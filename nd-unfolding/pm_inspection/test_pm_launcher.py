#!/usr/bin/env python3
"""Tests for the launch-mode primitives. No scheduler is contacted."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pm_root_inspect as producer  # noqa: E402


def fake_run(returncode=0, stdout="", stderr=""):
    return mock.Mock(returncode=returncode, stdout=stdout, stderr=stderr)


class IdentityIsRecordedBeforeAnythingCanSpend(unittest.TestCase):
    def test_job_id_is_written_at_submission(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids = Path(tmp) / "task-ids.json"
            with mock.patch.object(producer.subprocess, "run",
                                   return_value=fake_run(0, "5551212\n")):
                job = producer.submit_one_job(
                    "true", run_dir=Path(tmp), task_ids_path=ids,
                    account="m3246", qos="debug", minutes=25, comment="digest")
            self.assertEqual(job, "5551212")
            self.assertEqual(json.loads(ids.read_text()), ["5551212"])

    def test_parsable_cluster_suffix_is_stripped(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids = Path(tmp) / "task-ids.json"
            with mock.patch.object(producer.subprocess, "run",
                                   return_value=fake_run(0, "5551212;perlmutter\n")):
                self.assertEqual(producer.submit_one_job(
                    "true", run_dir=Path(tmp), task_ids_path=ids, account="m3246",
                    qos="debug", minutes=25, comment="d"), "5551212")

    def test_submission_uses_exactly_one_node_one_task_no_requeue(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(producer.subprocess, "run",
                                   return_value=fake_run(0, "1\n")) as run:
                producer.submit_one_job("true", run_dir=Path(tmp),
                                        task_ids_path=Path(tmp) / "i.json",
                                        account="m3246", qos="debug", minutes=25,
                                        comment="d")
            argv = run.call_args[0][0]
            for flag, value in (("--nodes", "1"), ("--ntasks", "1"),
                                ("--constraint", "cpu"), ("--time", "25")):
                self.assertEqual(argv[argv.index(flag) + 1], value)
            self.assertIn("--no-requeue", argv)
            self.assertIn("--export=ALL", argv)
            self.assertNotIn("--gres", argv)
            self.assertFalse([a for a in argv if a.startswith("--gpus")])


class UncertainSubmissionRetainsTheReservation(unittest.TestCase):
    def test_nonzero_sbatch_is_uncertain_not_proof_of_no_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(producer.subprocess, "run",
                                   return_value=fake_run(1, "", "boom")):
                with self.assertRaises(producer.SubmissionUncertain) as caught:
                    producer.submit_one_job("true", run_dir=Path(tmp),
                                            task_ids_path=Path(tmp) / "i.json",
                                            account="m3246", qos="debug", minutes=25,
                                            comment="tok")
            message = str(caught.exception)
            self.assertIn("NOT evidence that no job was created", message)
            self.assertIn("tok", message)
            self.assertFalse((Path(tmp) / "i.json").exists())

    def test_sbatch_that_cannot_run_is_uncertain(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(producer.subprocess, "run",
                                   side_effect=OSError("no sbatch")):
                with self.assertRaises(producer.SubmissionUncertain):
                    producer.submit_one_job("true", run_dir=Path(tmp),
                                            task_ids_path=Path(tmp) / "i.json",
                                            account="m3246", qos="debug", minutes=25,
                                            comment="d")

    def test_unparseable_job_id_is_uncertain_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids = Path(tmp) / "i.json"
            with mock.patch.object(producer.subprocess, "run",
                                   return_value=fake_run(0, "Submitted batch job 42\n")):
                with self.assertRaises(producer.SubmissionUncertain):
                    producer.submit_one_job("true", run_dir=Path(tmp),
                                            task_ids_path=ids, account="m3246",
                                            qos="debug", minutes=25, comment="d")
            self.assertFalse(ids.exists())


class CancellationIsScopedToThisJob(unittest.TestCase):
    def test_scancel_names_only_the_id(self):
        with mock.patch.object(producer.subprocess, "run",
                               return_value=fake_run(0)) as run:
            producer.cancel_this_job("5551212")
        argv = run.call_args[0][0]
        self.assertEqual(argv, ["scancel", "5551212"])
        self.assertNotIn("--user", argv)
        self.assertNotIn("--name", argv)


class WaitingIsBounded(unittest.TestCase):
    def test_terminal_state_returns_it(self):
        with mock.patch.object(producer.subprocess, "run",
                               return_value=fake_run(0, "COMPLETED\n")):
            self.assertEqual(
                producer.wait_for_job("1", deadline=producer.time.time() + 60), "COMPLETED")

    def test_deadline_already_passed_returns_none_without_polling(self):
        with mock.patch.object(producer.subprocess, "run") as run:
            self.assertIsNone(producer.wait_for_job("1", deadline=0))
        run.assert_not_called()

    def test_running_job_is_not_terminal(self):
        with mock.patch.object(producer.subprocess, "run",
                               return_value=fake_run(0, "RUNNING\n")):
            self.assertIsNone(
                producer.wait_for_job("1", deadline=producer.time.time() + 0.2,
                                      poll_seconds=0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
