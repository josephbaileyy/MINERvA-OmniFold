"""Freeze actual initial arrays from the unchanged CPU/checkpoint sequence."""

from __future__ import annotations

import argparse
import os
import hashlib
import json
from pathlib import Path
import sys
from typing import Any
from unittest.mock import patch

import numpy as np

import compatibility_preflight as original


def main() -> None:
    """Run the original preflight and save observations outside its gated output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if hasattr(os, "sched_getaffinity"):
        affinity = sorted(os.sched_getaffinity(0))
        if len(affinity) < 8:
            raise RuntimeError("Eight application CPUs required")
        os.sched_setaffinity(0, affinity[:8])
    args.output.mkdir(parents=True, exist_ok=False)
    initial = args.output / "initial"
    initial.mkdir()
    exercise = original.exercise
    pairs = [(case, route) for case in original.CASES for route in ("pooled", "direct")]
    rows: list[dict[str, Any]] = []

    def observe(
        tf: Any, model: Any, inputs: dict[str, Any], device: str
    ) -> dict[str, Any]:
        index = len(rows)
        case, route = pairs[index // 2]
        role = "reference" if index % 2 == 0 else "candidate"
        weights = model.get_weights()
        path = initial / f"{case}-{route}-{role}.npz"
        np.savez(path, **{f"weight_{i}": value for i, value in enumerate(weights)})
        hashes = [hashlib.sha256(value.tobytes()).hexdigest() for value in weights]
        if index % 2 and hashes != rows[-1]["weight_hashes"]:
            raise AssertionError("Original paired initialization differs")
        rows.append(
            {"case": case, "routing": route, "role": role, "weight_hashes": hashes}
        )
        return exercise(tf, model, inputs, device)

    argv = [
        str(original.__file__),
        "--device",
        "cpu",
        "--output",
        str(args.output / "baseline"),
    ]
    with patch.object(original, "exercise", side_effect=observe), patch.object(
        sys, "argv", argv
    ):
        original.main()
    if len(rows) != 16:
        raise AssertionError("Incomplete original initialization sequence")
    files = {
        str(p.relative_to(args.output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(args.output.rglob("*"))
        if p.is_file()
    }
    (args.output / "bundle.json").write_text(
        json.dumps(
            {
                "terminal": "PASS",
                "recipe": "original-cpu-preflight-including-checkpoint-reload",
                "rows": rows,
                "files": files,
                "code_sha256": original.code_hashes(),
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
