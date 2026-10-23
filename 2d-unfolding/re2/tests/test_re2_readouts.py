"""Tests for the RE-2 J0 readouts ``re2_k1.py`` and ``re2_units.py`` (synthetic files; PyROOT and numpy):
    PYTHONPATH=$(root-config --libdir) python3.13 -m unittest 2d-unfolding/re2/tests/test_re2_readouts.py -v
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))

try:
    import ROOT
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False

if HAVE_ROOT:
    import re2_k1 as K
import re2_units as U


def root_xsec(path: Path, x: np.ndarray, refinement: dict | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    f = ROOT.TFile.Open(str(path), "RECREATE")
    h = ROOT.TH2D("hXSec2D", "", 14, 0, 14, 16, 0, 16)
    for i in range(14):
        for j in range(16):
            h.SetBinContent(i + 1, j + 1, float(x[i, j]))
    h.Write()
    if refinement is not None:
        ROOT.TNamed("re2Refinement", json.dumps(refinement)).Write()
    f.Close()


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class K1(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        d = self.d = Path(self.td.name)
        rng = np.random.default_rng(1)
        self.eu = rng.uniform(1, 2, (14, 16))
        self.eu.ravel()[:19] = 0.0                       # 205 reported cells
        root_xsec(d / "eu.root", self.eu)
        self.good = {"params": {"random_state": 45, "n_estimators": 400, "num_leaves": 31},
                     "clipped_fraction": 0.0, "refined_over_signed": 1.0}
        root_xsec(d / "out" / "A" / "xsec.root", self.eu)
        root_xsec(d / "out" / "B" / "xsec.root", self.eu * (1 + 5e-9))
        root_xsec(d / "out" / "R" / "xsec.root", self.eu * 1.01, self.good)
        root_xsec(d / "ref.root", self.eu)
        (d / "runs.tsv").write_text("job\tlane\tlabel\tcpus\tscript\targs\n"
                                    "J0b\tb1\tA\t64\tre2\t--bkg-mode purity\n"
                                    "J0b\tb1\tB\t64\tre2\t--bkg-mode purity\n"
                                    "J0b\tb1\tR\t64\tre2\t--bkg-mode negweight-refined --refine-n-estimators 400\n")

    def tearDown(self):
        self.td.cleanup()

    def run_checks(self, rows: str) -> dict:
        (self.d / "checks.tsv").write_text("id\tkind\ttest\tref\tref_sha256\n" + rows)
        K.main(["--runs", str(self.d / "runs.tsv"), "--checks", str(self.d / "checks.tsv"), "--out-dir",
                str(self.d / "out"), "--eu", str(self.d / "eu.root"), "--expect-eu-sha256",
                K.sha256_path(self.d / "eu.root"), "--result", str(self.d / "k1.json")])
        return json.loads((self.d / "k1.json").read_text())

    def test_pass_fail_and_power(self):
        sha = K.sha256_path(self.d / "ref.root")
        r = self.run_checks(f"c1\tle\tA\t{self.d / 'ref.root'}\t{sha}\nc2\tle\tB\trun:A\t\n"
                            f"c3\tle\tR\trun:A\t\nc4\tdiffers\tR\trun:A\t\nc5\tdiffers\tA\t{self.d / 'ref.root'}\t\n")
        v = {c["id"]: c["verdict"] for c in r["checks"]}
        self.assertEqual(v, {"c1": "PASS", "c2": "PASS", "c3": "FAIL", "c4": "PASS", "c5": "FAIL"})
        self.assertTrue(r["checks"][0]["bitwise_224"])
        self.assertFalse(r["checks"][1]["bitwise_224"])
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual([h["verdict"] for h in r["health"]], ["PASS"])

    def test_wrong_reference_digest_fails(self):
        r = self.run_checks(f"c1\tle\tA\t{self.d / 'ref.root'}\t{'0' * 64}\n")
        self.assertEqual(r["checks"][0]["verdict"], "FAIL")

    def test_health_fails_on_clipping_or_size(self):
        root_xsec(self.d / "out" / "R" / "xsec.root", self.eu, dict(self.good, clipped_fraction=0.02))
        r = self.run_checks(f"c1\tle\tA\trun:A\t\n")
        self.assertEqual(r["health"][0]["verdict"], "FAIL")
        root_xsec(self.d / "out" / "R" / "xsec.root", self.eu,
                  dict(self.good, params={"random_state": 45, "n_estimators": 100, "num_leaves": 8}))
        r = self.run_checks(f"c1\tle\tA\trun:A\t\n")
        self.assertEqual(r["health"][0]["verdict"], "FAIL")


class Units(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.d = Path(self.td.name)
        labels = sorted({l for ls, _, _ in U.CLASSES.values() for l in ls})
        (self.d / "runs.tsv").write_text("job\tlane\tlabel\tcpus\tscript\targs\n" +
                                         "".join(f"J0\tx\t{l}\t64\tre2\t-\n" for l in labels))
        self.labels = labels

    def tearDown(self):
        self.td.cleanup()

    def verdict(self, seconds: dict) -> dict:
        (self.d / "steps.psv").write_text("".join(f"1.{i}|{l}|{seconds.get(l, 1000)}|64|COMPLETED\n"
                                                  for i, l in enumerate(self.labels)))
        U.main(["--runs", str(self.d / "runs.tsv"), "--steps", str(self.d / "steps.psv"),
                "--result", str(self.d / "u.json")])
        return json.loads((self.d / "u.json").read_text())

    def test_rule_branches(self):
        # 1000 s at 64 CPUs = 0.0694 node-h per run; core counts 3+175+10+300+80+37 = 605 -> 42.0, worst 52.5
        r = self.verdict({})
        self.assertAlmostEqual(r["core_projected"], 605 * 1000 * 64 / 256 / 3600, places=9)
        self.assertEqual(r["verdict"], "CORE AND DIAGNOSTICS within 90")
        r = self.verdict({l: 1800 for l in self.labels})            # core worst 94.5
        self.assertTrue(r["verdict"].startswith("RETURN TO DIRECTOR"))
        r = self.verdict({l: 1500 for l in self.labels})            # core worst 78.8, with diagnostics 98.0
        self.assertTrue(r["verdict"].startswith("CORE ONLY"))

    def test_unit_is_the_class_maximum_and_missing_steps_stop(self):
        r = self.verdict({"F_MaCCQE0": 3000})
        self.assertAlmostEqual(r["classes"]["universe"]["unit_node_h"], 3000 * 64 / 256 / 3600, places=12)
        (self.d / "steps.psv").write_text("1.0|D_cv|1000|64|COMPLETED\n")
        U.main(["--runs", str(self.d / "runs.tsv"), "--steps", str(self.d / "steps.psv"),
                "--result", str(self.d / "u.json")])
        self.assertTrue(json.loads((self.d / "u.json").read_text())["verdict"].startswith("INCOMPLETE"))


if __name__ == "__main__":
    unittest.main()
