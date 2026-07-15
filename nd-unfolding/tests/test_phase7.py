"""Phase-7 tests: universe-key -> bank-file mapping, r_u injection alignment,
and the predeclared materiality metric. Pure numpy (login-runnable)."""
import sys
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND / "pet"))

import phase7_extract_compare as pc  # noqa: E402


class MaterialityTests(unittest.TestCase):
    def test_immaterial_small_delta(self):
        rng = np.random.default_rng(0)
        s = rng.normal(size=500)
        delta = 0.01 * s                      # 1% of the frozen shift everywhere
        m = pc.materiality(delta, s)
        self.assertFalse(m["material"])
        self.assertLess(m["overall_ratio"], pc.THRESH_OVERALL)
        self.assertEqual(m["frac_bins_over"], 0.0)

    def test_material_by_overall(self):
        rng = np.random.default_rng(1)
        s = rng.normal(size=500)
        delta = 0.5 * s                        # 50% overall -> material
        m = pc.materiality(delta, s)
        self.assertTrue(m["material"])
        self.assertGreater(m["overall_ratio"], pc.THRESH_OVERALL)

    def test_material_by_bin_tail(self):
        # small overall norm but a fat per-bin tail in >5% of bins
        s = np.ones(1000)
        delta = np.zeros(1000)
        delta[:80] = 0.5                       # 8% of bins exceed 0.25*|s|
        m = pc.materiality(delta, s)
        self.assertGreater(m["frac_bins_over"], pc.THRESH_FRAC)
        self.assertTrue(m["material"])

    def test_zero_frozen_shift_is_inf(self):
        m = pc.materiality(np.array([1e-40, -1e-40]), np.zeros(2))
        self.assertEqual(m["norm_s"], 0.0)
        self.assertTrue(np.isinf(m["overall_ratio"]))
        self.assertTrue(m["material"])


class RatioInjectionTests(unittest.TestCase):
    """Prove the disk-free r_u injection == scaling raw w_truth then normalizing.
    Normalization is scale-homogeneous, so normalize(w_norm * r) must equal
    normalize(w_raw * r) up to the same overall constant."""

    @staticmethod
    def _normalize(w):
        w = np.asarray(w, float)
        return w * (w.size / w.sum())

    def test_scale_homogeneous_injection(self):
        rng = np.random.default_rng(2)
        w_raw = rng.uniform(0.1, 3.0, 4000)
        r = rng.uniform(0.2, 5.0, 4000)
        w_norm = self._normalize(w_raw)                       # loader already normalized
        path_inject = self._normalize(w_norm * r)             # driver's disk-free path
        path_raw = self._normalize(w_raw * r)                 # scale-then-normalize truth
        np.testing.assert_allclose(path_inject, path_raw, rtol=1e-12)

    def test_subsample_index_alignment(self):
        # r_u is full-cloud order; the driver applies r_u[imc] to the subsample.
        N = 10000
        r_full = np.arange(N, dtype=float)                    # identity so we can check
        rng = np.random.default_rng(3)
        imc = np.sort(rng.choice(N, 2000, replace=False))
        got = r_full[imc]
        self.assertEqual(got.shape[0], imc.shape[0])
        np.testing.assert_array_equal(got, imc.astype(float))


class UniverseKeyTests(unittest.TestCase):
    def test_knob_endpoints(self):
        self.assertEqual(pc.universe_file("MaRES:1"), ("sig_MaRES_t_1.npy", "MaRES:+1"))
        self.assertEqual(pc.universe_file("2p2h:0"), ("sig_2p2h_t_0.npy", "2p2h:-1"))
        self.assertEqual(pc.universe_file("flux:37"), ("sig_flux_t_37.npy", "Flux:37"))

    def test_bad_endpoint_raises(self):
        with self.assertRaises(ValueError):
            pc.universe_file("MaRES:2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
