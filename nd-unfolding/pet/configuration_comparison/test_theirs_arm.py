"""Tests for the complete arm as an OmniFold estimator.

The load-bearing one is the mask. Inheriting the port's default mask column
would mask on `pz`, which a real object can legitimately have at zero.
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np
import tensorflow as tf

import pet2_keras_port as port
import theirs_omnifold_arm as arm

SMALL = dict(base_dim=16, num_transformers=2, num_transformers_head=2,
             num_tokens=2, num_heads=4, mlp_ratio=2)


def _model():
    m = arm.TheirsCompleteArm(num_part=12, K=5)
    m.backbone = port.PET2Port(**m.settings, **SMALL)
    return m


def _batch(rows=3, tokens=12):
    rng = np.random.RandomState(0)
    tok = rng.randn(rows, tokens, 5).astype("float32")
    tok[:, :, 4] = rng.randint(0, 8, (rows, tokens))     # PID column
    tok[:, 8:, :] = 0.0                                   # padded tail
    add = rng.randn(rows, tokens, 5).astype("float32"); add[:, 8:, :] = 0.0
    glob = rng.randn(rows, 16).astype("float32")
    return [tf.constant(tok), tf.constant(add), tf.constant(glob)]


class Masking(unittest.TestCase):
    def test_the_mask_is_on_log_energy_not_the_port_default(self):
        self.assertEqual(arm.LOG_E_COLUMN, 3)
        self.assertNotEqual(arm.LOG_E_COLUMN, port.HIS_MASK_COLUMN)

    def test_a_real_token_with_zero_pz_is_not_masked(self):
        """The failure inheriting column 2 would cause, made explicit."""
        m = _model()
        x = _batch()
        tok = np.array(x[0]); tok[:, 0, 2] = 0.0          # pz = 0, real object
        mask = m.pad_mask(tf.constant(tok)).numpy()
        self.assertEqual(mask[0, 0, 0], 1.0)

    def test_padded_rows_are_masked(self):
        m = _model()
        mask = m.pad_mask(_batch()[0]).numpy()
        self.assertTrue(np.all(mask[:, 8:, 0] == 0.0))

    def test_padded_tokens_cannot_change_the_output(self):
        m = _model()
        x = _batch()
        before = m(x, training=False).numpy()
        tok = np.array(x[0]); tok[:, 8:, :3] = np.random.randn(3, 4, 3)
        after = m([tf.constant(tok), x[1], x[2]], training=False).numpy()
        np.testing.assert_array_equal(before, after)


class Shapes(unittest.TestCase):
    def test_the_output_is_one_logit_per_event(self):
        m = _model()
        self.assertEqual(m(_batch(), training=False).shape, (3, 1))

    def test_pid_is_read_from_the_token_block(self):
        self.assertEqual(arm.PID_COLUMN, 4)

    def test_a_training_step_moves_the_weights(self):
        m = _model()
        x = _batch()
        y = tf.constant(np.stack([np.array([0, 1, 0]), np.ones(3)], axis=1),
                        dtype=tf.float32)
        m.compile(optimizer=tf.keras.optimizers.Adam(1e-3))
        before = [v.numpy().copy() for v in m.trainable_variables]
        m.train_step((x, y))
        moved = max(float(np.max(np.abs(a - v.numpy())))
                    for a, v in zip(before, m.trainable_variables))
        self.assertGreater(moved, 0.0)


if __name__ == "__main__":
    unittest.main()


class PackedForm(unittest.TestCase):
    """His own storage is one 10-wide array; the engine carries two tensors."""

    def test_packed_and_unpacked_agree_exactly(self):
        m = _model()
        tok, add, glob = _batch()
        packed = tf.concat([tok, add], axis=2)
        self.assertEqual(packed.shape[-1], arm.PACKED_WIDTH)
        a = m([tok, add, glob], training=False).numpy()
        b = m([packed, glob], training=False).numpy()
        np.testing.assert_array_equal(a, b)

    def test_the_add_info_slice_is_the_second_five(self):
        self.assertEqual(arm.ADD_INFO_SLICE, slice(5, 10))

    def test_the_packed_form_still_masks_on_log_energy(self):
        m = _model()
        tok, add, glob = _batch()
        packed = np.concatenate([np.array(tok), np.array(add)], axis=2)
        packed[:, 8:, :] = 0.0
        mask = m.pad_mask(tf.constant(packed)).numpy()
        self.assertTrue(np.all(mask[:, 8:, 0] == 0.0))


class ThePretrainedArmMustBePretrained(unittest.TestCase):
    """The goal names his PRETRAINED PET2-small and rules out the substitute.

    `frozen_design.THEIRS_COMPLETE["initialization"]` records
    `best_model_pretrain_s.pt via load_pretrained_omnilearned`. The arm built
    the port and never loaded it, so the campaign would have trained his
    ARCHITECTURE from random initialisation and reported it as his
    configuration. Nothing contradicted the freeze; the freeze described an
    intent.
    """

    def test_the_driver_requires_the_checkpoint_for_the_theirs_arm(self):
        from pathlib import Path
        import run_arm_evaluation as rae
        source = Path(rae.__file__).read_text()
        self.assertIn('"--theirs-state-npz"', source)
        self.assertIn("scratch cannot substitute for the pretrained arm", source)

    def test_the_driver_refuses_to_record_a_scratch_run_as_pretrained(self):
        from pathlib import Path
        import run_arm_evaluation as rae
        source = Path(rae.__file__).read_text()
        self.assertIn("refusing to", source)
        self.assertIn("reports no pretrained load", source)

    def test_the_arm_accepts_a_state_and_records_it(self):
        import inspect
        import theirs_omnifold_arm as toa
        params = inspect.signature(toa.TheirsCompleteArm.__init__).parameters
        self.assertIn("state_npz", params)
        self.assertIn("manifest", params)

    def test_a_manifest_for_a_different_model_is_refused_by_setting_name(self):
        import json
        import tempfile
        from pathlib import Path
        import theirs_omnifold_arm as toa
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "m.json"
            manifest.write_text(json.dumps({
                "settings": {"input_dim": 4, "pid": True, "pid_dim": 8,
                             "add_info": True, "add_dim": 5, "conditional": True,
                             "cond_dim": 16, "num_coord": 2, "K": 10,
                             "num_classes": 1, "use_int": False,
                             "local_int": False},
                "preset": {"num_transformers": 99, "num_transformers_head": 2,
                           "num_tokens": 4, "num_heads": 8, "base_dim": 128,
                           "mlp_ratio": 2}}))
            with self.assertRaisesRegex(ValueError, "different preset"):
                toa.TheirsCompleteArm(num_part=5, manifest=manifest)

    def test_both_launchers_pass_the_checkpoint_and_check_it_exists(self):
        from pathlib import Path
        here = Path(__file__).resolve().parent
        for name in ("sbatch_campaign.sh", "sbatch_campaign_smoke.sh"):
            text = (here / name).read_text()
            self.assertIn("THEIRS_STATE=${THEIRS_STATE:-", text, msg=name)
            self.assertIn('[[ -f "$THEIRS_STATE" ]]', text, msg=name)
            self.assertIn('--theirs-state-npz "$THEIRS_STATE"', text, msg=name)

    def test_the_freeze_and_the_code_now_agree(self):
        import frozen_design as fd
        self.assertIn("best_model_pretrain_s.pt",
                      fd.THEIRS_COMPLETE["initialization"])

    def test_the_paper_interaction_flags_are_stated_not_defaulted(self):
        """They are the V1-paper flags and the freeze names them."""
        import frozen_design as fd
        import theirs_omnifold_arm as toa
        arm = toa.TheirsCompleteArm(num_part=5)
        for flag in ("use_int", "local_int"):
            self.assertIn(flag, arm.settings)
            self.assertEqual(arm.settings[flag], fd.THEIRS_COMPLETE[flag])

    def test_a_missing_setting_is_reported_as_a_difference(self):
        """"False" and "not mentioned" are different, and the check says so."""
        import json
        import tempfile
        from pathlib import Path
        import theirs_omnifold_arm as toa
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "m.json"
            manifest.write_text(json.dumps({"settings": {}, "preset": {}}))
            with self.assertRaisesRegex(ValueError, "different settings"):
                toa.TheirsCompleteArm(num_part=5, manifest=manifest)
