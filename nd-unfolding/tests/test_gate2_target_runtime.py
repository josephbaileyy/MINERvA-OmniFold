"""Login-safe regression tests for Gate-2 receipt-last staging semantics."""

import importlib.util
from pathlib import Path
import tempfile
import sys
import unittest

import numpy as np


MODULE_PATH = Path(__file__).parents[1] / "pet" / "gate2_target_runtime.py"
SPEC = importlib.util.spec_from_file_location("gate2_target_runtime", MODULE_PATH)
g2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g2)
FED_PATH = Path(__file__).parents[1] / "pet" / "fullevent_fps_dataloader.py"
FED_SPEC = importlib.util.spec_from_file_location("gate2_test_fed", FED_PATH)
fed = importlib.util.module_from_spec(FED_SPEC)
FED_SPEC.loader.exec_module(fed)


class StagingContract(unittest.TestCase):
    def test_empty_mktemp_paths_are_valid_and_writable(self):
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "receipt.json"
            npy_path = Path(directory) / "weights.npy"
            json_path.touch()
            npy_path.touch()
            g2.require_available_staging(json_path)
            g2.require_available_staging(npy_path)
            g2.write_json_fsync(json_path, {"status": "PASS"})
            g2.write_npy_fsync(npy_path, np.array([1.0, 2.0], np.float32))
            self.assertGreater(json_path.stat().st_size, 0)
            self.assertGreater(npy_path.stat().st_size, 0)

    def test_nonempty_staging_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "occupied"
            path.write_text("occupied")
            with self.assertRaises(RuntimeError):
                g2.require_available_staging(path)


class IndependentHistogramUnits(unittest.TestCase):
    def test_out_of_domain_gev_row_stays_out_of_domain(self):
        measured = np.array([[31.0, 121.0, 0.0, 0.0]])
        background = np.array([[0.5, 2.0, 0.0, 0.0]])
        measured_xy, background_xy = g2.independent_gev_coordinates(
            measured, background
        )
        self.assertEqual(
            g2._hist2(measured_xy, np.array([0.0, 4.5]), np.array([1.5, 60.0])).sum(),
            0,
        )
        np.testing.assert_array_equal(background_xy, background[:, :2])

    def test_multi_bin_fixture_does_not_collapse_into_one_bin(self):
        measured = np.array(
            [[0.1, 2.0, 9.0], [0.8, 4.0, 8.0], [1.8, 8.0, 7.0]]
        )
        background = np.array([[0.2, 2.5, 6.0]])
        measured_xy, _ = g2.independent_gev_coordinates(measured, background)
        hist = g2._hist2(
            measured_xy,
            np.array([0.0, 0.5, 1.0, 2.0]),
            np.array([1.5, 3.0, 6.0, 10.0]),
        )
        self.assertEqual(int(np.count_nonzero(hist)), 3)
        self.assertEqual(int(hist.sum()), 3)

    def test_independent_coordinates_equal_loader_refiner_gev_columns(self):
        measured = np.array([[0.2, 2.0, 1000.0], [1.4, 7.0, 2000.0]])
        background = np.array([[0.4, 3.5, 3000.0]])
        measured_xy, background_xy = g2.independent_gev_coordinates(
            measured, background
        )
        np.testing.assert_array_equal(measured_xy, measured[:, :2])
        np.testing.assert_array_equal(background_xy, background[:, :2])
        loader_features = fed.build_signed_measured_inventory(
            measured[:, :2],
            background[:, :2],
            np.ones(background.shape[0]),
            0.25,
        )[0]
        np.testing.assert_array_equal(
            measured_xy, loader_features[: measured.shape[0]]
        )
        np.testing.assert_array_equal(
            background_xy, loader_features[measured.shape[0] :]
        )


class TargetOnlyDataLoader(unittest.TestCase):
    def test_exact_numpy_source_loads_without_tensorflow_package_init(self):
        saved_parent = sys.modules.pop("omnifold", None)
        saved_child = sys.modules.pop("omnifold.dataloader", None)
        saved_repo = g2.REPO
        g2.REPO = Path(__file__).parents[2]
        tensorflow_before = {k for k in sys.modules if k == "tensorflow" or k.startswith("tensorflow.")}
        try:
            module = g2.install_target_only_dataloader()
            expected = g2.REPO / "omnifold_nn/omnifold/dataloader.py"
            self.assertEqual(Path(module.__file__).resolve(), expected.resolve())
            self.assertTrue(hasattr(module, "DataLoader"))
            tensorflow_after = {k for k in sys.modules if k == "tensorflow" or k.startswith("tensorflow.")}
            self.assertEqual(tensorflow_after, tensorflow_before)
        finally:
            g2.REPO = saved_repo
            sys.modules.pop("omnifold.dataloader", None)
            sys.modules.pop("omnifold", None)
            if saved_parent is not None:
                sys.modules["omnifold"] = saved_parent
            if saved_child is not None:
                sys.modules["omnifold.dataloader"] = saved_child

    def test_dangling_symlink_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dangling"
            path.symlink_to(Path(directory) / "missing")
            with self.assertRaises(RuntimeError):
                g2.require_available_staging(path)


if __name__ == "__main__":
    unittest.main()
