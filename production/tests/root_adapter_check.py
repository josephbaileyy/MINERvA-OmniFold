"""Tiny native ROOT collector parity check; no training or real-data scans.

Run with ``python -m production.tests.root_adapter_check`` in the ROOT environment.
The trees are hand-built fixtures, so this is not real-input integration evidence.
"""

from __future__ import annotations

from array import array
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from numpy.testing import assert_array_equal

from production.minerva_production.root_input import (
    ENTRY_BRANCH,
    EntryIndexedTree,
    prepare,
)
from production.minerva_production.storage import ROOT, legacy_module


def tree(name: str, columns: dict[str, list[float]]) -> Any:
    """Build a six-row in-memory ROOT tree with native scalar branch types."""
    import ROOT as root

    result = root.TTree(name, name)
    result.SetDirectory(0)
    buffers = {}
    for column in columns:
        is_flag = column.endswith("pass")
        buffers[column] = array("B" if is_flag else "d", [0])
        result.Branch(column, buffers[column], f"{column}/{'b' if is_flag else 'D'}")
    for row in range(6):
        for column, values in columns.items():
            buffers[column][0] = values[row]
        result.Fill()
    result.ResetBranchAddresses()
    return result


def equal(actual: Any, expected: Any) -> None:
    """Check native nested collector arrays without tolerance or reordering."""
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            equal(actual[key], expected[key])
    elif isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected)
        for actual_item, expected_item in zip(actual, expected):
            equal(actual_item, expected_item)
    else:
        assert_array_equal(actual, expected)


def main() -> None:
    """Compare all four retained collectors with and without entry transport."""
    legacy_module("mnv_guarded_run").install(str(ROOT))
    driver = legacy_module("scalar_driver")
    axes = [dict(driver.EXTRA_AXES["eavail"], name="eavail")]
    indexed_axes = [
        *axes,
        {key: ENTRY_BRANCH for key in ("truth", "reco", "data", "bkg")},
    ]
    bounds = (0.0, 4.5, 1.5, 60.0)
    truth_columns = {
        "MC": [0.3, 0.4, 0.5, 4.0, float("nan"), 0.2],
        "MC_pz": [6.0, 5.0, 5.0, 2.0, 5.0, 7.0],
        "MC_eavail": [0.2] * 6,
        "w_truth": [1.0, 1.0, -1.0, 1.0, 1.0, 1.0],
    }
    signal_tree = tree(
        "mc_signal_reco",
        {
            **truth_columns,
            "sim": [0.4, float("nan"), 0.4, 0.4, 0.4, 0.4],
            "sim_pz": [6.0] * 6,
            "sim_eavail": [0.3] * 6,
            "w_reco": [1.0] * 6,
            "sim_pass": [1, 1, 1, 1, 1, 0],
        },
    )
    raw = driver.collect_signal_nd(signal_tree, axes, *bounds, 2.0, use_weights=True)
    view = EntryIndexedTree(signal_tree)
    indexed = driver.collect_signal_nd(
        view, indexed_axes, *bounds, 2.0, use_weights=True
    )
    assert_array_equal(indexed["truth_extras"].pop(), [0, 1, 3, 5])
    indexed["reco_extras"].pop()
    equal(indexed, raw)
    view.close()

    denominator_tree = tree("mc_truth_denom", truth_columns)
    raw = driver.collect_truth_denom_nd(
        denominator_tree, axes, *bounds, 2.0, use_weights=True
    )
    view = EntryIndexedTree(denominator_tree)
    indexed = driver.collect_truth_denom_nd(
        view, indexed_axes, *bounds, 2.0, use_weights=True
    )
    assert_array_equal(indexed["extras"].pop(), [0, 1, 5])
    equal(indexed, raw)
    view.close()

    trees = {"mc_signal_reco": signal_tree, "mc_truth_denom": denominator_tree}
    for name, prefix, collect in (
        ("data", "measured", driver.collect_data_nd),
        ("mc_background", "sim_background", driver.collect_bkg_nd),
    ):
        columns = {
            prefix: [0.4, 0.4, float("nan"), 10.0, 0.4, 0.4],
            prefix + "_pz": [6.0] * 6,
            prefix + "_eavail": [0.3, 0.3, 0.3, 0.3, float("inf"), 0.3],
            prefix + "_pass": [1, 0, 1, 1, 1, 1],
        }
        arguments = bounds
        if name == "mc_background":
            columns["w_bkg"] = [0.1] * 6
            arguments = (2.0, *bounds)
        source = tree(name, columns)
        trees[name] = source
        raw = collect(source, axes, *arguments)
        view = EntryIndexedTree(source)
        indexed = collect(view, indexed_axes, *arguments)
        assert_array_equal(indexed[2].pop(), [0, 5])
        equal(indexed, raw)
        view.close()
    print(
        "PASS: four native collectors preserve arrays exactly and retain expected source entries"
    )
    with TemporaryDirectory(prefix="scalar-root-fixture-", dir="/tmp") as temporary:
        directory = Path(temporary)
        root = driver.ROOT
        source_path = directory / "source.root"
        source_file = root.TFile.Open(str(source_path), "RECREATE")
        for source_tree in trees.values():
            source_tree.Write()
        root.TParameter("double")("dataPOTUsed", 2e20).Write()
        root.TParameter("double")("mcPOTUsed", 1e20).Write()
        root.TParameter("int")("hasTruthOnlyMisses", 1).Write()
        source_file.Close()
        flux_path = directory / "flux.root"
        flux_file = root.TFile.Open(str(flux_path), "RECREATE")
        flux_histogram = driver.u2d.make_flux_hist(
            "pTmu_reweightedflux_integrated", driver.u2d.PT_EDGES, [1.2e-3] * 14
        )
        flux_histogram.Write()
        flux_file.Close()
        output = directory / "events.npz"
        prepare(
            {"mode": "scalar-root", "axes": ["eavail"], "flux_file": str(flux_path)},
            source_path,
            output,
        )
        from production.minerva_production.scalar import load_inputs, resolve_config

        config = resolve_config(
            {
                "backend": "nominal-lgbm-v1",
                "features": ["pt", "pparallel", "eavail"],
                "selection": "nd-standard-v1",
                "background": "preweighted-purity",
            }
        )
        arrays, metadata = load_inputs(output, config)
        assert_array_equal(arrays["truth_id"], [0, 1, 3, 5])
        assert_array_equal(arrays["reco_id"], arrays["truth_id"])
        assert_array_equal(arrays["data_id"], [0, 5])
        assert_array_equal(arrays["denominator_entries"], [0, 1, 5])
        assert metadata["has_native_misses"] is True
        assert metadata["identity"]["kind"] == "source-file-sha256/tree/entry"
        assert arrays["data_pot"] == 2e20
        assert arrays["n_nucleons"] == driver.u2d.TRACKER_FIDUCIAL_N_NUCLEONS
        assert_array_equal(arrays["measured_weights"], [0.8, 0.8])
        print(
            "PASS: tiny ROOT fixture adapts to the validated scalar input contract; no fit performed"
        )


if __name__ == "__main__":
    main()
