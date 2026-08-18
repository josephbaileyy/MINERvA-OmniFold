import ast
import importlib.util
import sys
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
                     seed=np.int64(42), flux_normalized=np.int64(1))
            np.savez(p / "throws_1.npz", xs=throws[2:], throws=np.array([2]),
                     seed=np.int64(42), flux_normalized=np.int64(1))
            endpoints = np.array([[0.9, 2.2], [1.1, 1.8]])
            np.savez(p / "blocks.npz", xs=endpoints,
                     labels=np.array(["MaCCQE:0", "MaCCQE:1"], dtype=object),
                     seed=np.int64(42),
                     kinds=np.array(["knob", "knob"], dtype=object),
                     flux_normalized=np.int64(1))

            d = {"edges": [np.array([0.0, 1.0, 2.0])],
                 "w_truth": np.ones(1), "w_reco": np.ones(1), "td_w": np.ones(1)}
            old_load, old_kernel = utc._load_bank, utc._xsec_for_weights
            utc._load_bank = lambda bank: (d, ["MaCCQE"], 0)
            utc._xsec_for_weights = lambda *args, **kwargs: np.array([1.0, 2.0])
            try:
                args = SimpleNamespace(
                    bank=td, iters=1, seed=42,
                    combine=str(p / "throws_*.npz"),
                    block_slabs=str(p / "blocks.npz"),
                    expected_throws="0-2", null=True, out_root=None)
                result = utc.do_combine(args)
                args.expected_throws = "0-3"
                with self.assertRaises(SystemExit):
                    utc.do_combine(args)
                # F2 guard: a slab stamped with a different estimator seed is rejected
                args.expected_throws = "0-2"
                np.savez(p / "throws_0.npz", xs=throws[:2], throws=np.array([0, 1]),
                         seed=np.int64(999))
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
                         seed=np.int64(seed_a), flux_normalized=np.int64(1))
                np.savez(p / "throws_1.npz", xs=throws[2:], throws=np.array([2]),
                         seed=np.int64(seed_b), flux_normalized=np.int64(1))
                np.savez(p / "blocks.npz", xs=np.array([[0.9, 2.2], [1.1, 1.8]]),
                         labels=np.array(["MaCCQE:0", "MaCCQE:1"], dtype=object),
                         seed=np.int64(seed_a),
                         kinds=np.array(["knob", "knob"], dtype=object),
                         flux_normalized=np.int64(1))

            d = {"edges": [np.array([0.0, 1.0, 2.0])],
                 "w_truth": np.ones(1), "w_reco": np.ones(1), "td_w": np.ones(1)}
            old_load, old_kernel = utc._load_bank, utc._xsec_for_weights
            utc._load_bank = lambda bank: (d, ["MaCCQE"], 0)
            utc._xsec_for_weights = lambda *a, **k: np.array([1.0, 2.0])
            try:
                args = SimpleNamespace(bank=td, iters=1, seed=42,
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
                     seed=np.int64(42), flux_normalized=np.int64(1))
            np.savez(p / "throws_1.npz", xs=throws[2:], throws=np.array([2]),
                     seed=np.int64(42), flux_normalized=np.int64(1))
            np.savez(p / "blocks.npz", xs=np.array([[0.9, 2.2], [1.1, 1.8]]),
                     labels=np.array(["MaCCQE:0", "MaCCQE:1"], dtype=object),
                     seed=np.int64(42),
                     kinds=np.array(["knob", "knob"], dtype=object),
                     flux_normalized=np.int64(1))

            d = {"edges": [np.array([0.0, 1.0, 2.0])],
                 "w_truth": np.ones(1), "w_reco": np.ones(1), "td_w": np.ones(1)}
            old_load, old_kernel = utc._load_bank, utc._xsec_for_weights
            utc._load_bank = lambda bank: (d, ["MaCCQE"], 0)
            utc._xsec_for_weights = lambda *a, **k: np.array([1.0, 2.0])
            try:
                args = SimpleNamespace(bank=td, iters=1, seed=42,
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

        Without this the static test is a spelling check. Same technique as
        `test_flux_universe_fix.EavailWFluxBlockIsPerUniverse.test_the_prefix_source_would_fail`.
        """
        src = (ND / self.FNAME).read_text()
        marker = "    # BOTH DIRECTIONS (added 2026-08-11, quarantine cause 6)."
        self.assertIn(marker, src, "guard block marker missing; this test can no longer locate it")
        head, _, tail = src.partition(marker)
        # drop the whole guard block: everything from the marker to the next top-level-ish statement
        rest = tail.split("\n    fs = ROOT.TFile.Open(args.stat5d)", 1)
        self.assertEqual(len(rest), 2, "guard block no longer ends where this test expects")
        prefix_src = head + "    fs = ROOT.TFile.Open(args.stat5d)" + rest[1]

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
        self.assertEqual(found, ["analyze_universes_5d.py:109"],
                         "unaccounted outer product on X's build path -- a cause-1 candidate")
if __name__ == "__main__":
    unittest.main()
