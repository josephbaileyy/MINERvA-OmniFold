#!/usr/bin/env python3
"""MSR C-ROUTE blind diagnostic 2 (the director's ruling of 2026-11-23, option (i)).

For the 21 2D Z_well rows that failed C-ROUTE in diagnostic 1 (route-diag/diag.json) and three passing 5D Z_well rows
as controls, it writes ONLY:
    stat, vector_id, build,
    kappa2_C        kappa_2 of C = J F+ J^T (float64, as the eigen route forms it),
    kappa2_CQ       kappa_2 of C_Q = B_Q^T C B_Q (float64, as the eigen route decomposes it),
    rel_diff_drivers           Z_well with numpy eigh vs scipy evr (what N-PREC compares),
    rel_diff_eigen_vs_ref      the eigen route vs a 50-digit mpmath reference,
    rel_diff_indep_vs_ref      the independent route vs the same reference,
    ref_partition_equal        whether the reference's partition (n_well, dim U-inf) equals the float64 one.
The reference takes the same float64 inputs (R, t0, b, J) and follows the declared formulas (section 3.3) in mpmath at
50 digits, forming C = J F+ J^T there. It is computed for 2D only (the director's scope); on the three 5D control rows
the two reference fields are NaN and ref_partition_equal is null. It never writes a, b, a reference value, a label, a band, or anything a reading is
computed from; `Record` refuses any other field. msr_project.py is imported unchanged (sha asserted) and the readings it
computes in memory are discarded unwritten.

    msr_route_diag2.py --products DIR --out FILE.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import mpmath as mp
import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import msr_project as P  # noqa: E402

MSR_PROJECT_SHA = "ffb88e7b32d8cf1f5df03be96e9506b82c00f81f4f12123d6de0c134d7af994e"
DPS = 50
WELL_CUT = P.CUT   # 0.10, the declared cut; the tests vary it on toy problems only
# the rows, fixed before the run: diagnostic 1's 21 failing 2D Z_well rows, and three passing 5D Z_well controls
TARGETS_2D = tuple(f"2d#{i:03d}" for i in (13, 14, 15)) + tuple(f"2d#{i:03d}" for i in range(30, 48))
TARGETS_5D = ("5d#001", "5d#002", "5d#003")
FIELDS = ("stat", "vector_id", "build", "kappa2_C", "kappa2_CQ", "rel_diff_drivers", "rel_diff_eigen_vs_ref",
          "rel_diff_indep_vs_ref", "ref_partition_equal")
FLOATS = ("kappa2_C", "kappa2_CQ", "rel_diff_drivers", "rel_diff_eigen_vs_ref", "rel_diff_indep_vs_ref")


class Record:
    def __init__(self):
        self.rows: list[dict] = []

    def add(self, **row) -> None:
        if set(row) != set(FIELDS) or len(row) != len(FIELDS):
            raise ValueError(f"refused: fields {sorted(row)} are not exactly {sorted(FIELDS)}")
        if not (row["ref_partition_equal"] is None or isinstance(row["ref_partition_equal"], bool)):
            raise ValueError("refused: ref_partition_equal must be a bool or None")
        for k in FLOATS:
            if not isinstance(row[k], float):
                raise ValueError(f"refused: {k} must be a float")
        for k in ("stat", "vector_id", "build"):
            if not isinstance(row[k], str):
                raise ValueError(f"refused: {k} must be a string")
        self.rows.append(dict(row))

    def dump(self, path: Path) -> None:
        path.write_text(json.dumps({"schema": "msr-route-diag2/1", "fields": list(FIELDS), "rows": self.rows},
                                   indent=1) + "\n")


def rel(a, b) -> float:
    if a is None or b is None:
        return float("inf") if (a is None) != (b is None) else 0.0
    a, b = float(a), float(b)
    return float(abs(a - b) / max(abs(a), abs(b), 1e-300))


# ------------------------------------------------------------------------------------------- the 50-digit reference
def mp_fisher(R, t0: np.ndarray, b: np.ndarray):
    """F = R^T diag(1/mu) R over reco cells with mu = R t0 + b > 0 (did.fisher's definition), in mpmath."""
    Rc = sparse.csr_matrix(R)
    n = Rc.shape[1]
    F = mp.zeros(n, n)
    t = [mp.mpf(float(x)) for x in t0]
    for i in range(Rc.shape[0]):
        lo, hi = Rc.indptr[i], Rc.indptr[i + 1]
        if lo == hi:
            continue
        cols = Rc.indices[lo:hi]
        vals = [mp.mpf(float(v)) for v in Rc.data[lo:hi]]
        mu = mp.fsum(v * t[c] for v, c in zip(vals, cols)) + mp.mpf(float(b[i]))
        if mu <= 0:
            continue
        for a, ca in zip(vals, cols):
            for bb, cb in zip(vals, cols):
                F[ca, cb] += a * bb / mu
    return F


def mp_decompose(F, J_np: np.ndarray) -> dict:
    """Section 3.3 in mpmath: the range cut, F+, U-infinity by the generalized eigenproblem, C_Q and its widths."""
    J = mp.matrix(J_np.tolist())
    lam, V = mp.eigsy(F)
    n = F.rows
    lmax = max(lam[i] for i in range(n))
    rng = [i for i in range(n) if lam[i] > mp.mpf(repr(float(P.EIG_RTOL))) * lmax]
    nul = [i for i in range(n) if i not in rng]
    Fp = mp.zeros(n, n)
    for k in rng:
        v = V[:, k]
        Fp += (v * v.T) / lam[k]
    C = J * Fp * J.T
    m = J.rows
    if nul:
        VN = mp.matrix(n, len(nul))
        for jj, k in enumerate(nul):
            VN[:, jj] = V[:, k]
        Mm = J * VN * VN.T * J.T
        K = J * J.T
        Lc = mp.cholesky(K)
        Li = mp.inverse(Lc)
        A = Li * Mm * Li.T
        A = (A + A.T) / 2
        r2, Y = mp.eigsy(A)
        U = Li.T * Y
        inf = [i for i in range(m) if mp.sqrt(max(r2[i], 0)) > mp.mpf(repr(float(P.NULL_TOL)))]
        keep = [i for i in range(m) if i not in inf]
        Uq = mp.matrix(m, len(keep))
        for jj, k in enumerate(keep):
            Uq[:, jj] = U[:, k]
        BQ, _ = mp.qr(Uq, mode="skinny") if keep else (mp.matrix(m, 0), None)
        dim_inf = len(inf)
    else:
        BQ, dim_inf = mp.eye(m), 0
    CQ = BQ.T * C * BQ
    CQ = (CQ + CQ.T) / 2
    s2, Cv = mp.eigsy(CQ)
    w = BQ * Cv
    s = [mp.sqrt(max(s2[i], 0)) for i in range(CQ.rows)]
    well = [k for k in range(CQ.rows) if s[k] <= mp.mpf(repr(float(WELL_CUT)))]
    return {"w": w, "s": s, "well": well, "n_well": len(well), "dim_inf": dim_inf}


def mp_z(ref: dict, beta: np.ndarray):
    if ref["n_well"] == 0:
        return None
    b = mp.matrix([mp.mpf(float(x)) for x in beta])
    tot = mp.mpf(0)
    for k in ref["well"]:
        proj = (ref["w"][:, k].T * b)[0]
        tot += proj ** 2 / ref["s"][k] ** 2
    return mp.sqrt(tot)


# ------------------------------------------------------------------------------------------- the rule
RULE_TOL = 1e-8


def branch(rows: list[dict]) -> str:
    """The director's rule, fixed before the run, over the 21 2D rows (a NaN or inf difference counts as a miss).
      "independent-route":  the eigen route is within 1e-8 of the reference on all 21 rows and the independent route
                            misses on at least one;
      "c-formation":        on at least one row both routes miss the reference by more than 1e-8;
      "director":           anything else, including any row whose reference partition differs from the float64 one."""
    two = [r for r in rows if r["vector_id"].startswith("2d#")]
    if sorted(r["vector_id"] for r in two) != sorted(TARGETS_2D):
        return "director"
    if not all(r["ref_partition_equal"] is True for r in two):
        return "director"

    def ok(x):
        return x <= RULE_TOL   # False for NaN; False for inf
    eig_ok = [ok(r["rel_diff_eigen_vs_ref"]) for r in two]
    ind_ok = [ok(r["rel_diff_indep_vs_ref"]) for r in two]
    if all(eig_ok) and not all(ind_ok):
        return "independent-route"
    if any(not e and not i for e, i in zip(eig_ok, ind_ok)):
        return "c-formation"
    return "director"


# ------------------------------------------------------------------------------------------- the run
def install(capture: dict, targets: set) -> None:
    real = P.route_independent
    count = {"v": 0}

    def route(dec, beta):
        out = real(dec, beta)
        count["v"] += 1
        vid = f"{'5d' if beta.size == 16 else '2d'}#{count['v']:03d}"
        if vid in targets:
            capture[vid] = {"beta": np.array(beta, float), "z_ind": out[1]}
        return out
    P.route_independent = route


def run(prod: Path, out: Path) -> int:
    import did
    got = hashlib.sha256(Path(P.__file__).read_bytes()).hexdigest()
    if got != MSR_PROJECT_SHA:
        print(f"REFUSED: msr_project.py is {got}, not {MSR_PROJECT_SHA}", file=sys.stderr)
        return 9
    rec_controls, L = P.controls(prod)
    if not all(v["pass"] for v in rec_controls.values()):
        print("REFUSED: a first-block control failed", file=sys.stderr)
        return 3
    mp.mp.dps = DPS
    cells = np.asarray(L["a2"]["truths"]["nominal"]["cells"], int)
    probs5 = {"full": L["p5"], "A": P.problem_5d(L["z5"], "h2_halfA", did), "B": P.problem_5d(L["z5"], "h2_halfB", did)}
    probs2 = {h: P.problem_2d(L["z2"], k, cells) for h, k in (("full", "full"), ("A", "halfA"), ("B", "halfB"))}
    decs = {}
    for dim, probs in (("5d", probs5), ("2d", probs2)):
        for h, p in probs.items():
            for drv in ("numpy", "evr"):
                d = P.decompose(p["F"], p["J"], drv)
                d["keep"] = p["keep"]
                decs[(dim, h, drv)] = d
    capture: dict = {}
    install(capture, set(TARGETS_2D) | set(TARGETS_5D))
    _discarded = P.readings(L, probs5, probs2, decs, did, cells)
    del _discarded
    missing = sorted((set(TARGETS_2D) | set(TARGETS_5D)) - set(capture))
    if missing:
        print(f"REFUSED: target rows not reached: {missing}", file=sys.stderr)
        return 4
    rec = Record()
    for dim, targets, prob in (("2d", TARGETS_2D, probs2["full"]), ("5d", TARGETS_5D, probs5["full"])):
        dn, de = decs[(dim, "full", "numpy")], decs[(dim, "full", "evr")]
        ref = mp_decompose(mp_fisher(prob["R"], prob["t0"], prob["b"]), prob["J"]) if dim == "2d" else None
        part_eq = None if ref is None else bool((ref["n_well"], ref["dim_inf"]) == (dn["n_well"], dn["dim_inf"]))
        BQ = dn["w"]   # w = B_Q C_v with C_v orthogonal: span and kappa of C_Q equal those of w^T C w
        kq = float(np.linalg.cond(BQ.T @ dn["C"] @ BQ, 2)) if BQ.shape[1] else float("nan")
        kc = float(np.linalg.cond(dn["C"], 2))
        for vid in targets:
            beta = capture[vid]["beta"]
            z_np, z_ev, z_in = P.z_well(dn, beta), P.z_well(de, beta), capture[vid]["z_ind"]
            if ref is None:
                r_eig = r_ind = float("nan")
            else:
                z_ref = mp_z(ref, beta)
                r_eig, r_ind = rel(z_np, z_ref), rel(z_in, z_ref)
            rec.add(stat="Z_well", vector_id=vid, build="full/numpy", kappa2_C=kc, kappa2_CQ=kq,
                    rel_diff_drivers=rel(z_np, z_ev), rel_diff_eigen_vs_ref=r_eig, rel_diff_indep_vs_ref=r_ind,
                    ref_partition_equal=part_eq)
    rec.dump(out)
    print(json.dumps({"rows": len(rec.rows), "branch": branch(rec.rows)}))
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
