"""Numerical equivalence and perturbation contracts on real LightGBM fits."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from production.minerva_production.preparation import synthetic
from production.minerva_production.scalar import (
    calculate,
    closure_inputs,
    load_inputs,
    resolve_config,
)
from production.minerva_production.storage import ROOT, legacy_module
from production.minerva_production.uncertainty import (
    statistical_inputs,
    training_config,
)

# Fixed before comparisons: deterministic CPU fits should agree to relative 1e-12.
# Zero absolute tolerance prevents tiny cross sections from passing vacuously.
RTOL = 1e-12


@pytest.fixture
def scalar_input(
    tmp_path: Path,
) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    path = tmp_path / "events.npz"
    synthetic(path, {"mode": "synthetic", "seed": 17, "events": 800})
    cfg = resolve_config(
        {
            "features": ["pt", "pparallel"],
            "selection": "synthetic-cuts-v1",
            "background": "signal-only",
            "iterations": 2,
        }
    )
    inputs, meta = load_inputs(path, cfg)
    return path, cfg, inputs, meta


def test_legacy_nominal_and_bootstrap_equivalence(
    scalar_input: Any, tmp_path: Path
) -> None:
    path, cfg, inputs, meta = scalar_input
    nominal = calculate(inputs, meta, cfg)
    assert np.ptp(nominal["push"]) > 0.01  # Real learned shape, not an all-ones fake.
    core = legacy_module("omnifold_nn_core")
    pull, push = core.omnifold_loop(
        inputs["MCgen"],
        inputs["MCreco"],
        inputs["measured"],
        inputs["pass_reco"],
        inputs["pass_truth"],
        inputs["meas_pass_reco"],
        2,
        "lgbm",
        MCgen_weights=inputs["w_truth"],
        MCreco_weights=inputs["w_reco"],
        measured_weights=inputs["measured_weights"],
        seed=42,
        verbose=False,
    )
    np.testing.assert_allclose(nominal["pull"], pull, rtol=RTOL, atol=0)
    np.testing.assert_allclose(nominal["push"], push, rtol=RTOL, atol=0)
    np.testing.assert_array_equal(
        nominal["truth_id"], inputs["truth_id"][inputs["pass_truth"]]
    )
    # The historical executable has no measured mask. Give both paths its exact
    # selected rows, keeping the same draw order and normalization inputs.
    selected = inputs["meas_pass_reco"]
    cached = {
        **inputs,
        "measured": inputs["measured"][selected],
        "measured_weights": inputs["measured_weights"][selected],
        "meas_pass_reco": np.ones(int(selected.sum()), bool),
    }
    edges = [np.array(axis["edges"]) for axis in meta["output_contract"]["axes"]]
    legacy_input = tmp_path / "legacy.npz"
    np.savez(legacy_input, **cached, nedges=2, edges_0=edges[0], edges_1=edges[1])
    old_output = tmp_path / "old.npz"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "nd-unfolding/bootstrap_nd.py"),
            "--npz",
            str(legacy_input),
            "--seed",
            "7",
            "--iters",
            "2",
            "--estimator-seed",
            "42",
            "--out",
            str(old_output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    varied = statistical_inputs(cached, seed=7, mode="data-plus-mc")
    new = calculate(varied, meta, cfg)
    with np.load(old_output) as old:
        np.testing.assert_allclose(new["xsec"], old["xsec_flat"], rtol=RTOL, atol=0)
        widths = np.outer(np.diff(edges[0]), np.diff(edges[1])).ravel()
        np.testing.assert_allclose(
            new["xsec"] @ widths, old["total_xsec"], rtol=RTOL, atol=0
        )
    # Independent intermediate histogram and normalization calculations.
    mask = varied["pass_truth"]
    prior = np.histogramdd(
        varied["MCgen"][mask], bins=edges, weights=varied["w_truth"][mask]
    )[0]
    unfolded = np.histogramdd(
        varied["MCgen"][mask], bins=edges, weights=varied["w_truth"][mask] * new["push"]
    )[0]
    completeness = prior / varied["denom_nd"]
    expected = (
        unfolded
        * 1e4
        / (
            completeness
            * varied["flux"][:, None]
            * float(varied["data_pot"])
            * float(varied["n_nucleons"])
            * widths.reshape(2, 2)
        )
    )
    for key, expected_array in (
        ("prior", prior),
        ("unfolded", unfolded),
        ("completeness", completeness),
        ("xsec", expected.ravel()),
    ):
        np.testing.assert_allclose(new[key], expected_array, rtol=RTOL, atol=0)
    assert path.exists()


def test_statistical_perturbations_keep_pairing_and_estimator(
    scalar_input: Any,
) -> None:
    _, cfg, inputs, _ = scalar_input
    snapshot = {key: value.copy() for key, value in inputs.items()}
    for mode in ("data-only", "data-plus-mc"):
        varied = statistical_inputs(inputs, seed=7, mode=mode)
        data_factors = np.random.default_rng(7).poisson(1.0, len(inputs["measured"]))
        np.testing.assert_array_equal(
            varied["measured_weights"], inputs["measured_weights"] * data_factors
        )
        if mode == "data-plus-mc":
            factors = np.random.default_rng(10000007).poisson(1.0, len(inputs["MCgen"]))
            for key in ("w_truth", "w_reco"):
                np.testing.assert_array_equal(varied[key], inputs[key] * factors)
        changed = {"measured_weights"} | (
            {"w_truth", "w_reco"} if mode == "data-plus-mc" else set()
        )
        for key in inputs.keys() - changed:
            assert varied[key] is inputs[key]
    for key in inputs:
        np.testing.assert_array_equal(inputs[key], snapshot[key])
    assert cfg["estimator_seed"] == 42
    assert cfg["seed_policy"] == "same-seed-for-both-classifiers-and-regressor"


def test_closure_uses_signal_rows_and_nominal_calculation(scalar_input: Any) -> None:
    _, cfg, inputs, meta = scalar_input
    pseudo, reference = closure_inputs(inputs, meta)
    mask = inputs["pass_reco"] & inputs["pass_truth"]
    np.testing.assert_array_equal(pseudo["measured"], inputs["MCreco"][mask])
    np.testing.assert_array_equal(pseudo["measured_weights"], inputs["w_reco"][mask])
    result = calculate(pseudo, meta, cfg)
    np.testing.assert_allclose(result["xsec"], reference["xsec"], rtol=RTOL, atol=0)


def test_training_split_is_a_separate_perturbation(scalar_input: Any) -> None:
    _, cfg, inputs, meta = scalar_input
    with pytest.raises(ValueError, match="nominal train_fraction"):
        training_config(cfg, 3)
    split_cfg = {**cfg, "train_fraction": 0.8}
    changed = training_config(split_cfg, 3)
    assert {key for key in changed if changed[key] != split_cfg[key]} == {"split_seed"}
    first = calculate(inputs, meta, split_cfg)
    second = calculate(inputs, meta, changed)
    assert not np.array_equal(first["push"], second["push"])


@pytest.mark.parametrize(
    "damage", ["identity", "mask", "weight", "flux", "units", "support"]
)
def test_input_contract_rejects_mismatch(
    scalar_input: Any, tmp_path: Path, damage: str
) -> None:
    _, cfg, inputs, meta = scalar_input
    if damage == "identity":
        inputs["reco_id"] = inputs["reco_id"][::-1]
    elif damage == "mask":
        inputs["pass_truth"] = inputs["pass_truth"].astype(int)
    elif damage == "weight":
        inputs["w_truth"][0] = -1
    elif damage == "flux":
        inputs["flux"][0] = 0
    elif damage == "units":
        meta.pop("normalization_units")
    else:
        meta["output_contract"].pop("support")
    path = tmp_path / "bad.npz"
    np.savez(path, **inputs, metadata=json.dumps(meta))
    with pytest.raises(ValueError):
        load_inputs(path, cfg)


def test_help_needs_no_optional_runtime(tmp_path: Path) -> None:
    # -S removes site packages entirely: even numpy is unavailable.
    for name in (
        "prepare_events",
        "unfold_gbdt.py",
        "unfold_pet.py",
        "uncertainties.py",
        "closure.py",
        "project.py",
    ):
        result = subprocess.run(
            [sys.executable, "-S", str(ROOT / "production" / name), "--help"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "--config" in result.stdout and "--plan" in result.stdout


def test_imports_resolve_this_checkout_from_foreign_directory(tmp_path: Path) -> None:
    program = "from minerva_production.storage import ROOT, legacy_module; print(ROOT); print(legacy_module('omnifold_nn_core').__file__)"
    result = subprocess.run(
        [sys.executable, "-c", program],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(ROOT / "production")},
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.splitlines() == [
        str(ROOT),
        str(ROOT / "nd-unfolding/omnifold_nn_core.py"),
    ]
