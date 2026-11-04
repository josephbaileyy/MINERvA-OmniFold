import sys, importlib.util
import numpy as np
ND = sys.argv[1]
sys.argv = ["mw_diag.py", ND.rsplit("/nd-unfolding", 1)[0], "/nonexistent", "/nonexistent"]
spec = importlib.util.spec_from_file_location("mw", "mw_diag.py"); mw = importlib.util.module_from_spec(spec); spec.loader.exec_module(mw)
rp, ri = mw.rp, mw.ri
rng = np.random.default_rng(7)
edges = [np.array([0., 1., 2., 3.]), np.array([0., 0.5, 1.0])]
n = 4000
x64 = np.column_stack([rng.uniform(0, 3, n), rng.uniform(0, 1, n)])
movers = np.arange(10)
x64[movers, 0] = 1.0 - 1e-9          # below edge 1 in float64; float32 rounds to exactly 1.0
bkg_nd = np.full((3, 2), 20.0)
# the original weights, by the same rule on the float64 coordinates
z64 = {"measured": x64, "nedges": 2, "edges_0": edges[0], "edges_1": edges[1]}
*_, w64 = mw.recompute(z64, {"bkg_nd": bkg_nd}, edges)
w64[500] *= 1.5                      # one corruption far from any edge (row 500 is uniform)
z = {"measured": x64.astype(np.float32), "measured_weights": w64, "nedges": np.array(2),
     "edges_0": edges[0], "edges_1": edges[1]}
b = {"bkg_nd": bkg_nd}
r = mw.diagnose(z, b)
share_fn = rp.measured_weights_agreement(z, b, edges)
print("share", r["share_equal"], "== deploy function", share_fn, r["share_equal"] == share_fn)
print("n_diff", r["n_diff"], "cat", r["differing_rows_by_category"])
print("bins", r["bins_with_differing_rows"], "unexplained", r["bins_unexplained"], "not invertible", r["bins_not_invertible"])
print("cat", r["differing_rows_by_category"]); print("not explained", r["differing_rows_not_explained"])
for k, v in r["bins"].items(): print(k, {q: v[q] for q in ("D_recomputed", "D0_from_w0", "delta", "near_edge_rows_in_bin", "near_edge_rows_whose_other_side_is_this_bin", "explained") if q in v})
assert share_fn == r["share_equal"]
assert [d["row"] for d in r["differing_rows_not_explained"]] == [500], r["differing_rows_not_explained"]
assert not r["bins_unexplained"]
# negative direction: a count change no near-edge row can supply -> unexplained
w_bad = w64.copy(); m = (x64[:, 0] > 2.2) & (x64[:, 1] > 0.6); w_bad[m] = (np.sum(m) + 5 - 20) / (np.sum(m) + 5)
r2 = mw.diagnose({**z, "measured_weights": w_bad}, b)
print("NEG unexplained", r2["bins_unexplained"], "rows", len(r2["differing_rows_not_explained"])); assert r2["bins_unexplained"] and r2["differing_rows_not_explained"]
# clean case: no corruption, no movers -> nothing differs
z3 = {**z, "measured": x64.astype(np.float32)}; x64c = x64.copy(); x64c[movers, 0] = 0.5
z3c = {"measured": x64c, "nedges": 2, "edges_0": edges[0], "edges_1": edges[1]}; *_, w3 = mw.recompute(z3c, b, edges)
r3 = mw.diagnose({**z, "measured": x64c.astype(np.float32), "measured_weights": w3}, b); print("CLEAN", r3["n_diff"], r3["differing_rows_by_category"]); assert r3["n_diff"] == 0
print("ALL OK")
