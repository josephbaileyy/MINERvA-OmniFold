"""Local controls for truth semantics, recovery readings and admission arithmetic."""

from __future__ import annotations

import importlib.util
import sys

import numpy as np
import pytest

import ibukt as core
import run_ibukt as runner


@pytest.fixture
def cfg():
    return core.configuration()


def test_root_edges_and_axis_order(cfg):
    got = core.cells(
        np.array([0, 0.07, 4.5, 1.0, np.nan]), np.array([1.5, 2.0, 3.0, 60.0, 4.0]), cfg
    )
    assert got.tolist() == [0, 17, -1, -1, -1]


def test_opposite_within_bin_truths_preserve_counts_but_change_efficiency(cfg):
    pt = np.array([0.08, 0.14, 0.08, 0.14])
    pz = np.full(4, 4.2)
    weights = np.array([1.0, 3.0, 2.0, 4.0])
    means = core.moments(pt, pz, weights, cfg)
    plus = core.truth_factor("within_plus", pt, pz, means, cfg, {})
    minus = core.truth_factor("within_minus", pt, pz, means, cfg, {})
    np.testing.assert_allclose(plus + minus, 2)
    np.testing.assert_allclose(
        core.histogram(pt, pz, weights * plus, cfg),
        core.histogram(pt, pz, weights, cfg),
    )
    efficiency = np.array([0.2, 0.8, 0.2, 0.8])
    assert np.sum(weights * plus * efficiency) > np.sum(weights * efficiency)
    # A one-bin IBU response retains its nominal efficiency and over-recovers.
    inferred = np.sum(weights * plus * efficiency) / (
        np.sum(weights * efficiency) / weights.sum()
    )
    assert inferred > weights.sum()


def test_means_use_full_truth_weights_not_reco_weights(cfg):
    pt, pz = np.array([0.08, 0.14]), np.array([4.0, 4.0])
    full = np.array([1.0, 9.0])
    correct = core.moments(pt, pz, full, cfg)
    wrong = core.moments(pt, pz, np.ones(2), cfg)
    index = core.cells(pt, pz, cfg)[0]
    assert correct[index] != wrong[index]
    f = core.truth_factor("within_plus", pt, pz, wrong, cfg, {})
    assert not np.isclose(np.sum(full * f), full.sum())


def test_poisson_is_shared_reproducible_and_does_not_resample_template():
    features = np.arange(8.0).reshape(4, 2)
    signed = np.array([20.0, 5.0, -5.0, 0.0])
    first = core.poisson_target(features, signed, 771001)
    second = core.poisson_target(features, signed, 771001)
    for a, b in zip(first, second):
        np.testing.assert_array_equal(a, b)
    np.testing.assert_array_equal(first[0][-1], features[2])
    assert first[1][-1] == -5
    assert np.all(first[1][:-1] == 1)
    assert not np.shares_memory(first[1], signed)


def test_recovery_reading_fires_on_planted_cell_and_keeps_sign():
    truth = np.array([10.0, 20.0, 30.0])
    estimates = truth * np.tile([1.0, 1.03, 0.96], (5, 1))
    got = core.recoveries(estimates, truth, truth)
    assert got["reading"] == [
        "within tolerance",
        "outside tolerance",
        "outside tolerance",
    ]
    assert got["mean"][2] < 0


def test_large_sampling_noise_is_unresolved():
    estimates = np.array([[0.9], [1.1], [0.9], [1.1], [1.0]])
    assert core.recoveries(estimates, np.ones(1), np.ones(1))["reading"] == [
        "unresolved"
    ]


@pytest.mark.parametrize("count", [0, 4, 6])
def test_partial_or_extra_ensemble_refused(count):
    with pytest.raises(ValueError):
        core.recoveries(np.ones((count, 1)), np.ones(1), np.ones(1))


def test_zero_truth_and_nonfinite_refused():
    with pytest.raises(ValueError):
        core.recoveries(np.ones((5, 1)), np.zeros(1), np.ones(1))
    with pytest.raises(ValueError):
        runner.require_close(np.array([np.nan]), np.ones(1), "plant")


def test_identity_detects_shape_and_scale_errors():
    expected = np.array([1e-38, 2e-38, 3e-38])
    assert runner.require_close(expected, expected, "same") == 0
    for actual in (expected * 1.01, expected[::-1], expected[:2]):
        with pytest.raises(ValueError):
            runner.require_close(actual, expected, "plant")


def test_budget_counts_failures_active_and_scheduler_lag():
    rows = "1|ibukt-env|FAILED|180|1\n2|ibukt-screen|RUNNING|60|1\n"
    got = core.budget(rows, {"1": 0.3, "2": 5.0, "3": 0.1}, 0.5)
    assert got["total"] == pytest.approx(5.65)
    with pytest.raises(ValueError):
        core.budget(rows, {"1": 0.3, "2": 5.0, "3": 0.1}, 0.8)


@pytest.mark.parametrize(
    "rows",
    [
        "9|ibukt-other|COMPLETED|1|1",
        "1|ibukt-env|FAILED|NaN|1",
        "1|ibukt-env|RUNNING|1|2",
    ],
)
def test_unpriceable_budget_refused(rows):
    with pytest.raises(ValueError):
        core.budget(rows, {"1": 0.3}, 0.1)


def test_duplicate_attempt_refused():
    line = "1|ibukt-env|COMPLETED|1|1\n"
    with pytest.raises(ValueError):
        core.budget(line * 2, {"1": 0.3}, 0.1)


def test_declared_grid_matches_driver_ast(cfg):
    import ast

    tree = ast.parse((runner.REPO / "2d-unfolding/re2/re2_driver.py").read_text())
    for symbol, key in [("PT_EDGES", "pt_edges"), ("PZ_EDGES", "pz_edges")]:
        value = next(
            ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == symbol for t in node.targets)
        )
        assert value == cfg[key]


def test_exact_ibu_known_nontrivial_truth(cfg):
    path = runner.REPO / "2d-unfolding/ref_c2c1/ref_c2c1.py"
    spec = importlib.util.spec_from_file_location("ibukt_test_comparison", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    prior = np.array([10.0, 20.0])
    matrix = np.diag([5.0, 15.0])
    truth = np.array([12.0, 16.0])
    measured = (matrix / prior) @ truth
    result = module.dagostini(matrix, prior, measured, [5])
    np.testing.assert_allclose(result[5], truth)


@pytest.fixture
def portable_io(monkeypatch):
    """Use local reads only in synthetic tests; production still requires noatime."""
    import hashlib
    import json

    monkeypatch.setattr(
        runner, "digest", lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    )
    monkeypatch.setattr(runner, "read_json", lambda path: json.loads(path.read_text()))

    def read_npz(path):
        with np.load(path, allow_pickle=False) as data:
            return {key: data[key] for key in data.files}

    monkeypatch.setattr(runner, "read_npz", read_npz)


def test_pair_shares_exact_refined_target_and_preserves_response(
    cfg, tmp_path, monkeypatch, portable_io
):
    from argparse import Namespace
    from types import SimpleNamespace

    gen = np.array([[0.08, 4.2], [0.14, 4.2]])
    weights = np.array([10.0, 30.0])
    nominal = core.histogram(gen[:, 0], gen[:, 1], weights, cfg)
    bank = dict(
        gen=gen,
        reco=gen.copy(),
        pt=np.ones(2, bool),
        pr=np.array([True, False]),
        wt=weights,
        wr=np.array([10.0, 0.0]),
        bkg=gen[:1],
        bw=np.array([2.0]),
        means=core.moments(gen[:, 0], gen[:, 1], weights, cfg),
        factor=np.ones(224),
        selected=np.flatnonzero(nominal),
        truth_nominal=nominal,
        truth_within_plus=nominal,
    )
    bank_path = tmp_path / "bank.npz"
    np.savez(bank_path, **bank)
    identity = tmp_path / "identity.json"
    runner.write_json(
        identity,
        dict(
            status="PASS",
            bank_sha256=runner.digest(bank_path),
            config_sha256=runner.digest(core.CONFIG),
        ),
    )
    observed = {}

    def refine(features, signed, **kwargs):
        observed["features"] = features
        observed["refined"] = np.abs(signed) * 0.75
        return observed["refined"], None, 0.0

    def binned(gen_in, reco, measured, pr, pt, wt, wr, refined, *edges):
        assert measured is observed["features"]
        assert refined is observed["refined"]
        np.testing.assert_array_equal(wt, weights)
        np.testing.assert_array_equal(gen_in, gen)
        return nominal, np.eye(224), nominal, None

    def omnifold(gen_in, reco, measured, pr, pt, pm, iterations, **kwargs):
        assert measured is observed["features"]
        assert kwargs["measured_weights"] is observed["refined"]
        assert iterations == 5
        assert kwargs["classifier1_params"] == {"random_state": 42}
        np.testing.assert_array_equal(kwargs["MCgen_weights"], weights)
        return None, np.ones(2)

    comparison = SimpleNamespace(
        binned_problem=binned, roounfold_bayes=lambda *args: {5: nominal, 10: nominal}
    )
    monkeypatch.setattr(
        runner,
        "dependencies",
        lambda: (
            comparison,
            SimpleNamespace(refine_stay_positive=refine),
            SimpleNamespace(omnifold=omnifold),
        ),
    )
    monkeypatch.setattr(runner, "ratios", lambda cfg: {})
    out = tmp_path / "out"
    out.mkdir()
    runner.pair(
        Namespace(
            identity=identity,
            bank=bank_path,
            truth="within_plus",
            trial=0,
            out=out,
            stage=tmp_path,
        ),
        cfg,
    )
    data = runner.read_npz(out / "pair.npz")
    np.testing.assert_array_equal(data["truth"], nominal)
    np.testing.assert_array_equal(data["omnifold"], nominal)
    np.testing.assert_array_equal(runner.read_npz(bank_path)["wt"], weights)


def test_score_requires_complete_consistent_digest_bound_pairs(
    cfg, tmp_path, portable_io
):
    from argparse import Namespace

    products = tmp_path / "products"
    products.mkdir()
    for name in cfg["truths"]:
        for trial in range(5):
            directory = products / f"{name}-{trial}"
            directory.mkdir()
            np.savez(
                directory / "pair.npz",
                truth=np.ones(2),
                prior=np.ones(2),
                selected=np.arange(2),
                omnifold=np.array([1, 1.04]),
                ibu5=np.array([0.96, 1]),
                ibu10=np.ones(2),
            )
            runner.write_json(
                directory / "pair.json",
                dict(
                    status="PASS",
                    truth=name,
                    trial=trial,
                    seed=cfg["seeds"][trial],
                    config_sha256=runner.digest(core.CONFIG),
                    bank_sha256="one-bank",
                    product_sha256=runner.digest(directory / "pair.npz"),
                ),
            )
    out = tmp_path / "out"
    out.mkdir()
    args = Namespace(products=products, out=out)
    runner.score(args, cfg)
    result = runner.read_json(out / "readout.json")
    assert len(result["truths"]) == 7
    assert result["truths"]["nominal"]["omnifold"]["reading"] == [
        "within tolerance",
        "outside tolerance",
    ]
    assert result["truths"]["nominal"]["ibu5"]["reading"] == [
        "outside tolerance",
        "within tolerance",
    ]
    # A receipt cannot relabel a changed product as a completed pair.
    product = products / "within_minus-4" / "pair.npz"
    product.write_bytes(product.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="digest differs"):
        runner.score(args, cfg)
    product.unlink()
    with pytest.raises(FileNotFoundError):
        runner.score(args, cfg)


def test_missing_generator_map_is_not_a_within_bin_truth(cfg):
    with pytest.raises(ValueError, match="missing generator ratio"):
        core.truth_factor(
            "nuwro", np.array([0.1]), np.array([4.0]), np.zeros(224), cfg, {}
        )


def test_nonpositive_prior_refused():
    with pytest.raises(ValueError):
        core.recoveries(np.ones((5, 1)), np.ones(1), np.zeros(1))


def test_launcher_refuses_non_scratch_paths_before_writing(tmp_path):
    import os
    import subprocess

    product = tmp_path / "must-not-exist"
    environment = dict(
        os.environ,
        IBUKT_DEPLOY=str(tmp_path),
        IBUKT_STAGE=str(tmp_path),
        IBUKT_PREPARE=str(tmp_path),
        IBUKT_PRODUCTS=str(product),
        IBUKT_PYTHON=sys.executable,
        IBUKT_DEPLOY_SHA="unused",
    )
    result = subprocess.run(
        ["bash", str(runner.REPO / "2d-unfolding/ibukt/screen.sbatch")],
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "must resolve under /pscratch" in result.stderr
    assert not product.exists()
