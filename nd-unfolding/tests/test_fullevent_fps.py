"""P5A pure-function tests for the full-event FPS interface (KNOWN_ISSUES #19).

No TensorFlow: exercises the FPS domain guard, cloud builders + explicit KNN
coordinates, the three event-feature schemas, and the step-1 no-truth-leakage
invariant. The TF paired-training e2e is a separate GPU/CPU smoke."""
import sys
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
        # token with px=py=0, pz>0 -> theta=0; token along +x -> phi=0, theta=pi/2
        part[0, 0] = [2000., 0., 0., 2000., 2212.]      # proton, forward
        part[0, 1] = [1000., 1000., 0., 0., 211.]       # pi+, transverse +x
        cloud, coord = fe.build_truth_cloud(part)
        self.assertEqual(coord, (5, 6))                 # KNN uses (theta, phi)
        self.assertEqual(cloud.shape[-1], 7)            # E,px,py,pz,pdg,theta,phi
        self.assertAlmostEqual(float(cloud[0, 0, 5]), 0.0, places=5)          # theta forward
        self.assertAlmostEqual(float(cloud[0, 1, 5]), np.pi / 2, places=5)    # theta transverse
        self.assertAlmostEqual(float(cloud[0, 0, 4]), 2212.0, places=3)       # PDG retained
        # padded token angular coords are zeroed
        self.assertTrue(np.all(cloud[0, 2, :] == 0))
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
