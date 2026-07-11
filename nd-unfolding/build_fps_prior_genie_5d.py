#!/usr/bin/env python3
"""Build the bare-GENIE prior reweight for the 5D FPS 3-prior envelope (step 3).

Companion to build_fps_prior_nuwro_5d.py (school): same 4D (pT,p||,Eavail,W)
shape-ratio machinery + save schema, so the envelope driver consumes both priors
identically. Here the alternative prior is BARE GENIE = the no-weights MC shape
(the 2D pilot's use_weights=False / "no-weights mode" prior), i.e. the raw
generated distribution with the MINERvA tune removed:

  ratio(pT,p||,Eavail,W) = [unweighted GENIE truth shape] / [MnvTune-weighted shape]

Both area-normalised (shape-only). Applied per truth event by a 4D bin lookup on
(MC, MC_pz, MC_eavail, MC_W) in the envelope driver, exactly as the NuWro ratio.
Ratio clipped to [0.2, 5]; cells where either side is empty fall back to 1.

  python build_fps_prior_genie_5d.py --omnifile runEventLoopOmniFold_PC_FPS_MEFHC.root
"""
import argparse
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from fps_acceptance import PT_EXT, PZ_EXT


def main():
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_PC_FPS_MEFHC.root",
                    help="FPS omnifile providing the truth shape (mc_truth_denom)")
    ap.add_argument("--eav-source", default="of_inputs_pc.npz",
                    help="npz providing edges_2 (Eavail edges)")
    ap.add_argument("--w-source", default="of_inputs_5d.npz",
                    help="npz providing edges_4 (W edges)")
    ap.add_argument("--clip", type=float, nargs=2, default=[0.2, 5.0])
    ap.add_argument("--out", default=f"{_REPO}/nd-unfolding/products/5d/fps_prior_genie_ratio_5d.npz")
    args = ap.parse_args()

    pt_e = np.asarray(PT_EXT, float)
    pz_e = np.asarray(PZ_EXT, float)
    eav_e = np.asarray(np.load(args.eav_source)["edges_2"], float)
    w_e = np.asarray(np.load(args.w_source)["edges_4"], float)
    edges = [pt_e, pz_e, eav_e, w_e]
    shape = tuple(len(e) - 1 for e in edges)
    print(f"[genie5d] grid {shape}  PT_EXT[{pt_e[0]},{pt_e[-1]}] PZ_EXT[{pz_e[0]},{pz_e[-1]}]")
    print(f"[genie5d] eav edges = {eav_e}\n[genie5d] W edges = {w_e}")

    td = ROOT.RDataFrame("mc_truth_denom", args.omnifile).AsNumpy(
        ["MC", "MC_pz", "MC_eavail", "MC_W", "w_truth"])
    gsel = (np.isfinite(td["MC"]) & np.isfinite(td["MC_pz"])
            & np.isfinite(td["MC_eavail"]) & np.isfinite(td["MC_W"]))
    coords = np.stack([td["MC"][gsel], td["MC_pz"][gsel],
                       td["MC_eavail"][gsel], td["MC_W"][gsel]], axis=1)
    wt = td["w_truth"][gsel].astype(np.float64)
    print(f"[genie5d] truth events = {int(gsel.sum())} (of {td['MC'].size})")

    HG, _ = np.histogramdd(coords, bins=edges, weights=wt)          # MnvTune-weighted shape
    HB, _ = np.histogramdd(coords, bins=edges)                      # unweighted (bare-GENIE) shape

    HGs = HG / HG.sum()
    HBs = HB / HB.sum()
    ratio = np.ones(shape, float)
    ok = (HBs > 0) & (HGs > 0)
    raw = np.ones(shape, float)
    raw[ok] = HBs[ok] / HGs[ok]
    ratio[ok] = np.clip(raw[ok], args.clip[0], args.clip[1])
    n_clip = int((raw[ok] != ratio[ok]).sum())
    cov_n = HG[(HG > 0) & (HB == 0)].sum() / HG.sum()
    print(f"[genie5d] cells ratio!=1: {int(ok.sum())}/{int(np.prod(shape))}; clipped: {n_clip}; "
          f"tuned rate in bare-empty cells: {100*cov_n:.3f}%")
    print(f"[genie5d] ratio range used: [{ratio[ok].min():.3f}, {ratio[ok].max():.3f}] "
          f"median {np.median(ratio[ok]):.3f}")

    np.savez(args.out, ratio=ratio, edges_pt=pt_e, edges_pz=pz_e,
             edges_eav=eav_e, edges_W=w_e,
             clip=np.asarray(args.clip), n_clip=n_clip, tuned_in_bare_empty=cov_n)
    print(f"[genie5d] wrote {args.out}")


if __name__ == "__main__":
    main()
