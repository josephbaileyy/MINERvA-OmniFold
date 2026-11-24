"""Tests for covfix_u2_calibrate.py (synthetic tables only; no pinned input is read)."""
from __future__ import annotations

import unittest

import numpy as np

import covfix_u2_calibrate as cal

SHAPE = cal.SHAPE


def gaussian_table(rho: float, seed: int = 0, sparse: float = 0.0) -> np.ndarray:
    """Per (pT, p_par, E_avail) cell, a discretized bivariate normal in (q3 index, W index) with correlation rho."""
    rng = np.random.default_rng(seed)
    qi = np.arange(SHAPE[3])[:, None] - 3.0
    wi = np.arange(SHAPE[4])[None, :] - 2.5
    base = np.exp(-(qi ** 2 - 2 * rho * qi * wi + wi ** 2) / (2 * 1.5 ** 2 * (1 - rho ** 2)))
    scale = rng.uniform(0.5, 2.0, SHAPE[:3])
    s = scale[..., None, None] * base
    if sparse:
        s[rng.uniform(size=SHAPE[:3]) < sparse] = 0.0
    return s


class Correlation(unittest.TestCase):
    def test_sign_and_size(self):
        r_pos, v = cal.cell_corr(gaussian_table(0.5))
        r_neg, _ = cal.cell_corr(gaussian_table(-0.5))
        self.assertTrue(v.all())
        self.assertTrue(np.all(r_pos > 0.3) and np.all(r_neg < -0.3))
        np.testing.assert_allclose(r_pos, -r_neg, atol=1e-12)

    def test_exact_two_by_two(self):
        s = np.zeros(SHAPE)
        s[0, 0, 0, 0, 0] = s[0, 0, 0, 1, 1] = 1.0   # perfectly correlated indices
        s[0, 0, 1, 0, 1] = s[0, 0, 1, 1, 0] = 1.0   # perfectly anti-correlated
        s[0, 0, 2, 0, 0] = 1.0                        # one bin: invalid
        rho, valid = cal.cell_corr(s)
        self.assertAlmostEqual(rho[0, 0, 0], 1.0, places=12)
        self.assertAlmostEqual(rho[0, 0, 1], -1.0, places=12)
        self.assertFalse(valid[0, 0, 2])
        self.assertEqual(int(valid.sum()), 2)

    def test_scale_invariant(self):
        s = gaussian_table(0.3)
        np.testing.assert_allclose(cal.cell_corr(s)[0], cal.cell_corr(7.0 * s)[0], atol=1e-12)

    def test_mean_abs_drho_weights_and_validity(self):
        a, b = gaussian_table(0.4), gaussian_table(0.1)
        d, n = cal.mean_abs_drho(a, b, a.sum(axis=(3, 4)))
        ra, _ = cal.cell_corr(a)
        rb, _ = cal.cell_corr(b)
        w = a.sum(axis=(3, 4))
        self.assertAlmostEqual(d, float((w * np.abs(ra - rb)).sum() / w.sum()), places=12)
        self.assertEqual(n, int(np.prod(SHAPE[:3])))
        b2 = b.copy()
        b2[0, 0, 0] = 0.0
        self.assertEqual(cal.mean_abs_drho(a, b2, w)[1], n - 1)


class Raking(unittest.TestCase):
    def test_restores_all_three_margins(self):
        w = gaussian_table(0.2, sparse=0.3)
        rng = np.random.default_rng(3)
        r, it = cal.rake(w, rng.uniform(0.5, 2.0, SHAPE))
        v = w * r
        for ax in ((3, 4), (0, 1, 2, 4), (0, 1, 2, 3)):
            t = w.sum(axis=ax)
            m = t > 0
            self.assertLessEqual(np.max(np.abs(v.sum(axis=ax)[m] - t[m]) / t[m]), cal.RAKE_TOL)
        self.assertLessEqual(it, cal.RAKE_MAXIT)

    def test_identity_is_one_iteration(self):
        w = gaussian_table(0.2)
        r, it = cal.rake(w, np.ones(SHAPE))
        self.assertEqual(it, 1)
        np.testing.assert_allclose(r, 1.0, atol=1e-14)

    def test_non_convergence_refused(self):
        w = gaussian_table(0.2)
        old = cal.RAKE_MAXIT
        cal.RAKE_MAXIT = 1
        try:
            with self.assertRaises(cal.Refusal):
                cal.rake(w, np.random.default_rng(1).uniform(0.5, 2.0, SHAPE))
        finally:
            cal.RAKE_MAXIT = old


class Tilt(unittest.TestCase):
    def test_clip_and_zero(self):
        w = gaussian_table(0.0)
        np.testing.assert_allclose(cal.tilt(w, 0.0), 1.0)
        r = cal.tilt(w, 50.0)
        self.assertEqual(r.min(), 0.5)
        self.assertEqual(r.max(), 2.0)

    def test_amplitude_increases_and_positive_c_raises_rho(self):
        w = gaussian_table(0.0)
        a0, _, _ = cal.amplitude(w, 0.0)
        a1, r1, _ = cal.amplitude(w, 0.2)
        a2, _, _ = cal.amplitude(w, 0.4)
        self.assertAlmostEqual(a0, 0.0, places=9)
        self.assertLess(a1, a2)
        rho1, _ = cal.cell_corr(w * r1)
        self.assertGreater(float(rho1.mean()), 0.0)


class Noise(unittest.TestCase):
    def test_zero_noise_is_zero_and_noise_is_positive(self):
        tabs = {g: gaussian_table(0.1 * i, seed=1) for i, g in enumerate(("genie_cv", *cal.BUILD_TRUTHS))}
        zero = cal.noise_diagnostic(tabs, {g: np.zeros(SHAPE) for g in tabs})
        self.assertTrue(all(v == 0.0 for v in zero["self_noise"].values()))
        some = cal.noise_diagnostic(tabs, {g: 0.05 * t for g, t in tabs.items()})
        self.assertTrue(all(v > 0.0 for v in some["self_noise"].values()))
        q = some["quadrature_vs_reference"]["gibuu"]
        self.assertAlmostEqual(q, float(np.hypot(some["self_noise"]["gibuu"], some["self_noise"]["genie_cv"])))


class Calibrate(unittest.TestCase):
    def tables(self):
        return {"genie_cv": gaussian_table(0.0, seed=1), "genie_mec": gaussian_table(0.05, seed=1),
                "nuwro": gaussian_table(0.10, seed=1), "gibuu": gaussian_table(-0.15, seed=1)}

    def test_brackets_and_targets(self):
        out = cal.calibrate(self.tables())
        self.assertLess(out["a_lo"], out["a_hi"])
        self.assertAlmostEqual(out["at_a_lo"]["A"], out["D_min"], places=4)
        self.assertAlmostEqual(out["at_a_hi"]["A"], out["D_max"], places=4)
        self.assertEqual(out["D_min"], min(v["D"] for v in out["D"].values()))

    def test_target_beyond_scan_refused(self):
        t = self.tables()
        t["gibuu"] = gaussian_table(-0.99, seed=1)
        old = cal.SCAN
        cal.SCAN = np.linspace(0.0, 0.05, 6)
        try:
            with self.assertRaises(cal.Refusal):
                cal.calibrate(t)
        finally:
            cal.SCAN = old

    def test_main_refuses_wrong_sha_and_overwrite(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            for g, (name, _) in cal.PINS.items():
                (d / name).write_bytes(b"not the pinned file")
            self.assertEqual(cal.main(["--inputs", str(d), "--out", str(d / "o.json")]), 3)
            (d / "o.json").write_text("{}")
            self.assertEqual(cal.main(["--inputs", str(d), "--out", str(d / "o.json")]), 2)


if __name__ == "__main__":
    unittest.main()
