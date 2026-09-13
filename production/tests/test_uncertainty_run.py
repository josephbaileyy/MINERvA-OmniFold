"""Member orchestration with real cache IO and a no-fit calculation stand-in."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from production.minerva_production import cli, scalar, storage
from production.minerva_production.preparation import synthetic


@pytest.mark.parametrize(
    ("backend", "source", "mode"),
    [
        (backend, "statistical", mode)
        for backend in ("cached-lgbm-v1", "nominal-lgbm-v1")
        for mode in ("data-only", "data-plus-mc")
    ]
    + [("cached-lgbm-v1", "ml", None)],
)
def test_run_preserves_nominal_estimator_and_declared_perturbation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    backend: str,
    source: str,
    mode: str | None,
) -> None:
    path = tmp_path / "events.npz"
    synthetic(path, {"mode": "synthetic", "seed": 17, "events": 400})
    cfg = scalar.resolve_config(
        {
            "backend": backend,
            "features": ["pt", "pparallel"],
            "selection": "synthetic-cuts-v1",
            "background": "signal-only",
            "train_fraction": 0.8 if source == "ml" else 1.0,
        }
    )
    original, metadata = scalar.load_inputs(path, cfg)
    calls: list[tuple[dict[str, Any], dict[str, Any]]] = []

    def calculate(
        inputs: dict[str, Any], meta: dict[str, Any], config: dict[str, Any]
    ) -> dict[str, Any]:
        calls.append((copy.deepcopy(inputs), copy.deepcopy(config)))
        assert meta["output_contract"] == metadata["output_contract"]
        return {"xsec": np.arange(4, dtype=float) + len(calls)}

    monkeypatch.setattr(scalar, "calculate", calculate)
    args = argparse.Namespace(
        input=path,
        output=tmp_path / "nominal",
        nominal=tmp_path / "nominal",
        resume=False,
        action="run",
        source=source,
        mode=mode,
        seeds=[7, 8],
    )
    cli._unfold(args, cfg, "unfold_gbdt")
    args.output = tmp_path / "members"
    cli._uncertainties(args, cfg)
    assert len(calls) == 3
    for seed, (inputs, member_config) in zip(args.seeds, calls[1:]):
        assert member_config == ({**cfg, "split_seed": seed} if source == "ml" else cfg)
        for key in (
            "MCgen",
            "MCreco",
            "measured",
            "pass_truth",
            "pass_reco",
            "meas_pass_reco",
            "denom_nd",
            "flux",
            "data_pot",
            "n_nucleons",
        ):
            np.testing.assert_array_equal(inputs[key], original[key])
        data_factor = (
            np.random.default_rng(seed).poisson(1.0, len(original["measured"]))
            if source == "statistical"
            else 1
        )
        mc_factor = (
            np.random.default_rng(seed + 10_000_000).poisson(
                1.0, len(original["w_truth"])
            )
            if mode == "data-plus-mc"
            else 1
        )
        for key, factor in (
            ("measured_weights", data_factor),
            ("w_truth", mc_factor),
            ("w_reco", mc_factor),
        ):
            np.testing.assert_array_equal(inputs[key], original[key] * factor)
        _, record = storage.load_result(args.output / f"member_{seed}")
        assert record["resolved_member_config"] == member_config
    args.resume = True
    cli._uncertainties(args, cfg)
    assert len(calls) == 3
    args.input, args.output = args.output, tmp_path / "covariance"
    args.action = "combine"
    cli._uncertainties(args, cfg)
    arrays, record = storage.load_result(args.output)
    np.testing.assert_array_equal(arrays["covariance"], np.full((4, 4), 0.5))
    np.testing.assert_array_equal(arrays["mean_shift"], np.full(4, 1.5))
    assert record["covariance_contract"]["source"] == source
    assert record["covariance_contract"]["ensemble_size"] == 2
