"""clip_probe2 on test_clip_probe's synthetic omnifile (PyROOT, uproot 5.6.9, scipy, numpy). With the declared draws
cut to the first 40 per tune, o_a, R, o_b, the efficiency, the three variance ratios and the coherent chi2 are
recomputed independently, row by row in draw order with cov2d.compose and an explicit per-row product. The row match
and the fixed reading are tested on crafted inputs in both directions."""
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
sys.path.insert(0, str(HERE))
import test_clip_probe as tcp  # noqa: E402
import clip_probe2 as cp2  # noqa: E402

c, rc, tc = tcp.c, cp2.rc, tcp.tc
K = 40


class Probe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = Path(cls.tmp.name)
        cls.patch = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        cls.patch.start()
        cls.w, p = tcp.build(d)
        td = cls.w.trees["mc_truth_denom"]
        n = len(td["w_truth"])
        td["w_truth_LowQ2_0"][: n // 4] = 0.0        # truth-tree negatives too, so option (1) moves the truth
        td["w_truth_LowQ2_1"][: n // 4] = 0.0
        td["w_truth_MaRES_1"][5:9] = -0.2            # floored rows for the multiplicative composition
        p = cls.w.write() | {"q205": p["q205"]}
        import ROOT
        f = ROOT.TFile.Open(str(p["uni"]), "UPDATE")
        ROOT.TParameter("double")("dataPOTUsed", tcp.DATA_POT).Write()
        ROOT.TParameter("double")("mcPOTUsed", tcp.MC_POT).Write()
        f.Close()
        real = c.declared_draws
        out = d / "c2.json"
        buf = io.StringIO()
        with mock.patch.object(c, "declared_draws", lambda t, w: real(t, w)[:K]), contextlib.redirect_stdout(buf):
            cp2.main(["--out", str(out), "--uni", str(p["uni"]), "--prep", str(p["prep"]), "--constraint",
                      str(p["cons"]), "--q205", str(p["q205"]), "--chunk", "650", "--no-pins"])
        cls.text, cls.rec, cls.q = buf.getvalue(), json.loads(out.read_text()), np.load(p["q205"])
        import pvl_lib
        import s5e_deform
        sig, td = cls.w.trees["mc_signal_reco"], cls.w.trees["mc_truth_denom"]
        g = lambda t: np.stack([t[k] for k in tcp.cp.GEN], axis=1)
        gen = np.concatenate([g(td), g(sig)])
        wcat = np.concatenate([td["w_truth"], np.zeros(len(sig["w_reco"]))])
        r = s5e_deform.ratio_weight(gen, [pvl_lib.FINE[a] for a in pvl_lib.AXES5], wcat, tc.ratio_json(11), 1.0)
        cls.r_d, cls.r_s = r[: len(td["w_truth"])], r[len(td["w_truth"]):]
        cls.draws = c.declared_draws("G18", tc.W_FLUX)[:K]

    @classmethod
    def tearDownClass(cls):
        cls.patch.stop()
        cls.tmp.cleanup()

    def comp(self, tree, pre, d):
        return c.compose(tree[pre], [tree[c.column(pre, b, i)] for b, i in d.universes])

    def rel(self, k, which="Q"):
        return np.sqrt(np.diag(self.q[which]))[k] / self.q["x"][k]

    def test_runs_without_moving_atime_and_reads(self):
        self.assertIn("COV2D-CLIP-PROBE2 done atime_moved=[]", self.text)
        self.assertIn("C2-READING", self.text)
        self.assertIn(self.rec["reading"]["overall"].split(":")[0],
                      ("option (3)", "option (1)", "positivity-preserving (multiplicative) composition",
                       "no rule of the reading fires", "the tunes read differently"))

    def per_draw(self, cell):
        sig, td = self.w.trees["mc_signal_reco"], self.w.trees["mc_truth_denom"]
        s = tcp.DATA_POT / tcp.MC_POT
        kept, _ = tcp.cp.reco_cell(sig["sim"], sig["sim_pz"], sig["sim_pass"])
        tcell = rc.truth_cell(sig["MC"], sig["MC_pz"])
        dcell = rc.truth_cell(td["MC"], td["MC_pz"])
        out = []
        for d in self.draws:
            lam = np.where(kept, self.comp(sig, "w_reco", d) * self.r_s * s, 0.0)
            tw = self.comp(td, "w_truth", d) * self.r_d * s
            sel, tsel = kept & (tcell == cell), dcell == cell
            o_a = -np.minimum(lam[sel], 0).sum() / lam[sel].sum()
            N = tw[tsel].sum()
            m_all = -np.minimum(tw[tsel], 0).sum()
            prod = np.zeros(int(tsel.sum()))
            rows = np.flatnonzero(tsel)
            for j, row in enumerate(rows):
                a_cv = td["w_truth"][row]
                if a_cv <= 0:
                    continue
                v = a_cv
                for b, i in d.universes:
                    u = td[c.column("w_truth", b, i)][row]
                    v = 0.0 if u <= 0 else v * (u / a_cv)
                prod[j] = v
            out.append((o_a, o_a - m_all / N, N, N + m_all, (prod * self.r_d[rows] * s).sum()))
        return np.array(out)

    def pick_cell(self):
        R = np.array(self.rec["b"]["G18"]["option_1"]["sigma_Q"]["signed_median"])
        A = np.array(self.rec["b"]["G18"]["option_a"]["sigma_Q"]["signed_median"])
        ok = np.flatnonzero(np.isfinite(R) & (np.abs(R - A) > 1e-6))
        self.assertGreater(ok.size, 0)
        return int(ok[0])

    def test_offsets_recomputed(self):
        cell = self.pick_cell()
        v = self.per_draw(cell)
        b = self.rec["b"]["G18"]
        self.assertAlmostEqual(b["option_a"]["sigma_Q"]["signed_median"][cell], np.median(v[:, 0]) / self.rel(cell), 9)
        self.assertAlmostEqual(b["option_1"]["sigma_Q"]["signed_median"][cell], np.median(v[:, 1]) / self.rel(cell), 9)
        self.assertAlmostEqual(b["option_1"]["sigma_stat"]["abs_max"][cell],
                               np.max(np.abs(v[:, 1])) / self.rel(cell, "stat"), 9)

    def test_variance_ratios_recomputed(self):
        cell = self.pick_cell()
        v = self.per_draw(cell)
        td = self.w.trees["mc_truth_denom"]
        s = tcp.DATA_POT / tcp.MC_POT
        dcell = rc.truth_cell(td["MC"], td["MC_pz"])
        ref = 0.0
        for b in c.ORDER:
            X = np.array([(td[c.column("w_truth", b, i)] * self.r_d * s)[dcell == cell].sum() for i in range(c.BANDS[b])])
            p = tc.W_FLUX / tc.W_FLUX.sum() if b == c.FLUX else np.full(c.BANDS[b], 1 / c.BANDS[b])
            ref += p @ (X - p @ X) ** 2
        vr = self.rec["b"]["G18"]["variance_ratio"]
        for k, col in (("first_order", 2), ("option_1_clipped", 3), ("multiplicative", 4)):
            self.assertAlmostEqual(vr[k][cell], np.var(v[:, col], ddof=1) / ref, places=8, msg=k)
        self.assertGreater(self.rec["v_multiplicative_rows"]["a_universe_floored"], 0)

    def test_coherent_chi2(self):
        F = np.random.default_rng(3).normal(0, 0.01, (205, 7))
        got = cp2.chi2_coherent(F, self.q["x"], self.q["Q"])
        want = [float((F[:, j] * self.q["x"]) @ np.linalg.inv(self.q["Q"]) @ (F[:, j] * self.q["x"])) for j in range(7)]
        np.testing.assert_allclose(got, want, rtol=1e-9)

    def test_background_offset_recomputed(self):
        bkg, sig = self.w.trees["mc_background"], self.w.trees["mc_signal_reco"]
        s = tcp.DATA_POT / tcp.MC_POT
        kb, cb = tcp.cp.reco_cell(bkg["sim_background"], bkg["sim_background_pz"], bkg["sim_background_pass"])
        ks, cs = tcp.cp.reco_cell(sig["sim"], sig["sim_pz"], sig["sim_pass"])
        vals = []
        for d in self.draws:
            lb = np.where(kb, self.comp(bkg, "w_bkg", d) * s, 0.0)
            ls = np.where(ks, self.comp(sig, "w_reco", d) * self.r_s * s, 0.0)
            vals.append([-np.minimum(lb[cb == k], 0).sum() / ls[cs == k].sum() if ls[cs == k].sum() else np.nan
                         for k in range(205)])
        vals = np.array(vals)
        got = np.array(self.rec["b"]["G18"]["background_both_options"]["sigma_Q"]["abs_max"])
        k = int(np.nanargmax(np.nanmax(np.abs(vals), axis=0)))
        self.assertAlmostEqual(got[k], np.nanmax(np.abs(vals[:, k])) / self.rel(k), places=9)

    def test_efficiency_recomputed(self):
        sig, td = self.w.trees["mc_signal_reco"], self.w.trees["mc_truth_denom"]
        kept, _ = tcp.cp.reco_cell(sig["sim"], sig["sim_pz"], sig["sim_pass"])
        tcell, dcell = rc.truth_cell(sig["MC"], sig["MC_pz"]), rc.truth_cell(td["MC"], td["MC_pz"])
        cell = self.pick_cell()
        want = sig["w_truth"][kept & (tcell == cell)].sum() / td["w_truth"][dcell == cell].sum()
        self.assertAlmostEqual(self.rec["efficiency"]["eps_c"][cell], want, places=12)


class RowMatch(unittest.TestCase):
    def test_multiplicities(self):
        a = np.array([5, 5, 5, 7, 9], np.uint64)
        b = np.array([5, 9, 9, 11], np.uint64)
        np.testing.assert_array_equal(cp2.unmatched(a, b), [False, True, True, True, False])
        np.testing.assert_array_equal(cp2.unmatched(b, a), [False, False, True, True])

    def test_hash_separates_rows_and_columns(self):
        x = np.array([1.0, 2.0, 1.0])
        y = np.array([2.0, 1.0, 2.0])
        h = cp2.row_hash([x, y])
        self.assertEqual(h[0], h[2])
        self.assertNotEqual(h[0], h[1])
        self.assertNotEqual(cp2.row_hash([x, y])[0], cp2.row_hash([y, x])[0])
        self.assertNotEqual(cp2.row_hash([np.array([0.0])])[0], cp2.row_hash([np.array([-0.0])])[0])


def fake(med, p90, vr_clip=1.0, vr_mult=1.0, share=0.0):
    n = 205
    b = {"option_1": {"sigma_Q": {"abs_median": list(np.broadcast_to(med, n)), "abs_p90": list(np.broadcast_to(p90, n))}},
         "variance_ratio": {"first_order": [1.0] * n, "option_1_clipped": list(np.broadcast_to(vr_clip, n)),
                            "multiplicative": list(np.broadcast_to(vr_mult, n))}}
    return {"b": {"G18": b, "AR23": b}, "vi": {"largest_cell_unmatched_share": share}}


class Reading(unittest.TestCase):
    def read(self, *a, **k):
        return cp2.reading(fake(*a, **k))["overall"]

    def test_option_1(self):
        self.assertEqual(self.read(0.15, 0.35), "option (1)")
        med = np.full(205, 0.15)
        med[3] = 0.21                                   # one cell above 0.2 at the median: not option (1)
        self.assertNotEqual(self.read(med, 0.35), "option (1)")
        p90 = np.full(205, 0.35)
        p90[:21] = 0.45                                 # 10.2 % of cells above 0.4: not option (1)
        self.assertNotEqual(self.read(0.15, p90), "option (1)")
        p90[:20] = 0.45
        p90[20] = 0.35                                  # 9.8 %: still option (1)
        self.assertEqual(self.read(0.15, p90), "option (1)")
        self.assertNotEqual(self.read(0.15, 0.35, vr_clip=1.3), "option (1)")

    def test_positivity_preferred(self):
        med = np.full(205, 0.25)
        med[:21] = 0.31                                 # 10.2 % above 0.3
        self.assertEqual(self.read(med, 0.5), "positivity-preserving (multiplicative) composition")
        med[20] = 0.25                                  # 9.8 %: and every p90 at 0.5 <= 0.6
        self.assertEqual(self.read(med, 0.5), "no rule of the reading fires")
        p90 = np.full(205, 0.5)
        p90[0] = 0.61
        self.assertEqual(self.read(med, p90), "positivity-preserving (multiplicative) composition")
        self.assertEqual(self.read(med, p90, vr_mult=1.25), "no rule of the reading fires")

    def test_option_3(self):
        med = np.full(205, 0.4)
        med[:41] = 0.7                                  # 20.0 % at 0.7
        self.assertEqual(self.read(med, 0.9, vr_clip=1.3, vr_mult=0.7), "option (3)")
        self.assertEqual(self.read(med, 0.9, vr_clip=1.3, vr_mult=1.0),
                         "positivity-preserving (multiplicative) composition")
        self.assertEqual(self.read(0.15, 0.35, share=0.06), "option (3)")
        self.assertEqual(self.read(0.15, 0.35, share=None), "option (3)")

    def test_variance_gate_share(self):
        vr = np.ones(205)
        vr[:10] = 1.5                                   # 95.1 % within: passes
        self.assertEqual(self.read(0.15, 0.35, vr_clip=vr), "option (1)")
        vr[10] = 1.5                                    # 94.6 %: fails
        self.assertNotEqual(self.read(0.15, 0.35, vr_clip=vr), "option (1)")


if __name__ == "__main__":
    unittest.main()
