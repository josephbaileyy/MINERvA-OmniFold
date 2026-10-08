#!/usr/bin/env python3
"""Independent reproduction of the report-only kappa-breakdown (SPEC-20261007-kappa-breakdown.md).

Reuses from the frozen nd-unfolding/s5p_inference.py ONLY the per-experiment statistics stat_total and
stat_shape. The metric W = V[dom,dom] + diag(var[dom]), the seed-keyed prediction-residual draw
(rng([seed0, pseudo_seed, 0x4A02]).normal(size=109) * sqrt(var)), the claim rule, Holm with the determinacy
rule and the Clopper-Pearson interval are re-implemented here from the frozen definitions.

Usage: kappa_repro.py <worktree> <rc4_dir> <out_json>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.dont_write_bytecode = True  # never write __pycache__ into the read-only worktree

WORKTREE, RC4, OUT = (Path(a) for a in sys.argv[1:4])
sys.path.insert(0, str(WORKTREE / "nd-unfolding"))
import s5p_inference as si  # noqa: E402  (stat_total, stat_shape only)

ALPHA = 0.05
LEVEL = 0.95
STATS = ("total", "shape")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ----------------------------------------------------------------------------------------------- own rules
def clopper_pearson(k: int, B: int, level: float = LEVEL) -> tuple[float, float]:
    """Exact two-sided Clopper-Pearson interval for a binomial proportion k/B."""
    a = 1.0 - level
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a / 2.0, k, B - k + 1))
    hi = 1.0 if k == B else float(stats.beta.ppf(1.0 - a / 2.0, k + 1, B - k))
    return lo, hi


def status(lo: float, hi: float, th: float) -> str:
    if hi < th:
        return "below"
    if lo > th:
        return "above"
    return "straddles"


def holm_with_determinacy(claims: dict[str, dict], alpha: float = ALPHA) -> dict[str, dict]:
    """Holm step-down over the claims in increasing p (ties keep the insertion order, as a stable sort).
    Step i (0-based) has threshold alpha/(m-i). Below -> rejected; above -> 'not rejected' for this and all
    later steps; straddling (including touching) -> 'undetermined' for this and all later steps."""
    keys = list(claims)
    order = sorted(range(len(keys)), key=lambda j: claims[keys[j]]["p"])  # Python sort is stable
    m = len(keys)
    out: dict[str, dict] = {}
    carried = None
    for i, j in enumerate(order):
        key = keys[j]
        c = claims[key]
        th = alpha / (m - i)
        lo, hi = clopper_pearson(c["k"], c["B"])
        own = status(lo, hi, th)
        if carried is None:
            if own == "below":
                decision = "rejected"
            else:
                carried = decision = "not rejected" if own == "above" else "undetermined"
        else:
            decision = carried
        out[key] = {"k": c["k"], "B": c["B"], "p": c["p"], "step": i + 1, "threshold": th,
                    "interval": [lo, hi], "own_status": own, "decision": decision}
    return {k: out[k] for k in keys}


# ------------------------------------------------------------------------------------------ the statistics
class Null:
    def __init__(self, z, name: str, spec: dict, coefs: list[float]):
        self.name = name
        self.F = np.asarray(z[f"F__{name}"], float)
        self.seeds = np.asarray(z[f"seeds__{name}"], np.int64)
        self.mu = np.asarray(z[f"mu__{name}"], float)
        self.var = np.asarray(z[f"var__{name}"], float)
        self.dom = np.asarray(z[f"dom__{name}"], bool)
        self.S = np.asarray(z[f"S__{name}"], float)
        self.has_m1 = spec.get("m1") is not None
        self.d1 = np.asarray(z[f"d1__{name}"], float) if self.has_m1 else None
        self.seed0 = int(spec["surrogate_seed0"])
        self.B = int(self.F.shape[0])
        assert self.B == int(spec["B"]), (name, self.B, spec["B"])
        V = np.asarray(z["V"], float)
        d = self.dom
        self.W = V[np.ix_(d, d)] + np.diag(self.var[d])
        self.Winv = np.linalg.inv(self.W)
        # seed-keyed prediction residual, one per pseudo-experiment, over all 109 cells
        sd = np.sqrt(self.var)
        self.r_mu = np.array([self.mu + np.random.default_rng([self.seed0, int(s), 0x4A02]).normal(size=self.mu.size) * sd
                              for s in self.seeds])
        f = np.asarray(z["f_data"], float)
        self.t_obs = {"total": si.stat_total(f[d], self.mu[d], self.Winv),
                      "shape": si.stat_shape(f[d], self.mu[d], self.W)}
        self.coefs = coefs
        self._k_cache: dict[tuple, dict] = {}

    def null_k(self, shift: np.ndarray | None, key: tuple) -> dict:
        """k = #{T_null >= T_obs} for the ensemble shifted by ``shift``, both statistics."""
        if key in self._k_cache:
            return self._k_cache[key]
        d = self.dom
        F = self.F + (shift if shift is not None else 0.0)
        tt = np.array([si.stat_total(F[i][d], self.r_mu[i][d], self.Winv) for i in range(self.B)])
        ts = np.array([si.stat_shape(F[i][d], self.r_mu[i][d], self.W) for i in range(self.B)])
        res = {"total": int(np.sum(tt >= self.t_obs["total"])), "shape": int(np.sum(ts >= self.t_obs["shape"]))}
        self._k_cache[key] = res
        return res

    def process_variants(self) -> dict[str, dict]:
        return {f"c={c}": self.null_k(c * self.S, ("c", float(c))) for c in self.coefs}

    def m1_variants(self, kappa: float) -> dict[str, dict]:
        if not self.has_m1:
            return {}
        return {f"+{kappa}d1": self.null_k(kappa * self.d1, ("m1", float(kappa))),
                f"-{kappa}d1": self.null_k(-kappa * self.d1, ("m1", -float(kappa)))}

    def claim(self, variants: dict[str, dict]) -> dict[str, dict]:
        out = {}
        for s in STATS:
            k = max(v[s] for v in variants.values())
            out[s] = {"k": k, "B": self.B, "p": (k + 1) / (self.B + 1),
                      "variant_k": {n: v[s] for n, v in variants.items()}}
        return out

    def family_A(self, kappa: float) -> dict[str, dict]:
        return self.claim({**self.process_variants(), **self.m1_variants(kappa)})

    def family_B(self, kappa: float) -> dict[str, dict]:
        assert kappa >= 2
        return self.claim({**self.process_variants(), **self.m1_variants(2.0), **self.m1_variants(kappa)})


class Reading:
    def __init__(self, npz: Path):
        self.npz = npz
        self.manifest = json.loads(Path(str(npz) + ".manifest.json").read_text())
        z = np.load(npz, allow_pickle=False)
        coefs = [float(c) for c in self.manifest["shift_coefficients"]]
        self.nulls = {n: Null(z, n, spec, coefs) for n, spec in self.manifest["nulls"].items()}

    def evaluate(self, family: str, kappa: float) -> dict[str, dict]:
        claims = {}
        for n, nl in self.nulls.items():
            c = nl.family_A(kappa) if family == "A" else nl.family_B(kappa)
            for s in STATS:
                claims[f"{n}:{s}"] = c[s]
        dec = holm_with_determinacy({k: {"k": v["k"], "B": v["B"], "p": v["p"]} for k, v in claims.items()})
        for k in dec:
            dec[k]["variant_k"] = claims[k]["variant_k"]
        return dec


# ------------------------------------------------------------------------------------------- references
def compare(dec: dict, expected: dict, decisions_key: str, test_suffix: str) -> dict:
    problems = []
    for key, d in dec.items():
        g, s = key.split(":")
        e_test = expected["tests"][g][s + test_suffix]
        e_dec = expected[decisions_key][key]
        for src, e in (("tests", e_test), (decisions_key, e_dec)):
            if int(e["k"]) != d["k"] or int(e["B"]) != d["B"]:
                problems.append(f"{key} {src}: k/B {e['k']}/{e['B']} vs {d['k']}/{d['B']}")
            if not np.isclose(d["p"], e["p"], rtol=1e-12, atol=0.0):
                problems.append(f"{key} {src}: p {e['p']} vs {d['p']}")
        if e_dec["decision"] != d["decision"]:
            problems.append(f"{key}: decision {e_dec['decision']} vs {d['decision']}")
        if not np.isclose(e_dec["threshold"], d["threshold"], rtol=1e-12, atol=0):
            problems.append(f"{key}: threshold {e_dec['threshold']} vs {d['threshold']}")
        if not np.allclose(e_dec["interval"], d["interval"], rtol=1e-12, atol=0):
            problems.append(f"{key}: interval {e_dec['interval']} vs {d['interval']}")
    return {"agree": not problems, "problems": problems, "n_tests": len(dec)}


def extra_reference_checks(r: Reading, expected: dict) -> dict:
    """Beyond the required check: T_obs and every per-variant k (incl. the kappa_robust variants)."""
    problems = []
    for n, nl in r.nulls.items():
        e = expected["tests"][n]
        for s in STATS:
            if not np.isclose(nl.t_obs[s], e[f"T_{s}_obs"], rtol=1e-12, atol=0):
                problems.append(f"{n}: T_{s}_obs {e[f'T_{s}_obs']} vs {nl.t_obs[s]}")
        mine = {**{f"{c}": nl.null_k(c * nl.S, ("c", float(c))) for c in nl.coefs}}
        if nl.has_m1:
            mine["m1+2"] = nl.null_k(2.0 * nl.d1, ("m1", 2.0))
            mine["m1-2"] = nl.null_k(-2.0 * nl.d1, ("m1", -2.0))
        for name, v in e["variants"].items():
            for s in STATS:
                if int(v[s]["k"]) != mine[name][s]:
                    problems.append(f"{n} variant {name} {s}: k {v[s]['k']} vs {mine[name][s]}")
        for name, v in e.get("robustness_variants", {}).items():
            sign = 1.0 if "+" in name else -1.0
            kap = float(name.split("+" if sign > 0 else "-")[1])
            km = nl.null_k(sign * kap * nl.d1, ("m1", sign * kap))
            for s in STATS:
                if int(v[s]["k"]) != km[s]:
                    problems.append(f"{n} robust {name} {s}: k {v[s]['k']} vs {km[s]}")
    return {"agree": not problems, "problems": problems}


def table(dec: dict) -> dict:
    return {k: {f: v[f] for f in ("k", "B", "p", "step", "threshold", "interval", "own_status", "decision", "variant_k")}
            for k, v in dec.items()}


def main() -> int:
    readings = {"frozen": (RC4 / "data/frozen/inference_sufficient.npz", RC4 / "expected/joint-evaluate.json"),
                "union": (RC4 / "data/recovery-union/inference_sufficient.npz", RC4 / "expected/resolved-evaluate.json")}
    out = {"code_sha256": sha256(Path(__file__)), "inputs": {}, "references": {}}
    R = {}
    for name, (npz, exp) in readings.items():
        out["inputs"][name] = {"npz": str(npz), "npz_sha256": sha256(npz),
                               "manifest_sha256": sha256(Path(str(npz) + ".manifest.json")),
                               "expected": str(exp), "expected_sha256": sha256(exp)}
        R[name] = Reading(npz)
        expected = json.loads(exp.read_text())
        a2 = R[name].evaluate("A", 2.0)
        b3 = R[name].evaluate("B", 3.0)
        out["references"][name] = {
            "family_A_kappa2_vs_decisions": compare(a2, expected, "decisions", ""),
            "family_B_kappa3_vs_decisions_robust_kappa": compare(b3, expected, "decisions_robust_kappa", "_robust"),
            "extra_Tobs_and_per_variant_k": extra_reference_checks(R[name], expected),
            "family_A_kappa2": table(a2), "family_B_kappa3": table(b3)}
        print(name, {k: v["agree"] for k, v in out["references"][name].items() if isinstance(v, dict) and "agree" in v},
              flush=True)

    k2 = [0, 2, 3, 5.2546875, 5.25625, 5.6640625, 5.665625, 6.478125, 6.4796875, 7.2109375, 7.2125, 8.459375,
          8.4609375, 10.328125, 10.3296875, 12]
    k3 = [5.16875, 5.1703125, 6.540625, 6.5421875, 6.8453125, 6.846875]
    out["task2_frozen_family_A"] = {repr(float(k)): table(R["frozen"].evaluate("A", float(k))) for k in k2}
    print("task2 done", flush=True)
    out["task3_union_family_A"] = {repr(float(k)): table(R["union"].evaluate("A", float(k))) for k in k3}
    print("task3 done", flush=True)
    grid = [0.5 * i for i in range(25)]
    mono = {repr(k): {key: v["k"] for key, v in R["frozen"].evaluate("A", k).items()} for k in grid}
    decreases = []
    for i in range(1, len(grid)):
        a, b = mono[repr(grid[i - 1])], mono[repr(grid[i])]
        for key in a:
            if b[key] < a[key]:
                decreases.append({"test": key, "from_kappa": grid[i - 1], "to_kappa": grid[i], "k_from": a[key], "k_to": b[key]})
    out["task4_monotonicity_frozen_family_A"] = {"grid": grid, "claim_k": mono, "decreases": decreases}
    print("task4 done; decreases:", decreases, flush=True)
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
