"""Turn a captured `sacct` table into rows of `phase_e/resources-E1.tsv` (COMMON.md's columns).

Capture on Perlmutter (this script queries nothing, so it runs anywhere):

    sacct -j <ids> -X -P --format=JobID,JobName,Account,Partition,QOS,NNodes,AllocCPUS,AllocTRES,\\
        ElapsedRaw,State,Start > sacct.psv

    python record_resources.py --sacct sacct.psv --purpose <jobid>="what it was for" ...

`cpu_core_hours` is the allocated CPUs times elapsed (what the share is charged against, the same
convention as `phase_b/scalar/resources-B1.tsv`); `gpu_hours` is device-hours from `AllocTRES`.
Existing rows for the same job id are replaced, so re-running after a job finishes is safe.
"""
from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = ["date_utc", "phase", "slurm_job", "account", "partition_qos", "nodes", "gpus",
           "elapsed_s", "gpu_hours", "cpu_core_hours", "state", "purpose"]


def parse_sacct(text: str) -> list[dict[str, str]]:
    rows = list(csv.DictReader(text.strip().splitlines(), delimiter="|"))
    if not rows:
        raise SystemExit("[resources] no sacct rows")
    return rows


def gpus_of(alloc_tres: str) -> int:
    m = re.search(r"gres/gpu=(\d+)", alloc_tres or "")
    return int(m.group(1)) if m else 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sacct", type=Path, required=True)
    ap.add_argument("--purpose", nargs="*", default=[], help="<jobid>=<purpose> (prefix match)")
    ap.add_argument("--phase", default="E1")
    ap.add_argument("--output", type=Path,
                    default=Path(__file__).resolve().parent / "resources-E1.tsv")
    args = ap.parse_args()
    purposes = dict(p.split("=", 1) for p in args.purpose)

    existing: dict[str, list[str]] = {}
    if args.output.exists():
        with args.output.open() as handle:
            reader = csv.reader(handle, delimiter="\t")
            header = next(reader, None)
            for row in reader:
                if row:
                    existing[row[2]] = row
    for r in parse_sacct(args.sacct.read_text()):
        job = r["JobID"]
        purpose = next((v for k, v in purposes.items() if job.startswith(k)), "")
        elapsed = int(r.get("ElapsedRaw") or 0)
        gpus = gpus_of(r.get("AllocTRES", ""))
        started = (r.get("Start") or "")[:19]
        try:
            date_utc = (datetime.fromisoformat(started).astimezone(timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ")) if started and started != "Unknown" else ""
        except ValueError:
            date_utc = ""
        existing[job] = [date_utc, args.phase, job, r.get("Account", ""),
                         f"{r.get('Partition', '')}/{r.get('QOS', '')}", r.get("NNodes", ""),
                         str(gpus), str(elapsed), f"{gpus * elapsed / 3600:.3f}",
                         f"{int(r.get('AllocCPUS') or 0) * elapsed / 3600:.3f}",
                         r.get("State", "").split()[0], purpose or existing.get(job, [""] * 12)[11]]
    with args.output.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(COLUMNS)
        for job in sorted(existing, key=lambda j: (j.split("_")[0], j)):
            writer.writerow(existing[job])
    total = sum(float(v[9]) for v in existing.values())
    print(f"[resources] {len(existing)} jobs, {total:.2f} CPU core-hours -> {args.output}")


if __name__ == "__main__":
    main()
