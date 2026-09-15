"""Run the frozen 69-test suite followed by the 25 amended-gate controls."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from unittest.mock import patch

import calibration_measure


def main() -> None:
    """Keep the existing optional-probe guard behavior and require both suites."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if hasattr(os, "sched_getaffinity"):
        affinity = sorted(os.sched_getaffinity(0))
        if len(affinity) < 8:
            raise RuntimeError("Eight application CPUs required")
        os.sched_setaffinity(0, affinity[:8])
    argv = [
        str(calibration_measure.__file__),
        "--tests-only",
        "--output",
        str(args.output),
    ]
    with patch.object(sys, "argv", argv):
        try:
            calibration_measure.main()
        except SystemExit as result:
            if result.code not in (None, 0):
                raise
    import pytest

    raise SystemExit(
        pytest.main(
            ["-q", str(Path(__file__).parent / "test_optimizer_equivalence.py")]
        )
    )


if __name__ == "__main__":
    main()
