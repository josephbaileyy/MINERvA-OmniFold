#!/usr/bin/env python3
"""Fail-closed gate tests for the standard P4 lateral repair (2026-07-18).

Covers the eight verifier-identified failure modes: missing endpoint, truncated/
incomplete output, missing census/migration evidence, zero/absent component,
order/hash mismatch, missing support block, component-sum mismatch, invalid
projection. ROOT-free. Also checks the preserved MAT two-endpoint formula and
that the happy path does NOT false-trip.
"""
import sys, unittest
from pathlib import Path
import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
import p4_lib as P
from p4_lib import P4GateError


def _band_cov(minus, plus):
    """MAT two-endpoint block via uq_math (preserved formula)."""
    from uq_math import mat_covariance
    return mat_covariance(np.stack([np.asarray(minus, float), np.asarray(plus, float)]))


class ManifestAndConfig(unittest.TestCase):
    def test_missing_endpoint_fails(self):
        entries = [(b, e, "fp") for (b, e) in P.canonical_endpoints()][:-1]  # 9/10
        with self.assertRaises(P4GateError):
            P.endpoint_manifest_hash(entries)

    def test_full_inventory_hashes_and_is_order_independent(self):
        full = [(b, e, f"{b}{e}") for (b, e) in P.canonical_endpoints()]
        h1 = P.endpoint_manifest_hash(full)
        h2 = P.endpoint_manifest_hash(list(reversed(full)))
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_truncated_incomplete_unfold_set_fails(self):
        present = {f"{b}_{e}" for (b, e) in P.canonical_endpoints()}
        present.discard("MuonResolution_1")  # truncated -> failed content-validation
        with self.assertRaises(P4GateError):
            P.require_complete_unfold_set(present)
        P.require_complete_unfold_set({f"{b}_{e}" for (b, e) in P.canonical_endpoints()})

    def test_config_hash_and_validate(self):
        good = P.P4Config(seed=42, iters=5, use_weights=True, universe=None)
        self.assertTrue(good.validate())
        self.assertNotEqual(good.hash(), P.P4Config(seed=7).hash())         # order/hash mismatch
        with self.assertRaises(P4GateError):
            P.P4Config(universe="BeamAngleX:0").validate()                  # must be nominal
        with self.assertRaises(P4GateError):
            P.P4Config(seed=7).validate()


class MergedAudit(unittest.TestCase):
    def _meta(self, **ov):
        m = {"tree_entries": {"mc_truth_denom": 100, "mc_signal_reco": 100,
                              "mc_background": 5, "data": 20},
             "mcPOT": 1.2e20, "dataPOT": 3.4e19, "hasTruthOnlyMisses": 1,
             "nTruthOnlyMisses": 66989,
             "census": {"TruthEntrants": 0, "TruthExits": 0,
                        "RecoEntrants": 21, "RecoExits": 21},
             "migration_policy": "active-universe selection-complete"}
        m.update(ov); return m

    def test_happy_path(self):
        self.assertTrue(P.check_merged_metadata(self._meta()))

    def test_missing_census_evidence_fails(self):
        m = self._meta(census={"TruthEntrants": 0})  # missing 3 counters
        with self.assertRaises(P4GateError):
            P.check_merged_metadata(m)

    def test_missing_migration_policy_fails(self):
        with self.assertRaises(P4GateError):
            P.check_merged_metadata(self._meta(migration_policy=""))

    def test_completeness_equality_and_empty_tree_and_pot(self):
        with self.assertRaises(P4GateError):     # signal_reco != truth_denom
            P.check_merged_metadata(self._meta(tree_entries={
                "mc_truth_denom": 100, "mc_signal_reco": 98,
                "mc_background": 5, "data": 20}))
        with self.assertRaises(P4GateError):     # empty tree
            P.check_merged_metadata(self._meta(tree_entries={
                "mc_truth_denom": 100, "mc_signal_reco": 100,
                "mc_background": 0, "data": 20}))
        with self.assertRaises(P4GateError):     # non-positive POT
            P.check_merged_metadata(self._meta(mcPOT=0.0))


class ComponentGates(unittest.TestCase):
    def _bands(self):
        rng = np.random.default_rng(0)
        d = {}
        for b in P.BANDS:
            m = rng.normal(1.0, 0.05, 4); p = rng.normal(1.0, 0.05, 4)
            d[b] = _band_cov(m, p)
        return d

    def test_mat_two_endpoint_formula_preserved(self):
        minus = np.array([8.0, 22.0]); plus = np.array([14.0, 18.0])
        expected = np.outer((plus - minus) / 2, (plus - minus) / 2)
        np.testing.assert_allclose(_band_cov(minus, plus), expected)

    def test_exact_bands_required(self):
        b = self._bands(); P.require_exact_bands(b)
        b.pop("Muon_Energy_MINOS")
        with self.assertRaises(P4GateError):
            P.require_exact_bands(b)
        b2 = self._bands(); b2["ExtraBand"] = b2["BeamAngleX"]
        with self.assertRaises(P4GateError):
            P.require_exact_bands(b2)

    def test_zero_or_absent_component_fails(self):
        b = self._bands(); b["BeamAngleX"] = np.zeros((4, 4))  # zero component
        with self.assertRaises(P4GateError):
            P.component_traces_positive_finite(b)
        b2 = self._bands(); del b2["BeamAngleY"]               # absent component
        with self.assertRaises(P4GateError):
            P.component_traces_positive_finite(b2)

    def test_component_sum_exact_and_mismatch(self):
        b = self._bands()
        total = sum(b[k] for k in P.BANDS)
        self.assertLessEqual(P.check_component_sum(total, b), 1e-9)
        with self.assertRaises(P4GateError):
            P.check_component_sum(total * 1.01, b)             # component-sum mismatch


class SupportAndPSD(unittest.TestCase):
    def test_missing_support_block_fails(self):
        A = np.eye(4)
        with self.assertRaises(P4GateError):
            P.check_support_comparison(A, None)                # missing support
        with self.assertRaises(P4GateError):
            P.check_support_comparison(None, A)
        r = P.check_support_comparison(2 * np.eye(4), np.eye(4))
        self.assertGreater(r["ratio"], 1.0)

    def test_psd_symmetry_gate(self):
        P.check_symmetric_psd(np.array([[4.0, 1.0], [1.0, 9.0]]))
        with self.assertRaises(P4GateError):                  # not PSD
            P.check_symmetric_psd(np.array([[1.0, 2.0], [2.0, 1.0]]))


class Projection(unittest.TestCase):
    def test_mask_order_hash_mismatch(self):
        m1 = np.zeros(P.GRID_NBINS, bool); m1[:100] = True
        m2 = np.zeros(P.GRID_NBINS, bool); m2[1:101] = True
        h1, n1 = P.mask_order_hash(m1); h2, _ = P.mask_order_hash(m2)
        self.assertNotEqual(h1, h2)
        self.assertEqual(n1, 100)
        with self.assertRaises(P4GateError):
            P.mask_order_hash(np.zeros(P.GRID_NBINS, bool))   # zero reported bins

    def test_projection_nonmutation_and_invalid(self):
        C = np.diag([4.0, 9.0, 16.0])
        M = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 1.0]])      # sum drop-axis
        x = np.array([2.0, 3.0, 5.0]); xlow = M @ x
        Clow, st = P.check_projection_nonmutation(C, M, x, xlow)
        self.assertEqual(Clow.shape, (2, 2))
        Mbad = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 1.0]])
        xlow_wrong = np.array([2.0, 99.0])                    # invalid projection (mutated central)
        with self.assertRaises(P4GateError):
            P.check_projection_nonmutation(C, Mbad, x, xlow_wrong)


if __name__ == "__main__":
    unittest.main(verbosity=2)
