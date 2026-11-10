"""Tests of T3 (T3-PIPELINE-TESTS-DECLARATION.md rev 2): the tasks, the price, the queues through the real runner's
parser, the arms against the production loop, the install, staging, C-PAIR (REQUIRED: a one-ulp change fails it),
the gate, every reading in the direction it acts and the other, an end-to-end read, and the job script's refusals.

Run: python3 -B -m unittest nd-unfolding/tier3/test_t3p.py (no LightGBM, no ROOT, no cluster: the estimators are
deterministic stand-ins, the inputs synthetic rows on the real 5D fine grid, FD-STAB's test helpers).
"""
import argparse
import contextlib
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

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
for _p in (HERE, ND, ND / "tests", ND / "pv-ladder", ND / "prior_retention"):
    if str(_p) not in sys.path:
        sys.path.insert(1, str(_p))
import t3p_arms as A  # noqa: E402
import t3p_probe as T  # noqa: E402
import t3p_read as RT  # noqa: E402
import prr_probe as P  # noqa: E402
import prr_read as RD  # noqa: E402
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
import s5c_pseudo  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5e_trace  # noqa: E402
import test_estimator_stability_probe as TS  # noqa: E402  (FD-STAB's synthetic fine-grid inputs)

if not hasattr(os, "O_NOATIME"):  # macOS: REF-G1's copy reads os.O_NOATIME at each open; a 0 flag is a plain read
    os.O_NOATIME = 0


def quiet():
    return contextlib.redirect_stderr(io.StringIO())


class Linear:
    """A deterministic smooth stand-in with LightGBM's surface; it records every fit's sample weight."""

    def __init__(self, **params):
        self.params = dict(params)
        self.weights = []

    def get_params(self, deep=True):
        return dict(self.params)

    def set_params(self, **params):
        self.params.update(params)
        return self

    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X, float)
        self.weights.append(None if sample_weight is None else np.array(sample_weight, copy=True))
        w = np.ones(len(X)) if sample_weight is None else np.sqrt(np.asarray(sample_weight, float))
        Z = np.c_[X, np.ones(len(X))]
        self.coef = np.linalg.lstsq(Z * w[:, None], np.asarray(y, float) * w, rcond=None)[0]
        return self

    def _z(self, X):
        return np.c_[np.asarray(X, float), np.ones(len(X))] @ self.coef

    def predict_proba(self, X):
        p = 1 / (1 + np.exp(-np.clip(self._z(X), -5, 5)))
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return 1.0 + 0.1 * np.tanh(self._z(X))


class StandIns:
    """onc.make_estimators replaced by stand-ins for the test; the built estimators are kept."""

    def setUp(self):
        self.saved_make = onc.make_estimators
        self.built = []

        def make(kind, nvars, seed=None):
            e = (Linear(), Linear(), Linear())
            self.built.append(e)
            return e
        onc.make_estimators = make
        inp = TS.fine_inputs(2500, 2)
        self.unf = {k: inp[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco",
                                         "denom_nd", "flux", "data_pot", "n_nucleons", "edges")}
        self.unf["measured"], self.unf["measured_weights"] = inp["measured"], inp["measured_weights"]
        n = len(inp["MCgen"])
        self.r = np.random.default_rng(5).uniform(0.7, 1.3, n)
        self.ncell = int(np.prod([len(e) - 1 for e in inp["edges"]]))
        self.fm = (np.arange(self.ncell) % 17 - 1).astype(int)  # -1 marks fine cells outside every cell
        self.M16 = np.vstack([(self.fm == c).astype(float) for c in range(16)])

    def tearDown(self):
        onc.make_estimators = self.saved_make

    def traced(self, arm, iters):
        rec = A.ArmRecorder(self.unf, self.r, self.M16, self.fm, iters)
        xs, params, tr = A.traced_unfold_arm(self.unf, rec, 42, 1, iters, arm, self.r)
        return xs, rec, tr


# ============================================================================================ constants and price
class Constants(unittest.TestCase):
    def test_t_quantile(self):
        from scipy.stats import t
        self.assertAlmostEqual(RT.T_Q, t.ppf(1 - 0.01 / 20, 4), places=12)

    def test_delta_t_from_fd_prr(self):
        prr = RT.check_inputs(REPO)
        self.assertAlmostEqual(RT.delta_t(prr), max(0.02, 9.02936702750999 * 0.0023377215802034717), places=12)

    def test_arms_and_iterations(self):
        self.assertEqual(A.ARMS, ("B0", "MU", "MW", "MO", "SO", "OP"))
        self.assertEqual({a: A.ITERS[a] for a in A.ARMS}, {"B0": 50, "MU": 50, "MW": 50, "MO": 50, "SO": 50, "OP": 2})

    def test_tasks_and_jobs(self):
        tasks = T.all_tasks()
        self.assertEqual(len(tasks), 36)
        self.assertEqual(len(set(tasks)), 36)
        counts = {j: sum(1 for t in tasks if T.job_of(*t) == j) for j in T.JOBS}
        self.assertEqual(counts, {"dry": 6, "q3": 6, "floor": 24})
        self.assertTrue(all(t[1] == "A7_gibuu" for t in tasks if t[2] != T.PRIMARY_SEED))
        self.assertEqual((T.job_of("B0", "A7_gibuu", T.PRIMARY_SEED), T.job_of("B0", "q3", T.PRIMARY_SEED),
                          T.job_of("B0", "A7_gibuu", 994003)), ("dry", "q3", "floor"))

    def test_price_limits_and_cap(self):
        pr = T.price()
        for j, v in pr.items():
            self.assertGreaterEqual(v["limit_h"], v["least_limit_h"], j)
        self.assertEqual(sum(T.JOB_LIMIT_H.values()), T.CAP_NODE_H)
        self.assertEqual(sum(v["lane_s"] for v in pr.values()), 183600.0)
        self.assertEqual(pr["floor"]["wall_h"], 5.0)

    def test_limit_strings(self):
        out = {}
        for j in T.JOBS:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(T.main(["limit", j]), 0)
            out[j] = buf.getvalue().strip()
        self.assertEqual(out, {"dry": "2:15:00", "q3": "2:00:00", "floor": "5:45:00"})

    def test_pins_hold_and_include_the_imported_probe(self):
        P.check_pins(T.CODE_PINS)
        self.assertIn("nd-unfolding/prior_retention/prr_probe.py", T.CODE_PINS)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(P.Refused):
            P.check_pins(T.CODE_PINS, Path(d))


# ============================================================================================ the queues
def parse_runner(rest):
    """The real runner's parse of a queue line's arguments (s5p_nullexp.main stops right after it)."""
    import s5p_nullexp
    cap = {}
    orig = argparse.ArgumentParser.parse_args

    def pa(self, args=None, namespace=None):
        cap["ns"] = orig(self, args, namespace)
        raise KeyboardInterrupt
    argparse.ArgumentParser.parse_args = pa
    try:
        s5p_nullexp.main(rest)
    except KeyboardInterrupt:
        pass
    finally:
        argparse.ArgumentParser.parse_args = orig
    return cap["ns"]


class Queues(unittest.TestCase):
    def setUp(self):
        self.a = T.staged_paths(Path("/S/stage"), Path("/S/runs"), stage_json=Path("/S/stage.json"))

    def lines(self):
        for j in T.JOBS:
            for ln in T.queue_lines(self.a, j)[1:]:
                yield j, ln.split("\t")

    def test_every_line_passes_the_runners_parse_and_the_check(self):
        n = 0
        for j, cols in self.lines():
            argv = cols[4:]
            arm, truth = argv[argv.index("--arm") + 1], argv[argv.index("--truth") + 1]
            ns = parse_runner(argv[argv.index("--") + 1:])
            self.assertIsNone(T.check_namespace(ns, arm, truth), cols[0])
            self.assertEqual(T.job_of(arm, truth, int(ns.pseudo_seeds.split(":")[0])), j)
            n += 1
        self.assertEqual(n, 36)

    def test_lines_are_fd_prrs_k50_line_but_for_three_fields(self):
        for arm, t, s in T.all_tasks():
            ours = T.runner_argv(self.a, arm, t, s)
            base = P.runner_argv(self.a, "K50", t, s)
            diff = {base[i - 1] for i in range(1, len(base)) if base[i] != ours[i]}
            self.assertEqual(len(ours), len(base))
            self.assertLessEqual(diff, {"--iters", "--tag", "--out"})
            self.assertEqual(ours[ours.index("--iters") + 1], str(A.ITERS[arm]))

    def test_queue_columns(self):
        for j, cols in self.lines():
            self.assertEqual(cols[0], T.task_id(cols[1], cols[cols.index("--truth") + 1],
                                                int(cols[cols.index("--pseudo-seeds") + 1].split(":")[0])))
            self.assertEqual(float(cols[2]), T.TASK_S[A.ITERS[cols[1]]])
            self.assertEqual(cols[3], "tier3/t3p_probe.py")

    def test_the_refusals_fire_on_the_runners_parse(self):
        argv = T.runner_argv(self.a, "B0", "q3", T.PRIMARY_SEED)
        good = parse_runner(argv)
        self.assertIsNone(T.check_namespace(good, "B0", "q3"))
        cases = {"iters": 5, "capacity": "400,31", "mc_fraction": "quarter", "pseudo_seeds": "991000:991001",
                 "estimator_seed": 43, "threads": 8, "tag": "prr_K50_q3", "config": None,
                 "hypothesis": "docs/orchestration/state/s5p/ratios/nullsF/null-gibuu_cv-F.json",
                 "alternative_amplitude": 0.5, "expectation": False}
        for k, v in cases.items():
            ns = argparse.Namespace(**vars(good))
            setattr(ns, k, v)
            self.assertIsNotNone(T.check_namespace(ns, "B0", "q3"), k)
        ns = argparse.Namespace(**vars(good))
        ns.pseudo_seeds = "994001:994001"
        self.assertIsNotNone(T.check_namespace(ns, "B0", "q3"))  # q3 is not run on the floor splits
        self.assertIsNotNone(T.check_namespace(good, "OP", "q3"))  # OP runs 2 iterations


# ============================================================================================ staging sources
class Sources(unittest.TestCase):
    def test_sources(self):
        src = T.sources()
        roles = [e["role"] for e in src]
        self.assertEqual(len(src), 26)
        self.assertEqual(len(set(roles)), 26)
        self.assertEqual(len({e["name"] for e in src}), 26)
        self.assertEqual(sum(r.startswith("prr_") for r in roles), 21)
        self.assertEqual([r for r in roles if r.startswith("rho_")], ["rho_gibuu_cv-F"])
        hyp = json.loads((REPO / P.closure_spec("A7_gibuu")[1]).read_text())
        rho = next(e for e in src if e["role"] == "rho_gibuu_cv-F")
        self.assertEqual(rho["sha256"], hyp["rho_npz"]["sha256"])
        dig = T.prr_digests()
        for e in src:
            if e["role"].startswith("prr_"):
                rel = e["src"][len(T.PRR_OUT) + 1:]
                self.assertEqual(e["sha256"], dig[rel])

    def test_pair_refs(self):
        refs = T.pair_refs()
        self.assertEqual(len(refs), 21)
        self.assertEqual(sum(1 for r in refs if r[3] is None), 5)

    def test_disagreeing_listings_refuse(self):
        with tempfile.TemporaryDirectory() as d:
            for i, j in enumerate(("dry", "iter", "cap", "misc")):
                p = Path(d) / j / "cluster" / f"log-{j}"
                p.mkdir(parents=True)
                sha = "a" * 64 if i < 3 else "b" * 64
                (p / "SHA256SUMS").write_text(f"{sha}  runs/B0/q3/prr_B0_q3_s991000.npz\n")
            with self.assertRaises(P.Refused):
                T.prr_digests(Path(d))


# ============================================================================================ the arms
class Arms(StandIns, unittest.TestCase):
    def test_b0_trace_at_k_equals_the_plain_unfold_at_k(self):
        """REQUIRED (C-PAIR's premise): the loop's state after iteration k does not depend on the total count."""
        _, rec, _ = self.traced("B0", 5)
        for k in (5,):
            plain, _ = s5c_unfold.unfold(self.unf, "deterministic", 42, 1, k)
            self.assertTrue(np.array_equal(rec.xs_at[k], plain.ravel(order="C")))
        xs3, _, _ = self.traced("B0", 3)
        plain3, _ = s5c_unfold.unfold(self.unf, "deterministic", 42, 1, 3)
        self.assertTrue(np.array_equal(xs3, plain3))

    def test_the_trace_records_r00_r15_from_the_production_extraction(self):
        xs, rec, tr = self.traced("B0", 5)
        a = rec.arrays(tr)
        self.assertTrue(np.allclose(a["X16_push"][4], self.M16 @ rec.xs_at[5], rtol=1e-12, atol=0))
        self.assertTrue(np.allclose(a["X16_push"][-1], self.M16 @ xs.ravel(order="C"), rtol=1e-12, atol=0))
        self.assertEqual(a["X16_push"].shape, (5, 16))
        self.assertAlmostEqual(a["reco_in_cells"][0], float(a["R16_prior"].sum()), delta=1e-9 * a["reco_in_cells"][0])

    def test_mu_fills_misses_with_one(self):
        _, _, tr = self.traced("MU", 3)
        self.assertEqual(tr.evidence["fill_all_one"], [True] * 3)
        xb, _, _ = self.traced("B0", 3)
        xu, _, _ = self.traced("MU", 3)
        self.assertFalse(np.array_equal(xb, xu))

    def test_mw_weights_reach_the_regressor(self):
        _, _, tr = self.traced("MW", 3)
        reg = self.built[-1][2]
        self.assertEqual(len(reg.weights), 3)
        self.assertTrue(all(w is not None for w in reg.weights))
        self.assertEqual(tr.evidence["mw_fits"], 3)
        m = np.asarray(self.unf["pass_truth"], bool)
        pr = np.asarray(self.unf["pass_reco"])[m]
        self.assertTrue(np.array_equal(reg.weights[0], np.asarray(self.unf["w_truth"])[m][pr]))  # w_push = 1 at k = 1
        _, _, _ = self.traced("B0", 3)
        self.assertTrue(all(w is None for w in self.built[-1][2].weights))

    def test_mw_refuses_a_wrong_weight(self):
        orig = A.ArmTracer.mw_weight
        A.ArmTracer.mw_weight = lambda self: orig(self) * 1.001
        try:
            with self.assertRaises(s5e_trace.TraceError):
                self.traced("MW", 2)
        finally:
            A.ArmTracer.mw_weight = orig

    def test_mo_gives_misses_the_true_weight(self):
        _, _, tr = self.traced("MO", 3)
        self.assertEqual(len(tr.evidence["max_rel_oracle"]), 3)
        self.assertTrue(all(d <= A.ORACLE_RTOL for d in tr.evidence["max_rel_oracle"]))

    def test_mo_and_op_refuse_a_wrong_oracle(self):
        orig = A.ArmTracer.oracle_new_w
        A.ArmTracer.oracle_new_w = lambda self, pass_side: orig(self, pass_side) * (1 + 1e-9)
        try:
            for arm in ("MO", "OP"):
                with self.assertRaises(s5e_trace.TraceError):
                    self.traced(arm, 2)
        finally:
            A.ArmTracer.oracle_new_w = orig

    def test_op_gives_every_event_the_true_weight_and_records_the_repeat(self):
        _, _, tr = self.traced("OP", 2)
        self.assertIsInstance(tr.evidence["op_push_rel_change"], float)
        self.assertLess(tr.evidence["op_push_rel_change"], 1e-6)
        self.assertTrue(all(d <= A.ORACLE_RTOL for d in tr.evidence["max_rel_oracle"]))

    def test_unknown_arm_and_bad_r_refuse(self):
        with self.assertRaises(ValueError):
            self.traced("XX", 2)
        rec = A.ArmRecorder(self.unf, self.r, self.M16, self.fm, 2)
        with self.assertRaises(s5e_trace.TraceError):
            A.traced_unfold_arm(self.unf, rec, 42, 1, 2, "MO", self.r[:-1])

    def test_the_clip_is_counted(self):
        saved = Linear.predict_proba
        Linear.predict_proba = lambda self, X: np.column_stack([np.ones(len(X)), np.zeros(len(X))])
        try:
            _, rec, tr = self.traced("B0", 2)
        finally:
            Linear.predict_proba = saved
        a = rec.arrays(tr)
        self.assertGreater(a["clip_step1"][0, 0], 0)
        self.assertEqual(a["clip_step1"][0, 1], 0)


# ============================================================================================ the install
def toy_bkg(inp, n=400, seed=7):
    rng = np.random.default_rng(seed)
    return {"bkg_reco": inp["MCreco"][100:100 + n].copy(), "bkg_w": rng.uniform(0.1, 0.5, n),
            "bkg_nd": np.zeros(1)}


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

    def build(self, arm):
        split = s5c_pseudo.split_key_for(T.PRIMARY_SEED)
        with T.install(arm, "q3", rho=None, guard=False) as st:
            exp, xt, info = s5n_pseudo.build_pseudo(self.inp, self.bkg, "hypothesis", 1.0, split, T.PRIMARY_SEED, None)
        return st, exp, split

    def test_so_builds_signal_only_and_r_is_captured(self):
        st, exp, split = self.build("SO")
        self.assertEqual(st["so"]["template_rows"], 0)
        self.assertEqual(st["so"]["pseudo_background_events"], 0.0)
        is_b = s5c_pseudo.half_mask(len(self.inp["MCgen"]), split)
        self.assertTrue(np.array_equal(st["r_A"], self.r[~is_b]))
        st0, exp0, _ = self.build("B0")
        self.assertGreater(st0["so"]["template_rows"], 0)

    def test_a_development_option_from_the_runner_is_refused(self):
        with T.install("B0", "q3", rho=None, guard=False):
            with self.assertRaises(P.Refused):
                s5n_pseudo.build_pseudo(self.inp, self.bkg, "hypothesis", 1.0, 5, 6, None, no_background=True)

    def test_no_product_without_the_check_or_the_steps(self):
        with T.install("B0", "q3", rho=None, guard=True):
            with self.assertRaisesRegex(RuntimeError, "never checked"):
                s5n_pseudo.write_product(Path("x.npz"), {}, {})
        with T.install("B0", "q3", rho=None, guard=False):
            with self.assertRaisesRegex(RuntimeError, "0 builds, 0 unfolds"):
                s5n_pseudo.write_product(Path("x.npz"), {}, {})
        self.assertEqual(self.written, [])

    def test_unfold_one_refuses_a_missing_r_a_mismatched_r_or_a_substitute(self):
        import s5p_numerics
        split = s5c_pseudo.split_key_for(T.PRIMARY_SEED)
        with T.install("B0", "q3", rho=None, guard=False):
            with self.assertRaises(P.Refused):  # r not captured yet
                s5p_numerics.unfold_one({"MCgen": np.zeros((3, 5))}, np.float32, 42, 1, 2)
            exp, _, _ = s5n_pseudo.build_pseudo(self.inp, self.bkg, "hypothesis", 1.0, split, T.PRIMARY_SEED, None)
            with self.assertRaises(P.Refused):  # r captured, on another number of rows
                s5p_numerics.unfold_one({"MCgen": np.zeros((3, 5))}, np.float32, 42, 1, 2)
            with self.assertRaises(P.Refused):  # r captured and matching, but a substitute unfold
                s5p_numerics.unfold_one(exp, np.float32, 42, 1, 2, unfold_fn=lambda *a: None)

    def test_the_rho_loader_reads_only_a_staged_copy(self):
        import s5p_truths
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "rho.npz"
            np.savez(p, rho=np.arange(4.0))
            sha = T.sha256_path(p)
            ratio = {"rho_npz": {"path": "/pscratch/elsewhere/rho.npz", "sha256": sha}}
            with T.install("B0", "A7_gibuu", rho=None, guard=False):
                with self.assertRaises(P.Refused):
                    s5p_truths.load_fine_rho(ratio)
            with T.install("B0", "A7_gibuu", rho={sha: p}, guard=False):
                self.assertTrue(np.array_equal(s5p_truths.load_fine_rho(ratio), np.arange(4.0)))

    def test_names_are_restored_after_an_error(self):
        import s5p_numerics
        import s5p_truths
        before = (argparse.ArgumentParser.parse_args, s5n_pseudo.build_pseudo, s5p_numerics.unfold_one,
                  s5p_truths.load_fine_rho, s5n_pseudo.write_product)
        with self.assertRaises(KeyError):
            with T.install("MO", "q3", rho=None):
                raise KeyError("x")
        after = (argparse.ArgumentParser.parse_args, s5n_pseudo.build_pseudo, s5p_numerics.unfold_one,
                 s5p_truths.load_fine_rho, s5n_pseudo.write_product)
        self.assertEqual(before, after)


# ============================================================================================ C-PAIR and C-X
class Pair(unittest.TestCase):
    """A dry job's products and FD-PRR references in a temporary stage: identical arrays pass; one ulp fails."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.runs, stage = d / "runs", d / "stage"
        rng = np.random.default_rng(0)
        self.xt = {t: rng.uniform(1, 2, 64) * 1e-39 for t in T.TRUTHS + (T.PRIOR,)}
        self.xs = {k: rng.uniform(1, 2, 64) * 1e-39 for k in A.PAIR_KS}
        files = []
        for lv, t, s, k in T.pair_refs():
            if s != T.PRIMARY_SEED:
                continue
            p = stage / T.prr_name(lv, t, s)
            p.parent.mkdir(parents=True, exist_ok=True)
            np.savez(p, xsec_flat=self.xs[k] if k else self.xt[t], xtrue_flat=self.xt[t])
            files.append({"role": f"prr_{lv}_{t}_s{s}", "copy": str(p), "sha256": T.sha256_path(p)})
        self.stage = {"dest": str(stage), "files": files}
        for arm, t, s in T.all_tasks():
            if T.job_of(arm, t, s) != "dry":
                continue
            p = T.product_path(self.runs, arm, t, s)
            p.parent.mkdir(parents=True, exist_ok=True)
            extra = {f"xs_k{k}": self.xs[k] for k in A.PAIR_KS} if arm == "B0" else {}
            np.savez(p, xsec_flat=self.xs[50], xtrue_flat=self.xt[t], **extra)

    def tearDown(self):
        self.tmp.cleanup()

    def b0(self):
        return T.product_path(self.runs, "B0", "A7_gibuu", T.PRIMARY_SEED)

    def rewrite(self, path, **change):
        with np.load(path) as z:
            arrays = {k: np.asarray(z[k]) for k in z.files}
        arrays.update(change)
        np.savez(path, **arrays)

    def test_identical_arrays_pass(self):
        res = T.pair(self.stage, self.runs, "dry")
        self.assertTrue(res["pass"], res)
        self.assertEqual(len(res["C-PAIR"]), 4)
        self.assertEqual(len(res["C-X"]), 6)

    def test_one_ulp_in_our_trace_fails_c_pair(self):
        """REQUIRED: one ulp in one cell of B0's k = 5 unfold fails C-PAIR, and names one cell."""
        x = self.xs[5].copy()
        x[17] = np.nextafter(x[17], np.inf)
        self.rewrite(self.b0(), xs_k5=x)
        res = T.pair(self.stage, self.runs, "dry")
        self.assertFalse(res["pass"])
        self.assertFalse(res["C-PAIR"]["A7_gibuu/s991000/k5"]["pass"])
        self.assertEqual(res["C-PAIR"]["A7_gibuu/s991000/k5"]["cells_differing"], 1)
        self.assertTrue(res["C-PAIR"]["A7_gibuu/s991000/k10"]["pass"])

    def test_one_ulp_in_the_reference_fails_c_pair(self):
        """REQUIRED: one ulp in the staged FD-PRR product (its pin recomputed, so only the comparison can catch it)."""
        e = next(f for f in self.stage["files"] if f["role"] == "prr_K50_A7_gibuu_s991000")
        x = self.xs[50].copy()
        x[3] = np.nextafter(x[3], -np.inf)
        self.rewrite(Path(e["copy"]), xsec_flat=x)
        e["sha256"] = T.sha256_path(Path(e["copy"]))
        res = T.pair(self.stage, self.runs, "dry")
        self.assertFalse(res["C-PAIR"]["A7_gibuu/s991000/k50"]["pass"])
        self.assertFalse(res["pass"])

    def test_a_reference_that_is_not_its_pin_fails(self):
        e = next(f for f in self.stage["files"] if f["role"] == "prr_B0_A7_gibuu_s991000")
        e["sha256"] = "0" * 64
        res = T.pair(self.stage, self.runs, "dry")
        self.assertFalse(res["C-PAIR"]["A7_gibuu/s991000/k5"]["pass"])
        self.assertIn("why", res["C-PAIR"]["A7_gibuu/s991000/k5"])

    def test_a_dtype_change_fails(self):
        x32 = self.xs[10].astype(np.float32)  # values exact in both dtypes: only the dtype differs
        e = next(f for f in self.stage["files"] if f["role"] == "prr_K10_A7_gibuu_s991000")
        self.rewrite(Path(e["copy"]), xsec_flat=x32.astype(np.float64))
        e["sha256"] = T.sha256_path(Path(e["copy"]))
        self.rewrite(self.b0(), xs_k10=x32)
        self.assertTrue(np.array_equal(x32, x32.astype(np.float64)))
        self.assertFalse(T.pair(self.stage, self.runs, "dry")["C-PAIR"]["A7_gibuu/s991000/k10"]["pass"])

    def test_one_ulp_in_an_arms_truth_fails_c_x(self):
        p = T.product_path(self.runs, "SO", "A7_gibuu", T.PRIMARY_SEED)
        x = self.xt["A7_gibuu"].copy()
        x[0] = np.nextafter(x[0], np.inf)
        self.rewrite(p, xtrue_flat=x)
        res = T.pair(self.stage, self.runs, "dry")
        self.assertFalse(res["C-X"]["t3p_SO_A7_gibuu_s991000"]["pass"])
        self.assertFalse(res["pass"])


# ============================================================================================ the gate
class Gate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.q, self.log = d / "q.tsv", d / "log"
        self.log.mkdir()
        a = T.staged_paths(Path("/S/stage"), Path("/S/runs"), stage_json=Path("/S/stage.json"))
        self.q.write_text("\n".join(T.queue_lines(a, "dry")) + "\n")
        self.ids = [ln.split("\t")[0] for ln in self.q.read_text().splitlines()[1:] if ln]

    def tearDown(self):
        self.tmp.cleanup()

    def test_dry_starts_within_the_limit_and_records_the_start(self):
        self.assertEqual(T.gate(self.ids[0], self.q, self.log, 0.0, 2.25, "dry", now=10.0), 0)
        self.assertTrue((self.log / f"{self.ids[0]}.start").exists())

    def test_a_projection_above_the_limit_stops(self):
        self.assertEqual(T.gate(self.ids[0], self.q, self.log, 0.0, 1.0, "dry", now=10.0), 3)
        self.assertIn("exceeds", json.loads((self.log / "STOP").read_text())["reason"])
        self.assertEqual(T.gate(self.ids[1], self.q, self.log, 0.0, 9.0, "dry", now=10.0), 3)  # STOP holds

    def test_a_full_job_refuses_an_unmeasured_arm_and_uses_a_measured_one(self):
        self.assertEqual(T.gate(self.ids[0], self.q, self.log, 0.0, 9.0, "full", now=10.0), 3)
        self.assertIn("no rate", json.loads((self.log / "STOP").read_text())["reason"])
        (self.log / "STOP").unlink()
        for arm in A.ARMS:
            tid = f"t3p_{arm}_A7_gibuu_s994001"
            (self.log / f"{tid}.start").write_text("0\n")
            (self.log / f"{tid}.end").write_text("100\n")
        self.assertEqual(T.measured_rates(P.read_log(self.log))["MO"], 100.0)
        self.assertEqual(T.gate(self.ids[0], self.q, self.log, 0.0, 9.0, "full", now=10.0), 0)

    def test_an_ended_task_is_skipped_and_an_unknown_one_stops(self):
        (self.log / f"{self.ids[0]}.end").write_text("5\n")
        self.assertEqual(T.gate(self.ids[0], self.q, self.log, 0.0, 9.0, "dry", now=10.0), 4)
        self.assertEqual(T.gate("t3p_XX_q3_s1", self.q, self.log, 0.0, 9.0, "dry", now=10.0), 3)


# ============================================================================================ the readings
class Readings(unittest.TestCase):
    dt = 0.0211

    def traj(self, f):
        return [f(k) for k in range(1, 51)]

    def test_trajectory_classes(self):
        C = RT.trajectory_class
        self.assertEqual(C(self.traj(lambda k: 0.3 - 0.02 * k), self.dt), "crosses")
        self.assertEqual(C(self.traj(lambda k: 0.2 * 0.8 ** k), self.dt), "reaches 0")
        self.assertEqual(C(self.traj(lambda k: 0.3 - 0.003 * k), self.dt), "slow approach")
        self.assertEqual(C(self.traj(lambda k: 0.12 + 0.05 * 0.5 ** k), self.dt), "plateau")
        self.assertEqual(C(self.traj(lambda k: 0.1 + 0.002 * k), self.dt), "rises")
        self.assertEqual(C(self.traj(lambda k: None if k == 30 else 0.1), self.dt), "undefined")
        self.assertEqual(C([0.1] * 2, self.dt), "undefined")

    def test_the_tail_bar_is_delta_t(self):
        f = lambda k: 0.2 - 0.0008 * k  # noqa: E731  rho(25) - rho(50) = 0.02
        self.assertEqual(RT.trajectory_class(self.traj(f), 0.0211), "plateau")
        self.assertEqual(RT.trajectory_class(self.traj(f), 0.019), "slow approach")

    def test_location_classes(self):
        L = RT.location_class
        self.assertEqual(L(0.06, 0.0, 0.1), "step 1 does not match the pseudo-data")
        self.assertEqual(L(-0.06, 0.0, 0.1), "step 1 does not match the pseudo-data")  # a reco overshoot counts
        self.assertEqual(L(0.01, 0.07, 0.1), "the pull-back or step 2 loses it")
        self.assertEqual(L(0.01, 0.02, 0.1), "reco matched, truth not")
        self.assertEqual(L(0.01, 0.02, -0.06), "reco matched, truth not")
        self.assertEqual(L(0.01, 0.02, 0.01), "closed")
        self.assertEqual(L(None, 0.02, 0.01), "undefined")

    def test_tr1_and_tr2(self):
        self.assertEqual(RT.tr1_class(-0.06, 0.05), "lowers the limit")
        self.assertEqual(RT.tr1_class(0.06, 0.05), "raises the limit")
        self.assertEqual(RT.tr1_class(0.04, 0.05), "no effect")
        self.assertEqual(RT.tr1_class(-0.05, 0.05), "lowers the limit")
        self.assertEqual(RT.tr1_class(None, 0.05), "undefined")
        self.assertEqual(RT.tr2_class(0.03, 0.05), "step 2 carries the truth")
        self.assertEqual(RT.tr2_class(-0.07, 0.05), "step 2 does not carry the truth")

    def test_labels(self):
        L = RT.labels_for
        self.assertEqual(L({"MO": "no effect", "MW": "no effect", "MU": "no effect", "SO": "no effect"},
                           "step 2 carries the truth", "plateau", "closed"), ["unattributed"])
        got = L({"MO": "lowers the limit", "MW": "no effect", "MU": "lowers the limit", "SO": "lowers the limit"},
                "step 2 does not carry the truth", "slow approach", "reco matched, truth not")
        self.assertEqual(len(got), 6)

    def test_bias_split_is_exact(self):
        rng = np.random.default_rng(3)
        d = rng.uniform(-0.3, 0.3, 16)
        d[:2] = 0.001  # outside S
        b = rng.normal(0, 0.05, 16)
        S = np.abs(d) >= 0.01
        rho = float(-np.sum(b[S] * d[S]) / np.sum(d[S] ** 2))
        out = RT.split_bias(b, d, rho)
        self.assertAlmostEqual(out["rms_par"] ** 2 + out["rms_perp"] ** 2, float(np.mean(b ** 2)), places=14)
        self.assertEqual(RT.split_bias(b, d, None)["rms_perp"], None)


# ============================================================================================ end to end
class EndToEnd(unittest.TestCase):
    """read() on a planted run (M16 = identity on 16 cells): planted trajectories give the declared classes, every
    control refuses, and the readout carries no absolute value."""

    def setUp(self):
        import estimator_stability_analyze as an
        self.an, self.saved = an, an.cell_matrix
        an.cell_matrix = lambda h2: np.eye(16)
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name) / "out"
        self.base = 3e-39 * (1 + np.arange(16) / 16)

    def tearDown(self):
        self.an.cell_matrix = self.saved
        self.tmp.cleanup()

    def X(self, t, s):
        rng = np.random.default_rng({"A7_gibuu": 1, "q3": 2}[t])
        return self.base * (1 + rng.uniform(-0.3, 0.3, 16))

    def P(self, s):
        return self.base * (1 + 0.001 * (s % 7))

    def meta(self, arm, t, s):
        want = RD.expected_truth(t, REPO)
        it = A.ITERS[arm]
        ev = {"arm": arm, "mw_fits": it if arm == "MW" else 0, "op_push_rel_change": 1e-15 if arm == "OP" else None,
              "fill_all_one": [True] * it if arm == "MU" else [], "max_rel_oracle": [1e-16] * it if arm in ("MO", "OP") else []}
        pins = {Path(r).name: d for r, d in T.CODE_PINS.items()}
        return {"iters": it, "capacity": None, "nuisance_draw": None, "development": {"expectation": True, "mc_fraction": "half"},
                "pseudo_seed": s, "split_key": s5c_pseudo.split_key_for(s), "hypothesis": {"sha256": want["hyp"]},
                "alternative": want["alt"], "refinement": {"ran": arm != "SO"},
                "code_sha256": {k: pins[k] for k in ("s5p_nullexp.py", "s5n_pseudo.py", "unfold_2d_omnifold_unbinned.py")},
                "tier3": {"schema": T.SCHEMA, "arm": arm, "truth": t, "iters": it, "evidence": ev,
                          "so": {"no_background": arm == "SO", "template_rows": 0 if arm == "SO" else 9,
                                 "pseudo_background_events": 0.0 if arm == "SO" else 3.0},
                          "code_sha256": {"t3p_probe.py": T.sha256_path(Path(T.__file__).resolve()),
                                          "t3p_arms.py": T.sha256_path(Path(A.__file__).resolve())}}}

    def build(self, plant, tamper=None):
        stage_files = []
        for s in (T.PRIMARY_SEED, *T.FLOOR_SEEDS):
            p = self.run / "stage" / T.prr_name("B0", T.PRIOR, s)
            p.parent.mkdir(parents=True, exist_ok=True)
            np.savez(p, xsec_flat=self.P(s), xtrue_flat=self.P(s))
            stage_files.append({"role": f"prr_B0_{T.PRIOR}_s{s}", "copy": str(p), "sha256": T.sha256_path(p)})
        (self.run / "stage.json").write_text(json.dumps({"dest": str(self.run / "stage"), "files": stage_files}))
        for arm, t, s in T.all_tasks():
            it = A.ITERS[arm]
            X, P_ = self.X(t, s), self.P(s)
            rhos = [plant(arm, t, s, k) for k in range(1, it + 1)]
            Xh = np.array([X - r * (X - P_) for r in rhos])
            Rp = 100.0 * (1 + np.arange(16) / 32)
            Rd = Rp * (1 + 0.05 * np.sin(np.arange(16)))
            Rt = Rd * 1.001
            arrays = {"xsec_flat": Xh[-1], "xtrue_flat": X, "X16_push": Xh, "X16_pull": Xh,
                      "R16_pull": np.array([Rd - 0.01 * (Rd - Rp)] * it), "R16_push": np.array([Rd - 0.02 * (Rd - Rp)] * it),
                      "R16_D": Rd, "R16_true": Rt, "R16_prior": Rp, "miss_share16": np.full((it, 16), 0.3),
                      "norm_pull": np.ones(it), "norm_push": np.ones(it), "mean_fill_fail": np.ones(it),
                      "clip_step1": np.zeros((it, 2)), "clip_step2": np.zeros((it, 2)),
                      "reco_in_cells": np.array([Rp.sum(), Rd.sum()])}
            for k in A.PAIR_KS:
                if k <= it:
                    arrays[f"xs_k{k}"] = Xh[k - 1]
            m = self.meta(arm, t, s)
            if tamper and tamper[0] == (arm, t, s):
                tamper[1](arrays, m)
            p = T.product_path(self.run / "runs", arm, t, s)
            p.parent.mkdir(parents=True, exist_ok=True)
            np.savez(p, **arrays, meta=json.dumps(m))
        q = self.run / "queues"
        q.mkdir()
        a = T.staged_paths(self.run / "stage", self.run / "runs", stage_json=self.run / "stage.json")
        for j in T.JOBS:
            lines = T.queue_lines(a, j)
            (q / f"{j}.tsv").write_text("\n".join(lines) + "\n")
            log = self.run / f"log-{j}"
            log.mkdir()
            n = len(lines) - 1
            (log / "DONE").write_text(json.dumps({"mode": j, "tasks": n, "ended": n, "rc": 0}))
            (log / "pair.json").write_text(json.dumps({"pass": True}))

    @staticmethod
    def plant(arm, t, s, k):
        """B0 plateaus at 0.12; MO falls to 0 (lowers the limit); OP carries the truth; a small spread over splits."""
        jitter = 0.001 * ((s % 5) - 2)
        if arm == "OP":
            return 0.01 + jitter
        if arm == "MO":
            return 0.2 * 0.8 ** k + jitter
        return 0.12 + 0.05 * 0.6 ** k + jitter + (0.002 if arm == "MW" else 0.0)

    def test_planted_classes(self):
        self.build(self.plant)
        out, rc = RT.read(self.run, REPO)
        self.assertEqual((out["verdict"], rc), ("COMPLETE", 0), out.get("why"))
        rd = out["readings"]
        for t in T.TRUTHS:
            self.assertEqual(rd["TR-1"][t], {"MU": "no effect", "MW": "no effect", "MO": "lowers the limit", "SO": "no effect"})
            self.assertEqual(rd["TR-2"][t], "step 2 carries the truth")
            self.assertEqual(rd["trajectory"][t]["B0"], "plateau")
            self.assertEqual(rd["trajectory"][t]["MO"], "reaches 0")
            self.assertEqual(rd["location"][t]["B0"], "reco matched, truth not")
            self.assertEqual(rd["labels"][t], ["consistent with a limit set at the misses",
                                               "consistent with weakly constrained directions"])
        self.assertEqual(rd["floor"]["bars"]["MO"], 0.05)
        self.assertNotIn("e-39", json.dumps(out))

    def test_mo_bounded_by_step_2(self):
        def plant(arm, t, s, k):
            if arm == "OP":
                return 0.11 + 0.001 * (s % 3)
            return 0.12 + 0.001 * (s % 3)
        self.build(plant)
        out, _ = RT.read(self.run, REPO)
        self.assertEqual(out["readings"]["TR-1"]["q3"]["MO"], "no effect (bounded by step 2)")
        self.assertEqual(out["readings"]["TR-2"]["q3"], "step 2 does not carry the truth")

    def test_incomplete_without_a_done(self):
        self.build(self.plant)
        (self.run / "log-floor" / "DONE").unlink()
        out, rc = RT.read(self.run, REPO)
        self.assertEqual((out["verdict"], rc), ("INCOMPLETE", RT.INCOMPLETE_RC))

    def test_incomplete_when_a_pair_record_failed(self):
        self.build(self.plant)
        (self.run / "log-q3" / "pair.json").write_text(json.dumps({"pass": False}))
        self.assertEqual(RT.read(self.run, REPO)[0]["verdict"], "INCOMPLETE")

    def test_a_product_check_stops(self):
        def bad(arrays, m):
            m["tier3"]["evidence"]["max_rel_oracle"][3] = 1e-6
        self.build(self.plant, tamper=(("MO", "q3", T.PRIMARY_SEED), bad))
        with self.assertRaises(RT.Stop):
            RT.read(self.run, REPO)

    def test_so_with_the_refinement_running_stops(self):
        def bad(arrays, m):
            m["refinement"]["ran"] = True
        self.build(self.plant, tamper=(("SO", "A7_gibuu", 994002), bad))
        with self.assertRaises(RT.Stop):
            RT.read(self.run, REPO)

    def test_c_trace_stops(self):
        def bad(arrays, m):
            arrays["xs_k5"] = arrays["xs_k5"] * (1 + 1e-9)
        self.build(self.plant, tamper=(("B0", "A7_gibuu", 994001), bad))
        with self.assertRaises(RT.Stop):
            RT.read(self.run, REPO)

    def test_c_reco_stops(self):
        def bad(arrays, m):
            arrays["reco_in_cells"] = arrays["reco_in_cells"] * np.array([1.0, 1.001])
        self.build(self.plant, tamper=(("MU", "q3", T.PRIMARY_SEED), bad))
        with self.assertRaises(RT.Stop):
            RT.read(self.run, REPO)

    def test_a_prior_not_its_pin_stops(self):
        self.build(self.plant)
        rec = json.loads((self.run / "stage.json").read_text())
        rec["files"][2]["sha256"] = "0" * 64
        (self.run / "stage.json").write_text(json.dumps(rec))
        with self.assertRaises(RT.Stop):
            RT.read(self.run, REPO)


# ============================================================================================ the job script
class JobScript(unittest.TestCase):
    """sbatch_t3p.sh's refusals, run locally (T3P_SMOKE) against a git deploy whose nd-unfolding links to this one."""

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
        self.squeue("")

    def tearDown(self):
        self.tmp.cleanup()

    def squeue(self, lines, rc=0):
        p = self.bin / "squeue"
        p.write_text(f"#!/bin/bash\nprintf '%s' '{lines}'\nexit {rc}\n")
        p.chmod(0o755)

    def sh(self, mode, pin=None, **env):
        e = {**os.environ, "T3P_SMOKE": "1", "PATH": f"{self.bin}:{os.environ['PATH']}", **env}
        e.pop("SLURM_JOB_ID", None)
        p = subprocess.run(["bash", str(HERE / "sbatch_t3p.sh"), mode, str(self.deploy), pin or self.pin, str(self.out)],
                           capture_output=True, text=True, env=e, timeout=120)
        return p.returncode, p.stderr

    def test_a_deploy_not_at_its_pin_refuses(self):
        rc, err = self.sh("dry", pin="0" * 40)
        self.assertEqual(rc, 2)
        self.assertIn("deploy HEAD", err)

    def test_a_wrong_job_name_refuses(self):
        rc, err = self.sh("dry", T3P_NAME="t3p_q3")
        self.assertEqual(rc, 2)
        self.assertIn("job name", err)

    def test_a_limit_above_the_declared_refuses_and_an_unreadable_one_says_so(self):
        rc, err = self.sh("dry", T3P_TIMELIMIT="2:16:00")
        self.assertIn("exceeds", err)
        rc, err = self.sh("dry", T3P_TIMELIMIT="abc")
        self.assertIn("could not read", err)

    def test_every_slurm_form_of_a_limit_within_passes_the_check(self):
        for tl in ("30:00", "2:15:00", "0-2:15:00", "135"):
            rc, err = self.sh("dry", T3P_TIMELIMIT=tl)
            self.assertEqual(rc, 2)
            self.assertIn("manifest.json", err, tl)  # past the limit check, refused at the next one

    def test_the_dry_run_refuses_without_a_fence_and_on_a_fenced_job(self):
        (self.out / "manifest.json").write_text("[]")
        rc, err = self.sh("dry")
        self.assertEqual(rc, 2)
        self.assertIn("naming the fenced job-name prefixes", err)
        (self.out / "fence.txt").write_text("ll5d_\ncov2d_\n")
        self.squeue("ll5d_bulk_03|RUNNING")
        rc, err = self.sh("dry")
        self.assertEqual(rc, 2)
        self.assertIn("fenced jobs (ll5d_*)", err)
        self.squeue("", rc=1)
        rc, err = self.sh("dry")
        self.assertIn("squeue failed", err)

    def test_a_fence_prefix_matches_only_at_the_start(self):
        (self.out / "manifest.json").write_text("[]")
        (self.out / "fence.txt").write_text("ll5d_\n")
        self.squeue("my_ll5d_x|RUNNING")
        rc, err = self.sh("dry")
        self.assertNotIn("fenced jobs", err)
        self.assertIn("queue", err)  # refused later: no queue (nothing was staged or run)

    def test_a_full_job_refuses_without_the_dry_runs_done_and_an_existing_log(self):
        rc, err = self.sh("q3")
        self.assertIn("no DONE receipt from the dry run", err)
        (self.out / "log-floor").mkdir()
        rc, err = self.sh("floor")
        self.assertIn("exists", err)


if __name__ == "__main__":
    unittest.main()
