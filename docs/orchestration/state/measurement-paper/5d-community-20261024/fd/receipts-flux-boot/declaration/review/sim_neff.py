"""Synthetic: is the bootstrap sd of the weighted mean sigma_w / sqrt(n_eff) when the weights are a function of the
universe (a constraint likelihood on the normalization), and what does 3D's delta_method_ratio report then?"""
import sys
import numpy as np

sys.path.insert(0, sys.argv[1])
import fd_flux_boot as FB  # noqa: E402

rng = np.random.default_rng(4)
N = 100
z = rng.normal(size=N)                                  # each universe's normalization pull
X = np.column_stack([z, z + 0.3 * rng.normal(size=N), rng.normal(size=N)])   # col 0 = norm, 1 = correlated, 2 = indep
idx = FB.indices()


def solve(make):
    lo, hi = 0.0, 10.0
    for _ in range(80):
        s = (lo + hi) / 2
        lo, hi = (s, hi) if FB.n_eff(make(s)) > 19.06 else (lo, s)
    return make(s)


cases = {"independent lognormal": solve(lambda s: np.exp(s * np.random.default_rng(9).normal(size=N))),
         "constraint on col 0 (Gaussian likelihood, offset 0.5)": solve(lambda s: np.exp(-0.5 * (s * (z - 0.5)) ** 2))}
for name, w in cases.items():
    mu = (w[:, None] * X).sum(0) / w.sum()
    sw = np.sqrt((w[:, None] * (X - mu) ** 2).sum(0) / w.sum())
    boot = np.array([(w[i][:, None] * X[i]).sum(0) / w[i].sum() for i in idx]).std(0, ddof=1)
    print(f"{name}: n_eff {FB.n_eff(w):.2f}")
    print("  boot sd / (sigma_w / sqrt(n_eff)) per column:", np.round(boot / (sw / np.sqrt(FB.n_eff(w))), 3))
    print("  3D delta_method_ratio per column:           ", np.round(FB.delta_method_ratio(X, w, idx), 3))
