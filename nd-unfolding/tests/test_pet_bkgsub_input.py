"""Phase-1 tests for the corrected PET background-subtracted point-cloud input.

Exercises the import-safe (no ROOT) gate helpers in
pet/build_bkgsub_pointcloud_input.py on synthetic fixtures:
  * corrected measured-weight construction / validation,
  * data row-alignment (pass and failure detection, incl. float32 precision),
  * MC byte-identity (CRC) alignment,
  * per-bin purity structure report,
  * strict corrected-npz assembly (weights swapped, scalars added, old file
    untouched, common ordering preserved).
"""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND / "pet"))

import build_bkgsub_pointcloud_input as bbi  # noqa: E402


def _fake_ref5d(path, n=200, seed=0):
    """A tiny of_inputs_5d-like npz: measured (n,5) f32, measured_weights (n,)
    in [0,1] constant per coarse reco bin, edges_0..4, MC arrays."""
    rng = np.random.default_rng(seed)
    edges = [np.array([0.0, 0.5, 1.0, 4.5]),          # pt
             np.array([1.5, 3.0, 60.0]),               # pz
             np.array([0.0, 1.0, 100.0]),              # eavail
             np.array([0.0, 1.0, 100.0]),              # q3
             np.array([0.0, 2.0, 100.0])]              # W
    measured = np.column_stack([
        rng.uniform(0.05, 4.4, n), rng.uniform(1.6, 59.0, n),
        rng.uniform(0.05, 90.0, n), rng.uniform(0.05, 90.0, n),
        rng.uniform(0.05, 90.0, n)]).astype(np.float32)
    # per-bin-constant purity weight in [0,1]
    idx = np.zeros(n, dtype=np.int64)
    for j in range(5):
        b = np.digitize(measured[:, j].astype(np.float64), edges[j])
        idx = idx * (len(edges[j]) + 1) + b
    uniq, inv = np.unique(idx, return_inverse=True)
    bin_w = rng.uniform(0.0, 1.0, len(uniq))
    w = bin_w[inv].astype(np.float64)
    mc = rng.uniform(size=2 * n).astype(np.float64)
    np.savez(path, measured=measured, measured_weights=w,
             edges_0=edges[0], edges_1=edges[1], edges_2=edges[2],
             edges_3=edges[3], edges_4=edges[4],
             w_truth=mc[:n], w_reco=mc[n:],
             pass_reco=(mc[:n] > 0.5), pass_truth=(mc[n:] > 0.3),
             axes=np.array(["eavail", "q3", "W"], dtype=object))
    return measured, w, edges


def _fake_fullcloud(path, ref_measured, ref_npz, n=200, seed=1):
    """A tiny of_inputs_pc_fullcloud-like npz: clouds + UNIT measured_weights,
    with MC arrays byte-copied from ref so the CRC gate can pass."""
    rng = np.random.default_rng(seed)
    ref = np.load(ref_npz, allow_pickle=True)
    P = 4
    np.savez(path, num_part=P,
             part_gen=rng.uniform(size=(n, P, 5)).astype(np.float32),
             part_reco=rng.uniform(size=(n, P, 3)).astype(np.float32),
             measured_pc=rng.uniform(size=(n, P, 3)).astype(np.float32),
             measured_weights=np.ones(n),
             w_truth=ref["w_truth"], w_reco=ref["w_reco"],
             pass_reco=ref["pass_reco"], pass_truth=ref["pass_truth"],
             truth_scalars=rng.uniform(size=(n, 4)).astype(np.float32),
             reco_scalars=rng.uniform(size=(n, 4)).astype(np.float32),
             edges_0=ref["edges_0"], edges_1=ref["edges_1"],
             edges_2=ref["edges_2"], edges_3=ref["edges_3"],
             gen_feats=np.array(["a"], dtype=object),
             reco_feats=np.array(["b"], dtype=object),
             data_pot=np.asarray(1.0e21))


class DataAlignmentTests(unittest.TestCase):
    def test_identical_passes(self):
        m = np.random.default_rng(3).uniform(size=(50, 5)).astype(np.float32)
        g = bbi.check_data_alignment(m.astype(np.float64), m)
        self.assertTrue(g["exact"])
        self.assertEqual(g["n_mismatch_rows"], 0)

    def test_row_perturbation_detected(self):
        m = np.random.default_rng(4).uniform(size=(50, 5)).astype(np.float32)
        a = m.astype(np.float64).copy()
        a[7, 2] += 0.5  # perturb eavail on row 7
        g = bbi.check_data_alignment(a, m)
        self.assertFalse(g["exact"])
        self.assertGreaterEqual(g["n_mismatch_rows"], 1)
        self.assertIn(7, g["first_mismatch_rows"])
        self.assertEqual(g["per_col"]["eavail"]["n_mismatch"], 1)
        self.assertEqual(g["per_col"]["pt"]["n_mismatch"], 0)

    def test_shape_mismatch_detected(self):
        a = np.zeros((49, 5)); b = np.zeros((50, 5), np.float32)
        g = bbi.check_data_alignment(a, b)
        self.assertFalse(g["exact"])
        self.assertIn("shape", g.get("reason", ""))

    def test_float32_precision_boundary(self):
        # doubles that round to the SAME float32 must compare equal (stored prec).
        base = np.full((10, 5), 1.2345678, np.float32).astype(np.float64)
        near = base + 1e-9  # below float32 resolution at this magnitude
        g = bbi.check_data_alignment(near, base.astype(np.float32))
        self.assertTrue(g["exact"], "sub-float32 diffs must not count as mismatch")
        far = base.copy(); far[0, 0] += 1e-3  # above float32 resolution
        g2 = bbi.check_data_alignment(far, base.astype(np.float32))
        self.assertFalse(g2["exact"])


class WeightGateTests(unittest.TestCase):
    def test_valid_weights(self):
        w = np.clip(np.random.default_rng(5).uniform(-0.1, 1.1, 100), 0, 1)
        g = bbi.validate_bkgsub_weights(w, w)
        self.assertTrue(g["finite"] and g["in_unit_interval"]
                        and g["exact_equal_to_ref"] and g["sum_exact"])

    def test_out_of_unit_interval(self):
        w = np.array([0.0, 0.5, 1.0, 1.2])
        g = bbi.validate_bkgsub_weights(w, w)
        self.assertFalse(g["in_unit_interval"])

    def test_not_equal_to_ref(self):
        w = np.array([0.1, 0.2, 0.3]); r = np.array([0.1, 0.2, 0.4])
        g = bbi.validate_bkgsub_weights(w, r)
        self.assertFalse(g["exact_equal_to_ref"])


class McAlignmentTests(unittest.TestCase):
    def test_crc_identity_and_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            ref_measured, _, _ = _fake_ref5d(p / "ref.npz")
            _fake_fullcloud(p / "pc.npz", ref_measured, p / "ref.npz")
            g = bbi.check_mc_alignment(p / "pc.npz", p / "ref.npz")
            self.assertTrue(g["all_identical"])
            # now a mismatched MC array
            ref = np.load(p / "ref.npz", allow_pickle=True)
            bad = dict(np.load(p / "pc.npz", allow_pickle=True))
            bad["w_truth"] = bad["w_truth"] + 1.0
            np.savez(p / "pc_bad.npz", **bad)
            g2 = bbi.check_mc_alignment(p / "pc_bad.npz", p / "ref.npz")
            self.assertFalse(g2["all_identical"])
            self.assertFalse(g2["members"]["w_truth"]["identical"])
            self.assertTrue(g2["members"]["pass_reco"]["identical"])


class PurityReportTests(unittest.TestCase):
    def test_constant_per_bin_has_no_spread(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            measured, w, edges = _fake_ref5d(p / "ref.npz", n=500)
            rep = bbi.per_bin_purity_report(measured, w, edges)
            self.assertEqual(rep["n_bins_spread_gt_1e-9"], 0)
            self.assertGreater(rep["n_populated_bins"], 0)


class BuildCorrectedNpzTests(unittest.TestCase):
    def test_build_swaps_weights_and_adds_scalars(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            ref_measured, ref_w, _ = _fake_ref5d(p / "ref.npz", n=120)
            _fake_fullcloud(p / "pc.npz", ref_measured, p / "ref.npz", n=120)
            pc_before = dict(np.load(p / "pc.npz", allow_pickle=True))
            scalars = ref_measured.astype(np.float64)  # aligned by construction
            out = p / "out.npz"
            bbi.build_corrected_npz(p / "pc.npz", p / "ref.npz", scalars, str(out),
                                    verbose=False)
            got = np.load(out, allow_pickle=True)
            # weights swapped to the bkgsub target
            self.assertTrue(np.array_equal(np.asarray(got["measured_weights"]), ref_w))
            self.assertFalse(np.array_equal(np.asarray(got["measured_weights"]),
                                            np.ones(120)))
            # scalars added, clouds + MC + ordering preserved
            self.assertEqual(got["measured_scalars"].shape, (120, 5))
            self.assertTrue(np.array_equal(got["measured_pc"], pc_before["measured_pc"]))
            self.assertTrue(np.array_equal(got["w_truth"], pc_before["w_truth"]))
            self.assertEqual(list(got["measured_scalars_cols"]), bbi.SCALAR_COLS)
            self.assertIn("edges_4", got.files)
            # the unsubtracted source file is NOT modified
            pc_after = dict(np.load(p / "pc.npz", allow_pickle=True))
            self.assertTrue(np.array_equal(pc_after["measured_weights"], np.ones(120)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
