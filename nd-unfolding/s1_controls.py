#!/usr/bin/env python3
"""5D community route, S1 (S1-DECLARATION.md section 4): the mechanical gates of the pilot, production and readout.

Every gate prints PASS or FAIL with a reason and never prints a cross-section value, so no H2-level quantity is
formed from an (e) data product before the assembly is bound (DECISION-20261024 H2 definition, the director's
ruling on item 2). The one numeric gate, ``denominator``, compares simulation-only histograms.

  products     every listed universe product exists, was made by the declared estimator from the declared source
               (s1_assemble.check_universe) and has a finite, non-negative xsec_flat
  seeds        the same for the seed-block products of one estimator seed (s1_assemble.check_meta)
  cv           the universe tool's CV control equals the central product bitwise (the matched-CV control)
  central      the central product data_b-_j- (fb5cc679), s5e's data_R (361030f3) and RE-1's P5 rerun (e36f3b25)
               carry the same xsec_flat bitwise
  denominator  the bank path's truth denominator, rebuilt from the bank's GEANT tdw (CV-equal truth weights), has
               the support and the total of the detector dump's and the npz's CV denom_nd (<= 1e-9), and agrees per
               cell within 1e-3. The per-cell bound is measured, not exact: the bank's truth coordinates move events
               across bin edges (max 4.098e-4 relative in 2026-10-24's simulation-only review), a common offset of
               every bank universe that mean-centring cancels (S1-DECLARATION.md section 4)

Exit 0 when every gate passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s1_assemble as sa  # noqa: E402

CENTRAL_SHA256 = "fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c"  # stage0 INVENTORY.sha256
DATA_R_SHA256 = "361030f3a3d179b1d31b7e64666dc01169b5d6afe0f677805beac2258289850f"  # measured 2026-10-24, login12
P5_SHA256 = "e36f3b25459e068cec9dba941f7b3aea8f48c6e22c931fde7c9d315e7b1e8de2"
DENOM_TOTAL_TOL = 1e-9
DENOM_CELL_TOL = 1e-3
GEANT = [f"{b}_{i}" for b in ("GEANT_Neutron", "GEANT_Pion", "GEANT_Proton") for i in (0, 1)]


def report(name: str, ok: bool, why: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}{'' if ok else ': ' + why}", flush=True)
    return ok


def gate_finite(path: Path) -> tuple[bool, str]:
    x = sa.xs(path)
    if x.size != int(np.prod(sa.s1.fine_shape())):
        return False, f"xsec_flat has {x.size} entries"
    if not np.all(np.isfinite(x)):
        return False, "non-finite entries"
    if np.any(x < 0):
        return False, "negative entries"
    return True, ""


def products(a) -> bool:
    man = sa.load_manifest(a.manifest)
    try:
        sa.require_listed(a.detector_receipt, man, "detector-dump receipt")
    except SystemExit as e:
        return report("detector_receipt_sha256", False, str(e))
    det = json.loads(a.detector_receipt.read_text())["files_sha256"]
    ok = True
    for item in a.universes.split(","):
        band, _, idx = item.partition(":")
        p = a.dir / f"{a.tag}_{band}_{idx}.npz"
        if not p.exists():
            ok &= report(p.name, False, "missing")
            continue
        try:
            sa.check_universe(p, band, man, det)
        except SystemExit as e:
            ok &= report(p.name, False, str(e))
            continue
        good, why = gate_finite(p)
        ok &= report(p.name, good, why)
    return ok


def seeds(a) -> bool:
    ok = True
    for b in sa.SEED_REPLICAS:
        p = a.dir / f"{a.tag}{a.seed}_b{b}_j{100 + b}.npz"
        if not p.exists():
            ok &= report(p.name, False, "missing")
            continue
        try:
            sa.check_meta(p, "s5p-numerics/1", seed=a.seed, expect={"bootstrap_seed": b, "jitter_seed": 100 + b, "coords": "float64"})
        except SystemExit as e:
            ok &= report(p.name, False, str(e))
            continue
        good, why = gate_finite(p)
        ok &= report(p.name, good, why)
    return ok


def cv(a) -> bool:
    try:
        sa.check_meta(a.cv, "s5p-universe/1")
    except SystemExit as e:
        return report("cv_control_meta", False, str(e))
    return report("cv_control_equals_central_bitwise", np.array_equal(sa.xs(a.cv), sa.xs(a.central)), "xsec_flat differs")


def central(a) -> bool:
    ok = report("central_sha256", sa.sha256(a.central) == CENTRAL_SHA256, "digest differs")
    ok &= report("data_R_sha256", sa.sha256(a.data_r) == DATA_R_SHA256, "digest differs")
    ok &= report("p5_sha256", sa.sha256(a.p5) == P5_SHA256, "digest differs")
    x = sa.xs(a.central)
    ok &= report("central_equals_data_R_bitwise", np.array_equal(x, sa.xs(a.data_r)), "xsec_flat differs")
    ok &= report("central_equals_p5_bitwise", np.array_equal(x, sa.xs(a.p5)), "xsec_flat differs")
    return ok


def denominator(a) -> bool:
    import s5p_universe as su
    if sa.sha256(a.inputs_npz) != sa.INPUT_NPZ_SHA256:
        return report("inputs_npz_sha256", False, "digest differs")
    z = np.load(a.inputs_npz, allow_pickle=False)
    edges = [np.asarray(z[f"edges_{i}"], float) for i in range(len(sa.s1.AXES))]
    if any(not np.array_equal(e, np.asarray(sa.s1.FINE[k], float)) for e, k in zip(edges, sa.s1.AXES)):
        return report("edges", False, "npz edges differ from the fine grid")
    cv_denom = np.asarray(z["denom_nd"], float)
    bank_cv = np.load(a.bank / "cv.npz", allow_pickle=False)
    ok, out = True, {}
    for tag in GEANT:
        tdw = np.load(a.bank / f"{tag}_tdw.npy").astype(np.float64)
        dn_bank = su.denominator(bank_cv, tdw, edges)
        dn_dump = np.load(a.dump / f"{tag}_denom_nd.npy").astype(np.float64)
        for name, ref in (("dump", dn_dump), ("npz_cv", cv_denom)):
            same_support = bool(np.array_equal(dn_bank > 0, ref > 0))
            m = ref > 0
            dev = float(np.max(np.abs(dn_bank[m] / ref[m] - 1))) if m.any() else 0.0
            tot = float(abs(dn_bank.sum() / ref.sum() - 1))
            out[f"{tag}_vs_{name}"] = {"same_support": same_support, "total_rel_dev": tot, "max_cell_rel_dev": dev,
                                        "cells_above_1e-9": int(np.sum(np.abs(dn_bank[m] / ref[m] - 1) > 1e-9))}
            ok &= report(f"denominator_{tag}_vs_{name}", same_support and tot <= DENOM_TOTAL_TOL and dev <= DENOM_CELL_TOL,
                         f"support {same_support}, total rel dev {tot:.3e}, max cell rel dev {dev:.3e}")
    print(json.dumps(out))
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="gate", required=True)
    p = sub.add_parser("products")
    p.add_argument("--dir", type=Path, required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--universes", required=True, help="BAND:IDX[,...]")
    p.add_argument("--manifest", type=Path, required=True, help="sf1 manifest/inputs-sha256.txt")
    p.add_argument("--detector-receipt", type=Path, required=True, help="bank_detector/detector-dump.json")
    p = sub.add_parser("seeds")
    p.add_argument("--dir", type=Path, required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--seed", type=int, required=True)
    p = sub.add_parser("cv")
    p.add_argument("--cv", type=Path, required=True)
    p.add_argument("--central", type=Path, required=True)
    p = sub.add_parser("central")
    p.add_argument("--central", type=Path, required=True)
    p.add_argument("--data-r", type=Path, required=True)
    p.add_argument("--p5", type=Path, required=True)
    p = sub.add_parser("denominator")
    p.add_argument("--inputs-npz", type=Path, required=True)
    p.add_argument("--bank", type=Path, required=True)
    p.add_argument("--dump", type=Path, required=True)
    a = ap.parse_args(argv)
    ok = {"products": products, "seeds": seeds, "cv": cv, "central": central, "denominator": denominator}[a.gate](a)
    print(f"{'ALL PASS' if ok else 'STOP'} {a.gate}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
