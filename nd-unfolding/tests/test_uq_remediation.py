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


if __name__ == "__main__":
    unittest.main()
