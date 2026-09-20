"""Pick each arm's learning rate from the tuning split, and nothing else.

`frozen_design.TUNING_GRID` declares four points, `trials_per_arm: 4`,
`selected_on: the tuning split ONLY` and `selection_statistic: mean seven-bin
E_avail recovery over the tuning seeds`. The tuning stage evaluated one point
and nothing read the results, so the grid described work nobody had
implemented and the pilot and final would have run at the default.

Three things this refuses, each because the frozen design says so:

* selecting on anything but the tuning stage -- a rate chosen on the pilot or
  the final is a rate fitted to the data the effect is measured on;
* selecting a rate that is not on the grid;
* selecting when a point is missing a seed, because a mean over a different
  number of seeds for different points is not a comparison between points.

The two arms are selected INDEPENDENTLY. They are different networks at
different batch sizes and the grid is `same_for_both_arms`, which means the
same four points are offered to each -- not that they must land on the same
one.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

import frozen_design as fd
import score_campaign as sc


def select(scored: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """`scored` rows carry arm, seed, learning_rate and recovery."""
    points = [float(x) for x in fd.TUNING_GRID["points"]]
    seeds = list(fd.SEEDS["tuning"])
    rows = [dict(r) for r in scored]

    off_grid = sorted({float(r["learning_rate"]) for r in rows} - set(points))
    if off_grid:
        raise ValueError(
            f"tuning rows at rates {off_grid}, which are not on the frozen grid "
            f"{points}. A point nobody predeclared cannot be selected")

    table: dict[str, dict[float, dict[int, float]]] = {}
    for row in rows:
        (table.setdefault(row["arm"], {})
              .setdefault(float(row["learning_rate"]), {})[int(row["seed"])]) = \
            float(row["recovery"])

    selected: dict[str, Any] = {}
    for arm in ("ours", "theirs"):
        per_point = table.get(arm, {})
        missing = {p: sorted(set(seeds) - set(per_point.get(p, {}))) for p in points}
        incomplete = {p: m for p, m in missing.items() if m}
        if incomplete:
            raise ValueError(
                f"{arm}: learning rates {sorted(incomplete)} are missing seeds "
                f"{incomplete}. A mean over a different number of seeds for "
                "different points is not a comparison between points")
        means = {p: float(np.mean([per_point[p][s] for s in seeds])) for p in points}
        best = max(points, key=lambda p: (means[p], -p))
        selected[arm] = {
            "learning_rate": best,
            "mean_recovery": means[best],
            "mean_recovery_by_point": means,
            "seeds": seeds,
            "ties_broken_towards": "the smaller rate",
        }
    return {
        "selected": selected,
        "grid": points,
        "selected_on": fd.TUNING_GRID["selected_on"],
        "statistic": fd.TUNING_GRID["selection_statistic"],
        "arms_selected_independently": True,
        "reading": ("the grid is the same for both arms; that is the same four "
                    "points offered to each, not a requirement that they land "
                    "on the same one"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--closure-npz", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import report_campaign as rc

    folder = args.campaign / "tuning"
    weights = sorted(folder.rglob("weights_*.npz"))
    if not weights:
        raise SystemExit(f"[select] no tuning weights under {folder}")
    endpoint, context = rc.build_endpoint(args.closure_npz, weights[0])

    scored = []
    for path in weights:
        run = sc.load_run(path)
        receipt = json.loads((path.parent / "receipt.json").read_text())
        row = sc.score_run(run, endpoint,
                           scoreable_regions=context["scoreable_regions"])
        row["learning_rate"] = float(receipt["learning_rate"])
        scored.append(row)

    record = select(scored)
    record["tuning_rows"] = len(scored)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2))
    for arm, pick in record["selected"].items():
        print(f"[select] {arm}: lr {pick['learning_rate']} "
              f"(mean recovery {pick['mean_recovery']:+.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
