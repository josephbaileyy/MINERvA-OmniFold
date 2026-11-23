#!/usr/bin/env python3
"""Synthetic tests of msr_project.py (declaration section 6's list), never on the real products.

    python3 -m unittest nd-unfolding/msr/test_msr.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import msr_project as P  # noqa: E402
import did  # noqa: E402  (msr_project put the pinned d-id directory on sys.path)


def planted(s: np.ndarray, seed: int = 0):
    """F (count space) and J = I with C = J F^+ J^T = Q diag(s^2) Q^T: planted widths s along the columns of Q."""
    n = s.size
    Q = np.linalg.qr(np.random.default_rng(seed).normal(size=(n, n)))[0]
    F = Q @ np.diag(1.0 / s ** 2) @ Q.T
    return F, np.eye(n), Q


class Bands(unittest.TestCase):
    def test_s_edges(self):
        self.assertEqual(P.band_s(0.8), "poor-dominated")
        self.assertEqual(P.band_s(0.7999999), "mixed")
        self.assertEqual(P.band_s(0.2), "well-dominated")
        self.assertEqual(P.band_s(0.2000001), "mixed")

    def test_z_edges(self):
        self.assertEqual(P.band_z(0.9999999), "below")
        self.assertEqual(P.band_z(1.0), "intermediate")
        self.assertEqual(P.band_z(1.9999999), "intermediate")
        self.assertEqual(P.band_z(2.0), "resolvable")

    def test_r_edges(self):
        self.assertEqual(P.band_r(0.5), "removes most")
        self.assertEqual(P.band_r(0.4999999), "removes part")
        self.assertEqual(P.band_r(0.2), "removes part")
        self.assertEqual(P.band_r(0.1999999), "no change")
        self.assertEqual(P.band_r(-0.1999999), "no change")
        self.assertEqual(P.band_r(-0.2), "increases")

    def test_interval_rule(self):
        self.assertEqual(P.label(0.3, 0.7, P.band_s, P.S_BANDS), "mixed")
        self.assertEqual(P.label(0.1, 0.9, P.band_s, P.S_BANDS), "unresolved across well-dominated, mixed, poor-dominated")
        self.assertEqual(P.label(0.5, 1.5, P.band_z, P.Z_BANDS), "unresolved across below, intermediate")

    def test_noise_maximum_rule_three_cases(self):
        self.assertEqual(P.label_z(2.5, 3.0, 2.4), "resolvable")
        self.assertEqual(P.label_z(2.1, 2.4, 2.4), "within the noise maximum")       # f_hi = Z_noise
        self.assertEqual(P.label_z(2.1, 2.6, 2.4), "unresolved across within-the-noise-maximum and resolvable")
        self.assertEqual(P.label_z(2.4, 2.6, 2.4), "unresolved across within-the-noise-maximum and resolvable")
        self.assertEqual(P.label_z(1.5, 2.6, 2.4), "unresolved across intermediate, resolvable")   # plain rule below 2
        self.assertEqual(P.label_z(None, None, None), "no well-constrained combination")

    def test_floor_three_branches(self):
        self.assertEqual(P.floor_reading(0.001, 0.009), "no bias to locate")
        self.assertEqual(P.floor_reading(0.005, 0.02), "unresolved at the floor")
        self.assertEqual(P.floor_reading(0.011, 0.05), "read")
        self.assertEqual(P.floor_reading(0.001, 0.01), "unresolved at the floor")     # 0.01 is contained

    def test_combined_order(self):
        self.assertEqual(P.combined("well-dominated", "resolvable", "no bias to locate", 3), "points at a resolvable component")
        self.assertEqual(P.combined("poor-dominated", "below", "no bias to locate", 3), "no bias to locate")
        self.assertEqual(P.combined("poor-dominated", "below", "read", 3), "consistent with an information limit")
        self.assertEqual(P.combined("poor-dominated", "no well-constrained combination", "read", 0),
                         "all combinations poorly constrained")
        self.assertEqual(P.combined("mixed", "intermediate", "read", 3), "intermediate")
        self.assertEqual(P.combined("mixed", "below", "read", 3), "intermediate")
        self.assertEqual(P.combined("poor-dominated", "intermediate", "read", 3), "intermediate")
        self.assertEqual(P.combined("unresolved across mixed, poor-dominated", "below", "read", 3), "unresolved")

    def test_across_truths(self):
        self.assertEqual(P.across({"a": "intermediate", "b": "intermediate"}, ("a", "b")), "intermediate at every tested truth")
        self.assertEqual(P.across({"a": "intermediate", "b": "consistent with an information limit"}, ("a", "b")),
                         "truth-dependent")
        self.assertEqual(P.across({"a": "unresolved", "b": "intermediate"}, ("a", "b")), "unresolved at a")


class Decomposition(unittest.TestCase):
    def test_poor_and_well_spans(self):
        s = np.array([0.02, 0.05, 0.3, 0.8])
        F, J, Q = planted(s)
        d = P.decompose(F, J)
        self.assertEqual((d["n_well"], d["n_mid"], d["dim_inf"]), (2, 2, 0))
        self.assertAlmostEqual(P.s_poor(d, Q[:, 2] + Q[:, 3]), 1.0, places=10)
        self.assertAlmostEqual(P.s_poor(d, Q[:, 0] - 2 * Q[:, 1]), 0.0, places=10)

    def test_z_is_the_span_maximum_not_the_axis_maximum(self):
        s = np.array([0.04, 0.06, 0.5])      # distinct widths, so the planted axes are the eigenvectors
        F, J, Q = planted(s, seed=3)
        d = P.decompose(F, J)
        beta = 0.9 * 0.04 * Q[:, 0] + 0.9 * 0.06 * Q[:, 1]
        self.assertLess(P.z_axis(d, beta), 1.0)
        self.assertAlmostEqual(P.z_well(d, beta), 0.9 * np.sqrt(2), places=8)
        self.assertGreater(P.z_well(d, beta), 1.0)

    def test_duplicated_column_goes_to_u_infinity(self):
        R = np.array([[1.0, 1.0, 0.0], [2.0, 2.0, 1.0], [0.5, 0.5, 3.0], [1.0, 1.0, 1.0]])
        F = P.fisher_c(did, R, np.ones(3), np.zeros(4))
        d = P.decompose(F, np.eye(3))
        self.assertEqual(d["dim_inf"], 1)
        u = d["U_inf"][:, 0] / np.linalg.norm(d["U_inf"][:, 0])
        self.assertAlmostEqual(abs(u @ np.array([1, -1, 0]) / np.sqrt(2)), 1.0, places=8)

    def test_a_tiny_null_component_is_still_unconstrained(self):
        F = np.diag([1.0, 1.0, 0.0])
        J = np.array([[1.0, 0.0, 0.0], [0.0, 1e-8, 1e-9]])
        d = P.decompose(F, J)
        self.assertEqual(d["dim_inf"], 1)
        mine, ref = P.rho_coordinate(d, J)
        np.testing.assert_allclose(mine, ref, atol=1e-12)
        self.assertGreater(mine[1], P.NULL_TOL)

    def test_count_space_case_r11_t0_1e7(self):
        R = np.array([[1.0, 1.0]])
        F = P.fisher_c(did, R, np.array([1.0, 1e7]), np.zeros(1))
        J = np.array([[1.0, -1.0], [1.0, 1.0]])
        d = P.decompose(F, J)
        mine, ref = P.rho_coordinate(d, J)
        np.testing.assert_allclose(mine, ref, atol=1e-12)
        _, nul = did.widths_from_eig(d["lam"], d["V"], J[:1])
        self.assertGreater(nul[0], 1e-6)                     # widths_from_eig marks it infinite
        self.assertEqual(d["dim_inf"], 1)                    # and it lands in U-infinity
        self.assertAlmostEqual(P.s_poor(d, np.array([1.0, 0.0])), 1.0, places=10)   # so outside W

    def test_route_independent_agrees(self):
        F, J, Q = planted(np.array([0.03, 0.06, 0.09, 0.4, 0.7]), seed=5)
        d = P.decompose(F, J)
        beta = np.random.default_rng(1).normal(size=5) * 0.05
        sp, zw = P.route_independent(d, beta)
        self.assertAlmostEqual(sp, P.s_poor(d, beta), places=10)
        self.assertAlmostEqual(zw, P.z_well(d, beta), places=8)

    def test_two_drivers_agree_on_a_planted_case(self):
        F, J, _ = planted(np.array([0.03, 0.2, 0.5]), seed=7)
        a, b = P.decompose(F, J, "numpy"), P.decompose(F, J, "evr")
        beta = np.array([0.01, 0.02, -0.03])
        self.assertTrue(P.nprec(a, b, P.evaluate(a, beta, "single"), P.evaluate(b, beta, "single")))


class Statistics(unittest.TestCase):
    def test_r_pair_floors_and_values(self):
        F, J, Q = planted(np.array([0.05, 0.5]), seed=2)
        d = P.decompose(F, J)
        b0 = 0.1 * Q[:, 0] + 0.1 * Q[:, 1]
        r = P.r_pair(d, 0.05 * Q[:, 0] + 0.1 * Q[:, 1], b0)
        self.assertAlmostEqual(r["r_well"], 0.5, places=10)
        self.assertAlmostEqual(r["r_poor"], 0.0, places=10)
        self.assertIsNone(P.r_pair(d, b0, 0.001 * Q[:, 0] + 0.1 * Q[:, 1])["r_well"])   # well part under the floor

    def test_sentinel_when_no_well_combination(self):
        F, J, _ = planted(np.array([0.3, 0.6]))
        d = P.decompose(F, J)
        self.assertIsNone(P.z_well(d, np.array([0.1, 0.1])))
        ev = P.evaluate(d, np.array([0.1, 0.1]), "single")
        self.assertEqual(ev["Z_label"], "no well-constrained combination")
        self.assertEqual(ev["combined"], "all combinations poorly constrained")

    def test_intervals(self):
        lo, hi = P.interval_splits(1.0, [0.9, 1.0, 1.1, 1.0, 1.0])
        h = P.T_MULT * np.std([0.9, 1.0, 1.1, 1.0, 1.0], ddof=1) / np.sqrt(5)
        self.assertAlmostEqual(hi - 1.0, h, places=12)
        self.assertEqual(P.interval_splits(1.0, [1.0, None, 1, 1, 1]), (None, None))
        d1, d2 = P.perturbations(np.ones(3)), P.perturbations(np.ones(3))
        np.testing.assert_array_equal(d1, d2)
        self.assertEqual(d1.shape, (P.N_PERT, 3))
        lo, hi = P.interval_noisy(lambda v: float(v[0]), np.zeros(3), np.ones(3))
        self.assertAlmostEqual(lo, np.percentile(d1[:, 0], 2.5))
        self.assertAlmostEqual(hi, np.percentile(d1[:, 0], 97.5))

    def test_evaluate_kinds(self):
        F, J, Q = planted(np.array([0.05, 0.5, 0.9]), seed=4)
        d = P.decompose(F, J)
        beta = 0.2 * Q[:, 1] + 0.01 * Q[:, 0]
        e1 = P.evaluate(d, beta, "single")
        self.assertEqual(e1["floor"], "read")
        e2 = P.evaluate(d, beta, "splits", splits=[beta * (1 + 0.01 * k) for k in range(5)])
        self.assertLessEqual(e2["S_interval"][0], e2["S_poor"])
        e3 = P.evaluate(d, beta, "noisy", sd=np.full(3, 0.001))
        self.assertIsNotNone(e3["Z_noise"])
        e4 = P.evaluate(d, np.full(3, 0.001), "single")
        self.assertEqual(e4["floor"], "no bias to locate")
        self.assertEqual(e4["combined"], "no bias to locate")
        r = P.evaluate_r(d, beta, 2 * beta, [beta] * 5, [2 * beta] * 5)
        self.assertEqual(r["r_poor"]["label"], "removes most")


class Branches(unittest.TestCase):
    """The guard and failure branches the line tracer requires (each one reached by a planted case)."""

    def test_everything_unconstrained(self):
        d = P.decompose(np.zeros((2, 2)), np.eye(2))
        self.assertEqual((d["n_well"], d["dim_inf"]), (0, 2))
        self.assertEqual(d["w"].shape, (2, 0))

    def test_r_split_failing_its_floor(self):
        F, J, Q = planted(np.array([0.05, 0.5]), seed=2)
        d = P.decompose(F, J)
        b0 = 0.1 * Q[:, 0] + 0.1 * Q[:, 1]
        splits_b0 = [b0] * 4 + [0.001 * Q[:, 0] + 0.1 * Q[:, 1]]
        r = P.evaluate_r(d, b0, b0, [b0] * 5, splits_b0)
        self.assertEqual(r["r_well"]["label"], "unresolved across bands")

    def test_matching_with_an_empty_basis(self):
        F, J, _ = planted(np.array([0.02, 0.3]), seed=1)
        f = P.decompose(F, J)
        e = dict(f, w=np.zeros((2, 0)), s=np.zeros(0))
        c = P.matched_counts({"full": f, "A": e, "B": f})
        self.assertEqual((c["n_well_resolved"], c["n_mid_resolved"]), (0, 0))

    def test_dropped_cells_differ_is_mc_unresolved(self):
        F, J, _ = planted(np.array([0.02, 0.3]), seed=1)
        f = dict(P.decompose(F, J), keep=np.array([True, True, True]))
        g = dict(f, keep=np.array([True, False, True]))
        ok, rec = P.mc_partition_ok({"full": f, "A": f, "B": g})
        self.assertFalse(ok)
        self.assertTrue(rec["dropped_cells_differ"])
        self.assertIsNone(P.matched_counts({"full": f, "A": f, "B": g})["n_well_resolved"])

    def test_r_independent_route_and_m2_sentences(self):
        F, J, Q = planted(np.array([0.05, 0.5]), seed=2)
        d = P.decompose(F, J)
        b0, arm = 0.1 * Q[:, 0] + 0.1 * Q[:, 1], 0.1 * Q[:, 0] + 0.02 * Q[:, 1]
        a, b = P.r_pair(d, arm, b0), P.r_independent(d, arm, b0)
        self.assertAlmostEqual(a["r_poor"], b["r_poor"], places=12)
        self.assertAlmostEqual(a["r_well"], b["r_well"], places=12)
        none = P.decompose(*planted(np.array([0.3, 0.6]))[:2])
        self.assertIsNone(P.r_independent(none, arm, b0)["r_well"])
        v = {"k": 5, "b0_k": 5, "r_poor": {"label": "removes most"}, "r_well": {"label": "no change"}}
        self.assertIn("remove mainly the poorly constrained part", P.m2_sentences("MO", v)[0])
        v2 = {"k": 2, "b0_k": 5, "r_poor": {"label": "no change"}, "r_well": {"label": "removes most"}}
        out = P.m2_sentences("OP", v2)
        self.assertIn("remove mainly the well-constrained part", out[0])
        self.assertIn("k = 2", out[1])
        self.assertEqual(P.m2_sentences("MO", {"k": 5, "b0_k": 5, "r_poor": {"label": "removes part"},
                                                "r_well": {"label": "no change"}}), [])

    def test_nprec_failure_branches(self):
        F, J, Q = planted(np.array([0.03, 0.2, 0.5]), seed=7)
        a = P.decompose(F, J)
        beta = np.array([0.01, 0.02, -0.03])
        ea = P.evaluate(a, beta, "single")
        self.assertFalse(P.nprec(a, dict(a, n_well=a["n_well"] + 1), ea, ea))
        self.assertFalse(P.nprec(a, a, ea, dict(ea, S_poor=ea["S_poor"] + 0.02)))
        self.assertFalse(P.nprec(a, a, ea, dict(ea, Z_well=None)))
        self.assertFalse(P.nprec(a, a, ea, dict(ea, Z_well=ea["Z_well"] + 0.5)))


class MCRule(unittest.TestCase):
    def test_hungarian_matching_on_a_permuted_sign_flipped_basis(self):
        F, J, Q = planted(np.array([0.02, 0.05, 0.3, 0.6]), seed=9)
        f = P.decompose(F, J)
        a = dict(f, w=-f["w"][:, ::-1], s=f["s"][::-1])
        b = dict(f, w=f["w"][:, [1, 0, 3, 2]], s=f["s"][[1, 0, 3, 2]])
        c = P.matched_counts({"full": f, "A": a, "B": b})
        self.assertEqual((c["n_well_resolved"], c["n_mid_resolved"], c["dim_inf"]), (2, 2, 0))

    def test_a_rotated_basis_below_the_overlap_bar_is_not_matched(self):
        F, J, Q = planted(np.array([0.02, 0.05, 0.6]), seed=9)
        f = P.decompose(F, J)
        w = f["w"].copy()
        c, s_ = np.cos(np.pi / 4), np.sin(np.pi / 4)
        w[:, 0], w[:, 1] = c * f["w"][:, 0] + s_ * f["w"][:, 1], -s_ * f["w"][:, 0] + c * f["w"][:, 1]
        b = dict(f, w=w)
        cnt = P.matched_counts({"full": f, "A": f, "B": b})
        self.assertEqual(cnt["n_well_resolved"], 0)          # overlaps 0.707 < 0.9
        self.assertEqual(cnt["n_mid_resolved"], 1)

    def test_crossing_widths_are_not_counted(self):
        F, J, Q = planted(np.array([0.02, 0.09, 0.3]), seed=9)
        f = P.decompose(F, J)
        a = dict(f, s=np.where(np.isclose(f["s"], 0.09), 0.11, f["s"]))
        c = P.matched_counts({"full": f, "A": a, "B": f})
        self.assertEqual((c["n_well_resolved"], c["unmatched_or_crossing"]), (1, 1))

    def test_partition_rule(self):
        F, J, Q = planted(np.array([0.02, 0.3]), seed=1)
        f = P.decompose(F, J)
        ok, _ = P.mc_partition_ok({"full": f, "A": f, "B": f})
        self.assertTrue(ok)
        F2, _, _ = planted(np.array([0.02, 0.3]), seed=2)      # a rotated well axis
        g = P.decompose(F2, J)
        ok, rec = P.mc_partition_ok({"full": f, "A": f, "B": g})
        self.assertFalse(ok)
        self.assertGreater(rec["proj_AB"], P.MC_PROJ)


class Marginal(unittest.TestCase):
    def test_summing_reco_axes_equals_direct_binning(self):
        rng = np.random.default_rng(0)
        reco = rng.uniform(0, 1, (5000, 3))
        truth = rng.integers(0, 4, 5000)
        w = rng.uniform(0.5, 1.5, 5000)
        edges = [np.linspace(0, 1, 3), np.linspace(0, 1, 3), np.linspace(0, 1, 4)]
        idx = [np.clip(np.searchsorted(e, reco[:, i], side="right") - 1, 0, len(e) - 2) for i, e in enumerate(edges)]
        flat3 = np.ravel_multi_index(idx, (2, 2, 3))
        R3 = np.zeros((12, 4))
        np.add.at(R3, (flat3, truth), w)
        flat2 = np.ravel_multi_index(idx[:2], (2, 2))
        R2 = np.zeros((4, 4))
        np.add.at(R2, (flat2, truth), w)
        b3 = np.bincount(flat3, weights=w, minlength=12)
        Rm, bm = P.marginal(sparse.csr_matrix(R3), b3, (2, 2, 3), (2,))
        np.testing.assert_allclose(Rm.toarray(), R2, rtol=1e-12)
        np.testing.assert_allclose(bm, np.bincount(flat2, weights=w, minlength=4), rtol=1e-12)
        t0 = np.full(4, 10.0)
        np.testing.assert_allclose(P.fisher_c(did, Rm, t0, bm), P.fisher_c(did, R2, t0, bm), rtol=1e-12)


class RID(unittest.TestCase):
    ref = {"sigma_rel": [0.1, float("inf"), 0.3], "null_fraction": [0.0, 1.0, 0.0], "n_null_modes": 1, "n_cells_grid": 29}

    def test_equal_passes(self):
        self.assertTrue(P.compare_rid(dict(self.ref), self.ref)[0])

    def test_failures(self):
        for change in ({"sigma_rel": [0.1, 0.2, 0.3]}, {"sigma_rel": [0.1 * (1 + 2e-6), float("inf"), 0.3]},
                       {"null_fraction": [0.0, 1.0, 2e-6]}, {"n_null_modes": 2}, {"n_cells_grid": 28}):
            self.assertFalse(P.compare_rid({**self.ref, **change}, self.ref)[0], change)


# ---------------------------------------------------------------------------------------------- end to end
def make_fixture(root: Path, seed: int = 11) -> tuple[Path, dict]:
    """Small products and operands built so that every control passes; returns (products dir, operands mapping)."""
    rng = np.random.default_rng(seed)
    shape, nH, nT1, nf = [2, 2, 2, 2, 3], 18, 10, 48
    prod = root / "build"
    prod.mkdir(parents=True)
    names = [f"F{i}" for i in range(6)]

    def resp(n_reco, n_cols, mask_p=0.6):
        R = rng.uniform(0.1, 1.0, (n_reco, n_cols)) * (rng.random((n_reco, n_cols)) < mask_p)
        R[rng.integers(0, n_reco, n_cols), np.arange(n_cols)] += 0.5
        return R / R.sum(axis=0, keepdims=True) * 0.6
    Rf = resp(nf, nH)
    t0 = rng.uniform(1e4, 2e4, nH)
    L = rng.uniform(0.5, 1.5, (16, nH)) * (rng.random((16, nH)) < 0.7) + np.eye(16, nH)
    M16 = rng.uniform(0, 1, (16, nf))
    z5 = {"gw_U": M16}

    def put(prefix, R, prior, Lm=None, bx=None):
        Rs = sparse.csr_matrix(R)
        z5.update({f"{prefix}__R_data": Rs.data, f"{prefix}__R_indices": Rs.indices.astype(np.int32),
                   f"{prefix}__R_indptr": Rs.indptr.astype(np.int32), f"{prefix}__R_shape": np.array(Rs.shape),
                   f"{prefix}__b_known": rng.uniform(0, 1, nf),
                   f"{prefix}__b_extra": rng.uniform(1, 5, nf) if bx is None else bx,
                   f"{prefix}__prior": prior, f"{prefix}__u_fine": rng.uniform(1, 2, nf),
                   f"{prefix}__cell_of_fine": rng.integers(0, R.shape[1], nf), f"{prefix}__n_cells": np.array(R.shape[1])})
        if Lm is not None:
            z5[f"{prefix}__L"], z5[f"{prefix}__L_t0"] = Lm, Lm @ prior
    put("h2_full", Rf, t0, L)
    put("h2_halfA", Rf * rng.uniform(0.99, 1.01, Rf.shape), t0 * rng.uniform(0.99, 1.01, nH), L)
    put("h2_halfB", Rf * rng.uniform(0.99, 1.01, Rf.shape), t0 * rng.uniform(0.99, 1.01, nH), L)
    put("h2_rid", Rf, t0)
    R1, t1 = resp(nf, nT1), rng.uniform(1e3, 2e3, nT1)
    put("t1_did", R1, t1, bx=np.zeros(nf))
    ibu_names = names + ["IBU1ONLY"]                 # a functional IBU-1 names and D-ID does not (Amendment C)
    maps = rng.uniform(0, 1, (len(ibu_names), nT1))
    z5["t1_did__maps"] = maps
    np.savez(prod / "r5d.npz", **z5)
    F1 = P.fisher_c(did, R1, t1, z5["t1_did__b_known"])
    lam, V = np.linalg.eigh(F1)
    sig, nul = did.widths_from_eig(lam, V, maps)
    srel = sig / np.abs(maps @ t1)
    all_names = names + ["DIDONLY"] + [f"X{i}" for i in range(178)]   # and one D-ID names and IBU-1 does not
    sr183, nf183 = np.full(183, np.nan), np.full(183, np.nan)
    sr183[:6], nf183[:6] = srel[:6], nul[:6]
    sr183[6], nf183[6] = 0.5, 0.0
    np.savez(root / "tables.npz", names=np.array(all_names), f183=np.arange(183),
             **{"T1/nominal/widths_nom/sigma_rel": sr183, "T1/nominal/widths_nom/null_fraction": nf183})
    rid = {"label": "x", "sigma_rel": list(rng.uniform(0.01, 0.2, 16)), "null_fraction": [0.0] * 16, "n_null_modes": 0,
           "n_cells_grid": nH}
    (prod / "r5d.json").write_text(json.dumps({"world_shape": shape, "axes": ["pt", "pz", "eavail", "q3", "W"],
                                               "C-L_linearity_rel": 0.0, "R-ID_rebuilt": rid, "t1_names": ibu_names,
                                               "n_cells": {"h2": nH, "t1": nT1, "h2_rid": nH, "h2_nonempty_coarse": nH}}))
    # 2D
    T = rng.uniform(50, 100, 224)
    M = (np.eye(224) * 0.5 + rng.uniform(0, 0.1, (224, 224)) / 224) * T[None, :]
    sel = np.sort(rng.choice(224, 205, replace=False))
    z2 = {"d2__b_bkg": rng.uniform(1, 3, 224), "d2__truth_nominal": T.copy(), "d2__factor": np.ones(224),
          "d2__selected_ids": sel, "d2__selected_mask": np.isin(np.arange(224), sel), "d2__bank_ibu_response": M,
          "d2__bank_ibu_prior": T}
    z2["d2__b_bkg_globalindex"] = z2["d2__b_bkg"].copy()
    for h, k in (("full", 1.0), ("halfA", 1.01), ("halfB", 0.99)):
        z2.update({f"d2_{h}__T": T * k, f"d2_{h}__M": M * k, f"d2_{h}__b_known": np.zeros(224),
                   f"d2_{h}__b_known_ibukt": np.zeros(224)})
    np.savez(prod / "r2d.npz", **z2)
    (prod / "r2d.json").write_text(json.dumps({"C-2D": {"M_vs_bank_ibu_response_max_abs": 0.0,
                                                        "T_vs_bank_ibu_prior_max_rel": 0.0}}))
    # T3 and FD-PRR
    z3 = {"M16": M16}
    table = {}
    for s in P.SPLITS:
        z3[f"t3__P__s{s}"] = L @ t0 * rng.uniform(0.99, 1.01, 16)
        for arm, ks in (("B0", (5, 50)), ("MO", (5, 50)), ("OP", (2,))):
            for k in ks:
                z3[f"t3__b__{arm}__A7_gibuu__s{s}__k{k}"] = rng.normal(0, 0.03, 16)
        table[f"B0/A7_gibuu/s{s}"] = {"b": z3[f"t3__b__B0__A7_gibuu__s{s}__k5"].tolist(), "d": list(rng.normal(0, 0.1, 16))}
    for arm, ks in (("B0", (5, 50)), ("MO", (5, 50)), ("OP", (2,))):
        for k in ks:
            z3[f"t3__b__{arm}__q3__s991000__k{k}"] = rng.normal(0, 0.03, 16)
    table["B0/q3/s991000"] = {"b": z3["t3__b__B0__q3__s991000__k5"].tolist(), "d": list(rng.normal(0, 0.1, 16))}
    for t in P.F0B_PRIMARY + ("closure_nuwro",):
        table.setdefault(f"B0/{t}/s991000", {"b": list(rng.normal(0, 0.03, 16)), "d": list(rng.normal(0, 0.1, 16))})
    np.savez(prod / "t3.npz", **z3)
    (prod / "t3.json").write_text("{}")
    sums = "\n".join(f"{P.sha256(prod / f)}  {f}" for f in ("r5d.npz", "r5d.json", "r2d.npz", "r2d.json", "t3.npz", "t3.json"))
    (prod / "SHA256SUMS").write_text(sums + "\n")
    ops = {}

    def op(key, name, obj):
        p = root / name
        p.write_text(json.dumps(obj))
        ops[key] = (p, P.sha256(p))
    op("fdprr", "fdprr.json", {"R-ID": rid, "table": table})
    truths = [{"name": t, "bias": list(rng.normal(0, 0.03, 16)), "noise_sigma": list(rng.uniform(0.001, 0.004, 16))}
              for t in P.F0B_PRIMARY + ("closure_nuwro", "P1r")]
    op("f0b", "f0b.json", {"truths": truths})
    op("f0b_cpl", "f0b_cpl.json", {"truths": truths})
    op("t3_readout", "t3r.json", {"verdict": "COMPLETE"})
    a2t = {}
    for t in P.A2_PRIMARY + P.A2_SECONDARY:
        entry = {"cells": sel.tolist()}
        for m in ("omnifold", "ibu5", "ibu10"):
            res = rng.normal(0, 0.02, (5, 205))
            entry[m] = {"residuals": res.tolist(), "mean": np.mean(res, axis=0).tolist(),
                        "departure": list(rng.normal(0, 0.1, 205))}
        a2t[t] = entry
    op("a2", "a2.json", {"truths": a2t, "bank_sha256": P.BANK_SHA})
    ops["did_tables"] = (root / "tables.npz", P.sha256(root / "tables.npz"))
    return prod, ops


class Pins(unittest.TestCase):
    def test_the_recorded_c_did_expectation(self):
        self.assertEqual(P.C_DID_COMMON_EXPECTED, 151)
        self.assertEqual(P.F0B_SECONDARY_WITH_D, ("closure_nuwro",))


class Problems(unittest.TestCase):
    def test_5d_gradient_is_the_count_space_one(self):
        """Section 3.3: J = diag(1/f0) L (count space, the gradient widths_from_eig uses), f0 = L t0."""
        with tempfile.TemporaryDirectory() as d:
            prod, _ = make_fixture(Path(d))
            z5 = np.load(prod / "r5d.npz")
            p = P.problem_5d(z5, "h2_full", did)
        L, t0 = z5["h2_full__L"], z5["h2_full__prior"]
        f0 = L @ t0
        np.testing.assert_allclose(p["f0"], f0, rtol=1e-15)
        np.testing.assert_allclose(p["J"], L / f0[:, None], rtol=1e-15)
        b = z5["h2_full__b_known"] + z5["h2_full__b_extra"]
        np.testing.assert_allclose(p["F"], P.fisher_c(did, P.csr(z5, "h2_full"), t0, b), rtol=1e-15)

    def test_2d_gradient_selects_the_cells_in_order(self):
        with tempfile.TemporaryDirectory() as d:
            prod, _ = make_fixture(Path(d))
            z2 = np.load(prod / "r2d.npz")
            cells = z2["d2__selected_ids"]
            p = P.problem_2d(z2, "full", cells)
        T = z2["d2_full__T"]
        self.assertEqual(p["J"].shape, (205, 224))
        for r, c in enumerate(cells):
            self.assertEqual(p["J"][r, c], 1.0 / T[c])
            self.assertEqual(np.count_nonzero(p["J"][r]), 1)


FIXTURE_COMMON = 6   # the fixture's shared functional set (the real inputs' is pinned at 151)


class EndToEnd(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(P, "C_DID_COMMON_EXPECTED", FIXTURE_COMMON)
        p.start()
        self.addCleanup(p.stop)

    def test_c_did_reads_the_declared_intersection(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            with mock.patch.dict(P.OPERANDS, ops):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 0, rec.get("stops"))
        c = rec["controls"]["C-DID"]
        self.assertEqual((c["functionals_compared"], c["ibu1_only"]), (6, ["IBU1ONLY"]))
        self.assertIn("DIDONLY", c["did_only"])

    def test_c_did_stops_when_the_intersection_is_not_the_expected_size(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "C_DID_COMMON_EXPECTED", 7):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 3)
        self.assertEqual(rec["stops"], ["C-DID"])

    def test_c_2d_takes_the_declared_relative_bar(self):
        for scale, want in ((1e-14, 0), (1e-9, 3)):
            with tempfile.TemporaryDirectory() as d:
                prod, ops = make_fixture(Path(d))
                z2 = dict(np.load(prod / "r2d.npz"))
                z2["d2_full__M"] = z2["d2_full__M"] * (1 + scale)
                np.savez(prod / "r2d.npz", **z2)
                sums = "\n".join(f"{P.sha256(prod / f)}  {f}" for f in ("r5d.npz", "r5d.json", "r2d.npz", "r2d.json", "t3.npz", "t3.json"))
                (prod / "SHA256SUMS").write_text(sums + "\n")
                with mock.patch.dict(P.OPERANDS, ops):
                    rc = P.run(prod, Path(d) / "out")
                rec = json.loads((Path(d) / "out/readout.json").read_text())
            self.assertEqual(rc, want, (scale, rec.get("stops")))
            if want:
                self.assertIn("C-2D", rec["stops"])

    def test_c_d_covers_the_secondary_truth_converted_with_d(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            fd = json.loads(ops["fdprr"][0].read_text())
            del fd["table"]["B0/closure_nuwro/s991000"]
            ops["fdprr"][0].write_text(json.dumps(fd))
            ops["fdprr"] = (ops["fdprr"][0], P.sha256(ops["fdprr"][0]))
            with mock.patch.dict(P.OPERANDS, ops):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 3)
        self.assertIn("C-D", rec["stops"])
        self.assertEqual(rec["controls"]["C-D"]["printed_without_d"], ["P1r"])
    def test_controls_pass_and_the_readout_is_written(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            with mock.patch.dict(P.OPERANDS, ops):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 0, rec.get("stops"))
        self.assertEqual(rec["stops"], [])
        self.assertTrue(all(v["pass"] for v in rec["controls"].values()))
        for k in ("M1", "M1_across", "M2", "M3", "M4", "secondary", "printed"):
            self.assertIn(k, rec)
        self.assertEqual(set(rec["M1"]["5D-F0b"]), set(P.F0B_PRIMARY))
        self.assertEqual(rec["M2"]["OP"]["k"], 2)
        self.assertEqual(rec["M2"]["MO"]["k"], 5)
        self.assertIn("5D k=50, secondary; not M2", rec["secondary"])
        # FD-PRR's b in phi units: b * P / f0, the five-split mean (section 3.5)
        with tempfile.TemporaryDirectory() as d2:
            prod2, ops2 = make_fixture(Path(d2))
            z5, z3 = np.load(prod2 / "r5d.npz"), np.load(prod2 / "t3.npz")
            f0 = z5["h2_full__L"] @ z5["h2_full__prior"]
            fd = json.loads(ops2["fdprr"][0].read_text())
            want = np.mean([np.asarray(fd["table"][f"B0/A7_gibuu/s{s}"]["b"]) * z3[f"t3__P__s{s}"] / f0 for s in P.SPLITS], axis=0)
        self.assertAlmostEqual(rec["M1"]["5D-B0"]["A7_gibuu"]["norm"], float(np.linalg.norm(want)), places=12)

    def test_m2_r_numerically_unresolved_and_route_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            real = P.evaluate_r

            def drift(dec, *a):
                out = real(dec, *a)
                if dec.get("_tag") == "evr":
                    for k in out:
                        if out[k]["value"] is not None:
                            out[k] = dict(out[k], value=out[k]["value"] + 0.05)
                return out
            real_dec = P.decompose

            def tagged(F, J, driver="numpy", cut=P.CUT):
                return dict(real_dec(F, J, driver, cut), _tag=driver)
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "evaluate_r", drift), \
                    mock.patch.object(P, "decompose", tagged):
                P.run(prod, Path(d) / "o1")
            r1 = json.loads((Path(d) / "o1/readout.json").read_text())
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "r_independent", lambda dec, a, b: {"r_poor": -9.0, "r_well": -9.0}):
                rc = P.run(prod, Path(d) / "o2")
            r2 = json.loads((Path(d) / "o2/readout.json").read_text())
        labels = [r1["M2"][a][n]["label"] for a in ("MO", "OP") for n in ("r_poor", "r_well")]
        self.assertIn("numerically unresolved", labels)
        self.assertEqual(rc, 3)
        self.assertEqual(r2["stops"], ["C-ROUTE"])

    def test_c_l_rejects_out_of_range_ids(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            z2 = dict(np.load(prod / "r2d.npz"))
            z2["d2__selected_ids"] = z2["d2__selected_ids"].copy()
            z2["d2__selected_ids"][-1] = 300
            np.savez(prod / "r2d.npz", **z2)
            a2 = json.loads(ops["a2"][0].read_text())
            for t in a2["truths"].values():
                t["cells"] = z2["d2__selected_ids"].tolist()
            ops["a2"][0].write_text(json.dumps(a2))
            ops["a2"] = (ops["a2"][0], P.sha256(ops["a2"][0]))
            sums = "\n".join(f"{P.sha256(prod / f)}  {f}" for f in ("r5d.npz", "r5d.json", "r2d.npz", "r2d.json", "t3.npz", "t3.json"))
            (prod / "SHA256SUMS").write_text(sums + "\n")
            with mock.patch.dict(P.OPERANDS, ops):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 3)
        self.assertIn("C-L", rec["stops"])

    def test_a_c_rho_failure_stops_after_the_decompositions(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            with mock.patch.dict(P.OPERANDS, ops), \
                    mock.patch.object(P, "rho_coordinate", lambda dec, J: (np.zeros(J.shape[0]), np.ones(J.shape[0]))):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 3)
        self.assertEqual(rec["stops"], ["C-RHO"])
        self.assertNotIn("M1", rec)

    def test_a_t3_mismatch_fails_c_t3(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            fd = json.loads(ops["fdprr"][0].read_text())
            fd["table"]["B0/A7_gibuu/s994002"]["b"][3] += 1e-9
            ops["fdprr"][0].write_text(json.dumps(fd))
            ops["fdprr"] = (ops["fdprr"][0], P.sha256(ops["fdprr"][0]))
            with mock.patch.dict(P.OPERANDS, ops):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 3)
        self.assertIn("C-T3", rec["stops"])

    def test_a_failed_stop_control_computes_no_reading(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            fd = json.loads(ops["fdprr"][0].read_text())
            fd["R-ID"]["n_null_modes"] = 3
            ops["fdprr"][0].write_text(json.dumps(fd))
            ops["fdprr"] = (ops["fdprr"][0], P.sha256(ops["fdprr"][0]))
            with mock.patch.dict(P.OPERANDS, ops):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 3)
        self.assertIn("C-RID", rec["stops"])
        self.assertNotIn("M1", rec)

    def test_a_changed_operand_fails_c_ops(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            ops["t3_readout"] = (ops["t3_readout"][0], "0" * 64)
            with mock.patch.dict(P.OPERANDS, ops):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 3)
        self.assertIn("C-OPS", rec["stops"])

    def test_c_route_failure_stops(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "route_independent", lambda dec, b: (-1.0, None)):
                rc = P.run(prod, Path(d) / "out")
            rec = json.loads((Path(d) / "out/readout.json").read_text())
        self.assertEqual(rc, 3)
        self.assertEqual(rec["stops"], ["C-ROUTE"])
        self.assertNotIn("M1", rec)

    def test_numerically_and_mc_unresolved_relabel(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            with mock.patch.dict(P.OPERANDS, ops), mock.patch.object(P, "nprec", lambda *a: False):
                P.run(prod, Path(d) / "o1")
            r1 = json.loads((Path(d) / "o1/readout.json").read_text())
            with mock.patch.dict(P.OPERANDS, ops), \
                    mock.patch.object(P, "mc_partition_ok", lambda decs: (False, {"forced": True})):
                P.run(prod, Path(d) / "o2")
            r2 = json.loads((Path(d) / "o2/readout.json").read_text())
        self.assertTrue(all(v["S_label"] == "numerically unresolved" for v in r1["M1"]["5D-F0b"].values()))
        self.assertTrue(all(v["S_label"] == "MC-unresolved" for v in r2["M1"]["2D-A2"].values()))
        self.assertEqual(r2["M2"]["MO"]["r_poor"]["label"] in ("MC-unresolved", "no poorly constrained component to remove"), True)

    def test_main_refuses_a_changed_code_pin(self):
        pins = {"did.py": (P.CODE_PINS["did.py"][0], "0" * 64)}
        with mock.patch.dict(P.CODE_PINS, pins):
            self.assertEqual(P.main(["run", "--products", "x", "--out", "y"]), 9)

    def test_the_module_entry_point(self):
        """The __main__ line runs: with no subcommand argparse exits 2, before anything is read."""
        import runpy
        with mock.patch.object(sys, "argv", ["msr_project.py"]), self.assertRaises(SystemExit) as cm:
            runpy.run_path(P.__file__, run_name="__main__")
        self.assertEqual(cm.exception.code, 2)

    def test_main_runs_with_pins(self):
        with tempfile.TemporaryDirectory() as d:
            prod, ops = make_fixture(Path(d))
            with mock.patch.dict(P.OPERANDS, ops):
                rc = P.main(["run", "--products", str(prod), "--out", str(Path(d) / "o2")])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
