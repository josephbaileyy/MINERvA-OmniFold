"""Synthetic tests for b1_projection.py (DECLARATION.md section 4, "Tests before the run")."""
import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b1_projection as b  # noqa: E402


def synth(n=205, seed=0):
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(n, n))
    lam = np.logspace(-10, 0, n)
    Q, _ = np.linalg.qr(A)
    V = (Q * lam) @ Q.T
    V = (V + V.T) / 2
    d = rng.normal(size=n) * 1e-3
    return V, d


class Bands(unittest.TestCase):
    def test_band_edges(self):
        self.assertEqual(b.band_of(0.5), "candidate")
        self.assertEqual(b.band_of(0.4999999), "partial")
        self.assertEqual(b.band_of(0.2), "minor")
        self.assertEqual(b.band_of(0.2000001), "partial")
        self.assertEqual(b.band_of(-0.2), "minor")
        self.assertEqual(b.band_of(-0.2000001), "opposite")
        self.assertEqual(b.band_of(1.5), "candidate")
        self.assertEqual(b.band_of(1.5000001), "overshoot")
        self.assertEqual(b.band_of(7.0), "overshoot")

    def test_label_interval(self):
        self.assertEqual(b.label(0.8, 0.3), "candidate")
        self.assertEqual(b.label(0.0, 0.2), "minor")
        self.assertEqual(b.label(0.49, 0.02), "unresolved across partial, candidate")
        self.assertEqual(b.label(-0.3, 0.2), "unresolved across opposite, minor")
        self.assertEqual(b.label(0.0, 1.0), "unresolved across opposite, minor, partial, candidate")
        self.assertEqual(b.label(0.5, 2.0), "unresolved across opposite, minor, partial, candidate, overshoot")
        self.assertEqual(b.label(1.6, 0.05), "overshoot")
        self.assertEqual(b.label(1.45, 0.1), "unresolved across candidate, overshoot")
        self.assertEqual(b.label(float("nan"), 0.1), "unresolved (non-finite)")

    def test_guard_zero_for_constant(self):
        self.assertEqual(b.guard([0.3] * 5), 0.0)

    def test_guard_formula(self):
        fs = [0.1, 0.2, 0.3, 0.4, 0.5]
        want = 2.7764451051977987 * np.std(fs, ddof=1) / math.sqrt(5)
        self.assertAlmostEqual(b.guard(fs), want, places=15)

    def test_combined(self):
        c = lambda labs: b.combined(dict(zip(("nominal", "genie_mec", "nuwro"), labs)))
        self.assertEqual(c(["candidate"] * 3), "candidate at every tested truth")
        self.assertEqual(c(["partial"] * 3), "partial at every tested truth")
        self.assertEqual(c(["minor"] * 3), "weakened at every tested truth")
        self.assertEqual(c(["opposite"] * 3), "opposite at every tested truth")
        self.assertEqual(c(["overshoot"] * 3), "overshoot at every tested truth")
        self.assertEqual(c(["minor", "minor", "partial"]), "truth-dependent")
        self.assertEqual(c(["minor", "minor", "unresolved across minor, partial"]), "unresolved at nuwro")
        self.assertEqual(c(["numerically unresolved", "minor", "unresolved across minor, partial"]),
                         "unresolved at nominal, nuwro")


class Projection(unittest.TestCase):
    def setUp(self):
        V, self.d = synth()
        lam, U = b.basis(V, "numpy")
        self.lam, self.U = b.signed_basis(lam, U, self.d)

    def run_pattern(self, beta):
        return b.project(self.lam, self.U, self.d, np.array([beta] * 5))[0]

    def test_beta_equals_delta(self):
        pr = self.run_pattern(self.d)
        for s in pr["sets"].values():
            self.assertAlmostEqual(s["g"], 1.0, places=10)
            self.assertAlmostEqual(s["remainder_unit_amplitude"], 0.0, places=10)
        for m in pr["modes"].values():
            self.assertAlmostEqual(m["rho"], 1.0, places=8)

    def test_beta_minus_delta(self):
        pr = self.run_pattern(-self.d)
        for s in pr["sets"].values():
            self.assertAlmostEqual(s["g"], -1.0, places=10)
        for m in pr["modes"].values():
            self.assertAlmostEqual(m["rho"], -1.0, places=8)

    def test_orthogonal(self):
        zd = b.whiten(self.lam, self.U, self.d)
        rng = np.random.default_rng(5)
        zb = rng.normal(size=zd.size)
        for idx in b.mode_sets(self.lam).values():  # orthogonalise within each set separately
            proj = np.sum(zb[idx] * zd[idx]) / np.sum(zd[idx] ** 2)
            zb[idx] -= proj * zd[idx]
        beta = self.U @ (np.sqrt(self.lam) * zb)
        pr = self.run_pattern(beta)
        for name, s in pr["sets"].items():
            self.assertLess(abs(s["g"]), 1e-6, name)

    def test_signs_fixed_positive(self):
        zd = b.whiten(self.lam, self.U, self.d)
        self.assertTrue(np.all(zd >= 0))

    def test_linearity_and_noise(self):
        rng = np.random.default_rng(9)
        betas = np.array([self.d * 0.3 + rng.normal(size=self.d.size) * 1e-5 for _ in range(5)])
        pr = b.project(self.lam, self.U, self.d, betas)[0]
        for s in pr["sets"].values():
            self.assertAlmostEqual(s["g"], s["g_mean_of_trials"], places=10)
            self.assertGreater(s["h"], 0.0)
        for m in pr["modes"].values():
            self.assertAlmostEqual(m["rho"], m["rho_mean_of_trials"], places=8)

    def test_mode_sets(self):
        ms = b.mode_sets(self.lam)
        self.assertEqual(len(ms["K73"]), 73)
        self.assertEqual(len(ms["Kbar"]), 132)
        self.assertTrue(np.all(self.lam[ms["K73"]].min() > self.lam[ms["Kbar"]].max()))
        for r in b.M_RANKS:
            self.assertIn(r, ms["Kbar"])  # declaration: all six M modes are in K-bar (ranks < 132)

    def test_drivers_agree_on_large_modes(self):
        lam2, U2 = b.signed_basis(*b.basis((self.U * self.lam) @ self.U.T, "evr"), self.d)
        z1 = b.whiten(self.lam, self.U, self.d)
        z2 = b.whiten(lam2, U2, self.d)
        top = b.mode_sets(self.lam)["K73"]
        self.assertLess(np.max(np.abs(z1[top] - z2[top]) / np.abs(z1[top])), 1e-6)


if __name__ == "__main__":
    unittest.main()
