"""Re-check of the 'follows-x' arm of sim_coverage_basic.py with the right target.  When w = L(x) is a likelihood of
each universe's own value, the weighted ensemble estimates the CONSTRAINED covariance C_post = (Ct^-1 + s^2 q q^T /
lam0)^-1, not the prior Ct; chi2(C_true) is the wrong comparator.  Same toy, same seeds as the author's script."""
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
L = np.linalg.cholesky(Ct)
q0 = Q[:, 0]
B = 400
idx = np.random.default_rng(2).integers(0, N, (B, N))
rows = []
for k in range(150):
    X = (L @ rng.normal(size=(n, N))).T
    z = (X @ q0) / np.sqrt(lam[0])
    lo, hi = 0.0, 5.0
    for _ in range(60):
        s = (lo + hi) / 2
        w = np.exp(-0.5 * (s * (z - 0.3)) ** 2)
        lo, hi = (s, hi) if FB.n_eff(w) > 19 else (lo, s)
    w = np.exp(-0.5 * (s * (z - 0.3)) ** 2)
    Cpost = np.linalg.inv(np.linalg.inv(Ct) + (s ** 2 / lam[0]) * np.outer(q0, q0))
    target = chi(rest + Cpost)
    C0 = sa.mat_cov(X, w)
    chat = chi(rest + C0)
    res = {}
    for v in ("correlation", "block"):
        vals = [chi(rest + (FB.correlation_swap(sa.mat_cov(X[i], w[i]), C0) if v == "correlation"
                            else sa.mat_cov(X[i], w[i]))) for i in idx]
        q16, q50, q84 = np.percentile(vals, [16, 50, 84])
        res[v] = (q16 <= target <= q84, 2 * chat - q84 <= target <= 2 * chat - q16, q50 - chat)
    rows.append((target, chat, res))
t = np.array([r[0] for r in rows]); c = np.array([r[1] for r in rows])
print(f"chi2(C_true prior) = {chi(rest + Ct):.2f}; chi2(C_post) median {np.median(t):.2f}; chi2_hat median {np.median(c):.2f}; "
      f"median(chi2_hat - chi2(C_post)) {np.median(c - t):+.2f}; sd(chi2_hat - target) {np.std(c - t):.2f}")
for v in ("correlation", "block"):
    print(f"  {v:11s}: percentile band covers chi2(C_post) {np.mean([r[2][v][0] for r in rows]):.2f}; basic "
          f"{np.mean([r[2][v][1] for r in rows]):.2f}; median offset {np.median([r[2][v][2] for r in rows]):+.2f}")
