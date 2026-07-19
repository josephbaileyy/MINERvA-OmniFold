import unittest

from generate_live_state import MAX_LINES, render


class LiveStateTests(unittest.TestCase):
    def fixtures(self):
        config = {
            "campaign": "test",
            "current_dag_node": "node",
            "state": "ACTIVE",
            "orchestrator_thread_id": "thread",
            "owners": [{"role": "worker", "uuid": "uuid-1", "purpose": "test"}],
            "blockers": ["blocked"],
            "next_authorized_action": "next",
            "wake": {"tmux_session": "wake"},
            "canonical_science": ["VALIDATION_LEDGER.md"],
            "append_only_history": ["docs/orchestration/RUNS.tsv"],
            "archival_index_only": ["superseded followup prompts"],
        }
        sessions = {"sessions": {"worker": {"session_id": "uuid-1", "provider": "agy", "profile": "agy"}}}
        usage = {
            "gate_ok": False,
            "profiles": {
                "codex-personal": {"windows": {"seven_day": {"remaining_percent": 5, "resets_at_utc": "later"}}, "reset_credits": {"valid_available_full_reset_count": 0, "protected_reserve": 1}},
                "codex-school": {"windows": {}, "reset_credits": {}},
                "agy": {"status": "unknown"},
            },
            "accounts": {"claude-school": {"status": "unknown"}},
            "warnings": ["credit constrained"],
        }
        jobs = [{"job_id": "42", "tasks": "1-2", "receipt": {"cpus_per_task": 4, "memory_per_task": "1G", "time_limit": "1:00", "qos": "shared"}, "snapshot": {"overall": "ACTIVE", "counts": {"RUNNING": 2}, "error_tasks": []}}]
        return config, sessions, usage, jobs

    def test_dashboard_is_bounded_and_missing_credit_is_rendered_not_fatal(self):
        config, sessions, usage, jobs = self.fixtures()
        text = render(config, sessions, usage, 3, jobs, {"head": "abc", "dirty_count": 1}, {"tmux": "ACTIVE", "event": "absent", "invoked": "absent", "completed": "absent"}, "now")
        self.assertLessEqual(len(text.splitlines()), MAX_LINES)
        self.assertIn("0 available/1 protected", text)
        self.assertIn("BLOCKED/UNKNOWN", text)

    def test_uuid_mismatch_fails(self):
        config, sessions, usage, jobs = self.fixtures()
        sessions["sessions"]["worker"]["session_id"] = "replacement"
        with self.assertRaisesRegex(RuntimeError, "UUID mismatch"):
            render(config, sessions, usage, 0, jobs, {"head": "abc", "dirty_count": 0}, {"tmux": "INACTIVE", "event": "absent", "invoked": "absent", "completed": "absent"}, "now")


if __name__ == "__main__":
    unittest.main()
