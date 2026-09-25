"""Review r5: reco-level (E_avail,W) ratio of expected pseudo-data signal under each departure vs nominal,
and the truth-level ratio; compared with the unfold's EW output ratio (from r2)."""
import json, sys, os
import numpy as np
DEP = "/pscratch/sd/j/josephrb/s5n-20260925/deploy/82dc1517"
sys.path.insert(0, DEP + "/nd-unfolding")
import s5c_unfold, s5n_pseudo
inputs = s5c_unfold.load_inputs("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz")
ratio = json.load(open(DEP + "/docs/orchestration/state/s5n/eavail-ratio-gibuu-over-genie.json"))
E, Wd = inputs["edges"][2], inputs["edges"][4]
pr = inputs["pass_reco"]; reco = inputs["MCreco"]; gen = inputs["MCgen"]; wr = inputs["w_reco"].astype(float); wt = inputs["w_truth"].astype(float)
def ew(cols, w, sel, half_open):
    e0, w0 = cols[sel, 2], cols[sel, 4]
    ok = (e0 >= E[0]) & (w0 >= Wd[0]) & ((e0 < E[-1]) & (w0 < Wd[-1]) if half_open else (e0 <= E[-1]) & (w0 <= Wd[-1]))
    h, _, _ = np.histogram2d(e0[ok], w0[ok], bins=[E, Wd], weights=w[sel][ok]); return h.ravel()
# reco window on all axes
win = np.ones(len(wr), bool)
for k, e in enumerate(inputs["edges"]): win &= (reco[:, k] >= e[0]) & (reco[:, k] < e[-1])
sel_r = pr & win
out = {}
r0 = ew(reco, wr, sel_r, True); t0 = ew(gen, wt, np.ones(len(wt), bool), False)
res = {l.split()[0]: l for l in open(os.path.dirname(os.path.abspath(__file__)) + "/r2_response.txt") if l.startswith("EW") and "|" in l}
for name, amp in (("eavail_shape", 1.0), ("q3_given_eavail_w", 0.3)):
    r = s5n_pseudo.truth_weight(name, inputs, amp, ratio)
    rr = ew(reco, wr * r, sel_r, True) / r0
    tt = ew(gen, wt * r, np.ones(len(wt), bool), False) / t0
    out[name] = {"reco_EW_ratio": rr.tolist(), "truth_EW_ratio": tt.tolist()}
    print("==", name, " cell: truth_ratio reco_ratio | unfold_ratio (from r2)")
    for i in range(42):
        f = res[f"EW{i}"].split("|")
        uf = float(f[2].split()[0]) if name == "eavail_shape" else float(f[5].split()[1])
        print(f"EW{i:<3d} {tt[i]:.4f} {rr[i]:.4f} | {uf:.4f}")
json.dump(out, open(os.path.dirname(os.path.abspath(__file__)) + "/r5_recolevel.json", "w"), indent=1)
