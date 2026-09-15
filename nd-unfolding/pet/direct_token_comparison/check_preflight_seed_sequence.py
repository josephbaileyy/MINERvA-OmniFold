"""Observe initial weights in the unchanged CPU preflight's complete sequence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any
from unittest.mock import patch

import numpy as np

import compatibility_preflight as preflight


def main() -> None:
    """Run the original CLI, recording weights without adding model operations."""
    if "--device" not in sys.argv or sys.argv[sys.argv.index("--device") + 1] != "cpu":
        raise ValueError("Only local CPU evidence is permitted")
    output = Path(sys.argv[sys.argv.index("--output") + 1])
    observations = output.with_name(output.name + "-initial-weight-hashes.json")
    original = preflight.exercise
    rows: list[dict[str, Any]] = []

    def observe(
        tf: Any, model: Any, inputs: dict[str, Any], device: str
    ) -> dict[str, Any]:
        weights = model.get_weights()
        rows.append(
            {
                "index": len(rows),
                "sha256": [
                    hashlib.sha256(np.asarray(value).tobytes()).hexdigest()
                    for value in weights
                ],
            }
        )
        observations.write_text(json.dumps(rows, indent=2) + "\n")
        return original(tf, model, inputs, device)

    with patch.object(preflight, "exercise", side_effect=observe):
        preflight.main()


if __name__ == "__main__":
    main()
