#!/usr/bin/env python3
"""Integrity checks for the read-only PET Gate-6 strategy figures."""

import importlib.util
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "docs/orchestration/plot_pet_gate6_strategy_evidence.py"
SPEC = importlib.util.spec_from_file_location("pet_gate6_strategy_evidence", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
STRATEGY = (REPO / "docs/orchestration/PET-GATE6-STRATEGY-20260825.md").read_text(
    encoding="utf-8"
)


def test_strategy_sources_preserve_block_and_all_exact_prohibitions():
    evidence = MODULE.load_evidence()
    assert evidence["member_values"].shape == (5, 3)
    assert evidence["floor_values"].shape == (5, 3)
    assert MODULE.PROHIBITIONS == [
        "do_not_select_passing_subset",
        "do_not_construct_C_ML",
        "do_not_move_central",
        "do_not_start_leg_2",
        "do_not_retry_unchanged",
    ]


def test_reused_draw_is_bit_identical_to_member_one():
    evidence = MODULE.load_evidence()
    assert np.array_equal(evidence["floor_values"][0], evidence["member_values"][0])


def test_committed_floor_contraction_and_loss_proxy_are_transcribed():
    evidence = MODULE.load_evidence()
    assert np.all(np.diff(evidence["floor_range"]) < 0)
    assert np.all(np.diff(evidence["floor_sd"]) < 0)
    assert evidence["floor_range"][-1] == 0.06452911345365375
    assert np.array_equal(
        evidence["reco_loss_entry"],
        np.asarray([0.21884547173976898, 0.14990445971488953, 0.11996693909168243]),
    )
    assert np.array_equal(
        evidence["truth_loss_entry"],
        np.asarray([1.093201756477356, 0.9419060349464417, 0.8775396347045898]),
    )


def test_strategy_keeps_convergence_equivalence_and_coverage_distinct():
    assert "## Three questions that must not be collapsed" in STRATEGY
    assert "**Training convergence**" in STRATEGY
    assert "**Estimator equivalence**" in STRATEGY
    assert "**Interval coverage**" in STRATEGY
    assert "ordinary closure is a central-estimator test" in STRATEGY


def test_strategy_preserves_closed_oi126_and_no_compute_boundary():
    assert "does not activate that contingency or\nreopen" in STRATEGY
    assert "This request authorizes **no GPU run, no pseudoexperiment count" in STRATEGY
    assert "do_not_construct_C_ML" in STRATEGY
