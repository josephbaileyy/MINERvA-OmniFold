"""Identifiability of every predeclared distortion at the historical pseudodata size (Amendment 1).

For each distortion: a GBDT two-sample classifier on RECO quantities (muon p_T, p_par, reco E_avail,
reco q3, stored-token count and stored-token energy sum) separating a distorted sample from an
undistorted one, both drawn from pool T at 600,111 events, 50/50 train/test, statistic = weighted
test AUC - 0.5. The null comes from 20 equal-model splits (two undistorted samples of the same
size). A distortion whose statistic lies inside the null's 95 % range is reported as NOT
DISTINGUISHABLE AT THIS SAMPLE SIZE -- never as unrecoverable.

Two things the protocol's null does not by itself cover, both measured here rather than assumed:

* a truth distortion makes the probe sample WEIGHTED, which inflates the sampling variance of the
  AUC. The null is therefore also reported scaled by sqrt((1/ESS_ref + 1/ESS_probe) / (1/n + 1/n))
  from the effective sample sizes of the test weights, and the verdict is given against both the
  raw and the scaled threshold;
* that scaling is checked directly for the most weight-dispersed distortions by a PERMUTATION null:
  the same distortion weights, randomly permuted among the probe events (the same weight
  distribution, no dependence on the event), five splits each.

Also reported per distortion: the reco E_avail L1 distance in the endpoint's seven bins, both
between the two samples and at the population level over all of pool T, and the truth-level
injected L1 -- the size of the thing an estimator would have to recover.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

import common as cm
import distortions as dist
import replicates as rp

scm = cm.scm
SAMPLE = cm.HISTORICAL_SIZES["pseudo"]
FEATURES = ("pt", "ppar", "eavail", "q3", "tok_sumE", "tok_n")
HGB_PARAMS = dict(learning_rate=0.1, max_iter=200, max_leaf_nodes=31, min_samples_leaf=200,
                  early_stopping=False)
NULL_SPLITS = 20
PERMUTATION_SPLITS = 5
CLASS_TOTAL = 1_000_000.0


def feature_matrix(reco: dict[str, np.ndarray]) -> np.ndarray:
    """The classifier's reco features, with any non-finite entry filled by its column median."""
    feats = dist.reco_features(reco)
    X = np.stack([feats[k] for k in FEATURES], axis=1)
    for j in range(X.shape[1]):
        col = X[:, j]
        bad = ~np.isfinite(col)
        if bad.any():
            col[bad] = float(np.median(col[~bad]))
    return X


def ess(w: np.ndarray) -> float:
    w = np.asarray(w, float)
    return float(w.sum() ** 2 / (w * w).sum())


def two_sample_auc(X0: np.ndarray, w0: np.ndarray, X1: np.ndarray, w1: np.ndarray, seed: int
                   ) -> dict[str, Any]:
    """Weighted test AUC of a HistGradientBoosting classifier on a 50/50 train/test split."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics import roc_auc_score
    X = np.concatenate([X0, X1])
    y = np.concatenate([np.zeros(len(X0)), np.ones(len(X1))])
    w = np.concatenate([w0 * (CLASS_TOTAL / w0.sum()), w1 * (CLASS_TOTAL / w1.sum())])
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    half = len(idx) // 2
    tr, te = idx[:half], idx[half:]
    fit, val = tr[:int(0.8 * len(tr))], tr[int(0.8 * len(tr)):]
    t0 = time.perf_counter()
    model = HistGradientBoostingClassifier(random_state=seed, **HGB_PARAMS)
    model.fit(X[fit], y[fit], sample_weight=w[fit])
    p_te = model.decision_function(X[te])
    p_val = model.decision_function(X[val])
    auc = float(roc_auc_score(y[te], p_te, sample_weight=w[te]))
    return {"auc": auc, "auc_minus_half": auc - 0.5,
            "auc_validation": float(roc_auc_score(y[val], p_val, sample_weight=w[val])) - 0.5,
            "n_train": int(len(fit)), "n_test": int(len(te)),
            "ess_test_class0": ess(w[te][y[te] == 0]), "ess_test_class1": ess(w[te][y[te] == 1]),
            "n_test_class0": int((y[te] == 0).sum()), "n_test_class1": int((y[te] == 1).sum()),
            "seconds": time.perf_counter() - t0}


def l1_on_endpoint(x0: np.ndarray, w0: np.ndarray, x1: np.ndarray, w1: np.ndarray) -> float:
    sc = cm.historical()["sc"]
    h0 = sc._histogram(x0, w0, cm.ENDPOINT_EDGES)
    h1 = sc._histogram(x1, w1, cm.ENDPOINT_EDGES)
    return float(np.abs(h1 / h1.sum() - h0 / h0.sum()).sum())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--prepare", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--null-splits", type=int, default=NULL_SPLITS)
    ap.add_argument("--only", nargs="*", default=None, help="distortion ids (default: all)")
    args = ap.parse_args()
    t0 = time.perf_counter()
    prep = json.loads(args.prepare.read_text())
    cache = cm.load_cache(args.cache, prep["caches"]["T"]["sha256"])
    reg = dist.registry()
    chosen = list(reg) if args.only is None else list(args.only)

    design = rp.ReplicateDesign("T", "E1-identifiability", n_prior=SAMPLE, n_pseudo=SAMPLE)
    reps, draw_record = rp.draw_replicates(design, [0], cache["rows"], cache["identity"])
    ref = cm.take(cache, reps[0].prior_rows)
    probe = cm.take(cache, reps[0].pseudo_rows)
    m_ref, m_probe = ref["pass_reco"], probe["pass_reco"]
    X_ref = feature_matrix(cm.reco_view(ref, m_ref))
    w_ref = ref["w_reco"][m_ref]
    truth_probe = cm.truth_view(probe)
    pool_truth = cm.truth_view(cache)
    pool_reco_mask = cache["pass_reco"]

    # population-level (all of pool T) undistorted spectra, for the L1 references
    sc = cm.historical()["sc"]
    pool_reco_eav = cache["reco"][pool_reco_mask, 2]
    pool_w_reco = cache["w_reco"][pool_reco_mask]
    pool_truth_eav = cache["truth"][:, 2]

    results: dict[str, Any] = {}

    def run_one(name: str, dst: dist.Distortion | None, seed: int,
                permute: np.random.Generator | None = None) -> dict[str, Any]:
        if dst is None or dst.kind == "truth_weight":
            w = (np.ones(probe["rows"].size) if dst is None
                 else dist.normalize_unit_mean(dst.truth_weight(truth_probe)))
            if permute is not None:
                w = w[permute.permutation(w.size)]
            reco_p = cm.reco_view(probe, m_probe)
            w_probe = probe["w_reco"][m_probe] * w[m_probe]
        else:
            noise = (dist.token_noise(probe["identity"][m_probe]) if dst.family == "R3" else None)
            reco_p = dst.transform(cm.reco_view(probe, m_probe), noise)
            w_probe = probe["w_reco"][m_probe]
        X_probe = feature_matrix(reco_p)
        out = two_sample_auc(X_ref, w_ref, X_probe, w_probe, seed)
        out["sample_reco_eavail_l1"] = l1_on_endpoint(X_ref[:, 2], w_ref, X_probe[:, 2], w_probe)
        return out

    # ---- the null: equal-model splits ------------------------------------------------------
    null_design = rp.ReplicateDesign("T", "E1-identifiability-null", n_prior=SAMPLE,
                                     n_pseudo=SAMPLE, disjoint=False)
    null_reps, null_record = rp.draw_replicates(null_design, list(range(args.null_splits)),
                                                cache["rows"], cache["identity"])
    null = []
    for rep in null_reps:
        a = cm.take(cache, rep.prior_rows)
        b = cm.take(cache, rep.pseudo_rows)
        ma, mb = a["pass_reco"], b["pass_reco"]
        Xa = feature_matrix(cm.reco_view(a, ma))
        Xb = feature_matrix(cm.reco_view(b, mb))
        rec = two_sample_auc(Xa, a["w_reco"][ma], Xb, b["w_reco"][mb],
                             seed=7_000 + rep.replicate)
        rec["sample_reco_eavail_l1"] = l1_on_endpoint(Xa[:, 2], a["w_reco"][ma], Xb[:, 2],
                                                      b["w_reco"][mb])
        null.append(rec)
        print(f"[ident] null {rep.replicate:2d} AUC-0.5={rec['auc_minus_half']:+.5f} "
              f"L1={rec['sample_reco_eavail_l1']:.5f} {rec['seconds']:.0f}s", flush=True)
    stat = np.array([r["auc_minus_half"] for r in null])
    null_summary = {"splits": len(null), "mean": float(stat.mean()), "sd": float(stat.std(ddof=1)),
                    "min": float(stat.min()), "max": float(stat.max()),
                    "q2.5": float(np.percentile(stat, 2.5)),
                    "q97.5": float(np.percentile(stat, 97.5)),
                    "reco_eavail_l1_mean": float(np.mean([r["sample_reco_eavail_l1"]
                                                          for r in null])),
                    "reco_eavail_l1_max": float(np.max([r["sample_reco_eavail_l1"] for r in null])),
                    "runs": null, "draws": null_record}
    n_test = float(np.mean([r["n_test"] for r in null])) / 2.0

    # ---- every distortion -------------------------------------------------------------------
    for i, name in enumerate(chosen):
        d = reg[name]
        rec = run_one(name, d, seed=11_000 + i)
        inflate = float(np.sqrt(((1.0 / rec["ess_test_class0"] + 1.0 / rec["ess_test_class1"])
                                 / (2.0 / n_test))))
        scaled = null_summary["mean"] + inflate * (null_summary["q97.5"] - null_summary["mean"])
        if d.kind == "truth_weight":
            w_pool = dist.normalize_unit_mean(d.truth_weight(pool_truth))
            pop_reco_l1 = l1_on_endpoint(pool_reco_eav, pool_w_reco, pool_reco_eav,
                                         pool_w_reco * w_pool[pool_reco_mask])
            pop_truth_l1 = l1_on_endpoint(pool_truth_eav, cache["w_truth"], pool_truth_eav,
                                          cache["w_truth"] * w_pool)
            weight_summary = scm.weight_summary(w_pool)
        else:
            noise = (dist.token_noise(cache["identity"][pool_reco_mask])
                     if d.family == "R3" else None)
            moved = d.transform(cm.reco_view(cache, pool_reco_mask), noise)
            pop_reco_l1 = l1_on_endpoint(pool_reco_eav, pool_w_reco, moved["eavail"], pool_w_reco)
            pop_truth_l1 = 0.0
            weight_summary = None
        rec.update({
            "distortion": d.spec(), "content_hash": d.content_hash(),
            "predeclared": dict(d.params).get("predeclared", True),
            "null_inflation_factor_from_ess": inflate,
            "threshold_raw_q97.5": null_summary["q97.5"], "threshold_ess_scaled": scaled,
            "distinguishable_vs_raw_null": bool(rec["auc_minus_half"] > null_summary["q97.5"]),
            "distinguishable_vs_scaled_null": bool(rec["auc_minus_half"] > scaled),
            "population_reco_eavail_l1": pop_reco_l1,
            "population_truth_eavail_injected_l1": pop_truth_l1,
            "distortion_weight_summary": weight_summary})
        results[name] = rec
        print(f"[ident] {name:22s} AUC-0.5={rec['auc_minus_half']:+.5f} "
              f"thr={scaled:.5f} recoL1={pop_reco_l1:.4f} truthL1={pop_truth_l1:.4f} "
              f"{'DISTINGUISHABLE' if rec['distinguishable_vs_scaled_null'] else 'not-dist.'} "
              f"{rec['seconds']:.0f}s", flush=True)

    # ---- permutation null for the most weight-dispersed truth distortions -------------------
    dispersion = sorted(((results[n]["ess_test_class1"] / results[n]["n_test_class1"], n)
                         for n in results if reg[n].kind == "truth_weight"))
    permutation: dict[str, Any] = {}
    for _ess_frac, name in dispersion[:2]:
        runs = []
        for j in range(PERMUTATION_SPLITS):
            g = np.random.default_rng(31_000 + j)
            runs.append(run_one(name, reg[name], seed=31_000 + j, permute=g))
            print(f"[ident] permutation-null {name} {j} AUC-0.5="
                  f"{runs[-1]['auc_minus_half']:+.5f}", flush=True)
        s = np.array([r["auc_minus_half"] for r in runs])
        permutation[name] = {
            "splits": len(runs), "mean": float(s.mean()),
            "sd": float(s.std(ddof=1)) if len(s) > 1 else None, "max": float(s.max()),
            "observed": results[name]["auc_minus_half"],
            "predicted_scaled_threshold": results[name]["threshold_ess_scaled"],
            "runs": runs,
            "reading": ("the same distortion weights permuted among the probe events: the same "
                        "weight dispersion with no dependence on the event, so this is the null "
                        "AT this ESS")}

    payload = {
        "schema": "phase-e-identifiability/1", "commit": scm.repo_commit(),
        "historical_sources": getattr(cm.historical, "_verified", None),
        "design": {"features": list(FEATURES), "sample_size": SAMPLE,
                   "train_test": "50/50, 80/20 fit/validation inside train",
                   "classifier": {"model": "HistGradientBoostingClassifier", **HGB_PARAMS},
                   "class_weight_total": CLASS_TOTAL,
                   "statistic": "weighted test AUC - 0.5",
                   "null": f"{args.null_splits} equal-model splits, both samples undistorted",
                   "verdict_rule": "distinguishable if the statistic exceeds the null's 97.5th "
                                   "percentile (raw, and ESS-scaled for weighted samples)"},
        "inputs": {"cache": str(args.cache), "cache_sha256": prep["caches"]["T"]["sha256"],
                   "prepare": str(args.prepare), "prepare_sha256": scm.sha256_file(args.prepare),
                   "pools": prep["pools"]},
        "draws": draw_record, "null": null_summary, "permutation_null": permutation,
        "distortions": results, "environment": cm.environment(),
        "seconds": time.perf_counter() - t0,
        "scope": ("simulation-only identifiability measurement on pool T; a distortion that is "
                  "not distinguishable at this sample size is NOT unrecoverable; PET is "
                  "diagnostic method development"),
    }
    cm.write_json(args.output, payload)
    print(f"[ident] wrote {args.output} in {time.perf_counter() - t0:.0f}s")


if __name__ == "__main__":
    main()
