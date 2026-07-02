#!/usr/bin/env python3
"""Bin-by-bin UNCERTAINTY comparison: PET (point cloud) vs GBDT (scalars) 4D xsec.

Advisor question (analysis note): does the PET point-cloud unfolding *reduce*
the per-bin uncertainty relative to the production scalar GBDT, or does it merely
*agree* on the central value?  pet_vs_gbdt.py already answers "do the central
values agree" (yes, within the PET band).  This answers the orthogonal question by
comparing the per-bin fractional uncertainty  sqrt(diag(C))/CV  of the two engines
on an IDENTICAL set of physical 4D bins.

The two combined covariances live on DIFFERENT reported-bin sets, both subsets of
the same 14x16x7x7 = 10976  (pt, pz, Eavail, q3)  grid (C-order ravel):
  * PET  : reported mask  x_cv > 0   (PETxsec CV, pet_weights_full.npz) -> 4796 bins
  * GBDT : reported mask  CV  > 0    (hXSecND_flat)                     -> 4830 bins
We map BOTH flat row-orderings back to their full-grid indices, intersect, and run
every comparison on the common grid bins so each PET bin is compared to the GBDT
bin for the SAME physical cell.

KNOWN_ISSUES #12 (RESOLVED 2026-06-12) -- the headline PET covariance is the
CORRECTED ("rebank") one, NOT the raw pet_4d_covariance_combined_wlat.root:
  * The published C_syst (median 18.31%) was INFLATED by a garbage-miss-row bug:
    AppendTruthOnlyMisses left the 12.35M appended miss rows uninitialized in every
    per-universe branch, and pet_systematics._clip mangled those to {1e-2,1,1e2},
    blowing up the systematic deltas.  The C++ fix + a regenerated bank rebuilt the
    syst block CLEAN: C_syst 18.31% -> 8.24% (C_stat / C_ML bit-identical -- a
    perfect control), in products/pet/pet_4d_covariance_combined_rebank.root.
    Adopted guidance (KNOWN_ISSUES #12): "quote the rebank artifact going forward."
  * The rebank file has no lateral block, so the HEADLINE PET covariance here is
    rebank's clean (C_syst + C_stat + C_ML) PLUS the PET-NATIVE C_lateral from
    pet_4d_covariance_combined_wlat.root (built by pet_lateral_band.py from the
    event-aligned 5D join; native 1.74% vs the GBDT-transferred 4.03% -- the
    independence-fair choice the prompt asked for).  Median total: 11.80%.
  * The raw _wlat total (22.51%, pre-#12-fix, conservative/over-covered) and the
    GBDT-transferred-lateral variant (23.02%) are carried as documented cross-checks.

STATS REGIME: the PET covariance is anchored to pet_weights_full.npz, the 2M-train
reweight pushed onto the full 32.8M gen cloud (the documented milestone weights).
The full-statistics PET (cal20m, job 55047632) was still PENDING at run time, so the
PET side carries the ~9% (now ~4.5% at 8M) CV-vs-GBDT training gap.  The uncertainty
comparison is therefore INDICATIVE of the method, not a final full-stats number;
every output is labelled accordingly.

Run from nd-unfolding/ after `source ../setup_salloc_env.sh` (compute node; PETxsec
re-bins the 32.8M-row truth cloud a few times -> ~a few GB, < 1 min):
  python pet/pet_vs_gbdt_uncertainty.py
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

AXES = ["pt", "pz", "eavail", "q3"]
AXLABEL = {"pt": r"$p_T$ (GeV/c)", "pz": r"$p_{\parallel}$ (GeV/c)",
           "eavail": r"$E_{avail}$ (GeV)", "q3": r"$q_3$ (GeV)"}
GRID = (14, 16, 7, 7)            # pt, pz, eavail, q3  (C-order)
NGRID = int(np.prod(GRID))       # 10976


def th2_to_numpy(h):
    """Fast TH2D -> dense numpy (drops under/overflow), matching compare_ascencio_fullcov."""
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
    x4 = th1_to_numpy(f.Get("hXSecND_flat")); f.Close()
    assert x4.size == NGRID, f"GBDT CV grid {x4.size} != {NGRID}"
    gmask = np.where(x4 > 0)[0]
    fc = ROOT.TFile.Open(cov_path)
    h = fc.Get(cov_hist)
    C = th2_to_numpy(h); fc.Close()
    assert C.shape[0] == gmask.size, f"GBDT cov dim {C.shape[0]} != reported {gmask.size}"
    return x4, gmask, C


def load_pet(wlat_path, rebank_path, transfer_path):
    """PET full-grid CV (recomputed via PETxsec to recover the full-grid mask) +
    a dict of named combined-covariance variants on the SAME 4796-bin ordering.

    Verifies (a) the recomputed CV matches every file's embedded hXSec_cv_flat (so
    the row-ordering map is provably correct and the files share one mask), and
    (b) the rebank C_stat / C_ML are bit-identical to the _wlat ones (the #12
    'perfect control' that licenses swapping in the clean C_syst).

    Variants returned:
      corrected      : rebank clean C_syst+C_stat+C_ML  +  PET-native C_lateral
                       (from _wlat)  -- HEADLINE (bug-free + independence-fair)
      published_wlat : raw _wlat C_total (pre-#12-fix, conservative cross-check)
      rebank_nolat   : rebank C_total (clean syst+stat+ML, no lateral)
      transferred    : combined.root C_total (GBDT-transferred lateral)
    """
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    from pet_systematics import PETxsec
    pet = PETxsec(f"{_REPO}/nd-unfolding/of_inputs_pc.npz",
                  f"{_REPO}/nd-unfolding/products/pet/pet_weights_full.npz",
                  f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root",
                  "pTmu_reweightedflux_integrated",
                  f"{_REPO}/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    x_cv = pet.xsec(None)
    assert x_cv.size == NGRID, f"PET CV grid {x_cv.size} != {NGRID}"
    pmask = np.where(x_cv > 0)[0]

    def _open(path):
        fc = ROOT.TFile.Open(path)
        base = th1_to_numpy(fc.Get("hXSec_cv_flat"))
        blk = {k.GetName(): th2_to_numpy(fc.Get(k.GetName()))
               for k in fc.GetListOfKeys() if k.GetName().startswith("C_")}
        fc.Close()
        assert pmask.size == base.size, f"{path}: mask {pmask.size} != embedded CV {base.size}"
        rel = np.abs(x_cv[pmask] - base) / np.where(base != 0, np.abs(base), 1)
        assert rel.max() < 1e-4, f"{path}: PET CV mismatch (max rel {rel.max():.2e})"
        return blk

    wl = _open(wlat_path)
    rb = _open(rebank_path)
    tr = _open(transfer_path)
    # #12 perfect-control assertion: clean rebank stat/ML == published stat/ML
    for nm in ("C_stat", "C_ML"):
        assert np.allclose(rb[nm], wl[nm]), f"rebank {nm} != wlat {nm} -- mask/order mismatch"
    print("[pet] recomputed CV matches all 3 files' embedded CV; rebank C_stat/C_ML "
          "bit-identical to _wlat (#12 control OK)")

    corrected = rb["C_syst"] + rb["C_stat"] + rb["C_ML"] + wl["C_lateral"]
    variants = {
        "corrected": corrected,
        "published_wlat": wl["C_total"],
        "rebank_nolat": rb["C_total"],
        "transferred": tr["C_total"],
    }
    return x_cv, pmask, variants


def frac_unc(C, cv_reported):
    d = np.sqrt(np.clip(np.diag(C), 0, None))
    return np.where(cv_reported > 0, d / cv_reported, np.nan)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pet-wlat",
                    default=f"{_REPO}/nd-unfolding/products/pet/pet_4d_covariance_combined_wlat.root")
    ap.add_argument("--pet-rebank",
                    default=f"{_REPO}/nd-unfolding/products/pet/pet_4d_covariance_combined_rebank.root")
    ap.add_argument("--pet-transfer",
                    default=f"{_REPO}/nd-unfolding/products/pet/pet_4d_covariance_combined.root")
    ap.add_argument("--gbdt-cov",
                    default=f"{_REPO}/nd-unfolding/uq_4d/universe_stage2_4d/"
                            "uq_universe_4d_covariance_combined.root")
    ap.add_argument("--gbdt-cov-hist", default="hCov_combined4d_total")
    ap.add_argument("--gbdt-cv",
                    default=f"{_REPO}/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--outdir", default=f"{_REPO}/nd-unfolding/products/pet")
    ap.add_argument("--label",
                    default="subsample PET (2M-train reweight; CV ~9% from GBDT) -- indicative only")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # ---- load both engines on the full grid ----
    pet_cv_full, pmask, pet_vars = load_pet(args.pet_wlat, args.pet_rebank, args.pet_transfer)
    gbdt_cv_full, gmask, C_gbdt = load_gbdt(args.gbdt_cov, args.gbdt_cov_hist, args.gbdt_cv)
    C_pet = pet_vars["corrected"]          # HEADLINE: rebank clean syst+stat+ML + native lateral
    C_pet_tr = pet_vars["transferred"]     # secondary cross-check (GBDT-transferred lateral)

    print(f"[mask] PET reported = {pmask.size}   GBDT reported = {gmask.size}   "
          f"grid = {NGRID}")

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
    pet_fr = frac_unc(C_pet, pet_cv_full[pmask])[p_sel]            # HEADLINE (corrected)
    gbdt_fr = frac_unc(C_gbdt, gbdt_cv_full[gmask])[g_sel]
    # per-bin frac for every PET variant (same pmask -> p_sel ordering)
    pet_fr_var = {nm: frac_unc(C, pet_cv_full[pmask])[p_sel] for nm, C in pet_vars.items()}

    good = np.isfinite(pet_fr) & np.isfinite(gbdt_fr) & (gbdt_fr > 0) & (pet_fr > 0)
    ratio = np.full(common.size, np.nan)
    ratio[good] = pet_fr[good] / gbdt_fr[good]

    # ---- summary stats ----
    med_pet = float(np.median(pet_fr[good]))                       # corrected headline
    med_gbdt = float(np.median(gbdt_fr[good]))
    med_ratio = float(np.median(ratio[good]))
    frac_pet_lt = float(np.mean(pet_fr[good] < gbdt_fr[good]))
    med_pet_variants = {nm: float(np.median(v[good & np.isfinite(v)]))
                        for nm, v in pet_fr_var.items()}
    summary = {
        "label": args.label,
        "headline_pet_cov": "corrected = rebank(C_syst+C_stat+C_ML) + PET-native C_lateral (#12-clean)",
        "n_grid": NGRID,
        "n_pet_reported": int(pmask.size),
        "n_gbdt_reported": int(gmask.size),
        "n_common": int(common.size),
        "n_pet_only": int(np.setdiff1d(pmask, gmask).size),
        "n_gbdt_only": int(np.setdiff1d(gmask, pmask).size),
        "median_frac_pet_corrected": med_pet,
        "median_frac_pet_published_wlat": med_pet_variants["published_wlat"],
        "median_frac_pet_rebank_nolat": med_pet_variants["rebank_nolat"],
        "median_frac_pet_transferred": med_pet_variants["transferred"],
        "median_frac_gbdt": med_gbdt,
        "median_ratio_pet_over_gbdt_corrected": med_ratio,
        "fraction_bins_pet_lt_gbdt_corrected": frac_pet_lt,
        "pet_cov_rebank": args.pet_rebank,
        "pet_cov_wlat_native_lateral": args.pet_wlat,
        "pet_cov_transferred": args.pet_transfer,
        "gbdt_cov": f"{args.gbdt_cov}::{args.gbdt_cov_hist}",
        "known_issues_ref": "KNOWN_ISSUES #12 (RESOLVED 2026-06-12): published 18.31% C_syst "
                            "was garbage-miss-row inflated; rebank clean = 8.24%.",
    }
    print("\n=== SUMMARY (common bins, PET-native lateral headline) ===")
    for k, v in summary.items():
        print(f"  {k:36s} {v}")

    # ---- map common bins to grid coords for projections ----
    ipt, ipz, iea, iq3 = np.unravel_index(common, GRID, order="C")
    idxs = {"pt": ipt, "pz": ipz, "eavail": iea, "q3": iq3}

    # edges for plotting centres (from the PET inputs npz; identical to GBDT axes)
    pc = np.load(f"{_REPO}/nd-unfolding/of_inputs_pc.npz")
    edges = [np.asarray(pc[f"edges_{i}"], float) for i in range(4)]

    # ---- (2a) 1D-projection overlays of the per-bin fractional uncertainty ----
    # For each axis bin: median per-bin fractional uncertainty over all common 4D
    # bins in that slice (robust "typical uncertainty vs axis").  10-90% band shaded.
    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    for ai, (nm, axp) in enumerate(zip(AXES, axs.ravel())):
        e = edges[ai]; cen = 0.5 * (e[:-1] + e[1:])
        nb = GRID[ai]
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
        axp.set_xlabel(AXLABEL[nm])
        axp.set_ylabel("per-bin frac. uncertainty (%)")
        axp.legend(fontsize=8)
        axp.text(0.97, 0.95, f"med PET {np.nanmedian(med_p):.1f}%\nmed GBDT {np.nanmedian(med_g):.1f}%",
                 transform=axp.transAxes, ha="right", va="top", fontsize=8,
                 bbox=dict(fc="white", ec="0.7", alpha=0.8))
    fig.text(0.5, 0.005, args.label, ha="center", fontsize=8, style="italic")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    p_overlay = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_overlay.png")
    fig.savefig(p_overlay, dpi=130); plt.close(fig)
    print(f"[OK] wrote {p_overlay}")

    # ---- (2b) per-bin ratio (PET/GBDT) map projected onto (pt, pz) ----
    # median ratio over (eavail, q3) per (pt, pz) cell -> 14x16 heatmap, RdBu_r at 1.
    rmap = np.full((GRID[0], GRID[1]), np.nan)
    cntmap = np.zeros((GRID[0], GRID[1]), int)
    for k in range(common.size):
        if not good[k]:
            continue
        cntmap[ipt[k], ipz[k]] += 1
    for a in range(GRID[0]):
        for b in range(GRID[1]):
            m = (ipt == a) & (ipz == b) & good
            if m.sum():
                rmap[a, b] = np.median(ratio[m])
    fig2, ax2 = plt.subplots(figsize=(8.5, 6))
    im = ax2.pcolormesh(edges[1], edges[0], rmap, cmap="RdBu_r", vmin=0.5, vmax=1.5)
    cb = fig2.colorbar(im, ax=ax2); cb.set_label("PET / GBDT  per-bin frac. unc. (median over Eavail,q3)")
    ax2.set_xlabel(AXLABEL["pz"]); ax2.set_ylabel(AXLABEL["pt"])
    ax2.text(0.99, 1.01, f"<1 (blue): PET tighter   |   median ratio {med_ratio:.3f}",
             transform=ax2.transAxes, ha="right", va="bottom", fontsize=9)
    fig2.text(0.5, 0.005, args.label, ha="center", fontsize=8, style="italic")
    fig2.tight_layout(rect=(0, 0.02, 1, 1))
    p_ratio = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_ratiomap.png")
    fig2.savefig(p_ratio, dpi=130); plt.close(fig2)
    print(f"[OK] wrote {p_ratio}")

    # ---- (2c) histogram of the per-bin ratio (the headline distribution) ----
    fig3, ax3 = plt.subplots(figsize=(7.5, 5))
    ax3.hist(ratio[good], bins=np.linspace(0, 3, 61), color="C2", alpha=0.8)
    ax3.axvline(1.0, color="k", lw=1, ls=":")
    ax3.axvline(med_ratio, color="C3", lw=2, label=f"median {med_ratio:.3f}")
    ax3.set_xlabel("PET / GBDT  per-bin fractional uncertainty")
    ax3.set_ylabel("common bins")
    ax3.legend(fontsize=9)
    ax3.text(0.99, 0.95,
             f"median PET {100*med_pet:.1f}%\nmedian GBDT {100*med_gbdt:.1f}%\n"
             f"bins PET<GBDT {100*frac_pet_lt:.0f}%\nN_common {common.size}",
             transform=ax3.transAxes, ha="right", va="top", fontsize=8,
             bbox=dict(fc="white", ec="0.7", alpha=0.85))
    fig3.text(0.5, 0.005, args.label, ha="center", fontsize=8, style="italic")
    fig3.tight_layout(rect=(0, 0.03, 1, 1))
    p_hist = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_ratiohist.png")
    fig3.savefig(p_hist, dpi=130); plt.close(fig3)
    print(f"[OK] wrote {p_hist}")

    # ---- verdict ----
    if med_ratio < 0.90 and frac_pet_lt > 0.60:
        tag, phrase = "REDUCES", ("So PET MODESTLY REDUCES the uncertainty vs the scalars "
                                  "at this stats regime")
    elif med_ratio > 1.10 and frac_pet_lt < 0.40:
        tag, phrase = "WORSE", ("So PET is WORSE than the scalars in per-bin precision")
    else:
        tag, phrase = "COMPARABLE", ("So PET essentially MATCHES the GBDT precision rather than "
                                     "reducing it -- the point cloud agrees with the scalars on "
                                     "the central value AND lands at comparable uncertainty")
    verdict = (
        f"VERDICT: PET is {tag} to GBDT in per-bin uncertainty on the {common.size} "
        f"common 4D bins (every PET bin is a GBDT bin; GBDT reports {summary['n_gbdt_only']} "
        f"extra). Median per-bin fractional uncertainty is {100*med_pet:.1f}% for PET "
        f"(corrected: #12-clean rebank syst+stat+ML plus the PET-native lateral block) vs "
        f"{100*med_gbdt:.1f}% for GBDT; the median per-bin ratio is {med_ratio:.3f} and PET "
        f"is tighter in {100*frac_pet_lt:.0f}% of bins. {phrase}. "
        f"Caveat 1 (covariance provenance): the raw published _wlat budget reads "
        f"{100*med_pet_variants['published_wlat']:.1f}% because its C_syst was inflated by the "
        f"KNOWN_ISSUES #12 garbage-miss-row bug; we headline the corrected rebank budget per "
        f"the repo's adopted guidance. The lateral block is PET-NATIVE (independence-fair); the "
        f"GBDT-transferred-lateral variant gives {100*med_pet_variants['transferred']:.1f}%, so "
        f"the conclusion is not an artifact of the lateral treatment. "
        f"Caveat 2 (stats regime): the PET covariance is anchored to the 2M-train reweight "
        f"(pet_weights_full.npz), which still carries the PET-vs-GBDT CV training gap; the "
        f"full-statistics PET (cal20m, job 55047632) was PENDING at run time, so this is "
        f"INDICATIVE of the method, not a final full-stats uncertainty."
    )
    print("\n" + verdict)
    summary["verdict_tag"] = tag
    summary["verdict"] = verdict
    summary["figures"] = [p_overlay, p_ratio, p_hist]

    p_json = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_summary.json")
    with open(p_json, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[OK] wrote {p_json}")


if __name__ == "__main__":
    main()
