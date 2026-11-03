"""Tests of the estimator-stability probe (FD-STAB-DECLARATION.md): the candidates' wiring, cross-fitting, the
declared truth table against F0's own pins, and every criterion in the direction it acts and the other.

Run: python3 -B -m unittest nd-unfolding/tests/test_estimator_stability_probe.py (no LightGBM, no ROOT: the estimators
are deterministic stand-ins with LightGBM's fit/predict_proba/get_params/set_params surface).
"""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
sys.path.insert(1, str(ND))
import estimator_stability_analyze as an  # noqa: E402
import estimator_stability_probe as probe  # noqa: E402
import fd_f0_regrade  # noqa: E402
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402


class Memorizer:
    """predict_proba = 1 for a row seen in training, 0 otherwise (keyed by its bytes)."""

    def __init__(self, **params):
        self.params = dict(params)
        self.seen = set()

    def get_params(self, deep=True):
        return dict(self.params)

    def set_params(self, **params):
        self.params.update(params)
        return self

    def fit(self, X, y, sample_weight=None):
        self.seen = {np.asarray(r).tobytes() for r in np.asarray(X)}
        return self

    def predict_proba(self, X):
        p = np.array([1.0 if np.asarray(r).tobytes() in self.seen else 0.0 for r in np.asarray(X)])
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return self.predict_proba(X)[:, 1]


class Linear(Memorizer):
    """A deterministic smooth model, for the bitwise pass-through check."""

    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X, float)
        self.coef = np.linalg.lstsq(np.c_[X, np.ones(len(X))], np.asarray(y, float), rcond=None)[0]
        return self

    def predict_proba(self, X):
        z = np.c_[np.asarray(X, float), np.ones(len(X))] @ self.coef
        p = 1 / (1 + np.exp(-z))
        return np.column_stack([1 - p, p])


def toy(n=400, d=3, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, d)), (rng.random(n) < 0.5).astype(float)


class FoldsAndCrossFit(unittest.TestCase):
    def test_folds_depend_on_position_and_key_only(self):
        a = probe.fold_ids(1000, 2)
        self.assertTrue(np.array_equal(a, probe.fold_ids(1000, 2)))
        self.assertGreater(min(np.bincount(a)), 400)  # roughly balanced
        self.assertFalse(np.array_equal(a, probe.fold_ids(1000, 2, key=probe.FOLD_KEY + 1)))

    def test_folds_unchanged_by_a_rounding_scale_perturbation(self):
        X, y = toy()
        Xj = X * (1 + 1e-7)
        c1 = probe.CrossFit(Memorizer(), "clf1", [], 2, paired=False).fit(X, y)
        c2 = probe.CrossFit(Memorizer(), "clf1", [], 2, paired=False).fit(Xj, y)
        self.assertTrue(np.array_equal(c1.folds, c2.folds))

    def test_every_evaluated_row_is_predicted_by_a_model_that_did_not_train_on_it(self):
        X, y = toy()
        c = probe.CrossFit(Memorizer(), "clf1", [], 2, paired=False).fit(X, y)
        self.assertEqual(float(c.predict_proba(X[:300])[:, 1].max()), 0.0)  # a memorizer never saw its own rows
        plain = probe.Recorded(Memorizer(), "clf1", []).fit(X, y)
        self.assertEqual(float(plain.predict_proba(X[:300])[:, 1].min()), 1.0)  # the control sees them all

    def test_paired_copies_share_a_fold(self):
        X, _ = toy(200)
        X2 = np.vstack([X, X])
        y2 = np.r_[np.zeros(200), np.ones(200)]
        c = probe.CrossFit(Memorizer(), "clf2", [], 2, paired=True).fit(X2, y2)
        self.assertTrue(np.array_equal(c.folds[:200], c.folds[200:]))
        self.assertEqual(float(c.predict_proba(X)[:, 1].max()), 0.0)  # neither copy leaked into its own model

    def test_paired_refuses_two_different_halves(self):
        X, y = toy(200)
        with self.assertRaises(RuntimeError):
            probe.CrossFit(Memorizer(), "clf2", [], 2, paired=True).fit(X, y)

    def test_prediction_off_the_fit_prefix_is_refused(self):
        X, y = toy()
        c = probe.CrossFit(Memorizer(), "clf1", [], 2, paired=False).fit(X, y)
        with self.assertRaises(RuntimeError):
            c.predict_proba(X[1:50])

    def test_recorded_is_bitwise_pass_through(self):
        X, y = toy()
        a = Linear().fit(X, y).predict_proba(X)
        b = probe.Recorded(Linear(), "clf1", []).fit(X, y).predict_proba(X)
        self.assertTrue(np.array_equal(a, b))

    def test_crossfit_set_params_reaches_every_fold_model(self):
        X, y = toy()
        c = probe.CrossFit(Memorizer(), "clf1", [], 2, paired=False).fit(X, y)
        c.set_params(min_child_samples=7)
        self.assertTrue(all(m.get_params()["min_child_samples"] == 7 for m in c.models))


class Install(unittest.TestCase):
    def setUp(self):
        self.saved = (onc.make_estimators, s5n_pseudo.write_product, s5c_unfold.config_params)
        onc.make_estimators = lambda kind, nvars, seed=None: (Memorizer(a=1), Memorizer(a=1), Memorizer(a=1))
        self.written = []
        s5n_pseudo.write_product = lambda out, arrays, meta: self.written.append(meta) or 0

    def tearDown(self):
        onc.make_estimators, s5n_pseudo.write_product, s5c_unfold.config_params = self.saved

    def test_b3_parameters_reach_the_deterministic_configuration_only(self):
        with probe.install("B3b"):
            self.assertEqual(s5c_unfold.config_params("deterministic", 4)["min_child_samples"], 100_000)
            self.assertNotIn("min_child_samples", s5c_unfold.config_params("full_binning", 4))
        with probe.install("control"):
            self.assertNotIn("min_child_samples", s5c_unfold.config_params("deterministic", 4))

    def test_b2_wraps_the_two_classifiers_and_not_the_regressor(self):
        with probe.install("B2"):
            c1, c2, r = onc.make_estimators("lgbm", 5)
        self.assertIsInstance(c1, probe.CrossFit)
        self.assertTrue(c2.paired and not c1.paired)
        self.assertNotIsInstance(r, probe.CrossFit)
        with probe.install("control"):
            self.assertFalse(any(isinstance(e, probe.CrossFit) for e in onc.make_estimators("lgbm", 5)))

    def test_every_product_carries_its_candidate(self):
        with probe.install("B3a"):
            s5n_pseudo.write_product(Path("x.npz"), {}, {"schema": "s"})
        sp = self.written[-1]["stability_probe"]
        self.assertEqual((sp["candidate"], sp["override"]), ("B3a", {"min_child_samples": 10_000}))
        self.assertEqual(sp["code_sha256"], probe.sha256_path(Path(probe.__file__).resolve()))

    def test_names_are_restored_on_exit_even_after_an_error(self):
        before = (onc.make_estimators, s5n_pseudo.write_product, s5c_unfold.config_params)
        with self.assertRaises(KeyError):
            with probe.install("B2"):
                raise KeyError("x")
        self.assertEqual(before, (onc.make_estimators, s5n_pseudo.write_product, s5c_unfold.config_params))


class Refusals(unittest.TestCase):
    def test_refusals_fire(self):
        self.assertTrue(probe._refuse(["--construction", "data"], "stability"))
        self.assertTrue(probe._refuse([], "stability"))
        self.assertTrue(probe._refuse(["--construction", "pseudo", "--capacity", "100,8"], "stability"))
        self.assertTrue(probe._refuse(["--construction", "pseudo", "--config", "B0"], "stability"))
        self.assertTrue(probe._refuse(["--expectation"], "closure"))

    def test_refusals_stay_silent_on_the_declared_invocations(self):
        self.assertIsNone(probe._refuse(["--construction", "pseudo", "--config", "R"], "stability"))
        self.assertIsNone(probe._refuse(["--expectation", "--no-nuisance", "--config", "R"], "closure"))

    def test_schema_names_the_truth_and_an_unknown_schema_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.json"
            p.write_text(json.dumps({"schema": "s5e-shape-ratio/1"}))
            self.assertEqual(probe.closure_truth_kind(p, "SCHEMA"), "ratio_nd")
            self.assertEqual(probe.closure_truth_kind(p, "cond_ratio"), "cond_ratio")
            p.write_text(json.dumps({"schema": "something-else/1"}))
            with self.assertRaises(ValueError):
                probe.closure_truth_kind(p, "SCHEMA")

    def test_q3_truth_never_reads_its_placeholder_ratio(self):
        class Untouchable(dict):
            def __getitem__(self, k):
                raise AssertionError("ratio read")

            def get(self, *a):
                raise AssertionError("ratio read")

        edges = [np.linspace(0, 1, 3)] * 5
        rng = np.random.default_rng(1)
        inputs = {"MCgen": rng.random((50, 5)), "edges": edges, "w_truth": np.ones(50)}
        a = s5n_pseudo.truth_weight("q3_given_eavail_w", inputs, 0.3, Untouchable())
        b = s5n_pseudo.truth_weight("q3_given_eavail_w", inputs, 0.3, None)
        self.assertTrue(np.array_equal(a, b))


class SigmaPin(unittest.TestCase):
    def test_the_committed_receipt_carries_the_pin(self):
        self.assertEqual(probe.sha256_path(REPO / "docs/orchestration/state/s5e/cand/assess_receipt.json"),
                         an.SIGMA_RECEIPT_SHA256)


class Tasks(unittest.TestCase):
    def test_the_declared_task_list(self):
        import types
        a = types.SimpleNamespace(npz=Path("/n.npz"), bkg=Path("/b.npz"), bank=Path("/bank"), detector_dir=Path("/det"),
                                  expect_npz_sha256="a" * 64, expect_bkg_sha256="b" * 64,
                                  closure_ratio_dir=Path("/pvl"), runs=Path("/runs"))
        lines = [l.split("\t") for l in probe.task_lines(a) if not l.startswith("#")]
        self.assertEqual(len(lines), len(probe.CANDIDATES) * (13 + len(probe.CLOSURES)))
        pairs, unfolds = {c: [] for c in probe.CANDIDATES}, {c: 0 for c in probe.CANDIDATES}
        for cols in lines:
            self.assertEqual(cols[2:4], ["estimator_stability_probe.py", "--candidate"])
            c, mode, rest = cols[4], cols[5], cols[7:]
            self.assertIsNone(probe._refuse(rest, mode))
            unfolds[c] += int(cols[1])
            if mode == "stability":
                got = rest[rest.index("--pairs") + 1].split(",")
                self.assertEqual(int(cols[1]), len(got))
                pairs[c] += got
        for c in probe.CANDIDATES:  # every candidate: the base and the 51 jitters exactly once, 70 unfolds in all
            self.assertEqual(pairs[c], ["-:-"] + [f"-:{j}" for j in probe.JITTER_SEEDS])
            self.assertEqual(unfolds[c], 52 + 18)
        self.assertEqual([l[4] for l in lines[:4]], list(probe.CANDIDATES))  # interleaved: B2 starts in the first round
        nuwro = [c for c in lines if c[0].endswith("closure_closure_nuwro")]
        self.assertTrue(all("/pvl/prep/ratios/L-5D-PV/nuwro.json" in c for c in nuwro))

    def test_the_dry_run_tasks_are_queue_tasks(self):
        import types
        a = types.SimpleNamespace(npz=Path("/n.npz"), bkg=Path("/b.npz"), bank=Path("/bank"), detector_dir=Path("/det"),
                                  expect_npz_sha256="a" * 64, expect_bkg_sha256="b" * 64,
                                  closure_ratio_dir=Path("/pvl"), runs=Path("/runs"))
        ids = {l.split("\t")[0] for l in probe.task_lines(a) if not l.startswith("#")}
        self.assertLessEqual(set(probe.DRY_TASKS), ids)
        self.assertEqual(len(probe.DRY_TASKS), 4)


class TruthTable(unittest.TestCase):
    """The 18 closures are F0b's truths: names in F0's order, and every committed file carries F0's own pin."""

    def test_names_are_f0s(self):
        self.assertEqual([c[0] for c in probe.CLOSURES], [t["name"] for t in fd_f0_regrade.TRUTHS])

    def test_every_file_carries_f0s_pin(self):
        want = {"W1": fd_f0_regrade.RATIO["W1"], "W2": fd_f0_regrade.RATIO["W2"], "W3": fd_f0_regrade.RATIO["W3"],
                "stage0c_gibuu": fd_f0_regrade.RATIO["gibuu"],
                "P1r": fd_f0_regrade.ALT["P1"][1], "P2r": fd_f0_regrade.ALT["P2"][1], "P3r": fd_f0_regrade.ALT["P3"][1],
                "P1g": fd_f0_regrade.ALT["P1"][1], "P2g": fd_f0_regrade.ALT["P2"][1], "P3g": fd_f0_regrade.ALT["P3"][1]}
        for name, hyp, alt, kind, amp in probe.CLOSURES:
            hyp_key = "mnvtune_v1" if "mnvtune" in hyp else hyp.split("null-")[1].split("-F")[0]
            self.assertEqual(probe.sha256_path(REPO / hyp), fd_f0_regrade.HYP[hyp_key], name)
            if name in want:
                self.assertEqual(probe.sha256_path(REPO / alt), want[name], name)
        alt_kinds = {n: k for n, _, _, k, _ in probe.CLOSURES}
        for p, (kind, _) in fd_f0_regrade.ALT.items():
            self.assertEqual(alt_kinds[f"{p}r"], kind)
            self.assertEqual(alt_kinds[f"{p}g"], kind)

    def test_amplitudes_and_kinds_are_f0s(self):
        ident = {t["name"]: t.get("ident") for t in fd_f0_regrade.TRUTHS}
        for name, hyp, alt, kind, amp in probe.CLOSURES:
            i = ident.get(name)
            if i and i["truth"] != "nominal":
                self.assertEqual((kind, amp), (i["truth"], i["amplitude"]), name)

    def test_stability_input_is_not_an_f0b_truth(self):
        self.assertEqual(probe.sha256_path(REPO / probe.STABILITY_TRUTH["ratio"]), probe.STABILITY_TRUTH["ratio_sha256"])
        f0b = set(fd_f0_regrade.RATIO.values()) | {v[1] for v in fd_f0_regrade.ALT.values()} | set(fd_f0_regrade.HYP.values())
        self.assertNotIn(probe.STABILITY_TRUTH["ratio_sha256"], f0b)


def planted(pair_max_med, pair_max_max, F=10):
    """51 x F relative deviations whose 25 pairs each give s5e's statistic (median, max) = the planted values, sigma 1."""
    rel = np.zeros((51, F))
    for p in range(25):
        row = np.full(F, pair_max_med)
        row[0] = pair_max_max
        rel[2 * p] = row
        rel[2 * p + 1] = row * 0.5
    return rel, np.ones(F)


class Stability(unittest.TestCase):
    def test_pair_statistic_reproduces_planted_values(self):
        s = an.stability_stats(*planted(0.2, 0.8))
        self.assertAlmostEqual(s["mean_median"], 0.2)
        self.assertAlmostEqual(s["mean_max"], 0.8)
        self.assertTrue(s["passes"])

    def test_the_bound_fires_on_either_statistic(self):
        self.assertFalse(an.stability_stats(*planted(0.31, 0.8))["passes"])
        self.assertFalse(an.stability_stats(*planted(0.2, 1.01))["passes"])

    def test_a_single_extreme_jitter_does_not_set_the_statistic(self):
        rel, sig = planted(0.1, 0.5)
        rel[50, 0] = 50.0  # the 51st jitter is in no pair
        self.assertAlmostEqual(an.stability_stats(rel, sig)["mean_max"], 0.5)

    def test_g0(self):
        self.assertTrue(an.g0_informative({"passes": False}))
        self.assertFalse(an.g0_informative({"passes": True}))


class Bias(unittest.TestCase):
    def test_worse_beyond_the_floor_fires(self):
        b0, s = np.full(16, 0.01), np.full(16, 0.001)
        self.assertFalse(an.no_worse(b0 + 0.02, s, b0, s)["no_worse"])

    def test_within_the_floor_is_silent(self):
        b0, s = np.full(16, 0.01), np.full(16, 0.001)
        self.assertTrue(an.no_worse(b0 + 0.0008, s, b0, s)["no_worse"])

    def test_a_coherent_shift_is_judged_by_the_rms_floor_which_averages_down(self):
        # per-cell noise 0.001 gives Delta_max ~ 0.0051 but Delta_rms ~ 0.0013: a uniform +0.002 passes MAX, fails RMS
        b0, s = np.full(16, 0.01), np.full(16, 0.001)
        r = an.no_worse(b0 + 0.002, s, b0, s)
        self.assertLess(r["max"] - r["max_control"], r["delta_max"])
        self.assertGreater(r["rms"] - r["rms_control"], r["delta_rms"])
        self.assertFalse(r["no_worse"])

    def test_better_is_silent(self):
        b0, s = np.full(16, 0.05), np.full(16, 0.001)
        self.assertTrue(an.no_worse(b0 * 0.1, s, b0, s)["no_worse"])

    def test_the_floor_grows_with_the_measured_noise(self):
        b0 = np.full(16, 0.01)
        quiet = an.no_worse(b0 + 0.004, np.full(16, 0.0005), b0, np.full(16, 0.0005))
        noisy = an.no_worse(b0 + 0.004, np.full(16, 0.005), b0, np.full(16, 0.005))
        self.assertFalse(quiet["no_worse"])
        self.assertTrue(noisy["no_worse"])
        self.assertAlmostEqual(noisy["delta_max"], 3 * 1.2 * math.hypot(0.005, 0.005))

    def test_one_bad_cell_fires_through_max(self):
        b0, s = np.full(16, 0.01), np.full(16, 0.001)
        b = b0.copy()
        b[5] = 0.05
        self.assertFalse(an.no_worse(b, s, b0, s)["no_worse"])


def stab(passes, mean_max, se=0.01):
    return {"passes": passes, "mean_max": mean_max, "se_max": se}


class Verdict(unittest.TestCase):
    def test_uninformative_when_the_control_passes(self):
        v = an.verdict({"control": stab(True, 0.5), "B2": stab(True, 0.1)}, {"B2": True})
        self.assertEqual(v["verdict"], "UNINFORMATIVE")

    def test_none_pass(self):
        v = an.verdict({"control": stab(False, 2), "B2": stab(False, 1.5), "B3a": stab(True, 0.5)}, {"B2": True, "B3a": False})
        self.assertEqual(v["verdict"], "NONE_PASS")

    def test_single_winner(self):
        v = an.verdict({"control": stab(False, 2), "B2": stab(True, 0.3), "B3a": stab(True, 0.9)}, {"B2": True, "B3a": True})
        self.assertEqual((v["verdict"], v["winners"]), ("WINNER", ["B2"]))

    def test_co_winners_within_one_combined_se(self):
        v = an.verdict({"control": stab(False, 2), "B2": stab(True, 0.30, 0.02), "B3a": stab(True, 0.31, 0.02)},
                       {"B2": True, "B3a": True})
        self.assertEqual((v["verdict"], v["winners"]), ("CO_WINNERS", ["B2", "B3a"]))

    def test_the_control_is_never_a_winner(self):
        v = an.verdict({"control": stab(False, 2), "B2": stab(True, 0.3)}, {"B2": True, "control": True})
        self.assertNotIn("control", v["winners"])

    def test_the_verdict_takes_no_bias_magnitude(self):
        import inspect
        self.assertEqual(list(inspect.signature(an.verdict).parameters), ["stab", "bias_ok"])



class EndToEnd(unittest.TestCase):
    """run() on synthetic products over a 40-cell grid: the product checks refuse, and the verdict follows the plant."""

    G, F = 40, 6

    def setUp(self):
        self.saved = (an.functionals, an.cell_matrix)
        rng = np.random.default_rng(7)
        self.U = rng.random((self.F, self.G)) + 0.1
        self.M16 = np.vstack([np.where(np.arange(self.G) % 16 == c, 1.0, 0.0) for c in range(16)])
        an.functionals = lambda contract: (self.U, [f"f{i}" for i in range(self.F)])
        an.cell_matrix = lambda h2: self.M16
        self.saved_pin = an.SIGMA_RECEIPT_SHA256
        self.saved_nf = an.N_FUNCTIONALS
        an.N_FUNCTIONALS = self.F
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "receipt.json").write_text(json.dumps({"functional_names": [f"f{i}" for i in range(self.F)],
                                                            "sigma_rel_pct": [1.0] * self.F}))
        (self.root / "contract.json").write_text("{}")
        an.SIGMA_RECEIPT_SHA256 = probe.sha256_path(self.root / "receipt.json")

    def tearDown(self):
        an.functionals, an.cell_matrix = self.saved
        an.SIGMA_RECEIPT_SHA256 = self.saved_pin
        an.N_FUNCTIONALS = self.saved_nf
        self.tmp.cleanup()

    def write(self, path, x, meta, xt=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        arrays = {"xsec_flat": x}
        if xt is not None:
            arrays["xtrue_flat"] = xt
        np.savez_compressed(path, **arrays, meta=json.dumps(meta))

    def products(self, jitter_rel, closure_bias, tamper=None):
        base = np.full(self.G, 2.0)
        for c, eps in jitter_rel.items():
            sp = {"schema": probe.SCHEMA, "candidate": c, "override": probe.CANDIDATES[c]}
            common = {"construction": "pseudo", "truth": probe.STABILITY_TRUTH["truth"], "bootstrap_seed": None,
                      "eavail_ratio_sha256": probe.STABILITY_TRUTH["ratio_sha256"], "pseudo_seed": probe.STABILITY_PSEUDO_SEED,
                      "stability_probe": sp}
            if c == "B2":
                if tamper == "stab_truth":
                    common["truth"] = "nominal"
                if tamper == "stab_ratio":
                    common["eavail_ratio_sha256"] = "0" * 64
                if tamper == "stab_seed":
                    common["pseudo_seed"] = probe.STABILITY_PSEUDO_SEED + 1
            d = self.root / "runs" / c / "stability"
            self.write(d / "base.npz", base, {**common, "jitter_seed": None})
            for j in probe.JITTER_SEEDS:
                if tamper == "missing_jitter" and c == "B2" and j == 7:
                    continue
                sign = 1.0 if j % 2 else -0.5
                meta = {**common, "jitter_seed": j}
                if tamper == "bootstrap" and c == "B3a" and j == 3:
                    meta["bootstrap_seed"] = 5
                self.write(d / f"j{j}.npz", base * (1 + sign * eps), meta)
            for name, hyp, alt, kind, amp in probe.CLOSURES:
                xt = np.full(self.G, 3.0)
                b = closure_bias.get((c, name), 0.01)
                meta = {"stability_probe": sp, "development": {"expectation": True, "mc_fraction": "half"},
                        "pseudo_seed": probe.CLOSURE_SEED, "split_key": 2630545839174644,
                        "hypothesis": {"sha256": an.expected_pin(hyp, REPO)},
                        "alternative": None if alt is None else
                        {"sha256": an.expected_pin(alt, REPO), "amplitude": amp, "truth": kind if kind != "SCHEMA" else "ratio_nd"}}
                if tamper == "hypothesis" and c == "B3a" and name == "W2":
                    meta["hypothesis"] = {"sha256": "0" * 64}
                if tamper == "candidate" and c == "B3b" and name == "q3":
                    meta["stability_probe"] = {**sp, "candidate": "B3a"}
                if tamper == "expectation" and c == "B2" and name == "W1":
                    meta["development"] = {**meta["development"], "expectation": False}
                if tamper == "amplitude" and c == "B2" and name == "q3":
                    meta["alternative"] = {**meta["alternative"], "amplitude": 0.5}
                if tamper == "mc_fraction" and c == "B3a" and name == "W3":
                    meta["development"] = {**meta["development"], "mc_fraction": "quarter"}
                if tamper == "split_seed" and c == "B3a" and name == "W3":
                    meta["pseudo_seed"] = probe.CLOSURE_SEED + 1
                if tamper == "split_key" and c == "B2" and name == "P1r":
                    meta["split_key"] = 1
                if tamper == "determinism" and c == "B3b" and name == "A7_mnvtune":
                    b = 0.0100001
                self.write(self.root / "runs" / c / "closure" / name / "p.npz", xt * (1 + b), meta, xt)

    def run_analysis(self):
        out = self.root / "out.json"
        args = ["--runs", str(self.root / "runs"), "--s5c-contract", str(self.root / "contract.json"),
                "--sigma-receipt", str(self.root / "receipt.json"), "--h2-definition", "unused", "--out", str(out),
                "--repo", str(REPO)]
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            an.main(args)
        return json.loads(out.read_text())

    def test_the_verdict_follows_the_plant(self):
        # control unstable (G0 informative); B2 stable and no worse; B3a stable but worse at A7_nuwro; B3b unstable
        self.products({"control": 0.03, "B2": 0.002, "B3a": 0.002, "B3b": 0.03}, {("B3a", "A7_nuwro"): 0.2})
        r = self.run_analysis()
        self.assertTrue(r["g0_informative"])
        self.assertEqual((r["verdict"]["verdict"], r["verdict"]["winners"]), ("WINNER", ["B2"]))
        self.assertFalse(r["bias"]["B3a"]["A7_nuwro"]["no_worse"])
        self.assertIn("A7_gibuu", r["gibuu_readout_descriptive"]["B2"])

    def test_a_gibuu_improvement_does_not_move_the_verdict(self):
        plant = {"control": 0.03, "B2": 0.002, "B3a": 0.0021, "B3b": 0.03}
        self.products(plant, {})
        first = self.run_analysis()["verdict"]
        self.products(plant, {("B3a", "A7_gibuu"): -0.009, ("B3a", "stage0c_gibuu"): -0.009})
        self.assertEqual(self.run_analysis()["verdict"], first)

    def test_the_product_checks_refuse(self):
        for tamper in ("missing_jitter", "hypothesis", "candidate", "expectation", "amplitude", "bootstrap",
                       "stab_truth", "stab_ratio", "stab_seed", "mc_fraction", "split_seed", "split_key", "determinism"):
            with self.subTest(tamper=tamper):
                import shutil
                shutil.rmtree(self.root / "runs", ignore_errors=True)
                self.products({"control": 0.03, "B2": 0.002, "B3a": 0.002, "B3b": 0.03}, {}, tamper=tamper)
                with self.assertRaises(SystemExit):
                    self.run_analysis()

    def test_the_product_checks_stay_silent_without_tampering(self):
        self.products({"control": 0.03, "B2": 0.002, "B3a": 0.002, "B3b": 0.03}, {})
        r = self.run_analysis()
        self.assertEqual(len(r["truths_judged"]), 17)
        self.assertNotIn("A7_mnvtune", r["truths_judged"])

    def test_the_sigma_pin_refuses_another_receipt(self):
        self.products({"control": 0.03, "B2": 0.002, "B3a": 0.002, "B3b": 0.03}, {})
        an.SIGMA_RECEIPT_SHA256 = "0" * 64
        with self.assertRaises(SystemExit):
            self.run_analysis()

    def test_every_candidate_must_use_all_the_functionals(self):
        self.products({"control": 0.03, "B2": 0.002, "B3a": 0.002, "B3b": 0.03}, {})
        an.N_FUNCTIONALS = self.F + 1
        with self.assertRaises(SystemExit):
            self.run_analysis()

    def test_the_floor_uses_the_sd_around_the_mean(self):
        # jitters alternate +eps / -eps/2 about a base of 1: the run's recorded per-cell SD is cell_sd's, ddof = 1
        self.products({"control": 0.03, "B2": 0.002, "B3a": 0.002, "B3b": 0.03}, {})
        r = self.run_analysis()
        rel = np.r_[1.0, [1 + (0.002 if j % 2 else -0.001) for j in probe.JITTER_SEEDS]]
        self.assertAlmostEqual(r["cell_sd"]["B2"][0], float(np.std(rel, ddof=1)), places=7)


class CellSd(unittest.TestCase):
    def test_sd_is_around_the_mean_with_ddof_one(self):
        base = np.array([2.0, 4.0])
        jit = [base * 1.01, base * 1.01, base * 1.01]  # every jitter moved alike: around the BASE this would be 0.0087
        sd = an.cell_sd(base, jit)
        want = float(np.std([1.0, 1.01, 1.01, 1.01], ddof=1))
        self.assertTrue(np.allclose(sd, want))
        self.assertLess(want, float(np.sqrt(np.mean(np.square([0.01] * 3)))))

    def test_scale(self):
        base = np.ones(3)
        rng = np.random.default_rng(3)
        jit = [base * (1 + 0.01 * rng.normal(size=3)) for _ in range(51)]
        sd = an.cell_sd(base, jit)
        self.assertTrue(np.all((sd > 0.008) & (sd < 0.012)))  # about the planted 0.01, not half or double it


class AuditGaps(unittest.TestCase):
    """The test gaps of the #720 audit, each in the direction it acts."""

    def test_pairs_are_the_25_disjoint_ones(self):
        rel = np.full((51, 4), 0.1)
        rel[1, 0] = rel[2, 0] = 0.9  # disjoint pairs (0,1) and (2,3) each hold one; overlapping (p,p+1) would hold three
        s = an.stability_stats(rel, np.ones(4))
        self.assertAlmostEqual(s["mean_max"], (2 * 0.9 + 23 * 0.1) / 25)

    def test_passes_reads_the_mean_over_pairs_not_the_worst_pair(self):
        rel = np.full((51, 4), 0.1)
        rel[0, 0] = 1.5  # one pair's maximum above 1.0; the mean over the 25 pairs, 0.156, is below it
        s = an.stability_stats(rel, np.ones(4))
        self.assertGreater(s["worst_pair_max"], 1.0)
        self.assertTrue(s["passes"])

    def test_max_noise_is_the_argmax_cells(self):
        b = np.zeros(16)
        b[3] = 0.05
        s = np.full(16, 0.001)
        s[7] = 0.02  # the noisiest cell is not the argmax cell
        self.assertEqual(an.metric_noise(b, s)[1], 0.001)

    def test_delta_combines_both_estimators_noise(self):
        b = np.full(16, 0.01)
        r = an.no_worse(b, np.full(16, 0.003), b, np.full(16, 0.001))
        self.assertAlmostEqual(r["delta_max"], 3 * 1.2 * math.hypot(0.003, 0.001))

    def test_a_zero_floor_is_invalid_not_worse(self):
        b = np.array([0.0, 0.05, 0.0])
        s = np.array([0.01, 0.0, 0.01])
        r = an.no_worse(b + np.array([0, 1e-9, 0]), s, b, s)
        self.assertEqual((r["valid"], r["no_worse"]), (False, None))
        self.assertTrue(an.no_worse(b, s + 0.001, b, s + 0.001)["valid"])

    def test_an_invalid_floor_makes_the_verdict_invalid(self):
        v = an.verdict({"control": stab(False, 2), "B2": stab(True, 0.3), "B3a": stab(True, 0.4)}, {"B2": True, "B3a": None})
        self.assertEqual((v["verdict"], v["invalid_floor"]), ("INVALID", ["B3a"]))
        # a candidate that fails stability cannot pass, so its floor cannot change the verdict
        v = an.verdict({"control": stab(False, 2), "B2": stab(True, 0.3), "B3a": stab(False, 0.4)}, {"B2": True, "B3a": None})
        self.assertEqual(v["verdict"], "WINNER")


class DeclaredConstants(unittest.TestCase):
    """The constants are the declaration's: each value here, and each is printed in the declaration."""

    DECL = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/FD-STAB-DECLARATION.md"

    def test_constants(self):
        self.assertEqual((probe.STABILITY_PSEUDO_SEED, probe.CLOSURE_SEED, probe.CLOSURE_MC_FRACTION),
                         (990000, 991000, "half"))
        self.assertEqual(probe.JITTER_SEEDS, tuple(range(1, 52)))
        self.assertEqual((an.N_PAIRS, an.BOUND_MEDIAN, an.BOUND_MAX, an.FLOOR_K, an.SD_UPPER, an.N_FUNCTIONALS),
                         (25, 0.3, 1.0, 3.0, 1.20, 153))
        self.assertEqual((probe.CAP_NODE_H, probe.LANES, probe.STAB_CHUNK, probe.B2_STOP_RATIO), (8.0, 8, 4, 2.0))
        self.assertAlmostEqual(probe.UNIT_S, 0.022828 * 3600 * 8)

    def test_the_declaration_prints_them(self):
        text = self.DECL.read_text()
        for lit in ("990000", "991000", "--mc-fraction half", "51", "25 disjoint", "0.3", "1.0", "1.20", "153",
                    "8.0 CPU node-h", "0.022828", "8 lanes"):
            self.assertTrue(lit in text, f"the declaration does not print {lit!r}")

    def test_the_task_list_carries_them(self):
        import types
        a = types.SimpleNamespace(npz=Path("/n.npz"), bkg=Path("/b.npz"), bank=Path("/bank"), detector_dir=Path("/det"),
                                  expect_npz_sha256="a" * 64, expect_bkg_sha256="b" * 64,
                                  closure_ratio_dir=Path("/pvl"), runs=Path("/runs"))
        for line in probe.task_lines(a)[1:]:
            cols = line.split("\t")
            if cols[5] == "closure":
                self.assertEqual(cols[cols.index("--mc-fraction") + 1], "half")
                self.assertEqual(cols[cols.index("--pseudo-seeds") + 1], "991000:991000")
            else:
                self.assertEqual(cols[cols.index("--pseudo-seed") + 1], "990000")


class ArgvForms(unittest.TestCase):
    """R2: every form the runner's argparse would read as data or a capacity is refused, by the pre-scan and by the
    check on the runner's own parse."""

    BAD = [(["--construction", "pseudo", "--construction", "data"], "stability"),
           (["--construction", "pseudo", "--constr", "data"], "stability"),
           (["--construction", "pseudo", "--capacity=400,31"], "stability"),
           (["--construction", "pseudo", "--capac", "400,31"], "stability"),
           (["--expectation", "--no-nuisance", "--capacity=400,31"], "closure")]

    def test_the_prescan_refuses_the_five_forms(self):
        for argv, mode in self.BAD:
            with self.subTest(argv=argv):
                self.assertTrue(probe._refuse(argv, mode))

    def _runner(self, argv):
        """A parser with s5p_numerics' relevant options and argparse's defaults (abbreviations on, last value wins)."""
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("--construction", choices=("data", "pseudo"), required=True)
        ap.add_argument("--capacity", default=None)
        ap.add_argument("--config", choices=("R",), default="R")
        ap.add_argument("--pseudo-seed", type=int, default=None)
        ap.add_argument("--pseudo-seeds", default=None)
        return ap.parse_args(argv)

    def test_the_namespace_check_refuses_what_the_runner_would_read(self):
        state = {"checked": False}
        for argv in (["--construction", "pseudo", "--constr", "data", "--pseudo-seed", "990000"],
                     ["--construction", "pseudo", "--capac", "400,31", "--pseudo-seed", "990000"],
                     ["--construction", "pseudo", "--pseudo-seed", "990001"]):
            with self.subTest(argv=argv), probe.namespace_guard("stability", state):
                with self.assertRaises(SystemExit):
                    self._runner(argv)
        self.assertFalse(state["checked"])
        with probe.namespace_guard("stability", state):
            self._runner(["--construction", "pseudo", "--pseudo-seed", "990000"])
        self.assertTrue(state["checked"])

    def test_the_guard_reaches_the_real_runners(self):
        import contextlib
        import io
        import s5p_numerics
        import s5p_nullexp
        bad = {"stability": (s5p_numerics.main, ["--npz", "x", "--bkg", "y", "--expect-npz-sha256", "a",
                                                 "--expect-bkg-sha256", "b", "--construction", "pseudo", "--constr", "data",
                                                 "--pairs", "-:-", "--tag", "t", "--out", "o"]),
               "closure": (s5p_nullexp.main, ["--expectation", "--no-nuisance", "--capac", "400,31"])}
        for mode, (fn, argv) in bad.items():
            with self.subTest(mode=mode), probe.namespace_guard(mode, {"checked": False}):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    fn(argv)

    def test_no_product_without_the_check(self):
        saved = s5n_pseudo.write_product
        s5n_pseudo.write_product = lambda out, arrays, meta: 0
        try:
            with probe.install("control", "stability"):
                with self.assertRaises(RuntimeError):
                    s5n_pseudo.write_product(Path("x.npz"), {}, {})
        finally:
            s5n_pseudo.write_product = saved


class DataNeverInAProduct(unittest.TestCase):
    """The measured events are loaded but never reach an unfold: the pseudo-experiment and the unfolding's inputs are
    the same whatever the data are."""

    def test_unfold_inputs_are_invariant_under_the_data(self):
        import s5e_trace
        rng = np.random.default_rng(5)
        n, nb = 400, 60
        edges = [np.linspace(0, 1, 3)] * 5
        inputs = {"MCgen": rng.random((n, 5)), "MCreco": rng.random((n, 5)), "pass_reco": rng.random(n) < 0.8,
                  "pass_truth": np.ones(n, bool), "w_truth": np.ones(n), "w_reco": np.ones(n), "edges": edges,
                  "denom_nd": np.full([2] * 5, 50.0), "flux": np.ones(2), "data_pot": 1.0, "n_nucleons": 1.0}
        bkg = {"bkg_reco": rng.random((nb, 5)), "bkg_w": np.full(nb, 0.5), "bkg_nd": np.zeros([2] * 5)}
        outs = []
        for data in (rng.random((300, 5)), rng.random((50, 5)) * 0.1):
            exp, _, _ = s5n_pseudo.build_pseudo({**inputs, "measured": data}, bkg, "nominal", 0.0, 12345, 990000)
            feat, w, _, _ = s5n_pseudo.signed_sample(exp)
            outs.append(s5e_trace.unf_inputs(exp, feat, w))
        self.assertEqual(sorted(outs[0]), sorted(outs[1]))
        for k in outs[0]:
            if k != "edges":
                self.assertTrue(np.array_equal(np.asarray(outs[0][k]), np.asarray(outs[1][k])), k)


class Gate(unittest.TestCase):
    """The budget gate: it admits within the cap, stops past it, stops on B2 above 2x, and stays stopped."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.log = self.root / "log"
        self.log.mkdir()
        import types
        a = types.SimpleNamespace(npz=Path("/n.npz"), bkg=Path("/b.npz"), bank=Path("/bank"), detector_dir=Path("/det"),
                                  expect_npz_sha256="a" * 64, expect_bkg_sha256="b" * 64,
                                  closure_ratio_dir=Path("/pvl"), runs=Path("/runs"))
        self.q = self.root / "queue.tsv"
        self.q.write_text("\n".join(probe.task_lines(a)) + "\n")
        self.queue = probe.read_queue(self.q)

    def tearDown(self):
        self.tmp.cleanup()

    def finish(self, tid, start, seconds):
        (self.log / f"{tid}.start").write_text(f"{start}\n")
        (self.log / f"{tid}.end").write_text(f"{start + seconds}\n")

    def test_the_declared_price_before_any_measurement(self):
        p = probe.project(0.0, 0.0, self.queue, {})
        self.assertAlmostEqual(p["projected_node_h"], (210 + 2 * 70) * probe.UNIT_S / 8 / 3600, places=6)  # 7.99
        self.assertLessEqual(p["projected_node_h"], 8.0)

    def test_admits_within_the_cap_and_records_the_start(self):
        self.assertEqual(probe.gate("stab_control_stability_00", self.q, self.log, 0.0, 8.0, now=0.0), 0)
        self.assertTrue((self.log / "stab_control_stability_00.start").exists())

    def test_stops_when_the_remainder_of_the_cap_is_too_small(self):
        self.assertEqual(probe.gate("stab_control_stability_00", self.q, self.log, 0.0, 7.0, now=0.0), 3)
        self.assertIn("exceeds the cap", json.loads((self.log / "STOP").read_text())["reason"])
        self.assertEqual(probe.gate("stab_B3a_stability_00", self.q, self.log, 0.0, 8.0, now=0.0), 3)  # stays stopped

    def test_the_audits_mixed_overrun_stops(self):
        # B2 at 1.9x and the others at 1.1x: 8.31 node-h in all, which the B2-only rule alone would not stop
        u = probe.UNIT_S
        self.finish("stab_control_closure_nominal", 0, 1.1 * u)
        self.finish("stab_B3a_closure_nominal", 0, 1.1 * u)
        self.finish("stab_B3b_closure_nominal", 0, 1.1 * u)
        self.finish("stab_B2_closure_nominal", 0, 1.9 * u)
        p = probe.project(1.9 * u, 0.0, self.queue, probe.read_log(self.log))
        self.assertGreater(p["projected_node_h"], 8.0)
        self.assertEqual(probe.gate("stab_control_stability_00", self.q, self.log, 0.0, 8.0, now=1.9 * u), 3)

    def test_b2_above_twice_the_control_stops_and_below_does_not(self):
        u = probe.UNIT_S
        self.finish("stab_control_closure_nominal", 0, 0.5 * u)
        self.finish("stab_B2_closure_nominal", 0, 1.1 * u)  # 2.2x the control, though cheap in absolute terms
        self.assertEqual(probe.gate("stab_B3a_stability_00", self.q, self.log, 0.0, 8.0, now=1.1 * u), 3)
        self.assertIn("B2 costs", json.loads((self.log / "STOP").read_text())["reason"])
        (self.log / "STOP").unlink()
        self.finish("stab_B2_closure_nominal", 0, 0.9 * u)  # 1.8x
        self.assertEqual(probe.gate("stab_B3a_stability_00", self.q, self.log, 0.0, 8.0, now=0.9 * u), 0)

    def test_a_finished_task_is_skipped_not_rerun(self):
        self.finish("stab_B2_closure_nominal", 0, 600)
        self.assertEqual(probe.gate("stab_B2_closure_nominal", self.q, self.log, 0.0, 8.0, now=700.0), 4)
        self.assertEqual((self.log / "stab_B2_closure_nominal.start").read_text(), "0\n")  # its timing is kept

    def test_a_task_outside_the_queue_stops(self):
        self.assertEqual(probe.gate("not_a_task", self.q, self.log, 0.0, 8.0, now=0.0), 3)

    def test_running_tasks_count_their_remainder(self):
        u = probe.UNIT_S
        (self.log / "stab_control_stability_00.start").write_text("0\n")
        p_early = probe.project(10.0, 0.0, self.queue, probe.read_log(self.log))
        p_late = probe.project(3 * u, 0.0, self.queue, probe.read_log(self.log))
        self.assertGreater(p_late["charged_node_h"], p_early["charged_node_h"])
        # the running task's remainder shrinks as it runs, so the projected remainder falls
        left = lambda p: p["projected_node_h"] - p["charged_node_h"]  # noqa: E731
        self.assertLess(left(p_late), left(p_early))


class JobScript(unittest.TestCase):
    """sbatch_fd_stab.sh run locally on a stand-in deploy: the real gate, runners that only record their argv. The dry
    run admits its four tasks; a cap too small for the queue stops before any runner starts; the full run inherits the
    dry run's timings and runs the rest; a refused deploy pin stops at once."""

    def setUp(self):
        import shutil
        import subprocess
        if not shutil.which("git") or not shutil.which("bash"):
            self.skipTest("needs git and bash")
        self.tmp = tempfile.TemporaryDirectory()
        r = Path(self.tmp.name)
        self.D, self.OUT = r / "deploy", r / "out"
        (self.D / "nd-unfolding").mkdir(parents=True)
        (self.D / "nd-unfolding" / "estimator_stability_probe.py").write_text(
            "import sys\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "import estimator_stability_probe as p\n"
            "if sys.argv[1] == 'gate':\n"
            "    sys.exit(p.main(sys.argv[1:]))\n"
            "import time\n"
            "n = len(sys.argv[sys.argv.index('--pairs') + 1].split(',')) if '--pairs' in sys.argv else 1\n"
            "time.sleep(0.2 * n)  # a lane time in proportion to the unfolds, as on the cluster\n"
            "print('RAN', ' '.join(sys.argv[1:]))\n")
        (self.D / "setup_salloc_env.sh").write_text(f"export PYTHONPATH={str(r / 'mods')!r}\n")
        for m in ("lightgbm", "scipy"):
            (r / "mods").mkdir(exist_ok=True)
            (r / "mods" / f"{m}.py").write_text("")
        (r / "bin").mkdir()
        (r / "bin" / "fake_time").write_text('#!/bin/bash\nshift 3\nexec "$@"\n')
        (r / "bin" / "fake_time").chmod(0o755)
        (r / "bin" / "sha256sum").write_text('#!/bin/bash\nexec shasum -a 256 "$@"\n')
        (r / "bin" / "sha256sum").chmod(0o755)
        g = ["git", "-C", str(self.D), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "init", "-q", str(self.D)], check=True)
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "x"], check=True)
        self.pin = subprocess.run(["git", "-C", str(self.D), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        import types
        a = types.SimpleNamespace(npz=Path("/n.npz"), bkg=Path("/b.npz"), bank=Path("/bank"), detector_dir=Path("/det"),
                                  expect_npz_sha256="a" * 64, expect_bkg_sha256="b" * 64,
                                  closure_ratio_dir=Path("/pvl"), runs=self.OUT / "runs")
        self.OUT.mkdir()
        lines = probe.task_lines(a)
        (self.OUT / "queue.tsv").write_text("\n".join(lines) + "\n")
        (self.OUT / "dry.tsv").write_text("\n".join(l for l in lines if l.split("\t")[0] in probe.DRY_TASKS) + "\n")
        self.env = {**__import__("os").environ, "STAB_TIME_BIN": str(r / "bin" / "fake_time"),
                    "PATH": f"{r / 'bin'}:{__import__('os').environ['PATH']}"}

    def tearDown(self):
        self.tmp.cleanup()

    def job(self, mode, cap, pin=None):
        import subprocess
        return subprocess.run(["bash", str(ND / "sbatch_fd_stab.sh"), mode, str(self.D), pin or self.pin, str(self.OUT),
                               str(cap)], capture_output=True, text=True, env=self.env, timeout=600)

    def test_dry_then_full(self):
        p = self.job("dry", 8.0)
        self.assertEqual(p.returncode, 0, p.stderr)
        L = self.OUT / "log-dry"
        self.assertEqual(sorted(x.stem for x in L.glob("*.end")), sorted(probe.DRY_TASKS))
        self.assertIn("RAN --candidate B2 closure --", (L / "tasks" / "stab_B2_closure_nominal.log").read_text())
        dry_end = (L / "stab_B2_closure_nominal.end").read_text()
        p = self.job("full", 7.25)
        self.assertEqual(p.returncode, 0, p.stderr)
        # the dry run's tasks are skipped in the full run: their timing is the dry run's, and no runner ran them again
        self.assertEqual((self.OUT / "log-full" / "stab_B2_closure_nominal.end").read_text(), dry_end)
        self.assertFalse((self.OUT / "log-full" / "tasks" / "stab_B2_closure_nominal.log").exists())
        n = len([l for l in (self.OUT / "queue.tsv").read_text().splitlines() if not l.startswith("#")])
        self.assertEqual(len(list((self.OUT / "log-full").glob("*.end"))), n)
        self.assertFalse((self.OUT / "log-full" / "STOP").exists())

    def test_a_cap_too_small_stops_before_any_runner(self):
        p = self.job("dry", 0.001)
        self.assertEqual(p.returncode, 1)
        L = self.OUT / "log-dry"
        self.assertTrue((L / "STOP").exists())
        self.assertEqual(list(L.glob("*.end")), [])
        self.assertEqual(list((L / "tasks").glob("*.log")), [])

    def test_full_refuses_without_a_clean_dry_run(self):
        self.assertEqual(self.job("full", 7.25).returncode, 2)

    def test_a_wrong_pin_refuses(self):
        self.assertEqual(self.job("dry", 8.0, pin="0" * 40).returncode, 2)


if __name__ == "__main__":
    unittest.main()
