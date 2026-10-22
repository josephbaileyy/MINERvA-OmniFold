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
def load(n_bins):
    fm = types.ModuleType("mp2_s2_fit"); fm.V3_BINS = {f"d{i}": None for i in range(n_bins)}
    sys.modules["mp2_s2_fit"] = fm; sys.modules["s5p_stage1_inspect"] = types.ModuleType("s1")
    spec = importlib.util.spec_from_file_location("V", p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
try:
    load(3); raise AssertionError("a 3-distribution family was accepted")
except AssertionError as e:
    assert "Holm family" in str(e), e
print("N_V3 == len(V3_BINS) asserted (a 3-member family is refused)")
V = load(4)
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
fc = V.v3_rule({"ndf": 0, "n_bins_used": 1, "chi2": 0.0, "max_abs_pull_used": 0.0, "chi2_ndf": None})
assert fc["p_d"] is None and fc["status"].startswith("FAIL-CLOSED"), fc
print("fail-closed ndf<1 reported as", fc["status"])


def stops(f, *a):
    try:
        f(*a)
    except SystemExit as e:
        assert str(e).startswith("STOP"), e
        return str(e)
    raise AssertionError(f"no STOP for {f.__name__}{a}")


nan, inf = float("nan"), float("inf")
for a_, b_ in ((nan, 1.0), (1.0, nan), (nan, nan), (inf, inf), (1.0, inf)):
    stops(V.same, a_, b_, "x")
good = {"ndf": 5, "n_bins_used": 6, "chi2": 4.0, "chi2_ndf": 0.8, "max_abs_pull_used": 1.2}
for k_, v_ in (("chi2", nan), ("chi2", inf), ("max_abs_pull_used", nan), ("max_abs_pull_used", inf)):
    stops(V.v3_rule, dict(good, **{k_: v_}))
assert V.v3_rule(good)["p_d"] > 0
stops(V.finite, [], "empty")
stops(V.finite, [1.0, nan], "vec")
stops(V.clustered, np.array([0, 1]), np.array([0, 7]), np.array([1.0, 1.0]), 7)
stops(V.clustered, np.array([0, 1]), np.array([-1, 0]), np.array([1.0, 1.0]), 7)
print("NaN/inf STOP: same (5 cases), v3_rule (chi2, z_max as nan and inf), finite (empty, nan); clustered out-of-range STOP")
