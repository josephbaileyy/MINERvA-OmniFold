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

    def test_missing_is_active_unknown_not_false_terminal(self):
        result = build_snapshot("42", [1], self.runner("", ""))
        self.assertEqual(result["overall"], "ACTIVE")
        self.assertEqual(result["unknown_tasks"], [1])


if __name__ == "__main__":
    unittest.main()
