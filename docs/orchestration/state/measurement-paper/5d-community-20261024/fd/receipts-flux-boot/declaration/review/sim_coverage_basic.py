"""(The declaration's extension of the reviewer's sim_coverage.py: adds the basic (reflected) band 2 chi2(C_hat) - q.)
Synthetic check (no real product read): does the 3D percentile band of chi2(C*_b) bracket chi2(C_true), and is its
spread the ensemble-to-ensemble spread of chi2(C_hat)?  Flux-like 16-cell block, spectrum 1e-3..1e-7 relative
(Stage G's flux group lambda_min is 2.2e-7), weights with n_eff ~ 19, S1's estimator, 3D's resampling."""
import sys
import numpy as np

sys.path.insert(0, sys.argv[1])
import fd_flux_boot as FB  # noqa: E402
import s1_assemble as sa  # noqa: E402

rng = np.random.default_rng(11)
n, N = 16, 100
Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
Q[:, 0] = np.abs(np.ones(n) / 4 + 0.05 * rng.normal(size=n)); Q, _ = np.linalg.qr(Q)
lam = 1e-3 * np.logspace(0, -4, n)
Ct = (Q * lam) @ Q.T
rest = np.diag((0.012 + 0.004 * rng.random(n)) ** 2)
d = 0.03 * rng.normal(size=n) + 0.02
chi = lambda M: float(d @ np.linalg.solve(M, d))
chi_true = chi(rest + Ct)
L = np.linalg.cholesky(Ct)


def weights(X, mode):
    z = rng.normal(size=N) if mode == "indep" else (X @ Q[:, 0]) / np.sqrt(lam[0])
    lo, hi = 0.0, 5.0
    for _ in range(60):
        s = (lo + hi) / 2
        w = np.exp(s * z) if mode == "indep" else np.exp(-0.5 * (s * (z - 0.3)) ** 2)
        lo, hi = (s, hi) if FB.n_eff(w) > 19 else (lo, s)
    return w


B = 400
idx = np.random.default_rng(2).integers(0, N, (B, N))
for mode in ("indep", "follows-x"):
    rows = []
    for k in range(150):
        X = (L @ rng.normal(size=(n, N))).T
        w = weights(X, mode)
        C0 = sa.mat_cov(X, w)
        chat = chi(rest + C0)
        out = {}
        for v in ("correlation", "block"):
            vals = []
            for ib in idx:
                Cs = sa.mat_cov(X[ib], w[ib])
                Cv = FB.correlation_swap(Cs, C0) if v == "correlation" else Cs
                vals.append(chi(rest + Cv))
            q = np.percentile(vals, [16, 50, 84])
            out[v] = (q, np.std(vals), (2 * chat - q[2], 2 * chat - q[0]))
        rows.append((chat, out, FB.n_eff(w)))
    chats = np.array([r[0] for r in rows])
    print(f"--- weights {mode}: chi2(C_true) = {chi_true:.2f}; over 150 ensembles chi2(C_hat) median "
          f"{np.median(chats):.2f}, 16-84 [{np.percentile(chats, 16):.2f}, {np.percentile(chats, 84):.2f}], sd {chats.std():.2f}")
    for v in ("correlation", "block"):
        cover = np.mean([r[1][v][0][0] <= chi_true <= r[1][v][0][2] for r in rows])
        shift = np.median([r[1][v][0][1] - r[0] for r in rows])
        bsd = np.median([r[1][v][1] for r in rows])
        basic = np.mean([r[1][v][2][0] <= chi_true <= r[1][v][2][1] for r in rows])
        print(f"  {v:11s}: P(chi2_true in 16-84 band) {cover:.2f}; basic band {basic:.2f}; median(boot median - "
              f"chi2_hat) {shift:+.2f}; median boot sd {bsd:.2f}")
