#!/usr/bin/python3.11
"""Deterministic external-event continuation for the persistent orchestration campaign.

wakerctl turns external facts (Slurm terminal states, queue latency, provider
resets, deadlines, heartbeats, file sentinels) into durable filesystem events,
and turns each event into at most one root-thread resume or worker follow-up.
It performs zero LLM calls while no event condition holds. All state lives on
the shared filesystem so any login node can scan, dispatch, and observe it.

Exactly-once is enforced by hard-link claims (atomic on Lustre/GPFS), never by
process liveness, tmux visibility, or flock alone. See WAKER.md for the design.
"""

from __future__ import annotations

import argparse
from collections import Counter
import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import agentctl  # noqa: E402  (expand_path, add_codex_options, profiles helpers)
import slurm_array_status  # noqa: E402

DEFAULT_CONFIG = HERE / "waker-config.json"
SCRON_BEGIN = "# BEGIN wakerctl managed block"
SCRON_END = "# END wakerctl managed block"

SLURM_TERMINAL_FAILURES = {
    "FAILED",
    "CANCELLED",
    "TIMEOUT",
    "OUT_OF_MEMORY",
    "NODE_FAIL",
    "PREEMPTED",
    "BOOT_FAIL",
    "DEADLINE",
    "REVOKED",
    "SPECIAL_EXIT",
}

DEFAULT_PREAMBLE = (
    "A real external event occurred for watch {watch_id} (type {event_type}). "
    "Read {event_path} exactly once and validate it; do not poll or enter a "
    "bounded wait loop. Preserve every persistent worker UUID; never replace a "
    "worker; use orchestration/agentctl.py send for worker follow-ups. Never "
    "consume a Codex reset credit without new explicit user authorization. Run "
    "one complete usage snapshot (orchestration/usagectl.py snapshot --json) "
    "before any provider dispatch. Handle the event, commit required receipts, "
    "and then continue with the next dependency-ready campaign action under "
    "this standing authorization; do not stop after only recommending it. "
    "Before ending the turn, re-arm continuation coverage with wakerctl (a "
    "watch for every job you submit, deadline you set, or reset you expect) "
    "and refresh docs/orchestration/LIVE-STATE.md with its generator. A turn "
    "may only end in one of two states: at least one armed watch exists, or "
    "you have written and committed "
    "docs/orchestration/state/waker/BLOCKED-ON-USER.json stating exactly "
    "which user decision is required. Goals remain disabled. If the ledger "
    "shows this event already reconciled, record that and stop."
)


class ActionTerminated(Exception):
    """The dispatcher received SIGTERM (e.g. Slurm wall) during an action."""


class WakerError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def parse_utc(value: str) -> float:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.timestamp()


def owner_string() -> str:
    return f"{socket.gethostname()}:{os.getpid()}"


def create_exclusive(path: Path, text: str) -> bool:
    """Atomically create path with text; False if it already exists.

    Uses write-temp + link(2), the primitive proven cluster-coherent on this
    filesystem, instead of relying on flock mount semantics.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
            return True
        except FileExistsError:
            return False
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


class Ctx:
    """Paths, configuration, and injectable runners for one wakerctl process."""

    def __init__(
        self,
        config_path: Path = DEFAULT_CONFIG,
        state_dir: Path | None = None,
        runner=None,
        clock=None,
    ) -> None:
        self.config_path = config_path
        self.config = read_json(config_path)
        env_state = os.environ.get("WAKER_STATE_DIR")
        if state_dir is not None:
            self.state_dir = state_dir
        elif env_state:
            self.state_dir = Path(env_state)
        else:
            self.state_dir = HERE / self.config.get("state_dir", "state/waker")
        self.repo = HERE.parent.parent
        self.watches_dir = self.state_dir / "watches"
        self.watch_archive_dir = self.state_dir / "archive" / "watches"
        self.events_dir = self.state_dir / "events"
        self.logs_dir = self.state_dir / "logs"
        self.ledger_path = self.state_dir / "LEDGER.tsv"
        self.resume_mutex = self.state_dir / "resume.mutex"
        self.runner = runner or self._run
        self.clock = clock or (lambda: dt.datetime.now(dt.timezone.utc).timestamp())

    @staticmethod
    def _run(
        argv: list[str],
        env: dict | None = None,
        cwd: Path | None = None,
        input_text: str | None = None,
    ):
        return subprocess.run(
            argv,
            env=env,
            cwd=cwd,
            **({"input": input_text} if input_text is not None else {"stdin": subprocess.DEVNULL}),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    def now(self) -> float:
        return self.clock()

    def now_iso(self) -> str:
        return (
            dt.datetime.fromtimestamp(self.now(), tz=dt.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        )

    # -- configuration accessors -------------------------------------------
    def profiles(self) -> dict:
        return agentctl.load_profiles(HERE / "profiles.json")

    def root(self) -> dict:
        root = self.config.get("root")
        if not isinstance(root, dict) or not root.get("thread_id"):
            raise WakerError("waker-config.json must define root.thread_id")
        return root

    def python_bin(self) -> str:
        return self.config.get("python", "/usr/bin/python3.11")

    def codex_bin(self) -> str | None:
        configured = self.config.get("codex_bin")
        if configured:
            return configured
        return shutil.which("codex")

    def claude_bin(self) -> str | None:
        configured = self.config.get("claude_bin")
        if configured:
            return configured
        fallback = agentctl.login_home() / ".local" / "bin" / "claude"
        return shutil.which("claude") or (str(fallback) if fallback.is_file() else None)

    def base_env(self) -> dict:
        env = os.environ.copy()
        env["HOME"] = str(agentctl.login_home())
        extra = [str(agentctl.login_home() / ".local" / "bin"), "/usr/bin", "/bin"]
        codex = self.config.get("codex_bin")
        if codex:
            extra.insert(0, str(Path(codex).parent))
        env["PATH"] = ":".join(extra + [env.get("PATH", "")])
        return env

    def ledger(self, event_id: str, transition: str, detail: str) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        line = "\t".join(
            [self.now_iso(), event_id, transition, owner_string(), detail.replace("\t", " ").replace("\n", " ")]
        )
        with open(self.ledger_path, "a") as handle:
            handle.write(line + "\n")


# ---------------------------------------------------------------------------
# Lease-based claims


def acquire_claim(ctx: Ctx, path: Path, lease_seconds: int, guard=None) -> bool:
    """Claim path exclusively; steal only expired claims whose guard allows it.

    guard() is consulted before stealing; it must return True only when it is
    provably safe (for events: the invoked marker is still absent).
    """
    payload = json.dumps(
        {"owner": owner_string(), "acquired_epoch": ctx.now(), "lease_seconds": lease_seconds},
        sort_keys=True,
    )
    if create_exclusive(path, payload):
        return True
    try:
        existing = read_json(path)
        expired = ctx.now() - float(existing.get("acquired_epoch", 0)) > float(
            existing.get("lease_seconds", lease_seconds)
        )
    except (OSError, json.JSONDecodeError, ValueError):
        expired = True
    if not expired:
        return False
    if guard is not None and not guard():
        return False
    with contextlib.suppress(FileNotFoundError):
        os.unlink(path)
    return create_exclusive(path, payload)


def release_claim(path: Path) -> None:
    with contextlib.suppress(FileNotFoundError):
        os.unlink(path)


# ---------------------------------------------------------------------------
# Watches


def watch_path(ctx: Ctx, watch_id: str) -> Path:
    agentctl.safe_role(watch_id)
    return ctx.watches_dir / f"{watch_id}.json"


def archived_watch_path(ctx: Ctx, watch_id: str) -> Path:
    agentctl.safe_role(watch_id)
    return ctx.watch_archive_dir / f"{watch_id}.json"


def archive_watch(ctx: Ctx, watch_id: str) -> bool:
    """Move one terminal watch out of the live scan directory.

    The event spool carries an immutable snapshot of the action and context, so
    dispatch and retries no longer need a terminal watch file.  Keeping only
    non-terminal watches in ``watches/`` prevents an old Lustre inode from
    wedging every future tick, while the archive preserves the exact record.
    """
    source = watch_path(ctx, watch_id)
    if not source.exists():
        return False
    destination = archived_watch_path(ctx, watch_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise WakerError(f"refusing to overwrite archived watch: {watch_id}")
    os.replace(source, destination)
    ctx.ledger(f"evt-{watch_id}", "watch-archived", str(destination))
    return True


def save_watch(ctx: Ctx, watch: dict) -> None:
    agentctl.atomic_write_json(watch_path(ctx, watch["watch_id"]), watch)


def load_watches(ctx: Ctx) -> list[dict]:
    if not ctx.watches_dir.is_dir():
        return []
    result = []
    for path in sorted(ctx.watches_dir.glob("*.json")):
        with contextlib.suppress(OSError, json.JSONDecodeError):
            result.append(read_json(path))
    return result


def compact_terminal_watches(ctx: Ctx) -> list[str]:
    """Archive terminal legacy watches whose event contract is complete.

    Disarmed watches have no future action.  Fired watches move only after a
    terminal ``.done`` marker exists, so old events that still depend on their
    watch file retain the legacy routing fallback until they finish.
    """
    archived: list[str] = []
    for watch in load_watches(ctx):
        watch_id = str(watch.get("watch_id") or "")
        state = watch_state(watch)
        if not watch_id or state not in {"disarmed", "fired"}:
            continue
        if state == "fired" and not event_paths(ctx, f"evt-{watch_id}")["done"].exists():
            continue
        if archive_watch(ctx, watch_id):
            archived.append(watch_id)
    return archived


def add_watch(ctx: Ctx, watch: dict) -> None:
    path = watch_path(ctx, watch["watch_id"])
    if path.exists() or archived_watch_path(ctx, watch["watch_id"]).exists():
        raise WakerError(f"watch already exists: {watch['watch_id']}")
    watch.setdefault("state", "armed")
    watch.setdefault("armed_at_utc", ctx.now_iso())
    watch.setdefault("armed_by", owner_string())
    watch.setdefault("unreliable", 0)
    validate_watch(ctx, watch)
    check_array_spec_against_slurm(ctx, watch)
    save_watch(ctx, watch)
    ctx.ledger(f"evt-{watch['watch_id']}", "watch-armed", f"kind={watch['kind']}")


KINDS = {
    "slurm-job",
    "slurm-array",
    "queue-latency",
    "provider-reset",
    "deadline",
    "heartbeat",
    "file-sentinel",
}


def validate_watch(ctx: Ctx, watch: dict) -> None:
    kind = watch.get("kind")
    params = watch.get("params") or {}
    action = watch.get("action") or {}
    if kind not in KINDS:
        raise WakerError(f"unknown watch kind: {kind}")
    required = {
        "slurm-job": ["job_id"],
        "slurm-array": ["job_id", "tasks"],
        "queue-latency": ["job_id", "threshold_seconds"],
        "provider-reset": ["at_utc", "account"],
        "deadline": ["at_utc"],
        "heartbeat": ["path", "max_age_seconds"],
        "file-sentinel": ["path"],
    }[kind]
    for key in required:
        if key not in params:
            raise WakerError(f"watch kind {kind} requires params.{key}")
    if "at_utc" in params:
        parse_utc(params["at_utc"])
    action_type = action.get("type")
    if action_type == "root-resume":
        ctx.root()
    elif action_type == "role-send":
        if not action.get("role") or not action.get("prompt_file"):
            raise WakerError("role-send action requires role and prompt_file")
    elif action_type == "command":
        argv = action.get("argv")
        if not argv or not isinstance(argv, list):
            raise WakerError("command action requires argv")
        program = Path(argv[0])
        if not program.is_absolute() or ctx.repo not in program.resolve().parents:
            raise WakerError("command action argv[0] must be an absolute path inside the repository")
    else:
        raise WakerError(f"unknown action type: {action_type}")


# ---------------------------------------------------------------------------
# Condition evaluation (pure given injected runner/clock)


def slurm_job_state(ctx: Ctx, job_id: str) -> tuple[str, str] | None:
    """Return (state, exit_code) once terminal, ('ACTIVE','') if visible, None if invisible."""
    queue = ctx.runner(["squeue", "-h", "-j", job_id, "-o", "%T|%r"])
    if queue.returncode == 0 and queue.stdout.strip():
        visible = []
        for raw in queue.stdout.splitlines():
            parts = raw.strip().split("|", 1)
            state = parts[0].strip().upper()
            reason = parts[1].strip() if len(parts) == 2 else ""
            if state:
                visible.append((state, reason))
        # Slurm leaves a job with an impossible dependency visible as PENDING,
        # so the sacct fallback is never reached.  It is nevertheless terminal
        # for orchestration purposes: no future scheduler transition can make
        # the dependency satisfiable.  Require every visible row to have the
        # dead dependency reason so an array with any live element stays active.
        if visible and all(
            state in {"PENDING", "DEPENDENCY_NEVER_SATISFIED"}
            and reason.split(maxsplit=1)[0].rstrip("+") == "DependencyNeverSatisfied"
            for state, reason in visible
        ):
            return ("DEPENDENCY_NEVER_SATISFIED", "N/A")
        return ("ACTIVE", "")
    acct = ctx.runner(
        ["sacct", "-X", "-n", "-P", "-j", job_id, "--format=JobIDRaw,State,ExitCode"]
    )
    if acct.returncode != 0:
        return None
    for raw in acct.stdout.splitlines():
        parts = raw.strip().split("|")
        if len(parts) >= 3 and parts[0] == job_id:
            state = parts[1].split()[0].rstrip("+") if parts[1].strip() else "UNKNOWN"
            if state == "COMPLETED" or state in SLURM_TERMINAL_FAILURES:
                return (state, parts[2])
            return ("ACTIVE", "")
    return None


def slurm_job_has_started(ctx: Ctx, job_id: str) -> tuple[bool | None, str]:
    """Return whether any allocation record has a real start time.

    Queue-latency watches are allowed to hedge only a wholly prestart job.  Array
    elements that already completed disappear from squeue, so current queue state
    alone is insufficient: consult allocation-level accounting (-X) and treat an
    explicit Start timestamp as durable started evidence.  None means accounting
    was unavailable or supplied no parseable records.
    """
    acct = ctx.runner(
        ["sacct", "-X", "-n", "-P", "-j", job_id, "--format=JobIDRaw,State,Start"]
    )
    if acct.returncode != 0:
        return None, f"sacct rc={acct.returncode}"
    saw = False
    for raw in acct.stdout.splitlines():
        parts = raw.strip().split("|")
        if len(parts) < 3 or not parts[0].strip():
            continue
        saw = True
        state = parts[1].strip().split()[0].rstrip("+") if parts[1].strip() else "UNKNOWN"
        start = parts[2].strip()
        if start not in {"", "Unknown", "N/A", "None", "NONE"}:
            return True, f"{parts[0].strip()} state={state} start={start}"
        if state in {"RUNNING", "COMPLETING"}:
            return True, f"{parts[0].strip()} state={state}"
    if not saw:
        return None, "sacct returned no allocation records"
    return False, "all accounting records are prestart"


def evaluate(ctx: Ctx, watch: dict) -> tuple[str, dict] | None:
    """Return (event_type, payload) when the watch condition holds, else None."""
    kind = watch["kind"]
    params = watch.get("params") or {}
    max_unreliable = int(watch.get("max_unreliable", 10))

    def unreliable_step() -> tuple[str, dict] | None:
        watch["unreliable"] = int(watch.get("unreliable", 0)) + 1
        save_watch(ctx, watch)
        if watch["unreliable"] >= max_unreliable:
            return ("monitor-error", {"kind": kind, "unreliable": watch["unreliable"]})
        return None

    def reliable() -> None:
        if watch.get("unreliable"):
            watch["unreliable"] = 0
            save_watch(ctx, watch)

    if kind == "slurm-job":
        observed = slurm_job_state(ctx, str(params["job_id"]))
        if observed is None:
            return unreliable_step()
        state, exit_code = observed
        if state == "ACTIVE":
            reliable()
            return None
        event = "slurm-job-complete" if state == "COMPLETED" and exit_code == "0:0" else "slurm-job-error"
        return (event, {"job_id": str(params["job_id"]), "state": state, "exit_code": exit_code})

    if kind == "slurm-array":
        snapshot = slurm_array_status.build_snapshot(
            str(params["job_id"]),
            slurm_array_status.expand_spec(str(params["tasks"])),
            runner=lambda argv: _text_runner(ctx, argv),
        )
        overall = snapshot.get("overall")
        if overall == "COMPLETE":
            return ("slurm-array-complete", snapshot)
        if overall == "ERROR":
            return ("slurm-array-error", snapshot)
        if snapshot.get("observer_errors") or snapshot.get("unknown_tasks"):
            return unreliable_step()
        reliable()
        return None

    if kind == "queue-latency":
        job_id = str(params["job_id"])
        threshold = float(params["threshold_seconds"])
        # SLURM_TIME_FORMAT=%s makes squeue print the submit time as an epoch,
        # avoiding the cluster-local-timezone ambiguity of the default format.
        queue = ctx.runner(
            ["squeue", "-h", "-j", job_id, "-o", "%T|%V"],
            env={**os.environ, "SLURM_TIME_FORMAT": "%s"},
        )
        if queue.returncode != 0 or not queue.stdout.strip():
            reliable()
            return None  # not pending anymore; the slurm-job watch owns terminal handling
        rows = []
        for raw in queue.stdout.splitlines():
            state, sep, submitted = raw.strip().partition("|")
            if not sep or not submitted.strip():
                return unreliable_step()
            rows.append((state.strip(), submitted.strip()))

        def disarm_started(detail: str) -> None:
            reliable()
            watch["state"] = "disarmed"
            watch["disarmed_at_utc"] = ctx.now_iso()
            watch["disarm_reason"] = f"job-started: {detail}"
            save_watch(ctx, watch)
            ctx.ledger(watch["watch_id"], "watch-auto-disarmed", watch["disarm_reason"])

        active = [state for state, _ in rows if state != "PENDING"]
        if active:
            disarm_started(f"current squeue states={sorted(set(active))}")
            return None
        submit_epochs = []
        try:
            for _, submitted in rows:
                submit_epochs.append(float(submitted) if submitted.isdigit() else parse_utc(submitted))
        except (TypeError, ValueError):
            return unreliable_step()
        submit_epoch = min(submit_epochs)
        waited = ctx.now() - submit_epoch
        if waited >= threshold:
            started, detail = slurm_job_has_started(ctx, job_id)
            if started is None:
                return unreliable_step()
            if started:
                disarm_started(detail)
                return None
            return (
                "queue-latency",
                {"job_id": job_id, "waited_seconds": int(waited),
                 "threshold_seconds": int(threshold), "prestart_verified": True},
            )
        return None

    if kind in {"deadline", "provider-reset"}:
        if ctx.now() >= parse_utc(params["at_utc"]):
            payload = {"at_utc": params["at_utc"]}
            if kind == "provider-reset":
                payload["account"] = params["account"]
            return (kind, payload)
        return None

    if kind == "heartbeat":
        path = Path(params["path"])
        max_age = float(params["max_age_seconds"])
        if path.exists():
            age = ctx.now() - path.stat().st_mtime
        else:
            age = ctx.now() - parse_utc(watch["armed_at_utc"])
        if age > max_age:
            return ("heartbeat-missed", {"path": str(path), "age_seconds": int(age)})
        return None

    if kind == "file-sentinel":
        path = Path(params["path"])
        if not path.exists():
            return None
        if "must_contain" in params:
            with contextlib.suppress(OSError):
                if params["must_contain"] not in path.read_text(errors="replace")[:65536]:
                    return None
        return ("file-sentinel", {"path": str(path)})

    raise WakerError(f"unknown watch kind: {kind}")


def _text_runner(ctx: Ctx, argv: list[str]) -> str:
    result = ctx.runner(argv)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, argv, output=result.stdout)
    return result.stdout


# ---------------------------------------------------------------------------
# Events


def event_paths(ctx: Ctx, event_id: str) -> dict[str, Path]:
    # Event ids may contain dots (retry/recon derivatives), so suffixes are
    # appended to the full name rather than substituted with with_suffix().
    base = ctx.events_dir / event_id
    return {
        "event": Path(f"{base}.json"),
        "claim": Path(f"{base}.claim"),
        "invoked": Path(f"{base}.invoked"),
        "done": Path(f"{base}.done"),
        "blocked": Path(f"{base}.blocked"),
        "recon": Path(f"{base}.recon-emitted"),
    }


def git_head(ctx: Ctx) -> str:
    result = ctx.runner(["git", "-C", str(ctx.repo), "rev-parse", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def emit_event(
    ctx: Ctx,
    event_id: str,
    watch_id: str,
    event_type: str,
    payload: dict,
    *,
    retry_of: str | None = None,
    recon_of: str | None = None,
    context: str | None = None,
    action: dict | None = None,
) -> bool:
    record = {
        "schema_version": 1,
        "event_id": event_id,
        "watch_id": watch_id,
        "event_type": event_type,
        "observed_at_utc": ctx.now_iso(),
        "source": {"node": socket.gethostname(), "pid": os.getpid()},
        "payload": payload,
        "head_at_event": git_head(ctx),
    }
    if retry_of:
        record["retry_of"] = retry_of
    if recon_of:
        record["recon_of"] = recon_of
    if context:
        record["context"] = context
    if action:
        # Snapshot routing before the watch is archived.  Event records are the
        # durable dispatch contract; live watch files are only condition state.
        record["action"] = action
    created = create_exclusive(
        event_paths(ctx, event_id)["event"], json.dumps(record, indent=2, sort_keys=True) + "\n"
    )
    if created:
        ctx.ledger(event_id, "event-emitted", f"type={event_type} watch={watch_id}")
    return created


def scan(ctx: Ctx) -> list[str]:
    """One poll pass; emits events for fired watches. Returns emitted event ids.

    EACH WATCH IS ISOLATED. Before 2026-08-11 `evaluate()` was called unguarded, so a single
    malformed watch aborted this loop, skipped the `_write_tick_receipt()` below it, and propagated
    out through `tick()` -- which meant dispatch, idle_guard, notify_guard and status_report_guard
    were all skipped as well. The whole waker then did nothing on that tick and on every tick after,
    and its only growing signal was `logs/cron-tick.log`, the one file the liveness rule tells you
    NOT to read for health. So the failure was silent in the direction that matters.

    The realistic malformation is NOT a corrupt file: `load_watches()` already suppresses
    `OSError`/`json.JSONDecodeError`, so unparseable JSON is skipped and harms nothing. It is a watch
    that is valid JSON with bad CONTENT -- an unknown `kind` (which `evaluate()` ends by raising on,
    deliberately), a missing `kind`, or missing `params` -- i.e. a watch armed under an older schema,
    or hand-edited in this text-file state tree.

    Errors are counted and surfaced rather than swallowed: the count goes into `last-tick.json` as
    `watch_errors`, ALWAYS present so that zero is distinguishable from written-by-an-older-version.
    A guard that hides its own firing is the defect one level along.
    """
    emitted: list[str] = []
    errors: list[dict] = []
    for watch in load_watches(ctx):
        if watch.get("state") != "armed":
            continue
        wid = watch.get("watch_id") or "<no-watch_id>"
        try:
            fired = evaluate(ctx, watch)
            if fired is None:
                continue
            event_type, payload = fired
            event_id = f"evt-{wid}"
            emit_event(
                ctx,
                event_id,
                wid,
                event_type,
                payload,
                context=(watch.get("action") or {}).get("context") or None,
                action=watch.get("action") or {"type": "root-resume"},
            )
            watch["state"] = "fired"
            watch["fired_at_utc"] = ctx.now_iso()
            save_watch(ctx, watch)
            emitted.append(event_id)
        except Exception as exc:  # noqa: BLE001 -- one bad watch must not silence every other one
            errors.append({"watch_id": wid, "error": f"{type(exc).__name__}: {exc}"})
            # Both writes below are individually guarded: nothing in the per-watch path may abort the
            # tick, INCLUDING the code that records that the per-watch path failed.
            with contextlib.suppress(Exception):
                ctx.ledger(f"evt-{wid}", "watch-evaluate-error", f"{type(exc).__name__}: {exc}")
            # Bump the existing `unreliable` counter so a repeatedly-failing watch is visible in
            # `watch-list` state and not only in the ledger. It is NOT disarmed: an exception here is
            # not necessarily permanent (a subprocess or filesystem hiccup raises too), and disarming
            # on one bad tick would silently retire a watch somebody is depending on -- the same
            # fail-open-into-silence this guard exists to end.
            with contextlib.suppress(Exception):
                watch["unreliable"] = int(watch.get("unreliable", 0)) + 1
                save_watch(ctx, watch)
    _write_tick_receipt(ctx, errors)
    return emitted


def _write_tick_receipt(ctx: Ctx, errors: list[dict] | None = None) -> None:
    """Record that a tick completed, and how cleanly.

    `watch_errors` is written UNCONDITIONALLY -- 0 when the pass was clean. An absent key would be
    indistinguishable from a receipt written before this field existed, which is the null-as-absent
    shape: a reader checking "no errors" would pass on a file that never looked.
    """
    errors = errors or []
    receipt = {
        "at_utc": ctx.now_iso(),
        "node": socket.gethostname(),
        "pid": os.getpid(),
        "watch_errors": len(errors),
    }
    if errors:
        receipt["watch_error_detail"] = errors
    agentctl.atomic_write_json(ctx.state_dir / "last-tick.json", receipt)


# ---------------------------------------------------------------------------
# Dispatch


# ---------------------------------------------------------------------------
# Control-plane assessment (read-only; consumed by `preflight --` from the CLI)
#
# On 2026-08-19 three controls failed together and every one of them was silent:
#   (1) scron job 56585597 -- the `wakerctl tick` job -- had been PENDING with
#       Priority=0, Reason="user env retrieval failed requeued held" and
#       StartTime=Unknown since 2026-08-17T15:05Z (Restarts=1869). wakerctl only
#       ever read the crontab TEXT (`read_scrontab()`), so it confirmed the
#       SCHEDULE and never asked Slurm whether the job that schedule creates was
#       runnable. Presence of a schedule is not execution of a schedule.
#   (2) watch `gate5-do-train-57266000-r2` was armed with params.tasks="1" while
#       array 57266000 has only task 0. `expand_spec` reads `tasks` as a task-id
#       SPEC, not a count, so the watch was armed on a task that does not exist:
#       build_snapshot -> overall=UNOBSERVED, unknown_tasks=[1], which routes to
#       unreliable_step() forever and can only ever reach `monitor-error`.
#   (3) the session that "verified" watch health used `grep -c '...armed'`, which
#       counts "disarmed" too. State comparisons here go through `watch_state()`
#       and match the WHOLE FIELD.
#
# Every function below is read-only and takes its Slurm access through
# `ctx.runner`, so all of it is unit-testable on a host with no Slurm. When it
# cannot reach Slurm it returns a `NO EVIDENCE:` line, never silence: a control
# that reports green because it could not run is the failure class above.

NO_EVIDENCE_PREFIX = "NO EVIDENCE"
CRON_QOS = "cron"
DEFAULT_CRON_STALE_MULTIPLIER = 6.0
# squeue prints these for "there is no start time", i.e. nothing is scheduled.
NO_START_TOKENS = {"", "N/A", "NONE", "UNKNOWN", "(NULL)"}
RUNNABLE_JOB_STATES = {
    "PENDING",
    "RUNNING",
    "COMPLETING",
    "CONFIGURING",
    "REQUEUED",
    "REQUEUE_FED",
    "RESIZING",
    "SUSPENDED",
}


def no_evidence(detail: str) -> str:
    return f"{NO_EVIDENCE_PREFIX}: {detail}"


def watch_state(watch: dict) -> str:
    """The watch's state as a WHOLE FIELD, for equality comparison only.

    Never test a watch state with a substring: "disarmed" contains "armed", and a
    `grep -c '<job>.*armed'` health check has already reported 2 armed watches on a
    job that had one disarmed and one armed (2026-08-19).
    """
    return str(watch.get("state") or "").strip()


def is_armed(watch: dict) -> bool:
    return watch_state(watch) == "armed"


def read_scrontab_lines(ctx: Ctx) -> tuple[list[str] | None, str]:
    """Like read_scrontab() but distinguishes "empty table" from "could not read".

    `read_scrontab()` returns [] on failure, which is indistinguishable from a user
    with no crontab -- the null-as-absent shape. Callers that assess health need
    those apart, so this returns None only when the query itself failed.
    """
    result = ctx.runner(["scrontab", "-l"])
    text = (result.stdout or "").strip()
    if result.returncode != 0:
        if "no crontab" in text.lower():
            return [], text[:200]
        return None, f"scrontab -l rc={result.returncode}: {text[:200]}"
    return (result.stdout or "").splitlines(), ""


def managed_block_lines(lines: list[str]) -> list[str]:
    """The contents of the wakerctl-managed block, markers excluded."""
    inside, block = False, []
    for line in lines:
        stripped = line.strip()
        if stripped == SCRON_BEGIN:
            inside = True
            continue
        if stripped == SCRON_END:
            inside = False
            continue
        if inside:
            block.append(line)
    return block


def minute_field_interval(field: str) -> int | None:
    """Minutes between two firings of a cron minute field, or None if unparseable.

    Handles the two forms this block is seen in: the `*/5` we write, and the
    `0,5,10,...` list Slurm echoes back in `CrontabSpec`.
    """
    field = field.strip()
    if field == "*":
        return 1
    if field.startswith("*/"):
        step = field[2:]
        return int(step) if step.isdigit() and int(step) > 0 else None
    parts = [part.strip() for part in field.split(",") if part.strip()]
    if not parts or not all(part.isdigit() for part in parts):
        return None
    values = sorted({int(part) for part in parts})
    if len(values) == 1:
        return 60
    gaps = [b - a for a, b in zip(values, values[1:])]
    gaps.append(60 - values[-1] + values[0])
    return min(gap for gap in gaps if gap > 0) or None


def cron_interval_minutes(lines: list[str]) -> int | None:
    for line in managed_block_lines(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) < 6:
            continue
        return minute_field_interval(fields[0])
    return None


def squeue_self_rows(ctx: Ctx) -> tuple[list[dict] | None, str]:
    """This user's queued jobs, or None when squeue could not be reached.

    REASON IS THE LAST FORMAT FIELD ON PURPOSE: it is the only one that can itself
    contain the '|' separator, so it is parsed as the remainder.
    """
    fields = ["%i", "%T", "%Q", "%S", "%q", "%j", "%r"]
    result = ctx.runner(["squeue", "--me", "-h", "-o", "|".join(fields)])
    if result.returncode != 0:
        return None, f"squeue rc={result.returncode}: {(result.stdout or '').strip()[:200]}"
    rows = []
    for raw in (result.stdout or "").splitlines():
        if not raw.strip():
            continue
        parts = raw.split("|", len(fields) - 1)
        if len(parts) < len(fields) - 1:
            continue
        parts.extend([""] * (len(fields) - len(parts)))
        rows.append(
            {
                "job_id": parts[0].strip(),
                "state": parts[1].strip().upper(),
                "priority": parts[2].strip(),
                "start_time": parts[3].strip(),
                "qos": parts[4].strip(),
                "name": parts[5].strip(),
                "reason": parts[6].strip(),
            }
        )
    return rows, ""


def _reason_tokens(reason: str) -> set[str]:
    cleaned = reason.lower()
    for character in "_,;:()":
        cleaned = cleaned.replace(character, " ")
    return set(cleaned.split())


def cron_job_problems(row: dict) -> list[str]:
    """Why this QOS=cron job cannot be relied on to run. Empty means runnable."""
    problems: list[str] = []
    label = f"cron job {row.get('job_id', '?')} (name={row.get('name', '?')!r})"
    state = row.get("state", "")
    reason = row.get("reason", "")
    if "held" in _reason_tokens(reason):
        problems.append(
            f"{label} is HELD: state={state} reason={reason!r}. The tick schedule exists "
            "and nothing executes it; save `scrontab -l`, reinstall the table, and verify "
            "that every unmanaged line survived (scrontab jobs cannot be released with scontrol)."
        )
    priority = row.get("priority", "")
    if priority.strip().lstrip("-").isdigit() and int(priority) == 0:
        problems.append(
            f"{label} has Priority=0, so Slurm will never schedule it: state={state} reason={reason!r}."
        )
    if state and state not in RUNNABLE_JOB_STATES:
        problems.append(f"{label} is in non-runnable state {state}: reason={reason!r}.")
    start = row.get("start_time", "").strip().upper()
    if state == "PENDING" and start in NO_START_TOKENS:
        # A healthy scron job is PENDING with its next cron slot as START_TIME.
        # No start time at all means no next firing is planned.
        problems.append(
            f"{label} is PENDING with no eligible start time (START_TIME={row.get('start_time', '')!r}): "
            f"reason={reason!r}."
        )
    return problems


def check_cron_job_runnable(ctx: Ctx, expect_job: bool = True) -> list[str]:
    """Ask SLURM -- not the crontab text -- whether the managed tick can run."""
    if not expect_job:
        return []
    rows, detail = squeue_self_rows(ctx)
    if rows is None:
        return [no_evidence(f"cannot assess whether the tick job is runnable: {detail}")]
    cron_rows = [row for row in rows if row["qos"] == CRON_QOS]  # whole field, not substring
    python = ctx.python_bin()
    named = [row for row in cron_rows if row["name"] in {python, Path(python).name}]
    candidates = named or cron_rows
    if not candidates:
        return [
            "the managed scrontab block is installed but Slurm shows no QOS=cron job for this "
            "user: the schedule exists and nothing executes it"
        ]
    problems: list[str] = []
    for row in candidates:
        problems.extend(cron_job_problems(row))
    return problems


def check_tick_freshness(ctx: Ctx, interval_minutes: int | None) -> list[str]:
    """Staleness of last-tick.json -- the instrument-independent liveness signal.

    This is deliberately not tied to any Slurm Reason string: whatever wedges the
    ticker next time, the receipt stops advancing, and that is what this measures.
    """
    path = ctx.state_dir / "last-tick.json"
    if interval_minutes is None:
        return [no_evidence(f"tick interval unknown, so staleness of {path} cannot be bounded")]
    multiplier = float(ctx.config.get("cron_stale_multiplier", DEFAULT_CRON_STALE_MULTIPLIER))
    limit = interval_minutes * 60.0 * multiplier
    if not path.exists():
        return [f"no tick receipt at {path}: no tick has ever completed against this state dir"]
    try:
        receipt = read_json(path)
        age = ctx.now() - parse_utc(str(receipt["at_utc"]))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return [f"unreadable tick receipt {path}: {type(exc).__name__}: {exc}"]
    if age > limit:
        return [
            f"the ticker is STALE: last tick {receipt.get('at_utc')} is {age / 60:.0f} min old, "
            f"past the {limit / 60:.0f} min bound ({interval_minutes}m interval x {multiplier:g}). "
            "No watch has been evaluated since then."
        ]
    return []


def check_cron_ticker(ctx: Ctx) -> list[str]:
    problems: list[str] = []
    lines, detail = read_scrontab_lines(ctx)
    interval, expect_job = None, False
    if lines is None:
        problems.append(no_evidence(f"cannot read the scrontab: {detail}"))
    elif not managed_block_lines(lines):
        problems.append(
            "the wakerctl-managed scrontab block is absent: nothing schedules `wakerctl tick`"
        )
    else:
        expect_job = True
        interval = cron_interval_minutes(lines)
        if interval is None:
            problems.append(
                "the managed scrontab block has no parseable schedule line; tick staleness "
                "cannot be bounded from it"
            )
    problems.extend(check_cron_job_runnable(ctx, expect_job=expect_job))
    problems.extend(check_tick_freshness(ctx, interval))
    return problems


def watch_subject_tasks(watch: dict) -> tuple[str, list[int]]:
    """(as-written spec, expanded task ids) for a Slurm-subject watch.

    `params.tasks` is a task-id SPEC and never a count: expand_spec("1") == [1],
    which is task index 1, not "one task". That reading is exactly how
    gate5-do-train-57266000-r2 came to watch a task its array does not have.
    """
    params = watch.get("params") or {}
    if watch.get("kind") == "slurm-array":
        raw = str(params.get("tasks", ""))
        return raw, slurm_array_status.expand_spec(raw)
    # A non-array job is probed as synthetic task 0, the same convention
    # slurm_array_status.task_ids() uses.
    return "(non-array)", [0]


def watch_subject_problems(ctx: Ctx, watch: dict) -> list[str]:
    """Is this armed watch's subject OBSERVABLE? No existing control asks this."""
    kind = watch.get("kind")
    if kind not in {"slurm-job", "slurm-array"}:
        return []
    wid = watch.get("watch_id") or "<no-watch_id>"
    params = watch.get("params") or {}
    job_id = str(params.get("job_id", "")).strip()
    if not job_id:
        return [f"watch {wid}: armed {kind} watch has no params.job_id"]
    try:
        raw, tasks = watch_subject_tasks(watch)
    except ValueError as exc:
        return [f"watch {wid}: params.tasks={params.get('tasks')!r} is not a valid task spec: {exc}"]
    if not tasks:
        return [f"watch {wid}: params.tasks={raw!r} expands to no tasks; the watch has no subject"]
    snapshot = slurm_array_status.build_snapshot(
        job_id, tasks, runner=lambda argv: _text_runner(ctx, argv)
    )
    if snapshot.get("observer_errors"):
        return [
            no_evidence(
                f"watch {wid}: cannot observe job {job_id}: "
                + "; ".join(str(item) for item in snapshot["observer_errors"])
            )
        ]
    unknown = snapshot.get("unknown_tasks") or []
    if unknown:
        return [
            f"watch {wid} ({kind}) is armed on a subject that DOES NOT EXIST: job {job_id} "
            f"requested tasks {raw!r} -> {tasks}, and Slurm has no {unknown}. overall="
            f"{snapshot.get('overall')}. This watch can never report completion; it can only "
            "count unreliable ticks up to max_unreliable and emit monitor-error."
        ]
    return []


def check_armed_watch_subjects(ctx: Ctx) -> list[str]:
    problems: list[str] = []
    for watch in load_watches(ctx):
        if not is_armed(watch):  # whole-field equality; "disarmed" must not match
            continue
        wid = watch.get("watch_id") or "<no-watch_id>"
        try:
            problems.extend(watch_subject_problems(ctx, watch))
        except Exception as exc:  # noqa: BLE001 -- one unassessable watch must not hide the rest
            problems.append(
                no_evidence(f"watch {wid}: subject check raised {type(exc).__name__}: {exc}")
            )
    return problems


def slurm_known_tasks(ctx: Ctx, job_id: str) -> tuple[set[int] | None, str]:
    """Task ids Slurm actually knows for job_id; None when neither query worked.

    An EMPTY set is a real answer ("Slurm has no record of this job"), distinct from
    None ("we could not look"), and the caller must treat them differently.
    """
    known: set[int] = set()
    saw_any_query = False
    for argv in (
        ["squeue", "-h", "-r", "-j", job_id, "-o", "%i"],
        ["sacct", "-X", "-j", job_id, "-n", "-P", "-o", "JobID"],
    ):
        result = ctx.runner(argv)
        if result.returncode != 0:
            continue
        saw_any_query = True
        for raw in (result.stdout or "").splitlines():
            # Take the first field: these two queries ask for JobID only, but a
            # caller-supplied runner (or a future --format) may carry more columns,
            # and a whole line would silently parse as "no tasks known".
            token = raw.strip().split("|")[0].strip()
            if not token:
                continue
            with contextlib.suppress(ValueError):
                known.update(slurm_array_status.task_ids(job_id, token))
    if not saw_any_query:
        return None, "neither squeue nor sacct could be queried"
    return known, ""


def check_array_spec_against_slurm(ctx: Ctx, watch: dict) -> None:
    """Reject at ADD time an array watch whose tasks the array does not have.

    Rejects only on POSITIVE evidence: Slurm must know some task of this job and not
    the requested ones. "Job invisible" and "Slurm unreachable" both arm with a
    NO EVIDENCE note on stderr rather than blocking -- a watch is often armed for a
    job whose accounting record has not appeared yet, and preflight remains the net.
    """
    if watch.get("kind") != "slurm-array":
        return
    job_id = str((watch.get("params") or {}).get("job_id", "")).strip()
    _, tasks = watch_subject_tasks(watch)
    known, detail = slurm_known_tasks(ctx, job_id)
    if known is None or not known:
        suffix = f" ({detail})" if detail else ""
        print(
            "[watch-add] "
            + no_evidence(
                f"job {job_id} is not visible to Slurm from here{suffix}; "
                f"tasks={sorted(tasks)} were NOT verified against the array"
            ),
            file=sys.stderr,
        )
        return
    missing = sorted(set(tasks) - known)
    if missing:
        raise WakerError(
            f"array {job_id} has no task {missing} (Slurm knows {sorted(known)}); "
            f"params.tasks is a task-id spec, not a count -- a watch on a task the array "
            f"does not have can never fire"
        )


def preflight(ctx: Ctx, quiet: bool = False, control_plane: bool = False) -> list[str]:
    """Environment checks, plus control-plane checks when explicitly requested.

    `control_plane` DEFAULTS OFF because dispatch_one() uses this function as a
    fail-closed gate: making a dispatch depend on squeue reachability or on some
    unrelated watch's subject would strand real events, and would add a Slurm round
    trip per watch to every dispatch. The CLI turns it on; the dispatch path is
    byte-for-byte unchanged.
    """
    problems: list[str] = []
    python = ctx.python_bin()
    if not Path(python).is_file() or not os.access(python, os.X_OK):
        problems.append(f"python missing or not executable: {python!r}")
    binary = None
    try:
        root = ctx.root()
        profile = agentctl.get_profile(ctx.profiles(), root.get("profile", "codex-personal"))
        provider = profile.get("provider")
        binary = ctx.codex_bin() if provider == "codex" else ctx.claude_bin()
        if not binary or not Path(binary).is_file() or not os.access(binary, os.X_OK):
            problems.append(f"root {provider} binary missing or not executable: {binary!r}")
        home = Path(agentctl.expand_path(profile["home"]))
        if not home.is_dir():
            problems.append(f"root provider home missing: {home}")
    except (WakerError, agentctl.AgentCtlError) as exc:
        problems.append(str(exc))
    if control_plane:
        # NO EVIDENCE lines stay in `problems` on purpose: an unreachable Slurm must
        # make this command non-zero, because "could not look" printed as PASS is the
        # exact shape of the failures this section exists to end.
        problems.extend(check_cron_ticker(ctx))
        problems.extend(check_armed_watch_subjects(ctx))
    if not quiet:
        for problem in problems:
            print(f"[preflight] {problem}", file=sys.stderr)
        if not problems:
            scope = "checked" if control_plane else "NOT CHECKED (--env-only)"
            print(f"[preflight] PASS root={binary} python={python} control-plane={scope}")
    return problems


def build_root_resume(ctx: Ctx, event: dict) -> tuple[list[str], dict]:
    """Build the resume command for whichever provider currently holds root.

    The root is normally the canonical Codex thread; during a Codex capacity
    conservation window it may be an interim Claude session (PORTING.md §6d).
    Binary paths are always absolute (F2) and the provider home is explicit.
    """
    root = ctx.root()
    profile = agentctl.get_profile(ctx.profiles(), root.get("profile", "codex-personal"))
    provider = profile.get("provider")
    prompt = render_prompt(ctx, event)
    if provider == "codex":
        env = ctx.base_env()
        env["CODEX_HOME"] = agentctl.expand_path(profile["home"])
        codex = ctx.codex_bin()
        if not codex:
            raise WakerError("codex binary unresolved")
        command = [codex, "exec", "resume"]
        agentctl.add_codex_options(command, profile)
        for feature in root.get("disable_features", ["goals"]):
            command.extend(["--disable", feature])
        command.extend(["--skip-git-repo-check", root["thread_id"], prompt])
        return command, env
    if provider == "claude":
        command, env = agentctl.build_resume_command(profile, prompt, root["thread_id"])
        claude = ctx.claude_bin()
        if not claude:
            raise WakerError("claude binary unresolved")
        command[0] = claude
        for key, value in ctx.base_env().items():
            env.setdefault(key, value)
        env["PATH"] = ctx.base_env()["PATH"]
        return command, env
    raise WakerError(f"root resume unsupported for provider {provider!r}")


def render_prompt(ctx: Ctx, event: dict) -> str:
    preamble = ctx.config.get("prompt_preamble") or DEFAULT_PREAMBLE
    event_path = event_paths(ctx, event["event_id"])["event"]
    with contextlib.suppress(ValueError):
        event_path = event_path.relative_to(ctx.repo)
    text = preamble.format(
        watch_id=event.get("watch_id", "unknown"),
        event_type=event.get("event_type", "unknown"),
        event_path=str(event_path),
    )
    context = event.get("context") or watch_context(ctx, event)
    if event.get("recon_of"):
        text += (
            "\nThis is a reconciliation event: an earlier dispatch invoked a resume for "
            f"{event['recon_of']} but its outcome was never recorded. Verify from the ledger "
            "and provider logs whether that turn ran before taking any action."
        )
    if event.get("retry_of"):
        text += f"\nThis is retry {event['event_id'].rsplit('.r', 1)[-1]} of {event['retry_of']}."
    if context:
        text += "\n\nCampaign context for this watch: " + context
    return text


def watch_context(ctx: Ctx, event: dict) -> str:
    action = event.get("action")
    if isinstance(action, dict):
        return str(action.get("context") or "")
    path = ctx.watches_dir / f"{event.get('watch_id', '')}.json"
    if path.is_file():
        with contextlib.suppress(OSError, json.JSONDecodeError):
            return read_json(path).get("action", {}).get("context", "")
    return ""


def event_action(ctx: Ctx, event: dict) -> dict:
    """Resolve routing from the immutable event, with legacy-watch fallback."""
    action = event.get("action")
    if isinstance(action, dict) and action.get("type"):
        return action
    watch_file = ctx.watches_dir / f"{event.get('watch_id', '')}.json"
    if watch_file.is_file():
        with contextlib.suppress(OSError, json.JSONDecodeError):
            legacy = read_json(watch_file).get("action")
            if isinstance(legacy, dict) and legacy.get("type"):
                return legacy
    return {"type": "root-resume"}


def run_action(ctx: Ctx, event: dict) -> int:
    action = event_action(ctx, event)
    log_path = ctx.logs_dir / f"{event['event_id']}.log"
    ctx.logs_dir.mkdir(parents=True, exist_ok=True)

    if action.get("type") == "role-send":
        command = [
            ctx.python_bin(),
            str(HERE / "agentctl.py"),
            "send",
            "--role",
            action["role"],
            "--prompt-file",
            str(action["prompt_file"]),
        ]
        env = ctx.base_env()
    elif action.get("type") == "command":
        command = list(action["argv"])
        env = ctx.base_env()
    else:
        command, env = build_root_resume(ctx, event)

    result = ctx.runner(command, env=env, cwd=ctx.repo)
    redacted = command[:-1] + ["<prompt>"] if action.get("type") not in {"role-send", "command"} else command
    with open(log_path, "a") as handle:
        handle.write(f"=== {ctx.now_iso()} rc={result.returncode} argv={redacted}\n")
        handle.write(result.stdout or "")
        handle.write("\n")
    return result.returncode


def dispatch(ctx: Ctx) -> list[tuple[str, str]]:
    """Claim and act on spooled events serially. Returns (event_id, outcome) pairs."""
    outcomes: list[tuple[str, str]] = []
    if not ctx.events_dir.is_dir():
        return outcomes
    lease = int(ctx.config.get("claim_lease_seconds", 900))
    grace = int(ctx.config.get("invoke_grace_seconds", 7200))
    for event_file in sorted(ctx.events_dir.glob("*.json")):
        event_id = event_file.stem
        paths = event_paths(ctx, event_id)
        if paths["done"].exists():
            continue
        if paths["invoked"].exists():
            outcomes.append((event_id, maybe_reconcile(ctx, event_id, grace)))
            continue
        if not acquire_claim(ctx, paths["claim"], lease, guard=lambda p=paths: not p["invoked"].exists()):
            outcomes.append((event_id, "claim-held"))
            continue
        if not acquire_claim(ctx, ctx.resume_mutex, lease, guard=lambda: True):
            release_claim(paths["claim"])
            outcomes.append((event_id, "mutex-held"))
            continue
        try:
            outcomes.append((event_id, dispatch_one(ctx, event_id, paths)))
        finally:
            release_claim(ctx.resume_mutex)
    return outcomes


def dispatch_one(ctx: Ctx, event_id: str, paths: dict[str, Path]) -> str:
    problems = preflight(ctx, quiet=True)
    event = read_json(paths["event"])
    if not problems:
        problems.extend(capacity_problems(ctx, event))
    if problems:
        # Fail closed without consuming the event: no invocation happened, so a
        # later tick (possibly after a human repairs the environment) retries.
        paths["blocked"].parent.mkdir(parents=True, exist_ok=True)
        agentctl.atomic_write_json(
            paths["blocked"],
            {"at_utc": ctx.now_iso(), "owner": owner_string(), "problems": problems},
        )
        ctx.ledger(event_id, "dispatch-blocked", "; ".join(problems))
        release_claim(paths["claim"])
        return "blocked"
    if not create_exclusive(
        paths["invoked"],
        json.dumps({"at_utc": ctx.now_iso(), "owner": owner_string()}, sort_keys=True) + "\n",
    ):
        return "invoked-race"
    ctx.ledger(event_id, "invoked", f"type={event.get('event_type')}")
    # A Slurm wall or shutdown delivers SIGTERM before SIGKILL. Convert it
    # into a recorded failure + bounded retry so the event does not strand
    # invoked-without-outcome until the reconciliation grace expires
    # (post-deployment incident 2026-07-19 16:30 UTC, see WAKER.md).
    old_handler = None
    in_main_thread = threading.current_thread() is threading.main_thread()
    if in_main_thread:

        def _terminated(signum, frame):
            raise ActionTerminated(f"signal {signum}")

        old_handler = signal.signal(signal.SIGTERM, _terminated)
    try:
        rc = run_action(ctx, event)
    except ActionTerminated as exc:
        ctx.ledger(event_id, "action-terminated", str(exc))
        rc = 143
    except (WakerError, agentctl.AgentCtlError, OSError) as exc:
        ctx.ledger(event_id, "action-exception", str(exc))
        rc = -1
    finally:
        if in_main_thread and old_handler is not None:
            signal.signal(signal.SIGTERM, old_handler)
    outcome = "resumed" if rc == 0 else "failed"
    agentctl.atomic_write_json(
        paths["done"],
        {"at_utc": ctx.now_iso(), "owner": owner_string(), "rc": rc, "outcome": outcome},
    )
    ctx.ledger(event_id, "done", f"rc={rc} outcome={outcome}")
    with contextlib.suppress(FileNotFoundError):
        os.unlink(paths["blocked"])
    if rc != 0:
        schedule_retry(ctx, event, event_id)
    with contextlib.suppress(FileNotFoundError):
        archive_watch(ctx, str(event.get("watch_id", "")))
    return outcome


def capacity_problems(ctx: Ctx, event: dict) -> list[str]:
    """Fail closed before a root LLM invocation when its account is unavailable.

    Command and role-send actions keep their own provider/session policy.  This
    check never swaps an existing root thread to a different account.
    """
    if ctx.config.get("capacity_guard") is not True:
        return []
    action = event_action(ctx, event)
    if action.get("type") != "root-resume":
        return []
    profile_name = str(ctx.root().get("profile", "codex-personal"))
    command = [
        ctx.python_bin(),
        str(HERE / "usagectl.py"),
        "check",
        "--profile",
        profile_name,
        "--json",
    ]
    result = ctx.runner(command, env=ctx.base_env(), cwd=ctx.repo)
    if result.returncode == 0:
        return []
    detail = (result.stdout or "").strip()[-1000:]
    return [
        f"root profile {profile_name} has no measured READY/LOW capacity; "
        f"the event remains unconsumed and will retry after reset/auth recovery. {detail}"
    ]


def schedule_retry(ctx: Ctx, event: dict, event_id: str) -> None:
    base_id = event.get("retry_of") or event_id
    attempt = 1
    if ".r" in event_id:
        with contextlib.suppress(ValueError):
            attempt = int(event_id.rsplit(".r", 1)[1]) + 1
    max_retries = int(ctx.config.get("max_retries_default", 2))
    watch = {}
    watch_file = ctx.watches_dir / f"{event.get('watch_id', '')}.json"
    if watch_file.is_file():
        with contextlib.suppress(OSError, json.JSONDecodeError):
            watch = read_json(watch_file)
    max_retries = int(watch.get("max_retries", max_retries))
    if attempt > max_retries:
        ctx.ledger(base_id, "retries-exhausted", f"attempts={attempt - 1}")
        notify(
            ctx,
            f"retries-exhausted-{base_id}",
            "[MINERvA waker] Resume retries exhausted",
            f"Event {base_id} failed {attempt - 1} retries; the campaign will not "
            f"self-resume for it. Inspect state/waker/logs/{base_id}*.log and the "
            "ledger, then emit a manual event or send a bounded turn.",
        )
        return
    retry_id = f"{base_id}.r{attempt}"
    emit_event(
        ctx,
        retry_id,
        event.get("watch_id", "unknown"),
        event.get("event_type", "unknown"),
        event.get("payload", {}),
        retry_of=base_id,
        context=event.get("context"),
        action=event_action(ctx, event),
    )


def maybe_reconcile(ctx: Ctx, event_id: str, grace: int) -> str:
    paths = event_paths(ctx, event_id)
    try:
        invoked_age = ctx.now() - paths["invoked"].stat().st_mtime
    except OSError:
        return "invoked-unreadable"
    if invoked_age <= grace:
        return "awaiting-outcome"
    if not create_exclusive(paths["recon"], utc_now() + "\n"):
        return "recon-already-emitted"
    event = read_json(paths["event"])
    recon_id = f"{event_id}.recon"
    emit_event(
        ctx,
        recon_id,
        event.get("watch_id", "unknown"),
        "resume-outcome-unknown",
        {"original_event": event_id},
        recon_of=event_id,
        context=event.get("context"),
        action=event_action(ctx, event),
    )
    # The recon event supersedes the original: give the original a terminal
    # disposition so it is never re-dispatched and its record is complete.
    agentctl.atomic_write_json(
        paths["done"],
        {"at_utc": ctx.now_iso(), "owner": owner_string(), "rc": None, "outcome": "reconciled"},
    )
    ctx.ledger(event_id, "recon-emitted", f"invoked_age={int(invoked_age)}s")
    with contextlib.suppress(FileNotFoundError):
        archive_watch(ctx, str(event.get("watch_id", "")))
    return "recon-emitted"


def blocked_on_user_path(ctx: Ctx) -> Path:
    return ctx.state_dir / "BLOCKED-ON-USER.json"


def notify(ctx: Ctx, key: str, subject: str, body: str) -> bool:
    """Send one user notification per key via the configured command.

    The marker is written only after a successful send so transient transport
    failures retry on later ticks; a rare crash between send and marker can
    duplicate a notification, which is harmless.
    """
    command = ctx.config.get("notify_command")
    if not command:
        return False
    marker = ctx.state_dir / "notified" / f"{key}.sent"
    if marker.exists():
        return False
    argv = [
        str(part).replace("{subject}", subject).replace("{key}", key)
        for part in command
    ]
    result = ctx.runner(argv, env=ctx.base_env(), cwd=ctx.repo, input_text=body)
    if result.returncode != 0:
        ctx.ledger(key, "notify-failed", f"rc={result.returncode}")
        return False
    create_exclusive(marker, ctx.now_iso() + "\n")
    ctx.ledger(key, "notified", subject)
    return True


ANSWER_POINTER = (
    "\n\nHow to answer: docs/orchestration/WAKER.md section 'Answering a "
    "BLOCKED-ON-USER stop' (read the ask, delete the file, emit your decision "
    "with wakerctl)."
)


def notify_guard(ctx: Ctx) -> list[str]:
    """Push needs-your-input conditions to the user, exactly once each."""
    sent: list[str] = []
    blocked = blocked_on_user_path(ctx)
    if blocked.exists():
        stamp = int(blocked.stat().st_mtime)
        with contextlib.suppress(OSError):
            body = blocked.read_text()[:4000] + ANSWER_POINTER
            if notify(
                ctx,
                f"blocked-on-user-{stamp}",
                "[MINERvA waker] Orchestrator needs your decision",
                body,
            ):
                sent.append(f"blocked-on-user-{stamp}")
    if ctx.events_dir.is_dir():
        for marker in ctx.events_dir.glob("*.blocked"):
            event_id = marker.name[: -len(".blocked")]
            if event_paths(ctx, event_id)["done"].exists():
                continue
            with contextlib.suppress(OSError):
                if notify(
                    ctx,
                    f"env-blocked-{event_id}",
                    "[MINERvA waker] Dispatch blocked by environment",
                    f"Event {event_id} cannot dispatch:\n{marker.read_text()[:4000]}",
                ):
                    sent.append(f"env-blocked-{event_id}")
    queue_status_command = ctx.config.get("campaign_queue_status_command")
    if queue_status_command:
        result = ctx.runner(list(queue_status_command), env=ctx.base_env(), cwd=ctx.repo)
        if result.returncode == 0:
            with contextlib.suppress(json.JSONDecodeError, AttributeError):
                for item in json.loads(result.stdout).get("items", []):
                    if item.get("state") != "staged":
                        continue
                    item_id = str(item.get("id", "unknown")).replace("\n", " ")[:100]
                    item_digest = str(item.get("digest", ""))
                    stable = hashlib.sha256(
                        f"{item_id}:{item_digest}".encode("utf-8")
                    ).hexdigest()[:16]
                    key = f"campaign-approval-{stable}"
                    if notify(
                        ctx,
                        key,
                        f"[MINERvA queue] Approval requested: {item_id}",
                        "A deterministic campaign command is staged and will not run "
                        "without your approval. From Termius:\n"
                        "cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration\n"
                        f"/usr/bin/python3.11 campaignctl.py show --id {item_id}\n"
                        f"proposal digest: {item_digest}",
                    ):
                        sent.append(key)
    return sent


def campaign_is_idle(ctx: Ctx) -> bool:
    """No armed watch and every spooled event has a terminal disposition.

    The idle guard's own events are excluded so that firing the guard does
    not reset its one-nudge-per-episode state.
    """
    for watch in load_watches(ctx):
        if watch.get("state") == "armed":
            return False
    if ctx.events_dir.is_dir():
        for event_file in ctx.events_dir.glob("*.json"):
            if event_file.stem.startswith("evt-idle-"):
                continue
            if not event_paths(ctx, event_file.stem)["done"].exists():
                return False
    return True


def idle_guard(ctx: Ctx) -> str | None:
    """Emit one campaign-idle wake per idle episode (2026-07-19 stall fix).

    A campaign that ends a turn with nothing armed would otherwise wait
    silently forever. The guard resumes the root once so it either arms the
    next dependency-ready action or declares BLOCKED-ON-USER; the declaration
    (or any newly armed watch) silences the guard. Deleting the declaration
    re-enables it, which is the user's lever to wake the campaign after
    answering.
    """
    threshold = int(ctx.config.get("idle_guard_ticks", 3))
    if threshold <= 0:
        return None
    state_path = ctx.state_dir / "idle-state.json"
    state = {"idle_ticks": 0, "fired_event": None}
    if state_path.is_file():
        with contextlib.suppress(OSError, json.JSONDecodeError):
            state.update(read_json(state_path))
    if not campaign_is_idle(ctx):
        agentctl.atomic_write_json(state_path, {"idle_ticks": 0, "fired_event": None})
        return None
    if blocked_on_user_path(ctx).exists():
        # Acknowledged stop: quiet is intentional until the user answers.
        agentctl.atomic_write_json(state_path, {"idle_ticks": 0, "fired_event": None})
        return None
    state["idle_ticks"] = int(state.get("idle_ticks", 0)) + 1
    fired = None
    if state["idle_ticks"] >= threshold and not state.get("fired_event"):
        stamp = dt.datetime.fromtimestamp(ctx.now(), tz=dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        event_id = f"evt-idle-{stamp}"
        emit_event(
            ctx,
            event_id,
            "idle-guard",
            "campaign-idle",
            {"idle_ticks": state["idle_ticks"]},
            context=(
                "The campaign has no armed watch, no pending event, and no "
                "BLOCKED-ON-USER declaration: it ended without continuation. "
                "Either arm wakerctl watches for the next dependency-ready "
                "campaign action and proceed with it now, or write and commit "
                "docs/orchestration/state/waker/BLOCKED-ON-USER.json stating "
                "exactly which user decision is required, then stop."
            ),
        )
        state["fired_event"] = event_id
        fired = event_id
    agentctl.atomic_write_json(state_path, state)
    return fired


def compose_status_report(ctx: Ctx) -> tuple[str, str]:
    """Build a concise, action-oriented digest from live machine state."""
    report = status(ctx)
    armed = [watch for watch in report["watches"] if watch.get("state") == "armed"]
    live_events = [
        event for event in report["events"]
        if event.get("state") in {"new", "claimed", "invoked", "blocked"}
    ]

    counts = {
        "staged": 0,
        "approved": 0,
        "failed": 0,
        "stale": 0,
        "outcome-unknown": 0,
        "succeeded": 0,
        "revoked": 0,
    }
    queue_evidence = "not-configured"
    queue_status_command = ctx.config.get("campaign_queue_status_command")
    if queue_status_command:
        queue_evidence = "unavailable"
        queued = ctx.runner(list(queue_status_command), env=ctx.base_env(), cwd=ctx.repo)
        if queued.returncode == 0:
            with contextlib.suppress(json.JSONDecodeError, AttributeError, TypeError):
                measured = json.loads(queued.stdout).get("counts", {})
                for key in counts:
                    counts[key] = int(measured.get(key, 0) or 0)
                queue_evidence = "measured"

    scheduler = ctx.runner(
        ["squeue", "-u", os.environ.get("USER", "josephrb"), "-h", "-r", "-o", "%i|%T|%j"]
    )
    compute_rows: list[tuple[str, str, str]] = []
    ticker_rows = 0
    scheduler_evidence = "unavailable"
    if scheduler.returncode == 0:
        scheduler_evidence = "measured"
        for raw in scheduler.stdout.splitlines():
            fields = raw.split("|", 2)
            if len(fields) != 3:
                continue
            job_id, state, name = (field.strip() for field in fields)
            if name == ctx.python_bin():
                ticker_rows += 1
            else:
                compute_rows.append((job_id, state, name))
    compute_states = Counter(row[1] for row in compute_rows)
    compute_names = Counter(row[2] for row in compute_rows)

    last_tick = report.get("last_tick") or {}
    tick_at = last_tick.get("at_utc")
    tick_age = None
    if isinstance(tick_at, str):
        with contextlib.suppress(ValueError):
            tick_age = max(0, int(ctx.now() - parse_utc(tick_at)))
    if tick_age is None:
        ticker_text = "no completed tick receipt"
    else:
        ticker_text = (
            f"{tick_age // 60}m {tick_age % 60}s ago at {tick_at} "
            f"on {last_tick.get('node', '?')}; watch_errors={last_tick.get('watch_errors', '?')}"
        )

    queue_attention = counts["outcome-unknown"]
    queue_terminal_failures = counts["failed"] + counts["stale"]
    blocked_events = sum(1 for event in live_events if event.get("state") == "blocked")
    action_parts = []
    if report["blocked_on_user"]:
        action_parts.append("a user decision is required")
    if counts["staged"]:
        action_parts.append(f"review {counts['staged']} staged queue item(s)")
    if queue_attention:
        action_parts.append(f"inspect {queue_attention} uncertain queue outcome(s)")
    if queue_evidence == "unavailable":
        action_parts.append("inspect queue status availability")
    if scheduler_evidence == "unavailable":
        action_parts.append("inspect scheduler availability")
    if blocked_events:
        action_parts.append(f"inspect {blocked_events} blocked waker event(s)")
    ticker_stale = tick_age is None or tick_age > 15 * 60
    if ticker_stale:
        action_parts.append("inspect ticker freshness")

    working = bool(compute_rows or armed or live_events or counts["approved"])
    if action_parts:
        headline = "ACTION REQUIRED — " + "; ".join(action_parts)
    elif working:
        headline = "WORKING — no action required"
    else:
        headline = "HEALTHY — quiet, no action required"

    lines = [f"MINERvA operator summary ({report['observed_at_utc']}): {headline}", ""]
    lines.append("Action required: " + ("; ".join(action_parts) if action_parts else "none"))
    if queue_evidence == "measured":
        lines.append(
            "Queue: "
            f"staged={counts['staged']}, approved={counts['approved']}, "
            f"attention={queue_attention}, terminal_failures={queue_terminal_failures}, "
            f"completed={counts['succeeded']}"
        )
    else:
        lines.append("Queue: NO EVIDENCE (status command unavailable)")
    if scheduler_evidence == "measured":
        state_text = ", ".join(f"{key}={value}" for key, value in sorted(compute_states.items()))
        lines.append(f"Compute: {state_text or 'none'}")
        if compute_names:
            name_text = ", ".join(f"{key}={value}" for key, value in compute_names.most_common(5))
            lines.append(f"Compute names: {name_text}")
        lines.append(f"Ticker scheduler row: {'present' if ticker_rows else 'not visible'}")
    else:
        lines.append("Compute: NO EVIDENCE (squeue unavailable)")
    lines.append(f"Armed watches: {len(armed)}")
    for watch in armed[:5]:
        lines.append(f"  {watch['watch_id']} ({watch['kind']})")
    lines.append(f"Live waker events: {len(live_events)}")
    for event in live_events[:5]:
        lines.append(f"  {event['event_id']} ({event['state']})")
    lines.append(f"Last ticker: {ticker_text}")
    idle_threshold = int(ctx.config.get("idle_guard_ticks", 3))
    if report["campaign_idle"]:
        if idle_threshold <= 0:
            lines.append("Orchestrator: quiet; automatic idle resume is disabled")
        else:
            lines.append(f"Orchestrator: quiet; idle guard threshold={idle_threshold} ticks")
    else:
        lines.append("Orchestrator: active")
    closed_watches = len(report["watches"]) - len(armed)
    closed_events = len(report["events"]) - len(live_events)
    lines.append(f"Historical records omitted: {closed_watches} closed watches, {closed_events} terminal events")
    lines.append("")
    lines.append("Termius commands:")
    lines.append("  cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration")
    lines.append("  /usr/bin/python3.11 campaignctl.py list")
    lines.append("  /usr/bin/python3.11 wakerctl.py status")
    lines.append("Guide: docs/orchestration/OPERATOR-GUIDE.md")
    return f"[MINERvA waker] {headline}", "\n".join(lines)


def status_report_guard(ctx: Ctx) -> str | None:
    """Send a digest once per interval bucket; zero LLM involvement.

    The bucketed notify key dedupes across concurrent tickers on different
    nodes, and pins sends to fixed epoch boundaries (00/06/12/18 UTC for the
    default 21600 s).
    """
    interval = int(ctx.config.get("status_report_interval_seconds", 0) or 0)
    if interval <= 0 or not ctx.config.get("notify_command"):
        return None
    key = f"status-{int(ctx.now() // interval)}"
    if (ctx.state_dir / "notified" / f"{key}.sent").exists():
        return None
    subject, body = compose_status_report(ctx)
    return key if notify(ctx, key, subject, body) else None


def heartbeat_guard(ctx: Ctx) -> bool | None:
    """Ping an optional external dead-man monitor after a deterministic tick."""
    command = ctx.config.get("heartbeat_command")
    if not command:
        return None
    result = ctx.runner(list(command), env=ctx.base_env(), cwd=ctx.repo)
    if result.returncode != 0:
        ctx.ledger("heartbeat", "heartbeat-failed", f"rc={result.returncode}")
        return False
    return True


def campaign_queue_guard(ctx: Ctx) -> dict | None:
    """Run at most one already-approved deterministic queue item.

    This is deliberately separate from dispatch(): queue entries cannot resume
    or prompt an LLM, and campaignctl itself enforces interactive approval,
    exact digests, file bindings, no shell, and exactly-once claims.
    """
    command = ctx.config.get("campaign_queue_command")
    if not command:
        return None
    result = ctx.runner(list(command), env=ctx.base_env(), cwd=ctx.repo)
    output = (result.stdout or "").strip()
    try:
        value = json.loads(output) if output else {"status": "unknown"}
    except json.JSONDecodeError:
        value = {"status": "invalid-output", "output": output[:1000]}
    value["returncode"] = result.returncode
    if result.returncode != 0:
        stable = hashlib.sha256(output.encode("utf-8")).hexdigest()[:16]
        key = f"campaign-queue-{stable}"
        ctx.ledger("campaign-queue", "queue-failed", f"rc={result.returncode} {output[:500]}")
        notify(
            ctx,
            key,
            "[MINERvA queue] Approved command needs attention",
            f"campaignctl run-ready returned rc={result.returncode}:\n{output[:4000]}",
        )
    return value


def tick(ctx: Ctx) -> dict:
    emitted = scan(ctx)
    outcomes = dispatch(ctx)
    queue_result = campaign_queue_guard(ctx)
    idle_event = idle_guard(ctx)
    if idle_event:
        emitted = emitted + [idle_event]
    notified = notify_guard(ctx)
    report_key = status_report_guard(ctx)
    if report_key:
        notified = notified + [report_key]
    result = {"emitted": emitted, "dispatch": outcomes}
    if queue_result is not None:
        result["campaign_queue"] = queue_result
    if notified:
        result["notified"] = notified
    heartbeat = heartbeat_guard(ctx)
    if heartbeat is not None:
        result["heartbeat"] = heartbeat
    return result


# ---------------------------------------------------------------------------
# Status / cron / smoke


def status(ctx: Ctx) -> dict:
    watches = [
        {k: w.get(k) for k in ("watch_id", "kind", "state", "armed_at_utc", "fired_at_utc", "unreliable")}
        for w in load_watches(ctx)
    ]
    events = []
    if ctx.events_dir.is_dir():
        for event_file in sorted(ctx.events_dir.glob("*.json")):
            event_id = event_file.stem
            paths = event_paths(ctx, event_id)
            if paths["done"].exists():
                disposition = read_json(paths["done"])
                state = disposition.get("outcome", "done")
            elif paths["invoked"].exists():
                state = "invoked"
            elif paths["blocked"].exists():
                state = "blocked"
            elif paths["claim"].exists():
                state = "claimed"
            else:
                state = "new"
            events.append({"event_id": event_id, "state": state})
    last_tick = None
    tick_file = ctx.state_dir / "last-tick.json"
    if tick_file.is_file():
        with contextlib.suppress(OSError, json.JSONDecodeError):
            last_tick = read_json(tick_file)
    idle_state = None
    idle_path = ctx.state_dir / "idle-state.json"
    if idle_path.is_file():
        with contextlib.suppress(OSError, json.JSONDecodeError):
            idle_state = read_json(idle_path)
    return {
        "observed_at_utc": ctx.now_iso(),
        "node": socket.gethostname(),
        "watches": watches,
        "archived_watch_count": (
            len(list(ctx.watch_archive_dir.glob("*.json")))
            if ctx.watch_archive_dir.is_dir()
            else 0
        ),
        "events": events,
        "last_tick": last_tick,
        "resume_mutex_held": ctx.resume_mutex.exists(),
        "campaign_idle": campaign_is_idle(ctx),
        "blocked_on_user": blocked_on_user_path(ctx).exists(),
        "idle_state": idle_state,
    }


def scrontab_lines(ctx: Ctx, interval_minutes: int) -> list[str]:
    log = ctx.state_dir / "logs" / "cron-tick.log"
    # The wall must exceed the longest legitimate root-resume turn: a tick
    # that dispatches an action stays alive for the whole turn, and Slurm
    # killing it mid-resume strands the event (2026-07-19 16:40 UTC incident).
    walltime = ctx.config.get("cron_walltime", "12:00:00")
    state_prefix = ""
    if os.environ.get("WAKER_STATE_DIR"):
        state_prefix = f"WAKER_STATE_DIR={shlex.quote(str(ctx.state_dir))} "
    return [
        SCRON_BEGIN,
        "#SCRON -q cron",
        f"#SCRON -t {walltime}",
        f"#SCRON -o {log}",
        "#SCRON --open-mode=append",
        f"*/{interval_minutes} * * * * {state_prefix}{ctx.python_bin()} "
        f"{HERE / 'wakerctl.py'} tick --quiet",
        SCRON_END,
    ]


def read_scrontab(ctx: Ctx) -> list[str]:
    lines, detail = read_scrontab_lines(ctx)
    if lines is None:
        raise WakerError(f"refusing to replace an unreadable scrontab: {detail}")
    return lines


def write_scrontab(ctx: Ctx, lines: list[str]) -> None:
    content = "\n".join(lines).rstrip("\n")
    with tempfile.NamedTemporaryFile("w", suffix=".scron", delete=False) as handle:
        handle.write(content + "\n" if content else "")
        temp_name = handle.name
    try:
        result = ctx.runner(["scrontab", temp_name])
        if result.returncode != 0:
            raise WakerError(f"scrontab rejected the new table: {result.stdout.strip()}")
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temp_name)


def strip_managed_block(lines: list[str]) -> list[str]:
    result, skipping = [], False
    for line in lines:
        if line.strip() == SCRON_BEGIN:
            skipping = True
            continue
        if line.strip() == SCRON_END:
            skipping = False
            continue
        if not skipping:
            result.append(line)
    return result


def install_cron(ctx: Ctx, interval_minutes: int) -> None:
    (ctx.state_dir / "logs").mkdir(parents=True, exist_ok=True)
    lines = strip_managed_block(read_scrontab(ctx))
    lines.extend(scrontab_lines(ctx, interval_minutes))
    write_scrontab(ctx, lines)


def uninstall_cron(ctx: Ctx) -> None:
    write_scrontab(ctx, strip_managed_block(read_scrontab(ctx)))


def run_loop(ctx: Ctx, poll_seconds: int) -> None:
    import time

    lock_path = ctx.state_dir / f"daemon-{socket.gethostname()}.lock"
    with agentctl.exclusive_lock(lock_path):
        while True:
            tick(ctx)
            time.sleep(poll_seconds)


def smoke(config_path: Path) -> int:
    """Bounded end-to-end proof in an isolated state dir with a fake provider.

    Touches no live worker UUID, job, or production output. Asserts: a quiet
    tick performs zero provider calls; a sentinel event produces exactly one
    resume with correct CODEX_HOME/flags/thread; a duplicate tick performs no
    second call.
    """
    with tempfile.TemporaryDirectory(prefix="waker-smoke.") as temp:
        temp_dir = Path(temp)
        calls = temp_dir / "calls.log"
        fake_codex = temp_dir / "codex"
        fake_codex.write_text(
            "#!/bin/bash\n"
            f'echo "CODEX_HOME=$CODEX_HOME argv=$*" >> {calls}\n'
            "exit 0\n"
        )
        fake_codex.chmod(fake_codex.stat().st_mode | stat.S_IXUSR)
        config = read_json(config_path)
        config["codex_bin"] = str(fake_codex)
        # The sandbox must never send real notifications or count as idle.
        config["notify_command"] = None
        config["status_report_interval_seconds"] = 0
        config["idle_guard_ticks"] = 0
        config["root"] = {
            "provider": "codex",
            "profile": "codex-personal",
            "thread_id": "00000000-0000-0000-0000-00000000abcd",
            "disable_features": ["goals"],
        }
        smoke_config = temp_dir / "waker-config.json"
        smoke_config.write_text(json.dumps(config))
        ctx = Ctx(config_path=smoke_config, state_dir=temp_dir / "state")

        result = tick(ctx)
        assert not calls.exists(), "quiet tick must make no provider call"
        assert result == {"emitted": [], "dispatch": []}

        sentinel = temp_dir / "DONE.sentinel"
        add_watch(
            ctx,
            {
                "watch_id": "smoke-sentinel",
                "kind": "file-sentinel",
                "params": {"path": str(sentinel)},
                "action": {"type": "root-resume", "context": "smoke test only"},
            },
        )
        tick(ctx)
        assert not calls.exists(), "unfired watch must make no provider call"
        sentinel.write_text("done\n")
        tick(ctx)
        tick(ctx)
        text = calls.read_text()
        invocations = text.count("CODEX_HOME=")
        assert invocations == 1, f"expected exactly one resume, saw {invocations}"
        assert "00000000-0000-0000-0000-00000000abcd" in text
        assert "--disable goals" in text
        assert "codex-homes/personal" in text
        print("[smoke] PASS: quiet ticks silent; one event -> exactly one resume")
        return 0


# ---------------------------------------------------------------------------
# CLI


def parse_params(pairs: list[str]) -> dict:
    params: dict[str, object] = {}
    for pair in pairs:
        key, _, value = pair.partition("=")
        if not key or not value:
            raise WakerError(f"invalid --param (expected key=value): {pair}")
        params[key] = value
    return params


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("watch-add", help="Arm a watch")
    add.add_argument("--id", required=True)
    add.add_argument("--kind", required=True, choices=sorted(KINDS))
    add.add_argument("--param", action="append", default=[], help="key=value, repeatable")
    add.add_argument("--context", default="", help="Campaign context appended to the resume prompt")
    add.add_argument("--action", default="root-resume", choices=["root-resume", "role-send", "command"])
    add.add_argument("--role")
    add.add_argument("--prompt-file")
    add.add_argument("--argv", nargs=argparse.REMAINDER)
    add.add_argument("--max-retries", type=int)

    for name, help_text in (
        ("watch-list", "List watches"),
        ("watch-compact", "Archive terminal watches out of the live scan directory"),
        ("scan", "One condition-evaluation pass"),
        ("dispatch", "One claim/act pass over spooled events"),
        ("tick", "scan + dispatch once"),
        ("status", "Show watches, events, and tick liveness"),
        ("smoke", "Isolated end-to-end proof with a fake provider"),
        ("uninstall-cron", "Remove the managed scrontab block"),
    ):
        sub = commands.add_parser(name, help=help_text)
        if name in {"tick", "scan", "dispatch"}:
            sub.add_argument("--quiet", action="store_true")

    pre = commands.add_parser(
        "preflight",
        help="Validate binaries, root profile, CODEX_HOME, the cron ticker, and armed watch subjects",
    )
    pre.add_argument(
        "--env-only",
        action="store_true",
        help="Skip the cron-ticker and watch-subject checks (the subset the dispatch path uses)",
    )

    disarm = commands.add_parser("watch-disarm", help="Disarm a watch without deleting it")
    disarm.add_argument("--id", required=True)

    emit = commands.add_parser("emit", help="Manually emit an event")
    emit.add_argument("--id", required=True)
    emit.add_argument("--type", default="manual")
    emit.add_argument("--context", default="")

    cron = commands.add_parser("install-cron", help="Install the scrontab tick")
    cron.add_argument("--interval-minutes", type=int, default=5)

    run = commands.add_parser("run", help="Foreground poll loop (optional; cron remains the net)")
    run.add_argument("--poll-seconds", type=int, default=60)

    args = parser.parse_args()
    config_path = Path(args.config).expanduser().resolve()
    if args.command == "smoke":
        return smoke(config_path)
    ctx = Ctx(config_path=config_path)

    try:
        if args.command == "watch-add":
            action: dict[str, object] = {"type": args.action, "context": args.context}
            if args.action == "role-send":
                action.update({"role": args.role, "prompt_file": args.prompt_file})
            if args.action == "command":
                action["argv"] = args.argv or []
            watch = {
                "watch_id": args.id,
                "kind": args.kind,
                "params": parse_params(args.param),
                "action": action,
            }
            if args.max_retries is not None:
                watch["max_retries"] = args.max_retries
            add_watch(ctx, watch)
            print(f"armed {args.id}")
        elif args.command == "watch-list":
            for watch in load_watches(ctx):
                print(f"{watch['watch_id']}\t{watch['kind']}\t{watch.get('state')}")
        elif args.command == "watch-compact":
            archived = compact_terminal_watches(ctx)
            print(json.dumps({"archived": archived, "count": len(archived)}, indent=2))
        elif args.command == "watch-disarm":
            path = watch_path(ctx, args.id)
            watch = read_json(path)
            watch["state"] = "disarmed"
            save_watch(ctx, watch)
            ctx.ledger(f"evt-{args.id}", "watch-disarmed", "")
            archive_watch(ctx, args.id)
            print(f"disarmed {args.id}")
        elif args.command == "emit":
            created = emit_event(
                ctx, f"evt-{args.id}", args.id, args.type, {}, context=args.context
            )
            print("emitted" if created else "already-exists")
        elif args.command in {"scan", "dispatch", "tick"}:
            result = {"scan": scan, "dispatch": dispatch, "tick": tick}[args.command](ctx)
            if not getattr(args, "quiet", False):
                print(json.dumps(result, indent=2, default=str))
        elif args.command == "status":
            print(json.dumps(status(ctx), indent=2))
        elif args.command == "preflight":
            return 1 if preflight(ctx, control_plane=not args.env_only) else 0
        elif args.command == "install-cron":
            install_cron(ctx, args.interval_minutes)
            print(f"installed scrontab tick every {args.interval_minutes}m")
        elif args.command == "uninstall-cron":
            uninstall_cron(ctx)
            print("removed managed scrontab block")
        elif args.command == "run":
            run_loop(ctx, args.poll_seconds)
    except (WakerError, agentctl.AgentCtlError, OSError) as exc:
        print(f"wakerctl: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
