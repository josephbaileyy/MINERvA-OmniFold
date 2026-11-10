#!/usr/bin/env python3
"""Tests for capture_e.py on a stub phase S (no ROOT, no pscratch): each case runs the wrapper in a fresh subprocess
against a temporary directory holding stub ``cov2d.py``, ``cov2d_score.py`` and ``cov2d_readout.py``.

The stub readout's ``main`` calls ``cs.errors`` once, checks that it received exactly the object the original returned
(the pass-through), and writes a score record; ``STUB_MODE`` selects a defect. Run: ``python3 test_capture_e.py``.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

TOOL = Path(__file__).resolve().parent / "capture_e.py"

STUB_COV2D = 'TOY_SEEDS = {"G18": range(5_720_000, 5_720_300), "AR23": range(5_730_000, 5_730_300)}\n'

STUB_SCORE = '''
import numpy as np
LAST = {}
def errors(x_hat, x_true, natures, deltas, C_T):
    E = np.asarray(x_hat, float) - np.asarray(x_true, float)
    out = (E, {"max_over_sigma": 0.5})
    LAST["E_id"] = id(E)
    LAST["out_id"] = id(out)
    return out
'''

STUB_READOUT = '''
import argparse, json, os, sys
from pathlib import Path
import numpy as np
import cov2d as c
import cov2d_score as cs

def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("score")
    p.add_argument("--truth", required=True); p.add_argument("--null-digest", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    mode = os.environ.get("STUB_MODE", "ok")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "phase_s_ran").write_text("1")
    if mode == "rc3":
        return 3
    if mode == "raise":
        raise ModuleNotFoundError("No module named 'ROOT'")
    rng = np.random.default_rng(7)
    n = 300 if mode != "shape" else 299
    x_hat = rng.normal(size=(n, 205)); x_true = np.zeros((n, 205))
    if mode == "nan":
        x_hat[3, 4] = np.nan
    res = cs.errors(x_hat, x_true, [], None, None)
    passthrough = (id(res) == cs.LAST["out_id"]) and (id(res[0]) == cs.LAST["E_id"])
    if mode == "twice":
        cs.errors(x_hat, x_true, [], None, None)
    E = res[0]
    rec = {"M": "m" * 40, "truth": a.truth, "utc": os.environ.get("STUB_UTC", "2026-11-10T00:00:00Z"),
           "host": os.environ.get("STUB_HOST", "login02"), "null_digest": a.null_digest,
           "grade": {"chi2_mean_over_ndf": float(np.nanmean(E ** 2)), "counts": [int(x) for x in np.sum(np.abs(E) <= 1, 0)]},
           "passthrough": bool(passthrough), "nan_leaf": float("nan")}
    if mode == "drift":
        rec["grade"]["counts"][17] += 1
    if mode == "extra":
        rec["extra"] = 1
    if mode == "missing":
        del rec["passthrough"]
    (out / f"score_{a.truth}.json").write_text(json.dumps(rec, indent=1))
    print(f"COV2D-SCORE {a.truth} UNDER-COVERS")
    return 0
'''


def expected_E() -> np.ndarray:
    return np.random.default_rng(7).normal(size=(300, 205))


def reference_record(truth="G18") -> dict:
    E = expected_E()
    return {"M": "m" * 40, "truth": truth, "utc": "2026-11-08T03:35:34Z", "host": "login02", "null_digest": "d" * 64,
            "grade": {"chi2_mean_over_ndf": float(np.nanmean(E ** 2)), "counts": [int(x) for x in np.sum(np.abs(E) <= 1, 0)]},
            "passthrough": True, "nan_leaf": float("nan")}


class Capture(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        d = Path(self.td.name)
        self.cov2d = d / "deploy" / "2d-unfolding" / "cov2d"
        self.cov2d.mkdir(parents=True)
        (self.cov2d / "cov2d.py").write_text(STUB_COV2D)
        (self.cov2d / "cov2d_score.py").write_text(STUB_SCORE)
        (self.cov2d / "cov2d_readout.py").write_text(STUB_READOUT)
        self.ref = d / "ref_score_G18.json"
        self.ref.write_text(json.dumps(reference_record(), indent=1))
        self.ref_sha = hashlib.sha256(self.ref.read_bytes()).hexdigest()
        self.out = d / "out"

    def tearDown(self):
        self.td.cleanup()

    def run_capture(self, mode="ok", ref_sha=None, env=None):
        e = dict(os.environ, STUB_MODE=mode, PYTHONDONTWRITEBYTECODE="1", **(env or {}))
        cmd = [sys.executable, "-B", str(TOOL), "--cov2d-dir", str(self.cov2d), "--truth", "G18",
               "--null-digest", "d" * 64, "--out", str(self.out), "--ref-score", str(self.ref),
               "--ref-score-sha256", ref_sha or self.ref_sha]
        p = subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=str(self.cov2d))
        return p

    def assertNoE(self):
        self.assertFalse((self.out / "E_G18.npz").exists())
        self.assertFalse((self.out / "E_G18.partial.npz").exists())

    def test_ok_writes_E_and_excepts_only_utc_host(self):
        p = self.run_capture("ok", env={"STUB_UTC": "2026-11-11T09:00:00Z", "STUB_HOST": "login17"})
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        z = np.load(self.out / "E_G18.npz", allow_pickle=False)
        np.testing.assert_array_equal(z["E"], expected_E())
        self.assertEqual(z["seeds"][0], 5_720_000)
        self.assertEqual(z["seeds"][-1], 5_720_299)
        self.assertEqual(str(z["truth"]), "G18")
        rec = json.loads((self.out / "capture_G18.json").read_text())
        self.assertEqual(rec["status"], "OK")
        self.assertTrue(rec["A0"]["equal"])
        self.assertEqual(rec["A0"]["excepted"], ["utc", "host"])
        self.assertEqual(rec["e_npz_sha256"], hashlib.sha256((self.out / "E_G18.npz").read_bytes()).hexdigest())
        self.assertEqual(rec["wrapper_sha256"], hashlib.sha256(TOOL.read_bytes()).hexdigest())
        self.assertIn("COV2D-SCORE G18 UNDER-COVERS", p.stdout)

    def test_passthrough_is_exact(self):
        # the stub writes passthrough=False if the readout received anything but the original's return value
        p = self.run_capture("ok")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        regen = json.loads((self.out / "score_G18.json").read_text())
        self.assertIs(regen["passthrough"], True)

    def test_drifted_leaf_stops_without_E(self):
        p = self.run_capture("drift")
        self.assertEqual(p.returncode, 8, p.stdout + p.stderr)
        rec = json.loads((self.out / "STOP_G18.json").read_text())
        self.assertEqual(rec["A0"]["differing_fields"], ["grade"])
        self.assertEqual(rec["A0"]["differing_leaves"], ["grade.counts[17]"])
        self.assertNoE()

    def test_extra_and_missing_fields_stop(self):
        for mode, field in (("extra", "extra"), ("missing", "passthrough")):
            with self.subTest(mode=mode):
                for f in self.out.glob("*"):
                    f.unlink()
                p = self.run_capture(mode)
                self.assertEqual(p.returncode, 8, p.stdout + p.stderr)
                rec = json.loads((self.out / "STOP_G18.json").read_text())
                self.assertEqual(rec["A0"]["differing_fields"], [field])
                self.assertNoE()

    def test_ref_sha_mismatch_stops_before_phase_s(self):
        p = self.run_capture("ok", ref_sha="0" * 64)
        self.assertEqual(p.returncode, 8, p.stdout + p.stderr)
        self.assertFalse((self.out / "phase_s_ran").exists())
        self.assertTrue((self.out / "STOP_G18.json").exists())
        self.assertNoE()

    def test_phase_s_failure_is_failed(self):
        p = self.run_capture("rc3")
        self.assertEqual(p.returncode, 9, p.stdout + p.stderr)
        rec = json.loads((self.out / "FAILED_G18.json").read_text())
        self.assertEqual(rec["phase_s_rc"], 3)
        self.assertNoE()

    def test_phase_s_exception_is_failed(self):
        p = self.run_capture("raise")
        self.assertEqual(p.returncode, 9, p.stdout + p.stderr)
        rec = json.loads((self.out / "FAILED_G18.json").read_text())
        self.assertIn("ModuleNotFoundError", rec["why"])
        self.assertIn("traceback", rec)
        self.assertNoE()

    def test_errors_called_twice_is_failed(self):
        p = self.run_capture("twice")
        self.assertEqual(p.returncode, 9, p.stdout + p.stderr)
        self.assertIn("called 2 times", json.loads((self.out / "FAILED_G18.json").read_text())["why"])
        self.assertNoE()

    def test_wrong_shape_and_nonfinite_are_failed(self):
        for mode in ("shape", "nan"):
            with self.subTest(mode=mode):
                for f in self.out.glob("*"):
                    f.unlink()
                # the reference is this mode's own record, so A0 passes and the E check is what fires
                rec = reference_record()
                rng = np.random.default_rng(7)
                n = 299 if mode == "shape" else 300
                x = rng.normal(size=(n, 205))
                if mode == "nan":
                    x[3, 4] = np.nan
                rec["grade"] = {"chi2_mean_over_ndf": float(np.nanmean(x ** 2)),
                                "counts": [int(v) for v in np.sum(np.abs(x) <= 1, 0)]}
                self.ref.write_text(json.dumps(rec, indent=1))
                sha = hashlib.sha256(self.ref.read_bytes()).hexdigest()
                p = self.run_capture(mode, ref_sha=sha)
                self.assertEqual(p.returncode, 9, p.stdout + p.stderr)
                self.assertIn("E is", json.loads((self.out / "FAILED_G18.json").read_text())["why"])
                self.assertNoE()

    def test_nonempty_out_is_refused(self):
        self.out.mkdir()
        (self.out / "left").write_text("x")
        p = self.run_capture("ok")
        self.assertEqual(p.returncode, 8, p.stdout + p.stderr)
        self.assertFalse((self.out / "phase_s_ran").exists())

    def test_runs_with_a_wrapped_original(self):
        # a stub whose original errors() records its arguments' identity; the wrapper must pass them through
        (self.cov2d / "cov2d_score.py").write_text(STUB_SCORE + '''
_orig = errors
def errors(x_hat, x_true, natures, deltas, C_T):
    LAST["args"] = (x_hat.shape, x_true.shape, natures, deltas, C_T)
    return _orig(x_hat, x_true, natures, deltas, C_T)
''')
        p = self.run_capture("ok")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


class Compare(unittest.TestCase):
    def test_leaves(self):
        sys.path.insert(0, str(TOOL.parent))
        try:
            import capture_e as ce
        finally:
            sys.path.pop(0)
        a = {"x": [1, 2.0, {"y": float("nan")}], "utc": "a", "host": "h"}
        b = {"x": [1, 2.0, {"y": float("nan")}], "utc": "b", "host": "g"}
        self.assertTrue(ce.compare(a, b)["equal"])
        b2 = {"x": [1, 2, {"y": float("nan")}], "utc": "b", "host": "g"}     # int vs float is a difference
        self.assertEqual(ce.compare(a, b2)["differing_leaves"], ["x[1]"])
        b3 = {"x": [1, 2.0], "utc": "b", "host": "g"}
        self.assertEqual(ce.compare(a, b3)["differing_leaves"], ["x[len 3 != 2]"])
        self.assertEqual(ce.compare({"M": "a"}, {"M": "b"})["differing_fields"], ["M"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
