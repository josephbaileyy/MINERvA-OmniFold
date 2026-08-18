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

if __name__ == "__main__":
    unittest.main()
