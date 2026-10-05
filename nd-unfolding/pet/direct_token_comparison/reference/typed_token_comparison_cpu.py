"""Matched pooled/direct typed-token attention for diagnostic experiments.

Both routes reuse the v2 family feature preparation and token MLPs. Only the
reduction before attention differs. This is an isolated attention bridge, not
the production PET architecture or a checkpoint-compatible Gregor model.
"""

from __future__ import annotations

from functools import cache
from typing import Any

import typed_descriptor_keras as adapter
import typed_descriptors as typed


@cache
def comparison_model_type() -> type[Any]:
    """Register and return the lazily imported Keras comparison model class."""
    tf = adapter.require_tensorflow()

    @tf.keras.utils.register_keras_serializable(package="minerva_pet")
    class TypedTokenComparison(tf.keras.Model):  # type: ignore[name-defined,misc]
        """Route identical typed embeddings through a shared attention architecture.

        Parameters
        ----------
        normalization_config : dict
            Serialized, schema-bound v2 normalization; never fitted here.
        routing : str
            ``pooled`` sums within families; ``direct`` retains each object.
        width : int
            Attention width, divisible by four.
        """

        def __init__(
            self,
            normalization_config: dict[str, Any],
            routing: str,
            width: int = 32,
            **kwargs: Any,
        ) -> None:
            super().__init__(**kwargs)
            if routing not in ("pooled", "direct"):
                raise ValueError("routing must be pooled or direct")
            if width < 4 or width % 4:
                raise ValueError("width must be positive and divisible by four")
            normalization = adapter.frozen_normalization_from_config(
                normalization_config
            )
            self.normalization_config = adapter.frozen_normalization_to_config(
                normalization
            )
            self.routing = routing
            self.width = width
            reference = adapter.build_keras_typed_descriptor_adapter(normalization)
            self.encoders = list(reference.family_encoders.values())
            self.event_projection = tf.keras.layers.Dense(width)
            self.generic_projection = tf.keras.layers.Dense(width)
            self.typed_projection = tf.keras.layers.Dense(width)
            self.attention = tf.keras.layers.MultiHeadAttention(4, width // 4)
            self.attention_norm = tf.keras.layers.LayerNormalization()
            self.feed_forward = tf.keras.Sequential(
                [
                    tf.keras.layers.Dense(2 * width, activation="gelu"),
                    tf.keras.layers.Dense(width),
                ]
            )
            self.output_norm = tf.keras.layers.LayerNormalization()
            self.classifier = tf.keras.layers.Dense(1)

        def build(self, input_shape: dict[str, Any]) -> None:
            for encoder in self.encoders:
                encoder.build({})
            self.event_projection.build((None, 16))
            self.generic_projection.build(input_shape["generic_values"])
            self.typed_projection.build((None, None, 16))
            shape = (None, None, self.width)
            self.attention.build(shape, shape)
            self.attention_norm.build(shape)
            self.feed_forward.build(shape)
            self.output_norm.build(shape)
            self.classifier.build((None, self.width))
            super().build(input_shape)

        def route_tokens(
            self, inputs: dict[str, Any], training: bool = False
        ) -> tuple[Any, Any, Any]:
            """Return typed embeddings, explicit presence, and enabled raw counts."""
            rows = tf.shape(inputs[adapter.DETECTOR_INPUT_KEY])[0]
            clouds, presence, counts = [], [], []
            for contract, encoder in zip(typed.FAMILY_CONTRACTS, self.encoders):
                prefix = contract.name
                token_mask = tf.cast(inputs[f"{prefix}_token_mask"], tf.bool)
                segment = tf.cast(inputs[f"{prefix}_segment_ids"], tf.int32)
                enabled = tf.cast(inputs[f"{prefix}_enabled"], tf.bool)
                count = tf.cast(inputs[f"{prefix}_counts"], tf.float32)
                tf.debugging.assert_equal(
                    tf.math.unsorted_segment_sum(
                        tf.cast(token_mask, tf.float32), segment, rows
                    ),
                    count,
                )
                features = encoder.prepare_features(
                    inputs[f"{prefix}_values"], inputs[f"{prefix}_masks"], token_mask
                )
                projected = encoder.token_mlp(features, training=training)
                active = token_mask & tf.gather(enabled, segment)
                projected = tf.where(active[:, None], projected, 0.0)
                counts.append(tf.where(enabled, count, 0.0))
                if self.routing == "pooled":
                    clouds.append(
                        tf.math.unsorted_segment_sum(projected, segment, rows)[
                            :, None, :
                        ]
                    )
                    presence.append((enabled & (count > 0))[:, None])
                else:
                    # Padding is local to this batch and never truncates objects.
                    clouds.append(
                        tf.RaggedTensor.from_value_rowids(
                            projected, segment, nrows=rows
                        ).to_tensor()
                    )
                    presence.append(
                        tf.RaggedTensor.from_value_rowids(
                            active, segment, nrows=rows
                        ).to_tensor(default_value=False)
                    )
            return (
                tf.concat(clouds, axis=1),
                tf.concat(presence, axis=1),
                tf.stack(counts, axis=1),
            )

        def call(self, inputs: dict[str, Any], training: bool = False) -> Any:
            typed_cloud, typed_mask, counts = self.route_tokens(inputs, training)
            event = tf.cast(inputs[adapter.DETECTOR_INPUT_KEY], tf.float32)
            tf.debugging.assert_equal(tf.shape(event)[1], 13)
            tf.debugging.assert_all_finite(event, "Non-finite event features")
            generic_mask = tf.cast(inputs["generic_mask"], tf.bool)
            generic = tf.cast(inputs["generic_values"], tf.float32)
            generic = tf.where(generic_mask[:, :, None], generic, 0.0)
            tf.debugging.assert_all_finite(generic, "Non-finite active generic input")
            event_token = self.event_projection(tf.concat([event, counts], -1))
            tokens = tf.concat(
                [
                    event_token[:, None, :],
                    self.generic_projection(generic),
                    self.typed_projection(typed_cloud),
                ],
                axis=1,
            )
            mask = tf.concat(
                [
                    tf.ones((tf.shape(event)[0], 1), dtype=tf.bool),
                    generic_mask,
                    typed_mask,
                ],
                axis=1,
            )
            attended = self.attention(
                tokens, tokens, attention_mask=mask[:, None, :], training=training
            )
            hidden = self.attention_norm(tokens + attended)
            hidden = self.output_norm(hidden + self.feed_forward(hidden))
            return self.classifier(hidden[:, 0, :])

        def get_config(self) -> dict[str, Any]:
            return {
                **super().get_config(),
                "normalization_config": self.normalization_config,
                "routing": self.routing,
                "width": self.width,
            }

    return TypedTokenComparison


def build_comparison(
    normalization: typed.FrozenNormalization, *, routing: str, width: int = 32
) -> Any:
    """Build an untrained diagnostic model with explicit frozen normalization."""
    return comparison_model_type()(
        adapter.frozen_normalization_to_config(normalization), routing, width
    )
