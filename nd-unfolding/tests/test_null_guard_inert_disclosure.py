#!/usr/bin/env python3
"""The fixed-seed null guard can be incapable of failing, and it must now say so.

WHAT WAS WRONG. `unified_throw_cov.py`'s null check compares an ABSOLUTE difference norm against
`1e-12 * max(||base||, 1.0)`. The clamp makes the tolerance an absolute `1e-12` whenever
`||base|| < 1`, and this CV vector's norm is order `1e-37` (SPEC §6.4), so the bound is ~1e37 times
the scale it should bound. A source trace established the two CV executions are LIKE-FOR-LIKE --
identical `_xsec_for_weights` arguments, same seed, same process -- so the observed `4.452e-14`
RELATIVE deviation is genuine within-process nondeterminism that this guard passed without comment.
Measured slack: ~2.25e38x. The check could not have failed.

WHAT WAS AND WAS NOT CHANGED. The threshold and the raise condition are UNTOUCHED, deliberately:
SPEC §6.4 rules that the replacement bound must be "justified by precision and sensitivity controls
established before implementation and not chosen from a favourable production result", and §3.7a's
routes to such a bound are all closed -- so choosing one here would be the prohibited act, not the
fix. What changed is that an inert pass no longer reports indistinguishably from a real one. Same
pattern as `check_dead_containment.py`'s "inert by declaration, not passing on evidence".

⚠ PART RATCHET, PART ARITHMETIC. The disclosure is inline in `main()`, which needs ROOT and a full
payload, so its execution is NOT covered here; restructuring a production module for testability was
the worse trade. `DisclosureRatchet` proves the code is present and correctly shaped;
`ClampArithmetic` proves the predicate it implements is the right one at the real scale. Neither
proves the branch runs. That is honest, and OI-129's owning re-verification already covers execution.
"""
import re
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "unified_throw_cov.py"


class ClampArithmetic(unittest.TestCase):
    """The predicate, at the real scale and at scales where it must NOT fire."""

    @staticmethod
    def state(base_norm, rel):
        null_norm = rel * base_norm
        tol = 1e-12 * max(base_norm, 1.0)
        return {"clamped": base_norm < 1.0, "tol": tol, "null_norm": null_norm,
                "slack": tol / null_norm if null_norm else float("inf"),
                "raise_fires": null_norm > tol}

    def test_at_the_real_scale_the_guard_cannot_fail(self):
        s = self.state(1e-37, 4.452e-14)
        self.assertTrue(s["clamped"])
        self.assertFalse(s["raise_fires"], "if this fired, the defect would not exist")
        self.assertGreater(s["slack"], 1e30, f"slack only {s['slack']:.2e}x")

    def test_a_LARGE_relative_deviation_still_would_not_fire(self):
        """The decisive property: even a 100% relative deviation passes. The guard is not
        insensitive by degree, it is blind."""
        s = self.state(1e-37, 1.0)
        self.assertFalse(s["raise_fires"])

    def test_the_clamp_does_NOT_engage_for_an_order_one_vector(self):
        """Opposite direction, so the disclosure is not unconditional."""
        s = self.state(10.0, 1e-14)
        self.assertFalse(s["clamped"])
        self.assertFalse(s["raise_fires"])

    def test_an_order_one_vector_WOULD_catch_a_real_deviation(self):
        """Confirms the guard is only broken because of the scale, not in its form."""
        s = self.state(10.0, 1e-6)
        self.assertFalse(s["clamped"])
        self.assertTrue(s["raise_fires"])


class DisclosureRatchet(unittest.TestCase):
    def setUp(self):
        self.s = SRC.read_text()

    def test_the_threshold_is_UNCHANGED(self):
        """If a future edit 'fixes' the number here, that is the prohibited act, not a repair."""
        self.assertIn("tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)", self.s)

    def test_the_raise_condition_is_UNCHANGED(self):
        self.assertIn("if null_norm > tol:", self.s)

    def test_the_inert_disclosure_is_present_and_computes_the_slack(self):
        self.assertIn("INERT", self.s)
        self.assertRegex(self.s, r"_slack\s*=\s*\(tol\s*/\s*null_norm\)")
        self.assertRegex(self.s, r"_clamped\s*=\s*_base_norm\s*<\s*1\.0")

    def test_the_disclosure_is_CONDITIONAL_on_the_clamp(self):
        """An unconditional warning would cry wolf on a well-scaled vector and be tuned out."""
        self.assertRegex(self.s, r"if _clamped:\s*\n\s*print\(")

    def test_it_reports_the_RELATIVE_ratio_the_bound_should_have_used(self):
        """The disclosure has to surface the quantity SPEC §6.4 rules on, or a reader cannot act."""
        self.assertIn("null_norm/_base_norm", self.s)

    def test_it_declines_to_choose_the_replacement_bound(self):
        self.assertIn("NOT chosen here", self.s)


if __name__ == "__main__":
    unittest.main(verbosity=2)
