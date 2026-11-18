#!/usr/bin/env python3
"""PILOT-FB §3: the fixed bin edges, per model role and feature, from the unjittered base's matrices. Numpy only.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/pilot-fb/
PILOT-FB-DECLARATION.md rev 3 (§2 items 3-6, §3 rules 1-7), bound by PILOT-FB-BINDING-1 at M_PFB 522ac0b6.

For a role r and feature f, F is the fit column and U the fit column together with the scored column. The policy
(G0 refuses unless every rule holds):
  1. every value of U is finite;
  2. no value v of U has 5e-36 < |v| < 2e-35 (the zero band), so no jitter carries a value across +-K;
  3. z = [any F <= -K] + [any F > K], K = float64(float32(1e-35)) (LightGBM's kZeroThreshold, meta.h:56), and
     n = max_bin - z - 1;
  4. s(u) = float64(numpy.spacing(float32(|u|))): the protocol jitter's step bound (s5e_trace.py:362-364);
  5. a gap between consecutive distinct values u_k < u_{k+1} of U is admissible iff
     u_k + s(u_k)/2 < u_{k+1} - s(u_{k+1})/2; its edge is the float64 midpoint of those two numbers, strictly between
     them, with |edge| > 2e-35;
  6. placement: B_k = #(F <= u_k); edge i (i = 1..n) aims at t_i = q_i * N, at the admissible gap minimizing
     |B_k - t_i| (ties to the lower k); a gap not above the previous edge's moves to the next admissible gap above it;
     none left: INFEASIBLE (no backtracking, padding, smaller count or fallback);
  7. one native LightGBM forced-bins JSON per (set, role), `[{"feature": f, "bin_upper_bound": [...]}]`, edges written
     at 17 significant digits.

The intended upper-bound list of (r, f) is, sorted: -K if z counts a non-positive side, +K if a positive side, the n
edges, +inf. G2 and G3 (fb_pilot_gates.py) use exactly that list.

MEASURES: the edges a policy places. CANNOT AUTHORIZE: a reading.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

K = float(np.float32(1e-35))  # LightGBM's kZeroThreshold: `const double kZeroThreshold = 1e-35f` (meta.h:56)
ZERO_BAND = (5e-36, 2e-35)
EDGE_MIN_ABS = 2e-35
ROLES = ("clf1", "reg", "clf2", "ref")
SETS = {"E1": {"max_bin": 255, "offset": 0.0}, "E2": {"max_bin": 255, "offset": 0.5}, "E3": {"max_bin": 127, "offset": 0.0}}


class Infeasible(RuntimeError):
    """G0 refuses: a rule fails, or a feature has too few admissible gaps (§5.1, INFEASIBLE)."""


def half_step(u: np.ndarray) -> np.ndarray:
    """s(u)/2 with s(u) = float64(numpy.spacing(float32(|u|))) (§3 rule 4)."""
    return 0.5 * np.spacing(np.abs(np.asarray(u, np.float32))).astype(np.float64)


def zero_bounds(F: np.ndarray) -> list:
    """The zero bounds LightGBM places for a fit column (bin.cpp:183-197): -K if any value <= -K, +K if any > K."""
    F = np.asarray(F, np.float64)
    out = []
    if np.any(F <= -K):
        out.append(-K)
    if np.any(F > K):
        out.append(K)
    return out


def admissible_gaps(U: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(the lower value u_k of each admissible gap, its edge), over the distinct values of U (§3 rule 5)."""
    u = np.unique(np.asarray(U, np.float64))
    if u.size < 2:
        return np.empty(0), np.empty(0)
    lo = u[:-1] + half_step(u[:-1])
    hi = u[1:] - half_step(u[1:])
    ok = lo < hi
    e = (lo + hi) / 2.0
    ok &= (lo < e) & (e < hi) & (np.abs(e) > EDGE_MIN_ABS)
    return u[:-1][ok], e[ok]


def check_policy(F: np.ndarray, U: np.ndarray, what: str) -> None:
    """§3 rules 1-2; raises Infeasible."""
    U = np.asarray(U, np.float64)
    if not np.all(np.isfinite(U)):
        raise Infeasible(f"{what}: rule 1, a value is not finite")
    a = np.abs(U)
    if np.any((a > ZERO_BAND[0]) & (a < ZERO_BAND[1])):
        raise Infeasible(f"{what}: rule 2, a value lies in the zero band (5e-36, 2e-35)")
    if F.size == 0:
        raise Infeasible(f"{what}: the fit column is empty")


def place(F: np.ndarray, U: np.ndarray, max_bin: int, offset: float, what: str = "") -> dict:
    """§3 rules 3-6 for one role and feature: {"z", "n", "zero_bounds", "edges", "admissible", "intended"}."""
    F = np.asarray(F, np.float64)
    check_policy(F, U, what)
    zb = zero_bounds(F)
    n = int(max_bin) - len(zb) - 1
    lower, edges = admissible_gaps(U)
    if lower.size < n:
        raise Infeasible(f"{what}: {lower.size} admissible gaps for {n} edges")
    Fs = np.sort(F)
    N = Fs.size
    B = np.searchsorted(Fs, lower, side="right").astype(np.float64)  # #(F <= u_k), non-decreasing in k
    chosen = []
    prev = -1
    for i in range(1, n + 1):
        t = (i + offset) / (n + 1) * N
        j = int(np.searchsorted(B, t, side="left"))
        cands = [c for c in (j - 1, j) if 0 <= c < B.size]
        k = min(cands, key=lambda c: (abs(B[c] - t), c))
        if k <= prev:
            k = prev + 1
        if k >= B.size:
            raise Infeasible(f"{what}: the next-gap walk ran out of admissible gaps at edge {i} of {n}")
        chosen.append(k)
        prev = k
    out_edges = [float(edges[k]) for k in chosen]
    intended = sorted(zb + out_edges + [math.inf])
    if len(intended) != int(max_bin):
        raise Infeasible(f"{what}: the intended list has {len(intended)} bounds, not max_bin {max_bin}")
    return {"z": len(zb), "n": n, "zero_bounds": zb, "edges": out_edges, "admissible": int(lower.size),
            "intended": intended}


def edge_text(e: float) -> str:
    """An edge at 17 significant digits (§3 rule 5)."""
    return format(float(e), ".17g")


def forcedbins_json(per_feature: list) -> str:
    """The native LightGBM forced-bins file for one role: features 0..4 in the role's column order."""
    items = [f'{{"feature": {f}, "bin_upper_bound": [{", ".join(edge_text(e) for e in p["edges"])}]}}'
             for f, p in enumerate(per_feature)]
    return "[" + ", ".join(items) + "]\n"


def build_edges(matrices: dict, out_dir: Path, sets: dict = SETS) -> dict:
    """G0 and §3 rule 7. matrices = {role: (fit [rows, 5], scored [rows, 5] or None)}. Writes
    <out_dir>/<set>_<role>.json and INDEX.json; returns the index. Raises Infeasible, writing nothing more."""
    import hashlib
    out_dir = Path(out_dir)
    if set(matrices) != set(ROLES):
        raise ValueError(f"the roles are {sorted(matrices)}, not {sorted(ROLES)}")
    plan = {}
    for s, cfg in sets.items():
        for r in ROLES:
            fit, scored = matrices[r]
            fit = np.asarray(fit, np.float64)
            U_all = fit if scored is None else np.vstack([fit, np.asarray(scored, np.float64)])
            if fit.ndim != 2 or fit.shape[1] != 5:
                raise ValueError(f"{r}: the fit matrix is {fit.shape}, not (rows, 5)")
            plan[(s, r)] = [place(fit[:, f], U_all[:, f], cfg["max_bin"], cfg["offset"], f"{s}/{r}/feature {f}")
                            for f in range(5)]
    out_dir.mkdir(parents=True, exist_ok=False)
    index = {"schema": "pfb-edges/1", "K": K, "sets": {}}
    for (s, r), per in plan.items():
        text = forcedbins_json(per)
        p = out_dir / f"{s}_{r}.json"
        p.write_text(text)
        index["sets"].setdefault(s, {"max_bin": sets[s]["max_bin"], "offset": sets[s]["offset"], "roles": {}})
        index["sets"][s]["roles"][r] = {
            "file": p.name, "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "features": [{k: v for k, v in q.items() if k != "edges"} for q in per]}
    (out_dir / "INDEX.json").write_text(json.dumps(index, indent=1, allow_nan=True) + "\n")
    return index


def load_intended(index_path: Path, s: str, r: str) -> list:
    """The intended upper-bound lists of (set, role), feature by feature, from INDEX.json (+inf restored)."""
    idx = json.loads(Path(index_path).read_text())
    return [np.asarray(q["intended"], np.float64) for q in idx["sets"][s]["roles"][r]["features"]]
