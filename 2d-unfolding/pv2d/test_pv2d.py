"""Synthetic controls for pv2d_lib (no ROOT): run with `python3 -m unittest test_pv2d -v` from this directory."""
import json
import os
import tempfile
import unittest

import numpy as np

import pv2d_lib as L


def toy(n=200_000, seed=1):
    rng = np.random.default_rng(seed)
    pt = rng.uniform(0.0, 4.5, n)
    pz = rng.uniform(1.5, 60.0, n)
    pt[:5] = [4.5, -0.1, np.nan, 0.0, 2.5]      # last edge (overflow), underflow, nan, first edge, interior edge
    pz[:5] = [10.0, 3.0, 3.0, 60.0, 1.5]        # interior edge, -, -, last edge (overflow), first edge
    pass_truth = rng.uniform(size=n) > 0.02
    sig = {"truth_pt": pt, "truth_pz": pz, "pass_truth": pass_truth,
           "w_truth": rng.uniform(0.5, 1.5, n), "w_reco": rng.uniform(0.5, 1.5, n)}
    den = {"truth_pt": np.concatenate([pt[pass_truth], rng.uniform(0, 4.5, 1000)]),
           "truth_pz": np.concatenate([pz[pass_truth], rng.uniform(1.5, 60, 1000)]),
           "w_truth": np.concatenate([sig["w_truth"][pass_truth], rng.uniform(0.5, 1.5, 1000)])}
    return sig, den


def ratio(seed=2):
    return np.random.default_rng(seed).uniform(0.6, 1.6, (L.NPT, L.NPZ))


class CellIndex(unittest.TestCase):
    def test_root_convention(self):
        e = L.PT_EDGES
        self.assertEqual(L.cell_index([0.0], e)[0], 0)            # first edge -> first bin
        self.assertEqual(L.cell_index([0.07], e)[0], 1)           # interior edge -> upper bin (TH1::FindBin)
        self.assertEqual(L.cell_index([4.5], e)[0], L.NPT)        # last edge -> overflow
        self.assertEqual(L.cell_index([-1e-9], e)[0], -1)
        self.assertEqual(L.cell_index([np.nan], e)[0], -1)

    def test_weight_outside_is_one(self):
        r = ratio()
        w = L.cell_ratio_weight(r, [4.5, -0.1, np.nan, 0.0, 1.0], [10.0, 3.0, 3.0, 60.0, 60.0 - 1e-9])
        self.assertEqual(w[0], 1.0)
        self.assertEqual(w[1], 1.0)
        self.assertEqual(w[2], 1.0)
        self.assertEqual(w[3], 1.0)
        self.assertEqual(w[4], r[L.cell_index([1.0], L.PT_EDGES)[0], L.NPZ - 1])

    def test_shape_refused(self):
        with self.assertRaises(ValueError):
            L.cell_ratio_weight(np.ones((L.NPZ, L.NPT)), [1.0], [2.0])


class DenominatorGuard(unittest.TestCase):
    """The s5p study-P defect: the guard must fire on the defective form and stay silent on the repaired one."""

    def test_repaired_form_is_silent(self):
        sig, den = toy()
        c0 = L.completeness(sig, den)
        L.apply_prior_ratio(sig, den, ratio())
        d = L.completeness_guard(c0, L.completeness(sig, den))
        self.assertLess(d, 1e-12)

    def test_defective_form_fires(self):
        sig, den = toy()
        c0 = L.completeness(sig, den)
        rs = L.cell_ratio_weight(ratio(), sig["truth_pt"], sig["truth_pz"])
        sig["w_truth"] = sig["w_truth"] * rs           # numerator only: the denominator is left unreweighted
        with self.assertRaises(SystemExit):
            L.completeness_guard(c0, L.completeness(sig, den))

    def test_identity_is_bitwise(self):
        sig, den = toy()
        w0, r0, d0 = sig["w_truth"].copy(), sig["w_reco"].copy(), den["w_truth"].copy()
        L.apply_prior_ratio(sig, den, np.ones((L.NPT, L.NPZ)))
        self.assertTrue(np.array_equal(sig["w_truth"], w0))
        self.assertTrue(np.array_equal(sig["w_reco"], r0))
        self.assertTrue(np.array_equal(den["w_truth"], d0))

    def test_fakes_keep_their_weights(self):
        sig, den = toy()
        fake = ~sig["pass_truth"]
        w0 = sig["w_reco"][fake].copy()
        L.apply_prior_ratio(sig, den, ratio())
        self.assertTrue(np.array_equal(sig["w_reco"][fake], w0))

    def test_reco_weight_moves_by_r(self):
        sig, den = toy()
        r = ratio()
        m = sig["pass_truth"]
        w0 = sig["w_reco"].copy()
        L.apply_prior_ratio(sig, den, r)
        f = L.cell_ratio_weight(r, sig["truth_pt"], sig["truth_pz"])
        self.assertTrue(np.allclose(sig["w_reco"][m], w0[m] * f[m], rtol=1e-15, atol=0))
        self.assertTrue(np.any(f[m] != 1.0))

    def test_denominator_moves_by_r(self):
        sig, den = toy()
        r = ratio()
        h0 = L.hist2d(den["truth_pt"], den["truth_pz"], den["w_truth"])
        L.apply_prior_ratio(sig, den, r)
        h1 = L.hist2d(den["truth_pt"], den["truth_pz"], den["w_truth"])
        ok = h0 > 0
        self.assertLess(np.max(np.abs(h1[ok] / h0[ok] / r[ok] - 1)), 1e-12)

    def test_guard_refuses_support_change(self):
        c0 = np.ones((L.NPT, L.NPZ))
        c1 = c0.copy()
        c1[2, 3] = 0.0
        with self.assertRaises(SystemExit):
            L.completeness_guard(c0, c1)

    def test_prior_histogram_moves_by_r(self):
        sig, den = toy()
        r = ratio()
        m = sig["pass_truth"]
        h0 = L.hist2d(sig["truth_pt"][m], sig["truth_pz"][m], sig["w_truth"][m])
        L.apply_prior_ratio(sig, den, r)
        h1 = L.hist2d(sig["truth_pt"][m], sig["truth_pz"][m], sig["w_truth"][m])
        ok = h0 > 0
        self.assertLess(np.max(np.abs(h1[ok] / h0[ok] / r[ok] - 1)), 1e-12)


class LoadRatio(unittest.TestCase):
    def write(self, d):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump(d, f)
        self.addCleanup(os.remove, path)
        return path

    def good(self):
        return {"schema": L.RATIO_SCHEMA, "pt_edges": list(L.PT_EDGES), "pz_edges": list(L.PZ_EDGES),
                "r": ratio().tolist()}

    def test_accepts_declared(self):
        p = self.write(self.good())
        r, _ = L.load_ratio(p, L.sha256_path(p))
        self.assertEqual(r.shape, (L.NPT, L.NPZ))

    def test_refuses_wrong_sha(self):
        p = self.write(self.good())
        with self.assertRaises(SystemExit):
            L.load_ratio(p, "0" * 64)

    def test_refuses_wrong_edges(self):
        d = self.good()
        d["pz_edges"] = d["pz_edges"][:-1] + [61.0]
        p = self.write(d)
        with self.assertRaises(SystemExit):
            L.load_ratio(p, L.sha256_path(p))

    def test_refuses_wrong_schema(self):
        d = self.good()
        d["schema"] = "pv2d-ratio/0"
        p = self.write(d)
        with self.assertRaises(SystemExit):
            L.load_ratio(p, L.sha256_path(p))

    def test_refuses_wrong_shape(self):
        d = self.good()
        d["r"] = d["r"][:-1]
        p = self.write(d)
        with self.assertRaises(SystemExit):
            L.load_ratio(p, L.sha256_path(p))

    def test_refuses_nan(self):
        d = self.good()
        d["r"][0][0] = float("nan")
        p = self.write(d)
        with self.assertRaises(SystemExit):
            L.load_ratio(p, L.sha256_path(p))

    def test_refuses_nonpositive(self):
        d = self.good()
        d["r"][3][4] = 0.0
        p = self.write(d)
        with self.assertRaises(SystemExit):
            L.load_ratio(p, L.sha256_path(p))


class BuildRatio(unittest.TestCase):
    def test_shape_only_and_region(self):
        rng = np.random.default_rng(3)
        p = rng.uniform(1, 10, (L.NPT, L.NPZ))
        t = p * 2.0
        g = t * rng.uniform(0.7, 1.3, t.shape) * 5.0
        region = rng.uniform(size=t.shape) > 0.2
        r, k = L.build_ratio(g, t, p, region)
        self.assertTrue(np.all(r[~region] == 1.0))
        self.assertAlmostEqual((p[region] * r[region]).sum() / p[region].sum(), 1.0, places=12)
        q = r[region] / (g[region] / t[region])
        self.assertLess(np.ptp(q), 1e-12)                       # one constant on the region

    def test_refuses_empty_region_cell(self):
        p = np.ones((L.NPT, L.NPZ))
        g = p.copy()
        g[0, 0] = 0.0
        with self.assertRaises(ValueError):
            L.build_ratio(g, p, p, np.ones_like(p, bool))

    def test_vertex_equal_to_prior_is_identity(self):
        p = np.random.default_rng(4).uniform(1, 10, (L.NPT, L.NPZ))
        r, _ = L.build_ratio(3.0 * p, p, p, np.ones_like(p, bool))
        self.assertLess(np.max(np.abs(r - 1)), 1e-12)


class Readouts(unittest.TestCase):
    def test_nominal_control_both_directions(self):
        x = np.random.default_rng(5).uniform(1, 2, 205)
        self.assertTrue(L.nominal_control(x * (1 + 5e-6), x)["pass"])
        self.assertFalse(L.nominal_control(x * (1 + 2e-5), x)["pass"])
        self.assertTrue(L.nominal_control(x.copy(), x)["bitwise"])

    def test_positive_control_branches(self):
        rng = np.random.default_rng(6)
        bias = rng.normal(0, 0.05, 205)
        good = -bias + rng.normal(0, 0.005, 205)
        self.assertEqual(L.positive_control(good, bias)["verdict"], "PASS")
        self.assertEqual(L.positive_control(rng.normal(0, 0.05, 205), bias)["verdict"], "FAIL")   # uncorrelated
        self.assertEqual(L.positive_control(-0.3 * bias, bias)["verdict"], "FAIL")                # slope too small
        self.assertEqual(L.positive_control(bias, bias)["verdict"], "FAIL")                       # wrong sign
        self.assertEqual(L.positive_control(-2.0 * bias, bias)["verdict"], "FAIL")                # slope too large
        tiny = rng.normal(0, 0.001, 205)
        self.assertEqual(L.positive_control(-tiny, tiny)["verdict"], "NOT_POWERED")

    def test_envelope(self):
        s = {"a": np.array([0.01, -0.05, 0.0]), "b": np.array([-0.02, 0.03, 0.0])}
        h, who = L.envelope(s)
        self.assertTrue(np.allclose(h, [0.02, 0.05, 0.0]))
        self.assertEqual(who[:2], ["b", "a"])

    def test_compare_to_sigma(self):
        c = L.compare_to_sigma(np.array([0.01, 0.1]), np.array([0.05, 0.05]))
        self.assertAlmostEqual(c["frac_h_gt_sigma"], 0.5)
        self.assertAlmostEqual(c["ratio_max"], 2.0)


class GatedRatio(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        self.gref = rng.uniform(1, 10, (L.NPT, L.NPZ))
        self.g = self.gref * rng.uniform(0.8, 1.2, self.gref.shape)
        self.region = np.ones(self.gref.shape, bool)

    def test_precise_cells_keep_their_own_ratio(self):
        v = (0.01 * self.g) ** 2
        rho, assigned, label, st = L.gated_shape_ratio(self.g, v, self.gref, (0.01 * self.gref) ** 2,
                                                       self.region, 0.05)
        self.assertTrue(np.all(label == "fine"))
        self.assertTrue(np.allclose(rho, self.g / self.gref, rtol=1e-14))
        self.assertTrue(np.allclose(st, np.sqrt(2) * 0.01))

    def test_noisy_cells_pool_by_coarse_cell(self):
        v = (0.01 * self.g) ** 2
        v[13, :] = (0.08 * self.g[13, :]) ** 2         # noisy per cell (8 %), <= 4 % pooled over >= 4 cells
        rho, assigned, label, _ = L.gated_shape_ratio(self.g, v, self.gref, np.zeros_like(v), self.region, 0.05)
        self.assertTrue(np.all(label[13, :] == "coarse"))
        coarse = L.coarse_of_cells()
        for cid in np.unique(coarse[13, :]):
            u = coarse[13, :] == cid
            self.assertTrue(np.allclose(rho[13, u], self.g[13, u].sum() / self.gref[13, u].sum()))

    def test_noisy_pool_is_unassigned(self):
        v = (0.5 * self.g) ** 2                         # everything noisy; one-row pools stay above 5 %
        region = np.zeros_like(self.region)
        region[13, 15] = True
        rho, assigned, label, _ = L.gated_shape_ratio(self.g, v, self.gref, np.zeros_like(v), region, 0.05)
        self.assertEqual(label[13, 15], "noisy")
        self.assertFalse(assigned.any())
        self.assertTrue(np.all(rho == 1.0))

    def test_off_region_is_one(self):
        region = self.region.copy()
        region[:, 12:] = False
        rho, assigned, label, _ = L.gated_shape_ratio(self.g, np.zeros_like(self.g), self.gref,
                                                      np.zeros_like(self.g), region, 0.05)
        self.assertTrue(np.all(rho[:, 12:] == 1.0))
        self.assertTrue(np.all(label[:, 12:] == "off"))

    def test_coarse_partition(self):
        c = L.coarse_of_cells()
        self.assertEqual(c.shape, (L.NPT, L.NPZ))
        self.assertEqual(len(np.unique(c)), 9)
        self.assertEqual(c[0, 0], 0)                   # pT < 0.55, p_par < 3.5
        self.assertEqual(c[13, 15], 8)                 # pT > 0.85, p_par > 6


class ReportTables(unittest.TestCase):
    def test_largest_step_both_directions(self):
        import report_tables as T
        r = np.ones((L.NPT, L.NPZ))
        self.assertEqual(T.largest_step(r, 5 * L.NPZ + 5), (0.0, (5, 5)))      # flat: no step, no neighbour
        r[5, 6] = 1.3
        step, nb = T.largest_step(r, 5 * L.NPZ + 5)
        self.assertAlmostEqual(step, 0.3)
        self.assertEqual(nb, (5, 6))
        self.assertEqual(T.largest_step(r, 0)[0], 0.0)                         # corner cell, far from the step
        r[0, 1] = 0.8
        self.assertAlmostEqual(T.largest_step(r, 0)[0], 0.2)                   # a corner sees its in-grid neighbour

    def test_classify_cell_both_directions(self):
        import report_tables as T
        r = np.ones((L.NPT, L.NPZ))
        lab = np.full((L.NPT, L.NPZ), "fine", dtype=object)
        g = 5 * L.NPZ + 5
        self.assertEqual(T.classify_cell(r, lab, g), "none")
        r[5, 6] = 1.3
        self.assertEqual(T.classify_cell(r, lab, g), "generator")           # fine|fine: the generator's step
        self.assertFalse(T.beside_construction_step(r, lab, g))
        for other, kind in (("coarse", "gate"), ("noisy", "gate"), ("off", "cut")):
            lab[5, 6] = other
            self.assertEqual(T.classify_cell(r, lab, g), kind)
            self.assertTrue(T.beside_construction_step(r, lab, g))
        lab[5, 5], lab[5, 6] = "coarse", "coarse"
        self.assertEqual(T.classify_cell(r, lab, g), "gate")                # coarse|coarse: a pooled-cell edge
        r[5, 6] = 1.05
        self.assertEqual(T.classify_cell(r, lab, g), "none")                # below the threshold
        self.assertEqual(T.classify_cell(r, lab, 9 * L.NPZ + 9), "none")    # far from any step
        r[5, 6], lab[5, 6] = 1.3, "off"                                     # a gate pair outranks a cut pair
        r[4, 5], lab[4, 5] = 1.3, "fine"
        self.assertEqual(T.classify_cell(r, lab, g), "gate")

    def test_tiers_cover_every_label_once(self):
        import report_tables as T
        labs = [x for _, t in T.TIERS for x in t]
        self.assertEqual(sorted(labs), sorted(["fine", "coarse", "noisy", "off"]))
        self.assertEqual(dict(T.TIERS)["r = 1"], ("noisy", "off"))


_HERE = os.path.dirname(os.path.abspath(__file__))


@unittest.skipUnless(os.path.exists(os.path.join(_HERE, "readouts", "readout_ref.json")), "committed readouts absent")
class ReportTablesOnCommittedReadouts(unittest.TestCase):
    """Pinned regression: the post-hoc counts REPORT.md quotes, from the committed files."""

    @classmethod
    def setUpClass(cls):
        import report_tables as T
        cls.T = T
        cls.I = T.Inputs(os.path.join(_HERE, "ratios", "projections.json"), os.path.join(_HERE, "ratios"))
        cls.A = T.load(os.path.join(_HERE, "readouts", "readout_a.json"))
        cls.R = T.load(os.path.join(_HERE, "readouts", "readout_ref.json"))
        cls.I.check(cls.A, "a")
        cls.I.check(cls.R, "refined")

    def test_union_rule_for_h(self):
        n = {v: int(self.I.near[v].sum()) for v in ("genie_mec", "nuwro", "gibuu", "h")}
        self.assertEqual(n, {"genie_mec": 2, "nuwro": 34, "gibuu": 19, "h": 52})
        self.assertTrue(np.array_equal(self.I.near["h"], self.I.near["genie_mec"] | self.I.near["nuwro"]
                                       | self.I.near["gibuu"]))

    def test_h_over_sigma_both_ways(self):
        keep = ~self.I.near["h"]
        for X, full, rest in ((self.A, 30, 9), (self.R, 26, 6)):
            h, sq = np.asarray(X["envelope"]["h"]), np.asarray(X["sigma_Q"]["cells"])
            self.assertEqual(int((h > sq).sum()), full)
            self.assertEqual(int((h[keep] > sq[keep]).sum()), rest)

    def test_step_classes_of_the_h_over_sigma_cells(self):
        h, sq = np.asarray(self.A["envelope"]["h"]), np.asarray(self.A["sigma_Q"]["cells"])
        dom = self.A["envelope"]["dominant"]
        got = [self.I.cls[dom[k]][k] for k in np.flatnonzero(h > sq)]
        self.assertEqual({k: got.count(k) for k in ("gate", "cut", "generator", "none")},
                         {"gate": 21, "cut": 0, "generator": 4, "none": 5})

    def test_refuses_a_wrong_arm(self):
        with self.assertRaises(SystemExit):
            self.I.check(self.A, "refined")

if __name__ == "__main__":
    unittest.main()
