"""control1_content_check on synthetic omnifile pairs written with uproot (needs uproot 5.6.9 and numpy):
  python3 -B -m pytest -q docs/.../fd/receipts-cov2d/control1/test_control1_content_check.py
Each fixture mirrors the real pair's tree and branch layout (p1p3_probe.out): the universe file carries every CV branch
plus extra ones. The check must be silent on an exact copy and fire on each way the copy can differ."""
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control1_content_check as cc  # noqa: E402

N_SIG, N_DATA, N_BKG = 23, 11, 7


def cv_world(seed=0):
    r = np.random.default_rng(seed)
    sig = {"sim": r.normal(size=N_SIG), "sim_pz": r.normal(size=N_SIG), "sim_pass": r.random(N_SIG) < 0.7,
           "w_reco": r.random(N_SIG), "MC": r.normal(size=N_SIG), "MC_pz": r.normal(size=N_SIG),
           "w_truth": r.random(N_SIG)}
    sig["sim"][3] = np.nan
    return {
        "mc_signal_reco": sig,
        "mc_truth_denom": {"MC": sig["MC"].copy(), "MC_pz": sig["MC_pz"].copy(), "w_truth": sig["w_truth"].copy()},
        "data": {"measured": r.normal(size=N_DATA), "measured_pz": r.normal(size=N_DATA),
                 "measured_pass": r.random(N_DATA) < 0.5},
        "mc_background": {"sim_background": r.normal(size=N_BKG), "sim_background_pz": r.normal(size=N_BKG),
                          "sim_background_pass": r.random(N_BKG) < 0.5, "w_bkg": r.random(N_BKG)},
    }


def uni_from(cv):
    """The universe file: an exact copy of every CV column plus extra branches, as the real $UNI carries."""
    uni = {t: {b: v.copy() for b, v in cols.items()} for t, cols in cv.items()}
    n = {t: len(next(iter(c.values()))) for t, c in cv.items()}
    uni["mc_signal_reco"]["MC_eavail"] = np.linspace(0, 1, n["mc_signal_reco"])
    uni["mc_truth_denom"]["MC_q3"] = np.linspace(0, 2, n["mc_truth_denom"])
    uni["data"]["measured_W"] = np.linspace(0, 3, n["data"])
    uni["mc_background"]["w_bkg_2p2h_0"] = np.ones(n["mc_background"])
    return uni


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        p.start()
        self.addCleanup(p.stop)

    def write(self, name, world):
        path = os.path.join(self.tmp.name, name)
        with uproot.recreate(path) as f:
            for t, cols in world.items():
                f.mktree(t, {b: v.dtype for b, v in cols.items()}).extend(cols)
        future = time.time() + 86400  # atime after mtime, so a relatime filesystem leaves it alone on read
        os.utime(path, (future, os.stat(path).st_mtime))
        return path

    def run_check(self, cv, uni, step=5):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cc.main(["--cv", self.write("cv.root", cv), "--uni", self.write("uni.root", uni), "--step", str(step)])
        return rc, out.getvalue()

    def assert_fails(self, cv, uni, needle, step=5):
        rc, text = self.run_check(cv, uni, step)
        self.assertEqual(rc, 3, text)
        self.assertIn("CONTROL1 FAIL", text)
        self.assertIn(needle, "\n".join(l for l in text.splitlines() if l.startswith("FAILURE")), text)
        return text


class Silent(Case):
    def test_exact_copy_passes(self):
        cv = cv_world()
        rc, text = self.run_check(cv, uni_from(cv))
        self.assertEqual(rc, 0, text)
        self.assertIn("CONTROL1 PASS failures=0", text)
        self.assertNotIn("FAILURE", text)
        self.assertEqual(text.count("EQUAL "), 17)  # 7 + 3 + 3 + 4 CV branches, each compared
        self.assertNotIn("MC_eavail rows", text)  # UNI-only branches are not compared

    def test_step_larger_than_tree(self):
        cv = cv_world()
        rc, text = self.run_check(cv, uni_from(cv), step=10_000)
        self.assertEqual(rc, 0, text)


class Fires(Case):
    def test_one_value_in_last_partial_chunk(self):
        cv = cv_world()
        uni = uni_from(cv)
        uni["mc_signal_reco"]["w_truth"][N_SIG - 1] += 1e-12
        text = self.assert_fails(cv, uni, f"mc_signal_reco.w_truth: 1 rows differ (value-unequal 1); first row {N_SIG - 1}")
        self.assertIn("EQUAL  mc_truth_denom.w_truth", text)
        line = next(l for l in text.splitlines() if "DIFFER mc_signal_reco.w_truth" in l)
        cv_hash, uni_hash = line.split("sha256 CV=")[1].split(" UNI=")
        self.assertNotEqual(cv_hash, uni_hash, line)  # each file's digest is of its own column

    def test_each_tree_is_read(self):
        for tree, branch in (("mc_truth_denom", "MC_pz"), ("data", "measured"), ("mc_background", "w_bkg")):
            with self.subTest(tree=tree):
                cv = cv_world()
                uni = uni_from(cv)
                uni[tree][branch][0] *= 2
                self.assert_fails(cv, uni, f"{tree}.{branch}: 1 rows differ")

    def test_row_swap_is_not_equal(self):
        cv = cv_world()
        uni = uni_from(cv)
        col = uni["mc_signal_reco"]["MC"]
        col[[4, 9]] = col[[9, 4]]
        self.assert_fails(cv, uni, "mc_signal_reco.MC: 2 rows differ")

    def test_bool_flip(self):
        cv = cv_world()
        uni = uni_from(cv)
        uni["data"]["measured_pass"][2] = ~uni["data"]["measured_pass"][2]
        self.assert_fails(cv, uni, "data.measured_pass: 1 rows differ")

    def test_negative_zero_is_a_bitwise_difference(self):
        cv = cv_world()
        cv["mc_signal_reco"]["MC_pz"][5] = 0.0
        uni = uni_from(cv)
        uni["mc_signal_reco"]["MC_pz"][5] = -0.0
        self.assert_fails(cv, uni, "mc_signal_reco.MC_pz: 1 rows differ (value-unequal 0)")

    def test_nan_against_number(self):
        cv = cv_world()
        uni = uni_from(cv)
        uni["mc_signal_reco"]["sim"][3] = 0.5  # CV row 3 is NaN
        self.assert_fails(cv, uni, "mc_signal_reco.sim: 1 rows differ (value-unequal 1); first row 3")

    def test_dtype_narrowed_with_equal_values(self):
        cv = cv_world()
        cv["mc_signal_reco"]["w_reco"] = np.round(cv["mc_signal_reco"]["w_reco"], 2).astype(np.float32).astype(np.float64)
        uni = uni_from(cv)
        uni["mc_signal_reco"]["w_reco"] = uni["mc_signal_reco"]["w_reco"].astype(np.float32)
        self.assert_fails(cv, uni, "mc_signal_reco.w_reco: interpretation")

    def test_cv_branch_absent_from_uni(self):
        cv = cv_world()
        uni = uni_from(cv)
        del uni["mc_background"]["sim_background_pz"]
        self.assert_fails(cv, uni, "mc_background.sim_background_pz: in CV, absent from UNI")

    def test_declared_branch_absent_from_both(self):
        cv = cv_world()
        del cv["mc_truth_denom"]["w_truth"]
        uni = uni_from(cv)
        self.assert_fails(cv, uni, "mc_truth_denom.w_truth: declared, absent from CV")

    def test_tree_absent_from_uni(self):
        cv = cv_world()
        uni = uni_from(cv)
        del uni["mc_background"]
        self.assert_fails(cv, uni, "tree mc_background: in CV, absent from UNI")

    def test_entry_count_differs(self):
        cv = cv_world()
        uni = uni_from(cv)
        uni["data"] = {b: v[:-1] for b, v in uni["data"].items()}
        self.assert_fails(cv, uni, f"data: entries CV={N_DATA} UNI={N_DATA - 1}")

    def test_atime_move_fails(self):
        cv = cv_world()
        uni = uni_from(cv)
        real = cc.stat_line
        calls = {"n": 0}

        def moving(path):
            line, atime = real(path)
            calls["n"] += 1
            return line, atime + (1 if calls["n"] > 2 and path.endswith("uni.root") else 0)

        with mock.patch.object(cc, "stat_line", moving):
            self.assert_fails(cv, uni, "UNI: atime moved")


class FailClosed(unittest.TestCase):
    def test_no_noatime_flag_raises(self):
        no_flag = types.SimpleNamespace(open=os.open, fdopen=os.fdopen, O_RDONLY=os.O_RDONLY)  # os without O_NOATIME
        with mock.patch.object(cc, "os", no_flag), self.assertRaises(AttributeError):
            cc.open_noatime(__file__)


if __name__ == "__main__":
    unittest.main()
