"""The one-time gather, and the key that keeps it honest."""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import frozen_design as fd
import prematerialize_theirs as pre


class CacheKey(unittest.TestCase):
    BASE = dict(inputs_npz=Path("/x/G2.npz"), subsample_seed=0,
                max_events=4_000_000, split_seed=20260920,
                half_size=2_000_000, stage="final")

    def test_it_is_stable_across_calls(self):
        self.assertEqual(pre.cache_key(**self.BASE), pre.cache_key(**self.BASE))

    def test_every_row_determining_input_changes_it(self):
        base = pre.cache_key(**self.BASE)
        for field, other in (("subsample_seed", 1), ("max_events", 4_000_001),
                             ("split_seed", 7), ("half_size", 1_000_000),
                             ("stage", "pilot")):
            changed = dict(self.BASE)
            changed[field] = other
            self.assertNotEqual(pre.cache_key(**changed), base, msg=field)

    def test_the_estimator_seed_is_NOT_in_it(self):
        """It is the only thing that varies across the campaign; if it entered
        the key, every task would gather its own copy and the cache would buy
        nothing."""
        import inspect
        self.assertNotIn("estimator", inspect.signature(pre.cache_key).parameters)
        self.assertNotIn("seed_", str(inspect.signature(pre.cache_key)))


class Loading(unittest.TestCase):
    def _write(self, folder: Path, key: str) -> Path:
        path = folder / "cache.npz"
        np.savez(path, pdata_packed=np.ones((4, 33, 10), np.float32),
                 pdata_globals=np.ones((4, 16), np.float32),
                 prior_packed=np.ones((6, 33, 10), np.float32),
                 prior_globals=np.ones((6, 16), np.float32),
                 rows_a=np.arange(4), rows_b=np.arange(6),
                 s1_a=np.ones(4, bool), key=np.array(key))
        return path

    def test_a_matching_key_loads(self):
        with TemporaryDirectory() as tmp:
            key = pre.cache_key(**CacheKey.BASE)
            blob = pre.load(self._write(Path(tmp), key), expected_key=key)
            self.assertEqual(np.asarray(blob["pdata_packed"]).shape[0], 4)

    def test_a_cache_from_a_DIFFERENT_split_is_refused(self):
        """It would gather one run's rows into another run's legs."""
        with TemporaryDirectory() as tmp:
            other = dict(CacheKey.BASE, split_seed=7)
            path = self._write(Path(tmp), pre.cache_key(**other))
            with self.assertRaisesRegex(SystemExit, "different subsample"):
                pre.load(path, expected_key=pre.cache_key(**CacheKey.BASE))


class WhyItExists(unittest.TestCase):
    def test_the_frozen_inputs_the_rows_depend_on_do_not_vary_by_seed(self):
        """Every task gathers the same rows: that is what makes one gather
        enough. The subsample and the split are frozen; the seeds are not part
        of either."""
        self.assertEqual(fd.SPLITS["split_seed"], 20260920)
        seeds = set(fd.SEEDS["tuning"]) | set(fd.SEEDS["pilot"]) | set(fd.SEEDS["final"])
        self.assertGreater(len(seeds), 1)
        keys = {pre.cache_key(**CacheKey.BASE) for _ in seeds}
        self.assertEqual(len(keys), 1)


if __name__ == "__main__":
    unittest.main()
