"""fd_1b_c2 (FD-1B-STAGED-ADDENDUM-A2-1.md): #724's gate, the reading through cov2d's code, the draw law, 1B's
graded truth from fine sums, and the calibration's outputs. Every rule is tested in the direction it acts and the
other."""
import itertools
import math
import sys
import unittest
from unittest import mock
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fd_1b_c2 as c2  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_toys as toys  # noqa: E402
import s5n_pseudo  # noqa: E402
from xsec_nd import extract_cross_section_nd  # noqa: E402

cp2, cov2d = c2.cp2, c2.cov2d


def ratios(beyond=0, dev=0.25, base=1.0):
    r = np.full(c2.N_CELLS, base)
    r[:beyond] = 1.0 + dev
    return r


class Gate(unittest.TestCase):
    def test_the_constants_are_joseph_s(self):
        self.assertEqual((c2.GATE_K, c2.GATE_DEV, c2.GATE_LOGMEAN, c2.GATE_MAX), (2, 0.20, 0.07, 0.35))
        self.assertEqual((c2.SD_MULT_LOGMEAN, c2.SD_MULT_CELL, c2.UNION_LIMIT), (3.5, 4.3, 0.01))

    def test_i_allows_two_cells_and_stops_at_three(self):
        r2 = np.full(16, 0.995)
        r2[:2] = 1.25
        r3 = r2.copy()
        r3[2] = 1.25
        self.assertTrue(c2.gate_724(r2)["i"])
        self.assertFalse(c2.gate_724(r3)["i"])
        edge = np.ones(16)
        edge[:3] = 1.0 + c2.GATE_DEV              # exactly 0.20 is not beyond
        self.assertEqual(c2.gate_724(edge)["cells_beyond"], 0)
        edge[:3] = np.nextafter(1.0 + c2.GATE_DEV, 2.0)
        self.assertEqual(c2.gate_724(edge)["cells_beyond"], 3)

    def test_ii_at_and_past_its_bound(self):
        at = np.full(16, math.exp(0.07 * (1 - 1e-12)))
        past = np.full(16, math.exp(0.0701))
        self.assertTrue(c2.gate_724(at)["ii"])
        self.assertFalse(c2.gate_724(past)["ii"])
        self.assertFalse(c2.gate_724(1 / past)["ii"])
        self.assertFalse(c2.gate_724(past)["passes"])

    def test_iii_at_and_past_its_bound(self):
        at = 1.0 + c2.GATE_MAX
        while at - 1.0 > c2.GATE_MAX:            # the largest ratio whose |r - 1| is <= 0.35 in float
            at = np.nextafter(at, 0.0)
        r = np.ones(16)
        r[0] = at
        self.assertTrue(c2.gate_724(r)["iii"])
        r[0] = np.nextafter(at, 2.0)
        self.assertFalse(c2.gate_724(r)["iii"])
        self.assertFalse(c2.gate_724(r)["passes"])
        r[0] = 1.0 - c2.GATE_MAX - 1e-9
        self.assertFalse(c2.gate_724(r)["iii"])

    def test_ii_exactly_at_its_bound_passes(self):
        """A mean log of exactly 0.07 is reachable (15 cells at exp(0.07), the 16th searched): it passes (ii)."""
        r = np.full(16, math.exp(0.07))
        x = r[15]
        for _ in range(2500):
            x = np.nextafter(x, 0)
        for _ in range(5000):
            r[15] = x
            if np.mean(np.log(r)) == c2.GATE_LOGMEAN:
                break
            x = np.nextafter(x, 2)
        self.assertEqual(np.mean(np.log(r)), c2.GATE_LOGMEAN)
        self.assertTrue(c2.gate_724(r)["ii"])

    def test_iii_exactly_at_its_bound_passes(self):
        r = np.ones(16)
        r[0] = 0.65                                           # 1 - 0.65 is exactly the double 0.35 (Sterbenz)
        self.assertEqual(abs(r[0] - 1.0), c2.GATE_MAX)
        self.assertTrue(c2.gate_724(r)["iii"])

    def test_i_at_exactly_0_20_is_unreachable(self):
        """The receipt's one equivalent mutant ((i) at >= 0.20): no double r has |r - 1| == 0.20 (r - 1 is exact
        for r in [0.5, 2], and neither 1 + 0.2 nor 1 - 0.2 is representable as such), so > and >= agree on every
        input. Shown on the doubles within 10,000 ulps of 1.2 and of 0.8."""
        for c in (1.2, 0.8):
            r = c
            for _ in range(10_000):
                r = np.nextafter(r, 0)
            for _ in range(20_000):
                self.assertNotEqual(abs(r - 1.0), c2.GATE_DEV)
                r = np.nextafter(r, 2)

    def test_passes_only_when_all_three_hold(self):
        self.assertTrue(c2.gate_724(np.ones(16))["passes"])
        self.assertTrue(c2.gate_724(ratios(2, 0.3, 0.98))["passes"])

    def test_refuses_what_it_is_not_defined_on(self):
        for bad in (np.ones(15), np.r_[np.ones(15), np.nan], np.r_[np.ones(15), 0.0], np.r_[np.ones(15), np.inf]):
            with self.assertRaises(c2.Refusal):
                c2.gate_724(bad)


def record(med, p90, vr, worst, cells=16):
    sig = {"abs_median": list(med), "abs_p90": list(p90)}
    return {"vi": {"largest_cell_unmatched_share": worst},
            "b": {"T": {"option_1": {"sigma_Q": sig}, "variance_ratio": {k: list(v) for k, v in vr.items()}}}}


def grid(cells=16):
    """Records crossing every edge of the reading: medians and p90s at each threshold's two sides and in shares
    either side of each share rule, each composition's gate passing and failing, and the mismatch bounded or not."""
    med_levels = [0.1, cp2.R1_MEDIAN, np.nextafter(cp2.R1_MEDIAN, 1), 0.35, cp2.OPT3_MEDIAN, 0.8]
    p90_levels = [0.3, cp2.R1_P90, np.nextafter(cp2.R1_P90, 1), 0.5, cp2.POS_P90, np.nextafter(cp2.POS_P90, 1)]
    counts = [0, 1, 2, 3, 4, cells]
    vr_pass, vr_fail = np.ones(cells), np.r_[np.full(2, 1.5), np.ones(cells - 2)]
    for ml, mn, pl, pn, gc, gm, worst in itertools.product(med_levels, counts, p90_levels, counts,
                                                          (True, False), (True, False),
                                                          (None, 0.01, cp2.MISMATCH_BOUND, 0.06)):
        med = np.r_[np.full(mn, ml), np.full(cells - mn, 0.05)]
        p90 = np.r_[np.full(pn, pl), np.full(cells - pn, 0.1)]
        vr = {"first_order": vr_pass, c2.CLIPPED: vr_pass if gc else vr_fail,
              "multiplicative": vr_pass if gm else vr_fail}
        yield record(med, p90, vr, worst, cells)


class Reading(unittest.TestCase):
    def test_equals_clip_probe2_under_c2s_gate(self):
        n = 0
        for rec in grid():
            self.assertEqual(c2.reading_1b(rec), cp2.reading(rec))
            n += 1
        self.assertGreater(n, 10_000)

    def test_option_1_is_q1_and_bounded_under_either_gate(self):
        """The audit's identity: reads option (1) <=> q1 and the mismatch bounded, so no other gate can move it."""
        for gates in (None, c2.GATES_1B):
            for rec in grid():
                got = c2.reading_1b(rec, gates)["T"]
                self.assertEqual(got["reads"] == "option (1)", got["option_1_qualifies"] and got["mismatch_bounded"])

    def test_1b_gate_acts_on_the_clipped_ratio(self):
        med, p90 = np.full(16, 0.05), np.full(16, 0.1)
        ok = {"first_order": np.ones(16), "multiplicative": np.ones(16)}
        two = ratios(2, 0.25, 1.0)                 # C2's 95 % rule fails it; #724 passes it
        three = ratios(3, 0.25, 1.0)
        rec = record(med, p90, {**ok, c2.CLIPPED: two}, 0.01)
        self.assertEqual(cp2.reading(rec)["T"]["reads"], "no rule of the reading fires")
        self.assertEqual(c2.reading_1b(rec, c2.GATES_1B)["T"]["reads"], "option (1)")
        rec = record(med, p90, {**ok, c2.CLIPPED: three}, 0.01)
        self.assertNotEqual(c2.reading_1b(rec, c2.GATES_1B)["T"]["reads"], "option (1)")

    def test_the_16_cell_counts(self):
        """On 16 cells the reading's shares are: 'every cell' 16, '>= 90 %' 15, '> 10 %' 2 or more, '>= 20 %' 4."""
        ok = {"first_order": np.ones(16), c2.CLIPPED: np.ones(16), "multiplicative": np.ones(16)}
        base_med = np.full(16, 0.05)
        for n_bad, want in ((1, True), (2, False)):        # p90 <= 0.4 in >= 90 %: 15 of 16 pass, 14 fail
            p90 = np.r_[np.full(n_bad, 0.45), np.full(16 - n_bad, 0.1)]
            self.assertEqual(c2.reading_1b(record(base_med, p90, ok, 0.01))["T"]["option_1_qualifies"], want)
        med = np.r_[0.25, np.full(15, 0.05)]                # every cell: one cell above 0.2 fails q1
        self.assertFalse(c2.reading_1b(record(med, np.full(16, 0.1), ok, 0.01))["T"]["option_1_qualifies"])
        for n, want in ((1, False), (2, True)):            # positivity: median > 0.3 in more than 10 %
            med = np.r_[np.full(n, 0.35), np.full(16 - n, 0.05)]
            self.assertEqual(c2.reading_1b(record(med, np.full(16, 0.1), ok, 0.01))["T"]["positivity_preferred"],
                             want)
        fail = {"first_order": np.ones(16), c2.CLIPPED: ratios(3, 0.5), "multiplicative": ratios(3, 0.5)}
        for n, want in ((3, False), (4, True)):            # option (3): median >= 0.7 in >= 20 %, no gate passing
            med = np.r_[np.full(n, 0.75), np.full(16 - n, 0.05)]
            self.assertEqual(c2.reading_1b(record(med, np.full(16, 0.1), fail, 0.01))["T"]["option_3_applies"], want)


class Law(unittest.TestCase):
    def test_band_reference_equals_clip_probe2s_on_cov2ds_layout(self):
        rng = np.random.default_rng(1)
        h = rng.normal(size=(cov2d.N_UNIVERSES, 7))
        w = rng.uniform(0.5, 1.5, cov2d.BANDS[cov2d.FLUX])
        self.assertTrue(np.array_equal(c2.band_reference(h, w, cov2d.ORDER, cov2d.BANDS, cov2d.FLUX),
                                       cp2.band_reference(h, w)))

    def test_band_reference_refuses_a_wrong_row_count(self):
        with self.assertRaises(c2.Refusal):
            c2.band_reference(np.ones((5, 2)), np.ones(100), cov2d.ORDER, cov2d.BANDS, cov2d.FLUX)

    def test_1b_layout_is_s1s_bands_in_draw_order(self):
        order, bands, tags = c2.layout_1b()
        self.assertEqual(len(tags), 175)
        self.assertEqual(len(order), 38)
        self.assertEqual(bands["Flux"], 100)
        p = np.full(100, 0.01)
        groups = {b: [f"{b}_{i}" for i in range(bands[b])] for b in toys.INTERACTION_BANDS}
        col = {t: i for i, t in enumerate(tags)}
        S = c2.selection(c2.calibration_draws("g18", 0, p, groups, n=5), col, bands)
        self.assertTrue(np.all(S.sum(axis=1) == 38))
        with self.assertRaises(c2.Refusal):
            c2.selection([tags[:3]], col, bands)

    def test_the_streams_are_disjoint_from_the_declared_draws(self):
        p = np.full(100, 0.01)
        groups = {b: [f"{b}_{i}" for i in range(2 if b != "2p2h" else 3)] for b in toys.INTERACTION_BANDS}
        a = c2.calibration_draws("g18", 0, p, groups, n=50)
        self.assertEqual(a, c2.calibration_draws("g18", 0, p, groups, n=50))
        self.assertNotEqual(a, c2.calibration_draws("ar23", 0, p, groups, n=50))
        self.assertNotEqual(a, c2.calibration_draws("g18", 1, p, groups, n=50))
        declared = [mc.draw_universes(toys.draw_for_seed(s, p, groups)) for s in range(3_620_000, 3_620_050)]
        self.assertNotEqual(a, declared)
        seeds = [s for t in mc.TOY_SEEDS for s in mc.TOY_SEEDS[t]] + list(mc.STAT_SEED.values())
        self.assertFalse(set(c2.CAL_SEED.values()) & set(seeds))
        self.assertNotEqual(c2.CAL_SALT, 0)       # SeedSequence zero-pads: [a, b] is [a, b, 0] (audit W4)
        two = np.random.default_rng([c2.CAL_SEED["g18"], 0]).random(4)
        self.assertTrue(np.array_equal(two, np.random.default_rng([c2.CAL_SEED["g18"], 0, 0]).random(4)))
        self.assertFalse(np.array_equal(two, np.random.default_rng([c2.CAL_SEED["g18"], 0, c2.CAL_SALT]).random(4)))
        with mock.patch.object(c2, "CAL_SALT", 0), self.assertRaises(c2.Refusal):
            c2.calibration_draws("g18", 0, p, groups, n=1)

    def test_the_count_law_check_is_one_on_average(self):
        """D4's law half on a toy layout: the linear count's ratio averages to 1 within CONTROL_Z SEs."""
        order, bands = ("Flux", "x", "y"), {"Flux": 5, "x": 2, "y": 3}
        tags = [f"{b}_{i}" for b in order for i in range(bands[b])]
        col = {t: i for i, t in enumerate(tags)}
        w = np.array([1.0, 2.0, 1.0, 3.0, 1.0])
        rng = np.random.default_rng(2)
        cvA = rng.uniform(5, 10, 4)
        HA = cvA + rng.normal(0, 1, (len(tags), 4))
        Ucount = np.ones((1, 4))
        ref = c2.band_reference(HA @ Ucount.T, w, order, bands, "Flux")
        out = []
        for s in range(800):
            r = np.random.default_rng([9, s])
            draws = [[f"Flux_{r.choice(5, p=w / w.sum())}", f"x_{r.integers(2)}", f"y_{r.integers(3)}"]
                     for _ in range(300)]
            S = c2.selection(draws, col, bands)
            L = c2.composite_sums(S, {"A": HA, "B": HA, "D": HA}, {"A": cvA, "B": cvA, "D": cvA})["A"] @ Ucount.T
            out.append(np.var(L, axis=0, ddof=1) / ref)
        self.assertTrue(c2.control({"t": np.array(out)})["holds"])
        self.assertFalse(c2.control({"t": np.array(out) * 1.05})["holds"])


class Block(unittest.TestCase):
    def test_c2_block_reads_each_quantity(self):
        """R = m_seen/S - m_all/N, and the clipped ratio is Nc's variance, first order's N's (the receipt's survivors)."""
        rng = np.random.default_rng(8)
        d = 50
        q = {"S": np.full((16, d), 100.0), "m_seen": np.full((16, d), 2.0), "N": np.full((16, d), 50.0),
             "m_all": np.full((16, d), 1.0), "S_reco": np.full((16, d), 100.0), "m_bkg": np.zeros((16, d)),
             "Nm": rng.normal(50, 1, (16, d))}
        q["Nc"] = rng.normal(51, 2.0, (16, d))
        q["N"] = q["N"] + rng.normal(0, 1.0, (16, d))
        b = c2.c2_block(q, np.ones(16), np.ones(16))
        R = q["m_seen"] / q["S"] - q["m_all"] / q["N"]
        np.testing.assert_allclose(b["option_1"]["sigma_Q"]["signed_median"], np.median(R, axis=1))
        np.testing.assert_allclose(b["variance_ratio"][c2.CLIPPED], np.var(q["Nc"], axis=1, ddof=1))
        np.testing.assert_allclose(b["variance_ratio"]["first_order"], np.var(q["N"], axis=1, ddof=1))


class Linearisation(unittest.TestCase):
    def test_the_tolerance_both_ways_and_the_values_either_way(self):
        R = np.ones((10, 16))
        R[:, 3] = 1.02 - 1e-12
        out = c2.linearisation({"t": R})
        self.assertTrue(out["holds"])
        self.assertAlmostEqual(out["t"]["mean_ratio_minus_1"][3], 0.02, places=9)
        R[:, 3] = 1.0201
        out = c2.linearisation({"t": R, "u": np.ones((10, 16))})
        self.assertFalse(out["holds"])
        self.assertFalse(out["t"]["holds"])
        self.assertTrue(out["u"]["holds"])
        self.assertEqual(len(out["u"]["mean_ratio_minus_1"]), 16)
        self.assertEqual((c2.LINEARISATION_TOL, c2.CONTROL_Z), (0.02, 4.0))


class Truth(unittest.TestCase):
    def world(self, rng, n=4000):
        edges = [np.array([0, 1, 2.0]), np.array([0, 1, 2, 3.0]), np.array([0, 1.0, 2]), np.array([0, 1.0, 2]),
                 np.array([0, 2.0])]
        gen = np.column_stack([rng.uniform(0, e[-1], n) for e in edges])
        wt = rng.uniform(0.5, 1.5, n)
        wt[:50] = -0.3
        pt = rng.uniform(size=n) > 0.1
        denom, _ = np.histogramdd(gen, bins=edges, weights=np.abs(wt) * 1.3)
        return {"edges": edges, "MCgen": gen, "w_truth": wt, "pass_truth": pt, "denom_nd": denom,
                "flux": np.array([2.0, 3.0]), "data_pot": 1e20, "n_nucleons": 3e30}

    def test_xt_flat_is_true_xsec_bitwise(self):
        rng = np.random.default_rng(3)
        w = self.world(rng)
        r = rng.uniform(0.5, 2, w["MCgen"].shape[0])
        half = dict(w, w_truth=0.5 * w["w_truth"])
        x = s5n_pseudo.true_xsec(half, np.ones(w["MCgen"].shape[0], bool), r).ravel()
        sel = w["pass_truth"]
        A, _ = np.histogramdd(w["MCgen"][sel], bins=w["edges"], weights=2.0 * half["w_truth"][sel] * r[sel])
        B, _ = np.histogramdd(w["MCgen"][sel], bins=w["edges"], weights=2.0 * half["w_truth"][sel])
        got = c2.xt_flat(A[None], B[None], w["denom_nd"][None], w["flux"][None], w["n_nucleons"], w["data_pot"],
                         A.shape, w["edges"])
        self.assertTrue(np.array_equal(got[0], x))

    def test_xt_flat_zero_where_the_extraction_is(self):
        rng = np.random.default_rng(4)
        w = self.world(rng)
        D = w["denom_nd"].copy()
        D.flat[0] = 0.0
        x, good = extract_cross_section_nd(np.ones_like(D), np.zeros_like(D), w["flux"], 1e20, 3e30, w["edges"])
        got = c2.xt_flat(np.ones_like(D)[None], np.ones_like(D)[None], D[None], w["flux"][None], 3e30, 1e20,
                         D.shape, w["edges"])
        self.assertEqual(got[0, 0], 0.0)
        self.assertTrue(np.all(got[0, 1:] > 0))

    def test_composite_sums_are_the_histogram_of_the_row_composite(self):
        rng = np.random.default_rng(5)
        n, nu, cells = 500, 6, 8
        cell = rng.integers(0, cells, n)
        cv = rng.uniform(0.5, 1.5, n)
        V = cv + rng.normal(0, 0.3, (nu, n))
        S = np.zeros((4, nu))
        for d, cols in enumerate(([0, 2], [1, 3, 5], [4], [0, 1, 2, 3])):
            S[d, cols] = 1
        hist = lambda a: np.bincount(cell, weights=a, minlength=cells)  # noqa: E731
        H = np.array([hist(v) for v in V])
        got = c2.composite_sums(S, {"A": H, "B": H, "D": H}, {"A": hist(cv), "B": hist(cv), "D": hist(cv)})["A"]
        for d in range(4):
            cols = np.flatnonzero(S[d])
            row = V[cols[0]] + sum(V[j] - cv for j in cols[1:])
            self.assertTrue(np.allclose(got[d], hist(row), rtol=1e-12, atol=1e-12))

    def test_draw_flux_is_the_flux_universes(self):
        S = np.array([[1, 0, 1, 0], [0, 1, 0, 1.0]])
        phi = np.array([[1.0, 2], [3, 4]])
        self.assertTrue(np.array_equal(c2.draw_flux(S, np.array([0, 1]), phi), phi))
        with self.assertRaises(c2.Refusal):
            c2.draw_flux(np.array([[1, 1, 0, 0.0]]), np.array([0, 1]), phi)


class Rates(unittest.TestCase):
    def test_each_rate_counts_its_own_rule(self):
        R = np.ones((4, 16))
        R[0, :3] = 1.25                     # (i) only
        R[1] = math.exp(0.08)               # (ii) only: 1.083 is within 0.20
        R[2, 0] = 1.36                      # (iii) only
        out = c2.rates({"t": R})["t"]["b"]
        self.assertEqual([out[k]["rate"] for k in ("i", "ii", "iii", "union")], [0.25, 0.25, 0.25, 0.75])

    def test_the_rates_are_gate_724s_at_each_edge(self):
        """Audit W2: each rule's rate equals gate_724's verdict on the same replicate, at each bound and one ulp past."""
        at_max = 1.0 + c2.GATE_MAX
        while at_max - 1.0 > c2.GATE_MAX:
            at_max = np.nextafter(at_max, 0.0)
        at_dev = 1.0 + c2.GATE_DEV
        while at_dev - 1.0 > c2.GATE_DEV:
            at_dev = np.nextafter(at_dev, 0.0)
        rows = []
        for v in (at_max, np.nextafter(at_max, 2.0)):
            r = np.ones(16)
            r[0] = v
            rows.append(r)
        for k, v in ((2, at_dev), (3, at_dev), (2, np.nextafter(at_dev, 2.0)), (3, np.nextafter(at_dev, 2.0))):
            r = np.full(16, 0.99)
            r[:k] = v
            rows.append(r)
        ml = math.exp(c2.GATE_LOGMEAN)
        rows += [np.full(16, ml * (1 - 1e-15)), np.full(16, np.nextafter(ml, 2.0) * (1 + 1e-15))]
        exact = np.full(16, ml)                               # a mean log of exactly 0.07 (passes (ii))
        x = exact[15]
        for _ in range(2500):
            x = np.nextafter(x, 0)
        for _ in range(5000):
            exact[15] = x
            if np.mean(np.log(exact)) == c2.GATE_LOGMEAN:
                break
            x = np.nextafter(x, 2)
        rows.append(exact)
        R = np.array(rows)
        out = c2.rates({"t": R})["t"]["b"]
        g = [c2.gate_724(x) for x in R]
        for k in ("i", "ii", "iii"):
            self.assertAlmostEqual(out[k]["rate"], np.mean([not x[k] for x in g]))
        self.assertAlmostEqual(out["union"]["rate"], np.mean([not x["passes"] for x in g]))
        self.assertGreater(out["union"]["rate"], 0)
        self.assertLess(out["union"]["rate"], 1)

    def test_the_route_to_joseph_is_on_b_not_c(self):
        """(b)'s union above 1 % and (c)'s below: 2 % of the sets sit at a mean log of 0.08 (past 0.07, inside
        3.5 x the SD of 0.03)."""
        rng = np.random.default_rng(3)
        ml = rng.normal(0, 0.03, 5000)
        ml[:100] = 0.08
        R = np.exp(ml)[:, None] * np.ones((1, 16))
        out = c2.rates({"a": R, "b": np.roll(R, 2500, axis=0)})
        self.assertGreater(out["over_truths_b"]["union_per_replicate"], c2.UNION_LIMIT)
        self.assertLess(out["over_truths_c"]["union_per_replicate"], c2.UNION_LIMIT)
        self.assertTrue(out["to_joseph"])

    def test_the_verdict_in_its_order(self):
        ok, no = {"holds": True}, {"holds": False}
        self.assertEqual(c2.calibration_verdict(no, no, {"to_joseph": True}), "CONTROL_FAILED")
        self.assertEqual(c2.calibration_verdict(ok, no, {"to_joseph": True}), "LINEARISATION_TO_DIRECTOR")
        self.assertEqual(c2.calibration_verdict(ok, ok, {"to_joseph": True}), "TO_JOSEPH")
        self.assertEqual(c2.calibration_verdict(ok, ok, {"to_joseph": False}), "CALIBRATED")

    def test_power_moves_the_mean_log_by_the_deflation(self):
        R = np.full((10, 16), 1.0)
        out = c2.rates({"t": R * np.exp(np.random.default_rng(0).normal(0, 0.01, (10, 1)))})["t"]
        self.assertEqual(out["power_ii"]["at_fixed"], 1.0)        # log 0.9 = -0.105 is past 0.07
        self.assertEqual(c2.rates({"t": R}, deflation=0.95)["t"]["power_ii"]["at_fixed"], 0.0)

    def test_c_thresholds_use_the_measured_sds(self):
        rng = np.random.default_rng(6)
        R = np.exp(rng.normal(0, 0.02, (4000, 1)) + rng.normal(0, 0.05, (4000, 16)))
        out = c2.rates({"t": R})["t"]
        ml = np.mean(np.log(R), axis=1)
        self.assertAlmostEqual(out["c"]["ii_threshold"], 3.5 * np.std(ml, ddof=1))
        sd_c = np.std(R, axis=0, ddof=1)
        alpha = np.mean(np.max(np.abs(R - 1) / sd_c, axis=1) > 4.3)
        self.assertAlmostEqual(out["c"]["iii_alpha"]["rate"], alpha)

    def test_the_union_over_truths_and_the_route_to_joseph(self):
        R = np.ones((1000, 16))
        stop = R.copy()
        stop[:4, :3] = 1.25                 # 0.4 % per truth
        out = c2.rates({"a": stop, "b": np.roll(stop, 4, axis=0), "c": np.roll(stop, 8, axis=0)})
        self.assertAlmostEqual(out["over_truths_b"]["union_per_replicate"], 0.012)
        self.assertAlmostEqual(out["over_truths_b"]["union_product"], 1 - 0.996 ** 3)
        self.assertTrue(out["to_joseph"])
        out = c2.rates({"a": stop, "b": stop, "c": stop})          # same replicates fail together: 0.4 %
        self.assertAlmostEqual(out["over_truths_b"]["union_per_replicate"], 0.004)
        self.assertFalse(out["to_joseph"])


import argparse  # noqa: E402
import json  # noqa: E402

import s1_assemble as sa  # noqa: E402
import s5p_universe  # noqa: E402
import test_fd_1b_mc as tmc  # noqa: E402


class Job(tmc.Case):
    """calibrate_main over amendment 2's toy world: one read per universe, the checks, the timing guard, the outputs."""

    def run_job(self, det_equal=True, budget=1e6, r_neg=0, tdw_cv=True, prepare_only=False):
        world = {"inputs": self.inputs, "bkg": self.bkg, "bank_cv": self.bank_cv, "flux": self.flux,
                 "groups": toys.interaction_groups(self.w.bank), "pins": json.loads(self.w.pins.read_text()),
                 "npz_sha": "n", "bkg_sha": "b", "tdw_cv": np.ones(50) if tdw_cv else None}
        n_bins = int(np.prod([np.asarray(e).size - 1 for e in self.inputs["edges"]]))
        cells = mc.flat_cells(np.asarray(self.inputs["MCgen"], float), self.inputs["edges"])
        live = np.unique(cells[(cells >= 0) & np.asarray(self.inputs["pass_truth"], bool)])
        fm = np.full(n_bins, -1)
        fm[live] = np.arange(live.size) % sa.N_CELLS           # every reporting cell holds populated fine cells
        U = np.vstack([np.where(fm == c, 1.0, 0.0) for c in range(sa.N_CELLS)])
        real = mc._single

        def single(inputs, bkg, bank_cv, tag, w, flux):
            w = self.consistent(tag, w)
            if not det_equal and "denom_nd" in w:
                w = dict(w, denom_nd=np.asarray(self.inputs["denom_nd"], float) * 1.01)
            return real(inputs, bkg, bank_cv, tag, w, flux)

        def weight(t, inputs, ratio, push):
            rr = np.random.default_rng(len(t)).uniform(0.8, 1.2, inputs["w_truth"].shape[0])
            rr[np.flatnonzero(np.asarray(inputs["pass_truth"], bool))[:r_neg]] = -0.1
            return rr

        a = argparse.Namespace(flux_constraint=self.w.constraint, definition=self.tmp / "d.json", truths=["g18", "ar23"],
                               prep=self.tmp, push=None, expect_push_sha256=None, sets=40, workers=2,
                               budget_seconds=budget, bank=self.w.bank, detector_dir=self.w.det,
                               expect_pins_sha256="p", expect_flux_table_sha256="f", expect_cv_tdw_sha256="t",
                               out=self.tmp / "cal" / "cal.json")
        with mock.patch.object(mc, "_load_world", lambda a: world), mock.patch.object(mc, "_single", single), \
                mock.patch.object(sa, "fine_map", lambda p: fm), mock.patch.object(sa, "functional_matrix", lambda f: U), \
                mock.patch.object(mc, "truth_ratio", lambda t, p: (None, None)), \
                mock.patch.object(mc, "truth_weight", weight):
            return c2.prepare(a, rows=True) if prepare_only else c2.calibrate_main(a)

    def test_a_calibration_over_the_toy_world(self):
        rec = self.run_job()
        self.assertEqual(rec["schema"], c2.SCHEMA_CAL)
        self.assertEqual(rec["checks"]["detector_denominator_differs_from_cv"], [])
        self.assertEqual(rec["checks"]["r_negative"]["g18"]["rows"], 0)
        for t in ("g18", "ar23"):
            self.assertEqual(rec["outputs"][t]["sets"], 40)
            self.assertEqual(len(rec["ratio_mean_per_cell"][t]), sa.N_CELLS)
        z = np.load(self.tmp / "cal" / "cal.npz")
        self.assertEqual(z["ratio_g18"].shape, (40, sa.N_CELLS))
        self.assertTrue(np.all(np.isfinite(z["count_ratio_ar23"])))
        self.assertTrue(rec["control_law"]["holds"])
        self.assertIn(rec["verdict"], ("CALIBRATED", "TO_JOSEPH", "CONTROL_FAILED", "LINEARISATION_TO_DIRECTOR"))
        self.assertEqual(len(rec["control_linearisation"]["g18"]["mean_ratio_minus_1"]), sa.N_CELLS)
        self.assertEqual(rec["atime"]["moved"], [])

    def test_the_checks_are_silent_when_they_hold_and_name_rows_when_not(self):
        rec = self.run_job(r_neg=3)
        self.assertEqual(rec["checks"]["detector_denominator_differs_from_cv"], [])
        with self.assertRaisesRegex(c2.Refusal, "detector denominators differ"):
            self.run_job(det_equal=False)
        with self.assertRaisesRegex(c2.Refusal, "need --cv-tdw"):
            self.run_job(tdw_cv=False)
        self.assertEqual(rec["checks"]["r_negative"]["g18"]["rows"], 3)
        self.assertEqual(len(rec["checks"]["r_negative"]["ar23"]["first_rows"]), 3)

    def test_prepare_uses_the_float32_cv_denominator(self):
        """(e2) in prepare: d_CV is hist_f32(tdw_CV), not the npz's denom_nd, when the two differ (as on the real files)."""
        import s5p_universe
        d32 = s5p_universe.denominator(self.bank_cv, np.ones(50), self.inputs["edges"])
        npz = np.array(d32, float)
        c = np.flatnonzero(np.ravel(npz) > 1)[:2]
        npz.flat[c[0]] -= 1.0
        npz.flat[c[1]] += 1.0
        with mock.patch.dict(self.inputs, {"denom_nd": npz}):
            P = self.run_job(prepare_only=True)
        np.testing.assert_array_equal(P["D_cv_full"], np.ravel(d32))
        self.assertFalse(np.array_equal(P["D_cv_full"], np.ravel(npz)))

    def test_the_budget_guard_refuses_before_the_pool(self):
        with self.assertRaisesRegex(c2.Refusal, "passes the budget"):
            self.run_job(budget=1e-3)


class C2Truth(tmc.Case):
    """D1: c2check's truth is the bulk's. c2_truth's N and Nc for a declared draw equal U x_T of toy_experiment's own
    truth under "data" and "nature" on fd_1b_mc.compose's composite of the same draw (summation order aside)."""

    def matrices(self):
        tags = toys.s1_universes()
        inputs = self.inputs
        n_bins = int(np.prod([np.asarray(e).size - 1 for e in inputs["edges"]]))
        V = {k: [] for k in ("wt", "wr", "bkgw", "tdw", "D")}
        for t in tags:
            w = self.weights_cv_det(t)
            single, _ = mc._single(inputs, self.bkg, self.bank_cv, t, w, self.flux)
            for k in ("wt", "wr", "bkgw"):
                V[k].append(single[k])
            V["tdw"].append(np.asarray(w["tdw"], float) if "tdw" in w else np.ones(50))
            V["D"].append(np.ravel(single["denom"]))
        V = {k: np.array(v) for k, v in V.items()}
        cv = {"wt": np.asarray(inputs["w_truth"], float), "wr": np.asarray(inputs["w_reco"], float),
              "bkgw": np.asarray(self.bkg["bkg_w"], float), "tdw": np.ones(50),
              "D": np.ravel(np.asarray(inputs["denom_nd"], float))}
        return tags, V, cv, n_bins

    def test_the_gates_truth_is_the_bulks(self):
        tags, V, cv, n_bins = self.matrices()
        inputs = self.inputs
        col = {t: i for i, t in enumerate(tags)}
        groups = toys.interaction_groups(self.w.bank)
        flux_p = np.full(100, 0.01)
        seeds = [3_620_000, 3_620_001, 3_620_002]
        draws = [mc.draw_universes(toys.draw_for_seed(sd, flux_p, groups)) for sd in seeds]
        _, bands, _ = c2.layout_1b()
        S = c2.selection(draws, col, bands)
        shape = tuple(np.asarray(e).size - 1 for e in inputs["edges"])
        fm = np.arange(n_bins) % sa.N_CELLS
        U = np.vstack([np.where(fm == c, 1.0 + 0.1 * c, 0.0) for c in range(sa.N_CELLS)])
        keep = np.arange(n_bins)
        pack = c2.packing(keep, shape, inputs["edges"])
        ptru, prec = np.asarray(inputs["pass_truth"], bool), np.asarray(inputs["pass_reco"], bool)
        geo = {"gen": np.where(ptru, mc.flat_cells(np.asarray(inputs["MCgen"], float), inputs["edges"]), -1),
               "reco": np.where(prec, mc.flat_cells(np.asarray(inputs["MCreco"], float), inputs["edges"]), -1),
               "bkg": mc.flat_cells(np.asarray(self.bkg["bkg_reco"], float), inputs["edges"]),
               "td": mc.td_cells(self.bank_cv, inputs["edges"]), "fm": fm, "U": U, "shape": shape}
        phi = np.array([self.flux[int(d[0].rpartition("_")[2])] for d in draws])
        r = np.random.default_rng(11).uniform(0.7, 1.3, inputs["w_truth"].shape[0])
        V["wt"][:, :40] *= -1.0                         # negative truth rows, so the clip acts
        tdc = geo["td"]
        counts = np.bincount(tdc[tdc >= 0], minlength=n_bins)
        busy = np.flatnonzero((tdc >= 0) & (counts[np.maximum(tdc, 0)] >= 4))
        self.assertGreater(busy.size, 0)
        V["tdw"][col["MaRES_1"], busy[:1]] = -0.2         # a negative composite row in a cell that stays positive
        V["tdw"][col["MaRES_0"], busy[:1]] = -0.2
        for t in ("MaRES_0", "MaRES_1"):                  # the precondition: each universe's D is its rows' histogram
            V["D"][col[t]] = np.ravel(s5p_universe.denominator(self.bank_cv, V["tdw"][col[t]], inputs["edges"]))
        const = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]), "pack": pack}
        q = c2.c2_truth(V, cv, S, r, geo, phi, const, block=2)

        def load(t):
            w = dict(self.weights_cv_det(t))
            i = col[t]
            w["wt"] = V["wt"][i]
            if "tdw" in w:
                w["tdw"] = V["tdw"][i]
            return w
        moved = 0
        for d, tags_d in enumerate(draws):
            ui, ub, _ = mc.compose(inputs, self.bkg, self.bank_cv, tags_d, load, self.flux, np.ones(50))
            for rule, key in (("data", "N"), ("nature", "Nc")):
                _, x, _ = mc.toy_experiment(inputs, self.bkg, ui, ub, r, seeds[d], rule)
                np.testing.assert_allclose(q[key][:, d], U @ np.ravel(x), rtol=1e-10, atol=0, err_msg=f"{rule} {d}")
            moved += int(np.any(q["Nc"][:, d] != q["N"][:, d]))
        self.assertGreater(moved, 0)
        self.assertTrue(np.all(np.isfinite(q["Nm"])))



if __name__ == "__main__":
    unittest.main()
