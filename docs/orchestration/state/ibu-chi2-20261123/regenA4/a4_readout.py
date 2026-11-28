#!/usr/bin/env python3
"""regenA amendment A4: the numbers behind four appC caption claims, on one input. Reads; draws nothing.

  a4_readout.py --module-dir <W>/2d-unfolding --anc <anc dir> --xsec <xsec.root> --captures <FR>/cap --out <json>

(1) tension_mode_maps (appC:22-23): the six modes the figure draws, chosen as diagnose_tension.py:137-154 does
    (eigh of the published TotalCovariance on the 205 reported cells; ranked by c_k^2 / lam_k, c = U^T (ours - pub)).
    For each panel (a)-(f): its chi2 contribution, the share of sum u^2 in the two highest p_par bins (20-60 GeV/c),
    and the p_par bin of the largest |u|.
(2) the slice figures (appC:30, :37): for each pT slice and each p_par slice, over the slice's reported cells,
    D_ours = sum ((ours - pub) / s)^2 and D_prior = sum ((prior - pub) / s)^2, with s the published statistical
    standard deviation (sqrt of StatOnlyCovariance's diagonal, the bars the figures draw). The prior is the figures'
    own (plot_2d_cross_section.compute_truth_xsec_2d of hOFTruthDenom2D, as plot_2d_paper_comparison.main() makes it).
    "toward" counts the slices with D_ours < D_prior.
(3) each slice panel's printed chi2/n string, read from the capture's drawn texts (.texts files).
"""
import argparse, glob, json, re, sys
import numpy as np

ap = argparse.ArgumentParser()
for k in ("module-dir", "anc", "xsec", "captures", "out"):
    ap.add_argument("--" + k, required=True)
a = ap.parse_args()
sys.path[:0] = [a.module_dir, a.module_dir + "/uq"]
import ROOT
import compare_to_paper_fullcov as cpf
import plot_2d_cross_section as pxs

N_PT, N_PZ = 14, 16
fp = ROOT.TFile.Open(f"{a.anc}/cov_ptpl_minerva_inclusive_6GeV.root")
pub = cpf.flatten_th2d(fp.Get("pt_pl_cross_section"))
cov_t = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance")); cov_s = cpf.tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
fp.Close()
fo = ROOT.TFile.Open(a.xsec)
ours = cpf.flatten_ours(fo.Get("hXSec2D"))
h_truth = fo.Get("hOFTruthDenom2D") or fo.Get("hTruth2D")
flux, flux_src = pxs.load_flux_bins_for_truth(fo, a.xsec, pt_edges=pxs.th2d_edges(h_truth)[0])
prior_h = pxs.compute_truth_xsec_2d(h_truth, fo.Get("hEff2D"), flux, float(fo.Get("dataPOT").GetVal()),
                                     float(fo.Get("nNucleons").GetVal()))
prior = cpf.flatten_ours(prior_h)
pt_edges = [float(x) for x in pxs.th2d_edges(fo.Get("hXSec2D"))[0]]
fo.Close()

mask = np.diag(cov_s) > 0
n = int(mask.sum())
# (1) modes, as diagnose_tension.py:110-154
d = (ours - pub)[mask]
V = cov_t[np.ix_(mask, mask)]
lam, U = np.linalg.eigh(V)
c = U.T @ d
keep = lam > 1e-15 * lam.max()
contrib = np.where(keep, c ** 2 / np.where(keep, lam, 1.0), 0.0)
order = np.argsort(contrib)[::-1]
idx = np.where(mask)[0]
modes = []
for j in range(6):
    k = order[j]
    g = np.zeros((N_PT, N_PZ)); g[idx // N_PZ, idx % N_PZ] = U[:, k] ** 2
    ipt, ipz = np.unravel_index(int(np.argmax(g)), g.shape)
    modes.append({"panel": "abcdef"[j], "chi2_contrib": float(contrib[k]), "share_pz_ge_20": float(g[:, 14:].sum() / g.sum()),
                  "argmax_pz_bin": int(ipz), "argmax_pt_bin": int(ipt)})
# (2) slices
s = np.sqrt(np.where(mask, np.diag(cov_s), np.nan))
G = lambda v: v.reshape(N_PT, N_PZ)
M, O, P, PUB, S = G(mask), G(ours), G(prior), G(pub), G(s)
def slices(axis):
    rows = []
    for i in range(N_PT if axis == "pt" else N_PZ):
        sel = (lambda X: X[i, :]) if axis == "pt" else (lambda X: X[:, i])
        m = sel(M)
        do = float(np.sum(((sel(O) - sel(PUB)) / sel(S))[m] ** 2)); dp = float(np.sum(((sel(P) - sel(PUB)) / sel(S))[m] ** 2))
        rows.append({"slice": i, "n_cells": int(m.sum()), "D_ours": do, "D_prior": dp, "toward": do < dp})
    return {"rows": rows, "toward_count": sum(r["toward"] for r in rows), "n_slices": len(rows)}
# (3) printed chi2/n strings
texts = {}
for stem in ("MEFHC_5iter_xsec_paper_pt_slices", "MEFHC_5iter_xsec_paper_pz_slices"):
    f = sorted(glob.glob(f"{a.captures}/**/{stem}.pdf.texts", recursive=True))
    texts[stem] = ([re.sub(r"\s+", " ", t) for _, t in json.load(open(f[-1]))["texts"] if "chi^2/n" in t] if f else None)
out = {"xsec": a.xsec, "pt_edges": pt_edges, "flux_source": flux_src, "n_reported": n, "modes": modes,
       "modes_share_gt_half": [m["panel"] for m in modes if m["share_pz_ge_20"] > 0.5],
       "pt_slices": slices("pt"), "pz_slices": slices("pz"), "printed_panel_chi2": texts}
json.dump(out, open(a.out, "w"), indent=1)
print(json.dumps({"modes_share_gt_half": out["modes_share_gt_half"], "pt_toward": out["pt_slices"]["toward_count"],
                  "pz_toward": out["pz_slices"]["toward_count"]}))
