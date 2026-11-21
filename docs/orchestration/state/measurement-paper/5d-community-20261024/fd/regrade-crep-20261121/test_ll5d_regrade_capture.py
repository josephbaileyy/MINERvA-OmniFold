"""Stub tests of ll5d_regrade_capture.py: fake fd_1b_inv / ll5d / ll5d_b modules and fake inputs in a temp dir (no study
file is read). Checked: the success path writes four captures and a manifest that regrade_crep.load_capture reads back;
a product pin mismatch, a missing toy, a wrong pin on S1 or the constraint, a wrong list digest, and a moved atime are
each a STOP with no capture kept.

    python3 -B -m unittest -v test_ll5d_regrade_capture.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ll5d_regrade_capture as cap  # noqa: E402
import regrade_crep as rc  # noqa: E402
import fd_1b_null as fn  # noqa: E402

SEEDS = {"g18": range(10, 13), "ar23": range(20, 23)}
READINGS = ("minus2", "all")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Fixture:
    def __init__(self, td: Path, n_toys=3):
        self.td = td
        self.deploy = td / "deploy"
        (self.deploy / "nd-unfolding").mkdir(parents=True)
        self.staged = td / "staged"
        (self.staged / "s1").mkdir(parents=True)
        self.s1 = self.staged / "s1" / "s1_assembly.npz"
        self.s1.write_bytes(b"s1")
        self.constraint = td / "constraint.txt"
        self.constraint.write_bytes(b"flux")
        self.unfolds = td / "U"
        self.unfolds.mkdir()
        rows = []
        for t in ("g18", "ar23"):
            p = self.unfolds / f"ll5d_{t}_central_T.npz"
            p.write_bytes(f"c{t}".encode())
            rows.append(("null_roles", sha(p), str(p)))
            for rd in READINGS:
                for s in SEEDS[t]:
                    p = self.unfolds / f"ll5d_{t}_toy_{rd}_{s}.npz"
                    p.write_bytes(f"{t}{rd}{s}".encode())
                    rows.append(("toys", sha(p), str(p)))
        self.list = td / "list.tsv"
        self.list.write_text("".join("\t".join(r) + "\n" for r in rows))
        self.out = td / "out"
        self.n_toys = n_toys

    def modules(self):
        inv = types.ModuleType("fd_1b_inv")
        inv.sha256_noatime = lambda p: sha(p)
        ll5d = types.ModuleType("ll5d")
        ll5d.READINGS = READINGS
        ll5d.TOY_SEEDS = SEEDS
        lb = types.ModuleType("ll5d_b")
        n = self.n_toys

        def setup(ns):
            assert ns.flux_constraint == self.constraint and ns.unfolds == self.unfolds
            return {"f": np.arange(1.0, 17.0)}, np.eye(16), None, None, np.ones(2)

        def remade(unfolds, t, s1, U, w, frac, rd):
            law = fn.Discrete.two_point(np.full(16, 0.1))
            return {"X_T": np.arange(1.0, 17.0) * 1.01, "C_T": np.eye(16) * 2.0, "C_e": np.eye(16), "C_model_abs":
                    np.eye(16) * 0.5, "gauss": np.eye(16) * 1.5 - law.cov(), "laws": [("lat:X", law, None)]}

        def toy_errors(unfolds, t, rd, U, rm, f):
            return np.ones((n, 16)) * 0.1, [], np.zeros((n, 16)), []
        lb.setup, lb.remade, lb.toy_errors = setup, remade, toy_errors
        return {"fd_1b_inv": inv, "ll5d": ll5d, "ll5d_b": lb}

    def argv(self):
        return ["--deploy", str(self.deploy), "--staged", str(self.staged), "--unfolds", str(self.unfolds),
                "--constraint", str(self.constraint), "--list", str(self.list), "--out", str(self.out)]


class Capture(unittest.TestCase):
    def run_cap(self, fx, n_toys=300, **patch):
        fx.n_toys = n_toys
        pins = {"S1_SHA": sha(fx.s1), "CONSTRAINT_SHA": sha(fx.constraint), "LIST_SHA": sha(fx.list)}
        pins.update(patch)
        with mock.patch.dict(sys.modules, fx.modules()), \
                mock.patch.object(cap, "check_deploy", return_value={"head": cap.M_L, "bound_ok": []}), \
                mock.patch.multiple(cap, **pins):
            return cap.main(fx.argv())

    def test_success_and_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            fx = Fixture(Path(td))
            self.assertEqual(self.run_cap(fx), 0)
            man = json.loads((fx.out / "capture-manifest.json").read_text())
            self.assertEqual(sorted(man["outputs"]), sorted(f"capture_{t}_{rd}.npz" for t in ("g18", "ar23")
                                                             for rd in READINGS))
            self.assertEqual(man["atime_moved"], [])
            d = rc.load_capture(fx.out / "capture_g18_minus2.npz")
            self.assertEqual(d["E"].shape, (300, 16))
            self.assertEqual(len(d["laws"]), 1)
            np.testing.assert_array_equal(d["laws"][0].cov() + d["gauss"], np.eye(16) * 1.5)
            for k, v in man["outputs"].items():
                self.assertEqual(sha(fx.out / k), v)

    def test_product_pin_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as td:
            fx = Fixture(Path(td))
            p = fx.unfolds / "ll5d_g18_toy_all_11.npz"
            p.write_bytes(b"changed")
            self.assertEqual(self.run_cap(fx), 8)
            self.assertTrue((fx.out / "STOP.json").exists())
            self.assertEqual(list(fx.out.glob("capture_*.npz")), [])

    def test_wrong_pins_stop(self):
        for k in ("S1_SHA", "CONSTRAINT_SHA", "LIST_SHA"):
            with tempfile.TemporaryDirectory() as td:
                fx = Fixture(Path(td))
                self.assertEqual(self.run_cap(fx, **{k: "0" * 64}), 8, k)
                self.assertEqual(list(fx.out.glob("capture_*.npz")), [], k)

    def test_missing_toy_row_stops(self):
        with tempfile.TemporaryDirectory() as td:
            fx = Fixture(Path(td))
            lines = fx.list.read_text().splitlines(keepends=True)
            fx.list.write_text("".join(l for l in lines if "toy_minus2_10" not in l))
            self.assertEqual(self.run_cap(fx), 8)

    def test_wrong_shape_stops(self):
        with tempfile.TemporaryDirectory() as td:
            fx = Fixture(Path(td))
            self.assertEqual(self.run_cap(fx, n_toys=299), 8)
            self.assertEqual(list(fx.out.glob("capture_*.npz")), [])

    def test_moved_atime_stops(self):
        with tempfile.TemporaryDirectory() as td:
            fx = Fixture(Path(td))
            real = cap.stat4
            calls = {"n": 0}

            def stat4(p):
                s = real(p)
                calls["n"] += 1
                if calls["n"] > 1000 or (p.endswith("constraint.txt") and calls.get("seen")):
                    s[2] += 1
                if p.endswith("constraint.txt"):
                    calls["seen"] = True
                return s
            with mock.patch.object(cap, "stat4", side_effect=stat4):
                self.assertEqual(self.run_cap(fx), 8)
            self.assertIn("atime moved", json.loads((fx.out / "STOP.json").read_text())["stop"])
            self.assertEqual(list(fx.out.glob("capture_*.npz")), [])

    def test_out_exists_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            fx = Fixture(Path(td))
            fx.out.mkdir()
            self.assertEqual(self.run_cap(fx), 2)


if __name__ == "__main__":
    unittest.main()
