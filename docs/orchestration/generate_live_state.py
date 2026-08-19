#!/usr/bin/python3.11
"""Generate the concise orchestration dashboard from live and machine sources."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from typing import Any

from slurm_array_status import build_snapshot, expand_spec


HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_CONFIG = HERE / "state" / "live-state.json"
DEFAULT_OUTPUT = HERE / "LIVE-STATE.md"
MAX_LINES = 120
# Kinds whose watch has a SLURM SUBJECT that can be checked for existence.
WATCH_SUBJECT_KINDS = {"slurm-job", "slurm-array"}
# Used only when the managed scrontab block cannot be read or parsed, and always
# rendered with the word "assumed" so it is never mistaken for an observation.
# It matches `wakerctl cron --interval-minutes`' default (wakerctl.py argparse).
ASSUMED_TICK_INTERVAL_MINUTES = 5
# Three severities, because two are not enough: a check that can only say
# PASS/FAIL has to call "I could not look" one of them, and BEN-323 is what
# happens when it picks PASS.
QUIET, NO_EVIDENCE, LOUD = "quiet", "no-evidence", "loud"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def run_text(command: list[str], *, check: bool = True) -> str:
    result = subprocess.run(command, cwd=REPO, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}: {result.stderr.strip()}")
    return result.stdout


def usage_snapshot() -> tuple[dict[str, Any], int]:
    result = subprocess.run(
        [sys.executable, str(HERE / "usagectl.py"), "snapshot", "--json"],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    try:
        return json.loads(result.stdout), result.returncode
    except json.JSONDecodeError:
        return {"gate_ok": False, "warnings": [f"usage snapshot unavailable (rc={result.returncode})"]}, result.returncode


def validate_owners(config: dict[str, Any], sessions: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    registry = sessions.get("sessions", {})
    for owner in config["owners"]:
        role = owner["role"]
        if role not in registry:
            raise RuntimeError(f"configured owner role missing from registry: {role}")
        record = registry[role]
        actual = record.get("session_id")
        if actual != owner["uuid"]:
            raise RuntimeError(f"UUID mismatch for {role}: config={owner['uuid']} registry={actual}")
        if actual in seen:
            raise RuntimeError(f"duplicate configured owner UUID: {actual}")
        seen.add(actual)
        rows.append(
            {
                "role": role,
                "provider": f"{record.get('provider','?')}/{record.get('profile','?')}",
                "uuid": actual,
                "purpose": owner["purpose"],
            }
        )
    return rows


def rel_link(repo_path: str) -> str:
    if repo_path == "superseded followup prompts":
        return repo_path
    target = pathlib.Path(repo_path)
    return os.path.relpath(REPO / target, HERE)


def codex_capacity(usage: dict[str, Any], profile: str) -> str:
    record = usage.get("profiles", {}).get(profile, {})
    window = record.get("windows", {}).get("seven_day", {})
    remaining = window.get("remaining_percent", "unknown")
    reset = window.get("resets_at_utc", "unknown")
    credits = record.get("reset_credits", {})
    available = credits.get("valid_available_full_reset_count", "unknown")
    protected = credits.get("protected_reserve", "unknown")
    return f"{remaining}% weekly remaining; reset {reset}; Full resets {available} available/{protected} protected"



# ---------------------------------------------------------------------------
# Wake-section health.
#
# EVERY verdict below is computed by calling wakerctl's own checks -- never by
# reimplementing them here. The renderer and the evaluator must not be able to
# disagree about whether a watch's subject exists or whether the ticker is
# alive; two implementations of one predicate diverge, and the divergence is
# invisible precisely because both look right in isolation. So this module owns
# the WORDS and wakerctl owns the JUDGEMENT.


def _wakerctl():
    """Imported lazily: the non-waker wake path must not pay for it."""
    import wakerctl

    return wakerctl


def classify_problems(problems: list[str]) -> str:
    """QUIET (no problems) / NO_EVIDENCE (only unobservability) / LOUD (a finding).

    A `NO EVIDENCE:` line means the check could not run. Silence and NO EVIDENCE
    must never render the same way -- that conflation is BEN-323, where an
    unreachable Slurm rendered as **ACTIVE** for 24 h.
    """
    wakerctl = _wakerctl()
    if not problems:
        return QUIET
    if all(str(item).startswith(wakerctl.NO_EVIDENCE_PREFIX) for item in problems):
        return NO_EVIDENCE
    return LOUD


def safe_health_call(function, *args) -> list[str]:
    """Run a wakerctl health check, converting unreachability into NO EVIDENCE.

    This generator is routinely run from a Mac with no `squeue`, `sacct` or
    `scrontab` on PATH, and wakerctl's checks call `ctx.runner` directly, so a
    missing binary surfaces as FileNotFoundError rather than a return code. A
    crash here would take the whole dashboard down; a swallowed exception would
    render as health. Neither is acceptable, so it becomes NO EVIDENCE.
    """
    wakerctl = _wakerctl()
    try:
        return list(function(*args))
    except OSError as exc:
        return [wakerctl.no_evidence(f"{type(exc).__name__}: {exc} (this host cannot query the scheduler)")]
    except Exception as exc:  # noqa: BLE001 -- an unassessable check is NO EVIDENCE, never PASS
        return [wakerctl.no_evidence(f"check raised {type(exc).__name__}: {exc}")]


def age_phrase(seconds: float) -> str:
    if abs(seconds) >= 7200:
        return f"{seconds / 3600.0:.1f} h"
    return f"{seconds / 60.0:.0f} min"


def watch_subject_text(watch: dict[str, Any]) -> str:
    """The watch's SUBJECT: job id, the `tasks` spec AS WRITTEN, and its expansion.

    Until 2026-08-19 a watch rendered as `id`(kind:state) and nothing else, so
    `gate5-do-train-57266000-r2` displayed as `armed` for ~45 h while its
    params were {"job_id": "57266000", "tasks": "1"} against an array whose only
    task is index 0. `tasks` is a task-id SPEC and never a count --
    expand_spec("1") == [1] -- and the expansion is printed here because that
    single fact is what nobody could see. A stored `state` field is not a
    liveness claim (BEN-456, BEN-478).
    """
    kind = watch.get("kind")
    if kind not in WATCH_SUBJECT_KINDS:
        return ""
    params = watch.get("params")
    if not isinstance(params, dict):
        # wakerctl.status() projects watches to six keys and `params` is not one
        # of them, so this is what a status-only record looks like.
        return "; subject=UNKNOWN (this record carries no `params`)"
    job_id = str(params.get("job_id", "")).strip() or "<missing>"
    if kind != "slurm-array":
        return f"; subject=job {job_id}"
    raw = str(params.get("tasks", ""))
    try:
        expanded = expand_spec(raw)
    except ValueError as exc:
        return f"; subject=job {job_id} tasks={raw!r} INVALID SPEC ({exc})"
    return f"; subject=job {job_id} tasks={raw!r} -> task ids {expanded}"


def watch_subject_verdict(watch: dict[str, Any], waker_ctx) -> tuple[str, str]:
    """Is this watch's subject OBSERVABLE? Delegated to wakerctl entirely.

    `wakerctl.watch_subject_problems` builds its snapshot with
    `slurm_array_status.build_snapshot`, the same function `evaluate()` uses, so
    the render cannot disagree with the evaluator.
    """
    if waker_ctx is None:
        return NO_EVIDENCE, "NO EVIDENCE its subject exists: Slurm was not asked in this run"
    wakerctl = _wakerctl()
    problems = safe_health_call(wakerctl.watch_subject_problems, waker_ctx, watch)
    severity = classify_problems(problems)
    detail = " | ".join(str(item) for item in problems)
    if severity == QUIET:
        return QUIET, "subject OBSERVED in Slurm"
    if severity == NO_EVIDENCE:
        return NO_EVIDENCE, f"{detail} -- NOT a claim the subject exists"
    return LOUD, f"**\u26a0 {detail}**"


def render_watch(watch: dict[str, Any], waker_ctx) -> tuple[str, str]:
    """(severity, rendered) for one watch. Never renders `state` alone."""
    wakerctl = _wakerctl()
    watch_id = watch.get("watch_id") or "<no-watch_id>"
    kind = watch.get("kind")
    state = wakerctl.watch_state(watch) or "<no-state>"
    body = f"`{watch_id}`({kind}:{state}{watch_subject_text(watch)}"
    if kind not in WATCH_SUBJECT_KINDS:
        return QUIET, body + ")"
    # WHOLE-FIELD equality, never a substring: "disarmed" CONTAINS "armed", and a
    # `grep -c '<job>.*armed'` health check has already reported 2 armed watches
    # for a job that had one armed and one disarmed (2026-08-19).
    if not wakerctl.is_armed(watch):
        return QUIET, body + "; not armed, so its subject was not probed)"
    severity, verdict = watch_subject_verdict(watch, waker_ctx)
    return severity, f"{body}; {verdict})"


def safe_load_watches(waker_ctx) -> list[dict[str, Any]]:
    try:
        return _wakerctl().load_watches(waker_ctx)
    except OSError:
        return []


def tick_interval_minutes(waker_ctx) -> tuple[int, str]:
    """(minutes, how we know) -- parsed from the managed scrontab block if readable."""
    wakerctl = _wakerctl()
    fallback = (
        ASSUMED_TICK_INTERVAL_MINUTES,
        f"{ASSUMED_TICK_INTERVAL_MINUTES} m ASSUMED (the managed scrontab block was not readable here)",
    )
    if waker_ctx is None:
        return fallback
    try:
        lines, _ = wakerctl.read_scrontab_lines(waker_ctx)
    except OSError:
        return fallback
    if lines is None:
        return fallback
    interval = wakerctl.cron_interval_minutes(lines)
    if interval is None:
        return fallback
    return interval, f"{interval} m from the managed scrontab block"


def tick_line(last_tick: dict[str, Any], waker_ctx) -> tuple[str, str]:
    """(severity, the `Last tick:` bullet) -- a VERDICT, not a transcription.

    Before 2026-08-19 this printed `Last tick: {at_utc}` verbatim. On that day it
    would have read 2026-08-17T15:05:14+00:00 against a wall clock of
    2026-08-19T12:40Z: the number that proved the supervision net was dead had
    been on the repo's first-read page, unjudged, for two days (ISSUE-52 --
    WAKER.md:52 already stated the rule in prose, and a rule that exists only as
    prose is not a control).

    BEN-199 governs the shape: the FRESH case is quiet and unalarming, because a
    check with no passing state is a check nobody reads.
    """
    wakerctl = _wakerctl()
    stamp = last_tick.get("at_utc", "never")
    node = last_tick.get("node", "unknown")
    prefix = f"- Last tick: {stamp} on {node}"
    suffix = " (scrontab is the supervision net; see WAKER.md)"
    interval, interval_source = tick_interval_minutes(waker_ctx)
    multiplier = wakerctl.DEFAULT_CRON_STALE_MULTIPLIER
    if waker_ctx is not None:
        multiplier = float(waker_ctx.config.get("cron_stale_multiplier", multiplier))
    bound = f"bound {interval * multiplier:.0f} min = {interval_source} x {multiplier:g}"

    age = None
    if waker_ctx is not None and stamp not in (None, "", "never"):
        try:
            age = waker_ctx.now() - wakerctl.parse_utc(str(stamp))
        except (TypeError, ValueError):
            age = None
    age_text = f"{age_phrase(age)} old" if age is not None else "age NOT COMPUTABLE from this stamp"

    if waker_ctx is None:
        return NO_EVIDENCE, (
            f"{prefix} -- **NO EVIDENCE ABOUT THE TICKER, AND THAT IS NOT A LIVENESS CLAIM**: this"
            f" run had no waker state dir, so neither the tick receipt nor the scrontab was read"
            f" and this timestamp is UNJUDGED.{suffix}"
        )
    # One call covers all three a0a31176 control-plane checks that bear on the
    # ticker: the managed block's presence, `check_cron_job_runnable` (is the
    # scron job RUNNABLE in Slurm, not merely scheduled), and
    # `check_tick_freshness` (is the heartbeat younger than its own interval).
    problems = safe_health_call(wakerctl.check_cron_ticker, waker_ctx)
    severity = classify_problems(problems)
    if severity == QUIET:
        return QUIET, f"{prefix} -- FRESH, {age_text}; {bound}; scron tick job runnable.{suffix}"
    detail = " | ".join(str(item) for item in problems)
    if severity == NO_EVIDENCE:
        return NO_EVIDENCE, (
            f"{prefix} -- **NO EVIDENCE ABOUT THE TICKER -- NOT A LIVENESS CLAIM** ({age_text};"
            f" {bound}): {detail}{suffix}"
        )
    return LOUD, (
        f"{prefix} -- **\u26a0 SUPERVISION NET NOT HEALTHY: {age_text}; {bound}. {detail}"
        f" Treat no watch below as supervised.**{suffix}"
    )


def render(
    config: dict[str, Any],
    sessions: dict[str, Any],
    usage: dict[str, Any],
    usage_rc: int,
    jobs: list[dict[str, Any]],
    git_state: dict[str, Any],
    wake_state: dict[str, Any],
    observed_at: str,
    waker_ctx=None,
) -> str:
    owners = validate_owners(config, sessions)
    lines = [
        "# Live orchestration state",
        "",
        "> GENERATED by `generate_live_state.py`; do not hand-edit. This is the normal-turn control-plane entrypoint.",
        "",
        f"- Observed: `{observed_at}`",
        f"- Campaign: {config['campaign']}",
        f"- Current DAG node: **{config['current_dag_node']}**",
        f"- Declared state: **{config['state']}**",
        f"- Git: `{git_state['head']}`; worktree entries: {git_state['dirty_count']} (uncommitted science is never live evidence)",
        "- FRESHNESS TEST, and read it before comparing anything: this snapshot is **born one "
        "commit stale by construction** -- the generator reads `HEAD`, then the commit that "
        "carries the output moves `HEAD`. So `Git:` is normally its own commit's PARENT. "
        "**FRESH iff `HEAD` equals `Git:` or `Git:` is `HEAD`'s parent; anything further back "
        "is STALE.** Run `python3 docs/orchestration/generate_live_state.py --check-freshness` "
        "rather than eyeballing it. A rule of \"`Git:` must equal `HEAD`\" has NO passing "
        "state and a check that always fires is a check nobody reads (BEN-199).",
        "- AND FRESHNESS IS NOT TRUTH: `Declared state` below is AUTHORED PROSE the generator "
        "carries forward verbatim. Regenerating updates the timestamp and the sha; it does NOT "
        "revalidate that text. On 2026-08-12 this field still read \"no cause is discharged\" "
        "after cause 2 was discharged at `d75833a`, through two regenerations.",
        "",
        "## Owners",
        "",
        "| Role | Provider/profile | UUID | Responsibility |",
        "|---|---|---|---|",
    ]
    for owner in owners:
        lines.append(f"| `{owner['role']}` | {owner['provider']} | `{owner['uuid']}` | {owner['purpose']} |")
    lines.extend(["", "## Compute", ""])
    # If this generator ran somewhere without Slurm, EVERY row below is a non-observation.
    # Say so above the table, because a per-row caveat is read after the eye has already
    # taken the bolded state. BEN-323.
    if any(job["snapshot"].get("overall") == "UNOBSERVED" for job in jobs):
        lines.extend([
            "> **⚠ THIS TABLE IS NOT A LIVE VIEW IN THIS SNAPSHOT.** One or more rows are"
            " `STATE UNAVAILABLE`, which means the generator could not reach Slurm from the"
            " host it ran on — **not** that the job is running, and **not** that it is done."
            " A `squeue`/`sacct` error in the Errors column means this file has NO state"
            " evidence for that job and you must query Slurm yourself before acting."
            " Until 2026-08-15 these rows rendered as **ACTIVE** (`BEN-323`): Leg F"
            " `56863958_[2-5]` was displayed ACTIVE for over 24 h after all four tasks"
            " COMPLETED, and a ~39 GPU-h scheduling constraint was built on it."
            " **Regenerate from a host with Slurm to make this table evidence.**",
            "",
        ])
    lines.extend(["| Job | State counts | Errors | Resources / placement |", "|---|---|---|---|"])
    for job in jobs:
        receipt = job["receipt"]
        counts = ", ".join(f"{key}={value}" for key, value in job["snapshot"].get("counts", {}).items()) or "unknown"
        errors = ",".join(str(x) for x in job["snapshot"].get("error_tasks", [])) or "none"
        placement = "batch job" if job.get("single_job") else "batch array"
        resources = f"{receipt.get('cpus_per_task','?')} CPU, {receipt.get('memory_per_task','?')}, {receipt.get('time_limit','?')}; {receipt.get('qos','?')} {placement}"
        label = job["job_id"] if job.get("single_job") else f"{job['job_id']}_[{job['tasks']}]"
        overall = job["snapshot"].get("overall", "UNOBSERVED")
        # `observer_errors` was computed and RETURNED by build_snapshot and then dropped
        # here, so the one piece of evidence proving Slurm was never reached did not
        # reach the reader. It is now the Errors cell whenever the state is UNOBSERVED.
        # BEN-323.
        if overall == "UNOBSERVED":
            why = "; ".join(str(x) for x in job["snapshot"].get("observer_errors", []))
            errors = f"NOT OBSERVED — {why}" if why else "NOT OBSERVED — no Slurm reply"
            resources = f"declared (not observed): {resources}"
            lines.append(
                f"| `{label}` | **STATE UNAVAILABLE — NOT A LIVENESS CLAIM**: {counts} | {errors} | {resources} |"
            )
        else:
            lines.append(f"| `{label}` | **{overall}**: {counts} | {errors} | {resources} |")
    lines.extend(["", "## Wake", ""])
    if "waker_status" in wake_state:
        waker = wake_state["waker_status"]
        # `wakerctl.status()` projects each watch to six keys and `params` is NOT
        # among them, so the full records are re-read here: without them this
        # section can only ever show `state`, which is the defect being fixed.
        full: dict[str, dict[str, Any]] = {}
        if waker_ctx is not None:
            for record in safe_load_watches(waker_ctx):
                full[str(record.get("watch_id"))] = record
        rendered, severities = [], []
        for projected in waker.get("watches", []):
            watch = full.get(str(projected.get("watch_id"))) or projected
            severity, text = render_watch(watch, waker_ctx)
            severities.append(severity)
            rendered.append(text)
        watches = ", ".join(rendered) or "none"
        events = ", ".join(
            f"`{e['event_id']}`:{e['state']}" for e in waker.get("events", [])
        ) or "none"
        last_tick = waker.get("last_tick") or {}
        tick_severity, tick_text = tick_line(last_tick, waker_ctx)
        if LOUD in severities or tick_severity == LOUD:
            lines.extend([
                "> **\u26a0 THE SUPERVISION NET IS NOT HEALTHY IN THIS SNAPSHOT.** An armed watch"
                " whose subject Slurm does not have, or a ticker that is stale or not runnable,"
                " means NOTHING WILL WAKE ANYONE when the job below ends -- and the watch will"
                " still read `armed`. A watch on a nonexistent task cannot reach"
                " `slurm-array-complete` in either direction: it counts unreliable ticks to"
                " `max_unreliable` and emits `monitor-error` (BEN-456, BEN-478). Re-arm the watch"
                " with the correct `params`, or release/reinstall the tick job, before treating"
                " any row here as supervised.",
                "",
            ])
        elif NO_EVIDENCE in severities or tick_severity == NO_EVIDENCE:
            lines.extend([
                "> **THIS SECTION IS NOT A LIVE VIEW IN THIS SNAPSHOT.** One or more entries read"
                " `NO EVIDENCE`, which means this host could not reach the scheduler or the waker"
                " state dir -- **not** that the watch is fine and **not** that the ticker is"
                " alive. Regenerate from a host with Slurm and the waker state dir to make this"
                " section evidence.",
                "",
            ])
        lines.extend(
            [
                f"- wakerctl watches: {watches}",
                f"- wakerctl events: {events}",
                tick_text,
                f"- Resume target: `{config['orchestrator_thread_id']}` with goals disabled and full-access flag.",
            ]
        )
    else:
        lines.extend(
            [
                f"- tmux `{config['wake']['tmux_session']}`: **{wake_state['tmux']}**",
                f"- Event/invoked/done markers: {wake_state['event']} / {wake_state['invoked']} / {wake_state['completed']}",
                f"- Resume target: `{config['orchestrator_thread_id']}` with goals disabled and full-access flag.",
            ]
        )
    lines.extend(
        [
            "- Only real external terminal events may wake the thread; quiet intervals make zero LLM calls.",
            "",
            "## Provider capacity",
            "",
            f"- Usage gate: **{'PASS' if usage.get('gate_ok') else 'BLOCKED/UNKNOWN'}** (helper rc={usage_rc})",
            f"- Codex personal: {codex_capacity(usage, 'codex-personal')}",
            f"- Codex school: {codex_capacity(usage, 'codex-school')}",
        ]
    )
    school = usage.get("accounts", {}).get("claude-school", {})
    agy = usage.get("profiles", {}).get("agy", {})
    lines.append(f"- Claude school shared account: {school.get('status','unknown')} (school + legacy are one quota; never sum aliases)")
    lines.append(f"- agy/Gemini: {agy.get('status','unknown')} (no percentage API; heartbeat/cap evidence only)")
    warnings = usage.get("warnings", [])
    if warnings:
        lines.append(f"- Capacity warnings: {len(warnings)}; inspect the complete snapshot before dispatch.")
    lines.extend(["", "## Exact blockers", ""])
    lines.extend(f"- {value}" for value in config["blockers"])
    lines.extend(["", "## Next authorized action", "", config["next_authorized_action"], "", "## Source routing", "", "| Class | Sources |", "|---|---|"])
    for label, key in (
        ("Canonical science", "canonical_science"),
        ("Append-only history", "append_only_history"),
        ("Archival/index-only", "archival_index_only"),
    ):
        rendered = ", ".join(f"[{path}]({rel_link(path)})" if path != "superseded followup prompts" else path for path in config[key])
        lines.append(f"| {label} | {rendered} |")
    lines.extend(
        [
            "",
            "## Fail-closed invariants",
            "",
            "- Preserve configured worker UUIDs; use `agentctl.py send`, never replacement conversations.",
            "- A scientific result is live only after its exact receipt/summary/ledger/status commit is pushed.",
            "- Do not double-count Claude School aliases or infer stale Claude/agy percentages.",
            "- Never consume the protected Codex Full reset without new credit-specific authorization.",
            "- Never use LLM polling/sleep loops; external terminal events perform at most one resume.",
            "- Choose live interactive capacity only for ready single-node work; queue independent arrays/long work early.",
            "",
        ]
    )
    if len(lines) > MAX_LINES:
        raise RuntimeError(f"dashboard exceeds {MAX_LINES} lines: {len(lines)}")
    return "\n".join(lines)


def atomic_write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check_freshness(repo_root) -> int:
    """Exit 0 if LIVE-STATE.md is fresh, 1 if stale, 2 if it cannot be read.

    FRESH means: HEAD == the recorded `Git:` sha, OR the recorded sha is HEAD's parent. The second
    disjunct is not slack -- it is the normal state, because the commit that carries the snapshot moves
    HEAD after the generator read it. BEN-199: the orchestrator prescribed `Git:` vs `HEAD` as "the only
    freshness test" and it has NO passing state, so it fired on a maximally fresh file and could not
    separate born-stale-by-one from dangerously-stale-by-five, which was the condition it existed to
    detect. Found by the personal-account verifier session re-deriving the rule against the file.
    """
    import subprocess
    live = pathlib.Path(repo_root) / "docs/orchestration/LIVE-STATE.md"
    if not live.exists():
        print("CANNOT CHECK :: LIVE-STATE.md absent")
        return 2
    m = re.search(r"^- Git: `([0-9a-f]+)`", live.read_text(encoding="utf-8"), re.M)
    if not m:
        print("CANNOT CHECK :: no `- Git:` line in LIVE-STATE.md")
        return 2
    recorded = m.group(1)
    def rev(spec):
        r = subprocess.run(["git", "-C", str(repo_root), "rev-parse", "--short", spec],
                           capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    head, parent = rev("HEAD"), rev("HEAD^")
    if recorded == head:
        print(f"FRESH :: Git: {recorded} == HEAD")
        return 0
    if parent and recorded == parent:
        print(f"FRESH :: Git: {recorded} is HEAD's parent ({head}) -- the normal born-stale-by-one state")
        return 0
    print(f"STALE :: Git: {recorded}, HEAD {head}, HEAD^ {parent}. Regenerate before quoting any field.")
    print("  NOTE: regeneration fixes the sha and timestamp; it does NOT revalidate `Declared state`,")
    print("        which is authored prose the generator carries forward.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--check-freshness", action="store_true",
                        help="Exit 0 fresh / 1 stale / 2 cannot-check; writes nothing. BEN-199: the "
                             "rule is HEAD == Git: OR Git: is HEAD's parent, because the commit "
                             "carrying this file moves HEAD after the generator read it.")
    args = parser.parse_args()

    if args.check_freshness:
        return check_freshness(HERE.parent.parent)

    config = load_json(args.config)
    sessions = load_json(HERE / "state" / "sessions.json")
    usage, usage_rc = usage_snapshot()
    jobs = []
    for job in config["jobs"]:
        receipt = load_json(REPO / job["receipt"])
        if receipt.get("job_id") != job["job_id"]:
            raise RuntimeError(f"job receipt mismatch for {job['job_id']}")
        jobs.append(
            {
                **job,
                "receipt": receipt,
                "snapshot": build_snapshot(job["job_id"], expand_spec(job["tasks"])),
            }
        )
    wake = config["wake"]
    waker_ctx = None
    if wake.get("waker"):
        import wakerctl

        waker_ctx = wakerctl.Ctx()
        wake_state = {"waker_status": wakerctl.status(waker_ctx)}
    else:
        tmux_rc = subprocess.run(["tmux", "has-session", "-t", wake["tmux_session"]], capture_output=True).returncode
        wake_state = {
            "tmux": "ACTIVE" if tmux_rc == 0 else "INACTIVE",
            "event": "present" if (REPO / wake["event"]).exists() else "absent",
            "invoked": "present" if (REPO / wake["invoked"]).exists() else "absent",
            "completed": "present" if (REPO / wake["completed"]).exists() else "absent",
        }
    git_state = {
        "head": run_text(["git", "rev-parse", "--short", "HEAD"]).strip(),
        "dirty_count": len(run_text(["git", "status", "--short"]).splitlines()),
    }
    output = render(
        config, sessions, usage, usage_rc, jobs, git_state, wake_state, utc_now(), waker_ctx=waker_ctx
    )
    if args.stdout:
        print(output)
    else:
        atomic_write(args.output, output)
        print(f"wrote {args.output} ({len(output.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
