"""Preflight must detect the 2026-08-19 three-way control failure, not narrate it.

EVERY FIXTURE IN THIS FILE IS A TRANSCRIPT, NOT A CONSTRUCTION. A fixture derived from
the rule under test cannot disagree with the rule (BEN-476), so each failing input below
is the literal output of the real command against the real wedged control plane, captured
from Perlmutter on 2026-08-19, and each healthy input is the same command against the same
cluster in a state that genuinely is healthy:

  (1) `scrontab -l`                                    -> SCRONTAB_REAL
      `squeue --me -o '%i|%T|%Q|%S|%q|%j|%r'`           -> SQUEUE_CRON_HELD
      state/waker/last-tick.json                       -> LAST_TICK_REAL (2026-08-17T15:05:14Z)
  (2) watches/gate5-do-train-57266000-r2.json params    -> WATCH_R2_PARAMS  (tasks="1")
      `sacct -X -j 57266000 -n -P -o JobID,State,ExitCode` -> SACCT_57266000
      `squeue -h -r -j 57266000 -o '%i|%T|%r'`          -> SQUEUE_57266000
      The healthy negative is spec "0-0" against the SAME array: overall=ACTIVE,
      unknown_tasks=[] -- a real healthy subject, not a mock.
  (3) the disarmed predecessor gate5-do-train-57266000 carries the identical bad spec,
      and is the input that a substring state test ("armed" in "disarmed") mishandles.

Slurm does not exist on the host these tests run on; every check reaches Slurm through
ctx.runner, so all of it is exercised here, including the must-not-report-PASS path.
"""

import json
from pathlib import Path
import stat
import tempfile
import types
import unittest

import wakerctl


ROOT_THREAD = "00000000-0000-0000-0000-00000000abcd"

# `scrontab -l` on Perlmutter, 2026-08-19 (paths as they really are there).
SCRONTAB_REAL = """# BEGIN wakerctl managed block
#SCRON -q cron
#SCRON -t 12:00:00
#SCRON -o /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/waker/logs/cron-tick.log
#SCRON --open-mode=append
*/5 * * * * /usr/bin/python3.11 /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/wakerctl.py tick --quiet
# END wakerctl managed block
"""

# `squeue --me` for the tick job 56585597: PENDING, Priority=0, no start time,
# Reason="user env retrieval failed requeued held", Restarts=1869, last real
# execution 2026-08-17T15:05Z. Field order is wakerctl's (reason last).
SQUEUE_CRON_HELD = (
    "56585597|PENDING|0|N/A|cron|/usr/bin/python3.11|user env retrieval failed requeued held\n"
    "57266000_0|PENDING|68100|N/A|gpu_shared|g5dotrain|ReqNodeNotAvail, Reserved for maintenance\n"
)
# The same row for a tick job that Slurm will actually run: priority accrued and the
# next cron slot scheduled. This is the only difference; nothing else was touched.
SQUEUE_CRON_RUNNABLE = (
    "56585597|PENDING|4021|2026-08-19T12:05:00|cron|/usr/bin/python3.11|None\n"
    "57266000_0|PENDING|68100|N/A|gpu_shared|g5dotrain|ReqNodeNotAvail, Reserved for maintenance\n"
)

LAST_TICK_REAL = {
    "at_utc": "2026-08-17T15:05:14+00:00",
    "node": "login27",
    "pid": 1820039,
    "watch_errors": 0,
}
NOW = wakerctl.parse_utc("2026-08-19T12:00:00+00:00")  # ~45 h after the last real tick

SACCT_57266000 = "57266000_0|PENDING|0:0\n"
SQUEUE_57266000 = "57266000_0|PENDING|ReqNodeNotAvail, Reserved for maintenance\n"
WATCH_R2_PARAMS = {"job_id": "57266000", "tasks": "1"}  # verbatim from the armed watch
HEALTHY_PARAMS = {"job_id": "57266000", "tasks": "0-0"}  # the spec the array really has


class FakeRunner:
    """ctx.runner stand-in: first matching rule wins, unmatched calls are recorded."""

    def __init__(self):
        self.rules = []
        self.calls = []

    def add(self, predicate, returncode=0, stdout=""):
        self.rules.append((predicate, returncode, stdout))
        return self

    def __call__(self, argv, env=None, cwd=None, input_text=None):
        self.calls.append(list(argv))
        for predicate, returncode, stdout in self.rules:
            if predicate(list(argv)):
                return types.SimpleNamespace(returncode=returncode, stdout=stdout)
        return types.SimpleNamespace(returncode=0, stdout="")

    def saw(self, program):
        return [call for call in self.calls if call and call[0] == program]


def is_scrontab_list(argv):
    return argv[:2] == ["scrontab", "-l"]


def is_squeue_me(argv):
    return argv[0] == "squeue" and "--me" in argv


def is_squeue_job(argv):
    return argv[0] == "squeue" and "-j" in argv


def is_sacct(argv):
    return argv[0] == "sacct"


class PreflightHealthTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="waker-health-test.")
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.codex = self.dir / "codex"
        self.codex.write_text("#!/bin/bash\nexit 0\n")
        self.codex.chmod(self.codex.stat().st_mode | stat.S_IXUSR)
        self.config_path = self.dir / "waker-config.json"
        self.config_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "python": "/usr/bin/python3.11",
                    "state_dir": "state/waker",
                    "codex_bin": str(self.codex),
                    "root": {
                        "provider": "codex",
                        "profile": "codex-personal",
                        "thread_id": ROOT_THREAD,
                        "disable_features": ["goals"],
                    },
                }
            )
        )
        self.runner = FakeRunner()

    def ctx(self, runner=None, now=NOW):
        return wakerctl.Ctx(
            config_path=self.config_path,
            state_dir=self.dir / "state",
            runner=runner or self.runner,
            clock=lambda: now,
        )

    # -- helpers -----------------------------------------------------------
    def write_tick(self, receipt=None):
        ctx = self.ctx()
        ctx.state_dir.mkdir(parents=True, exist_ok=True)
        (ctx.state_dir / "last-tick.json").write_text(
            json.dumps(LAST_TICK_REAL if receipt is None else receipt)
        )

    def write_watch(self, watch_id, params, state="armed", kind="slurm-array"):
        ctx = self.ctx()
        ctx.watches_dir.mkdir(parents=True, exist_ok=True)
        (ctx.watches_dir / f"{watch_id}.json").write_text(
            json.dumps(
                {
                    "watch_id": watch_id,
                    "kind": kind,
                    "params": params,
                    "state": state,
                    "armed_at_utc": "2026-08-19T05:39:52+00:00",
                    "unreliable": 0,
                    "action": {"type": "root-resume", "context": "fixture"},
                }
            )
        )

    def array_runner(self, sacct=SACCT_57266000, squeue=SQUEUE_57266000, rc=0):
        runner = FakeRunner()
        runner.add(is_sacct, rc, sacct)
        runner.add(is_squeue_job, rc, squeue)
        return runner


class CronTickerChecks(PreflightHealthTestCase):
    """(1) The schedule existed the whole time; the job it schedules could not run."""

    def held_runner(self, squeue=SQUEUE_CRON_HELD, scrontab=SCRONTAB_REAL):
        runner = FakeRunner()
        runner.add(is_scrontab_list, 0, scrontab)
        runner.add(is_squeue_me, 0, squeue)
        return runner

    def test_fires_on_the_real_held_tick_job(self):
        problems = wakerctl.check_cron_job_runnable(self.ctx(self.held_runner()))
        text = " || ".join(problems)
        self.assertTrue(problems, "a held Priority=0 tick job must be reported")
        self.assertIn("56585597", text)
        self.assertIn("HELD", text)
        self.assertIn("Priority=0", text)
        self.assertIn("no eligible start time", text)

    def test_does_not_fire_on_a_runnable_tick_job(self):
        problems = wakerctl.check_cron_job_runnable(
            self.ctx(self.held_runner(squeue=SQUEUE_CRON_RUNNABLE))
        )
        self.assertEqual(problems, [])

    def test_does_not_confuse_the_users_other_jobs_for_the_ticker(self):
        """57266000_0 is PENDING with no start time too -- but its QOS is not `cron`."""
        runner = self.held_runner(squeue=SQUEUE_CRON_RUNNABLE)
        problems = wakerctl.check_cron_job_runnable(self.ctx(runner))
        self.assertEqual(problems, [])

    def test_unreachable_squeue_reports_no_evidence_and_never_silence(self):
        runner = FakeRunner()
        runner.add(is_scrontab_list, 0, SCRONTAB_REAL)
        runner.add(is_squeue_me, 1, "slurm_load_jobs error: Unable to contact slurm controller")
        problems = wakerctl.check_cron_job_runnable(self.ctx(runner))
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith(wakerctl.NO_EVIDENCE_PREFIX), problems[0])

    def test_installed_schedule_with_no_cron_job_at_all_fires(self):
        runner = self.held_runner(squeue="")
        problems = wakerctl.check_cron_job_runnable(self.ctx(runner))
        self.assertTrue(any("no QOS=cron job" in problem for problem in problems), problems)

    def test_interval_comes_from_the_real_managed_block(self):
        self.assertEqual(wakerctl.cron_interval_minutes(SCRONTAB_REAL.splitlines()), 5)
        # Slurm echoes the same schedule back as an explicit list in CrontabSpec.
        self.assertEqual(
            wakerctl.minute_field_interval("0,5,10,15,20,25,30,35,40,45,50,55"), 5
        )
        self.assertIsNone(wakerctl.minute_field_interval("H/5"))

    def test_stale_receipt_fires_on_the_real_45_hour_gap(self):
        self.write_tick()
        problems = wakerctl.check_tick_freshness(self.ctx(), 5)
        self.assertEqual(len(problems), 1)
        self.assertIn("STALE", problems[0])
        self.assertIn("2026-08-17T15:05:14", problems[0])

    def test_fresh_receipt_does_not_fire(self):
        self.write_tick({"at_utc": "2026-08-19T11:58:00+00:00", "watch_errors": 0})
        self.assertEqual(wakerctl.check_tick_freshness(self.ctx(), 5), [])

    def test_absent_receipt_fires(self):
        problems = wakerctl.check_tick_freshness(self.ctx(), 5)
        self.assertTrue(any("no tick receipt" in problem for problem in problems), problems)

    def test_unknown_interval_is_no_evidence_not_pass(self):
        self.write_tick({"at_utc": "2026-08-19T11:58:00+00:00", "watch_errors": 0})
        problems = wakerctl.check_tick_freshness(self.ctx(), None)
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith(wakerctl.NO_EVIDENCE_PREFIX), problems[0])

    def test_unreadable_scrontab_is_no_evidence_but_an_empty_one_is_a_failure(self):
        runner = FakeRunner().add(is_scrontab_list, 1, "scrontab: error contacting slurmctld")
        problems = wakerctl.check_cron_ticker(self.ctx(runner))
        self.assertTrue(
            any(problem.startswith(wakerctl.NO_EVIDENCE_PREFIX) for problem in problems), problems
        )
        empty = FakeRunner().add(is_scrontab_list, 1, "no crontab for josephrb")
        problems = wakerctl.check_cron_ticker(self.ctx(empty))
        self.assertTrue(any("managed scrontab block is absent" in p for p in problems), problems)

    def test_whole_check_fires_end_to_end_on_the_real_wedged_control_plane(self):
        self.write_tick()
        problems = wakerctl.check_cron_ticker(self.ctx(self.held_runner()))
        text = " || ".join(problems)
        self.assertIn("HELD", text)
        self.assertIn("STALE", text)


class ArmedWatchSubjectChecks(PreflightHealthTestCase):
    """(2) The check no existing control performed: does the subject exist?"""

    def test_fires_on_the_real_watch_armed_on_a_task_the_array_lacks(self):
        self.write_watch("gate5-do-train-57266000-r2", WATCH_R2_PARAMS)
        problems = wakerctl.check_armed_watch_subjects(self.ctx(self.array_runner()))
        self.assertEqual(len(problems), 1, problems)
        problem = problems[0]
        self.assertIn("gate5-do-train-57266000-r2", problem)
        self.assertIn("DOES NOT EXIST", problem)
        self.assertIn("'1'", problem)  # the requested spec, as written
        self.assertIn("[1]", problem)  # the unknown set
        self.assertIn("57266000", problem)

    def test_does_not_fire_on_the_healthy_spec_for_the_same_array(self):
        self.write_watch("gate5-do-train-57266000-healthy", HEALTHY_PARAMS)
        self.assertEqual(wakerctl.check_armed_watch_subjects(self.ctx(self.array_runner())), [])

    def test_unreachable_slurm_reports_no_evidence_not_a_missing_subject(self):
        self.write_watch("gate5-do-train-57266000-r2", WATCH_R2_PARAMS)
        problems = wakerctl.check_armed_watch_subjects(
            self.ctx(self.array_runner(rc=1, sacct="sacct: error", squeue="squeue: error"))
        )
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith(wakerctl.NO_EVIDENCE_PREFIX), problems[0])
        self.assertNotIn("DOES NOT EXIST", problems[0])

    def test_only_armed_watches_are_checked_and_disarmed_never_matches(self):
        """(3) The disarmed predecessor carries the identical bad spec.

        A substring test is what reported two armed watches for this job; both
        directions are asserted so the whole-field rule cannot silently regress.
        """
        self.write_watch("gate5-do-train-57266000", WATCH_R2_PARAMS, state="disarmed")
        self.assertEqual(wakerctl.check_armed_watch_subjects(self.ctx(self.array_runner())), [])
        disarmed = {"state": "disarmed"}
        self.assertFalse(wakerctl.is_armed(disarmed))
        self.assertTrue(wakerctl.is_armed({"state": "armed"}))
        self.assertIn("armed", wakerctl.watch_state(disarmed))  # the trap, made explicit
        self.assertNotEqual(wakerctl.watch_state(disarmed), "armed")

    def test_slurm_job_watch_on_an_unknown_job_fires(self):
        self.write_watch("ghost-job", {"job_id": "99999999"}, kind="slurm-job")
        runner = FakeRunner().add(is_sacct, 0, "").add(is_squeue_job, 0, "")
        problems = wakerctl.check_armed_watch_subjects(self.ctx(runner))
        self.assertTrue(any("DOES NOT EXIST" in problem for problem in problems), problems)

    def test_slurm_job_watch_on_a_known_job_does_not_fire(self):
        self.write_watch("real-job", {"job_id": "57266000"}, kind="slurm-job")
        runner = FakeRunner().add(is_sacct, 0, "57266000|RUNNING|0:0\n").add(is_squeue_job, 0, "")
        self.assertEqual(wakerctl.check_armed_watch_subjects(self.ctx(runner)), [])

    def test_a_malformed_task_spec_is_reported_rather_than_raising(self):
        self.write_watch("bad-spec", {"job_id": "57266000", "tasks": "5-2"})
        problems = wakerctl.check_armed_watch_subjects(self.ctx(self.array_runner()))
        self.assertTrue(any("not a valid task spec" in problem for problem in problems), problems)

    def test_non_slurm_watches_are_ignored(self):
        self.write_watch("sent", {"path": str(self.dir / "x")}, kind="file-sentinel")
        self.assertEqual(wakerctl.check_armed_watch_subjects(self.ctx(self.array_runner())), [])


class PreflightWiring(PreflightHealthTestCase):
    def full_runner(self):
        runner = FakeRunner()
        runner.add(is_scrontab_list, 0, SCRONTAB_REAL)
        runner.add(is_squeue_me, 0, SQUEUE_CRON_HELD)
        runner.add(is_sacct, 0, SACCT_57266000)
        runner.add(is_squeue_job, 0, SQUEUE_57266000)
        return runner

    def test_control_plane_preflight_reports_both_failures(self):
        self.write_tick()
        self.write_watch("gate5-do-train-57266000-r2", WATCH_R2_PARAMS)
        problems = wakerctl.preflight(self.ctx(self.full_runner()), quiet=True, control_plane=True)
        text = " || ".join(problems)
        self.assertIn("HELD", text)
        self.assertIn("STALE", text)
        self.assertIn("gate5-do-train-57266000-r2", text)

    def test_dispatch_path_preflight_is_unchanged_and_touches_no_slurm(self):
        """dispatch_one() gates on preflight(quiet=True); it must not gain a Slurm dependency."""
        self.write_tick()
        self.write_watch("gate5-do-train-57266000-r2", WATCH_R2_PARAMS)
        runner = self.full_runner()
        problems = wakerctl.preflight(self.ctx(runner), quiet=True)
        self.assertEqual(runner.saw("squeue"), [])
        self.assertEqual(runner.saw("scrontab"), [])
        self.assertNotIn("gate5-do-train-57266000-r2", " || ".join(problems))
        self.assertNotIn("STALE", " || ".join(problems))


class WatchAddValidation(PreflightHealthTestCase):
    def add(self, params, runner=None):
        ctx = self.ctx(runner or self.array_runner())
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "wa-test",
                "kind": "slurm-array",
                "params": params,
                "action": {"type": "root-resume", "context": "fixture"},
            },
        )
        return ctx

    def test_rejects_the_real_bad_spec_at_add_time(self):
        with self.assertRaises(wakerctl.WakerError) as caught:
            self.add(dict(WATCH_R2_PARAMS))
        message = str(caught.exception)
        self.assertIn("57266000", message)
        self.assertIn("[1]", message)
        self.assertIn("[0]", message)  # what the array actually has
        ctx = self.ctx()
        self.assertFalse((ctx.watches_dir / "wa-test.json").exists(), "rejected watch must not land")

    def test_accepts_the_real_healthy_spec(self):
        ctx = self.add(dict(HEALTHY_PARAMS))
        self.assertTrue((ctx.watches_dir / "wa-test.json").exists())

    def test_arms_with_no_evidence_when_slurm_cannot_be_reached(self):
        """Arming a watch for a job Slurm cannot confirm must not be blocked; preflight is the net."""
        ctx = self.add(dict(WATCH_R2_PARAMS), runner=self.array_runner(rc=1, sacct="", squeue=""))
        self.assertTrue((ctx.watches_dir / "wa-test.json").exists())


if __name__ == "__main__":
    unittest.main()
