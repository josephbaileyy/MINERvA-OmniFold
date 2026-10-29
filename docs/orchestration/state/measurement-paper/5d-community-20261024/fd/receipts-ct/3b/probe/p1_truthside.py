"""3b feasibility probe (read-only, login node): is every shifted lateral dump's truth side bitwise the zero dump's?
Compares array shapes and bytes of MCgen, w_truth, pass_truth, denom_nd, flux, data_pot, n_nucleons, edges and the
data rows; and reports only whether MCreco, w_reco and pass_reco differ (not by how much). No product is read."""
import hashlib, sys
import numpy as np
P = "/pscratch/sd/j/josephrb"
ZERO = f"{P}/measurement-paper/phase1/mp1/s1/lateral/lat_zero.npz"
V = [f"{P}/measurement-paper/phase1/mp1/s1/lateral/lat_{s}_{t}.npz" for s in ("proton", "meson", "em", "other", "xtalk")
     for t in ("m1", "p1")] + [f"{P}/w2-recoil-20261006/w2b/lateral/lat_w2b_rr{x}.npz" for x in ("0", "1")]
TRUTH = ("MCgen", "w_truth", "pass_truth", "denom_nd", "flux", "data_pot", "n_nucleons", "nedges", "measured",
         "measured_weights")
RECO = ("MCreco", "w_reco", "pass_reco")
def h(a): return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]
z = np.load(ZERO, allow_pickle=True)
zt = {k: (z[k].shape, str(z[k].dtype), h(z[k])) for k in TRUTH + RECO}
ze = [h(z[f"edges_{i}"]) for i in range(int(z["nedges"]))]
print("zero", {k: zt[k][0] for k in ("MCgen", "MCreco", "measured")}, "axes", list(z["axes"]))
for p in V:
    v = np.load(p, allow_pickle=True)
    t_eq = {k: (v[k].shape, str(v[k].dtype), h(v[k])) == zt[k] for k in TRUTH}
    e_eq = [h(v[f"edges_{i}"]) for i in range(int(v["nedges"]))] == ze
    r_diff = {k: ((v[k].shape, str(v[k].dtype)) == zt[k][:2], h(v[k]) != zt[k][2]) for k in RECO}
    print(p.split("/")[-1], "truth-side identical:", all(t_eq.values()) and e_eq,
          "" if all(t_eq.values()) else {k: x for k, x in t_eq.items() if not x},
          "| reco (same shape, differs):", r_diff)
