#!/usr/bin/env python3
"""Dump OmniFold inputs from a (3D/4D) omnifile to a ROOT-free .npz.

Step 1 of the NN-vs-GBDT cross-check (HIGHER_DIM_OMNIFOLD_DESIGN.md Phase 2). Runs
under the ROOT env, reuses the axis-list readers in unfold_nd_omnifold_unbinned.py,
and writes the feature stacks + masks + weights + binning so the NN OmniFold can run
in a TensorFlow env that has no ROOT (nn_run_from_npz.py). Default axes=eavail so the
NN result is directly comparable to the frozen 3D GBDT cross section.

Usage (ROOT env):
  python nn_dump_inputs.py --omnifile ../3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root \
      --axes eavail --out of_inputs_3d.npz
"""
import argparse
import sys

import numpy as np
import ROOT

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if p not in sys.path:
        sys.path.insert(0, p)
import unfold_2d_omnifold_unbinned as u2d  # noqa: E402
import unfold_nd_omnifold_unbinned as und  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--axes", default="eavail")
    ap.add_argument("--pt-edges", default=None,
                    help="comma-separated pT edge override (FPS extended grid)")
    ap.add_argument("--pz-edges", default=None,
                    help="comma-separated p|| edge override (FPS extended grid)")
    ap.add_argument("--full-phase-space", action="store_true",
                    help="lift the theta_mu truth gate (mirror the nd driver)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    names = [a.strip() for a in args.axes.split(",") if a.strip()]
    extras = [dict(und.EXTRA_AXES[a], name=a) for a in names]
    pt_edges = ([float(x) for x in args.pt_edges.split(",")] if args.pt_edges
                else u2d.PT_EDGES)
    pz_edges = ([float(x) for x in args.pz_edges.split(",")] if args.pz_edges
                else u2d.PZ_EDGES)
    if args.full_phase_space:
        import math
        u2d.MAX_MUON_THETA_RAD = math.pi
        print("[INFO] FULL PHASE SPACE: theta_mu truth gate lifted")
    edges = [pt_edges, pz_edges] + [ax["edges"] for ax in extras]
    pt_lo, pt_hi, pz_lo, pz_hi = pt_edges[0], pt_edges[-1], pz_edges[0], pz_edges[-1]

    f = ROOT.TFile.Open(args.omnifile, "READ")
    t_sig, t_bkg = f.Get("mc_signal_reco"), f.Get("mc_background")
    t_data, t_td = f.Get("data"), f.Get("mc_truth_denom")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    if args.pt_edges:
        # extended pT binning: remap the (pT-constant) integrated flux exactly as the
        # nd driver does (bin-centre lookup into the frozen-edge flux histogram)
        flux_ref, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, u2d.PT_EDGES)
        ref_e = np.asarray(u2d.PT_EDGES, float)
        ctrs = 0.5 * (np.asarray(pt_edges[:-1]) + np.asarray(pt_edges[1:]))
        ref_i = np.clip(np.digitize(ctrs, ref_e) - 1, 0, len(flux_ref) - 1)
        flux_bins = flux_ref[ref_i]
        print(f"[INFO] flux remapped to {len(pt_edges)-1} pT bins")
    else:
        flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_edges)

    meas_pt, meas_pz, meas_ex = und.collect_data_nd(t_data, extras, pt_lo, pt_hi, pz_lo, pz_hi)
    bkg_pt, bkg_pz, bkg_ex, bkg_w = und.collect_bkg_nd(t_bkg, extras, pot_scale, pt_lo, pt_hi, pz_lo, pz_hi)
    sig = und.collect_signal_nd(t_sig, extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale, use_weights=True)
    td = und.collect_truth_denom_nd(t_td, extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale, use_weights=True)

    data_nd, _ = und.histnd([meas_pt, meas_pz] + meas_ex, np.ones(meas_pt.size), edges)
    bkg_nd, _ = und.histnd([bkg_pt, bkg_pz] + bkg_ex, bkg_w, edges)
    meas_w = und.build_measured_training_nd([meas_pt, meas_pz] + meas_ex, data_nd, bkg_nd, edges)

    MCgen = np.column_stack([sig["truth_pt"], sig["truth_pz"], *sig["truth_extras"]]).astype(np.float32)
    MCreco = np.column_stack([sig["reco_pt"], sig["reco_pz"], *sig["reco_extras"]]).astype(np.float32)
    measured = np.column_stack([meas_pt, meas_pz, *meas_ex]).astype(np.float32)

    # truth-denominator binned counts (for completeness), as a flat array + shape
    dcols = [td["pt"], td["pz"]] + td["extras"]
    denom_nd, _ = und.histnd(dcols, td["w"], edges)

    np.savez_compressed(
        args.out,
        axes=np.array(names, dtype=object),
        MCgen=MCgen, MCreco=MCreco, measured=measured,
        pass_reco=sig["pass_reco"], pass_truth=sig["pass_truth"],
        w_truth=sig["w_truth"], w_reco=sig["w_reco"], measured_weights=meas_w,
        denom_nd=denom_nd,
        flux=np.asarray(flux_bins, float), data_pot=data_pot,
        n_nucleons=u2d.TRACKER_FIDUCIAL_N_NUCLEONS,
        **{f"edges_{i}": np.asarray(e, float) for i, e in enumerate(edges)},
        nedges=len(edges),
    )
    print(f"[OK] wrote {args.out}: MCgen{MCgen.shape} measured{measured.shape} "
          f"pass_truth={sig['pass_truth'].sum()} pass_reco={sig['pass_reco'].sum()}")


if __name__ == "__main__":
    main()
