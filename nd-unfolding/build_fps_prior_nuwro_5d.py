#!/usr/bin/env python3
"""Build the NuWro-shaped prior reweight for the 5D FPS 3-prior envelope (step 3).

Extends build_fps_prior_nuwro.py from a (pT,p||)-only shape ratio to a
FOUR-dimensional (pT, p||, Eavail, W) shape ratio, so the envelope captures the
DIS-tail generator spread that motivated the W axis -- the generator differences
between NuWro and GENIE live in the hadronic variables (Eavail, W), not just muon
kinematics. q3 is intentionally NOT included: the plan specifies (pT,p||,Eavail,W),
and adding q3 would only thin the per-cell statistics of the shape ratio.

  ratio(pT,p||,Eavail,W) = [NuWro truth shape] / [MnvTune-weighted GENIE truth shape]

Both area-normalised (shape-only: the absolute scale comes from data via OmniFold
step 1). NuWro raw flat events (3d-unfolding/genie/work_nuwro_p*/nuwro_flat.root,
branches cc/pt/pz/eavail/W/weight) carry NO phase-space cut, so they populate the
FPS extension regions. Ratio clipped to [0.2, 5]; cells where either generator is
empty fall back to ratio = 1 (no reweight where there is no shape information).

Binning: PT_EXT x PZ_EXT (the FPS extended muon grid from fps_acceptance) x the
analysis Eavail edges (of_inputs_pc.npz edges_2) x the analysis W edges
(of_inputs_5d.npz edges_4). The envelope driver applies this per truth event by a
4D bin lookup on (MC, MC_pz, MC_eavail, MC_W).

Weight-INDEPENDENT: needs only NuWro flat events + the FPS truth denominator, not the
trained PET weights -- so it is built/validated ahead of the PET FPS train finishing.

Run from nd-unfolding/ after `source ../setup_salloc_env.sh`:
  python build_fps_prior_nuwro_5d.py --omnifile runEventLoopOmniFold_PC_FPS_MEFHC.root
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
    ROOT.EnableImplicitMT(16)

    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_PC_FPS_MEFHC.root",
                    help="FPS omnifile providing the MnvTune truth shape (mc_truth_denom)")
    ap.add_argument("--nuwro-glob",
                    default=f"{_REPO}/3d-unfolding/genie/work_nuwro_p*/nuwro_flat.root")
    ap.add_argument("--eav-source", default=f"{_REPO}/nd-unfolding/of_inputs_pc.npz")
    ap.add_argument("--w-source", default=f"{_REPO}/nd-unfolding/of_inputs_5d.npz")
    ap.add_argument("--clip", type=float, nargs=2, default=[0.2, 5.0])
    ap.add_argument("--out", default=f"{_REPO}/nd-unfolding/products/5d/fps_prior_nuwro_ratio_5d.npz")
    args = ap.parse_args()

    pt_e = np.asarray(PT_EXT, float)
    pz_e = np.asarray(PZ_EXT, float)
    eav_e = np.asarray(np.load(args.eav_source)["edges_2"], float)
    w_e = np.asarray(np.load(args.w_source)["edges_4"], float)
    bins = [pt_e, pz_e, eav_e, w_e]
    shape = tuple(len(b) - 1 for b in bins)
    print(f"[prior5d] grid = {shape}  ({int(np.prod(shape))} cells)")
    print(f"[prior5d] eav edges = {eav_e}\n[prior5d] W edges = {w_e}")

    # ---- NuWro truth shape (no phase-space cut) ----
    files = sorted(glob.glob(args.nuwro_glob))
    if not files:
        raise SystemExit(f"no NuWro flat files match {args.nuwro_glob}")
    cols = {k: [] for k in ("pt", "pz", "eavail", "W", "weight")}
    for fn in files:
        d = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(["cc", "pt", "pz", "eavail", "W", "weight"])
        sel = d["cc"].astype(bool)
        for k in ("pt", "pz", "eavail", "W"):
            sel &= np.isfinite(d[k])
        for k in cols:
            cols[k].append(d[k][sel])
    N = {k: np.concatenate(v) for k, v in cols.items()}
    print(f"[prior5d] NuWro events kept = {N['pt'].size} from {len(files)} files")
    HN, _ = np.histogramdd(np.stack([N["pt"], N["pz"], N["eavail"], N["W"]], axis=1),
                           bins=bins, weights=N["weight"])

    # ---- MnvTune truth shape from the FPS omnifile denominator ----
    td = ROOT.RDataFrame("mc_truth_denom", args.omnifile).AsNumpy(
        ["MC", "MC_pz", "MC_eavail", "MC_W", "w_truth"])
    gsel = np.isfinite(td["MC"]) & np.isfinite(td["MC_pz"]) & \
        np.isfinite(td["MC_eavail"]) & np.isfinite(td["MC_W"])
    print(f"[prior5d] MnvTune truth events = {int(gsel.sum())} (of {td['MC'].size})")
    HG, _ = np.histogramdd(
        np.stack([td["MC"][gsel], td["MC_pz"][gsel], td["MC_eavail"][gsel], td["MC_W"][gsel]], axis=1),
        bins=bins, weights=td["w_truth"][gsel])

    # ---- shape ratio, clipped, ratio=1 where either side empty ----
    HNs = HN / HN.sum()
    HGs = HG / HG.sum()
    ratio = np.ones(shape, float)
    ok = (HNs > 0) & (HGs > 0)
    raw = np.where(ok, HNs / np.where(HGs > 0, HGs, 1), 1.0)
    ratio[ok] = np.clip(raw[ok], args.clip[0], args.clip[1])
    n_clip = int((raw[ok] != ratio[ok]).sum())
    cov_n = HG[(HG > 0) & (HN == 0)].sum() / HG.sum()  # GENIE rate in NuWro-empty cells
    print(f"[prior5d] cells ratio!=1: {int(ok.sum())}/{int(np.prod(shape))}; clipped: {n_clip}; "
          f"GENIE rate in NuWro-empty cells: {100*cov_n:.2f}%")
    print(f"[prior5d] ratio range used: [{ratio[ok].min():.3f}, {ratio[ok].max():.3f}] "
          f"median {np.median(ratio[ok]):.3f}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    np.savez(args.out, ratio=ratio, edges_pt=pt_e, edges_pz=pz_e,
             edges_eav=eav_e, edges_W=w_e,
             clip=np.asarray(args.clip), n_clip=n_clip, genie_in_nuwro_empty=cov_n)
    print(f"[prior5d] wrote {args.out}")


if __name__ == "__main__":
    main()
