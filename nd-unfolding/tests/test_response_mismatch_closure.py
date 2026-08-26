"""Regression tests for the diagnostic E_avail response-mismatch closure.

The closure is intentionally narrow: it may alter only a copied pseudo-data
reconstructed E_avail column.  Truth, nominal response arrays, weights, and
event membership are outside the perturbation contract.
"""
import os
import sys
import types
import unittest

import numpy as np

_ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT_DIR = os.path.dirname(_ND)


def _load_module():
    if "ROOT" not in sys.modules:
        stub = types.ModuleType("ROOT")
        stub.gROOT = types.SimpleNamespace(SetBatch=lambda *a, **k: None)
        sys.modules["ROOT"] = stub
    for path in (os.path.join(_ROOT_DIR, "2d-unfolding"), _ND):
        if path not in sys.path:
            sys.path.insert(0, path)
    import unfold_nd_omnifold_unbinned as module
    return module


m = _load_module()


class RecordOnlyEavailShift(unittest.TestCase):
    def setUp(self):
        self.names = ["eavail", "q3", "W"]
        self.original = [
            np.array([0.1, 0.4, 1.2]),
            np.array([0.2, 0.7, 1.8]),
            np.array([0.9, 1.3, 2.4]),
        ]

    def test_positive_and_negative_arms_touch_only_eavail(self):
        for frac in (+0.10, -0.10):
            with self.subTest(frac=frac):
                shifted = m.apply_record_only_eavail_shift(
                    self.original, self.names, frac)
                np.testing.assert_allclose(shifted[0], self.original[0] * (1.0 + frac))
                np.testing.assert_array_equal(shifted[1], self.original[1])
                np.testing.assert_array_equal(shifted[2], self.original[2])

    def test_nominal_arrays_are_not_mutated_or_aliased(self):
        before = [col.copy() for col in self.original]
        shifted = m.apply_record_only_eavail_shift(self.original, self.names, 0.10)
        for got, expected in zip(self.original, before):
            np.testing.assert_array_equal(got, expected)
        for out, source in zip(shifted, self.original):
            self.assertFalse(np.shares_memory(out, source))

    def test_invalid_shift_or_schema_fails_closed(self):
        for frac in (0.0, -1.0, -1.2, np.nan, np.inf):
            with self.subTest(frac=frac), self.assertRaises(ValueError):
                m.apply_record_only_eavail_shift(self.original, self.names, frac)
        with self.assertRaises(ValueError):
            m.apply_record_only_eavail_shift(self.original[:2], ["q3", "W"], 0.1)
        with self.assertRaises(ValueError):
            m.apply_record_only_eavail_shift(self.original[:2], self.names, 0.1)
        with self.assertRaises(ValueError):
            m.apply_record_only_eavail_shift(
                [np.ones(2), np.ones(3), np.ones(2)], self.names, 0.1)


class DriverGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(_ND, "unfold_nd_omnifold_unbinned.py")) as stream:
            cls.source = stream.read()

    def test_diagnostic_is_applied_only_inside_closure_branch(self):
        closure = self.source.index("if args.closure:", self.source.index("# --- pseudo-data"))
        application = self.source.index("meas_ex = apply_record_only_eavail_shift", closure)
        real_data = self.source.index('elif args.bkg_mode == "purity":', closure)
        self.assertLess(closure, application)
        self.assertLess(application, real_data)

    def test_artifacts_are_labeled_nonquotable(self):
        self.assertIn('"NONQUOTABLE-DIAGNOSTIC."', self.source)
        self.assertIn('ROOT.TNamed("analysis_status", "NONQUOTABLE-DIAGNOSTIC")',
                      self.source)
        self.assertIn('"response-mismatch:reco-eavail-record-only"', self.source)

    def test_low_w_target_map_is_persisted(self):
        self.assertIn('"hClosureRatio_eavail_W"', self.source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
