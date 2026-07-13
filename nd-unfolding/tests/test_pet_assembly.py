"""Phase-8 tests: the 5D->4D density projection and PSD diagnostics."""
import sys
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND / "pet"))

import assemble_ctotal_bkgsub as ac  # noqa: E402


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.shape5 = (2, 3, 2, 2, 3)      # small stand-in for (14,16,7,7,6)
        self.w_edges = np.array([0.0, 1.0, 3.0, 6.0])   # dW = [1,2,3]
        rng = np.random.default_rng(0)
        self.cv_full = rng.uniform(0.1, 1.0, int(np.prod(self.shape5)))
        # reported: drop ~30% of bins
        self.mask = rng.uniform(size=self.cv_full.size) > 0.3

    def test_projection_matches_bruteforce(self):
        M, rep5_idx, rep4_idx, shape4 = ac.build_5d_to_4d_projection(
            self.mask, self.shape5, self.w_edges)
        cv5 = self.cv_full[self.mask]
        cv4 = M @ cv5
        # brute force: 4D density = sum over reported W bins of cv5 * dW
        dW = np.diff(self.w_edges)
        brute = {}
        idx = np.unravel_index(np.flatnonzero(self.mask), self.shape5)
        q4 = np.ravel_multi_index(idx[:4], shape4)
        for p, (q, m) in enumerate(zip(q4, idx[4])):
            brute[int(q)] = brute.get(int(q), 0.0) + self.cv_full[np.flatnonzero(self.mask)[p]] * dW[m]
        expected = np.array([brute[int(q)] for q in rep4_idx])
        np.testing.assert_allclose(cv4, expected, rtol=1e-12)

    def test_c4d_symmetric_psd(self):
        M, rep5_idx, rep4_idx, _ = ac.build_5d_to_4d_projection(
            self.mask, self.shape5, self.w_edges)
        n5 = M.shape[1]
        rng = np.random.default_rng(1)
        A = rng.normal(size=(n5, n5 + 4))
        C5 = A @ A.T                        # PSD by construction
        C4 = M @ C5 @ M.T
        self.assertLess(float(np.abs(C4 - C4.T).max()), 1e-9)
        self.assertGreaterEqual(float(np.linalg.eigvalsh(0.5 * (C4 + C4.T)).min()),
                                -1e-9 * max(np.linalg.eigvalsh(C4).max(), 1e-9))

    def test_w_edge_mismatch_raises(self):
        with self.assertRaises(ValueError):
            ac.build_5d_to_4d_projection(self.mask, self.shape5,
                                         np.array([0.0, 1.0]))  # only 1 W bin != 3

    def test_psd_diagnostics_flags(self):
        good = np.diag([1.0, 2.0, 3.0])
        self.assertTrue(ac.psd_diagnostics(good)["psd_within_tol"])
        bad = np.array([[1.0, 2.0], [2.0, 1.0]])   # eigenvalues -1, 3
        self.assertFalse(ac.psd_diagnostics(bad)["psd_within_tol"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
