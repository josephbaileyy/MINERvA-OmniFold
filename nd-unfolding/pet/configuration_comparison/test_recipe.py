"""Tests for the derived training recipe and the checkpoint transfer map.

The load-bearing ones are the tests that a quantity is DERIVED rather than copied,
and that the transfer map's verdict is structural rather than proportional.
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import checkpoint_transfer as ct
import tensorflow as tf
import training_recipe as tr

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None


class Budget(unittest.TestCase):
    """The fairness axis is example presentations, and it is shared."""

    def test_a_fit_presents_both_classes_not_one(self):
        """The regression the realized-policy check found: NTRAIN is 2N, not N."""
        self.assertEqual(tr.rows_per_fit("step2_gen", n_mc=2_000_000), 4_000_000)
        self.assertEqual(tr.rows_per_fit("step1_reco", n_mc=2_000_000,
                                         n_data=3_000_000), 5_000_000)
        self.assertEqual(
            tr.examples_per_fit("step2_gen", epochs=8, n_mc=2_000_000, train_frac=0.8),
            25_600_000)

    def test_step_one_refuses_to_guess_the_measured_leg_size(self):
        """--max-events subsamples the MC only; n_data is a production property."""
        with self.assertRaises(ValueError):
            tr.rows_per_fit("step1_reco", n_mc=2_000_000)

    def test_unknown_step_is_refused(self):
        with self.assertRaises(ValueError):
            tr.rows_per_fit("step3", n_mc=10)

    def test_both_arms_get_the_same_examples_and_different_step_counts(self):
        theirs = tr.derive_schedule(2048)
        ours = tr.derive_schedule(512)
        self.assertEqual(theirs["examples_per_fit"], ours["examples_per_fit"])
        self.assertEqual(ours["max_steps"], 4 * theirs["max_steps"])

    def test_max_steps_is_not_his_literal(self):
        """The whole point: 250,000 is his dataset's step count, not our budget."""
        self.assertNotEqual(tr.derive_schedule(2048)["max_steps"],
                            tr.HIS_REFERENCE_RUN["max_steps"])
        self.assertEqual(tr.derive_schedule(2048)["max_steps"], 12500)

    def test_warmup_preserves_the_fraction_not_the_count(self):
        schedule = tr.derive_schedule(2048)
        self.assertNotEqual(schedule["warmup_steps"], 1000)
        self.assertAlmostEqual(schedule["warmup_steps"] / schedule["max_steps"],
                               tr.HIS_WARMUP_FRACTION, places=3)

    def test_grad_accumulation_changes_steps_not_examples(self):
        plain = tr.derive_schedule(1024, grad_accum_steps=1)
        accumulated = tr.derive_schedule(512, grad_accum_steps=2)
        self.assertEqual(plain["examples_per_update"], accumulated["examples_per_update"])
        self.assertEqual(plain["max_steps"], accumulated["max_steps"])

    def test_a_budget_too_small_for_its_warmup_is_refused(self):
        with self.assertRaises(ValueError):
            tr.derive_schedule(2048, examples=2048)

    def test_nonsense_inputs_are_refused(self):
        for kwargs in ({"batch_size": 0}, {"batch_size": 512, "grad_accum_steps": 0}):
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    tr.derive_schedule(**kwargs)
        with self.assertRaises(ValueError):
            tr.examples_per_fit(train_frac=0.0)
        with self.assertRaises(ValueError):
            tr.examples_per_fit(epochs=0)


class Schedule(unittest.TestCase):
    """The cosine is his, transcribed."""

    WARMUP, MAX, BASE = 50, 12500, 1e-4

    def his_lambda(self, step: int) -> float:
        if step < self.WARMUP:
            return float(step) / max(1, self.WARMUP)
        progress = float(step - self.WARMUP) / max(1, self.MAX - self.WARMUP)
        return max(0.0, 0.5 * (1.0 + np.cos(np.pi * progress)))

    def test_matches_his_lr_lambda(self):
        schedule = tr.WarmupCosine(self.BASE, self.WARMUP, self.MAX)
        for step in (0, 1, 12, 24, 25, 26, 100, 3000, 6249, 6250):
            with self.subTest(step=step):
                self.assertAlmostEqual(float(schedule(step).numpy()),
                                       self.BASE * self.his_lambda(step), places=11)

    def test_the_first_step_has_zero_learning_rate(self):
        """His LambdaLR multiplies by lr_lambda(0) = 0. Transcribed, not tidied."""
        self.assertEqual(float(tr.WarmupCosine(self.BASE, self.WARMUP, self.MAX)(0).numpy()),
                         0.0)

    def test_the_peak_is_at_the_end_of_warmup(self):
        schedule = tr.WarmupCosine(self.BASE, self.WARMUP, self.MAX)
        peak = float(schedule(self.WARMUP).numpy())
        self.assertAlmostEqual(peak, self.BASE, places=9)
        self.assertLess(float(schedule(self.MAX - 1).numpy()), peak / 100.0)

    def test_warmup_must_fit(self):
        with self.assertRaises(ValueError):
            tr.WarmupCosine(self.BASE, 100, 100)


class Clipping(unittest.TestCase):
    """Global-norm clipping is torch's, epsilon included."""

    SHAPES = ((7,), (3, 4), (5, 5))

    def _gradients(self, norm: float):
        rng = np.random.RandomState(0)
        raw = [rng.randn(*s) for s in self.SHAPES]
        total = np.sqrt(sum((g ** 2).sum() for g in raw))
        return [g * (norm / total) for g in raw]

    @unittest.skipIf(torch is None, "torch unavailable")
    def test_matches_clip_grad_norm(self):
        for norm in (0.3, 1.0, 1.001, 7.0):
            with self.subTest(norm=norm):
                gradients = self._gradients(norm)
                parameters = [torch.nn.Parameter(torch.zeros(s, dtype=torch.float64))
                              for s in self.SHAPES]
                for parameter, gradient in zip(parameters, gradients):
                    parameter.grad = torch.tensor(gradient)
                torch.nn.utils.clip_grad_norm_(parameters, 1.0)
                global_norm = tf.linalg.global_norm([tf.constant(g) for g in gradients])
                coefficient = float(tr.torch_clip_coefficient(
                    tf.cast(global_norm, tf.float64), 1.0).numpy())
                for parameter, gradient in zip(parameters, gradients):
                    np.testing.assert_allclose(gradient * coefficient,
                                               parameter.grad.numpy(), atol=1e-15)

    @unittest.skipIf(torch is None, "torch unavailable")
    def test_keras_global_clipnorm_would_differ_at_the_threshold(self):
        """The control: the rejected formula, and where it diverges."""
        gradients = self._gradients(1.001)
        global_norm = float(tf.linalg.global_norm(
            [tf.constant(g) for g in gradients]).numpy())
        mine = float(tr.torch_clip_coefficient(
            tf.constant(global_norm, tf.float64), 1.0).numpy())
        keras = 1.0 / max(global_norm, 1.0)
        self.assertNotAlmostEqual(mine, keras, places=9)
        self.assertLess(mine, keras)          # torch's epsilon clips slightly harder

    def test_below_the_threshold_nothing_is_scaled(self):
        coefficient = tr.torch_clip_coefficient(tf.constant(0.5, tf.float64), 1.0)
        self.assertEqual(float(coefficient.numpy()), 1.0)

    def test_a_nonpositive_clip_is_refused(self):
        with self.assertRaises(ValueError):
            tr.ClippedTorchAdamW(grad_clip=0.0)

    def test_clipping_is_global_not_per_tensor(self):
        """Two tensors each under the threshold can still exceed it together."""
        optimizer = tr.ClippedTorchAdamW(grad_clip=1.0, **{**tr.TORCH_DEFAULTS})
        variables = [tf.Variable(np.zeros(4), dtype=tf.float64) for _ in range(2)]
        each = np.full(4, 0.4)                 # per-tensor norm 0.8, global 1.13
        optimizer.apply_gradients([(tf.constant(each), v) for v in variables])
        self.assertEqual(int(optimizer.clip_events.numpy()), 1)


class Realized(unittest.TestCase):
    """The plan and the record are different objects."""

    def test_a_matching_run_verifies(self):
        intended = tr.derive_schedule(512)
        policy = tr.RealizedPolicy(intended)
        policy.fits.append({"label": "step1", "examples_presented": intended["examples_per_fit"]})
        self.assertTrue(policy.verify()["held"])

    def test_a_short_run_is_caught(self):
        intended = tr.derive_schedule(512)
        policy = tr.RealizedPolicy(intended)
        policy.fits.append({"label": "step1",
                            "examples_presented": intended["examples_per_fit"] // 2})
        outcome = policy.verify()
        self.assertFalse(outcome["held"])
        self.assertIn("step1", outcome["problems"][0])

    def test_one_update_of_slack_is_allowed(self):
        intended = tr.derive_schedule(512)
        policy = tr.RealizedPolicy(intended)
        policy.fits.append({
            "label": "step1",
            "examples_presented": intended["examples_per_fit"] + intended["examples_per_update"],
        })
        self.assertTrue(policy.verify()["held"])

    def test_the_optimizer_counters_are_read_not_assumed(self):
        intended = tr.derive_schedule(512)
        optimizer = tr.ClippedTorchAdamW(grad_clip=1.0, **tr.TORCH_DEFAULTS)
        variable = tf.Variable(np.zeros(3), dtype=tf.float64)
        for _ in range(3):
            optimizer.apply_gradients([(tf.constant(np.full(3, 10.0)), variable)])
        row = tr.RealizedPolicy(intended).record_fit(optimizer, "probe")
        self.assertEqual(row["optimizer_steps_taken"], 3)
        self.assertEqual(row["clip_events"], 3)          # norm 17.3 >> 1.0 every time
        self.assertEqual(row["clip_fraction"], 1.0)


class Transfer(unittest.TestCase):
    """The loader's rules, and a verdict that is structural rather than proportional."""

    SOURCE = {
        "embed.mlp.fc1.weight": (256, 4),
        "embed.mlp.fc2.weight": (128, 256),
        "in_blocks.0.attn.in_proj_weight": (384, 128),
        "time_embed.fc1.weight": (256, 128),
        "out.weight": (1, 512),
    }

    def test_out_is_excluded_by_the_loader_rule(self):
        result = ct.classify(self.SOURCE, dict(self.SOURCE))
        verdicts = {r["key"]: r["verdict"] for r in result["rows"]}
        self.assertEqual(verdicts["out.weight"], "replaced")
        self.assertEqual(verdicts["embed.mlp.fc2.weight"], "transferred")

    def test_out_proj_is_not_caught_by_the_out_rule(self):
        """`out_proj.weight` does not contain the substring `out.`; attention must load."""
        result = ct.classify({"attn.out_proj.weight": (128, 128)},
                             {"attn.out_proj.weight": (128, 128)})
        self.assertEqual(result["rows"][0]["verdict"], "transferred")

    def test_shape_mismatch_reinitializes(self):
        target = dict(self.SOURCE)
        target["embed.mlp.fc1.weight"] = (256, 5)
        result = ct.classify(self.SOURCE, target)
        row = next(r for r in result["rows"] if r["key"] == "embed.mlp.fc1.weight")
        self.assertEqual(row["verdict"], "reinitialized")
        self.assertIn("(256, 5)", row["reason"])

    def test_a_missing_module_is_absent_not_reinitialized(self):
        target = {k: v for k, v in self.SOURCE.items() if k != "time_embed.fc1.weight"}
        result = ct.classify(self.SOURCE, target)
        row = next(r for r in result["rows"] if r["key"] == "time_embed.fc1.weight")
        self.assertEqual(row["verdict"], "absent_in_target")

    def test_a_broken_input_interface_is_flagged_despite_a_tiny_parameter_loss(self):
        """0.3 % of parameters, 100 % of the coordinate system. The point of the check."""
        target = dict(self.SOURCE)
        target["embed.mlp.fc1.weight"] = (256, 5)
        result = ct.classify(self.SOURCE, target)
        self.assertFalse(result["input_interface_intact"])
        self.assertIn("embed.mlp.fc1.weight", result["input_interface_broken_keys"])
        lost = sum(r["parameters"] for r in result["rows"] if r["verdict"] == "reinitialized")
        total = sum(r["parameters"] for r in result["rows"])
        self.assertLess(lost / total, 0.02)          # proportionally negligible
        self.assertIn("BROKEN", result["input_interface_reading"])

    def test_an_intact_interface_says_so(self):
        result = ct.classify(self.SOURCE, dict(self.SOURCE))
        self.assertTrue(result["input_interface_intact"])
        self.assertEqual(result["input_interface_broken_keys"], [])


if __name__ == "__main__":
    unittest.main(verbosity=1)
