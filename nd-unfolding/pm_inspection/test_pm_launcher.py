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


class Claim:
    """A queue-shaped claim directory outside any checkout."""

    def __init__(self, tmp):
        self.dir = Path(tmp) / "runs" / "pm-root-inspection-20260908"
        self.dir.mkdir(parents=True)
        self.ids = self.dir / "task-ids.json"

    def args(self, **over):
        base = dict(mode="launch", inner_python="/conda/bin/python",
                    expect_root=Path("/exec"), account="m3246", qos="debug",
                    minutes=25, comment="tok", bindings=Path("/bound dir/inputs.json"),
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

            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                with mock.patch.object(producer.time, "time",
                                       side_effect=[0, 10 ** 9, 10 ** 9]):
                    code = producer.launch(claim.args(), claim.dir, claim.ids)
            self.assertEqual(code, producer.EXIT_ERROR)
            # The finding: a bare IsADirectoryError used to escape here, losing the id.
            recorded = json.loads((claim.dir / "task-ids-write-failed.txt").read_text())
            self.assertEqual(recorded["job_id"], "5551212")
            self.assertEqual(calls.count("scancel"), 1)


class UnknownStateNeverReadsAsTerminal(unittest.TestCase):
    def test_sacct_rc1_with_completed_stdout_is_not_terminal(self):
        with mock.patch.object(producer.subprocess, "run",
                               return_value=run(1, "COMPLETED\n")):
            state, detail = producer.job_state("5551212")
        self.assertIsNone(state)
        self.assertIn("exited 1", detail)

    def test_sacct_timeout_is_not_terminal(self):
        with mock.patch.object(producer.subprocess, "run",
                               side_effect=subprocess.TimeoutExpired("sacct", 60)):
            state, _ = producer.job_state("5551212")
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

            with mock.patch.object(producer.subprocess, "run", side_effect=fake):
                with mock.patch.object(producer.time, "time",
                                       side_effect=[0, 10 ** 9, 10 ** 9]):
                    code = producer.launch(claim.args(), claim.dir, claim.ids)
            self.assertEqual(code, producer.EXIT_ERROR)
            self.assertEqual(calls.count("scancel"), 1)


class CancelRequestIsNotProofOfTermination(unittest.TestCase):
    def test_scancel_rc1_is_unresolved_not_cancelled(self):
        def fake(argv, **kw):
            return run(1, "", "denied") if argv[0] == "scancel" else run(0, "RUNNING\n")

        with mock.patch.object(producer.subprocess, "run", side_effect=fake):
            result = producer.cancel_this_job("5551212")
        self.assertEqual(result["scancel_returncode"], 1)
        self.assertEqual(result["cleanup"], "UNRESOLVED")
        self.assertIsNone(result["terminal_state"])

    def test_verified_terminal_is_reported_as_such(self):
        def fake(argv, **kw):
            return run(0) if argv[0] == "scancel" else run(0, "CANCELLED\n")

        with mock.patch.object(producer.subprocess, "run", side_effect=fake):
            result = producer.cancel_this_job("5551212")
        self.assertEqual(result["cleanup"], "verified-terminal")

    def test_cancel_names_only_the_id(self):
        with mock.patch.object(producer.subprocess, "run", return_value=run(0)) as r:
            producer.cancel_this_job("5551212")
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
