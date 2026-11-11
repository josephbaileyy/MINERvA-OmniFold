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


# ------------------------------------------------------------------------------------------- audit V1, V2, V3
def events_on(cells, fixed, axes, weight_of):
    """One event per cell of a candidate's axes, at cell centres, reco = gen; the other axes at the fixed indices."""
    rows = []
    w = []
    for idx in cells:
        ix = dict(fixed)
        ix.update(dict(zip(axes, idx)))
        rows.append(point(ix["pt"], ix["pz"], ix["eavail"], ix["q3"], ix["W"]))
        w.append(weight_of(idx))
    rows, w = np.asarray(rows), np.asarray(w, float)
    keep = w > 0
    rows, w = rows[keep], w[keep]
    n = len(w)
    return {"MCgen": rows, "MCreco": rows.copy(), "pass_reco": np.ones(n, bool), "pass_truth": np.ones(n, bool),
            "w_truth": w, "w_reco": w.copy()}


FIX = {"pt": 9, "pz": 8, "eavail": 2, "q3": 3, "W": 3}     # pT >= 0.7 and W >= 1.8: inside Ω on every axis


def c7_arrays(row_j, row_weights, empty_row=None):
    def wt(idx):
        e, q = idx
        if q == empty_row:
            return 0.0
        return row_weights[e] if q == row_j else 2000.0
    return events_on([(e, q) for e in range(7) for q in range(7)], FIX, ("eavail", "q3"), wt)


def synthetic_h2def(arrays):
    stats = h2.stats_from_rows(arrays)
    boxes, steps, flagged = h2.merge(stats)
    reported = {tuple(b): stats.of(b)["reported"] for b in boxes}
    lut, _, sha = h2.fine_map(boxes, reported)
    return {"tau": 0.1, "reporting_cells": [{"h2_cells": b} for b in boxes if reported[tuple(b)]],
            "unreported_boxes": [b for b in boxes if not reported[tuple(b)]], "flagged_no_partner": flagged,
            "h2_to_reporting_cell": lut.tolist(), "fine_map_sha256_int32le": sha, "steps": steps}


def random_arrays(seed, n=60000):
    rng = np.random.default_rng(seed)
    idx = np.stack([rng.integers(0, vb.NFINE[a], n) for a in vb.AXES], axis=1)
    gen = np.array([[centre(a, i) for a, i in zip(vb.AXES, r)] for r in idx])
    reco = gen.copy()
    box25 = H2_OF_FINE[np.ravel_multi_index(idx.T, tuple(vb.NFINE[a] for a in vb.AXES))] == 25
    into25 = ~box25 & (rng.uniform(size=n) < 0.3)
    reco[into25] = point(9, 8, 1, 2, 3)                     # 30 % of other events reconstruct in box 25: its purity is
    reco[box25] = gen[rng.permutation(n)][box25]            # far below 0.1, so the H2 rule merges it
    return {"MCgen": gen, "MCreco": reco, "pass_reco": np.ones(n, bool), "pass_truth": np.ones(n, bool),
            "w_truth": np.full(n, 3.0), "w_reco": np.full(n, 3.0)}


class Reproduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arrays = random_arrays(5)
        cls.h2def = synthetic_h2def(cls.arrays)
        h2_of_fine, _ = S1.coarse_map(S1.H2_EDGES)
        cls.h2_of_fine = h2_of_fine

    def test_reproduces_the_synthetic_record(self):
        self.assertTrue(self.h2def["steps"], "the fixture must make the H2 rule merge")
        rec = vb.reproduce(self.arrays, self.h2def, self.h2_of_fine)
        self.assertTrue(all(rec["checks"].values()))

    def test_each_mismatch_stops(self):
        for field, bad in (("fine_map_sha256_int32le", "0" * 64), ("flagged_no_partner", [99]),
                           ("unreported_boxes", [[0]]), ("reporting_cells", [{"h2_cells": [0]}]), ("tau", 0.2)):
            d = dict(self.h2def)
            d[field] = bad
            with self.assertRaises(vb.Stop, msg=field):
                vb.reproduce(self.arrays, d, self.h2_of_fine)


class Main(unittest.TestCase):
    """main() end to end on a synthetic npz and a synthetic H2 record, with the module's pins patched to them."""

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.saved = (vb.NPZ_SHA256, vb.H2_DEF, vb.H2_DEF_SHA256)

    def tearDown(self):
        vb.NPZ_SHA256, vb.H2_DEF, vb.H2_DEF_SHA256 = self.saved
        self.tmp.cleanup()

    def prepare(self, arrays, h2def=None):
        import hashlib
        npz = self.d / "in.npz"
        np.savez(npz, **arrays)
        h2p = self.d / "h2.json"
        h2p.write_text(json.dumps(h2def or synthetic_h2def(arrays)))
        vb.NPZ_SHA256 = hashlib.sha256(npz.read_bytes()).hexdigest()
        vb.H2_DEF, vb.H2_DEF_SHA256 = h2p, hashlib.sha256(h2p.read_bytes()).hexdigest()
        return npz

    def test_writes_reproduction_and_candidates_with_provenance(self):
        npz = self.prepare(random_arrays(6))
        out = self.d / "out"
        self.assertEqual(vb.main(["--npz", str(npz), "--out", str(out), "--candidates", "C3,C0"]), 0)
        rec = json.loads((out / "binning_C3.json").read_text())
        self.assertEqual(rec["inputs"]["npz_sha256"], vb.NPZ_SHA256)
        self.assertEqual(rec["inputs"]["code"]["vhr_binning.py"], vb.file_sha256(vb.__file__))
        self.assertTrue(json.loads((out / "reproduction_R00-R15.json").read_text())["checks"]["fine map"])

    def test_failed_reproduction_writes_nothing(self):
        arrays = random_arrays(6)
        d = synthetic_h2def(arrays)
        d["flagged_no_partner"] = [31]
        npz = self.prepare(arrays, d)
        out = self.d / "out"
        self.assertEqual(vb.main(["--npz", str(npz), "--out", str(out)]), 2)
        self.assertFalse(out.exists())

    def test_negative_weight_stops_main(self):
        arrays = random_arrays(6)
        arrays["w_truth"][0] = -1.0
        npz = self.prepare(arrays, synthetic_h2def(random_arrays(6)))
        self.assertEqual(vb.main(["--npz", str(npz), "--out", str(self.d / "out")]), 2)

    def test_pins_refuse(self):
        npz = self.prepare(random_arrays(6))
        with self.assertRaises(vb.Stop):
            vb.load_mc(npz, expect="0" * 64)
        with self.assertRaises(vb.Stop):
            vb.h2_definition(expect="0" * 64)
        bad = dict(H2DEF)
        bad["h2_to_reporting_cell"] = list(bad["h2_to_reporting_cell"])
        bad["h2_to_reporting_cell"][2] = 0
        with self.assertRaises(vb.Stop):
            vb.omega_mask(bad)


class BuildLevel(unittest.TestCase):
    def test_candidate_table(self):
        self.assertEqual(vb.CANDIDATES, {
            "C1": (("pt",), False, False), "C2": (("pz",), True, False), "C3": (("eavail",), False, False),
            "C4": (("q3",), False, False), "C5": (("W",), False, False), "C6": (("pt", "pz"), True, True),
            "C7": (("eavail", "q3"), False, True), "C8": (("eavail", "W"), False, False)})

    def test_c7_structural_ends_at_t2(self):
        rec, _ = vb.build("C7", c7_arrays(2, [500, 500, 500, 7000, 500, 500, 500]), OMEGA, H2_OF_FINE, H2DEF)
        t2 = [o for o in rec["outcome"] if o.get("T2") == "two-dimensional resolution: structural"]
        self.assertTrue(t2)
        self.assertIn("row q3[2]", [x["line"] for x in t2[0]["lines"]])
        self.assertEqual(rec["status"], "terminal (binning alone)")

    def test_c7_final_failure_ends_at_t2(self):
        rec, _ = vb.build("C7", c7_arrays(2, [6500, 500, 500, 500, 500, 500, 1000]), OMEGA, H2_OF_FINE, H2DEF)
        struct = [x["line"] for o in rec["outcome"] if o.get("T2") == "two-dimensional resolution: structural"
                  for x in o["lines"]]
        final = [x["line"] for o in rec["outcome"] if o.get("T2") == "two-dimensional resolution: final"
                 for x in o["lines"]]
        self.assertNotIn("row q3[2]", struct)
        self.assertIn("row q3[2]", final)
        self.assertEqual(rec["status"], "terminal (binning alone)")

    def test_c7_empty_row_is_exempt_and_guarded(self):
        rec, _ = vb.build("C7", c7_arrays(2, [2000] * 7, empty_row=5), OMEGA, H2_OF_FINE, H2DEF)
        self.assertIn("row q3[5]", rec["empty_lines"])
        final = [x["line"] for o in rec["outcome"] if o.get("T2") == "two-dimensional resolution: final"
                 for x in o["lines"]]
        self.assertNotIn("row q3[5]", final)

    def test_c2_keeps_the_pz_edge(self):
        def wt(idx):
            return 500.0 if idx[0] == 5 else 5000.0
        arr = events_on([(z,) for z in range(16)], FIX, ("pz",), wt)
        mig = events_on([(3,)], FIX, ("pz",), lambda i: 3000.0)       # truth in p_par bin 3, reco in bin 4
        mig["MCreco"] = np.asarray([point(FIX["pt"], 4, FIX["eavail"], FIX["q3"], FIX["W"])])
        arr = {k: np.concatenate([arr[k], mig[k]]) for k in arr}
        rec, _ = vb.build("C2", arr, OMEGA, H2_OF_FINE, H2DEF)
        edges = [b["pz"] for b in rec["bins"]]
        self.assertIn([S1.FINE["pz"][4], S1.FINE["pz"][6]], edges)
        self.assertFalse(any(lo < 4.5 < hi for lo, hi in edges))

    def test_c6_keeps_the_pz_edge(self):
        arr = events_on([(t, z) for t in range(14) for z in range(16)], FIX, ("pt", "pz"),
                        lambda i: 0.0 if (i[0] >= 10 and i[1] <= 3) else (300.0 if i[1] in (5, 6) else 3000.0))
        rec, _ = vb.build("C6", arr, OMEGA, H2_OF_FINE, H2DEF)
        self.assertFalse(any(lo < 4.5 < hi for lo, hi in (b["pz"] for b in rec["bins"])))

    def test_2d_floor(self):
        g = vb.Grid(("eavail", "W"), False, False, dims=(6, 1))
        r = vb.Response(np.diag(np.full(6, 9000.0)), np.full(6, 1e4), np.full(6, 1e4), np.full(6, 5000.0))
        five = [((i, i), (0, 0)) for i in range(4)] + [((4, 5), (0, 0))]
        six = [((i, i), (0, 0)) for i in range(6)]
        self.assertEqual(vb.outcome(r, g, five, "C8", [], [])[0]["T2"], "minimum")
        self.assertEqual(vb.outcome(r, g, six, "C8", [], []), [])

    def test_c0_mask(self):
        rec, fmap = vb.build("C0", random_arrays(7, n=20000), OMEGA, H2_OF_FINE, H2DEF)
        self.assertTrue(np.all(fmap[~OMEGA] == -1))
        self.assertEqual(rec["domain"]["h2_boxes"], [2, 6, 10, 14])

    def test_c0_in_share_counts_truth_outside_omega(self):
        # audit w3: the in share of C0's bin holding H2 box 25 equals the reco weight there whose truth is outside Ω
        arr = random_arrays(7, n=20000)
        rec, _ = vb.build("C0", arr, OMEGA, H2_OF_FINE, H2DEF)
        b = next(x for x in rec["bins"] if 25 in x["h2_cells"])
        ft, fr = S1.fine_index(arr["MCgen"]), S1.fine_index(arr["MCreco"])
        reco_in = (fr >= 0) & np.isin(H2_OF_FINE[np.maximum(fr, 0)], b["h2_cells"]) & arr["pass_reco"]
        truth_out = (ft < 0) | ~OMEGA[np.maximum(ft, 0)] | ~arr["pass_truth"]
        want = arr["w_reco"][reco_in & truth_out].sum() / arr["w_reco"][reco_in].sum()
        self.assertGreater(want, 0.0)
        self.assertAlmostEqual(b["in_share"], want, places=12)

    def test_excluded_region_named(self):
        self.assertEqual(vb.excluded_region(H2DEF)["region"], {"pt": [0.0, 0.7], "q3": [2.0, 100.0], "W": [0.0, 1.8]})

    def test_w_reco_on_a_truth_side_row_stops(self):
        a = {"MCgen": np.asarray([point(3, 2, 2, 2, 1)]), "MCreco": np.asarray([point(3, 2, 2, 6, 1)]),
             "pass_reco": np.ones(1, bool), "pass_truth": np.ones(1, bool), "w_truth": np.ones(1),
             "w_reco": np.asarray([np.inf])}
        with self.assertRaises(vb.Stop):
            vb.check_weights(a, OMEGA)


class TieBreaks(unittest.TestCase):
    """A4.2 (audit V3)."""

    @staticmethod
    def line(same, ra, tr):
        return vb.Response(np.diag(np.asarray(same, float)), np.asarray(ra, float), np.asarray(tr, float),
                           np.full(len(same), 5000.0))

    def test_equal_lows_take_the_lowest_first_index(self):
        # bins 1 and 2 are low at the same value 0.4; bin 1 goes first, joins 0; then bin 2 joins 3
        r = self.line([900, 400, 400, 5000], [1000, 421, 421, 5263], [1000, 1000, 1000, 5100])
        bins, _, _ = vb.merge(r, vb.Grid(("pt",), False, False, dims=(4,)))
        self.assertEqual(bins, [((0, 1),), ((2, 3),)])

    def test_the_lowest_low_goes_first(self):
        # bin 2 (0.40) goes before bin 1 (0.45): bin 2 joins 3, then bin 1 joins (2,3)
        r = self.line([900, 450, 400, 5000], [1000, 474, 421, 5263], [1000, 1000, 1000, 5100])
        bins, _, _ = vb.merge(r, vb.Grid(("pt",), False, False, dims=(4,)))
        self.assertEqual(bins, [((0, 0),), ((1, 3),)])

    def test_partner_ties_take_the_lowest_axis_then_first_index(self):
        g = vb.Grid(("eavail", "W"), False, False, dims=(3, 3))
        n = 9
        same = np.full(n, 5000.0)
        ra = same.copy()
        ra[4] = same[4] = 500.0                                  # the centre is unsupported; every union is pure
        r = vb.Response(np.diag(same), ra, ra.copy(), ra.copy())
        bins, _, _ = vb.merge(r, g)
        self.assertIn(((0, 1), (1, 1)), bins)                    # axis 0, the lower first index

    def test_value_zero_ties_on_empty_corners(self):
        # the empty corners make many bins tie at value 0 (reco_all = 0); the tie-breaks fix the fine map
        c8 = events_on([(e, w) for e in range(7) for w in range(6)], FIX, ("eavail", "W"),
                       lambda i: 0.0 if (i[0] >= 3 and i[1] >= 2) else 2000.0)
        rec8, _ = vb.build("C8", c8, OMEGA, H2_OF_FINE, H2DEF)
        c6 = events_on([(t, z) for t in range(14) for z in range(16)], FIX, ("pt", "pz"),
                       lambda i: 0.0 if (i[0] >= 10 and i[1] <= 3) else 3000.0)
        rec6, _ = vb.build("C6", c6, OMEGA, H2_OF_FINE, H2DEF)
        self.assertEqual((rec8["n_bins"], rec8["fine_map_sha256_int32le"][:16]), PIN_C8)
        self.assertEqual((rec6["n_bins"], rec6["fine_map_sha256_int32le"][:16]), PIN_C6)


PIN_C8 = (26, "4b608bf34eb08ff6")     # the head's binning, pinned: a changed tie-break changes it (audit V3)
PIN_C6 = (208, "8184cc2e9bfcf48e")    # equal to coverage-5b-audit's head value for an empty-corner C6


if __name__ == "__main__":
    unittest.main(verbosity=2)
