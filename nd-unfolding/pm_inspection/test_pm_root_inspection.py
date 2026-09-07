#!/usr/bin/env python3
"""Focused tests for the bounded ROOT inspection producer and validator.

These do NOT need ROOT. They drive the pure classification path and the guards that do not
touch a ROOT file, which is where the failures that would matter live: confusing an
expected absence with a fault, letting runtime output land inside a checkout, and losing a
declared read silently.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pm_root_inspect as producer  # noqa: E402
import pm_root_validate as validator  # noqa: E402

REQUIRED = validator.REQUIRED
OPTIONAL = validator.OPTIONAL


def report_with(reads, declared=None, **extra):
    declared = declared if declared is not None else [r["read_id"] for r in reads]
    base = {"reads": reads, "declared_read_ids": declared}
    base.update(extra)
    return base


class ExpectedAbsenceIsNotAFault(unittest.TestCase):
    def test_absent_optional_key_is_COMPLETE(self):
        """hRowIndex5D absent from G is the answer to the question, not a failure."""
        report = report_with([
            {"read_id": "G:key_listing", "status": "read", "kind": REQUIRED},
            {"read_id": "G:hRowIndex5D", "status": "absent", "kind": OPTIONAL},
        ])
        code, findings = validator.classify(report)
        self.assertEqual(code, validator.EXIT_COMPLETE)
        self.assertEqual(findings["expected_optional_absences"], ["G:hRowIndex5D"])
        self.assertEqual(findings["required_read_failures"], [])

    def test_present_optional_key_is_also_COMPLETE(self):
        """Both answers to a conditional read are complete captures."""
        report = report_with([
            {"read_id": "G:hRowIndex5D", "status": "read", "kind": OPTIONAL},
        ])
        self.assertEqual(validator.classify(report)[0], validator.EXIT_COMPLETE)

    def test_unreadable_required_input_is_ERROR(self):
        report = report_with([
            {"read_id": "input:CV_central", "status": "unreadable", "kind": REQUIRED,
             "detail": "sha256 mismatch"},
        ])
        code, findings = validator.classify(report)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["required_read_failures"], ["input:CV_central"])

    def test_absent_required_object_is_ERROR_not_a_measurement(self):
        report = report_with([
            {"read_id": "EP_BeamAngleX_0:hXSecND_flat", "status": "absent",
             "kind": REQUIRED},
        ])
        self.assertEqual(validator.classify(report)[0], validator.EXIT_ERROR)


class MissingRecordsAreIncomplete(unittest.TestCase):
    def test_declared_read_with_no_record_is_INCOMPLETE(self):
        report = report_with(
            [{"read_id": "G:key_listing", "status": "read", "kind": REQUIRED}],
            declared=["G:key_listing", "CS:key_listing"])
        code, findings = validator.classify(report)
        self.assertEqual(code, validator.EXIT_INCOMPLETE)
        self.assertEqual(findings["missing_read_records"], ["CS:key_listing"])

    def test_a_required_failure_outranks_a_missing_record(self):
        report = report_with(
            [{"read_id": "input:G", "status": "unreadable", "kind": REQUIRED}],
            declared=["input:G", "G:key_listing"])
        self.assertEqual(validator.classify(report)[0], validator.EXIT_ERROR)


class ErrorEvidenceIsPreserved(unittest.TestCase):
    def test_producer_traceback_is_ERROR(self):
        report = report_with(
            [{"read_id": "input:G", "status": "read", "kind": REQUIRED}],
            traceback="Traceback (most recent call last): ...")
        code, findings = validator.classify(report)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["producer_traceback"])

    def test_unparseable_report_is_ERROR_and_still_writes_a_verdict(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "report.json"
            bad.write_text("{not json")
            out = Path(tmp) / "run"
            code = validator.main(["--report", str(bad), "--out", str(out)])
            self.assertEqual(code, validator.EXIT_ERROR)
            verdict = json.loads((out / "pm-inspection-verdict.json").read_text())
            self.assertEqual(verdict["terminal_branch"], "ERROR")

    def test_unknown_kind_is_ERROR_rather_than_silently_passing(self):
        report = report_with([
            {"read_id": "G:mystery", "status": "read", "kind": "something-else"},
        ])
        code, findings = validator.classify(report)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["records_with_unknown_kind"], ["G:mystery"])


class OutputMustLiveOutsideEveryCheckout(unittest.TestCase):
    def test_relative_out_dir_is_refused(self):
        with self.assertRaises(SystemExit):
            producer.refuse_output_inside_a_checkout(Path("relative/run"))

    def test_out_dir_inside_a_git_checkout_is_refused(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / ".git").mkdir()
            with self.assertRaises(SystemExit):
                producer.refuse_output_inside_a_checkout(root / "state" / "run")

    def test_out_dir_outside_any_checkout_is_accepted(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            producer.refuse_output_inside_a_checkout(Path(tmp).resolve() / "run")


class DeclaredReadsCoverThePredeclaration(unittest.TestCase):
    def setUp(self):
        self.bindings = json.loads(
            (HERE / "INPUT-BINDINGS-20260908.json").read_text())

    def test_thirteen_inputs_exactly(self):
        self.assertEqual(len(self.bindings["inputs"]), 13)

    def test_five_bands_ten_endpoints(self):
        self.assertEqual(len(self.bindings["bands"]), 5)
        endpoints = [e for e in self.bindings["inputs"] if e["id"].startswith("EP_")]
        self.assertEqual(len(endpoints), 10)

    def test_CS_is_not_hashed_at_runtime_and_says_why(self):
        cs = next(e for e in self.bindings["inputs"] if e["id"] == "CS")
        self.assertFalse(cs["verify_digest_at_runtime"])
        self.assertIn("NOT re-hashed", cs["digest_limitation"])
        self.assertEqual(cs["digest_provenance"], "committed-historical")

    def test_current_digests_are_labelled_current_not_historical(self):
        cv = next(e for e in self.bindings["inputs"] if e["id"] == "CV_central")
        self.assertEqual(cv["digest_provenance"], "measured-current-2026-09-08")

    def test_bindings_do_not_claim_historical_production_input(self):
        """The PM-4 gap must be stated in the bindings, not left to a reader's memory."""
        disclaimer = self.bindings["what_these_digests_are_NOT"]
        self.assertIn("NOT evidence", disclaimer)
        self.assertIn("PM-4 provenance gap", disclaimer)
        self.assertIn("reconstructed through G's producer-input route", disclaimer)
        self.assertNotIn("read from G'", disclaimer.replace("never 'read from G'", ""))

    def test_declared_ids_are_unique_and_cover_every_input(self):
        ids = producer.declared_read_ids(self.bindings)
        self.assertEqual(len(ids), len(set(ids)))
        for entry in self.bindings["inputs"]:
            self.assertIn(f"input:{entry['id']}", ids)

    def test_grid_nbins_matches_p4_lib(self):
        self.assertEqual(self.bindings["grid_nbins"], 65856)


if __name__ == "__main__":
    unittest.main(verbosity=2)
