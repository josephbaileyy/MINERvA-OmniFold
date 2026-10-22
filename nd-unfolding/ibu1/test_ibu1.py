#!/usr/bin/env python3
"""Synthetic controls for ``ibu1.py`` and ``ibu1_read.py``: each mechanism fires on its defect and is
silent on the clean case. The world uses the real 5D grid, the real J partition and the real functional
rows; the events are synthetic, so nothing here reads an analysis input."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ibu1  # noqa: E402
import ibu1_read as rd  # noqa: E402

CFG = json.loads(ibu1.CONFIG.read_text())
PROD = ibu1.Producers(CFG)
CONTRACT = json.loads((ibu1.REPO / CFG["contract"]["path"]).read_text())
import project_cov_nd as pc  # noqa: E402  (after Producers put nd-unfolding on sys.path)
import s5c_coverage  # noqa: E402

EDGES = [np.asarray(pc.AXIS_EDGES[a], float) for a in ("pt", "pz", "eavail", "q3", "W")]
SHAPE = tuple(len(e) - 1 for e in EDGES)


def synthetic_inputs(n=60_000, seed=0, sentinels=40, edge_rows=10):
    rng = np.random.default_rng(seed)
    lo = np.array([0.1, 2.1, 0.05, 0.1, 0.5])
    hi = np.array([1.4, 9.0, 2.5, 1.9, 2.9])
    gen = (lo + (hi - lo) * rng.random((n, 5))).astype(np.float32)
    reco = (gen * (1 + 0.08 * rng.standard_normal((n, 5)))).astype(np.float32)
    gen[:sentinels, 4] = -9999.0  # out-of-grid truth, as the input sample's W sentinels
    reco[sentinels:sentinels + edge_rows, 0] = EDGES[0][-1]  # rows exactly on an upper reco edge
    gen[sentinels + edge_rows:sentinels + 2 * edge_rows, 1] = EDGES[1][-1]  # and on an upper truth edge
    pass_reco = rng.random(n) < 0.7
    w_truth = 0.05 * (1 + 0.2 * rng.random(n))
    w_reco = w_truth * (1 + 0.01 * rng.standard_normal(n))
    ofin, _ = np.histogramdd(gen.astype(float), bins=EDGES, weights=w_truth)
    cfac = 1.0 + 2.0 * np.random.default_rng(seed + 7).random(ofin.shape)  # completeness 0.33-1 per fine cell
    meas = reco[pass_reco][:5000]
    return {"MCgen": gen, "MCreco": reco, "pass_reco": pass_reco, "pass_truth": np.ones(n, bool),
            "w_truth": w_truth, "w_reco": w_reco, "measured": meas, "measured_weights": np.full(meas.shape[0], 0.97),
            "denom_nd": ofin * cfac, "flux": np.linspace(1.0, 2.0, SHAPE[0]), "data_pot": np.array(1e20),
            "n_nucleons": np.array(1e30), "nedges": np.array(5), "edges": EDGES}


def synthetic_bkg(n=4000, seed=1):
    rng = np.random.default_rng(seed)
    reco = np.column_stack([rng.uniform(0.1, 1.4, n), rng.uniform(2.1, 9, n), rng.uniform(0.05, 2.5, n),
                            rng.uniform(0.1, 1.9, n), rng.uniform(0.5, 2.9, n)]).astype(np.float32)
    w = np.full(n, 0.04)
    nd, _ = np.histogramdd(reco.astype(float), bins=EDGES, weights=w)
    return {"bkg_reco": reco, "bkg_w": w, "bkg_nd": nd}


INPUTS = synthetic_inputs()
BKG = synthetic_bkg()
WORLD = ibu1.World(PROD, INPUTS, CONTRACT, chunk=7_000)
KS = CFG["iterations"]["reported"]


def direct_functionals(half: ibu1.Half, r: np.ndarray | None = None) -> np.ndarray:
    """The functionals of the half's truth, reweighted by r, through the committed extraction with the
    half's unreweighted completeness (``s5c_pseudo.build_experiment``'s x_true spelling)."""
    m = INPUTS["pass_truth"][half.rows]
    samp = INPUTS["MCgen"][half.rows][m].astype(float)
    rw = np.ones(m.sum()) if r is None else r[half.rows][m]
    unf, _ = np.histogramdd(samp, bins=EDGES, weights=half.w_truth[m] * rw)
    ofin, _ = np.histogramdd(samp, bins=EDGES, weights=half.w_truth[m])
    dn = INPUTS["denom_nd"]
    comp = np.zeros_like(unf)
    comp[dn > 0] = ofin[dn > 0] / dn[dn > 0]
    xs, _ = PROD.xsec_nd.extract_cross_section_nd(unf, comp, INPUTS["flux"], 1e20, 1e30, EDGES)
    return WORLD.functionals(xs)


def expected_fold(half: ibu1.Half) -> np.ndarray:
    rows = half.rows[INPUTS["pass_reco"][half.rows]]
    w = half.w_reco[INPUTS["pass_reco"][half.rows]]
    return WORLD.reco_hist(INPUTS["MCreco"][rows], w)


class Grid(unittest.TestCase):
    def test_split_key_equals_producer(self):
        for s in (1, 4, 200000, 204000, 301000, 349999, 700000, 803000):
            self.assertEqual(ibu1.split_key_for(s), PROD.s5c_pseudo.split_key_for(s))

    def test_truth_cells_equal_histogramdd(self):
        """u_fine from flat_index equals the histogramdd s5c_unfold uses, upper-edge rows included."""
        h, _ = np.histogramdd(INPUTS["MCgen"].astype(float), bins=EDGES, weights=INPUTS["w_truth"])
        ok = WORLD.tflat >= 0
        u = np.bincount(WORLD.tflat[ok], weights=INPUTS["w_truth"][ok], minlength=WORLD.n_fine)
        np.testing.assert_allclose(u, h.ravel(), rtol=1e-13, atol=0)

    def test_reco_window_excludes_upper_edge(self):
        on_edge = INPUTS["MCreco"][:, 0] == EDGES[0][-1]
        self.assertTrue(on_edge.any())
        self.assertTrue(np.all(WORLD.rflat[on_edge] == -1))

    def test_functional_rows_are_the_contracts(self):
        U, names = s5c_coverage.reported_functionals(CONTRACT)
        self.assertEqual(names, WORLD.names)
        self.assertEqual(len(names), 153)
        self.assertEqual(sum(n.startswith("J") for n in names), 109)


class Closure(unittest.TestCase):
    def test_noise_free_same_sample_closes_at_every_K(self):
        """prior = truth and y = the expected fold: IBU's fixed point, so every K returns the truth."""
        half = ibu1.Half(np.arange(INPUTS["MCgen"].shape[0]), INPUTS["w_truth"], INPUTS["w_reco"])
        r = ibu1.unfold_ibu(WORLD, half, expected_fold(half), np.zeros(WORLD.n_fine), KS)
        want = direct_functionals(half)
        nz = np.abs(want) > 0
        for F in r["F"]:
            np.testing.assert_allclose(F[nz], want[nz], rtol=1e-10)

    def test_dropping_the_known_term_breaks_closure(self):
        half = ibu1.Half(np.arange(INPUTS["MCgen"].shape[0]), INPUTS["w_truth"], INPUTS["w_reco"])
        k = WORLD.known_rows
        self.assertGreater(k.size, 0)
        b = np.bincount(WORLD.rflat[k], weights=INPUTS["w_reco"][k], minlength=WORLD.n_fine)
        r = ibu1.unfold_ibu(WORLD, half, expected_fold(half), -b, [5])  # cancels the known term
        want = direct_functionals(half)
        nz = np.abs(want) > 0
        self.assertGreater(np.max(np.abs(r["F"][0][nz] / want[nz] - 1)), 1e-6)

    def test_background_in_the_fold_closes(self):
        half = ibu1.Half(np.arange(INPUTS["MCgen"].shape[0]), INPUTS["w_truth"], INPUTS["w_reco"])
        B = WORLD.reco_hist(BKG["bkg_reco"], BKG["bkg_w"])
        r = ibu1.unfold_ibu(WORLD, half, expected_fold(half) + B, B, [5, 20])
        want = direct_functionals(half)
        nz = np.abs(want) > 0
        np.testing.assert_allclose(r["F"][1][nz], want[nz], rtol=1e-10)

    def test_a_departure_is_partly_recovered(self):
        """A J-cell-constant truth reweight (a step on the J edge E_avail = 1.5, so no within-cell binning
        bias) folded into y: the K = 20 estimate is closer to the departed truth than K = 1 and the prior."""
        n = INPUTS["MCgen"].shape[0]
        half = ibu1.Half(np.arange(n), INPUTS["w_truth"], INPUTS["w_reco"])
        r = 1 + 0.3 * (INPUTS["MCgen"][:, 2] >= 1.5)
        dep = ibu1.Half(half.rows, INPUTS["w_truth"] * r, INPUTS["w_reco"] * r)
        res = ibu1.unfold_ibu(WORLD, half, expected_fold(dep), np.zeros(WORLD.n_fine), [1, 20])
        prior, truth = direct_functionals(half), direct_functionals(half, r)
        ok = np.abs(truth - prior) > 1e-3 * np.abs(prior)
        self.assertGreater(ok.sum(), 5)
        e1 = np.abs(res["F"][0][ok] - truth[ok]).sum()
        e20 = np.abs(res["F"][1][ok] - truth[ok]).sum()
        self.assertLess(e20, e1)
        self.assertLess(e20, np.abs(prior[ok] - truth[ok]).sum())


class Oracle(unittest.TestCase):
    def test_floor_is_zero_for_a_J_constant_departure(self):
        half = ibu1.Half(np.arange(INPUTS["MCgen"].shape[0]), INPUTS["w_truth"], INPUTS["w_reco"])
        r = 1 + 0.3 * (INPUTS["MCgen"][:, 2] >= 1.5)
        o, ref = ibu1.oracle_floor(WORLD, half, r)
        nz = np.abs(ref) > 0
        np.testing.assert_allclose(o[nz], ref[nz], rtol=1e-10)

    def test_floor_fires_inside_cells_with_varying_completeness(self):
        """Review finding 3: a departure that varies inside a J cell, with completeness varying across its
        fine cells, leaves a floor the J estimator cannot remove."""
        half = ibu1.Half(np.arange(INPUTS["MCgen"].shape[0]), INPUTS["w_truth"], INPUTS["w_reco"])
        r = 1 + 0.75 * (INPUTS["MCgen"][:, 2] - 1.25) / 1.25
        o, ref = ibu1.oracle_floor(WORLD, half, r)
        nz = np.abs(ref) > 0
        self.assertGreater(np.max(np.abs(o[nz] / ref[nz] - 1)), 1e-3)

    def test_truth_reweight_matches_the_builders(self):
        u = {"arm": "P", "truth": "eavail_tilt", "amplitude": 0.2}
        r = ibu1.truth_reweight(WORLD, u, {})
        np.testing.assert_array_equal(r, PROD.s5c_pseudo.truth_weight("eavail_tilt", INPUTS["MCgen"], EDGES, 0.2,
                                                                      w_truth=INPUTS["w_truth"]))


class Constructions(unittest.TestCase):
    def test_p_variants_are_the_measured_sample(self):
        key = ibu1.split_key_for(200000)
        exp, x_true, info, is_b, v = ibu1.build_p(WORLD, BKG, "eavail_tilt", 0.2, key, 200000)
        y_pur, b_pur = v["pur"]
        self.assertAlmostEqual(float(y_pur.sum()), float(exp["measured_weights"][ibu1.in_window(exp["measured"].astype(float), EDGES)].sum()), places=6)
        self.assertEqual(float(b_pur.sum()), 0.0)
        y_fold, b_fold = v["fold"]
        self.assertTrue(np.all(y_fold >= y_pur - 1e-9))
        self.assertAlmostEqual(float(b_fold.sum()), float(BKG["bkg_nd"].sum()))
        half = ibu1.half_from_experiment(WORLD, exp, is_b)
        self.assertEqual(half.rows.size, info["n_half_a"])

    def test_half_mismatch_is_refused(self):
        key = ibu1.split_key_for(200001)
        exp, _, _, is_b, _ = ibu1.build_p(WORLD, BKG, "nominal", 0.0, key, 200001)
        bad = dict(exp, w_reco=exp["w_reco"] * (1 + 1e-15))
        with self.assertRaises(ibu1.GateFailure):
            ibu1.half_from_experiment(WORLD, bad, is_b)
        with self.assertRaises(ibu1.GateFailure):
            ibu1.half_from_experiment(WORLD, exp, ~is_b)

    def test_n_variants(self):
        key = ibu1.split_key_for(301000)
        exp, x_true, info, is_b, v = ibu1.build_n(WORLD, BKG, "nominal", 0.0, key, 301000, None)
        y, t = v["fold"]
        ys, zs = v["sub"]
        np.testing.assert_allclose(ys, np.maximum(0, y - t))
        self.assertEqual(float(zs.sum()), 0.0)
        self.assertAlmostEqual(float(y.sum()), float(exp["obs_counts"].sum()), places=6)
        half = ibu1.half_from_experiment(WORLD, exp, is_b)
        self.assertEqual(half.rows.size, info["n_half_a"])

    def test_ratio_truths_dispatch(self):
        self.assertIn("ratio_nd", PROD.s5n_pseudo.TRUTHS)


class Pairing(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        key = ibu1.split_key_for(204000)
        self.exp, self.x_true, self.info, _, _ = ibu1.build_p(WORLD, BKG, "eavail_tilt", 0.2, key, 204000)
        self.key = key
        self.expect = ibu1.expected_construction(CFG, {"arm": "P"}, "eavail_tilt", 0.2)

    def product(self, xtrue, info, seed=204000, key=None, **flags):
        p = self.tmp / f"c{np.random.randint(1e9)}.npz"
        meta = {"pseudo_seed": seed, "split_key": self.key if key is None else key, "experiment": info,
                **self.expect["required"], **flags}
        np.savez(p, xsec_flat=xtrue.ravel(), xtrue_flat=xtrue.ravel(), meta=json.dumps(meta))
        return p

    def test_gate_passes_on_the_same_experiment(self):
        g = ibu1.comparator_gate(self.product(self.x_true, self.info), self.x_true, self.info, 204000, self.key, self.expect)
        self.assertTrue(g["pass"], g["checks"])

    def test_gate_fires_on_one_ulp(self):
        x = self.x_true.copy().ravel()
        i = int(np.flatnonzero(x)[0])
        x[i] = np.nextafter(x[i], np.inf)
        g = ibu1.comparator_gate(self.product(x.reshape(self.x_true.shape), self.info), self.x_true, self.info, 204000, self.key, self.expect)
        self.assertFalse(g["pass"])
        self.assertFalse(g["checks"]["xtrue_bitwise"])

    def test_gate_fires_on_a_different_draw(self):
        info = dict(self.info, pseudo_signal_events=self.info["pseudo_signal_events"] + 1)
        g = ibu1.comparator_gate(self.product(self.x_true, info), self.x_true, self.info, 204000, self.key, self.expect)
        self.assertFalse(g["checks"]["experiment_record"])

    def test_gate_fires_on_construction_flags(self):
        for flags in ({"prior_matches_truth": True}, {"no_background": True}, {"iters": 6}, {"truth": "nominal"},
                      {"bkg_dump_sha256": "0" * 64}):
            g = ibu1.comparator_gate(self.product(self.x_true, self.info, **flags), self.x_true, self.info, 204000,
                                     self.key, self.expect)
            self.assertFalse(g["pass"], flags)

    def test_gate_fires_on_seed_or_split(self):
        g = ibu1.comparator_gate(self.product(self.x_true, self.info, seed=204001), self.x_true, self.info, 204000, self.key, self.expect)
        self.assertFalse(g["checks"]["pseudo_seed"])
        g = ibu1.comparator_gate(self.product(self.x_true, self.info, key=self.key + 1), self.x_true, self.info, 204000, self.key, self.expect)
        self.assertFalse(g["checks"]["split_key"])


class Bootstrap(unittest.TestCase):
    def setUp(self):
        self.exp, *_ = ibu1.build_p(WORLD, BKG, "nominal", 0.0, 20260924, 1)

    def test_replica_equals_run_bootstrap(self):
        c = ibu1.replica_capture(PROD, self.exp, 3)
        self.assertTrue(c["pass"], c)
        self.assertEqual(c["files_written"], [])

    def test_capture_fires_on_a_different_replica(self):
        real = ibu1.p_bootstrap_replica

        def shifted(exp, b):
            return real(exp, b + 1)

        with mock.patch.object(ibu1, "p_bootstrap_replica", shifted):
            self.assertFalse(ibu1.replica_capture(PROD, self.exp, 3)["pass"])

    def test_n_replica_variants_use_the_replicas_counts_and_template(self):
        exp, *_ = ibu1.build_n(WORLD, BKG, "nominal", 0.0, ibu1.split_key_for(349999), 349999, None)
        rep = PROD.s5n_pseudo.bootstrap_replica(exp, 5)
        v = ibu1.n_variants(WORLD, rep)
        self.assertAlmostEqual(float(v["fold"][0].sum()), float(rep["obs_counts"].sum()), places=6)
        self.assertAlmostEqual(float(v["fold"][1].sum()), float(rep["tmpl_w"].sum()), places=6)
        self.assertNotAlmostEqual(float(v["fold"][1].sum()), float(exp["tmpl_w"].sum()), places=6)


class Coverage(unittest.TestCase):
    def test_hits_equal_s5c_coverage(self):
        tmp = Path(tempfile.mkdtemp())
        U, names = s5c_coverage.reported_functionals(CONTRACT)
        rng = np.random.default_rng(3)
        x0 = np.abs(rng.standard_normal(U.shape[1])) + 0.1
        est, tru = [], []
        for s in range(30):
            xt = x0 * (1 + 0.01 * rng.standard_normal(x0.size))
            xh = xt * (1 + 0.02 * rng.standard_normal(x0.size) + 0.005)
            np.savez(tmp / f"t_s{s}.npz", xsec_flat=xh, xtrue_flat=xt)
            est.append(U @ xh)
            tru.append(U @ xt)
        sigma = np.abs(U @ x0) * 0.01
        beta, se = np.full(len(names), 0.004), np.full(len(names), 0.001)
        for corr in (None, (beta, se)):
            ref = s5c_coverage.evaluate(U, sigma, tmp, "t", 0, 29, corr=corr)
            h = rd.hits(np.array(est), np.array(tru), sigma, corr)
            self.assertEqual(h[0].tolist(), ref["hits68"])
            self.assertEqual(h[1].tolist(), ref["hits95"])


class Rule(unittest.TestCase):
    def test_count_relation(self):
        self.assertEqual(rd.count_relation(0, 2), "within")
        self.assertEqual(rd.count_relation(10, 20), "within")
        self.assertEqual(rd.count_relation(9, 20), "better")
        self.assertEqual(rd.count_relation(21, 10), "worse")
        self.assertEqual(rd.count_relation(0, 3), "better")

    def test_count_interval_spans_the_boundary(self):
        rows = np.arange(4)
        n = 20
        h = np.array([[13, 14, 20, 20], [19, 19, 20, 20]])
        c = rd.count_interval(h, n, rows)
        self.assertLessEqual(c["definite"], c["point"])
        self.assertLessEqual(c["point"], c["possible"])
        cI = {"definite": 0, "possible": 10, "n": 400}
        cO = {"definite": 6, "possible": 12, "n": 400}
        self.assertFalse(rd.count_reading(cI, cO)["resolved"])
        self.assertTrue(rd.count_reading({"definite": 0, "possible": 1, "n": 400},
                                         {"definite": 30, "possible": 40, "n": 400})["resolved"])

    def test_count_interval_at_400_is_the_futility_count(self):
        """At n = 400 ``definite`` is the Tier-S futility count (UCB below a gate at 0.05/459)."""
        g = json.loads((ibu1.REPO / CFG["receipts"]["interim"]["path"]).read_text())
        tilt = next(x for x in g["grid"] if x["truth"] == "eavail_tilt")
        h = np.array([tilt["hits68"], tilt["hits95"]])
        c = rd.count_interval(h, 400, np.arange(h.shape[1]))
        futile = sum((u68 < 0.66) or (u95 < 0.94) for u68, u95 in zip(tilt["ucb68"], tilt["ucb95"]))
        self.assertEqual(c["definite"], futile)

    def test_residual_reading(self):
        rng = np.random.default_rng(4)
        rows = np.arange(50)
        relO = 0.05 + 0.001 * rng.standard_normal((60, 50))
        res = rd.residual_reading(0.01 + 0.001 * rng.standard_normal((60, 50)), relO, rows)
        self.assertEqual(res["relation"], "better")
        self.assertTrue(res["resolved"])
        res = rd.residual_reading(0.05 + 0.001 * rng.standard_normal((60, 50)), relO, rows)
        self.assertEqual(res["relation"], "within")
        noisy = rd.residual_reading(0.024 + 0.05 * rng.standard_normal((5, 50)), 0.05 + 0.05 * rng.standard_normal((5, 50)), rows)
        self.assertFalse(noisy["resolved"])

    def test_readings_and_verdicts(self):
        def t(res, cnt, rposs=None, corners=None, decisive=True):
            r = {"relation": res, "possible": rposs or [res]}
            c = {"relation": cnt, "corners": corners or [cnt], "decisive": decisive}
            return rd.truth_reading(r, c)

        self.assertEqual(t("within", "within")["reading"], "consistent")
        self.assertEqual(t("better", "better")["reading"], "IBU better")
        self.assertEqual(t("better", "within")["reading"], "mixed")
        self.assertTrue(t("within", "within", corners=["within", "worse"])["reading"].startswith("unresolved"))
        # below n = 400 the count is descriptive: the residual decides
        self.assertEqual(t("better", "within", corners=["within", "better"], decisive=False)["reading"], "IBU better")
        base = {k: t("within", "within") for k in ("tilt", "gibuu", "w1", "w2", "w3")}
        self.assertEqual(rd.overall(base), "inverse-problem limited")
        imp = dict(base, tilt=t("better", "better"), gibuu=t("better", "x", decisive=False))
        self.assertEqual(rd.overall(imp), "implementation specific")
        self.assertEqual(rd.overall(dict(base, w2=t("worse", "worse"))), "mixed")
        unr = dict(base, w3=t("within", "x", rposs=["within", "worse"], decisive=False))
        self.assertEqual(rd.overall(unr), "unresolved")
        # review finding 4: tilt resolved worse with an unresolved count rules out both verdicts -> mixed
        tilt_worse = t("worse", "within", corners=["within", "worse"])
        self.assertEqual(tilt_worse["possible"], ["IBU worse", "mixed"])
        self.assertEqual(rd.overall(dict(base, tilt=tilt_worse)), "mixed")

    def test_count_box_spanning_better_and_worse_allows_within(self):
        """Re-review: corners {better, worse} with an interior equal pair must keep "consistent" possible."""
        c = rd.count_reading({"definite": 5, "possible": 100, "n": 400}, {"definite": 30, "possible": 40, "n": 400})
        self.assertIn("within", c["corners"])
        r = rd.truth_reading({"relation": "within", "possible": ["within"]}, c)
        self.assertIn("consistent", r["possible"])
        base = {k: {"possible": ["consistent"]} for k in ("gibuu", "w1", "w2", "w3")}
        self.assertEqual(rd.overall(dict(base, tilt=r)), "unresolved")

    def test_small_n_count_cannot_resolve_and_is_descriptive(self):
        """Review finding 2: at n = 60 a functional covered 60/60 still has CP LB < 0.94 at 0.05/459."""
        rows = np.arange(109)
        cI = rd.count_interval(np.full((2, 109), 60), 60, rows)
        cO = rd.count_interval(np.zeros((2, 109), int), 60, rows)
        self.assertEqual(cI["possible"], 109)
        c = rd.count_reading(cI, cO)
        self.assertFalse(c["resolved"])
        self.assertFalse(c["decisive"])
        res = {"relation": "better", "possible": ["better"]}
        self.assertEqual(rd.truth_reading(res, c)["reading"], "IBU better")
        cI4 = rd.count_interval(np.full((2, 109), 400), 400, rows)
        cO4 = rd.count_interval(np.zeros((2, 109), int), 400, rows)
        c4 = rd.count_reading(cI4, cO4)
        self.assertTrue(c4["resolved"] and c4["decisive"] and c4["relation"] == "better")


class Tasks(unittest.TestCase):
    def test_committed_table_is_the_generators(self):
        import make_tasks

        self.assertEqual((HERE / "tasks.tsv").read_text(), make_tasks.render(CFG))

    def test_table_covers_every_declared_seed_once(self):
        import make_tasks

        seen = {}
        for line in make_tasks.lines(CFG):
            _, unit, seeds = line.split("\t")
            if seeds:
                a, b = (int(v) for v in seeds.split(":"))
                seen.setdefault(unit, []).extend(range(a, b + 1))
        for u in CFG["units"]:
            if u["kind"] == "experiments" and "seeds" in u:
                self.assertEqual(sorted(seen[u["name"]]), list(range(u["seeds"][0], u["seeds"][1] + 1)))

    def test_seed_subrange_is_refused_outside_the_unit(self):
        rc = ibu1.main(["--npz", "x", "--bkg", "y", "--out", "z", "--unit", "P_tilt", "--seeds", "203999:204001"])
        self.assertEqual(rc, 2)


class EndToEnd(unittest.TestCase):
    """The driver's units on the synthetic world, then the reader over them (fake OmniFold side)."""

    def test_units_then_read(self):
        tmp = Path(tempfile.mkdtemp())
        cfg = json.loads(json.dumps(CFG))
        comp = tmp / "comp"
        comp.mkdir()
        units = {u["name"]: u for u in cfg["units"]}
        small = {"P_nominal": [200000, 200004], "P_tilt": [204000, 204004], "N_nominal_dev": [300000, 300004],
                 "N_nominal_val": [300060, 300064], "N_gibuu": [301000, 301004], "N_gibuu_R": [801000, 801004],
                 "N_nominal_R": [800000, 800004], "N_w1": [803000, 803004], "N_w2": [804000, 804004],
                 "N_w3": [805000, 805004]}
        for name, seeds in small.items():
            u = units[name]
            u["seeds"] = seeds
            if "comparator" in u:
                u["comparator"] = {"template": str(comp / (name + "_s{seed}.npz")), "seeds": seeds}
        units["P_d1"]["pairs"] = units["P_d1"]["pairs"][:3]
        units["P_d1"]["comparator"] = {"paths": {str(s): str(comp / f"P_d1_s{s}.npz") for s, _ in units["P_d1"]["pairs"]}}
        for b in ("P_sigma", "N_sigma_s5n", "N_sigma_R"):
            units[b]["replicas"] = [1, 4]
            units[b]["comparator_base"] = str(comp / f"{b}_base.npz")
        ratios = ibu1.load_ratios(cfg)
        # comparator products: the experiment's own truth and record, estimate = truth x 1.03
        for name, u in units.items():
            if u["kind"] != "experiments":
                continue
            for seed, key in ibu1.unit_seeds(u):
                p = ibu1.comparator_path(u, seed)
                if p is None:
                    continue
                if u["arm"] == "P":
                    _, xt, info, _, _ = ibu1.build_p(WORLD, BKG, u["truth"], u["amplitude"], key, seed)
                else:
                    _, xt, info, _, _ = ibu1.build_n(WORLD, BKG, u["truth"], u["amplitude"], key, seed, ratios.get(u.get("ratio")))
                exp_c = ibu1.expected_construction(cfg, u, u["truth"], u["amplitude"])["required"]
                np.savez(p, xsec_flat=xt.ravel() * 1.03, xtrue_flat=xt.ravel(),
                         meta=json.dumps({"pseudo_seed": seed, "split_key": key, "experiment": json.loads(json.dumps(info)),
                                          **exp_c}))
        for b in ("P_sigma", "N_sigma_s5n", "N_sigma_R"):
            u = units[b]
            builder = ibu1.build_p if u["arm"] == "P" else ibu1.build_n
            args = (WORLD, BKG, "nominal", 0.0, u["experiment"]["split_key"], u["experiment"]["pseudo_seed"])
            _, _, info, _, _ = builder(*args) if u["arm"] == "P" else builder(*args, None)
            np.savez(u["comparator_base"], xsec_flat=np.zeros(3),
                     meta=json.dumps({"pseudo_seed": u["experiment"]["pseudo_seed"], "split_key": u["experiment"]["split_key"],
                                      "experiment": json.loads(json.dumps(info)),
                                      **ibu1.expected_construction(cfg, u, "nominal", 0.0)["required"]}))
        out = tmp / "out"
        rc = 0
        for name, u in units.items():
            if u["kind"] == "experiments":
                rc |= ibu1.run_experiments(WORLD, cfg, BKG, u, out, ratios)
            elif u["kind"] == "bootstrap":
                rc |= ibu1.run_bootstrap(WORLD, cfg, BKG, u, out)
            else:
                rc |= ibu1.run_data(WORLD, cfg, BKG, u, out)
        self.assertEqual(rc, 0)
        boot = np.load(out / "P_sigma.npz", allow_pickle=True)
        self.assertTrue(json.loads(str(boot["meta"]))["controls"]["replica_capture"]["pass"])
        self.assertEqual(boot["F_pur"].shape, (4, len(KS), 153))
        # a fake OmniFold receipt set with the shapes the reader expects
        names = WORLD.names
        nF = len(names)

        def per(n):
            return {"cov68": [0.5] * nF, "cov95": [0.9] * nF, "mean_rel": [0.0] * nF}

        receipts = {"interim": {"sigma": [1.0] * nF, "grid": [
            {"truth": "nominal", "n_present": 5, "hits68": [3] * nF, "hits95": [5] * nF},
            {"truth": "eavail_tilt", "n_present": 5, "hits68": [1] * nF, "hits95": [2] * nF}]},
            "bias_correction": {"beta": [0.0] * nF, "se": [0.0] * nF},
            "s5n": {"grid": {"C3_nominal": {"n_experiments": 5, "per_functional": per(5)},
                             "C4_eavail_shape": {"n_experiments": 5, "per_functional": per(5)}}},
            "R": {"points": {k: {"n": 5, "per_functional": per(5)} for k in ("nominal", "eavail_gibuu", "W1", "W2", "W3")}}}
        variant = {"P": "pur", "N": "fold"}
        res = rd.evaluate(out, receipts, names, variant, [5])
        k5 = res["per_K"]["5"]
        self.assertIn(k5["verdict"], ("inverse-problem limited", "implementation specific", "mixed", "unresolved"))
        self.assertEqual(set(k5["deformed"]), {"tilt", "gibuu", "w1", "w2", "w3"})
        for v in k5["deformed"].values():
            self.assertEqual(v["gates_passed"], v["gates_total"])
            self.assertAlmostEqual(v["residual"]["median_abs_of"], 0.03, places=9)
        # review finding 1: a single-K evaluation reads the K = 5 slice, not slot 0
        tilt = rd.load_unit(out, "N_gibuu", "sub", [301000, 301059])
        i5 = tilt["ks"].index(5)
        self.assertFalse(np.allclose(tilt["F"][:, 0, :], tilt["F"][:, i5, :], rtol=1e-6, atol=0))
        sec = rd.evaluate(out, receipts, names, {"P": "fold", "N": "sub"}, [5])["per_K"]["5"]["deformed"]["gibuu"]
        rows = np.array([i for i, nm in enumerate(names) if nm.startswith("J")])
        rows = rows[np.all(tilt["t"][:, rows] != 0, axis=0)]
        want = float(np.median(np.abs((tilt["F"][:, i5, :] / tilt["t"] - 1)[:, rows].mean(0))))
        self.assertAlmostEqual(sec["residual"]["median_abs_ibu"], want, places=12)
        self.assertFalse(any(p.suffix == ".tmp" for p in out.iterdir()))
        d = np.load(out / "D_P.npz", allow_pickle=True)
        self.assertEqual(d["F_pur"].shape, (len(KS), 153))


if __name__ == "__main__":
    unittest.main()
