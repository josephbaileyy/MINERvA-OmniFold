"""No-fit checks of estimator dispatch, masks, seeds and closure extraction."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

from production.minerva_production import scalar
from production.minerva_production.preparation import synthetic
from production.minerva_production.storage import legacy_module
from production.minerva_production.uncertainty import (
    statistical_inputs,
    training_config,
)


def config(backend: str = "nominal-lgbm-v1", **extra: Any) -> dict[str, Any]:
    return scalar.resolve_config(
        {
            "backend": backend,
            "features": ["pt", "pparallel"],
            "selection": "synthetic-cuts-v1",
            "background": "signal-only",
            **extra,
        }
    )


@pytest.fixture
def inputs(tmp_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    path = tmp_path / "events.npz"
    synthetic(path, {"mode": "synthetic", "seed": 17, "events": 400})
    return scalar.load_inputs(path, config())


def test_nominal_policy_and_resolved_parameters() -> None:
    cfg = config()
    parameters = scalar.estimator_parameters(cfg)
    assert [
        parameters[name]["random_state"]
        for name in ("classifier1", "classifier2", "regressor")
    ] == [42, 43, 44]
    for model in parameters.values():
        assert {key: model[key] for key in scalar.MODEL} == scalar.MODEL
    cached = scalar.estimator_parameters(config("cached-lgbm-v1"))
    assert [model["random_state"] for model in cached.values()] == [42, 42, 42]
    with pytest.raises(ValueError, match="seed_policy"):
        config(seed_policy=scalar.SEED_POLICIES["cached-lgbm-v1"])
    with pytest.raises(ValueError, match="no split"):
        config(train_fraction=0.8)
    with pytest.raises(ValueError, match="train_fraction"):
        training_config(cfg, 7)


@pytest.mark.parametrize("backend", ["nominal-lgbm-v1", "cached-lgbm-v1"])
def test_nominal_and_replica_use_the_selected_engine(
    backend: str,
    inputs: tuple[dict[str, Any], dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arrays, metadata = inputs
    calls = []

    def engine(*args: Any, **kwargs: Any) -> tuple[np.ndarray, np.ndarray]:
        calls.append((args, kwargs))
        count = int(args[4].sum())
        return np.ones(count), np.ones(count)

    def module(name: str) -> Any:
        if name == "nominal_omnifold":
            assert backend == "nominal-lgbm-v1"
            return SimpleNamespace(
                OmniFold_helper_functions=SimpleNamespace(omnifold=engine)
            )
        if name == "omnifold_nn_core":
            assert backend == "cached-lgbm-v1"
            return SimpleNamespace(omnifold_loop=engine)
        return legacy_module(name)

    monkeypatch.setattr(scalar, "legacy_module", module)
    cfg = config(backend)
    nominal = scalar.calculate(arrays, metadata, cfg)
    replica_inputs = statistical_inputs(arrays, seed=7, mode="data-plus-mc")
    scalar.calculate(replica_inputs, metadata, cfg)
    assert len(calls) == 2
    for (args, kwargs), supplied in zip(calls, (arrays, replica_inputs)):
        for actual, name in zip(
            args[:6],
            (
                "MCgen",
                "MCreco",
                "measured",
                "pass_reco",
                "pass_truth",
                "meas_pass_reco",
            ),
        ):
            np.testing.assert_array_equal(actual, supplied[name])
        assert args[6] == cfg["iterations"]
        for passed, name in (
            ("MCgen_weights", "w_truth"),
            ("MCreco_weights", "w_reco"),
            ("measured_weights", "measured_weights"),
        ):
            np.testing.assert_array_equal(kwargs[passed], supplied[name])
        if backend == "nominal-lgbm-v1":
            assert kwargs["classifier1_params"] == {"random_state": 42}
            assert kwargs["classifier2_params"] == {"random_state": 43}
            assert kwargs["regressor_params"] == {"random_state": 44}
            assert kwargs["estimator"] == "lgbm" and kwargs["device"] == "cpu"
            assert kwargs["parameter_format"] == "dict"
        else:
            assert kwargs["seed"] == 42 and kwargs["kind"] == "lgbm"
    np.testing.assert_array_equal(nominal["prior"], nominal["unfolded"])


def test_nominal_closure_uses_unity_completeness_and_signal_reco(
    inputs: tuple[dict[str, Any], dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arrays, metadata = inputs
    metadata = {**metadata, "background": "preweighted-purity"}
    cfg = config(background="preweighted-purity")
    pseudo, reference = scalar.closure_inputs(arrays, metadata, cfg)
    selected = arrays["pass_truth"] & arrays["pass_reco"]
    np.testing.assert_array_equal(pseudo["measured"], arrays["MCreco"][selected])
    np.testing.assert_array_equal(
        pseudo["measured_weights"], arrays["w_reco"][selected]
    )

    def engine(*args: Any, **kwargs: Any) -> tuple[np.ndarray, np.ndarray]:
        count = int(args[4].sum())
        return np.ones(count), np.ones(count)

    monkeypatch.setattr(
        scalar,
        "legacy_module",
        lambda name: (
            SimpleNamespace(OmniFold_helper_functions=SimpleNamespace(omnifold=engine))
            if name == "nominal_omnifold"
            else legacy_module(name)
        ),
    )
    result = scalar.calculate(pseudo, metadata, cfg, closure=True)
    np.testing.assert_array_equal(result["completeness"], np.ones_like(result["prior"]))
    np.testing.assert_array_equal(result["xsec"], reference["xsec"])
    nonclosure = scalar.calculate(arrays, metadata, cfg)
    np.testing.assert_allclose(nonclosure["completeness"], 0.9, rtol=1e-14)


def test_nominal_loader_requires_real_root_when_unavailable() -> None:
    import importlib.util

    if importlib.util.find_spec("ROOT") is not None:
        pytest.skip("ROOT is installed; absence test is inapplicable")
    with pytest.raises(ModuleNotFoundError, match="ROOT"):
        legacy_module("nominal_omnifold")


@pytest.mark.parametrize("denominator_empty", [False, True])
def test_empty_resampled_bin_keeps_nominal_support(
    inputs: tuple[dict[str, Any], dict[str, Any]],
    denominator_empty: bool,
) -> None:
    arrays, metadata = inputs
    selected = arrays["pass_truth"]
    weights = arrays["w_truth"].copy()
    weights[(arrays["MCgen"][:, 0] < 1) & (arrays["MCgen"][:, 1] < 2)] = 0
    denominator = arrays["denom_nd"].copy()
    if denominator_empty:
        denominator.flat[0] = 0
    result = scalar.extract(
        {**arrays, "w_truth": weights, "denom_nd": denominator},
        metadata,
        np.ones(int(selected.sum())),
    )
    assert result["xsec"][0] == 0
    assert result["empty_supported_bins"][0]
    assert len(result["xsec"]) == sum(metadata["output_contract"]["support"])
