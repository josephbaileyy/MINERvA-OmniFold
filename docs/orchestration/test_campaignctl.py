import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import campaignctl


class CampaignQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="campaign-queue-test.")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        os.system(f"git -C {self.repo} init -q")
        os.system(f"git -C {self.repo} config user.email test@example.invalid")
        os.system(f"git -C {self.repo} config user.name Test")
        self.script = self.repo / "work.py"
        self.script.write_text("from pathlib import Path\nPath('ran').write_text('yes')\n")
        os.system(f"git -C {self.repo} add work.py && git -C {self.repo} commit -qm initial")
        self.queue = campaignctl.Queue(
            repo=self.repo,
            state=self.root / "state",
            clock=lambda: "2026-08-25T12:00:00+00:00",
        )

    def stage(self, item_id="one", depends=None):
        return campaignctl.stage(
            self.queue, item_id, "test item", "write", ".", depends or [], [],
            [sys.executable, "work.py"], 30,
        )

    def approve(self, item):
        return campaignctl.approve(
            self.queue, item["id"], item["proposal_digest"], interactive=False
        )

    def test_stage_approve_and_run_exactly_once(self):
        item = self.stage()
        self.approve(item)
        rc, outcome = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, outcome["status"]), (0, "succeeded"))
        self.assertEqual((self.repo / "ran").read_text(), "yes")
        rc, value = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, value["status"]), (0, "idle"))

    def test_requires_exact_approval_digest(self):
        item = self.stage()
        with self.assertRaisesRegex(campaignctl.QueueError, "does not match"):
            campaignctl.approve(self.queue, item["id"], "0" * 64, interactive=False)

    def test_noninteractive_cli_approval_is_rejected(self):
        item = self.stage()
        with mock.patch.object(campaignctl.sys.stdin, "isatty", return_value=False):
            with self.assertRaisesRegex(campaignctl.QueueError, "interactive TTY"):
                campaignctl.approve(self.queue, item["id"], item["proposal_digest"])

    def test_bound_file_drift_fails_closed(self):
        item = self.stage()
        self.approve(item)
        self.script.write_text("raise SystemExit('changed')\n")
        rc, outcome = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, outcome["status"]), (4, "stale"))
        self.assertFalse((self.repo / "ran").exists())

    def test_head_drift_fails_closed(self):
        item = self.stage()
        self.approve(item)
        extra = self.repo / "extra"
        extra.write_text("x")
        os.system(f"git -C {self.repo} add extra && git -C {self.repo} commit -qm next")
        rc, outcome = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, outcome["status"]), (4, "stale"))

    def test_dependency_must_succeed_first(self):
        first = self.stage("first")
        second = self.stage("second", ["first"])
        self.approve(first)
        self.approve(second)
        self.assertEqual(campaignctl.run_ready(self.queue)[1]["id"], "first")
        self.assertEqual(campaignctl.run_ready(self.queue)[1]["id"], "second")

    def test_shell_and_external_executables_are_rejected(self):
        with self.assertRaisesRegex(campaignctl.QueueError, "outside repository"):
            campaignctl.stage(
                self.queue, "bad", "bad", "write", ".", [], [],
                ["/bin/bash", "-c", "true"], 30,
            )

    def test_claim_without_outcome_is_never_retried(self):
        item = self.stage()
        self.approve(item)
        campaignctl.atomic_json(
            self.queue.path("claims", item["id"]), {"id": item["id"]}, exclusive=True
        )
        rc, value = campaignctl.run_ready(self.queue)
        self.assertEqual((rc, value["status"]), (5, "outcome-unknown"))
        self.assertFalse((self.repo / "ran").exists())


if __name__ == "__main__":
    unittest.main()
