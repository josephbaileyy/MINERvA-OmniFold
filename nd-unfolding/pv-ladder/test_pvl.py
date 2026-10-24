"""Synthetic controls for the PV ladder (numpy only): run with `python3 -m unittest test_pvl -v` from this directory."""
import json
import os
import sys
import tempfile
import unittest

import numpy as np

import pvl_lib as L

_PV2D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "2d-unfolding", "pv2d")
sys.path.insert(0, _PV2D)
import pv2d_lib as P  # noqa: E402

NAMES3 = ("pt", "pz", "eavail")


def shape(names):
    return tuple(len(L.FINE[a]) - 1 for a in names)


def toy_inputs(names=NAMES3, n=40_000, seed=1):
    rng = np.random.default_rng(seed)
    gen = np.column_stack([rng.uniform(L.FINE[a][0], min(L.FINE[a][-1], 20.0), n) for a in names])
    reco = gen * rng.normal(1.0, 0.05, gen.shape)
    pass_truth = rng.uniform(size=n) > 0.05
    pass_reco = rng.uniform(size=n) > 0.2
    w = rng.uniform(0.5, 1.5, n)
    edges = [np.asarray(L.FINE[a], float) for a in names]
    of, _ = np.histogramdd(gen[pass_truth], bins=edges, weights=w[pass_truth])
    return {"MCgen": gen, "MCreco": reco, "pass_truth": pass_truth, "pass_reco": pass_reco, "w_truth": w,
            "w_reco": w * rng.uniform(0.9, 1.1, n), "denom_nd": of * 1.3, "edges": edges,
            "flux": np.ones(len(edges[0]) - 1), "data_pot": 1.0, "n_nucleons": 1.0}


class Cells(unittest.TestCase):
    def test_flat_index_matches_histogramdd(self):
        rng = np.random.default_rng(2)
        x = np.column_stack([rng.uniform(-0.5, 5.0, 5000), rng.uniform(1.0, 70.0, 5000), rng.uniform(-1, 120, 5000)])
        x[:4] = [[4.5, 60.0, 100.0], [0.0, 1.5, 0.0], [4.6, 10.0, 1.0], [np.nan, 3.0, 1.0]]
        idx = L.flat_index(x, NAMES3)
        h, _ = np.histogramdd(x[np.isfinite(x).all(1)], bins=[L.FINE[a] for a in NAMES3])
        mine = np.bincount(idx[idx >= 0], minlength=int(np.prod(shape(NAMES3))))
        np.testing.assert_array_equal(mine, h.ravel())
        self.assertEqual(idx[0], int(np.prod(shape(NAMES3))) - 1)   # the last edge is in the last bin
        self.assertEqual(idx[2], -1)                                   # above the last pT edge: outside
        self.assertEqual(idx[3], -1)

    def test_coarse_map_is_pv2ds_on_pt_pz(self):
        np.testing.assert_array_equal(L.coarse_of_cells(("pt", "pz")), P.coarse_of_cells().ravel())

    def test_gate_is_pv2ds_on_pt_pz(self):
        rng = np.random.default_rng(3)
        g, gref = rng.uniform(1, 2, (14, 16)), rng.uniform(1, 2, (14, 16))
        vg, vr = (g * rng.uniform(0.0, 0.12, g.shape)) ** 2, (gref * rng.uniform(0.0, 0.12, g.shape)) ** 2
        region = rng.uniform(size=g.shape) > 0.1
        vg[:7, :4] = (0.5 * g[:7, :4]) ** 2           # coarse cell 0 is too noisy even pooled
        mine = L.gated_shape_ratio(g.ravel(), vg.ravel(), gref.ravel(), vr.ravel(), region.ravel(),
                                   L.coarse_of_cells(("pt", "pz")), 0.05)
        theirs = P.gated_shape_ratio(g, vg, gref, vr, region, 0.05)
        np.testing.assert_array_equal(mine[0], theirs[0].ravel())
        np.testing.assert_array_equal(mine[2], theirs[2].ravel())
        self.assertTrue({"fine", "coarse", "noisy", "off"} <= set(mine[2]))

    def test_readout_spaces_sum_the_dropped_axes(self):
        names = L.AXES5
        x = np.random.default_rng(4).uniform(size=int(np.prod(shape(names))))
        full = x.reshape(shape(names))
        np.testing.assert_allclose(L.readout_space(x, names, "EW"), full.sum(axis=(0, 1, 3)).ravel())
        np.testing.assert_allclose(L.readout_space(x, names, "PTPZ"), full.sum(axis=(2, 3, 4)).ravel())
        j = L.readout_space(x, names, "J")
        self.assertEqual(j.size, 3 ** 5)
        self.assertAlmostEqual(j.sum(), x.sum())
        self.assertEqual(L.ew_headline().size, 39)

    def test_integrated_is_x_times_volume(self):
        x = np.ones(int(np.prod(shape(("eavail", "W")))))
        v = np.outer(np.diff(L.FINE["eavail"]), np.diff(L.FINE["W"])).ravel()
        np.testing.assert_allclose(L.integrated(x, ("eavail", "W")), v)


class Reweight(unittest.TestCase):
    def ratio(self, axes, r, cut=None):
        rec = {"schema": L.RATIO_SCHEMA, "axes": list(axes), "r": list(np.asarray(r, float).ravel())}
        if cut:
            rec["truth_cut"] = cut
        return rec

    def test_row_weight_cells_outside_and_cut(self):
        names = L.AXES5
        n_ew = 7 * 6
        r = np.arange(1, n_ew + 1, dtype=float)
        gen = np.array([[0.1, 2.0, 0.05, 0.1, 0.5],      # EW0
                        [0.1, 2.0, 99.0, 0.1, 100.0],    # E_avail last bin, W on the last edge: EW41
                        [0.1, 2.0, 150.0, 0.1, 0.5],     # outside the E_avail grid: r = 1
                        [0.1, 12.0, 0.05, 0.1, 0.5],     # p_parallel 12: fails the GiBUU cut
                        [0.1, 2.0, 0.05, -9999, 0.5],    # a q3 sentinel: outside the npz's grid, r = 1
                        [0.1, 2.0, 0.05, 0.1, 0.5]])     # a fake (fails the truth selection): r = 1
        pt = np.array([True, True, True, True, True, False])
        r2 = np.full(n_ew, 2.0)
        cut = {"axis": "pz", "below": 10.0}
        np.testing.assert_array_equal(L.row_weight(gen, names, self.ratio(("eavail", "W"), r2), pt), [2, 2, 1, 2, 1, 1])
        np.testing.assert_array_equal(L.row_weight(gen, names, self.ratio(("eavail", "W"), r2, cut), pt),
                                      [2, 2, 1, 1, 1, 1])
        np.testing.assert_array_equal(L.row_weight(gen[:2], names, self.ratio(("eavail", "W"), r), pt[:2]), [1, 42])
        with self.assertRaises(ValueError):
            L.row_weight(gen, names, self.ratio(("eavail", "W"), r[:-1]), pt)
        with self.assertRaises(ValueError):
            L.row_weight(gen, names, {"schema": "other"}, pt)

    def test_normalize_keeps_the_assigned_prior_weight(self):
        rng = np.random.default_rng(5)
        rho, p = rng.uniform(0.7, 1.4, 50), rng.uniform(1, 3, 50)
        assigned = rng.uniform(size=50) > 0.3
        r, k = L.normalize(rho, assigned, p)
        self.assertAlmostEqual((p * r)[assigned].sum(), p[assigned].sum())
        np.testing.assert_array_equal(r[~assigned], 1.0)
        np.testing.assert_allclose(r[assigned], rho[assigned] * k)

    def test_project_prediction_and_pz_cut(self):
        names = L.AXES5
        x = np.ones(shape(names))
        g, var = L.project_prediction(x, x, [np.asarray(L.FINE[a]) for a in names], ("eavail", "W"))
        vol_rest = np.diff(L.FINE["pt"]).sum() * np.diff(L.FINE["pz"]).sum() * np.diff(L.FINE["q3"]).sum()
        np.testing.assert_allclose(g, np.outer(np.diff(L.FINE["eavail"]), np.diff(L.FINE["W"])).ravel() * vol_rest)
        g10, _ = L.project_prediction(x, x, [np.asarray(L.FINE[a]) for a in names], ("eavail", "W"), 10.0)
        np.testing.assert_allclose(g10 / g, (10.0 - 1.5) / (60.0 - 1.5))
        with self.assertRaises(ValueError):
            L.project_prediction(x, x, [np.asarray(L.FINE[a]) for a in names], ("eavail", "W"), 11.0)


class PriorInputs(unittest.TestCase):
    def test_guard_silent_on_the_repaired_form(self):
        d = toy_inputs()
        r = L.row_weight(d["MCgen"], NAMES3, {"schema": L.RATIO_SCHEMA, "axes": list(NAMES3),
                                               "r": np.random.default_rng(6).uniform(0.8, 1.3, 1568).tolist()},
                         d["pass_truth"])
        ui, guards = L.prior_inputs(d, r)
        self.assertEqual(guards["r_spread_in_cell"], 0.0)
        self.assertLess(guards["completeness"], 1e-12)
        np.testing.assert_allclose(ui["w_truth"], d["w_truth"] * r)
        np.testing.assert_allclose(ui["w_reco"], d["w_reco"] * r)

    def test_guard_fires_when_r_varies_inside_a_cell(self):
        d = toy_inputs()
        r = 1.0 + 0.3 * (np.random.default_rng(7).uniform(size=d["w_truth"].size) > 0.5)
        with self.assertRaises(RuntimeError):
            L.prior_inputs(d, r)

    def test_identity_rescaling_is_exact(self):
        d = toy_inputs()
        ui, _ = L.prior_inputs(d, np.ones(d["w_truth"].size))
        np.testing.assert_array_equal(ui["denom_nd"], d["denom_nd"])     # the NC can be bitwise

    def test_closure_excludes_fakes(self):
        d = toy_inputs()
        exp, _ = L.closure_inputs(d, np.ones(d["w_truth"].size))
        keep = d["pass_reco"] & d["pass_truth"]
        for k, e in enumerate(d["edges"]):
            keep &= (d["MCreco"][:, k] >= e[0]) & (d["MCreco"][:, k] < e[-1])
        self.assertTrue(np.any(d["pass_reco"] & ~d["pass_truth"]))       # the toy has fakes to exclude
        np.testing.assert_array_equal(exp["obs"], d["MCreco"][keep])
        np.testing.assert_array_equal(exp["obs_counts"], d["w_reco"][keep])

    def test_closure_at_r1_is_the_nominal_truth(self):
        d = toy_inputs()
        exp, xt = L.closure_inputs(d, np.ones(d["w_truth"].size))
        self.assertEqual(exp["tmpl"].shape[0], 0)
        m = d["pass_truth"]
        unf, _ = np.histogramdd(d["MCgen"][m], bins=d["edges"], weights=d["w_truth"][m])
        comp = np.where(d["denom_nd"] > 0, unf / np.where(d["denom_nd"] > 0, d["denom_nd"], 1), 0)
        vol = L.integrated(np.ones(unf.size), NAMES3).reshape(unf.shape)
        want = np.where(comp > 0, unf * 1e4 / np.where(comp > 0, comp * vol, 1), 0)
        np.testing.assert_allclose(xt, want, rtol=1e-12)


class Support(unittest.TestCase):
    def test_rule(self):
        d = toy_inputs(n=20_000)
        s = L.support(d, NAMES3)
        m = d["pass_truth"]
        h, _ = np.histogramdd(d["MCgen"][m], bins=d["edges"], weights=d["w_truth"][m])
        np.testing.assert_allclose(s["truth_selected"], h.ravel())
        np.testing.assert_array_equal(s["supported"], (s["reco_signal"] >= 1000) & (s["truth_selected"] >= 1000))


class FeatureRestriction(unittest.TestCase):
    """pvl_unfold.unfold hands the classifiers only the declared columns and histograms on all of them."""

    def run_unfold(self, cols):
        import pvl_unfold as U  # puts nd-unfolding on sys.path
        import omnifold_nn_core as onc

        seen = {}

        class Est:
            def set_params(self, **kw):
                self.p = kw

            def get_params(self):
                return getattr(self, "p", {})

        def fake_make(kind, nvars, seed=None):
            return (Est(), Est(), Est())

        def fake_loop(gen, reco, meas, *args, **kw):
            onc.make_estimators("lgbm", gen.shape[1], seed=kw.get("seed"))
            seen.update(gen=gen.shape[1], reco=reco.shape[1], meas=meas.shape[1])
            return None, np.ones(int(np.asarray(args[1]).sum()))

        d = toy_inputs()
        d["measured"] = d["MCreco"][:1000] if cols is None else d["MCreco"][:1000][:, cols]
        d["measured_weights"] = np.ones(1000)
        saved = onc.make_estimators, onc.omnifold_loop
        onc.make_estimators, onc.omnifold_loop = fake_make, fake_loop
        try:
            xs, _ = U.unfold(d, cols, 42, 1, 1)
        finally:
            onc.make_estimators, onc.omnifold_loop = saved
        return seen, xs, d

    def test_restricted_columns_reach_the_classifiers_only(self):
        seen, xs, d = self.run_unfold([2])
        self.assertEqual(seen, {"gen": 1, "reco": 1, "meas": 1})
        self.assertEqual(xs.shape, shape(NAMES3))
        seen_all, xs_all, _ = self.run_unfold(None)
        self.assertEqual(seen_all, {"gen": 3, "reco": 3, "meas": 3})
        np.testing.assert_array_equal(xs, xs_all)    # wpush = 1 in both: the histogramming is the same


class MeasuredSides(unittest.TestCase):
    """The refinement (arm e) and arm (c)'s data see only the restricted columns."""

    def test_refinement_input_is_restricted(self):
        import pvl_unfold as U
        import s5e_trace

        seen = {}
        saved = s5e_trace.measured_side

        def fake(e, seed, threads, override, dtype):
            seen.update(obs=e["obs"].shape[1], tmpl=e["tmpl"].shape[1])
            return e["obs"], np.ones(len(e["obs"])), {}

        exp = {"obs": np.zeros((4, 5)), "tmpl": np.zeros((2, 5))}
        s5e_trace.measured_side = fake
        try:
            U.measured_negweight(exp, [2, 4], 42, 1)
            self.assertEqual(seen, {"obs": 2, "tmpl": 2})
            U.measured_negweight(exp, None, 42, 1)
            self.assertEqual(seen, {"obs": 5, "tmpl": 5})
        finally:
            s5e_trace.measured_side = saved
        self.assertEqual(exp["obs"].shape[1], 5)                       # the experiment itself is untouched

    def test_purity_measured_is_restricted(self):
        import pvl_unfold as U

        m = np.arange(20.0).reshape(4, 5)
        np.testing.assert_array_equal(U.measured_purity({"measured": m}, [2, 4]), m[:, [2, 4]])
        self.assertIs(U.measured_purity({"measured": m}, None), m)


class AnalyzeRefusals(unittest.TestCase):
    def setUp(self):
        import pvl_analyze as A

        self.A = A
        self.task = {"task": "L-EW_e_nuwro", "rung": "L-EW", "arm": "e", "features": "eavail,W", "vertex": "nuwro",
                     "mode": "data"}
        self.ratios = {"vertices": {"nuwro": {"ratio_sha256": "r" * 64}}}
        self.cfg = {"npz": {"sha256": "n" * 64}, "bkg": {"sha256": "b" * 64}}
        self.meta = {"rung": "L-EW", "arm": "e", "closure": False, "input_npz_sha256": "n" * 64,
                     "bkg_dump_sha256": "b" * 64, "ratio_sha256": "r" * 64, "features": ["eavail", "W"],
                     "estimator_seed": 42, "iters": 5, "threads": 32,
                     "refinement": {"ran": True, "classifier_params": dict(A.REFINE)},
                     "completeness_guard": {"r_spread_in_cell": 0.0, "completeness": 0.0},
                     "code_sha256": {"x": "1"}, "estimator_params": [{"a": 1}], "_name": "ref.npz"}

    def test_silent_on_a_consistent_product(self):
        self.A.check_meta("p.npz", dict(self.meta), self.task, self.ratios, self.cfg, dict(self.meta))

    def test_fires_on_each_mismatch(self):
        bad = {"features": ["pt", "pz", "eavail", "q3", "W"], "threads": 64, "ratio_sha256": "x" * 64,
               "refinement": {"ran": True, "classifier_params": {"n_estimators": 100}},
               "completeness_guard": {"r_spread_in_cell": 1e-3, "completeness": 0.0},
               "code_sha256": {"x": "2"}}
        for k, v in bad.items():
            m = dict(self.meta, **{k: v})
            with self.subTest(k), self.assertRaises(SystemExit):
                self.A.check_meta("p.npz", m, self.task, self.ratios, self.cfg, dict(self.meta))


class Tasks(unittest.TestCase):
    def test_declared_jobs(self):
        here = os.path.dirname(os.path.abspath(__file__))
        rows = [ln.split("\t") for ln in open(os.path.join(here, "tasks.tsv")) if not ln.startswith("#")]
        jobs = {}
        for r in rows:
            jobs.setdefault(r[6], []).append(r[0])
        self.assertEqual({k: len(v) for k, v in jobs.items()}, {"J1": 7, "J2": 6, "J3": 6, "J4": 6, "J5": 5, "F": 8})
        for r in rows:
            self.assertIn(r[1], L.RUNGS)
            if r[5] == "closure":
                self.assertEqual(r[2], "e")
        cfg = json.load(open(os.path.join(here, "config.json")))
        self.assertEqual(set(cfg["rungs"]), set(L.RUNGS))


if __name__ == "__main__":
    unittest.main()
