"""Check diagnostic arithmetic against independent small examples."""

import numpy as np
import pytest

from optimizer_diagnostic import float64_adam, metrics


def test_metrics_preserves_asymmetric_tolerance() -> None:
    """The reported failures use the unchanged reference-relative budget."""
    result = metrics([0.0, 1.0002], [0.000011, 1.0])
    assert result["failed"] == 2
    assert result["worst_flat_index"] == 1
    assert not result["exact"]
    assert metrics([], [])["count"] == 0
    with pytest.raises(ValueError):
        metrics([np.nan], [0.0])
    with pytest.raises(ValueError):
        metrics([0.0], [0.0, 1.0])


def test_float64_adam_constant_gradient() -> None:
    """Constant gradients have closed-form moments at both steps."""
    initial = np.array([1.0, -2.0, 0.0], dtype=np.float32)
    gradient = np.array([0.25, -0.5, 0.0], dtype=np.float32)
    states = float64_adam([initial], [[gradient], [gradient]])
    expected = initial.astype(np.float64)
    for step, actual in enumerate(states, 1):
        moment = gradient.astype(float) * (1 - 0.9**step)
        variance = gradient.astype(float) ** 2 * (1 - 0.999**step)
        alpha = float(np.float32(0.001)) * np.sqrt(1 - 0.999**step) / (1 - 0.9**step)
        expected -= alpha * moment / (np.sqrt(variance) + 1e-7)
        assert np.allclose(actual[0], expected, rtol=0, atol=1e-15)
    assert np.array_equal(initial, [1.0, -2.0, 0.0])
