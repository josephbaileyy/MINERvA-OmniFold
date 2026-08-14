"""Acceptance tests for the Gate-5 full-input extraction and complete-manifest gate."""

import inspect
import json
import os
import sys
from types import SimpleNamespace

import numpy as np
import pytest

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET = os.path.join(ND, "pet")
for item in (PET, ND):
    if item not in sys.path:
        sys.path.insert(0, item)

import extract_fullevent_replica as rex  # noqa: E402
import fullevent_fps_dataloader as fe  # noqa: E402
import validate_gate5_extraction_family as family  # noqa: E402
from atomic_write import mark_complete  # noqa: E402


def make_artifact(tmp_path, *, corrupt_signal=False):
    idx, seed = 0, 50000
    n_data, n_sig, n_bkg = 3, 5, 2
    data, sig, bkg = fe.coherent_bootstrap_factors(n_data, n_sig, n_bkg, seed)
    stored_sig = sig.copy()
    if corrupt_signal:
        stored_sig[0] += 1
    imc = np.asarray([1, 3], dtype=np.int64)
    contract = {
        "step2_checkpoint": str(tmp_path / "step2.h5"),
        "pet_arch": {"num_evt": len(fe.DEFAULT_TRUTH_EVT_FEATURES)},
        "event_features_reco": list(fe.DEFAULT_EVT_FEATURES),
        "event_features_truth": list(fe.DEFAULT_TRUTH_EVT_FEATURES),
        "truth_norm_mean": [0.0] * len(fe.DEFAULT_TRUTH_EVT_FEATURES),
        "truth_norm_std": [1.0] * len(fe.DEFAULT_TRUTH_EVT_FEATURES),
    }
    factor_meta = {
        "data_factor_sha256": rex.hash_array(data),
        "signal_factor_sha256": rex.hash_array(sig),
        "background_factor_sha256": rex.hash_array(bkg),
    }
    path = tmp_path / "GATE5_REPLICA_WEIGHTS.npz"
    np.savez_compressed(
        path,
        campaign_role=np.asarray(rex.ROLE),
        replica_index=np.asarray(idx),
        bootstrap_seed=np.asarray(seed),
        replica_seed_policy=np.asarray(rex.SEED_POLICY),
        estimator_fingerprint=np.asarray(rex.nominal_extract.ESTIMATOR_FINGERPRINT),
        inputs_path=np.asarray(str(tmp_path / "G2.npz")),
        inputs_sha256=np.asarray("a" * 64),
        inference_contract=np.asarray(contract, dtype=object),
        weights_push=np.ones(imc.size),
        mc_indices=imc,
        sig_bootstrap_factor=sig[imc],
        sig_bootstrap_factor_full=stored_sig,
        bkg_indices=np.arange(n_bkg, dtype=np.int64),
        bkg_bootstrap_factor=bkg,
        bootstrap_factor_sha256=np.asarray(factor_meta, dtype=object),
        n_data_full=np.asarray(n_data),
        n_sig_full=np.asarray(n_sig),
        n_bkg_full=np.asarray(n_bkg),
        inventory_hashes=np.asarray("inventory"),
        bkg_inventory_hash=np.asarray("bkg-inventory"),
        input_identity_hashes=np.asarray({"bkg": "bkg-inventory"}, dtype=object),
        replica_target_sha256=np.asarray("b" * 64),
        replica_target_receipt_sha256=np.asarray("c" * 64),
    )
    mark_complete(str(path))
    return path, sig


def test_replica_contract_replays_full_factors(tmp_path):
    path, expected_sig = make_artifact(tmp_path)
    contract, sig, evidence = rex.read_replica_contract(path, 0, 50000, "a" * 64)
    np.testing.assert_array_equal(sig, expected_sig)
    assert contract["_inputs_sha256"] == "a" * 64
    assert evidence["factor_sha256"]["signal_factor_sha256"] == rex.hash_array(expected_sig)


def test_replica_contract_refuses_corrupt_full_signal_factor(tmp_path):
    path, _ = make_artifact(tmp_path, corrupt_signal=True)
    with pytest.raises(SystemExit, match="full signal factor differs"):
        rex.read_replica_contract(path, 0, 50000, "a" * 64)


def test_signal_factor_reaches_counts_and_completeness(monkeypatch):
    seen = {}

    def fake_extract(_inputs, weighted_push, **_kwargs):
        seen["weighted_push"] = np.asarray(weighted_push)
        # The adapter temporarily replaces this global with the factor-aware wrapper.
        comp, denom, _ = rex.nominal_extract.completeness_2d(
            np.asarray([0.2, 0.2]), np.asarray([2.0, 2.0]),
            np.asarray([1.0, 1.0]), np.asarray([True, True]),
            np.asarray([True, False]), [np.asarray([0.0, 1.0]), np.asarray([1.0, 3.0])]
        )
        seen["comp"] = comp
        seen["denom"] = denom
        return np.asarray([[1.0]]), {}

    monkeypatch.setattr(rex.nominal_extract, "extract_xsec", fake_extract)
    sig = np.asarray([0, 2], dtype=np.uint8)
    xsec, telem = rex.extract_replica_xsec(
        "unused", np.asarray([3.0, 4.0]), sig,
        mcfile="unused", flux_hist="unused", n_nucleons=None,
    )
    np.testing.assert_array_equal(seen["weighted_push"], np.asarray([0.0, 8.0]))
    # Only the factor-2 row remains in the truth denominator, and it fails reco.
    np.testing.assert_array_equal(seen["denom"], np.asarray([[2.0]]))
    np.testing.assert_array_equal(seen["comp"], np.asarray([[0.0]]))
    assert xsec.shape == (1, 1)
    assert telem["gate5_signal_factor_applied_to_truth_counts"] is True
    assert telem["gate5_signal_factor_applied_to_completeness_and_reporting_mask"] is True


def test_adapter_calls_shared_extractor_instead_of_reimplementing_engine():
    source = inspect.getsource(rex)
    assert "nominal_extract.reweight_full_inventory" in source
    assert "nominal_extract.extract_xsec" in source
    assert "REWEIGHT_LOGIT_CAP" not in source
    assert "np.clip(logit" not in source


def test_family_validator_blocks_a_missing_member(tmp_path):
    promoted = {"artifact": {"sha256": "d" * 64}, "verdict": "PASS"}
    args = SimpleNamespace(
        expected_head="e" * 40,
        source_array_job="123",
        expected_inputs_sha="a" * 64,
        expected_driver_sha="b" * 64,
        expected_nominal_extractor_sha="c" * 64,
        expected_loader_sha="d" * 64,
    )
    row = family.validate_member(tmp_path, 0, promoted, args)
    assert row["verdict"] == "FAIL"
    assert any("missing or invalid completion marker" in item for item in row["failures"])


def test_promoted_inventory_requires_exactly_50(tmp_path):
    report = tmp_path / "promoted.json"
    report.write_text(json.dumps({
        "verdict": "GATE5_TRAINING_ARTIFACTS_PASS",
        "declared_inventory": 50,
        "members": [{"replica_index": i, "verdict": "PASS"} for i in range(49)],
    }))
    with pytest.raises(SystemExit, match="lacks 50"):
        family.load_promoted_training_inventory(report)
