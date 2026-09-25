"""Clopper-Pearson helpers of s5c_samplesize against textbook values and brute force."""
import sys
import unittest
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5c_samplesize as ss  # noqa: E402


class CP(unittest.TestCase):
    def test_zero_successes_upper_is_rule_of_three(self):
        # one-sided 95% upper bound with 0/n is 1 - 0.05**(1/n) ~ 3/n
        self.assertAlmostEqual(ss.cp_upper(0, 1000, 0.05), 1 - 0.05 ** (1 / 1000), places=10)

    def test_all_successes_lower(self):
        self.assertAlmostEqual(ss.cp_lower(100, 100, 0.05), 0.05 ** (1 / 100), places=10)

    def test_min_k_by_brute_force(self):
        n, thr, a = 500, 0.66, 0.01
        k = ss.min_k_lower_above(n, thr, a)
        self.assertGreater(ss.cp_lower(k, n, a), thr)
        self.assertLessEqual(ss.cp_lower(k - 1, n, a), thr)

    def test_max_k_by_brute_force(self):
        n, thr, a = 5000, 0.06, 0.05
        k = ss.max_k_upper_below(n, thr, a)
        self.assertLessEqual(ss.cp_upper(k, n, a), thr)
        self.assertGreater(ss.cp_upper(k + 1, n, a), thr)

    def test_assurance_rises_with_n(self):
        lo = ss.coverage_assurance(500, 0.6827, 0.66, 10)["assurance_lower_bound"]
        hi = ss.coverage_assurance(20000, 0.6827, 0.66, 10)["assurance_lower_bound"]
        self.assertLess(lo, hi)


if __name__ == "__main__":
    unittest.main()
