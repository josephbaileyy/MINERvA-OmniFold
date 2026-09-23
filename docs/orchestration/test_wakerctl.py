import contextlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest import mock

import test_wakerctl_preflight_watch_health as health
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

    def __call__(self, argv, env=None, cwd=None, input_text=None):
        with self.lock:
            self.calls.append(
                {
                    "argv": list(argv),
                    "env": dict(env) if env else None,
                    "cwd": Path(cwd).resolve() if cwd else None,
                    "input": input_text,
                }
            )
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
            # OFF here only: these fixtures have no scrontab or squeue, so the tick's
            # report-only control-plane checks would add a notice to every notify count.
            # They run ON (the production default) in ControlPlaneTickTests and in
            # test_wakerctl_preflight_watch_health.TickControlPlaneWiring.
            "tick_control_plane_checks": False,
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

    def write_registry(
        self,
        *,
        role="agent-B-p5b",
        profile="codex-personal",
        session_id="session-agent-b",
    ):
        registry = self.dir / "sessions.json"
        wakerctl.agentctl.atomic_write_json(
            registry,
            {
                "version": 1,
                "sessions": {
                    role: {
                        "provider": profile.split("-", 1)[0],
                        "profile": profile,
                        "session_id": session_id,
                        "cwd": str(self.dir),
                        "turns": [],
                    }
                },
            },
        )
        return registry


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

    def test_slurm_job_dependency_never_satisfied_is_terminal(self):
        ctx = self.ctx()
        self.runner.add(
            lambda a: a[0] == "squeue",
            0,
            "PENDING|DependencyNeverSatisfied\n",
        )
        self.assertEqual(
            wakerctl.slurm_job_state(ctx, "77"),
            ("DEPENDENCY_NEVER_SATISFIED", "N/A"),
        )
        self.assertFalse(any(call["argv"][0] == "sacct" for call in self.runner.calls))

    def test_slurm_job_ordinary_pending_reason_stays_active(self):
        ctx = self.ctx()
        self.runner.add(lambda a: a[0] == "squeue", 0, "PENDING|Resources\n")
        self.assertEqual(wakerctl.slurm_job_state(ctx, "77"), ("ACTIVE", ""))

    def test_slurm_job_mixed_visible_rows_stay_active(self):
        ctx = self.ctx()
        self.runner.add(
            lambda a: a[0] == "squeue",
            0,
            "PENDING|DependencyNeverSatisfied\nRUNNING|None\n",
        )
        self.assertEqual(wakerctl.slurm_job_state(ctx, "77"), ("ACTIVE", ""))

    def test_slurm_job_dependency_never_satisfied_emits_error_event(self):
        ctx = self.ctx()
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "job77-dead-dependency",
                "kind": "slurm-job",
                "params": {"job_id": "77"},
                "action": {"type": "root-resume", "context": ""},
            },
        )
        self.runner.add(
            lambda a: a[0] == "squeue",
            0,
            "PENDING|DependencyNeverSatisfied\n",
        )
        emitted = wakerctl.scan(ctx)
        self.assertEqual(emitted, ["evt-job77-dead-dependency"])
        event = wakerctl.read_json(
            wakerctl.event_paths(ctx, "evt-job77-dead-dependency")["event"]
        )
        self.assertEqual(event["event_type"], "slurm-job-error")
        self.assertEqual(event["payload"]["state"], "DEPENDENCY_NEVER_SATISFIED")
        self.assertEqual(event["payload"]["exit_code"], "N/A")

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
        self.runner.add(lambda a: a[0] == "sacct", 0, "99|PENDING|Unknown\n")
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
        self.assertEqual(wakerctl.read_json(ctx.watches_dir / "qrun.json")["state"], "disarmed")

    def test_queue_latency_array_with_completed_element_auto_disarms(self):
        ctx = self.ctx()
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "qarray",
                "kind": "queue-latency",
                "params": {"job_id": "99", "threshold_seconds": 1},
                "action": {"type": "root-resume", "context": ""},
            },
        )
        submit = int(self.now - 999)
        self.runner.add(lambda a: a[0] == "squeue", 0, f"PENDING|{submit}\n")
        self.runner.add(
            lambda a: a[0] == "sacct",
            0,
            "99|PENDING|Unknown\n1001|COMPLETED|2026-07-20T06:05:01\n",
        )
        self.assertEqual(wakerctl.scan(ctx), [])
        saved = wakerctl.read_json(ctx.watches_dir / "qarray.json")
        self.assertEqual(saved["state"], "disarmed")
        self.assertIn("1001 state=COMPLETED", saved["disarm_reason"])

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
        event = wakerctl.read_json(wakerctl.event_paths(ctx, "evt-w1")["event"])
        self.assertEqual(event["action"]["type"], "root-resume")
        self.assertEqual(event["context"], "ctx-note")
        self.assertFalse(wakerctl.watch_path(ctx, "w1").exists())
        self.assertTrue(wakerctl.archived_watch_path(ctx, "w1").exists())
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

    def test_retry_keeps_event_action_after_live_watch_is_archived(self):
        ctx = self.ctx()
        state = {"first": True}

        def flaky(argv):
            if state["first"]:
                state["first"] = False
                return types.SimpleNamespace(returncode=1, stdout="first failed")
            return types.SimpleNamespace(returncode=0, stdout="second passed")

        self.runner.add(lambda a: "codex" in a[0], flaky)
        self.fire_sentinel(ctx, "snapshot-retry")
        self.assertEqual(wakerctl.dispatch(ctx), [("evt-snapshot-retry", "failed")])
        self.assertFalse(wakerctl.watch_path(ctx, "snapshot-retry").exists())
        retry = wakerctl.read_json(
            wakerctl.event_paths(ctx, "evt-snapshot-retry.r1")["event"]
        )
        self.assertEqual(retry["action"]["type"], "root-resume")
        self.assertEqual(retry["context"], "ctx-note")
        self.assertEqual(
            wakerctl.dispatch(ctx), [("evt-snapshot-retry.r1", "resumed")]
        )

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
        self.write_config(python=sys.executable)
        ctx = self.ctx()
        registry = self.write_registry()
        self.runner.add(
            lambda a: len(a) > 1 and "usagectl.py" in a[1],
            0,
            '{"profile":"codex-personal","state":"READY"}',
        )
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
                    "registry": str(registry),
                    "prompt_file": str(prompt),
                    "context": "",
                },
            },
        )
        sentinel.write_text("x")
        wakerctl.scan(ctx)
        with mock.patch.object(wakerctl, "preflight", return_value=[]):
            outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-role", "resumed")])
        call = self.runner.calls[-1]
        self.assertIn("agentctl.py", call["argv"][1])
        self.assertIn("agent-B-p5b", call["argv"])
        self.assertIn(str(registry.resolve()), call["argv"])
        self.assertIn("session-agent-b", call["argv"])

    def test_provider_capacity_deferral_resumes_exact_session_once(self):
        self.write_config(python=sys.executable, capacity_guard=True)
        ctx = self.ctx()
        registry = self.write_registry(
            role="school-main",
            profile="claude-school",
            session_id="claude-session-1",
        )
        reset_utc = wakerctl.dt.datetime.fromtimestamp(
            self.now + 3600,
            tz=wakerctl.dt.timezone.utc,
        ).isoformat()
        deferred = wakerctl.defer_role(
            ctx,
            watch_id="quota-school-main-1",
            role="school-main",
            registry_path=registry,
            expected_session_id="claude-session-1",
            prompt="continue",
            not_before_utc=reset_utc,
        )
        prompt_path = Path(deferred["prompt_file"])
        self.assertEqual(prompt_path.read_text(), "continue")
        self.assertEqual(stat.S_IMODE(prompt_path.stat().st_mode), 0o600)
        watch = wakerctl.read_json(wakerctl.watch_path(ctx, deferred["watch_id"]))
        self.assertEqual(watch["max_retries"], 0)

        self.now += 3601
        self.runner.add(
            lambda a: len(a) > 1 and "usagectl.py" in a[1],
            3,
            '{"profile":"claude-school","state":"EXHAUSTED"}',
        )
        self.assertEqual(wakerctl.scan(ctx), [])

        self.runner.rules.clear()
        self.runner.add(
            lambda a: len(a) > 1 and "usagectl.py" in a[1],
            0,
            '{"profile":"claude-school","state":"READY"}',
        )
        self.assertEqual(wakerctl.scan(ctx), ["evt-quota-school-main-1"])
        with mock.patch.object(wakerctl, "preflight", return_value=[]):
            self.assertEqual(
                wakerctl.dispatch(ctx),
                [("evt-quota-school-main-1", "resumed")],
            )
            self.assertEqual(wakerctl.dispatch(ctx), [])
        sends = [
            call
            for call in self.runner.calls
            if len(call["argv"]) > 1 and "agentctl.py" in call["argv"][1]
        ]
        self.assertEqual(len(sends), 1)
        self.assertIn(str(registry.resolve()), sends[0]["argv"])
        self.assertIn("claude-session-1", sends[0]["argv"])

    def test_claude_stale_cache_uses_observed_reset_boundary_once(self):
        self.write_config(python=sys.executable, capacity_guard=True)
        ctx = self.ctx()
        registry = self.write_registry(
            role="school-main",
            profile="claude-school",
            session_id="claude-session-1",
        )
        reset_utc = wakerctl.dt.datetime.fromtimestamp(
            self.now + 60,
            tz=wakerctl.dt.timezone.utc,
        ).isoformat()
        wakerctl.defer_role(
            ctx,
            watch_id="quota-school-main-stale",
            role="school-main",
            registry_path=registry,
            expected_session_id="claude-session-1",
            prompt="continue",
            not_before_utc=reset_utc,
        )
        self.runner.add(
            lambda a: len(a) > 1 and "usagectl.py" in a[1],
            3,
            '{"profile":"claude-school","state":"UNKNOWN"}',
        )
        self.assertEqual(wakerctl.scan(ctx), [])
        usage_calls = [
            call
            for call in self.runner.calls
            if len(call["argv"]) > 1 and "usagectl.py" in call["argv"][1]
        ]
        self.assertEqual(usage_calls, [])

        self.now += 61
        self.assertEqual(wakerctl.scan(ctx), ["evt-quota-school-main-stale"])
        event = wakerctl.read_json(
            wakerctl.event_paths(ctx, "evt-quota-school-main-stale")["event"]
        )
        self.assertEqual(event["payload"]["state"], "RESET_BOUNDARY_REACHED")
        with mock.patch.object(wakerctl, "preflight", return_value=[]):
            self.assertEqual(
                wakerctl.dispatch(ctx),
                [("evt-quota-school-main-stale", "resumed")],
            )
            self.assertEqual(wakerctl.dispatch(ctx), [])
        sends = [
            call
            for call in self.runner.calls
            if len(call["argv"]) > 1 and "agentctl.py" in call["argv"][1]
        ]
        self.assertEqual(len(sends), 1)

    def test_root_limit_defers_exact_thread_until_observed_reset(self):
        claude = self.dir / "claude"
        claude.write_text("#!/bin/bash\nexit 0\n")
        claude.chmod(claude.stat().st_mode | stat.S_IXUSR)
        self.write_config(
            python=sys.executable,
            capacity_guard=True,
            claude_bin=str(claude),
            root={
                "provider": "claude",
                "profile": "claude-school",
                "thread_id": "claude-root-session",
                "cwd": str(self.dir),
            },
        )
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, "root-quota")
        sentinel.write_text("done")
        self.assertEqual(wakerctl.scan(ctx), ["evt-root-quota"])
        reset_utc = wakerctl.dt.datetime.fromtimestamp(
            self.now + 60,
            tz=wakerctl.dt.timezone.utc,
        ).isoformat()
        capacity_calls = 0

        def capacity_result(_argv):
            nonlocal capacity_calls
            capacity_calls += 1
            if capacity_calls == 1:
                state = {"profile": "claude-school", "state": "READY"}
                return types.SimpleNamespace(returncode=0, stdout=json.dumps(state))
            if capacity_calls == 2:
                state = {
                    "profile": "claude-school",
                    "state": "EXHAUSTED",
                    "next_reset_utc": reset_utc,
                }
                return types.SimpleNamespace(returncode=3, stdout=json.dumps(state))
            state = {"profile": "claude-school", "state": "UNKNOWN"}
            return types.SimpleNamespace(returncode=3, stdout=json.dumps(state))

        provider_calls = 0

        def provider_result(_argv):
            nonlocal provider_calls
            provider_calls += 1
            if provider_calls == 1:
                payload = {
                    "is_error": True,
                    "result": "You've hit your usage limit. Try again at 8:44 AM.",
                }
            else:
                payload = {"is_error": False, "result": "continued"}
            return types.SimpleNamespace(returncode=0, stdout=json.dumps(payload))

        self.runner.add(
            lambda a: len(a) > 1 and "usagectl.py" in a[1],
            capacity_result,
        )
        self.runner.add(lambda a: a[0] == str(claude), provider_result)
        with mock.patch.object(wakerctl, "preflight", return_value=[]):
            self.assertEqual(
                wakerctl.dispatch(ctx),
                [("evt-root-quota", "deferred")],
            )
        watch_id = "quota-root-evt-root-quota"
        watch = wakerctl.read_json(wakerctl.watch_path(ctx, watch_id))
        self.assertEqual(watch["action"]["expected_thread_id"], "claude-root-session")
        self.assertEqual(watch["max_retries"], 0)

        self.now += 61
        self.assertEqual(wakerctl.scan(ctx), [f"evt-{watch_id}"])
        with mock.patch.object(wakerctl, "preflight", return_value=[]):
            self.assertEqual(
                wakerctl.dispatch(ctx),
                [(f"evt-{watch_id}", "resumed")],
            )
            self.assertEqual(wakerctl.dispatch(ctx), [])
        self.assertEqual(provider_calls, 2)

    def test_root_remap_blocks_deferred_event_without_invocation(self):
        self.write_config(
            python=sys.executable,
            capacity_guard=True,
            root={
                "provider": "claude",
                "profile": "claude-school",
                "thread_id": "claude-root-session",
                "cwd": str(self.dir),
            },
        )
        ctx = self.ctx()
        reset_utc = wakerctl.dt.datetime.fromtimestamp(
            self.now + 60,
            tz=wakerctl.dt.timezone.utc,
        ).isoformat()
        event = {"event_id": "evt-root-remap"}
        wakerctl.defer_root(
            ctx,
            event,
            {
                "state": "EXHAUSTED",
                "next_reset_utc": reset_utc,
            },
        )
        ctx.config["root"]["thread_id"] = "replacement-root-session"
        self.now += 61
        self.runner.add(
            lambda a: len(a) > 1 and "usagectl.py" in a[1],
            0,
            '{"profile":"claude-school","state":"READY"}',
        )
        watch_id = "quota-root-evt-root-remap"
        self.assertEqual(wakerctl.scan(ctx), [f"evt-{watch_id}"])
        with mock.patch.object(wakerctl, "preflight", return_value=[]):
            self.assertEqual(
                wakerctl.dispatch(ctx),
                [(f"evt-{watch_id}", "blocked")],
            )
        provider_calls = [
            call
            for call in self.runner.calls
            if call["argv"] and call["argv"][0].endswith("claude")
        ]
        self.assertEqual(provider_calls, [])

    def test_role_remap_blocks_deferred_event_without_invocation(self):
        self.write_config(python=sys.executable, capacity_guard=True)
        ctx = self.ctx()
        registry = self.write_registry(
            role="school-main",
            profile="claude-school",
            session_id="claude-session-1",
        )
        wakerctl.defer_role(
            ctx,
            watch_id="quota-school-main-remap",
            role="school-main",
            registry_path=registry,
            expected_session_id="claude-session-1",
            prompt="continue",
            not_before_utc=wakerctl.dt.datetime.fromtimestamp(
                self.now + 3600,
                tz=wakerctl.dt.timezone.utc,
            ).isoformat(),
        )
        replacement = wakerctl.agentctl.read_registry(registry)
        replacement["sessions"]["school-main"]["session_id"] = "replacement"
        wakerctl.agentctl.atomic_write_json(registry, replacement)
        self.now += 3601
        self.runner.add(
            lambda a: len(a) > 1 and "usagectl.py" in a[1],
            0,
            '{"profile":"claude-school","state":"READY"}',
        )
        self.assertEqual(wakerctl.scan(ctx), ["evt-quota-school-main-remap"])
        with mock.patch.object(wakerctl, "preflight", return_value=[]):
            self.assertEqual(
                wakerctl.dispatch(ctx),
                [("evt-quota-school-main-remap", "blocked")],
            )
        sends = [
            call
            for call in self.runner.calls
            if len(call["argv"]) > 1 and "agentctl.py" in call["argv"][1]
        ]
        self.assertEqual(sends, [])

    def test_capacity_guard_blocks_root_before_invocation_without_consuming_event(self):
        self.write_config(capacity_guard=True)
        ctx = self.ctx()
        path = self.arm_sentinel(ctx, "capacity")
        path.write_text("done")
        wakerctl.scan(ctx)
        self.runner.add(
            lambda a: "usagectl.py" in a[1] and "check" in a,
            3,
            '{"profile":"codex-personal","state":"EXHAUSTED"}',
        )
        self.assertEqual(wakerctl.dispatch(ctx), [("evt-capacity", "blocked")])
        self.assertEqual(self.runner.action_calls("codex"), [])
        paths = wakerctl.event_paths(ctx, "evt-capacity")
        self.assertFalse(paths["invoked"].exists())
        self.assertTrue(paths["blocked"].exists())

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


class NotifyTests(WakerTestCase):
    def write_config(self, **overrides):
        overrides.setdefault("notify_command", ["/usr/bin/mail", "-s", "{subject}", "user@example.com"])
        overrides.setdefault("idle_guard_ticks", 0)
        super().write_config(**overrides)

    def mail_calls(self):
        return [c for c in self.runner.calls if c["argv"][0] == "/usr/bin/mail"]

    def test_blocked_on_user_notifies_exactly_once_with_instructions(self):
        ctx = self.ctx()
        blocked = wakerctl.blocked_on_user_path(ctx)
        blocked.parent.mkdir(parents=True, exist_ok=True)
        blocked.write_text(json.dumps({"decision_needed": "authorize Gate 3"}))
        for _ in range(5):
            wakerctl.tick(ctx)
        calls = self.mail_calls()
        self.assertEqual(len(calls), 1)
        self.assertIn("needs your decision", calls[0]["argv"][2])
        self.assertIn("authorize Gate 3", calls[0]["input"])
        self.assertIn("Answering a BLOCKED-ON-USER stop", calls[0]["input"])

    def test_new_blocked_declaration_notifies_again(self):
        ctx = self.ctx()
        blocked = wakerctl.blocked_on_user_path(ctx)
        blocked.parent.mkdir(parents=True, exist_ok=True)
        blocked.write_text("{}")
        os.utime(blocked, (self.now - 100, self.now - 100))
        wakerctl.tick(ctx)
        os.unlink(blocked)
        blocked.write_text(json.dumps({"decision_needed": "second ask"}))
        os.utime(blocked, (self.now + 100, self.now + 100))
        wakerctl.tick(ctx)
        self.assertEqual(len(self.mail_calls()), 2)

    def test_environment_blocked_event_notifies_once(self):
        self.write_config(codex_bin=str(self.dir / "missing-codex"))
        ctx = self.ctx()
        path = self.arm_sentinel(ctx, "envblk")
        path.write_text("x")
        for _ in range(4):
            wakerctl.tick(ctx)
        calls = self.mail_calls()
        self.assertEqual(len(calls), 1)
        self.assertIn("Dispatch blocked", calls[0]["argv"][2])
        self.assertIn("evt-envblk", calls[0]["input"])

    def test_retries_exhausted_notifies(self):
        ctx = self.ctx()
        self.runner.add(lambda a: "codex" in a[0], 1, "always failing")
        path = self.arm_sentinel(ctx, "exh")
        path.write_text("x")
        for _ in range(8):
            wakerctl.tick(ctx)
        exhausted = [c for c in self.mail_calls() if "retries exhausted" in c["argv"][2].lower()]
        self.assertEqual(len(exhausted), 1)

    def test_failed_send_retries_next_tick(self):
        ctx = self.ctx()
        state = {"fails": 1}

        def flaky_mail(argv):
            if state["fails"]:
                state["fails"] -= 1
                return types.SimpleNamespace(returncode=1, stdout="relay down")
            return types.SimpleNamespace(returncode=0, stdout="")

        self.runner.add(lambda a: a[0] == "/usr/bin/mail", flaky_mail)
        blocked = wakerctl.blocked_on_user_path(ctx)
        blocked.parent.mkdir(parents=True, exist_ok=True)
        blocked.write_text("{}")
        wakerctl.tick(ctx)
        wakerctl.tick(ctx)
        wakerctl.tick(ctx)
        self.assertEqual(len(self.mail_calls()), 2)  # one failed, one delivered, then quiet
        ledger = (self.dir / "state" / "LEDGER.tsv").read_text()
        self.assertIn("notify-failed", ledger)
        self.assertIn("\tnotified\t", ledger)

    def test_no_notify_command_is_silent(self):
        self.write_config(notify_command=None)
        ctx = self.ctx()
        blocked = wakerctl.blocked_on_user_path(ctx)
        blocked.parent.mkdir(parents=True, exist_ok=True)
        blocked.write_text("{}")
        wakerctl.tick(ctx)
        self.assertEqual(self.mail_calls(), [])


class ClaudeRootTests(WakerTestCase):
    """An interim Claude root (PORTING.md §6d) must resume correctly."""

    def setUp(self):
        super().setUp()
        self.root_cwd = self.dir / "claude-root"
        self.root_cwd.mkdir()
        self.claude = self.dir / "claude"
        self.claude.write_text("#!/bin/bash\nexit 0\n")
        self.claude.chmod(self.claude.stat().st_mode | stat.S_IXUSR)
        self.write_config(
            claude_bin=str(self.claude),
            root={
                "provider": "claude",
                "profile": "claude-school",
                "thread_id": "11111111-2222-3333-4444-555555555555",
                "cwd": str(self.root_cwd),
            },
        )

    def test_claude_root_resume_argv_and_home(self):
        ctx = self.ctx()
        path = self.arm_sentinel(ctx, "croot")
        path.write_text("x")
        wakerctl.scan(ctx)
        outcomes = wakerctl.dispatch(ctx)
        self.assertEqual(outcomes, [("evt-croot", "resumed")])
        call = self.runner.action_calls("claude")[0]
        argv, env = call["argv"], call["env"]
        self.assertEqual(argv[0], str(self.claude))
        self.assertIn("--resume", argv)
        self.assertIn("11111111-2222-3333-4444-555555555555", argv)
        self.assertIn("--dangerously-skip-permissions", argv)
        self.assertIn("--model", argv)
        self.assertTrue(env["HOME"].endswith("claude-homes/school"))
        self.assertIn("next dependency-ready campaign action", argv[-1])
        self.assertEqual(call["cwd"], self.root_cwd.resolve())

    def test_preflight_checks_claude_binary_for_claude_root(self):
        self.write_config(
            claude_bin=str(self.dir / "missing-claude"),
            root={"provider": "claude", "profile": "claude-school", "thread_id": "1" * 8},
        )
        ctx = self.ctx()
        problems = wakerctl.preflight(ctx, quiet=True)
        self.assertTrue(any("claude binary missing" in p for p in problems))


class StatusReportTests(WakerTestCase):
    def write_config(self, **overrides):
        overrides.setdefault("notify_command", ["/usr/bin/mail", "-s", "{subject}", "user@example.com"])
        overrides.setdefault("status_report_interval_seconds", 21600)
        overrides.setdefault("idle_guard_ticks", 0)
        super().write_config(**overrides)

    def mail_calls(self):
        return [c for c in self.runner.calls if c["argv"][0] == "/usr/bin/mail"]

    def test_production_config_disables_routine_digest(self):
        config = json.loads(wakerctl.DEFAULT_CONFIG.read_text())
        self.assertEqual(config["status_report_interval_seconds"], 0)

    def test_digest_sent_once_per_interval_bucket(self):
        ctx = self.ctx()
        self.arm_sentinel(ctx, "steady")
        for _ in range(5):
            wakerctl.tick(ctx)
            self.now += 300
        self.assertEqual(len(self.mail_calls()), 1)
        self.now += 21600
        wakerctl.tick(ctx)
        wakerctl.tick(ctx)
        calls = self.mail_calls()
        self.assertEqual(len(calls), 2)
        self.assertIn("WORKING", calls[0]["argv"][2])
        self.assertIn("Armed watches: 1", calls[0]["input"])
        self.assertIn("steady (file-sentinel)", calls[0]["input"])
        self.assertIn("OPERATOR-GUIDE.md", calls[0]["input"])

    def test_digest_headline_reflects_blocked_state(self):
        ctx = self.ctx()
        blocked = wakerctl.blocked_on_user_path(ctx)
        blocked.parent.mkdir(parents=True, exist_ok=True)
        blocked.write_text("{}")
        wakerctl.tick(ctx)
        digests = [c for c in self.mail_calls() if "ACTION REQUIRED" in c["argv"][2]]
        self.assertEqual(len(digests), 1)
        self.assertIn("a user decision is required", digests[0]["argv"][2])

    def test_digest_omits_closed_history_and_names_disabled_idle_guard(self):
        ctx = self.ctx()
        self.arm_sentinel(ctx, "historical")
        watch_path = ctx.watches_dir / "historical.json"
        watch = wakerctl.read_json(watch_path)
        watch["state"] = "fired"
        wakerctl.agentctl.atomic_write_json(watch_path, watch)
        paths = wakerctl.event_paths(ctx, "evt-historical")
        wakerctl.agentctl.atomic_write_json(paths["event"], {"event_id": "evt-historical"})
        wakerctl.agentctl.atomic_write_json(paths["done"], {"outcome": "resumed"})
        wakerctl.agentctl.atomic_write_json(
            ctx.state_dir / "last-tick.json",
            {"at_utc": ctx.now_iso(), "node": "test", "watch_errors": 0},
        )
        subject, body = wakerctl.compose_status_report(ctx)
        self.assertIn("HEALTHY", subject)
        self.assertNotIn("historical (", body)
        self.assertIn("Historical records omitted: 1 closed watches, 1 terminal events", body)
        self.assertIn("automatic idle resume is disabled", body)
        self.assertNotIn("guard will act", body)

    def test_digest_prioritizes_staged_queue_and_summarizes_compute(self):
        self.write_config(
            campaign_queue_status_command=["/bin/campaignctl", "status", "--json"],
        )
        queue_status = (
            '{"counts":{"staged":2,"approved":1,"failed":0,"stale":0,'
            '"outcome-unknown":0,"succeeded":7,"revoked":0},"items":[]}'
        )
        self.runner.add(lambda a: a[0] == "/bin/campaignctl", 0, queue_status)
        self.runner.add(
            lambda a: a[0] == "squeue",
            0,
            "/usr/bin/python3.11|RUNNING|/usr/bin/python3.11\n"
            "101|RUNNING|analysis\n102|PENDING|analysis\n103|PENDING|combine\n",
        )
        subject, body = wakerctl.compose_status_report(self.ctx())
        self.assertIn("ACTION REQUIRED", subject)
        self.assertIn("review 2 staged queue item(s)", body)
        self.assertIn(
            "Queue: staged=2, approved=1, attention=0, terminal_failures=0, completed=7",
            body,
        )
        self.assertIn("Compute: PENDING=2, RUNNING=1", body)
        self.assertIn("Compute names: analysis=2, combine=1", body)
        self.assertIn("Ticker scheduler row: present", body)
        self.assertNotIn("/usr/bin/python3.11=", body)

    def test_digest_disabled_by_interval_zero(self):
        self.write_config(status_report_interval_seconds=0)
        ctx = self.ctx()
        self.arm_sentinel(ctx, "quiet")
        for _ in range(4):
            wakerctl.tick(ctx)
            self.now += 21600
        self.assertEqual(self.mail_calls(), [])


class StatusAndCronTests(WakerTestCase):
    def test_status_reports_states_cross_node_readably(self):
        ctx = self.ctx()
        path = self.arm_sentinel(ctx, "st")
        path.write_text("x")
        wakerctl.tick(ctx)
        report = wakerctl.status(ctx)
        self.assertEqual(report["watches"], [])
        self.assertEqual(report["archived_watch_count"], 1)
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

    def test_cron_preserves_explicit_runtime_state_directory(self):
        with mock.patch.dict(
            os.environ, {"WAKER_STATE_DIR": "/shared/runtime state"}
        ):
            ctx = wakerctl.Ctx(
                config_path=self.config_path,
                state_dir=Path("/shared/runtime state"),
                runner=self.runner,
                clock=lambda: self.now,
            )
            cron = "\n".join(wakerctl.scrontab_lines(ctx, 5))
        self.assertIn(
            "WAKER_STATE_DIR='/shared/runtime state' /usr/bin/python3.11", cron
        )

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

    def test_install_cron_refuses_when_existing_table_cannot_be_read(self):
        self.runner.add(
            lambda a: a == ["scrontab", "-l"],
            1,
            "temporary controller failure",
        )
        ctx = self.ctx()
        with self.assertRaisesRegex(wakerctl.WakerError, "refusing to replace"):
            wakerctl.install_cron(ctx, 5)
        writes = [
            call for call in self.runner.calls
            if call["argv"][0] == "scrontab" and call["argv"] != ["scrontab", "-l"]
        ]
        self.assertEqual(writes, [])

    def test_tick_runs_optional_heartbeat_without_affecting_dispatch(self):
        self.write_config(heartbeat_command=["/bin/heartbeat"])
        self.runner.add(lambda a: a[0] == "/bin/heartbeat", 0, "")
        result = wakerctl.tick(self.ctx())
        self.assertTrue(result["heartbeat"])
        self.assertEqual(len(self.runner.action_calls("heartbeat")), 1)

    def test_tick_runs_optional_approval_queue_without_llm_dispatch(self):
        self.write_config(campaign_queue_command=["/bin/campaignctl", "run-ready", "--json"])
        self.runner.add(
            lambda a: a[0] == "/bin/campaignctl",
            0,
            '{"status":"idle"}',
        )
        result = wakerctl.tick(self.ctx())
        self.assertEqual(result["campaign_queue"]["status"], "idle")
        self.assertEqual(result["campaign_queue"]["returncode"], 0)
        self.assertEqual(len(self.runner.action_calls("campaignctl")), 1)

    def test_queue_failure_is_ledgered_and_notified(self):
        self.write_config(
            campaign_queue_command=["/bin/campaignctl", "run-ready", "--json"],
            notify_command=["/bin/notify", "{key}", "{subject}"],
        )
        self.runner.add(
            lambda a: a[0] == "/bin/campaignctl",
            4,
            '{"id":"x","status":"stale"}',
        )
        self.runner.add(lambda a: a[0] == "/bin/notify", 0, "")
        result = wakerctl.tick(self.ctx())
        self.assertEqual(result["campaign_queue"]["status"], "stale")
        ledger = (self.dir / "state" / "LEDGER.tsv").read_text()
        self.assertIn("queue-failed", ledger)
        self.assertEqual(len(self.runner.action_calls("notify")), 1)

    def test_staged_queue_item_notifies_once(self):
        self.write_config(
            campaign_queue_status_command=["/bin/campaignctl", "status", "--json"],
            notify_command=["/bin/notify", "{key}", "{subject}"],
        )
        status = (
            '{"counts":{"staged":1},"items":['
            '{"id":"next-check","state":"staged","digest":"abc123"}]}'
        )
        self.runner.add(lambda a: a[0] == "/bin/campaignctl", 0, status)
        self.runner.add(lambda a: a[0] == "/bin/notify", 0, "")
        first = wakerctl.tick(self.ctx())
        second = wakerctl.tick(self.ctx())
        self.assertEqual(len(first["notified"]), 1)
        self.assertNotIn("notified", second)
        self.assertEqual(len(self.runner.action_calls("notify")), 1)

    def test_ledger_records_full_lifecycle(self):
        ctx = self.ctx()
        path = self.arm_sentinel(ctx, "led")
        path.write_text("x")
        wakerctl.tick(ctx)
        rows = [line.split("\t") for line in (self.dir / "state" / "LEDGER.tsv").read_text().splitlines()]
        transitions = [row[2] for row in rows if row[1] == "evt-led"]
        self.assertEqual(
            transitions,
            ["watch-armed", "event-emitted", "invoked", "done", "watch-archived"],
        )
        for row in rows:
            self.assertEqual(len(row), 5)  # ts, id, transition, owner, detail

    def test_compact_archives_only_terminal_legacy_watches(self):
        ctx = self.ctx()
        terminal_path = self.arm_sentinel(ctx, "terminal")
        terminal_path.write_text("done")
        wakerctl.scan(ctx)
        wakerctl.event_paths(ctx, "evt-terminal")["done"].write_text(
            json.dumps({"outcome": "resumed"})
        )
        self.arm_sentinel(ctx, "active")
        archived = wakerctl.compact_terminal_watches(ctx)
        self.assertEqual(archived, ["terminal"])
        self.assertTrue(wakerctl.archived_watch_path(ctx, "terminal").exists())
        self.assertTrue(wakerctl.watch_path(ctx, "active").exists())


class ScanPerWatchIsolationTests(WakerTestCase):
    """One malformed watch must not silence the waker (KNOWN_ISSUES: `scan()` has no per-watch guard).

    THE ITERATION ORDER IS LOAD-BEARING AND IS WHY THE IDS ARE NAMED AS THEY ARE. `load_watches()`
    iterates `sorted(watches_dir.glob("*.json"))`, so the filenames fix the order. The broken watch is
    `aaa-broken` and the valid one `zzz-valid` precisely so the broken one is evaluated FIRST -- with
    the order reversed, the pre-fix code would fire the valid watch before reaching the broken one and
    every assertion below would pass against the unguarded source, i.e. the test would be unpowered
    while looking identical.

    THE MALFORMATION IS SEMANTIC, NOT SYNTACTIC, AND THAT ALSO MATTERS. `load_watches()` already wraps
    `read_json` in `contextlib.suppress(OSError, json.JSONDecodeError)`, so a corrupt file is skipped
    and breaks nothing -- a test that wrote garbage bytes would pass on the unfixed code too. What
    actually raises is valid JSON with an unknown `kind`, which `evaluate()` ends by raising
    `WakerError` on, deliberately. That is the realistic shape: a watch armed under an older schema.

    The watch is written straight to disk rather than through `add_watch()`, because `add_watch()`
    calls `validate_watch()` and would reject it -- correctly. The file arrives by schema drift or a
    hand edit in this text-file state tree, not through the CLI.
    """

    def _write_broken_watch(self, ctx, watch_id="aaa-broken", kind="a-kind-that-does-not-exist"):
        path = wakerctl.watch_path(ctx, watch_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "watch_id": watch_id,
            "kind": kind,                      # valid JSON, unknown kind -> evaluate() raises
            "params": {},
            "state": "armed",
            "armed_at_utc": "2027-01-01T00:00:00+00:00",
            "unreliable": 0,
        }))
        return path

    @staticmethod
    def _prefix_scan(ctx):
        """The scan() body EXACTLY as it stood before the per-watch guard, as a positive control.

        Reproduced here rather than described so the test can prove its own power: the assertions
        below are only meaningful if this scenario genuinely breaks the old code, and the way to
        establish that is to run the old code. Same technique as
        `test_flux_universe_fix.test_the_prefix_source_would_fail`.
        """
        emitted = []
        for watch in wakerctl.load_watches(ctx):
            if watch.get("state") != "armed":
                continue
            fired = wakerctl.evaluate(ctx, watch)          # <- unguarded: this is the defect
            if fired is None:
                continue
            event_type, payload = fired
            event_id = f"evt-{watch['watch_id']}"
            wakerctl.emit_event(ctx, event_id, watch["watch_id"], event_type, payload)
            watch["state"] = "fired"
            watch["fired_at_utc"] = ctx.now_iso()
            wakerctl.save_watch(ctx, watch)
            emitted.append(event_id)
        wakerctl._write_tick_receipt(ctx)
        return emitted

    # ---- the positive control: prove the scenario breaks the PRE-FIX code -----------------------
    def test_prefix_scan_aborts_and_skips_the_receipt(self):
        """POWER TEST. Without this, everything below could be vacuously true."""
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, watch_id="zzz-valid")
        sentinel.write_text("done")
        self._write_broken_watch(ctx)

        with self.assertRaises(wakerctl.WakerError):
            self._prefix_scan(ctx)

        # The two consequences that make the defect silent rather than loud:
        self.assertFalse(
            (ctx.state_dir / "last-tick.json").exists(),
            "pre-fix scan should skip the tick receipt, which is what makes liveness go stale",
        )
        self.assertFalse(
            wakerctl.event_paths(ctx, "evt-zzz-valid")["event"].exists(),
            "pre-fix scan should never reach the valid watch",
        )

    # ---- the fix ------------------------------------------------------------------------------
    def test_malformed_watch_does_not_stop_a_valid_one(self):
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, watch_id="zzz-valid")
        sentinel.write_text("done")
        self._write_broken_watch(ctx)

        emitted = wakerctl.scan(ctx)

        self.assertEqual(emitted, ["evt-zzz-valid"])
        self.assertTrue(wakerctl.event_paths(ctx, "evt-zzz-valid")["event"].exists())

    def test_tick_receipt_is_written_and_names_the_failing_watch(self):
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, watch_id="zzz-valid")
        sentinel.write_text("done")
        self._write_broken_watch(ctx)

        wakerctl.scan(ctx)

        receipt = json.loads((ctx.state_dir / "last-tick.json").read_text())
        self.assertEqual(receipt["watch_errors"], 1)
        self.assertEqual([e["watch_id"] for e in receipt["watch_error_detail"]], ["aaa-broken"])
        self.assertIn("WakerError", receipt["watch_error_detail"][0]["error"])

    def test_clean_pass_records_zero_errors_AND_the_key_is_PRESENT(self):
        """PRESENCE, not merely absence.

        A test asserting only "no errors were reported" passes on a receipt that has no such key at
        all -- so it would also pass if the field were removed, which is the null-as-absent shape.
        Assert the key exists and equals 0, so a reader can distinguish "clean" from "never looked".
        """
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, watch_id="zzz-valid")
        sentinel.write_text("done")

        wakerctl.scan(ctx)

        receipt = json.loads((ctx.state_dir / "last-tick.json").read_text())
        self.assertIn("watch_errors", receipt)          # <- the presence half
        self.assertEqual(receipt["watch_errors"], 0)
        self.assertNotIn("watch_error_detail", receipt)

    def test_failing_watch_is_marked_unreliable_and_not_disarmed(self):
        """The counter makes a persistently-broken watch visible in `watch-list`.

        It is deliberately NOT disarmed: an exception here is not necessarily permanent, and retiring
        a watch on one bad tick would be the same fail-open-into-silence the guard exists to end.
        """
        ctx = self.ctx()
        self._write_broken_watch(ctx)

        wakerctl.scan(ctx)
        after_one = wakerctl.read_json(wakerctl.watch_path(ctx, "aaa-broken"))
        self.assertEqual(after_one["unreliable"], 1)
        self.assertEqual(after_one["state"], "armed", "must stay armed, not be retired on one error")

        wakerctl.scan(ctx)
        self.assertEqual(wakerctl.read_json(wakerctl.watch_path(ctx, "aaa-broken"))["unreliable"], 2)

    def test_every_valid_watch_after_several_broken_ones_still_fires(self):
        """The defect was order-dependent, so check more than one broken watch ahead of the good one."""
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, watch_id="zzz-valid")
        sentinel.write_text("done")
        for i in range(3):
            self._write_broken_watch(ctx, watch_id=f"aaa-broken-{i}")

        emitted = wakerctl.scan(ctx)

        self.assertEqual(emitted, ["evt-zzz-valid"])
        receipt = json.loads((ctx.state_dir / "last-tick.json").read_text())
        self.assertEqual(receipt["watch_errors"], 3)

    def test_tick_still_reaches_its_guards_when_a_watch_is_malformed(self):
        """The blast radius was never just scan(): tick() calls it first, unguarded.

        `dispatch()` and the three guards all run AFTER `scan()`, so an escaping exception skipped
        every one of them. `tick()` returning a result dict at all is the assertion.
        """
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, watch_id="zzz-valid")
        sentinel.write_text("done")
        self._write_broken_watch(ctx)

        result = wakerctl.tick(ctx)

        self.assertIn("emitted", result)
        self.assertIn("dispatch", result)
        self.assertEqual(result["emitted"], ["evt-zzz-valid"])


class WatchArmTests(WakerTestCase):
    """`watch-arm` is the inverse of `watch-disarm` (KNOWN_ISSUES row 56: a one-way door)."""

    def ledger_transitions(self, watch_id):
        rows = [line.split("\t") for line in (self.dir / "state" / "LEDGER.tsv").read_text().splitlines()]
        return [row[2] for row in rows if row[1] == f"evt-{watch_id}"]

    def test_add_disarm_arm_restores_an_armed_watch_with_a_ledger_row(self):
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, "door")
        wakerctl.disarm_watch(ctx, "door")
        self.assertFalse(wakerctl.watch_path(ctx, "door").exists())
        self.assertTrue(wakerctl.archived_watch_path(ctx, "door").exists())

        wakerctl.rearm_watch(ctx, "door")

        self.assertFalse(wakerctl.archived_watch_path(ctx, "door").exists())
        watch = wakerctl.read_json(wakerctl.watch_path(ctx, "door"))
        self.assertEqual(wakerctl.watch_state(watch), "armed")
        self.assertEqual(watch["action"]["context"], "ctx-note")  # context survives the round trip
        self.assertNotIn("disarmed_at_utc", watch)
        self.assertIn("rearmed_at_utc", watch)
        self.assertEqual(
            self.ledger_transitions("door"),
            ["watch-armed", "watch-disarmed", "watch-archived", "watch-rearmed"],
        )
        # And it is a WORKING watch, not only a relabelled one: it fires.
        sentinel.write_text("done\n")
        self.assertEqual(wakerctl.scan(ctx), ["evt-door"])

    def test_arm_refuses_a_fired_watch(self):
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, "fired")
        sentinel.write_text("done\n")
        self.assertEqual(wakerctl.scan(ctx), ["evt-fired"])
        with self.assertRaisesRegex(wakerctl.WakerError, "'fired', not 'disarmed'"):
            wakerctl.rearm_watch(ctx, "fired")
        live = wakerctl.read_json(wakerctl.watch_path(ctx, "fired"))
        self.assertEqual(wakerctl.watch_state(live), "fired")

    def test_arm_refuses_an_unknown_id(self):
        with self.assertRaisesRegex(wakerctl.WakerError, "unknown watch: ghost"):
            wakerctl.rearm_watch(self.ctx(), "ghost")

    def test_arm_refuses_an_already_armed_watch(self):
        ctx = self.ctx()
        self.arm_sentinel(ctx, "live")
        with self.assertRaisesRegex(wakerctl.WakerError, "'armed', not 'disarmed'"):
            wakerctl.rearm_watch(ctx, "live")

    def test_arm_refuses_when_its_event_id_is_already_taken(self):
        """Re-arming into an existing evt-<id> would go `fired` and never dispatch."""
        ctx = self.ctx()
        self.arm_sentinel(ctx, "taken")
        wakerctl.disarm_watch(ctx, "taken")
        wakerctl.emit_event(ctx, "evt-taken", "taken", "manual", {})
        with self.assertRaisesRegex(wakerctl.WakerError, "already exists"):
            wakerctl.rearm_watch(ctx, "taken")
        self.assertTrue(wakerctl.archived_watch_path(ctx, "taken").exists())

    def test_arm_revalidates_against_slurm_now_and_leaves_the_archive_on_refusal(self):
        ctx = self.ctx()
        # Armed while Slurm could not see the job, so add-time validation could not refuse.
        self.runner.add(lambda a: a[0] in {"squeue", "sacct"}, 1, "")
        wakerctl.add_watch(
            ctx,
            {
                "watch_id": "arr",
                "kind": "slurm-array",
                "params": {"job_id": "57266000", "tasks": "1"},
                "action": {"type": "root-resume", "context": ""},
            },
        )
        wakerctl.disarm_watch(ctx, "arr")
        # Now Slurm knows the array, and it has only task 0.
        self.runner.rules.clear()
        self.runner.add(lambda a: a[0] == "sacct", 0, "57266000_0\n")
        with self.assertRaisesRegex(wakerctl.WakerError, r"has no task \[1\]"):
            wakerctl.rearm_watch(ctx, "arr")
        archived = wakerctl.read_json(wakerctl.archived_watch_path(ctx, "arr"))
        self.assertEqual(wakerctl.watch_state(archived), "disarmed")
        self.assertFalse(wakerctl.watch_path(ctx, "arr").exists())
        self.assertNotIn("watch-rearmed", self.ledger_transitions("arr"))

    def run_cli(self, *argv):
        out = io.StringIO()
        argv_patch = mock.patch.object(
            sys, "argv", ["wakerctl.py", "--config", str(self.config_path), *argv]
        )
        env_patch = mock.patch.dict(os.environ, {"WAKER_STATE_DIR": str(self.dir / "state")})
        with argv_patch, env_patch, contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = wakerctl.main()
        return code, out.getvalue()

    def test_cli_round_trip_and_state_filter_is_whole_field(self):
        sentinel = self.dir / "cli.sentinel"
        added = self.run_cli(
            "watch-add", "--id", "cli", "--kind", "file-sentinel", "--param", f"path={sentinel}"
        )
        self.assertEqual(added[0], 0)
        self.assertEqual(self.run_cli("watch-disarm", "--id", "cli")[0], 0)
        # A disarmed watch must NOT list under --state armed (the `grep armed` trap).
        self.assertEqual(self.run_cli("watch-list", "--state", "armed"), (0, ""))
        self.assertEqual(self.run_cli("watch-arm", "--id", "cli"), (0, "armed cli\n"))
        self.assertEqual(
            self.run_cli("watch-list", "--state", "armed"), (0, "cli\tfile-sentinel\tarmed\n")
        )
        self.assertEqual(self.run_cli("watch-arm", "--id", "cli")[0], 1)  # already armed
        self.assertEqual(self.run_cli("watch-arm", "--id", "nope")[0], 1)  # unknown


class ControlPlaneTickTests(WakerTestCase):
    """The preflight control-plane checks run from tick(), REPORT-ONLY (KNOWN_ISSUES row 52).

    Slurm and scrontab outputs are the 2026-08-19 Perlmutter transcripts from
    test_wakerctl_preflight_watch_health, with the ticker row in its RUNNABLE form so
    that the only real problem is the watch on a task the array does not have.
    """

    def write_config(self, **overrides):
        overrides.setdefault("tick_control_plane_checks", True)
        overrides.setdefault("notify_command", ["/bin/notify", "{key}", "{subject}"])
        # A real interpreter, so preflight passes and dispatch is observable on any host.
        overrides.setdefault("python", sys.executable)
        super().write_config(**overrides)

    def setUp(self):
        super().setUp()
        self.runner.add(lambda a: a[:2] == ["scrontab", "-l"], 0, health.SCRONTAB_REAL)
        self.runner.add(lambda a: a[0] == "squeue" and "--me" in a, 0, health.SQUEUE_CRON_RUNNABLE)
        self.runner.add(lambda a: a[0] == "sacct", 0, health.SACCT_57266000)
        self.runner.add(lambda a: a[0] == "squeue" and "-j" in a, 0, health.SQUEUE_57266000)
        self.runner.add(lambda a: a[0] == "/bin/notify", 0, "")

    def write_bad_subject_watch(self, ctx):
        """Saved directly, as a watch armed before add-time validation existed would be."""
        ctx.watches_dir.mkdir(parents=True, exist_ok=True)
        wakerctl.save_watch(
            ctx,
            {
                "watch_id": "gate5-do-train-57266000-r2",
                "kind": "slurm-array",
                "params": dict(health.WATCH_R2_PARAMS),
                "state": "armed",
                "unreliable": 0,
                "action": {"type": "root-resume", "context": "fixture"},
            },
        )

    def notices(self):
        return self.runner.action_calls("/bin/notify")

    def test_bad_subject_watch_emits_one_notice_and_the_tick_still_dispatches(self):
        ctx = self.ctx()
        self.write_bad_subject_watch(ctx)
        sentinel = self.arm_sentinel(ctx, "st")
        sentinel.write_text("done\n")

        first = wakerctl.tick(ctx)

        self.assertEqual(first["dispatch"], [("evt-st", "resumed")])
        self.assertEqual(len(self.runner.action_calls("codex")), 1)
        self.assertEqual(len(self.notices()), 1)
        notice = self.notices()[0]
        self.assertIn("armed but not working", " ".join(notice["argv"]))
        self.assertIn("gate5-do-train-57266000-r2", notice["input"])
        self.assertEqual(first["control_plane"]["actionable"], 1)
        recorded = wakerctl.read_json(wakerctl.control_plane_path(ctx))
        self.assertIn("gate5-do-train-57266000-r2", " ".join(recorded["problems"]))

        second = wakerctl.tick(ctx)  # the same problem set sends no second notice
        self.assertEqual(len(self.notices()), 1)
        self.assertEqual(second["control_plane"]["actionable"], 1)
        ledger = (ctx.state_dir / "LEDGER.tsv").read_text()
        self.assertEqual(ledger.count("control-plane-problem"), 1)

    def test_healthy_control_plane_adds_nothing_to_the_tick(self):
        ctx = self.ctx()
        result = wakerctl.tick(ctx)
        self.assertNotIn("control_plane", result)
        self.assertEqual(self.notices(), [])
        self.assertEqual(wakerctl.read_json(wakerctl.control_plane_path(ctx))["problems"], [])

    def test_unreachable_slurm_is_recorded_but_does_not_notify(self):
        self.runner.rules.insert(0, (lambda a: a[0] in {"squeue", "sacct"}, 1, "down"))
        ctx = self.ctx()
        self.write_bad_subject_watch(ctx)
        result = wakerctl.tick(ctx)
        problems = result["control_plane"]["problems"]
        self.assertTrue(problems)
        self.assertTrue(all(p.startswith(wakerctl.NO_EVIDENCE_PREFIX) for p in problems), problems)
        self.assertEqual(self.notices(), [])

    def test_a_raising_check_cannot_escape_the_tick_or_block_dispatch(self):
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, "st")
        sentinel.write_text("done\n")
        with mock.patch.object(wakerctl, "check_armed_watch_subjects", side_effect=RuntimeError("boom")):
            result = wakerctl.tick(ctx)
        self.assertEqual(result["dispatch"], [("evt-st", "resumed")])
        self.assertIn("boom", " ".join(result["control_plane"]["problems"]))

    def test_a_raising_guard_cannot_escape_the_tick(self):
        ctx = self.ctx()
        sentinel = self.arm_sentinel(ctx, "st")
        sentinel.write_text("done\n")
        with mock.patch.object(wakerctl, "control_plane_guard", side_effect=RuntimeError("guard-boom")):
            result = wakerctl.tick(ctx)
        self.assertEqual(result["dispatch"], [("evt-st", "resumed")])
        self.assertIn("guard-boom", " ".join(result["control_plane"]["problems"]))

    def test_checks_default_on_when_the_config_key_is_absent(self):
        config = json.loads(self.config_path.read_text())
        del config["tick_control_plane_checks"]
        self.config_path.write_text(json.dumps(config))
        ctx = self.ctx()
        self.write_bad_subject_watch(ctx)
        self.assertEqual(wakerctl.tick(ctx)["control_plane"]["actionable"], 1)

    def test_config_can_switch_the_checks_off(self):
        self.write_config(tick_control_plane_checks=False)
        ctx = self.ctx()
        self.write_bad_subject_watch(ctx)
        self.assertNotIn("control_plane", wakerctl.tick(ctx))
        self.assertEqual([c for c in self.runner.calls if c["argv"][:2] == ["scrontab", "-l"]], [])


if __name__ == "__main__":
    unittest.main()
