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
        self.assertEqual(cal["partials_excluded"], 1)
        self.assertEqual(cal["missing_seeds_in_range"], [SEED_BASE["MnvTune_v1"] + 7, SEED_BASE["MnvTune_v1"] + 33])
        self.assertEqual(cal["seeds_outside_final_range"], [SEED_BASE["MnvTune_v1"] + 75])
        self.assertEqual(cal["products_used"], 58)
        self.assertFalse(cal["count_matches_final_B"])

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
        prods, _ = ev.load_ensemble(t.design()["nulls"]["MnvTune_v1"]["calibration_glob"], SEED_BASE["MnvTune_v1"], None)
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
    """The comparer's verdict: AGREE only when every production leaf is consumed or excluded by the documented
    scope; an unmapped required field, an unknown variant name or a missing labels file leaves it INCOMPLETE; a
    changed value makes it DISCREPANT. The ruled labels and the frozen keep-both fields are compared separately."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="s5p_recompute_cmp_"))
        t = Toy(self.dir / "w")
        t.calibration("MnvTune_v1", 60)
        t.calibration("GiBUU_2019", 60)
        self.mine = R.jsonable(R.evaluate(t.design(), t.v_path, t.contract, log=lambda *a: None))

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def production_like(self):
        m = self.mine
        tests, dec, hp, rk, rb = {}, {}, {}, {}, {}
        for key, rec in m["nulls"].items():
            tests[key] = {"domain_cells": rec["domain_cells"], "T_total_obs": rec["observed_T"]["total"],
                          "T_shape_obs": rec["observed_T"]["shape"]}
            for t in ("total", "shape"):
                tests[key][t] = {x: rec["tests"][t][x] for x in ("p", "k", "B")}
        rob = {d["test"]: d["decision"] for d in m["family"]["keep_both_kappa3_diagnostic"]["holm"]}  # frozen field
        for d in m["family"]["decisions"]:
            key, t = d["test"].split(":")
            dec.setdefault(key, {})[t] = d["decision"]
            hp.setdefault(key, {})[t] = d["holm_point"]
            rk.setdefault(key, {})[t] = rob[d["test"]]
            rb.setdefault(key, {})[t] = m["family"]["frozen_boolean_equivalent_diagnostic"][d["test"]]
        prod = {"schema": "x", "v_sha256": m["provenance"]["V"]["sha256"], "names": m["names"], "tests": tests,
                "decisions": dec, "holm_point": hp, "decisions_robust_kappa": rk,
                "robust_to_the_sub_fine_residual": rb, "power": {}}
        labels = self.labels_v2()
        return prod, labels

    @staticmethod
    def prod_name(n):  # production-style variant names, as the campaign describes them ("0.5", "m1+3")
        return n.replace("c=", "").replace("m1=", "m1") if not n.startswith("c=") else str(float(n[2:]))

    def labels_v2(self):
        """A robust-labels.json in the campaign's schema s5p-robust-labels/2 (flat '<null>:<test>' keys)."""
        m = self.mine
        m.setdefault("inputs", {})["design_sha256"] = "d" * 64
        fam = m["family"]
        members = lambda which: {f"{k}:{t}": [self.prod_name(n) for n in  # noqa: E731
                                              (r["tests"][t].get(f"robust_kappa3_{which}_kappa2") or r["tests"][t]).get("variants", {})]
                                 for k, r in m["nulls"].items() for t in ("total", "shape")}
        return {"schema": "s5p-robust-labels/2", "labels": dict(fam["robust_labels"]),
                "decisions_kappa3_replace": {d["test"]: {x: d[x] for x in ("p", "k", "B", "threshold", "interval",
                                                                          "level", "decision")}
                                             for d in fam["holm_at_kappa_robust"]},
                "family_members": members("replace"),
                "diagnostics": {"frozen_boolean_robust_to_the_sub_fine_residual":
                                dict(fam["frozen_boolean_equivalent_diagnostic"]),
                                "keep_both": {"family": members("retain"),
                                              "labels": dict(fam["keep_both_kappa3_diagnostic"]["labels"])}},
                "evaluate_sha256": "e" * 64, "design_sha256": "d" * 64, "alpha_family": 0.05,
                "code_sha256": "c" * 64, "ruling": "RULING-20260929-s5p-A7-robustness-flag.md"}

    def test_agree_only_when_everything_is_accounted_for(self):
        import s5p_recompute_compare as C
        prod, labels = self.production_like()
        rep = C.compare(self.mine, prod, labels, prod_sha256="e" * 64)
        self.assertEqual((rep["verdict"], rep["discrepancies"], rep["unresolved_production_leaves"],
                          rep["not_located"], rep["pending_ruling"]), ("AGREE", [], [], [], []))
        self.assertEqual(rep["excluded_by_scope"]["counts"], {"schema": 1})
        items = {r["item"].split(":")[0] + ":" + r["item"].split(":")[1] for r in rep["rows"]
                 if r["item"].startswith("robust-labels.json")}
        for f in ("labels", "decisions_kappa3_replace", "family_members",
                  "diagnostics/frozen_boolean_robust_to_the_sub_fine_residual", "diagnostics/keep_both/labels",
                  "diagnostics/keep_both/family", "evaluate_sha256", "design_sha256", "alpha_family"):
            self.assertIn(f"robust-labels.json:{f}", items)

    def test_unmapped_required_field_blocks_agreement(self):
        import s5p_recompute_compare as C
        prod, labels = self.production_like()
        prod["tests"]["GiBUU_2019"]["total"]["some_new_quantity"] = 0.3
        rep = C.compare(self.mine, prod, labels, prod_sha256="e" * 64)
        self.assertEqual(rep["verdict"], "INCOMPLETE")
        self.assertEqual([u["path"] for u in rep["unresolved_production_leaves"]],
                         ["tests/GiBUU_2019/total/some_new_quantity"])
        prod, labels = self.production_like()
        prod["family_summary"] = {"rejections": 1}  # an unknown top-level field is required too
        self.assertEqual(C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["verdict"], "INCOMPLETE")

    def test_unknown_variant_name_is_unresolved(self):
        import s5p_recompute_compare as C
        k0 = self.mine["nulls"]["GiBUU_2019"]["tests"]["total"]["variants"]["c=0"]["k"]
        prod, labels = self.production_like()
        prod["tests"]["GiBUU_2019"]["variants"] = [{"label": "0.0", "total": {"k": k0}},
                                                   {"label": "kappa-two-up", "total": {"k": 3}}]
        rep = C.compare(self.mine, prod, labels, prod_sha256="e" * 64)
        self.assertEqual(rep["discrepancies"], [])
        self.assertEqual(rep["verdict"], "INCOMPLETE")
        self.assertIn("tests/GiBUU_2019/variants/1/total/k", [u["path"] for u in rep["unresolved_production_leaves"]])
        self.assertNotIn("tests/GiBUU_2019/variants/0/total/k", [u["path"] for u in rep["unresolved_production_leaves"]])
        # a parsable production name ("m1+2") maps to the recompute's "m1=+2": a wrong count is then a discrepancy
        kp2 = self.mine["nulls"]["GiBUU_2019"]["tests"]["total"]["variants"]["m1=+2"]["k"]
        prod["tests"]["GiBUU_2019"]["variants"][1] = {"label": "m1+2", "total": {"k": kp2 + 1}}
        bad = C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["discrepancies"]
        self.assertEqual([b["item"] for b in bad], ["GiBUU_2019:total:variants[m1+2]:k"])

    def test_excluded_metadata_does_not_block(self):
        import s5p_recompute_compare as C
        prod, labels = self.production_like()
        prod.update({"utc": "2026-10-01T00:00:00Z", "lateral_symmetry": {"BeamAngleX": {"corr": -0.3}},
                     "shrinkage": 0.015})
        rep = C.compare(self.mine, prod, labels, prod_sha256="e" * 64)
        self.assertEqual(rep["verdict"], "AGREE")
        self.assertEqual(rep["excluded_by_scope"]["counts"], {"schema": 1, "utc": 1, "lateral_symmetry": 1,
                                                              "shrinkage": 1})

    def test_discrepancy_and_missing_inputs(self):
        import s5p_recompute_compare as C
        prod, labels = self.production_like()
        prod["tests"]["GiBUU_2019"]["shape"]["k"] += 1
        self.assertEqual(C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["verdict"], "DISCREPANT")
        prod, labels = self.production_like()
        self.assertEqual(C.compare(self.mine, prod, None)["verdict"], "INCOMPLETE")
        prod, labels = self.production_like()
        del prod["robust_to_the_sub_fine_residual"]
        rep = C.compare(self.mine, prod, labels, prod_sha256="e" * 64)
        self.assertEqual((rep["verdict"], rep["not_located"]), ("INCOMPLETE", ["robust_to_the_sub_fine_residual"]))
        prod, labels = self.production_like()
        first = next(iter(labels["labels"]))
        labels["labels"][first] = "something else"
        self.assertEqual(C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["verdict"], "DISCREPANT")

    def test_ruled_labels_and_frozen_keep_both_fields_are_compared_separately(self):
        import s5p_recompute_compare as C
        prod, labels = self.production_like()
        fam = self.mine["family"]
        test = fam["decisions"][2]["test"]
        null, t = test.split(":")
        # production's labels file must carry the RULED (replace) label: the keep-both label is not accepted there
        wrong = R.NOT_ROBUST if fam["robust_labels"][test] != R.NOT_ROBUST else R.ROBUST
        labels["labels"][test] = wrong
        bad = {r["item"] for r in C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["discrepancies"]}
        self.assertEqual(bad, {f"robust-labels.json:labels:{test}"})
        # a family member set that differs (the keep-both members reported as the ruled family) is a discrepancy
        prod, labels = self.production_like()
        labels["family_members"]["GiBUU_2019:total"] = labels["diagnostics"]["keep_both"]["family"]["GiBUU_2019:total"]
        bad = {r["item"] for r in C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["discrepancies"]}
        self.assertEqual(bad, {"robust-labels.json:family_members:GiBUU_2019:total"})
        # an unparsable member name is never guessed: UNRESOLVED
        prod, labels = self.production_like()
        labels["family_members"]["GiBUU_2019:shape"] = ["c-half", "m1+3"]
        rep = C.compare(self.mine, prod, labels, prod_sha256="e" * 64)
        self.assertEqual(rep["verdict"], "INCOMPLETE")
        self.assertIn("robust-labels.json/family_members/GiBUU_2019:shape",
                      [u["path"] for u in rep["unresolved_production_leaves"]])
        # the frozen decisions_robust_kappa is checked against the keep-both diagnostic, not the ruled re-run
        prod, labels = self.production_like()
        ruled = {d["test"]: d["decision"] for d in fam["holm_at_kappa_robust"]}
        keep = {d["test"]: d["decision"] for d in fam["keep_both_kappa3_diagnostic"]["holm"]}
        self.assertEqual(prod["decisions_robust_kappa"][null][t], keep[test])
        self.assertEqual(C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["verdict"], "AGREE")
        if ruled != keep:  # where the families differ, the frozen field must still match keep-both
            diff = next(k for k in ruled if ruled[k] != keep[k])
            n2, t2 = diff.split(":")
            prod["decisions_robust_kappa"][n2][t2] = ruled[diff]
            self.assertEqual(C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["verdict"], "DISCREPANT")

    def test_labels_doc_provenance_and_unknown_fields(self):
        import s5p_recompute_compare as C
        prod, labels = self.production_like()
        self.assertEqual(C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["verdict"], "AGREE")
        self.assertEqual(C.compare(self.mine, prod, labels, prod_sha256="f" * 64)["verdict"], "DISCREPANT")
        labels["labels_new_name"] = {"MnvTune_v1:total": "x"}
        rep = C.compare(self.mine, prod, labels, prod_sha256="e" * 64)
        self.assertEqual(rep["verdict"], "INCOMPLETE")
        self.assertEqual([u["path"] for u in rep["unresolved_production_leaves"]],
                         ["robust-labels.json/labels_new_name/MnvTune_v1:total"])

    def test_production_variant_names_parse(self):
        # the exact names the frozen evaluator writes (campaign, 2026-09-29): str(float(c)) and f"m1{sign}{kappa}"
        import s5p_recompute_compare as C
        prod_names = ["0.0", "0.5", "1.0", "m1+2", "m1-2", "m1+3", "m1-3"]
        mine = ["c=0", "c=0.5", "c=1", "m1=+2", "m1=-2", "m1=+3", "m1=-3"]
        self.assertEqual(sorted(map(C.variant_key, prod_names)), sorted(map(C.variant_key, mine)))

    def test_null_not_calibrated_at_B0_is_located(self):
        import s5p_recompute_compare as C
        d = Path(tempfile.mkdtemp(prefix="s5p_recompute_b0_"))
        try:
            t = Toy(d / "w")
            t.calibration("MnvTune_v1", 60)
            t.status("GiBUU_2019", 0, True, "budget")
            self.mine = R.jsonable(R.evaluate(t.design(), t.v_path, t.contract, log=lambda *a: None))
            prod, labels = self.production_like()
            prod["tests"]["GiBUU_2019"] = {"not_calibrated": "budget stop at B = 0"}
            for fam in ("family_members",):
                labels[fam]["GiBUU_2019:total"] = labels[fam]["GiBUU_2019:shape"] = []
            rep = C.compare(self.mine, prod, labels, prod_sha256="e" * 64)
            self.assertEqual((rep["verdict"], rep["not_located"]), ("AGREE", []))
            self.assertIn("GiBUU_2019:not_calibrated", [r["item"] for r in rep["rows"]])
            self.mine["nulls"]["GiBUU_2019"]["B"] = 5  # a recompute that did calibrate it disagrees
            self.assertEqual(C.compare(self.mine, prod, labels, prod_sha256="e" * 64)["verdict"], "DISCREPANT")
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_variant_names_are_parsed_never_guessed(self):
        import s5p_recompute_compare as C
        self.assertEqual([C.variant_key(n) for n in ("c=0.5", "0.5", "m1=+3", "m1+3", "m1-2")],
                         [("c", 0.5), ("c", 0.5), ("m1", 3.0), ("m1", 3.0), ("m1", -2.0)])
        self.assertIsNone(C.variant_key("kappa3"))

    def test_exit_codes(self):
        import s5p_recompute_compare as C
        prod, labels = self.production_like()
        files = {}
        import hashlib
        files["prod"] = self.dir / "prod.json"
        files["prod"].write_text(json.dumps(prod))
        labels["evaluate_sha256"] = hashlib.sha256(files["prod"].read_bytes()).hexdigest()
        for name, doc in (("mine", self.mine), ("labels", labels)):
            files[name] = self.dir / f"{name}.json"
            files[name].write_text(json.dumps(doc))
        out = str(self.dir / "cmp.json")
        self.assertEqual(C.compare_files(str(files["mine"]), str(files["prod"]), out, str(files["labels"])), 0)
        self.assertEqual(C.compare_files(str(files["mine"]), str(files["prod"]), out, None), 2)
        prod["tests"]["MnvTune_v1"]["total"]["B"] += 1
        files["prod"].write_text(json.dumps(prod))  # (its digest no longer matches the labels file either)
        self.assertEqual(C.compare_files(str(files["mine"]), str(files["prod"]), out, str(files["labels"])), 1)


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
