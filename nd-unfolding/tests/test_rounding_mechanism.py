"""Tests of RS1 (RS1-DECLARATION.md §8): the arms' rebindings, the jitters, every refusal in the direction it acts and
the other, the analysis's gates and readings, R0's controls, and the job script.

Run: python3 -B nd-unfolding/tests/test_rounding_mechanism.py (no LightGBM, no ROOT). The estimators are a deterministic
histogram stand-in (``Hist``): like LightGBM in histogram mode, a row reaches a fit only through bins built from the
sorted distinct values and their counts. The stand-in is a fixture of that one property, not of LightGBM.
"""
import contextlib
import gzip
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
sys.path.insert(1, str(ND))
import estimator_stability_probe as esp  # noqa: E402
import omnifold_nn_core as onc  # noqa: E402
import rounding_mechanism_analyze as rma  # noqa: E402
import rounding_mechanism_probe as rmp  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_trace  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402

NB = 4


# ------------------------------------------------------------------------------------------- stand-ins

class Booster:
    def __init__(self, th):
        self.th = th

    def dump_model(self):
        trees = []
        for k, ts in enumerate(self.th):
            node = {"leaf_value": 0.0, "leaf_count": 1}
            for t in reversed(list(ts)):
                node = {"split_feature": k, "threshold": float(t), "split_gain": 1.0, "internal_count": 2,
                        "left_child": {"leaf_value": float(t), "leaf_count": 1}, "right_child": node}
            trees.append({"tree_structure": node})
        return {"tree_info": trees}


class Hist:
    """Equal-count bins over each feature's sorted distinct values (ties are units); the prediction is the weighted mean
    label (or target) of the row's joint bin on features 0-2."""

    def __init__(self, **params):
        self.params = dict(params)

    def get_params(self, deep=True):
        return dict(self.params)

    def set_params(self, **params):
        self.params.update(params)
        return self

    @staticmethod
    def bounds(col):
        vals, cnt = np.unique(col, return_counts=True)
        cum, th, target, k = np.cumsum(cnt), [], len(col) / NB, 1
        for i in range(len(vals) - 1):
            if cum[i] >= k * target:
                th.append((vals[i] + vals[i + 1]) / 2.0)
                k += 1
        return np.array(th)

    def key(self, X):
        X = np.asarray(X)
        return sum(np.searchsorted(self.th[k], X[:, k], side="left") * NB ** k for k in range(3))

    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X)
        w = np.ones(len(y)) if sample_weight is None else np.asarray(sample_weight, float)
        self.th = [self.bounds(X[:, k]) for k in range(X.shape[1])]
        key = self.key(X)
        num = np.bincount(key, weights=w * np.asarray(y, float), minlength=NB ** 3)
        den = np.bincount(key, weights=w, minlength=NB ** 3)
        self.table = np.where(den > 0, num / np.where(den > 0, den, 1), 0.5)
        self.booster_ = Booster(self.th)
        return self

    def predict_proba(self, X):
        p = np.clip(self.table[self.key(X)], 0.05, 0.95)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return self.table[self.key(X)]


def standin_estimators(kind, nvars, seed=None):
    d = {"n_estimators": 100, "num_leaves": 8, "learning_rate": 0.1, "verbose": -1, "random_state": seed}
    return Hist(**d), Hist(**d), Hist(**d)


REFINE_SEEN: list = []


def standin_refine(feat, signed, params):
    REFINE_SEEN.append(np.array(feat, copy=True))
    lab = (signed > 0).astype(float)
    h = Hist().fit(feat, lab, np.abs(signed))
    g = np.clip(h.predict_proba(feat)[:, 1], 1e-6, 1 - 1e-6)
    f = 2 * g - 1
    return np.abs(signed) * np.clip(f, 0, None), g, float((f < 0).mean())


# ---------------------------------------------------------------------------------------------- fixture

EDGES = [np.array([0.0, 0.5, 1.0])] * 5


def lattice(rng, n, step=1 / 64):
    """float32 coordinates on a coarse lattice inside the grid, so float32 ties are common; some exact zeros."""
    x = np.round(rng.uniform(0.0, 0.999, (n, 5)) / step) * step
    x[rng.random((n, 5)) < 0.05] = 0.0
    return np.minimum(x, 1.0 - step).astype(np.float32)


def write_fixture(d: Path, n=2400, nb=500, seed=7):
    rng = np.random.default_rng(seed)
    mc_gen = lattice(rng, n)
    mc_reco = lattice(rng, n)
    np.savez(d / "in.npz", MCgen=mc_gen, MCreco=mc_reco, measured=lattice(rng, 300),
             pass_reco=np.ones(n, bool), pass_truth=np.ones(n, bool), w_truth=np.full(n, 0.5),
             w_reco=np.full(n, 0.5), measured_weights=np.ones(300), denom_nd=np.full([2] * 5, 40.0),
             flux=np.ones(2), data_pot=np.array(1.0), n_nucleons=np.array(1.0), nedges=np.array(5),
             **{f"edges_{i}": e for i, e in enumerate(EDGES)})
    sha = s5n_pseudo.sha256_path(d / "in.npz")
    np.savez(d / "bkg.npz", bkg_reco=lattice(rng, nb), bkg_w=np.full(nb, 0.2), bkg_nd=np.zeros([2] * 5),
             meta=json.dumps({"npz_sha256": sha}))
    (d / "ratio.json").write_text(json.dumps({"schema": "test"}))
    return sha, s5n_pseudo.sha256_path(d / "bkg.npz")


@contextlib.contextmanager
def standins(d: Path):
    """Stand-in estimators and refinement; the declared stability input replaced by the fixture's; every module name the
    bound installers rebind is restored after."""
    names = [(onc, "make_estimators"), (s5n_pseudo, "refine"), (s5n_pseudo, "refine_params"),
             (s5n_pseudo, "code_digests"), (s5n_pseudo, "truth_weight")]
    saved = [(m, k, getattr(m, k)) for m, k in names]
    stab = dict(rmp.STABILITY)
    orig_refine = s5n_pseudo.refine
    onc.make_estimators = standin_estimators
    s5n_pseudo.refine = lambda feat, w, seed, thr, refine_fn=None: orig_refine(feat, w, seed, thr, refine_fn=standin_refine)
    rmp.STABILITY.update({"truth": "nominal", "amplitude": 0.0, "ratio": str(d / "ratio.json"),
                          "ratio_sha256": s5n_pseudo.sha256_path(d / "ratio.json"), "threads": 1})
    try:
        yield
    finally:
        for m, k, v in saved:
            setattr(m, k, v)
        rmp.STABILITY.clear()
        rmp.STABILITY.update(stab)


def runner_args(d: Path, shas, pairs: str, arm: str, **over):
    a = {"--npz": str(d / "in.npz"), "--bkg": str(d / "bkg.npz"), "--expect-npz-sha256": shas[0],
         "--expect-bkg-sha256": shas[1], "--config": "R", "--iters": "5", "--threads": "1", "--construction": "pseudo",
         "--truth": "nominal", "--amplitude": "0.0", "--eavail-ratio": str(d / "ratio.json"),
         "--pseudo-seed": str(esp.STABILITY_PSEUDO_SEED), "--tag": f"rs1_{arm}", "--out": str(d / "runs" / arm)}
    a.update(over)
    out = []
    for k, v in a.items():
        out += [k, v]
    return out + [f"--pairs={pairs}"]


def run_arm(d, shas, arm, pairs, U=None, **over):
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        try:
            with rmp.install(arm, U):
                rc = esp.main(["--candidate", "control", "stability", "--", *runner_args(d, shas, pairs, arm, **over)])
        except rmp.Refusal as exc:
            print(exc, file=err)
            rc = 5
        except SystemExit as exc:
            rc = exc.code
    return rc, err.getvalue()


def product(d, arm, seed):
    s = "-" if seed is None else seed
    return rma.load(d / "runs" / arm / f"rs1_{arm}_b-_j{s}.npz")


class Fixture(unittest.TestCase):
    """One fixture directory per class; arms are run once and shared by the class's tests."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.d = Path(cls.tmp.name)
        cls.shas = write_fixture(cls.d)
        cls.U = np.random.default_rng(3).random((6, 32))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()


# ------------------------------------------------------------------------------------------------ jitters

class ValueKeyedJitter(unittest.TestCase):
    def power_of_two_neighbours(self):
        """Adjacent float32 values on both sides of every power of two in [2^-10, 2^10], both signs."""
        vals = []
        for e in range(-10, 11):
            p = np.float32(2.0 ** e)
            lo = np.nextafter(p, np.float32(0))
            hi = np.nextafter(p, np.float32(np.inf))
            vals += [lo, p, hi]
        v = np.array(vals, np.float32)
        return np.concatenate([v, -v])

    def test_order_is_strictly_preserved_across_powers_of_two(self):
        v = np.sort(self.power_of_two_neighbours())
        X = np.tile(v[:, None], (1, 5))
        for seed in range(1, 200):
            out = rmp.value_keyed_jitter(X, seed)
            self.assertTrue(np.all(np.diff(out[:, 0]) > 0), f"seed {seed} reordered adjacent float32 values")

    def test_the_protocols_row_keyed_jitter_does_reorder_at_a_power_of_two(self):
        """The counterfactual: the bound protocol's step (spacing above) can swap a power of two with its lower
        neighbour, which is why V uses the spacing toward zero."""
        p = np.float32(1.0)
        pair = np.array([np.nextafter(p, np.float32(0)), p], np.float32)
        X = np.tile(pair[:, None], (1, 5))
        flips = sum(bool(j[1, 0] < j[0, 0]) for j in (s5e_trace.jitter_coords(X, s) for s in range(1, 400)))
        self.assertGreater(flips, 0)

    def test_equal_values_move_identically_in_every_array(self):
        rng = np.random.default_rng(1)
        a = lattice(rng, 500)
        b = lattice(rng, 300)
        ja, jb = rmp.value_keyed_jitter(a, 5), rmp.value_keyed_jitter(b, 5)
        for k in range(5):
            m = {}
            for x, y in zip(np.concatenate([a[:, k], b[:, k]]), np.concatenate([ja[:, k], jb[:, k]])):
                m.setdefault(float(x), set()).add(float(y))
            self.assertTrue(all(len(s) == 1 for s in m.values()), f"axis {k}: one float32 value moved two ways")

    def test_ties_are_kept_and_the_protocol_breaks_them(self):
        rng = np.random.default_rng(2)
        a = lattice(rng, 2000)
        n_tied = len(np.unique(a[:, 1]))
        self.assertEqual(len(np.unique(rmp.value_keyed_jitter(a, 3)[:, 1])), n_tied)
        self.assertGreater(len(np.unique(s5e_trace.jitter_coords(a, 3)[:, 1])), n_tied)

    def test_edges_unmoved_and_steps_within_half_the_spacing_toward_zero(self):
        rng = np.random.default_rng(4)
        a = lattice(rng, 3000)
        out = rmp.value_keyed_jitter(a, 9, EDGES)
        base = a.astype(np.float64)
        on_edge = np.isin(base, np.array([0.0, 0.5, 1.0]))
        self.assertTrue(np.array_equal(out[on_edge], base[on_edge]))
        self.assertTrue(np.any(out[~on_edge] != base[~on_edge]))
        self.assertTrue(np.all(np.abs(out - base) <= 0.5 * rmp.ulp_toward_zero(a)))

    def test_no_seed_is_the_float64_copy(self):
        a = lattice(np.random.default_rng(5), 100)
        self.assertTrue(np.array_equal(rmp.value_keyed_jitter(a, None), a.astype(np.float64)))


class AxisJitter(unittest.TestCase):
    def test_axis_k_carries_the_protocols_own_draws_and_the_others_none(self):
        a = lattice(np.random.default_rng(6), 800)
        full = s5e_trace.jitter_coords(a, 4, EDGES)
        for k in range(5):
            out = rmp.axis_jitter(s5e_trace.jitter_coords, k)(a, 4, EDGES)
            self.assertTrue(np.array_equal(out[:, k], full[:, k]))
            others = [j for j in range(5) if j != k]
            self.assertTrue(np.array_equal(out[:, others], a.astype(np.float64)[:, others]))


class Float64Base(unittest.TestCase):
    """Audit E2: seed 0 is the protocol's step-free float64 upcast, and a jittered product differs from it by the step."""

    def test_seed_zero_is_the_upcast_and_a_jitter_differs_by_exactly_the_step(self):
        rng = np.random.default_rng(8)
        inputs = {"MCgen": lattice(rng, 400), "MCreco": lattice(rng, 400), "measured": lattice(rng, 50), "edges": EDGES}
        bkg = {"bkg_reco": lattice(rng, 60)}
        with rmp.install("B63"):
            ji0, jb0 = s5p_numerics.jittered(inputs, bkg, rmp.UNJITTERED_F64)
            ji3, jb3 = s5p_numerics.jittered(inputs, bkg, 3)
        for k in ("MCgen", "MCreco", "measured"):
            x32 = np.asarray(inputs[k], np.float32)
            self.assertTrue(np.array_equal(ji0[k], x32.astype(np.float64)), k)
            ulp = np.spacing(np.abs(x32)).astype(np.float64)
            step = np.random.default_rng(3).uniform(-0.5, 0.5, x32.shape) * ulp
            for e_k, e in enumerate(EDGES):
                step[np.isin(ji0[k][:, e_k], e), e_k] = 0.0
            self.assertTrue(np.array_equal(ji3[k], ji0[k] + step), k)
        self.assertTrue(np.array_equal(jb0["bkg_reco"], np.asarray(bkg["bkg_reco"], np.float32).astype(np.float64)))

    def test_without_the_install_seed_zero_would_be_a_jitter(self):
        """The other direction: the bound function treats 0 as an ordinary seed, so the rebinding is what makes it a
        base."""
        rng = np.random.default_rng(8)
        inputs = {"MCgen": lattice(rng, 400), "MCreco": lattice(rng, 400), "measured": lattice(rng, 50), "edges": EDGES}
        ji, _ = s5p_numerics.jittered(inputs, {"bkg_reco": lattice(rng, 60)}, 0)
        self.assertFalse(np.array_equal(ji["MCgen"], np.asarray(inputs["MCgen"], np.float32).astype(np.float64)))


# ----------------------------------------------------------------------------------------- end to end

class EndToEnd(Fixture):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        d, s = cls.d, cls.shas
        cls.rc = {}
        with standins(d):
            cls.rc["A0"] = run_arm(d, s, "A0", "-:-,-:0,-:1,-:2,-:3", U=cls.U)
            cls.rc["V"] = run_arm(d, s, "V", "-:1,-:2,-:3")
            cls.rc["S_all"] = run_arm(d, s, "S_all", "-:1,-:2,-:3")
            REFINE_SEEN.clear()
            cls.rc["S_ref"] = run_arm(d, s, "S_ref", "-:1")
            cls.seen_ref = list(REFINE_SEEN)
            REFINE_SEEN.clear()
            cls.rc["S_omni"] = run_arm(d, s, "S_omni", "-:1")
            cls.seen_omni = list(REFINE_SEEN)
            cls.rc["B63"] = run_arm(d, s, "B63", "-:0,-:1")
            cls.rc["P1"] = run_arm(d, s, "P1", "-:0")
            cls.rc["F_pz"] = run_arm(d, s, "F_pz", "-:1")

    def test_every_arm_ran(self):
        for arm, (rc, err) in self.rc.items():
            self.assertEqual(rc, 0, f"{arm}: {err}")

    def test_products_carry_the_arm_and_go_through_fdstabs_control_path(self):
        x, m = product(self.d, "A0", 1)
        self.assertEqual(m["rounding_mechanism"]["arm"], "A0")
        self.assertEqual(m["stability_probe"]["candidate"], "control")
        self.assertEqual(m["jitter_seed"], 1)
        _, m0 = product(self.d, "A0", 0)
        self.assertTrue(m0["rounding_mechanism"]["unjittered_float64"])
        self.assertEqual(m0["coords"], "float64")

    def test_K1_logic_on_the_histogram_fixture(self):
        """With every row reco-passing (no untrained rows), V's tie-preserving jitter leaves the result bitwise equal to
        the float64 base; the protocol's tie-breaking jitter does not."""
        base = product(self.d, "A0", 0)[0]
        for s in (1, 2, 3):
            self.assertTrue(np.array_equal(product(self.d, "V", s)[0], base), f"V seed {s}")
        self.assertFalse(all(np.array_equal(product(self.d, "A0", s)[0], base) for s in (1, 2, 3)))

    def test_G4_s_all_is_a0_bitwise(self):
        for s in (1, 2, 3):
            self.assertTrue(np.array_equal(product(self.d, "S_all", s)[0], product(self.d, "A0", s)[0]), s)

    def test_s_ref_jitters_only_the_refinement_and_s_omni_only_the_loop(self):
        a0_1 = product(self.d, "A0", 1)[0]
        base = product(self.d, "A0", 0)[0]
        ref_feat, omni_feat = self.seen_ref[0], self.seen_omni[0]
        # the refinement saw jittered rows under S-ref and the upcast rows under S-omni
        self.assertTrue(np.array_equal(omni_feat, omni_feat.astype(np.float32).astype(np.float64)))
        self.assertFalse(np.array_equal(ref_feat, ref_feat.astype(np.float32).astype(np.float64)))
        # the same rows, each within the protocol's +-1/2 float32 spacing (above) of its unjittered value
        self.assertEqual(ref_feat.shape, omni_feat.shape)
        spacing = np.spacing(np.abs(omni_feat.astype(np.float32))).astype(np.float64)
        self.assertTrue(np.all(np.abs(ref_feat - omni_feat) <= 0.5 * spacing))
        for arm in ("S_ref", "S_omni"):
            x = product(self.d, arm, 1)[0]
            self.assertTrue(np.all(np.isfinite(x)))
        self.assertFalse(np.array_equal(a0_1, base))

    def test_trace_sidecars(self):
        t = rma.trace(self.d / "runs", "A0", 1)
        self.assertEqual(np.shape(t["fn_push"]), (5, self.U.shape[0]))
        self.assertTrue(t["fits"] and {f["role"] for f in t["fits"]} <= {"clf1", "clf2", "reg"})
        b = rma.trace(self.d / "runs", "A0", None)
        self.assertEqual(len(b["ties_mc_truth"]), 5)
        self.assertTrue(all(0 < v <= 1 for v in b["ties_mc_truth"]))
        self.assertIn("zero_weight_rows", b["measured_sides"][0])
        self.assertIsNone(rma.trace(self.d / "runs", "V", 1).get("fn_push"))

    def test_the_bound_probes_leaf_counts_read_through_the_wrapper(self):
        _, m = product(self.d, "A0", 1)
        self.assertTrue(any(f["min_leaf_count"][0] is not None for f in m["stability_probe"]["fits"]))

    def test_b_arm_max_bin_reaches_the_loop_and_the_refinement(self):
        _, m = product(self.d, "B63", 1)
        self.assertTrue(all(p.get("max_bin") == 63 for p in m["estimator_params"]))
        self.assertEqual(m["refinement"]["classifier_params"]["max_bin"], 63)

    def test_p_arm_is_a_permutation_of_the_float64_base(self):
        x = product(self.d, "P1", 0)[0]
        base = product(self.d, "A0", 0)[0]
        self.assertEqual(x.shape, base.shape)
        self.assertTrue(np.allclose(x, base, rtol=1e-9, atol=0))

    def test_names_restored_after_every_arm(self):
        self.assertEqual(s5p_numerics.jittered.__module__, "s5p_numerics")
        self.assertEqual(s5e_trace.jitter_coords.__module__, "s5e_trace")
        self.assertEqual(s5c_unfold.config_params.__module__, "s5c_unfold")
        self.assertEqual(s5n_pseudo.write_product.__module__, "s5n_pseudo")


class Refusals(Fixture):
    def test_undeclared_pair_wrong_truth_and_wrong_threads_are_refused_and_the_declared_run_is_not(self):
        d, s = self.d, self.shas
        with standins(d):
            self.assertEqual(run_arm(d, s, "V", "-:0")[0], 2)          # V declares no float64 base
            self.assertEqual(run_arm(d, s, "P1", "-:1")[0], 2)         # P declares only seed 0
            self.assertEqual(run_arm(d, s, "V", "-:21")[0], 2)         # beyond the 20 seeds
            self.assertEqual(run_arm(d, s, "V", "-:1", **{"--threads": "2"})[0], 2)
            self.assertEqual(run_arm(d, s, "V", "-:1", **{"--truth": "eavail_shape"})[0], 2)
            self.assertEqual(run_arm(d, s, "V", "-:4")[0], 0)

    def test_a_write_without_the_namespace_check_is_refused(self):
        with rmp.install("V"):
            with self.assertRaises(rmp.Refusal):
                s5n_pseudo.write_product(self.d / "x.npz", {}, {})

    def test_misaligned_experiments_are_refused_and_aligned_ones_pass(self):
        e = {"obs_counts": np.ones(3), "tmpl_w": np.ones(2), "w_truth": np.ones(4), "w_reco": np.ones(4),
             "pass_reco": np.ones(4, bool), "pass_truth": np.ones(4, bool), "MCgen": np.zeros((4, 5)),
             "MCreco": np.zeros((4, 5)), "obs": np.zeros((3, 5)), "tmpl": np.zeros((2, 5))}
        rmp.check_aligned(e, dict(e), None, None)
        bad = dict(e, obs_counts=np.array([1.0, 2.0, 1.0]))
        with self.assertRaises(rmp.Refusal):
            rmp.check_aligned(e, bad, None, None)
        with self.assertRaises(rmp.Refusal):
            rmp.check_aligned(e, dict(e, obs=np.zeros((2, 5))), None, None)
        with self.assertRaises(rmp.Refusal):
            rmp.check_aligned(e, dict(e), np.ones(2), np.zeros(2))

    def test_an_s_arm_whose_second_build_differs_stops_with_rc5(self):
        d, s = self.d, self.shas
        with standins(d):
            orig = s5n_pseudo.build_pseudo
            calls = []

            def build(inputs, bkg, *a, **k):
                exp, xt, info = orig(inputs, bkg, *a, **k)
                calls.append(1)
                if len(calls) == 2:
                    exp = dict(exp, obs_counts=exp["obs_counts"] + 1)
                return exp, xt, info

            s5n_pseudo.build_pseudo = build
            try:
                rc, err = run_arm(d, s, "S_ref", "-:2")
            finally:
                s5n_pseudo.build_pseudo = orig
        self.assertEqual(rc, 5, err)
        self.assertIn("not aligned", err)

    def test_a_refinement_without_max_bin_is_refused(self):
        d, s = self.d, self.shas
        with standins(d):
            saved = s5n_pseudo.refine_params
            s5n_pseudo.refine_params = lambda seed, thr: {"random_state": seed + 3}  # drops config_params
            try:
                rc, err = run_arm(d, s, "B1023", "-:2")
            finally:
                s5n_pseudo.refine_params = saved
        self.assertEqual(rc, 5, err)

    def test_names_are_restored_after_an_error(self):
        before = (s5p_numerics.jittered, s5p_numerics.unfold_one, s5e_trace.jitter_coords, s5n_pseudo.build_pseudo,
                  s5n_pseudo.write_product, s5c_unfold.config_params, s5c_unfold.unfold, onc.make_estimators)
        with self.assertRaises(KeyError):
            with rmp.install("A0", np.zeros((1, 32))):
                raise KeyError("x")
        after = (s5p_numerics.jittered, s5p_numerics.unfold_one, s5e_trace.jitter_coords, s5n_pseudo.build_pseudo,
                 s5n_pseudo.write_product, s5c_unfold.config_params, s5c_unfold.unfold, onc.make_estimators)
        self.assertEqual(before, after)

    def test_a_traced_arm_without_u_is_refused(self):
        with self.assertRaises(ValueError):
            with rmp.install("A0"):
                pass


# ----------------------------------------------------------------------------------------------- queue

class Queue(unittest.TestCase):
    def lines(self, d):
        a = type("A", (), {"npz": Path("/x/of_inputs_5d.npz"), "bkg": Path("/x/bkg_dump.npz"), "runs": d / "runs",
                           "expect_npz_sha256": "0" * 64, "expect_bkg_sha256": "1" * 64})
        return rmp.task_lines(a)

    def test_the_declared_counts(self):
        with tempfile.TemporaryDirectory() as d:
            lines, dry = self.lines(Path(d))
        body = lines[1:]
        self.assertEqual(sum(int(l.split("\t")[1]) for l in body), 229)
        self.assertEqual(len(dry), 9)
        self.assertTrue(all(int(l.split("\t")[1]) == 1 for l in body if l.split("\t")[0] in dry))
        self.assertTrue(all(int(l.split("\t")[1]) <= rmp.CHUNK for l in body))
        per_arm = {}
        for l in body:
            per_arm[l.split("\t")[0].rsplit("_", 1)[0]] = per_arm.get(l.split("\t")[0].rsplit("_", 1)[0], 0) + int(l.split("\t")[1])
        self.assertEqual(per_arm["rs1_A0"], 22)
        self.assertEqual(per_arm["rs1_S_all"], 3)
        self.assertEqual(per_arm["rs1_B1023"], 21)

    def test_every_queue_line_passes_the_real_parsers_and_rs1s_check(self):
        """Each line through rmp.main into esp.main and s5p_numerics.main's own parser, stopped just after RS1's and
        FD-STAB's namespace checks pass. Any SystemExit or other return fails."""
        class Parsed(Exception):
            pass

        with tempfile.TemporaryDirectory() as d:
            lines, _ = self.lines(Path(d))
        saved = s5p_numerics.s5e_candidate.install
        cwd = os.getcwd()
        os.chdir(REPO)
        saved_fm = rmp.functional_matrix
        rmp.functional_matrix = lambda c, h: np.zeros((169, 32))
        try:
            def stop(config):
                raise Parsed
            s5p_numerics.s5e_candidate.install = stop
            for l in lines[1:]:
                cols = l.split("\t")
                with self.subTest(task=cols[0]):
                    with self.assertRaises(Parsed), contextlib.redirect_stderr(io.StringIO()):
                        rmp.main(cols[3:])
        finally:
            s5p_numerics.s5e_candidate.install = saved
            rmp.functional_matrix = saved_fm
            os.chdir(cwd)


# ------------------------------------------------------------------------------------------- analysis

class Statistics(unittest.TestCase):
    def F(self, m, n=20, seed=0, c=0.0, f=153):
        rng = np.random.default_rng(seed)
        s = 1e-3 * 10 ** rng.uniform(-0.5, 0.5, f)
        z0 = np.sqrt(c) * rng.normal(size=(n, 1)) + np.sqrt(1 - c) * rng.normal(size=(n, f))
        za = np.sqrt(c) * rng.normal(size=(n, 1)) + np.sqrt(1 - c) * rng.normal(size=(n, f))
        return 1 + m * s * za, 1 + s * z0

    def test_bands_read_in_each_direction(self):
        rng = np.random.default_rng(1)
        for m, want in ((0.0, "R"), (0.05, "R"), (0.4, "P"), (1.0, "C"), (1.6, "C")):
            Fa, F0 = self.F(m)
            self.assertEqual(rma.spread_ratio(Fa, F0, rng)["reading"], want, m)

    def test_an_interval_across_a_band_edge_is_inconclusive(self):
        rng = np.random.default_rng(2)
        Fa, F0 = self.F(0.70, n=6, c=0.9)
        r = rma.spread_ratio(Fa, F0, rng)
        self.assertLess(r["interval_90"][0], rma.C_MIN)
        self.assertEqual(r["reading"], "INCONCLUSIVE")

    def test_zero_spread_functionals_are_excluded_and_too_many_invalidate(self):
        rng = np.random.default_rng(3)
        Fa, F0 = self.F(1.0)
        F0[:, :10] = 1.0
        r = rma.spread_ratio(Fa, F0, rng)
        self.assertEqual(r["excluded"], 10)
        self.assertFalse(r["invalid"])
        F0[:, :20] = 1.0
        self.assertTrue(rma.spread_ratio(Fa, F0, rng)["invalid"])
        self.assertEqual(rma.spread_ratio(Fa, F0, rng)["reading"], "INVALID")

    def test_rules(self):
        R = {"reading": "R", "M": 0.0, "interval_90": [0, 0], "invalid": False}
        P = {"reading": "P", "M": 0.4, "interval_90": [0.3, 0.5], "invalid": False}
        C = {"reading": "C", "M": 1.0, "interval_90": [0.8, 1.2], "invalid": False}
        self.assertEqual(rma.both({"a": R, "b": R}, rma.k1_rule), "SUPPORTED")
        self.assertEqual(rma.both({"a": C, "b": C}, rma.k1_rule), "NOT SUPPORTED")
        self.assertEqual(rma.both({"a": P, "b": P}, rma.k1_rule), "PARTIAL")
        self.assertEqual(rma.both({"a": R, "b": C}, rma.k1_rule), "INCONCLUSIVE")
        self.assertEqual(rma.both({"a": C, "b": C}, rma.k5_rule), "SUPPORTED")
        self.assertEqual(rma.both({"a": R, "b": R}, rma.k5_rule), "NOT SUPPORTED")
        self.assertEqual(rma.k2_rule(P), "SUPPORTED")
        self.assertEqual(rma.k2_rule(dict(P, interval_90=[0.3, 0.71])), "INCONCLUSIVE")
        self.assertEqual(rma.k2_rule(dict(P, M=0.51)), "INCONCLUSIVE")
        self.assertEqual(rma.k2_rule(C), "NOT SUPPORTED")
        self.assertEqual(rma.k3_reading(True, {"a": 9.0, "b": 9.0}), "NOT SUPPORTED")
        self.assertEqual(rma.k3_reading(False, {"a": 0.3, "b": 0.31}), "SUPPORTED")
        self.assertEqual(rma.k3_reading(False, {"a": 0.29, "b": 0.1}), "PARTIAL")
        self.assertEqual(rma.k4_reading({"a": 0.10, "b": 0.2}), "SUPPORTED")
        self.assertEqual(rma.k4_reading({"a": 0.01, "b": 0.0}), "NOT SUPPORTED")
        self.assertEqual(rma.k4_reading({"a": 0.05, "b": 0.05}), "INCONCLUSIVE")
        self.assertEqual(rma.k4_reading({"a": 0.2, "b": 0.0}), "INCONCLUSIVE")

    def test_base_difference(self):
        s0 = np.array([0.01, 0.01, 0.0])
        self.assertEqual(rma.base_difference(np.array([1.0, 1.0, 5.0]), np.ones(3), s0), 0.0)
        self.assertAlmostEqual(rma.base_difference(np.array([1.003, 1.005, 5.0]), np.ones(3), s0), 0.4)

    def test_first_difference(self):
        a = [[["s", 0, 0.5, 1.0, 2], ["l", 0.1, 1], ["l", 0.2, 1]]]
        self.assertEqual(rma.first_difference(a, a)["first_structure_difference"], None)
        b = [[["s", 0, 0.6, 1.0, 2], ["l", 0.1, 1], ["l", 0.2, 1]]]
        r = rma.first_difference(a, b)
        self.assertEqual((r["identical_trees"], r["identical_structure"]), (0, 1))
        c = [[["s", 1, 0.5, 1.0, 2], ["l", 0.1, 1], ["l", 0.2, 1]]]
        r = rma.first_difference(a, c)
        self.assertEqual(r["first_structure_difference"], 0)
        self.assertTrue(r["first_node"]["new_feature"])


def fake_products(runs: Path, arms=None, tamper=None, s_all_differs=False):
    """Products for every declared arm, with A0 equal to the FD-STAB references; returns the references directory and
    SHA256SUMS."""
    rng = np.random.default_rng(11)
    n = 32
    base = rng.uniform(1, 2, n)
    noise = {s: rng.normal(0, 1e-3, n) for s in rmp.SEEDS}
    for arm, cfg in rmp.ARMS.items():
        if arms and arm not in arms:
            continue
        (runs / arm).mkdir(parents=True, exist_ok=True)
        for p in cfg["pairs"]:
            b = p.split(":")[1]
            seed = None if b == "-" else int(b)
            x = base.copy()
            if seed not in (None, 0):
                scale = 0.0 if arm == "V" else 1.0
                x = base * (1 + scale * noise[seed])
                if arm == "S_all" and s_all_differs:
                    x = x * (1 + 1e-12)
            meta = {"construction": "pseudo", "truth": rmp.STABILITY["truth"],
                    "eavail_ratio_sha256": rmp.STABILITY["ratio_sha256"], "pseudo_seed": rmp.STABILITY["pseudo_seed"],
                    "bootstrap_seed": None, "amplitude": rmp.STABILITY["amplitude"], "jitter_seed": seed,
                    "stability_probe": {"candidate": "control"},
                    "rounding_mechanism": {"schema": rmp.SCHEMA, "arm": arm, "jitter_seed": seed}}
            if tamper:
                meta = tamper(arm, seed, meta)
            s = "-" if seed is None else seed
            np.savez(runs / arm / f"rs1_{arm}_b-_j{s}.npz", xsec_flat=x, meta=json.dumps(meta))
    refs = runs.parent / "refs"
    refs.mkdir(exist_ok=True)
    lines = []
    for seed in (None, *rmp.SEEDS):
        s = "-" if seed is None else seed
        src = runs / "A0" / f"rs1_A0_b-_j{s}.npz"
        dst = refs / f"stab_control_b-_j{s}.npz"
        if src.exists():
            shutil.copy(src, dst)
            lines.append(f"{rma.sha256_path(dst)}  runs/control/stability/{dst.name}")
    (runs.parent / "SUMS").write_text("\n".join(lines) + "\n")
    (runs.parent / "log-full").mkdir(exist_ok=True)
    (runs.parent / "log-full" / "DONE").write_text("{}")
    return refs, runs.parent / "SUMS"


class Analysis(unittest.TestCase):
    def args(self, d, refs, sums):
        return type("A", (), {"runs": d / "runs", "fdstab_refs": refs, "fdstab_sums": sums, "s5c_contract": None,
                              "h2_definition": None, "sigma_receipt": None, "out": d / "out.json"})

    def run_read(self, d, refs, sums, readouts=False):
        saved = (rmp.functional_matrix, rma.readouts)
        rmp.functional_matrix = lambda c, h: np.vstack([np.eye(32)] * 6)[:169]
        if not readouts:
            rma.readouts = lambda *a, **k: {}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = rma.read(self.args(d, refs, sums))
        finally:
            rmp.functional_matrix, rma.readouts = saved
        return rc, json.loads((d / "out.json").read_text())

    def test_a_full_fake_run_reads_and_k1_is_supported(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            refs, sums = fake_products(d / "runs")
            rc, out = self.run_read(d, refs, sums)
        self.assertEqual(rc, 0)
        self.assertTrue(all(out["G1"].values()) and all(out["G4"].values()))
        self.assertEqual(out["readings"]["K1"], "SUPPORTED")
        self.assertEqual(out["readings"]["K3"], "NOT SUPPORTED")
        self.assertEqual(out["readings"]["K6"], "NOT TESTABLE")
        self.assertIn("K1", out["supported"])

    def test_no_receipt_grades_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            refs, sums = fake_products(d / "runs")
            (d / "log-full" / "DONE").unlink()
            rc, out = self.run_read(d, refs, sums)
            self.assertEqual((rc, out["status"]), (rma.INCOMPLETE_RC, "INCOMPLETE"))
            (d / "log-full" / "DONE").write_text("{}")
            (d / "log-full" / "FAILED").write_text("rc=1")
            rc, out = self.run_read(d, refs, sums)
        self.assertEqual(out["status"], "INCOMPLETE")

    def test_g1_failure_reads_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            refs, sums = fake_products(d / "runs")
            z = np.load(refs / "stab_control_b-_j5.npz")
            np.savez(refs / "stab_control_b-_j5.npz", xsec_flat=z["xsec_flat"] * (1 + 1e-15), meta=z["meta"])
            lines = [l if "j5.npz" not in l else f"{rma.sha256_path(refs / 'stab_control_b-_j5.npz')}  "
                     "runs/control/stability/stab_control_b-_j5.npz" for l in sums.read_text().splitlines()]
            sums.write_text("\n".join(lines) + "\n")
            rc, out = self.run_read(d, refs, sums)
        self.assertEqual((rc, out["status"]), (rma.STOP_RC, "NOT REPRODUCED"))
        self.assertNotIn("readings", out)

    def test_a_reference_that_is_not_fdstabs_pinned_product_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            refs, sums = fake_products(d / "runs")
            sums.write_text(sums.read_text().replace(sums.read_text()[:8], "00000000", 1))
            with self.assertRaises(SystemExit):
                self.run_read(d, refs, sums)

    def test_g4_failure_leaves_k5_unread(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            refs, sums = fake_products(d / "runs", s_all_differs=True)
            rc, out = self.run_read(d, refs, sums)
        self.assertEqual(rc, 0)
        self.assertFalse(all(out["G4"].values()))
        self.assertTrue(out["readings"]["K5"].startswith("NOT READ"))

    def test_product_refusals(self):
        cases = {
            "wrong arm": lambda arm, s, m: dict(m, rounding_mechanism={**m["rounding_mechanism"], "arm": "X"}),
            "wrong truth": lambda arm, s, m: dict(m, truth="nominal_other"),
            "not control": lambda arm, s, m: dict(m, stability_probe={"candidate": "B2"}),
            "seed mismatch": lambda arm, s, m: dict(m, rounding_mechanism={**m["rounding_mechanism"], "jitter_seed": -1}),
        }
        for name, tamper in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as d:
                d = Path(d)
                fake_products(d / "runs", arms={"V"}, tamper=lambda arm, s, m, t=tamper: t(arm, s, m) if s == 4 else m)
                with self.assertRaises(SystemExit):
                    rma.arm_products(d / "runs", "V")
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            fake_products(d / "runs", arms={"V"})
            self.assertEqual(len(rma.arm_products(d / "runs", "V")), 20)
            (d / "runs" / "V" / "rs1_V_b-_j7.npz").unlink()
            with self.assertRaises(SystemExit):
                rma.arm_products(d / "runs", "V")


class R0(unittest.TestCase):
    def files(self):
        cells = [f"R{c:02d}" for c in range(16)]
        f = np.linspace(1.0, 2.5, 16)
        rel = np.array([0.133] * 14 + [0.055, 0.252]) / 100
        i0 = {"cells": cells, "sigma_J_data": (rel * f).tolist()}
        ce = np.linspace(0.04, 0.08, 16).tolist()
        dp = {"cells": [{"cell": c} for c in cells], "f": f.tolist(), "relative_sigma": {"C_e": ce}}
        stat = np.full(16, 0.0024)
        stat[15] = 0.002  # below sigma_J/f there: R0b undefined
        s1 = {"cells": cells, "relative_sigma": {"C_e": ce, "stat": stat.tolist()}}
        return i0, dp, s1

    def test_r0_reads_with_its_controls_and_an_undefined_cell(self):
        rec = rma.r0(*self.files())
        self.assertAlmostEqual(rec["R0a"][0], 0.00133 / 0.0024)
        self.assertEqual(rec["R0b_undefined_cells"], ["R15"])
        self.assertIsNone(rec["R0b"][15])
        self.assertIsNone(rec["R0b_summary"])
        self.assertAlmostEqual(rec["R0b"][0], 0.00133 / np.sqrt(0.0024 ** 2 - 0.00133 ** 2))

    def test_each_control_refuses(self):
        i0, dp, s1 = self.files()
        with self.assertRaises(SystemExit):
            rma.r0(dict(i0, cells=list(reversed(i0["cells"]))), dp, s1)
        with self.assertRaises(SystemExit):
            rma.r0(i0, dict(dp, relative_sigma={"C_e": [v * 1.001 for v in dp["relative_sigma"]["C_e"]]}), s1)
        with self.assertRaises(SystemExit):
            rma.r0(i0, dict(dp, f=[v * 1.1 for v in dp["f"]]), s1)  # sigma_J/f no longer reproduces I0's 0.133


# ------------------------------------------------------------------------------------------- job script

class JobScript(unittest.TestCase):
    """sbatch_rs1.sh run locally on a stand-in deploy whose runner writes one product per task."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.D, self.OUT, self.stub = t / "deploy", t / "out", t / "stub"
        (self.D / "nd-unfolding").mkdir(parents=True)
        self.stub.mkdir()
        (self.stub / "lightgbm.py").write_text("__version__ = 'stub'\n")
        (self.stub / "scipy.py").write_text("")
        (self.D / "setup_salloc_env.sh").write_text(f"export PYTHONPATH={self.stub}\n")
        (self.D / "nd-unfolding" / "runner.py").write_text(
            "import sys, pathlib\n"
            "if 'FAIL' in sys.argv: sys.exit(3)\n"
            "out = pathlib.Path(sys.argv[sys.argv.index('--out') + 1]); out.mkdir(parents=True, exist_ok=True)\n"
            "(out / (sys.argv[1] + '.npz')).write_text('p')\n")
        subprocess.run(["git", "init", "-q", str(self.D)], check=True)
        subprocess.run(["git", "-C", str(self.D), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.D), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "d"],
                       check=True)
        self.pin = subprocess.run(["git", "-C", str(self.D), "rev-parse", "HEAD"], capture_output=True, text=True,
                                  check=True).stdout.strip()
        self.OUT.mkdir()
        self.time = t / "time.sh"
        self.time.write_text('#!/bin/bash\nshift 3\nexec "$@"\n')
        self.time.chmod(0o755)

    def tearDown(self):
        self.tmp.cleanup()

    def queue(self, name, ids, fail=()):
        rows = ["# id\tunfolds\tscript\targv"]
        for i in ids:
            argv = [i, "--out", str(self.OUT / "runs" / "A0")] + (["FAIL"] if i in fail else [])
            rows.append("\t".join([i, "1", "runner.py", *argv]))
        (self.OUT / name).write_text("\n".join(rows) + "\n")

    def job(self, mode, pin=None):
        env = dict(os.environ, RS1_TIME_BIN=str(self.time))
        return subprocess.run(["bash", str(ND / "sbatch_rs1.sh"), mode, str(self.D), pin or self.pin, str(self.OUT)],
                              capture_output=True, text=True, env=env)

    def test_dry_then_full_skips_the_dry_tasks_and_writes_done(self):
        self.queue("dry.tsv", ["a", "b"])
        self.queue("queue.tsv", ["a", "b", "c", "d"])
        self.assertEqual(self.job("dry").returncode, 0)
        self.assertTrue((self.OUT / "log-dry" / "DONE").exists())
        (self.OUT / "runs" / "A0" / "a.npz").write_text("dry product")
        r = self.job("full")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.OUT / "runs" / "A0" / "a.npz").read_text(), "dry product")
        self.assertTrue((self.OUT / "log-full" / "DONE").exists())
        self.assertFalse((self.OUT / "log-full" / "tasks" / "a.log").exists())
        self.assertIn("runs/A0/c.npz", (self.OUT / "log-full" / "SHA256SUMS").read_text())

    def test_full_refuses_without_a_dry_receipt(self):
        self.queue("dry.tsv", ["a"])
        self.queue("queue.tsv", ["a", "b"])
        r = self.job("full")
        self.assertEqual(r.returncode, 2)
        self.assertFalse((self.OUT / "log-full").exists())

    def test_a_failed_task_leaves_no_receipt(self):
        self.queue("dry.tsv", ["a", "b"], fail=("b",))
        self.assertEqual(self.job("dry").returncode, 1)
        self.assertTrue((self.OUT / "log-dry" / "FAILED").exists())
        self.assertFalse((self.OUT / "log-dry" / "DONE").exists())
        self.assertTrue((self.OUT / "log-dry" / "SHA256SUMS").exists())

    def test_an_existing_log_and_a_wrong_pin_are_refused(self):
        self.queue("dry.tsv", ["a"])
        (self.OUT / "log-dry").mkdir()
        self.assertEqual(self.job("dry").returncode, 2)
        shutil.rmtree(self.OUT / "log-dry")
        self.assertEqual(self.job("dry", pin="0" * 40).returncode, 2)
        self.assertEqual(self.job("dry").returncode, 0)

    def test_a_dirty_deploy_is_refused(self):
        self.queue("dry.tsv", ["a"])
        (self.D / "nd-unfolding" / "runner.py").write_text("changed\n")
        self.assertEqual(self.job("dry").returncode, 2)


class DeclaredConstants(unittest.TestCase):
    def test_constants_match_the_declaration(self):
        self.assertEqual(rmp.SEEDS, tuple(range(1, 21)))
        self.assertEqual(rmp.UNJITTERED_F64, 0)
        self.assertNotIn(0, esp.JITTER_SEEDS)
        self.assertEqual(sum(len(c["pairs"]) for c in rmp.ARMS.values()), 229)
        self.assertEqual((rma.R_MAX, rma.C_MIN, rma.N_BOOT, rma.BOOT_SEED), (0.10, 0.70, 2000, 20261106))
        self.assertEqual((rma.K2_POINT, rma.K2_UPPER, rma.K3_SUPPORTED, rma.K4_SUPPORTED, rma.K4_NOT),
                         (0.5, 0.7, 0.3, 0.10, 0.01))
        self.assertEqual(rmp.STABILITY["pseudo_seed"], 990000)
        self.assertEqual(rma.I0_PRINTED, (0.133, 0.055, 0.252))


if __name__ == "__main__":
    unittest.main()
