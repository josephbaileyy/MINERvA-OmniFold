"""Certified upper bound on R(c) = int_0^1 P_p(exists B<=BMAX: U95(K_B,B) < c) dp, U95 = upper end of the two-sided
95% Clopper-Pearson interval (= beta.ppf(0.975, k+1, B-k)). g_c(p) is nonincreasing in p (coupling), so a LEFT
Riemann sum over a grid 0=p_0<...<p_n=h plus the tail (1-h) g_c(h) is an upper bound. Exact DP in p for each grid
point (absorbing 'crossed' state); counts above max_B k*(B) can never cross later (counts never decrease)."""
import numpy as np, json, sys
from scipy import stats
BMAX = 1999
def kstar(c):
    ks = np.full(BMAX + 1, -1)
    for B in range(1, BMAX + 1):
        # largest k with U95(k,B) < c ; U increasing in k
        lo, hi, best = 0, B - 1, -1
        while lo <= hi:
            m = (lo + hi) // 2
            if stats.beta.ppf(0.975, m + 1, B - m) < c: best, lo = m, m + 1
            else: hi = m - 1
        ks[B] = best
    return ks
def g(c, ps, ks):
    K = int(ks.max()) + 2  # states 0..K-1 live counts, K-1 = 'too many, can never cross'
    ps = np.asarray(ps)[:, None]
    dist = np.zeros((ps.shape[0], K)); dist[:, 0] = 1.0
    crossed = np.zeros(ps.shape[0])
    for B in range(1, BMAX + 1):
        new = dist * (1 - ps)
        new[:, 1:] += dist[:, :-1] * ps
        new[:, -1] += dist[:, -1] * ps[:, 0]  # overflow stays overflow
        dist = new
        k = ks[B]
        if k >= 0:
            crossed += dist[:, :k + 1].sum(1)
            dist[:, :k + 1] = 0.0
    return crossed
out = {}
for j in range(1, 11):
    c = 0.05 / j
    ks = kstar(c)
    h = min(1.0, 6 * c)
    n = 6000
    grid = np.linspace(0.0, h, n + 1)
    gv = g(c, grid, ks)
    assert np.all(np.diff(gv) <= 1e-12), "g not monotone on grid"
    upper = float((gv[:-1] * np.diff(grid)).sum() + (1 - h) * gv[-1])
    lower = float((gv[1:] * np.diff(grid)).sum())
    out[j] = {"c": c, "R_upper": upper, "R_lower": lower, "ratio_upper": upper / c, "ratio_lower": lower / c,
              "tail_g_at_h": float(gv[-1]), "h": h, "grid_n": n}
    print(j, f"c={c:.5f} R/c in [{lower/c:.4f}, {upper/c:.4f}] tail g(h)={gv[-1]:.2e}", flush=True)
# Holm: FWER <= max_{m0} m0 R(alpha/m0) = max_j j*R(0.05/j) = max_j R(c_j)/c_j * alpha
q = max(v["ratio_upper"] for v in out.values())
print("certified q (max over j of R_upper/c) =", q)
json.dump({"BMAX": BMAX, "per_threshold": out, "q_upper": q}, open("certify_out.json", "w"), indent=1)
