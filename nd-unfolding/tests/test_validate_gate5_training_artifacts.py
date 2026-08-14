"""Power tests for the independent Gate-5 training-artifact validator."""

import importlib.util
from pathlib import Path

import numpy as np


ND_ROOT = Path(__file__).resolve().parents[1]
PATH = ND_ROOT / "pet" / "validate_gate5_training_artifacts.py"
SPEC = importlib.util.spec_from_file_location("g5_training_validator", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_factor_hash_contract_changes_on_content_and_order():
    a = np.asarray([0, 1, 2, 1], dtype=np.uint8)
    b = np.asarray([0, 2, 1, 1], dtype=np.uint8)
    assert MOD.hash_array(a) != MOD.hash_array(b)
    assert MOD.hash_array(a) != MOD.hash_array(a.astype(np.uint16))


def test_frozen_policy_names_subsample_and_anneal():
    p = MOD.FROZEN_POLICY
    assert p["estimator_seed"] == 42
    assert p["subsample_seed"] == 0
    assert p["train_events"] == 2_000_000
    assert p["niter"] == 3
    assert p["epochs"] == 8
    assert p["batch_size"] == 512
    assert p["lr_policy"]["base_lr"] == 1e-4
    assert p["lr_policy"]["annealed_lr"] == 1e-5


def test_checkpoint_inventory_is_exact_and_six_fit_pairs():
    names = MOD.expected_checkpoints()
    assert len(names) == 14
    assert "OmniFold_fe_nominal_nominal_iter2_step1_final.weights.h5" in names
    assert "OmniFold_fe_nominal_nominal_iter2_step2_final.weights.h5" in names
    assert sum(name.endswith(".pkl") for name in names) == 6


def test_sacct_parser_rejectable_operands_are_preserved(tmp_path):
    path = tmp_path / "sacct.psv"
    path.write_text(
        "56857233_0|56857235|COMPLETED|0:0|03:01:20|start|end|nid0\n"
        "56857233_1|56857236|FAILED|1:0|00:02:00|start|end|nid1\n"
    )
    rows = MOD.parse_sacct(path)
    assert rows[0]["state"] == "COMPLETED"
    assert rows[0]["exit_code"] == "0:0"
    assert rows[1]["state"] == "FAILED"
    assert rows[1]["exit_code"] == "1:0"


def test_checks_fail_on_tampered_fit_count_and_subset():
    c = MOD.Checks()
    realized = {"n_fits_base_lr": 2, "n_fits_annealed": 3}
    c.eq("base", realized["n_fits_base_lr"], 2)
    c.eq("annealed", realized["n_fits_annealed"], 4)
    full = np.asarray([0, 1, 2, 3], dtype=np.uint8)
    idx = np.asarray([0, 2])
    subset = np.asarray([0, 1], dtype=np.uint8)
    c.truth("subset", np.array_equal(subset, full[idx]))
    assert c.summary()["n_failed"] == 2


def test_family_target_rows_key_by_persisted_index():
    rows = MOD.family_target_rows({"targets": [
        {"replica_index": 3, "verdict": "PASS"},
        {"replica_index": 1, "verdict": "FAIL"},
    ]})
    assert sorted(rows) == [1, 3]
    assert rows[1]["verdict"] == "FAIL"
