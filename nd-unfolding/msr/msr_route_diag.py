#!/usr/bin/env python3
"""MSR C-ROUTE blind diagnostic (the director's ruling of 2026-11-23, option (a)).

It imports the merged msr_project.py unchanged (its sha256 is asserted) and recomputes, on the committed products, every
comparison C-ROUTE makes: S_poor and Z_well per bias vector (route_independent) and r_poor / r_well per oracle arm
(r_independent), each against the eigen route. For each comparison it writes ONLY:
    stat, vector_id, build, rel_diff = |a - b| / max(|a|, |b|, 1e-300), passes_current_bar (bool),
    kappa2 (of the matrix the independent route solves), ten_kappa_eps = 10 * kappa2 * eps(float64).
It never writes a, b, |a|, a label, a band, or anything a reading is computed from: `Record` refuses any other field,
and test_msr_route_diag.py fails if one is written. The readings msr_project computes in memory along the way are
discarded unwritten.

    msr_route_diag.py --products DIR --out FILE.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import msr_project as P  # noqa: E402

MSR_PROJECT_SHA = "ffb88e7b32d8cf1f5df03be96e9506b82c00f81f4f12123d6de0c134d7af994e"   # merged at 88994c9a
FIELDS = ("stat", "vector_id", "build", "rel_diff", "passes_current_bar", "kappa2", "ten_kappa_eps")
EPS = float(np.finfo(np.float64).eps)


class Record:
    """The only writer: a list of rows whose keys are exactly FIELDS, with the declared types."""

    def __init__(self):
        self.rows: list[dict] = []

    def add(self, **row) -> None:
        if tuple(sorted(row)) != tuple(sorted(FIELDS)):
            raise ValueError(f"refused: fields {sorted(row)} are not exactly {sorted(FIELDS)}")
        if not isinstance(row["passes_current_bar"], bool):
            raise ValueError("refused: passes_current_bar must be a bool")
        for k in ("rel_diff", "kappa2", "ten_kappa_eps"):
            if not isinstance(row[k], float):
                raise ValueError(f"refused: {k} must be a float")
        if not (isinstance(row["stat"], str) and isinstance(row["vector_id"], str) and isinstance(row["build"], str)):
            raise ValueError("refused: stat, vector_id and build must be strings")
        self.rows.append(dict(row))

    def dump(self, path: Path) -> None:
        for r in self.rows:
            assert set(r) == set(FIELDS)
        path.write_text(json.dumps({"schema": "msr-route-diag/1", "fields": list(FIELDS), "rows": self.rows},
                                   indent=1) + "\n")


def rel(a, b) -> float:
    if a is None or b is None:
        return float("inf") if (a is None) != (b is None) else 0.0
    return float(abs(a - b) / max(abs(a), abs(b), 1e-300))


def passes(a, b) -> bool:
    """C-ROUTE's current bar for one value, as msr_project applies it: |b - a| <= 1e-10 + 1e-8 |a| (a = eigen route)."""
    if a is None or b is None:
        return (a is None) == (b is None)
    return bool(abs(b - a) <= 1e-10 + 1e-8 * abs(a))


def kappa_solve(dec: dict) -> float:
    """kappa_2 of W^T C W, the matrix route_independent solves for Z_well."""
    if dec["n_well"] == 0:
        return float("nan")
    W = dec["w"][:, dec["well"]]
    return float(np.linalg.cond(W.T @ dec["C"] @ W, 2))


def kappa_qr(dec: dict) -> float:
    """kappa_2 of the well-constrained block W, the matrix the QR projector route factors (S_poor, r)."""
    if dec["n_well"] == 0:
        return float("nan")
    return float(np.linalg.cond(dec["w"][:, dec["well"]], 2))


def install(rec: Record) -> None:
    """Wrap the two independent-route functions so each comparison is recorded as it is made (vector ids by order)."""
    real_route, real_r = P.route_independent, P.r_independent
    count = {"v": 0, "arm": 0}

    def route(dec, beta):
        sp_ind, z_ind = real_route(dec, beta)
        sp_eig, z_eig = P.s_poor(dec, beta), P.z_well(dec, beta)
        count["v"] += 1
        vid = f"{'5d' if beta.size == 16 else '2d'}#{count['v']:03d}"
        for stat, a, b, kap in (("S_poor", sp_eig, sp_ind, kappa_qr(dec)), ("Z_well", z_eig, z_ind, kappa_solve(dec))):
            rec.add(stat=stat, vector_id=vid, build="full/numpy", rel_diff=rel(a, b), passes_current_bar=passes(a, b),
                    kappa2=kap, ten_kappa_eps=float(10.0 * kap * EPS))
        return sp_ind, z_ind

    def r_route(dec, arm, b0):
        ind = real_r(dec, arm, b0)
        eig = P.r_pair(dec, arm, b0)
        count["arm"] += 1
        vid = f"arm#{count['arm']}"
        kap = kappa_qr(dec)
        for stat in ("r_poor", "r_well"):
            rec.add(stat=stat, vector_id=vid, build="full/numpy", rel_diff=rel(eig[stat], ind[stat]),
                    passes_current_bar=passes(eig[stat], ind[stat]), kappa2=kap, ten_kappa_eps=float(10.0 * kap * EPS))
        return ind

    P.route_independent, P.r_independent = route, r_route


def run(prod: Path, out: Path) -> int:
    import did
    got = hashlib.sha256(Path(P.__file__).read_bytes()).hexdigest()
    if got != MSR_PROJECT_SHA:
        print(f"REFUSED: msr_project.py is {got}, not the merged {MSR_PROJECT_SHA}", file=sys.stderr)
        return 9
    rec_controls, L = P.controls(prod)
    if not all(v["pass"] for v in rec_controls.values()):
        print("REFUSED: a first-block control failed", file=sys.stderr)
        return 3
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
    rec = Record()
    install(rec)
    _discarded = P.readings(L, probs5, probs2, decs, did, cells)   # computed in memory, never written
    del _discarded
    rec.dump(out)
    n_fail = sum(1 for r in rec.rows if not r["passes_current_bar"])
    print(json.dumps({"comparisons": len(rec.rows), "failing_current_bar": n_fail}))
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
