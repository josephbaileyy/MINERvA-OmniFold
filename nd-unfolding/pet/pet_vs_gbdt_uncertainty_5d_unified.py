#!/usr/bin/env python3
"""D7 (UNIFIED) -- PET vs GBDT 5D per-bin uncertainty on the UNIFIED-THROW covariances.

Companion to pet/pet_vs_gbdt_uncertainty_5d.py (which compares the BLOCK-SUM budgets).
Here both engines use their UNIFIED-THROW systematic covariance -- the throw is
re-unfolded as a whole, so cross-band correlations (and, for GBDT, the retraining
nonlinearity) are captured rather than summed band-by-band.

  * GBDT : adopted unified cov = C_unified + stat + ML + 9 detector-lateral bands
           (uq_5d/gbdt_5d_covariance_adopted.root::hCov_gbdt5d_adopted, from D5).
           CV = hXSecND_flat -> 10694 reported bins.
  * PET  : C_total from pet_5d_covariance_combined_unified_wlat.root
           (unified C_syst + C_stat + C_ML + PET-native shifted-W C_lateral).
           CV recomputed via PETxsec5D (pet_weights_full.npz) -> 10550 reported bins.

Comparison runs on the intersection of the two full-grid index sets (C-order ravel of
the 14x16x7x7x6 grid), exactly as the block-sum companion.

CRUCIAL ASYMMETRY (reported, not hidden): the GBDT unified throw RE-TRAINS/re-unfolds
each throw, so its C_unified contains the full retraining-response nonlinearity. The PET
unified throw uses the FROZEN reweighter (a fixed trained network reweighted per throw),
so PET's unified C_syst is a LOWER BOUND -- it omits the PET retraining-response term
(being measured separately as the Tier-2 study). The PET number here can therefore only
RISE once Tier-2 is folded in; a PET<=GBDT result at this stage is not yet conclusive.

Run from nd-unfolding/ after `source ../setup_salloc_env.sh`:
  python pet/pet_vs_gbdt_uncertainty_5d_unified.py
"""
import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402

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
GRID = (14, 16, 7, 7, 6)
NGRID = int(np.prod(GRID))


def th2_to_numpy(h):
    n = h.GetNbinsX()
    a = np.frombuffer(h.GetArray(), dtype=np.float64,
                      count=(n + 2) * (n + 2)).reshape(n + 2, n + 2)[1:n + 1, 1:n + 1].T.copy()
    return a


def th1_to_numpy(h):
    return np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])


def get_param(f, name, default=None):
    o = f.Get(name)
    return o.GetVal() if o else default


def load_gbdt_unified(cov_path, cov_hist, cv_path, cv_hist, unified_path):
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(cv_path)
    x5 = th1_to_numpy(f.Get(cv_hist)); f.Close()
    assert x5.size == NGRID, f"GBDT CV grid {x5.size} != {NGRID}"
    gmask = np.where(x5 > 0)[0]
    fc = ROOT.TFile.Open(cov_path)
    C = th2_to_numpy(fc.Get(cov_hist)); fc.Close()
    assert C.shape[0] == gmask.size, f"GBDT cov dim {C.shape[0]} != reported {gmask.size}"
    # unified/block inflation from the throw file
    fu = ROOT.TFile.Open(unified_path)
    tr_u = get_param(fu, "sqrt_tr_unified"); tr_b = get_param(fu, "sqrt_tr_block")
    fu.Close()
    ub = (tr_u / tr_b) if (tr_u and tr_b) else float("nan")
    return x5, gmask, C, ub


def load_pet_unified(path, w_source, comp_ref):
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

    fc = ROOT.TFile.Open(path)
    base = th1_to_numpy(fc.Get("hXSec_cv_flat"))
    want = ("C_syst", "C_stat", "C_ML", "C_lateral", "C_total")
    blk = {nm: th2_to_numpy(fc.Get(nm)) for nm in want}
    ub = get_param(fc, "pet_unified_block_ratio", float("nan"))
    fc.Close()
    assert pmask.size == base.size, f"{path}: mask {pmask.size} != embedded CV {base.size}"
    rel = np.abs(x_cv[pmask] - base) / np.where(base != 0, np.abs(base), 1)
    assert rel.max() < 1e-4, f"{path}: PET CV mismatch (max rel {rel.max():.2e})"
    print("[pet5d-uni] recomputed CV matches embedded CV (row-order map OK)")
    variants = {"headline": blk["C_total"],
                "vertical_nolat": blk["C_syst"] + blk["C_stat"] + blk["C_ML"]}
    return x_cv, pmask, variants, ub


def frac_unc(C, cv_reported):
    d = np.sqrt(np.clip(np.diag(C), 0, None))
    return np.where(cv_reported > 0, d / cv_reported, np.nan)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pet-unified",
                    default=f"{_REPO}/nd-unfolding/products/pet/pet_5d_covariance_combined_unified_wlat.root")
    ap.add_argument("--pet-wsource", default=f"{_REPO}/nd-unfolding/of_inputs_5d.npz")
    ap.add_argument("--pet-compref",
                    default=f"{_REPO}/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--gbdt-cov",
                    default=f"{_REPO}/nd-unfolding/uq_5d/gbdt_5d_covariance_adopted.root")
    ap.add_argument("--gbdt-cov-hist", default="hCov_gbdt5d_adopted")
    ap.add_argument("--gbdt-unified",
                    default=f"{_REPO}/nd-unfolding/uq_5d/unified_throw_cov_5d.root")
    ap.add_argument("--gbdt-cv",
                    default=f"{_REPO}/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--gbdt-cv-hist", default="hXSecND_flat")
    ap.add_argument("--outdir", default=f"{_REPO}/nd-unfolding/products/pet/unified")
    ap.add_argument("--label",
                    default="UNIFIED-THROW covariance, 5D (pt,pz,Eavail,q3,W); PET frozen-reweighter "
                            "(lower bound -- Tier-2 retraining not yet folded in)")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    pet_cv_full, pmask, pet_vars, pet_ub = load_pet_unified(args.pet_unified, args.pet_wsource, args.pet_compref)
    gbdt_cv_full, gmask, C_gbdt, gbdt_ub = load_gbdt_unified(
        args.gbdt_cov, args.gbdt_cov_hist, args.gbdt_cv, args.gbdt_cv_hist, args.gbdt_unified)
    C_pet = pet_vars["headline"]
    print(f"[mask] PET reported = {pmask.size}   GBDT reported = {gmask.size}   grid = {NGRID}")
    print(f"[unified/block] GBDT = {gbdt_ub:.3f}   PET = {pet_ub:.3f}")

    common = np.intersect1d(pmask, gmask)
    print(f"[mask] INTERSECTION = {common.size}   PET-only={np.setdiff1d(pmask,gmask).size}  "
          f"GBDT-only={np.setdiff1d(gmask,pmask).size}")

    p_pos = {g: i for i, g in enumerate(pmask)}
    g_pos = {g: i for i, g in enumerate(gmask)}
    p_sel = np.array([p_pos[g] for g in common])
    g_sel = np.array([g_pos[g] for g in common])

    pet_fr = frac_unc(C_pet, pet_cv_full[pmask])[p_sel]
    gbdt_fr = frac_unc(C_gbdt, gbdt_cv_full[gmask])[g_sel]
    pet_fr_var = {nm: frac_unc(C, pet_cv_full[pmask])[p_sel] for nm, C in pet_vars.items()}

    good = np.isfinite(pet_fr) & np.isfinite(gbdt_fr) & (gbdt_fr > 0) & (pet_fr > 0)
    ratio = np.full(common.size, np.nan)
    ratio[good] = pet_fr[good] / gbdt_fr[good]

    med_pet = float(np.median(pet_fr[good]))
    med_gbdt = float(np.median(gbdt_fr[good]))
    med_ratio = float(np.median(ratio[good]))
    frac_pet_lt = float(np.mean(pet_fr[good] < gbdt_fr[good]))
    med_pet_variants = {nm: float(np.median(v[good & np.isfinite(v)])) for nm, v in pet_fr_var.items()}

    summary = {
        "label": args.label,
        "covariance_method": "unified-throw (re-unfolded), both engines",
        "gbdt_cov": f"{args.gbdt_cov}::{args.gbdt_cov_hist}",
        "pet_cov": f"{args.pet_unified}::C_total",
        "gbdt_unified_over_block": gbdt_ub,
        "pet_unified_over_block": pet_ub,
        "n_common": int(common.size),
        "n_pet_reported": int(pmask.size),
        "n_gbdt_reported": int(gmask.size),
        "n_gbdt_only": int(np.setdiff1d(gmask, pmask).size),
        "median_frac_pet_headline": med_pet,
        "median_frac_pet_vertical_nolat": med_pet_variants["vertical_nolat"],
        "median_frac_gbdt": med_gbdt,
        "median_ratio_pet_over_gbdt": med_ratio,
        "fraction_bins_pet_lt_gbdt": frac_pet_lt,
    }
    print("\n=== SUMMARY (unified, common bins, 5D) ===")
    for k, v in summary.items():
        print(f"  {k:34s} {v}")

    coords = np.unravel_index(common, GRID, order="C")
    idxs = {nm: coords[i] for i, nm in enumerate(AXES)}
    pc = np.load(f"{_REPO}/nd-unfolding/of_inputs_pc.npz")
    g5 = np.load(args.pet_wsource)
    edges = [np.asarray(pc[f"edges_{i}"], float) for i in range(4)] + [np.asarray(g5["edges_4"], float)]

    # (a) 1D-projection overlays
    fig, axs = plt.subplots(2, 3, figsize=(15, 8)); axs = axs.ravel()
    for ai, nm in enumerate(AXES):
        axp = axs[ai]; e = edges[ai]; cen = 0.5 * (e[:-1] + e[1:]); nb = GRID[ai]
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
        axp.step(cen, med_p, where="mid", lw=2, color="C0", label="PET (frozen, lower bound)")
        axp.step(cen, med_g, where="mid", lw=2, ls="--", color="C1", label="GBDT (re-unfolded)")
        axp.set_xlabel(AXLABEL[nm]); axp.set_ylabel("per-bin frac. uncertainty (%)")
        axp.legend(fontsize=8)
        axp.text(0.97, 0.95, f"med PET {np.nanmedian(med_p):.1f}%\nmed GBDT {np.nanmedian(med_g):.1f}%",
                 transform=axp.transAxes, ha="right", va="top", fontsize=8,
                 bbox=dict(fc="white", ec="0.7", alpha=0.8))
    axs[-1].axis("off")
    fig.text(0.5, 0.005, args.label, ha="center", fontsize=8, style="italic")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    p_overlay = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_5d_unified_overlay.png")
    fig.savefig(p_overlay, dpi=130); plt.close(fig); print(f"[OK] wrote {p_overlay}")

    # (b) ratio histogram
    fig3, ax3 = plt.subplots(figsize=(7.5, 5))
    ax3.hist(ratio[good], bins=np.linspace(0, 3, 61), color="C2", alpha=0.8)
    ax3.axvline(1.0, color="k", lw=1, ls=":")
    ax3.axvline(med_ratio, color="C3", lw=2, label=f"median {med_ratio:.3f}")
    ax3.set_xlabel("PET / GBDT  per-bin fractional uncertainty (unified throw)")
    ax3.set_ylabel("common bins"); ax3.legend(fontsize=9)
    ax3.text(0.99, 0.95,
             f"median PET {100*med_pet:.1f}%\nmedian GBDT {100*med_gbdt:.1f}%\n"
             f"bins PET<GBDT {100*frac_pet_lt:.0f}%\nN_common {common.size}\n"
             f"unified/block: GBDT {gbdt_ub:.2f}x  PET {pet_ub:.2f}x",
             transform=ax3.transAxes, ha="right", va="top", fontsize=8,
             bbox=dict(fc="white", ec="0.7", alpha=0.85))
    fig3.text(0.5, 0.005, args.label, ha="center", fontsize=8, style="italic")
    fig3.tight_layout(rect=(0, 0.03, 1, 1))
    p_hist = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_5d_unified_ratiohist.png")
    fig3.savefig(p_hist, dpi=130); plt.close(fig3); print(f"[OK] wrote {p_hist}")

    verdict = (
        f"VERDICT (UNIFIED throw): on the {common.size} common 5D bins, median per-bin fractional "
        f"uncertainty is {100*med_pet:.1f}% for PET (frozen-reweighter unified C_total, a LOWER BOUND) "
        f"vs {100*med_gbdt:.1f}% for GBDT (re-unfolded adopted unified cov); median ratio {med_ratio:.3f}, "
        f"PET tighter in {100*frac_pet_lt:.0f}% of bins. The unified throw inflates the systematic over "
        f"block-sum by {gbdt_ub:.2f}x (GBDT) and {pet_ub:.2f}x (PET). ASYMMETRY CAVEAT: the GBDT unified "
        f"throw re-unfolds each throw (captures the retraining nonlinearity), whereas the PET unified throw "
        f"uses a FROZEN reweighter, so the PET number OMITS its retraining-response term and can only rise "
        f"once the Tier-2 study is folded in -- a PET<=GBDT reading here is therefore not yet conclusive."
    )
    print("\n" + verdict)
    summary["verdict"] = verdict
    summary["figures"] = [p_overlay, p_hist]
    p_json = os.path.join(args.outdir, "pet_vs_gbdt_uncertainty_5d_unified_summary.json")
    with open(p_json, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[OK] wrote {p_json}")


if __name__ == "__main__":
    main()
