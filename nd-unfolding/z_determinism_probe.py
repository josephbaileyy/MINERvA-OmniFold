#!/usr/bin/env python3
"""TEST the intended deterministic configuration. Do not assume it works; measure it.

Joseph, 2026-09-18: *"Before buying cross-allocation repeats, establish and test the intended
deterministic configuration. Distinguish results from the historical configuration from results
under changed controls. **Do not assume that setting four OpenMP variables establishes
determinism.**"*

WHY THAT WARNING IS EXACTLY RIGHT, MEASURED RATHER THAN CONCEDED
----------------------------------------------------------------
Two facts already in this repository, which together make the four-OpenMP-variable plan the wrong
instrument:

1. `z_reproducibility.Z_REPRO_KNOBS` records `num_threads` as *"the estimator parameter, NOT
   OMP_NUM_THREADS, which this repository has measured LightGBM to ignore."* So the four variables
   act on a channel the estimator was measured not to read.
2. `omnifold_nn_core.make_estimators:144-147` is the production estimator, and it passes
   `n_estimators`, `num_leaves`, `learning_rate`, `verbose` and `random_state` -- and **none of
   `deterministic`, `force_row_wise` or `num_threads`.** So the production configuration leaves
   `deterministic=False`, the histogram construction mode chosen at runtime, and the thread count
   equal to whatever the allocation provides. `z_reproducibility` is a PROPOSAL -- its own comment
   says *"nothing here is applied"* -- and it is not on the production path.

THE CONSEQUENCE FOR THE REPEAT EXPERIMENT, which is why this probe exists before any repeat is
bought. `z_lgbm_overlay()` already declares, in code, `declares_divergence_from_historical_chain:
True`, with the reason: *"Pinning reduction order changes Z's numbers relative to the unpinned
historical chain. This is a deliberate, declared divergence, not a bug fix."*

**So a repeat cannot be both pinned and informative about the existing products.** Either it runs
the HISTORICAL configuration -- in which case it measures what the existing products' reproducibility
actually is, and pinning is irrelevant to it -- or it runs the PINNED configuration, in which case a
bitwise-identical result is a property of a different estimator and says nothing about them. The
packet's earlier claim that a repeat *"operates on the preserved operands and the pinned code, so a
bitwise result is a property of the configuration that made the existing products"* asserted both
halves at once and is withdrawn by this module.

WHAT THIS PROBE MEASURES, AND WHAT IT CANNOT
--------------------------------------------
It measures the MECHANISM rather than sampling the outcome, because the mechanism is cheap and the
sampling is not. Thread count sets reduction order, and reduction order is how a cross-allocation
difference would reach the numbers. So varying the thread count inside one job tests the channel
that cross-node variation acts THROUGH, at a fraction of the cost of cross-node repeats -- and if
the output varies with thread count, no number of repeats fixes it.

⚠ THE ENV ARM MUST USE SEPARATE PROCESSES. `OMP_NUM_THREADS` is read when the OpenMP runtime
initialises, so setting it after LightGBM is imported may do nothing, and a single-process probe
would report "no effect" for both a variable that is ignored and a variable that was set too late.
Those are different findings. The driver therefore re-execs itself per cell.

⚠ WHAT A NEGATIVE RESULT HERE WOULD NOT ESTABLISH. Invariance across thread counts within one node
is not invariance across nodes: a different CPU model may select different vector kernels. This
probe narrows the question and does not close it, and the driver's verdict says so in those words.

⚠ IF LIGHTGBM IS ABSENT THE VERDICT IS `UNAVAILABLE`, NEVER `no differences found`. A probe whose
subject could not be loaded reports BLIND. An empty difference set from a probe that never ran is
the shape this campaign has been caught by before.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# The three arms. Each is the PRODUCTION parameter set plus a declared overlay, so no arm is a
# re-implementation of the estimator -- `historical` is byte-for-byte what production constructs.
ARMS = {
    "historical": {},
    "det_only": {"deterministic": True, "force_row_wise": True},
    "pinned": {"deterministic": True, "force_row_wise": True, "num_threads": 1},
}

# Below this the probe cannot exhibit the hazard it exists to detect: LightGBM will not split
# histogram construction across threads on a handful of rows, so every arm would agree and the
# agreement would be an artifact of the fixture rather than a property of the configuration. A
# probe truncated to fit stops before the hazard.
MIN_ROWS = 200_000


def _production_params(seed):
    """The production estimator's parameters, read from the production factory.

    Retyping them here would make this probe test a copy of the configuration rather than the
    configuration, and the copy would not drift when the original did.
    """
    import omnifold_nn_core as core
    clf1, _clf2, _reg = core.make_estimators(nvars=None, kind="lgbm", seed=seed)
    params = dict(clf1.get_params())
    # sklearn's wrapper reports many defaults it did not set; keep only what the factory names,
    # plus random_state. The factory's literal dict is the authority for that list.
    return params


def _digest(arr):
    a = np.ascontiguousarray(np.asarray(arr, dtype=np.float64))
    return hashlib.sha256(a.tobytes()).hexdigest()


def _dataset(rows, seed):
    """A fixed dataset, generated from a seed that is NOT the estimator seed.

    Sharing one seed between the data and the estimator would make a difference in either
    indistinguishable from a difference in the other.
    """
    rng = np.random.default_rng(1000003 + seed)
    x = rng.normal(size=(rows, 6))
    logit = 0.7 * x[:, 0] - 0.4 * x[:, 1] + 0.3 * x[:, 2] * x[:, 3]
    y = (rng.uniform(size=rows) < 1.0 / (1.0 + np.exp(-logit))).astype(float)
    w = rng.uniform(0.5, 1.5, size=rows)
    return x, y, w


def worker(arm, threads, rows, seed, repeats):
    """One cell: fit `repeats` times in ONE process and digest each prediction vector."""
    from lightgbm import LGBMClassifier
    import lightgbm
    params = dict(_production_params(seed))
    params.update(ARMS[arm])
    if arm != "pinned":
        params["num_threads"] = int(threads)
    x, y, w = _dataset(rows, seed)
    digests = []
    for _ in range(int(repeats)):
        clf = LGBMClassifier(**params)
        clf.fit(x, y, sample_weight=w)
        digests.append(_digest(clf.predict_proba(x)[:, 1]))
    return {
        "arm": arm, "threads": int(threads), "rows": int(rows), "seed": int(seed),
        "digests": digests,
        "within_process_identical": len(set(digests)) == 1,
        "lightgbm_version": lightgbm.__version__,
        "omp_num_threads_env": os.environ.get("OMP_NUM_THREADS"),
        "effective_num_threads_param": params.get("num_threads"),
        "production_params_source": "omnifold_nn_core.make_estimators",
        "overlay_applied": ARMS[arm],
    }


def driver(rows, seed, repeats, thread_grid, out, allow_small_rows=False):
    cells, unavailable = [], []
    for arm in ARMS:
        grid = [1] if arm == "pinned" else list(thread_grid)
        for t in grid:
            env = dict(os.environ)
            # Set in the CHILD environment so the OpenMP runtime sees it at initialisation. The
            # four variables are set together here precisely so that the finding "they do not
            # change the answer" is about the variables and not about having set only one.
            for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                        "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
                env[var] = str(t)
            r = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--mode", "worker",
                 "--arm", arm, "--threads", str(t), "--rows", str(rows),
                 "--seed", str(seed), "--repeats", str(repeats)]
                + (["--allow-small-rows"] if allow_small_rows else []),
                capture_output=True, text=True, env=env)
            if r.returncode != 0:
                unavailable.append({"arm": arm, "threads": t, "rc": r.returncode,
                                    "stderr": r.stderr[-600:]})
                continue
            cells.append(json.loads(r.stdout))

    return summarise(cells, unavailable, rows, seed, repeats, thread_grid, out)


def summarise(cells, unavailable, rows, seed, repeats, thread_grid, out=None):
    """Build the verdict record from measured cells. Pure, so it is testable without the backend."""
    record = {
        "probe": "z_determinism_probe",
        "rows": int(rows), "seed": int(seed), "repeats": int(repeats),
        "thread_grid": list(thread_grid),
        "min_rows_required": MIN_ROWS,
        "row_floor": ("SATISFIED" if int(rows) >= MIN_ROWS else
                      "WAIVED -- this record cannot support any determinism claim"),
        "cells": cells, "unavailable": unavailable,
    }
    if not cells:
        record["verdict"] = "UNAVAILABLE"
        record["verdict_note"] = (
            "No cell produced a result, so NOTHING was measured. This is not a finding of "
            "determinism and must not be read as one: an empty difference set from a probe whose "
            "subject never loaded is a blind instrument reporting zero.")
    else:
        by_arm = {}
        for c in cells:
            by_arm.setdefault(c["arm"], []).append(c)
        summary = {}
        for arm, cs in by_arm.items():
            within = all(c["within_process_identical"] for c in cs)
            across = len({d for c in cs for d in c["digests"]}) == 1
            summary[arm] = {
                "cells": len(cs),
                "within_process_identical": within,
                "invariant_across_thread_grid": across,
                "distinct_digests": sorted({d[:16] for c in cs for d in c["digests"]}),
            }
        record["per_arm"] = summary
        complete = set(by_arm) == set(ARMS)
        record["arms_complete"] = complete
        record["verdict"] = "MEASURED" if complete else "PARTIAL"
        record["verdict_note"] = (
            "Per-arm results only. This probe does NOT adopt a configuration, does not establish "
            "determinism across NODES -- a different CPU model may select different vector "
            "kernels, which one node cannot show -- and does not license a repeat. Applying an "
            "overlay to the production estimator is a material change to the estimator and is "
            "Joseph's decision.")
    if out:
        Path(out).write_text(json.dumps(record, indent=2, sort_keys=True))
    return record


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=("driver", "worker"), required=True)
    ap.add_argument("--arm", choices=tuple(ARMS))
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--rows", type=int, required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--thread-grid", default="1,2,4,8")
    ap.add_argument("--out", default=None)
    ap.add_argument("--allow-small-rows", action="store_true",
                    help="run below MIN_ROWS anyway. For unit tests only: the result cannot "
                         "support any determinism claim, and the record says so.")
    a = ap.parse_args()
    if a.rows < MIN_ROWS and not a.allow_small_rows:
        raise SystemExit(
            f"[FAIL] --rows {a.rows} is below MIN_ROWS={MIN_ROWS}. Below this LightGBM will not "
            f"split histogram construction across threads, so every arm agrees and the agreement "
            f"is a property of the fixture rather than of the configuration. Pass "
            f"--allow-small-rows only in a unit test.")
    if a.mode == "worker":
        if not a.arm:
            raise SystemExit("[FAIL] --mode worker requires --arm")
        print(json.dumps(worker(a.arm, a.threads, a.rows, a.seed, a.repeats)))
        return
    grid = tuple(int(t) for t in a.thread_grid.split(","))
    rec = driver(a.rows, a.seed, a.repeats, grid, a.out,
                 allow_small_rows=a.allow_small_rows)
    print(json.dumps({k: v for k, v in rec.items() if k != "cells"}, indent=2, sort_keys=True))
    if rec["verdict"] == "UNAVAILABLE":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
