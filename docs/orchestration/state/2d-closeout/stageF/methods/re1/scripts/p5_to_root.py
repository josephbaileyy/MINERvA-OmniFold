#!/usr/bin/env python3
"""RE-1 F: package the P5 product (s5p data central, configuration (e)) as the 5D producer's input container.

Container conversion only. The flat TH1D 'hXSecND_flat' is written by the production writer
unfold_nd_omnifold_unbinned.write_thnd (not retyped) and read back by the figure producer's own loader
excess_eavail_W.load_data_xsec; the readback must equal the npz xsec_flat bitwise or nothing is kept.
Before writing, the P5 grid is checked against the producer's grid: the npz input's edges (of_inputs_5d.npz,
the grid P5 was unfolded on) must equal [u2d.PT_EDGES, u2d.PZ_EDGES, EXTRA_AXES eavail, q3, W] exactly.
Control: the same write/readback is applied to the current 5D product's hXSecND_flat.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--code-root", type=Path, required=True)
ap.add_argument("--p5", type=Path, required=True)
ap.add_argument("--expect-p5-sha256", required=True)
ap.add_argument("--npz-inputs", type=Path, required=True)
ap.add_argument("--current-5d", type=Path, required=True)
ap.add_argument("--out", type=Path, required=True)
ap.add_argument("--control-out", type=Path, required=True)
ap.add_argument("--json", type=Path, required=True)
a = ap.parse_args()
for p in (a.out, a.control_out, a.json):
    if p.exists():
        sys.exit(f"refusing to overwrite {p}")
cr = a.code_root.resolve()
for sub in ("2d-unfolding", "nd-unfolding"):
    sys.path.insert(0, str(cr / sub))
import ROOT  # noqa: E402
ROOT.gROOT.SetBatch(True)
import unfold_nd_omnifold_unbinned as und  # noqa: E402
import excess_eavail_W as eew  # noqa: E402
import xsec_nd  # noqa: E402
for m in (und, eew, und.u2d, xsec_nd):
    if not Path(m.__file__).resolve().is_relative_to(cr):
        sys.exit(f"{m.__name__} imported from {m.__file__}, outside {cr}")

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

rec = {"p5": str(a.p5), "p5_sha256": sha(a.p5), "current_5d": str(a.current_5d), "current_5d_sha256": sha(a.current_5d),
       "npz_inputs": str(a.npz_inputs)}
if rec["p5_sha256"] != a.expect_p5_sha256:
    sys.exit(f"P5 sha256 {rec['p5_sha256']} != expected")
z = np.load(a.p5, allow_pickle=True)
meta = json.loads(str(z["meta"]))
shape = tuple(int(s) for s in z["shape"])
xs = np.asarray(z["xsec_flat"], np.float64)
# the producer's grid
axis_names = ["eavail", "q3", "W"]
edges = [und.u2d.PT_EDGES, und.u2d.PZ_EDGES] + [und.EXTRA_AXES[x]["edges"] for x in axis_names]
pshape = tuple(len(e) - 1 for e in edges)
e = np.load(a.npz_inputs, allow_pickle=True)
n = int(e["nedges"])
npz_edges = [np.asarray(e[f"edges_{i}"], np.float64) for i in range(n)]
grid_equal = (n == 5) and all(len(x) == len(y) and np.array_equal(np.asarray(x, np.float64), y)
                              for x, y in zip(edges, npz_edges))
rec.update({"p5_meta_config": meta["config"], "p5_iters": meta["iters"], "p5_construction": meta["construction"],
            "p5_shape": list(shape), "producer_shape": list(pshape), "grid_edges_equal": bool(grid_equal),
            "npz_edges": [x.tolist() for x in npz_edges]})
if shape != pshape or not grid_equal or xs.size != int(np.prod(pshape)):
    json.dump(rec, open(a.json, "w"), indent=1)
    sys.exit("P5 grid differs from the producer's grid; refusing")

def write_and_check(arr_flat, out, title):
    f = ROOT.TFile.Open(str(out), "RECREATE")
    und.write_thnd(f, arr_flat.reshape(pshape), None, "hXSecND", title, edges, None)
    f.Close()
    back = eew.load_data_xsec(str(out), pshape).ravel(order="C")
    return bool(np.array_equal(back, arr_flat)), float(np.max(np.abs(back - arr_flat)))

ok, d = write_and_check(xs, a.out, "RE-1 P5: s5p data central, configuration (e)")
rec.update({"p5_readback_bitwise": ok, "p5_readback_maxabs": d})
cur = eew.load_data_xsec(str(a.current_5d), pshape).ravel(order="C")
ok2, d2 = write_and_check(cur, a.control_out, "RE-1 control: current 5D product repackaged")
rec.update({"control_readback_bitwise": ok2, "control_readback_maxabs": d2})
# descriptive comparison P5 vs current, same producer projection
md_p5 = xsec_nd.project_marginal(xs.reshape(pshape), edges, drop_axes=[0, 1, 3])
md_cur = xsec_nd.project_marginal(cur.reshape(pshape), edges, drop_axes=[0, 1, 3])
dvol = np.outer(np.diff(und.EXTRA_AXES["eavail"]["edges"]), np.diff(und.EXTRA_AXES["W"]["edges"]))
r = (md_p5 * dvol) / np.where(md_cur > 0, md_cur * dvol, np.nan)
rec.update({"total_p5_over_current": float((md_p5 * dvol).sum() / (md_cur * dvol).sum()),
            "eavailW_cell_ratio_p5_over_current": r.tolist(),
            "n_support_p5": int((xs > 0).sum()), "n_support_current": int((cur > 0).sum()),
            "n_support_both": int(((xs > 0) & (cur > 0)).sum())})
rec["out_sha256"], rec["control_out_sha256"] = sha(a.out), sha(a.control_out)
json.dump(rec, open(a.json, "w"), indent=1)
print(json.dumps({k: v for k, v in rec.items() if k not in ("npz_edges", "eavailW_cell_ratio_p5_over_current")}, indent=1))
if not (ok and ok2):
    a.out.unlink(); sys.exit("readback not bitwise; P5 container removed")
