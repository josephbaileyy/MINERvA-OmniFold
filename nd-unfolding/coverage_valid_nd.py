#!/usr/bin/env python3
"""Split-sample truth-containment diagnostic (Agent C, WS1). REUSE-ONLY: consumes existing closure+bootstrap
toys as the EVALUATION ensemble and estimates the interval sigma INDEPENDENTLY, so it is not the
circular same-ensemble standardized-pull fraction that coverage_toy_nd.py/fps_extension_validation.py/
coverage_toys.py report (those are preserved as the Gaussianity/pull diagnostic).

Two independent-sigma variants are reported. Aggregate bin--toy cells are correlated within
each toy, so the script does NOT attach a naive binomial uncertainty to the aggregate:
  A) analytic: sigma_i = sqrt(diag(C)) from an INDEPENDENTLY estimated covariance (C_stat for the
     stat-only closure toys). Tests whether the independently estimated interval contains truth.
  B) split-ensemble: partition toys by predeclared seed parity into disjoint CALIBRATION (estimate
     sigma = std) and EVALUATION (count truth-containment) halves. No circularity.

Truth must be independent of the evaluation toys.  In NPZ mode it is reconstructed from the
unfluctuated closure input exactly as fps_extension_validation.py does (completeness=1).  ROOT-toy
mode requires an explicit independent ROOT:hist reference; the per-toy hTruth histogram is not a
valid substitute when the MC bootstrap also fluctuates it.

  python coverage_valid_nd.py --toys-glob 'cov_fps/res_toy_*.npz' --npz of_inputs_fps.npz \
      --cv <CVprod.root:hXSecND_flat> --cov uq_fps/corrected/uq_cov_stat_fps.root:hCov_statfps_reported \
      --tag fps --out coverage_valid_fps.json
"""
import argparse, glob, json, os, sys
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from xsec_nd import extract_cross_section_nd


def _toy_seed(path):
    if path.endswith(".npz"):
        d = np.load(path, allow_pickle=True)
        for k in ("seed", "toy_seed", "replica_id"):
            if k in d.files:
                return int(np.asarray(d[k]).item())
    # ROOT toys (or npz without an id key): trailing integer in the filename
    base = os.path.basename(path); digits = "".join(ch if ch.isdigit() else " " for ch in base).split()
    return int(digits[-1]) if digits else -1


def _load_cov_diag(spec):
    import ROOT
    path, key = spec.rsplit(":", 1)
    f = ROOT.TFile.Open(path)
    h = f.Get(key)
    if not h:
        raise SystemExit(f"[FAIL] missing {key} in {path}")
    n = h.GetNbinsX()
    diag = np.array([h.GetBinContent(i + 1, i + 1) for i in range(n)])
    f.Close()
    return diag


def _load_cv_flat(spec):
    import ROOT
    path, key = spec.rsplit(":", 1) if ":" in spec else (spec, "hXSecND_flat")
    f = ROOT.TFile.Open(path)
    h = f.Get(key)
    a = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    f.Close()
    return a


def _closure_truth(npz):
    d = np.load(npz, allow_pickle=True)
    ne = int(d["nedges"]); edges = [d[f"edges_{i}"] for i in range(ne)]
    bins = [np.asarray(e, float) for e in edges]
    m = d["pass_truth"].astype(bool)
    samp = np.column_stack([d["MCgen"][m, i] for i in range(d["MCgen"].shape[1])])
    refh, _ = np.histogramdd(samp, bins=bins, weights=d["w_truth"][m])
    xs, _ = extract_cross_section_nd(refh, np.ones_like(refh), d["flux"],
                                     float(d["data_pot"]), float(d["n_nucleons"]), edges)
    return xs.ravel(order="C")


def _th_flat(h):
    """Flatten a TH1/TH2 to a C-order 1D numpy vector (matches ravel(order='C'))."""
    if h.InheritsFrom("TH2"):
        nx, ny = h.GetNbinsX(), h.GetNbinsY()
        return np.array([[h.GetBinContent(ix + 1, iy + 1) for iy in range(ny)] for ix in range(nx)]).ravel(order="C")
    return np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])


def _load_root_toys(paths, toy_hist, truth_hist):
    """ROOT-mode toy loader. Return unfolded and stored per-toy truth arrays.

    The stored truth stack is retained only to audit whether the toy procedure fluctuated it; it
    is never averaged into the independent truth reference used for containment.
    """
    import ROOT
    X, T = [], []
    for p in paths:
        f = ROOT.TFile.Open(p)
        hu = f.Get(toy_hist); ht = f.Get(truth_hist)
        if not hu or not ht:
            raise SystemExit(f"[FAIL] {p}: missing {toy_hist} or {truth_hist}")
        X.append(_th_flat(hu)); T.append(_th_flat(ht))
        f.Close()
    return np.stack(X, 0), np.stack(T, 0)


def _conditional_toy_cluster_se(contained):
    """SE over independent toy-level bin fractions, conditional on calibrated widths.

    This retains arbitrary within-toy bin correlation.  It does not include uncertainty from
    estimating the calibration widths and is therefore diagnostic, not a global coverage error.
    """
    per_toy = np.asarray(contained, bool).mean(axis=1)
    return float(per_toy.std(ddof=1) / np.sqrt(per_toy.size)) if per_toy.size > 1 else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--toys-glob", required=True)
    ap.add_argument("--npz", default=None, help="of_inputs npz for the fixed closure truth (npz-toy mode)")
    ap.add_argument("--toy-hist", default=None, help="ROOT-toy mode: unfolded TH1/TH2 name (e.g. hXSec2D)")
    ap.add_argument("--truth-hist", default=None, help="ROOT-toy mode: truth TH1/TH2 name (e.g. hTruthXSec2D)")
    ap.add_argument("--fixed-truth", default=None,
                    help="ROOT-toy mode: independent unfluctuated ROOT:hist truth reference; required")
    ap.add_argument("--cv", default=None, help="CV product ROOT[:hist] to define reported bins (CV>0); "
                    "default uses truth>0")
    ap.add_argument("--cov", default=None, help="independent covariance ROOT:hist for variant A (e.g. C_stat)")
    ap.add_argument("--tag", default="nd")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    paths = sorted(glob.glob(a.toys_glob))
    if len(paths) < 4:
        raise SystemExit(f"[FAIL] need >=4 toys, found {len(paths)}")
    seeds = np.array([_toy_seed(p) for p in paths])
    if a.toy_hist:  # ROOT-toy mode (e.g. 2D closure toys)
        if not a.truth_hist:
            raise SystemExit("[FAIL] --toy-hist requires --truth-hist")
        if not a.fixed_truth:
            raise SystemExit(
                "[FAIL] ROOT-toy mode requires --fixed-truth ROOT:HIST. The stored per-toy "
                "truth histogram may share the MC-bootstrap fluctuation and must not be averaged "
                "over the scored ensemble.")
        X, toy_truth = _load_root_toys(paths, a.toy_hist, a.truth_hist)
        truth = _load_cv_flat(a.fixed_truth)
        truth_src = "independent unfluctuated truth from " + a.fixed_truth
    else:           # npz-toy mode (FPS/ND)
        if not a.npz:
            raise SystemExit("[FAIL] npz-toy mode requires --npz")
        X = np.stack([np.load(p, allow_pickle=True)["xsec_flat"] for p in paths], 0)
        truth = _closure_truth(a.npz)
        truth_src = "fixed closure truth from " + a.npz
    if X.shape[1] != truth.size:
        raise SystemExit(f"[FAIL] toy nbins {X.shape[1]} != truth {truth.size}")

    rep = (_load_cv_flat(a.cv) > 0) if a.cv else (truth > 0)
    if rep.size != truth.size:
        raise SystemExit(f"[FAIL] reported mask {rep.size} != {truth.size}")
    Xr, tr = X[:, rep], truth[rep]
    N, nb = Xr.shape
    out = {"tag": a.tag, "n_toys": int(N), "n_reported_bins": int(nb),
           "estimator_seed_fixed": 42, "toy_seeds_manifest": sorted(int(s) for s in seeds),
           "truth": truth_src, "note": "REUSE-ONLY; existing toys = evaluation ensemble"}
    if a.toy_hist:
        stored_range = np.ptp(toy_truth, axis=0)
        out["stored_toy_truth_audit"] = {
            "hist": a.truth_hist,
            "max_abs_range": float(stored_range.max()),
            "n_varying_bins": int(np.count_nonzero(stored_range)),
            "note": "audit only; never used as the independent containment truth",
        }

    # ---- Variant A: independent analytic covariance ----
    if a.cov:
        diag = _load_cov_diag(a.cov)
        if diag.size != nb:
            raise SystemExit(f"[FAIL] cov diag {diag.size} != reported {nb}")
        sig = np.sqrt(np.clip(diag, 0, None))
        good = sig > 0
        contained = (np.abs(Xr[:, good] - tr[good]) <= sig[good])  # (N, nbin)
        per_bin = contained.mean(axis=0)
        agg = float(contained.mean())          # over all (toy,bin) pairs
        out["variant_A_independent_cov"] = {
            "cov": a.cov, "n_bins_used": int(good.sum()),
            "coverage_aggregate": agg,
            "conditional_toy_cluster_se": _conditional_toy_cluster_se(contained),
            "coverage_bin_median": float(np.median(per_bin)),
            "coverage_bin_mean": float(per_bin.mean()),
            "interpretation": "independently-estimated (C_stat) +/-1sigma interval containing the fixed truth "
                              "across the stat-closure toys; nominal 68.27%",
        }
        print(f"[A] independent-cov containment aggregate = {100*agg:.2f}% "
              f"(bins {int(good.sum())}, toys {N}); bin-median {100*np.median(per_bin):.2f}%; "
              "no naive aggregate binomial error")

    # ---- Variant B: split calibration / evaluation (disjoint by seed parity) ----
    calib = (seeds % 2 == 0); evalm = ~calib
    if calib.sum() >= 2 and evalm.sum() >= 2:
        sig_b = Xr[calib].std(axis=0, ddof=1)
        good = sig_b > 0
        Ev = Xr[np.ix_(evalm, good)]
        contained = (np.abs(Ev - tr[good]) <= sig_b[good])
        agg = float(contained.mean()); per_bin = contained.mean(axis=0)
        ne = int(evalm.sum())
        out["variant_B_split_ensemble"] = {
            "n_calib": int(calib.sum()), "n_eval": ne, "n_bins_used": int(good.sum()),
            "coverage_aggregate": agg,
            "conditional_toy_cluster_se": _conditional_toy_cluster_se(contained),
            "coverage_bin_median": float(np.median(per_bin)), "coverage_bin_mean": float(per_bin.mean()),
            "interpretation": "sigma from disjoint calibration toys; containment counted on untouched "
                              "evaluation toys; nominal 68.27%",
        }
        print(f"[B] split-ensemble containment aggregate = {100*agg:.2f}% "
              f"(calib {int(calib.sum())}, eval {ne}); bin-median {100*np.median(per_bin):.2f}%; "
              "no naive aggregate binomial error")
    else:
        out["variant_B_split_ensemble"] = {"skipped": "insufficient toys per parity class"}

    # ---- preserved circular diagnostic (for comparison, explicitly labeled) ----
    sig_all = Xr.std(axis=0, ddof=1); good = sig_all > 0
    # Reproduce the legacy ROOT-toy pull diagnostic against its all-toy mean only for comparison;
    # containment variants above always use the explicit independent truth.
    circular_truth = toy_truth.mean(axis=0)[rep] if a.toy_hist else tr
    pull = np.abs(Xr[:, good] - circular_truth[good]) / sig_all[good]
    out["circular_pull_diagnostic_NOT_coverage"] = {
        "same_ensemble_pull_fraction": float((pull <= 1.0).mean()),
        "mean_abs_r": float(pull.mean()), "sqrt_2_over_pi": float(np.sqrt(2/np.pi)),
        "note": "std from the SAME toys scored against themselves; ~0.68 by construction; Gaussianity check only",
    }
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[wrote] {a.out}")


if __name__ == "__main__":
    main()
