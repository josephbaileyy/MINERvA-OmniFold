#!/usr/bin/env python3
"""Bin-identical FULL-COVARIANCE comparison to MINERvA's low-recoil measurement
(Ascencio et al., arXiv:2110.13372, PRD 106 032001) -- closing OPEN_ITEMS #1.

The published supplemental data (Tables II+III: 44-cell d^2sigma/(dEavail dq3)
+ full covariance) ships INSIDE the public arXiv source tarball
(supplementalMELowRecoilData.txt; copied to
3d-unfolding/genie/ascencio_2110.13372_supplemental.txt).

Method
  * Their grid: 6 q3 columns x region-dependent Eavail bins (44 cells),
    phase space theta<20deg, 1.5<p_mu<20 GeV, q3<1.2 GeV.
  * Our side: frozen 4D product d^4sigma/(dpT dpz dEavail dq3) + the ADOPTED
    combined 4D covariance (unified-throw), marginalised over (pT, pz) with
    pz < 20 GeV to mirror their muon gate (reported cells already carry the
    theta<20 selection).
  * Common super-grid: q3 super-bins {0-0.2, 0.2-0.4, 0.4-0.6, 0.6-1.2}
    (exact merges of both sides); per q3 column, Eavail super-bins between
    edges PRESENT IN BOTH binnings and fully tiled by both. Both cross
    sections and covariances are pushed through the same linear merge maps.
  * chi2 = D^T (C_ours + C_theirs)^-1 D on the super-grid. CAVEATS (quote with
    the number): (i) the two measurements share MINERvA flux/detector
    systematics, which this treats as independent (correlations ignored ->
    indicative, not rigorous); (ii) p_mu-vs-p_z gate mismatch at the 20 GeV
    boundary (<~6% kinematic smearing on one edge bin); (iii) different
    fiducial nucleon counts and flux files enter each normalisation.

Run from nd-unfolding/ after `source ../setup_salloc_env.sh`:
  python compare_ascencio_fullcov.py
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import os
import re
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SUPP = f"{_REPO}/3d-unfolding/genie/ascencio_2110.13372_supplemental.txt"
PZ_MU_MAX = 20.0   # their muon momentum cut (GeV); our pz edge aligns exactly
Q3_SUPER = [0.0, 0.2, 0.4, 0.6, 1.2]


def parse_supplemental(path):
    """Tables II+III -> (cells [(ea_lo,ea_hi,q3_lo,q3_hi)], xsec[44], cov[44,44])."""
    txt = open(path).read()
    t2 = txt.split("Table II")[1].split("Table III")[0]
    pat = re.compile(r"^\s*(\d+)\s+Eavail:\s*\[([\d.]+)\s*-\s*([\d.]+)\),\s*"
                     r"q3:\s*\[([\d.]+)\s*-\s*([\d.]+)\),\s*cross section:\s*([\d.eE+-]+)",
                     re.M)
    cells, xs = [], []
    for m in pat.finditer(t2):
        idx, ea_lo, ea_hi, q3_lo, q3_hi, x = m.groups()
        assert int(idx) == len(cells), f"non-contiguous index {idx}"
        cells.append((float(ea_lo), float(ea_hi), float(q3_lo), float(q3_hi)))
        xs.append(float(x))
    xs = np.asarray(xs)
    t3 = txt.split("Table III")[1]
    rows = [list(map(float, ln.split())) for ln in t3.splitlines()
            if re.match(r"^\s*[\d-]", ln) and len(ln.split()) == len(cells)]
    cov = np.asarray(rows)
    assert cov.shape == (len(cells), len(cells)), f"cov shape {cov.shape}"
    asym = np.abs(cov - cov.T).max() / np.abs(cov).max()
    print(f"[asc] parsed {len(cells)} cells; cov asymmetry {asym:.1e}")
    return cells, xs, cov


def load_ours():
    """Frozen 4D xsec + adopted combined covariance -> (x4 flat, gmask, edges, C4830)."""
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    import unfold_2d_omnifold_unbinned as u2d
    import unfold_nd_omnifold_unbinned as und
    pt_e = np.asarray(u2d.PT_EDGES, float)
    pz_e = np.asarray(u2d.PZ_EDGES, float)
    ea_e = np.asarray(und.EXTRA_AXES["eavail"]["edges"], float)
    q3_e = np.asarray(und.EXTRA_AXES["q3"]["edges"], float)
    f = ROOT.TFile.Open(f"{_REPO}/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    hf = f.Get("hXSecND_flat")
    x4 = np.array([hf.GetBinContent(i + 1) for i in range(hf.GetNbinsX())])
    f.Close()
    gmask = np.where(x4 > 0)[0]
    fc = ROOT.TFile.Open(f"{_REPO}/nd-unfolding/uq_4d/universe_stage2_4d/"
                         "uq_universe_4d_covariance_combined_uthrow.root")
    h = fc.Get("hCov_combined4d_total_uthrow")
    n = h.GetNbinsX()
    assert n == gmask.size, f"cov dim {n} != reported {gmask.size}"
    C = np.frombuffer(h.GetArray(), dtype=np.float64,
                      count=(n + 2) * (n + 2)).reshape(n + 2, n + 2)[1:n+1, 1:n+1].T.copy()
    fc.Close()
    return x4, gmask, (pt_e, pz_e, ea_e, q3_e), C


def common_eavail_edges(theirs_col_edges, ours_edges, ea_max):
    """Edges present in BOTH binnings (within their coverage), incl. 0 and ea_max."""
    o = set(np.round(ours_edges, 6))
    t = set(np.round(theirs_col_edges, 6))
    com = sorted(e for e in (o & t) if e <= ea_max + 1e-9)
    return com


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-png", default="products/4d/ascencio_fullcov_compare.png")
    args = ap.parse_args()

    cells, x_a, C_a = parse_supplemental(SUPP)
    x4, gmask, (pt_e, pz_e, ea_e, q3_e), C_o = load_ours()
    sh4 = (len(pt_e) - 1, len(pz_e) - 1, len(ea_e) - 1, len(q3_e) - 1)
    ip, iz, ie, iq = np.unravel_index(gmask, sh4)
    dpt, dpz = np.diff(pt_e), np.diff(pz_e)

    # ---- build the common super-grid ----
    super_bins = []   # (q3_lo, q3_hi, ea_lo, ea_hi)
    for qlo, qhi in zip(Q3_SUPER[:-1], Q3_SUPER[1:]):
        col = [(c, i) for i, c in enumerate(cells)
               if c[2] >= qlo - 1e-9 and c[3] <= qhi + 1e-9]
        col_edges = sorted({c[0] for c, _ in col} | {c[1] for c, _ in col})
        ea_max = max(c[1] for c, _ in col)
        com = common_eavail_edges(col_edges, ea_e, ea_max)
        fine_q3 = sorted({(c[2], c[3]) for c, _ in col})
        for elo, ehi in zip(com[:-1], com[1:]):
            # require EVERY fine q3 sub-column of theirs, and our binning, to
            # tile [elo, ehi] exactly
            ok = all(
                abs(sum((c[1] - c[0]) for c, _ in col
                        if (c[2], c[3]) == fq
                        and c[0] >= elo - 1e-9 and c[1] <= ehi + 1e-9)
                    - (ehi - elo)) < 1e-6
                for fq in fine_q3)
            our_w = sum(ea_e[k+1] - ea_e[k] for k in range(len(ea_e) - 1)
                        if ea_e[k] >= elo - 1e-9 and ea_e[k+1] <= ehi + 1e-9)
            if ok and abs(our_w - (ehi - elo)) < 1e-6:
                super_bins.append((qlo, qhi, elo, ehi))
    ns = len(super_bins)
    print(f"[grid] {ns} common super-bins:")
    for qlo, qhi, elo, ehi in super_bins:
        print(f"   q3 [{qlo},{qhi})  Eavail [{elo},{ehi})")

    # ---- merge matrices ----
    # theirs: T[s, j] = dEa_j*dq3_j / (dEa_s*dq3_s) for cell j inside super-bin s
    T = np.zeros((ns, len(cells)))
    for s, (qlo, qhi, elo, ehi) in enumerate(super_bins):
        vol_s = (ehi - elo) * (qhi - qlo)
        for j, (alo, ahi, blo, bhi) in enumerate(cells):
            if alo >= elo - 1e-9 and ahi <= ehi + 1e-9 and blo >= qlo - 1e-9 and bhi <= qhi + 1e-9:
                T[s, j] = (ahi - alo) * (bhi - blo) / vol_s
    # ours: O[s, r] over reported 4D cells r: dpt*dpz*dEa*dq3 / (dEa_s*dq3_s),
    # restricted to pz_hi <= PZ_MU_MAX (their muon gate; theta<20 via reported mask)
    O = np.zeros((ns, gmask.size))
    for s, (qlo, qhi, elo, ehi) in enumerate(super_bins):
        vol_s = (ehi - elo) * (qhi - qlo)
        sel = ((ea_e[ie] >= elo - 1e-9) & (ea_e[ie + 1] <= ehi + 1e-9) &
               (q3_e[iq] >= qlo - 1e-9) & (q3_e[iq + 1] <= qhi + 1e-9) &
               (pz_e[iz + 1] <= PZ_MU_MAX + 1e-9))
        O[s, sel] = (dpt[ip] * dpz[iz] * np.diff(ea_e)[ie] * np.diff(q3_e)[iq])[sel] / vol_s

    y_o = O @ x4[gmask]
    y_a = T @ x_a
    Cs_o = O @ C_o @ O.T
    Cs_a = T @ C_a @ T.T

    print(f"\n[cmp] {'q3':14s} {'Eavail':14s} {'ours':>11s} {'Ascencio':>11s} "
          f"{'ratio':>7s} {'pull':>7s}")
    D = y_o - y_a
    sig = np.sqrt(np.diag(Cs_o) + np.diag(Cs_a))
    for s, (qlo, qhi, elo, ehi) in enumerate(super_bins):
        print(f"[cmp] [{qlo},{qhi}) GeV  [{elo},{ehi}) GeV {y_o[s]:11.4g} {y_a[s]:11.4g} "
              f"{y_o[s]/y_a[s]:7.3f} {D[s]/sig[s]:7.2f}")
    wid = np.array([(ehi - elo) * (qhi - qlo) for qlo, qhi, elo, ehi in super_bins])
    print(f"[cmp] integrated (common region): ours {np.sum(y_o*wid):.4g} "
          f"vs Ascencio {np.sum(y_a*wid):.4g}  ratio {np.sum(y_o*wid)/np.sum(y_a*wid):.4f}")

    C_tot = Cs_o + Cs_a
    chi2 = float(D @ np.linalg.solve(C_tot, D))
    from scipy import stats
    p = stats.chi2.sf(chi2, ns)
    chi2_diag = float(np.sum(D**2 / np.diag(C_tot)))
    print(f"\n[chi2] full-cov chi2/ndf = {chi2:.2f}/{ns} (p = {p:.3g}); "
          f"diag-only {chi2_diag:.2f}/{ns}")
    print("[chi2] caveats: shared MINERvA flux/detector systematics treated as "
          "independent; p_mu~p_z gate approximation at 20 GeV; independent "
          "normalisation inputs.")

    # ---- overlay figure ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cols = [(qlo, qhi) for qlo, qhi in zip(Q3_SUPER[:-1], Q3_SUPER[1:])
            if any(b[0] == qlo for b in super_bins)]
    ncol = len(cols)
    fig, axs = plt.subplots(1, ncol, figsize=(4.6 * ncol, 4.2), sharey=False,
                            squeeze=False)
    axs = axs[0]
    for c, (qlo, qhi) in enumerate(cols):
        idx = [s for s, b in enumerate(super_bins) if b[0] == qlo]
        e = sorted({super_bins[s][2] for s in idx} | {super_bins[s][3] for s in idx})
        ctr = [0.5 * (super_bins[s][2] + super_bins[s][3]) for s in idx]
        we = [0.5 * (super_bins[s][3] - super_bins[s][2]) for s in idx]
        A = axs[c]
        A.errorbar(ctr, [y_o[s] for s in idx], xerr=we,
                   yerr=[np.sqrt(Cs_o[s, s]) for s in idx],
                   fmt="ko", label="this work (4D marginal, $p_z<20$)")
        A.errorbar(ctr, [y_a[s] for s in idx], xerr=we,
                   yerr=[np.sqrt(Cs_a[s, s]) for s in idx],
                   fmt="rs", mfc="none", label="Ascencio et al.")
        A.set_title(f"$q_3 \\in [{qlo},{qhi})$ GeV")
        A.set_xlabel(r"$E_{\rm avail}$ (GeV)")
        if c == 0:
            A.set_ylabel(r"$d^2\sigma/(dE_{\rm avail}\,dq_3)$ (cm$^2$/GeV$^2$/nucleon)")
            A.legend(fontsize=8)
    fig.suptitle("Bin-identical comparison on the common super-grid "
                 f"(full-cov $\\chi^2$/ndf = {chi2:.1f}/{ns}, p = {p:.2g})")
    technote_style.minerva_tag(axs[0])
    os.makedirs(os.path.dirname(args.out_png), exist_ok=True)
    fig.savefig(args.out_png, dpi=140, bbox_inches="tight")
    print(f"[cmp] wrote {args.out_png}")


if __name__ == "__main__":
    main()
