import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

import agentctl


class AgentCtlTests(unittest.TestCase):
    def test_parse_codex_thread_and_last_message(self):
        stream = "\n".join(
            [
                json.dumps({"type": "thread.started", "thread_id": "thread-1"}),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": "first"},
                    }
                ),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": "last"},
                    }
                ),
            ]
        )
        self.assertEqual(agentctl.parse_codex(stream), ("thread-1", "last"))

    def test_parse_claude(self):
        payload = json.dumps({"session_id": "session-1", "result": "done"})
        self.assertEqual(agentctl.parse_claude(payload), ("session-1", "done"))

    def test_parse_agy_conversation(self):
        log = (
            "Created conversation 01964ce7-5ee0-44f9-aa9e-21dd1d73614b\n"
            "Print mode: conversation=01964ce7-5ee0-44f9-aa9e-21dd1d73614b"
        )
        self.assertEqual(
            agentctl.parse_agy(log, "READY.\n"),
            ("01964ce7-5ee0-44f9-aa9e-21dd1d73614b", "READY."),
        )

    def test_usage_limit_markers_are_case_insensitive(self):
        self.assertTrue(
            agentctl.reports_usage_limit(
                "You've hit your usage limit. Try again at 8:44 AM."
            )
        )
        self.assertFalse(agentctl.reports_usage_limit("ordinary worker failure"))

    def test_claude_success_exit_with_limit_payload_is_capacity_error(self):
        payload = json.dumps(
            {
                "is_error": True,
                "session_id": "session-1",
                "result": "You've hit your usage limit. Try again at 8:44 AM.",
            }
        )
        completed = types.SimpleNamespace(returncode=0, stdout=payload, stderr="")
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            agentctl.subprocess, "run", return_value=completed
        ):
            with self.assertRaises(agentctl.ProviderCapacityError):
                agentctl.run_worker(
                    ["claude"],
                    {},
                    Path(temporary),
                    Path(temporary) / "run",
                    "claude",
                )

    def test_claude_allowed_tools_cannot_consume_prompt(self):
        profile = {
            "provider": "claude",
            "home": "~/claude-homes/school",
            "config_env": "HOME",
            "dangerously_skip_permissions": True,
            "model": "opus",
            "allowed_tools": ["Read", "WebSearch"],
        }
        command, env = agentctl.build_start_command(
            profile, "the prompt", Path.cwd(), "session-1"
        )
        self.assertIn("--allowedTools=Read,WebSearch", command)
        self.assertIn("--dangerously-skip-permissions", command)
        self.assertEqual(command[-1], "the prompt")
        self.assertEqual(
            env["HOME"], str(agentctl.login_home() / "claude-homes" / "school")
        )

    def test_tilde_uses_login_home_when_home_is_overridden(self):
        original = os.environ.get("HOME")
        try:
            os.environ["HOME"] = "/tmp/fake-claude-home"
            self.assertEqual(
                agentctl.expand_path("~/codex-homes/personal"),
                str(agentctl.login_home() / "codex-homes" / "personal"),
            )
        finally:
            if original is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = original

    def test_agy_commands_pin_home_to_login_home(self):
        profile = {"provider": "agy", "model": "Gemini 3.1 Pro (High)"}
        original = os.environ.get("HOME")
        try:
            os.environ["HOME"] = "/tmp/fake-claude-home"
            start_command, start_env = agentctl.build_start_command(
                profile, "hi", Path("/tmp/cwd"), "sess", provider_log=Path("/tmp/p.log")
            )
            resume_command, resume_env = agentctl.build_resume_command(
                profile, "hi", "sess", cwd=Path("/tmp/cwd"), provider_log=Path("/tmp/p.log")
            )
            login = str(agentctl.login_home())
            self.assertEqual(start_env["HOME"], login)
            self.assertEqual(resume_env["HOME"], login)
            for command in (start_command, resume_command):
                self.assertTrue(command[0].startswith(login))
        finally:
            if original is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = original

    def test_account_home_symlink_is_not_dereferenced(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            physical = root / "physical-home"
            logical = root / "logical-home"
            physical.mkdir()
            logical.symlink_to(physical, target_is_directory=True)
            with mock.patch.object(agentctl, "login_home", return_value=logical):
                self.assertEqual(
                    agentctl.expand_path("~/claude-homes/school"),
                    str(logical / "claude-homes" / "school"),
                )

    def test_codex_yolo_uses_supported_long_flag_without_sandbox_conflict(self):
        profile = {
            "provider": "codex",
            "home": "~/codex-homes/personal",
            "model": "gpt-5.6-sol",
            "sandbox": "read-only",
            "yolo": True,
        }
        command, _env = agentctl.build_start_command(
            profile, "the prompt", Path.cwd(), "unused"
        )
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", command)
        self.assertNotIn("--sandbox", command)


class AutoCodexProfileTests(unittest.TestCase):
    def setUp(self):
        self.profiles = {
            "codex-personal": {"provider": "codex", "home": "~/codex-homes/personal"},
            "codex-school2": {"provider": "codex", "home": "~/codex-homes/school2"},
            "agy": {"provider": "agy", "executable": "~/.local/bin/agy"},
        }

    @staticmethod
    def runner(returncode=0, payload=None):
        payload = payload or {"selected": "codex-school2"}

        def run(argv, **kwargs):
            return types.SimpleNamespace(
                returncode=returncode,
                stdout=json.dumps(payload),
            )

        return run

    def test_auto_codex_records_concrete_selected_profile(self):
        selected, request = agentctl.resolve_start_profile(
            "auto-codex",
            self.profiles,
            Path("profiles.json"),
            runner=self.runner(),
        )
        self.assertEqual(selected, "codex-school2")
        self.assertEqual(request, "auto-codex")

    def test_existing_session_profile_is_not_reselected(self):
        selected, request = agentctl.resolve_start_profile(
            "codex-personal",
            self.profiles,
            Path("profiles.json"),
            runner=lambda *args, **kwargs: self.fail("selector must not run"),
        )
        self.assertEqual(selected, "codex-personal")
        self.assertIsNone(request)

    def test_auto_codex_fails_closed_without_capacity(self):
        with self.assertRaisesRegex(agentctl.AgentCtlError, "could not select"):
            agentctl.resolve_start_profile(
                "auto-codex",
                self.profiles,
                Path("profiles.json"),
                runner=self.runner(returncode=3, payload={"selected": None}),
            )

    def test_auto_codex_rejects_non_codex_selection(self):
        with self.assertRaisesRegex(agentctl.AgentCtlError, "non-Codex"):
            agentctl.resolve_start_profile(
                "auto-codex",
                self.profiles,
                Path("profiles.json"),
                runner=self.runner(payload={"selected": "agy"}),
            )


class CapacityResumeTests(unittest.TestCase):
    profile_name = "claude-school"
    session_id = "session-school-1"
    role = "school-main"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agentctl-capacity.")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cwd = self.root / "worktree"
        self.cwd.mkdir()
        self.registry = self.root / "sessions.json"
        agentctl.atomic_write_json(
            self.registry,
            {
                "version": 1,
                "sessions": {
                    self.role: {
                        "provider": "claude",
                        "profile": self.profile_name,
                        "session_id": self.session_id,
                        "cwd": str(self.cwd),
                        "turns": [],
                    }
                },
            },
        )
        self.profiles = {
            self.profile_name: {
                "provider": "claude",
                "home": "~/claude-homes/school",
                "model": "opus",
            }
        }

    def args(self, **overrides):
        values = {
            "role": self.role,
            "prompt": ["finish", "the", "task"],
            "prompt_file": None,
            "expected_session_id": None,
            "defer_on_exhaustion": True,
            "waker_config": str(self.root / "waker-config.json"),
            "waker_state_dir": str(self.root / "waker-state"),
        }
        values.update(overrides)
        return types.SimpleNamespace(**values)

    def test_capacity_check_accepts_exhausted_exit_code(self):
        runner = mock.Mock(
            return_value=types.SimpleNamespace(
                returncode=3,
                stdout=json.dumps(
                    {
                        "profile": self.profile_name,
                        "state": "EXHAUSTED",
                        "next_reset_utc": "2026-08-28T08:44:00+00:00",
                    }
                ),
            )
        )
        result = agentctl.check_profile_capacity(
            self.profile_name, self.root / "profiles.json", runner=runner
        )
        self.assertEqual(result["state"], "EXHAUSTED")

    def test_claude_deferral_requires_measured_reset_time(self):
        with self.assertRaisesRegex(agentctl.AgentCtlError, "measured reset time"):
            agentctl.queue_deferred_send(
                self.args(),
                role=self.role,
                prompt="continue",
                registry_path=self.registry,
                session_id=self.session_id,
                provider="claude",
                capacity={"state": "EXHAUSTED"},
            )

    def test_deferred_send_passes_reset_and_exact_registry_to_waker(self):
        calls = []

        def runner(argv, **kwargs):
            calls.append((argv, kwargs))
            return types.SimpleNamespace(returncode=0, stdout="{}")

        reset_utc = "2026-08-28T08:44:00+00:00"
        agentctl.defer_role_send(
            role=self.role,
            prompt="continue",
            registry_path=self.registry,
            session_id=self.session_id,
            waker_config_path=self.root / "waker-config.json",
            waker_state_dir=self.root / "waker-state",
            not_before_utc=reset_utc,
            runner=runner,
        )
        argv, kwargs = calls[0]
        self.assertIn(str(self.registry.resolve()), argv)
        self.assertIn(self.session_id, argv)
        self.assertIn(reset_utc, argv)
        self.assertEqual(kwargs["input"], "continue")

    def test_expected_session_mismatch_fails_before_capacity_probe(self):
        with mock.patch.object(agentctl, "check_profile_capacity") as capacity:
            with self.assertRaisesRegex(agentctl.AgentCtlError, "different session"):
                agentctl.send(
                    self.args(expected_session_id="replacement-session"),
                    self.profiles,
                    self.registry,
                )
        capacity.assert_not_called()

    def test_preflight_exhaustion_defers_original_prompt_without_provider_call(self):
        exhausted = {
            "profile": self.profile_name,
            "state": "EXHAUSTED",
            "next_reset_utc": "2026-08-28T08:44:00+00:00",
        }
        with mock.patch.object(
            agentctl, "check_profile_capacity", return_value=exhausted
        ), mock.patch.object(
            agentctl, "queue_deferred_send", return_value="quota-school-main-1"
        ) as queue, mock.patch.object(agentctl, "run_worker") as worker:
            agentctl.send(self.args(), self.profiles, self.registry)
        worker.assert_not_called()
        self.assertEqual(queue.call_args.kwargs["prompt"], "finish the task")
        self.assertEqual(queue.call_args.kwargs["session_id"], self.session_id)
        self.assertIs(queue.call_args.kwargs["capacity"], exhausted)

    def test_provider_limit_defers_one_continue_prompt(self):
        capacities = iter(
            [
                {"profile": self.profile_name, "state": "READY"},
                {
                    "profile": self.profile_name,
                    "state": "EXHAUSTED",
                    "next_reset_utc": "2026-08-28T08:44:00+00:00",
                },
            ]
        )
        with mock.patch.object(
            agentctl, "check_profile_capacity", side_effect=lambda *_: next(capacities)
        ), mock.patch.object(
            agentctl,
            "run_worker",
            side_effect=agentctl.ProviderCapacityError("usage limit"),
        ), mock.patch.object(
            agentctl, "queue_deferred_send", return_value="quota-school-main-2"
        ) as queue:
            agentctl.send(self.args(), self.profiles, self.registry)
        self.assertEqual(
            queue.call_args.kwargs["prompt"],
            agentctl.CONTINUE_AFTER_LIMIT_PROMPT,
        )
        self.assertEqual(queue.call_args.kwargs["capacity"]["state"], "EXHAUSTED")
        self.assertEqual(queue.call_count, 1)


class WorktreeIsolationTests(unittest.TestCase):
    def test_external_registry_keeps_run_receipts_out_of_control_checkout(self):
        with tempfile.TemporaryDirectory() as temporary:
            registry = Path(temporary) / "runtime" / "sessions.json"
            base = agentctl.run_base("root", "start", registry)
        self.assertEqual(
            base.parent.parent, registry.resolve().parent / "agent-runs"
        )

    def test_new_role_rejects_registered_shared_cwd(self):
        with tempfile.TemporaryDirectory() as temporary:
            cwd = Path(temporary).resolve()
            registry = {
                "sessions": {"existing": {"cwd": str(cwd)}}
            }
            with self.assertRaisesRegex(agentctl.AgentCtlError, "isolated git worktree"):
                agentctl.assert_new_role_cwd_isolated(registry, "new", cwd)

    def test_new_role_accepts_unique_cwd(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            registry = {"sessions": {"existing": {"cwd": str(Path(first).resolve())}}}
            agentctl.assert_new_role_cwd_isolated(registry, "new", Path(second))

    def test_dirty_git_start_fails_closed(self):
        replies = iter(
            [
                types.SimpleNamespace(returncode=0, stdout="true\n"),
                types.SimpleNamespace(returncode=0, stdout="?? unowned.txt\n"),
            ]
        )

        def runner(argv, **kwargs):
            return next(replies)

        with self.assertRaisesRegex(agentctl.AgentCtlError, "dirty worktree"):
            agentctl.assert_clean_git_start(Path("/repo"), runner=runner)

    def test_non_git_scratch_directory_is_allowed(self):
        def runner(argv, **kwargs):
            return types.SimpleNamespace(returncode=128, stdout="not a git repository")

        agentctl.assert_clean_git_start(Path("/scratch"), runner=runner)


if __name__ == "__main__":
    unittest.main()
