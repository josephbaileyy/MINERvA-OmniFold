#!/usr/bin/env python3
"""Gate-5 GPU stage: train one coherent full-event PET statistical replica.

The promoted nominal driver is intentionally not edited or copied.  This dedicated adapter invokes
that exact driver and injects the only replica-specific operations at its existing seams: the
bootstrap seed, the receipt-bound precomputed target, and coherent-factor provenance fields.  The
nominal path therefore still owns the PET architecture, anneal assertion, checkpoint round-trip,
fold-forward telemetry, and transactional artifact write.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for item in (HERE, REPO / "nd-unfolding", REPO / "nd-unfolding/pet"):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import fullevent_fps_dataloader as fe  # noqa: E402
import train_fullevent_nominal as nominal  # noqa: E402
from atomic_write import atomic_write, is_complete, mark_complete  # noqa: E402

SEED_POLICY = "gate5-cstat-n50-v1: bootstrap_seed=50000+replica_index"


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
    return value


def git_head():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()


def read_replica_target_receipt(target_npy, receipt_path, inputs_npz, bootstrap_seed,
                                replica_index):
    try:
        with open(receipt_path, encoding="utf-8") as stream:
            receipt = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"[gate5-train] target receipt unreadable: {exc}")
    if receipt.get("status") != "PASS":
        raise SystemExit(f"[gate5-train] target receipt status {receipt.get('status')!r} != PASS")
    if int(receipt.get("replica_index", -1)) != int(replica_index):
        raise SystemExit("[gate5-train] target receipt replica index mismatch")
    if int(receipt.get("bootstrap_seed", -1)) != int(bootstrap_seed):
        raise SystemExit("[gate5-train] target receipt bootstrap seed mismatch")
    if receipt.get("seed_policy") != SEED_POLICY:
        raise SystemExit("[gate5-train] target receipt seed policy is not the predeclared N=50 policy")
    target_meta = dict(receipt.get("runtime_target") or {})
    fe.assert_refined_target_is_replica(target_meta, bootstrap_seed=int(bootstrap_seed))
    if target_meta.get("target_mode") != nominal.BKG_MODE:
        raise SystemExit("[gate5-train] target receipt is not negweight-refined")
    if not target_meta.get("refinement_is_learned_production"):
        raise SystemExit("[gate5-train] target receipt is not the learned production refinement")

    feed = (receipt.get("step1_feed") or {}).get("weights") or {}
    target_npy = os.path.abspath(target_npy)
    if os.path.abspath(feed.get("path", "")) != target_npy:
        raise SystemExit("[gate5-train] target path differs from the path owned by its receipt")
    if not is_complete(target_npy):
        raise SystemExit("[gate5-train] target lacks a valid size/mtime completion marker")
    target_sha = sha256_file(target_npy)
    if target_sha != feed.get("sha256"):
        raise SystemExit("[gate5-train] target SHA-256 differs from its receipt")
    if int(feed.get("size_bytes", -1)) != os.path.getsize(target_npy):
        raise SystemExit("[gate5-train] target size differs from its receipt")

    source = receipt.get("input_preflight") or {}
    if os.path.abspath(source.get("path", "")) != os.path.abspath(inputs_npz):
        raise SystemExit("[gate5-train] source dump differs from target receipt")
    if int(source.get("size_bytes", -1)) != os.path.getsize(inputs_npz):
        raise SystemExit("[gate5-train] source dump size differs from target receipt")
    if not source.get("sha256"):
        raise SystemExit("[gate5-train] target receipt does not bind a source SHA-256")
    receipt["_verified_input_sha256"] = source["sha256"]
    receipt["_verified_target_sha256"] = target_sha
    return receipt


def write_json(path, payload):
    def writer(tmp):
        with open(tmp, "w", encoding="utf-8") as stream:
            json.dump(jsonable(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())

    atomic_write(path, writer, suffix=".json", overwrite=False, fsync=True)
    mark_complete(path, note="Gate-5 coherent replica training receipt; published last")


def run_nominal_adapter(args, target_receipt):
    """Invoke the exact nominal main() while injecting the replica-only contract.

    Hooks are restored in a finally block, so importing this module cannot leave the canonical module
    mutated.  The captured loader metadata is added inside the nominal driver's own atomic write.
    """
    original_build = nominal.fe.build_fullevent_loaders
    original_provenance = nominal.assert_target_provenance
    original_atomic = nominal.atomic_savez_compressed
    captured = {}

    def replica_provenance(target_npy, receipt_path, inputs_npz):
        if os.path.abspath(target_npy) != os.path.abspath(args.target_npy):
            raise SystemExit("[gate5-train] nominal adapter received an unexpected target path")
        if os.path.abspath(receipt_path) != os.path.abspath(args.target_receipt):
            raise SystemExit("[gate5-train] nominal adapter received an unexpected receipt path")
        if os.path.abspath(inputs_npz) != os.path.abspath(args.inputs):
            raise SystemExit("[gate5-train] nominal adapter received an unexpected source path")
        return target_receipt

    def replica_build(*build_args, **build_kwargs):
        if build_kwargs.get("bootstrap_seed") not in (None, int(args.bootstrap_seed)):
            raise SystemExit("[gate5-train] conflicting bootstrap seed at loader seam")
        build_kwargs["bootstrap_seed"] = int(args.bootstrap_seed)
        build_kwargs["precomputed_target_replica_seed"] = int(args.bootstrap_seed)
        result = original_build(*build_args, **build_kwargs)
        meta = result[-1]
        fe.assert_refined_target_is_replica(
            meta.get("target") or {}, bootstrap_seed=int(args.bootstrap_seed)
        )
        captured["meta"] = meta
        return result

    def replica_atomic(path, arrays, **kwargs):
        if "meta" not in captured:
            raise SystemExit("[gate5-train] artifact write occurred before replica loader evidence")
        meta = captured["meta"]
        bootstrap = dict(meta.get("bootstrap") or {})
        if int(bootstrap.get("bootstrap_seed", -1)) != int(args.bootstrap_seed):
            raise SystemExit("[gate5-train] loader bootstrap evidence carries the wrong seed")
        n_bkg = int(bootstrap.get("n_bkg_full", -1))
        bkg_factor = np.asarray(bootstrap.get("bkg_bootstrap_factor"), dtype=np.uint8)
        if bkg_factor.shape != (n_bkg,):
            raise SystemExit("[gate5-train] full background factor was not retained")
        augmented = dict(arrays)
        augmented.update({
            "campaign_role": np.asarray("gate5-cstat-coherent-replica"),
            "replica_index": np.asarray(int(args.replica_index)),
            "bootstrap_seed": np.asarray(int(args.bootstrap_seed)),
            "sig_bootstrap_factor": np.asarray(
                bootstrap.get("sig_bootstrap_factor"), dtype=np.uint8
            ),
            "bkg_indices": np.arange(n_bkg, dtype=np.int64),
            "bkg_bootstrap_factor": bkg_factor,
            "n_data_full": np.asarray(int(bootstrap.get("n_data_full", -1))),
            "n_sig_full": np.asarray(int(bootstrap.get("n_sig_full", -1))),
            "n_bkg_full": np.asarray(n_bkg),
            "inventory_hashes": np.asarray(str(bootstrap.get("inventory_hashes"))),
            "bkg_inventory_hash": np.asarray(
                str((meta.get("input_identity_hashes") or {}).get("bkg"))
            ),
            "input_identity_hashes": np.asarray(
                dict(meta.get("input_identity_hashes") or {}), dtype=object
            ),
            "bootstrap_factor_sha256": np.asarray(
                dict(target_receipt.get("bootstrap") or {}), dtype=object
            ),
            "replica_target_receipt_path": np.asarray(os.path.abspath(args.target_receipt)),
            "replica_target_receipt_sha256": np.asarray(sha256_file(args.target_receipt)),
            "replica_target_sha256": np.asarray(target_receipt["_verified_target_sha256"]),
            "replica_seed_policy": np.asarray(SEED_POLICY),
        })
        return original_atomic(path, augmented, **kwargs)

    nominal.fe.build_fullevent_loaders = replica_build
    nominal.assert_target_provenance = replica_provenance
    nominal.atomic_savez_compressed = replica_atomic
    try:
        return nominal.main([
            "--inputs", args.inputs,
            "--out", args.output,
            "--tag", "nominal",
            "--gate3-manifest", args.gate3_manifest,
            "--target-npy", args.target_npy,
            "--target-receipt", args.target_receipt,
        ])
    finally:
        nominal.fe.build_fullevent_loaders = original_build
        nominal.assert_target_provenance = original_provenance
        nominal.atomic_savez_compressed = original_atomic


def validate_artifact(path, bootstrap_seed, replica_index, target_receipt):
    if not is_complete(path):
        raise SystemExit("[gate5-train] replica artifact lacks a valid completion marker")
    with np.load(path, allow_pickle=True) as store:
        if str(np.asarray(store["campaign_role"]).item()) != "gate5-cstat-coherent-replica":
            raise SystemExit("[gate5-train] artifact role is not Gate-5 coherent replica")
        if int(np.asarray(store["replica_index"]).item()) != int(replica_index):
            raise SystemExit("[gate5-train] artifact replica index mismatch")
        n_sig = int(np.asarray(store["n_sig_full"]).item())
        n_bkg = int(np.asarray(store["n_bkg_full"]).item())
        identities = np.asarray(store["input_identity_hashes"], dtype=object).item()
        fe.validate_coherent_bootstrap(
            store,
            bootstrap_seed=int(bootstrap_seed),
            n_sig_full=n_sig,
            n_bkg_full=n_bkg,
            estimator_fingerprint=nominal.ESTIMATOR_FINGERPRINT,
            inventory_hashes=str(np.asarray(store["inventory_hashes"]).item()),
            bkg_inventory_hash=identities["bkg"],
        )
        if str(np.asarray(store["replica_target_sha256"]).item()) != target_receipt[
            "_verified_target_sha256"
        ]:
            raise SystemExit("[gate5-train] artifact target hash differs from verified receipt")
        seed_policy = np.asarray(store["seed_policy"], dtype=object).item()
        if seed_policy != nominal.NOMINAL_SEED_POLICY:
            raise SystemExit("[gate5-train] replica drifted from the promoted nominal policy")
        realized = np.asarray(store["lr_policy_realized"], dtype=object).item()
        if not realized.get("verified_from_optimizer"):
            raise SystemExit("[gate5-train] fit-time anneal was not verified from optimizer")
        if (int(realized.get("n_fits_base_lr", -1)),
                int(realized.get("n_fits_annealed", -1))) != (2, 4):
            raise SystemExit("[gate5-train] realized anneal is not the required 2 base + 4 annealed fits")
        factor_meta = np.asarray(store["bootstrap_factor_sha256"], dtype=object).item()
        bkg_factor = np.asarray(store["bkg_bootstrap_factor"])
        if hash_array(bkg_factor) != factor_meta["background_factor_sha256"]:
            raise SystemExit("[gate5-train] persisted background factor hash mismatch")
        return {
            "rows": int(np.asarray(store["weights_push"]).size),
            "n_sig_full": n_sig,
            "n_data_full": int(np.asarray(store["n_data_full"]).item()),
            "n_bkg_full": n_bkg,
            "lr_policy_realized": realized,
            "input_identity_hashes": identities,
        }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--target-npy", required=True)
    ap.add_argument("--target-receipt", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--train-receipt", required=True)
    ap.add_argument("--gate3-manifest", required=True)
    ap.add_argument("--bootstrap-seed", type=int, required=True)
    ap.add_argument("--replica-index", type=int, required=True)
    args = ap.parse_args(argv)

    expected_seed = 50000 + int(args.replica_index)
    if args.replica_index < 0 or args.replica_index >= 50 or args.bootstrap_seed != expected_seed:
        raise SystemExit("[gate5-train] replica index/seed violates predeclared N=50 policy")
    for path in (args.output, args.train_receipt):
        if os.path.lexists(path) or os.path.lexists(f"{path}.done"):
            raise SystemExit(f"[gate5-train] collision/no-clobber guard: {path}")
    nominal.run_config_gate(args.inputs, args.gate3_manifest)
    target_receipt = read_replica_target_receipt(
        args.target_npy, args.target_receipt, args.inputs,
        args.bootstrap_seed, args.replica_index,
    )
    started = time.monotonic()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    rc = run_nominal_adapter(args, target_receipt)
    if rc != 0:
        raise SystemExit(f"[gate5-train] nominal adapter returned {rc}")
    evidence = validate_artifact(
        args.output, args.bootstrap_seed, args.replica_index, target_receipt
    )
    receipt = {
        "schema_version": 1,
        "status": "PASS",
        "verdict": "GATE5_REPLICA_TRAINING_PASS_EXTRACTION_PENDING",
        "replica_index": int(args.replica_index),
        "bootstrap_seed": int(args.bootstrap_seed),
        "seed_policy": SEED_POLICY,
        "started_at_utc": started_utc,
        "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "execution": {
            "slurm_job_id": os.environ.get("SLURM_JOB_ID", "none"),
            "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID", "none"),
            "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID", "none"),
            "host": socket.gethostname(),
            "head_at_runtime": git_head(),
        },
        "artifact": {
            "path": os.path.abspath(args.output),
            "sha256": sha256_file(args.output),
            "size_bytes": os.path.getsize(args.output),
            "completion_marker_valid": True,
        },
        "target": {
            "path": os.path.abspath(args.target_npy),
            "sha256": target_receipt["_verified_target_sha256"],
            "receipt_path": os.path.abspath(args.target_receipt),
            "receipt_sha256": sha256_file(args.target_receipt),
        },
        "evidence": evidence,
        "code": {
            "replica_driver": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(__file__)},
            "nominal_driver_unmodified": {
                "path": str(Path(nominal.__file__).resolve()),
                "sha256": sha256_file(nominal.__file__),
            },
            "loader": {"path": str(Path(fe.__file__).resolve()), "sha256": sha256_file(fe.__file__)},
        },
        "timing": {"total_seconds": time.monotonic() - started},
    }
    write_json(args.train_receipt, receipt)
    print(json.dumps({
        "status": "PASS",
        "replica_index": args.replica_index,
        "bootstrap_seed": args.bootstrap_seed,
        "artifact": os.path.abspath(args.output),
        "receipt": os.path.abspath(args.train_receipt),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
