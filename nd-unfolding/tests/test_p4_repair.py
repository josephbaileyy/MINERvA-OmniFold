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
import p4_adopt_standard as ADOPT     # OI-128: for the gate name, so it is never respelled here


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


# REPAIR-7 item 3: class MergedAudit is REMOVED along with `p4_lib.check_merged_metadata`.
#
# It was eight tests against a function with no production caller. Deleting the function without
# deleting its tests would leave a suite that cannot run; keeping the tests would mean keeping a
# dead function alive purely to satisfy them, which is how the dead path survived three rounds.
#
# **This is a real coverage REDUCTION and is declared, not hidden.** The equivalent checks now
# live in p4_evidence.py's inline path -- tree completeness, POT positivity, census counters,
# the native-miss comparison, and the two-sided migration-policy check. That path imports ROOT,
# so it cannot be unit-tested here and is exercised only when the evidence stage runs on the
# cluster. Restoring laptop-side coverage means extracting those checks into a ROOT-free helper
# AND wiring it into p4_evidence in the same change -- introduced WITH its caller, which is the
# rule that would have prevented the original dead gate.


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

    def test_projection_validity_is_gated(self):
        """RE-SPECIFIED 2026-08-09: what is gated is the projection's own validity, which is a
        recomputation identity, not agreement with a separately-produced product."""
        C = np.diag([4.0, 9.0, 16.0])
        M = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 1.0]])      # sum drop-axis
        Clow, st = P.check_projection_validity(C, M)
        self.assertEqual(Clow.shape, (2, 2))
        self.assertLess(st["projection_identity_relerr"], 1e-12)
        with self.assertRaises(P4GateError):                   # non-PSD input must still fail
            P.check_projection_validity(np.diag([1.0, -5.0, 1.0]), M)

    def test_marginal_crosscheck_reports_and_never_raises(self):
        """The cross-check has NO pass/fail by specification. Demonstrated: a disagreement that
        the retired 3% gate would have rejected is reported, not raised."""
        M = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 1.0]])
        x = np.array([2.0, 3.0, 5.0])
        indep = np.array([2.0, 4.0])                           # 100% off on the second bin
        out = P.crosscheck_marginal_vs_independent(M, x, indep)   # must NOT raise
        self.assertEqual(out["n_bins"], 2)
        self.assertAlmostEqual(out["max_abs_rel"], 1.0)
        self.assertEqual(out["n_over_3pct"], 1)
        self.assertIn("NO pass/fail", out["note"])

    def test_crosscheck_reports_a_distribution_not_only_a_max(self):
        """BEN-064: a bare max is owned by the worst bin. One wildly-off bin among many good ones
        must not be able to hide the body of the comparison."""
        M = np.eye(100)
        x = np.ones(100)
        indep = np.ones(100)
        indep[0] = 1e-6                                        # one degenerate bin -> huge rel
        out = P.crosscheck_marginal_vs_independent(M, x, indep)
        self.assertGreater(out["max_abs_rel"], 1e5)            # the max is enormous...
        self.assertEqual(out["median_abs_rel"], 0.0)           # ...and the body is perfect
        self.assertEqual(out["n_over_3pct"], 1)

    # ---------------------------------------------------------------- N3 / N4 repair, 2026-08-16
    @staticmethod
    def _recipe():
        """A real width-weighted recipe with UNEQUAL dropped-axis widths, so a weight error is
        distinguishable from a mapping error."""
        edges = [np.array([0., 1., 2.])] * 4 + [np.array([0., 0.5, 1.5, 3.0])]   # W widths .5,1,1.5
        nb = [len(e) - 1 for e in edges]
        mh = np.ones(int(np.prod(nb)), bool)
        ml = P.reachable_low_mask(edges, 4, mh)
        return edges, 4, mh, ml

    def test_a_corrupted_M_is_REJECTED_by_the_recipe_gate(self):
        """THE BAR (B1, predeclared bf97279). The pre-repair projection gate could not detect a
        wrong M: both of its legs read M, so a corrupted M reproduced in both and PASSED at rel
        3.033e-17. This test fails on the pre-repair form -- where `check_projection_matrix_matches
        _recipe` does not exist at all -- and it fails on a wrong M, which is the whole point.

        BEN-344 is honoured INSIDE this test: the same instrument is shown returning a clean PASS
        on the good M in the same run, so 'it raised' is not confounded with 'it always raises'."""
        edges, ax, mh, ml = self._recipe()
        M = P.build_projection_M(edges, ax, mh, ml)

        st = P.check_projection_matrix_matches_recipe(M, edges, ax, mh, ml)   # non-null capability
        self.assertEqual(st["projection_M_recipe_max_abs_diff"], 0.0)
        self.assertEqual(st["projection_M_recipe_entries_differing"], 0)
        self.assertEqual(st["projection_M_recipe_nnz"], int(mh.sum()))        # one nonzero per column

        def scale_row(m):
            m[0, :] *= 3.0

        def scale_one_weight(m):
            r = int(np.nonzero(m[:, 0])[0][0])
            m[r, 0] *= 3.0

        def move_column_to_wrong_row(m):
            r = int(np.nonzero(m[:, 0])[0][0])       # capture BEFORE zeroing it
            w = m[r, 0]
            m[r, 0] = 0.0
            m[(r + 1) % m.shape[0], 0] = w

        def swap_two_rows(m):
            m[[0, 1], :] = m[[1, 0], :]

        for label, mutate in (("row scaled by 3 (the probe's corruption)", scale_row),
                              ("one weight scaled by 3", scale_one_weight),
                              ("one column moved to the wrong row", move_column_to_wrong_row),
                              ("two rows swapped", swap_two_rows)):
            bad = M.copy()
            mutate(bad)
            self.assertFalse(np.array_equal(bad, M), f"mutation did not change M: {label}")
            with self.assertRaises(P4GateError, msg=f"corrupted M accepted: {label}"):
                P.check_projection_matrix_matches_recipe(bad, edges, ax, mh, ml)

    def test_the_recomputation_identity_is_BLIND_to_a_wrong_M_and_says_so(self):
        """The other half of the bar, stated as a property rather than a hope. The identity gate is
        blind to a wrong M BY CONSTRUCTION -- both routes read M -- so this pins that limit in place
        instead of leaving a future reader to assume the gate covers the map. If someone later makes
        the identity gate M-sensitive, this test fails and the docstring gets revisited."""
        edges, ax, mh, ml = self._recipe()
        M = P.build_projection_M(edges, ax, mh, ml)
        rng = np.random.default_rng(20260816)
        A = rng.normal(size=(M.shape[1], M.shape[1]))
        C = A @ A.T / M.shape[1]
        bad = M.copy(); bad[0, :] *= 3.0
        _, st = P.check_projection_validity(C, bad)                # does NOT raise: blind
        self.assertLess(st["projection_identity_relerr"], 1e-9)
        self.assertFalse(st["projection_identity_gates_M"])        # and it reports its own blindness
        # ...while the recipe gate, on the SAME corrupted M in the SAME run, rejects it.
        with self.assertRaises(P4GateError):
            P.check_projection_matrix_matches_recipe(bad, edges, ax, mh, ml)

    def test_the_identity_route_is_not_the_same_product_re_associated(self):
        """N3's defect was that `direct` was `MH[i,:] @ M.T` with `MH = M @ C_high`, i.e. M C M^T
        with a different loop order, so the identity measured BLAS accumulation order. The repaired
        route must contain no matrix multiplication at all -- checked structurally, because a
        numeric check cannot distinguish two routes that agree to 1e-16 by construction."""
        import inspect
        src = inspect.getsource(P._block_sum_projection)
        body = "\n".join(l for l in src.splitlines()
                         if not l.strip().startswith(("#", '"', "'")))
        self.assertNotIn("@", body.split('"""')[-1], "the block-sum route still uses matmul")
        for banned in (".dot(", "np.dot", "np.matmul", "np.einsum", "np.tensordot"):
            self.assertNotIn(banned, body, f"the block-sum route still uses {banned}")
        # and it must still BE the projection, on a width-weighted M with unequal widths
        edges, ax, mh, ml = self._recipe()
        M = P.build_projection_M(edges, ax, mh, ml)
        rng = np.random.default_rng(11)
        A = rng.normal(size=(M.shape[1], M.shape[1]))
        C = A @ A.T / M.shape[1]
        ref = P.project(C, M)
        got = P._block_sum_projection(C, M)
        self.assertLess(float(np.max(np.abs(ref - got)) / np.max(np.abs(ref))), 1e-12)

    def test_identity_gate_still_catches_a_project_expression_bug(self):
        """The one thing the pre-repair leg DID do must survive the repair: a value-changing edit to
        project() is caught. 'The old check was useless' is too strong and this keeps it honest."""
        edges, ax, mh, ml = self._recipe()
        M = P.build_projection_M(edges, ax, mh, ml)
        rng = np.random.default_rng(5)
        A = rng.normal(size=(M.shape[1], M.shape[1]))
        C = A @ A.T / M.shape[1]
        orig = P.project
        try:
            P.project = lambda C_high, M_: 2.0 * orig(C_high, M_)   # still symmetric, still PSD
            with self.assertRaises(P4GateError):
                P.check_projection_validity(C, M)
        finally:
            P.project = orig
        P.check_projection_validity(C, M)                           # and passes once restored

    def test_crosscheck_reports_nonfinite_and_still_never_raises(self):
        """N4. A single nan silently poisoned every summary here -- median/p90/p99/max all become
        nan and `n_over_3pct` drops to 0 because `nan > 0.03` is False -- and the block was printed
        and written to the receipt as if it were a measurement. REPORT ONLY is unchanged: this must
        not raise. BEN-344: the same fields are shown clean in the same run."""
        M = np.eye(4)
        x = np.array([1.0, 1.0, 1.0, 1.0])
        clean = P.crosscheck_marginal_vs_independent(M, x, np.array([1.0, 1.0, 1.0, 2.0]))
        self.assertTrue(clean["all_finite"])                       # non-null capability, same run
        self.assertEqual(clean["n_nonfinite_rel"], 0)
        self.assertEqual(clean["n_over_3pct"], 1)

        # LOCALISED: one non-finite INDEPENDENT bin taints exactly its own bin.
        local = P.crosscheck_marginal_vs_independent(               # must NOT raise
            M, x, np.array([1.0, 1.0, 1.0, np.nan]))
        self.assertFalse(local["all_finite"])
        self.assertEqual(local["n_nonfinite_rel"], 1)
        self.assertEqual(local["n_nonfinite_independent"], 1)
        self.assertEqual(local["n_nonfinite_marginal"], 0)
        # the defect it makes visible: the all-bin summaries ARE nan and the count DID drop to 0
        self.assertTrue(np.isnan(local["median_abs_rel"]))
        self.assertTrue(np.isnan(local["max_abs_rel"]))
        self.assertEqual(local["n_over_3pct"], 0)                   # `nan > 0.03` is False
        # ...while the finite-only fields stay usable and the excluded bin is counted
        self.assertTrue(np.isfinite(local["max_abs_rel_finite_only"]))
        self.assertEqual(local["median_abs_rel_finite_only"], 0.0)
        self.assertIn("POISONED", local["note"])
        self.assertIn("NO pass/fail", local["note"])                # specification unchanged

        # AMPLIFIED, and this is why the counts are worth reporting rather than a bare flag: one
        # non-finite HIGH bin poisons EVERY low bin, because `0.0 * nan` is `nan`, so a zero entry
        # of M does not isolate it. Measured here as 1 bad input -> 4 of 4 bad outputs; on the real
        # products that is one bad 5D bin taking all 4825 reported 4D bins with it.
        amp = P.crosscheck_marginal_vs_independent(                 # must NOT raise
            M, np.array([1.0, np.nan, 1.0, 1.0]), np.array([1.0, 1.0, 1.0, 2.0]))
        self.assertEqual(amp["n_nonfinite_marginal"], 4)
        self.assertEqual(amp["n_nonfinite_rel"], 4)
        self.assertEqual(amp["n_bins"], 4)
        self.assertFalse(amp["all_finite"])
        self.assertTrue(np.isnan(amp["max_abs_rel_finite_only"]))   # nothing survives to summarise
        self.assertEqual(amp["n_over_3pct_finite_only"], 0)

    def test_production_path_gates_M_against_its_recipe(self):
        """Non-regression on the WIRING, not the library. The recipe gate only protects the campaign
        if the one production caller calls it; a library gate nobody invokes is the defect class this
        repair is fixing (a qualifying fact computed and not put where the reader looks)."""
        src = (ND / "p4_project_4d.py").read_text()
        self.assertIn("check_projection_matrix_matches_recipe", src)
        self.assertIn("projection_M_recipe_check", src)             # and it reaches the receipt
        self.assertIn("all_finite", src)                            # N4 fact reaches the log line

    def test_projection_M_rejects_an_unreachable_low_bin(self):
        """BEN-064, the masking defect: a reported LOW bin no HIGH bin reaches used to yield an
        all-zero row of M, which reached the central check as an exact 0 and reported rel=1.0
        no matter how negligible the bin was. It must now fail at CONSTRUCTION."""
        edges = [np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0]), np.array([0.0, 1.0]),
                 np.array([0.0, 1.0]), np.array([0.0, 1.0, 2.0])]
        nb = [2, 1, 1, 1, 2]
        mh = np.zeros(int(np.prod(nb)), bool)
        ml = np.ones(2, bool)                                  # both low bins reported
        mh[0] = True; mh[1] = True                             # only low bin 0 is reachable
        with self.assertRaises(P4GateError) as cm:
            P.build_projection_M(edges, 4, mh, ml)
        self.assertIn("receive no contribution", str(cm.exception))
        mh2 = np.ones(int(np.prod(nb)), bool)                  # full coverage -> must succeed
        M = P.build_projection_M(edges, 4, mh2, ml)
        self.assertTrue(M.any(axis=1).all())


class IntegrationCLI(unittest.TestCase):
    """Invoke the REAL fail-closed CLI entrypoints (pre-ROOT guards) and assert
    nonzero exit + no product written. Runnable without PyROOT (lazy ROOT import)."""
    import os as _os
    ND = str(Path(__file__).resolve().parents[1])

    def _run(self, script, args):
        import subprocess
        r = subprocess.run([sys.executable, f"{self.ND}/{script}", *args],
                           cwd=self.ND, capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr)

    def test_build_components_rejects_adopted_out_path(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "uq_universe_5d_covariance_combined_uthrow.root")
            rc, _ = self._run("p4_build_components.py",
                              ["--manifest", "/dev/null", "--support-family",
                               "uq_5d/universe_stage2_5d_bkgaware/x.root",
                               "--out", out, "--out-manifest", os.path.join(td, "m.json")])
            self.assertNotEqual(rc, 0)
            self.assertFalse(os.path.exists(out))

    def test_build_components_rejects_superseded_support_family(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "cand.root")
            rc, _ = self._run("p4_build_components.py",
                              ["--manifest", "/dev/null", "--support-family",
                               "uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined.root",
                               "--out", out, "--out-manifest", os.path.join(td, "m.json")])
            self.assertNotEqual(rc, 0)
            self.assertFalse(os.path.exists(out))

    def test_build_components_requires_bkgaware_family(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "cand.root")
            rc, _ = self._run("p4_build_components.py",
                              ["--manifest", "/dev/null", "--support-family",
                               "some/other/combined.root",
                               "--out", out, "--out-manifest", os.path.join(td, "m.json")])
            self.assertNotEqual(rc, 0)
            self.assertFalse(os.path.exists(out))

    def test_project_rejects_protected_out_path(self):
        """REPAIR-4 (verifier defect 6b). This test used to pass `--proj`, an argument the
        projector does not define, so argparse exited nonzero BEFORE the path guard ran and
        `assertNotEqual(rc, 0)` passed for the wrong reason. It asserted nothing about the
        guard it was named for. Now: only real arguments, and the assertion is on the SPECIFIC
        gate reached, not merely a nonzero return."""
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = "uq_4d/corrected/proj_candidate.root"
            rc, err = self._run("p4_project_4d.py",
                                ["--c5", os.path.join(td, "c5.root:k"),
                                 "--manifest", "/dev/null", "--out", out])
            self.assertNotEqual(rc, 0)
            self.assertNotIn("unrecognized arguments", err)   # would mean we never reached the guard
            self.assertIn("candidate must resolve inside", err)  # the guard we are actually testing
            self.assertFalse(os.path.exists(f"{self.ND}/{out}"))


class Round3Gates(unittest.TestCase):
    def test_candidate_path_guard(self):
        P.require_candidate_path("nd-unfolding/active_universe_5d/standard/candidate/std5d.root")
        for bad in ("active_universe_5d/standard/candidate/std_uthrow.root",  # adopted token
                    "active_universe_5d/standard/candidate/uq_universe_5d_covariance_combined.root",
                    "uq_4d/corrected/x.root",                                  # protected
                    "active_universe_5d/standard/merged/x.root"):              # not candidate subdir
            with self.assertRaises(P4GateError):
                P.require_candidate_path(bad)

    def test_config_axes_estimator_enforced(self):
        with self.assertRaises(P4GateError):
            P.P4Config(axes="eavail,q3").validate()
        with self.assertRaises(P4GateError):
            P.P4Config(estimator="nn").validate()

    def test_prove_identity(self):
        A = np.eye(3); self.assertLessEqual(P.prove_identity(A, A.copy(), 1e-12, "x"), 1e-12)
        with self.assertRaises(P4GateError):
            P.prove_identity(A, A * 1.1, 1e-9, "x")

    def test_edges_bin_volume_hash_deterministic_and_sensitive(self):
        e1 = [np.array([0., 1.]), np.array([0., 1.]), np.array([0., 1.]),
              np.array([0., 1.]), np.array([0., 1., 3.])]
        h1 = P.edges_bin_volume_hash(e1); h2 = P.edges_bin_volume_hash([a.copy() for a in e1])
        self.assertEqual(h1, h2)
        e2 = e1[:4] + [np.array([0., 1., 2.])]                 # different W edges/widths
        self.assertNotEqual(P.edges_bin_volume_hash(e2)["bin_volume_hash"], h1["bin_volume_hash"])

    def test_deterministic_projection_M_width_weighted(self):
        edges = [np.array([0., 1.])] * 4 + [np.array([0., 1., 3.])]   # 2 W bins, widths 1,2
        mh = np.array([True, True]); ml = np.array([True])
        M = P.build_projection_M(edges, 4, mh, ml)
        np.testing.assert_allclose(M, np.array([[1.0, 2.0]]))         # width-weighted marginalization
        x = np.array([5.0, 7.0]); np.testing.assert_allclose(M @ x, np.array([5.0 * 1 + 7.0 * 2]))
        with self.assertRaises(P4GateError):                          # wrong high-mask size
            P.build_projection_M(edges, 4, np.array([True]), ml)

    def test_orchestrator_receipt_validation(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            paths = [f"m/{b}_{e}.root" for b in P.BANDS for e in P.ENDPOINTS]
            open(os.path.join(td, "COMPLETE"), "w").write("1")
            open(os.path.join(td, "summary.tsv"), "w").write("x\n")
            open(os.path.join(td, "validation.tsv"), "w").write("ok\n")
            open(os.path.join(td, "standard.sha256"), "w").write(
                "\n".join(f"{'a'*64}  {p}" for p in paths) + "\n")
            open(os.path.join(td, "standard.inventory.tsv"), "w").write(
                "\n".join(f"100\t1700000000\t{p}" for p in paths) + "\n")
            live = {p: (100, 1700000000) for p in paths}
            rec = P.validate_orchestrator_merged_receipt(td, live)
            self.assertEqual(rec["n"], 10); self.assertEqual(len(rec["hash_list_digest"]), 64)
            with self.assertRaises(P4GateError):                      # size/mtime drift
                P.validate_orchestrator_merged_receipt(td, {p: (101, 1700000000) for p in paths})
            os.remove(os.path.join(td, "COMPLETE"))
            with self.assertRaises(P4GateError):                      # missing COMPLETE
                P.validate_orchestrator_merged_receipt(td, live)


class IntegrationCLI2(unittest.TestCase):
    ND = str(Path(__file__).resolve().parents[1])
    def _run(self, script, args):
        import subprocess
        r = subprocess.run([sys.executable, f"{self.ND}/{script}", *args],
                           cwd=self.ND, capture_output=True, text=True)
        return r.returncode

    def test_project_rejects_cli_tolerance_override(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            out = "active_universe_5d/standard/candidate/proj.root"
            rc = self._run("p4_project_4d.py", ["--c5", os.path.join(td, "c.root:k"),
                           "--manifest", "/dev/null", "--out", out, "--central-rel", "0.9"])
            self.assertNotEqual(rc, 0)

    def test_adopt_requires_explicit_flag(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            for n in ("cand.root", "prov.json", "val.json"):
                open(os.path.join(td, n), "w").write("{}" if n.endswith("json") else "x")
            rc = self._run("p4_adopt_standard.py", ["--candidate", os.path.join(td, "cand.root"),
                           "--component-manifest", os.path.join(td, "prov.json"),
                           "--validation", os.path.join(td, "val.json"),
                           "--out", os.path.join(td, "adopted.root")])
            self.assertNotEqual(rc, 0)


class StandardFooting(unittest.TestCase):
    """G-1 (2026-08-07): the standard lane must RECORD its background footing rather than
    inherit the driver default, and must fail closed when the footing is absent or wrong.

    Fixtures here are the real producer's literal output, never hand-assembled to match what
    the consumer expects -- that inversion is precisely BEN-040, in this same chain."""

    FIXTURE = (Path(__file__).resolve().parent / "fixtures"
               / "p4_std_unfold_purity_BeamAngleX_0.log")
    DRIVER = Path(__file__).resolve().parents[1] / "unfold_nd_omnifold_unbinned.py"

    # ---------- the declared footing ----------
    def test_config_carries_and_hashes_bkg_mode(self):
        c = P.P4Config()
        self.assertEqual(c.bkg_mode, "purity")            # the 2026-08-07 decision
        self.assertIn("bkg_mode", c.as_dict())
        # the footing participates in the config hash, so it cannot drift unnoticed
        self.assertNotEqual(c.hash(), P.P4Config(bkg_mode="negweight-refined").hash())

    def test_config_rejects_unknown_and_unauthorized_bkg_mode(self):
        with self.assertRaises(P4GateError):
            P.P4Config(bkg_mode="nonsense").validate()     # not a driver choice at all
        with self.assertRaises(P4GateError):
            P.P4Config(bkg_mode="negweight-refined").validate()   # known, but not the decision

    def test_footing_block_is_nested_producer_shape(self):
        f = P.P4Config().footing()
        for k in P.STANDARD_FOOTING_KEYS:
            self.assertIn(k, f)
        self.assertEqual(f["estimator"], "lgbm")
        self.assertEqual(f["seed"], 42)
        self.assertEqual(f["iters"], 5)
        self.assertIs(f["use_weights"], True)
        self.assertIs(f["full_phase_space"], False)        # standard, not FPS

    # ---------- the fail-closed gate: positive, absent, mismatched ----------
    def test_gate_accepts_purity(self):                    # POSITIVE: it can actually pass
        self.assertTrue(P.require_standard_footing({"footing": P.P4Config().footing()}))

    def test_gate_rejects_absent_footing(self):
        with self.assertRaises(P4GateError):
            P.require_standard_footing({})                 # no field at all == unprovable
        with self.assertRaises(P4GateError):
            P.require_standard_footing({"footing": {}})

    def test_gate_rejects_missing_bkg_mode_and_mismatch(self):
        f = P.P4Config().footing(); f.pop("bkg_mode")
        with self.assertRaises(P4GateError):
            P.require_standard_footing({"footing": f})     # unprovable
        bad = P.P4Config().footing(); bad["bkg_mode"] = "negweight-refined"
        with self.assertRaises(P4GateError):
            P.require_standard_footing({"footing": bad})   # mismatched
        wrong = P.P4Config().footing(); wrong["estimator"] = "nn"
        with self.assertRaises(P4GateError):
            P.require_standard_footing({"footing": wrong})

    def test_gate_rejects_flattened_footing(self):
        """A manifest with the five keys at TOP level and no nested block must fail, not
        silently read None on every key. This is the BEN-040 shape, inverted into a guard."""
        flat = dict(P.STANDARD_REQUIRED_FOOTING); flat["bkg_mode"] = "purity"
        with self.assertRaises(P4GateError):
            P.require_standard_footing(flat)

    # ---------- log classification, against real producer output ----------
    def test_real_purity_log_is_positively_identified(self):
        text = self.FIXTURE.read_text(errors="replace")
        mode, why = P.classify_log_bkg_mode(text)
        self.assertEqual(mode, "purity", why)
        self.assertNotIn("[INFO] bkg-mode=", text)         # the silent branch, as claimed

    def test_negweight_announcement_is_read_from_the_log(self):
        base = self.FIXTURE.read_text(errors="replace")
        for m in ("negweight", "negweight-refined"):
            text = base + (f"[INFO] bkg-mode={m}: data side 4091707 events "
                           f"(of 4119797) in the analysis window at +1.\n")
            mode, why = P.classify_log_bkg_mode(text)
            self.assertEqual(mode, m, why)                 # announcement beats the signature

    def test_indeterminate_log_is_unprovable_not_assumed_purity(self):
        mode, why = P.classify_log_bkg_mode("[INFO] axes (5D): pt, pz\nStarting iteration 0\n")
        self.assertIsNone(mode)                            # no signature => cannot conclude
        self.assertIn("unprovable", why)

    def test_conflicting_and_unrecognized_announcements_fail(self):
        two = ("[INFO] bkg-mode=negweight: x\n"
               "[INFO] bkg-mode=negweight-refined: y\n")
        self.assertIsNone(P.classify_log_bkg_mode(two)[0])
        self.assertIsNone(P.classify_log_bkg_mode("[INFO] bkg-mode=banana: z\n")[0])

    # ---------- contract: the classifier must track the real producer ----------
    def test_classifier_markers_still_exist_in_the_driver(self):
        """If the driver's print statements change, this classifier's inference from silence
        becomes wrong. Pin both markers to the producer's source so drift fails a test
        rather than silently mislabelling a footing."""
        src = self.DRIVER.read_text(errors="replace")
        self.assertIn('f"[INFO] bkg-mode={args.bkg_mode}', src)
        self.assertIn('[INFO] measured training:', src)
        self.assertIn('default="purity"', src)             # the default the launcher overrides
        self.assertIn('elif args.bkg_mode == "purity":', src)   # the branch that stays silent

    def test_launcher_passes_bkg_mode_explicitly(self):
        sh = (Path(__file__).resolve().parents[1] / "run_p4_unfold_std.sh").read_text()
        self.assertIn("--bkg-mode", sh)                    # no reliance on the driver default
        self.assertIn('"${BKG_MODE}"', sh)                 # and it comes from P4Config
        self.assertIn('"bkg_mode":"%s"', sh)               # stamped into the receipts


class Repair4DriverContract(unittest.TestCase):
    """REPAIR-4, verifier defect 1. Stages 4-6 had NEVER executed, so nothing caught that the
    driver called the validator and projector with arguments they do not define and a ROOT key
    nothing writes. These tests derive the expectation from the REAL callees -- each script's
    own argparse and the builder's own key constants -- so they fail if either side drifts.
    That is the point: the previous suite asserted only `rc != 0` and was satisfied by an
    argparse error (defect 6b)."""

    ND = Path(__file__).resolve().parents[1]

    def _driver(self):
        return (self.ND / "run_p4_standard.sh").read_text()

    def _argparse_opts(self, script):
        """The set of long options a script actually defines, read from its source."""
        import re
        src = (self.ND / script).read_text()
        return set(re.findall(r'add_argument\("(--[a-z0-9-]+)"', src))

    def _driver_opts_for(self, script):
        """The long options the driver passes to `script`, read from the driver."""
        import re
        drv = self._driver()
        m = re.search(rf"python3 {re.escape(script)}((?:[^\n]*\\\n)*[^\n]*)", drv)
        self.assertIsNotNone(m, f"driver does not invoke {script}")
        return set(re.findall(r"(--[a-z0-9-]+)", m.group(1)))

    # ---------- D1b/D1c: the driver must speak each callee's real CLI ----------
    def test_driver_passes_only_options_the_validator_defines(self):
        passed = self._driver_opts_for("p4_validate_active_lateral.py")
        defined = self._argparse_opts("p4_validate_active_lateral.py")
        self.assertTrue(passed, "no options parsed from the validator invocation")
        self.assertEqual(passed - defined, set(),
                         f"driver passes options the validator does not define: {passed - defined}")

    def test_driver_supplies_every_required_validator_option(self):
        passed = self._driver_opts_for("p4_validate_active_lateral.py")
        for req in ("--candidate", "--support", "--manifest", "--merged-audit", "--out"):
            self.assertIn(req, passed, f"driver omits required validator option {req}")

    def test_driver_passes_only_options_the_projector_defines(self):
        passed = self._driver_opts_for("p4_project_4d.py")
        defined = self._argparse_opts("p4_project_4d.py")
        self.assertEqual(passed - defined, set(),
                         f"driver passes options the projector does not define: {passed - defined}")
        self.assertNotIn("--proj", passed)        # the exact retired argument from defect 1

    def test_driver_passes_only_options_the_builder_defines(self):
        passed = self._driver_opts_for("p4_build_components.py")
        defined = self._argparse_opts("p4_build_components.py")
        self.assertEqual(passed - defined, set(),
                         f"driver passes options the builder does not define: {passed - defined}")

    # ---------- D1c: the key must be one the builder actually writes ----------
    DEAD_KEY = "hCov_std" + "_final5_candidate"      # split so this file is not its own hit

    @staticmethod
    def _code_lines(text):
        """Lines that are not wholly a `#` comment. Keeps history in comments testable-around:
        documenting the dead key is good, *referencing* it is the defect."""
        return [l for l in text.splitlines() if not l.lstrip().startswith("#")]

    def test_candidate_key_is_produced_by_the_builder(self):
        builder = (self.ND / "p4_build_components.py").read_text()
        self.assertIn("P.CANDIDATE_TOTAL_KEY", builder)      # builder writes the shared constant
        self.assertIn("CANDIDATE_TOTAL_KEY", self._driver()) # driver reads the same one
        self.assertNotIn(self.DEAD_KEY, "\n".join(self._code_lines(self._driver())))

    def test_dead_candidate_key_appears_in_no_executable_line(self):
        import subprocess
        r = subprocess.run(["git", "grep", "-l", self.DEAD_KEY],
                           cwd=self.ND.parent, capture_output=True, text=True)
        offenders = []
        for rel in r.stdout.splitlines():
            if not rel.strip() or rel.endswith(".md") or "runs/" in rel or "tests/" in rel:
                continue
            body = (self.ND.parent / rel).read_text(errors="replace")
            if self.DEAD_KEY in "\n".join(self._code_lines(body)):
                offenders.append(rel)
        self.assertEqual(offenders, [],
                         f"dead candidate key referenced in executable code: {offenders}")

    def test_candidate_keys_are_single_sourced(self):
        self.assertEqual(P.CANDIDATE_TOTAL_KEY, "hCov_stdcombined5d_total_candidate")
        self.assertEqual(P.CANDIDATE_SYST_KEY, "hCov_stdsyst5d_total_candidate")
        self.assertEqual(P.candidate_band_key("BeamAngleX"), "hCov_active5d_BeamAngleX")
        with self.assertRaises(P4GateError):
            P.candidate_band_key("NotABand")

    # ---------- D1a: stage order ----------
    def test_stage_order_is_audit_then_unfold_then_evidence(self):
        drv = self._driver()
        i_audit = drv.index("run bash run_p4_merge_audit_std.sh")
        i_unfold = drv.index("run bash run_p4_unfold_std.sh")
        i_evid = drv.index("python3 p4_evidence.py")
        self.assertLess(i_audit, i_unfold, "merge+audit must precede unfold")
        self.assertLess(i_unfold, i_evid,
                        "endpoint evidence must come AFTER unfold, or the manifest describes "
                        "endpoints the next stage can rewrite")

    def test_default_stop_after_is_the_safe_preflight(self):
        drv = self._driver()
        self.assertIn('STOP_AFTER="${STOP_AFTER:-audit}"', drv)
        self.assertIn("unknown STOP_AFTER", drv)          # invalid values abort, not fall through

    def test_covariance_stages_are_still_gated(self):
        """Compare EXECUTABLE positions, not the header comment -- both strings appear in the
        stage-list comment at the top, so a naive index() compares documentation."""
        code = "\n".join(self._code_lines(self._driver()))
        self.assertIn("P4_VERIFIER_PASS", code)
        self.assertLess(code.index("P4_VERIFIER_PASS"),
                        code.index("python3 p4_build_components.py"),
                        "the verifier gate must precede component construction")


class Repair4EvidenceBindings(unittest.TestCase):
    """REPAIR-4, verifier defect 3 (the two parts that are pure logic and testable ROOT-free)."""

    ND = Path(__file__).resolve().parents[1]

    def test_config_hash_covers_the_reported_grid(self):
        """D3a: the grid field used to be added to man["config"] AFTER config_hash was
        computed, so the recorded hash did not cover the recorded configuration."""
        c = P.P4Config()
        self.assertIn("full_phase_space_reported_grid", c.as_dict())
        self.assertEqual(c.as_dict()["full_phase_space_reported_grid"], P.GRID_NBINS)
        # and it is inside the hash, not bolted on beside it
        import hashlib, json
        expect = hashlib.sha256(json.dumps(c.as_dict(), sort_keys=True).encode()).hexdigest()
        self.assertEqual(c.hash(), expect)

    def test_evidence_no_longer_mutates_config_after_hashing(self):
        src = (self.ND / "p4_evidence.py").read_text()
        code = [l for l in src.splitlines() if not l.lstrip().startswith("#")]
        joined = "\n".join(code)
        self.assertNotIn('man["config"]["full_phase_space_reported_grid"]', joined)

    # ---- OI-43 / the cluster-P4 hold release condition ---------------------------------------
    # Joseph's hold on the cluster P4 lane names p4_evidence.py's hardcoded root as its release
    # condition, and asks for "a test that fails against the old form". These three are that test.
    # POWER-TESTED, both directions, by reconstructing the old form in a temp copy: see
    # test_derooting_test_actually_fails_against_the_old_form below, which is the negative control.

    @staticmethod
    def _executable_source(path):
        """Source with comment lines removed. Required, not cosmetic: the de-rooting commit
        deliberately QUOTES the old hardcoded path in a comment so the next reader knows what
        changed, and a raw substring check would fire on that comment forever."""
        return "\n".join(l for l in path.read_text().splitlines()
                         if not l.lstrip().startswith("#"))

    def test_evidence_has_no_hardcoded_absolute_root(self):
        code = self._executable_source(self.ND / "p4_evidence.py")
        self.assertNotIn("/pscratch/sd/j/josephrb", code)
        self.assertNotIn('REPO = "/', code)

    def test_evidence_root_is_the_same_anchor_p4_lib_guards_against(self):
        """The defect this closes is DISAGREEMENT, not merely a literal. Every containment guard
        in p4_lib checks against p4_lib.REPO_ROOT; p4_evidence carried its own independent root,
        so the two could differ and no guard could see it."""
        code = self._executable_source(self.ND / "p4_evidence.py")
        self.assertIn("P.REPO_ROOT", code)
        # behavioural, not textual: the resolver must actually land on THIS checkout
        self.assertTrue((Path(P.REPO_ROOT) / "nd-unfolding" / "p4_evidence.py").is_file())
        self.assertEqual(Path(P.REPO_ROOT).resolve(), self.ND.parent.resolve())
        self.assertEqual(Path(P.ND_ROOT).resolve(), self.ND.resolve())

    def test_evidence_does_not_create_directories_at_import_time(self):
        """The module docstring claims "Read-only: opens nothing for write", and an import-time
        os.makedirs falsified it. That side effect is also why this suite reads the file as text
        instead of importing it, so it is load-bearing for the integration matrix (defect 6)."""
        src = (self.ND / "p4_evidence.py").read_text()
        head = src.split("_PRODUCTS = (")[0]
        head_code = "\n".join(l for l in head.splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn("os.makedirs", head_code)
        # and it still happens before the writes, or the stage breaks on a fresh checkout
        tail_code = "\n".join(l for l in src.split("_PRODUCTS = (")[1].splitlines()
                              if not l.lstrip().startswith("#"))
        self.assertIn("os.makedirs(EVID", tail_code)
        self.assertLess(tail_code.index("os.makedirs(EVID"), tail_code.index(".PENDING"))

    def test_derooting_test_actually_fails_against_the_old_form(self):
        """NEGATIVE CONTROL for the three tests above. A de-rooting test that was never run
        against the rooted form is an assertion nobody has seen fail -- BEN-119. This rebuilds
        the pre-fix source in a temp file and asserts each check flips."""
        import tempfile
        real = (self.ND / "p4_evidence.py").read_text()
        old = real.replace(
            "REPO = P.REPO_ROOT; ND = P.ND_ROOT",
            'REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND = f"{REPO}/nd-unfolding"')
        self.assertNotEqual(old, real, "anchor line not found -- this control has gone stale")
        old = old.replace('EVID = f"{ND}/active_universe_5d/standard/evidence"',
                          'EVID = f"{ND}/active_universe_5d/standard/evidence"; '
                          'os.makedirs(EVID, exist_ok=True)', 1)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "p4_evidence.py"
            p.write_text(old)
            code = self._executable_source(p)
            # 1. the literal is back
            self.assertIn("/pscratch/sd/j/josephrb", code)
            # 2. the shared anchor is gone
            self.assertNotIn("P.REPO_ROOT", code)
            # 3. the import-time side effect is back
            head = old.split("_PRODUCTS = (")[0]
            head_code = "\n".join(l for l in head.splitlines()
                                  if not l.lstrip().startswith("#"))
            self.assertIn("os.makedirs", head_code)

    # ---- OI-43 increment 2: the three shell drivers ------------------------------------------
    # De-rooting p4_evidence.py alone was NOT sufficient. run_p4_standard.sh `cd`s into its own
    # hardcoded ND before invoking it, so the chain stayed pinned to one checkout through the
    # CALLER. Fixing the callee and not the caller is BEN-162/163's shape, which is the class I had
    # just cited in the increment-1 commit -- so these tests cover all three drivers, not the one
    # that OI-43 names.
    #
    # These are EXECUTION tests, not source-text tests: they run `bash <driver>` in a fake checkout
    # and assert the specific documented exit code. That is what defect 6 of the repair brief asks
    # for ("Assert the specific intended failure, not a generic argparse nonzero"), and it is the
    # axis the 111-test baseline did not cover at all.

    P4_DRIVERS = ("run_p4_standard.sh", "run_p4_merge_audit_std.sh", "run_p4_unfold_std.sh")

    def test_drivers_have_no_hardcoded_absolute_root(self):
        for name in self.P4_DRIVERS:
            code = self._executable_source(self.ND / name)
            with self.subTest(driver=name):
                self.assertNotIn("/pscratch/sd/j/josephrb", code)
                self.assertIn("BASH_SOURCE", code)

    def test_drivers_refuse_an_unresolved_root_with_exit_3(self):
        """BEHAVIOURAL. Copy each driver into a tree with no p4_lib.py beside it and run it. It
        must abort with exit 3 before doing anything -- not 0, and not a generic 1."""
        import subprocess, tempfile
        for name in self.P4_DRIVERS:
            with self.subTest(driver=name), tempfile.TemporaryDirectory() as d:
                nd = Path(d) / "nd-unfolding"
                nd.mkdir()
                dst = nd / name
                dst.write_text((self.ND / name).read_text())
                r = subprocess.run(["bash", str(dst)], capture_output=True, text=True, timeout=60)
                self.assertEqual(r.returncode, 3,
                                 f"{name}: expected exit 3, got {r.returncode}\n"
                                 f"stdout={r.stdout[-400:]}\nstderr={r.stderr[-400:]}")
                self.assertIn("no p4_lib.py", r.stdout + r.stderr)

    def test_driver_root_derivation_lands_on_its_own_checkout(self):
        """BEHAVIOURAL, positive side. Runs only the derivation header (everything up to and
        including the guard) plus an echo, in a fake checkout. Truncating is deliberate and is
        stated: the happy path of the real driver would launch the chain, which this suite must
        never do. What is under test is the derivation, and it is executed, not read."""
        import subprocess, tempfile
        for name in self.P4_DRIVERS:
            src = (self.ND / name).read_text().splitlines()
            end = [i for i, l in enumerate(src) if "no p4_lib.py" in l]
            self.assertEqual(len(end), 1, f"{name}: expected exactly one guard line")
            header = "\n".join(src[:end[0] + 1])
            with self.subTest(driver=name), tempfile.TemporaryDirectory() as d:
                nd = Path(d) / "nd-unfolding"
                nd.mkdir()
                (nd / "p4_lib.py").write_text("# stub\n")
                probe = nd / name
                probe.write_text(header + '\necho "ND=${ND}"\necho "REPO=${REPO}"\nexit 0\n')
                r = subprocess.run(["bash", str(probe)], capture_output=True, text=True, timeout=60)
                self.assertEqual(r.returncode, 0, f"{name}: {r.stdout}\n{r.stderr}")
                # resolve() BOTH sides, never compare the raw strings: on macOS the temp dir is
                # /var/... while bash's `cd && pwd` reports /private/var/..., because /var is a
                # symlink. A raw compare fails on macOS and passes on the cluster, which is the
                # worst available outcome for a test whose whole subject is path resolution.
                self.assertEqual(
                    Path([l[3:] for l in r.stdout.splitlines()
                          if l.startswith("ND=")][0]).resolve(), nd.resolve())
                self.assertEqual(
                    Path([l[5:] for l in r.stdout.splitlines()
                          if l.startswith("REPO=")][0]).resolve(), Path(d).resolve())

    def test_zero_sel_is_actually_enforced(self):
        """D3d: ZERO_SEL was declared and referenced by no check -- the bin-migration-only
        claim for the three muon bands was documentation, not a gate."""
        src = (self.ND / "p4_evidence.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("ZERO_SEL", code)
        self.assertIn("elif b in ZERO_SEL", code)
        self.assertIn("selmig == 0", code)

    def test_endpoint_index_is_asserted(self):
        src = (self.ND / "p4_evidence.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("idx_meta", code)
        self.assertIn("endpoint INDEX mismatch", code)

    def test_source_blobs_come_from_the_commit_not_the_working_tree(self):
        """D3b: `git hash-object <path>` records whatever is checked out, which is how an
        unrelated dirty blob was absorbed in 2026-07 and how re-running evidence in 2026-08
        re-attributed 07-18 endpoints to newer code (KNOWN_ISSUES #23)."""
        src = (self.ND / "p4_evidence.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn('"rev-parse", f"HEAD:{rel}"', code)      # committed object
        self.assertIn("_committed_blob", code)
        self.assertIn("is DIRTY", code)                        # dirty source fails closed
        # the old working-tree call must not be what populates source_blobs
        self.assertNotIn('man["source_blobs"] = {k: _blob(', code)

    def test_source_commit_is_the_one_that_introduced_the_blob(self):
        """D3c: the old code recorded the last commit to TOUCH the path, which need not be the
        commit that introduced the blob recorded beside it."""
        src = (self.ND / "p4_evidence.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("_blob_introducing_commit", code)
        self.assertNotIn('"log", "-1", "--format=%H", "--", rel', code)

    def test_binary_hash_is_labelled_as_present_not_producing(self):
        """#23: the binary is hashed as it is on disk now, which need not be what produced the
        merged inputs. The manifest must not let a reader confuse the two."""
        src = (self.ND / "p4_evidence.py").read_text()
        self.assertIn("binary_sha256_semantics", src)
        self.assertIn("NOT proof that this binary produced", src)

    def test_the_two_band_sets_partition_the_five_bands(self):
        """repair-5: the sets are single-sourced in p4_lib now (they were duplicated in
        p4_evidence.py and the validator, one edit away from disagreeing)."""
        nz, zs = P.NONZERO_MIGRATION_BANDS, P.ZERO_MIGRATION_BANDS
        self.assertEqual(set(nz) | set(zs), set(P.BANDS),
                         "the two sets must cover exactly the five bands")
        self.assertEqual(set(nz) & set(zs), set(), "a band cannot be in both sets")

    def test_consumers_use_the_single_source(self):
        for f in ("p4_evidence.py", "p4_validate_active_lateral.py"):
            src = (self.ND / f).read_text()
            self.assertIn("P.NONZERO_MIGRATION_BANDS", src, f)
            self.assertIn("P.ZERO_MIGRATION_BANDS", src, f)


class Repair4CandidateProvenance(unittest.TestCase):
    """REPAIR-4, verifier defect 4 (the parts that are testable without ROOT)."""

    ND = Path(__file__).resolve().parents[1]

    def test_candidate_guard_rejects_traversal_out_of_the_candidate_dir(self):
        """D4e: the guard was a bare substring test, so a path merely CONTAINING the candidate
        directory passed -- including one that climbs back out of it."""
        good = "nd-unfolding/active_universe_5d/standard/candidate/std5d.root"
        self.assertTrue(P.require_candidate_path(good))
        escapes = [
            "active_universe_5d/standard/candidate/../../../products/5d/xsec_5d.root",
            "active_universe_5d/standard/candidate/../../fps/x.root",
            "a/active_universe_5d/standard/candidate/../evil.root",
        ]
        for bad in escapes:
            with self.assertRaises(P4GateError, msg=f"traversal accepted: {bad}"):
                P.require_candidate_path(bad)

    def test_candidate_guard_rejects_lookalike_directory_names(self):
        """Structural containment, not textual: a directory merely NAMED like the candidate
        path fragment must not satisfy it."""
        with self.assertRaises(P4GateError):
            P.require_candidate_path("nd-unfolding/active_universe_5d_standard_candidate/x.root")
        with self.assertRaises(P4GateError):
            P.require_candidate_path("some/other/place/x.root")

    def test_candidate_guard_still_rejects_adopted_tokens(self):
        for bad in ("active_universe_5d/standard/candidate/std_uthrow.root",
                    "active_universe_5d/standard/candidate/uq_universe_5d_covariance_combined.root"):
            with self.assertRaises(P4GateError):
                P.require_candidate_path(bad)

    def test_builder_writes_candidate_before_manifest_and_binds_it(self):
        """D4b: the manifest was written BEFORE the candidate ROOT existed and carried no
        candidate hash, so it could describe a candidate that was never completed."""
        src = (self.ND / "p4_build_components.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        i_root = code.index('ROOT.TFile.Open(a.out, "RECREATE")')
        i_man = code.index("os.replace(tmp_manifest, a.out_manifest)")
        self.assertLess(i_root, i_man, "candidate ROOT must be published before the manifest")
        self.assertIn('prov["candidate_sha256"]', code)
        self.assertIn('prov["candidate_keys"]', code)
        # and the manifest publication is atomic
        self.assertIn("tmp_manifest", code)

    def test_validator_checks_the_audit_it_loads(self):
        """D3e: the merged-audit JSON was loaded and used only for its ten SHA values; every
        census, completeness and migration field it exists to carry was ignored."""
        src = (self.ND / "p4_validate_active_lateral.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        for tok in ("band_meta", "idx_meta", "tree_entries", "selection_migration_abs",
                    "merged_audit_census_and_migration"):
            self.assertIn(tok, code, f"validator still ignores {tok}")

    def test_validator_binds_the_component_manifest(self):
        """D4f: candidate and component provenance were separable -- the validator never opened
        the manifest the builder wrote beside the candidate."""
        src = (self.ND / "p4_validate_active_lateral.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("std_component_manifest.json", code)
        self.assertIn("component manifest does not describe THIS candidate", code)
        self.assertIn("retired self-asserted `pure_addition` flag", code)
        self.assertIn("component_manifest_bound", code)

    def test_validator_proves_full_total_against_the_bound_stat_and_ml_blocks(self):
        """REPAIR-5 (D4b/D6). This test previously asserted the presence of a PSD-only check
        while being NAMED `..._recomputes_the_full_total_identity` -- a strong name over a weak
        check, the same pattern as the argparse false positive it sat beside. The gate is now a
        real comparison against the bound stat/ML blocks, and this asserts THAT."""
        src = (self.ND / "p4_validate_active_lateral.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn("combined_minus_syst_is_psd", code)      # the retired weak gate
        self.assertIn("full_total_identity_recomputed", code)
        self.assertIn("check_full_total_identity", code)
        self.assertIn("_bound_block", code)                        # stat/ML sha re-verified

    def test_validator_uses_the_shared_key_constants(self):
        src = (self.ND / "p4_validate_active_lateral.py").read_text()
        self.assertIn("P.CANDIDATE_TOTAL_KEY", src)
        self.assertIn("P.CANDIDATE_SYST_KEY", src)

    def test_builder_key_inventory_matches_what_it_writes(self):
        src = (self.ND / "p4_build_components.py").read_text()
        for tok in ("P.candidate_band_key(b)", "P.CANDIDATE_ACTIVE_TOTAL_KEY",
                    "P.CANDIDATE_SYST_KEY", "P.CANDIDATE_TOTAL_KEY"):
            self.assertIn(tok, src)


class Repair5SelfGuards(unittest.TestCase):
    """REPAIR-5. One assertion per defect that FAILS if the defect is reintroduced.

    Every check here is a live computation, not a source-text grep, except where the thing
    being guarded IS a source property. If any of these can be deleted and the four defects
    still stay fixed, the defect was not really closed."""

    ND = Path(__file__).resolve().parents[1]

    # ---------- D3: dirty-source guard must fail closed on a DELETED source ----------
    def test_deleted_bound_source_is_a_blocker_not_a_pass(self):
        """The old guard read `_w is None or _c == _w`; _worktree_blob returns None when the
        file is gone, so DELETING a bound source passed the dirty check."""
        src = (self.ND / "p4_evidence.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn("_w is None or _c == _w", code)   # the fail-OPEN disjunct is gone
        self.assertIn("need(_c == _w,", code)              # replaced by a direct comparison
        self.assertIn("ABSENT from the working tree", code)
        self.assertIn("os.path.exists(_abs)", code)
        self.assertIn("`git hash-object` failed", code)   # git-unavailable distinguished

    # ---------- D4a: containment must survive a symlink escape ----------
    def test_symlink_escape_is_rejected(self):
        """A symlink inside the candidate dir pointing out of it must not launder a path.
        normpath could not see this; realpath can."""
        import tempfile, os
        cand_root = os.path.join(P.ND_ROOT, P.CANDIDATE_SUBDIR)
        os.makedirs(cand_root, exist_ok=True)
        with tempfile.TemporaryDirectory() as outside:
            link = os.path.join(cand_root, "_p5_escape_probe")
            if os.path.islink(link) or os.path.exists(link):
                os.remove(link)
            os.symlink(outside, link)
            try:
                with self.assertRaises(P4GateError):
                    P.require_candidate_path(os.path.join(link, "out.root"))
            finally:
                os.remove(link)

    def test_absolute_path_outside_the_repo_is_rejected(self):
        """The verifier's exact bypass: the component sequence appearing anywhere."""
        with self.assertRaises(P4GateError):
            P.require_candidate_path("/evil/active_universe_5d/standard/candidate/out.root")
        with self.assertRaises(P4GateError):
            P.require_candidate_path("/tmp/active_universe_5d/standard/candidate/x.root")

    def test_legitimate_candidate_paths_still_accepted(self):
        """A guard that cannot PASS is as broken as one that cannot FAIL."""
        for good in ("active_universe_5d/standard/candidate/std_final5_candidate.root",
                     "nd-unfolding/active_universe_5d/standard/candidate/std5d.root"):
            self.assertTrue(P.require_candidate_path(good), good)

    # ---------- D4b: PSD is not the identity ----------
    def test_psd_residual_that_is_not_stat_plus_ml_fails(self):
        """THE self-guard for the overclaim. This residual is symmetric PSD -- so it passes the
        repair-4 check -- but it is NOT stat+ML, so the real identity must reject it."""
        Csyst = np.diag([4.0, 9.0])
        Cstat = np.diag([1.0, 1.0])
        Cml = np.diag([0.5, 0.5])
        Ccomb_good = Csyst + Cstat + Cml
        self.assertLessEqual(
            P.check_full_total_identity(Ccomb_good, Csyst, Cstat, Cml, 1e-9), 1e-9)
        # residual = diag(3,3): symmetric, PSD, and wrong
        Ccomb_bad = Csyst + np.diag([3.0, 3.0])
        P.check_symmetric_psd(Ccomb_bad - Csyst)          # the weak check still passes...
        with self.assertRaises(P4GateError):              # ...the real identity does not
            P.check_full_total_identity(Ccomb_bad, Csyst, Cstat, Cml, 1e-9)

    def test_full_total_identity_catches_a_swapped_stat_block(self):
        Csyst = np.diag([4.0, 9.0]); Cstat = np.diag([1.0, 2.0]); Cml = np.diag([0.5, 0.5])
        Ccomb = Csyst + Cstat + Cml
        with self.assertRaises(P4GateError):
            P.check_full_total_identity(Ccomb, Csyst, np.diag([2.0, 1.0]), Cml, 1e-9)

    # ---------- pattern 1: declared-but-uncompared ----------
    def test_declared_migration_policy_is_compared_to_the_census(self):
        """`check_merged_metadata` required migration_policy to be truthy and compared it to
        nothing -- a declared policy no consumer checked."""
        nz, zs = {"BeamAngleX"}, {"MuonResolution"}
        self.assertTrue(P.check_declared_migration_policy(
            "active-universe selection-complete", 4792, "BeamAngleX", nz, zs))
        self.assertTrue(P.check_declared_migration_policy(
            "bin-migration only", 0, "MuonResolution", nz, zs))
        with self.assertRaises(P4GateError):      # claims migration, census says none
            P.check_declared_migration_policy(
                "active-universe selection-complete", 0, "BeamAngleX", nz, zs)
        with self.assertRaises(P4GateError):      # declared bin-only but migrated
            P.check_declared_migration_policy("bin-migration only", 17, "MuonResolution", nz, zs)
        with self.assertRaises(P4GateError):      # migrates but policy does not claim it
            P.check_declared_migration_policy("weights only", 4792, "BeamAngleX", nz, zs)
        with self.assertRaises(P4GateError):      # empty policy
            P.check_declared_migration_policy("", 0, "MuonResolution", nz, zs)

    def test_identities_are_measured_not_asserted(self):
        """The builder wrote four identity flags as literal `True`, and two consumers read them
        as evidence. They are now measured errors, and the retired flag is rejected."""
        b = (self.ND / "p4_build_components.py").read_text()
        self.assertNotIn('"pure_addition": True', b)
        self.assertIn("_relerr", b)
        self.assertIn("must RECOMPUTE", b)
        v = (self.ND / "p4_validate_active_lateral.py").read_text()
        self.assertIn("retired self-asserted `pure_addition` flag", v)


class Repair4ProjectionGeometry(unittest.TestCase):
    """REPAIR-4, verifier defect 5: the projector bound only some of its geometry."""

    ND = Path(__file__).resolve().parents[1]

    def test_4d_mask_hash_distinguishes_a_permutation(self):
        """D5c: the projector compared the reported COUNT only. A count is not an ordering."""
        a = np.array([True, True, False, True, False])
        b = np.array([True, False, True, True, False])       # same population, different bins
        self.assertEqual(int(a.sum()), int(b.sum()))
        self.assertNotEqual(P.cmask_order_hash_4d(a), P.cmask_order_hash_4d(b))
        self.assertEqual(P.cmask_order_hash_4d(a), P.cmask_order_hash_4d(a.copy()))
        with self.assertRaises(P4GateError):
            P.cmask_order_hash_4d(np.zeros(5, dtype=bool))    # empty mask fails closed

    def test_4d_mask_hash_matches_the_evidence_generator_construction(self):
        """Both sides must hash the same thing or the comparison is meaningless."""
        import hashlib
        x4 = np.array([0.0, 1.5, 0.0, 2.5, 3.5])
        m4 = x4 > 0
        idx = np.nonzero(x4 > 0)[0].astype(np.int64)          # p4_evidence.cmask_hash's form
        expect = hashlib.sha256(idx.tobytes() + b"|C").hexdigest()
        self.assertEqual(P.cmask_order_hash_4d(m4), expect)

    def test_matrix_content_hash_catches_a_changed_weight(self):
        """D5d: only M_shape was recorded, and two different projectors share a shape."""
        M1 = np.array([[1.0, 2.0], [0.0, 1.0]])
        M2 = np.array([[1.0, 2.0000001], [0.0, 1.0]])
        self.assertEqual(P.matrix_content_hash(M1), P.matrix_content_hash(M1.copy()))
        self.assertNotEqual(P.matrix_content_hash(M1), P.matrix_content_hash(M2))
        self.assertEqual(len(P.matrix_content_hash(M1)), 64)

    def test_matrix_content_hash_is_shape_sensitive(self):
        flat = np.arange(6, dtype=float)
        self.assertNotEqual(P.matrix_content_hash(flat.reshape(2, 3)),
                            P.matrix_content_hash(flat.reshape(3, 2)))

    def test_projector_requires_both_geometry_hashes(self):
        src = (self.ND / "p4_project_4d.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn('if "edge_hash" in man:', code)      # no longer optional
        self.assertIn('P.require("edge_hash" in man', code)
        self.assertIn('P.require("bin_volume_hash" in man', code)
        self.assertIn("bin-volume hash drift", code)
        self.assertIn("4D mask/order hash drift", code)

    def test_projection_receipt_records_m_contents_and_its_input(self):
        src = (self.ND / "p4_project_4d.py").read_text()
        self.assertIn("M_content_sha256", src)
        self.assertIn("candidate_c5_sha256", src)             # binds WHICH candidate was projected


class Repair4ReceiptSchema(unittest.TestCase):
    """REPAIR-4, verifier defect 2. The resume path accepted any ROOT plus any nonempty .done.

    The receipt fixture here is built by running the launcher's OWN `printf` format string,
    extracted from run_p4_unfold_std.sh at test time -- not hand-written to match the reader.
    If the producer's field list changes, this fixture changes with it, and a reader that
    drifted from the writer fails here. That inversion (fixture shaped like the consumer) is
    precisely BEN-040, in this same chain."""

    ND = Path(__file__).resolve().parents[1]

    # repair-6b: code_rev is checked for REACHABILITY in this history, so the fixture uses the
    # real HEAD. A synthetic sha is precisely what the gate now rejects.
    import subprocess as _sp
    _HEAD = _sp.check_output(["git", "rev-parse", "HEAD"],
                             cwd=str(Path(__file__).resolve().parents[2]), text=True).strip()
    GOOD = dict(tag="BeamAngleX_0", root_sha256="a" * 64, merged_sha256="b" * 64,
                central5d_sha256="c" * 64, config_hash="d" * 64, bkg_mode="purity",
                code_rev=_HEAD, unfold_blob="f" * 40)

    def _producer_receipt(self, mode="produced", **over):
        """Render a receipt through the launcher's real format string."""
        import re, subprocess, json
        sh = (self.ND / "run_p4_unfold_std.sh").read_text()
        m = re.search(r"printf '(\{\"tag\".*?\}\\n)'", sh, re.S)
        self.assertIsNotNone(m, "could not extract the launcher's receipt format")
        fmt = m.group(1)
        vals = dict(self.GOOD); vals.update(over)
        # positional order matches the launcher's own argument order. PB2 added two: the declared
        # receipt schema and the producing-closure blob map, the latter derived from the same
        # helper the launcher calls rather than restated here.
        surface = json.dumps(
            P.producing_closure_blobs(str(self.ND.parent), P.UNFOLD_DRIVER_REL)[1],
            sort_keys=True, separators=(",", ":"))
        args = [vals["tag"], str(P.RECEIPT_SCHEMA_CURRENT), vals["root_sha256"],
                vals["merged_sha256"], vals["central5d_sha256"], vals["config_hash"],
                vals["bkg_mode"], vals["code_rev"], vals["unfold_blob"], surface,
                "2026-08-07T00:00:00Z"]
        if mode == "legacy-attested":
            fmt = fmt.replace('"mode":"produced"', '"mode":"legacy-attested"')
        out = subprocess.run(["printf", fmt, *args], capture_output=True, text=True).stdout
        return json.loads(out)

    def test_producer_receipt_has_every_required_key(self):
        rec = self._producer_receipt()
        for k in P.RECEIPT_REQUIRED_KEYS:
            self.assertIn(k, rec, f"the real producer omits required key {k}")

    def test_validator_accepts_the_real_producer_output(self):
        rec = self._producer_receipt()
        self.assertTrue(P.validate_endpoint_receipt(rec, **self.GOOD))

    def test_legacy_attested_receipt_now_carries_merged_and_central(self):
        """D2b: the legacy receipt used to omit these, making an attested endpoint permanently
        less provable than a produced one."""
        rec = self._producer_receipt(mode="legacy-attested")
        self.assertEqual(rec["mode"], "legacy-attested")
        self.assertIn("merged_sha256", rec)
        self.assertIn("central5d_sha256", rec)
        self.assertTrue(P.validate_endpoint_receipt(rec, **self.GOOD))

    def test_incomplete_legacy_format_is_rejected(self):
        rec = self._producer_receipt()
        for drop in ("merged_sha256", "central5d_sha256", "bkg_mode", "config_hash", "tag"):
            bad = {k: v for k, v in rec.items() if k != drop}
            with self.assertRaises(P4GateError, msg=f"missing {drop} accepted"):
                P.validate_endpoint_receipt(bad, **self.GOOD)

    def test_every_identity_drift_is_rejected(self):
        rec = self._producer_receipt()
        for field, kw in (("root_sha256", "root_sha256"), ("merged_sha256", "merged_sha256"),
                          ("central5d_sha256", "central5d_sha256"), ("config_hash", "config_hash"),
                          ("bkg_mode", "bkg_mode")):
            drifted = dict(rec); drifted[field] = "z" * 64 if field != "bkg_mode" else "negweight"
            with self.assertRaises(P4GateError, msg=f"{field} drift accepted"):
                P.validate_endpoint_receipt(drifted, **self.GOOD)

    def test_receipt_root_pair_mismatch_is_rejected(self):
        rec = self._producer_receipt(tag="BeamAngleY_1")
        with self.assertRaises(P4GateError):
            P.validate_endpoint_receipt(rec, **self.GOOD)      # receipt belongs to another endpoint

    def test_unknown_mode_rejected(self):
        rec = self._producer_receipt(); rec["mode"] = "hand-written"
        with self.assertRaises(P4GateError):
            P.validate_endpoint_receipt(rec, **self.GOOD)

    # ---------- D2d: extras as well as missing ----------
    def test_exact_tag_set_rejects_missing_and_extra(self):
        full = [f"{b}_{e}" for b in P.BANDS for e in P.ENDPOINTS]
        self.assertTrue(P.require_exact_endpoint_tags(full))
        with self.assertRaises(P4GateError):
            P.require_exact_endpoint_tags(full[:-1])                    # missing
        with self.assertRaises(P4GateError):
            P.require_exact_endpoint_tags(full + ["BeamAngleX_2"])      # extra
        with self.assertRaises(P4GateError):
            P.require_exact_endpoint_tags(full + ["SomeOtherBand_0"])   # foreign product

    # ---------- D2a/D2c: the launcher wires them ----------
    def test_launcher_uses_the_receipt_gate_and_clears_stale_pairs(self):
        sh = (self.ND / "run_p4_unfold_std.sh").read_text()
        self.assertIn("p4_check_receipt.py", sh)         # skip is content-validating
        self.assertIn("STALE", sh)                       # and a reject re-runs
        self.assertIn('rm -f "${REC}"', sh)              # leaving no stale ROOT/receipt pair

    def test_launcher_propagates_receipt_write_failure(self):
        sh = (self.ND / "run_p4_unfold_std.sh").read_text()
        self.assertIn("receipt publication failed after ROOT publish", sh)
        self.assertIn("return 8", sh)

    def test_receipt_checker_rejects_absent_and_malformed(self):
        import subprocess, tempfile, os
        with tempfile.TemporaryDirectory() as td:
            missing = os.path.join(td, "nope.done")
            r = subprocess.run([sys.executable, str(self.ND / "p4_check_receipt.py"),
                                "--receipt", missing, "--tag", "BeamAngleX_0",
                                "--root", missing, "--merged", missing],
                               capture_output=True, text=True, cwd=str(self.ND))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("RECEIPT-REJECT", r.stdout + r.stderr)
            bad = os.path.join(td, "bad.done")
            open(bad, "w").write("not json")
            r2 = subprocess.run([sys.executable, str(self.ND / "p4_check_receipt.py"),
                                 "--receipt", bad, "--tag", "BeamAngleX_0",
                                 "--root", bad, "--merged", bad],
                                capture_output=True, text=True, cwd=str(self.ND))
            self.assertNotEqual(r2.returncode, 0)
            self.assertIn("RECEIPT-REJECT", r2.stdout + r2.stderr)


class NonAdoptableMarker(unittest.TestCase):
    """2026-08-09. The CANDIDATE is being produced WITHOUT a verifier PASS, deliberately, so it
    carries a self-declaring rejection. A marker whose only test is truthiness is worth nothing
    unless BOTH directions are demonstrated: that a marked manifest is refused, and that an
    unmarked one is not refused on that ground (otherwise a gate that always fires reads the
    same as a gate that works). Both are exercised against the real adopter CLI, not the
    library, because the adopter is what a future adoption step will actually invoke."""

    def _prov(self, marked):
        env = {"P4_NON_ADOPTABLE": "1"} if marked else {}
        prov = {"identities": {"active_only_eq_sum5_relerr": 0.0,
                               "C_combined_eq_syst_stat_ml_relerr": 0.0,
                               "full_total_residual_eq_stat_plus_ml_relerr": 0.0}}
        return P.stamp_non_adoptable(prov, env=env)

    def test_producer_stamps_only_under_the_env_var(self):
        self.assertIs(self._prov(True)[P.NON_ADOPTABLE_KEY], True)
        self.assertNotIn(P.NON_ADOPTABLE_KEY, self._prov(False))
        # an unset/other value must not stamp -- a truthy-string bug here would mark every build
        for v in ("", "0", "true", "yes"):
            self.assertNotIn(P.NON_ADOPTABLE_KEY,
                             P.stamp_non_adoptable({}, env={"P4_NON_ADOPTABLE": v}),
                             f"value {v!r} should not stamp; only the exact string '1' does")

    def _run_adopt(self, d, manifest_obj, receipt_extra=None, manifest_on_disk=None, drop_keys=()):
        """Invoke the real adopter CLI. `manifest_on_disk` lets a caller hand the adopter a
        DIFFERENT manifest from the one the receipt was built against -- the bypass path.
        `drop_keys` REMOVES keys after `receipt_extra` is applied, which `update()` cannot do; it
        exists so a test can build a receipt that is missing a key entirely (OI-128).

        The default receipt carries `gates` with the band-completeness gate because that is what a
        receipt from the CURRENT validator looks like -- it appends every cleared gate and only
        then sets result=PASS. Omitting it here would make every caller below exercise OI-128's
        refusal instead of the gate it is actually testing."""
        import json, subprocess
        mf = Path(d) / "std_component_manifest.json"
        mf.write_text(json.dumps(manifest_obj))
        val_obj = {"result": "PASS", "component_manifest_sha256": P.sha256_file(str(mf)),
                   "gates": [ADOPT.BAND_COMPLETENESS_GATE]}
        val_obj.update(receipt_extra or {})
        for _k in drop_keys:
            val_obj.pop(_k, None)
        if manifest_on_disk is not None:            # swap the file AFTER the receipt was digested
            mf.write_text(json.dumps(manifest_on_disk))
        val = Path(d) / "val.json"
        val.write_text(json.dumps(val_obj))
        cand = Path(d) / "cand.root"
        cand.write_bytes(b"x")
        r = subprocess.run([sys.executable, str(ND / "p4_adopt_standard.py"),
                            "--candidate", str(cand), "--component-manifest", str(mf),
                            "--validation", str(val), "--out", str(Path(d) / "o.root"),
                            "--i-understand-adoption"],
                           capture_output=True, text=True, cwd=str(ND))
        return r.stdout + r.stderr

    def test_marked_manifest_is_refused_and_unmarked_is_not(self):
        """Extended 2026-08-10 for the binding fix. The adopter used to read the marker out of a
        manifest supplied on its own command line with nothing tying that file to the receipt, so
        the refusal could be deleted by editing a copy. Three cases now: marked is refused; a
        marker-STRIPPED substitute is refused on the binding; unmarked-and-genuine is not refused
        on either ground."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out_marked = self._run_adopt(d, self._prov(True))
        with tempfile.TemporaryDirectory() as d:
            out_unmarked = self._run_adopt(d, self._prov(False))
        with tempfile.TemporaryDirectory() as d:
            # THE BYPASS: receipt digested the marked manifest, adopter is handed a stripped one
            out_swapped = self._run_adopt(d, self._prov(True),
                                          manifest_on_disk=self._prov(False))

        self.assertIn(P.NON_ADOPTABLE_KEY, out_marked,
                      "the adopter did not cite the non-adoptable marker when refusing")
        self.assertIn("not adoptable", out_marked)

        self.assertIn("sha256 mismatch", out_swapped,
                      "a marker-stripped substitute manifest was NOT caught by the receipt "
                      "binding -- the self-declared rejection is editable away")

        # the genuine unmarked one still fails (its inputs are fake) -- but it must NOT fail on
        # either the marker or the binding, or those gates fire unconditionally and prove nothing
        self.assertNotIn("not adoptable", out_unmarked,
                         "an UNMARKED manifest was refused as non-adoptable; the gate fires "
                         "unconditionally and would refuse a real candidate too")
        self.assertNotIn("sha256 mismatch", out_unmarked,
                         "the binding rejected a manifest that IS the validated one")

    # ---- OI-128: a PASS receipt must PROVE the band-completeness gate ran -------------------
    # The adopter required only `result == "PASS"`, and `gates` appeared nowhere in it except a
    # success print. A receipt written after the 2026-08-10 component-manifest binding fix but
    # before the band-completeness gate existed therefore carried the binding, said PASS, had never
    # refereed the band set against the support family -- and was adoptable.

    def test_adopt_refuses_a_pass_receipt_that_never_ran_band_completeness(self):
        """THE DEFECT. A PASS receipt whose gate inventory lacks the band-completeness gate must be
        refused, and the refusal must NAME the gate rather than failing generically."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = self._run_adopt(d, self._prov(False),
                                  receipt_extra={"gates": ["merged_inseparability",
                                                           "component_manifest_bound",
                                                           "exact_5_active_bands"]})
        self.assertIn(ADOPT.BAND_COMPLETENESS_GATE, out,
                      "the adopter accepted, or refused without naming, a PASS receipt that never "
                      "ran the band-completeness gate -- OI-128 is open")
        self.assertIn("silently short", out,
                      "the refusal did not explain WHY a missing band-completeness gate matters")

    def test_adopt_fails_closed_when_the_receipt_has_no_gates_key_at_all(self):
        """Fail CLOSED, not open. An absent inventory is the oldest form of exactly the receipt
        this gate exists to reject, so 'no gates key' must never read as 'old format, allow'."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = self._run_adopt(d, self._prov(False), drop_keys=("gates",))
        self.assertIn("carries no `gates` list", out,
                      "a receipt with NO gates key was not refused on that ground -- the "
                      "absent-inventory case is waved through")
        self.assertIn("FAIL-CLOSED", out)

    def test_the_band_completeness_gate_does_not_fire_when_the_gate_is_recorded(self):
        """Negative control. Without this, the two tests above would pass just as well if the new
        requirement rejected EVERY receipt, which would refuse a real candidate too."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = self._run_adopt(d, self._prov(False))       # default receipt records the gate
        self.assertNotIn("silently short", out,
                         "the band-completeness requirement fired on a receipt that DOES record "
                         "the gate -- it rejects unconditionally and proves nothing")
        self.assertNotIn("carries no `gates` list", out)

    def test_band_completeness_gate_name_matches_the_validator_literal(self):
        """Drift guard. The gate name is duplicated in p4_adopt_standard.py because p4_lib.py was
        under repair when this landed. Duplication that nothing checks is how a consumer silently
        stops matching its producer, so assert the producer still spells it the same way."""
        src = (ND / "p4_validate_active_lateral.py").read_text()
        self.assertIn(f'out["gates"].append("{ADOPT.BAND_COMPLETENESS_GATE}")', src,
                      "p4_validate_active_lateral.py no longer appends the gate name that "
                      "p4_adopt_standard.BAND_COMPLETENESS_GATE requires -- the adopter would "
                      "refuse every genuine receipt. Re-sync the two, or move the constant to "
                      "p4_lib.py now that it is free.")

    def test_removing_the_marker_from_a_manifest_makes_the_gate_pass(self):
        """Self-guard: if someone deletes the stamp from the builder, this is what the adopter
        would then see -- and it would sail through. Demonstrated, not asserted."""
        prov = self._prov(True)
        with self.assertRaises(P4GateError):
            P.require_adoptable(prov)
        prov.pop(P.NON_ADOPTABLE_KEY)
        P.require_adoptable(prov)      # must not raise


class IntegralLegIsADiscriminator(unittest.TestCase):
    """2026-08-09. The integral reproducibility leg was widened once, correctly, and must not be
    widened again: its whole dynamic range is ~100x (incoherent round-off floor to fully coherent
    ceiling) and the tolerance already sits at 55% of the ceiling. A comment saying so is not a
    guard -- the previous widening was also well-commented -- so the ceiling is asserted here."""

    def test_tolerance_stays_below_the_coherent_ceiling(self):
        """Widening toward the ceiling does not buy margin; it buys the inability to detect a
        coherent shift, which is the leg's only purpose."""
        self.assertLess(P.REPRO_RTOL_INTEGRAL, P.INTEGRAL_LEG_COHERENT_CEILING,
                        "REPRO_RTOL_INTEGRAL has reached the fully-coherent ceiling: at this "
                        "tolerance a uniform shift of every bin PASSES the integral leg, so the "
                        "leg no longer discriminates anything. See the derivation in p4_lib.")
        self.assertGreater(P.REPRO_RTOL_INTEGRAL, P.INTEGRAL_LEG_INCOHERENT_FLOOR,
                           "REPRO_RTOL_INTEGRAL is at or below the pure round-off floor; it will "
                           "false-alarm on every correct re-run")

    def test_the_range_is_genuinely_narrow(self):
        """The reason this cannot be fixed by picking a better number: the whole usable band is
        two orders of magnitude, so 'leave more margin' has nowhere to go."""
        span = P.INTEGRAL_LEG_COHERENT_CEILING / P.INTEGRAL_LEG_INCOHERENT_FLOOR
        self.assertLess(span, 200.0,
                        "the coherent/incoherent span grew; re-derive the argument rather than "
                        "assuming the recorded reasoning still applies")
        self.assertAlmostEqual(span, 103.4, delta=2.0)

    def test_breach_diagnostic_separates_roundoff_from_a_coherent_shift(self):
        """The pre-specified response, DEMONSTRATED on both branches rather than described. A
        criterion written before a breach is worth nothing if it cannot actually tell the two
        cases apart -- and 'sign' was already offered once as a discriminator that could not
        (BEN-060), so this test is the check that the replacement is not the same mistake."""
        rng = np.random.default_rng(20260809)
        n = 10694
        b = rng.uniform(1.0, 100.0, n)

        # (1) round-off tail: scattered, sign-biased at the recorded 0.4594, content-independent
        signs = np.where(rng.random(n) < 0.4594, 1.0, -1.0)
        a_round = b + signs * b * rng.uniform(0, 2e-11, n)
        d_round = P.diagnose_integral_breach(a_round, b, central=b)
        self.assertLess(abs(d_round["sigma_from_roundoff_bias"]), 4.0,
                        "a genuine round-off tail must look like the recorded bias")
        self.assertLess(abs(d_round.get("corr_reldev_vs_central", 0.0)), 0.05,
                        "round-off must be uncorrelated with bin content")

        # (2) coherent shift: every bin moves the same way and the deviation scales with content
        a_coh = b * (1.0 + 3e-11)
        d_coh = P.diagnose_integral_breach(a_coh, b, central=b)
        self.assertEqual(d_coh["frac_positive"], 1.0)
        self.assertGreater(abs(d_coh["sigma_from_roundoff_bias"]), 50.0,
                           "a coherent shift must be many sigma from the round-off bias -- if it "
                           "is not, this diagnostic cannot do its job and must be replaced")

        # the two branches must reach OPPOSITE verdicts under the pre-specified rule
        def proceeds(d):
            return (abs(d["sigma_from_roundoff_bias"]) < 4.0
                    and abs(d.get("corr_reldev_vs_central", 0.0)) < 0.05)
        self.assertTrue(proceeds(d_round))
        self.assertFalse(proceeds(d_coh))


class TmpdirGuardItself(unittest.TestCase):
    """The conftest tmpdir guard had NO test of its own (found in the 2026-08-09 verifier preflight).

    It exists because three consecutive verifier passes lost ~14% of the suite -- 23 of 165 on the
    last -- to ERRORS rather than failures, when the read-only audit sandbox provided no writable
    temp directory. A guard whose whole job is to protect a run happening somewhere this machine is
    NOT is the last place to rely on "it worked when I tried it": here the guard is INERT, because
    a writable tmpdir exists, so an ordinary green run says nothing about it. Test the mechanism."""

    def _fresh_conftest(self):
        import importlib
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import conftest
        return importlib.reload(conftest)

    class _Boom:
        def __init__(self, *a, **k):
            raise OSError("read-only file system")

    class _FakeItem:
        def __init__(self, fn=None):
            if fn is not None:
                self.function = fn
            self.marks = []

        def get_closest_marker(self, _name):
            return None

        def add_marker(self, m):
            self.marks.append(m)

    def test_probe_is_true_when_a_tmpdir_works(self):
        self.assertTrue(self._fresh_conftest()._tmpdir_is_writable())

    def test_probe_is_false_when_tempfile_raises(self):
        """The sandbox failure mode. TMPDIR alone CANNOT simulate it -- pointing TMPDIR at a
        read-only directory does not reproduce the sandbox because tempfile falls through to
        /tmp, /var/tmp and cwd. A preflight that set TMPDIR, saw green, and concluded the guard
        was exercised would have been wrong; that is why this monkeypatches instead."""
        import tempfile
        real = tempfile.TemporaryDirectory
        tempfile.TemporaryDirectory = self._Boom
        try:
            self.assertFalse(self._fresh_conftest().TMPDIR_WRITABLE)
        finally:
            tempfile.TemporaryDirectory = real
            self._fresh_conftest()

    def test_tmpdir_dependent_tests_are_SKIPPED_not_errored(self):
        """The point of the guard: an error reads as a defect, a skip reads as a skip."""
        import tempfile
        real = tempfile.TemporaryDirectory

        def needs_a_tmpdir():
            with tempfile.TemporaryDirectory() as d:
                return d

        def needs_nothing():
            return 1 + 1

        tempfile.TemporaryDirectory = self._Boom
        try:
            cf = self._fresh_conftest()
            items = [self._FakeItem(needs_a_tmpdir), self._FakeItem(needs_nothing)]
            cf.pytest_collection_modifyitems(None, items)
            self.assertEqual(len(items[0].marks), 1,
                             "a tmpdir-dependent test was NOT skipped with no writable tmpdir; it "
                             "would ERROR in the audit sandbox and read as a defect")
            self.assertEqual(len(items[1].marks), 0,
                             "a test needing no tmpdir was skipped; the guard over-fires and would "
                             "hide real coverage behind phantom skips")
        finally:
            tempfile.TemporaryDirectory = real
            self._fresh_conftest()

    def test_guard_is_inert_when_a_tmpdir_exists(self):
        """Both directions: with a writable tmpdir nothing is skipped -- so a green local run is
        not evidence the guard works, which is exactly why the tests above exist."""
        cf = self._fresh_conftest()
        self.assertTrue(cf.TMPDIR_WRITABLE)
        items = [self._FakeItem(lambda: 1)]
        cf.pytest_collection_modifyitems(None, items)
        self.assertEqual(len(items[0].marks), 0)


class PacketB1BandSetCompleteness(unittest.TestCase):
    """PACKET B1 / verifier defect #6 — acceptance record.

    The eleven adversarial manifests were authored by the OVERSIGHT session, blind, independently
    of this check (Packet B constraint 3; BEN-040 and repair-7's self-guard are why). Their key was
    withheld until after the run. Batch 2 is deliberately MIXED — B1_K is an over-rejection control
    that must be ACCEPTED, and was not identified in advance.

    Pre-fix code accepts every must-reject variant: the only band-related gates were "every key the
    manifest lists exists in the candidate ROOT" and a C_syst identity summing exactly the keys the
    manifest lists, both of which a short BUILD satisfies by construction."""

    FIX = Path(__file__).resolve().parent / "fixtures" / "packet_b1_adversarial"
    MUST_REJECT = ["B1_A", "B1_B", "B1_C", "B1_D", "B1_E", "B1_F",
                   "B1_G", "B1_H", "B1_I", "B1_J"]
    MUST_ACCEPT = ["B1_K"]

    def _real(self):
        import json
        p = self.FIX / "REFERENCE_real_manifest.json"
        if not p.exists():
            self.skipTest("reference manifest not present")
        return json.load(open(p))

    def _run(self, comp, real):
        return P.require_band_set_completeness(
            comp, real["all_syst_bands"], real["component_content_hash"],
            P.BANDS, real["support_family_sha256"])

    def _load(self, tag):
        import json
        return json.load(open(self.FIX / f"std_component_manifest.{tag}.json"))

    def test_real_manifest_is_accepted(self):
        real = self._real()
        st = self._run(real, real)
        self.assertEqual(st["n_required_bands"], 45)
        self.assertEqual(st["n_retained_expected"], 40)
        self.assertEqual(st["n_candidate_keys_expected"], 48)

    def test_every_adversarial_variant_is_rejected(self):
        real = self._real()
        for tag in self.MUST_REJECT:
            with self.subTest(tag):
                with self.assertRaises(P4GateError, msg=f"{tag} was ACCEPTED"):
                    self._run(self._load(tag), real)

    def test_the_over_rejection_control_is_accepted(self):
        """B1_K is clean. A check that rejects the whole batch has failed it, not passed it --
        `code_rev == HEAD` and `verifier_crosscheck` were both correct about their defect and both
        blocked correct data (KNOWN_ISSUES #24)."""
        real = self._real()
        for tag in self.MUST_ACCEPT:
            with self.subTest(tag):
                self._run(self._load(tag), real)

    def test_identity_comparison_is_not_prefix_based(self):
        """B1_H's perturbed hash matches the real one in its first 12 characters. This repo prints
        sha[:12] almost everywhere, so a prefix comparison is a natural thing to write."""
        real = self._real()
        h = self._load("B1_H")
        band = next(b for b in real["all_syst_bands"]
                    if h["component_content_hash"].get(b) != real["component_content_hash"].get(b))
        self.assertEqual(h["component_content_hash"][band][:12],
                         real["component_content_hash"][band][:12],
                         "fixture no longer exercises the truncated-comparison trap")
        self.assertNotEqual(h["component_content_hash"][band],
                            real["component_content_hash"][band])


class PacketPB2ResumeSurface(unittest.TestCase):
    """PACKET PB2 / verifier defect #2 — acceptance record.

    Cases are GENERATED (`tests/fixtures/packet_b2_adversarial/gen_b2_cases.py`) rather than static,
    because they reference repo blobs: a static receipt would, after the next commit to any surface
    module, mismatch on several paths at once — still rejecting, but for the wrong reason, leaving a
    green test that no longer isolates the defect. Authored by the oversight session; which cases
    must be ACCEPTED was withheld, because for PB2 the live hazard is over-rejection.

    THE DECISION, in the form a future reader needs: resume binds the PRODUCING CLOSURE (6 modules
    reachable from the unfold driver), not the 15-module surface. Whole-surface binding would
    invalidate all ten endpoint resumes on every `p4_lib.py` commit -- and the point is not the
    ~1h40m of re-unfolds. It is that such a check GETS SWITCHED OFF within two rounds, after which
    there is neither the binding nor an honest record of not having one, while the documentation
    still claims the property. A narrower check that stays on beats a broader one that is disabled.

    THE CLOSURE WAS DERIVED TWICE, INDEPENDENTLY, AND AGREED. The oversight session walked the
    import graph with its own AST traversal, deliberately not importing `p4_lib` so that it COULD
    disagree; this lane derived it from the other side. Both returned the same six modules and the
    same sole transitive-only member at depth 2 (`omnifold_nn_core.py`). That is a stronger
    provenance claim than either derivation alone, and it is what makes case P a decision rather
    than a possible miss.

    SCOPE OF THIS CLASS, CORRECTED 2026-08-11. What follows proves the HELPERS, and the verifier
    was right that on its own that proved nothing about resume: when these cases were written the
    launcher wrote no blob record and `p4_check_receipt.py` never called `check_resume_surface`,
    so the production skip path could not fail any of them. The end-to-end half now lives in
    `tests/test_p4_resume_integration.py::PB2ProducingClosureResume`, which drives the real
    checker CLI against receipts rendered by the launcher's own format string and its own closure
    command. Keep both: these cases isolate the logic, those bind it to the path that runs.
    """

    REPO = str(Path(__file__).resolve().parents[2])
    DRIVER = "nd-unfolding/unfold_nd_omnifold_unbinned.py"

    def _closure(self):
        return P.producing_closure(self.REPO, self.DRIVER)

    def test_closure_excludes_modules_that_cannot_run_during_production(self):
        """The design decision, asserted: p4_* modules are in the execution surface but are not
        reachable from the unfold driver, so they cannot have affected an endpoint ROOT."""
        c = set(self._closure())
        self.assertIn("unbinned_unfolding/python/omnifold.py", c)
        self.assertIn("nd-unfolding/xsec_nd.py", c)
        self.assertIn("nd-unfolding/omnifold_nn_core.py", c)   # transitive-only, depth 2
        for excluded in ("nd-unfolding/p4_lib.py", "nd-unfolding/p4_evidence.py",
                         "nd-unfolding/p4_project_4d.py"):
            self.assertNotIn(excluded, c,
                             f"{excluded} is not reachable from the unfold driver; binding it "
                             f"would invalidate every endpoint resume on each p4_* commit")

    def test_a_changed_closure_member_blocks_resume(self):
        c = self._closure()
        head = {q: f"blob{i}" for i, q in enumerate(c)}
        ok, _ = P.check_resume_surface({P.RESUME_BLOB_FIELD: dict(head)}, c, head)
        self.assertTrue(ok)
        for victim in c:                       # every member, direct or transitive
            with self.subTest(victim):
                rec = dict(head); rec[victim] = "CHANGED"
                ok, why = P.check_resume_surface({P.RESUME_BLOB_FIELD: rec}, c, head)
                self.assertFalse(ok, f"a change to {victim} did not block resume")
                self.assertIn(victim, why)

    def test_an_incomplete_record_blocks_resume(self):
        c = self._closure()
        head = {q: f"blob{i}" for i, q in enumerate(c)}
        rec = {q: v for q, v in head.items() if q != c[0]}
        ok, why = P.check_resume_surface({P.RESUME_BLOB_FIELD: rec}, c, head)
        self.assertFalse(ok)
        self.assertIn("omits", why)

    def test_a_legacy_receipt_is_grandfathered_not_blocked(self):
        """KNOWN_ISSUES #24. The ten receipts on scratch carry no such field. A check that demands
        one blocks demonstrably correct data, which this lane has shipped twice.

        BOUNDED 2026-08-11: this holds only for a receipt that ALSO declares no `receipt_schema`.
        Once the launcher began writing the record, absence stopped being evidence of age, so a
        receipt declaring the current schema without one is malformed and rejects -- see
        `PB2ProducingClosureResume.test_current_schema_receipt_without_the_record_is_rejected...`.
        """
        c = self._closure()
        ok, why = P.check_resume_surface({"tag": "BeamAngleX_0", "mode": "produced"}, c, {})
        self.assertTrue(ok)
        self.assertIn("GRANDFATHERED", why)


if __name__ == "__main__":
    unittest.main(verbosity=2)
