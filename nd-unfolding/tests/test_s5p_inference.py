"""Controls for the s5p joint-test library: the shape statistic is invariant to the dropped cell and equals
the chi-square of normalized Gaussian residuals; Monte Carlo p-values are never 0 and the rank rule gives a
test of size <= alpha on exchangeable nulls; Besag-Clifford and Holm behave as defined."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_inference as si  # noqa: E402


class Tests(unittest.TestCase):
    def test_shape_statistic_is_invariant_to_the_dropped_cell(self):
        rng = np.random.default_rng(0)
        n = 6
        A = rng.normal(size=(n, n))
        V = A @ A.T + n * np.eye(n)
        mu = rng.uniform(1, 2, n)
        f = mu * (1 + 0.1 * rng.normal(size=n))
        vals = [si.stat_shape(f, mu, V, drop=d) for d in range(n)]
        np.testing.assert_allclose(vals, vals[0], rtol=1e-8)

    def test_pvalue_never_zero_and_rank_test_size(self):
        rng = np.random.default_rng(1)
        self.assertGreater(si.mc_pvalue(1e9, rng.normal(size=99))["p"], 0)
        rej = 0
        for _ in range(4000):
            x = rng.normal(size=20)
            rej += si.mc_pvalue(x[0], x[1:])["p"] <= 0.05
        self.assertLess(rej / 4000, 0.05 + 3 * np.sqrt(0.05 * 0.95 / 4000))

    def test_besag_clifford_stops_at_h(self):
        r = si.besag_clifford(0.5, iter([0.1, 0.9, 0.2, 0.8, 0.7]), h=2, n_max=10)
        self.assertEqual((r["stopped_at"], r["p"]), (4, 0.5))
        r = si.besag_clifford(5.0, iter([0.1] * 10), h=2, n_max=10)
        self.assertEqual(r["p"], 1 / 11)

    def test_holm(self):
        out = si.holm({"a": 0.001, "b": 0.02, "c": 0.04}, 0.05)
        self.assertTrue(all(out[k]["reject"] for k in "abc"))  # 0.001 <= 0.05/3, 0.02 <= 0.05/2, 0.04 <= 0.05/1
        out = si.holm({"a": 0.001, "b": 0.03, "c": 0.04}, 0.05)
        self.assertTrue(out["a"]["reject"])
        self.assertFalse(out["b"]["reject"] or out["c"]["reject"])  # 0.03 > 0.025 stops the procedure
        self.assertAlmostEqual(out["b"]["p_holm"], 0.06)

    def test_power_of_a_shifted_alternative(self):
        rng = np.random.default_rng(2)
        null = rng.chisquare(5, 999)
        alt = rng.chisquare(5, 400) + 15
        self.assertGreater(si.power(alt, null)["power"], 0.9)
        self.assertLess(si.size(rng.chisquare(5, 400), null, 0.05)["rejection_fraction"], 0.1)


class SequentialTests(unittest.TestCase):
    TH = sorted(set(si.holm_thresholds(0.05, 10)) | {0.01, 0.05})

    def test_bulk_p_stops_once_precise_and_not_before(self):
        # p ~ 0.5: the absolute half-width 0.05 at 99.5% needs B ~ 800
        self.assertFalse(si.sequential_decision(100, 200, self.TH)["stop"])
        d = si.sequential_decision(500, 1000, self.TH)
        self.assertTrue(d["stop"], d)

    def test_zero_exceedances_stop_only_below_every_threshold(self):
        self.assertFalse(si.sequential_decision(0, 200, self.TH)["stop"])  # 99.5% upper bound 0.026
        d = si.sequential_decision(0, 1200, self.TH)
        self.assertTrue(d["stop"], d)
        self.assertLess(d["look_interval"][1], 0.005)

    def test_a_straddled_threshold_never_stops(self):
        d = si.sequential_decision(100, 1999, self.TH)  # p ~ 0.05
        self.assertIn(0.05, d["straddled_thresholds"])
        self.assertFalse(d["stop"])

    def test_holm_thresholds(self):
        self.assertEqual(si.holm_thresholds(0.05, 2), [0.025, 0.05])
        self.assertAlmostEqual(min(si.holm_thresholds(0.05, 10)), 0.005)


class DeterminacyTests(unittest.TestCase):
    def test_holm_rejects_only_determined_steps_and_stops_on_undetermined(self):
        e = {"a": {"p": 1 / 2000, "k": 0, "B": 1999},     # interval [0, 0.0018] < 0.05/3: rejected
             "b": {"p": 51 / 2000, "k": 50, "B": 1999},   # ~0.025 vs 0.025: straddles -> undetermined
             "c": {"p": 0.5, "k": 999, "B": 1999}}
        d = si.holm_determined(e, 0.05)
        self.assertEqual(d["a"]["decision"], "rejected")
        self.assertEqual(d["b"]["decision"], "undetermined")
        self.assertEqual(d["c"]["decision"], "undetermined")  # the procedure stopped at b

    def test_holm_not_rejected_stops_the_procedure(self):
        e = {"a": {"p": 0.3, "k": 600, "B": 1999}, "b": {"p": 0.6, "k": 1200, "B": 1999}}
        d = si.holm_determined(e, 0.05)
        self.assertEqual({v["decision"] for v in d.values()}, {"not rejected"})

    def test_power_determined_is_stricter_than_the_rank_rule(self):
        rng = np.random.default_rng(12)
        null = rng.chisquare(10, 800)
        alt = rng.chisquare(10, 400) + 12.0
        rank = si.power(alt, null, 0.005)["power"]
        det = si.power_determined(alt, [null], 0.005)["power"]
        self.assertLessEqual(det, rank)
        self.assertGreater(rank, 0.0)
        # at B = 800 and alpha = 0.005 a rejection needs k = 0
        k = np.array([np.sum(null >= a) for a in alt])
        self.assertAlmostEqual(det, float(np.mean(k == 0)), places=12)


if __name__ == "__main__":
    unittest.main()
