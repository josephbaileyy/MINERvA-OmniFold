#!/usr/bin/env python3
"""Report-only kappa-breakdown of the ten joint-test decisions (SPEC-20261007-kappa-breakdown.md).

For each kappa on the frozen grid, re-evaluates the full ten-test family under Holm with determinacy, with the
sub-fine-grid variants at +-kappa*delta_M1 (family A: pointwise; family B: kappa = 2 variants plus +-kappa).
Uses the release's standalone restatement of the frozen rules (``publication/release/replay_inference.py``)
unchanged, on existing sufficient inputs only.

MEASURES: the sensitivity of the frozen decisions to rescaling the frozen shift delta_M1 along that one direction.
CANNOT AUTHORIZE: any change to a frozen decision; any statement about convergence, the true residual, other shift
directions, or detector-model adequacy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

REPLAY = Path(__file__).resolve().parents[1] / "release" / "replay_inference.py"
REPLAY_SHA256 = "41f4af05eed0c07ad74acad73900fd22474e8bbac0e58f2e54eb424dddcbd7a4"
GRID = np.round(np.arange(0, 241) * 0.05, 10)
BISECT_STEPS = 5
RTOL = 1e-12


def load_replay():
    digest = hashlib.sha256(REPLAY.read_bytes()).hexdigest()
    if digest != REPLAY_SHA256:
        raise SystemExit(f"replay_inference.py sha256 {digest} != frozen {REPLAY_SHA256}")
    sys.path.insert(0, str(REPLAY.parent))
    import replay_inference as ri
    return ri


class Scan:
    def __init__(self, ri, z, man):
        self.ri, self.z, self.man = ri, z, man
        self.V, self.f_data = z["V"], z["f_data"]
        self.alpha = man["alpha_family"]
        self.keys = list(man["nulls"])
        self.base, self.obs, self.cache = {}, {}, {}
        for key, nm in man["nulls"].items():
            mu, var, dom = z[f"mu__{key}"], z[f"var__{key}"], z[f"dom__{key}"].astype(bool)
            tt_o, ts_o = ri.statistics(self.f_data[None, :], mu, var, self.V, dom, 0, draw=False)
            self.obs[key] = {"total": float(tt_o[0]), "shape": float(ts_o[0])}
            S = z[f"S__{key}"] if f"S__{key}" in z.files else None
            coefs = man["shift_coefficients"] if S is not None else [0.0]
            self.base[key] = {}
            for c in coefs:
                tt, ts = self._stats(key, (c * S) if S is not None else 0.0)
                self.base[key][str(c)] = self._pv(key, tt, ts)

    def _stats(self, key, shift):
        z, nm = self.z, self.man["nulls"][key]
        mu, var, dom = z[f"mu__{key}"], z[f"var__{key}"], z[f"dom__{key}"].astype(bool)
        return self.ri.statistics(z[f"F__{key}"] + shift, mu, var, self.V, dom, nm["surrogate_seed0"],
                                  seeds=z[f"seeds__{key}"])

    def _pv(self, key, tt, ts):
        return {s: self.ri.mc_pvalue(self.obs[key][s], t) for s, t in (("total", tt), ("shape", ts))}

    def m1(self, key, kappa: float) -> dict:
        """p-values of the +kappa and -kappa variants (memoized)."""
        ck = (key, round(float(kappa), 9))
        if ck not in self.cache:
            d1 = self.z[f"d1__{key}"]
            self.cache[ck] = {f"m1+{kappa:g}": self._pv(key, *self._stats(key, kappa * d1)),
                              f"m1-{kappa:g}": self._pv(key, *self._stats(key, -kappa * d1))}
        return self.cache[ck]

    def family(self, kappa: float, fam: str) -> dict:
        claims, detail = {}, {}
        for key, nm in self.man["nulls"].items():
            variants = dict(self.base[key])
            if nm["m1"] is not None:
                if fam == "B":
                    variants.update(self.m1(key, 2.0))
                variants.update(self.m1(key, kappa))
            for s in ("total", "shape"):
                name, claim = max(((n, v[s]) for n, v in variants.items()), key=lambda x: x[1]["p"])
                claims[f"{key}:{s}"] = {k: claim[k] for k in ("p", "k", "B")}
                detail[f"{key}:{s}"] = {"argmax_variant": name, "kappa_dependent": nm["m1"] is not None}
        dec = self.ri.holm_determined(claims, self.alpha)
        for t, d in dec.items():
            lo, hi = d["interval"]
            own = "below" if hi < d["threshold"] else ("above" if lo > d["threshold"] else "straddles")
            d.update(detail[t], own_interval_vs_threshold=own)
        return dec


def reference_checks(scan: Scan, expected: dict) -> list[str]:
    bad = []

    def close(a, b):
        return bool(np.isclose(float(a), float(b), rtol=RTOL, atol=0.0))

    a2, b3 = scan.family(2.0, "A"), scan.family(3.0, "B")
    for t, d in a2.items():
        key, s = t.split(":")
        ref = expected["tests"][key][s]
        for f in ("p", "k", "B"):
            if not close(d[f], ref[f]):
                bad.append(f"A@2 {t}.{f}: {d[f]} != {ref[f]}")
        if d["decision"] != expected["decisions"][t]["decision"]:
            bad.append(f"A@2 {t}.decision: {d['decision']} != {expected['decisions'][t]['decision']}")
    for t, d in b3.items():
        key, s = t.split(":")
        ref = expected["tests"][key][s + "_robust"]
        for f in ("p", "k", "B"):
            if not close(d[f], ref[f]):
                bad.append(f"B@3 {t}.{f}: {d[f]} != {ref[f]}")
        if d["decision"] != expected["decisions_robust_kappa"][t]["decision"]:
            bad.append(f"B@3 {t}.decision: {d['decision']} != {expected['decisions_robust_kappa'][t]['decision']}")
    return bad


def compact(dec: dict) -> dict:
    return {t: {"p": d["p"], "k": d["k"], "B": d["B"], "threshold": d["threshold"], "interval": d["interval"],
                "decision": d["decision"], "own": d["own_interval_vs_threshold"], "argmax": d["argmax_variant"]}
            for t, d in dec.items()}


def run(scan: Scan, fam: str, log) -> dict:
    grid = [float(k) for k in GRID if fam == "A" or k >= 2.0]
    points = {}
    t0 = time.time()
    for i, k in enumerate(grid):
        points[k] = compact(scan.family(k, fam))
        if i % 20 == 0:
            log(f"  family {fam} kappa {k:5.2f}  ({time.time() - t0:7.1f} s)")
    tests = list(points[grid[0]])
    brackets = []
    for k0, k1 in zip(grid[:-1], grid[1:]):
        for t in tests:
            if points[k0][t]["decision"] == points[k1][t]["decision"]:
                continue
            lo, hi = k0, k1
            d_lo = points[k0][t]["decision"]
            for _ in range(BISECT_STEPS):
                mid = round((lo + hi) / 2, 9)
                if mid not in points:
                    points[mid] = compact(scan.family(mid, fam))
                if points[mid][t]["decision"] == d_lo:
                    lo = mid
                else:
                    hi = mid
            brackets.append({"test": t, "from": d_lo, "to": points[k1][t]["decision"], "grid_cell": [k0, k1],
                             "bracket": [lo, hi], "decision_at_bracket_hi": points[hi][t]["decision"],
                             "own_at_bracket_hi": points[hi][t]["own"]})
    mono = {}
    for t in tests:
        ks = [points[k][t]["k"] for k in grid]
        decs = [points[k][t]["decision"] for k in grid]
        k_decreases = [grid[i + 1] for i in range(len(grid) - 1) if ks[i + 1] < ks[i]]
        regains = [grid[i + 1] for i in range(len(grid) - 1) if decs[i + 1] == "rejected" and decs[i] != "rejected"]
        intervals, start = [], None
        for k, d in zip(grid, decs):
            if d == "rejected" and start is None:
                start = k
            if d != "rejected" and start is not None:
                intervals.append([start, prev])
                start = None
            prev = k
        if start is not None:
            intervals.append([start, grid[-1]])
        first_loss = next((k for k, d in zip(grid, decs) if d != "rejected"), None)
        mono[t] = {"k_decreases_at": k_decreases, "rejection_regained_at": regains, "rejected_intervals": intervals,
                   "first_grid_loss": first_loss,
                   "first_loss_state": None if first_loss is None else points[first_loss][t]["decision"]}
    return {"grid": grid, "points": {f"{k:.9g}": v for k, v in sorted(points.items())}, "brackets": brackets,
            "monotonicity": mono}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--expected", type=Path, required=True)
    ap.add_argument("--reading", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    ri = load_replay()
    man = json.loads(Path(str(a.npz) + ".manifest.json").read_text())
    z = np.load(a.npz, allow_pickle=False)

    def log(msg):
        print(msg, flush=True)

    t0 = time.time()
    scan = Scan(ri, z, man)
    bad = reference_checks(scan, json.loads(a.expected.read_text()))
    log(f"[{a.reading}] reference checks (A@2 vs decisions, B@3 vs decisions_robust_kappa): "
        f"{'AGREE' if not bad else 'DIFFER'} ({len(bad)})")
    for b in bad:
        log("  " + b)
    out = {"schema": "kappa-breakdown/1", "spec": "publication/kappa/SPEC-20261007-kappa-breakdown.md",
           "reading": a.reading, "npz_sha256": hashlib.sha256(a.npz.read_bytes()).hexdigest(),
           "expected_sha256": hashlib.sha256(a.expected.read_bytes()).hexdigest(), "replay_sha256": REPLAY_SHA256,
           "observed": scan.obs, "reference_checks": {"agree": not bad, "differences": bad}}
    if bad:
        a.out.write_text(json.dumps(out, indent=1) + "\n")
        log("STOP: a reference disagrees (SPEC sec. 6); no thresholds computed")
        return 2
    for fam in ("A", "B"):
        out[f"family_{fam}"] = run(scan, fam, log)
    out["wall_seconds"] = time.time() - t0
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    log(f"[{a.reading}] done in {out['wall_seconds']:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
