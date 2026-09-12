"""Calculation-scoped compatibility without fitting or scanning event inputs."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np
import pytest

from production.minerva_production import cli, storage


@pytest.fixture
def checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "checkout"
    sources = set(storage.code_identity()["sources"])
    sources.update(storage.code_identity(backend="nominal-lgbm-v1")["sources"])
    sources.update(storage.code_identity("projection")["sources"])
    sources.update(
        {
            "production/minerva_production/pet.py",
            "production/unfold_pet.py",
            "production/README.md",
        }
    )
    for source in sources:
        destination = root / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(storage.ROOT / source, destination)
    monkeypatch.setattr(storage, "ROOT", root)
    monkeypatch.setattr(storage, "provenance", lambda: {"revision": "a" * 40})
    return root


def test_resume_ignores_revision_docs_and_pet(
    checkout: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    identity = {
        "code": storage.code_identity(),
        "input_sha256": "input",
        "config": {"seed": 42},
    }
    output = tmp_path / "nominal"
    storage.save_result(output, {"xsec": np.array([1.0])}, {"identity": identity})
    for name in (
        "production/README.md",
        "production/minerva_production/pet.py",
        "production/unfold_pet.py",
    ):
        (checkout / name).write_text("unrelated change\n")
    monkeypatch.setattr(storage, "provenance", lambda: {"revision": "b" * 40})
    assert storage.code_identity() == identity["code"]
    assert storage.check_output(output, identity, True)
    _, record = storage.load_result(output)
    assert record["provenance"]["revision"] == "a" * 40
    assert "revision" not in record["identity"]["code"]
    assert storage.provenance()["revision"] == "b" * 40


@pytest.mark.parametrize(
    "path",
    [
        "production/minerva_production/scalar.py",
        "production/minerva_production/uncertainty.py",
        "nd-unfolding/omnifold_nn_core.py",
        "nd-unfolding/xsec_nd.py",
        "nd-unfolding/mnv_guarded_run.py",
    ],
)
def test_resume_rejects_relevant_source_changes(
    checkout: Path, tmp_path: Path, path: str
) -> None:
    identity = {"code": storage.code_identity()}
    output = tmp_path / "nominal"
    storage.save_result(output, {"xsec": np.array([1.0])}, {"identity": identity})
    with (checkout / path).open("a") as stream:
        stream.write("\nchanged_implementation = True\n")
    with pytest.raises(ValueError, match="resume identity differs"):
        storage.check_output(output, {"code": storage.code_identity()}, True)


def test_assembly_after_unrelated_changes(checkout: Path, tmp_path: Path) -> None:
    config = {"estimator_seed": 42, "backend": "cached-lgbm-v1"}
    nominal_identity = {
        "operation": "unfold_gbdt",
        "code": storage.code_identity(),
        "config": config,
    }
    nominal = tmp_path / "nominal"
    contract = {"support": [True, True]}
    storage.save_result(
        nominal,
        {"xsec": np.array([2.0, 4.0])},
        {
            "identity": nominal_identity,
            "output_contract": contract,
        },
    )
    _, nominal_record = storage.load_result(nominal)
    members = tmp_path / "members"
    for seed in (1, 2):
        identity = {
            **nominal_identity,
            "operation": "member",
            "nominal": storage.fingerprint(nominal_record),
            "perturbation": {
                "source": "statistical",
                "mode": "data-only",
                "seed": seed,
            },
        }
        storage.save_result(
            members / f"member_{seed}",
            {"xsec": np.array([seed, 2.0 * seed])},
            {
                "identity": identity,
                "output_contract": contract,
            },
        )
    (checkout / "production/minerva_production/pet.py").write_text("unrelated change\n")
    args = argparse.Namespace(
        nominal=nominal,
        input=members,
        output=tmp_path / "covariance",
        action="combine",
        source="statistical",
        mode="data-only",
        seeds=[1, 2],
        resume=False,
    )
    cli._uncertainties(args, config)
    arrays, _ = storage.load_result(args.output)
    np.testing.assert_array_equal(arrays["covariance"], [[0.5, 1.0], [1.0, 2.0]])
    args.resume = True
    cli._uncertainties(args, config)
    (checkout / "nd-unfolding/omnifold_nn_core.py").write_text("relevant change\n")
    with pytest.raises(ValueError, match="nominal code/dependencies differ"):
        cli._uncertainties(args, config)


def test_projection_excludes_training_engine(checkout: Path) -> None:
    identity = storage.code_identity("projection")
    (checkout / "nd-unfolding/omnifold_nn_core.py").write_text("different training\n")
    assert storage.code_identity("projection") == identity
    (checkout / "nd-unfolding/uq_math.py").write_text("different projection\n")
    assert storage.code_identity("projection") != identity


def test_each_estimator_binds_only_its_engine(checkout: Path) -> None:
    nominal = storage.code_identity(backend="nominal-lgbm-v1")
    cached = storage.code_identity()
    source = checkout / "unbinned_unfolding/python/omnifold.py"
    source.write_text("changed nominal estimator\n")
    assert storage.code_identity(backend="nominal-lgbm-v1") != nominal
    assert storage.code_identity() == cached
