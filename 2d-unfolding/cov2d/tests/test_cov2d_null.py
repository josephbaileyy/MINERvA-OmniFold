"""cov2d_null: the laws reproduce the blocks (so check_matched holds at 1e-12), the seed is cov2d.NULL_SEED and the
cell rule divides by 205 (the director's R5), and a mismatched null refuses. numpy only: runs in either env.
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_null
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cov2d as c  # noqa: E402
import cov2d_null as cn  # noqa: E402

N = 205


def fixture(seed=4):
    r = np.random.default_rng(seed)
    x = r.uniform(1.0, 2.0, N)
    bands = {b: x + 0.05 * r.standard_normal((c.BANDS[b], N)) for b in c.ORDER}
    for b in c.LATERAL_BANDS:
        bands[b] = x + 0.05 * r.standard_normal((2, N))
    minos_x = x + 0.05 * r.standard_normal((2, N))
    w = r.uniform(0.5, 1.5, 100)
    A = r.standard_normal((N, 30)) * 0.01
    G = A @ A.T

    def wcov(X, p):
        d = X - p @ X
        return (d * p[:, None]).T @ d
    C_univ = sum(wcov(bands[b], w / w.sum() if b == c.FLUX else np.full(c.BANDS[b], 1 / c.BANDS[b])) for b in c.ORDER)
    C_lat = sum(0.25 * np.outer(*(2 * [(minos_x if b == cn.MINOS else bands[b])[0]
                                       - (minos_x if b == cn.MINOS else bands[b])[1]])) for b in c.LATERAL_BANDS)
    blocks = {"C_stat": 0.4 * G, "C_norm": 0.2 * G, "C08": 0.1 * G, "C_model_abs": 0.3 * G}
    blocks["C_T"] = C_univ + C_lat + G
    return blocks, bands, minos_x, w


class Null(unittest.TestCase):
    def setUp(self):
        self.blocks, self.bands, self.minos_x, self.w = fixture()

    def test_laws_reproduce_the_blocks_and_the_null_runs_at_the_declared_seed(self):
        seen = {}
        real = cn.nl.null_contents

        def spy(laws, gauss, C_T, n_mc, seed):
            seen.update(seed=seed, n_laws=len(laws))
            return real(laws, gauss, C_T, n_mc=n_mc, seed=seed)
        with mock.patch.object(cn.nl, "null_contents", spy):
            out = cn.null_at_T(self.blocks, self.bands, self.minos_x, self.w, n_mc=20_000)
        self.assertEqual(seen, {"seed": 5_742_000, "n_laws": 43})
        self.assertLessEqual(out["null"]["match_rel"], 1e-12)
        self.assertEqual(out["thresholds"]["alpha_cell"], 0.025 / 205)
        self.assertEqual(len(out["thresholds"]["k_cell"]), 205)
        self.assertEqual(out["thresholds"]["n"], 300)

    def test_minos_law_uses_x01(self):
        laws = cn.laws_at_T(self.bands, self.minos_x, self.w)
        minos = laws[38 + c.LATERAL_BANDS.index(cn.MINOS)]
        d = self.minos_x[0] - self.minos_x[1]
        np.testing.assert_allclose(minos.cov(), 0.25 * np.outer(d, d), rtol=1e-12)

    def test_a_mismatched_null_refuses(self):
        bad = dict(self.blocks, C_T=self.blocks["C_T"] * (1 + 1e-9))
        with self.assertRaises(cn.nl.Refusal):
            cn.null_at_T(bad, self.bands, self.minos_x, self.w, n_mc=1000)

    def test_wrong_universe_counts_refuse(self):
        bands = dict(self.bands, MaRES=self.bands["MaRES"][:1])
        with self.assertRaises(c.Refusal):
            cn.laws_at_T(bands, self.minos_x, self.w)
        with self.assertRaises(c.Refusal):
            cn.null_at_T(dict(self.blocks, C_T=np.eye(10)), self.bands, self.minos_x, self.w, n_mc=10)


if __name__ == "__main__":
    unittest.main()
