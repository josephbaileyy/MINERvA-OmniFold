#!/usr/bin/env python3
"""Self-normalized shape comparison: 2D OmniFold vs arXiv:2106.16210.

Defines the unit-area shape

    shape(i,j) = xsec(i,j) / sum_{B} xsec(B) * dpT(B) * dp||(B)

evaluated identically on our `hXSec2D` and on the paper-ancillary
TH2D `pt_pl_cross_section`. Total flux normalization, target nucleon
count, POT, and the absolute scale of the FluxAndCV reweighter all
cancel by construction; what survives is the per-Eν shape effect of
flux CV (much smaller than the 1.41x scale mismatch at p||=1.5-2 GeV/c).

Reports shape chi^2 with the paper's full covariance propagated through
the unit-area Jacobian:

    s = x / (w . x)             (w = bin widths, dot = sum)
    J_ij = (delta_ij - s_i * w_j) / (w . x)
    C_shape = J C_paper J^T

J has rank n-1 (one direction killed by the unit-area constraint), so
C_shape is rank-deficient by 1 and we use a pseudo-inverse on the
selected block. ndf = (n_selected_bins - 1) accordingly.

Two bin selections are reported:
  * 205-bin paper-reported set (paper's own sigma_total definition)
  * 185-bin strict-interior set (pt_hi/pz_lo <= tan 20 deg) -- noisy
    edges removed; secondary number, not the headline.

Outputs:
  * ROOT file with hXSec2D_shape (ours), hXSecPaper2D_shape (paper),
    and the propagated covariance C_shape_205, C_shape_185 as
    TMatrixDSym instances.
  * stdout summary printed in the same style as compare_to_paper_*.py
    so the run log can ingest it directly.
"""
import argparse
import math
import pathlib
import sys

import numpy as np
import ROOT

_UQ = str(pathlib.Path(__file__).resolve().parent / "uq")
if _UQ not in sys.path:
    sys.path.append(_UQ)
from reported_cells import th2d_edges  # noqa: E402


ANC_DIR = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc"
DEFAULT_OURS = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root"
DEFAULT_OUT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter_shape.root"

N_PT, N_PZ = 14, 16
N = N_PT * N_PZ

# The analysis grid (bin_mapping.txt's printed edges). main() takes each side's widths from its own TH2D axes.
PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
THETA_MAX_DEG = 20.0
TAN_THETA_MAX = math.tan(math.radians(THETA_MAX_DEG))


def tm_to_np(tm):
    n = tm.GetNrows()
    a = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            a[i, j] = tm(i, j)
    return a


def fill_paper(h):
    """Paper TH2D: x=p||(16), y=pt(14). gid = (ptb-1)*16 + (pzb-1)."""
    if (h.GetNbinsX(), h.GetNbinsY()) != (N_PZ, N_PT):
        raise ValueError(f"{h.GetName()}: {h.GetNbinsX()} x {h.GetNbinsY()} bins, expected x = p|| ({N_PZ}), "
                         f"y = pt ({N_PT})")
    v = np.zeros(N)
    for ix in range(1, N_PZ + 1):
        for iy in range(1, N_PT + 1):
            gid = (iy - 1) * N_PZ + (ix - 1)
            v[gid] = h.GetBinContent(ix, iy)
    return v


def fill_ours(h):
    """Our TH2D: x=pt(14), y=p||(16)."""
    v = np.zeros(N)
    for ix in range(1, N_PT + 1):
        for iy in range(1, N_PZ + 1):
            gid = (ix - 1) * N_PZ + (iy - 1)
            v[gid] = h.GetBinContent(ix, iy)
    return v


def bin_widths(pt_edges=PT_EDGES, pz_edges=PZ_EDGES):
    """w[gid] = ΔpT * Δp||  for each (ptb, pzb) bin."""
    w = np.zeros(N)
    for ptb in range(1, N_PT + 1):
        dpt = pt_edges[ptb] - pt_edges[ptb - 1]
        for pzb in range(1, N_PZ + 1):
            dpz = pz_edges[pzb] - pz_edges[pzb - 1]
            w[(ptb - 1) * N_PZ + (pzb - 1)] = dpt * dpz
    return w


def interior_mask(pt_edges=PT_EDGES, pz_edges=PZ_EDGES):
    m = np.zeros(N, dtype=bool)
    for ptb in range(1, N_PT + 1):
        pt_hi = pt_edges[ptb]
        for pzb in range(1, N_PZ + 1):
            pz_lo = pz_edges[pzb - 1]
            m[(ptb - 1) * N_PZ + (pzb - 1)] = (pt_hi / pz_lo) <= TAN_THETA_MAX
    return m


def normalize_shape(x, w, mask):
    """Return shape vector s (full length N) and total = sum_{mask} x*w."""
    total = float((x * w * mask).sum())
    s = np.zeros_like(x)
    s[mask] = x[mask] / total
    return s, total


def shape_jacobian(x, w, mask, total):
    """Jacobian J of s_i = x_i / sum_{mask} x_j w_j, restricted to mask block.

    For i, j both in mask:
        J_ij = (delta_ij - s_i * w_j) / total
    """
    idx = np.where(mask)[0]
    n = len(idx)
    s_sub = (x[idx] / total)
    w_sub = w[idx]
    J = (np.eye(n) - np.outer(s_sub, w_sub)) / total
    return J, idx


def shape_chi2(ours_v, paper_v, w, cov_paper, mask, tag, w_ours=None):
    """Compute shape chi^2 with paper covariance propagated through the
    unit-area Jacobian. `w` are the paper's bin areas and `w_ours` ours
    (default `w`). Returns (chi2, ndf, shape_ours, shape_paper,
    cov_shape, idx_used).
    """
    diag = np.diag(cov_paper)
    use = mask & (diag > 0)
    s_ours, tot_ours = normalize_shape(ours_v, w if w_ours is None else w_ours, use)
    s_paper, tot_paper = normalize_shape(paper_v, w, use)

    J, idx = shape_jacobian(paper_v, w, use, tot_paper)
    C_block = cov_paper[np.ix_(idx, idx)]
    C_shape = J @ C_block @ J.T

    d = (s_ours - s_paper)[idx]
    if w_ours is not None and not np.array_equal(w_ours[idx], w[idx]):
        # C_shape's null vector is the paper's area vector (the unit-area constraint). With our areas
        # different, d has a component along it, which an exact pseudo-inverse ignores and a numerical
        # one may not; drop it explicitly.
        u = w[idx] / np.linalg.norm(w[idx])
        d = d - (d @ u) * u
    Cinv = np.linalg.pinv(C_shape)
    chi2 = float(d @ Cinv @ d)
    ndf = max(int(use.sum()) - 1, 1)  # one DOF removed by unit-area constraint

    print(f"  {tag:32s}  chi2 = {chi2:9.2f}   ndf = {ndf:3d}   "
          f"chi2/ndf = {chi2/ndf:6.3f}   "
          f"sigma_tot(ours)/sigma_tot(paper) = {tot_ours/tot_paper:.4f}")
    return chi2, ndf, s_ours, s_paper, C_shape, idx


def shape_to_th2d(name, title, s_vec, pt_edges=PT_EDGES, pz_edges=PZ_EDGES):
    """Pack a shape vector back into a TH2D with the given bin edges (x=pt, y=p||)."""
    pt_edges = np.array(pt_edges, dtype="d")
    pz_edges = np.array(pz_edges, dtype="d")
    h = ROOT.TH2D(name, title, N_PT, pt_edges, N_PZ, pz_edges)
    h.GetXaxis().SetTitle("p_{T} (GeV/c)")
    h.GetYaxis().SetTitle("p_{||} (GeV/c)")
    h.GetZaxis().SetTitle("(1/#sigma) d^{2}#sigma/(dp_{T} dp_{||}) (GeV/c)^{-2}")
    h.SetDirectory(0)
    for ptb in range(1, N_PT + 1):
        for pzb in range(1, N_PZ + 1):
            gid = (ptb - 1) * N_PZ + (pzb - 1)
            h.SetBinContent(ptb, pzb, s_vec[gid])
    return h


def cov_to_tmatrix(C, idx_used):
    """Pack C_shape (size n_used) into a 224x224 TMatrixDSym indexed by global IDs."""
    M = ROOT.TMatrixDSym(N)
    for ii, gi in enumerate(idx_used):
        for jj, gj in enumerate(idx_used):
            M[int(gi)][int(gj)] = float(C[ii, jj])
    return M


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ours", default=DEFAULT_OURS,
                    help="Path to our 2D cross-section ROOT file (contains hXSec2D)")
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="Output ROOT file with shape histograms and propagated cov")
    args = ap.parse_args()

    print(f"[paper] opening {ANC_DIR}/cov_ptpl_minerva_inclusive_6GeV.root")
    fp = ROOT.TFile.Open(f"{ANC_DIR}/cov_ptpl_minerva_inclusive_6GeV.root")
    h_paper = fp.Get("pt_pl_cross_section")
    paper_v = fill_paper(h_paper)
    paper_pt, paper_pz = th2d_edges(h_paper)
    cov_tot = tm_to_np(fp.Get("TotalCovariance"))
    cov_sta = tm_to_np(fp.Get("StatOnlyCovariance"))

    print(f"[ours] opening {args.ours}")
    fo = ROOT.TFile.Open(args.ours)
    h_ours = fo.Get("hXSec2D")
    ours_v = fill_ours(h_ours)
    ours_pt, ours_pz = th2d_edges(h_ours)
    fo.Close()

    w = bin_widths(paper_pt, paper_pz)
    w_ours = bin_widths(ours_pt, ours_pz)
    m_rep = (np.diag(cov_sta) > 0)
    m_int = interior_mask(paper_pt, paper_pz) & m_rep
    print(f"[masks] reported={int(m_rep.sum())}/{N}  strict-interior={int(m_int.sum())}/{N}")

    # 205-bin shape: paper's own sigma_total definition
    print("\n=== shape chi^2, 205 reported bins (headline) ===")
    chi2_205, ndf_205, s_o_205, s_p_205, C_205, idx_205 = shape_chi2(
        ours_v, paper_v, w, cov_tot, m_rep,
        "TOTAL covariance, 205-bin shape", w_ours)
    chi2_205_stat, _, _, _, _, _ = shape_chi2(
        ours_v, paper_v, w, cov_sta, m_rep,
        "STAT-only covariance, 205-bin shape", w_ours)

    # 185-bin interior shape: secondary
    print("\n=== shape chi^2, 185 strict-interior bins (secondary) ===")
    chi2_185, ndf_185, s_o_185, s_p_185, C_185, idx_185 = shape_chi2(
        ours_v, paper_v, w, cov_tot, m_int,
        "TOTAL covariance, 185-bin shape", w_ours)

    # Sanity: shape integrals must equal 1 on the selected bins
    for label, s, mask, w_side in [("205 ours", s_o_205, m_rep, w_ours),
                                    ("205 paper", s_p_205, m_rep, w),
                                    ("185 ours", s_o_185, m_int, w_ours),
                                    ("185 paper", s_p_185, m_int, w)]:
        integral = float((s * w_side * mask).sum())
        print(f"  closure: shape integral on {label} = {integral:.10f}")

    # Save shape histograms and propagated covariances
    print(f"\n[out] writing {args.out}")
    fout = ROOT.TFile.Open(args.out, "RECREATE")
    shape_to_th2d("hXSec2D_shape_205", "OmniFold shape, 205-bin", s_o_205, ours_pt, ours_pz).Write()
    shape_to_th2d("hXSecPaper2D_shape_205", "Paper shape, 205-bin", s_p_205, paper_pt, paper_pz).Write()
    shape_to_th2d("hXSec2D_shape_185", "OmniFold shape, 185-bin", s_o_185, ours_pt, ours_pz).Write()
    shape_to_th2d("hXSecPaper2D_shape_185", "Paper shape, 185-bin", s_p_185, paper_pt, paper_pz).Write()
    fout.WriteObject(cov_to_tmatrix(C_205, idx_205), "CShape205_total")
    fout.WriteObject(cov_to_tmatrix(C_185, idx_185), "CShape185_total")
    # Persist scalar diagnostics
    ROOT.TParameter("double")("chi2_shape_205_total", chi2_205).Write()
    ROOT.TParameter("int")("ndf_shape_205", ndf_205).Write()
    ROOT.TParameter("double")("chi2_shape_205_stat", chi2_205_stat).Write()
    ROOT.TParameter("double")("chi2_shape_185_total", chi2_185).Write()
    ROOT.TParameter("int")("ndf_shape_185", ndf_185).Write()
    fout.Close()
    fp.Close()

    print("\nSummary for run log / slide:")
    print(f"  205-bin shape chi^2/ndf (total cov)  = {chi2_205/ndf_205:.3f}   "
          f"({chi2_205:.1f}/{ndf_205})")
    print(f"  205-bin shape chi^2/ndf (stat only)  = {chi2_205_stat/ndf_205:.3f}")
    print(f"  185-bin shape chi^2/ndf (total cov)  = {chi2_185/ndf_185:.3f}   "
          f"({chi2_185:.1f}/{ndf_185})")


if __name__ == "__main__":
    main()
