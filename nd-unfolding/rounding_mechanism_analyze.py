#!/usr/bin/env python3
"""RS1's analysis: gates G1-G4, the readings K1-K5 of §5.2, the readouts of §6, and R0.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/
RS1-DECLARATION.md.

    rounding_mechanism_analyze.py read --runs <OUT>/runs --fdstab-refs DIR --fdstab-sums SHA256SUMS
        --s5c-contract P --h2-definition P --sigma-receipt P --out JSON
    rounding_mechanism_analyze.py r0 --i0 P --data-product P --s1-assembly P --out JSON

``read`` grades nothing unless the full run's DONE receipt (``<OUT>/log-full/DONE``, derived from ``--runs``) exists
with no STOP or FAILED beside it. G1 compares A0's float32 base and jitters 1-20 bitwise with FD-STAB's control
products, each of which must first match its line in FD-STAB's pinned SHA256SUMS. G4 compares S-all's jitters
bitwise with A0's. If G1 fails nothing is read; if G4 fails K5 is not read.

MEASURES: the declared readings on RS1's products. CANNOT AUTHORIZE: a mechanism on data, an estimator change, or
any change to OUTCOME-20261105-fd-stab-none-pass.md.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import rounding_mechanism_probe as rmp  # noqa: E402

SCHEMA = "rs1-analysis/1"
R_MAX, C_MIN = 0.10, 0.70
N_BOOT, BOOT_SEED = 2000, 20261106
EXCLUDE_MAX = 0.10
K2_POINT, K2_UPPER = 0.5, 0.7
K3_SUPPORTED = 0.3
K4_SUPPORTED, K4_NOT = 0.10, 0.01
G4_SEEDS = (1, 2, 3)
FDSTAB_PREFIX = "runs/control/stability/"
SIGMA_RECEIPT_SHA256 = "84266e309d1aae0d2db1db315750b8164413a7d0125fcaa4a6c9b25834261a2c"
INCOMPLETE_RC, STOP_RC = 3, 4


def sha256_path(p: Path) -> str:
    return rmp.sha256_path(Path(p))


# -------------------------------------------------------------------------------------------- products

def load(path: Path) -> tuple[np.ndarray, dict]:
    z = np.load(path, allow_pickle=False)
    return np.asarray(z["xsec_flat"], float), json.loads(str(z["meta"]))


def arm_products(runs: Path, arm: str, metas: list | None = None) -> dict:
    """{jitter seed (None, 0, 1..): xsec} for one arm, every product checked against the declared input and arm. With
    ``metas``, each product's (name, meta) is appended to it for the code-consistency check."""
    out = {}
    for p in sorted((Path(runs) / arm).glob("*.npz")):
        if ".partial" in p.name:
            raise SystemExit(f"{p.name}: a partial product")
        x, m = load(p)
        rm = m.get("rounding_mechanism") or {}
        if rm.get("schema") != rmp.SCHEMA or rm.get("arm") != arm:
            raise SystemExit(f"{p.name}: not an RS1 {arm} product")
        sp = m.get("stability_probe") or {}
        if sp.get("candidate") != "control":
            raise SystemExit(f"{p.name}: not through FD-STAB's control path")
        want = (m.get("construction"), m.get("truth"), m.get("eavail_ratio_sha256"), m.get("pseudo_seed"),
                m.get("bootstrap_seed"), m.get("amplitude"))
        if want != ("pseudo", rmp.STABILITY["truth"], rmp.STABILITY["ratio_sha256"], rmp.STABILITY["pseudo_seed"], None,
                    rmp.STABILITY["amplitude"]):
            raise SystemExit(f"{p.name}: not the declared stability input")
        if (m.get("input_npz_sha256"), m.get("bkg_dump_sha256")) != (rmp.STABILITY["npz_sha256"],
                                                                     rmp.STABILITY["bkg_sha256"]):
            raise SystemExit(f"{p.name}: its input digests are not the declared inputs' (RS1-C1)")
        if metas is not None:
            metas.append((f"{arm}/{p.name}", m))
        j = m.get("jitter_seed")
        if j != rm.get("jitter_seed"):
            raise SystemExit(f"{p.name}: the runner's and RS1's jitter seeds differ")
        if j in out:
            raise SystemExit(f"{p.name}: jitter seed {j} twice")
        out[j] = x
    declared = {None if b == "-" else int(b) for b in (p.split(":")[1] for p in rmp.ARMS[arm]["pairs"])}
    if set(out) != declared:
        raise SystemExit(f"{arm}: products {sorted(out, key=str)} are not the declared {sorted(declared, key=str)}")
    return out


def trace(runs: Path, arm: str, seed) -> dict | None:
    s = "-" if seed is None else seed
    p = Path(runs) / arm / f"rs1_{arm}_b-_j{s}.trace.json.gz"
    if not p.exists():
        return None
    with gzip.open(p, "rt") as fh:
        return json.load(fh)


CODE_DIGESTS = (("runner code_sha256", lambda m: m.get("code_sha256")),
                ("stability_probe.code_sha256", lambda m: (m.get("stability_probe") or {}).get("code_sha256")),
                ("rounding_mechanism.code_sha256", lambda m: (m.get("rounding_mechanism") or {}).get("code_sha256")))


def code_problem(metas: list) -> str | None:
    """RS1-C1: each code digest must take ONE value, never missing, across every product of the run."""
    for label, get in CODE_DIGESTS:
        seen = {}
        for name, m in metas:
            v = get(m)
            if v is None:
                return f"{name}: no {label}"
            seen.setdefault(json.dumps(v, sort_keys=True), name)
        if len(seen) != 1:
            return f"{label} takes {len(seen)} values across the products (e.g. {sorted(seen.values())[:2]})"
    return None


def receipt_problem(runs: Path) -> str | None:
    """The full run's DONE, with no STOP or FAILED beside it, and the dry run's DONE at the same deploy pin."""
    pins = {}
    for mode in ("dry", "full"):
        log = Path(runs).parent / f"log-{mode}"
        if not (log / "DONE").is_file():
            return f"no DONE receipt at {log / 'DONE'}"
        for bad in ("STOP", "FAILED"):
            if (log / bad).exists():
                return f"{bad} beside the {mode} receipt"
        pins[mode] = json.loads((log / "DONE").read_text()).get("pin")
    if not pins["dry"] or pins["dry"] != pins["full"]:
        return f"the dry and full runs' pins differ or are missing: {pins} (RS1-C1)"
    return None


def fdstab_refs(refs: Path, sums: Path) -> dict:
    """FD-STAB's control base and jitters 1-20, each verified against its pinned SHA256SUMS line."""
    pinned = {}
    for line in Path(sums).read_text().splitlines():
        h, name = line.split(None, 1)
        if name.startswith(FDSTAB_PREFIX):
            pinned[name[len(FDSTAB_PREFIX):]] = h
    out = {}
    for seed in (None, *rmp.SEEDS):
        name = f"stab_control_b-_j{'-' if seed is None else seed}.npz"
        p = Path(refs) / name
        if name not in pinned or sha256_path(p) != pinned[name]:
            raise SystemExit(f"G1 reference {name} is not FD-STAB's pinned product")
        out[seed] = load(p)[0]
    return out


# ------------------------------------------------------------------------------------------ statistics

def rel_sd(F: np.ndarray) -> np.ndarray:
    """F: (seeds, functionals) -> per functional, the SD (ddof 1) of F / mean - 1 over seeds."""
    F = np.asarray(F, float)
    return np.std(F / F.mean(axis=0, keepdims=True), axis=0, ddof=1)


def band(m: float) -> str:
    return "R" if m <= R_MAX else ("C" if m >= C_MIN else "P")


def spread_ratio(Fa: np.ndarray, F0: np.ndarray, rng) -> dict:
    """§5: M = median_j s_a,j / s_A0,j over functionals with s_A0,j > 0; a paired bootstrap of the seeds."""
    Fa, F0 = np.asarray(Fa, float), np.asarray(F0, float)
    if Fa.shape != F0.shape:
        raise ValueError(f"paired arms need equal shapes, got {Fa.shape} and {F0.shape}")
    s0 = rel_sd(F0)
    ok = s0 > 0
    excluded = int((~ok).sum())
    frac = excluded / s0.size
    point = float(np.median(rel_sd(Fa)[ok] / s0[ok])) if ok.any() else float("nan")
    n = F0.shape[0]
    meds = np.empty(N_BOOT)
    for b in range(N_BOOT):
        i = rng.integers(0, n, n)
        sb0 = rel_sd(F0[i])[ok]
        sba = rel_sd(Fa[i])[ok]
        good = sb0 > 0
        meds[b] = np.median(sba[good] / sb0[good]) if good.any() else np.nan
    lo, hi = (float(v) for v in np.nanpercentile(meds, [5, 95]))
    b_lo, b_hi = band(lo), band(hi)
    return {"M": point, "interval_90": [lo, hi], "excluded": excluded, "excluded_fraction": frac,
            "invalid": frac > EXCLUDE_MAX, "reading": "INVALID" if frac > EXCLUDE_MAX else (b_lo if b_lo == b_hi else
                                                                                         "INCONCLUSIVE")}


def base_difference(Fx: np.ndarray, Fref: np.ndarray, s0: np.ndarray) -> float:
    """D = median_j |F_x / F_ref - 1| / s_A0,j over functionals with s_A0,j > 0."""
    ok = (s0 > 0) & (Fref != 0)
    return float(np.median(np.abs(Fx[ok] / Fref[ok] - 1.0) / s0[ok]))


def both(readings: dict, rule) -> str:
    """A candidate's reading: the rule on each functional set; agreement required, else INCONCLUSIVE."""
    got = {k: rule(v) for k, v in readings.items()}
    vals = set(got.values())
    return vals.pop() if len(vals) == 1 else "INCONCLUSIVE"


def k1_rule(r):
    return {"R": "SUPPORTED", "P": "PARTIAL", "C": "NOT SUPPORTED"}.get(r["reading"], r["reading"])


def k2_rule(r):
    if r["invalid"]:
        return "INVALID"
    lo, hi = r["interval_90"]
    if r["M"] <= K2_POINT and hi <= K2_UPPER:
        return "SUPPORTED"
    if lo >= C_MIN:
        return "NOT SUPPORTED"
    return "INCONCLUSIVE"


def k3_reading(bitwise_equal: bool, d: dict) -> str:
    if bitwise_equal:
        return "NOT SUPPORTED"
    return both(d, lambda v: "SUPPORTED" if v >= K3_SUPPORTED else "PARTIAL")


def k4_reading(d: dict) -> str:
    return both(d, lambda v: "SUPPORTED" if v >= K4_SUPPORTED else ("NOT SUPPORTED" if v <= K4_NOT else "INCONCLUSIVE"))


def k5_rule(r):
    return {"C": "SUPPORTED", "P": "PARTIAL", "R": "NOT SUPPORTED"}.get(r["reading"], r["reading"])


# ---------------------------------------------------------------------------------------------- readouts

def first_difference(a: list, b: list) -> dict:
    """Two fits' split tables: identical trees, the first tree whose structure (features, leaf counts) differs, and
    its first differing internal node."""
    def struct(t):
        return [(n[0], n[1]) if n[0] == "s" else ("l", n[2]) for n in t]
    n = min(len(a), len(b))
    same_full = sum(a[i] == b[i] for i in range(n))
    same_struct = sum(struct(a[i]) == struct(b[i]) for i in range(n))
    first = next((i for i in range(n) if struct(a[i]) != struct(b[i])), None)
    node = None
    if first is not None:
        for na, nb in zip(a[first], b[first]):
            if na != nb:
                node = {"base": na, "other": nb, "new_feature": na[0] == "s" and nb[0] == "s" and na[1] != nb[1]}
                break
    return {"n_trees": [len(a), len(b)], "identical_trees": same_full, "identical_structure": same_struct,
            "first_structure_difference": first, "first_node": node}


def split_readout(runs: Path) -> dict:
    base = trace(runs, "A0", rmp.UNJITTERED_F64)
    out = {}
    if base is None:
        return {"missing": "A0's float64 base trace"}
    for arm, seeds in (("A0", (1, 2, 3)), ("V", (1, 2, 3))):
        for s in seeds:
            t = trace(runs, arm, s)
            if t is None:
                out[f"{arm}_{s}"] = {"missing": True}
                continue
            fits = [first_difference(fb["trees"], fo["trees"]) for fb, fo in zip(base["fits"], t["fits"])]
            ref = None
            if base.get("refinement_tree") and t.get("refinement_tree"):
                ref = first_difference(base["refinement_tree"], t["refinement_tree"])
            out[f"{arm}_{s}"] = {"refinement": ref, "omnifold_fits": fits,
                                 "fit_roles": [f["role"] for f in t["fits"]]}
    return out


def clip_readout(runs: Path) -> dict:
    base = trace(runs, "A0", rmp.UNJITTERED_F64)
    if base is None or not base.get("measured_sides"):
        return {"missing": "A0's float64 base trace"}
    z0 = set(base["measured_sides"][0]["zero_weight_rows"])
    out = {}
    for arm in ("A0", "V", "S_ref"):
        for s in rmp.SEEDS:
            t = trace(runs, arm, s)
            if t and t.get("measured_sides"):
                z = set(t["measured_sides"][0]["zero_weight_rows"])
                out[f"{arm}_{s}"] = {"n_zero": len(z), "changed_vs_f64_base": len(z ^ z0)}
    return {"n_zero_f64_base": len(z0), "per_product": out}


# --------------------------------------------------------------------------------------------------- read

def read(a) -> int:
    why = receipt_problem(a.runs)
    if why:
        Path(a.out).write_text(json.dumps({"schema": SCHEMA, "status": "INCOMPLETE", "why": why}, indent=1) + "\n")
        print(json.dumps({"status": "INCOMPLETE", "why": why}))
        return INCOMPLETE_RC
    U = rmp.functional_matrix(a.s5c_contract, a.h2_definition)
    sets = {"functionals_153": slice(0, U.shape[0] - 16), "cells_16": slice(U.shape[0] - 16, U.shape[0])}
    if U.shape[0] - 16 != 153:
        raise SystemExit(f"{U.shape[0] - 16} functionals, not s5e's 153")
    metas: list = []
    prods = {arm: arm_products(a.runs, arm, metas) for arm in rmp.ARMS}
    why = code_problem(metas)
    if why:
        raise SystemExit(f"RS1-C1: {why}")
    refs = fdstab_refs(a.fdstab_refs, a.fdstab_sums)
    a0 = prods["A0"]
    g1 = {str(s): bool(np.array_equal(a0[s], refs[s])) for s in refs}
    out = {"schema": SCHEMA, "label": "RS1 step 1 readings (RS1-DECLARATION.md §5)", "G1": g1}
    if not all(g1.values()):
        out["status"] = "NOT REPRODUCED"
        Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps({"status": out["status"]}))
        return STOP_RC
    F = {arm: {s: U @ x for s, x in p.items()} for arm, p in prods.items()}

    def jit(arm, seeds=rmp.SEEDS):
        return np.array([F[arm][s] for s in seeds])

    s0 = {k: rel_sd(jit("A0")[:, sl]) for k, sl in sets.items()}
    g2_frac = float((s0["functionals_153"] == 0).mean())
    out["G2"] = {"zero_spread_fraction": g2_frac, "pass": g2_frac <= EXCLUDE_MAX}
    if not out["G2"]["pass"]:
        out["status"] = "UNINFORMATIVE"
        Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps({"status": out["status"]}))
        return STOP_RC
    out["G4"] = {str(s): bool(np.array_equal(prods["S_all"][s], a0[s])) for s in G4_SEEDS}
    rng = np.random.default_rng(BOOT_SEED)
    ratio = {}
    for arm in ("V", *[f"F_{ax}" for ax in rmp.AXES], "S_ref", "S_omni", "B63", "B1023"):
        ratio[arm] = {k: spread_ratio(jit(arm)[:, sl], jit("A0")[:, sl], rng) for k, sl in sets.items()}
    bit_k3 = bool(np.array_equal(a0[rmp.UNJITTERED_F64], a0[None]))
    d3 = {k: base_difference(F["A0"][rmp.UNJITTERED_F64][sl], F["A0"][None][sl], s0[k]) for k, sl in sets.items()}
    d4 = {k: max(base_difference(F[p][rmp.UNJITTERED_F64][sl], F["A0"][rmp.UNJITTERED_F64][sl], s0[k])
                 for p in ("P1", "P2")) for k, sl in sets.items()}
    g4 = all(out["G4"].values())
    out["readings"] = {
        "K1": both(ratio["V"], k1_rule),
        "K2": both(ratio["B1023"], k2_rule),
        "K3": k3_reading(bit_k3, d3),
        "K4": k4_reading(d4),
        "K5": both(ratio["S_ref"], k5_rule) if g4 else "NOT READ: G4 failed",
        "K6": "NOT TESTABLE",
    }
    out["statistics"] = {"ratio": ratio, "K3_bitwise_equal": bit_k3, "K3_D": d3, "K4_D_P": d4}
    out["supported"] = [k for k, v in out["readings"].items() if v == "SUPPORTED"] or "NONE"
    out["readouts"] = readouts(a, F, prods, sets, s0, U)
    out["status"] = "READ"
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"status": out["status"], "readings": out["readings"]}))
    return 0


def readouts(a, F, prods, sets, s0, U) -> dict:
    import estimator_stability_analyze as esa
    if sha256_path(a.sigma_receipt) != SIGMA_RECEIPT_SHA256:
        raise SystemExit("sigma receipt is not the pinned file")
    sigma = np.asarray(json.loads(Path(a.sigma_receipt).read_text())["sigma_rel_pct"], float) / 100.0
    a0 = F["A0"]
    k153 = sets["functionals_153"]
    rel = np.array([a0[s][k153] / a0[None][k153] - 1.0 for s in rmp.SEEDS])
    z = np.abs(rel) / sigma
    pairs = [np.maximum(z[2 * p], z[2 * p + 1]) for p in range(len(rmp.SEEDS) // 2)]
    abs_spread = {arm: float(np.median(rel_sd(np.array([F[arm][s][k153] for s in rmp.SEEDS])) / sigma))
                  for arm in F if set(rmp.SEEDS) <= set(F[arm])}
    per_iter = []
    tr = [rmp_trace for rmp_trace in (trace(a.runs, "A0", s) for s in rmp.SEEDS) if rmp_trace and "fn_push" in rmp_trace]
    if len(tr) == len(rmp.SEEDS):
        fp = np.array([t["fn_push"] for t in tr])  # (seeds, iters, functionals)
        s1 = rel_sd(fp[:, 0, k153])
        for k in range(fp.shape[1]):
            sk = rel_sd(fp[:, k, k153])
            ok = s1 > 0
            per_iter.append(float(np.median(sk[ok] / s1[ok])))
    base_tr = trace(a.runs, "A0", None) or {}
    w0 = {f"{arm}_{s}": (t["measured_sides"][0]["w0_measured"], t["measured_sides"][0]["w0_mc_reco"])
          for arm in prods for s in prods[arm] if (t := trace(a.runs, arm, s)) and t.get("measured_sides")}
    return {
        "absolute_median_spread_in_pseudo_sigma": abs_spread,
        "A0_pair_statistic_10_pairs": {"mean_median": float(np.mean([np.median(m) for m in pairs])),
                                       "mean_max": float(np.mean([np.max(m) for m in pairs]))},
        "per_iteration_spread_over_iteration_1": per_iter,
        "ties_float32_base": {k: base_tr.get(k) for k in ("ties_mc_truth", "ties_mc_reco", "ties_measured")},
        "split_tables": split_readout(a.runs),
        "clip": clip_readout(a.runs),
        "w0_rows_measured_and_mc_reco": w0,
        "fdstab_bound_used": [esa.BOUND_MEDIAN, esa.BOUND_MAX],
    }


# ----------------------------------------------------------------------------------------------------- R0

I0_PRINTED = (0.133, 0.055, 0.252)  # FD-1B-INV-I0-REPORT.md:67, in %


def r0(i0: dict, dp: dict, s1: dict) -> dict:
    cells = [f"R{c:02d}" for c in range(16)]
    dp_cells = [c["cell"] for c in dp["cells"]]
    if list(i0["cells"]) != cells or dp_cells != cells or list(s1["cells"]) != cells:
        raise SystemExit("R0: the three files do not list R00-R15 in the same order")
    ce_dp = np.asarray(dp["relative_sigma"]["C_e"], float)
    ce_s1 = np.asarray(s1["relative_sigma"]["C_e"], float)
    if not np.allclose(ce_dp, ce_s1, rtol=1e-12, atol=0):
        raise SystemExit("R0: the data product's C_e is not S1's, so its f is not S1's")
    f = np.asarray(dp["f"], float)
    sj = np.asarray(i0["sigma_J_data"], float)  # absolute (fd_1b_inv.py:220-225)
    rel_j = sj / f
    pct = 100 * rel_j
    got = (round(float(np.median(pct)), 3), round(float(pct.min()), 3), round(float(pct.max()), 3))
    if got != I0_PRINTED:
        raise SystemExit(f"R0: sigma_J/f in % reads {got}, not I0's printed {I0_PRINTED}")
    stat = np.asarray(s1["relative_sigma"]["stat"], float)
    r0a = rel_j / stat
    defined = stat > rel_j
    r0b = np.where(defined, rel_j / np.sqrt(np.where(defined, stat ** 2 - rel_j ** 2, 1.0)), np.nan)

    def summ(v):
        return {"median": float(np.median(v)), "min": float(np.min(v)), "max": float(np.max(v))}

    return {"schema": "rs1-r0/1", "label": "RS1 R0: description only, read as neither a pass nor a fail",
            "cells": cells, "sigma_J_over_f": rel_j.tolist(), "sigma_S1_stat_rel": stat.tolist(),
            "R0a": r0a.tolist(), "R0a_summary": summ(r0a),
            "R0b": [None if not d else float(v) for d, v in zip(defined, r0b)],
            "R0b_undefined_cells": [c for c, d in zip(cells, defined) if not d],
            "R0b_summary": summ(r0b) if defined.all() else None,
            "assumption": "R0b assumes the rounding and the remaining statistical variances add, per cell",
            "controls": {"sigma_J_over_f_pct_reproduces": list(got), "C_e_identity": True}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0], allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read", allow_abbrev=False)
    for opt in ("--runs", "--fdstab-refs", "--fdstab-sums", "--s5c-contract", "--h2-definition", "--sigma-receipt",
                "--out"):
        r.add_argument(opt, type=Path, required=True)
    z = sub.add_parser("r0", allow_abbrev=False)
    for opt in ("--i0", "--data-product", "--s1-assembly", "--out"):
        z.add_argument(opt, type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "read":
        return read(a)
    rec = r0(json.loads(a.i0.read_text()), json.loads(a.data_product.read_text()), json.loads(a.s1_assembly.read_text()))
    rec["inputs_sha256"] = {k: sha256_path(p) for k, p in (("i0", a.i0), ("data_product", a.data_product),
                                                           ("s1_assembly", a.s1_assembly))}
    a.out.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({"R0a": rec["R0a_summary"], "R0b": rec["R0b_summary"], "undefined": rec["R0b_undefined_cells"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
