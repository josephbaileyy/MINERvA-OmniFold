#!/usr/bin/python3.11
"""Forward interactive Codex and Claude attention events to notifyctl.

Hook processes return immediately after placing a mode-0600 envelope in the
waker state directory.  A detached delivery process performs the potentially
slow email and ntfy fanout, so notification delivery cannot hold up an agent
or exceed Claude's short SessionEnd hook budget.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import pwd
import socket
import subprocess
import sys
import time
import uuid


PYTHON = "/usr/bin/python3.11"
MAX_DETAIL_CHARS = 1200
DEDUPE_SECONDS = 30


class AgentNotifyError(RuntimeError):
    pass


def real_home() -> Path:
    return Path(pwd.getpwuid(os.getuid()).pw_dir)


def orchestration_dir() -> Path:
    override = os.environ.get("MINERVA_ORCHESTRATION_DIR")
    candidates = []
    if override:
        candidates.append(Path(override).expanduser())
    username = pwd.getpwuid(os.getuid()).pw_name
    candidates.extend(
        [
            Path(f"/pscratch/sd/j/{username}/MINERvA-OmniFold/docs/orchestration"),
            real_home() / "mnv-work" / "MINERvA-OmniFold" / "docs" / "orchestration",
            Path(__file__).resolve().parent,
        ]
    )
    for candidate in candidates:
        if (candidate / "notifyctl.py").is_file() and (
            candidate / "state" / "waker" / "notification-secrets.json"
        ).is_file():
            return candidate
    raise AgentNotifyError("no orchestration directory with notifyctl and notification secrets")


def read_payload(provider: str, values: list[str]) -> dict:
    raw = values[-1] if values else sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentNotifyError(f"invalid {provider} hook JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AgentNotifyError(f"{provider} hook payload must be a JSON object")
    return value


def tmux_session() -> str | None:
    pane = os.environ.get("TMUX_PANE")
    if not pane:
        return None
    try:
        result = subprocess.run(
            ["tmux", "display-message", "-p", "-t", pane, "#{session_name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def account_name(provider: str) -> str:
    if provider == "codex":
        configured_home = os.environ.get("CODEX_HOME")
    else:
        configured_home = os.environ.get("HOME")
    if configured_home:
        name = Path(configured_home).name
        if name in {"personal", "school", "school2"}:
            return name
    return "default"


def transcript_fingerprint(payload: dict) -> str:
    path_value = payload.get("transcript_path")
    if isinstance(path_value, str):
        try:
            stat = Path(path_value).stat()
            return f"{stat.st_size}:{stat.st_mtime_ns}"
        except OSError:
            pass
    return ""


def event_state(provider: str, payload: dict) -> tuple[str, str]:
    if provider == "codex":
        event = str(payload.get("type", "codex-notification"))
        if event == "agent-turn-complete":
            return event, "needs input"
        return event, "needs attention"

    event = str(payload.get("hook_event_name", "Claude event"))
    if event == "Stop":
        return event, "needs input"
    if event == "Notification":
        notification_type = str(payload.get("notification_type", "notification"))
        states = {
            "permission_prompt": "needs permission",
            "idle_prompt": "needs input",
            "elicitation_dialog": "needs input",
        }
        return f"{event}:{notification_type}", states.get(notification_type, "needs attention")
    if event == "StopFailure":
        return event, "turn failed"
    if event == "SessionEnd":
        return event, "session ended"
    return event, "needs attention"


def compact_detail(value: object) -> str:
    if isinstance(value, list):
        text = "\n".join(str(item) for item in value)
    else:
        text = str(value or "")
    return " ".join(text.split())[:MAX_DETAIL_CHARS]


def build_message(envelope: dict) -> tuple[str, str, str]:
    provider = envelope["provider"]
    payload = envelope["payload"]
    event, state = event_state(provider, payload)
    account = envelope["account"]
    session = envelope.get("tmux_session") or f"{provider}-{account}"
    subject = f"[MINERvA agent] {session}: {state}"

    fields = [
        f"Session: {session}",
        f"Provider/account: {provider}/{account}",
        f"State: {state}",
        f"Event: {event}",
        f"Host: {envelope.get('host', 'unknown')}",
        f"Working directory: {payload.get('cwd') or envelope.get('cwd') or 'unknown'}",
    ]
    if payload.get("reason"):
        fields.append(f"Reason: {compact_detail(payload['reason'])}")
    detail = payload.get("message") or payload.get("last-assistant-message")
    if detail:
        fields.extend(["", "Last detail:", compact_detail(detail)])
    fields.extend(["", f"Attach with: tmux attach -t {session}"])
    body = "\n".join(fields) + "\n"

    stable_event_id = (
        payload.get("turn-id")
        or transcript_fingerprint(payload)
        or payload.get("request_id")
        or payload.get("tool_use_id")
    )
    identity = {
        "provider": provider,
        "account": account,
        "session": session,
        "event": event,
        "session_id": payload.get("session_id") or payload.get("thread-id"),
        "turn_id": payload.get("turn-id"),
        "stable_event_id": stable_event_id
        or int(envelope.get("observed_at_ns", time.time_ns()) / 1_000_000_000 / DEDUPE_SECONDS),
    }
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return f"agent-session:{digest}", subject, body


def claim_attention_window(root: Path, envelope: dict, subject: str) -> bool:
    """Claim a short per-session/state window, suppressing concurrent duplicate hooks."""
    session = envelope.get("tmux_session") or f"{envelope['provider']}-{envelope['account']}"
    token = hashlib.sha256(f"{session}\0{subject}".encode()).hexdigest()
    directory = root / "state" / "waker" / "agent-notify-cooldown"
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / f"{token}.sent"
    lock = directory / f"{token}.lock"
    for _ in range(20):
        try:
            lock.mkdir()
            break
        except FileExistsError:
            time.sleep(0.025)
    else:
        # Fail open if a stale lock cannot be acquired.
        return True
    try:
        now = time.time()
        try:
            age = now - marker.stat().st_mtime
        except FileNotFoundError:
            age = DEDUPE_SECONDS + 1
        if age < DEDUPE_SECONDS:
            return False
        temporary = marker.with_name(f".{marker.name}.{os.getpid()}.tmp")
        temporary.write_text(f"{now}\n")
        os.replace(temporary, marker)
        return True
    finally:
        lock.rmdir()


def enqueue(provider: str, payload: dict) -> Path:
    root = orchestration_dir()
    spool_dir = root / "state" / "waker" / "agent-notify-spool"
    spool_dir.mkdir(parents=True, exist_ok=True)
    spool_id = uuid.uuid4().hex
    path = spool_dir / f"{spool_id}.json"
    envelope = {
        "schema_version": 1,
        "spool_id": spool_id,
        "provider": provider,
        "account": account_name(provider),
        "tmux_session": tmux_session(),
        "host": socket.gethostname(),
        "cwd": os.getcwd(),
        "observed_at_ns": time.time_ns(),
        "payload": payload,
    }
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        json.dump(envelope, handle, sort_keys=True)
        handle.write("\n")

    log_path = root / "state" / "waker" / "logs" / "agent-notifications.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("ab") as log:
            subprocess.Popen(
                [PYTHON, str(Path(__file__).resolve()), "--deliver", str(path)],
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True,
            )
    except OSError:
        path.unlink(missing_ok=True)
        raise
    return path


def deliver(path: Path) -> int:
    try:
        envelope = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentNotifyError(f"cannot read delivery envelope {path}: {exc}") from exc
    key, subject, body = build_message(envelope)
    root = orchestration_dir()
    if not claim_attention_window(root, envelope, subject):
        path.unlink(missing_ok=True)
        print(f"deduplicated {subject}")
        return 0
    command = [PYTHON, str(root / "notifyctl.py"), "send", "--key", key, "--subject", subject]
    delays = (0, 2, 10)
    for attempt, delay in enumerate(delays, start=1):
        if delay:
            time.sleep(delay)
        result = subprocess.run(command, input=body, text=True, check=False)
        if result.returncode == 0:
            path.unlink(missing_ok=True)
            print(f"delivered {subject}")
            return 0
        print(f"delivery attempt {attempt} failed rc={result.returncode}", file=sys.stderr)
    return 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--deliver", metavar="ENVELOPE")
    result.add_argument("--dry-run", action="store_true")
    result.add_argument("provider", nargs="?", choices=("codex", "claude", "test"))
    result.add_argument("payload", nargs="*")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.deliver:
            return deliver(Path(args.deliver))
        if not args.provider:
            raise AgentNotifyError("provider is required")
        if args.provider == "test":
            provider = "codex"
            payload = {
                "type": "agent-turn-complete",
                "cwd": os.getcwd(),
                "last-assistant-message": "Notification fanout test; no action is required.",
            }
        else:
            provider = args.provider
            payload = read_payload(provider, args.payload)
        if args.dry_run:
            envelope = {
                "spool_id": "dry-run",
                "provider": provider,
                "account": account_name(provider),
                "tmux_session": tmux_session(),
                "host": socket.gethostname(),
                "cwd": os.getcwd(),
                "payload": payload,
            }
            key, subject, body = build_message(envelope)
            print(json.dumps({"key": key, "subject": subject, "body": body}, indent=2))
            return 0
        enqueue(provider, payload)
        return 0
    except (AgentNotifyError, OSError) as exc:
        print(f"agent_session_notify: {exc}", file=sys.stderr)
        # A broken alert must never block or alter the agent lifecycle.
        return 0 if args.provider in {"codex", "claude"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
