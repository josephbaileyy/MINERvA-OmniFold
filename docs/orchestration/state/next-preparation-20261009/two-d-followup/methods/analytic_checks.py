"""Exact checks of the split-sample identities for a linear statistic (no sampling, no training).

For T(w) = sum_i w_i x_i with fixed x (fixed bin mappers and purity), complementary 0/1 masks m and
half-exposure normalization U_A = 2 T(w m), U_B = 2 T(w (1 - m)):
  (1) E_m[(U_A - U_B)^2 / 2] = 2 sum_i w_i^2 x_i^2                (the split target, given the data)
  (2) Var_m(U_A) = sum w^2 x^2 = -Cov_m(U_A, U_B): corr = -1 given the data
  (3) E_m[ Var_Poisson(1)(2 T(w m b)) ] = 2 sum w^2 x^2             (the masked bootstrap's target)
so the split and the masked bootstrap have the same limit and kappa = 1 identically for any linear
statistic: the test has power only against the estimator's non-linear response.
  (4) Over new Poisson productions the two halves are independent (thinning), each with variance
      2 E[sum w^2 x^2]: the split's expectation over productions is the half-exposure variance.
(1)-(3) are verified by enumerating all 2^n masks (n = 12) and exact Poisson(1) moments;
(4) by a seeded Monte Carlo of a Poisson process (known answer 2 lambda E[x^2]).

    python3 analytic_checks.py --out analytic_checks.json
"""
import argparse
import itertools
import json

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = np.random.default_rng(20261010)
    n = 12
    x = rng.gamma(2.0, 1.0, n)
    w = rng.uniform(0.5, 1.5, n)
    s2 = float(np.sum(w ** 2 * x ** 2))
    ua, ub = [], []
    for bits in itertools.product((0, 1), repeat=n):
        m = np.array(bits, float)
        ua.append(2 * np.sum(w * m * x))
        ub.append(2 * np.sum(w * (1 - m) * x))
    ua, ub = np.array(ua), np.array(ub)
    split = float(np.mean((ua - ub) ** 2 / 2))
    var_a = float(np.var(ua))
    cov = float(np.mean((ua - ua.mean()) * (ub - ub.mean())))
    # Poisson(1) bootstrap of the masked half: Var(2 sum w m b x) = 4 sum w^2 m x^2 (Var b = 1);
    # averaged over masks (E m = 1/2): 2 sum w^2 x^2
    boot = float(np.mean([4 * np.sum(w ** 2 * np.array(bits) * x ** 2) for bits in itertools.product((0, 1), repeat=n)]))
    # (4) Poisson process: lambda events with marks x ~ Gamma(2, 1): half-exposure estimate 2 sum_A x
    lam, P = 400.0, 20000
    halves_a, halves_b = [], []
    for _ in range(P):
        k = rng.poisson(lam)
        xs = rng.gamma(2.0, 1.0, k)
        m = rng.random(k) < 0.5
        halves_a.append(2 * xs[m].sum())
        halves_b.append(2 * xs[~m].sum())
    halves_a, halves_b = np.array(halves_a), np.array(halves_b)
    ex2 = 2.0 * 3.0  # E[x^2] for Gamma(2, 1) = k(k+1) theta^2 = 6
    out = {
        "n_masks": 2 ** n,
        "split_target_over_2sum": split / (2 * s2),
        "var_half_over_sum": var_a / s2,
        "corr_halves_given_data": cov / var_a,
        "masked_bootstrap_target_over_2sum": boot / (2 * s2),
        "poisson_process": {"productions": P, "var_half_over_known": float(np.var(halves_a, ddof=1) / (2 * lam * ex2)),
                            "corr_halves_over_productions": float(np.corrcoef(halves_a, halves_b)[0, 1]),
                            "se_corr": 1 / np.sqrt(P)},
    }
    ok = (abs(out["split_target_over_2sum"] - 1) < 1e-12 and abs(out["var_half_over_sum"] - 1) < 1e-12
          and abs(out["corr_halves_given_data"] + 1) < 1e-12 and abs(out["masked_bootstrap_target_over_2sum"] - 1) < 1e-12
          and abs(out["poisson_process"]["var_half_over_known"] - 1) < 0.05
          and abs(out["poisson_process"]["corr_halves_over_productions"]) < 4 / np.sqrt(P))
    out["all_identities_hold"] = bool(ok)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
