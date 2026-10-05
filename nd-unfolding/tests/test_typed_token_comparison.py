"""Synthetic invariants for the isolated pooled/direct attention comparison."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pet"))
import typed_descriptor_keras as adapter  # noqa: E402
import typed_descriptors as typed  # noqa: E402
import typed_token_comparison as comparison  # noqa: E402
from test_typed_descriptors import _synthetic_fixture  # noqa: E402


@pytest.fixture
def paired() -> Any:
    tf = adapter.require_tensorflow()
    tf.config.set_visible_devices([], "GPU")
    tf.keras.utils.set_random_seed(17)
    batch, generic, event, _ = _synthetic_fixture()
    norm = typed.fit_frozen_normalization_for_smoke(
        batch, fit_inventory_row_selection_digest="e" * 64
    )
    inputs = adapter.prepare_keras_inputs(batch, event)
    inputs.update(generic_values=generic, generic_mask=np.ones((3, 12), bool))
    models = [
        comparison.build_comparison(norm, routing=route)
        for route in ("pooled", "direct")
    ]
    for model in models:
        model(inputs)
    models[1].set_weights(models[0].get_weights())
    return tf, inputs, models, norm


def test_parameter_footing_and_reference_pool(paired: Any) -> None:
    _, inputs, (pooled, direct), norm = paired
    assert pooled.count_params() == direct.count_params()
    for left, right in zip(pooled.get_weights(), direct.get_weights()):
        np.testing.assert_array_equal(left, right)
    cloud, mask, counts = direct.route_tokens(inputs)
    assert np.sum(mask.numpy()[2]) == 98
    reference = adapter.build_keras_typed_descriptor_adapter(norm)
    reference(inputs)
    for target, source in zip(reference.family_encoders.values(), pooled.encoders):
        target.set_weights(source.get_weights())
    expected = reference(inputs).numpy()[:, 13:]
    summaries, _, count = pooled.route_tokens(inputs)
    actual = np.concatenate(
        [np.concatenate([summaries[:, i], count[:, i : i + 1]], 1) for i in range(3)], 1
    )
    np.testing.assert_allclose(actual, expected, atol=1e-6)
    assert cloud.shape[1] >= 90


@pytest.mark.parametrize("route", [0, 1])
def test_permutation_masking_batch_isolation(paired: Any, route: int) -> None:
    _, inputs, models, _ = paired
    model = models[route]
    expected = model(inputs).numpy()
    changed = {key: value.copy() for key, value in inputs.items()}
    for family in typed.FAMILY_CONTRACTS:
        prefix = family.name
        segment = changed[f"{prefix}_segment_ids"]
        order = np.concatenate(
            [np.flatnonzero(segment == row)[::-1] for row in range(3)]
        )
        for suffix in ("values", "masks", "segment_ids", "token_mask"):
            key = f"{prefix}_{suffix}"
            changed[key] = changed[key][order]
        changed[f"{prefix}_values"][~changed[f"{prefix}_masks"]] = 123456.0
    np.testing.assert_allclose(model(changed), expected, rtol=1e-5, atol=1e-5)
    changed[adapter.DETECTOR_INPUT_KEY][2] += 100.0
    np.testing.assert_allclose(model(changed).numpy()[:2], expected[:2], atol=1e-5)


def test_disabled_empty_and_gradient(paired: Any) -> None:
    tf, inputs, models, _ = paired
    disabled = {key: value.copy() for key, value in inputs.items()}
    for family in typed.FAMILY_CONTRACTS:
        disabled[f"{family.name}_enabled"][:] = False
    np.testing.assert_allclose(models[0](disabled), models[1](disabled), atol=2e-6)
    for model in models:
        with tf.GradientTape() as tape:
            loss = tf.reduce_sum(model(inputs) ** 2)
        gradients = tape.gradient(loss, model.trainable_variables)
        assert all(g is not None and np.all(np.isfinite(g)) for g in gradients)
        for encoder in model.encoders:
            indices = [
                i
                for i, variable in enumerate(model.trainable_variables)
                if any(variable is v for v in encoder.trainable_variables)
            ]
            assert any(np.any(gradients[i].numpy() != 0) for i in indices)


@pytest.mark.parametrize("route", [0, 1])
def test_serialization_and_graph(paired: Any, route: int, tmp_path: Path) -> None:
    tf, inputs, models, _ = paired
    model = models[route]
    expected = model(inputs)
    np.testing.assert_allclose(tf.function(model)(inputs), expected, atol=1e-5)
    path = tmp_path / "comparison.keras"
    model.save(path)
    restored = tf.keras.models.load_model(path)
    np.testing.assert_allclose(restored(inputs), expected, atol=1e-6)
    config = model.get_config()
    config["normalization_config"]["schema_digest"] = "0" * 64
    with pytest.raises(ValueError):
        comparison.comparison_model_type().from_config(config)


def test_padding_is_not_kinematics(paired: Any) -> None:
    _, inputs, models, _ = paired
    changed = {key: value.copy() for key, value in inputs.items()}
    changed["generic_mask"][:, -1] = False
    for model in models:
        expected = model(changed)
        changed["generic_values"][:, -1] = np.nan
        np.testing.assert_allclose(model(changed), expected, atol=1e-6)
        # Zero is a valid measured feature, not evidence of absent objects.
        changed["generic_values"][:, 0] = 0.0
        assert np.all(np.isfinite(model(changed)))


def test_weighted_odds_have_correct_prior() -> None:
    from run_typed_token_comparison import train_ratio, predict_ratio

    tf = adapter.require_tensorflow()
    features = np.zeros((8, 2), np.float32)
    model = tf.keras.Sequential([tf.keras.layers.Input((2,)), tf.keras.layers.Dense(1)])
    model.set_weights(
        [np.zeros((2, 1), np.float32), np.asarray([np.log(2.0)], np.float32)]
    )
    train_ratio(
        model,
        features,
        np.ones(8, np.float32),
        np.full(8, 2, np.float32),
        epochs=1,
        batch_size=8,
        seed=17,
        packed=False,
    )
    np.testing.assert_allclose(
        predict_ratio(model, features, packed=False, batch_size=8), 2.0, rtol=1e-5
    )


def test_complete_matrix_required(tmp_path: Path) -> None:
    import importlib.util

    path = (
        Path(__file__).resolve().parents[1]
        / "pet/direct_token_comparison/summarize_runs.py"
    )
    spec = importlib.util.spec_from_file_location("comparison_summary", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(FileNotFoundError):
        module.summarize(tmp_path)


def test_fresh_process_reload(paired: Any, tmp_path: Path) -> None:
    import subprocess

    tf, inputs, models, _ = paired
    path = tmp_path / "direct.keras"
    inputs_path = tmp_path / "inputs.npz"
    prediction_path = tmp_path / "prediction.npy"
    models[1].save(path)
    np.savez(inputs_path, **inputs)
    source = (
        "import sys,numpy as np; "
        "sys.path.insert(0,sys.argv[1]); "
        "from typed_token_comparison import comparison_model_type; "
        "comparison_model_type(); import tensorflow as tf; "
        "model=tf.keras.models.load_model(sys.argv[2]); "
        "inputs=dict(np.load(sys.argv[3])); "
        "np.save(sys.argv[4],model(inputs).numpy())"
    )
    subprocess.run(
        [
            sys.executable,
            "-c",
            source,
            str(Path(__file__).resolve().parents[1] / "pet"),
            str(path),
            str(inputs_path),
            str(prediction_path),
        ],
        check=True,
    )
    np.testing.assert_allclose(np.load(prediction_path), models[1](inputs), atol=1e-6)
