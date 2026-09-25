"""Controls for the s5n successor's experiment construction and resampling (no LightGBM or ROOT).

Each guard is tested in the direction it acts (fires on the defect) and on its innocent neighbour."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5c_pseudo  # noqa: E402
import s5n_pseudo  # noqa: E402

EDGES = [np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 2.0]), np.array([0.0, 0.1, 0.4, 5.0]),
         np.array([0.0, 1.0, 3.0]), np.array([0.0, 1.5, 9.0])]


def toy_inputs(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    gen = np.column_stack([rng.uniform(0, 2, n), rng.uniform(0, 2, n), rng.uniform(0, 5, n),
                           rng.uniform(0, 3, n), rng.uniform(0, 9, n)]).astype(np.float32)
    gen[:25, 3] = -9999.0  # sentinels, as in the real sample
    reco = (gen + rng.normal(0, 0.05, gen.shape)).astype(np.float32)
    reco[:25, 3] = -9999.0
    pass_truth = np.ones(n, bool)
    pass_truth[-100:] = False
    pass_reco = rng.uniform(size=n) < 0.8
    w = rng.uniform(0.1, 0.3, n)
    shape = tuple(len(e) - 1 for e in EDGES)
    return {"MCgen": gen, "MCreco": reco, "pass_reco": pass_reco, "pass_truth": pass_truth,
            "w_truth": w, "w_reco": w * rng.uniform(0.9, 1.1, n), "measured": reco[:500].copy(),
            "measured_weights": np.ones(500), "denom_nd": np.full(shape, 50.0), "flux": np.ones(2),
            "data_pot": 1.0, "n_nucleons": 1.0, "edges": EDGES}


def toy_bkg(n=600, seed=1):
    rng = np.random.default_rng(seed)
    reco = np.column_stack([rng.uniform(0, 2.2, n), rng.uniform(0, 2, n), rng.uniform(0, 5, n),
                            rng.uniform(0, 3, n), rng.uniform(0, 9, n)]).astype(np.float32)
    bw = rng.uniform(0.05, 0.4, n)
    nd, _ = np.histogramdd(reco, bins=EDGES, weights=bw)
    return {"bkg_reco": reco, "bkg_w": bw, "bkg_nd": nd}


class FidMask(unittest.TestCase):
    def test_half_open_window_on_every_axis(self):
        c = np.array([[0.0, 0.0, 0.0, 0.0, 0.0], [2.0, 1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, -1.0, 1.0],
                      [1.9999, 1.9999, 4.9999, 2.9999, 8.9999]])
        np.testing.assert_array_equal(s5n_pseudo.fid_mask(c, EDGES), [True, False, False, True])


class EavailShape(unittest.TestCase):
    def setUp(self):
        self.inp = toy_inputs()
        self.ratio = {"eavail_edges": EDGES[2].tolist(), "shape_ratio": [1.3, 0.9, 0.8]}

    def test_preserves_in_grid_total_and_leaves_outside_rows_alone(self):
        r = s5n_pseudo.eavail_ratio_weight(self.inp["MCgen"], EDGES, self.inp["w_truth"], self.ratio, 1.0)
        gen = self.inp["MCgen"]
        ok = np.all([(gen[:, k] >= e[0]) & (gen[:, k] <= e[-1]) for k, e in enumerate(EDGES)], axis=0)
        self.assertFalse(ok[:25].any())
        np.testing.assert_array_equal(r[~ok], 1.0)
        w = self.inp["w_truth"]
        self.assertAlmostEqual((w[ok] * r[ok]).sum() / w[ok].sum(), 1.0, places=12)

    def test_is_the_declared_shape_up_to_one_constant(self):
        r = s5n_pseudo.eavail_ratio_weight(self.inp["MCgen"], EDGES, self.inp["w_truth"], self.ratio, 1.0)
        gen = self.inp["MCgen"]
        ok = r != 1.0
        ie = np.searchsorted(EDGES[2], gen[ok, 2], side="right") - 1
        const = r[ok] / np.asarray(self.ratio["shape_ratio"])[ie]
        self.assertLess(np.ptp(const), 1e-12)

    def test_amplitude_zero_is_nominal_and_wrong_edges_refused(self):
        r = s5n_pseudo.eavail_ratio_weight(self.inp["MCgen"], EDGES, self.inp["w_truth"], self.ratio, 0.0)
        np.testing.assert_allclose(r, 1.0)
        bad = dict(self.ratio, eavail_edges=[0.0, 0.2, 0.4, 5.0])
        with self.assertRaises(ValueError):
            s5n_pseudo.eavail_ratio_weight(self.inp["MCgen"], EDGES, self.inp["w_truth"], bad, 1.0)


class BuildPseudo(unittest.TestCase):
    def setUp(self):
        self.inp, self.bkg = toy_inputs(), toy_bkg()

    def test_signal_split_and_truth_equal_the_s5c_construction(self):
        exp, xt, info = s5n_pseudo.build_pseudo(self.inp, self.bkg, "nominal", 0.0, 77, 5)
        _, xt_c, _ = s5c_pseudo.build_experiment(self.inp, self.bkg, "nominal", 0.0, 77, 5)
        np.testing.assert_array_equal(xt, xt_c)
        is_b = s5c_pseudo.half_mask(self.inp["MCgen"].shape[0], 77)
        np.testing.assert_array_equal(exp["w_truth"], 2.0 * self.inp["w_truth"][~is_b])

    def test_template_is_the_other_background_half_at_twice_its_weight(self):
        exp, _, info = s5n_pseudo.build_pseudo(self.inp, self.bkg, "nominal", 0.0, 77, 5)
        is_c = s5c_pseudo.half_mask(self.bkg["bkg_w"].shape[0], s5n_pseudo.bkg_split_key(77))
        tkeep = s5n_pseudo.fid_mask(self.bkg["bkg_reco"][~is_c], EDGES)
        np.testing.assert_array_equal(exp["tmpl_w"], 2.0 * self.bkg["bkg_w"][~is_c][tkeep])
        self.assertLess(tkeep.mean(), 1.0)  # the toy background spills over the pt window
        self.assertTrue(np.all(s5n_pseudo.fid_mask(exp["obs"], EDGES)))
        self.assertTrue(np.all(s5n_pseudo.fid_mask(exp["tmpl"], EDGES)))

    def test_background_split_is_independent_of_the_signal_split(self):
        n = 200_000
        a = s5c_pseudo.half_mask(n, 77)
        c = s5c_pseudo.half_mask(n, s5n_pseudo.bkg_split_key(77))
        self.assertLess(abs((a == c).mean() - 0.5), 0.01)

    def test_seed_reproducible_and_seed_dependent(self):
        e1, _, _ = s5n_pseudo.build_pseudo(self.inp, self.bkg, "nominal", 0.0, 77, 5)
        e2, _, _ = s5n_pseudo.build_pseudo(self.inp, self.bkg, "nominal", 0.0, 77, 5)
        e3, _, _ = s5n_pseudo.build_pseudo(self.inp, self.bkg, "nominal", 0.0, 77, 6)
        np.testing.assert_array_equal(e1["obs_counts"], e2["obs_counts"])
        self.assertFalse(np.array_equal(e1["obs_counts"], e3["obs_counts"][: e1["obs_counts"].size])
                         and e1["obs_counts"].size == e3["obs_counts"].size)

    def test_no_background_reference_has_no_template_and_no_background_events(self):
        exp, _, info = s5n_pseudo.build_pseudo(self.inp, self.bkg, "nominal", 0.0, 77, 5, no_background=True)
        self.assertEqual(exp["tmpl"].shape[0], 0)
        self.assertEqual(info["pseudo_background_events"], 0.0)

    def test_expected_counts_have_the_split_normalization(self):
        tot = np.zeros(2)
        for s in range(40):
            exp, _, info = s5n_pseudo.build_pseudo(self.inp, self.bkg, "nominal", 0.0, 1000 + s, s)
            tot += [info["pseudo_background_events"], info["expected_background_source"]]
        self.assertLess(abs(tot[0] / tot[1] - 1.0), 0.02)


class Bootstrap(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(3)
        self.exp = {"obs": np.zeros((20000, 5), np.float32), "obs_counts": rng.integers(1, 4, 20000).astype(float),
                    "tmpl": np.zeros((5000, 5), np.float32), "tmpl_w": rng.uniform(0.1, 0.5, 5000),
                    "w_truth": np.full(8000, 0.2), "w_reco": np.full(8000, 0.3)}

    def test_count_k_rows_get_poisson_k_not_k_times_poisson_1(self):
        k = self.exp["obs_counts"]
        reps = np.array([s5n_pseudo.bootstrap_replica(self.exp, b)["obs_counts"] for b in range(1, 41)])
        for kk in (1.0, 2.0, 3.0):
            sel = k == kk
            v = reps[:, sel].var(ddof=1)
            self.assertLess(abs(v / kk - 1.0), 0.05, (kk, v))  # Poisson(k): var k; k*Poisson(1): var k^2

    def test_mc_and_template_are_resampled_on_independent_streams(self):
        rep = s5n_pseudo.bootstrap_replica(self.exp, 7)
        fm = rep["w_truth"] / self.exp["w_truth"]
        np.testing.assert_allclose(rep["w_reco"] / self.exp["w_reco"], fm, rtol=1e-12)
        ft = rep["tmpl_w"] / self.exp["tmpl_w"]
        self.assertAlmostEqual(ft.mean(), 1.0, delta=0.05)
        self.assertLess(abs(np.corrcoef(fm[:5000], ft)[0, 1]), 0.05)
        np.testing.assert_allclose(ft, np.round(ft), atol=1e-12)  # integer Poisson(1) factors

    def test_nominal_experiment_is_not_mutated(self):
        before = self.exp["obs_counts"].copy()
        s5n_pseudo.bootstrap_replica(self.exp, 9)
        np.testing.assert_array_equal(self.exp["obs_counts"], before)


class SignedSampleAndRefinement(unittest.TestCase):
    def setUp(self):
        self.exp = {"obs": np.arange(12, dtype=np.float32).reshape(4, 3), "obs_counts": np.array([1.0, 0.0, 2.0, 1.0]),
                    "tmpl": np.ones((3, 3), np.float32), "tmpl_w": np.array([0.5, 0.0, 0.25])}

    def test_signs_and_zero_rows_dropped(self):
        feat, w, no, nt = s5n_pseudo.signed_sample(self.exp)
        np.testing.assert_array_equal(w, [1.0, 2.0, 1.0, -0.5, -0.25])
        self.assertEqual((no, nt), (3, 2))
        self.assertEqual(feat.shape, (5, 3))

    @staticmethod
    def fake_refine(feat, signed_w, params):
        g = np.where(signed_w > 0, 0.9, 0.3)
        f = 2 * g - 1
        return np.abs(signed_w) * np.clip(f, 0, None), g, float((f < 0).mean())

    def test_evidence_records_normalization_clipping_and_effective_size(self):
        feat, w, _, _ = s5n_pseudo.signed_sample(self.exp)
        w_ref, ev = s5n_pseudo.refine(feat, w, 42, 4, refine_fn=self.fake_refine)
        self.assertTrue(ev["ran"])
        self.assertEqual(ev["n_negative"], 2)
        self.assertAlmostEqual(ev["signed_sum"], 3.25)
        self.assertAlmostEqual(ev["refined_sum"], 0.8 * 4.0)
        self.assertEqual(ev["n_clipped"], 2)
        self.assertAlmostEqual(ev["clipped_signed_mass"], -0.4 * 0.75)
        self.assertEqual(ev["classifier_params"]["random_state"], 45)
        self.assertTrue(ev["classifier_params"]["deterministic"])

    def test_a_refinement_without_the_f2_parameters_is_refused(self):
        import s5c_unfold

        orig = s5c_unfold.config_params
        s5c_unfold.config_params = lambda c, t: {}
        try:
            feat, w, _, _ = s5n_pseudo.signed_sample(self.exp)
            params = s5n_pseudo.refine_params(42, 4)
            self.assertNotIn("deterministic", params)
        finally:
            s5c_unfold.config_params = orig
        record = [dict(s5n_pseudo.DRIVER_CLASSIFIER_DEFAULTS, random_state=45)]  # what a bare driver builds
        want = {**s5n_pseudo.DRIVER_CLASSIFIER_DEFAULTS, **s5n_pseudo.refine_params(42, 4)}
        self.assertTrue(any(record[0].get(k) != v for k, v in want.items()))

    def test_unfold_receives_the_refined_sample_and_signal_only_skips_refinement(self):
        seen = {}

        def fake_unfold(d, config, seed, threads, iters):
            seen.update(d)
            return np.zeros(3), [{}]

        exp = dict(self.exp, MCgen=np.zeros((2, 3)), MCreco=np.zeros((2, 3)), pass_reco=np.ones(2, bool),
                   pass_truth=np.ones(2, bool), w_truth=np.ones(2), w_reco=np.ones(2), denom_nd=None,
                   flux=None, data_pot=1.0, n_nucleons=1.0, edges=None)
        _, ev = s5n_pseudo.unfold_negweight(exp, 42, 4, 5, refine_fn=self.fake_refine, unfold_fn=fake_unfold)
        np.testing.assert_allclose(seen["measured_weights"], [0.8, 1.6, 0.8, 0.0, 0.0])
        self.assertTrue(ev["refinement"]["ran"])
        exp0 = dict(exp, tmpl_w=np.zeros(3))
        _, ev0 = s5n_pseudo.unfold_negweight(exp0, 42, 4, 5, refine_fn=self.fake_refine, unfold_fn=fake_unfold)
        self.assertFalse(ev0["refinement"]["ran"])
        np.testing.assert_allclose(seen["measured_weights"], [1.0, 2.0, 1.0])


if __name__ == "__main__":
    unittest.main()
