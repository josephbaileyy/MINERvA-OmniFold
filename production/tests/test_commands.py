"""Public workflow execution, prerequisite failures, and honest resume."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from production.minerva_production.storage import (
    ROOT,
    check_output,
    load_result,
    save_result,
)


def command(
    name: str, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "production" / name), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


@pytest.fixture(scope="module")
def smoke(tmp_path_factory: Any) -> Path:
    path = tmp_path_factory.mktemp("smoke") / "run"
    result = subprocess.run(
        ["bash", str(ROOT / "production/smoke.sh"), str(path)],
        cwd=ROOT,
        env={**os.environ, "PYTHON": sys.executable},
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return path


def test_real_smoke_products_and_covariance(smoke: Path) -> None:
    nominal, nominal_record = load_result(smoke / "nominal")
    covariance, record = load_result(smoke / "covariance")
    members = [load_result(smoke / "members" / f"member_{seed}") for seed in (7, 8, 9)]
    for _, member_record in members:
        assert (
            member_record["resolved_member_config"]
            == nominal_record["identity"]["config"]
        )
        assert member_record["output_contract"] == nominal_record["output_contract"]
    spectra = np.stack([arrays["xsec"] for arrays, _ in members])
    np.testing.assert_allclose(
        covariance["covariance"],
        np.cov(spectra, rowvar=False, ddof=1),
        rtol=1e-12,
        atol=0,
    )
    np.testing.assert_array_equal(covariance["xsec"], nominal["xsec"])
    assert record["covariance_contract"]["ensemble_size"] == 3
    assert record["scientific_status"] == "diagnostic; no publication adoption"
    closure, _ = load_result(smoke / "closure")
    np.testing.assert_allclose(
        closure["xsec"], closure["truth_xsec"], rtol=1e-12, atol=0
    )
    projection, projected_record = load_result(smoke / "projection")
    # Dropping pt weights the first row by 1 and the second by 2.
    expected = np.array([[1, 0, 2, 0], [0, 1, 0, 2]])
    np.testing.assert_allclose(
        projection["xsec"], expected @ nominal["xsec"], rtol=1e-12, atol=0
    )
    assert projected_record["covariance_contract"] == record["covariance_contract"]


def test_nominal_resume_and_changed_config(smoke: Path, tmp_path: Path) -> None:
    common = [
        "--input",
        str(smoke / "events.npz"),
        "--output",
        str(smoke / "nominal"),
        "--resume",
    ]
    command("unfold_gbdt.py", "--config", "production/examples/scalar.json", *common)
    cfg = json.loads((ROOT / "production/examples/scalar.json").read_text())
    cfg["estimator_seed"] += 1
    config_path = tmp_path / "changed.json"
    config_path.write_text(json.dumps(cfg))
    result = command(
        "unfold_gbdt.py", "--config", str(config_path), *common, check=False
    )
    assert result.returncode != 0 and "resume identity differs" in result.stderr


def test_combine_refuses_wrong_source_and_missing_member(
    smoke: Path, tmp_path: Path
) -> None:
    args = [
        "combine",
        "--source",
        "statistical",
        "--mode",
        "data-only",
        "--seeds",
        "7",
        "8",
        "9",
        "--config",
        "production/examples/scalar.json",
        "--input",
        str(smoke / "members"),
        "--nominal",
        str(smoke / "nominal"),
        "--output",
        str(tmp_path / "wrong"),
    ]
    result = command("uncertainties.py", *args, check=False)
    assert result.returncode != 0 and "mismatch" in result.stderr
    args[4] = "data-plus-mc"
    args[8] = "10"
    result = command("uncertainties.py", *args, check=False)
    assert result.returncode != 0 and "member_10" in result.stderr
    assert not (tmp_path / "wrong").exists()


def test_resume_rejects_partial_and_tampered_payload(tmp_path: Path) -> None:
    identity = {"input": "fixture", "code": "test"}
    partial = tmp_path / "partial"
    partial.mkdir()
    with pytest.raises(FileNotFoundError):
        check_output(partial, identity, True)
    complete = tmp_path / "complete"
    save_result(complete, {"xsec": np.array([1e-39])}, {"identity": identity})
    assert check_output(complete, identity, True)
    with (complete / "result.npz").open("ab") as stream:
        stream.write(b"corruption")
    with pytest.raises(ValueError, match="digest mismatch"):
        check_output(complete, identity, True)


def test_plan_does_not_load_arrays_or_write_products(tmp_path: Path) -> None:
    invalid_input = tmp_path / "events.npz"
    invalid_input.write_bytes(b"not an npz; planning must not load it")
    output = tmp_path / "output"
    result = command(
        "unfold_gbdt.py",
        "--config",
        "production/examples/scalar.json",
        "--input",
        str(invalid_input),
        "--output",
        str(output),
        "--plan",
    )
    assert json.loads(result.stdout)["status"] == "plan-only"
    assert not output.exists()


def test_root_plan_and_pet_prerequisites(tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = command(
        "prepare_events",
        "--config",
        "production/examples/prepare_root.json",
        "--input",
        "production/examples/playlists.json",
        "--output",
        str(output),
        "--plan",
    )
    plan = json.loads(result.stdout)
    assert len(plan["commands"]) == 2
    assert plan["commands"][0]["cwd"] != plan["commands"][1]["cwd"]
    assert "hadd_universes_full.py" in plan["merge"][1]
    assert "flux_file" in plan["normalization"]
    assert not output.exists()
    args = [
        "--config",
        "production/examples/pet.json",
        "--input",
        str(tmp_path / "absent.npz"),
        "--output",
        str(output),
    ]
    result = command("unfold_pet.py", *args, "--plan")
    plan = json.loads(result.stdout)
    assert "mnv_guarded_run.py" in plan["argv"][1]
    assert plan["missing_paths"] and not output.exists()
    result = command("unfold_pet.py", *args, check=False)
    assert result.returncode != 0 and "PET prerequisites missing" in result.stderr
    assert not output.exists()


def test_systematic_and_implicit_statistical_modes_fail(tmp_path: Path) -> None:
    args = [
        "run",
        "--source",
        "systematic",
        "--seeds",
        "7",
        "--config",
        "production/examples/scalar.json",
        "--input",
        "absent.npz",
        "--nominal",
        "absent",
        "--output",
        str(tmp_path / "no-output"),
    ]
    result = command("uncertainties.py", *args, check=False)
    assert result.returncode != 0 and "selection-complete" in result.stderr
    args[2] = "statistical"
    result = command("uncertainties.py", *args, check=False)
    assert result.returncode != 0 and "explicit --mode" in result.stderr


@pytest.mark.skipif(
    __import__("importlib.util").util.find_spec("ROOT") is None,
    reason="ROOT integration not run: ROOT is unavailable",
)
def test_optional_root_extraction_reference() -> None:
    # Importing the full legacy scalar module checks the actual ROOT boundary;
    # event-file production equivalence still requires the external campaign.
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "legacy_root_omnifold", ROOT / "unbinned_unfolding/python/omnifold.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.OmniFold_helper_functions.omnifold)
