"""Local controls for truth semantics, recovery readings and admission arithmetic."""

from __future__ import annotations

import importlib.util
import sys
from types import SimpleNamespace
from unittest.mock import Mock

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


@pytest.mark.parametrize("reported_count", [204, 205])
def test_prepare_mask_matches_legacy_covariance_conversion(
    tmp_path, monkeypatch, reported_count
):
    # The IBUKT declaration defines 205 positive-diagonal cells from paper.root.
    unreported = np.arange(1, 200, 11)
    expected = np.delete(np.arange(224), unreported)[:reported_count]
    diagonal = np.full(224, -1.0)
    diagonal[unreported] = 0.0
    diagonal[expected] = 2.0
    dense = np.full((224, 224), 9.0)
    np.fill_diagonal(dense, diagonal)
    legacy = np.flatnonzero(np.diag(dense) > 0)
    np.testing.assert_array_equal(legacy, expected)
    covariance = Mock(side_effect=lambda row, col: dense[row, col])
    covariance.GetNrows.return_value = 224
    covariance.GetNcols.return_value = 224
    source = Mock()
    source.IsZombie.return_value = False
    source.Get.return_value = covariance
    root = SimpleNamespace(TFile=SimpleNamespace(Open=Mock(return_value=source)))
    monkeypatch.setitem(sys.modules, "ROOT", root)
    monkeypatch.setitem(sys.modules, "compare_to_paper_fullcov", None)

    path = tmp_path / "paper.root"
    if reported_count == 205:
        np.testing.assert_array_equal(runner._reporting_cells(path), legacy)
    else:
        with pytest.raises(ValueError, match="exactly 205 cells"):
            runner._reporting_cells(path)
    source.Get.assert_called_once_with("StatOnlyCovariance")
    source.Close.assert_called_once_with()


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
        core.budget(rows, {"1": 0.3, "2": 5.0, "3": 0.1}, 1.4)


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


def synthetic_admissibility(path, bank, cfg, **targets):
    from types import SimpleNamespace

    expected = {
        key: core.target_digest(np.zeros(224)) for _, _, key in runner.target_keys(cfg)
    }
    expected.update({key: core.target_digest(value) for key, value in targets.items()})
    runner.write_json(
        path,
        {
            "status": "PASS",
            "bank_sha256": runner.digest(bank),
            "config_sha256": runner.digest(core.CONFIG),
            "target_treatments": cfg["target_treatments"],
            "targets": expected,
            "signed_identity": {
                "checks": dict.fromkeys(
                    (
                        "row_sum",
                        "roo_K5",
                        "roo_K10",
                        "numpy_K5",
                        "numpy_K10",
                        "agreement_K5",
                        "agreement_K10",
                    ),
                    0.0,
                ),
                "truth_indices": [],
                "reco_indices": [],
            },
        },
    )
    return SimpleNamespace(
        path=path,
        fields=lambda key: {
            "admissibility_sha256": runner.digest(path),
            "target_treatments": cfg["target_treatments"],
            "signed_target_sha256": expected[key],
        },
    )


def test_pair_uses_signed_target_and_preserves_refinement_for_omnifold(
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
        ibu_prior=nominal,
        ibu_response=np.eye(224),
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
    control_dir = tmp_path / "control"
    control_dir.mkdir()
    np.savez(
        control_dir / "pair.npz",
        omnifold=nominal,
        ibu5=nominal,
        truth=nominal,
        selected=bank["selected"],
    )
    from unittest.mock import patch

    with patch.object(runner, "ratios", return_value={}):
        _, _, target = runner.draw_target(bank, cfg, {}, "within_plus", 0)
    admission = synthetic_admissibility(
        tmp_path / "admissibility.json", bank_path, cfg, **{"within_plus-0": target}
    )
    runner.write_json(
        control_dir / "pair.json",
        dict(
            **admission.fields("nominal-control"),
            status="PASS",
            truth="nominal",
            sampling="noise-free",
            nominal_tolerance=core.RECOVERY_TOLERANCE,
            config_sha256=runner.digest(core.CONFIG),
            bank_sha256=runner.digest(bank_path),
            product_sha256=runner.digest(control_dir / "pair.npz"),
        ),
    )
    observed = {}
    original_poisson = core.poisson_target

    def poisson(features, signed, seed):
        # r(first row)=1 + 0.5*(0.125 - 0.6875); second signal row is missed.
        np.testing.assert_allclose(signed, [10 * 0.71875, 2, -2])
        assert seed == 771001
        observed["poisson_checked"] = True
        return original_poisson(features, signed, seed)

    monkeypatch.setattr(core, "poisson_target", poisson)

    def refine(features, signed, **kwargs):
        assert kwargs == {
            "estimator": "lgbm",
            "device": "cpu",
            "params": {"random_state": 45, "n_estimators": 400, "num_leaves": 31},
        }
        observed["features"] = features
        observed["refined"] = np.abs(signed) * 0.75
        return observed["refined"], None, 0.0

    def omnifold(gen_in, reco, measured, pr, pt, pm, iterations, **kwargs):
        assert measured is observed["features"]
        assert kwargs["measured_weights"] is observed["refined"]
        assert iterations == 5
        assert kwargs["classifier1_params"] == {"random_state": 42}
        assert kwargs["classifier2_params"] == {"random_state": 43}
        assert kwargs["regressor_params"] == {"random_state": 44}
        assert kwargs["parameter_format"] == "dict"
        assert kwargs["estimator"] == "lgbm" and kwargs["device"] == "cpu"
        assert np.all(pm)
        np.testing.assert_array_equal(kwargs["MCgen_weights"], weights)
        return None, np.array([1.1, 0.9])

    def ibu(matrix, truth, binned_target, iterations, library):
        np.testing.assert_array_equal(binned_target, target)
        np.testing.assert_array_equal(matrix, np.eye(224))
        np.testing.assert_array_equal(truth, nominal)
        assert iterations == [5, 10]
        assert library == str(tmp_path / "libRooUnfold.so")
        return {5: nominal, 10: nominal}

    comparison = SimpleNamespace(roounfold_bayes=ibu)
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
            admissibility=admission.path,
            identity=identity,
            bank=bank_path,
            truth="within_plus",
            trial=0,
            out=out,
            stage=tmp_path,
            noise_free=False,
            control=control_dir / "pair.json",
        ),
        cfg,
    )
    data = runner.read_npz(out / "pair.npz")
    np.testing.assert_array_equal(data["truth"], nominal)
    assert observed["poisson_checked"]
    np.testing.assert_allclose(
        data["omnifold"],
        core.histogram(gen[:, 0], gen[:, 1], weights * [1.1, 0.9], cfg),
    )
    np.testing.assert_array_equal(runner.read_npz(bank_path)["wt"], weights)


@pytest.fixture
def score_inputs(cfg, tmp_path, portable_io):
    """Build a complete synthetic ensemble with pinned bank and nominal control."""
    from argparse import Namespace

    bank = {"selected": np.arange(205)}
    for index, name in enumerate(cfg["truths"]):
        bank[f"truth_{name}"] = np.linspace(1, 2, 224) * (1 + index / 10)
    bank_path = tmp_path / "bank.npz"
    np.savez(bank_path, **bank)
    bank_pin = runner.digest(bank_path)
    config_pin = runner.digest(core.CONFIG)
    identity = tmp_path / "identity.json"
    runner.write_json(
        identity,
        dict(status="PASS", bank_sha256=bank_pin, config_sha256=config_pin),
    )
    products = tmp_path / "products"
    products.mkdir()
    admission = synthetic_admissibility(tmp_path / "admissibility.json", bank_path, cfg)
    control_dir = products / "nominal-control"
    control_dir.mkdir()
    nominal = bank["truth_nominal"]
    np.savez(
        control_dir / "pair.npz",
        truth=nominal,
        prior=nominal,
        selected=bank["selected"],
        omnifold=nominal * 1.01,
        ibu5=nominal,
        ibu10=nominal,
    )
    control = control_dir / "pair.json"
    runner.write_json(
        control,
        dict(
            **admission.fields("nominal-control"),
            status="PASS",
            truth="nominal",
            sampling="noise-free",
            nominal_tolerance=core.RECOVERY_TOLERANCE,
            bank_sha256=bank_pin,
            config_sha256=config_pin,
            product_sha256=runner.digest(control_dir / "pair.npz"),
        ),
    )
    for name in cfg["truths"]:
        for trial in range(5):
            directory = products / f"{name}-{trial}"
            directory.mkdir()
            truth = bank[f"truth_{name}"]
            of = truth.copy()
            of[1] *= 1.04
            ibu = truth.copy()
            ibu[0] *= 0.96
            np.savez(
                directory / "pair.npz",
                truth=truth,
                prior=nominal,
                selected=bank["selected"],
                omnifold=of,
                ibu5=ibu,
                ibu10=truth,
            )
            runner.write_json(
                directory / "pair.json",
                dict(
                    **admission.fields(f"{name}-{trial}"),
                    status="PASS",
                    sampling="poisson",
                    truth=name,
                    trial=trial,
                    seed=cfg["seeds"][trial],
                    config_sha256=config_pin,
                    bank_sha256=bank_pin,
                    control_sha256=runner.digest(control),
                    product_sha256=runner.digest(directory / "pair.npz"),
                ),
            )
    out = tmp_path / "out"
    out.mkdir()
    return Namespace(
        products=products,
        out=out,
        bank=bank_path,
        identity=identity,
        control=control,
        admissibility=admission.path,
    )


def rewrite_product(directory, **changes):
    """Replace synthetic arrays and update their receipt's byte identity."""
    import json

    product = directory / "pair.npz"
    values = runner.read_npz(product)
    values.update(changes)
    np.savez(product, **values)
    receipt = directory / "pair.json"
    record = runner.read_json(receipt)
    record["product_sha256"] = runner.digest(product)
    receipt.write_text(json.dumps(record))


def test_score_requires_complete_consistent_digest_bound_pairs(cfg, score_inputs):
    args = score_inputs
    runner.score(args, cfg)
    result = runner.read_json(args.out / "readout.json")
    assert len(result["truths"]) == 7
    assert result["schema"] == "ibukt-recovery/3"
    assert result["secondary_methods"] == ["ibu10"]
    assert result["bank_sha256"] == runner.digest(args.bank)
    assert result["config_sha256"] == runner.digest(core.CONFIG)
    assert result["control_sha256"] == runner.digest(args.control)
    assert result["control_product_sha256"] == runner.digest(
        args.control.parent / "pair.npz"
    )
    assert result["control_checks"]["omnifold"] == pytest.approx(0.01)
    assert result["truths"]["nominal"]["ibu10"]["role"] == "secondary"
    assert result["truths"]["nominal"]["ibu5"]["role"] == "primary"
    for name in cfg["truths"]:
        assert result["truths"][name]["cells"] == list(range(205))
        assert result["truths"][name]["omnifold"]["reading"][:2] == [
            "within tolerance",
            "outside tolerance",
        ]
        assert result["truths"][name]["ibu5"]["reading"][:2] == [
            "outside tolerance",
            "within tolerance",
        ]
    # A receipt cannot relabel a changed product as a completed pair.
    product = args.products / "within_minus-4" / "pair.npz"
    product.write_bytes(product.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="digest differs"):
        runner.score(args, cfg)
    product.unlink()
    with pytest.raises(FileNotFoundError):
        runner.score(args, cfg)


@pytest.mark.parametrize("artifact", ["pair.json", "pair.npz"])
def test_score_refuses_missing_control(cfg, score_inputs, artifact):
    (score_inputs.control.parent / artifact).unlink()
    with pytest.raises(FileNotFoundError):
        runner.score(score_inputs, cfg)
    assert not (score_inputs.out / "readout.json").exists()


@pytest.mark.parametrize("artifact", ["pair.json", "pair.npz"])
def test_score_refuses_changed_control(cfg, score_inputs, artifact):
    path = score_inputs.control.parent / artifact
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError):
        runner.score(score_inputs, cfg)
    assert not (score_inputs.out / "readout.json").exists()


def test_score_refuses_mixed_controls(cfg, score_inputs):
    import json

    path = score_inputs.products / "within_minus-4" / "pair.json"
    record = runner.read_json(path)
    record["control_sha256"] = "another-control"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="mismatched pair receipt"):
        runner.score(score_inputs, cfg)


def test_score_recomputes_control_recovery(cfg, score_inputs):
    rewrite_product(
        score_inputs.control.parent,
        omnifold=runner.read_npz(score_inputs.bank)["truth_nominal"] * 1.03,
    )
    with pytest.raises(ValueError, match="noise-free nominal omnifold"):
        runner.score(score_inputs, cfg)


@pytest.mark.parametrize("scope", ["all", "one-truth"])
def test_score_refuses_shortened_or_cross_truth_masks(cfg, score_inputs, scope):
    for name in cfg["truths"]:
        if scope == "one-truth" and name != "within_minus":
            continue
        selected = np.arange(204) if scope == "all" else np.arange(1, 206)
        for trial in range(5):
            rewrite_product(
                score_inputs.products / f"{name}-{trial}", selected=selected
            )
    with pytest.raises(ValueError, match="reporting mask differs"):
        runner.score(score_inputs, cfg)
    assert not (score_inputs.out / "readout.json").exists()


@pytest.mark.parametrize("key", ["truth", "prior"])
def test_score_refuses_uniform_wrong_truth_or_prior(cfg, score_inputs, key):
    for trial in range(5):
        directory = score_inputs.products / f"bump-{trial}"
        rewrite_product(
            directory, **{key: runner.read_npz(directory / "pair.npz")[key] * 1.01}
        )
    with pytest.raises(ValueError, match=f"product {key} differs from bank"):
        runner.score(score_inputs, cfg)


@pytest.mark.parametrize("key", ["truth", "prior", "omnifold", "ibu5", "ibu10"])
def test_score_refuses_wrong_vector_shapes(cfg, score_inputs, key):
    rewrite_product(score_inputs.products / "nominal-0", **{key: np.ones(205)})
    with pytest.raises(ValueError, match=f"invalid product vector: {key}"):
        runner.score(score_inputs, cfg)


def test_score_refuses_changed_bank(cfg, score_inputs):
    score_inputs.bank.write_bytes(score_inputs.bank.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="bank differs from identity control"):
        runner.score(score_inputs, cfg)


@pytest.mark.parametrize("key", ["bank_sha256", "config_sha256"])
def test_score_refuses_control_identity_mismatch(cfg, score_inputs, key):
    import json

    record = runner.read_json(score_inputs.control)
    record[key] = "different-identity"
    score_inputs.control.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="nominal control identity differs"):
        runner.score(score_inputs, cfg)


@pytest.mark.parametrize(
    "selected",
    [
        np.arange(204),
        np.arange(205, dtype=float),
        np.zeros(205, dtype=int),
        np.arange(-1, 204),
        np.arange(20, 225),
    ],
)
def test_score_refuses_invalid_bank_mask(cfg, score_inputs, selected):
    import json

    bank = runner.read_npz(score_inputs.bank)
    bank["selected"] = selected
    np.savez(score_inputs.bank, **bank)
    identity = runner.read_json(score_inputs.identity)
    identity["bank_sha256"] = runner.digest(score_inputs.bank)
    score_inputs.identity.write_text(json.dumps(identity))
    with pytest.raises(ValueError, match="205 unique valid cells"):
        runner.score(score_inputs, cfg)


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
        IBUKT_ADMISSION=str(tmp_path / "admission.json"),
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


def test_within_integrals_hold_across_distinct_cells(cfg):
    pt = np.array([0.08, 0.14, 0.26, 0.32, 0.26, 0.32])
    pz = np.array([4.2, 4.2, 4.2, 4.2, 8.5, 8.5])
    weights = np.array([1.0, 9.0, 3.0, 7.0, 8.0, 2.0])
    means = core.moments(pt, pz, weights, cfg)
    nominal = core.histogram(pt, pz, weights, cfg)
    assert np.count_nonzero(nominal) == 3
    for name in ("within_plus", "within_minus"):
        factors = core.truth_factor(name, pt, pz, means, cfg, {})
        np.testing.assert_allclose(
            core.histogram(pt, pz, weights * factors, cfg), nominal, rtol=1e-12
        )


def test_pinned_ratio_map_index_and_overflow(cfg, portable_io):
    maps = runner.ratios(cfg)
    values = core.truth_factor(
        "nuwro",
        np.array([0.08, 0.32, 4.5]),
        np.array([4.2, 8.5, 4.2]),
        np.zeros(224),
        cfg,
        maps,
    )
    np.testing.assert_array_equal(
        values, [maps["nuwro"][1, 5], maps["nuwro"][3, 10], 1]
    )


def test_prepare_truth_controls_reject_vacuous_or_nonconserving_stresses():
    truths = dict(
        nominal=np.array([10.0, 20.0]),
        within_plus=np.array([10.0, 20.0]),
        within_minus=np.array([10.0, 20.0]),
    )
    reco = dict(
        nominal=np.array([5.0, 12.0]),
        within_plus=np.array([6.0, 11.0]),
        within_minus=np.array([4.0, 13.0]),
    )
    assert (
        runner.truth_controls(truths, reco, np.arange(2))[
            "reco_relative_shift_within_plus"
        ]
        > 0
    )
    with pytest.raises(ValueError, match="vacuous"):
        runner.truth_controls(
            truths, dict(reco, within_plus=reco["nominal"]), np.arange(2)
        )
    with pytest.raises(ValueError, match="within-bin integral"):
        runner.truth_controls(
            dict(truths, within_plus=truths["nominal"] * 1.001), reco, np.arange(2)
        )


def test_preflight_prices_real_lane_wall_and_retains_scoring():
    got = core.forecast(910, 1820, 0.4)
    assert got["projected_seconds"] == 18 * 910
    assert got["remaining_seconds"] == 5.25 * 3600 - 1820 - 60
    with pytest.raises(ValueError, match="STOP"):
        core.forecast(1000, 2000, 0.4)
    with pytest.raises(ValueError, match="STOP"):
        core.forecast(910, 1820, 1.5)
    for wall, elapsed, prior in (
        (0, 100, 0),
        (100, 50, 0),
        (100, 200, -1),
        (np.nan, 200, 0),
    ):
        with pytest.raises(ValueError):
            core.forecast(wall, elapsed, prior)


def test_screen_allocation_and_steps_use_declared_packing():
    script = (runner.REPO / "2d-unfolding/ibukt/screen.sbatch").read_text()
    assert "#SBATCH --exclusive\n" in script
    assert "#SBATCH --time=05:15:00" in script
    assert "srun -n1 -c 64 --exact --mem=121920M --mem-bind=local" in script
    step = script.split("srun ", 1)[1].split("\n", 1)[0]
    assert "--exclusive" not in step and "--nodes" not in step
    assert (
        script.index("run_pair nominal-control")
        < script.index("run_pair nominal-0")
        < script.index("jobs.py forecast")
        < script.index("for truth in")
    )


@pytest.mark.parametrize("bad_method", [None, "omnifold", "ibu5"])
def test_noise_free_pair_closes_or_stops_before_pass_receipt(
    cfg, tmp_path, monkeypatch, portable_io, bad_method
):
    from argparse import Namespace
    from types import SimpleNamespace

    gen = np.array([[0.1, 4.2], [0.3, 8.5]])
    wt = np.array([10.0, 20.0])
    truth = core.histogram(gen[:, 0], gen[:, 1], wt, cfg)
    selected = np.flatnonzero(truth)
    bank_path = tmp_path / "bank.npz"
    np.savez(
        bank_path,
        gen=gen,
        reco=gen,
        pt=np.ones(2, bool),
        pr=np.ones(2, bool),
        wt=wt,
        ibu_prior=truth,
        ibu_response=np.diag(truth),
        wr=wt,
        bkg=gen[:1],
        bw=np.array([2.0]),
        means=np.zeros(224),
        factor=np.ones(224),
        selected=selected,
        truth_nominal=truth,
    )
    identity = tmp_path / "identity.json"
    runner.write_json(
        identity,
        dict(
            status="PASS",
            config_sha256=runner.digest(core.CONFIG),
            bank_sha256=runner.digest(bank_path),
        ),
    )

    def forbid_poisson(*args):
        pytest.fail("noise-free control must not draw Poisson counts")

    def refine(features, signed, **kwargs):
        np.testing.assert_array_equal(signed, [10, 20, 2, -2])
        return np.abs(signed), None, 0.0

    ibu5 = truth * (1.03 if bad_method == "ibu5" else 1.01)
    helper = SimpleNamespace(
        omnifold=lambda *a, **kw: (
            None,
            np.full(2, 1.03 if bad_method == "omnifold" else 1.01),
        )
    )
    comparison = SimpleNamespace(
        binned_problem=lambda *a: (truth, np.eye(224), truth, None),
        roounfold_bayes=lambda *a: {5: ibu5, 10: truth},
    )
    monkeypatch.setattr(
        runner,
        "dependencies",
        lambda: (comparison, SimpleNamespace(refine_stay_positive=refine), helper),
    )
    monkeypatch.setattr(runner, "ratios", lambda cfg: {})
    monkeypatch.setattr(core, "poisson_target", forbid_poisson)
    out = tmp_path / "control"
    out.mkdir()
    admission = synthetic_admissibility(
        tmp_path / "admissibility.json", bank_path, cfg, **{"nominal-control": truth}
    )
    args = Namespace(
        admissibility=admission.path,
        identity=identity,
        bank=bank_path,
        out=out,
        stage=tmp_path,
        truth="nominal",
        trial=0,
        noise_free=True,
        control=None,
    )
    if bad_method:
        with pytest.raises(ValueError, match=f"noise-free nominal {bad_method}"):
            runner.pair(args, cfg)
        assert not (out / "pair.json").exists()
        assert (out / "pair.npz").exists()
    else:
        runner.pair(args, cfg)
        record = runner.read_json(out / "pair.json")
        assert record["sampling"] == "noise-free" and record["seed"] is None
        assert record["nominal_tolerance"] == 0.02
        assert runner.nominal_control(
            out / "pair.json", runner.digest(bank_path)
        ) == pytest.approx({"omnifold": 0.01, "ibu5": 0.01})
        # A newly hashed but biased product still cannot unlock Poisson fits.
        np.savez(
            out / "pair.npz",
            omnifold=truth * 1.03,
            ibu5=truth,
            truth=truth,
            selected=selected,
        )
        record["product_sha256"] = runner.digest(out / "pair.npz")
        (out / "pair.json").unlink()
        runner.write_json(out / "pair.json", record)
        with pytest.raises(ValueError, match="noise-free nominal omnifold"):
            runner.nominal_control(out / "pair.json", runner.digest(bank_path))


def test_screen_admission_reserves_score_and_rejects_full_earlier_caps(
    tmp_path, portable_io
):
    import jobs

    def record(spent):
        values = core.budget(
            "", {}, jobs.LIMITS["screen"] + jobs.LIMITS["score"] + spent
        )
        return dict(
            values,
            requested=jobs.LIMITS["screen"] + jobs.LIMITS["score"],
            spent_or_reserved=spent,
            request_stage="screen",
            config_sha256=runner.digest(core.CONFIG),
        )

    path = tmp_path / "admission.json"
    runner.write_json(path, record(1.15))
    assert jobs.screen_admission(path)["total"] == pytest.approx(6.50)
    with pytest.raises(ValueError, match="cap exceeded"):
        record(1.2)
    path.unlink()
    runner.write_json(path, dict(record(1.15), total=5.0))
    with pytest.raises(ValueError, match="accounting"):
        jobs.screen_admission(path)


@pytest.mark.parametrize("factor", [0.981, 1.019])
def test_nominal_control_accepts_nonzero_residuals_inside_two_percent(factor):
    truth = np.array([1e-38, 2e-40])
    assert core.nominal_recovery(truth * factor, truth, "plant") == pytest.approx(
        abs(factor - 1)
    )


@pytest.mark.parametrize("factor", [0.979, 1.021])
def test_nominal_control_refuses_either_sign_outside_two_percent(factor):
    truth = np.array([1.0, 1e-20])
    with pytest.raises(ValueError):
        core.nominal_recovery(truth * [1, factor], truth, "plant")


def test_exact_within_bin_identity_remains_strict():
    truth = np.array([10.0, 20.0])
    # A 1% fitted recovery is acceptable; a 1% integral-identity error is not.
    assert core.nominal_recovery(truth * 1.01, truth, "fit") == pytest.approx(0.01)
    with pytest.raises(ValueError):
        runner.require_close(truth * 1.01, truth, "integral identity")


def test_signed_target_refuses_negative_unsupported_and_nonfinite_bins():
    target = np.zeros(224)
    response = np.zeros(224)
    response[:3] = 2
    target[0] = -0.125
    target[1] = 1
    target[3] = 2
    target[4] = np.nan

    assert core.signed_target_violations(target, response) == [
        {"index": 0, "signed_count": -0.125, "response_row_sum": 2.0},
        {"index": 3, "signed_count": 2.0, "response_row_sum": 0.0},
        {"index": 4, "signed_count": "nan", "response_row_sum": 0.0},
    ]


def test_signed_target_digest_binds_counts_and_bin_order():
    target = np.arange(224, dtype=np.float64)
    assert core.target_digest(target) == core.target_digest(target.astype(">f8"))
    assert core.target_digest(target) != core.target_digest(target[::-1])


def test_final_inadmissible_draw_stops_before_unfolding(cfg, tmp_path, monkeypatch):
    from argparse import Namespace

    diagonal = np.ones(224)
    generated = []

    def draw(bank, cfg, maps, name, trial):
        generated.append((name, trial))
        target = diagonal.copy()
        if (name, trial) == ("within_minus", 4):
            target[-1] = -0.125
        return None, None, target

    monkeypatch.setattr(runner, "draw_target", draw)
    monkeypatch.setattr(runner, "ratios", lambda _: {})
    monkeypatch.setattr(
        runner,
        "checked_bank",
        lambda _: (
            "bank-pin",
            {
                "ibu_prior": diagonal,
                "ibu_response": np.eye(224),
                "selected": np.arange(205),
            },
        ),
    )
    monkeypatch.setattr(runner, "digest", lambda _: "config-pin")
    monkeypatch.setattr(runner, "dependencies", lambda: pytest.fail("early unfold"))
    with pytest.raises(ValueError, match="within_minus-4"):
        runner.admissibility(Namespace(out=tmp_path), cfg)
    assert len(generated) == 36
    assert not (tmp_path / "admissibility.json").exists()
    stop = __import__("json").loads((tmp_path / "stop.json").read_text())
    assert stop["bins"] == [
        {"index": 223, "signed_count": -0.125, "response_row_sum": 1.0}
    ]


def test_nominal_signed_background_cancels_exactly(cfg):
    reco = np.array([[0.12, 4.2], [0.13, 4.2]])
    bank = {
        "gen": reco,
        "reco": reco,
        "pt": np.array([True, True]),
        "pr": np.array([True, True]),
        "wr": np.array([0.125, 0.375]),
        "bkg": reco[:1],
        "bw": np.array([1000.1]),
        "means": np.zeros(224),
    }
    _, _, target = runner.draw_target(bank, cfg, {}, "nominal", None)
    assert np.count_nonzero(target) == 1
    assert target.sum() == 0.5
    assert core.signed_target_violations(target, target) == []
