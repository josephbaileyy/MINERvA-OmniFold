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
import contextlib
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys
import tempfile

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
    "and refresh docs/orchestration/LIVE-STATE.md with its generator. Goals "
    "remain disabled. If the ledger shows this event already reconciled, "
    "record that and stop."
)


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
        self.events_dir = self.state_dir / "events"
        self.logs_dir = self.state_dir / "logs"
        self.ledger_path = self.state_dir / "LEDGER.tsv"
        self.resume_mutex = self.state_dir / "resume.mutex"
        self.runner = runner or self._run
        self.clock = clock or (lambda: dt.datetime.now(dt.timezone.utc).timestamp())

    @staticmethod
    def _run(argv: list[str], env: dict | None = None, cwd: Path | None = None):
        return subprocess.run(
            argv,
            env=env,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
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


def add_watch(ctx: Ctx, watch: dict) -> None:
    path = watch_path(ctx, watch["watch_id"])
    if path.exists():
        raise WakerError(f"watch already exists: {watch['watch_id']}")
    watch.setdefault("state", "armed")
    watch.setdefault("armed_at_utc", ctx.now_iso())
    watch.setdefault("armed_by", owner_string())
    watch.setdefault("unreliable", 0)
    validate_watch(ctx, watch)
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
    queue = ctx.runner(["squeue", "-h", "-j", job_id, "-o", "%T"])
    if queue.returncode == 0 and queue.stdout.strip():
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
        state, _, submitted = queue.stdout.strip().partition("|")
        submitted = submitted.strip()
        if state.strip() != "PENDING" or not submitted:
            reliable()
            return None
        if submitted.isdigit():
            submit_epoch = float(submitted)
        else:
            submit_epoch = parse_utc(submitted)
        waited = ctx.now() - submit_epoch
        if waited >= threshold:
            return (
                "queue-latency",
                {"job_id": job_id, "waited_seconds": int(waited), "threshold_seconds": int(threshold)},
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
    created = create_exclusive(
        event_paths(ctx, event_id)["event"], json.dumps(record, indent=2, sort_keys=True) + "\n"
    )
    if created:
        ctx.ledger(event_id, "event-emitted", f"type={event_type} watch={watch_id}")
    return created


def scan(ctx: Ctx) -> list[str]:
    """One poll pass; emits events for fired watches. Returns emitted event ids."""
    emitted: list[str] = []
    for watch in load_watches(ctx):
        if watch.get("state") != "armed":
            continue
        fired = evaluate(ctx, watch)
        if fired is None:
            continue
        event_type, payload = fired
        event_id = f"evt-{watch['watch_id']}"
        emit_event(ctx, event_id, watch["watch_id"], event_type, payload)
        watch["state"] = "fired"
        watch["fired_at_utc"] = ctx.now_iso()
        save_watch(ctx, watch)
        emitted.append(event_id)
    _write_tick_receipt(ctx)
    return emitted


def _write_tick_receipt(ctx: Ctx) -> None:
    agentctl.atomic_write_json(
        ctx.state_dir / "last-tick.json",
        {"at_utc": ctx.now_iso(), "node": socket.gethostname(), "pid": os.getpid()},
    )


# ---------------------------------------------------------------------------
# Dispatch


def preflight(ctx: Ctx, quiet: bool = False) -> list[str]:
    problems: list[str] = []
    codex = ctx.codex_bin()
    if not codex or not Path(codex).is_file() or not os.access(codex, os.X_OK):
        problems.append(f"codex binary missing or not executable: {codex!r}")
    python = ctx.python_bin()
    if not Path(python).is_file() or not os.access(python, os.X_OK):
        problems.append(f"python missing or not executable: {python!r}")
    try:
        root = ctx.root()
        profile = agentctl.get_profile(ctx.profiles(), root.get("profile", "codex-personal"))
        home = Path(agentctl.expand_path(profile["home"]))
        if not home.is_dir():
            problems.append(f"root CODEX_HOME missing: {home}")
    except (WakerError, agentctl.AgentCtlError) as exc:
        problems.append(str(exc))
    if not quiet:
        for problem in problems:
            print(f"[preflight] {problem}", file=sys.stderr)
        if not problems:
            print(f"[preflight] PASS codex={codex} python={python}")
    return problems


def build_root_resume(ctx: Ctx, event: dict) -> tuple[list[str], dict]:
    root = ctx.root()
    profile = agentctl.get_profile(ctx.profiles(), root.get("profile", "codex-personal"))
    if profile.get("provider") != "codex":
        raise WakerError("root resume requires a codex profile")
    env = ctx.base_env()
    env["CODEX_HOME"] = agentctl.expand_path(profile["home"])
    codex = ctx.codex_bin()
    if not codex:
        raise WakerError("codex binary unresolved")
    command = [codex, "exec", "resume"]
    agentctl.add_codex_options(command, profile)
    for feature in root.get("disable_features", ["goals"]):
        command.extend(["--disable", feature])
    command.extend(["--skip-git-repo-check", root["thread_id"], render_prompt(ctx, event)])
    return command, env


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
    path = ctx.watches_dir / f"{event.get('watch_id', '')}.json"
    if path.is_file():
        with contextlib.suppress(OSError, json.JSONDecodeError):
            return read_json(path).get("action", {}).get("context", "")
    return ""


def run_action(ctx: Ctx, event: dict) -> int:
    watch_file = ctx.watches_dir / f"{event.get('watch_id', '')}.json"
    action = {"type": "root-resume"}
    if watch_file.is_file():
        with contextlib.suppress(OSError, json.JSONDecodeError):
            action = read_json(watch_file).get("action") or action
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
    event = read_json(paths["event"])
    if not create_exclusive(
        paths["invoked"],
        json.dumps({"at_utc": ctx.now_iso(), "owner": owner_string()}, sort_keys=True) + "\n",
    ):
        return "invoked-race"
    ctx.ledger(event_id, "invoked", f"type={event.get('event_type')}")
    try:
        rc = run_action(ctx, event)
    except (WakerError, agentctl.AgentCtlError, OSError) as exc:
        ctx.ledger(event_id, "action-exception", str(exc))
        rc = -1
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
    return outcome


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
        return
    retry_id = f"{base_id}.r{attempt}"
    emit_event(
        ctx,
        retry_id,
        event.get("watch_id", "unknown"),
        event.get("event_type", "unknown"),
        event.get("payload", {}),
        retry_of=base_id,
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
    )
    # The recon event supersedes the original: give the original a terminal
    # disposition so it is never re-dispatched and its record is complete.
    agentctl.atomic_write_json(
        paths["done"],
        {"at_utc": ctx.now_iso(), "owner": owner_string(), "rc": None, "outcome": "reconciled"},
    )
    ctx.ledger(event_id, "recon-emitted", f"invoked_age={int(invoked_age)}s")
    return "recon-emitted"


def tick(ctx: Ctx) -> dict:
    emitted = scan(ctx)
    outcomes = dispatch(ctx)
    return {"emitted": emitted, "dispatch": outcomes}


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
    return {
        "observed_at_utc": ctx.now_iso(),
        "node": socket.gethostname(),
        "watches": watches,
        "events": events,
        "last_tick": last_tick,
        "resume_mutex_held": ctx.resume_mutex.exists(),
    }


def scrontab_lines(ctx: Ctx, interval_minutes: int) -> list[str]:
    log = ctx.state_dir / "logs" / "cron-tick.log"
    return [
        SCRON_BEGIN,
        "#SCRON -q cron",
        "#SCRON -t 00:10:00",
        f"#SCRON -o {log}",
        "#SCRON --open-mode=append",
        f"*/{interval_minutes} * * * * {ctx.python_bin()} {HERE / 'wakerctl.py'} tick --quiet",
        SCRON_END,
    ]


def read_scrontab(ctx: Ctx) -> list[str]:
    result = ctx.runner(["scrontab", "-l"])
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


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
        ("scan", "One condition-evaluation pass"),
        ("dispatch", "One claim/act pass over spooled events"),
        ("tick", "scan + dispatch once"),
        ("status", "Show watches, events, and tick liveness"),
        ("preflight", "Validate binaries, root profile, and CODEX_HOME"),
        ("smoke", "Isolated end-to-end proof with a fake provider"),
        ("uninstall-cron", "Remove the managed scrontab block"),
    ):
        sub = commands.add_parser(name, help=help_text)
        if name in {"tick", "scan", "dispatch"}:
            sub.add_argument("--quiet", action="store_true")

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
        elif args.command == "watch-disarm":
            path = watch_path(ctx, args.id)
            watch = read_json(path)
            watch["state"] = "disarmed"
            save_watch(ctx, watch)
            ctx.ledger(f"evt-{args.id}", "watch-disarmed", "")
            print(f"disarmed {args.id}")
        elif args.command == "emit":
            created = emit_event(ctx, f"evt-{args.id}", args.id, args.type, {"context": args.context})
            print("emitted" if created else "already-exists")
        elif args.command in {"scan", "dispatch", "tick"}:
            result = {"scan": scan, "dispatch": dispatch, "tick": tick}[args.command](ctx)
            if not getattr(args, "quiet", False):
                print(json.dumps(result, indent=2, default=str))
        elif args.command == "status":
            print(json.dumps(status(ctx), indent=2))
        elif args.command == "preflight":
            return 1 if preflight(ctx) else 0
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
