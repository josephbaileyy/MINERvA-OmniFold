#!/usr/bin/env python3
"""Build padded point-cloud OmniFold inputs from a MNV101_DUMP_POINTCLOUD omnifile.

Phase 3 reader: the event loop (runEventLoopOmniFold.cpp, MNV101_DUMP_POINTCLOUD=1)
writes per-event variable-length vectors part_gen_{E,px,py,pz,pdg} (truth FS hadrons,
muon+nu removed) and part_reco_{E,x,y,z} (reco recoil clusters) on mc_signal_reco, and
part_reco_{E,x,y,z} on data. This loops those trees with the SAME (pt,pz) gating as the
scalar nd driver, truncates/zero-pads each cloud to a fixed num_part (keeping the
highest-energy constituents), and writes of_inputs_pc.npz for minerva_pet_dataloader.py
(pointcloud mode) -> the vendored PET.

  python dump_pointcloud_inputs.py --omnifile runEventLoopOmniFold_PC_MEFHC.root \
      --num-part 12 --out of_inputs_pc.npz
"""
import argparse
import sys
from array import array

import numpy as np
import ROOT

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if p not in sys.path:
        sys.path.insert(0, p)
import unfold_2d_omnifold_unbinned as u2d  # noqa: E402

GEN_FEATS = ["part_gen_E", "part_gen_px", "part_gen_py", "part_gen_pz", "part_gen_pdg"]
RECO_FEATS = ["part_reco_E", "part_reco_pos", "part_reco_z"]


def _pad_cloud(feat_vecs, num_part, sort_by_first_desc=True):
    """feat_vecs: list of equal-length python lists (one per feature) for ONE event.
    Returns (num_part, n_feat) zero-padded, truncated to the top num_part by feature[0]."""
    n_feat = len(feat_vecs)
    n = len(feat_vecs[0])
    out = np.zeros((num_part, n_feat), dtype=np.float32)
    if n == 0:
        return out
    arr = np.array(feat_vecs, dtype=np.float32).T  # (n, n_feat)
    if sort_by_first_desc and n > 1:
        arr = arr[np.argsort(-arr[:, 0])]
    k = min(n, num_part)
    out[:k] = arr[:k]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--num-part", type=int, default=12)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    P = args.num_part
    pt_e, pz_e = u2d.PT_EDGES, u2d.PZ_EDGES
    pt_lo, pt_hi, pz_lo, pz_hi = pt_e[0], pt_e[-1], pz_e[0], pz_e[-1]

    f = ROOT.TFile.Open(args.omnifile)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {args.omnifile}")
    t = f.Get("mc_signal_reco"); d = f.Get("data")
    if not t.GetBranch("part_gen_E"):
        raise SystemExit("[FAIL] no part_gen_E branch -- re-run the event loop with "
                         "MNV101_DUMP_POINTCLOUD=1")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_e)

    # ---- signal (MC): gen + reco clouds, pass flags, weights ----
    import math
    # scalar branches: pt/pz/eavail/q3 (truth + reco) so the PET push weights can be
    # binned into the SAME 4D axes as the GBDT result (PET-vs-GBDT comparison).
    sc = {b: array("d", [0.0]) for b in
          ("MC", "MC_pz", "MC_eavail", "MC_q3", "sim", "sim_pz", "sim_eavail", "sim_q3",
           "w_truth", "w_reco")}
    sp = array("B", [0])
    for b, a in sc.items():
        t.SetBranchAddress(b, a)
    t.SetBranchAddress("sim_pass", sp)
    genv = {b: ROOT.std.vector("double")() if b != "part_gen_pdg" else ROOT.std.vector("int")()
            for b in GEN_FEATS}
    recv = {b: ROOT.std.vector("double")() for b in RECO_FEATS}
    for b, v in {**genv, **recv}.items():
        t.SetBranchAddress(b, v)

    # Preallocate to the upper-bound entry count and fill by index (then truncate).
    # A python list of 32.8M small (P,nfeat) arrays + the np.asarray copy at the end
    # OOM-killed the 48G job (MaxRSS 50G); contiguous arrays cost ~15G total here.
    n = t.GetEntries()
    ng, nr = len(GEN_FEATS), len(RECO_FEATS)
    gen_cl = np.zeros((n, P, ng), np.float32)
    reco_cl = np.zeros((n, P, nr), np.float32)
    pr = np.zeros(n, bool); ptru = np.zeros(n, bool)
    wt = np.zeros(n, np.float64); wr = np.zeros(n, np.float64)
    tru_sc = np.zeros((n, 4), np.float32)   # per-event (pt,pz,eavail,q3) truth scalars
    rec_sc = np.zeros((n, 4), np.float32)   # per-event reco scalars
    k = 0
    for i in range(n):
        t.GetEntry(i)
        a_pt, a_pz = float(sc["MC"][0]), float(sc["MC_pz"][0])
        b_pt, b_pz = float(sc["sim"][0]), float(sc["sim_pz"][0])
        passed = sp[0] != 0
        tru_ok = u2d.in_truth_phase_space(a_pt, a_pz, pt_lo, pt_hi, pz_lo, pz_hi)
        rec_ok = (math.isfinite(b_pt) and math.isfinite(b_pz)
                  and pt_lo <= b_pt <= pt_hi and pz_lo <= b_pz <= pz_hi)
        if not (tru_ok or (passed and rec_ok)):
            continue
        gen_cl[k] = _pad_cloud([list(genv[b]) for b in GEN_FEATS], P)
        reco_cl[k] = _pad_cloud([list(recv[b]) for b in RECO_FEATS], P)
        pr[k] = passed and rec_ok; ptru[k] = tru_ok
        wt[k] = float(sc["w_truth"][0]) * pot_scale
        wr[k] = float(sc["w_reco"][0]) * pot_scale
        tru_sc[k] = (a_pt, a_pz, float(sc["MC_eavail"][0]), float(sc["MC_q3"][0]))
        rec_sc[k] = (b_pt if (passed and rec_ok) else -9999.0,
                     b_pz if (passed and rec_ok) else -9999.0,
                     float(sc["sim_eavail"][0]) if (passed and rec_ok) else -9999.0,
                     float(sc["sim_q3"][0]) if (passed and rec_ok) else -9999.0)
        k += 1
        if i % 200000 == 0:
            print(f"  signal {i}/{n}", flush=True)
    gen_cl = gen_cl[:k]; reco_cl = reco_cl[:k]
    pr = pr[:k]; ptru = ptru[:k]; wt = wt[:k]; wr = wr[:k]
    tru_sc = tru_sc[:k]; rec_sc = rec_sc[:k]
    print(f"  signal kept {k}/{n}", flush=True)

    # ---- data: reco cloud only ----
    dm = {b: array("d", [0.0]) for b in ("measured", "measured_pz")}
    dp = array("B", [0])
    for b, a in dm.items():
        d.SetBranchAddress(b, a)
    d.SetBranchAddress("measured_pass", dp)
    drecv = {b: ROOT.std.vector("double")() for b in RECO_FEATS}
    for b, v in drecv.items():
        d.SetBranchAddress(b, v)
    nd = d.GetEntries()
    meas_buf = np.zeros((nd, P, len(RECO_FEATS)), np.float32)
    km = 0
    for i in range(nd):
        d.GetEntry(i)
        if dp[0] == 0:
            continue
        pt, pz = float(dm["measured"][0]), float(dm["measured_pz"][0])
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            continue
        meas_buf[km] = _pad_cloud([list(drecv[b]) for b in RECO_FEATS], P)
        km += 1
    meas_cl = meas_buf[:km]
    f.Close()

    part_gen = np.asarray(gen_cl, np.float32)
    part_reco = np.asarray(reco_cl, np.float32)
    measured_pc = np.asarray(meas_cl, np.float32)
    print(f"[OK] signal clouds: gen {part_gen.shape} reco {part_reco.shape}; "
          f"data {measured_pc.shape}; num_part={P}")
    import unfold_nd_omnifold_unbinned as und
    pt_e, pz_e = u2d.PT_EDGES, u2d.PZ_EDGES
    ea_e = und.EXTRA_AXES["eavail"]["edges"]; q3_e = und.EXTRA_AXES["q3"]["edges"]
    np.savez_compressed(
        args.out, num_part=P,
        part_gen=part_gen, part_reco=part_reco, measured_pc=measured_pc,
        pass_reco=np.asarray(pr, bool), pass_truth=np.asarray(ptru, bool),
        w_truth=np.asarray(wt), w_reco=np.asarray(wr),
        measured_weights=np.ones(len(meas_cl)),
        # per-event (pt,pz,eavail,q3) scalars for binning the PET result vs GBDT
        truth_scalars=np.asarray(tru_sc, np.float32), reco_scalars=np.asarray(rec_sc, np.float32),
        edges_0=np.asarray(pt_e, float), edges_1=np.asarray(pz_e, float),
        edges_2=np.asarray(ea_e, float), edges_3=np.asarray(q3_e, float),
        gen_feats=np.array(GEN_FEATS, dtype=object),
        reco_feats=np.array(RECO_FEATS, dtype=object),
        data_pot=data_pot)
    print(f"[wrote] {args.out}")


if __name__ == "__main__":
    main()
