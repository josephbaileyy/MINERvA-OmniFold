"""Analytic controls for units, support, boundaries and interval interpretation."""

import copy
import json
from pathlib import Path

import numpy as np
import pytest

from analyze import _binomial_interval
from reduce import Projection


def test_constant_density_has_geometric_integrals() -> None:
    definition = json.loads((Path(__file__).parent / "definition.json").read_text())
    projection = Projection(definition)
    integrated = projection.integrate(
        np.ones(np.prod(projection.shape)), crosscheck=True
    )
    extents = np.array([edges[-1] - edges[0] for edges in definition["fine"].values()])
    expected_total = extents.prod()
    assert np.isclose(integrated[:42].sum(), expected_total)
    assert np.isclose(integrated[-32:].sum(), expected_total)
    # The EW entries are integrals, not the original differential projection.
    assert np.isclose(integrated[0], 0.1 * 1.1 * extents[[0, 1, 3]].prod())


def test_unsupported_cells_remain_in_total() -> None:
    definition = json.loads((Path(__file__).parent / "definition.json").read_text())
    projection = Projection(definition)
    missing = np.flatnonzero(~np.isin(projection.cells["J"], projection.keep["J"]))[0]
    density = np.zeros(np.prod(projection.shape))
    density[missing] = 1 / projection.volume[missing]
    integrals = projection.integrate(density, crosscheck=True)
    assert np.isclose(integrals[:42].sum(), 1)
    assert np.isclose(integrals[-32:].sum(), 1)
    assert integrals[42:151].sum() == 0


def test_reporting_edge_must_not_split_a_saved_bin() -> None:
    definition = json.loads((Path(__file__).parent / "definition.json").read_text())
    changed = copy.deepcopy(definition)
    changed["partitions"]["H2"]["pt"][1] = 0.71
    with pytest.raises(ValueError, match="cuts a fine bin"):
        Projection(changed)


def test_empty_coverage_sample_does_not_imply_zero_probability() -> None:
    low, high = _binomial_interval(0, 20)
    assert low == 0
    assert np.isclose((1 - high) ** 20, 0.025)
    assert high > 0.16


def test_aggregation_can_cancel_bias_without_improving_each_cell() -> None:
    truth = np.array([1.0, 1.0])
    estimates = np.array([[1.2, 0.8], [1.3, 0.7], [1.1, 0.9]])
    assert np.abs((estimates.mean(0) - truth) / truth).min() > 0.19
    assert np.allclose(estimates.sum(1), truth.sum())
