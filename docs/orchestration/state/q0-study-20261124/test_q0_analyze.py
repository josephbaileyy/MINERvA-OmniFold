#!/usr/bin/env python3
"""Tests of q0_analyze.py: the weighted statistics, the coarse grid's merge rule, the readings' structure, and the refusals.

    python3 -m unittest docs/orchestration/state/q0-study-20261124/test_q0_analyze.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import q0_analyze as A  # noqa: E402


class Weighted(unittest.TestCase):
    def test_unit_weights_match_the_standard_statistics(self):
        rng = np.random.default_rng(0)
        x, y = rng.normal(size=500), rng.normal(size=500)
        y = y + 0.5 * x
        w = np.ones(500)
        self.assertAlmostEqual(A.wpearson(x, y, w), np.corrcoef(x, y)[0, 1], places=12)
        self.assertAlmostEqual(A.wspearman(x, y, w), stats.spearmanr(x, y)[0], places=12)

    def test_integer_weights_equal_replication(self):
        rng = np.random.default_rng(1)
        x, y = rng.normal(size=50), rng.normal(size=50)
        k = rng.integers(1, 4, 50)
        xr, yr = np.repeat(x, k), np.repeat(y, k)
        self.assertAlmostEqual(A.wpearson(x, y, k.astype(float)), np.corrcoef(xr, yr)[0, 1], places=12)
        self.assertAlmostEqual(A.wspearman(x, y, k.astype(float)), stats.spearmanr(xr, yr)[0], places=12)

    def test_weighted_quantile(self):
        x = np.arange(1.0, 101.0)
        self.assertAlmostEqual(A.wquantile(x, np.ones(100), [0.5])[0], 50.5)
        q = A.wquantile(np.array([0.0, 10.0]), np.array([3.0, 1.0]), [0.375, 0.875])
        self.assertAlmostEqual(q[0], 0.0)
        self.assertAlmostEqual(q[1], 10.0)

    def test_ties_get_mid_ranks(self):
        r = A.wrank(np.array([1.0, 1.0, 2.0]), np.array([1.0, 1.0, 2.0]))
        np.testing.assert_allclose(r, [1.0, 1.0, 3.0])


class Grid(unittest.TestCase):
    def rows(self, counts: dict):
        """counts {(ip, iz): n} -> pt, pz arrays at the cell centres."""
        pt, pz = [], []
        for (ip, iz), n in counts.items():
            pt += [0.5 * (A.PT_C[ip] + A.PT_C[ip + 1])] * n
            pz += [0.5 * (A.PZ_C[iz] + A.PZ_C[iz + 1])] * n
        return np.array(pt), np.array(pz)

    def test_no_merge_when_every_cell_is_full(self):
        with mock.patch.object(A, "MERGE_MIN", 2):
            pt, pz = self.rows({(i, j): 3 for i in range(6) for j in range(6)})
            cell, names = A.coarse_cells(pt, pz, np.ones(pt.size, bool))
        self.assertEqual(len(names), 36)

    def test_sparse_cell_merges_into_its_lower_pt_neighbour(self):
        with mock.patch.object(A, "MERGE_MIN", 10):
            c = {(i, 0): 20 for i in range(6)}
            c[(3, 0)] = 2
            c.update({(i, j): 20 for i in range(6) for j in range(1, 6)})
            pt, pz = self.rows(c)
            cell, names = A.coarse_cells(pt, pz, np.ones(pt.size, bool))
        merged = [v for v in names.values() if len(v["members"]) > 1]
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["pt"], [A.PT_C[2], A.PT_C[4]])
        self.assertEqual(merged[0]["n_eligible"], 22)

    def test_lowest_pt_cell_merges_upward_and_chains_repeat(self):
        with mock.patch.object(A, "MERGE_MIN", 10):
            c = {(i, j): 20 for i in range(6) for j in range(6)}
            c[(0, 2)] = 1
            c[(1, 2)] = 1                      # 1 + 1 still < 10: the chain continues into (2, 2)
            pt, pz = self.rows(c)
            cell, names = A.coarse_cells(pt, pz, np.ones(pt.size, bool))
        row2 = [v for v in names.values() if v["pz"] == [A.PZ_C[2], A.PZ_C[3]]]
        self.assertEqual(sorted(len(v["members"]) for v in row2), [1, 1, 1, 3])
        self.assertTrue(all(v["n_eligible"] >= 10 for v in names.values()))

    def test_outside_rows_are_minus_one(self):
        cell, _ = A.coarse_cells(np.array([5.0, 0.1]), np.array([2.0, 70.0]), np.ones(2, bool))
        self.assertEqual(cell.tolist(), [-1, -1])


def fake(n=20000, seed=2):
    rng = np.random.default_rng(seed)
    pt, pz = rng.uniform(0.05, 1.4, n), rng.uniform(1.6, 15, n)
    q0 = rng.gamma(2.0, 0.3, n)
    ea = 0.7 * q0 + rng.normal(0, 0.05, n)
    q3 = np.sqrt(pt ** 2 + (0.3 * q0) ** 2) + q0 + rng.normal(0, 0.02, n)
    W = 0.94 + 0.8 * q0 - 0.1 * pt + rng.normal(0, 0.02, n)
    W[:10] = np.nan
    st = np.zeros(n, np.int8)
    st[10:13] = 2
    return {"pt": pt, "pz": pz, "eavail": ea, "q0": q0, "w_reco": rng.uniform(0.5, 1.5, n), "q3_true": q3, "W_true": W,
            "q0_status": st, "q3": q3, "W": W, "in_truth_ps": np.ones(n, np.int8)}


class Readings(unittest.TestCase):
    def test_structure_and_that_q0_helps_when_it_should(self):
        with mock.patch.object(A, "MERGE_MIN", 500):
            r = A.readings(fake(), n_fit=6000, n_score=6000, hgb=dict(A.HGB, max_iter=60))
        self.assertEqual(set(r), {"n_rows", "R4", "excluded_R1_R2", "cells", "R1", "R2", "R3"})
        self.assertGreater(r["R1"]["overall"]["pearson"], 0.9)
        self.assertEqual(len(r["R2"]), 7)
        self.assertAlmostEqual(r["R4"]["frac_status_2_unweighted"], 3 / 20000)
        for t in ("q3_true", "W_true"):
            o = r["R3"][t]["by_group"]["overall"]
            self.assertLess(o["ratio_B_over_A"]["rms"], 1.0)    # q0 carries information E_avail lacks here
            self.assertEqual(r["R3"][t]["n_fit"], 6000)
        self.assertEqual(r["R3"]["W_true"]["n_excluded_nonfinite_target"], 10)
        txt = A.render(r)
        self.assertIn("R3  W_true", txt)

    def test_deterministic(self):
        kw = dict(n_fit=3000, n_score=3000, hgb=dict(A.HGB, max_iter=20))
        with mock.patch.object(A, "MERGE_MIN", 500):
            a, b = A.readings(fake(), **kw), A.readings(fake(), **kw)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


class Refusals(unittest.TestCase):
    def test_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            npz = Path(d) / "x.npz"
            np.savez(npz, **fake(100))
            self.assertEqual(A.main(["--npz", str(npz), "--out", d]), 9)                          # out exists
            self.assertEqual(A.main(["--npz", str(npz), "--out", str(Path(d) / "o")]), 9)        # sha
            with mock.patch.object(A, "NPZ_SHA", __import__("hashlib").sha256(npz.read_bytes()).hexdigest()), \
                    mock.patch.dict("os.environ", {"OMP_NUM_THREADS": "1"}):
                self.assertEqual(A.main(["--npz", str(npz), "--out", str(Path(d) / "o")]), 9)    # threads


if __name__ == "__main__":
    unittest.main()
