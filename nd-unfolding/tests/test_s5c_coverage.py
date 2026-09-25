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

    def test_functional_count(self):
        U, names = sc.reported_functionals({"measurement": {"partition_J": J}})
        self.assertEqual(U.shape[0], 43 + 3 + 1)
        self.assertEqual(names[-1], "total_integrated")


if __name__ == "__main__":
    unittest.main()
