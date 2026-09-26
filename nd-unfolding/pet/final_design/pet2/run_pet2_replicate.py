"""One PET2-hybrid study run: PET2-small (pretrained or scratch) at step 1, our truth PET at step 2.

Built on the study runner `final_design/runner/run_design.py` and REUSING it: the command line is
run_design's (parsed by `run_design.parse_args` itself), plus the PET2 options below; the selection
(`run_design.select_rows`: predecessor-drawn pool replicates P0-2/F0-11/S0/T0-1 or bank draws
`--bank-draw STAGE:REP --pseudo-bank {DEV,FB,RB}` with design_inputs' FB/RB release checks; pool R
refused), the distortions (`design_inputs.get_distortion`: dev, null, phase_e truth weights,
products `A*B`, `R1_x<s>[+<id>]`, `R2_x<s>[+<id>]`), the input assembly, regions and bootstrap
members (`run_design.build_inputs`: Poisson(1) weights on the pseudodata and both prior legs
before the loaders normalize, member estimator seeds) and the run-directory artifacts are
run_design's, so `confirm/score_replicate.py` scores the run unchanged. What differs:

* the config must be a PET2 hybrid (`hybrid_driver.check_hybrid_config`);
* step 1's inputs are PET2's packed tokens and globals for the SAME prior and pseudodata rows
  (`theirs_rows.py`, optionally through a keyed per-replicate cache). They are per event, so a
  bootstrap member changes only the weights, which reach both steps through run_design's weights;
* R1 / R2 are applied to the pseudodata's STORED PET2 inputs as the same physical change the ours
  path makes (`pet2_response.py`, field table in its docstring), in addition to run_design's own
  handling of the ours-side arrays (which feed the truth step's scoring arrays and reco E_avail);
* the driver is `hybrid_driver.HybridMultiFold` (init verification at the first optimizer step,
  recipe audit, throughput / GPU memory);
* stored non-finite PET2 inputs are refused unless `--nonfinite-momentum zero` /
  `--nonfinite-addinfo zero` opt in (each repair recorded in the receipt; README.md);
* the historical halves are refused (no PET2 positive control is defined for them), and the miss
  rule must be given explicitly (`--step2-miss-mode`).

    run_pet2_replicate.py <run_design.py arguments> --step2-miss-mode efficiency_corrected
        [--theirs-join-dir D] [--theirs-cache F] [--nonfinite-momentum zero]
        [--nonfinite-addinfo zero] [--pretrained-reference NPZ] [--theirs-cache-only]

Outputs as run_design (`iterations/`, `halves.npz`, `replicate_arrays.npz`, `run_identity.json`,
`receipt.json`, `status.txt`) plus `init_verification.json` and `resources.jsonl`.

Simulation only. PET is diagnostic method development.
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
STUDY = HERE.parent
PET = STUDY.parent
CAMPAIGN = PET / "improvement_campaign"
for _p in (CAMPAIGN, CAMPAIGN / "phase_b" / "pet", CAMPAIGN / "confirm", STUDY / "runner", HERE):
    if str(_p) in sys.path:
        sys.path.remove(str(_p))
    sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import design_inputs as di  # noqa: E402
import hybrid_driver as hd  # noqa: E402
import pet2_response as pr  # noqa: E402
import run_design as rd  # noqa: E402
import theirs_rows as tr  # noqa: E402
from recipe import RunConfig  # noqa: E402

SCHEMA = "pet-final-design-pet2-run-receipt/2"
PRETRAINED_STATE = Path("/pscratch/sd/j/josephrb/pet-checkpoints-20260919/pretrained_state_s.npz")


def pet2_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--theirs-join-dir", type=Path, default=tr.JOIN_DIR)
    p.add_argument("--theirs-cache", type=Path, default=None,
                   help="keyed per-replicate PET2 input cache (built if absent, reused if the "
                        "key matches, refused otherwise)")
    p.add_argument("--nonfinite-momentum", choices=tr.NONFINITE_POLICIES, default="refuse")
    p.add_argument("--nonfinite-addinfo", choices=tr.NONFINITE_POLICIES, default="refuse")
    p.add_argument("--pretrained-reference", type=Path, default=PRETRAINED_STATE)
    p.add_argument("--theirs-cache-only", action="store_true",
                   help="CPU pre-gather of PET2's legs into --theirs-cache; no TensorFlow")
    return p


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        pet2_parser().print_help()
        print("\nrun_design.py options follow.\n")
    mine, rest = pet2_parser().parse_known_args(argv)
    args = rd.parse_args(rest)
    for k, v in vars(mine).items():
        setattr(args, k, v)
    if args.historical_halves or args.crosscheck_closure_data:
        raise SystemExit("[pet2] the historical halves / closure crosscheck are not defined for "
                         "the PET2 path")
    if args.step2_miss_mode is None:
        raise SystemExit("[pet2] --step2-miss-mode is required (the miss rule is part of the "
                         "design)")
    if args.theirs_cache_only and args.theirs_cache is None:
        raise SystemExit("[pet2] --theirs-cache-only needs --theirs-cache")
    return args


def pinned_state_sha256() -> str:
    return str(di._frozen_design().PINNED_HASHES["pretrained_state_npz"])


def preflight(args: argparse.Namespace) -> tuple[Path, RunConfig, Any, Any, dict, Any]:
    """Every refusal that needs no data and no TensorFlow (run_design's, with the PET2 checks)."""
    out = scope.refuse_historical_output(args.out)
    scope.refuse_real_data_inputs(
        bkg_mode="mc-only", measured_leg_is_real=False, npz_keys_read=di.SIGNAL_MEMBERS,
        input_paths=[x for x in (args.inputs_npz, args.identity_sidecar, args.populations,
                                 args.pools_npz, args.manifest, args.banks_npz,
                                 args.theirs_join_dir, args.pretrained_reference,
                                 args.theirs_cache) if x is not None])
    config = RunConfig.from_json(args.config.read_text())
    if config.content_hash() != args.config_hash:
        raise SystemExit(f"[pet2] config hash {config.content_hash()} != --config-hash "
                         f"{args.config_hash}")
    import design_arms
    arm = design_arms.get(config.feature_arm)
    pinned = pinned_state_sha256()
    hybrid = hd.check_hybrid_config(config, arm, pinned)
    got = tr.sha256_file(args.pretrained_reference)
    if got != pinned:
        raise SystemExit(f"[pet2] --pretrained-reference sha256 {got} != pinned {pinned}")
    if config.step1.init.policy == "pretrained" and \
            Path(config.step1.init.pretrained_state).resolve() != \
            args.pretrained_reference.resolve():
        raise SystemExit("[pet2] the config's pretrained state is not the verification reference")
    args.frozen_record = None
    if args.frozen_config is not None:
        import freeze_runs
        args.frozen_record = freeze_runs.verify_generated(config, args.frozen_config,
                                                          args.frozen_sha256)
    if args.pool is not None:
        di.refuse_pool(args.pool, args.replicate, args.family, args.n_prior, args.n_pseudo)
    if args.bank_draw is not None:
        di.refuse_bank(args.pseudo_bank)
        di.bank_draw_salts(args.bank_stage, args.bank_replicate)
        args.release_listing = di.check_release_listing(       # [pfd] row-level release
            args.pseudo_bank, config.content_hash(), args.bank_draw, args.distortion,
            args.bootstrap_member)
    args.miss_mode, args.miss_mode_source = rd.resolve_miss_mode(config, args.step2_miss_mode)
    distortion = di.get_distortion(args.distortion, config.endpoint.amplitude,
                                   config.endpoint.clip)
    response = pr.transform_for(distortion)
    hybrid.update({"pretrained_reference": {"path": str(args.pretrained_reference),
                                            "sha256": got},
                   "pet2_response": (None if response is None
                                     else pr.transform_record(response[0], response[1]))})
    return out, config, arm, distortion, hybrid, response


def transform_key(response: Any) -> str:
    return pr.transform_key(None, None) if response is None else \
        pr.transform_key(response[0], response[1])


def run_identity(config: RunConfig, arm: Any, args: argparse.Namespace, selection: Any,
                 distortion: Any, index: Any, response: Any,
                 boot_config: dict | None) -> dict[str, Any]:
    ident = rd.run_identity(config, arm, args.miss_mode, selection, distortion, boot_config)
    ident.pop("run_identity")
    ident.update({"driver": hd.SCHEMA, "variant": hd.variant_of(config),
                  "nonfinite_momentum": args.nonfinite_momentum,
                  "nonfinite_addinfo": args.nonfinite_addinfo,
                  "pet2_response": transform_key(response),
                  "theirs_join_npz_sha256": index.record["join_sig_npz_sha256"]})
    ident["run_identity"] = hashlib.sha256(json.dumps(ident, sort_keys=True).encode()).hexdigest()
    return ident


def gather_theirs(args: argparse.Namespace, index: Any, pdata_rows: Any, prior_rows: Any,
                  pass_reco: Any, pass_reco_sha: str, response: Any) -> dict[str, Any]:
    """PET2's legs; a reco-response distortion transforms the pseudodata leg only."""
    transform = None if response is None else (pdata_rows, response[2])
    return tr.gather_legs_cached(index, {"pdata": pdata_rows, "prior": prior_rows}, pass_reco,
                                 pass_reco_sha, args.theirs_cache,
                                 transform_key=transform_key(response),
                                 nonfinite_momentum=args.nonfinite_momentum,
                                 nonfinite_addinfo=args.nonfinite_addinfo, transform=transform)


def theirs_cache_only(args: argparse.Namespace, config: RunConfig, response: Any) -> int:
    """PET2's legs for a selection from the inventory's pass flags alone (CPU, no TensorFlow):
    every prior row, and the pseudodata rows passing reco and truth (`assemble_closure`'s
    `s1_a`); the full run's cache-key check refuses the cache if anything differs."""
    import numpy as np
    t0 = time.perf_counter()
    index = tr.load_index(args.theirs_join_dir)
    selection, bank_check = rd.select_rows(args, config, None)
    raw = np.load(args.inputs_npz, allow_pickle=False)
    view = scope.SignalOnlyNpz(raw)
    try:
        pass_reco = np.asarray(view["pass_reco"]).astype(bool)
        pass_truth = np.asarray(view["pass_truth"]).astype(bool)
    finally:
        view.close()
    pseudo = selection.pseudo_rows
    pdata_rows = pseudo[pass_reco[pseudo] & pass_truth[pseudo]]
    del pass_truth
    theirs = gather_theirs(args, index, pdata_rows, selection.prior_rows, pass_reco,
                           tr.sha256_array(pass_reco), response)
    record = {"schema": SCHEMA + "/theirs-cache", "config_hash": config.content_hash(),
              "selection": selection.record, "bank_membership_check": bank_check,
              "join": index.record, "union": theirs["union"], "legs": theirs["legs"],
              "cache": theirs["cache"], "cache_sha256": tr.sha256_file(args.theirs_cache),
              "seconds": time.perf_counter() - t0, "code_commit": git_head(args.repo),
              "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "keys_read": view.keys_read}
    rd.write_json_atomic(Path(str(args.theirs_cache) + ".json"), record)
    print(json.dumps({"cache": str(args.theirs_cache), "reused": theirs["cache"]["reused"],
                      "legs": {k: v["rows"] for k, v in theirs["legs"].items()},
                      "seconds": record["seconds"]}))
    return 0


def git_head(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                          text=True).stdout.strip()


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    out, config, arm, distortion, hybrid, response = preflight(args)
    if args.theirs_cache_only:
        return theirs_cache_only(args, config, response)
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    import b2_driver as b2d
    import design_arms
    import run_unfold as ru
    probe_record = ru._load_numpy_probe()
    import numpy as np
    import closure_data as cd
    # `theirs_rows` appended configuration_comparison LAST; drop it so `import_historical` puts
    # it at sys.path[0] exactly as in the predecessor's run (same module resolution order).
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != tr.COMP.resolve()]
    mods = cd.import_historical(args.repo)
    import tensorflow as tf
    import training_recipe
    import torch_adamw
    gpus = [d.name for d in tf.config.list_physical_devices("GPU")]
    if not gpus and not args.inputs_only:
        raise SystemExit("[pet2] no GPU visible to TensorFlow; refusing to train on CPU")
    if mods["omnifold"].REWEIGHT_LOGIT_CAP != b2d.rec.REWEIGHT_LOGIT_CAP:
        raise SystemExit("[pet2] the recorder's logit cap differs from the engine's")
    b2d.rec.install_counters(tf, next(k for k in tf.keras.optimizers.Adam.__mro__
                                      if "_clip_gradients" in vars(k)))
    ffd = mods["ffd"]

    # ---- rows, loader, closure, bootstrap: run_design's ---------------------------------------
    t_load = time.perf_counter()
    index = tr.load_index(args.theirs_join_dir)
    selection, bank_check = rd.select_rows(args, config, mods)
    run_config, boot_config = config, None
    if args.bootstrap_member is not None:
        run_config, boot_config = di.bootstrap_config(config, args.bootstrap_member)
        boot_config["seed"] = int(args.bootstrap_seed)
    ident = run_identity(config, arm, args, selection, distortion, index, response, boot_config)
    ident_path = out / "run_identity.json"
    if ident_path.exists():
        before = json.loads(ident_path.read_text())
        if before != ident:
            raise SystemExit(f"[pet2] {out} belongs to another run: {before} vs {ident}")
    else:
        rd.write_json_atomic(ident_path, ident)
    inputs, arrays, r1, bootstrap = rd.build_inputs(args, config, distortion, selection, mods,
                                                    cd.ClosureInputs)
    arrays_digest = {k: di.sha256_bytes(v) for k, v in sorted(arrays.items())}
    arrays_path = out / "replicate_arrays.npz"
    if arrays_path.exists():
        with np.load(arrays_path) as old:
            if {k: di.sha256_bytes(old[k]) for k in sorted(old.files)} != arrays_digest:
                raise SystemExit("[pet2] replicate_arrays.npz differs from this rebuild")
    else:
        np.savez(out / "replicate_arrays.tmp.npz", **arrays)
        os.replace(out / "replicate_arrays.tmp.npz", arrays_path)
    digests_before_arm = inputs.digests(np)
    study = {"bank_manifest": rd.bank_manifest_record(args.bank_manifest),
             "draw_digests": {"prior_rows_sha256": selection.record["prior_rows_sha256"],
                              "pseudo_rows_sha256": selection.record["pseudo_rows_sha256"],
                              "prior_identity_sha256": selection.record.get(
                                  "prior_identity_sha256"),
                              "pseudo_identity_sha256": selection.record.get(
                                  "pseudo_identity_sha256")},
             "bank_membership_check": bank_check, "bootstrap": bootstrap,
             "bootstrap_config": boot_config, "run_config_hash": run_config.content_hash(),
             "step2_miss_mode_source": args.miss_mode_source, "distortion_name": distortion.name,
             "study_protocol_sha256": di.sha256_file(di.STUDY_PROTOCOL)}

    # ---- PET2 step-1 inputs for the same rows (per event: weights come from run_design) -------
    t_theirs = time.perf_counter()
    pass_reco_all, pass_reco_sha = tr.read_pass_reco(args.inputs_npz)
    if not np.array_equal(pass_reco_all[arrays["prior_rows"]], arrays["prior_pass_reco"]) or \
            not np.array_equal(pass_reco_all[arrays["pseudo_rows"]], arrays["pseudo_pass_reco"]):
        raise SystemExit("[pet2] inventory pass_reco disagrees with the loader's")
    if not pass_reco_all[inputs.pdata["rows"]].all():
        raise SystemExit("[pet2] a pseudodata step-1 row does not pass reco")
    theirs = gather_theirs(args, index, inputs.pdata["rows"], inputs.mc["rows"], pass_reco_all,
                           pass_reco_sha, response)
    del pass_reco_all
    theirs_record = {"join": index.record, "pass_reco_sha256": pass_reco_sha,
                     "union": theirs["union"], "legs": theirs["legs"], "cache": theirs["cache"],
                     "nonfinite_repairs": theirs["union"].get("nonfinite_repairs"),
                     "pet2_response": hybrid["pet2_response"],
                     "seconds": time.perf_counter() - t_theirs}
    if args.inputs_only:
        rd.write_json_atomic(out / "inputs_receipt.json", {
            "schema": SCHEMA + "/inputs-only", "config_hash": config.content_hash(),
            "run_identity": ident, "hybrid": hybrid, "selection": selection.record,
            "distortion": distortion.record, "theirs_inputs": theirs_record, "study": study,
            "input_digests_before_arm": digests_before_arm,
            "replicate_arrays_digests": arrays_digest,
            "load_seconds": time.perf_counter() - t_load, "code_commit": git_head(args.repo),
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "measured_leg_is_real_data": False})
        print(json.dumps({"inputs_receipt": str(out / "inputs_receipt.json"),
                          "load_seconds": time.perf_counter() - t_load}))
        return 0

    # ---- step-2 arm (truth side only), then PET2's step-1 inputs --------------------------
    read = di.scaled_reader(np, b2d.scalar_reader(np, ffd, args.inputs_npz), r1,
                            getattr(args, "_r2", None))
    arm_record = design_arms.apply_arm(np, arm, inputs, read, None, b2d)
    step1_changed = arm_record.get("step1") or (arm_record.get("base_record") or {}).get("step1")
    if step1_changed:
        raise SystemExit(f"[pet2] the input arm changed step-1 inputs: {step1_changed}")
    substitution = hd.substitute_theirs(inputs, theirs)
    del theirs
    pdata, mcb = cd.make_loaders(mods, np, inputs)
    factories, pretrained_check = ru.model_factories(run_config, mods, inputs)
    import pet2_keras_port as port
    verifier = hd.InitVerifier(args.pretrained_reference, pinned_state_sha256(),
                               hybrid["variant"],
                               lambda model: port.parameter_inventory(model.backbone))
    load_seconds = time.perf_counter() - t_load

    # ---- the unfolding --------------------------------------------------------------------
    Hybrid = hd.make_hybrid_multifold(mods["omnifold"].MultiFold, tf, np)
    unfolder = Hybrid(run_config.name, config=run_config, factories=factories, data=pdata,
                      mc=mcb, out_dir=out, pretrained_check=pretrained_check,
                      training_recipe=training_recipe, torch_adamw=torch_adamw,
                      probe_rows=args.probe_rows, deadline_unix=args.deadline_unix,
                      first_iteration_estimate_s=args.first_iteration_estimate_s,
                      stop_after_iteration=args.stop_after_iteration,
                      step2_miss_mode=args.miss_mode, init_verifier=verifier)
    complete = unfolder.Unfold()
    np.savez_compressed(out / "halves.npz", dump_rows_a=inputs.meta["dump_rows_a"],
                        dump_rows_b=inputs.meta["dump_rows_b"], tilt_a=inputs.meta["tilt_a"],
                        pass_gen_a=inputs.meta["pass_gen_a"], pass_gen_b=inputs.mc["pass_gen"],
                        pass_reco_b=inputs.mc["pass_reco"])
    closure_meta = {k: v for k, v in inputs.meta.items()
                    if k not in ("dump_rows_a", "dump_rows_b", "tilt_a", "pass_gen_a",
                                 "mc_indices")}
    resources = ([json.loads(x) for x in unfolder.resources_path.read_text().splitlines() if x]
                 if unfolder.resources_path.exists() else [])
    init_brief = [{k: r.get(k) for k in ("iteration", "expect", "ok", "compared", "equal",
                                         "differ", "equal_names", "parameters", "model_digest",
                                         "optimizer_iterations", "slurm_job_id")}
                  for r in unfolder.init_records]
    s1 = config.step1.init
    receipt = {
        "schema": SCHEMA, "driver": hd.SCHEMA, "config": config.to_dict(),
        "config_hash": config.content_hash(), "frozen_config": args.frozen_record,
        "run_identity": ident, "hybrid": hybrid, "study": study,
        "b2_arm": arm.name, "b2_arm_hash": arm.content_hash(), "b2_arm_record": arm_record,
        "step2_miss_mode": args.miss_mode, "selection": selection.record,
        "distortion": distortion.record, "code_commit": git_head(args.repo),
        "model_identity": {
            "step1": {"kind": config.model_step1.kind, "class": "TheirsCompleteArm",
                      "size": "small", "variant": hybrid["variant"],
                      "tensors": init_brief[0]["compared"] if init_brief else None,
                      "parameters": init_brief[0]["parameters"] if init_brief else None,
                      "pretrained_state": s1.pretrained_state,
                      "pretrained_state_sha256": s1.pretrained_state_sha256,
                      "pretrained_manifest": s1.pretrained_manifest},
            "step2": {"kind": config.model_step2.kind, "params": config.model_step2.kwargs()}},
        "init_verification": init_brief,
        "init_verification_file": {"path": str(unfolder.init_path),
                                   "sha256": (di.sha256_file(unfolder.init_path)
                                              if unfolder.init_path.exists() else None)},
        "recipe_audit": hd.recipe_audit(ru, run_config, unfolder.fit_records),
        "theirs_inputs": theirs_record, "step1_substitution": substitution,
        "inputs": {"inputs_npz": str(args.inputs_npz),
                   "identity_sidecar": str(args.identity_sidecar),
                   "populations": str(args.populations),
                   "populations_sha256": di.sha256_file(args.populations),
                   "members_read": inputs.meta["members_read"]},
        "input_digests_before_arm": digests_before_arm,
        "replicate_arrays_digests": arrays_digest, "closure": closure_meta,
        "numpy_sve_probe": probe_record, "precision_policy": mods["precision_policy"],
        "sys_path_entries_removed": mods["sys_path_entries_removed"],
        "fits": unfolder.fit_records, "iterations": unfolder.iteration_records,
        "segments": unfolder.segments, "complete": bool(complete), "resources": resources,
        "iteration_files": {p.name: di.sha256_file(p)
                            for p in sorted((out / "iterations").glob("iter*.npz"))},
        "load_seconds": load_seconds, "seconds": time.perf_counter() - started,
        "gpus": gpus, "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "measured_leg_is_real_data": False, "scored_here": False,
    }
    audit_ok = bool(receipt["recipe_audit"].get("all_as_declared"))
    rd.write_json_atomic(out / "receipt.json", receipt)
    # a run whose executed recipe differs from the declared one is never COMPLETE (review ec475e7b)
    (out / "status.txt").write_text("COMPLETE\n" if complete and audit_ok else "INCOMPLETE\n")
    if complete and not audit_ok:
        raise SystemExit("[pet2] recipe audit failed: executed recipe differs from the declared "
                         "one (receipt recipe_audit); run not marked COMPLETE")
    print(json.dumps({"receipt": str(out / "receipt.json"), "complete": bool(complete),
                      "variant": hybrid["variant"],
                      "init_ok": [r["ok"] for r in unfolder.init_records],
                      "load_seconds": load_seconds, "seconds": receipt["seconds"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
