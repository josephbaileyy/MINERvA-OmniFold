"""Bounded read-only seam for safely staged xps2 ``.npy`` inventories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import argparse
import json

import numpy as np

from .artifacts import write_json
from .utils import array_hash, environment_receipt, fingerprint

REQUIRED_XPS2_ARRAYS = (
    "part_gen",
    "part_reco",
    "pass_reco",
    "pass_truth",
    "w_truth",
)
MAX_XPS2_PACKET_ROWS = 1_000_000


@dataclass(frozen=True)
class XPS2MemmapInventory:
    directory: Path
    arrays: Mapping[str, np.memmap]
    row_count: int
    selected_rows: np.ndarray
    receipt: dict[str, Any]

    def read_packet(self) -> dict[str, np.ndarray]:
        """Materialize only the predeclared bounded row packet."""
        return {
            key: np.asarray(value[self.selected_rows])
            for key, value in self.arrays.items()
        }


def _bounded_indices(row_count: int, max_rows: int, seed: int) -> np.ndarray:
    """Generate O(max_rows) deterministic indices without an O(N) permutation."""
    if max_rows >= row_count:
        return np.arange(row_count, dtype=np.int64)
    # An odd stride is coprime to a power of two but not every N.  Resolve any
    # rare duplicates within the bounded packet deterministically, still
    # without allocating an N-row inventory.
    mask64 = (1 << 64) - 1
    start = ((int(seed) & mask64) * 0x9E3779B97F4A7C15 & mask64) % row_count
    stride = (
        (((int(seed) ^ 0x5A17) & mask64) * 0xD1B54A32D192ED03 & mask64)
        % row_count
    ) | 1
    candidates = (start + stride * np.arange(max_rows, dtype=np.uint64)) % np.uint64(
        row_count
    )
    unique = np.unique(candidates.astype(np.int64))
    if unique.size != max_rows:
        # A contiguous circular packet is the deterministic collision-safe
        # fallback and remains bounded.
        candidates = (start + np.arange(max_rows, dtype=np.uint64)) % np.uint64(
            row_count
        )
        unique = np.unique(candidates.astype(np.int64))
    if unique.size != max_rows:
        raise AssertionError("bounded xps2 selection did not produce unique rows")
    return np.sort(unique)


def open_xps2_memmap(
    directory: str | Path,
    *,
    max_rows: int,
    seed: int = 424242,
) -> XPS2MemmapInventory:
    """Open the xps2 MC inventory as read-only memmaps and select a bounded packet."""
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"xps2 memmap directory is absent: {root}")
    if max_rows < 1 or max_rows > MAX_XPS2_PACKET_ROWS:
        raise ValueError(
            f"max_rows must be in [1,{MAX_XPS2_PACKET_ROWS}] for bounded xps2 reads"
        )
    arrays: dict[str, np.memmap] = {}
    row_count = None
    for key in REQUIRED_XPS2_ARRAYS:
        path = root / f"{key}.npy"
        if not path.is_file():
            raise FileNotFoundError(f"xps2 required array is absent: {path}")
        value = np.load(path, mmap_mode="r", allow_pickle=False)
        if not isinstance(value, np.memmap):
            raise ValueError(f"xps2 array did not open as a memmap: {path}")
        if value.ndim < 1:
            raise ValueError(f"xps2 array is scalar: {path}")
        value.flags.writeable = False
        if row_count is None:
            row_count = int(value.shape[0])
        elif value.shape[0] != row_count:
            raise ValueError("xps2 arrays have different row counts")
        arrays[key] = value
    assert row_count is not None
    selected = _bounded_indices(row_count, min(max_rows, row_count), seed)
    receipt = {
        "status": "bounded_recoil_input_diagnostic",
        "adapter": "read_only_npy_memmap",
        "directory": str(root),
        "inventory_rows": row_count,
        "selected_rows": int(selected.size),
        "selection_seed": seed,
        "selection_hash": array_hash(selected),
        "w_reco_available": False,
        "w_truth_available": True,
        "weight_footing": (
            "w_truth proxy would be required on reco; explicit downgrade from "
            "the separate-w_reco publication contract"
        ),
        "full_event_evidence": False,
        "g2_evidence": False,
        "publication_omnifold_eligible": False,
    }
    receipt["fingerprint"] = fingerprint(receipt)
    return XPS2MemmapInventory(
        directory=root,
        arrays=arrays,
        row_count=row_count,
        selected_rows=selected,
        receipt=receipt,
    )


def inspect_xps2_packet(
    directory: str | Path,
    *,
    max_rows: int,
    seed: int = 424242,
) -> dict[str, Any]:
    inventory = open_xps2_memmap(directory, max_rows=max_rows, seed=seed)
    packet = inventory.read_packet()
    return {
        **inventory.receipt,
        "packet_arrays": {
            key: {
                "shape": list(value.shape),
                "dtype": str(value.dtype),
                "sha256": array_hash(value),
            }
            for key, value in packet.items()
        },
        "environment": environment_receipt(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--max-rows", type=int, required=True)
    parser.add_argument("--seed", type=int, default=424242)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = inspect_xps2_packet(
        args.directory, max_rows=args.max_rows, seed=args.seed
    )
    write_json(args.out, result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
