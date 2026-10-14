"""Shared pieces for the playlist-spread coverage scripts: grids, projections, band groups, proxy ratios.

Grids
  analysis : 14 x 16 (p_T, p_||), uq/reported_cells.py; 205 reported cells (E_U > 0), C-order flat index.
  proxy    : 10 x 10 triage grid of the prior look (ref_shape.py). Every proxy edge is an analysis edge, so each
             analysis cell lies inside exactly one proxy cell.
"""
import hashlib
import os

import numpy as np

PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
REF = PLS[:5]
BLOCKS = {"1G-1M": ["1G", "1L", "1M"], "1N-1P": ["1N", "1O", "1P"], "1F": ["1F"], "all": PLS}

PT_A = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_A = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
PT_P = np.array([0, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5])
PZ_P = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 60])
NPT, NPZ = len(PT_A) - 1, len(PZ_A) - 1

# p_|| ranges of the step statistic (GeV/c): the 1G-1M proxy ratio is flat-low on [1.5, 8) and steps up on [8, 15)
STEP_LO, STEP_HI = (1.5, 8.0), (8.0, 15.0)


def cell_ipt_ipz(cells):
    return cells // NPZ, cells % NPZ


def proxy_index_of_cells(cells):
    """(jpt, jpz) proxy-grid indices of each analysis cell."""
    ipt, ipz = cell_ipt_ipz(cells)
    cpt = 0.5 * (PT_A[ipt] + PT_A[ipt + 1])
    cpz = 0.5 * (PZ_A[ipz] + PZ_A[ipz + 1])
    return np.searchsorted(PT_P, cpt) - 1, np.searchsorted(PZ_P, cpz) - 1


def proj_matrix(axis, cells):
    """C_1D = P C P^T as in uq/plot_uncertainty_fig6_7_style.py:178-201 (orthogonal-axis bin widths)."""
    ipt, ipz = cell_ipt_ipz(cells)
    if axis == "pt":
        M = np.zeros((NPT, cells.size))
        M[ipt, np.arange(cells.size)] = np.diff(PZ_A)[ipz]
    else:
        M = np.zeros((NPZ, cells.size))
        M[ipz, np.arange(cells.size)] = np.diff(PT_A)[ipt]
    return M


def area(cells):
    ipt, ipz = cell_ipt_ipz(cells)
    return np.diff(PT_A)[ipt] * np.diff(PZ_A)[ipz]


def category_for_band(band):
    """Copy of uq/analyze_universes.py:77-97."""
    clean = band[len("full_"):] if band.startswith("full_") else band
    if clean == "Flux":
        return "Flux"
    if clean == "__Normalization_flat":
        return "Normalization"
    if clean.startswith("Fr") or clean.startswith("MFP_") or clean.startswith("GEANT_"):
        return "Hadronic response"
    if clean.startswith("Muon_") or clean.startswith("BeamAngle") or clean in {"MuonResolution", "MinosEfficiency"}:
        return "Muon reconstruction"
    return "Models"


GROUPS = ["Flux", "Models", "Normalization", "Hadronic response", "Muon reconstruction"]


def wcov(X, w=None):
    """MAT MnvVertErrorBand::CalcCovMx (mean-centred, 1/sum w); w = None is analyze_universes.py's form."""
    X = np.asarray(X, float)
    w = np.ones(len(X)) if w is None else np.asarray(w, float)
    mu = (w[:, None] * X).sum(0) / w.sum()
    Z = X - mu
    return (Z.T * w) @ Z / w.sum()


def proxy_yields(P, meta, pls, grid="proxy"):
    """Sum over playlists of D, k*S, k*B and their variances, k = POT_d/POT_mc per playlist (per-playlist mix)."""
    D = sum(P[f"{q}__{grid}__D"] for q in pls)
    k = {q: meta[q]["pot_data"] / meta[q]["pot_mc"] for q in pls}
    S = sum(k[q] * P[f"{q}__{grid}__S"] for q in pls)
    B = sum(k[q] * P[f"{q}__{grid}__B"] for q in pls)
    S2 = sum(k[q] ** 2 * P[f"{q}__{grid}__S2"] for q in pls)
    B2 = sum(k[q] ** 2 * P[f"{q}__{grid}__B2"] for q in pls)
    return D, S, B, S2, B2


def ratio(D, S, B):
    with np.errstate(divide="ignore", invalid="ignore"):
        return (D - B) / S


def block_q(P, meta, pls, ref=REF):
    """Proxy ratio R(pls)/R(ref) on the proxy grid: per bin, p_T and p_|| marginals, total.
    Data-statistics error as the prior ref_shape.py (independent-sample formula)."""
    out = {}
    Dg, Sg, Bg, _, _ = proxy_yields(P, meta, pls)
    Dr, Sr, Br, _, _ = proxy_yields(P, meta, ref)
    for name, ax in (("bin", None), ("pt", 1), ("pz", 0), ("tot", (0, 1))):
        if ax is None:
            a, b = ratio(Dg, Sg, Bg), ratio(Dr, Sr, Br)
            ea, eb = np.sqrt(Dg) / Sg, np.sqrt(Dr) / Sr
        else:
            a, b = ratio(Dg.sum(ax), Sg.sum(ax), Bg.sum(ax)), ratio(Dr.sum(ax), Sr.sum(ax), Br.sum(ax))
            ea, eb = np.sqrt(Dg.sum(ax)) / Sg.sum(ax), np.sqrt(Dr.sum(ax)) / Sr.sum(ax)
        with np.errstate(divide="ignore", invalid="ignore"):
            q = a / b
            eq = q * np.sqrt((ea / a) ** 2 + (eb / b) ** 2)
        out[name], out[name + "_err"] = q, eq
    out["ok"] = (Dg >= 50) & (Dr >= 50)
    out["S_share"] = Sg / proxy_yields(P, meta, PLS)[1]
    return out


def step_stat_from_marginal(edges, values, weights):
    """r_hi / r_lo - 1 where r_range = sum(values*weights)/sum(weights) over the p_|| bins inside the range.
    values = ratio per bin (e.g. 1 + shift), weights = the central yield per bin."""
    lo = (edges[:-1] >= STEP_LO[0]) & (edges[1:] <= STEP_LO[1])
    hi = (edges[:-1] >= STEP_HI[0]) & (edges[1:] <= STEP_HI[1])
    r = lambda m: np.sum(values[m] * weights[m]) / np.sum(weights[m])
    return r(hi) / r(lo) - 1.0


def mahalanobis2(b, C, rcond=1e-12):
    """b^T C^+ b by eigen-decomposition, dropping eigenvalues below rcond * max. Returns (chi2, n_kept, cond)."""
    Cs = 0.5 * (C + C.T)
    lam, V = np.linalg.eigh(Cs)
    keep = lam > rcond * lam.max()
    proj = V[:, keep].T @ b
    return float(np.sum(proj ** 2 / lam[keep])), int(keep.sum()), float(lam.max() / lam[keep].min())


def file_record(path):
    """Absolute path and sha256 of an input file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return {"path": os.path.abspath(path), "sha256": h.hexdigest()}
