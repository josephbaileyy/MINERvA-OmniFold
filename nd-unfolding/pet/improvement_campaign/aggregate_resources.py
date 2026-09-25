#!/usr/bin/env python3
"""Rebuild the campaign's cumulative resource ledger from the per-task ledgers.

Every delegate records the jobs it submitted in a ``resources-<task>.tsv`` somewhere under this
directory. This script concatenates them into ``RESOURCE_LEDGER.tsv`` (adding the source file as a
column), refuses a job id recorded twice with different charges, and prints the totals.

Usage: python3 aggregate_resources.py [--check]
``--check`` exits non-zero if the committed ledger differs from what would be written.
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "RESOURCE_LEDGER.tsv"
COLUMNS = ["date_utc", "phase", "slurm_job", "account", "partition_qos", "nodes", "gpus",
           "elapsed_s", "gpu_hours", "cpu_core_hours", "state", "purpose"]


def _rows():
    seen: dict[str, tuple[str, str, str]] = {}
    for path in sorted(HERE.rglob("resources-*.tsv")):
        with path.open(newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            if reader.fieldnames != COLUMNS:
                raise SystemExit(f"{path}: unexpected columns {reader.fieldnames}")
            for row in reader:
                key = row["slurm_job"]
                charge = (row["gpu_hours"], row["cpu_core_hours"], row["state"])
                if key in seen and seen[key][:2] != charge[:2]:
                    raise SystemExit(f"job {key} recorded twice with different charges: {seen[key]} vs {charge}")
                if key in seen:
                    continue
                seen[key] = charge
                yield {**row, "source": str(path.relative_to(HERE))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = list(_rows())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS + ["source"], delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    text = buf.getvalue()
    gpu = sum(float(r["gpu_hours"] or 0) for r in rows)
    cpu = sum(float(r["cpu_core_hours"] or 0) for r in rows)
    print(f"jobs={len(rows)} gpu_hours={gpu:.3f} cpu_core_hours={cpu:.2f}")
    if args.check:
        return 0 if LEDGER.exists() and LEDGER.read_text() == text else 1
    LEDGER.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
