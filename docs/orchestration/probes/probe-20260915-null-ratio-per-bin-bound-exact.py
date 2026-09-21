import numpy as np, sys, os
from fractions import Fraction as F
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "nd-unfolding"))
from z_statistics import support_mask

# EXACT check: no floating point in the comparison at all. Operands are float64 values
# (so this is the inequality on the numbers the implementation actually holds), but the
# norms and the ratio are formed in exact rational arithmetic.
def exact_violates(x, x2):
    m = support_mask(x)
    if not m.any(): return None
    a = [F(v) for v in x[m]]; b = [F(v) for v in x2[m]]
    num2 = sum((bi-ai)**2 for ai, bi in zip(a, b))
    den2 = sum(ai*ai for ai in a)
    pbm  = max(abs((bi-ai)/ai) for ai, bi in zip(a, b))
    # r_null <= pbm   <=>   num2 <= pbm^2 * den2
    return num2 > pbm*pbm*den2

rng = np.random.default_rng(20260915)
viol = 0; n = 0
for _ in range(4000):
    k = int(rng.integers(3, 40))
    x = rng.lognormal(-85, 3.0, size=k)
    x[rng.random(k) < 0.15] = 0.0
    neg = rng.random(k) < 0.10
    x[neg] = -np.abs(x[neg])
    x2 = x + x * rng.normal(0, 1e-9, size=k)
    v = exact_violates(x, x2)
    if v is None: continue
    n += 1; viol += bool(v)
print(f"EXACT RATIONAL CHECK  trials={n}  violations={viol}")

# and an adversarial set aimed at the bound rather than sampled away from it
cases = {
 "uniform relative deviation (equality case)": (np.array([1.0,2.0,3.0]), np.array([1+1e-9,2*(1+1e-9),3*(1+1e-9)])),
 "all deviation in the SMALLEST bin":          (np.array([1e-30,1.0]),   np.array([1e-30*(1+1e-3),1.0])),
 "negative bins present (excluded by rep)":    (np.array([-5.0,1.0,2.0]),np.array([-5.0*1.5,1.0+1e-9,2.0])),
 "zeros present (excluded by rep)":            (np.array([0.0,1.0]),     np.array([7.0,1.0+1e-9])),
}
for name,(x,x2) in cases.items():
    print(f"  {name:45s} violates={exact_violates(np.asarray(x,float), np.asarray(x2,float))}")
