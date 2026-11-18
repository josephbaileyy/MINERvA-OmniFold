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
        base = {"G4_failing": [], "G1": True, "missing": [],
                "per_product": {"J": [], "G2": [], "G3": [], "identity": [], "binding": []}}
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


class Rev2(unittest.TestCase):
    """The code audits' findings on code 1 (both readers), each with its fix's test."""

    def test_placement_takes_the_lowest_gap_on_a_plateau(self):
        F = f32(np.concatenate([np.arange(1.0, 4.0), np.arange(10.0, 40.0)]))
        U = np.concatenate([F, f32([4.0, 5.0, 6.0, 7.0])])  # scored-only values: B is flat across 3..10
        lower, edges = E.admissible_gaps(U)
        B = np.searchsorted(np.sort(F), lower, side="right")
        self.assertTrue(np.sum(B == 3) >= 4, "the fixture has a plateau of B")
        t_target = 3.0
        N = F.size
        out = E.place(F, U, 31, 0.0)
        i = next(k for k in range(1, out["n"] + 1) if abs(k / (out["n"] + 1) * N - t_target) < 0.5)
        plateau = edges[B == 3]
        self.assertEqual(out["edges"][i - 1], float(plateau[0]), "the lowest gap among tied distances (rule 6)")

    def test_the_slurm_limit_and_the_scripts_cap(self):
        for ok in ("00:50:00", "50:00", "0:49:59"):
            self.assertTrue(A.slurm_limit_ok(ok), ok)
        for bad in ("00:50:01", "01:00:00", "1-00:00:00", "UNLIMITED", "", "0:00"):
            self.assertFalse(A.slurm_limit_ok(bad), bad)
        text = (ND / "sbatch_pfb.sh").read_text()
        self.assertIn("#SBATCH --time=0:50:00\n", text)
        self.assertIn("#SBATCH --job-name=pfb_run\n", text)
        self.assertIn("slurm-limit --timelimit", text)
        self.assertIn('pfb_*) ;; *) refuse "the job name', text)

    def run_job(self, stage, root, env=None):
        import os
        import subprocess
        d = Path(self.tmp) / "deploy"
        if not d.exists():
            d.mkdir()
            subprocess.run(["git", "init", "-q", str(d)], check=True)
            (d / "x").write_text("x")
            subprocess.run(["git", "-C", str(d), "add", "x"], check=True)
            subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], check=True)
        pin = subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        e = {**os.environ, "SLURM_JOB_ID": "77", **(env or {})}
        return subprocess.run(["bash", str(ND / "sbatch_pfb.sh"), str(d), pin, str(stage), str(root)], env=e,
                              capture_output=True, text=True)

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.tmp = self._t.name

    def tearDown(self):
        self._t.cleanup()

    def test_the_job_refuses_a_stale_root_a_bad_stage_and_a_foreign_name(self):
        stage, root = Path(self.tmp) / "stage", Path(self.tmp) / "root"
        r = self.run_job(stage, root, {"PFB_LOCAL_TEST": "1"})
        self.assertEqual(r.returncode, 2)
        self.assertIn("lacks a0-refs", json.loads((stage / "job-77.refused.json").read_text())["refused"])
        (stage / "a0-refs").mkdir(parents=True)
        (stage / "assess_receipt.json").write_text("{}")
        (stage / "smoke-edges").mkdir()
        (stage / "smoke-edges" / "INDEX.json").write_text("{}")
        root.mkdir()
        (stage / "job-77.refused.json").unlink()
        r = self.run_job(stage, root, {"PFB_LOCAL_TEST": "1"})
        self.assertEqual(r.returncode, 2)
        self.assertIn("not fresh", json.loads((stage / "job-77.refused.json").read_text())["refused"])
        self.assertFalse((root / "job-status.json").exists(), "a refusal writes no run status into the old root")
        (stage / "job-77.refused.json").unlink()
        r = self.run_job(stage, Path(self.tmp) / "elsewhere", {"SLURM_JOB_NAME": "pfb_run"})
        self.assertIn("not the declared", json.loads((stage / "job-77.refused.json").read_text())["refused"])
        (stage / "job-77.refused.json").unlink()
        r = self.run_job(stage, Path("/pscratch/sd/j/josephrb/pfb-20261117"), {"SLURM_JOB_NAME": "rdx_s3_a"})
        self.assertIn("pfb_ family", json.loads((stage / "job-77.refused.json").read_text())["refused"])

    def stage_and_root(self):
        import hashlib
        stage, root = Path(self.tmp) / "stage", Path(self.tmp) / "root"
        (stage / "a0-refs").mkdir(parents=True)
        sums = []
        for s in (None, *A.SEEDS):
            p = stage / "a0-refs" / A.name("rs1_A0", s)
            np.savez(p, xsec_flat=np.full(169, 2.0 + (s or 0) * 1e-3), meta=np.array("{}"))
            sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  runs/A0/{p.name}")
        (Path(self.tmp) / "sums").write_text("\n".join(sums) + "\n")
        real = A._REPO / "docs/orchestration/state/s5e/cand/assess_receipt.json"
        (stage / A.SIGMA_NAME).write_bytes(real.read_bytes())
        root.mkdir()
        return stage, root

    def test_g4_rechecks_the_inputs_the_deploy_and_the_sigma_copy(self):
        stage, root = self.stage_and_root()
        npz, bkg = Path(self.tmp) / "in.npz", Path(self.tmp) / "bkg.npz"
        npz.write_bytes(b"x")
        bkg.write_bytes(b"y")
        g = A.gates(root, stage, None, None, rs1_sums=Path(self.tmp) / "sums", npz=str(npz), bkg=str(bkg))
        self.assertIn("the input in.npz", g["G4_failing"])
        self.assertIn("the input bkg.npz", g["G4_failing"])
        self.assertTrue(any("no deploy given" in x for x in g["G4_failing"]))
        g = A.gates(root, stage, Path(self.tmp), "0" * 40, rs1_sums=Path(self.tmp) / "sums", check_inputs=False)
        self.assertTrue(any("not a readable git checkout" in x or "not " in x for x in g["G4_failing"]))
        (stage / A.SIGMA_NAME).write_text("{}")
        g = A.gates(root, stage, None, None, rs1_sums=Path(self.tmp) / "sums", check_inputs=False)
        self.assertIn("the sigma receipt copy", g["G4_failing"])
        self.assertFalse([x for x in g["G4_failing"] if x.startswith("rs1_A0")], "the A0 copies are at their pins")

    def test_identity_is_every_fit_with_the_file_digest(self):
        want = {"max_bin": 255, "forcedbins_filename": "/x/E1_clf1.json"}
        good = {"max_bin": 255, "forcedbins_filename": "/x/E1_clf1.json", "forcedbins_sha256": "a" * 64}
        self.assertEqual(P.identity_problems([good, good], want, "a" * 64), [])
        later = dict(good, max_bin=127, forcedbins_filename="/x/E3_clf1.json")
        self.assertTrue(P.identity_problems([good, later], want, "a" * 64), "a later fit's change is caught")
        self.assertTrue(P.identity_problems([good, dict(good, forcedbins_sha256="b" * 64)], want, "a" * 64))
        self.assertTrue(P.identity_problems([], want, "a" * 64))

    def write_remedy(self, root, s, j, side_overrides=None, meta_overrides=None, index_sha="i" * 64, code=None):
        import hashlib
        code = code or {"fb_pilot_probe.py": "c"}
        p = root / A.expected()[(s, j)]
        p.parent.mkdir(parents=True, exist_ok=True)
        blk = {"set": s, "jitter_seed": j, "edges_index_sha256": index_sha, "code_sha256": code, **(meta_overrides or {})}
        np.savez(p, xsec_flat=np.full(169, 2.0), meta=np.array(json.dumps({"pilot_fb": blk})))
        gates_ = {g: {"pass": True} for g in ("J", "G2", "G3", "identity")}
        side = {"set": s, "jitter_seed": j, "product": p.name, "product_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "edges_index_sha256": index_sha, "code_sha256": code, "gates": gates_, **(side_overrides or {})}
        p.with_name(p.name[:-4] + ".pfb.json").write_text(json.dumps(side))
        return p

    def test_a_sidecar_is_bound_to_its_product(self):
        _, root = self.stage_and_root()
        p = self.write_remedy(root, "E2", None)
        have = {("E2", None): A.expected()[("E2", None)]}
        code = {"fb_pilot_probe.py": "c"}
        self.assertEqual(A.gate_records(root, have, "i" * 64, code)["binding"], [])
        self.write_remedy(root, "E2", None, side_overrides={"product_sha256": "0" * 64})
        self.assertTrue(A.gate_records(root, have, "i" * 64, code)["binding"])
        self.write_remedy(root, "E2", None, meta_overrides={"set": "E3"})
        self.assertTrue(A.gate_records(root, have, "i" * 64, code)["binding"])
        self.write_remedy(root, "E2", None)
        self.assertTrue(A.gate_records(root, have, "j" * 64, code)["binding"], "another INDEX.json")
        self.assertTrue(A.gate_records(root, have, "i" * 64, {"fb_pilot_probe.py": "d"})["binding"], "other code")
        p.with_name(p.name[:-4] + ".pfb.json").unlink()
        self.assertTrue(A.gate_records(root, have, "i" * 64, code)["binding"], "no sidecar")

    def test_exits_4_and_5_and_operational_failures_keep_their_place(self):
        base = {"G4_failing": [], "G1": True, "missing": ["E1/7"],
                "per_product": {"J": [], "G2": [], "G3": ["E1/2"], "identity": [], "binding": []}}
        self.assertEqual(A.first_gate({"inputs_changed": "exit 4"}, base)[0], "INPUTS CHANGED")
        self.assertEqual(A.first_gate({"refused": "grid-membership exit 5 in: E1_3"}, base)[0], "RUN REFUSED")
        self.assertEqual(A.first_gate({"interrupted": "tasks failed: E1_7:1", "task_failures": " E1_7:1"}, base)[0],
                         "INCOMPLETE", "a crashed task outranks another product's G3 failure")
        self.assertEqual(A.first_gate({"task_failures": " E1_7:1"}, base)[0], "INCOMPLETE")
        b2 = dict(base, per_product=dict(base["per_product"], binding=["E1/2: x"]))
        self.assertEqual(A.first_gate({}, b2)[0], "PREMISE FAILED (identity)")
        self.assertEqual(A.first_gate({}, dict(b2, G1=False))[0], "NOT REPRODUCED", "G1 precedes a binding failure")
        text = (ND / "sbatch_pfb.sh").read_text()
        self.assertIn('4) bad4="$bad4 $id"', text)
        self.assertIn('5) bad5="$bad5 $id"', text)

    def test_s1_invalid_reads_invalid_and_non_finite_values_write_as_null(self):
        self.assertEqual(A.s1_reading({"invalid": True, "reading": "INVALID", "interval_90": [0.1, 0.2]}), "INVALID")
        self.assertEqual(A.s1_reading({"invalid": True, "reading": "R", "interval_90": [0.0, 0.05]}), "INVALID",
                         "the invalid flag wins over any band")
        out = A.json_safe({"S1": {"interval_90": [float("nan"), 0.05], "M": float("inf")}, "ok": 1.0})
        spots = []
        out = A.json_safe({"S1": {"interval_90": [float("nan"), 0.05], "M": float("inf")}, "ok": 1.0}, "", spots)
        self.assertEqual(out["S1"]["interval_90"], [None, 0.05])
        self.assertEqual(sorted(spots), ["/S1/M", "/S1/interval_90[0]"])
        json.dumps(out, allow_nan=False)

    def test_base_only_statistics_survive_a_round1_stop(self):
        stage, root = self.stage_and_root()
        for s in A.SETS:
            self.write_remedy(root, s, None)
        p = root / A.expected()[("E3", None)]
        z = dict(np.load(p))
        z["xsec_flat"] = np.full(169, 2.02)
        np.savez(p, **z)
        have = {(s, None): A.expected()[(s, None)] for s in A.SETS}
        st = A.statistics(root, have, stage / "a0-refs", np.eye(169), np.full(153, 0.01), None)
        self.assertIn("S3", st, "S3 needs no jitter")
        self.assertNotIn("S1", st)
        self.assertIn("readouts_shift_from_e", st)
        self.assertAlmostEqual(st["S3"]["max"], (1 - 2.0 / 2.02) / 0.01, places=6)

    def test_the_analysis_is_bound_to_one_job(self):
        stage, root = self.stage_and_root()
        with self.assertRaisesRegex(SystemExit, "names job"):
            A.analyze(root, stage, {"job": "11"}, "12", U=np.eye(169), check_inputs=False)

    def test_g0_records_every_role_and_feature(self):
        good = np.column_stack([f32(np.round(np.random.default_rng(k).normal(3, 1, 3000), 3)) for k in range(5)])
        bad = good.copy()
        bad[:, 2] = f32(np.arange(3000) % 7)  # too few gaps on one feature
        mats = {r: (good if r != "reg" else bad, None) for r in E.ROLES}
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(E.Infeasible) as cm:
                E.build_edges(mats, Path(d) / "edges")
            rec = json.loads(str(cm.exception))
            self.assertEqual(len(rec["diagnostics"]), 3 * 4 * 5)
            self.assertEqual(sorted(rec["failing"]), sorted(f"{s}/reg/feature 2" for s in E.SETS))
            self.assertIn("admissible gaps", rec["diagnostics"]["E1/reg/feature 2"]["first_failing_rule"])
            self.assertIsNone(rec["diagnostics"]["E1/clf1/feature 0"]["first_failing_rule"])
            self.assertFalse((Path(d) / "edges").exists(), "G0 writes nothing when it refuses")

    def test_the_smoke_is_a_login_node_step(self):
        import os
        import subprocess
        r = subprocess.run(["bash", str(ND / "pfb_smoke_prep.sh"), "/x", "0" * 40, self.tmp],
                           env={**os.environ, "SLURM_JOB_ID": "5"}, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("outside any Slurm job", r.stderr)


if __name__ == "__main__":
    unittest.main()
