#!/usr/bin/env python3
"""IBUB's lane table (IBUB-DECLARATION.md section 8): the job's two phases on one node, four lanes of 64 CPUs.

- **The reference phase:** ``central`` on lane 0 and ``central_df`` on lane 1. Lanes 2 and 3 are empty.
- **The toy phase:** the 600 toys, G18's 300 in seed order then AR23's, dealt round-robin. Toy k goes to lane k mod 4,
  so each lane runs 150.

  python ibub_lanes.py PHASE LANE     prints that lane's --unit arguments, one per line (PHASE refs | toys)
  python ibub_lanes.py table          prints every row as "phase<TAB>lane<TAB>unit"
  python ibub_lanes.py verify         exit 0 only if the table is the declared one

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


def verify() -> list[str]:
    """The table's own checks: the two references alone on lanes 0 and 1; each declared toy exactly once; 150 per
    lane. The problems, empty when it holds."""
    rows = table()
    probs = []
    if [r for r in rows if r[0] == "refs"] != [("refs", 0, "central"), ("refs", 1, "central_df")]:
        probs.append("the reference rows are not central on lane 0 and central_df on lane 1")
    toys = [u for p, _, u in rows if p == "toys"]
    want = [f"toy:{t}:{s}" for t in TUNES for s in c.TOY_SEEDS[t]]
    if sorted(toys) != sorted(want) or len(set(toys)) != len(toys):
        probs.append("the toys are not each declared toy exactly once")
    for ln in range(LANES):
        n = sum(1 for p, x, _ in rows if p == "toys" and x == ln)
        if n != len(want) // LANES:
            probs.append(f"lane {ln} has {n} toys, not {len(want) // LANES}")
    return probs


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["verify"]:
        probs = verify()
        print("\n".join(probs) if probs else "LANES OK: 2 references, 600 toys, 150 per lane")
        return 1 if probs else 0
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
