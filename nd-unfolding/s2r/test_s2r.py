"""Tests of the S2R arm (S2R-DECLARATION.md): the step-2 intervention against the production loop, its controls in
the direction each acts and the other, and the declared pass rule.

Run: python3 -B -m unittest nd-unfolding/s2r/test_s2r.py (no LightGBM, no ROOT, no cluster: T3's deterministic
stand-ins on FD-STAB's synthetic fine-grid inputs).
"""
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
for _p in (HERE, ND, ND / "tier3", ND / "tests", ND / "pv-ladder", ND / "prior_retention"):
    if str(_p) not in sys.path:
        sys.path.insert(1, str(_p))
import argparse  # noqa: E402
import contextlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import s2r_arm as S  # noqa: E402
import s2r_probe as SP  # noqa: E402
import s2r_read as SR  # noqa: E402
import prr_probe as P  # noqa: E402
import t3p_probe as T  # noqa: E402
import s5c_pseudo  # noqa: E402
import s5n_pseudo  # noqa: E402
from test_t3p import parse_runner, toy_bkg  # noqa: E402
import test_estimator_stability_probe as TS  # noqa: E402
import s2r_rule as RULE  # noqa: E402
import t3p_arms as A  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_trace  # noqa: E402
from test_t3p import Linear, StandIns  # noqa: E402


class Arm(StandIns, unittest.TestCase):
    def traced(self, arm, iters):
        rec = A.ArmRecorder(self.unf, self.r, self.M16, self.fm, iters)
        xs, params, tr = S.traced_unfold_s2r(self.unf, rec, 42, 1, iters, arm, self.r)
        return xs, rec, tr

    def setUp(self):
        super().setUp()
        self.saved_iters = dict(S.ITERS)
        S.ITERS.update({"B0": 4, "S2R": 4})

    def tearDown(self):
        S.ITERS.clear()
        S.ITERS.update(self.saved_iters)
        super().tearDown()

    def test_b0_is_the_production_unfold(self):
        xs, _, tr = self.traced("B0", 4)
        plain, _ = s5c_unfold.unfold(self.unf, "deterministic", 42, 1, 4)
        self.assertTrue(np.array_equal(xs, plain))
        self.assertEqual(tr.evidence["s2r_fits"], 0)

    def test_s2r_fits_step2_against_the_previous_push(self):
        """REQUIRED: the inner step-2 fit's first class carries nu_(k-1) * w_truth, nu_(k-1) being the push weights the
        loop produced at iteration k-1 (recorded from the loop's own w_push, independently of the fit)."""
        pushes = []
        orig = s5c_unfold.unfold

        import omnifold_nn_core as onc
        orig_loop = onc._reweight

        def spy(events, clf):
            out = orig_loop(events, clf)
            if getattr(clf, "_role", None) == "step2":
                pushes.append(np.array(out, copy=True))
            return out
        onc._reweight = spy
        try:
            _, rec, tr = self.traced("S2R", 4)
        finally:
            onc._reweight = orig_loop
        clf2 = self.built[-1][1]
        m = np.asarray(self.unf["pass_truth"], bool)
        wt = np.asarray(self.unf["w_truth"])[m]
        n = len(wt)
        self.assertEqual((len(clf2.weights), len(pushes)), (4, 4))
        self.assertTrue(np.array_equal(clf2.weights[0][:n], wt))  # nu_0 = 1
        for k in range(1, 4):
            self.assertTrue(np.array_equal(clf2.weights[k][:n], pushes[k - 1] * wt), k)
            self.assertFalse(np.array_equal(clf2.weights[k][:n], wt), k)
        self.assertEqual(tr.evidence["s2r_fits"], 4)
        self.assertTrue(all(d <= S.ROUND_TRIP_RTOL for d in tr.evidence["s2r_max_round_trip"]))

    def test_s2r_second_class_is_the_loops_pull(self):
        _, _, tr = self.traced("S2R", 4)
        b0 = self.built[-1][1]
        n = len(b0.weights[0]) // 2
        # the loop's second class is w_pull * w_truth, which the tracer has already checked bitwise; S2R keeps it
        self.traced("B0", 4)
        k1_b0 = self.built[-1][1].weights[0]
        self.assertTrue(np.array_equal(b0.weights[0][n:], k1_b0[n:]))

    def test_iteration_one_matches_b0_and_later_iterations_differ(self):
        _, rb, tb = self.traced("B0", 4)
        _, rs, ts = self.traced("S2R", 4)
        ab, as_ = rb.arrays(tb), rs.arrays(ts)
        self.assertTrue(np.allclose(as_["X16_push"][0], ab["X16_push"][0], rtol=1e-12, atol=0))
        self.assertFalse(np.allclose(as_["X16_push"][3], ab["X16_push"][3], rtol=1e-9, atol=0))

    def test_a_wrong_reference_is_refused(self):
        orig = S.S2RTracer.s2r_weight

        def bad(self, loop_w):
            w = orig(self, loop_w)
            self._s2r_ref = self._s2r_ref * 1.001
            return w
        S.S2RTracer.s2r_weight = bad
        try:
            with self.assertRaises(s5e_trace.TraceError):
                self.traced("S2R", 2)
        finally:
            S.S2RTracer.s2r_weight = orig

    def test_a_broken_round_trip_is_refused(self):
        orig = S.S2RTracer.s2r_output

        def bad(self, inner):
            out = orig(self, inner)
            self._s2r_q = self._s2r_q * (1 + 1e-6)
            return out
        S.S2RTracer.s2r_output = bad
        try:
            with self.assertRaises(s5e_trace.TraceError):
                self.traced("S2R", 2)
        finally:
            S.S2RTracer.s2r_output = orig

    def test_the_iteration_count_is_the_arms(self):
        rec = A.ArmRecorder(self.unf, self.r, self.M16, self.fm, 3)
        with self.assertRaises(s5e_trace.TraceError):
            S.traced_unfold_s2r(self.unf, rec, 42, 1, 3, "S2R", self.r)
        with self.assertRaises(ValueError):
            S.S2RTracer({"pass_reco": np.ones(2, bool), "w_truth": np.ones(2), "w_reco": np.ones(2)},
                        lambda *a: None, "MO", np.ones(2))

    def test_saturation_of_the_accumulated_ratio_stops(self):
        """B1 (codex read): where nu_(k-1) * L leaves the loop's clip range, the loop would saturate it: C-ARM STOPs."""
        saved = Linear.predict_proba
        Linear.predict_proba = lambda self, X: np.column_stack([np.ones(len(X)), np.zeros(len(X))])
        try:
            with self.assertRaisesRegex(s5e_trace.TraceError, "outside"):
                self.traced("S2R", 4)
        finally:
            Linear.predict_proba = saved

    def test_saturation_bounds_sit_inside_the_loops_clip(self):
        lo, hi = S.Q_LOW, S.Q_HIGH
        self.assertGreater(lo, S.CLIP / (1 - S.CLIP))
        self.assertLess(hi, (1 - S.CLIP) / S.CLIP)
        for q in (lo * 1.0001, 1.0, hi * 0.9999):  # inside: the loop's odds return q to 1e-10
            p = q / (1 + q)
            self.assertLess(abs(s5e_trace.reweight_like_loop(np.array([[1 - p, p]]))[0] / q - 1), S.ROUND_TRIP_RTOL)


class Rule(unittest.TestCase):
    B0 = {"A7_gibuu": 0.125, "q3": 0.1785}

    def verdict(self, g, q, nominal_flag=False, b0=None):
        return RULE.verdict({"A7_gibuu": g, "q3": q}, b0 or self.B0, nominal_flag)

    def test_passes_only_when_both_truths_clear_the_bar(self):
        self.assertEqual(self.verdict(0.07, 0.12)["verdict"], "PASS")
        self.assertEqual(self.verdict(0.08, 0.12)["verdict"], "FAIL")  # GiBUU short
        self.assertEqual(self.verdict(0.07, 0.13)["verdict"], "FAIL")  # q3 short
        self.assertEqual(self.verdict(0.20, 0.20)["verdict"], "FAIL")  # worse

    def test_the_bar_is_inclusive_and_each_operand_counts(self):
        self.assertEqual(self.verdict(0.125 - 0.05, 0.1785 - 0.05)["verdict"], "PASS")
        self.assertEqual(self.verdict(0.125 - 0.05 + 1e-9, 0.1785 - 0.05)["verdict"], "FAIL")
        self.assertEqual(self.verdict(0.07, 0.12, b0={"A7_gibuu": 0.11, "q3": 0.1785})["verdict"], "FAIL")
        self.assertEqual(self.verdict(0.07, 0.12, b0={"A7_gibuu": 0.125, "q3": 0.16})["verdict"], "FAIL")

    def test_a_nominal_flag_fails_and_an_undefined_rho_fails(self):
        self.assertEqual(self.verdict(0.07, 0.12, nominal_flag=True)["verdict"], "FAIL")
        self.assertEqual(self.verdict(None, 0.12)["verdict"], "FAIL")
        self.assertEqual(self.verdict(0.07, 0.12, b0={"A7_gibuu": None, "q3": 0.1785})["verdict"], "FAIL")

    def test_the_declared_constants(self):
        self.assertEqual(RULE.BAR, 0.05)
        self.assertEqual(RULE.TRUTHS, ("A7_gibuu", "q3"))
        self.assertEqual(S.GRADE_K, 5)


if not hasattr(os, "O_NOATIME"):  # macOS: REF-G1's copy reads os.O_NOATIME at each open; a 0 flag is a plain read
    os.O_NOATIME = 0
REPO = ND.parent


class Constants(unittest.TestCase):
    def test_tasks(self):
        tasks = SP.all_tasks()
        self.assertEqual(len(tasks), 6)
        self.assertEqual(set(tasks), {(a, t, 991000) for a in ("B0", "S2R") for t in ("nominal", "A7_gibuu", "q3")})
        self.assertEqual(S.ITERS, {"B0": 5, "S2R": 20})

    def test_price_and_limit(self):
        pr = SP.price()
        self.assertGreaterEqual(pr["limit_h"], pr["least_limit_h"])
        self.assertEqual(pr["least_limit_h"], 1.0)
        self.assertEqual(pr["cap_node_h"], 1.0)
        self.assertEqual(pr["wall_h"], 2100.0 / 3600)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(SP.main(["limit"]), 0)
        self.assertEqual(buf.getvalue().strip(), "1:00:00")

    def test_pins_hold(self):
        P.check_pins(SP.CODE_PINS)
        self.assertIn("nd-unfolding/tier3/t3p_arms.py", SP.CODE_PINS)
        self.assertIn("nd-unfolding/tier3/t3p_probe.py", SP.CODE_PINS)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(P.Refused):
            P.check_pins(SP.CODE_PINS, Path(d))


class Queues(unittest.TestCase):
    def setUp(self):
        self.a = SP.staged_paths(Path("/S/stage"), Path("/S/runs"), Path("/S/stage.json"))

    def lines(self):
        for ln in SP.queue_lines(self.a)[1:]:
            yield ln.split("\t")

    def test_every_line_passes_the_runners_parse_and_the_check(self):
        n = 0
        for cols in self.lines():
            argv = cols[4:]
            arm, truth = argv[argv.index("--arm") + 1], argv[argv.index("--truth") + 1]
            ns = parse_runner(argv[argv.index("--") + 1:])
            self.assertIsNone(SP.check_namespace(ns, arm, truth), cols[0])
            self.assertEqual(cols[0], SP.task_id(arm, truth))
            self.assertEqual(float(cols[2]), SP.TASK_S[arm])
            self.assertEqual(cols[3], "s2r/s2r_probe.py")
            n += 1
        self.assertEqual(n, 6)

    def test_lines_are_fd_prrs_b0_line_but_for_three_fields(self):
        for arm, t, s in SP.all_tasks():
            ours = SP.runner_argv(self.a, arm, t, s)
            base = P.runner_argv(self.a, "B0", t, s)
            self.assertEqual(len(ours), len(base))
            diff = {base[i - 1] for i in range(1, len(base)) if base[i] != ours[i]}
            self.assertLessEqual(diff, {"--iters", "--tag", "--out"})
            self.assertEqual(ours[ours.index("--iters") + 1], str(S.ITERS[arm]))
        b0 = SP.runner_argv(self.a, "B0", "q3")
        self.assertEqual(b0[b0.index("--iters") + 1], "5")  # FD-PRR's B0 line, unchanged in its iterations

    def test_the_refusals_fire_on_the_runners_parse(self):
        good = parse_runner(SP.runner_argv(self.a, "S2R", "q3"))
        self.assertIsNone(SP.check_namespace(good, "S2R", "q3"))
        cases = {"iters": 5, "capacity": "400,31", "mc_fraction": "quarter", "pseudo_seeds": "991000:991001",
                 "estimator_seed": 43, "threads": 8, "tag": "s2r_B0_q3", "config": None,
                 "hypothesis": "docs/orchestration/state/s5p/ratios/nullsF/null-gibuu_cv-F.json",
                 "alternative_amplitude": 0.5, "expectation": False, "no_nuisance": False}
        for k, v in cases.items():
            ns = argparse.Namespace(**vars(good))
            setattr(ns, k, v)
            self.assertIsNotNone(SP.check_namespace(ns, "S2R", "q3"), k)
        ns = argparse.Namespace(**vars(good))
        ns.pseudo_seeds = "994001:994001"
        self.assertIsNotNone(SP.check_namespace(ns, "S2R", "q3"))
        self.assertIsNotNone(SP.check_namespace(good, "B0", "q3"))  # B0 runs 5 iterations
        for k, v in {"alternative": Path("docs/elsewhere.json"), "alternative_truth": "eavail_tilt",
                     "out": Path("/S/elsewhere/S2R/q3"), }.items():
            ns = argparse.Namespace(**vars(good))
            setattr(ns, k, v)
            self.assertIsNotNone(SP.check_namespace(ns, "S2R", "q3"), k)
        ns = argparse.Namespace(**vars(good))
        ns.out = Path("/S/runs/B0/q3")
        self.assertIsNotNone(SP.check_namespace(ns, "S2R", "q3"))
        self.assertIsNotNone(SP.check_namespace(good, "S2R", "A7_gibuu"))  # q3's hypothesis


class Sources(unittest.TestCase):
    def test_sources(self):
        src = SP.sources()
        roles = [e["role"] for e in src]
        self.assertEqual(len(src), len(set(roles)))
        self.assertEqual(len({e["name"] for e in src}), len(src))
        self.assertEqual(sorted(r for r in roles if r.startswith("prr_")),
                         ["prr_B0_A7_gibuu_s991000", "prr_B0_nominal_s991000", "prr_B0_q3_s991000"])
        self.assertEqual([r for r in roles if r.startswith("rho_")], ["rho_gibuu_cv-F"])
        self.assertEqual({"of_inputs_5d", "bkg_dump", "bank_cv", "closure_ratio_nuwro"} - set(roles), set())
        dig = T.prr_digests()
        for e in src:
            if e["role"].startswith("prr_"):
                self.assertEqual(e["sha256"], dig[e["src"][len(T.PRR_OUT) + 1:]])
        base = {e["role"]: e["sha256"] for e in P.SOURCES}
        for e in src:
            if e["role"] in base:
                self.assertEqual(e["sha256"], base[e["role"]])
        self.assertTrue(all(e["src"].startswith("/pscratch/sd/j/josephrb/") for e in src))


class Install(unittest.TestCase):
    def setUp(self):
        self.inp = TS.fine_inputs(3000, 4)
        self.bkg = toy_bkg(self.inp)
        self.r = np.random.default_rng(1).uniform(0.8, 1.2, len(self.inp["MCgen"]))
        self.saved = (s5n_pseudo.truth_weight, s5n_pseudo.write_product)
        s5n_pseudo.truth_weight = lambda *a: self.r
        self.written = []
        s5n_pseudo.write_product = lambda out, arrays, meta: self.written.append((arrays, meta)) or 0

    def tearDown(self):
        s5n_pseudo.truth_weight, s5n_pseudo.write_product = self.saved

    def test_r_is_captured_on_the_unfolding_half(self):
        split = s5c_pseudo.split_key_for(SP.SEED)
        with SP.install("S2R", "q3", rho=None, guard=False) as st:
            s5n_pseudo.build_pseudo(self.inp, self.bkg, "hypothesis", 1.0, split, SP.SEED, None)
        is_b = s5c_pseudo.half_mask(len(self.inp["MCgen"]), split)
        self.assertTrue(np.array_equal(st["r_A"], self.r[~is_b]))
        self.assertEqual(st["builds"], 1)

    def test_a_development_option_is_refused(self):
        for kw in ({"no_background": True}, {"prior_matches_truth": True}):
            with SP.install("B0", "q3", rho=None, guard=False):
                with self.assertRaises(P.Refused):
                    s5n_pseudo.build_pseudo(self.inp, self.bkg, "hypothesis", 1.0, 5, 6, None, **kw)

    def test_no_product_without_the_check_or_the_steps_or_the_refinement(self):
        with SP.install("B0", "q3", rho=None, guard=True):
            with self.assertRaisesRegex(RuntimeError, "never checked"):
                s5n_pseudo.write_product(Path("x.npz"), {}, {})
        with SP.install("B0", "q3", rho=None, guard=False):
            with self.assertRaisesRegex(RuntimeError, "0 builds, 0 unfolds"):
                s5n_pseudo.write_product(Path("x.npz"), {}, {})
        self.assertEqual(self.written, [])

    def test_unfold_one_refuses_a_missing_r_a_mismatched_r_or_a_substitute(self):
        import s5p_numerics
        split = s5c_pseudo.split_key_for(SP.SEED)
        with SP.install("S2R", "q3", rho=None, guard=False):
            with self.assertRaises(P.Refused):
                s5p_numerics.unfold_one({"MCgen": np.zeros((3, 5))}, np.float32, 42, 1, 20)
            exp, _, _ = s5n_pseudo.build_pseudo(self.inp, self.bkg, "hypothesis", 1.0, split, SP.SEED, None)
            with self.assertRaises(P.Refused):
                s5p_numerics.unfold_one({"MCgen": np.zeros((3, 5))}, np.float32, 42, 1, 20)
            with self.assertRaises(P.Refused):
                s5p_numerics.unfold_one(exp, np.float32, 42, 1, 20, unfold_fn=lambda *a: None)

    def test_unknown_arm_or_truth_and_restore(self):
        import s5p_numerics
        import s5p_truths
        for arm, t in (("MO", "q3"), ("S2R", "W1")):
            with self.assertRaises(ValueError):
                with SP.install(arm, t, rho=None):
                    pass
        before = (argparse.ArgumentParser.parse_args, s5n_pseudo.build_pseudo, s5p_numerics.unfold_one,
                  s5p_truths.load_fine_rho, s5n_pseudo.write_product)
        with self.assertRaises(KeyError):
            with SP.install("S2R", "q3", rho=None):
                raise KeyError("x")
        after = (argparse.ArgumentParser.parse_args, s5n_pseudo.build_pseudo, s5p_numerics.unfold_one,
                 s5p_truths.load_fine_rho, s5n_pseudo.write_product)
        self.assertEqual(before, after)

    def test_the_rho_loader_reads_only_a_staged_copy(self):
        import s5p_truths
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "rho.npz"
            np.savez(p, rho=np.arange(4.0))
            sha = T.sha256_path(p)
            ratio = {"rho_npz": {"path": "/pscratch/elsewhere/rho.npz", "sha256": sha}}
            with SP.install("B0", "A7_gibuu", rho=None, guard=False):
                with self.assertRaises(P.Refused):
                    s5p_truths.load_fine_rho(ratio)
            with SP.install("B0", "A7_gibuu", rho={sha: p}, guard=False):
                self.assertTrue(np.array_equal(s5p_truths.load_fine_rho(ratio), np.arange(4.0)))


class Pair(unittest.TestCase):
    """Products and FD-PRR references in a temporary stage: identical arrays pass; one ulp fails."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.runs, stage = d / "runs", d / "stage"
        rng = np.random.default_rng(0)
        self.xt = {t: rng.uniform(1, 2, 64) * 1e-39 for t in SP.TRUTHS}
        self.xs = {t: rng.uniform(1, 2, 64) * 1e-39 for t in SP.TRUTHS}
        self.x16 = {t: rng.uniform(1, 2, 16) for t in SP.TRUTHS}
        files = []
        for t, s in SP.pair_refs():
            p = stage / T.prr_name("B0", t, s)
            p.parent.mkdir(parents=True, exist_ok=True)
            np.savez(p, xsec_flat=self.xs[t], xtrue_flat=self.xt[t])
            files.append({"role": f"prr_B0_{t}_s{s}", "copy": str(p), "sha256": T.sha256_path(p)})
        self.stage = {"dest": str(stage), "files": files}
        for arm, t, s in SP.all_tasks():
            p = SP.product_path(self.runs, arm, t, s)
            p.parent.mkdir(parents=True, exist_ok=True)
            it = S.ITERS[arm]
            x16 = np.vstack([self.x16[t] * (1 + 0.01 * k * (arm == "S2R")) for k in range(it)])
            np.savez(p, xsec_flat=self.xs[t] if arm == "B0" else self.xs[t] * 1.01, xtrue_flat=self.xt[t], X16_push=x16)

    def tearDown(self):
        self.tmp.cleanup()

    def rewrite(self, path, **change):
        with np.load(path) as z:
            arrays = {k: np.asarray(z[k]) for k in z.files}
        arrays.update(change)
        np.savez(path, **arrays)

    def test_identical_arrays_pass(self):
        res = SP.pair(self.stage, self.runs)
        self.assertTrue(res["pass"], res)
        self.assertEqual((len(res["C-PAIR"]), len(res["C-X"]), len(res["C-ONE"])), (3, 6, 3))

    def test_one_ulp_in_b0_fails_c_pair(self):
        """REQUIRED: one ulp in one cell of B0's k = 5 unfold fails C-PAIR, and names one cell."""
        x = self.xs["q3"].copy()
        x[17] = np.nextafter(x[17], np.inf)
        self.rewrite(SP.product_path(self.runs, "B0", "q3"), xsec_flat=x)
        res = SP.pair(self.stage, self.runs)
        self.assertFalse(res["pass"])
        self.assertEqual(res["C-PAIR"]["q3"]["cells_differing"], 1)
        self.assertTrue(res["C-PAIR"]["A7_gibuu"]["pass"])

    def test_one_ulp_in_the_reference_fails_c_pair(self):
        e = next(f for f in self.stage["files"] if f["role"] == "prr_B0_A7_gibuu_s991000")
        x = self.xs["A7_gibuu"].copy()
        x[3] = np.nextafter(x[3], -np.inf)
        self.rewrite(Path(e["copy"]), xsec_flat=x)
        e["sha256"] = T.sha256_path(Path(e["copy"]))
        self.assertFalse(SP.pair(self.stage, self.runs)["C-PAIR"]["A7_gibuu"]["pass"])

    def test_a_reference_not_its_pin_fails_pair_and_x(self):
        e = next(f for f in self.stage["files"] if f["role"] == "prr_B0_nominal_s991000")
        e["sha256"] = "0" * 64
        res = SP.pair(self.stage, self.runs)
        self.assertFalse(res["C-PAIR"]["nominal"]["pass"])
        self.assertFalse(res["C-X"]["s2r_S2R_nominal_s991000"]["pass"])
        self.assertFalse(res["pass"])

    def test_one_ulp_in_s2rs_truth_fails_c_x(self):
        x = self.xt["q3"].copy()
        x[0] = np.nextafter(x[0], np.inf)
        self.rewrite(SP.product_path(self.runs, "S2R", "q3"), xtrue_flat=x)
        res = SP.pair(self.stage, self.runs)
        self.assertFalse(res["C-X"]["s2r_S2R_q3_s991000"]["pass"])
        self.assertTrue(res["C-X"]["s2r_B0_q3_s991000"]["pass"])

    def test_s2r_departing_at_k1_fails_c_one(self):
        p = SP.product_path(self.runs, "S2R", "A7_gibuu")
        with np.load(p) as z:
            x16 = np.array(z["X16_push"])
        x16[0, 4] *= 1 + 1e-9
        self.rewrite(p, X16_push=x16)
        res = SP.pair(self.stage, self.runs)
        self.assertFalse(res["C-ONE"]["A7_gibuu"]["pass"])
        self.assertFalse(res["pass"])


class Read(unittest.TestCase):
    """read() on a planted run (M16 = identity): planted rho give the declared verdict in each direction."""

    def setUp(self):
        import estimator_stability_analyze as an
        self.an, self.saved = an, an.cell_matrix
        an.cell_matrix = lambda h2: np.eye(16)
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name)
        self.base = 3e-39 * (1 + np.arange(16) / 16)

    def tearDown(self):
        self.an.cell_matrix = self.saved
        self.tmp.cleanup()

    def X(self, t):
        if t == "nominal":
            return self.base.copy()
        rng = np.random.default_rng({"A7_gibuu": 1, "q3": 2}[t])
        return self.base * (1 + rng.uniform(-0.3, 0.3, 16))

    def build(self, plant, tamper=None):
        p = self.run / "stage" / T.prr_name("B0", "nominal", SP.SEED)
        p.parent.mkdir(parents=True, exist_ok=True)
        np.savez(p, xsec_flat=self.base, xtrue_flat=self.base)
        self.stage = {"dest": str(self.run / "stage"),
                      "files": [{"role": f"prr_B0_nominal_s{SP.SEED}", "copy": str(p), "sha256": T.sha256_path(p)}]}
        P_ = self.base
        for arm, t, s in SP.all_tasks():
            it = S.ITERS[arm]
            X = self.X(t)
            rows = []
            for k in range(1, it + 1):
                r, nom = plant(arm, t, k)
                rows.append(X - r * (X - P_) if t != "nominal" else X * (1 + nom))
            Xh = np.array(rows)
            Rp = 100.0 * (1 + np.arange(16) / 32)
            Rd = Rp * (1 + 0.05 * np.sin(np.arange(16)))
            arrays = {"xsec_flat": Xh[-1], "xtrue_flat": X, "X16_push": Xh, "X16_pull": Xh,
                      "R16_pull": np.array([Rd] * it), "R16_push": np.array([Rd] * it), "R16_D": Rd,
                      "R16_true": Rd * 1.001, "R16_prior": Rp, "miss_share16": np.full((it, 16), 0.3),
                      "norm_pull": np.ones(it), "norm_push": np.ones(it), "mean_fill_fail": np.ones(it),
                      "clip_step1": np.zeros((it, 2)), "clip_step2": np.zeros((it, 2)),
                      "reco_in_cells": np.array([Rp.sum(), Rd.sum()])}
            for k in A.PAIR_KS:
                if k <= it:
                    arrays[f"xs_k{k}"] = Xh[k - 1]
            meta = {"s2r": {"schema": SP.SCHEMA, "arm": arm, "truth": t, "iters": it, "evidence": {"arm": arm}}}
            if tamper and tamper[0] == (arm, t):
                tamper[1](arrays, meta)
            q = SP.product_path(self.run / "runs", arm, t, s)
            q.parent.mkdir(parents=True, exist_ok=True)
            np.savez(q, **arrays, meta=json.dumps(meta))

    def read(self, pair_ok=True):
        return SR.read(self.run / "runs", self.stage, {"pass": pair_ok}, REPO)

    @staticmethod
    def passing(arm, t, k):
        if arm == "B0":
            return {"A7_gibuu": 0.125, "q3": 0.1785}.get(t, 0.0), 0.0
        return {"A7_gibuu": 0.06, "q3": 0.11}.get(t, 0.0) if k >= 5 else 0.2, 0.0

    def test_a_planted_improvement_at_both_truths_passes_at_k5(self):
        self.build(self.passing)
        out = self.read()
        self.assertEqual(out["verdict"], "PASS", out["rule"])
        self.assertAlmostEqual(out["rule"]["per_truth"]["A7_gibuu"]["rho_B0"], 0.125)
        self.assertAlmostEqual(out["rule"]["per_truth"]["q3"]["rho_S2R"], 0.11)
        self.assertNotIn("e-39", json.dumps(out))
        self.assertIn("PASS", SR.text(out))

    def test_it_is_read_at_k5_not_at_the_end(self):
        """S2R reaches the bar only from k = 6 on: FAIL, although its k = 20 value would pass."""
        def plant(arm, t, k):
            r, n = self.passing(arm, t, k)
            return (0.2 if (arm == "S2R" and k == 5) else r), n
        self.build(plant)
        self.assertEqual(self.read()["verdict"], "FAIL")

    def test_one_truth_short_fails(self):
        for short in ("A7_gibuu", "q3"):
            def plant(arm, t, k, short=short):
                r, n = self.passing(arm, t, k)
                return (r + 0.03 if (arm == "S2R" and t == short) else r), n
            self.build(plant)
            out = self.read()
            self.assertEqual(out["verdict"], "FAIL", short)
            self.assertFalse(out["rule"]["per_truth"][short]["clears"])

    def test_a_flagged_nominal_fails(self):
        def plant(arm, t, k):
            r, n = self.passing(arm, t, k)
            return r, (0.2 if (arm == "S2R" and t == "nominal") else 0.0)
        self.build(plant)
        out = self.read()
        self.assertTrue(out["rule"]["nominal_flagged"])
        self.assertEqual(out["verdict"], "FAIL")

    def test_controls_stop(self):
        self.build(self.passing)
        with self.assertRaises(SR.Stop):
            self.read(pair_ok=False)

        def bad_trace(arrays, meta):
            arrays["xs_k5"] = arrays["xs_k5"] * (1 + 1e-9)
        self.build(self.passing, tamper=(("S2R", "q3"), bad_trace))
        with self.assertRaises(SR.Stop):
            self.read()

        def no_k5(arrays, meta):
            del arrays["xs_k5"]
        self.build(self.passing, tamper=(("S2R", "q3"), no_k5))
        with self.assertRaisesRegex(SR.Stop, "snapshots"):
            self.read()

        def bad_meta(arrays, meta):
            meta["s2r"]["iters"] = 50
        self.build(self.passing, tamper=(("B0", "A7_gibuu"), bad_meta))
        with self.assertRaises(SR.Stop):
            self.read()

    def test_a_prior_not_its_pin_stops(self):
        self.build(self.passing)
        self.stage["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(SR.Stop):
            self.read()


class JobScript(unittest.TestCase):
    """sbatch_s2r.sh's refusals, run locally (S2R_SMOKE) against a git deploy whose nd-unfolding links to this one."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.deploy, self.out, self.bin = d / "deploy", d / "out", d / "bin"
        self.deploy.mkdir()
        (self.deploy / "nd-unfolding").symlink_to(ND)
        (self.deploy / "docs").symlink_to(REPO / "docs")
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t"}
        for c in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "deploy"]):
            subprocess.run(["git", "-C", str(self.deploy), *c], check=True, env=env, capture_output=True)
        self.pin = subprocess.run(["git", "-C", str(self.deploy), "rev-parse", "HEAD"], capture_output=True,
                                  text=True, check=True).stdout.strip()
        self.out.mkdir()
        self.bin.mkdir()
        self.sacct("")
        (self.bin / "squeue").write_text("#!/bin/bash\necho squeue-was-called >&2\nexit 99\n")
        (self.bin / "squeue").chmod(0o755)

    def tearDown(self):
        self.tmp.cleanup()

    def sacct(self, lines, rc=0):
        p = self.bin / "sacct"
        p.write_text(f"#!/bin/bash\nprintf '%s\\n' '{lines}'\nexit {rc}\n")
        p.chmod(0o755)

    def sh(self, pin=None, **env):
        e = {**os.environ, "S2R_SMOKE": "1", "PATH": f"{self.bin}:{os.environ['PATH']}", **env}
        e.pop("SLURM_JOB_ID", None)
        p = subprocess.run(["bash", str(HERE / "sbatch_s2r.sh"), str(self.deploy), pin or self.pin, str(self.out)],
                           capture_output=True, text=True, env=e, timeout=120)
        self.assertNotIn("squeue-was-called", p.stderr)
        return p.returncode, p.stderr

    def test_a_deploy_not_at_its_pin_refuses(self):
        rc, err = self.sh(pin="0" * 40)
        self.assertEqual(rc, 2)
        self.assertIn("deploy HEAD", err)

    def test_out_is_pinned_outside_a_smoke(self):
        e = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "SLURM_JOB_ID": "1", "SLURM_JOB_NAME": "s2r_run"}
        e.pop("S2R_SMOKE", None)
        p = subprocess.run(["bash", str(HERE / "sbatch_s2r.sh"), str(self.deploy), self.pin, str(self.out)],
                           capture_output=True, text=True, env=e, timeout=120)
        self.assertEqual(p.returncode, 2)
        self.assertIn("is not the declared /pscratch/sd/j/josephrb/s2r-20261124", p.stderr)

    def test_a_wrong_job_name_refuses(self):
        rc, err = self.sh(S2R_NAME="t3p_dry")
        self.assertEqual(rc, 2)
        self.assertIn("job name", err)

    def test_limits(self):
        rc, err = self.sh(S2R_TIMELIMIT="1:00:01")
        self.assertIn("exceeds", err)
        rc, err = self.sh(S2R_TIMELIMIT="abc")
        self.assertIn("could not read", err)
        for tl in ("30:00", "1:00:00", "0-1:00:00", "60"):
            rc, err = self.sh(S2R_TIMELIMIT=tl)
            self.assertEqual(rc, 2)
            self.assertIn("fence.txt", err, tl)  # past the limit check, refused at the fence

    def test_existing_outputs_refuse(self):
        for name in ("log", "stage", "runs"):
            (self.out / name).mkdir()
            rc, err = self.sh()
            self.assertEqual(rc, 2)
            self.assertIn("exists", err)
            (self.out / name).rmdir()

    def test_the_fence(self):
        (self.out / "fence.txt").write_text("cov2d\nrpd_\n")
        self.sacct("123|rpd_reco_x|RUNNING")
        rc, err = self.sh()
        self.assertEqual(rc, 2)
        self.assertIn("fenced jobs (rpd_*)", err)
        self.sacct("123|rpd_reco_x|PENDING")
        self.assertIn("fenced jobs (rpd_*)", self.sh()[1])
        self.sacct("123|rpd_reco_x|CANCELLED by 5")
        rc, err = self.sh()
        self.assertNotIn("fenced jobs", err)
        self.assertEqual(rc, 0)
        self.assertIn("smoke: past the fence", err)
        self.assertFalse((self.out / "log").exists())
        self.sacct("", rc=1)
        self.assertIn("sacct failed", self.sh()[1])

    def test_a_fence_prefix_matches_only_at_the_start_and_then_the_env_is_checked(self):
        (self.out / "fence.txt").write_text("cov2d\n")
        self.sacct("9|my_cov2d_x|RUNNING\n10|ibub_run|RUNNING")
        rc, err = self.sh()
        self.assertNotIn("fenced jobs", err)
        self.assertEqual(rc, 0)  # past the fence, the smoke stops: nothing staged, run or written
        self.assertIn("smoke: past the fence", err)
        self.assertEqual(sorted(x.name for x in self.out.iterdir()), ["fence.txt"])


class Cli(unittest.TestCase):
    """Every subcommand of s2r_probe.main and s2r_read.main on a temporary tree."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, fn, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = fn(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_tasks_manifest_price_and_usage(self):
        rc, out, _ = self.call(SP.main, ["tasks", "--out", str(self.d / "q"), "--stage-dir", "/S/stage",
                                         "--runs", "/S/runs", "--stage-json", "/S/stage.json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["tasks"], 6)
        q = (self.d / "q" / "run.tsv").read_text().splitlines()
        self.assertEqual(len([x for x in q if not x.startswith("#")]), 6)
        self.assertTrue(q[1].startswith("s2r_S2R_"))  # longest first
        rc, _, _ = self.call(SP.main, ["manifest", "--out", str(self.d / "m.json")])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads((self.d / "m.json").read_text()), SP.sources())
        rc, out, _ = self.call(SP.main, ["price"])
        self.assertEqual((rc, json.loads(out)["least_limit_h"]), (0, 1.0))
        self.assertEqual(self.call(SP.main, ["nope"])[0], 2)
        self.assertEqual(self.call(SP.main, ["run", "--arm", "S2R"])[0], 2)  # no "--"

    def test_gate_starts_records_and_stops(self):
        q = self.d / "run.tsv"
        q.write_text("# q\n" + "".join(f"{SP.task_id(a, t)}\t{a}\t{SP.TASK_S[a]}\ts2r/s2r_probe.py\n"
                                       for a, t, _ in SP.ordered(SP.all_tasks())))
        log = self.d / "log"
        log.mkdir()
        tid = SP.task_id("S2R", "q3")
        rc, _, _ = self.call(SP.main, ["gate", "--task", tid, "--queue", str(q), "--log", str(log), "--t0", "1000",
                                       "--limit-h", "1.0"])
        self.assertEqual(rc, 3)  # t0 long ago: the projection exceeds 0.9 x 1.0 h, so nothing starts
        self.assertTrue((log / "STOP").exists())
        (log / "STOP").unlink()
        import time
        self.assertEqual(SP.gate(tid, q, log, time.time(), 1.0), 0)
        self.assertTrue((log / f"{tid}.start").exists())
        (log / f"{tid}.end").write_text("1\n")
        self.assertEqual(SP.gate(tid, q, log, time.time(), 1.0), 4)
        self.assertEqual(SP.gate("s2r_XX_q3_s991000", q, log, time.time(), 1.0), 3)

    def test_run_refuses_a_bad_argv_and_a_bad_stage_record(self):
        rc, _, err = self.call(lambda a: SP.run("S2R", "q3", self.d / "none.json", a), ["--iters=20"])
        self.assertEqual(rc, 2)
        self.assertIn("separate argument", err)
        rc, _, err = self.call(lambda a: SP.run("S2R", "q3", self.d / "none.json", a), ["--iters", "20"])
        self.assertEqual(rc, 2)
        self.assertIn("the stage record", err)

    def test_stage_and_pair_refuse_cleanly(self):
        (self.d / "stage.json").write_text(json.dumps({"dest": str(self.d), "files": [
            {"role": "prr_B0_q3_s991000", "copy": str(self.d / "missing.npz"), "sha256": "0" * 64}]}))
        rc, _, err = self.call(SP.main, ["verify-stage", "--stage", str(self.d / "stage.json")])
        self.assertEqual(rc, 2)
        rc, _, err = self.call(SP.main, ["pair", "--stage", str(self.d / "stage.json"), "--runs", str(self.d),
                                         "--out", str(self.d / "pair.json")])
        self.assertEqual(rc, 2)
        self.assertFalse((self.d / "pair.json").exists())


class ReadMain(Read):
    def test_main_writes_the_readout_and_prints_only_the_verdict(self):
        self.build(self.passing)
        (self.run / "stage.json").write_text(json.dumps(self.stage))
        (self.run / "pair.json").write_text(json.dumps({"pass": True}))
        args = ["--runs", str(self.run / "runs"), "--stage", str(self.run / "stage.json"),
                "--pair", str(self.run / "pair.json"), "--out", str(self.run / "read")]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(SR.main(args), 0)
        self.assertEqual(out.getvalue().strip(), json.dumps({"verdict": "COMPLETE"}))
        ro = json.loads((self.run / "read" / "readout.json").read_text())
        self.assertEqual(ro["verdict"], "PASS")
        self.assertIn("S2R readout: PASS", (self.run / "read" / "readout.txt").read_text())
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(SR.main(args), 2)  # the readout exists: refused
        (self.run / "pair.json").write_text(json.dumps({"pass": False}))
        args[-1] = str(self.run / "read2")
        with contextlib.redirect_stderr(err):
            self.assertEqual(SR.main(args), 5)
        self.assertFalse((self.run / "read2").exists())


if __name__ == "__main__":
    unittest.main()
