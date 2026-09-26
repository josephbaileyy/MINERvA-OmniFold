"""D1 residuals, D2 seeds/upcast/edge-safe probes, repaired parity meta, and zero counts in the inputs."""
import numpy as np
from common import *
print("== D1: driver fn_unf vs fn_true, npz asimov fn_push[4] vs fn_true")
for t in ("nominal", "eavail", "q3"):
    d = L(f"{RUNS}/drv/driver_{t}.npz"); a = L(f"{RUNS}/asimov/asimov_b0_{t}.npz")
    rd = R(d["fn_unf"], d["fn_true"]); ra = R(a["fn_push"][4], a["fn_true"])
    ra5 = R(U @ a["xsec_it5_flat"], a["fn_true"])
    diff = np.abs(rd - ra)
    print(t, "driver", ew(rd), "npz k5", ew(ra), "npz(xsec_it5)", ew(ra5),
          "max|diff|pp all153 %.3f (%s) EW-only %.3f (EW%d)" % (100 * diff.max(), NAMES[int(diff.argmax())], 100 * diff[:42].max(), int(diff[:42].argmax())),
          "corrEW %.5f" % np.corrcoef(rd[:42], ra[:42])[0, 1], "truth relmax %.2e" % np.abs(R(d["fn_true"], a["fn_true"])).max())
    print("   fn_push[4] == U@xsec_it5 ?", np.allclose(a["fn_push"][4], U @ a["xsec_it5_flat"], rtol=1e-12, atol=0))
    print("   driver meta problems", d["meta"]["problems"], "r", d["meta"]["r"], "parity", d["meta"]["input_parity"])
print("== D2 asimov probes vs asimov_b0_eavail k5")
base = L(f"{RUNS}/asimov/asimov_b0_eavail.npz"); b5 = base["xsec_it5_flat"]
for n in ("asimov_eavail_upcast", "asimov_eavail_seedper", "asimov_eavail_jitter1"):
    p = L(f"{RUNS}/asimov/{n}.npz"); x = np.abs(R(U @ p["xsec_flat"], U @ b5))
    print(n, "bitwise:", np.array_equal(p["xsec_flat"], b5), "max %.4f%% med %.4f%%" % (100 * x.max(), 100 * np.median(x)), p["meta"]["coords"], p["meta"]["jitter_f32"], p["meta"]["seed_per_estimator"])
print("== D2 data probes vs data_b0")
db = L(f"{RUNS}/drv/data_b0.npz"); fd = U @ db["xsec_flat"]
for n in ("drv/data_upcast", "drv/data_seedper", "drv/data_jitter1", "rep/rep_data_jitteredge1", "rep/rep_data_jitteredge2", "rep/rep_data_nosentinel"):
    p = L(f"{RUNS}/{n}.npz"); x = np.abs(R(U @ p["xsec_flat"], fd))
    print(n, "bitwise:", np.array_equal(p["xsec_flat"], db["xsec_flat"]), "max %.4f%% (%s) med %.4f%%" % (100 * x.max(), NAMES[int(x.argmax())], 100 * np.median(x)), "mode", p["meta"].get("jitter_mode"), "dropped", p["meta"].get("sentinel_rows_dropped"))
p = L(f"{RUNS}/rep/rep_asimov_eavail_jitteredge1.npz"); x = np.abs(R(U @ p["xsec_flat"], U @ b5))
print("edge-safe asimov: max %.4f%% med %.4f%%" % (100 * x.max(), 100 * np.median(x)), p["meta"]["jitter_mode"])
x1 = np.abs(R(U @ L(f"{RUNS}/rep/rep_data_jitteredge1.npz")["xsec_flat"], fd))
x2 = np.abs(R(U @ L(f"{RUNS}/rep/rep_data_jitteredge2.npz")["xsec_flat"], fd))
x12 = np.abs(R(U @ L(f"{RUNS}/rep/rep_data_jitteredge1.npz")["xsec_flat"], U @ L(f"{RUNS}/rep/rep_data_jitteredge2.npz")["xsec_flat"]))
print("jitter1 vs jitter2 (seed-to-seed): max %.4f%% med %.4f%%" % (100 * x12.max(), 100 * np.median(x12)))
np.save("probe_scale_data.npy", np.vstack([x1, x2]))
# refinement evidence data_b0 vs nosentinel
for n in ("drv/data_b0", "rep/rep_data_nosentinel"):
    ev = L(f"{RUNS}/{n}.npz")["meta"]["refinement"]
    print(n, "refined_sum %.2f n_clipped %d signed_sum %.2f" % (ev["refined_sum"], ev["n_clipped"], ev["signed_sum"]))
par = L(f"{RUNS}/rep/rep_driver_nominal_parity.npz")
print("parity meta:", par["meta"]["input_parity"])
print("== zero counts in inputs")
z = np.load("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", allow_pickle=True)
edges = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
for i, e in enumerate(edges): print("edge", i, e[0], e[-1], len(e) - 1)
g = z["MCgen"]; pt = z["pass_truth"].astype(bool); pr = z["pass_reco"].astype(bool)
print("MCgen dtype", g.dtype, g.shape)
print("MC truth zeros per axis (all rows):", [int((g[:, k] == 0).sum()) for k in range(5)])
print("MC truth zeros per axis (pass_truth):", [int((g[pt, k] == 0).sum()) for k in range(5)])
sent = np.any(g < -9000, axis=1); print("sentinel rows:", int(sent.sum()), "of which pass_truth", int((sent & pt).sum()), "pass_reco", int((sent & pr).sum()))
wr = z["w_reco"]; print("sentinel reco-passing weight: %.2f of %.2f (%.4f%%)" % (wr[sent & pr & pt].sum(), wr[pr & pt].sum(), 100 * wr[sent & pr & pt].sum() / wr[pr & pt].sum()))
del g
rc = z["MCreco"]
print("MC reco zeros per axis (all rows):", [int((rc[:, k] == 0).sum()) for k in range(5)])
print("MC reco zeros per axis (pass_reco&pass_truth):", [int((rc[pr & pt, k] == 0).sum()) for k in range(5)], "frac W=0 among reco-passing: %.4f" % ((rc[pr & pt, 4] == 0).mean()))
del rc
m = z["measured"]; print("data rows", m.shape, "data zeros per axis:", [int((m[:, k] == 0).sum()) for k in range(5)], "frac W=0: %.4f" % ((m[:, 4] == 0).mean()))
b = np.load("/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz", allow_pickle=True)["bkg_reco"]
print("bkg reco zeros per axis:", [int((b[:, k] == 0).sum()) for k in range(5)])
