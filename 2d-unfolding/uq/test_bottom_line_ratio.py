"""Tests for bottom_line_test.bottom_line_ratio, the shared 2D/3D/5D recovery statistic.

ROOT is stubbed so the pure-numpy statistic runs anywhere.
"""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

import numpy as np

sys.modules.setdefault("ROOT", types.SimpleNamespace(
    gROOT=types.SimpleNamespace(SetBatch=lambda *_: None),
    TH1=types.SimpleNamespace(AddDirectory=lambda *_: None)))
_spec = importlib.util.spec_from_file_location(
    "bottom_line_test", Path(__file__).resolve().parent / "bottom_line_test.py")
blt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(blt)

NOM = np.array([10.0, 8.0, 6.0, 4.0, 2.0, 1.0])
BUMP = np.array([1.0, 1.30, 1.10, 1.0, 1.0, 1.0])
REF = NOM * BUMP


class BottomLineRatioTest(unittest.TestCase):
    def test_perfect_recovery_passes_with_zero_ratio(self):
        r = blt.bottom_line_ratio(REF, REF, NOM, 0.20)
        self.assertEqual(r["ratio"], 0.0)
        self.assertEqual(r["verdict"], "PASS")

    def test_no_recovery_fails(self):
        # Unfolding returns the prior: the residual is the whole feature.
        r = blt.bottom_line_ratio(NOM, REF, NOM, 0.20)
        self.assertGreater(r["ratio"], 0.7)
        self.assertEqual(r["verdict"], "FAIL")

    def test_null_injection_has_no_feature(self):
        # The June 5D defect: ref == nom, so the statistic is undefined, not a pass.
        r = blt.bottom_line_ratio(NOM, NOM, NOM, 0.20)
        self.assertTrue(np.isnan(r["ratio"]))
        self.assertEqual(r["verdict"], "FAIL")

    def test_feature_bins_and_hand_value(self):
        unf = REF * np.array([1.0, 1.03, 0.99, 1.0, 1.0, 1.0])
        r = blt.bottom_line_ratio(unf, REF, NOM, 0.20)
        inj = BUMP - 1
        all_rms = np.sqrt(np.mean(inj ** 2))
        feat = np.abs(inj) > all_rms
        self.assertEqual(list(np.flatnonzero(r["feature_mask"])), list(np.flatnonzero(feat)))
        want = (np.sqrt(np.mean((unf / REF - 1)[feat] ** 2))
                / np.sqrt(np.mean(inj[feat] ** 2)))
        self.assertAlmostEqual(r["ratio"], want, places=12)
        self.assertEqual(r["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
