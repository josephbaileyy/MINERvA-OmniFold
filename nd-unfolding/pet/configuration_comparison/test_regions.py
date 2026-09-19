"""Tests for the regional census: the partition, and the exemption's audit."""

from __future__ import annotations

import unittest

import numpy as np

import characterize_regions as cr


class Census(unittest.TestCase):
    """Regions come from cells, and an exempt region is reported, not hidden."""

    def _cells(self):
        # four cells, one per region, with deliberately unequal mass and signal
        acceptance = np.array([0.01, 0.10, 0.40, 0.80])
        mass = np.array([0.40, 0.30, 0.20, 0.10])
        displacement = np.array([0.001, 0.30, 0.40, 0.29])
        return acceptance, mass, displacement

    def test_every_cell_lands_in_exactly_one_region(self):
        acceptance, mass, displacement = self._cells()
        census = cr.region_census(acceptance, mass, displacement)
        self.assertEqual(sum(r["cells"] for r in census["regions"]), len(acceptance))
        self.assertAlmostEqual(sum(r["truth_mass_fraction"] for r in census["regions"]), 1.0)

    def test_a_region_without_signal_is_exempt_and_its_mass_is_reported(self):
        acceptance, mass, displacement = self._cells()
        census = cr.region_census(acceptance, mass, displacement)
        unresolvable = next(r for r in census["regions"] if r["region"] == "unresolvable")
        self.assertFalse(unresolvable["scoreable"])
        self.assertIsNotNone(unresolvable["exempt_reason"])
        # 40 % of the truth mass is exempt, and the census says so out loud.
        self.assertAlmostEqual(census["exempt_truth_mass_fraction"], 0.40)

    def test_a_region_with_signal_is_scoreable(self):
        acceptance, mass, displacement = self._cells()
        census = cr.region_census(acceptance, mass, displacement)
        self.assertEqual(census["scoreable_regions"], ["poor", "moderate", "good"])

    def test_the_marginal_can_hide_what_the_cells_show(self):
        """The motivating case: a well-accepted average over a failing cell."""
        acceptance = np.array([0.004, 0.89])
        mass = np.array([0.5, 0.5])
        displacement = np.array([0.5, 0.5])
        census = cr.region_census(acceptance, mass, displacement)
        occupied = [r["region"] for r in census["regions"] if r["cells"]]
        self.assertEqual(occupied, ["unresolvable", "good"])
        # The mean acceptance is 0.447, which would sit in "moderate" and report
        # nothing wrong; the cells put half the mass in "unresolvable".
        self.assertAlmostEqual(float(acceptance.mean()), 0.447)

    def test_mismatched_cell_arrays_are_refused(self):
        with self.assertRaises(ValueError):
            cr.region_census(np.zeros(4), np.zeros(3), np.zeros(4))

    def test_regions_do_not_overlap_and_cover_zero_to_one(self):
        bounds = [(lo, hi) for _, lo, hi in cr.SAFEGUARD_REGIONS]
        self.assertEqual(bounds[0][0], 0.0)
        self.assertGreaterEqual(bounds[-1][1], 1.0)
        for (_, hi), (lo, _) in zip(bounds, bounds[1:]):
            self.assertEqual(hi, lo)

    def test_the_injection_matches_the_committed_candidate(self):
        """Transcribed constants must not drift from the guarded script's."""
        import json
        from pathlib import Path

        committed = json.loads(
            (Path(__file__).parent / "CANDIDATE_ENDPOINT_CHOICES-20260918.json").read_text())
        blob = json.dumps(committed)
        self.assertIn("0.35", blob)
        self.assertIn("3.0", blob)
        self.assertEqual(cr.TILT_AMPLITUDE, 0.35)
        self.assertEqual(cr.TILT_CLIP_Z, 3.0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
