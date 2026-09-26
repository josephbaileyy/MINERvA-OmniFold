"""Controls for s5p_validate: correctly sized Gaussian errors pass T4/T5, an understated sigma fails T5 in the
direction it acts, a bias beyond the bounded component fails T4, and a missing experiment is INCOMPLETE."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_validate as sv  # noqa: E402

N = 65856


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="s5p-val-"))
        U = np.zeros((3, N))
        U[0, :10], U[1, 10:20], U[2, :20] = 1.0, 1.0, 1.0
        self.U = U
        self.truth = np.ones(N)
        f = U @ self.truth
        rel_ns = 0.01
        np.savez(self.tmp / "asm.npz", U=U, f=f, C_prob=np.diag((rel_ns * f) ** 2 + (0.02 * f) ** 2),
                 C_stat=np.diag((0.02 * f) ** 2), h=0.0 * f, meta=json.dumps({"functional_names": ["a", "b", "total"]}))

    def experiments(self, name, n, rel_err, bias=0.0, seed=0):
        d = self.tmp / name
        d.mkdir()
        rng = np.random.default_rng(seed)
        for i in range(n):
            # one common relative fluctuation per functional block
            e = np.ones(N) * (1 + bias)
            e[:10] *= 1 + rel_err * rng.normal()
            e[10:20] *= 1 + rel_err * rng.normal()
            np.savez(d / f"e{i}.npz", xsec_flat=e, xtrue_flat=self.truth)
        return str(d / "*.npz")

    def design(self, points, s_stat=0.02):
        return {"assembly": str(self.tmp / "asm.npz"), "sigma_stat_rel": [s_stat, s_stat, s_stat / np.sqrt(2)],
                "alpha_family": 0.05, "points": points}

    def test_correct_sigma_passes_and_understated_fails_T5(self):
        g = self.experiments("nom", 400, 0.02)
        res = sv.evaluate(self.design([{"name": "nom", "glob": g, "n": 400, "statistical_check": True}]))
        self.assertTrue(res["points"][0]["T5"]["pass"])
        res = sv.evaluate(self.design([{"name": "nom", "glob": g, "n": 400, "statistical_check": True}], s_stat=0.012))
        self.assertFalse(res["points"][0]["T5"]["pass"])

    def test_bias_beyond_the_interval_fails_T4(self):
        g = self.experiments("biased", 200, 0.005, bias=0.08)
        res = sv.evaluate(self.design([{"name": "b", "glob": g, "n": 200}]))
        self.assertFalse(res["points"][0]["T4_pass"])

    def test_missing_experiment_is_incomplete(self):
        g = self.experiments("few", 10, 0.02)
        self.assertEqual(sv.evaluate(self.design([{"name": "f", "glob": g, "n": 11}]))["verdict"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
