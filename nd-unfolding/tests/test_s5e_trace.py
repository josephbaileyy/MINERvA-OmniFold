"""Controls for the s5e diagnosis instrumentation (no LightGBM or ROOT: deterministic stub estimators).

The tracer must (a) not perturb the unfold it observes, (b) rebuild the loop's per-iteration weights
exactly, and (c) refuse when its rebuild disagrees with the loop. Each guard is tested in the
direction it acts and on its innocent neighbour."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_trace as st  # noqa: E402

EDGES = [np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 2.0]), np.array([0.0, 0.1, 0.4, 5.0]),
         np.array([0.0, 1.0, 3.0]), np.array([0.0, 1.5, 9.0])]
SHAPE = tuple(len(e) - 1 for e in EDGES)


def toy_inputs(n=6000, seed=0):
    rng = np.random.default_rng(seed)
    gen = np.column_stack([rng.uniform(0, 2, n), rng.uniform(0, 2, n), rng.uniform(0, 5, n),
                           rng.uniform(0, 3, n), rng.uniform(0, 9, n)]).astype(np.float32)
    reco = (gen + rng.normal(0, 0.1, gen.shape)).astype(np.float32)
    pass_reco = rng.uniform(size=n) < 0.7
    w = rng.uniform(0.1, 0.3, n)
    return {"MCgen": gen, "MCreco": reco, "pass_reco": pass_reco, "pass_truth": np.ones(n, bool),
            "w_truth": w, "w_reco": w * rng.uniform(0.9, 1.1, n), "denom_nd": np.full(SHAPE, 80.0),
            "flux": np.ones(2), "data_pot": 1.0, "n_nucleons": 1.0, "edges": EDGES}


class StubClf:
    """Deterministic weighted-histogram classifier on feature 0; exposes the sklearn surface used."""

    def __init__(self, seed=None):
        self.params = {"random_state": seed}

    def set_params(self, **kw):
        self.params.update(kw)
        return self

    def get_params(self, deep=True):
        return dict(self.params)

    @staticmethod
    def _bin(X):
        return np.clip((np.asarray(X)[:, 0] * 5).astype(int), 0, 9)

    def fit(self, X, y, sample_weight=None):
        b, w = self._bin(X), np.asarray(sample_weight, float)
        w1 = np.bincount(b[y == 1], w[y == 1], 10) + 1e-3
        w0 = np.bincount(b[y == 0], w[y == 0], 10) + 1e-3
        self.p = w1 / (w0 + w1)
        return self

    def predict_proba(self, X):
        p = self.p[self._bin(X)]
        return np.column_stack([1 - p, p])


class StubReg(StubClf):
    def fit(self, X, y, sample_weight=None):
        b = self._bin(X)
        self.m = np.bincount(b, np.asarray(y, float), 10) / np.maximum(np.bincount(b, minlength=10), 1)
        return self

    def predict(self, X):
        return self.m[self._bin(X)] * 1.07  # deliberately not 1, so the missed-event probe is visible


def stub_factory(kind, nvars, seed=None):
    return StubClf(seed), StubClf(seed), StubReg(seed)


class StubbedLoop(unittest.TestCase):
    def setUp(self):
        self.original = onc.make_estimators
        onc.make_estimators = stub_factory
        inp = toy_inputs()
        r = 1.0 + 0.4 * (inp["MCgen"][:, 2] > 1.0)
        self.unf_in, self.x_true = st.asimov_same(inp, r)
        self.r = r
        self.U = np.random.default_rng(3).uniform(size=(7, int(np.prod(SHAPE))))

    def tearDown(self):
        onc.make_estimators = self.original

    def traced(self, iters, **kw):
        rec = st.Recorder(self.unf_in, self.r, self.U, iters)
        xs, params, tracer = st.traced_unfold(self.unf_in, rec, 42, 1, iters, **kw)
        return xs, rec, tracer

    def test_tracing_does_not_perturb_the_unfold(self):
        ref, _ = s5c_unfold.unfold(self.unf_in, "deterministic", 42, 1, 4)
        xs, rec, tracer = self.traced(4)
        np.testing.assert_array_equal(xs, ref)
        self.assertEqual(tracer.checks, {"step1_mc_weights": 4, "step2_pull_weights": 4})

    def test_iteration_five_of_a_longer_run_is_the_five_iteration_unfold(self):
        ref, _ = s5c_unfold.unfold(self.unf_in, "deterministic", 42, 1, 5)
        _, rec, _ = self.traced(7)
        np.testing.assert_array_equal(rec.xs_it5, ref)

    def test_recorded_final_functionals_match_the_returned_unfold(self):
        xs, rec, _ = self.traced(3)
        np.testing.assert_allclose(rec.out["fn_push"][-1], self.U @ xs.ravel(), rtol=1e-12)

    def test_truth_and_folded_truth_references(self):
        _, rec, _ = self.traced(1)
        np.testing.assert_allclose(rec.out["fn_true_A"], self.U @ self.x_true.ravel(), rtol=1e-12)
        # asimov_same: the measured side IS the folded truth model
        np.testing.assert_allclose(rec.out["reco5d_D"], rec.out["reco5d_true"], rtol=1e-12)

    def test_missed_unity_changes_only_the_fill(self):
        ref, _ = s5c_unfold.unfold(self.unf_in, "deterministic", 42, 1, 3)
        xs, rec, _ = self.traced(3, missed="unity")
        np.testing.assert_array_equal(rec.out["mean_fill_fail"], 1.0)
        self.assertGreater(np.max(np.abs(xs - ref)), 0.0)

    def test_capacity_and_seed_overrides_reach_the_estimators(self):
        seen = []

        def spy(kind, nvars, seed=None):
            ests = stub_factory(kind, nvars, seed)
            seen.append(ests)
            return ests

        onc.make_estimators = spy
        self.traced(1, capacity=(400, 31), seed_per_estimator=True)
        params = [e.get_params() for e in seen[0]]
        self.assertEqual([p["n_estimators"] for p in params], [400] * 3)
        self.assertEqual([p["num_leaves"] for p in params], [31] * 3)
        self.assertEqual([p["random_state"] for p in params], [42, 43, 44])


class TracerRefuses(unittest.TestCase):
    def setUp(self):
        self.ctx = {"pass_reco": np.array([True, True, False]), "w_truth": np.array([1.0, 2.0, 3.0]),
                    "w_reco": np.array([0.5, 0.5, 0.5])}
        self.calls = []
        self.t = st.Tracer(self.ctx, lambda *a: self.calls.append(a))

    def test_step1_weights_not_equal_to_the_rebuilt_w_push(self):
        self.t.on_fit("step1", None, None, np.array([0.5, 0.5, 1.0]))  # innocent: w_push = 1
        with self.assertRaises(st.TraceError):
            self.t.on_fit("step1", None, None, np.array([0.5, 0.5000001, 1.0]))

    def test_step2_weights_not_equal_to_the_rebuilt_w_pull(self):
        self.t.on_fit("step1", None, None, np.array([0.5, 0.5, 9.0]))
        self.t.on_proba("step1", np.array([[0.5, 0.5], [0.2, 0.8]]))
        self.t.on_fit("reg", None, np.array([1.0, 4.0]), None)
        self.t.fill = np.array([2.0])
        good = np.concatenate([self.ctx["w_truth"], np.array([1.0, 4.0, 2.0]) * self.ctx["w_truth"]])
        self.t.on_fit("step2", None, None, good)
        bad = good.copy()
        bad[-1] *= 1.0 + 1e-15
        with self.assertRaises(st.TraceError):
            self.t.on_fit("step2", None, None, bad)


class Binning(unittest.TestCase):
    def test_flat_index_is_histogramdds_assignment(self):
        rng = np.random.default_rng(5)
        x = np.column_stack([rng.uniform(-0.2, 2.2, 5000), rng.uniform(0, 2, 5000), rng.uniform(0, 5.2, 5000),
                             rng.uniform(0, 3, 5000), rng.uniform(0, 9, 5000)])
        x[:10, 0] = 2.0  # last edge: inside (histogramdd convention)
        x[10:20, 2] = 0.1  # interior edge
        flat = st.flat_index(x, EDGES)
        h, _ = np.histogramdd(x, bins=EDGES)
        np.testing.assert_array_equal(np.bincount(flat[flat >= 0], minlength=h.size), h.ravel().astype(int))
        self.assertTrue(np.all(flat[:10] >= 0))

    def test_ew_cell_of_a_flat_index(self):
        flat = np.ravel_multi_index(([1], [0], [2], [1], [1]), SHAPE)
        self.assertEqual(int(st.ew_of_flat(flat, SHAPE)[0]), 2 * SHAPE[4] + 1)
        self.assertEqual(int(st.ew_of_flat(np.array([-1]), SHAPE)[0]), -1)


class Constructions(unittest.TestCase):
    def test_asimov_same_nominal_is_the_mc_itself(self):
        inp = toy_inputs()
        unf_in, x_true = st.asimov_same(inp, np.ones(inp["MCgen"].shape[0]))
        pr = inp["pass_reco"]
        np.testing.assert_array_equal(unf_in["measured"], inp["MCreco"][pr])
        np.testing.assert_array_equal(unf_in["measured_weights"], inp["w_reco"][pr])
        np.testing.assert_allclose(x_true, st.xs_from_push(unf_in, np.ones(pr.size)), rtol=1e-12)

    def test_jitter_stays_within_half_an_ulp_and_upcast_is_exact(self):
        x = np.random.default_rng(1).uniform(0, 50, (20000, 5)).astype(np.float32)
        np.testing.assert_array_equal(st.jitter_coords(x, None), x.astype(np.float64))
        j = st.jitter_coords(x, 7)
        d = np.abs(j - x.astype(np.float64))
        self.assertTrue(np.all(d <= 0.5 * np.spacing(x).astype(np.float64)))
        self.assertGreater(np.mean(d > 0), 0.99)
        self.assertGreater(np.mean(j.astype(np.float32) == x), 0.9999)

    def test_expectation_template_is_the_source_half_at_expected_weight(self):
        rng = np.random.default_rng(2)
        reco = np.column_stack([rng.uniform(0, 2.2, 800), rng.uniform(0, 2, 800), rng.uniform(0, 5, 800),
                                rng.uniform(0, 3, 800), rng.uniform(0, 9, 800)]).astype(np.float32)
        bkg = {"bkg_reco": reco, "bkg_w": rng.uniform(0.05, 0.4, 800)}
        exp = {"edges": EDGES, "tmpl": None, "tmpl_w": None}
        out = st.expectation_template(exp, bkg, split_key=12345)
        import s5c_pseudo, s5n_pseudo
        is_c = s5c_pseudo.half_mask(800, s5n_pseudo.bkg_split_key(12345))
        keep = s5n_pseudo.fid_mask(reco[is_c], EDGES)
        np.testing.assert_array_equal(out["tmpl"], reco[is_c][keep])
        np.testing.assert_array_equal(out["tmpl_w"], 2.0 * bkg["bkg_w"][is_c][keep])


if __name__ == "__main__":
    unittest.main()
