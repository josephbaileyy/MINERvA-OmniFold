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


if __name__ == "__main__":
    unittest.main()
