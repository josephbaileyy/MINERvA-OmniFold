"""KNOWN_ISSUES 85 diagnostic: compare the data-only bootstrap of one toy (arm B), fresh-Poisson toys
(arm T) and the real-data data-only bootstrap, per reported bin, and apply the committed decision rule
(docs/orchestration/DECISION-RULE-20261006-ki85-bootstrap-diagnostic.md).

    python ki85_compare.py --out ki85_result.json      (Perlmutter, root_6_28 environment)

The statistics and the rule are the pure functions below; main() only reads the ROOT files.
"""
import argparse, glob, json, math, re, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUTROOT = "/pscratch/sd/j/josephrb/ki85-diag-20261006"
REALBOOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/boot_data"
INTERIM = REPO / "docs/orchestration/state/coverage-2d-20261005/interim.npz"
PURITY = REPO / "docs/orchestration/state/ki84-adopt-20261006/purity_fdata.json"
N_RESAMPLE = 2000
RESAMPLE_SEED = 20_261_006


def rel_spread(X):
    """Per-bin std (ddof = 1) / mean over replicas; X is (n_replicas, n_bins)."""
    return X.std(axis=0, ddof=1) / X.mean(axis=0)


def per_bin_ratios(XB, XT, XR, corr):
    """rho1 = sB/sT, rho2 = (sB/corr)/sR, rhoT = (sT/corr)/sR, each per bin."""
    sB, sT, sR = rel_spread(XB), rel_spread(XT), rel_spread(XR)
    return {"rho1": sB / sT, "rho2": sB / corr / sR, "rhoT": sT / corr / sR}


def summary(x):
    return {"median": float(np.median(x)), "p16": float(np.percentile(x, 16)),
            "p84": float(np.percentile(x, 84))}


def median_intervals(XB, XT, XR, corr, n=N_RESAMPLE, seed=RESAMPLE_SEED, level=0.95):
    """95 % intervals of the three medians, resampling replicas within each arm."""
    rng = np.random.default_rng(seed)
    meds = {k: [] for k in ("rho1", "rho2", "rhoT")}
    for _ in range(n):
        r = per_bin_ratios(XB[rng.integers(0, len(XB), len(XB))], XT[rng.integers(0, len(XT), len(XT))],
                           XR[rng.integers(0, len(XR), len(XR))], corr)
        for k in meds:
            meds[k].append(np.median(r[k]))
    a = (1 - level) / 2
    return {k: [float(np.quantile(v, a)), float(np.quantile(v, 1 - a))] for k, v in meds.items()}


def classify(M1, M1_ci, M2, MT):
    """The committed rule, steps 0-3. Returns (outcome, share of the log-gap attributed to (a))."""
    share = math.log(M1) / math.log(1 / MT) if 0 < MT < 1 and M1 > 0 else float("nan")
    if not 0.50 <= MT <= 0.80:
        return "premise not reproduced", share
    if 0.90 <= M1_ci[0] and M1_ci[1] <= 1.10 and M2 <= 0.80:
        return "consistent with (b): the bootstrap is faithful on same-event pseudo-data", share
    if M1 >= 1.30 and M1_ci[0] > 1.20 and 0.90 <= M2 <= 1.10:
        return "consistent with (a): the production data bootstrap over-scatters", share
    return "mixed", share


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sys.path.insert(0, "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq")
    import analyze_uq as au
    import ROOT
    ROOT.gROOT.SetBatch(True)
    d = np.load(INTERIM)
    rep = d["reported"].ravel(order="C")
    pur = np.array(json.loads(PURITY.read_text())["purity_reco"]).ravel(order="C")
    r = (d["prod_mean"] / np.where(d["T"] > 0, d["T"], 1)).ravel(order="C")
    corr = np.sqrt(r[rep] / pur[rep])

    def load(pattern, expect):
        files = sorted(glob.glob(pattern), key=lambda p: int(re.findall(r"(\d+)\.root$", p)[0]))
        files = [f for f in files if Path(f + ".done").exists() or "boot_data" in f]
        if len(files) != expect:
            raise SystemExit(f"[FAIL] {pattern}: {len(files)} files, expected {expect}")
        X = []
        for p in files:
            f = ROOT.TFile.Open(p)
            X.append(au.th2_to_array(f.Get("hXSec2D")).ravel(order="C")[rep])
            f.Close()
        return np.array(X), files
    XB, fb = load(f"{OUTROOT}/armB/boot*.root", 50)
    XT, ft = load(f"{OUTROOT}/armT/toy*.root", 50)
    XR, fr = load(f"{REALBOOT}/2d_xsec_MEFHC_5iter_lgbm_boot*.root", 200)
    ratios = per_bin_ratios(XB, XT, XR, corr)
    ci = median_intervals(XB, XT, XR, corr)
    M = {k: float(np.median(v)) for k, v in ratios.items()}
    outcome, share = classify(M["rho1"], ci["rho1"], M["rho2"], M["rhoT"])
    out = {"rule": "docs/orchestration/DECISION-RULE-20261006-ki85-bootstrap-diagnostic.md",
           "n": {"armB": len(fb), "armT": len(ft), "realboot": len(fr), "bins": int(rep.sum())},
           "size_correction_sqrt_r_over_p": summary(corr),
           "sigma_B_over_sigma_T": {**summary(ratios["rho1"]), "median_ci95": ci["rho1"]},
           "sigma_B_over_sigma_realboot_corrected": {**summary(ratios["rho2"]), "median_ci95": ci["rho2"]},
           "sigma_T_over_sigma_realboot_corrected": {**summary(ratios["rhoT"]), "median_ci95": ci["rhoT"]},
           "median_rel_spread_pct": {"armB": float(100 * np.median(rel_spread(XB))),
                                     "armT": float(100 * np.median(rel_spread(XT))),
                                     "realboot": float(100 * np.median(rel_spread(XR)))},
           "outcome": outcome, "share_of_log_gap_attributed_to_a": share,
           "statement": "No outcome changes the quoted band (VL170) or any printed number before publication."}
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
