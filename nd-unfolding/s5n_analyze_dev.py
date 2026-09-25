#!/usr/bin/env python3
"""The s5n Stage-1 development receipt: controls C0-C8 of ``docs/orchestration/state/s5n/contract.json``.

Reads the committed-table products under the s5n namespace and writes one JSON receipt:

* C0 -- the purity baseline product against the s5c product it must reproduce (max |diff|).
* C1 -- refinement evidence on every negweight-refined product: presence, refined/signed sum, clipped
  fraction and mass, effective sizes.
* C2 -- repeat and estimator-seed bitwise equality; the row-permutation shift over the development sigma.
* C3/C4/C5 -- per grid point, per reported functional: mean relative residual (f_hat - f_true)/f_true,
  its standard error and t, the mean and standard deviation of the pull (f_hat - f_true)/sigma, the
  empirical 68%/95% coverage of f_hat +- sigma and +- 1.96 sigma, and the normal-model coverage from
  the pull's mean and spread; C3's frozen pass criterion; the purity D1 result on the same functionals.
* C6 -- sigma from the declared bootstrap; the nominal ensemble spread over sigma.
* C7 -- real data: negweight-refined against purity on the npz path (method sensitivity), and the
  driver path against the npz path.
* C8 -- the signal-only reference, for description only.

MEASURES: development behaviour of family N. CANNOT AUTHORIZE: a coverage verdict (validation seeds
only), a measured bias on data, or any change to the frozen contract by itself.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import s5c_assemble
import s5c_coverage as sc

HIGH_W = ["EW5", "EW11", "EW17", "EW23", "EW29", "EW35", "EW41"]
T_CRIT = 3.6  # contract C3: two-sided 0.05/153 Bonferroni


def load(path: Path) -> dict:
    z = np.load(path, allow_pickle=False)
    out = {"xs": np.asarray(z["xsec_flat"], float), "meta": json.loads(str(z["meta"]))}
    if "xtrue_flat" in z.files:
        out["xt"] = np.asarray(z["xtrue_flat"], float)
    return out


def phi(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + np.vectorize(math.erf)(np.asarray(x) / math.sqrt(2.0)))


def point_stats(files: list[Path], U: np.ndarray, sig: np.ndarray, names: list[str]) -> dict:
    rel, pull, ev = [], [], []
    for f in files:
        p = load(f)
        fh, ft = U @ p["xs"], U @ p["xt"]
        rel.append((fh - ft) / ft)
        pull.append((fh - ft) / sig)
        ev.append(p["meta"].get("refinement", {}))
    rel, pull = np.array(rel), np.array(pull)
    n = rel.shape[0]
    mean, se = rel.mean(0), rel.std(0, ddof=1) / math.sqrt(n)
    t = mean / se
    mu, sd = pull.mean(0), pull.std(0, ddof=1)
    cov68, cov95 = np.mean(np.abs(pull) <= 1.0, 0), np.mean(np.abs(pull) <= 1.96, 0)
    norm68 = phi((1.0 - mu) / sd) - phi((-1.0 - mu) / sd)
    norm95 = phi((1.96 - mu) / sd) - phi((-1.96 - mu) / sd)
    worst = np.argsort(-np.abs(t))[:10]
    return {
        "n_experiments": n,
        "max_abs_t": float(np.max(np.abs(t))), "n_abs_t_gt_crit": int(np.sum(np.abs(t) > T_CRIT)),
        "n_abs_t_gt_4": int(np.sum(np.abs(t) > 4)),
        "pooled_cov68": float(np.mean(np.abs(pull) <= 1.0)), "pooled_cov95": float(np.mean(np.abs(pull) <= 1.96)),
        "min_cov68": float(cov68.min()), "min_cov95": float(cov95.min()),
        "normal_model_cov68_min": float(np.min(norm68)), "normal_model_cov68_median": float(np.median(norm68)),
        "normal_model_cov95_min": float(np.min(norm95)), "normal_model_cov95_median": float(np.median(norm95)),
        "pull_sd_median": float(np.median(sd)), "pull_sd_min": float(sd.min()), "pull_sd_max": float(sd.max()),
        "pull_mean_abs_max": float(np.max(np.abs(mu))),
        "worst_t": [{"name": names[i], "mean_rel_pct": 100 * float(mean[i]), "se_rel_pct": 100 * float(se[i]),
                     "t": float(t[i]), "mean_pull": float(mu[i]), "pull_sd": float(sd[i])} for i in worst],
        "high_W": {nm: {"mean_rel_pct": 100 * float(mean[names.index(nm)]), "se_rel_pct": 100 * float(se[names.index(nm)]),
                        "mean_pull": float(mu[names.index(nm)])} for nm in HIGH_W},
        "per_functional": {"mean_rel": mean.tolist(), "se_rel": se.tolist(), "mean_pull": mu.tolist(),
                           "pull_sd": sd.tolist(), "cov68": cov68.tolist(), "cov95": cov95.tolist(),
                           "normal_cov68": norm68.tolist(), "normal_cov95": norm95.tolist()},
        "refinement": evidence_summary(ev),
    }


def evidence_summary(ev: list[dict]) -> dict:
    ran = [e for e in ev if e.get("ran")]
    if not ran:
        return {"n_products": len(ev), "n_refined": 0}
    col = lambda k: np.array([e[k] for e in ran], float)  # noqa: E731
    out = {"n_products": len(ev), "n_refined": len(ran)}
    for k in ("refined_over_signed", "clipped_fraction", "clipped_signed_mass", "n_eff_refined",
              "n_eff_signed_abs", "sum_negative", "seconds"):
        v = col(k)
        out[k] = {"min": float(v.min()), "median": float(np.median(v)), "max": float(v.max())}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--s5c-contract", type=Path, required=True)
    ap.add_argument("--ns", type=Path, required=True, help="the s5n namespace (runs/ below it)")
    ap.add_argument("--s5c-d1-product", type=Path, required=True, help="the s5c product C0 reproduces")
    ap.add_argument("--s5c-d1-summary", type=Path, required=True)
    ap.add_argument("--s5c-driver-purity", required=True, help="the s5c F2 driver central value (purity)")
    ap.add_argument("--n-sigma", type=int, default=200)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    runs = a.ns / "runs"
    U, names = sc.reported_functionals(json.loads(a.s5c_contract.read_text()))
    C = sc.stat_covariance(U, runs / "sigma", 1, a.n_sigma)
    sig = np.sqrt(np.diag(C))
    rec = {"schema": "s5n-dev/1", "functional_names": names, "sigma": sig.tolist(),
           "sigma_replicas": a.n_sigma, "controls": {}}
    ctl = rec["controls"]

    c0 = load(runs / "c0" / "c0_purity_d1_split_s4.npz")
    ref = np.load(a.s5c_d1_product, allow_pickle=False)
    ctl["C0"] = {"max_abs_diff_xsec": float(np.max(np.abs(c0["xs"] - ref["xsec_flat"]))),
                 "max_abs_diff_xtrue": float(np.max(np.abs(c0["xt"] - ref["xtrue_flat"]))),
                 "reference": str(a.s5c_d1_product)}
    ctl["C0"]["pass"] = ctl["C0"]["max_abs_diff_xsec"] == 0.0 and ctl["C0"]["max_abs_diff_xtrue"] == 0.0

    c2 = {k: load(runs / "c2" / f"{k}.npz") for k in ("c2_rep_a", "c2_rep_b", "c2_seed43", "c2_perm1")}
    fa = U @ c2["c2_rep_a"]["xs"]
    ctl["C2"] = {
        "repeat_bitwise_equal": bool(np.array_equal(c2["c2_rep_a"]["xs"], c2["c2_rep_b"]["xs"])),
        "seed43_bitwise_equal": bool(np.array_equal(c2["c2_rep_a"]["xs"], c2["c2_seed43"]["xs"])),
        "permutation_max_shift_over_sigma": float(np.max(np.abs(U @ c2["c2_perm1"]["xs"] - fa) / sig)),
        "refinement_params": c2["c2_rep_a"]["meta"]["refinement"].get("classifier_params"),
        "seed43_refinement_random_state": c2["c2_seed43"]["meta"]["refinement"].get("classifier_params", {}).get("random_state"),
        "construction_equivalence": "satisfied by construction: s5n_pseudo.refine calls unfold_2d_omnifold_unbinned.refine_stay_positive itself (no second implementation); test_s5n_cluster.py checks the call bitwise against a direct call",
    }
    ctl["C2"]["pass"] = (ctl["C2"]["repeat_bitwise_equal"] and ctl["C2"]["seed43_bitwise_equal"]
                         and ctl["C2"]["permutation_max_shift_over_sigma"] <= 0.05)

    d1 = json.loads(a.s5c_d1_summary.read_text())["groups"]["split_F2"]
    points = {}
    for tag, pattern in (("C3_nominal", "nominal_a0_s*.npz"), ("C4_eavail_shape", "eavail_shape_a1_s*.npz"),
                         ("C5_q3_given_eavail_w", "q3_given_eavail_w_a0.3_s*.npz")):
        files = sorted((runs / "dev").glob(pattern))
        points[tag] = point_stats(files, U, sig, names)
    s3 = points["C3_nominal"]
    pf = s3["per_functional"]
    big = [i for i in range(len(names)) if abs(pf["mean_rel"][i] / pf["se_rel"][i]) > 3 and abs(pf["mean_pull"][i]) > 0.5]
    s3["criterion"] = {"max_abs_t": s3["max_abs_t"], "t_crit": T_CRIT, "n_over_half_sigma_with_t_gt_3": len(big),
                       "pass": s3["max_abs_t"] <= T_CRIT and not big}
    s3["purity_D1_same_functionals"] = {nm: {"negweight_refined_mean_rel_pct": s3["high_W"][nm]["mean_rel_pct"],
                                             "purity_D1_mean_rel_pct": 100 * d1["mean_rel"][names.index(nm)],
                                             "purity_D1_se_rel_pct": 100 * d1["se_rel"][names.index(nm)]} for nm in HIGH_W}
    rec["grid"] = points
    ctl["C3"] = s3["criterion"]
    ctl["C6"] = {"sigma_rel_median": float(np.median(sig / np.abs(U @ c2["c2_rep_a"]["xt"]))),
                 "nominal_pull_sd_median": s3["pull_sd_median"], "nominal_pull_sd_min": s3["pull_sd_min"],
                 "nominal_pull_sd_max": s3["pull_sd_max"],
                 "pull_sd_sampling_se_approx": 1.0 / math.sqrt(2.0 * (s3["n_experiments"] - 1)),
                 "sigma_replica_count": a.n_sigma}

    dp, dn = load(runs / "c7" / "data_purity.npz"), load(runs / "c7" / "data_negweight.npz")
    fp, fn = U @ dp["xs"], U @ dn["xs"]
    drv = U @ s5c_assemble.read_flat(str(runs / "c7" / "xsec_5d_driver_negweight_F2.root"))
    drv_p = U @ s5c_assemble.read_flat(a.s5c_driver_purity)
    rd = (fn - fp) / fp
    order = np.argsort(-np.abs(rd))[:12]
    ctl["C7"] = {
        "label": "METHOD SENSITIVITY on the real data (negweight-refined minus purity, same estimator and inputs); NOT a measured bias",
        "rel_diff_median_abs_pct": 100 * float(np.median(np.abs(rd))), "rel_diff_max_abs_pct": 100 * float(np.max(np.abs(rd))),
        "high_W_rel_diff_pct": {nm: 100 * float(rd[names.index(nm)]) for nm in HIGH_W},
        "largest": [{"name": names[i], "rel_diff_pct": 100 * float(rd[i]),
                     "diff_over_dev_sigma_scale_only": float((fn[i] - fp[i]) / sig[i])} for i in order],
        "total_rel_diff_pct": 100 * float(rd[names.index("total_integrated")]),
        "refinement_data": dn["meta"]["refinement"],
        "driver_vs_npz_negweight_max_abs_rel_pct": 100 * float(np.max(np.abs(drv / fn - 1.0))),
        "driver_vs_npz_purity_max_abs_rel_pct": 100 * float(np.max(np.abs(drv_p / fp - 1.0))),
        "scale_note": "diff_over_dev_sigma uses the development (half-MC pseudo-data) sigma as a SCALE only; the data's own statistical sigma is built in Stage 2",
    }
    c8 = [load(f) for f in sorted((runs / "c8").glob("c8_signal_only_s*.npz"))]
    if c8:
        r8 = np.array([(U @ p["xs"] - U @ p["xt"]) / (U @ p["xt"]) for p in c8])
        ctl["C8"] = {"label": "signal-only reference: description only, not background-inclusive closure evidence",
                     "n": len(c8), "max_abs_mean_rel_pct": 100 * float(np.max(np.abs(r8.mean(0)))),
                     "high_W_mean_rel_pct": {nm: 100 * float(r8.mean(0)[names.index(nm)]) for nm in HIGH_W}}
    all_nw = [p for p in (runs / "dev").glob("*.npz")] + [runs / "c7" / "data_negweight.npz"] + \
        [runs / "c2" / f"{k}.npz" for k in c2] + list((runs / "sigma").glob("boot_b*.npz"))
    missing = [str(p) for p in all_nw if not load(p)["meta"].get("refinement", {}).get("ran")]
    ctl["C1"] = {"negweight_products_checked": len(all_nw), "without_refinement_evidence": missing,
                 "driver_evidence": json.loads((runs / "c7" / "ev_driver_negweight.json").read_text()).get("problems"),
                 "pass": not missing}
    a.out.write_text(json.dumps(rec, indent=1) + "\n")
    summary = {k: v.get("pass") for k, v in ctl.items() if isinstance(v, dict) and "pass" in v}
    print(json.dumps(summary))
    for tag, s in points.items():
        print(tag, json.dumps({k: s[k] for k in ("n_experiments", "max_abs_t", "n_abs_t_gt_crit", "pooled_cov68",
                                                  "pooled_cov95", "min_cov68", "min_cov95", "pull_sd_median",
                                                  "normal_model_cov68_min", "normal_model_cov95_min")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
