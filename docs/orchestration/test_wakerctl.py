import json
import os
from pathlib import Path
import stat
import tempfile
import threading
import time
import types
import unittest
from unittest import mock

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


if __name__ == "__main__":
    unittest.main()


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
