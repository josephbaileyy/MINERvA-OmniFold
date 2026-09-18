#!/usr/bin/env python3
"""The pre-submission gate, with the REAL incident as its negative control.

Job `58507305`'s submission command is `test_the_historical_failing_command_is_refused` below,
verbatim in shape. It must be refused, and the refusal must name `MNV_THREAD_GRID` and report the
exact truncation that happened: arrived as `1`, dropped `2`, `4`, `8`.

⚠ A FIXTURE BUILT FROM THE RULE COULD NOT DISAGREE WITH IT. So the negative control here is not a
constructed example -- it is the command that actually ran, and the assertion is against the
observed outcome (`thread_grid: [1]` in the job's record), not against my model of Slurm.

Slurm was not wrong; it did what its documentation says. The defect was in the command, which is
why this checks commands.
"""
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "nd-unfolding" / "check_sbatch_export.py"
sys.path.insert(0, str(REPO / "nd-unfolding"))

import check_sbatch_export as C  # noqa: E402

HISTORICAL = ("sbatch --export=ALL,MNV_CODE_ROOT=/w,MNV_OUT=/d/rec.json,"
              "MNV_R5_RECEIPT=/d/r5.json,MNV_DECLARED_TASK_HOURS=0.25,MNV_ROWS=200000,"
              "MNV_THREAD_GRID=1,2,4,8,HOME=/global/homes/j/josephrb "
              "--output=/d/o run_determinism_probe.sh")
CORRECTED = HISTORICAL.replace("MNV_THREAD_GRID=1,2,4,8", "MNV_THREAD_GRID=1:2:4:8")


def _run(command):
    return subprocess.run([sys.executable, str(TOOL), "--command", command],
                          capture_output=True, text=True)


class TheHistoricalIncident(unittest.TestCase):
    def test_the_historical_failing_command_is_refused(self):
        r = _run(HISTORICAL)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("MNV_THREAD_GRID", r.stderr)

    def test_the_refusal_reports_the_truncation_that_actually_happened(self):
        """The job's record showed `thread_grid: [1]`. The tool must say `1`, and name the tail."""
        r = _run(HISTORICAL)
        self.assertIn("would arrive as '1'", r.stderr)
        for lost in ("'2'", "'4'", "'8'"):
            self.assertIn(lost, r.stderr)

    def test_the_corrected_command_passes(self):
        r = _run(CORRECTED)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("no assignment would be truncated", r.stdout)

    def test_only_the_separator_differs_between_the_two_fixtures(self):
        """Guards the controls themselves: if they diverged in some other way, the pass/fail
        difference would no longer isolate the comma."""
        self.assertEqual(HISTORICAL.replace("1,2,4,8", "SEP"), CORRECTED.replace("1:2:4:8", "SEP"))


class WhatCountsAsTruncation(unittest.TestCase):
    def test_a_bare_name_after_an_assignment_is_not_truncation(self):
        """`--export=ALL,A=1,PATH` exports PATH's current value; the list item is legitimate."""
        self.assertEqual(C.findings(["sbatch", "--export=ALL,A=1,PATH", "x.sh"]), [])

    def test_a_following_assignment_is_not_truncation(self):
        self.assertEqual(C.findings(["sbatch", "--export=ALL,A=1,B=2", "x.sh"]), [])

    def test_ALL_NONE_NIL_are_list_items(self):
        for word in ("ALL", "NONE", "NIL"):
            self.assertEqual(C.findings(["sbatch", f"--export=A=1,{word}", "x.sh"]), [], word)

    def test_a_trailing_comma_value_is_caught(self):
        found = C.findings(["sbatch", "--export=ALL,GRID=1,2", "x.sh"])
        self.assertEqual(found, [("GRID", "1", ["2"])])

    def test_multiple_truncated_assignments_are_all_reported(self):
        found = C.findings(["sbatch", "--export=A=1,2,B=3,4,5", "x.sh"])
        self.assertEqual(found, [("A", "1", ["2"]), ("B", "3", ["4", "5"])])

    def test_the_space_separated_form_is_also_read(self):
        """`--export VALUE` as two tokens, not `--export=VALUE`."""
        found = C.findings(["sbatch", "--export", "ALL,GRID=1,2", "x.sh"])
        self.assertEqual(found, [("GRID", "1", ["2"])])

    def test_a_non_sbatch_command_is_refused_rather_than_passed(self):
        """Silence on an unrecognised command would read as a clean check."""
        r = _run("srun --export=ALL,GRID=1,2 x.sh")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("does not look like an sbatch command", r.stderr)

    def test_a_command_with_no_export_is_reported_as_zero_checked(self):
        """Not an error, but it must not claim to have checked something."""
        r = _run("sbatch --time=00:15:00 x.sh")
        self.assertEqual(r.returncode, 0)
        self.assertIn("0 --export value(s) checked", r.stdout)


class TheLauncherKeepsItsOwnSecondLine(unittest.TestCase):
    def test_the_in_job_refusal_still_exists(self):
        """This tool runs before an allocation exists; rc 14 fires after a node is assigned. Both
        are wanted, and neither replaces the other."""
        sh = (REPO / "nd-unfolding" / "run_determinism_probe.sh").read_text()
        self.assertIn("exit 14", sh)


if __name__ == "__main__":
    unittest.main()
