"""Login-safe regression tests for the isolated annealed powered-closure route."""
from pathlib import Path
import importlib.util
import inspect
import subprocess
import sys
import types
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[2]
PET = REPO / "nd-unfolding" / "pet"
WRAPPER = PET / "closure_powered_annealed_lr.py"
LAUNCHER = PET / "sbatch_annealed_shape_validation.sh"


def _load_wrapper():
    spec = importlib.util.spec_from_file_location("annealed_shape_wrapper_test", WRAPPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AnnealedShapeValidationTests(unittest.TestCase):
    def test_subclass_preserves_engine_constructor_signature(self):
        """Regression for job 56547490: (*a, **kw) must not hide early_stop."""
        class BaseMultiFold:
            def __init__(self, name, *, early_stop=10):
                self.name = name
                self.start = 0

            def CompileModel(self, model, num_steps, fixed=False):
                return model

            def RunModel(self, *args, **kwargs):
                return None

        fake_tf = types.ModuleType("tensorflow")
        fake_omnifold = types.ModuleType("omnifold")
        fake_omnifold.MultiFold = BaseMultiFold
        fake_numpy = types.ModuleType("numpy")
        with mock.patch.dict(sys.modules, {"numpy": fake_numpy, "tensorflow": fake_tf,
                                           "omnifold": fake_omnifold}):
            wrapper = _load_wrapper()
            annealed, _ = wrapper.install_annealed_multifold()

        base = inspect.signature(BaseMultiFold.__init__).parameters["early_stop"]
        inherited = inspect.signature(annealed.__init__).parameters["early_stop"]
        self.assertEqual(inherited.default, base.default)

    def test_launcher_preflights_the_inherited_signature(self):
        src = LAUNCHER.read_text()
        self.assertIn("inspect.signature(A.__init__).parameters", src)
        self.assertIn("['early_stop'].default", src)
        self.assertIn("import/signature preflight OK", src)

    def test_launcher_syntax_and_isolation(self):
        result = subprocess.run(["bash", "-n", str(LAUNCHER)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        src = LAUNCHER.read_text()
        self.assertIn("POWERED_CLOSURE_ANNEALED.slurm-${JOB}", src)
        self.assertIn("engine_edited\": False", src)
        self.assertNotIn("scancel", src)


if __name__ == "__main__":
    unittest.main()
