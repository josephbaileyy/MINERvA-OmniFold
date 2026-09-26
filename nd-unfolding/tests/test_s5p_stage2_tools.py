"""Controls for the s5p Stage-2 tools (no LightGBM or ROOT: stub estimators and a stub refinement).

s5p_numerics must reproduce the production negweight-refined path exactly when nothing is perturbed,
keep every jittered coordinate within half a float32 ulp without moving any row across a grid edge, and
make a capacity override reach the estimators. s5p_converge must add the H2 rows and the late snapshots
without changing anything else."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
sys.path.insert(1, str(Path(__file__).resolve().parent))
import omnifold_nn_core as onc  # noqa: E402
import s5c_coverage  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_trace  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_converge  # noqa: E402
import s5p_numerics as sn  # noqa: E402
from test_s5e_trace import EDGES, StubClf, StubReg, stub_factory, toy_inputs  # noqa: E402


def stub_refine(feat, signed_w, params):
    """Deterministic stand-in with refine_stay_positive's return signature."""
    g = np.clip(0.5 + 0.01 * np.tanh(feat[:, 0]), 0.0, 1.0)
    w = np.clip(np.abs(signed_w) * (2 * g - 1), 0.0, None) * (signed_w > 0) + 1e-6
    return w, g, 0.0


def toy_experiment(n=6000, seed=0):
    inputs = toy_inputs(n, seed)
    rng = np.random.default_rng(seed + 1)
    data = inputs["MCreco"][inputs["pass_reco"]][: n // 3]
    tmpl = inputs["MCreco"][inputs["pass_reco"]][n // 3: n // 3 + 400]
    return {**{k: inputs[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco",
                                      "denom_nd", "flux", "data_pot", "n_nucleons", "edges")},
            "obs": data, "obs_counts": np.ones(data.shape[0]), "tmpl": tmpl,
            "tmpl_w": rng.uniform(0.05, 0.1, tmpl.shape[0])}


class Stubbed(unittest.TestCase):
    def setUp(self):
        self.orig_make, self.orig_refine = onc.make_estimators, s5n_pseudo.refine
        onc.make_estimators = stub_factory
        original_refine = self.orig_refine

        def refine(feat, signed_w, estimator_seed, threads, refine_fn=None):
            return original_refine(feat, signed_w, estimator_seed, threads, refine_fn=stub_refine)

        s5n_pseudo.refine = refine

    def tearDown(self):
        onc.make_estimators, s5n_pseudo.refine = self.orig_make, self.orig_refine


class NumericsTests(Stubbed):
    def test_unperturbed_float32_path_is_the_production_path_bitwise(self):
        exp = toy_experiment()
        xs_prod, _ = s5n_pseudo.unfold_negweight(exp, 42, 1, 3)
        xs, ev = sn.unfold_one(exp, np.float32, 42, 1, 3)
        np.testing.assert_array_equal(xs, xs_prod)
        self.assertTrue(ev["refinement"]["ran"])

    def test_float64_upcast_without_jitter_changes_nothing_here(self):
        exp = toy_experiment()
        up = dict(exp)
        for k in ("MCgen", "MCreco", "obs", "tmpl"):
            up[k] = np.asarray(exp[k], np.float32).astype(np.float64)
        np.testing.assert_array_equal(sn.unfold_one(exp, np.float32, 42, 1, 3)[0],
                                      sn.unfold_one(up, np.float64, 42, 1, 3)[0])

    def test_capacity_override_reaches_every_estimator_and_is_restored(self):
        exp = toy_experiment()
        with sn.omnifold_capacity((400, 31)):
            _, ev = sn.unfold_one(exp, np.float32, 42, 1, 3)
        for p in ev["estimator_params"]:
            self.assertEqual((p["n_estimators"], p["num_leaves"]), (400, 31))
        self.assertNotIn("n_estimators", s5c_unfold.config_params("deterministic", 1))

    def test_capacity_that_does_not_reach_the_estimators_is_refused(self):
        class Deaf(StubClf):
            def set_params(self, **kw):
                return self  # swallows the override

        class DeafReg(StubReg):
            def set_params(self, **kw):
                return self

        onc.make_estimators = lambda kind, nvars, seed=None: (Deaf(seed), Deaf(seed), DeafReg(seed))
        with sn.omnifold_capacity((400, 31)), self.assertRaises(RuntimeError):
            sn.unfold_one(toy_experiment(), np.float32, 42, 1, 3)


class JitterTests(unittest.TestCase):
    def test_jitter_is_sub_ulp_edge_safe_and_keeps_membership(self):
        inputs = toy_inputs(20000, 3)
        on_edge = np.float32(EDGES[2][1])
        inputs["MCgen"][:50, 2] = on_edge  # rows sitting exactly on a grid edge
        bkg = {"bkg_reco": inputs["MCreco"][:500].copy(), "bkg_w": np.ones(500), "bkg_nd": None}
        inputs["measured"] = inputs["MCreco"][:3000].copy()
        ji, jb = sn.jittered(inputs, bkg, 7)
        for k in sn.COORD_KEYS:
            x32 = np.asarray(inputs[k], np.float32)
            ulp = np.spacing(np.abs(x32)).astype(np.float64)
            d = np.abs(ji[k] - x32.astype(np.float64))
            self.assertTrue(np.all(d <= 0.5 * ulp))
            self.assertGreater(int((d > 0).sum()), 0)
        self.assertTrue(np.all(ji["MCgen"][:50, 2] == np.float64(on_edge)))
        base = sn.cell_membership(inputs, bkg["bkg_reco"])
        moved = sn.cell_membership(ji, jb["bkg_reco"])
        for k in base:
            np.testing.assert_array_equal(base[k], moved[k])

    def test_pairs_parse_and_refuse_duplicates(self):
        self.assertEqual(sn.parse_pairs("-:-,1:-,1:101"), [(None, None), (1, None), (1, 101)])
        with self.assertRaises(ValueError):
            sn.parse_pairs("1:2,1:2")
        self.assertEqual(sn.product_name("d", None, 3), "d_b-_j3.npz")
        self.assertEqual(sn.product_name("n", 5001, None, 930000), "n_s930000_b5001_j-.npz")


class ConvergeTests(unittest.TestCase):
    def test_h2_rows_partition_the_fine_grid_by_volume(self):
        H, names = s5p_converge.h2_rows()
        self.assertEqual(H.shape[0], 32)
        self.assertEqual(len(names), 32)
        covered = (H > 0).sum(axis=0)
        self.assertTrue(np.all(covered == 1))  # each fine cell in exactly one H2 cell

    def test_install_appends_h2_and_late_snapshots_only(self):
        contract = {"measurement": {"partition_J": {"edges": {"pt": [0.0, 0.55, 0.85, 4.5],
                    "pz": [1.5, 3.5, 6.0, 60.0], "eavail": [0.0, 0.4, 1.5, 100.0], "q3": [0.0, 1.2, 2.0, 100.0],
                    "W": [0.0, 1.4, 2.2, 100.0]}, "supported_cells": [0, 1, 4]}}}
        U0, n0 = s5c_coverage.reported_functionals(contract)
        saved = (s5c_coverage.reported_functionals, s5e_trace.Recorder.__init__.__defaults__, s5n_pseudo.code_digests)
        try:
            s5p_converge.install()
            U1, n1 = s5c_coverage.reported_functionals(contract)
            np.testing.assert_array_equal(U1[: U0.shape[0]], U0)
            self.assertEqual(n1[: len(n0)], n0)
            self.assertEqual(U1.shape[0], U0.shape[0] + 32)
            snaps = s5e_trace.Recorder.__init__.__defaults__[-1]
            self.assertIn(200, snaps)
            self.assertTrue(set(s5e_trace.SNAPSHOTS) <= set(snaps))
        finally:
            s5c_coverage.reported_functionals = saved[0]
            s5e_trace.Recorder.__init__.__defaults__ = saved[1]
            s5n_pseudo.code_digests = saved[2]


if __name__ == "__main__":
    unittest.main()
