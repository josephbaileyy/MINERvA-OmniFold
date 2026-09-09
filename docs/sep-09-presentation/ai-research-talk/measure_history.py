#!/usr/bin/env python3
"""Measure repository activity at a fixed revision for the September presentation.

Outputs describe commits and paths, not authorship, effort, or productivity.
All reads use the recorded revision; concurrent working-tree edits are excluded.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "measurements"
MONTHS = [f"2026-{month:02d}" for month in range(4, 10)]
PATH_GROUPS = (
    "Analysis directories",
    "Orchestration directories",
    "Presentation / note",
    "Other paths",
)


def git(*args: str) -> str:
    """Read git output, raising on a failed command."""
    return subprocess.check_output(["git", *args], cwd=REPO, text=True)


def classify_path(path: str) -> str:
    """Assign a path to one mutually exclusive location category."""
    if path.startswith(("orchestration/", "docs/orchestration/")):
        return PATH_GROUPS[1]
    if path.startswith(("2d-unfolding/", "3d-unfolding/", "nd-unfolding/")):
        return PATH_GROUPS[0]
    if path.startswith(("docs/analysis-note/", "docs/technote/", "docs/sep-09-")):
        return PATH_GROUPS[2]
    return PATH_GROUPS[3]


def measure_activity(
    revision: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Count non-merge commits and commit/path touches by author calendar month."""
    output = git(
        "log",
        revision,
        "--no-merges",
        "--format=%x1e%H%x1f%as",
        "--name-only",
        "--no-renames",
    )
    monthly: dict[str, Counter[str]] = {month: Counter() for month in MONTHS}
    commits: list[dict[str, Any]] = []
    for record in output.split("\x1e"):
        if not record.strip():
            continue
        header, *lines = record.strip().splitlines()
        commit, author_date = header.split("\x1f")
        paths = sorted({line.strip() for line in lines if line.strip()})
        month = author_date[:7]
        if month not in monthly or author_date > "2026-09-08":
            raise ValueError(f"Commit {commit} falls outside the named months")
        monthly[month]["nonmerge_commits"] += 1
        for path in paths:
            monthly[month][classify_path(path)] += 1
        commits.append({"commit": commit, "author_date": author_date, "paths": paths})
    expected = int(git("rev-list", "--no-merges", "--count", revision))
    if not commits or len(commits) != expected:
        raise ValueError(f"Parsed {len(commits)} commits; rev-list counted {expected}")
    rows: list[dict[str, Any]] = [
        {
            "month": month,
            "nonmerge_commits": counts["nonmerge_commits"],
            **{group: counts[group] for group in PATH_GROUPS},
        }
        for month, counts in monthly.items()
    ]
    if sum(sum(row[group] for group in PATH_GROUPS) for row in rows) != sum(
        len(commit["paths"]) for commit in commits
    ):
        raise ValueError("Path categories do not partition the touch population")
    return rows, commits


def measure_snapshots(revision: str) -> list[dict[str, Any]]:
    """Count tracked Python files at monthly first-parent snapshots."""
    snapshots = []
    for month in MONTHS:
        if month == MONTHS[-1]:
            snapshot = revision
            label = "Sep 8 snapshot"
        else:
            year, month_number = map(int, month.split("-"))
            last_day = calendar.monthrange(year, month_number)[1]
            cutoff = f"{month}-{last_day}T23:59:59Z"
            snapshot = git(
                "rev-list", "--first-parent", "-1", f"--before={cutoff}", revision
            ).strip()
            label = f"{month} month end (UTC)"
        if not snapshot:
            raise ValueError(f"No first-parent snapshot for {month}")
        paths = git("ls-tree", "-r", "--name-only", snapshot).splitlines()
        python_paths = [path for path in paths if path.endswith(".py")]
        counts = Counter(classify_path(path) for path in python_paths)
        snapshots.append(
            {
                "month": month,
                "label": label,
                "revision": snapshot,
                "tracked_files": len(paths),
                "tracked_python_files": len(python_paths),
                **{group: counts[group] for group in PATH_GROUPS},
            }
        )
    return snapshots


def read_receipt(revision: str, path: str) -> tuple[dict[str, Any], dict[str, str]]:
    """Read a committed receipt and return its content digest."""
    content = subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=REPO)
    return json.loads(content), {
        "path": path,
        "revision": revision,
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def main() -> None:
    """Write the measurement tables and the ingredients behind plotted numbers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    revision = git("rev-parse", f"{args.revision}^{{commit}}").strip()
    rows, commits = measure_activity(revision)
    snapshots = measure_snapshots(revision)
    agreement, agreement_source = read_receipt(
        revision,
        "docs/orchestration/receipts/RECEIPT-2d-agreement-windows-20260821.json",
    )
    checkpoint, checkpoint_source = read_receipt(
        revision, "nd-unfolding/pet/fullevent_nominal/GATE_AB_PUSH_PROVENANCE.json"
    )
    repaired, repaired_source = read_receipt(
        revision,
        "nd-unfolding/pet/fullevent_nominal/"
        "GATE_AB_PUSH_PROVENANCE.slurm-56445883.batch512.json",
    )
    totals = agreement["headline_totals_oi130"]["values"]
    denominator = agreement["denominator"]["n_ratio_used"]
    windows = [
        agreement["results"][f"within_{width}_percent"]["count"]
        for width in (5, 10, 20)
    ]
    if (
        denominator != 205
        or not 0 <= windows[0] <= windows[1] <= windows[2] <= denominator
    ):
        raise ValueError("Agreement windows violate their documented population")
    if checkpoint["gate_B"]["Bi_pass"] or not repaired["gate_B"]["Bi_pass"]:
        raise ValueError("Historical failure / repaired-pass receipt identity changed")
    payload = {
        "revision": revision,
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "All non-merge commits reachable from revision; author dates; no working-tree files",
        "limits": [
            "Repository starts in April; project began in December by speaker recollection.",
            "April and September are partial observation months.",
            "A touch is one distinct path in one non-merge commit; repeated edits count again.",
            "Directory categories are locations, not a classifier of scientific value or labor.",
            "Authorship, human hours, accepted tasks, learning, and causal speedup are unmeasured.",
            "Snapshot stock is sensitive to migrations, deletions, and vendoring.",
            "Scientific figures replot historical committed receipts; no training or new extraction.",
        ],
        "monthly": rows,
        "snapshots": snapshots,
        "scientific": {
            "agreement_n": denominator,
            "agreement_counts": windows,
            "total_ours": totals["integral_ours_reported"],
            "total_paper": totals["integral_paper_reported"],
            "integral_ratio": totals["ratio_integrals_reported"],
            "bare_sum_ratio": totals["ratio_bare_sums"],
            "bare_sum_ours": totals["bare_content_sum_ours"],
            "bare_sum_paper": totals["bare_content_sum_paper"],
            "checkpoint_quantiles": {
                key: checkpoint["gate_B"][key]
                for key in (
                    "Bi_median_rel_dev",
                    "Bi_rel_dev_p90",
                    "Bi_rel_dev_p99",
                    "Bi_max_rel_dev",
                )
            },
            "checkpoint_aggregate_absolute_gap": abs(
                checkpoint["consequence"]["ratio_from_stored"]
                - checkpoint["consequence"]["ratio_from_checkpoint"]
            ),
            "checkpoint_n": checkpoint["gate_B"]["n_pass_gen"],
            "repaired_max_rel_dev": repaired["gate_B"]["Bi_max_rel_dev"],
            "repaired_batch_size": repaired["batch_size"],
        },
        "sources": [agreement_source, checkpoint_source, repaired_source],
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n")
    (OUT / "commit_inventory.json").write_text(json.dumps(commits, indent=2) + "\n")
    for name, table in (("monthly.csv", rows), ("snapshots.csv", snapshots)):
        with (OUT / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(table[0]))
            writer.writeheader()
            writer.writerows(table)
    print(
        json.dumps(
            {"revision": revision, "monthly": rows, "snapshots": snapshots}, indent=2
        )
    )


if __name__ == "__main__":
    main()
