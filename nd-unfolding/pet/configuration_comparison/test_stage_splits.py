"""The stage split: disjoint, covering, stable, and independent of the dump."""
from __future__ import annotations

import unittest

import numpy as np

import frozen_design as fd
import stage_splits as ss


def identities(n=60000, seed=0):
    rng = np.random.default_rng(seed)
    return np.stack([rng.integers(110000, 110500, n),
                     rng.integers(0, 500, n),
                     rng.integers(0, 1300, n)], axis=1)


class Partition(unittest.TestCase):
    def setUp(self):
        self.ident = identities()

    def test_the_three_stages_are_disjoint_and_cover_everything(self):
        rows = {s: set(ss.rows_for_stage(self.ident, s).tolist())
                for s in ss.STAGES}
        self.assertEqual(sum(len(v) for v in rows.values()), self.ident.shape[0])
        for a in ss.STAGES:
            for b in ss.STAGES:
                if a < b:
                    self.assertEqual(rows[a] & rows[b], set(), msg=f"{a}/{b}")

    def test_the_observed_fractions_track_the_frozen_ones(self):
        got = ss.census(self.ident)["fractions_observed"]
        for stage, want in fd.SPLITS["fractions"].items():
            self.assertAlmostEqual(got[stage], want, places=2, msg=stage)

    def test_the_same_event_always_lands_in_the_same_stage(self):
        first = ss.assign(self.ident)
        shuffled = np.random.default_rng(9).permutation(self.ident.shape[0])
        again = ss.assign(self.ident[shuffled])
        np.testing.assert_array_equal(again, first[shuffled])

    def test_adding_events_does_not_move_the_existing_ones(self):
        """A seeded permutation would move every assignment; a per-event hash
        does not. That is why this is a hash."""
        before = ss.assign(self.ident)
        grown = np.concatenate([self.ident, identities(5000, seed=77)])
        after = ss.assign(grown)[: self.ident.shape[0]]
        np.testing.assert_array_equal(after, before)

    def test_it_is_the_identity_and_not_the_row_number(self):
        """A regenerated dump reorders rows; the split must not follow."""
        order = np.random.default_rng(3).permutation(self.ident.shape[0])
        by_identity = dict(zip(map(tuple, self.ident.tolist()),
                               ss.assign(self.ident)))
        reordered = self.ident[order]
        for ident, stage in zip(map(tuple, reordered.tolist()),
                                ss.assign(reordered)):
            self.assertEqual(stage, by_identity[ident])

    def test_a_different_seed_gives_a_different_split(self):
        self.assertFalse(np.array_equal(ss.assign(self.ident, seed=1),
                                        ss.assign(self.ident, seed=2)))

    def test_the_split_is_reproducible_across_processes(self):
        """`hash()` is salted per process; this must not be."""
        import subprocess
        import sys
        code = (
            "import numpy as np, stage_splits as ss;"
            "rng=np.random.default_rng(0);"
            "i=np.stack([rng.integers(110000,110500,1000),"
            "rng.integers(0,500,1000),rng.integers(0,1300,1000)],axis=1);"
            "print(ss.assign(i)[:20].tolist())")
        runs = {subprocess.run([sys.executable, "-c", code], cwd=__file__.rsplit("/", 1)[0],
                               capture_output=True, text=True).stdout
                for _ in range(2)}
        self.assertEqual(len(runs), 1)
        self.assertTrue(next(iter(runs)).strip())


class Sizing(unittest.TestCase):
    def test_each_stage_reports_the_half_it_can_support(self):
        ident = identities(100000)
        halves = {s: ss.usable_half_size(ident, s) for s in ss.STAGES}
        self.assertLess(halves["tuning"], halves["final"])
        for stage, half in halves.items():
            self.assertLessEqual(2 * half,
                                 ss.rows_for_stage(ident, stage).size)

    def test_an_unknown_stage_is_refused(self):
        with self.assertRaisesRegex(ValueError, "unknown stage"):
            ss.rows_for_stage(identities(100), "validation")


if __name__ == "__main__":
    unittest.main()
