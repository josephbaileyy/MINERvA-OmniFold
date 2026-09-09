#!/usr/bin/env python3
"""The validator's output path: a verdict artifact, or a reported failure to write one.

Round 3 moved every classification failure inside a guard so that a malformed report ends
as a written ERROR verdict rather than a traceback. The WRITE ITSELF stayed outside that
guard, so three ordinary output-path shapes -- an ``--out`` that is a regular file, a
verdict path that is already a directory, and an unwritable ``--out`` -- each ended in a
traceback with no artifact. The contract's ``otherwise`` branch still selects
``capture-error`` from the return code, so the branch was selected; what was lost was the
artifact ``preservation_behavior`` lists.

These tests drive ``main`` end to end against a report the REAL producer wrote, because
the classification that must survive a write failure is a real classification.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pm_root_validate as validator  # noqa: E402
from test_pm_producer_driven import ATTEMPT, Tree  # noqa: E402


class Run:
    """A temporary tree, a producer report on disk, and somewhere to put a verdict."""

    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.tree = Tree(tmp)
        self.code, self.report = self.tree.run_producer()
        self.report_path = self.tree.out / "pm-inspection-report.json"
        self.out = self.tmp / "verdict-dir"

    def validate(self, out=None, attempt=ATTEMPT):
        """Return (exit_code, the one line main printed)."""
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = validator.main([
                "--report", str(self.report_path),
                "--bindings", str(self.tree.bindings_path),
                "--attempt-id", attempt,
                "--out", str(self.out if out is None else out)])
        return code, json.loads(stdout.getvalue().strip().splitlines()[-1])

    def written(self, out=None):
        path = (self.out if out is None else Path(out)) / validator.VERDICT_FILENAME
        return json.loads(path.read_text())


class AVerdictIsWrittenOrItsAbsenceIsReported(unittest.TestCase):
    def test_the_control_writes_a_verdict_and_returns_its_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            code, printed = run.validate()
            self.assertEqual(code, validator.EXIT_COMPLETE)
            self.assertEqual(printed["terminal_branch"], "COMPLETE")
            self.assertEqual(run.written()["terminal_branch"], "COMPLETE")
            self.assertEqual(run.written()["validator_exit_code"],
                             validator.EXIT_COMPLETE)

    def test_out_that_is_a_regular_file_is_ERROR_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            occupied = run.tmp / "not-a-directory"
            occupied.write_text("I am a file\n")
            code, printed = run.validate(out=occupied)
            self.assertEqual(code, validator.EXIT_ERROR)
            self.assertIn("verdict_not_written", printed)
            # The classification is not lost just because it could not be filed.
            self.assertEqual(printed["classification_that_could_not_be_written"],
                             "COMPLETE")

    def test_a_verdict_path_that_is_a_directory_is_ERROR_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            (run.out / validator.VERDICT_FILENAME).mkdir(parents=True)
            code, printed = run.validate()
            self.assertEqual(code, validator.EXIT_ERROR)
            self.assertIn("verdict_not_written", printed)

    @unittest.skipIf(os.geteuid() == 0, "root ignores the mode bits")
    def test_an_unwritable_out_is_ERROR_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            run.out.mkdir(parents=True)
            run.out.chmod(0o500)
            try:
                code, printed = run.validate()
            finally:
                run.out.chmod(0o700)
            self.assertEqual(code, validator.EXIT_ERROR)
            self.assertIn("verdict_not_written", printed)

    def test_an_unreadable_report_still_writes_a_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            run.report_path = run.tmp / "there-is-no-report-here.json"
            code, printed = run.validate()
            self.assertEqual(code, validator.EXIT_ERROR)
            self.assertEqual(printed["terminal_branch"], "ERROR")
            self.assertIn("cannot read report", run.written()["reason"])

    def test_a_report_that_is_not_json_still_writes_a_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            run.report_path.write_bytes(b"\x00 not json at all")
            code, _ = run.validate()
            self.assertEqual(code, validator.EXIT_ERROR)
            self.assertEqual(run.written()["terminal_branch"], "ERROR")


class AVerdictIsNeverOverwritten(unittest.TestCase):
    """preserve-first, the same rule the producer applies to its report. Review replaced a
    COMPLETE verdict with an INCOMPLETE one over identical argv, and nothing recorded that
    the first had ever existed."""

    def test_the_first_verdict_survives_a_second_classification(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            self.assertEqual(run.validate()[0], validator.EXIT_COMPLETE)
            first = (run.out / validator.VERDICT_FILENAME).read_bytes()

            # Review's reproducer: drop a record and classify again, same argv.
            report = json.loads(run.report_path.read_text())
            report["reads"] = report["reads"][:-1]
            run.report_path.write_text(json.dumps(report, indent=2) + "\n")

            code, printed = run.validate()
            self.assertEqual(code, validator.EXIT_ERROR)
            self.assertIn("never overwritten", printed["verdict_not_written"])
            self.assertEqual(printed["classification_that_could_not_be_written"],
                             "INCOMPLETE")
            self.assertEqual((run.out / validator.VERDICT_FILENAME).read_bytes(), first)

    def test_a_fresh_run_directory_is_how_a_second_classification_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            self.assertEqual(run.validate()[0], validator.EXIT_COMPLETE)
            second = run.tmp / "verdict-dir-attempt-2"
            self.assertEqual(run.validate(out=second)[0], validator.EXIT_COMPLETE)
            self.assertEqual(run.written(second)["terminal_branch"], "COMPLETE")


class OutputStillMayNotLandInsideACheckout(unittest.TestCase):
    def test_a_relative_out_is_refused_before_anything_is_classified(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            with self.assertRaises(SystemExit):
                run.validate(out=Path("relative/verdict"))

    def test_an_out_inside_a_checkout_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Run(tmp)
            repo = run.tmp / "repo"
            (repo / ".git").mkdir(parents=True)
            with self.assertRaises(SystemExit):
                run.validate(out=repo / "state" / "verdict")


if __name__ == "__main__":
    unittest.main(verbosity=2)
