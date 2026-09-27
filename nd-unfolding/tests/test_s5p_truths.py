"""Controls for s5p_truths: the conditional reweight preserves every fine (E_avail, W) truth marginal exactly
and changes the q3 shape; the coarse reweight reproduces the numerator's coarse integrals when the
denominator is the truth itself; out-of-grid rows keep r = 1."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_truths as st  # noqa: E402

EDGES = [np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 2.0]), np.array([0.0, 0.5, 1.0]),
         np.array([0.0, 1.0, 2.0, 3.0]), np.array([0.0, 1.5, 3.0])]


def rows(n=40000, seed=0):
    rng = np.random.default_rng(seed)
    gen = np.column_stack([rng.uniform(0, 2, n), rng.uniform(0, 2, n), rng.uniform(0, 1, n),
                           rng.uniform(0, 3, n), rng.uniform(0, 3, n)])
    gen[:10, 3] = -9999.0
    return gen, rng.uniform(0.5, 1.5, n)


class Tests(unittest.TestCase):
    def test_cond_reweight_preserves_the_eavail_w_marginal_and_moves_q3(self):
        gen, w = rows()
        shape = tuple(len(e) - 1 for e in EDGES)
        num = np.ones(shape)
        num[:, :, :, 2, :] = 3.0  # more high q3 in the numerator
        rho, stats = st.cond_ratio(num, np.ones(shape), EDGES)
        ratio = {"edges": [EDGES[2].tolist(), EDGES[4].tolist(), EDGES[3].tolist()], "rho": rho.ravel().tolist()}
        r = st.cond_weight(gen, EDGES, w, ratio, 1.0)
        self.assertTrue(np.all(r[:10] == 1.0))
        ok = np.all(gen[:, 3:4] >= 0, axis=1)
        ie = np.clip(np.searchsorted(EDGES[2], gen[ok, 2], side="right") - 1, 0, 1)
        iw = np.clip(np.searchsorted(EDGES[4], gen[ok, 4], side="right") - 1, 0, 1)
        cell = ie * 2 + iw
        np.testing.assert_allclose(np.bincount(cell, w[ok] * r[ok]), np.bincount(cell, w[ok]), rtol=1e-12)
        hi = gen[ok, 3] >= 2.0
        self.assertGreater(np.average(r[ok][hi], weights=w[ok][hi]), 1.5)

    def test_coarse_reweight_reproduces_numerator_integrals_without_rescaling(self):
        gen, w = rows()
        shape = tuple(len(e) - 1 for e in EDGES)
        cedges = [EDGES[0][[0, 2]], EDGES[1][[0, 1, 2]], EDGES[2][[0, 2]], EDGES[3][[0, 1, 3]], EDGES[4][[0, 2]]]
        den = np.ones(shape)
        num = np.ones(shape) * np.linspace(0.5, 2.0, int(np.prod(shape))).reshape(shape)
        n_c, d_c = st.coarse_integrals(num, EDGES, cedges), st.coarse_integrals(den, EDGES, cedges)
        ratio = {"coarse_edges": [c.tolist() for c in cedges], "rho": (n_c / d_c).tolist(), "preserve_total": False}
        r = st.coarse_weight(gen, EDGES, w, ratio, 1.0)
        ok, cell = st.coarse_cells(gen, EDGES, cedges)
        np.testing.assert_allclose(r[ok], (n_c / d_c)[cell])
        self.assertTrue(np.all(r[~ok] == 1.0))
        ratio["preserve_total"] = True
        r2 = st.coarse_weight(gen, EDGES, w, ratio, 1.0)
        self.assertAlmostEqual((w[ok] * r2[ok]).sum() / w[ok].sum(), 1.0, places=12)

    def _fine_setup(self):
        shape = tuple(len(e) - 1 for e in EDGES)
        cedges = [EDGES[0][[0, 2]], EDGES[1][[0, 1, 2]], EDGES[2][[0, 2]], EDGES[3][[0, 1, 3]], EDGES[4][[0, 2]]]
        rng = np.random.default_rng(7)
        den = rng.uniform(0.5, 1.5, shape)
        num = den * rng.uniform(0.6, 1.6, shape)
        n_den = np.full(shape, 100.0).ravel()
        n_num = np.full(shape, 100.0).ravel()
        return shape, cedges, num, den, n_num, n_den

    def test_fine_ratio_is_the_fine_ratio_and_keeps_every_coarse_integral(self):
        """Review round 1 F2: the fine null's within-coarse-cell shape is the numerator's; the coarse integrals
        of rho x D are N_c exactly, also when low-count fine cells share a remainder."""
        shape, cedges, num, den, n_num, n_den = self._fine_setup()
        n_num[::5] = 3.0  # unresolved fine cells
        only = np.ones(4, bool)
        only[3] = False
        rho, acc = st.fine_ratio(num, den, n_num, n_den, EDGES, cedges, only)
        vol = st.volumes(EDGES).ravel()
        cell = st.fine_cell_of_fine_grid(EDGES, cedges)
        N, D = num.ravel() * vol, den.ravel() * vol
        resolved = n_num >= st.FINE_N_MIN
        for c in range(3):
            inc = cell == c
            self.assertAlmostEqual((rho[inc] * D[inc]).sum() / N[inc].sum(), 1.0, places=12)
            np.testing.assert_allclose(rho[inc & resolved], (N / D)[inc & resolved], rtol=1e-12)
        self.assertTrue(np.all(rho[cell == 3] == 1.0))
        self.assertEqual(acc["coarse_cells_carrying"], 3)
        self.assertGreater(acc["fine_cells_fallback"], 0)
        self.assertLess(acc["max_abs_coarse_integral_error_rel"], 1e-12)

    def test_fine_ratio_reverts_a_cell_whose_remainder_is_unphysical(self):
        shape, cedges, num, den, n_num, n_den = self._fine_setup()
        vol = st.volumes(EDGES).ravel()
        cell = st.fine_cell_of_fine_grid(EDGES, cedges)
        inc = np.flatnonzero(cell == 0)
        n_num[inc[0]] = 1.0  # one unresolved cell whose remainder ratio 50 exceeds the fallback clip
        num = num.ravel().copy()
        num[inc[0]] = 50.0 * den.ravel()[inc[0]]
        rho, acc = st.fine_ratio(num.reshape(shape), den, n_num, n_den, EDGES, cedges, np.ones(4, bool))
        D, N = den.ravel() * vol, num * vol
        np.testing.assert_allclose(rho[inc], N[inc].sum() / D[inc].sum(), rtol=1e-12)
        self.assertEqual(acc["coarse_cells_reverted_to_coarse"], 1)

    def test_fine_ratio_lets_an_empty_generator_region_empty_the_truth(self):
        shape, cedges, num, den, n_num, n_den = self._fine_setup()
        cell = st.fine_cell_of_fine_grid(EDGES, cedges)
        inc = np.flatnonzero(cell == 0)
        num = num.ravel().copy()
        num[inc[:2]] = 0.0
        n_num[inc[:2]] = 0.0
        rho, acc = st.fine_ratio(num.reshape(shape), den, n_num, n_den, EDGES, cedges, np.ones(4, bool))
        self.assertTrue(np.all(rho[inc[:2]] == 0.0))
        self.assertEqual(acc["coarse_cells_reverted_to_coarse"], 0)

    def test_fine_ratio_of_a_prediction_with_itself_is_one(self):
        shape, cedges, num, den, n_num, n_den = self._fine_setup()
        rho, _ = st.fine_ratio(den, den, n_den, n_den, EDGES, cedges, np.ones(4, bool))
        np.testing.assert_allclose(rho, 1.0, rtol=1e-12)

    def test_fine_weight_reads_a_verified_rho_and_reweights_rows_by_fine_cell(self):
        import tempfile
        gen, w = rows()
        shape, cedges, num, den, n_num, n_den = self._fine_setup()
        rho, _ = st.fine_ratio(num, den, n_num, n_den, EDGES, cedges, np.ones(4, bool))
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "rho.npz"
            np.savez_compressed(f, rho=rho)
            ratio = {"schema": "s5p-fine-ratio/1", "fine_edges": [e.tolist() for e in EDGES],
                     "rho_npz": {"path": str(f), "sha256": st.sha256(f)}}
            r = st.hypothesis_weight(gen, EDGES, w, ratio)
            self.assertTrue(np.all(r[:10] == 1.0))
            ok, idx = st.cell_of(gen, EDGES)
            np.testing.assert_allclose(r[ok], rho[np.ravel_multi_index(idx, shape)], rtol=0)
            ratio["rho_npz"]["sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                st.hypothesis_weight(gen, EDGES, w, ratio)

    def test_fine_weight_accepts_a_zero_rho_and_refuses_a_negative_weight(self):
        import tempfile
        gen, w = rows()
        shape = tuple(len(e) - 1 for e in EDGES)
        rho = np.ones(int(np.prod(shape)))
        rho[0] = 0.0
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "rho.npz"
            np.savez_compressed(f, rho=rho)
            ratio = {"schema": "s5p-fine-ratio/1", "fine_edges": [e.tolist() for e in EDGES],
                     "rho_npz": {"path": str(f), "sha256": st.sha256(f)}}
            r = st.fine_weight(gen, EDGES, w, ratio, 1.0)
            ok, idx = st.cell_of(gen, EDGES)
            self.assertTrue(np.all(r[ok][np.ravel_multi_index(idx, shape) == 0] == 0.0))
            with self.assertRaises(ValueError):
                st.fine_weight(gen, EDGES, w, ratio, 2.0)  # 1 + 2 (0 - 1) < 0

    def test_mid_ratio_keeps_coarse_integrals_and_is_constant_within_merged_cells(self):
        shape, cedges, num, den, n_num, n_den = self._fine_setup()
        me = st.merged_edges(EDGES, cedges, 2)
        for m, c in zip(me, cedges):
            self.assertTrue(set(np.asarray(c).tolist()) <= set(m.tolist()))
        rho, acc = st.mid_ratio(num, den, n_num, n_den, EDGES, cedges, np.ones(4, bool), 2)
        vol = st.volumes(EDGES).ravel()
        cell = st.fine_cell_of_fine_grid(EDGES, cedges)
        N, D = num.ravel() * vol, den.ravel() * vol
        for c in range(4):
            inc = cell == c
            self.assertAlmostEqual((rho[inc] * D[inc]).sum() / N[inc].sum(), 1.0, places=12)
        self.assertEqual(acc["resolution"], "merged x2")


if __name__ == "__main__":
    unittest.main()
