#!/usr/bin/env python3
"""Tests for vhr_wtruth_check.py on synthetic npz files in the 5D input's format (unittest; numpy only).

Each refusal and each gated set is tested in the direction it acts. The real h2_definition.json is used, so the
fine-map check runs against the pinned record."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vhr_wtruth_check as m  # noqa: E402

# true coordinates (pT, ppar, Eavail, q3, W): one row per case
IN_OMEGA = [0.3, 3.0, 0.3, 0.5, 1.2]       # pT < 0.7 but q3 < 2: inside Ω
EXCLUDED = [0.3, 3.0, 0.3, 3.0, 1.2]       # pT < 0.7, q3 >= 2, W < 1.8: the unreported region
OUT_GRID = [-9999.0] * 5                   # the input sample's gen sentinel


def make_npz(d, rows, pass_truth, w_truth):
    p = Path(d) / "inputs.npz"
    np.savez(p, MCgen=np.asarray(rows, float), pass_truth=np.asarray(pass_truth, bool),
             w_truth=np.asarray(w_truth, float), measured=np.zeros(3))
    return p, hashlib.sha256(p.read_bytes()).hexdigest()


class Check(unittest.TestCase):
    def run_check(self, rows, pt, wt):
        with tempfile.TemporaryDirectory() as d:
            p, sha = make_npz(d, rows, pt, wt)
            return m.check(p, expect_npz_sha=sha)

    def test_omega_is_the_pinned_fine_map(self):
        d = json.loads(m.H2_DEF.read_text())
        omega, sha = m.omega_mask(d)
        self.assertEqual(sha, d["fine_map_sha256_int32le"])
        self.assertEqual(int(omega.size - omega.sum()), 8 * 16 * 7 * 1 * 3)   # pT<0.7 x all ppar x all Eavail x q3>=2 x W<1.8

    def test_pass(self):
        r = self.run_check([IN_OMEGA, EXCLUDED, OUT_GRID], [True, True, False], [1.0, 2.0, 0.0])
        self.assertEqual(r["verdict"], "PASS")
        self.assertEqual(r["sets"]["shares"]["rows"], 1)
        self.assertEqual(r["sets"]["tilt"]["rows"], 1)
        self.assertEqual(r["sets"]["all"]["rows"], 3)

    def test_negative_in_shares_fails(self):
        r = self.run_check([IN_OMEGA, IN_OMEGA], [True, True], [1.0, -0.5])
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(r["sets"]["shares"]["negative"], 1)

    def test_nonfinite_in_tilt_only_fails(self):
        # a row failing pass_truth is outside the shares set but inside the tilt population
        r = self.run_check([IN_OMEGA, IN_OMEGA], [True, False], [1.0, np.nan])
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(r["sets"]["shares"]["nonfinite"], 0)
        self.assertEqual(r["sets"]["tilt"]["nonfinite"], 1)

    def test_bad_weights_outside_omega_are_descriptive(self):
        r = self.run_check([IN_OMEGA, EXCLUDED, OUT_GRID], [True, True, True], [1.0, -3.0, np.inf])
        self.assertEqual(r["verdict"], "PASS")
        self.assertEqual(r["sets"]["all"]["negative"], 1)
        self.assertEqual(r["sets"]["all"]["nonfinite"], 1)

    def test_npz_sha_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p, _ = make_npz(d, [IN_OMEGA], [True], [1.0])
            with self.assertRaises(m.Refusal):
                m.check(p, expect_npz_sha="0" * 64)

    def test_h2def_sha_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p, sha = make_npz(d, [IN_OMEGA], [True], [1.0])
            with self.assertRaises(m.Refusal):
                m.check(p, expect_npz_sha=sha, expect_h2def_sha="0" * 64)

    def test_tampered_map_refused(self):
        with tempfile.TemporaryDirectory() as d:
            h2 = json.loads(m.H2_DEF.read_text())
            h2["h2_to_reporting_cell"][2] = 0          # report box 2: the built map no longer matches the record's sha
            h2["unreported_boxes"] = [[6], [10], [14]]
            q = Path(d) / "h2.json"
            q.write_text(json.dumps(h2))
            p, sha = make_npz(d, [IN_OMEGA], [True], [1.0])
            with self.assertRaises(m.Refusal):
                m.check(p, expect_npz_sha=sha, h2def_path=q,
                        expect_h2def_sha=hashlib.sha256(q.read_bytes()).hexdigest())

    def test_missing_key_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "inputs.npz"
            np.savez(p, MCgen=np.asarray([IN_OMEGA], float), pass_truth=np.asarray([True]))
            with self.assertRaises(m.Refusal):
                m.check(p, expect_npz_sha=hashlib.sha256(p.read_bytes()).hexdigest())

    def test_main_exit_codes_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p, sha = make_npz(d, [IN_OMEGA], [True], [-1.0])
            old = m.NPZ_SHA256
            try:
                m.check.__defaults__ = (sha,) + m.check.__defaults__[1:]
                out = Path(d) / "rec.json"
                self.assertEqual(m.main(["--npz", str(p), "--out", str(out)]), 3)
                self.assertEqual(json.loads(out.read_text())["verdict"], "FAIL")
                with self.assertRaises(FileExistsError):
                    m.main(["--npz", str(p), "--out", str(out)])
                m.check.__defaults__ = ("0" * 64,) + m.check.__defaults__[1:]
                self.assertEqual(m.main(["--npz", str(p), "--out", str(Path(d) / "r2.json")]), 2)
            finally:
                m.check.__defaults__ = (old,) + m.check.__defaults__[1:]


if __name__ == "__main__":
    unittest.main(verbosity=2)
