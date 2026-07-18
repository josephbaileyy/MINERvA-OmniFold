import json
import os
from pathlib import Path
import tempfile
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


if __name__ == "__main__":
    unittest.main()
