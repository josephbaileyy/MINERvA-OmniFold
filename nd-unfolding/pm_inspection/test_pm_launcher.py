#!/usr/bin/env python3
"""End-to-end launch-mode tests. No scheduler is contacted; every call is mocked.

Each test names the reviewer finding it pins. The successful path is here too: a launcher that
refuses everything is not correct either.
"""
from __future__ import annotations

import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pm_root_inspect as producer  # noqa: E402

ENV = producer.CAMPAIGN_TASK_IDS_FILE_ENV


def run(returncode=0, stdout="", stderr=""):
    return mock.Mock(returncode=returncode, stdout=stdout, stderr=stderr)


class FakeClock:
    """A monotonic clock the test drives. Nothing here sleeps or waits for real."""

    def __init__(self, start=0.0):
        self.now = float(start)
        self.naps: list[float] = []

    def read(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.naps.append(seconds)
        self.now += seconds

    def advance(self, seconds: float) -> None:
        self.now += seconds


def fresh_budget():
    """A budget with its whole wall still in front of it."""
    return producer.Budget(clock=FakeClock().read)


def clock_that_jumps_after_the_first_read(jump=2000.0):
    """Whole budget at construction, none of it by the first call that asks."""
    state = {"first": True}

    def read():
        if state["first"]:
            state["first"] = False
            return 0.0
        return jump

    return read


class Claim:
    """A queue-shaped claim directory outside any checkout."""

    def __init__(self, tmp):
        self.dir = Path(tmp) / "runs" / "pm-root-inspection-20260908"
        self.dir.mkdir(parents=True)
        self.ids = self.dir / "task-ids.json"

    def args(self, **over):
        base = dict(mode="launch", inner_python="/conda/bin/python",
                    expect_root=Path("/exec"), account="m3246", qos="debug",
                    minutes=producer.DEFAULT_MINUTES, comment="tok", bindings=Path("/bound dir/inputs.json"),
                    data_root=Path("/data"))
        base.update(over)
        return mock.Mock(**base)


class SubmissionReceiptIsValidatedBeforeAnythingCanLoseIt(unittest.TestCase):
    def test_multiline_receipt_is_unknown_not_truncated(self):
        with self.assertRaises(producer.SubmissionUncertain) as caught:
            producer.parse_parsable_receipt("5551212;perlmutter\n5551213;perlmutter\n")
        self.assertIn("not one line", str(caught.exception))
        self.assertIn("nothing will be cancelled", str(caught.exception))

    def test_prose_receipt_is_unknown(self):
        with self.assertRaises(producer.SubmissionUncertain):
            producer.parse_parsable_receipt("Submitted batch job 42\n")

    def test_cluster_suffix_is_accepted(self):
        self.assertEqual(producer.parse_parsable_receipt("5551212;perlmutter\n"), "5551212")


class KnownIdSurvivesAWriteFailure(unittest.TestCase):
    def test_task_ids_write_failure_keeps_the_id_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            claim = Claim(tmp)
            claim.ids.mkdir()  # the write target is a DIRECTORY: IsADirectoryError
            calls = []

            def fake(argv, **kw):
                calls.append(argv[0])
                if argv[0] == "sbatch":
                    return run(0, "5551212\n")
                if argv[0] == "sacct":
                    return run(0, "RUNNING\n")   # never terminal: cleanup must run
                return run(0)

            clock = FakeClock()
            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                code = producer.launch(
                    claim.args(), claim.dir, claim.ids, clock=clock.read,
                    sleeper=lambda _s: clock.advance(
                        producer.LAUNCHER_BUDGET_SECONDS
                        - producer.CLEANUP_RESERVE_SECONDS))
            self.assertEqual(code, producer.EXIT_ERROR)
            # The finding: a bare IsADirectoryError used to escape here, losing the id.
            recorded = json.loads((claim.dir / "task-ids-write-failed.txt").read_text())
            self.assertEqual(recorded["job_id"], "5551212")
            self.assertEqual(calls.count("scancel"), 1)


class UnknownStateNeverReadsAsTerminal(unittest.TestCase):
    def test_sacct_rc1_with_completed_stdout_is_not_terminal(self):
        with mock.patch.object(producer.subprocess, "run",
                               return_value=run(1, "COMPLETED\n")):
            state, detail = producer.job_state("5551212", budget=fresh_budget())
        self.assertIsNone(state)
        self.assertIn("exited 1", detail)

    def test_sacct_timeout_is_not_terminal(self):
        with mock.patch.object(producer.subprocess, "run",
                               side_effect=subprocess.TimeoutExpired("sacct", 60)):
            state, _ = producer.job_state("5551212", budget=fresh_budget())
        self.assertIsNone(state)

    def test_sacct_timeout_after_submission_still_cancels(self):
        with tempfile.TemporaryDirectory() as tmp:
            claim = Claim(tmp)
            calls = []

            def fake(argv, **kw):
                calls.append(argv[0])
                if argv[0] == "sbatch":
                    return run(0, "5551212\n")
                if argv[0] == "sacct":
                    raise subprocess.TimeoutExpired("sacct", 60)
                return run(0)

            clock = FakeClock()
            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                code = producer.launch(
                    claim.args(), claim.dir, claim.ids, clock=clock.read,
                    sleeper=lambda _s: clock.advance(
                        producer.LAUNCHER_BUDGET_SECONDS
                        - producer.CLEANUP_RESERVE_SECONDS))
            self.assertEqual(code, producer.EXIT_ERROR)
            self.assertEqual(calls.count("scancel"), 1)


class CancelRequestIsNotProofOfTermination(unittest.TestCase):
    def test_scancel_rc1_is_unresolved_not_cancelled(self):
        def fake(argv, **kw):
            return run(1, "", "denied") if argv[0] == "scancel" else run(0, "RUNNING\n")

        with mock.patch.object(producer.subprocess, "run", side_effect=fake):
            result = producer.cancel_this_job("5551212", budget=fresh_budget())
        self.assertEqual(result["scancel_returncode"], 1)
        self.assertEqual(result["cleanup"], "UNRESOLVED")
        self.assertIsNone(result["terminal_state"])

    def test_verified_terminal_is_reported_as_such(self):
        def fake(argv, **kw):
            return run(0) if argv[0] == "scancel" else run(0, "CANCELLED\n")

        with mock.patch.object(producer.subprocess, "run", side_effect=fake):
            result = producer.cancel_this_job("5551212", budget=fresh_budget())
        self.assertEqual(result["cleanup"], "verified-terminal")

    def test_cancel_names_only_the_id(self):
        with mock.patch.object(producer.subprocess, "run", return_value=run(0)) as r:
            producer.cancel_this_job("5551212", budget=fresh_budget())
        argv = r.call_args_list[0][0][0]
        self.assertEqual(argv, ["scancel", "5551212"])


class TheWrapStringSurvivesSpaces(unittest.TestCase):
    def test_bindings_path_with_a_space_stays_one_argument(self):
        with tempfile.TemporaryDirectory() as tmp:
            claim = Claim(tmp)
            captured = {}

            def fake(argv, **kw):
                if argv[0] == "sbatch":
                    captured["wrap"] = argv[argv.index("--wrap") + 1]
                    return run(0, "5551212\n")
                return run(0, "COMPLETED\n")

            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                producer.launch(claim.args(), claim.dir, claim.ids)
            parts = shlex.split(captured["wrap"])
            self.assertIn("/bound dir/inputs.json", parts)


class LaunchRequiresTheQueue(unittest.TestCase):
    def test_launch_without_the_queue_variable_refuses(self):
        with mock.patch.dict(producer.os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as caught:
                producer.main(["--mode", "launch", "--bindings", "/b.json",
                               "--data-root", "/d"])
        self.assertIn(ENV, str(caught.exception))


class TheSuccessfulPathStillWorks(unittest.TestCase):
    def test_completed_job_is_exit_zero_and_records_its_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            claim = Claim(tmp)
            calls = []

            def fake(argv, **kw):
                calls.append(argv[0])
                return run(0, "5551212\n") if argv[0] == "sbatch" else run(0, "COMPLETED\n")

            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                code = producer.launch(claim.args(), claim.dir, claim.ids)
            self.assertEqual(code, producer.EXIT_COMPLETE)
            self.assertEqual(json.loads(claim.ids.read_text()), ["5551212"])
            self.assertNotIn("scancel", calls)


class UncertainSubmissionRetainsTheReservation(unittest.TestCase):
    def test_nonzero_sbatch_writes_no_ids_and_cancels_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            claim = Claim(tmp)
            calls = []

            def fake(argv, **kw):
                calls.append(argv[0])
                return run(1, "", "boom")

            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                code = producer.launch(claim.args(), claim.dir, claim.ids)
            self.assertEqual(code, producer.EXIT_SUBMISSION_UNCERTAIN)
            self.assertFalse(claim.ids.exists())
            self.assertNotIn("scancel", calls)
            self.assertIn("NOT evidence",
                          (claim.dir / "submission-uncertain.txt").read_text())


class TheBudgetIsAbsoluteAndStartsBeforeSubmission(unittest.TestCase):
    """The finding: nothing bounded the launcher, so the controller's SIGKILL did."""

    def test_the_budget_starts_before_the_first_submission(self):
        with tempfile.TemporaryDirectory() as tmp:
            claim = Claim(tmp)
            clock = FakeClock()
            order = []

            def read():
                order.append("clock")
                return clock.now

            def fake(argv, **kw):
                order.append(argv[0])
                return run(0, "5551212\n") if argv[0] == "sbatch" else run(0, "COMPLETED\n")

            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                producer.launch(claim.args(), claim.dir, claim.ids, clock=read,
                                sleeper=clock.sleep)
            # A deadline fixed after submission cannot cover the submission.
            self.assertEqual(order[0], "clock")
            self.assertEqual(order[order.index("sbatch") - 1], "clock")

    def test_worst_case_walk_finishes_before_the_controller_kill(self):
        """The reviewer's 1799/1919 arithmetic, replayed: every call burns its whole grant."""
        with tempfile.TemporaryDirectory() as tmp:
            claim = Claim(tmp)
            clock = FakeClock()
            grants = []

            def fake(argv, **kw):
                grants.append((argv[0], kw["timeout"]))
                clock.advance(kw["timeout"])        # worst case: the full grant, every time
                if argv[0] == "sbatch":
                    return run(0, "5551212\n")
                return run(0, "PENDING\n")          # never terminal, so the wait runs out

            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                code = producer.launch(claim.args(), claim.dir, claim.ids,
                                       clock=clock.read, sleeper=clock.sleep)

            self.assertEqual(code, producer.EXIT_ERROR)
            self.assertEqual(grants[0][0], "sbatch")
            self.assertIn("scancel", [name for name, _ in grants])
            # Everything, cancellation and its verification included, inside our own wall ...
            self.assertLessEqual(clock.now, producer.LAUNCHER_BUDGET_SECONDS)
            # ... inside the producer timeout staging must declare ...
            self.assertLessEqual(clock.now + producer.CONTROLLER_START_SLACK_SECONDS,
                                 producer.STAGED_TIMEOUT_SECONDS)
            # ... and with the validator's share of the shared wall still unspent.
            self.assertLessEqual(
                producer.STAGED_TIMEOUT_SECONDS + producer.VALIDATOR_RESERVE_SECONDS,
                producer.CONTROLLER_WALL_SECONDS)

    def test_every_grant_is_within_what_was_left_at_the_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            claim = Claim(tmp)
            clock = FakeClock()
            grants = []

            def fake(argv, **kw):
                grants.append((clock.now, kw["timeout"]))
                clock.advance(kw["timeout"] / 2)
                if argv[0] == "sbatch":
                    return run(0, "5551212\n")
                return run(0, "PENDING\n")

            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                producer.launch(claim.args(), claim.dir, claim.ids, clock=clock.read,
                                sleeper=clock.sleep)
            for started, granted in grants:
                self.assertGreater(granted, 0)
                self.assertLessEqual(started + granted, producer.LAUNCHER_BUDGET_SECONDS)


class TheWaitNeverEatsTheCleanupReserve(unittest.TestCase):
    def test_the_last_nap_is_truncated_to_the_reserve_boundary(self):
        clock = FakeClock()
        budget = producer.Budget(clock=clock.read)
        clock.advance(producer.LAUNCHER_BUDGET_SECONDS
                      - producer.CLEANUP_RESERVE_SECONDS - 5)
        with mock.patch.object(producer.subprocess, "run", return_value=run(0, "PENDING\n")):
            state, detail = producer.wait_for_job("5551212", budget=budget,
                                                  sleeper=clock.sleep)
        self.assertIsNone(state)
        # A full 20s poll here would have spent five seconds of the cancellation reserve.
        self.assertEqual(clock.naps, [5.0])
        self.assertGreaterEqual(budget.remaining(), producer.CLEANUP_RESERVE_SECONDS - 1e-9)

    def test_cleanup_still_has_a_positive_grant_after_a_full_wait(self):
        clock = FakeClock()
        budget = producer.Budget(clock=clock.read)
        with mock.patch.object(producer.subprocess, "run", return_value=run(0, "PENDING\n")):
            producer.wait_for_job("5551212", budget=budget, sleeper=clock.sleep)
        self.assertGreater(budget.grant_for_cleanup(producer.SCANCEL_TIMEOUT_SECONDS), 0)


class AnExhaustedBudgetIsExplicitNotSilent(unittest.TestCase):
    def test_cleanup_past_the_deadline_starts_nothing_and_claims_nothing(self):
        clock = FakeClock()
        budget = producer.Budget(clock=clock.read)
        clock.advance(producer.LAUNCHER_BUDGET_SECONDS + 1)
        with mock.patch.object(producer.subprocess, "run") as runner:
            result = producer.cancel_this_job("5551212", budget=budget)
        runner.assert_not_called()
        self.assertFalse(result["cancel_requested"])
        self.assertIsNone(result["terminal_state"])
        self.assertEqual(result["cleanup"], "UNRESOLVED")
        self.assertIn("not started", result["verification"])

    def test_a_probe_that_could_not_start_is_unknown_not_terminal(self):
        clock = FakeClock()
        budget = producer.Budget(clock=clock.read)
        clock.advance(producer.LAUNCHER_BUDGET_SECONDS + 1)
        with mock.patch.object(producer.subprocess, "run") as runner:
            state, detail = producer.job_state("5551212", budget=budget)
        runner.assert_not_called()
        self.assertIsNone(state)
        self.assertIn("unknown", detail)

    def test_no_budget_at_submission_means_no_sbatch_and_no_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            claim = Claim(tmp)
            with mock.patch.object(producer.subprocess, "run") as runner:
                code = producer.launch(claim.args(), claim.dir, claim.ids,
                                       clock=clock_that_jumps_after_the_first_read())
            runner.assert_not_called()
            self.assertEqual(code, producer.EXIT_ERROR)
            self.assertFalse(claim.ids.exists())
            outcome = json.loads((claim.dir / "launch-outcome.json").read_text())
            self.assertEqual(outcome["submission"], "not attempted")
            self.assertEqual(outcome["reservation"], "RETAINED")


class TheStagedTimeoutIsPartOfTheDesign(unittest.TestCase):
    """campaignctl defaults --timeout-seconds to 600; staging must override it."""

    def test_the_stage_default_would_kill_this_launcher(self):
        self.assertGreater(producer.STAGED_TIMEOUT_SECONDS, 600.0)

    def test_the_planned_item_timeout_leaves_the_validator_its_share(self):
        self.assertLessEqual(producer.STAGED_TIMEOUT_SECONDS,
                             producer.CONTROLLER_WALL_SECONDS)
        self.assertLessEqual(
            producer.STAGED_TIMEOUT_SECONDS + producer.VALIDATOR_RESERVE_SECONDS,
            producer.CONTROLLER_WALL_SECONDS)

    def test_a_walltime_longer_than_the_wait_window_is_refused(self):
        with self.assertRaises(SystemExit) as caught:
            producer.verify_budget_arithmetic(25)
        self.assertIn("would be cancelled rather than read", str(caught.exception))
        self.assertIn("authorization question", str(caught.exception))

    def test_the_default_walltime_fits_the_wait_window(self):
        plan = producer.verify_budget_arithmetic(producer.DEFAULT_MINUTES)
        self.assertLessEqual(plan["job_walltime_seconds"], plan["wait_window_seconds"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
