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

    def __init__(self, num_part: int = 33, size: str = "small", **overrides: Any):
        super().__init__()
        settings = dict(input_dim=4, pid=True, pid_dim=8, add_info=True, add_dim=5,
                        conditional=True, cond_dim=16, num_coord=2, K=10,
                        num_classes=1)
        settings.update(overrides)
        self.num_part = num_part
        self.settings = settings
        self.backbone = port.PET2Port(**settings, **port.preset(size))
        self.loss_tracker = keras.metrics.Mean(name="loss")

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
