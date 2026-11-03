"""fd_1b_cvdenom (A2.1, S3 (d1)): the two writers' row gates, the phase space, checks (A)-(D) in both directions, and
the job end to end on a stand-in tree."""
import hashlib
import json
import math
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fd_1b_cvdenom as cd  # noqa: E402

EDGES = [np.array([0.0, 0.5, 1.0, 2.5]), np.array([1.5, 4.0, 8.0, 20.0]), np.array([0.0, 0.4, 100.0]),
         np.array([0.0, 0.6, 100.0]), np.array([0.0, 1.4, 100.0])]


def tree(n=3000, seed=0):
    rng = np.random.default_rng(seed)
    a = {"MC": rng.uniform(-0.1, 2.7, n), "MC_pz": rng.uniform(1.0, 21.0, n), "MC_eavail": rng.uniform(0, 2, n),
         "MC_q3": rng.uniform(0, 2, n), "MC_W": rng.uniform(0.5, 3, n), "w_truth": rng.uniform(0.2, 2.0, n)}
    a["MC"][:5] = np.nan
    a["w_truth"][5:10] = -0.1
    a["w_truth"][10:12] = 2e4
    a["MC_q3"][12:20] = np.nan                    # bank keeps these rows; the npz drops them
    return a


def bank_cv(a, pot):
    bank, _ = cd.row_sets(a, EDGES)
    return {k: np.asarray(a[s][bank], np.float32) for k, s in zip(cd.TD, cd.KEYS[:5])}, a["w_truth"][bank] * pot


class Gates(unittest.TestCase):
    def test_phase_space_is_u2ds_rule_at_its_edges(self):
        pz = np.array([5.0, 5.0, 5.0, 5.0])
        edge = 5.0 * math.tan(cd.MAX_MUON_THETA_RAD)
        pt = np.array([np.nextafter(edge, 0), edge, np.nextafter(edge, 9), 0.1])
        got = cd.in_phase_space(pt, pz, 0.0, 2.5, 1.5, 20.0)
        want = [math.atan2(a, b) < cd.MAX_MUON_THETA_RAD for a, b in zip(pt, pz)]
        self.assertEqual(got.tolist(), want)
        self.assertFalse(cd.in_phase_space(np.array([2.6]), np.array([10.0]), 0.0, 2.5, 1.5, 20.0)[0])
        self.assertTrue(cd.in_phase_space(np.array([2.5]), np.array([20.0]), 0.0, 2.5, 1.5, 20.0)[0])
        self.assertFalse(cd.in_phase_space(np.array([np.inf]), np.array([10.0]), 0.0, 2.5, 1.5, 20.0)[0])

    def test_the_two_writers_gates(self):
        a = tree()
        bank, npz = cd.row_sets(a, EDGES)
        self.assertFalse(bank[:12].any())                      # non-finite pt, w < 0, w >= 1e4
        self.assertTrue(np.all(npz <= bank))
        self.assertEqual(int(np.sum(bank & ~npz)), int(np.sum(bank[12:20])))
        self.assertGreater(int(np.sum(bank[12:20])), 0)
        a["w_truth"][30] = cd.W_MAX
        self.assertFalse(cd.row_sets(a, EDGES)[0][30])
        a["w_truth"][30] = 0.0
        a["MC"][30], a["MC_pz"][30] = 0.1, 10.0
        self.assertTrue(cd.row_sets(a, EDGES)[0][30])          # w = 0 is kept, as both writers keep it

    def test_the_phase_space_against_u2d_row_by_row(self):
        """The copy against the instrument (needs ROOT: root_6_28's suites; skipped elsewhere)."""
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "2d-unfolding"))
            import unfold_2d_omnifold_unbinned as u2d
        except ImportError:
            self.skipTest("u2d needs ROOT")
        self.assertEqual(cd.MAX_MUON_THETA_RAD, u2d.MAX_MUON_THETA_RAD)
        a = tree(20000, seed=4)
        edge = a["MC_pz"][:200] * math.tan(cd.MAX_MUON_THETA_RAD)
        a["MC"][:200] = np.where(np.arange(200) % 2, edge, np.nextafter(edge, 0))
        got = cd.in_phase_space(a["MC"], a["MC_pz"], EDGES[0][0], EDGES[0][-1], EDGES[1][0], EDGES[1][-1])
        want = [u2d.in_truth_phase_space(float(x), float(y), EDGES[0][0], EDGES[0][-1], EDGES[1][0], EDGES[1][-1])
                for x, y in zip(a["MC"], a["MC_pz"])]
        self.assertEqual(got.tolist(), want)


class Checks(unittest.TestCase):
    def test_a_and_b_hold_on_the_banks_own_rows(self):
        a, pot = tree(), 0.2
        cv, w = bank_cv(a, pot)
        denom = cd.histogram([np.asarray(cv[k], np.float64) for k in cd.TD], w, EDGES)
        rec, tdw = cd.checks(a, pot, cv, denom, EDGES)
        self.assertTrue(rec["A_coordinates_equal_row_by_row"])
        self.assertTrue(rec["B_histogram_equals_denom_nd"])
        self.assertTrue(np.array_equal(tdw, w))
        self.assertGreater(rec["bank_rows_not_npz"], 0)

    def test_a_fails_on_a_missing_or_moved_row(self):
        a, pot = tree(), 0.2
        cv, w = bank_cv(a, pot)
        denom = cd.histogram([np.asarray(cv[k], np.float64) for k in cd.TD], w, EDGES)
        short = {k: v[1:] for k, v in cv.items()}
        rec, _ = cd.checks(a, pot, short, denom, EDGES)
        self.assertFalse(rec["A_coordinates_equal_row_by_row"])
        self.assertFalse(rec["B_histogram_equals_denom_nd"])
        moved = dict(cv, td_pt=cv["td_pt"].copy())
        moved["td_pt"][3] += np.float32(0.01)
        rec, _ = cd.checks(a, pot, moved, denom, EDGES)
        self.assertFalse(rec["A_coordinates_equal_row_by_row"])
        self.assertEqual(rec["A_diff"]["td_pt"]["rows_differing"], 1)
        self.assertEqual(rec["A_diff"]["td_pt"]["first"][0][0], 3)
        self.assertEqual(rec["A_diff"]["td_q3"]["rows_differing"], 0)      # NaN rows compare equal
        self.assertEqual(cd.checks(a, pot, short, denom, EDGES)[0]["A_diff"], {"row_counts": [len(w), len(w) - 1]})

    def test_b_fails_on_a_denominator_one_ulp_away(self):
        a, pot = tree(), 0.2
        cv, w = bank_cv(a, pot)
        denom = cd.histogram([np.asarray(cv[k], np.float64) for k in cd.TD], w, EDGES)
        i = np.flatnonzero(denom)[0]
        off = denom.copy()
        off.flat[i] = np.nextafter(off.flat[i], np.inf)
        rec, _ = cd.checks(a, pot, cv, off, EDGES)
        self.assertTrue(rec["A_coordinates_equal_row_by_row"])
        self.assertFalse(rec["B_histogram_equals_denom_nd"])
        self.assertEqual(rec["B_diff"]["cells_differing"], 1)
        self.assertEqual(rec["B_diff"]["first"][0][0], int(i))
        self.assertNotIn("B_diff", cd.checks(a, pot, cv, denom, EDGES)[0])

    def test_c_reproduces_the_npz_writer_only_on_its_own_rows(self):
        a, pot = tree(), 0.2
        cv, w = bank_cv(a, pot)
        _, npz = cd.row_sets(a, EDGES)
        denom = cd.histogram([a[k][npz] for k in cd.KEYS[:5]], a["w_truth"][npz] * pot, EDGES)
        self.assertTrue(cd.checks(a, pot, cv, denom, EDGES)[0]["C_npz_writer_reproduced"])
        bank_denom = cd.histogram([np.asarray(cv[k], np.float64) for k in cd.TD], w, EDGES)
        self.assertTrue(np.allclose(bank_denom, denom, rtol=1e-6))  # histogramdd drops the NaN-extra rows
        self.assertFalse(cd.checks(a, pot, cv, denom * 1.001, EDGES)[0]["C_npz_writer_reproduced"])


class Detector(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.denom = np.random.default_rng(1).uniform(1, 2, (3, 3, 2, 2, 2))
        self.pins = {"files": {}}
        for b in cd.DETECTOR_BANDS:
            for i in (0, 1):
                p = self.tmp / f"{b}_{i}_denom_nd.npy"
                np.save(p, self.denom)
                self.pins["files"][str(p)] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        self.ps = mock.patch.object(cd, "NOATIME", 0)
        self.ps.start()

    def tearDown(self):
        self.ps.stop()

    def test_d_both_ways_and_the_pin(self):
        out = cd.detector_check(self.tmp, self.pins, self.denom)
        self.assertTrue(all(v["equal"] for v in out.values()))
        self.assertEqual(len(out), 8)
        p = self.tmp / "GEANT_Pion_1_denom_nd.npy"
        np.save(p, self.denom * 1.01)
        self.pins["files"][str(p)]["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
        out = cd.detector_check(self.tmp, self.pins, self.denom)
        self.assertEqual([k for k, v in out.items() if not v["equal"]], ["GEANT_Pion_1"])
        self.assertEqual(out["GEANT_Pion_1"]["diff"]["cells_differing"], self.denom.size)
        self.assertNotIn("diff", out["GEANT_Pion_0"])
        self.pins["files"][str(p)]["sha256"] = "0" * 64
        with self.assertRaisesRegex(cd.Refusal, "not the pinned file"):
            cd.detector_check(self.tmp, self.pins, self.denom)


class Job(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ps = mock.patch.object(cd, "NOATIME", 0)
        self.ps.start()
        cd.OPENED.clear()

    def tearDown(self):
        self.ps.stop()

    def build(self, a, pot, denom_override=None, det_scale=1.0):
        cv, w = bank_cv(a, pot)
        bank, det = self.tmp / "bank", self.tmp / "det"
        bank.mkdir(exist_ok=True)
        det.mkdir(exist_ok=True)
        np.savez(bank / "cv.npz", **cv)
        denom = cd.histogram([np.asarray(cv[k], np.float64) for k in cd.TD], w, EDGES) \
            if denom_override is None else denom_override
        np.savez(self.tmp / "in.npz", denom_nd=denom, nedges=5, **{f"edges_{k}": e for k, e in enumerate(EDGES)})
        files = {str(bank / "cv.npz"): {}}
        for b in cd.DETECTOR_BANDS:
            for i in (0, 1):
                np.save(det / f"{b}_{i}_denom_nd.npy", denom * det_scale)
                files[str(det / f"{b}_{i}_denom_nd.npy")] = {}
        for p in files:
            files[p]["sha256"] = hashlib.sha256(Path(p).read_bytes()).hexdigest()
        (self.tmp / "pins.json").write_text(json.dumps({"files": files}))
        (self.tmp / "u.root").write_bytes(b"stand-in")
        return bank, det

    def run_main(self, a, pot, **kw):
        bank, det = self.build(a, pot, **kw)
        par = lambda v: types.SimpleNamespace(member=lambda k: v)  # noqa: E731
        fake = {"dataPOTUsed": par(pot * 10.0), "mcPOTUsed": par(10.0),
                cd.TREE: types.SimpleNamespace(arrays=lambda keys, library: {k: a[k] for k in keys})}
        sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
        argv = ["--root", str(self.tmp / "u.root"), "--npz", str(self.tmp / "in.npz"), "--bank", str(bank),
                "--detector-dir", str(det), "--pins", str(self.tmp / "pins.json"), "--out", str(self.tmp / "o.json"),
                "--expect-pins-sha256", sha(self.tmp / "pins.json"), "--expect-npz-sha256", sha(self.tmp / "in.npz")]
        with mock.patch.dict(sys.modules, {"uproot": types.SimpleNamespace(open=lambda fh: fake, __version__="x")}):
            rc = cd.main(argv)
        return rc, json.loads((self.tmp / "o.json").read_text())

    def test_pass_writes_the_weights_and_their_digest(self):
        a = tree()
        rc, rec = self.run_main(a, 0.25)
        self.assertEqual((rc, rec["verdict"]), (0, "PASS"))
        w = np.load(self.tmp / "o.npy")
        bank, _ = cd.row_sets(a, EDGES)
        self.assertTrue(np.array_equal(w, a["w_truth"][bank] * 0.25))
        self.assertEqual(rec["tdw_cv_file_sha256"], hashlib.sha256((self.tmp / "o.npy").read_bytes()).hexdigest())
        self.assertEqual(rec["atime_moved"], [])

    def test_a_failed_check_writes_no_weights_and_goes_to_the_director(self):
        a = tree()
        rc, rec = self.run_main(a, 0.25, det_scale=1.001)
        self.assertEqual((rc, rec["verdict"]), (3, "TO_DIRECTOR"))
        self.assertFalse(rec["checks"]["D_all_equal"])
        self.assertFalse((self.tmp / "o.npy").exists())
        rc, rec = self.run_main(tree(), 0.25, denom_override=np.ones((3, 3, 2, 2, 2)))
        self.assertEqual(rc, 3)
        self.assertFalse(rec["checks"]["B_histogram_equals_denom_nd"])

    def test_digests_refuse(self):
        a = tree()
        bank, det = self.build(a, 0.25)
        argv = ["--root", str(self.tmp / "u.root"), "--npz", str(self.tmp / "in.npz"), "--bank", str(bank),
                "--detector-dir", str(det), "--pins", str(self.tmp / "pins.json"), "--out", str(self.tmp / "o.json"),
                "--expect-pins-sha256", "0" * 64, "--expect-npz-sha256", "0" * 64]
        with self.assertRaisesRegex(cd.Refusal, "pins file digest"):
            cd.main(argv)


if __name__ == "__main__":
    unittest.main()
