#!/usr/bin/python3.11
"""Install cluster-wide interactive agent attention hooks for all accounts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import pwd
import re
import shutil


PYTHON = "/usr/bin/python3.11"
CODEX_ACCOUNTS = ("personal", "school", "school2")
CLAUDE_ACCOUNTS = ("personal", "school")


class InstallError(RuntimeError):
    pass


def atomic_write(path: Path, text: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode or 0o600)
        with os.fdopen(descriptor, "w") as handle:
            handle.write(text)
        os.replace(temporary, path)
        if mode is not None:
            os.chmod(path, mode)
    finally:
        temporary.unlink(missing_ok=True)


def install_codex_config(path: Path, notifier: Path) -> bool:
    text = path.read_text()
    value = json.dumps([PYTHON, str(notifier), "codex"], separators=(",", ":"))
    line = f"notify = {value}\n"
    pattern = re.compile(r"^notify\s*=.*(?:\n|$)", re.MULTILINE)
    if pattern.search(text):
        updated = pattern.sub(line, text, count=1)
    else:
        updated = line + text
    if updated == text:
        return False
    atomic_write(path, updated, path.stat().st_mode & 0o777)
    return True


def hook_entry(command: str, matcher: str | None = None) -> dict:
    result = {"hooks": [{"type": "command", "command": command, "timeout": 5}]}
    if matcher is not None:
        result["matcher"] = matcher
    return result


def install_claude_config(path: Path, notifier: Path) -> bool:
    try:
        settings = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise InstallError(f"invalid Claude settings {path}: {exc}") from exc
    if not isinstance(settings, dict):
        raise InstallError(f"Claude settings are not an object: {path}")
    command = f"{PYTHON} {notifier} claude"
    wanted = {
        "Stop": [hook_entry(command)],
        "Notification": [
            hook_entry(command, "permission_prompt"),
            hook_entry(command, "elicitation_dialog"),
        ],
        "StopFailure": [hook_entry(command)],
        "SessionEnd": [hook_entry(command)],
    }
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise InstallError(f"Claude hooks are not an object: {path}")
    changed = False
    for event, entries in wanted.items():
        existing = hooks.setdefault(event, [])
        if not isinstance(existing, list):
            raise InstallError(f"Claude hook event {event} is not an array: {path}")
        for entry in entries:
            if entry not in existing:
                existing.append(entry)
                changed = True
    if changed:
        atomic_write(path, json.dumps(settings, indent=2, sort_keys=True) + "\n", path.stat().st_mode & 0o777)
    return changed


def install(source: Path, home: Path) -> list[str]:
    if not source.is_file():
        raise InstallError(f"missing notifier source: {source}")
    notifier = home / "bin" / "minerva-agent-notify"
    notifier.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, notifier)
    os.chmod(notifier, 0o755)
    results = [f"deployed {notifier}"]
    for account in CODEX_ACCOUNTS:
        path = home / "codex-homes" / account / "config.toml"
        if not path.is_file():
            raise InstallError(f"missing Codex config: {path}")
        changed = install_codex_config(path, notifier)
        results.append(f"codex/{account}: {'updated' if changed else 'current'}")
    for account in CLAUDE_ACCOUNTS:
        path = home / "claude-homes" / account / ".claude" / "settings.json"
        if not path.is_file():
            raise InstallError(f"missing Claude config: {path}")
        changed = install_claude_config(path, notifier)
        results.append(f"claude/{account}: {'updated' if changed else 'current'}")
    return results


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--source",
        default=str(Path(__file__).resolve().with_name("agent_session_notify.py")),
    )
    result.add_argument("--home", default=pwd.getpwuid(os.getuid()).pw_dir)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        for line in install(Path(args.source), Path(args.home)):
            print(line)
        return 0
    except (InstallError, OSError) as exc:
        print(f"install_agent_notifications: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
