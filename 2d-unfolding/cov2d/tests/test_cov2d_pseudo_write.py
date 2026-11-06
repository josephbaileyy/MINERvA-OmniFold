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
sys.path.insert(0, str(HERE.parent / "jobs"))
import cov2d as c  # noqa: E402
import cov2d_jobs as cj  # noqa: E402
from deploy_fixture import clean_checkout  # noqa: E402
import noatime_emu  # noqa: E402

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
    (a / "pseudo_a.json").write_text(json.dumps({"truth": "G18", "verdict": "PASS", "pins_checked": True,
                                                 "pot": {"data": POT_DATA},
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
        self.deploy, self.head = clean_checkout(self.d / "deploy")
        p = mock.patch.object(pw, "DEPLOY", self.deploy)
        p.start()
        self.addCleanup(p.stop)
        emu = contextlib.ExitStack()
        emu.enter_context(noatime_emu.emulated(c, pw))
        self.addCleanup(emu.close)
        p = mock.patch.object(c, "SETTLE_WAIT", 0.0)
        p.start()
        self.addCleanup(p.stop)

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

    def test_the_writers_record_is_what_order_admits(self):
        # F1: the record step B itself writes, not a hand-written one, opens the pilot only for the deploy's commit
        # (A2's L1: with its pins checked, here against the fixture's own digests)
        import hashlib
        write_fixture(self.d, self.drv)
        fixture_pins = {k: (pw.PINS[k][0], hashlib.sha256((self.d / f).read_bytes()).hexdigest())
                        for k, f in (("er", "xsec.root"), ("mcfile", "mc.root"), ("flux_universe_file", "fluxu.root"))}
        buf = io.StringIO()
        with mock.patch.dict(pw.PINS, fixture_pins), contextlib.redirect_stdout(buf):
            code = pw.main(["--a", str(self.d / "a"), "--out", str(self.d / "out"), "--er", str(self.d / "xsec.root"),
                            "--mcfile", str(self.d / "mc.root"), "--flux-universe-file", str(self.d / "fluxu.root")])
        self.assertEqual(code, 0, buf.getvalue())
        rec = self.rec()
        self.assertEqual((rec["M"], rec["pins_checked"]), (self.head, True))
        path = cj.PSEUDO_RECORD.format(truth="G18")
        self.assertEqual(cj.order("pilot", "pilot", {path: rec}, set(), self.head), [])
        self.assertTrue(cj.order("pilot", "pilot", {path: dict(rec, pins_checked=False)}, set(), self.head))
        # A2's N1, the real sequence: binding 2's committed G18 and pilot records (by M and bytes) and this writer's
        # record as AR23's, at this deploy's M, open the universe jobs
        repo = HERE.parents[2]
        committed = {cj.PSEUDO_RECORD.format(truth="AR23"): rec}
        digests = {cj.PSEUDO_RECORD.format(truth="AR23"):
                   hashlib.sha256((self.d / "out" / "pseudo_b.json").read_bytes()).hexdigest()}
        for p in (cj.PSEUDO_RECORD.format(truth="G18"), cj.PILOT_RECORD):
            committed[p] = json.loads((repo / p).read_bytes())
            digests[p] = hashlib.sha256((repo / p).read_bytes()).hexdigest()
        self.assertEqual(cj.order("G18_Ua", "G18", committed, set(), self.head, digests), [])
        self.assertEqual(cj.order("AR23_Ua", "AR23", committed, set(), self.head, digests), [])
        self.assertTrue(cj.order("pilot", "pilot", {path: {k: v for k, v in rec.items() if k != "M"}}, set(), self.head))
        self.assertTrue(cj.order("pilot", "pilot", {path: dict(rec, M="f" * 40)}, set(), self.head))

    def test_a_dirty_deploy_is_refused_before_any_output(self):
        write_fixture(self.d, self.drv)
        (self.deploy / "untracked").write_text("x")
        with self.assertRaises(c.Refusal):
            self.run_b()
        self.assertFalse((self.d / "out").exists())

    def test_a_deploy_that_moves_during_step_b_stops(self):
        write_fixture(self.d, self.drv)
        with mock.patch.object(pw.c, "deploy_head", side_effect=[self.head, "f" * 40]):
            code, _ = self.run_b()
        self.assertEqual((code, self.rec()["verdict"]), (3, "STOP"))
        self.assertTrue(any("moved off" in x for x in self.rec()["stop"]))

    def test_inputs_are_staged_root_reads_working_copies_and_the_guard_records(self):
        import hashlib
        write_fixture(self.d, self.drv)
        code, text = self.run_b()
        self.assertEqual(code, 0, text)
        rec, stage = self.rec(), self.d / "out" / "stage"
        src = {"er": "xsec.root", "mcfile": "mc.root", "flux_universe_file": "fluxu.root"}
        self.assertEqual(set(rec["staged"]), set(src))
        for k, rel in src.items():
            v = rec["staged"][k]
            self.assertEqual((v["src"], Path(v["path"]).parent), (str(self.d / rel), stage))
            self.assertEqual(v["sha256"], hashlib.sha256((self.d / rel).read_bytes()).hexdigest())
            self.assertEqual(rec["inputs"][k]["staged"], v["path"])
        self.assertEqual(set(rec["atime_ns"]), {v["path"] for v in rec["staged"].values()})    # the staged copies only
        self.assertTrue(all(isinstance(x["before"], int) and x["before"] == x["after"] for x in rec["atime_ns"].values()))
        self.assertEqual((rec["atime_moved"], rec["verdict"]), ([], "PASS"))

    def test_a_plain_read_of_a_staged_copy_stops(self):
        write_fixture(self.d, self.drv)
        copy = self.d / "out" / "stage" / "er_xsec.root"
        real = pw.section_9_4

        def section_9_4(*a):      # mid-step, after the guard's first reading: a plain read of the private copy
            time.sleep(0.25)      # in a later clock tick than the copy's creation (A2 stage 1, attempt 1)
            with open(copy, "rb") as fh:
                fh.read()
            return real(*a)
        with mock.patch.object(pw, "section_9_4", section_9_4):
            code, _ = self.run_b()
        rec = self.rec()
        self.assertEqual((code, rec["verdict"], rec["atime_moved"]), (3, "STOP", [str(copy)]))
        self.assertGreater(rec["atime_ns"][str(copy)]["after"], rec["atime_ns"][str(copy)]["before"])

    def test_a_copy_whose_atime_will_not_settle_is_refused_before_the_work(self):
        # D2: a stand-in moves the staged copies' atime between every pair of readings
        write_fixture(self.d, self.drv)
        tick = iter(range(1, 10 ** 6))

        def sleep(_):
            for f in (self.d / "out" / "stage").iterdir():
                os.utime(f, ns=(next(tick) * 10 ** 9, os.stat(f).st_mtime_ns))
        with mock.patch("time.sleep", sleep):
            code, text = self.run_b()
        rec = self.rec()
        self.assertEqual((code, rec["verdict"], rec["stop"]), (2, "REFUSED", []))
        self.assertEqual(len(rec["settle_atime_ns"]), c.SETTLE_TRIES + 1)     # every reading is recorded
        self.assertEqual(sorted(p.name for p in (self.d / "out").glob("data_*.root")), [])
        self.assertIn("REFUSED", text)

    def test_a_pinned_step_b_refuses_an_unpinned_step_a(self):
        # A2's L1: otherwise a pinned step B after an unpinned step A would record pins_checked: true
        write_fixture(self.d, self.drv)
        p = self.d / "a" / "pseudo_a.json"
        p.write_text(json.dumps(dict(json.loads(p.read_text()), pins_checked=False)))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(c.Refusal) as e:
            pw.main(["--a", str(self.d / "a"), "--out", str(self.d / "out"), "--er", str(self.d / "xsec.root"),
                     "--mcfile", str(self.d / "mc.root"), "--flux-universe-file", str(self.d / "fluxu.root")])
        self.assertIn("pins unchecked", str(e.exception))
        self.assertFalse((self.d / "out").exists())

    def test_refuses_a_stopped_step_a(self):
        write_fixture(self.d, self.drv)
        p = self.d / "a" / "pseudo_a.json"
        p.write_text(json.dumps(dict(json.loads(p.read_text()), verdict="STOP")))
        with self.assertRaises(c.Refusal):
            self.run_b()

    def test_a_staged_input_off_its_pin_is_a_stop(self):
        # the director's ruling on A2 section 6: the declared input is not the pinned one
        write_fixture(self.d, self.drv)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = pw.main(["--a", str(self.d / "a"), "--out", str(self.d / "out"), "--er", str(self.d / "xsec.root"),
                            "--mcfile", str(self.d / "mc.root"), "--flux-universe-file", str(self.d / "fluxu.root")])
        rec = self.rec()
        self.assertEqual((code, rec["verdict"], len(rec["stop"])), (3, "STOP", 1))
        import hashlib
        self.assertEqual(rec["off_pin"], {"step": "step B", "input": "er", "src": str(self.d / "xsec.root"),
                                          "sha256": hashlib.sha256((self.d / "xsec.root").read_bytes()).hexdigest(),
                                          "pinned": pw.PINS["er"][1], "text": rec["stop"][0]})
        self.assertIn("step B: staged input er (", rec["stop"][0])
        self.assertEqual(rec["staged"], {})                       # the first input, E_R, is off its pin
        self.assertEqual(sorted(p.name for p in (self.d / "out").glob("data_*.root")), [])
        self.assertIn("COV2D-PSEUDO-B G18 STOP", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
