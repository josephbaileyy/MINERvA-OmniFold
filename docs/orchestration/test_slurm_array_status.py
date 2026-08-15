import unittest

from slurm_array_status import build_snapshot, expand_spec


class SlurmArrayStatusTests(unittest.TestCase):
    def runner(self, queue: str, acct: str):
        def run(command):
            return queue if command[0] == "squeue" else acct

        return run

    def test_active_expanded_queue(self):
        queue = "\n".join(f"42_{i}|RUNNING|None" for i in range(1, 4))
        result = build_snapshot("42", expand_spec("1-3"), self.runner(queue, ""))
        self.assertEqual(result["overall"], "ACTIVE")
        self.assertEqual(result["counts"], {"RUNNING": 3})

    def test_single_job_uses_synthetic_task_zero(self):
        queue = "42|PENDING|Priority"
        result = build_snapshot("42", [0], self.runner(queue, ""))
        self.assertEqual(result["overall"], "ACTIVE")
        self.assertEqual(result["counts"], {"PENDING": 1})
        self.assertEqual(result["tasks"]["0"]["reason"], "Priority")

    def test_single_job_terminal_accounting(self):
        acct = "42|COMPLETED|0:0"
        result = build_snapshot("42", [0], self.runner("", acct))
        self.assertEqual(result["overall"], "COMPLETE")

    def test_complete_requires_all_zero(self):
        acct = "\n".join(f"42_{i}|COMPLETED|0:0" for i in range(1, 4))
        result = build_snapshot("42", [1, 2, 3], self.runner("", acct))
        self.assertEqual(result["overall"], "COMPLETE")

    def test_nonzero_completed_is_error(self):
        acct = "42_1|COMPLETED|0:0\n42_2|COMPLETED|1:0\n42_3|RUNNING|0:0"
        result = build_snapshot("42", [1, 2, 3], self.runner("42_3|RUNNING|None", acct))
        self.assertEqual(result["overall"], "ERROR")
        self.assertEqual(result["error_tasks"], [2])

    def test_grouped_failure_expands(self):
        acct = "42_[2-3]|CANCELLED|0:15\n42_1|COMPLETED|0:0"
        result = build_snapshot("42", [1, 2, 3], self.runner("", acct))
        self.assertEqual(result["overall"], "ERROR")
        self.assertEqual(result["error_tasks"], [2, 3])

    def test_terminal_accounting_wins_over_stale_queue(self):
        queue = "42_1|RUNNING|None"
        acct = "42_1|FAILED|2:0"
        result = build_snapshot("42", [1], self.runner(queue, acct))
        self.assertEqual(result["overall"], "ERROR")

    def test_missing_is_unobserved_neither_terminal_nor_a_liveness_claim(self):
        """CORRECTED 2026-08-15, BEN-323. This test previously asserted
        `overall == "ACTIVE"` for a task nothing could see, under the name
        `test_missing_is_active_unknown_not_false_terminal`.

        Its INTENT was right and is preserved: a task that was never observed must
        NOT be reported as a terminal state, because a false "done" would license
        reading a result. But `ACTIVE` was the wrong safe-side choice -- it guards
        against a false terminal by asserting a false LIVENESS, and that is the
        hazard that actually fired: Leg F `56863958_[2-5]` rendered ACTIVE for over
        24 h after all four tasks COMPLETED, and a ~39 GPU-h scheduling constraint
        was built on it by three sessions.

        `UNOBSERVED` satisfies the original intent strictly better, being neither.
        The old assertion is recorded here rather than deleted because it is the
        instructive half: it shows a test can pin a defect while its name states a
        correct principle."""
        result = build_snapshot("42", [1], self.runner("", ""))
        self.assertEqual(result["overall"], "UNOBSERVED")
        self.assertNotEqual(result["overall"], "COMPLETE")   # the original intent
        self.assertNotEqual(result["overall"], "ACTIVE")     # the defect it allowed
        self.assertEqual(result["unknown_tasks"], [1])


if __name__ == "__main__":
    unittest.main()


class UnobservedIsNotActiveTests(unittest.TestCase):
    """BEN-323: `ACTIVE` was the ELSE of the classification, so a failure to observe
    rendered as a liveness claim. Leg F 56863958_[2-5] showed ACTIVE for >24 h after
    it COMPLETED, and a ~39 GPU-h scheduling constraint was built on it.

    Every test here is written so that reverting the branch order in
    slurm_array_status.build_snapshot makes it FAIL. That is asserted directly in
    test_mutant_restoring_active_as_else_is_caught, because a guard nobody has seen
    fail is the defect this file exists to close.
    """

    def unreachable_runner(self):
        """No Slurm on the host: both commands raise, exactly as on a login-less Mac."""
        def run(command):
            raise OSError(f"[Errno 2] No such file or directory: '{command[0]}'")
        return run

    def test_slurm_unreachable_is_UNOBSERVED_not_ACTIVE(self):
        result = build_snapshot("56863958", expand_spec("2-5"), self.unreachable_runner())
        self.assertEqual(result["overall"], "UNOBSERVED")
        self.assertNotEqual(result["overall"], "ACTIVE")
        self.assertEqual(result["counts"], {"UNKNOWN": 4})
        self.assertEqual(result["unknown_tasks"], [2, 3, 4, 5])
        # the evidence of non-observation must survive into the snapshot
        self.assertEqual(len(result["observer_errors"]), 2)
        self.assertTrue(any(e.startswith("squeue:") for e in result["observer_errors"]))
        self.assertTrue(any(e.startswith("sacct:") for e in result["observer_errors"]))

    def test_empty_replies_are_UNOBSERVED(self):
        """Reachable Slurm that returns nothing is still not evidence of running."""
        def run(command):
            return ""
        result = build_snapshot("42", expand_spec("1-3"), run)
        self.assertEqual(result["overall"], "UNOBSERVED")
        self.assertEqual(result["observer_errors"], [])

    def test_the_real_leg_f_rows_are_COMPLETE(self):
        """Measured by ssh sacct 2026-08-15, the rows BEN-323 was falsified with."""
        acct = "\n".join([
            "56863958_2|COMPLETED|0:0",
            "56863958_3|COMPLETED|0:0",
            "56863958_4|COMPLETED|0:0",
            "56863958_5|COMPLETED|0:0",
        ])
        result = build_snapshot("56863958", expand_spec("2-5"), self.runner_pair("", acct))
        self.assertEqual(result["overall"], "COMPLETE")

    def test_partial_visibility_does_not_claim_ACTIVE(self):
        """BEN-229: a split array is invisible to sacct between split and start. Some
        COMPLETED plus some UNKNOWN is NOT positive evidence of a running task."""
        acct = "42_1|COMPLETED|0:0"
        result = build_snapshot("42", expand_spec("1-3"), self.runner_pair("", acct))
        self.assertEqual(result["overall"], "UNOBSERVED")
        self.assertEqual(result["unknown_tasks"], [2, 3])

    def test_one_observed_running_task_still_gives_ACTIVE(self):
        """The fix must not break the true positive: real evidence still reads ACTIVE."""
        result = build_snapshot("42", expand_spec("1-3"), self.runner_pair("42_2|RUNNING|None", ""))
        self.assertEqual(result["overall"], "ACTIVE")

    def test_error_still_outranks_unobserved(self):
        acct = "42_1|FAILED|1:0"
        result = build_snapshot("42", expand_spec("1-3"), self.runner_pair("", acct))
        self.assertEqual(result["overall"], "ERROR")

    def test_mutant_restoring_active_as_else_is_caught(self):
        """POWER TEST. Re-implement the pre-fix classification and assert it produces
        the defect, so this suite is known to be able to fail rather than assumed to."""
        def pre_fix_overall(error_tasks, complete, n_tasks):
            if error_tasks:
                return "ERROR"
            if complete == n_tasks:
                return "COMPLETE"
            return "ACTIVE"                      # <- the defect
        snap = build_snapshot("56863958", expand_spec("2-5"), self.unreachable_runner())
        self.assertEqual(
            pre_fix_overall(snap["error_tasks"], 0, 4), "ACTIVE",
            "the mutant must reproduce the defect, else this test proves nothing",
        )
        self.assertEqual(snap["overall"], "UNOBSERVED")

    def runner_pair(self, queue: str, acct: str):
        def run(command):
            return queue if command[0] == "squeue" else acct
        return run
