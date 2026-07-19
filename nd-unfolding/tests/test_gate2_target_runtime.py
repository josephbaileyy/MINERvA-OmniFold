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


class TargetOnlyDataLoader(unittest.TestCase):
    def test_exact_numpy_source_loads_without_tensorflow_package_init(self):
        saved_parent = sys.modules.pop("omnifold", None)
        saved_child = sys.modules.pop("omnifold.dataloader", None)
        tensorflow_before = {k for k in sys.modules if k == "tensorflow" or k.startswith("tensorflow.")}
        try:
            module = g2.install_target_only_dataloader()
            expected = g2.REPO / "omnifold_nn/omnifold/dataloader.py"
            self.assertEqual(Path(module.__file__).resolve(), expected.resolve())
            self.assertTrue(hasattr(module, "DataLoader"))
            tensorflow_after = {k for k in sys.modules if k == "tensorflow" or k.startswith("tensorflow.")}
            self.assertEqual(tensorflow_after, tensorflow_before)
        finally:
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
