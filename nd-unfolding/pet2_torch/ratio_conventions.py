"""Cross-engine physical density-ratio convention checks.

This module compares formulas at fixed logits and class masses.  It makes no
claim that stochastic TensorFlow and PyTorch classifiers are layer-equivalent.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .density_ratio import calibrated_ratio


def tensorflow_odds(posterior_class1: np.ndarray) -> np.ndarray:
    """Existing TF inference convention ``p(1|x)/p(0|x)``."""
    posterior = np.asarray(posterior_class1, dtype=np.float64)
    if (
        not np.all(np.isfinite(posterior))
        or np.any(posterior <= 0)
        or np.any(posterior >= 1)
    ):
        raise ValueError("posterior probabilities must lie strictly between zero and one")
    return posterior / (1.0 - posterior)


def fixed_ratio_convention_fixture() -> dict[str, Any]:
    """Return fixed unequal-mass logits that both conventions map identically."""
    mass0 = 7.0
    mass1 = 23.0
    balanced_logits = np.asarray([-2.0, -0.4, 0.0, 0.7, 1.9], dtype=np.float64)
    physical_logits = balanced_logits + np.log(mass1 / mass0)
    # The existing TF loaders balance the class masses before fitting, so its
    # raw odds are the normalized density ratio.  Restoring the original class
    # mass ratio produces the same physical measure ratio as the PyTorch
    # balanced-logit offset.
    posterior = 1.0 / (1.0 + np.exp(-balanced_logits))
    tf_normalized_odds = tensorflow_odds(posterior)
    tf_ratio = tf_normalized_odds * mass1 / mass0
    torch_ratio, telemetry = calibrated_ratio(
        balanced_logits, mass0, mass1, log_ratio_cap=30.0
    )
    return {
        "mass0": mass0,
        "mass1": mass1,
        "balanced_logits": balanced_logits,
        "physical_logits": physical_logits,
        "tf_balanced_posterior": posterior,
        "tf_normalized_odds": tf_normalized_odds,
        "tf_odds_ratio": tf_ratio,
        "torch_balanced_plus_mass_offset_ratio": torch_ratio,
        "torch_telemetry": telemetry,
        "equivalent": bool(np.allclose(tf_ratio, torch_ratio, rtol=1e-13, atol=1e-13)),
        "scope": (
            "fixed-logit ratio convention only; TF normalized odds are "
            "mass-corrected exactly once; no stochastic classifier or "
            "layer-equivalence claim"
        ),
    }
