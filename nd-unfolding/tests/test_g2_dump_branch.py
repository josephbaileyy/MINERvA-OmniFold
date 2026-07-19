"""Login-safe tests for the G2 full-event READ branch of pet/dump_pointcloud_inputs.py.

No ROOT / no TF. These exercise the pure, ROOT-free pieces of the publication-default G2 dump:
  * branch-name / manifest mapping (authoritative C++ schema -> contract REQUIRED_KEYS);
  * retained extended-FPS domain exclusion (pT in [0,30], p_parallel in [0,120] GeV);
  * per-token cloud padding with ALIGNED view/time;
  * native truth-only miss preservation + step-1 truth-leakage sentinel guard;
  * identity/order hashes + background alignment + fail-closed missing-branch/tamper.

The actual PyROOT read (_read_signal/_read_data/_read_background_inventory, _run_g2_dump) needs a
COMPUTE node + the G2 ROOT and is the RUNTIME step -- NOT exercised here. The row-level decision
logic those loops call (select_signal_row / in_fps_domain / reco_*_row / pad_*) IS covered, and the
final assembler (finalize_g2_arrays) is round-tripped through the write contract."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ND, "pet"))

import dump_pointcloud_inputs as dp   # noqa: E402  (ROOT deferred -> login-safe import)
import fullevent_dump_contract as fdc  # noqa: E402
import fullevent_fps_dataloader as fed  # noqa: E402


def synth_inventories(ns=6, nd=5, nb=4, P=12, seed=0):
    """Build three already-domain-filtered inventory dicts whose keys are the FINAL contract
    output names the readers emit (so finalize_g2_arrays is exercised exactly as at runtime)."""
    rng = np.random.default_rng(seed)
    sig = dict(
        part_reco=rng.random((ns, P, 3), np.float32), reco_scalars=rng.random((ns, 4), np.float32),
        reco_muon=rng.random((ns, dp.NUM_MUON), np.float32),
        reco_vertex=rng.random((ns, 3), np.float32),
        reco_view=rng.integers(0, 4, (ns, P)).astype(np.float32),
        reco_time=rng.random((ns, P), np.float32), part_gen=rng.random((ns, P, 5), np.float32),
        truth_scalars=rng.random((ns, 4), np.float32),
        pass_reco=(rng.random(ns) > 0.3), pass_truth=np.ones(ns, bool),
        w_truth=rng.random(ns).astype(np.float32), w_reco=rng.random(ns).astype(np.float32))
    data = dict(
        measured_pc=rng.random((nd, P, 3), np.float32),
        measured_scalars=rng.random((nd, 4), np.float32),
        data_muon=rng.random((nd, dp.NUM_MUON), np.float32),
        data_vertex=rng.random((nd, 3), np.float32),
        data_view=rng.integers(0, 4, (nd, P)).astype(np.float32),
        data_time=rng.random((nd, P), np.float32))
    bkg = dict(
        bkg_part_reco=rng.random((nb, P, 3), np.float32),
        bkg_reco_scalars=rng.random((nb, 4), np.float32),
        bkg_muon=rng.random((nb, dp.NUM_MUON), np.float32),
        bkg_vertex=rng.random((nb, 3), np.float32),
        bkg_view=rng.integers(0, 4, (nb, P)).astype(np.float32),
        bkg_time=rng.random((nb, P), np.float32),
        w_bkg=(rng.random(nb) + 0.5).astype(np.float32),
        bkg_nuPDG=rng.integers(-14, 15, nb), bkg_current=np.ones(nb, int),
        bkg_inttype=rng.integers(1, 5, nb))
    return sig, data, bkg


def finalize(sig, data, bkg, num_part=12, data_pot=8.97e19, mc_pot=4.07e20, pot_scale=0.22):
    return dp.finalize_g2_arrays(sig, data, bkg, data_pot=data_pot, mc_pot=mc_pot,
                                 pot_scale=pot_scale, edges_pt=fed.CANONICAL_PT_EDGES,
                                 edges_pz=fed.CANONICAL_PPARALLEL_EDGES, num_part=num_part)


class BranchNameMapping(unittest.TestCase):
    """The dumper's branch-name constants must match Agent-E's authoritative G2 C++ dump exactly;
    a drift here would silently read the wrong branch. Independent expected copies below."""
    def test_reco_cloud_and_token_branches(self):
        self.assertEqual(dp.RECO_CLOUD_BRANCHES, ("part_reco_E", "part_reco_pos", "part_reco_z"))
        self.assertEqual((dp.RECO_VIEW_BRANCH, dp.RECO_TIME_BRANCH),
                         ("part_reco_view", "part_reco_time"))

    def test_truth_cloud_branches(self):
        self.assertEqual(dp.TRUTH_CLOUD_BRANCHES,
                         ("part_gen_E", "part_gen_px", "part_gen_py", "part_gen_pz", "part_gen_pdg"))

    def test_muon_vertex_branches(self):
        self.assertEqual(dp.RECO_MUON_BRANCHES,
                         ("mu_reco_px", "mu_reco_py", "mu_reco_pz", "mu_reco_E",
                          "mu_reco_phi", "mu_reco_qp", "mu_reco_minos_ok"))
        self.assertEqual(dp.RECO_VERTEX_BRANCHES, ("vtx_reco_x", "vtx_reco_y", "vtx_reco_z"))

    def test_scalar_coordinate_branches(self):
        self.assertEqual(dp.SIG_SCALAR_BRANCHES, ("sim", "sim_pz", "sim_eavail", "sim_q3"))
        self.assertEqual(dp.TRUTH_SCALAR_BRANCHES, ("MC", "MC_pz", "MC_eavail", "MC_q3"))
        self.assertEqual(dp.DATA_SCALAR_BRANCHES,
                         ("measured", "measured_pz", "measured_eavail", "measured_q3"))
        self.assertEqual(dp.BKG_SCALAR_BRANCHES,
                         ("sim_background", "sim_background_pz",
                          "sim_background_eavail", "sim_background_q3"))

    def test_audit_branches_never_features(self):
        self.assertEqual(dp.BKG_AUDIT_BRANCHES, ("bkg_nuPDG", "bkg_current", "bkg_inttype"))
        for k in dp.BKG_AUDIT_BRANCHES:
            self.assertNotIn(k, fdc.REQUIRED_KEYS)

    def test_fps_domain_bounds(self):
        self.assertEqual((dp.FPS_PT_LO, dp.FPS_PT_HI), (0.0, 30.0))
        self.assertEqual((dp.FPS_PZ_LO, dp.FPS_PZ_HI), (0.0, 120.0))
        # bounds are exactly the min/max of the canonical extended-FPS reporting grid
        self.assertEqual(dp.FPS_PT_HI, float(fed.CANONICAL_PT_EDGES[-1]))
        self.assertEqual(dp.FPS_PZ_HI, float(fed.CANONICAL_PPARALLEL_EDGES[-1]))


class ManifestMapping(unittest.TestCase):
    def test_finalize_produces_full_manifest(self):
        a = finalize(*synth_inventories())
        missing = [k for k in fdc.REQUIRED_KEYS if k not in a]
        self.assertEqual(missing, [], f"missing REQUIRED_KEYS {missing}")

    def test_output_shapes_and_dtypes(self):
        ns, nd, nb, P = 6, 5, 4, 12
        a = finalize(*synth_inventories(ns, nd, nb, P), num_part=P)
        self.assertEqual(a["part_reco"].shape, (ns, P, 3))
        self.assertEqual(a["part_gen"].shape, (ns, P, 5))
        self.assertEqual(a["reco_muon"].shape, (ns, dp.NUM_MUON))
        self.assertEqual(a["reco_scalars"].shape, (ns, dp.NUM_SCALAR))
        self.assertEqual(a["reco_view"].shape, (ns, P))
        self.assertEqual(a["measured_pc"].shape, (nd, P, 3))
        self.assertEqual(a["bkg_part_reco"].shape, (nb, P, 3))
        self.assertEqual(a["w_bkg"].shape, (nb,))
        self.assertEqual(a["bkg_indices"].tolist(), list(range(nb)))
        self.assertEqual(a["pass_reco"].dtype, np.dtype(bool))
        self.assertEqual(str(a["petSchemaVersion"]), "g2-fullevent-v1")
        self.assertEqual(int(a["hasFullEventSchema"]), 1)
        self.assertEqual(int(a["fullPhaseSpace"]), 1)
        self.assertEqual(str(a["estimator_fingerprint"]), "pet-fullevent-fps-v1")

    def test_write_reload_all_gates(self):
        a = finalize(*synth_inventories())
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "of_inputs_g2_fullevent_fps.npz")
            fdc.write_fullevent_npz_atomic(out, a, bkg_mode="negweight-refined")
            self.assertTrue(os.path.exists(out))
            self.assertEqual([f for f in os.listdir(td) if f.startswith(".g2dump_")], [])
            z = dict(np.load(out, allow_pickle=True))
        fdc.assert_g2_schema(z)
        fdc.assert_inventory_alignment(z)
        fdc.assert_identity_consistency(z)
        fdc.assert_no_purity_fallback(z, "negweight-refined")
        fed.assert_extended_fps_edges(z["edges_0"], z["edges_1"])
        fed.assert_publication_config(dict(
            estimator_fingerprint=str(z["estimator_fingerprint"]), bkg_mode="negweight-refined",
            petSchemaVersion=str(z["petSchemaVersion"]), hasFullEventSchema=int(z["hasFullEventSchema"]),
            fullPhaseSpace=int(z["fullPhaseSpace"]), has_background=True,
            input="of_inputs_g2_fullevent_fps.npz"))

    def test_no_measured_weights_purity_placeholder(self):
        # The negweight-refined nominal builds measured_weights PER REPLICA; the dumper must NOT
        # emit an all-ones purity placeholder. finalize omits it -> the purity guard passes.
        a = finalize(*synth_inventories())
        self.assertNotIn("measured_weights", a)
        fdc.assert_no_purity_fallback(a, "negweight-refined")  # must not raise


class WeightNormalization(unittest.TestCase):
    def test_weights_are_raw_not_pot_scaled(self):
        sig, data, bkg = synth_inventories()
        a = finalize(sig, data, bkg, pot_scale=0.22)
        np.testing.assert_allclose(a["w_truth"], sig["w_truth"], rtol=0, atol=0)
        np.testing.assert_allclose(a["w_bkg"], bkg["w_bkg"], rtol=0, atol=0)
        self.assertAlmostEqual(float(a["pot_scale"]), 0.22)     # provenance carried for consumers
        self.assertIn("mc_pot", a)
        self.assertIn("data_pot", a)


class DomainExclusion(unittest.TestCase):
    def test_in_fps_domain_bounds(self):
        self.assertTrue(dp.in_fps_domain(0.0, 0.0))            # inclusive lower corner
        self.assertTrue(dp.in_fps_domain(30.0, 120.0))        # inclusive upper corner
        self.assertFalse(dp.in_fps_domain(30.0001, 5.0))      # pT just above
        self.assertFalse(dp.in_fps_domain(5.0, 120.0001))     # p|| just above
        self.assertFalse(dp.in_fps_domain(-0.1, 5.0))         # negative pT
        self.assertFalse(dp.in_fps_domain(float("nan"), 5.0))
        self.assertFalse(dp.in_fps_domain(float("inf"), 5.0))

    def test_corrupt_1D_row_excluded(self):
        # playlist-1D upstream-corrupt AnaTuple muon: scalar pT~2.96e6, p_par~3.12e7 GeV.
        self.assertFalse(dp.in_fps_domain(2.96e6, 3.12e7))

    def test_signal_row_gate(self):
        # matched, in-domain -> kept, pass_reco & pass_truth
        self.assertEqual(dp.select_signal_row(1.0, 2.0, 1, 1.0, 2.0), (True, True, True))
        # reco in-domain but truth out-of-domain -> kept via reco only
        self.assertEqual(dp.select_signal_row(1.0, 2.0, 1, 99.0, 2.0), (True, True, False))
        # both out-of-domain -> dropped entirely
        self.assertEqual(dp.select_signal_row(50.0, 2.0, 1, 99.0, 2.0), (False, False, False))
        # corrupt out-of-domain reco but valid truth -> kept for step 2, EXCLUDED from step 1
        self.assertEqual(dp.select_signal_row(2.96e6, 3.12e7, 1, 1.0, 2.0), (True, False, True))

    def test_data_and_background_domain_gate(self):
        # readers keep a reco row iff its scalar (pT, p||) is in the retained domain
        self.assertTrue(dp.in_fps_domain(3.5, 10.0))
        self.assertFalse(dp.in_fps_domain(40.0, 10.0))        # pT > 30 -> dropped by reader


class NativeMissAndLeakage(unittest.TestCase):
    def test_native_miss_preserved(self):
        # sim_pass==0, reco sentinel, truth in-domain -> kept, !pass_reco, pass_truth
        keep, pr, ptru = dp.select_signal_row(dp.SENTINEL, dp.SENTINEL, 0, 1.0, 2.0)
        self.assertTrue(keep and (not pr) and ptru)

    def test_miss_reco_sentinels(self):
        self.assertEqual(dp.reco_scalar_row(False, [1, 2, 3, 4]), (dp.SENTINEL,) * 4)
        self.assertEqual(dp.reco_muon_row(False, list(range(7))),
                         (dp.SENTINEL,) * 6 + (0.0,))          # minos_ok=0 on a miss
        self.assertEqual(dp.reco_vertex_row(False, [1, 2, 3]), (dp.SENTINEL,) * 3)

    def test_pass_reco_uses_real_values(self):
        self.assertEqual(dp.reco_scalar_row(True, [1.0, 2.0, 3.0, 4.0]), (1.0, 2.0, 3.0, 4.0))
        self.assertEqual(dp.reco_muon_row(True, [1., 2., 3., 4., 5., 6., 1.]),
                         (1., 2., 3., 4., 5., 6., 1.))

    def test_no_truth_leakage_into_event_reco(self):
        # Build a signal block where misses carry the reco SENTINEL; the fullevent event-feature
        # builder must normalize over pass_reco only and never see a truth quantity.
        rng = np.random.default_rng(1)
        ns = 8
        pass_reco = np.array([1, 1, 0, 1, 0, 1, 1, 0], bool)
        reco = rng.random((ns, 4)).astype(np.float32)
        reco[~pass_reco] = dp.SENTINEL                         # miss reco scalars = sentinel
        truth = (rng.random((ns, 4)).astype(np.float32) + 10.0)  # clearly distinct from reco
        er, et, ed, meta = fed.build_event_features(
            reco, truth, rng.random((3, 4)).astype(np.float32),
            pass_reco=pass_reco, pass_truth=np.ones(ns, bool))
        fed.assert_no_truth_leakage(er, reco, truth, fed.DEFAULT_EVT_FEATURES, pass_reco=pass_reco)
        self.assertTrue(np.allclose(er[~pass_reco], 0.0))      # miss rows zeroed post-normalization


class Padding(unittest.TestCase):
    def test_aligned_view_time_follow_energy_sort(self):
        E = [1.0, 5.0, 3.0]; pos = [.1, .2, .3]; z = [.4, .5, .6]
        view = [1, 2, 3]; time = [7., 8., 9.]
        cloud, vw, tm = dp.pad_reco_cloud_tokens(E, pos, z, view, time, 3)
        self.assertEqual(cloud.shape, (3, 3))
        # E-desc order: 5(idx1),3(idx2),1(idx0)
        self.assertAlmostEqual(float(cloud[0, 0]), 5.0)
        self.assertAlmostEqual(float(vw[0]), 2.0)
        self.assertAlmostEqual(float(tm[0]), 8.0)
        self.assertAlmostEqual(float(cloud[1, 0]), 3.0)
        self.assertAlmostEqual(float(vw[1]), 3.0)

    def test_truncate_to_top_p_by_energy(self):
        E = [1., 9., 2., 8.]; z = [1., 2., 3., 4.]
        cloud, vw, tm = dp.pad_reco_cloud_tokens(E, z, z, [1, 2, 3, 4], [1., 2., 3., 4.], 2)
        self.assertEqual(cloud.shape, (2, 3))
        self.assertAlmostEqual(float(cloud[0, 0]), 9.0)
        self.assertAlmostEqual(float(cloud[1, 0]), 8.0)

    def test_empty_cloud_zeros(self):
        cloud, vw, tm = dp.pad_reco_cloud_tokens([], [], [], [], [], 5)
        self.assertFalse(cloud.any() or vw.any() or tm.any())

    def test_truth_cloud_padding(self):
        g = dp.pad_truth_cloud_tokens([2., 5.], [.1, .2], [.1, .2], [.1, .2], [211, -211], 4)
        self.assertEqual(g.shape, (4, 5))
        self.assertAlmostEqual(float(g[0, 0]), 5.0)            # highest-E token first
        self.assertAlmostEqual(float(g[0, 4]), -211.0)         # its raw PDG retained
        self.assertFalse(g[2:].any())                          # padded tokens zero


class IdentityAndAlignment(unittest.TestCase):
    def test_identity_hashes_consistent(self):
        a = finalize(*synth_inventories())
        fdc.assert_identity_consistency(a)                     # must not raise

    def test_tamper_signal_identity(self):
        a = finalize(*synth_inventories())
        a["w_truth"] = a["w_truth"][::-1].copy()               # hash now stale
        with self.assertRaises(ValueError):
            fdc.assert_identity_consistency(a)

    def test_tamper_background_order(self):
        a = finalize(*synth_inventories())
        a["bkg_indices"] = np.roll(a["bkg_indices"], 1)
        with self.assertRaises(ValueError):
            fdc.assert_identity_consistency(a)

    def test_background_row_misalignment(self):
        a = finalize(*synth_inventories())
        a["bkg_view"] = a["bkg_view"][:-1]                     # bkg rows misaligned
        with self.assertRaises(ValueError):
            fdc.assert_inventory_alignment(a)

    def test_background_token_length_mismatch(self):
        a = finalize(*synth_inventories())
        a["bkg_time"] = a["bkg_time"][:, :-1]                  # token len != P
        with self.assertRaises(ValueError):
            fdc.assert_inventory_alignment(a)


class FailClosed(unittest.TestCase):
    def test_batch_launcher_preflights_numpy_interpreter(self):
        launcher = (Path(__file__).parents[1] / "pet" / "sbatch_dump_g2_mefhc.sh").read_text()
        self.assertIn('PYTHON_BIN="$(command -v python3 || true)"', launcher)
        self.assertIn('"$PYTHON_BIN" -c \'import numpy\'', launcher)
        self.assertNotIn("/usr/bin/python3.11", launcher)

    def test_missing_required_key_fails_manifest(self):
        # a reader that failed to emit a required inventory -> write must fail closed (no partial)
        a = finalize(*synth_inventories())
        del a["bkg_muon"]
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "g2.npz")
            with self.assertRaises(ValueError):
                fdc.write_fullevent_npz_atomic(out, a, bkg_mode="negweight-refined")
            self.assertFalse(os.path.exists(out))

    def test_negweight_refined_requires_background(self):
        sig, data, bkg = synth_inventories(nb=0)               # empty background
        a = finalize(sig, data, bkg)
        with self.assertRaises(ValueError):
            fdc.assert_no_purity_fallback(a, "negweight-refined")

    def test_publication_default_never_recoil_markers(self):
        a = finalize(*synth_inventories())
        self.assertEqual(str(a["petSchemaVersion"]), "g2-fullevent-v1")
        self.assertNotEqual(str(a["petSchemaVersion"]), "recoil-only-crosscheck")
        self.assertEqual(int(a["hasFullEventSchema"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
