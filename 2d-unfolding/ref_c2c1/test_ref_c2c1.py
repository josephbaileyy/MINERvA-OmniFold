#!/usr/bin/env python3
"""Controls for ``ref_c2c1.py`` and ``ref_c2c1_read.py`` (REF-C2C1-DECLARATION.md §1-§4): each mechanism fires on its
defect and stays silent on the clean case.

The driver tests run E_R's real driver, in-process, on RE-2's own synthetic omnifile (``re2/tests/test_re2_driver.py``
``write_fixture``, post-Phase-18-shaped, through the driver's real loaders), with two OmniFold iterations. The reader
tests use hand-made ROOT products whose readings are known. Needs PyROOT, LightGBM, scikit-learn, scipy and matplotlib
(the cluster's root_6_28 environment); RooUnfold only for the C-ROO test, which is skipped unless
``REF_C2C1_ROOUNFOLD`` names a loadable libRooUnfold.so. LightGBM sizes its pool from the CPU affinity: run pinned, as
RE-2's suite says."""
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "re2" / "tests"))
import ref_c2c1 as C  # noqa: E402
import ref_c2c1_read as R  # noqa: E402
import test_re2_driver as T2  # noqa: E402  (RE-2's own fixture writer, not retyped)

ROOUNFOLD = os.environ.get("REF_C2C1_ROOUNFOLD")
TD = Path(tempfile.mkdtemp())
OMNI, FLUX = TD / "fx.root", TD / "flux.root"
T2.write_fixture(OMNI, FLUX)
DRIVER, OHF = C.load_driver()
CFG = json.loads(C.CONFIG.read_text())
CFG["inputs"].update(CV=str(OMNI), MC=str(FLUX))
CFG["e_r"]["argv"] = ["--omnifile", "$CV", "--mcfile", "$MC", "--iters", "2", "--use-weights", "--estimator", "lgbm",
                      "--seed", "42", "--branch-select", "all", "--bkg-mode", "negweight-refined",
                      "--refine-n-estimators", "400", "--refine-num-leaves", "31"]
CFG["c1"]["threads"] = 2
KS = CFG["c2"]["iterations"]["scan"]


def run(unit, out, **kw):
    return C.run_unit(DRIVER, OHF, CFG, unit, out, unfolder=kw.pop("unfolder", C.dagostini), **kw)


class Ibu(unittest.TestCase):
    def test_dagostini_by_hand(self):
        M = np.array([[8.0, 1.0], [2.0, 6.0]])  # reco x truth; truth columns 10 and 10 (efficiencies 1 and 0.7)
        T = np.array([10.0, 10.0])
        y = np.array([9.0, 4.0])
        R = M / T
        u1 = T * (R.T @ (y / (R @ T))) / R.sum(axis=0)  # one update, written out
        got = C.dagostini(M, T, y, [1, 200])
        np.testing.assert_allclose(got[1], u1, rtol=1e-14)
        truth = np.linalg.solve(R, y)  # y = R u has an exact positive solution here: IBU converges to it
        self.assertTrue(np.all(truth > 0))
        np.testing.assert_allclose(got[200], truth, rtol=1e-8)
        fixed = C.dagostini(M, T, M.sum(axis=1), [1, 5, 20])
        for k in (1, 5, 20):
            np.testing.assert_allclose(fixed[k], T, rtol=1e-14)

    def test_c_sim_fires_on_a_chain_defect(self):
        M = np.array([[8.0, 1.0], [2.0, 6.0]])
        cap = C.Capture(T=np.array([10.0, 10.0]), M=M)
        self.assertTrue(C.c_sim(cap, C.dagostini, KS, 1e-9)["pass"])
        broken = lambda M, T, y, ks: {k: v * (1 + 1e-6) for k, v in C.dagostini(M, T, y, ks).items()}  # noqa: E731
        self.assertFalse(C.c_sim(cap, broken, KS, 1e-9)["pass"])

    @unittest.skipUnless(ROOUNFOLD, "C-ROO needs libRooUnfold.so (REF_C2C1_ROOUNFOLD)")
    def test_roounfold_bayes_is_the_same_update(self):
        rng = np.random.default_rng(3)
        M = rng.uniform(0, 5, (6, 6)) + np.diag(rng.uniform(20, 30, 6))
        T = M.sum(axis=0) * rng.uniform(1.1, 1.5, 6)
        y = M @ rng.uniform(0.8, 1.2, 6)
        a, b = C.roounfold_bayes(M, T, y, KS, ROOUNFOLD), C.dagostini(M, T, y, KS)
        for k in KS:
            np.testing.assert_allclose(a[k], b[k], rtol=1e-9)


class Driver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = TD / "units"
        for u in (("er", None), ("c2_central", None), ("c1_central", None)):
            assert run(u, cls.out) == 0

    def test_c2_is_e_rs_pipeline_with_ibu_in_the_omnifold_seam(self):
        z = np.load(self.out / "c2_central.npz")
        m = json.loads(str(z["meta"]))
        self.assertTrue(m["controls"]["C-SIM"]["pass"])
        h = R.th2(self.out / "c2_central.root")  # the driver's own fill and extraction at the primary K
        x = z["xsec"][list(z["ks"]).index(CFG["c2"]["iterations"]["primary"])]
        self.assertLess(R.rel(x, h), 1e-12)
        self.assertAlmostEqual(float(z["y"].sum()), m["measured_weights_sum"], places=9)  # y is the driver's own w~
        self.assertEqual(len(z["ks"]), len(KS))
        self.assertFalse(np.array_equal(z["xsec"][0], z["xsec"][-1]))  # K moves the result

    def test_er_is_the_driver_unchanged(self):
        out = TD / "plain.root"
        argv = ["re2_driver.py", *C.resolve_argv(CFG, None), "--out", str(out)]
        code = (f"import sys, runpy; sys.path.insert(0, {str(C.HELPER)!r}); import omnifold; sys.argv = {argv!r}; "
                f"runpy.run_path({str(C.RE2)!r}, run_name='__main__')")
        subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, env=dict(os.environ, OMP_NUM_THREADS="1"))
        self.assertLess(R.rel(R.th2(self.out / "er.root"), R.th2(out)), 1e-8)

    def test_c1_differs_from_e_r_by_exactly_the_four_keys(self):
        er, c1 = R.lgbm(self.out, "er"), R.lgbm(self.out, "c1_central")
        res = R.c_set(er, c1, CFG["c1"]["deterministic_keys"])
        self.assertTrue(res["pass"], res)
        self.assertEqual(sorted(r["kind"] for r in res["constructions"]), ["classifier"] * 3 + ["regressor"])
        self.assertIn([400, 31], [[e["params"]["n_estimators"], e["params"]["num_leaves"]] for e in er])  # refinement
        extra = copy.deepcopy(c1)
        extra[0]["params"]["min_child_samples"] = 7
        self.assertFalse(R.c_set(er, extra, CFG["c1"]["deterministic_keys"])["pass"])
        missing = copy.deepcopy(c1)
        missing[1]["params"].pop("deterministic")
        self.assertFalse(R.c_set(er, missing, CFG["c1"]["deterministic_keys"])["pass"])

    def test_the_background_stream_guard_both_ways(self):
        out = TD / "bkgstream"
        self.assertEqual(run(("c2_replica", 3), out), 0)  # the real input as it is: no fakes, the guard silent
        real = DRIVER.collect_signal_arrays_2d

        def planted(*a, **k):
            sig = real(*a, **k)
            i = int(np.flatnonzero(np.asarray(sig["pass_reco"], bool) & np.asarray(sig["pass_truth"], bool))[0])
            sig["pass_truth"] = np.array(sig["pass_truth"], bool, copy=True)
            sig["pass_truth"][i] = False  # one signal fake inside the binning
            return sig

        with mock.patch.object(DRIVER, "collect_signal_arrays_2d", planted), \
                self.assertRaises((SystemExit, RuntimeError)) as cm:
            run(("c2_replica", 4), out)
        self.assertIn("fakes", str(cm.exception))  # the driver's own guard (re2_driver.py:1920-1922), not another error

    def test_a_unit_without_a_pass_marker_is_never_done(self):
        out = TD / "done"
        shutil.copytree(self.out, out, dirs_exist_ok=True)
        self.assertEqual(run(("c2_central", None), out), 0)  # PASS: skipped
        (out / "c2_central.done").write_text(json.dumps({"verdict": "FAIL"}))
        self.assertEqual(run(("c2_central", None), out), C.RC_CONTROL)
        (out / "c2_central.done").unlink()
        self.assertEqual(run(("c2_central", None), out), C.RC_CONTROL)


class Units(unittest.TestCase):
    def test_the_replica_set_is_bound_at_step_two(self):
        cfg = copy.deepcopy(CFG)
        with self.assertRaises(C.GateFailure):
            C.parse_units(cfg, ["c2_replica:3"])
        cfg["replica_set"]["choice"] = "reuse"
        self.assertEqual(C.parse_units(cfg, ["c2_replica:300"]), [("c2_replica", 300)])
        with self.assertRaises(ValueError):
            C.parse_units(cfg, ["c2_replica:301"])
        cfg["replica_set"]["choice"] = "new"
        self.assertEqual(C.parse_units(cfg, ["c2_replica:301"]), [("c2_replica", 301)])
        with self.assertRaises(ValueError):
            C.parse_units(cfg, ["c2_replica:3"])
        with self.assertRaises(ValueError):
            C.parse_units(cfg, ["c1_replica:51"])

    def test_the_argv_is_e_rs_and_a_replica_adds_its_streams(self):
        a = C.resolve_argv(CFG, None)
        self.assertNotIn("$CV", a)
        self.assertEqual(C.resolve_argv(CFG, 7)[len(a):], ["--bootstrap-seed", "7", "--bootstrap-streams", "three"])
        real = json.loads(C.CONFIG.read_text())["e_r"]["argv"]
        self.assertEqual(real[real.index("--refine-n-estimators") + 1], "400")
        self.assertEqual(real[real.index("--seed") + 1], "42")


# ============================================================================== reader


PT, PZ = DRIVER.PT_EDGES, DRIVER.PZ_EDGES


def write_th2(path: Path, v: np.ndarray, name="hXSec2D", refinement: dict | None = None):
    import ROOT
    f = ROOT.TFile.Open(str(path), "RECREATE")
    h = ROOT.TH2D(name, "", 14, np.asarray(PT, float), 16, np.asarray(PZ, float))
    for g in range(224):
        h.SetBinContent(g // 16 + 1, g % 16 + 1, float(v[g]))
    h.Write()
    if refinement is not None:
        ROOT.TNamed("re2Refinement", json.dumps(refinement, sort_keys=True)).Write()
    f.Close()


class Fixture:
    """Hand-made products: a publication, E_R, the units and their replicas, with the readings known."""

    def __init__(self, ibu_shift: float = 0.0, toward_paper: bool = False, n_c2: int = 40, n_c1: int = 20):
        import ROOT
        rng = np.random.default_rng(1)
        self.tmp = Path(tempfile.mkdtemp())
        run, e = self.tmp / "run", self.tmp / "e"
        run.mkdir()
        e.mkdir()
        rep = np.ones(224, bool)
        rep[rng.choice(224, 19, replace=False)] = False  # 205 reported cells
        paper = np.where(rep, rng.uniform(1, 3, 224), 0.0) * 1e-39
        sig = 0.03 * paper
        f = ROOT.TFile.Open(str(self.tmp / "pub.root"), "RECREATE")
        h = ROOT.TH2D("pt_pl_cross_section", "", 14, np.asarray(PT, float), 16, np.asarray(PZ, float))
        for g in range(224):
            h.SetBinContent(g // 16 + 1, g % 16 + 1, paper[g])
        h.Write()
        for name, scale in (("TotalCovariance", 1.0), ("StatOnlyCovariance", 0.3)):
            m = ROOT.TMatrixD(224, 224)
            for g in np.flatnonzero(rep):
                m[int(g)][int(g)] = scale * sig[g] ** 2
            m.Write(name)
        f.Close()
        ref = {"params": {"n_estimators": 400}, "signed_sum": 100.0, "refined_sum": 99.0, "clipped_fraction": 0.01}
        self.x_er = paper * (1 + 0.05 * np.where(rep, 1, 0))
        write_th2(e / "ER.root", self.x_er, refinement=ref)
        shutil.copy(e / "ER.root", run / "er.root")
        target = paper if toward_paper else self.x_er * (1 + ibu_shift)
        np.savez(run / "c2_central.npz", ks=np.array(KS), xsec=np.tile(target, (len(KS), 1)),
                 meta=json.dumps({"measured_weights_sum": 99.0, "controls": {"C-SIM": {"pass": True},
                                                                           "C-ROO": {"pass": True}}}))
        write_th2(run / "c2_central.root", target, refinement=ref)
        noise = lambda: 0.005 * paper * rng.standard_normal(224)  # noqa: E731
        for b in range(1, n_c2 + 1):
            eb = self.x_er + noise()
            write_th2(e / f"S1_{b:03d}.root", eb)
            cb = (paper + noise()) if toward_paper else eb * (1 + ibu_shift) + 0.3 * noise()
            np.savez(run / f"c2_replica_b{b}.npz", ks=np.array(KS), xsec=np.tile(cb, (len(KS), 1)), meta="{}")
        lg = [{"kind": "classifier", "params": {"n_estimators": 100, "random_state": 42}}]
        keys = {k: True for k in CFG["c1"]["deterministic_keys"]}
        np.savez(run / "er.npz", lgbm_params=np.array(json.dumps(lg)), meta="{}")
        np.savez(run / "c1_central.npz", lgbm_params=np.array(json.dumps([{**lg[0], "params": {**lg[0]["params"],
                                                                                                **keys}}])), meta="{}")
        write_th2(run / "c1_central.root", self.x_er)
        for b in range(1, n_c1 + 1):
            write_th2(run / f"c1_replica_b{b}.root", R.th2(e / f"S1_{b:03d}.root") + 0.3 * noise())
        for p in run.glob("*.npz"):
            (run / f"{p.stem}.done").write_text(json.dumps({"verdict": "PASS"}))
        for u in ("er", "c1_central"):
            (run / f"{u}.done").write_text(json.dumps({"verdict": "PASS"}))
        for b in range(1, n_c1 + 1):
            (run / f"c1_replica_b{b}.done").write_text(json.dumps({"verdict": "PASS"}))
        self.cfg = copy.deepcopy(CFG)
        chi2 = float(np.sum(((self.x_er - paper)[rep]) ** 2 / sig[rep] ** 2))
        self.cfg["publication"].update(path=str(self.tmp / "pub.root"), sha256=C.sha256(self.tmp / "pub.root"),
                                       c_pub={"chi2": chi2, "ndf": 205, "rtol": 1e-8})
        self.cfg["e_r"].update(central=str(e / "ER.root"), central_sha256=C.sha256(e / "ER.root"),
                               replica=str(e / "S1_{b:03d}.root"))
        self.cfg["replica_set"]["choice"] = "reuse"
        self.cfg["replica_set"]["options"]["reuse"].update(first=1, last=n_c2)
        self.cfg["c1"]["replicas"].update(first=1, last=n_c1)
        self.run, self.out = run, self.tmp / "out"
        self.out.mkdir()
        self.cells = self.out / "cells.root"
        R.write_cells(self.cfg, self.cells)

    def read(self, sha=None):
        return R.read(self.cfg, self.run, self.cells, sha or C.sha256(self.cells), self.out / "readout.json")

    def close(self):
        shutil.rmtree(self.tmp)


class Readings(unittest.TestCase):
    def test_the_rank_rule(self):
        self.assertEqual([R.rank_for(n, CFG) for n in (300, 200, 50)], [75, 50, 12])

    def test_the_leave_one_out_null_on_a_known_answer(self):
        """No difference: T falls above the null's maximum about 1 / (N + 1) of the time; a large difference
        always does."""
        rng = np.random.default_rng(5)
        n, p = 60, 20
        A = rng.standard_normal((p, p)) / np.sqrt(p) + np.eye(p)
        above = 0
        trials = 120
        for _ in range(trials):
            D = rng.standard_normal((n, p)) @ A.T
            t = R.t_and_null(rng.standard_normal(p) @ A.T, D, R.rank_for(n, CFG))
            above += t["T"] > t["max"]
        self.assertLess(above / trials, 0.06)
        D = rng.standard_normal((n, p)) @ A.T
        self.assertEqual(R.classify_t(R.t_and_null(D.mean(axis=0) + 10 * (A @ np.ones(p)), D, 15),
                                      ("agree", "marginal", "differ")), "differ")

    def test_the_rho_classes_at_their_bars(self):
        c = lambda lo, hi, r1="agree": R.classify_rho(lo, hi, r1, CFG)  # noqa: E731
        self.assertEqual(c(0.75, 1.3333333333333333), "input side")
        self.assertEqual(c(0.74, 1.0), "unresolved")
        self.assertEqual(c(0.9, 1.34), "unresolved")
        self.assertEqual(c(0.1, 0.5, "differ"), "algorithm side")
        self.assertEqual(c(0.1, 0.5, "marginal"), "unresolved")
        self.assertEqual(c(0.1, 0.51, "differ"), "unresolved")
        self.assertEqual(c(1.34, 2.0), "IBU farther: no attribution")

    def test_the_readings_on_known_products(self):
        for kw, r1, r2 in (({}, "agree", "input side"), ({"toward_paper": True}, "differ", "algorithm side")):
            fx = Fixture(**kw)
            try:
                rec = fx.read()
                with self.subTest(kw=kw):
                    self.assertNotIn("stopped", rec, rec.get("controls"))
                    k = rec[f"K{CFG['c2']['iterations']['primary']}"]
                    self.assertEqual(k["C2-R1"]["reading"], r1)
                    self.assertEqual(k["C2-R1"]["rank"], 10)
                    self.assertEqual(k["C2-R2"], r2)
                    lo, hi = k["rho_interval"]  # the replicas' central 90 % interval, not the point
                    self.assertLess(lo, hi)
                    self.assertTrue(lo <= k["rho"] <= hi or r2 == "algorithm side")
                    self.assertIn(f"K{CFG['c2']['iterations']['second']}", rec)
                    self.assertEqual(set(rec["D_IBU_every_K"]), set(KS))
                    self.assertEqual(rec["C1-R1"]["reading"], "equivalent")
                    self.assertTrue((fx.out / "readout.json").exists())
            finally:
                fx.close()

    def test_c_pub_reads_the_comparisons_own_chi2(self):
        fx = Fixture()
        try:
            rec = fx.read()
            self.assertTrue(rec["controls"]["C-PUB"]["pass"])
            self.assertEqual(rec["ndf"], 205)
        finally:
            fx.close()


class Controls(unittest.TestCase):
    def stopped(self, fx, name):
        rec = fx.read()
        self.assertTrue(rec.get("stopped"), name)
        self.assertIn(name, rec["stopped_by"])
        self.assertFalse((fx.out / "readout.json").exists())
        self.assertTrue((fx.out / "STOP.json").exists())

    def test_each_control_stops_the_read(self):
        cases = {
            "C-CV": lambda fx: write_th2(fx.run / "er.root", fx.x_er * (1 + 1e-6),
                                         refinement=json.loads(R.named(fx.run / "c2_central.root", "re2Refinement"))),
            "C-PUB": lambda fx: fx.cfg["publication"]["c_pub"].update(chi2=fx.cfg["publication"]["c_pub"]["chi2"] * 1.001),
            "C-SET": lambda fx: np.savez(fx.run / "c1_central.npz", lgbm_params=np.array(json.dumps(
                [{"kind": "classifier", "params": {"n_estimators": 100, "random_state": 42, "deterministic": True}}])),
                meta="{}"),
            "C-REF": lambda fx: write_th2(fx.run / "c2_central.root", fx.x_er, refinement={
                "params": {"n_estimators": 400}, "signed_sum": 100.5, "refined_sum": 99.0, "clipped_fraction": 0.01}),
            "C-SIM": lambda fx: np.savez(fx.run / "c2_central.npz", ks=np.array(KS), xsec=np.tile(fx.x_er, (len(KS), 1)),
                                         meta=json.dumps({"measured_weights_sum": 99.0, "controls": {
                                             "C-SIM": {"pass": False}, "C-ROO": {"pass": True}}})),
            "done": lambda fx: (fx.run / "c2_replica_b7.done").write_text(json.dumps({"verdict": "FAIL"})),
            "C-IN": lambda fx: fx.cfg["e_r"].update(central_sha256="0" * 64),
        }
        for name, tamper in cases.items():
            fx = Fixture()
            try:
                tamper(fx)
                with self.subTest(control=name):
                    self.stopped(fx, name)
            finally:
                fx.close()

    def test_the_cells_are_bound_index_by_index(self):
        import ROOT
        import reported_cells as rc
        fx = Fixture()
        try:
            with self.assertRaises(R.Refused):
                fx.read(sha="0" * 64)
            cells, _ = rc.read_cells(ROOT.TFile.Open(str(fx.cells)))
            shifted = np.sort(np.concatenate([cells[1:], [int(np.setdiff1d(np.arange(224), cells)[0])]]))
            f = ROOT.TFile.Open(str(fx.cells), "RECREATE")  # 205 cells, one of them another cell: same count
            rc.identity_hist(shifted).Write()
            f.Close()
            self.stopped(fx, "C-CELLS")
        finally:
            fx.close()


def tearDownModule():
    shutil.rmtree(TD, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
