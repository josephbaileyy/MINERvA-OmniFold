"""Both directions of the loader fix, on real .npz files holding an object array: v1 raises, v2 loads the keys
diagnose() needs, and diagnose() on them equals diagnose() on the in-memory arrays."""
import importlib.util, os, sys, tempfile
from pathlib import Path
import numpy as np
os.O_NOATIME = getattr(os, "O_NOATIME", 0)          # macOS has no O_NOATIME; Linux uses the real flag
ND = sys.argv[1]
sys.argv = ["mw_diag.py", ND.rsplit("/nd-unfolding", 1)[0], "/nonexistent", "/nonexistent"]
def load(name):
    spec = importlib.util.spec_from_file_location(name, f"{name}.py"); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
v1, v2 = load("mw_diag.v1"), load("mw_diag")
rng = np.random.default_rng(3)
edges = [np.array([0., 1., 2., 3.]), np.array([0., 0.5, 1.0])]
x = rng.uniform(0, 1, (3000, 2)) * [3, 1]
bkg_nd = np.full((3, 2), 20.0)
*_, w = v2.recompute({"measured": x}, {"bkg_nd": bkg_nd}, edges)
w[7] *= 1.3
obj = np.array([{"a": 1}, "s"], dtype=object)
d = Path(tempfile.mkdtemp())
np.savez_compressed(d / "lat.npz", measured=x.astype(np.float32), measured_weights=w, nedges=np.array(2),
                    edges_0=edges[0], edges_1=edges[1], cfg=obj, data_pot=np.array(1.0))
np.savez_compressed(d / "bkg.npz", bkg_nd=bkg_nd, bkg_w=np.ones(4), meta=np.array('{"k": 1}'), extra=obj)
for f in ("lat.npz", "bkg.npz"):
    try:
        v1.load_noatime(d / f); print(f"v1 {f}: loaded (UNEXPECTED)"); sys.exit(1)
    except ValueError as e:
        print(f"v1 {f}: ValueError ({str(e)[:40]}...) as on the cluster")
z = v2.load_noatime(d / "lat.npz", v2.LAT_KEYS); b = v2.load_noatime(d / "bkg.npz", v2.BKG_KEYS)
print("v2 lat keys", sorted(z), "bkg keys", sorted(b))
assert sorted(z) == ["edges_0", "edges_1", "measured", "measured_weights", "nedges"] and sorted(b) == ["bkg_nd"]
mem = {"measured": x.astype(np.float32), "measured_weights": w, "nedges": np.array(2), "edges_0": edges[0], "edges_1": edges[1]}
r_file, r_mem = v2.diagnose(z, b), v2.diagnose(mem, {"bkg_nd": bkg_nd})
assert r_file == r_mem, "file and memory diagnoses differ"
assert r_file["share_equal"] == v2.rp.measured_weights_agreement(z, b, edges)
print("v2 diagnose(file) == diagnose(memory); share", r_file["share_equal"], "n_diff", r_file["n_diff"],
      "not explained", [a["row"] for a in r_file["differing_rows_not_explained"]])
assert [a["row"] for a in r_file["differing_rows_not_explained"]] == [7]
for f in ("lat.npz", "bkg.npz"): (d / f).unlink()
d.rmdir()
print("LOAD TEST OK")
