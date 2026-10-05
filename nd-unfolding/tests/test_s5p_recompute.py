"""Controls for the independent s5p evaluator (s5p_recompute): library known answers from the specification and
the reviews' own numbers, exchangeability (size), the variant and claim rules, Holm with determinacy, the
sequential stopping rule, and end-to-end runs on a synthetic world in the production file formats covering
incomplete products, budget-terminal stops, keyed draws and determinism."""
import ast
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(1, str(HERE.parent))
sys.path.insert(1, str(HERE))
import s5p_recompute as R  # noqa: E402
from s5p_recompute_toy import SEED_BASE, Toy  # noqa: E402

THR = R.decision_thresholds(0.05, 10)


class Independence(unittest.TestCase):
    def test_imports_nothing_from_the_production_evaluator(self):
        for name in ("s5p_recompute.py", "s5p_recompute_compare.py"):
            tree = ast.parse((HERE.parent / name).read_text())
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    mods |= {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            self.assertFalse(mods & {"s5p_joint", "s5p_inference", "s5p_seqstop"}, name)


class ClopperPearson(unittest.TestCase):
    def test_k0_closed_form(self):
        for n in (1, 200, 1999):
            self.assertAlmostEqual(R.cp_interval(0, n)[1], 1 - 0.025 ** (1 / n), places=12)
            self.assertEqual(R.cp_interval(0, n)[0], 0.0)
            self.assertEqual(R.cp_interval(n, n)[1], 1.0)

    def test_review1_interval_at_p_001(self):
        lo, hi = R.cp_interval(19, 1999)  # p = 20/2000
        self.assertAlmostEqual(lo, 0.0057, places=4)
        self.assertAlmostEqual(hi, 0.0148, places=4)

    def test_review2_m3_counts(self):
        det = lambda B: [k for k in range(10) if R.cp_interval(k, B)[1] < 0.005]  # noqa: E731
        rank = lambda B: [k for k in range(10) if R.mc_p(k, B) <= 0.005]  # noqa: E731
        self.assertEqual(det(800), [0])
        self.assertEqual(rank(800), [0, 1, 2, 3])
        self.assertEqual(det(1999), [0, 1, 2, 3])

    def test_k0_at_0005_needs_736(self):
        # amendment 7 states B >= 737; the exact two-sided 95% interval already allows 736 (recorded in the handoff)
        self.assertGreater(R.cp_interval(0, 735)[1], 0.005)
        self.assertLess(R.cp_interval(0, 736)[1], 0.005)

    def test_empty(self):
        self.assertEqual(R.cp_interval(0, 0), (0.0, 1.0))


class Statistics(unittest.TestCase):
    def setUp(self):
        r = np.random.default_rng(1)
        a = r.standard_normal((9, 9))
        self.W = a @ a.T + 9 * np.eye(9)
        self.mu = r.uniform(1, 2, 9)
        self.f = self.mu * (1 + 0.1 * r.standard_normal(9))

    def test_total_is_the_inverse_quadratic_form(self):
        r = self.f - self.mu
        from scipy import linalg
        ch = linalg.cho_factor(self.W, lower=True)
        self.assertAlmostEqual(R.t_total(r, ch), r @ np.linalg.inv(self.W) @ r, places=10)
        stack = np.vstack([r, 2 * r])
        np.testing.assert_allclose(R.t_total(stack, ch), [r @ np.linalg.inv(self.W) @ r * m for m in (1, 4)])

    def test_shape_invariances(self):
        t = R.t_shape(self.f, self.mu, self.W)
        self.assertAlmostEqual(R.t_shape(self.mu * 3.0, self.mu, self.W), 0.0, places=20)
        perm = np.r_[1:9, 0]  # a different cell becomes the dropped last one
        self.assertAlmostEqual(R.t_shape(self.f[perm], self.mu[perm], self.W[np.ix_(perm, perm)]), t, places=8)
        # scaling f and W together (a unit change) leaves the shape statistic unchanged
        self.assertAlmostEqual(R.t_shape(5 * self.f, self.mu, 25 * self.W), t, places=8)

    def test_rank_counts_ties_count(self):
        self.assertEqual(list(R.rank_counts([1.0, 2.0, 5.0], [1.0, 1.0, 2.0, 3.0])), [4, 2, 0])


class Holm(unittest.TestCase):
    def e(self, name, k, B):
        return {"test": name, "k": k, "B": B, "p": R.mc_p(k, B)}

    def test_rejections_then_undetermined_stop(self):
        ents = [self.e("a", 0, 1999), self.e("b", 0, 1999), self.e("c", 9, 1999), self.e("d", 400, 1999)]
        out = R.holm_determined(ents, 0.05)
        # c: p = 0.005 against 0.05/2 = 0.025; its interval [0.0021, 0.0085] lies below -> rejected
        self.assertEqual([o["decision"] for o in out], ["rejected", "rejected", "rejected", "not rejected"])
        ents = [self.e("a", 0, 1999), self.e("b", 50, 1999), self.e("c", 60, 1999)]
        out = R.holm_determined(ents, 0.05)
        # b: the interval of 50/1999, [0.019, 0.033], contains 0.05/2 -> undetermined; c inherits it although its
        # own interval [0.023, 0.038] lies below its threshold 0.05
        self.assertEqual([o["decision"] for o in out], ["rejected", "undetermined", "undetermined"])
        ents = [self.e("a", 0, 1999), self.e("b", 20, 1999)]  # [0.0061, 0.0154] below 0.025: rejected
        self.assertEqual([o["decision"] for o in R.holm_determined(ents, 0.05)], ["rejected", "rejected"])

    def test_not_rejected_stops_every_later_test(self):
        ents = [self.e("a", 1500, 1999), self.e("b", 0, 1999), self.e("c", 1900, 1999)]
        out = R.holm_determined(ents, 0.05)
        self.assertEqual([o["decision"] for o in out], ["not rejected", "rejected", "not rejected"])
        self.assertEqual(out[1]["threshold"], 0.05 / 3)

    def test_point_holm_differs_from_determined(self):
        ents = [self.e("a", 3, 800)]  # p = 0.005 <= 0.05 but also the determinacy check at m = 1
        self.assertEqual(R.holm_point(ents, 0.05), ["rejected"])
        ents = [self.e("a", 3, 800), self.e("b", 3, 800)]
        self.assertEqual(R.holm_point(ents, 0.01), ["rejected", "rejected"])
        self.assertEqual([o["decision"] for o in R.holm_determined(ents, 0.01)], ["undetermined", "undetermined"])

    def test_uncalibrated_null_is_undetermined_at_its_step(self):
        ents = [self.e("a", 0, 1999), {"test": "b", "k": 0, "B": 0, "p": 1.0}]
        self.assertEqual([o["decision"] for o in R.holm_determined(ents, 0.05)], ["rejected", "undetermined"])


class Sequential(unittest.TestCase):
    def test_review_described_stops(self):
        self.assertTrue(R.sequential_stop(190, 200, THR)["stop"])       # p ~ 0.95 at 200
        self.assertTrue(R.sequential_stop(40, 400, THR)["stop"])        # p ~ 0.1 at 400
        self.assertTrue(R.sequential_stop(0, 1200, THR)["stop"])        # below every threshold
        self.assertFalse(R.sequential_stop(0, 200, THR)["stop"])        # straddles the Holm levels
        self.assertFalse(R.sequential_stop(9, 1999, THR)["stop"])       # p = 0.005 on a threshold
        self.assertFalse(R.sequential_stop(0, 0, THR)["stop"])

    def test_precision_branch(self):
        # p ~ 0.5 at B = 200: no threshold inside, half-width ~0.09 > 0.05 -> continue
        s = R.sequential_stop(100, 200, THR)
        self.assertFalse(s["straddled"])
        self.assertFalse(s["t7_precise"])
        self.assertFalse(s["stop"])

    def test_thresholds(self):
        self.assertEqual(len(THR), 10)
        self.assertIn(0.01, THR)
        self.assertAlmostEqual(min(THR), 0.005)


class Variants(unittest.TestCase):
    def setUp(self):
        from scipy import linalg
        r = np.random.default_rng(3)
        n = 6
        self.mu = np.ones(n)
        self.ts = R.TestSetup(dom=np.arange(n), mu=self.mu, var_mu=np.zeros(n), w=np.eye(n),
                              w_chol=linalg.cho_factor(np.eye(n), lower=True))
        self.b = np.array([1.0, 0, 0, 0, 0, 0])
        self.F = self.mu + self.b + 0.01 * r.standard_normal((50, n))
        self.F -= self.F.mean(0) - (self.mu + self.b)

    def test_aligned_pairs_give_positive_magnitude_along_b(self):
        d = np.tile([0.1, 0, 0, 0, 0, 0], (16, 1)) + 0.01 * np.random.default_rng(4).standard_normal((16, 6))
        sh = R.bias_aligned_shift(self.F, self.ts, d)
        self.assertGreater(sh["magnitude"], 0.1)
        np.testing.assert_allclose(sh["S"] / sh["magnitude"], self.b, atol=1e-12)

    def test_anti_aligned_pairs_give_zero(self):
        d = np.tile([-0.1, 0, 0, 0, 0, 0], (16, 1)) + 0.001 * np.random.default_rng(4).standard_normal((16, 6))
        self.assertEqual(R.bias_aligned_shift(self.F, self.ts, d)["magnitude"], 0.0)

    def test_variant_sets(self):
        S, dm = np.ones(3), np.full(3, 2.0)
        u = R.variant_shifts(S, dm, [0, 0.5, 1], 2, "union")
        self.assertEqual(sorted(u), ["c=0", "c=0.5", "c=1", "m1=+2", "m1=-2"])
        np.testing.assert_allclose(u["m1=-2"], -4.0)
        self.assertEqual(len(R.variant_shifts(S, dm, [0, 0.5, 1], 2, "product")), 9)
        self.assertEqual(sorted(R.variant_shifts(S, None, [0, 0.5, 1], None, "union")), ["c=0", "c=0.5", "c=1"])
        self.assertEqual(len(R.variant_shifts(S, None, [0, 0.5, 1], None, "product")), 3)

    def test_claim_is_the_largest_count(self):
        ens = {"c=0": {"total": np.array([1.0, 2, 3, 4])}, "c=1": {"total": np.array([3.0, 4, 5, 6])}}
        c = R.claim(3.5, ens, "total")
        self.assertEqual((c["variants"]["c=0"]["k"], c["variants"]["c=1"]["k"], c["k"]), (1, 3, 3))
        self.assertEqual(c["p"], 4 / 5)


class Size(unittest.TestCase):
    def test_rank_p_is_valid_under_exchangeability(self):
        """Observed and null draws from one process: P(p <= a) <= a for the unshifted test and the claim."""
        from scipy import linalg
        r = np.random.default_rng(11)
        n, B, reps = 5, 99, 1500
        W = np.eye(n) + 0.3
        ch = linalg.cho_factor(W, lower=True)
        ts = R.TestSetup(dom=np.arange(n), mu=np.full(n, 10.0), var_mu=np.zeros(n), w=W, w_chol=ch)
        L = np.linalg.cholesky(W)
        rej = {"total": 0, "shape": 0, "claim": 0}
        for _ in range(reps):
            F = 10.0 + (L @ r.standard_normal((n, B + 1))).T
            eps = np.zeros_like(F)
            ens = R.null_ensembles(F[1:], eps[1:], ts, {"c=0": np.zeros(n), "c=1": 0.2 * np.ones(n)})
            obs = R.stats_of(F[0], ts.mu, ts)
            for t in ("total", "shape"):
                rej[t] += R.claim(obs[t], {"c=0": ens["c=0"]}, t)["p"] <= 0.05
            rej["claim"] += R.claim(obs["total"], ens, "total")["p"] <= 0.05
        se = np.sqrt(0.05 * 0.95 / reps)
        for t in ("total", "shape"):
            self.assertLess(rej[t] / reps, 0.05 + 3 * se, t)
            self.assertGreater(rej[t] / reps, 0.05 - 3 * se, t)
        self.assertLessEqual(rej["claim"], rej["total"] + 0)  # the claim can only be more conservative


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="s5p_recompute_"))
        self.t = Toy(self.dir / "w")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_eval(self, **kw):
        return R.evaluate(self.t.design(**kw), self.t.v_path, self.t.contract, log=lambda *a: None)

    def test_known_answer_without_surrogates(self):
        t = self.t
        for b in t.lat:  # identical endpoints: Delta = 0
            t.lat[b][1] = t.lat[b][0]
        base = t.truth["MnvTune_v1"]
        t.jitters = [t.npz(f"jit0/j{j}.npz", xsec_flat=base) for j in range(20)]  # s_num = 0
        t.pred["MnvTune_v1"] = t.npz("pred0.npz", xsec_flat=base, sumw2_flat=np.zeros_like(base), **t.edges())
        x = base * (1 + 0.02 * np.random.default_rng(5).standard_normal(base.size))
        t.set_data(x)
        t.calibration("MnvTune_v1", 30)
        t.calibration("GiBUU_2019", 30)
        out = self.run_eval()
        r = t.jint(x) - t.jint(base)
        expect = r @ np.linalg.inv(t.V) @ r
        self.assertAlmostEqual(out["nulls"]["MnvTune_v1"]["observed_T"]["total"] / expect, 1.0, places=10)

    def test_domain_is_pz_index_le_1(self):
        t = self.t
        t.calibration("MnvTune_v1", 20)
        t.calibration("GiBUU_2019", 20)
        out = self.run_eval()
        pz = [np.unravel_index(c, [3] * 5)[1] for c in t.supported]
        self.assertEqual(out["nulls"]["GiBUU_2019"]["domain_cells"], sum(1 for p in pz if p <= 1))
        self.assertEqual(out["nulls"]["MnvTune_v1"]["domain_cells"], len(t.supported))

    def test_incomplete_products_are_reported_and_partials_excluded(self):
        t = self.t
        t.calibration("MnvTune_v1", 60, skip=(7, 33))
        t.product("cal", "MnvTune_v1", SEED_BASE["MnvTune_v1"] + 60, t.truth["MnvTune_v1"], partial=True)
        t.product("cal", "MnvTune_v1", SEED_BASE["MnvTune_v1"] + 75, t.truth["MnvTune_v1"])  # beyond final B
        t.status("MnvTune_v1", 60, True, "budget")
        t.calibration("GiBUU_2019", 20)
        out = self.run_eval()
        cal = out["nulls"]["MnvTune_v1"]["calibration"]
        b = SEED_BASE["MnvTune_v1"]
        self.assertEqual(cal["partials_excluded"], 1)
        # A13 (revised): every finished product is used, the one beyond the final B included; the count mismatch
        # against the final status is reported, not repaired
        self.assertEqual(cal["products_used"], 59)
        self.assertEqual(out["nulls"]["MnvTune_v1"]["B"], 59)
        self.assertFalse(cal["count_matches_final_B"])
        self.assertEqual(cal["count_mismatch"], {"final_status_B": 60, "products": 59})
        gaps = cal["seed_gaps"]
        self.assertEqual(gaps["span"], [b, b + 200])  # the B = 0 look continued: one batch submitted
        self.assertEqual(gaps["span_basis"], {"looks_with_stop_false": 1, "last_batch_holding_a_product": 1,
                                              "used": "looks"})
        self.assertEqual(gaps["missing_seeds"], sorted({b + 7, b + 33, b + 60} | set(range(b + 61, b + 75))
                                                       | set(range(b + 76, b + 200))))
        self.assertEqual(gaps["seeds_outside_submitted_batches"], [])

    def test_budget_stop_at_zero_is_not_calibrated(self):
        t = self.t
        t.status("GiBUU_2019", 0, True, "budget")
        t.calibration("MnvTune_v1", 400)
        base = t.truth["MnvTune_v1"]
        t.set_data(base * np.repeat(np.linspace(0.8, 1.2, 4), base.size // 4))  # MnvTune rejected first
        out = self.run_eval()
        g = out["nulls"]["GiBUU_2019"]
        self.assertEqual(g["B"], 0)
        self.assertEqual(g["tests"]["total"]["p"], 1.0)
        labels = {d["test"]: d for d in out["family"]["decisions"]}
        self.assertEqual(labels["GiBUU_2019:total"].get("label"), "not calibrated")
        self.assertEqual(labels["MnvTune_v1:total"]["decision"], "rejected")
        self.assertEqual(labels["GiBUU_2019:total"]["decision"], "undetermined")
        self.assertEqual(labels["GiBUU_2019:shape"]["decision"], "undetermined")

    def test_draws_are_keyed_by_seed(self):
        t = self.t
        t.calibration("MnvTune_v1", 50)
        t.calibration("GiBUU_2019", 10)
        ev = R.Evaluator(t.design(), t.v_path, t.contract, log=lambda *a: None)
        prods = ev.load_ensemble(t.design()["nulls"]["MnvTune_v1"]["calibration_glob"])
        a = ev.null_context("MnvTune_v1", prods)
        b = ev.null_context("MnvTune_v1", prods[::-1][:20])
        by_seed = {p.seed: i for i, p in enumerate(prods)}
        for j, p in enumerate(prods[::-1][:20]):
            np.testing.assert_array_equal(b["f_cal"][j], a["f_cal"][by_seed[p.seed]])
            np.testing.assert_array_equal(b["eps"][j], a["eps"][by_seed[p.seed]])

    def test_pseudo_seed_mismatch_is_refused(self):
        t = self.t
        p = t.product("cal", "MnvTune_v1", SEED_BASE["MnvTune_v1"], t.truth["MnvTune_v1"])
        z = dict(np.load(p))
        meta = json.loads(str(z["meta"]))
        meta["pseudo_seed"] = 5
        z["meta"] = np.array(json.dumps(meta))
        np.savez(p, **z)
        t.calibration("GiBUU_2019", 5)
        with self.assertRaises(SystemExit):
            self.run_eval()

    def test_declared_digest_is_enforced(self):
        t = self.t
        t.calibration("MnvTune_v1", 10)
        t.calibration("GiBUU_2019", 10)
        d = t.design()
        d["process_shift"]["MnvTune_v1"]["sha256"] = "0" * 64
        with self.assertRaises(SystemExit):
            R.evaluate(d, t.v_path, t.contract, log=lambda *a: None)

    def test_deterministic(self):
        t = self.t
        t.calibration("MnvTune_v1", 40)
        t.calibration("GiBUU_2019", 40)
        a = json.dumps(R.jsonable(self.run_eval()), sort_keys=True)
        b = json.dumps(R.jsonable(self.run_eval()), sort_keys=True)
        self.assertEqual(a, b)

    def test_rejection_power_and_incomplete_power_set(self):
        t = self.t
        base = t.truth["MnvTune_v1"]
        t.calibration("MnvTune_v1", 400)
        t.calibration("GiBUU_2019", 200)
        t.status("MnvTune_v1", 400, True, "maximum reached")
        t.status("GiBUU_2019", 200, True, "rule met for both tests")
        factor = np.repeat(np.linspace(0.8, 1.2, 4), base.size // 4)  # a pT-ordered tilt
        t.set_data(base * factor)
        t.power("P1_a1.0", 30, "MnvTune_v1", factor)
        spec = {"P1_a1.0": {"glob": str(t.root / "pow/P1_a1.0/pow_P1_a1.0_s*.npz"), "surrogate_seed0": 1951000,
                            "n": 40, "null": "MnvTune_v1"}}
        out = self.run_eval(power=spec)
        dec = {d["test"]: d["decision"] for d in out["family"]["decisions"]}
        self.assertEqual(dec["MnvTune_v1:total"], "rejected")
        self.assertEqual(dec["MnvTune_v1:shape"], "rejected")
        pw = out["power"]["P1_a1.0"]
        self.assertFalse(pw["complete"])
        self.assertEqual(pw["n_present"], 30)
        self.assertEqual(pw["shape"]["0.05"]["rank_unshifted"]["power"], 1.0)
        # at B = 400 a determined rejection at 0.005 needs k = 0 and B >= 736: power is zero by construction
        self.assertEqual(pw["shape"]["0.005"]["determined_claim"]["count"], 0)
        self.assertEqual(pw["shape"]["0.005"]["rank_claim"]["power"], 1.0)

    def test_sequential_looks_pair_with_status_and_respect_min_B(self):
        t = self.t
        base = t.truth["MnvTune_v1"]
        t.calibration("MnvTune_v1", 600)
        t.calibration("GiBUU_2019", 20)
        for B in (200, 400):
            t.status("MnvTune_v1", B, False, "continue")
        t.status("MnvTune_v1", 600, True, "rule met for both tests")
        t.set_data(base * np.repeat(np.linspace(0.7, 1.3, 4), base.size // 4))
        out = self.run_eval(mins={"MnvTune_v1": 400})
        seq = out["nulls"]["MnvTune_v1"]["sequential"]
        self.assertEqual([lk["B"] for lk in seq["looks"]], [200, 400, 600])
        self.assertTrue(all(lk["status_file"] for lk in seq["looks"]))
        lk200 = seq["looks"][0]
        self.assertTrue(lk200["below_min_B"])
        self.assertFalse(lk200["rule_stops"])
        # k = 0 everywhere. The toy family has m = 4 tests, so the smallest Holm level is 0.0125: at B = 400 the
        # 99.5% upper end 0.0149 straddles it, at B = 600 (0.0099) every threshold lies above -> the rule stops
        self.assertEqual([lk["rule_stops"] for lk in seq["looks"]], [False, False, True])
        self.assertEqual(seq["first_look_where_rule_stops"], 600)
        self.assertEqual(seq["looks"][2]["status"]["reason"], "rule met for both tests")
        self.assertEqual(out["nulls"]["MnvTune_v1"]["tests"]["total"]["k"], 0)


def withdrawn_a13_selection(seed_hi: dict):
    """The selection in force at 1bfd8910 (seeds restricted to [base, base + final B)), for the mutation control."""
    def load(self, pattern):
        key = next(k for k, s in self.design["nulls"].items() if s["calibration_glob"] == pattern)
        return [p for p in load_ensemble_fixed(self, pattern) if p.seed < seed_hi.get(key, float("inf"))]
    return load


load_ensemble_fixed = R.Evaluator.load_ensemble


class SeedGaps(unittest.TestCase):
    """s5p-F4: lost seeds leave gaps; the ensemble is every finished product (amendment 7), not a seed range.

    A null with two batches (seeds base .. base + 399): base + 5, base + 17 and base + 203 have no product, base + 17
    a partial; looks B = 0 and 198 continue, the final status has B = 397. A power set is judged against this null.
    """

    NULL = "MnvTune_v1"

    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp(prefix="s5p_recompute_gaps_"))
        t = cls.t = Toy(cls.dir / "w")
        b = cls.base = SEED_BASE[cls.NULL]
        # surrogates off for a known answer: Delta = 0, s_num = 0, Var(mu) = 0 (the normalization z stays)
        for band in t.lat:
            t.lat[band][1] = t.lat[band][0]
        truth = t.truth[cls.NULL]
        t.jitters = [t.npz(f"jit0/j{j}.npz", xsec_flat=truth) for j in range(20)]
        t.pred[cls.NULL] = t.npz("pred0.npz", xsec_flat=truth, sumw2_flat=np.zeros_like(truth), **t.edges())
        t.set_data(truth + t.fine_noise(np.random.default_rng(31), truth * t.noise))  # a typical T: k inside (0, B)
        t.calibration(cls.NULL, 400, skip=(5, 17, 203))
        t.product("cal", cls.NULL, b + 17, truth, partial=True)
        t.status(cls.NULL, 0, False, "no calibration product yet")
        t.status(cls.NULL, 198, False, "continue")
        t.status(cls.NULL, 397, True, "batches exhausted")
        t.calibration("GiBUU_2019", 20)
        t.power("P1_a1.0", 12, cls.NULL, 1.0)
        cls.power = {"P1_a1.0": {"glob": str(t.root / "pow/P1_a1.0/pow_P1_a1.0_s*.npz"), "surrogate_seed0": 1951000,
                                 "n": 12, "null": cls.NULL}}
        cls.out = R.evaluate(t.design(power=cls.power), t.v_path, t.contract, log=lambda *a: None)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def brute_unshifted(self, seeds):
        """k, B, p of the unshifted test from the product files, written from the specification (no evaluator)."""
        t, b = self.t, self.base
        chol = np.linalg.cholesky(t.V)
        tq = lambda r: float(np.sum(np.linalg.solve(chol, r) ** 2))  # noqa: E731
        with np.load(t.data) as z:
            t_obs = tq(t.jint(z["xsec_flat"]) - t.jint(t.truth[self.NULL]))
        k = 0
        for s in seeds:
            with np.load(t.root / f"cal/{self.NULL}/cal_{self.NULL}_s{s}.npz") as z:
                f = t.jint(z["xsec_flat"]) * (1 + 0.014 * json.loads(str(z["meta"]))["nuisance_draw"]["normalization_z"])
            k += tq(f - t.jint(t.truth[self.NULL])) >= t_obs
        return k, len(seeds), (k + 1) / (len(seeds) + 1)

    def failures(self, out):
        """Every assertion of the correction, as a list (empty = the corrected selection); the mutation reuses it."""
        b, bad = self.base, []
        rec = out["nulls"][self.NULL]
        cal, seq = rec["calibration"], rec["sequential"]
        expect = [s for s in range(b, b + 400) if s not in (b + 5, b + 17, b + 203)]
        if rec["B"] != 397 or cal["products_used"] != 397:
            bad.append(f"ensemble B {rec['B']} (products_used {cal['products_used']}), expected 397")
        if cal["count_matches_final_B"] is not True or cal["count_mismatch"] is not None:
            bad.append("count against the final status B = 397 not matched")
        if [lk["B"] for lk in seq["looks"]] != [198, 397]:
            bad.append(f"look B {[lk['B'] for lk in seq['looks']]}, expected [198, 397]")
        if not all(lk["status_file"] and lk["status"]["B"] == lk["B"] for lk in seq["looks"]):
            bad.append("a look is not paired with the status file of its B")
        if seq["batches_adding_no_product"] or seq["final_look_is_final_B"] is not True:
            bad.append(f"batches adding no product {seq['batches_adding_no_product']}, final look is final B "
                       f"{seq['final_look_is_final_B']}")
        if seq["status_files_without_a_look"]:
            bad.append(f"status files without a look {seq['status_files_without_a_look']}")
        gaps = cal["seed_gaps"]
        if gaps["missing_seeds"] != [b + 5, b + 17, b + 203] or gaps["span"] != [b, b + 400]:
            bad.append(f"gap report {gaps['missing_seeds']} over {gaps['span']}")
        if gaps["seeds_outside_submitted_batches"]:
            bad.append("seeds reported outside the submitted batches")
        k, B, p = self.brute_unshifted(expect)
        for t in ("total",):
            u = rec["tests"][t]["unshifted"]
            if (u["k"], rec["tests"][t]["B"], u["p"]) != (k, B, p):
                bad.append(f"{t} unshifted (k, B, p) {(u['k'], rec['tests'][t]['B'], u['p'])} != brute {(k, B, p)}")
        if out["power"]["P1_a1.0"].get("B_null") != 397:
            bad.append(f"power judged against B_null {out['power']['P1_a1.0'].get('B_null')}, expected 397")
        return bad

    def test_ensemble_looks_gaps_and_power_follow_the_frozen_definition(self):
        self.assertEqual(self.failures(self.out), [])

    def test_the_seeds_beyond_the_final_B_are_used(self):
        b = self.base
        seeds = sorted(R.seed_of(p) for p in R.finished_products(self.t.design()["nulls"][self.NULL]["calibration_glob"]))
        self.assertEqual(seeds[-3:], [b + 397, b + 398, b + 399])
        self.assertEqual(len(seeds), 397)
        self.assertEqual(self.out["nulls"][self.NULL]["calibration"]["partials_excluded"], 1)

    def test_known_answer_is_discriminating(self):
        k, B, _ = self.brute_unshifted([s for s in range(self.base, self.base + 400)
                                        if s not in (self.base + 5, self.base + 17, self.base + 203)])
        self.assertTrue(0 < k < B, k)  # an extreme T_obs would make k = 0 whatever the ensemble

    def test_control_the_withdrawn_selection_goes_red(self):
        # the withdrawn SELECTION under the corrected look loop (1bfd8910's own loop repeated B = 394 nine times)
        from unittest import mock
        b = self.base
        with mock.patch.object(R.Evaluator, "load_ensemble", withdrawn_a13_selection({self.NULL: b + 397})):
            out = R.evaluate(self.t.design(power=self.power), self.t.v_path, self.t.contract, log=lambda *a: None)
        self.assertEqual(out["nulls"][self.NULL]["B"], 394)
        bad = self.failures(out)
        joined = "\n".join(bad)
        for part in ("ensemble B 394", "not matched", "look B [198, 394]", "B_null 394"):
            self.assertIn(part, joined)

    def test_a_trailing_batch_without_products_gets_no_look(self):
        """Batch 1 launched after the B = 198 look but holding no product (still running, or refused by the meter and
        then a 'budget' final status written without rewriting the look file): one look, nothing listed. The gap
        diagnostic counts batch 1 as submitted (documented: a budget refusal is not visible in the look files)."""
        for final in (None, "budget"):
            with self.subTest(final=final):
                t = Toy(self.dir / f"w-nonew-{final}")
                t.calibration(self.NULL, 200, skip=(5, 17))
                t.status(self.NULL, 198, False, "continue")
                if final:
                    (t.root / "status" / f"{self.NULL}-final.json").write_text(
                        json.dumps({"null": self.NULL, "B": 198, "max": 1999, "stop": True, "reason": final}))
                t.calibration("GiBUU_2019", 20)
                out = R.evaluate(t.design(), t.v_path, t.contract, log=lambda *a: None)
                seq = out["nulls"][self.NULL]["sequential"]
                self.assertEqual([lk["B"] for lk in seq["looks"]], [198])
                self.assertEqual(seq["batches_adding_no_product"], [])
                self.assertEqual(seq["status_files_without_a_look"], [])
                self.assertEqual(seq["final_look_is_final_B"], True if final else None)
                self.assertEqual(out["nulls"][self.NULL]["calibration"]["seed_gaps"]["batches_submitted"], 2)

    def lost_batches_world(self, name, lost, final_B, reason, statuses, drop_b0=False):
        """k = 0 at every look (m = 4: the rule first stops at B = 600); `lost` batches have no product at all."""
        t = Toy(self.dir / name)
        truth = t.truth[self.NULL]
        t.set_data(truth * np.repeat(np.linspace(0.7, 1.3, 4), truth.size // 4))
        n_seeds = 200 * (final_B // 200 + len(lost))
        t.calibration(self.NULL, n_seeds, skip={i for bt in lost for i in range(200 * bt, 200 * bt + 200)})
        for B in statuses:  # a repeated look at one B writes one file
            t.status(self.NULL, B, False, "continue")
        t.status(self.NULL, final_B, True, reason)
        if drop_b0:
            (t.root / "status" / f"{self.NULL}-B0.json").unlink()
        t.calibration("GiBUU_2019", 20)
        return R.evaluate(t.design(), t.v_path, t.contract, log=lambda *a: None)["nulls"][self.NULL]["sequential"]

    def test_a_batch_lost_whole_keeps_every_later_look(self):
        # review F1: batch 1 lost whole; the look after it repeats B = 200 (one file); the rule stops at 600
        seq = self.lost_batches_world("w-lost1", [1], 600, "rule met for both tests", [200, 400])
        self.assertEqual([lk["B"] for lk in seq["looks"]], [200, 400, 600])
        self.assertEqual(seq["batches_adding_no_product"], [1])
        self.assertEqual((seq["first_look_where_rule_stops"], seq["stop_verdict"]), (600, "consistent"))
        self.assertTrue(seq["final_look_is_final_B"])
        self.assertTrue(all(lk["status_file"] for lk in seq["looks"]))
        # two batches lost whole (two collisions): the missed looks would hide a failure to stop at 600
        seq = self.lost_batches_world("w-lost2", [1, 2], 800, "batches exhausted", [200, 400, 600])
        self.assertEqual([lk["B"] for lk in seq["looks"]], [200, 400, 600, 800])
        self.assertEqual(seq["batches_adding_no_product"], [1, 2])
        self.assertEqual((seq["first_look_where_rule_stops"], seq["stop_verdict"]), (600, "INCONSISTENT"))
        self.assertTrue(seq["final_look_is_final_B"])

    def test_looks_do_not_need_the_b0_file(self):
        # review F2: B-files for 200 and 400 and a rule stop at 600, but no B0 file
        seq = self.lost_batches_world("w-nob0", [], 600, "rule met for both tests", [200, 400], drop_b0=True)
        self.assertEqual([lk["B"] for lk in seq["looks"]], [200, 400, 600])
        self.assertEqual((seq["stop_verdict"], seq["final_look_is_final_B"]), ("consistent", True))

    def test_any_partial_name_is_excluded(self):
        d = Path(tempfile.mkdtemp(prefix="s5p_partial_"))
        try:
            for n in ("c_s1.npz", "c_s2.partial-77.npz", "c_s3.partial.npz"):
                (d / n).write_bytes(b"")
            self.assertEqual([Path(p).name for p in R.finished_products(str(d / "c_s*.npz"))], ["c_s1.npz"])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_a_product_outside_the_submitted_batches_is_kept_and_listed(self):
        d = self.t.design()
        b = self.base
        g = R.seed_gap_report(d, self.NULL, b, list(range(b, b + 10)) + [b + 450, b - 1])
        self.assertEqual(g["span"], [b, b + 400])
        self.assertEqual(g["batches_submitted"], 2)
        self.assertEqual(g["seeds_outside_submitted_batches"], [b - 1, b + 450])
        self.assertEqual(g["missing_seeds_by_batch"]["1"], list(range(b + 200, b + 400)))
        self.assertEqual(g["span_basis"]["last_batch_holding_a_product"], 3)  # reported, not used: looks exist
        # no per-look status file: the batches are inferred from the products
        d["nulls"][self.NULL]["calibration_n"]["sequential_status"] = str(self.dir / "nostatus" / "x-final.json")
        g = R.seed_gap_report(d, self.NULL, b, [b + 3, b + 450])
        self.assertEqual((g["span"], g["span_basis"]["used"]), ([b, b + 600], "products (no per-look status file)"))
        self.assertEqual(g["seeds_outside_submitted_batches"], [])


class A8Sensitivity(unittest.TestCase):
    """The A8 readings of the stopping rule on synthetic boundary cases; the primary reading is unchanged."""

    def test_primary_defaults_are_the_primary_reading(self):
        for B in (200, 400, 1999):
            for k in range(0, B + 1, 7):
                self.assertEqual(R.sequential_stop(k, B, THR), R.stop_readings(k, B, THR)["primary"])

    def test_precision_level_boundary_at_200_and_400(self):
        # p ~ 0.90 at B = 200: 99.5% half-width 0.058 > 0.05 (continue), 95% half-width 0.042 <= 0.05 (stop)
        r = R.stop_readings(179, 200, THR)
        self.assertFalse(r["primary"]["stop"])
        self.assertTrue(r["A8_alt_precision_95"]["stop"])
        lo, hi = r["primary"]["look_interval"]
        plo, phi = r["A8_alt_precision_95"]["precision_interval"]
        self.assertGreater((hi - lo) / 2, 0.05)
        self.assertLessEqual((phi - plo) / 2, 0.05)
        # p ~ 0.30 at B = 400: the same split
        r = R.stop_readings(119, 400, THR)
        self.assertEqual((r["primary"]["stop"], r["A8_alt_precision_95"]["stop"]), (False, True))
        # a threshold in the look interval blocks every reading (condition (a) is on the look interval in all)
        r = R.stop_readings(20, 400, THR)  # p ~ 0.052, look interval contains 0.05
        self.assertFalse(any(v["stop"] for v in r.values()))

    def test_readings_agree_from_1000_on_and_alt_never_stops_later(self):
        m = R.a8_sensitivity_map(THR, looks=(200, 800, 1000, 1600), final=1999)
        for B in ("1000", "1600", "1999"):
            self.assertEqual(m[B], {}, B)
        for B in ("200", "800"):
            self.assertNotIn("A8_alt_open_boundaries", m[B])
            self.assertEqual(m[B]["A8_alt_precision_95"]["primary_stops_where_alt_continues"], 0)
            self.assertGreater(m[B]["A8_alt_precision_95"]["alt_stops_where_primary_continues"], 0)

    def test_open_versus_closed_on_exact_endpoints(self):
        thr = [0.01, 0.05]
        # threshold exactly at the upper end (p = 0.035: half-width 0.015 <= 0.5 p = 0.0175)
        c = R.stop_condition((0.02, 0.05), (0.02, 0.05), 0.035, thr, "closed")
        o = R.stop_condition((0.02, 0.05), (0.02, 0.05), 0.035, thr, "open")
        self.assertEqual((c["straddled"], o["straddled"]), ([0.05], []))
        self.assertEqual((c["stop"], o["stop"]), (False, True))
        # threshold exactly at the lower end (p = 0.1: half-width 0.045 <= 0.05)
        c = R.stop_condition((0.05, 0.14), (0.05, 0.14), 0.1, thr, "closed")
        o = R.stop_condition((0.05, 0.14), (0.05, 0.14), 0.1, thr, "open")
        self.assertEqual((c["stop"], o["stop"]), (False, True))
        c = R.stop_condition((0.01, 0.04), (0.01, 0.04), 0.02, thr, "closed")
        o = R.stop_condition((0.01, 0.04), (0.01, 0.04), 0.02, thr, "open")
        self.assertEqual((c["straddled"], o["straddled"]), ([0.01], []))
        both = R.stop_condition((0.005, 0.02), (0.005, 0.02), 0.01, thr, "open")
        self.assertEqual(both["straddled"], [0.01])  # an interior threshold is straddled in both readings

    def test_precision_bounds_are_inclusive_and_the_small_p_bound_strict(self):
        thr = [0.005, 0.05]
        self.assertTrue(R.stop_condition((0.2, 0.3), (0.2, 0.3), 0.25, thr)["t7_precise"])     # half = 0.05
        self.assertTrue(R.stop_condition((0.02, 0.04), (0.02, 0.04), 0.02, thr)["t7_precise"])  # half = 0.5 p
        self.assertFalse(R.stop_condition((0.0, 0.005), (0.0, 0.005), 0.004, thr, "open")["t7_precise"])
        self.assertTrue(R.stop_condition((0.0, 0.0049), (0.0, 0.0049), 0.004, thr)["t7_precise"])

    def test_stop_verdict(self):
        v = R.stop_verdict
        self.assertEqual(v("rule met for both tests", 600, 600), "consistent")
        self.assertEqual(v("rule met for both tests", 400, 600), "INCONSISTENT")
        self.assertEqual(v("rule met for both tests", None, 600), "INCONSISTENT")
        self.assertEqual(v("batches exhausted", None, 1999), "consistent")
        self.assertEqual(v("maximum reached", 1999, 1999), "consistent")
        self.assertEqual(v("maximum reached", 1400, 1999), "INCONSISTENT")
        self.assertEqual(v("budget", None, 800), "consistent")
        self.assertEqual(v("budget", 600, 800), "INCONSISTENT")
        self.assertEqual(v(None, None, None), "not terminal")

    def test_end_to_end_readings_are_carried_and_labelled(self):
        d = Path(tempfile.mkdtemp(prefix="s5p_recompute_a8_"))
        try:
            t = Toy(d / "w")
            base = t.truth["MnvTune_v1"]
            t.calibration("MnvTune_v1", 600)
            t.calibration("GiBUU_2019", 20)
            t.set_data(base * (1 + 0.01 * np.random.default_rng(21).standard_normal(base.size)))
            for B in (200, 400):
                t.status("MnvTune_v1", B, False, "continue")
            t.status("MnvTune_v1", 600, True, "batches exhausted")
            out = R.evaluate(t.design(), t.v_path, t.contract, log=lambda *a: None)
            seq = out["nulls"]["MnvTune_v1"]["sequential"]
            a8 = seq["a8_sensitivity"]
            self.assertEqual(list(a8["readings"])[0], "primary")
            self.assertEqual(a8["first_look_where_rule_stops"]["primary"], seq["first_look_where_rule_stops"])
            self.assertEqual(a8["stop_verdict_by_reading"]["primary"], seq["stop_verdict"])
            thr = R.decision_thresholds(0.05, 4)
            for lk in seq["looks"]:
                for name, rec in lk["a8_sensitivity"].items():
                    self.assertNotEqual(name, "primary")
                    want = all(R.stop_readings(lk["tests"][t_]["k"], lk["B"], thr)[name]["stop"] for t_ in R.TESTS)
                    self.assertEqual(rec["rule_stops"], want)
                    self.assertEqual(rec["differs_from_primary"], want != lk["rule_stops"])
            fs = a8["first_look_where_rule_stops"]
            if fs["primary"] is not None and fs["A8_alt_precision_95"] is not None:
                self.assertLessEqual(fs["A8_alt_precision_95"], fs["primary"])
        finally:
            shutil.rmtree(d, ignore_errors=True)




class Compare(unittest.TestCase):
    """The comparer (review REVIEW-20260929-s5p-recompute-comparer.md, F-1..F-8): AGREE only when every REQUIRED leaf
    is located and agrees, and every production leaf is consumed or excluded by an anchored scalar pattern; strict
    types; a B = 0 null needs a scalar marker; the ruled robustness members are m1 +-3 only; ERROR/exit 3 on
    failure, and a stale report is never left behind."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="s5p_recompute_cmp_"))
        t = Toy(self.dir / "w")
        t.calibration("MnvTune_v1", 60)
        t.calibration("GiBUU_2019", 60)
        self.mine = R.jsonable(R.evaluate(t.design(), t.v_path, t.contract, log=lambda *a: None))
        self.mine["inputs"] = {"design_sha256": "d" * 64}

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    @staticmethod
    def prod_name(n):  # production-form variant names, as the owner states them ("0.5", "m1+3")
        return str(float(n[2:])) if n.startswith("c=") else n.replace("m1=", "m1")

    def production_like(self):
        """A joint-evaluate.json and a robust-labels.json (schema /2) in production form, agreeing with self.mine."""
        m = self.mine
        pn = self.prod_name
        tests = {}
        for key, rec in m["nulls"].items():
            if rec["B"] == 0:
                tests[key] = {"not_calibrated": "budget stop at B = 0"}
                continue
            r = {"domain_cells": rec["domain_cells"], "T_total_obs": rec["observed_T"]["total"],
                 "T_shape_obs": rec["observed_T"]["shape"], "variants": {}, "robustness_variants": {},
                 "observed_jitter_p": {}, "implied_size_of_unshifted_test": {},
                 "process_shift": {"path": m["provenance"][f"process_shift:{key}"]["path"],
                                   "sha256": m["provenance"][f"process_shift:{key}"]["sha256"],
                                   "mode": m["provenance"][f"process_shift:{key}"]["mode"],
                                   "magnitude": rec["process_shift"]["magnitude"]}}
            for t in ("total", "shape"):
                tr = rec["tests"][t]
                r[t] = {x: tr[x] for x in ("p", "k", "B")}
                for n, v in tr["variants"].items():
                    r["variants"].setdefault(pn(n), {})[t] = {"k": v["k"], "p": v["p"]}
                rob = tr.get("robust_kappa3_replace_kappa2")
                for n, v in ((rob or {}).get("variants") or {}).items():
                    if n.startswith("m1="):
                        r["robustness_variants"].setdefault(pn(n), {})[t] = {"k": v["k"], "p": v["p"]}
                j = tr["observed_jitter"]
                r["observed_jitter_p"][t] = {"min": j["p_min"], "median": j["p_median"], "max": j["p_max"], "n": j["n"]}
                for n, v in tr["implied_size"].items():
                    r["implied_size_of_unshifted_test"].setdefault(pn(n), {})[t] = v
            tests[key] = r
        dec, hp, rk, rb = {}, {}, {}, {}
        keep = {d["test"]: d["decision"] for d in m["family"]["keep_both_kappa3_diagnostic"]["holm"]}
        for d in m["family"]["decisions"]:
            dec[d["test"]] = d["decision"]
            hp[d["test"]] = d["holm_point"]
            rk[d["test"]] = keep[d["test"]]
            rb[d["test"]] = m["family"]["frozen_boolean_equivalent_diagnostic"][d["test"]]
        prod = {"schema": "x", "design_sha256": "d" * 64, "v_sha256": m["provenance"]["V"]["sha256"],
                "names": m["names"], "tests": tests, "decisions": dec, "holm_point": hp,
                "decisions_robust_kappa": rk, "robust_to_the_sub_fine_residual": rb, "power": {}}
        fam = m["family"]
        members = lambda which: {test: [pn(n) for n in v] for test, v in C_family(m, which).items()}  # noqa: E731
        labels = {"schema": "s5p-robust-labels/2", "labels": dict(fam["robust_labels"]),
                  "decisions_kappa3_replace": {d["test"]: {x: d[x] for x in ("p", "k", "B", "threshold", "interval",
                                                                            "level", "decision")}
                                               for d in fam["holm_at_kappa_robust"]},
                  "family_members": members("replace"),
                  "diagnostics": {"frozen_boolean_robust_to_the_sub_fine_residual":
                                  dict(fam["frozen_boolean_equivalent_diagnostic"]),
                                  "keep_both": {"family": members("retain"),
                                                "labels": dict(fam["keep_both_kappa3_diagnostic"]["labels"])}},
                  "evaluate_sha256": "e" * 64, "design_sha256": "d" * 64, "alpha_family": 0.05,
                  "code_sha256": "c" * 64, "ruling": "RULING-20260929-s5p-A7-robustness-flag.md",
                  "evaluate": "/x/joint-evaluate.json"}
        return prod, labels

    def cmp(self, prod, labels, sha="e" * 64):
        import s5p_recompute_compare as C
        return C.compare(self.mine, prod, labels, prod_sha256=sha)

    def assertVerdict(self, want, prod, labels, sha="e" * 64):
        rep = self.cmp(prod, labels, sha)
        self.assertEqual(rep["verdict"], want, (rep["discrepancies"][:3], rep["not_located"][:5],
                                                rep["unresolved_production_leaves"][:5]))
        return rep

    def test_baseline_agrees_with_everything_accounted_for(self):
        prod, labels = self.production_like()
        rep = self.assertVerdict("AGREE", prod, labels)
        self.assertEqual((rep["not_located"], rep["unresolved_production_leaves"]), ([], []))
        self.assertEqual(sorted(e["path"] for e in rep["excluded_by_scope"]["paths"]),
                         ["joint-evaluate.json:schema", "robust-labels.json:code_sha256", "robust-labels.json:evaluate",
                          "robust-labels.json:ruling", "robust-labels.json:schema"])

    def test_F1_missing_required_quantities(self):
        G = "GiBUU_2019"
        cases = {
            "claim p": lambda p, l: p["tests"][G]["total"].pop("p"),
            "claim k and B": lambda p, l: (p["tests"][G]["total"].pop("k"), p["tests"][G]["total"].pop("B")),
            "whole test": lambda p, l: p["tests"][G].pop("total"),
            "all variants": lambda p, l: p["tests"][G].pop("variants"),
            "one variant": lambda p, l: p["tests"][G]["variants"].pop("m1-2"),
            "robustness empty": lambda p, l: p["tests"][G].__setitem__("robustness_variants", {}),
            "variant p": lambda p, l: p["tests"][G]["variants"]["m1+2"]["total"].pop("p"),
            "null reduced to T": lambda p, l: p["tests"].__setitem__(G, {"T_total_obs": p["tests"][G]["T_total_obs"]}),
            "jitter p": lambda p, l: p["tests"][G].pop("observed_jitter_p"),
            "implied size": lambda p, l: p["tests"][G].pop("implied_size_of_unshifted_test"),
            "design digest": lambda p, l: p.pop("design_sha256"),
            "V digest": lambda p, l: p.pop("v_sha256"),
        }
        for name, mut in cases.items():
            prod, labels = self.production_like()
            mut(prod, labels)
            with self.subTest(name):
                self.assertVerdict("INCOMPLETE", prod, labels)

    def test_F1_power_requirements(self):
        prod, labels = self.production_like()
        self.mine["power"] = {"P1": {"null": "MnvTune_v1", "n_declared": 12, "n_present": 10, "complete": False,
                                     "total": {}, "shape": {}}}
        mp = self.mine["power"]["P1"]
        pw = {"n": 10, "declared": 12, "null": "MnvTune_v1", "incomplete": True}
        for t in ("total", "shape"):
            pw[t] = {}
            for rule, prule in (("rank_unshifted", "unshifted"), ("rank_claim", "claim_rule"),
                                ("determined_claim", "claim_rule_determined")):
                pw[t][prule] = {}
                for lvl in ("0.05", "0.005"):
                    mp[t].setdefault(lvl, {})[rule] = {"count": 3, "power": 0.3, "interval": [0.1, 0.6]}
                    pw[t][prule][lvl] = 0.3
        prod["power"] = {"P1": pw}
        self.assertVerdict("AGREE", prod, labels)
        for mut in (lambda: prod["power"].__setitem__("P1", {}), lambda: pw.pop("shape"),
                    lambda: pw["total"]["claim_rule"].pop("0.005"), lambda: pw.pop("n")):
            import copy
            saved = copy.deepcopy(prod["power"])
            mut()
            with self.subTest(str(mut)):
                self.assertVerdict("INCOMPLETE", prod, labels)
            prod["power"] = saved
            pw = prod["power"]["P1"]

    def test_F2_labels_document_requirements(self):
        cases = {
            "decisions_kappa3_replace": lambda l: l.pop("decisions_kappa3_replace"),
            "family_members": lambda l: l.pop("family_members"),
            "diagnostics": lambda l: l.pop("diagnostics"),
            "keep_both family": lambda l: l["diagnostics"]["keep_both"].pop("family"),
            "evaluate_sha256": lambda l: l.pop("evaluate_sha256"),
            "design_sha256": lambda l: l.pop("design_sha256"),
            "alpha_family": lambda l: l.pop("alpha_family"),
            "replace p": lambda l: l["decisions_kappa3_replace"]["GiBUU_2019:total"].pop("p"),
            "replace level": lambda l: l["decisions_kappa3_replace"]["GiBUU_2019:total"].pop("level"),
            "one label": lambda l: l["labels"].pop("MnvTune_v1:shape"),
        }
        for name, mut in cases.items():
            prod, labels = self.production_like()
            mut(labels)
            with self.subTest(name):
                self.assertVerdict("INCOMPLETE", prod, labels)
        prod, labels = self.production_like()
        self.assertVerdict("INCOMPLETE", prod, None)

    def test_F3_strict_types(self):
        cases = {
            "bool as int": lambda p, l: p["robust_to_the_sub_fine_residual"].__setitem__(
                "MnvTune_v1:total", int(p["robust_to_the_sub_fine_residual"]["MnvTune_v1:total"])),
            "p as string": lambda p, l: p["tests"]["GiBUU_2019"]["total"].__setitem__(
                "p", str(p["tests"]["GiBUU_2019"]["total"]["p"])),
            "members as dict": lambda p, l: l["family_members"].__setitem__(
                "GiBUU_2019:total", {n: {"k": 999} for n in l["family_members"]["GiBUU_2019:total"]}),
            "count as bool": lambda p, l: p["tests"]["GiBUU_2019"].__setitem__("domain_cells", True),
            "decision as list": lambda p, l: p["decisions"].__setitem__("MnvTune_v1:total", ["rejected"]),
        }
        for name, mut in cases.items():
            prod, labels = self.production_like()
            mut(prod, labels)
            with self.subTest(name):
                self.assertNotEqual(self.cmp(prod, labels)["verdict"], "AGREE")

    def test_F4_exclusions_are_anchored_and_scalar(self):
        G = "GiBUU_2019"
        hidden = {
            "under kappa": lambda p, l: p["tests"][G]["total"].__setitem__("kappa", {"p": 0.9, "k": 55}),
            "top ruling": lambda p, l: p.__setitem__("ruling", {"decisions": {"x": "rejected"}}),
            "evaluate wrapper": lambda p, l: p.__setitem__("evaluate", {"tests": {}}),
            "null reason": lambda p, l: p["tests"][G].__setitem__("reason", "budget"),
            "mode dict": lambda p, l: p["tests"][G].__setitem__("mode", {"a": {"p": 0.5}}),
            "labels keep_both ruling": lambda p, l: l["diagnostics"]["keep_both"].__setitem__("ruling", {"x": "y"}),
            "schema not at top": lambda p, l: p["tests"][G].__setitem__("schema", "v9"),
            "lateral_symmetry deep": lambda p, l: p["tests"][G].__setitem__("lateral_symmetry", {"b": {"c": 1.0}}),
            "schema as dict": lambda p, l: p.__setitem__("schema", {"p": 0.5}),
        }
        for name, mut in hidden.items():
            prod, labels = self.production_like()
            mut(prod, labels)
            with self.subTest(name):
                self.assertVerdict("INCOMPLETE", prod, labels)
        prod, labels = self.production_like()
        prod.update({"utc": "2026-10-01T00:00:00Z", "lateral_symmetry": {"BeamAngleX": {"corr": -0.3}},
                     "shrinkage": 0.015, "files_first_last": ["a", "b"]})
        rep = self.assertVerdict("AGREE", prod, labels)
        self.assertIn("joint-evaluate.json:lateral_symmetry/BeamAngleX/corr",
                      [e["path"] for e in rep["excluded_by_scope"]["paths"]])

    def test_F5_digests_are_compared_not_excluded(self):
        prod, labels = self.production_like()
        prod["tests"]["GiBUU_2019"]["process_shift"]["sha256"] = "0" * 64
        self.assertVerdict("DISCREPANT", prod, labels)
        prod, labels = self.production_like()
        prod["tests"]["GiBUU_2019"]["process_shift"]["mode"] = "raw"
        self.assertVerdict("DISCREPANT", prod, labels)
        prod, labels = self.production_like()
        prod.pop("v_sha256")
        prod["provenance"] = {"V": {"sha256": "wrong"}}
        self.assertVerdict("INCOMPLETE", prod, labels)
        prod, labels = self.production_like()
        prod["v_sha256"] = "0" * 64
        self.assertVerdict("DISCREPANT", prod, labels)

    def test_B0_marker_rules(self):
        d = Path(tempfile.mkdtemp(prefix="s5p_recompute_b0_"))
        try:
            t = Toy(d / "w")
            t.calibration("MnvTune_v1", 60)
            t.status("GiBUU_2019", 0, True, "budget")
            self.mine = R.jsonable(R.evaluate(t.design(), t.v_path, t.contract, log=lambda *a: None))
            self.mine["inputs"] = {"design_sha256": "d" * 64}
            prod, labels = self.production_like()
            self.assertEqual(labels["family_members"]["GiBUU_2019:total"], [])
            self.assertVerdict("AGREE", prod, labels)
            prod["tests"]["GiBUU_2019"] = {"not_calibrated": {"B": 7, "p": 0.3, "k": 2}}  # F-6: a dict marker
            self.assertNotEqual(self.cmp(prod, labels)["verdict"], "AGREE")
            prod["tests"]["GiBUU_2019"] = {"not_calibrated": False}
            self.assertVerdict("DISCREPANT", prod, labels)
            tobs = self.mine["nulls"]["GiBUU_2019"]["observed_T"]["total"]
            prod["tests"]["GiBUU_2019"] = {"T_total_obs": tobs}  # Z8: neither a marker nor a B -> not located
            self.assertVerdict("INCOMPLETE", prod, labels)
            prod["tests"]["GiBUU_2019"] = {"T_total_obs": tobs + 1.0}  # a wrong T beside it is a discrepancy
            self.assertVerdict("DISCREPANT", prod, labels)
            prod["tests"]["GiBUU_2019"] = {"total": {"p": 1.0, "k": 0, "B": 0}, "shape": {"p": 1.0, "k": 0, "B": 0}}
            self.assertVerdict("AGREE", prod, labels)
            prod["tests"]["GiBUU_2019"]["total"]["B"] = 60
            self.assertVerdict("DISCREPANT", prod, labels)
            self.mine["nulls"]["GiBUU_2019"]["B"] = 5  # a recompute that calibrated it, against a marker
            prod["tests"]["GiBUU_2019"] = {"not_calibrated": "budget"}
            self.assertNotEqual(self.cmp(prod, labels)["verdict"], "AGREE")
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_F7_robustness_slot_holds_only_the_ruled_m1_members(self):
        prod, labels = self.production_like()
        rv = prod["tests"]["GiBUU_2019"]["robustness_variants"]
        self.assertEqual(sorted(rv), ["m1+3", "m1-3"])
        rv.clear()
        rv["m1+2"] = prod["tests"]["GiBUU_2019"]["variants"]["m1+2"]
        self.assertVerdict("INCOMPLETE", prod, labels)
        prod, labels = self.production_like()
        prod["tests"]["GiBUU_2019"]["variants"]["m1+3"] = prod["tests"]["GiBUU_2019"]["robustness_variants"]["m1+3"]
        self.assertVerdict("INCOMPLETE", prod, labels)  # an extra member in the claim slot is unresolved

    def test_family_membership_and_names(self):
        import s5p_recompute_compare as C
        prod, labels = self.production_like()
        labels["family_members"]["GiBUU_2019:total"] = labels["diagnostics"]["keep_both"]["family"]["GiBUU_2019:total"]
        bad = {r["item"] for r in self.cmp(prod, labels)["discrepancies"]}
        self.assertEqual(bad, {"family_members:GiBUU_2019:total"})
        prod, labels = self.production_like()
        labels["family_members"]["GiBUU_2019:total"] = labels["family_members"]["GiBUU_2019:total"][:-1]
        self.assertVerdict("DISCREPANT", prod, labels)
        prod, labels = self.production_like()
        labels["family_members"]["GiBUU_2019:shape"] = ["c-half", "m1+3"]
        self.assertVerdict("INCOMPLETE", prod, labels)
        prod_names = ["0.0", "0.5", "1.0", "m1+2", "m1-2", "m1+3", "m1-3"]
        mine = ["c=0", "c=0.5", "c=1", "m1=+2", "m1=-2", "m1=+3", "m1=-3"]
        self.assertEqual(sorted(map(C.variant_key, prod_names)), sorted(map(C.variant_key, mine)))
        self.assertEqual([C.variant_key(n) for n in ("kappa3", "m1=3", "-0.5", 3)], [None, None, None, None])

    def test_altered_values_are_discrepant(self):
        G = "GiBUU_2019"
        cases = {
            "claim k": lambda p, l: p["tests"][G]["shape"].__setitem__("k", p["tests"][G]["shape"]["k"] + 1),
            "T": lambda p, l: p["tests"][G].__setitem__("T_total_obs", p["tests"][G]["T_total_obs"] * (1 + 1e-6)),
            "decision": lambda p, l: p["decisions"].__setitem__("MnvTune_v1:total", "something"),
            "robust variant k": lambda p, l: p["tests"][G]["robustness_variants"]["m1+3"]["total"].__setitem__("k", -1),
            "label": lambda p, l: l["labels"].__setitem__("MnvTune_v1:total", "something"),
            "keep-both label": lambda p, l: l["diagnostics"]["keep_both"]["labels"].__setitem__("MnvTune_v1:total", "x"),
            "replace k": lambda p, l: l["decisions_kappa3_replace"]["MnvTune_v1:total"].__setitem__("k", 10 ** 6),
            "frozen boolean": lambda p, l: p["robust_to_the_sub_fine_residual"].__setitem__(
                "MnvTune_v1:total", not p["robust_to_the_sub_fine_residual"]["MnvTune_v1:total"]),
            "jitter median": lambda p, l: p["tests"][G]["observed_jitter_p"]["total"].__setitem__("median", -1.0),
        }
        for name, mut in cases.items():
            prod, labels = self.production_like()
            mut(prod, labels)
            with self.subTest(name):
                self.assertVerdict("DISCREPANT", prod, labels)
        prod, labels = self.production_like()
        self.assertVerdict("DISCREPANT", prod, labels, sha="f" * 64)  # labels bound to another evaluate file

    def test_unknown_fields_at_any_depth_are_unresolved(self):
        G = "GiBUU_2019"
        for name, mut in {
            "top": lambda p, l: p.__setitem__("family_summary", {"rejections": 1}),
            "test record": lambda p, l: p["tests"][G]["total"].__setitem__("new_q", 0.3),
            "variant entry": lambda p, l: p["tests"][G]["variants"]["0.5"]["total"].__setitem__("extra", 1),
            "unparsable variant": lambda p, l: p["tests"][G]["variants"].__setitem__("kappa-two", {"total": {"k": 1}}),
            "labels top": lambda p, l: l.__setitem__("labels_new_name", {"MnvTune_v1:total": "x"}),
        }.items():
            prod, labels = self.production_like()
            mut(prod, labels)
            with self.subTest(name):
                self.assertVerdict("INCOMPLETE", prod, labels)

    def test_verification_round_ND1_to_ND5_and_robust_claims(self):
        """Second review round (verification of 6c7c7b9f): ND-1..ND-5 and the per-test keep-both robust claims."""
        import copy
        G = "GiBUU_2019"
        base_prod, base_labels = self.production_like()
        # ND-1: the frozen e2e layout, the implied size inside each variant entry as {"power": ...}
        prod, labels = copy.deepcopy(base_prod), copy.deepcopy(base_labels)
        for key, rec in prod["tests"].items():
            per = rec.pop("implied_size_of_unshifted_test")
            for name, by_t in per.items():
                for t, v in by_t.items():
                    rec["variants"][name].setdefault("implied_size_of_unshifted_test", {})[t] = {"power": v}
        self.assertVerdict("AGREE", prod, labels)
        prod["tests"][G]["variants"]["0.5"]["implied_size_of_unshifted_test"]["shape"]["power"] += 0.01
        self.assertVerdict("DISCREPANT", prod, labels)
        # ND-2: the contents of the jitter summary and the c > 0 implied sizes are required
        for mut in (lambda p: p["tests"][G]["observed_jitter_p"].pop("shape"),
                    lambda p: p["tests"][G]["observed_jitter_p"]["total"].pop("median"),
                    lambda p: p["tests"][G]["implied_size_of_unshifted_test"].pop("0.5"),
                    lambda p: p["tests"][G]["implied_size_of_unshifted_test"]["1.0"].pop("shape")):
            prod = copy.deepcopy(base_prod)
            mut(prod)
            self.assertVerdict("INCOMPLETE", prod, base_labels)
        prod = copy.deepcopy(base_prod)  # an M1 variant's implied size is compared where present, not required
        prod["tests"][G]["implied_size_of_unshifted_test"].pop("m1+2")
        self.assertVerdict("AGREE", prod, base_labels)
        # ND-4: argmax written with production variant names
        prod = copy.deepcopy(base_prod)
        am = self.mine["nulls"][G]["tests"]["total"]["argmax"]
        prod["tests"][G]["total"]["argmax"] = [self.prod_name(n) for n in am]
        self.assertVerdict("AGREE", prod, base_labels)
        prod["tests"][G]["total"]["argmax"] = ["0.5"] if am != ["c=0.5"] else ["1.0"]
        self.assertVerdict("DISCREPANT", prod, base_labels)
        # N2: the frozen per-test keep-both robust claim (tests/<null>/total_robust)
        prod = copy.deepcopy(base_prod)
        for key, rec in self.mine["nulls"].items():
            for t in ("total", "shape"):
                r = rec["tests"][t].get("robust_kappa3_retain_kappa2") or rec["tests"][t]
                prod["tests"][key][f"{t}_robust"] = {x: r[x] for x in ("p", "k", "B")}
        self.assertVerdict("AGREE", prod, base_labels)
        prod["tests"][G]["shape_robust"]["k"] += 1
        self.assertVerdict("DISCREPANT", prod, base_labels)

    def test_ND3_marker_of_unstated_shape_is_incomplete(self):
        d = Path(tempfile.mkdtemp(prefix="s5p_recompute_nd3_"))
        try:
            t = Toy(d / "w")
            t.calibration("MnvTune_v1", 60)
            t.status("GiBUU_2019", 0, True, "budget")
            self.mine = R.jsonable(R.evaluate(t.design(), t.v_path, t.contract, log=lambda *a: None))
            self.mine["inputs"] = {"design_sha256": "d" * 64}
            prod, labels = self.production_like()
            prod["tests"]["GiBUU_2019"] = {"not_calibrated": {"reason": "budget", "B": 0}}
            self.assertVerdict("INCOMPLETE", prod, labels)
            prod["tests"]["GiBUU_2019"] = {"not_calibrated": ""}
            self.assertVerdict("DISCREPANT", prod, labels)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_ND5_unwritable_report_is_an_error(self):
        import s5p_recompute_compare as C
        prod, labels = self.production_like()
        f = {n: self.dir / f"{n}.json" for n in ("mine", "prod", "labels")}
        for n, doc in (("mine", self.mine), ("prod", prod), ("labels", labels)):
            f[n].write_text(json.dumps(doc))
        self.assertEqual(C.compare_files(str(f["mine"]), str(f["prod"]), str(self.dir / "no" / "such" / "cmp.json"),
                                         str(f["labels"])), 3)

    def test_F8_exit_codes_errors_and_no_stale_report(self):
        import s5p_recompute_compare as C
        import hashlib
        prod, labels = self.production_like()
        f = {n: self.dir / f"{n}.json" for n in ("mine", "prod", "labels")}
        f["prod"].write_text(json.dumps(prod))
        labels["evaluate_sha256"] = hashlib.sha256(f["prod"].read_bytes()).hexdigest()
        f["mine"].write_text(json.dumps(self.mine))
        f["labels"].write_text(json.dumps(labels))
        out = self.dir / "cmp.json"
        s = lambda: json.loads(out.read_text())["verdict"]  # noqa: E731
        self.assertEqual(C.compare_files(str(f["mine"]), str(f["prod"]), str(out), str(f["labels"])), 0)
        self.assertEqual(s(), "AGREE")
        self.assertEqual(C.compare_files(str(f["mine"]), str(f["prod"]), str(out), str(self.dir / "nope.json")), 2)
        self.assertEqual(s(), "INCOMPLETE")
        self.assertEqual(C.compare_files(str(f["mine"]), str(f["prod"]), str(out), None), 2)
        bad = dict(prod)
        bad["tests"] = "not a dict"  # handled, not an error: the nulls are not located (and the digest differs)
        f["prod"].write_text(json.dumps(bad))
        self.assertEqual(C.compare_files(str(f["mine"]), str(f["prod"]), str(out), str(f["labels"])), 1)
        f["prod"].write_text("[]")  # unprocessable: a top-level list
        self.assertEqual(C.compare_files(str(f["mine"]), str(f["prod"]), str(out), str(f["labels"])), 3)
        self.assertEqual(s(), "ERROR")
        f["prod"].write_text("{not json")
        self.assertEqual(C.compare_files(str(f["mine"]), str(f["prod"]), str(out), str(f["labels"])), 3)
        self.assertEqual(s(), "ERROR")  # the earlier AGREE report is gone
        prod["tests"]["MnvTune_v1"]["total"]["B"] += 1
        f["prod"].write_text(json.dumps(prod))
        self.assertEqual(C.compare_files(str(f["mine"]), str(f["prod"]), str(out), str(f["labels"])), 1)


def C_family(mine, which):
    import s5p_recompute_compare as C
    return C.family_names(mine, which)


class A7Ruling(unittest.TestCase):
    """The ruled label (full Holm re-run at kappa = 3) and the preserved per-test diagnostic can differ."""

    def e(self, name, k, B=1999):
        return {"test": name, "k": k, "B": B, "p": R.mc_p(k, B)}

    def test_labels(self):
        prim = R.holm_determined([self.e("a", 0), self.e("b", 5), self.e("c", 1500)], 0.05)
        rob = R.holm_determined([self.e("a", 0), self.e("b", 60), self.e("c", 1500)], 0.05)
        lab = R.robust_labels(prim, rob)
        self.assertEqual(lab, {"a": R.ROBUST, "b": R.NOT_ROBUST, "c": R.NOT_APPLICABLE})
        with self.assertRaises(ValueError):
            R.robust_labels(prim, rob[::-1])

    def test_full_rerun_and_per_test_reading_disagree(self):
        # primary: blocker z (k = 0) rejected at 0.05/2; x (k = 40, upper 0.027) rejected at its step's 0.05
        prim = R.holm_determined([self.e("z", 0), self.e("x", 40)], 0.05)
        self.assertEqual([(d["decision"], d["threshold"]) for d in prim], [("rejected", 0.025), ("rejected", 0.05)])
        # kappa = 3: z (k = 45, interval [0.0165, 0.030]) sorts first and contains 0.025 -> the re-run stops
        # 'undetermined'; x (k = 46) inherits it -> the ruled label for x is 'not robust'
        rob = R.holm_determined([self.e("z", 45), self.e("x", 46)], 0.05)
        self.assertEqual([d["decision"] for d in rob], ["undetermined", "undetermined"])
        self.assertEqual(R.robust_labels(prim, rob), {"z": R.NOT_ROBUST, "x": R.NOT_ROBUST})
        # the preserved per-test reading A7(b): x's own kappa = 3 interval lies below the threshold of the step
        # that rejected it -> 'robust'; the two readings disagree on x
        self.assertLess(R.cp_interval(46, 1999)[1], prim[1]["threshold"])

    def test_end_to_end_sets_and_labels(self):
        d = Path(tempfile.mkdtemp(prefix="s5p_recompute_a7_"))
        try:
            t = Toy(d / "w")
            t.calibration("MnvTune_v1", 200)
            t.calibration("GiBUU_2019", 200)
            out = R.evaluate(t.design(), t.v_path, t.contract, log=lambda *a: None)
            g = out["nulls"]["GiBUU_2019"]["tests"]
            for test in R.TESTS:
                keep, repl = g[test]["robust_kappa3_retain_kappa2"], g[test]["robust_kappa3_replace_kappa2"]
                self.assertEqual(sorted(keep["variants"]), ["c=0", "c=0.5", "c=1", "m1=+2", "m1=+3", "m1=-2", "m1=-3"])
                self.assertEqual(sorted(repl["variants"]), ["c=0", "c=0.5", "c=1", "m1=+3", "m1=-3"])
                self.assertGreaterEqual(keep["k"], max(repl["k"], g[test]["k"]))  # a superset of both
            self.assertIsNone(out["nulls"]["MnvTune_v1"]["tests"]["total"]["robust_kappa3_retain_kappa2"])
            fam = out["family"]
            k3 = fam["kappa3"]
            self.assertIn("A7-VS ruled", k3["ruling"])
            # the reported labels and re-run are the RULED replace family; keep-both and the frozen boolean are diagnostics
            self.assertEqual(fam["robust_labels"], k3["replace_kappa2"]["labels"])
            self.assertEqual(fam["holm_at_kappa_robust"], k3["replace_kappa2"]["holm"])
            self.assertEqual(fam["keep_both_kappa3_diagnostic"]["labels"], k3["retain_kappa2"]["labels"])
            self.assertEqual(fam["frozen_boolean_equivalent_diagnostic"], k3["retain_kappa2"]["boolean_equivalent"])
            for i, dd in enumerate(fam["decisions"]):
                rr = fam["holm_at_kappa_robust"][i]
                want = R.NOT_APPLICABLE if dd["decision"] != "rejected" else (
                    R.ROBUST if rr["decision"] == "rejected" else R.NOT_ROBUST)
                self.assertEqual(fam["robust_labels"][dd["test"]], want)
            self.assertEqual(k3["tests_where_the_sets_differ"],
                             [x["test"] for x in fam["decisions"] if fam["robust_labels"][x["test"]]
                              != fam["keep_both_kappa3_diagnostic"]["labels"][x["test"]]])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_ruled_family_can_differ_from_keep_both(self):
        """A synthetic case where the +-2 members change the outcome: the reported label follows the replace family."""
        prim = R.holm_determined([self.e("z", 0), self.e("x", 40)], 0.05)
        keep = R.holm_determined([self.e("z", 45), self.e("x", 46)], 0.05)   # the +-2 members raise z's k
        repl = R.holm_determined([self.e("z", 10), self.e("x", 20)], 0.05)
        self.assertEqual((R.robust_labels(prim, repl)["x"], R.robust_labels(prim, keep)["x"]),
                         (R.ROBUST, R.NOT_ROBUST))


if __name__ == "__main__":
    unittest.main()


# ------------------------------------------------------------------------------------------- mapping extension

def _norm_path(p):
    """A key path with nulls, variants, power sets, levels and lateral bands replaced by placeholders."""
    import re
    nulls = {"MnvTune_v1", "GENIE_2_12_10_CV", "GENIE_2_12_10_MEC", "NuWro_21_09", "GiBUU_2019"}
    out = []
    for i, seg in enumerate(p):
        if i == 1 and p[0] == "lateral_symmetry":
            out.append("<band>")
        elif seg in nulls:
            out.append("<null>")
        elif ":" in seg and seg.split(":")[0] in nulls:
            out.append("<null>:" + seg.split(":")[1])
        elif re.fullmatch(r"\d+\.\d+|m1[+-]\d", seg):
            out.append("<v>")
        elif re.fullmatch(r"P\dg?_a1\.0", seg):
            out.append("<set>")
        else:
            out.append(seg)
    return "/".join(out)


def _signature(doc):
    def walk(o, p=()):
        if isinstance(o, dict) and o:
            for k, v in o.items():
                yield from walk(v, p + (k,))
        elif isinstance(o, list) and o and not all(not isinstance(x, (dict, list)) for x in o):
            for v in o:
                yield from walk(v, p + ("<i>",))
        else:
            yield p
    return sorted({_norm_path(p) for p in walk(doc)})


class CompareObservedLayout(unittest.TestCase):
    """The mapping extension (owner decision DECISION-20261005-s5p-recompute-extension-and-lost-seed-recovery.md):
    production's layout as OBSERVED in its terminal outputs. The fixture's key structure must equal the real files'
    (tests/data/s5p_production_layout_signature.json, key paths only), so a layout invented here cannot pass; the
    A16 descriptive fields are compared against the ruled reading."""

    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp(prefix="s5p_recompute_obs_"))
        t = Toy(cls.dir / "w")
        base = t.truth["MnvTune_v1"]
        tilt = np.repeat(np.linspace(0.9, 1.1, 4), base.size // 4)
        t.set_data(base * tilt)
        t.calibration("MnvTune_v1", 120)
        t.calibration("GiBUU_2019", 120)
        t.power("P1_a1.0", 12, "MnvTune_v1", tilt)
        pw = {"P1_a1.0": {"glob": str(t.root / "pow/P1_a1.0/pow_P1_a1.0_s*.npz"), "surrogate_seed0": 1951000,
                          "n": 15, "null": "MnvTune_v1"}}
        cls.mine = R.jsonable(R.evaluate(t.design(power=pw), t.v_path, t.contract, log=lambda *a: None))
        cls.mine["inputs"] = {"design_sha256": "d" * 64}
        cls.sig = json.loads((HERE / "data" / "s5p_production_layout_signature.json").read_text())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    @staticmethod
    def pn(n):
        return str(float(n[2:])) if n.startswith("c=") else n.replace("m1=", "m1")

    def observed(self):
        """joint-evaluate.json and robust-labels.json in production's observed layout, agreeing with self.mine under
        the ruled A16 reading."""
        m, pn = self.mine, self.pn
        fam = m["family"]
        tests = {}
        for key, rec in m["nulls"].items():
            prov = m["provenance"]
            psd, m1d = prov[f"process_shift:{key}"], prov[f"m1_shift:{key}"]
            r = {"domain_cells": rec["domain_cells"], "T_total_obs": rec["observed_T"]["total"],
                 "T_shape_obs": rec["observed_T"]["shape"],
                 "process_shift": {"mode": psd["mode"], "path": psd["path"], "sha256": psd["sha256"]},
                 "shift": {"mode": psd["mode"], **{f: rec["process_shift"][f] for f in
                                                   ("bias_norm_W", "a", "se", "n_pairs", "magnitude")}},
                 "variants": {}, "robustness_variants": {}, "observed_jitter_p": {}}
            if "none" not in m1d:
                r["m1_shift"] = {"path": m1d["path"], "kappa": m1d["kappa"], "kappa_robust": m1d["kappa_robust"]}
            for t in ("total", "shape"):
                tr = rec["tests"][t]
                r[t] = {"p": tr["p"], "k": tr["k"], "B": tr["B"], "tail_interval": tr["interval"],
                        "level": tr["level"], "rule": "the largest p over the declared shift variants"}
                rob = tr.get("robust_kappa3_retain_kappa2") or tr
                r[f"{t}_robust"] = {"p": rob["p"], "k": rob["k"], "B": rob["B"], "tail_interval": rob["interval"],
                                    "level": rob["level"], "rule": "the claim p with the kappa_robust M1 variants added"}
                for n, v in tr["variants"].items():
                    e = r["variants"].setdefault(pn(n), {})
                    e[t] = {x: v[y] for x, y in (("p", "p"), ("k", "k"), ("B", "B"), ("tail_interval", "interval"),
                                                 ("level", "level"))}
                    nt = tr["null_T_by_variant"][n]
                    e[f"null_T_{t}_median"], e[f"null_T_{t}_sd"] = nt["median"], nt["sd_ddof0"]  # A16 ruled
                    if n != "c=0":
                        d = tr["implied_size_detail"][n]
                        e.setdefault("implied_size_of_unshifted_test", {})[t] = {
                            "power": d["power"], "n": d["n"], "interval": d["interval"], "alpha": d["alpha"]}
                        e.setdefault("median_shift_in_null_sd", {})[t] = tr["median_shift_in_null_sd_A16_ruled"][n]
                rv = (tr.get("robust_kappa3_replace_kappa2") or {}).get("variants") or {}
                for n, v in rv.items():
                    if n.startswith("m1="):
                        r["robustness_variants"].setdefault(pn(n), {})[t] = {
                            x: v[y] for x, y in (("p", "p"), ("k", "k"), ("B", "B"), ("tail_interval", "interval"),
                                                 ("level", "level"))}
                j = tr["observed_jitter"]
                r["observed_jitter_p"][t] = {"min": j["p_min"], "median": j["p_median"], "max": j["p_max"], "n": j["n"]}
            tests[key] = r
        drec = lambda d: {x: d[x] for x in ("p", "k", "B", "threshold", "interval", "level", "decision")}  # noqa
        keep = {d["test"]: d for d in fam["keep_both_kappa3_diagnostic"]["holm"]}
        power = {"levels": list(m["power_levels"])}
        for sk, p in m["power"].items():
            e = {"n": p["n_present"], "null": p["null"], "declared": p["n_declared"], "incomplete": not p["complete"]}
            for t in ("total", "shape"):
                e[t] = {}
                for lvl in ("0.05", "0.005"):
                    q = p[t][lvl]
                    e[t][lvl] = {
                        "unshifted": {"power": q["rank_unshifted"]["power"], "n": p["n_present"],
                                      "interval": q["rank_unshifted"]["interval"], "alpha": float(lvl)},
                        "claim_rule": {"power": q["rank_claim"]["power"], "n": p["n_present"]},
                        "claim_rule_determined": {"power": q["determined_claim"]["power"], "n": p["n_present"],
                                                  "interval": q["determined_claim"]["interval"], "alpha": float(lvl),
                                                  "B": p["B_null"], "rule": "claim rule with determinacy"}}
            power[sk] = e
        prod = {"schema": "s5p-joint-evaluate/x", "design_sha256": "d" * 64, "v_sha256": m["provenance"]["V"]["sha256"],
                "names": m["names"], "tests": tests,
                "holm_point": {d["test"]: dict(fam["holm_point_classical"][d["test"]]) for d in fam["decisions"]},
                "decisions": {d["test"]: drec(d) for d in fam["decisions"]},
                "decisions_robust_kappa": {d["test"]: drec(keep[d["test"]]) for d in fam["decisions"]},
                "robust_to_the_sub_fine_residual": dict(fam["frozen_boolean_equivalent_diagnostic"]),
                "power": power,
                "lateral_symmetry": {b: {"corr_up_vs_minus_down": -0.3, "median_abs_delta_rel": 0.001}
                                     for b in ("BeamAngleX", "Muon_Energy_MINOS")}}
        members = {test: [pn(n) for n in v] for test, v in C_family(m, "replace").items()}
        labels = {"schema": "s5p-robust-labels/2", "labels": dict(fam["robust_labels"]),
                  "decisions_kappa3_replace": {d["test"]: drec(d) for d in fam["holm_at_kappa_robust"]},
                  "family_members": members,
                  "kappa3_family": "replace: the process-shift variants c S and F +- kappa_robust delta_M1",
                  "diagnostics": {"frozen_boolean_robust_to_the_sub_fine_residual":
                                  dict(fam["frozen_boolean_equivalent_diagnostic"]),
                                  "keep_both": {"family": "claim variants union F +- kappa_robust delta_M1",
                                                "labels": dict(fam["keep_both_kappa3_diagnostic"]["labels"])}},
                  "evaluate_sha256": "e" * 64, "design_sha256": "d" * 64, "alpha_family": 0.05,
                  "code_sha256": "c" * 64, "ruling": "RULING-20260929-s5p-A7-robustness-flag.md",
                  "evaluate": "/x/joint-evaluate.json"}
        return prod, labels

    def cmp(self, prod, labels):
        import s5p_recompute_compare as C
        return C.compare(self.mine, prod, labels, prod_sha256="e" * 64)

    def test_the_fixture_has_production_s_observed_layout(self):
        prod, labels = self.observed()
        self.assertEqual(_signature(prod), self.sig["joint-evaluate.json"])
        self.assertEqual(_signature(labels), self.sig["robust-labels.json"])

    def test_the_observed_layout_agrees_with_everything_accounted_for(self):
        prod, labels = self.observed()
        rep = self.cmp(prod, labels)
        self.assertEqual(rep["verdict"], "AGREE", (rep["discrepancies"][:3], rep["not_located"][:5],
                                                   rep["unresolved_production_leaves"][:5]))
        excl = {e["path"].split(":", 1)[1] for e in rep["excluded_by_scope"]["paths"]}
        self.assertTrue(all(p == "schema" or p.endswith("/rule") or p.startswith("lateral_symmetry/") or
                            p in ("code_sha256", "ruling", "evaluate", "kappa3_family", "diagnostics/keep_both/family")
                            for p in excl), excl)
        own = rep["a16_recompute_own_reading_rows"]
        self.assertGreater(own["items"], 0)
        self.assertLess(own["agree"], own["items"])  # the own reading differs and still does not enter the verdict

    def mutate(self, f):
        prod, labels = self.observed()
        f(prod, labels)
        return self.cmp(prod, labels)

    def test_each_new_mapping_detects_a_changed_value(self):
        G, M = "GiBUU_2019", "MnvTune_v1"
        nt0 = self.mine["nulls"][G]["tests"]["total"]["null_T_by_variant"]["m1=+2"]
        cases = {
            "holm p_holm": lambda p, l: p["holm_point"][f"{G}:total"].__setitem__("p_holm", 0.5),
            "holm reject": lambda p, l: p["holm_point"][f"{G}:shape"].__setitem__(
                "reject", not p["holm_point"][f"{G}:shape"]["reject"]),
            "holm p_raw": lambda p, l: p["holm_point"][f"{M}:total"].__setitem__("p_raw", 0.123),
            "variant tail_interval": lambda p, l: p["tests"][G]["variants"]["0.5"]["total"].__setitem__(
                "tail_interval", [0.0, 0.9]),
            "variant B": lambda p, l: p["tests"][G]["variants"]["m1-2"]["shape"].__setitem__("B", 7),
            "variant level": lambda p, l: p["tests"][M]["variants"]["1.0"]["total"].__setitem__("level", 0.9),
            "robustness variant interval": lambda p, l: p["tests"][G]["robustness_variants"]["m1+3"]["total"].__setitem__(
                "tail_interval", [0.0, 0.8]),
            "claim tail_interval": lambda p, l: p["tests"][M]["shape"].__setitem__("tail_interval", [0.1, 0.2]),
            "robust tail_interval (no M1: the claim)": lambda p, l: p["tests"][M]["total_robust"].__setitem__(
                "tail_interval", [0.1, 0.2]),
            "null-T median": lambda p, l: p["tests"][G]["variants"]["0.0"].__setitem__("null_T_total_median", 1.0),
            "null-T SD in the recompute's own (ddof 1) reading": lambda p, l: p["tests"][G]["variants"]["m1+2"].__setitem__(
                "null_T_total_sd", nt0["sd_ddof1"]),
            "median shift in the recompute's own reading": lambda p, l: p["tests"][G]["variants"]["m1+2"][
                "median_shift_in_null_sd"].__setitem__("total", self.mine["nulls"][G]["tests"]["total"][
                    "median_shift_in_null_sd"]["m1=+2"]),
            "implied size n": lambda p, l: p["tests"][G]["variants"]["0.5"]["implied_size_of_unshifted_test"][
                "shape"].__setitem__("n", 3),
            "implied size interval": lambda p, l: p["tests"][G]["variants"]["1.0"]["implied_size_of_unshifted_test"][
                "total"].__setitem__("interval", [0.0, 1.0]),
            "implied size alpha": lambda p, l: p["tests"][M]["variants"]["0.5"]["implied_size_of_unshifted_test"][
                "total"].__setitem__("alpha", 0.01),
            "shift a": lambda p, l: p["tests"][G]["shift"].__setitem__("a", 99.0),
            "shift mode": lambda p, l: p["tests"][M]["shift"].__setitem__("mode", "other"),
            "shift n_pairs": lambda p, l: p["tests"][M]["shift"].__setitem__("n_pairs", 15),
            "power alpha": lambda p, l: p["power"]["P1_a1.0"]["total"]["0.005"]["unshifted"].__setitem__("alpha", 0.05),
            "power B": lambda p, l: p["power"]["P1_a1.0"]["shape"]["0.05"]["claim_rule_determined"].__setitem__("B", 1),
            "power n": lambda p, l: p["power"]["P1_a1.0"]["shape"]["0.05"]["claim_rule"].__setitem__("n", 99),
            "power levels": lambda p, l: p["power"].__setitem__("levels", [0.05, 0.01]),
        }
        for name, mut in cases.items():
            with self.subTest(name):
                rep = self.mutate(mut)
                self.assertEqual(rep["verdict"], "DISCREPANT", (name, rep["not_located"][:3],
                                                                rep["unresolved_production_leaves"][:3]))

    def test_missing_or_unknown_content_is_incomplete(self):
        G = "GiBUU_2019"
        cases = {
            "holm p_holm removed": lambda p, l: p["holm_point"][f"{G}:total"].pop("p_holm"),
            "keep-both family removed": lambda p, l: l["diagnostics"]["keep_both"].pop("family"),
            "keep-both family empty": lambda p, l: l["diagnostics"]["keep_both"].__setitem__("family", "  "),
            "an unknown variant field": lambda p, l: p["tests"][G]["variants"]["0.5"].__setitem__("new_stat", 1.5),
            "a container at a rule path": lambda p, l: p["tests"][G]["total"].__setitem__("rule", {"x": 1}),
            "a container for a family text": lambda p, l: l.__setitem__("kappa3_family", {"x": "y"}),
        }
        for name, mut in cases.items():
            with self.subTest(name):
                self.assertEqual(self.mutate(mut)["verdict"], "INCOMPLETE", name)

    def test_holm_classical_adjusted_p(self):
        hc = self.mine["family"]["holm_point_classical"]
        dec = self.mine["family"]["decisions"]
        ps = [(d["test"], hc[d["test"]]["p_raw"]) for d in dec]
        m = len(ps)
        order = sorted(range(m), key=lambda i: (ps[i][1], i))
        run = 0.0
        for step, i in enumerate(order):  # an independent restatement: p_holm = max over earlier steps
            run = max(run, min(1.0, (m - step) * ps[i][1]))
            self.assertAlmostEqual(hc[ps[i][0]]["p_holm"], run, places=15)
            self.assertEqual(hc[ps[i][0]]["reject"], hc[ps[i][0]]["p_holm"] <= 0.05)

    def test_a16_ruled_summaries_are_their_definitions(self):
        tr = self.mine["nulls"]["GiBUU_2019"]["tests"]["total"]
        for n, v in tr["null_T_by_variant"].items():
            B = self.mine["nulls"]["GiBUU_2019"]["B"]
            self.assertAlmostEqual(v["sd_ddof0"], v["sd_ddof1"] * np.sqrt((B - 1) / B), places=12)
        base = tr["null_T_by_variant"]["c=0"]
        for n, x in tr["median_shift_in_null_sd_A16_ruled"].items():
            self.assertAlmostEqual(x, (tr["null_T_by_variant"][n]["median"] - base["median"]) / base["sd_ddof0"],
                                   places=12)
