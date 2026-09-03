"""LIVE-STATE.md's Wake section must JUDGE, not transcribe.

Every fixture in this file is a RECORDED OBSERVATION, not a construction from the
rule under test -- a fixture derived from the rule it tests cannot disagree with
it. The Slurm transcripts below were captured read-only from saul.nersc.gov on
2026-08-19 (`squeue -h -r -j 57266000 -o '%i|%T|%r'`, `sacct -X -j 57266000 -n -P
-o JobID,State,ExitCode`, `scrontab -l`, `squeue --me -h -o '%i|%T|%Q|%S|%q|%j|%r'`)
and pasted verbatim. Array 57266000's ONLY task is 57266000_0, which is why a
watch armed with tasks="1" can never fire.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import subprocess
import tempfile
import os
import unittest

import generate_live_state
import wakerctl
from generate_live_state import LOUD, MAX_LINES, NO_EVIDENCE, QUIET, render, render_watch, tick_line

# --- recorded 2026-08-19, read-only, from saul.nersc.gov ---------------------
SQUEUE_57266000 = "57266000_0|PENDING|ReqNodeNotAvail, Reserved for maintenance\n"
SACCT_57266000 = "57266000_0|PENDING|0:0\n"
SCRONTAB_L = """# BEGIN wakerctl managed block
#SCRON -q cron
#SCRON -t 12:00:00
#SCRON -o /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/waker/logs/cron-tick.log
#SCRON --open-mode=append
*/5 * * * * /usr/bin/python3.11 /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/wakerctl.py tick --quiet
# END wakerctl managed block
"""
SQUEUE_ME = (
    "57275989|PENDING|1|2026-08-19T06:00:00|cron|/usr/bin/python3.11|BeginTime\n"
    "57266000_0|PENDING|68135|N/A|gpu_shared|g5dotrain|ReqNodeNotAvail, Reserved for maintenance\n"
)

# The watch as it actually stood, armed for ~45 h on a task its array lacks.
UNHEALTHY_WATCH = {
    "watch_id": "gate5-do-train-57266000-r2",
    "kind": "slurm-array",
    "state": "armed",
    "params": {"job_id": "57266000", "tasks": "1"},
}
# The same watch with the spec the array actually has.
HEALTHY_WATCH = {
    "watch_id": "gate5-do-train-57266000-r2",
    "kind": "slurm-array",
    "state": "armed",
    "params": {"job_id": "57266000", "tasks": "0-0"},
}
STALE_TICK = {"at_utc": "2026-08-17T15:05:14+00:00", "node": "login11"}
FRESH_TICK = {"at_utc": "2026-08-19T12:40:28+00:00", "node": "login11"}
NOW = dt.datetime(2026, 8, 19, 12, 40, 28, tzinfo=dt.timezone.utc).timestamp()


def completed(argv, stdout, returncode=0):
    return subprocess.CompletedProcess(argv, returncode, stdout=stdout, stderr="")


def make_runner(*, missing=False):
    """Replay the recorded transcripts; `missing` models a host with no Slurm."""

    def runner(argv, env=None, cwd=None, input_text=None):
        if missing:
            raise FileNotFoundError(2, "No such file or directory", argv[0])
        command = argv[0]
        if command == "scrontab":
            return completed(argv, SCRONTAB_L)
        if command == "squeue":
            if "--me" in argv:
                return completed(argv, SQUEUE_ME)
            return completed(argv, SQUEUE_57266000)
        if command == "sacct":
            return completed(argv, SACCT_57266000)
        raise AssertionError(f"unexpected command in test: {argv}")

    return runner


class WakeHealthRenderTests(unittest.TestCase):
    def ctx(self, *, watches=(), tick=None, missing=False, now=NOW):
        directory = pathlib.Path(tempfile.mkdtemp(prefix="waker-test-"))
        (directory / "watches").mkdir()
        for watch in watches:
            (directory / "watches" / f"{watch['watch_id']}.json").write_text(json.dumps(watch))
        if tick is not None:
            (directory / "last-tick.json").write_text(json.dumps(tick))
        return wakerctl.Ctx(state_dir=directory, runner=make_runner(missing=missing), clock=lambda: now)

    # -- defect 1: the watch render showed `state` and never `params` ---------

    def test_unhealthy_watch_renders_LOUD_with_its_subject(self):
        ctx = self.ctx(watches=[UNHEALTHY_WATCH], tick=FRESH_TICK)
        severity, text = render_watch(UNHEALTHY_WATCH, ctx)
        self.assertEqual(severity, LOUD, text)
        self.assertIn("tasks='1' -> task ids [1]", text)
        self.assertIn("job 57266000", text)
        self.assertIn("DOES NOT EXIST", text)
        self.assertIn("⚠", text)
        self.assertIn("monitor-error", text)
        self.assertNotIn("subject OBSERVED", text)

    def test_healthy_watch_renders_QUIET_and_unalarming(self):
        ctx = self.ctx(watches=[HEALTHY_WATCH], tick=FRESH_TICK)
        severity, text = render_watch(HEALTHY_WATCH, ctx)
        self.assertEqual(severity, QUIET, text)
        self.assertIn("tasks='0-0' -> task ids [0]", text)
        self.assertIn("subject OBSERVED in Slurm", text)
        # BEN-199: the passing state must be quiet, or nobody reads the check.
        self.assertNotIn("⚠", text)
        self.assertNotIn("DOES NOT EXIST", text)
        self.assertNotIn("NO EVIDENCE", text)

    def test_disarmed_is_not_armed_because_the_state_is_a_WHOLE_field(self):
        # The substring trap, asserted in the direction it bites: a prior
        # session's `grep -c '...armed'` returned 2 where exactly one watch was
        # armed, because "disarmed" CONTAINS "armed".
        self.assertIn("armed", "disarmed")
        watch = dict(UNHEALTHY_WATCH, state="disarmed")
        ctx = self.ctx(watches=[watch], tick=FRESH_TICK)
        severity, text = render_watch(watch, ctx)
        self.assertEqual(severity, QUIET, text)
        self.assertIn("(slurm-array:disarmed", text)
        self.assertIn("not armed, so its subject was not probed", text)
        # The subject is still shown -- a retired watch's params stay auditable.
        self.assertIn("tasks='1' -> task ids [1]", text)

    def test_no_slurm_is_NO_EVIDENCE_and_never_a_health_claim(self):
        ctx = self.ctx(watches=[UNHEALTHY_WATCH], tick=FRESH_TICK, missing=True)
        severity, text = render_watch(UNHEALTHY_WATCH, ctx)
        self.assertEqual(severity, NO_EVIDENCE, text)
        self.assertIn("NO EVIDENCE", text)
        self.assertIn("NOT a claim the subject exists", text)
        self.assertNotIn("subject OBSERVED", text)

    def test_invalid_and_missing_params_do_not_crash_the_render(self):
        ctx = self.ctx(tick=FRESH_TICK)
        _, text = render_watch(dict(UNHEALTHY_WATCH, params={"job_id": "57266000", "tasks": "3-1"}), ctx)
        self.assertIn("INVALID SPEC", text)
        _, text = render_watch({"watch_id": "w", "kind": "slurm-array", "state": "armed"}, ctx)
        self.assertIn("carries no `params`", text)

    # -- defect 2: `Last tick:` was printed verbatim, unjudged ----------------

    def test_stale_tick_renders_LOUD_with_the_age(self):
        ctx = self.ctx(tick=STALE_TICK)
        severity, text = tick_line(STALE_TICK, ctx)
        self.assertEqual(severity, LOUD, text)
        self.assertIn("2026-08-17T15:05:14+00:00", text)
        self.assertIn("45.6 h old", text)
        self.assertIn("SUPERVISION NET NOT HEALTHY", text)
        self.assertIn("STALE", text)
        self.assertIn("5 m from the managed scrontab block", text)
        self.assertNotIn("FRESH", text)

    def test_fresh_tick_renders_QUIET(self):
        ctx = self.ctx(tick=FRESH_TICK, now=NOW + 180)
        severity, text = tick_line(FRESH_TICK, ctx)
        self.assertEqual(severity, QUIET, text)
        self.assertIn("FRESH, 3 min old", text)
        self.assertIn("bound 30 min = 5 m from the managed scrontab block x 6", text)
        self.assertNotIn("⚠", text)
        self.assertNotIn("STALE", text)
        self.assertNotIn("NO EVIDENCE", text)

    def test_tick_without_slurm_is_NO_EVIDENCE_not_FRESH(self):
        ctx = self.ctx(tick=FRESH_TICK, missing=True)
        severity, text = tick_line(FRESH_TICK, ctx)
        self.assertEqual(severity, NO_EVIDENCE, text)
        self.assertIn("NOT A LIVENESS CLAIM", text)
        self.assertIn("ASSUMED", text)
        self.assertNotIn("FRESH", text)

    def test_tick_with_no_waker_ctx_is_NO_EVIDENCE(self):
        severity, text = tick_line(FRESH_TICK, None)
        self.assertEqual(severity, NO_EVIDENCE, text)
        self.assertIn("UNJUDGED", text)
        self.assertNotIn("FRESH", text)

    def test_missing_tick_receipt_is_reported_and_does_not_crash(self):
        ctx = self.ctx(tick=None)
        severity, text = tick_line({}, ctx)
        self.assertIn(severity, {LOUD, NO_EVIDENCE})
        self.assertIn("Last tick: never on unknown", text)


class WakeSectionEndToEndTests(unittest.TestCase):
    def fixtures(self):
        config = {
            "campaign": "test",
            "current_dag_node": "node",
            "state": "ACTIVE",
            "orchestrator_thread_id": "thread",
            "owners": [{"role": "worker", "uuid": "uuid-1", "purpose": "test"}],
            "blockers": ["blocked"],
            "next_authorized_action": "next",
            "wake": {"waker": True},
            "canonical_science": ["VALIDATION_LEDGER.md"],
            "append_only_history": ["docs/orchestration/RUNS.tsv"],
            "archival_index_only": ["superseded followup prompts"],
        }
        sessions = {"sessions": {"worker": {"session_id": "uuid-1", "provider": "agy", "profile": "agy"}}}
        usage = {
            "gate_ok": True,
            "profiles": {"codex-personal": {}, "codex-school": {}, "agy": {"status": "ok"}},
            "accounts": {"claude-school": {"status": "ok"}},
            "warnings": [],
        }
        jobs = [
            {
                "job_id": "57266000",
                "tasks": "0-0",
                "receipt": {"cpus_per_task": 32, "memory_per_task": "57472M", "time_limit": "2:00:00", "qos": "gpu_shared"},
                "snapshot": {"overall": "ACTIVE", "counts": {"PENDING": 1}, "error_tasks": []},
            }
        ]
        return config, sessions, usage, jobs

    def dashboard(self, watch, tick, *, missing=False, now=NOW):
        helper = WakeHealthRenderTests("test_stale_tick_renders_LOUD_with_the_age")
        ctx = helper.ctx(watches=[watch], tick=tick, missing=missing, now=now)
        config, sessions, usage, jobs = self.fixtures()
        wake_state = {
            "waker_status": {
                # PROJECTED exactly as wakerctl.status() projects it: no `params`.
                "watches": [{k: watch.get(k) for k in ("watch_id", "kind", "state")}],
                "events": [{"event_id": f"evt-{watch['watch_id']}", "state": "new"}],
                "last_tick": tick,
            }
        }
        text = render(
            config, sessions, usage, 0, jobs, {"head": "abc", "dirty_count": 0}, wake_state, "now",
            waker_ctx=ctx,
        )
        self.assertLessEqual(len(text.splitlines()), MAX_LINES)
        return text

    def test_dashboard_is_LOUD_on_the_real_failing_watch_and_stale_tick(self):
        text = self.dashboard(UNHEALTHY_WATCH, STALE_TICK)
        self.assertIn("Wake health: **UNHEALTHY**", text)
        self.assertIn("DOES NOT EXIST", text)
        self.assertIn("45.6 h old", text)
        print("\n--- LOUD render ---")
        for line in text.splitlines():
            if "watches:" in line or "Last tick" in line or "SUPERVISION NET" in line:
                print(line)

    def test_dashboard_is_QUIET_on_the_healthy_watch_and_fresh_tick(self):
        text = self.dashboard(HEALTHY_WATCH, FRESH_TICK, now=NOW + 180)
        self.assertNotIn("Wake health: **UNHEALTHY**", text)
        self.assertNotIn("Wake health: **UNKNOWN**", text)
        self.assertIn("subject OBSERVED in Slurm", text)
        self.assertIn("FRESH, 3 min old", text)
        print("\n--- QUIET render ---")
        for line in text.splitlines():
            if "watches:" in line or "Last tick" in line:
                print(line)

    def test_dashboard_without_slurm_says_NO_EVIDENCE_and_does_not_crash(self):
        text = self.dashboard(UNHEALTHY_WATCH, STALE_TICK, missing=True)
        self.assertIn("Wake health: **UNKNOWN**", text)
        self.assertIn("NO EVIDENCE", text)
        self.assertNotIn("subject OBSERVED", text)
        self.assertNotIn("FRESH,", text)

    def test_params_reach_the_render_even_though_status_projects_them_away(self):
        # The projected record in wake_state has no `params`; the subject can only
        # appear because render() re-reads the full watch files from the state dir.
        text = self.dashboard(HEALTHY_WATCH, FRESH_TICK, now=NOW + 180)
        self.assertIn("tasks='0-0' -> task ids [0]", text)
        self.assertNotIn("carries no `params`", text)


if __name__ == "__main__":
    unittest.main()


class AbsentWatchStoreIsNotZeroWatches(unittest.TestCase):
    """An absent state dir must render NO EVIDENCE, never `none`.

    2026-08-19: exactly one watch was armed on the cluster while this host had no
    state/waker at all. `", ".join(rendered) or "none"` rendered that as `none` --
    a claim about the world derived from a fact about the host. The section banner
    covered it, but a banner is prose and the line is what gets quoted.
    """

    def test_absent_store_is_not_readable(self):
        class Ctx:
            state_dir = "/nonexistent/definitely/not/here/waker"
        self.assertFalse(generate_live_state._watch_store_readable(Ctx()))

    def test_present_empty_store_IS_readable(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "watches"))

            class Ctx:
                state_dir = d
            self.assertTrue(generate_live_state._watch_store_readable(Ctx()))

    def test_none_ctx_is_not_readable(self):
        self.assertFalse(generate_live_state._watch_store_readable(None))
