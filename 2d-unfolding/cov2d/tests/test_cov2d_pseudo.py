"""cov2d_pseudo (the pseudo-data job's step A) on a synthetic $UNI written with uproot alone, so the tests run in
omnifold_py310, the environment step A runs in. uproot cannot write a TParameter, so ``read_pot`` is replaced by the
fixture's POT (its own test reads a stand-in object). The expected values are recomputed here independently of the
code under test: a plain loop for the composition, the ratio's bin lookup and rescale by hand, and a fresh generator
for the counts.
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_pseudo
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
import cov2d_pseudo as ps  # noqa: E402
import cov2d_receipt as rc  # noqa: E402

try:
    import uproot  # noqa: F401
    HAVE = True
except Exception:  # pragma: no cover
    HAVE = False

N, NB = 1500, 400
POT = (1.5e20, 4.5e20)
RHO = [0.7, 0.9, 1.1, 1.3, 1.6, 0.8, 1.2]


def universe_cols(prefix, cv, rng):
    """CV x (1 + 0.25 z) per universe, with a few rows driven negative so the clipping is exercised."""
    out = {}
    for b in c.ORDER:
        for i in range(c.BANDS[b]):
            u = cv * (1 + 0.25 * rng.standard_normal(cv.size))
            u[rng.integers(0, cv.size, 3)] *= -2.0
            out[c.column(prefix, b, i)] = u
    return out


def build(d: Path, truth_override=None):
    r = np.random.default_rng(31)
    pt = r.uniform(0.05, 1.0, N)
    pz = r.uniform(3.0, 15.0, N)
    gen = {"MC": pt, "MC_pz": pz, "MC_eavail": r.uniform(0.0, 2.5, N), "MC_q3": r.uniform(0.1, 1.5, N),
           "MC_W": r.uniform(0.9, 2.5, N)}
    w_t = r.uniform(0.5, 1.5, N)
    w_r = w_t * r.uniform(0.6, 1.0, N)
    truth = dict(gen, w_truth=w_t, **universe_cols("w_truth", w_t, r))
    if truth_override:
        truth_override(truth)
    sig = dict(gen, sim=pt + 0.02 * r.standard_normal(N), sim_pz=pz + 0.2 * r.standard_normal(N),
               sim_pass=(r.uniform(size=N) < 0.85).astype(np.int32), w_reco=w_r, w_truth=w_t,
               **universe_cols("w_reco", w_r, r))
    w_b = r.uniform(0.2, 0.8, NB)
    bkg = dict(sim_background=r.uniform(0.05, 1.0, NB), sim_background_pz=r.uniform(3.0, 15.0, NB),
               sim_background_pass=(r.uniform(size=NB) < 0.9).astype(np.int32), w_bkg=w_b,
               **universe_cols("w_bkg", w_b, r))
    with uproot.recreate(d / "uni.root") as f:
        f["mc_truth_denom"] = truth
        f["mc_signal_reco"] = sig
        f["mc_background"] = bkg
    with uproot.recreate(d / "cv.root") as f:
        f["data"] = {"measured": np.zeros(3)}
    (d / "constraint.txt").write_text("".join(f"Flux {i} {0.5 + (i % 7) / 10}\n" for i in range(100)))
    (d / "prep" / "bridged").mkdir(parents=True)
    import pvl_lib
    ratio = {"schema": "s5e-shape-ratio/1", "axes": [2], "edges": [list(pvl_lib.FINE["eavail"])], "shape_ratio": RHO}
    (d / "prep" / "bridged" / "genie_v3_g18.json").write_text(json.dumps(ratio))
    # where O_NOATIME is absent (macOS) a read can move atime; a future atime keeps it still, as the writer's tests do
    future = time.time() + 86400
    for f in ("uni.root", "cv.root", "constraint.txt", "prep/bridged/genie_v3_g18.json"):
        os.utime(d / f, (future, os.stat(d / f).st_mtime))
    return truth, sig, bkg


@unittest.skipUnless(HAVE, "needs uproot")
class PseudoA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.d = Path(cls.td.name)
        cls.truth, cls.sig, cls.bkg = build(cls.d)
        cls.patches = [mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True),
                       mock.patch.object(ps, "read_pot", lambda f: POT)]
        for p in cls.patches:
            p.start()
        cls.rc_main, cls.text = cls.run_main("out", 200_000)

    @classmethod
    def tearDownClass(cls):
        for p in cls.patches:
            p.stop()
        cls.td.cleanup()

    @classmethod
    def run_main(cls, name, chunk, d=None):
        d = d or cls.d
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = ps.main(["--truth", "G18", "--out", str(d / name), "--uni", str(d / "uni.root"),
                            "--cv", str(d / "cv.root"), "--prep", str(d / "prep"),
                            "--constraint", str(d / "constraint.txt"), "--chunk", str(chunk), "--no-pins"])
        return code, buf.getvalue()

    def rec(self, name="out"):
        return json.loads((self.d / name / "pseudo_a.json").read_text())

    # -------------------------------------------------------------- independent expectations
    def r_expected(self):
        import pvl_lib
        e = np.asarray(pvl_lib.FINE["eavail"])
        lims = [(pvl_lib.FINE[a][0], pvl_lib.FINE[a][-1]) for a in pvl_lib.AXES5]

        def raw(t):
            g = np.stack([t[k] for k in rc.TRUTH_VARS], axis=1)
            ok = np.all([(g[:, k] >= lo) & (g[:, k] <= hi) for k, (lo, hi) in enumerate(lims)], axis=0)
            b = np.clip(np.searchsorted(e, g[:, 2], side="right") - 1, 0, e.size - 2)
            return np.where(ok, np.asarray(RHO)[b], 1.0), ok
        rt, okt = raw(self.truth)
        rs, oks = raw(self.sig)
        w = self.truth["w_truth"]
        scale = w[okt].sum() / (w[okt] * rt[okt]).sum()
        return np.where(okt, rt * scale, 1.0), np.where(oks, rs * scale, 1.0)

    def composed(self, tree, prefix, draw):
        cv = tree[prefix].astype(np.float64)
        if draw is None:
            return cv.copy()
        out = tree[c.column(prefix, *draw.universes[0])].astype(np.float64).copy()
        for u in draw.universes[1:]:
            out += tree[c.column(prefix, *u)] - cv
        return out

    def natures(self):
        return ps.natures("G18", c.flux_weights((self.d / "constraint.txt").read_text()))

    # -------------------------------------------------------------- tests
    def test_pass_and_products(self):
        self.assertEqual(self.rc_main, 0, self.text)
        self.assertIn("COV2D-PSEUDO-A G18 PASS natures=301", self.text)
        out = self.d / "out"
        for s in list(c.TOY_SEEDS["G18"]) + [c.REALIZATION_SEED["G18"]]:
            self.assertTrue((out / f"counts_{s}.npz").exists(), s)
        rec = self.rec()
        self.assertEqual([t["seed"] for t in rec["toys"]], list(c.TOY_SEEDS["G18"]) + [5_721_000])
        self.assertEqual(rec["atime_moved"], [])
        self.assertEqual(rec["pot"]["scale"], POT[0] / POT[1])

    def test_seeds_are_the_declared_ranges(self):
        nat = self.natures()
        self.assertEqual([n["seed"] for n in nat[:-1]], list(range(5_720_000, 5_720_300)))
        self.assertEqual((nat[-1]["role"], nat[-1]["seed"], nat[-1]["draw"]), ("realization", 5_721_000, None))
        self.assertEqual(ps.natures("AR23", np.ones(100))[-1]["seed"], 5_731_000)

    def test_r_T_is_one_call_shared_by_both_trees(self):
        rt, rs = self.r_expected()
        r_t, r_s = ps.r_rows(json.loads((self.d / "prep/bridged/genie_v3_g18.json").read_text()),
                             np.stack([self.truth[k] for k in rc.TRUTH_VARS], axis=1), self.truth["w_truth"],
                             np.stack([self.sig[k] for k in rc.TRUTH_VARS], axis=1))
        np.testing.assert_allclose(r_t, rt, rtol=1e-13)
        np.testing.assert_allclose(r_s, rs, rtol=1e-13)
        np.testing.assert_array_equal(r_s, r_t)   # the fixture's signal rows carry the truth rows' kinematics

    def test_counts_equal_an_independent_draw(self):
        rt, rs = self.r_expected()
        s = POT[0] / POT[1]
        nat = self.natures()
        for k in (0, 1, 299, 300):
            n = nat[k]
            ls = self.composed(self.sig, "w_reco", n["draw"]) * rs * s
            lb = self.composed(self.bkg, "w_bkg", n["draw"]) * s
            g = np.random.default_rng([n["seed"], c.DRAW_SALT, 1])
            ks, kb = g.poisson(np.maximum(ls, 0)), g.poisson(np.maximum(lb, 0))
            z = np.load(self.d / "out" / f"counts_{n['seed']}.npz")
            np.testing.assert_array_equal(z["signal"], ks)
            np.testing.assert_array_equal(z["background"], kb)
            t = self.rec()["toys"][k]
            self.assertEqual(t["lambda"]["signal"]["rows_neg"], int((ls < 0).sum()))
            self.assertAlmostEqual(t["sum_lambda_plus"], float(np.maximum(ls, 0).sum() + np.maximum(lb, 0).sum()),
                                   places=9)

    def test_truth_is_clipped_row_by_row_in_the_phase_space(self):
        rt, _ = self.r_expected()
        s = POT[0] / POT[1]
        nat = self.natures()
        cell = rc.truth_cell(self.truth["MC"], self.truth["MC_pz"])
        z = np.load(self.d / "out" / "cells.npz")
        ok = cell >= 0
        clipped_any = False
        for k in (0, 7, 300):
            w = self.composed(self.truth, "w_truth", nat[k]["draw"]) * rt * s
            clipped_any |= bool(np.any(w[ok] < 0))
            np.testing.assert_allclose(z["truth_clipped"][k], np.bincount(cell[ok], np.maximum(w[ok], 0),
                                                                          minlength=z["truth_clipped"].shape[1]),
                                       rtol=1e-12)
            np.testing.assert_allclose(z["N"][k], np.bincount(cell[ok], w[ok], minlength=z["N"].shape[1]),
                                       rtol=1e-12, atol=1e-12)
        self.assertTrue(clipped_any, "the fixture must drive some truth composite negative")
        w1 = self.truth["w_truth"] * s
        np.testing.assert_allclose(z["truth_cv_r1"], np.bincount(cell[ok], np.maximum(w1[ok], 0),
                                                                 minlength=z["truth_cv_r1"].size), rtol=1e-12)

    def test_seen_sums_use_the_reco_kept_rows(self):
        import clip_probe as cp
        _, rs = self.r_expected()
        s = POT[0] / POT[1]
        n = self.natures()[3]
        lam = self.composed(self.sig, "w_reco", n["draw"]) * rs * s
        kept, _ = cp.reco_cell(self.sig["sim"], self.sig["sim_pz"], self.sig["sim_pass"])
        tc = rc.truth_cell(self.sig["MC"], self.sig["MC_pz"])
        ok = kept & (tc >= 0)
        z = np.load(self.d / "out" / "cells.npz")
        nc = z["S"].shape[1]
        np.testing.assert_allclose(z["S"][3], np.bincount(tc[ok], lam[ok], minlength=nc), rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(z["m_seen"][3], np.bincount(tc[ok], np.where(lam[ok] < 0, -lam[ok], 0),
                                                               minlength=nc), rtol=1e-12, atol=1e-15)

    def test_chunking_changes_nothing(self):
        code, text = self.run_main("out_chunk", 377)
        self.assertEqual(code, 0, text)
        for s in (5_720_000, 5_720_150, 5_721_000):
            a, b = np.load(self.d / "out" / f"counts_{s}.npz"), np.load(self.d / "out_chunk" / f"counts_{s}.npz")
            np.testing.assert_array_equal(a["signal"], b["signal"])
            np.testing.assert_array_equal(a["background"], b["background"])
        za, zb = np.load(self.d / "out" / "cells.npz"), np.load(self.d / "out_chunk" / "cells.npz")
        np.testing.assert_allclose(za["truth_clipped"], zb["truth_clipped"], rtol=1e-12)

    def test_refuses_an_existing_output(self):
        with self.assertRaises(FileExistsError):
            self.run_main("out", 200_000)


@unittest.skipUnless(HAVE, "needs uproot")
class Guards(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.d = Path(self.td.name)
        for p in (mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True),
                  mock.patch.object(ps, "read_pot", lambda f: POT)):
            p.start()
            self.addCleanup(p.stop)

    def run_main(self):
        return PseudoA.run_main("out", 200_000, d=self.d)

    def assert_r1_stop(self, override, key):
        build(self.d, override)
        code, text = self.run_main()
        self.assertEqual(code, 3, text)
        self.assertIn("R1:", text)
        rec = json.loads((self.d / "out" / "pseudo_a.json").read_text())
        self.assertGreater(rec["r1_counts"][key]["rows"], 0)
        self.assertEqual(sorted(p.name for p in (self.d / "out").glob("counts_*.npz")), [])

    def test_r1_weight_at_or_above_1e4_stops(self):
        def f(t):
            t["w_truth"][5] = 1e4
        self.assert_r1_stop(f, "w_ge_1e4")

    def test_r1_in_box_outside_the_phase_space_stops(self):
        def f(t):
            t["MC"][6], t["MC_pz"][6] = 4.0, 1.6     # theta near 68 degrees, inside the pT/p_par box
        self.assert_r1_stop(f, "box_outside_phase_space")

    def test_r1_nonfinite_stops(self):
        def f(t):
            t["MC_pz"][8] = np.nan
        self.assert_r1_stop(f, "nonfinite")

    def test_r1_counts_are_zero_on_a_clean_fixture(self):
        build(self.d)
        code, text = self.run_main()
        self.assertEqual(code, 0, text)
        rec = json.loads((self.d / "out" / "pseudo_a.json").read_text())
        self.assertEqual({k: v["rows"] for k, v in rec["r1_counts"].items()},
                         {"w_ge_1e4": 0, "box_outside_phase_space": 0, "nonfinite": 0})

    def test_section_9_6_stops_when_compose_is_not_bitwise(self):
        build(self.d)
        real = c.compose

        def off(cv, univ):   # one element moved by one ulp: the smallest change a bitwise check must catch
            out = real(cv, univ)
            if len(univ) == 1:
                out[0] = np.nextafter(out[0], np.inf)
            return out
        with mock.patch.object(ps.c, "compose", off):
            code, text = self.run_main()
        self.assertEqual(code, 3, text)
        self.assertIn("section 9.6", text)
        self.assertEqual(list((self.d / "out").glob("counts_*.npz")), [])

    def test_pot_mismatch_refuses(self):
        build(self.d)
        pots = iter([POT, (POT[0], POT[1] * 2)])
        with mock.patch.object(ps, "read_pot", lambda f: next(pots)), self.assertRaises(c.Refusal):
            self.run_main()

    def test_signal_tree_without_5d_truth_refuses(self):
        build(self.d)
        with uproot.open(self.d / "uni.root") as f:
            trees = {k: f[k].arrays(library="np") for k in ("mc_truth_denom", "mc_signal_reco", "mc_background")}
        del trees["mc_signal_reco"]["MC_W"]
        with uproot.recreate(self.d / "uni.root") as f:
            for k, v in trees.items():
                f[k] = v
        with self.assertRaises(c.Refusal):
            self.run_main()


class ReadPot(unittest.TestCase):
    def test_reads_both_tparameters(self):
        class P:
            def __init__(self, v):
                self.v = v

            def member(self, name):
                assert name == "fVal"
                return self.v
        self.assertEqual(ps.read_pot({"dataPOTUsed": P(2.0), "mcPOTUsed": P(8.0)}), (2.0, 8.0))


if __name__ == "__main__":
    unittest.main()
