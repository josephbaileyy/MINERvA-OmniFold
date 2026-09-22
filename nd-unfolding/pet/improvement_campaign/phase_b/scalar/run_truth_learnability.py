"""Truth-only learnability of the KNOWN tilt with a scalar step-2 classifier, on held-out events.

LEARNABILITY DIAGNOSTIC OF THE STEP-2 INPUT SET -- NOT A DETECTOR-LEVEL BOUND. The classifier is
shown the prior's truth rows unweighted (class 0) against the SAME rows weighted by the true tilt
(class 1): the answer is handed to it, and the question is only whether this input set and this
learner can represent and estimate it from a finite sample. Nothing at detector level enters, so
the score says nothing about what an unfolding can recover.

Population: half B's truth-passing rows (the historical prior). The tilt is the historical
`closure_powered_truth_reweight.clipped_exponential_tilt` evaluated on those rows (its quantiles
are therefore half B's; half A's spec is recorded beside it for comparison). A seeded 50/50 split
gives a training half (80/20 inside it for early stopping) and a held-out half on which the
seven-bin recovery is computed with the historical `recovery` function:
prior = held-out rows at w_truth, target = the same rows at w_truth * tilt, unfolded = the same
rows at w_truth * learned ratio.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

import numpy as np

import features
import run_ibu
import scalar_common as scm
import scalar_omnifold as so

INPUT_SETS = ("eavail", "truth4", "muon_truth")
MODELS = ("hgb", "mlp")
SEEDS = (1, 2, 3)


def score_on(rows: np.ndarray, eavail: np.ndarray, w: np.ndarray, tilt: np.ndarray,
             ratio: np.ndarray, regions: np.ndarray, edges: np.ndarray) -> dict[str, Any]:
    mods = scm.historical_modules()
    rae, sc = mods["rae"], mods["sc"]

    def one(mask: np.ndarray) -> dict[str, Any]:
        sel = rows[mask[rows]]
        prior = sc._histogram(eavail[sel], w[sel], edges)
        target = sc._histogram(eavail[sel], w[sel] * tilt[sel], edges)
        unfolded = sc._histogram(eavail[sel], w[sel] * ratio[sel], edges)
        rec = rae.recovery(prior, unfolded, target)
        tn, un = target / target.sum(), unfolded / unfolded.sum()
        return {"recovery": rec["recovery"], "injected_l1": rec["injected_l1"],
                "residual_l1": rec["residual_l1"],
                "overshoot_projection": float(sc.overshoot_projection(prior, unfolded, target)),
                "prior_hist": prior.tolist(), "unfolded_hist": unfolded.tolist(),
                "target_hist": target.tolist(), "signed_residual_per_bin": (un - tn).tolist(),
                "n_events": int(sel.size)}

    everything = np.ones(eavail.shape, dtype=bool)
    out = {"aggregate": one(everything), "regions": {}}
    for name in run_ibu.SCOREABLE + run_ibu.INFORMATIONAL:
        out["regions"][name] = one(regions == name)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--populations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--models", nargs="*", default=list(MODELS))
    args = parser.parse_args()
    started = time.perf_counter()
    sources = scm.verify_historical_sources()
    cp = scm.historical_modules()["cp"]
    fd = scm.historical_modules()["fd"]

    pop = scm.load_populations(args.populations)
    pg = pop["b_pass_truth"].astype(bool)
    # the Endpoint's half-B arrays ARE the pass_truth rows of half B, in order; use its labels
    region = pop["ep_region_b"].astype("<U32")
    eav = pop["b_truth"][pg, 2]
    if not np.array_equal(eav, pop["ep_eavail_b"]):
        raise SystemExit("[learnability] half-B truth rows do not align with the Endpoint")
    w = pop["b_w_truth"][pg]
    tilt, spec_b = cp.clipped_exponential_tilt(eav, amplitude=float(fd.ENDPOINT["amplitude"]),
                                               clip_z=float(fd.ENDPOINT["clip"]))
    edges = pop["endpoint_edges"]
    n = eav.size

    results = []
    fills: dict[str, Any] = {}
    for seed in SEEDS:
        rng = np.random.default_rng(10_000 + seed)
        perm = rng.permutation(n)
        train, held = np.sort(perm[: n // 2]), np.sort(perm[n // 2:])
        inner = rng.permutation(train.size)
        n_tr = int(so.TRAIN_FRAC * train.size)
        fit_rows, val_rows = train[inner[:n_tr]], train[inner[n_tr:]]
        exact = score_on(held, eav, w, tilt, tilt, region, edges)
        for input_set in INPUT_SETS:
            X_all, fills[input_set] = features.truth_matrix(pop, "b", input_set, used=pg)
            X = X_all[pg]
            for model in args.models:
                t0 = time.perf_counter()
                clf = (so.HGBRatio(seed=seed) if model == "hgb" else so.MLPRatio(seed=seed))

                def stack(rows: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
                    return (np.concatenate([X[rows], X[rows]]),
                            np.concatenate([np.zeros(rows.size), np.ones(rows.size)]),
                            np.concatenate([w[rows], w[rows] * tilt[rows]]))

                Xf, yf, wf = stack(fit_rows)
                Xv, yv, wv = stack(val_rows)
                info = clf.fit(Xf, yf, wf, Xv, yv, wv)
                ratio, saturated = so._capped_ratio(clf.logit(X))
                rec = {
                    "seed": seed, "input_set": input_set,
                    "features": features.labels(input_set, reco=False), "model": model,
                    "classifier": info, "saturated": saturated,
                    "held_out": score_on(held, eav, w, tilt, ratio, region, edges),
                    "in_sample": score_on(train, eav, w, tilt, ratio, region, edges),
                    "ratio_vs_true_tilt_held_out": {
                        "mean_abs_log_ratio_error": float(np.average(
                            np.abs(np.log(ratio[held]) - np.log(tilt[held])), weights=w[held])),
                        "ratio_summary": scm.weight_summary(ratio[held])},
                    "seconds": time.perf_counter() - t0,
                }
                results.append(rec)
                print(f"[learnability] seed={seed} {input_set:10s} {model}: held-out R="
                      f"{rec['held_out']['aggregate']['recovery']:.4f} in-sample R="
                      f"{rec['in_sample']['aggregate']['recovery']:.4f} "
                      + " ".join(f"{k}={v['recovery']:.3f}"
                                 for k, v in rec["held_out"]["regions"].items())
                      + f" ({rec['seconds']:.0f}s)", flush=True)
        results.append({"seed": seed, "input_set": "exact_true_tilt", "model": "none",
                        "held_out": exact})

    payload = {
        "schema": "phase-b1-truth-learnability/1",
        "label": ("LEARNABILITY DIAGNOSTIC of the step-2 input set: the true tilt is supplied "
                  "as the class-1 weight. NOT a detector-level bound and NOT an unfolding "
                  "recovery."),
        "commit": scm.repo_commit(),
        "historical_sources": sources,
        "inputs": {"populations_npz": str(args.populations),
                   "populations_npz_sha256": scm.sha256_file(args.populations)},
        "population": {"half": "B (historical prior)", "rows": int(n),
                       "split": "seeded 50/50 train/held-out per seed; 80/20 inside train"},
        "tilt_spec_half_B": spec_b,
        "nonfinite_fills": fills,
        "results": results,
        "seconds": time.perf_counter() - started,
    }
    scm.write_json(args.output, payload, compact=True)
    print(f"[learnability] wrote {args.output}")


if __name__ == "__main__":
    main()
