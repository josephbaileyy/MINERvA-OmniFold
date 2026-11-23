"""Tests for covfix_p0 on a synthetic 20-cell world (no committed record is read: every pin is repointed to a temp
file built here).

  python3 -B -m unittest -v test_covfix_p0.py
"""
from __future__ import annotations

import contextlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

import covfix_core as cc
import covfix_p0 as p0
import build_cmodel as bcm
import fd_1b_null as fn

N_CELL, N_TOY = 20, 60


def psd(n, seed, rank=None, scale=1.0):
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(n, n if rank is None else rank))
    return scale * (A @ A.T) / n


def build(tmp: Path, *, cpl_scale=1e-3, break_identity=False, nonpsd=False, a0_off=False, zero_xT=False,
          ibukt_cells_off=False, map_off=False, ndf_off=False, g2r_map_off=False) -> dict:
    """Write a synthetic world under tmp; return {"pins", "g2r_sha", "q_sha", "cmodel_sha", "q", "g2r"}."""
    n = N_CELL
    x = np.linspace(1.0, 3.0, n)
    universe, stat, c08 = psd(n, 1), psd(n, 2, scale=0.3), psd(n, 3, scale=0.05)
    if nonpsd:
        c08 = c08 - 2.0 * np.eye(n) * np.linalg.eigvalsh(c08).max()
    C_PL = psd(n, 4, rank=2, scale=cpl_scale)
    s5 = universe + stat + c08
    Q = s5 + C_PL
    if break_identity:
        Q = Q.copy()
        Q[0, 0] += 1e-9
    qp = tmp / "Q.npz"
    np.savez(qp, Q=Q, s5_total=s5, universe=universe, stat=stat, c08=c08, C_PL=C_PL, cells=np.arange(n), x=x)
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
        d = cc.carry_factor(np.where(xT == 0, 1.0, xT), x)
        Cm_T = cc.absolute(C_model, xT)
        C_T = cc.carry(s5, d) + Cm_T + psd(n, 10 + k, scale=0.01)
        E = np.random.default_rng(20 + k).multivariate_normal(np.full(n, 0.05), 2.0 * C_T, size=N_TOY)
        chi2, ndf = fn.chi2_nonnull(E, C_T)
        score = {"grade": {"chi2_mean_over_ndf": float(chi2.mean() / ndf) * (1.01 if a0_off else 1.0),
                           "ndf": ndf - (1 if ndf_off else 0)}}
        bp, ep, sp = tmp / f"blocks_{T}.npz", tmp / f"E_{T}.npz", tmp / f"score_{T}.json"
        np.savez(bp, C_T=C_T, C_model_abs=Cm_T, x_T=xT, x_R=x if not (map_off and T == "G18") else x * 1.0001,
                 rep=rep)
        np.savez(ep, E=E)
        sp.write_text(json.dumps(score))
        (g2r / T).mkdir(parents=True)
        gp = g2r / T / f"blocks_g2r_{T}.npz"
        np.savez(gp, C_T=C_T + psd(n, 30 + k, scale=0.01), C_model_abs=Cm_T,
                 x_T=xT * (1.0001 if g2r_map_off else 1.0), x_R=x)
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
            "q": qp, "g2r": g2r, "x": x}


@contextlib.contextmanager
def patched(w: dict):
    saved = (p0.PINS, p0.G2R_SHA, p0.Q_REP_SHA, p0.C_MODEL_SHA)
    p0.PINS, p0.G2R_SHA, p0.Q_REP_SHA, p0.C_MODEL_SHA = w["pins"], w["g2r_sha"], w["q_sha"], w["cmodel_sha"]
    try:
        yield
    finally:
        p0.PINS, p0.G2R_SHA, p0.Q_REP_SHA, p0.C_MODEL_SHA = saved


class Run(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def go(self, xhat=None, **kw):
        w = build(self.tmp, **kw)
        with patched(w):
            return p0.run(w["q"], w["g2r"], xhat), w

    def test_done_and_sections(self):
        rec, _ = self.go()
        self.assertEqual(rec["status"], "done", rec.get("stop"))
        self.assertEqual(rec["validates"], "nothing (declaration section 3.1)")
        self.assertEqual(set(rec["carry_check"]), {"G18", "AR23"})
        for T in p0.TUNES:
            self.assertTrue(rec["controls"][f"A0_{T}"]["pass"])
            self.assertTrue(all(rec["controls"][f"map_{T}"].values()))
            self.assertIn("pending W1", rec["carry_check"][T]["xhat_round"])
            self.assertFalse(rec["residual_rule"][T]["fires"])
            self.assertEqual(set(rec["profiles"][T]), {"K0_carried", "C_T", "C_T_prime_G2R"})
            self.assertEqual(rec["c2"][T]["carried_to_tune"]["rank"], 2)
            self.assertLess(rec["controls"][f"C_model_abs_blocks_vs_rebuilt_{T}"], 1e-15)
        self.assertTrue(all(r["pass"] for r in rec["controls"]["C_PSD"]))
        self.assertEqual(len(rec["controls"]["C_PSD"]), 9)
        self.assertEqual(set(rec["ibukt_a2"]["truths"]), {"nominal", "genie_mec", "nuwro"})

    def test_carry_matches_formula(self):
        rec, w = self.go()
        Z = p0.load_npz(w["q"])
        B = p0.load_npz(w["pins"]["blocks_G18"][0])
        E = p0.load_npz(w["pins"]["E_G18"][0])["E"]
        S = json.loads(w["pins"]["cmodel_json"][0].read_text())["S"]
        K0 = Z["Q"] + cc.absolute(bcm.cmodel(np.asarray(S)), Z["x"])
        d = B["x_T"] / Z["x"]
        r = cc.mode_readings(E, d[:, None] * K0 * d[None, :], d[:, None] * Z["Q"] * d[None, :])
        got = rec["carry_check"]["G18"]["xhat_committed"]["K0_carried"]
        self.assertEqual(got["M"]["X"], r["M"]["X"])
        self.assertEqual(got["lambda_F1"], r["lambda_F1"])              # V_F is the CARRIED Q
        self.assertNotEqual(got["lambda_F1"], float(np.linalg.eigvalsh(Z["Q"])[-1]))
        prof = rec["profiles"]["G18"]["K0_carried"]
        self.assertEqual(prof["M"]["X"], r["M"]["X"])
        self.assertEqual(prof["lambda_F1"], r["lambda_F1"])
        ct = rec["profiles"]["G18"]["C_T"]
        self.assertEqual(ct["lambda_F1"], float(np.linalg.eigvalsh(B["C_T"] - B["C_model_abs"])[-1]))

    def test_ibukt_m_is_projection(self):
        rec, w = self.go()
        Z = p0.load_npz(w["q"])
        S = json.loads(w["pins"]["cmodel_json"][0].read_text())["S"]
        K0 = Z["Q"] + cc.absolute(bcm.cmodel(np.asarray(S)), Z["x"])
        lam, U = cc.eig_basis(K0)
        keep = cc.kept_mask(lam, np.linalg.eigvalsh(Z["Q"])[-1])
        R = json.loads(w["pins"]["ibukt_readout"][0].read_text())
        b = np.asarray(R["truths"]["nuwro"]["omnifold"]["mean"]) * Z["x"]
        m = (U[:, keep].T @ b) / np.sqrt(lam[keep])
        np.testing.assert_allclose(rec["ibukt_a2"]["truths"]["nuwro"]["m"], m, rtol=0, atol=0)

    def test_c2_carried_directions(self):
        rec, w = self.go()
        Z = p0.load_npz(w["q"])
        B = p0.load_npz(w["pins"]["blocks_AR23"][0])
        E = p0.load_npz(w["pins"]["E_AR23"][0])["E"]
        lam, U = cc.eig_basis(cc.carry(Z["C_PL"], B["x_T"] / Z["x"]))
        got = rec["c2"]["AR23"]["carried_to_tune"]["directions"]
        self.assertEqual([d["mu"] for d in got], [float(v) for v in lam[:2]])
        self.assertEqual(got[0]["projection"], float(U[:, 0] @ E.mean(axis=0)))

    def test_residual_rule_pair_is_regrade(self):
        rec, w = self.go()
        Z = p0.load_npz(w["q"])
        B = p0.load_npz(w["pins"]["blocks_G18"][0])
        F = B["C_T"] - B["C_model_abs"]
        Cr = cc.carry(Z["C_PL"], B["x_T"] / Z["x"])
        want = cc.residual_rule(B["C_T"], F, B["C_T"] + Cr, F + Cr)
        got = rec["residual_rule"]["G18"]
        self.assertEqual(got["residual"], want["residual"])
        self.assertEqual(got["n_well"], want["n_well"])

    def test_g2r_pin(self):
        w = build(self.tmp)
        w["g2r_sha"] = dict(w["g2r_sha"], AR23="4" * 64)
        with patched(w):
            rec = p0.run(w["q"], w["g2r"], None)
        self.assertIn("C-PIN", rec["stop"])

    def test_c2_shares_sum_at_most_one(self):
        rec, _ = self.go()
        for T in p0.TUNES:
            s = sum(d["share_of_ebar2"] for d in rec["c2"][T]["carried_to_tune"]["directions"])
            self.assertLessEqual(s, 1.0 + 1e-12)

    def test_xhat_round_used(self):
        w0 = build(self.tmp)
        xr = self.tmp / "xr.npz"
        B = {T: p0.load_npz(w0["pins"][f"blocks_{T}"][0])["x_T"] for T in p0.TUNES}
        np.savez(xr, xhat_G18=B["G18"] * 1.01, xhat_AR23=B["AR23"])
        with patched(w0):
            rec = p0.run(w0["q"], w0["g2r"], xr)
        self.assertEqual(rec["status"], "done", rec.get("stop"))
        self.assertAlmostEqual(rec["carry_check"]["G18"]["vector_difference_max_rel"], 0.01, places=12)
        self.assertEqual(rec["carry_check"]["AR23"]["vector_difference_max_rel"], 0.0)
        self.assertIn("K0_carried", rec["carry_check"]["G18"]["xhat_round"])
        self.assertIn("sha256", rec["inputs"]["xhat_round"])

    def test_stops(self):
        cases = {"break_identity": "C-ID", "nonpsd": "C-PSD", "a0_off": "A0", "zero_xT": "carry",
                 "ibukt_cells_off": "IBUKT", "map_off": "C-MAP", "ndf_off": "A0", "g2r_map_off": "C-MAP"}
        for k, word in cases.items():
            with self.subTest(k):
                td = tempfile.TemporaryDirectory()
                self.tmp = Path(td.name)
                rec, _ = self.go(**{k: True})
                td.cleanup()
                self.assertEqual(rec["status"], "STOP", k)
                self.assertIn(word, rec["stop"], k)

    def test_residual_rule_fire_stops_to_director(self):
        rec, _ = self.go(cpl_scale=1e16)
        self.assertEqual(rec["status"], "STOP")
        self.assertIn("residual rule fires", rec["stop"])
        self.assertIn("director", rec["stop"])
        self.assertTrue(rec["residual_rule"]["G18"]["fires"])
        self.assertIn("ibukt_a2", rec)                       # the rest still ran and is recorded

    def test_residual_fire_at_cut_scale_is_the_declared_pair(self):
        rec, w = self.go(cpl_scale=1e12)                    # lambda_1(F_new) moves the new cut; no precision loss
        Z = p0.load_npz(w["q"])
        B = p0.load_npz(w["pins"]["blocks_G18"][0])
        F = B["C_T"] - B["C_model_abs"]
        Cr = cc.carry(Z["C_PL"], B["x_T"] / Z["x"])
        want = cc.residual_rule(B["C_T"], F, B["C_T"] + Cr, F + Cr)
        got = rec["residual_rule"]["G18"]
        self.assertEqual((got["ndf_new"], got["residual"], got["fires"]), (want["ndf_new"], want["residual"], True))
        self.assertLess(want["ndf_new"], N_CELL)
        self.assertEqual(rec["status"], "STOP")

    def test_pin_mismatch_stops(self):
        w = build(self.tmp)
        w["pins"]["E_G18"] = (w["pins"]["E_G18"][0], "0" * 64)
        with patched(w):
            rec = p0.run(w["q"], w["g2r"], None)
        self.assertEqual(rec["status"], "STOP")
        self.assertIn("C-PIN", rec["stop"])

    def test_q_pin(self):
        w = build(self.tmp)
        w["q_sha"] = "1" * 64
        with patched(w):
            rec = p0.run(w["q"], w["g2r"], None)
        self.assertIn("C-PIN", rec["stop"])

    def test_cmodel_sha(self):
        w = build(self.tmp)
        w["cmodel_sha"] = "2" * 64
        with patched(w):
            rec = p0.run(w["q"], w["g2r"], None)
        self.assertIn("C-MODEL", rec["stop"])


class Main(unittest.TestCase):
    def test_exit_codes(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            w = build(tmp)
            out = tmp / "p0.json"
            with patched(w):
                self.assertEqual(p0.main(["--q-rep", str(w["q"]), "--g2r-dir", str(w["g2r"]), "--out", str(out)]), 0)
                rec = json.loads(out.read_text())
                self.assertEqual(rec["status"], "done")
                self.assertEqual(set(rec["code_sha256"]), {"covfix_p0.py", "covfix_core.py"})
                self.assertEqual(p0.main(["--q-rep", str(w["q"]), "--g2r-dir", str(w["g2r"]), "--out", str(out)]), 2)
            w["q_sha"] = "3" * 64
            out2 = tmp / "p0b.json"
            with patched(w):
                self.assertEqual(p0.main(["--q-rep", str(w["q"]), "--g2r-dir", str(w["g2r"]), "--out", str(out2)]), 3)
            self.assertEqual(json.loads(out2.read_text())["status"], "STOP")

    def test_json_default(self):
        self.assertEqual(json.dumps([np.int64(3), np.float32(0.5), np.bool_(True), np.arange(2)],
                                    default=p0._json_default), "[3, 0.5, true, [0, 1]]")
        with self.assertRaises(TypeError):
            json.dumps(object(), default=p0._json_default)

    def test_real_pins_are_the_declared_ones(self):
        self.assertEqual(p0.Q_REP_SHA, "ff66b91d6d2c574a1786b057ce7566e8ed7184700a45b989fa41ae0eb8cb0295")
        self.assertEqual(p0.C_MODEL_SHA, "11fe68188bd31a35103f5eb4708bd6a7cdab8965164680caa6671c509dcd3470")
        for k, (path, want) in p0.PINS.items():
            self.assertTrue(path.is_file(), k)
            self.assertEqual(p0.sha256(path), want, k)


if __name__ == "__main__":
    unittest.main()
