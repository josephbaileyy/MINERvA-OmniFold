#!/usr/bin/env python3
"""D2's mu_max in LL5D's own space (the director's design rulings of 2026-11-16; closes lrows-g README:121-127's
"not covered"): per truth, G = band:GEANT_Neutron + band:GEANT_Proton as LL5D rebuilt them at T from that truth's own
detector-universe unfolds, against LL5D's graded matrices M:
  primary    C_T   = C_e + C_model_abs at T, the "all" reading's matrix (the matrix graded WITH the two bands);
  secondary  C_T^- = C_e + C_model_abs^- at T (leave-out-MEC), the readout's second matrix.
mu_max = max_a (a^T G a) / (a^T M a), the largest generalized eigenvalue, bounds every chi2 change from dropping G:
chi2(M - G) / chi2(M) in [1, 1 / (1 - mu_max)]. The arithmetic is lrows-g's own geant_full.summarize (45fc4bcf),
imported unchanged, on fractional matrices (divided by X_T X_T^T, the truth's own central value, as geant_full divides
by the data's f f^T); mu_max does not depend on that scaling, the eigenmode shares do.

Steps (python3 -I from the repository root):
  s1-control   the same mumax_record on S1's committed data blocks (geant_full's construction) must reproduce
               geant_full.json's mu_max for C_total and for the reported covariance to 1e-12 relative. Exit 0 PASS.
  inputs       print the atime watch list of `ll5d` for the given truths, one path per line: the inputs the run must
               not move (the staged S1 assembly, the constraint, every product at T in the null's roles). The
               definition and the cmodel json are left out: they are files of the connect's own fresh deploy, which
               LL5D's setup, made_from and cmodel_parts read plainly (coverage-5b-audit blocker 1).
  ll5d         per truth, reading only through LL5D's own functions (ll5d_b.setup, remade; products O_NOATIME):
               (0) --null gives LL5D's committed null record per truth (the connect checks its sha256 first); the
                   truth, products_sha256 and made_from are read from it, and mc.made_from(a, U) must equal its made_from
                   (U, the cmodel json and the definition the null was made from);
               (1) the products at T (roles central, seed, block, stat) are the null's: their digest, made exactly as
                   ll5d_b.products_digest makes it but reading every product O_NOATIME, equals the null's
                   products_sha256 (products_digest's own sha256_path reads plainly);
               (2) the removal control on the G used here: max |C_T(minus2) - (C_T(all) - G)| <= 1e-12 max |C_T(all)|
                   (ll5d_b.removal_control's tolerance), so a G that is not the two bands' blocks STOPs;
               (3) mumax_record for C_T and for C_T^-.
               Writes --out (JSON). Exit 0 PASS, 2 STOP (a control failed; the record says which).
MEASURES: arithmetic on committed and pinned products. CANNOT AUTHORIZE: a reading, a paper edit or a claim.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path.cwd()
sys.path.insert(0, str(REPO / "nd-unfolding"))
FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024"
LROWS = REPO / "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/lrows-g"
GEANT_FULL_SHA = "45fc4bcf1da5f717"          # geant_full.py's sha256 prefix (lrows-g README)
S1_CELLS_JSON = FD / "s1/readout/s1_assembly.json"
REMOVAL_TOL = 1e-12
GEANT = ("band:GEANT_Neutron", "band:GEANT_Proton")


def load_geant_full():
    p = LROWS / "geant_full.py"
    if not hashlib.sha256(p.read_bytes()).hexdigest().startswith(GEANT_FULL_SHA):
        raise SystemExit(f"{p} is not geant_full.py {GEANT_FULL_SHA}")
    spec = importlib.util.spec_from_file_location("geant_full", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def mumax_record(G_abs: np.ndarray, M_abs: np.ndarray, scale: np.ndarray, cells: list, gf) -> dict:
    """geant_full.summarize on G and M divided by scale scale^T (the fractional form geant_full uses)."""
    ss = np.outer(scale, scale)
    G, M = G_abs / ss, M_abs / ss
    rec = gf.summarize(G, M, cells)
    rec["G_offdiagonal_abs_share"] = float(np.sum(np.abs(G - np.diag(np.diag(G)))) / np.sum(np.abs(G)))
    return rec


def removal_check(C_all: np.ndarray, C_m2: np.ndarray, G: np.ndarray) -> dict:
    dev = float(np.max(np.abs(C_m2 - (C_all - G))))
    lim = REMOVAL_TOL * float(np.max(np.abs(C_all)))
    return {"max_abs_dev": dev, "limit": lim, "passes": bool(dev <= lim)}


def read_noatime(p: Path) -> bytes:
    fd = os.open(p, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 22)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    return b"".join(chunks)


def products_digest_noatime(unfolds: Path, truth: str, roles, tag: str) -> tuple[str, int]:
    """ll5d_b.products_digest's construction (sorted names, name then the product's hex sha256), O_NOATIME reads."""
    left = sorted(p.name for p in unfolds.glob(f"{tag}_{truth}_*.partial-*"))
    if left:
        raise SystemExit(f"partial products are present: {left[:3]}")
    h, n = hashlib.sha256(), 0
    for p in sorted(unfolds.glob(f"{tag}_{truth}_*.npz")):
        if p.name.split("_")[2] in roles:
            h.update(p.name.encode())
            h.update(hashlib.sha256(read_noatime(p)).hexdigest().encode())
            n += 1
    return h.hexdigest(), n


def cmd_s1_control(a) -> int:
    import s1_assemble as sa
    gf = load_geant_full()
    want = json.loads((LROWS / "geant_full.json").read_text())["matrices"]
    U = sa.functional_matrix(sa.fine_map(gf.FILES["definition"]))
    blk = {b: sa.mat_cov(np.array([U @ sa.xs(gf.S1D / f"S1_{b}_{i}.npz") for i in (0, 1)]))
           for b in ("GEANT_Neutron", "GEANT_Proton")}
    dp = json.loads(gf.FILES["dp_cpl"].read_text())
    Mx = {k: np.array(v) for k, v in dp["matrices"].items()}
    f, cells = np.array(dp["f"]), json.loads(S1_CELLS_JSON.read_text())["cells"]
    G = blk["GEANT_Neutron"] + blk["GEANT_Proton"]
    got = {"C_total (C_e + C_model_abs, at the data)": mumax_record(G, Mx["C_e"] + Mx["C_model_abs"], f, cells, gf),
           "reported (C_total + C_resp + C_PL5D)": mumax_record(G, Mx["C_total_plus_C_resp_plus_C_PL5D"], f, cells, gf)}
    ok = True
    for k, r in got.items():
        w = want[k]["mu_max"]
        rel = abs(r["mu_max"] - w) / w
        ok &= rel <= 1e-12
        print(f"S1-CONTROL {k}: mu_max {r['mu_max']!r} vs geant_full.json {w!r}, rel {rel:.2e}")
    print(f"S1-CONTROL {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def declared_inputs(a, truth: str) -> list[str]:
    import ll5d_b as lb
    out = [str(a.staged / "s1" / "s1_assembly.npz"), str(a.flux_constraint)]     # not the deploy's definition/cmodel
    out += sorted(str(p) for p in a.unfolds.glob(f"{lb.TAG}_{truth}_*.npz") if p.name.split("_")[2] in lb.BLOCK_ROLES)
    return out


def cmd_inputs(a) -> int:
    for t in a.truth:
        print("\n".join(declared_inputs(a, t)))
    return 0


def cmd_ll5d(a) -> int:
    import ll5d_b as lb
    import s1_assemble as sa
    gf = load_geant_full()
    cells = json.loads(S1_CELLS_JSON.read_text())["cells"]
    import fd_1b_mc as mc
    s1, U, frac, minus, w = lb.setup(a)
    made = mc.made_from(a, U)
    rec = {"schema": "ll5d-mumax/1", "geant_full_sha256_prefix": GEANT_FULL_SHA, "truths": {}, "stop": [], "made_from": made,
           "inputs_sha256_noatime": {str(p): hashlib.sha256(read_noatime(p)).hexdigest()
                                     for p in (a.staged / "s1" / "s1_assembly.npz", a.flux_constraint)}}
    for nullp in a.null:
        raw = read_noatime(nullp)
        nl = json.loads(raw)
        t, want = nl["truth"], nl["products_sha256"]
        r = {"null": str(nullp), "null_sha256": hashlib.sha256(raw).hexdigest(),
             "made_from_match": nl.get("made_from") == made}
        rec["truths"][t] = r
        if not r["made_from_match"]:
            rec["stop"].append(f"{t}: made_from is not the null's")
            continue
        got, n = products_digest_noatime(a.unfolds, t, lb.BLOCK_ROLES, lb.TAG)
        r.update(products_sha256=got, expected=want, n_products=n, products_match=got == want)
        if got != want:
            rec["stop"].append(f"{t}: the products at T are not the null's")
            continue
        rm_all = lb.remade(a.unfolds, t, s1, U, w, frac, "all")
        rm_m2 = lb.remade(a.unfolds, t, s1, U, w, frac, "minus2")
        G = rm_all["blocks"][GEANT[0]] + rm_all["blocks"][GEANT[1]]
        r["removal_control_on_G"] = removal_check(rm_all["C_T"], rm_m2["C_T"], G)
        r["removal_control_ll5d_b"] = lb.removal_control(rm_all, rm_m2)
        if not (r["removal_control_on_G"]["passes"] and r["removal_control_ll5d_b"]["passes"]):
            rec["stop"].append(f"{t}: the removal control failed on G")
            continue
        Cm = rm_all["C_e"] + sa.model_abs(rm_all["X_T"], minus)
        r["G_eigenvalues_top3_abs"] = [float(x) for x in np.sort(np.linalg.eigvalsh(G))[::-1][:3]]
        r["primary C_T (all)"] = mumax_record(G, rm_all["C_T"], rm_all["X_T"], cells, gf)
        r["secondary C_T^- (all, leave-out-MEC)"] = mumax_record(G, Cm, rm_all["X_T"], cells, gf)
        p, s = r["primary C_T (all)"], r["secondary C_T^- (all, leave-out-MEC)"]
        print(f"[{t}] mu_max C_T {p['mu_max']!r} (1/(1-mu) {p['chi2_ratio_bound']!r}); C_T^- {s['mu_max']!r} "
              f"({s['chi2_ratio_bound']!r}); removal dev {r['removal_control_on_G']['max_abs_dev']:.3e}", flush=True)
    rec["verdict"] = "PASS" if not rec["stop"] else "STOP"
    a.out.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"MUMAX {rec['verdict']}: {rec['stop']}")
    return 0 if rec["verdict"] == "PASS" else 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("s1-control")
    for name in ("inputs", "ll5d"):
        s = sub.add_parser(name)
        for k in ("staged", "definition", "unfolds", "cmodel_json", "flux_constraint"):
            s.add_argument("--" + k.replace("_", "-"), type=Path, required=True)
        if name == "inputs":
            s.add_argument("--truth", action="append", required=True)
        else:
            s.add_argument("--null", type=Path, action="append", required=True, help="LL5D's null record, one per truth")
            s.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    return {"s1-control": cmd_s1_control, "inputs": cmd_inputs, "ll5d": cmd_ll5d}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
