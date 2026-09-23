"""KNOWN_ISSUES #33: the nominal artifact stores the TARGET R as `step1_class_ratio_target`.

The old key, `step1_class_ratio`, was read as a measurement of what step 1 achieved. It is a copy of
the loader's target. These tests pin that the driver writes the new name and not the old, that the
shared reader prefers the new name, falls back to the old one for artifacts written before
2026-09-23, and refuses an artifact with neither, and that no nominal-artifact reader in `pet/` still
subscripts the old key directly.
"""
import ast
import os
import re
import sys
import tempfile
import unittest

import numpy as np

PET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pet")
if PET not in sys.path:
    sys.path.insert(0, PET)

import nominal_artifact_keys as nak  # noqa: E402


def _npz(tmp, **arrays):
    path = os.path.join(tmp, "a.npz")
    np.savez(path, **{k: np.asarray(v) for k, v in arrays.items()})
    return np.load(path, allow_pickle=True)


class Reader(unittest.TestCase):

    def test_new_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            with _npz(tmp, step1_class_ratio_target=1.124) as z:
                self.assertEqual(nak.step1_class_ratio_target_key(z.files), "step1_class_ratio_target")
                self.assertEqual(nak.step1_class_ratio_target(z), 1.124)

    def test_legacy_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            with _npz(tmp, step1_class_ratio=1.124) as z:
                self.assertEqual(nak.step1_class_ratio_target_key(z.files), "step1_class_ratio")
                self.assertEqual(nak.step1_class_ratio_target(z), 1.124)

    def test_new_key_wins_when_both_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            with _npz(tmp, step1_class_ratio_target=1.0, step1_class_ratio=2.0) as z:
                self.assertEqual(nak.step1_class_ratio_target(z), 1.0)

    def test_neither_key_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with _npz(tmp, weights_push=[1.0]) as z:
                self.assertIsNone(nak.step1_class_ratio_target_key(z.files))
                with self.assertRaises(KeyError):
                    nak.step1_class_ratio_target(z)


class AnnealedReproductionEvaluatorReadsBothNames(unittest.TestCase):
    """`evaluate_annealed_nominal_reproduction.evaluate` on artifacts carrying each key form.

    test_annealed_nominal_reproduction.py (receipt-bound, so left as it is) writes the legacy key
    only; this covers the new key, precedence, and refusal.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_eval_anr", os.path.join(PET, "evaluate_annealed_nominal_reproduction.py"))
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def _artifact(self, tmp, ratios, deviation=-0.011724):
        import json
        path = os.path.join(tmp, "artifact.npz")
        fits = [{"iteration": i, "learning_rate": 1e-4 if i == 0 else 1e-5} for i in (0, 0, 1, 1, 2, 2)]
        lr = {"verified_from_optimizer": True, "base_lr": 1e-4, "annealed_lr": 1e-5,
              "n_fits_base_lr": 2, "n_fits_annealed": 4, "fits": fits}
        seed = {"lr_policy": {"schedule": "fit-time-anneal-after-iteration-0", "base_lr": 1e-4,
                              "annealed_lr": 1e-5, "applies_from_iteration": 1}}
        np.savez_compressed(path, fold_forward_sum_w_push_reco=np.asarray(1.0 + deviation),
                            fold_forward_sum_w_reco=np.asarray(1.0),
                            seed_policy=np.asarray(seed, dtype=object),
                            lr_policy_realized=np.asarray(lr, dtype=object),
                            **{k: np.asarray(v) for k, v in ratios})
        with open(path + ".done", "w") as fh:
            json.dump({"output": path}, fh)
        return path

    def test_new_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.mod.evaluate(self._artifact(tmp, [("step1_class_ratio_target", 1.0)]))
            self.assertEqual(out["fold_forward"]["verdict"], "REPRODUCED")

    def test_legacy_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.mod.evaluate(self._artifact(tmp, [("step1_class_ratio", 1.0)]))
            self.assertEqual(out["fold_forward"]["verdict"], "REPRODUCED")

    def test_new_key_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.mod.evaluate(self._artifact(
                tmp, [("step1_class_ratio_target", 1.0), ("step1_class_ratio", 2.0)]))
            self.assertEqual(out["fold_forward"]["step1_class_ratio_R"], 1.0)

    def test_neither_key_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "lacks required fields"):
                self.mod.evaluate(self._artifact(tmp, []))


class DriverWritesTheNewName(unittest.TestCase):
    """The keyword names of the dict(...) the nominal driver hands to atomic_savez_compressed."""

    def _saved_keys(self):
        with open(os.path.join(PET, "train_fullevent_nominal.py")) as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "atomic_savez_compressed"
                    and len(node.args) >= 2 and isinstance(node.args[1], ast.Call)
                    and getattr(node.args[1].func, "id", None) == "dict"):
                return {kw.arg for kw in node.args[1].keywords}
        self.fail("could not find the driver's atomic_savez_compressed(args.out, dict(...)) call")

    def test_writes_target_name_and_not_the_legacy_name(self):
        keys = self._saved_keys()
        self.assertIn(nak.STEP1_CLASS_RATIO_TARGET_KEY, keys)
        self.assertNotIn(nak.LEGACY_STEP1_CLASS_RATIO_KEY, keys)


class NoDirectLegacyReads(unittest.TestCase):
    """A reader that subscripts the old key would fail on every new artifact."""

    PATTERN = re.compile(r"""\b(?:z|data|npz)\[\s*["']step1_class_ratio["']\s*\]""")

    def test_no_pet_module_subscripts_the_legacy_key_on_an_npz(self):
        hits = []
        for name in sorted(os.listdir(PET)):
            if name.endswith(".py") and name != "nominal_artifact_keys.py":
                with open(os.path.join(PET, name)) as fh:
                    for i, line in enumerate(fh, 1):
                        if self.PATTERN.search(line):
                            hits.append(f"{name}:{i}: {line.strip()}")
        self.assertEqual(hits, [], "read it through nominal_artifact_keys.step1_class_ratio_target")

    def test_the_pattern_has_power(self):
        self.assertTrue(self.PATTERN.search('r = float(z["step1_class_ratio"])'))
        self.assertFalse(self.PATTERN.search('R = float(t["step1_class_ratio"])'),
                         "the loader's target dict legitimately keeps its own key")


if __name__ == "__main__":
    unittest.main(verbosity=2)
