"""Toy (D Agostini, 5 iterations from the MC prior): is the 3b closure half-span the same sign as C_resp's data half-span? Binned, matrix-inversion unfolding.
Truth E in [0,10], reco = s*E*(1+0.1 N). C_resp: unfold DATA with response at s=1+-eps. 3b: unfold PSEUDO built at
s=1+-eps with the response at s=1. Both relative, as fd_ct_readers.run_mismatch forms them."""
import numpy as np
rng = np.random.default_rng(1)
nb = 12; edges = np.linspace(0, 10, nb + 1); redges = np.linspace(0, 12, nb + 1)
N = 2_000_000
Emc = rng.gamma(3.0, 1.2, N); Emc = Emc[Emc < 10]
t_mc = np.histogram(Emc, bins=edges)[0]
noise = rng.normal(0, 0.1, Emc.size)
def resp(s):
    r = s * Emc * (1 + noise)
    H, _, _ = np.histogram2d(r, Emc, bins=[redges, edges])
    t, _ = np.histogram(Emc, bins=edges)
    return H / t, H.sum(1)          # P(reco | truth), MC reco histogram
t_mc, _ = np.histogram(Emc, bins=edges)
# "data": a different truth shape, the nominal detector
Ed = rng.gamma(3.2, 1.15, N); Ed = Ed[Ed < 10]
D, _ = np.histogram(Ed * (1 + rng.normal(0, 0.1, Ed.size)), bins=redges)
def unf(R, y, it=5):
    x = t_mc.astype(float).copy()
    for _ in range(it):
        fold = R @ x
        x = x * (R.T @ np.where(fold > 0, y / fold, 0)) / R.sum(0)
    return x
eps = 0.04
R0, _ = resp(1.0)
f = unf(R0, D)
xp, xm = unf(resp(1 + eps)[0], D), unf(resp(1 - eps)[0], D)
d = (xp - xm) / (2 * f)                         # C_resp-style data half-span, relative to f
Pp, Pm = resp(1 + eps)[1], resp(1 - eps)[1]     # pseudo-data from the shifted detector, nominal truth
bp, bm = unf(R0, Pp) / t_mc - 1, unf(R0, Pm) / t_mc - 1
b0 = unf(R0, resp(1.0)[1]) / t_mc - 1
h = ((bp - b0) - (bm - b0)) / 2                 # fd_ct_readers' closure half-span
sl = slice(1, nb - 1)
c = float(h[sl] @ d[sl] / np.linalg.norm(h[sl]) / np.linalg.norm(d[sl]))
print("closure floor max|b0|", float(np.abs(b0).max()))
print("data half-span d  ", np.round(d[sl], 4))
print("closure half-span h", np.round(h[sl], 4))
print(f"cosine(h, d) = {c:.4f}   norm ratio = {np.linalg.norm(h[sl])/np.linalg.norm(d[sl]):.4f}")
print(f"cosine(h, -d) = {-c:.4f}")
print("per-bin h/d", np.round(h[sl]/d[sl], 3))
