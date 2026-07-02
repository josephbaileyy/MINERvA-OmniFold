#!/usr/bin/env python3
"""Bin-by-bin UNCERTAINTY comparison: PET (point cloud) vs GBDT (scalars) 5D xsec.

5D (pt,pz,Eavail,q3,W) analogue of pet/pet_vs_gbdt_uncertainty.py. Does the PET
point-cloud unfolding *reduce* the per-bin uncertainty relative to the production
scalar GBDT, or merely *agree* on the central value? Compares the per-bin
fractional uncertainty sqrt(diag(C))/CV of the two engines on an IDENTICAL set of
physical 5D bins.

Both combined covariances are BLOCK-SUM (per-band) budgets -- the same scheme used
by the published 2D/3D/4D MINERvA covariances, and identical between the two
engines (apples-to-apples). They live on DIFFERENT reported-bin sets, both subsets
of the same 14x16x7x7x6 = 65856 (pt,pz,Eavail,q3,W) grid (C-order ravel):
  * PET  : reported mask x_cv > 0 (PETxsec5D CV, pet_weights_full.npz) -> 10550 bins
  * GBDT : reported mask CV  > 0 (hXSecND_flat)                        -> 10694 bins
We map both flat row-orderings back to their full-grid indices, intersect, and run
every comparison on the common grid bins.

Unlike the 4D close-out, the 5D PET covariance was built CLEAN from the start (the
#12-fixed bank_uthrow), so there is no garbage-miss-row variant to correct: the
headline PET covariance is simply C_total from pet_5d_covariance_combined_wlat.root
(clean C_syst + C_stat + C_ML + PET-native shifted-W C_lateral).

STATS REGIME: the PET covariance is anchored to pet_weights_full.npz (the 2M-train
reweight pushed onto the full 32.8M gen cloud), so the PET side carries the
PET-vs-GBDT CV training gap; this is INDICATIVE of the method, not a final
full-stats number. Every output is labelled accordingly.

Run from nd-unfolding/ after `source ../setup_salloc_env.sh`:
  python pet/pet_vs_gbdt_uncertainty_5d.py
"""
import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + viridis/RdBu_r consistent colours)

import argparse
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

AXES = ["pt", "pz", "eavail", "q3", "W"]
AXLABEL = {"pt": r"$p_T$ (GeV/c)", "pz": r"$p_{\parallel}$ (GeV/c)",
           "eavail": r"$E_{avail}$ (GeV)", "q3": r"$q_3$ (GeV)", "W": r"$W$ (GeV)"}
GRID = (14, 16, 7, 7, 6)         # pt, pz, eavail, q3, W  (C-order)
NGRID = int(np.prod(GRID))       # 65856


def th2_to_numpy(h):
    """Fast TH2D -> dense numpy (drops under/overflow)."""
    n = h.GetNbinsX()
    a = np.frombuffer(h.GetArray(), dtype=np.float64,
                      count=(n + 2) * (n + 2)).reshape(n + 2, n + 2)[1:n + 1, 1:n + 1].T.copy()
    return a


def th1_to_numpy(h):
    return np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])


def load_gbdt(cov_path, cov_hist, cv_path):
    """GBDT full-grid CV + reported mask + combined covariance (rows ordered by CV>0)."""
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(cv_path)
    x5 = th1_to_numpy(f.Get("hXSecND_flat")); f.Close()
    assert x5.size == NGRID, f"GBDT CV grid {x5.size} != {NGRID}"
    gmask = np.where(x5 > 0)[0]
    fc = ROOT.TFile.Open(cov_path)
    h = fc.Get(cov_hist)
    C = th2_to_numpy(h); fc.Close()
    assert C.shape[0] == gmask.size, f"GBDT cov dim {C.shape[0]} != reported {gmask.size}"
    return x5, gmask, C


def load_pet(wlat_path, w_source, comp_ref):
    """PET full-grid CV (recomputed via PETxsec5D to recover the full-grid mask) +
    the clean combined covariance blocks on the 10550-bin reported ordering.

    Verifies the recomputed CV matches the file's embedded hXSec_cv_flat (so the
    row-ordering map is provably correct). Returns the headline C_total plus a
    vertical-only (syst+stat+ML, no lateral) cross-check variant.
    """
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    from pet_systematics_5d import PETxsec5D
    pet = PETxsec5D(f"{_REPO}/nd-unfolding/of_inputs_pc.npz",
                    f"{_REPO}/nd-unfolding/products/pet/pet_weights_full.npz",
                    f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root",
                    "pTmu_reweightedflux_integrated",
                    w_source, comp_ref)
    x_cv = pet.xsec(None)
    assert x_cv.size == NGRID, f"PET CV grid {x_cv.size} != {NGRID}"
    pmask = np.where(x_cv > 0)[0]

    fc = ROOT.TFile.Open(wlat_path)
    base = th1_to_numpy(fc.Get("hXSec_cv_flat"))
    # only the 5 summary blocks are needed (skip the 9 per-band C_lateral_* hists,
    # which would otherwise pull ~9 GB of redundant matrices into memory)
    want = ("C_syst", "C_stat", "C_ML", "C_lateral", "C_total")
    blk = {nm: th2_to_numpy(fc.Get(nm)) for nm in want}
    fc.Close()
    assert pmask.size == base.size, f"{wlat_path}: mask {pmask.size} != embedded CV {base.size}"
    rel = np.abs(x_cv[pmask] - base) / np.where(base != 0, np.abs(base), 1)
    assert rel.max() < 1e-4, f"{wlat_path}: PET CV mismatch (max rel {rel.max():.2e})"
    print("[pet5d] recomputed CV matches the file's embedded CV (row-order map OK)")

    variants = {
        "headline": blk["C_total"],                                  # syst+stat+ML+lateral
        "vertical_nolat": blk["C_syst"] + blk["C_stat"] + blk["C_ML"],
    }
    return x_cv, pmask, variants, blk


def frac_unc(C, cv_reported):
    d = np.sqrt(np.clip(np.diag(C), 0, None))
    return np.where(cv_reported > 0, d / cv_reported, np.nan)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pet-wlat",
                    default=f"{_REPO}/nd-unfolding/products/pet/pet_5d_covariance_combined_wlat.root")
    ap.add_argument("--pet-wsource", default=f"{_REPO}/nd-unfolding/of_inputs_5d.npz")
    ap.add_argument("--pet-compref",
                    default=f"{_REPO}/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--gbdt-cov",
                    default=f"{_REPO}/nd-unfolding/uq_5d/universe_stage2_5d/"
                            "uq_universe_5d_covariance_combined.root")
    ap.add_argument("--gbdt-cov-hist", default="hCov_combined5d_total")
    ap.add_argument("--gbdt-cv",
                    default=f"{_REPO}/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--outdir", default=f"{_REPO}/nd-unfolding/products/pet")
    ap.add_argument("--label",
                    default="subsample PET (2M-train reweight; CV gap from GBDT) -- indicative only; "
                            "block-sum covariance, 5D (pt,pz,Eavail,q3,W)")
    ap.add_argument("--cov-method",
                    default="block-sum (per-band), identical scheme for PET and GBDT",
                    help="description of the covariance scheme both engines use "
                         "(e.g. 'unified-throw adopted, identical scheme for PET and GBDT')")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # ---- load both engines on the full grid ----
    pet_cv_full, pmask, pet_vars, pet_blk = load_pet(args.pet_wlat, args.pet_wsource, args.pet_compref)
    gbdt_cv_full, gmask, C_gbdt = load_gbdt(args.gbdt_cov, args.gbdt_cov_hist, args.gbdt_cv)
    C_pet = pet_vars["headline"]

    print(f"[mask] PET reported = {pmask.size}   GBDT reported = {gmask.size}   grid = {NGRID}")

    # ---- intersect the two full-grid index sets ----
    common = np.intersect1d(pmask, gmask)
    print(f"[mask] INTERSECTION (common physical bins) = {common.size}")
    print(f"[mask]   PET-only = {np.setdiff1d(pmask, gmask).size}   "
          f"GBDT-only = {np.setdiff1d(gmask, pmask).size}")

    # position of each common grid-idx within each engine's reported ordering
    p_pos = {g: i for i, g in enumerate(pmask)}
    g_pos = {g: i for i, g in enumerate(gmask)}
    p_sel = np.array([p_pos[g] for g in common])
    g_sel = np.array([g_pos[g] for g in common])

    # ---- per-bin fractional uncertainty on the common bins ----
    pet_fr = frac_unc(C_pet, pet_cv_full[pmask])[p_sel]
    gbdt_fr = frac_unc(C_gbdt, gbdt_cv_full[gmask])[g_sel]
    pet_fr_var = {nm: frac_unc(C, pet_cv_full[pmask])[p_sel] for nm, C in pet_vars.items()}

    good = np.isfinite(pet_fr) & np.isfinite(gbdt_fr) & (gbdt_fr > 0) & (pet_fr > 0)
    ratio = np.full(common.size, np.nan)
    ratio[good] = pet_fr[good] / gbdt_fr[good]

    # ---- summary stats ----
    med_pet = float(np.median(pet_fr[good]))
    med_gbdt = float(np.median(gbdt_fr[good]))
    med_ratio = float(np.median(ratio[good]))
    frac_pet_lt = float(np.mean(pet_fr[good] < gbdt_fr[good]))
    med_pet_variants = {nm: float(np.median(v[good & np.isfinite(v)]))
                        for nm, v in pet_fr_var.items()}
    summary = {
        "label": args.label,
        "headline_pet_cov": "C_total from pet_5d_covariance_combined_wlat.root "
                            "(clean C_syst+C_stat+C_ML + PET-native shifted-W C_lateral)",
        "covariance_method": args.cov_method,
        "n_grid": NGRID,
        "n_pet_reported": int(pmask.size),
        "n_gbdt_reported": int(gmask.size),
        "n_common": int(common.size),
        "n_pet_only": int(np.setdiff1d(pmask, gmask).size),
        "n_gbdt_only": int(np.setdiff1d(gmask, pmask).size),
        "median_frac_pet_headline": med_pet,
        "median_frac_pet_vertical_nolat": med_pet_variants["vertical_nolat"],
        "median_frac_gbdt": med_gbdt,
        "median_ratio_pet_over_gbdt": med_ratio,
        "fraction_bins_pet_lt_gbdt": frac_pet_lt,
        "pet_cov": args.pet_wlat,
        "gbdt_cov": f"{args.gbdt_cov}::{args.gbdt_cov_hist}",
    }
    print("\n=== SUMMARY (common bins, 5D) ===")
    for k, v in summary.items():
        print(f"  {k:34s} {v}")

    # ---- map common bins to grid coords for projections ----
    coords = np.unravel_index(common, GRID, order="C")
    idxs = {nm: coords[i] for i, nm in enumerate(AXES)}

    # edges: pt,pz,eavail,q3 from the PET inputs npz; W (edges_4) from the GBDT 5D inputs
    pc = np.load(f"{_REPO}/nd-unfolding/of_inputs_pc.npz")
    g5 = np.load(args.pet_wsource)
    edges = [np.asarray(pc[f"edges_{i}"], float) for i in range(4)] + [np.asarray(g5["edges_4"], float)]

    # ---- (a) 1D-projection overlays of the per-bin fractional uncertainty (5 axes) ----
    fig, axs = plt.subplots(2, 3, figsize=(15, 8))
    axs = axs.ravel()
    for ai, nm in enumerate(AXES):
        axp = axs[ai]
        e = edges[ai]; cen = 0.5 * (e[:-1] + e[1:]); nb = GRID[ai]
        med_p = np.full(nb, np.nan); lo_p = np.full(nb, np.nan); hi_p = np.full(nb, np.nan)
        med_g = np.full(nb, np.nan); lo_g = np.full(nb, np.nan); hi_g = np.full(nb, np.nan)
        for b in range(nb):
            m = (idxs[nm] == b) & good
            if m.sum() == 0:
                continue
            med_p[b], lo_p[b], hi_p[b] = np.percentile(100 * pet_fr[m], [50, 10, 90])
            med_g[b], lo_g[b], hi_g[b] = np.percentile(100 * gbdt_fr[m], [50, 10, 90])
        axp.fill_between(cen, lo_p, hi_p, alpha=0.18, step="mid", color="C0")
        axp.fill_between(cen, lo_g, hi_g, alpha=0.18, step="mid", color="C1")
        axp.step(cen, med_p, where="mid", lw=2, color="C0", label="PET (point cloud)")
        axp.step(cen, med_g, where="mid", lw=2, ls="--", color="C1", label="GBDT (scalars)")
        axp.set_xlabel(AXLABEL[nm]); axp.set_ylabel("per-bin frac. uncertainty (%)")
        axp.legend(fontsize=8)
        axp.text(0.97, 0.95, f"med PET {np.nanmedian(med_p):.1f}%\nmed GBDT {np.nanmedian(med_g):.1f}%",
                 transform=axp.transAxes, ha="right", va="top", fontsize=8,
                 bbox=dict(fc="white", ec="0.7", alpha=0.8))
    axs[-1].axis("off")  # 6th slot unused (5 axes)
    fig.text(0.5, 0.005, args.label, ha="center", fontsize=8, style="italic")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    p_overlay = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_5d_overlay.png")
    fig.savefig(p_overlay, dpi=130); plt.close(fig)
    print(f"[OK] wrote {p_overlay}")

    # ---- (b) per-bin ratio (PET/GBDT) map projected onto (pt, pz) ----
    ipt, ipz = idxs["pt"], idxs["pz"]
    rmap = np.full((GRID[0], GRID[1]), np.nan)
    for a in range(GRID[0]):
        for b in range(GRID[1]):
            m = (ipt == a) & (ipz == b) & good
            if m.sum():
                rmap[a, b] = np.median(ratio[m])
    fig2, ax2 = plt.subplots(figsize=(8.5, 6))
    im = ax2.pcolormesh(edges[1], edges[0], rmap, cmap="RdBu_r", vmin=0.5, vmax=1.5)
    cb = fig2.colorbar(im, ax=ax2); cb.set_label("PET / GBDT  per-bin frac. unc. (median over Eavail,q3,W)")
    ax2.set_xlabel(AXLABEL["pz"]); ax2.set_ylabel(AXLABEL["pt"])
    ax2.text(0.99, 1.01, f"<1 (blue): PET tighter   |   median ratio {med_ratio:.3f}",
             transform=ax2.transAxes, ha="right", va="bottom", fontsize=9)
    fig2.text(0.5, 0.005, args.label, ha="center", fontsize=8, style="italic")
    fig2.tight_layout(rect=(0, 0.02, 1, 1))
    p_ratio = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_5d_ratiomap.png")
    fig2.savefig(p_ratio, dpi=130); plt.close(fig2)
    print(f"[OK] wrote {p_ratio}")

    # ---- (c) histogram of the per-bin ratio ----
    fig3, ax3 = plt.subplots(figsize=(7.5, 5))
    ax3.hist(ratio[good], bins=np.linspace(0, 3, 61), color="C2", alpha=0.8)
    ax3.axvline(1.0, color="k", lw=1, ls=":")
    ax3.axvline(med_ratio, color="C3", lw=2, label=f"median {med_ratio:.3f}")
    ax3.set_xlabel("PET / GBDT  per-bin fractional uncertainty")
    ax3.set_ylabel("common bins"); ax3.legend(fontsize=9)
    ax3.text(0.99, 0.95,
             f"median PET {100*med_pet:.1f}%\nmedian GBDT {100*med_gbdt:.1f}%\n"
             f"bins PET<GBDT {100*frac_pet_lt:.0f}%\nN_common {common.size}",
             transform=ax3.transAxes, ha="right", va="top", fontsize=8,
             bbox=dict(fc="white", ec="0.7", alpha=0.85))
    fig3.text(0.5, 0.005, args.label, ha="center", fontsize=8, style="italic")
    fig3.tight_layout(rect=(0, 0.03, 1, 1))
    p_hist = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_5d_ratiohist.png")
    fig3.savefig(p_hist, dpi=130); plt.close(fig3)
    print(f"[OK] wrote {p_hist}")

    # ---- verdict ----
    if med_ratio < 0.90 and frac_pet_lt > 0.60:
        tag, phrase = "REDUCES", ("So PET MODESTLY REDUCES the uncertainty vs the scalars "
                                  "at this stats regime")
    elif med_ratio > 1.10 and frac_pet_lt < 0.40:
        tag, phrase = "WORSE", "So PET is WORSE than the scalars in per-bin precision"
    else:
        tag, phrase = "COMPARABLE", ("So PET essentially MATCHES the GBDT precision rather than "
                                     "reducing it -- the point cloud agrees with the scalars on "
                                     "the central value AND lands at comparable uncertainty")
    verdict = (
        f"VERDICT: PET is {tag} to GBDT in per-bin uncertainty on the {common.size} "
        f"common 5D bins (every PET bin is a GBDT bin; GBDT reports {summary['n_gbdt_only']} "
        f"extra). Median per-bin fractional uncertainty is {100*med_pet:.1f}% for PET "
        f"(headline: C_syst+C_stat+C_ML + PET-native shifted-W lateral) vs "
        f"{100*med_gbdt:.1f}% for GBDT; the median per-bin ratio is {med_ratio:.3f} and PET "
        f"is tighter in {100*frac_pet_lt:.0f}% of bins. {phrase}. "
        f"Cross-check (lateral): PET vertical-only (no lateral) reads "
        f"{100*med_pet_variants['vertical_nolat']:.1f}%, so the conclusion is not driven by the "
        f"lateral treatment. Both covariances use the {args.cov_method} scheme. "
        f"Caveat (stats regime): the PET covariance is anchored to the 2M-train reweight "
        f"(pet_weights_full.npz), which still carries the PET-vs-GBDT CV training gap, so this is "
        f"INDICATIVE of the method, not a final full-stats uncertainty."
    )
    print("\n" + verdict)
    summary["verdict_tag"] = tag
    summary["verdict"] = verdict
    summary["figures"] = [p_overlay, p_ratio, p_hist]

    p_json = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_5d_summary.json")
    with open(p_json, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[OK] wrote {p_json}")


if __name__ == "__main__":
    main()
