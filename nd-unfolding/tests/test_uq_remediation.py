import ast
import importlib.util
import sys
import contextlib
import os
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np


ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))


class UnifiedThrowTests(unittest.TestCase):
    def test_asymmetric_interpolation_endpoints_and_pair(self):
        from uq_math import interpolate_asymmetric_ratio

        plus = np.array([2.0, 4.0])
        minus = np.array([0.5, 0.25])
        np.testing.assert_array_equal(interpolate_asymmetric_ratio(1.0, plus, minus), plus)
        np.testing.assert_array_equal(interpolate_asymmetric_ratio(0.0, plus, minus), np.ones(2))
        np.testing.assert_array_equal(interpolate_asymmetric_ratio(-1.0, plus, minus), minus)
        np.testing.assert_allclose(
            interpolate_asymmetric_ratio(np.array([0.5, -0.5]), plus, minus),
            np.array([np.sqrt(2.0), 0.5]),
        )

    def test_invalid_ratio_is_explicit(self):
        from uq_math import interpolate_asymmetric_ratio

        with self.assertRaises(ValueError):
            interpolate_asymmetric_ratio(1.0, np.array([0.0, np.nan]), np.ones(2))

    def test_mat_pair_covariance(self):
        from uq_math import mat_covariance

        minus = np.array([8.0, 22.0])
        plus = np.array([14.0, 18.0])
        expected = np.outer((plus - minus) / 2.0, (plus - minus) / 2.0)
        np.testing.assert_allclose(mat_covariance(np.stack([minus, plus])), expected)

    def test_fixed_seed_null_throws_zero(self):
        from uq_math import joint_throw_covariance

        X = np.repeat(np.array([[1.0, 2.0, 3.0]]), 12, axis=0)
        C, shift = joint_throw_covariance(X, np.array([1.0, 2.0, 3.0]))
        np.testing.assert_allclose(C, 0.0, atol=1e-15)
        np.testing.assert_allclose(shift, 0.0, atol=1e-15)

    def test_synthetic_slab_and_block_combine_end_to_end(self):
        import unified_throw_cov as utc
        from uq_math import joint_throw_covariance, mat_covariance

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            # flux_normalized=1 on every synthetic slab. This is FIXTURE-STALE, not the guard being
            # over-strict: J28 (081ae4a) made `--combine` refuse slabs that carry no stamp, because a
            # real unstamped slab was divided by the CV flux integral instead of each universe's own
            # Phi_u. A fixture built here has no flux normalisation to get wrong -- there is no Phi_CV
            # division to correct -- so it is normalised by construction and stamping states that.
            # Stamping loses NO coverage: the rejection behaviour is separately and deliberately
            # tested by test_flux_universe_fix.CombineRefusesUnstampedSlabs, which asserts the
            # predicate accepts only a stamped slab. The guard itself must stay fail-closed.
            throws = np.array([[0.8, 2.1], [1.2, 1.9], [1.1, 2.2]])
            np.savez(p / "throws_0.npz", xs=throws[:2], throws=np.array([0, 1]),
                     estimator_seed=np.int64(42), draw_seed=np.int64(1000), flux_normalized=np.int64(1))
            np.savez(p / "throws_1.npz", xs=throws[2:], throws=np.array([2]),
                     estimator_seed=np.int64(42), draw_seed=np.int64(1000), flux_normalized=np.int64(1))
            endpoints = np.array([[0.9, 2.2], [1.1, 1.8]])
            np.savez(p / "blocks.npz", xs=endpoints,
                     labels=np.array(["MaCCQE:0", "MaCCQE:1"], dtype=object),
                     estimator_seed=np.int64(42), draw_seed=np.int64(1000),
                     kinds=np.array(["knob", "knob"], dtype=object),
                     flux_normalized=np.int64(1))

            d = {"edges": [np.array([0.0, 1.0, 2.0])],
                 "w_truth": np.ones(1), "w_reco": np.ones(1), "td_w": np.ones(1)}
            old_load, old_kernel = utc._load_bank, utc._xsec_for_weights
            utc._load_bank = lambda bank: (d, ["MaCCQE"], 0)
            utc._xsec_for_weights = lambda *args, **kwargs: np.array([1.0, 2.0])
            try:
                args = SimpleNamespace(
                    bank=td, iters=1, estimator_seed=42, draw_seed=1000,
                    combine=str(p / "throws_*.npz"),
                    block_slabs=str(p / "blocks.npz"),
                    expected_throws="0-2", null=True, out_root=None)
                result = utc.do_combine(args)
                args.expected_throws = "0-3"
                with self.assertRaises(SystemExit):
                    utc.do_combine(args)
                # F2 guard: a slab stamped with a different estimator seed is rejected
                args.expected_throws = "0-2"
                # flux_normalized MUST be stamped here: without it the J28 guard fires FIRST
                # and this assertRaises passes without ever reaching the estimator-seed guard.
                # It was missing until 2026-08-18 -- the test was green via the wrong guard.
                np.savez(p / "throws_0.npz", xs=throws[:2], throws=np.array([0, 1]),
                         estimator_seed=np.int64(999), draw_seed=np.int64(1000),
                         flux_normalized=np.int64(1))
                with self.assertRaises(SystemExit):
                    utc.do_combine(args)
            finally:
                utc._load_bank, utc._xsec_for_weights = old_load, old_kernel

            expected_uni, expected_shift = joint_throw_covariance(throws, np.array([1.0, 2.0]))
            np.testing.assert_allclose(result["C_unified"], expected_uni)
            np.testing.assert_allclose(result["mean_shift"], expected_shift)
            np.testing.assert_allclose(result["C_blocksum"], mat_covariance(endpoints))
            self.assertEqual(result["fixed_seed_null_norm"], 0.0)
            np.testing.assert_array_equal(result["throw_ids"], [0, 1, 2])

    def test_unified_bank_rejects_missing_endpoints(self):
        import unified_throw_cov as utc

        with tempfile.TemporaryDirectory() as td:
            np.savez(Path(td) / "cv.npz", MCgen=np.zeros((2, 1)),
                     edges_0=np.array([0.0, 1.0]))
            with self.assertRaises(RuntimeError):
                utc._load_bank(td)

    def test_unified_bank_requires_exactly_100_flux_universes(self):
        import unified_throw_cov as utc

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            np.savez(p / "cv.npz", MCgen=np.zeros((2, 1)),
                     edges_0=np.array([0.0, 1.0]))
            for band in utc.KNOB_BANDS:
                for idx in (0, 1):
                    for stem in (f"sig_{band}_t_{idx}", f"sig_{band}_r_{idx}",
                                 f"td_{band}_{idx}"):
                        np.save(p / f"{stem}.npy", np.ones(2))
            # A contiguous 0..98 inventory used to be accepted by max-id inference.
            for idx in range(99):
                for stem in ("sig_flux_t_", "sig_flux_r_", "td_flux_"):
                    np.save(p / f"{stem}{idx}.npy", np.ones(2))
            with self.assertRaisesRegex(RuntimeError, "exactly 100"):
                utc._load_bank(td)

    def test_incremental_slab_write_is_atomic(self):
        import unified_throw_cov as utc

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "slab.npz"
            utc._atomic_savez(out, xs=np.arange(4), seed=np.int64(42))
            with np.load(out) as slab:
                np.testing.assert_array_equal(slab["xs"], np.arange(4))
                self.assertEqual(int(slab["seed"]), 42)
            self.assertEqual(list(Path(td).glob("*.tmp.npz")), [])

    def test_truth_ratio_bank_requires_exact_inventory(self):
        from uq_math import require_truth_ratio_bank

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            for idx in (0, 1):
                np.save(p / f"sig_Test_t_{idx}.npy", np.ones(2))
            for idx in range(3):
                np.save(p / f"sig_flux_t_{idx}.npy", np.ones(2))
            self.assertEqual(require_truth_ratio_bank(p, ["Test"], 3), [0, 1, 2])
            (p / "sig_flux_t_1.npy").unlink()
            with self.assertRaises(ValueError):
                require_truth_ratio_bank(p, ["Test"], 3)

    def test_guarded_ratio_policy_is_explicit(self):
        from uq_math import guarded_ratio

        with self.assertRaises(ValueError):
            guarded_ratio(np.array([1.0, np.nan]), invalid_policy="error")
        np.testing.assert_array_equal(
            guarded_ratio(np.array([1.0, np.nan]), invalid_policy="neutral"),
            np.ones(2),
        )
        # A composed joint throw is validated but not clipped a second time.
        np.testing.assert_array_equal(
            guarded_ratio(np.array([1e-4, 1e4]), clip=None),
            np.array([1e-4, 1e4]),
        )


class ProjectionAndIntegralTests(unittest.TestCase):
    def test_covariance_projection(self):
        from uq_math import project_covariance

        C = np.array([[4.0, 1.0, 0.0], [1.0, 9.0, 2.0], [0.0, 2.0, 16.0]])
        M = np.array([[1.0, 2.0, 0.0], [0.0, -1.0, 3.0]])
        np.testing.assert_allclose(project_covariance(C, M), M @ C @ M.T)

    def test_nonuniform_density_integral(self):
        from xsec_nd import total_xsec

        edges = [np.array([0.0, 1.0, 3.0]), np.array([0.0, 2.0, 5.0])]
        density = np.array([[1.0, 2.0], [3.0, 4.0]])
        expected = 1 * 1 * 2 + 2 * 1 * 3 + 3 * 2 * 2 + 4 * 2 * 3
        self.assertEqual(total_xsec(density, edges), expected)
        self.assertNotEqual(density.sum(), expected)


class SelectionSupportTests(unittest.TestCase):
    def test_lateral_migrations_both_directions(self):
        from uq_math import active_selection_masks

        truth = np.array([[0.9, 2.0], [1.1, 2.0], [0.5, 2.0], [0.5, 2.0]])
        reco = np.array([[0.9, 2.0], [1.1, 2.0], [0.9, 2.0], [1.1, 2.0]])
        pt_edges = (0.0, 1.0)
        pz_edges = (1.5, 3.0)
        tmask, rmask = active_selection_masks(truth, reco, pt_edges, pz_edges)
        np.testing.assert_array_equal(tmask, [True, False, True, True])
        np.testing.assert_array_equal(rmask, [True, False, True, False])

        truth_lat = np.array([[1.1, 2.0], [0.9, 2.0], [0.5, 2.0], [0.5, 2.0]])
        reco_lat = np.array([[1.1, 2.0], [0.9, 2.0], [1.1, 2.0], [0.9, 2.0]])
        tl, rl = active_selection_masks(truth_lat, reco_lat, pt_edges, pz_edges)
        self.assertTrue((~tmask & tl).any() and (tmask & ~tl).any())
        self.assertTrue((~rmask & rl).any() and (rmask & ~rl).any())

    def test_finite_support_signal_denom_closure(self):
        from uq_math import finite_observable_mask

        coords = np.array([[0.2, 2.0, 0.3], [0.3, 2.1, np.nan], [0.4, 2.2, 0.5]])
        signal = finite_observable_mask(coords)
        denom = finite_observable_mask(coords.copy())
        np.testing.assert_array_equal(signal, denom)
        self.assertEqual(signal.sum(), 2)


class ReplicaManifestTests(unittest.TestCase):
    def _write(self, path, seed, x):
        np.savez(path, seed=seed, xsec_flat=np.asarray(x), shape=np.array(np.asarray(x).shape))

    def test_manifest_rejects_missing_duplicate_nan_wrong_shape(self):
        from replica_manifest import load_replica_manifest

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            self._write(p / "r0.npz", 0, [1.0, 2.0])
            self._write(p / "r1.npz", 1, [1.1, 2.1])
            with self.assertRaises(ValueError):
                load_replica_manifest([p / "r0.npz"], expected_ids={0, 1})
            self._write(p / "dup.npz", 1, [1.2, 2.2])
            with self.assertRaises(ValueError):
                load_replica_manifest([p / "r0.npz", p / "r1.npz", p / "dup.npz"], expected_ids={0, 1})
            self._write(p / "nan.npz", 2, [np.nan, 1.0])
            with self.assertRaises(ValueError):
                load_replica_manifest([p / "r0.npz", p / "r1.npz", p / "nan.npz"])
            self._write(p / "badshape.npz", 2, [1.0, 2.0, 3.0])
            with self.assertRaises(ValueError):
                load_replica_manifest([p / "r0.npz", p / "r1.npz", p / "badshape.npz"])


class PETAndNNTests(unittest.TestCase):
    def test_pet_mc_bootstrap_factor_is_reproducible(self):
        from pet_bootstrap import mc_poisson_factor, poisson_event_weights

        seed = 19
        _, weighted = poisson_event_weights(np.ones(4), np.ones(20), seed)
        np.testing.assert_array_equal(weighted, mc_poisson_factor(20, seed))

        data32, mc32 = poisson_event_weights(
            np.ones(4, dtype=np.float32), np.ones(20, dtype=np.float32), seed)
        self.assertEqual(data32.dtype, np.float32)
        self.assertEqual(mc32.dtype, np.float32)

    def test_pet_toy_measured_bootstrap_retrains(self):
        from pet_bootstrap import retrained_bootstrap_toy

        nominal, replica = retrained_bootstrap_toy(seed=4)
        self.assertGreater(np.max(np.abs(replica - nominal)), 1e-6)

    def test_pet_replica_requires_full_coherent_draw_and_writes_manifest(self):
        from pet_bootstrap import (mc_poisson_factor, validate_full_replica_weights,
                                   write_xsec_replica)
        from replica_manifest import load_replica_manifest

        seed, n = 7, 6
        with tempfile.TemporaryDirectory() as td:
            weights = Path(td) / "weights.npz"
            np.savez(weights, w_push=np.linspace(0.8, 1.2, n),
                     mc_indices=np.arange(n),
                     mc_bootstrap_factor=mc_poisson_factor(n, seed),
                     bootstrap_seed=seed)
            with np.load(weights, allow_pickle=False) as z:
                validate_full_replica_weights(z, n, seed)
                with self.assertRaises(ValueError):
                    validate_full_replica_weights(z, n, seed + 1)

            edges = [np.array([0.0, 1.0, 3.0]), np.array([0.0, 2.0, 5.0])]
            xsec = np.array([[1.0, 2.0], [3.0, 4.0]])
            out = Path(td) / "replica_7.npz"
            total = write_xsec_replica(out, seed, xsec, edges)
            self.assertEqual(total, 44.0)
            rows, ids = load_replica_manifest([out], expected_ids={seed})
            np.testing.assert_array_equal(ids, [seed])
            np.testing.assert_array_equal(rows[0], xsec.ravel(order="C"))

    def test_inpipeline_nn_imports_sys(self):
        path = ND.parent / "unbinned_unfolding" / "python" / "omnifold.py"
        tree = ast.parse(path.read_text())
        imports = {n.names[0].name for n in tree.body if isinstance(n, ast.Import)}
        self.assertIn("sys", imports)

    def test_pet_cli_fixes_estimator_seed(self):
        path = ND / "pet" / "minerva_pet_dataloader.py"
        source = path.read_text()
        self.assertIn('"--estimator-seed"', source)
        self.assertIn("tf.keras.utils.set_random_seed(args.estimator_seed)", source)



class QuarantineCauseGuardTests(unittest.TestCase):
    """The TEST leg of quarantine causes 1, 2, 3 and 4 (VALIDATION_LEDGER.md's 2026-07-12 list).

    Criteria and the four legs each cause must clear:
    `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`.

    Every guard here is checked in BOTH directions -- the defect must fail, and the guarded object
    disappearing must ALSO fail. A test asserting only the absence of a bad construction passes
    vacuously once the thing under test is renamed or deleted, which is the null-as-absent shape.
    Mutation counts are recorded in the commit rather than asserted here, because a test cannot
    measure its own power.
    """

    # ---- cause 1: one-sided endpoint interpolation ------------------------------------------------
    def test_cause1_one_sided_cv_centered_pair_overstates_and_mat_form_does_not(self):
        """The defect, quantified on a pair rather than merely named.

        For a +/-1sigma pair the corrected form is mean-centered `mat_covariance([x-, x+])`, which is
        rank 1 in `(x+ - x-)/2`. The defective form was a CV-centered outer product of ONE endpoint,
        `outer(x+ - CV)`, which for an ASYMMETRIC pair keeps the symmetric component that mean-
        centering is supposed to kill -- so it does not merely differ, it overstates
        (`app_statmethods.tex:300-306, 1462`).

        This is the T leg. It is NOT the Magnitude leg for the adopted covariance, which requires the
        same comparison on that product's own bank and does not exist yet.
        """
        from uq_math import mat_covariance

        cv = np.array([10.0, 20.0])
        minus = np.array([8.0, 22.0])
        plus = np.array([14.0, 18.0])          # deliberately asymmetric about CV

        corrected = mat_covariance(np.stack([minus, plus]))
        half_range = (plus - minus) / 2.0
        np.testing.assert_allclose(corrected, np.outer(half_range, half_range))

        one_sided = np.outer(plus - cv, plus - cv)

        # Both are rank 1, so rank alone does not discriminate -- the direction and the size do.
        self.assertEqual(np.linalg.matrix_rank(corrected), 1)
        self.assertEqual(np.linalg.matrix_rank(one_sided), 1)
        self.assertGreater(
            np.trace(one_sided), np.trace(corrected),
            "on this asymmetric pair the one-sided CV-centered form must OVERSTATE the variance; "
            "if it ever does not, the fixture has drifted and the test has stopped discriminating",
        )
        # Pin the size so a future reader sees a magnitude and not just an inequality:
        # trace 4*4+2*2=20 corrected vs 16+4=20 ... asserted numerically rather than reasoned.
        self.assertAlmostEqual(float(np.trace(corrected)), 9.0 + 4.0, places=12)
        self.assertAlmostEqual(float(np.trace(one_sided)), 16.0 + 4.0, places=12)

    def test_cause1_the_corrected_primitives_are_PRESENT_and_not_merely_unbroken(self):
        """Presence half. Every cause-1 assertion above routes through these two names.

        If either is renamed or deleted, the tests above stop testing the convention and start
        testing an ImportError -- which reads as a tooling problem, not as the guard firing. Assert
        they exist and are callable so that failure mode is explicit.
        """
        import uq_math

        for name in ("mat_covariance", "interpolate_asymmetric_ratio"):
            self.assertTrue(hasattr(uq_math, name), f"uq_math.{name} has disappeared")
            self.assertTrue(callable(getattr(uq_math, name)))

    # ---- cause 2: CV centering (the F7 rule) ------------------------------------------------------
    def test_cause2_f7_requires_cv_centered_at_the_measured_ratio_and_not_at_the_floor(self):
        """The predeclared F7 rule, with the campaign's own measured numbers as the fixture.

        Measured on the adopted ensemble: ||mean_shift|| is 4.69x the sampling floor (37.1% of
        sqrt(Tr C) against a 7.9% floor), rising to 4.83x after the flux correction. Both must land
        on the "CV-centered variant is mandatory" side. A shift AT the floor must not.
        """
        from uq_math import f7_cv_centered_required, mean_shift_over_floor

        sqrt_tr, n = 4.443673650575504e-38, 160          # the J28-corrected throw ROOT, read from it
        floor = sqrt_tr / np.sqrt(n)

        self.assertAlmostEqual(mean_shift_over_floor(4.69 * floor, sqrt_tr, n), 4.69, places=9)
        self.assertTrue(f7_cv_centered_required(4.69 * floor, sqrt_tr, n))
        self.assertTrue(f7_cv_centered_required(4.83 * floor, sqrt_tr, n))
        self.assertFalse(f7_cv_centered_required(1.00 * floor, sqrt_tr, n))

        # The real adopted mean shift, from the ROOT: 1.878696733368378e-38 against sqrt_tr above.
        # 1.8787e-38 / (4.4437e-38/sqrt(160)) = 5.35 -- comfortably required. Pinned so the rule is
        # exercised on the actual product and not only on synthetic multiples of the floor.
        self.assertTrue(f7_cv_centered_required(1.878696733368378e-38, sqrt_tr, n))
        self.assertGreater(mean_shift_over_floor(1.878696733368378e-38, sqrt_tr, n), 5.0)

    def test_cause2_the_threshold_boundary_is_pinned_explicitly(self):
        """The codified threshold is 2.0 and that is a choice, so it is asserted rather than implied.

        The predeclared rule is qualitative ("~floor" vs ">> floor"); no number was ever recorded.
        Pinning the boundary here means a future change to F7_FLOOR_MULTIPLE fails a test that names
        it, instead of silently moving a publication gate.
        """
        from uq_math import F7_FLOOR_MULTIPLE, f7_cv_centered_required

        self.assertEqual(F7_FLOOR_MULTIPLE, 2.0)
        sqrt_tr, n = 1.0, 100
        floor = sqrt_tr / np.sqrt(n)
        self.assertFalse(f7_cv_centered_required(2.0 * floor, sqrt_tr, n), "strictly greater-than")
        self.assertTrue(f7_cv_centered_required(2.000001 * floor, sqrt_tr, n))

    def test_cause2_the_shift_is_returned_SEPARATELY_and_folding_it_in_changes_the_answer(self):
        """Cause 2 is about *where the shift goes*, so prove the two conventions are not the same.

        `joint_throw_covariance` returns (covariance, shift) as two objects. A CV-centered
        construction adds shift**2 to the per-bin variance. If that addition were zero the whole
        distinction would be empty, so assert it is not -- otherwise this guard could pass on a
        degenerate fixture forever.
        """
        from uq_math import joint_throw_covariance

        cv = np.array([1.0, 2.0])
        throws = np.array([[1.5, 2.5], [1.7, 2.1], [1.9, 2.9]])
        C, shift = joint_throw_covariance(throws, cv)

        self.assertEqual(np.asarray(C).ndim, 2)
        self.assertEqual(np.asarray(shift).ndim, 1)
        self.assertGreater(float(np.linalg.norm(shift)), 0.0, "degenerate fixture: shift is zero")

        mean_centered_var = np.diag(C)
        cv_centered_var = mean_centered_var + shift ** 2
        self.assertTrue(np.all(cv_centered_var > mean_centered_var),
                        "CV-centering must strictly inflate; if not, the fixture has drifted")

    # ---- cause 3: varying estimator seeds --------------------------------------------------------
    def test_cause3_mixed_seed_slabs_are_rejected_and_a_single_seed_is_accepted(self):
        """Both directions in one test, because only the pair is evidence.

        Rejection alone does not show the guard discriminates -- a guard that rejects everything
        would pass it. The accept case is what makes the reject case mean something.
        """
        import unified_throw_cov as utc

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            throws = np.array([[0.8, 2.1], [1.2, 1.9], [1.1, 2.2]])

            def write(seed_a, seed_b):
                np.savez(p / "throws_0.npz", xs=throws[:2], throws=np.array([0, 1]),
                         estimator_seed=np.int64(seed_a), draw_seed=np.int64(1000), flux_normalized=np.int64(1))
                np.savez(p / "throws_1.npz", xs=throws[2:], throws=np.array([2]),
                         estimator_seed=np.int64(seed_b), draw_seed=np.int64(1000), flux_normalized=np.int64(1))
                np.savez(p / "blocks.npz", xs=np.array([[0.9, 2.2], [1.1, 1.8]]),
                         labels=np.array(["MaCCQE:0", "MaCCQE:1"], dtype=object),
                         estimator_seed=np.int64(seed_a), draw_seed=np.int64(1000),
                         kinds=np.array(["knob", "knob"], dtype=object),
                         flux_normalized=np.int64(1))

            d = {"edges": [np.array([0.0, 1.0, 2.0])],
                 "w_truth": np.ones(1), "w_reco": np.ones(1), "td_w": np.ones(1)}
            old_load, old_kernel = utc._load_bank, utc._xsec_for_weights
            utc._load_bank = lambda bank: (d, ["MaCCQE"], 0)
            utc._xsec_for_weights = lambda *a, **k: np.array([1.0, 2.0])
            try:
                args = SimpleNamespace(bank=td, iters=1, estimator_seed=42, draw_seed=1000,
                                       combine=str(p / "throws_*.npz"),
                                       block_slabs=str(p / "blocks.npz"),
                                       expected_throws="0-2", null=True, out_root=None)
                write(42, 42)
                self.assertIsNotNone(utc.do_combine(args), "one seed must be ACCEPTED")
                write(42, 999)
                with self.assertRaises(SystemExit):
                    utc.do_combine(args)
            finally:
                utc._load_bank, utc._xsec_for_weights = old_load, old_kernel

    # ---- cause 4: scalar jitter subtraction ------------------------------------------------------
    def test_cause4_null_is_CHECKED_flag_is_present_in_both_directions(self):
        """The null-as-absent trap, in cause 4's own evidence.

        `--null` is optional, so a product built without it carries no `fixed_seed_null_norm` at all,
        and a criterion phrased "the null norm is not large" PASSES ON IT VACUOUSLY. The remedy is a
        flag that is always present: `fixed_seed_null_checked`. Assert it in BOTH states -- present
        and true when the check ran, present and FALSE when it did not. Asserting only the true case
        would leave "the flag is missing entirely" indistinguishable from "not checked".
        """
        import unified_throw_cov as utc

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            throws = np.array([[0.8, 2.1], [1.2, 1.9], [1.1, 2.2]])
            np.savez(p / "throws_0.npz", xs=throws[:2], throws=np.array([0, 1]),
                     estimator_seed=np.int64(42), draw_seed=np.int64(1000), flux_normalized=np.int64(1))
            np.savez(p / "throws_1.npz", xs=throws[2:], throws=np.array([2]),
                     estimator_seed=np.int64(42), draw_seed=np.int64(1000), flux_normalized=np.int64(1))
            np.savez(p / "blocks.npz", xs=np.array([[0.9, 2.2], [1.1, 1.8]]),
                     labels=np.array(["MaCCQE:0", "MaCCQE:1"], dtype=object),
                     estimator_seed=np.int64(42), draw_seed=np.int64(1000),
                     kinds=np.array(["knob", "knob"], dtype=object),
                     flux_normalized=np.int64(1))

            d = {"edges": [np.array([0.0, 1.0, 2.0])],
                 "w_truth": np.ones(1), "w_reco": np.ones(1), "td_w": np.ones(1)}
            old_load, old_kernel = utc._load_bank, utc._xsec_for_weights
            utc._load_bank = lambda bank: (d, ["MaCCQE"], 0)
            utc._xsec_for_weights = lambda *a, **k: np.array([1.0, 2.0])
            try:
                args = SimpleNamespace(bank=td, iters=1, estimator_seed=42, draw_seed=1000,
                                       combine=str(p / "throws_*.npz"),
                                       block_slabs=str(p / "blocks.npz"),
                                       expected_throws="0-2", null=True, out_root=None)
                checked = utc.do_combine(args)
                self.assertIn("fixed_seed_null_checked", checked)
                self.assertTrue(checked["fixed_seed_null_checked"])
                self.assertEqual(checked["fixed_seed_null_norm"], 0.0)

                args.null = False
                unchecked = utc.do_combine(args)
                self.assertIn("fixed_seed_null_checked", unchecked,
                              "the flag must be PRESENT even when the check did not run")
                self.assertFalse(unchecked["fixed_seed_null_checked"])
                self.assertIsNone(unchecked["fixed_seed_null_norm"],
                                  "a number nobody measured must not be invented as 0.0")
            finally:
                utc._load_bank, utc._xsec_for_weights = old_load, old_kernel

    def test_cause4_no_jitter_subtraction_survives_on_the_combine_path(self):
        """Absence AND presence.

        A grep-style assertion that the token `jitter` does not appear in a subtraction would pass if
        `unified_throw_cov.py` were deleted, so it is paired with a presence assertion on the thing
        that REPLACED the subtraction: the `--null` requirement itself. Structural (AST/attribute)
        rather than textual, so a comment mentioning jitter cannot fail it -- the file's own header
        legitimately says "no jitter subtraction".
        """
        import unified_throw_cov as utc

        # presence: the replacement mechanism exists and is reachable
        source = Path(utc.__file__).read_text()
        tree = ast.parse(source)
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        self.assertIn("null_norm", names,
                      "the fixed-seed null is what replaced the jitter subtraction; if this name is "
                      "gone the guard below is testing nothing")

        # absence: no assignment anywhere subtracts a scalar jitter term from a covariance/trace
        offenders = []
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
                seg = ast.get_source_segment(source, node) or ""
                if "jitter" in seg.lower():
                    offenders.append(seg)
        self.assertEqual(offenders, [], f"scalar jitter subtraction reintroduced: {offenders}")


class Cause6ProjectionCoverageTests(unittest.TestCase):
    """Quarantine cause 6 (incomplete statistical projection), the `(E_avail,W)` route.

    Two halves, because a static check alone would only prove a string is present:
      * NUMERIC -- prove the hazard is real, that an all-zero row of M yields an exactly zero
        variance rather than an error. No ROOT needed; `project_covariance` is pure numpy.
      * STATIC  -- prove `eavailW_covariance.py` now detects it. That module imports ROOT and reads
        a 142 GB omnifile, so it cannot be executed here; same constraint and same convention as
        `test_flux_universe_fix.EavailWFluxBlockIsPerUniverse`, including a pre-fix positive control.
    """

    FNAME = "eavailW_covariance.py"

    def test_an_all_zero_projection_row_yields_a_silently_ZERO_variance(self):
        """The hazard, demonstrated rather than asserted.

        A destination bin no source bin reaches gets variance exactly 0. That does not look like
        missing data downstream -- it looks like an infinitely precise measurement, and any chi2 or
        significance built on it divides by it. This is why the guard reports rather than shrugs.
        """
        from uq_math import project_covariance

        C_src = np.array([[4.0, 1.0], [1.0, 9.0]])
        # dst bin 0 gets both source bins; dst bin 1 is an ORPHAN -- an all-zero row.
        M = np.array([[1.0, 1.0], [0.0, 0.0]])
        C_dst = project_covariance(C_src, M)

        self.assertEqual(C_dst.shape, (2, 2))
        self.assertEqual(float(C_dst[1, 1]), 0.0, "the orphan bin's variance is exactly zero")
        self.assertGreater(float(C_dst[0, 0]), 0.0, "the supported bin is unaffected")
        # And nothing in the projection itself complains -- that is the whole point.
        self.assertTrue(np.all(np.isfinite(C_dst)))
        # A PSD check passes too, so PSD cannot be the thing that catches this.
        self.assertGreaterEqual(float(np.linalg.eigvalsh(C_dst)[0]), -1e-12)

    def test_eavailW_detects_orphan_rows(self):
        """STATIC: the module computes the empty-row set and says something about it."""
        src = (ND / self.FNAME).read_text()
        tree = ast.parse(src)

        calls_any_axis1 = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "nonzero"
        ]
        self.assertTrue(calls_any_axis1, "no np.nonzero(...) -- the orphan-row set is not computed")
        self.assertIn("Mew.any(axis=1)", src,
                      "the empty-row test must be over Mew's rows (the destination direction)")
        self.assertIn("_ew_empty", src, "the orphan-row count must be bound to a name and reported")

    def test_the_prefix_source_would_fail(self):
        """POWER: reconstruct the pre-fix module and require the assertions above to fail on it.

        KEYED ON AST `FunctionDef` NODES AND EXPLICIT CALL SITES, NOT ON COMMENT MARKERS. Lane D's
        specification, after the marker version broke twice under the `BEN-450` repair -- once when
        propagation put the value in a second place and once when the single-source helper put the
        computation in a third, both outside a marker-based excision. Two properties a marker
        cannot give you:

          * it follows the code through further factoring;
          * IT RAISES WHEN THE FUNCTION IS RENAMED. A marker that stops matching excises ZERO
            lines, and the assertions below then pass on an UNMODIFIED source -- a power test that
            has silently stopped being one. That is the failure mode this rewrite exists to remove.

        Substitution over deletion throughout, and the `ast.parse` arm is kept: deleting a line
        inside a multi-line call leaves an unclosed paren, and every token-absence assertion is
        true of source that is no longer a program.
        """
        src = (ND / self.FNAME).read_text()
        lines = src.split("\n")

        # ---- region 1: the helper that computes the empty-row set, located by NAME ----
        tree = ast.parse(src)
        fdefs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        self.assertIn("ew_coverage_report", fdefs,
                      "ew_coverage_report not found as a top-level function: this power test can no "
                      "longer locate what it must excise, and would otherwise pass vacuously")
        fd = fdefs["ew_coverage_report"]
        lo, hi = fd.lineno - 1, (fd.end_lineno or fd.lineno)
        for i in range(lo, hi):
            lines[i] = ""

        # ---- regions 2-4: every STATEMENT in main() that mentions the names, excised as a
        # STATEMENT rather than as a line. This is the same lesson twice: the guard's report is a
        # multi-line f-string expression followed by an `if` block, so blanking matching LINES
        # orphans continuation lines and an if-body -- caught by the `ast.parse` arm below as an
        # IndentationError, the second time that arm has caught this reconstruction failing for the
        # wrong reason. Statement boundaries come from the AST, so a multi-line expression and a
        # compound statement are each removed whole.
        #
        # THE ONE STATEMENT THAT MUST SURVIVE is the `write_ew_outputs(...)` call: deleting it would
        # remove the write entirely, and the pre-fix module DID write its outputs -- it just did not
        # propagate the coverage result. Its argument is SUBSTITUTED instead.
        main_fd = next((n for n in tree.body
                        if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
        self.assertIsNotNone(main_fd, "main() not found; this power test cannot locate its subject")
        NAMES = ("_ew_empty", "_n_ew_empty")
        touched = 0
        for stmt in ast.walk(main_fd):
            if not isinstance(stmt, ast.stmt) or stmt is main_fd:
                continue
            lo, hi = stmt.lineno - 1, (stmt.end_lineno or stmt.lineno)
            seg = "\n".join(src.split("\n")[lo:hi])
            if not any(nm in seg for nm in NAMES):
                continue
            if "write_ew_outputs(" in seg:
                continue          # survives; its argument is substituted below
            for i in range(lo, hi):
                lines[i] = ""
            touched += 1
        self.assertGreater(touched, 0,
                           "no statement in main() mentions the empty-row names: the guard is not "
                           "where this test expects it and the assertions below would pass vacuously")

        arg = "        (_ew_empty, _n_ew_empty))"
        self.assertIn(arg, src, "the propagated argument is not where this test expects it")
        prefix_src = "\n".join(lines).replace(arg, "        (np.array([], dtype=int), 0))")

        self.assertNotIn("_ew_empty", prefix_src)
        self.assertNotIn("Mew.any(axis=1)", prefix_src)
        # and it must still be valid Python, i.e. the reconstruction is a real pre-fix source and
        # not a mangling that would fail the assertions for the wrong reason
        ast.parse(prefix_src)


class Cause1PathAuditTests(unittest.TestCase):
    """Quarantine cause 1's CODE leg for the adopted 5D GBDT covariance (X).

    The criterion asks for *"a committed static audit naming every module X's build invokes, with the
    call site and the convention for each — not a claim that the sweep covered it"*. This is that
    audit, executable, so it re-runs instead of decaying.

    THE AUDIT FOUND A HOLE IN THIS FILE'S OWN CAUSE-1 GUARD, which is why it exists.
    `QuarantineCauseGuardTests` pins `uq_math.mat_covariance` — but `analyze_universes_5d` does NOT
    call it. It reimplements the same arithmetic inline (`Z = D - D.mean(axis=0, keepdims=True)`,
    `(Z.T @ Z) / D.shape[0]`), and that inlined site is what built X's sweep `C_syst`. So the
    existing guard would stay green while the convention on X's actual path changed. Pinned here.
    """

    # The four production entry points, per sbatch_finalize_5d_bkgaware_gpu.sh and
    # sbatch_readopt_5d_bkgaware_footing.sh: sweep -> block sum -> throw -> adopt.
    ENTRY = ["sweep_bank_5d", "analyze_universes_5d", "unified_throw_cov_5d", "adopt_unified_5d"]

    @classmethod
    def _local_modules(cls):
        return {p.stem for p in ND.glob("*.py")}

    @classmethod
    def _imports_of(cls, mod, local):
        f = ND / f"{mod}.py"
        if not f.exists():
            return set()
        out = set()
        for n in ast.walk(ast.parse(f.read_text())):
            if isinstance(n, ast.Import):
                out |= {a.name.split(".")[0] for a in n.names if a.name.split(".")[0] in local}
            elif isinstance(n, ast.ImportFrom) and n.module:
                if n.module.split(".")[0] in local:
                    out.add(n.module.split(".")[0])
        return out

    @classmethod
    def _reachable(cls):
        local = cls._local_modules()
        seen, stack = set(), list(cls.ENTRY)
        while stack:
            m = stack.pop()
            if m in seen:
                continue
            seen.add(m)
            stack.extend(cls._imports_of(m, local) - seen)
        return seen

    def test_no_pet_module_is_on_X_build_path(self):
        """The two one-sided sites the 2026-07-12 sweep found and did NOT fix are both `pet_*`.

        `pet_unified_throw_5d.py:108-111` and `pet_lateral_correction.py:118`. Cause 1's criterion
        requires them PROVEN off X's path rather than assumed, because if either were on it the C leg
        would be open and no amount of correct convention elsewhere would close it. They belong to the
        PET budget, i.e. cause 5.
        """
        seen = self._reachable()
        self.assertEqual(sorted(m for m in seen if m.startswith("pet")), [],
                         "a pet_* module became reachable from X's build; cause 1's C leg reopens")
        self.assertNotIn("pet_unified_throw_5d", seen)
        self.assertNotIn("pet_lateral_correction", seen)

    def test_unified_throw_is_not_on_X_build_path(self):
        """`unified_throw.do_combine:391` uses an UNBIASED 1/(N-1), not the MAT biased 1/N.

        It is a 3D legacy path (it reads `hXSec3D`) and nothing on X's build imports it -- the module
        appeared in a first draft of this audit only because I had SEEDED it as an entry point, which
        is a property of my seeding and not a measurement. Pinned so that if anything on X's path ever
        does import it, the differing normalization is caught rather than inherited.
        """
        seen = self._reachable()
        self.assertNotIn("unified_throw", seen)

    def test_analyze_universes_5d_band_covariance_is_mean_centered_and_biased(self):
        """The inlined `mat_covariance` that built X's sweep C_syst. NOT covered by the uq_math guard.

        Asserts the two properties that distinguish the corrected convention from cause 1's defect:
        centering on the universe MEAN (not the CV), and the MAT biased `1/N` (not `1/(N-1)`).
        """
        src = (ND / "analyze_universes_5d.py").read_text()
        self.assertIn("Z = D - D.mean(axis=0, keepdims=True)", src,
                      "band covariance must be UNIVERSE-MEAN centered; CV-centering is cause 1")
        self.assertIn("(Z.T @ Z) / D.shape[0]", src,
                      "MAT convention is the biased 1/N; 1/(N-1) is a different estimator")
        self.assertNotIn("(Z.T @ Z) / (D.shape[0] - 1)", src)

    def test_the_only_outer_product_on_X_path_is_the_documented_norm_band(self):
        """`np.outer` is cause 1's signature, so every occurrence on X's path must be accounted for.

        There is exactly one, and it is the target-nucleon normalization rank-1 add-on --
        `C^norm = (sigma_N X^CV)(sigma_N X^CV)^T` with sigma_N = 0.014, `app_statmethods.tex`
        eq:normband, applied via `--add-norm`. That is a legitimate rank-1 term, NOT a one-sided band.
        Any NEW outer product on this path is a cause-1 candidate and should fail here.
        """
        seen = self._reachable()
        found = []
        for mod in sorted(seen):
            f = ND / f"{mod}.py"
            if not f.exists():
                continue
            for i, line in enumerate(f.read_text().splitlines(), 1):
                if "np.outer(" in line:
                    found.append(f"{mod}.py:{i}")
        # PINNED ON CONTENT, NOT ON A LINE NUMBER -- changed 2026-08-18 and flagged for the owning
        # lane's review. This asserted `analyze_universes_5d.py:109` and went RED when a 15-line
        # comment was added ABOVE it in load_flat for B4: the outer product moved to :124 and nothing
        # about the audited property changed. That is BEN-249/BEN-480's subject arriving in a TEST,
        # which is the strongest form of it -- a test is a citation-bearing artifact and this one
        # asserted the citation rather than the fact.
        #
        # Bumping 109 to 124 would have been the quiet fix and it would rot again on the next edit
        # above it. So: still EXACTLY ONE occurrence on X's path, and it must be the documented
        # norm-band term, identified by what the line SAYS. The line number is reported, not asserted
        # -- "cite the line and quote it": the number locates, the content survives the edit.
        self.assertEqual(len(found), 1,
                         f"expected exactly ONE np.outer on X's build path, found {found} -- any NEW "
                         "outer product here is a cause-1 candidate")
        mod, _, lineno = found[0].rpartition(":")
        self.assertEqual(mod, "analyze_universes_5d.py", f"outer product moved module: {found}")
        src = (ND / mod).read_text().splitlines()
        line = src[int(lineno) - 1]
        self.assertIn("np.outer(", line)
        # SYMMETRIC rank-1: `np.outer(v, v)`. A one-sided band would be np.outer(a, b) with a != b,
        # which is cause 1's actual signature, so the symmetry is the property worth asserting.
        args_in = line.split("np.outer(", 1)[1].split(")", 1)[0]
        lhs, _, rhs = (x.strip() for x in args_in.partition(","))
        self.assertEqual(lhs, rhs,
                         f"{found[0]} is a NON-SYMMETRIC outer product ({args_in}) -- a one-sided "
                         "band is cause 1's signature, not the documented norm term")
        # ...and it is the --add-norm-gated norm band built from the CV, not some new term. Checked in
        # the three lines above it so this survives the block moving as a whole.
        context = "\n".join(src[max(0, int(lineno) - 4):int(lineno)])
        self.assertIn("add_norm", context,
                      f"{found[0]} is a symmetric outer product but is NOT gated on --add-norm; the "
                      f"documented term is (sigma_N X^CV)(sigma_N X^CV)^T. Context:\n{context}")
        self.assertIn("cv_rep", context,
                      f"{found[0]}'s vector is not built from the reported CV: {context!r}")

class Gate1TwoRoleSeedSplit(unittest.TestCase):
    """The gate-1 split of `--seed` into `--draw-seed` (throw realization) and
    `--estimator-seed` (the unfolding estimator).

    THE THIRD TEST IS THE ONLY ONE WHOSE EXPECTED RESULT THE DIFF CHANGES, so it is the only one
    that could be written to pass vacuously, and it carries a PRE-DIFF CONTROL: the same
    configuration is run against the module as it existed at HEAD~ and must FAIL there. Without
    that arm, a green result cannot distinguish the change from a no-op (BEN-181's shape).
    """

    def _fixture(self, tmp, *, est, draw, est2=None, draw2=None, legacy=None):
        """Write two throw slabs and one block slab. `legacy` writes the PRE-SPLIT single
        ambiguous `seed` key instead of the two role keys.

        flux_normalized IS stamped on every slab, deliberately: without it the J28 guard fires
        FIRST and any assertRaises below would pass without reaching the seed guards at all.
        """
        p = Path(tmp)
        throws = np.array([[0.8, 2.1], [1.2, 1.9], [1.1, 2.2]])
        def stamp(seed_est, seed_draw):
            if legacy is not None:
                return {"seed": np.int64(legacy)}
            return {"estimator_seed": np.int64(seed_est), "draw_seed": np.int64(seed_draw)}
        np.savez(p / "throws_0.npz", xs=throws[:2], throws=np.array([0, 1]),
                 flux_normalized=np.int64(1), **stamp(est, draw))
        np.savez(p / "throws_1.npz", xs=throws[2:], throws=np.array([2]),
                 flux_normalized=np.int64(1),
                 **stamp(est if est2 is None else est2, draw if draw2 is None else draw2))
        np.savez(p / "blocks.npz", xs=np.array([[0.9, 2.2], [1.1, 1.8]]),
                 labels=np.array(["MaCCQE:0", "MaCCQE:1"], dtype=object),
                 kinds=np.array(["knob", "knob"], dtype=object),
                 flux_normalized=np.int64(1), **stamp(est, draw))
        return str(p / "throws_*.npz"), str(p / "blocks.npz")

    @contextlib.contextmanager
    def _stubbed(self, module):
        d = {"edges": [np.array([0.0, 1.0, 2.0])],
             "w_truth": np.ones(1), "w_reco": np.ones(1), "td_w": np.ones(1)}
        old_load, old_kernel = module._load_bank, module._xsec_for_weights
        module._load_bank = lambda bank: (d, ["MaCCQE"], 0)
        module._xsec_for_weights = lambda *a, **k: np.array([1.0, 2.0])
        try:
            yield
        finally:
            module._load_bank, module._xsec_for_weights = old_load, old_kernel

    def _args(self, td, combine, blocks, *, est, draw):
        return SimpleNamespace(bank=td, iters=1, estimator_seed=est, draw_seed=draw,
                               combine=combine, block_slabs=blocks,
                               expected_throws="0-2", null=True, out_root=None)

    def test_legacy_single_seed_slab_is_REJECTED_and_the_message_names_the_migration(self):
        """Item 6, policy (a) STRICT. A pre-split slab carries only the ambiguous `seed` key.

        The rejected alternative was a fallback reading `seed` as the estimator seed, which
        would let a legacy slab combine beside a post-split one whose draw seed differs -- a
        silent mixed-estimator covariance, strictly worse than failing.
        """
        import unified_throw_cov as utc
        with tempfile.TemporaryDirectory() as td:
            combine, blocks = self._fixture(td, est=1000, draw=1000, legacy=1000)
            with self._stubbed(utc):
                with self.assertRaises(SystemExit) as cm:
                    utc.do_combine(self._args(td, combine, blocks, est=1000, draw=1000))
        msg = str(cm.exception)
        self.assertIn("estimator_seed", msg)
        self.assertIn("MIGRATION", msg,
                      "a strict rejection must tell the operator how to move forward")

    def test_two_draw_seeds_in_one_combine_are_REJECTED(self):
        """New guard. Distinct throw ids do NOT make two draw seeds one coherent ensemble."""
        import unified_throw_cov as utc
        with tempfile.TemporaryDirectory() as td:
            combine, blocks = self._fixture(td, est=1000, draw=1000, draw2=7)
            with self._stubbed(utc):
                with self.assertRaises(SystemExit) as cm:
                    utc.do_combine(self._args(td, combine, blocks, est=1000, draw=1000))
        self.assertIn("draw seed", str(cm.exception))

    def test_roles_may_DIFFER_post_split_and_the_pre_diff_module_cannot_express_it(self):
        """THE POWER TEST. estimator 1000 with draw 7 is the configuration M(ii) needs and the
        pre-split code could not express, because one integer drove both roles.

        ACCEPT arm: the split module combines it.
        PRE-DIFF CONTROL: the module at HEAD~ must NOT. Its slab reader keys on `seed`, which
        these slabs do not carry, so it fails closed -- and that failure is what proves the
        accept arm above is caused by this diff rather than true all along.
        """
        import unified_throw_cov as utc
        with tempfile.TemporaryDirectory() as td:
            combine, blocks = self._fixture(td, est=1000, draw=7)
            with self._stubbed(utc):
                out = utc.do_combine(self._args(td, combine, blocks, est=1000, draw=7))
            self.assertIsNotNone(out, "estimator 1000 / draw 7 must be ACCEPTED after the split")
            self.assertEqual(out["estimator_seed"], 1000)
            self.assertEqual(out["draw_seed"], 7, "the product must record BOTH roles (item 4)")

            # PINNED SHA, NOT `HEAD~`. This read `HEAD~` for exactly one commit, and it broke on
            # the next one: `HEAD~` became the gate-1 commit itself, so the "pre-diff" module
            # already had the split and the control failed. A relative ref is not a definition --
            # the same lesson as publishing a command without its ref, arriving inside a test
            # written to enforce it. 26e4e343 is the last commit before the split.
            prev = _import_module_at_rev("26e4e343", "nd-unfolding/unified_throw_cov.py",
                                         "unified_throw_cov_prediff")
            # FAIL, DO NOT SKIP. This was a skipTest for one commit, and lane Assistant named the
            # hole: in a shallow clone or a fresh CI checkout the pinned object may be absent, and
            # a skip is GREEN in exactly the environment where nobody is watching -- a check that
            # cannot fail, guarding the one test whose expected result this diff changes. Verified
            # here in a checkout that HAS the object, which is why the branch needed naming rather
            # than testing. Same move as widening the assertion below: make the control's own
            # failure mode loud.
            if prev is None:
                self.fail("pre-diff revision 26e4e343 could not be loaded (shallow clone? run "
                          "`git fetch --unshallow`). The control arm did NOT run, so the accept "
                          "arm above is UNCONTROLLED and this test proves nothing about the diff.")
            # THE CONTROL'S FAILURE MODE IS ITSELF INFORMATIVE, so it is asserted as a union
            # rather than narrowed to SystemExit. Measured: the pre-diff module raises
            # AttributeError at its `args.seed` read -- it cannot even be CALLED with split-role
            # arguments, which is a stronger statement than "its guard rejects them". Narrowing
            # this to SystemExit would have made the control fail for the right reason and be
            # RECORDED as a broken test.
            with self._stubbed(prev):
                with self.assertRaises((SystemExit, AttributeError, TypeError),
                                       msg="PRE-DIFF module accepted a split-role combine; the "
                                           "accept arm above is then not evidence about this diff"):
                    prev.do_combine(self._args(td, combine, blocks, est=1000, draw=7))


def _import_module_at_rev(rev, path, name):
    """Import `path` as it existed at `rev`, or None if git cannot produce it."""
    import importlib.util
    import subprocess
    root = Path(__file__).resolve().parent.parent.parent
    try:
        src = subprocess.run(["git", "-C", str(root), "show", f"{rev}:{path}"],
                             capture_output=True, text=True, check=True).stdout
    except Exception:
        return None
    if not src:
        return None
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(src)
        tmp = fh.name
    spec = importlib.util.spec_from_file_location(name, tmp)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    return mod


class _RootRecorder:
    """Minimal ROOT stub that RECORDS what a writer wrote.

    Manufactured rather than mocked-away: ROOT is not installed on every checkout, so the only way
    to test that a value reaches the FILE is to stand in for the file. Records TParameter names and
    values, TH1/TH2 names, and per-bin contents of the mask.
    """

    def __init__(self):
        self.params = {}
        self.hists = {}        # BUILT: populated by SetBinContent. Not evidence of a write.
        self.written = set()   # REACHED THE FILE: populated ONLY by Write().
        self.closed = False

    class _Obj:
        """WRITTEN AND BUILT ARE SEPARATE, and lane D's finding 3 is why.

        The first version recorded the histogram's name in `hists` from `SetBinContent`, so a
        populated-but-never-written object was indistinguishable from a written one: deleting
        `hmask.Write()` left the suite GREEN. That is `BEN-450` -- an object constructed,
        populated, and not propagated -- reproduced inside the test written to detect `BEN-450`,
        with the instrument blind to the very distinction it exists to make.

        Only the zero-case test caught it, and by luck: with an empty index set the loop never
        runs, so the key could only appear via `Write()`. Assertions now bind to `written`.
        """
        def __init__(self, rec, name):
            self._rec, self._name = rec, name
        def SetBinContent(self, *a):
            self._rec.hists.setdefault(self._name, {})[tuple(a[:-1])] = a[-1]
        def Write(self):
            self._rec.written.add(self._name)
            self._rec.hists.setdefault(self._name, {})

    class _Param:
        def __init__(self, rec, name, value):
            self._rec, self._name, self._value = rec, name, value
        def Write(self):
            self._rec.written.add(self._name)
            self._rec.params[self._name] = self._value

    def TFile(self):  # pragma: no cover - shape only
        raise AssertionError("use TFile.Open")

    def TParameter(self, _type):
        return lambda name, value: _RootRecorder._Param(self, name, value)

    def TH2D(self, name, *a):
        return _RootRecorder._Obj(self, name)

    def TH1I(self, name, *a):
        return _RootRecorder._Obj(self, name)

    def TH1D(self, name, *a):
        return _RootRecorder._Obj(self, name)


class _StubbedRoot:
    """Install a recorder as `ROOT` for the duration of a with-block."""

    def __init__(self):
        self.rec = _RootRecorder()

    def __enter__(self):
        import sys, types
        mod = types.ModuleType("ROOT")
        mod.TParameter = self.rec.TParameter
        mod.TH2D = self.rec.TH2D
        mod.TH1I = self.rec.TH1I
        mod.TH1D = self.rec.TH1D
        opened = types.SimpleNamespace(Close=lambda: setattr(self.rec, "closed", True))
        mod.TFile = types.SimpleNamespace(Open=lambda *a, **k: opened)
        self._saved = sys.modules.get("ROOT")
        sys.modules["ROOT"] = mod
        return self.rec

    def __exit__(self, *exc):
        import sys
        if self._saved is None:
            sys.modules.pop("ROOT", None)
        else:
            sys.modules["ROOT"] = self._saved
        return False


class Cause6CoverageGuardPropagates(unittest.TestCase):
    """`BEN-450`: the guard DETECTED and did not PROPAGATE.

    The pre-existing test was STATIC -- it asserted the empty-row set was computed and two strings
    were present -- and lane D's observation is that deleting both `print`s leaves it green. So
    these tests bind to the value reaching the FILE, and the last one is the MUTATION CONTROL that
    proves they can fail.
    """

    def _call(self, empty_rows, n=4):
        import eavailW_covariance as ew
        mats = [(nm, np.zeros((n, n))) for nm in ("C_syst", "C_stat", "C_lateral", "C_total")]
        data = (2, 2, np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 2.0]), np.zeros((2, 2)))
        idx = np.asarray(empty_rows, dtype=int)
        with tempfile.TemporaryDirectory() as td:
            out = str(Path(td) / "sub" / "out.root")   # `sub` exercises the makedirs branch
            with _StubbedRoot() as rec:
                got = ew.write_ew_outputs(out, mats, n, data, (idx, int(idx.size)))
        return rec, got

    def test_the_helper_is_the_single_source_of_the_value(self):
        import eavailW_covariance as ew
        Mew = np.zeros((3, 2))
        Mew[0, 0] = 1.0
        idx, count = ew.ew_coverage_report(Mew)
        np.testing.assert_array_equal(idx, [1, 2])
        self.assertEqual(count, 2)
        self.assertIsInstance(count, int, "the count must be a plain int to survive a ROOT write")

    def test_count_AND_set_reach_the_file(self):
        rec, got = self._call([1, 3], n=4)
        self.assertEqual(got, 2)
        self.assertIn("n_ew_unsupported", rec.written, "the count did not reach the artifact")
        self.assertEqual(rec.params["n_ew_unsupported"], 2)
        self.assertIn("hEwUnsupportedMask", rec.written,
                      "the SET was BUILT but never WRITTEN -- assert on `written`, not `hists`")
        mask = rec.hists["hEwUnsupportedMask"]
        self.assertEqual({k[0] for k in mask}, {2, 4},
                         "mask must be 1-indexed and index-aligned to the covariance rows")

    def test_count_is_written_WHEN_ZERO(self):
        """The half most likely to be dropped as pedantry, and the repo has paid for it once.

        A build that skips the write on zero is indistinguishable from one that never checked, and
        a downstream criterion phrased as "the unsupported count is not large" passes vacuously.
        Same argument as `unified_throw_cov.py`'s `fixed_seed_null_checked`, same quarantine.
        """
        rec, got = self._call([], n=4)
        self.assertEqual(got, 0)
        self.assertIn("n_ew_unsupported", rec.written,
                      "ZERO must still be written -- absence is indistinguishable from unchecked")
        self.assertEqual(rec.params["n_ew_unsupported"], 0)
        self.assertNotIn("ew_coverage_checked", rec.params,
                         "dropped on D's finding 1: a literal-1 flag on the only path cannot fail "
                         "in the direction it claims. n_ew_unsupported IS the checked flag -- its "
                         "ABSENCE means the product predates the check, 0 means fully supported")
        self.assertIn("hEwUnsupportedMask", rec.written,
                      "the mask is written even when empty, for the same reason as the count")

    # EVERY propagating write gets its own mutant, on lane D's finding 2: the first version
    # mutated only the COUNT, so the SET test was assumed rather than controlled -- and the set is
    # the half a downstream chi2 needs, since the count says there IS a problem and the mask says
    # which bins to drop. `(needle, key)` pairs; each mutant must lose exactly its own key.
    PROPAGATION_WRITES = [
        ('ROOT.TParameter("int")("n_ew_unsupported", count).Write()', "n_ew_unsupported"),
        ("hmask.Write()", "hEwUnsupportedMask"),
    ]

    def test_MUTATION_removing_ANY_propagating_write_is_detected(self):
        """POSITIVE CONTROL, one mutant per propagating write.

        Without it the tests above could be passing on a property they do not constrain -- which is
        exactly `BEN-450`'s criticism of the static test they replace: a positive control on a
        static test controls only the static property. The `hmask.Write()` mutant is the one that
        matters: until the recorder separated WRITTEN from BUILT, deleting that line left the suite
        green because `SetBinContent` had already created the key.
        """
        src = (ND / "eavailW_covariance.py").read_text()
        mats = [(nm, np.zeros((4, 4))) for nm in ("C_syst",)]
        data = (2, 2, np.array([0.0, 1.0, 2.0]), np.array([0.0, 1.0, 2.0]), np.zeros((2, 2)))
        for needle, key in self.PROPAGATION_WRITES:
            with self.subTest(write=key):
                self.assertIn(needle, src,
                              f"the write propagating {key} is not where the mutation expects it")
                mutant_src = src.replace(needle, "pass  # MUTATED: propagation removed")
                self.assertNotEqual(mutant_src, src, "the mutation changed nothing")
                ns = {"__name__": "eavailW_mutant"}
                exec(compile(mutant_src, "eavailW_mutant.py", "exec"), ns)
                with tempfile.TemporaryDirectory() as td:
                    out = str(Path(td) / "sub" / "out.root")
                    with _StubbedRoot() as rec:
                        ns["write_ew_outputs"](out, mats, 4, data,
                                               (np.array([1], dtype=int), 1))
                self.assertNotIn(key, rec.written,
                                 f"the mutant still propagated {key}, so this control is VOID")


class SeedOffsetGridAliasing(unittest.TestCase):
    """Spec (B) option (ii): the offset grid must not alias two ensemble members onto one seed.

    THE MEASURED BASELINES, 2026-08-18: group 1 = {sweep_bank_5d, bootstrap_nd, seedscan_split} at
    42, group 2 = {unified_throw_cov} at 1000. An offset preserves the grouping; it can still make
    one group at offset k share a seed with the other group at a DIFFERENT offset k'.
    """

    B = {"g1": 42, "g2": 1000}

    def test_the_single_value_form_is_UNDER_INCLUSIVE_and_the_pairwise_form_catches_what_it_misses(self):
        """THE CONTROL THAT JUSTIFIES THE MODULE. Without it, "we check the grid" is unfalsifiable.

        `assert k not in (958, -958)` is only the special case k'=0 -- the baseline member. This
        grid aliases TWICE and that form flags one of them, so it would ship the second silently:
        a guard that certifies a grid it has not checked, which is worse than no guard.
        """
        import seed_offset_policy as sp
        grid = [0, 100, 500, 958, 1058, 1500]
        bad = sp.check_offset_grid(self.B, grid)
        pairs = {(ka, kb) for _, ka, _, kb, _ in bad}
        self.assertEqual(pairs, {(958, 0), (1058, 100)},
                         "the pairwise form must catch BOTH, including the pair with neither "
                         "offset in {+-958}")

        naive_flagged = {k for k in grid if k in (958, -958)}
        self.assertEqual(naive_flagged, {958},
                         "the single-value form flags only the baseline-relative collision")
        survivors = {(ka, kb) for ka, kb in pairs if ka not in naive_flagged}
        self.assertEqual(survivors, {(1058, 100)},
                         "and this aliasing pair SURVIVES the single-value form -- the exact "
                         "failure the pairwise check exists to prevent")

    def test_a_clean_grid_passes_so_the_guard_is_not_vacuous(self):
        import seed_offset_policy as sp
        self.assertEqual(sp.check_offset_grid(self.B, [0, 1, 2, 5, 10]), [])
        self.assertTrue(sp.assert_offset_grid_is_alias_free(self.B, [0, 1, 2, 5, 10]))

    def test_a_single_group_can_never_alias(self):
        """One baseline means no distinct-group pair, so no k/k' can collide across groups."""
        import seed_offset_policy as sp
        self.assertEqual(sp.check_offset_grid({"only": 42}, [0, 958, -958, 1058]), [])

    def test_the_assertion_FAILS_CLOSED_and_its_message_names_ALIASING_not_structure(self):
        """The message matters as much as the raise: the first description of this defect said the
        co-variation STRUCTURE was destroyed, which is false -- at k=958 the within-run structure is
        intact (42+958=1000, 1000+958=1958, distinct). What collides is g1@958 with g2@0. A wrong
        message sends the next reader after the wrong bug.
        """
        import seed_offset_policy as sp
        with self.assertRaises(SystemExit) as cm:
            sp.assert_offset_grid_is_alias_free(self.B, [0, 958])
        msg = str(cm.exception)
        self.assertIn("ALIASES", msg)
        self.assertIn("SAME estimator seed", msg)
        self.assertNotIn("destroy", msg.lower(),
                         "the failure is aliasing between grid points, not destruction of the "
                         "within-run co-variation structure")
        self.assertIn("PAIRWISE", msg, "the message must say why a single-value exclusion is not enough")

    def test_the_docstring_cites_the_UNMEASURED_premise_rather_than_asserting_a_fact(self):
        """The whole constraint is necessary only IF a shared seed across legs produces correlated
        noise, which lane C recorded CONSIDERED-AND-DECLINED and UNMEASURED. Imposing the policy
        anyway is conservative; presenting it as structural would be a claim the campaign has
        explicitly declined to make. Pinned so the caveat cannot be quietly dropped.
        """
        import seed_offset_policy as sp
        doc = sp.__doc__ or ""
        self.assertIn("UNMEASURED", doc)
        self.assertIn("CONSIDERED-AND-DECLINED", doc)
        self.assertIn("decorrelate", doc)


class MiiFourLegDriver(unittest.TestCase):
    """The four-leg offset-scan driver: the five dispatch requirements, each with its mutation."""

    def _drv(self):
        import mii_seed_offset_driver as d
        return d

    def test_R3_one_offset_fans_across_all_FIVE_legs_preserving_BOTH_groups(self):
        """INTEGRATION is the deliverable. A flag is capability; a launcher diff is not a launcher.

        WAS `..._all_four_legs`. Renamed rather than patched, so the reversal is visible: lane C's
        determination (item 7 ruling (a)) put the LATERAL leg in g1 at 42+k, making it FIVE legs
        across SEVEN launchers. The old name encoded a superseded declaration, and a fixture that
        keeps a stale count while its assertion is loosened is how a test stops describing the system.
        """
        d = self._drv()
        # argv_probe=False: the observed-argv GATE is cluster-only (the launchers hardcode a cluster
        # REPO and source a cluster env activator). These assertions are PLAN-LEVEL only -- they say
        # nothing about whether the offset reaches a seed or an output path in any branch, and the
        # gate that answers that runs via --cluster-probe. Stated so the pass is not over-read.
        plan = d.build_plan([0, 1200], argv_probe=False)
        legs = {m["leg"] for m in plan["members"]}
        self.assertEqual(legs, {"sweep_bank_5d", "unified_throw_cov", "bootstrap_nd",
                                "seedscan_split", "unfold_nd_omnifold_unbinned"},
                         "a scan must reach all FIVE legs -- the lateral joined g1 under item 7(a)")
        for k in (0, 1200):
            seeds = {m["leg"]: m["estimator_seed"] for m in plan["members"] if m["k"] == k}
            self.assertEqual(seeds["sweep_bank_5d"], 42 + k)
            self.assertEqual(seeds["bootstrap_nd"], 42 + k)
            self.assertEqual(seeds["seedscan_split"], 42 + k)
            self.assertEqual(seeds["unfold_nd_omnifold_unbinned"], 42 + k,
                             "the lateral leg moves with g1, which is what item 7(a) ruled")
            self.assertEqual(seeds["unified_throw_cov"], 1000 + k)
            # the whole point of (ii): g1 stays internally equal and stays unequal to g2
            self.assertEqual(len({seeds["sweep_bank_5d"], seeds["bootstrap_nd"],
                                  seeds["seedscan_split"],
                                  seeds["unfold_nd_omnifold_unbinned"]}), 1,
                             "group g1 must remain coherent -- INCLUDING the lateral, which is the "
                             "whole point of item 7(a): holding laterals at 42 while verticals move "
                             "is the condition unified_throw_cov.py's F2 guard fails closed on")
            self.assertNotEqual(seeds["sweep_bank_5d"], seeds["unified_throw_cov"],
                                "g1 and g2 must remain independent")

    def test_R5_the_draw_seed_does_NOT_move_with_k(self):
        """LANE D's MUTATION, run here so it is not only a review step.

        Passing 1000+k to both flags is the natural implementation and gives every member a
        different THROW ENSEMBLE -- estimator noise convolved with ensemble noise, which the combine
        guard cannot catch because every member runs its own combine and 1000/1000 and 1005/1005
        both pass. Per-member coherence is not ensemble coherence.
        """
        d = self._drv()
        # NOT [0, 5, 958]: that ALIASES (958 - 0 is exactly b2 - b1). And not [0, 5, 10] either:
        # the clean-offset predicate now forbids 5 and 10 (42+5 and 42+10 land in the bootstrap
        # replica range). The fixture tripped BOTH guards in turn, which is both guards working.
        # argv_probe=False: the observed-argv GATE is cluster-only (the launchers hardcode a cluster
        # REPO and source a cluster env activator). These assertions are PLAN-LEVEL only -- they say
        # nothing about whether the offset reaches a seed or an output path in any branch, and the
        # gate that answers that runs via --cluster-probe. Stated so the pass is not over-read.
        plan = d.build_plan([0, 1200, 2400], argv_probe=False)
        draws = {m["draw_seed"] for m in plan["members"] if m["leg"] == "unified_throw_cov"}
        self.assertEqual(draws, {1000}, "the draw seed moved with k -- the scan would measure "
                                        "estimator noise convolved with ensemble noise")

    def test_R5_MUTATION_parameterising_the_draw_seed_is_REJECTED(self):
        import seed_offset_policy as sp
        with self.assertRaises(SystemExit) as cm:
            sp.assert_draw_seed_is_pinned({"x.sh": "python3 f.py --draw-seed ${EST_SEED}"})
        self.assertIn("Per-member coherence is not ensemble coherence", str(cm.exception))

    def test_R4_k0_control_is_TWO_SIDED(self):
        """Mutate the LAUNCHER side and the ARCHIVE side; both must fail.

        A reproduction check that only notices changes on one side is comparing a value against
        itself -- `BEN-423`, which caught three lanes today.
        """
        d = self._drv()
        import seed_offset_policy as sp
        src = d.launcher_sources()
        self.assertTrue(d.assert_k0_reproduces_the_archive(src))

        mutated = dict(src)
        k = "sbatch_sweep_bank_5d_run_bkgaware_gpu.sh"
        mutated[k] = mutated[k].replace("EST_SEED=$(( 42 +", "EST_SEED=$(( 43 +")
        self.assertNotEqual(mutated[k], src[k], "launcher-side mutation changed nothing")
        with self.assertRaises(SystemExit):
            d.assert_k0_reproduces_the_archive(mutated)

        saved = sp.LEG_BASELINES["sweep_bank_5d"]
        sp.LEG_BASELINES["sweep_bank_5d"] = ("g1", 43)
        try:
            with self.assertRaises(SystemExit, msg="ARCHIVE-side mutation was not detected: the "
                                                   "control is comparing a value against itself"):
                d.assert_k0_reproduces_the_archive(src)
        finally:
            sp.LEG_BASELINES["sweep_bank_5d"] = saved

    def test_R1_an_aliasing_grid_is_REJECTED_and_a_one_member_grid_cannot_pass_vacuously(self):
        d = self._drv()
        with self.assertRaises(SystemExit) as cm:
            d.build_plan([0, 958], argv_probe=False)
        self.assertIn("ALIASES", str(cm.exception))
        import seed_offset_policy as sp
        with self.assertRaises(SystemExit) as cm2:
            sp.assert_offset_grid_is_alias_free({"only": 42}, [0, 1, 2])
        self.assertIn("ZERO pairs", str(cm2.exception))

    def test_MUTATION_removing_the_offset_hook_from_a_launcher_is_REJECTED(self):
        """Without this the driver exports a variable nothing reads, every member runs at baseline,
        and the scan returns a null produced by the plumbing rather than by the physics."""
        d = self._drv()
        src = dict(d.launcher_sources())
        k = "sbatch_bootstrap_5d_gpu.sh"
        src[k] = src[k].replace("MNV_EST_SEED_OFFSET", "MNV_DISABLED")
        with self.assertRaises(SystemExit) as cm:
            d.assert_offset_hook_present(src)
        self.assertIn("would run at baseline for every k", str(cm.exception))

    def test_the_driver_HAS_NO_SUBMISSION_PATH(self):
        """Asserted on the source, because the dispatch said do not submit and a review of intent is
        weaker than a check of the file."""
        import ast as _ast
        src = (ND / "mii_seed_offset_driver.py").read_text()
        tree = _ast.parse(src)
        called = {n.func.attr for n in _ast.walk(tree)
                  if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)}
        for forbidden in ("run", "check_call", "check_output", "Popen", "system", "spawn"):
            self.assertNotIn(forbidden, called, f"driver may call no process-spawning API: {forbidden}")
        self.assertNotIn("import subprocess", src)
        self.assertFalse(any(m.get("submitted") for m in [d for d in []]), "sanity")


class LauncherArgvProbe(unittest.TestCase):
    """The probe that reads the USE, not the assignment. It found two live defects in my own hook
    insertions after three text/assignment-level checks had passed on both."""

    def _reinsert_into_then_branch(self, text):
        L = text.split("\n")
        ai = next(i for i, l in enumerate(L) if l.strip().startswith("EST_SEED=$(("))
        assign = L.pop(ai)
        ii = next(i for i, l in enumerate(L) if l.strip().startswith("if [[") and '"$T" -eq 0' in l)
        L.insert(ii + 1, assign)          # column 0 INSIDE the then block: the original bug
        return "\n".join(L)

    LOCAL_HARNESS_NOTE = (
        "CLUSTER-ONLY. These two tests exercise the `_prepare`-based LOCAL harness, which cannot "
        "execute these launchers: they hardcode a cluster REPO and source a cluster env activator. "
        "Six successive attempts to make the transformation work each MOVED the failure, which is why "
        "native mode deletes the transformation instead. The DETECTION they assert -- a nested "
        "assignment or a continuation-swallowed argument shows up as a missing/absent seed value -- is "
        "exactly what --cluster-probe checks. WHAT SUBSTITUTES FOR THESE TWO, so a reader who finds a "
        "skip can trace it to its replacement instead of assuming nothing covers it: "
        "`python3 mii_seed_offset_driver.py --gate-only <TREE>` (exit 0, all four intercepted commands "
        "still shell functions after the env activation) followed by "
        "`python3 mii_seed_offset_driver.py --offsets 1200 --cluster-probe <TREE>`, run on the cluster "
        "at sha bd578ac4: exit 0, 16 START / 16 DONE, 14 observations, seeds 1242 on all four g1 legs "
        "and 2200 on all three g2 legs, every output path member-namespaced, stub_fired=True on all 14 "
        "executing cases. A SKIP NOBODY CAN TRACE TO ITS REPLACEMENT DECAYS INTO 'we turned that off'. "
        "Skipped rather than deleted because these two are the only record that the local path was "
        "tried and why it was abandoned, and a skip with a reason is falsifiable where a deletion is "
        "not. Set MNV_ARGV_PROBE_LOCAL=1 to run them anyway and watch the local harness fail."
    )

    def _skip_if_local(self):
        if not os.environ.get("MNV_ARGV_PROBE_LOCAL"):
            self.skipTest(self.LOCAL_HARNESS_NOTE)

    def test_it_catches_an_assignment_NESTED_IN_A_BRANCH(self):
        """`sbatch_uthrow_block_5d.sh`'s real defect: the else branch expanded ${EST_SEED} to nothing
        and every T != 0 task died. INDENTATION IS NOT SCOPE -- column 0 inside an indented block is
        legal bash and reads as top level, which is why an indentation-based heuristic cleared it."""
        self._skip_if_local()
        import launcher_argv_probe as probe
        f = "sbatch_uthrow_block_5d.sh"
        orig = (ND / f).read_text()
        (ND / f).write_text(self._reinsert_into_then_branch(orig))
        try:
            rows = probe.observed_argv(f, {"SLURM_ARRAY_TASK_ID": 3, "MNV_EST_SEED_OFFSET": 5})
            self.assertEqual(probe.flag_values(rows, "--estimator-seed"), ["<MISSING>"],
                             "the probe must SEE the value vanish, not merely fail to find the flag")
            with self.assertRaises(SystemExit):
                probe.assert_estimator_seed_is_an_integer_in_every_branch(
                    f, [{"SLURM_ARRAY_TASK_ID": 0, "MNV_EST_SEED_OFFSET": 5},
                        {"SLURM_ARRAY_TASK_ID": 3, "MNV_EST_SEED_OFFSET": 5}])
        finally:
            (ND / f).write_text(orig)
        # and the restored file passes, so the test is not asserting a permanent failure
        probe.assert_estimator_seed_is_an_integer_in_every_branch(
            f, [{"SLURM_ARRAY_TASK_ID": 0, "MNV_EST_SEED_OFFSET": 5},
                {"SLURM_ARRAY_TASK_ID": 3, "MNV_EST_SEED_OFFSET": 5}])

    def test_it_catches_an_assignment_INSIDE_A_CONTINUED_COMMAND(self):
        r"""`sbatch_bootstrap_5d_gpu.sh`'s real defect, and the worse of the two: the hook landed
        between a `\`-continued command's first line and its continuation, so bash swallowed the
        continuation as a comment. The command truncated to `bootstrap_nd.py --npz of_inputs_5d.npz`
        -- NO seed arguments at all -- and `bash -n` PASSED on it. Syntax valid, arguments destroyed.
        """
        self._skip_if_local()
        import launcher_argv_probe as probe
        f = "sbatch_bootstrap_5d_gpu.sh"
        orig = (ND / f).read_text()
        L = orig.split("\n")
        ai = next(i for i, l in enumerate(L) if l.strip().startswith("EST_SEED=$(("))
        assign = L.pop(ai)
        ri = next(i for i, l in enumerate(L)
                  if l.strip().startswith("rg_run") and "bootstrap_nd.py" in l)
        L.insert(ri + 1, assign)          # between the command and its continuation
        (ND / f).write_text("\n".join(L))
        try:
            rows = probe.observed_argv(f, {"SLURM_ARRAY_TASK_ID": 9, "MNV_EST_SEED_OFFSET": 5})
            vals = probe.flag_values(rows, "--estimator-seed")
            self.assertEqual(vals, [], "the flag should have been swallowed entirely")
            with self.assertRaises(SystemExit):
                probe.assert_estimator_seed_is_an_integer_in_every_branch(
                    f, [{"SLURM_ARRAY_TASK_ID": 9, "MNV_EST_SEED_OFFSET": 5}])
        finally:
            (ND / f).write_text(orig)

    def test_the_probe_refuses_to_run_with_fewer_cases_than_branches(self):
        import launcher_argv_probe as probe
        with self.assertRaises(SystemExit) as cm:
            probe.assert_estimator_seed_is_an_integer_in_every_branch(
                "sbatch_uthrow_block_5d.sh", [{"SLURM_ARRAY_TASK_ID": 0}])
        self.assertIn("has not checked the launcher", str(cm.exception))


class OffsetProvenanceStamp(unittest.TestCase):
    """The offset itself is stamped, not just the resulting seed -- lane D's point that an unhooked
    leg stamps its baseline and is then indistinguishable from a deliberate k=0 anchor member."""

    def test_declared_and_value_are_two_keys_not_a_sentinel(self):
        import seed_offset_policy as sp
        self.assertEqual(sp.declared_offset({}), (0, 0),
                         "unset must be DECLARED=0: nothing can be concluded about the member")
        self.assertEqual(sp.declared_offset({"MNV_EST_SEED_OFFSET": "0"}), (1, 0),
                         "a deliberate anchor member is declared=1, value=0 -- distinguishable from "
                         "an unhooked run, which is the whole point")
        self.assertEqual(sp.declared_offset({"MNV_EST_SEED_OFFSET": "5"}), (1, 5))

    def test_a_malformed_offset_FAILS_rather_than_being_recorded_as_provenance(self):
        import seed_offset_policy as sp
        with self.assertRaises(SystemExit):
            sp.declared_offset({"MNV_EST_SEED_OFFSET": "nope"})

    def test_all_four_legs_stamp_both_keys(self):
        """Asserted on the source of each writer, because the alternative is a run whose provenance
        cannot be reconstructed -- cheap now and impossible after the spend."""
        for mod in ("unified_throw_cov.py", "bootstrap_nd.py", "seedscan_split.py", "sweep_bank_5d.py"):
            src = (ND / mod).read_text()
            with self.subTest(module=mod):
                self.assertIn("est_seed_offset_declared", src)
                self.assertIn("est_seed_offset", src)

    def test_archive_expansion_FAILS_when_a_leg_cannot_be_parsed(self):
        """Attack #2: the parse is by string, so an unmatched leg was silently ABSENT from the result
        and the k=0 control would pass over a leg it never read."""
        import mii_seed_offset_driver as d
        src = dict(d.launcher_sources())
        k = "sbatch_seedscan_split_5d.sh"
        src[k] = src[k].replace("EST_SEED=$((", "EST_SEED=$(( ")   # still bash-valid, no longer matched
        src[k] = src[k].replace("EST_SEED=$(( ", "ESTSEED=$(( ")
        with self.assertRaises(SystemExit) as cm:
            d.archive_expansion(src)
        self.assertIn("silently", str(cm.exception))


class CleanOffsetPredicate(unittest.TestCase):
    """Lane C's constraint: an offset must not slide a leg's ESTIMATOR seed into the range of that
    leg's own per-unit DRAW seeds. A DIFFERENT confound from pairwise aliasing, and both are needed."""

    def test_the_measured_forbidden_set_reproduces(self):
        import seed_offset_policy as sp
        bad = sp.forbidden_offsets(-200, 1400)
        self.assertEqual(len(bad), 361, "361 forbidden offsets in [-200,1400]")
        self.assertEqual((min(bad), max(bad)), (-41, 1117))
        self.assertEqual(next(k for k in range(1, 4000) if k not in bad), 160,
                         "smallest strictly positive clean offset")

    def test_a_remembered_threshold_would_be_wrong(self):
        """`1000` and `997` both FAIL -- 42+1000 and 42+997 are inside [1000,1159] -- which is why the
        predicate is derived from the ranges rather than from a number anyone remembers."""
        import seed_offset_policy as sp
        # k=0 removed: it is the ARCHIVE's own coincidence and is exempt by allowlist (BEN-463).
        # Its arithmetic is unchanged and is asserted in the allowlist tests instead.
        for k in (5, 159, 958, 997, 1000):
            with self.subTest(k=k), self.assertRaises(SystemExit):
                sp.assert_offsets_are_clean([k])
        self.assertTrue(sp.assert_offsets_are_clean([160, 1200, 2400]))

    def test_j0_IS_the_archive_and_is_exempt_by_ALLOWLIST_not_by_a_member_skip(self):
        """WAS `test_Cs_grid_1200j_is_DIRTY_AT_j0`, and it encoded the PRE-RULING behaviour.

        The predicate did reject `j = 0`, for two reasons that are properties of the ARCHIVE:
        `g1`'s estimator seed 42 lands in the bootstrap replica seeds and `g2`'s 1000 lands in the
        per-throw draw seeds. Lane C's determination (`BEN-463`) is that this is not a defect to
        route around: A CLEAN ANCHOR IS NOT AN ANCHOR. The anchor's function is reproducing the
        published product, the published product HAS the coincidences, so the confound and the
        anchoring are the same fact -- and dropping `j = 0` costs not a member but the ANCHOR,
        leaving 49 members tied to no published value.

        Rewritten rather than deleted so the reversal is visible: the earlier assertion was correct
        about the arithmetic and wrong about the disposition, and the disposition was a ruling.
        """
        import seed_offset_policy as sp
        self.assertEqual(sp.assert_offsets_are_clean([1200 * j for j in range(50)]), 300,
                         "the ruled grid, anchor included, must now pass")
        # the arithmetic the earlier test asserted is still true -- it is the DISPOSITION that moved
        raw = sp.forbidden_offsets(-200, 1400)
        self.assertIn(0, raw, "k=0 still HAS the coincidences; it is exempt, not clean")
        self.assertEqual(len(raw[0]), 2, "both archive coincidences, not one")

    def test_the_range_table_is_DATA_and_names_what_it_omits(self):
        """Lane C reports a PET-family band making k=2000 dirty. This lane has not measured it, so it
        is ABSENT rather than guessed -- and the predicate must be computed from the table so that
        adding it is a data change, not a rewrite."""
        import seed_offset_policy as sp
        self.assertIn("uthrow per-throw draw seed", sp.PER_UNIT_SEED_RANGES)
        src = (ND / "seed_offset_policy.py").read_text()
        self.assertIn("PET-family band", src.replace("PET family band", "PET-family band"))
        # a caller-supplied range table must change the answer, or the table is decorative
        extra = dict(sp.PER_UNIT_SEED_RANGES, **{"hypothetical band": (2042, 2100)})
        with self.assertRaises(SystemExit):
            sp.assert_offsets_are_clean([2000], ranges=extra)

    def test_it_refuses_a_vacuous_pass(self):
        import seed_offset_policy as sp
        with self.assertRaises(SystemExit):
            sp.assert_offsets_are_clean([])
        with self.assertRaises(SystemExit):
            sp.assert_offsets_are_clean([1200], ranges={})


class CoincidenceAllowlist(unittest.TestCase):
    """`BEN-463`: the archive's own coincidences are exempt, expressed as an ALLOWLIST rather than a
    member skip -- because a skip passes ANY coincidence at the anchor, including a third one a later
    `--array` widening introduces, and the anchor is the member everyone has agreed is special."""

    def test_the_ruled_grid_is_accepted(self):
        import seed_offset_policy as sp
        self.assertEqual(sp.assert_offsets_are_clean([1200 * j for j in range(50)]), 300)

    def test_A_THIRD_COINCIDENCE_AT_THE_ANCHOR_STILL_FAILS(self):
        """THE NARROWING'S OWN TEST, and the reason the allowlist form was worth wiring. Without it,
        widening the exemption later looks free."""
        import seed_offset_policy as sp
        widened = dict(sp.PER_UNIT_SEED_RANGES, **{"hypothetical widened array": (40, 44)})
        with self.assertRaises(SystemExit) as cm:
            sp.assert_offsets_are_clean([0], ranges=widened)
        self.assertIn("hypothetical widened array", str(cm.exception))

    def test_the_exemption_does_not_leak_to_other_offsets_or_other_groups(self):
        """Keyed on `(group, range, SEED)`, a strengthening of the two-entry form: on `(group, range)`
        alone the exemption would also excuse k=5's bootstrap coincidence, same group same range. And
        k=958 puts g1's seed at 1000 -- the archive's coincidence is g2's at 1000, not g1's."""
        import seed_offset_policy as sp
        for k in (5, 47, 158, 958, 997, 1000):
            with self.subTest(k=k), self.assertRaises(SystemExit):
                sp.assert_offsets_are_clean([k])
        hits = sp.unexempted_coincidences([958])
        self.assertTrue(any("g1 estimator seed 1000" in r for r in hits[958]),
                        "g1 at 1000 must NOT inherit g2's exemption")

    def test_the_allowlist_has_exactly_the_two_archive_entries(self):
        import seed_offset_policy as sp
        self.assertEqual(sp.COINCIDENCE_ALLOWLIST,
                         {("g2", "uthrow per-throw draw seed", 1000),
                          ("g1", "bootstrap replica seed", 42)})

    def test_the_driver_now_enforces_it(self):
        import mii_seed_offset_driver as d
        plan = d.build_plan([1200 * j for j in range(1, 4)], argv_probe=False)
        self.assertGreater(plan["clean_offset_combinations_checked"], 0)
        with self.assertRaises(SystemExit):
            d.build_plan([5], argv_probe=False)


class AnchorCoincidenceRead(unittest.TestCase):
    """Lane C's two reads: is the anchor's coincidence EMPIRICALLY material? Tested on synthetic
    families with and without a planted outlier, because a detector never pointed at a positive is
    not a detector."""

    def _reps(self, n=100, outlier_at=None, kick=0.0, seed=3):
        rng = np.random.default_rng(seed)
        out = {}
        for k in range(1, n + 1):
            row = rng.normal(1.0, 0.05, size=8)
            if outlier_at is not None and k == outlier_at:
                row = row + kick
            out[k] = (float(row.sum()), row)
        return out

    def test_a_clean_family_does_NOT_flag(self):
        import anchor_coincidence_displacement as acd
        r = acd.displacement(self._reps(), 42, "replicas")
        self.assertFalse(r["FLAGS"], f"clean family flagged at |z|={r['max_abs_z']:.2f}")
        self.assertTrue(r["below_test_resolution"],
                        "a clean family's max |z| must sit under the expected max of 100 draws")

    def test_a_PLANTED_outlier_DOES_flag(self):
        """The positive control. Without it, 'nothing flagged' is not evidence."""
        import anchor_coincidence_displacement as acd
        r = acd.displacement(self._reps(outlier_at=42, kick=1.5), 42, "replicas")
        self.assertTrue(r["FLAGS"], f"planted outlier not flagged: |z|={r['max_abs_z']:.2f}")
        self.assertGreater(r["max_abs_z"], r["flag_at_abs_z"])

    def test_the_sd_excludes_the_member_under_test(self):
        """A member cannot inflate its own denominator -- otherwise a large outlier suppresses its
        own z and the test gets quieter exactly as the defect gets worse."""
        import anchor_coincidence_displacement as acd
        small = acd.displacement(self._reps(outlier_at=42, kick=1.0), 42, "replicas")["max_abs_z"]
        big = acd.displacement(self._reps(outlier_at=42, kick=3.0), 42, "replicas")["max_abs_z"]
        self.assertGreater(big, small, "z must grow with the kick, not shrink")

    def test_leverage_is_leave_one_out_and_small_for_one_of_a_hundred(self):
        import anchor_coincidence_displacement as acd
        lv = acd.leverage(self._reps(), 42, "replicas")
        self.assertLess(lv["relative_leverage"], 0.05,
                        "dropping 1 of 100 clean members must move the summary very little")
        self.assertGreater(acd.leverage(self._reps(outlier_at=42, kick=3.0), 42,
                                        "replicas")["relative_leverage"],
                           lv["relative_leverage"], "an outlier must have MORE leverage")

    def test_a_wrong_family_size_warns_that_the_threshold_is_not_valid(self):
        """The family-wise threshold was derived for m=100; at another m it is not the same test."""
        import anchor_coincidence_displacement as acd, io as _io, contextlib as _c
        buf = _io.StringIO()
        with _c.redirect_stdout(buf):
            # n=60, NOT n=30: a 30-member family has no member 42, so the earlier fixture raised
            # "member absent" before ever reaching the warning under test. Fourth fixture-index bug
            # of the day, and the third time a reported failure was the fixture's rather than the code's.
            acd.displacement(self._reps(n=60), 42, "replicas")
        self.assertIn("NOT valid as stated", buf.getvalue())

    def test_it_FAILS_CLOSED_when_the_products_are_absent(self):
        import anchor_coincidence_displacement as acd
        with tempfile.TemporaryDirectory() as td:
            rc = acd.main(["--boot-dir", str(Path(td) / "nope"),
                           "--throw-glob", str(Path(td) / "nope" / "*.npz")])
        self.assertEqual(rc, 2, "absent products must be a loud non-zero, not a clean zero")


class DerivedTargetSet(unittest.TestCase):
    """C's item 2: the target set is DERIVED, not listed -- and the derivation has a limit that
    matters for how it is read."""

    SIX = {"sbatch_sweep_bank_5d_run_bkgaware_gpu.sh", "sbatch_uthrow_run_5d_fast.sh",
           "sbatch_uthrow_block_5d.sh", "sbatch_uthrow_combine_5d_fast.sh",
           "sbatch_bootstrap_5d_gpu.sh", "sbatch_seedscan_split_5d.sh"}
    SEVEN = SIX | {"sbatch_unfold_5d_detector_bkgaware_gpu.sh"}

    def _root(self):
        return str(ND.parent)

    def test_a_targeted_but_unhooked_launcher_hard_FAILS(self):
        """WAS `test_the_lateral_leg_hard_FAILS_once_it_is_targeted`, which was true until the lateral
        got its hook. Superseded by the work itself rather than by a ruling: the lateral is now both
        targeted AND hooked, so it correctly PASSES.

        The MECHANISM still needs a test, so the example is now a launcher that is targeted and has no
        hook -- one of the six same-module variants, borrowed as a fixture. Deleting the test because
        its original example was fixed would have removed the only check that the failure half fires
        at all.
        """
        import seed_offset_policy as sp
        # the real seven now pass
        self.assertTrue(sp.assert_target_set_is_complete(self._root(), self.SEVEN))
        # ...and a targeted-but-unhooked launcher still fails
        with self.assertRaises(SystemExit) as cm:
            sp.assert_target_set_is_complete(self._root(),
                                             self.SEVEN | {"sbatch_uthrow_run_5d.sh"})
        self.assertIn("sbatch_uthrow_run_5d.sh", str(cm.exception))
        self.assertIn("would not reach them", str(cm.exception))

    def test_THE_LIMIT_the_failure_half_cannot_DISCOVER_an_undeclared_leg(self):
        """THE RESULT WORTH REPORTING. With the pre-ruling SIX the predicate PASSES -- it hard-fails
        only on launchers already declared targeted, so it cannot discover a leg nobody declared.

        The discovery channel is the HAZARD half, which IS derived from code: the lateral appears
        there under the six-set. So the predicate is a completeness check on the declared set plus a
        discovery list beside it, and reading the pass alone would reproduce exactly the miss C's item
        2 exists to prevent.
        """
        import seed_offset_policy as sp
        # The lateral was the original example and is now hooked, so the demonstration uses a launcher
        # that is still unhooked. The CLAIM is unchanged and is not about the lateral: the failure half
        # passes over anything undeclared, and only the discovery half sees it.
        r = sp.assert_target_set_is_complete(self._root(), self.SIX)
        self.assertIn("nd-unfolding/sbatch_uthrow_run_5d.sh", r["substitution_hazards"],
                      "an undeclared same-module launcher must appear in the DISCOVERY half even "
                      "when the failure half passes -- that asymmetry IS the finding")

    def test_the_hazard_list_discriminates_by_MODULE_not_by_name(self):
        """`sbatch_fps_reunfold_5d*.sh` carry `--seed 1000` and are a DIFFERENT measurement -- they run
        fps_gbdt_prior_reunfold_5d.py, not a leg module. Group mapping separates them from the six real
        same-module variants, which is what 'a coherence group is the shared seed VALUE' requires."""
        import seed_offset_policy as sp
        hard, haz, scoped = sp.derive_seed_literal_sites(self._root(), self.SEVEN)
        by = {r["file"].split("/")[-1]: r["groups"] for r in haz}
        self.assertEqual(by.get("sbatch_fps_reunfold_5d.sh"), [],
                         "a non-leg module must map to no coherence group")
        self.assertEqual(by.get("sbatch_uthrow_run_5d.sh"), ["g2"])
        self.assertEqual(by.get("sbatch_sweep_bank_5d_run.sh"), ["g1"])
        self.assertGreater(scoped, 0, "the denominator must be measured, not assumed")

    def test_it_refuses_a_pass_computed_over_zero_files(self):
        import seed_offset_policy as sp
        with tempfile.TemporaryDirectory() as td:
            import subprocess
            subprocess.run(["git", "-C", td, "init", "-q"], check=True, capture_output=True)
            with self.assertRaises(SystemExit) as cm:
                sp.assert_target_set_is_complete(td, self.SEVEN)
            self.assertIn("ZERO files", str(cm.exception))


class FenceAndFrozenHazards(unittest.TestCase):
    """C's items 2-4: the six hazards are FENCED not hooked, the fence has a test that it FIRES, F2
    is confirmed by RUN in both directions, and the hazard list is a CLOSED enumeration."""

    def test_the_fence_FIRES_for_every_one_of_the_six_same_module_hazards(self):
        """A fence nobody has tripped is a fence nobody knows works. Parameterised over all six."""
        import mii_seed_offset_driver as d
        import seed_offset_policy as sp
        six = sorted(h for h in sp.FROZEN_SUBSTITUTION_HAZARDS if "fps_reunfold" not in h)
        self.assertEqual(len(six), 6, "the six same-module variants")
        for h in six:
            with self.subTest(launcher=h), self.assertRaises(SystemExit) as cm:
                d.preflight_launcher(h)
            self.assertIn("NOT on the derived target list", str(cm.exception))

    def test_the_fence_ADMITS_every_targeted_launcher(self):
        """Otherwise a fence that rejects everything would pass the test above."""
        import mii_seed_offset_driver as d
        for rel in sorted(d.targeted_launchers()):
            with self.subTest(launcher=rel):
                self.assertTrue(d.preflight_launcher(rel))

    def test_the_hazard_list_is_EXACTLY_the_frozen_nine(self):
        """C's item 4, and the counterweight the non-raising choice needs. `len(hazards) > 0` and
        `FROZEN <= hazards` both pass forever and discover nothing; equality fails the moment a tenth
        appears. The nine block nobody; a tenth stops the build."""
        import seed_offset_policy as sp
        import mii_seed_offset_driver as d
        targeted = {p.split("/")[-1] for p in d.targeted_launchers()}
        _hard, haz, _n = sp.derive_seed_literal_sites(str(ND.parent), targeted)
        self.assertEqual({r["file"] for r in haz}, set(sp.FROZEN_SUBSTITUTION_HAZARDS),
                         "the derived hazard list must EQUAL the frozen enumeration -- a tenth "
                         "hazard is a build stop, not a longer list")

    def test_offsets_are_sort_safe_and_the_check_fires(self):
        import seed_offset_policy as sp
        self.assertEqual(sp.assert_offsets_are_sort_safe([1200 * j for j in range(50)]), 58800)
        with self.assertRaises(SystemExit):
            sp.assert_offsets_are_sort_safe([sp.MEMBER_DIR_SORT_SAFE_LIMIT])

    # ---- F2 CONFIRMED BY RUN, BOTH DIRECTIONS (C's item 3(ii)) ----
    def _f2_fixture(self, td, slab_est):
        p = Path(td)
        throws = np.array([[0.8, 2.1], [1.2, 1.9], [1.1, 2.2]])
        for nm, xs, ids in (("throws_0.npz", throws[:2], [0, 1]), ("throws_1.npz", throws[2:], [2])):
            np.savez(p / nm, xs=xs, throws=np.array(ids), flux_normalized=np.int64(1),
                     estimator_seed=np.int64(slab_est), draw_seed=np.int64(1000))
        np.savez(p / "blocks.npz", xs=np.array([[0.9, 2.2], [1.1, 1.8]]),
                 labels=np.array(["MaCCQE:0", "MaCCQE:1"], dtype=object),
                 kinds=np.array(["knob", "knob"], dtype=object), flux_normalized=np.int64(1),
                 estimator_seed=np.int64(slab_est), draw_seed=np.int64(1000))
        return str(p / "throws_*.npz"), str(p / "blocks.npz")

    @contextlib.contextmanager
    def _stub(self, utc):
        d = {"edges": [np.array([0.0, 1.0, 2.0])], "w_truth": np.ones(1),
             "w_reco": np.ones(1), "td_w": np.ones(1)}
        ol, ok = utc._load_bank, utc._xsec_for_weights
        utc._load_bank = lambda b: (d, ["MaCCQE"], 0)
        utc._xsec_for_weights = lambda *a, **k: np.array([1.0, 2.0])
        try:
            yield
        finally:
            utc._load_bank, utc._xsec_for_weights = ol, ok

    def _combine(self, slab_est, comb_est):
        import unified_throw_cov as utc
        with tempfile.TemporaryDirectory() as td:
            comb, blocks = self._f2_fixture(td, slab_est)
            args = SimpleNamespace(bank=td, iters=1, estimator_seed=comb_est, draw_seed=1000,
                                   combine=comb, block_slabs=blocks, expected_throws="0-2",
                                   null=True, out_root=None)
            with self._stub(utc):
                return utc.do_combine(args)

    def test_F2_refuses_ARCHIVE_slabs_against_an_OFFSET_combine(self):
        """Direction 1: slabs at 1000, combine at 1000+k."""
        with self.assertRaises(SystemExit) as cm:
            self._combine(1000, 2200)
        self.assertIn("refusing mixed-seed combine", str(cm.exception))

    def test_F2_refuses_OFFSET_slabs_against_an_ARCHIVE_combine(self):
        """Direction 2, the one C would not infer: slabs at 1000+k, combine at 1000."""
        with self.assertRaises(SystemExit) as cm:
            self._combine(2200, 1000)
        self.assertIn("refusing mixed-seed combine", str(cm.exception))

    def test_F2_ACCEPTS_a_matching_pair_so_it_is_not_rejecting_everything(self):
        self.assertIsNotNone(self._combine(1000, 1000))


class StubGateAndGateOnly(unittest.TestCase):
    """The probe ran a REAL unfold on a login node twice while claiming to be read-only, because PATH
    shims are displaced by the launchers' own `conda activate`. These tests pin the fix."""

    def test_a_PATH_shim_is_displaced_and_a_shell_function_is_not(self):
        """The mechanism, asserted rather than described -- the whole fix rests on this asymmetry."""
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            shim, real = Path(td) / "shim", Path(td) / "real"
            shim.mkdir(); real.mkdir()
            for d, word in ((shim, "SHIM"), (real, "REAL")):
                exe = d / "python3"
                exe.write_text("#!/bin/sh\necho %s\n" % word)
                exe.chmod(0o755)
            env = dict(os.environ, PATH=f"{shim}:{os.environ['PATH']}")
            path_only = subprocess.run(
                ["bash", "-c", f'PATH="{real}:$PATH"; python3'],
                capture_output=True, text=True, env=env).stdout.strip()
            self.assertEqual(path_only, "REAL", "a PATH shim MUST be shown displaceable")
            as_function = subprocess.run(
                ["bash", "-c", f'python3() {{ echo STUB; }}; PATH="{real}:$PATH"; python3'],
                capture_output=True, text=True, env=env).stdout.strip()
            self.assertEqual(as_function, "STUB", "a shell function MUST survive the displacement")

    def test_the_gate_FIRES_when_a_stub_would_not_survive(self):
        """Positive control. A gate that has never refused is a gate nobody knows works -- and this
        one's absence is what let a real producer run."""
        import launcher_argv_probe as probe
        saved = probe._NATIVE_PREAMBLE
        probe._NATIVE_PREAMBLE = '\nset +e\n_ARGV_SENTINEL="__SENTINEL__"\n'   # no functions
        try:
            with self.assertRaises(SystemExit) as cm:
                probe.assert_stubs_survive_activation(str(ND.parent))
            self.assertIn("STUB GATE", str(cm.exception))
            self.assertIn("not a stub", str(cm.exception))
        finally:
            probe._NATIVE_PREAMBLE = saved

    def test_the_gate_PASSES_with_the_real_preamble(self):
        import launcher_argv_probe as probe
        got = probe.assert_stubs_survive_activation(str(ND.parent))
        for cmd in probe._STUB_COMMANDS:
            self.assertEqual(got.get(cmd), "function", f"{cmd} must be a function after activation")

    def test_sbatch_IS_among_the_gated_commands(self):
        """sbatch was UNSTUBBED and nothing submitted only because these seven launchers happen not to
        invoke it. The safety rested on that accident; it must rest on the gate."""
        import launcher_argv_probe as probe
        self.assertIn("sbatch", probe._STUB_COMMANDS)

    def test_NO_LAUNCHER_IS_REACHABLE_FROM_gate_only(self):
        """STRUCTURAL, by AST. An early `return` inside the full path would be one edit from being
        bypassed; this asserts the separation instead of trusting it."""
        import ast as _ast
        tree = _ast.parse((ND / "launcher_argv_probe.py").read_text())
        fn = next(n for n in tree.body
                  if isinstance(n, _ast.FunctionDef) and n.name == "gate_only")
        called = {c.func.id for c in _ast.walk(fn)
                  if isinstance(c, _ast.Call) and isinstance(c.func, _ast.Name)}
        called |= {c.func.attr for c in _ast.walk(fn)
                   if isinstance(c, _ast.Call) and isinstance(c.func, _ast.Attribute)}
        for forbidden in ("observed_argv_native", "observed_argv", "cluster_check"):
            self.assertNotIn(forbidden, called,
                             f"gate_only must not be able to reach {forbidden}")


class CodeBasisAndCanonicalNamespace(unittest.TestCase):
    """B3 (C's addition ii) and R1 (C's ruling that `_sb` is canonical for both legs)."""

    def test_the_basis_covers_BOTH_sourced_shell_libraries(self):
        """An anchor comparison pinned to a basis excluding the code that decides whether the anchor
        RAN is pinned to the wrong object. `lib/resume_guard.sh` decides skip-versus-run."""
        import seed_offset_policy as sp
        basis = sp.member_axis_code_basis(str(ND.parent))
        for need in ("lib/resume_guard.sh", "nd-unfolding/lib_member_resume.sh"):
            self.assertIn(need, basis, f"{need} must be in the stage-1 code basis")
            self.assertRegex(basis[need], r"^[0-9a-f]{64}$")
        self.assertTrue(sp.assert_code_basis_covers_the_resume_path(basis))

    def test_the_basis_FAILS_CLOSED_on_an_absent_required_file(self):
        """A basis computed over whatever exists silently SHRINKS -- section 10c's invariant applied
        to the basis itself: an absent entry is not a weak yes."""
        import seed_offset_policy as sp
        with self.assertRaises(SystemExit) as cm:
            sp.member_axis_code_basis(str(ND.parent),
                                      required=("lib/resume_guard.sh", "nd-unfolding/nope.sh"))
        self.assertIn("INCOMPLETE", str(cm.exception))

    def test_the_resume_path_check_is_SEPARATE_from_completeness(self):
        """Deliberately two checks: a later lane trimming CODE_BASIS_REQUIRED would still get a
        COMPLETE-looking basis, and the resume libraries are the entries whose absence is invisible --
        the payload comparison would still pass bit-exact."""
        import seed_offset_policy as sp
        trimmed = {"nd-unfolding/seed_offset_policy.py": "0" * 64}
        with self.assertRaises(SystemExit) as cm:
            sp.assert_code_basis_covers_the_resume_path(trimmed)
        self.assertIn("RESUME path", str(cm.exception))

    def test_every_leg_module_and_launcher_is_in_the_required_set(self):
        """The basis must not silently omit a leg. Five leg modules, seven launchers, two libraries,
        two policy modules -- and the lateral is among them, which it was not when it joined g1."""
        import seed_offset_policy as sp
        req = set(sp.CODE_BASIS_REQUIRED)
        for leg in ("unified_throw_cov.py", "sweep_bank_5d.py", "bootstrap_nd.py",
                    "seedscan_split.py", "unfold_nd_omnifold_unbinned.py"):
            self.assertIn(f"nd-unfolding/{leg}", req, f"leg module {leg} missing from the basis")
        import mii_seed_offset_driver as d
        for rel in d.targeted_launchers():
            self.assertIn(f"nd-unfolding/{rel}", req,
                          f"targeted launcher {rel} is not in the code basis")

    def test_R1_a_member_block_producer_and_its_combine_agree_on_the_sb_namespace(self):
        """`_sb` is canonical (`receipt_construction_contract_5d.py:313-314` binds both `_sb` globs).
        The member's producer writes `_sb` so the zero-slab SystemExit is unreachable per member, and
        the UNSET path is deliberately left on the pre-existing non-`_sb` literal -- repointing it
        would let a NON-SCAN run write into the LIVE ARCHIVE directory, which is destructive on 124
        receipt-bound slabs. Right action, and my original reason for it was wrong."""
        block = (ND / "sbatch_uthrow_block_5d.sh").read_text()
        comb = (ND / "sbatch_uthrow_combine_5d_fast.sh").read_text()
        self.assertIn('mr_dir_prefix uq_5d/block_slabs_5d_sb', block,
                      "the member's block producer must write the canonical _sb namespace")
        self.assertIn('BLOCK_DIR="uq_5d/block_slabs_5d"', block,
                      "the UNSET path must stay on the pre-existing literal -- untouched by the scan")
        self.assertIn('mr_dir_prefix uq_5d/block_slabs_5d_sb', comb,
                      "the combine reads _sb unconditionally; it was never the misaligned side")
        self.assertNotIn("mr_declared", comb,
                         "the combine's conditional was reverted once _sb was ruled canonical")


class CompletenessGuardClassifiesUnopenable(unittest.TestCase):
    """`TFile.Open` RAISES under PyROOT 6.28 instead of returning null, so `check()`'s own
    `zombie/unopenable` branch was DEAD CODE and the caller's clean SystemExit never appeared.

    ROOT is absent on this machine, so the guard is exercised against a STUB `ROOT` module -- the same
    device as the stub gate. That tests the classification logic, which is what changed; it does not
    test PyROOT's actual behaviour, which the mediator measured on real truncated products.
    """

    @contextlib.contextmanager
    def _stub_root(self, open_impl):
        """A ROOT stub COMPLETE for what this module touches, not just for what I first assumed.

        My first version stubbed only TFile and the import died on `ROOT.gROOT` -- a stub whose
        incompleteness looks like a failure of the code under test. Attributes are derived from the
        module's own `ROOT.` references rather than guessed.
        """
        import sys
        import types
        mod = types.ModuleType("ROOT")
        mod.TFile = types.SimpleNamespace(Open=open_impl, kRecovered=1)
        mod.gROOT = types.SimpleNamespace(SetBatch=lambda *a, **k: None,
                                          GetVersion=lambda: "stub")
        mod.gErrorIgnoreLevel = 0
        mod.kError = 3000
        mod.kWarning = 1000
        saved = sys.modules.get("ROOT")
        sys.modules["ROOT"] = mod
        sys.modules.pop("fps_unfold_complete", None)
        try:
            import fps_unfold_complete as fuc
            yield fuc
        finally:
            sys.modules.pop("fps_unfold_complete", None)
            if saved is None:
                sys.modules.pop("ROOT", None)
            else:
                sys.modules["ROOT"] = saved

    def test_an_OSError_from_Open_is_CLASSIFIED_not_propagated(self):
        """The defect: a truncated file raised out of check() so the caller could never report why."""
        def _raises(path, *a, **k):
            raise OSError(f"file {path} does not exist or is unreadable")
        with self._stub_root(_raises) as fuc, tempfile.TemporaryDirectory() as td:
            target = Path(td) / "trunc.root"
            target.write_bytes(b"\x00" * 4096)      # >1024 so it clears the tiny-file check
            r = fuc.check(str(target), expect_nbins=0, require_completeness=False)
        self.assertFalse(r["ok"], "an unopenable file must not be ok")
        self.assertIn("zombie/unopenable", r["why"],
                      "check() must CLASSIFY the failure rather than let OSError escape -- a guard "
                      "that cannot report its own reason leaves a bare ROOT traceback for the next "
                      f"reader. got: {r!r}")
        self.assertIn("OSError", r["why"], "the reason should name what actually happened")

    def test_the_null_return_branch_is_KEPT_and_still_classifies(self):
        """Both branches kept: the except handles pythonized PyROOT, `not f` is still correct for a
        build or call path that returns null. Removing either trades one blind spot for another."""
        with self._stub_root(lambda *a, **k: None) as fuc, tempfile.TemporaryDirectory() as td:
            target = Path(td) / "null.root"
            target.write_bytes(b"\x00" * 4096)
            r = fuc.check(str(target), expect_nbins=0, require_completeness=False)
        self.assertFalse(r["ok"])
        self.assertIn("zombie/unopenable", r["why"])

    def test_the_stub_itself_is_not_what_makes_these_pass(self):
        """CONTROL. A stub that raises on IMPORT would fail these tests for the wrong reason, and a
        stub too permissive would pass them for the wrong reason. So: a HEALTHY open must reach further
        into check() and fail on a LATER gate, proving the early return is the one under test."""
        import types
        class _H:
            # IsZombie was missing on the first attempt and the CONTROL is what surfaced it -- the two
            # real tests above never reach this far, so an incomplete healthy-file stub would have gone
            # unnoticed and they would both have been passing over a stub that could not represent a
            # healthy file at all.
            def IsZombie(self): return False
            def TestBit(self, _): return False
            def Get(self, _): return None
            def Close(self): pass
        with self._stub_root(lambda *a, **k: _H()) as fuc, tempfile.TemporaryDirectory() as td:
            target = Path(td) / "openable.root"
            target.write_bytes(b"\x00" * 4096)
            r = fuc.check(str(target), expect_nbins=0, require_completeness=False)
        self.assertFalse(r["ok"])
        self.assertIn("no hXSecND_flat", r["why"],
                      "an OPENABLE file must fail on a LATER gate, not on zombie/unopenable -- "
                      f"otherwise these tests pass because the stub is broken. got: {r!r}")


class MemberRootFirst(unittest.TestCase):
    """C reversed my path shape, and the preflight below is the mechanism that decided it."""

    def _paths(self, offset, args):
        import subprocess
        script = 'source lib_member_resume.sh\n' + "\n".join(
            f'mr_dir_prefix "{a}" ; echo' for a in args)
        env = dict(os.environ, MNV_EST_SEED_OFFSET=str(offset),
                   REPO=str(ND.parent), ND=str(ND))
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                           env=env, cwd=str(ND))
        return [l for l in r.stdout.split("\n") if l.strip()]

    def test_the_member_root_comes_FIRST_for_relative_and_absolute_paths(self):
        rel, absol = "uq_5d/block_slabs_5d_sb", f"{ND}/uq_5d/universe_sweep_bkgaware"
        got = self._paths(1200, [rel, absol])
        self.assertEqual(got[0], "mii/member_k001200/uq_5d/block_slabs_5d_sb")
        self.assertEqual(got[1], f"{ND}/mii/member_k001200/uq_5d/universe_sweep_bkgaware",
                         "an absolute path is anchored after /nd-unfolding/, not prefixed blindly")

    def test_UNDECLARED_paths_are_byte_identical_to_the_archive_paths(self):
        rel = "uq_5d/block_slabs_5d_sb"
        self.assertEqual(self._paths("", [rel])[0], rel,
                         "every non-scan use of these launchers must be unchanged")

    def test_an_unanchored_absolute_path_FAILS_CLOSED(self):
        """A member path assembled by guesswork is how a member writes outside its own tree."""
        import subprocess
        r = subprocess.run(["bash", "-c",
                            'source lib_member_resume.sh; mr_dir_prefix /tmp/nowhere; echo "rc=$?"'],
                           capture_output=True, text=True,
                           env=dict(os.environ, MNV_EST_SEED_OFFSET="1200"), cwd=str(ND))
        self.assertIn("no /nd-unfolding/ anchor", r.stderr)
        self.assertIn("Refusing to guess", r.stderr)

    def test_THE_PREFLIGHT_REJECTS_MY_OWN_PREVIOUS_PATH_SHAPE(self):
        """C's argument (1), demonstrated rather than argued.

        Spec section 1's preflight must reject any member output path equal to, under, or
        glob-overlapping the six canonical archive namespaces. Under my original
        `uq_5d/block_slabs_5d_sb/member_k001200/` EVERY member path is beneath a canonical namespace by
        construction -- so this check would have had to reject all 50 members or carry an
        "under, but with a member component" exception, which is a guard special-casing the thing it
        guards. The new shape passes the same check as a plain prefix test.
        """
        import seed_offset_policy as sp
        with self.assertRaises(SystemExit) as cm:
            sp.assert_member_path_is_outside_the_archive("uq_5d/block_slabs_5d_sb/member_k001200")
        self.assertIn("inside the canonical archive namespace", str(cm.exception))
        self.assertTrue(sp.assert_member_path_is_outside_the_archive(
            "mii/member_k001200/uq_5d/block_slabs_5d_sb"))

    def test_the_preflight_also_rejects_an_UNSCOPED_path(self):
        """A path that is neither under the archive nor under the member container is a path nobody
        can show is safe by inspection -- which is the property member-first buys."""
        import seed_offset_policy as sp
        for bad in ("uq_5d/block_slabs_5d_sb", "boot_nd_5d/member_k001200/x.npz", "somewhere/else"):
            with self.subTest(path=bad), self.assertRaises(SystemExit):
                sp.assert_member_path_is_outside_the_archive(bad)

    def test_every_canonical_namespace_is_listed(self):
        """Six, and the list is what the check is only as good as."""
        import seed_offset_policy as sp
        self.assertEqual(len(sp.CANONICAL_ARCHIVE_NAMESPACES), 6)
        for ns in ("uq_5d/uthrow_slabs_5d_sb", "uq_5d/block_slabs_5d_sb", "boot_nd_5d",
                   "seedscan_split_5d", "uq_5d/universe_sweep_bkgaware"):
            self.assertIn(ns, sp.CANONICAL_ARCHIVE_NAMESPACES)


class CompletenessGateIsRequiredNotSkipped(CompletenessGuardClassifiesUnopenable):
    """The tightening of 2026-08-18, tested IN THE DIRECTION IT ACTS.

    `analyze_universes_5d.load_flat` passed `require_completeness=False` on the stated grounds that
    this family "does not always write globalCompleteness". The mediator read the key straight out of a
    real archive universe (0.9998608732766575) and asked for a real absent case or a tightening.
    MEASURED: there is no absent case -- `sweep_bank_5d.py:289` and
    `unfold_nd_omnifold_unbinned.py:1014` both write it unconditionally, in the same straight-line
    block as `hXSecND_flat`. So the flag was tightened, and what it had been silently admitting was not
    a threshold but a NaN, whose cause is known (`denom_nd.sum() <= 0`).

    Inherits the stub harness deliberately -- a second copy of a ROOT stub drifts exactly the way a
    second copy of a completeness rule does, which is what this whole delegation was about.
    """

    def _file(self, gc, nbins=4):
        class _P:
            def __init__(self, v): self._v = v
            def GetVal(self): return self._v
        class _H:
            def GetNbinsX(self): return nbins
            def GetBinContent(self, i): return 1.0
        class _F:
            def IsZombie(self): return False
            def TestBit(self, _): return False
            def Get(self, k):
                if k == "hXSecND_flat": return _H()
                if k == "globalCompleteness": return None if gc is None else _P(gc)
                return None
            def Close(self): pass
        return lambda *a, **k: _F()

    def _check(self, gc, nbins=4, **kw):
        with self._stub_root(self._file(gc, nbins)) as fuc, tempfile.TemporaryDirectory() as td:
            target = Path(td) / "u.root"
            target.write_bytes(b"\x00" * 4096)
            kw.setdefault("expect_nbins", 0)
            return fuc.check(str(target), **kw)

    def test_a_NaN_completeness_universe_is_REJECTED_under_the_new_settings(self):
        """THE DEFECT THE RELAXATION ADMITTED. A universe whose denominator integrates to zero has a
        meaningless cross-section and was being folded into the 188-universe covariance silently."""
        r = self._check(float("nan"), min_complete=0.0, require_completeness=True)
        self.assertFalse(r["ok"], "a NaN-completeness universe must not be accepted")
        self.assertIn("no/NaN globalCompleteness", r["why"])

    def test_the_OLD_settings_ACCEPTED_that_same_NaN_universe(self):
        """The control that makes the test above mean something: same stub, old flag, opposite verdict.
        Without this the new test could be passing for a reason unrelated to what changed."""
        r = self._check(float("nan"), require_completeness=False)
        self.assertTrue(r["ok"], "if this fails, the NaN test above is not measuring the tightening")

    def test_an_ABSENT_completeness_key_is_also_REJECTED(self):
        r = self._check(None, min_complete=0.0, require_completeness=True)
        self.assertFalse(r["ok"]); self.assertIn("no/NaN globalCompleteness", r["why"])

    def test_a_HEALTHY_universe_still_passes_and_its_value_is_RECORDED(self):
        r = self._check(0.9998608732766575, min_complete=0.0, require_completeness=True)
        self.assertTrue(r["ok"], f"the real archive value must pass: {r!r}")
        self.assertAlmostEqual(r["gc"], 0.9998608732766575, places=12)

    def test_the_FPS_FLOOR_IS_DELIBERATELY_NOT_INHERITED(self):
        """min_complete=0.0, not 0.50. A floor tuned on the 285-bin FPS grid is not a measurement about
        the 5D universe family, and I have not measured that family's distribution. This test pins the
        CHOICE so it cannot be quietly changed into an inherited default -- and it fails the moment
        someone measures the 188 and adopts a real floor, which is when it should be revisited."""
        low = 0.30
        self.assertTrue(self._check(low, min_complete=0.0, require_completeness=True)["ok"],
                        "0.30 must pass under the chosen floor")
        inherited = self._check(low, require_completeness=True)     # min_complete=None -> FPS 0.50
        self.assertFalse(inherited["ok"])
        self.assertIn("< 0.5", inherited["why"],
                      "and it WOULD have been rejected by the inherited FPS floor -- which is the "
                      "choice being pinned, not an accident")

    def test_a_WRONG_GRID_universe_gets_a_CLEAN_DIAGNOSTIC(self):
        """Previously `expect_nbins=0` skipped this and the mismatch surfaced as a numpy broadcast
        error at the subtraction two frames up. Universes are now checked against the CV's bin count."""
        r = self._check(1.0, nbins=4)
        self.assertTrue(r["ok"])
        r2 = self._check(1.0, nbins=4, expect_nbins=65856, min_complete=0.0,
                         require_completeness=True)
        self.assertFalse(r2["ok"]); self.assertIn("nbins 4 != 65856", r2["why"])

    def test_the_CONSUMER_no_longer_asks_for_the_relaxation(self):
        """Read the CALL, not the file.

        My first version of this test did `assertNotIn("require_completeness=False", src)` and it
        FAILED -- on the comment I had just written explaining why the flag was removed. A substring
        search over a source file cannot distinguish a call from prose ABOUT a call, and every honest
        retraction I write makes that kind of check likelier to misfire. This is the same shape as the
        `.count()` collision earlier in this campaign, so it gets the same remedy: parse it.
        """
        import ast
        src = (ND / "analyze_universes_5d.py").read_text()
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "load_flat")
        calls = [c for c in ast.walk(fn)
                 if isinstance(c, ast.Call) and getattr(c.func, "attr", None) == "check"]
        self.assertEqual(len(calls), 1, "load_flat should delegate exactly once")
        kw = {k.arg: k.value for k in calls[0].keywords}
        self.assertIn("require_completeness", kw)
        self.assertIs(kw["require_completeness"].value, True,
                      "the completeness gate must be REQUIRED, not skipped")
        import mii_root_payload_classes  # noqa: F401  (import-order sanity for the suite)
        self.assertEqual(getattr(kw["min_complete"], "id", None), "MIN_COMPLETE_5D_UNIVERSE",
                         "the floor must be a NAMED, documented constant -- a bare literal in the "
                         "call site is where a measured threshold turns back into a magic number")
        self.assertIn("expect_nbins", kw,
                      "universes are checked against the CV's grid; the CV itself defines it")

    def test_the_UNIVERSE_call_site_passes_the_CVs_bin_count(self):
        """The other half of the grid check: load_flat's caller must supply cv.size for universes and
        nothing for the CV, which is the file that defines the grid."""
        import ast
        src = (ND / "analyze_universes_5d.py").read_text()
        sites = [c for c in ast.walk(ast.parse(src))
                 if isinstance(c, ast.Call) and getattr(c.func, "id", None) == "load_flat"]
        self.assertEqual(len(sites), 2, "one CV load, one universe load")
        shapes = sorted(
            (len(c.args), tuple(k.arg for k in c.keywords),
             ast.unparse(c.keywords[0].value) if c.keywords else None)
            for c in sites)
        self.assertEqual(shapes[0], (1, (), None), "the CV passes no expectation")
        self.assertEqual(shapes[1], (1, ("expect_nbins",), "cv.size"),
                         "the universes are pinned to the CV's own bin count")

    def test_the_helper_docstring_RETRACTS_the_false_premise(self):
        """NOT "the phrase is gone" -- the phrase is deliberately still there, in quotes, being
        retracted, because a correction that deletes the wrong claim leaves the next reader free to
        re-derive it. My first version of this test asserted its ABSENCE and failed against my own
        retraction. What must be true is that the phrase never appears as an active justification.
        """
        src = (ND / "fps_unfold_complete.py").read_text()
        self.assertIn("for products that do not write it", src,
                      "the false claim is quoted so the retraction has a referent")
        self.assertIn("that was\n    false of the family I applied it to", src,
                      "and it must be quoted AS FALSE, adjacent to the quote")
        self.assertIn("DO NOT REACH FOR `require_completeness=False` TO RELAX A THRESHOLD", src)
        # the operative form: nothing in this repo may still CALL for the relaxation on that ground
        import ast
        for mod in ("analyze_universes_5d.py", "fps_unfold_complete.py"):
            for c in ast.walk(ast.parse((ND / mod).read_text())):
                if isinstance(c, ast.Call) and getattr(c.func, "attr", None) == "check":
                    for k in c.keywords:
                        if k.arg == "require_completeness":
                            self.assertIsNot(k.value.value, False,
                                             f"{mod} still calls check() with the gate off")


class RootPayloadThreeClasses(unittest.TestCase):
    """B2's table. C ruled stage 1 cannot gate until this enumeration exists."""

    def setUp(self):
        import mii_root_payload_classes as m
        self.m = m
        self.arch = {"C_unified": "d1", "C_blocksum": "d2", "C_cross": "d3",
                     "hJointMeanShift": "d4", "sqrt_tr_unified": 1.0, "sqrt_tr_block": 2.0,
                     "joint_mean_shift_norm": 3.0, "fixed_seed_null_norm": 4.0, "n_throws": 160}
        self.mem = dict(self.arch, fixed_seed_null_checked=1, estimator_seed=1000,
                        draw_seed=1000, est_seed_offset=0, est_seed_offset_declared=1)
        self.A = "uq_5d/unified_throw_cov_5d.root"

    def test_an_UNCLASSIFIED_key_fails_closed(self):
        """The whole point: an unclassified key is the one a future writer added without telling the
        comparator. It must fail, not default to a permissive class."""
        with self.assertRaises(SystemExit) as cm:
            self.m.classify("sweep_universe.root", "some_future_key")
        self.assertIn("NO CLASS", cm.exception.fail_message)
        self.assertEqual(cm.exception.code, 2,
                         "H4: a fail-closed exit must be 2, which main() maps to FAIL. Exit 1 is INCOMPLETE, and a driver treating rc 1 as continue walks past a corrupt archive.")

    def test_a_correct_k0_anchor_is_INCOMPLETE_not_PASS_and_not_FAIL(self):
        """THREE VERDICTS. A correct anchor has no mismatch and still cannot be PASS: 9 keys are
        derived from other keys in the same file and nothing has recomputed them (BEN-077). Folding
        that into FAIL conflates a real mismatch with an unfinished comparator; folding it into PASS is
        worse, because the pressure at stage 1 is toward green."""
        verdict, findings = self.m.compare(self.A, self.arch, self.mem)
        self.assertEqual(verdict, "INCOMPLETE")
        # TWO kinds of owed, after H2: recomputation not yet performed, and keys the ARCHIVE CANNOT
        # SUPPLY because it predates their writer. Both are "not verified"; neither is a mismatch.
        self.assertTrue(all(("RECOMPUTATION NOT PERFORMED" in f) or f.startswith("UNCOMPARABLE ")
                            for f in findings),
                        f"only recomputation and archive-predates should be owed: {findings}")
        self.assertTrue(any(f.startswith("UNCOMPARABLE ") for f in findings),
                        "and the archive-predates keys must be RECORDED, since admissible is not checked")

    def test_a_CONFIGURATION_difference_is_a_HARD_FAILURE(self):
        v, f = self.m.compare(self.A, self.arch, dict(self.mem, n_throws=159))
        self.assertEqual(v, "FAIL")
        self.assertTrue(any("n_throws" in x and "HARD FAILURE" in x for x in f), f)

    def test_PROVENANCE_may_differ_but_may_NOT_be_ABSENT_from_the_member(self):
        """C's clarification, and the distinction is load-bearing: superset is allowed on the ARCHIVE
        side only. A member missing its offset stamp is inadmissible, not merely undocumented."""
        v, f = self.m.compare(self.A, self.arch, dict(self.mem, estimator_seed=99999))
        self.assertEqual(v, "INCOMPLETE", "a differing provenance value is fine across the scan")
        short = dict(self.mem); short.pop("est_seed_offset_declared")
        v2, f2 = self.m.compare(self.A, self.arch, short)
        self.assertEqual(v2, "FAIL")
        self.assertTrue(any("ABSENT FROM MEMBER" in x for x in f2), f2)

    def test_the_DRAW_SEED_row_is_enforceable_which_is_what_running_the_table_caught(self):
        """The archive carries NO seed key of any kind, so "draw_seed must equal the archive" was a
        check that could never run. Its value comes from the pinned g2 literal instead -- a THIRD kind
        of map entry (declared constant, external to both files) that I had not anticipated."""
        self.assertEqual(self.m._g2_baseline(), 1000)
        self.assertNotIn("draw_seed", self.arch, "the premise: the archive has no draw_seed")
        v, f = self.m.compare(self.A, self.arch, dict(self.mem, draw_seed=1200))
        self.assertEqual(v, "FAIL")
        self.assertTrue(any("draw_seed" in x and "1000" in x for x in f),
                        f"a drifted draw seed must be caught against the declared constant: {f}")

    def test_the_draw_seed_constant_is_SOURCED_not_RETYPED(self):
        """One place it can be wrong, not two. A second copy of 1000 drifts silently."""
        import seed_offset_policy as sp
        self.assertEqual(sp.LEG_BASELINES["unified_throw_cov"], ("g2", 1000))
        src = (ND / "mii_root_payload_classes.py").read_text()
        self.assertIn("seed_offset_policy.LEG_BASELINES", src)
        self.assertIn('_g2_baseline()', src)

    def test_the_k0_ANCHORs_provenance_is_NOT_free(self):
        """PROVENANCE means "may differ across the scan". The anchor is the member that must NOT
        differ, and the class alone does not say so."""
        self.assertEqual(self.m.anchor_identity(self.mem, 0), [])
        wrong = self.m.anchor_identity(dict(self.mem, estimator_seed=1200), 0)
        self.assertTrue(any("k=0 ANCHOR" in p for p in wrong), wrong)
        self.assertEqual(
            self.m.anchor_identity(dict(self.mem, estimator_seed=1200, est_seed_offset=1200), 1200),
            [], "member 1200 differing from the archive is the whole point of the scan")

    def test_an_UNDECLARED_offset_cannot_pass_as_a_deliberate_anchor(self):
        """declared==0 means an unhooked launcher stamping its baseline is indistinguishable from a
        deliberate k=0 member. That ambiguity is why the stamp is two keys and not a sentinel."""
        p = self.m.anchor_identity(dict(self.mem, est_seed_offset_declared=0), 0)
        self.assertTrue(any("UNHOOKED" in x for x in p), p)

    def test_the_ARCHIVE_KEY_MAP_covers_every_key_the_writers_added(self):
        """The headline finding, as a check: the archive predates its own writers' provenance blocks,
        so a k=0 anchor built today carries keys the archive lacks FOR REASONS UNRELATED TO THE SEED.
        Every such key needs a dated row or stage 1 reddens for the wrong reason."""
        archive_9 = set(self.arch)
        writer_keys = set(self.m.UNIFIED_THROW_COV)
        extra = writer_keys - archive_9
        self.assertEqual(len(extra), 5, f"5 extra keys in the throw root: {sorted(extra)}")
        for k in extra:
            self.assertIn(k, self.m.ARCHIVE_KEY_MAP, f"{k} has no dated map row")
            self.assertIn("landed", self.m.ARCHIVE_KEY_MAP[k])

    def test_an_UNEXPLAINED_member_only_key_is_reported_rather_than_tolerated(self):
        """Not in the archive AND not in the map: the map is dated and derivable, so silence is not an
        option. This is the branch that keeps the map honest as writers change."""
        self.m.ARTIFACTS["sweep_universe.root"]["ndim"]   # sanity: table is a dict
        v, f = self.m.compare("sweep_universe.root",
                              {"hXSecND_flat": "d", "ndim": 5},
                              {"hXSecND_flat": "d", "ndim": 5, "dataPOT": 1e21})
        self.assertEqual(v, "FAIL")
        self.assertTrue(any("NOT IN THE ARCHIVE KEY MAP" in x for x in f), f)

    def test_the_STAMP_COVERAGE_table_names_the_three_unstamped_writers(self):
        """Remedy (B) -- never resume a ROOT product -- must cover every writer with 0 here. Its scope
        NARROWS as (A) lands, so this table is what gets re-measured, not the prose."""
        zero = {k for k, v in self.m.STAMP_COVERAGE.items() if v == 0}
        self.assertEqual(zero, {"unfold_nd_omnifold_unbinned.py", "adopt_unified_5d.py",
                                "analyze_universes_5d.py"})
        self.assertEqual(self.m.STAMP_COVERAGE["unified_throw_cov.py"], 4)
        self.assertEqual(self.m.STAMP_COVERAGE["sweep_bank_5d.py"], 3)

    def test_the_stamp_coverage_table_MATCHES_THE_WRITERS(self):
        """A table of measurements rots the moment a writer changes. Re-derive it here rather than
        trusting the number I typed -- a claim about code is dated unless something re-reads the code.
        """
        import re
        pat = re.compile(r'TParameter\("int"\)\(\s*"(estimator_seed|draw_seed|est_seed_offset'
                         r'|est_seed_offset_declared)"')
        for fname, expected in self.m.STAMP_COVERAGE.items():
            got = len(pat.findall((ND / fname).read_text()))
            self.assertEqual(got, expected,
                             f"{fname}: table says {expected} identity stamps, source has {got}")

    def test_the_flat_length_is_65856_not_285(self):
        """C sized a per-bin array off the extended-FPS 285-bin grid and was wrong by 230x. Pinned so
        the next reader cannot inherit the wrong number from this table."""
        self.assertEqual(self.m.FLAT_NBINS, 65856)
        self.assertAlmostEqual(self.m.FLAT_NBINS * 8 / 1e6, 0.527, places=3)


class ProbeAssertsShapeNotSubstring(unittest.TestCase):
    """The mediator found that the probe's predicate could not distinguish the shape it was re-run to
    confirm: `"member_k" in str(o)` is true of BOTH `uq_5d/.../member_k001200/x` and
    `mii/member_k001200/uq_5d/.../x`. The re-run returned byte-for-byte the same summary as the
    pre-change run, and THAT IDENTITY WAS THE EVIDENCE.

    A SUBSTRING TEST CANNOT EXPRESS A POSITIONAL REQUIREMENT -- containment is the one relation blind
    to order, and the requirement was "the member root comes FIRST".
    """

    def setUp(self):
        import launcher_argv_probe as P
        self.P = P

    def test_the_NEW_shape_passes_relative_and_absolute(self):
        for path in ("mii/member_k001200/uq_5d/block_slabs_5d_sb/x.npz",
                     f"{ND}/mii/member_k001200/boot_nd_5d/res_boot_7.npz"):
            with self.subTest(path=path):
                ok, why = self.P.is_member_scoped(path, 1200)
                self.assertTrue(ok, why)

    def test_THE_OLD_SHAPE_FAILS_which_the_substring_test_could_not_do(self):
        """POSITIVE CONTROL, and it is the whole point of the change: a planted old-shape path must
        FAIL. Without this the new predicate could be as blind as the one it replaced."""
        for path in ("uq_5d/block_slabs_5d_sb/member_k001200/x.npz",
                     f"{ND}/boot_nd_5d/member_k001200/res_boot_7.npz"):
            with self.subTest(path=path):
                ok, why = self.P.is_member_scoped(path, 1200)
                self.assertFalse(ok, f"the OLD shape must not pass: {path}")
                self.assertIn("NOT AT THE ROOT", why,
                              "and the reason must say WHICH failure it is -- 'contains a member "
                              "component but in the wrong position' is a different defect from "
                              "'not scoped at all' and they get fixed differently")

    def test_the_OLD_predicate_would_have_passed_both(self):
        """Demonstrates the defect rather than asserting it. If this ever fails, the premise of the
        change was wrong and the change should be re-argued."""
        for path in ("mii/member_k001200/uq_5d/x.npz", "uq_5d/member_k001200/x.npz"):
            self.assertIn("member_k", path,
                          "the substring predicate accepted both shapes -- that is why the re-run "
                          "produced an identical summary and proved nothing about placement")

    def test_an_UNSCOPED_path_fails_with_a_DIFFERENT_reason(self):
        ok, why = self.P.is_member_scoped("boot_nd_5d/res_boot_7.npz", 1200)
        self.assertFalse(ok)
        self.assertIn("not member-scoped at all", why)

    def test_the_member_name_AGREES_WITH_BASH_rather_than_being_a_second_copy(self):
        """A second copy of the naming rule drifts silently, and this one lives in a different
        language from the original. Derived from `mr_member_dir` itself, not from my Python."""
        import subprocess
        for k in (0, 1200, 9600, -600):
            with self.subTest(k=k):
                r = subprocess.run(
                    ["bash", "-c", 'source lib_member_resume.sh; mr_member_root'],
                    capture_output=True, text=True, cwd=str(ND),
                    env=dict(os.environ, MNV_EST_SEED_OFFSET=str(k)))
                self.assertEqual(r.stdout.strip(), self.P.member_root_for(k),
                                 f"python and bash disagree on the member root for k={k}: "
                                 f"bash={r.stdout.strip()!r} python={self.P.member_root_for(k)!r}")

    def test_the_probe_PRINTS_every_observed_path(self):
        """A passing run's log contained NO PATH -- 36 lines, zero occurrences of `member_k` or `mii/`
        outside the summary counts -- so nothing downstream could audit what passed, and the counts
        were identical across two different shapes. The paths ARE the ingredients of `namespaced=N`."""
        src = (ND / "launcher_argv_probe.py").read_text()
        self.assertIn('print(f"[probe]   PATH', src)

    def test_the_substring_predicate_is_GONE_FROM_THE_CODE_not_merely_from_the_text(self):
        """BEN-482'S THIRD INSTANCE, AND I HIT IT IN THE SAME TURN I FILED THE ROW.

        My first version was `assertNotIn('if "member_k" in str(o)', src)` and it failed -- because
        `is_member_scoped`'s docstring QUOTES THE OLD PREDICATE VERBATIM, deliberately, so the next
        reader can see what was replaced. The grep could not tell the retired predicate from the
        explanation of its retirement. Third time today; the row's own remedy is to parse, so:
        walk the AST for a `"member_k" in <expr>` comparison, which cannot exist in a docstring.
        """
        import ast
        tree = ast.parse((ND / "launcher_argv_probe.py").read_text())

        def containments(node):
            return [c.lineno for c in ast.walk(node)
                    if isinstance(c, ast.Compare) and any(isinstance(o, ast.In) for o in c.ops)
                    and isinstance(c.left, ast.Constant) and c.left.value == "member_k"]

        funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        # NARROWED AFTER MY FIRST VERSION FAILED ON A LEGITIMATE USE, and the narrowing is the finding:
        # ONE containment test survives INSIDE `is_member_scoped` at :458, and it SHOULD. There it is
        # not the acceptance predicate -- acceptance is `startswith` -- it only refines the REJECTION
        # REASON, distinguishing "contains a member component but in the wrong position" (the shape C
        # reversed) from "not member-scoped at all". Those are different defects with different fixes,
        # and collapsing them would make the diagnostic worse.
        #
        # So the requirement is not "containment appears nowhere" but "CONTAINMENT IS NOT THE
        # ACCEPTANCE PREDICATE". A blanket ban would have forced me to delete a better error message to
        # satisfy a test -- the shape of over-broad assertion that makes people weaken checks.
        self.assertEqual(len(containments(funcs["is_member_scoped"])), 1,
                         "the classifier keeps exactly one containment, for the reason string")
        for name, fn in funcs.items():
            if name == "is_member_scoped":
                continue
            self.assertEqual(containments(fn), [],
                             f"{name}() uses containment on 'member_k' -- acceptance must go through "
                             "is_member_scoped(), because containment is blind to order and cannot "
                             "express 'the member root comes first'")
        # and the shape test IS present as code, so this is not passing by the file being empty
        self.assertTrue(any(isinstance(n, ast.FunctionDef) and n.name == "is_member_scoped"
                            for n in ast.walk(tree)),
                        "control: the replacement predicate must exist")


class Stage0Distinctness(unittest.TestCase):
    """Stage 0 answers a question the probe cannot: the probe showed the offset REACHES the seed;
    stage 0 shows it CHANGES THE NUMBERS.

    ITS POLARITY IS INVERTED FROM EVERY OTHER GATE -- PASS means "these DIFFER" -- so the usual
    failure modes (missing file, empty glob, self-comparison) all produce NO OBSERVED DIFFERENCE and
    would read as "the offset does nothing", which is a physics claim. Hence three verdicts.
    """

    def setUp(self):
        import mii_stage0_distinctness as S
        self.S = S
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def _member(self, offset, replicas, *, xsec=None, seed_of=None, est_of=None, declared=1):
        d = self.root / f"mii/member_k{offset:06d}" / "boot_nd_5d"
        d.mkdir(parents=True, exist_ok=True)
        for rid in replicas:
            x = np.full(64, 1.0 + rid) if xsec is None else xsec(rid, offset)
            np.savez_compressed(
                d / f"res_boot_{rid}.npz",
                seed=np.int64(rid if seed_of is None else seed_of(rid, offset)),
                xsec_flat=x, shape=np.array([64]), total_xsec=float(x.sum()),
                estimator_seed=np.int64(42 + offset if est_of is None else est_of(rid, offset)),
                est_seed_offset_declared=np.int64(declared),
                est_seed_offset=np.int64(offset))
            # np.savez_compressed on 64 floats is under the 1024 B floor, so pad to a realistic size
            pth = d / f"res_boot_{rid}.npz"
            if pth.stat().st_size < 1024:
                x2 = np.tile(x, 64)
                np.savez_compressed(
                    pth, seed=np.int64(rid if seed_of is None else seed_of(rid, offset)),
                    xsec_flat=x2 + np.arange(x2.size) * 1e-12, shape=np.array([x2.size]),
                    total_xsec=float(x2.sum()),
                    estimator_seed=np.int64(42 + offset if est_of is None else est_of(rid, offset)),
                    est_seed_offset_declared=np.int64(declared),
                    est_seed_offset=np.int64(offset))
        return str(self.root / f"mii/member_k{offset:06d}")

    def test_genuinely_different_products_are_DISTINCT(self):
        a = self._member(0, [1, 2, 3], xsec=lambda r, k: np.full(64, 1.0 + r))
        b = self._member(1200, [1, 2, 3], xsec=lambda r, k: np.full(64, 1.0 + r + 0.5))
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.DISTINCT, rep.get("why"))
        self.assertEqual(rep["n_differing"], 3)
        self.assertTrue(all(r["max_abs_delta"] > 0 for r in rep["replicas"]),
                        "a DISTINCT verdict whose max|delta| is 0 would contradict itself")

    def test_identical_products_are_IDENTICAL_a_REAL_NEGATIVE_not_an_error(self):
        a = self._member(0, [1, 2], xsec=lambda r, k: np.full(64, 1.0 + r))
        b = self._member(1200, [1, 2], xsec=lambda r, k: np.full(64, 1.0 + r))
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.IDENTICAL)
        self.assertIn("REAL NEGATIVE RESULT", rep["why"],
                      "this is the one outcome that IS a physics answer, and it must not be reported "
                      "in the same class as a broken comparison")

    def test_an_EMPTY_TREE_is_INCOMPARABLE_not_IDENTICAL(self):
        """THE DEFECT THIS MODULE EXISTS TO PREVENT. An empty glob produces no observed difference,
        which under a two-valued checker reads as 'the offset changes nothing' -- a physics claim made
        from a directory nothing was found in."""
        a = self._member(0, [1, 2])
        empty = self.root / "mii/member_k001200"
        empty.mkdir(parents=True, exist_ok=True)
        v, rep = self.S.compare_member_pair(a, str(empty), 0, 1200)
        self.assertEqual(v, self.S.INCOMPARABLE)
        self.assertIn("EVIDENCE ABOUT THE SEARCH", rep["why"])

    def test_SELF_COMPARISON_is_INCOMPARABLE(self):
        """C's stage-1 asymmetry, applied one stage earlier: a null from comparing a member to itself
        says nothing about the seed."""
        a = self._member(0, [1])
        v, rep = self.S.compare_member_pair(a, a, 0, 0)
        self.assertEqual(v, self.S.INCOMPARABLE)
        self.assertIn("comparing a member to itself", rep["why"])
        v2, rep2 = self.S.compare_member_pair(a, a, 0, 1200)
        self.assertEqual(v2, self.S.INCOMPARABLE, "same directory under two offset labels")
        self.assertIn("one directory, two names", rep2["why"])

    def test_a_DIFFERENT_DATA_DRAW_is_INCOMPARABLE_even_though_the_products_DIFFER(self):
        """BOTH SIDES NAMED BEFORE THE DELTA IS BELIEVED. If the draws differ, the difference is
        attributable to the draw and the measurement is not the one stage 0 makes -- and it would be
        LARGE, which is the direction that fools you."""
        a = self._member(0, [1], xsec=lambda r, k: np.full(64, 1.0))
        b = self._member(1200, [1], xsec=lambda r, k: np.full(64, 9.0),
                         seed_of=lambda r, k: r + 77)
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.INCOMPARABLE)
        self.assertIn("DATA DRAW DIFFERS", rep["why"])

    def test_an_estimator_seed_delta_that_does_not_match_the_offset_delta_is_INCOMPARABLE(self):
        a = self._member(0, [1], xsec=lambda r, k: np.full(64, 1.0))
        b = self._member(1200, [1], xsec=lambda r, k: np.full(64, 2.0),
                         est_of=lambda r, k: 42 + 7)
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.INCOMPARABLE)
        self.assertIn("not demonstrably", rep["why"])

    def test_an_UNDECLARED_offset_is_INCOMPARABLE(self):
        a = self._member(0, [1], declared=0)
        b = self._member(1200, [1])
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.INCOMPARABLE)
        self.assertIn("declared == 0", rep["why"])

    def test_PARTIAL_distinctness_is_not_a_pass(self):
        """If the estimator seed moves the estimate it should move every replica. An identical subset
        means something else is varying, and calling that DISTINCT would ship a half-effect."""
        a = self._member(0, [1, 2], xsec=lambda r, k: np.full(64, 1.0 + r))
        b = self._member(1200, [1, 2],
                         xsec=lambda r, k: np.full(64, 1.0 + r + (0.5 if r == 1 else 0.0)))
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.INCOMPARABLE)
        self.assertIn("Partial distinctness", rep["why"])

    def test_an_ASYMMETRIC_replica_population_is_REPORTED_not_silently_reduced(self):
        """A silently reduced denominator is how 'all replicas differ' gets said about three of them."""
        a = self._member(0, [1, 2, 3], xsec=lambda r, k: np.full(64, 1.0 + r))
        b = self._member(1200, [1, 2], xsec=lambda r, k: np.full(64, 1.5 + r))
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.DISTINCT)
        self.assertIn("asymmetric population", rep["partial"])
        self.assertEqual(rep["n_shared"], 2)
        self.assertIn("asymmetric population", self.S.format_report(v, rep))

    def test_a_TRUNCATED_replica_is_INCOMPARABLE(self):
        """TWO BRANCHES, NOT ONE, AND MY FIRST VERSION OF THIS TEST CONFLATED THEM.

        I truncated a fixture to 60% and asserted "unreadable" or "missing keys". It came back
        `tiny (848 B)` -- because a constant array compresses to ~1.4 kB, so 60% of it is UNDER the
        1024 B floor and the size check fired first. Both rejections are correct and the test was
        wrong: it named one branch and exercised another. The size floor is cheap and fires early; the
        deflate reader is the one that matters for a realistically-sized product, and it gets its own
        test below so neither can pass for the other's reason.
        """
        a = self._member(0, [1], xsec=lambda r, k: np.full(64, 1.0))
        b = self._member(1200, [1], xsec=lambda r, k: np.full(64, 2.0))
        victim = Path(b) / "boot_nd_5d" / "res_boot_1.npz"
        raw = victim.read_bytes()
        victim.write_bytes(raw[:int(len(raw) * 0.6)])
        self.assertLess(victim.stat().st_size, 1024, "this fixture exercises the SIZE FLOOR")
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.INCOMPARABLE)
        self.assertIn("tiny", rep["why"])

    def test_a_TRUNCATED_DEFLATE_STREAM_above_the_size_floor_is_INCOMPARABLE(self):
        """THE BRANCH THAT ACTUALLY MATTERS. A compressed npz can list every key in its header while a
        member's deflate stream is truncated, so a key-presence check passes and `d[k]` raises -- which
        is why `validate_replica` MATERIALIZES every array instead of checking names. Incompressible
        content, and the truncated file is asserted to clear the size floor so it reaches the reader.
        """
        rng = np.random.default_rng(20260818)          # incompressible, so truncation lands >1024 B
        a = self._member(0, [1], xsec=lambda r, k: rng.random(4096))
        b = self._member(1200, [1], xsec=lambda r, k: rng.random(4096))
        victim = Path(b) / "boot_nd_5d" / "res_boot_1.npz"
        raw = victim.read_bytes()
        victim.write_bytes(raw[:int(len(raw) * 0.6)])
        self.assertGreater(victim.stat().st_size, 1024,
                           "the point of this fixture is to get PAST the size floor")
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.INCOMPARABLE)
        self.assertNotIn("tiny", rep["why"], "the size floor must NOT be what caught this")
        self.assertTrue("unreadable" in rep["why"] or "missing keys" in rep["why"], rep["why"])

    def test_a_NON_FINITE_replica_is_INCOMPARABLE(self):
        a = self._member(0, [1], xsec=lambda r, k: np.full(64, 1.0))
        b = self._member(1200, [1],
                         xsec=lambda r, k: np.concatenate([np.full(63, 2.0), [np.nan]]))
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.INCOMPARABLE)
        self.assertIn("non-finite", rep["why"])

    def test_the_three_verdicts_map_to_three_EXIT_CODES(self):
        """A caller checking `!= 0` still behaves correctly; one that wants to distinguish a negative
        RESULT from a broken COMPARISON can."""
        a = self._member(0, [1], xsec=lambda r, k: np.full(64, 1.0))
        b = self._member(1200, [1], xsec=lambda r, k: np.full(64, 2.0))
        args = ["--root-a", a, "--root-b", b, "--offset-a", "0", "--offset-b", "1200"]
        self.assertEqual(self.S.main(args), 0)
        same = self._member(2400, [1], xsec=lambda r, k: np.full(64, 1.0))
        self.assertEqual(self.S.main(["--root-a", a, "--root-b", same,
                                      "--offset-a", "0", "--offset-b", "2400"]), 1)
        self.assertEqual(self.S.main(["--root-a", a, "--root-b", a,
                                      "--offset-a", "0", "--offset-b", "0"]), 2)


    def test_the_CHANGED_BIN_COUNT_ships_its_DENOMINATOR_and_the_denominator_is_the_SUPPORT(self):
        """THE REPORT'S HEADLINE NUMBER WAS WRONG BY CONSTRUCTION UNTIL THIS SHIPPED.

        Stage 0's real output read `changed 10510/65856`, which the mediator reported as "the seed moves
        ~16% of bins". But ~84% of the 65,856-bin 5D grid is EMPTY -- the analysis reports on the `cv > 0`
        mask, 10,694 bins (`analyze_universes_5d.py:160`, and "the same 10694 support" at
        `p4_evidence.py:137`). A bin that is zero in both members CANNOT change, so it is not evidence of
        anything. Against the support the same measurement reads ~98% of the bins that CAN move.

        SHIPPING ONLY THE GRID SIZE MADE A STRONG RESULT LOOK WEAK, which is the rarer direction and the
        reason it would have survived review. BEN-077 against my own report: the ingredient of "changed
        bins" is how many bins were ever in play.
        """
        sparse = np.zeros(64)
        sparse[:8] = 1.0
        moved = sparse.copy()
        moved[:6] = 1.5                                  # 6 of the 8 populated bins move
        a = self._member(0, [1], xsec=lambda r, k: sparse)
        b = self._member(1200, [1], xsec=lambda r, k: moved)
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        self.assertEqual(v, self.S.DISTINCT, rep.get("why"))
        row = rep["replicas"][0]
        # the fixture pads to clear the 1 kB floor, so assert the RELATION rather than literal counts
        self.assertLess(row["support_either"], row["nbins"],
                        "the fixture must be sparse or this test proves nothing")
        self.assertEqual(row["changed_bins"] / row["support_either"],
                         row["changed_frac_of_support"])
        self.assertGreater(row["changed_frac_of_support"],
                           row["changed_bins"] / row["nbins"],
                           "the support-based fraction must EXCEED the grid-based one -- that gap is "
                           "the entire correction")

    def test_the_report_prints_BOTH_denominators_so_neither_reading_is_available_alone(self):
        sparse = np.zeros(64); sparse[:8] = 1.0
        moved = sparse.copy(); moved[:6] = 1.5
        a = self._member(0, [1], xsec=lambda r, k: sparse)
        b = self._member(1200, [1], xsec=lambda r, k: moved)
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        text = self.S.format_report(v, rep)
        self.assertIn("of support", text)
        self.assertIn("[grid", text, "the grid size stays visible; it is just not the denominator")
        self.assertIn("of peak", text,
                      "and max|d| must be labelled as a fraction of the PEAK, not as 'rel'")

    def test_max_delta_over_peak_is_NOT_a_per_bin_relative_error(self):
        """The second misreadable number. `max_rel_delta` divides max|delta| by the PEAK bin value, so
        "0.6-1.2% relative" invites reading it as "bins move by ~1%". It is the largest absolute change
        expressed as a fraction of the largest bin. The median per-bin relative change on the support is
        now shipped beside it, and they differ by construction."""
        x = np.array([100.0] + [1.0] * 63)
        y = x.copy(); y[1:] = 1.5                      # every small bin moves 50%; the peak does not
        a = self._member(0, [1], xsec=lambda r, k: x)
        b = self._member(1200, [1], xsec=lambda r, k: y)
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        row = rep["replicas"][0]
        self.assertLess(row["max_delta_over_peak"], 0.02,
                        "max|d|/peak is small because the peak is large")
        self.assertGreater(row["median_rel_delta_on_support"], 0.2,
                           "while the TYPICAL bin moved a lot -- the two numbers answer different "
                           "questions and only shipping both prevents the substitution")

    def test_the_report_ships_its_INGREDIENTS(self):
        """A verdict-only receipt is unfalsifiable (BEN-077). The report must carry enough that its own
        numbers could contradict each other."""
        a = self._member(0, [1], xsec=lambda r, k: np.full(64, 1.0))
        b = self._member(1200, [1], xsec=lambda r, k: np.full(64, 2.0))
        v, rep = self.S.compare_member_pair(a, b, 0, 1200)
        row = rep["replicas"][0]
        for key in ("nbins", "changed_bins", "max_abs_delta", "scale_max_abs_a", "max_rel_delta",
                    "digest_a", "digest_b", "estimator_seed_a", "estimator_seed_b"):
            self.assertIn(key, row)
        self.assertNotEqual(row["digest_a"], row["digest_b"])
        text = self.S.format_report(v, rep)
        self.assertIn("max|d|", text)
        self.assertIn(row["digest_a"], text, "the digests must reach the human-readable report too")


class TheCompletenessFloorIsMeasured(unittest.TestCase):
    """The mediator ran the 188-universe archive distribution; this pins what it decided.

        present 188/188  NaN 0  min 0.9720202  p05 0.9743379  median 0.9987681
        p95 1.0074093  max 1.0240842   below 0.50: 0   below 0.99: 66
    """

    OBSERVED_MIN, OBSERVED_MAX, BELOW_099 = 0.9720201555, 1.0240842128, 66

    def setUp(self):
        """READ THE CONSTANT, DO NOT IMPORT THE MODULE. `analyze_universes_5d.py:25` is a MODULE-LEVEL
        `import ROOT` and ROOT is absent here -- unlike `unified_throw_cov.py`, whose only ROOT import
        is function-local, which is why that module's guards ARE locally testable. Same repo, opposite
        answer, decided by where the heavy import sits.
        """
        import ast
        src = (ND / "analyze_universes_5d.py").read_text()
        self.consts = {}
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        self.consts[tgt.id] = node.value.value
        self.src = src

    def test_the_floor_is_0_90(self):
        self.assertEqual(self.consts.get("MIN_COMPLETE_5D_UNIVERSE"), 0.90)

    def test_the_floor_is_NOT_VACUOUS_but_clears_the_observed_population(self):
        """Both directions. A floor below every conceivable value is an unexercised guard; a floor
        inside the observed spread is a quality gate on a population nobody measured."""
        f = self.consts["MIN_COMPLETE_5D_UNIVERSE"]
        self.assertLess(f, self.OBSERVED_MIN, "must accept every healthy archive universe")
        self.assertGreater(f, 0.0, "must be capable of firing at all")
        spread = self.OBSERVED_MAX - self.OBSERVED_MIN
        margin = self.OBSERVED_MIN - f
        self.assertGreater(margin, spread,
                           f"margin {margin:.4f} must exceed the observed spread {spread:.4f} -- a "
                           "member at 42+k has no reason to occupy the archive's range, and a floor "
                           "inside one spread-width starts clipping correct work")

    def test_the_FPS_floor_would_have_been_VACUOUS_here(self):
        """Not wrong -- unexercised. 0.50 sits 0.47 below the observed minimum and could never fire,
        which is why declining to inherit it was right for a reason that is now measured.

        `fps_unfold_complete.py` also imports ROOT at module level, so the constant is read from source
        for the same reason as above.
        """
        import ast
        fps = {}
        for node in ast.walk(ast.parse((ND / "fps_unfold_complete.py").read_text())):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        fps[tgt.id] = node.value.value
        self.assertEqual(fps["MIN_COMPLETE"], 0.50)
        self.assertLess(fps["MIN_COMPLETE"], self.OBSERVED_MIN - 0.4)

    def test_0_99_IS_THE_TRAP_and_the_docstring_says_so(self):
        """The round number anyone reaches for rejects a THIRD of the healthy archive."""
        self.assertGreater(0.99, self.OBSERVED_MIN,
                           "0.99 is above the observed minimum, hence rejects real universes")
        src = self.src
        self.assertIn("0.99 IS THE TRAP", src)
        self.assertIn("66 OF 188", src, "the cost of the trap must be stated, not implied")

    def test_only_a_ONE_SIDED_floor_is_meaningful_because_the_ratio_EXCEEDS_ONE(self):
        """39 of 188 exceed unity, so an upper bound or an |x-1| tolerance would reject a fifth of the
        archive. Recorded because 'completeness' reads as a fraction bounded by 1 and is not."""
        self.assertGreater(self.OBSERVED_MAX, 1.0)
        self.assertIn("NOT BOUNDED BY 1", self.src)

    def test_the_NaN_branch_is_UNREALIZED_IN_THE_ARCHIVE(self):
        """0 of 188. So the hole closed at aae49f2a would have FIRST APPEARED IN A MEMBER, silently,
        with no archive precedent -- the failure mode with no natural discoverer."""
        self.assertIn("UNREALIZED IN THE ARCHIVE", self.src)


class AnchorComparatorB2(unittest.TestCase):
    """B2. ROOT is absent here, so the reader is injected and only the DECISIONS are exercised."""

    def setUp(self):
        import mii_anchor_comparator as B
        self.B = B
        self.C = np.array([1.0, 2.0, 3.0, 4.0])          # trace 10
        self.MS = np.array([0.3, 0.4])                   # norm 0.5

    #: THE FIXTURE'S OWN EXPECTED SIZES. The real ones are 10,694 and 10,694^2 -- 114 million elements,
    #: which no unit test allocates. So the fixture declares its own, and the COVERAGE MECHANISM is then
    #: exercised at 100% here and at <100% in the dedicated partial test. Patching the expectation is
    #: honest; weakening the check to accommodate a small fixture would not be.
    FIXTURE_SIZES = {"C_unified": 4, "C_blocksum": 4, "C_cross": 4, "hJointMeanShift": 2,
                     "hCov_combined5d_total_uthrow": 1}

    def setUpSizes(self):
        """IDEMPOTENT, and it was not.

        `_throw()` calls this, and some tests call it directly as well -- so it ran twice. The second
        call's `dict(EXPECTED_ELEMENTS)` captured THE FIRST CALL'S PATCH as the "original", and the
        cleanup then restored the module global to a PATCHED state that LEAKED INTO THE NEXT TEST. That
        is how `test_a_key_with_NO_derived_expectation` came to see C_unified == 4: a fixture corrupting
        its own restore, which reads as a defect in the code under test.
        A SAVE-AND-RESTORE HELPER MUST BE IDEMPOTENT OR IT IS A STATE LEAK WITH EXTRA STEPS.
        """
        import mii_root_payload_classes as classes
        if getattr(self, "_saved_sizes", None) is None:
            self._saved_sizes = dict(classes.EXPECTED_ELEMENTS)
            saved = self._saved_sizes
            self.addCleanup(lambda: (classes.EXPECTED_ELEMENTS.clear(),
                                     classes.EXPECTED_ELEMENTS.update(saved)))
        classes.EXPECTED_ELEMENTS.update(self.FIXTURE_SIZES)

    def _throw(self, **over):
        """(scalars, diagonals, matrices) -- the THREE-tuple the H1 fix requires.

        `diagonals` is for the recomputation half; `matrices` is what the comparison digests. The reader
        returning one array for both roles WAS the H1 defect, so the fixture must distinguish them too or
        it cannot represent the shape under test.
        """
        self.setUpSizes()
        sc = {"sqrt_tr_unified": float(np.sqrt(10.0)), "sqrt_tr_block": float(np.sqrt(10.0)),
              "joint_mean_shift_norm": 0.5, "n_throws": 160, "fixed_seed_null_checked": 0}
        sc.update(over)
        di = {"C_unified": self.C, "C_blocksum": self.C, "C_cross": self.C,
              "hJointMeanShift": self.MS}
        # matrices are (sha256_hex, n_elements) after the memory restructure -- C corrected the cost to
        # ~2 GB per LIVE TH2D (ROOT resides sumw2 alongside contents), so the reader must not retain
        # arrays at all. The fixture mirrors that shape or it is not testing the reader's contract.
        mx = {k: (self.B.digest(v), int(v.size)) for k, v in di.items()}
        return sc, di, mx

    def _reader(self, member_over=None, drop_diag=()):
        arch = self._throw()
        over = {"estimator_seed": 1000, "draw_seed": 1000, "est_seed_offset": 0,
                "est_seed_offset_declared": 1}
        over.update(member_over or {})          # build THEN update, so member_over can override
        m_sc, m_di, m_mx = self._throw(**over)
        m_di = {k: v for k, v in m_di.items() if k not in drop_diag}
        m_mx = {k: v for k, v in m_mx.items() if k not in drop_diag}
        return lambda p: (arch if p == "A" else (m_sc, m_di, m_mx))

    def _go(self, **kw):
        fixture = {k: v for k, v in kw.items() if k in ("member_over", "drop_diag")}
        return self.B.compare_files("uq_5d/unified_throw_cov_5d.root", "A", "M", 0,
                                    read_keys=self._reader(**fixture),
                                    **{k: v for k, v in kw.items() if k not in fixture}, archive_date=(2026, 7, 14))

    def test_a_SELF_CONSISTENT_k0_anchor_PASSES(self):
        v, lines = self._go()
        self.assertEqual(v, "PASS", [l for l in lines if "OK" not in l])
        self.assertEqual(sum(1 for l in lines if l.startswith("[recompute] OK")), 3)

    def test_a_FILE_THAT_CONTRADICTS_ITSELF_fails_which_equality_could_NEVER_catch(self):
        """BEN-077's whole point: the archive and the member can agree exactly on a scalar and both be
        inconsistent with their own matrices. Equality is necessary and not sufficient."""
        v, lines = self._go(member_over={"sqrt_tr_unified": 99.0})
        self.assertEqual(v, "FAIL")
        self.assertTrue(any("CONTRADICTS ITSELF" in l for l in lines), lines)

    def test_a_MISSING_INGREDIENT_fails_rather_than_being_skipped(self):
        """A scalar whose ingredient is gone is UNVERIFIABLE, and unverifiable must not read as fine."""
        v, lines = self._go(drop_diag=("C_unified",))
        self.assertEqual(v, "FAIL")
        self.assertTrue(any("ingredient 'C_unified' absent" in l for l in lines), lines)

    def test_an_UNDECLARED_anchor_fails_on_IDENTITY_not_on_payload(self):
        v, lines = self._go(member_over={"est_seed_offset_declared": 0})
        self.assertEqual(v, "FAIL")
        self.assertTrue(any("UNHOOKED" in l for l in lines), lines)

    def test_rtol_DEFAULTS_TO_BIT_EXACT(self):
        """A tolerance is a decision, not a default. This is the gate that decides whether the archive
        was reproduced; a silent 1e-9 would make 'reproduced' mean something nobody chose."""
        import inspect
        sig = inspect.signature(self.B.compare_files)
        self.assertEqual(sig.parameters["rtol"].default, 0.0)
        # AND MY FIRST VERSION OF THIS TEST MEASURED THE WRONG THING. I perturbed only the member's
        # scalar, so it failed the PAYLOAD equality against the archive -- a different check, decided
        # before rtol is ever consulted. `rtol` governs the RECOMPUTATION comparison only. So both
        # sides carry the perturbed value and the archive equality holds; what is left is the file
        # disagreeing with its own matrix by 1e-12.
        eps = float(np.sqrt(10.0)) * (1 + 1e-12)
        both = lambda p: (self._throw(sqrt_tr_unified=eps) if p == "A"
                          else self._throw(sqrt_tr_unified=eps, estimator_seed=1000, draw_seed=1000,
                                           est_seed_offset=0, est_seed_offset_declared=1))   # 3-tuple
        go = lambda **kw: self.B.compare_files("uq_5d/unified_throw_cov_5d.root", "A", "M", 0,
                                               read_keys=both, **kw, archive_date=(2026, 7, 14))
        self.assertEqual(go()[0], "FAIL", "bit-exact by default: 1e-12 self-inconsistency is a FAIL")
        self.assertEqual(go(rtol=1e-9)[0], "PASS", "and an EXPLICIT tolerance admits it")

    def test_the_report_does_not_say_NOT_PERFORMED_and_OK_about_one_key(self):
        """The table emits the DEMAND and the comparator emits the DISCHARGE. Printing both left a
        report contradicting itself three lines apart, which is worse than either alone."""
        v, lines = self._go()
        for key in ("sqrt_tr_unified", "sqrt_tr_block", "joint_mean_shift_norm"):
            demanded = [l for l in lines if "RECOMPUTATION NOT PERFORMED" in l and l.startswith(key)]
            self.assertEqual(demanded, [], f"{key}: superseded demand still printed")

    def test_the_UNRECOMPUTABLE_keys_BLOCK_unless_explicitly_acknowledged(self):
        """A key whose ingredients are not in the file cannot satisfy BEN-077, and the failure must be
        loud. Silently treating it as checked is the exact shape of an unfalsifiable receipt."""
        # MEASURED ON AN ARTIFACT WHOSE IDENTITY CAN BE SATISFIED, and my first version could not be.
        # I used the adopted root, which today carries NO identity stamp -- so it FAILS on identity
        # before recomputation is ever reached, and the test would have "passed" for the wrong reason
        # had I asserted FAIL. The throw root stamps all four keys, so `fixed_seed_null_norm` -- also
        # NOT_RECOMPUTABLE, ingredients unwritten -- is the clean case.
        # ON BOTH SIDES. My previous attempt put the key only on the member, so the ARCHIVE KEY MAP
        # branch fired first -- "present in member, absent from archive, unexplained" -- and the test
        # measured that instead. The archive DOES carry `fixed_seed_null_norm` (1.9706093906025077e-50,
        # read on the cluster), so the fixture must too or it is not the archive.
        NULL = 1.9706093906025077e-50
        both = lambda p: (self._throw(fixed_seed_null_norm=NULL) if p == "A"
                          else self._throw(fixed_seed_null_norm=NULL, estimator_seed=1000,
                                           draw_seed=1000, est_seed_offset=0,
                                           est_seed_offset_declared=1))   # 3-tuple
        go = lambda **kw: self.B.compare_files("uq_5d/unified_throw_cov_5d.root", "A", "M", 0,
                                               read_keys=both, **kw, archive_date=(2026, 7, 14))
        v, lines = go()
        self.assertEqual(v, "INCOMPLETE",
                         [l for l in lines if not l.startswith("[recompute] OK")])
        self.assertTrue(any("BLOCKED" in l and "fixed_seed_null_norm" in l for l in lines), lines)
        self.assertTrue(any("CANNOT BE SATISFIED" in l for l in lines))
        full = sorted(self.B.declared_unrecomputable())
        self.assertEqual(go(acknowledge_unrecomputable=full)[0], "PASS",
                         "the EXACT declared list lets it through, RECORDED as unverified")

    def test_an_ADOPTED_root_reports_IDENTITY_UNCHECKABLE_not_an_UNAVOIDABLE_FAIL(self):
        """H3 CHANGED THIS TEST'S PREMISE, AND THE OLD VERSION WAS DEFENDING THE DEFECT.

        It asserted FAIL because a member's adopted root cannot satisfy `anchor_identity` --
        `adopt_unified_5d.py` stamps nothing. The observation is right; making it a FAIL was not. D's
        reason is the pressure-toward-green risk arriving from the other side: AT STAGE 1 AN UNAVOIDABLE
        FAIL IS THE THING MOST LIKELY TO GET THE GATE ROUTED AROUND. Three of five artifacts emitted
        three identity problems every run and failed regardless of payload, which teaches the caller to
        skip the check -- and a skipped check protects nothing.

        Now UNCHECKABLE is reported explicitly, the artifact still cannot be admitted (remedy (A) is
        C's ruling, and C has since WIDENED it to LATERAL_CV as well), and the verdict reflects the
        payload questions rather than an unfixable one.
        """
        self.setUpSizes()
        keys = {"sqrt_tr_old": 1.0, "sqrt_tr_new": 2.0}
        diag = {"hCov_combined5d_total_uthrow": np.array([4.0])}
        v, lines = self.B.compare_files("adopted_uthrow.root", "A", "M", 0,
                                        read_keys=lambda p: (
                                            keys, diag,
                                            {k: (self.B.digest(v), int(v.size))
                                             for k, v in diag.items()}),
                                        archive_date=(2026, 7, 14))
        self.assertEqual(v, "INCOMPLETE",
                         "not FAIL -- an unavoidable FAIL gets routed around; and not PASS either")
        unchk = [l for l in lines if l.startswith("[identity] UNCHECKABLE")]
        self.assertTrue(unchk, lines)
        self.assertIn("stamps no identity key", unchk[0])
        self.assertIn("NOT a pass", unchk[0], "the artifact still cannot be admitted")
        self.assertIn("remedy (A)", unchk[0], "and the reader must be told what would fix it")
        self.assertFalse(any("ABSENT FROM MEMBER" in l for l in lines),
                         "identity keys must not be demanded of a writer that cannot emit them")

    def test_identity_IS_still_enforced_where_the_writer_DOES_stamp(self):
        """CONTROL for the test above. Relaxing three artifacts must not relax the two that CAN carry
        identity -- without this, H3's fix could have disabled the check everywhere and nothing would
        have noticed."""
        import mii_root_payload_classes as classes
        self.assertTrue(classes.identity_is_checkable("uq_5d/unified_throw_cov_5d.root"))
        self.assertTrue(classes.identity_is_checkable("sweep_universe.root"))
        for a in ("adopted_uthrow.root", "adopted_uthrow_cvcentered.root", "lateral_cv.root"):
            self.assertFalse(classes.identity_is_checkable(a),
                             f"{a} carries no identity key -- C widened remedy (A) to cover LATERAL_CV "
                             "as well, on D's enumeration rather than mine")
        v, lines = self._go(member_over={"est_seed_offset_declared": 0})
        self.assertEqual(v, "FAIL", "the throw root DOES stamp, so an undeclared offset still fails")
        self.assertTrue(any("UNHOOKED" in l for l in lines), lines)

    def test_an_ADOPTED_ROOT_CANNOT_carry_an_identity_stamp_TODAY_and_the_table_says_so(self):
        """A REAL GAP THE TABLE SURFACED WHILE I WAS WRITING THIS TEST, and I am recording it rather
        than patching around it.

        My first version handed the adopted artifact `estimator_seed`/`est_seed_offset{,_declared}` and
        `classify()` refused: those keys HAVE NO CLASS in `ADOPTED_UTHROW`. That is CORRECT, because
        `adopt_unified_5d.py` writes none of them (`STAMP_COVERAGE == 0`) -- so a member's adopted root
        cannot be told from the archive's by its own contents, which IS the fifth gate. The fix is not
        to add speculative rows to the table; it is remedy (A) in the writer, which is C's call.

        So the table stays honest and the comparator FAILS CLOSED on a key nobody has classified --
        which is exactly what should happen the moment (A) lands and adoption starts stamping.
        """
        import mii_root_payload_classes as classes
        for key in ("estimator_seed", "est_seed_offset", "est_seed_offset_declared"):
            with self.subTest(key=key), self.assertRaises(SystemExit) as cm:
                classes.classify("adopted_uthrow.root", key)
            self.assertIn("NO CLASS", cm.exception.fail_message)
        self.assertEqual(cm.exception.code, 2,
                         "H4: a fail-closed exit must be 2, which main() maps to FAIL. Exit 1 is INCOMPLETE, and a driver treating rc 1 as continue walks past a corrupt archive.")
        self.assertEqual(classes.STAMP_COVERAGE["adopt_unified_5d.py"], 0,
                         "and the reason the table lacks them is that the writer lacks them")
        # the throw root, by contrast, DOES classify all three -- so this is a per-writer gap, not a
        # hole in the table's design
        for key in ("estimator_seed", "est_seed_offset", "est_seed_offset_declared"):
            self.assertEqual(classes.classify("uq_5d/unified_throw_cov_5d.root", key),
                             classes.PROVENANCE)

    def test_THE_BARS_OPERAND_IS_NOT_RECOMPUTABLE_and_the_table_says_why(self):
        """THE FINDING. `sqrt_tr_old` is the predeclared bar's operand and its sole ingredient is
        `hCov_combined5d_total` in the 41.44 GB intermediate C ruled need not be retained. C's argument
        was that the bar's operands live downstream in the 892 MB adopted roots -- true of
        `sqrt_tr_new`, false of `sqrt_tr_old`."""
        how, kind, why = self.B.RECOMPUTABILITY["sqrt_tr_old"]
        self.assertEqual(how, self.B.NOT_RECOMPUTABLE)
        self.assertEqual(kind, self.B.WRITER_GAP,
                         "a WRITER GAP, not a mathematical impossibility -- diag_comb is already in "
                         "memory at adopt_unified_5d.py:128, so C's 11g remedy is a WRITE")
        self.assertIn("41.44 GB", why)
        self.assertEqual(self.B.RECOMPUTABILITY["sqrt_tr_new"][0], self.B.IN_FILE,
                         "the OTHER operand IS recomputable, which is what makes this specific")

    def test_only_FOUR_of_the_recompute_keys_are_IN_FILE(self):
        """C classified seven scalars as mandatory-recomputation; four can be recomputed from the file
        that carries them. Derived, not assumed, and pinned so the count cannot drift silently."""
        by = {}
        for k, (how, _kind, _why) in self.B.RECOMPUTABILITY.items():
            by.setdefault(how, []).append(k)
        self.assertEqual(len(by[self.B.IN_FILE]), 4)
        self.assertEqual(sorted(by[self.B.NOT_RECOMPUTABLE]),
                         ["fixed_seed_null_norm", "globalCompleteness", "sqrt_tr_old"])
        for k in self.B.RECOMPUTE:
            self.assertEqual(self.B.RECOMPUTABILITY[k][0], self.B.IN_FILE,
                             f"{k} has a recompute implementation, so it must be classified IN_FILE")
        for k, (how, _kind, _why) in self.B.RECOMPUTABILITY.items():
            if how is self.B.IN_FILE:
                self.assertIn(k, self.B.RECOMPUTE,
                              f"{k} is classified IN_FILE but has no implementation -- the claim and "
                              "the capability must not drift apart")

    def test_the_TWO_HALVES_use_DIFFERENT_arrays_which_is_H1s_whole_lesson(self):
        """THIS TEST'S PREVIOUS PREMISE WAS THE DEFECT. It asserted the TH2D reader "takes the diagonal
        only", on the grounds that `trace(C) == sum(diag(C))` so no matrix need be materialised -- and
        that reasoning is sound FOR THE RECOMPUTATION and false for the COMPARISON, which is what H1 was.
        The old assertion literally required the bug.

        Two facts now, one per half:
          RECOMPUTE   still uses the diagonal -- a sqrt-trace never needs the full matrix
          COMPARE     uses the FULL content array, and `_th2_content` exists to produce it
        And there was never a memory argument: `key.ReadObj()` materialises the matrix regardless
        (D measured peak RSS 3,773 MB), so the diagonal saved numpy memory and cost the comparison.
        """
        self.assertEqual(self.B._sqrt_trace_from_diag(np.array([9.0, 16.0])), 5.0)
        src = (ND / "mii_anchor_comparator.py").read_text()
        self.assertIn("def _th2_content(", src, "the full-matrix reader must exist")
        self.assertIn("[1:ny + 1, 1:nx + 1]", src,
                      "content bins only -- under/overflow excluded, and ALL of them")
        self.assertIn("np.diagonal(arr)", src,
                      "the diagonal is DERIVED from the full array, not read instead of it")
        # and the summation-route warning D asked for must be present at the recompute helper
        self.assertIn("PROPERTY OF THE SUMMATION ROUTE", src)

    def test_a_PARTIAL_comparison_FAILS_and_says_what_fraction(self):
        """H1's remedy, in the direction it acts. A payload comparison covering 1 element in 114 million
        must FAIL, and the verdict line must carry the fraction -- D's non-optional ask, and the part
        that outlives any particular reader."""
        import mii_root_payload_classes as classes
        reader = self._reader()            # builds the fixture (and patches the small sizes) FIRST
        classes.EXPECTED_ELEMENTS["C_unified"] = 114361636      # then the REAL size, so it survives
        v, lines = self.B.compare_files("uq_5d/unified_throw_cov_5d.root", "A", "M", 0,
                                        read_keys=reader, archive_date=(2026, 7, 14))
        self.assertEqual(v, "FAIL")
        cov = [l for l in lines if l.startswith("[coverage] C_unified")]
        self.assertTrue(cov, lines)
        self.assertIn("of 114361636 elements", cov[0])
        self.assertIn("PARTIAL COMPARISON", cov[0])
        self.assertTrue(any("PARTIAL COMPARISON" in l and "BIT-EXACT OVER THE WHOLE ARRAY" in l
                            for l in lines),
                        "and it must be a FINDING, not merely a footnote")

    def test_a_key_with_NO_derived_expectation_is_reported_not_asserted(self):
        """My first version of the coverage check used ONE global constant and was wrong about it --
        `hXSecND_flat` is on the 65,856 GRID while every covariance is on the 10,694 SUPPORT. Asserting a
        number I have not read out of a writer is exactly how the wrong constant arrived. So an unlisted
        key gets its coverage printed and NOT asserted."""
        # NO setUpSizes HERE -- this test reads the SHIPPED table, and calling the fixture would have it
        # assert against the fixture's own small sizes. That is exactly what it did at first: 4 != 114361636,
        # a test that looked like it had caught a wrong constant and had only patched one.
        import mii_root_payload_classes as classes
        self.assertNotIn("hXSec_pt", classes.EXPECTED_ELEMENTS)
        self.assertEqual(classes.EXPECTED_ELEMENTS["hXSecND_flat"], classes.FLAT_NBINS,
                         "hXSecND_flat is len(xsec.ravel()) -- the FULL GRID (sweep_bank_5d.py:278,291)")
        self.assertEqual(classes.EXPECTED_ELEMENTS["C_unified"], classes.REPORTED_NBINS ** 2,
                         "a covariance is nrep x nrep on the SUPPORT (unified_throw_cov.py:348,522)")
        self.assertNotEqual(classes.EXPECTED_ELEMENTS["hXSecND_flat"],
                            classes.EXPECTED_ELEMENTS["hInflation_g"],
                            "two different dimensions in one file family is the whole reason a single "
                            "global constant was wrong about both")


class RecomputabilityIsADeclaredAttribute(unittest.TestCase):
    """C ruled: NO FOURTH CLASS -- `recomputable: yes|no` as a required attribute on PAYLOAD.

    Its reason is structural and worth keeping: each of the three classes names a COMPARISON RULE
    (bit-exact, equal, superset) and "not recomputable" is not one, because those keys still compare
    bit-exact. What differs is whether the INGREDIENT CHECK is available.
    """

    def setUp(self):
        import mii_anchor_comparator as B
        self.B = B

    def test_every_entry_declares_how_kind_and_reason(self):
        self.assertEqual(self.B.assert_reasons_are_stated(), 9)

    def test_a_BARE_no_IS_THE_FAIL_CLOSED_CASE(self):
        """A `no` without a stated kind reads as a law of nature and freezes a writer gap forever."""
        saved = dict(self.B.RECOMPUTABILITY)
        try:
            self.B.RECOMPUTABILITY["invented"] = (self.B.NOT_RECOMPUTABLE, None, "")
            with self.assertRaises(SystemExit) as cm:
                self.B.assert_reasons_are_stated()
            self.assertIn("law of nature", cm.exception.fail_message)
        finally:
            self.B.RECOMPUTABILITY.clear(); self.B.RECOMPUTABILITY.update(saved)

    def test_a_no_with_a_KIND_but_NO_REASON_also_fails(self):
        saved = dict(self.B.RECOMPUTABILITY)
        try:
            self.B.RECOMPUTABILITY["invented"] = (self.B.NOT_RECOMPUTABLE, self.B.WRITER_GAP, "short")
            with self.assertRaises(SystemExit) as cm:
                self.B.assert_reasons_are_stated()
            self.assertIn("no usable reason", cm.exception.fail_message)
        finally:
            self.B.RECOMPUTABILITY.clear(); self.B.RECOMPUTABILITY.update(saved)

    def test_every_no_DISTINGUISHES_a_writer_gap_from_an_impossibility(self):
        """C's requirement, and its purpose is that recording WHICH KIND determines whether anyone can
        ever close it. All three of today's `no`s are WRITER GAPS -- i.e. all three are closable."""
        for key in self.B.declared_unrecomputable():
            how, kind, why = self.B.RECOMPUTABILITY[key]
            with self.subTest(key=key):
                self.assertIn(kind, (self.B.WRITER_GAP, self.B.IMPOSSIBLE))
                self.assertEqual(kind, self.B.WRITER_GAP,
                                 f"{key} is a writer gap; if this ever becomes IMPOSSIBLE the reason "
                                 "must say what changed")
                self.assertIn("writ", why.lower(),
                              "the reason must name the unwritten ingredient, not just assert absence")

    def test_the_ACKNOWLEDGEMENT_IS_A_CLOSED_SET_not_a_boolean(self):
        """C's strengthening. A blanket flag lets a FUTURE `no` ride in silently: someone adds a key,
        declares it unrecomputable, and every existing invocation swallows it without anyone deciding.
        Same defect as the comparator being blind to a key absent from both files."""
        self.assertEqual(sorted(self.B.declared_unrecomputable()),
                         ["fixed_seed_null_norm", "globalCompleteness", "sqrt_tr_old"])
        import inspect
        self.assertIsNone(inspect.signature(self.B.compare_files)
                          .parameters["acknowledge_unrecomputable"].default,
                          "the default must be 'acknowledge nothing', not False-as-boolean")

    def _reader(self):
        C = np.array([1.0, 2.0, 3.0, 4.0])
        MS = np.array([0.3, 0.4])
        def mk(**over):
            sc = {"sqrt_tr_unified": float(np.sqrt(10.0)), "sqrt_tr_block": float(np.sqrt(10.0)),
                  "joint_mean_shift_norm": 0.5, "n_throws": 160, "fixed_seed_null_checked": 1,
                  "fixed_seed_null_norm": 1.9706093906025077e-50}
            sc.update(over)
            d = {"C_unified": C, "C_blocksum": C, "C_cross": C, "hJointMeanShift": MS}
            import mii_anchor_comparator as _B
            return sc, d, {k: (_B.digest(v), int(v.size)) for k, v in d.items()}
        import mii_root_payload_classes as classes
        saved = dict(classes.EXPECTED_ELEMENTS)
        classes.EXPECTED_ELEMENTS.update({"C_unified": 4, "C_blocksum": 4, "C_cross": 4,
                                          "hJointMeanShift": 2})
        self.addCleanup(lambda: (classes.EXPECTED_ELEMENTS.clear(),
                                 classes.EXPECTED_ELEMENTS.update(saved)))
        return lambda p: (mk() if p == "A" else
                          mk(estimator_seed=1000, draw_seed=1000, est_seed_offset=0,
                             est_seed_offset_declared=1))

    def test_a_SUBSET_acknowledgement_is_REJECTED(self):
        """A subset would leave a blocked key looking acknowledged."""
        with self.assertRaises(SystemExit) as cm:
            self.B.compare_files("uq_5d/unified_throw_cov_5d.root", "A", "M", 0,
                                 read_keys=self._reader(),
                                 acknowledge_unrecomputable=["globalCompleteness"], archive_date=(2026, 7, 14))
        self.assertIn("must match the DECLARED", cm.exception.fail_message)
        self.assertIn("missing", cm.exception.fail_message, "and it must NAME what is missing")

    def test_a_SUPERSET_acknowledgement_is_ALSO_rejected(self):
        """A superset names a key nobody declared -- a sign the caller is working from a stale list, and
        the direction that would otherwise pass silently."""
        with self.assertRaises(SystemExit) as cm:
            self.B.compare_files("uq_5d/unified_throw_cov_5d.root", "A", "M", 0,
                                 read_keys=self._reader(), archive_date=(2026, 7, 14),
                                 acknowledge_unrecomputable=sorted(
                                     self.B.declared_unrecomputable()) + ["not_a_key"])
        self.assertIn("extra", cm.exception.fail_message)

    def test_the_EXACT_set_is_accepted_and_the_keys_are_LABELLED_unverified(self):
        """Unverified-and-LABELLED versus unverified-and-indistinguishable-from-verified is the whole
        distinction. PASS is allowed; silence is not."""
        v, lines = self.B.compare_files(
            "uq_5d/unified_throw_cov_5d.root", "A", "M", 0, read_keys=self._reader(),
            archive_date=(2026, 7, 14),
            acknowledge_unrecomputable=sorted(self.B.declared_unrecomputable()))
        self.assertEqual(v, "PASS")
        self.assertTrue(any("UNVERIFIED (acknowledged)" in l and "fixed_seed_null_norm" in l
                            for l in lines),
                        f"an acknowledged key must still be LABELLED in the report: {lines}")

    def test_WITHOUT_the_flag_the_same_run_is_INCOMPLETE(self):
        """The control: if this were PASS too, the flag would be decorative."""
        v, _ = self.B.compare_files("uq_5d/unified_throw_cov_5d.root", "A", "M", 0,
                                    read_keys=self._reader(), archive_date=(2026, 7, 14))
        self.assertEqual(v, "INCOMPLETE")

    def test_an_UNDECLARED_key_in_RECOMPUTE_REQUIRED_fails_closed(self):
        """Declared in the enumeration, never DISCOVERED at comparison time -- so a recompute-required
        key with no RECOMPUTABILITY row must not silently default to anything."""
        import mii_root_payload_classes as classes
        for key in classes.RECOMPUTE_REQUIRED:
            with self.subTest(key=key):
                self.assertIn(key, self.B.RECOMPUTABILITY,
                              f"{key} is RECOMPUTE_REQUIRED with no declared recomputability")


class SubstitutionFenceS1(unittest.TestCase):
    """S1. The driver's `preflight_launcher()` was TAUTOLOGICAL -- called only on names from the driver's
    own allowlist, so it verified that the launchers it chose are the launchers it chose. And the driver
    does not submit; the printed commands execute outside it. C ruled the fence moves INTO the launchers,
    because THE ONLY PLACE A SUBSTITUTION CAN BE CAUGHT IS INSIDE THE THING SUBSTITUTED IN.
    """

    def _sh(self):
        import subprocess
        out = subprocess.run(["git", "ls-files", "nd-unfolding/*.sh"], capture_output=True, text=True,
                             cwd=str(ND.parent)).stdout.split()
        return {f: (ND.parent / f).read_text(errors="replace") for f in out}

    #: `lib_*.sh` DEFINE the two symbols and are not launchers. Excluded EXPLICITLY, by rule, because
    #: the alternative bit me: see `_partition`.
    DEFINITION_PREFIX = "lib_"

    def _partition(self):
        """Partition LAUNCHERS -- comments stripped, definition files excluded by rule.

        TWO DEFECTS OF MINE, BOTH FOUND BY THIS TEST FAILING AFTER A REBASE, AND BOTH ARE THE DAY'S
        FAMILY:

        (1) THE MATCH READ PROSE. `lib_substitution_fence.sh` landed in BOTH sets because its own comment
            says "this is the MIRROR of `mr_require_valid_offset`". My own explanatory comment classified
            my own library as a hooked launcher. That is `BEN-482` in the file I wrote to close S1, and
            the remedy is `BEN-482`'s own: strip comments before matching.

        (2) THE TEST PASSED THE FIRST TIME FOR A REASON THAT HAD NOTHING TO DO WITH CORRECTNESS.
            I ran the partition BEFORE committing `lib_substitution_fence.sh`, so `git ls-files` could
            not see it and it was absent from the corpus entirely. `total` read 262. After the commit and
            the rebase it reads 265, the file appears, and it appears in BOTH.
            **`git ls-files` CANNOT SEE WHAT YOU HAVE NOT ADDED, so a corpus test measured before its own
            commit is measured against a tree that will never exist again.** Measure after the commit.

        The exclusion is by RULE rather than by name-list so a third library does not silently rejoin the
        launcher population -- and it is asserted below, so the rule cannot quietly widen either.
        """
        hooked, fenced, both, neither = [], [], [], []
        for f, raw in self._sh().items():
            if f.split("/")[-1].startswith(self.DEFINITION_PREFIX):
                continue
            t = "\n".join(l for l in raw.split("\n") if not l.lstrip().startswith("#"))
            h, fe = "mr_require_valid_offset" in t, "mr_fence_unhooked" in t
            (both if (h and fe) else hooked if h else fenced if fe else neither).append(f)
        return sorted(hooked), sorted(fenced), sorted(both), sorted(neither)

    def test_the_DEFINITION_FILES_are_excluded_BY_RULE_and_are_exactly_two(self):
        """The exclusion must not become a place to hide a launcher. Two files, both `lib_*`, both of
        which DEFINE a symbol rather than guarding an output with it."""
        defs = sorted(f for f in self._sh() if f.split("/")[-1].startswith(self.DEFINITION_PREFIX))
        self.assertEqual(defs, ["nd-unfolding/lib_member_resume.sh",
                                "nd-unfolding/lib_substitution_fence.sh"])
        for d in defs:
            body = (ND.parent / d).read_text(errors="replace")
            self.assertIn("()", body, f"{d} must be a definition file")
            self.assertNotIn("#SBATCH", body, f"{d} must not be a launcher")

    def test_comments_are_STRIPPED_before_matching_and_it_MATTERS_here(self):
        """Not hypothetical: `lib_substitution_fence.sh` names `mr_require_valid_offset` in prose to
        explain the mirrored polarity, and that comment is worth keeping. The matcher must be the thing
        that changes, not the comment -- same conclusion as `BEN-482` reached about a docstring."""
        raw = (ND / "lib_substitution_fence.sh").read_text()
        self.assertIn("mr_require_valid_offset", raw, "the prose mention is deliberate")
        stripped = "\n".join(l for l in raw.split("\n") if not l.lstrip().startswith("#"))
        self.assertNotIn("mr_require_valid_offset", stripped,
                         "and it exists ONLY in a comment, so stripping removes it entirely")

    def test_ALL_NINE_hazard_launchers_carry_the_fence(self):
        import seed_offset_policy as sp
        _, fenced, _, _ = self._partition()
        self.assertEqual(set(fenced), {str(x) for x in sp.FROZEN_SUBSTITUTION_HAZARDS})
        self.assertEqual(len(fenced), 9,
                         "NINE, not six -- measured from FROZEN_SUBSTITUTION_HAZARDS rather than "
                         "recalled from a message")

    def test_the_two_sets_are_DISJOINT(self):
        """A launcher in both would be asserting it has an offset hook AND that it has none."""
        _, _, both, _ = self._partition()
        self.assertEqual(both, [], f"launchers in BOTH sets: {both}")

    def test_the_HOOKED_set_is_EXACTLY_the_driver_legs(self):
        """Closed-set on the other side: every one of the driver's seven legs must be hooked, and no
        other launcher may be. The libraries that DEFINE the symbols are excluded by rule."""
        import mii_seed_offset_driver as d
        hooked, _, _, _ = self._partition()
        vals = list(d.LEG_LAUNCHERS.values())
        flat = []
        for v in vals:
            flat.extend(v if isinstance(v, (list, tuple)) else [v])
        legs = {f if f.startswith("nd-unfolding/") else "nd-unfolding/" + f for f in map(str, flat)}
        self.assertEqual(len(legs), 7)
        import seed_offset_policy as sp
        consumers = {"nd-unfolding/" + c for c in sp.MEMBER_LOCAL_CONSUMERS}
        self.assertEqual(set(hooked), legs | consumers,
                         "the hooked set is EXACTLY the seven driver LEGS plus the DECLARED member-local "
                         "CONSUMERS -- declared, not 'whatever happens to be hooked', or the set is not "
                         "closed and absorbs a mistake silently")
        self.assertEqual(legs - set(hooked), set(), "every leg launcher must require a valid offset")
        self.assertEqual(consumers - set(hooked), set(),
                         "every declared consumer must actually be hooked")
        self.assertEqual(legs & consumers, set(),
                         "a launcher is a producer or a consumer, not both")

    def test_the_UNCLASSIFIED_REMAINDER_IS_PINNED_because_it_is_the_real_exposure(self):
        """245 tracked shell files are in NEITHER set, and that number is the honest statement of what
        S1 does NOT cover.

        THE FENCE IS ONLY AS GOOD AS THE HAZARD LIST. `FROZEN_SUBSTITUTION_HAZARDS` is nine files
        somebody enumerated; the other 245 are unreviewed, and any of them that writes a canonical
        product would be an unfenced substitution. Pinning the count means the remainder cannot GROW
        silently -- a new launcher lands in NEITHER and this test reddens, which forces a classification
        rather than letting the default be "unfenced".
        """
        hooked, fenced, both, neither = self._partition()
        self.assertEqual(len(neither), 246,
                         "if this moved, a launcher was added or removed and needs classifying as "
                         "hooked, fenced, or explicitly out of scope. 247 -> 246 when B1 made "
                         "sbatch_finalize_5d_bkgaware_gpu.sh a member-local CONSUMER.")
        self.assertEqual(len(hooked) + len(fenced) + len(both) + len(neither), 263,
                         "263 LAUNCHERS = 265 tracked nd-unfolding/*.sh minus the 2 definition files. "
                         "The number moved from 262 across a rebase: peers added launchers AND my own "
                         "library became visible to `git ls-files` once committed.")

    def test_the_fence_fires_on_a_DECLARATION_including_ZERO_and_EMPTY(self):
        """DECLARED-AT-ALL, not truthy, and the k=0 case is the one worth arguing.

        An unhooked launcher at k=0 writes to the CANONICAL paths, so it would collide with the
        published archive rather than produce an anchor member. The anchor IS a member and must come
        from a hooked launcher like every other one. Set-but-empty is included because that exact
        disagreement -- `${VAR+x}` vs `${VAR:-0}` -- already bit the member library once.
        """
        import subprocess
        script = 'source ./lib_substitution_fence.sh; mr_fence_unhooked; echo CONTINUED'
        for decl in ("0", "", "1200", "-600"):
            with self.subTest(decl=decl):
                r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                                   cwd=str(ND), env=dict(os.environ, MNV_EST_SEED_OFFSET=decl))
                self.assertEqual(r.returncode, 3, f"decl={decl!r} must refuse: {r.stdout}{r.stderr}")
                self.assertNotIn("CONTINUED", r.stdout, "and it must not fall through")
                self.assertIn("REFUSING TO RUN", r.stderr)

    def test_the_fence_is_a_NO_OP_when_UNDECLARED(self):
        """CONTROL, and it is the whole compatibility claim: every non-scan use of these nine launchers
        is byte-identical in behaviour. Without this the fence could be refusing unconditionally."""
        import subprocess
        env = {k: v for k, v in os.environ.items() if k != "MNV_EST_SEED_OFFSET"}
        r = subprocess.run(["bash", "-c",
                            'source ./lib_substitution_fence.sh; mr_fence_unhooked; echo CONTINUED'],
                           capture_output=True, text=True, cwd=str(ND), env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("CONTINUED", r.stdout)
        self.assertEqual(r.stderr, "", "a no-op must be silent, not merely non-fatal")

    def test_every_fenced_launcher_still_PARSES(self):
        r"""`bash -n` on all nine. The insertion sits immediately after a standalone `set -` line and
        NEVER inside a `\`-continued command -- that defect truncated a command to its first line and
        `bash -n` passed on it, so parsing is necessary and not sufficient. The position is asserted
        separately below."""
        import subprocess
        import seed_offset_policy as sp
        for rel in sorted(sp.FROZEN_SUBSTITUTION_HAZARDS):
            with self.subTest(rel=rel):
                r = subprocess.run(["bash", "-n", str(ND.parent / rel)],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_the_fence_is_not_inside_a_CONTINUED_command(self):
        r"""The necessary half `bash -n` cannot give. A hook inserted between a `\`-continued command's
        first line and its continuation makes bash swallow the continuation as a comment: the command
        truncates, arguments vanish, and the syntax stays valid."""
        import seed_offset_policy as sp
        for rel in sorted(sp.FROZEN_SUBSTITUTION_HAZARDS):
            lines = (ND.parent / rel).read_text(errors="replace").split("\n")
            i = next(n for n, l in enumerate(lines) if "mr_fence_unhooked" in l)
            with self.subTest(rel=rel):
                prev = lines[i - 2].rstrip() if i >= 2 else ""
                self.assertFalse(prev.endswith("\\"),
                                 f"{rel}: the line before the fence block is CONTINUED: {prev!r}")
                self.assertTrue(lines[i - 1].startswith("_HERE="),
                                f"{rel}: fence not preceded by its own _HERE line")

    def test_the_fence_is_sourced_RELATIVELY_not_through_REPO(self):
        """BEN-483. A launcher frozen at a sha that sources its fence through the mutable `${REPO}` is
        not frozen -- the cluster probe failed 16/16 on exactly that, and canonical was 180 commits
        behind for 27.5 hours today."""
        import seed_offset_policy as sp
        for rel in sorted(sp.FROZEN_SUBSTITUTION_HAZARDS):
            t = (ND.parent / rel).read_text(errors="replace")
            with self.subTest(rel=rel):
                self.assertIn('source "${_HERE}/lib_substitution_fence.sh"', t)
                self.assertNotIn('source "${REPO}/lib_substitution_fence.sh"', t)


class LibraryResolverSurvivesSbatch(unittest.TestCase):
    """`${BASH_SOURCE[0]}` IS THE SPOOL PATH UNDER sbatch, and that killed stage 0 in 12 seconds.

    Slurm copies the batch script to /var/spool/slurmd/job<N>/slurm_script and executes the COPY, so
    `dirname "${BASH_SOURCE[0]}"` is the spool directory and the library was never staged there. All
    nine tasks of the first three arrays died at that line.

    WHY FOUR PROBE RUNS AND A GATE PASSED OVER IT, which is the part worth keeping: direct execution and
    the argv probe (which SOURCES launchers from a parent shell) BOTH preserve BASH_SOURCE as the real
    path. sbatch is the ONLY invocation that stages the script and the ONLY one production uses. The
    go-line was verified twice in environments that share the property it depends on -- and the probe
    STILL cannot verify the fix, for the same reason, so these tests simulate the spool directly.
    """

    #: DERIVED, not hardcoded. My first version listed seven names and B1 added an eighth
    #: (`sbatch_finalize_5d_bkgaware_gpu.sh`), so a fixed list would have silently stopped covering the
    #: new copy -- the resolver could drift there and no test would look. The count is asserted below so
    #: the derivation cannot quietly return nothing either.
    @property
    def LAUNCHERS(self):
        return tuple(sorted(
            f.name for f in ND.glob("sbatch_*.sh")
            if "# --- M(ii) member axis: LOCATE" in f.read_text(errors="replace")))

    def _block(self):
        """The resolver, extracted VERBATIM from a shipped launcher -- not a copy in the test."""
        lines = (ND / self.LAUNCHERS[0]).read_text().split("\n")
        a = next(i for i, l in enumerate(lines) if l.startswith("# --- M(ii) member axis: LOCATE"))
        b = next(i for i, l in enumerate(lines)
                 if "mr_require_valid_offset" in l and l.startswith("source "))
        return "\n".join(lines[a:b + 1]) + "\necho RESOLVED=$_mr_lib\n"

    def _run(self, cwd, env, script_name="slurm_script"):
        import subprocess
        p = Path(cwd) / script_name
        p.write_text(self._block())
        base = {k: v for k, v in os.environ.items()
                if k not in ("MNV_EST_SEED_OFFSET", "SLURM_JOB_ID", "MNV_LAUNCHER_DIR")}
        base.update(env)
        return subprocess.run(["bash", f"./{script_name}"], capture_output=True, text=True,
                              cwd=str(cwd), env=base)

    def test_EVERY_launcher_carrying_the_resolver_carries_a_BYTE_IDENTICAL_copy(self):
        """It has to be inlined -- it is the code that FINDS the library, so it cannot live in it.
        Inlined copies drift, so identity is pinned instead. EIGHT as of B1: the seven legs plus
        `sbatch_finalize_5d_bkgaware_gpu.sh`, and the list is derived so a ninth is covered on arrival."""
        self.assertEqual(len(self.LAUNCHERS), 8,
                         f"expected 8 resolver-carrying launchers, found {self.LAUNCHERS}")
        import hashlib
        digests = {}
        for f in self.LAUNCHERS:
            lines = (ND / f).read_text().split("\n")
            a = next(i for i, l in enumerate(lines) if l.startswith("# --- M(ii) member axis: LOCATE"))
            b = next(i for i, l in enumerate(lines)
                     if "mr_require_valid_offset" in l and l.startswith("source "))
            digests[f] = hashlib.sha256("\n".join(lines[a:b + 1]).encode()).hexdigest()
        self.assertEqual(len(set(digests.values())), 1,
                         f"the seven resolvers have diverged: {digests}")

    def test_DIRECT_EXECUTION_resolves_via_BASH_SOURCE(self):
        r = self._run(ND, {}, script_name="_t_direct.sh")
        try:
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn(f"RESOLVED={ND}", r.stdout)
        finally:
            (ND / "_t_direct.sh").unlink(missing_ok=True)

    def test_the_SPOOL_CASE_FAILS_CLOSED_rather_than_guessing(self):
        """THE DEFECT, REPRODUCED. A script running from a directory with no library, no override and no
        job id must exit 2 and NAME every candidate it tried -- not fall back to something plausible."""
        with tempfile.TemporaryDirectory() as td:
            r = self._run(td, {})
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("cannot locate lib_member_resume.sh", r.stderr)
            for candidate in ("MNV_LAUNCHER_DIR", "BASH_SOURCE", "scontrol Command"):
                self.assertIn(candidate, r.stderr, "the diagnostic must name what it tried")
            self.assertIn("runs from the spool", r.stderr,
                          "and it must say WHY BASH_SOURCE was wrong, or the next reader re-diagnoses it")

    def test_the_SPOOL_CASE_resolves_with_an_EXPLICIT_override(self):
        with tempfile.TemporaryDirectory() as td:
            r = self._run(td, {"MNV_LAUNCHER_DIR": str(ND)})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn(f"RESOLVED={ND}", r.stdout)

    def test_the_SPOOL_CASE_resolves_via_scontrol_Command(self):
        """The fallback branch. Exercised here against a STUB `scontrol`, so on its own this tests the
        parser against my own idea of the format -- which is the same shape as the defect this class is
        about, and is why it was shipped LABELLED rather than claimed.

        THAT LABEL IS NOW DISCHARGED, by the mediator, against REAL scontrol output on an existing job
        (no new submission):
            raw     Command=/pscratch/.../gate5-data-only-frozen-52df398/nd-unfolding/pet/sbatch_gate5_data_only_target_array.sh
            parsed  the same path, which exists and is ours
        So `tr ' ' '\n' | sed -n 's/^Command=//p' | head -1` returns the true script path on real output.
        The stub stays: it is what makes the branch testable HERE, where scontrol does not exist. What
        changed is that the stub's FORMAT is no longer an assumption -- and the distinction between "this
        test passes" and "the format is right" is exactly the one this class exists to police.

        THE SPACE-IN-PATH LIMITATION STANDS: `tr ' '` splits on spaces, so a script path containing one
        would break. None of this repo's paths do, and that is a property of the paths rather than of the
        parser.
        """
        with tempfile.TemporaryDirectory() as td:
            binp = Path(td) / "bin"
            binp.mkdir()
            (binp / "scontrol").write_text(
                "#!/bin/bash\n"
                f'echo "JobId=99 UserId=x(1) JobName=y Command={ND}/sbatch_bootstrap_5d_gpu.sh WorkDir=/z"\n')
            (binp / "scontrol").chmod(0o755)
            r = self._run(td, {"SLURM_JOB_ID": "99", "PATH": f"{binp}:{os.environ['PATH']}"})
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn(f"RESOLVED={ND}", r.stdout)

    def test_SLURM_SUBMIT_DIR_IS_NOT_A_CANDIDATE_and_that_is_deliberate(self):
        """It would have worked for stage 0 and it is REFUSED, because it is the SUBMIT directory rather
        than the script's. Submitting from the canonical checkout -- which also contains a
        lib_member_resume.sh -- would silently source the CANONICAL library instead of the frozen one,
        reintroducing the exact frozen-deployment defect the relative source closed, and invisibly.
        A candidate that can resolve to the wrong tree is worse than failing closed.
        """
        for f in self.LAUNCHERS:
            body = (ND / f).read_text()
            resolver = body[:body.index("mr_require_valid_offset")]
            # BEN-482, SEVENTH INSTANCE, AND I HIT IT IN THIS VERY TEST. My first version was
            # `assertNotIn("SLURM_SUBMIT_DIR", resolver)` and it FAILED -- on the comment that explains
            # why SLURM_SUBMIT_DIR is deliberately excluded. The comment is the most valuable line in
            # the block, so the matcher is what changes. Strip comments; then assert BOTH directions,
            # so neither the exclusion nor its stated reason can be removed silently.
            code = "\n".join(l for l in resolver.split("\n") if not l.lstrip().startswith("#"))
            with self.subTest(f=f):
                self.assertNotIn("SLURM_SUBMIT_DIR", code,
                                 "SLURM_SUBMIT_DIR must not be CONSULTED to locate the library")
                self.assertIn("SLURM_SUBMIT_DIR IS DELIBERATELY NOT A CANDIDATE", resolver,
                              "and the reason must stay, or the next reader adds it back as an "
                              "obvious robustness improvement")

    def test_a_DECOY_library_in_the_spool_would_be_used_and_that_is_CORRECT(self):
        """Boundary case, recorded so nobody 'fixes' it. Each candidate is validated by the library's
        PRESENCE, so a spool directory that genuinely contained the library would be used -- which is
        right: the file beside the running script IS the frozen library in a direct deployment. Slurm
        does not stage it, so this cannot arise under sbatch; the test pins the semantics."""
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "lib_member_resume.sh").write_text(
                "mr_require_valid_offset() { :; }\n")
            r = self._run(td, {})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn(f"RESOLVED={os.path.realpath(td)}", r.stdout.replace("/private/", "/"))

    def test_the_OLD_go_line_is_GONE_from_every_leg(self):
        """`_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` followed by an unguarded source was
        the defect. The new resolver still consults BASH_SOURCE -- correctly, as one validated candidate
        -- so the check is that no launcher sources the library from an UNVALIDATED path."""
        for f in self.LAUNCHERS:
            body = (ND / f).read_text()
            with self.subTest(f=f):
                self.assertNotIn('source "${_HERE}/lib_member_resume.sh"', body)
                self.assertIn('source "${_mr_lib}/lib_member_resume.sh"', body)


class B1MemberLocalConsumerChain(unittest.TestCase):
    """B1 steps 1-3. The defect is in `sbatch_finalize_5d_bkgaware_gpu.sh`'s OWN HEADER:

        "C_stat/C_ML are #13-invariant -> reuse existing uq_cov_stat_5d.root / uq_cov_mlsplit_5d.root"

    Correct for a background-treatment comparison where only the vertical sweep changes; EXACTLY WRONG
    for a member, whose premise is a different estimator seed. Unmodified, it injects the ARCHIVE's
    C_stat into the member's combined covariance and discards the member's own 100 replicas.
    Stage 0 made that quantitative: the seed moves C_stat's replicas across essentially the whole
    reported support (three DISTINCT verdicts, jobs 57252337-9).
    """

    SCRIPT = "sbatch_finalize_5d_bkgaware_gpu.sh"

    def _resolve(self, offset):
        """Evaluate the script's own path assignments under the real member library."""
        import subprocess
        body = (ND / self.SCRIPT).read_text()
        wanted = ("OUTD=", "SWEEP_GLOB=", "UTHROW=", "STAT_COV=", "ML_COV=")
        assigns = [l for l in body.split("\n") if l.startswith(wanted)]
        script = ("source ./lib_member_resume.sh\n" + "\n".join(assigns) +
                  '\nfor v in OUTD SWEEP_GLOB UTHROW STAT_COV ML_COV; do'
                  ' echo "$v=${!v}"; done\n'
                  'mr_declared && echo DECLARED=yes || echo DECLARED=no\n')
        env = {k: v for k, v in os.environ.items() if k != "MNV_EST_SEED_OFFSET"}
        if offset is not None:
            env["MNV_EST_SEED_OFFSET"] = str(offset)
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                           cwd=str(ND), env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return dict(l.split("=", 1) for l in r.stdout.strip().split("\n") if "=" in l)

    def test_UNDECLARED_every_path_reduces_to_its_ARCHIVE_LITERAL(self):
        """The compatibility claim, and it is the hard constraint: this script must remain the
        CV-background comparator it has always been for every non-scan use."""
        g = self._resolve(None)
        self.assertEqual(g["OUTD"], "uq_5d/universe_stage2_5d_bkgaware")
        self.assertEqual(g["SWEEP_GLOB"],
                         "uq_5d/universe_sweep_bkgaware/5d_xsec_*_uni_full_*.root")
        self.assertEqual(g["UTHROW"], "uq_5d/unified_throw_cov_5d.root")
        self.assertEqual(g["STAT_COV"], "uq_cov_stat_5d.root")
        self.assertEqual(g["ML_COV"], "uq_cov_mlsplit_5d.root")
        self.assertEqual(g["DECLARED"], "no")

    def test_DECLARED_every_path_is_MEMBER_SCOPED_including_the_two_covariance_roots(self):
        g = self._resolve(1200)
        root = "mii/member_k001200"
        for k in ("OUTD", "SWEEP_GLOB", "UTHROW", "STAT_COV", "ML_COV"):
            with self.subTest(var=k):
                self.assertTrue(g[k].startswith(root + "/"),
                                f"{k}={g[k]!r} must start with {root!r}")
        self.assertEqual(g["DECLARED"], "yes")

    def test_the_COVARIANCE_ROOTS_are_member_scoped_which_is_the_WHOLE_POINT(self):
        """If only the sweep glob were memberized, the member would still consume the archive's C_stat --
        the defect would survive the patch and look fixed. These two paths are the fix."""
        g = self._resolve(1200)
        import seed_offset_policy as sp
        for k in ("STAT_COV", "ML_COV"):
            sp.assert_member_path_is_outside_the_archive(g[k])

    def test_the_EXACT_POPULATION_validators_are_KEPT_at_full_range(self):
        """`--expected-ids 1-100` / `1-24` must not be relaxed for members. A member with a partial
        replica set must REFUSE rather than combine what it has -- that barrier is what makes its C_stat
        comparable to the archive's at all, and relaxing it is the obvious way to make a member 'work'."""
        body = (ND / self.SCRIPT).read_text()
        self.assertIn("--expected-ids 1-100", body)
        self.assertIn("--expected-ids 1-24", body)

    def test_the_ADOPTIONS_PAUSE_with_an_EXPIRY_CONDITION_not_a_rationale(self):
        """C CORRECTED THE FRAMING AND IT CHANGES WHAT MUST BE RECORDED.

        The cut is a PAUSE, not a boundary, and the reason is specific: `sqrt_tr_old` -- THE BAR'S OWN
        OPERAND -- is written at `adopt_unified_5d.py:177`, INSIDE steps (4)/(5). So stopping here means
        stage 1 cannot compare the quantity the bar is about. A STOP-AFTER-(3) MEMBER IS A STAGE 1 *NOT
        ATTEMPTED*, NOT ONE AWAITING PAPERWORK, AND THE TWO READ IDENTICALLY IN A STATUS TABLE. Hence the
        EXPIRY CONDITION is what goes in the message, not the justification.
        """
        body = (ND / self.SCRIPT).read_text()
        i = body.index("MEMBER PAUSE")
        j = body.index("adopt (mean-centered)")
        self.assertLess(i, j, "the pause must precede the adoption calls")
        self.assertIn("EXPIRY: remedy (A)", body, "the expiry condition, not the rationale")
        self.assertIn("STAGE 1", body[i:j])
        self.assertIn("NOT ATTEMPTED", body[i:j],
                      "the status distinction is the point -- 'not attempted' and 'pending' read the same")
        self.assertIn("exit 0", body[i:j], "and it must exit rather than fall through")

    def test_the_PAUSE_forbids_deleting_the_intermediate(self):
        """C: 11g gates deletion on MVFINAL_j, which needs (4)/(5). So "stop after (3)" combined with
        "11g releases the 41 GB" would delete THE ONLY INPUT to the steps that have not run. Two rulings
        that are each correct and jointly destructive -- which is why the pause has to say so."""
        body = (ND / self.SCRIPT).read_text()
        self.assertIn("DO NOT DELETE", body)
        self.assertIn("11g gates deletion on MVFINAL_j", body)

    def test_remedy_A_is_recorded_as_covering_BOTH_writers_not_just_adoption(self):
        """C WIDENED (A) to LATERAL_CV after D's enumeration was longer than mine: I enumerated WRITERS
        needing stamps, D enumerated ARTIFACTS THE GATE CANNOT READ. Same defect, two directions, and
        D's direction found more."""
        body = (ND / self.SCRIPT).read_text()
        self.assertIn("unfold_nd_omnifold_unbinned.py", body,
                      "the pause must name BOTH writers (A) now covers")
        import mii_root_payload_classes as classes
        self.assertFalse(classes.identity_is_checkable("lateral_cv.root"))

    def test_the_CV_IS_MEMBER_SCOPED_because_C_RULED_SUBSTITUTE(self):
        """MY HOLD WAS REVERSED, AND THE REASON IS ABOUT SPREADS RATHER THAN VALUES.

        I proposed pinning to the archive's CV, documented as a choice. C's own earlier sentence --
        "substituting would inject a difference that is NOT estimator noise, which is worse than pinning"
        -- is the right test for comparing VALUES. THE BAR COMPARES SPREADS, and there it inverts:
            PIN        sd_j(0.014 * ||cv_arch||) is EXACTLY 0 -> the flat-norm term contributes NOTHING
            SUBSTITUTE sd is driven by the seed response      -> the term contributes its real sensitivity
        AND THE DIRECTION OF THE BIAS IS TOWARD *MET* -- a pass bought by omitting a term -- which is why
        it was not a free choice and why C asked for the direction to be recorded, not just the decision.
        My call-site documentation instinct was right; what I documented was the wrong conclusion.
        """
        body = (ND / self.SCRIPT).read_text()
        self.assertIn("C RULED **SUBSTITUTE**, REVERSING MY HOLD", body)
        self.assertIn("THE BAR COMPARES SPREADS", body)
        self.assertIn("TOWARD *MET*", body, "the DIRECTION of the bias, which is C's specific ask")
        # case-insensitive: the point is that the cancellation is still stated, not how it is cased.
        # My first version asserted an ALL-CAPS form and failed on prose that says the same thing --
        # and pytest then dumped the entire 12 kB launcher into the failure, which is its own argument
        # for asserting on structure rather than on capitalisation.
        self.assertIn("cancels algebraically", body.lower(),
                      "still true of the systematic covariance, and still worth stating")
        self.assertIn("mask_order_hash", body,
                      "the mask must not be checked by COUNTING -- equal-size supports can differ in "
                      "MEMBERSHIP, which silently compares the wrong pairs")

    def test_the_member_CV_resolves_to_the_members_own_uni_full_CV(self):
        """Behavioural, both regimes, since the whole point is that undeclared must not move."""
        import subprocess
        snippet = ('source ./lib_member_resume.sh\n'
                   'CV_ARCHIVE="products/5d/xsec_5d_MEFHC_5iter_lgbm.root"\n'
                   'if mr_declared; then CV="$(mr_prefix uq_5d/universe_sweep_bkgaware)'
                   '/5d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"; else CV="${CV_ARCHIVE}"; fi\n'
                   'echo "$CV"\n')
        base = {k: v for k, v in os.environ.items() if k != "MNV_EST_SEED_OFFSET"}
        undecl = subprocess.run(["bash", "-c", snippet], capture_output=True, text=True,
                                cwd=str(ND), env=base).stdout.strip()
        decl = subprocess.run(["bash", "-c", snippet], capture_output=True, text=True, cwd=str(ND),
                              env=dict(base, MNV_EST_SEED_OFFSET="1200")).stdout.strip()
        self.assertEqual(undecl, "products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
        self.assertEqual(decl, "mii/member_k001200/uq_5d/universe_sweep_bkgaware/"
                               "5d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root")

    def test_ANY_reduction_needs_TWO_numbers_and_there_are_currently_NONE(self):
        """C: a reduction must declare element coverage AND the mass fraction it excludes, measured.
        0.00935% and 997x is the template. The table is EMPTY because PAYLOAD-class reduction is refused;
        it exists so that adding one costs a MEASUREMENT rather than a line."""
        import mii_anchor_comparator as B
        self.assertEqual(B.DECLARED_REDUCTIONS, {})
        self.assertIsNone(B.assert_reduction_is_declared("C_unified", 1.0),
                          "full coverage needs no declaration")
        msg = B.assert_reduction_is_declared("C_unified", 0.0000935)
        self.assertIn("UNDECLARED REDUCTION", msg)
        self.assertIn("mass fraction", msg, "both numbers must be named in the refusal")

    def test_the_cv_cancellation_claim_is_TRUE_of_the_analyzer_as_written(self):
        """Not a comment I can edit freely: re-derive it from the analyzer's actual lines."""
        src = (ND / "analyze_universes_5d.py").read_text()
        self.assertIn("load_flat(p, expect_nbins=cv.size) - cv", src, "D_i = u_i - cv")
        self.assertIn("Z = D - D.mean(axis=0, keepdims=True)", src, "column mean subtracted")
        u = np.array([[1.0, 5.0], [3.0, 9.0], [2.0, 1.0]])
        def cov(cv):
            D = u - cv
            Z = D - D.mean(axis=0, keepdims=True)
            return (Z.T @ Z) / D.shape[0]
        a, b = cov(np.array([0.5, 0.5])), cov(np.array([7.0, -3.0]))
        self.assertTrue(np.array_equal(a, b),
                        "the covariance must be BIT-identical under a different cv, not merely close")


class SummationRouteIsLoadBearing(unittest.TestCase):
    """C's ask, and it is the only control that stops a no-op-looking diff from breaking a bit-exact gate.

    D measured all four recomputations BIT-EXACT against the stamped values -- and found that a sequential
    Python sum over the SAME diagonal differs in the last ulps. It holds because NUMPY PAIRWISE SUMMATION
    IS ON BOTH SIDES: `np.trace` in the writer (`unified_throw_cov.py:483-484`) and `np.sum` in
    `_sqrt_trace_from_diag`. THAT IS A PROPERTY OF THE SUMMATION ROUTE, NOT OF THE MATHEMATICS.

    So asserting only "the recompute matches" is insufficient: it would keep passing if someone replaced
    either side with a loop on a machine where the ulps happened to agree. The control asserts BOTH
    directions -- pairwise matches AND naive sequential does NOT -- so the dependency is visible.
    """

    def _diag(self):
        # values chosen so sequential and pairwise summation genuinely differ: many small terms after a
        # large one, which is the classic catastrophic-accumulation shape.
        rng = np.random.default_rng(20260819)
        return np.concatenate([[1e16], rng.random(4096) * 1e-3])

    def test_pairwise_and_sequential_summation_DISAGREE_on_this_diagonal(self):
        """The premise. If this ever fails, the fixture stopped exercising the hazard and the control
        below is vacuous -- which is exactly the state a power test exists to prevent."""
        d = self._diag()
        pairwise = float(np.sum(d))
        seq = 0.0
        for x in d:
            seq += float(x)
        self.assertNotEqual(pairwise, seq,
                            "the fixture must distinguish the two routes or the control proves nothing")

    def test_the_recompute_uses_the_PAIRWISE_route_and_a_LOOP_would_break_it(self):
        import mii_anchor_comparator as B
        d = self._diag()
        got = B._sqrt_trace_from_diag(d)
        self.assertEqual(got, float(np.sqrt(max(float(np.sum(d)), 0.0))),
                         "the shipped helper must use numpy pairwise summation")
        seq = 0.0
        for x in d:
            seq += float(x)
        self.assertNotEqual(got, float(np.sqrt(max(seq, 0.0))),
                            "and a naive sequential sum must NOT reproduce it -- if it did, the "
                            "bit-exactness would not depend on the route and this control would be "
                            "asserting nothing")

    def test_the_dependency_is_DOCUMENTED_at_the_helper(self):
        """A diff that reviews as a no-op is the worst kind to break a gate with, so the warning has to
        be where the change would be made."""
        src = (ND / "mii_anchor_comparator.py").read_text()
        self.assertIn("PROPERTY OF THE SUMMATION ROUTE", src)
        self.assertIn("unified_throw_cov.py:483-484", src, "both sides of the route must be named")
        self.assertIn("math.fsum", src, "and the other tempting 'simplification' too")


class TwoReadPathsCrossCheck(unittest.TestCase):
    """C's section 20: THE DANGEROUS FAILURE DOES NOT RAISE, so the fallback structurally cannot catch it.

    A wrong dtype, a single-precision TH2D, an off-by-one in the under/overflow slice, or a future ROOT
    layout change each returns an array of THE RIGHT SHAPE WITH WRONG NUMBERS. The fallback never
    triggers, and the coverage line reports 100.00%. THAT IS H1 INVERTED -- there the word was wrong and
    the bytes right; here the word is right and the bytes wrong. COVERAGE COUNTS ELEMENTS COMPARED AND
    CANNOT SEE WHETHER THEY WERE READ CORRECTLY.
    The two paths compute the same quantity by INDEPENDENT ROUTES, so they need no oracle.
    """

    class _Buf:
        """Mimics PyROOT's low-level buffer: SetSize() plus the buffer protocol."""
        def __init__(self, arr):
            self._arr = arr
        def SetSize(self, n):
            self._n = n
        def __buffer__(self, flags):
            return memoryview(self._arr)

    class _TH2:
        def __init__(self, ny, nx, corrupt_buffer=False):
            self._nx, self._ny = nx, ny
            self._flat = np.arange((nx + 2) * (ny + 2), dtype=np.float64) * 0.5
            self._corrupt = corrupt_buffer
        def GetNbinsX(self): return self._nx
        def GetNbinsY(self): return self._ny
        def GetArray(self):
            a = self._flat.copy()
            if self._corrupt:
                a[:] = a[::-1]      # right shape, WRONG BYTES -- and it does not raise
            return TwoReadPathsCrossCheck._Buf(a)
        def GetBinContent(self, i, j):
            return float(self._flat[j * (self._nx + 2) + i])
        def Delete(self): pass

    def setUp(self):
        import mii_anchor_comparator as B
        self.B = B

    def test_the_BUFFER_path_executes_and_AGREES_with_the_row_loop(self):
        h = self._TH2(3, 4)
        arr, which = self.B._th2_content(h)
        self.assertEqual(which, "buffer", "the fast path must actually run, or the cross-check is vacuous")
        r = self.B.cross_check_readers(h)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["digest_buffer"], r["digest_rowloop"])
        self.assertEqual(r["elements"], 12)

    def test_the_cross_check_CATCHES_succeeds_but_wrong(self):
        """THE DIRECTION IT ACTS IN, and the only failure mode the fallback cannot see: a buffer read that
        returns the right shape and the wrong numbers, WITHOUT RAISING."""
        h = self._TH2(3, 4, corrupt_buffer=True)
        arr, which = self.B._th2_content(h)
        self.assertEqual(which, "buffer", "it must NOT have fallen back -- that is the whole point")
        r = self.B.cross_check_readers(h)
        self.assertFalse(r["ok"], "a wrong-bytes buffer read must be caught")
        self.assertIn("THE TWO READ PATHS DISAGREE", r["why"])
        self.assertGreater(r["n_differing"], 0)
        self.assertNotEqual(r["digest_buffer"], r["digest_rowloop"])

    def test_the_returned_array_NEVER_ALIASES_the_ROOT_buffer(self):
        """C's finding, and my copy was safe only BY ACCIDENT. `np.frombuffer` returns a VIEW, and
        [1:ny+1, 1:nx+1] of an (ny+2, nx+2) array is NON-CONTIGUOUS -- the under/overflow padding is the
        only reason `ascontiguousarray` copied. Remove the padding arithmetic, a plausible
        'simplification', and the slice becomes contiguous, the copy vanishes, and the function returns a
        view into a buffer that `read_keys_pyroot` then Delete()s. Two separately-correct rulings --
        explicit Delete(), and padding-aware slicing -- interacting destructively.
        """
        h = self._TH2(3, 4)
        arr, which = self.B._th2_content(h)
        self.assertEqual(which, "buffer")
        # mutate the source after the read; an aliasing return would change too
        original = arr.copy()
        h._flat[:] = -999.0
        np.testing.assert_array_equal(arr, original,
                                      "the returned array must be an independent copy")
        src = (ND / "mii_anchor_comparator.py").read_text()
        self.assertIn("np.shares_memory(out, flat)", src,
                      "and the non-aliasing must be PINNED by an assert, not left to np.array's "
                      "argument surviving a future edit")
        self.assertIn("copy=True", src)

    def test_the_FALLBACK_ANNOUNCES_ITSELF_rather_than_hiding(self):
        """A bare `except Exception` over five operations made the fast path's failure INVISIBLE: any
        failure returned the RIGHT answer by the slow route and no run ever said so, so the fast path
        could be permanently broken and unnoticed. WHICH READER EXECUTED IS AN INGREDIENT OF THE DIGEST."""
        import contextlib, io as _io
        class _NoBuffer(TwoReadPathsCrossCheck._TH2):
            def GetArray(self):
                raise AttributeError("no GetArray on this build")
        h = _NoBuffer(3, 4)
        err = _io.StringIO()
        with contextlib.redirect_stderr(err):
            arr, which = self.B._th2_content(h)
        self.assertEqual(which, "rowloop")
        self.assertIn("BUFFER PATH FAILED", err.getvalue())
        self.assertIn("AttributeError", err.getvalue(), "and it must name what failed")
        self.assertIn("INGREDIENT OF THE DIGEST", err.getvalue())
        src = (ND / "mii_anchor_comparator.py").read_text()
        self.assertNotIn("except Exception:\n        # FALLBACK", src, "the bare catch must be gone")

    def test_the_cross_check_REFUSES_to_claim_a_check_it_could_not_run(self):
        """If the buffer path did not execute there is nothing to cross-check, and saying so beats
        returning ok=True over one path run twice."""
        class _NoBuffer(TwoReadPathsCrossCheck._TH2):
            def GetArray(self):
                raise AttributeError("no GetArray")
        import contextlib, io as _io
        with contextlib.redirect_stderr(_io.StringIO()):
            r = self.B.cross_check_readers(_NoBuffer(3, 4))
        self.assertFalse(r["ok"])
        self.assertIn("nothing to cross-check", r["why"])
        self.assertEqual(r["path"], "rowloop")

if __name__ == "__main__":
    unittest.main()
