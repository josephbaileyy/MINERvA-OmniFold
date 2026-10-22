"""TEST ONLY (not a study output; local, no cluster): mp2_s2_verdict helpers against independent hand computations."""
import importlib.util, sys, types
import numpy as np
from scipy.stats import norm
import itertools
def holm_ref(ps, alpha=0.05):
    # step-down definition: adjusted p_(i) = max_{j<=i} min(1, (m-j+1) p_(j)); reject p_(i) while p_(i) <= alpha/(m-i+1)
    m = len(ps); o = sorted(range(m), key=lambda i: ps[i]); adj = [0.0]*m; run = 0.0; rej = [False]*m; go = True
    for r, i in enumerate(o):
        run = max(run, min(1.0, (m - r) * ps[i])); adj[i] = run
        go = go and ps[i] <= alpha / (m - r); rej[i] = go
    return adj, rej
p = sys.argv[1]
sys.modules["mp2_s2_fit"] = types.ModuleType("mp2_s2_fit"); sys.modules["s5p_stage1_inspect"] = types.ModuleType("s1")
spec = importlib.util.spec_from_file_location("V", p); V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
rng = np.random.default_rng(1)
for _ in range(200):
    ps = list(rng.uniform(0, 0.2, 4) ** rng.uniform(1, 3))
    ref, rej = holm_ref(ps)
    assert np.allclose(V.holm(ps), ref, rtol=0, atol=1e-15), (ps, V.holm(ps), ref)
    assert (min(ps) > 0.0125) == (not any(rej))
print("holm ok (vs step-down definition, 200 draws; min p > 0.0125 <=> Holm rejects none)")
for z, n in ((3.497, 109), (2.0, 5), (6.0, 10), (0.1, 3)):
    ref = 1 - (1 - 2 * norm.sf(z)) ** n
    assert abs(V.sidak_p(z, n) - ref) <= 1e-12 * max(ref, 1e-300) + 1e-15, (z, n)
print("sidak ok; p at 3.4970, n=109:", V.sidak_p(3.4970, 109))
# clustered variance by brute force
ev_id = rng.integers(0, 50, 400); nb = 7; ib = rng.integers(0, nb, 400); we = rng.uniform(0.1, 2, 50); wt = we[ev_id]
c, v, n = V.clustered(ev_id, ib, wt, nb)
vb = np.zeros(nb)
for e in range(50):
    for b in range(nb):
        vb[b] += (np.sum((ev_id == e) & (ib == b)) * we[e]) ** 2
assert np.allclose(c, np.bincount(ib, wt, nb)) and np.allclose(v, vb, rtol=1e-13) and np.array_equal(n, np.bincount(ib, None, nb))
assert np.all(v >= np.bincount(ib, wt * wt, nb) - 1e-12)
print("clustered ok (brute force; >= per-entry sumw2)")
print("fail-closed ndf<1:", V.v3_rule({"ndf": 0, "n_bins_used": 1, "chi2": 0.0, "max_abs_pull_used": 0.0, "chi2_ndf": None}))
