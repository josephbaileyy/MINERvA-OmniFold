"""Stage pinned inputs or check an IBUKT reservation; never submit jobs."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import ibukt as core
import run_ibukt as runner

LIMITS = {"envstage": 0.3, "prepare": 0.5, "screen": 5.25, "score": 0.1}


def stage(sources: dict[str, Any], output: Path) -> None:
    """Copy each declared source once through O_NOATIME and verify the copy.

    Source locations are supplied by the audited connect binding; identities
    come exclusively from the committed experiment configuration.
    """
    if not output.resolve().is_relative_to(Path("/pscratch")):
        raise ValueError("staging must be on pscratch")
    cfg = core.configuration()
    if set(sources) != set(cfg["inputs"]):
        raise ValueError("source manifest must name exactly the six pinned inputs")
    sys.path.insert(0, str(runner.REPO / "2d-unfolding/ref_c2c1"))
    import ref_c2c1 as comparison

    needed = sum(Path(source).stat().st_size for source in sources.values())
    stat = os.statvfs(output.parent)
    if stat.f_bavail * stat.f_frsize < 2 * needed:
        raise ValueError(
            "filesystem free space below twice staging size; quota also needs the connect check"
        )
    output.mkdir(exist_ok=False)
    receipts = {}
    for role, source in sources.items():
        path = Path(source)
        before = path.stat().st_atime_ns
        pin = cfg["inputs"][role]
        got = comparison.copy_noatime(path, output / pin["filename"])
        after = path.stat().st_atime_ns
        if got != pin["sha256"] or before != after:
            raise ValueError(f"{role}: digest or source atime changed")
        receipts[role] = {"sha256": got, "atime_before": before, "atime_after": after}
    runner.write_json(output / "stage.json", receipts)


def screen_admission(path: Path) -> dict[str, Any]:
    """Validate the prior-spend receipt with screen and scoring time reserved."""
    record = runner.read_json(path)
    requested = LIMITS["screen"] + LIMITS["score"]
    if (record["request_stage"], record["requested"], record["config_sha256"]) != (
        "screen",
        requested,
        runner.digest(core.CONFIG),
    ):
        raise ValueError("invalid screen admission identity")
    spent, total = record["spent_or_reserved"], record["total"]
    if (
        not all(math.isfinite(x) for x in (spent, total))
        or spent < 0
        or total > core.CAMPAIGN_CAP_HOURS
        or abs(total - spent - requested) > 1e-12
    ):
        raise ValueError("invalid screen admission accounting")
    return dict(record)


def main() -> None:
    """Stage files or price a requested envelope from freshly captured sacct output."""
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="mode", required=True)
    copy = subs.add_parser("stage")
    copy.add_argument("--sources", type=Path, required=True)
    copy.add_argument("--out", type=Path, required=True)
    gate = subs.add_parser("gate")
    gate.add_argument("--sacct", type=Path, required=True)
    gate.add_argument("--reservations", type=Path, required=True)
    gate.add_argument("--request", choices=LIMITS, required=True)
    admission_parser = subs.add_parser("screen-admission")
    admission_parser.add_argument("--admission", type=Path, required=True)
    forecast = subs.add_parser("forecast")
    forecast.add_argument("--admission", type=Path, required=True)
    forecast.add_argument("--measured-seconds", type=float, required=True)
    forecast.add_argument("--elapsed-seconds", type=float, required=True)
    args = parser.parse_args()
    if args.mode == "stage":
        stage(runner.read_json(args.sources), args.out)
    elif args.mode == "screen-admission":
        print(json.dumps(screen_admission(args.admission)))
    elif args.mode == "forecast":
        admission = screen_admission(args.admission)
        print(
            json.dumps(
                core.forecast(
                    args.measured_seconds,
                    args.elapsed_seconds,
                    admission["spent_or_reserved"],
                )
            )
        )
    else:
        result: dict[str, Any] = core.budget(
            args.sacct.read_text(),
            json.loads(args.reservations.read_text()),
            LIMITS[args.request] + (LIMITS["score"] if args.request == "screen" else 0),
        )
        result.update(
            request_stage=args.request, config_sha256=runner.digest(core.CONFIG)
        )
        print(json.dumps(result))


if __name__ == "__main__":
    main()
