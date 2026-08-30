"""Tests for dashboard_collector.

The fixtures are verbatim output captured from Perlmutter on 2026-08-30, not strings
written to match the parser.  A fixture derived from the rule cannot disagree with it.
"""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dashboard_collector as dc


class FrozenClock(dc.Clock):
    def __init__(self, epoch: float):
        self.epoch = epoch

    def now(self) -> float:
        return self.epoch


# 2026-08-30T05:31:17Z, the instant the reference fixtures were captured.
NOW = 1788067877.0

# --- verbatim captures -----------------------------------------------------

CRON_PARTITION = (
    "PartitionName=cron\n   AllocNodes=ALL Default=NO QoS=cron\n"
    "   DefaultTime=00:10:00 MaxTime=90-00:00:00\n"
    "   Nodes=login[01-40]\n   State=UP TotalNodes=40\n"
)
RESERVATIONS = (
    "ReservationName=debug StartTime=2025-11-06T06:03:31 EndTime=2026-11-06T06:03:31\n"
    "   Nodes=login17,nid[001164-001165,001204-001205] NodeCnt=44 "
    "Flags=MAINT,IGNORE_JOBS,SPEC_NODES\n"
    "   State=ACTIVE BurstBuffer=(null)\n"
)
TMUX_SESSIONS = "mnv-orch: 3 windows (created Sat Aug 29 14:53:00 2026)\n"
TMUX_NO_SOCKET = "error connecting to /run/tmux/112498/default (No such file or directory)\n"
TMUX_NO_SERVER = "no server running on /run/tmux/112498/default\n"
BANNER = (
    "***************************************************************************\n"
    "                          NOTICE TO USERS\n\n"
    "Lawrence Berkeley National Laboratory operates this computer system under\n"
    "contract to the U.S. Department of Energy.  This computer system is the\n"
    "property of the United States Government and is for authorized use only.\n"
    "*****************************************************************************\n"
)
PAM_NOLOGIN = (
    "\nLogin connection to host x3114c0s19b0n0:\n\n"
    "System is going down. Unprivileged users are not permitted to log in anymore. "
    "For technical details, see pam_nologin(8).\n\n"
    "Connection closed by 128.55.64.28 port 22\n"
)


class FakeRunner:
    """Matches argv by substring and returns a captured (rc, stdout, stderr)."""

    def __init__(self):
        self.rules = []
        self.calls = []

    def add(self, needle, rc=0, out="", err=""):
        self.rules.append((needle, rc, out, err))
        return self

    def __call__(self, argv, timeout=30.0):
        joined = " ".join(argv)
        self.calls.append(joined)
        for needle, rc, out, err in self.rules:
            if needle in joined:
                return rc, out, err
        return 127, "", f"no rule for: {joined}"


class HostlistTest(unittest.TestCase):
    def test_expands_padded_range_and_keeps_only_login_nodes(self):
        self.assertEqual(len(dc.expand_hostlist("login[01-40]")), 40)
        self.assertIn("login01", dc.expand_hostlist("login[01-40]"))
        self.assertIn("login40", dc.expand_hostlist("login[01-40]"))

    def test_drops_compute_nodes_from_a_mixed_reservation_list(self):
        hosts = dc.expand_hostlist("login17,nid[001164-001165,001204-001205]")
        self.assertEqual(hosts, ["login17"])

    def test_reads_the_node_list_from_slurm_rather_than_a_constant(self):
        runner = FakeRunner().add("show partition cron", 0, CRON_PARTITION)
        nodes, error = dc.login_nodes(runner)
        self.assertIsNone(error)
        self.assertEqual(len(nodes), 40)

    def test_a_failed_partition_query_yields_no_nodes_and_an_error(self):
        runner = FakeRunner().add("show partition cron", 1, "", "slurm_load_partitions: error")
        nodes, error = dc.login_nodes(runner)
        self.assertEqual(nodes, [])
        self.assertIn("rc=1", error)


class DurationAndStampTest(unittest.TestCase):
    def test_parses_slurm_duration_forms(self):
        self.assertEqual(dc.parse_duration("55:29"), 55 * 60 + 29)
        self.assertEqual(dc.parse_duration("1:00:00"), 3600)
        self.assertEqual(dc.parse_duration("2-00:00:00"), 172800)

    def test_unparseable_duration_is_none_not_zero(self):
        # UNLIMITED must not silently become "0 seconds left".
        self.assertIsNone(dc.parse_duration("UNLIMITED"))
        self.assertIsNone(dc.parse_duration("N/A"))

    def test_na_and_unknown_stamps_are_none(self):
        self.assertIsNone(dc.parse_utc_stamp("N/A"))
        self.assertIsNone(dc.parse_utc_stamp("Unknown"))

    def test_a_forced_utc_stamp_parses_as_utc(self):
        # Slurm printed this under TZ=UTC; reading it as local time would shift it 7 h.
        self.assertEqual(dc.parse_utc_stamp("2026-08-30T05:30:00"), 1788067800.0)


class EtaHonestyTest(unittest.TestCase):
    def test_running_job_reports_real_time_left(self):
        rows = [{"state": "RUNNING", "time_left_seconds": 3329, "time_left_text": "55:29",
                 "reason": "None", "token": "57727774_3"}]
        eta = dc.classify_eta(rows, {}, NOW)
        self.assertEqual(eta["kind"], "time_left")
        self.assertEqual(eta["seconds"], 3329)

    def test_pending_on_priority_reports_unknown_and_names_the_blocker(self):
        rows = [{"state": "PENDING", "time_left_seconds": 3600, "time_left_text": "1:00:00",
                 "reason": "Priority", "token": "57727774_4"}]
        eta = dc.classify_eta(rows, {"57727774_4": "N/A"}, NOW)
        self.assertEqual(eta["kind"], "unknown")
        self.assertIsNone(eta["seconds"])
        self.assertIn("Priority", eta["detail"])

    def test_pending_time_left_is_never_reported_as_an_eta(self):
        # A PENDING task's TIME_LEFT is its requested walltime, not time until anything.
        rows = [{"state": "PENDING", "time_left_seconds": 3600, "time_left_text": "1:00:00",
                 "reason": "Dependency", "token": "57727775_5"}]
        eta = dc.classify_eta(rows, {"57727775_5": "N/A"}, NOW)
        self.assertNotEqual(eta["kind"], "time_left")

    def test_a_future_start_estimate_is_shown_as_an_estimate(self):
        rows = [{"state": "PENDING", "time_left_seconds": None, "time_left_text": "",
                 "reason": "BeginTime", "token": "57712764"}]
        eta = dc.classify_eta(rows, {"57712764": "2026-08-30T05:35:00"}, NOW)
        self.assertEqual(eta["kind"], "start_estimate")
        self.assertGreater(eta["seconds"], 0)

    def test_a_past_start_estimate_is_stale_not_an_eta(self):
        rows = [{"state": "PENDING", "time_left_seconds": None, "time_left_text": "",
                 "reason": "BeginTime", "token": "57712764"}]
        eta = dc.classify_eta(rows, {"57712764": "2026-08-29T22:30:00"}, NOW)
        self.assertEqual(eta["kind"], "unknown")
        self.assertIn("past", eta["detail"])


class TmuxProbeTest(unittest.TestCase):
    def probe(self, rc, out="", err=""):
        runner = FakeRunner().add("login24", rc, out, err)
        return dc.probe_node("login24", runner, FrozenClock(NOW), 8.0)

    def test_sessions_are_parsed(self):
        row = self.probe(0, out=TMUX_SESSIONS)
        self.assertEqual(row["state"], "sessions")
        self.assertEqual(row["sessions"][0]["name"], "mnv-orch")
        self.assertEqual(row["sessions"][0]["windows"], 3)

    def test_no_age_is_derived_from_an_unzoned_tmux_timestamp(self):
        row = self.probe(0, out=TMUX_SESSIONS)
        self.assertIsNone(row["sessions"][0]["age_seconds"])
        self.assertIsNotNone(row["sessions"][0]["created_local_text"])

    def test_absent_socket_is_measured_false(self):
        self.assertEqual(self.probe(1, err=TMUX_NO_SOCKET)["state"], "no_tmux_server")

    def test_dead_server_is_measured_false_and_distinguishable(self):
        row = self.probe(1, err=TMUX_NO_SERVER)
        self.assertEqual(row["state"], "no_tmux_server")
        self.assertIn("server gone", row["detail"])

    def test_unreachable_node_is_unmeasured_not_empty(self):
        # THE central distinction: ssh failure must never read as "no sessions here".
        row = self.probe(255, err="ssh: connect to host login17 port 22: No route to host")
        self.assertEqual(row["state"], "unmeasured")
        self.assertIn("No route to host", row["error"])
        self.assertEqual(row["unreachable_cause"], "no_route")

    def test_a_session_banner_never_reaches_the_session_parser(self):
        # The banner is 24 lines of legal text on stderr; parsing must ignore it.
        row = self.probe(0, out=TMUX_SESSIONS, err=BANNER)
        self.assertEqual(len(row["sessions"]), 1)
        self.assertEqual(row["sessions"][0]["name"], "mnv-orch")

    def test_a_draining_node_reports_pam_nologin_not_a_bare_rc(self):
        row = self.probe(255, err=BANNER + PAM_NOLOGIN)
        self.assertEqual(row["state"], "unmeasured")
        self.assertEqual(row["unreachable_cause"], "draining")
        self.assertIn("System is going down", row["error"])
        # The banner must be stripped, or the reason is 200 chars of legal notice.
        self.assertNotIn("Lawrence Berkeley", row["error"])

    def test_probe_does_not_suppress_ssh_diagnostics(self):
        runner = FakeRunner().add("login24", 0, TMUX_SESSIONS)
        dc.probe_node("login24", runner, FrozenClock(NOW), 8.0)
        self.assertNotIn(" -q ", runner.calls[0])
        self.assertNotIn("LogLevel=ERROR", runner.calls[0])

    def test_probe_disables_connection_multiplexing(self):
        runner = FakeRunner().add("login24", 0, TMUX_SESSIONS)
        dc.probe_node("login24", runner, FrozenClock(NOW), 8.0)
        self.assertIn("ControlPath=none", runner.calls[0])


class SweepCoverageTest(unittest.TestCase):
    def runner_for(self, unreachable):
        runner = FakeRunner()
        runner.add("show partition cron", 0, CRON_PARTITION)
        runner.add("show reservation", 0, RESERVATIONS)
        for node in unreachable:
            runner.add(f" {node} ", 255, "", "ssh: connect: No route to host")
        runner.add("tmux ls", 1, "", TMUX_NO_SOCKET)
        return runner

    def test_partial_coverage_is_never_reported_complete(self):
        unreachable = [f"login{n:02d}" for n in (17, 19, 21, 22, 26, 27, 29, 30, 40)]
        rows, coverage, source = dc.collect_sweep(self.runner_for(unreachable), FrozenClock(NOW), 8.0)
        self.assertEqual(coverage["nodes_total"], 40)
        self.assertEqual(coverage["nodes_measured"], 31)
        self.assertFalse(coverage["complete"])
        self.assertEqual(len(coverage["unmeasured"]), 9)

    def test_unmeasured_nodes_are_listed_by_name_with_a_reason(self):
        rows, coverage, source = dc.collect_sweep(self.runner_for(["login17"]), FrozenClock(NOW), 8.0)
        entry = next(e for e in coverage["unmeasured"] if e["node"] == "login17")
        self.assertIn("No route to host", entry["reason"])
        self.assertTrue(entry["in_maint_reservation"])

    def test_full_coverage_is_reported_complete(self):
        rows, coverage, source = dc.collect_sweep(self.runner_for([]), FrozenClock(NOW), 8.0)
        self.assertTrue(coverage["complete"])
        self.assertEqual(coverage["nodes_measured"], 40)


class SourceTest(unittest.TestCase):
    def test_a_failed_source_has_no_age_and_no_staleness_verdict(self):
        source = dc.Source("waker_tick").fail("unreadable")
        payload = source.to_json(dc.DEFAULT_STALE_SECONDS)
        self.assertFalse(payload["ok"])
        self.assertIsNone(payload["age_seconds"])
        # `stale` must be null, not False: we did not measure it to be fresh.
        self.assertIsNone(payload["stale"])

    def test_a_fresh_source_is_not_stale(self):
        payload = dc.Source("waker_tick").succeed(7.0).to_json(dc.DEFAULT_STALE_SECONDS)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["stale"])

    def test_an_old_source_is_stale(self):
        payload = dc.Source("waker_tick").succeed(99999.0).to_json(dc.DEFAULT_STALE_SECONDS)
        self.assertTrue(payload["stale"])


class TickerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_receipt_age_comes_from_the_receipt_not_the_file_mtime(self):
        (self.state / "last-tick.json").write_text(
            json.dumps({"at_utc": "2026-08-30T05:31:14+00:00", "node": "login32",
                        "pid": 389138, "watch_errors": 0})
        )
        runner = FakeRunner().add("squeue", 0, "57712764|PENDING|BeginTime")
        ticker, source = dc.collect_ticker(self.state, runner, FrozenClock(NOW))
        self.assertTrue(source.ok)
        self.assertAlmostEqual(ticker["receipt"]["age_seconds"], 3.0, places=0)
        self.assertEqual(ticker["receipt"]["node"], "login32")

    def test_a_cron_job_is_reported_separately_from_the_tick(self):
        # The failure this guards: a restarting scron job read as evidence of work.
        (self.state / "last-tick.json").write_text(
            json.dumps({"at_utc": "2026-08-25T00:00:00+00:00", "node": "login35"})
        )
        runner = FakeRunner().add("squeue", 0, "57712764|PENDING|BeginTime")
        ticker, source = dc.collect_ticker(self.state, runner, FrozenClock(NOW))
        self.assertEqual(len(ticker["scron"]["jobs"]), 1)
        self.assertIn("not evidence", ticker["scron"]["note"])
        self.assertTrue(source.to_json(dc.DEFAULT_STALE_SECONDS)["stale"])

    def test_a_missing_receipt_fails_the_source(self):
        runner = FakeRunner().add("squeue", 0, "")
        ticker, source = dc.collect_ticker(self.state, runner, FrozenClock(NOW))
        self.assertFalse(source.ok)
        self.assertIsNone(ticker["receipt"])

    def test_a_daemon_lock_is_labelled_as_a_start_not_a_heartbeat(self):
        (self.state / "last-tick.json").write_text(json.dumps({"at_utc": "2026-08-30T05:31:14Z"}))
        (self.state / "daemon-login32.lock").write_text("")
        runner = FakeRunner().add("squeue", 0, "")
        ticker, _ = dc.collect_ticker(self.state, runner, FrozenClock(NOW))
        self.assertEqual(ticker["daemon_locks"][0]["node"], "login32")
        self.assertIn("STARTED", ticker["daemon_locks"][0]["note"])


class JobsTest(unittest.TestCase):
    def runner(self):
        runner = FakeRunner()
        runner.add("--me -h -r -o %i|%j|%P|%T|%L|%M|%r|%N", 0,
                   "57727774_3|g6gap1push|shared_gp|RUNNING|55:29|4:31|None|nid008597\n"
                   "57727774_4|g6gap1push|shared_gp|PENDING|1:00:00|0:00|Priority|\n")
        runner.add("--start", 0, "57727774_3|N/A\n57727774_4|N/A\n")
        runner.add("squeue -h -r -j 57727774", 0,
                   "57727774_3|RUNNING|None\n57727774_4|PENDING|Priority\n")
        runner.add("sacct", 0, "")
        return runner

    def test_classification_is_delegated_to_slurm_array_status(self):
        jobs, source = dc.collect_jobs(self.runner(), FrozenClock(NOW))
        self.assertTrue(source.ok)
        self.assertEqual(jobs[0]["overall"], "ACTIVE")
        self.assertEqual(jobs[0]["tasks_total"], 2)

    def test_a_job_slurm_cannot_be_asked_about_is_unobserved_not_active(self):
        runner = self.runner()
        # Both observers fail: build_snapshot must not call that ACTIVE.
        runner.rules = [r for r in runner.rules if "-j 57727774" not in r[0] and "sacct" != r[0]]
        runner.add("squeue -h -r -j 57727774", 1, "", "slurm_load_jobs error")
        runner.add("sacct", 1, "", "sacct: error")
        jobs, source = dc.collect_jobs(runner, FrozenClock(NOW))
        self.assertEqual(jobs[0]["overall"], "UNOBSERVED")
        self.assertTrue(jobs[0]["observer_errors"])

    def test_a_failed_queue_query_fails_the_source_and_yields_no_jobs(self):
        runner = FakeRunner().add("squeue", 1, "", "slurm_load_jobs error: Unable to contact slurm")
        jobs, source = dc.collect_jobs(runner, FrozenClock(NOW))
        self.assertEqual(jobs, [])
        self.assertFalse(source.ok)


class SecretsTest(unittest.TestCase):
    def test_writing_into_the_state_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "waker"
            state.mkdir()
            with self.assertRaises(SystemExit) as caught:
                dc.guard_output_path(state / "status.json", state)
            self.assertIn("notification-secrets.json", str(caught.exception))

    def test_a_web_path_outside_the_state_directory_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "waker"
            state.mkdir()
            dc.guard_output_path(Path(tmp) / "www" / "status.json", state)

    def test_the_collector_never_opens_the_secrets_file(self):
        """Record every path opened during a full collection and assert the secret is absent.

        Deliberately not a substring search of the source: the filename appears in this
        module's own docstrings, so a text scan fails in both directions.  This watches
        the behaviour instead.
        """
        opened = []
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            (state / "notification-secrets.json").write_text('{"ntfy":{"topic":"minerva-SECRET"}}')
            (state / "last-tick.json").write_text(json.dumps({"at_utc": "2026-08-30T05:31:14Z"}))
            (state / "agent-sessions-v2.json").write_text(json.dumps({"sessions": {}}))

            # Patch io.open, not builtins.open: Path.read_text() reaches the filesystem
            # through io.open, so patching builtins records nothing (the control arm
            # below is what caught that).
            import io as io_module
            original = io_module.open

            def recording_open(file, *args, **kwargs):
                opened.append(str(file))
                return original(file, *args, **kwargs)

            io_module.open = recording_open
            try:
                runner = FakeRunner().add("squeue", 0, "")
                dc.collect_ticker(state, runner, FrozenClock(NOW))
                dc.collect_agents(state, FrozenClock(NOW))
            finally:
                io_module.open = original

        self.assertTrue(opened, "control: the collection did open some files")
        self.assertFalse(
            [path for path in opened if "notification-secrets" in path],
            f"the collector opened the secrets file; opened={opened}",
        )

    def test_agent_records_carry_no_prompt_or_transcript_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            (state / "agent-sessions-v2.json").write_text(json.dumps({
                "sessions": {"s1": {"provider": "claude", "profile": "p", "cwd": "/x",
                                    "updated_at": "2026-08-30T05:00:00+00:00",
                                    "turns": [{"action": "send", "returncode": 0,
                                               "stdout": "/secret/path.json"}]}}}))
            agents, source = dc.collect_agents(state, FrozenClock(NOW))
            self.assertTrue(source.ok)
            self.assertNotIn("stdout", json.dumps(agents))
            self.assertEqual(agents[0]["turns"], 1)


class ScrontabTest(unittest.TestCase):
    def test_markers_differ_from_wakerctls_so_install_cron_preserves_them(self):
        import wakerctl
        self.assertNotEqual(dc.SCRON_BEGIN, wakerctl.SCRON_BEGIN)
        self.assertEqual(wakerctl.strip_managed_block([dc.SCRON_BEGIN, "x", dc.SCRON_END]),
                         [dc.SCRON_BEGIN, "x", dc.SCRON_END])

    def test_walltime_is_within_the_cron_qos_cap(self):
        args = type("A", (), {"out": None, "interval_minutes": 5})()
        block = dc.scrontab_block(args, Path("/tmp/state"))
        wall = next(line for line in block if line.startswith("#SCRON -t"))
        self.assertLess(dc.parse_duration(wall.split()[-1]), 86400)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class AlertTest(unittest.TestCase):
    def status(self, **overrides):
        base = {
            "sources": [{"name": "waker_tick", "ok": True}, {"name": "slurm_queue", "ok": True}],
            "ticker": {"receipt": {"age_seconds": 12.0}},
            "jobs": [{"job_id": "57727774", "overall": "ACTIVE"}],
            "coverage": {"nodes_total": 40, "nodes_measured": 31},
        }
        base.update(overrides)
        return base

    def test_a_healthy_snapshot_alerts_about_nothing(self):
        self.assertEqual(dc.alert_conditions(self.status()), [])

    def test_a_partial_but_normal_sweep_does_not_alert(self):
        # 31/40 is this cluster's steady state; alerting on it would train him to ignore.
        self.assertEqual(dc.alert_conditions(self.status()), [])

    def test_a_stale_ticker_alerts(self):
        conditions = dc.alert_conditions(self.status(ticker={"receipt": {"age_seconds": 4000.0}}))
        self.assertTrue(any(c.startswith("ticker-stale") for c, _ in conditions))

    def test_an_unreadable_receipt_alerts_as_unknown_not_as_stale(self):
        conditions = dc.alert_conditions(self.status(
            sources=[{"name": "waker_tick", "ok": False}], ticker={"receipt": None}))
        self.assertIn("ticker-unreadable", [c for c, _ in conditions])

    def test_an_errored_job_alerts_and_names_it(self):
        conditions = dc.alert_conditions(
            self.status(jobs=[{"job_id": "57727775", "overall": "ERROR"}]))
        subject = next(s for c, s in conditions if c.startswith("job-error"))
        self.assertIn("57727775", subject)

    def test_collapsed_coverage_alerts(self):
        conditions = dc.alert_conditions(
            self.status(coverage={"nodes_total": 40, "nodes_measured": 12}))
        self.assertIn("coverage-low", [c for c, _ in conditions])

    def test_no_subject_leaks_a_path_or_a_secret(self):
        # The ntfy topic is a bearer URL and the channel sends the SUBJECT only.
        for status in (
            self.status(ticker={"receipt": None}, sources=[{"name": "waker_tick", "ok": False}]),
            self.status(jobs=[{"job_id": "1", "overall": "ERROR"}]),
            self.status(coverage={"nodes_total": 40, "nodes_measured": 3}),
        ):
            for _, subject in dc.alert_conditions(status):
                # A path segment, not any slash: "3/40" is a fraction and is fine.
                self.assertIsNone(re.search(r"/[A-Za-z._~-]", subject), subject)
                self.assertNotIn("secret", subject.lower())
                self.assertNotIn("pscratch", subject)
                self.assertNotIn("global", subject)

    def test_the_dedupe_key_rebuckets_so_alerts_recur_but_do_not_spam(self):
        status = self.status(ticker={"receipt": None},
                             sources=[{"name": "waker_tick", "ok": False}])
        first = dc.send_alerts(status, Path("/tmp"), window_seconds=3600,
                               dry_run=True, clock=FrozenClock(NOW))
        same = dc.send_alerts(status, Path("/tmp"), window_seconds=3600,
                              dry_run=True, clock=FrozenClock(NOW + 60))
        later = dc.send_alerts(status, Path("/tmp"), window_seconds=3600,
                               dry_run=True, clock=FrozenClock(NOW + 7200))
        self.assertEqual(first, same)          # same window -> same key -> deduped
        self.assertNotEqual(first, later)      # next window -> new key -> re-alerts


class RedactionTest(unittest.TestCase):
    def test_an_absolute_path_is_shortened(self):
        self.assertEqual(
            dc.redact_paths("out=/global/cfs/cdirs/m3246/www/mnv-status/status.json"),
            "out=.../status.json")

    def test_a_checkout_root_does_not_leak_the_account_name(self):
        # Regression: keeping the last TWO segments left ".../josephrb/MINERvA-OmniFold",
        # because the account name is the second-to-last segment of a checkout root.
        self.assertEqual(
            dc.redact_paths("/pscratch/sd/j/josephrb/MINERvA-OmniFold"),
            ".../MINERvA-OmniFold")

    def test_the_account_name_does_not_survive(self):
        # The whole point: portal.nersc.gov serves this to the open internet.
        redacted = dc.redact_paths({"name": "WAKER_STATE_DIR=/pscratch/sd/j/josephrb/"
                                            "MINERvA-OmniFold/docs/orchestration/state/waker"})
        self.assertNotIn("josephrb", json.dumps(redacted))

    def test_nested_structures_are_walked(self):
        redacted = dc.redact_paths(
            {"a": [{"b": "/global/homes/j/josephrb/secretish/file.log"}], "n": 3})
        self.assertNotIn("josephrb", json.dumps(redacted))
        self.assertEqual(redacted["n"], 3)

    def test_a_fraction_or_plain_text_is_untouched(self):
        self.assertEqual(dc.redact_paths("31/40 nodes"), "31/40 nodes")
        self.assertEqual(dc.redact_paths("blocked on Priority"), "blocked on Priority")

    def test_node_names_and_job_ids_survive_redaction(self):
        # Redaction must not eat the fields the dashboard exists to show.
        kept = dc.redact_paths({"node": "login32", "job_id": "57727774", "reason": "Priority"})
        self.assertEqual(kept, {"node": "login32", "job_id": "57727774", "reason": "Priority"})
