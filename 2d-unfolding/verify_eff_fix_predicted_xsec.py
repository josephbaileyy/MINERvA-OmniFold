#!/usr/bin/env python3
"""Predict the post-fix MEHFC cross section without re-running OmniFold.

The pre-fix unfolded result `2d_crossSection_omnifold_MEHFC_5iter.root`
stores `hXSec2D = U / (Φ · N · POT · ΔpT · Δp||)` (no ε division). The
post-fix formula is `hXSec2D_new = hXSec2D_old / ε`, where:

    ε = hEffNum / hEffDen_full
    hEffNum    = mc_signal_reco truth-pass + sim_pass events (unchanged)
    hEffDen_old = mc_signal_reco truth-pass events (the bug)
    hEffDen_new = mc_truth_denom (the canonical denominator)

So per-bin scale factor:
    hXSec_new[i,j] = hXSec_old[i,j] · (hEffDen_old[i,j] / hEffDen_new[i,j])
                   = hXSec_old[i,j] · (1 / ε_new) · ε_old
where ε_old = hEffNum / hEffDen_old (=1 for the cancellation since the
old code does not divide). Equivalently, the multiplicative correction
factor is k[i,j] = hEffDen_new[i,j] / hEffDen_old[i,j].

This script computes k per bin and applies it to the stored hXSec2D,
then totals over the 205 reported bins for comparison with the paper.
"""
import math
import os
import sys
import tempfile

os.environ.setdefault(
    "MPLCONFIGDIR",
    os.path.join(tempfile.gettempdir(), "minerva101-mplconfig"),
)

import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
sys.path.insert(0, REPO)
from unfold_2d_omnifold_unbinned import PT_EDGES, PZ_EDGES  # noqa: E402

PRE_XSEC = f"{REPO}/2d_crossSection_omnifold_MEHFC_5iter.root"
OMNIFOLD_INPUT = f"{REPO}/runEventLoopOmniFold_MEHFC.root"
PAPER_TOTAL = 3.039e-38  # paper-reported xsec summed over 205 bins
PRE_TOTAL = 2.285e-38    # current MEHFC integrated total (status doc)

N_PT = len(PT_EDGES) - 1
N_PZ = len(PZ_EDGES) - 1
TAN_THETA_MAX = math.tan(math.radians(20.0))


def load_hist_2d(path, name):
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"open failed: {path}")
    h = f.Get(name)
    if not h:
        raise RuntimeError(f"{name} missing in {path}")
    arr = np.zeros((N_PT, N_PZ), dtype=float)
    for ix in range(1, N_PT + 1):
        for iy in range(1, N_PZ + 1):
            arr[ix - 1, iy - 1] = float(h.GetBinContent(ix, iy))
    f.Close()
    return arr


def fill_truth_denom(pot_scale):
    """Project mc_truth_denom with POT-scaled w_truth, matching the
    POT-scaling that compute_efficiency_2d applies via sig."""
    from array import array as carray
    f = ROOT.TFile.Open(OMNIFOLD_INPUT, "READ")
    t = f.Get("mc_truth_denom")
    pt_edges_c = carray("d", PT_EDGES)
    pz_edges_c = carray("d", PZ_EDGES)
    ROOT.gROOT.cd()
    if ROOT.gDirectory.Get("h_den_new"): ROOT.gDirectory.Delete("h_den_new;*")
    h = ROOT.TH2D("h_den_new", "denom",
                  N_PT, pt_edges_c, N_PZ, pz_edges_c)
    n = t.Project("h_den_new", "MC_pz:MC",
                  f"w_truth * {pot_scale:.10g}", "")
    print(f"[INFO] mc_truth_denom: projected {n} entries, "
          f"POT-scaled sum = {h.Integral():.6g}")
    arr = np.zeros((N_PT, N_PZ), dtype=float)
    for ix in range(1, N_PT + 1):
        for iy in range(1, N_PZ + 1):
            arr[ix - 1, iy - 1] = h.GetBinContent(ix, iy)
    f.Close()
    return arr


def get_pot_scale_from(path):
    f = ROOT.TFile.Open(path, "READ")
    p = f.Get("potScale")
    if not p:
        raise RuntimeError(f"potScale missing in {path}")
    s = float(p.GetVal())
    f.Close()
    return s


def reported_bins_mask():
    """205 reported bins: exclude (pt_lo*pz_hi outside 20° cone) per paper."""
    # Strict mask matching diagnose_truth_shape_vs_paper.py: pt_hi/pz_lo <= tan20
    mask_strict = np.zeros((N_PT, N_PZ), dtype=bool)
    mask_205 = np.zeros((N_PT, N_PZ), dtype=bool)
    for ptb in range(N_PT):
        pt_hi = PT_EDGES[ptb + 1]
        pt_lo = PT_EDGES[ptb]
        for pzb in range(N_PZ):
            pz_lo = PZ_EDGES[pzb]
            mask_strict[ptb, pzb] = (pt_hi / pz_lo) <= TAN_THETA_MAX
            # 205-bin convention: exclude bins fully outside 20° cone
            mask_205[ptb, pzb] = (pt_lo / pz_lo) <= TAN_THETA_MAX
    return mask_strict, mask_205


def main():
    print(f"[INFO] loading pre-fix hEffDen, hXSec2D from {PRE_XSEC}")
    eff_den_old = load_hist_2d(PRE_XSEC, "hEffDen")
    xsec_old = load_hist_2d(PRE_XSEC, "hXSec2D")
    eff_num_old = load_hist_2d(PRE_XSEC, "hEffNum")
    print(f"[INFO]   sum(hEffDen_old) = {eff_den_old.sum():.6g}")
    print(f"[INFO]   sum(hEffNum)     = {eff_num_old.sum():.6g}")
    print(f"[INFO]   eff_avg (old)    = "
          f"{eff_num_old.sum()/eff_den_old.sum():.4f}")

    pot_scale = get_pot_scale_from(PRE_XSEC)
    print(f"\n[INFO] potScale (from pre-fix output) = {pot_scale:.6f}")
    print(f"[INFO] building new hEffDen from mc_truth_denom (POT-scaled)")
    eff_den_new = fill_truth_denom(pot_scale)
    print(f"[INFO]   sum(hEffDen_new) = {eff_den_new.sum():.6g}")
    print(f"[INFO]   global ratio old/new = "
          f"{eff_den_old.sum()/eff_den_new.sum():.4f}")
    print(f"[INFO]   eff_avg (new)    = "
          f"{eff_num_old.sum()/eff_den_new.sum():.4f}")

    # The correct correction is the OmniFold input completeness:
    #   c = (mc_signal_reco truth-pass events) / (mc_truth_denom)
    #     = hEffDen_old / hEffDen_new  (with consistent POT scaling)
    # OmniFold's step-1 miss regression handles within-input misses
    # (sim_pass=False), so dividing by the absolute selection efficiency
    # over-corrects. Dividing by completeness scales hUnfold from the
    # OmniFold-input truth subset to the full truth phase space.
    completeness = np.where(eff_den_new > 0,
                            eff_den_old / np.maximum(eff_den_new, 1e-300),
                            0.0)
    xsec_new = np.where(completeness > 0,
                        xsec_old / np.maximum(completeness, 1e-300),
                        0.0)
    print(f"[INFO]   global completeness = {eff_den_old.sum()/eff_den_new.sum():.4f}")

    pt_w = np.diff(PT_EDGES)
    pz_w = np.diff(PZ_EDGES)
    bin_areas = np.outer(pt_w, pz_w)

    mask_strict, mask_205 = reported_bins_mask()

    # Total xsec = sum(d2sigma * dpT * dpz) over reported bins.
    total_old_205 = float((xsec_old * bin_areas * mask_205).sum())
    total_new_205 = float((xsec_new * bin_areas * mask_205).sum())
    total_old_strict = float((xsec_old * bin_areas * mask_strict).sum())
    total_new_strict = float((xsec_new * bin_areas * mask_strict).sum())

    print(f"\n[RESULT] 205-bin totals:")
    print(f"  pre-fix  : {total_old_205:.4e} cm^2/nucleon "
          f"(stored claim: {PRE_TOTAL:.4e})")
    print(f"  post-fix : {total_new_205:.4e} cm^2/nucleon "
          f"(paper:        {PAPER_TOTAL:.4e})")
    print(f"  ratio post/paper: {total_new_205/PAPER_TOTAL:.4f}")
    print(f"  ratio pre/paper:  {total_old_205/PAPER_TOTAL:.4f}")

    print(f"\n[RESULT] 185-bin strict-interior totals:")
    print(f"  pre-fix  : {total_old_strict:.4e}")
    print(f"  post-fix : {total_new_strict:.4e}")

    # Per-strip ratio (paper-comparable). Build simple p_|| projection
    # in the 205-bin region by summing the differential xsec * dpT.
    proj_old = (xsec_old * pt_w[:, None] * mask_205).sum(axis=0)
    proj_new = (xsec_new * pt_w[:, None] * mask_205).sum(axis=0)

    print(f"\n[RESULT] dsigma/dp_|| (post-fix vs pre-fix) by strip:")
    print(f"{'pz_lo':>5} {'pz_hi':>5} "
          f"{'dsig_pre':>12} {'dsig_post':>12} {'post/pre':>9}")
    for j in range(N_PZ):
        if proj_old[j] == 0 and proj_new[j] == 0:
            continue
        ratio = proj_new[j]/proj_old[j] if proj_old[j] > 0 else float("nan")
        print(f"{PZ_EDGES[j]:5.1f} {PZ_EDGES[j+1]:5.1f} "
              f"{proj_old[j]:12.4e} {proj_new[j]:12.4e} {ratio:9.4f}")


if __name__ == "__main__":
    main()
