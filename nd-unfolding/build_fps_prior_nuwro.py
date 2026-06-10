#!/usr/bin/env python3
"""Build the NuWro-shaped prior reweight for the FPS 3-prior envelope.

ratio(pT,pz) = [NuWro truth shape] / [MnvTune-weighted GENIE truth shape]
on the EXTENDED (pT,p||) grid, both area-normalised (shape-only: the unfold's
absolute scale comes from data via step 1). NuWro raw flat events
(3d-unfolding/genie/work_nuwro_p*/nuwro_flat.root) carry NO phase-space cut,
so they cover the extension regions. Ratio clipped to [0.2, 5] to keep the
reweight sane in empty corners.

  python build_fps_prior_nuwro.py --omnifile runEventLoopOmniFold_5D_FPS_1A.root
"""
import argparse
import glob
import os
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
    ROOT.EnableImplicitMT(8)

    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_5D_FPS_1A.root",
                    help="FPS omnifile providing the MnvTune truth shape")
    ap.add_argument("--nuwro-glob",
                    default=f"{_REPO}/3d-unfolding/genie/work_nuwro_p*/nuwro_flat.root")
    ap.add_argument("--clip", type=float, nargs=2, default=[0.2, 5.0])
    ap.add_argument("--out", default="products/5d/fps_prior_nuwro_ratio.root")
    args = ap.parse_args()

    pt_e, pz_e = np.asarray(PT_EXT), np.asarray(PZ_EXT)

    # NuWro truth shape (no phase-space cut)
    files = sorted(glob.glob(args.nuwro_glob))
    if not files:
        raise SystemExit(f"no NuWro flat files match {args.nuwro_glob}")
    pts, pzs, ws = [], [], []
    for fn in files:
        d = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(["cc", "pt", "pz", "weight"])
        sel = d["cc"].astype(bool) & np.isfinite(d["pt"]) & np.isfinite(d["pz"])
        pts.append(d["pt"][sel]); pzs.append(d["pz"][sel]); ws.append(d["weight"][sel])
    pt, pz, w = map(np.concatenate, (pts, pzs, ws))
    print(f"[prior] NuWro events kept={pt.size} from {len(files)} files")
    HN, _, _ = np.histogram2d(pt, pz, bins=[pt_e, pz_e], weights=w)

    # MnvTune truth shape from the FPS omnifile
    td = ROOT.RDataFrame("mc_truth_denom", args.omnifile)
    m2 = ROOT.RDF.TH2DModel("g2", "", len(pt_e) - 1, pt_e, len(pz_e) - 1, pz_e)
    hG = td.Histo2D(m2, "MC", "MC_pz", "w_truth").GetValue()
    HG = np.array([[hG.GetBinContent(i + 1, j + 1) for j in range(len(pz_e) - 1)]
                   for i in range(len(pt_e) - 1)])

    HNs = HN / HN.sum()
    HGs = HG / HG.sum()
    ratio = np.ones_like(HNs)
    ok = (HNs > 0) & (HGs > 0)
    ratio[ok] = np.clip(HNs[ok] / HGs[ok], args.clip[0], args.clip[1])
    n_clip = int(((HNs[ok] / HGs[ok]) != ratio[ok]).sum())
    cov_n = HG[(HG > 0) & (HN == 0)].sum() / HG.sum()
    print(f"[prior] cells ratio!=1: {int(ok.sum())}; clipped: {n_clip}; "
          f"GENIE rate in NuWro-empty cells: {100*cov_n:.2f}%")
    print(f"[prior] ratio range used: [{ratio[ok].min():.3f}, {ratio[ok].max():.3f}] "
          f"median {np.median(ratio[ok]):.3f}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fo = ROOT.TFile.Open(args.out, "RECREATE")
    h = ROOT.TH2D("hPriorRatio", "NuWro/MnvTune truth shape ratio;p_{T};p_{||}",
                  len(pt_e) - 1, pt_e, len(pz_e) - 1, pz_e)
    for i in range(len(pt_e) - 1):
        for j in range(len(pz_e) - 1):
            h.SetBinContent(i + 1, j + 1, float(ratio[i, j]))
    h.Write(); fo.Close()
    print(f"[prior] wrote {args.out}")


if __name__ == "__main__":
    main()
