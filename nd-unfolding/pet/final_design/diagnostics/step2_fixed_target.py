"""Bounded step-2 intervention: step 2 ALONE on a controlled, fixed class-1 target (simulation only).

Builds a replicate's inputs exactly as the predecessor's `confirm/run_replicate.py` does (same
selection, loader, closure, regions, feature arm, factories, B2 training loop), then runs ONE step-2
fit with the class-1 weights ("pull") fixed to a declared target and writes the result in the
predecessor's run-directory format (`replicate_arrays.npz`, `iterations/iter00.npz` with
pull = the target and push = the learned step-2 weights), so `posthoc_iterations.py` measures it
with the same observables as the unfolding runs.

Targets (`--target`):
* `oracle` -- the exact distortion weight on the prior's truth on EVERY truth event: a truth-level
  LEARNABILITY test of the step-2 input set (what the truth network can represent), not an
  unfolding and not a detector-level bound.
* `oracle_accepted` -- the exact weight on reco-passing events, 1 on misses: what an ideal per-event
  correction restricted to the accepted events hands to step 2; with `--step2-miss-mode
  efficiency_corrected` it measures the extrapolation of a perfect accepted-event correction to the
  misses, with `carry` the dilution by misses.
* `pull:<run dir>:<k>` -- the pull of iteration k of a completed predecessor/study run on the SAME
  events (checked): step 2's projection of a realistic detector-step output.

Truth representations (`--truth-arm`): the config's feature arm, or `pdg_onehot_counts` = the
`pdg_onehot` arm plus the truncated-cloud species counts (protons, neutrons, charged pions, neutral
pions, other, number of real tokens; from `row_features.npz`) appended to the truth globals,
standardized on the prior's truth-passing rows. Truth information is permitted here because this is
the truth step; none reaches step 1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[1] / "improvement_campaign"
for p in (CAMPAIGN, CAMPAIGN / "confirm", CAMPAIGN / "phase_b" / "pet"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import run_replicate as rr  # noqa: E402  (predecessor entry; imported, not modified)

COUNT_COLUMNS = ("tr_n_p", "tr_n_n", "tr_n_pipm", "tr_n_pi0", "tr_n_other", "tr_n_valid")


def parse(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True)
    ap.add_argument("--truth-arm", default=None,
                    help="override the config's feature arm for the truth side; "
                         "'pdg_onehot_counts' adds truncated-cloud species counts")
    ap.add_argument("--row-features", type=Path, default=None)
    ap.add_argument("--step2-epochs", type=int, default=None)
    known, rest = ap.parse_known_args(argv)
    args = rr.parse_args(rest)
    for k, v in vars(known).items():
        setattr(args, k.replace("-", "_"), v)
    return args


def main(argv=None) -> int:
    args = parse(argv)
    out, config, distortion = rr.preflight(args)
    if args.truth_arm is not None:
        base_arm = "pdg_onehot" if args.truth_arm == "pdg_onehot_counts" else args.truth_arm
        config = config.replace(feature_arm=base_arm)
    if args.step2_epochs is not None:
        import dataclasses
        config = config.replace(step2=dataclasses.replace(
            config.step2, stopping=dataclasses.replace(config.step2.stopping,
                                                       max_epochs=int(args.step2_epochs))))
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    import b2_arms
    import b2_driver as b2d
    import run_unfold as ru
    import replicate_inputs as ri
    arm = b2_arms.get(config.feature_arm)
    probe_record = ru._load_numpy_probe()
    import numpy as np
    import closure_data as cd
    mods = cd.import_historical(args.repo)
    import tensorflow as tf
    import training_recipe
    import torch_adamw
    if not tf.config.list_physical_devices("GPU"):
        raise SystemExit("[step2-fixed] no GPU visible")
    b2d.rec.install_counters(tf, next(k for k in tf.keras.optimizers.Adam.__mro__
                                      if "_clip_gradients" in vars(k)))
    ffd = mods["ffd"]
    selection = ri.replicate_selection(
        args.pool, args.replicate, pools_npz=args.pools_npz, manifest=args.manifest,
        identity_sidecar=args.identity_sidecar, n_prior=args.n_prior, n_pseudo=args.n_pseudo,
        family=args.family)
    r1 = (None if distortion.reco_energy_scale is None
          else (selection.pseudo_rows, distortion.reco_energy_scale))
    loaded = ri.load_signal_rows(ffd, mods["DataLoader"], args.inputs_npz, selection.load_rows,
                                 reco_energy_scale=r1)
    inputs, arrays = ri.assemble_closure(ffd, loaded, selection, distortion, cd.ClosureInputs)
    del loaded
    cr = ri.historical_cr()
    arrays["pseudo_region"] = ri.region_codes(cr, arrays["pseudo_truth"][:, 0],
                                              arrays["pseudo_truth"][:, 1], args.populations)
    arrays["prior_region"] = ri.region_codes(cr, arrays["prior_truth"][:, 0],
                                             arrays["prior_truth"][:, 1], args.populations)
    np.savez(out / "replicate_arrays.npz", **arrays)
    read = ri.scaled_reader(np, b2d.scalar_reader(np, ffd, args.inputs_npz), r1)
    arm_record = b2d.apply_arm(np, arm, inputs, read, None)
    counts_record = None
    if args.truth_arm == "pdg_onehot_counts":
        if args.row_features is None:
            raise SystemExit("[step2-fixed] pdg_onehot_counts needs --row-features")
        R = np.load(args.row_features)
        rows = np.asarray(inputs.mc["rows"], np.int64)
        extra = np.stack([R[c][rows].astype(np.float32) for c in COUNT_COLUMNS], axis=1)
        pg = np.asarray(inputs.mc["pass_gen"], bool)
        mu, sd = extra[pg].mean(0), extra[pg].std(0)
        sd[sd == 0] = 1.0
        extra = ((extra - mu) / sd).astype(np.float32)
        extra[~pg] = 0.0
        inputs.mc["gen_evt"] = np.concatenate(
            [np.asarray(inputs.mc["gen_evt"], np.float32), extra], axis=1)
        counts_record = {"columns": list(COUNT_COLUMNS), "mean": mu.tolist(), "sd": sd.tolist(),
                         "truncated_cloud_counts": True}
    pdata, mcb = cd.make_loaders(mods, np, inputs)
    factories, _check = ru.model_factories(config, mods, inputs)

    # ---- the fixed target -----------------------------------------------------------------
    pass_reco = np.asarray(inputs.mc["pass_reco"], bool)
    if args.target in ("oracle", "oracle_accepted"):
        target = np.asarray(arrays["prior_oracle"], np.float64)
        if args.target == "oracle_accepted":
            target = np.where(pass_reco, target, 1.0)
        source = {"kind": args.target}
    elif args.target.startswith("pull:"):
        _, run_dir, k = args.target.split(":")
        run_dir = Path(run_dir)
        with np.load(run_dir / "replicate_arrays.npz") as other:
            if not np.array_equal(other["prior_rows"], arrays["prior_rows"]):
                raise SystemExit("[step2-fixed] the pull's run has different prior rows")
        with np.load(run_dir / "iterations" / f"iter{int(k):02d}.npz") as it:
            target = np.asarray(it["pull"], np.float64)
        source = {"kind": "pull", "run": str(run_dir), "iteration_file": f"iter{int(k):02d}.npz",
                  "sha256": rr.sha256_file(run_dir / "iterations" / f"iter{int(k):02d}.npz")}
    else:
        raise SystemExit(f"[step2-fixed] unknown target {args.target!r}")

    B2 = b2d.make_b2_multifold(mods["omnifold"].MultiFold, tf, np)
    unfolder = B2(config.name, config=config, factories=factories, data=pdata, mc=mcb,
                  out_dir=out, pretrained_check=None, training_recipe=training_recipe,
                  torch_adamw=torch_adamw, probe_rows=args.probe_rows,
                  step2_miss_mode=args.step2_miss_mode)
    unfolder.step1_models, unfolder.step2_models = [], []
    unfolder.weights_pull = target.astype(np.float32)
    unfolder.weights_push = np.ones_like(unfolder.weights_pull)
    unfolder.iteration_records = []
    unfolder.segments = [{"job": os.environ.get("SLURM_JOB_ID"), "first_iteration": 0}]
    t_fit = time.perf_counter()
    unfolder.seed_step(2, 0)
    unfolder.RunStep2(0)
    fit_seconds = time.perf_counter() - t_fit
    (out / "iterations").mkdir(exist_ok=True)
    np.savez(out / "iterations" / "iter00.npz", pull=np.asarray(target, np.float32),
             push=np.asarray(unfolder.weights_push, np.float32))
    receipt = {
        "schema": "pet-final-design/step2-fixed-target/1",
        "label": "BOUNDED INTERVENTION (development evidence): one step-2 fit on a fixed target",
        "target": source, "truth_arm": args.truth_arm or config.feature_arm,
        "b2_arm": arm.name, "b2_arm_record": arm_record, "counts_arm": counts_record,
        "step2_miss_mode": args.step2_miss_mode, "config": config.to_dict(),
        "config_hash_effective": config.content_hash(), "selection": selection.record,
        "distortion": distortion.record, "fits": unfolder.fit_records,
        "fit_seconds": fit_seconds, "seconds": time.perf_counter() - t0,
        "numpy_sve_probe": probe_record,
        "code_commit": subprocess.run(["git", "-C", str(args.repo), "rev-parse", "HEAD"],
                                      capture_output=True, text=True).stdout.strip(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "measured_leg_is_real_data": False,
    }
    rr.write_json_atomic(out / "receipt.json", receipt)
    (out / "status.txt").write_text("COMPLETE\n")
    print(json.dumps({"out": str(out), "fit_seconds": fit_seconds}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
