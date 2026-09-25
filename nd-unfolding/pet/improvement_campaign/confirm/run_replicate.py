"""One confirmatory-stage PET run: a frozen RunConfig on one (pool, replicate, distortion).

The training loop is B2's (`phase_b/pet/b2_driver.B2MultiFold`: the A1 recipe driver plus
per-iteration pull/push and model state, bit-exact resume, a deadline, the B2 input arms, the
opt-in efficiency-corrected step 2). What is new is only WHICH events it sees:
`replicate_inputs.py` draws the prior and the distorted pseudodata from a pool and builds the
driver's inputs for them exactly as `closure_data.py` builds them for the historical halves.

    run_replicate.py --config C.json --config-hash <sha256 of C> --repo <checkout> --out <dir>
        --inputs-npz ... --identity-sidecar ... --populations <B1 populations.npz>
        (--pool S --replicate 0 --pools-npz ... --manifest ... | --historical-halves)
        [--distortion dev] [--step2-miss-mode carry] [--deadline-unix T]
        [--crosscheck-closure-data]   (historical halves only: byte-compare with closure_data)

Outputs in `--out`: `iterations/iterNN.npz` (pull, push over every prior row), `halves.npz` (B2's
layout: `dump_rows_a` = pseudodata rows, `dump_rows_b` = prior rows), `replicate_arrays.npz` (what
`score_replicate.py` needs: truth, weights, pass flags, regions, the distortion on the pseudodata
and the oracle weight on the prior), `run_identity.json`, `receipt.json`, `status.txt`
(COMPLETE / INCOMPLETE). A rerun with the same arguments resumes after the last completed
iteration and refuses if the config, arm, miss mode, selected rows or distortion differ.

Scope: simulation only (the inventory is opened through `authorization_scope.SignalOnlyNpz`);
pools P and F are refused until the protocol's Amendment 2; the historical comparison's output
directory is refused as a write target. PET is diagnostic method development.
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
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
B2DIR = CAMPAIGN / "phase_b" / "pet"
for _p in (CAMPAIGN, B2DIR, HERE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import replicate_inputs as ri  # noqa: E402
from recipe import RunConfig  # noqa: E402

SCHEMA = "pet-improvement-confirm-run-receipt/1"
STEP2_MISS_MODES = ("carry", "efficiency_corrected")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--config-hash", required=True,
                   help="sha256 content hash of the frozen RunConfig; refused on a mismatch")
    p.add_argument("--frozen-config", type=Path, default=None,
                   help="the committed frozen config this run's config was generated from "
                        "(amendment 2); must differ from --config only in name, note and seeds")
    p.add_argument("--frozen-sha256", default=None, help="sha256 of --frozen-config's bytes")
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--inputs-npz", type=Path, required=True)
    p.add_argument("--identity-sidecar", type=Path, required=True)
    p.add_argument("--populations", type=Path, required=True,
                   help="B1 populations.npz (the historical acceptance map for the regions)")
    sel = p.add_mutually_exclusive_group(required=True)
    sel.add_argument("--pool", choices=sorted(ri.rp.POOL_CODES))
    sel.add_argument("--historical-halves", action="store_true",
                     help="positive control: the historical development halves in place of a "
                          "replicate draw")
    p.add_argument("--replicate", type=int, default=None)
    p.add_argument("--family", default=ri.FAMILY)
    p.add_argument("--n-prior", type=int, default=ri.N_PRIOR)
    p.add_argument("--n-pseudo", type=int, default=ri.N_PSEUDO)
    p.add_argument("--pools-npz", type=Path, default=None)
    p.add_argument("--manifest", type=Path, default=None)
    p.add_argument("--distortion", default=ri.DEV)
    p.add_argument("--step2-miss-mode", choices=STEP2_MISS_MODES, default="carry")
    p.add_argument("--crosscheck-closure-data", action="store_true")
    p.add_argument("--probe-rows", type=int, default=50_000)
    p.add_argument("--deadline-unix", type=float, default=None)
    p.add_argument("--first-iteration-estimate-s", type=float, default=1200.0)
    p.add_argument("--stop-after-iteration", type=int, default=None)
    p.add_argument("--inputs-only", action="store_true",
                   help="build and check the inputs (and the crosscheck), write "
                        "replicate_arrays.npz and inputs_receipt.json, and stop before any "
                        "training (no GPU needed)")
    args = p.parse_args(argv)
    if args.pool is not None and (args.replicate is None or args.pools_npz is None
                                  or args.manifest is None):
        p.error("--pool needs --replicate, --pools-npz and --manifest")
    if args.historical_halves and args.replicate is not None:
        p.error("--historical-halves takes no --replicate")
    if args.crosscheck_closure_data and not args.historical_halves:
        p.error("--crosscheck-closure-data compares against the historical halves only")
    if args.historical_halves and args.distortion != ri.DEV:
        p.error("the historical halves carry the development distortion only")
    return args


def write_json_atomic(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1, default=repr) + "\n")
    os.replace(tmp, path)


def preflight(args: argparse.Namespace) -> tuple[Path, RunConfig, Any]:
    """Every refusal that needs no data and no TensorFlow, before anything is read."""
    out = scope.refuse_historical_output(args.out)
    scope.refuse_real_data_inputs(
        bkg_mode="mc-only", measured_leg_is_real=False, npz_keys_read=ri.SIGNAL_MEMBERS,
        input_paths=[x for x in (args.inputs_npz, args.identity_sidecar, args.populations,
                                 args.pools_npz, args.manifest) if x is not None])
    config = RunConfig.from_json(args.config.read_text())
    if config.content_hash() != args.config_hash:
        raise SystemExit(f"[confirm] config hash {config.content_hash()} != --config-hash "
                         f"{args.config_hash}")
    if config.arm != "ours":
        raise SystemExit("[confirm] the confirmatory path runs the ours arm only")
    args.frozen_record = None
    if args.frozen_config is not None:
        import freeze_runs
        args.frozen_record = freeze_runs.verify_generated(config, args.frozen_config,
                                                          args.frozen_sha256)
    if args.pool is not None:
        ri.refuse_sealed_pool(args.pool)
    distortion = ri.get_distortion(args.distortion, config.endpoint.amplitude,
                                   config.endpoint.clip)
    return out, config, distortion


def run_identity(config: RunConfig, arm: Any, miss_mode: str, selection: Any,
                 distortion: Any) -> dict[str, Any]:
    ident = {"config_hash": config.content_hash(), "b2_arm": arm.name,
             "b2_arm_hash": arm.content_hash(), "step2_miss_mode": miss_mode,
             "selection_mode": selection.mode,
             "prior_rows_sha256": selection.record["prior_rows_sha256"],
             "pseudo_rows_sha256": selection.record["pseudo_rows_sha256"],
             "distortion": distortion.name, "distortion_hash": distortion.content_hash()}
    ident["run_identity"] = hashlib.sha256(json.dumps(ident, sort_keys=True).encode()).hexdigest()
    return ident


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    out, config, distortion = preflight(args)
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    import b2_arms
    import b2_driver as b2d
    import run_unfold as ru
    arm = b2_arms.get(config.feature_arm)
    probe_record = ru._load_numpy_probe()
    import numpy as np
    import closure_data as cd
    mods = cd.import_historical(args.repo)
    import tensorflow as tf
    import training_recipe
    import torch_adamw
    gpus = [d.name for d in tf.config.list_physical_devices("GPU")]
    if not gpus and not args.inputs_only:
        raise SystemExit("[confirm] no GPU visible to TensorFlow; refusing to train on CPU")
    if mods["omnifold"].REWEIGHT_LOGIT_CAP != b2d.rec.REWEIGHT_LOGIT_CAP:
        raise SystemExit("[confirm] the recorder's logit cap differs from the engine's")
    b2d.rec.install_counters(tf, next(k for k in tf.keras.optimizers.Adam.__mro__
                                      if "_clip_gradients" in vars(k)))
    ffd = mods["ffd"]

    # ---- rows, loader, closure ------------------------------------------------------------
    t_load = time.perf_counter()
    if args.historical_halves:
        selection = ri.historical_selection(mods, config.events, args.inputs_npz,
                                            args.identity_sidecar)
    else:
        selection = ri.replicate_selection(
            args.pool, args.replicate, pools_npz=args.pools_npz, manifest=args.manifest,
            identity_sidecar=args.identity_sidecar, n_prior=args.n_prior,
            n_pseudo=args.n_pseudo, family=args.family)
    ident = run_identity(config, arm, args.step2_miss_mode, selection, distortion)
    ident_path = out / "run_identity.json"
    if ident_path.exists():
        before = json.loads(ident_path.read_text())
        if before != ident:
            raise SystemExit(f"[confirm] {out} belongs to another run: {before} vs {ident}")
    else:
        write_json_atomic(ident_path, ident)
    r1 = (None if distortion.reco_energy_scale is None
          else (selection.pseudo_rows, distortion.reco_energy_scale))
    loaded = ri.load_signal_rows(ffd, mods["DataLoader"], args.inputs_npz, selection.load_rows,
                                 reco_energy_scale=r1)
    inputs, arrays = ri.assemble_closure(ffd, loaded, selection, distortion, cd.ClosureInputs)
    del loaded
    crosscheck = None
    if args.crosscheck_closure_data:
        reference = cd.build_closure_inputs(
            mods, np, arm="ours", events=config.events, endpoint=config.endpoint,
            inputs_npz=args.inputs_npz, identity_sidecar=args.identity_sidecar,
            theirs_index=None, theirs_cache=None)
        crosscheck = ri.compare_inputs(np, inputs, reference)
        crosscheck["historical_tilt_spec"] = reference.meta["tilt_spec"]
        crosscheck["frozen_constants_equal_historical_quantiles"] = bool(
            reference.meta["tilt_spec"]["pt_p50"] == distortion.record["p50"]
            and reference.meta["tilt_spec"]["pt_iqr"] == distortion.record["iqr"])
        del reference
        write_json_atomic(out / "crosscheck_closure_data.json", crosscheck)
        if not crosscheck["all_equal"]:
            raise SystemExit(f"[confirm] inputs differ from closure_data's: {crosscheck}")
    cr = ri.historical_cr()
    arrays["pseudo_region"] = ri.region_codes(cr, arrays["pseudo_truth"][:, 0],
                                              arrays["pseudo_truth"][:, 1], args.populations)
    arrays["prior_region"] = ri.region_codes(cr, arrays["prior_truth"][:, 0],
                                             arrays["prior_truth"][:, 1], args.populations)
    arrays_digest = {k: ri.sha256_bytes(v) for k, v in sorted(arrays.items())}
    arrays_path = out / "replicate_arrays.npz"
    if arrays_path.exists():
        with np.load(arrays_path) as old:
            if {k: ri.sha256_bytes(old[k]) for k in sorted(old.files)} != arrays_digest:
                raise SystemExit("[confirm] replicate_arrays.npz differs from this rebuild")
    else:
        np.savez(out / "replicate_arrays.tmp.npz", **arrays)
        os.replace(out / "replicate_arrays.tmp.npz", arrays_path)
    digests_before_arm = inputs.digests(np)
    if args.inputs_only:
        write_json_atomic(out / "inputs_receipt.json", {
            "schema": SCHEMA + "/inputs-only", "config_hash": config.content_hash(),
            "run_identity": ident, "selection": selection.record,
            "distortion": distortion.record, "closure": {
                k: v for k, v in inputs.meta.items()
                if k not in ("dump_rows_a", "dump_rows_b", "tilt_a", "pass_gen_a", "mc_indices")},
            "input_digests_before_arm": digests_before_arm, "frozen_config": args.frozen_record,
            "replicate_arrays_digests": arrays_digest, "crosscheck_closure_data": crosscheck,
            "counts": {"pdata_rows": int(len(inputs.pdata["rows"])),
                       "prior_rows": int(len(inputs.mc["rows"])),
                       "prior_pass_reco": int(np.sum(inputs.mc["pass_reco"])),
                       "prior_pass_truth": int(np.sum(inputs.mc["pass_gen"]))},
            "load_seconds": time.perf_counter() - t_load,
            "code_commit": subprocess.run(["git", "-C", str(args.repo), "rev-parse", "HEAD"],
                                          capture_output=True, text=True).stdout.strip(),
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "measured_leg_is_real_data": False})
        print(json.dumps({"inputs_receipt": str(out / "inputs_receipt.json"),
                          "load_seconds": time.perf_counter() - t_load}))
        return 0
    read = ri.scaled_reader(np, b2d.scalar_reader(np, ffd, args.inputs_npz), r1)
    arm_record = b2d.apply_arm(np, arm, inputs, read, None)
    pdata, mcb = cd.make_loaders(mods, np, inputs)
    factories, _check = ru.model_factories(config, mods, inputs)
    load_seconds = time.perf_counter() - t_load

    # ---- the unfolding (B2's loop) -------------------------------------------------------
    B2 = b2d.make_b2_multifold(mods["omnifold"].MultiFold, tf, np)
    unfolder = B2(config.name, config=config, factories=factories, data=pdata, mc=mcb,
                  out_dir=out, pretrained_check=None, training_recipe=training_recipe,
                  torch_adamw=torch_adamw, probe_rows=args.probe_rows,
                  deadline_unix=args.deadline_unix,
                  first_iteration_estimate_s=args.first_iteration_estimate_s,
                  stop_after_iteration=args.stop_after_iteration,
                  step2_miss_mode=args.step2_miss_mode)
    complete = unfolder.Unfold()
    np.savez_compressed(out / "halves.npz", dump_rows_a=inputs.meta["dump_rows_a"],
                        dump_rows_b=inputs.meta["dump_rows_b"], tilt_a=inputs.meta["tilt_a"],
                        pass_gen_a=inputs.meta["pass_gen_a"], pass_gen_b=inputs.mc["pass_gen"],
                        pass_reco_b=inputs.mc["pass_reco"])
    closure_meta = {k: v for k, v in inputs.meta.items()
                    if k not in ("dump_rows_a", "dump_rows_b", "tilt_a", "pass_gen_a",
                                 "mc_indices")}
    receipt = {
        "schema": SCHEMA, "config": config.to_dict(), "config_hash": config.content_hash(),
        "frozen_config": args.frozen_record, "run_identity": ident, "b2_arm": arm.name, "b2_arm_hash": arm.content_hash(),
        "b2_arm_record": arm_record, "step2_miss_mode": args.step2_miss_mode,
        "selection": selection.record, "distortion": distortion.record,
        "code_commit": subprocess.run(["git", "-C", str(args.repo), "rev-parse", "HEAD"],
                                      capture_output=True, text=True).stdout.strip(),
        "inputs": {"inputs_npz": str(args.inputs_npz),
                   "identity_sidecar": str(args.identity_sidecar),
                   "populations": str(args.populations),
                   "populations_sha256": ri.sha256_file(args.populations),
                   "members_read": inputs.meta["members_read"]},
        "input_digests_before_arm": digests_before_arm,
        "replicate_arrays_digests": arrays_digest,
        "crosscheck_closure_data": crosscheck, "closure": closure_meta,
        "numpy_sve_probe": probe_record, "precision_policy": mods["precision_policy"],
        "sys_path_entries_removed": mods["sys_path_entries_removed"],
        "fits": unfolder.fit_records, "iterations": unfolder.iteration_records,
        "segments": unfolder.segments, "complete": bool(complete),
        "iteration_files": {p.name: ri.sha256_file(p)
                            for p in sorted((out / "iterations").glob("iter*.npz"))},
        "load_seconds": load_seconds, "seconds": time.perf_counter() - started,
        "gpus": gpus, "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "measured_leg_is_real_data": False, "scored_here": False,
    }
    write_json_atomic(out / "receipt.json", receipt)
    (out / "status.txt").write_text("COMPLETE\n" if complete else "INCOMPLETE\n")
    print(json.dumps({"receipt": str(out / "receipt.json"), "complete": bool(complete),
                      "load_seconds": load_seconds, "seconds": receipt["seconds"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
