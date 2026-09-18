#!/usr/bin/env python3
"""Tests for the replacement significance consumer. Core is pure numpy, so ROOT is not needed.

Every refusal has a control that TRIPS it and there is a positive control proving none trips on a
fully declared call -- without which a module that refused everything would pass every other test.
The two that carry the most weight are `test_region_not_fully_prespecified_REFUSES` (D5 enforced in
code) and `test_ndf_is_the_retained_rank_not_the_bin_count`, because the second is the defect the
existing consumers have and it is invisible unless something asserts on it.
"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rank6_significance as R

EAVAIL_LO = np.array([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0])
W_LO = np.array([0.0, 1.1, 1.4, 1.8, 2.2, 3.0])
N = EAVAIL_LO.size * W_LO.size            # 42, the real (E_avail, W) plane


def full_decl(**over):
    kw = dict(rcond=1e-10, claim_threshold_sigma=3.0, region_eavail_min=0.8, region_w_min=0.0,
              region_prespecified="both", selection_aware=None)
    kw.update(over)
    return R.Declarations(**kw)


def graded(n, orders=12, seed=0):
    """A spectrum spanning many orders, which is C_Z's actual regime: its recorded spectrum runs
    1e-90 to 1e-75, ~15 orders. An EXACTLY rank-deficient matrix gives a CONSTANT retained rank
    across every plausible rcond, so it is the wrong fixture for a truncation scan -- the scan only
    demonstrates anything when there are small-but-nonzero eigenvalues for rcond to cut into."""
    rng = np.random.default_rng(seed)
    Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
    w = np.logspace(0, -orders, n)
    return (Q * w) @ Q.T


def psd(n, rank=None, seed=0):
    rng = np.random.default_rng(seed)
    k = rank or n
    A = rng.normal(size=(n, k))
    return A @ A.T


class Refusals(unittest.TestCase):
    def _code(self, decl):
        with self.assertRaises(SystemExit) as cm:
            decl.check()
        return cm.exception.code

    def test_missing_rcond_REFUSES_3(self):
        self.assertEqual(self._code(full_decl(rcond=None)), 3)

    def test_out_of_range_rcond_REFUSES_3(self):
        for bad in (0.0, 1.0, -1e-3, 5.0):
            self.assertEqual(self._code(full_decl(rcond=bad)), 3, f"rcond={bad}")

    def test_missing_claim_threshold_REFUSES_6(self):
        self.assertEqual(self._code(full_decl(claim_threshold_sigma=None)), 6)

    def test_region_not_fully_prespecified_REFUSES_5(self):
        """D5 IN CODE: a significance on a boundary the data chose needs selection-aware
        calibration, or the claim stays at central-value level."""
        for p in ("eavail-only", "neither"):
            self.assertEqual(self._code(full_decl(region_prespecified=p)), 5, p)

    def test_declaring_selection_awareness_LIFTS_the_region_refusal(self):
        """The refusal must be liftable by a declaration, or it is a prohibition not a criterion."""
        full_decl(region_prespecified="eavail-only",
                  selection_aware="declared:some-calibration-record.md").check()

    def test_unknown_prespecification_value_REFUSES_5(self):
        self.assertEqual(self._code(full_decl(region_prespecified="probably")), 5)

    def test_POSITIVE_CONTROL_a_fully_declared_call_is_accepted(self):
        full_decl().check()


class RetainedSubspace(unittest.TestCase):
    def test_rank_deficiency_is_detected_and_declared(self):
        C = psd(42, rank=12, seed=1)
        sub = R.retained_subspace(C, 1e-10)
        self.assertEqual(sub["retained_rank"], 12)
        self.assertEqual(sub["n_bins"], 42)

    def test_rcond_CHANGES_the_retained_rank(self):
        """If it did not, declaring it would be decoration."""
        C = psd(42, rank=30, seed=2)
        ranks = {rc: R.retained_subspace(C, rc)["retained_rank"]
                 for rc in (1e-14, 1e-3, 1e-1)}
        self.assertGreater(len(set(ranks.values())), 1, f"rank unchanged across rcond: {ranks}")

    def test_pseudo_inverse_annihilates_the_discarded_directions(self):
        C = psd(42, rank=10, seed=3)
        sub = R.retained_subspace(C, 1e-10)
        self.assertEqual(np.linalg.matrix_rank(sub["Cinv"], tol=1e-8), 10)

    def test_ndf_basis_states_the_rank_is_not_a_calibrated_ndf(self):
        sub = R.retained_subspace(psd(42, rank=9, seed=4), 1e-10)
        self.assertIn("not the bin count", sub["ndf_basis"])
        self.assertIn("calibrated", sub["ndf_basis"])


class Evaluate(unittest.TestCase):
    def setUp(self):
        # NO RIDGE. A `+ eps*I` would make C full rank and destroy the rank deficiency these tests
        # exist to exercise -- C_Z itself has 5214 negative eigenvalues of 10694, so full rank is
        # the wrong regime to fixture. Rank 8 is deliberately BELOW the 18-cell region below, so
        # the retained rank must come out under the cell count.
        self.C = psd(N, rank=8, seed=5)
        rng = np.random.default_rng(6)
        self.central = rng.uniform(1.0, 2.0, N)
        self.gen = self.central - rng.normal(0, 0.05, N)

    def test_ndf_is_the_retained_rank_not_the_bin_count(self):
        """THE defect in both existing consumers: the header reads chi2/ndf(all7)."""
        out = R.evaluate(self.C, self.central, self.gen, full_decl(), EAVAIL_LO, W_LO)
        self.assertEqual(out["result"]["ndf"], out["retained"]["retained_rank"])
        self.assertLess(out["result"]["ndf"], out["region"]["n_cells"],
                        "ndf must be the retained rank, which is below the cell count here")

    def test_region_is_computed_from_the_declared_cuts(self):
        out = R.evaluate(self.C, self.central, self.gen,
                         full_decl(region_eavail_min=0.4, region_w_min=1.8), EAVAIL_LO, W_LO)
        self.assertEqual(out["region"]["n_cells"], 12)      # 4 E_avail x 3 W, the audited corner

    def test_empty_region_REFUSES_5(self):
        with self.assertRaises(SystemExit) as cm:
            R.evaluate(self.C, self.central, self.gen,
                       full_decl(region_eavail_min=1e9), EAVAIL_LO, W_LO)
        self.assertEqual(cm.exception.code, 5)

    def test_mismatched_central_and_covariance_provenance_REFUSES_7(self):
        with self.assertRaises(SystemExit) as cm:
            R.evaluate(self.C, self.central, self.gen, full_decl(), EAVAIL_LO, W_LO,
                       central_provenance="independent_2d.root", cov_provenance="m1_proj.root")
        self.assertEqual(cm.exception.code, 7)

    def test_matching_provenance_is_accepted(self):
        R.evaluate(self.C, self.central, self.gen, full_decl(), EAVAIL_LO, W_LO,
                   central_provenance="m1_proj.root", cov_provenance="m1_proj.root")

    def test_truncation_scan_is_emitted_and_varies(self):
        """Uses a GRADED spectrum, not the rank-8 fixture: with an exactly rank-deficient matrix
        the retained rank is constant across every rcond, so the scan could not show the
        dependence it exists to expose."""
        C = graded(N, orders=12, seed=7)
        out = R.evaluate(C, self.central, self.gen, full_decl(), EAVAIL_LO, W_LO)
        scan = out["truncation_scan"]
        self.assertGreater(len(scan), 3)
        self.assertGreater(len({r.get("retained_rank") for r in scan}), 1,
                           "a scan whose rank never moves demonstrates nothing")

    def test_threshold_comparison_is_reported_not_assumed(self):
        out = R.evaluate(self.C, self.central, self.gen, full_decl(claim_threshold_sigma=99.0),
                         EAVAIL_LO, W_LO)
        self.assertFalse(out["claim_supported_at_threshold"])
        self.assertEqual(out["claim_threshold_sigma"], 99.0)

    def test_output_disclaims_what_it_cannot_authorize(self):
        out = R.evaluate(self.C, self.central, self.gen, full_decl(), EAVAIL_LO, W_LO)
        joined = " ".join(out["cannot_authorize"])
        for must in ("coverage", "adoption", "event-level"):
            self.assertIn(must, joined)
        self.assertIn("CANDIDATE", out["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
