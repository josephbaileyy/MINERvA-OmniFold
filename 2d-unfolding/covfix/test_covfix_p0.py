"""Tests for covfix_p0 on a synthetic 20-cell world: every pin is repointed to a temp file built here, so no committed
record is read. The production pin audit is test_covfix_p0_pins.py.

  python3 -B -m unittest -v test_covfix_p0.py
"""
from __future__ import annotations

import contextlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

import covfix_core as cc
import covfix_p0 as p0
import build_cmodel as bcm
import fd_1b_null as fn

N_CELL, N_TOY = 20, 60
DONE = "done (pre-W1 part)"


def psd(n, seed, rank=None, scale=1.0):
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(n, n if rank is None else rank))
    return scale * (A @ A.T) / n


def build(tmp: Path, *, cpl_scale=1e-3, cpl_small_second=False, break_q=False, break_s5=False, nonpsd=False,
          a0_off=False, ndf_off=False, zero_xT=False, ibukt_cells_off=False, map_off=False, g2r_map_off=False,
          g2r_rep_off=False, g2r_nonpsd=False, ft_nonpsd=False, g2r_zero=False, xR_zero=False) -> dict:
    """Write a synthetic world under tmp; return its pins and paths."""
    n = N_CELL
    x = np.linspace(1.0, 3.0, n)
    if xR_zero:
        x[5] = 0.0
    universe, stat, c08 = psd(n, 1), psd(n, 2, scale=0.3), psd(n, 3, scale=0.05)
    if nonpsd:
        c08 = c08 - 2.0 * np.eye(n) * np.linalg.eigvalsh(c08).max()
    C_PL = psd(n, 4, rank=2, scale=cpl_scale)
    if cpl_small_second:
        lam, U = np.linalg.eigh(C_PL)
        C_PL = cpl_scale * (np.outer(U[:, -1], U[:, -1]) + 1e-14 * np.outer(U[:, -2], U[:, -2]))
    s5 = universe + stat + c08
    Q = s5 + C_PL
    if break_q:
        Q = Q.copy()
        Q[0, 0] += 1e-9
    s5_saved = s5.copy()
    if break_s5:
        s5_saved[1, 1] += 1e-9
        Q = s5_saved + C_PL                                  # Q's own identity still holds
    qp = tmp / "Q.npz"
    np.savez(qp, Q=Q, s5_total=s5_saved, universe=universe, stat=stat, c08=c08, C_PL=C_PL, cells=np.arange(n), x=x)
    S = np.random.default_rng(5).normal(scale=0.05, size=(3, n))
    cmj = tmp / "cmodel.json"
    cmj.write_text(json.dumps({"S": S.tolist(), "vertices": ["genie_mec", "nuwro", "gibuu"]}))
    C_model = bcm.cmodel(S)
    pins = {"cmodel_json": (cmj, p0.sha256(cmj))}
    g2r = tmp / "g2r"
    g2r_sha = {}
    rep = np.zeros(n + 4, bool)
    rep[:n] = True
    for k, T in enumerate(p0.TUNES):
        xT = x * (1.0 + 0.1 * np.sin(np.arange(n) + k))
        if zero_xT and T == "AR23":
            xT[3] = 0.0
        d = cc.carry_factor(np.where(xT == 0, 1.0, xT), np.where(x == 0, 1.0, x))
        Cm_T = cc.absolute(C_model, xT)
        C_T = cc.carry(s5, d) + Cm_T + psd(n, 10 + k, scale=0.01)
        E = np.random.default_rng(20 + k).multivariate_normal(np.full(n, 0.05), 2.0 * C_T, size=N_TOY)
        chi2, ndf = fn.chi2_nonnull(E, C_T)
        score = {"grade": {"chi2_mean_over_ndf": float(chi2.mean() / ndf) * (1.01 if a0_off else 1.0),
                           "ndf": ndf - (1 if ndf_off else 0)}}
        bp, ep, sp = tmp / f"blocks_{T}.npz", tmp / f"E_{T}.npz", tmp / f"score_{T}.json"
        np.savez(bp, C_T=C_T, C_model_abs=Cm_T * (100.0 if ft_nonpsd else 1.0), x_T=xT,
                 x_R=x if not (map_off and T == "G18") else x * 1.0001, rep=rep)
        np.savez(ep, E=E)
        sp.write_text(json.dumps(score))
        (g2r / T).mkdir(parents=True)
        gp = g2r / T / f"blocks_g2r_{T}.npz"
        CTp = C_T + psd(n, 30 + k, scale=0.01)
        if g2r_nonpsd:
            CTp = CTp - 2.0 * np.eye(n) * np.linalg.eigvalsh(CTp).max()
        Cm_G = Cm_T
        if g2r_zero:
            CTp, Cm_G = np.zeros((n, n)), np.zeros((n, n))
        grep = rep.copy()
        if g2r_rep_off:
            grep[n - 1], grep[n] = False, True
        np.savez(gp, C_T=CTp, C_model_abs=Cm_G, x_T=xT * (1.0001 if g2r_map_off else 1.0), x_R=x, rep=grep)
        g2r_sha[T] = p0.sha256(gp)
        pins |= {f"blocks_{T}": (bp, p0.sha256(bp)), f"E_{T}": (ep, p0.sha256(ep)), f"score_{T}": (sp, p0.sha256(sp))}
    cells = list(range(n))
    if ibukt_cells_off:
        cells = cells[::-1]
    rng = np.random.default_rng(40)
    truths = {t: {"cells": cells, "omnifold": {"mean": rng.normal(scale=0.01, size=n).tolist()}}
              for t in ("nominal", "genie_mec", "nuwro")}
    ib = tmp / "readout.json"
    ib.write_text(json.dumps({"truths": truths}))
    pins["ibukt_readout"] = (ib, p0.sha256(ib))
    return {"pins": pins, "g2r_sha": g2r_sha, "q_sha": p0.sha256(qp), "cmodel_sha": bcm.matrix_sha256(C_model),
            "q": qp, "g2r": g2r}


@contextlib.contextmanager
def patched(w: dict):
    saved = (p0.PINS, p0.G2R_SHA, p0.Q_REP_SHA, p0.C_MODEL_SHA)
    p0.PINS, p0.G2R_SHA, p0.Q_REP_SHA, p0.C_MODEL_SHA = w["pins"], w["g2r_sha"], w["q_sha"], w["cmodel_sha"]
    try:
        yield
    finally:
        p0.PINS, p0.G2R_SHA, p0.Q_REP_SHA, p0.C_MODEL_SHA = saved


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def go(self, **kw):
        w = build(self.tmp, **kw)
        with patched(w):
            return p0.run(w["q"], w["g2r"]), w

    def world(self, w):
        Z = p0.load_npz(w["q"].read_bytes())
        S = json.loads(w["pins"]["cmodel_json"][0].read_text())["S"]
        K0 = Z["Q"] + cc.absolute(bcm.cmodel(np.asarray(S)), Z["x"])
        return Z, K0


class Run(Base):
    def test_done_and_sections(self):
        rec, _ = self.go()
        self.assertEqual(rec["status"], DONE, rec.get("stop"))
        self.assertEqual((rec["part"], rec["validates"]), ("pre-W1", "nothing (declaration section 3.1)"))
        for T in p0.TUNES:
            self.assertTrue(rec["controls"][f"A0_{T}"]["pass"])
            self.assertTrue(all(rec["controls"][f"map_{T}"].values()))
            self.assertIn("pending W1", rec["carry_check"][T]["xhat_round"])
            self.assertFalse(rec["residual_rule"][T]["fires"])
            self.assertEqual(set(rec["profiles"][T]), {"K0_carried", "C_T", "C_T_prime_G2R"})
            self.assertLess(rec["controls"][f"C_model_abs_blocks_vs_rebuilt_{T}"], 1e-15)
            self.assertIn("G2R_" + T, rec["inputs"])
        self.assertTrue(all(r["pass"] for r in rec["controls"]["C_PSD"]))
        self.assertEqual(len(rec["controls"]["C_PSD"]), 9 + 2 * 12)       # reference blocks + every per-tune block
        self.assertIn("C_model_abs rebuilt(G18)", [r["name"] for r in rec["controls"]["C_PSD"]])
        self.assertEqual(list(rec["controls"])[-1], "A0_AR23")             # A0 after C-PSD
        self.assertEqual(set(rec["ibukt_a2"]["truths"]), {"nominal", "genie_mec", "nuwro"})

    def test_carry_matches_formula(self):
        rec, w = self.go()
        Z, K0 = self.world(w)
        B = p0.load_npz(w["pins"]["blocks_G18"][0].read_bytes())
        E = p0.load_npz(w["pins"]["E_G18"][0].read_bytes())["E"]
        d = B["x_T"] / Z["x"]
        r = cc.mode_readings(E, d[:, None] * K0 * d[None, :], d[:, None] * Z["Q"] * d[None, :])
        got = rec["carry_check"]["G18"]["xhat_committed"]["K0_carried"]
        self.assertEqual((got["M"]["X"], got["lambda_F1"]), (r["M"]["X"], r["lambda_F1"]))
        self.assertNotEqual(got["lambda_F1"], cc.lambda_1(Z["Q"]))         # V_F is the CARRIED Q
        prof = rec["profiles"]["G18"]
        self.assertEqual((prof["K0_carried"]["M"]["X"], prof["K0_carried"]["lambda_F1"]), (r["M"]["X"], r["lambda_F1"]))
        self.assertEqual(prof["C_T"]["lambda_F1"], cc.lambda_1(B["C_T"] - B["C_model_abs"]))
        ratio = rec["carry_check"]["G18"]["xhat_committed"]["eigenvalue_ratio_K0_over_C_T"]
        self.assertEqual(ratio["R1"]["n"], N_CELL)
        self.assertIn("dropped", ratio["R2"])

    def test_ibukt_m_only_and_is_projection(self):
        rec, w = self.go()
        Z, K0 = self.world(w)
        lam, U = cc.eig_basis(K0)
        keep = cc.kept_mask(lam, cc.lambda_1(Z["Q"]))
        R = json.loads(w["pins"]["ibukt_readout"][0].read_text())
        b = np.asarray(R["truths"]["nuwro"]["omnifold"]["mean"]) * Z["x"]
        got = rec["ibukt_a2"]["truths"]["nuwro"]
        self.assertEqual(set(got), {"m"})
        np.testing.assert_allclose(got["m"], (U[:, keep].T @ b) / np.sqrt(lam[keep]), rtol=0, atol=0)

    def test_c2_carried_directions(self):
        rec, w = self.go()
        Z, _ = self.world(w)
        B = p0.load_npz(w["pins"]["blocks_AR23"][0].read_bytes())
        E = p0.load_npz(w["pins"]["E_AR23"][0].read_bytes())["E"]
        lam, U = cc.eig_basis(cc.carry(Z["C_PL"], B["x_T"] / Z["x"]))
        got = rec["c2"]["AR23"]["carried_to_tune"]["directions"]
        self.assertEqual([g["mu"] for g in got], [float(v) for v in lam[:2]])
        self.assertEqual([g["projection"] for g in got], [float(U[:, i] @ E.mean(axis=0)) for i in range(2)])
        self.assertLessEqual(sum(g["share_of_ebar2"] for g in got), 1.0 + 1e-12)

    def test_c2_small_second_direction_kept(self):
        rec, _ = self.go(cpl_small_second=True)
        self.assertEqual(rec["status"], DONE, rec.get("stop"))
        self.assertEqual(len(rec["c2"]["G18"]["carried_to_tune"]["directions"]), 2)

    def test_c2_zero_mean_share_undefined(self):
        C_PL = psd(N_CELL, 4, rank=2)
        out = p0.c2(np.zeros((3, N_CELL)), C_PL, np.ones(N_CELL))
        for g in out["carried_to_tune"]["directions"]:
            self.assertEqual((g["projection"], g["share_of_ebar2"]), (0.0, None))

    def test_residual_rule_pair_is_regrade(self):
        rec, w = self.go()
        Z, _ = self.world(w)
        B = p0.load_npz(w["pins"]["blocks_G18"][0].read_bytes())
        F = B["C_T"] - B["C_model_abs"]
        Cr = cc.carry(Z["C_PL"], B["x_T"] / Z["x"])
        want = cc.residual_rule(B["C_T"], F, B["C_T"] + Cr, F + Cr)
        got = rec["residual_rule"]["G18"]
        self.assertEqual((got["residual"], got["n_well"], got["ndf_new"]), (want["residual"], want["n_well"], want["ndf_new"]))
        self.assertIn("cut_diagnostic", got)

    def test_residual_fire_stops_before_readings(self):
        rec, w = self.go(cpl_scale=1e12)            # lambda_1(F_new) moves the new cut; no precision loss
        Z, _ = self.world(w)
        B = p0.load_npz(w["pins"]["blocks_G18"][0].read_bytes())
        F = B["C_T"] - B["C_model_abs"]
        Cr = cc.carry(Z["C_PL"], B["x_T"] / Z["x"])
        want = cc.residual_rule(B["C_T"], F, B["C_T"] + Cr, F + Cr)
        got = rec["residual_rule"]["G18"]
        self.assertEqual((got["ndf_new"], got["residual"], got["fires"]), (want["ndf_new"], want["residual"], True))
        self.assertLess(want["ndf_new"], N_CELL)
        self.assertEqual(rec["status"], "STOP")
        self.assertIn("residual rule fires", rec["stop"])
        self.assertIn("director", rec["stop"])
        for k in ("carry_check", "profiles", "c2", "ibukt_a2"):
            self.assertNotIn(k, rec)

    def test_stops(self):
        cases = {"break_q": "C-ID", "break_s5": "C-ID", "nonpsd": "C-PSD", "g2r_nonpsd": "C-PSD",
                 "ft_nonpsd": "C-PSD", "a0_off": "A0", "ndf_off": "A0",
                 "ibukt_cells_off": "IBUKT", "map_off": "C-MAP", "g2r_rep_off": "C-MAP"}
        for k, word in cases.items():
            with self.subTest(k):
                with tempfile.TemporaryDirectory() as td:
                    w = build(Path(td), **{k: True})
                    with patched(w):
                        rec = p0.run(w["q"], w["g2r"])
                self.assertEqual(rec["status"], "STOP", k)
                self.assertIn(word, rec["stop"], k)

    def test_carry_refusal_is_scoped_to_its_tune(self):
        rec, _ = self.go(zero_xT=True)                       # AR23's x_T has a zero cell
        self.assertEqual(rec["status"], DONE, rec.get("stop"))
        self.assertIn("refused", rec["controls"]["carry_AR23"])
        self.assertNotIn("carry_G18", rec["controls"])
        self.assertIn("refused", rec["carry_check"]["AR23"]["xhat_committed"])
        self.assertIn("refused", rec["profiles"]["AR23"]["K0_carried"])
        self.assertIn("M", rec["profiles"]["AR23"]["C_T"])
        self.assertIn("residual", rec["residual_rule"]["AR23"])      # REGRADE's carry forms C_run with a zero cell
        self.assertIn("M", rec["carry_check"]["G18"]["xhat_committed"]["K0_carried"])
        names = [r["name"] for r in rec["controls"]["C_PSD"]]
        self.assertNotIn("K0 carried(AR23)", names)
        self.assertIn("K0 carried(G18)", names)

    def test_regrade_pair_unavailable_at_a_zero_x_R(self):
        rec, _ = self.go(xR_zero=True)
        self.assertEqual(rec["status"], DONE, rec.get("stop"))
        for T in p0.TUNES:
            self.assertIn("unavailable", rec["residual_rule"][T])
            self.assertIn("unavailable", rec["c2"][T])
            self.assertIn("refused", rec["controls"]["carry_" + T])

    def test_regrade_c_run_unavailable(self):
        self.assertIsNone(p0.regrade_c_run(np.eye(2), np.ones(2), np.array([1.0, 0.0])))
        np.testing.assert_array_equal(p0.regrade_c_run(np.eye(2), np.array([0.0, 2.0]), np.ones(2)),
                                      np.diag([0.0, 4.0]))

    def test_inputs_parsed_from_the_hashed_bytes(self):
        w = build(self.tmp)
        real = p0.read_pinned
        seen = []

        def spy(path, want):
            data = real(path, want)
            seen.append(Path(path))
            Path(path).write_bytes(b"replaced")             # a swap after the check cannot be read
            return data
        with patched(w), mock.patch.object(p0, "read_pinned", spy):
            rec = p0.run(w["q"], w["g2r"])
        self.assertEqual(rec["status"], DONE, rec.get("stop"))
        self.assertEqual(len(seen), len(set(seen)))          # each input read exactly once

    def test_ibukt_arm_shape_and_missing(self):
        for bad in ("column", "missing"):
            with self.subTest(bad), tempfile.TemporaryDirectory() as td:
                w = build(Path(td))
                ib = w["pins"]["ibukt_readout"][0]
                R = json.loads(ib.read_text())
                if bad == "column":
                    R["truths"]["nuwro"]["omnifold"]["mean"] = [[v] for v in R["truths"]["nuwro"]["omnifold"]["mean"]]
                else:
                    del R["truths"]["nuwro"]["omnifold"]
                ib.write_text(json.dumps(R))
                w["pins"]["ibukt_readout"] = (ib, p0.sha256(ib))
                with patched(w):
                    rec = p0.run(w["q"], w["g2r"])
                self.assertEqual(rec["status"], "STOP")
                self.assertIn("IBUKT", rec["stop"])

    def test_ibukt_empty_basis(self):
        out = p0.ibukt({"truths": {}}, np.zeros((3, 3)), np.eye(3), np.ones(3))
        self.assertIn("refused", out)

    def test_ibukt_checked_in_preflight(self):
        rec, _ = self.go(ibukt_cells_off=True)
        self.assertIn("IBUKT", rec["stop"])
        self.assertNotIn("C_PSD", rec["controls"])

    def test_psd_reported_before_a0(self):
        rec, _ = self.go(nonpsd=True, a0_off=True)
        self.assertIn("C-PSD", rec["stop"])

    def test_g2r_frame_vectors_printed_not_barred(self):
        rec, _ = self.go(g2r_map_off=True)
        self.assertEqual(rec["status"], DONE, rec.get("stop"))
        self.assertFalse(rec["controls"]["map_G18"]["printed, not barred"]["G2R x_T = blocks x_T"])

    def test_empty_reading_is_scoped(self):
        rec, _ = self.go(g2r_zero=True)
        self.assertEqual(rec["status"], DONE, rec.get("stop"))
        self.assertIn("refused", rec["profiles"]["G18"]["C_T_prime_G2R"])
        self.assertIn("M", rec["profiles"]["G18"]["C_T"])
        with mock.patch.object(p0, "carry_compare", side_effect=cc.Refusal("x")):
            self.assertEqual(p0.scoped(p0.carry_compare, 1), {"refused": "x"})

    def test_psd_stop_names_block(self):
        rec, _ = self.go(g2r_nonpsd=True)
        self.assertIn("C_T_prime(G18)", rec["stop"])
        with tempfile.TemporaryDirectory() as td:
            w = build(Path(td), ft_nonpsd=True)
            with patched(w):
                rec2 = p0.run(w["q"], w["g2r"])
        self.assertIn("F_T(G18)", rec2["stop"])

    def test_pin_failures(self):
        for what in ("E_G18", "q", "cmodel", "g2r", "g2r_missing"):
            with self.subTest(what):
                with tempfile.TemporaryDirectory() as td:
                    w = build(Path(td))
                    if what == "E_G18":
                        w["pins"]["E_G18"] = (w["pins"]["E_G18"][0], "0" * 64)
                    elif what == "q":
                        w["q_sha"] = "1" * 64
                    elif what == "cmodel":
                        w["cmodel_sha"] = "2" * 64
                    elif what == "g2r":
                        w["g2r_sha"] = dict(w["g2r_sha"], AR23="4" * 64)
                    else:
                        (w["g2r"] / "AR23" / "blocks_g2r_AR23.npz").unlink()
                    with patched(w):
                        rec = p0.run(w["q"], w["g2r"])
                self.assertEqual(rec["status"], "STOP")
                self.assertIn("C-MODEL" if what == "cmodel" else "C-PIN", rec["stop"])


class A0(unittest.TestCase):
    def test_tolerance_branches(self):
        self.assertEqual(p0.a0_tol(np.diag([1.0, 0.5, 0.1]))["tol"], 1e-9)            # floor
        t = p0.a0_tol(np.diag([1.0, 1e-9]))                                          # kappa 1e9
        self.assertAlmostEqual(t["kappa2"], 1e9, delta=1.0)
        self.assertAlmostEqual(t["tol"], 10 * 1e9 * cc.EPS, delta=1e-12)
        self.assertEqual(p0.a0_tol(np.diag([1.0, 1e-13]))["kappa2"], 1.0)           # under the cut: not in kappa

    def test_no_positive_eigenvalue_stops(self):
        with self.assertRaises(p0.Stop):
            p0.a0_tol(np.zeros((2, 2)))
        with self.assertRaises(p0.Stop):                                             # before any scoring
            p0.a0_control(np.ones((3, 2)), np.zeros((2, 2)), {"chi2_mean_over_ndf": 1.0, "ndf": 2})

    def test_positivity_checked_before_the_grader(self):
        with mock.patch.object(p0.fn, "chi2_nonnull", side_effect=RuntimeError("grader refused")):
            with self.assertRaises(p0.Stop):
                p0.a0_control(np.ones((3, 2)), np.zeros((2, 2)), {"chi2_mean_over_ndf": 1.0, "ndf": 2})

    def test_zero_reference(self):
        C = np.eye(2)
        self.assertTrue(p0.a0_control(np.zeros((3, 2)), C, {"chi2_mean_over_ndf": 0.0, "ndf": 2})["pass"])
        with self.assertRaises(p0.Stop):
            p0.a0_control(np.ones((3, 2)), C, {"chi2_mean_over_ndf": 0.0, "ndf": 2})

    def test_literal_scores(self):
        C = np.diag([4.0, 1.0])                              # E rows (2, 1) and (0, 1): chi2 = 2 and 1, mean/ndf = 0.75
        E = np.array([[2.0, 1.0], [0.0, 1.0]])
        self.assertTrue(p0.a0_control(E, C, {"chi2_mean_over_ndf": 0.75 * (1 + 5e-10), "ndf": 2})["pass"])
        with self.assertRaises(p0.Stop):
            p0.a0_control(E, C, {"chi2_mean_over_ndf": 0.75 * (1 + 2e-9), "ndf": 2})

    def test_inside_and_outside(self):
        C = np.diag([1.0, 1e-9])
        E = np.random.default_rng(3).normal(size=(10, 2)) * np.sqrt(np.diag(C))
        chi2, ndf = fn.chi2_nonnull(E, C)
        got = float(chi2.mean() / ndf)
        tol = p0.a0_tol(C)["tol"]
        self.assertTrue(p0.a0_control(E, C, {"chi2_mean_over_ndf": got * (1 + 0.5 * tol), "ndf": 2})["pass"])
        with self.assertRaises(p0.Stop):
            p0.a0_control(E, C, {"chi2_mean_over_ndf": got * (1 + 2.0 * tol), "ndf": 2})


class Ratio(unittest.TestCase):
    def test_nine_and_ten_common_ranks(self):
        b = np.geomspace(1, 1e-3, 83)
        self.assertEqual(p0.eig_ratio_by_band(2 * b, b)["R2"], {"n": 10, "mean": 2.0, "min": 2.0, "max": 2.0})
        self.assertIn("dropped", p0.eig_ratio_by_band(2 * b[:82], b)["R2"])         # 82 common ranks: R2 holds 9

    def test_straddling_tie(self):
        b = np.geomspace(1, 1e-3, 90)
        b[73] = b[72] * (1 - 0.5e-9)
        r = p0.eig_ratio_by_band(b, b)
        self.assertEqual((r["R1"]["n"], r["R2"]["n"]), (74, 16))


class Main(unittest.TestCase):
    def test_exit_codes_and_strict_json(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            w = build(tmp)
            out = tmp / "p0.json"
            argv = ["--q-rep", str(w["q"]), "--g2r-dir", str(w["g2r"]), "--out", str(out)]
            with patched(w):
                self.assertEqual(p0.main(argv), 0)
                rec = json.loads(out.read_text(), parse_constant=lambda c: self.fail(f"non-strict JSON {c}"))
                self.assertEqual(rec["status"], DONE)
                self.assertEqual(set(rec["code_sha256"]), {"covfix_p0.py", "covfix_core.py"})
                self.assertEqual(p0.main(argv), 2)
            w["q_sha"] = "3" * 64
            out2 = tmp / "p0b.json"
            with patched(w):
                self.assertEqual(p0.main(argv[:-1] + [str(out2)]), 3)
            self.assertEqual(json.loads(out2.read_text())["status"], "STOP")

    def test_exclusive_creation(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            w = build(tmp)
            out = tmp / "race.json"
            real = p0.run

            def racing(*a):
                rec = real(*a)
                out.write_text("{}")                         # another writer lands first
                return rec
            with patched(w), mock.patch.object(p0, "run", racing):
                rc = p0.main(["--q-rep", str(w["q"]), "--g2r-dir", str(w["g2r"]), "--out", str(out)])
            self.assertEqual((rc, out.read_text()), (2, "{}"))


if __name__ == "__main__":
    unittest.main()
