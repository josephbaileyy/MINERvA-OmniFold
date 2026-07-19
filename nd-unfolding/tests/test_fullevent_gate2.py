"""Login-safe Gate-2 tests: the negweight-refined measured-target CONSTRUCTION in
fullevent_fps_dataloader.build_fullevent_loaders (Option-A literal background injection +
Stay-Positive refinement).

No GPU / no PET training / no TF. The vendored numpy-only DataLoader is loaded directly (bypassing
omnifold/__init__.py, which imports TensorFlow) so the fixture reaches the REAL loader boundary. The
CANONICAL learned refinement (u2d.refine_stay_positive) imports ROOT/TF at module load and segfaults
on the login node, so it is NEVER called here; the construction is validated against an
algorithm-identical sklearn refinement injected via refine_fn. The binned closed-form
stay_positive_refine_binned is exercised as the FIXTURE-ONLY independent cross-check.

=> These tests do NOT establish Gate-2 PASS: the learned PRODUCTION refinement (u2d) is wired via a
deferred import + injectable hook but its canonical execution + full-scale materialization remain a
runtime (compute-node) step. See the module docstring / report."""
import importlib.util
import os
import sys
import tempfile
import types
import unittest

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ND, "pet"))

import dump_pointcloud_inputs as dp   # noqa: E402  (ROOT deferred)
import fullevent_fps_dataloader as fed  # noqa: E402


def _load_real_dataloader():
    """Load the numpy-only omnifold.dataloader.DataLoader WITHOUT triggering omnifold/__init__.py
    (which imports TensorFlow), so build_fullevent_loaders' internal import resolves login-safe."""
    if "omnifold.dataloader" in sys.modules:
        return
    dlp = os.path.join(REPO, "omnifold_nn", "omnifold", "dataloader.py")
    if "omnifold" not in sys.modules:
        pkg = types.ModuleType("omnifold"); pkg.__path__ = [os.path.dirname(dlp)]
        sys.modules["omnifold"] = pkg
    spec = importlib.util.spec_from_file_location("omnifold.dataloader", dlp)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["omnifold.dataloader"] = mod
    spec.loader.exec_module(mod)


def _scal(rng, n):
    """(pt, p_parallel, eavail, q3) all inside the retained extended-FPS domain."""
    return np.column_stack([rng.uniform(0.1, 3.0, n), rng.uniform(0.5, 10.0, n),
                            rng.uniform(0.0, 2.0, n), rng.uniform(0.0, 1.0, n)]).astype(np.float32)


def small_g2_arrays(ns=40, nd=30, nb=12, P=6, seed=1):
    """A small, contract-VALID g2-fullevent-v1 arrays dict via the dumper's finalizer (real markers,
    edges, identity hashes). measured_scalars present; no measured_weights (matches the G2 dump)."""
    rng = np.random.default_rng(seed)
    sig = dict(part_reco=rng.random((ns, P, 3), np.float32), reco_scalars=_scal(rng, ns),
               reco_muon=rng.random((ns, 7), np.float32), reco_vertex=rng.random((ns, 3), np.float32),
               reco_view=rng.integers(0, 4, (ns, P)).astype(np.float32),
               reco_time=rng.random((ns, P), np.float32), part_gen=rng.random((ns, P, 5), np.float32),
               truth_scalars=_scal(rng, ns), pass_reco=np.ones(ns, bool), pass_truth=np.ones(ns, bool),
               w_truth=rng.random(ns).astype(np.float32), w_reco=rng.random(ns).astype(np.float32))
    data = dict(measured_pc=rng.random((nd, P, 3), np.float32), measured_scalars=_scal(rng, nd),
                data_muon=rng.random((nd, 7), np.float32), data_vertex=rng.random((nd, 3), np.float32),
                data_view=rng.integers(0, 4, (nd, P)).astype(np.float32),
                data_time=rng.random((nd, P), np.float32))
    bkg = dict(bkg_part_reco=rng.random((nb, P, 3), np.float32), bkg_reco_scalars=_scal(rng, nb),
               bkg_muon=rng.random((nb, 7), np.float32), bkg_vertex=rng.random((nb, 3), np.float32),
               bkg_view=rng.integers(0, 4, (nb, P)).astype(np.float32),
               bkg_time=rng.random((nb, P), np.float32), w_bkg=(rng.random(nb) + 0.5).astype(np.float32),
               bkg_nuPDG=rng.integers(-14, 15, nb), bkg_current=np.ones(nb, int),
               bkg_inttype=rng.integers(1, 5, nb))
    return dp.finalize_g2_arrays(sig, data, bkg, data_pot=8.97e19, mc_pot=4.07e20, pot_scale=0.22,
                                 edges_pt=fed.CANONICAL_PT_EDGES,
                                 edges_pz=fed.CANONICAL_PPARALLEL_EDGES, num_part=P)


def write_npz(td, arrays, name="G2_small.npz"):
    p = os.path.join(td, name); np.savez(p, **arrays); return p


def sklearn_refine(feat, signed, estimator="exact", **kw):
    """Algorithm-identical login-safe stand-in for u2d.refine_stay_positive: train g(x) on
    |w|-weighted (pos vs neg) events, refine w~=|w|*clip(2g-1,0). Returns (w_ref, g, frac_clip)."""
    from sklearn.ensemble import GradientBoostingClassifier
    feat = np.asarray(feat, float); signed = np.asarray(signed, float)
    lab = (signed > 0).astype(int); absw = np.abs(signed)
    clf = GradientBoostingClassifier(random_state=0)
    clf.fit(feat, lab, sample_weight=absw)
    g = np.clip(clf.predict_proba(feat)[:, 1], 1e-6, 1.0 - 1e-6)
    fac = 2.0 * g - 1.0
    return absw * np.clip(fac, 0.0, None), g, float((fac < 0).mean())


def build(td, arrays=None, **kw):
    _load_real_dataloader()
    arrays = arrays if arrays is not None else small_g2_arrays()
    p = write_npz(td, arrays)
    kw.setdefault("refine_fn", sklearn_refine)
    kw.setdefault("bkg_mode", "negweight-refined")
    return fed.build_fullevent_loaders(p, **kw)


class SignedInventoryConstruction(unittest.TestCase):
    def test_positive_data_negative_background(self):
        fd = np.array([[1.0, 2.0], [1.1, 2.1], [1.2, 2.2]]); fb = np.array([[0.5, 0.5], [0.6, 0.6]])
        w_bkg = np.array([2.0, 4.0]); pot = 0.25
        feat, signed, n_d, n_b, pos, neg = fed.build_signed_measured_inventory(fd, fb, w_bkg, pot)
        self.assertEqual((n_d, n_b), (3, 2))
        self.assertEqual(feat.shape, (5, 2))
        np.testing.assert_allclose(signed[:3], 1.0)                    # data +1
        np.testing.assert_allclose(signed[3:], [-0.5, -1.0])           # -w_bkg*pot
        self.assertAlmostEqual(pos, 3.0)
        self.assertAlmostEqual(neg, 1.5)

    def test_factors_applied_before_refinement(self):
        fd = np.ones((2, 2)); fb = np.ones((2, 2)); w_bkg = np.array([1.0, 1.0])
        _, signed, _, _, pos, neg = fed.build_signed_measured_inventory(
            fd, fb, w_bkg, 0.5, data_factor=np.array([2, 0]), bkg_factor=np.array([3, 1]))
        np.testing.assert_allclose(signed, [2.0, 0.0, -1.5, -0.5])     # +df ; -(w*pot)*bf
        self.assertAlmostEqual(neg, 2.0)

    def test_invalid_pot_fails_closed(self):
        fd = np.ones((2, 2)); fb = np.ones((1, 2)); w = np.ones(1)
        for bad in (0.0, -0.5, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                fed.build_signed_measured_inventory(fd, fb, w, bad)

    def test_misaligned_background_fails_closed(self):
        fd = np.ones((3, 2)); fb = np.ones((2, 2)); w = np.ones(3)   # w_bkg rows != fb rows
        with self.assertRaises(ValueError):
            fed.build_signed_measured_inventory(fd, fb, w, 0.2)

    def test_misaligned_columns_fails_closed(self):
        with self.assertRaises(ValueError):
            fed.build_signed_measured_inventory(np.ones((3, 2)), np.ones((2, 3)), np.ones(2), 0.2)

    def test_nonfinite_fails_closed(self):
        fb = np.ones((2, 2)); w = np.array([1.0, np.nan])
        with self.assertRaises(ValueError):
            fed.build_signed_measured_inventory(np.ones((3, 2)), fb, w, 0.2)

    def test_bad_factor_length_fails_closed(self):
        with self.assertRaises(ValueError):
            fed.build_signed_measured_inventory(np.ones((3, 2)), np.ones((2, 2)), np.ones(2), 0.2,
                                                data_factor=np.ones(2))


class RefineSignedMeasured(unittest.TestCase):
    def test_learned_refinement_finite_nonnegative_aligned(self):
        rng = np.random.default_rng(3)
        feat = rng.random((60, 2)); signed = np.concatenate([np.ones(40), -rng.random(20)])
        w_ref, telem = fed.refine_signed_measured(feat, signed, sklearn_refine)
        self.assertEqual(w_ref.shape[0], 60)
        self.assertTrue(np.all(np.isfinite(w_ref)) and np.all(w_ref >= 0))
        for k in ("refined_sum", "refined_min", "refined_max", "n_floored_zero"):
            self.assertIn(k, telem)

    def test_bare_array_return_supported(self):
        feat = np.random.default_rng(0).random((6, 2)); signed = np.array([1, 1, 1, -1, -1, 1.0])
        w_ref, _ = fed.refine_signed_measured(feat, signed, lambda f, s, **k: np.abs(s))
        np.testing.assert_allclose(w_ref, np.abs(signed))

    def test_negative_output_rejected(self):
        with self.assertRaises(ValueError):
            fed.refine_signed_measured(np.ones((3, 2)), np.array([1.0, -1, 1]),
                                       lambda f, s, **k: np.array([1.0, -0.1, 1.0]))

    def test_nonfinite_output_rejected(self):
        with self.assertRaises(ValueError):
            fed.refine_signed_measured(np.ones((3, 2)), np.array([1.0, -1, 1]),
                                       lambda f, s, **k: np.array([1.0, np.inf, 1.0]))

    def test_misaligned_output_rejected(self):
        with self.assertRaises(ValueError):
            fed.refine_signed_measured(np.ones((3, 2)), np.array([1.0, -1, 1]),
                                       lambda f, s, **k: np.ones(2))


class IndependentBinnedCheck(unittest.TestCase):
    """Cross-check the signed construction against the closed-form binned Stay-Positive (fixture)."""
    def test_binned_refined_sums_to_D_minus_B_and_nonnegative(self):
        fd = np.array([[0.2], [0.2], [1.0]]); fb = np.array([[0.2], [1.0]])
        w_bkg = np.array([1.0, 5.0]); pot = 0.5     # cell0: D=2,B=0.5 ; cell1: D=1,B=2.5 (B>D)
        _, signed, n_d, n_b, _, _ = fed.build_signed_measured_inventory(fd, fb, w_bkg, pot)
        cell = np.array([0, 0, 1, 0, 1])            # data cells [0,0,1], bkg cells [0,1]
        refined = fed.stay_positive_refine_binned(signed, cell, 2)
        self.assertTrue(np.all(refined >= 0))
        s0 = refined[cell == 0].sum(); s1 = refined[cell == 1].sum()
        self.assertAlmostEqual(s0, 2.0 - 0.5, places=6)   # D-B where D>=B
        self.assertAlmostEqual(s1, 0.0, places=6)         # floored at 0 where B>D


class EndToEndLoaderBoundary(unittest.TestCase):
    def test_reaches_real_dataloader_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            data, mc, imc, cr, cg, meta = build(td)
            nd_ = meta["target"]["n_data_rows"]; nb = meta["target"]["n_bkg_rows"]
            self.assertEqual(np.asarray(data.reco).shape[0], nd_ + nb)
            self.assertEqual(np.asarray(data.reco_evt).shape[0], nd_ + nb)
            w = np.asarray(data.weight)
            self.assertTrue(np.all(np.isfinite(w)) and np.all(w >= 0))

    def test_data_count_from_measured_pc_not_measured_weights(self):
        a = small_g2_arrays(nd=30)
        self.assertNotIn("measured_weights", a)     # G2 dump omits the purity placeholder
        with tempfile.TemporaryDirectory() as td:
            _, _, _, _, _, meta = build(td, arrays=a)
            self.assertEqual(meta["target"]["n_data_rows"], 30)

    def test_decision_ready_telemetry(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, _, _, _, meta = build(td)
            t = meta["target"]
            for k in ("target_mode", "bootstrap_seed", "refinement", "refinement_backend",
                      "refinement_is_learned_production", "estimator_fingerprint",
                      "input_identity_hashes", "pot_scale", "raw_positive_sum", "raw_negative_sum",
                      "refined_sum", "refined_min", "refined_max", "n_floored_zero",
                      "n_data_rows", "n_bkg_rows", "n_measured_rows", "signed_target_hash"):
                self.assertIn(k, t, f"telemetry missing {k}")
            self.assertEqual(t["target_mode"], "negweight-refined")
            self.assertEqual(t["estimator_fingerprint"], "pet-fullevent-fps-v1")
            self.assertEqual(set(meta["input_identity_hashes"]), {"sig", "data", "bkg"})
            self.assertFalse(t["refinement_is_learned_production"])   # injected fn, not u2d default

    def test_no_all_ones_purity_substitution(self):
        with tempfile.TemporaryDirectory() as td:
            data, _, _, _, _, _ = build(td)
            w = np.asarray(data.weight)
            self.assertFalse(np.allclose(w, w.flat[0]))   # not a degenerate all-equal purity target


class FailClosed(unittest.TestCase):
    def test_missing_background_fails_closed(self):
        a = small_g2_arrays()
        for k in ("w_bkg", "bkg_part_reco", "bkg_reco_scalars"):
            b = dict(a); b.pop(k)
            with tempfile.TemporaryDirectory() as td:
                with self.assertRaises(ValueError):
                    build(td, arrays=b)

    def test_old_schema_fails_closed(self):
        a = small_g2_arrays(); a["petSchemaVersion"] = np.asarray("recoil-only-crosscheck")
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                build(td, arrays=a)

    def test_tampered_identity_fails_closed(self):
        a = small_g2_arrays(); a["data_identity_hash"] = np.asarray("deadbeef" * 8)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                build(td, arrays=a)

    def test_misaligned_background_rows_fails_closed(self):
        a = small_g2_arrays()
        a["bkg_reco_scalars"] = a["bkg_reco_scalars"][:-1]     # rows disagree with w_bkg
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                build(td, arrays=a, verify_identities=False)   # isolate the alignment guard

    def test_invalid_pot_scale_in_input_fails_closed(self):
        a = small_g2_arrays(); a["pot_scale"] = np.asarray(0.0)
        # remove data_pot/mc_pot so the loader cannot recompute a valid pot_scale
        a.pop("data_pot", None); a.pop("mc_pot", None)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                build(td, arrays=a)


class ReplicaReuseGuard(unittest.TestCase):
    def test_nominal_target_cannot_be_reused_for_replica(self):
        with self.assertRaises(ValueError):
            fed.assert_refined_target_is_replica({"bootstrap_seed": None}, bootstrap_seed=7)

    def test_wrong_seed_rejected(self):
        with self.assertRaises(ValueError):
            fed.assert_refined_target_is_replica({"bootstrap_seed": 3}, bootstrap_seed=7)

    def test_matching_seed_accepted(self):
        self.assertTrue(fed.assert_refined_target_is_replica({"bootstrap_seed": 7}, bootstrap_seed=7))

    def test_replica_target_differs_from_nominal(self):
        a = small_g2_arrays()
        with tempfile.TemporaryDirectory() as td:
            _, _, _, _, _, m0 = build(td, arrays=a, bootstrap_seed=None)
            _, _, _, _, _, m1 = build(td, arrays=a, bootstrap_seed=123)
            self.assertNotEqual(m0["target"]["signed_target_hash"],
                                m1["target"]["signed_target_hash"])
            fed.assert_refined_target_is_replica(m1["target"], bootstrap_seed=123)
            with self.assertRaises(ValueError):        # nominal cannot masquerade as this replica
                fed.assert_refined_target_is_replica(m0["target"], bootstrap_seed=123)


class FixtureVsProductionResolution(unittest.TestCase):
    def test_binned_helper_is_fixture_only_documented(self):
        # closed-form binned form needs a pre-assigned cell -> NOT the continuous production path
        self.assertIn("Production uses the trained classifier",
                      fed.stay_positive_refine_binned.__doc__)

    def test_learned_production_hook_present_but_deferred(self):
        # canonical production refinement is the deferred u2d.refine_stay_positive; we do NOT call it
        # here (u2d imports ROOT/TF -> segfaults on the login node). Just assert the hook exists.
        self.assertTrue(callable(fed.learned_stay_positive_refiner))


if __name__ == "__main__":
    unittest.main(verbosity=2)
