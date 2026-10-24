"""Unit tests for RE-2 part C's own code (RE2-DECLARATION-C.md §2.3). numpy only; no ROOT, no cluster.

    python3 -m unittest test_re2c -v      (from this directory)

The copies' purity arms are tested where they matter, by the K1-roll on the real inputs (re2c_k1roll.py). Here:
the sibling pins, the committed copy diffs, the values engine's three gates in both directions, the period mode
guard in both directions, the K1-roll comparator's helpers, and C_model's arithmetic beside Q_R.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class SiblingPins(unittest.TestCase):
    def test_playlist_and_combine_pin_the_current_period_copies(self):
        for target in ("re2c_playlist_term.py", "re2c_combine.py"):
            s = (HERE / target).read_text()
            for n in ("re2c_analyze_periods.py", "re2c_periods.py"):
                d = hashlib.sha256((HERE / n).read_bytes()).hexdigest()
                self.assertIn(f'f"{{SCRIPTS}}/{n}": "{d}"', s, f"{target} pins a stale {n}: run pin_siblings.py")


class CopyDiffs(unittest.TestCase):
    """Each committed copy diff (diffs/<copy>.diff) is the diff of the copy against its original as committed."""
    ORIGINALS = {
        "re2c_analyze.py": "docs/orchestration/state/2d-closeout/stageC/production/analyze_prod.py",
        "re2c_rollup.py": "docs/orchestration/state/2d-closeout/stageC/production/s5_rollup.py",
        "re2c_export_cov.py": "docs/orchestration/state/2d-closeout/playlist-spread-20261014/coverage/scripts/export_cov.py",
        "re2c_periods.py": "docs/orchestration/state/2d-closeout/period-unfold-20261014/scripts/periods.py",
        "re2c_analyze_periods.py": "docs/orchestration/state/2d-closeout/period-unfold-20261014/scripts/analyze_periods.py",
        "re2c_playlist_term.py": "docs/orchestration/state/2d-closeout/playlist-term/scripts/playlist_term.py",
        "re2c_combine.py": "docs/orchestration/state/2d-closeout/playlist-term/scripts/combine_s5.py",
        "re2c_build_q.py": "docs/orchestration/state/2d-closeout/stageF/rebuild/scripts/build_q_products.py",
        "re2c_fig1.py": "docs/orchestration/state/2d-closeout/stageF/rebuild/scripts/make_fig1_q.py",
    }

    def test_committed_diffs_are_current(self):
        for copy, orig in self.ORIGINALS.items():
            want = subprocess.run(["diff", "-u", "--label", orig, "--label", f"2d-unfolding/re2/partc/{copy}",
                                   str(REPO / orig), str(HERE / copy)], capture_output=True, text=True).stdout
            got = (HERE / "diffs" / f"{copy}.diff").read_text()
            self.assertEqual(got, want, f"diffs/{copy}.diff is stale: run make_diffs.sh")

    def test_every_removed_line_is_accounted_for(self):
        """A purity path must not lose code: every line a copy removes from its original reappears in the copy
        (moved under an arm branch or into the new docstring), except the lines in diffs/removed_lines.json, each
        reviewed: a docstring head, a pin or path the refined arm generalizes, or a call that gained an argument.
        The set must match exactly, both ways, so a new removal or a stale entry fails."""
        allowed = json.loads((HERE / "diffs" / "removed_lines.json").read_text())
        self.assertEqual(set(allowed), set(self.ORIGINALS))
        for copy in self.ORIGINALS:
            text = (HERE / copy).read_text()
            removed = [ln[1:].strip() for ln in (HERE / "diffs" / f"{copy}.diff").read_text().splitlines()
                       if ln.startswith("-") and not ln.startswith("---") and ln[1:].strip()]
            self.assertEqual([ln for ln in removed if ln not in text], allowed[copy], copy)


class ValuesEngine(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        n = self.d / "docs" / "analysis-note"
        n.mkdir(parents=True)
        (n / "values.tex").write_text("\\newcommand{\\foo}{1.23}\n\\newcommand{\\dup}{1}\n\\newcommand{\\dup}{1}\n")
        (n / "body.tex").write_text("line one\nthe value is 4.56 here\n")
        self.V = load("re2c_values")
        self.V.SOURCES = {"src": ("p.json", "r.json")}
        (self.d / "p.json").write_text(json.dumps({"a": {"b": 1.234, "c": 4.561}}))
        self.ref = self.d / "refined"
        self.ref.mkdir()
        (self.ref / "r.json").write_text(json.dumps({"a": {"b": 1.301, "c": 4.559}}))

    def run_spec(self, rows, refined=True):
        spec = self.d / "spec.tsv"
        hdr = ["id", "where", "printed", "source", "path", "transform", "fmt", "group", "note", "expect"]
        spec.write_text("\t".join(hdr) + "\n" + "".join("\t".join(r) + "\n" for r in rows))
        argv = ["--repo", str(self.d), "--spec", str(spec), "--out-tsv", str(self.d / "t.tsv"),
                "--out-json", str(self.d / "t.json")] + (["--refined-dir", str(self.ref)] if refined else [])
        rc = self.V.main(argv)
        return rc, {r["id"]: r for r in json.loads((self.d / "t.json").read_text())["rows"]}

    def test_good_rows_pass_and_regenerate(self):
        rc, r = self.run_spec([["m", "N/values.tex:\\foo", "1.23", "src", "a.b", "v", ".2f", "g", "", ""],
                               ["l", "N/body.tex:2", "4.56", "src", "a.c", "v", ".2f", "g", "", ""]])
        self.assertEqual(rc, 0)
        self.assertEqual((r["m"]["refined_rendered"], r["m"]["changes_at_printed_precision"]), ("1.30", True))
        self.assertEqual((r["l"]["refined_rendered"], r["l"]["changes_at_printed_precision"]), ("4.56", False))

    def test_each_gate_fires(self):
        cases = {"wrong printed (control)": ["x", "N/values.tex:\\foo", "1.24", "src", "a.b", "v", ".2f", "g", "", ""],
                 "not on the line (anchor)": ["x", "N/body.tex:1", "4.56", "src", "a.c", "v", ".2f", "g", "", ""],
                 "macro defined twice": ["x", "N/values.tex:\\dup", "1", "src", "a.b", "v", ".0f", "g", "", ""],
                 "no such field": ["x", "N/body.tex:2", "4.56", "src", "a.zz", "v", ".2f", "g", "", ""]}
        for why, row in cases.items():
            rc, r = self.run_spec([row])
            self.assertEqual(rc, 3, why)
            self.assertNotIn("refined_rendered", r["x"], f"{why}: a failed row must not be regenerated")

    def test_declared_failure_is_listed_not_fatal_and_cannot_silently_close(self):
        rc, r = self.run_spec([["x", "N/values.tex:\\foo", "1.24", "src", "a.b", "v", ".2f", "g", "", "fails"]])
        self.assertEqual(rc, 0)
        self.assertEqual(r["x"]["status"], "CONTROL FAILS: not regenerated")
        rc, _ = self.run_spec([["x", "N/values.tex:\\foo", "1.23", "src", "a.b", "v", ".2f", "g", "", "fails"]])
        self.assertEqual(rc, 3, "a declared failure that passes must be flagged")

    def test_per_arm_source_and_path(self):
        self.V.SOURCES["alt"] = (None, "alt.json")
        (self.ref / "alt.json").write_text(json.dumps({"z": 9.87}))
        rc, r = self.run_spec([["x", "N/body.tex:2", "4.56", "src || alt", "a.c || z", "v", ".2f", "g", "", ""]])
        self.assertEqual((rc, r["x"]["refined_rendered"]), (0, "9.87"))

    def test_purity_only_run_writes_no_regenerated_value(self):
        rc, r = self.run_spec([["m", "N/values.tex:\\foo", "1.23", "src", "a.b", "v", ".2f", "g", "", ""]],
                              refined=False)
        self.assertEqual(rc, 0)
        self.assertNotIn("refined_rendered", r["m"])


class PeriodModeGuard(unittest.TestCase):
    def setUp(self):
        self.PD = load("re2c_periods")

    def test_purity_arm(self):
        ok = {"path": "p", "driverSha256": self.PD.PINS["producer"][1], "bkg_mode": "purity"}
        self.PD.check_mode(ok)
        self.PD.check_mode({**ok, "bkg_mode": None})
        for bad in ({**ok, "driverSha256": "0" * 64}, {**ok, "bkg_mode": "negweight-refined"}):
            with self.assertRaises(SystemExit):
                self.PD.check_mode(bad)

    def test_refined_arm(self):
        self.PD.set_arm("refined", work_cov=("/x/work_cov.npz", "a" * 64), ns="/x/ns")
        self.assertEqual(self.PD.PINS["E_U"][1], "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef")
        self.assertEqual(self.PD.PINS["work_cov"], ("/x/work_cov.npz", "a" * 64))
        ok = {"path": "p", "driverSha256": self.PD.PINS_REFINED["producer"][1], "bkg_mode": "negweight-refined",
              "refine_n_estimators": 400, "refine_num_leaves": 31}
        self.PD.check_mode(ok)
        for bad in ({**ok, "refine_num_leaves": 8}, {**ok, "bkg_mode": "purity"}, {**ok, "driverSha256": None}):
            with self.assertRaises(SystemExit):
                self.PD.check_mode(bad)

    def test_refined_arm_needs_its_pins(self):
        with self.assertRaises(SystemExit):
            self.PD.set_arm("refined")


class K1rollHelpers(unittest.TestCase):
    def setUp(self):
        self.K = load("re2c_k1roll")

    def test_drop_and_diff(self):
        a = {"x": 1, "y": {"z": 2, "w": 3}, "arm": "purity"}
        b = {"x": 1, "y": {"z": 2, "w": 4}}
        self.assertEqual(self.K.diff(self.K.drop(a, ["arm", "y.w"]), self.K.drop(b, ["y.w"])), [])
        self.assertTrue(self.K.diff(self.K.drop(a, ["arm"]), b))

    def test_text_drops_path_lines_only(self):
        p = Path(tempfile.mkdtemp()) / "t.txt"
        p.write_text("[ours] opening: /pscratch/a.root\n  chi2/ndf = 0.964\nwrote /x.png\n")
        self.assertEqual(self.K.text(p), ["  chi2/ndf = 0.964"])


class CmodelArithmetic(unittest.TestCase):
    def test_total_is_q_plus_c_abs_and_q_is_untouched(self):
        sys.path.insert(0, str(REPO / "2d-unfolding" / "pv2d" / "cmodel"))
        sys.path.insert(0, str(REPO / "2d-unfolding" / "pv2d"))
        import build_cmodel as BC
        rng = np.random.default_rng(1)
        S = rng.normal(0, 0.03, (3, 6))
        x = rng.uniform(1, 2, 6)
        A = rng.normal(0, 1, (6, 6))
        Q = A @ A.T * 1e-3
        Q0 = Q.copy()
        C = BC.cmodel(S)
        total = Q + BC.absolute(C, x)
        self.assertTrue(np.array_equal(Q, Q0))
        np.testing.assert_allclose(np.diag(total), np.diag(Q) + (S ** 2).sum(0) * x ** 2, rtol=1e-14)
        self.assertEqual(np.linalg.matrix_rank(C), 3)


if __name__ == "__main__":
    unittest.main()
