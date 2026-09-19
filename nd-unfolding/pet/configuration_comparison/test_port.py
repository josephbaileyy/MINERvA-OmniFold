"""Tests for the PET2 port, the torch-faithful optimizer and the OI-125 recorder.

The regression tests that matter are the ones that would have caught the defects
found while building these: `_gelu` using the library's inexact "exact" GELU, the
recorder hooking the step that CONSUMES a push rather than the one that produces
it, and an optimizer that is nearly but not quite torch's.
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import fold_forward_recorder as ffr
import pet2_keras_port as port
import pet2_omnifold_adapter as adapter
import port_checks as pc
import tensorflow as tf
from torch_adamw import TORCH_DEFAULTS, TorchAdamW

try:
    import torch
except ImportError:  # pragma: no cover - torch is present in this environment
    torch = None


class Inventory(unittest.TestCase):
    """P-1's content, at unit scale."""

    def test_paper_preset_parameter_count(self):
        model = port.PET2Port(input_dim=4, conditional=True, cond_dim=16, pid=True,
                              pid_dim=8, add_info=True, add_dim=5, num_classes=1,
                              num_coord=2, K=10, **port.preset("small"))
        inventory = port.parameter_inventory(model)
        self.assertEqual(len(inventory), 176)
        total = sum(int(np.prod(v.shape)) for _, v in inventory)
        self.assertEqual(total, 2_758_702)

    def test_names_are_unique(self):
        model = port.PET2Port(input_dim=4, conditional=True, cond_dim=16,
                              num_classes=1, num_coord=2, K=10, **port.preset("small"))
        names = [n for n, _ in port.parameter_inventory(model)]
        self.assertEqual(len(names), len(set(names)))

    def test_preset_is_a_copy(self):
        """A caller mutating the returned preset must not edit the table."""
        first = port.preset("small")
        first["num_heads"] = 999
        self.assertEqual(port.preset("small")["num_heads"], 8)


class Refusals(unittest.TestCase):
    """The port fails loudly where it would otherwise invent physics or shapes."""

    def test_interaction_blocks_are_refused(self):
        for flags in ({"use_int": True}, {"local_int": True}, {"use_int": True, "local_int": True}):
            with self.subTest(**flags):
                with self.assertRaises(NotImplementedError):
                    port.PET2Port(input_dim=4, num_classes=1, num_coord=2, K=10,
                                  **flags, **port.preset("small"))

    def test_paper_flags_are_both_false(self):
        self.assertEqual(port.PAPER_INTERACTION_FLAGS, {"use_int": False, "local_int": False})

    def test_coord_idx_out_of_range_is_refused(self):
        with self.assertRaises(ValueError):
            port.PET2Port(input_dim=4, num_classes=1, coord_idx=(0, 9), num_coord=2,
                          K=10, **port.preset("small"))

    def test_mask_idx_out_of_range_is_refused(self):
        with self.assertRaises(ValueError):
            port.PET2Port(input_dim=4, num_classes=1, num_coord=2, mask_idx=7, K=10,
                          **port.preset("small"))

    def test_unknown_preset_is_refused(self):
        with self.assertRaises(ValueError):
            port.preset("enormous")

    def test_adapter_refuses_K_larger_than_the_token_budget(self):
        """K + 1 neighbours cannot be drawn from fewer than K + 1 tokens."""
        with self.assertRaises(ValueError):
            adapter.PET2OmniFold(num_feat=5, num_evt=13, num_part=10, coord_idx=(1, 2), K=10)
        adapter.PET2OmniFold(num_feat=5, num_evt=13, num_part=11, coord_idx=(1, 2), K=10)


class Activation(unittest.TestCase):
    """`tf.nn.gelu(approximate=False)` is not exact; the port's written-out form is."""

    @unittest.skipIf(torch is None, "torch unavailable")
    def test_gelu_matches_torch_in_float64(self):
        x = np.linspace(-6.0, 6.0, 257)
        reference = torch.nn.functional.gelu(torch.from_numpy(x)).numpy()
        ours = port._gelu(tf.constant(x)).numpy()
        self.assertLess(np.abs(ours - reference).max(), 1e-15)

    @unittest.skipIf(torch is None, "torch unavailable")
    def test_library_gelu_would_have_failed_this(self):
        """The control: the rejected implementation is off by ~1e-9, not ~1e-16."""
        x = np.linspace(-6.0, 6.0, 257)
        reference = torch.nn.functional.gelu(torch.from_numpy(x)).numpy()
        library = tf.nn.gelu(tf.constant(x), approximate=False).numpy()
        self.assertGreater(np.abs(library - reference).max(), 1e-12)


class Masking(unittest.TestCase):
    """The mask column is ours, not his, and padded slots stay unreachable."""

    def test_adapter_masks_on_energy_not_column_two(self):
        model = adapter.PET2OmniFold(num_feat=5, num_evt=13, num_part=12, coord_idx=(1, 2))
        part = np.ones((2, 12, 5), dtype=np.float32)
        part[0, 3, 2] = 0.0          # z == 0 on a REAL token: his rule would drop it
        part[1, 4, 0] = 0.0          # energy == 0: genuinely padded
        mask = model.pad_mask(tf.constant(part)).numpy()
        self.assertEqual(mask[0, 3, 0], 1.0)
        self.assertEqual(mask[1, 4, 0], 0.0)

    def test_padded_tokens_cannot_change_the_output(self):
        model = adapter.PET2OmniFold(num_feat=5, num_evt=13, num_part=12, coord_idx=(1, 2))
        rng = np.random.RandomState(3)
        part = np.abs(rng.rand(4, 12, 5)).astype(np.float32)
        part[:, 6:, :] = 0.0
        evt = rng.randn(4, 13).astype(np.float32)
        before = model([tf.constant(part), tf.constant(evt)], training=False).numpy()
        noisy = part.copy()
        noisy[:, 6:, :] = rng.randn(4, 6, 5).astype(np.float32)
        noisy[:, 6:, adapter.PAD_COLUMN] = 0.0
        after = model([tf.constant(noisy), tf.constant(evt)], training=False).numpy()
        np.testing.assert_array_equal(before, after)

    def test_event_with_no_tokens_and_a_zeroed_event_block_is_finite(self):
        """The production state that makes every attention key vanish.

        `fullevent_fps_dataloader` zeroes the event block of rows failing
        `pass_reco`, and `PET2.initialize_weights` zeroes every bias, so at the
        first training step `cond_embed(0)` is exactly 0 and masks the conditioning
        token off too. With no recoil tokens either, the classifier's query has no
        key left. A plain softmax gives NaN; torch returns zero and so must we.
        """
        model = adapter.PET2OmniFold(num_feat=5, num_evt=13, num_part=12, coord_idx=(1, 2))
        part = np.zeros((1, 12, 5), dtype=np.float32)
        evt = np.zeros((1, 13), dtype=np.float32)
        out = model([tf.constant(part), tf.constant(evt)], training=False).numpy()
        self.assertTrue(np.isfinite(out).all())

    def test_fully_masked_attention_returns_zero_like_torch(self):
        attention = port.MultiheadAttention(4, 2, bias=False, dtype="float64")
        q = tf.constant(np.random.RandomState(0).randn(1, 2, 4))
        k = tf.constant(np.random.RandomState(1).randn(1, 3, 4))
        out = attention(q, k, k, key_padding_mask=tf.constant([[True, True, True]]))
        np.testing.assert_array_equal(out.numpy(), np.zeros((1, 2, 4)))


class Optimizer(unittest.TestCase):
    """TorchAdamW must be torch's rule, and must beat the stock one decisively."""

    GRADIENTS = np.array([1.0, 1e-3, 1e-6, 1e-9, 0.0, -2.5])

    def _run(self, make_keras, steps):
        start = np.random.RandomState(0).randn(6)
        parameter = torch.tensor(start.copy(), requires_grad=True)
        reference = torch.optim.AdamW(
            [parameter], lr=TORCH_DEFAULTS["learning_rate"],
            weight_decay=TORCH_DEFAULTS["weight_decay"], betas=(0.9, 0.999), eps=1e-8)
        variable = tf.Variable(start.copy(), dtype=tf.float64)
        optimizer = make_keras()
        for _ in range(steps):
            parameter.grad = torch.tensor(self.GRADIENTS.copy())
            reference.step()
            optimizer.apply_gradients([(tf.constant(self.GRADIENTS, tf.float64), variable)])
        return np.abs(parameter.detach().numpy() - variable.numpy()).max()

    @unittest.skipIf(torch is None, "torch unavailable")
    def test_matches_torch(self):
        for steps in (1, 5):
            with self.subTest(steps=steps):
                self.assertLess(self._run(lambda: TorchAdamW(**TORCH_DEFAULTS), steps), 1e-12)

    @unittest.skipIf(torch is None, "torch unavailable")
    def test_stock_keras_adamw_does_not(self):
        """The control. Without this the previous test proves only that a number is small."""
        stock = self._run(lambda: tf.keras.optimizers.AdamW(**TORCH_DEFAULTS), 1)
        ported = self._run(lambda: TorchAdamW(**TORCH_DEFAULTS), 1)
        self.assertGreater(stock, 1e-6)
        self.assertGreater(stock / max(ported, 1e-300), 1e3)

    def test_sparse_gradients_are_refused(self):
        variable = tf.Variable(np.zeros(4), dtype=tf.float64)
        optimizer = TorchAdamW(**TORCH_DEFAULTS)
        slices = tf.IndexedSlices(tf.constant([[1.0]], tf.float64), tf.constant([0]),
                                  tf.constant([4]))
        with self.assertRaises(NotImplementedError):
            optimizer.apply_gradients([(slices, variable)])


class FoldForwardRatio(unittest.TestCase):
    """The arithmetic, and the populations on which it is undefined."""

    def test_matches_the_driver_formula(self):
        w = np.array([1.0, 2.0, 3.0, 4.0])
        push = np.array([1.0, 2.0, 0.5, 9.0])
        keep = np.array([True, True, True, False])
        expected = (1 * 1 + 2 * 2 + 3 * 0.5) / (1 + 2 + 3)
        self.assertAlmostEqual(ffr.fold_forward_ratio(w, push, keep), expected)

    def test_unit_push_gives_one(self):
        w = np.array([3.0, 1.0, 2.0])
        self.assertAlmostEqual(
            ffr.fold_forward_ratio(w, np.ones(3), np.array([True, False, True])), 1.0)

    def test_rows_outside_pass_reco_are_ignored(self):
        w = np.array([1.0, 1.0])
        keep = np.array([True, False])
        first = ffr.fold_forward_ratio(w, np.array([2.0, 5.0]), keep)
        second = ffr.fold_forward_ratio(w, np.array([2.0, 1e9]), keep)
        self.assertEqual(first, second)

    def test_empty_population_is_refused(self):
        with self.assertRaises(ValueError):
            ffr.fold_forward_ratio(np.ones(3), np.ones(3), np.zeros(3, dtype=bool))

    def test_misaligned_rows_are_refused(self):
        with self.assertRaises(ValueError):
            ffr.fold_forward_ratio(np.ones(3), np.ones(4), np.ones(3, dtype=bool))

    def test_zero_weight_population_is_refused(self):
        with self.assertRaises(ValueError):
            ffr.fold_forward_ratio(np.zeros(2), np.ones(2), np.ones(2, dtype=bool))


class FakeMultiFold:
    """The two-step loop's push bookkeeping, and nothing else."""

    def __init__(self, rows, niter, pushes):
        self.niter = niter
        self.start = 0
        self._pushes = pushes
        self.weights_push = np.ones(rows)
        self.step1_saw = []

    def RunStep1(self, i):
        self.step1_saw.append(self.weights_push.copy())

    def RunStep2(self, i):
        self.weights_push = np.full_like(self.weights_push, self._pushes[i])

    def Unfold(self):
        for i in range(self.start, self.niter):
            self.RunStep1(i)
            self.RunStep2(i)


class Recorder(unittest.TestCase):
    """OI-125: the end-of-run push must be RECORDED, not reconstructed."""

    ROWS = 5

    def _run(self, pushes):
        engine = FakeMultiFold(self.ROWS, len(pushes), pushes)
        w = np.ones(self.ROWS)
        keep = np.ones(self.ROWS, dtype=bool)
        recorder = ffr.FoldForwardRecorder(engine, w, keep, label="t")
        with recorder:
            engine.Unfold()
        return engine, recorder

    def test_end_of_run_push_is_captured(self):
        """The regression. A RunStep1-only hook never sees the last RunStep2."""
        pushes = [0.5, 0.75, 1.25]
        engine, recorder = self._run(pushes)
        self.assertAlmostEqual(recorder.end_of_run_ratio(), 1.25)
        # What the old instrumentation would have seen: the pushes CONSUMED by the
        # three step 1s, which are 1.0, 0.5 and 0.75 -- the final 1.25 is absent.
        consumed = [r["ratio"] for r in recorder.rows if r["occasion"] == "consumed_by_step1"]
        self.assertEqual(consumed, [1.0, 0.5, 0.75])
        self.assertNotIn(1.25, consumed)

    def test_last_consumed_row_has_the_opposite_sign_to_the_end_of_run_row(self):
        """The ledger's finding, reproduced: substituting flips sign(ratio - 1)."""
        _, recorder = self._run([0.5, 0.75, 1.25])
        consumed = [r["ratio"] for r in recorder.rows if r["occasion"] == "consumed_by_step1"]
        self.assertLess(consumed[-1] - 1.0, 0.0)
        self.assertGreater(recorder.end_of_run_ratio() - 1.0, 0.0)

    def test_summary_counts_and_flags(self):
        _, recorder = self._run([0.5, 0.75, 1.25])
        summary = recorder.summary()
        self.assertEqual(summary["pushes_produced"], 3)
        self.assertEqual(summary["pushes_consumed_by_a_later_step1"], 3)
        self.assertTrue(summary["end_of_run_is_recorded_not_reconstructed"])
        self.assertAlmostEqual(summary["end_of_run_ratio"], 1.25)

    def test_detach_restores_the_engine(self):
        engine = FakeMultiFold(self.ROWS, 1, [0.5])
        original_step1, original_step2 = engine.RunStep1, engine.RunStep2
        recorder = ffr.FoldForwardRecorder(engine, np.ones(self.ROWS),
                                           np.ones(self.ROWS, dtype=bool))
        recorder.attach()
        self.assertIn("RunStep1", vars(engine))
        recorder.detach()
        # Bound methods compare unequal by identity on every access, so the check
        # is that no instance attribute SHADOWS the class method any more.
        self.assertNotIn("RunStep1", vars(engine))
        self.assertNotIn("RunStep2", vars(engine))
        self.assertEqual(engine.RunStep1.__func__, original_step1.__func__)
        self.assertEqual(engine.RunStep2.__func__, original_step2.__func__)

    def test_detach_happens_even_on_an_exception(self):
        engine = FakeMultiFold(self.ROWS, 1, [0.5])
        recorder = ffr.FoldForwardRecorder(engine, np.ones(self.ROWS),
                                           np.ones(self.ROWS, dtype=bool))
        with self.assertRaises(RuntimeError):
            with recorder:
                raise RuntimeError("boom")
        self.assertNotIn("RunStep2", vars(engine))

    def test_no_step2_means_no_end_of_run_value(self):
        """Better to refuse than to hand back the last thing in the list."""
        engine = FakeMultiFold(self.ROWS, 0, [])
        recorder = ffr.FoldForwardRecorder(engine, np.ones(self.ROWS),
                                           np.ones(self.ROWS, dtype=bool))
        with recorder:
            engine.Unfold()
        with self.assertRaises(RuntimeError):
            recorder.end_of_run_ratio()
        self.assertFalse(recorder.summary()["end_of_run_is_recorded_not_reconstructed"])

    def test_attaching_twice_is_refused(self):
        engine = FakeMultiFold(self.ROWS, 1, [0.5])
        recorder = ffr.FoldForwardRecorder(engine, np.ones(self.ROWS),
                                           np.ones(self.ROWS, dtype=bool))
        recorder.attach()
        with self.assertRaises(RuntimeError):
            recorder.attach()
        recorder.detach()

    def test_engine_without_the_two_step_loop_is_refused(self):
        class NotMultiFold:
            pass

        with self.assertRaises(AttributeError):
            ffr.FoldForwardRecorder(NotMultiFold(), np.ones(2),
                                    np.ones(2, dtype=bool)).attach()


class Schemas(unittest.TestCase):
    """The two OmniFold steps carry different widths and different geometry."""

    def test_step_schemas_match_the_production_loader(self):
        self.assertEqual(adapter.STEP_SCHEMAS["step1_reco"]["num_feat"], 5)
        self.assertEqual(adapter.STEP_SCHEMAS["step1_reco"]["num_evt"], 13)
        self.assertEqual(adapter.STEP_SCHEMAS["step1_reco"]["coord_idx"], (1, 2))
        self.assertEqual(adapter.STEP_SCHEMAS["step2_gen"]["num_feat"], 8)
        self.assertEqual(adapter.STEP_SCHEMAS["step2_gen"]["num_evt"], 2)
        self.assertEqual(adapter.STEP_SCHEMAS["step2_gen"]["coord_idx"], (5, 6, 7))

    def test_each_step_model_takes_its_own_widths(self):
        for step, rows in (("step1_reco", 3), ("step2_gen", 3)):
            with self.subTest(step=step):
                schema = adapter.STEP_SCHEMAS[step]
                model = adapter.build_step_model(step, num_part=12)
                part = np.abs(np.random.RandomState(1).rand(rows, 12, schema["num_feat"]))
                evt = np.random.RandomState(2).randn(rows, schema["num_evt"])
                out = model([tf.constant(part, tf.float32), tf.constant(evt, tf.float32)],
                            training=False)
                self.assertEqual(tuple(out.shape), (rows, 1))

    def test_unknown_step_is_refused(self):
        with self.assertRaises(ValueError):
            adapter.build_step_model("step3_imaginary")


if __name__ == "__main__":
    unittest.main(verbosity=1)


class Float32Limit(unittest.TestCase):
    """P-2a's limit must not widen when the thing it tests gets worse."""

    def test_a_correct_port_passes(self):
        verdict = pc.float32_verdict(cross_engine=2.6e-7, reference_deviation=2.0e-7,
                                     our_deviation=1.6e-7)
        self.assertTrue(verdict["held"])

    def test_inflating_our_own_error_makes_the_verdict_worse(self):
        """The regression. Under the old `reference + ours` budget this PASSED."""
        reference, cross = 2.0e-7, 2.6e-7
        good = pc.float32_verdict(cross, reference, our_deviation=1.6e-7)
        bad = pc.float32_verdict(cross, reference, our_deviation=9.0e-6)
        self.assertTrue(good["held"])
        self.assertFalse(bad["held"])
        # The limit is identical in both: it depends on the reference alone.
        self.assertEqual(good["limit_from_reference_only"],
                         bad["limit_from_reference_only"])
        # And the superseded rule would have admitted the bad one.
        self.assertLess(cross, reference + 9.0e-6)

    def test_a_large_cross_engine_difference_fails_whatever_our_deviation(self):
        for ours in (1e-12, 1.0e-7, 1.0e-3):
            with self.subTest(ours=ours):
                self.assertFalse(
                    pc.float32_verdict(5.0e-6, 2.0e-7, ours)["held"])
