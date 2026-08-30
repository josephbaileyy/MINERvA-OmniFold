#!/usr/bin/env python3
"""Pure regression tests for the GAP-3 reco truncation audit contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


MODULE_PATH = Path(__file__).with_name("audit_reco_truncation.py")
LAUNCHER_PATH = Path(__file__).with_name("sbatch_gap3_reco_truncation_audit.sh")
SPEC = importlib.util.spec_from_file_location("audit_reco_truncation", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {MODULE_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def test_safe_fraction() -> None:
    assert AUDIT.safe_fraction(2.0, 8.0) == 0.25
    assert AUDIT.safe_fraction(0.0, 8.0) == 0.0
    assert AUDIT.safe_fraction(1.0, 0.0) is None
    assert AUDIT.safe_fraction(float("nan"), 1.0) is None


def test_fraction_derivation_keeps_operands() -> None:
    operands = {
        "events": 10.0,
        "cap_events": 4.0,
        "clusters_total": 100.0,
        "clusters_discarded": 5.0,
        "energy_total_mev": 1_000.0,
        "energy_discarded_mev": 20.0,
    }
    result = AUDIT.derive_fractions(operands)
    assert all(result[key] == value for key, value in operands.items())
    assert result["cap_event_fraction"] == 0.4
    assert result["discarded_cluster_fraction"] == 0.05
    assert result["discarded_energy_fraction"] == 0.02


def test_combination_adds_operands_before_division() -> None:
    first = {
        "events": 2.0,
        "cap_events": 1.0,
        "clusters_total": 20.0,
        "clusters_discarded": 2.0,
        "energy_total_mev": 200.0,
        "energy_discarded_mev": 4.0,
    }
    second = {
        "events": 8.0,
        "cap_events": 1.0,
        "clusters_total": 80.0,
        "clusters_discarded": 1.0,
        "energy_total_mev": 800.0,
        "energy_discarded_mev": 6.0,
    }
    combined = AUDIT.derive_fractions(AUDIT.add_metric_payloads(first, second))
    assert combined["cap_event_fraction"] == 0.2
    assert combined["discarded_cluster_fraction"] == 0.03
    assert combined["discarded_energy_fraction"] == 0.01


def test_frozen_contract_operands() -> None:
    assert AUDIT.CAP == 12
    assert AUDIT.EXPECTED_SELECTED_ROWS == {
        "signal": 20_573_521,
        "data": 4_116_128,
        "background": 564_591,
    }
    assert len(AUDIT.PT_EDGES) - 1 == 15
    assert len(AUDIT.PPARALLEL_EDGES) - 1 == 19
    assert len(AUDIT.EAVAIL_EDGES) - 1 == 7
    assert len(AUDIT.Q3_EDGES) - 1 == 7


def test_launcher_resource_and_authorization_contract() -> None:
    launcher = LAUNCHER_PATH.read_text(encoding="utf-8")
    assert "#SBATCH --constraint=cpu" in launcher
    assert "#SBATCH --cpus-per-task=8" in launcher
    assert "#SBATCH --time=04:00:00" in launcher
    assert "#SBATCH --gres" not in launcher
    assert "PET-G6-GAP3-RECO-TRUNCATION-20260830-ONE-SCAN" in launcher
    assert "EXPECTED_GATE6_RECEIPT_SHA256" in launcher


if __name__ == "__main__":
    test_safe_fraction()
    test_fraction_derivation_keeps_operands()
    test_combination_adds_operands_before_division()
    test_frozen_contract_operands()
    test_launcher_resource_and_authorization_contract()
    print("PASS: GAP-3 reco truncation pure contract tests")
