"""Login-safe tests for the G2 full-event dump CONTRACT (pet/fullevent_dump_contract.py).

No ROOT / no TF: fake in-memory sources exercise schema rejection, missing/tampered background,
identity/order mismatch, vector-length mismatch, interrupted output, and the forbidden purity
fallback. Actual PyROOT integration in dump_pointcloud_inputs.py is RUNTIME-BLOCKED (needs the
G2 ROOT) and is NOT exercised here."""
import os
import sys
import tempfile
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ND, "pet"))

import fullevent_dump_contract as fdc  # noqa: E402
import fullevent_fps_dataloader as fe  # noqa: E402


def valid_arrays(ns=6, nd=4, nb=3, P=5):
    rng = np.random.default_rng(0)
    a = {
        "part_gen": rng.random((ns, P, 5), np.float32),
        "part_reco": rng.random((ns, P, 3), np.float32),
        "reco_scalars": rng.random((ns, 4), np.float32),
        "reco_muon": rng.random((ns, 5), np.float32),
        "reco_vertex": rng.random((ns, 3), np.float32),
        "reco_view": rng.integers(0, 3, (ns, P)).astype(np.float32),
        "reco_time": rng.random((ns, P), np.float32),
        "pass_reco": (rng.random(ns) > 0.3), "pass_truth": (rng.random(ns) > 0.1),
        "w_truth": rng.random(ns), "w_reco": rng.random(ns),
        "truth_scalars": rng.random((ns, 4), np.float32),
        "measured_pc": rng.random((nd, P, 3), np.float32),
        "measured_scalars": rng.random((nd, 5), np.float32),
        "data_muon": rng.random((nd, 5), np.float32),
        "data_vertex": rng.random((nd, 3), np.float32),
        "data_view": rng.integers(0, 3, (nd, P)).astype(np.float32),
        "data_time": rng.random((nd, P), np.float32),
        "bkg_part_reco": rng.random((nb, P, 3), np.float32),
        "bkg_reco_scalars": rng.random((nb, 4), np.float32),
        "bkg_muon": rng.random((nb, 5), np.float32),
        "bkg_vertex": rng.random((nb, 3), np.float32),
        "bkg_view": rng.integers(0, 3, (nb, P)).astype(np.float32),
        "bkg_time": rng.random((nb, P), np.float32),
        "w_bkg": rng.random(nb), "bkg_indices": np.arange(nb),
        "edges_0": fe.CANONICAL_PT_EDGES, "edges_1": fe.CANONICAL_PPARALLEL_EDGES,
        "petSchemaVersion": "g2-fullevent-v1", "hasFullEventSchema": 1, "fullPhaseSpace": 1,
        "estimator_fingerprint": "pet-fullevent-fps-v1", "data_pot": 1.0,
    }
    a["sig_identity_hash"] = fdc.inventory_order_hash(a["w_truth"], a["pass_truth"])
    a["data_identity_hash"] = fdc.inventory_order_hash(a["measured_pc"])
    a["bkg_identity_hash"] = fdc.inventory_order_hash(a["w_bkg"], a["bkg_indices"])
    return a


class DumpContract(unittest.TestCase):
    def test_valid_write_atomic(self):
        a = valid_arrays()
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "g2.npz")
            fdc.write_fullevent_npz_atomic(out, a)
            self.assertTrue(os.path.exists(out))
            z = np.load(out, allow_pickle=True)
            self.assertIn("bkg_part_reco", z.files)
            self.assertEqual(str(z["petSchemaVersion"]), "g2-fullevent-v1")

    def test_schema_rejection(self):
        for bad in ({"petSchemaVersion": "recoil-only"}, {"hasFullEventSchema": 0},
                    {"fullPhaseSpace": 0}, {"petSchemaVersion": None}):
            a = valid_arrays(); a.update(bad)
            with self.assertRaises(ValueError):
                fdc.write_fullevent_npz_atomic(os.path.join(tempfile.gettempdir(), "x.npz"), a)

    def test_missing_background_manifest(self):
        a = valid_arrays(); del a["w_bkg"]
        with self.assertRaises(ValueError):
            fdc.write_fullevent_npz_atomic(os.path.join(tempfile.gettempdir(), "x.npz"), a)

    def test_forbidden_purity_fallback(self):
        a = valid_arrays(); a["measured_weights"] = np.ones(4)
        with self.assertRaises(ValueError):
            fdc.assert_no_purity_fallback(a, "negweight-refined")

    def test_tampered_background_identity(self):
        a = valid_arrays(); a["bkg_indices"] = np.roll(a["bkg_indices"], 1)  # hash now stale
        with self.assertRaises(ValueError):
            fdc.assert_identity_consistency(a)

    def test_signal_identity_order_mismatch(self):
        a = valid_arrays(); a["w_truth"] = a["w_truth"][::-1].copy()          # hash now stale
        with self.assertRaises(ValueError):
            fdc.assert_identity_consistency(a)

    def test_vector_length_mismatch(self):
        a = valid_arrays(); a["reco_view"] = a["reco_view"][:, :-1]           # token len != P
        with self.assertRaises(ValueError):
            fdc.assert_inventory_alignment(a)

    def test_row_count_mismatch(self):
        a = valid_arrays(); a["w_bkg"] = a["w_bkg"][:-1]                      # bkg rows misaligned
        with self.assertRaises(ValueError):
            fdc.assert_inventory_alignment(a)

    def test_interrupted_output_leaves_no_partial(self):
        a = valid_arrays()
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "g2.npz")
            orig = fdc.np.savez_compressed
            fdc.np.savez_compressed = lambda *x, **k: (_ for _ in ()).throw(IOError("disk full"))
            try:
                with self.assertRaises(IOError):
                    fdc.write_fullevent_npz_atomic(out, a)
            finally:
                fdc.np.savez_compressed = orig
            self.assertFalse(os.path.exists(out))                            # no partial at path
            self.assertEqual([f for f in os.listdir(td) if f.startswith(".g2dump_")], [])  # temp cleaned

    def test_generator_labels_never_required_features(self):
        for k in fdc.AUDIT_ONLY_KEYS:
            self.assertNotIn(k, fdc.REQUIRED_KEYS)   # bkg_nuPDG/current/inttype = audit only


if __name__ == "__main__":
    unittest.main(verbosity=2)
