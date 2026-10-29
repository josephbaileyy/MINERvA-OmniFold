"""A host that cannot read the waker state dir must say so, and must not print its checkout path.

2026-10-28: dashboards rendered from a fresh clone (#469) read `Last tick: never on unknown` --
a missing file rendered as a state -- and embedded the clone's absolute path, which no longer
exists. Both directions are tested:
  * state dir ABSENT    -> NO EVIDENCE (or LOUD on a real scheduler finding), never "never", no path;
  * state dir PRESENT, no receipt -> still the measurement "never" (that one IS a reading).
"""
import pathlib
import tempfile
import unittest

import wakerctl
from generate_live_state import LOUD, NO_EVIDENCE, REPO, LastKnown, render, tick_line
from test_generate_live_state_watch_health import (
    FRESH_TICK, NOW, WakeSectionEndToEndTests, completed, make_runner)

# A state dir path inside this checkout that does not exist: what a fresh clone or a laptop sees.
ABSENT = REPO / "docs" / "orchestration" / "state" / "waker-absent-for-test"


def runner_without_block(argv, env=None, cwd=None, input_text=None):
    """The recorded transcripts, except that the scrontab holds no wakerctl block."""
    if argv[0] == "scrontab":
        return completed(argv, "# no managed block\n")
    return make_runner()(argv, env=env, cwd=cwd, input_text=input_text)


class UnreadStateDirTests(unittest.TestCase):
    def setUp(self):
        self.assertFalse(ABSENT.exists(), "the fixture path must not exist")

    def absent_ctx(self, runner):
        return wakerctl.Ctx(state_dir=ABSENT, runner=runner, clock=lambda: NOW)

    def test_absent_state_dir_with_a_healthy_schedule_is_NO_EVIDENCE(self):
        severity, text = tick_line({}, self.absent_ctx(make_runner()))
        self.assertEqual(severity, NO_EVIDENCE, text)
        self.assertIn("**NO EVIDENCE**", text)
        self.assertNotIn("never on", text)
        self.assertNotIn(str(REPO), text)
        self.assertNotIn("waker-absent-for-test", text)

    def test_absent_state_dir_keeps_a_real_scheduler_finding_LOUD(self):
        severity, text = tick_line({}, self.absent_ctx(runner_without_block))
        self.assertEqual(severity, LOUD, text)
        self.assertIn("scrontab block is absent", text)
        self.assertIn("**NO EVIDENCE**", text)
        self.assertNotIn("never on", text)
        self.assertNotIn(str(REPO), text)
        # the freshness finding is about a file this host could not read, so it is dropped
        self.assertNotIn("no tick receipt at", text)
        self.assertNotIn("staleness of", text)

    def test_readable_state_dir_without_a_receipt_still_reads_never(self):
        with tempfile.TemporaryDirectory() as directory:
            ctx = wakerctl.Ctx(state_dir=pathlib.Path(directory), runner=make_runner(),
                               clock=lambda: NOW)
            severity, text = tick_line({}, ctx)
        self.assertIn(severity, {LOUD, NO_EVIDENCE})
        self.assertIn("Last tick: never on unknown", text)
        self.assertNotIn("**NO EVIDENCE**", text)

    def test_the_dashboard_marks_the_reading_incomplete_and_records_no_tick(self):
        helper = WakeSectionEndToEndTests("test_dashboard_is_QUIET_on_the_healthy_watch_and_fresh_tick")
        config, sessions, usage, jobs = helper.fixtures()
        wake_state = {"waker_status": {"watches": [], "events": [], "last_tick": FRESH_TICK}}

        store = LastKnown(None, host="test-host", observed_at="now", head="abc")
        text = render(config, sessions, usage, 0, jobs, {"head": "abc", "dirty_count": 0},
                      wake_state, "now", waker_ctx=self.absent_ctx(runner_without_block),
                      last_known=store)
        self.assertIn("Wake health: **UNHEALTHY**", text)
        self.assertIn("NOT A COMPLETE READING", text)
        self.assertNotIn(str(REPO), text)
        self.assertNotIn("waker:last-tick", store.probes)
        self.assertNotIn(FRESH_TICK["at_utc"] + " on", text)


if __name__ == "__main__":
    unittest.main()
