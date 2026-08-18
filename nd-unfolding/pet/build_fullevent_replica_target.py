#!/usr/bin/env python3
"""Gate-5 CPU stage: build one coherent, per-replica Stay-Positive target.

This is deliberately separate from TensorFlow training.  The canonical learned refiner needs the
ROOT environment, while PET training needs the TensorFlow environment; no production interpreter
on Perlmutter carries both.  The output receipt is published last and binds the target to the full
inventory, the coherent factor streams, the source dump, and the replica seed.
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for item in (HERE, REPO / "2d-unfolding", REPO / "nd-unfolding", REPO / "nd-unfolding/pet"):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import fullevent_fps_dataloader as fe  # noqa: E402
import cstat_data_only as cdo  # noqa: E402  (T1-T5, L2; one home)
import train_fullevent_nominal as nominal  # noqa: E402
from atomic_write import atomic_write, mark_complete  # noqa: E402

SCHEMA_VERSION = 1
SEED_POLICY = "gate5-cstat-n50-v1: bootstrap_seed=50000+replica_index"
REFINEMENT_SEED = 45  # canonical Gate-2 exact target: MASTER_SEED(42) + 3


def sha256_file(path, chunk=16 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def hash_array(value):
    a = np.ascontiguousarray(value)
    h = hashlib.sha256()
    h.update(str(a.dtype).encode("ascii"))
    h.update(json.dumps(list(a.shape), separators=(",", ":")).encode("ascii"))
    h.update(memoryview(a).cast("B"))
    return h.hexdigest()


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()


def install_target_only_dataloader():
    """Bind this checkout's exact NumPy DataLoader without importing PET/TensorFlow."""
    name = "omnifold.dataloader"
    source = REPO / "omnifold_nn/omnifold/dataloader.py"
    if not source.is_file() or source.is_symlink():
        raise SystemExit(f"[gate5-target] canonical NumPy DataLoader invalid: {source}")
    loaded = sys.modules.get(name)
    if loaded is not None:
        if Path(loaded.__file__).resolve() != source.resolve():
            raise SystemExit("[gate5-target] omnifold.dataloader already bound to another checkout")
        return loaded
    parent = sys.modules.get("omnifold")
    if parent is None:
        parent = types.ModuleType("omnifold")
        parent.__package__ = "omnifold"
        parent.__path__ = [str(source.parent)]
        sys.modules["omnifold"] = parent
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise SystemExit(f"[gate5-target] cannot load {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    setattr(parent, "dataloader", module)
    return module


def refuse_occupied(*paths):
    occupied = [str(p) for p in paths if os.path.lexists(p) or os.path.lexists(f"{p}.done")]
    if occupied:
        raise SystemExit("[gate5-target] collision/no-clobber guard: " + ", ".join(occupied))


def write_npy(path, array):
    def writer(tmp):
        with open(tmp, "wb") as stream:
            np.save(stream, array, allow_pickle=False)

    atomic_write(str(path), writer, suffix=".npy", overwrite=False, fsync=True)
    mark_complete(str(path), note="Gate-5 coherent replica target")


def write_json(path, payload):
    def writer(tmp):
        with open(tmp, "w", encoding="utf-8") as stream:
            json.dump(jsonable(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())

    atomic_write(str(path), writer, suffix=".json", overwrite=False, fsync=True)
    mark_complete(str(path), note="Gate-5 coherent replica target receipt; published last")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--output", required=True, help="collision-isolated target .npy")
    ap.add_argument("--receipt", required=True, help="receipt JSON, published after target")
    ap.add_argument("--bootstrap-seed", type=int, required=True)
    ap.add_argument("--replica-index", type=int, required=True)
    ap.add_argument("--expected-input-sha256", required=True)
    ap.add_argument("--gate3-manifest", required=True)
    ap.add_argument("--max-mc-events", type=int, default=200000)
    # Defaults to three-stream so every existing launcher invocation is unchanged. The default is
    # made IRRELEVANT by L2 below rather than trusted: `--cstat-product` and the family root must
    # agree, so a data-only launcher cannot silently produce three-stream targets and vice versa.
    ap.add_argument("--cstat-product", choices=list(cdo.CSTAT_PRODUCTS),
                    default=cdo.CSTAT_THREE_STREAM)
    args = ap.parse_args(argv)

    inputs = Path(args.inputs).resolve()
    output = Path(args.output).resolve()
    receipt_path = Path(args.receipt).resolve()
    gate3 = Path(args.gate3_manifest).resolve()
    if args.replica_index < 0 or args.replica_index >= 50:
        raise SystemExit("[gate5-target] replica-index must be in [0,49]")
    expected_seed = 50000 + int(args.replica_index)
    if int(args.bootstrap_seed) != expected_seed:
        raise SystemExit(
            f"[gate5-target] seed {args.bootstrap_seed} != predeclared 50000+index "
            f"({expected_seed}); fail closed"
        )
    refuse_occupied(output, receipt_path)
    nominal.run_config_gate(str(inputs), str(gate3))
    source_sha = sha256_file(inputs)
    if source_sha != args.expected_input_sha256:
        raise SystemExit(
            f"[gate5-target] source SHA-256 mismatch: {source_sha} != "
            f"{args.expected_input_sha256}"
        )

    # The exact NumPy DataLoader is the Gate-2 precedent for running target construction without
    # importing TensorFlow.  The learned refiner remains the canonical deferred ROOT implementation.
    numpy_loader = install_target_only_dataloader()

    # L2 -- TAG <=> FAMILY ROOT, both ways, before anything is written.
    data_only = (getattr(args, "cstat_product", cdo.CSTAT_THREE_STREAM) == cdo.CSTAT_DATA_ONLY)
    cdo.assert_tag_matches_root(args.cstat_product, output, receipt_path)

    # THE DATA-ONLY MECHANISM. The target stage genuinely NEEDS the data factor applied -- it is
    # what the refined target carries -- so `bootstrap_seed=None`, which is right for the TRAINING
    # stage, would remove the very variation this stage exists to produce. "Data Poisson, background
    # unity" is not reachable through the loader's single switch, and the loader is pinned. So the
    # driver substitutes the module-global the loader calls, in the same idiom this file already
    # uses for the DataLoader itself, and RESTORES IT BEFORE THE VERIFICATION BLOCK so the replay
    # below sees the canonical function rather than comparing a patched draw against itself.
    original_factors = fe.coherent_bootstrap_factors
    canonical_data_factor = None
    inv = {}
    if data_only:
        with np.load(str(inputs)) as _d:
            inv = {"n_data": int(np.asarray(_d["measured_pc"]).shape[0]),
                   "n_sig": int(np.asarray(_d["w_truth"]).shape[0]),
                   "n_bkg": int(np.asarray(_d["w_bkg"]).shape[0])}
        patched, canonical_data_factor = cdo.unity_mc_factor_patch(
            int(args.bootstrap_seed), inv["n_data"], inv["n_sig"], inv["n_bkg"])
        fe.coherent_bootstrap_factors = patched

    started = time.monotonic()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
            str(inputs),
            max_events=int(args.max_mc_events),
            seed=int(nominal.NOMINAL_SEED_POLICY["subsample_seed"]),
            bootstrap_seed=int(args.bootstrap_seed),
            bkg_mode=nominal.BKG_MODE,
            refine_fn=None,
            refine_kwargs={
                "estimator": "exact",
                "device": "cpu",
                "params": {"random_state": REFINEMENT_SEED},
                "verbose": True,
            },
            verify_identities=True,
        )
    finally:
        fe.coherent_bootstrap_factors = original_factors
    target_meta = dict(meta.get("target") or {})
    fe.assert_refined_target_is_replica(
        target_meta, bootstrap_seed=int(args.bootstrap_seed)
    )
    if target_meta.get("target_mode") != nominal.BKG_MODE:
        raise SystemExit("[gate5-target] target mode is not negweight-refined")
    if not target_meta.get("refinement_is_learned_production"):
        raise SystemExit("[gate5-target] target did not use the learned production refiner")

    weights = np.asarray(data.weight, dtype=np.float32)
    bootstrap = dict(meta.get("bootstrap") or {})
    n_data = int(bootstrap.get("n_data_full", -1))
    n_sig = int(bootstrap.get("n_sig_full", -1))
    n_bkg = int(bootstrap.get("n_bkg_full", -1))
    if weights.shape != (n_data + n_bkg,):
        raise SystemExit(
            f"[gate5-target] target rows {weights.shape} != data+bkg {(n_data + n_bkg,)}"
        )
    if not np.all(np.isfinite(weights)) or np.any(weights < 0.0):
        raise SystemExit("[gate5-target] target is non-finite or negative")
    if not np.isclose(
        weights.sum(dtype=np.float64),
        float(target_meta["step1_measured_normalization"]),
        rtol=2e-6,
        atol=1e-2,
    ):
        raise SystemExit("[gate5-target] normalized target sum misses replica 1e6*R")

    # THE REPLAY BRANCHES, and so does the closure above it -- two checks, not one. Neither is
    # relaxed: each asserts a DIFFERENT POSITIVE condition for the data-only product.
    data_factor, sig_factor, bkg_factor = fe.coherent_bootstrap_factors(
        n_data, n_sig, n_bkg, int(args.bootstrap_seed)
    )
    if data_only:
        # T2 / T5 at source: the MC streams the loader actually applied must be UNITY, and the
        # DATA stream must be the canonical draw. Asserted against what the loader published,
        # which is the whole point of substituting the factors rather than trusting the switch.
        if not np.array_equal(np.asarray(bootstrap["sig_bootstrap_factor"]),
                              np.ones(imc.size, dtype=np.uint8)):
            raise SystemExit("[gate5-target-dataonly] T5 loader applied a non-unity signal factor")
        if not np.array_equal(np.asarray(bootstrap["bkg_bootstrap_factor"]),
                              np.ones(n_bkg, dtype=np.uint8)):
            raise SystemExit("[gate5-target-dataonly] T2 loader applied a non-unity background "
                             "factor; the background MC fluctuation is in the measured target")
        if not np.array_equal(np.asarray(data_factor), np.asarray(canonical_data_factor)):
            raise SystemExit("[gate5-target-dataonly] T3 canonical data factor is not the draw the "
                             "patch supplied; the substitution did not reach the loader")
        # THE CLOSURE ABOVE targets `step1_measured_normalization` == 1e6*R. With unity background
        # the loader computed R from the DATA draw alone, so that stamp is already 1e6*R_dataonly --
        # and this asserts it rather than assuming it, by re-deriving R the loader's own way.
        with np.load(str(inputs)) as _d:
            r_do = float(fe.step1_class_ratio_from_dump(
                _d, n_data=n_data,
                w_truth_full=np.asarray(_d["w_truth"], dtype=np.float32),
                w_reco_full=np.asarray(_d["w_reco"], dtype=np.float32),
                data_factor=np.asarray(data_factor),
                bkg_factor=np.ones(n_bkg, dtype=np.uint8))[0])
        want = fe.STEP1_MC_NORMALIZATION * r_do
        got = float(target_meta["step1_measured_normalization"])
        if abs(got - want) > 4.0 * float(np.finfo(np.float32).eps) * abs(want):
            raise SystemExit(f"[gate5-target-dataonly] normalized-target closure targets "
                             f"{got!r}, not 1e6*R_dataonly {want!r}")
    else:
        if not np.array_equal(sig_factor[imc], np.asarray(bootstrap["sig_bootstrap_factor"])):
            raise SystemExit("[gate5-target] loader signal factors differ from canonical replay")
        if not np.array_equal(bkg_factor, np.asarray(bootstrap["bkg_bootstrap_factor"])):
            raise SystemExit("[gate5-target] loader background factors differ from canonical replay")

    output.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    if data_only:
        # T1-T5 asserted over the block ABOUT TO BE WRITTEN, so a target carrying a Poisson
        # background never comes into existence rather than being detected afterwards.
        cdo.assert_data_only_target_streams(
            {"cstat_product": np.asarray(cdo.CSTAT_DATA_ONLY),
             "data_bootstrap_seed": np.asarray(int(args.bootstrap_seed)),
             "data_bootstrap_factor": np.asarray(data_factor),
             "bkg_bootstrap_factor": np.ones(n_bkg, dtype=np.uint8),
             "sig_bootstrap_factor_full": np.ones(n_sig, dtype=np.uint8)},
            data_bootstrap_seed=int(args.bootstrap_seed),
            n_data_full=n_data, n_sig_full=n_sig, n_bkg_full=n_bkg)
    write_npy(output, weights)
    target_sha = sha256_file(output)
    completed_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "verdict": "GATE5_REPLICA_TARGET_PASS_TRAINING_PENDING",
        "replica_index": int(args.replica_index),
        "bootstrap_seed": int(args.bootstrap_seed),
        "seed_policy": SEED_POLICY,
        "started_at_utc": started_utc,
        "completed_at_utc": completed_utc,
        "execution": {
            "slurm_job_id": os.environ.get("SLURM_JOB_ID", "none"),
            "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID", "none"),
            "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID", "none"),
            "host": socket.gethostname(),
            "head_at_runtime": git_head(),
        },
        "input_preflight": {
            "path": str(inputs),
            "sha256": source_sha,
            "size_bytes": inputs.stat().st_size,
            "input_identity_hashes": meta.get("input_identity_hashes"),
        },
        "gate3_manifest": {
            "path": str(gate3),
            "sha256": sha256_file(gate3),
        },
        "runtime_target": target_meta,
        "cstat_product": args.cstat_product,
        # T4. The data-only seed gets ITS OWN KEY, in the target's own receipt.
        #
        # `bootstrap_seed` above means "the three-stream coherent seed", and in a data-only build it
        # is the seed of the DATA draw while the loader's echo of it is None -- one field, two
        # meanings, which is what 57194055_0/_1 died of. `precomputed_target_replica_seed` is not a
        # substitute: it is a PARAMETER the driver passes and the loader writes back, so it records
        # the CALLER'S INTENT rather than a fact about this target. This key is written by the stage
        # that BUILT the target, into the receipt that owns it, and it has exactly one meaning.
        "data_bootstrap_seed": (int(args.bootstrap_seed) if data_only else None),
        "configuration": {
            "target_mode": nominal.BKG_MODE,
            "refinement_estimator": "exact",
            "refinement_device": "cpu",
            "refinement_random_state": REFINEMENT_SEED,
            "max_mc_events": int(args.max_mc_events),
            "full_measured_inventory": True,
        },
        "step1_feed": {
            "rows": int(weights.size),
            "normalized_sum": float(weights.sum(dtype=np.float64)),
            "min": float(weights.min()),
            "max": float(weights.max()),
            "zero_rows": int((weights == 0.0).sum()),
            "weights": {
                "path": str(output),
                "sha256": target_sha,
                "size_bytes": output.stat().st_size,
                "dtype": str(weights.dtype),
            },
        },
        "bootstrap": {
            "n_data_full": n_data,
            "n_sig_full": n_sig,
            "n_bkg_full": n_bkg,
            "mc_subset_rows": int(len(imc)),
            "inventory_hashes": bootstrap.get("inventory_hashes"),
            "input_identity_hashes": meta.get("input_identity_hashes"),
            "data_factor_sha256": hash_array(data_factor),
            "signal_factor_sha256": hash_array(sig_factor),
            "background_factor_sha256": hash_array(bkg_factor),
            "factor_hash_contract": "sha256(dtype || JSON(shape) || contiguous raw bytes)",
            "canonical_replay_verified": True,
        },
        "code": {
            "target_builder": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(__file__)},
            "loader": {"path": str(Path(fe.__file__).resolve()), "sha256": sha256_file(fe.__file__)},
            "numpy_dataloader": {
                "path": str(Path(numpy_loader.__file__).resolve()),
                "sha256": sha256_file(numpy_loader.__file__),
            },
            "canonical_u2d": {
                "path": str(REPO / "2d-unfolding/unfold_2d_omnifold_unbinned.py"),
                "sha256": sha256_file(REPO / "2d-unfolding/unfold_2d_omnifold_unbinned.py"),
            },
        },
        "timing": {"total_seconds": time.monotonic() - started},
        "pet_training_started": False,
    }
    write_json(receipt_path, receipt)
    print(json.dumps({
        "status": "PASS",
        "replica_index": args.replica_index,
        "bootstrap_seed": args.bootstrap_seed,
        "target": str(output),
        "target_sha256": target_sha,
        "receipt": str(receipt_path),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
