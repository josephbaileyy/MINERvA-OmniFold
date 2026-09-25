"""Controls for s5c_coverage: known-coverage synthetic experiments, the complete-population rule."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5c_coverage as sc  # noqa: E402

J = {"edges": {"pt": [0.0, 0.55, 4.5], "pz": [1.5, 6.0, 60.0], "eavail": [0.0, 0.4, 100.0],
               "q3": [0.0, 1.2, 100.0], "W": [0.0, 1.4, 100.0]}, "supported_cells": [0, 5, 31]}


def contract(n_exp, width):
    return {"measurement": {"partition_J": J},
            "coverage": {"sigma": {"bootstrap_seeds": [1, 400]},
                         "gate": {"lcb68_threshold": 0.66, "lcb95_threshold": 0.94},
                         "grid": [{"truth": "nominal", "amplitude": 0.0, "validation_seeds": [1000, 1000 + n_exp - 1]}]}}


class Coverage(unittest.TestCase):
    def build(self, n_exp, inflate, drop=None):
        tmp = Path(tempfile.mkdtemp())
        rng = np.random.default_rng(0)
        n = 65856
        truth = rng.uniform(1.0, 2.0, n)
        scale = 0.01
        (tmp / "boot").mkdir(); (tmp / "exp").mkdir()
        for b in range(1, 401):
            np.savez(tmp / "boot" / f"boot_b{b}.npz", xsec_flat=truth + scale * rng.standard_normal(n))
        for s in range(1000, 1000 + n_exp):
            if s == drop:
                continue
            np.savez(tmp / "exp" / f"nominal_a0_s{s}.npz",
                     xsec_flat=truth + inflate * scale * rng.standard_normal(n), xtrue_flat=truth)
        c = tmp / "c.json"
        c.write_text(json.dumps(contract(n_exp, scale)))
        return tmp, c

    def score(self, tmp, c):
        out = tmp / "out.json"
        rc = sc.main(["--contract", str(c), "--experiments", str(tmp / "exp"), "--bootstrap", str(tmp / "boot"),
                      "--out", str(out)])
        return rc, json.loads(out.read_text())

    def test_conservative_intervals_pass_and_undercovering_fail(self):
        tmp, c = self.build(1500, inflate=0.8)   # true 68% coverage ~0.79
        rc, res = self.score(tmp, c)
        self.assertEqual((rc, res["verdict"]), (0, "PASS"))
        tmp, c = self.build(1500, inflate=1.3)   # true 68% coverage ~0.56
        rc, res = self.score(tmp, c)
        self.assertEqual((rc, res["verdict"]), (1, "FAIL"))

    def test_missing_experiment_is_incomplete_not_dropped(self):
        tmp, c = self.build(300, inflate=0.8, drop=1100)
        rc, res = self.score(tmp, c)
        self.assertEqual((rc, res["verdict"]), (4, "INCOMPLETE"))
        self.assertEqual(res["grid"][0]["missing"], [1100])

    def test_interim_futility_fires_on_gross_undercoverage_and_not_on_good(self):
        tmp, c = self.build(400, inflate=3.0)   # true 68% coverage ~0.26
        rc = sc.main(["--contract", str(c), "--experiments", str(tmp / "exp"), "--bootstrap", str(tmp / "boot"),
                      "--interim", "400", "--out", str(tmp / "i.json")])
        self.assertEqual(json.loads((tmp / "i.json").read_text())["verdict"], "FUTILITY-FAIL")
        tmp, c = self.build(400, inflate=0.8)
        sc.main(["--contract", str(c), "--experiments", str(tmp / "exp"), "--bootstrap", str(tmp / "boot"),
                 "--interim", "400", "--out", str(tmp / "i.json")])
        self.assertEqual(json.loads((tmp / "i.json").read_text())["verdict"], "CONTINUE")

    def test_bias_allowance_widens_intervals(self):
        tmp, c = self.build(300, inflate=1.3)
        U, names = sc.reported_functionals({"measurement": {"partition_J": J}})
        ba = tmp / "ba.json"
        ba.write_text(json.dumps({"functional_names": names, "b_rel": [0.05] * len(names)}))
        rc = sc.main(["--contract", str(c), "--experiments", str(tmp / "exp"), "--bootstrap", str(tmp / "boot"),
                      "--bias-allowance", str(ba), "--out", str(tmp / "o.json")])
        self.assertEqual(json.loads((tmp / "o.json").read_text())["verdict"], "PASS")

    def build_biased(self, n_exp, rel_bias):
        """Conservative-width experiments (true 68% coverage ~0.79 unbiased) with every cell scaled
        by (1 + rel_bias): a known multiplicative bias."""
        tmp, c = self.build(n_exp, inflate=0.8)
        for f in (tmp / "exp").glob("*.npz"):
            z = dict(np.load(f))
            np.savez(f, xsec_flat=z["xsec_flat"] * (1 + rel_bias), xtrue_flat=z["xtrue_flat"])
        return tmp, c

    def correct(self, tmp, c, beta, se):
        U, names = sc.reported_functionals({"measurement": {"partition_J": J}})
        bc = tmp / "bc.json"
        bc.write_text(json.dumps({"functional_names": names, "beta": [beta] * len(names), "se": [se] * len(names)}))
        sc.main(["--contract", str(c), "--experiments", str(tmp / "exp"), "--bootstrap", str(tmp / "boot"),
                 "--bias-correction", str(bc), "--out", str(tmp / "o.json")])
        return json.loads((tmp / "o.json").read_text())

    def test_bias_correction_repairs_a_known_bias_and_keeps_widths(self):
        tmp, c = self.build_biased(600, 0.04)
        rc, res = self.score(tmp, c)
        self.assertEqual(res["verdict"], "FAIL")             # uncorrected: the bias undercovers
        res = self.correct(tmp, c, 0.04, 0.0)
        self.assertEqual(res["verdict"], "PASS")
        self.assertAlmostEqual(res["grid"][0]["median_halfwidth68_over_sigma"], 1.0, places=6)

    def test_a_wrong_bias_correction_still_fails(self):
        tmp, c = self.build_biased(600, 0.04)
        self.assertEqual(self.correct(tmp, c, -0.04, 0.0)["verdict"], "FAIL")

    def test_zero_correction_reproduces_the_frozen_construction(self):
        tmp, c = self.build(300, inflate=1.0)
        rc, frozen = self.score(tmp, c)
        res = self.correct(tmp, c, 0.0, 0.0)
        self.assertEqual(res["grid"][0]["hits68"], frozen["grid"][0]["hits68"])
        self.assertEqual(res["grid"][0]["hits95"], frozen["grid"][0]["hits95"])

    def test_allowance_and_correction_are_exclusive(self):
        tmp, c = self.build(10, inflate=1.0)
        with self.assertRaises(SystemExit):
            sc.main(["--contract", str(c), "--experiments", str(tmp / "exp"), "--bootstrap", str(tmp / "boot"),
                     "--bias-allowance", "a", "--bias-correction", "b", "--out", str(tmp / "o.json")])

    def test_functional_count(self):
        U, names = sc.reported_functionals({"measurement": {"partition_J": J}})
        self.assertEqual(U.shape[0], 43 + 3 + 1)
        self.assertEqual(names[-1], "total_integrated")


if __name__ == "__main__":
    unittest.main()
