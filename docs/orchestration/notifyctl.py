#!/usr/bin/python3.11
"""Independent notification fanout and external heartbeat for wakerctl.

Tracked configuration contains no credentials.  Optional ntfy and heartbeat
URLs live in the gitignored waker state directory with mode 0600.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "notification-config.json"
DEFAULT_SECRETS = HERE / "state" / "waker" / "notification-secrets.json"


class NotifyError(RuntimeError):
    pass


def load_object(path: Path, *, required: bool) -> dict:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError:
        if required:
            raise NotifyError(f"missing configuration: {path}")
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        raise NotifyError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise NotifyError(f"configuration must be a JSON object: {path}")
    return value


def marker_path(state_dir: Path, key: str, channel: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return state_dir / "notification-channels" / f"{digest}.{channel}.sent"


def mark_sent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text("sent\n")
        try:
            os.link(temporary, path)
        except FileExistsError:
            pass
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def send_email(config: dict, subject: str, body: str) -> None:
    command = config.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
        raise NotifyError("email.command must be a nonempty string array")
    argv = [part.replace("{subject}", subject) for part in command]
    try:
        result = subprocess.run(
            argv,
            input=body,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=float(config.get("timeout_seconds", 30)),
        )
    except subprocess.TimeoutExpired as exc:
        raise NotifyError(f"email command timed out: {exc}") from exc
    if result.returncode != 0:
        raise NotifyError(f"email command failed rc={result.returncode}: {result.stdout[-500:]}")


def http_post(url: str, data: bytes, headers: dict[str, str], timeout: float) -> None:
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if not 200 <= response.status < 300:
                raise NotifyError(f"HTTP POST returned {response.status}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise NotifyError(f"HTTP POST failed: {exc}") from exc


def ntfy_url(config: dict, secrets: dict) -> str | None:
    ntfy_secret = secrets.get("ntfy")
    if not isinstance(ntfy_secret, dict):
        return None
    url = ntfy_secret.get("url")
    if isinstance(url, str) and url.startswith("https://"):
        return url
    topic = ntfy_secret.get("topic")
    base = config.get("base_url", "https://ntfy.sh")
    if isinstance(topic, str) and topic and isinstance(base, str) and base.startswith("https://"):
        return f"{base.rstrip('/')}/{topic}"
    return None


def send_ntfy(config: dict, secrets: dict, subject: str, body: str) -> None:
    url = ntfy_url(config, secrets)
    if not url:
        raise NotifyError("ntfy is enabled but notification-secrets.json has no HTTPS url/topic")
    ntfy_secret = secrets.get("ntfy") or {}
    token = ntfy_secret.get("token")
    headers = {
        "Title": subject.encode("ascii", "replace").decode("ascii")[:250],
        "Priority": str(config.get("priority", "default")),
        "Content-Type": "text/plain; charset=utf-8",
    }
    if isinstance(token, str) and token:
        headers["Authorization"] = f"Bearer {token}"
    if config.get("include_body") is True:
        message = body[: int(config.get("max_body_chars", 2000))]
    else:
        message = str(config.get("generic_body", "Open email or Termius for details."))
    http_post(url, message.encode("utf-8"), headers, float(config.get("timeout_seconds", 15)))


def send(config: dict, secrets: dict, state_dir: Path, key: str, subject: str, body: str) -> int:
    channels = []
    email = config.get("email")
    if isinstance(email, dict) and email.get("enabled") is True:
        channels.append(("email", lambda: send_email(email, subject, body)))
    ntfy = config.get("ntfy")
    if isinstance(ntfy, dict) and ntfy.get("enabled") is True:
        channels.append(("ntfy", lambda: send_ntfy(ntfy, secrets, subject, body)))
    if not channels:
        raise NotifyError("no notification channel is enabled")

    failures = []
    for name, action in channels:
        marker = marker_path(state_dir, key, name)
        if marker.exists():
            continue
        try:
            action()
            mark_sent(marker)
        except NotifyError as exc:
            failures.append(f"{name}: {exc}")
    if failures:
        print("; ".join(failures), file=sys.stderr)
        return 1
    return 0


def heartbeat(config: dict, secrets: dict) -> int:
    heartbeat_config = config.get("heartbeat")
    heartbeat_secret = secrets.get("heartbeat")
    if not isinstance(heartbeat_config, dict) or heartbeat_config.get("enabled") is not True:
        return 0
    if not isinstance(heartbeat_secret, dict) or not isinstance(heartbeat_secret.get("url"), str):
        # A heartbeat is intentionally optional until the user creates an
        # external dead-man check; absence must not break the local ticker.
        return 0
    http_post(
        heartbeat_secret["url"],
        b"",
        {"User-Agent": "MINERvA-waker/1"},
        float(heartbeat_config.get("timeout_seconds", 15)),
    )
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--config", default=str(DEFAULT_CONFIG))
    result.add_argument(
        "--secrets",
        default=os.environ.get("WAKER_NOTIFICATION_SECRETS", str(DEFAULT_SECRETS)),
    )
    commands = result.add_subparsers(dest="command", required=True)
    send_parser = commands.add_parser("send")
    send_parser.add_argument("--key", required=True)
    send_parser.add_argument("--subject", required=True)
    commands.add_parser("heartbeat")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        config = load_object(Path(args.config).expanduser(), required=True)
        secrets_path = Path(args.secrets).expanduser()
        secrets = load_object(secrets_path, required=False)
        if secrets_path.exists() and secrets_path.stat().st_mode & 0o077:
            raise NotifyError(f"secrets file must have mode 0600: {secrets_path}")
        if args.command == "heartbeat":
            return heartbeat(config, secrets)
        state_dir = Path(config.get("state_dir", HERE / "state" / "waker"))
        if not state_dir.is_absolute():
            state_dir = HERE / state_dir
        return send(config, secrets, state_dir, args.key, args.subject, sys.stdin.read())
    except NotifyError as exc:
        print(f"notifyctl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
