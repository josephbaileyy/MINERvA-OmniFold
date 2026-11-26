"""Compare regenerated central values, controls and signed projections to the receipt."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def compare_json(actual: object, expected: object) -> None:
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            compare_json(actual[key], expected[key])
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for a, b in zip(actual, expected, strict=True):
            compare_json(a, b)
    elif isinstance(expected, (int, float)):
        np.testing.assert_allclose(actual, expected, rtol=1e-8, atol=0)
    else:
        assert actual == expected


if __name__ == "__main__":
    original = Path(sys.argv[1])
    for relative in [
        "inputs/replay/cross-section.csv",
        "inputs/replay/reco-bands.csv",
        "modes/six-modes.csv",
        "merged-all.csv",
        "validation-all.csv",
        "merged-origin.csv",
        "merged-quality.csv",
        "validation-quality.csv",
        "validation-origin.csv",
        "shifted-threshold.csv",
        "signed-qp.csv",
    ]:
        current = pd.read_csv(relative)
        saved = pd.read_csv(original / relative)
        pd.testing.assert_frame_equal(
            current, saved, check_exact=False, rtol=1e-6, atol=0
        )
    for output, saved in [
        ("control-results.json", "inputs/control/results.json"),
        ("inputs/control/fine-results.json", "inputs/control/fine-results.json"),
        ("shifted-threshold.json", "shifted-threshold.json"),
    ]:
        compare_json(
            json.loads(Path(output).read_text()),
            json.loads((original / saved).read_text()),
        )
    for name in ["curvature-scale.txt", "width.txt"]:
        assert Path(name).read_text() == (original / name).read_text(), name
    print(
        "Exact-edge replay, held-out controls, six signed modes and charge checks reproduced."
    )
