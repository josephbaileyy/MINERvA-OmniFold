"""Tests for covfix_b_threshold_sim (COVFIX rev 12 §4.5).

  python3 -B -m unittest -v test_covfix_b_threshold_sim.py
"""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
from scipy.stats import binom, chi2

import covfix_b_threshold_sim as sim


def write_cov(d: Path, k: np.ndarray, names=None) -> str:
    names = names or [f"R{i:02d}" for i in range(k.shape[0])]
    p = d / "cov.csv"
    lines = ["cell," + ",".join(names)] + [n + "," + ",".join(repr(float(v)) for v in row) for n, row in zip(names, k)]
    p.write_text("\n".join(lines) + "\n")
    return str(p)


class Exact(unittest.TestCase):
    def test_veto_and_deficit_counts_at_k16(self):
        self.assertEqual((sim.veto_count(16, 3), sim.veto_count(16, 2)), (179, 180))
        self.assertEqual((sim.deficit_bound(16, 3), sim.deficit_bound(16, 2)), (153, 154))

    def test_veto_count_is_the_exact_tail_edge(self):
        for k, t in ((16, 3), (5, 2), (1, 3)):
            c, a = sim.veto_count(k, t), 0.05 / (k * t)
            self.assertLessEqual(binom.cdf(c, 300, 0.6827), a)
            self.assertGreater(binom.cdf(c + 1, 300, 0.6827), a)

    def test_scale_gives_the_declared_joint_coverage(self):
        for k in (1, 4, 16):
            self.assertAlmostEqual(sim.scale_for(0.6827, k), 1.0)
            s = sim.scale_for(0.60, k)
            self.assertAlmostEqual(chi2.cdf(chi2.ppf(0.6827, k) / s ** 2, k), 0.60, places=9)


class Model(unittest.TestCase):
    def test_k1_pass_rate_matches_the_binomial(self):
        """k = 1: the joint and the cell reading coincide up to q = chi2_1(0.6827) vs 1."""
        rng = np.random.default_rng(1)
        p, se = sim.pass_rate(np.eye(1), 2, 0.6827, 4000, rng)
        veto = sim.veto_count(1, 2)
        exact = binom.sf(max(184, veto), 300, 0.6827) ** 2
        self.assertLess(abs(p - exact), 5 * se + 0.01)

    def test_independent_cells_pass_less_than_one_cell(self):
        rng = np.random.default_rng(2)
        p1, _ = sim.pass_rate(np.eye(1), 3, 0.6827, 2000, rng)
        p8, _ = sim.pass_rate(np.eye(8), 3, 0.6827, 2000, rng)
        self.assertLess(p8, p1)

    def test_main_reads_symmetrizes_and_selects(self):
        with tempfile.TemporaryDirectory() as td:
            k = np.array([[4.0, 1.0, 0.0], [1.0 + 1e-12, 9.0, 0.5], [0.0, 0.5, 1.0]])
            path = write_cov(Path(td), k)
            names, kk = sim.load_cov(path)
            self.assertTrue(np.array_equal(kk, kk.T))
            buf = io.StringIO()
            with redirect_stdout(buf):
                sim.main(["--cov", path, "--cells", "R00,R02", "--truths", "2", "--replicas", "200"])
            out = json.loads(buf.getvalue())
            self.assertEqual((out["cells"], out["k"], out["every_cell_needs"]), (["R00", "R02"], 2,
                                                                                 sim.veto_count(2, 2) + 1))
            buf = io.StringIO()
            with redirect_stdout(buf):
                sim.main(["--cov", path, "--cells", "none", "--truths", "3"])
            self.assertEqual(json.loads(buf.getvalue())["result"], "no measured-set test")
            for bad in ("R00,R00", "R09", ""):
                with self.subTest(bad=bad), self.assertRaises(SystemExit):
                    sim.main(["--cov", path, "--cells", bad, "--truths", "2", "--replicas", "10"])


if __name__ == "__main__":
    unittest.main()
