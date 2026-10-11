#!/usr/bin/env python3
"""Run one pilot step under the authorized caps and append it to the budget ledger.

Caps (authorization of 2026-10-11): 36,000 CPU core-seconds of scientific
computation and 10,000 generated events in total, across every run, failure,
review and rerun. Before launching, the requested allotment is added to the
ledger's charged totals; the launch is refused if either cap would be exceeded.

During the run:
* ``NUWRO_PILOT_EVENT_CAP`` is exported, so the instrumented NuWro exits (97)
  before sampling one event beyond the allotment;
* ``ulimit -t`` limits the process tree to the CPU allotment.

After the run, measured user+sys CPU of the children and the number of sampled
events (dump lines; the full allotment when the count is unknown) are charged.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import resource
import shlex
import subprocess
import sys
from pathlib import Path

CPU_CAP_S = 36_000.0
EVENT_CAP = 10_000


def ledger_totals(ledger: Path) -> tuple[float, int]:
    cpu, events = 0.0, 0
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                cpu += float(rec["cpu_charged_s"])
                events += int(rec["events_charged"])
    return cpu, events


def count_events(dump: Path | None) -> int | None:
    if dump is None or not dump.exists():
        return None
    with dump.open() as fh:
        return sum(1 for line in fh if line.strip() and not line.startswith("#"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--events", type=int, required=True, help="event allotment (0 for no sampling)")
    ap.add_argument("--cpu-seconds", type=float, required=True, help="CPU allotment")
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--dump", type=Path, help="event dump whose lines count sampled events")
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        ap.error("no command")

    used_cpu, used_events = ledger_totals(args.ledger)
    if used_events + args.events > EVENT_CAP or used_cpu + args.cpu_seconds > CPU_CAP_S:
        print(f"[pilot_run] REFUSED {args.run_id}: used {used_events} events / {used_cpu:.1f} s; "
              f"request {args.events} / {args.cpu_seconds:.0f} s; caps {EVENT_CAP} / {CPU_CAP_S:.0f}",
              file=sys.stderr)
        return 3

    env = dict(os.environ)
    env["NUWRO_PILOT_EVENT_CAP"] = str(args.events)
    if args.dump:
        env["NUWRO_PILOT_DUMP"] = str(args.dump.resolve())
    shell = f"ulimit -t {int(args.cpu_seconds)}; exec {shlex.join(cmd)}"
    start = dt.datetime.now(dt.timezone.utc)
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    args.workdir.mkdir(parents=True, exist_ok=True)
    with args.log.open("w") as log:
        rc = subprocess.run(["/bin/bash", "-c", shell], cwd=args.workdir, env=env,
                            stdout=log, stderr=subprocess.STDOUT).returncode
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    end = dt.datetime.now(dt.timezone.utc)
    cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    sampled = count_events(args.dump)
    events_charged = args.events if (sampled is None and args.events > 0) else (sampled or 0)
    rec = {
        "run_id": args.run_id, "start_utc": start.isoformat(timespec="seconds"),
        "end_utc": end.isoformat(timespec="seconds"), "wall_s": round((end - start).total_seconds(), 3),
        "cmd": cmd, "workdir": str(args.workdir), "rc": rc,
        "events_allotted": args.events, "events_sampled_dumped": sampled,
        "events_charged": events_charged, "cpu_allotted_s": args.cpu_seconds,
        "cpu_charged_s": round(cpu, 3),
        "totals_after": {"events": used_events + events_charged, "cpu_s": round(used_cpu + cpu, 3)},
    }
    with args.ledger.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))
    return rc


if __name__ == "__main__":
    sys.exit(main())
