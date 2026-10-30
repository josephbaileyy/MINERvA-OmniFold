"""1B stage-1 declaration arithmetic: nominal rates, windows, SEs, 4A windows, stage prices."""
from math import erf, sqrt
from scipy import stats

def C(k, s=1.0):  # P(|z|<=k) when band/scatter = s, Gaussian
    return erf(k * s / sqrt(2))

print("nominal C1 C2", f"{C(1):.6f}", f"{C(2):.6f}")
print("window C1", f"[{C(1,0.9):.6f}, {C(1,1.1):.6f}]", "C2", f"[{C(2,0.9):.6f}, {C(2,1.1):.6f}]")
for N in (100, 300):
    for k in (1, 2):
        p = C(k); print(f"N={N} k={k} per-cell binomial SE at nominal {sqrt(p*(1-p)/N):.4f}")
print("dC1/ds at s=1", f"{2*stats.norm.pdf(1):.4f}", "dC2/ds", f"{4*stats.norm.pdf(2):.4f}")
for k, se in ((1, sqrt(C(1)*(1-C(1))/300)), (2, sqrt(C(2)*(1-C(2))/300))):
    d = 2*k*stats.norm.pdf(k)
    print(f"k={k}: per-cell scale resolution (1 SE) {se/d:.4f}; pooled-independent SE {se/4:.4f} -> scale {se/4/d:.4f}")
# per-cell flag: 99.5% two-sided Wilson upper bound below nominal; smallest flagged count at N=300
def pc(n, N, alpha, method="wilson"):
    z = stats.norm.ppf(1 - alpha / 2); p = n / N
    c = (p + z*z/(2*N)) / (1 + z*z/N); h = z*sqrt(p*(1-p)/N + z*z/(4*N*N)) / (1 + z*z/N)
    return c - h, c + h
for k in (1, 2):
    p0 = C(k)
    for n in range(300, -1, -1):
        lo, hi = pc(n, 300, alpha=0.005, method="wilson")
        if hi < p0:
            print(f"k={k}: per-cell flag fires at <= {n}/300 = {n/300:.4f} (Wilson 99.5% upper {hi:.4f})"); break
# 4A windows: chi2 of toys when matrix = s^2 x true scatter -> chi2 ~ chi2_16 / s^2
q95 = stats.chi2.ppf(0.95, 16); print("chi2_16 95th pct", f"{q95:.3f}", "mean SE N=300", f"{sqrt(32/300):.4f}", "tail SE", f"{sqrt(.05*.95/300):.4f}")
print("4A mean window", f"[{16/1.1**2:.3f}, {16/0.9**2:.3f}]")
print("4A tail window", f"[{stats.chi2.sf(q95*1.1**2,16):.4f}, {stats.chi2.sf(q95*0.9**2,16):.4f}]")
# prices from measured walls
unf = (7129/11, 7227/11)            # S1 P1/P2 per-unfold wall, s (S1-REPORT section 3)
over = (720-641, 720-545)           # A7 build overhead: ~720 s mean per experiment minus seconds_unfold median 545-641 (FD-PLAN 5.1)
toy = (unf[0]+over[0], unf[1]+over[1]); print("toy wall s", [round(t,1) for t in toy])
nh = [t/8/3600 for t in toy]; print("node-h per toy (8 lanes)", [round(x,5) for x in nh])
s1unit = 2.00889/88; print("S1 measured node-h per full-MC unfold (P1)", round(s1unit,5))
# S1's universe set (s1_assembly.json meta.inputs_sha256): 100 flux + 67 interaction + 8 detector = 175, plus CV
stages = {"2a derivation runs (176) + pilot (16 full-MC) + correspondence (8 half-MC) + reproduction (2)": 176 + 16 + 8 + 2,
          "2b control interim (100)": 100, "2c control final (+200)": 200, "3 test arms (2 x 300)": 600}
lo = hi = cap = 0.0
for name, n in stages.items():
    a, b, c = n * nh[0], n * nh[1], n * nh[1] * 1.5625
    lo, hi, cap = lo + a, hi + b, cap + c
    print(f"{name}: {n} unfolds, {a:.2f}-{b:.2f} node-h, ceiling {c:.2f}")
    print(f"   lane wall at 8 lanes per node: {n/8*toy[1]/3600:.2f} node-wall-h in all")
print(f"total priced {lo:.2f}-{hi:.2f}, sum of ceilings {cap:.2f}")
# job layout: 8 lanes per node; projected wall = (most toys on one lane) x high toy wall; enforced cap = nodes x limit
import math
jobs = [("2a", 202, 3, 3.0), ("2b", 100, 2, 2.5), ("2c", 200, 3, 3.0), ("3i", 200, 3, 3.0), ("3f", 400, 5, 3.5)]
tp = tc = 0.0
for j, n, nodes, limit_h in jobs:
    per_lane = math.ceil(n / (8 * nodes)); wall = per_lane * toy[1] / 3600
    tp += nodes * wall; tc += nodes * limit_h
    print(f"job {j}: {n} unfolds, {nodes} nodes, <= {per_lane} per lane, projected wall {wall:.2f} h, "
          f"projected charge {nodes*wall:.2f}, limit {limit_h} h, enforced cap {nodes*limit_h:.2f}")
print(f"jobs: projected {tp:.2f} node-h, enforced caps {tc:.2f} node-h")
