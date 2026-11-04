"""cov2d_pseudo_write (the pseudo-data job's step B) on a synthetic step-A directory, a synthetic E_R file and synthetic
flux files, all written with PyROOT alone, so the tests run in root_6_28, the environment step B runs in (it has no
uproot). Expected values are recomputed here: counts summed by hand, the file read back with RDataFrame, the cross
section by the formula of extract_cross_section_2d's docstring.
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_pseudo_write
"""
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
sys.path.insert(0, str(HERE.parent))
import cov2d as c  # noqa: E402

try:
    import ROOT
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.AddDirectory(False)
    import cov2d_pseudo_write as pw  # noqa: E402
    HAVE = True
except Exception:  # pragma: no cover
    HAVE = False

NS, NB = 600, 150
POT_DATA = 1.5e20


def write_fixture(d: Path, drv, perturb=None):
    """A step-A directory with 3 natures (a toy with Flux:7, a toy with Flux:2, the realization), E_R and flux files.
    ``perturb`` may edit (T, I, D, X, truth_cv_r1, sum_plus_passed) before they are written."""
    r = np.random.default_rng(5)
    pe, ze = np.asarray(drv.PT_EDGES, float), np.asarray(drv.PZ_EDGES, float)
    nx, ny = pe.size - 1, ze.size - 1
    D = r.uniform(50, 500, (nx, ny))
    T = D * r.uniform(0.6, 0.95, (nx, ny))
    X = r.uniform(1, 2, (nx, ny))
    X.ravel()[r.choice(nx * ny, nx * ny - 205, replace=False)] = 0.0
    flux = r.uniform(1e-9, 3e-9, nx)
    fix = {"T": T, "I": T.copy(), "D": D, "X": X, "truth_cv_r1": D.ravel().copy(), "plus_passed": None}
    a = d / "a"
    a.mkdir()
    sig = {"sim": r.uniform(0.05, 1.2, NS), "sim_pz": r.uniform(2.0, 18.0, NS),
           "sim_pass": (r.uniform(size=NS) < 0.8).astype(np.int32)}
    bkg = {"sim_background": r.uniform(0.05, 1.2, NB), "sim_background_pz": r.uniform(2.0, 18.0, NB),
           "sim_background_pass": (r.uniform(size=NB) < 0.9).astype(np.int32)}
    np.savez(a / "reco_signal.npz", **sig)
    np.savez(a / "reco_background.npz", **bkg)
    seeds = [5_720_000, 5_720_001, 5_721_000]
    nats = [{"role": "toy", "seed": seeds[0], "universes": ["Flux:7", "2p2h:1"]},
            {"role": "toy", "seed": seeds[1], "universes": ["Flux:2", "2p2h:0"]},
            {"role": "realization", "seed": seeds[2], "universes": []}]
    toys = []
    for n in nats:
        ks, kb = r.poisson(0.9, NS), r.poisson(0.9, NB)
        np.savez(a / f"counts_{n['seed']}.npz", signal=ks.astype(np.uint16), background=kb.astype(np.uint16))
        passed = int(ks[sig["sim_pass"] != 0].sum() + kb[bkg["sim_background_pass"] != 0].sum())
        toys.append({"role": n["role"], "seed": n["seed"], "sum_lambda_plus_passed": float(passed)})
    if perturb:
        perturb(fix, toys)
    clipped = r.uniform(10, 400, (3, nx * ny))
    np.savez(a / "cells.npz", truth_clipped=clipped, truth_cv_r1=fix["truth_cv_r1"], seeds=np.array(seeds))
    (a / "pseudo_a.json").write_text(json.dumps({"truth": "G18", "verdict": "PASS", "pot": {"data": POT_DATA},
                                                 "natures": nats, "toys": toys}))
    f = ROOT.TFile.Open(str(d / "xsec.root"), "RECREATE")
    for name, arr in (("hTruth2D", fix["T"]), ("hOFInputTruth2D", fix["I"]), ("hOFTruthDenom2D", fix["D"]),
                      ("hOFCompleteness2D", fix["T"] / fix["D"]), ("hXSec2D", fix["X"])):
        pw.to_th2(drv, name, arr).Write(name)
    drv.make_flux_hist("hFlux_pt", drv.PT_EDGES, flux).Write("hFlux_pt")
    ROOT.TParameter("double")("dataPOT", POT_DATA).Write()
    ROOT.TParameter("double")("nNucleons", drv.TRACKER_FIDUCIAL_N_NUCLEONS).Write()
    f.Close()
    f = ROOT.TFile.Open(str(d / "mc.root"), "RECREATE")
    drv.make_flux_hist(pw.FLUX_HIST, drv.PT_EDGES, flux).Write(pw.FLUX_HIST)
    f.Close()
    univ = flux[:, None] * r.uniform(0.9, 1.1, (nx, 100))
    f = ROOT.TFile.Open(str(d / "fluxu.root"), "RECREATE")
    drv.make_flux_hist("hFluxCV", drv.PT_EDGES, flux).Write("hFluxCV")
    h = ROOT.TH2D("hFluxUniv", "", nx, np.asarray(drv.PT_EDGES, float), 100, -0.5, 99.5)
    for i in range(nx):
        for u in range(100):
            h.SetBinContent(i + 1, u + 1, univ[i, u])
    h.Write("hFluxUniv")
    f.Close()
    future = time.time() + 86400
    for p in ("xsec.root", "mc.root", "fluxu.root"):
        os.utime(d / p, (future, os.stat(d / p).st_mtime))
    return {"sig": sig, "bkg": bkg, "seeds": seeds, "flux": flux, "univ": univ, "clipped": clipped, "X": X}


@unittest.skipUnless(HAVE, "needs PyROOT")
class StepB(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.d = Path(self.td.name)
        p = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        p.start()
        self.addCleanup(p.stop)
        self.drv = pw.driver()

    def run_b(self, extra=()):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = pw.main(["--a", str(self.d / "a"), "--out", str(self.d / "out"), "--er", str(self.d / "xsec.root"),
                            "--mcfile", str(self.d / "mc.root"), "--flux-universe-file", str(self.d / "fluxu.root"),
                            "--no-pins", *extra])
        return code, buf.getvalue()

    def rec(self):
        return json.loads((self.d / "out" / "pseudo_b.json").read_text())

    def test_pass_files_read_back_and_truth(self):
        fx = write_fixture(self.d, self.drv)
        code, text = self.run_b()
        self.assertEqual(code, 0, text)
        rec = self.rec()
        self.assertTrue(rec["section_9_4"]["pass"])
        self.assertEqual(rec["section_9_4"]["cells"], 205)
        self.assertEqual(rec["atime_moved"], [])
        for k, s in enumerate(fx["seeds"]):
            path = self.d / "out" / f"data_{s}.root"
            z = np.load(self.d / "a" / f"counts_{s}.npz")
            want = int(z["signal"][fx["sig"]["sim_pass"] != 0].sum()
                       + z["background"][fx["bkg"]["sim_background_pass"] != 0].sum())
            self.assertEqual(int(ROOT.RDataFrame("data", str(path)).Count().GetValue()), want)
            f = ROOT.TFile.Open(str(path))
            self.assertEqual(sorted((key.GetName(), key.GetCycle()) for key in f.GetListOfKeys()),
                             [("data", 1), ("dataPOTUsed", 1)])
            self.assertEqual(f.Get("dataPOTUsed").GetVal(), POT_DATA)
            f.Close()
            import hashlib
            self.assertEqual(rec["files"][k]["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertTrue(rec["files"][k]["section_9_11"]["pass"])
        self.assertIn("realization_z", rec["files"][2]["section_9_11"])

    def test_truth_uses_the_drawn_flux_universe(self):
        fx = write_fixture(self.d, self.drv)
        code, text = self.run_b()
        self.assertEqual(code, 0, text)
        x = np.load(self.d / "out" / "truth_xsec.npz")["xsec"]
        pe, ze = np.asarray(self.drv.PT_EDGES), np.asarray(self.drv.PZ_EDGES)
        area = np.outer(np.diff(pe), np.diff(ze))
        n = self.drv.TRACKER_FIDUCIAL_N_NUCLEONS
        for k, phi in ((0, fx["univ"][:, 7]), (1, fx["univ"][:, 2]), (2, fx["flux"])):
            want = fx["clipped"][k].reshape(area.shape) / (phi[:, None] * n * POT_DATA * area) * 1e4
            np.testing.assert_allclose(x[k], want, rtol=1e-12)

    def test_section_9_4_stops_before_any_data_file(self):
        def off(fix, toys):
            fix["truth_cv_r1"][17] *= 1 + 1e-9
        write_fixture(self.d, self.drv, off)
        code, text = self.run_b()
        self.assertEqual(code, 3, text)
        self.assertIn("section 9.4", text)
        self.assertEqual(list((self.d / "out").glob("data_*.root")), [])

    def test_section_9_4_cross_check_on_hTruth2D(self):
        def off(fix, toys):
            fix["I"] = fix["I"].copy()
            fix["I"][3, 4] += 1.0
        write_fixture(self.d, self.drv, off)
        code, text = self.run_b()
        self.assertEqual(code, 3, text)
        self.assertFalse(self.rec()["section_9_4"]["hTruth2D_equals_hOFInputTruth2D"])

    def test_section_9_4_needs_205_cells(self):
        def off(fix, toys):
            fix["X"] = fix["X"].copy()
            fix["X"][fix["X"] > 0] = 0.0
            fix["X"].ravel()[:204] = 1.0
        write_fixture(self.d, self.drv, off)
        code, text = self.run_b()
        self.assertEqual(code, 3, text)
        self.assertEqual(self.rec()["section_9_4"]["cells"], 204)

    def test_section_9_11_realization_more_than_5_sigma_stops(self):
        def off(fix, toys):
            toys[2]["sum_lambda_plus_passed"] *= 3.0
        write_fixture(self.d, self.drv, off)
        code, text = self.run_b()
        self.assertEqual(code, 3, text)
        self.assertIn("section 9.11: seed 5721000", text)
        self.assertGreater(abs(self.rec()["files"][2]["section_9_11"]["realization_z"]), 5)

    def test_section_9_11_catches_a_wrong_file(self):
        write_fixture(self.d, self.drv)
        real = pw.cw.write_data_file

        def drop_one(path, cols, pot):   # the writer loses one row
            real(path, {k: v[1:] for k, v in cols.items()}, pot)
        with mock.patch.object(pw.cw, "write_data_file", drop_one):
            code, text = self.run_b()
        self.assertEqual(code, 3, text)
        chk = self.rec()["files"][0]["section_9_11"]
        self.assertFalse(chk["rows_equal"])
        self.assertFalse(chk["reco_cells_equal"])

    def test_section_9_11_catches_a_moved_row(self):
        write_fixture(self.d, self.drv)
        real = pw.cw.write_data_file

        def move(path, cols, pot):   # one row's pT moved by one ulp: no longer any passing row's
            m = cols["measured"].copy()
            m[0] = np.nextafter(m[0], np.inf)
            real(path, dict(cols, measured=m), pot)
        with mock.patch.object(pw.cw, "write_data_file", move):
            code, text = self.run_b()
        self.assertEqual(code, 3, text)
        self.assertEqual(self.rec()["files"][0]["section_9_11"]["rows_not_a_passing_row"], 1)

    def test_refuses_a_stopped_step_a(self):
        write_fixture(self.d, self.drv)
        p = self.d / "a" / "pseudo_a.json"
        p.write_text(json.dumps(dict(json.loads(p.read_text()), verdict="STOP")))
        with self.assertRaises(c.Refusal):
            self.run_b()

    def test_pins_are_checked(self):
        write_fixture(self.d, self.drv)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(c.Refusal):
            pw.main(["--a", str(self.d / "a"), "--out", str(self.d / "out"), "--er", str(self.d / "xsec.root"),
                     "--mcfile", str(self.d / "mc.root"), "--flux-universe-file", str(self.d / "fluxu.root")])


if __name__ == "__main__":
    unittest.main()
