import json
import os
from pathlib import Path
import stat
import tempfile
import threading
import time
import types
import unittest

import wakerctl


ROOT_THREAD = "00000000-0000-0000-0000-00000000abcd"


class FakeRunner:
    """Programmable subprocess stand-in recording every call."""

    def __init__(self):
        self.rules = []  # (predicate, returncode, stdout) or (predicate, callable)
        self.calls = []
        self.lock = threading.Lock()

    def add(self, predicate, returncode=0, stdout=""):
        self.rules.append((predicate, returncode, stdout))

    def __call__(self, argv, env=None, cwd=None):
        with self.lock:
            self.calls.append({"argv": list(argv), "env": dict(env) if env else None})
        for predicate, returncode, stdout in self.rules:
            if predicate(argv):
                if callable(returncode):
                    return returncode(argv)
                return types.SimpleNamespace(returncode=returncode, stdout=stdout)
        return types.SimpleNamespace(returncode=0, stdout="")

    def action_calls(self, needle):
        with self.lock:
            return [c for c in self.calls if needle in c["argv"][0]]


class WakerTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="waker-test.")
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.codex = self.dir / "codex"
        self.codex.write_text("#!/bin/bash\nexit 0\n")
        self.codex.chmod(self.codex.stat().st_mode | stat.S_IXUSR)
        self.now = 1_800_000_000.0
        self.config_path = self.dir / "waker-config.json"
        self.write_config()
        self.runner = FakeRunner()

    def write_config(self, **overrides):
        config = {
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
            "claim_lease_seconds": 900,
            "invoke_grace_seconds": 7200,
            "max_retries_default": 2,
        }
        config.update(overrides)
        self.config_path.write_text(json.dumps(config))

    def ctx(self, runner=None):
        return wakerctl.Ctx(
            config_path=self.config_path,
            state_dir=self.dir / "state",
            runner=runner or self.runner,
            clock=lambda: self.now,
        )

    def arm_sentinel(self, ctx, watch_id="w1", path=None, context="ctx-note"):
        path = path or (self.dir / f"{watch_id}.sentinel")
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": watch_id,
                "kind": "file-sentinel",
                "params": {"path": str(path)},
                "action": {"type": "root-resume", "context": context},
            },
        )
        return path


class ClaimPrimitiveTests(WakerTestCase):
    def test_create_exclusive_is_exactly_once(self):
        target = self.dir / "claim"
        results = [wakerctl.create_exclusive(target, "a") for _ in range(3)]
        self.assertEqual(results, [True, False, False])
        self.assertEqual(target.read_text(), "a")

    def test_expired_claim_is_stolen_only_when_guard_allows(self):
        ctx = self.ctx()
        claim = self.dir / "state" / "c.claim"
        claim.parent.mkdir(parents=True)
        claim.write_text(json.dumps({"owner": "x", "acquired_epoch": self.now - 10_000, "lease_seconds": 900}))
        self.assertFalse(wakerctl.acquire_claim(ctx, claim, 900, guard=lambda: False))
        self.assertTrue(wakerctl.acquire_claim(ctx, claim, 900, guard=lambda: True))

    def test_fresh_claim_is_not_stolen(self):
        ctx = self.ctx()
        claim = self.dir / "state" / "c.claim"
        claim.parent.mkdir(parents=True)
        claim.write_text(json.dumps({"owner": "x", "acquired_epoch": self.now - 1, "lease_seconds": 900}))
        self.assertFalse(wakerctl.acquire_claim(ctx, claim, 900, guard=lambda: True))

    def test_event_paths_preserve_dotted_ids(self):
        ctx = self.ctx()
        paths = wakerctl.event_paths(ctx, "evt-x.r1")
        self.assertTrue(str(paths["event"]).endswith("evt-x.r1.json"))
        self.assertTrue(str(paths["claim"]).endswith("evt-x.r1.claim"))


class ConditionTests(WakerTestCase):
    def test_slurm_job_active_then_complete(self):
        ctx = self.ctx()
        self.runner.add(lambda a: a[0] == "squeue", 0, "RUNNING\n")
        self.assertEqual(wakerctl.slurm_job_state(ctx, "77"), ("ACTIVE", ""))
        self.runner.rules.clear()
        self.runner.add(lambda a: a[0] == "squeue", 0, "")
        self.runner.add(lambda a: a[0] == "sacct", 0, "77|COMPLETED|0:0\n")
        self.assertEqual(wakerctl.slurm_job_state(ctx, "77"), ("COMPLETED", "0:0"))

    def test_slurm_job_watch_emits_error_event(self):
        ctx = self.ctx()
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "job77",
                "kind": "slurm-job",
                "params": {"job_id": "77"},
                "action": {"type": "root-resume", "context": ""},
            },
        )
        self.runner.add(lambda a: a[0] == "squeue", 0, "")
        self.runner.add(lambda a: a[0] == "sacct", 0, "77|FAILED|1:0\n")
        emitted = wakerctl.scan(ctx)
        self.assertEqual(emitted, ["evt-job77"])
        event = wakerctl.read_json(wakerctl.event_paths(ctx, "evt-job77")["event"])
        self.assertEqual(event["event_type"], "slurm-job-error")
        self.assertEqual(event["payload"]["state"], "FAILED")

    def test_monitor_error_after_sustained_unreliability(self):
        ctx = self.ctx()
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "job88",
                "kind": "slurm-job",
                "params": {"job_id": "88"},
                "action": {"type": "root-resume", "context": ""},
                "max_unreliable": 3,
            },
        )
        self.runner.add(lambda a: a[0] == "squeue", 0, "")
        self.runner.add(lambda a: a[0] == "sacct", 1, "boom")
        self.assertEqual(wakerctl.scan(ctx), [])
        self.assertEqual(wakerctl.scan(ctx), [])
        self.assertEqual(wakerctl.scan(ctx), ["evt-job88"])
        event = wakerctl.read_json(wakerctl.event_paths(ctx, "evt-job88")["event"])
        self.assertEqual(event["event_type"], "monitor-error")

    def test_queue_latency_fires_once_past_threshold(self):
        ctx = self.ctx()
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "qlat",
                "kind": "queue-latency",
                "params": {"job_id": "99", "threshold_seconds": 3600},
                "action": {"type": "root-resume", "context": ""},
            },
        )
        submit = int(self.now - 100)
        self.runner.add(lambda a: a[0] == "squeue", 0, f"PENDING|{submit}\n")
        self.assertEqual(wakerctl.scan(ctx), [])
        self.now += 4000
        self.assertEqual(wakerctl.scan(ctx), ["evt-qlat"])
        # Watch is now fired; no repeat emission on later scans.
        self.now += 4000
        self.assertEqual(wakerctl.scan(ctx), [])

    def test_queue_latency_ignores_running_job(self):
        ctx = self.ctx()
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "qrun",
                "kind": "queue-latency",
                "params": {"job_id": "99", "threshold_seconds": 1},
                "action": {"type": "root-resume", "context": ""},
            },
        )
        self.runner.add(lambda a: a[0] == "squeue", 0, f"RUNNING|{int(self.now - 999)}\n")
        self.assertEqual(wakerctl.scan(ctx), [])

    def test_deadline_provider_reset_and_heartbeat(self):
        ctx = self.ctx()
        import datetime as dt

        at = (
            dt.datetime.fromtimestamp(self.now + 5000, tz=dt.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        )
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "reset-school",
                "kind": "provider-reset",
                "params": {"at_utc": at, "account": "codex-school"},
                "action": {"type": "root-resume", "context": ""},
            },
        )
        beat = self.dir / "beat"
        beat.write_text("x")
        os.utime(beat, (self.now - 50, self.now - 50))
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "beat",
                "kind": "heartbeat",
                "params": {"path": str(beat), "max_age_seconds": 600},
                "action": {"type": "root-resume", "context": ""},
            },
        )
        self.assertEqual(wakerctl.scan(ctx), [])
        self.now = wakerctl.parse_utc(at) + 1
        emitted = wakerctl.scan(ctx)
        self.assertIn("evt-reset-school", emitted)
        self.assertIn("evt-beat", emitted)  # heartbeat now stale as well
        event = wakerctl.read_json(wakerctl.event_paths(ctx, "evt-reset-school")["event"])
        self.assertEqual(event["payload"]["account"], "codex-school")

    def test_sentinel_with_content_gate(self):
        ctx = self.ctx()
        sentinel = self.dir / "s"
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "sent",
                "kind": "file-sentinel",
                "params": {"path": str(sentinel), "must_contain": "rc=0"},
                "action": {"type": "root-resume", "context": ""},
            },
        )
        self.assertEqual(wakerctl.scan(ctx), [])
        sentinel.write_text("rc=1\n")
        self.assertEqual(wakerctl.scan(ctx), [])
        sentinel.write_text("loop rc=0\n")
        self.assertEqual(wakerctl.scan(ctx), ["evt-sent"])


class DispatchTests(WakerTestCase):
    def fire_sentinel(self, ctx, watch_id="w1"):
        path = self.arm_sentinel(ctx, watch_id)
        path.write_text("done\n")
        return wakerctl.scan(ctx)

    def test_completion_causes_exactly_one_resume_with_correct_env(self):
        ctx = self.ctx()
        self.fire_sentinel(ctx)
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-w1", "resumed")])
        calls = self.runner.action_calls("codex")
        self.assertEqual(len(calls), 1)
        argv, env = calls[0]["argv"], calls[0]["env"]
        self.assertEqual(argv[:3], [str(self.codex), "exec", "resume"])
        self.assertIn(ROOT_THREAD, argv)
        self.assertIn("--disable", argv)
        self.assertIn("goals", argv)
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", argv)
        self.assertIn("--model", argv)
        self.assertTrue(env["CODEX_HOME"].endswith("codex-homes/personal"))
        prompt = argv[-1]
        self.assertIn("evt-w1", prompt)
        self.assertIn("ctx-note", prompt)
        self.assertIn("next dependency-ready campaign action", prompt)
        # Second dispatch performs nothing further.
        self.assertEqual(wakerctl.dispatch(ctx), [])
        self.assertEqual(len(self.runner.action_calls("codex")), 1)

    def test_quiet_interval_makes_zero_provider_calls(self):
        ctx = self.ctx()
        self.arm_sentinel(ctx, "quiet")
        for _ in range(25):
            wakerctl.tick(ctx)
            self.now += 60
        self.assertEqual(self.runner.action_calls("codex"), [])
        self.assertEqual(self.runner.action_calls("claude"), [])
        self.assertEqual(self.runner.action_calls("agy"), [])

    def test_duplicate_producers_yield_single_event_and_single_resume(self):
        ctx_a, ctx_b = self.ctx(), self.ctx()
        path = self.arm_sentinel(ctx_a, "dup")
        path.write_text("done\n")
        wakerctl.scan(ctx_a)
        # Second producer re-arms its own view and scans concurrently; the
        # event id is deterministic so the second emission must collide.
        watch = wakerctl.read_json(wakerctl.watch_path(ctx_b, "dup"))
        watch["state"] = "armed"
        wakerctl.save_watch(ctx_b, watch)
        wakerctl.scan(ctx_b)
        events = list((self.dir / "state" / "events").glob("evt-dup*.json"))
        self.assertEqual(len(events), 1)
        wakerctl.dispatch(ctx_a)
        wakerctl.dispatch(ctx_b)
        self.assertEqual(len(self.runner.action_calls("codex")), 1)

    def test_concurrent_dispatchers_one_invocation(self):
        contexts = []
        for _ in range(8):
            runner = FakeRunner()
            runner.add(lambda a: "codex" in a[0], lambda a: (time.sleep(0.05), types.SimpleNamespace(returncode=0, stdout=""))[1])
            contexts.append(self.ctx(runner=runner))
        path = self.arm_sentinel(contexts[0], "race")
        path.write_text("done\n")
        wakerctl.scan(contexts[0])
        threads = [threading.Thread(target=wakerctl.dispatch, args=(c,)) for c in contexts]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        total = sum(len(c.runner.action_calls("codex")) for c in contexts)
        self.assertEqual(total, 1)

    def test_controller_restart_reclaims_expired_claim(self):
        ctx = self.ctx()
        self.fire_sentinel(ctx, "restart")
        paths = wakerctl.event_paths(ctx, "evt-restart")
        # Simulate a controller that claimed and died before invoking.
        paths["claim"].parent.mkdir(parents=True, exist_ok=True)
        paths["claim"].write_text(
            json.dumps({"owner": "dead:1", "acquired_epoch": self.now - 10_000, "lease_seconds": 900})
        )
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-restart", "resumed")])
        self.assertEqual(len(self.runner.action_calls("codex")), 1)

    def test_fresh_foreign_claim_is_respected(self):
        ctx = self.ctx()
        self.fire_sentinel(ctx, "held")
        paths = wakerctl.event_paths(ctx, "evt-held")
        paths["claim"].write_text(
            json.dumps({"owner": "other:2", "acquired_epoch": self.now - 1, "lease_seconds": 900})
        )
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-held", "claim-held")])
        self.assertEqual(self.runner.action_calls("codex"), [])

    def test_stale_resume_mutex_is_taken_over(self):
        ctx = self.ctx()
        self.fire_sentinel(ctx, "mutex")
        ctx.resume_mutex.parent.mkdir(parents=True, exist_ok=True)
        ctx.resume_mutex.write_text(
            json.dumps({"owner": "dead:3", "acquired_epoch": self.now - 10_000, "lease_seconds": 900})
        )
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-mutex", "resumed")])
        self.assertFalse(ctx.resume_mutex.exists())

    def test_fresh_resume_mutex_defers_and_releases_event_claim(self):
        ctx = self.ctx()
        self.fire_sentinel(ctx, "busy")
        ctx.resume_mutex.parent.mkdir(parents=True, exist_ok=True)
        ctx.resume_mutex.write_text(
            json.dumps({"owner": "other:4", "acquired_epoch": self.now - 1, "lease_seconds": 900})
        )
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-busy", "mutex-held")])
        self.assertFalse(wakerctl.event_paths(ctx, "evt-busy")["claim"].exists())
        os.unlink(ctx.resume_mutex)
        self.assertEqual(wakerctl.dispatch(ctx), [("evt-busy", "resumed")])

    def test_resume_failure_retries_bounded(self):
        ctx = self.ctx()
        self.runner.add(lambda a: "codex" in a[0], 1, "transient provider failure")
        self.fire_sentinel(ctx, "flaky")
        for _ in range(6):
            wakerctl.dispatch(ctx)
        calls = self.runner.action_calls("codex")
        self.assertEqual(len(calls), 3)  # original + r1 + r2, then exhausted
        ledger = (self.dir / "state" / "LEDGER.tsv").read_text()
        self.assertIn("retries-exhausted", ledger)
        for event_id in ("evt-flaky", "evt-flaky.r1", "evt-flaky.r2"):
            done = wakerctl.read_json(wakerctl.event_paths(ctx, event_id)["done"])
            self.assertEqual(done["outcome"], "failed")

    def test_retry_succeeds_after_transient_failure(self):
        ctx = self.ctx()
        state = {"first": True}

        def flaky(argv):
            if state["first"]:
                state["first"] = False
                return types.SimpleNamespace(returncode=1, stdout="cap")
            return types.SimpleNamespace(returncode=0, stdout="ok")

        self.runner.add(lambda a: "codex" in a[0], flaky)
        self.fire_sentinel(ctx, "recover")
        wakerctl.dispatch(ctx)
        outcomes = wakerctl.dispatch(ctx)
        self.assertIn(("evt-recover.r1", "resumed"), outcomes)
        self.assertEqual(len(self.runner.action_calls("codex")), 2)
        self.assertEqual(wakerctl.dispatch(ctx), [])

    def test_invoked_without_done_emits_one_reconciliation(self):
        ctx = self.ctx()
        self.fire_sentinel(ctx, "lost")
        paths = wakerctl.event_paths(ctx, "evt-lost")
        wakerctl.create_exclusive(paths["invoked"], "{}")
        stale = self.now - 8000
        os.utime(paths["invoked"], (stale, stale))
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes[0], ("evt-lost", "recon-emitted"))
        recon = wakerctl.read_json(wakerctl.event_paths(ctx, "evt-lost.recon")["event"])
        self.assertEqual(recon["event_type"], "resume-outcome-unknown")
        self.assertEqual(recon["recon_of"], "evt-lost")
        original_done = wakerctl.read_json(paths["done"])
        self.assertEqual(original_done["outcome"], "reconciled")
        # Next pass dispatches only the recon event; the original never reruns.
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-lost.recon", "resumed")])
        calls = self.runner.action_calls("codex")
        self.assertEqual(len(calls), 1)
        self.assertIn("reconciliation event", calls[0]["argv"][-1])
        self.assertEqual(wakerctl.dispatch(ctx), [])

    def test_missing_binary_blocks_without_consuming_event(self):
        self.write_config(codex_bin=str(self.dir / "missing-codex"))
        ctx = self.ctx()
        self.fire_sentinel(ctx, "blocked")
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-blocked", "blocked")])
        self.assertEqual(self.runner.action_calls("codex"), [])
        paths = wakerctl.event_paths(ctx, "evt-blocked")
        self.assertTrue(paths["blocked"].exists())
        self.assertFalse(paths["invoked"].exists())
        self.assertFalse(paths["claim"].exists())
        # Repair the environment; the same event now dispatches exactly once.
        self.write_config(codex_bin=str(self.codex))
        repaired = self.ctx()
        outcomes = wakerctl.dispatch(repaired)
        self.assertEqual(outcomes, [("evt-blocked", "resumed")])
        self.assertFalse(paths["blocked"].exists())
        self.assertEqual(len(self.runner.action_calls("codex")), 1)

    def test_role_send_action_routes_through_agentctl(self):
        ctx = self.ctx()
        prompt = self.dir / "p.md"
        prompt.write_text("hello")
        sentinel = self.dir / "role.sentinel"
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "role",
                "kind": "file-sentinel",
                "params": {"path": str(sentinel)},
                "action": {
                    "type": "role-send",
                    "role": "agent-B-p5b",
                    "prompt_file": str(prompt),
                    "context": "",
                },
            },
        )
        sentinel.write_text("x")
        wakerctl.scan(ctx)
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-role", "resumed")])
        call = self.runner.calls[-1]
        self.assertIn("agentctl.py", call["argv"][1])
        self.assertIn("agent-B-p5b", call["argv"])

    def test_command_action_must_stay_inside_repo(self):
        ctx = self.ctx()
        with self.assertRaises(wakerctl.WakerError):
            wakerctl.add_watch(
                ctx,
                {
                    "watch_id": "esc",
                    "kind": "file-sentinel",
                    "params": {"path": str(self.dir / "x")},
                    "action": {"type": "command", "argv": ["/usr/bin/true"]},
                },
            )

    def test_manual_emit_is_idempotent(self):
        ctx = self.ctx()
        first = wakerctl.emit_event(ctx, "evt-manual", "manual", "manual", {})
        second = wakerctl.emit_event(ctx, "evt-manual", "manual", "manual", {})
        self.assertTrue(first)
        self.assertFalse(second)


class IdleGuardTests(WakerTestCase):
    def write_config(self, **overrides):
        overrides.setdefault("idle_guard_ticks", 3)
        super().write_config(**overrides)

    def test_idle_guard_fires_once_per_episode_and_resumes(self):
        ctx = self.ctx()
        for _ in range(2):
            self.assertEqual(wakerctl.tick(ctx)["emitted"], [])
        result = wakerctl.tick(ctx)
        self.assertEqual(len(result["emitted"]), 1)
        idle_id = result["emitted"][0]
        self.assertTrue(idle_id.startswith("evt-idle-"))
        # The idle event dispatches on the next tick; the guard must not
        # re-fire while it is pending or after it is done.
        for _ in range(6):
            wakerctl.tick(ctx)
            self.now += 60
        calls = self.runner.action_calls("codex")
        self.assertEqual(len(calls), 1)
        self.assertIn("ended without continuation", calls[0]["argv"][-1])
        idle_events = [e for e in (self.dir / "state" / "events").glob("evt-idle-*.json")]
        self.assertEqual(len(idle_events), 1)

    def test_idle_guard_respects_blocked_on_user_and_delete_reenables(self):
        ctx = self.ctx()
        blocked = wakerctl.blocked_on_user_path(ctx)
        blocked.parent.mkdir(parents=True, exist_ok=True)
        blocked.write_text(json.dumps({"decision_needed": "authorize Gate 3"}))
        for _ in range(8):
            self.assertEqual(wakerctl.tick(ctx)["emitted"], [])
        self.assertEqual(self.runner.action_calls("codex"), [])
        # The user answers and deletes the declaration: the guard wakes the
        # campaign within threshold ticks.
        os.unlink(blocked)
        emitted = []
        for _ in range(4):
            emitted += wakerctl.tick(ctx)["emitted"]
            self.now += 1
        self.assertEqual(len(emitted), 1)

    def test_idle_guard_resets_when_a_watch_is_armed(self):
        ctx = self.ctx()
        for _ in range(2):
            wakerctl.tick(ctx)
        self.arm_sentinel(ctx, "revive")
        self.assertEqual(wakerctl.tick(ctx)["emitted"], [])
        state = wakerctl.read_json(self.dir / "state" / "idle-state.json")
        self.assertEqual(state, {"idle_ticks": 0, "fired_event": None})

    def test_idle_guard_disabled_by_config(self):
        self.write_config(idle_guard_ticks=0)
        ctx = self.ctx()
        for _ in range(10):
            self.assertEqual(wakerctl.tick(ctx)["emitted"], [])


class SigtermTests(WakerTestCase):
    def test_sigterm_during_action_records_failure_and_retry(self):
        ctx = self.ctx()

        def slow_action(argv):
            threading.Timer(0.2, os.kill, args=(os.getpid(), 15)).start()
            time.sleep(5)
            return types.SimpleNamespace(returncode=0, stdout="late")

        self.runner.add(lambda a: "codex" in a[0], slow_action)
        path = self.arm_sentinel(ctx, "walled")
        path.write_text("x")
        wakerctl.scan(ctx)
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-walled", "failed")])
        done = wakerctl.read_json(wakerctl.event_paths(ctx, "evt-walled")["done"])
        self.assertEqual(done["rc"], 143)
        self.assertTrue(wakerctl.event_paths(ctx, "evt-walled.r1")["event"].exists())
        ledger = (self.dir / "state" / "LEDGER.tsv").read_text()
        self.assertIn("action-terminated", ledger)


class StatusAndCronTests(WakerTestCase):
    def test_status_reports_states_cross_node_readably(self):
        ctx = self.ctx()
        path = self.arm_sentinel(ctx, "st")
        path.write_text("x")
        wakerctl.tick(ctx)
        report = wakerctl.status(ctx)
        self.assertEqual(report["watches"][0]["state"], "fired")
        self.assertEqual(report["events"][0]["state"], "resumed")
        self.assertIsNotNone(report["last_tick"])

    def test_scrontab_managed_block_roundtrip(self):
        ctx = self.ctx()
        existing = ["# user entry", "0 1 * * * /bin/true"]
        lines = existing + wakerctl.scrontab_lines(ctx, 5)
        self.assertEqual(wakerctl.strip_managed_block(lines), existing)
        block = wakerctl.scrontab_lines(ctx, 5)
        self.assertIn("#SCRON -q cron", block)
        self.assertIn("#SCRON -t 12:00:00", block)  # wall must outlive a resume turn
        self.assertTrue(any("wakerctl.py tick --quiet" in line for line in block))

    def test_install_cron_writes_table_through_scrontab(self):
        captured = {}

        def scrontab_rule(argv):
            if argv[0] == "scrontab" and len(argv) == 2 and argv[1] != "-l":
                captured["table"] = Path(argv[1]).read_text()
            return types.SimpleNamespace(returncode=0, stdout="")

        self.runner.add(lambda a: a[0] == "scrontab", scrontab_rule)
        ctx = self.ctx()
        wakerctl.install_cron(ctx, 7)
        self.assertIn("*/7 * * * *", captured["table"])
        self.assertIn(wakerctl.SCRON_BEGIN, captured["table"])

    def test_ledger_records_full_lifecycle(self):
        ctx = self.ctx()
        path = self.arm_sentinel(ctx, "led")
        path.write_text("x")
        wakerctl.tick(ctx)
        rows = [line.split("\t") for line in (self.dir / "state" / "LEDGER.tsv").read_text().splitlines()]
        transitions = [row[2] for row in rows if row[1] == "evt-led"]
        self.assertEqual(transitions, ["watch-armed", "event-emitted", "invoked", "done"])
        for row in rows:
            self.assertEqual(len(row), 5)  # ts, id, transition, owner, detail


if __name__ == "__main__":
    unittest.main()
