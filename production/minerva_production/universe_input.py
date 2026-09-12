"""Native universe input contracts: active selections or vertical branch swaps."""

from __future__ import annotations

import re
from typing import Any

LATERAL_BANDS = frozenset(
    {
        "BeamAngleX",
        "BeamAngleY",
        "MuonResolution",
        "Muon_Energy_MINERvA",
        "Muon_Energy_MINOS",
    }
)
MIGRATION_KEYS = (
    "activeUniverseTruthEntrants",
    "activeUniverseTruthExits",
    "activeUniverseRecoEntrants",
    "activeUniverseRecoExits",
)


def resolve_universe(value: Any) -> dict[str, Any]:
    """Validate a named native band and a nonnegative universe index."""
    if not isinstance(value, dict) or set(value) != {"band", "index"}:
        raise ValueError("universe requires exactly band and index")
    if not isinstance(value["band"], str) or not re.fullmatch(
        r"[A-Za-z0-9_]+", value["band"]
    ):
        raise ValueError("universe band must be a native alphanumeric/underscore name")
    if type(value["index"]) is not int or value["index"] < 0:
        raise ValueError("universe index must be a nonnegative integer")
    return dict(value)


def source_contract(
    source: Any, universe: dict[str, Any] | None, driver: Any
) -> dict[str, Any]:
    """Verify active selections or vertical-only support before collector reads.

    Parameters
    ----------
    source : ROOT.TFile
        Open native event-loop product.
    universe : dict or None
        Requested systematic variation, or the nominal source.
    driver : module
        Retained N-D driver with native branch-name helpers.

    Returns
    -------
    dict
        Observed source mode and migration census; missing metadata stays missing.
    """
    active_object = source.Get("hasActiveUniverse")
    active = int(active_object.GetVal()) if active_object else None
    if active not in {None, 0, 1}:
        raise ValueError("hasActiveUniverse must be 0 or 1")
    if universe is None:
        if active == 1:
            raise ValueError("an active-universe input cannot serve as the nominal")
        return {"mode": "nominal", "hasActiveUniverse": active}
    universe = resolve_universe(universe)
    band, index = universe["band"], universe["index"]
    if active == 1:
        names = (
            "activeUniverseBand",
            "activeUniverseIndex",
            "activeUniverseIsLateral",
            "hasTruthOnlyMisses",
            *MIGRATION_KEYS,
        )
        objects = {name: source.Get(name) for name in names}
        if not all(objects.values()):
            raise ValueError(
                "active universe requires identity, native misses and all migration metadata"
            )
        if (
            str(objects["activeUniverseBand"].GetTitle()) != band
            or int(objects["activeUniverseIndex"].GetVal()) != index
        ):
            raise ValueError(
                "active universe band/index differs from requested variation"
            )
        lateral = int(objects["activeUniverseIsLateral"].GetVal())
        if lateral not in {0, 1} or bool(lateral) != (band in LATERAL_BANDS):
            raise ValueError(
                "active universe lateral classification differs from the supported native bands"
            )
        if int(objects["hasTruthOnlyMisses"].GetVal()) != 1:
            raise ValueError(
                "selection-complete active input requires native truth-only misses"
            )
        census = {name: int(objects[name].GetVal()) for name in MIGRATION_KEYS}
        if any(value < 0 for value in census.values()):
            raise ValueError("migration counts must be nonnegative")
        return {
            "mode": "active-selection",
            "universe": universe,
            "migration_counts": census,
            "lateral": bool(lateral),
        }
    if band in LATERAL_BANDS:
        raise ValueError(
            "lateral variations require selection-complete active-universe ROOT files, not dump-all CV support"
        )
    variation = (band, index)
    for tree_name, context in (
        ("mc_signal_reco", "reco_tree_reco"),
        ("mc_signal_reco", "reco_tree_truth"),
        ("mc_truth_denom", "truth_tree"),
        ("mc_background", "bkg_tree_reco"),
    ):
        tree = source.Get(tree_name)
        if not tree:
            raise ValueError(f"missing systematic source tree: {tree_name}")
        shifted = driver.u2d._universe_kine_branches(variation, context)
        if any(tree.GetBranch(name) for name in shifted):
            raise ValueError(
                "shifted kinematic branches require selection-complete active inputs"
            )
    return {
        "mode": "vertical-branches",
        "universe": universe,
        "hasActiveUniverse": active,
    }
