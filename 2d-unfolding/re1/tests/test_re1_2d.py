"""Unit and fixture tests for the RE-1 2D path (``2d-unfolding/re1/re1_2d.py``).

Needs PyROOT and numpy. The unit tests stub LightGBM, so they also run where it is absent:
    PYTHONPATH=$(root-config --libdir) python3.13 -m unittest 2d-unfolding/re1/tests/test_re1_2d.py -v
``DriverEquivalence`` needs LightGBM and scikit-learn (the cluster's ``root_6_28`` environment) and is
skipped otherwise. LightGBM sizes its default thread pool from the process's CPU affinity and ignores
OMP_NUM_THREADS, so on a login node run it pinned, e.g. ``taskset -c 8-11 python -m unittest ...``. It runs the frozen driver's ``main()`` and this path on one synthetic omnifile, and
requires the same ``hXSec2D`` bit for bit: purity at the driver's settings, and the refinement with the
400/31 override removed (the driver's ``negweight-refined``), so the only difference left in
production is the override itself.
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
RE1 = HERE.parents[1]
REPO = HERE.parents[3]
sys.path.insert(0, str(RE1))

try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False
try:
    import lightgbm  # noqa: F401
    import sklearn  # noqa: F401
    HAVE_LGBM = True
except Exception:
    HAVE_LGBM = False

if HAVE_ROOT:
    import re1_2d as R
    U2D, _ = None, None


def u2d():
    global U2D
    if U2D is None:
        sys.path.insert(0, str(REPO / "2d-unfolding"))
        import unfold_2d_omnifold_unbinned as m
        U2D = m
    return U2D


def synthetic_cache(seed=7, n=4000, nb=1500, nd=3000):
    """A cache-shaped dict on the driver's grid, every reco row strictly inside the window."""
    rng = np.random.default_rng(seed)
    pt = rng.uniform(0.01, 2.4, n)
    pz = rng.uniform(1.6, 19.0, n)
    pass_truth = np.ones(n, bool)
    pass_reco = rng.uniform(size=n) < 0.7
    rpt = np.where(pass_reco, np.clip(pt * rng.normal(1, 0.05, n), 0.001, 4.4), -9999.0)
    rpz = np.where(pass_reco, np.clip(pz * rng.normal(1, 0.05, n), 1.51, 59.0), -9999.0)
    c = {"sig_truth_pt": pt, "sig_truth_pz": pz, "sig_reco_pt": rpt, "sig_reco_pz": rpz,
         "sig_pass_reco": pass_reco, "sig_pass_truth": pass_truth,
         "sig_w_truth": rng.uniform(0.1, 0.3, n), "sig_w_reco": rng.uniform(0.1, 0.3, n),
         "bkg_pt": rng.uniform(0.01, 2.4, nb), "bkg_pz": rng.uniform(1.6, 19.0, nb),
         "bkg_w": rng.uniform(0.0, 0.3, nb), "meas_pt": rng.uniform(0.01, 2.4, nd),
         "meas_pz": rng.uniform(1.6, 19.0, nd), "den_pt": pt, "den_pz": pz,
         "flux_bins": np.full(14, 1e-3)}
    c["den_w"] = c["sig_w_truth"].copy()
    c["bkg_w"][::50] = 0.0
    meta = {"pt_edges": [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50],
            "pz_edges": [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0],
            "data_pot": 1e21, "n_nucleons": 3e30}
    return c, meta


class FakeClassifier:
    def __init__(self, params):
        self.params = params

    def get_params(self):
        return dict(self.params)

    def fit(self, x, y, sample_weight=None):
        self.p = float(np.average(y, weights=sample_weight))
        return self

    def predict_proba(self, x):
        p = np.full(x.shape[0], self.p)
        return np.column_stack([1 - p, p])


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class Sampling(unittest.TestCase):
    def test_pseudo_matches_s5n_draw(self):
        """Same seed -> the same observed rows, counts, template and unfolding half as s5n's build_pseudo."""
        c, meta = synthetic_cache()
        _, s5n = R.nd_modules()
        inputs = {"MCgen": np.column_stack([c["sig_truth_pt"], c["sig_truth_pz"]]),
                  "MCreco": np.column_stack([c["sig_reco_pt"], c["sig_reco_pz"]]),
                  "pass_reco": c["sig_pass_reco"], "pass_truth": c["sig_pass_truth"],
                  "w_truth": c["sig_w_truth"], "w_reco": c["sig_w_reco"],
                  "edges": [np.array(meta["pt_edges"]), np.array(meta["pz_edges"])],
                  "denom_nd": np.ones((14, 16)), "flux": c["flux_bins"], "data_pot": 1e21, "n_nucleons": 3e30}
        bkg = {"bkg_reco": np.column_stack([c["bkg_pt"], c["bkg_pz"]]), "bkg_w": c["bkg_w"]}
        for seed in (1, 2, 20):
            key, _ = R.split_keys(seed)
            ref, _, _ = s5n.build_pseudo(inputs, bkg, "nominal", 0.0, key, seed)
            ours = R.build_pseudo(c, seed)
            np.testing.assert_array_equal(np.column_stack([ours["obs_pt"], ours["obs_pz"]]), ref["obs"])
            np.testing.assert_array_equal(ours["obs_counts"], ref["obs_counts"])
            keep = ours["tmpl_w"] > 0  # s5n drops nothing here either: its window keeps every row
            np.testing.assert_array_equal(np.column_stack([ours["tmpl_pt"], ours["tmpl_pz"]]), ref["tmpl"])
            np.testing.assert_array_equal(ours["tmpl_w"], ref["tmpl_w"])
            self.assertTrue(keep.any())
            np.testing.assert_array_equal(ours["sig"]["w_truth"], ref["w_truth"])
            np.testing.assert_array_equal(ours["sig"]["w_reco"], ref["w_reco"])

    def test_halves_partition_and_scale(self):
        c, _ = synthetic_cache()
        e = R.build_pseudo(c, 3)
        n_a, n_b = e["info"]["n_half_a"], e["info"]["n_half_b"]
        self.assertEqual(n_a + n_b, c["sig_w_truth"].size)
        self.assertEqual(e["sig"]["w_truth"].size, n_a)
        self.assertEqual(e["truth_sig"]["w_truth"].size, n_b)
        self.assertEqual(e["info"]["n_bkg_source_c"] + e["info"]["n_bkg_template_d"], c["bkg_w"].size)
        self.assertGreater(min(n_a, n_b), 0.4 * c["sig_w_truth"].size)
        a = ~R.nd_modules()[0].half_mask(c["sig_w_truth"].size, e["info"]["split_key"])
        np.testing.assert_array_equal(e["sig"]["w_truth"], 2.0 * c["sig_w_truth"][a])

    def test_seed_changes_draw(self):
        c, _ = synthetic_cache()
        a, b = R.build_pseudo(c, 1), R.build_pseudo(c, 2)
        self.assertNotEqual(a["info"]["split_key"], b["info"]["split_key"])
        self.assertFalse(np.array_equal(a["obs_counts"][:50], b["obs_counts"][:50]))


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class Arms(unittest.TestCase):
    def setUp(self):
        self.c, self.meta = synthetic_cache()
        self.exp = R.build_pseudo(self.c, 5)
        self.edges = (self.meta["pt_edges"], self.meta["pz_edges"])

    def test_purity_equals_s5c_weights(self):
        s5c, _ = R.nd_modules()
        pt, pz, w, ev = R.purity_measured(u2d(), self.exp, self.edges)
        b = ev["h_bkg"][1:-1, 1:-1]
        coords = np.column_stack([pt, pz])
        ref = s5c.purity_weights(coords, self.exp["obs_counts"], b, [np.array(e) for e in self.edges])
        np.testing.assert_allclose(w, ref, rtol=1e-12, atol=0)
        np.testing.assert_array_equal(pt, self.exp["obs_pt"])

    def test_both_arms_see_the_same_observed_rows(self):
        pt_p, pz_p, _, _ = R.purity_measured(u2d(), self.exp, self.edges)
        pt_s, pz_s, w_s = R.signed_sample(self.exp)
        n = self.exp["obs_pt"].size
        np.testing.assert_array_equal(pt_s[:n], pt_p)
        np.testing.assert_array_equal(pz_s[:n], pz_p)
        np.testing.assert_array_equal(w_s[:n], self.exp["obs_counts"])
        np.testing.assert_array_equal(w_s[n:], -self.exp["tmpl_w"])
        self.assertEqual(w_s.size, n + self.exp["tmpl_w"].size)  # zero-weight template rows kept, as the driver

    def test_refinement_override_reaches_the_classifier(self):
        m = u2d()
        orig = m._make_bkg_classifier
        m._make_bkg_classifier = lambda est, params, dev: FakeClassifier({**R.LGBM_DEFAULTS, **params})
        try:
            _, _, w, ev = R.refined_measured(m, self.exp, 42)
        finally:
            m._make_bkg_classifier = orig
        p = ev["classifier_params"]
        self.assertEqual((p["n_estimators"], p["num_leaves"], p["random_state"]), (400, 31, 45))
        self.assertTrue(np.all(w >= 0))

    def test_refinement_refuses_a_classifier_without_the_override(self):
        m = u2d()
        orig = m._make_bkg_classifier
        m._make_bkg_classifier = lambda est, params, dev: FakeClassifier(
            {**R.LGBM_DEFAULTS, "random_state": params["random_state"]})
        try:
            with self.assertRaisesRegex(RuntimeError, "n_estimators"):
                R.refined_measured(m, self.exp, 42)
        finally:
            m._make_bkg_classifier = orig


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class Fits(unittest.TestCase):
    def fits(self, iters=5, seeds=(42, 43, 44), reg=True):
        rec = []
        for _ in range(iters):
            rec.append({"class": "LGBMClassifier", "random_state": seeds[0], **R.LGBM_DEFAULTS})
            if reg:
                rec.append({"class": "LGBMRegressor", "random_state": seeds[2], **R.LGBM_DEFAULTS})
            rec.append({"class": "LGBMClassifier", "random_state": seeds[1], **R.LGBM_DEFAULTS})
        return rec

    def test_accepts_the_driver_parameters(self):
        out = R.check_omnifold_fits(self.fits(), 42, 5)
        self.assertEqual(out["random_states"], [42, 43, 44])

    def test_refuses_a_wrong_seed(self):
        with self.assertRaisesRegex(RuntimeError, "random_state"):
            R.check_omnifold_fits(self.fits(seeds=(1, 2, 3)), 42, 5)

    def test_refuses_a_wrong_capacity_or_count(self):
        rec = self.fits()
        rec[0]["num_leaves"] = 31
        with self.assertRaisesRegex(RuntimeError, "num_leaves"):
            R.check_omnifold_fits(rec, 42, 5)
        with self.assertRaisesRegex(RuntimeError, "classifier"):
            R.check_omnifold_fits(self.fits(iters=4), 42, 5)


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class Truth(unittest.TestCase):
    def test_nominal_truth_is_the_denominator_cross_section(self):
        """At r = 1 the truth is B's truth over B's completeness: the full denominator's cross section."""
        c, meta = synthetic_cache()
        e = R.build_pseudo(c, 9)
        xt = R.xsec(u2d(), e["truth_sig"], None, c, meta)
        full = R.xsec(u2d(), R.sig_dict(c, slice(None)), None, c, meta)
        ok = xt > 0
        self.assertTrue(ok.sum() > 50)
        np.testing.assert_allclose(xt[ok], full[ok], rtol=1e-12)

    def test_unit_weights_reproduce_the_truth(self):
        c, meta = synthetic_cache()
        s = R.sig_dict(c, slice(None))
        x1 = R.xsec(u2d(), s, np.ones(int(s["pass_truth"].sum())), c, meta)
        x0 = R.xsec(u2d(), s, None, c, meta)
        np.testing.assert_array_equal(x1, x0)
        with self.assertRaisesRegex(RuntimeError, "mismatch"):
            R.xsec(u2d(), s, np.ones(3), c, meta)


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class Refusals(unittest.TestCase):
    def test_wrong_cache_digest_and_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            cache = Path(td) / "c.npz"
            np.savez(cache, meta=json.dumps({"schema": R.SCHEMA_CACHE}))
            out = Path(td) / "x.npz"
            self.assertEqual(R.main(["data", "--cache", str(cache), "--expect-cache-sha256", "0" * 64,
                                     "--arm", "purity", "--out", str(out)]), 4)
            self.assertEqual(R.main(["dump", "--omnifile", str(cache), "--mcfile", str(cache),
                                     "--expect-omnifile-sha256", "0" * 64, "--expect-mcfile-sha256", "0" * 64,
                                     "--out", str(cache)]), 3)


def write_fixture(path: Path, flux: Path, seed: int = 11, n: int = 6000) -> None:
    """A Phase-17-shaped omnifile: every truth-passing signal row is in mc_truth_denom, no fakes."""
    import ROOT
    rng = np.random.default_rng(seed)
    pt = rng.uniform(0.02, 2.0, n)
    pz = rng.uniform(1.6, 18.0, n)
    pt = np.minimum(pt, 0.3 * pz)  # inside the 20-degree truth cut
    sim_pass = (rng.uniform(size=n) < 0.7).astype(np.uint8)
    spt = np.clip(pt * rng.normal(1, 0.06, n), 0.001, 4.4)
    spz = np.clip(pz * rng.normal(1, 0.06, n), 1.51, 59.0)
    cols = {"MC": pt, "MC_pz": pz, "sim": spt, "sim_pz": spz, "sim_pass": sim_pass,
            "w_truth": rng.uniform(0.5, 1.5, n), "w_reco": rng.uniform(0.5, 1.5, n)}
    nb, nd = 2500, 4000
    bkg = {"sim_background": rng.uniform(0.02, 2.0, nb), "sim_background_pz": rng.uniform(1.6, 18.0, nb),
           "sim_background_pass": np.ones(nb, np.uint8), "w_bkg": rng.uniform(0.0, 2.0, nb)}
    data = {"measured": rng.uniform(0.02, 2.0, nd), "measured_pz": rng.uniform(1.6, 18.0, nd),
            "measured_pass": np.ones(nd, np.uint8)}
    den = {"MC": pt, "MC_pz": pz, "w_truth": cols["w_truth"]}
    from array import array
    f = ROOT.TFile.Open(str(path), "RECREATE")
    trees = []
    for name, c in (("mc_signal_reco", cols), ("mc_background", bkg), ("data", data), ("mc_truth_denom", den)):
        t = ROOT.TTree(name, name)
        bufs = {}
        for k, v in c.items():  # UChar_t for the pass flags, Double_t otherwise, as the real file
            code, leaf = ("B", "b") if v.dtype == np.uint8 else ("d", "D")
            bufs[k] = array(code, [0])
            t.Branch(k, bufs[k], f"{k}/{leaf}")
        for i in range(next(iter(c.values())).size):
            for k, v in c.items():
                bufs[k][0] = v[i].item()
            t.Fill()
        t.Write()
        trees.append(t)  # keep each tree alive until the file is closed
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


def th2(path: Path, name: str = "hXSec2D") -> np.ndarray:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    h = f.Get(name)
    out = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)] for i in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return out


@unittest.skipUnless(HAVE_ROOT and HAVE_LGBM, "needs PyROOT, LightGBM and scikit-learn")
class DriverEquivalence(unittest.TestCase):
    """This path against the frozen driver on one synthetic omnifile, one thread, two iterations."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        d = Path(cls.td.name)
        cls.omni, cls.flux, cls.cache = d / "fx.root", d / "flux.root", d / "cache.npz"
        env = dict(os.environ, OMP_NUM_THREADS="1")
        cls.env = env
        code = f"import sys; sys.path.insert(0, {str(HERE.parent)!r}); import test_re1_2d as t; " \
               f"from pathlib import Path; t.write_fixture(Path({str(cls.omni)!r}), Path({str(cls.flux)!r}))"
        subprocess.run([sys.executable, "-c", code], check=True, env=env)
        sha = R.sha256_path
        subprocess.run([sys.executable, str(RE1 / "re1_2d.py"), "dump", "--omnifile", str(cls.omni),
                        "--mcfile", str(cls.flux), "--expect-omnifile-sha256", sha(cls.omni),
                        "--expect-mcfile-sha256", sha(cls.flux), "--branch-select", "all", "--out", str(cls.cache)],
                       check=True, env=env)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def driver(self, out: Path, mode: str) -> np.ndarray:
        """The frozen driver, importing THIS checkout's helper (its hard-coded insert is outranked by
        pre-loading the module from this checkout, then main() reuses sys.modules['omnifold'])."""
        code = ("import sys, runpy; sys.path.insert(0, %r); import omnifold; "
                "sys.argv = ['unfold_2d_omnifold_unbinned.py', '--omnifile', %r, '--mcfile', %r, '--iters', '2', "
                "'--use-weights', '--estimator', 'lgbm', '--seed', '42', '--bkg-mode', %r, '--out', %r]; "
                "runpy.run_path(%r, run_name='__main__')") % (
            str(REPO / "unbinned_unfolding" / "python"), str(self.omni), str(self.flux), mode, str(out),
            str(REPO / "2d-unfolding" / "unfold_2d_omnifold_unbinned.py"))
        subprocess.run([sys.executable, "-c", code], check=True, env=self.env, cwd=str(out.parent))
        return th2(out)

    def ours(self, out: Path, arm: str, override: dict | None = None) -> np.ndarray:
        code = ("import sys; sys.path.insert(0, %r); import re1_2d as R; R.REFINE_OVERRIDE = %r; "
                "sys.exit(R.main(['data', '--cache', %r, '--expect-cache-sha256', %r, '--arm', %r, "
                "'--iters', '2', '--out', %r]))") % (
            str(RE1), R.REFINE_OVERRIDE if override is None else override, str(self.cache),
            R.sha256_path(self.cache), arm, str(out))
        subprocess.run([sys.executable, "-c", code], check=True, env=self.env)
        return np.load(out)["xsec"]

    def test_purity_equals_the_driver(self):
        d = Path(self.td.name)
        ref = self.driver(d / "drv_purity.root", "purity")
        got = self.ours(d / "ours_purity.npz", "purity")
        self.assertGreater(int((ref > 0).sum()), 20)
        np.testing.assert_array_equal(got, ref)

    def test_refined_without_override_equals_the_driver(self):
        d = Path(self.td.name)
        ref = self.driver(d / "drv_refined.root", "negweight-refined")
        got = self.ours(d / "ours_refined_100_8.npz", "refined", override={})
        np.testing.assert_array_equal(got, ref)
        with_override = self.ours(d / "ours_refined_400_31.npz", "refined")
        self.assertFalse(np.array_equal(with_override, ref))  # the override reaches the result


if __name__ == "__main__":
    unittest.main()
