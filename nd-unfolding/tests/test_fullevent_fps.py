"""P5A pure-function tests for the full-event FPS interface (KNOWN_ISSUES #19).

No TensorFlow: exercises the FPS domain guard, cloud builders + explicit KNN
coordinates, the three event-feature schemas, and the step-1 no-truth-leakage
invariant. The TF paired-training e2e is a separate GPU/CPU smoke."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND / "pet"))

import fullevent_fps_dataloader as fe  # noqa: E402


class FPSEdgeGuard(unittest.TestCase):
    def test_accepts_canonical(self):
        self.assertTrue(fe.assert_extended_fps_edges(
            fe.CANONICAL_PT_EDGES, fe.CANONICAL_PPARALLEL_EDGES))

    def test_rejects_paper_pt_top(self):
        bad = fe.CANONICAL_PT_EDGES.copy(); bad[-1] = 4.5  # paper top edge
        with self.assertRaises(ValueError):
            fe.assert_extended_fps_edges(bad, fe.CANONICAL_PPARALLEL_EDGES)

    def test_rejects_paper_ppar_bottom(self):
        bad = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0,
                        10.0, 15.0, 20.0, 40.0, 60.0], float)  # paper-style, starts at 1.5
        with self.assertRaises(ValueError):
            fe.assert_extended_fps_edges(fe.CANONICAL_PT_EDGES, bad)

    def test_rejects_reordered(self):
        bad = fe.CANONICAL_PT_EDGES.copy(); bad[1], bad[2] = bad[2], bad[1]
        with self.assertRaises(ValueError):
            fe.assert_extended_fps_edges(bad, fe.CANONICAL_PPARALLEL_EDGES)


class CloudBuilders(unittest.TestCase):
    def test_reco_cloud_coords_and_pad(self):
        part = np.zeros((3, 4, 3), np.float32)
        part[0, 0] = [1000., 200., 5000.]  # one real token (MeV, mm)
        cloud, coord = fe.build_reco_cloud(part)
        self.assertEqual(coord, (1, 2))                 # KNN uses (pos, z), not (E,pos)
        self.assertAlmostEqual(float(cloud[0, 0, 0]), 1.0, places=5)   # E MeV->GeV
        self.assertTrue(np.all(cloud[0, 1:] == 0))      # padding preserved as 0
        self.assertTrue(np.all(cloud[1:] == 0))

    def test_truth_cloud_angular_coords_pdg(self):
        part = np.zeros((2, 3, 5), np.float32)
        part[0, 0] = [2000., 0., 0., 2000., 2212.]      # proton, forward (pz)
        part[0, 1] = [1000., 0., 1000., 0., 211.]       # pi+, transverse +y
        cloud, coord = fe.build_truth_cloud(part)
        self.assertEqual(coord, (5, 6, 7))              # KNN = (theta, cos_phi, sin_phi), periodic
        self.assertEqual(cloud.shape[-1], 8)            # E,px,py,pz,pdg,theta,cos_phi,sin_phi
        self.assertAlmostEqual(float(cloud[0, 0, 5]), 0.0, places=5)          # theta forward
        self.assertAlmostEqual(float(cloud[0, 0, 6]), 1.0, places=5)          # cos_phi(0)=1
        self.assertAlmostEqual(float(cloud[0, 0, 7]), 0.0, places=5)          # sin_phi(0)=0
        self.assertAlmostEqual(float(cloud[0, 1, 5]), np.pi / 2, places=5)    # theta transverse
        self.assertAlmostEqual(float(cloud[0, 1, 6]), 0.0, places=5)          # cos_phi(pi/2)=0
        self.assertAlmostEqual(float(cloud[0, 1, 7]), 1.0, places=5)          # sin_phi(pi/2)=1
        self.assertAlmostEqual(float(cloud[0, 0, 4]), 2212.0, places=3)       # PDG retained
        self.assertTrue(np.all(cloud[0, 2, :] == 0))                          # padded token zeroed
        self.assertTrue(np.all(cloud[1] == 0))


class EventSchemas(unittest.TestCase):
    def _scalars(self, n=200, seed=0):
        rng = np.random.default_rng(seed)
        reco = np.stack([rng.uniform(0, 2, n), rng.uniform(1, 10, n),
                         rng.uniform(0, 1, n), rng.uniform(0, 2, n)], axis=1).astype(np.float32)
        truth = reco + rng.normal(0, 0.05, reco.shape).astype(np.float32)  # muon smearing
        meas = np.stack([rng.uniform(0, 2, n), rng.uniform(1, 10, n),
                         rng.uniform(0, 1, n), rng.uniform(0, 2, n)], axis=1).astype(np.float32)
        return reco, truth, meas

    def test_reco_data_same_schema_truth_distinct(self):
        reco, truth, meas = self._scalars()
        er, et, ed, meta = fe.build_event_features(reco, truth, meas)
        self.assertEqual(er.shape[1], ed.shape[1])          # reco == data feature dim
        self.assertEqual(er.shape[1], len(fe.DEFAULT_EVT_FEATURES))
        self.assertEqual(meta["feature_names"], list(fe.DEFAULT_EVT_FEATURES))
        # reco/data normalized with the SAME (reco) statistics; truth with its OWN
        self.assertNotEqual(meta["reco_norm_mean"], meta["truth_norm_mean"])
        self.assertTrue(np.all(np.isfinite(er)) and np.all(np.isfinite(et)) and np.all(np.isfinite(ed)))

    def test_no_truth_leakage_invariant(self):
        reco, truth, meas = self._scalars()
        er, et, ed, meta = fe.build_event_features(reco, truth, meas)
        self.assertTrue(fe.assert_no_truth_leakage(er, reco, truth, fe.DEFAULT_EVT_FEATURES))

    def test_leakage_detector_catches_truth_injection(self):
        reco, truth, meas = self._scalars()
        # forge an "event_reco" built from TRUTH scalars -> the detector must catch it
        cols = [fe.SCALAR_COLS[f] for f in fe.DEFAULT_EVT_FEATURES]
        rmu = reco[:, cols].mean(0); rsd = reco[:, cols].std(0) + 1e-6
        leaked = (truth[:, cols] - rmu) / rsd
        with self.assertRaises(AssertionError):
            fe.assert_no_truth_leakage(leaked.astype(np.float32), reco, truth,
                                       fe.DEFAULT_EVT_FEATURES)

    def test_sentinel_pass_masked_normalization(self):
        # Regression for the FPS reco-muon sentinel bug: reco muon = -9999 where !pass_reco.
        # Normalization must use pass_reco rows only, and !pass rows must be zeroed post-norm.
        reco, truth, meas = self._scalars(n=400, seed=3)
        pr = np.zeros(400, bool); pr[:250] = True          # 250 real, 150 misses
        reco[~pr, :] = -9999.0                              # sentinel in the miss rows
        pt = np.ones(400, bool)
        er, et, ed, meta = fe.build_event_features(reco, truth, meas, pass_reco=pr, pass_truth=pt)
        cols = [fe.SCALAR_COLS[f] for f in fe.DEFAULT_EVT_FEATURES]
        # norm mean must be the pass_reco muon mean (physical, ~O(1)), NOT polluted by -9999
        expected_mu = reco[pr][:, cols].mean(0)
        np.testing.assert_allclose(meta["reco_norm_mean"], expected_mu, rtol=1e-4)
        self.assertLess(abs(meta["reco_norm_mean"][0]), 100.0)   # not the -5732 pathology
        self.assertTrue(np.all(er[~pr] == 0.0))            # undefined reco rows zeroed
        self.assertTrue(np.all(np.isfinite(er)))
        # leakage detector must still pass with pass_reco supplied
        self.assertTrue(fe.assert_no_truth_leakage(er, reco, truth, fe.DEFAULT_EVT_FEATURES,
                                                   pass_reco=pr))


class CLM007DataScalarGuard(unittest.TestCase):
    """Regression for CLM-007: build_fullevent_loaders must FAIL CLOSED on a missing data
    'measured_scalars' rather than silently falling back to MC reco_scalars (sentinel/misalign).
    These paths raise before the vendored-engine (TF) import, so they run on the login node."""

    def _make_pc_npz(self, path, with_measured_scalars=False, N=24, M=10, P=12):
        rng = np.random.default_rng(0)
        arr = dict(
            part_reco=rng.random((N, P, 3)).astype("f4"),
            part_gen=rng.random((N, P, 5)).astype("f4"),
            measured_pc=rng.random((M, P, 3)).astype("f4"),
            reco_scalars=rng.random((N, 4)).astype("f4"),
            truth_scalars=rng.random((N, 4)).astype("f4"),
            pass_reco=(rng.random(N) > 0.3), pass_truth=(rng.random(N) > 0.1),
            w_truth=np.ones(N, "f4"), measured_weights=np.ones(M, "f4"),
            edges_0=fe.CANONICAL_PT_EDGES, edges_1=fe.CANONICAL_PPARALLEL_EDGES,
            # G2 schema marker so build_fullevent_loaders passes the schema gate and reaches the
            # CLM-007 / needs-background guards these tests actually target (Gate-2 rewire).
            petSchemaVersion="g2-fullevent-v1",
        )
        if with_measured_scalars:
            arr["measured_scalars"] = rng.random((M, 4)).astype("f4")
        np.savez(path, **arr)

    def test_fail_closed_when_no_data_scalars(self):
        with tempfile.TemporaryDirectory() as td:
            pc = os.path.join(td, "pc.npz"); self._make_pc_npz(pc)
            with self.assertRaises(ValueError):        # CLM-007 guard fires, no silent fallback
                fe.build_fullevent_loaders(pc, enforce_fps_edges=True)

    def test_row_count_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            pc = os.path.join(td, "pc.npz"); self._make_pc_npz(pc, M=10)
            ds = os.path.join(td, "ds.npz"); np.savez(ds, measured=np.zeros((7, 5), "f4"))
            with self.assertRaises(ValueError):        # 7 data-scalar rows != 10 measured_pc rows
                fe.build_fullevent_loaders(pc, data_scalars_npz=ds, enforce_fps_edges=True)


class F7CoherentBootstrap(unittest.TestCase):
    """F7 coherent estimator-bootstrap over the 3 inventories (data, signal-MC, background-MC).
    Pure numpy; proves the P5B C_stat gate properties without TF/GPU."""

    def test_deterministic_replay(self):
        a = fe.coherent_bootstrap_factors(100, 200, 50, seed=7)
        b = fe.coherent_bootstrap_factors(100, 200, 50, seed=7)
        for x, y in zip(a, b):
            self.assertTrue(np.array_equal(x, y))                 # same seed -> identical draw
        self.assertFalse(np.array_equal(a[1], fe.coherent_bootstrap_factors(100, 200, 50, seed=8)[1]))

    def test_global_before_subset(self):
        from pet_bootstrap import mc_poisson_factor
        N, M, nb, seed = 500, 300, 80, 3
        data_f, sig_f, bkg_f = fe.coherent_bootstrap_factors(M, N, nb, seed=seed)
        imc = np.sort(np.random.default_rng(1).choice(N, 120, replace=False))
        ida = np.sort(np.random.default_rng(2).choice(M, 90, replace=False))
        ibk = np.sort(np.random.default_rng(3).choice(nb, 40, replace=False))
        # each subset factor is the RESTRICTION of the ONE global draw (data/signal/background),
        # never a post-subset redraw
        self.assertTrue(np.array_equal(sig_f[imc], mc_poisson_factor(N, seed)[imc]))
        self.assertTrue(np.array_equal(
            data_f[ida], np.random.default_rng(seed).poisson(1.0, M).astype(np.uint8)[ida]))
        self.assertTrue(np.array_equal(
            bkg_f[ibk],
            np.random.default_rng(seed + 20_000_000).poisson(1.0, nb).astype(np.uint8)[ibk]))

    def test_same_training_and_extraction_mc(self):
        N, nb, seed = 400, 60, 5
        _, sig, bkg = fe.coherent_bootstrap_factors(80, N, nb, seed=seed)
        imc = np.sort(np.random.default_rng(0).choice(N, 100, replace=False))
        store = {"mc_indices": imc, "sig_bootstrap_factor": sig[imc], "bootstrap_seed": seed,
                 "bkg_indices": np.arange(nb), "bkg_bootstrap_factor": bkg,
                 "estimator_fingerprint": "pet-fullevent-fps-v1", "inventory_hashes": "H"}
        self.assertTrue(fe.validate_coherent_bootstrap(
            store, bootstrap_seed=seed, n_sig_full=N, n_bkg_full=nb,
            estimator_fingerprint="pet-fullevent-fps-v1", inventory_hashes="H"))

    def test_background_factor_before_refinement(self):
        rng = np.random.default_rng(0); nd_, nb_, nc = 300, 120, 8
        dcell = rng.integers(0, nc, nd_); bcell = rng.integers(0, nc, nb_)
        wbkg = rng.uniform(0.5, 1.5, nb_)
        df = np.ones(nd_, np.uint8)
        d1, b1 = fe.build_negweight_refined_target(dcell, bcell, wbkg, 1.0, nc, df, np.ones(nb_, np.uint8))
        d2, b2 = fe.build_negweight_refined_target(dcell, bcell, wbkg, 1.0, nc, df,
                                                   rng.integers(0, 3, nb_).astype(np.uint8))
        self.assertFalse(np.allclose(d1, d2))                    # bkg factor entered before refine
        self.assertTrue(np.all(d1 >= 0) and np.all(b1 >= 0))     # Stay-Positive: non-negative

    def test_no_nominal_refinement_reuse(self):
        rng = np.random.default_rng(1); nd_, nb_, nc = 300, 120, 8
        dcell = rng.integers(0, nc, nd_); bcell = rng.integers(0, nc, nb_); wbkg = rng.uniform(0.5, 1.5, nb_)
        dfA, _, bfA = fe.coherent_bootstrap_factors(nd_, 10, nb_, seed=11)
        dfB, _, bfB = fe.coherent_bootstrap_factors(nd_, 10, nb_, seed=12)
        dA, _ = fe.build_negweight_refined_target(dcell, bcell, wbkg, 1.0, nc, dfA, bfA)
        dB, _ = fe.build_negweight_refined_target(dcell, bcell, wbkg, 1.0, nc, dfB, bfB)
        self.assertFalse(np.allclose(dA, dB))                    # per-replica rebuild, not copied

    def test_mismatch_fails_closed(self):
        N, seed = 300, 9
        _, sig, _ = fe.coherent_bootstrap_factors(50, N, 20, seed=seed)
        base = {"mc_indices": np.arange(N), "sig_bootstrap_factor": sig, "bootstrap_seed": seed,
                "estimator_fingerprint": "pet-fullevent-fps-v1", "inventory_hashes": "H"}
        with self.assertRaises(ValueError):                      # wrong seed
            fe.validate_coherent_bootstrap(base, bootstrap_seed=seed + 1, n_sig_full=N)
        bad = dict(base); bad["sig_bootstrap_factor"] = sig.copy(); bad["sig_bootstrap_factor"][0] += 1
        with self.assertRaises(ValueError):                      # tampered factor / redraw
            fe.validate_coherent_bootstrap(bad, bootstrap_seed=seed, n_sig_full=N)
        with self.assertRaises(ValueError):                      # wrong fingerprint
            fe.validate_coherent_bootstrap(base, bootstrap_seed=seed, n_sig_full=N,
                                           estimator_fingerprint="pet-reduced-fps-cross")
        with self.assertRaises(ValueError):                      # wrong inventory hash
            fe.validate_coherent_bootstrap(base, bootstrap_seed=seed, n_sig_full=N,
                                           inventory_hashes="different")
        # --- background inventory (3rd inventory): tamper + omission fail closed ---
        N2, nb, s2 = 300, 40, 4
        _, sig2, bkg2 = fe.coherent_bootstrap_factors(50, N2, nb, seed=s2)
        bstore = {"mc_indices": np.arange(N2), "sig_bootstrap_factor": sig2, "bootstrap_seed": s2,
                  "bkg_indices": np.arange(nb), "bkg_bootstrap_factor": bkg2,
                  "bkg_inventory_hash": "BG"}
        self.assertTrue(fe.validate_coherent_bootstrap(                     # valid full 3-inv check
            bstore, bootstrap_seed=s2, n_sig_full=N2, n_bkg_full=nb, bkg_inventory_hash="BG"))
        bad = dict(bstore); bad["bkg_bootstrap_factor"] = bkg2.copy(); bad["bkg_bootstrap_factor"][0] += 1
        with self.assertRaises(ValueError):                                # tampered bkg factor
            fe.validate_coherent_bootstrap(bad, bootstrap_seed=s2, n_sig_full=N2, n_bkg_full=nb)
        bad = dict(bstore); bad["bkg_indices"] = np.roll(np.arange(nb), 1)
        with self.assertRaises(ValueError):                                # tampered bkg indices/order
            fe.validate_coherent_bootstrap(bad, bootstrap_seed=s2, n_sig_full=N2, n_bkg_full=nb)
        with self.assertRaises(ValueError):                                # n_bkg_full omitted
            fe.validate_coherent_bootstrap(bstore, bootstrap_seed=s2, n_sig_full=N2)
        bad = {k: v for k, v in bstore.items() if k != "bkg_indices"}
        with self.assertRaises(ValueError):                                # bkg order evidence omitted
            fe.validate_coherent_bootstrap(bad, bootstrap_seed=s2, n_sig_full=N2, n_bkg_full=nb)
        with self.assertRaises(ValueError):                                # wrong bkg inventory hash
            fe.validate_coherent_bootstrap(bstore, bootstrap_seed=s2, n_sig_full=N2, n_bkg_full=nb,
                                           bkg_inventory_hash="WRONG")

    def test_negweight_refined_fails_closed_without_background(self):
        with tempfile.TemporaryDirectory() as td:
            pc = os.path.join(td, "pc.npz")
            CLM007DataScalarGuard()._make_pc_npz(pc)             # no w_bkg, no measured_scalars
            ds = os.path.join(td, "ds.npz"); np.savez(ds, measured=np.zeros((10, 5), "f4"))
            with self.assertRaises(ValueError):                 # nominal needs bkg inventory
                fe.build_fullevent_loaders(pc, data_scalars_npz=ds, enforce_fps_edges=True,
                                           bkg_mode="negweight-refined")


class PublicationConfigGate(unittest.TestCase):
    """No-GPU dry-run: a publication full-event run must require the full fingerprint, G2
    full-schema, negweight-refined, and a real background inventory; recoil/purity/old aborts."""

    def _valid(self):
        return {"estimator_fingerprint": "pet-fullevent-fps-v1", "bkg_mode": "negweight-refined",
                "petSchemaVersion": "g2-fullevent-v1", "hasFullEventSchema": 1, "fullPhaseSpace": 1,
                "has_background": True,
                "input": "of_inputs_pc_fps_fullevent_g2.npz"}

    def test_valid_publication_config_passes(self):
        self.assertTrue(fe.assert_publication_config(self._valid()))

    def test_reduced_fingerprint_aborts(self):
        c = self._valid(); c["estimator_fingerprint"] = "pet-reduced-fps-cross"
        with self.assertRaises(ValueError):
            fe.assert_publication_config(c)

    def test_purity_bkg_mode_aborts(self):
        c = self._valid(); c["bkg_mode"] = "purity"
        with self.assertRaises(ValueError):
            fe.assert_publication_config(c)

    def test_missing_g2_schema_aborts(self):
        c = self._valid(); c["hasFullEventSchema"] = 0
        with self.assertRaises(ValueError):
            fe.assert_publication_config(c)

    def test_no_background_aborts(self):
        c = self._valid(); c["has_background"] = False
        with self.assertRaises(ValueError):
            fe.assert_publication_config(c)

    def test_recoil_or_xps2_input_aborts(self):
        for bad in ("of_inputs_pc_fullcloud_bkgsub_5d.npz", "of_inputs_pc_fps_xps2.npz"):
            c = self._valid(); c["input"] = bad
            with self.assertRaises(ValueError):
                fe.assert_publication_config(c)


if __name__ == "__main__":
    unittest.main(verbosity=2)
