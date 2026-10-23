"""Equivalence and power tests for the RE-2 driver (``2d-unfolding/re2/re2_driver.py``).

Needs PyROOT, numpy, LightGBM and scikit-learn (the cluster's ``root_6_28`` environment); skipped otherwise.
LightGBM sizes its thread pool from the CPU affinity and ignores OMP_NUM_THREADS, so run it pinned:
    taskset -c 8-11 python -m unittest 2d-unfolding/re2/tests/test_re2_driver.py -v

Every test runs ``driver_p1.py`` (the Stage C production copy, ``3056e625...``) and/or ``re2_driver.py`` on one
synthetic omnifile with one vertical universe, two iterations, and compares EVERY histogram in the outputs
(contents and errors) bit for bit:

* the purity arm equals ``driver_p1.py`` on the CV, a three-stream replica, a background-only replica and a
  universe (selective read);
* the refined arm without a size override equals ``driver_p1.py``'s own ``negweight-refined`` (CV, universe);
* with the 400/31 size, the result moves and the output records the classifier's parameters;
* the refined three-stream bootstrap with all factors 1 equals the refined CV;
* the refined background stream changes the injected weights exactly as an independent recomputation from the
  fixture's rows and the stream's draws says, and a three-stream replica's signed sum is the data and
  background factors' sum;
* the guards refuse the size options without the refined mode, and the P1 streams with plain ``negweight``.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
DRIVER_P1 = REPO / "2d-unfolding" / "driver_p1.py"
RE2 = REPO / "2d-unfolding" / "re2" / "re2_driver.py"
HELPER = REPO / "unbinned_unfolding" / "python"
UNIVERSE = ("MaCCQE", 0)

try:
    import ROOT  # noqa: F401
    import lightgbm  # noqa: F401
    import sklearn  # noqa: F401
    HAVE = True
except Exception:  # pragma: no cover
    HAVE = False


def write_fixture(path: Path, flux: Path, seed: int = 11, n: int = 6000) -> dict:
    """A post-Phase-18-shaped omnifile (no fakes) with one vertical universe in all four trees.
    Returns the background tree's columns, for the independent recomputations below."""
    import ROOT
    from array import array
    rng = np.random.default_rng(seed)
    pt = rng.uniform(0.02, 2.0, n)
    pz = rng.uniform(1.6, 18.0, n)
    pt = np.minimum(pt, 0.3 * pz)
    sim_pass = (rng.uniform(size=n) < 0.7).astype(np.uint8)
    spt = np.clip(pt * rng.normal(1, 0.06, n), 0.001, 4.4)
    spz = np.clip(pz * rng.normal(1, 0.06, n), 1.51, 59.0)
    wt, wr = rng.uniform(0.5, 1.5, n), rng.uniform(0.5, 1.5, n)
    u = f"{UNIVERSE[0]}_{UNIVERSE[1]}"
    cols = {"MC": pt, "MC_pz": pz, "sim": spt, "sim_pz": spz, "sim_pass": sim_pass, "w_truth": wt, "w_reco": wr,
            f"w_truth_{u}": wt * rng.uniform(0.8, 1.2, n), f"w_reco_{u}": wr * rng.uniform(0.8, 1.2, n)}
    nb, nd = 2500, 4000
    bpt = rng.uniform(0.0, 2.2, nb)            # some rows outside the reco window: overflow fills
    bpz = rng.uniform(1.4, 18.0, nb)
    bpass = (rng.uniform(size=nb) < 0.9).astype(np.uint8)
    bw = rng.uniform(0.0, 2.0, nb)
    bkg = {"sim_background": bpt, "sim_background_pz": bpz, "sim_background_pass": bpass, "w_bkg": bw,
           f"w_bkg_{u}": bw * rng.uniform(0.8, 1.2, nb)}
    data = {"measured": rng.uniform(0.02, 2.0, nd), "measured_pz": rng.uniform(1.6, 18.0, nd),
            "measured_pass": np.ones(nd, np.uint8)}
    den = {"MC": pt, "MC_pz": pz, "w_truth": wt, f"w_truth_{u}": cols[f"w_truth_{u}"]}
    f = ROOT.TFile.Open(str(path), "RECREATE")
    trees = []
    for name, c in (("mc_signal_reco", cols), ("mc_background", bkg), ("data", data), ("mc_truth_denom", den)):
        t = ROOT.TTree(name, name)
        bufs = {}
        for k, v in c.items():
            code, leaf = ("B", "b") if v.dtype == np.uint8 else ("d", "D")
            bufs[k] = array(code, [0])
            t.Branch(k, bufs[k], f"{k}/{leaf}")
        for i in range(next(iter(c.values())).size):
            for k, v in c.items():
                bufs[k][0] = v[i].item()
            t.Fill()
        t.Write()
        trees.append(t)
    ROOT.TParameter("double")("dataPOTUsed", 1.0e20).Write()
    ROOT.TParameter("double")("mcPOTUsed", 4.0e20).Write()
    ROOT.TParameter("int")("hasTruthOnlyMisses", 1).Write()
    f.Close()
    g = ROOT.TFile.Open(str(flux), "RECREATE")
    edges = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
    h = ROOT.TH1D("pTmu_reweightedflux_integrated", "", 14, edges)
    for i in range(1, 15):
        h.SetBinContent(i, 1e-3 * i)
    h.Write()
    g.Close()
    return {"pt": bpt, "pz": bpz, "pass": bpass, "w": bw, "nd": nd}


def hists(path: Path) -> dict:
    """Every histogram in the file: (contents, errors) including under- and overflow."""
    import ROOT
    f = ROOT.TFile.Open(str(path))
    out = {}
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        if obj.InheritsFrom("TH1"):
            n = obj.GetNcells()
            out[key.GetName()] = (np.array([obj.GetBinContent(i) for i in range(n)]),
                                  np.array([obj.GetBinError(i) for i in range(n)]))
    f.Close()
    return out


def named(path: Path, name: str) -> str:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    v = f.Get(name).GetTitle()
    f.Close()
    return v


@unittest.skipUnless(HAVE, "needs PyROOT, LightGBM and scikit-learn")
class RE2Driver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        d = Path(cls.td.name)
        cls.omni, cls.flux = d / "fx.root", d / "flux.root"
        cls.env = dict(os.environ, OMP_NUM_THREADS="1")
        code = (f"import sys; sys.path.insert(0, {str(HERE.parent)!r}); import test_re2_driver as t, json; "
                f"from pathlib import Path; b = t.write_fixture(Path({str(cls.omni)!r}), Path({str(cls.flux)!r})); "
                f"import numpy as np; np.savez({str(d / 'bkg.npz')!r}, **{{k: np.asarray(v) for k, v in b.items()}})")
        subprocess.run([sys.executable, "-c", code], check=True, env=cls.env)
        cls.bkg = dict(np.load(d / "bkg.npz"))
        cls.n = 0

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def run_driver(self, script: Path, *extra: str, check: bool = True):
        """One run on the fixture. The helper is pre-loaded from this checkout, so driver_p1's hard-coded
        insert reuses it (main() takes sys.modules['omnifold']); re2_driver imports it from here anyway."""
        type(self).n += 1
        out = Path(self.td.name) / f"out_{self.n}.root"
        argv = [script.name, "--omnifile", str(self.omni), "--mcfile", str(self.flux), "--iters", "2",
                "--use-weights", "--estimator", "lgbm", "--seed", "42", "--out", str(out), *extra]
        code = (f"import sys, runpy; sys.path.insert(0, {str(HELPER)!r}); import omnifold; sys.argv = {argv!r}; "
                f"runpy.run_path({str(script)!r}, run_name='__main__')")
        r = subprocess.run([sys.executable, "-c", code], env=self.env, cwd=self.td.name, capture_output=True,
                           text=True)
        if check and r.returncode:
            raise AssertionError(f"{script.name} {extra} rc={r.returncode}\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
        return out, r

    def assert_same(self, a: Path, b: Path):
        ha, hb = hists(a), hists(b)
        self.assertEqual(sorted(ha), sorted(hb))
        self.assertIn("hXSec2D", ha)
        for k in ha:
            np.testing.assert_array_equal(ha[k][0], hb[k][0], err_msg=f"{k} contents")
            np.testing.assert_array_equal(ha[k][1], hb[k][1], err_msg=f"{k} errors")

    def refinement(self, path: Path) -> dict:
        return json.loads(named(path, "re2Refinement"))

    # ---------------------------------------------------------------- purity arm == driver_p1

    def test_purity_cv(self):
        a, _ = self.run_driver(DRIVER_P1, "--bkg-mode", "purity")
        b, _ = self.run_driver(RE2, "--bkg-mode", "purity")
        self.assert_same(a, b)

    def test_purity_three_stream_and_bkg_only(self):
        for streams in ("three", "bkg"):
            extra = ("--bkg-mode", "purity", "--bootstrap-seed", "3", "--bootstrap-streams", streams)
            a, _ = self.run_driver(DRIVER_P1, *extra)
            b, _ = self.run_driver(RE2, *extra)
            self.assert_same(a, b)

    def test_purity_universe_selective(self):
        extra = ("--bkg-mode", "purity", "--universe", f"{UNIVERSE[0]}:{UNIVERSE[1]}", "--branch-select", "derived")
        a, _ = self.run_driver(DRIVER_P1, *extra)
        b, _ = self.run_driver(RE2, *extra)
        self.assert_same(a, b)
        cv, _ = self.run_driver(RE2, "--bkg-mode", "purity")
        self.assertFalse(np.array_equal(hists(b)["hXSec2D"][0], hists(cv)["hXSec2D"][0]))  # the universe moves it

    # ---------------------------------------------------------------- refined arm

    def test_refined_without_size_equals_driver_p1(self):
        for extra in (("--bkg-mode", "negweight-refined"),
                      ("--bkg-mode", "negweight-refined", "--universe", f"{UNIVERSE[0]}:{UNIVERSE[1]}",
                       "--branch-select", "derived")):
            a, _ = self.run_driver(DRIVER_P1, *extra)
            b, _ = self.run_driver(RE2, *extra)
            self.assert_same(a, b)

    def test_size_reaches_the_classifier_and_moves_the_result(self):
        base, _ = self.run_driver(RE2, "--bkg-mode", "negweight-refined")
        big, _ = self.run_driver(RE2, "--bkg-mode", "negweight-refined", "--refine-n-estimators", "400",
                                 "--refine-num-leaves", "31")
        p = self.refinement(big)["params"]
        self.assertEqual(p, {"random_state": 45, "n_estimators": 400, "num_leaves": 31})
        self.assertEqual(self.refinement(base)["params"], {"random_state": 45})
        self.assertFalse(np.array_equal(hists(big)["hXSec2D"][0], hists(base)["hXSec2D"][0]))

    def test_refined_unit_factors_equal_the_refined_cv(self):
        size = ("--refine-n-estimators", "400", "--refine-num-leaves", "31")
        cv, _ = self.run_driver(RE2, "--bkg-mode", "negweight-refined", *size)
        unit, _ = self.run_driver(RE2, "--bkg-mode", "negweight-refined", *size, "--bootstrap-seed", "1",
                                  "--bootstrap-streams", "three", "--unit-factors")
        self.assert_same(cv, unit)

    def expected_injected(self, bootstrap_seed: int) -> tuple[float, np.ndarray]:
        """Independent of the driver: the fiducial rows of the fixture's background tree, their POT-scaled
        weights, and the stream's Poisson(1) draw over all entries (seed + 20,000,000)."""
        b = self.bkg
        pot_scale = 1.0e20 / 4.0e20
        ok = (b["pass"] == 1) & np.isfinite(b["w"]) & (b["w"] >= 0) & (b["w"] < 1e6)
        edges_pt, edges_pz = (0.0, 4.5), (1.5, 60.0)
        fid = ok & (b["pt"] >= edges_pt[0]) & (b["pt"] <= edges_pt[1]) & (b["pz"] >= edges_pz[0]) & \
            (b["pz"] <= edges_pz[1])
        factors = np.random.default_rng(bootstrap_seed + 20_000_000).poisson(1.0, size=b["w"].size).astype(float)
        return float((b["w"][fid] * pot_scale).sum()), float((factors[fid] * b["w"][fid] * pot_scale).sum())

    def test_background_stream_changes_exactly_the_injected_rows(self):
        nd = int(self.bkg["nd"])
        size = ("--refine-n-estimators", "400", "--refine-num-leaves", "31")
        cv, _ = self.run_driver(RE2, "--bkg-mode", "negweight-refined", *size)
        bk, _ = self.run_driver(RE2, "--bkg-mode", "negweight-refined", *size, "--bootstrap-seed", "3",
                                "--bootstrap-streams", "bkg")
        w_cv, w_star = self.expected_injected(3)
        r_cv, r_bk = self.refinement(cv), self.refinement(bk)
        self.assertAlmostEqual(r_cv["signed_sum"], nd - w_cv, delta=1e-9 * nd)
        self.assertAlmostEqual(r_bk["signed_sum"], nd - w_star, delta=1e-9 * nd)
        self.assertNotAlmostEqual(w_cv, w_star, places=3)
        self.assertTrue(r_bk["background_stream"])
        self.assertFalse(np.array_equal(hists(bk)["hXSec2D"][0], hists(cv)["hXSec2D"][0]))

    def test_three_stream_signed_sum(self):
        size = ("--refine-n-estimators", "400", "--refine-num-leaves", "31")
        rep, _ = self.run_driver(RE2, "--bkg-mode", "negweight-refined", *size, "--bootstrap-seed", "3",
                                 "--bootstrap-streams", "three")
        nd = int(self.bkg["nd"])
        b_data = np.random.default_rng(3).poisson(1.0, size=nd).astype(float)
        _, w_star = self.expected_injected(3)
        self.assertAlmostEqual(self.refinement(rep)["signed_sum"], b_data.sum() - w_star, delta=1e-9 * nd)

    # ---------------------------------------------------------------- guards

    def test_guards(self):
        _, r = self.run_driver(RE2, "--bkg-mode", "purity", "--refine-n-estimators", "400", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("need --bkg-mode negweight-refined", r.stdout + r.stderr)
        _, r = self.run_driver(RE2, "--bkg-mode", "negweight", "--bootstrap-seed", "1", "--bootstrap-streams",
                               "three", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("purity or negweight-refined", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
