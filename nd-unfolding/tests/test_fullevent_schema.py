"""The full-event schema actually IS the full event (AUDIT-FINDINGS-20260731 J01).

Three things this file establishes that no existing test could:

  1. The loader's mirrored column orders equal the DUMPER's, read out of
     `dump_pointcloud_inputs`' own constants. `fullevent_fps_dataloader` cannot import that
     module (it pulls ROOT at use time) so it mirrors `RECO_MUON_BRANCHES` / `RECO_VERTEX_BRANCHES`
     by hand -- and a hand-mirrored column order is exactly the thing that goes stale silently. It
     already had: `make_synthetic_g2_fullevent._muon` built a 6-column block against the dumper's
     7 and passed every G2 gate, because `assert_inventory_alignment` checks the muon block's rows
     and never its width.
  2. Every G2 extension array reaches the estimator, end to end through
     `build_fullevent_loaders` on a contract-valid fixture. Stated as sensitivity (permute the
     source, the output must move) rather than as a name list, because a name list is satisfied by
     a loader that reads the array and drops it.
  3. The reduced `pet-reduced-fps-cross` schema stays selectable and stays labelled.

Login-safe. The vendored numpy-only DataLoader is loaded from THIS repo (not the /pscratch
literal `test_fullevent_gate2.py` uses) and sys.modules is restored afterwards, so this file runs
off Perlmutter without rescuing that module's documented platform failures.
"""
import contextlib
import importlib.util
import os
import sys
import tempfile
import types
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(ND)
for _p in (os.path.join(ND, "pet"), ND):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import dump_pointcloud_inputs as dp        # noqa: E402  (ROOT deferred to use time)
import fullevent_fps_dataloader as fed     # noqa: E402
import make_synthetic_g2_fullevent as syn  # noqa: E402


@contextlib.contextmanager
def real_dataloader():
    """Install the numpy-only omnifold.dataloader for the duration of the block, then restore
    sys.modules exactly as found (see test_b1_normalization_fix's note on why restoring matters).

    PRESENCE IS NOT ENOUGH, and this cost a debugging round. `test_fullevent_gate2._load_real_-
    dataloader` resolves the same import through the frozen /pscratch literal; off Perlmutter that
    raises FileNotFoundError *after* `sys.modules["omnifold.dataloader"]` has been assigned, so it
    leaves a poisoned EMPTY module behind. This file sorts after that one, so a `not in
    sys.modules` guard would hand the loader a module with no `DataLoader` in it and the failure
    would surface here, inside code that is fine, as an ImportError from `build_fullevent_loaders`.
    The check is therefore on the attribute, not on the key."""
    keys = ("omnifold", "omnifold.dataloader")
    saved = {k: sys.modules.get(k) for k in keys}
    present = {k: k in sys.modules for k in keys}
    try:
        dlp = os.path.join(ROOT, "omnifold_nn", "omnifold", "dataloader.py")
        if "omnifold" not in sys.modules:
            pkg = types.ModuleType("omnifold")
            pkg.__path__ = [os.path.dirname(dlp)]
            sys.modules["omnifold"] = pkg
        if not hasattr(sys.modules.get("omnifold.dataloader"), "DataLoader"):
            spec = importlib.util.spec_from_file_location("omnifold.dataloader", dlp)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["omnifold.dataloader"] = mod
            spec.loader.exec_module(mod)
        yield sys.modules["omnifold.dataloader"]
    finally:
        for k in keys:
            if present[k]:
                sys.modules[k] = saved[k]
            else:
                sys.modules.pop(k, None)


def sklearn_refine(feat, signed, **kw):
    """Algorithm-identical login-safe stand-in for u2d.refine_stay_positive (which imports ROOT)."""
    from sklearn.ensemble import GradientBoostingClassifier
    feat = np.asarray(feat, float)
    signed = np.asarray(signed, float)
    lab = (signed > 0).astype(int)
    absw = np.abs(signed)
    clf = GradientBoostingClassifier(random_state=0, n_estimators=20)
    clf.fit(feat, lab, sample_weight=absw)
    g = np.clip(clf.predict_proba(feat)[:, 1], 1e-6, 1.0 - 1e-6)
    fac = 2.0 * g - 1.0
    return absw * np.clip(fac, 0.0, None), g, float((fac < 0).mean())


def synthetic(td, name="G2.npz", **over):
    """A contract-valid g2-fullevent-v1 fixture, written through the SAME gates a real dump is."""
    kw = dict(n_sig=600, n_data=200, n_bkg=80, tokens=6, seed=4,
              fingerprint="pet-fullevent-fps-v1")
    kw.update(over)
    arrays = syn.build(**kw)
    import fullevent_dump_contract as fdc
    path = os.path.join(td, name)
    fdc.write_fullevent_npz_atomic(path, arrays)
    return path, arrays


class MirroredColumnOrders(unittest.TestCase):
    """The loader's constants against the dumper's, so the mirror cannot go stale silently."""

    def test_muon_columns_match_the_dumper(self):
        want = {name: i for i, name in enumerate(dp.RECO_MUON_BRANCHES)}
        got = {f"mu_{k.split('mu_reco_')[1]}": v for k, v in want.items()}
        self.assertEqual(fed.MUON_COLS, got)
        self.assertEqual(fed.N_MUON_COLS, dp.NUM_MUON)

    def test_vertex_columns_match_the_dumper(self):
        want = {f"vtx_{b.split('vtx_reco_')[1]}": i
                for i, b in enumerate(dp.RECO_VERTEX_BRANCHES)}
        self.assertEqual(fed.VERTEX_COLS, want)
        self.assertEqual(fed.N_VERTEX_COLS, dp.NUM_VTX)

    def test_sentinel_matches_the_dumper(self):
        self.assertEqual(fed.SENTINEL, dp.SENTINEL)

    def test_the_synthetic_fixture_matches_the_dumper_widths(self):
        """The specific drift that existed: a 6-column placeholder muon."""
        rng = np.random.default_rng(0)
        self.assertEqual(syn._muon(rng, 5).shape, (5, dp.NUM_MUON))
        self.assertEqual(syn._vertex(rng, 5).shape, (5, dp.NUM_VTX))

    def test_the_synthetic_fixture_stamps_the_miss_sentinel(self):
        rng = np.random.default_rng(0)
        pr = np.array([True, False, True, False, True])
        m = syn._muon(rng, 5, pr)
        v = syn._vertex(rng, 5, pr)
        s = syn._scalars(rng, 5, pr)
        for arr in (v, s):
            self.assertTrue(np.all(arr[~pr] == dp.SENTINEL))
        self.assertTrue(np.all(m[~pr, :dp.NUM_MUON - 1] == dp.SENTINEL))
        # minos_ok is 0 on a miss, not -9999 (dump_pointcloud_inputs.reco_muon_row)
        self.assertTrue(np.all(m[~pr, fed.MUON_COLS["mu_minos_ok"]] == 0.0))
        self.assertTrue(np.all(m[pr] != dp.SENTINEL))


class EveryExtensionArrayReachesTheEstimator(unittest.TestCase):
    """End to end through build_fullevent_loaders on a contract-valid fixture."""

    @classmethod
    def setUpClass(cls):
        cls._td = tempfile.TemporaryDirectory()
        cls.path, cls.arrays = synthetic(cls._td.name)

    @classmethod
    def tearDownClass(cls):
        cls._td.cleanup()

    def _build(self, path=None, **kw):
        kw.setdefault("refine_fn", sklearn_refine)
        kw.setdefault("bkg_mode", "negweight-refined")
        kw.setdefault("max_events", 400)
        with real_dataloader():
            return fed.build_fullevent_loaders(path or self.path, **kw)

    def test_reco_cloud_carries_view_and_time(self):
        _data, mc, _imc, coord_reco, _cg, meta = self._build()
        self.assertEqual(np.asarray(mc.reco).shape[-1], 5)
        self.assertEqual(meta["reco_cloud_cols"], ["E", "pos", "z", "view", "time"])
        self.assertTrue(meta["token_view_time_read"])
        self.assertEqual(coord_reco, (1, 2))

    def test_the_measured_and_background_clouds_carry_them_too(self):
        """Not just the MC leg: a data cloud one column narrower than the MC cloud would be a
        step-1 classifier told which side of the comparison it is on."""
        data, mc, _imc, _cr, _cg, _meta = self._build()
        self.assertEqual(np.asarray(data.reco).shape[-1], np.asarray(mc.reco).shape[-1])

    def test_event_block_is_the_full_schema_and_the_truth_block_is_not(self):
        _data, mc, _imc, _cr, _cg, meta = self._build()
        self.assertEqual(meta["feature_names"], list(fed.DEFAULT_EVT_FEATURES))
        self.assertEqual(meta["truth_feature_names"], list(fed.DEFAULT_TRUTH_EVT_FEATURES))
        self.assertEqual(np.asarray(mc.reco_evt).shape[1], meta["n_evt_reco"])
        self.assertEqual(np.asarray(mc.gen_evt).shape[1], meta["n_evt_truth"])
        self.assertGreater(meta["n_evt_reco"], meta["n_evt_truth"])
        # the alias the recoil-era callers read must track the RECO leg, not average the two
        self.assertEqual(meta["n_evt"], meta["n_evt_reco"])

    def test_perturbing_each_extension_array_moves_the_estimator_input(self):
        """The J01 regression proper. For every extension array the dump carries, permute one
        column and require the built input to change. A permutation leaves the mean and standard
        deviation fixed, so it cannot be absorbed by the z-score the way a shift or a scale is --
        the only thing it can detect is whether the values reach the output."""
        base_data, base_mc, _i, _cr, _cg, _m = self._build()
        base_reco_evt = np.asarray(base_mc.reco_evt).copy()
        base_cloud = np.asarray(base_mc.reco).copy()
        rng = np.random.default_rng(1)
        cases = {
            "reco_muon": ("evt", 0), "reco_vertex": ("evt", 0),
            "reco_view": ("cloud", None), "reco_time": ("cloud", None),
        }
        for key, (which, col) in cases.items():
            arrays = dict(self.arrays)
            a = np.array(arrays[key], copy=True)
            perm = rng.permutation(a.shape[0])
            if col is None:
                a[:] = a[perm]
            else:
                a[:, col] = a[perm, col]
            arrays[key] = a
            with tempfile.TemporaryDirectory() as td:
                p = os.path.join(td, "bumped.npz")
                np.savez(p, **arrays)
                _d, mc, _i2, _c1, _c2, _m2 = self._build(p, verify_identities=False)
                got = (np.asarray(mc.reco_evt) if which == "evt" else np.asarray(mc.reco))
                ref = base_reco_evt if which == "evt" else base_cloud
                self.assertFalse(np.allclose(got, ref),
                                 f"'{key}' does not reach the estimator -- it is not read")

    def test_the_refiner_is_fitted_in_the_classifier_feature_space(self):
        """B-5 / J05: the Stay-Positive target used to be learned on (pT, p||) alone and then
        attached to cloud-plus-event space, so background structure anywhere else could only be
        subtracted on average. Recorded, and required to be the full block."""
        _data, _mc, _imc, _cr, _cg, meta = self._build()
        tgt = meta["target"]
        self.assertEqual(list(tgt["refinement_feature_names"]), list(fed.DEFAULT_EVT_FEATURES))
        self.assertIn("event_reco block", tgt["refinement_feature_space"])
        # ...and it says out loud what it still does NOT cover, so the narrowing is not read as
        # a closure of J05.
        self.assertIn("cloud still excluded", tgt["refinement_feature_space"])

    def test_widening_the_refiner_actually_changed_the_target(self):
        """A claim that the refiner sees more features is worth nothing unless the refined
        weights differ from the ones the reduced space produced."""
        _d1, _m1, _i1, _c1, _c2, full = self._build()
        _d2, _m2, _i2, _c3, _c4, red = self._build(feature_names=fed.REDUCED_EVT_FEATURES)
        # The SIGNED inventory is identical either way (same rows, same w_bkg, same pot_scale) --
        # only the space g(x) is fitted in differs. So the signed hash matching while the refined
        # weights differ is the precise statement: same target, different conditioning.
        self.assertEqual(full["target"]["signed_target_hash"],
                         red["target"]["signed_target_hash"])
        self.assertNotAlmostEqual(full["target"]["refined_sum"], red["target"]["refined_sum"],
                                  places=6)

    def test_reduced_schema_runs_and_is_labelled(self):
        _data, mc, _imc, _cr, _cg, meta = self._build(feature_names=fed.REDUCED_EVT_FEATURES)
        self.assertEqual(meta["n_evt_reco"], 2)
        self.assertEqual(meta["feature_names"], list(fed.REDUCED_EVT_FEATURES))
        # the cloud still carries view/time: the reduction is of the EVENT block only
        self.assertEqual(np.asarray(mc.reco).shape[-1], 5)


class FailClosedOnANarrowerInput(unittest.TestCase):
    def test_a_dump_without_the_muon_block_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path, arrays = synthetic(td)
            arrays = {k: v for k, v in arrays.items() if k != "reco_muon"}
            p2 = os.path.join(td, "no_muon.npz")
            np.savez(p2, **arrays)
            with real_dataloader():
                with self.assertRaises(ValueError) as cm:
                    fed.build_fullevent_loaders(p2, max_events=100, refine_fn=sklearn_refine,
                                                verify_identities=False)
            msg = str(cm.exception)
            self.assertIn("reco_muon", msg)
            self.assertIn("full-event dump", msg)

    def test_a_sidecar_data_leg_cannot_serve_a_wide_schema(self):
        """CLM-007 extended: the sidecar carries scalars only, so a wide MC schema paired with it
        would have no data muon at all."""
        with tempfile.TemporaryDirectory() as td:
            path, arrays = synthetic(td)
            arrays = {k: v for k, v in arrays.items() if k != "measured_scalars"}
            p2 = os.path.join(td, "no_meas.npz")
            np.savez(p2, **arrays)
            side = os.path.join(td, "sidecar.npz")
            n_data = int(np.asarray(arrays["measured_pc"]).shape[0])
            np.savez(side, measured_scalars=np.zeros((n_data, 4), np.float32))
            with real_dataloader():
                with self.assertRaises(ValueError) as cm:
                    fed.build_fullevent_loaders(p2, max_events=100, data_scalars_npz=side,
                                                refine_fn=sklearn_refine,
                                                verify_identities=False)
            self.assertIn("CLM-007", str(cm.exception))

    def test_a_background_inventory_without_the_muon_block_is_refused(self):
        """The injected background rows must live in the SAME feature space as the data rows they
        are subtracted from, or the negweight target is comparing two different things."""
        with tempfile.TemporaryDirectory() as td:
            path, arrays = synthetic(td)
            arrays = {k: v for k, v in arrays.items() if k != "bkg_muon"}
            p2 = os.path.join(td, "no_bkg_muon.npz")
            np.savez(p2, **arrays)
            with real_dataloader():
                with self.assertRaises(ValueError) as cm:
                    fed.build_fullevent_loaders(p2, max_events=100, refine_fn=sklearn_refine,
                                                verify_identities=False)
            self.assertIn("bkg_muon", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
