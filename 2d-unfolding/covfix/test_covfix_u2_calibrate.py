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
    def test_rho_variance_zero_without_noise_and_inf_when_invalid(self):
        s = gaussian_table(0.2)
        s[0, 0, 0] = 0.0
        v = cal.rho_variance(s, np.zeros(SHAPE), np.random.default_rng(0))
        self.assertTrue(np.isinf(v[0, 0, 0]))
        self.assertLess(float(np.max(v[np.isfinite(v)])), 1e-25)

    def test_rho_variance_matches_spread(self):
        s = gaussian_table(0.2)
        old = cal.NOISE_REPS
        cal.NOISE_REPS = 400
        try:
            v1 = cal.rho_variance(s, 0.02 * s, np.random.default_rng(1))
            v2 = cal.rho_variance(s, 0.04 * s, np.random.default_rng(1))
        finally:
            cal.NOISE_REPS = old
        self.assertTrue(np.all(v1 > 0))
        ratio = float(np.median(v2 / v1))
        self.assertGreater(ratio, 3.0)
        self.assertLess(ratio, 5.0)

    def test_rho_variance_is_ddof1_over_the_replay(self):
        s = gaussian_table(0.2)
        sd = 0.05 * s
        old = cal.NOISE_REPS
        cal.NOISE_REPS = 5
        try:
            v = cal.rho_variance(s, sd, np.random.default_rng(9))
            rng = np.random.default_rng(9)
            reps = np.stack([cal.cell_corr(cal.resample(s, sd, rng))[0] for _ in range(5)])
        finally:
            cal.NOISE_REPS = old
        np.testing.assert_allclose(v, np.var(reps, axis=0, ddof=1), rtol=1e-12)

    def test_debiased_formula(self):
        a, b = gaussian_table(0.3, seed=2), gaussian_table(0.1, seed=2)
        w = b.sum(axis=(3, 4))
        ra, _ = cal.cell_corr(a)
        rb, _ = cal.cell_corr(b)
        va = np.random.default_rng(5).uniform(0.0, 0.004, SHAPE[:3])
        vb = np.full(SHAPE[:3], 0.002)
        va[0, 0, 0] = np.inf
        out = cal.debiased(a, b, va, vb, w)
        d2 = np.maximum(0.0, (ra - rb) ** 2 - va - vb)
        self.assertAlmostEqual(out["D_debiased"], float((w * np.sqrt(d2)).sum() / w.sum()), places=12)
        self.assertAlmostEqual(out["D"], float((w * np.abs(ra - rb)).sum() / w.sum()), places=12)
        self.assertEqual(out["cells_debiased_to_zero"], int(np.sum(d2 == 0.0)))
        self.assertEqual(out["cells_with_infinite_noise"], 1)
        m = np.isfinite(va)
        self.assertAlmostEqual(out["noise_scale"], float((w[m] * np.sqrt(va + vb)[m]).sum() / w[m].sum()), places=12)
        self.assertLess(out["D_debiased"], out["D"])

    def test_debiased_equals_raw_without_noise(self):
        a, b = gaussian_table(0.3, seed=2), gaussian_table(0.1, seed=2)
        z = np.zeros(SHAPE[:3])
        out = cal.debiased(a, b, z, z, b.sum(axis=(3, 4)))
        self.assertAlmostEqual(out["D_debiased"], out["D"], places=12)
        self.assertEqual(out["cells_debiased_to_zero"], 0)


class Calibrate(unittest.TestCase):
    def tables(self, gibuu_rho=-0.15, mec_rho=0.05):
        return {"genie_cv": gaussian_table(0.0, seed=1), "genie_mec": gaussian_table(mec_rho, seed=1),
                "nuwro": gaussian_table(0.10, seed=1), "gibuu": gaussian_table(gibuu_rho, seed=1)}

    def run_cal(self, tables, rel_sd=0.0, reps=20):
        old = cal.NOISE_REPS
        cal.NOISE_REPS = reps
        try:
            return cal.calibrate(tables, {g: rel_sd * t for g, t in tables.items()})
        finally:
            cal.NOISE_REPS = old

    def test_noiseless_rules_agree_min_branch(self):
        out = self.run_cal(self.tables())
        r1, r2 = out["rule1_raw"], out["rule2_debiased"]
        self.assertEqual(r2["branch"], "min")
        self.assertAlmostEqual(r1["a_lo"], r2["a_lo"], places=6)
        self.assertAlmostEqual(r1["a_hi"], r2["a_hi"], places=6)
        self.assertAlmostEqual(r2["at_a_lo"]["A"], r2["t_lo"], places=4)
        self.assertAlmostEqual(r2["at_a_hi"]["A"], r2["t_hi"], places=4)
        self.assertEqual(out["a_lo"], r2["a_lo"])
        self.assertAlmostEqual(r2["nontrivial_threshold"], 0.5 * r2["t_lo"], places=15)
        self.assertEqual(out["map_noise"]["at_a_lo"]["A_sd"], 0.0)

    def test_floor_branch(self):
        t = self.tables(mec_rho=0.005)   # min D' below 0.25 x max D'
        out = self.run_cal(t)
        r2 = out["rule2_debiased"]
        self.assertEqual(r2["branch"], "floor")
        self.assertAlmostEqual(r2["t_lo"], 0.25 * r2["t_hi"], places=15)
        self.assertGreater(r2["t_lo"], r2["min_D_debiased"])
        self.assertAlmostEqual(r2["at_a_lo"]["A"], r2["t_lo"], places=4)

    def test_noise_lowers_debiased_targets(self):
        out = self.run_cal(self.tables(), rel_sd=0.05, reps=50)
        per = out["per_truth"]
        self.assertTrue(all(v["D_debiased"] < v["D"] for v in per.values()))
        self.assertLess(out["rule2_debiased"]["t_hi"], out["rule1_raw"]["t_hi"])
        self.assertGreater(out["map_noise"]["at_a_hi"]["A_sd"], 0.0)

    def test_non_monotone_scan_refused(self):
        old = cal.amplitude
        cal.amplitude = lambda w, c: (abs(c - 1.0), None, 1)
        try:
            with self.assertRaises(cal.Refusal):
                cal._scan(gaussian_table(0.0))
        finally:
            cal.amplitude = old

    def test_all_zero_debiased_refused(self):
        t = {g: gaussian_table(0.0, seed=1) for g in ("genie_cv", *cal.BUILD_TRUTHS)}
        with self.assertRaises(cal.Refusal):
            self.run_cal(t)

    def test_target_beyond_scan_refused(self):
        t = self.tables(gibuu_rho=-0.99)
        old = cal.SCAN
        cal.SCAN = np.linspace(0.0, 0.05, 6)
        try:
            with self.assertRaises(cal.Refusal):
                self.run_cal(t)
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
