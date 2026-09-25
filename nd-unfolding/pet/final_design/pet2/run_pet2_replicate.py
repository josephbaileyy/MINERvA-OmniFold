"""One PET2-hybrid replicate run: PET2-small (pretrained or scratch) at step 1, our truth PET at step 2.

Derived from the predecessor's `improvement_campaign/confirm/run_replicate.py` (same CLI where
possible, same run-directory artifacts, so `confirm/score_replicate.py` scores the run unchanged):
the rows, the distortion, the loader, the closure assembly, the regions and `replicate_arrays.npz`
are the predecessor's functions (`replicate_inputs.py`), called in the same order. What differs:

* the config must be a PET2 hybrid (`arm = theirs`, `model_step1 = theirs_pet2_small`, step 2 our
  PET, a B2 input arm that does not touch step 1) -- `hybrid_driver.check_hybrid_config`;
* step 1's inputs are PET2's packed tokens and globals for the SAME prior and pseudodata rows,
  gathered from the identity join (`theirs_rows.py`; optionally through a keyed per-replicate cache
  shared by the pretrained and scratch runs);
* the driver is `hybrid_driver.HybridMultiFold` (B2's loop, the A1 recipe and optimizer
  verification, plus the step-1 initialization verification at the first optimizer step and the
  throughput / GPU-memory measurements);
* only predecessor-drawn replicate selections of family `confirm-historical-size-v1` (P0-2, F0-11,
  S0, T0-1) are accepted; pool R, other families, other sizes and the historical halves are refused.
  Reco-response distortions (R1) are refused: PET2's tokens are not rescaled by the R1 path, and
  that is not approximated.

    run_pet2_replicate.py --config C.json --config-hash <sha256> --repo <checkout> --out <dir>
        --inputs-npz ... --identity-sidecar ... --populations <B1 populations.npz>
        --pool F --replicate 0 --pools-npz ... --manifest ... --step2-miss-mode efficiency_corrected
        [--distortion dev] [--theirs-join-dir D] [--theirs-cache F] [--deadline-unix T]
        [--stop-after-iteration K] [--inputs-only]

Outputs in `--out`: `iterations/iterNN.npz`, `halves.npz`, `replicate_arrays.npz`,
`run_identity.json`, `receipt.json` (model identity, initialization verification, recipe audit,
row and input digests, measurements), `init_verification.json`, `resources.jsonl`, `status.txt`.
A rerun with the same arguments resumes after the last completed iteration.

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
CONFIRM = CAMPAIGN / "confirm"
B2DIR = CAMPAIGN / "phase_b" / "pet"
for _p in (STUDY / "dev", CAMPAIGN, B2DIR, CONFIRM, HERE):
    if str(_p) in sys.path:
        sys.path.remove(str(_p))
    sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import b2_arms  # noqa: E402
import hybrid_driver as hd  # noqa: E402
import replicate_inputs as ri  # noqa: E402
import run_replicate as rr  # noqa: E402
import theirs_rows as tr  # noqa: E402
from make_dev_configs import DRAWN  # noqa: E402
from recipe import RunConfig  # noqa: E402

SCHEMA = "pet-final-design-pet2-run-receipt/1"
PRETRAINED_STATE = Path("/pscratch/sd/j/josephrb/pet-checkpoints-20260919/pretrained_state_s.npz")
REFUSED_POOLS = ("R",)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--config-hash", required=True)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--inputs-npz", type=Path, required=True)
    p.add_argument("--identity-sidecar", type=Path, required=True)
    p.add_argument("--populations", type=Path, required=True)
    p.add_argument("--pool", choices=sorted(ri.rp.POOL_CODES), required=True)
    p.add_argument("--replicate", type=int, required=True)
    p.add_argument("--family", default=ri.FAMILY)
    p.add_argument("--n-prior", type=int, default=ri.N_PRIOR)
    p.add_argument("--n-pseudo", type=int, default=ri.N_PSEUDO)
    p.add_argument("--pools-npz", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--distortion", default=ri.DEV)
    p.add_argument("--step2-miss-mode", choices=rr.STEP2_MISS_MODES, required=True,
                   help="required (no default): the miss rule is part of the design")
    p.add_argument("--theirs-join-dir", type=Path, default=tr.JOIN_DIR)
    p.add_argument("--theirs-cache", type=Path, default=None,
                   help="keyed per-replicate PET2 input cache (built if absent, reused if the "
                        "key matches, refused otherwise)")
    p.add_argument("--pretrained-reference", type=Path, default=PRETRAINED_STATE,
                   help="the exported pretrained state the first-step verification compares "
                        "with (both variants); must hash to the pinned sha256")
    p.add_argument("--probe-rows", type=int, default=50_000)
    p.add_argument("--deadline-unix", type=float, default=None)
    p.add_argument("--first-iteration-estimate-s", type=float, default=1200.0)
    p.add_argument("--stop-after-iteration", type=int, default=None)
    p.add_argument("--theirs-cache-only", action="store_true",
                   help="CPU pre-gather: draw the selection, gather PET2's legs for its prior rows "
                        "and its reco- and truth-passing pseudodata rows into --theirs-cache, and "
                        "stop (no TensorFlow, no inventory cloud load)")
    p.add_argument("--inputs-only", action="store_true",
                   help="build and check every input (ours and PET2's), write "
                        "replicate_arrays.npz, the PET2 cache and inputs_receipt.json, and stop "
                        "before any training (no GPU needed)")
    args = p.parse_args(argv)
    if args.theirs_cache_only and args.theirs_cache is None:
        p.error("--theirs-cache-only needs --theirs-cache")
    return args


def pinned_state_sha256() -> str:
    return str(ri._frozen_design().PINNED_HASHES["pretrained_state_npz"])


def refuse_selection(pool: str, replicate: int, family: str, n_prior: int, n_pseudo: int) -> dict:
    """Only the predecessor's own draws are open to this runner for now."""
    if pool in REFUSED_POOLS:
        raise scope.ScopeViolation(f"pool {pool} is the reserve bank (RB); refused")
    if family != ri.FAMILY or (n_prior, n_pseudo) != (ri.N_PRIOR, ri.N_PSEUDO):
        raise SystemExit(f"[pet2] only family {ri.FAMILY} at {ri.N_PRIOR}/{ri.N_PSEUDO} rows is "
                         "accepted (predecessor-drawn selections)")
    if replicate not in DRAWN.get(pool, ()):
        raise scope.ScopeViolation(f"{pool}:{replicate} was not drawn by the predecessor; refused "
                                   "(could touch the final or reserve bank)")
    return {"pool": pool, "replicate": int(replicate), "family": family,
            "allowed": {k: list(v) for k, v in DRAWN.items()}}


def preflight(args: argparse.Namespace) -> tuple[Path, RunConfig, Any, Any, dict]:
    """Every refusal that needs no data and no TensorFlow, before anything is read."""
    out = scope.refuse_historical_output(args.out)
    scope.refuse_real_data_inputs(
        bkg_mode="mc-only", measured_leg_is_real=False,
        npz_keys_read=ri.SIGNAL_MEMBERS,
        input_paths=[args.inputs_npz, args.identity_sidecar, args.populations, args.pools_npz,
                     args.manifest, args.theirs_join_dir, args.pretrained_reference]
        + ([args.theirs_cache] if args.theirs_cache else []))
    config = RunConfig.from_json(args.config.read_text())
    if config.content_hash() != args.config_hash:
        raise SystemExit(f"[pet2] config hash {config.content_hash()} != --config-hash "
                         f"{args.config_hash}")
    arm = b2_arms.get(config.feature_arm)
    pinned = pinned_state_sha256()
    hybrid = hd.check_hybrid_config(config, arm, pinned)
    got = tr.sha256_file(args.pretrained_reference)
    if got != pinned:
        raise SystemExit(f"[pet2] --pretrained-reference sha256 {got} != pinned {pinned}")
    if config.step1.init.policy == "pretrained" and \
            Path(config.step1.init.pretrained_state).resolve() != args.pretrained_reference.resolve():
        raise SystemExit("[pet2] the config's pretrained state is not the verification reference")
    selection_guard = refuse_selection(args.pool, args.replicate, args.family, args.n_prior,
                                       args.n_pseudo)
    ri.refuse_sealed_pool(args.pool)
    distortion = ri.get_distortion(args.distortion, config.endpoint.amplitude,
                                   config.endpoint.clip)
    if distortion.reco_energy_scale is not None:
        raise SystemExit("[pet2] reco-response distortions are refused: PET2's step-1 tokens are "
                         "not rescaled by the R1 path (not approximated)")
    hybrid.update({"selection_guard": selection_guard, "pretrained_reference": {
        "path": str(args.pretrained_reference), "sha256": got}})
    return out, config, arm, distortion, hybrid


def run_identity(config: RunConfig, arm: Any, miss_mode: str, selection: Any, distortion: Any,
                 index: Any) -> dict[str, Any]:
    ident = rr.run_identity(config, arm, miss_mode, selection, distortion)
    ident.pop("run_identity")
    ident.update({"driver": hd.SCHEMA, "variant": hd.variant_of(config),
                  "theirs_join_npz_sha256": index.record["join_sig_npz_sha256"]})
    ident["run_identity"] = hashlib.sha256(json.dumps(ident, sort_keys=True).encode()).hexdigest()
    return ident


def theirs_cache_only(args: argparse.Namespace, config: RunConfig, arm: Any, distortion: Any,
                      hybrid: dict) -> int:
    """PET2's legs for a selection, from the inventory's pass flags alone (CPU, no TensorFlow).

    The legs are exactly the ones the full run gathers: every prior row, and the pseudodata rows
    passing reco and truth (`replicate_inputs.assemble_closure`'s `s1_a`); the full run's cache
    key check refuses the cache if its rows differ."""
    import numpy as np
    t0 = time.perf_counter()
    index = tr.load_index(args.theirs_join_dir)
    selection = ri.replicate_selection(
        args.pool, args.replicate, pools_npz=args.pools_npz, manifest=args.manifest,
        identity_sidecar=args.identity_sidecar, n_prior=args.n_prior, n_pseudo=args.n_pseudo,
        family=args.family)
    raw = np.load(args.inputs_npz, allow_pickle=False)
    view = scope.SignalOnlyNpz(raw)
    try:
        pass_reco = np.asarray(view["pass_reco"]).astype(bool)
        pass_truth = np.asarray(view["pass_truth"]).astype(bool)
    finally:
        view.close()
    pseudo = selection.pseudo_rows
    legs = {"pdata": pseudo[pass_reco[pseudo] & pass_truth[pseudo]],
            "prior": selection.prior_rows}
    del pass_truth
    theirs = tr.gather_legs_cached(index, legs, pass_reco, tr.sha256_array(pass_reco),
                                   args.theirs_cache)
    record = {"schema": SCHEMA + "/theirs-cache", "config_hash": config.content_hash(),
              "selection": selection.record, "join": index.record, "union": theirs["union"],
              "legs": theirs["legs"], "cache": theirs["cache"],
              "cache_sha256": tr.sha256_file(args.theirs_cache),
              "seconds": time.perf_counter() - t0, "code_commit": git_head(args.repo),
              "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "keys_read": view.keys_read}
    rr.write_json_atomic(Path(str(args.theirs_cache) + ".json"), record)
    print(json.dumps({"cache": str(args.theirs_cache), "reused": theirs["cache"]["reused"],
                      "legs": {k: v["rows"] for k, v in theirs["legs"].items()},
                      "seconds": record["seconds"]}))
    return 0


def git_head(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                          text=True).stdout.strip()


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    out, config, arm, distortion, hybrid = preflight(args)
    if args.theirs_cache_only:
        return theirs_cache_only(args, config, arm, distortion, hybrid)
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    import b2_driver as b2d
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

    # ---- rows, loader, closure (the predecessor's functions, in its order) --------------------
    t_load = time.perf_counter()
    index = tr.load_index(args.theirs_join_dir)
    selection = ri.replicate_selection(
        args.pool, args.replicate, pools_npz=args.pools_npz, manifest=args.manifest,
        identity_sidecar=args.identity_sidecar, n_prior=args.n_prior, n_pseudo=args.n_pseudo,
        family=args.family)
    ident = run_identity(config, arm, args.step2_miss_mode, selection, distortion, index)
    ident_path = out / "run_identity.json"
    if ident_path.exists():
        before = json.loads(ident_path.read_text())
        if before != ident:
            raise SystemExit(f"[pet2] {out} belongs to another run: {before} vs {ident}")
    else:
        rr.write_json_atomic(ident_path, ident)
    loaded = ri.load_signal_rows(ffd, mods["DataLoader"], args.inputs_npz, selection.load_rows)
    inputs, arrays = ri.assemble_closure(ffd, loaded, selection, distortion, cd.ClosureInputs)
    del loaded
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
                raise SystemExit("[pet2] replicate_arrays.npz differs from this rebuild")
    else:
        np.savez(out / "replicate_arrays.tmp.npz", **arrays)
        os.replace(out / "replicate_arrays.tmp.npz", arrays_path)
    digests_before_arm = inputs.digests(np)

    # ---- PET2 step-1 inputs for the same rows ----------------------------------------------
    t_theirs = time.perf_counter()
    pass_reco_all, pass_reco_sha = tr.read_pass_reco(args.inputs_npz)
    if not np.array_equal(pass_reco_all[arrays["prior_rows"]], arrays["prior_pass_reco"]) or \
            not np.array_equal(pass_reco_all[arrays["pseudo_rows"]], arrays["pseudo_pass_reco"]):
        raise SystemExit("[pet2] inventory pass_reco disagrees with the loader's")
    if not pass_reco_all[inputs.pdata["rows"]].all():
        raise SystemExit("[pet2] a pseudodata step-1 row does not pass reco")
    theirs = tr.gather_legs_cached(index, {"pdata": inputs.pdata["rows"],
                                           "prior": inputs.mc["rows"]},
                                   pass_reco_all, pass_reco_sha, args.theirs_cache)
    del pass_reco_all
    theirs_record = {"join": index.record, "pass_reco_sha256": pass_reco_sha,
                     "union": theirs["union"], "legs": theirs["legs"], "cache": theirs["cache"],
                     "seconds": time.perf_counter() - t_theirs}
    if args.inputs_only:
        rr.write_json_atomic(out / "inputs_receipt.json", {
            "schema": SCHEMA + "/inputs-only", "config_hash": config.content_hash(),
            "run_identity": ident, "hybrid": hybrid, "selection": selection.record,
            "distortion": distortion.record, "theirs_inputs": theirs_record,
            "input_digests_before_arm": digests_before_arm,
            "replicate_arrays_digests": arrays_digest,
            "load_seconds": time.perf_counter() - t_load, "code_commit": git_head(args.repo),
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "measured_leg_is_real_data": False})
        print(json.dumps({"inputs_receipt": str(out / "inputs_receipt.json"),
                          "load_seconds": time.perf_counter() - t_load}))
        return 0

    # ---- step-2 arm (truth side only), then PET2's step-1 inputs --------------------------
    read = b2d.scalar_reader(np, ffd, args.inputs_npz)
    arm_record = b2d.apply_arm(np, arm, inputs, read, None)
    if arm_record["step1"]:
        raise SystemExit(f"[pet2] the B2 arm changed step-1 inputs: {arm_record['step1']}")
    substitution = hd.substitute_theirs(inputs, theirs)
    del theirs
    pdata, mcb = cd.make_loaders(mods, np, inputs)
    factories, pretrained_check = ru.model_factories(config, mods, inputs)
    import pet2_keras_port as port
    verifier = hd.InitVerifier(args.pretrained_reference, pinned_state_sha256(),
                               hybrid["variant"],
                               lambda model: port.parameter_inventory(model.backbone))
    load_seconds = time.perf_counter() - t_load

    # ---- the unfolding --------------------------------------------------------------------
    Hybrid = hd.make_hybrid_multifold(mods["omnifold"].MultiFold, tf, np)
    unfolder = Hybrid(config.name, config=config, factories=factories, data=pdata, mc=mcb,
                      out_dir=out, pretrained_check=pretrained_check,
                      training_recipe=training_recipe, torch_adamw=torch_adamw,
                      probe_rows=args.probe_rows, deadline_unix=args.deadline_unix,
                      first_iteration_estimate_s=args.first_iteration_estimate_s,
                      stop_after_iteration=args.stop_after_iteration,
                      step2_miss_mode=args.step2_miss_mode, init_verifier=verifier)
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
        "config_hash": config.content_hash(), "run_identity": ident, "hybrid": hybrid,
        "b2_arm": arm.name, "b2_arm_hash": arm.content_hash(), "b2_arm_record": arm_record,
        "step2_miss_mode": args.step2_miss_mode, "selection": selection.record,
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
                                   "sha256": (ri.sha256_file(unfolder.init_path)
                                              if unfolder.init_path.exists() else None)},
        "recipe_audit": hd.recipe_audit(ru, config, unfolder.fit_records),
        "theirs_inputs": theirs_record, "step1_substitution": substitution,
        "inputs": {"inputs_npz": str(args.inputs_npz),
                   "identity_sidecar": str(args.identity_sidecar),
                   "populations": str(args.populations),
                   "populations_sha256": ri.sha256_file(args.populations),
                   "members_read": inputs.meta["members_read"]},
        "input_digests_before_arm": digests_before_arm,
        "replicate_arrays_digests": arrays_digest, "closure": closure_meta,
        "numpy_sve_probe": probe_record, "precision_policy": mods["precision_policy"],
        "sys_path_entries_removed": mods["sys_path_entries_removed"],
        "fits": unfolder.fit_records, "iterations": unfolder.iteration_records,
        "segments": unfolder.segments, "complete": bool(complete), "resources": resources,
        "iteration_files": {p.name: ri.sha256_file(p)
                            for p in sorted((out / "iterations").glob("iter*.npz"))},
        "load_seconds": load_seconds, "seconds": time.perf_counter() - started,
        "gpus": gpus, "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "measured_leg_is_real_data": False, "scored_here": False,
    }
    rr.write_json_atomic(out / "receipt.json", receipt)
    (out / "status.txt").write_text("COMPLETE\n" if complete else "INCOMPLETE\n")
    print(json.dumps({"receipt": str(out / "receipt.json"), "complete": bool(complete),
                      "variant": hybrid["variant"],
                      "init_ok": [r["ok"] for r in unfolder.init_records],
                      "load_seconds": load_seconds, "seconds": receipt["seconds"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
