#!/usr/bin/env python3
"""MSR Amendment E: the blind confirmation on the real inputs, before the rerun (the director's ruling of 2026-11-23).

Diagnostic 2's harness, run against the amended msr_project.py: the same output fields (msr_route_diag2.FIELDS, written
only through msr_route_diag2.Record), the same rows (diagnostic 2's 21 2D Z_well rows and its three 5D controls), and the
same 50-digit reference (msr_route_diag2.mp_fisher / mp_decompose / mp_z, imported unchanged at its committed sha). The
differences from diagnostic 2, all forced by Amendment E:
  - decompositions get F_c's root A (msr_project.fisher_root), as the amended production run does;
  - C is never formed, so kappa2_C is (sigma_max(G) / sigma_min(G))^2 for C = G G^T (inf if G is rank deficient), and
    kappa2_CQ is (s_max / s_min)^2 from C_Q's singular-value widths;
  - the 5D control rows get the 50-digit reference too (5D has 29 parameters, so it is cheap), so their reference
    fields and ref_partition_equal are filled.
It writes no a, b, value, label or band. The verdict, fixed before the run (`confirm()`), is PASS only if every one of the
24 rows has ref_partition_equal true and both routes within 1e-8 of the reference; stdout carries only the verdict and
the counts.

    msr_route_confirm.py --products DIR --out FILE.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import mpmath as mp
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import msr_project as P  # noqa: E402
import msr_route_diag2 as D  # noqa: E402

MSR_PROJECT_SHA = "SET-AFTER-REVIEW"       # the amended msr_project.py
DIAG2_SHA = "35d2357f7eec5954c5b9de0d32bfbbcf9cb3cb93bebc82249f0e2ad0e71e2c1b"   # msr_route_diag2.py, merged (#1270)
TOL = 1e-8


def confirm(rows: list[dict]) -> tuple[str, int, int]:
    """PASS iff all 24 rows are present, each has ref_partition_equal True and both routes <= 1e-8 of the reference
    (NaN or inf is a miss). Returns (verdict, rows passing, rows expected)."""
    want = sorted(D.TARGETS_2D + D.TARGETS_5D)
    if sorted(r["vector_id"] for r in rows) != want:
        return "FAIL", 0, len(want)

    def ok(r):
        return (r["ref_partition_equal"] is True and r["rel_diff_eigen_vs_ref"] <= TOL
                and r["rel_diff_indep_vs_ref"] <= TOL)
    n = sum(1 for r in rows if ok(r))
    return ("PASS" if n == len(want) else "FAIL"), n, len(want)


def kappa_g(dec: dict) -> float:
    sg = np.linalg.svd(dec["G"], compute_uv=False)
    return float((sg[0] / sg[-1]) ** 2) if sg.size and sg[-1] > 0 and sg.size == dec["G"].shape[0] else float("inf")


def kappa_q(dec: dict) -> float:
    s = dec["s"]
    return float((s.max() / s.min()) ** 2) if s.size and s.min() > 0 else float("inf")


def run(prod: Path, out: Path) -> int:
    import did
    for path, want in ((Path(P.__file__), MSR_PROJECT_SHA), (Path(D.__file__), DIAG2_SHA)):
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != want:
            print(f"REFUSED: {path.name} is {got}, not {want}", file=sys.stderr)
            return 9
    rec_controls, L = P.controls(prod)
    if not all(v["pass"] for v in rec_controls.values()):
        print("REFUSED: a first-block control failed", file=sys.stderr)
        return 3
    mp.mp.dps = D.DPS
    cells = np.asarray(L["a2"]["truths"]["nominal"]["cells"], int)
    probs5 = {"full": L["p5"], "A": P.problem_5d(L["z5"], "h2_halfA", did), "B": P.problem_5d(L["z5"], "h2_halfB", did)}
    probs2 = {h: P.problem_2d(L["z2"], k, cells) for h, k in (("full", "full"), ("A", "halfA"), ("B", "halfB"))}
    decs = {}
    for dim, probs in (("5d", probs5), ("2d", probs2)):
        for h, p in probs.items():
            for drv in ("numpy", "evr"):
                d = P.decompose(p["F"], p["J"], drv, A=p["A"])
                d["keep"] = p["keep"]
                decs[(dim, h, drv)] = d
    capture: dict = {}
    D.install(capture, set(D.TARGETS_2D) | set(D.TARGETS_5D))
    _discarded = P.readings(L, probs5, probs2, decs, did, cells)
    del _discarded
    missing = sorted((set(D.TARGETS_2D) | set(D.TARGETS_5D)) - set(capture))
    if missing:
        print(f"REFUSED: target rows not reached: {missing}", file=sys.stderr)
        return 4
    rec = D.Record()
    for dim, targets, prob in (("2d", D.TARGETS_2D, probs2["full"]), ("5d", D.TARGETS_5D, probs5["full"])):
        dn, de = decs[(dim, "full", "numpy")], decs[(dim, "full", "evr")]
        ref = D.mp_decompose(D.mp_fisher(prob["R"], prob["t0"], prob["b"]), prob["J"])
        part_eq = bool((ref["n_well"], ref["dim_inf"]) == (dn["n_well"], dn["dim_inf"]))
        kc, kq = kappa_g(dn), kappa_q(dn)
        for vid in targets:
            beta = capture[vid]["beta"]
            z_np, z_ev, z_in = P.z_well(dn, beta), P.z_well(de, beta), capture[vid]["z_ind"]
            z_ref = D.mp_z(ref, beta)
            rec.add(stat="Z_well", vector_id=vid, build="full/numpy", kappa2_C=kc, kappa2_CQ=kq,
                    rel_diff_drivers=D.rel(z_np, z_ev), rel_diff_eigen_vs_ref=D.rel(z_np, z_ref),
                    rel_diff_indep_vs_ref=D.rel(z_in, z_ref), ref_partition_equal=part_eq)
    rec.dump(out)
    verdict, n, total = confirm(rec.rows)
    print(json.dumps({"verdict": verdict, "rows_passing": n, "rows": total}))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--products", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"REFUSED: {a.out} exists", file=sys.stderr)
        return 9
    return run(a.products, a.out)


if __name__ == "__main__":
    sys.exit(main())
