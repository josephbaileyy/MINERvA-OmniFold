"""Tests for loading the pretrained state into the Keras port.

The load-bearing ones are the refusals. A silently partial initialization is the
worst failure available here: the arm trains, converges to something, and gets
reported as "the pretrained arm" while part of it started from Keras' initializers
instead of Gregor's checkpoint. Nothing downstream could tell.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import pet2_keras_port as port
import pretrained_init as pi

SETTINGS = dict(input_dim=4, conditional=True, cond_dim=16, pid=True, pid_dim=8,
                add_info=True, add_dim=5, num_classes=1, num_coord=2, K=5)
PRESET = dict(base_dim=16, num_transformers=2, num_transformers_head=2,
              num_tokens=2, num_heads=4, mlp_ratio=2)


class Coverage(unittest.TestCase):
    """Every variable covered, every array consumed, every shape matched."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.model = port.PET2Port(**SETTINGS, dtype="float32", **PRESET)
        rng = np.random.RandomState(4)
        self.arrays = {
            name: rng.randn(*[int(d) for d in v.shape]).astype("float32")
            for name, v in port.parameter_inventory(self.model)
        }
        self.manifest = self.dir / "manifest.json"
        self.manifest.write_text(json.dumps(
            {"settings": dict(SETTINGS, use_int=False, local_int=False),
             "preset": PRESET, "checkpoint_sha256": "0" * 64}))

    def _npz(self, arrays, name="state.npz"):
        path = self.dir / name
        np.savez(path, **arrays)
        return path

    def test_a_complete_state_loads_exactly(self):
        record = pi.load_state_into(self.model, self._npz(self.arrays))
        self.assertEqual(record["tensors_loaded"], len(self.arrays))
        self.assertTrue(record["exact"])
        self.assertEqual(record["worst_absolute_difference_after_assign"], 0.0)
        # And the values are really the ones supplied, not merely self-consistent.
        inventory = dict(port.parameter_inventory(self.model))
        for name, value in self.arrays.items():
            np.testing.assert_array_equal(inventory[name].numpy(), value)

    def test_a_missing_array_is_refused(self):
        partial = dict(self.arrays)
        dropped = sorted(partial)[3]
        del partial[dropped]
        with self.assertRaises(ValueError) as caught:
            pi.load_state_into(self.model, self._npz(partial, "partial.npz"))
        self.assertIn("no array", str(caught.exception))

    def test_an_unused_array_is_refused(self):
        extra = dict(self.arrays, not_a_variable=np.zeros((2, 2), dtype="float32"))
        with self.assertRaises(ValueError) as caught:
            pi.load_state_into(self.model, self._npz(extra, "extra.npz"))
        self.assertIn("match no variable", str(caught.exception))

    def test_a_shape_mismatch_is_refused(self):
        wrong = dict(self.arrays)
        name = sorted(wrong)[0]
        wrong[name] = np.zeros(tuple(d + 1 for d in wrong[name].shape), dtype="float32")
        with self.assertRaises(ValueError) as caught:
            pi.load_state_into(self.model, self._npz(wrong, "wrong.npz"))
        self.assertIn("shape mismatch", str(caught.exception))

    def test_the_state_hash_travels_with_the_load(self):
        record = pi.load_state_into(self.model, self._npz(self.arrays))
        self.assertEqual(len(record["state_npz_sha256"]), 64)

    def test_the_model_is_built_from_the_manifest_not_a_constant(self):
        """A drifted constant would silently initialize a different network."""
        model, record = pi.build_pretrained_port(
            self._npz(self.arrays), self.manifest, dtype="float32")
        self.assertEqual(record["tensors_loaded"], len(self.arrays))
        self.assertTrue(record["exact"])
        self.assertEqual(record["checkpoint_sha256"], "0" * 64)

    def test_a_manifest_for_a_different_network_fails_loudly(self):
        other = json.loads(self.manifest.read_text())
        other["preset"] = dict(PRESET, base_dim=32)
        path = self.dir / "other.json"
        path.write_text(json.dumps(other))
        with self.assertRaises(ValueError):
            pi.build_pretrained_port(self._npz(self.arrays), path, dtype="float32")


if __name__ == "__main__":
    unittest.main()
