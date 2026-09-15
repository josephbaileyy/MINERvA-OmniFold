"""Adversarial controls for the pinned upstream overflow semantics probe.

The probe in ``verify_upstream_overflow_semantics.py`` asserts six properties of
Gregor's cap/aggregation code. A property that no mutation can break is untested,
not proven, so each control here mutates the upstream function so that exactly
the targeted property should fail.

The mutations are applied to the extracted function body and handed straight to
``measure``, deliberately bypassing the SHA-256 gate. Routing a mutant through
the gate instead would have it refused for the wrong reason -- a digest mismatch,
not a semantic divergence -- and the control would pass without ever reaching the
assertion it claims to exercise.

Upstream code is not vendored here, so every test skips unless the operator
supplies the pinned file via ``MINERVA_UPSTREAM_PREPROCESSING``.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import types
from typing import Any
import unittest
import warnings

import numpy as np

import verify_upstream_overflow_semantics as probe

ENVIRONMENT_KEY = "MINERVA_UPSTREAM_PREPROCESSING"


def _upstream_body() -> str:
    """Return the extracted upstream function source, or skip the test."""
    location = os.environ.get(ENVIRONMENT_KEY)
    if not location:
        raise unittest.SkipTest(
            f"Set {ENVIRONMENT_KEY} to the pinned upstream preprocessing.py"
        )
    text = Path(location).read_text()
    match = re.search(rf"def {probe.FUNCTION}\(.*?\n(?=def )", text, re.S)
    if match is None:
        raise unittest.SkipTest(f"{probe.FUNCTION} absent from the supplied file")
    return match.group(0)


def _measure(body: str) -> dict[str, Any]:
    """Execute a function body and measure its semantics."""
    module = types.ModuleType("mutant")
    module.np = np  # type: ignore[attr-defined]
    exec(body, module.__dict__)  # noqa: S102 - local mutation control
    return probe.measure(getattr(module, probe.FUNCTION))


def _failed(result: dict[str, Any]) -> set[str]:
    """Return the property names that did not hold."""
    return {name for name, held in result["properties"].items() if not held}


class UpstreamOverflowSemantics(unittest.TestCase):
    """Pin the upstream properties the overflow specification relies on."""

    def test_unmutated_upstream_passes(self) -> None:
        """The control must pass, or every mutation below is meaningless."""
        result = _measure(_upstream_body())
        self.assertEqual(_failed(result), set())
        self.assertEqual(result["verdict"], "UPSTREAM-SEMANTICS-AS-SPECIFIED")

    def test_removing_the_off_by_one_is_caught(self) -> None:
        """Keeping ``n_keep`` individually must break the token-count property."""
        body = _upstream_body()
        for name in ("four_momentum", "pid", "additional_info"):
            source = f"sorted_{name}[: n_keep - 1]"
            self.assertIn(source, body)
            body = body.replace(source, f"sorted_{name}[: n_keep]")
        self.assertIn("binding_output_equals_n_keep", _failed(_measure(body)))

    def test_auxiliary_sum_instead_of_mean_is_caught(self) -> None:
        """Summing the merged auxiliary block must break the mean property."""
        body = _upstream_body()
        mutated = body.replace(
            "np.mean(\n        low_energy_additional_info, axis=0, keepdims=True\n    )",
            "np.sum(low_energy_additional_info, axis=0, keepdims=True)",
        )
        self.assertNotEqual(mutated, body)
        self.assertEqual(
            _failed(_measure(mutated)), {"auxiliary_aggregate_is_tail_mean"}
        )

    def test_four_momentum_mean_instead_of_sum_is_caught(self) -> None:
        """Averaging the merged four-momentum must break energy conservation."""
        body = _upstream_body()
        mutated = body.replace(
            "np.sum(low_energy_four_momentum, axis=0, keepdims=True)",
            "np.mean(low_energy_four_momentum, axis=0, keepdims=True)",
        )
        self.assertNotEqual(mutated, body)
        self.assertEqual(_failed(_measure(mutated)), {"total_energy_conserved"})

    def test_disabling_the_early_returns_is_caught(self) -> None:
        """Aggregating below the cap must break the inert-transform property."""
        body = _upstream_body()
        mutated = body.replace("if n_blobs <= n_keep:", "if False:").replace(
            "if len(sorted_four_momentum) <= n_keep:", "if False:"
        )
        self.assertNotEqual(mutated, body)
        # The mutant averages an empty tail; that warning is the mutation working.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            self.assertEqual(_failed(_measure(mutated)), {"inert_below_cap"})

    def test_digest_gate_refuses_tampered_bytes(self) -> None:
        """The loader must refuse bytes that do not match the bound digest."""
        location = os.environ.get(ENVIRONMENT_KEY)
        if not location:
            self.skipTest(f"Set {ENVIRONMENT_KEY}")
        with self.assertRaises(ValueError) as caught:
            probe.load_upstream_function(Path(location), "0" * 64)
        self.assertIn("digest mismatch", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
