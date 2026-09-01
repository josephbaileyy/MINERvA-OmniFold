"""Lazy, CPU-only Keras Deep Sets adapter for typed PET descriptors.

The committed typed-descriptor module remains authoritative for raw fields,
component masks, categorical identities, and frozen normalization. This module
only converts its validated ragged batches into flat tensor inputs and supplies
family-specific trainable token networks with segment-sum pooling. TensorFlow is
imported only when a Keras-facing function is called.

The adapter augments the 13-column reconstructed detector event block. It has no
truth-descriptor interface and rejects the legitimate two-column truth block.
"""

from __future__ import annotations

import importlib
from functools import cache
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

import typed_descriptors as typed


DETECTOR_INPUT_KEY = "detector_event_features"
KERAS_SERIALIZATION_PACKAGE = "minerva_pet"


def require_tensorflow() -> Any:
    """Import and return TensorFlow only when the Keras adapter is requested.

    Returns
    -------
    module
        Imported TensorFlow module.

    Raises
    ------
    ImportError
        If TensorFlow is not installed in the active environment.
    """

    try:
        return importlib.import_module("tensorflow")
    except ImportError as error:
        raise ImportError(
            "The typed-descriptor Keras adapter requires optional TensorFlow; "
            "the NumPy contract and source smoke do not."
        ) from error


def prepare_keras_inputs(
    batch: typed.TypedDescriptorBatch,
    detector_event_features: np.ndarray,
) -> dict[str, np.ndarray]:
    """Convert one validated ragged descriptor batch into flat tensor inputs.

    Values remain raw here. The Keras family layers apply the explicit frozen
    normalization and masks so those operations are serialized with the model.
    Segment IDs preserve arbitrary object cardinality without global padding.

    Parameters
    ----------
    batch : typed_descriptors.TypedDescriptorBatch
        Validated detector-side typed descriptors.
    detector_event_features : numpy.ndarray
        Existing reconstructed event block with shape ``(rows, 13)``.

    Returns
    -------
    dict[str, numpy.ndarray]
        Flat per-token values and masks, segment IDs, explicit counts, family
        enable masks, and the unchanged detector event block.

    Raises
    ------
    ValueError
        If the event block is not the detector-side 13-column schema or any
        converted input is non-finite.
    """

    event_array = np.asarray(detector_event_features, dtype=np.float32)
    expected_shape = (batch.row_count, typed.DETECTOR_EVENT_WIDTH)
    if event_array.shape != expected_shape:
        raise ValueError(
            f"Detector event features must have shape {expected_shape}; "
            "truth descriptors are not defined"
        )
    if not np.all(np.isfinite(event_array)):
        raise ValueError("Detector event features must be finite")

    inputs: dict[str, np.ndarray] = {DETECTOR_INPUT_KEY: event_array.copy()}
    for contract in typed.FAMILY_CONTRACTS:
        family = batch.families[contract.name]
        contract.validate_batch(family)
        values = np.concatenate(
            [
                np.asarray(family.values[field.name], dtype=np.float32)
                for field in contract.fields
            ],
            axis=1,
        )
        masks = np.concatenate(
            [
                np.asarray(family.masks[field.name], dtype=np.bool_)
                for field in contract.fields
            ],
            axis=1,
        )
        if not np.all(np.isfinite(values)):
            raise ValueError(f"{contract.name} raw values must be finite")
        row_lengths = np.diff(family.offsets)
        segment_ids = np.repeat(
            np.arange(batch.row_count, dtype=np.int32), row_lengths
        )
        prefix = contract.name
        inputs[f"{prefix}_values"] = values
        inputs[f"{prefix}_masks"] = masks
        inputs[f"{prefix}_segment_ids"] = segment_ids
        inputs[f"{prefix}_token_mask"] = np.asarray(
            family.token_mask, dtype=np.bool_
        )
        inputs[f"{prefix}_counts"] = np.asarray(
            family.counts, dtype=np.float32
        )
        inputs[f"{prefix}_enabled"] = np.asarray(
            family.enabled, dtype=np.bool_
        )
    return inputs


def frozen_normalization_to_config(
    normalization: typed.FrozenNormalization,
) -> dict[str, object]:
    """Convert a validated frozen normalization to a Keras-safe config.

    Parameters
    ----------
    normalization : typed_descriptors.FrozenNormalization
        Explicit normalization object. This function never fits statistics.

    Returns
    -------
    dict[str, object]
        JSON-compatible normalization config including schema and fit digests.
    """

    return {
        "schema_digest": normalization.schema_digest,
        "fit_inventory_row_selection_digest": (
            normalization.fit_inventory_row_selection_digest
        ),
        "fitting_policy": normalization.fitting_policy,
        "families": {
            contract.name: {
                "means": {
                    field_name: values.tolist()
                    for field_name, values in normalization.families[
                        contract.name
                    ].means.items()
                },
                "scales": {
                    field_name: values.tolist()
                    for field_name, values in normalization.families[
                        contract.name
                    ].scales.items()
                },
            }
            for contract in typed.FAMILY_CONTRACTS
        },
    }


def frozen_normalization_from_config(
    config: Mapping[str, object],
) -> typed.FrozenNormalization:
    """Recover and validate a frozen normalization from Keras config.

    Parameters
    ----------
    config : mapping
        Result of :func:`frozen_normalization_to_config`.

    Returns
    -------
    typed_descriptors.FrozenNormalization
        Recovered normalization bound to the current descriptor schema.
    """

    raw_families = config["families"]
    if not isinstance(raw_families, Mapping):
        raise ValueError("Normalization families config must be a mapping")
    families: dict[str, typed.FamilyNormalization] = {}
    for contract in typed.FAMILY_CONTRACTS:
        raw_family = raw_families[contract.name]
        if not isinstance(raw_family, Mapping):
            raise ValueError(f"{contract.name} normalization must be a mapping")
        raw_means = raw_family["means"]
        raw_scales = raw_family["scales"]
        if not isinstance(raw_means, Mapping) or not isinstance(
            raw_scales, Mapping
        ):
            raise ValueError(
                f"{contract.name} means and scales must be mappings"
            )
        families[contract.name] = typed.FamilyNormalization(
            means={
                str(name): np.asarray(values, dtype=np.float32)
                for name, values in raw_means.items()
            },
            scales={
                str(name): np.asarray(values, dtype=np.float32)
                for name, values in raw_scales.items()
            },
        )
    return typed.FrozenNormalization(
        schema_digest=str(config["schema_digest"]),
        fit_inventory_row_selection_digest=str(
            config["fit_inventory_row_selection_digest"]
        ),
        fitting_policy=str(config["fitting_policy"]),
        families=families,
    )


@cache
def _keras_types() -> tuple[Any, type[Any], type[Any]]:
    """Create and register the custom Keras types after lazy import."""

    tf = require_tensorflow()

    @tf.keras.utils.register_keras_serializable(
        package=KERAS_SERIALIZATION_PACKAGE
    )
    class KerasFamilyDeepSet(tf.keras.layers.Layer):
        """One family-specific token MLP followed by masked segment-sum pooling."""

        def __init__(
            self,
            family_name: str,
            normalization_config: Mapping[str, object],
            *,
            hidden_units: Sequence[int],
            token_embedding_dim: int,
            activation: str,
            **kwargs: object,
        ) -> None:
            super().__init__(**kwargs)
            if family_name not in typed.CONTRACT_BY_NAME:
                raise ValueError(f"Unknown typed family {family_name!r}")
            if token_embedding_dim < 1:
                raise ValueError("token_embedding_dim must be positive")
            if any(int(units) < 1 for units in hidden_units):
                raise ValueError("Every hidden layer width must be positive")
            self.family_name = family_name
            self.contract = typed.CONTRACT_BY_NAME[family_name]
            self.normalization_config = dict(normalization_config)
            normalization = frozen_normalization_from_config(
                self.normalization_config
            )
            self.family_normalization = normalization.families[family_name]
            self.hidden_units = tuple(int(units) for units in hidden_units)
            self.token_embedding_dim = int(token_embedding_dim)
            self.activation = str(activation)
            dense_layers = [
                tf.keras.layers.Dense(
                    units,
                    activation=self.activation,
                    name=f"{family_name}_token_dense_{index}",
                )
                for index, units in enumerate(self.hidden_units)
            ]
            dense_layers.append(
                tf.keras.layers.Dense(
                    self.token_embedding_dim,
                    activation=self.activation,
                    name=f"{family_name}_token_embedding",
                )
            )
            self.token_mlp = tf.keras.Sequential(
                dense_layers, name=f"{family_name}_token_mlp"
            )

        @property
        def contribution_width(self) -> int:
            """Return pooled token width plus the explicit count column."""

            return self.token_embedding_dim + 1

        def build(self, input_shape: Mapping[str, object]) -> None:
            self.token_mlp.build((None, self.contract.feature_width))
            super().build(input_shape)

        def prepare_features(
            self,
            values: Any,
            masks: Any,
            token_mask: Any,
        ) -> Any:
            """Apply frozen normalization, categories, and component masks."""

            values = tf.convert_to_tensor(values, dtype=tf.float32)
            masks = tf.convert_to_tensor(masks, dtype=tf.bool)
            token_mask = tf.convert_to_tensor(token_mask, dtype=tf.bool)
            tf.debugging.assert_all_finite(
                values, f"{self.family_name} raw values are non-finite"
            )
            tf.debugging.assert_equal(tf.shape(values), tf.shape(masks))
            tf.debugging.assert_equal(tf.shape(values)[0], tf.shape(token_mask)[0])

            prepared: list[Any] = []
            validity: list[Any] = []
            raw_offset = 0
            for field in self.contract.fields:
                field_values = values[:, raw_offset : raw_offset + field.width]
                field_masks = masks[:, raw_offset : raw_offset + field.width]
                field_masks = tf.logical_and(field_masks, token_mask[:, None])
                if field.kind == "continuous":
                    means = tf.constant(
                        self.family_normalization.means[field.name],
                        dtype=tf.float32,
                    )
                    scales = tf.constant(
                        self.family_normalization.scales[field.name],
                        dtype=tf.float32,
                    )
                    safe_values = tf.where(field_masks, field_values, means)
                    normalized = (safe_values - means) / scales
                    prepared.append(normalized)
                else:
                    categories = tf.constant(field.categories, dtype=tf.float32)
                    matches = tf.equal(field_values[..., None], categories)
                    unknown = tf.logical_not(
                        tf.reduce_any(matches, axis=-1, keepdims=True)
                    )
                    categorical = tf.concat([matches, unknown], axis=-1)
                    categorical = tf.logical_and(
                        categorical, field_masks[..., None]
                    )
                    prepared.append(
                        tf.reshape(
                            tf.cast(categorical, tf.float32),
                            (tf.shape(values)[0], -1),
                        )
                    )
                validity.append(tf.cast(field_masks, tf.float32))
                raw_offset += field.width
            features = tf.concat(prepared + validity, axis=1)
            return tf.ensure_shape(
                features, (None, self.contract.feature_width)
            )

        def call(
            self,
            inputs: Mapping[str, Any],
            training: bool | None = None,
        ) -> Any:
            features = self.prepare_features(
                inputs["values"], inputs["masks"], inputs["token_mask"]
            )
            segment_ids = tf.convert_to_tensor(
                inputs["segment_ids"], dtype=tf.int32
            )
            token_mask = tf.convert_to_tensor(inputs["token_mask"], dtype=tf.bool)
            counts = tf.convert_to_tensor(inputs["counts"], dtype=tf.float32)
            enabled = tf.convert_to_tensor(inputs["enabled"], dtype=tf.bool)
            row_count = tf.shape(counts)[0]
            tf.debugging.assert_equal(tf.shape(segment_ids)[0], tf.shape(features)[0])
            tf.debugging.assert_equal(tf.shape(enabled)[0], row_count)
            observed_counts = tf.math.unsorted_segment_sum(
                tf.cast(token_mask, tf.float32), segment_ids, row_count
            )
            tf.debugging.assert_equal(observed_counts, counts)

            projected = self.token_mlp(features, training=training)
            projected *= tf.cast(token_mask[:, None], projected.dtype)
            pooled = tf.math.unsorted_segment_sum(
                projected, segment_ids, row_count
            )
            contribution = tf.concat([pooled, counts[:, None]], axis=1)
            return contribution * tf.cast(enabled[:, None], contribution.dtype)

        def get_config(self) -> dict[str, object]:
            config = super().get_config()
            config.update(
                {
                    "family_name": self.family_name,
                    "normalization_config": self.normalization_config,
                    "hidden_units": list(self.hidden_units),
                    "token_embedding_dim": self.token_embedding_dim,
                    "activation": self.activation,
                }
            )
            return config

    @tf.keras.utils.register_keras_serializable(
        package=KERAS_SERIALIZATION_PACKAGE
    )
    class KerasTypedDescriptorAdapter(tf.keras.Model):
        """CPU-only detector-side Deep Sets adapter for all typed families."""

        def __init__(
            self,
            normalization_config: Mapping[str, object],
            *,
            hidden_units: Sequence[int] = (32, 32),
            token_embedding_dim: int = 16,
            activation: str = "relu",
            **kwargs: object,
        ) -> None:
            super().__init__(**kwargs)
            normalization = frozen_normalization_from_config(normalization_config)
            self.normalization_config = frozen_normalization_to_config(normalization)
            self.hidden_units = tuple(int(units) for units in hidden_units)
            self.token_embedding_dim = int(token_embedding_dim)
            self.activation = str(activation)
            self.family_encoders = {
                contract.name: KerasFamilyDeepSet(
                    contract.name,
                    self.normalization_config,
                    hidden_units=self.hidden_units,
                    token_embedding_dim=self.token_embedding_dim,
                    activation=self.activation,
                    name=f"{contract.name}_deep_set",
                )
                for contract in typed.FAMILY_CONTRACTS
            }

        @property
        def typed_embedding_width(self) -> int:
            """Return the concatenated width of all family contributions."""

            return sum(
                encoder.contribution_width
                for encoder in self.family_encoders.values()
            )

        def family_output_slice(self, family_name: str) -> slice:
            """Return one family's columns in the augmented detector output."""

            if family_name not in self.family_encoders:
                raise ValueError(f"Unknown typed family {family_name!r}")
            start = typed.DETECTOR_EVENT_WIDTH
            for contract in typed.FAMILY_CONTRACTS:
                width = self.family_encoders[contract.name].contribution_width
                if contract.name == family_name:
                    return slice(start, start + width)
                start += width
            raise AssertionError("Family contract ordering is inconsistent")

        def build(self, input_shape: Mapping[str, object]) -> None:
            with tf.device("/CPU:0"):
                for contract in typed.FAMILY_CONTRACTS:
                    prefix = contract.name
                    self.family_encoders[prefix].build(
                        {
                            "values": input_shape[f"{prefix}_values"],
                            "masks": input_shape[f"{prefix}_masks"],
                            "segment_ids": input_shape[f"{prefix}_segment_ids"],
                            "token_mask": input_shape[f"{prefix}_token_mask"],
                            "counts": input_shape[f"{prefix}_counts"],
                            "enabled": input_shape[f"{prefix}_enabled"],
                        }
                    )
            super().build(input_shape)

        def call(
            self,
            inputs: Mapping[str, Any],
            training: bool | None = None,
        ) -> Any:
            with tf.device("/CPU:0"):
                detector = tf.convert_to_tensor(
                    inputs[DETECTOR_INPUT_KEY], dtype=tf.float32
                )
                if detector.shape.rank != 2:
                    raise ValueError("Detector event block must be rank two")
                if detector.shape[-1] not in (
                    None,
                    typed.DETECTOR_EVENT_WIDTH,
                ):
                    raise ValueError(
                        "The typed adapter requires the 13-column detector event "
                        "block; the truth block is not augmented"
                    )
                detector = tf.ensure_shape(
                    detector, (None, typed.DETECTOR_EVENT_WIDTH)
                )
                tf.debugging.assert_all_finite(
                    detector, "Detector event block is non-finite"
                )
                row_count = tf.shape(detector)[0]
                contributions = []
                for contract in typed.FAMILY_CONTRACTS:
                    prefix = contract.name
                    contribution = self.family_encoders[prefix](
                        {
                            "values": inputs[f"{prefix}_values"],
                            "masks": inputs[f"{prefix}_masks"],
                            "segment_ids": inputs[f"{prefix}_segment_ids"],
                            "token_mask": inputs[f"{prefix}_token_mask"],
                            "counts": inputs[f"{prefix}_counts"],
                            "enabled": inputs[f"{prefix}_enabled"],
                        },
                        training=training,
                    )
                    tf.debugging.assert_equal(
                        tf.shape(contribution)[0], row_count
                    )
                    contributions.append(contribution)
                return tf.concat([detector] + contributions, axis=1)

        def get_config(self) -> dict[str, object]:
            config = super().get_config()
            config.update(
                {
                    "normalization_config": self.normalization_config,
                    "hidden_units": list(self.hidden_units),
                    "token_embedding_dim": self.token_embedding_dim,
                    "activation": self.activation,
                }
            )
            return config

    return tf, KerasFamilyDeepSet, KerasTypedDescriptorAdapter


def build_keras_typed_descriptor_adapter(
    normalization: typed.FrozenNormalization,
    *,
    hidden_units: Sequence[int] = (32, 32),
    token_embedding_dim: int = 16,
    activation: str = "relu",
    name: str = "typed_descriptor_deep_sets",
) -> Any:
    """Build an untrained CPU-only Keras Deep Sets adapter.

    Parameters
    ----------
    normalization : typed_descriptors.FrozenNormalization
        Explicit frozen statistics. The adapter exposes no fitting operation.
    hidden_units : sequence of int, optional
        Widths of the family-specific token MLP hidden layers.
    token_embedding_dim : int, optional
        Width of each projected token before segment-sum pooling.
    activation : str, optional
        Keras activation used by every token MLP layer.
    name : str, optional
        Keras model name.

    Returns
    -------
    tensorflow.keras.Model
        Untrained detector-side adapter. TensorFlow is imported by this call.
    """

    _, _, adapter_type = _keras_types()
    return adapter_type(
        frozen_normalization_to_config(normalization),
        hidden_units=hidden_units,
        token_embedding_dim=token_embedding_dim,
        activation=activation,
        name=name,
    )


def load_keras_typed_descriptor_adapter(path: str | Path) -> Any:
    """Load a natively serialized Keras typed-descriptor adapter.

    Parameters
    ----------
    path : str or pathlib.Path
        Existing Keras ``.keras`` archive.

    Returns
    -------
    tensorflow.keras.Model
        Recovered adapter with frozen normalization and trainable weights.
    """

    tf, _, _ = _keras_types()
    return tf.keras.models.load_model(Path(path))
