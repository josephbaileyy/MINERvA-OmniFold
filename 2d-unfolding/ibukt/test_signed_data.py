"""Synthetic checks of the signed-data readout on a common covariance."""

from types import SimpleNamespace

import numpy as np
import pytest

import signed_data


def test_signed_data_reads_both_iterations_and_the_fixed_control_subset():
    selected = np.arange(205)
    mask = np.arange(224) < len(selected)
    covariance = np.diag(mask.astype(float))

    def distance(delta, _cov, _tag, *, report):
        assert not report
        return float(np.square(delta[mask]).sum()), int(mask.sum()), mask

    cp = SimpleNamespace(chi2_with_cov=distance)
    published = np.zeros(224)
    er = np.full(224, np.sqrt(465.41527219152636 / 205))
    refined = {k: np.full(224, np.sqrt(value)) for k, value in ((5, 0.83), (10, 1.03))}
    signed = {k: refined[k].copy() for k in signed_data.KS}
    signed[5][15] -= 0.5
    signed[10][15] += 0.25
    readings = signed_data._readings(
        cp, covariance, published, er, selected, refined, signed
    )

    assert readings["E_R"]["chi2"] == pytest.approx(465.41527219152636)
    for k, shift in ((5, -0.5), (10, 0.25)):
        result = readings[str(k)]
        assert result["signed_minus_refined"][15] == pytest.approx(shift)
        assert result["historical_control_cells"]["max_index"] == 15
        assert result["historical_control_cells"]["max_absolute"] == pytest.approx(
            abs(shift)
        )
        assert result["er_vs_signed"]["ndf"] == result["er_vs_refined"]["ndf"] == 205
        assert result["er_minus_refined"][15] - result["er_minus_signed"][
            15
        ] == pytest.approx(shift)
