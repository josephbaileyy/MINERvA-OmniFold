#!/usr/bin/env python3
"""Controls for ``run_suite.py``, which ``run_tests.sh`` decides from (the director's ruling on the REF-C2C1 cluster run
of 2026-11-05, which read RUN FAIL with every test passing: RooUnfoldBayes printed to stdout between the C-ROO test's
name and its "ok", and the old one-line grep counted it as not run).

The fixture is a two-test suite whose C-ROO-named test writes to file descriptor 1 mid-run, as RooUnfold's C++ does,
so the verbose text interleaves exactly as on the cluster. Needs only the standard library."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_suite  # noqa: E402

FIXTURE = '''import os
import unittest


class Ibu(unittest.TestCase):
    def test_roounfold_bayes_is_the_same_update(self):
        os.write(1, b"RooUnfoldBayes: iteration 1 of 5, chi2 = 0.0\\n")  # unbuffered, as RooUnfold's C++ writes


class Other(unittest.TestCase):
    def test_quiet(self):
        pass
'''
OLD_GREP = re.compile(r"^test_roounfold_bayes_is_the_same_update .*\.\.\. ok$", re.M)  # run_tests.sh before the fix
ROO = "Ibu.test_roounfold_bayes_is_the_same_update"


class Runner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        (cls.tmp / "fixture_suite.py").write_text(FIXTURE)
        cls.out = cls.tmp / "outcomes.json"
        p = subprocess.run([sys.executable, "-B", str(HERE / "run_suite.py"), "run", str(cls.tmp / "fixture_suite.py"),
                            str(cls.out)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        cls.rc, cls.text = p.returncode, p.stdout

    def test_the_runner_counts_a_test_that_prints_mid_run(self):
        self.assertEqual(self.rc, 0, self.text)
        rec = json.loads(self.out.read_text())
        self.assertEqual(rec["ran"], 2)
        self.assertEqual(rec["outcomes"], {ROO: "ok", "Other.test_quiet": "ok"})
        self.assertEqual(run_suite.verdict(rec, 2, ROO), (True, f"2 tests, none skipped, failed or errored; {ROO} ok"))
        self.assertIn("RooUnfoldBayes: iteration 1", self.text)  # the library's stdout stays in the log

    def test_the_old_grep_misses_it_on_the_same_fixture(self):
        """The fixture reaches the defect: the interleaved stdout breaks the old one-line pattern."""
        self.assertIsNone(OLD_GREP.search(self.text), self.text)
        self.assertRegex(self.text, r"test_roounfold_bayes_is_the_same_update")


class Verdict(unittest.TestCase):
    def rec(self, **outcomes):
        o = {ROO: "ok", "A.t1": "ok", **outcomes}
        return {"ran": len(o), "outcomes": o}

    def test_it_passes_only_a_complete_clean_run(self):
        self.assertTrue(run_suite.verdict(self.rec(), 2, ROO)[0])
        for bad in ("skip", "fail", "error", "unexpected success"):
            with self.subTest(outcome=bad):
                self.assertFalse(run_suite.verdict(self.rec(**{"A.t1": bad}), 2, ROO)[0])
                self.assertFalse(run_suite.verdict(self.rec(**{ROO: bad}), 2, ROO)[0])
        self.assertFalse(run_suite.verdict(self.rec(), 3, ROO)[0])  # fewer ran than expected
        r = self.rec()
        del r["outcomes"][ROO]
        r["ran"] = 2
        r["outcomes"]["A.t2"] = "ok"
        self.assertFalse(run_suite.verdict(r, 2, ROO)[0])  # C-ROO absent

    def test_a_class_level_error_is_not_ok(self):
        r = {"ran": 1, "outcomes": {ROO: "ok", "setUpClass (fixture.Driver)": "error"}}
        self.assertFalse(run_suite.verdict(r, 1, ROO)[0])

    def test_the_check_command_exits_by_the_verdict(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "o.json"
            p.write_text(json.dumps(self.rec()))
            self.assertEqual(run_suite.main(["check", str(p), "2", ROO]), 0)
            p.write_text(json.dumps(self.rec(**{ROO: "skip"})))
            self.assertEqual(run_suite.main(["check", str(p), "2", ROO]), 1)


if __name__ == "__main__":
    unittest.main()
