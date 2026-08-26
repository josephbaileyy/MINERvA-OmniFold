#!/usr/bin/env python3
"""CPU-only guards for the PET-v2 fixed-draw equivalence machinery fixture."""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "docs/orchestration/pet_v2_fixed_draw_equivalence_fixture.py"
RECEIPT = (
    REPO
    / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-fixture-result-20260825.json"
)
CONTRACT = REPO / "docs/orchestration/PET-V2-EQUIVALENCE-FIXTURE-CONTRACT-20260825.md"
SPEC = importlib.util.spec_from_file_location("pet_v2_fixed_draw_equivalence_fixture", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_committed_receipt_is_exact_deterministic_render():
    assert json.loads(RECEIPT.read_text(encoding="utf-8")) == MODULE.build_receipt()


def test_literal_replays_counts_and_preserves_unique_split_membership():
    unique = MODULE.fixed_unique_rows()
    weighted = MODULE.weighted_arm(unique)
    literal = MODULE.literal_arm(unique)
    MODULE.validate_literal_materialization(unique, literal)

    counts = np.bincount(literal["source_index"], minlength=unique["event_id"].size)
    np.testing.assert_array_equal(counts, unique["multiplicity"])
    assert weighted["event_id"].size == unique["event_id"].size
    assert literal["event_id"].size == int(unique["multiplicity"].sum())
    assert set(unique["event_id"][unique["multiplicity"] == 0]).isdisjoint(literal["event_id"])


def test_literal_validator_rejects_count_identity_and_split_tampering():
    unique = MODULE.fixed_unique_rows()

    wrong_count = MODULE.literal_arm(unique)
    wrong_count["source_index"] = wrong_count["source_index"][:-1]
    with pytest.raises(ValueError, match="copy counts"):
        MODULE.validate_literal_materialization(unique, wrong_count)

    wrong_identity = MODULE.literal_arm(unique)
    wrong_identity["event_id"][0] += 100
    with pytest.raises(ValueError, match="event identity"):
        MODULE.validate_literal_materialization(unique, wrong_identity)

    wrong_split = MODULE.literal_arm(unique)
    wrong_split["is_train"][0] = ~wrong_split["is_train"][0]
    with pytest.raises(ValueError, match="split membership"):
        MODULE.validate_literal_materialization(unique, wrong_split)


def test_unique_validator_rejects_noninteger_and_negative_multiplicity():
    noninteger = MODULE.fixed_unique_rows()
    noninteger["multiplicity"] = noninteger["multiplicity"].astype(np.float64)
    with pytest.raises(ValueError, match="integer array"):
        MODULE.literal_arm(noninteger)

    negative = MODULE.fixed_unique_rows()
    negative["multiplicity"][2] = -1
    with pytest.raises(ValueError, match="non-negative"):
        MODULE.literal_arm(negative)


def test_fixture_separates_mechanical_identity_from_optimizer_positive_control():
    result = MODULE.build_receipt()
    equality = result["mechanical_equalities"]
    positive = result["optimization_positive_control"]
    assert result["status"] == "PASS_MACHINERY_VALIDATION_ONLY"
    assert result["scientific_pet_equivalence"] == "NOT_MEASURED"
    assert result["interval_coverage"] == "NOT_MEASURED"
    assert equality["per_event_loss_contribution_max_abs_delta"] <= 1e-12
    assert equality["projection_max_abs_delta"] <= 1e-12
    assert positive["optimizer_paths_differ"] is True
    assert positive["validation_monitor_paths_differ"] is True
    assert positive["is_pet_training_or_pet_bias_measurement"] is False


def test_contract_and_receipt_preserve_every_no_compute_boundary():
    text = CONTRACT.read_text(encoding="utf-8")
    receipt = MODULE.build_receipt()
    for prohibition in MODULE.PROHIBITIONS:
        assert prohibition in text
        assert receipt["prohibitions_applied"][prohibition] is True
    assert "No Slurm job, `srun`, GPU training" in text
    assert "cannot establish PET estimator equivalence" in text
    assert "Joseph must approve that proposal separately" in text
