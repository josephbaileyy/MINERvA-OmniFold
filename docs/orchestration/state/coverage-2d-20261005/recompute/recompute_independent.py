"""Independent recomputation of the interim 2D fixed-truth coverage look (numpy only)."""
# Receipt copy of the independent reviewer's script. Two changes by the study owner, neither
# touching the computation: NPZ is resolved relative to this file, and points print at 17
# significant digits (the reviewer printed 12).
import math
from pathlib import Path
import numpy as np

NPZ = Path(__file__).resolve().parent.parent / "interim.npz"
NBOOT = 40_000
CL = 0.995
RNG = np.random.default_rng(987654321)  # own stream, not 20261005

d = np.load(NPZ)
idx, U, P, T = d["toy_index"], d["U"], d["P"], d["T"]
rep = d["reported"]
sel = (idx >= 1) & (idx <= 100)
U, P, idx = U[sel], P[sel], idx[sel]
n = len(idx)
truth_fixed = bool(np.all(d["T_max_abs_diff"][sel] == 0))
r = d["prod_sigma"][rep] / d["prod_mean"][rep]
Tb = T[rep]
Ub = U[:, rep]
Pb = P[:, rep]
assert np.all(Tb > 0) and np.all(np.isfinite(r))
print("n_toys", n, "n_bins", rep.sum(), "idx", idx.min(), idx.max(), "truth_fixed", truth_fixed)

W1 = (math.erf(0.9 / math.sqrt(2)), math.erf(1.1 / math.sqrt(2)))
W2 = (math.erf(1.8 / math.sqrt(2)), math.erf(2.2 / math.sqrt(2)))
print("windows", W1, W2)

BOOT = RNG.integers(0, n, size=(NBOOT, n))
a = (1 - CL) / 2


def score(Uarr, s):
    z = (Uarr - Tb) / (s * r * Tb)
    in1 = (np.abs(z) <= 1).mean(axis=1)  # per toy (equal bin count per toy -> pooled mean = mean of toy means)
    in2 = (np.abs(z) <= 2).mean(axis=1)
    z2 = (z ** 2).mean(axis=1)
    zm = z.mean(axis=1)
    pt = dict(C1=in1.mean(), C2=in2.mean(), RMS=math.sqrt(z2.mean()), MEAN=zm.mean())
    # pooled direct for exactness check
    assert abs(pt["C1"] - (np.abs(z) <= 1).mean()) < 1e-14
    b1 = in1[BOOT].mean(axis=1)
    b2 = in2[BOOT].mean(axis=1)
    brms = np.sqrt(z2[BOOT].mean(axis=1))
    bm = zm[BOOT].mean(axis=1)
    ci = lambda x: tuple(np.quantile(x, [a, 1 - a]))
    return pt, dict(C1=ci(b1), C2=ci(b2), RMS=ci(brms), MEAN=ci(bm))


def side(ci, w):
    if ci[0] >= w[0] and ci[1] <= w[1]:
        return "in"
    if ci[1] < w[0]:
        return "below"
    if ci[0] > w[1]:
        return "above"
    return "straddle"


def verdict(cis):
    s = [side(cis["C1"], W1), side(cis["C2"], W2)]
    if all(x == "in" for x in s):
        return "PASS"
    below, above = "below" in s, "above" in s
    if below and above:
        return "FAIL-mixed"
    if below:
        return "FAIL-undercoverage"
    if above:
        return "FAIL-overcoverage"
    return "INCONCLUSIVE"


res = {}
for s in (1.0, 0.7, 1.3):
    pt, ci = score(Ub, s)
    res[s] = (pt, ci, verdict(ci))
    print(f"s={s}", {k: f"{v:.17g}" for k, v in pt.items()}, ci, res[s][2],
          [side(ci['C1'], W1), side(ci['C2'], W2)])

p1, c1, v1 = res[1.0]
_, c07, v07 = res[0.7]
_, c13, v13 = res[1.3]
cond1 = (c07["C1"][1] < p1["C1"] and c07["C2"][1] < p1["C2"]
         and c13["C1"][0] > p1["C1"] and c13["C2"][0] > p1["C2"])
cond2 = (v1 != "PASS") or (v07 == "FAIL-undercoverage" and v13 == "FAIL-overcoverage")
print("posctl cond1", cond1, "cond2", cond2)

Urep = Ub * Tb / Pb
pr, cr = score(Urep, 1.0)
print("replica", {k: f"{v:.17g}" for k, v in pr.items()}, cr, verdict(cr),
      [side(cr['C1'], W1), side(cr['C2'], W2)])
