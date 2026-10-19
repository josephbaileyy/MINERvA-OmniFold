"""Upper bound on the null size of the s5p decision rule under ANY stopping rule.
Rejection at threshold t requires CP95 upper(k_B,B) < t at the stopping B (s5p_inference.holm_determined).
Union over looks L: size(t) <= int_0^1 P(exists b in L: k_b <= c_b(t) | u) du, u ~ U(0,1) the true tail prob.
Also: the plain MC p (k+1)/(b+1) <= t at any look (no CP gate)."""
import numpy as np
from scipy import stats

def cp_hi(k, b, level=0.95):
    a = 1 - level
    return 1.0 if k == b else stats.beta.ppf(1 - a / 2, k + 1, b - k)

def boundary(t, bmax, kind):
    c = np.full(bmax + 1, -1)
    for b in range(1, bmax + 1):
        if kind == "cp":
            # largest k with cp_hi(k,b) < t ; cp_hi increasing in k
            k = -1
            while k + 1 <= b and cp_hi(k + 1, b) < t:
                k += 1
        else:
            k = int(np.floor(t * (b + 1) - 1 + 1e-12))
        c[b] = k
    return c

def cross_prob(u, c, looks):
    # DP over k for paths not yet crossed; k_b ~ binomial increments with prob u
    kmax = int(c.max()) + 2
    dist = np.zeros(kmax + 1); dist[0] = 1.0  # state k (capped at kmax = "far above")
    crossed = 0.0
    lookset = set(looks)
    for b in range(1, max(looks) + 1):
        new = dist * (1 - u)
        new[1:] += dist[:-1] * u
        new[-1] += dist[-1] * u  # absorbing cap
        dist = new
        if b in lookset and c[b] >= 0:
            m = min(c[b], kmax - 1)
            crossed += dist[: m + 1].sum()
            dist[: m + 1] = 0.0
    return crossed

def size(t, looks, kind):
    c = boundary(t, max(looks), kind)
    # integrate over u: below t contributes <= t; fine grid above
    us = np.concatenate([np.linspace(1e-6, t, 200), np.linspace(t, min(1, 8 * t), 1200)[1:]])
    vals = np.array([cross_prob(u, c, looks) for u in us])
    return np.trapz(vals, us)

if __name__ == "__main__":
    every = list(range(1, 2000))
    batches = [200 * i for i in range(1, 10)] + [1999]
    for t in [0.005, 0.00556, 0.01, 0.025, 0.05]:
        s_cp_all = size(t, every, "cp")
        s_cp_bat = size(t, batches, "cp")
        s_p_bat = size(t, batches, "p")
        s_p_all = size(t, every, "p")
        print(f"t={t:<8} CP-gated: every-b {s_cp_all/t:.3f}t  batch-looks {s_cp_bat/t:.3f}t | "
              f"plain (k+1)/(B+1): batch-looks {s_p_bat/t:.3f}t  every-b {s_p_all/t:.3f}t")
