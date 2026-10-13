#!/usr/bin/env python3
"""Meter one repair check against the repair allowance (300 aggregate CPU-s).

The repair of 2026-10-11 has its own allowance and ledger
(``logs/repair_ledger.jsonl``); it does not draw on the campaign ledger. Checks
need child processes (the launcher tests spawn launchers), so this meter does
not use the sandbox. It reserves the allotment with ``pilot_run.reserve``
(same lock, same never-release-on-crash rule), runs the command with a
per-process ``ulimit -t`` backstop, and settles the measured user+sys CPU of all
waited descendants. Processes a check deliberately orphans are not measured;
the check passes their certified bound as ``--extra-charge``.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_run as pr  # noqa: E402

REPAIR_CPU_CAP_S = 300.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--cpu-seconds", type=int, required=True)
    ap.add_argument("--extra-charge", type=float, default=0.0,
                    help="certified CPU bound of processes the check orphans on purpose")
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    reserved = a.cpu_seconds + a.extra_charge
    try:
        res = pr.reserve(a.ledger, a.id, reserved, 0, REPAIR_CPU_CAP_S, 0, {"cmd": cmd})
    except (PermissionError, pr.LedgerError) as exc:
        print(f"[repair_meter] {exc}", file=sys.stderr)
        return 3
    before = pr.children_cpu()
    with a.log.open("w") as log:
        rc = subprocess.run(["/bin/bash", "-c", f"ulimit -t {a.cpu_seconds}; exec {shlex.join(cmd)}"],
                            stdout=log, stderr=subprocess.STDOUT).returncode
    cpu = pr.children_cpu() - before
    rec = pr.settle(a.ledger, res, cpu + a.extra_charge, 0,
                    {"rc": rc, "basis": "measured+extra", "measured_s": round(cpu, 3),
                     "extra_charge_s": a.extra_charge})
    total = pr.ledger_totals(a.ledger)[0]
    print(f"[repair_meter] {a.id}: rc={rc} charged {rec['cpu_charged_s']} s; "
          f"repair total {total:.3f} / {REPAIR_CPU_CAP_S:.0f} s", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
