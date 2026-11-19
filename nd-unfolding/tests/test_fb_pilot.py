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
        self.assertTrue(a2["pass"] and bc2["pass"], "a bound moved where no split acts passes G3")
        self.assertTrue(np.array_equal(m0.predict_proba(self.X), m2.predict_proba(self.X)),
                        "a bound moved where no split acts changes no prediction")
        scored = np.random.default_rng(5).uniform(self.X.min(axis=0), self.X.max(axis=0), (500, self.X.shape[1]))
        # scored rows the fit never saw: a bound moved where no split acts moves no fit row's bin, so no threshold used
        self.assertTrue(np.array_equal(m0.predict_proba(scored), m2.predict_proba(scored)))
        self.assertTrue(np.array_equal(m0.predict_proba(scored), m1.predict_proba(scored)))

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
                    o = A.outcome(self.stats(s1, s2, s3))
                    seen[(s1, s2, s3)] = o["row"]
                    self.assertEqual(o["outcome"], {1: "NOT A REMEDY", 2: "NOT AN OPTION AS DECLARED",
                                                    3: "NO OPTION STATEMENT", 4: "OPTION A", 5: "OPTION B",
                                                    6: "OPTION C", 7: "OPTION D"}[o["row"]], (s1, s2, s3))
        self.assertEqual(len(seen), 16)
        self.assertEqual(seen[("REMOVED", "STAB_PASS", "POLICY-STABLE")], 4)
        self.assertEqual(seen[("REMOVED", "STAB_PASS", "POLICY-SENSITIVE")], 5)
        self.assertEqual(seen[("REDUCED", "STAB_PASS", "POLICY-SENSITIVE")], 7)
        self.assertEqual(seen[("INCONCLUSIVE", "STAB_PASS", "POLICY-SENSITIVE")], 3)
        self.assertEqual(seen[("REDUCED", "STAB_PASS", "POLICY-STABLE")], 6)
        self.assertEqual(seen[("INCONCLUSIVE", "STAB_FAIL", "POLICY-STABLE")], 2)
        self.assertEqual(seen[("NOT REMOVED", "STAB_FAIL", "POLICY-SENSITIVE")], 1)

    def test_the_bars_include_equality_and_rows_5_7_name_what_crossed(self):
        s3 = {"median": 0.2, "max": 2.0, "place": {"median": 0.1, "max": 0.3}, "res": {"median": 0.2, "max": 2.0}}
        text = A.statement(5, s3)
        self.assertIn("maximum 2 beyond 1.0", text)
        self.assertNotIn("median 0.2 beyond", text)
        self.assertIn("at most 10 %", A.statement(4, self.S3))
        self.assertEqual(A.s2_reading({"mean_median": 0.3, "mean_max": 1.0}), "STAB_PASS", "S2's bars include equality")
        self.assertEqual(A.s2_reading({"mean_median": 0.3, "mean_max": np.nextafter(1.0, 2)}), "STAB_FAIL")
        self.assertEqual(A.s2_reading({"mean_median": np.nextafter(0.3, 1), "mean_max": 1.0}), "STAB_FAIL")
        self.assertEqual(A.s3_reading({"median": 0.3, "max": 1.0}), "POLICY-STABLE", "S3's bars include equality")
        self.assertEqual(A.s3_reading({"median": 0.3, "max": np.nextafter(1.0, 2)}), "POLICY-SENSITIVE")
        self.assertEqual(A.s3_reading({"median": np.nextafter(0.3, 1), "max": 1.0}), "POLICY-SENSITIVE")
        self.assertIn("in pseudo-data σ", A.statement(4, self.S3))
        self.assertIn("in pseudo-data σ", A.statement(6, self.S3))
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
        self.assertTrue(A.invalid_reasons(dict(ok, E1_jit=np.zeros((20, 153))), s, {"invalid": False}))
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
        self.assertIn('pfb_*) ;; *) preflight "the job name', text)

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
        blk = {"set": s, "jitter_seed": j, "edges_index_sha256": index_sha, "code_sha256": code,
               "gates_pass": {g: True for g in A.GATES}, **(meta_overrides or {})}
        np.savez(p, xsec_flat=np.full(169, 2.0), meta=np.array(json.dumps({"pilot_fb": blk, "slurm_job": "77"})))
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
        self.assertTrue(A.gate_records(root, have, None, code)["binding"], "a missing INDEX fails, never skips")
        self.assertTrue(A.gate_records(root, have, "i" * 64, None)["binding"], "missing deploy code fails, never skips")
        self.write_remedy(root, "E2", None, side_overrides={"gates": {g: {"pass": True} for g in A.GATES}},
                          meta_overrides={"gates_pass": {"J": True, "G2": False, "G3": True, "identity": True}})
        b = A.gate_records(root, have, "i" * 64, code)
        self.assertTrue(b["binding"] and "gates_pass" in b["binding"][0], "the sidecar's pass bits must be the meta's")
        self.assertEqual(b["G2"], [], "a mismatched sidecar is not trusted for any gate")
        self.write_remedy(root, "E2", None)
        p.with_name(p.name[:-4] + ".pfb.json").write_text("{not json")
        self.assertIn("unreadable", A.gate_records(root, have, "i" * 64, code)["binding"][0])
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
        rd = str(root.resolve())
        ok = {"job": "12", "pin": "p", "root": rd}
        sp = lambda st, path=None: A.status_problem(st, "12", "p", path, root, stage, root_declared=rd)  # noqa: E731
        self.assertIsNone(sp(ok, root / "job-status.json"))
        self.assertIsNone(sp(ok, stage / "job-12.refused.json"))
        self.assertIn("pin", sp(dict(ok, pin="q")))
        self.assertIn("root", sp(dict(ok, root="/elsewhere")))
        self.assertIn("is not", sp(ok, stage / "job-11.refused.json"))
        self.assertIn("no outcome", sp(dict(ok, preflight_refused="x")))
        self.assertIn("names root", A.status_problem(ok, "12", "p", None, root, stage), "the declared root by default")

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



class Rev3(unittest.TestCase):
    """The code-2 confirmation audits (Codex FAIL, Grok PASS WITH FIXES), each finding with its fix's test."""
    JOB = "77"
    DECLARED_PY_GIT = {"PYTHONNOUSERSITE": "1", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.tmp = Path(self._t.name).resolve()

    def tearDown(self):
        self._t.cleanup()

    def env(self, **kw):
        import os
        e = {k: v for k, v in os.environ.items() if not k.startswith(("SLURM_", "PFB_"))}
        e["PATH"] = f"{Path(sys.executable).parent}:/usr/bin:/bin:/usr/sbin:/sbin"
        e.update(kw)
        return e

    def deploy(self):
        """A clean git deploy with the files the scripts and the analysis read: stub code, a stub setup file, and the
        real fb_pilot_analyze.py (the smoke receipt); the stub prep imports a module, so bytecode would land here."""
        import hashlib
        import subprocess
        d = self.tmp / "deploy"
        if d.exists():
            return d, self.pin, self.setup_sha
        (d / "nd-unfolding").mkdir(parents=True)
        for f in A.CODE_FILES:
            (d / "nd-unfolding" / f).write_text(f"# stub {f}\n")
        (d / "nd-unfolding" / "rounding_mechanism_probe.py").write_text('STABILITY = {"ratio": "ratio.json"}\n')
        (d / "nd-unfolding" / "fb_pilot_probe.py").write_text(
            "import os, sys\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
            "import rounding_mechanism_probe\n"
            "a = sys.argv\nout = a[a.index('--edges-out') + 1]\nos.makedirs(a[a.index('--out') + 1])\n"
            "os.makedirs(out)\n"
            "for s in ('E1', 'E2', 'E3'):\n    for r in ('clf1', 'reg', 'clf2', 'ref'):\n"
            "        open(os.path.join(out, s + '_' + r + '.json'), 'w').write('[]\\n')\n"
            "if not os.environ.get('PFB_STUB_NO_INDEX'):\n    open(os.path.join(out, 'INDEX.json'), 'w').write('{}\\n')\n")
        (d / "nd-unfolding" / "fb_pilot_analyze.py").write_bytes((ND / "fb_pilot_analyze.py").read_bytes())
        self.nested = self.tmp / "ext" / "nested_setup.sh"  # outside the deploy, as the real setup's nested files are
        self.nested.parent.mkdir()
        self.nested.write_text("export STUB_NESTED=1\n")
        self.deny_flag, self.extra_flag = self.tmp / "ext" / "deny", self.tmp / "ext" / "extra"
        self.path_flag = self.tmp / "ext" / "path"
        self.nl_a, self.nl_b, self.py_flag = self.tmp / "ext" / "nl_a", self.tmp / "ext" / "nl_b", self.tmp / "ext" / "py"
        (d / "setup_salloc_env.sh").write_text(f"# stub setup\nexport STUB_SETUP=1\nsource {self.nested}\n"
                                               f"[ -f {self.deny_flag} ] && export PYTHONSTARTUP=/nowhere\n"
                                               f"[ -f {self.extra_flag} ] && export STUB_EXTRA=1\n"
                                               f"[ -f {self.path_flag} ] && export PATH=/stub/extra:$PATH\n"
                                               f"[ -f {self.nl_a} ] && export CONDA_PREFIX=\"$(printf 'p\\nCONDARC=q')\" CONDARC=r\n"
                                               f"[ -f {self.nl_b} ] && export CONDA_PREFIX=p CONDARC=\"$(printf 'q\\nCONDARC=r')\"\n"
                                               f"[ -f {self.py_flag} ] && export PATH={self.tmp / 'pystub'}:$PATH\n"
                                               "env | sed 's/^/ENV-DUMP /'\n")
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"], check=True)
        self.pin = subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.setup_sha = hashlib.sha256((d / "setup_salloc_env.sh").read_bytes()).hexdigest()
        return d, self.pin, self.setup_sha

    def deploy_untouched(self, d):
        import subprocess
        st = subprocess.run(["git", "--no-optional-locks", "-C", str(d), "status", "--porcelain", "--untracked-files=all",
                             "--ignored"],
                            capture_output=True, text=True).stdout
        self.assertEqual(st, "", "nothing is written in the deploy (no __pycache__, nothing untracked)")
        self.assertEqual(list(d.rglob("__pycache__")), [])

    # -- the analysis: a complete run, then one defect at a time --------------------------------------------------
    def stage(self):
        import hashlib
        stage = self.tmp / "stage"
        (stage / "a0-refs").mkdir(parents=True)
        sums = []
        for s_ in (None, *A.SEEDS):
            q = stage / "a0-refs" / A.name("rs1_A0", s_)
            np.savez(q, xsec_flat=np.full(169, 2.0 + (s_ or 0) * 1e-3), meta=np.array("{}"))
            sums.append(f"{hashlib.sha256(q.read_bytes()).hexdigest()}  runs/A0/{q.name}")
        (self.tmp / "sums").write_text("\n".join(sums) + "\n")
        (stage / A.SIGMA_NAME).write_bytes((A._REPO / "docs/orchestration/state/s5e/cand/assess_receipt.json").read_bytes())
        return stage

    def edges(self, root):
        import hashlib
        e = root / "edges"
        e.mkdir(parents=True)
        idx = {"schema": "pfb-edges/1", "K": E.K, "sets": {}}
        for s_ in A.SETS:
            idx["sets"][s_] = {"max_bin": E.SETS[s_]["max_bin"], "offset": E.SETS[s_]["offset"], "roles": {}}
            for r in A.ROLES:
                f = e / f"{s_}_{r}.json"
                f.write_text(f"[{s_} {r}]\n")
                idx["sets"][s_]["roles"][r] = {
                    "file": f.name, "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                    "features": [{"edges": [1.0, 2.0], "z": 0, "n": 2, "admissible": 5} for _ in range(5)]}
        (e / "INDEX.json").write_text(json.dumps(idx))
        return hashlib.sha256((e / "INDEX.json").read_bytes()).hexdigest()

    def put(self, root, s_, j, x, job=JOB, gates_pass=None, side_gates=None, index_sha=None, code=None):
        import hashlib
        q = root / A.expected()[(s_, j)]
        q.parent.mkdir(parents=True, exist_ok=True)
        meta = {"slurm_job": job, "seconds_unfold": 1.0}
        if s_ != "A0R":
            gp = gates_pass or {g: True for g in A.GATES}
            meta["pilot_fb"] = {"set": s_, "jitter_seed": j, "edges_index_sha256": index_sha, "code_sha256": code,
                                "gates_pass": gp}
        np.savez(q, xsec_flat=x, meta=np.array(json.dumps(meta)))
        if s_ != "A0R":
            side = {"set": s_, "jitter_seed": j, "product": q.name, "product_sha256": hashlib.sha256(q.read_bytes()).hexdigest(),
                    "edges_index_sha256": index_sha, "code_sha256": code, "gate_seconds": 0.1,
                    "gates": side_gates or {g: {"pass": True} for g in A.GATES}}
            q.with_name(q.name[:-4] + ".pfb.json").write_text(json.dumps(side))
        return q

    def run_tree(self, job=JOB):
        d, pin, _ = self.deploy()
        stage, root = self.stage(), self.tmp / "root"
        root.mkdir()
        isha = self.edges(root)
        code = A.code_shas(d)
        self.put(root, "A0R", None, np.full(169, 2.0), job)
        for s_, j in A.expected():
            if s_ == "A0R":
                continue
            x = np.full(169, 2.0) * (1 + {"E1": 0, "E2": 1e-6, "E3": 2e-6}[s_] + (j or 0) * 1e-7)
            self.put(root, s_, j, x, job, index_sha=isha, code=code)
        self.ctx = {"deploy": d, "pin": pin, "stage": stage, "root": root, "index_sha": isha, "code": code}
        return self.ctx

    def analyze(self, status=None, job=JOB, status_path=None):
        c = self.ctx
        st = status if status is not None else {"job": job, "pin": c["pin"], "root": str(c["root"])}
        import unittest.mock as um
        with um.patch.object(A, "RS1_SUMS", self.tmp / "sums"):
            return A.analyze(c["root"], c["stage"], st, job, c["deploy"], c["pin"], U=np.eye(169), check_inputs=False,
                             status_path=status_path, root_declared=str(c["root"]))

    def test_a_complete_valid_run_reads_one_row(self):
        self.run_tree()
        out = self.analyze()
        self.assertIn("row", out["outcome"], out["outcome"])
        self.assertEqual(out["gates"]["per_product"]["binding"], [])
        self.assertEqual(out["gates"]["foreign"], [])
        self.assertTrue(out["gates"]["G1"])
        for k in ("S1", "S2", "S3", "readouts_cells16_relative_policy_shift"):
            self.assertIn(k, out["statistics"])

    def test_a_missing_index_or_an_altered_edge_file_fails_identity(self):
        """Codex HIGH 1, Grok 2: a missing INDEX disabled the identity check; now absent evidence FAILS."""
        c = self.run_tree()
        (c["root"] / "edges" / "INDEX.json").unlink()
        out = self.analyze()
        self.assertEqual(out["outcome"]["outcome"], "PREMISE FAILED (identity)")
        self.assertIn("INDEX.json is missing", out["outcome"]["why"])
        self._t.cleanup(); self.setUp()
        c = self.run_tree()
        (c["root"] / "edges" / "E2_reg.json").write_text("changed\n")
        out = self.analyze()
        self.assertEqual(out["outcome"]["outcome"], "PREMISE FAILED (identity)")
        self.assertIn("E2_reg.json is not the file INDEX.json records", out["outcome"]["why"])

    def test_products_of_another_job_are_run_refused(self):
        """Codex HIGH 2: the job id is bound to every product's meta, not only to the caller's arguments."""
        self.run_tree(job="11")
        out = self.analyze(job="12")
        self.assertEqual(out["outcome"]["outcome"], "RUN REFUSED")
        self.assertIn("job '11'", out["outcome"]["why"])
        out = self.analyze(job="11")
        self.assertIn("row", out["outcome"])
        c = self.ctx
        self.put(c["root"], "E2", None, np.full(169, 2.0), job=None, index_sha=c["index_sha"], code=c["code"])
        self.assertEqual(self.analyze(job="11")["outcome"]["outcome"], "RUN REFUSED", "a product with no job fails")
        with self.assertRaisesRegex(SystemExit, "pin"):
            self.analyze({"job": "11", "pin": "0" * 40, "root": str(c["root"])}, job="11")
        with self.assertRaisesRegex(SystemExit, "is not"):
            self.analyze(job="11", status_path=c["stage"] / "elsewhere.json")

    def test_a_malformed_artifact_keeps_the_named_outcome(self):
        """Codex MEDIUM 5: INPUTS CHANGED is returned before any unsafe read; an unreadable product or sidecar is
        classified, never raised."""
        c = self.run_tree()
        (c["stage"] / A.SIGMA_NAME).write_text("{}")
        out = self.analyze()
        self.assertEqual(out["outcome"]["outcome"], "INPUTS CHANGED")
        self.assertEqual(out["statistics_NOT_READ"], {})
        (c["stage"] / A.SIGMA_NAME).unlink()
        self.assertEqual(self.analyze()["outcome"]["outcome"], "INPUTS CHANGED", "a missing sigma copy")
        self._t.cleanup(); self.setUp()
        c = self.run_tree()
        q = c["root"] / A.expected()[("E1", 9)]
        q.write_bytes(q.read_bytes()[:40])
        out = self.analyze()
        self.assertEqual(out["outcome"]["outcome"], "INCOMPLETE")
        self.assertIn("unreadable", out["outcome"]["why"])
        self.assertIn("S3", out["statistics_NOT_READ"], "base-only statistics survive")
        q = c["root"] / A.expected()[("E1", 9)]
        self.put(c["root"], "E1", 9, np.full(169, 2.0), index_sha=c["index_sha"], code=c["code"])
        q.with_name(q.name[:-4] + ".pfb.json").write_text("{")
        self.assertEqual(self.analyze()["outcome"]["outcome"], "PREMISE FAILED (identity)")

    def test_a_stage_copy_must_be_a_plain_file(self):
        """The LOW item: a symlink or hard link in the stage could reach a protected original."""
        import os
        c = self.run_tree()
        ref = c["stage"] / "a0-refs" / A.name("rs1_A0", 3)
        real = self.tmp / "original.npz"
        os.replace(ref, real)
        ref.symlink_to(real)
        self.assertEqual(self.analyze()["outcome"]["outcome"], "INPUTS CHANGED")
        ref.unlink()
        os.link(real, ref)
        out = self.analyze()
        self.assertEqual(out["outcome"]["outcome"], "INPUTS CHANGED")
        self.assertTrue(any("hard link" in x for x in out["gates"]["G4_failing"]))

    def test_the_prep_step_keeps_the_runners_exit_4(self):
        """Codex MEDIUM 6, Grok 1: a returned input-digest failure stays 4 (INPUTS CHANGED), not 5."""
        import unittest.mock as um
        for rc, want in ((4, 4), (2, 2), (0, 5)):
            with um.patch.object(P.esp, "main", lambda argv, rc=rc: rc):
                got = P.main(["prep", "--edges-out", str(self.tmp / f"e{rc}"), "--", "--x"])
            self.assertEqual(got, want, rc)

    def test_s2_survives_s1s_own_invalid_and_each_base_has_its_shift(self):
        """Codex 7: S1's own INVALID suppresses S1's reading only; one base suffices for its own shift."""
        c = self.run_tree()
        have = {k: v for k, v in A.expected().items()}
        sigma = np.asarray(json.loads((c["stage"] / A.SIGMA_NAME).read_text())["sigma_rel_pct"], float) / 100
        import unittest.mock as um
        ra = __import__("rounding_mechanism_analyze")
        real = ra.spread_ratio
        with um.patch.object(ra, "spread_ratio", lambda *a, **k: dict(real(*a, **k), invalid=True)):
            st = A.statistics(c["root"], have, c["stage"] / "a0-refs", np.eye(169), sigma, None)
        self.assertTrue(st["INVALID"]["S1"])
        self.assertEqual(st["INVALID"]["S2"], [])
        self.assertIn("S2", st)
        one = {("E2", None): have[("E2", None)]}
        st = A.statistics(c["root"], one, c["stage"] / "a0-refs", np.eye(169), sigma, None)
        self.assertEqual(sorted(st["readouts_shift_from_e"]), ["E2"])
        self.assertNotIn("S3", st)

    def test_g0_counts_survive_a_policy_failure(self):
        """Codex 7: a zero-band failure still reports z, n and the admissible-gap count; a non-finite value cannot."""
        F = f32(np.concatenate([np.arange(1.0, 200.0), [1e-35]]))
        d = E.diagnose(F, F, 63)
        self.assertIsNotNone(d["first_failing_rule"])
        self.assertEqual((d["z"], d["n"]), (1, 61))
        self.assertEqual(d["admissible"], int(E.admissible_gaps(F)[0].size))
        d = E.diagnose(np.append(F, np.nan), F, 63)
        self.assertIsNone(d["admissible"])

    # -- the job script ---------------------------------------------------------------------------------------------
    def run_job(self, stage, root, **env):
        import subprocess
        d, pin, _ = self.deploy()
        return subprocess.run(["bash", str(ND / "sbatch_pfb.sh"), str(d), env.pop("PIN", pin), str(stage), str(root)],
                              env=self.env(**env), capture_output=True, text=True, cwd=self.tmp)

    def test_the_test_switch_cannot_reach_a_real_job(self):
        """Codex HIGH 4, Grok 3: inside Slurm any PFB_ variable refuses, even empty; then the one-node, family, root
        and stage checks run; nothing is written before the stage is validated."""
        stage, root = self.tmp / "stage", self.tmp / "root"
        stage.mkdir()
        slurm = {"SLURM_JOB_ID": "77", "SLURM_JOB_NUM_NODES": "1", "SLURM_JOB_NAME": "pfb_run", "SLURM_EXPORT_ENV": "NIL"}
        for extra, why in (({"PFB_LOCAL_TEST": "1"}, "PFB_ variables"), ({"PFB_LOCAL_TEST": ""}, "PFB_ variables"),
                           ({"SLURM_EXPORT_ENV": "ALL"}, "export mode is 'ALL', not the approved NIL"),
                           ({"SLURM_EXPORT_ENV": "NONE"}, "export mode is 'NONE', not the approved NIL"),
                           ({"PFB_LOCAL_TEST": "0"}, "PFB_ variables"), ({"PFB_SETUP_SHA": "x"}, "PFB_ variables"),
                           ({"SLURM_JOB_NUM_NODES": "2"}, "nodes, not 1"),
                           ({"SLURM_JOB_NAME": "rdx_s3_a"}, "pfb_ family")):
            r = self.run_job(A.STAGE_DECLARED, A.ROOT_DECLARED, **{**slurm, **extra})
            self.assertEqual(r.returncode, 2, extra)
            self.assertIn(why, r.stderr, extra)
        r = self.run_job(A.STAGE_DECLARED, root, **slurm)
        self.assertIn("is not the declared /pscratch/sd/j/josephrb/pfb-20261117", r.stderr)
        r = self.run_job(stage, A.ROOT_DECLARED, **slurm)
        self.assertIn("is not the declared /pscratch/sd/j/josephrb/pfb-20261117-stage", r.stderr)
        self.assertEqual(list(stage.iterdir()), [], "a refusal before the stage is validated writes nothing")
        r = self.run_job(stage, root)
        self.assertIn("runs only under sbatch", r.stderr)
        text = (ND / "sbatch_pfb.sh").read_text()
        self.assertIn("#SBATCH --output=/pscratch/sd/j/josephrb/pfb-20261117-stage/slurm-%j.out\n", text)
        self.assertIn("#SBATCH --error=/pscratch/sd/j/josephrb/pfb-20261117-stage/slurm-%j.err\n", text)

    def clean_job_files(self, stage):
        for q in stage.glob("job-local.*"):
            q.unlink()

    def staged(self):
        """The stage as the job finds it: the smoke created it (local mode), then the connect copied a0-refs/ and the
        sigma receipt in."""
        (self.tmp / "cwd").mkdir(exist_ok=True)
        _, _, sha = self.deploy()
        stage = self.tmp / "stage"
        r = self.run_smoke(stage, PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (stage / "a0-refs").mkdir()
        for s_ in (None, *A.SEEDS):
            (stage / "a0-refs" / A.name("rs1_A0", s_)).write_bytes(b"a0")
        (stage / A.SIGMA_NAME).write_text("{}")
        return stage, sha

    def test_the_job_preflight_spends_no_root(self):
        """Every refusal but an existing root is a preflight refusal, recorded in the stage before the root exists; an
        existing root is RUN REFUSED; the setup file and its sourced closure are pinned; relative paths refuse."""
        stage, sha = self.staged()
        root = self.tmp / "root"
        root.mkdir()
        loc = {"PFB_LOCAL_TEST": "1", "PFB_SETUP_SHA": sha}
        r = self.run_job(stage, root, **loc)
        self.assertEqual(r.returncode, 2, r.stderr)
        rec = json.loads((stage / "job-local.refused.json").read_text())
        self.assertIn("not fresh", rec["refused"], rec)
        self.assertEqual((rec["job"], rec["root"]), ("local", str(root)))
        root.rmdir()

        def refused(**env):
            self.clean_job_files(stage)
            r = self.run_job(stage, root, **{**loc, **env})
            self.assertEqual(r.returncode, 2, r.stderr)
            return json.loads((stage / "job-local.refused.json").read_text())["preflight_refused"]

        self.assertIn("setup_salloc_env.sh is not the pinned one", refused(PFB_SETUP_SHA="0" * 64))
        self.assertIn("deploy HEAD", refused(PIN="0" * 40))
        self.nested.write_text("export STUB_NESTED=2\n")  # the setup's sourced closure moved since the smoke
        self.assertIn("setup closure", refused())
        self.nested.write_text("export STUB_NESTED=1\n")
        self.extra_flag.write_text("")  # the setup now leaves a name the smoke's setup did not
        self.assertIn("smoke receipt", refused())
        self.extra_flag.unlink()
        rec = json.loads((stage / "smoke-receipt.json").read_text())
        (stage / "smoke-receipt.json").unlink()
        (stage / "smoke-receipt.json").write_text(json.dumps(dict(rec, local_test=False)))
        self.assertIn("smoke receipt", refused())
        (stage / "smoke-receipt.json").unlink()
        (stage / "smoke-receipt.json").write_text(json.dumps(rec))
        (stage / "extra").symlink_to(self.tmp / "deploy")
        self.assertIn("the stage holds something other", refused())
        (stage / "extra").unlink()
        (self.tmp / "deploy" / "nd-unfolding" / "lightgbm.py").write_text("__version__ = '4.6.0'\n")
        self.assertIn("untracked .py", refused())
        (self.tmp / "deploy" / "nd-unfolding" / "lightgbm.py").unlink()
        self.assertFalse(root.exists(), "no preflight refusal creates the root")
        self.clean_job_files(stage)
        r = self.run_job("stage", root, **loc)
        self.assertIn("canonical absolute", r.stderr)
        r = self.run_job(stage, "/pscratch/sd/j/josephrb/x", **loc)
        self.assertIn("never names a cluster path", r.stderr)
        self.deploy_untouched(self.tmp / "deploy")

    def test_the_job_writes_through_no_pre_placed_link(self):
        """Code 4: every file the job creates in the stage is created new (O_CREAT|O_EXCL|O_NOFOLLOW); a pre-placed
        symlink at the env log or the refusal record refuses, and its target is never written."""
        stage, sha = self.staged()
        loc = {"PFB_LOCAL_TEST": "1", "PFB_SETUP_SHA": sha}
        victim = self.tmp / "victim.txt"
        victim.write_text("untouched\n")
        (stage / "job-local.env.log").symlink_to(victim)
        r = self.run_job(stage, self.tmp / "root", **loc)
        self.assertEqual(r.returncode, 2)
        self.assertIn("cannot create", r.stderr)
        self.assertEqual(victim.read_text(), "untouched\n")
        (stage / "job-local.env.log").unlink()
        (stage / "job-local.refused.json").unlink()
        (stage / "job-local.refused.json").symlink_to(victim)
        r = self.run_job(stage, self.tmp / "root", PIN="0" * 40, **loc)
        self.assertEqual(r.returncode, 2)
        self.assertIn("deploy HEAD", r.stderr)
        self.assertEqual(victim.read_text(), "untouched\n", "the refusal record is never written through a link")
        self.assertFalse((self.tmp / "root").exists())

    # -- the smoke --------------------------------------------------------------------------------------------------
    def run_smoke(self, stage, **env):
        import subprocess
        d, pin, sha = self.deploy()
        return subprocess.run(["bash", str(ND / "pfb_smoke_prep.sh"), str(d), env.pop("PIN", pin), str(stage)],
                              env=self.env(**env), capture_output=True, text=True, cwd=self.tmp / "cwd")

    def test_the_smoke_writes_only_under_its_stage(self):
        """Codex HIGH 3 (code 2) and code 4: the smoke creates a fresh stage, writes nothing in the deploy (no bytecode,
        no git index refresh) or the caller's directory, pins the setup file and records its sourced closure, and a
        failed final hash fails the exit status."""
        import os
        (self.tmp / "cwd").mkdir()
        _, _, sha = self.deploy()
        later = (self.tmp / "deploy" / "setup_salloc_env.sh").stat().st_mtime_ns + 5 * 10 ** 9
        os.utime(self.tmp / "deploy" / "setup_salloc_env.sh", ns=(later, later))  # stat-dirty: a plain status rewrites
        idx = self.tmp / "deploy" / ".git" / "index"
        before = idx.stat().st_mtime_ns
        stage = self.tmp / "stage"
        r = self.run_smoke(stage, PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        got = sorted(str(q.relative_to(stage)) for q in stage.rglob("*"))
        self.assertEqual(got, sorted(["smoke-edges", "smoke-env.log", "smoke-receipt.json", "smoke-unused", "smoke.log",
                                      "smoke-setup-env.txt",
                                      *(f"smoke-edges/{f}" for f in A.EDGE_FILES)]))
        rec = json.loads((stage / "smoke-receipt.json").read_text())
        self.assertEqual(rec["local_test"], True)
        self.assertEqual(sorted(rec["setup_closure"]), sorted(os.path.realpath(q) for q in
                                                               (self.tmp / "deploy" / "setup_salloc_env.sh", self.nested)))
        self.assertEqual(idx.stat().st_mtime_ns, before, "the deploy's git index is never refreshed")
        self.deploy_untouched(self.tmp / "deploy")
        self.assertEqual(list((self.tmp / "cwd").iterdir()), [])
        tr = self.tmp / "trace.txt"  # bash 3.2 can drop the space PS4 ends with; the closure reads both forms
        tr.write_text(f"++@{self.nested}@export X=1\n+++@{self.tmp / 'deploy' / 'setup_salloc_env.sh'}@ y\n")
        self.assertEqual(sorted(A.setup_closure(tr)), sorted(os.path.realpath(q) for q in
                                                             (self.nested, self.tmp / "deploy" / "setup_salloc_env.sh")))
        r = self.run_smoke(stage, PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha)
        self.assertEqual(r.returncode, 2, "a second smoke into the same stage refuses")
        self.assertIn("exists: the smoke creates it", r.stderr)
        for bad, why in (("stage2", "absolute"), (f"{self.tmp}/x/../stage3", "canonical"),
                         (f"{self.tmp}/missing/stage", "parent")):
            r = self.run_smoke(bad, PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha)
            self.assertEqual(r.returncode, 2, bad)
            self.assertIn(why, r.stderr, bad)
        self.assertEqual(list((self.tmp / "cwd").iterdir()), [], "a relative stage creates nothing")
        r = self.run_smoke(self.tmp / "stage4", PFB_LOCAL_TEST="1", PFB_SETUP_SHA="0" * 64)
        self.assertIn("not the pinned one", r.stderr)
        self.assertFalse((self.tmp / "stage4").exists(), "a refusal before the stage is created writes nothing")
        r = self.run_smoke(self.tmp / "stage5", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha, PFB_STUB_NO_INDEX="1")
        self.assertEqual(r.returncode, 9, "prep exited 0 but left no INDEX: the final hash fails the smoke")
        self.assertFalse((self.tmp / "stage5" / "smoke-receipt.json").exists())
        r = self.run_smoke(self.tmp / "stage6", PFB_SETUP_SHA=sha)
        self.assertIn("is not the declared /pscratch/sd/j/josephrb/pfb-20261117-stage", r.stderr)
        self.assertFalse((self.tmp / "stage6").exists())
        self.assertEqual(self.run_smoke(self.tmp / "stage7", PFB_LOCAL_TEST="1", SLURM_JOB_ID="5").returncode, 2)

    def test_the_environment_is_the_declared_one(self):
        """Code 4 (--export=NONE reversal; Codex's inherited BASH_ENV): the scripts re-execute under env -i with a named
        list, so an inherited variable never reaches the setup or its children; a pre-set marker with extra variables
        refuses."""
        (self.tmp / "cwd").mkdir()
        _, _, sha = self.deploy()
        hook = self.tmp / "hook.sh"
        hook.write_text(f"echo sourced >> {self.tmp / 'bash_env_ran'}\n")
        r = self.run_smoke(self.tmp / "stage", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha, FOO_INHERITED="x",
                           BASH_ENV=str(hook), GIT_DIR="/nowhere", PYTHONPYCACHEPREFIX=str(self.tmp / "pyc"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        dump = [ln[9:] for ln in (self.tmp / "stage" / "smoke-env.log").read_text().splitlines()
                if ln.startswith("ENV-DUMP ")]
        names = {ln.split("=", 1)[0] for ln in dump}
        self.assertTrue({"STUB_SETUP", "STUB_NESTED", "PFBCLEAN"} <= names, names)
        for v in ("FOO_INHERITED", "BASH_ENV", "GIT_DIR", "PYTHONPYCACHEPREFIX"):
            self.assertNotIn(v, names, "an inherited variable reached the setup")
        self.assertEqual((self.tmp / "bash_env_ran").read_text().count("sourced"), 1,
                         "BASH_ENV runs only in the outer bash the test starts, never after the re-exec")
        self.assertFalse((self.tmp / "pyc").exists())
        r = self.run_smoke(self.tmp / "stage2", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha, PFBCLEAN="1", FOO_INHERITED="x",
                           LC_ALL="C", PYTHONDONTWRITEBYTECODE="1", **self.DECLARED_PY_GIT)
        self.assertEqual(r.returncode, 2)
        self.assertIn("[pfb] refusing: the environment holds ", r.stderr)
        for f in ("sbatch_pfb.sh", "pfb_smoke_prep.sh"):
            text = (ND / f).read_text()
            block = text[text.index("# --- the environment:"):text.index("# --- end of the environment block ---")]
            self.assertIn('exec /usr/bin/env -i "${keep[@]}" /bin/bash --noprofile --norc "$0" "$@"', block)
            if f == "sbatch_pfb.sh":
                self.assertIn("#SBATCH --export=NIL\n", text)
                self.assertNotIn("--export=ALL", text)
        blocks = [(ND / f).read_text() for f in ("sbatch_pfb.sh", "pfb_smoke_prep.sh")]
        cut = [t[t.index("# --- the environment:"):t.index("# --- end of the environment block ---")] for t in blocks]
        self.assertEqual(cut[0], cut[1], "the job and the smoke share one environment block")


class Rev4(Rev3):
    """The code-3 confirmation audits (Codex FAIL, Grok PASS WITH FIXES) and the director's code-4 rulings. It reuses
    Rev3's fixtures; Rev3's own tests run once, in Rev3 (they are removed from this class below)."""

    def test_a_symlinked_a0_directory_or_the_original_inode_fails_g4(self):
        """Codex 2, Grok 1: every path component is checked physically, and a copy that is the protected original's
        inode fails."""
        import os
        c = self.run_tree()
        refs = c["stage"] / "a0-refs"
        moved = self.tmp / "rs1-originals"
        os.replace(refs, moved)
        refs.symlink_to(moved)
        out = self.analyze()
        self.assertEqual(out["outcome"]["outcome"], "INPUTS CHANGED")
        self.assertTrue(any("a path component is a symlink" in x for x in out["gates"]["G4_failing"]), out["gates"])
        refs.unlink()
        os.replace(moved, refs)
        g4 = A.g4_failing(c["stage"], c["deploy"], c["pin"], rs1_sums=self.tmp / "sums", check_inputs=False,
                          a0_originals=refs)
        self.assertEqual(len([x for x in g4 if "the protected original itself" in x]), 21, g4)
        self.assertEqual(A.g4_failing(c["stage"], c["deploy"], c["pin"], rs1_sums=self.tmp / "sums", check_inputs=False,
                                      a0_originals=self.tmp / "nowhere"), [])

    def test_the_root_read_is_the_statuss_root(self):
        """Codex 3: a copied tree read under another path fails, even when its status names the declared root."""
        import shutil
        c = self.run_tree()
        other = self.tmp / "copy-of-root"
        shutil.copytree(c["root"], other)
        st = {"job": self.JOB, "pin": c["pin"], "root": str(c["root"])}
        with self.assertRaisesRegex(SystemExit, "the root read"):
            A.analyze(other, c["stage"], st, self.JOB, c["deploy"], c["pin"], U=np.eye(169), check_inputs=False,
                      root_declared=str(c["root"]))

    def test_null_hashes_missing_files_and_a_bad_index_fail(self):
        """Codex 4: a recorded sha256 that is not a sha256 (null) with its file missing, an INDEX without its schema,
        and a file name outside the declared pattern all fail."""
        c = self.run_tree()
        e = c["root"] / "edges"
        idx = json.loads((e / "INDEX.json").read_text())
        for s_ in A.SETS:
            for r in A.ROLES:
                idx["sets"][s_]["roles"][r]["sha256"] = None
                (e / f"{s_}_{r}.json").unlink()
        (e / "INDEX.json").write_text(json.dumps(idx))
        sha, bad = A.edges_problems(e)
        self.assertEqual(len(bad), 12, bad)
        self.assertTrue(all("is not a sha256" in b for b in bad))
        idx2 = dict(idx)
        idx2.pop("schema")
        (e / "INDEX.json").write_text(json.dumps(idx2))
        self.assertTrue(any("schema" in b for b in A.edges_problems(e)[1]))
        idx["sets"]["E1"]["roles"]["reg"]["file"] = "../../elsewhere.json"
        (e / "INDEX.json").write_text(json.dumps(idx))
        self.assertTrue(any("names the file '../../elsewhere.json'" in b for b in A.edges_problems(e)[1]))

    def test_wrong_typed_meta_keeps_the_named_outcome(self):
        """Codex 5: a readable product whose meta is valid JSON of the wrong type is classified, and a missing
        display-only RS1 readout never removes the statistics."""
        c = self.run_tree()
        q = c["root"] / A.expected()[("E1", 7)]
        np.savez(q, xsec_flat=np.full(169, 2.0), meta=np.array("[]"))
        out = self.analyze()
        self.assertEqual(out["outcome"]["outcome"], "INCOMPLETE")
        self.assertIn("not an object", out["outcome"]["why"])
        self._t.cleanup(); self.setUp()
        c = self.run_tree()
        q = c["root"] / A.expected()[("E2", None)]
        z = dict(np.load(q))
        m = json.loads(str(z["meta"]))
        m["pilot_fb"] = ["not", "an", "object"]
        np.savez(q, xsec_flat=z["xsec_flat"], meta=np.array(json.dumps(m)))
        import hashlib
        side = q.with_name(q.name[:-4] + ".pfb.json")  # the sidecar names the new product, so only the type is wrong
        sd = json.loads(side.read_text())
        sd["product_sha256"] = hashlib.sha256(q.read_bytes()).hexdigest()
        side.write_text(json.dumps(sd))
        out = self.analyze()
        self.assertEqual(out["outcome"]["outcome"], "PREMISE FAILED (identity)")
        self.assertIn("not a JSON object", out["outcome"]["why"])
        self._t.cleanup(); self.setUp()
        self.run_tree()
        import unittest.mock as um
        with um.patch.object(A, "RS1_READ", self.tmp / "absent.json"):
            out = self.analyze()
        self.assertIn("row", out["outcome"])
        self.assertIn("readouts_rs1_A0_pair_statistic_unreadable", out["statistics"])
        self.assertIn("S3", out["statistics"])

    def test_the_analysis_writes_only_a_new_file_under_the_stage_or_root(self):
        """The director's ruling: the analyzer's --out is constrained in code, and created new."""
        import os
        stage, root = self.tmp / "stage", self.tmp / "root"
        stage.mkdir()
        root.mkdir()
        self.assertIsNone(A.out_problem(stage / "analysis.json", stage, root))
        self.assertIsNone(A.out_problem(root / "logs" / "a.json", stage, root))
        self.assertIn("is not under", A.out_problem(self.tmp / "elsewhere.json", stage, root))
        (stage / "link").symlink_to(self.tmp)
        self.assertIn("is not under", A.out_problem(stage / "link" / "x.json", stage, root))
        (stage / "dangling.json").symlink_to(self.tmp / "nothing-there.json")
        self.assertIn("refusing to overwrite", A.out_problem(stage / "dangling.json", stage, root))
        victim = self.tmp / "v.json"
        victim.write_text("v")
        os.link(victim, stage / "hard.json")
        self.assertIn("refusing to overwrite", A.out_problem(stage / "hard.json", stage, root))
        with self.assertRaises(FileExistsError):
            A.write_new(stage / "dangling.json", "x")
        self.assertFalse((self.tmp / "nothing-there.json").exists())

    def test_the_stage_inventory(self):
        """The job's stage-check: only the smoke's files, the copies and the jobs' own logs; no link anywhere."""
        import os
        stage, _ = self.staged()
        self.assertEqual(A.stage_problems(stage), [])
        (stage / "slurm-61500000.out").write_text("log")
        (stage / "job-61500000.refused.json").write_text("{}")
        self.assertEqual(A.stage_problems(stage), [])
        (stage / "a0-refs" / "extra.npz").write_text("x")
        self.assertTrue(any("extra ['extra.npz']" in b for b in A.stage_problems(stage)))
        (stage / "a0-refs" / "extra.npz").unlink()
        os.link(stage / A.SIGMA_NAME, self.tmp / "outside")
        self.assertTrue(any("a hard link" in b for b in A.stage_problems(stage)))
        (self.tmp / "outside").unlink()
        (stage / "slurm-61500001.err").symlink_to(self.tmp / "victim")
        self.assertTrue(any("slurm-61500001.err: a symlink" in b for b in A.stage_problems(stage)))



class Rev5(Rev3):
    """The code-4 confirmation audits and the director's code-5 rulings: values as well as names, a clean first shell,
    a post-setup check, a typed status, and INDEX's policy fields."""

    def raw_smoke(self, stage, env, argv0=None):
        import subprocess
        d, pin, _ = self.deploy()
        cmd = [argv0] if argv0 else ["/bin/bash", str(ND / "pfb_smoke_prep.sh")]
        return subprocess.run(cmd + [str(d), pin, str(stage)], env=env, capture_output=True, text=True,
                              cwd=self.tmp / "cwd")

    def test_the_environment_values_are_checked_whatever_the_marker(self):
        """Codex: a forged PFBCLEAN with a foreign PATH, HOME or bytecode setting was accepted; now every value is."""
        (self.tmp / "cwd").mkdir()
        _, _, sha = self.deploy()
        base = {"PFBCLEAN": "1", "LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1", "HOME": "/global/homes/j/josephrb",
                "USER": "josephrb", "LOGNAME": "josephrb", "SCRATCH": "/pscratch/sd/j/josephrb", **self.DECLARED_PY_GIT}
        r = self.raw_smoke(A.STAGE_DECLARED, {**base, "PATH": "/nondeclared/bin"})
        self.assertEqual(r.returncode, 2)
        self.assertIn("PATH is '/nondeclared/bin', not the declared '/usr/bin:/bin'", r.stderr)
        r = self.raw_smoke(A.STAGE_DECLARED, {**base, "PATH": "/usr/bin:/bin", "HOME": "/nondeclared/home"})
        self.assertIn("HOME is '/nondeclared/home'", r.stderr)
        loc = {"PFBCLEAN": "1", "LC_ALL": "C", "PFB_LOCAL_TEST": "1", "PFB_SETUP_SHA": sha, "HOME": str(self.tmp),
               "PATH": f"{Path(sys.executable).parent}:/usr/bin:/bin", **self.DECLARED_PY_GIT}
        r = self.raw_smoke(self.tmp / "s1", {**loc, "PYTHONDONTWRITEBYTECODE": "0"})
        self.assertIn("PYTHONDONTWRITEBYTECODE is '0', not the declared '1'", r.stderr)
        r = self.raw_smoke(self.tmp / "s2", loc)
        self.assertIn("PYTHONDONTWRITEBYTECODE is '<unset>'", r.stderr)
        self.assertFalse((self.tmp / "s1").exists() or (self.tmp / "s2").exists())

    def test_the_setup_may_not_export_a_denied_variable(self):
        """The director's ruling: the environment is checked again after the setup."""
        (self.tmp / "cwd").mkdir()
        _, _, sha = self.deploy()
        self.deny_flag.write_text("")
        r = self.run_smoke(self.tmp / "stage", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("the setup exported PYTHONSTARTUP, which is denied", r.stderr)
        self.assertIn("returned 97", r.stderr)
        self.assertFalse((self.tmp / "stage" / "smoke-receipt.json").exists())

    def test_the_first_shell_starts_clean(self):
        """The director's ruling (Codex, Grok): BASH_ENV never runs in the first shell. Both scripts' shebang is
        `env -S -u BASH_ENV -u ENV /bin/bash --noprofile --norc`, and the reviewed smoke launch is env -i."""
        import os
        import shutil
        import subprocess
        (self.tmp / "cwd").mkdir()
        d, pin, sha = self.deploy()
        hook = self.tmp / "hook.sh"
        ran = self.tmp / "bash_env_ran"
        hook.write_text(f"echo ran >> {ran}\n")
        exe = self.tmp / "pfb_smoke_prep.sh"
        shutil.copy(ND / "pfb_smoke_prep.sh", exe)
        exe.chmod(0o755)
        r = self.raw_smoke(self.tmp / "stage", self.env(PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha, BASH_ENV=str(hook),
                                                        ENV=str(hook)), argv0=str(exe))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(ran.exists(), "BASH_ENV ran before the script's first line")
        job = self.tmp / "sbatch_pfb.sh"
        shutil.copy(ND / "sbatch_pfb.sh", job)
        job.chmod(0o755)
        r = subprocess.run([str(job), str(d), pin, str(self.tmp / "nostage"), str(self.tmp / "root")],
                           env=self.env(PFB_LOCAL_TEST="1", BASH_ENV=str(hook)), capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(ran.exists(), "BASH_ENV ran in the job's first shell")
        for f in ("sbatch_pfb.sh", "pfb_smoke_prep.sh"):
            self.assertTrue((ND / f).read_text().startswith(
                "#!/usr/bin/env -S -u BASH_ENV -u ENV /bin/bash --noprofile --norc\n"), f)
        launch = ('[ -z "${SLURM_JOB_ID-}" ] && /usr/bin/env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin '
                  "/bin/bash --noprofile --norc <deploy>/nd-unfolding/pfb_smoke_prep.sh")
        self.assertIn(launch, (ND / "pfb_smoke_prep.sh").read_text())
        r = subprocess.run(["/usr/bin/env", "-i", f"HOME={self.tmp}",
                            f"PATH={Path(sys.executable).parent}:/usr/bin:/bin:/usr/sbin:/sbin",
                            "PFB_LOCAL_TEST=1", f"PFB_SETUP_SHA={sha}", "/bin/bash", "--noprofile", "--norc",
                            str(ND / "pfb_smoke_prep.sh"), str(d), pin, str(self.tmp / "stage2")],
                           capture_output=True, text=True, cwd=self.tmp / "cwd")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.isfile(self.tmp / "stage2" / "smoke-receipt.json"))

    def test_a_status_of_the_wrong_type_is_classified(self):
        """Codex 4: a status that is valid JSON of another type refuses with its reason, never an AttributeError."""
        c = self.run_tree()
        self.assertIn("not an object", A.status_problem([], self.JOB, c["pin"], None, c["root"], c["stage"]))
        with self.assertRaisesRegex(SystemExit, "the job status is a JSON list, not an object"):
            self.analyze([])

    def test_the_index_policy_fields(self):
        """Codex 4: INDEX's K, and each set's max_bin and offset, must be the declared ones."""
        c = self.run_tree()
        e = c["root"] / "edges"
        self.assertEqual(A.edges_problems(e)[1], [])
        idx = json.loads((e / "INDEX.json").read_text())
        for edit, why in ((lambda i: i.update(K=1e-35), "K is"), (lambda i: i.pop("K"), "K is None"),
                          (lambda i: i["sets"]["E3"].update(max_bin=255), "E3's max_bin is 255"),
                          (lambda i: i["sets"]["E2"].update(offset=0.0), "E2's offset is 0.0")):
            j = json.loads(json.dumps(idx))
            edit(j)
            (e / "INDEX.json").write_text(json.dumps(j))
            self.assertTrue(any(why in b for b in A.edges_problems(e)[1]), (why, A.edges_problems(e)[1]))


class Rev6(Rev3):
    """The code-5 confirmation read and the director's code-6 rulings F1-F6."""

    def sbatch_stub(self, version: str, help_text: str, vrc: int = 0, hrc: int = 0) -> Path:
        """A stub sbatch that answers --version and --help only; any other invocation (a submission) fails loudly and
        leaves a marker."""
        b = self.tmp / "sbin"
        b.mkdir(exist_ok=True)
        (b / "sbatch").write_text(
            f"#!/bin/sh\ncase \"$1\" in\n  --version) printf '%s\\n' '{version}'; exit {vrc} ;;\n"
            f"  --help) printf '%s\\n' '{help_text}'; exit {hrc} ;;\n"
            f"  *) echo \"stub sbatch: unexpected invocation $*\" >&2; echo \"$*\" >> {self.tmp / 'sbatch_submitted'}; exit 99 ;;\nesac\n")
        (b / "sbatch").chmod(0o755)
        return b

    def test_the_job_requires_export_nil(self):
        """F1: --export=NIL (no --get-user-env login environment); the job accepts only that mode."""
        text = (ND / "sbatch_pfb.sh").read_text()
        self.assertIn("#SBATCH --export=NIL\n", text)
        self.assertNotIn("--export=NONE\n", text)
        slurm = {"SLURM_JOB_ID": "77", "SLURM_JOB_NUM_NODES": "1", "SLURM_JOB_NAME": "pfb_run"}
        r = self.run_job(A.STAGE_DECLARED, A.ROOT_DECLARED, **slurm)
        self.assertIn("export mode is '<unset>', not the approved NIL", r.stderr)
        r = self.run_job(A.STAGE_DECLARED, A.ROOT_DECLARED, SLURM_EXPORT_ENV="NIL", **slurm)
        self.assertNotIn("export mode", r.stderr)

    def test_the_smoke_confirms_nil_without_submitting(self):
        """F1: the smoke records sbatch --version and --help and accepts NIL if the help names it or the version is at
        least 23.02.3; otherwise it stops with exit 8."""
        (self.tmp / "cwd").mkdir()
        _, _, sha = self.deploy()
        path = lambda b: f"{b}:{Path(sys.executable).parent}:/usr/bin:/bin:/usr/sbin:/sbin"  # noqa: E731
        r = self.run_smoke(self.tmp / "s1", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha,
                           PATH=path(self.sbatch_stub("slurm 24.05.4", "--export=names")))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rec = (self.tmp / "s1" / "smoke-sbatch.txt").read_text()
        self.assertIn("slurm 24.05.4", rec)
        self.assertIn("NIL accepted: sbatch --version 24.05.4 is at least 23.02.3", rec)
        self.assertFalse((self.tmp / "sbatch_submitted").exists(), "the smoke never submits")
        r = self.run_smoke(self.tmp / "s2", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha,
                           PATH=path(self.sbatch_stub("slurm 23.02.2", "--export=names")))
        self.assertEqual(r.returncode, 8, r.stderr)
        self.assertIn("STOP: no positive evidence that this sbatch supports --export=NIL", r.stderr)
        self.assertFalse((self.tmp / "s2" / "smoke-receipt.json").exists())
        r = self.run_smoke(self.tmp / "s3", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha,
                           PATH=path(self.sbatch_stub("slurm 23.02.2", "--export=names|ALL|NIL|NONE")))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NIL accepted: sbatch --help's --export line names NIL", (self.tmp / "s3" / "smoke-sbatch.txt").read_text())
        (self.tmp / "s3" / "a0-refs").mkdir()
        for s_ in (None, *A.SEEDS):
            (self.tmp / "s3" / "a0-refs" / A.name("rs1_A0", s_)).write_bytes(b"a0")
        (self.tmp / "s3" / A.SIGMA_NAME).write_text("{}")
        self.assertEqual(A.stage_problems(self.tmp / "s3"), [], "the stage inventory admits the sbatch record")

    def test_the_documented_smoke_launch_refuses_inside_an_allocation(self):
        """F2: the reviewed launch line itself, not a direct bash call: inside an allocation it refuses before the
        environment is cleared, so the script never runs."""
        import subprocess
        d, pin, _ = self.deploy()
        line = next(ln[1:].strip() for ln in (ND / "pfb_smoke_prep.sh").read_text().splitlines()
                    if "pfb_smoke_prep.sh <deploy> <pin>" in ln and ln.startswith("#   "))
        cmd = line.replace("<deploy>/nd-unfolding/pfb_smoke_prep.sh", str(ND / "pfb_smoke_prep.sh")) \
            .replace("<deploy>", str(d)).replace("<pin>", pin)
        r = subprocess.run(["/bin/bash", "-c", cmd], env={"SLURM_JOB_ID": "5", "PATH": "/usr/bin:/bin"},
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("[pfb", r.stderr, "the smoke never started inside an allocation")
        r = subprocess.run(["/bin/bash", "-c", cmd], env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True)
        self.assertIn("[pfb-smoke] refusing", r.stderr, "outside an allocation the documented line runs the smoke")

    def test_user_site_and_git_config_are_off(self):
        """F3: PYTHONNOUSERSITE=1 and git's system/global config off are declared values, checked; G4's git runs with
        fsmonitor off; LightGBM must resolve under the declared prefix."""
        import unittest.mock as um
        (self.tmp / "cwd").mkdir()
        _, _, sha = self.deploy()
        r = self.run_smoke(self.tmp / "stage", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha)
        self.assertEqual(r.returncode, 0, r.stderr)
        dump = (self.tmp / "stage" / "smoke-env.log").read_text()
        for want in ("ENV-DUMP PYTHONNOUSERSITE=1", "ENV-DUMP GIT_CONFIG_NOSYSTEM=1", "ENV-DUMP GIT_CONFIG_GLOBAL=/dev/null"):
            self.assertIn(want, dump)
        loc = {"PFBCLEAN": "1", "LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1", "PFB_LOCAL_TEST": "1", "HOME": str(self.tmp),
               "PATH": f"{Path(sys.executable).parent}:/usr/bin:/bin", **self.DECLARED_PY_GIT}
        for k, bad in (("PYTHONNOUSERSITE", "0"), ("GIT_CONFIG_GLOBAL", str(self.tmp / ".gitconfig"))):
            import subprocess
            r = subprocess.run(["/bin/bash", str(ND / "pfb_smoke_prep.sh"), "/x", "0" * 40, str(self.tmp / "s9")],
                               env={**loc, k: bad}, capture_output=True, text=True)
            self.assertIn(f"{k} is '{bad}'", r.stderr)
        seen = []
        real = A.subprocess.run

        def spy(cmd, **kw):
            seen.append((list(cmd), kw.get("env", {})))
            return real(cmd, **kw)

        d, pin, _ = self.deploy()
        with um.patch.object(A.subprocess, "run", spy):
            self.assertIsNone(A.deploy_problem(d, pin))
        self.assertTrue(seen and all(c[:3] == ["git", "-c", "core.fsmonitor=false"] for c, _ in seen), seen)
        self.assertTrue(all(e.get("GIT_CONFIG_NOSYSTEM") == "1" and e.get("GIT_CONFIG_GLOBAL") == "/dev/null"
                            for _, e in seen))
        pre = self.tmp / "envs" / "root_6_28"
        (pre / "lib").mkdir(parents=True)
        self.assertIsNone(A.module_problem(str(pre / "lib" / "lightgbm" / "__init__.py"), str(pre)))
        self.assertIn("not under", A.module_problem(str(self.tmp / ".local" / "lightgbm" / "__init__.py"), str(pre)))
        self.assertIn("not under", A.module_problem(str(self.tmp / "envs" / "root_6_28x" / "lgb.py"), str(pre)))
        text = (ND / "sbatch_pfb.sh").read_text()
        self.assertIn('python3 fb_pilot_analyze.py lgbm-check --prefix "$LGBM_PREFIX"', text)

    def test_the_setup_values_are_reproduced_before_any_setup_tool(self):
        """F4: the values the setup leaves (PATH, PYTHONPATH, LD_*, CONDA_*, git config) are the smoke's, compared before
        the live limit, the stage check or the receipt check run anything the setup selected."""
        stage, sha = self.staged()
        self.assertIn("PATH exported ", (stage / "smoke-setup-env.txt").read_text())
        self.assertIn("PYTHONNOUSERSITE exported 1", (stage / "smoke-setup-env.txt").read_text())
        self.path_flag.write_text("")
        (stage / "extra").symlink_to(self.tmp / "deploy")  # a stage-check failure too: the value check must come first
        r = self.run_job(stage, self.tmp / "root", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha)
        self.assertEqual(r.returncode, 2, r.stderr)
        rec = json.loads((stage / "job-local.refused.json").read_text())["preflight_refused"]
        self.assertIn("environment values", rec)
        self.assertFalse((self.tmp / "root").exists())

    def test_boolean_policy_fields_fail(self):
        """F5: a JSON false for an offset of 0.0, or true for K, is not the declared number."""
        c = self.run_tree()
        e = c["root"] / "edges"
        idx = json.loads((e / "INDEX.json").read_text())
        for edit, why in ((lambda i: i["sets"]["E1"].update(offset=False), "E1's offset is False"),
                          (lambda i: i["sets"]["E3"].update(max_bin=127.0), "E3's max_bin is 127.0"),
                          (lambda i: i.update(K=True), "K is True")):
            j = json.loads(json.dumps(idx))
            edit(j)
            (e / "INDEX.json").write_text(json.dumps(j))
            self.assertTrue(any(why in b for b in A.edges_problems(e)[1]), (why, A.edges_problems(e)[1]))

    def test_j2_rebuilds_the_jitter_from_the_jittered_sources(self):
        """F6: in a run, J2's rebuilt selection is build_pseudo on the jittered inputs and background, with the run's
        own truth, amplitude, split key, pseudo-seed and ratio (fb_pilot_probe.py, the jitter rebuild)."""
        import unittest.mock as um
        rng = np.random.default_rng(3)
        good = np.column_stack([f32(np.round(rng.normal(3, 1, 3000), 3)) for _ in range(5)])
        edges = self.tmp / "edges"
        E.build_edges({r: (good, None) for r in E.ROLES}, edges)
        exp = J().exp(np.random.default_rng(5))
        base = {k: f32(np.round(np.random.default_rng(7).normal(2, 1, (50, 5)), 2)) for k in P.SOURCES}
        inputs = {**base, "edges": [np.array([-50.0, 50.0])] * 5}
        bkg = {"bkg_reco": f32(np.round(np.random.default_rng(8).normal(2, 1, (20, 5)), 2))}
        ji = {k: v + 1e-3 for k, v in base.items()}
        jb = {"bkg_reco": bkg["bkg_reco"] + 1e-3}
        calls = []

        def fake_build(i, b, truth, amplitude, split_key, seed, ratio):
            calls.append((i, b, truth, amplitude, split_key, seed, ratio))
            return (exp,)

        ns = type("NS", (), {"truth": "eavail_shape", "amplitude": 1.0, "pseudo_seed": 990000,
                             "eavail_ratio": str(ND.parent / P.rmp.STABILITY["ratio"])})()
        with um.patch.object(P.s5p_numerics, "jittered", lambda i, b, j: (ji, jb)), \
                um.patch.object(P.s5p_numerics, "unfold_one", lambda *a, **k: "unfolded"), \
                um.patch.object(P.s5n_pseudo, "build_pseudo", fake_build):
            with P.install("run", "E1", edges) as st:
                st.update(ns=ns, seed=3, inputs=inputs, bkg=bkg, sources=(ji, jb))
                self.assertEqual(P.s5p_numerics.unfold_one({}, np.float64, 42, 32, 5), "unfolded")
        self.assertEqual(len(calls), 2, "the base rebuild, then the jitter rebuild")
        i, b, truth, amplitude, split_key, seed, ratio = calls[1]
        self.assertIs(i, ji, "the jitter rebuild reads the jittered inputs")
        self.assertIs(b, jb, "and the jittered background")
        self.assertEqual((truth, amplitude, seed), ("eavail_shape", 1.0, 990000))
        self.assertEqual(split_key, P.s5c_pseudo.split_key_for(990000))
        self.assertIsInstance(ratio, dict)
        self.assertIs(calls[0][0], inputs, "the base rebuild reads the unjittered inputs")
        self.assertEqual(st["j"]["j1"], [], "the sources the run used are the jittered ones it recorded")


def shell_function(name: str, script: str = "sbatch_pfb.sh") -> str:
    """One function's source from the shared environment block, as the script defines it."""
    text = (ND / script).read_text()
    i = text.index(f"\n{name}() {{") + 1
    return text[i:text.index("\n}\n", i) + 3]


class Rev7(Rev6):
    """The code-6 scoped read and the director's code-7 items G1-G3."""

    def test_nil_needs_positive_evidence(self):
        """G1: NIL only from a version probe that exits 0 and parses to at least 23.02.3, or from a help probe that exits
        0 with NIL on the --export line itself; anything else stops (exit 8), and nothing is ever submitted."""
        (self.tmp / "cwd").mkdir()
        _, _, sha = self.deploy()
        path = lambda b: f"{b}:{Path(sys.executable).parent}:/usr/bin:/bin:/usr/sbin:/sbin"  # noqa: E731
        cases = (("slurm 24.05.4", "error: NIL is unsupported", 1, 1, "a failing version probe"),
                 ("error: --export=NIL unknown", "error: NIL", 1, 2, "both probes fail, each naming NIL"),
                 ("slurm-wlm unknown", "--export=names", 0, 0, "a version line that will not parse"),
                 ("slurm 22.05.9", "--export=names\nsee NIL in the manual", 0, 0, "NIL outside the --export line"),
                 ("slurm 22.05.9", "--export=names|NIL", 0, 3, "a help probe that exits nonzero"))
        for k, (ver, hlp, vrc, hrc, why) in enumerate(cases):
            st = self.tmp / f"n{k}"
            r = self.run_smoke(st, PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha, PATH=path(self.sbatch_stub(ver, hlp, vrc, hrc)))
            self.assertEqual(r.returncode, 8, (why, r.stderr))
            self.assertFalse((st / "smoke-receipt.json").exists(), why)
        r = self.run_smoke(self.tmp / "ok", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha,
                           PATH=path(self.sbatch_stub("slurm 22.05.9", "  --export=names|ALL|NIL|NONE  environment")))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.tmp / "sbatch_submitted").exists(), "no probe ever submits")

    def test_the_snapshot_is_unambiguous(self):
        """G2 (a): one record per name, with its export status and its value under printf %q, so a newline cannot move
        a fragment from one variable to the next and reproduce another snapshot."""
        import subprocess
        fn = shell_function("setup_env_text")

        def snap(assign):
            r = subprocess.run(["/bin/bash", "--noprofile", "--norc", "-c", f"{fn}\n{assign}\nsetup_env_text"],
                               env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True)
            return r.stdout
        a = snap("export CONDA_PREFIX=\"$(printf 'p\\nCONDARC=q')\" CONDARC=r")
        b = snap("export CONDA_PREFIX=p CONDARC=\"$(printf 'q\\nCONDARC=r')\"")
        self.assertNotEqual(a, b, "the newline-shift probe")
        self.assertEqual(len(a.splitlines()), len(b.splitlines()), "one record per name")
        self.assertIn("CONDARC unset", snap("export CONDA_PREFIX=p"))
        self.assertIn("CONDARC set r", snap("CONDARC=r"), "set but not exported")
        self.assertIn("CONDARC exported r", snap("export CONDARC=r"))
        self.assertIn("GIT_CONFIG_COUNT exported 1", snap("export GIT_CONFIG_COUNT=1"))

    def test_the_newline_shift_refuses_at_the_job(self):
        """G2 (a), end to end: the smoke ran with one split, the job sees the other; the job refuses."""
        self.deploy()
        self.nl_a.write_text("")
        stage, sha = self.staged()
        self.nl_a.unlink()
        self.nl_b.write_text("")
        r = self.run_job(stage, self.tmp / "root", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("environment values", json.loads((stage / "job-local.refused.json").read_text())["preflight_refused"])

    def test_a_null_setup_digest_refuses(self):
        """G2 (b): the setup environment's digest is a required sha256 in the receipt writer and the checker."""
        stage, sha = self.staged()
        rec = json.loads((stage / "smoke-receipt.json").read_text())
        self.assertRegex(rec["setup_env_sha256"], "^[0-9a-f]{64}$")
        why = A.smoke_receipt_problem(dict(rec, setup_env_sha256=None), stage, self.pin, True, rec["setup_closure"],
                                      rec["post_setup_env"])
        self.assertIn("is not a sha256", why)
        (stage / "smoke-setup-env.txt").unlink()
        why = A.smoke_receipt_problem(dict(rec, setup_env_sha256=None), stage, self.pin, True, rec["setup_closure"],
                                      rec["post_setup_env"])
        self.assertIn("is not a sha256", why, "a missing file and a null digest do not match each other")
        (stage / "smoke-receipt.json").unlink()
        tr = stage / "smoke-env.log"
        rc = A.smoke_main(["write", "--stage", str(stage), "--pin", self.pin, "--local", "true", "--trace", str(tr)])
        self.assertEqual(rc, 9, "the writer refuses without the setup environment file")
        self.assertFalse((stage / "smoke-receipt.json").exists())

    def test_a_mismatch_refusal_never_runs_the_setups_python(self):
        """G2 (c): the setup now puts a python3 first on PATH; the values differ from the smoke's, and the refusal is
        written without ever running that python3."""
        stage, sha = self.staged()
        stub = self.tmp / "pystub"
        stub.mkdir()
        (stub / "python3").write_text(f"#!/bin/sh\necho ran >> {self.tmp / 'stub_python_ran'}\nexit 3\n")
        (stub / "python3").chmod(0o755)
        self.py_flag.write_text("")
        r = self.run_job(stage, self.tmp / "root", PFB_LOCAL_TEST="1", PFB_SETUP_SHA=sha)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("environment values", json.loads((stage / "job-local.refused.json").read_text())["preflight_refused"])
        self.assertFalse((self.tmp / "stub_python_ran").exists(), "the setup-selected python3 never ran")

    def test_the_declared_values_are_restored_before_the_denied_check(self):
        """G3 (code 6's regression): a setup that clears the bytecode setting and exports a denied variable is refused
        with the declared values already restored."""
        import subprocess
        d = self.tmp / "g3"
        d.mkdir()
        (d / "setup_salloc_env.sh").write_text("unset PYTHONDONTWRITEBYTECODE PYTHONNOUSERSITE\nexport PYTHONSTARTUP=/nowhere\n")
        body = (f"{shell_function('traced_setup')}\nD={d}\nexport PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1\n"
                f"traced_setup {d / 'log'}\necho \"rc=$? b=${{PYTHONDONTWRITEBYTECODE-unset}} u=${{PYTHONNOUSERSITE-unset}}\"\n")
        r = subprocess.run(["/bin/bash", "--noprofile", "--norc", "-c", body], env={"PATH": "/usr/bin:/bin"},
                           capture_output=True, text=True)
        self.assertIn("rc=97 b=1 u=1", r.stdout, r.stdout + r.stderr)


for _cls in (Rev4, Rev5, Rev6, Rev7):
    for _n in [n for n in vars(Rev3) if n.startswith("test_")]:
        setattr(_cls, _n, None)  # not collected twice: unittest collects only callable test_ attributes
for _n in [n for n in vars(Rev6) if n.startswith("test_")]:
    setattr(Rev7, _n, None)
del _cls, _n  # a module-level alias of a TestCase class would be collected again (code 5's count)


if __name__ == "__main__":
    unittest.main()
