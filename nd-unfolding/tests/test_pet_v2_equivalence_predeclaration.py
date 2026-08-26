#!/usr/bin/env python3
"""CPU-only guards for the PET-v2 full fixed-draw no-launch proposal."""

import importlib.util
import json
import math
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "docs/orchestration/derive_pet_v2_equivalence_predeclaration.py"
RECEIPT = (
    REPO
    / "docs/orchestration/state/pet-v2-fixed-draw-equivalence-proposal-20260825.json"
)
CONTRACT = (
    REPO
    / "docs/orchestration/PREDECLARATION-20260825-pet-v2-fixed-draw-equivalence.md"
)
GATE6 = REPO / "docs/orchestration/state/gate6-member-trajectories-result-56847059.json"

SPEC = importlib.util.spec_from_file_location("derive_pet_v2_equivalence_predeclaration", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PROPOSAL = MODULE.build_proposal()


def test_committed_receipt_is_exact_deterministic_render():
    assert json.loads(RECEIPT.read_text(encoding="utf-8")) == PROPOSAL


def test_fixed_draw_is_rederived_and_source_bound():
    draw = PROPOSAL["fixed_draw"]
    assert draw["bootstrap_seed"] == 50000
    assert draw["source_G2_sha256"] == (
        "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
    )
    assert draw["factors"]["data"] == {
        "n": 4116128,
        "sha256": "d151dd197c9662da4604c9609d761887d38437d510484efdf851c8de1028ca37",
        "sum": 4118323,
        "zeros": 1513511,
        "maximum": 9,
    }
    assert draw["factors"]["signal"]["n"] == 49152885
    assert draw["factors"]["background"]["n"] == 564591


def test_thresholds_follow_the_predeclared_arithmetic():
    threshold = PROPOSAL["threshold_derivation"]
    sd = threshold["F_sd_ddof1"]
    same = math.ceil(sd * 10_000.0) / 10_000.0
    margin = round(2.0 * same, 4)
    assert same == threshold["same_arm_validity_cap_S"] == 0.0251
    assert margin == threshold["cross_arm_materiality_margin_M"] == 0.0502
    assert threshold["existing_single_effect_MDE"] == 0.0695920150567661
    assert threshold["existing_MDE_is_annotation_not_gate"] is True
    assert "not a regional push" in threshold["scope_limit"]


def test_terminal_logic_requires_same_arm_and_both_cross_arm_comparisons():
    terminal = PROPOSAL["terminal_classification"]
    assert terminal["order"][0] == "INVALID_OR_NOISY"
    assert "D_same exceeds S=0.0251" in terminal["INVALID_OR_NOISY"]
    assert "D_cross_max <= M=0.0502" in (
        terminal["EQUIVALENT_AT_5P02_PERCENT_OPERATIONAL_RESOLUTION"]
    )
    different = terminal["MATERIALLY_DIFFERENT_IN_THIS_FIXED_DRAW"]
    assert "D_cross_min > 0.0502" in different
    assert "D_cross_min > 2*D_same" in different
    assert terminal["MIXED_OR_UNRESOLVED"].endswith("no favorable default")


def test_determinism_is_fail_closed_but_does_not_remove_same_arm_control():
    controls = PROPOSAL["determinism_and_same_arm_controls"]
    assert controls["required_environment_before_interpreter_start"] == {
        "PYTHONHASHSEED": "42",
        "TF_DETERMINISTIC_OPS": "1",
        "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
    }
    assert controls["fallback"].startswith("NONE")
    assert "A100-SXM4-80GB" in controls["hardware"]
    assert "fresh independent processes" in controls["same_arm"]


def test_resource_estimate_is_recomputed_from_all_historical_records():
    evidence = PROPOSAL["resource_evidence"]
    target = evidence["target_array"]
    train = evidence["training_array"]
    derivation = evidence["derivation"]
    assert len(target["elapsed_seconds"]) == target["summary"]["n_completed"] == 50
    assert len(train["elapsed_seconds"]) == train["summary"]["n_completed"] == 50
    assert target["summary"]["maximum_seconds"] == 2770
    assert train["summary"]["maximum_seconds"] == 11465
    assert train["summary"]["median_seconds"] == 10855.0
    assert math.isclose(derivation["expected_a100_hours_unrounded"], 12.642708333333331)
    assert derivation["expected_a100_hours_rounded_up"] == 13.0
    ceiling = PROPOSAL["proposed_resource_ceiling_if_later_authorized"]
    assert ceiling["allocation_ceiling_a100_hours"] == 18
    assert ceiling["coverage_or_family_compute_authorized"] is False


def test_future_operands_and_authorization_fail_closed_before_submission():
    contract = PROPOSAL["guarded_execution_contract"]
    operands = contract["future_required_operands"]
    assert len(operands) == 5
    assert all(item["sha256"] is None for item in operands)
    assert all(item["status"] == "NOT_IMPLEMENTED_OR_HASH_BOUND" for item in operands)
    assert PROPOSAL["launchable"] is False
    assert PROPOSAL["compute_decision"] == "HOLD_FOR_JOSEPH_AND_EXECUTABLE_IMPLEMENTATION"
    assert contract["guard_prefix"].startswith("${PETV2_PYTHON} ${PETV2_CODE_ROOT}")
    assert "has no default" in contract["python_supplier"]
    assert "outside the primary checkout" in contract["artifact_supplier"]
    assert "each Python process" in contract["subprocess_rule"]
    assert "exits before sbatch" in contract["authorization_guard"]


def test_exact_gate6_prohibitions_and_non_authorizations_are_preserved():
    gate6 = json.loads(GATE6.read_text(encoding="utf-8"))
    assert gate6["family_verdict"] == "BLOCK_GATE6_ML_ENSEMBLE"
    assert gate6["prohibitions_applied"] == list(MODULE.PROHIBITIONS)
    applied = PROPOSAL["governing_gate6"]["prohibitions_applied"]
    cannot = PROPOSAL["what_every_terminal_result_cannot_authorize"]
    for prohibition in MODULE.PROHIBITIONS:
        assert applied[prohibition] is True
        assert prohibition in cannot
    assert any("interval coverage" in item for item in cannot)
    assert any("note" in item for item in cannot)


def test_human_contract_names_every_operand_threshold_and_decision_boundary():
    text = CONTRACT.read_text(encoding="utf-8")
    for operand in MODULE.FUTURE_OPERANDS:
        assert Path(operand).name in text
    for prohibition in MODULE.PROHIBITIONS:
        assert prohibition in text
    assert "`S = ceil" not in text  # equation is a plain fenced operand, not a new code symbol
    assert "S = ceil(F_sd_ddof1" in text
    assert "M = 2 S" in text
    assert "13 A100 h" in text
    assert "do not authorize A100 compute yet" in text
    assert "launchable: false" in text
