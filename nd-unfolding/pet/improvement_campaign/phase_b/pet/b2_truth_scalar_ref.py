"""Experiment 2, T3: scalar truth-only references under the SAME protocol as the PET arms.

B1's classifiers (`phase_b/scalar/scalar_omnifold.HGBRatio`, `.MLPRatio`, unchanged) learn the
KNOWN tilt on half A's truth (class 0: prior truth at w_truth; class 1: the same events at
w_truth x tilt; 80/20 train/validation inside half A, seeded per seed), and the learned ratio is
evaluated on half B's truth -- exactly what `b2_driver.py --mode truth_only` does for the PET.
Scores (both through B1's historical-code scorers):

* `learnability`: B x ratio vs B x (the half-A tilt function evaluated on B), aggregate + regions;
* `endpoint`: the historical score of the push over half B (sampling ceiling 0.984, B1 anchors).

A LEARNABILITY DIAGNOSTIC of the input set, not a detector-level bound, not an unfolding recovery.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scalar"))

import run_ibu  # noqa: E402
import run_truth_learnability as rtl  # noqa: E402
import scalar_common as scm  # noqa: E402
import scalar_omnifold as so  # noqa: E402

INPUT_SETS = {"eavail_pt_ppar": (2, 0, 1), "pt_ppar": (0, 1)}   # truth_scalars columns
MODELS = ("hgb", "mlp")
SEEDS = (1, 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--populations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    t_start = time.perf_counter()
    sources = scm.verify_historical_sources()
    mods = scm.historical_modules()
    cp, fd = mods["cp"], mods["fd"]
    pop = scm.load_populations(args.populations)
    endpoint = scm.endpoint_from_populations(pop)
    pga, pgb = pop["a_pass_truth"].astype(bool), pop["b_pass_truth"].astype(bool)
    ta, tb = pop["a_truth"][pga], pop["b_truth"][pgb]
    w_a, w_b = pop["a_w_truth"][pga], pop["b_w_truth"][pgb]
    tilt_a = pop["a_tilt"][pga]
    tilt_check, spec = cp.clipped_exponential_tilt(ta[:, 2], amplitude=float(fd.ENDPOINT["amplitude"]),
                                                   clip_z=float(fd.ENDPOINT["clip"]))
    if float(np.max(np.abs(tilt_check - tilt_a))) != 0.0:
        raise SystemExit("[t3] the half-A tilt does not reproduce from its function")

    def tilt_fn(e: np.ndarray) -> np.ndarray:
        z = np.clip((e - spec["pt_p50"]) / spec["pt_iqr"], -spec["clip_z"], spec["clip_z"])
        return np.exp(spec["amplitude"] * z) / spec["pre_normalization_mean"]

    tilt_fn_b = tilt_fn(tb[:, 2])
    region_a, region_b = pop["ep_region_a"].astype("<U32"), pop["ep_region_b"].astype("<U32")
    edges = pop["endpoint_edges"]
    results: list[dict[str, Any]] = []
    for seed in SEEDS:
        rng = np.random.default_rng(20_000 + seed)
        perm = rng.permutation(ta.shape[0])
        n_tr = int(so.TRAIN_FRAC * perm.size)
        fit_rows, val_rows = np.sort(perm[:n_tr]), np.sort(perm[n_tr:])
        for set_name, cols in INPUT_SETS.items():
            Xa, Xb = ta[:, list(cols)], tb[:, list(cols)]
            for model in MODELS:
                t0 = time.perf_counter()
                clf = so.HGBRatio(seed=seed) if model == "hgb" else so.MLPRatio(seed=seed)

                def stack(rows: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
                    return (np.concatenate([Xa[rows], Xa[rows]]),
                            np.concatenate([np.zeros(rows.size), np.ones(rows.size)]),
                            np.concatenate([w_a[rows], w_a[rows] * tilt_a[rows]]))

                info = clf.fit(*stack(fit_rows), *stack(val_rows))
                ratio_b, sat_b = so._capped_ratio(clf.logit(Xb))
                ratio_a, _ = so._capped_ratio(clf.logit(Xa))
                push = np.ones(pgb.size)
                push[pgb] = ratio_b
                rec = {
                    "seed": seed, "input_set": set_name,
                    "truth_scalars_columns": list(cols), "model": model, "classifier": info,
                    "saturated_b": sat_b,
                    "learnability": rtl.score_on(np.arange(tb.shape[0]), tb[:, 2], w_b, tilt_fn_b,
                                                 ratio_b, region_b, edges),
                    "endpoint": run_ibu.compact_score(scm.score_push(
                        endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)),
                    "in_sample_half_a": rtl.score_on(np.arange(ta.shape[0]), ta[:, 2], w_a,
                                                     tilt_a, ratio_a, region_a, edges),
                    "mean_abs_log_ratio_error_b": float(np.average(
                        np.abs(np.log(ratio_b) - np.log(tilt_fn_b)), weights=w_b)),
                    "seconds": time.perf_counter() - t0}
                results.append(rec)
                print(f"[t3] seed={seed} {set_name} {model}: learnability R="
                      f"{rec['learnability']['aggregate']['recovery']:.4f} endpoint R="
                      f"{rec['endpoint']['recovery']:.4f} ({rec['seconds']:.0f}s)", flush=True)
    scm.write_json(args.output, {
        "schema": "phase-b2-truth-scalar-ref/1",
        "label": ("LEARNABILITY DIAGNOSTIC (true tilt supplied as the class-1 weight); NOT a "
                  "detector-level bound and NOT an unfolding recovery"),
        "protocol": "train/validate on half A truth (80/20, seeded), evaluate on half B truth",
        "commit": scm.repo_commit(), "historical_sources": sources,
        "populations": {"path": str(args.populations),
                        "sha256": scm.sha256_file(args.populations)},
        "tilt_spec_half_a": spec, "results": results,
        "seconds": time.perf_counter() - t_start}, compact=True)
    print(f"[t3] wrote {args.output}")


if __name__ == "__main__":
    main()
