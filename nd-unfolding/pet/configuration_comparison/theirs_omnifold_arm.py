"""Gregor's complete arm as an OmniFold-trainable estimator.

`pet2_omnifold_adapter.PET2OmniFold` wraps the port for OUR schema -- one token
block and an event block. His complete arm takes four inputs: the token block,
a categorical PID per token, a five-wide auxiliary block, and sixteen event
globals. This is that model, so the comparison can train the configuration F1
pins rather than a reduced stand-in.

Masking is the one thing that must not be inherited by accident. Our adapter
masks on the ENERGY column because our tokens are clusters and a zero-energy
cluster is padding. His token block is [px, py, pz, log E, PID] and a padded row
is all zeros, so the mask is "this row is not identically zero" -- taken on the
log-energy column, which is zero exactly for padding and non-zero for anything
real, since `log(E + 1e-3)` of a real object is never exactly 0 unless
E = 1 - 1e-3 by coincidence. The port's own `HIS_MASK_COLUMN` convention is
column 2, which for his tokens is `pz` -- a real object CAN have pz = 0, so
inheriting that would silently mask real tokens. The mask is passed explicitly
for exactly that reason.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from keras_backend import select_keras_backend

select_keras_backend()

import tensorflow as tf  # noqa: E402
from tensorflow import keras  # noqa: E402

import pet2_keras_port as port  # noqa: E402

# HIS STORAGE, not a convenience of ours: `preprocessing.py:583` stores
# `event_combined = concatenate([event_features, event_additional_info], axis=1)`
# as ONE (n_particles, 10) array, and the loader splits it at train time. So a
# 10-wide token block is his format, and it also happens to fit the vendored
# `DataLoader`, which carries two tensors per leg and not three.
#
#     columns 0..4   [px, py, pz, log E, PID]     -> features, PID split out
#     columns 5..9   [dE/dx, x, y, z, t]          -> add_info
#     event block    16 globals                    -> cond
PACKED_WIDTH = 10
LOG_E_COLUMN = 3          # [px, py, pz, log E, PID]
PID_COLUMN = 4
ADD_INFO_SLICE = slice(5, 10)


def weighted_binary_crossentropy(y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
    """The engine's loss: column 0 is the label, column 1 the weight."""
    labels = tf.cast(y_true[:, 0:1], y_pred.dtype)
    weights = tf.cast(y_true[:, 1:2], y_pred.dtype)
    per_row = tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=y_pred)
    return tf.reduce_mean(weights * per_row)


class TheirsCompleteArm(keras.Model):
    """PET2-small at the V1-paper flags, over his four inputs."""

    def __init__(self, num_part: int = 33, size: str = "small",
                 state_npz: Any = None, manifest: Any = None, **overrides: Any):
        """His configuration. `state_npz` is his PRETRAINED weights.

        The goal names his *pretrained* PET2-small, and the freeze records
        `initialization = best_model_pretrain_s.pt via
        load_pretrained_omnilearned`. This class built the port and never
        loaded it, so the arm was his ARCHITECTURE trained from scratch --
        which the goal rules out in as many words: "Scratch tuning and scratch
        variance cannot substitute for the pretrained arm." Nothing in the
        code contradicted the freeze; the freeze simply described an intent.

        `state_npz` stays optional because the port's own equivalence tests
        construct this class without a checkpoint. The DRIVER requires it, so
        a campaign arm cannot be scratch by omission.
        """
        super().__init__()
        # `use_int` and `local_int` are stated, not left to the port's
        # defaults. `frozen_design.THEIRS_COMPLETE` declares both False -- the
        # V1-paper flags -- and the pretrained manifest records both. Leaving
        # them implicit made the arm's settings INCOMPLETE, so the manifest
        # check reported a difference between False and "not mentioned".
        settings = dict(input_dim=4, pid=True, pid_dim=8, add_info=True, add_dim=5,
                        conditional=True, cond_dim=16, num_coord=2, K=10,
                        num_classes=1, use_int=False, local_int=False)
        settings.update(overrides)
        self.num_part = num_part
        self.settings = settings
        # What `get_config` must hand the clone. Stored before the model is
        # built, so a construction failure cannot leave it half-written.
        self._config = {"num_part": num_part, "size": size,
                        "state_npz": None if state_npz is None else str(state_npz),
                        "manifest": None if manifest is None else str(manifest),
                        **overrides}
        preset = port.preset(size)
        if manifest is not None:
            self._assert_matches_manifest(settings, preset, manifest)
        self.backbone = port.PET2Port(**settings, **preset)
        self.loss_tracker = keras.metrics.Mean(name="loss")
        self.pretrained = None
        if state_npz is not None:
            import pretrained_init as pinit

            self.pretrained = pinit.load_state_into(
                self.backbone, Path(state_npz),
                None if manifest is None else Path(manifest))

    def get_config(self) -> dict[str, Any]:
        """Carry the CHECKPOINT through `clone_model`.

        `omnifold.py:279` does `model_e = tf.keras.models.clone_model(model)`
        before every fit, and `clone_model` rebuilds the architecture with
        FRESH RANDOM WEIGHTS. So loading the pretrained state in `__init__`
        was undone by the engine on the first iteration, and the arm trained
        from scratch anyway.

        The proof it was happening: with the state loaded exactly -- 176
        tensors, 2,758,702 parameters, worst difference 0.0 -- step 1's
        validation loss came out 103.95602416992188, bit-identical to the
        scratch run before it. Different initial weights cannot give an
        identical loss.

        The clone goes through `from_config`, so putting the state path in the
        config makes the clone load it too. That fixes it without touching the
        engine, which is hash-pinned by the Gate-2 receipt.
        """
        config = dict(self._config)
        return config

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "TheirsCompleteArm":
        return cls(**config)

    @staticmethod
    def _assert_matches_manifest(settings: dict, preset: dict, manifest: Any) -> None:
        """The state was exported for one model; refuse to load it into another.

        `load_state_into` would already fail on coverage, but it fails with a
        list of tensor names. Comparing the settings first says WHICH setting
        disagrees, which is the difference between a five-minute fix and an
        afternoon.
        """
        import json

        record = json.loads(Path(manifest).read_text())
        for field, ours in (("settings", settings), ("preset", preset)):
            theirs = record.get(field, {})
            differing = {k: (ours.get(k), theirs.get(k)) for k in set(ours) | set(theirs)
                         if ours.get(k) != theirs.get(k)}
            if differing:
                raise ValueError(
                    f"the pretrained state was exported for different {field}: "
                    f"{differing} (ours, manifest). Loading it would either fail "
                    "on coverage or, worse, succeed into a different network")

    @property
    def metrics(self) -> list[Any]:
        return [self.loss_tracker]

    def pad_mask(self, tokens: tf.Tensor) -> tf.Tensor:
        """A padded row is identically zero; a real one is not.

        Taken on log-energy rather than on the port's default column 2, which is
        `pz` for his layout and is legitimately zero for a real object.
        """
        return tf.cast(tokens[:, :, LOG_E_COLUMN : LOG_E_COLUMN + 1] != 0,
                       tokens.dtype)

    def call(self, inputs: Any, training: bool = True) -> tf.Tensor:
        """Accepts his packed form `[part, evt]`, or the unpacked triple.

        The packed form is what the vendored `DataLoader` carries and what his
        own dataset stores, so the comparison runs through the engine unmodified.
        """
        if len(inputs) == 2:
            part, globals_ = inputs[0], inputs[1]
            tokens = part[:, :, :5]
            add_info = part[:, :, ADD_INFO_SLICE]
        else:
            tokens, add_info, globals_ = inputs[0], inputs[1], inputs[2]
        pid = tf.cast(tokens[:, :, PID_COLUMN], tf.int32)
        features = tokens[:, :, :4]
        return self.backbone(features, cond=globals_, pid=pid, add_info=add_info,
                             mask=self.pad_mask(tokens), training=training)

    #: XLA is NOT AVAILABLE through this engine, measured rather than assumed.
    #: Forcing `jit_compile=True` compiles the whole `train_step`, including the
    #: optimizer, and the engine wraps the optimizer in Horovod's
    #: `DistributedAdam`. Its allreduce emits a `cond` that tf2xla cannot
    #: convert: "tf2xla conversion failed while converting
    #: __inference_run_step" inside `DistributedAdam_Allreduce/cond_152`
    #: (job 58601848). Single GPU or not, the conditional is in the graph.
    #:
    #: So the 410.6 microseconds per example and 21.7 GiB in
    #: `EXECUTION` -- both taken under `tf.function(jit_compile=True)` on the
    #: bare model -- describe a path this arm cannot take while the engine owns
    #: the optimizer. What makes the arm fit in memory is the FLAT PROJECTION,
    #: which is a property of the model and needs no compiler.
    force_jit_compile = False

    def compile(self, *args: Any, **kw: Any) -> None:
        """Honour `force_jit_compile`, which is off for the reason above."""
        if self.force_jit_compile:
            kw["jit_compile"] = True
        super().compile(*args, **kw)

    def train_step(self, data: Any) -> dict[str, Any]:
        x, y = data
        with tf.GradientTape() as tape:
            loss = weighted_binary_crossentropy(y, self(x, training=True))
        self.optimizer.minimize(loss, self.trainable_variables, tape=tape)
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}

    def test_step(self, data: Any) -> dict[str, Any]:
        x, y = data
        loss = weighted_binary_crossentropy(y, self(x, training=False))
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}


def build(num_part: int = 33, size: str = "small", **overrides: Any):
    return TheirsCompleteArm(num_part=num_part, size=size, **overrides)
