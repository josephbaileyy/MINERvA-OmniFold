#!/usr/bin/python3.11
"""Return a machine-readable state for one Slurm array without mutating it."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from collections import Counter
from typing import Callable


FAILURE_STATES = {
    "BOOT_FAIL",
    "CANCELLED",
    "DEADLINE",
    "FAILED",
    "NODE_FAIL",
    "OUT_OF_MEMORY",
    "PREEMPTED",
    "REVOKED",
    "SPECIAL_EXIT",
    "TIMEOUT",
}
ACTIVE_STATES = {
    "COMPLETING",
    "CONFIGURING",
    "PENDING",
    "REQUEUED",
    "REQUEUE_FED",
    "REQUEUE_HOLD",
    "RESIZING",
    "RUNNING",
    "STAGE_OUT",
    "SUSPENDED",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_state(value: str) -> str:
    return value.strip().upper().split()[0].rstrip("+") if value.strip() else "UNKNOWN"


def expand_spec(spec: str) -> list[int]:
    values: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            first, last = (int(x) for x in part.split("-", 1))
            if last < first:
                raise ValueError(f"descending task range: {part}")
            values.extend(range(first, last + 1))
        else:
            values.append(int(part))
    if not values or len(values) != len(set(values)):
        raise ValueError(f"invalid/duplicate task specification: {spec}")
    return values


def task_ids(job_id: str, token: str) -> list[int]:
    prefix = f"{job_id}_"
    if not token.startswith(prefix) or "." in token:
        return []
    suffix = token[len(prefix) :]
    if suffix.isdigit():
        return [int(suffix)]
    match = re.fullmatch(r"\[([0-9,\-]+)\]", suffix)
    return expand_spec(match.group(1)) if match else []


def parse_squeue(job_id: str, text: str) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("|", 2)
        if len(parts) != 3:
            continue
        token, state, reason = (part.strip() for part in parts)
        for task in task_ids(job_id, token):
            result[task] = {
                "state": normalize_state(state),
                "exit_code": "unknown",
                "reason": reason or "None",
                "source": "squeue",
            }
    return result


def parse_sacct(job_id: str, text: str) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("|", 2)
        if len(parts) != 3:
            continue
        token, state, exit_code = (part.strip() for part in parts)
        for task in task_ids(job_id, token):
            result[task] = {
                "state": normalize_state(state),
                "exit_code": exit_code or "unknown",
                "reason": "accounting",
                "source": "sacct",
            }
    return result


def command_output(command: list[str]) -> str:
    return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)


def build_snapshot(
    job_id: str,
    tasks: list[int],
    runner: Callable[[list[str]], str] = command_output,
) -> dict:
    errors: list[str] = []
    try:
        queue_text = runner(["squeue", "-h", "-r", "-j", job_id, "-o", "%i|%T|%r"])
    except (OSError, subprocess.CalledProcessError) as exc:
        queue_text = ""
        errors.append(f"squeue:{exc}")
    try:
        acct_text = runner(["sacct", "-X", "-j", job_id, "-n", "-P", "-o", "JobID,State,ExitCode"])
    except (OSError, subprocess.CalledProcessError) as exc:
        acct_text = ""
        errors.append(f"sacct:{exc}")

    queue = parse_squeue(job_id, queue_text)
    acct = parse_sacct(job_id, acct_text)
    rows: dict[str, dict[str, str]] = {}
    error_tasks: list[int] = []
    complete = 0

    for task in tasks:
        # Accounting terminal state wins; otherwise live queue state is fresher.
        arow = acct.get(task)
        qrow = queue.get(task)
        astate = arow["state"] if arow else "UNKNOWN"
        if arow and (astate == "COMPLETED" or astate in FAILURE_STATES):
            row = dict(arow)
        elif qrow:
            row = dict(qrow)
        elif arow:
            row = dict(arow)
        else:
            row = {"state": "UNKNOWN", "exit_code": "unknown", "reason": "not-visible", "source": "none"}

        state = row["state"]
        exit_code = row["exit_code"]
        if state == "COMPLETED" and exit_code == "0:0":
            complete += 1
        elif state in FAILURE_STATES or (state == "COMPLETED" and exit_code != "0:0"):
            error_tasks.append(task)
        elif state not in ACTIVE_STATES and state != "UNKNOWN":
            error_tasks.append(task)
        rows[str(task)] = row

    counts = Counter(row["state"] for row in rows.values())
    unknown_tasks = [int(task) for task, row in rows.items() if row["state"] == "UNKNOWN"]
    if error_tasks:
        overall = "ERROR"
    elif complete == len(tasks):
        overall = "COMPLETE"
    else:
        overall = "ACTIVE"

    return {
        "schema_version": 1,
        "observed_at_utc": utc_now(),
        "job_id": job_id,
        "expected_tasks": tasks,
        "overall": overall,
        "counts": dict(sorted(counts.items())),
        "error_tasks": error_tasks,
        "unknown_tasks": unknown_tasks,
        "observer_errors": errors,
        "tasks": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--tasks", default="1-12")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    snapshot = build_snapshot(args.job_id, expand_spec(args.tasks))
    print(json.dumps(snapshot, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
