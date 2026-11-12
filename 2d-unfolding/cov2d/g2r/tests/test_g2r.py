"""COV2D-G2R's pure functions (g2r.py) and the readout's cores (g2r_readout.py), on synthetic arrays.

    python3 -B 2d-unfolding/cov2d/g2r/tests/test_g2r.py

The C_T' tests import the rollup (re2c_rollup, which imports ROOT) and compare with cov2d_blocks.assemble itself.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
G2R = HERE.parent
COV2D = G2R.parent
REPO = COV2D.parents[1]
sys.path[:0] = [str(G2R), str(COV2D), str(REPO / "nd-unfolding"), str(REPO / "2d-unfolding" / "re2" / "partc")]
import g2r  # noqa: E402
import g2r_readout as gr  # noqa: E402


def synthetic(blocks=((40, 12), (30, 9)), seed=3, universe_scale=None):
    """Signal and truth trees in the event loop's layout. Per block of n entries with m misses: the truth tree holds
    n distinct events in event-loop order; the reco loop's n - m rows (some failing the selection) come first in the
    signal tree, in a shuffled order, then the m misses in truth order, with sim = -9999 and every universe weight
    the CV w_truth. Returns S, T, block list, and the universe columns {name: (sig_wt, sig_wr, truth_wt)}."""
    rng = np.random.default_rng(seed)
    S = {k: [] for k in ("MC", "MC_pz", "w_truth", "w_reco", "sim", "sim_pass")}
    T = {k: [] for k in ("MC", "MC_pz", "w_truth")}
    U = {"same": ([], [], []), "varied": ([], [], []), "last": ([], [], [])}
    blk = []
    for b, (n, m) in enumerate(blocks):
        mc, pz, wt = rng.uniform(0, 2, n), rng.uniform(1.5, 20, n), rng.uniform(0.5, 1.5, n)
        f_var = rng.uniform(0.8, 1.2, n)
        f_last = rng.uniform(0.7, 1.3, n)
        miss = np.sort(rng.choice(n, m, replace=False))
        reco = np.setdiff1d(np.arange(n), miss)
        rng.shuffle(reco)
        for k, v in (("MC", mc), ("MC_pz", pz), ("w_truth", wt)):
            T[k].append(v)
        U["same"][2].append(wt)
        U["varied"][2].append(wt * f_var)
        U["last"][2].append(wt * f_last)
        # reco rows, then misses
        S["MC"].append(np.r_[mc[reco], mc[miss]])
        S["MC_pz"].append(np.r_[pz[reco], pz[miss]])
        S["w_truth"].append(np.r_[wt[reco], wt[miss]])
        S["w_reco"].append(np.r_[rng.uniform(0.5, 1.5, reco.size), wt[miss]])
        S["sim"].append(np.r_[rng.uniform(0, 2, reco.size), np.full(m, -9999.0)])
        sp = (rng.uniform(size=reco.size) < 0.8).astype(np.int64)
        S["sim_pass"].append(np.r_[sp, np.zeros(m, np.int64)])
        U["same"][0].append(np.r_[wt[reco], wt[miss]])
        U["same"][1].append(np.r_[S["w_reco"][-1][:reco.size], wt[miss]])
        U["varied"][0].append(np.r_[(wt * f_var)[reco], wt[miss]])        # misses carry the proxy
        U["varied"][1].append(np.r_[S["w_reco"][-1][:reco.size] * 1.1, wt[miss]])
        U["last"][0].append(np.r_[(wt * f_last)[reco], wt[miss]])
        U["last"][1].append(np.r_[S["w_reco"][-1][:reco.size] * 0.9, wt[miss]])
        blk.append((f"pl{b}", n, m))
    S = {k: np.concatenate(v) for k, v in S.items()}
    T = {k: np.concatenate(v) for k, v in T.items()}
    U = {k: tuple(np.concatenate(x) for x in v) for k, v in U.items()}
    return S, T, blk, U


def p5_reference(S, T, blk, truth_u):
    """P5's build_miss_override.py loop, transcribed: per block, the tail rows matched by exact key to the truth rows,
    and w_override = the truth tree's universe column there."""
    N = len(S["MC"])
    w = np.full(N, np.nan)
    o = 0
    for _, n, m in blk:
        r = n - m
        tk = g2r.keys([T["MC"][o:o + n], T["MC_pz"][o:o + n], T["w_truth"][o:o + n]])
        sk = g2r.keys([S["MC"][o + r:o + n], S["MC_pz"][o + r:o + n], S["w_truth"][o + r:o + n]])
        order = np.argsort(tk, kind="stable")
        pos = np.searchsorted(tk[order], sk)
        w[o + r:o + n] = truth_u[o:o + n][order[pos]]
        o += n
    return w


class Map(unittest.TestCase):
    def setUp(self):
        self.S, self.T, self.blk, self.U = synthetic()

    def test_the_map_finds_every_miss_and_its_truth_row(self):
        miss, truth, rep = g2r.build_map(self.S, self.T, self.blk)
        self.assertEqual(miss.size, sum(m for _, _, m in self.blk))
        for k in ("MC", "MC_pz", "w_truth"):
            np.testing.assert_array_equal(self.S[k][miss], self.T[k][truth])
        self.assertTrue(all(v["pass"] for v in rep["checks"].values()))

    def test_override_equals_p5_builder_semantics(self):
        """For every universe column of the fixture (the identity one, a varied one and the last), the map's override
        equals P5's builder loop bitwise, both as transcribed here and as g2r.p5_override (the prepare's G11)."""
        miss, truth, _ = g2r.build_map(self.S, self.T, self.blk)
        for name in ("same", "varied", "last"):
            with self.subTest(name):
                got = g2r.override(miss, truth, self.U[name][2], len(self.S["MC"]))
                for want in (p5_reference(self.S, self.T, self.blk, self.U[name][2]),
                             g2r.p5_override(self.S, self.T, self.blk, self.U[name][2])):
                    np.testing.assert_array_equal(np.isnan(got), np.isnan(want))
                    np.testing.assert_array_equal(got[~np.isnan(got)], want[~np.isnan(want)])

    def test_the_spot_check_passes_and_refuses(self):
        miss, truth, _ = g2r.build_map(self.S, self.T, self.blk)
        cols = {name: self.U[name][2] for name in ("same", "varied", "last")}
        rec = g2r.spot_check(self.S, self.T, self.blk, miss, truth, cols)
        self.assertEqual(sorted(rec), ["last", "same", "varied"])
        self.assertTrue(all(r["equal"] for r in rec.values()))
        bad = truth.copy()
        bad[[0, 1]] = bad[[1, 0]]
        with self.assertRaisesRegex(g2r.Refusal, "G11"):
            g2r.spot_check(self.S, self.T, self.blk, miss, bad, cols)

    def corrupt(self, key, idx, value):
        S = {k: v.copy() for k, v in self.S.items()}
        S[key][idx] = value
        return S

    def test_each_alignment_check_refuses(self):
        n0, m0 = self.blk[0][1], self.blk[0][2]
        tail0 = n0 - m0
        cases = {
            "a tail row passing": (self.corrupt("sim_pass", tail0, 1), self.T, self.blk),
            "a tail row without the sentinel": (self.corrupt("sim", tail0, 0.5), self.T, self.blk),
            "a tail w_reco not the proxy": (self.corrupt("w_reco", tail0, 9.0), self.T, self.blk),
            "a miss not in the truth tree": (self.corrupt("MC", tail0, 77.0), self.T, self.blk),
            "the block sizes": (self.S, self.T, [(self.blk[0][0], n0 + 1, m0), self.blk[1]]),
        }
        T_dup = {k: v.copy() for k, v in self.T.items()}
        for k in T_dup:
            T_dup[k][1] = T_dup[k][0]
        cases["duplicate truth keys"] = (self.S, T_dup, self.blk)
        # misses out of truth order: swap two tail rows
        S_sw = {k: v.copy() for k, v in self.S.items()}
        for k in S_sw:
            S_sw[k][[tail0, tail0 + 1]] = S_sw[k][[tail0 + 1, tail0]]
        cases["misses out of order"] = (S_sw, self.T, self.blk)
        # a reco row that is not a truth event of the block
        cases["the complement"] = (self.corrupt("MC_pz", 0, 99.0), self.T, self.blk)
        expect = {"a tail row passing": "tail_sim_pass_0", "a tail row without the sentinel": "tail_sim_sentinel",
                  "a tail w_reco not the proxy": "tail_w_reco_eq_w_truth", "a miss not in the truth tree":
                  "every_miss_found", "the block sizes": "n_signal_eq_sum_blocks", "duplicate truth keys":
                  "truth_keys_unique", "misses out of order": "subsequence_order",
                  "the complement": "complement_eq_reco_rows_cv"}
        self.assertEqual(set(expect), set(cases))
        for name, (S, T, blk) in cases.items():
            with self.subTest(name), self.assertRaisesRegex(g2r.Refusal, expect[name]):
                g2r.build_map(S, T, blk)

    def test_universe_check_counts_and_identity(self):
        miss, truth, _ = g2r.build_map(self.S, self.T, self.blk)
        same = g2r.universe_check(self.S, self.T, *self.U["same"], miss, truth, self.blk)
        self.assertTrue(same["identity"])
        self.assertEqual(same["n_changed"], 0)
        var = g2r.universe_check(self.S, self.T, *self.U["varied"], miss, truth, self.blk)
        self.assertFalse(var["identity"])
        self.assertEqual(var["n_changed"], miss.size)

    def test_universe_check_refuses_a_non_proxy_miss_and_a_complement_mismatch(self):
        miss, truth, _ = g2r.build_map(self.S, self.T, self.blk)
        wt, wr, tt = (a.copy() for a in self.U["varied"])
        wt[miss[0]] *= 1.5
        with self.assertRaises(g2r.Refusal):
            g2r.universe_check(self.S, self.T, wt, wr, tt, miss, truth, self.blk)
        wt, wr, tt = (a.copy() for a in self.U["varied"])
        head = np.setdiff1d(np.arange(len(wt)), miss)
        wt[head[0]] *= 1.5
        with self.assertRaises(g2r.Refusal):
            g2r.universe_check(self.S, self.T, wt, wr, tt, miss, truth, self.blk)


def spd(n, seed, lo=1e-3):
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(n, n))
    Q, _ = np.linalg.qr(A)
    return Q @ np.diag(np.geomspace(1.0, lo, n)) @ Q.T


class Readings(unittest.TestCase):
    def test_epsilon_is_zero_for_no_change_and_t_for_a_scaling(self):
        C = spd(12, 1)
        self.assertEqual(g2r.epsilon(C, np.zeros_like(C))["eps"], 0.0)
        self.assertAlmostEqual(g2r.epsilon(C, 0.07 * C)["eps"], 0.07, places=10)

    def test_epsilon_sees_a_change_in_the_weakest_direction(self):
        C = spd(12, 2)
        lam, U = g2r.retained(C)
        dC = 0.2 * lam[-1] * np.outer(U[:, -1], U[:, -1])
        self.assertAlmostEqual(g2r.epsilon(C, dC)["eps"], 0.2, places=8)
        self.assertLess(g2r.epsilon(C, dC, k=6)["eps"], 1e-8)

    def test_coupling_to_discarded_directions(self):
        C = spd(10, 3)
        lam, U = g2r.retained(C)
        dC = 1e-3 * (np.outer(U[:, 0], U[:, -1]) + np.outer(U[:, -1], U[:, 0]))
        self.assertGreater(g2r.epsilon(C, dC, k=5)["coupling_to_discarded"], 0)
        self.assertLess(g2r.epsilon(C, dC)["coupling_to_discarded"], 1e-12)

    def test_a_null_direction_does_not_enter_eps_and_coupling_sees_it(self):
        """On a rank-deficient C, eps uses only the retained eigensystem: a change confined to the null direction leaves
        eps at 0, and a change coupling it to a retained direction shows only in the coupling."""
        C = spd(9, 8)
        lam, U = g2r.retained(C)
        v = U[:, -1]
        C0 = C - lam[-1] * np.outer(v, v)                    # rank 8, v its null direction
        self.assertEqual(g2r.rank(C0), 8)
        r = g2r.epsilon(C0, 1e-3 * np.outer(v, v))
        self.assertLess(r["eps"], 1e-9)
        u0 = U[:, 0]
        r2 = g2r.epsilon(C0, 1e-3 * (np.outer(u0, v) + np.outer(v, u0)))
        self.assertLess(r2["eps"], 1e-9)
        self.assertGreater(r2["coupling_to_discarded"], 1e-6)

    def test_more_directions_than_retained_refuses(self):
        C = spd(6, 4)
        with self.assertRaises(g2r.Refusal):
            g2r.epsilon(C, C, k=7)

    def test_rank_and_correlation(self):
        C = spd(8, 5)
        v = np.ones(8)
        self.assertEqual(g2r.rank(C), 8)
        P = C - (C @ v)[:, None] * (C @ v)[None, :] / (v @ C @ v)        # rank 7, PSD
        self.assertEqual(g2r.rank(P), 7)
        self.assertEqual(g2r.corr_change(C, C)["max_abs_delta_rho"], 0.0)

    def test_readings_carry_every_field_and_the_metrics(self):
        C = spd(150, 6, lo=1e-4)
        x = np.ones(150)
        calls = []

        def metrics(Cm, xm, F):
            calls.append(F)
            return {"median_pct": float(np.median(np.sqrt(np.diag(Cm)))), "integral_sigma_pct": float(Cm.sum())}
        r = g2r.readings(C, 1.1 * C, metrics, x, "F")
        self.assertEqual(set(r["eps"]), {"retained", "73", "139"})
        self.assertAlmostEqual(r["eps"]["retained"]["eps"], 0.1, places=8)
        self.assertEqual(r["rank"], {"before": 150, "after": 150})
        self.assertEqual(calls, ["F", "F"])


class CTPrime(unittest.TestCase):
    """c_t_prime against cov2d_blocks.assemble itself: on the old bands it reproduces assemble's blocks bitwise (G6),
    and a changed universe band moves only C_univ and C_T."""

    @classmethod
    def setUpClass(cls):
        import cov2d as c
        import cov2d_blocks as cb
        cls.c, cls.cb = c, cb
        cls.ro = cb.rollup()
        rng = np.random.default_rng(9)
        n = 205
        cls.rep = np.zeros(256, bool)
        cls.rep[:n] = True
        x_T = rng.uniform(1, 2, n)
        cls.bands = {b: x_T * (1 + 0.02 * rng.normal(size=(c.BANDS[b], n))) for b in c.ORDER}
        for b in c.LATERAL_BANDS:
            cls.bands[b] = x_T * (1 + 0.02 * rng.normal(size=(2, n)))
        cls.minos_x = x_T * (1 + 0.02 * rng.normal(size=(2, n)))
        cls.w_flux = rng.uniform(0.5, 1.5, 100)
        X_rep = x_T * (1 + 0.01 * rng.normal(size=(300, n)))
        x_R = x_T * rng.uniform(0.95, 1.05, n)
        C08_R = np.diag((0.001 * x_R) ** 2)
        Cm = np.diag(np.full(n, 0.002))
        cls.Cminus = np.diag(np.full(n, 0.001))
        out = cb.assemble(x_T, cls.rep, cls.bands, cls.minos_x, cls.w_flux, X_rep, x_R, C08_R, Cm, cls.Cminus)
        cls.B = {k: out[k] for k in ("C_T", "C_univ", "C_lat", "C_norm", "C_stat", "C08", "C_model_abs", "C_T_minus")}
        cls.B.update(x_T=x_T, x_R=x_R, rep=cls.rep, minos_x=cls.minos_x, w_flux=np.asarray(cls.w_flux, np.float64))
        cls.B.update({f"band__{b}": v for b, v in cls.bands.items()})

    def rebuild(self, bands):
        cells = self.cb.CellsT(self.rep, self.B["x_T"])
        return g2r.c_t_prime(self.B, bands, self.ro.universe_block, cells, self.c.ORDER, self.c.LATERAL_BANDS,
                             self.cb.NORM_KEY, self.Cminus)

    def test_the_old_bands_reproduce_the_committed_blocks_bitwise(self):
        new = self.rebuild(gr.old_bands(self.B, self.c.ORDER))
        self.assertTrue(gr.g6_tune(self.B, new)["pass"])

    def test_a_changed_universe_band_moves_only_c_univ_and_c_t(self):
        bands = gr.old_bands(self.B, self.c.ORDER)
        bands["MaRES"] = bands["MaRES"] * 1.01
        new = self.rebuild(bands)
        self.assertFalse(np.array_equal(new["C_univ"], self.B["C_univ"]))
        self.assertFalse(gr.g6_tune(self.B, new)["pass"])
        for k in ("C_lat", "C_norm", "C_stat", "C08", "C_model_abs"):
            np.testing.assert_array_equal(new[k], self.B[k])
        np.testing.assert_allclose(new["C_T"] - new["C_univ"], self.B["C_T"] - self.B["C_univ"], rtol=0, atol=1e-15)

    def test_a_tampered_lateral_block_refuses(self):
        B = dict(self.B)
        B["C_lat"] = B["C_lat"] * (1 + 1e-15)
        cells = self.cb.CellsT(self.rep, B["x_T"])
        with self.assertRaises(g2r.Refusal):
            g2r.c_t_prime(B, gr.old_bands(B, self.c.ORDER), self.ro.universe_block, cells, self.c.ORDER,
                          self.c.LATERAL_BANDS, self.cb.NORM_KEY, self.Cminus)

    def test_a_missing_universe_band_refuses(self):
        bands = gr.old_bands(self.B, self.c.ORDER)
        del bands["MaRES"]
        with self.assertRaises(g2r.Refusal):
            self.rebuild(bands)

    def test_the_npz_layout_is_phase_ns(self):
        arrays = g2r.blocks_npz_arrays(self.B, self.rebuild(gr.old_bands(self.B, self.c.ORDER)))
        want = {"C_T", "C_univ", "C_lat", "C_norm", "C_stat", "C08", "C_model_abs", "C_T_minus", "x_T", "x_R", "rep",
                "minos_x", "w_flux"} | {f"band__{b}" for b in self.bands}
        self.assertEqual(set(arrays), want)


class ReadoutCores(unittest.TestCase):
    def test_grade_reproduction(self):
        g = {"ndf": 205, "counts": [1, 2], "k_cell": [0, 0], "cell_flag": [False, True], "joint_count": 0,
             "k_joint": 190, "flagged_cells": [29], "verdict": "UNDER-COVERS", "chi2_mean_over_ndf": 16.55}
        self.assertTrue(gr.grade_reproduces(dict(g), g, 1e-9)["pass"])
        self.assertFalse(gr.grade_reproduces(dict(g, joint_count=1), g, 1e-9)["pass"])
        self.assertFalse(gr.grade_reproduces(dict(g, chi2_mean_over_ndf=16.55 * (1 + 1e-6)), g, 1e-9)["pass"])

    def test_data_core_replaces_only_the_universe_bands(self):
        order, flux = ("Flux", "MaRES"), "Flux"
        rng = np.random.default_rng(4)
        X = {"Flux": rng.normal(size=(5, 4)), "MaRES": rng.normal(size=(2, 4))}

        def band_cov(A, w=None):
            w = np.ones(A.shape[0]) if w is None else np.asarray(w)
            m = (w[:, None] * A).sum(0) / w.sum()
            D = A - m
            return (w[:, None] * D).T @ D / w.sum()
        w = rng.uniform(0.5, 1.5, 5)
        s5 = {f"band_{b}": band_cov(X[b], w if b == flux else None) for b in order}
        Q = np.eye(4) + sum(s5.values())
        same = gr.data_core(s5, Q, X, w, band_cov, order, flux)
        np.testing.assert_allclose(same["C_new"], Q, rtol=0, atol=1e-14)
        X2 = dict(X, MaRES=X["MaRES"] * 2)
        moved = gr.data_core(s5, Q, X2, w, band_cov, order, flux)
        np.testing.assert_allclose(moved["C_new"] - Q, band_cov(X2["MaRES"]) - s5["band_MaRES"], atol=1e-14)
        with self.assertRaises(g2r.Refusal):
            gr.data_core(s5, Q, {"Flux": X["Flux"]}, w, band_cov, order, flux)

    def test_floor_is_zero_for_bitwise_reruns(self):
        rng = np.random.default_rng(5)
        X = {"MaRES": rng.normal(size=(2, 4))}

        def band_cov(A, w=None):
            return np.cov(A, rowvar=False, ddof=0)
        Q = np.eye(4)
        fl = gr.floor_core(Q, X, {("MaRES", 1): X["MaRES"][1].copy()}, None, band_cov, "Flux")
        self.assertEqual(fl["bitwise_equal"], {"MaRES:1": True})
        np.testing.assert_array_equal(fl["Q_floor"], Q)
        fl2 = gr.floor_core(Q, X, {("MaRES", 1): X["MaRES"][1] + 1e-3}, None, band_cov, "Flux")
        self.assertFalse(np.array_equal(fl2["Q_floor"], Q))


class RegradeCore(unittest.TestCase):
    """regrade_core on a synthetic tune of 205 cells (with the outlier cell) and 300 errors: the null comes from the
    corrected bands and C_T', the grade reads E against C_T' (not the committed C_T), and the null is handed out
    before the grade."""

    @classmethod
    def setUpClass(cls):
        import cov2d as c
        import cov2d_blocks as cb
        cls.c, cls.cb = c, cb
        ro = cb.rollup()
        rng = np.random.default_rng(31)
        n = 205
        rep = np.zeros(256, bool)
        rep[list(range(204)) + [c.OUTLIER_CELL]] = True
        x_T = rng.uniform(1, 2, n)
        bands = {b: x_T * (1 + 0.03 * rng.normal(size=(c.BANDS[b], n))) for b in c.ORDER}
        for b in c.LATERAL_BANDS:
            bands[b] = x_T * (1 + 0.03 * rng.normal(size=(2, n)))
        minos_x = x_T * (1 + 0.03 * rng.normal(size=(2, n)))
        w_flux = rng.uniform(0.5, 1.5, 100)
        X_rep = x_T * (1 + 0.02 * rng.normal(size=(300, n)))
        C08_R = np.diag((0.001 * x_T) ** 2)
        Cm, Cminus = np.diag(np.full(n, 0.002)), np.diag(np.full(n, 0.001))
        out = cb.assemble(x_T, rep, bands, minos_x, w_flux, X_rep, x_T, C08_R, Cm, Cminus)
        B = {k: out[k] for k in ("C_T", "C_univ", "C_lat", "C_norm", "C_stat", "C08", "C_model_abs", "C_T_minus")}
        B.update(x_T=x_T, x_R=x_T, rep=rep, minos_x=minos_x, w_flux=np.asarray(w_flux, np.float64))
        B.update({f"band__{b}": v for b, v in bands.items()})
        new_bands = {b: (bands[b] - x_T) * 1.3 + x_T for b in c.ORDER}          # every shift 30% larger
        cls.B = B
        cls.new = g2r.c_t_prime(B, new_bands, ro.universe_block, cb.CellsT(rep, x_T), c.ORDER, c.LATERAL_BANDS,
                                cb.NORM_KEY, Cminus)
        L = np.linalg.cholesky(cls.new["C_T"] + 1e-12 * np.eye(n) * np.trace(cls.new["C_T"]) / n)
        cls.E = (L @ rng.normal(size=(n, 300))).T * 1.5
        cls.flat = [int(i) for i in np.flatnonzero(rep)]
        cls.weak = np.ones(n)
        cls.handed = []
        cls.core = gr.regrade_core(B, cls.new, cls.E, "G18", cls.flat, cls.weak, [], "M", n_mc=20000,
                                   write_null=cls.handed.append)

    def test_the_null_is_from_the_corrected_bands_and_c_t_prime(self):
        import cov2d_null as cn
        want = cn.null_at_T(self.new, self.new["bands"], self.B["minos_x"], self.B["w_flux"], n_mc=20000)
        np.testing.assert_array_equal(np.asarray(self.core["null_record"]["null"]["p_cell"]),
                                      np.asarray(want["null"]["p_cell"]))
        self.assertEqual(len(self.handed), 1)
        self.assertIs(self.handed[0], self.core["null_record"])

    def test_the_grade_reads_the_errors_against_c_t_prime(self):
        import fd_1b_null as nl
        chi2, ndf = nl.chi2_nonnull(self.E, self.new["C_T"])
        g = self.core["grade"]
        self.assertEqual(g["ndf"], ndf)
        self.assertAlmostEqual(g["chi2_mean_over_ndf"], chi2.mean() / ndf, places=9)
        chi2_old, _ = nl.chi2_nonnull(self.E, self.B["C_T"])
        self.assertNotAlmostEqual(g["chi2_mean_over_ndf"], chi2_old.mean() / ndf, places=3)

    def test_the_tune_eps_is_of_c_t_prime_against_the_committed_c_t(self):
        r = g2r.readings(self.B["C_T"], self.new["C_T"])
        self.assertEqual(self.core["tune_eps"]["eps"]["retained"], r["eps"]["retained"])
        self.assertGreater(r["eps"]["retained"]["eps"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
