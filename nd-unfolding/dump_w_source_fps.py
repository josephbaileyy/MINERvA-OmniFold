#!/usr/bin/env python3
"""Build the FPS-gen-cloud-aligned W-source npz for the 5D PET FPS envelope.

PETxsec5D needs a W column + edges_4 ROW-ALIGNED to the FPS point-cloud gen cloud
(of_inputs_pc_fps.npz, 32.9M kept rows). The restricted of_inputs_5d.npz cannot be
reused (different event set: 32.85M restricted vs 32.9M FPS). So we replicate the
EXACT keep-filter of pet/dump_pointcloud_inputs.py on the SAME FPS omnifile's
mc_signal_reco tree -- but read only scalars (no cloud vectors) and vectorize the
filter -- then extract MC_W for the kept events.

keep(event) = in_truth_phase_space(MC,MC_pz)  OR  (sim_pass & reco-in-rectangle)
  in_truth_phase_space = finite & rectangle[PT_EDGES,PZ_EDGES] & atan2(pt,pz)<theta_max
Order = mc_signal_reco entry order (single-thread RDF preserves it), matching the pc dump.

Output of_inputs_5d_fps.npz: MCgen(N,5)=[pt,pz,ea,q3,W], w_truth(*pot_scale), pass_truth,
pass_reco, edges_0..4 -- the exact keys+dtypes PETxsec5D's alignment gate checks.
Self-verifies MCgen[:,:4]==pc truth_scalars and w_truth bit-identical before writing.

  python dump_w_source_fps.py --omnifile runEventLoopOmniFold_PC_FPS_MEFHC.root \
      --pc of_inputs_pc_fps.npz --wedges of_inputs_5d.npz --out of_inputs_5d_fps.npz
"""
import argparse
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import unfold_2d_omnifold_unbinned as u2d


def main():
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    # NB: single-thread (NO EnableImplicitMT) so AsNumpy preserves entry order.
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_PC_FPS_MEFHC.root")
    ap.add_argument("--pc", default="of_inputs_pc_fps.npz")
    ap.add_argument("--wedges", default="of_inputs_5d.npz",
                    help="npz providing edges_4 (W edges); shape-only, not row-aligned")
    ap.add_argument("--out", default="of_inputs_5d_fps.npz")
    ap.add_argument("--full-phase-space", action="store_true",
                    help="lift the theta_mu truth gate (must match the --pc dump's setting)")
    ap.add_argument("--pt-edges", default=None,
                    help="comma-separated pT edge override (must match the --pc dump's setting)")
    ap.add_argument("--pz-edges", default=None,
                    help="comma-separated p|| edge override (must match the --pc dump's setting)")
    args = ap.parse_args()

    if args.full_phase_space:
        import math
        u2d.MAX_MUON_THETA_RAD = math.pi
        print("[INFO] FULL PHASE SPACE: theta_mu truth gate lifted")

    pt_e = ([float(x) for x in args.pt_edges.split(",")] if args.pt_edges
            else u2d.PT_EDGES)
    pz_e = ([float(x) for x in args.pz_edges.split(",")] if args.pz_edges
            else u2d.PZ_EDGES)
    pt_lo, pt_hi, pz_lo, pz_hi = pt_e[0], pt_e[-1], pz_e[0], pz_e[-1]
    theta_max = u2d.MAX_MUON_THETA_RAD

    f = ROOT.TFile.Open(args.omnifile)
    _, _, pot_scale = u2d.get_pot_scales(f)
    f.Close()
    print(f"[wsrc] pot_scale={pot_scale:.6g}  rect pt[{pt_lo},{pt_hi}] pz[{pz_lo},{pz_hi}] "
          f"theta_max={theta_max:.5f}")

    cols = ["MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W",
            "sim", "sim_pz", "sim_pass_i", "w_truth"]
    # sim_pass is a char/bool branch; AsNumpy returns it as raw bytes ('\x01'),
    # so cast to int in C++ (order-preserving, single-thread).
    rdf = ROOT.RDataFrame("mc_signal_reco", args.omnifile).Define("sim_pass_i", "(int)sim_pass")
    a = rdf.AsNumpy(cols)
    MC = a["MC"].astype(np.float64); MCpz = a["MC_pz"].astype(np.float64)
    ea = a["MC_eavail"].astype(np.float64); q3 = a["MC_q3"].astype(np.float64)
    W = a["MC_W"].astype(np.float64)
    sim = a["sim"].astype(np.float64); simpz = a["sim_pz"].astype(np.float64)
    simpass = a["sim_pass_i"].astype(np.int64) != 0
    wtru = a["w_truth"].astype(np.float64)
    n = MC.size
    print(f"[wsrc] mc_signal_reco entries = {n}")

    finite_t = np.isfinite(MC) & np.isfinite(MCpz)
    with np.errstate(invalid="ignore"):
        theta = np.arctan2(MC, MCpz)
    tru_ok = (finite_t & (MC >= pt_lo) & (MC <= pt_hi)
              & (MCpz >= pz_lo) & (MCpz <= pz_hi) & (theta < theta_max))
    finite_r = np.isfinite(sim) & np.isfinite(simpz)
    rec_ok = (finite_r & (sim >= pt_lo) & (sim <= pt_hi)
              & (simpz >= pz_lo) & (simpz <= pz_hi))
    keep = tru_ok | (simpass & rec_ok)
    k = int(keep.sum())
    print(f"[wsrc] kept {k}/{n}")

    MCgen = np.column_stack([MC[keep], MCpz[keep], ea[keep], q3[keep], W[keep]]).astype(np.float32)
    w_truth = (wtru * pot_scale)[keep]
    pass_truth = tru_ok[keep]
    pass_reco = (simpass & rec_ok)[keep]

    # ---- self-verify alignment against the pc gen cloud (PETxsec5D's gate) ----
    pc = np.load(args.pc)
    ts = pc["truth_scalars"].astype(np.float32)   # (N,4) pt,pz,ea,q3
    pcw = pc["w_truth"].astype(np.float64)
    if MCgen.shape[0] != ts.shape[0]:
        raise SystemExit(f"[FAIL] row count {MCgen.shape[0]} != pc {ts.shape[0]}")
    both = np.isfinite(MCgen[:, :4]) & np.isfinite(ts)
    mism = int(((MCgen[:, :4] != ts) & both).sum())
    if mism:
        raise SystemExit(f"[FAIL] {mism} finite coord mismatches vs pc truth_scalars")
    wdiff = np.abs(w_truth - pcw).max()
    if wdiff != 0.0:
        raise SystemExit(f"[FAIL] w_truth not bit-identical (max|diff|={wdiff:.3e})")
    ptru_eq = bool((pass_truth == pc["pass_truth"].astype(bool)).all())
    prec_eq = bool((pass_reco == pc["pass_reco"].astype(bool)).all())
    nanx = int((np.isnan(MCgen[:, :4]) ^ np.isnan(ts)).sum())
    print(f"[wsrc] ALIGN OK: coords exact (0 mismatch), w_truth bit-identical, "
          f"pass_truth eq={ptru_eq} pass_reco eq={prec_eq}, {nanx} NaN-pattern rows")

    we = np.load(args.wedges)
    edges = {f"edges_{i}": pc[f"edges_{i}"].astype(float) for i in range(4)}
    edges["edges_4"] = we["edges_4"].astype(float)
    print(f"[wsrc] edges_4 (W) = {edges['edges_4']}")
    np.savez_compressed(args.out, MCgen=MCgen, w_truth=w_truth,
                        pass_truth=pass_truth, pass_reco=pass_reco, **edges)
    print(f"[wsrc] wrote {args.out}: MCgen{MCgen.shape} kept={k}")


if __name__ == "__main__":
    main()
