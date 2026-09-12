"""No-fit source-entry transport and ROOT adapter command boundaries."""

from __future__ import annotations

from array import array
from pathlib import Path
from typing import Any

import pytest

from production.minerva_production.root_input import (
    ENTRY_BRANCH,
    EntryIndexedTree,
    plan,
)


class Tree:
    """Small stand-in for the TTree branch-buffer protocol, not event data."""

    def __init__(self) -> None:
        self.buffers: dict[str, array[Any]] = {}
        self.enabled: list[tuple[str, int]] = []

    def GetEntries(self) -> int:
        return 3

    def GetName(self) -> str:
        return "source"

    def GetBranch(self, name: str) -> bool:
        return name in {"coordinate", "wrong_type"}

    def SetBranchStatus(self, name: str, enabled: int) -> None:
        self.enabled.append((name, enabled))

    def SetBranchAddress(self, name: str, buffer: array[Any]) -> int:
        if name == "wrong_type":
            return -2
        self.buffers[name] = buffer
        return 0

    def ResetBranchAddresses(self) -> None:
        self.buffers.clear()

    def GetEntry(self, entry: int) -> int:
        if entry >= 3:
            return 0
        for buffer in self.buffers.values():
            buffer[0] = entry * 2.5
        return 8


def test_entry_coordinates_share_the_native_read() -> None:
    tree = Tree()
    indexed = EntryIndexedTree(tree)
    coordinate, truth_entry, reco_entry = (array("d", [0]) for _ in range(3))
    indexed.SetBranchAddress("coordinate", coordinate)
    indexed.SetBranchAddress(ENTRY_BRANCH, truth_entry)
    indexed.SetBranchAddress(ENTRY_BRANCH, reco_entry)
    for entry in range(indexed.GetEntries()):
        indexed.GetEntry(entry)
        assert coordinate[0] == 2.5 * entry
        assert truth_entry[0] == reco_entry[0] == entry
    assert tree.enabled == [("*", 0), ("coordinate", 1)]
    indexed.close()
    assert tree.enabled[-1] == ("*", 1)
    assert tree.buffers == {}


def test_missing_mismatched_and_unreadable_entries_fail() -> None:
    indexed = EntryIndexedTree(Tree())
    for name, message in (
        ("missing", "missing source branch"),
        ("wrong_type", "incompatible branch type"),
    ):
        with pytest.raises(ValueError, match=message):
            indexed.SetBranchAddress(name, array("d", [0]))
    with pytest.raises(ValueError, match="failed to read source entry"):
        indexed.GetEntry(3)


def test_real_adapter_plan_needs_no_arrays_or_root(tmp_path: Path) -> None:
    output = tmp_path / "events.npz"
    config = {
        "mode": "scalar-root",
        "axes": ["eavail", "q3", "W"],
        "flux_file": str(tmp_path / "flux.root"),
    }
    resolved = plan(config, tmp_path / "source.root", output)
    assert resolved["features"] == ["pt", "pparallel", "eavail", "q3", "W"]
    assert len(resolved["missing_paths"]) == 2
    assert not output.exists()
    with pytest.raises(ValueError, match="exactly"):
        plan({**config, "universe": "Flux:0"}, tmp_path / "source.root", output)
    with pytest.raises(ValueError, match="axes"):
        plan({**config, "axes": ["q3"]}, tmp_path / "source.root", output)
