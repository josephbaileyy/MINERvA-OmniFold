#!/usr/bin/env python3
"""Ascencio 2110.13372 bin-identical comparison on their FULL 44-cell fine grid
(OPEN_ITEMS item 2, stage 1).

Uses the dedicated re-unfold on the union of their edges
(products/4d/xsec_4d_MEFHC_ascencio_fine.root, job 54351853): their
per-q3-column E_avail binnings tile the rectangular union grid exactly, so
every one of their 44 cells is an exact width-weighted merge of our fine
cells. The (pT,pz) marginal is restricted to pz < 20 GeV to mirror their muon
gate (theta < 20 deg is shared by construction).

Chi^2 here uses THEIR covariance only (CV-level): our statistical/systematic
errors on this binning are not yet available (stage 2 = a 187-universe sweep
on the fine binning), so the quoted chi^2 OVERSTATES tension -- it is an
upper bound. Shared-systematics caveat as in compare_ascencio_fullcov.py.

  python compare_ascencio_fine.py   # writes products/4d/ascencio_fine_compare.png
"""
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import unfold_2d_omnifold_unbinned as u2d
from compare_ascencio_fullcov import parse_supplemental, SUPP

EA_FINE = [0.0, 0.04, 0.08, 0.12, 0.16, 0.24, 0.32, 0.34, 0.4, 0.6, 0.8, 1.0, 1.2, 100.0]
Q3_FINE = [0.0, 0.2, 0.3, 0.4, 0.6, 0.9, 1.2, 100.0]
PZ_MU_MAX = 20.0
PROD = "products/4d/xsec_4d_MEFHC_ascencio_fine.root"


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError

    cells, x_a, C_a = parse_supplemental(SUPP)

    f = ROOT.TFile.Open(PROD)
    h = f.Get("hXSecND_flat")
    flat = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    f.Close()
    pt_e = np.asarray(u2d.PT_EDGES, float)
    pz_e = np.asarray(u2d.PZ_EDGES, float)
    ea_e = np.asarray(EA_FINE)
    q3_e = np.asarray(Q3_FINE)
    x4 = flat.reshape(len(pt_e) - 1, len(pz_e) - 1, len(ea_e) - 1, len(q3_e) - 1, order="C")

    # (ea, q3) density with the pz<20 muon gate: integrate pt fully, pz bins
    # with upper edge <= 20 (an exact edge of the paper grid)
    jz = np.where(pz_e[1:] <= PZ_MU_MAX + 1e-9)[0]
    wpt = np.diff(pt_e)[:, None, None, None]
    wpz = np.diff(pz_e)[None, :, None, None]
    dens = (x4 * wpt * wpz)[:, jz].sum(axis=(0, 1))     # (n_ea, n_q3) density in (ea,q3)

    # merge our fine cells into their 44
    ours = np.zeros(len(cells))
    for k, (elo, ehi, qlo, qhi) in enumerate(cells):
        jq = np.where((q3_e[:-1] >= qlo - 1e-9) & (q3_e[1:] <= qhi + 1e-9))[0]
        ie = np.where((ea_e[:-1] >= elo - 1e-9) & (ea_e[1:] <= ehi + 1e-9))[0]
        assert jq.size and ie.size, f"cell {k} not tiled"
        w_ea = np.diff(ea_e)[ie]
        w_q3 = np.diff(q3_e)[jq]
        assert abs(w_ea.sum() - (ehi - elo)) < 1e-9 and abs(w_q3.sum() - (qhi - qlo)) < 1e-9, \
            f"cell {k} tiling gap"
        num = (dens[np.ix_(ie, jq)] * w_ea[:, None] * w_q3[None, :]).sum()
        ours[k] = num / ((ehi - elo) * (qhi - qlo))

    sig_a = np.sqrt(np.clip(np.diag(C_a), 0, None))
    ok = (x_a > 0) & (ours > 0)
    r = ours[ok] / x_a[ok]
    pulls = (ours - x_a) / np.where(sig_a > 0, sig_a, np.inf)
    print(f"[fine] {ok.sum()}/44 cells compared (pz<{PZ_MU_MAX:g} gate)")
    print(f"[fine] ours/theirs: median={np.median(r):.3f}  mean={r.mean():.3f}  "
          f"range [{r.min():.2f}, {r.max():.2f}]")
    print(f"[fine] pulls (THEIR cov only): median={np.median(pulls[ok]):.2f}  "
          f"|pull|>2: {(np.abs(pulls[ok])>2).sum()}/{ok.sum()}")
    d = (ours - x_a)[ok]
    Cred = C_a[np.ix_(ok, ok)]
    chi2 = float(d @ np.linalg.solve(Cred, d))
    ndf = int(ok.sum())
    from scipy.stats import chi2 as chi2dist
    p = float(chi2dist.sf(chi2, ndf))
    print(f"[fine] chi2/ndf (their cov ONLY -- upper bound on tension) = "
          f"{chi2:.1f}/{ndf}  (p = {p:.3g})")
    diag_chi2 = float((d**2 / np.diag(Cred)).sum())
    print(f"[fine] diag-only chi2/ndf = {diag_chi2:.1f}/{ndf}")
    worst = np.argsort(-np.abs(pulls))[:5]
    for k in worst:
        elo, ehi, qlo, qhi = cells[k]
        print(f"  worst: Ea[{elo:g},{ehi:g}) q3[{qlo:g},{qhi:g})  "
              f"ours={ours[k]:.3e} theirs={x_a[k]:.3e}  pull={pulls[k]:+.2f}")

    # figure: per-q3-column Eavail panels
    q3cols = sorted({(qlo, qhi) for _, _, qlo, qhi in cells})
    fig, axs = plt.subplots(2, 3, figsize=(15, 8), sharex=False)
    for ax, (qlo, qhi) in zip(axs.ravel(), q3cols):
        ks = [k for k, (_, _, ql, qh) in enumerate(cells) if (ql, qh) == (qlo, qhi)]
        e = sorted({cells[k][0] for k in ks} | {cells[k][1] for k in ks})
        ctr = [0.5 * (cells[k][0] + cells[k][1]) for k in ks]
        wid = [0.5 * (cells[k][1] - cells[k][0]) for k in ks]
        ax.errorbar(ctr, [x_a[k] for k in ks], xerr=wid,
                    yerr=[sig_a[k] for k in ks], fmt="o", ms=3,
                    color="tab:blue", label="Ascencio (their cov)")
        ax.stairs([ours[k] for k in ks], e, color="tab:red", lw=2, label="ours (fine re-unfold)")
        ax.set_title(rf"$q_3 \in [{qlo:g}, {qhi:g})$ GeV")
        ax.set_xlabel(r"$E_{avail}$ (GeV)")
        ax.set_ylabel(r"$d^2\sigma/(dE_{avail}\,dq_3)$")
        ax.legend(fontsize=7)
    fig.suptitle(f"Ascencio 44-cell fine-grid comparison (CV level; their-cov-only "
                 f"$\\chi^2$/ndf = {chi2:.1f}/{ndf}, p = {p:.2g})")
    fig.tight_layout()
    out = "products/4d/ascencio_fine_compare.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"[wrote] {out}")


if __name__ == "__main__":
    main()
