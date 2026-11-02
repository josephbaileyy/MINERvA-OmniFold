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
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(Path(__file__).resolve().parent))

import fd_1b_inv as inv  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_null as fn  # noqa: E402
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
        return inv.universe_weights(mc.universe_dir(tag, self.w.bank, self.w.det), tag, "zero")


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

    def test_two_universes_multiply_ratios_and_add_on_zero_cv_rows(self):
        a, b = self.weights("MaRES_0"), self.weights("LowQ2_1")
        inputs = dict(self.inputs)
        wt = np.asarray(inputs["w_truth"], float).copy()
        wt[[30, 31]] = 0.0                                 # CV = 0 rows
        wt[32] = -0.5                                      # a negative CV row
        inputs["w_truth"] = wt
        a = dict(a, wt=a["wt"].copy())
        b = dict(b, wt=b["wt"].copy())
        a["wt"][30], b["wt"][30] = 0.25, 0.5               # CV = 0, universes non-zero: added
        a["wt"][33], b["wt"][33] = -0.2, 1.0               # a negative universe weight: kept
        ui, _, info = mc.compose(inputs, self.bkg, self.bank_cv, ["MaRES_0", "LowQ2_1"], {"MaRES_0": a, "LowQ2_1": b}.get, None)
        got = np.asarray(ui["w_truth"], float)
        self.assertEqual(got[30], 0.75)
        self.assertEqual(got[31], a["wt"][31] + b["wt"][31])
        self.assertAlmostEqual(got[32], a["wt"][32] * b["wt"][32] / -0.5, places=14)
        self.assertAlmostEqual(got[33], -0.2 * 1.0 / wt[33], places=14)
        self.assertLess(got[33], 0.0)
        k = 40
        self.assertAlmostEqual(got[k], a["wt"][k] * b["wt"][k] / wt[k], places=14)
        self.assertIn("n1", info)
        self.assertGreaterEqual(info["n1"]["wt"]["max_composite_over_max_single"], 0.0)

    def test_denominators_compose_per_cell(self):
        a, b = self.weights("MaRES_0"), self.weights("GEANT_Pion_0")
        ui, _, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, ["MaRES_0", "GEANT_Pion_0"], {"MaRES_0": a, "GEANT_Pion_0": b}.get, None)
        da = s5p_universe.universe_inputs(self.inputs, self.bkg, self.bank_cv, a, "MaRES", "0", None)[0]["denom_nd"]
        db = np.asarray(b["denom_nd"], float)
        cv = np.asarray(self.inputs["denom_nd"], float)
        np.testing.assert_allclose(ui["denom_nd"], da * db / cv, rtol=1e-14)

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
            mc.compose(self.inputs, self.bkg, self.bank_cv, ["Flux_1", "Flux_2"], self.weights, self.flux)

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


class Experiments(Case):
    def test_with_mc_sets_the_unfolding_flux(self):
        exp, _ = mc.mean_experiment(self.inputs, self.bkg, np.ones(self.inputs["w_truth"].shape[0]))
        ui, ub, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, ["Flux_3"], self.weights, self.flux)
        np.testing.assert_array_equal(mc.with_mc(exp, ui, ub)["flux"], self.flux[3])
        np.testing.assert_array_equal(mc.with_mc(exp, self.inputs, self.bkg)["flux"], self.inputs["flux"])

    def test_toy_unfolds_with_the_nominal_mc_and_keeps_natures_truth(self):
        tags = ["Flux_3", "MaRES_0"]
        ui, ub, _ = mc.compose(self.inputs, self.bkg, self.bank_cv, tags, self.weights, self.flux)
        r = np.ones(self.inputs["w_truth"].shape[0])
        exp, x_true = mc.toy_experiment(self.inputs, self.bkg, ui, ub, r, 3_620_000)
        np.testing.assert_array_equal(exp["flux"], self.inputs["flux"])
        ref = toys.build_full(ui, ub, r, np.ones(r.size), np.ones(ub["bkg_w"].size), 3_620_000, False)[1]
        np.testing.assert_array_equal(x_true, ref)
        nom = toys.build_full(self.inputs, self.bkg, r, np.ones(r.size), np.ones(ub["bkg_w"].size), 3_620_000, False)[1]
        self.assertFalse(np.array_equal(x_true, nom))

    def test_toy_carries_set_As_mc_and_template_streams(self):
        r = np.ones(self.inputs["w_truth"].shape[0])
        exp, _ = mc.toy_experiment(self.inputs, self.bkg, self.inputs, self.bkg, r, 3_620_001)
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
        mine = mc.stat_experiment(self.inputs, self.bkg, None, None, 1)
        ji, jb = s5p_numerics.jittered(self.inputs, self.bkg, 101)
        ref = s5n_pseudo.bootstrap_replica(s5n_pseudo.build_data(ji, jb), 1)
        for k in ("obs", "obs_counts", "w_truth", "w_reco", "tmpl_w"):
            np.testing.assert_array_equal(mine[k], ref[k], k)

    def test_stat_replicas_share_one_realization(self):
        r = np.ones(self.inputs["w_truth"].shape[0])
        e1 = mc.stat_experiment(self.inputs, self.bkg, r, 3_621_000, 1)
        e2 = mc.stat_experiment(self.inputs, self.bkg, r, 3_621_000, 2)
        base = toys.build_full(self.inputs, self.bkg, r, np.ones(r.size), np.ones(self.bkg["bkg_w"].size), 3_621_000, False)[0]
        self.assertEqual(e1["obs_counts"].size, base["obs_counts"].size)
        self.assertFalse(np.array_equal(e1["obs_counts"], e2["obs_counts"]))


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
                "--out", str(out)]

    def test_control_and_capture_only_on_the_data(self):
        out = self.tmp / "jobs1"
        self.assertEqual(mc.main(self.argv("g18", "control", "MaRES_0", out)), 4)
        self.assertEqual(mc.main(self.argv("data", "central", "T", out)), 4)

    def test_declared_ranges(self):
        a = mock.Mock(truth="g18", prep=self.w.prep, push=None, expect_push_sha256=None, threads=1,
                      flux_constraint=self.w.constraint, bank=self.w.bank, detector_dir=self.w.det)
        world = {"inputs": self.inputs, "bkg": self.bkg, "bank_cv": self.bank_cv, "flux": self.flux,
                 "groups": toys.interaction_groups(self.w.bank), "pins": {}}
        with self.assertRaises(mc.Refusal):
            mc.run_item(a, world, "toy", "3630000", unfold_fn=lambda *x: (np.zeros(3), {}))
        with self.assertRaises(mc.Refusal):
            mc.run_item(a, world, "stat", "51", unfold_fn=lambda *x: (np.zeros(3), {}))
        with self.assertRaises(mc.Refusal):
            mc.run_item(mock.Mock(truth="data"), world, "control", "LowQ2_1", unfold_fn=lambda *x: (np.zeros(3), {}))

    def test_central_and_seed_products(self):
        out = self.tmp / "jobs2"
        calls = []

        def fake(exp, threads, seed=42, unfold_fn=None):
            calls.append(seed)
            return np.asarray(exp["obs_counts"].sum() * np.ones(4)), {"seen_seed": seed}
        with mock.patch.object(mc, "_unfold_s1", fake):
            for role in ("central", "seed"):
                self.assertEqual(mc.main(self.argv("g18", role, "T", out)), 0)
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
        a = argparse.Namespace(staged=self.tmp)
        with mock.patch.object(mc.fs, "load_s1", reader), self.assertRaises(_Stop):
            mc.null_step(a)
        self.assert_noatime_only(self.s1, got)

    def test_readout_reads_the_assembly_through_o_noatime(self):
        got, reader = self.spy()
        null = self.tmp / "null.json"
        null.write_text(json.dumps({"products_sha256": "p"}))
        a = argparse.Namespace(staged=self.tmp, null=null, expect_null_sha256=digest(null), unfolds=self.tmp,
                               tag="t", truth="g18")
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

    def test_the_copy_gives_the_bound_readers_answer(self):
        want = digest(self.constraint)
        self.plain.clear()
        with mock.patch.object(sa, "CONSTRAINT_SHA256", want):
            w = mc.via_noatime(sa.flux_weights, self.constraint)
            self.assertNotIn(str(self.constraint), self.plain)
            np.testing.assert_array_equal(w, sa.flux_weights(self.constraint))


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
