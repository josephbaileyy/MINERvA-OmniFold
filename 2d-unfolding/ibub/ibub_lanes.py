#!/usr/bin/env python3
"""IBUB's lane table (IBUB-DECLARATION.md section 8): the job's two phases on one node, four lanes of 64 CPUs.

- **The reference phase:** ``central`` on lane 0 and ``central_df`` on lane 1. Lanes 2 and 3 are empty.
- **The toy phase:** the 600 toys, G18's 300 in seed order then AR23's, dealt round-robin. Toy k goes to lane k mod 4,
  so each lane runs 150.

  python ibub_lanes.py PHASE LANE     prints that lane's --unit arguments, one per line (PHASE refs | toys)
  python ibub_lanes.py table          prints every row as "phase<TAB>lane<TAB>unit"

MEASURES: nothing. CANNOT AUTHORIZE: a run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "cov2d"))
import cov2d as c  # noqa: E402

LANES = 4
TUNES = ("G18", "AR23")


def table() -> list[tuple[str, int, str]]:
    rows = [("refs", 0, "central"), ("refs", 1, "central_df")]
    toys = [f"toy:{t}:{s}" for t in TUNES for s in c.TOY_SEEDS[t]]
    rows += [("toys", k % LANES, u) for k, u in enumerate(toys)]
    return rows


def lane(phase: str, n: int) -> list[str]:
    if phase not in ("refs", "toys") or not 0 <= n < LANES:
        raise ValueError(f"no lane {phase}:{n}")
    return [u for p, ln, u in table() if p == phase and ln == n]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["table"]:
        print("\n".join(f"{p}\t{ln}\t{u}" for p, ln, u in table()))
        return 0
    if len(argv) == 2 and argv[1].isdigit():
        try:
            print("\n".join(lane(argv[0], int(argv[1]))))
        except ValueError as e:
            print(f"refusing: {e}", file=sys.stderr)
            return 2
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
