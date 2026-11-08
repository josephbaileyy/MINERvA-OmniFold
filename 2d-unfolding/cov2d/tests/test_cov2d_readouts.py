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

    def clip_fixture(self, m_seen_value, truth="G18"):
        rep = np.arange(224)[np.sort(self.r.choice(224, N, replace=False))]
        if c.OUTLIER_CELL not in rep:
            rep[-1] = c.OUTLIER_CELL
            rep = np.sort(rep)
        T = len(c.TOY_SEEDS[truth])
        z = {k: np.zeros((T + 1, 224)) for k in ("S", "m_seen", "N", "m_all", "neg_reco_background", "S_reco")}
        z["seeds"] = np.array(list(c.TOY_SEEDS[truth]) + [c.REALIZATION_SEED[truth]])
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
        z2, rep2, T2 = self.clip_fixture(m_seen_value=2.5, truth="AR23")  # R = 0.025 - 0.02 = 0.005 -> 0.05 sigma
        out2 = ro.clipping_residual(z2, list(range(T2)), rep2, np.full((T2, N), 1.0), np.full(N, 0.1),
                                    np.eye(N) * 0.01, [int(rep2[0])], "AR23")
        self.assertEqual(out2["reading_fires_in"], [])

    def test_clipping_residual_on_varying_inputs_against_a_hand_computation(self):
        import fd_1b_null as nl
        z, rep, T = self.clip_fixture(m_seen_value=0.0)
        r = self.r
        z["S"][:] = r.uniform(50, 150, z["S"].shape)
        z["N"][:] = r.uniform(150, 250, z["N"].shape)
        z["m_seen"][:] = r.uniform(0, 12, z["m_seen"].shape)
        z["m_all"][:] = r.uniform(0, 6, z["m_all"].shape)
        o = list(rep).index(c.OUTLIER_CELL)
        gone = r.choice(T, 120, replace=False)               # 40% of the outlier's toys missing, the rest large
        z["S"][gone, c.OUTLIER_CELL] = 0.0
        z["m_seen"][:T, c.OUTLIER_CELL] = r.uniform(20, 40, T)
        x_true, sigma = r.uniform(0.5, 2.0, (T, N)), r.uniform(0.05, 0.2, N)
        A = r.normal(size=(N, N)) * 0.01
        C_T = A @ A.T + np.diag(sigma ** 2)
        out = ro.clipping_residual(z, list(range(T)), rep, x_true, sigma, C_T, [], "G18")
        S, Nn = z["S"][:T][:, rep], z["N"][:T][:, rep]
        R = z["m_seen"][:T][:, rep] / np.where(S > 0, S, np.nan) - z["m_all"][:T][:, rep] / Nn
        Rs = np.abs(R * x_true / sigma)
        want = [float(np.median(Rs[~np.isnan(Rs[:, i]), i])) for i in range(N)]
        np.testing.assert_allclose(out["median_abs_R_sigma"], want, rtol=1e-12)
        col = Rs[:, o][~np.isnan(Rs[:, o])]
        self.assertAlmostEqual(out["outlier_cell"]["max_abs_R_sigma"], float(col.max()), places=12)
        self.assertAlmostEqual(out["outlier_cell"]["median_abs_R_sigma"], float(np.median(col)), places=12)
        self.assertEqual(out["outlier_cell"]["missing"], 120)
        self.assertGreater(out["outlier_cell"]["max_abs_R_sigma"], out["outlier_cell"]["median_abs_R_sigma"])
        zeros = np.median(np.nan_to_num(Rs[:, o]))           # a missing R_c read as 0 would give this instead
        self.assertGreater(abs(out["outlier_cell"]["median_abs_R_sigma"] - zeros), 0.5)
        vec = np.nan_to_num(R * x_true)
        chi = np.array([float(v @ np.linalg.solve(C_T, v)) for v in vec])   # C_T is full rank here
        np.testing.assert_allclose(out["coherent_offset"]["median"], np.median(chi), rtol=1e-8)
        np.testing.assert_allclose(out["coherent_offset"]["max"], chi.max(), rtol=1e-8)
        keep = np.setdiff1d(np.arange(T), gone)
        self.assertEqual(out["coherent_offset"]["complete_toys"], keep.size)
        np.testing.assert_allclose(out["coherent_offset"]["median_complete"], np.median(chi[keep]), rtol=1e-8)
        self.assertEqual(nl.chi2_nonnull(vec, C_T)[1], N)

    def test_refuses_rows_that_are_not_the_truths_toys_in_seed_order(self):
        z, rep, T = self.clip_fixture(m_seen_value=10.0)
        args = (rep, np.full((T, N), 1.0), np.full(N, 0.1), np.eye(N) * 0.01, [], "G18")
        for rows in (list(range(1, T + 1)), list(range(T))[::-1]):
            with self.subTest(rows[:2]), self.assertRaises(c.Refusal):
                ro.clipping_residual(z, rows, *args)
        with self.assertRaises(c.Refusal):                                   # G18's rows read as AR23's
            ro.clipping_residual(z, list(range(T)), *args[:-1], "AR23")

    def test_refuses_cells_without_the_outlier(self):
        z, rep, T = self.clip_fixture(m_seen_value=10.0)
        rep = np.array([x for x in range(224) if x != c.OUTLIER_CELL][:N])
        with self.assertRaises(c.Refusal):
            ro.clipping_residual(z, list(range(T)), rep, np.full((T, N), 1.0), np.full(N, 0.1), np.eye(N) * 0.01,
                                 [], "G18")


class LeaveOutMEC(unittest.TestCase):
    """1B's §5.4 text, verbatim (fd_1b_mc.py:803-808), on a C_T- null built by cov2d_null.null_at_T."""
    @classmethod
    def setUpClass(cls):
        import cov2d_null as cn
        import test_cov2d_null as tn
        cls.blocks, bands, minos_x, w = tn.fixture()
        G = cls.blocks["C_stat"] / 0.4
        cls.blocks["C_T_minus"] = cls.blocks["C_T"] - cls.blocks["C_model_abs"] + 0.01 * G
        cls.null_minus = cn.null_at_T(cls.blocks, bands, minos_x, w, n_mc=20_000)["null_minus"]

    def draws(self, C, scale, seed=1):
        r = np.random.default_rng(seed)
        L = np.linalg.cholesky(C + np.eye(N) * 1e-12)
        return scale * (L @ r.standard_normal((N, 300))).T

    def test_c_t_covers_and_c_t_minus_flags(self):
        E = self.draws(self.blocks["C_T"], 1.5)               # wider than C_T- by construction: C_T- must flag
        cells = list(range(7, 7 + N))
        out = ro.leave_out_mec(E, self.blocks, self.null_minus, {"verdict": "COVERS"}, cells)
        g = out["grade"]
        self.assertTrue(out["changes_no_verdict"])
        self.assertEqual(g["verdict"], "UNDER-COVERS")
        hit = [cells[i] for i, fl in enumerate(g["cell_flag"]) if fl]
        self.assertTrue(hit)
        self.assertTrue(g["joint_flag"])
        self.assertEqual(out["flagged_under_minus"], hit)
        self.assertEqual(out["reading"], f"its coverage in cells {hit}{' (and jointly)' if g['joint_flag'] else ''} "
                                         "rests on the GENIE + MEC shift")

    def test_c_t_minus_also_covers(self):
        E = self.draws(self.blocks["C_T_minus"], 1.0, seed=3)
        out = ro.leave_out_mec(E, self.blocks, self.null_minus, {"verdict": "COVERS"}, list(range(N)))
        self.assertEqual((out["flagged_under_minus"], out["grade"]["joint_flag"]), ([], False))
        self.assertEqual(out["reading"], "covers without the GENIE + MEC shift")

    def test_a_joint_flag_alone_is_a_shift_reading(self):
        import fd_1b_mc as mc
        g = {"cell_flag": [False] * N, "joint_flag": True, "verdict": "UNDER-COVERS"}
        with mock.patch.object(mc, "grade", lambda *a, **kw: g):        # addendum A5: grade takes chol_tol/chol_out
            out = ro.leave_out_mec(np.zeros((300, N)), self.blocks, self.null_minus, {"verdict": "COVERS"}, list(range(N)))
        self.assertEqual(out["reading"], "its coverage in cells [] (and jointly) rests on the GENIE + MEC shift")

    def test_no_reading_when_c_t_under_covers(self):
        E = self.draws(self.blocks["C_T"], 1.5)
        out = ro.leave_out_mec(E, self.blocks, self.null_minus, {"verdict": "UNDER-COVERS"}, list(range(N)))
        self.assertEqual(out["reading"], "printed; no reading (the tune under-covers under C_T)")


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
            self.assertFalse(rec["pins_checked"])
            arr = np.load(d / "x.npz")
            # one draw per truth, by hand: first order = c.compose; product = C2's; r_T on signal rows only; POT scale
            import types
            import clip_probe as cp
            w_flux = c.flux_weights((d / "constraint.txt").read_text())
            r_t, r_s = tp.PseudoA.r_expected(types.SimpleNamespace(truth=truth, sig=sig))
            s = tp.POT[0] / tp.POT[1]
            ks, cs = cp.reco_cell(sig["sim"], sig["sim_pz"], sig["sim_pass"])
            kb, cb = cp.reco_cell(bkg["sim_background"], bkg["sim_background_pz"], bkg["sim_background_pass"])
            for t, k in (("G18", 0), ("AR23", 299)):
                draw = c.declared_draws(t, w_flux)[k]
                self.assertEqual(draw.seed, c.TOY_SEEDS[t][k])
                F = np.zeros(cp.N_CELLS)
                P = np.zeros(cp.N_CELLS)
                for tree, prefix, kept, cell, r in ((sig, "w_reco", ks, cs, r_s), (bkg, "w_bkg", kb, cb, 1.0)):
                    cv = tree[prefix].astype(np.float64)
                    U = np.stack([tree[c.column(prefix, *u)].astype(np.float64) for u in draw.universes])
                    first = tp.PseudoA.composed(None, tree, prefix, draw)
                    ok = (cv > 0) & np.all(U > 0, axis=0)
                    prod = np.where(ok, cv * np.prod(U / np.where(cv > 0, cv, 1.0), axis=0), 0.0)
                    m = kept & (cell >= 0)
                    np.add.at(F, cell[m], (first * r * s)[m])
                    np.add.at(P, cell[m], (prod * r * s)[m])
                np.testing.assert_allclose(arr[f"{t}_first"][k], F, rtol=1e-12, atol=1e-12)
                np.testing.assert_allclose(arr[f"{t}_product"][k], P, rtol=1e-12, atol=1e-12)
            for t in ("G18", "AR23"):
                F, P = arr[f"{t}_first"], arr[f"{t}_product"]
                zz = np.abs((P[F > 0] - F[F > 0]) / np.sqrt(F[F > 0]))
                self.assertAlmostEqual(rec["draws"][t]["median_abs"], float(np.median(zz)), places=12)
                self.assertAlmostEqual(rec["draws"][t]["max_abs"], float(zz.max()), places=12)
                self.assertEqual(rec["draws"][t]["excluded_pairs_F_le_0"], int((F <= 0).sum()))
            self.assertFalse(np.allclose(arr["G18_first"], arr["AR23_first"]))   # the same ratio; different draws


if __name__ == "__main__":
    unittest.main()
