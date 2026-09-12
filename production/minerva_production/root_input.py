"""Scalar ROOT input adapter using the retained N-D selection and target builders."""

from __future__ import annotations

import hashlib
import json
import math
from array import array
from pathlib import Path
from typing import Any

from .storage import ROOT, digest, legacy_module, provenance
from .universe_input import resolve_universe, source_contract

ENTRY_BRANCH = "__production_source_entry__"
SUPPORTED_AXES = [["eavail"], ["eavail", "q3"], ["eavail", "q3", "W"]]
ADAPTER_SOURCES = (
    "production/minerva_production/root_input.py",
    "production/minerva_production/universe_input.py",
    "production/minerva_production/storage.py",
    "nd-unfolding/unfold_nd_omnifold_unbinned.py",
    "2d-unfolding/unfold_2d_omnifold_unbinned.py",
    "nd-unfolding/flux_universe.py",
)


class EntryIndexedTree:
    """Read-only TTree view carrying source row indices through native collectors.

    The virtual coordinate is always finite and never binned or trained on.
    It traverses the same retention branches as each physical coordinate, so
    selected identities need no second implementation of the physics cuts.
    Branch buffers belong to this view and are detached on close.
    """

    def __init__(self, tree: Any) -> None:
        self.tree = tree
        self.buffers: list[array[Any]] = []
        if tree.GetBranch(ENTRY_BRANCH):
            raise ValueError(f"reserved adapter branch already exists: {ENTRY_BRANCH}")
        if tree.GetEntries() >= 2**53:
            raise ValueError("TTree entry indices exceed exact double precision")
        tree.ResetBranchAddresses()
        tree.SetBranchStatus("*", 0)

    def GetEntries(self) -> int:
        """Return the full source inventory size."""
        return int(self.tree.GetEntries())

    def GetEntry(self, entry: int) -> int:
        """Read a source entry and populate its exact virtual coordinate."""
        result = int(self.tree.GetEntry(entry))
        if result <= 0:
            raise ValueError(f"{self.GetName()}: failed to read source entry {entry}")
        for buffer in self.buffers:
            buffer[0] = entry
        return result

    def GetBranch(self, name: str) -> Any:
        """Report the virtual coordinate or the underlying physical branch."""
        return True if name == ENTRY_BRANCH else self.tree.GetBranch(name)

    def GetName(self) -> str:
        """Return the unchanged source TTree name."""
        return str(self.tree.GetName())

    def SetBranchAddress(self, name: str, buffer: array[Any]) -> int:
        """Bind a collector buffer, refusing absent or mismatched source branches."""
        if name == ENTRY_BRANCH:
            self.buffers.append(buffer)
            return 0
        if not self.tree.GetBranch(name):
            raise ValueError(f"{self.GetName()}: missing source branch {name}")
        self.tree.SetBranchStatus(name, 1)
        result = self.tree.SetBranchAddress(name, buffer)
        if result is not None and int(result) < 0:
            raise ValueError(f"{self.GetName()}: incompatible branch type for {name}")
        return 0

    def close(self) -> None:
        """Detach Python buffers before the source file is closed."""
        self.tree.ResetBranchAddresses()
        self.tree.SetBranchStatus("*", 1)
        self.buffers.clear()


def plan(config: dict[str, Any], source: Path, output: Path) -> dict[str, Any]:
    """Resolve a standard scalar preparation without opening event or flux files."""
    required = {"mode", "axes", "flux_file"}
    if (
        required - config.keys()
        or set(config) - (required | {"universe", "flux_universe_file"})
        or config["mode"] != "scalar-root"
    ):
        raise ValueError(
            "scalar-root config requires exactly mode, axes and flux_file, with optional universe and flux_universe_file"
        )
    if config["axes"] not in SUPPORTED_AXES:
        raise ValueError(f"scalar-root axes must be one of {SUPPORTED_AXES}")
    flux_file = Path(config["flux_file"]).expanduser().resolve()
    paths = [source, flux_file]
    resolved_config = {**config, "flux_file": str(flux_file)}
    if "universe" in config:
        resolved_config["universe"] = resolve_universe(config["universe"])
    is_flux = resolved_config.get("universe", {}).get("band") == "Flux"
    if is_flux != ("flux_universe_file" in config):
        raise ValueError(
            "Flux variation requires flux_universe_file; other bands do not use it"
        )
    if is_flux:
        flux_universe_file = Path(config["flux_universe_file"]).expanduser().resolve()
        resolved_config["flux_universe_file"] = str(flux_universe_file)
        paths.append(flux_universe_file)
    return {
        "status": "plan-only",
        "input": str(source),
        "output": str(output),
        "resolved_config": resolved_config,
        "missing_paths": [str(path) for path in paths if not path.is_file()],
        "selection": "nd-standard-v1",
        "background": "preweighted-purity",
        "features": ["pt", "pparallel", *config["axes"]],
        "environment": "ROOT 6.28 with NumPy; guarded execution in an authorized allocation",
        "requirements": [
            "Input is the per-playlist merged scalar event-loop ROOT product, not an unidentified row cache.",
            "Flux is the separate baseline POT-weighted MEFHC product.",
            "Reads the full declared input; this command grants no compute authority.",
            "Standard phase space and native purity target; lateral universes require active selection metadata.",
        ],
    }


def prepare(config: dict[str, Any], source: Path, output: Path) -> None:
    """Materialize a source-bound scalar cache using the retained ROOT procedure.

    Parameters
    ----------
    config : dict
        Standard scalar axes and independent baseline flux path.
    source : Path
        Immutable ROOT event inventory with signal, data, background and denominator.
    output : Path
        Fresh NPZ path. No existing product is replaced.
    """
    import numpy as np

    resolved = plan(config, source, output)
    config = resolved["resolved_config"]
    if resolved["missing_paths"]:
        raise ValueError(
            f"scalar ROOT prerequisites missing: {resolved['missing_paths']}"
        )
    if output.exists():
        raise FileExistsError(output)
    legacy_module("mnv_guarded_run").install(str(ROOT))
    driver = legacy_module("scalar_driver")
    root = driver.ROOT

    flux_file = Path(resolved["resolved_config"]["flux_file"])
    paths = [source, flux_file]
    if "flux_universe_file" in config:
        paths.append(Path(config["flux_universe_file"]))
    snapshots = {path: path.stat() for path in paths}
    sources = {str(path): digest(path) for path in snapshots}
    source_file = root.TFile.Open(str(source), "READ")
    if not source_file or source_file.IsZombie():
        raise ValueError(f"cannot open ROOT input: {source}")
    views = {}
    try:
        variation = source_contract(source_file, config.get("universe"), driver)
        universe_branch = None
        if variation["mode"] == "vertical-branches":
            universe_branch = (config["universe"]["band"], config["universe"]["index"])
        for name in ("mc_signal_reco", "data", "mc_background", "mc_truth_denom"):
            tree = source_file.Get(name)
            if not tree or not tree.InheritsFrom("TTree"):
                raise ValueError(f"missing source TTree: {name}")
            views[name] = EntryIndexedTree(tree)
        if driver.u2d.MAX_MUON_THETA_RAD != math.radians(20):
            raise ValueError(
                "the loaded collector does not have the standard truth-angle gate"
            )
        axes = [dict(driver.EXTRA_AXES[name], name=name) for name in config["axes"]]
        identity_axis = {key: ENTRY_BRANCH for key in ("truth", "reco", "data", "bkg")}
        collect_axes = [*axes, identity_axis]
        edges = [
            driver.u2d.PT_EDGES,
            driver.u2d.PZ_EDGES,
            *[axis["edges"] for axis in axes],
        ]
        bounds = (edges[0][0], edges[0][-1], edges[1][0], edges[1][-1])
        data_pot, mc_pot, pot_scale = driver.u2d.get_pot_scales(source_file)
        flux, _ = driver.u2d.load_flux_bins(
            str(flux_file), "pTmu_reweightedflux_integrated", edges[0]
        )
        if "flux_universe_file" in config:
            flux = driver.fluxu.flux_universe_bins(
                config["flux_universe_file"],
                config["universe"]["index"],
                edges[0],
                flux,
            )
        signal = driver.collect_signal_nd(
            views["mc_signal_reco"],
            collect_axes,
            *bounds,
            pot_scale,
            use_weights=True,
            universe_branch=universe_branch,
        )
        measured_pt, measured_pz, measured_extra = driver.collect_data_nd(
            views["data"], collect_axes, *bounds
        )
        bkg_pt, bkg_pz, bkg_extra, bkg_weights = driver.collect_bkg_nd(
            views["mc_background"],
            collect_axes,
            pot_scale,
            *bounds,
            universe_branch=universe_branch,
        )
        denominator = driver.collect_truth_denom_nd(
            views["mc_truth_denom"],
            collect_axes,
            *bounds,
            pot_scale,
            use_weights=True,
            universe_branch=universe_branch,
        )
        signal_entries = signal["truth_extras"].pop().astype(np.int64)
        signal["reco_extras"].pop()
        data_entries = measured_extra.pop().astype(np.int64)
        bkg_entries = bkg_extra.pop().astype(np.int64)
        denominator_entries = denominator["extras"].pop().astype(np.int64)
        native_misses = source_file.Get("hasTruthOnlyMisses")
        has_native_misses = bool(int(native_misses.GetVal())) if native_misses else None
        if has_native_misses and int(signal["pass_truth"].sum()) != len(
            denominator["pt"]
        ):
            raise ValueError("finite-support signal/truth-denominator closure failed")
        measured_columns = [measured_pt, measured_pz, *measured_extra]
        measured_matrix = np.column_stack(measured_columns)
        measured_digest = hashlib.sha256(measured_matrix.tobytes())
        measured_digest.update(data_entries.tobytes())
        data_hist, _ = driver.histnd(measured_columns, np.ones(len(measured_pt)), edges)
        background_hist, _ = driver.histnd(
            [bkg_pt, bkg_pz, *bkg_extra], bkg_weights, edges
        )
        measured_weights = driver.build_measured_training_nd(
            measured_columns, data_hist, background_hist, edges
        )
        denominator_hist, _ = driver.histnd(
            [denominator["pt"], denominator["pz"], *denominator["extras"]],
            denominator["w"],
            edges,
        )
        truth = np.column_stack(
            [signal["truth_pt"], signal["truth_pz"], *signal["truth_extras"]]
        )
        prior = np.histogramdd(
            truth[signal["pass_truth"]],
            bins=edges,
            weights=signal["w_truth"][signal["pass_truth"]],
        )[0]
        if not (data_pot > 0 and np.isfinite(flux).all() and (flux > 0).all()):
            raise ValueError("positive data POT and finite positive flux are required")
        if (
            not ((prior > 0) & (denominator_hist > 0)).any()
            or not (measured_weights > 0).any()
        ):
            raise ValueError(
                "source has no populated support or positive measured target"
            )
        features = resolved["features"]
        units = {
            name: "GeV/c" if name in {"pt", "pparallel"} else "GeV" for name in features
        }
        metadata = {
            "selection": resolved["selection"],
            "background": resolved["background"],
            "feature_names": features,
            "feature_units": units,
            "flux_axis": 0,
            "denominator_policy": "fixed-under-bootstrap",
            "normalization_units": {
                "flux": "m^-2/POT",
                "data_pot": "POT",
                "n_nucleons": "nucleons",
            },
            "normalization_source": {
                "input_path": str(source),
                "input_sha256": sources[str(source)],
                "flux_path": str(flux_file),
                "flux_sha256": sources[str(flux_file)],
                "mc_pot": mc_pot,
            },
            "preparation_config": resolved["resolved_config"],
            "provenance": provenance(),
            "identity": {
                "kind": "source-file-sha256/tree/entry",
                "source_sha256": sources[str(source)],
                "truth_tree": "mc_signal_reco",
                "reco_tree": "mc_signal_reco",
                "data_tree": "data",
            },
            "has_native_misses": has_native_misses,
            "variation": variation,
            "measured_inventory_sha256": measured_digest.hexdigest(),
            "source_digests": sources,
            "background_contract": "native N-D purity max(0,D-B)/D; background tree varies only during universe preparation; fixed under the two-stream bootstrap",
            "output_contract": {
                "axes": [
                    {"name": name, "unit": units[name], "edges": list(axis_edges)}
                    for name, axis_edges in zip(features, edges)
                ],
                "ordering": "C",
                "meaning": "density",
                "value_unit": "cm^2/nucleon",
                "projection_domain": "reported-source",
                "support": ((prior > 0) & (denominator_hist > 0)).ravel().tolist(),
            },
            "adapter_sources": {name: digest(ROOT / name) for name in ADAPTER_SOURCES},
        }
        payload = {
            "MCgen": truth,
            "MCreco": np.column_stack(
                [signal["reco_pt"], signal["reco_pz"], *signal["reco_extras"]]
            ),
            "measured": measured_matrix,
            "measured_weights": measured_weights,
            "pass_truth": signal["pass_truth"],
            "pass_reco": signal["pass_reco"],
            "meas_pass_reco": np.ones(len(measured_pt), bool),
            "w_truth": signal["w_truth"],
            "w_reco": signal["w_reco"],
            "truth_id": signal_entries,
            "reco_id": signal_entries.copy(),
            "data_id": data_entries,
            "background_entries": bkg_entries,
            "denominator_entries": denominator_entries,
            "denom_nd": denominator_hist,
            "flux": flux,
            "data_pot": data_pot,
            "n_nucleons": driver.u2d.TRACKER_FIDUCIAL_N_NUCLEONS,
            "data_histogram": data_hist,
            "background_histogram": background_hist,
            "metadata": json.dumps(metadata, allow_nan=False),
        }
    finally:
        for view in views.values():
            view.close()
        source_file.Close()
    for path, before in snapshots.items():
        after = path.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise ValueError(f"source changed during preparation: {path}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        np.savez_compressed(stream, **payload)
