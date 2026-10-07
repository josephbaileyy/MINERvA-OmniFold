"""The standalone replay's restated rules equal the frozen ones on random inputs.

Run from the repository root: ``python3 -m unittest publication/release/test_replay_inference.py``. It imports the
frozen ``nd-unfolding/s5p_inference.py`` and ``s5p_joint.py`` of THIS checkout (checked by path) and the replay
module, and compares statistics, p-values, Holm-with-determinacy and power, including ties and the
undetermined/not-rejected branches. The end-to-end check (variant assembly and claim rule) is the replay's
``--compare`` against the frozen ``joint-evaluate.json`` on the real extracted inputs.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ND = ROOT / "nd-unfolding"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(ND))
si = _load("s5p_inference", ND / "s5p_inference.py")
sys.modules["s5p_inference"] = si
import s5p_joint as sj  # noqa: E402  (imports s5p_inference and s5p_stage1_inspect from ND)

rp = _load("replay_inference", Path(__file__).resolve().parent / "replay_inference.py")


class FrozenModules(unittest.TestCase):
    def test_frozen_modules_come_from_this_checkout(self):
        self.assertEqual(Path(sj.__file__).resolve().parent, ND)
        self.assertEqual(Path(si.__file__).resolve().parent, ND)


class Equivalence(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(20261006)
        n = 12
        A = self.rng.normal(size=(n, n))
        self.V = A @ A.T + n * np.eye(n)
        self.mu = self.rng.uniform(5, 10, n)
        self.var = self.rng.uniform(0.01, 0.1, n)
        self.F = self.mu + self.rng.normal(size=(40, n))
        self.seeds = self.rng.integers(10**6, 2 * 10**6, size=40)
        self.dom = np.ones(n, bool)
        self.dom[-3:] = False

    def test_statistics_bitwise(self):
        for draw, seed0 in ((True, 1780000), (False, 0)):
            a = sj.statistics(self.F, self.mu, self.var, self.V, self.dom, seed0, draw=draw, seeds=self.seeds)
            b = rp.statistics(self.F, self.mu, self.var, self.V, self.dom, seed0, draw=draw, seeds=self.seeds)
            for x, y in zip(a, b):
                np.testing.assert_array_equal(x, y)

    def test_mc_pvalue_including_ties(self):
        t_null = np.round(self.rng.normal(size=500), 1)
        for t_obs in (-5.0, 0.0, 0.3, 1.0, 3.5, 10.0):
            a, b = si.mc_pvalue(t_obs, t_null), rp.mc_pvalue(t_obs, t_null)
            self.assertEqual((a["p"], a["k"], a["B"]), (b["p"], b["k"], b["B"]))
            self.assertEqual(a["tail_interval"], b["tail_interval"])

    def test_holm_determined_all_branches(self):
        cases = [
            {f"t{i}": {"p": 1 / 1352, "k": 0, "B": 1351} for i in range(10)},  # all rejected
            {"a": {"p": 1 / 1352, "k": 0, "B": 1351}, "b": {"p": 0.3, "k": 300, "B": 999},
             "c": {"p": 0.5, "k": 500, "B": 999}},  # not rejected stops the procedure
            {"a": {"p": 0.02, "k": 4, "B": 199}, "b": {"p": 0.9, "k": 180, "B": 199}},  # undetermined
        ]
        for c in cases:
            a, b = si.holm_determined(c, 0.05), rp.holm_determined(c, 0.05)
            self.assertEqual({k: (v["decision"], v["threshold"], v["interval"]) for k, v in a.items()},
                             {k: (v["decision"], v["threshold"], v["interval"]) for k, v in b.items()})

    def test_power_determined(self):
        nulls = [self.rng.normal(size=300) + s for s in (0.0, 0.2, -0.1)]
        alt = self.rng.normal(size=150) + 2.5
        for al in (0.05, 0.005):
            a, b = si.power_determined(alt, nulls, al), rp.power_determined(alt, nulls, al)
            self.assertEqual((a["power"], a["n"], a["B"]), (b["power"], b["n"], b["B"]))


if __name__ == "__main__":
    unittest.main()
