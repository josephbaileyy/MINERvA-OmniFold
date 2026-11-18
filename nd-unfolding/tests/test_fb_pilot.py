#!/usr/bin/env python3
"""Tests of PILOT-FB's code (PILOT-FB-DECLARATION.md rev 3 §8), each guard in the direction it acts and in the other.
The LightGBM tests need LightGBM 4.6.0 (the receipt runs them in a venv that has it); without it they are skipped."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
import fb_pilot_analyze as A  # noqa: E402
import fb_pilot_edges as E  # noqa: E402
import fb_pilot_gates as G  # noqa: E402
import fb_pilot_probe as P  # noqa: E402
import s5e_trace  # noqa: E402

try:
    import lightgbm as lgb
    HAVE_LGB = lgb.__version__ == "4.6.0"
except ImportError:
    HAVE_LGB = False
need_lgb = unittest.skipUnless(HAVE_LGB, "LightGBM 4.6.0 is not installed")


def f32(x):
    return np.asarray(x, np.float32).astype(np.float64)


def extreme_jitters(u: np.ndarray) -> list:
    """The jitter's closed envelope ends, computed here as s5e_trace.jitter_coords computes a step (independent of
    the module under test): u -/+ spacing(|float32(u)|) / 2."""
    h = 0.5 * np.spacing(np.abs(np.asarray(u, np.float32))).astype(np.float64)
    return [u - h, u + h]


class Admissibility(unittest.TestCase):
    def values(self):
        p2 = [2.0 ** k for k in range(-6, 7)]
        vals = []
        for v in p2 + [1.5, 3.0, 8.0, 1e-3, 123.456]:
            x = np.float32(v)
            vals += [x, np.nextafter(x, np.float32(0)), np.nextafter(x, np.float32(np.inf))]
        vals += [np.float32(0.0), np.float32(-0.0)]
        vals = np.array(vals, np.float32)
        return f32(np.concatenate([vals, -vals]))

    def test_no_jitter_crosses_an_admissible_edge(self):
        U = np.unique(self.values())
        lower, edges = E.admissible_gaps(U)
        self.assertGreater(edges.size, 10)
        for side in extreme_jitters(U):
            before = np.searchsorted(np.sort(edges), U, side="left")
            after = np.searchsorted(np.sort(edges), side, side="left")
            self.assertTrue(np.array_equal(before, after), "a value at its envelope end crossed an edge")

    def test_signed_spacing_counterexamples_are_refused(self):
        for a32 in (np.float32(-1.5), np.nextafter(np.float32(-8.0), np.float32(-np.inf))):
            b32 = np.nextafter(a32, np.float32(np.inf))  # the adjacent float32 above
            lower, edges = E.admissible_gaps(f32([a32, b32]))
            self.assertEqual(edges.size, 0, f"the adjacent pair at {a32} must not hold an edge")
            # signed spacing, the defect both auditors named, would have accepted it
            sa, sb = np.spacing(a32).astype(np.float64), np.spacing(b32).astype(np.float64)
            self.assertLess(float(a32) + 0.5 * sa, float(b32) - 0.5 * sb)

    def test_a_power_of_two_needs_no_extra_rule(self):
        x = np.float32(8.0)
        below = np.nextafter(x, np.float32(0))
        self.assertEqual(E.admissible_gaps(f32([below, x]))[1].size, 0, "adjacent at a power of two: empty")
        two_below = np.nextafter(below, np.float32(0))
        self.assertEqual(E.admissible_gaps(f32([two_below, x]))[1].size, 1, "a wider gap below 8 holds an edge")

    def test_the_zero_band_and_finiteness_refuse(self):
        F = f32([0.0, 1.0, 2.0])
        for bad in (np.array([1e-35]), np.array([float(np.float32(1e-35))]), np.array([np.nan]), np.array([np.inf])):
            with self.assertRaises(E.Infeasible):
                E.check_policy(F, np.concatenate([F, bad]), "t")
        E.check_policy(F, np.concatenate([F, [4e-36, 3e-35, 0.0]]), "t")

    def test_no_edge_sits_in_the_zero_band(self):
        lower, edges = E.admissible_gaps(f32([-1e-30, 0.0, 1e-30]))
        self.assertTrue(np.all(np.abs(edges) > E.EDGE_MIN_ABS))
        self.assertEqual(E.admissible_gaps(f32([-2.5e-35, 2.5e-35]))[1].size, 0,
                         "a gap whose midpoint is inside +-2e-35 holds no edge")

    def test_intended_index_is_lightgbms_value_to_bin(self):
        b = [[1.0, 2.0, np.inf]]
        self.assertEqual(G.intended_index(np.array([[1.0], [1.5], [2.0], [9.0]]), b)[:, 0].tolist(), [0, 1, 1, 2],
                         "a value equal to an upper bound is in that bin (bin.h:631, value <= bin_upper_bound)")


class Placement(unittest.TestCase):
    def pool(self, seed=0, n=5000):
        rng = np.random.default_rng(seed)
        x = f32(np.round(rng.normal(3, 1, n), 2))
        x[:400] = 0.0
        return x

    def test_one_pool_gives_one_edge_set(self):
        F = self.pool()
        a = E.place(F, F, 63, 0.0)
        b = E.place(F.copy(), F.copy(), 63, 0.0)
        self.assertEqual(a["edges"], b["edges"])
        self.assertNotEqual(a["edges"], E.place(F, F, 63, 0.5)["edges"], "E2's offset moves edges")
        self.assertEqual(len(a["intended"]), 63)
        self.assertEqual(a["edges"], sorted(set(a["edges"])), "edges strictly increase")

    def test_ties_collide_and_walk_up(self):
        F = f32(np.concatenate([np.zeros(9000) + 1.0, np.arange(2.0, 70.0)]))
        out = E.place(F, F, 31, 0.0)
        self.assertEqual(len(out["edges"]), out["n"])
        self.assertEqual(out["edges"], sorted(set(out["edges"])))

    def test_too_few_gaps_is_infeasible(self):
        F = f32(np.arange(10.0))
        with self.assertRaisesRegex(E.Infeasible, r"\d+ admissible gaps for \d+ edges"):
            E.place(F, F, 63, 0.0)

    def test_z_comes_from_the_fit_column(self):
        F = f32(np.arange(1.0, 200.0))
        U = np.concatenate([F, [-5.0]])
        out = E.place(F, U, 63, 0.0)
        self.assertEqual((out["z"], out["zero_bounds"]), (1, [E.K]))
        self.assertEqual(E.place(U, U, 63, 0.0)["z"], 2)

    def test_k_is_lightgbms_float32_constant(self):
        self.assertEqual(E.K, float(np.float32(1e-35)))
        self.assertNotEqual(E.K, 1e-35)

    def test_edges_are_written_at_17_digits_and_round_trip(self):
        F = self.pool(1)
        per = [E.place(F, F, 31, 0.0) for _ in range(5)]
        loaded = json.loads(E.forcedbins_json(per))
        self.assertEqual([x["feature"] for x in loaded], list(range(5)))
        self.assertEqual(loaded[0]["bin_upper_bound"], per[0]["edges"])

    def test_build_edges_writes_twelve_files_and_refuses_an_existing_dir(self):
        F = np.column_stack([self.pool(k) for k in range(5)])
        mats = {r: (F, None if r in ("ref",) else F[:100]) for r in E.ROLES}
        with tempfile.TemporaryDirectory() as d:
            idx = E.build_edges(mats, Path(d) / "edges")
            self.assertEqual(sorted(p.name for p in (Path(d) / "edges").glob("*.json")), sorted(
                [f"{s}_{r}.json" for s in E.SETS for r in E.ROLES] + ["INDEX.json"]))
            self.assertEqual(idx["sets"]["E3"]["max_bin"], 127)
            with self.assertRaises(FileExistsError):
                E.build_edges(mats, Path(d) / "edges")


@need_lgb
class G3(unittest.TestCase):
    """Harmful changes, each with a fixture that activates it, must fail; harmless ones may pass (§8)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        rng = np.random.default_rng(5)
        n = 6000
        X = np.column_stack([f32(np.round(rng.normal(2, 1, n), 2)) for _ in range(5)])
        X[: n // 3, 0] = 0.0
        self.X = X
        self.y = ((X[:, 0] > 0) & (X[:, 1] + rng.normal(0, 0.5, n) > 2)).astype(int)
        self.mb = 31
        self.per = [E.place(X[:, f], X[:, f], self.mb, 0.0) for f in range(5)]
        self.intended = [p["intended"] for p in self.per]

    def tearDown(self):
        self.tmp.cleanup()

    def fit(self, per, forced=True, name="fb.json", X=None, raw=None):
        X = self.X if X is None else X
        path = self.d / name
        path.write_text(raw if raw is not None else E.forcedbins_json(per))
        p = dict(n_estimators=25, num_leaves=8, verbose=-1, max_bin=self.mb, bin_construct_sample_cnt=2 ** 31 - 1,
                 deterministic=True, force_row_wise=True, num_threads=1)
        if forced:
            p["forcedbins_filename"] = str(path)
        m = lgb.LGBMClassifier(**p).fit(X, self.y)
        return m, G.g3a(X, p, self.intended, self.d), G.g3bc(m.booster_.model_to_string(), self.intended)

    def test_a_correct_file_passes_and_a_zero_split_stores_k(self):
        m, a, bc = self.fit(self.per)
        self.assertTrue(a["pass"] and bc["pass"], (a, bc))
        # LightGBM's own zero boundary, isolating exact zeros, is stored and printed as 1e-35f promoted to double:
        # an unforced fit, where K is the only boundary between 0 and the positives, shows it; G3 (b) accepts it
        # because K is in the intended list, and would refuse the decimal 1e-35
        rng = np.random.default_rng(9)
        X = self.X.copy()
        X[:, 0] = f32(np.where(np.arange(len(X)) % 3 == 0, 0.0, np.round(rng.uniform(1, 3, len(X)), 2)))
        p = dict(n_estimators=5, num_leaves=4, verbose=-1, max_bin=self.mb, num_threads=1)
        m = lgb.LGBMClassifier(**p).fit(X, (X[:, 0] > 0).astype(int))
        text = m.booster_.model_to_string()
        th0 = {t for f, t, _ in G.model_splits(text) if f == 0}
        self.assertIn(E.K, th0, "the zero split stores exactly K")
        intended = [sorted(th0 | {np.inf}) if f == 0 else [np.inf] for f in range(5)]
        self.assertEqual(G.g3bc(text, intended)["thresholds_not_intended"],
                         sum(1 for f, t, _ in G.model_splits(text) if f != 0))
        decimal = [sorted((th0 - {E.K}) | {1e-35, np.inf}) if f == 0 else [np.inf] for f in range(5)]
        self.assertGreater(G.g3bc(text, decimal)["thresholds_not_intended"], G.g3bc(text, intended)["thresholds_not_intended"])

    def test_a_middle_edge_removed_changes_the_partition(self):
        per = [dict(p, edges=p["edges"][:10] + p["edges"][11:]) if f == 1 else p for f, p in enumerate(self.per)]
        _, a, bc = self.fit(per)
        self.assertFalse(a["pass"], "the greedy refill changed a populated partition: (a) must see it")

    def test_an_edge_moved_in_a_used_gap_fails_b(self):
        m0, _, _ = self.fit(self.per, name="ok.json")
        used = sorted({t for f, t, _ in G.model_splits(m0.booster_.model_to_string()) if f == 1 and np.isfinite(t)})
        e = used[len(used) // 2]
        i = self.per[1]["edges"].index(e)
        lo = max(v for v in self.X[:, 1] if v < e)
        hi = min(v for v in self.X[:, 1] if v > e)
        moved = (e + hi) / 2 if hi - e > e - lo else (lo + e) / 2
        per = [dict(p, edges=p["edges"][:i] + [moved] + p["edges"][i + 1:]) if f == 1 else p
               for f, p in enumerate(self.per)]
        m, a, bc = self.fit(per)
        self.assertTrue(a["pass"], "a move inside a training gap keeps every training index")
        self.assertFalse(bc["pass"], "the moved threshold is used, so (b) must fail")
        v = (moved + e) / 2
        moved_list = sorted(self.per[1]["zero_bounds"] + per[1]["edges"] + [np.inf])
        self.assertNotEqual(int(np.searchsorted(self.intended[1], v, side="left")),
                            int(np.searchsorted(moved_list, v, side="left")), "a scored row in that gap changes bin")

    def test_a_misparsed_edge_used_as_a_split_fails_b(self):
        m0, _, _ = self.fit(self.per, name="ok.json")
        used = sorted({t for f, t, _ in G.model_splits(m0.booster_.model_to_string()) if f == 1 and np.isfinite(t)})
        e = used[len(used) // 2]
        raw = E.forcedbins_json(self.per).replace(E.edge_text(e), format(e, ".6g"), 1)
        self.assertNotEqual(float(format(e, ".6g")), e)
        _, a, bc = self.fit(self.per, raw=raw, name="lowprec.json")
        self.assertFalse(bc["pass"], "the edge parsed to a different double and is used")

    def test_a_nan_in_a_split_feature_fails_c(self):
        X = self.X.copy()
        X[::50, 1] = np.nan
        _, a, bc = self.fit(self.per, X=X, name="nan.json")
        self.assertGreater(bc["missing_or_categorical"], 0)
        self.assertFalse(bc["pass"])

    def test_an_unopenable_file_fails_a(self):
        p = dict(n_estimators=5, num_leaves=8, verbose=-1, max_bin=self.mb, bin_construct_sample_cnt=2 ** 31 - 1,
                 forcedbins_filename=str(self.d / "absent.json"), num_threads=1)
        self.assertFalse(G.g3a(self.X, p, self.intended, self.d)["pass"])

    def test_an_unforced_fit_fails_g3(self):
        _, a, bc = self.fit(self.per, forced=False, name="none.json")
        self.assertFalse(a["pass"] and bc["pass"])

    def test_harmless_changes_may_pass_and_leave_predictions_unchanged(self):
        m0, a0, bc0 = self.fit(self.per, name="ok.json")
        extra = [dict(p, edges=p["edges"] + [p["edges"][-1] + 1e-3]) if f == 2 else p for f, p in enumerate(self.per)]
        m1, a1, bc1 = self.fit(extra, name="surplus.json")
        self.assertTrue(a1["pass"] and bc1["pass"], "a surplus edge after the budget is dropped")
        self.assertTrue(np.array_equal(m0.predict_proba(self.X), m1.predict_proba(self.X)))
        used4 = {t for f, t, _ in G.model_splits(m0.booster_.model_to_string()) if f == 4}
        e = next(v for v in self.per[4]["edges"] if v not in used4)
        lo = max(v for v in self.X[:, 4] if v < e)
        unused = [dict(p, edges=[(lo + e) / 2 if v == e else v for v in p["edges"]]) if f == 4 else p
                  for f, p in enumerate(self.per)]
        m2, a2, bc2 = self.fit(unused, name="unused.json")
        self.assertTrue(np.array_equal(m0.predict_proba(self.X), m2.predict_proba(self.X)),
                        "a bound moved where no split acts changes no prediction")

    def test_the_remedy_is_jitter_invariant_on_fit_and_scored_rows(self):
        rng = np.random.default_rng(11)
        n = 6000
        X = np.column_stack([f32(np.round(rng.normal(2, 1, n), 1)) for _ in range(5)])  # heavy ties, as RS1's K1
        y = (X[:, 0] + X[:, 1] + rng.normal(0, 0.7, n) > 4).astype(int)
        per = [E.place(X[:, f], X[:, f], self.mb, 0.0) for f in range(5)]
        (self.d / "r.json").write_text(E.forcedbins_json(per))
        Xs = X[:500].copy()
        Xj, Xsj = s5e_trace.jitter_coords(X, 7, None), s5e_trace.jitter_coords(Xs, 8, None)

        def fit(X_, forced):
            p = dict(n_estimators=25, num_leaves=8, verbose=-1, max_bin=self.mb, bin_construct_sample_cnt=2 ** 31 - 1,
                     deterministic=True, force_row_wise=True, num_threads=1)
            if forced:
                p["forcedbins_filename"] = str(self.d / "r.json")
            return lgb.LGBMClassifier(**p).fit(X_, y)

        a, b = fit(X, True), fit(Xj, True)
        self.assertTrue(np.array_equal(a.predict_proba(X), b.predict_proba(Xj)), "forced: fit rows bitwise identical")
        self.assertTrue(np.array_equal(a.predict_proba(Xs), b.predict_proba(Xsj)), "forced: scored rows bitwise identical")
        c, d = fit(X, False), fit(Xj, False)
        self.assertFalse(np.array_equal(c.predict_proba(Xs), d.predict_proba(Xsj)), "unforced: the jitter moves it")


class J(unittest.TestCase):
    def exp(self, rng):
        n = 400
        mcgen = f32(np.round(rng.normal(2, 1, (n, 5)), 2))
        mcreco = f32(np.round(rng.normal(2, 1, (n, 5)), 2))
        return {"MCgen": mcgen, "MCreco": mcreco, "pass_truth": rng.random(n) < 0.9, "pass_reco": rng.random(n) < 0.7,
                "obs": f32(np.round(rng.normal(2, 1, (150, 5)), 2)), "obs_counts": rng.integers(0, 3, 150).astype(float),
                "tmpl": f32(np.round(rng.normal(2, 1, (60, 5)), 2)), "tmpl_w": rng.random(60)}

    def test_role_matrices_follow_the_bound_selection(self):
        e = self.exp(np.random.default_rng(1))
        R = P.role_matrices(e, np.float64)
        feat = P.s5n_pseudo.signed_sample(e)[0]
        pt, pr = e["pass_truth"], e["pass_reco"][e["pass_truth"]]
        self.assertTrue(np.array_equal(R["ref"][0], feat))
        self.assertTrue(np.array_equal(R["clf1"][0], np.concatenate([e["MCreco"][pt][pr], feat])))
        self.assertTrue(np.array_equal(R["reg"][1], e["MCgen"][pt][~pr]))
        self.assertTrue(np.array_equal(R["clf2"][0], np.concatenate([e["MCgen"][pt], e["MCgen"][pt]])))

    def test_the_bound_jitter_is_not_jitter_coords_of_a_role_matrix(self):
        e = self.exp(np.random.default_rng(2))
        je = dict(e, MCgen=s5e_trace.jitter_coords(e["MCgen"], 3, None), MCreco=s5e_trace.jitter_coords(e["MCreco"], 3, None))
        received = P.role_matrices(je, np.float64)["reg"][0]
        wrong = s5e_trace.jitter_coords(P.role_matrices(e, np.float32)["reg"][0], 3, None)
        self.assertIsNotNone(G.j_compare("reg.fit", received, wrong, base=False), "Grok's case: a literal J would fail")
        self.assertIsNone(G.j_compare("reg.fit", received, P.role_matrices(je, np.float64)["reg"][0], base=False))

    def test_a_source_slice_is_not_the_signed_sample(self):
        e = self.exp(np.random.default_rng(3))
        R = P.role_matrices(e, np.float64)
        slice_ = np.concatenate([e["MCreco"][e["pass_truth"]][e["pass_reco"][e["pass_truth"]]], e["obs"]])
        self.assertIsNotNone(G.j_compare("clf1.fit", R["clf1"][0], slice_, base=False))

    def test_unapplied_wrong_seed_and_edge_moves_are_caught(self):
        rng = np.random.default_rng(4)
        base = np.asarray(np.round(rng.normal(2, 1, (300, 5)), 2), np.float32)
        base[:20, 0] = 0.0
        edges = [np.array([0.0, 10.0])] + [np.array([-50.0, 50.0])] * 4
        j = s5e_trace.jitter_coords(base, 5, edges)
        good = G.j3_moved(j, base, edges)
        self.assertGreater(good["moved_off_edge"], 0)
        self.assertEqual(good["moved_on_edge"], 0)
        self.assertEqual(G.j3_moved(base.astype(np.float64), base, edges)["moved_off_edge"], 0, "an unapplied jitter")
        bad = j.copy()
        bad[0, 0] += 1e-9
        self.assertEqual(G.j3_moved(bad, base, edges)["moved_on_edge"], 1, "a moved grid-edge entry")
        self.assertIsNotNone(G.j_compare("x", j, s5e_trace.jitter_coords(base, 6, edges), base=False), "a wrong seed")
        self.assertIsNone(G.j_compare("x", base, base.astype(np.float64), base=True), "a base compares as values")
        self.assertIsNotNone(G.j_compare("x", base, base.astype(np.float64), base=False))

    def test_j2_rebuilds_with_the_runs_own_build_inputs(self):
        calls = []

        def fake_build(inputs, bkg, truth, amplitude, split_key, seed, ratio):
            calls.append((truth, amplitude, split_key, seed, ratio))
            raise P.PrepDone()

        ns = type("NS", (), {"truth": "eavail_shape", "amplitude": 1.0, "pseudo_seed": 990000,
                             "eavail_ratio": str(ND.parent / P.rmp.STABILITY["ratio"])})()
        orig = P.s5n_pseudo.build_pseudo
        P.s5n_pseudo.build_pseudo = fake_build
        try:
            with P.install("prep", None, Path("/nonexistent")) as st:
                st.update(ns=ns, seed=3, inputs={}, bkg={}, sources=({}, {}))
                with self.assertRaises(P.PrepDone):
                    P.s5p_numerics.unfold_one({}, np.float64, 42, 32, 5)
        finally:
            P.s5n_pseudo.build_pseudo = orig
        truth, amplitude, split_key, seed, ratio = calls[0]
        self.assertEqual((truth, amplitude, seed), ("eavail_shape", 1.0, 990000))
        self.assertEqual(split_key, P.s5c_pseudo.split_key_for(990000))
        self.assertIsInstance(ratio, dict)


class Outcome(unittest.TestCase):
    S3 = {"median": 0.1, "max": 0.5, "place": {"median": 0.05, "max": 0.2}, "res": {"median": 0.1, "max": 0.5}}

    def stats(self, s1, s2, s3):
        return {"S1": {"reading": s1}, "S2": {"reading": s2, "mean_median": 0.1, "mean_max": 0.5},
                "S3": dict(self.S3, reading=s3)}

    def test_every_combination_reaches_exactly_one_row(self):
        seen = {}
        for s1 in ("REMOVED", "REDUCED", "NOT REMOVED", "INCONCLUSIVE"):
            for s2 in ("STAB_PASS", "STAB_FAIL"):
                for s3 in ("POLICY-STABLE", "POLICY-SENSITIVE"):
                    matches = [r for r, cond, _ in A.ROWS if cond(s1, s2, s3)]
                    self.assertGreaterEqual(len(matches), 1)
                    seen[(s1, s2, s3)] = A.outcome(self.stats(s1, s2, s3))["row"]
        self.assertEqual(len(seen), 16)
        self.assertEqual(seen[("REDUCED", "STAB_PASS", "POLICY-STABLE")], 6)
        self.assertEqual(seen[("INCONCLUSIVE", "STAB_FAIL", "POLICY-STABLE")], 2)
        self.assertEqual(seen[("NOT REMOVED", "STAB_FAIL", "POLICY-SENSITIVE")], 1)

    def test_the_bars_include_equality_and_rows_5_7_name_what_crossed(self):
        s3 = {"median": 0.2, "max": 2.0, "place": {"median": 0.1, "max": 0.3}, "res": {"median": 0.2, "max": 2.0}}
        text = A.statement(5, s3)
        self.assertIn("maximum 2 beyond 1.0", text)
        self.assertNotIn("median 0.2 beyond", text)
        self.assertIn("at most 10 %", A.statement(4, self.S3))
        self.assertIn("between 10 % and 70 %", A.statement(6, self.S3))

    def test_a_nonfinite_bootstrap_endpoint_is_inconclusive(self):
        self.assertEqual(A.s1_reading({"interval_90": [float("nan"), 0.05], "reading": "P"}), "INCONCLUSIVE")
        self.assertEqual(A.s1_reading({"interval_90": [0.0, 0.05], "reading": "R"}), "REMOVED")

    def test_gate_precedence_and_a_deliberate_round1_stop(self):
        base = {"G4_failing": [], "G1": True, "missing": [], "per_product": {"J": [], "G2": [], "G3": [], "identity": []}}
        self.assertIsNone(A.first_gate({}, base)[0])
        g = dict(base, G4_failing=["x"])
        self.assertEqual(A.first_gate({"refused": "r"}, g)[0], "INPUTS CHANGED")
        self.assertEqual(A.first_gate({"refused": "r", "prep": "INFEASIBLE"}, base)[0], "RUN REFUSED")
        self.assertEqual(A.first_gate({"prep": "INFEASIBLE"}, base)[0], "INFEASIBLE")
        self.assertEqual(A.first_gate({"interrupted": "time limit"}, base)[0], "INCOMPLETE")
        stop = dict(base, missing=[f"E1/{s}" for s in range(5, 21)], per_product=dict(base["per_product"], J=["E1/2"]))
        self.assertEqual(A.first_gate({"round1": "STOP"}, stop)[0], "JITTER NOT APPLIED",
                         "a round-1 gate failure with the later products intentionally absent is that gate's outcome")
        self.assertEqual(A.first_gate({}, dict(base, G1=False))[0], "NOT REPRODUCED")
        self.assertEqual(A.first_gate({}, dict(base, per_product=dict(base["per_product"], G3=["E2/None"])))[0],
                         "PREMISE FAILED (G3)")
        self.assertEqual(A.first_gate({}, dict(base, missing=["E1/7"]))[0], "INCOMPLETE")

    def test_invalid_branches(self):
        s = np.full(153, 0.01)
        ok = {"E1_jit": np.ones((20, 153)), "E1_base": np.ones(153), "E2_base": np.ones(153), "E3_base": np.ones(153)}
        self.assertEqual(A.invalid_reasons(ok, s, {"invalid": False}), [])
        self.assertTrue(A.invalid_reasons(dict(ok, E1_base=np.zeros(153)), s, None))
        self.assertTrue(A.invalid_reasons(dict(ok, E1_jit=np.zeros((20, 153))), s, None))
        self.assertTrue(A.invalid_reasons(ok, np.where(np.arange(153) == 3, np.nan, s), None))
        self.assertTrue(A.invalid_reasons(ok, s, {"invalid": True}))
        self.assertTrue(A.invalid_reasons(dict(ok, E2_base=np.full(153, np.inf)), s, None))

    def test_s2_and_s3_follow_their_definitions(self):
        sigma = np.full(153, 0.01)
        base = np.ones(153)
        F = np.ones((20, 153))
        F[1, 0] = 1.003   # pair (1, 2): this functional's larger |r|/sigma is 0.3
        st = A.pair_statistic(F, base, sigma)
        self.assertAlmostEqual(st["mean_max"], 0.3 / 10, places=9)
        bases = {"E1": np.ones(153), "E2": np.ones(153), "E3": np.ones(153)}
        bases["E3"] = bases["E3"].copy()
        bases["E3"][5] = 1.02
        s3 = A.policy_statistic(bases, sigma)
        self.assertAlmostEqual(s3["max"], (1 - 1 / 1.02) / 0.01, places=9)
        self.assertEqual(s3["place"]["max"], 0.0)


if __name__ == "__main__":
    unittest.main()
