"""Tests of the pool assignment the builder actually runs (``build_pools.assign_pools``)."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pools as bp  # noqa: E402


def _fixture(n=20000, seed=3):
    rng = np.random.default_rng(seed)
    identity = np.column_stack([np.full(n, 110000), rng.integers(1, 50, n), np.arange(n)]).astype(np.int32)
    keys = identity[:, 2].astype(np.uint64) + (identity[:, 1].astype(np.uint64) << np.uint64(32))
    pass_truth = rng.random(n) > 0.02
    excluded = rng.choice(n, size=500, replace=False)
    return identity, keys, pass_truth, excluded


class AssignPools(unittest.TestCase):
    def test_deterministic_disjoint_covering_and_excluding(self):
        identity, keys, pass_truth, excluded = _fixture()
        seed = bp.pool_seed(bp.SALT)
        a = bp.assign_pools(identity, keys, pass_truth, excluded, seed)
        b = bp.assign_pools(identity, keys, pass_truth, excluded, seed)
        np.testing.assert_array_equal(a, b)
        eligible = pass_truth.copy()
        eligible[excluded] = False
        np.testing.assert_array_equal(a >= 0, eligible)          # covers exactly the eligible rows
        self.assertTrue(np.all(a[excluded] == -1))               # exclusion honoured
        self.assertTrue(set(np.unique(a[a >= 0])) <= {0, 1, 2, 3, 4})

    def test_fractions_within_four_sigma(self):
        identity, keys, pass_truth, excluded = _fixture(n=200000)
        codes = bp.assign_pools(identity, keys, pass_truth, excluded, bp.pool_seed(bp.SALT))
        n = int(np.sum(codes >= 0))
        for _, code, lo, hi in bp.POOLS:
            p = hi - lo
            self.assertLessEqual(abs(np.sum(codes == code) - n * p), 4 * np.sqrt(n * p * (1 - p)))

    def test_assignment_depends_on_identity_not_row_order(self):
        identity, keys, pass_truth, excluded = _fixture()
        seed = bp.pool_seed(bp.SALT)
        a = bp.assign_pools(identity, keys, pass_truth, excluded, seed)
        perm = np.random.default_rng(9).permutation(len(identity))
        inv = np.argsort(perm)
        b = bp.assign_pools(identity[perm], keys[perm], pass_truth[perm], inv[excluded], seed)
        np.testing.assert_array_equal(a, b[inv])

    def test_duplicate_identity_is_refused(self):
        identity, keys, pass_truth, excluded = _fixture()
        keys = keys.copy()
        eligible = np.flatnonzero(pass_truth & ~np.isin(np.arange(len(keys)), excluded))
        keys[eligible[1]] = keys[eligible[0]]
        with self.assertRaises(SystemExit):
            bp.assign_pools(identity, keys, pass_truth, excluded, bp.pool_seed(bp.SALT))

    def test_other_salt_gives_other_pools(self):
        identity, keys, pass_truth, excluded = _fixture()
        a = bp.assign_pools(identity, keys, pass_truth, excluded, bp.pool_seed(bp.SALT))
        b = bp.assign_pools(identity, keys, pass_truth, excluded, bp.pool_seed(b"another-salt"))
        self.assertGreater(np.mean(a[a >= 0] != b[b >= 0]), 0.3)


if __name__ == "__main__":
    unittest.main()
