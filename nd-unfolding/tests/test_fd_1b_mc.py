"""Controls for 1B staged stage 1 (state/measurement-paper/5d-community-20261024/FD-1B-STAGED-DECLARATION.md sections
4-9, revision 2), each rule in the direction it acts and in the other:

* the composition rule (section 4.2, as amended in binding 2 for the denominator): one universe gives
  ``s5p_universe.universe_inputs``' arrays exactly, for a bank universe, a detector-dump universe carrying denom_nd and
  a Flux universe; two universes multiply their ratios where the CV is non-zero and add where it is zero; nothing is
  clipped; non-finite weights are zeroed at load, as S1's loader does; two flux universes refuse; N1's ratio record;
* the experiments: the unfolding MC carries the nominal flux, a block's MC its universe's flux; the toy's truth is the
  nature's; d_T is the toy path at its means; the stat replica's data path is ``s5p_numerics``' set-A path;
* the truths: the plug-in's r is the push weights on truth-passing rows, and its truth is the unfold's result
  (control (b), by construction); a G18 truth is F1's ratio; the capture is the unfold bitwise and keeps the push;
* the jobs: role and truth pairing, the declared seed and replica ranges, an atime move exits 8;
* the remade blocks and the null's laws: each law's covariance is its block; the lateral block is S1's transferred;
  the seed check refuses a difference; the graded matrix is C_e + C_model_abs;
* the grading: the flags against the null, one-sided, the Cholesky equality, the attribution;
* the null and readout refuse a wrong digest and products the null was not made from.

No real data are read: every fixture is synthetic. ``stage-flux`` needs ROOT and is exercised on the cluster only:
S1-0's Flux_0 procedure control checks its product end to end."""
from __future__ import annotations

import argparse
import builtins
import functools
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(Path(__file__).resolve().parent))

import fd_1b_inv as inv  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_null as fn  # noqa: E402
import fd_1b_score as fs  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_deform  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402
import s5p_universe  # noqa: E402
from test_fd_1b import World as ToyWorld, digest  # noqa: E402
from test_fd_1b_inv import plain_noatime  # noqa: E402


class Case(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fd1b-mc-"))
        cls.w = ToyWorld(cls.tmp)
        cls.inputs = s5c_unfold.load_inputs(cls.w.inputs)
        bz = np.load(cls.w.bkg, allow_pickle=True)
        cls.bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
        z = dict(np.load(cls.w.bank / "cv.npz", allow_pickle=True))
        rng = np.random.default_rng(3)
        for k, e in zip(("td_pt", "td_pz", "td_ea", "td_q3", "td_w"), cls.inputs["edges"]):
            z[k] = rng.uniform(e[0], e[-1], 50)
        cls.bank_cv = z
        cls.flux = np.random.default_rng(4).uniform(0.9, 1.1, (100, 2)) * np.asarray(cls.inputs["flux"], float)
        # Amendment 2: first order sums each universe's departure from the CV, so the fixture's denominators must
        # agree with its bank as the real ones do. A bank universe's is its tdw over the CV's truth rows (the CV's at
        # tdw = 1), and the real detector universes' denom_nd equals the CV's (stop report section 2); the toy
        # world's are unrelated random histograms, which the product rule's ratios hid.
        cls.inputs["denom_nd"] = s5p_universe.denominator(cls.bank_cv, np.ones(50), cls.inputs["edges"])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.ps = self.w.patches() + [plain_noatime()]
        for p in self.ps:
            p.start()

    def tearDown(self):
        for p in reversed(self.ps):
            p.stop()

    def weights(self, tag):
        return self.consistent(tag, inv.universe_weights(mc.universe_dir(tag, self.w.bank, self.w.det), tag, "zero"))

    def weights_cv_det(self, tag):
        """self.weights with each detector universe's denom_nd the CV's bitwise, as the nature rule's row clip needs
        (A2.1 (d1)'s check D)."""
        w = self.weights(tag)
        return dict(w, denom_nd=np.asarray(self.inputs["denom_nd"], float)) if "denom_nd" in w else w

    def consistent(self, tag, w):
        """The fixture's denominators as the real bank's behave, deterministically in the tag (the toy world seeds by
        hash(), which varies per process): a detector universe's denom_nd is the CV's within 5 %; a bank universe's
        tdw is 1 within 2 %, so first order's sum of about 37 departures cannot cross zero in a sparse cell by chance."""
        rng = np.random.default_rng(zlib.crc32(tag.encode()))
        if "denom_nd" in w:                    # the real detector universes' equal the CV's bitwise (A2.1 (d1), check D)
            w = dict(w, denom_nd=np.asarray(self.inputs["denom_nd"], float))
        if "tdw" in w:
            w = dict(w, tdw=rng.uniform(0.98, 1.02, np.shape(w["tdw"])))
        return w


# ------------------------------------------------------------------------------------------------- composition


class Compose(Case):
    def single_reference(self, tag):
        band, _, idx = tag.rpartition("_")
        w = self.weights(tag)
        if band == sa.FLUX:
            return mc._flux_universe_inputs(self.inputs, self.bkg, self.bank_cv, w, idx, self.flux)
        return s5p_universe.universe_inputs(self.inputs, self.bkg, self.bank_cv, w, band, idx, None)

    def test_one_universe_is_universe_inputs_exactly(self):
        for tag in ("MaRES_0", "2p2h_2", "GEANT_Pion_1", "MinosEfficiency_0", "Flux_7"):
            ui, ub, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, [tag], self.weights, self.flux)
            ri, rb, _ = self.single_reference(tag)
            for k in ("w_truth", "w_reco", "denom_nd", "flux"):
                np.testing.assert_array_equal(np.asarray(ui[k], float), np.asarray(ri[k], float), (tag, k))
            np.testing.assert_array_equal(ub["bkg_w"], rb["bkg_w"], tag)

    def test_flux_universe_divides_by_its_own_flux(self):
        ui, _, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, ["Flux_7"], self.weights, self.flux)
        np.testing.assert_array_equal(ui["flux"], self.flux[7])

    def test_two_universes_compose_to_first_order_in_the_draws_order(self):
        a, b = self.weights("MaRES_0"), self.weights("LowQ2_1")
        inputs = dict(self.inputs)
        wt = np.asarray(inputs["w_truth"], float).copy()
        wt[[30, 31]] = 0.0                                 # CV = 0 rows
        wt[32] = -0.5                                      # a negative CV row
        inputs["w_truth"] = wt
        a = dict(a, wt=a["wt"].copy())
        b = dict(b, wt=b["wt"].copy())
        a["wt"][30], b["wt"][30] = 0.25, 0.5               # CV = 0, universes non-zero: added, as before
        a["wt"][33], b["wt"][33] = -0.2, wt[33] - 0.3      # a negative composite, -0.5: kept, not clipped
        ui, _, info = mc.compose(inputs, self.bkg, self.bank_cv, ["MaRES_0", "LowQ2_1"], {"MaRES_0": a, "LowQ2_1": b}.get, None,
                                 np.ones(50))
        got = np.asarray(ui["w_truth"], float)
        self.assertEqual(got[30], 0.75)
        self.assertEqual(got[31], a["wt"][31] + b["wt"][31])
        self.assertEqual(got[32], a["wt"][32] + (b["wt"][32] - (-0.5)))
        self.assertEqual(got[33], -0.2 + ((wt[33] - 0.3) - wt[33]))
        self.assertLess(got[33], 0.0)
        np.testing.assert_array_equal(got, a["wt"] + (b["wt"] - wt))     # a_u1 + (a_u2 - a_CV), bitwise
        self.assertIn("n1", info)
        self.assertEqual(info["n1"]["wt"]["rows_negative_where_cv_positive"], int(np.sum((got < 0) & (wt > 0))))

    def test_three_universes_sum_in_the_draws_order(self):
        tags = ["Flux_3", "MaRES_0", "GEANT_Pion_1"]
        ui, ub, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, tags, self.weights, self.flux, np.ones(50))
        s = [mc._single(self.inputs, self.bkg, self.bank_cv, t, self.weights(t), self.flux)[0] for t in tags]
        cv = mc._cv_arrays(self.inputs, self.bkg)
        for k, got in (("wt", ui["w_truth"]), ("wr", ui["w_reco"]), ("bkgw", ub["bkg_w"]), ("denom", ui["denom_nd"])):
            want = s[0][k].copy()
            for x in s[1:]:
                want += x[k] - cv[k]
            np.testing.assert_array_equal(np.asarray(got, float), want, k)
        self.assertFalse(np.array_equal(np.asarray(ui["w_truth"]), s[0]["wt"] * (s[1]["wt"] / cv["wt"]) * (s[2]["wt"] / cv["wt"])))

    def real_files_denominator(self):
        """inputs whose denom_nd is not hist_f32(tdw_CV), as on the real files (the (d1) read's 16 moved rows): one
        row's CV weight sits in a neighbouring cell, and the detector universes carry that npz denom_nd (check D)."""
        d32 = s5p_universe.denominator(self.bank_cv, np.ones(50), self.inputs["edges"])
        npz = np.array(d32, float)
        c = np.flatnonzero(np.ravel(npz) > 1)[:2]
        npz.flat[c[0]] -= 1.0
        npz.flat[c[1]] += 1.0
        return dict(self.inputs, denom_nd=npz), d32, npz

    def test_composites_use_the_float32_cv_denominator(self):
        inputs, d32, npz = self.real_files_denominator()
        w = lambda t: (dict(self.weights(t), denom_nd=npz) if "denom_nd" in self.weights(t) else self.weights(t))  # noqa: E731
        uni = lambda t, b: s5p_universe.universe_inputs(inputs, self.bkg, self.bank_cv, w(t), b, "0", None)[0]["denom_nd"]  # noqa: E731
        ui, _, _ = mc.compose(inputs, self.bkg, self.bank_cv, ["MaRES_0", "LowQ2_1"], w, None, np.ones(50))
        np.testing.assert_array_equal(ui["denom_nd"], uni("MaRES_0", "MaRES") + (uni("LowQ2_1", "LowQ2") - d32))
        ui, _, _ = mc.compose(inputs, self.bkg, self.bank_cv, ["MaRES_0", "GEANT_Pion_0"], w, None, np.ones(50))
        np.testing.assert_array_equal(ui["denom_nd"], uni("MaRES_0", "MaRES") + (d32 - d32))

    def test_denominators_compose_per_cell(self):
        """Per cell, on one binning (A2.1 (e2)): d_CV = hist_f32(tdw_CV), and a detector universe's denominator, the
        npz's bitwise, is that hist_f32; a detector denominator that is not the CV's refuses."""
        a, b = self.weights("MaRES_0"), self.weights("LowQ2_1")
        ui, _, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, ["MaRES_0", "LowQ2_1"], {"MaRES_0": a, "LowQ2_1": b}.get,
                              None, np.ones(50))
        uni = lambda w, t: s5p_universe.universe_inputs(self.inputs, self.bkg, self.bank_cv, w, t, "0", None)[0]["denom_nd"]  # noqa: E731
        d32 = s5p_universe.denominator(self.bank_cv, np.ones(50), self.inputs["edges"])
        np.testing.assert_array_equal(ui["denom_nd"], uni(a, "MaRES") + (uni(b, "LowQ2") - d32))
        g = self.weights("GEANT_Pion_0")
        ui, _, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, ["MaRES_0", "GEANT_Pion_0"],
                              {"MaRES_0": a, "GEANT_Pion_0": g}.get, None, np.ones(50))
        np.testing.assert_array_equal(ui["denom_nd"], uni(a, "MaRES") + (d32 - d32))
        off = dict(g, denom_nd=np.asarray(g["denom_nd"], float) * 1.01)
        with self.assertRaisesRegex(mc.Refusal, "not the CV's"):
            mc.compose(self.inputs, self.bkg, self.bank_cv, ["MaRES_0", "GEANT_Pion_0"],
                       {"MaRES_0": a, "GEANT_Pion_0": off}.get, None, np.ones(50))
        with self.assertRaisesRegex(mc.Refusal, "needs the CV's per-row tdw"):
            mc.compose(self.inputs, self.bkg, self.bank_cv, ["MaRES_0", "LowQ2_1"], {"MaRES_0": a, "LowQ2_1": b}.get, None)

    def test_a_nonpositive_composite_denominator_cell_refuses(self):
        a, b = self.weights("MaRES_0"), dict(self.weights("LowQ2_1"))
        cv = s5p_universe.denominator(self.bank_cv, np.ones(50), self.inputs["edges"])
        da = s5p_universe.universe_inputs(self.inputs, self.bkg, self.bank_cv, a, "MaRES", "0", None)[0]["denom_nd"]
        cells = mc.td_cells(self.bank_cv, self.inputs["edges"])
        c = int(np.flatnonzero(np.ravel(cv) > 0)[0])
        rows = np.flatnonzero(cells == c)
        tdw = np.asarray(b["tdw"], float).copy()
        tdw[rows] = 0.0
        tdw[rows[0]] = np.ravel(cv)[c] - np.ravel(da)[c]   # d_D = da + (db - cv) = 0 exactly in cell c
        tags, load = ["MaRES_0", "LowQ2_1"], {"MaRES_0": a, "LowQ2_1": dict(b, tdw=tdw)}.get
        with self.assertRaisesRegex(mc.Refusal, "section 2b"):
            mc.compose(self.inputs, self.bkg, self.bank_cv, tags, load, None, np.ones(50))
        tdw[rows[0]] += 1e-6                               # just positive: passes
        mc.compose(self.inputs, self.bkg, self.bank_cv, tags, {"MaRES_0": a, "LowQ2_1": dict(b, tdw=tdw)}.get, None,
                   np.ones(50))
        g = self.weights("GEANT_Pion_0")
        one = {"GEANT_Pion_0": dict(g, denom_nd=np.where(np.asarray(self.inputs["denom_nd"]) > 0, -1.0, 0.0))}
        mc.compose(self.inputs, self.bkg, self.bank_cv, ["GEANT_Pion_0"], one.get, None)   # k = 1 is S1's own

    def test_nonfinite_weights_are_zeroed_at_load_as_s1(self):
        tag = "MaCCQE_1"
        p = self.w.bank / f"{tag}_wt.npy"
        orig = np.load(p)
        try:
            bad = orig.copy()
            bad[5] = np.nan
            np.save(p, bad)
            w = inv.universe_weights(self.w.bank, tag, "zero")
            self.assertEqual(w["wt"][5], 0.0)
            ui, _, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, [tag], {tag: w}.get, None)
            self.assertEqual(ui["w_truth"][5], 0.0)
        finally:
            np.save(p, orig)

    def test_two_flux_universes_refuse(self):
        with self.assertRaises(mc.Refusal):
            mc.compose(self.inputs, self.bkg, self.bank_cv, ["Flux_1", "Flux_2"], self.weights, self.flux, np.ones(50))

    def test_flux_without_a_table_refuses(self):
        with self.assertRaises(mc.Refusal):
            mc.compose(self.inputs, self.bkg, self.bank_cv, ["Flux_1"], self.weights, None)

    def test_no_universe_is_the_cv(self):
        ui, ub, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, [], self.weights, None)
        np.testing.assert_array_equal(ui["w_truth"], self.inputs["w_truth"])
        np.testing.assert_array_equal(ub["bkg_w"], self.bkg["bkg_w"])

    def test_draw_order(self):
        d = {"flux": 4, "model": {"MaRES": "MaRES_1", "2p2h": "2p2h_0"}, "detector": {"GEANT_Pion": 1, "MinosEfficiency": 0}}
        self.assertEqual(mc.draw_universes(d), ["Flux_4", "2p2h_0", "MaRES_1", "MinosEfficiency_0", "GEANT_Pion_1"])


class Functional(unittest.TestCase):
    """A2.1's fix to the U check (the binning run's refusal, 2026-11-03): S1 stores U as float32, so the check is
    exact equality in that precision; the old absolute 1e-6 tolerance refused every real assembly."""

    def test_a_float32_stored_u_with_large_entries(self):
        rng = np.random.default_rng(4)
        U = rng.uniform(0, 1, (16, 500)) * np.logspace(-3, 7.6, 500)        # volumes up to about 4e7, as the real U
        stored = U.astype(np.float32)
        self.assertFalse(np.allclose(U, stored, rtol=0, atol=1e-6))         # the old check refuses S1's own U
        self.assertTrue(mc.same_functional(U, stored))
        bad = stored.copy()
        bad[3, 400] = np.nextafter(bad[3, 400], np.float32(np.inf))         # one float32 ulp off
        self.assertFalse(mc.same_functional(U, bad))
        self.assertFalse(np.allclose(U, bad, rtol=0, atol=1e-6))
        self.assertFalse(mc.same_functional(U[:, :499], stored))           # a different shape

    def test_the_real_definitions_u(self):
        """The world, not a fixture (the audit): the committed H2 definition's U, as S1 stored it, passes; one entry one
        float32 ulp off refuses; and the old absolute check refuses S1's own U."""
        U = sa.functional_matrix(sa.fine_map(ND / "pv-ladder" / "readouts" / "h2_definition.json"))
        stored = U.astype(np.float32)                                       # s1_assemble.py's write
        self.assertGreater(float(U.max()), 3e7)
        self.assertTrue(mc.same_functional(U, stored))
        self.assertFalse(np.allclose(U, stored, rtol=0, atol=1e-6))
        i, j = np.unravel_index(int(np.argmax(np.abs(U - stored.astype(np.float64)))), U.shape)
        bad = stored.copy()
        bad[i, j] = np.nextafter(bad[i, j], np.float32(np.inf))
        self.assertFalse(mc.same_functional(U, bad))


class TruthWeight(Case):
    def test_ratio_nd_without_run_unfold(self):
        """truth_weight installs s5e_deform's ratio_nd itself (the binning run's ValueError, 2026-11-03): a job that never
        calls run_unfold (A2.1's calibration, c2check, binning) gets F1's ratio weight, unmocked."""
        import importlib
        import s5n_pseudo
        importlib.reload(s5n_pseudo)                                  # undo any earlier install in this process
        self.assertFalse(getattr(s5n_pseudo.truth_weight, "_s5e_ratio_nd", False))
        edges = self.inputs["edges"]
        ratio = {"schema": "s5e-shape-ratio/1", "axes": [2], "edges": [list(map(float, edges[2]))],
                 "shape_ratio": list(np.linspace(0.8, 1.2, len(edges[2]) - 1))}
        r = mc.truth_weight("g18", self.inputs, ratio, None)
        self.assertEqual(r.shape, (self.inputs["w_truth"].shape[0],))
        self.assertFalse(np.allclose(r, 1.0))
        self.assertTrue(getattr(s5n_pseudo.truth_weight, "_s5e_ratio_nd", False))
        mc.s5n_pseudo = s5n_pseudo


class Experiments(Case):
    def test_with_mc_sets_the_unfolding_flux(self):
        exp, _ = mc.mean_experiment(self.inputs, self.bkg, np.ones(self.inputs["w_truth"].shape[0]))
        ui, ub, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, ["Flux_3"], self.weights, self.flux)
        np.testing.assert_array_equal(mc.with_mc(exp, ui, ub)["flux"], self.flux[3])
        np.testing.assert_array_equal(mc.with_mc(exp, self.inputs, self.bkg)["flux"], self.inputs["flux"])

    def test_toy_unfolds_with_the_nominal_mc_and_keeps_natures_truth(self):
        tags = ["Flux_3", "MaRES_0"]
        ui, ub, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, tags, self.weights, self.flux, np.ones(50))
        r = np.ones(self.inputs["w_truth"].shape[0])
        exp, x_true, _ = mc.toy_experiment(self.inputs, self.bkg, ui, ub, r, 3_620_000)
        np.testing.assert_array_equal(exp["flux"], self.inputs["flux"])
        ref = toys.build_full(ui, ub, r, np.ones(r.size), np.ones(ub["bkg_w"].size), 3_620_000, False)[1]
        np.testing.assert_array_equal(x_true, ref)
        nom = toys.build_full(self.inputs, self.bkg, r, np.ones(r.size), np.ones(ub["bkg_w"].size), 3_620_000, False)[1]
        self.assertFalse(np.array_equal(x_true, nom))

    def test_toy_carries_set_As_mc_and_template_streams(self):
        r = np.ones(self.inputs["w_truth"].shape[0])
        exp, _, clip = mc.toy_experiment(self.inputs, self.bkg, self.inputs, self.bkg, r, 3_620_001)
        self.assertEqual(clip["record"]["signal"]["rows_negative"], 0)    # the CV has no negative weight
        base = toys.build_full(self.inputs, self.bkg, r, np.ones(r.size), np.ones(self.bkg["bkg_w"].size), 3_620_001, False)[0]
        ref = toys.mc_template_streams(mc.with_mc(base, self.inputs, self.bkg), 3_620_001)
        for k in ("w_truth", "w_reco", "tmpl_w", "obs_counts"):
            np.testing.assert_array_equal(exp[k], ref[k], k)
        self.assertFalse(np.array_equal(exp["w_truth"], self.inputs["w_truth"]))

    def test_mean_experiment_is_the_toy_path_at_its_means(self):
        r = np.random.default_rng(5).uniform(0.8, 1.2, self.inputs["w_truth"].shape[0])
        exp, x = mc.mean_experiment(self.inputs, self.bkg, r)
        ref, xr, _ = toys.build_full(self.inputs, self.bkg, r, np.ones(r.size), np.ones(self.bkg["bkg_w"].size), None, True)
        np.testing.assert_array_equal(exp["obs_counts"], ref["obs_counts"])
        np.testing.assert_array_equal(x, xr)

    def test_stat_replica_on_the_data_is_set_As_path(self):
        mine, clip = mc.stat_experiment(self.inputs, self.bkg, None, None, 1)
        self.assertIsNone(clip)
        ji, jb = s5p_numerics.jittered(self.inputs, self.bkg, 101)
        ref = s5n_pseudo.bootstrap_replica(s5n_pseudo.build_data(ji, jb), 1)
        for k in ("obs", "obs_counts", "w_truth", "w_reco", "tmpl_w"):
            np.testing.assert_array_equal(mine[k], ref[k], k)

    def test_stat_replicas_share_one_realization(self):
        r = np.ones(self.inputs["w_truth"].shape[0])
        e1, c1 = mc.stat_experiment(self.inputs, self.bkg, r, 3_621_000, 1)
        e2, _ = mc.stat_experiment(self.inputs, self.bkg, r, 3_621_000, 2)
        base = toys.build_full(self.inputs, self.bkg, r, np.ones(r.size), np.ones(self.bkg["bkg_w"].size), 3_621_000, False)[0]
        self.assertEqual(e1["obs_counts"].size, base["obs_counts"].size)
        self.assertFalse(np.array_equal(e1["obs_counts"], e2["obs_counts"]))
        self.assertEqual((c1["signal"]["rows_negative"], c1["background"]["rows_negative"]), (0, 0))

    def test_stat_replica_with_a_negative_r_is_drawn_at_lambda_plus(self):
        r = np.ones(self.inputs["w_truth"].shape[0])
        reco = np.flatnonzero(np.asarray(self.inputs["pass_reco"], bool))
        r[reco[[1, 5]]] = -0.5
        ji, jb = s5p_numerics.jittered(self.inputs, self.bkg, 104)
        with self.assertRaises(ValueError):                    # unclipped, the draw refuses
            toys.build_full(ji, jb, r, np.ones(r.size), np.ones(jb["bkg_w"].size), 3_621_000, False)
        mine, clip = mc.stat_experiment(self.inputs, self.bkg, r, 3_621_000, 4)
        self.assertEqual(clip["signal"]["rows_negative"], 2)
        du, db, _ = mc.clip_draw(ji, jb, r)
        base = toys.build_full(du, db, r, np.ones(r.size), np.ones(jb["bkg_w"].size), 3_621_000, False)[0]
        np.testing.assert_array_equal(mine["obs_counts"], s5n_pseudo.bootstrap_replica(base, 4)["obs_counts"])

    def test_stat_replica_with_r_nonnegative_is_unchanged_by_the_clip(self):
        r = np.random.default_rng(6).uniform(0.8, 1.2, self.inputs["w_truth"].shape[0])
        mine, _ = mc.stat_experiment(self.inputs, self.bkg, r, 3_621_000, 3)
        ji, jb = s5p_numerics.jittered(self.inputs, self.bkg, 103)
        base = toys.build_full(ji, jb, r, np.ones(r.size), np.ones(jb["bkg_w"].size), 3_621_000, False)[0]
        ref = s5n_pseudo.bootstrap_replica(base, 3)
        for k in ("obs", "obs_counts", "w_truth", "w_reco", "tmpl_w"):
            np.testing.assert_array_equal(mine[k], ref[k], k)


class Clipping(Case):
    """Decision section 2a (a), D2 and the audit's R1-R3: lambda+ = max(lambda, 0) on the full product in every
    Poisson draw, the nature's truth kept, the clipped mass recorded."""

    def nature(self, neg_reco=(), neg_bkg=()):
        ui, ub, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, ["MaRES_0"], self.weights, None, np.ones(50))
        wr = np.asarray(ui["w_reco"], float).copy()
        reco = np.flatnonzero(np.asarray(self.inputs["pass_reco"], bool))
        for i in neg_reco:
            wr[reco[i]] = -abs(wr[reco[i]]) - 0.1
        bw = np.asarray(ub["bkg_w"], float).copy()
        for i in neg_bkg:
            bw[i] = -abs(bw[i]) - 0.1
        return dict(ui, w_reco=wr), dict(ub, bkg_w=bw), reco

    def test_d2_a_negative_nature_is_drawn_not_refused(self):
        ui, ub, reco = self.nature(neg_reco=(0, 3, 7), neg_bkg=(1, 2))
        r = np.ones(self.inputs["w_truth"].shape[0])
        with self.assertRaises(ValueError):            # D2: binding 2's toy path refuses this nature
            toys.build_full(ui, ub, r, np.ones(r.size), np.ones(ub["bkg_w"].size), 3_620_000, False)
        exp, x_true, clip = mc.toy_experiment(self.inputs, self.bkg, ui, ub, r, 3_620_000)
        rec = clip["record"]
        self.assertEqual((rec["signal"]["rows_negative"], rec["background"]["rows_negative"]), (3, 2))
        lam = np.asarray(ui["w_reco"], float) * r
        self.assertEqual(rec["signal"]["sum_negative"], float(lam[reco[[0, 3, 7]]].sum()))
        self.assertEqual(rec["signal"]["sum_lambda"], float(lam[reco].sum()))
        self.assertEqual(rec["background"]["sum_negative"], float(np.asarray(ub["bkg_w"])[[1, 2]].sum()))
        # the truth is the nature's, negative weights kept
        ref_t = toys.build_full(dict(ui, w_reco=np.abs(ui["w_reco"])), ub | {"bkg_w": np.abs(ub["bkg_w"])}, r,
                                np.ones(r.size), np.ones(ub["bkg_w"].size), None, True)[1]
        np.testing.assert_array_equal(x_true, ref_t)
        # the draw is build_full's on the clipped weights, bitwise
        du = dict(ui, w_reco=np.where(np.isin(np.arange(r.size), reco[[0, 3, 7]]), 0.0, ui["w_reco"]))
        db = dict(ub, bkg_w=np.where(np.isin(np.arange(ub["bkg_w"].size), [1, 2]), 0.0, ub["bkg_w"]))
        base = toys.build_full(du, db, r, np.ones(r.size), np.ones(ub["bkg_w"].size), 3_620_000, False)[0]
        ref = toys.mc_template_streams(mc.with_mc(base, self.inputs, self.bkg), 3_620_000)
        for k in ("obs", "obs_counts", "w_truth", "w_reco", "tmpl_w"):
            np.testing.assert_array_equal(exp[k], ref[k], k)

    def test_the_nature_rule_is_c2s_option_1(self):
        """#718 through A2.1's S3: lambda+ for the draw and max(w_truth r, 0) for the truth, each on its own sign, equal
        to cov2d.lam_plus row by row; including the rows where the two signs differ (the audit's fixture)."""
        import fd_1b_c2
        ui, ub, reco = self.nature(neg_reco=(0, 3, 7), neg_bkg=(1,))
        r = np.ones(self.inputs["w_truth"].shape[0])
        wt = np.asarray(ui["w_truth"], float).copy()
        ptru, prec = np.asarray(self.inputs["pass_truth"], bool), np.asarray(self.inputs["pass_reco"], bool)
        pt = np.flatnonzero(ptru & ~prec)
        wt[pt[0]] = -0.3                                      # a negative truth weight on a row not reco-passing
        gen = np.array(ui["MCgen"], float)
        cell = mc.flat_cells(gen, self.inputs["edges"])
        host = next(i for i in np.flatnonzero(ptru & (cell >= 0)) if i != pt[0])
        gen[pt[0]] = gen[host]                                # into a populated truth cell, so the truth can see it
        w = np.asarray(ui["w_reco"], float).copy()
        both = [i for i in np.flatnonzero(ptru & prec & (w > 0) & (wt > 0)) if i not in reco[[0, 3, 7]]]
        lam_neg_truth_pos, lam_pos_truth_neg = both[0], both[1]
        w[lam_neg_truth_pos] = -0.4                           # lambda < 0, w_truth r > 0: the truth keeps it
        wt[lam_pos_truth_neg] = -0.2                          # lambda > 0, w_truth r < 0: the draw keeps it
        neg = (np.isin(np.arange(r.size), reco[[0, 3, 7]]) | (np.arange(r.size) == lam_neg_truth_pos)) & prec
        ui = dict(ui, w_truth=wt, w_reco=w, MCgen=gen)
        dd, bd, cd = mc.clip_draw(ui, ub, r, "data")
        dn, bn, cn = mc.clip_draw(ui, ub, r, "nature")
        np.testing.assert_array_equal(bd["bkg_w"], bn["bkg_w"])
        np.testing.assert_array_equal(dd["w_truth"], wt)                      # "data": the truth keeps its negatives
        np.testing.assert_array_equal(dd["w_reco"], np.where(neg, 0.0, w))    # both rules: only the draw's negatives
        np.testing.assert_array_equal(dn["w_reco"], dd["w_reco"])
        lam_plus, _ = fd_1b_c2.cov2d.lam_plus(w[prec] * r[prec])
        np.testing.assert_array_equal(dn["w_reco"][prec] * r[prec], lam_plus)
        t_plus, rec = fd_1b_c2.cov2d.lam_plus(wt[ptru] * r[ptru])
        np.testing.assert_array_equal(dn["w_truth"][ptru] * r[ptru], t_plus)
        self.assertEqual((dn["w_reco"][lam_pos_truth_neg], dn["w_truth"][lam_pos_truth_neg]),
                         (w[lam_pos_truth_neg], 0.0))
        self.assertEqual((dn["w_reco"][lam_neg_truth_pos], dn["w_truth"][lam_neg_truth_pos]),
                         (0.0, wt[lam_neg_truth_pos]))
        self.assertEqual(dn["w_truth"][pt[0]], 0.0)          # truth-only row: clipped on its own sign
        self.assertEqual(cn["record"]["truth"]["rows_negative"], rec["rows_neg"])
        self.assertEqual(cn["record"]["truth"]["sum_negative"], rec["sum_lambda_neg"])
        self.assertEqual((cd["record"]["rule"], cn["record"]["rule"]), ("data", "nature"))
        np.testing.assert_array_equal(dd["denom_nd"], ui["denom_nd"])           # "data": the denominator untouched
        np.testing.assert_array_equal(dn["denom_nd"], ui["denom_nd"])           # no negative denominator row here
        self.assertEqual(cn["record"]["denominator"]["rows_negative"], 0)
        r = np.random.default_rng(8).uniform(0.8, 1.2, r.size)   # at r = 1 the truth's completeness cancels its weights
        dn, bn, _ = mc.clip_draw(ui, ub, r, "nature")
        _, x_n, _ = mc.toy_experiment(self.inputs, self.bkg, ui, ub, r, 3_620_000, "nature")
        ref = toys.build_full(dn, bn, r, np.ones(r.size), np.ones(ub["bkg_w"].size), None, True)[1]
        np.testing.assert_array_equal(x_n, ref)
        _, x_d, _ = mc.toy_experiment(self.inputs, self.bkg, ui, ub, r, 3_620_000, "data")
        self.assertFalse(np.array_equal(x_n, x_d))
        with self.assertRaisesRegex(mc.Refusal, "clip rule"):
            mc.clip_draw(ui, ub, r, "both")


    def test_the_truth_clip_is_on_w_truth_r(self):
        """S3 on w_truth r's sign, not w_truth's: r < 0 on a positive weight clips; on a negative weight it does not
        (D8 found no r < 0 on the real files, so only a fixture can show the difference)."""
        ui, ub, _ = self.nature()
        ptru = np.flatnonzero(np.asarray(self.inputs["pass_truth"], bool))
        wt = np.asarray(ui["w_truth"], float).copy()
        a, b = ptru[5], ptru[6]
        wt[a], wt[b] = 0.4, -0.4
        r = np.ones(wt.size)
        r[a] = r[b] = -1.0
        dn, _, _ = mc.clip_draw(dict(ui, w_truth=wt), ub, r, "nature")
        self.assertEqual((dn["w_truth"][a], dn["w_truth"][b]), (0.0, -0.4))

    def test_the_nature_rule_clips_the_denominator_by_row(self):
        """S3 (d1): a negative composite denominator row adds its mass to its own cell only (C2's N + m_all); a cell
        without one keeps compose's value bitwise; the composite rows histogram to compose's per-cell denominator."""
        ui, ub, _ = self.nature()
        cells, rows = ui["td_cells"], np.array(ui["tdw_rows"], float)
        n = int(np.prod(np.shape(ui["denom_nd"])))
        np.testing.assert_allclose(np.bincount(cells[cells >= 0], weights=rows[cells >= 0], minlength=n),
                                   np.ravel(ui["denom_nd"]), rtol=1e-12, atol=1e-12)
        k = int(np.flatnonzero(cells >= 0)[0])
        rows[k] = -0.7
        dn, _, cn = mc.clip_draw(dict(ui, tdw_rows=rows), ub, np.ones(self.inputs["w_truth"].shape[0]), "nature")
        got, base = np.ravel(dn["denom_nd"]), np.ravel(ui["denom_nd"])
        self.assertAlmostEqual(got[cells[k]] - base[cells[k]], 0.7, places=12)
        others = np.arange(n) != cells[k]
        np.testing.assert_array_equal(got[others], base[others])
        self.assertEqual((cn["record"]["denominator"]["rows_negative"], cn["record"]["denominator"]["sum_negative"]),
                         (1, -0.7))

    def test_the_nature_rule_refuses_without_the_row_denominator(self):
        ui, ub, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, ["MaRES_0"], self.weights, None)
        with self.assertRaisesRegex(mc.Refusal, "clips the denominator by row"):
            mc.clip_draw(ui, ub, np.ones(self.inputs["w_truth"].shape[0]), "nature")
        mc.clip_draw(ui, ub, np.ones(self.inputs["w_truth"].shape[0]), "data")
        off = lambda t: (dict(self.weights(t), denom_nd=np.asarray(self.inputs["denom_nd"], float) * 1.01)  # noqa: E731
                         if t == "GEANT_Pion_0" else self.weights(t))
        with self.assertRaisesRegex(mc.Refusal, "denominator is not the CV's"):
            mc.compose(self.inputs, self.bkg, self.bank_cv, ["MaRES_0", "GEANT_Pion_0"], off, None, np.ones(50))
        ui, _, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, ["MaRES_0", "GEANT_Pion_0"], self.weights_cv_det,
                              None, np.ones(50))
        self.assertIn("tdw_rows", ui)
    def test_r1_the_draw_at_its_mean_is_the_mean_path_on_the_same_nature(self):
        ui, ub, _ = self.nature(neg_reco=(0, 3, 7), neg_bkg=(1,))
        r = np.random.default_rng(7).uniform(0.8, 1.2, self.inputs["w_truth"].shape[0])
        du, db, _ = mc.clip_draw(ui, ub, r)
        at_mean = toys.build_full(du, db, r, np.ones(r.size), np.ones(ub["bkg_w"].size), None, True)
        mean_path = toys.build_full(ui, ub, r, np.ones(r.size), np.ones(ub["bkg_w"].size), None, True)
        for k in ("obs", "obs_counts"):
            np.testing.assert_array_equal(at_mean[0][k], mean_path[0][k], k)
        np.testing.assert_array_equal(at_mean[1], mean_path[1])

    def test_t1_a_non_reco_row_with_negative_lambda_is_not_clipped(self):
        ui, ub, reco = self.nature()
        r = np.ones(self.inputs["w_truth"].shape[0])
        off = int(np.flatnonzero(~np.asarray(self.inputs["pass_reco"], bool))[0])
        wr = np.asarray(ui["w_reco"], float).copy()
        wr[off] = -2.0
        du, _, clip = mc.clip_draw(dict(ui, w_reco=wr), ub, r)
        self.assertEqual(du["w_reco"][off], -2.0)
        self.assertEqual(clip["record"]["signal"]["rows_negative"], 0)
        self.assertEqual(float(np.sum(clip["clip_reco_flat"])), float(np.sum(mc.clip_draw(ui, ub, r)[2]["clip_reco_flat"])))

    def test_r2_the_clip_is_on_the_full_product(self):
        ui, ub, reco = self.nature()
        r = np.ones(self.inputs["w_truth"].shape[0])
        r[reco[2]] = -0.5                                  # r < 0 on a positive w_reco: clipped
        wr = np.asarray(ui["w_reco"], float).copy()
        wr[reco[4]] = -1.0
        r[reco[4]] = -2.0                                  # r < 0 on a negative w_reco: lambda > 0, kept
        wr[reco[5]] = -1.0                                 # r > 0 on a negative w_reco: clipped
        ui = dict(ui, w_reco=wr)
        du, _, clip = mc.clip_draw(ui, ub, r)
        self.assertEqual(du["w_reco"][reco[2]], 0.0)
        self.assertEqual(du["w_reco"][reco[4]], -1.0)
        self.assertEqual(du["w_reco"][reco[5]], 0.0)
        self.assertEqual(clip["record"]["signal"]["rows_negative"], 2)
        lam = np.asarray(du["w_reco"], float)[reco] * r[reco]
        self.assertGreaterEqual(lam.min(), 0.0)
        np.random.default_rng(1).poisson(lam)             # no refusal

    def test_r3_the_clipped_mass_per_cell(self):
        pt = np.asarray(self.inputs["pass_truth"], bool)
        idx = np.flatnonzero(np.asarray(self.inputs["pass_reco"], bool))
        on = np.flatnonzero(pt[idx])[:2]                      # two reco-passing rows that are truth-passing
        off = int(np.flatnonzero(~pt[idx])[0])               # and one that is not
        pick = (int(on[0]), int(on[1]), off)
        ui, ub, reco = self.nature(neg_reco=pick, neg_bkg=(1, 2))
        self.assertFalse(pt[reco[off]])
        gen = np.array(ui["MCgen"], float)
        gen[reco[off]] = [0.5 * (np.asarray(e)[0] + np.asarray(e)[1]) for e in self.inputs["edges"]]   # in a cell
        ui = dict(ui, MCgen=gen)
        r = np.ones(self.inputs["w_truth"].shape[0])
        _, _, clip = mc.clip_draw(ui, ub, r)
        lam = np.asarray(ui["w_reco"], float) * r
        rows = reco[list(pick)]
        edges = self.inputs["edges"]
        want_r = np.histogramdd(self.inputs["MCreco"][rows], bins=edges, weights=-lam[rows])[0].ravel() + \
            np.histogramdd(self.bkg["bkg_reco"][[1, 2]], bins=edges, weights=-np.asarray(ub["bkg_w"])[[1, 2]])[0].ravel()
        np.testing.assert_array_equal(clip["clip_reco_flat"], want_r)
        t = rows[np.asarray(self.inputs["pass_truth"], bool)[rows]]
        want_t = np.histogramdd(gen[t], bins=edges, weights=-lam[t])[0].ravel()
        np.testing.assert_array_equal(clip["clip_truth_flat"], want_t)
        self.assertEqual(t.size, 2)                            # the non-truth-passing row is not in the truth cells

    def test_clipmean_adds_the_clipped_mass_to_d_t(self):
        ui, ub, reco = self.nature(neg_reco=(0, 3, 7), neg_bkg=(1,))
        r = np.ones(self.inputs["w_truth"].shape[0])
        exp, x_true, clip = mc.clipmean_experiment(self.inputs, self.bkg, ui, ub, r)
        base, xb = mc.mean_experiment(self.inputs, self.bkg, r)
        np.testing.assert_array_equal(x_true, xb)
        n0 = base["obs_counts"].size
        np.testing.assert_array_equal(exp["obs_counts"][:n0], base["obs_counts"])
        lam = np.asarray(ui["w_reco"], float) * r
        added = np.concatenate([-lam[reco[[0, 3, 7]]], -np.asarray(ub["bkg_w"])[[1]]])
        coords = np.concatenate([ui["MCreco"][reco[[0, 3, 7]]], ub["bkg_reco"][[1]]])
        keep = s5n_pseudo.fid_mask(coords, self.inputs["edges"])
        np.testing.assert_array_equal(exp["obs_counts"][n0:], added[keep])
        np.testing.assert_array_equal(exp["obs"][n0:], coords[keep])
        self.assertEqual(exp["obs"].shape[0], exp["obs_counts"].size)
        self.assertGreater(keep.sum(), 0)
        clean, _, _ = mc.clipmean_experiment(self.inputs, self.bkg, *self.nature()[:2], r)
        np.testing.assert_array_equal(clean["obs_counts"], base["obs_counts"])    # no negatives: d_T itself


class Truths(Case):
    def test_plugin_r_is_the_push_on_truth_rows(self):
        m = np.asarray(self.inputs["pass_truth"], bool)
        push = np.linspace(0.5, 1.5, int(m.sum()))
        r = mc.truth_weight("plugin", self.inputs, None, push)
        np.testing.assert_array_equal(r[m], push)
        self.assertTrue(np.all(r[~m] == 1.0))
        with self.assertRaises(mc.Refusal):
            mc.truth_weight("plugin", self.inputs, None, push[:-1])
        with self.assertRaises(mc.Refusal):
            mc.truth_weight("plugin", self.inputs, None, None)

    def test_plugin_truth_is_the_unfolds_result_by_construction(self):
        """Control (b): with r = the push weights, true_xsec is s5c_unfold.unfold's formula applied to them."""
        m = np.asarray(self.inputs["pass_truth"], bool)
        push = np.random.default_rng(6).uniform(0.7, 1.3, int(m.sum()))
        unf_in = s5n_pseudo.build_data(self.inputs, self.bkg)
        unf_in = {k: unf_in[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco",
                                         "denom_nd", "flux", "data_pot", "n_nucleons", "edges")}
        unf_in["measured"], unf_in["measured_weights"] = self.inputs["measured"], np.ones(len(self.inputs["measured"]))
        with mock.patch.object(s5c_unfold.onc, "omnifold_loop", lambda *a, **k: (None, push)), \
                mock.patch.object(s5c_unfold, "estimator_config", _no_factory):
            xs, _ = s5c_unfold.unfold(unf_in, "deterministic", 42, 1, 5)
        _, x_T = mc.mean_experiment(self.inputs, self.bkg, mc.truth_weight("plugin", self.inputs, None, push))
        np.testing.assert_allclose(np.asarray(x_T, float), np.asarray(xs, float), rtol=1e-12)

    def test_capture_is_the_unfold_and_keeps_the_push(self):
        m = np.asarray(self.inputs["pass_truth"], bool)
        push = np.random.default_rng(7).uniform(0.7, 1.3, int(m.sum()))
        unf_in = {k: self.inputs[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco",
                                              "denom_nd", "flux", "data_pot", "n_nucleons", "edges")}
        unf_in["measured"], unf_in["measured_weights"] = self.inputs["measured"], np.ones(len(self.inputs["measured"]))
        cap = mc.Capture()
        loop = lambda *a, **k: (None, push)  # noqa: E731
        with mock.patch.object(s5c_unfold.onc, "omnifold_loop", loop), \
                mock.patch.object(s5c_unfold, "estimator_config", _no_factory):
            ref, _ = s5c_unfold.unfold(unf_in, "deterministic", 42, 1, 5)
            got, _ = cap(unf_in, "deterministic", 42, 1, 5)
            loop_after = s5c_unfold.onc.omnifold_loop
        np.testing.assert_array_equal(got, ref)
        np.testing.assert_array_equal(cap.push, push)
        self.assertIsNot(cap.push, push)
        self.assertIs(loop_after, loop)                            # the wrap is removed after the call

    def test_the_capture_records_the_push_sign(self):
        m = np.asarray(self.inputs["pass_truth"], bool)
        push = np.full(int(m.sum()), 1.1)
        push[[2, 9]] = [-0.25, -0.5]

        def fake(exp, threads, cap):
            cap.push = push
            return np.zeros(4), {}
        _, meta = mc.run_item(argparse.Namespace(truth="data", threads=1), {"inputs": self.inputs, "bkg": self.bkg},
                              "capture", "data", unfold_fn=fake)
        self.assertEqual((meta["push_min"], meta["push_negative"]), (-0.5, 2))

    def test_g18_truth_is_f1s_ratio(self):
        ratio, sha = mc.truth_ratio("g18", self.w.prep)
        self.assertEqual(sha, digest(self.w.prep / "bridged" / "genie_v3_g18.json"))
        with mock.patch.object(s5n_pseudo, "truth_weight", s5n_pseudo.truth_weight):   # restored after
            s5e_deform.install_ratio_truth(s5n_pseudo)                                # what the job's install does
            r = mc.truth_weight("g18", self.inputs, ratio, None)
            ref = s5n_pseudo.truth_weight("ratio_nd", self.inputs, 1.0, ratio)
        np.testing.assert_array_equal(r, ref)
        self.assertFalse(np.all(r == 1.0))

    def test_a_ratio_off_the_committed_sum_refuses(self):
        p = self.w.prep / "bridged" / "genie_v3_ar23.json"
        orig = p.read_text()
        try:
            p.write_text(orig.replace("0.9", "0.91"))
            with self.assertRaises(mc.Refusal):
                mc.truth_ratio("ar23", self.w.prep)
        finally:
            p.write_text(orig)


class _no_factory:
    def __init__(self, extra, record):
        self.record = record

    def __enter__(self):
        self.record.append([])
        return None

    def __exit__(self, *a):
        return False


# ------------------------------------------------------------------------------------------------------- the jobs


class Jobs(Case):
    def argv(self, truth, role, items, out):
        return ["unfold", "--truth", truth, "--role", role, "--items", items, "--npz", str(self.w.inputs),
                "--bkg", str(self.w.bkg), "--bank", str(self.w.bank), "--detector-dir", str(self.w.det),
                "--pins", str(self.w.pins), "--flux-constraint", str(self.w.constraint),
                "--expect-pins-sha256", digest(self.w.pins), "--prep", str(self.w.prep), "--threads", "1",
                "--estimator", "R", "--clip-rule", "data", "--out", str(out)]

    def test_control_and_capture_only_on_the_data(self):
        """The role pairing refuses with its own message, before S2's gate (which would also refuse these argvs)."""
        import contextlib
        out = self.tmp / "jobs1"
        for argv in (self.argv("g18", "control", "MaRES_0", out), self.argv("data", "central", "T", out)):
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(mc.main(argv), 4)
            self.assertIn("the control and capture roles run on the data", err.getvalue())

    def test_declared_ranges(self):
        a = mock.Mock(truth="g18", prep=self.w.prep, push=None, expect_push_sha256=None, threads=1,
                      flux_constraint=self.w.constraint, bank=self.w.bank, detector_dir=self.w.det, clip_rule="data")
        world = {"inputs": self.inputs, "bkg": self.bkg, "bank_cv": self.bank_cv, "flux": self.flux,
                 "groups": toys.interaction_groups(self.w.bank), "pins": {}}
        with self.assertRaisesRegex(mc.Refusal, "outside g18's declared range"):
            mc.run_item(a, world, "toy", "3630000", unfold_fn=lambda *x: (np.zeros(3), {}))
        with self.assertRaisesRegex(mc.Refusal, "not one of set A's"):
            mc.run_item(a, world, "stat", "51", unfold_fn=lambda *x: (np.zeros(3), {}))
        with self.assertRaises(mc.Refusal):
            mc.run_item(mock.Mock(truth="data"), world, "control", "LowQ2_1", unfold_fn=lambda *x: (np.zeros(3), {}))

    def test_the_estimator_is_a_named_input(self):
        out = self.tmp / "jobs-est"
        installed = []
        argv = self.argv("g18", "central", "T", out)
        argv[argv.index("--estimator") + 1] = "B0"
        with mock.patch.object(mc, "_unfold_s1", lambda exp, threads, seed=42, unfold_fn=None: (np.ones(4), {})), \
                mock.patch.object(mc.s5e_candidate, "install", lambda c: installed.append(c)):
            self.assertEqual(mc.main(argv), 0)
        self.assertEqual(installed, ["B0"])
        z = np.load(out / mc.product_name("fd1b_mc", "g18", "central", "T"))
        self.assertEqual(json.loads(str(z["meta"]))["config"], "B0")
        out2 = self.tmp / "jobs-rule"
        argv2 = self.argv("g18", "central", "T", out2)
        argv2[argv2.index("--clip-rule") + 1] = "nature"
        argv2 = self.bound_gate(argv2, "g18")
        with mock.patch.object(mc, "_unfold_s1", lambda exp, threads, seed=42, unfold_fn=None: (np.ones(4), {})), \
                mock.patch.object(mc, "BOUND_GATE_SHA256", self.bound):
            self.assertEqual(mc.main(argv2), 0)
        z = np.load(out2 / mc.product_name("fd1b_mc", "g18", "central", "T"))
        self.assertEqual(json.loads(str(z["meta"]))["clip_rule"], "nature")
        argv[argv.index("--estimator") + 1] = "Z"
        with self.assertRaises(SystemExit):                     # not in the registry
            mc.main(argv)
        argv.remove("--estimator")
        argv.remove("Z")
        with self.assertRaises(SystemExit):                     # required
            mc.main(argv)

    def test_t3_a_stat_replica_records_its_clip(self):
        world = {"inputs": self.inputs, "bkg": self.bkg, "bank_cv": self.bank_cv, "flux": self.flux,
                 "groups": toys.interaction_groups(self.w.bank), "pins": {}}
        a = argparse.Namespace(truth="g18", prep=None, push=None, threads=1, clip_rule="data")
        with mock.patch.object(mc, "truth_ratio", lambda *x: (None, None)), \
                mock.patch.object(mc, "truth_weight", lambda *x: np.ones(self.inputs["w_truth"].shape[0])):
            _, meta = mc.run_item(a, world, "stat", "3", unfold_fn=lambda *x: (np.zeros(3), {}))
        self.assertEqual(meta["clip"]["rule"], "data")
        self.assertEqual((meta["clip"]["signal"]["rows_negative"], meta["clip"]["background"]["rows_negative"]), (0, 0))

    def test_c4_nature_is_refused_where_the_offset_is_read(self):
        a = argparse.Namespace(truth="g18", prep=None, push=None, threads=1, clip_rule="nature",
                               flux_constraint=self.w.constraint)
        with mock.patch.object(mc, "truth_ratio", lambda *x: (None, None)), \
                self.assertRaisesRegex(mc.Refusal, "descriptive figure"):
            mc.run_item(a, {"inputs": self.inputs, "bkg": self.bkg}, "clipmean", "3620000")
        with self.assertRaisesRegex(mc.Refusal, "descriptive figure"):
            mc.clipcheck(argparse.Namespace(clip_rule="nature"))
        with self.assertRaisesRegex(mc.Refusal, "descriptive figure"):
            mc.clipping_readout(self.tmp, "t", "g18", None, {}, [], "nature")

    def test_a_toy_draws_under_the_declared_clip_rule(self):
        world = {"inputs": self.inputs, "bkg": self.bkg, "bank_cv": self.bank_cv, "flux": self.flux,
                 "groups": toys.interaction_groups(self.w.bank), "pins": {}, "tdw_cv": np.ones(50)}
        seen = []
        real = mc.toy_experiment

        def spy(*args):
            seen.append(args[-1])
            return real(*args)
        for rule in ("data", "nature"):
            a = argparse.Namespace(truth="g18", prep=None, push=None, flux_constraint=self.w.constraint, threads=1,
                                   bank=self.w.bank, detector_dir=self.w.det, clip_rule=rule)
            with mock.patch.object(mc, "truth_ratio", lambda *x: (None, None)), \
                    mock.patch.object(mc, "truth_weight", lambda *x: np.ones(self.inputs["w_truth"].shape[0])), \
                    mock.patch.object(mc, "_weights", lambda w, a, t: self.weights_cv_det(t)), \
                    mock.patch.object(mc, "toy_experiment", spy):
                _, meta = mc.run_item(a, world, "toy", "3620000", unfold_fn=lambda *x: (np.zeros(3), {}))
            self.assertEqual(meta["clip"]["rule"], rule)
        self.assertEqual(seen, ["data", "nature"])

    def bound_gate(self, argv, truth, **over):
        """A gate record bound to this run's inputs, as c2check writes one (a named fixture: c2check's own PASS needs
        real data); ``over`` replaces fields, for the refusal directions. Returns argv with --clip-gate added."""
        import fd_1b_c2
        def val(flag):
            return argv[argv.index(flag) + 1] if flag in argv else None
        ins = {"npz_sha256": sa.INPUT_NPZ_SHA256, "bkg_sha256": sa.BKG_SHA256,
               "pins_sha256": val("--expect-pins-sha256"), "flux_table_sha256": val("--expect-flux-table-sha256"),
               "cv_tdw_sha256": val("--expect-cv-tdw-sha256"), "push_sha256": val("--expect-push-sha256")}
        code = fd_1b_c2.gate_code_digests()
        rec = {"schema": fd_1b_c2.SCHEMA_GATE, **mc.CLIP_GATE, "reads": {truth: "option (1)"}, "truths": [truth],
               "declared_seeds": {truth: [mc.TOY_SEEDS[truth][0], mc.TOY_SEEDS[truth][-1]]} if truth in mc.TOY_SEEDS else {},
               "code_sha256": code, "calibration_sha256": "c" * 64, "inputs": ins,
               "calibration": {"verdict": "CALIBRATED", "sha256": "c" * 64, "s": 1.0, "union": 0.009,
                               "three_truths_measured": True, "power_meets": True},
               "backstop": {truth: {"passes": True}}, "config_hash": fd_1b_c2.config_hash(code, ins, "nature")}
        for k, v in over.items():
            if "." in k:
                head, key = k.split(".", 1)
                rec[head] = dict(rec[head], **{key: v})
            else:
                rec[k] = v
        gate = self.tmp / f"gate-{len(list(self.tmp.glob('gate-*')))}.json"
        gate.write_text(json.dumps(rec))
        self.bound = digest(gate)                              # binding 3's declaration, for the run that follows
        return argv + ["--clip-gate", str(gate), "--expect-clip-gate-sha256", digest(gate)]

    def test_s2_the_bound_gate(self):
        """A2.1's S2: 'data' runs only the pre-gate items; 'nature' runs the graded roles only, and only on c2check's
        record bound to this run (D2: a hand-written file cannot pass). Each binding both ways."""
        fake = lambda exp, threads, seed=42, unfold_fn=None: (np.ones(4), {})  # noqa: E731
        k = [0]

        def run(truth, role, item, rule, gate=None, bind=True, **over):
            k[0] += 1
            argv = self.argv(truth, role, item, self.tmp / f"s2-{k[0]}")
            argv[argv.index("--clip-rule") + 1] = rule
            self.bound = None
            if gate:
                argv = self.bound_gate(argv, truth, **over)
            with mock.patch.object(mc, "_unfold_s1", fake), \
                    mock.patch.object(mc, "BOUND_GATE_SHA256", self.bound if bind else None):
                return mc.main(argv)
        self.assertEqual(run("g18", "central", "T", "data"), 0)                 # S1-0's pilot item
        self.assertEqual(run("ar23", "central", "T", "data"), 0)                # S1-0b's
        self.assertEqual(run("g18", "seed", "T", "data"), 4)                    # a bulk item under 'data'
        self.assertEqual(run("g18", "seed", "T", "nature"), 4)                  # no gate
        self.assertEqual(run("g18", "seed", "T", "nature", gate=True), 0)       # the bound record
        self.assertEqual(run("g18", "seed", "T", "nature", gate=True, bind=False), 4)   # H1: nothing bound yet
        for over in ({"verdict": "STOP"}, {"reading": "option (2)"}, {"reads": {"g18": "option (3)"}},
                     {"reads": {"ar23": "option (1)"}}, {"declared_seeds": {"g18": [1, 2]}},
                     {"code_sha256": {"fd_1b_c2.py": "0" * 64}}, {"inputs.pins_sha256": "0" * 64},
                     {"inputs.npz_sha256": "0" * 64}, {"calibration_sha256": None}, {"schema": "x"},
                     {"calibration.verdict": "TO_JOSEPH"}, {"calibration.sha256": "d" * 64},          # H2, each field
                     {"calibration.three_truths_measured": False}, {"calibration.union": 0.0101},
                     {"calibration.power_meets": False}, {"backstop": {"g18": {"passes": False}}},
                     {"backstop": {}}, {"config_hash": "0" * 64}):
            self.assertEqual(run("g18", "seed", "T", "nature", gate=True, **over), 4, over)
        argv = self.bound_gate(self.argv("g18", "seed", "T", self.tmp / "s2-other"), "g18")  # H1: a well-formed record
        argv[argv.index("--clip-rule") + 1] = "nature"
        other = self.bound
        argv2 = self.bound_gate(self.argv("g18", "seed", "T", self.tmp / "s2-other2"), "g18", **{"calibration.s": 1.01})
        argv2[argv2.index("--clip-rule") + 1] = "nature"
        with mock.patch.object(mc, "_unfold_s1", fake), mock.patch.object(mc, "BOUND_GATE_SHA256", other):
            self.assertEqual(mc.main(argv2), 4)                               # not the declared one: refused
        gate = self.tmp / "hand-written.json"                                   # D2: the stub's three fields alone
        gate.write_text(json.dumps(mc.CLIP_GATE))
        argv = self.argv("g18", "seed", "T", self.tmp / "s2-hand")
        argv[argv.index("--clip-rule") + 1] = "nature"
        with mock.patch.object(mc, "_unfold_s1", fake):
            self.assertEqual(mc.main(argv + ["--clip-gate", str(gate), "--expect-clip-gate-sha256", digest(gate)]), 4)
        argv = self.bound_gate(self.argv("g18", "seed", "T", self.tmp / "s2-digest"), "g18")
        argv[argv.index("--clip-rule") + 1] = "nature"
        argv[argv.index("--expect-clip-gate-sha256") + 1] = "0" * 64
        with mock.patch.object(mc, "_unfold_s1", fake), mock.patch.object(mc, "BOUND_GATE_SHA256", "0" * 64):
            self.assertEqual(mc.main(argv), 4)                                  # the file is not the digest given
        self.assertEqual(run("data", "control", "MaRES_0", "nature", gate=True), 4)   # not a graded role
        self.assertTrue({("g18", "toy", "3620000"), ("ar23", "stat", "1"), ("data", "capture", "data")}
                        <= mc.pre_gate_items())
        self.assertNotIn(("g18", "toy", "3620001"), mc.pre_gate_items())

    def test_central_and_seed_products(self):
        out = self.tmp / "jobs2"
        calls = []

        def fake(exp, threads, seed=42, unfold_fn=None):
            calls.append(seed)
            return np.asarray(exp["obs_counts"].sum() * np.ones(4)), {"seen_seed": seed}
        with mock.patch.object(mc, "_unfold_s1", fake):
            self.assertEqual(mc.main(self.argv("g18", "central", "T", out)), 0)
            argv = self.argv("g18", "seed", "T", out)                          # a bulk item: 'nature' with the gate
            argv[argv.index("--clip-rule") + 1] = "nature"
            argv = self.bound_gate(argv, "g18")
            with mock.patch.object(mc, "BOUND_GATE_SHA256", self.bound):
                self.assertEqual(mc.main(argv), 0)
        self.assertEqual(calls, [42, mc.SEED_CHECK])
        z = np.load(out / mc.product_name("fd1b_mc", "g18", "seed", "T"))
        self.assertEqual(json.loads(str(z["meta"]))["estimator_seed"], mc.SEED_CHECK)

    def test_an_atime_move_exits_8(self):
        out = self.tmp / "jobs3"
        with mock.patch.object(mc, "_unfold_s1", lambda exp, threads, seed=42: (np.ones(4), {})), \
                mock.patch.object(inv, "atime_check", lambda: {"moved": ["x"], "files": {}}):
            self.assertEqual(mc.main(self.argv("g18", "central", "T", out)) & 8, 8)


# -------------------------------------------------------------------------------- remade blocks, null, grading


def toy_staged(root: Path, rng, n_cells=16):
    """A staged S1 assembly and remade products at a truth, all synthetic."""
    f = rng.uniform(1.0, 2.0, n_cells)
    U = np.eye(n_cells)
    blocks = {}
    for band, n in sa.EXPECT.items():
        X = rng.normal(0, 0.01, (n, n_cells)) * f
        blocks[f"band:{band}"] = sa.mat_cov(X)
    for b in sa.LATERAL_BANDS:
        v = rng.normal(0, 0.01, n_cells) * f
        blocks[f"lat:{b}"] = np.outer(v, v)
    blocks["stat"] = np.diag((0.001 * f) ** 2)
    blocks["normalization"] = np.outer(0.014 * f, 0.014 * f)
    blocks["seed"] = np.zeros((n_cells, n_cells))
    return {"f": f, "U": U, "blocks": blocks}


class Remade(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-mc-rm-"))
        self.na = plain_noatime()
        self.na.start()
        self.addCleanup(self.na.stop)
        self.rng = np.random.default_rng(11)
        self.s1 = toy_staged(self.tmp, self.rng)
        self.U = np.eye(16)
        X_T = self.s1["f"] * 1.05
        self.write("central", "T", X_T)
        self.write("seed", "T", X_T)
        for band, n in sa.EXPECT.items():
            for i in range(n):
                self.write("block", f"{band}_{i}", X_T * (1 + self.rng.normal(0, 0.01, 16)))
        for b in sa.STAT_REPLICAS:
            self.write("stat", str(b), X_T * (1 + self.rng.normal(0, 0.001, 16)))
        self.constraint = self.tmp / "constraint.txt"
        w = self.rng.uniform(0.5, 4.0, 100)
        self.constraint.write_text("".join(f"Flux {i} {w[i]!r}\n" for i in range(100)))
        self.frac = np.outer(np.full(16, 0.03), np.full(16, 0.03))
        self.X_T = X_T

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, role, item, x):
        np.savez(self.tmp / mc.product_name("t", "g18", role, item), xsec_flat=np.asarray(x, float),
                 meta=json.dumps({"seconds_unfold": 1.0, "peak_rss_kib": 1}))

    def remade(self):
        with mock.patch.object(sa, "CONSTRAINT_SHA256", digest(self.constraint)):
            return mc.remade(self.tmp, "t", "g18", self.s1, self.U, self.constraint, self.frac)

    def test_laws_carry_their_blocks_and_the_null_matches(self):
        rm = self.remade()
        for name, law, _ in rm["laws"]:
            np.testing.assert_allclose(law.cov(), rm["blocks"][name], rtol=1e-10, atol=1e-18, err_msg=name)
        self.assertLessEqual(fn.check_matched([l for _, l, _ in rm["laws"]], rm["gauss"], rm["C_T"]), fn.MATCH_TOL)
        np.testing.assert_allclose(rm["C_T"], rm["C_e"] + sa.model_abs(self.X_T, self.frac), rtol=1e-14)

    def test_flux_law_is_constraint_weighted(self):
        rm = self.remade()
        with mock.patch.object(sa, "CONSTRAINT_SHA256", digest(self.constraint)):
            w = sa.flux_weights(self.constraint)
        X = np.array([np.load(self.tmp / mc.product_name("t", "g18", "block", f"Flux_{i}"))["xsec_flat"] for i in range(100)])
        np.testing.assert_allclose(rm["blocks"]["band:Flux"], sa.mat_cov(X, w), rtol=1e-12)

    def test_lateral_is_s1s_transferred(self):
        rm = self.remade()
        g = self.X_T / self.s1["f"]
        for b in sa.LATERAL_BANDS:
            np.testing.assert_allclose(rm["blocks"][f"lat:{b}"], self.s1["blocks"][f"lat:{b}"] * np.outer(g, g),
                                       rtol=1e-10, atol=1e-20)

    def test_the_seed_check_refuses_a_difference(self):
        self.write("seed", "T", self.X_T * (1 + 1e-15))
        with self.assertRaises(mc.Refusal):
            self.remade()


class Grading(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(12)
        A = rng.normal(size=(16, 16))
        self.C = A @ A.T / 16 + np.eye(16)
        self.L = np.linalg.cholesky(self.C)
        self.rng = rng
        self.null = {"p_cell": np.full(16, fn.P0), "se_cell": np.zeros(16), "q_joint": fn.P0, "se_joint": 0.0,
                     "chi2_cut": inv.chi2_ppf(fn.P0, 16)}

    def test_matched_errors_cover(self):
        E = (self.L @ self.rng.normal(size=(16, 300))).T
        g = mc.grade(E, self.C, self.null)
        self.assertEqual(g["verdict"], "COVERS")
        self.assertEqual(g["ndf"], 16)

    def test_wide_errors_under_cover_and_are_attributed_to_width(self):
        E = 1.6 * (self.L @ self.rng.normal(size=(16, 300))).T
        E -= E.mean(axis=0)
        g = mc.grade(E, self.C, self.null)
        self.assertEqual(g["verdict"], "UNDER-COVERS")
        self.assertTrue(g["joint_flag"])
        self.assertTrue(all(a["driven_by"] == "width" for a in g["attribution"].values()))

    def test_narrow_errors_do_not_flag(self):
        E = 0.5 * (self.L @ self.rng.normal(size=(16, 300))).T
        g = mc.grade(E, self.C, self.null)
        self.assertEqual(g["verdict"], "COVERS")
        self.assertTrue(any(g["over_covers"]))

    def test_wrong_correlations_flag_the_joint_region_only(self):
        """Per-cell widths right, correlations wrong: only the chi2 region can see it."""
        rng = np.random.default_rng(13)
        v = np.ones(16) / 4.0
        C = 0.1 * np.eye(16) + 0.9 * np.outer(v, v) * 16 / 16   # strongly correlated
        d = np.sqrt(np.diag(C))
        E = rng.normal(size=(300, 16)) * d                       # independent, the same diagonal
        null = dict(self.null, chi2_cut=inv.chi2_ppf(fn.P0, 16))
        g = mc.grade(E, C, null)
        self.assertFalse(any(g["cell_flag"]))
        self.assertTrue(g["joint_flag"])
        self.assertEqual(g["verdict"], "UNDER-COVERS")

    def test_cell_flag_boundary(self):
        k = fn.thresholds(self.null)["k_cell"][0]
        sig = np.sqrt(np.diag(self.C))
        base = (self.L @ self.rng.normal(size=(16, 300))).T * 0.3
        for count, flagged in ((k, True), (k + 1, False)):
            E = base.copy()
            E[:, 0] = np.where(np.arange(300) < count, 0.5, 2.0) * sig[0]
            self.assertEqual(mc.grade(E, self.C, self.null)["cell_flag"][0], flagged, count)

    def test_a_bias_is_attributed_to_bias(self):
        E = (self.L @ self.rng.normal(size=(16, 300))).T * 0.6
        E[:, 3] += 1.2 * np.sqrt(self.C[3, 3])
        g = mc.grade(E, self.C, self.null)
        self.assertTrue(g["cell_flag"][3])
        self.assertEqual(g["attribution"]["R03"]["driven_by"], "bias")


# --------------------------------------------------------------------------------- D1: reads through O_NOATIME


class _Stop(Exception):
    pass


class NoAtime(unittest.TestCase):
    """The audit's D1 on #679. The staged S1 assembly and the flux constraint are inputs this lane did not make, so at
    every stage-1 call site they are opened only through O_NOATIME, and never by a plain open."""
    FLAG = 1 << 29

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-mc-na-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.flagged, self.plain = [], []
        real_os_open = os.open

        def os_open(path, flags, *a, **k):
            if flags & self.FLAG:
                self.flagged.append(os.fspath(path))
            return real_os_open(path, flags & ~self.FLAG, *a, **k)

        def recording(real):
            def opener(file, *a, **k):
                if isinstance(file, (str, os.PathLike)):
                    self.plain.append(os.fspath(file))
                return real(file, *a, **k)
            return opener

        for p in (mock.patch.object(inv, "NOATIME_FLAG", self.FLAG), mock.patch.object(inv.os, "open", os_open),
                  mock.patch.object(builtins, "open", recording(builtins.open)),
                  mock.patch.object(io, "open", recording(io.open))):
            p.start()
            self.addCleanup(p.stop)
        (self.tmp / "s1").mkdir()
        self.s1 = self.tmp / "s1" / "s1_assembly.npz"
        self.s1.write_bytes(b"the staged assembly")
        self.constraint = self.tmp / "constraint.txt"
        self.constraint.write_text("".join(f"Flux {i} {1.0 + i / 100}\n" for i in range(100)))
        self.plain.clear()

    def spy(self):
        got = []

        def reader(path, *a, **k):
            got.append(os.fspath(path))
            raise _Stop
        return got, reader

    def assert_noatime_only(self, src: Path, got: list):
        self.assertIn(str(src), self.flagged, "the source was not opened with O_NOATIME")
        self.assertNotIn(str(src), self.plain, "the source was opened plainly")
        self.assertEqual(len(got), 1)
        self.assertNotEqual(got[0], str(src), "the bound reader was handed the source itself")

    def test_null_reads_the_assembly_through_o_noatime(self):
        got, reader = self.spy()
        a = argparse.Namespace(staged=self.tmp, unfolds=self.tmp, tag="t", truth="g18", estimator="R", clip_rule="data")
        with mock.patch.object(mc.fs, "load_s1", reader), self.assertRaises(_Stop):
            mc.null_step(a)
        self.assert_noatime_only(self.s1, got)

    def test_readout_reads_the_assembly_through_o_noatime(self):
        got, reader = self.spy()
        null = self.tmp / "null.json"
        null.write_text(json.dumps({"products_sha256": "p"}))
        a = argparse.Namespace(staged=self.tmp, null=null, expect_null_sha256=digest(null), unfolds=self.tmp,
                               tag="t", truth="g18", estimator="R", clip_rule="data")
        with mock.patch.object(mc.fs, "load_s1", reader), mock.patch.object(mc, "products_digest", lambda *a: "p"), \
                self.assertRaises(_Stop):
            mc.readout(a)
        self.assert_noatime_only(self.s1, got)

    def test_remade_reads_the_constraint_through_o_noatime(self):
        for role in ("central", "seed"):
            np.savez(self.tmp / mc.product_name("t", "g18", role, "T"), xsec_flat=np.ones(16))
        got, reader = self.spy()
        with mock.patch.object(mc.sa, "flux_weights", reader), self.assertRaises(_Stop):
            mc.remade(self.tmp, "t", "g18", {"f": np.ones(16)}, np.eye(16), self.constraint, None)
        self.assert_noatime_only(self.constraint, got)

    def test_a_toy_reads_the_constraint_through_o_noatime(self):
        got, reader = self.spy()
        a = argparse.Namespace(truth="g18", prep=None, push=None, flux_constraint=self.constraint)
        with mock.patch.object(mc, "truth_ratio", lambda *a: (None, None)), \
                mock.patch.object(mc.toys, "flux_probabilities", reader), self.assertRaises(_Stop):
            mc.run_item(a, {"inputs": {}, "bkg": {}}, "toy", "3620000")
        self.assert_noatime_only(self.constraint, got)

    def test_clipmean_reads_the_constraint_through_o_noatime(self):
        got, reader = self.spy()
        a = argparse.Namespace(truth="g18", prep=None, push=None, flux_constraint=self.constraint, clip_rule="data")
        with mock.patch.object(mc, "truth_ratio", lambda *a: (None, None)), \
                mock.patch.object(mc.toys, "flux_probabilities", reader), self.assertRaises(_Stop):
            mc.run_item(a, {"inputs": {}, "bkg": {}}, "clipmean", "3620000")
        self.assert_noatime_only(self.constraint, got)

    def test_receipt_reads_the_constraint_through_o_noatime(self):
        got, reader = self.spy()
        a = argparse.Namespace(flux_constraint=self.constraint)
        with mock.patch.object(mc, "_load_world", lambda a: {}), \
                mock.patch.object(mc.toys, "flux_probabilities", reader), self.assertRaises(_Stop):
            mc.receipt(a)
        self.assert_noatime_only(self.constraint, got)

    def test_receipt_reads_the_assembly_through_o_noatime(self):
        got, reader = self.spy()
        a = argparse.Namespace(staged=self.tmp, flux_constraint=self.constraint)
        with mock.patch.object(mc, "_load_world", lambda a: {"inputs": {}, "bkg": {}}), \
                mock.patch.object(mc.toys, "flux_probabilities", lambda p: None), \
                mock.patch.object(mc.fs, "load_s1", reader), self.assertRaises(_Stop):
            mc.receipt(a)
        self.assert_noatime_only(self.s1, got)

    def test_clipcheck_reads_the_assembly_through_o_noatime(self):
        got, reader = self.spy()
        a = argparse.Namespace(staged=self.tmp, clip_rule="data")
        with mock.patch.object(mc.fs, "load_s1", reader), self.assertRaises(_Stop):
            mc.clipcheck(a)
        self.assert_noatime_only(self.s1, got)

    def test_the_copy_gives_the_bound_readers_answer(self):
        want = digest(self.constraint)
        self.plain.clear()
        with mock.patch.object(sa, "CONSTRAINT_SHA256", want):
            w = mc.via_noatime(sa.flux_weights, self.constraint)
            self.assertNotIn(str(self.constraint), self.plain)
            np.testing.assert_array_equal(w, sa.flux_weights(self.constraint))


# ------------------------------------------------- the outcome path, end to end (the audit's B1 on #673)


def write_product(path: Path, x, xtrue=None, meta=None, **extra):
    arrays = {"xsec_flat": np.asarray(x, float)}
    if xtrue is not None:
        arrays["xtrue_flat"] = np.asarray(xtrue, float)
    meta = dict(meta or {"seconds_unfold": 1.0, "peak_rss_kib": 1})
    meta.setdefault("config", "R")                       # the estimator each product records (amendment 2)
    meta.setdefault("clip_rule", "data")                 # and the clipping rule
    np.savez(path, meta=json.dumps(meta), **arrays, **extra)


class Pipeline(unittest.TestCase):
    """``null`` then ``readout`` on a synthetic product set at a truth: every number the readout grades or prints is
    checked against an independent build from the fixture's own parts, and every refusal fires."""
    N = 16

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="fd1b-mc-pl-"))
        rng = np.random.default_rng(31)
        n = cls.N
        cls.f = rng.uniform(1.0, 2.0, n)
        cls.U = np.eye(n)
        cls.X_T = cls.f * 1.05
        cls.Xb = {b: cls.X_T * (1 + rng.normal(0.002, 0.01, (k, n))) for b, k in sa.EXPECT.items()}
        cls.R = cls.X_T * (1 + rng.normal(0, 0.001, (len(sa.STAT_REPLICAS), n)))
        cls.delta = {}
        for b in sa.LATERAL_BANDS:
            d = rng.normal(0, 0.01, n) * cls.f
            cls.delta[b] = d if d[np.argmax(np.abs(d))] > 0 else -d
        w = rng.uniform(0.5, 4.0, 100)
        cls.constraint = cls.tmp / "constraint.txt"
        cls.constraint.write_text("".join(f"Flux {i} {w[i]!r}\n" for i in range(100)))
        # C_model's two vertices, scaled to C_e's fractional diagonal ce, so that clause S's lists take every case:
        # R00-R03 MEC only (C_T's list, not C_T^-'s); R04-R07 a share near 0.35 (in neither, but in both at 0.25);
        # R08-R11 the other vertex (in both); R12-R13 both vertices (in C_T's and C_T^-'s, not in C_T^- read on C_T)
        ce = np.diag(cls.c_e(cls)) / cls.X_T ** 2
        c = np.arange(n)
        cls.s_mec = np.where(c < 4, np.sqrt(6 * ce), np.where((c >= 12) & (c < 14), np.sqrt(6 * ce), 0.001))
        cls.s_other = np.where((c >= 4) & (c < 8), np.sqrt(0.54 * ce),
                               np.where((c >= 8) & (c < 14), np.sqrt(3 * ce), 0.001))
        cls.frac = np.outer(cls.s_mec, cls.s_mec) + np.outer(cls.s_other, cls.s_other)
        # the staged assembly, in load_s1's layout
        blocks = {f"band:{b}": sa.mat_cov(rng.normal(0, 0.01, cls.Xb[b].shape) * cls.f)
                  for b in sa.EXPECT}
        blocks.update({f"lat:{b}": np.outer(d / 2, d / 2) for b, d in cls.delta.items()})
        blocks.update(stat=np.diag((0.001 * cls.f) ** 2), normalization=np.outer(0.014 * cls.f, 0.014 * cls.f),
                      seed=np.zeros((n, n)))
        cls.s1_blocks = blocks
        (cls.tmp / "staged" / "s1").mkdir(parents=True)
        cls.assembly = cls.tmp / "staged" / "s1" / "s1_assembly.npz"
        np.savez(cls.assembly, meta=json.dumps({"blocks": sorted(blocks)}), f=cls.f, U=cls.U,
                 C_e=sum(blocks.values()), C_model_frac=cls.frac,
                 **{"C_" + k.replace(":", "_"): v for k, v in blocks.items()})
        cls.definition = cls.tmp / "definition.json"
        cls.definition.write_text(json.dumps({"U": cls.U.tolist()}))
        cls.cmodel = cls.tmp / "cmodel.json"
        cls.cmodel.write_text(json.dumps({"vertices": ["genie_mec", "genie_other"],
                                          "S": [cls.s_mec.tolist(), cls.s_other.tolist()]}))
        cls.i2 = cls.tmp / "i2.json"
        cls.i2.write_text(json.dumps({"A": ((0.01 * cls.f) ** 2).tolist()}))
        cls.groups = {b: [f"{b}_{i}" for i in range(sa.EXPECT[b])] for b in toys.INTERACTION_BANDS}
        cls.flux_p = w / w.sum()
        cls.toy_rng = np.random.default_rng(32)
        cls.clip_offset = np.where(np.arange(n) % 4 == 0, 0.7, 0.1)       # R00, R04, ... above delta*, the rest below
        cls.receipt_file = cls.tmp / "receipt.json"
        cls.receipt_file.write_text(json.dumps({"verdict": "PASS", "clipping_c1": {"source_split": {"wr": 1}},
                                                "n_clip": {"seed": 3620011}}))
        cls.clip_ref = np.where(np.arange(n) % 2 == 0, 2.0, 0.0)          # N_clip's clipped mass, zero in odd cells

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.ps = [plain_noatime(), mock.patch.object(fs, "S1_NPZ_SHA256", digest(self.assembly)),
                   mock.patch.object(sa, "CONSTRAINT_SHA256", digest(self.constraint)),
                   mock.patch.object(sa, "fine_map", lambda p: json.loads(Path(p).read_text())["U"]),
                   mock.patch.object(sa, "functional_matrix", lambda fm: np.asarray(fm, float)),
                   mock.patch.object(mc.fn, "null_contents", functools.partial(fn.null_contents, n_mc=20_000))]
        for p in self.ps:
            p.start()
            self.addCleanup(p.stop)

    def products(self, name: str, truth: str = "g18", central_true=None) -> Path:
        """One product set at T under ``<tmp>/<name>``: central, seed, 175 blocks, 50 stat replicas, 300 toys."""
        d = self.tmp / name
        d.mkdir()
        write_product(d / mc.product_name("t", truth, "central", "T"), self.X_T,
                      self.f if central_true is None else central_true)
        write_product(d / mc.product_name("t", truth, "seed", "T"), self.X_T)
        for b, X in self.Xb.items():
            for i, x in enumerate(X):
                write_product(d / mc.product_name("t", truth, "block", f"{b}_{i}"), x)
        for b, x in zip(sa.STAT_REPLICAS, self.R):
            write_product(d / mc.product_name("t", truth, "stat", str(b)), x)
        rng = np.random.default_rng(33)
        sig = np.sqrt(np.diag(self.expected()["C_e"]))
        self.raw, self.draws = [], []
        self.clip_toys = []
        for k, seed in enumerate(mc.TOY_SEEDS[truth]):
            dr = toys.draw_for_seed(seed, self.flux_p, self.groups)
            x = self.X_T + rng.normal(0, 1, self.N) * sig
            n1 = {a: {"max_composite_over_max_single": 2.0 + k / 1000, "rows_above_bound": int(k == 7) * 3}
                  for a in ("wt", "wr", "bkgw", "denom")}
            clip = {"signal": {"sum_lambda": 1000.0, "sum_negative": -(k % 5) * 1.0, "rows_negative": k % 5},
                    "background": {"sum_lambda": 100.0, "sum_negative": -(k % 3) * 0.5, "rows_negative": k % 3}}
            cr = self.clip_ref * (k % 4) / 3.0
            write_product(d / mc.product_name("t", truth, "toy", str(seed)), x, self.X_T,
                          {"draw": dr, "universe_info": {"n1": n1}, "seconds_unfold": 1.0, "peak_rss_kib": 1,
                           "clip": clip}, clip_reco_flat=cr, clip_truth_flat=0.5 * cr)
            self.raw.append(x)
            self.draws.append(dr)
            self.clip_toys.append(clip)
        sig_T = np.sqrt(np.diag(self.expected()["C_T"]))
        write_product(d / mc.product_name("t", truth, "clipmean", "3620011"), self.X_T + self.clip_offset * sig_T,
                      self.X_T, {"n_clip_seed": 3620011, "seconds_unfold": 1.0, "peak_rss_kib": 1,
                                 "clip": {"signal": {"sum_lambda": 1000.0, "sum_negative": -6.0, "rows_negative": 6},
                                          "background": {"sum_lambda": 100.0, "sum_negative": -1.0, "rows_negative": 2}}},
                      clip_reco_flat=self.clip_ref, clip_truth_flat=0.5 * self.clip_ref)
        return d

    def c_e(self) -> np.ndarray:
        """C_e built from the fixture's parts by S1's estimators."""
        w = np.array([float(l.split()[2]) for l in self.constraint.read_text().splitlines()])
        g = self.X_T / self.f
        C_e = sum(sa.mat_cov(X, w if b == sa.FLUX else None) for b, X in self.Xb.items())
        C_e = C_e + np.cov(self.R, rowvar=False, ddof=1)
        C_e = C_e + sum(np.outer(d * g / 2, d * g / 2) for d in self.delta.values())
        return C_e + np.outer(sa.NORM_FRACTION * self.X_T, sa.NORM_FRACTION * self.X_T)

    def expected(self) -> dict:
        """C_e, C_T and the leave-out C_T^- built from the fixture's parts by S1's estimators."""
        w = np.array([float(l.split()[2]) for l in self.constraint.read_text().splitlines()])
        C_e = self.c_e()
        C_mabs = sa.model_abs(self.X_T, self.frac)
        C_minus = sa.model_abs(self.X_T, np.outer(self.s_other, self.s_other))
        p = {b: (w / w.sum() if b == sa.FLUX else np.full(len(X), 1 / len(X))) for b, X in self.Xb.items()}
        offset = -sum(p[b] @ X - self.X_T for b, X in self.Xb.items())
        return {"C_e": C_e, "C_mabs": C_mabs, "C_T": C_e + C_mabs, "C_minus": C_minus, "offset": offset}

    def args(self, d: Path, truth="g18", **kw):
        a = argparse.Namespace(staged=self.tmp / "staged", unfolds=d, definition=self.definition,
                               cmodel_json=self.cmodel, flux_constraint=self.constraint, tag="t", truth=truth,
                               i2=self.i2, out=d / "out.json", estimator="R", clip_rule="data")
        for k, v in kw.items():
            setattr(a, k, v)
        return a

    def null_and_readout(self, d: Path, truth="g18", **kw):
        nl = mc.null_step(self.args(d, truth, **kw))
        p = d / "null.json"
        p.write_text(json.dumps(nl, default=float))
        return nl, p

    def readout(self, d, p, truth="g18", **kw):
        return mc.readout(self.args(d, truth, null=p, expect_null_sha256=digest(p), **kw))

    def test_readout_reproduces_every_graded_and_printed_number(self):
        d = self.products("ok")
        nl, p = self.null_and_readout(d)
        self.assertEqual(nl["made_from"], mc.made_from(self.args(d), self.U))
        self.assertLessEqual(nl["C_T"]["match_rel"], fn.MATCH_TOL)
        ro = self.readout(d, p)
        ex = self.expected()
        np.testing.assert_allclose(ro["sigma_T"], np.sqrt(np.diag(ex["C_T"])), rtol=1e-10)
        X_hat = fs.surrogate(np.array(self.raw), self.draws, self.delta, self.f, self.X_T)
        E = X_hat - self.X_T
        self.assertGreater(np.max(np.abs(X_hat - np.array(self.raw))), 0)   # the surrogate moves the toys
        np.testing.assert_allclose(ro["descriptive"]["toys_mean_error"], E.mean(axis=0), rtol=1e-10, atol=1e-14)
        np.testing.assert_allclose(ro["descriptive"]["predicted_offset_uncentred_draws"], ex["offset"], rtol=1e-10)
        self.assertGreater(np.max(np.abs(ex["offset"])), 0)
        counts = np.sum(np.abs(E) <= np.sqrt(np.diag(ex["C_T"])), axis=0)
        counts_minus = np.sum(np.abs(E) <= np.sqrt(np.diag(ex["C_e"] + ex["C_minus"])), axis=0)
        self.assertNotEqual(counts.tolist(), counts_minus.tolist())                  # the fixture can tell them apart
        self.assertEqual(ro["C_T"]["counts"], counts.tolist())
        self.assertEqual(ro["leave_out_mec"]["grade"]["counts"], counts_minus.tolist())
        dom = lambda C, Cm: [f"R{c:02d}" for c in range(self.N) if Cm[c, c] > 0.5 * C[c, c]]  # noqa: E731
        want = {"C_T": dom(ex["C_T"], ex["C_mabs"]), "C_T_minus_mec": dom(ex["C_e"] + ex["C_minus"], ex["C_minus"])}
        self.assertEqual(ro["clause_S_model_dominant_cells"], want)
        cells = lambda *r: [f"R{c:02d}" for c in r]  # noqa: E731
        self.assertEqual(want, {"C_T": cells(0, 1, 2, 3, 8, 9, 10, 11, 12, 13),
                                "C_T_minus_mec": cells(8, 9, 10, 11, 12, 13)})
        # the fixture separates every wrong reading: the leave-out list read on C_T, C_T's list, a threshold of 0.25
        self.assertNotEqual(dom(ex["C_T"], ex["C_minus"]), want["C_T_minus_mec"])
        share = np.diag(ex["C_mabs"]) / np.diag(ex["C_T"])
        self.assertTrue(np.all((share[4:8] > 0.25) & (share[4:8] < 0.5)))
        self.assertNotIn("n1_max_composite_over_max_single", ro["descriptive"])     # N1 is read by its own step

    def test_the_clipping_readout(self):
        """Consult (ii) and the reading fixed before any number is read: o_c from the clipmean product, the toys'
        clipped fractions and per-cell mass against N_clip's, and the flagged cells the clipping may explain."""
        d = self.products("clip")
        _, p = self.null_and_readout(d)
        cl = self.readout(d, p)["clipping"]
        np.testing.assert_allclose(cl["offset_over_sigma"], self.clip_offset, rtol=1e-10)
        self.assertEqual(cl["n_clip_seed"], 3620011)
        fs_ = [abs(c["signal"]["sum_negative"]) / 1000.0 for c in self.clip_toys]
        self.assertEqual(cl["clipped_fraction"]["signal"], {"min": min(fs_), "median": float(np.median(fs_)), "max": max(fs_)})
        rel = cl["toys_clipped_mass_over_n_clip"]["reco"]
        q = np.array([(k % 4) / 3.0 for k in range(300)])
        self.assertAlmostEqual(rel["median"][0], float(np.median(q)), places=12)
        self.assertAlmostEqual(rel["max"][0], 1.0, places=12)
        self.assertTrue(np.isnan(rel["median"][1]))                       # N_clip clips nothing there
        rm = {"C_T": self.expected()["C_T"], "X_T": self.X_T}
        flags = [c in (0, 1, 4) for c in range(self.N)]
        got = mc.clipping_readout(d, "t", "g18", self.U, rm, flags)["flagged_cells_the_clipping_may_explain"]
        self.assertEqual(got, ["R00", "R04"])                             # R01 flagged but |o| = 0.1 < 0.667; 0.7 >= 0.667
        (d / mc.product_name("t", "g18", "clipmean", "3620012")).write_bytes((d / mc.product_name(
            "t", "g18", "clipmean", "3620011")).read_bytes())
        with self.assertRaisesRegex(mc.Refusal, "clipmean"):
            mc.clipping_readout(d, "t", "g18", self.U, rm, flags)

    def test_the_graders_refuse_a_mixed_or_undeclared_estimator(self):
        d = self.products("est")
        nl, p = self.null_and_readout(d)
        self.readout(d, p)                                       # one estimator throughout: grades
        toy = d / mc.product_name("t", "g18", "toy", "3620005")
        z = np.load(toy, allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        arrays = {k: z[k] for k in z.files if k != "meta"}
        np.savez(toy, meta=json.dumps(dict(meta, config="B0")), **arrays)
        with self.assertRaisesRegex(mc.Refusal, "estimator 'B0'"):
            self.readout(d, p)
        with self.assertRaisesRegex(mc.Refusal, "estimator"):
            mc.null_step(self.args(d))
        meta.pop("config")
        np.savez(toy, meta=json.dumps(meta), **arrays)
        with self.assertRaisesRegex(mc.Refusal, "estimator None"):
            self.readout(d, p)
        with self.assertRaisesRegex(mc.Refusal, "not the declared 'B0'"):
            self.readout(d, p, estimator="B0")
        np.savez(toy, meta=json.dumps(dict(meta, config="R", clip_rule="nature")), **arrays)
        with self.assertRaisesRegex(mc.Refusal, "clip rule 'nature'"):
            self.readout(d, p)
        np.savez(toy, meta=json.dumps(dict(meta, config="R", clip_rule="data")), **arrays)
        self.readout(d, p)                                       # restored: grades again
        cm = d / mc.product_name("t", "g18", "clipmean", "3620011")
        z = np.load(cm, allow_pickle=False)
        np.savez(cm, meta=json.dumps(dict(json.loads(str(z["meta"])), config="B0")), **{k: z[k] for k in z.files if k != "meta"})
        a = argparse.Namespace(truths="g18", unfolds=d, staged=self.tmp / "staged", definition=self.definition,
                               tag="t", out=d / "cc.json", estimator="R", clip_rule="data",
                               receipt=self.receipt_file, expect_receipt_sha256=digest(self.receipt_file))
        with mock.patch.object(mc.fs, "reported_matrix", lambda s1: np.eye(self.N)), \
                self.assertRaisesRegex(mc.Refusal, "estimator"):
            mc.clipcheck(a)

    def test_clipcheck_up_front(self):
        """The director's ruling: o_c against S1's reported sigma before the bulk; TO_JOSEPH at |o_c| >= delta*."""
        d = self.products("cc")
        rep = np.diag((0.02 * self.f) ** 2)
        a = argparse.Namespace(truths="g18", unfolds=d, staged=self.tmp / "staged", definition=self.definition,
                               tag="t", out=d / "cc.json", estimator="R", clip_rule="data",
                               receipt=self.receipt_file, expect_receipt_sha256=digest(self.receipt_file))
        with mock.patch.object(mc.fs, "reported_matrix", lambda s1: rep):
            res = mc.clipcheck(a)
        sig_T = np.sqrt(np.diag(self.expected()["C_T"]))
        want = self.clip_offset * sig_T / np.sqrt(np.diag(rep))
        np.testing.assert_allclose(res["truths"]["g18"]["offset_over_reported_sigma"], want, rtol=1e-10)
        hit = [f"R{c:02d}" for c in range(self.N) if abs(want[c]) >= mc.CLIP_DELTA_STAR]
        self.assertEqual(res["truths"]["g18"]["cells_at_or_above_delta_star"], hit)
        self.assertEqual(res["verdict"], "TO_JOSEPH" if hit else "PROCEED")
        self.assertTrue(hit)
        self.assertEqual(res["truths"]["g18"]["n_clip_clip"]["signal"]["rows_negative"], 6)
        self.assertEqual(res["receipt_clipping_c1"], {"source_split": {"wr": 1}})          # carried from the receipt
        bad = argparse.Namespace(**{**vars(a), "expect_receipt_sha256": "0" * 64})
        with mock.patch.object(mc.fs, "reported_matrix", lambda s1: rep), self.assertRaisesRegex(mc.Refusal, "digest"):
            mc.clipcheck(bad)
        other = self.tmp / "receipt-other-seed.json"
        other.write_text(json.dumps({"verdict": "PASS", "clipping_c1": {}, "n_clip": {"seed": 3620012}}))
        bad = argparse.Namespace(**{**vars(a), "receipt": other, "expect_receipt_sha256": digest(other)})
        with mock.patch.object(mc.fs, "reported_matrix", lambda s1: rep), \
                self.assertRaisesRegex(mc.Refusal, "not the receipt's 3620012"):
            mc.clipcheck(bad)
        stop = self.tmp / "receipt-stop.json"
        stop.write_text(json.dumps({"verdict": "STOP", "clipping_c1": {}, "n_clip": {"seed": 3620011}}))
        bad = argparse.Namespace(**{**vars(a), "receipt": stop, "expect_receipt_sha256": digest(stop)})
        with mock.patch.object(mc.fs, "reported_matrix", lambda s1: rep), self.assertRaisesRegex(mc.Refusal, "not PASS"):
            mc.clipcheck(bad)
        with mock.patch.object(mc.fs, "reported_matrix", lambda s1: rep * 1e6):    # sigma 1000 x: nothing at delta*
            res = mc.clipcheck(a)
        self.assertEqual((res["verdict"], res["cells"]), ("PROCEED", []))
        (d / mc.product_name("t", "g18", "clipmean", "3620012")).write_bytes((d / mc.product_name(
            "t", "g18", "clipmean", "3620011")).read_bytes())
        with mock.patch.object(mc.fs, "reported_matrix", lambda s1: rep), self.assertRaisesRegex(mc.Refusal, "clipmean"):
            mc.clipcheck(a)

    def test_s1_0b_walls(self):
        d = self.tmp / "s10b"
        d.mkdir()
        items = mc.pilot_b(True, 3620011)
        self.assertEqual(items, [("g18", "clipmean", "3620011"), ("ar23", "clipmean", "3620011"),
                                 ("plugin", "clipmean", "3620011"), ("ar23", "central", "T"), ("plugin", "central", "T")])
        self.assertEqual(len(mc.pilot_b(False, 3620011)), 3)
        names = [mc.product_name("t", tr, r, i) for tr, r, i in items]
        for n in names[:-1]:
            write_product(d / n, self.X_T)
        out = d / "walls.json"
        argv = ["walls", "--unfolds", str(d), "--plugin", "yes", "--stage", "s1-0b", "--clip-seed", "3620011", "--tag",
                "t", "--out", str(out)]
        self.assertEqual(mc.main(argv), 1)                      # one product missing: REPRICE
        write_product(d / names[-1], self.X_T)
        out.unlink()
        self.assertEqual(mc.main(argv), 0)
        out.unlink()
        self.assertEqual(mc.main(argv[:7] + argv[9:]), 4)       # S1-0b without --clip-seed refuses

    def test_n1_reads_the_toys_record_without_grading(self):
        d = self.products("n1")
        res = mc.n1_step(self.args(d))
        self.assertEqual(res["verdict"], "STOP")
        self.assertEqual(res["toys_with_rows_above"]["wt"], [mc.product_name("t", "g18", "toy", "3620007")])
        self.assertAlmostEqual(res["max_composite_over_max_single"]["wr"], 2.299)
        self.assertFalse((d / "null.json").exists())

    def test_readout_refuses_what_the_null_was_not_made_from(self):
        d = self.products("ref")
        _, p = self.null_and_readout(d)
        with self.assertRaisesRegex(mc.Refusal, "null's digest"):
            mc.readout(self.args(d, null=p, expect_null_sha256="0" * 64))
        other = self.tmp / "cmodel-other.json"
        other.write_text(self.cmodel.read_text() + " ")
        with self.assertRaisesRegex(mc.Refusal, "the null was made from"):
            self.readout(d, p, cmodel_json=other)
        defn = self.tmp / "definition-other.json"
        defn.write_text(json.dumps({"U": (self.U * 2).tolist()}))
        forged = json.loads(p.read_text())                  # a null that claims the foreign U: the readout's own check
        forged["made_from"] = mc.made_from(self.args(d, definition=defn), self.U * 2)
        q = d / "null-forged.json"
        q.write_text(json.dumps(forged))
        with self.assertRaisesRegex(mc.Refusal, "functional is not S1's"):
            self.readout(d, q, definition=defn)
        stat = d / mc.product_name("t", "g18", "stat", "1")
        keep = stat.read_bytes()
        write_product(stat, self.R[0] * 1.0001)
        with self.assertRaisesRegex(mc.Refusal, "not made from these products"):
            self.readout(d, p)
        stat.write_bytes(keep)
        (d / (mc.product_name("t", "g18", "block", "MaRES_0") + ".partial-1.npz")).write_bytes(b"")
        with self.assertRaisesRegex(mc.Refusal, "partial products"):
            self.readout(d, p)

    def test_readout_refuses_a_missing_toy(self):
        d = self.products("miss")
        _, p = self.null_and_readout(d)
        (d / mc.product_name("t", "g18", "toy", "3620299")).unlink()
        with self.assertRaisesRegex(mc.Refusal, "declared seeds"):
            self.readout(d, p)

    def test_null_refuses_a_foreign_u_and_an_unrebuilt_cmodel(self):
        d = self.products("nullref")
        defn = self.tmp / "definition-null.json"
        defn.write_text(json.dumps({"U": (self.U * 2).tolist()}))
        with self.assertRaises(mc.Refusal):
            mc.null_step(self.args(d, definition=defn))
        bad = self.tmp / "cmodel-bad.json"
        bad.write_text(json.dumps({"vertices": ["genie_mec", "genie_other"],
                                   "S": [(self.s_mec * 1.01).tolist(), self.s_other.tolist()]}))
        with self.assertRaises(mc.Refusal):
            mc.null_step(self.args(d, cmodel_json=bad))

    def test_plugin_control_b(self):
        d = self.products("plug", truth="plugin")
        _, p = self.null_and_readout(d, "plugin")
        self.assertIn(self.readout(d, p, "plugin")["verdict"], ("COVERS", "UNDER-COVERS"))
        d = self.products("plugbad", truth="plugin", central_true=self.f * (1 + 1e-9))
        _, p = self.null_and_readout(d, "plugin")
        with self.assertRaises(mc.Refusal):
            self.readout(d, p, "plugin")


class ExactN1(unittest.TestCase):
    """Amendment 2's receipt core on a small synthetic bank where every draw can be enumerated: the screen's
    proposition, screen against no-screen on every row and draw, the director's conditions (a tightened floor is
    caught), block and budget handling, the near-bound recompute, the pinned-order denominator check, and the
    cross-term histograms against a direct build."""
    BANDS = {"Flux": 3, "A": 2, "B": 2, "C": 2}

    def setUp(self):
        rng = np.random.default_rng(11)
        self.tags = [f"{b}_{i}" for b, n in self.BANDS.items() for i in range(n)]
        self.col = {t: c for c, t in enumerate(self.tags)}
        n = 400
        cv = rng.uniform(0.5, 1.5, n)
        cv[:20] = rng.uniform(1e-4, 1e-3, 20)              # small CV weights: N1's premise
        cv[20:25] = 0.0                                    # CV = 0 rows
        V = cv[None, :] * (1 + rng.normal(0, 0.6, (len(self.tags), n)))
        V[:, :20] = rng.uniform(0.0, 0.05, (len(self.tags), 20))   # large ratios on the small-CV rows
        V[:, 20:25] = rng.normal(0, 0.3, (len(self.tags), 5))
        V[0, 30] = 0.0                                     # a zero universe weight
        V[:, 40] = 0.0                                     # a row where every universe is 0 (0/0)
        cv[40] = 0.0
        self.V, self.cv = V, cv
        draws = [[f"Flux_{f}", f"A_{a}", f"B_{b}", f"C_{c}"] for f in range(3) for a in range(2) for b in range(2)
                 for c in range(2)]
        self.dcols = mc.draw_columns(draws, self.col)
        self.all_rows = np.arange(n)

    def run_exact(self, **kw):
        L = kw.pop("L", mc.screen_floor(self.V, self.col))
        return mc.exact_n1(self.V, self.cv, self.dcols, L, self.all_rows, **kw)

    def test_the_screens_proposition_on_every_row_and_draw(self):
        L = mc.screen_floor(self.V, self.col)
        ref = mc.no_screen_n1(self.V, self.cv, self.dcols, self.all_rows)
        for d, cs in enumerate(self.dcols):
            acc, _ = mc.pinned_composite(self.V, self.cv, cs, self.all_rows)
            screened_out = np.abs(acc) <= mc.N1_BOUND * L
            self.assertTrue(np.all(ref[d][screened_out] <= mc.N1_BOUND), d)
        self.assertGreater(int(np.sum(ref > mc.N1_BOUND)), 0)              # the fixture has rows above

    def test_screened_equals_no_screen_exhaustively(self):
        res = self.run_exact()
        ref = mc.no_screen_n1(self.V, self.cv, self.dcols, self.all_rows)
        self.assertEqual(mc.validate_screen(res, ref, self.all_rows), [])
        self.assertEqual(res["pairs_above"], int(np.sum(ref > mc.N1_BOUND)))
        self.assertEqual(res["rows_above"], int(np.sum(ref.max(axis=0) > mc.N1_BOUND)))
        self.assertAlmostEqual(res["max_evaluated"], float(ref.max()), places=9)

    def test_a_tightened_floor_is_caught(self):
        """A floor raised just enough to screen out a real pair above the bound: the validation and the independent
        floor check each catch it, and the true floor passes both."""
        ref = mc.no_screen_n1(self.V, self.cv, self.dcols, self.all_rows)
        L = mc.screen_floor(self.V, self.col)
        self.assertTrue(mc.screen_floor_check(self.V, self.col, L))
        row = int(np.argmax(ref.max(axis=0)))
        self.assertGreater(ref[:, row].max(), mc.N1_BOUND)
        amax = max(abs(mc.pinned_composite(self.V, self.cv, cs, np.array([row]))[0][0]) for cs in self.dcols)
        bad = L.copy()
        bad[row] = amax / mc.N1_BOUND * (1 + 1e-6)        # every draw of this row now screened out, past the margin
        res = self.run_exact(L=bad)
        self.assertTrue(mc.validate_screen(res, ref, self.all_rows), "a tightened floor went unseen")
        self.assertFalse(mc.screen_floor_check(self.V, self.col, bad))
        with mock.patch.object(mc, "screen_floor", lambda V, col: bad):
            self.assertFalse(mc.screen_floor_check(self.V, self.col, mc.screen_floor(self.V, self.col)))

    def test_blocks_do_not_change_the_result(self):
        r1, r7 = self.run_exact(block=1), self.run_exact(block=7)
        for k in ("pairs_past_screen", "pairs_above", "rows_above", "max_evaluated", "sample_above"):
            self.assertEqual(r1[k], r7[k], k)
        np.testing.assert_array_equal(r1["worst"], r7["worst"])
        np.testing.assert_array_equal(r1["negative_composite_rows"], r7["negative_composite_rows"])

    def test_the_pair_budget_refuses_as_invalid(self):
        with self.assertRaises(mc.InvalidReceipt):
            self.run_exact(max_pairs=0)
        self.assertTrue(issubclass(mc.InvalidReceipt, mc.Refusal))

    def test_a_near_bound_pair_is_recomputed_in_composes_order(self):
        V, cv = self.V.copy(), self.cv.copy()
        cs = self.dcols[0]
        row = 100
        cv[row] = 1.0
        V[:, row] = 1.0
        V[cs[1:], row] = 1.0
        V[cs[0], row] = 10.0                               # a_D = 10 + 0 = 10, peak 10 ... ratio 1
        V[cs[1], row] = 1.0 + 10.0 * 1.0 * (1 + 1e-12)    # make a_D near 10 x peak? keep simple: check the counter
        res = mc.exact_n1(V, cv, self.dcols, np.zeros(V.shape[1]), self.all_rows, block=5)
        ref = mc.no_screen_n1(V, cv, self.dcols, self.all_rows)
        self.assertEqual(mc.validate_screen(res, ref, self.all_rows), [])
        with mock.patch.object(mc, "NEAR_BOUND_REL", 1.0):     # every evaluated pair is near: all recomputed
            res2 = mc.exact_n1(V, cv, self.dcols, np.zeros(V.shape[1]), self.all_rows, block=5)
        self.assertEqual(res2["near_bound_recomputed"], res2["pairs_past_screen"])
        self.assertEqual(res2["sample_above"], res["sample_above"])

    def test_the_negative_composite_extent(self):
        reco = np.zeros(self.V.shape[1], bool)
        reco[::3] = True
        res = self.run_exact(reco=reco)
        any_neg = np.zeros(self.V.shape[1], bool)
        for d, cs in enumerate(self.dcols):
            acc, _ = mc.pinned_composite(self.V, self.cv, cs, self.all_rows)
            neg = (acc < 0) & (self.cv > 0)
            any_neg |= neg
            self.assertEqual(res["negative_composite_rows"][d], int(neg.sum()), d)
            self.assertAlmostEqual(res["negative_composite_sum"][d], float(np.minimum(acc[reco], 0).sum()), places=9)
            self.assertAlmostEqual(res["composite_sum"][d], float(acc[reco].sum()), places=9)
        self.assertEqual(res["negative_rows_in_some_draw"], int(any_neg.sum()))
        self.assertGreater(res["negative_rows_in_some_draw"], 0)
        f = mc.clipped_fraction(np.array([-1.0, 0.0, -2.0]), np.array([10.0, 0.0, 4.0]))
        self.assertEqual(f.tolist(), [0.1, 0.0, 0.5])
        self.assertEqual(mc._spread(np.array([0.1, 0.5, 0.3])),
                         {"min": 0.1, "median": 0.3, "p90": 0.46, "q95": 0.48, "max": 0.5})

    def test_clip_cells_against_a_direct_build(self):
        rng = np.random.default_rng(16)
        n, nb, n_bins = self.V.shape[1], 50, 6
        Vb = rng.normal(0.2, 0.3, (len(self.tags), nb))
        cvb = np.abs(rng.normal(0.2, 0.1, nb))
        V = {"wr": self.V, "wt": self.V * 1.3, "bkgw": Vb}
        cv = {"wr": self.cv, "wt": self.cv * 1.3, "bkgw": cvb}
        flat = {"signal": rng.integers(-1, n_bins, n), "background": rng.integers(-1, n_bins, nb),
                "truth": rng.integers(-1, n_bins, n)}
        U = rng.uniform(0, 1, (3, n_bins))
        k_flat = rng.uniform(0.5, 2.0, n_bins)
        truth_rows = rng.random(n) < 0.7
        reco = rng.random(n) < 0.8
        got = mc.clip_cells(V, cv, self.dcols, flat, n_bins, U, k_flat, truth_rows, reco, block=5)
        for d, cs in enumerate(self.dcols):
            ar, _ = mc.pinned_composite(V["wr"], cv["wr"], cs, np.arange(n))
            at, _ = mc.pinned_composite(V["wt"], cv["wt"], cs, np.arange(n))
            ab, _ = mc.pinned_composite(V["bkgw"], cv["bkgw"], cs, np.arange(nb))
            ms, mb = flat["signal"] >= 0, flat["background"] >= 0
            neg = np.bincount(flat["signal"][ms], weights=np.maximum(-ar[ms], 0), minlength=n_bins) + \
                np.bincount(flat["background"][mb], weights=np.maximum(-ab[mb], 0), minlength=n_bins)
            pos = np.bincount(flat["signal"][ms], weights=np.maximum(ar[ms], 0), minlength=n_bins) + \
                np.bincount(flat["background"][mb], weights=np.maximum(ab[mb], 0), minlength=n_bins)
            rows = (flat["truth"] >= 0) & truth_rows & reco & (ar < 0)
            tru = np.bincount(flat["truth"][rows], weights=np.abs(at[rows]), minlength=n_bins) * k_flat
            np.testing.assert_allclose(got["reco_clip"][d], U @ neg, rtol=1e-10, atol=1e-12)
            np.testing.assert_allclose(got["reco_plus"][d], U @ pos, rtol=1e-10, atol=1e-12)
            np.testing.assert_allclose(got["truth_clip"][d], U @ tru, rtol=1e-10, atol=1e-12)
        self.assertGreater(got["reco_clip"].max(), 0)
        self.assertGreater(got["truth_clip"].max(), 0)
        pc = mc._per_cell(got["truth_clip"])
        np.testing.assert_array_equal(pc["max"], got["truth_clip"].max(axis=0))
        np.testing.assert_array_equal(pc["median"], np.median(got["truth_clip"], axis=0))

    def test_t2_clip_flags_at_delta_star(self):
        d = mc.CLIP_DELTA_STAR
        self.assertEqual(mc.clip_flags(np.array([d, -d, np.nextafter(d, 0), 0.0, 2 * d])), [0, 1, 4])

    def test_c3_the_screen_keeps_a_pair_at_the_rounded_bound(self):
        """A floor with 10 L equal to the matmul's |a_D| bit for bit, on one row: without the margin the pair would be
        screened out; with it, it is evaluated."""
        row, d = 200, 3
        S = np.zeros(len(self.tags))
        S[self.dcols[d]] = 1.0
        A = float(S @ self.V[:, row] - (S.sum() - 1.0) * self.cv[row])
        L0 = abs(A) / mc.N1_BOUND
        while mc.N1_BOUND * L0 < abs(A):
            L0 = np.nextafter(L0, np.inf)
        while mc.N1_BOUND * L0 > abs(A):
            L0 = np.nextafter(L0, -np.inf)
        self.assertEqual(mc.N1_BOUND * L0, abs(A))
        L = np.full(self.V.shape[1], 1e300)
        L[row] = L0
        res = mc.exact_n1(self.V, self.cv, [self.dcols[d]], L, self.all_rows, block=1)
        self.assertEqual(res["pairs_past_screen"], 1)

    def test_c2_the_denominator_n1(self):
        rng = np.random.default_rng(17)
        dcv = rng.uniform(1, 2, 30)
        D = dcv[None, :] * (1 + rng.normal(0, 0.05, (len(self.tags), 30)))
        cs = self.dcols[4]
        D[cs[0], 7] = 30.0 * dcv[7]                       # one draw's cell far above its peak's tenth
        got = mc.denominator_check(D, dcv, self.dcols)
        want, worst = 0, 0.0
        for d, c in enumerate(self.dcols):
            acc = D[c[0]].copy()
            peak = np.abs(acc)
            for j in c[1:]:
                acc += D[j] - dcv
                np.maximum(peak, np.abs(D[j]), out=peak)
            r = mc.n1_ratio(acc, peak)
            want += int(np.sum(r > mc.N1_BOUND))
            worst = max(worst, float(r.max()))
        self.assertEqual(got["n1"]["pairs_above"], want)
        self.assertAlmostEqual(got["n1"]["max"], worst, places=12)
        with mock.patch.object(mc, "N1_BOUND", 0.5):
            self.assertGreater(mc.denominator_check(D, dcv, self.dcols)["n1"]["pairs_above"], 0)

    def test_n1_ratio_conventions(self):
        got = mc.n1_ratio(np.array([0.0, 0.0, 3.0, -4.0]), np.array([0.0, 2.0, 0.0, 2.0]))
        self.assertEqual(got.tolist(), [1.0, 0.0, np.inf, 2.0])

    def test_the_validation_checks_pairs_and_worsts_separately(self):
        rows = np.array([3, 8])
        ref = np.array([[12.0, 1.0], [2.0, 1.0]])            # row 3 above in draw 0 only
        ok = {"sample_above": {(0, 3)}, "worst": np.zeros(10)}
        ok["worst"][3] = 12.0
        self.assertEqual(mc.validate_screen(ok, ref, rows), [])
        pair_wrong = {"sample_above": {(1, 3)}, "worst": ok["worst"]}        # worst right, pair wrong
        self.assertTrue(any("pairs" in b for b in mc.validate_screen(pair_wrong, ref, rows)))
        worst_wrong = {"sample_above": {(0, 3)}, "worst": np.where(np.arange(10) == 3, 11.0, 0.0)}   # pairs right
        self.assertTrue(any("worst" in b for b in mc.validate_screen(worst_wrong, ref, rows)))

    def test_a_draw_missing_a_band_is_invalid(self):
        with self.assertRaises(mc.InvalidReceipt):
            mc.draw_columns([["Flux_0", "A_0", "B_0"]], self.col)

    def test_the_denominator_check_in_composes_order(self):
        rng = np.random.default_rng(12)
        dcv = rng.uniform(1, 2, 30)
        D = dcv[None, :] * (1 + rng.normal(0, 0.05, (len(self.tags), 30)))
        self.assertEqual(mc.denominator_check(D, dcv, self.dcols)["draws_with_nonpositive_cells"], [])
        cs = self.dcols[5]
        D[cs[1], 3] = dcv[3] - (D[cs[0], 3] + sum(D[c, 3] - dcv[3] for c in cs[2:]))   # d_D = 0 in draw 5's cell 3
        acc = D[cs[0], 3] + sum(D[c, 3] - dcv[3] for c in cs[1:])
        got = mc.denominator_check(D, dcv, self.dcols)
        self.assertEqual(5 in got["draws_with_nonpositive_cells"], bool(acc <= 0))
        self.assertTrue(got["draws_with_nonpositive_cells"])

    def test_flat_cells_are_histogramdds_bins(self):
        rng = np.random.default_rng(13)
        edges = [np.array([0.0, 0.5, 1.0]), np.array([0.0, 1.0, 2.0, 3.0])]
        x = np.column_stack([rng.uniform(-0.2, 1.2, 500), rng.uniform(-0.5, 3.5, 500)])
        x[:5, 0] = 1.0                                     # on the closed last edge
        x[5:10, 1] = 1.0                                   # on an inner edge
        f = mc.flat_cells(x, edges)
        w = rng.uniform(0, 1, 500)
        h = np.histogramdd(x, bins=edges, weights=w)[0].ravel()
        np.testing.assert_allclose(np.bincount(f[f >= 0], weights=w[f >= 0], minlength=h.size), h, rtol=1e-14)

    def test_crossterm_against_a_direct_build(self):
        rng = np.random.default_rng(14)
        n_bins = 6
        flat = rng.integers(-1, n_bins, self.V.shape[1])
        U = rng.uniform(0, 1, (3, n_bins))
        H_p, H_a, H0 = mc.crossterm(self.V, self.cv, self.dcols, flat, n_bins, U, block=4)
        m = flat >= 0
        nz = self.cv != 0
        for d, cs in enumerate(self.dcols):
            add, _ = mc.pinned_composite(self.V, self.cv, cs, self.all_rows)
            prod = self.V[cs[0]].copy()
            for c in cs[1:]:
                prod = np.where(nz, prod * (self.V[c] / np.where(nz, self.cv, 1.0)), prod + self.V[c])
            np.testing.assert_allclose(H_a[d], U @ np.bincount(flat[m], weights=add[m], minlength=n_bins), rtol=1e-10)
            np.testing.assert_allclose(H_p[d], U @ np.bincount(flat[m], weights=prod[m], minlength=n_bins), rtol=1e-9)
        np.testing.assert_allclose(H0, U @ np.bincount(flat[m], weights=self.cv[m], minlength=n_bins), rtol=1e-14)
        self.assertFalse(np.allclose(H_p, H_a))
        z = mc.cross_z(H_p, H_a, H0, np.full(3, 0.1))
        want = np.abs((H_p - H_a) / H0) / 0.1
        np.testing.assert_allclose(z["max_abs"], want.max(axis=0), rtol=1e-12)


class Receipt(Case):
    """``receipt`` over the toy bank (amendment 2): the single-universe counts against the raw weights, the exact
    pass against compose's own per-draw record, N_clip against clip_draw, the one-read loader, the verdict."""

    def setUp(self):
        super().setUp()
        self.n_bins = int(np.prod([np.asarray(e).size - 1 for e in self.inputs["edges"]]))
        self.U = np.random.default_rng(15).uniform(0, 1, (sa.N_CELLS, self.n_bins))
        self.seeds = (3620000, 3630001, 3640002)

    def test_the_receipt_subtracts_the_float32_cv_denominator(self):
        """(e2) in the receipt: with the npz's denom_nd far above hist_f32(tdw_CV) in one cell, subtracting the npz's
        would drive the composites there below zero (section 2b); the float32 d_CV does not."""
        d32 = s5p_universe.denominator(self.bank_cv, np.ones(50), self.inputs["edges"])
        npz = np.array(d32, float)
        npz.flat[int(np.flatnonzero(np.ravel(npz) > 0)[0])] += 50.0
        with mock.patch.dict(self.inputs, {"denom_nd": npz}):           # the detector universes carry it (check D)
            res, _ = self.run_receipt(self.inputs)
        self.assertEqual(res["denominator"]["draws_with_nonpositive_cells"], [])

    def run_receipt(self, inputs, bound=1.05):
        world = {"inputs": inputs, "bkg": self.bkg, "bank_cv": self.bank_cv, "flux": self.flux,
                 "groups": toys.interaction_groups(self.w.bank), "pins": json.loads(self.w.pins.read_text()),
                 "tdw_cv": np.ones(50)}
        a = argparse.Namespace(bank=self.w.bank, detector_dir=self.w.det, flux_constraint=self.w.constraint,
                               staged=self.tmp, definition=self.tmp / "definition.json")
        s1 = {"f": np.ones(sa.N_CELLS), "U": self.U, "blocks": {"stat": np.eye(sa.N_CELLS) * 1e-4}}
        labels = [(t, sd) for t in mc.TRUTHS for sd in mc.TOY_SEEDS[t]]
        (self.tmp / "s1").mkdir(exist_ok=True)
        (self.tmp / "s1" / "s1_assembly.npz").write_bytes(b"a staged assembly")
        with mock.patch.object(mc, "_load_world", lambda a: world), mock.patch.object(mc, "N1_BOUND", bound), \
                mock.patch.object(mc, "_single", self.single_with_consistent_denominators), \
                mock.patch.object(mc.fs, "load_s1", lambda p: s1), \
                mock.patch.object(mc.sa, "fine_map", lambda p: None), \
                mock.patch.object(mc.sa, "functional_matrix", lambda fm: self.U), \
                mock.patch.object(mc.fs, "reported_matrix", lambda s: np.eye(sa.N_CELLS) * 0.01), \
                mock.patch.object(mc, "declared_draws", lambda fp, g: [mc.draw_universes(toys.draw_for_seed(
                    sd, fp, g)) for sd in self.seeds]), \
                mock.patch.object(mc, "TOY_SEEDS", {"g18": [self.seeds[0]], "ar23": [self.seeds[1]],
                                                    "plugin": [self.seeds[2]]}):
            res = mc.receipt(a)
        return res, labels

    def single_with_consistent_denominators(self, inputs, bkg, bank_cv, tag, w, flux):
        return Receipt._real_single(inputs, bkg, bank_cv, tag, self.consistent(tag, w), flux)

    def test_counts_exact_pass_n_clip_and_verdict(self):
        wt = np.array(self.inputs["w_truth"], float)
        wt[100:110] = 0.0
        inputs = dict(self.inputs, w_truth=wt)
        res, _ = self.run_receipt(inputs)
        raw = inv.universe_weights(self.w.bank, "MaRES_0", "keep")["wt"]
        ratio = np.where(wt != 0, np.abs(raw / np.where(wt != 0, wt, 1.0)), 0.0)
        rec = res["universes"]["MaRES_0"]["wt"]
        self.assertEqual(rec["cv_zero_u_nonzero"], 10)
        self.assertAlmostEqual(rec["max_abs_ratio"], float(ratio.max()), places=12)
        self.assertEqual(rec["rows_ratio_above_bound"], int(np.sum(ratio > 1.05)))
        self.assertGreater(rec["rows_ratio_above_bound"], 0)
        # the exact pass against compose's own per-draw record, summed over the declared draws
        flux_p = mc.via_noatime(toys.flux_probabilities, self.w.constraint)
        groups = toys.interaction_groups(self.w.bank)
        want = {"wt": 0, "wr": 0, "bkgw": 0}
        negs = dict(want)
        neg = []
        with mock.patch.object(mc, "N1_BOUND", 1.05), mock.patch.object(mc, "_single", self.single_with_consistent_denominators):
            for sd in self.seeds:
                tags = mc.draw_universes(toys.draw_for_seed(sd, flux_p, groups))
                ui, ub, info = mc.compose(inputs, self.bkg, self.bank_cv, tags, self.weights, self.flux, np.ones(50))
                for k in want:
                    want[k] += info["n1"][k]["rows_above_bound"]
                    negs[k] += info["n1"][k]["rows_negative_where_cv_positive"]
                _, _, clip = mc.clip_draw(ui, ub, np.ones(wt.size))
                neg.append(abs(clip["record"]["signal"]["sum_negative"]) + abs(clip["record"]["background"]["sum_negative"]))
        for k, v in want.items():
            self.assertEqual(res["exact"][k]["pairs_above"], v, k)
            self.assertEqual(res["exact"][k]["negative_composite"]["pairs"], negs[k], k)
        self.assertGreater(sum(want.values()), 0)
        self.assertEqual(res["verdict"], "STOP")
        for k, v in want.items():                                # each source of the STOP is named
            self.assertEqual(any(r.startswith(f"N1: {k} ") for r in res["stop_reasons"]), v > 0, k)
        self.assertGreater(res["denominator"]["n1"]["pairs_above"], 0)
        self.assertTrue(any(r.startswith("N1: denom") for r in res["stop_reasons"]))
        self.assertTrue(all(v["agrees"] for v in res["validation"].values()))
        self.assertEqual(res["n_clip"]["draw_index"], int(np.argmax(neg)) if max(neg) > 0 else 0)
        self.assertEqual(res["denominator"]["draws_with_nonpositive_cells"], [])
        self.assertEqual(len(res["crossterm"]["reco_proxy_U_mapped"]["max_abs"]), sa.N_CELLS)
        # cov2d C1's source split, against a direct count over every universe
        lo = None
        with mock.patch.object(mc, "_single", self.single_with_consistent_denominators):
            for tg in toys.s1_universes():
                wr = mc._single(inputs, self.bkg, self.bank_cv, tg, self.weights(tg), self.flux)[0]["wr"]
                lo = wr.copy() if lo is None else np.minimum(lo, wr)
        cvr = np.asarray(inputs["w_reco"], float)
        sp = res["clipping_c1"]["source_split"]["wr"]
        self.assertEqual(sp["rows_with_a_universe_le_0"], int(np.sum((lo <= 0) & (cvr > 0))))
        self.assertEqual(sp["negative_in_some_draw_with_a_universe_le_0"] + sp["negative_in_some_draw_composite_only"],
                         res["exact"]["wr"]["negative_composite"]["rows_in_some_draw"])
        self.assertEqual(len(res["clipping_c1"]["clipped_rows_truth_xsec_over_sigma_c"]["max"]), sa.N_CELLS)
        self.assertIn("n1", res["denominator"])

    def test_a_2b_draw_stops_and_n_clip_counts_the_background(self):
        """Section 2b's STOP on a completed receipt, and N_clip's rule over signal plus background: one universe's
        denominator made non-positive in a cell, and one draw's background made negative."""
        flux_p = mc.via_noatime(toys.flux_probabilities, self.w.constraint)
        groups = toys.interaction_groups(self.w.bank)
        tags = [mc.draw_universes(toys.draw_for_seed(sd, flux_p, groups)) for sd in self.seeds]
        only2 = next(t for t in tags[2] if t not in tags[0] and t not in tags[1] and not t.startswith("Flux_"))
        only1 = next(t for t in tags[1] if t not in tags[0] and t not in tags[2] and not t.startswith("Flux_"))
        row = int(np.flatnonzero(np.asarray(self.inputs["pass_reco"], bool))[0])
        zrow = int(np.flatnonzero(np.asarray(self.inputs["pass_reco"], bool) & (np.asarray(self.inputs["w_reco"]) > 0))[1])
        cv = np.asarray(self.inputs["denom_nd"], float)
        c = tuple(np.argwhere(cv > 0)[0])
        real = self.single_with_consistent_denominators

        def hooked(inputs, bkg, bank_cv, tag, w, flux):
            single, phi = real(inputs, bkg, bank_cv, tag, w, flux)
            if tag == only1:                                             # draw 1: a large negative signal mass
                wr = single["wr"].copy()
                wr[row] = -1e3
                wr[zrow] = 0.0                                           # and one universe weight exactly 0
                single = dict(single, wr=wr)
            if tag == only2:                                             # draw 2: a larger negative background mass
                bw = -np.abs(single["bkgw"])
                bw[0] = -1e6
                single = dict(single, bkgw=bw)
                d = single["denom"].copy()
                d[c] = -1e6                                              # draw 2's composite denominator < 0
                single["denom"] = d
            return single, phi
        self.single_with_consistent_denominators = hooked
        res, _ = self.run_receipt(self.inputs, bound=1e9)
        want = []                                                       # compose's own section 2b, draw by draw
        with mock.patch.object(mc, "_single", hooked):
            for d, tg in enumerate(tags):
                try:
                    mc.compose(self.inputs, self.bkg, self.bank_cv, tg, self.weights, self.flux, np.ones(50))
                except mc.Refusal as e:
                    self.assertIn("section 2b", str(e))
                    want.append(d)
        self.assertIn(2, want)
        self.assertEqual(res["denominator"]["draws_with_nonpositive_cells"], want)
        self.assertEqual(res["verdict"], "STOP")
        self.assertTrue(any(r.startswith("2b:") for r in res["stop_reasons"]))
        self.assertEqual(res["n_clip"]["draw_index"], 2)          # signal alone would pick draw 1
        lo = None
        with mock.patch.object(mc, "_single", hooked):
            for tg in toys.s1_universes():
                wr = mc._single(self.inputs, self.bkg, self.bank_cv, tg, self.weights(tg), self.flux)[0]["wr"]
                lo = wr.copy() if lo is None else np.minimum(lo, wr)
        cvr = np.asarray(self.inputs["w_reco"], float)
        self.assertEqual(lo[zrow], 0.0)
        self.assertEqual(res["clipping_c1"]["source_split"]["wr"]["rows_with_a_universe_le_0"],
                         int(np.sum((lo <= 0) & (cvr > 0))))
        self.assertGreater(res["exact"]["wr"]["negative_composite"]["rows_in_some_draw"], 0)
        self.assertEqual(res["n_clip"]["seed"], self.seeds[2])

    def test_declared_draws_are_all_three_truths_seeds(self):
        flux_p = mc.via_noatime(toys.flux_probabilities, self.w.constraint)
        groups = toys.interaction_groups(self.w.bank)
        got = mc.declared_draws(flux_p, groups)
        self.assertEqual(len(got), 900)
        for k, seed in ((0, 3620000), (299, 3620299), (300, 3630000), (599, 3630299), (600, 3640000), (899, 3640299)):
            self.assertEqual(got[k], mc.draw_universes(toys.draw_for_seed(seed, flux_p, groups)), seed)

    def test_the_loader_zeroes_non_finite_values_as_s1_does(self):
        tmp = Path(tempfile.mkdtemp(prefix="fd1b-mc-ld-"))
        self.addCleanup(shutil.rmtree, tmp)
        pins = {"files": {}}
        for k in ("wt", "wr", "tdw", "bkgw"):
            a = np.load(self.w.bank / f"MaRES_0_{k}.npy")
            if k == "wt":
                a = a.copy()
                a[[1, 4]] = [np.nan, np.inf]
            np.save(tmp / f"MaRES_0_{k}.npy", a)
            pins["files"][str(tmp / f"MaRES_0_{k}.npy")] = {"sha256": digest(tmp / f"MaRES_0_{k}.npy")}
        keep, zero = mc.verified_weights({"pins": pins}, argparse.Namespace(bank=tmp, detector_dir=tmp), "MaRES_0")
        self.assertTrue(np.isnan(keep["wt"][1]) and np.isinf(keep["wt"][4]))
        self.assertEqual((zero["wt"][1], zero["wt"][4]), (0.0, 0.0))
        np.testing.assert_array_equal(zero["wt"], inv.universe_weights(tmp, "MaRES_0", "zero")["wt"])

    def test_pass_when_nothing_is_above(self):
        res, _ = self.run_receipt(self.inputs, bound=1e9)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["stop_reasons"], [])

    def test_the_loader_reads_each_file_once_and_hashes_those_bytes(self):
        world = {"pins": json.loads(self.w.pins.read_text())}
        a = argparse.Namespace(bank=self.w.bank, detector_dir=self.w.det)
        opened = []
        real = inv.open_noatime

        def counting(p):
            opened.append(str(p))
            return real(p)
        for tag in ("MaRES_0", "GEANT_Pion_1"):
            opened.clear()
            with mock.patch.object(inv, "open_noatime", counting):
                keep, zero = mc.verified_weights(world, a, tag)
            self.assertEqual(sorted(opened), sorted(set(opened)), "a file was opened twice")
            self.assertEqual(len(opened), 4)
            ref_k = inv.universe_weights(mc.universe_dir(tag, self.w.bank, self.w.det), tag, "keep")
            ref_z = inv.universe_weights(mc.universe_dir(tag, self.w.bank, self.w.det), tag, "zero")
            for k in ref_k:
                np.testing.assert_array_equal(keep[k], ref_k[k])
                np.testing.assert_array_equal(zero[k], ref_z[k])
        pins = json.loads(self.w.pins.read_text())
        p = next(k for k in pins["files"] if k.endswith("MaRES_0_wr.npy"))
        pins["files"][p] = dict(pins["files"][p], sha256="0" * 64)
        with self.assertRaisesRegex(mc.Refusal, "not the pinned file"):
            mc.verified_weights({"pins": pins}, a, "MaRES_0")


Receipt._real_single = staticmethod(mc._single)


class Loaders(Jobs):
    """The digest and finiteness refusals on the job path."""

    def test_input_and_flux_table_digests(self):
        out = self.tmp / "ld1"
        with mock.patch.object(sa, "INPUT_NPZ_SHA256", "0" * 64):
            self.assertEqual(mc.main(self.argv("g18", "central", "T", out)), 4)
        table = self.tmp / "flux-table.npz"
        np.savez(table, hFluxCV=np.ones(2), hFluxUniv=np.ones((100, 2)))
        a = argparse.Namespace(npz=self.w.inputs, bkg=self.w.bkg, pins=self.w.pins, bank=self.w.bank,
                               detector_dir=self.w.det, expect_pins_sha256=digest(self.w.pins), flux_table=table,
                               expect_flux_table_sha256="0" * 64)
        with self.assertRaisesRegex(mc.Refusal, "flux table's digest"):
            mc._load_world(a)

    def test_weight_pins_and_push_digest(self):
        pins = json.loads(self.w.pins.read_text())
        p = next(k for k in pins["files"] if k.endswith("MaRES_0_wt.npy"))
        pins["files"][p] = dict(pins["files"][p], sha256="0" * 64)
        a = argparse.Namespace(bank=self.w.bank, detector_dir=self.w.det)
        with self.assertRaises(mc.Refusal):
            mc._weights({"pins": pins}, a, "MaRES_0")
        push = self.tmp / "push.npz"
        np.savez(push, push=np.ones(3))
        a = argparse.Namespace(truth="plugin", prep=None, push=push, expect_push_sha256="0" * 64)
        with self.assertRaisesRegex(mc.Refusal, "declared digest"):
            mc.run_item(a, {"inputs": self.inputs, "bkg": self.bkg}, "central", "T")

    def test_a_non_finite_toy_truth(self):
        a = argparse.Namespace(truth="g18", prep=self.w.prep, push=None, flux_constraint=self.w.constraint,
                               threads=1, clip_rule="data")
        world = {"inputs": self.inputs, "bkg": self.bkg, "bank_cv": self.bank_cv, "flux": self.flux,
                 "groups": toys.interaction_groups(self.w.bank)}
        with mock.patch.object(mc, "compose", lambda *x: (self.inputs, self.bkg, {})), \
                mock.patch.object(mc, "truth_weight", lambda *x: None), \
                mock.patch.object(mc, "toy_experiment", lambda *x: ({}, np.array([1.0, np.nan]), {})), \
                self.assertRaisesRegex(mc.Refusal, "non-finite truth"):
            mc.run_item(a, world, "toy", "3620000")


class Walls(unittest.TestCase):
    def test_the_pilot_without_the_plugin_has_no_capture(self):
        self.assertNotIn(("capture", "data"), mc.PILOT[False])
        self.assertIn(("toy", "ar23:3630000"), mc.PILOT[False])
        self.assertEqual(len(mc.PILOT[False]), 8)
        self.assertEqual(len(mc.PILOT[True]), 8)

    def test_pass_and_reprice(self):
        tmp = Path(tempfile.mkdtemp(prefix="fd1b-mc-w-"))
        try:
            for role, item in mc.PILOT[True]:
                truth = "data" if role in ("control", "capture") else item.split(":")[0]
                it = "T" if role == "central" else (item.split(":", 1)[1] if ":" in item else item)
                np.savez(tmp / mc.product_name("t", truth, role, it), xsec_flat=np.zeros(2),
                         meta=json.dumps({"seconds_unfold": 900.0, "peak_rss_kib": 1000}))
            self.assertEqual(mc.pilot_walls(tmp, "t", True)["verdict"], "PASS")
            np.savez(tmp / mc.product_name("t", "data", "capture", "data"), xsec_flat=np.zeros(2),
                     meta=json.dumps({"seconds_unfold": 1100.0, "peak_rss_kib": 1000}))
            self.assertEqual(mc.pilot_walls(tmp, "t", True)["verdict"], "REPRICE")
            (tmp / mc.product_name("t", "g18", "central", "T")).unlink()
            self.assertEqual(mc.pilot_walls(tmp, "t", True)["verdict"], "REPRICE")
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
