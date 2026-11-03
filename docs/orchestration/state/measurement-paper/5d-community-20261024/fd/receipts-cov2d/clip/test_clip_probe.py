"""clip_probe on a synthetic universe omnifile with every branch it reads, POT parameters and a 205-cell Q file.
Needs PyROOT (to write the TParameters), uproot 5.6.9, scipy and numpy. From the checkout:
    python -B -m pytest -q docs/.../fd/receipts-cov2d/clip/test_clip_probe.py
One declared draw's clipped fractions and one cell's truth offset are recomputed independently, row by row in draw
order with cov2d.compose; (a)'s counts are recomputed from the fixture's columns."""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
sys.path[:0] = [str(HERE), str(REPO / "2d-unfolding" / "cov2d" / "tests"), str(REPO / "2d-unfolding" / "cov2d"),
                str(REPO / "nd-unfolding"), str(REPO / "nd-unfolding" / "pv-ladder")]
import clip_probe as cp  # noqa: E402
import cov2d as c  # noqa: E402
import test_cov2d as tc  # noqa: E402

DATA_POT, MC_POT = 1.0e20, 4.0e20


def build(d: Path, n=4000, nb=900, seed=17):
    import ROOT
    import uproot
    w = tc.World(d, n=n, seed=seed)
    r = np.random.default_rng(seed + 1)
    sig = w.trees["mc_signal_reco"]
    sig["MC"], sig["MC_pz"] = r.uniform(0, 2.4, n), r.uniform(1.6, 25, n)
    sig["MC_eavail"], sig["MC_q3"], sig["MC_W"] = r.uniform(0, 2, n), r.uniform(0, 2.5, n), r.uniform(0.9, 3, n)
    sig["sim"], sig["sim_pz"] = r.uniform(-0.1, 4.6, n), r.uniform(1.2, 62, n)
    sig["sim_pass"] = (r.uniform(size=n) < 0.8).astype(np.uint8)
    sig["w_truth"] = sig["w_reco"] * r.uniform(0.9, 1.1, n)       # $UNI's signal tree carries w_truth (control 1)
    sig["w_reco_LowQ2_0"][: n // 3] = 0.0                       # both LowQ2 universes zero a third of the rows,
    sig["w_reco_LowQ2_1"][: n // 3] = 0.0                       # so every draw holds a delta of -1 there
    w.trees["mc_signal_reco"] = sig
    bkg = {k: v[:nb] for k, v in w.trees["mc_background"].items()}
    bkg["sim_background"], bkg["sim_background_pz"] = r.uniform(0, 4.5, nb), r.uniform(1.5, 60, nb)
    bkg["sim_background_pass"] = (r.uniform(size=nb) < 0.9).astype(np.uint8)
    w.trees["mc_background"] = bkg
    paths = w.write()
    f = ROOT.TFile.Open(str(paths["uni"]), "UPDATE")
    ROOT.TParameter("double")("dataPOTUsed", DATA_POT).Write()
    ROOT.TParameter("double")("mcPOTUsed", MC_POT).Write()
    f.Close()
    cells = np.arange(224)[:205]
    A = r.normal(0, 0.02, (205, 205))
    x = r.uniform(1, 2, 205)
    np.savez(d / "q205.npz", cells=cells, x=x, stat=A @ A.T / 205 + np.diag(np.full(205, 1e-4)),
             Q=A @ A.T / 50 + np.diag(np.full(205, 1e-3)))
    future = time.time() + 86400
    for p in (paths["uni"], d / "q205.npz"):
        os.utime(p, (future, os.stat(p).st_mtime))
    paths["q205"] = d / "q205.npz"
    return w, paths


class ClipProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = Path(cls.tmp.name)
        cls.patch = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        cls.patch.start()
        cls.w, p = build(d)
        out = d / "clip.json"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cp.main(["--out", str(out), "--uni", str(p["uni"]), "--prep", str(p["prep"]), "--constraint",
                     str(p["cons"]), "--q205", str(p["q205"]), "--chunk", "700", "--no-pins"])
        cls.text, cls.rec = buf.getvalue(), json.loads(out.read_text())

    @classmethod
    def tearDownClass(cls):
        cls.patch.stop()
        cls.tmp.cleanup()

    def test_runs_and_reads_without_moving_atime(self):
        self.assertIn("COV2D-CLIP-PROBE done atime_moved=[]", self.text)
        self.assertEqual(self.rec["pot_scale"], DATA_POT / MC_POT)

    def test_a_counts(self):
        sig = self.w.trees["mc_signal_reco"]
        got = {x["universe"]: x for x in self.rec["a"]["wr"]}
        want = int(np.sum((sig["w_reco"] > 0) & (sig["w_reco_LowQ2_1"] <= 0)))
        self.assertEqual(got["LowQ2_1"]["rows"], want)
        self.assertAlmostEqual(got["LowQ2_1"]["cv_weight"], float(sig["w_reco"][: len(sig["w_reco"]) // 3].sum()), 9)
        self.assertEqual(self.rec["a"]["wr"][0]["universe"] in ("LowQ2_0", "LowQ2_1"), True)

    def test_one_draw_recomputed(self):
        import cov2d_receipt as rc
        import pvl_lib
        import s5e_deform
        sig, td = self.w.trees["mc_signal_reco"], self.w.trees["mc_truth_denom"]
        s = DATA_POT / MC_POT
        g = lambda t: np.stack([t[k] for k in cp.GEN], axis=1)
        gen = np.concatenate([g(td), g(sig)])
        wcat = np.concatenate([td["w_truth"], np.zeros(len(sig["w_reco"]))])
        r = s5e_deform.ratio_weight(gen, [pvl_lib.FINE[a] for a in pvl_lib.AXES5], wcat, tc.ratio_json(11), 1.0)
        r_s, r_d = r[len(td["w_truth"]):], r[: len(td["w_truth"])]
        d0 = c.declared_draws("G18", tc.W_FLUX)[7]
        lam = c.compose(sig["w_reco"], [sig[c.column("w_reco", b, i)] for b, i in d0.universes]) * r_s * s
        kept, _ = cp.reco_cell(sig["sim"], sig["sim_pz"], sig["sim_pass"])
        lam = np.where(kept, lam, 0.0)
        frac = -np.minimum(lam, 0).sum() / lam.sum()
        self.assertGreater(frac, 0)
        got = self.rec["b"]["G18"]["signal_clipped_fraction"]
        self.assertLessEqual(frac, got["max"] * (1 + 1e-12))
        tcell = rc.truth_cell(sig["MC"], sig["MC_pz"])
        cell = int(np.bincount(tcell[kept & (tcell >= 0) & (tcell < 205) & (lam < 0)]).argmax())   # the fixture's 205
        neg = -np.minimum(lam, 0)[kept & (tcell == cell)].sum()
        dcell = rc.truth_cell(td["MC"], td["MC_pz"])
        cvh = (td["w_truth"] * r_d * s)[dcell == cell].sum()
        uh = [(td[c.column("w_truth", b, i)] * r_d * s)[dcell == cell].sum() for b, i in d0.universes]
        n_cell = float(c.compose(np.array([cvh]), [np.array([x]) for x in uh])[0])
        self.assertGreater(neg / n_cell, 0)
        self.recomputed = (frac, cell, neg / n_cell)

    def test_draw_seven_matches_through_a_one_draw_run(self):
        """Run the probe's own accumulation with the declared draws cut to draw 7 at both tunes, and compare its
        signal clipped fraction and truth-cell fraction with the row-by-row recomputation."""
        self.test_one_draw_recomputed()
        frac, cell, cell_frac = self.recomputed
        real = c.declared_draws
        d = Path(self.tmp.name)
        with mock.patch.object(c, "declared_draws", lambda t, w: real(t, w)[7:8]):
            out = d / "one.json"
            with contextlib.redirect_stdout(io.StringIO()):
                cp.main(["--out", str(out), "--uni", str(d / "uni.root"), "--prep", str(d / "prep"), "--constraint",
                         str(d / "constraint.txt"), "--q205", str(d / "q205.npz"), "--chunk", "650", "--no-pins"])
        rec = json.loads(out.read_text())
        self.assertAlmostEqual(rec["b"]["G18"]["signal_clipped_fraction"]["median"], frac, places=12)
        q = np.load(d / "q205.npz")
        k = list(rec["b"]["G18"]["cells205"]).index(cell)
        rel_q = np.sqrt(np.diag(q["Q"]))[k] / q["x"][k]
        self.assertAlmostEqual(rec["b"]["G18"]["truth_cells_frac_over_sigma_Q"]["median"][k], cell_frac / rel_q,
                               places=9)


if __name__ == "__main__":
    unittest.main()
