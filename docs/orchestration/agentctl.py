#!/usr/bin/env python3
"""Persistent, cross-account Claude/Codex session dispatcher."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import pwd
import re
import subprocess
import sys
import tempfile
import uuid


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "profiles.json"
DEFAULT_REGISTRY = HERE / "state" / "sessions.json"


class AgentCtlError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path, default: object | None = None) -> object:
    if not path.exists():
        if default is not None:
            return default
        raise AgentCtlError(f"File not found: {path}")
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentCtlError(f"Could not read JSON from {path}: {exc}") from exc


def atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


@contextlib.contextmanager
def exclusive_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def safe_role(role: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", role):
        raise AgentCtlError(
            "Role must start with a letter or digit and contain only letters, "
            "digits, dot, underscore, or hyphen"
        )
    return role


def read_registry(path: Path) -> dict:
    value = load_json(path, {"version": 1, "sessions": {}})
    if not isinstance(value, dict) or not isinstance(value.get("sessions"), dict):
        raise AgentCtlError(f"Invalid registry format: {path}")
    return value


def mutate_registry(path: Path, callback) -> dict:
    with exclusive_lock(path.with_suffix(path.suffix + ".lock")):
        registry = read_registry(path)
        callback(registry)
        atomic_write_json(path, registry)
        return registry


def login_home() -> Path:
    """Return the login account home even when a delegate overrides HOME."""
    try:
        return Path(pwd.getpwuid(os.getuid()).pw_dir)
    except (KeyError, OSError):
        return Path.home()


def expand_path(value: str) -> str:
    # Claude account isolation may override HOME. Expand profile paths beginning
    # with ~ against the OS login home so they do not become recursively nested.
    # Do not dereference symlinks: NERSC's stable /global/homes spelling may
    # resolve to a storage-tier path such as /global/u2.
    if value == "~":
        expanded = login_home()
    elif value.startswith("~/"):
        expanded = login_home() / value[2:]
    else:
        expanded = Path(os.path.expandvars(value))
    return os.path.abspath(os.fspath(expanded))


def configure_claude_environment(env: dict, profile: dict) -> None:
    variable = profile.get("config_env", "CLAUDE_CONFIG_DIR")
    if variable not in {"HOME", "CLAUDE_CONFIG_DIR"}:
        raise AgentCtlError(
            "Claude profile config_env must be HOME or CLAUDE_CONFIG_DIR"
        )
    env[variable] = expand_path(profile["home"])


def load_profiles(path: Path) -> dict:
    value = load_json(path)
    if not isinstance(value, dict) or not isinstance(value.get("profiles"), dict):
        raise AgentCtlError(f"Invalid profiles file: {path}")
    return value["profiles"]


def get_profile(profiles: dict, name: str) -> dict:
    if name not in profiles:
        raise AgentCtlError(
            f"Unknown profile {name!r}; available: {', '.join(sorted(profiles))}"
        )
    profile = profiles[name]
    if profile.get("provider") not in {"agy", "claude", "codex"}:
        raise AgentCtlError(f"Profile {name!r} has an invalid provider")
    return profile


def prompt_from_args(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text()
    if args.prompt:
        return " ".join(args.prompt)
    raise AgentCtlError("Supply a prompt or --prompt-file")


def add_codex_options(command: list[str], profile: dict) -> None:
    if profile.get("model"):
        command.extend(["--model", profile["model"]])
    if profile.get("reasoning_effort"):
        command.extend(
            ["--config", f'model_reasoning_effort="{profile["reasoning_effort"]}"']
        )
    if profile.get("web_search"):
        command.extend(["--config", "tools.web_search=true"])
    if profile.get("yolo"):
        command.append("--dangerously-bypass-approvals-and-sandbox")


def build_start_command(
    profile: dict,
    prompt: str,
    cwd: Path,
    session_id: str,
    provider_log: Path | None = None,
) -> tuple[list[str], dict]:
    env = os.environ.copy()
    provider = profile["provider"]
    if provider == "codex":
        env["CODEX_HOME"] = expand_path(profile["home"])
        command = ["codex", "exec", "--json"]
        add_codex_options(command, profile)
        if not profile.get("yolo"):
            command.extend(["--sandbox", profile.get("sandbox", "read-only")])
        command.extend(
            ["--skip-git-repo-check", "--cd", str(cwd), prompt]
        )
    elif provider == "claude":
        configure_claude_environment(env, profile)
        command = [
            "claude",
            "--print",
            "--output-format",
            "json",
            "--session-id",
            session_id,
        ]
        if profile.get("model"):
            command.extend(["--model", profile["model"]])
        if profile.get("dangerously_skip_permissions"):
            command.append("--dangerously-skip-permissions")
        if profile.get("allowed_tools"):
            command.append(f'--allowedTools={",".join(profile["allowed_tools"])}')
        command.append(prompt)
    else:
        if provider_log is None:
            raise AgentCtlError("agy requires a provider log path")
        # agy reads its Antigravity OAuth state from $HOME/.gemini; a caller
        # running under Claude account isolation (HOME=~/claude-homes/*) would
        # otherwise send agy to an empty home and hit an auth prompt.
        env["HOME"] = str(login_home())
        command = [expand_path(profile.get("executable", "~/.local/bin/agy"))]
        if profile.get("model"):
            command.extend(["--model", profile["model"]])
        command.extend(
            [
                "--print-timeout",
                profile.get("print_timeout", "25m0s"),
                "--add-dir",
                str(cwd),
                "--log-file",
                str(provider_log),
            ]
        )
        if profile.get("dangerously_skip_permissions", False):
            command.append("--dangerously-skip-permissions")
        if profile.get("sandbox", False):
            command.append("--sandbox")
        command.extend(["--print", prompt])
    return command, env


def build_resume_command(
    profile: dict,
    prompt: str,
    session_id: str,
    cwd: Path | None = None,
    provider_log: Path | None = None,
) -> tuple[list[str], dict]:
    env = os.environ.copy()
    provider = profile["provider"]
    if provider == "codex":
        env["CODEX_HOME"] = expand_path(profile["home"])
        command = ["codex", "exec", "resume", "--json"]
        add_codex_options(command, profile)
        command.extend(["--skip-git-repo-check", session_id, prompt])
    elif provider == "claude":
        configure_claude_environment(env, profile)
        command = [
            "claude",
            "--print",
            "--output-format",
            "json",
            "--resume",
            session_id,
        ]
        if profile.get("model"):
            command.extend(["--model", profile["model"]])
        if profile.get("dangerously_skip_permissions"):
            command.append("--dangerously-skip-permissions")
        if profile.get("allowed_tools"):
            command.append(f'--allowedTools={",".join(profile["allowed_tools"])}')
        command.append(prompt)
    else:
        if cwd is None or provider_log is None:
            raise AgentCtlError("agy requires a working directory and provider log path")
        # Same HOME pin as build_start_command: agy auth lives in $HOME/.gemini.
        env["HOME"] = str(login_home())
        command = [expand_path(profile.get("executable", "~/.local/bin/agy"))]
        if profile.get("model"):
            command.extend(["--model", profile["model"]])
        command.extend(
            [
                "--conversation",
                session_id,
                "--print-timeout",
                profile.get("print_timeout", "25m0s"),
                "--add-dir",
                str(cwd),
                "--log-file",
                str(provider_log),
            ]
        )
        if profile.get("dangerously_skip_permissions", False):
            command.append("--dangerously-skip-permissions")
        if profile.get("sandbox", False):
            command.append("--sandbox")
        command.extend(["--print", prompt])
    return command, env


def parse_codex(stdout: str) -> tuple[str | None, str]:
    thread_id = None
    messages: list[str] = []
    for raw_line in stdout.splitlines():
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id") or thread_id
        item = event.get("item")
        if (
            event.get("type") == "item.completed"
            and isinstance(item, dict)
            and item.get("type") == "agent_message"
            and isinstance(item.get("text"), str)
        ):
            messages.append(item["text"])
    return thread_id, messages[-1] if messages else ""


def parse_claude(stdout: str) -> tuple[str | None, str]:
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise AgentCtlError(f"Claude returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AgentCtlError("Claude returned a non-object JSON result")
    result = value.get("result", "")
    if not isinstance(result, str):
        result = json.dumps(result)
    return value.get("session_id"), result


def parse_agy(log_text: str, stdout: str) -> tuple[str | None, str]:
    patterns = [
        r"Created conversation ([0-9a-fA-F-]{36})",
        r"Print mode: conversation=([0-9a-fA-F-]{36})",
        r'conversationID="([0-9a-fA-F-]{36})"',
    ]
    conversation_id = None
    for pattern in patterns:
        matches = re.findall(pattern, log_text)
        if matches:
            conversation_id = matches[-1]
            break
    return conversation_id, stdout.strip()


def run_worker(
    command: list[str],
    env: dict,
    cwd: Path,
    run_base: Path,
    provider: str,
    provider_log: Path | None = None,
) -> tuple[str | None, str, dict]:
    run_base.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    stdout_suffix = ".jsonl" if provider == "codex" else ".json"
    if provider == "agy":
        stdout_suffix = ".txt"
    stdout_path = run_base.with_suffix(stdout_suffix)
    stderr_path = run_base.with_suffix(".stderr.log")
    stdout_path.write_text(completed.stdout)
    stderr_path.write_text(completed.stderr)
    if completed.returncode != 0:
        detail = completed.stderr.strip()
        if provider == "claude":
            with contextlib.suppress(AgentCtlError):
                _session_id, provider_result = parse_claude(completed.stdout)
                detail = provider_result or detail
        elif provider == "codex":
            errors = []
            for raw_line in completed.stdout.splitlines():
                with contextlib.suppress(json.JSONDecodeError):
                    event = json.loads(raw_line)
                    if event.get("type") in {"error", "turn.failed"}:
                        errors.append(json.dumps(event, sort_keys=True))
            if errors:
                detail = errors[-1]
        elif provider_log and provider_log.exists():
            detail = "\n".join(provider_log.read_text().splitlines()[-20:]) or detail
        suffix = f": {detail}" if detail else ""
        raise AgentCtlError(
            f"Worker exited {completed.returncode}{suffix}; "
            f"see {stdout_path} and {stderr_path}"
        )
    if provider == "codex":
        session_id, result = parse_codex(completed.stdout)
    elif provider == "claude":
        session_id, result = parse_claude(completed.stdout)
    else:
        if provider_log is None or not provider_log.exists():
            raise AgentCtlError("agy completed without writing its conversation log")
        session_id, result = parse_agy(provider_log.read_text(), completed.stdout)
    metadata = {
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "returncode": completed.returncode,
    }
    if provider_log is not None:
        metadata["provider_log"] = str(provider_log)
    return session_id, result, metadata


def run_base(role: str, action: str) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return HERE / "runs" / role / f"{stamp}-{action}-{uuid.uuid4().hex[:8]}"


def start(args: argparse.Namespace, profiles: dict, registry_path: Path) -> None:
    role = safe_role(args.role)
    profile = get_profile(profiles, args.profile)
    prompt = prompt_from_args(args)
    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        raise AgentCtlError(f"Working directory does not exist: {cwd}")
    role_lock = registry_path.parent / "locks" / f"{role}.lock"
    with exclusive_lock(role_lock):
        if role in read_registry(registry_path)["sessions"]:
            raise AgentCtlError(
                f"Role {role!r} already exists; use send or choose another role"
            )
        provisional_id = str(uuid.uuid4())
        base = run_base(role, "start")
        provider_log = base.with_suffix(".agy.log") if profile["provider"] == "agy" else None
        command, env = build_start_command(
            profile, prompt, cwd, provisional_id, provider_log=provider_log
        )
        session_id, result, run = run_worker(
            command,
            env,
            cwd,
            base,
            profile["provider"],
            provider_log=provider_log,
        )
        if profile["provider"] in {"agy", "codex"} and not session_id:
            raise AgentCtlError(
                f"{profile['provider']} completed without reporting a conversation ID"
            )
        session_id = session_id or provisional_id

        def add_session(registry: dict) -> None:
            if role in registry["sessions"]:
                raise AgentCtlError(f"Role {role!r} was created concurrently")
            registry["sessions"][role] = {
                "provider": profile["provider"],
                "profile": args.profile,
                "session_id": session_id,
                "cwd": str(cwd),
                "created_at": utc_now(),
                "updated_at": utc_now(),
                "turns": [{"number": 1, "action": "start", **run}],
            }

        mutate_registry(registry_path, add_session)
    print(result)


def send(args: argparse.Namespace, profiles: dict, registry_path: Path) -> None:
    role = safe_role(args.role)
    prompt = prompt_from_args(args)
    role_lock = registry_path.parent / "locks" / f"{role}.lock"
    with exclusive_lock(role_lock):
        registry = read_registry(registry_path)
        if role not in registry["sessions"]:
            raise AgentCtlError(f"Unknown role {role!r}; start it first")
        session = registry["sessions"][role]
        profile = get_profile(profiles, session["profile"])
        cwd = Path(session["cwd"])
        base = run_base(role, "send")
        provider_log = base.with_suffix(".agy.log") if profile["provider"] == "agy" else None
        command, env = build_resume_command(
            profile,
            prompt,
            session["session_id"],
            cwd=cwd,
            provider_log=provider_log,
        )
        _session_id, result, run = run_worker(
            command,
            env,
            cwd,
            base,
            profile["provider"],
            provider_log=provider_log,
        )

        def record_turn(latest: dict) -> None:
            current = latest["sessions"].get(role)
            if not current or current["session_id"] != session["session_id"]:
                raise AgentCtlError(f"Role {role!r} changed while its turn was running")
            current["updated_at"] = utc_now()
            current["turns"].append(
                {"number": len(current["turns"]) + 1, "action": "send", **run}
            )

        mutate_registry(registry_path, record_turn)
    print(result)


def adopt(args: argparse.Namespace, profiles: dict, registry_path: Path) -> None:
    role = safe_role(args.role)
    profile = get_profile(profiles, args.profile)
    session_id = args.session_id.strip()
    if not session_id:
        raise AgentCtlError("Session ID cannot be empty")
    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        raise AgentCtlError(f"Working directory does not exist: {cwd}")
    role_lock = registry_path.parent / "locks" / f"{role}.lock"
    with exclusive_lock(role_lock):
        if role in read_registry(registry_path)["sessions"]:
            raise AgentCtlError(
                f"Role {role!r} already exists; use send or choose another role"
            )

        def add_session(registry: dict) -> None:
            if role in registry["sessions"]:
                raise AgentCtlError(f"Role {role!r} was created concurrently")
            registry["sessions"][role] = {
                "provider": profile["provider"],
                "profile": args.profile,
                "session_id": session_id,
                "cwd": str(cwd),
                "created_at": utc_now(),
                "updated_at": utc_now(),
                "turns": [],
                "adopted": True,
            }

        mutate_registry(registry_path, add_session)
    print(f"Adopted {role} ({profile['provider']}) as {session_id}")


def show(args: argparse.Namespace, registry_path: Path) -> None:
    registry = read_registry(registry_path)
    if args.role:
        role = safe_role(args.role)
        if role not in registry["sessions"]:
            raise AgentCtlError(f"Unknown role {role!r}")
        print(json.dumps(registry["sessions"][role], indent=2, sort_keys=True))
    else:
        print(json.dumps(registry, indent=2, sort_keys=True))


def list_profiles(profiles: dict) -> None:
    for name, profile in sorted(profiles.items()):
        location = profile.get("home") or profile.get("executable") or ""
        print(f"{name}\t{profile['provider']}\t{expand_path(location) if location else ''}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Start and resume persistent workers on Claude, Codex, and agy accounts"
    )
    result.add_argument("--config", default=str(DEFAULT_CONFIG))
    result.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    commands = result.add_subparsers(dest="command", required=True)

    profiles = commands.add_parser("profiles", help="List configured account profiles")
    profiles.set_defaults(handler="profiles")

    start_parser = commands.add_parser("start", help="Start a persistent role")
    start_parser.add_argument("--role", required=True)
    start_parser.add_argument("--profile", required=True)
    start_parser.add_argument("--cwd", default=os.getcwd())
    start_parser.add_argument("--prompt-file")
    start_parser.add_argument("prompt", nargs="*")
    start_parser.set_defaults(handler="start")

    adopt_parser = commands.add_parser(
        "adopt", help="Register an existing provider session under a role"
    )
    adopt_parser.add_argument("--role", required=True)
    adopt_parser.add_argument("--profile", required=True)
    adopt_parser.add_argument("--session-id", required=True)
    adopt_parser.add_argument("--cwd", default=os.getcwd())
    adopt_parser.set_defaults(handler="adopt")

    send_parser = commands.add_parser("send", help="Resume a persistent role")
    send_parser.add_argument("--role", required=True)
    send_parser.add_argument("--prompt-file")
    send_parser.add_argument("prompt", nargs="*")
    send_parser.set_defaults(handler="send")

    show_parser = commands.add_parser("show", help="Show the session registry")
    show_parser.add_argument("--role")
    show_parser.set_defaults(handler="show")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        config_path = Path(args.config).expanduser().resolve()
        registry_path = Path(args.registry).expanduser().resolve()
        profiles = load_profiles(config_path)
        if args.handler == "profiles":
            list_profiles(profiles)
        elif args.handler == "start":
            start(args, profiles, registry_path)
        elif args.handler == "adopt":
            adopt(args, profiles, registry_path)
        elif args.handler == "send":
            send(args, profiles, registry_path)
        else:
            show(args, registry_path)
    except (AgentCtlError, OSError) as exc:
        print(f"agentctl: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
