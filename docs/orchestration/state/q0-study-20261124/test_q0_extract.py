#!/usr/bin/env python3
"""Tests of q0_extract.py on a synthetic omnifile (uproot-written): the RecoQ3 inversion, the W-identity control, every
STOP, and that only `mc_signal_reco` is ever opened (never the data tree).

    python3 -m unittest docs/orchestration/state/q0-study-20261124/test_q0_extract.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import uproot

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import q0_extract as X  # noqa: E402


def reco_q3_w(pt, pz, q0):
    """Forward RecoQ3 / RecoW (CVUniverse.h:208-219, 227-240) in MeV, with M_bar as the omnifile's W uses."""
    emu = np.sqrt(pt ** 2 + pz ** 2 + X.M_MU ** 2)
    p = np.sqrt(pt ** 2 + pz ** 2)
    cos = pz / p
    q2 = 2.0 * (emu + q0) * (emu - p * cos) - X.M_MU ** 2
    q2 = np.maximum(q2, 0.0)
    q3 = np.sqrt(q2 + q0 * q0)
    w2 = X.M_BAR ** 2 + 2 * X.M_BAR * q0 - q2
    return q3, np.sqrt(np.maximum(w2, 0.0))


def make_omni(path: Path, n: int = 4000, seed: int = 1, drop=(), w_shift: float = 0.0):
    rng = np.random.default_rng(seed)
    pt = rng.uniform(0.05, 2.0, n)                # GeV
    pz = rng.uniform(1.6, 20.0, n)
    q0 = rng.uniform(0.02, 3.0, n)
    q3, W = reco_q3_w(pt * 1000, pz * 1000, q0 * 1000)
    q3[:5] = 1.0   # MeV, below sqrt(c) (the least q3 any q0 >= 0 gives): the inversion's Q^2 clamp branch, status 1
    sig = {"sim": pt, "sim_pz": pz, "sim_eavail": 0.6 * np.clip(q0, 0, None) + rng.normal(0, 0.02, n),
           "sim_q3": q3 / 1000, "sim_W": W / 1000 + w_shift, "sim_pass": (rng.uniform(size=n) < 0.7).astype(np.int32),
           "w_reco": rng.uniform(0.5, 1.5, n), "MC": pt * 1.01, "MC_pz": pz, "MC_q3": q3 / 1000 * 1.02,
           "MC_W": W / 1000 * 0.99, "MC_eavail": np.zeros(n), "MC_npip": np.zeros(n), "w_truth": np.ones(n)}
    for k in drop:
        sig.pop(k)
    with uproot.recreate(path) as f:
        f["mc_signal_reco"] = sig
        f["data"] = {"measured": rng.normal(size=10), "measured_q3": rng.normal(size=10)}
    return sig


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Recovery(unittest.TestCase):
    def test_inverts_recoq3(self):
        rng = np.random.default_rng(5)
        pt, pz, q0 = rng.uniform(50, 2000, 1000), rng.uniform(1600, 20000, 1000), rng.uniform(20, 3000, 1000)
        q3, _ = reco_q3_w(pt, pz, q0)
        got, st = X.recover_q0(pt, pz, q3)
        self.assertTrue(np.all(st == 0))
        np.testing.assert_allclose(got, q0, rtol=1e-9)

    def test_clamp_and_nonfinite_status(self):
        # q3 below sqrt(c) = sqrt(2 E a - m^2) has no q0 >= 0: the root is NaN, Q^2 fails ">= 0", q0 := q3 (status 1)
        got, st = X.recover_q0(np.array([300.0, np.nan]), np.array([5000.0, 1.0]), np.array([1.0, 1.0]))
        self.assertEqual(st.tolist(), [1, 2])
        self.assertAlmostEqual(got[0], 1.0)

    def test_a_negative_q0_is_not_recoverable_and_the_w_control_sees_it(self):
        """RecoQ3 clamps Q^2 for a negative q0; the inversion then returns another (positive) q0, so W(q0) != W."""
        q3, W = reco_q3_w(np.array([300.0]), np.array([5000.0]), np.array([-500.0]))
        got, st = X.recover_q0(np.array([300.0]), np.array([5000.0]), q3)
        self.assertEqual(st.tolist(), [0])
        self.assertGreater(got[0], 0)
        Wq, _ = X.w_from_q0(got, q3)
        self.assertGreater(abs(Wq[0] - W[0]), 1.0)

    def test_w_identity(self):
        q3, W = reco_q3_w(np.array([500.0]), np.array([6000.0]), np.array([800.0]))
        q0, _ = X.recover_q0(np.array([500.0]), np.array([6000.0]), q3)
        Wq, neg = X.w_from_q0(q0, q3)
        self.assertFalse(neg[0])
        np.testing.assert_allclose(Wq, W, rtol=1e-12)


class Extract(unittest.TestCase):
    def setUp(self):
        self.allow = mock.patch.object(X, "ALLOW_PLAIN_READ", True)
        self.noat = mock.patch.object(X, "NOATIME", None)
        self.allow.start()
        self.noat.start()

    def tearDown(self):
        self.allow.stop()
        self.noat.stop()

    def run_ok(self, d: Path, **kw):
        omni = d / "omni.root"
        sig = make_omni(omni, **kw)
        out = d / "out"
        out.mkdir()
        n = int((sig["sim_pass"] != 0).sum())
        return omni, out, n, sig

    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            omni, out, n, sig = self.run_ok(d)
            rec = X.extract(str(omni), out, expected_pass=n, omni_sha=sha(omni))
            z = np.load(out / "q0_extract.npz")
            self.assertEqual(sorted(z.files), sorted(["pt", "pz", "eavail", "q3", "W", "q0", "w_reco", "q3_true",
                                                      "W_true", "q0_status", "in_truth_ps"]))
            for k in ("pt", "pz", "eavail", "q3", "W", "q0", "w_reco", "q3_true", "W_true"):
                self.assertEqual(z[k].dtype, np.float32)
                self.assertEqual(z[k].size, n)
            self.assertEqual(z["q0_status"].dtype, np.int8)
            sel = sig["sim_pass"] != 0
            np.testing.assert_allclose(z["pt"], sig["sim"][sel].astype(np.float32))
            np.testing.assert_allclose(z["W_true"], sig["MC_W"][sel].astype(np.float32))
            self.assertEqual(rec["n_pass"], n)
            self.assertEqual(rec["npz_sha256"], sha(out / "q0_extract.npz"))
            self.assertLessEqual(rec["recovery_control"]["max_abs_resid_GeV"], 1e-6)
            self.assertGreater(rec["q0_status_counts"]["1"], 0)   # the planted clamp rows that pass
            self.assertEqual(rec["omni_stat_before"]["atime_ns"], rec["omni_stat_after"]["atime_ns"])

    def test_main_writes_json_and_refuses_a_non_empty_dir(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            omni, out, n, _ = self.run_ok(d)
            with mock.patch.object(X, "EXPECTED_PASS", n), mock.patch.object(X, "OMNI_SHA", sha(omni)), \
                    mock.patch.object(X.extract, "__defaults__", (n, sha(omni))):
                self.assertEqual(X.main(["--omni", str(omni), "--out", str(out)]), 0)
                self.assertTrue((out / "q0_extract.json").exists())
                self.assertEqual(json.loads((out / "q0_extract.json").read_text())["n_pass"], n)
                self.assertEqual(X.main(["--omni", str(omni), "--out", str(out)]), 9)

    def test_stops(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            omni, out, n, _ = self.run_ok(d)
            cases = [((), {"omni_sha": "0" * 64, "expected_pass": n}, 3),
                     ((), {"omni_sha": sha(omni), "expected_pass": n + 1}, 3)]
            for _, kw, rc in cases:
                with self.assertRaises(X.Stop) as e:
                    X.extract(str(omni), out, **kw)
                self.assertEqual(e.exception.rc, rc)
            omni2 = d / "omni2.root"
            make_omni(omni2, drop=("MC_W",))
            with self.assertRaises(X.Stop) as e:
                X.extract(str(omni2), out, expected_pass=n, omni_sha=sha(omni2))
            self.assertEqual(e.exception.rc, 3)
            omni3 = d / "omni3.root"
            make_omni(omni3, w_shift=0.01)              # reco W inconsistent with q3: the recovery control fails
            with self.assertRaises(X.Stop) as e:
                X.extract(str(omni3), out, expected_pass=n, omni_sha=sha(omni3))
            self.assertEqual(e.exception.rc, 5)
            self.assertFalse((out / "q0_extract.npz").exists())

    def test_atime_change_stops(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            omni, out, n, _ = self.run_ok(d)
            real, calls = os.stat, []

            def stat(p, *a, **k):
                s = real(p, *a, **k)
                if str(p) == str(omni):
                    calls.append(1)
                    if len(calls) == 2:
                        return os.stat_result((s.st_mode, s.st_ino, s.st_dev, s.st_nlink, s.st_uid, s.st_gid, s.st_size,
                                               s.st_atime + 5, s.st_mtime, s.st_ctime))
                return s
            with mock.patch.object(X.os, "stat", stat):
                with self.assertRaises(X.Stop) as e:
                    X.extract(str(omni), out, expected_pass=n, omni_sha=sha(omni))
            self.assertEqual(e.exception.rc, 4)

    def test_only_the_signal_tree_is_opened(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            omni, out, n, _ = self.run_ok(d)
            opened, real_open = [], uproot.open

            class Spy:
                def __init__(self, f):
                    self.f = f

                def __getitem__(self, k):
                    opened.append(k)
                    return self.f[k]
            with mock.patch.object(uproot, "open", lambda *a, **k: Spy(real_open(*a, **k))):
                X.extract(str(omni), out, expected_pass=n, omni_sha=sha(omni))
            self.assertEqual(opened, ["mc_signal_reco"])
        src = (HERE / "q0_extract.py").read_text()
        self.assertNotIn("measured", src.replace('"measured" key', ""))


class Refusals(unittest.TestCase):
    def test_no_noatime_refuses(self):
        with tempfile.TemporaryDirectory() as t:
            with mock.patch.object(X, "NOATIME", None), mock.patch.object(X, "ALLOW_PLAIN_READ", False):
                with self.assertRaises(X.Stop) as e:
                    X.sha256_noatime(__file__)
                self.assertEqual(e.exception.rc, 9)
                self.assertEqual(X.main(["--omni", __file__, "--out", t]), 9)


if __name__ == "__main__":
    unittest.main()
