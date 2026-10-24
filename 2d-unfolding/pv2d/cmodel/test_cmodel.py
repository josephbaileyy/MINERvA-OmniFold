"""Tests for build_cmodel (numpy only): run with `python3 -m unittest test_cmodel -v` from this directory."""
import copy
import json
import os
import tempfile
import unittest

import numpy as np

import build_cmodel as B

HERE = os.path.dirname(os.path.abspath(__file__))
PV2D = os.path.dirname(HERE)


def load(rel):
    with open(os.path.join(PV2D, rel)) as f:
        return json.load(f)


class Synthetic(unittest.TestCase):
    def setUp(self):
        self.S = np.random.default_rng(3).normal(0, 0.05, (3, 40))

    def test_form_rank_and_psd(self):
        C = B.cmodel(self.S)
        np.testing.assert_allclose(C, self.S.T @ self.S, rtol=0, atol=1e-16)
        self.assertEqual(np.linalg.matrix_rank(C), 3)
        self.assertGreater(np.linalg.eigvalsh(C).min(), -1e-15)
        np.testing.assert_array_equal(np.diag(C), (self.S ** 2).sum(axis=0))

    def test_two_vertices_give_rank_two(self):
        self.assertEqual(np.linalg.matrix_rank(B.cmodel(self.S[:2])), 2)

    def test_m2_total_is_never_below_the_envelope_total(self):
        t = B.totals(self.S, np.full(40, 0.06))
        self.assertTrue(np.all(t["total_m2"] >= t["total_envelope"]))
        self.assertTrue(np.all(t["sqrt_diag"] >= t["h"]))

    def test_absolute_scaling(self):
        x = np.linspace(1.0, 3.0, 40)
        C = B.cmodel(self.S)
        np.testing.assert_allclose(B.absolute(C, x), np.diag(x) @ C @ np.diag(x), rtol=1e-15)

    def test_factor_refuses_another_arm_a_short_array_and_a_stale_envelope(self):
        R = {"arm": "refined", "cells": list(range(40)),
             "vertices": {v: {"shift": self.S[i].tolist()} for i, v in enumerate(B.VERTICES)},
             "envelope": {"h": np.abs(self.S).max(axis=0).tolist()}}
        np.testing.assert_array_equal(B.factor(R), self.S)
        bad = [("arm", lambda r: r.update(arm="a")),
               ("short", lambda r: r["vertices"]["nuwro"].update(shift=self.S[1][:-1].tolist())),
               ("edited", lambda r: r["vertices"]["gibuu"]["shift"].__setitem__(0, 0.5))]
        for name, mutate in bad:
            r = copy.deepcopy(R)
            mutate(r)
            with self.subTest(name), self.assertRaises(ValueError):
                B.factor(r)

    def test_coverage_counts(self):
        S = np.array([[0.0, 0.03, 0.0, 0.2], [0.05, 0.01, 0.0, 0.0], [0.0, 0.04, 0.0, 0.0]])
        pc = {"vertex": "nuwro", "min_abs_bias": 0.01, "bias_cells": [0.04, -0.045, 0.005, 0.1]}
        c = B.coverage(S, pc)
        self.assertEqual(c["cells"], 3)                     # the 0.005 cell is below the PC's |bias| floor
        self.assertEqual(c["reach"], {"own_vertex_shift": 1, "leave_own_vertex_out": 2, "sqrt_diag_in_sample": 3})


class LoadQ(unittest.TestCase):
    """load_q fires on each mismatch and stays silent on a consistent pair."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "q.npz")
        x = np.array([2.0, 4.0, 5.0])
        Q = np.diag((0.1 * x) ** 2)
        np.savez(self.path, Q=Q, x=x, cells=np.array([7, 8, 9]))
        self.R = {"cells": [7, 8, 9], "sigma_Q": {"cells": [0.1, 0.1, 0.1]},
                  "inputs": {"Q": {"sha256": B.L.sha256_path(self.path)}}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_consistent(self):
        _, _, sig = B.load_q(self.path, self.R)
        np.testing.assert_allclose(sig, 0.1)

    def test_refusals(self):
        for key, val in (("sha", "0" * 64), ("cells", [7, 8, 10]), ("sigma", [0.1, 0.1, 0.11])):
            R = copy.deepcopy(self.R)
            if key == "sha":
                R["inputs"]["Q"]["sha256"] = val
            elif key == "cells":
                R["cells"] = val
            else:
                R["sigma_Q"]["cells"] = val
            with self.subTest(key), self.assertRaises(ValueError):
                B.load_q(self.path, R)


class Committed(unittest.TestCase):
    """The committed cmodel_2d.json against the committed readouts and projections (Q itself is not in git; its
    sigma_Q is, in the readout)."""

    @classmethod
    def setUpClass(cls):
        cls.X = load("readouts/readout_ref.json")
        cls.A = load("readouts/readout_a.json")
        cls.M = load("cmodel/cmodel_2d.json")
        cls.I = B.RT.Inputs(os.path.join(PV2D, "ratios/projections.json"), os.path.join(PV2D, "ratios"))

    def test_derived_fields_recompute_from_the_factor(self):
        S, sig_q = np.array(self.M["S"]), np.array(self.M["sigma_Q"])
        t = B.totals(S, sig_q)
        for k in ("sqrt_diag", "total_m2"):
            np.testing.assert_allclose(self.M[k], t[k], rtol=1e-15, atol=0)
        for k in ("sqrt_diag", "total_m2", "h", "total_envelope"):
            self.assertEqual(self.M["summary"][k], B.quantiles(t[k]))
        C = B.cmodel(S)
        near = self.I.near["h"]
        self.assertEqual(self.M["post_hoc"]["cells"], int(near.sum()))
        self.assertAlmostEqual(self.M["post_hoc"]["trace_share"], np.diag(C)[near].sum() / np.trace(C), places=14)
        self.assertEqual(self.M["coverage_vs_pc_bias"], B.coverage(S, self.A["controls"]["PC"]["primary"]))

    def test_inputs_check_refuses_crossed_readouts(self):
        with self.assertRaises(SystemExit):
            self.I.check(self.A, "refined")
        X = copy.deepcopy(self.X)
        X["ratios_projection_sha256"] = "0" * 64
        with self.assertRaises(SystemExit):
            self.I.check(X, "refined")

    def test_inputs(self):
        self.assertEqual(self.M["inputs"]["readout"]["sha256"],
                         B.L.sha256_path(os.path.join(PV2D, "readouts/readout_ref.json")))
        self.assertEqual(self.M["cells"], self.X["cells"])
        np.testing.assert_array_equal(np.array(self.M["S"]), B.factor(self.X))
        self.assertEqual(self.M["sigma_Q"], self.X["sigma_Q"]["cells"])

    def test_matrix_sha_rebuilds_from_the_factor(self):
        self.assertEqual(B.matrix_sha256(B.cmodel(np.array(self.M["S"]))), self.M["matrix_sha256"]["C_model"])

    def test_rank_and_label(self):
        self.assertEqual(self.M["rank"], 3)
        self.assertEqual(self.M["label"], "generator-shape model dependence; not a calibrated bound")

    def test_numbers_the_report_quotes(self):
        s = self.M["summary"]
        self.assertAlmostEqual(s["total_envelope"]["median"], 0.0769, places=4)   # the director's 7.69 %
        self.assertAlmostEqual(s["total_envelope"]["p84_weibull"], 0.1240, places=4)
        self.assertAlmostEqual(s["total_m2"]["median"], 0.0795, places=4)
        self.assertAlmostEqual(s["sqrt_diag"]["median"], 0.0371, places=4)
        self.assertAlmostEqual(s["total_m2"]["p84"], 0.1300, places=4)
        self.assertEqual(self.M["post_hoc"]["cells"], 52)
        self.assertAlmostEqual(self.M["post_hoc"]["trace_share"], 0.594, places=3)
        self.assertAlmostEqual(self.M["post_hoc"]["sqrt_diag_rest"]["median"], 0.0305, places=4)
        self.assertAlmostEqual(self.M["post_hoc"]["total_m2_rest"]["median"], 0.0728, places=4)
        self.assertEqual(self.M["coverage_vs_pc_bias"]["cells"], 127)
        self.assertEqual(self.M["coverage_vs_pc_bias"]["reach"],
                         {"own_vertex_shift": 67, "leave_own_vertex_out": 72, "sqrt_diag_in_sample": 116})
        shares = self.M["trace_share_by_vertex"]
        self.assertEqual([round(shares[v], 3) for v in B.VERTICES], [0.142, 0.566, 0.292])
        np.testing.assert_allclose(self.M["singular_values_S"], [0.6135, 0.4333, 0.2830], atol=5e-5)


if __name__ == "__main__":
    unittest.main()
