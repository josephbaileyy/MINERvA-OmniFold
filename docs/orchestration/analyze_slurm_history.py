#!/usr/bin/python3.11
"""Summarize Slurm queue/runtime evidence for orchestration placement policy."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import math
from pathlib import Path
import subprocess


FIELDS = [
    "JobIDRaw", "JobName", "Partition", "QOS", "Submit", "Eligible",
    "Start", "End", "ElapsedRaw", "State", "ExitCode", "ReqCPUS",
    "AllocCPUS", "ReqMem", "AllocNodes", "Reason",
]


def timestamp(value: str) -> dt.datetime | None:
    if not value or value in {"None", "Unknown", "N/A"}:
        return None
    return dt.datetime.fromisoformat(value)


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    low, high = math.floor(pos), math.ceil(pos)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - pos) + ordered[high] * (pos - low)


def distribution(values: list[float]) -> dict[str, float | int | None]:
    return {
        "n": len(values),
        "min": min(values) if values else None,
        "p50": percentile(values, 0.50),
        "p90": percentile(values, 0.90),
        "max": max(values) if values else None,
        "mean": sum(values) / len(values) if values else None,
    }


def summarize(rows: list[dict[str, str]]) -> dict:
    state_counts = collections.Counter(row["State"].split()[0] for row in rows)

    def group_summary(group: list[dict[str, str]]) -> dict:
        queue, submit_wait, dependency_hold, runtime = [], [], [], []
        group_states = collections.Counter()
        for row in group:
            submit = timestamp(row["Submit"])
            eligible = timestamp(row["Eligible"])
            start = timestamp(row["Start"])
            group_states[row["State"].split()[0]] += 1
            if eligible and start:
                queue.append((start - eligible).total_seconds())
            if submit and start:
                submit_wait.append((start - submit).total_seconds())
            if submit and eligible:
                dependency_hold.append((eligible - submit).total_seconds())
            try:
                seconds = int(row["ElapsedRaw"])
            except (TypeError, ValueError):
                continue
            if seconds >= 0 and start:
                runtime.append(seconds)
        return {
            "jobs": len(group),
            "states": dict(sorted(group_states.items())),
            "queue_from_eligible_seconds": distribution(queue),
            "submit_to_start_seconds": distribution(submit_wait),
            "dependency_hold_seconds": distribution(dependency_hold),
            "runtime_seconds": distribution(runtime),
        }

    by_qos_rows: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    by_name_rows: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        by_qos_rows[row["QOS"] or "(none)"].append(row)
        by_name_rows[row["JobName"] or "(none)"].append(row)

    # Retain families with repeated evidence, plus any current/pending family.
    retained_names = {
        name: group_summary(group)
        for name, group in sorted(by_name_rows.items())
        if len(group) >= 2
        or any(r["State"].split()[0] in {"RUNNING", "PENDING"} for r in group)
    }
    return {
        "rows": len(rows),
        "states": dict(sorted(state_counts.items())),
        "by_qos_task_weighted": {
            name: group_summary(group) for name, group in sorted(by_qos_rows.items())
        },
        "by_job_name_task_weighted": retained_names,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="Slurm query start")
    parser.add_argument("--end", required=True, help="Slurm query end")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    command = [
        "sacct", "-S", args.start, "-E", args.end, "-X", "-n", "-P",
        "-o", ",".join(FIELDS),
    ]
    output = subprocess.run(command, check=True, text=True, capture_output=True).stdout
    rows = []
    for line in output.splitlines():
        if not line:
            continue
        values = line.split("|")
        if len(values) != len(FIELDS):
            raise RuntimeError(f"Unexpected sacct row with {len(values)} fields: {line}")
        rows.append(dict(zip(FIELDS, values)))

    result = {
        "schema": "slurm-history-summary.v1",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "query": {"start": args.start, "end": args.end, "command": command},
        "time_note": (
            "Durations are timezone-independent. Slurm timestamps render in the "
            "NERSC scheduler timezone; queue delay is Start-Eligible, while "
            "Submit-Start also includes dependency/ineligible holds. Array tasks "
            "are task-weighted."
        ),
        "summary": summarize(rows),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    temporary.replace(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
