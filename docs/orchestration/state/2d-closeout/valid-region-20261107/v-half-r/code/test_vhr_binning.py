#!/usr/bin/env python3
"""Tests for vhr_binning.py (unittest; numpy only). AMENDMENT-1 A9's list:
  - the reproduction mode equals h2_definition.merge (A4.5, audit M1), on random responses with support failures;
  - both mask directions (A2), and shares computed within Ω;
  - strip refusal (A3.1) and the p∥ = 4.5 refusal (A5);
  - A3.4: the 19/62/19 and single-cell structural failures, the 80 % veto, the veto's monotonicity, 70/10/10/10;
  - a T3 for each failing quantity, the floors, the weight STOPs and C7's landmarks;
  - an end-to-end build on synthetic events, with a deterministic fine map.
Each refusal is tested in the direction it acts."""
import json
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vhr_binning as vb  # noqa: E402

sys.path.insert(0, str(vb.REPO / "nd-unfolding" / "pv-ladder"))
import h2_definition as h2  # noqa: E402

S1 = vb.s1
H2DEF = vb.h2_definition()
OMEGA, H2_OF_FINE = vb.omega_mask(H2DEF)


def centre(axis, i):
    e = S1.FINE[axis]
    return 0.5 * (e[i] + e[i + 1])


def point(pt, pz, ea, q3, w):
    """Coordinates at the centres of the given fine indices."""
    return [centre("pt", pt), centre("pz", pz), centre("eavail", ea), centre("q3", q3), centre("W", w)]


def resp_2d(dims, ts, purity=0.9):
    """A Response on a small 2D grid whose cells all have the given purity and diagonal fraction and large support."""
    n = int(np.prod(dims))
    big = 1e4
    M = np.diag(np.full(n, purity * big))
    return vb.Response(M, np.full(n, big), np.full(n, big), np.asarray(ts, float).reshape(-1), shape=tuple(dims))


class Repro(unittest.TestCase):
    def test_repro_equals_h2_merge(self):
        rng = np.random.default_rng(20261111)
        for trial in range(40):
            M = rng.uniform(0, 1, (32, 32)) ** 6 * 3000
            M[np.diag_indices(32)] += rng.uniform(0, 3000, 32)
            ra = M.sum(axis=0) + rng.uniform(0, 4000, 32)
            tr = M.sum(axis=1) + rng.uniform(0, 4000, 32)
            ts = rng.uniform(0, 5000, 32)
            ts[rng.choice(32, 5, replace=False)] = rng.uniform(0, 999, 5)   # support failures (audit M1)
            tau = float(rng.choice([0.1, 0.3, 0.5]))
            ref_boxes, _, ref_flag = h2.merge(h2.Stats(M, ra, tr, ts, np.ones(32)), tau=tau)
            got, _, flag = vb.merge(vb.Response(M, ra, tr, ts), vb.Boxes([[c] for c in range(32)], freeze_pz=False),
                                    mode="repro", tau=tau)
            self.assertEqual([list(b) for b in got], ref_boxes, f"trial {trial}")
            self.assertEqual(flag, ref_flag, f"trial {trial}")

    def test_unsupported_bins_are_never_low_in_repro(self):
        M = np.diag(np.full(32, 10.0))          # purity 10 / 2000 = 0.005 < tau everywhere
        ra, tr, ts = np.full(32, 2000.0), np.full(32, 2000.0), np.full(32, 500.0)   # truth_sel < 1000: unsupported
        got, steps, _ = vb.merge(vb.Response(M, ra, tr, ts), vb.Boxes([[c] for c in range(32)], False), mode="repro")
        self.assertEqual(len(got), 32)
        self.assertEqual(steps, [])

    def test_response_matches_h2_stats(self):
        rng = np.random.default_rng(7)
        M = rng.uniform(0, 100, (32, 32))
        ra, tr, ts = M.sum(0) + 50, M.sum(1) + 70, rng.uniform(500, 3000, 32)
        a, b = h2.Stats(M, ra, tr, ts, np.ones(32)), vb.Response(M, ra, tr, ts)
        for cells in ([0], [3, 7], [0, 1, 2, 3], list(range(16))):
            x, y = a.of(cells), b.of(cells)
            self.assertAlmostEqual(x["purity"], y["purity"], places=14)
            self.assertAlmostEqual(x["stability"], y["diagonal_fraction"], places=14)
            self.assertEqual(x["reported"], y["supported"])


class Mask(unittest.TestCase):
    def setUp(self):
        idx = vb.fine_axis_index()
        self.base = np.where(OMEGA, idx["pt"], -1)       # a C1-like base: the p_T fine bin, inside Ω only

    def events(self, gen, reco, pr=True, pt=True, wt=1.0, wr=1.0):
        n = len(gen)
        return vb.Response.from_events(np.asarray(gen), np.asarray(reco), np.full(n, pr), np.full(n, pt),
                                       np.full(n, wt), np.full(n, wr), self.base, 14)

    def test_truth_outside_omega_enters_reco_all_only(self):
        r = self.events([point(3, 2, 2, 6, 1)], [point(3, 2, 2, 2, 1)], wr=5.0)   # truth: pT<0.7, q3>=2, W<1.8
        self.assertEqual(r.reco_all[3], 5.0)
        self.assertEqual(r.M.sum(), 0.0)
        self.assertEqual(r.truth_reco.sum(), 0.0)
        self.assertEqual(r.of([3])["in_share"], 1.0)

    def test_reco_outside_omega_enters_truth_reco_only(self):
        r = self.events([point(3, 2, 2, 2, 1)], [point(3, 2, 2, 6, 1)], wr=5.0)
        self.assertEqual(r.truth_reco[3], 5.0)
        self.assertEqual(r.M.sum(), 0.0)
        self.assertEqual(r.reco_all.sum(), 0.0)
        self.assertEqual(r.of([3])["out_share"], 1.0)

    def test_shares_count_truth_sel_within_omega_only(self):
        r = self.events([point(3, 2, 2, 2, 1), point(3, 2, 2, 6, 1)], [point(3, 2, 2, 2, 1)] * 2, wt=4.0)
        self.assertEqual(r.truth_sel[3], 4.0)                  # the excluded-region truth is not counted

    def test_truth_reco_needs_pass_reco(self):
        r = self.events([point(3, 2, 2, 2, 1)], [point(3, 2, 2, 2, 1)], pr=False)
        self.assertEqual(r.truth_reco[3], 0.0)
        self.assertEqual(r.truth_sel[3], 1.0)

    def test_in_share_counts_truth_outside_the_base_cells(self):
        gen = [point(2, 2, 2, 2, 1), point(4, 2, 2, 6, 1)]   # truth in p_T bin 2; truth in the excluded region
        reco = [point(4, 2, 2, 2, 1), point(4, 2, 2, 2, 1)]  # both reconstruct in p_T bin 4
        r = self.events(gen, reco)
        self.assertEqual(r.of([4])["in_share"], 0.5)
        self.assertEqual(r.of([2])["out_share"], 0.0)

    def test_same_needs_both_passes(self):
        r = self.events([point(3, 2, 2, 2, 1)], [point(3, 2, 2, 2, 1)], pt=False)
        self.assertEqual(r.M.sum(), 0.0)
        self.assertEqual(r.reco_all[3], 1.0)


class Geometry(unittest.TestCase):
    def test_pz_edge_refused_for_c2(self):
        g = vb.Grid(("pz",), True, False)
        self.assertIsNotNone(g.refused(((vb.PZ_SPLIT - 1, vb.PZ_SPLIT),), 0))
        self.assertIsNone(g.refused(((vb.PZ_SPLIT - 2, vb.PZ_SPLIT - 1),), 0))
        self.assertIsNone(vb.Grid(("pz",), False, False).refused(((vb.PZ_SPLIT - 1, vb.PZ_SPLIT),), 0))

    def test_pz_edge_in_merge(self):
        # bin 5 is low; its union with 6 (across 4.5) would be best, so it must join 4 instead
        n = 16
        M = np.diag(np.full(n, 9000.0))
        M[5, 5], M[5, 6], M[6, 5] = 1000.0, 4000.0, 4000.0
        r = vb.Response(M, np.full(n, 10000.0), np.full(n, 10000.0), np.full(n, 5000.0))
        bins, steps, _ = vb.merge(r, vb.Grid(("pz",), True, False))
        self.assertIn(((4, 5),), bins)
        self.assertTrue(any(x["reason"].startswith("p_par") for s in steps for x in s["refused"]))
        bins_free, _, _ = vb.merge(r, vb.Grid(("pz",), False, False))
        self.assertIn(((5, 6),), bins_free)

    def test_c0_refuses_pz_joins(self):
        self.assertIsNotNone(vb.Boxes([], True).refused((0, 8), 1))
        self.assertIsNone(vb.Boxes([], True).refused((0, 16), 0))

    def test_strip_refused(self):
        g = vb.Grid(("pt", "pz"), True, True, dims=(2, 2))
        self.assertEqual(g.refused(((0, 1), (0, 0)), 0), "full strip (A3.1)")
        r = resp_2d((2, 2), np.full(4, 5000.0))
        r.M[0, 0] = 1000.0                                     # cell (0,0) is low
        bins, steps, flagged = vb.merge(r, g, two_d=True, grid=g)
        self.assertEqual(len(bins), 4)                         # both partners would form full strips
        self.assertEqual(flagged, [0])
        self.assertEqual({x["reason"] for x in steps[0]["refused"]}, {"full strip (A3.1)"})


class A34(unittest.TestCase):
    def test_19_62_19_is_structural(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(3, 2))
        ts = np.zeros((3, 2))
        ts[:, 0] = [19, 62, 19]
        ts[:, 1] = [40, 20, 40]
        fails, _ = vb.structural_failures(resp_2d((3, 2), ts), g)
        self.assertEqual([f["line"] for f in fails], ["row q3[0]"])

    def test_one_cell_above_80_is_structural(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(3, 2))
        ts = np.array([[5, 40], [85, 20], [10, 40]], float)
        fails, _ = vb.structural_failures(resp_2d((3, 2), ts), g)
        self.assertIn("row q3[0]", [f["line"] for f in fails])

    def test_balanced_line_passes_structural(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(3, 2))
        ts = np.array([[30, 40], [40, 20], [30, 40]], float)
        fails, empty = vb.structural_failures(resp_2d((3, 2), ts), g)
        self.assertEqual(fails, [])
        self.assertEqual(empty, [])

    def test_empty_line_listed_not_failed(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(3, 2))
        ts = np.array([[30, 0], [40, 0], [30, 0]], float)
        fails, empty = vb.structural_failures(resp_2d((3, 2), ts), g)
        self.assertEqual(empty, ["row q3[1]"])
        self.assertTrue(all(f["line"] != "row q3[1]" for f in fails))

    def test_veto_refuses_largest_above_80(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(3, 2))
        ts = np.array([[45, 30], [40, 40], [15, 30]], float)   # row q3[0]: 45/40/15
        r = resp_2d((3, 2), ts)
        bin_of = {c: c for c in range(6)}
        u = g.cells(((0, 1), (0, 0)))                          # (0,0)+(1,0): 85 % of row q3[0]
        self.assertTrue(vb.veto(r, g, vb.lines(g), bin_of, u, -1))
        u2 = g.cells(((1, 2), (0, 0)))                         # (1,0)+(2,0): 55 %
        self.assertFalse(vb.veto(r, g, vb.lines(g), bin_of, u2, -1))

    def test_veto_in_merge(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(3, 2))
        ts = np.array([[45, 30], [40, 40], [15, 30]], float) * 100
        r = resp_2d((3, 2), ts)
        r.M[0, 0] = 1000.0                                     # cell (0,0) low; its x partner would make 85 %
        bins, steps, _ = vb.merge(r, g, two_d=True, grid=g)
        self.assertTrue(any(x["reason"] == "80 % veto (A3.4)" for s in steps for x in s["refused"]))
        self.assertNotIn(((0, 1), (0, 0)), bins)

    def test_largest_share_never_falls_under_joins(self):
        rng = np.random.default_rng(11)
        g = vb.Grid(("eavail", "q3"), False, False, dims=(5, 4))
        r = resp_2d((5, 4), rng.uniform(0, 10, 20))
        for _ in range(30):
            bins = g.start()
            prev = None
            while True:
                bin_of = {c: g.first(b) for b in bins for c in g.cells(b)}
                now = [vb.piece_shares(r, cells, bin_of)[1][0] for _, cells in vb.lines(g)]
                if prev is not None:
                    self.assertTrue(all(b >= a - 1e-15 for a, b in zip(prev, now)))
                prev = now
                pairs = [(i, j, k) for i in range(len(bins)) for j in range(len(bins))
                         if i < j and (k := g.join_axis(bins[i], bins[j])) is not None]
                if not pairs:
                    break
                i, j, k = pairs[rng.integers(len(pairs))]
                u = g.union(bins[i], bins[j], k)
                bins = [b for t, b in enumerate(bins) if t not in (i, j)] + [u]

    def test_veto_refuses_a_push_from_exactly_80(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(3, 2))
        r = resp_2d((3, 2), np.array([[80, 40], [10, 40], [10, 40]], float))   # row q3[0]: 80/10/10, largest 0.8
        bin_of = {c: c for c in range(6)}
        self.assertTrue(vb.veto(r, g, vb.lines(g), bin_of, g.cells(((0, 1), (0, 0))), -1))   # 0.8 -> 0.9

    def test_line_already_above_80_does_not_veto(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(3, 2))
        r = resp_2d((3, 2), np.array([[85, 40], [10, 40], [5, 40]], float))   # row q3[0] starts at 0.85
        bin_of = {c: c for c in range(6)}
        self.assertFalse(vb.veto(r, g, vb.lines(g), bin_of, g.cells(((1, 2), (0, 0))), -1))
        fails, _ = vb.structural_failures(r, g)
        self.assertIn("row q3[0]", [f["line"] for f in fails])

    def test_70_10_10_10_fails_the_final_check(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(4, 1))
        r = resp_2d((4, 1), [70, 10, 10, 10])
        bin_of = {c: c for c in range(4)}                       # four pieces: largest 0.7 (veto passes)
        self.assertLessEqual(vb.piece_shares(r, [0, 1, 2, 3], bin_of)[1][0], vb.VETO)
        fails = vb.final_two_piece_failures(r, g, bin_of)
        self.assertIn("row q3[0]", [f["line"] for f in fails])

    def test_two_pieces_pass_the_final_check(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(4, 1))
        r = resp_2d((4, 1), [40, 30, 20, 10])
        bin_of = {0: 0, 1: 0, 2: 2, 3: 2}                       # 70 / 30 for the row; columns are single cells
        fails = vb.final_two_piece_failures(r, g, bin_of)
        self.assertNotIn("row q3[0]", [f["line"] for f in fails])


class Criterion(unittest.TestCase):
    def test_low_uses_the_smaller_fraction(self):
        # bin 1: purity 0.9 but diagonal fraction 0.45, so it is low (A4.1) and is merged once (the union is 0.6)
        M = np.diag([9000.0, 9000.0, 9000.0])
        tr = np.array([1e4, 2e4, 1e4])
        r = vb.Response(M, np.full(3, 1e4), tr, np.full(3, 5000.0))
        bins, steps, _ = vb.merge(r, vb.Grid(("pt",), False, False, dims=(3,)))
        self.assertEqual(len(bins), 2)
        self.assertEqual(steps[0]["bin"], {"pt": [S1.FINE["pt"][1], S1.FINE["pt"][2]]})

    def test_union_is_chosen_by_the_smaller_fraction(self):
        # bin 1 is low; union (0,1) has purity 0.892 and diagonal fraction 0.582, union (1,2) has 0.707 and 0.707:
        # A4.2 takes the union with the higher min, (1,2)
        M = np.diag([9000.0, 900.0, 9000.0])
        r = vb.Response(M, np.array([9100.0, 2000.0, 12000.0]), np.array([15000.0, 2000.0, 12000.0]),
                        np.full(3, 5000.0))
        bins, _, _ = vb.merge(r, vb.Grid(("pt",), False, False, dims=(3,)))
        self.assertIn(((1, 2),), bins)

    def test_unsupported_bin_is_low_in_candidate_mode(self):
        M = np.diag([9000.0, 900.0, 9000.0])
        ra = np.array([1e4, 999.0, 1e4])
        ra[1] = 1000.0 - 1.0
        M[1, 1] = 0.9 * ra[1]
        r = vb.Response(M, ra, np.array([1e4, 0.9 * ra[1] / 0.9, 1e4]), np.full(3, 5000.0))
        self.assertFalse(r.of([1])["supported"])
        bins, _, _ = vb.merge(r, vb.Grid(("pt",), False, False, dims=(3,)))
        self.assertEqual(len(bins), 2)

    def test_veto_allows_exactly_80(self):
        g = vb.Grid(("eavail", "q3"), False, True, dims=(3, 2))
        r = resp_2d((3, 2), np.array([[40, 40], [40, 40], [20, 40]], float))   # row q3[0]: 40/40/20
        bin_of = {c: c for c in range(6)}
        self.assertFalse(vb.veto(r, g, vb.lines(g), bin_of, g.cells(((0, 1), (0, 0))), -1))   # exactly 0.8


class Outcomes(unittest.TestCase):
    def one_bin(self, purity=0.9, diag=0.9, ra=5000.0, ts=5000.0):
        same = purity * ra
        tr = same / diag
        return vb.Response(np.array([[same]]), np.array([ra]), np.array([tr]), np.array([ts]))

    def t3(self, **kw):
        g = vb.Grid(("pt",), False, False, dims=(1,))
        out = vb.outcome(self.one_bin(**kw), g, [((0, 0),)], "C1", [], [])
        return [x for o in out if "T3" in o for x in o["T3"][0]["failing"]]

    def test_each_t3_quantity(self):
        self.assertEqual(self.t3(purity=0.49), ["purity"])
        self.assertEqual(self.t3(diag=0.49), ["diagonal fraction"])
        self.assertEqual(self.t3(ra=999.0), ["reco_all"])
        self.assertEqual(self.t3(ts=999.0), ["truth_sel"])
        self.assertEqual(self.t3(), [])

    def test_floor_1d(self):
        g = vb.Grid(("pt",), False, False, dims=(2,))
        r = vb.Response(np.diag([9000.0, 9000.0]), np.full(2, 1e4), np.full(2, 1e4), np.full(2, 5000.0))
        out = vb.outcome(r, g, [((0, 0),), ((1, 1),)], "C1", [], [])
        self.assertEqual(out[0]["T2"], "minimum")

    def test_floor_c0_per_side(self):
        geom = vb.Boxes(vb.c0_start(H2DEF), True)
        bins = geom.start()                                     # the 16 R-cells: 8 on each side of 4.5
        r = vb.Response(np.diag(np.full(32, 9000.0)), np.full(32, 1e4), np.full(32, 1e4), np.full(32, 5000.0))
        self.assertFalse(any("T2" in o for o in vb.outcome(r, geom, bins, "C0", [], [])))
        below = [b for b in bins if geom.box_of(b)[1] == (0,)]
        above = [b for b in bins if geom.box_of(b)[1] == (1,)]
        out = vb.outcome(r, geom, below[:3] + above, "C0", [], [])
        self.assertEqual(out[0]["T2"], "minimum")

    def test_c7_landmarks(self):
        g = vb.Grid(("eavail", "q3"), False, True)
        k = S1.FINE["q3"]
        bins = [((0, 6), (0, 3)), ((0, 6), (4, 4)), ((0, 6), (5, 6))]   # q3 edges at 0.8 and 1.2
        lm = vb.landmarks_c7(g, bins)
        self.assertEqual([x["q3_edge"] for x in lm], [k[4], k[5]])
        self.assertEqual(lm[0]["vs_0.8"], "equal")
        self.assertEqual(lm[1]["vs_1.2"], "equal")


class Weights(unittest.TestCase):
    def arrays(self, wt, wr, gen=None):
        gen = gen or [point(3, 2, 2, 2, 1)]
        return {"MCgen": np.asarray(gen), "MCreco": np.asarray(gen), "pass_reco": np.ones(len(gen), bool),
                "pass_truth": np.ones(len(gen), bool), "w_truth": np.asarray(wt, float), "w_reco": np.asarray(wr, float)}

    def test_negative_w_truth_stops(self):
        with self.assertRaises(vb.Stop):
            vb.check_weights(self.arrays([-1.0], [1.0]), OMEGA)

    def test_small_negative_w_truth_stops(self):
        with self.assertRaises(vb.Stop):
            vb.check_weights(self.arrays([-0.5], [1.0]), OMEGA)

    def test_nonfinite_w_truth_stops(self):
        with self.assertRaises(vb.Stop):
            vb.check_weights(self.arrays([np.nan], [1.0]), OMEGA)

    def test_nonfinite_w_reco_stops(self):
        with self.assertRaises(vb.Stop):
            vb.check_weights(self.arrays([1.0], [np.inf]), OMEGA)

    def test_outside_omega_is_not_counted(self):
        vb.check_weights(self.arrays([-1.0], [1.0], gen=[point(3, 2, 2, 6, 1)]), OMEGA)


class EndToEnd(unittest.TestCase):
    def test_build_c3_and_c0(self):
        rng = np.random.default_rng(3)
        n = 6000
        idx = [rng.integers(0, vb.NFINE[a], n) for a in vb.AXES]
        gen = np.array([[centre(a, i[r]) for a, i in zip(vb.AXES, idx)] for r in range(n)])
        reco = gen.copy()
        arrays = {"MCgen": gen, "MCreco": reco, "pass_reco": np.ones(n, bool), "pass_truth": np.ones(n, bool),
                  "w_truth": np.full(n, 3.0), "w_reco": np.full(n, 3.0)}
        rec, fmap = vb.build("C3", arrays, OMEGA, H2_OF_FINE, H2DEF)
        self.assertGreaterEqual(rec["n_bins"], 1)
        rec2, fmap2 = vb.build("C3", arrays, OMEGA, H2_OF_FINE, H2DEF)
        self.assertEqual(rec["fine_map_sha256_int32le"], rec2["fine_map_sha256_int32le"])
        self.assertTrue(np.all(fmap[~OMEGA] == -1))
        json.dumps(rec, allow_nan=False)
        rec0, _ = vb.build("C0", arrays, OMEGA, H2_OF_FINE, H2DEF)
        self.assertLessEqual(rec0["n_bins"], 16)


if __name__ == "__main__":
    unittest.main(verbosity=2)
