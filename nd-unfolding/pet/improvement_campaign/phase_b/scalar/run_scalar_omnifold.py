"""Scalar OmniFold (engine mirror) on the historical endpoint, every iteration recorded.

One task = one (reco input set, classifier, seed). `GRID` enumerates them so a Slurm array index
selects a task; ``--task`` may also be given by name. Step 2 always reads the four truth scalars
(`features.TRUTH_SETS["truth4"]`). Each iteration records the historical score of the push AND of
the pull (the truth-space distribution step 2 is asked to reproduce), the detector-level check of
step 1 in reco E_avail bins, classifier diagnostics, and weight summaries.
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Any

import numpy as np

import binned_unfolding as bu
import features
import run_ibu
import scalar_common as scm
import scalar_omnifold as so

SEEDS = (1, 2, 3)
GRID = [(inputs, model, seed) for inputs in ("muon", "muon_had") for model in ("hgb", "mlp")
        for seed in SEEDS]


def make_factory(model: str, seed: int):
    def factory(k: int):
        # a distinct, reproducible model seed per (task seed, iteration, step)
        return (so.HGBRatio(seed=seed * 1000 + k) if model == "hgb"
                else so.MLPRatio(seed=seed * 1000 + k))
    return factory


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--populations", type=Path, required=True)
    parser.add_argument("--task-index", type=int, default=None,
                        help="index into GRID (a Slurm array task id)")
    parser.add_argument("--inputs", choices=sorted(features.RECO_SETS), default=None)
    parser.add_argument("--model", choices=("hgb", "mlp"), default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warm-start", action="store_true",
                        help="MLP only: continue the same network across iterations")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--save-push-at", type=int, nargs="*", default=[3, 20])
    args = parser.parse_args()
    if args.task_index is not None:
        inputs, model, seed = GRID[args.task_index]
    else:
        inputs, model, seed = args.inputs, args.model, args.seed
    if None in (inputs, model, seed):
        raise SystemExit("give --task-index or all of --inputs/--model/--seed")
    warm = bool(args.warm_start and model == "mlp")
    started = time.perf_counter()
    sources = scm.verify_historical_sources()
    out_dir = scm.refuse_historical_output(args.output_dir)
    tag = f"omnifold_{inputs}_{model}_seed{seed}" + ("_warm" if warm else "")

    pop = scm.load_populations(args.populations)
    endpoint = scm.endpoint_from_populations(pop)
    bins = run_ibu.build_bins(pop)
    pga = pop["a_pass_truth"].astype(bool)
    s1a = pga & pop["a_pass_reco"].astype(bool)
    pgb = pop["b_pass_truth"].astype(bool)
    s1b = pgb & pop["b_pass_reco"].astype(bool)
    w_data = (pop["a_w_reco"] * pop["a_tilt"])[s1a]

    X_reco_mc = features.reco_matrix(pop, "b", inputs)
    X_reco_data = features.reco_matrix(pop, "a", inputs)[s1a]
    X_gen_mc = features.truth_matrix(pop, "b", "truth4")
    for name, X, mask in (("reco mc", X_reco_mc, s1b), ("reco data", X_reco_data, None),
                          ("truth mc", X_gen_mc, pgb)):
        sub = X if mask is None else X[mask]
        if not np.isfinite(sub).all():
            raise SystemExit(f"[omnifold] non-finite {name} inputs on the rows that are used")

    records: list[dict[str, Any]] = []
    saved: dict[str, np.ndarray] = {}

    def on_iteration(rec: dict[str, Any]) -> None:
        k = rec["iteration"]
        push, pull, prev = rec["push"], rec["pull"], rec["prev_push"]
        records.append({
            "iteration": k,
            "push": scm.score_push(endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL),
            "pull": run_ibu.compact_score(
                scm.score_push(endpoint, pull, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)),
            "step1_reco_eavail7_recovery": bu.reco_level_recovery(
                bins["b"]["reco_eavail7"], s1b, pop["b_w_reco"], prev, pull,
                bins["a"]["reco_eavail7"][s1a], w_data, run_ibu.N_EAV),
            "step1": rec["step1"], "step2": rec["step2"],
            "pull_summary_s1": scm.weight_summary(pull[s1b] / np.where(prev[s1b] > 0,
                                                                       prev[s1b], 1.0)),
            "push_summary": scm.weight_summary(push[pgb]),
        })
        if k in args.save_push_at:
            saved[f"push_iter{k}"] = push.astype(np.float32)
            saved[f"pull_iter{k}"] = pull.astype(np.float32)
        r = records[-1]
        print(f"[omnifold] {tag} k={k:2d} R(push)={r['push']['recovery']:.4f} "
              f"R(pull)={r['pull']['recovery']:.4f} "
              + " ".join(f"{n}={v:.3f}" for n, v in r["push"]["recovery_by_region"].items())
              + f" reco7={r['step1_reco_eavail7_recovery']['recovery']:.3f} "
              f"t1={r['step1']['seconds']:.0f}s t2={r['step2']['seconds']:.0f}s", flush=True)

    so.run_scalar_omnifold(
        X_reco_mc=X_reco_mc, X_reco_data=X_reco_data, X_gen_mc=X_gen_mc,
        pass_reco_mc=s1b, pass_gen_mc=pgb, w_truth_mc=pop["b_w_truth"],
        w_reco_mc=pop["b_w_reco"], w_data=w_data,
        make_step1=make_factory(model, seed), make_step2=make_factory(model, seed + 500),
        iterations=args.iterations, seed=seed, warm_start=warm, callback=on_iteration)

    push_path = out_dir / f"{tag}_push.npz"
    np.savez_compressed(push_path, **saved)
    payload = {
        "schema": "phase-b1-scalar-omnifold/1",
        "commit": scm.repo_commit(),
        "historical_sources": sources,
        "task": {"inputs": inputs, "model": model, "seed": seed, "warm_start": warm,
                 "iterations": args.iterations,
                 "reco_features": features.labels(inputs, reco=True),
                 "truth_features": features.labels("truth4", reco=False),
                 "classifier_params": (so.HGBRatio(seed=0).params if model == "hgb"
                                       else so.MLPRatio(seed=0).params),
                 "engine_mirror": {"train_frac": so.TRAIN_FRAC, "logit_cap": so.LOGIT_CAP,
                                   "normalization": bu.ENGINE_NORMALIZATION}},
        "inputs": {"populations_npz": str(args.populations),
                   "populations_npz_sha256": scm.sha256_file(args.populations)},
        "event_counts": {"prior_rows": int(pgb.size), "prior_pass_gen": int(pgb.sum()),
                         "prior_pass_reco_and_gen": int(s1b.sum()),
                         "pseudodata_rows": int(s1a.sum()),
                         "n_prior_scored": int(endpoint.n_prior)},
        "environment": {"slurm_job_id": os.environ.get("SLURM_JOB_ID"),
                        "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID"),
                        "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"),
                        "omp_num_threads": os.environ.get("OMP_NUM_THREADS")},
        "iterations": records,
        "saved_push": {"path": str(push_path), "sha256": scm.sha256_file(push_path)},
        "seconds": time.perf_counter() - started,
        "scope": "simulation-only scalar OmniFold diagnostic; PET is diagnostic method development",
    }
    scm.write_json(out_dir / f"{tag}.json", payload, compact=True)
    print(f"[omnifold] wrote {out_dir / (tag + '.json')} in {time.perf_counter() - started:.0f}s")


if __name__ == "__main__":
    main()
