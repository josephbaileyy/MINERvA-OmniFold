"""cov2d_readouts: each section 6 readout against a hand computation, the fixed 0.5 sigma_c reading, the GENIE + MEC
reading, C2's product composition, and the cross-terms CLI on the synthetic $UNI of test_cov2d_pseudo (uproot only).
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_readouts
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import cov2d as c  # noqa: E402
import cov2d_readouts as ro  # noqa: E402

N = 205


class Pure(unittest.TestCase):
    def setUp(self):
        self.r = np.random.default_rng(8)

    def test_product_compose_is_c2s(self):
        cv = np.array([1.0, 2.0, -1.0, 0.0, 1.5])
        u1 = np.array([1.2, 1.0, 2.0, 1.0, -0.3])
        u2 = np.array([0.9, 3.0, 1.0, 1.0, 1.0])
        got = ro.product_compose(cv, [u1, u2])
        np.testing.assert_allclose(got[:2], cv[:2] * (u1[:2] / cv[:2]) * (u2[:2] / cv[:2]), rtol=1e-15)
        self.assertEqual(list(got[2:]), [0.0, 0.0, 0.0])     # cv <= 0, cv = 0, a drawn universe <= 0
        np.testing.assert_allclose(ro.product_compose(cv[:2], [u1[:2]]), u1[:2], rtol=1e-15)

    def test_spread_bias_realization(self):
        E = self.r.normal(size=(300, 4))
        C = np.diag([2.0, 1.0, 1.0, 1.0])
        Cm = np.diag([1.0, 0.0, 0.0, 0.0])
        sp = ro.spread_alone(E, C, Cm)
        self.assertAlmostEqual(sp["p_hat"][0], float(np.mean(np.abs(E[:, 0]) <= 1.0)))
        self.assertAlmostEqual(ro.bias(E, np.ones(4))[2], float(E[:, 2].mean()))
        rc_ = ro.realization_check(np.array([1.0, 2.0]), np.array([1.5, 2.0]), np.array([0.5, 1.0]))
        self.assertEqual(rc_["per_cell_sigma"], [-1.0, 0.0])

    def test_predicted_offset(self):
        x = self.r.uniform(1, 2, N)
        bands = {b: x + self.r.normal(0, 0.05, (c.BANDS[b], N)) for b in c.ORDER}
        w = self.r.uniform(0.5, 1.5, 100)
        want = np.zeros(N)
        for b in c.ORDER:
            p = w / w.sum() if b == c.FLUX else np.full(c.BANDS[b], 1 / c.BANDS[b])
            want += sum(pi * (xu - x) for pi, xu in zip(p, bands[b]))
        np.testing.assert_allclose(ro.predicted_offset(bands, w, x), -want, rtol=1e-10, atol=1e-14)

    def clip_fixture(self, m_seen_value):
        rep = np.arange(224)[np.sort(self.r.choice(224, N, replace=False))]
        if c.OUTLIER_CELL not in rep:
            rep[-1] = c.OUTLIER_CELL
            rep = np.sort(rep)
        T = 4
        z = {k: np.zeros((T + 1, 224)) for k in ("S", "m_seen", "N", "m_all", "neg_reco_background", "S_reco")}
        z["S"][:] = 100.0
        z["N"][:] = 200.0
        z["m_seen"][:] = m_seen_value
        z["m_all"][:] = 4.0
        z["S_reco"][:] = 50.0
        z["neg_reco_background"][:] = -1.0
        z["S"][:, rep[3]] = 0.0              # one missing cell
        return z, rep, T

    def test_clipping_residual_and_its_reading(self):
        z, rep, T = self.clip_fixture(m_seen_value=10.0)   # R = 0.1 - 0.02 = 0.08
        x_true, sigma = np.full((T, N), 1.0), np.full(N, 0.1)   # in sigma_c: 0.8 > 0.5
        flagged = [int(rep[0]), int(rep[3])]
        out = ro.clipping_residual(z, list(range(T)), rep, x_true, sigma, np.eye(N) * 0.01, flagged, "G18")
        self.assertAlmostEqual(out["median_abs_R_sigma"][0], 0.8)
        self.assertEqual(out["missing_per_cell"][3], T)
        self.assertEqual(out["reading_fires_in"], [int(rep[0])])     # the missing cell cannot fire
        self.assertEqual(out["reading"][int(rep[0])], "the clipping may explain this cell's flag")
        self.assertEqual(out["c2_prediction_sigma_Q"], 0.043)
        self.assertAlmostEqual(out["background_offset_sigma"]["median_abs"], (1.0 / 50.0) / 0.1)
        self.assertEqual(out["outlier_cell"]["cell"], 216)
        z2, rep2, T2 = self.clip_fixture(m_seen_value=2.5)  # R = 0.025 - 0.02 = 0.005 -> 0.05 sigma
        out2 = ro.clipping_residual(z2, list(range(T2)), rep2, np.full((T2, N), 1.0), np.full(N, 0.1),
                                    np.eye(N) * 0.01, [int(rep2[0])], "AR23")
        self.assertEqual(out2["reading_fires_in"], [])


class LeaveOutMEC(unittest.TestCase):
    def test_reading_when_c_t_covers_and_c_t_minus_flags(self):
        import test_cov2d_null as tn
        blocks, bands, minos_x, w = tn.fixture()
        G = blocks["C_stat"] / 0.4
        blocks["C_T_minus"] = blocks["C_T"] - blocks["C_model_abs"] + 0.01 * G
        r = np.random.default_rng(1)
        L = np.linalg.cholesky(blocks["C_T"] + np.eye(N) * 1e-12)
        E = 1.5 * (L @ r.standard_normal((N, 300))).T       # wider than C_T- by construction: C_T- must flag
        grade_ct = {"verdict": "COVERS", "cell_flag": [False] * N}
        out = ro.leave_out_mec(E, blocks, bands, minos_x, w, grade_ct, list(range(N)), n_mc=20_000)
        self.assertTrue(out["changes_no_verdict"])
        self.assertEqual(out["grade"]["verdict"], "UNDER-COVERS")
        self.assertTrue(out["flagged_under_minus_not_under_C_T"])
        self.assertEqual(out["reading"], ro.GENIE_MEC_READING.format(cells=out["flagged_under_minus_not_under_C_T"]))
        out2 = ro.leave_out_mec(E, blocks, bands, minos_x, w, {"verdict": "UNDER-COVERS", "cell_flag": [False] * N},
                                list(range(N)), n_mc=20_000)
        self.assertNotIn("reading", out2)                    # the reading needs C_T to cover


class CrossTermsCLI(unittest.TestCase):
    def test_runs_over_600_draws_and_matches_a_hand_first_order_histogram(self):
        import test_cov2d_pseudo as tp
        import cov2d_pseudo as ps
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True), \
                mock.patch.object(ps, "read_pot", lambda f: tp.POT):
            d = Path(td)
            truth, sig, bkg = tp.build(d)
            g18 = (d / "prep/bridged/genie_v3_g18.json").read_text()
            (d / "prep/bridged/genie_v3_ar23.json").write_text(g18)
            import time
            fut = time.time() + 86400
            os.utime(d / "prep/bridged/genie_v3_ar23.json", (fut, os.stat(d / "prep/bridged/genie_v3_ar23.json").st_mtime))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = ro.main(["cross-terms", "--out", str(d / "x.json"), "--uni", str(d / "uni.root"),
                                "--prep", str(d / "prep"), "--constraint", str(d / "constraint.txt"), "--no-pins"])
            self.assertEqual(code, 0, buf.getvalue())
            rec = json.loads((d / "x.json").read_text())
            self.assertEqual({t: v["n"] for t, v in rec["draws"].items()}, {"G18": 300, "AR23": 300})
            self.assertEqual(rec["atime_moved"], [])
            self.assertGreater(rec["draws"]["G18"]["max_abs"], 0.0)


if __name__ == "__main__":
    unittest.main()
