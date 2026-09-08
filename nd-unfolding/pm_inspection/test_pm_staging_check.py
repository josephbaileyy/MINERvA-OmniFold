#!/usr/bin/env python3
"""Tests for the pre-approval check of a staged item. Nothing here stages or approves.

Each test names the thing that would have reached a human's TTY unnoticed.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_staged_item as checker  # noqa: E402
import pm_root_inspect as producer  # noqa: E402


def good_item() -> dict:
    """An item staged exactly as reviewed."""
    return {
        "id": checker.CAMPAIGN_ID,
        "kind": "compute",
        "timeout_seconds": int(producer.STAGED_TIMEOUT_SECONDS),
        "argv": checker.expected_argv(checker.DEFAULT_EXPECT_ROOT),
        "bindings": [{"path": checker.BINDINGS_PATH, "sha256": "0" * 64}],
        "git_head": "a" * 40,
        "proposal_digest": "b" * 64,
        "campaign_contract_path": checker.CONTRACT_PATH,
        "campaign_contract": {
            "campaign_id": checker.CAMPAIGN_ID,
            "output_namespace": "queue-claim-run-directory",
            "accounting": {"expects_scheduler_tasks": True},
            "maximum_cost": {"gpu_task_hours": 0.0, "cpu_task_hours": 0.5,
                             "wall_hours": 0.5},
            "terminal_validator": {
                "cwd": ".",
                "argv": ["/usr/bin/python3.11", "nd-unfolding/mnv_guarded_run.py",
                         "--expect-root", checker.DEFAULT_EXPECT_ROOT,
                         "--label", "pm-root-inspection-terminal-validator",
                         "--", "nd-unfolding/pm_inspection/pm_root_validate.py",
                         "--bindings", checker.BINDINGS_PATH,
                         "--campaign-mode", "required"],
            },
        },
    }


class ThePositiveControl(unittest.TestCase):
    """A checker that refuses everything proves nothing."""

    def test_the_reviewed_item_passes(self):
        self.assertEqual(checker.check_item(good_item(), expect_head="a" * 40), [])


class TheStageDefaultIsCaughtBeforeApproval(unittest.TestCase):
    def test_timeout_600_is_refused_by_name(self):
        item = good_item()
        item["timeout_seconds"] = 600          # campaignctl's default
        findings = checker.check_item(item)
        self.assertEqual(len(findings), 1)
        self.assertIn("killed mid-wait", findings[0])
        self.assertIn("do NOT approve", findings[0].replace("Do NOT", "do NOT"))

    def test_a_timeout_that_starves_the_validator_is_refused(self):
        item = good_item()
        item["timeout_seconds"] = 1790         # under the wall, over what leaves a validator
        findings = "\n".join(checker.check_item(item))
        self.assertIn("validator would not be started", findings)

    def test_a_smaller_wall_than_the_budget_was_sized_against_is_refused(self):
        item = good_item()
        item["campaign_contract"]["maximum_cost"]["wall_hours"] = 0.25
        findings = "\n".join(checker.check_item(item))
        self.assertIn("the launcher's budget was sized against the larger number", findings)


class TheStaleContractIsCaught(unittest.TestCase):
    """A copy with a filesystem namespace and --report/--out literals exists on another branch."""

    def test_filesystem_output_namespace_is_refused(self):
        item = good_item()
        item["campaign_contract"]["output_namespace"] = "/pscratch/sd/j/josephrb/pm-inspection-20260908"
        self.assertIn("claim-derived contract is the one that was reviewed",
                      "\n".join(checker.check_item(item)))

    def test_report_and_out_literals_are_refused(self):
        item = good_item()
        item["campaign_contract"]["terminal_validator"]["argv"] += ["--report", "/x.json"]
        self.assertIn("--report/--out literals", "\n".join(checker.check_item(item)))

    def test_a_validator_not_in_required_mode_is_refused(self):
        item = good_item()
        argv = item["campaign_contract"]["terminal_validator"]["argv"]
        item["campaign_contract"]["terminal_validator"]["argv"] = [
            a for a in argv if a != "--campaign-mode"]
        self.assertIn("--campaign-mode required", "\n".join(checker.check_item(item)))


class TheArgvMustBeTheReviewedArgv(unittest.TestCase):
    def test_a_changed_walltime_is_refused(self):
        item = good_item()
        item["argv"][item["argv"].index("--minutes") + 1] = "25"
        self.assertIn("staged argv is not the reviewed argv",
                      "\n".join(checker.check_item(item)))

    def test_an_unguarded_producer_is_refused(self):
        item = good_item()
        item["argv"] = [checker.OUTER_PYTHON,
                        "nd-unfolding/pm_inspection/pm_root_inspect.py", "--mode", "launch"]
        self.assertIn("staged argv is not the reviewed argv",
                      "\n".join(checker.check_item(item)))

    def test_a_different_execution_checkout_is_refused_unless_declared(self):
        item = good_item()          # staged against the old pin
        findings = checker.check_item(item, expect_root="/pscratch/sd/j/josephrb/exec-NEW")
        self.assertIn("staged argv is not the reviewed argv", "\n".join(findings))

    def test_the_walltime_tracks_the_launcher_and_cannot_drift(self):
        self.assertIn(str(producer.DEFAULT_MINUTES),
                      checker.expected_argv(checker.DEFAULT_EXPECT_ROOT))


class TheHeadMustBeTheOneReviewed(unittest.TestCase):
    def test_a_different_head_is_refused_when_one_is_declared(self):
        findings = checker.check_item(good_item(), expect_head="c" * 40)
        self.assertIn("not the reviewed", "\n".join(findings))

    def test_no_declared_head_checks_nothing_about_head(self):
        # Stated so nobody reads a PASS without --expect-head as a statement about HEAD.
        self.assertEqual(checker.check_item(good_item()), [])


class TheExitCodeIsTheGate(unittest.TestCase):
    def test_a_bad_item_exits_nonzero_and_prints_no_approve_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            item = good_item()
            item["timeout_seconds"] = 600
            path = Path(tmp) / "item.json"
            path.write_text(json.dumps(item))
            from io import StringIO
            from contextlib import redirect_stdout
            buffer = StringIO()
            with redirect_stdout(buffer):
                code = checker.main(["--item", str(path)])
            self.assertEqual(code, 1)
            self.assertNotIn("approve --id", buffer.getvalue())

    def test_a_good_item_exits_zero_and_says_it_is_not_an_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "item.json"
            path.write_text(json.dumps(good_item()))
            from io import StringIO
            from contextlib import redirect_stdout
            buffer = StringIO()
            with redirect_stdout(buffer):
                code = checker.main(["--item", str(path), "--expect-head", "a" * 40])
            self.assertEqual(code, 0)
            self.assertIn("NOT an approval", buffer.getvalue())
            self.assertIn("approve --id", buffer.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
