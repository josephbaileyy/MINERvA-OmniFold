"""Independent small projection calculations at physical cross-section scales."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest

from production.minerva_production.projection import project, projection_map
from production.minerva_production.storage import load_result, save_result


def contract(meaning: str = "density") -> dict[str, Any]:
    return {
        "axes": [
            {"name": "a", "unit": "GeV", "edges": [0, 1, 3]},
            {"name": "b", "unit": "GeV", "edges": [0, 2, 5]},
            {"name": "c", "unit": "GeV", "edges": [0, 4, 9]},
        ],
        "ordering": "C",
        "meaning": meaning,
        "value_unit": "cm^2/nucleon",
        "support": [True] * 8,
    }


@pytest.mark.parametrize("meaning", ["density", "yield"])
def test_unequal_widths_reordered_axes_and_correlations(
    meaning: str, tmp_path: Path
) -> None:
    source = contract(meaning)
    # Flattened source order: a,b,c. Destination order: c,a, integrated over b.
    factor = 3 if meaning == "density" else 1
    first = 2 if meaning == "density" else 1
    expected_map = np.array(
        [
            [first, 0, factor, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, first, 0, factor, 0],
            [0, first, 0, factor, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, first, 0, factor],
        ],
        float,
    )
    central = np.arange(1, 9) * 1e-39
    covariance = (np.eye(8) * 2 + np.ones((8, 8))) * 1e-80
    arrays, output = project(
        {"xsec": central, "covariance": covariance}, source, ["c", "a"]
    )
    np.testing.assert_array_equal(arrays["projection"], expected_map)
    expected_central = [11, 31, 16, 36] if meaning == "density" else [4, 12, 6, 14]
    np.testing.assert_allclose(
        arrays["xsec"], np.array(expected_central) * 1e-39, rtol=1e-14, atol=0
    )
    # Each diagonal: 2*sum(w^2) + sum(w)^2. Off-diagonal: sum(w)^2.
    expected_covariance = (
        np.eye(4) * (26 if meaning == "density" else 4)
        + np.ones((4, 4)) * (25 if meaning == "density" else 4)
    ) * 1e-80
    np.testing.assert_allclose(
        arrays["covariance"], expected_covariance, rtol=1e-14, atol=0
    )
    assert [axis["name"] for axis in output["axes"]] == ["c", "a"]
    directory = tmp_path / "result"
    save_result(
        directory,
        arrays,
        {"identity": {"test": "projection"}, "output_contract": output},
    )
    loaded, record = load_result(directory)
    assert record["output_contract"] == output
    np.testing.assert_array_equal(loaded["covariance"], arrays["covariance"])


def test_incomplete_support_is_not_silently_zero_filled() -> None:
    source = contract()
    source["support"][0] = False
    with pytest.raises(ValueError, match="incomplete source support"):
        projection_map(source, ["c", "a"])
    # Excluding an entire destination fiber is representable and remains explicit.
    source["support"][2] = False
    projection, output = projection_map(source, ["c", "a"])
    assert output["support"] == [False, True, True, True]
    assert projection.shape == (3, 6)
    np.testing.assert_array_equal(projection.sum(axis=0), [2, 3, 2, 2, 3, 3])


def test_shape_normalization_and_bad_covariance_are_refused() -> None:
    source = contract("normalized-shape")
    with pytest.raises(ValueError, match="normalized shapes"):
        projection_map(source, ["a"])
    source = contract()
    covariance = np.eye(8) * 1e-80
    covariance[0, 1] = 1e-80
    with pytest.raises(ValueError, match="symmetric"):
        project({"xsec": np.ones(8) * 1e-39, "covariance": covariance}, source, ["a"])
