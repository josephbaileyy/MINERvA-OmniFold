"""Reference assessment (c): a known-function toy where the attainable recovery at k is computable.

Amendment 1 (c): "a known-function toy (1-D Gaussian smearing with a known efficiency curve) where
the attainable recovery at k iterations is computable, testing whether `1-(1-a)^k` bounds, matches
or undershoots it."

The toy is one variable x (an E_avail stand-in) with

* a known truth density p(x) (gamma), binned in the endpoint's seven bins;
* a known efficiency eps(x) (logistic, rising from eps_lo at x = 0 to eps_hi at large x);
* known Gaussian smearing y = x + N(0, sigma(x)), sigma(x) = f (x + x_ref) -- f = 0 is the
  no-smearing limit the reference model assumes;
* the historical injection: the clipped exponential tilt at amplitude 0.35, standardized by the
  toy's own quartiles, clip 3.

Because every ingredient is a function, the iteration can be run on EXPECTED histograms -- infinite
statistics -- so what it reaches at iteration k is the attainable recovery of that estimator on
that response, with no sampling noise. Both miss-handling rules of the engine's binned twin are
run: misses carried (the engine's own rule, whose zero-smearing limit IS `1-(1-a)^k`) and textbook
efficiency correction. A finite-sample run at the historical size, through the same
`binned_unfolding.binned_omnifold` the references use, checks the expected-value iteration and
measures what finite statistics cost.

Prospective only: this says what the reference model describes, never what the historical verdict
was.
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

import common as cm

if str(cm.SCALAR_DIR) not in sys.path:
    sys.path.insert(0, str(cm.SCALAR_DIR))
import binned_unfolding as bu       # noqa: E402

scm = cm.scm
EDGES = cm.ENDPOINT_EDGES
TOY = {"density": "gamma(shape=1.1, scale=1.2) on [0, 100] GeV",
       "shape": 1.1, "scale": 1.2, "x_max": 100.0,
       "efficiency": "eps_lo + (eps_hi - eps_lo) / (1 + exp(-(x - x0)/w))",
       "eps_lo": 0.02, "eps_hi": 0.75, "x0": 0.8, "w": 0.5,
       "sigma": "f * (x + x_ref)", "x_ref": 0.1,
       "injection": "clipped exponential tilt, amplitude 0.35, clip 3, toy quartiles"}
SMEARINGS = (0.0, 0.05, 0.15, 0.30)
_PHI = np.vectorize(lambda z: 0.5 * (1.0 + math.erf(z / math.sqrt(2.0))))


def grid(n: int = 20000) -> tuple[np.ndarray, np.ndarray]:
    """A fine quadrature grid over [0, x_max) and the truth mass in each cell."""
    from math import lgamma
    edges = np.concatenate([np.linspace(0.0, 5.0, n // 2 + 1)[:-1],
                            np.geomspace(5.0, TOY["x_max"], n // 2 + 1)])
    x = 0.5 * (edges[:-1] + edges[1:])
    k, theta = TOY["shape"], TOY["scale"]
    logp = (k - 1) * np.log(x) - x / theta - lgamma(k) - k * math.log(theta)
    p = np.exp(logp) * np.diff(edges)
    return x, p / p.sum()


def efficiency(x: np.ndarray) -> np.ndarray:
    return TOY["eps_lo"] + (TOY["eps_hi"] - TOY["eps_lo"]) / (
        1.0 + np.exp(-(x - TOY["x0"]) / TOY["w"]))


def tilt_weights(x: np.ndarray, p: np.ndarray, amplitude: float = 0.35, clip_z: float = 3.0
                 ) -> tuple[np.ndarray, dict[str, float]]:
    """The historical injection, standardized by the toy's own (mass-weighted) quartiles."""
    c = np.cumsum(p)
    q25, q50, q75 = (float(np.interp(q, c, x)) for q in (0.25, 0.50, 0.75))
    iqr = max(q75 - q25, 1e-12)
    w = np.exp(amplitude * np.clip((x - q50) / iqr, -clip_z, clip_z))
    w = w / float((w * p).sum())
    return w, {"p25": q25, "p50": q50, "p75": q75, "iqr": iqr, "amplitude": amplitude,
               "clip_z": clip_z}


def smearing_matrix(x: np.ndarray, f: float) -> np.ndarray:
    """P(reco bin i | x) for each grid point; out-of-range smeared values fold into the edge bins
    (`run_ibu.eavail_bin`'s convention for the response, stated rather than silently dropped)."""
    if f == 0.0:
        idx = np.clip(np.digitize(x, EDGES) - 1, 0, len(EDGES) - 2)
        out = np.zeros((len(EDGES) - 1, x.size))
        out[idx, np.arange(x.size)] = 1.0
        return out
    sigma = f * (x + TOY["x_ref"])
    cdf = _PHI((np.asarray(EDGES)[:, None] - x[None, :]) / sigma[None, :])
    prob = np.diff(cdf, axis=0)
    prob[0] += cdf[0]                                   # below the first edge folds into bin 0
    prob[-1] += 1.0 - cdf[-1]                           # above the last edge folds into the top
    return prob


def expected_iteration(x: np.ndarray, p: np.ndarray, w: np.ndarray, f: float, mode: str,
                       iterations: int, normalization: str = "engine") -> dict[str, Any]:
    """The binned estimator on EXPECTED histograms (infinite statistics).

    Per truth bin j: t0_j prior mass, acc_j accepted mass, K_ij the accepted reco distribution of
    the PRIOR, D_i the accepted reco distribution of the pseudodata (whose within-bin composition
    differs -- that is what smearing plus a shape change does). One iteration is exactly what
    `binned_unfolding.binned_omnifold` does to the expectations:
        r_i     = D_i / sum_j K_ij acc_j push_j
        pull_j  = push_j sum_i K_ij r_i                          (accepted events of bin j)
        push_j <- a_j pull_j + (1 - a_j) push_j                  (misses carried), or
        push_j <- pull_j                                         (efficiency-corrected)
    """
    nb = len(EDGES) - 1
    jb = np.clip(np.digitize(x, EDGES) - 1, 0, nb - 1)
    eps = efficiency(x)
    prob = smearing_matrix(x, f)
    t0 = np.bincount(jb, weights=p, minlength=nb)
    acc = np.bincount(jb, weights=p * eps, minlength=nb)
    K = np.stack([np.bincount(jb, weights=p * eps * prob[i], minlength=nb) for i in range(nb)])
    K = np.where(acc > 0, K / np.where(acc > 0, acc, 1.0), 0.0)          # P(reco i | truth j, acc)
    T = np.bincount(jb, weights=p * w, minlength=nb)
    D = np.stack([float((p * w * eps * prob[i]).sum()) for i in range(nb)])
    a = np.where(t0 > 0, acc / np.where(t0 > 0, t0, 1.0), 0.0)
    f_prior = acc.sum() / t0.sum()
    f_data = float((p * w * eps).sum() / (p * w).sum())
    if normalization == "engine":
        D = D * (acc.sum() / D.sum())                     # both legs to the same accepted total
    else:                                                 # rate-matched (POT-like)
        D = D * (acc.sum() * (f_data / f_prior) / D.sum())
    push = np.ones(nb)
    rows = []
    for k in range(1, iterations + 1):
        M = K @ (acc * push)
        r = np.where(M > 0, D / np.where(M > 0, M, 1.0), 1.0)
        pull = push * (K.T @ r)
        push = a * pull + (1 - a) * push if mode == bu.MODE_CARRY_MISSES else np.where(a > 0, pull,
                                                                                       push)
        rec = cm.historical()["rae"].recovery(t0, t0 * push, T)
        rows.append({"iteration": k, "recovery": rec["recovery"],
                     "residual_l1": rec["residual_l1"], "injected_l1": rec["injected_l1"]})
    return {"acceptance_by_bin": a.tolist(), "prior_by_bin": t0.tolist(),
            "target_by_bin": T.tolist(), "iterations": rows}


def sample_events(x: np.ndarray, p: np.ndarray, w: np.ndarray, f: float, n: int, rng) -> dict:
    """Draw prior and pseudodata events from the toy and bin them (finite-sample check)."""
    out = {}
    for name, weights in (("prior", p), ("data", p * w)):
        idx = rng.choice(x.size, size=n, p=weights / weights.sum())
        xv = x[idx]
        acc = rng.random(n) < efficiency(xv)
        y = xv + (rng.normal(0.0, f * (xv + TOY["x_ref"])) if f > 0 else 0.0)
        out[name] = {"x": xv, "accepted": acc,
                     "truth_bin": np.clip(np.digitize(xv, EDGES) - 1, 0, len(EDGES) - 2),
                     "reco_bin": np.clip(np.digitize(y, EDGES) - 1, 0, len(EDGES) - 2)}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--iterations", type=int, default=30)
    ap.add_argument("--finite-n", type=int, default=600_111)
    ap.add_argument("--finite-seeds", type=int, default=3)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    t0 = time.perf_counter()
    rae, rc = cm.historical()["rae"], cm.historical()["rc"]
    x, p = grid()
    w, tilt_spec = tilt_weights(x, p)
    ks = list(range(1, args.iterations + 1))

    runs: dict[str, Any] = {}
    for f in SMEARINGS:
        for mode in (bu.MODE_CARRY_MISSES, bu.MODE_EFFICIENCY_CORRECTED):
            key = f"sigma_frac={f:.2f}/{mode}"
            runs[key] = expected_iteration(x, p, w, f, mode, args.iterations)
            runs[key]["smearing_fraction"] = f
            runs[key]["normalization"] = "engine"
            # the same with the pseudodata total set by the true rate (POT-like), which separates
            # the engine normalization's cost from the rule's own convergence
            rkey = f"sigma_frac={f:.2f}/{mode}/rate_matched"
            runs[rkey] = expected_iteration(x, p, w, f, mode, args.iterations, "rate_matched")
            runs[rkey]["smearing_fraction"] = f
            runs[rkey]["normalization"] = "rate_matched"
        # the reference model on this toy's own acceptance and displacement
        base = runs[f"sigma_frac={f:.2f}/{bu.MODE_CARRY_MISSES}"]
        t0b = np.asarray(base["prior_by_bin"])
        Tb = np.asarray(base["target_by_bin"])
        disp = np.abs(Tb / Tb.sum() - t0b / t0b.sum())
        runs[f"sigma_frac={f:.2f}/reference_model"] = {
            "smearing_fraction": f,
            "iterations": [{"iteration": k,
                            "recovery": float(rc.ceiling(np.asarray(base["acceptance_by_bin"]),
                                                         disp, k))} for k in ks]}
        for mode in (bu.MODE_CARRY_MISSES, bu.MODE_EFFICIENCY_CORRECTED):
            r = runs[f"sigma_frac={f:.2f}/{mode}"]["iterations"]
            ref = runs[f"sigma_frac={f:.2f}/reference_model"]["iterations"]
            rm = runs[f"sigma_frac={f:.2f}/{mode}/rate_matched"]["iterations"]
            print(f"[toy] f={f:.2f} {mode:22s} k1={r[0]['recovery']:.4f} k3={r[2]['recovery']:.4f}"
                  f" k10={r[9]['recovery']:.4f} k30={r[-1]['recovery']:.4f}  rate-matched "
                  f"k3={rm[2]['recovery']:.4f} k10={rm[9]['recovery']:.4f}  reference "
                  f"k3={ref[2]['recovery']:.4f} k10={ref[9]['recovery']:.4f}", flush=True)

    # ---- finite-sample check at the historical size -----------------------------------------
    finite: dict[str, Any] = {}
    f_check = 0.15
    for seed in range(args.finite_seeds):
        rng = np.random.default_rng(90_000 + seed)
        ev = sample_events(x, p, w, f_check, args.finite_n, rng)
        nb = len(EDGES) - 1
        for mode in (bu.MODE_CARRY_MISSES, bu.MODE_EFFICIENCY_CORRECTED):
            rows = []
            prior_hist = np.bincount(ev["prior"]["truth_bin"], minlength=nb).astype(float)
            target_hist = np.bincount(ev["data"]["truth_bin"], minlength=nb).astype(float)
            for step in bu.binned_omnifold(
                    reco_bin_mc=ev["prior"]["reco_bin"], truth_bin_mc=ev["prior"]["truth_bin"],
                    pass_reco_mc=ev["prior"]["accepted"],
                    pass_gen_mc=np.ones(args.finite_n, bool),
                    w_truth_mc=np.ones(args.finite_n), w_reco_mc=np.ones(args.finite_n),
                    reco_bin_data=ev["data"]["reco_bin"][ev["data"]["accepted"]],
                    w_data=np.ones(int(ev["data"]["accepted"].sum())),
                    n_reco_bins=nb, n_truth_bins=nb, iterations=args.iterations, mode=mode):
                unfolded = np.bincount(ev["prior"]["truth_bin"], weights=step["push"],
                                       minlength=nb)
                rows.append({"iteration": step["iteration"],
                             "recovery": rae.recovery(prior_hist, unfolded,
                                                      target_hist)["recovery"]})
            finite[f"seed{seed}/{mode}"] = {"smearing_fraction": f_check, "n": args.finite_n,
                                            "iterations": rows}
    for mode in (bu.MODE_CARRY_MISSES, bu.MODE_EFFICIENCY_CORRECTED):
        vals = {k: [finite[f"seed{s}/{mode}"]["iterations"][k - 1]["recovery"]
                    for s in range(args.finite_seeds)] for k in (3, 10, 30)}
        exp = runs[f"sigma_frac={f_check:.2f}/{mode}"]["iterations"]
        print(f"[toy] finite N={args.finite_n} f={f_check} {mode:22s} "
              + " ".join(f"k{k}={np.mean(v):.4f}+-{np.std(v, ddof=1):.4f} (expected "
                         f"{exp[k - 1]['recovery']:.4f})" for k, v in vals.items()), flush=True)

    payload = {"schema": "phase-e-toy-reference/1", "commit": scm.repo_commit(),
               "historical_sources": getattr(cm.historical, "_verified", None),
               "toy": TOY, "injection": tilt_spec, "edges": list(EDGES),
               "smearing_fractions": list(SMEARINGS), "expected": runs,
               "finite_sample": finite, "environment": cm.environment(),
               "seconds": time.perf_counter() - t0,
               "scope": ("a known-function toy: what the reference model describes, at infinite "
                         "statistics and at the historical size; prospective only")}
    cm.write_json(args.output, payload)
    print(f"[toy] wrote {args.output} in {time.perf_counter() - t0:.0f}s")


if __name__ == "__main__":
    main()
