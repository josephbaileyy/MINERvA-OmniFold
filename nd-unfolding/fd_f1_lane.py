#!/usr/bin/env python3
"""F1's lane launcher (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md section 4): run one lane's
steps of the committed step table, in order, so a closure and pseudo-experiments share a lane and the F1c unfolds
fill one node, as FD-PLAN.md section 5.2 priced them.

    fd_f1_lane.py --steps f1c-steps.tsv --lane K

A step line is <lane><TAB><step name><TAB><entrypoint relative to nd-unfolding/><TAB><args...>. Each step runs as
``python3 <deploy>/nd-unfolding/<entrypoint> <args>`` from the deploy root (this file's checkout); under s5c_array.sh
the lane runs inside mnv_guarded_run.py, whose guard arms every child interpreter (its own inventory record each).
The lane stops at the first step that exits non-zero and returns that code; nothing is retried.

MEASURES: nothing. CANNOT AUTHORIZE: anything.
"""
from __future__ import annotations

import argparse
import datetime
import subprocess
import sys
from pathlib import Path

_ND = Path(__file__).resolve().parent
DEPLOY = _ND.parent


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def lane_steps(table: Path, lane: int) -> list[tuple[str, str, list[str]]]:
    steps = []
    for line in table.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) < 3:
            raise SystemExit(f"[f1-lane] refusing: malformed step line {line[:80]!r}")
        if int(f[0]) != lane:
            continue
        entry = f[2]
        path = (_ND / entry).resolve()
        if _ND not in path.parents or not path.is_file() or path.suffix != ".py":
            raise SystemExit(f"[f1-lane] refusing: {entry} is not a Python entrypoint under nd-unfolding/")
        steps.append((f[1], entry, f[3:]))
    if not steps:
        raise SystemExit(f"[f1-lane] refusing: no steps for lane {lane} in {table}")
    return steps


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--steps", type=Path, required=True)
    ap.add_argument("--lane", type=int, required=True)
    a = ap.parse_args(argv)
    steps = lane_steps(a.steps, a.lane)
    print(f"[f1-lane] lane={a.lane} steps={[s[0] for s in steps]} start={now()}", flush=True)
    for name, entry, args in steps:
        print(f"[f1-lane] {name} start={now()}", flush=True)
        rc = subprocess.run([sys.executable, str(_ND / entry), *args], cwd=DEPLOY).returncode
        print(f"[f1-lane] {name} rc={rc} end={now()}", flush=True)
        if rc:
            return rc
    print(f"[f1-lane] lane={a.lane} done end={now()}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
