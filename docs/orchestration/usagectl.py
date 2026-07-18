#!/usr/bin/python3.11
"""Fail-closed, read-only cross-account usage snapshots."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import pwd
import selectors
import shlex
import subprocess
import sys
import time

import agentctl


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "profiles.json"
DEFAULT_POLICY = HERE / "usage-policy.json"
DEFAULT_CACHE = HERE / "state" / "usage"
DEFAULT_PROFILES = [
    "codex-personal",
    "codex-school",
    "claude-personal",
    "claude-school",
    "claude-school-legacy",
    "agy",
]
CACHE_SCHEMA_VERSION = 2
MAX_STDERR_BYTES = 65536
MAX_STDOUT_BUFFER_BYTES = 8 * 1024 * 1024


class UsageError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def iso_from_epoch(value: int) -> str:
    try:
        return dt.datetime.fromtimestamp(value, dt.timezone.utc).isoformat(timespec="seconds")
    except (OverflowError, OSError, ValueError) as exc:
        raise UsageError(f"Invalid epoch {value!r}: {exc}") from exc


def strict_int(value: object, label: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise UsageError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise UsageError(f"{label} must be >= {minimum}")
    return value


def strict_number(value: object, label: str, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise UsageError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not low <= result <= high:
        raise UsageError(f"{label} must be finite and in [{low}, {high}]")
    return result


def validate_future_epoch(
    value: object,
    label: str,
    now_epoch: int,
    duration_minutes: int | None = None,
) -> int:
    epoch = strict_int(value, label, 1)
    if epoch < now_epoch - 5:
        raise UsageError(f"{label} is in the past")
    if duration_minutes is not None:
        latest = now_epoch + duration_minutes * 60 + 3600
        if epoch > latest:
            raise UsageError(f"{label} is implausibly later than its window")
    return epoch


def trusted_login_home() -> tuple[Path, Path]:
    try:
        logical = Path(pwd.getpwuid(os.getuid()).pw_dir)
    except (KeyError, OSError) as exc:
        raise UsageError("Cannot determine the login home from passwd") from exc
    if not logical.is_absolute() or not logical.exists() or not logical.is_dir():
        raise UsageError(f"Invalid login home: {logical}")
    try:
        physical = logical.resolve(strict=True)
    except OSError as exc:
        raise UsageError(f"Cannot resolve login home {logical}: {exc}") from exc
    if physical.stat().st_uid != os.getuid():
        raise UsageError(f"Physical login home is not owned by uid {os.getuid()}: {physical}")
    return logical, physical


def validate_account_home(profile_name: str, profile: dict) -> tuple[Path, Path]:
    raw = profile.get("home")
    if not isinstance(raw, str) or not raw.startswith("~/") or "$" in raw:
        raise UsageError(f"{profile_name} home must be a literal ~/... path")
    relative = Path(raw[2:])
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise UsageError(f"Unsafe home path for {profile_name}: {raw}")
    logical_root, physical_root = trusted_login_home()
    logical = logical_root / relative
    current = logical_root
    for part in relative.parts:
        current = current / part
        try:
            if current.is_symlink():
                raise UsageError(f"Account home contains a symlink below login home: {current}")
        except OSError as exc:
            raise UsageError(f"Cannot inspect account-home component {current}: {exc}") from exc
    if not logical.exists() or not logical.is_dir():
        raise UsageError(f"Account home does not exist: {logical}")
    try:
        physical = logical.resolve(strict=True)
        physical.relative_to(physical_root)
    except (OSError, ValueError) as exc:
        raise UsageError(f"Account home escapes physical login home: {logical}") from exc
    if physical.stat().st_uid != os.getuid():
        raise UsageError(f"Account home is not owned by uid {os.getuid()}: {physical}")
    expected = profile_name.split("-", 1)[0]
    if profile.get("provider") != expected:
        raise UsageError(
            f"Canonical profile {profile_name} has provider {profile.get('provider')!r}, expected {expected!r}"
        )
    return logical, physical


def validate_profile_homes(profiles: dict, names: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    seen: dict[Path, str] = {}
    for name in names:
        profile = agentctl.get_profile(profiles, name)
        if profile["provider"] not in {"codex", "claude"}:
            continue
        logical, physical = validate_account_home(name, profile)
        if physical in seen:
            raise UsageError(f"Profiles {seen[physical]} and {name} share one real account home")
        seen[physical] = name
        result[name] = logical
    return result


def send_message(process: subprocess.Popen, message: dict) -> None:
    if process.stdin is None:
        raise UsageError("Codex app-server stdin is unavailable")
    payload = json.dumps(message, separators=(",", ":"), allow_nan=False).encode() + b"\n"
    try:
        process.stdin.write(payload)
        process.stdin.flush()
    except (BrokenPipeError, OSError) as exc:
        raise UsageError(f"Codex app-server stdin failed: {exc}") from exc


class JsonLineReader:
    """Nonblocking JSON-line reader with bounded stdout/stderr buffers."""

    def __init__(self, process: subprocess.Popen):
        if process.stdout is None or process.stderr is None:
            raise UsageError("Codex app-server pipes are unavailable")
        self.process = process
        self.selector = selectors.DefaultSelector()
        self.stdout = process.stdout
        self.stderr = process.stderr
        os.set_blocking(self.stdout.fileno(), False)
        os.set_blocking(self.stderr.fileno(), False)
        self.selector.register(self.stdout, selectors.EVENT_READ, "stdout")
        self.selector.register(self.stderr, selectors.EVENT_READ, "stderr")
        self.stdout_buffer = bytearray()
        self.stderr_buffer = bytearray()
        self.stdout_open = True
        self.stderr_open = True

    def close(self) -> None:
        self.selector.close()

    def stderr_text(self) -> str:
        return bytes(self.stderr_buffer).decode("utf-8", errors="replace")[-4096:]

    def _read_ready(self, fileobj, kind: str) -> None:
        try:
            chunk = os.read(fileobj.fileno(), 65536)
        except BlockingIOError:
            return
        if not chunk:
            with contextlib.suppress(Exception):
                self.selector.unregister(fileobj)
            if kind == "stdout":
                self.stdout_open = False
            else:
                self.stderr_open = False
            return
        if kind == "stderr":
            self.stderr_buffer.extend(chunk)
            if len(self.stderr_buffer) > MAX_STDERR_BYTES:
                del self.stderr_buffer[:-MAX_STDERR_BYTES]
        else:
            self.stdout_buffer.extend(chunk)
            if len(self.stdout_buffer) > MAX_STDOUT_BUFFER_BYTES:
                raise UsageError("Codex app-server stdout exceeded the bounded protocol buffer")

    def _messages(self):
        while True:
            newline = self.stdout_buffer.find(b"\n")
            if newline < 0:
                return
            raw = bytes(self.stdout_buffer[:newline])
            del self.stdout_buffer[: newline + 1]
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise UsageError("Malformed JSON from Codex app-server") from exc
            if not isinstance(value, dict):
                raise UsageError("Non-object JSON from Codex app-server")
            yield value

    def response(self, request_id: int, deadline: float) -> dict:
        while True:
            for message in self._messages():
                if message.get("id") != request_id:
                    continue
                if "error" in message:
                    raise UsageError(f"Codex app-server error: {message['error']}")
                result = message.get("result")
                if not isinstance(result, dict):
                    raise UsageError("Codex app-server returned a non-object result")
                return result
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise UsageError(
                    f"Timed out waiting for Codex app-server request {request_id}; stderr={self.stderr_text()!r}"
                )
            events = self.selector.select(remaining)
            for key, _mask in events:
                self._read_ready(key.fileobj, key.data)
            if not events and time.monotonic() >= deadline:
                continue
            if not self.stdout_open:
                rc = self.process.poll()
                if rc is None:
                    rc = "running"
                raise UsageError(
                    f"Codex app-server EOF before response {request_id} (rc={rc}); stderr={self.stderr_text()!r}"
                )


def cleanup_process(process: subprocess.Popen) -> None:
    with contextlib.suppress(BrokenPipeError, OSError):
        if process.stdin is not None:
            process.stdin.close()
    try:
        if process.poll() is None:
            with contextlib.suppress(ProcessLookupError, OSError):
                process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                with contextlib.suppress(ProcessLookupError, OSError):
                    process.kill()
                process.wait(timeout=3)
    finally:
        for stream in (process.stdout, process.stderr):
            with contextlib.suppress(OSError):
                if stream is not None:
                    stream.close()


def read_codex_rate_limits(profile: dict, account_home: Path, timeout: float = 12.0) -> dict:
    if not math.isfinite(timeout) or timeout <= 0:
        raise UsageError("Codex app-server timeout must be finite and positive")
    env = os.environ.copy()
    env["CODEX_HOME"] = str(account_home)
    process = subprocess.Popen(
        ["codex", "app-server", "--listen", "stdio://"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        bufsize=0,
        env=env,
    )
    reader: JsonLineReader | None = None
    try:
        reader = JsonLineReader(process)
        deadline = time.monotonic() + timeout
        send_message(
            process,
            {
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {
                        "name": "persistent-orchestrator-usage",
                        "version": "2.0",
                    }
                },
            },
        )
        reader.response(1, deadline)
        send_message(process, {"method": "initialized", "params": {}})
        send_message(process, {"id": 2, "method": "account/rateLimits/read"})
        return reader.response(2, deadline)
    finally:
        if reader is not None:
            reader.close()
        cleanup_process(process)


def normalize_codex(
    profile_name: str,
    raw: dict,
    policy: dict,
    now_epoch: int | None = None,
) -> dict:
    if not isinstance(raw, dict):
        raise UsageError("Codex rate-limit response must be an object")
    now = int(time.time()) if now_epoch is None else strict_int(now_epoch, "now_epoch", 1)
    by_id = raw.get("rateLimitsByLimitId")
    if isinstance(by_id, dict) and isinstance(by_id.get("codex"), dict):
        limits = by_id["codex"]
    else:
        limits = raw.get("rateLimits")
    if not isinstance(limits, dict):
        raise UsageError("Codex response has no recognized rate-limit envelope")
    plan_type = limits.get("planType")
    if not isinstance(plan_type, str) or not plan_type.strip():
        raise UsageError("Codex planType must be a nonempty string")

    windows: dict[str, dict] = {}
    duration_names = {300: "five_hour", 10080: "seven_day"}
    for fallback in ("primary", "secondary"):
        window = limits.get(fallback)
        if window is None:
            continue
        if not isinstance(window, dict):
            raise UsageError(f"Codex {fallback} window must be an object")
        duration = strict_int(window.get("windowDurationMins"), f"{fallback}.windowDurationMins", 1)
        if duration not in duration_names:
            raise UsageError(f"Unexpected Codex window duration: {duration}")
        name = duration_names[duration]
        if name in windows:
            raise UsageError(f"Duplicate Codex {name} window")
        used = strict_number(window.get("usedPercent"), f"{fallback}.usedPercent", 0, 100)
        reset = validate_future_epoch(window.get("resetsAt"), f"{fallback}.resetsAt", now, duration)
        windows[name] = {
            "used_percent": used,
            "remaining_percent": 100.0 - used,
            "window_duration_minutes": duration,
            "resets_at_epoch": reset,
            "resets_at_utc": iso_from_epoch(reset),
        }
    if "seven_day" not in windows:
        raise UsageError("Codex response lacks the required seven-day window")

    reset_summary = raw.get("rateLimitResetCredits")
    if not isinstance(reset_summary, dict):
        raise UsageError("Codex response lacks reset-credit data")
    available_count = strict_int(reset_summary.get("availableCount"), "availableCount", 0)
    raw_credits = reset_summary.get("credits")
    if not isinstance(raw_credits, list):
        raise UsageError("Reset-credit credits must be a list")
    credits = []
    valid_available = 0
    for index, credit in enumerate(raw_credits):
        if not isinstance(credit, dict):
            raise UsageError(f"Reset credit {index} must be an object")
        title = credit.get("title")
        status = credit.get("status")
        if not isinstance(title, str) or not isinstance(status, str):
            raise UsageError(f"Reset credit {index} has invalid title/status")
        expiry = validate_future_epoch(credit.get("expiresAt"), f"credit[{index}].expiresAt", now)
        if expiry <= now:
            raise UsageError(f"credit[{index}].expiresAt is not strictly in the future")
        if status == "available":
            if title != "Full reset":
                raise UsageError(f"Available reset credit {index} is not a Full reset")
            valid_available += 1
        credits.append(
            {
                "title": title,
                "status": status,
                "expires_at_epoch": expiry,
                "expires_at_utc": iso_from_epoch(expiry),
            }
        )
    violations: list[str] = []
    if valid_available != available_count:
        violations.append(
            f"availableCount={available_count} disagrees with {valid_available} valid available Full reset records"
        )
    reserve = policy["codex_personal_reset_credit_reserve"] if profile_name == "codex-personal" else 0
    if valid_available < reserve:
        violations.append(
            f"personal reset-credit reserve fell below {reserve}: {valid_available} independently valid"
        )
    warnings: list[str] = []
    if "five_hour" not in windows:
        warnings.append("five-hour window is absent from the live response; short-window capacity is unknown")
    weekly_remaining = windows["seven_day"]["remaining_percent"]
    threshold = policy["seven_day_low_remaining_percent"]
    if weekly_remaining <= threshold:
        warnings.append(
            f"seven-day remaining is {weekly_remaining:g}%, at or below {threshold:g}%"
        )
    return {
        "provider": "codex",
        "status": "blocked" if violations else "ok",
        "source": "live codex app-server account/rateLimits/read",
        "observed_at_utc": utc_now(),
        "plan_type": plan_type,
        "windows": windows,
        "reset_credits": {
            "available_count": available_count,
            "valid_available_full_reset_count": valid_available,
            "credits": credits,
            "protected_reserve": reserve,
            "automatic_consumption_allowed": False,
        },
        "warnings": warnings,
        "violations": violations,
    }


def claude_cache_path(cache_dir: Path, profile_name: str) -> Path:
    agentctl.safe_role(profile_name)
    return cache_dir / f"{profile_name}.json"


def normalize_claude_payload(rate_limits: object, now_epoch: int) -> dict[str, dict]:
    if not isinstance(rate_limits, dict):
        raise UsageError("Claude rate_limits must be an object")
    windows: dict[str, dict] = {}
    durations = {"five_hour": 300, "seven_day": 10080}
    for name, duration in durations.items():
        window = rate_limits.get(name)
        if window is None:
            continue
        if not isinstance(window, dict):
            raise UsageError(f"Claude {name} window must be an object")
        used = strict_number(window.get("used_percentage"), f"Claude {name}.used_percentage", 0, 100)
        reset = validate_future_epoch(window.get("resets_at"), f"Claude {name}.resets_at", now_epoch, duration)
        windows[name] = {"used_percentage": used, "resets_at": reset}
    if not windows:
        raise UsageError("Claude rate_limits contains no usable window")
    return windows


def claude_snapshot_signature(profile_name: str, rate_limits: dict) -> str:
    signed = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "provider": "claude",
        "profile": profile_name,
        "rate_limits": rate_limits,
    }
    return hashlib.sha256(
        json.dumps(signed, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def valid_existing_claude_windows(
    snapshot: object,
    profile_name: str,
    now_epoch: int,
) -> dict[str, dict]:
    """Return integrity-checked cached windows suitable for a recorder merge."""
    if not isinstance(snapshot, dict):
        return {}
    if (
        snapshot.get("schema_version") != CACHE_SCHEMA_VERSION
        or snapshot.get("provider") != "claude"
        or snapshot.get("profile") != profile_name
        or not isinstance(snapshot.get("rate_limits"), dict)
    ):
        return {}
    rate_limits = snapshot["rate_limits"]
    if snapshot.get("snapshot_signature") != claude_snapshot_signature(profile_name, rate_limits):
        return {}
    result: dict[str, dict] = {}
    durations = {"five_hour": 300, "seven_day": 10080}
    for name, value in rate_limits.items():
        if name not in durations or not isinstance(value, dict):
            return {}
        try:
            used = strict_number(value.get("used_percentage"), f"cached Claude {name}.used_percentage", 0, 100)
            reset = strict_int(value.get("resets_at"), f"cached Claude {name}.resets_at", 1)
            observed = strict_int(
                value.get("observed_at_epoch"),
                f"cached Claude {name}.observed_at_epoch",
                1,
            )
            if observed > now_epoch + 5:
                return {}
            validate_future_epoch(reset, f"cached Claude {name}.resets_at", observed, durations[name])
        except UsageError:
            return {}
        result[name] = {
            "used_percentage": used,
            "resets_at": reset,
            "observed_at_epoch": observed,
            "observed_at_utc": value.get("observed_at_utc"),
        }
    return result


def record_claude(profile_name: str, cache_dir: Path) -> None:
    if profile_name not in {"claude-personal", "claude-school", "claude-school-legacy"}:
        raise UsageError(f"Invalid Claude cache profile: {profile_name}")
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise UsageError("Claude status-line input must be a JSON object")
    now_epoch = int(time.time())
    path = claude_cache_path(cache_dir, profile_name)
    try:
        incoming = normalize_claude_payload(payload.get("rate_limits"), now_epoch)
    except UsageError:
        print("[Claude usage unavailable; prior cache preserved]")
        return
    try:
        existing = agentctl.load_json(path, {})
    except (agentctl.AgentCtlError, OSError, json.JSONDecodeError, ValueError, TypeError):
        existing = {}
    existing_windows = valid_existing_claude_windows(existing, profile_name, now_epoch)
    merged = dict(existing_windows)
    changed = False
    observed_utc = utc_now()
    for name, value in incoming.items():
        old = existing_windows.get(name)
        if old and old.get("used_percentage") == value["used_percentage"] and old.get("resets_at") == value["resets_at"]:
            continue
        merged[name] = {
            **value,
            "observed_at_epoch": now_epoch,
            "observed_at_utc": observed_utc,
        }
        changed = True
    if existing_windows and not changed:
        print("[Claude usage unchanged; per-window cache timestamps preserved]")
        return
    if not merged:
        print("[Claude usage unavailable; prior cache preserved]")
        return
    model = payload.get("model")
    display_name = model.get("display_name") if isinstance(model, dict) else None
    if not isinstance(display_name, str) and isinstance(existing, dict):
        display_name = existing.get("model")
    ordered = {name: merged[name] for name in sorted(merged)}
    snapshot = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "provider": "claude",
        "profile": profile_name,
        "model": display_name if isinstance(display_name, str) else None,
        "rate_limits": ordered,
        "snapshot_signature": claude_snapshot_signature(profile_name, ordered),
    }
    agentctl.atomic_write_json(path, snapshot)
    parts = [f"[{snapshot['model'] or 'Claude'}]"]
    for key, label in (("five_hour", "5h"), ("seven_day", "7d")):
        window = incoming.get(key)
        if window:
            parts.append(f"{label}:{window['used_percentage']:.0f}% used")
    print(" | ".join(parts))


def read_claude_cache(profile_name: str, cache_dir: Path, policy: dict) -> dict:
    path = claude_cache_path(cache_dir, profile_name)
    if not path.exists():
        return {
            "provider": "claude",
            "status": "missing",
            "source": "Claude status-line cache",
            "windows": {},
            "warnings": ["Claude usage cache is missing; capacity is unknown"],
            "violations": [],
        }
    snapshot = agentctl.load_json(path)
    if not isinstance(snapshot, dict):
        raise UsageError(f"Claude cache must be an object: {path}")
    if snapshot.get("schema_version") != CACHE_SCHEMA_VERSION:
        raise UsageError(f"Claude cache schema mismatch: {path}")
    if snapshot.get("provider") != "claude" or snapshot.get("profile") != profile_name:
        raise UsageError(f"Claude cache provider/profile mismatch: {path}")
    rate_limits = snapshot.get("rate_limits")
    if not isinstance(rate_limits, dict) or not rate_limits:
        raise UsageError(f"Claude cache contains no windows: {path}")
    if snapshot.get("snapshot_signature") != claude_snapshot_signature(profile_name, rate_limits):
        raise UsageError(f"Claude cache signature mismatch: {path}")
    now_epoch = int(time.time())
    max_age = policy["claude_cache_max_age_seconds"]
    durations = {"five_hour": 300, "seven_day": 10080}
    windows: dict[str, dict] = {}
    warnings: list[str] = []
    ages: list[int] = []
    observed_times: list[str] = []
    for name, value in rate_limits.items():
        if name not in durations or not isinstance(value, dict):
            raise UsageError(f"Claude cache has an invalid window: {name!r}")
        used = strict_number(value.get("used_percentage"), f"Claude {name}.used_percentage", 0, 100)
        reset = strict_int(value.get("resets_at"), f"Claude {name}.resets_at", 1)
        observed = strict_int(value.get("observed_at_epoch"), f"Claude {name}.observed_at_epoch", 1)
        if observed > now_epoch + 5:
            raise UsageError(f"Claude {name} cache is dated in the future: {path}")
        validate_future_epoch(reset, f"Claude {name}.resets_at", observed, durations[name])
        age = max(now_epoch - observed, 0)
        ages.append(age)
        observed_utc = value.get("observed_at_utc")
        if isinstance(observed_utc, str):
            observed_times.append(observed_utc)
        if age > max_age:
            warnings.append(f"Claude {name} snapshot is stale; that window is unknown")
            continue
        if reset < now_epoch - 5:
            warnings.append(f"Claude {name} reset has passed; that window is unknown")
            continue
        windows[name] = {
            "used_percent": used,
            "remaining_percent": 100.0 - used,
            "resets_at_epoch": reset,
            "resets_at_utc": iso_from_epoch(reset),
            "observed_at_epoch": observed,
            "observed_at_utc": observed_utc,
            "age_seconds": age,
        }
    if not windows:
        status = "stale"
        warnings.append("Claude has no fresh actionable window; capacity is unknown")
    elif len(windows) != len(durations):
        status = "partial"
        warnings.append("Claude has only a partial fresh usage snapshot; missing capacity is unknown")
    else:
        status = "ok"
    return {
        "provider": "claude",
        "status": status,
        "source": "Claude status-line cache",
        "observed_at_utc": max(observed_times) if observed_times else None,
        "age_seconds": min(ages) if ages else None,
        "model": snapshot.get("model"),
        "windows": windows,
        "warnings": warnings,
        "violations": [],
    }


def install_claude_statusline(
    profile_name: str,
    profile: dict,
    account_home: Path,
    cache_dir: Path,
    replace: bool,
) -> Path:
    if profile.get("provider") != "claude":
        raise UsageError(f"{profile_name} is not a Claude profile")
    settings_path = account_home / ".claude" / "settings.json"
    script = Path(__file__).resolve()
    command = " ".join(
        [
            shlex.quote("/usr/bin/python3.11"),
            shlex.quote(str(script)),
            "record-claude",
            "--profile",
            shlex.quote(profile_name),
            "--cache-dir",
            shlex.quote(str(cache_dir.resolve())),
        ]
    )
    desired = {"type": "command", "command": command}
    with agentctl.exclusive_lock(settings_path.with_suffix(".json.lock")):
        settings = agentctl.load_json(settings_path, {})
        if not isinstance(settings, dict):
            raise UsageError(f"Claude settings must be a JSON object: {settings_path}")
        existing = settings.get("statusLine")
        if "statusLine" in settings and existing != desired and not replace:
            raise UsageError(
                f"{settings_path} already has a different statusLine; use --replace only after review"
            )
        settings["statusLine"] = desired
        agentctl.atomic_write_json(settings_path, settings)
    return settings_path


def load_policy(path: Path) -> dict:
    value = agentctl.load_json(path)
    if not isinstance(value, dict):
        raise UsageError(f"Usage policy must be a JSON object: {path}")
    expected = {
        "schema_version",
        "claude_cache_max_age_seconds",
        "codex_personal_reset_credit_reserve",
        "never_consume_codex_reset_credits_automatically",
        "seven_day_low_remaining_percent",
        "required_codex_profiles",
        "profile_account_groups",
    }
    if set(value) != expected:
        raise UsageError(f"Usage policy keys mismatch: expected {sorted(expected)}")
    if strict_int(value["schema_version"], "policy.schema_version", 1) != 1:
        raise UsageError("Unsupported usage-policy schema version")
    strict_int(value["claude_cache_max_age_seconds"], "policy.claude_cache_max_age_seconds", 1)
    reserve = strict_int(
        value["codex_personal_reset_credit_reserve"],
        "policy.codex_personal_reset_credit_reserve",
        2,
    )
    if reserve < 2:
        raise UsageError("Policy must preserve at least two personal reset credits")
    if value["never_consume_codex_reset_credits_automatically"] is not True:
        raise UsageError("Policy must forbid automatic reset-credit consumption")
    strict_number(
        value["seven_day_low_remaining_percent"],
        "policy.seven_day_low_remaining_percent",
        0,
        100,
    )
    required = value["required_codex_profiles"]
    if required != ["codex-personal", "codex-school"]:
        raise UsageError("Policy required_codex_profiles must be codex-personal and codex-school")
    groups = value["profile_account_groups"]
    if not isinstance(groups, dict) or set(groups) != {"claude-school"}:
        raise UsageError("Policy must define the claude-school shared-account group")
    aliases = groups["claude-school"]
    if aliases != ["claude-school", "claude-school-legacy"]:
        raise UsageError(
            "Policy claude-school account aliases must be claude-school and claude-school-legacy"
        )
    return value


def profile_error(provider: str | None, message: str) -> dict:
    return {
        "provider": provider,
        "status": "error",
        "source": "usagectl validation",
        "windows": {},
        "warnings": [],
        "violations": [message],
    }


def consolidate_account_groups(profiles: dict, groups: dict) -> dict:
    """Merge profile aliases into one non-additive account-capacity view.

    Claude status-line caches are written by profile home, but two homes can
    authenticate the same provider account.  For each window, the most recent
    valid observation is authoritative.  Alias percentages are never summed.
    """
    accounts: dict[str, dict] = {}
    for account_id, aliases in groups.items():
        if not isinstance(aliases, list) or len(aliases) < 2 or len(set(aliases)) != len(aliases):
            raise UsageError(f"Invalid alias inventory for account group {account_id}")
        members = []
        for name in aliases:
            value = profiles.get(name)
            if not isinstance(value, dict):
                raise UsageError(f"Account group {account_id} is missing profile {name}")
            if value.get("provider") != "claude":
                raise UsageError(f"Account group {account_id} contains non-Claude profile {name}")
            value["account_id"] = account_id
            value["capacity_is_shared"] = True
            value["account_aliases"] = list(aliases)
            members.append((name, value))

        merged_windows: dict[str, dict] = {}
        window_sources: dict[str, str] = {}
        warnings = [
            f"Profiles {', '.join(aliases)} share one provider account; capacity must not be summed"
        ]
        for window_name in ("five_hour", "seven_day"):
            candidates = []
            for name, value in members:
                window = (value.get("windows") or {}).get(window_name)
                if not isinstance(window, dict):
                    continue
                observed = window.get("observed_at_epoch")
                if isinstance(observed, bool) or not isinstance(observed, int):
                    continue
                candidates.append((observed, name, window))
            if not candidates:
                continue
            candidates.sort(
                key=lambda item: (item[0], item[2].get("used_percent", -1), item[1])
            )
            observed, selected_name, selected = candidates[-1]
            merged_windows[window_name] = dict(selected)
            window_sources[window_name] = selected_name
            same_reset = [
                (old_observed, old_name, old)
                for old_observed, old_name, old in candidates[:-1]
                if old.get("resets_at_epoch") == selected.get("resets_at_epoch")
            ]
            if any(
                old_observed <= observed
                and old.get("used_percent", -1) > selected.get("used_percent", -1)
                for old_observed, _old_name, old in same_reset
            ):
                warnings.append(
                    f"{window_name} alias observations are non-monotonic; using freshest profile {selected_name}"
                )

        if not merged_windows:
            status = "unknown"
            warnings.append("No fresh alias cache supplies actionable account capacity")
        elif len(merged_windows) < 2:
            status = "partial"
            warnings.append("Shared Claude account has only a partial fresh usage snapshot")
        else:
            status = "ok"
        accounts[account_id] = {
            "provider": "claude",
            "status": status,
            "source": "freshest per-window Claude alias cache",
            "profiles": list(aliases),
            "windows": merged_windows,
            "window_sources": window_sources,
            "warnings": warnings,
            "violations": [],
        }
    return accounts


def snapshot_changes(previous: object, current: dict) -> list[dict]:
    if not isinstance(previous, dict) or not isinstance(previous.get("profiles"), dict):
        return [{"field": "baseline", "old": None, "new": "created"}]
    changes = []
    profile_targets = ("codex-personal", "codex-school", "claude-personal")
    targets = [
        (
            profile_name,
            (previous.get("profiles") or {}).get(profile_name) or {},
            (current.get("profiles") or {}).get(profile_name) or {},
        )
        for profile_name in profile_targets
    ]
    account_ids = sorted(
        set((previous.get("accounts") or {})) | set((current.get("accounts") or {}))
    )
    targets.extend(
        (
            f"account:{account_id}",
            (previous.get("accounts") or {}).get(account_id) or {},
            (current.get("accounts") or {}).get(account_id) or {},
        )
        for account_id in account_ids
    )
    paths = {
        "status": lambda item: item.get("status"),
        "plan_type": lambda item: item.get("plan_type"),
        "five_hour.remaining_percent": lambda item: ((item.get("windows") or {}).get("five_hour") or {}).get("remaining_percent"),
        "five_hour.resets_at_utc": lambda item: ((item.get("windows") or {}).get("five_hour") or {}).get("resets_at_utc"),
        "seven_day.remaining_percent": lambda item: ((item.get("windows") or {}).get("seven_day") or {}).get("remaining_percent"),
        "seven_day.resets_at_utc": lambda item: ((item.get("windows") or {}).get("seven_day") or {}).get("resets_at_utc"),
        "reset_credits.available_count": lambda item: (item.get("reset_credits") or {}).get("available_count"),
    }
    for profile_name, old, new in targets:
        for field, getter in paths.items():
            old_value, new_value = getter(old), getter(new)
            if old_value != new_value:
                changes.append(
                    {"profile": profile_name, "field": field, "old": old_value, "new": new_value}
                )
    return changes


def snapshot(args: argparse.Namespace) -> dict:
    profiles = agentctl.load_profiles(Path(args.config))
    policy = load_policy(Path(args.policy))
    selected = list(args.profile or DEFAULT_PROFILES)
    top_violations: list[str] = []
    if args.profile:
        top_violations.append("Partial --profile snapshots are advisory and cannot pass the dispatch gate")
    required_codex = policy["required_codex_profiles"]
    for required in required_codex:
        if required not in selected:
            top_violations.append(f"Required profile omitted: {required}")
    try:
        homes = validate_profile_homes(profiles, selected)
        home_error = None
    except (UsageError, agentctl.AgentCtlError) as exc:
        homes = {}
        home_error = str(exc)
        top_violations.append(home_error)
    result = {
        "schema_version": 1,
        "observed_at_utc": utc_now(),
        "policy": policy,
        "profiles": {},
        "accounts": {},
        "warnings": [],
        "policy_violations": top_violations,
        "changes": [],
        "gate_ok": False,
    }
    for name in selected:
        try:
            profile = agentctl.get_profile(profiles, name)
            if home_error and profile["provider"] in {"codex", "claude"}:
                raise UsageError(home_error)
            if profile["provider"] == "codex":
                raw = read_codex_rate_limits(profile, homes[name], timeout=args.timeout)
                value = normalize_codex(name, raw, policy)
            elif profile["provider"] == "claude":
                value = read_claude_cache(name, Path(args.cache_dir), policy)
            else:
                value = {
                    "provider": "agy",
                    "status": "unknown",
                    "source": "no usage API in installed agy CLI",
                    "windows": {},
                    "warnings": ["agy usage is unknown; use heartbeat/cap evidence"],
                    "violations": [],
                }
        except Exception as exc:
            provider = profiles.get(name, {}).get("provider") if isinstance(profiles.get(name), dict) else None
            value = profile_error(provider, str(exc))
        result["profiles"][name] = value
        result["warnings"].extend(f"{name}: {item}" for item in value.get("warnings", []))
        if value.get("violations"):
            result["policy_violations"].extend(
                f"{name}: {item}" for item in value.get("violations", [])
            )
    try:
        result["accounts"] = consolidate_account_groups(
            result["profiles"], policy["profile_account_groups"]
        )
    except UsageError as exc:
        result["policy_violations"].append(str(exc))
    for account_id, value in result["accounts"].items():
        result["warnings"].extend(
            f"account {account_id}: {item}" for item in value.get("warnings", [])
        )
    for name in required_codex:
        value = result["profiles"].get(name)
        if not value or value.get("status") != "ok":
            marker = f"Required Codex profile did not validate: {name}"
            if marker not in result["policy_violations"]:
                result["policy_violations"].append(marker)
    result["gate_ok"] = not result["policy_violations"]
    state_path = Path(args.cache_dir) / "last-valid-snapshot.json"
    previous = agentctl.load_json(state_path, {})
    result["changes"] = snapshot_changes(previous, result)
    if result["gate_ok"] and not args.profile:
        agentctl.atomic_write_json(state_path, result)
    return result


def cell(value: object) -> str:
    return "—" if value is None else str(value)


def print_table(value: dict) -> None:
    headers = ["PROFILE", "STATUS", "5H REM", "7D REM", "7D RESET UTC", "RESET CREDITS", "SOURCE"]
    rows = []
    for name, item in value["profiles"].items():
        windows = item.get("windows") or {}
        five = windows.get("five_hour") or {}
        seven = windows.get("seven_day") or {}
        credits = (item.get("reset_credits") or {}).get("available_count")
        rows.append(
            [
                name,
                item.get("status"),
                cell(five.get("remaining_percent")),
                cell(seven.get("remaining_percent")),
                cell(seven.get("resets_at_utc")),
                cell(credits),
                item.get("source") or "—",
            ]
        )
    widths = [max(len(str(row[index])) for row in [headers, *rows]) for index in range(len(headers))]
    print("  ".join(str(item).ljust(widths[index]) for index, item in enumerate(headers)))
    for row in rows:
        print("  ".join(str(item).ljust(widths[index]) for index, item in enumerate(row)))
    account_rows = []
    for account_id, item in value.get("accounts", {}).items():
        windows = item.get("windows") or {}
        five = windows.get("five_hour") or {}
        seven = windows.get("seven_day") or {}
        account_rows.append(
            [
                account_id,
                item.get("status"),
                cell(five.get("remaining_percent")),
                cell(seven.get("remaining_percent")),
                cell(five.get("resets_at_utc")),
                ",".join(f"{key}:{name}" for key, name in (item.get("window_sources") or {}).items()),
            ]
        )
    if account_rows:
        print()
        account_headers = ["SHARED ACCOUNT", "STATUS", "5H REM", "7D REM", "5H RESET UTC", "WINDOW SOURCES"]
        account_widths = [
            max(len(str(row[index])) for row in [account_headers, *account_rows])
            for index in range(len(account_headers))
        ]
        print(
            "  ".join(
                str(item).ljust(account_widths[index])
                for index, item in enumerate(account_headers)
            )
        )
        for row in account_rows:
            print(
                "  ".join(
                    str(item).ljust(account_widths[index])
                    for index, item in enumerate(row)
                )
            )
    print(f"GATE_OK {str(value['gate_ok']).lower()}")
    for warning in value.get("warnings", []):
        print(f"WARNING {warning}", file=sys.stderr)
    for violation in value.get("policy_violations", []):
        print(f"POLICY_VIOLATION {violation}", file=sys.stderr)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("snapshot", help="Read all available usage data")
    show.add_argument("--config", default=str(DEFAULT_CONFIG))
    show.add_argument("--policy", default=str(DEFAULT_POLICY))
    show.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    show.add_argument("--profile", action="append")
    show.add_argument("--timeout", type=float, default=12.0)
    show.add_argument("--json", action="store_true")

    record = subparsers.add_parser("record-claude", help="Record Claude status-line JSON from stdin")
    record.add_argument("--profile", required=True)
    record.add_argument("--cache-dir", default=str(DEFAULT_CACHE))

    install = subparsers.add_parser("install-claude-statusline", help="Install the Claude usage recorder")
    install.add_argument("--config", default=str(DEFAULT_CONFIG))
    install.add_argument("--profile", required=True)
    install.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    install.add_argument("--replace", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "snapshot":
            value = snapshot(args)
            if args.json:
                print(json.dumps(value, indent=2, sort_keys=True, allow_nan=False))
            else:
                print_table(value)
            return 0 if value["gate_ok"] else 3
        if args.command == "record-claude":
            record_claude(args.profile, Path(args.cache_dir))
            return 0
        profiles = agentctl.load_profiles(Path(args.config))
        profile = agentctl.get_profile(profiles, args.profile)
        logical, _physical = validate_account_home(args.profile, profile)
        path = install_claude_statusline(
            args.profile, profile, logical, Path(args.cache_dir), args.replace
        )
        print(path)
        return 0
    except (UsageError, agentctl.AgentCtlError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"usagectl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
