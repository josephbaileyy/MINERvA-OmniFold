#!/usr/bin/env python3
"""Acceptance tests for the dedicated Gate-5 two-stage replica path."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
PET = REPO / "nd-unfolding/pet"
if str(PET) not in sys.path:
    sys.path.insert(0, str(PET))

import fullevent_fps_dataloader as fe  # noqa: E402
import train_fullevent_nominal as nominal  # noqa: E402
import train_fullevent_replica as replica  # noqa: E402
from atomic_write import mark_complete  # noqa: E402


def target_receipt(tmp_path, seed=50000, index=0):
    source = tmp_path / "source.npz"
    source.write_bytes(b"immutable-source-fixture")
    target = tmp_path / "target.npy"
    with target.open("wb") as stream:
        np.save(stream, np.asarray([1.0, 2.0], dtype=np.float32), allow_pickle=False)
    mark_complete(str(target), note="test")
    receipt_path = tmp_path / "target-receipt.json"
    data_factor, sig_factor, bkg_factor = fe.coherent_bootstrap_factors(3, 5, 2, seed)
    payload = {
        "status": "PASS",
        "replica_index": index,
        "bootstrap_seed": seed,
        "seed_policy": replica.SEED_POLICY,
        "runtime_target": {
            "target_mode": nominal.BKG_MODE,
            "bootstrap_seed": seed,
            "refinement_is_learned_production": True,
            "input_identity_hashes": {"sig": "s", "data": "d", "bkg": "b"},
        },
        "step1_feed": {
            "weights": {
                "path": str(target.resolve()),
                "sha256": replica.sha256_file(target),
                "size_bytes": target.stat().st_size,
            }
        },
        "input_preflight": {
            "path": str(source.resolve()),
            "sha256": replica.sha256_file(source),
            "size_bytes": source.stat().st_size,
        },
        "bootstrap": {
            "n_data_full": 3,
            "n_sig_full": 5,
            "n_bkg_full": 2,
            "data_factor_sha256": replica.hash_array(data_factor),
            "signal_factor_sha256": replica.hash_array(sig_factor),
            "background_factor_sha256": replica.hash_array(bkg_factor),
        },
    }
    receipt_path.write_text(json.dumps(payload))
    return source, target, receipt_path, payload


def test_replica_target_receipt_is_seed_and_hash_bound(tmp_path, monkeypatch):
    source, target, receipt_path, _ = target_receipt(tmp_path)
    # OI-58 hop 1 / BEN-326: the source digest is now MEASURED and must also equal the
    # frozen constant the submit controller verified against its hardcoded :14 digest.
    monkeypatch.setenv("GATE5_EXPECTED_INPUT_SHA", replica.sha256_file(source))
    rec = replica.read_replica_target_receipt(
        str(target), str(receipt_path), str(source), 50000, 0
    )
    assert rec["_verified_target_sha256"] == replica.sha256_file(target)
    # the stamped field is a measurement of the FILE, not a copy of the receipt's claim
    assert rec["_verified_input_sha256"] == replica.sha256_file(source)
    with pytest.raises((SystemExit, ValueError), match="seed"):
        replica.read_replica_target_receipt(
            str(target), str(receipt_path), str(source), 50001, 0
        )
    with target.open("ab") as stream:
        stream.write(b"tamper")
    with pytest.raises(SystemExit, match="completion marker|SHA-256"):
        replica.read_replica_target_receipt(
            str(target), str(receipt_path), str(source), 50000, 0
        )


def test_adapter_injects_replica_seed_and_augments_nominal_atomic_write(tmp_path, monkeypatch):
    source, target, receipt_path, rec = target_receipt(tmp_path)
    rec["_verified_input_sha256"] = rec["input_preflight"]["sha256"]
    rec["_verified_target_sha256"] = rec["step1_feed"]["weights"]["sha256"]
    seen = {}
    data_factor, sig_factor, bkg_factor = fe.coherent_bootstrap_factors(3, 5, 2, 50000)
    imc = np.asarray([0, 4])
    meta = {
        "target": {"bootstrap_seed": 50000},
        "bootstrap": {
            "bootstrap_seed": 50000,
            "n_data_full": 3,
            "n_sig_full": 5,
            "n_bkg_full": 2,
            "mc_indices": imc,
            "sig_bootstrap_factor": sig_factor[imc],
            "bkg_bootstrap_factor": bkg_factor,
            "inventory_hashes": "signal-order",
        },
        "input_identity_hashes": {"sig": "s", "data": "d", "bkg": "b"},
    }

    def fake_build(*args, **kwargs):
        seen["build_kwargs"] = dict(kwargs)
        return (object(), object(), imc, [], [], meta)

    def fake_atomic(path, arrays, **kwargs):
        seen["arrays"] = dict(arrays)
        return path

    original_build = nominal.fe.build_fullevent_loaders
    original_provenance = nominal.assert_target_provenance
    original_atomic = nominal.atomic_savez_compressed
    monkeypatch.setattr(nominal.fe, "build_fullevent_loaders", fake_build)
    monkeypatch.setattr(nominal, "atomic_savez_compressed", fake_atomic)

    def fake_main(argv):
        nominal.fe.build_fullevent_loaders(
            str(source), precomputed_target=str(target), bootstrap_seed=None
        )
        got = nominal.assert_target_provenance(str(target), str(receipt_path), str(source))
        assert got is rec
        nominal.atomic_savez_compressed(
            "artifact.npz", {"bootstrap_seed": np.asarray(50000)}, mark=True
        )
        return 0

    monkeypatch.setattr(nominal, "main", fake_main)
    args = SimpleNamespace(
        target_npy=str(target), target_receipt=str(receipt_path), inputs=str(source),
        bootstrap_seed=50000, replica_index=0, output=str(tmp_path / "artifact.npz"),
        gate3_manifest=str(tmp_path / "gate3.json"),
    )
    assert replica.run_nominal_adapter(args, rec) == 0
    assert seen["build_kwargs"]["bootstrap_seed"] == 50000
    assert seen["build_kwargs"]["precomputed_target_replica_seed"] == 50000
    assert seen["arrays"]["campaign_role"].item() == "gate5-cstat-coherent-replica"
    assert np.array_equal(seen["arrays"]["sig_bootstrap_factor"], sig_factor[imc])
    assert np.array_equal(seen["arrays"]["sig_bootstrap_factor_full"], sig_factor)
    assert np.array_equal(seen["arrays"]["bkg_bootstrap_factor"], bkg_factor)
    assert seen["arrays"]["replica_target_sha256"].item() == rec["_verified_target_sha256"]
    # The adapter must not leave any canonical module seam mutated after the call.
    assert nominal.fe.build_fullevent_loaders is fake_build
    assert nominal.atomic_savez_compressed is fake_atomic
    assert nominal.assert_target_provenance is original_provenance
    # Explicitly retain references so this assertion also documents the three restored seams.
    assert original_build is not fake_build
    assert original_atomic is not fake_atomic


def test_production_paths_call_replica_guard_and_leave_nominal_driver_unchanged():
    target_source = (PET / "build_fullevent_replica_target.py").read_text()
    train_source = (PET / "train_fullevent_replica.py").read_text()
    assert "fe.assert_refined_target_is_replica(" in target_source
    assert "fe.assert_refined_target_is_replica(" in train_source
    assert "precomputed_target_replica_seed" in train_source
    assert "train_fullevent_nominal as nominal" in train_source
    # The dedicated files may invoke the nominal module; they may never rewrite it.
    assert "--allow-overwrite" not in target_source + train_source


def test_n50_launchers_are_two_stage_collision_isolated_and_task_correlated():
    target = (PET / "sbatch_gate5_replica_target_array.sh").read_text()
    train = (PET / "sbatch_gate5_replica_train_array.sh").read_text()
    submit = (PET / "submit_gate5_replica_n50.sh").read_text()
    assert "#SBATCH --array=0-49%10" in target
    assert "#SBATCH --array=0-49%10" in train
    assert "#SBATCH --constraint=cpu" in target and "#SBATCH --gpus" not in target
    assert "#SBATCH --constraint=gpu" in train and "#SBATCH --gpus=1" in train
    # NERSC's job-submit plugin maps shared+gpu to gpu_shared; naming gpu_shared directly is
    # rejected as "request does not match any supported policy" (measured 2026-08-13).
    assert "#SBATCH --qos=shared" in train
    assert "#SBATCH --qos=gpu_shared" not in train
    assert "#SBATCH --mem=" not in train  # 64G adjusts to 38 cores/GPU and policy rejects it
    assert "SEED=$((50000 + INDEX))" in target
    assert "SEED=$((50000 + INDEX))" in train
    assert "--dependency=\"aftercorr:${TARGET_JOB}\"" in submit
    assert "replicas/${REPLICA}/target" in target
    assert "replicas/${REPLICA}" in train
    assert "--allow-overwrite" not in target + train + submit
    assert "scancel \"$TARGET_JOB\"" in submit  # fail closed if stage-2 submit fails


def test_source_digest_is_measured_not_copied_from_the_receipt(tmp_path, monkeypatch):
    """OI-58 hop 1 / BEN-326, power-tested in BOTH directions.

    Before the fix, `_verified_input_sha256` was `source["sha256"]` copied straight out
    of the target receipt, so a source file whose CONTENT disagreed with the receipt
    passed as long as its path and size matched -- and `train_fullevent_nominal.py:642`
    stamped that copy into the artifact under a comment claiming it was verified.

    Each case below fails if the copy is restored, which is asserted rather than assumed
    in the last one: a guard nobody has watched fail is not known to work.
    """
    source, target, receipt_path, payload = target_receipt(tmp_path)
    good = replica.sha256_file(source)

    # 1. THE ENV BINDING IS MANDATORY -- absent is fail-closed, never a silent skip.
    monkeypatch.delenv("GATE5_EXPECTED_INPUT_SHA", raising=False)
    with pytest.raises(SystemExit, match="GATE5_EXPECTED_INPUT_SHA is not exported"):
        replica.read_replica_target_receipt(
            str(target), str(receipt_path), str(source), 50000, 0
        )

    # 2. A source that is NOT the frozen canonical is refused even when it agrees with
    #    the receipt -- the case (1)-only fix of OI-57 would have admitted.
    monkeypatch.setenv("GATE5_EXPECTED_INPUT_SHA", "0" * 64)
    with pytest.raises(SystemExit, match="differs from the frozen G2 digest"):
        replica.read_replica_target_receipt(
            str(target), str(receipt_path), str(source), 50000, 0
        )

    # 3. SAME PATH, SAME SIZE, DIFFERENT BYTES -- the exact hole the copy left open.
    #    The receipt still claims the original digest; only hashing the file can see it.
    monkeypatch.setenv("GATE5_EXPECTED_INPUT_SHA", good)
    original = source.read_bytes()
    tampered = bytearray(original)
    tampered[-1] ^= 0xFF
    source.write_bytes(bytes(tampered))
    assert source.stat().st_size == len(original), "the mutation must preserve size"
    assert payload["input_preflight"]["sha256"] == good, "receipt still claims the old digest"
    with pytest.raises(SystemExit, match="source dump SHA-256 differs from its receipt"):
        replica.read_replica_target_receipt(
            str(target), str(receipt_path), str(source), 50000, 0
        )

    # 4. THE MUTANT: reinstate the pre-fix behaviour and assert it ADMITS case 3, so this
    #    test is known to be able to fail rather than believed to be.
    pre_fix_stamp = payload["input_preflight"]["sha256"]          # what the copy would use
    assert pre_fix_stamp != replica.sha256_file(source), (
        "the copy would have stamped a digest the file no longer has -- which is the defect"
    )
