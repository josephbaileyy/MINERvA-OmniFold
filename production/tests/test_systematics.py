"""No-fit native universe boundaries, matched-family assembly and projection."""

from __future__ import annotations

import argparse
import copy
import shutil
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

from production.minerva_production import storage, systematics
from production.minerva_production.projection import project
from production.minerva_production.universe_input import MIGRATION_KEYS, source_contract


def family(band: str = "BeamAngleX") -> dict[str, Any]:
    return systematics.inventory(
        {
            "band": band,
            "expected_indices": [1, 0],
            "members": [{"index": index, "input": f"{index}.root"} for index in (0, 1)],
        }
    )


@pytest.mark.parametrize(
    "change",
    [
        {"expected_indices": [0]},
        {"expected_indices": [0, 0]},
        {"expected_indices": [0, 2]},
        {"members": []},
        {"members": [{"index": 0, "input": "0.root"}] * 2},
        {"flux_universe_file": "unexpected.npz"},
    ],
)
def test_inventory_refuses_incomplete_or_mixed_family(change: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        systematics.inventory({**family(), **change})


def test_flux_requires_explicit_table() -> None:
    with pytest.raises(ValueError, match="per-universe flux"):
        family("Flux")
    resolved = systematics.inventory(
        {**family(), "band": "Flux", "flux_universe_file": "flux.npz"}
    )
    assert resolved["expected_indices"] == [0, 1]
    assert resolved["flux_universe_file"] == "flux.npz"


def test_systematic_compatibility_tracks_adapter_not_pet_or_docs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = {"backend": "cached-lgbm-v1"}
    original = systematics.calculation_identity(cfg)
    unrelated = ("production/README.md", "production/minerva_production/pet.py")
    paths = (
        set(original["sources"]) | set(original["scalar"]["sources"]) | set(unrelated)
    )
    for path in paths:
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(storage.ROOT / path, destination)
    monkeypatch.setattr(storage, "ROOT", tmp_path)
    monkeypatch.setattr(systematics, "ROOT", tmp_path)
    for path in unrelated:
        (tmp_path / path).write_text("unrelated change\n")
    assert systematics.calculation_identity(cfg) == original
    for path in (
        "production/minerva_production/universe_input.py",
        "nd-unfolding/flux_universe.py",
    ):
        source = tmp_path / path
        content = source.read_text()
        source.write_text(content + "\nchanged_calculation = True\n")
        assert systematics.calculation_identity(cfg) != original
        source.write_text(content)


def root_source(values: dict[str, Any], shifted: bool = False) -> Any:
    objects = {
        name: SimpleNamespace(
            GetVal=lambda value=value: value, GetTitle=lambda value=value: value
        )
        for name, value in values.items()
    }
    objects.update(
        {
            name: SimpleNamespace(GetBranch=lambda name: shifted)
            for name in ("mc_signal_reco", "mc_truth_denom", "mc_background")
        }
    )
    return SimpleNamespace(Get=objects.get)


def active_metadata() -> dict[str, Any]:
    return {
        "hasActiveUniverse": 1,
        "activeUniverseBand": "BeamAngleX",
        "activeUniverseIndex": 0,
        "activeUniverseIsLateral": 1,
        "hasTruthOnlyMisses": 1,
        **dict.fromkeys(MIGRATION_KEYS, 0),
    }


def test_active_selection_requires_matching_identity_and_complete_census() -> None:
    values = active_metadata()
    universe = {"band": "BeamAngleX", "index": 0}
    contract = source_contract(root_source(values), universe, None)
    assert contract["mode"] == "active-selection"
    assert contract["migration_counts"] == dict.fromkeys(MIGRATION_KEYS, 0)
    for key in (*MIGRATION_KEYS, "hasTruthOnlyMisses", "activeUniverseBand"):
        missing = {name: value for name, value in values.items() if name != key}
        with pytest.raises(ValueError, match="requires identity"):
            source_contract(root_source(missing), universe, None)
    for change in (
        {"activeUniverseIndex": 1},
        {"activeUniverseIsLateral": 0},
        {"hasTruthOnlyMisses": 0},
        {MIGRATION_KEYS[0]: -1},
    ):
        with pytest.raises(ValueError):
            source_contract(root_source({**values, **change}), universe, None)
    with pytest.raises(ValueError, match="cannot serve as the nominal"):
        source_contract(root_source(values), None, None)


def test_dump_all_lateral_and_undeclared_shifts_are_refused() -> None:
    source = root_source({"hasActiveUniverse": 0})
    with pytest.raises(ValueError, match="selection-complete"):
        source_contract(source, {"band": "MuonResolution", "index": 0}, None)
    driver = SimpleNamespace(
        u2d=SimpleNamespace(
            _universe_kine_branches=lambda variation, context: ("shift_pt", "shift_pz")
        )
    )
    universe = {"band": "MinosEfficiency", "index": 0}
    assert source_contract(source, universe, driver)["mode"] == "vertical-branches"
    with pytest.raises(ValueError, match="shifted kinematic"):
        source_contract(root_source({}, shifted=True), universe, driver)
    assert source_contract(root_source({}), None, None)["hasActiveUniverse"] is None


def paired_metadata() -> dict[str, Any]:
    return {
        "selection": "nd-standard-v1",
        "background": "preweighted-purity",
        "feature_names": ["pt"],
        "feature_units": {"pt": "GeV/c"},
        "normalization_units": {"flux": "m^-2/POT"},
        "denominator_policy": "fixed-under-bootstrap",
        "flux_axis": 0,
        "adapter_sources": {"adapter": "hash"},
        "measured_inventory_sha256": "data-hash",
        "normalization_source": {"flux_sha256": "flux-hash", "mc_pot": 10.0},
        "normalization_values": {"data_pot": 4.0, "n_nucleons": 12.0},
        "variation": {"mode": "nominal"},
        "output_contract": {
            "axes": [{"name": "pt", "edges": [0, 1, 3], "unit": "GeV/c"}],
            "support": [True, True],
            "ordering": "C",
            "meaning": "density",
            "value_unit": "cm^2/nucleon",
            "projection_domain": "reported-source",
        },
    }


def test_pairing_refuses_data_calibration_and_producer_drift() -> None:
    metadata = paired_metadata()
    nominal = {
        "input_contract": metadata,
        "output_contract": metadata["output_contract"],
    }
    inputs = metadata["normalization_values"]
    systematics.validate_pairing(inputs, copy.deepcopy(metadata), nominal)
    for key in ("measured_inventory_sha256", "adapter_sources", "background"):
        with pytest.raises(ValueError, match=key):
            systematics.validate_pairing(
                inputs, {**metadata, key: "different"}, nominal
            )
    for key in ("flux_sha256", "mc_pot"):
        changed = copy.deepcopy(metadata)
        changed["normalization_source"][key] = "different"
        with pytest.raises(ValueError):
            systematics.validate_pairing(inputs, changed, nominal)


def test_native_mat_covariance_retains_common_shift_and_projects_both() -> None:
    arrays = systematics.assemble(
        {"xsec": np.array([1.0, 2.0])},
        [{"xsec": np.array([2.0, 4.0])}, {"xsec": np.array([4.0, 8.0])}],
    )
    np.testing.assert_array_equal(arrays["covariance"], [[1, 2], [2, 4]])
    np.testing.assert_array_equal(arrays["mean_shift"], [2, 4])
    np.testing.assert_array_equal(arrays["covariance_cv_centered"], [[5, 10], [10, 20]])
    projected, _ = project(arrays, paired_metadata()["output_contract"], ["pt"])
    for key in ("covariance", "covariance_cv_centered", "mean_shift"):
        np.testing.assert_array_equal(projected[key], arrays[key])


def test_combine_binds_inventory_nominal_dependencies_and_members(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = {"backend": "cached-lgbm-v1", "features": ["pt"]}
    declared = family()
    metadata = paired_metadata()
    nominal_path = tmp_path / "nominal"
    storage.save_result(
        nominal_path,
        {"xsec": np.array([1.0, 2.0])},
        {
            "identity": {
                "operation": "unfold_gbdt",
                "config": cfg,
                "code": storage.code_identity(),
            },
            "input_contract": metadata,
            "output_contract": metadata["output_contract"],
        },
    )
    _, nominal = storage.load_result(nominal_path)
    code = systematics.calculation_identity(cfg)
    for index in (0, 1):
        storage.save_result(
            tmp_path / "members" / f"member_{index}",
            {"xsec": np.array([index, 2 * index], dtype=float)},
            {
                "identity": {
                    "operation": "systematic-member",
                    "config": cfg,
                    "code": code,
                    "nominal": storage.fingerprint(nominal),
                    "inventory": storage.fingerprint(declared),
                    "variation": {"band": declared["band"], "index": index},
                    "sources": {"events": "event-hash", "flux": "flux-hash"},
                },
                "output_contract": metadata["output_contract"],
            },
        )
    args = argparse.Namespace(
        nominal=nominal_path,
        input=tmp_path / "members",
        output=tmp_path / "covariance",
        action="combine",
        resume=False,
    )
    systematics.execute(args, cfg, declared)
    arrays, record = storage.load_result(args.output)
    np.testing.assert_array_equal(arrays["covariance"], [[0.25, 0.5], [0.5, 1]])
    assert record["covariance_contract"]["divisor"] == "N"
    assert "quarantined" in record["covariance_contract"]["adoption"]
    args.resume = True
    monkeypatch.setattr(
        storage, "provenance", lambda: {"revision": "changed-unrelated-revision"}
    )
    systematics.execute(args, cfg, declared)
    with pytest.raises(ValueError, match="inventory, code or support mismatch"):
        systematics.execute(args, cfg, family("BeamAngleY"))
    monkeypatch.setattr(
        systematics,
        "calculation_identity",
        lambda cfg: {**code, "sources": {"changed": "dependency"}},
    )
    with pytest.raises(ValueError, match="inventory, code or support mismatch"):
        systematics.execute(args, cfg, declared)
