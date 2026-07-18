#!/usr/bin/python3.11
"""Summarize provider/account routing evidence from the canonical RUNS ledger."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import json
import math
from pathlib import Path


def account_group(value: str) -> str:
    lowered = value.lower()
    if lowered.startswith("claude-school-legacy") or lowered.startswith("claude-school"):
        return "claude-school-shared"
    for prefix in (
        "claude-personal", "codex-personal", "codex-school", "agy",
        "orchestrator", "slurm-m3246",
    ):
        if lowered.startswith(prefix):
            return prefix
    return value.split("(", 1)[0]


def role_class(account: str, role: str) -> str:
    if account == "slurm-m3246":
        return "compute"
    if account == "orchestrator":
        return "control"
    lowered = role.lower()
    if any(token in lowered for token in (
        "audit", "verifier", "review", "critique", "claims", "preflight",
        "redteam", "red-team", "recheck",
    )):
        return "review"
    return "implementation"


def parse_time(value: str) -> dt.datetime | None:
    if not value or value == "—" or "(" in value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    pos = (len(values) - 1) * q
    low, high = math.floor(pos), math.ceil(pos)
    if low == high:
        return values[low]
    return values[low] * (high - pos) + values[high] * (pos - low)


def outcome(verdict: str, exit_value: str) -> str:
    text = verdict.upper()
    if "PASS REJECTED" in text or "OVERCLAIM" in text:
        return "review_overclaim_rejected"
    if "PROVIDER BLOCK" in text or "PROVIDER-CAPPED" in text:
        return "provider_block"
    if text.startswith("BLOCK") or " EVIDENCE BLOCK" in text:
        return "scientific_or_evidence_block"
    if exit_value not in {"0", "—"}:
        return "dispatch_or_task_failure"
    if "PASS" in text or "CLOSED" in text or "COMPLETE" in text or "COMMITTED" in text:
        return "pass_or_complete"
    return "other_success_or_open"


def summarize(rows: list[dict[str, str]]) -> dict:
    grouped: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in rows:
        grouped[row["account_group"]].append(row)

    result = {}
    for account, group in sorted(grouped.items()):
        durations = [row["duration_seconds"] for row in group if row["duration_seconds"] is not None]
        exits = collections.Counter(row["exit"] for row in group)
        outcomes = collections.Counter(row["outcome"] for row in group)
        classes = collections.Counter(row["role_class"] for row in group)
        result[account] = {
            "rounds": len(group),
            "exit_counts": dict(sorted(exits.items())),
            "outcome_counts": dict(sorted(outcomes.items())),
            "role_class_counts": dict(sorted(classes.items())),
            "duration_seconds": {
                "n": len(durations),
                "p50": percentile(durations, 0.50),
                "p90": percentile(durations, 0.90),
                "max": max(durations) if durations else None,
            },
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.ledger.open(newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    rows = []
    for row in source:
        start, end = parse_time(row["start_utc"]), parse_time(row["end_utc"])
        duration = (end - start).total_seconds() if start and end and end >= start else None
        group = account_group(row["account"])
        rows.append({
            "task": row["task"],
            "account_group": group,
            "role_class": role_class(group, row["role"]),
            "exit": row["exit"],
            "duration_seconds": duration,
            "outcome": outcome(row["verdict"], row["exit"]),
        })

    result = {
        "schema": "dispatch-history-summary.v1",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "ledger": str(args.ledger),
        "rows": len(rows),
        "notes": [
            "claude-school and claude-school-legacy are one shared provider account",
            "exit=0 measures successful dispatch/response, not scientific PASS",
            "scientific BLOCK is useful reviewer output, while rejected overclaims are counted separately",
            "agy and Claude percentages remain unknown when no authoritative numeric API/cache is fresh",
        ],
        "by_account": summarize(rows),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    temporary.replace(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
