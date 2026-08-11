#!/usr/bin/env python3
"""Citable receipt for the 2D (pT, p||) chi^2/ndf numbers quoted against the
GENIE 2.12.6 MINERvA Tune v1 prediction.

WHY THIS EXISTS
---------------
`docs/analysis-note/sec_results.tex` quotes "chi2/ndf: data vs tune 33.0, ours
vs tune 26.5". The 33.0 is recorded in `3d-unfolding/3D_OMNIFOLD_RUN_LOG.md:112`
as a validation-gate result. The 26.5 appeared nowhere in the repository: it was
produced by `compare_to_models.py`, but that script emits its chi^2 lines with a
bare `print()` from the imported `chi2_with_cov()` helper instead of its own
`emit()` closure, so the numbers reach the console and are dropped from the
committed `model_comp_report.txt` -- which is why that report file ends at the
"--- chi^2 in paper TotalCov (ndf = 205) ---" header with no rows under it.

This script recomputes the same quantities on frozen inputs and writes a JSON
receipt carrying the ingredients (inputs + hashes, masking, inverse, ndf
justification, and enough intermediate operands that the reported numbers can
contradict each other), per
`docs/orchestration/CONVENTION-receipt-ingredients.md`.

NO UNFOLD IS RE-RUN. Every input is a pre-existing frozen artifact.

METHOD (unchanged from `compare_to_paper_fullcov.chi2_with_cov`)
----------------------------------------------------------------
  chi^2 = d^T pinv(C) d, restricted to the bins the paper reports
  (positive diagonal in StatOnlyCovariance -> 205 of 224 cells),
  C = the published TotalCovariance, ndf = n_reported = 205.

`np.linalg.pinv` is the documented convention at the point of use in
`compare_to_paper_fullcov.py` (the published cov is near-singular: cond ~1.5e12,
rank 204/205). ndf = n_reported is justified in 2D by the rank-truncation scan
recorded in `2d-unfolding/2D_OMNIFOLD_RUN_LOG.md:37` -- it rises smoothly
0.69(r=50) -> 2.35(100) -> 3.30(180) -> 3.66(205) with no cliff, so the
effective rank is not far below n_reported and no truncated ndf is warranted.
This script re-runs that scan for all three comparisons rather than assuming it.

Usage:
  source setup_salloc_env.sh
  python 2d-unfolding/receipt_model_chi2_2d.py [--out <receipt.json>]
"""

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

REPO = os.environ.get("MNV_REPO", "/pscratch/sd/j/josephrb/MINERvA-OmniFold")
ANC_DIR = os.path.join(REPO, "2d-unfolding", "minerva_paper_anc")

COV_ROOT = os.path.join(ANC_DIR, "cov_ptpl_minerva_inclusive_6GeV.root")
DATA_TXT = os.path.join(ANC_DIR, "data_result_ptpl_2D_minerva_inclusive_6GeV.txt")
TUNE_TXT = os.path.join(ANC_DIR,
                        "model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt")
OURS_ROOT = os.path.join(REPO, "2d-unfolding",
                         "2d_crossSection_omnifold_MEFHC_5iter.root")

# Paper global index: gid = (Ptbin - 1) * 16 + (P||bin - 1); Pt 1..14, P|| 1..16.
N_PT, N_PZ = 14, 16
N = N_PT * N_PZ  # 224

RANK_SCAN_POINTS = [10, 25, 50, 73, 100, 139, 150, 180, 200, 204, 205]


# --------------------------------------------------------------------------
# loaders (mirror compare_to_paper_fullcov.py / compare_to_models.py exactly)
# --------------------------------------------------------------------------
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tmatrix_to_numpy(tm):
    n = tm.GetNrows()
    arr = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            arr[i, j] = tm(i, j)
    return arr


def flatten_th2d(h):
    """Published data TH2D -> length-224 global vector."""
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    x_is_pt = (nx == N_PT)
    v = np.zeros(N)
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            ptb, pzb = (ix, iy) if x_is_pt else (iy, ix)
            v[(ptb - 1) * N_PZ + (pzb - 1)] = h.GetBinContent(ix, iy)
    return v


def flatten_ours(h):
    """Our hXSec2D: x = pt (14), y = p|| (16)."""
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    assert nx == N_PT and ny == N_PZ, f"ours shape: {nx}x{ny}"
    v = np.zeros(N)
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            v[(ix - 1) * N_PZ + (iy - 1)] = h.GetBinContent(ix, iy)
    return v


def load_ancillary_csv(path, col):
    """Ancillary CSV in `P||bin,Ptbin,<cols...>` format -> length-224 vector."""
    v = np.zeros(N)
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.lower().startswith("p|"):
                continue
            f = line.split(",")
            v[(int(f[1]) - 1) * N_PZ + (int(f[0]) - 1)] = float(f[col])
    return v


# --------------------------------------------------------------------------
# chi^2 machinery
# --------------------------------------------------------------------------
def chi2_pinv(d_red, C_red):
    """chi^2 = d^T pinv(C) d on the already-reduced (reported-bin) block."""
    Cinv = np.linalg.pinv(C_red)
    return float(d_red @ Cinv @ d_red)


def rank_scan(d_red, evals_desc, evecs_desc, points):
    """Truncated-spectral chi^2: keep the top-r eigen-directions of C.

    chi^2(r) = sum_{k<r} (u_k . d)^2 / lambda_k.  At r = n this is the
    unregularized quadratic form and must agree with the pinv result.
    """
    c = evecs_desc.T @ d_red                      # projection onto eigenbasis
    terms = c ** 2 / evals_desc
    cum = np.cumsum(terms)
    return {int(r): float(cum[r - 1]) for r in points if 1 <= r <= len(cum)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ours", default=OURS_ROOT)
    ap.add_argument("--tune", default=TUNE_TXT)
    ap.add_argument("--out", default=os.path.join(
        REPO, "2d-unfolding", "receipt_model_chi2_2d.json"))
    args = ap.parse_args()

    # ---- ingredients: inputs and their hashes ---------------------------
    inputs = {
        "paper_covariance_and_data_root": COV_ROOT,
        "paper_data_csv_crosscheck": DATA_TXT,
        "tune_v1_prediction_csv": args.tune,
        "our_unfolded_2d_result_root": args.ours,
    }
    hashes = {k: sha256(p) for k, p in inputs.items()}

    # ---- load ------------------------------------------------------------
    fp = ROOT.TFile.Open(COV_ROOT)
    if not fp or fp.IsZombie():
        sys.exit(f"[FAIL] cannot open {COV_ROOT}")
    cov_total = tmatrix_to_numpy(fp.Get("TotalCovariance"))
    cov_stat = tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
    data_v = flatten_th2d(fp.Get("pt_pl_cross_section"))

    fo = ROOT.TFile.Open(args.ours)
    if not fo or fo.IsZombie():
        sys.exit(f"[FAIL] cannot open {args.ours}")
    h_ours = fo.Get("hXSec2D")
    if not h_ours:
        sys.exit(f"[FAIL] hXSec2D missing in {args.ours}")
    ours_v = flatten_ours(h_ours)

    tune_v = load_ancillary_csv(args.tune, 2)
    data_csv_v = load_ancillary_csv(DATA_TXT, 2)

    assert cov_total.shape == (N, N), cov_total.shape

    # ---- reported-bin mask ----------------------------------------------
    mask = np.diag(cov_stat) > 0
    n_rep = int(mask.sum())
    idx = np.where(mask)[0]

    # CONTROL on the bin mapping. The tune CSV is indexed `P||bin,Ptbin` and is
    # mapped to the global grid by the same expression as the data CSV. If the
    # data CSV round-trips onto the ROOT TH2D under that mapping, the tune
    # vector is on the right bins too. This is the check that would catch a
    # transposed pt/p|| axis -- the one failure mode that silently changes chi^2.
    both = mask & (data_v > 0)
    map_reldev = float(np.max(np.abs(
        data_csv_v[both] / data_v[both] - 1.0)))
    mask_agrees_with_csv = bool(np.array_equal(mask, data_csv_v > 0))

    C = cov_total[np.ix_(idx, idx)]
    evals, evecs = np.linalg.eigh(C)             # ascending
    order = np.argsort(evals)[::-1]
    evals_d, evecs_d = evals[order], evecs[:, order]
    cond = float(evals_d[0] / evals_d[-1]) if evals_d[-1] > 0 else float("inf")
    rcond_pinv = float(max(C.shape) * np.finfo(C.dtype).eps)
    n_sv_kept = int((evals_d > rcond_pinv * evals_d[0]).sum())
    sigma = np.sqrt(np.diag(C))

    # ---- the three comparisons -------------------------------------------
    comparisons = [
        # (key, description, vector A, vector B)   -- diff = A - B
        ("ours_vs_data", "ours - published data (control; run log 3.661)",
         ours_v, data_v),
        ("data_vs_tune", "published data - MINERvA Tune v1 "
                         "(CONTROL; 3D_OMNIFOLD_RUN_LOG.md:112 -> 33.0)",
         data_v, tune_v),
        ("ours_vs_tune", "ours - MINERvA Tune v1 "
                         "(TARGET; sec_results.tex:167 -> 26.5)",
         ours_v, tune_v),
    ]

    results = {}
    for key, desc, a, b in comparisons:
        d = (a - b)[mask]
        chi2 = chi2_pinv(d, C)
        scan = rank_scan(d, evals_d, evecs_d, RANK_SCAN_POINTS)
        chi2_full_spectral = scan[n_rep]
        pulls = d / sigma
        diag_chi2 = float(np.sum(pulls ** 2))
        results[key] = {
            "description": desc,
            # --- headline
            "chi2": chi2,
            "ndf": n_rep,
            "chi2_per_ndf": chi2 / n_rep,
            # --- operands the headline must be derivable from
            "sum_A_reported": float(a[mask].sum()),
            "sum_B_reported": float(b[mask].sum()),
            "ratio_A_over_B": float(a[mask].sum() / b[mask].sum()),
            "pull_mean": float(pulls.mean()),
            "pull_rms": float(pulls.std()),
            "pull_max_abs": float(np.abs(pulls).max()),
            # --- falsifiers
            "chi2_diagonal_only": diag_chi2,
            "chi2_per_ndf_diagonal_only": diag_chi2 / n_rep,
            "offdiag_inflation_factor": chi2 / diag_chi2,
            # --- ndf justification: does the truncation scan rise smoothly?
            "rank_truncation_chi2_per_ndf": {
                str(r): v / n_rep for r, v in scan.items()},
            # --- internal consistency: spectral sum vs pinv, must match
            "chi2_full_spectral": chi2_full_spectral,
            "spectral_vs_pinv_reldiff": abs(chi2_full_spectral - chi2) / chi2,
        }

    # smoothness verdict for the ndf choice. The decisive test is the TAIL:
    # if ndf = n_reported were wrong, chi^2 would be carried by the smallest
    # eigenvalues (the near-null directions pinv barely constrains), and the
    # curve would jump at the top of the scan. `diagnose_tension.py` found the
    # 10 smallest modes carry only ~3% for ours-vs-data; that is the reference.
    scan_pts = [r for r in RANK_SCAN_POINTS if r <= n_rep]
    ndf_check = {}
    for key, desc, a, b in comparisons:
        vals = [results[key]["rank_truncation_chi2_per_ndf"][str(r)]
                for r in scan_pts]
        steps = np.diff(vals)
        d = (a - b)[mask]
        c = evecs_d.T @ d
        terms = c ** 2 / evals_d                 # per-eigendirection chi^2
        tot = float(terms.sum())
        ndf_check[key] = {
            "scan_points": scan_pts,
            "chi2_per_ndf_at_points": vals,
            "monotonic_nondecreasing": bool(np.all(steps >= -1e-9)),
            "largest_step_fraction_of_final": float(steps.max() / vals[-1]),
            "note_on_largest_step": "scan points are unevenly spaced, so this "
                                    "reflects point spacing, not a cliff; use "
                                    "the tail fractions below.",
            # cliff test: what the least-constrained directions actually carry
            "frac_chi2_in_smallest_1_modes": float(terms[-1:].sum() / tot),
            "frac_chi2_in_smallest_5_modes": float(terms[-5:].sum() / tot),
            "frac_chi2_in_smallest_10_modes": float(terms[-10:].sum() / tot),
            "frac_chi2_in_smallest_25_modes": float(terms[-25:].sum() / tot),
            # Two different orderings; keep both, they are easy to confuse.
            # (a) eigenvalue rank order (best-measured directions first) --
            #     this is what the rank-truncation scan above walks.
            "n_modes_to_reach_90pct_chi2_by_eigenvalue_rank": int(
                np.searchsorted(np.cumsum(terms) / tot, 0.90) + 1),
            # (b) contribution order (largest chi^2 carriers first) -- this is
            #     the "~90 modes reach 90%" figure in 2D_OMNIFOLD_RUN_LOG.md.
            "n_modes_to_reach_90pct_chi2_by_contribution": int(
                np.searchsorted(
                    np.cumsum(np.sort(terms)[::-1]) / tot, 0.90) + 1),
        }

    receipt = {
        "receipt": "2D (pT, p_par) chi^2/ndf vs GENIE 2.12.6 MINERvA Tune v1",
        "purpose": "Re-derive the unsourced 26.5 in docs/analysis-note/"
                   "sec_results.tex:167, with 33.0 as the control.",
        "generated_utc": datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": os.path.abspath(__file__),
        "unfold_rerun": False,
        "host": os.uname().nodename,
        "repo_commit": subprocess.run(
            ["git", "-C", REPO, "rev-parse", "HEAD"],
            capture_output=True, text=True).stdout.strip(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "root": ROOT.gROOT.GetVersion(),

        "ingredients": {
            "inputs": inputs,
            "sha256": hashes,
            "our_unfolded_product": {
                "file": args.ours,
                "hist": "hXSec2D",
                "identity": "Phase-18.2 frozen production MEFHC 5-iteration "
                            "OmniFold, d2sigma/(dpT dp_par); the finalised 2D "
                            "reproduction and the DEFAULT_OURS of "
                            "compare_to_paper_fullcov.py",
            },
            "tune_prediction": {
                "file": args.tune,
                "identity": "GENIE 2.12.6 MINERvA Tune v1 d2sigma/(dpT dp_par) "
                            "as SHIPPED in the arXiv:2106.16210 ancillary "
                            "(paper Figs. 15-18). Not re-derived: unlike 3D, "
                            "the 2D tune is published directly, so "
                            "3d-unfolding/genie/model_tune_xsec3d.py has no 2D "
                            "analogue to write -- the ancillary file IS the "
                            "reference that the 3D script was validated "
                            "against to 0.01%.",
            },
            "covariance": {
                "file": COV_ROOT,
                "object": "TotalCovariance (TMatrixT<double>, 224x224)",
                "identity": "published MINERvA total (stat+syst) covariance",
                "mask_object": "StatOnlyCovariance (positive diagonal defines "
                               "the reported bins)",
            },
            "masking": {
                "rule": "keep bins with positive diagonal in StatOnlyCovariance",
                "n_total_cells": N,
                "n_reported": n_rep,
                "n_dropped": N - n_rep,
                "mask_matches_xs_gt_0_in_data_csv": mask_agrees_with_csv,
                "bin_mapping_control_max_reldev_csv_vs_th2d": map_reldev,
                "bin_mapping_control_note":
                    "data CSV re-mapped through gid=(Ptbin-1)*16+(P||bin-1) "
                    "vs the ROOT TH2D; agreement to CSV print precision (~1e-3 "
                    "rel, 3 significant figures) confirms the tune CSV lands "
                    "on the same bins.",
            },
            "inverse": {
                "method": "numpy.linalg.pinv on the 205x205 reduced block",
                "why": "published TotalCov is near-singular; pinv is the "
                       "documented convention at the point of use in "
                       "2d-unfolding/compare_to_paper_fullcov.py:chi2_with_cov",
                "default_rcond": rcond_pinv,
                "condition_number": cond,
                "n_singular_values_kept_by_pinv": n_sv_kept,
                "n_singular_values_dropped_by_pinv": n_rep - n_sv_kept,
                "regularisation": "none beyond pinv's default rcond cut",
            },
            "ndf": {
                "value": n_rep,
                "rule": "ndf = n_reported = 205",
                "why": "no parameters are fitted in either comparison (both "
                       "the tune and our unfolded result are fixed "
                       "predictions), so ndf is the bin count.",
                "dimension_conditional_caveat":
                    "In this repo ndf = n_reported is justified in 2D and "
                    "explicitly NOT where effective rank is far below "
                    "n_reported. CHECKED, not assumed: see ndf_justification "
                    "below and 2D_OMNIFOLD_RUN_LOG.md:37.",
            },
        },

        "ndf_justification": {
            "test": "rank-truncation scan of chi^2/205 vs number of retained "
                    "eigen-directions of the published TotalCov; a cliff near "
                    "r = n_reported would mean the number is carried by "
                    "null/near-null directions and ndf = n_reported would be "
                    "wrong.",
            "reference_scan_2D_OMNIFOLD_RUN_LOG_line37_ours_vs_data": {
                "50": 0.69, "100": 2.35, "180": 3.30, "205": 3.66},
            "per_comparison": ndf_check,
        },

        "results": results,

        "targets": {
            "data_vs_tune": {"quoted": 33.0,
                             "source": "3d-unfolding/3D_OMNIFOLD_RUN_LOG.md:112"},
            "ours_vs_tune": {"quoted": 26.5,
                             "source": "docs/analysis-note/sec_results.tex:167 "
                                       "(no other occurrence in the repo)"},
            "ours_vs_data": {"quoted": 3.661,
                             "source": "2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md "
                                       "headline table"},
        },
    }

    for key, tgt in receipt["targets"].items():
        got = results[key]["chi2_per_ndf"]
        q = tgt["quoted"]
        tgt["recomputed"] = got
        tgt["abs_diff"] = abs(got - q)
        # quoted to 3 significant figures -> agreement within half an ulp of
        # the quoted precision is an exact reproduction.
        half_ulp = 0.5 * 10 ** -(len(str(q).split(".")[1]))
        tgt["quoted_precision_half_ulp"] = half_ulp
        tgt["reproduces"] = bool(abs(got - q) <= half_ulp)

    # ---- console report ---------------------------------------------------
    def line(s=""):
        print(s)

    line("=" * 78)
    line("RECEIPT  -  2D (pT, p_par) chi^2/ndf vs GENIE MINERvA Tune v1")
    line("=" * 78)
    line(f"reported bins (ndf) : {n_rep} / {N}")
    line(f"cov condition number: {cond:.3e}   pinv keeps {n_sv_kept}/{n_rep} "
         f"singular values")
    line(f"bin-mapping control : mask==csv(xs>0): {mask_agrees_with_csv}; "
         f"max |csv/th2d - 1| = {map_reldev:.2e}")
    line("")
    line(f"{'comparison':<16} {'chi2':>12} {'chi2/ndf':>10} {'quoted':>8} "
         f"{'repro':>6}  {'pull mean/rms':>16}")
    for key in ["ours_vs_data", "data_vs_tune", "ours_vs_tune"]:
        r = results[key]
        t = receipt["targets"][key]
        line(f"{key:<16} {r['chi2']:>12.2f} {r['chi2_per_ndf']:>10.3f} "
             f"{t['quoted']:>8} {str(t['reproduces']):>6}  "
             f"{r['pull_mean']:>7.3f}/{r['pull_rms']:<8.3f}")
    line("")
    line("ndf check - rank-truncation scan of chi^2/205 (no cliff => "
         "ndf = n_reported holds):")
    for key in ["ours_vs_data", "data_vs_tune", "ours_vs_tune"]:
        vals = ndf_check[key]["chi2_per_ndf_at_points"]
        pts = ndf_check[key]["scan_points"]
        line(f"  {key:<16} " + "  ".join(
            f"r={r}:{v:.2f}" for r, v in zip(pts, vals)))
        nc = ndf_check[key]
        line(f"  {'':<16} monotonic={nc['monotonic_nondecreasing']}  "
             f"chi2 carried by smallest 1/10/25 eigen-modes = "
             f"{nc['frac_chi2_in_smallest_1_modes']*100:.2f}% / "
             f"{nc['frac_chi2_in_smallest_10_modes']*100:.2f}% / "
             f"{nc['frac_chi2_in_smallest_25_modes']*100:.2f}%  "
             f"(90% of chi2 needs "
             f"{nc['n_modes_to_reach_90pct_chi2_by_eigenvalue_rank']} modes by "
             f"eigenvalue rank, "
             f"{nc['n_modes_to_reach_90pct_chi2_by_contribution']} by "
             f"contribution)")
    line("")
    line("falsifiers (derived quantities that must be mutually consistent):")
    for key in ["ours_vs_data", "data_vs_tune", "ours_vs_tune"]:
        r = results[key]
        line(f"  {key:<16} sum ratio A/B = {r['ratio_A_over_B']:.4f}   "
             f"diag-only chi2/ndf = {r['chi2_per_ndf_diagonal_only']:.3f}   "
             f"off-diag inflation = {r['offdiag_inflation_factor']:.2f}x   "
             f"spectral-vs-pinv reldiff = {r['spectral_vs_pinv_reldiff']:.2e}")

    with open(args.out, "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=False)
    line("")
    line(f"wrote {args.out}")


if __name__ == "__main__":
    main()
