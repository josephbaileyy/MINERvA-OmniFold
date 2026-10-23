"""Tests for the RE-2 J0 readouts ``re2_k1.py`` and ``re2_units.py`` (synthetic files; PyROOT and numpy):
    PYTHONPATH=$(root-config --libdir) python3.13 -m unittest 2d-unfolding/re2/tests/test_re2_readouts.py -v
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
RUN = HERE.parents[3] / "docs" / "orchestration" / "state" / "2d-closeout" / "stageF" / "methods" / "re2" / "run"

try:
    import ROOT
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False

if HAVE_ROOT:
    import re2_k1 as K
import re2_units as U


def root_xsec(path: Path, x: np.ndarray, refinement: dict | None = None, extra: dict | None = None,
              named: dict | None = None):
    """A driver-like output: hXSec2D (and any extra 14 x 16 histograms), plus TNamed JSON records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    f = ROOT.TFile.Open(str(path), "RECREATE")
    for name, arr in {"hXSec2D": x, **(extra or {})}.items():
        h = ROOT.TH2D(name, "", 14, 0, 14, 16, 0, 16)
        for i in range(14):
            for j in range(16):
                h.SetBinContent(i + 1, j + 1, float(arr[i, j]))
        h.Write()
    if refinement is not None:
        ROOT.TNamed("re2Refinement", json.dumps(refinement)).Write()
    for k, v in (named or {}).items():
        ROOT.TNamed(k, json.dumps(v)).Write()
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

    def test_health_fails_on_a_wrong_random_state(self):
        root_xsec(self.d / "out" / "R" / "xsec.root", self.eu,
                  dict(self.good, params={"random_state": 42, "n_estimators": 400, "num_leaves": 31}))
        r = self.run_checks(f"c1\tle\tA\trun:A\t\n")
        self.assertEqual(r["health"][0]["verdict"], "FAIL")

    def test_health_fails_on_clipping_or_size(self):
        root_xsec(self.d / "out" / "R" / "xsec.root", self.eu, dict(self.good, clipped_fraction=0.02))
        r = self.run_checks(f"c1\tle\tA\trun:A\t\n")
        self.assertEqual(r["health"][0]["verdict"], "FAIL")
        root_xsec(self.d / "out" / "R" / "xsec.root", self.eu,
                  dict(self.good, params={"random_state": 45, "n_estimators": 100, "num_leaves": 8}))
        r = self.run_checks(f"c1\tle\tA\trun:A\t\n")
        self.assertEqual(r["health"][0]["verdict"], "FAIL")


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class DeclaredTables(unittest.TestCase):
    """re2_k1.py over the DECLARED j0_runs.tsv and j0_checks.tsv, with synthetic outputs for every run: the
    verdict can be PASS (the p1ref rows carry no re2Refinement and are not health rows), and the stream check
    and the output digests fail when they should."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        d = self.d = Path(self.td.name)
        self.runs = list(csv.DictReader(open(RUN / "j0_runs.tsv"), delimiter="\t"))
        self.checks = list(csv.DictReader(open(RUN / "j0_checks.tsv"), delimiter="\t"))
        rng = np.random.default_rng(5)
        self.eu = rng.uniform(1, 2, (14, 16))
        self.eu.ravel()[:19] = 0.0
        root_xsec(d / "eu.root", self.eu)
        # every external reference becomes a local copy of E_U (its digest is then the declared one: rewritten below)
        self.refs = {}
        for c in self.checks:
            if not c["ref"].startswith("run:") and c["ref"] not in self.refs:
                p = d / "refs" / f"r{len(self.refs)}.root"
                root_xsec(p, self.eu * (1.01 if c["id"] == "K1-D1" else 1.0))   # D2 is a refined result
                self.refs[c["ref"]] = p

    def tearDown(self):
        self.td.cleanup()

    def write_outputs(self, stream_ok: bool = True):
        d = self.d
        x = {r["label"]: self.eu for r in self.runs}
        shift = {"D_cv": 1.01, "RB_001": 1.02, "RB_001_rep": 1.02, "F_MaCCQE0": 1.03, "FL_BAX0": 1.04,
                 "FL_BAX0_rep": 1.04, "RPR_PA_b01": 1.05, "D_unit": 1.01, "F_NormDISCC0": 1.01}
        good = {"params": {"random_state": 45, "n_estimators": 400, "num_leaves": 31}, "clipped_fraction": 0.0,
                "refined_over_signed": 1.0, "signed_sum": 90.0, "background_stream": True}
        for r in self.runs:
            lab = r["label"]
            ref = None
            if r["script"] == "re2" and "negweight-refined" in r["args"]:
                ref = dict(good) if "--refine-n-estimators" in r["args"] else dict(good, params={"random_state": 45})
            named = {"p1Streams": {"sum": {"data": 100.0}}} if lab == "RB_001" else None
            if lab == "RB_001" and not stream_ok:
                ref["signed_sum"] = 91.0
            extra = {"hEff2D": self.eu * 0.5}
            if lab == "B_S1_001":
                b = np.zeros((14, 16)); b[0, 0] = 10.0
                extra["hBkgRecoStar2D"] = b
            root_xsec(d / "out" / lab / "xsec.root", self.eu * shift.get(lab, 1.0), ref, extra, named)
        for job in ("J0a", "J0b"):
            lines = []
            for r in self.runs:
                if r["job"] == job:
                    p = d / "out" / r["label"] / "xsec.root"
                    lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {r['label']}/xsec.root")
            (d / f"SHA256SUMS.{job}").write_text("\n".join(lines) + "\n")

    def run_k1(self) -> dict:
        d = self.d
        rows = ["id\tkind\ttest\tref\tref_sha256\thist\tmin_shift"]
        for c in self.checks:
            ref, sha = c["ref"], c["ref_sha256"]
            if not ref.startswith("run:"):
                ref, sha = str(self.refs[ref]), K.sha256_path(self.refs[ref])
            rows.append("\t".join([c["id"], c["kind"], c["test"], ref, sha, c["hist"], c["min_shift"]]))
        (d / "checks.tsv").write_text("\n".join(rows) + "\n")
        K.main(["--runs", str(RUN / "j0_runs.tsv"), "--checks", str(d / "checks.tsv"), "--out-dir", str(d / "out"),
                "--eu", str(d / "eu.root"), "--expect-eu-sha256", K.sha256_path(d / "eu.root"),
                "--result", str(d / "k1.json")])
        return json.loads((d / "k1.json").read_text())

    def test_declared_tables_can_pass(self):
        self.write_outputs()
        r = self.run_k1()
        self.assertEqual([x["id"] for x in r["checks"] if x["verdict"] != "PASS"], [])
        self.assertEqual([x["label"] for x in r["health"] if x["verdict"] != "PASS"], [])
        health = {x["label"] for x in r["health"]}
        self.assertNotIn("R_p1_MaCCQE0", health)
        self.assertNotIn("RP_p1_PA", health)
        self.assertEqual(r["verdict"], "PASS")

    def test_stream_and_sums_fail_when_wrong(self):
        self.write_outputs(stream_ok=False)
        r = self.run_k1()
        self.assertEqual([x["id"] for x in r["checks"] if x["verdict"] != "PASS"], ["STREAM-1"])
        self.write_outputs()
        (self.d / "out" / "C_cv" / "xsec.root").write_bytes(b"tampered")
        r = self.run_k1()
        self.assertIn("C_cv/xsec.root", r["sums"]["mismatched"])
        self.assertEqual(r["verdict"], "FAIL")


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

    def verdict(self, seconds: dict, j0_charge: float = 0.0, state: dict | None = None) -> dict:
        (self.d / "steps.psv").write_text("".join(
            f"1.{i}|{l}|{seconds.get(l, 1000)}|64|{(state or {}).get(l, 'COMPLETED')}\n"
            for i, l in enumerate(self.labels)))
        (self.d / "ledger.tsv").write_text("jobid\tname\tqos\tstate\tstart\tend\telapsed_s\tbilling\tcharge_node_h\n"
                                           f"1\tre2-j0a\tregular\tCOMPLETED\t-\t-\t0\t256\t{j0_charge}\n")
        U.main(["--runs", str(self.d / "runs.tsv"), "--steps", str(self.d / "steps.psv"),
                "--ledger", str(self.d / "ledger.tsv"), "--result", str(self.d / "u.json")])
        return json.loads((self.d / "u.json").read_text())

    def test_rule_branches(self):
        # 1000 s at 64 CPUs = 0.0694 node-h per run; core counts 3+175+10+300+80+37 = 605 -> 42.0, worst 52.5
        r = self.verdict({})
        self.assertAlmostEqual(r["core_projected"], 605 * 1000 * 64 / 256 / 3600, places=9)
        self.assertEqual(r["verdict"], "WITHIN GRANT: core + J7 + J5")
        r = self.verdict({l: 1800 for l in self.labels})            # core worst 94.5 > 90
        self.assertTrue(r["verdict"].startswith("RETURN TO DIRECTOR"))
        # 1500 s: core worst 78.8; + J7 (39 runs, 3.4 worst... ) fits; + J5 (100 runs) does not
        r = self.verdict({l: 1500 for l in self.labels})
        self.assertEqual(r["included_diagnostics"], ["J7"])
        # J0's charge comes out of the 90: core worst 78.8 against room 90 - 15 = 75 -> return
        r = self.verdict({l: 1500 for l in self.labels}, j0_charge=15.0)
        self.assertTrue(r["verdict"].startswith("RETURN TO DIRECTOR"))
        self.assertAlmostEqual(r["room_node_h"], 75.0)

    def test_a_step_not_completed_stops(self):
        r = self.verdict({}, state={"F_MaRES0": "TIMEOUT"})
        self.assertTrue(r["verdict"].startswith("INCOMPLETE"))

    def test_unit_is_the_class_maximum_and_missing_steps_stop(self):
        r = self.verdict({"F_MaCCQE0": 3000})
        self.assertAlmostEqual(r["classes"]["universe"]["unit_node_h"], 3000 * 64 / 256 / 3600, places=12)
        (self.d / "steps.psv").write_text("1.0|D_cv|1000|64|COMPLETED\n")
        U.main(["--runs", str(self.d / "runs.tsv"), "--steps", str(self.d / "steps.psv"),
                "--ledger", str(self.d / "ledger.tsv"), "--result", str(self.d / "u.json")])
        self.assertTrue(json.loads((self.d / "u.json").read_text())["verdict"].startswith("INCOMPLETE"))


if __name__ == "__main__":
    unittest.main()
