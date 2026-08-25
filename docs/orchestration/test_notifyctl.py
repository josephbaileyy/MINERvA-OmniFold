from pathlib import Path
import tempfile
import unittest
from unittest import mock

import notifyctl


class NotificationFanoutTests(unittest.TestCase):
    def config(self):
        return {
            "email": {"enabled": True, "command": ["mail", "-s", "{subject}", "user@example.com"]},
            "ntfy": {"enabled": True, "base_url": "https://ntfy.sh", "include_body": False},
        }

    def test_independent_markers_prevent_email_duplicate_when_ntfy_retries(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            email_calls = []
            ntfy_calls = []

            def email(*args, **kwargs):
                email_calls.append((args, kwargs))

            def ntfy(*args, **kwargs):
                ntfy_calls.append((args, kwargs))
                if len(ntfy_calls) == 1:
                    raise notifyctl.NotifyError("temporary")

            with mock.patch.object(notifyctl, "send_email", side_effect=email):
                with mock.patch.object(notifyctl, "send_ntfy", side_effect=ntfy):
                    self.assertEqual(
                        notifyctl.send(self.config(), {"ntfy": {"topic": "secret"}}, state, "key", "subject", "body"),
                        1,
                    )
                    self.assertEqual(
                        notifyctl.send(self.config(), {"ntfy": {"topic": "secret"}}, state, "key", "subject", "body"),
                        0,
                    )
            self.assertEqual(len(email_calls), 1)
            self.assertEqual(len(ntfy_calls), 2)

    def test_ntfy_defaults_to_generic_body(self):
        captured = {}

        def post(url, data, headers, timeout):
            captured.update(url=url, data=data, headers=headers, timeout=timeout)

        config = {
            "base_url": "https://ntfy.sh",
            "include_body": False,
            "generic_body": "generic",
        }
        with mock.patch.object(notifyctl, "http_post", side_effect=post):
            notifyctl.send_ntfy(config, {"ntfy": {"topic": "abc"}}, "A subject", "sensitive body")
        self.assertEqual(captured["url"], "https://ntfy.sh/abc")
        self.assertEqual(captured["data"], b"generic")
        self.assertNotIn(b"sensitive", captured["data"])

    def test_missing_optional_heartbeat_is_noop(self):
        self.assertEqual(
            notifyctl.heartbeat({"heartbeat": {"enabled": True}}, {}),
            0,
        )

    def test_marker_key_cannot_escape_state_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            marker = notifyctl.marker_path(state, "../../escape", "email")
            self.assertEqual(marker.parent, state / "notification-channels")
            self.assertNotIn("..", marker.name)


if __name__ == "__main__":
    unittest.main()
