import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import agent_session_notify
import install_agent_notifications


class AgentSessionNotifyTests(unittest.TestCase):
    def test_codex_turn_is_actionable_and_includes_session(self):
        envelope = {
            "spool_id": "one",
            "provider": "codex",
            "account": "school2",
            "tmux_session": "minerva-codex-school-pet",
            "host": "login21",
            "cwd": "/repo",
            "payload": {
                "type": "agent-turn-complete",
                "thread-id": "thread",
                "turn-id": "turn",
                "last-assistant-message": "I need a decision.",
            },
        }
        key, subject, body = agent_session_notify.build_message(envelope)
        self.assertTrue(key.startswith("agent-session:"))
        self.assertEqual(subject, "[MINERvA agent] minerva-codex-school-pet: needs input")
        self.assertIn("I need a decision.", body)
        self.assertIn("tmux attach -t minerva-codex-school-pet", body)

    def test_claude_permission_is_distinct_from_stop(self):
        envelope = {
            "spool_id": "two",
            "provider": "claude",
            "account": "school",
            "tmux_session": "minerva-claude-school-main",
            "host": "login21",
            "cwd": "/repo",
            "payload": {
                "hook_event_name": "Notification",
                "notification_type": "permission_prompt",
                "message": "Approve Bash?",
            },
        }
        _, subject, body = agent_session_notify.build_message(envelope)
        self.assertIn("needs permission", subject)
        self.assertIn("Approve Bash?", body)

    def test_hook_failure_is_nonblocking(self):
        with mock.patch.object(agent_session_notify, "enqueue", side_effect=OSError("disk full")):
            with mock.patch("sys.argv", ["agent_session_notify.py", "claude"]):
                with mock.patch("sys.stdin.read", return_value=json.dumps({"hook_event_name": "Stop"})):
                    self.assertEqual(agent_session_notify.main(), 0)

    def test_short_attention_window_suppresses_duplicate_subject(self):
        envelope = {
            "provider": "claude",
            "account": "school",
            "tmux_session": "minerva-claude-school-main",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subject = "[MINERvA agent] minerva-claude-school-main: needs input"
            self.assertTrue(agent_session_notify.claim_attention_window(root, envelope, subject))
            self.assertFalse(agent_session_notify.claim_attention_window(root, envelope, subject))
            other = "[MINERvA agent] minerva-claude-school-main: needs permission"
            self.assertTrue(agent_session_notify.claim_attention_window(root, envelope, other))


class InstallAgentNotificationsTests(unittest.TestCase):
    def test_installer_preserves_existing_settings_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.py"
            source.write_text("#!/usr/bin/python3\n")
            for account in install_agent_notifications.CODEX_ACCOUNTS:
                path = root / "codex-homes" / account / "config.toml"
                path.parent.mkdir(parents=True)
                path.write_text('model = "gpt"\n[features]\nfoo = true\n')
            for account in install_agent_notifications.CLAUDE_ACCOUNTS:
                path = root / "claude-homes" / account / ".claude" / "settings.json"
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps({"permissions": {"allow": ["Read"]}}))

            first = install_agent_notifications.install(source, root)
            second = install_agent_notifications.install(source, root)
            self.assertTrue(any("updated" in line for line in first))
            self.assertTrue(all("updated" not in line for line in second))

            codex = (root / "codex-homes" / "school2" / "config.toml").read_text()
            self.assertEqual(codex.count("notify ="), 1)
            self.assertLess(codex.index("notify ="), codex.index("[features]"))

            claude_path = root / "claude-homes" / "school" / ".claude" / "settings.json"
            claude = json.loads(claude_path.read_text())
            self.assertEqual(claude["permissions"], {"allow": ["Read"]})
            self.assertEqual(len(claude["hooks"]["Stop"]), 1)
            self.assertEqual(len(claude["hooks"]["Notification"]), 2)


if __name__ == "__main__":
    unittest.main()
