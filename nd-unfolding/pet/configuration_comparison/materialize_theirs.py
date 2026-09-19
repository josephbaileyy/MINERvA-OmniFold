"""Gather his inputs for a specific set of inventory rows, without consolidating.

The signal inventory is 49.2 M rows, and a consolidated packed array would be
49.2e6 x 33 x 10 x 4 B = 65 GB. Nothing needs all of it at once: a fit sees the
2 M MC subsample and the 4.1 M data rows, which is 2.6 GB and 5.4 GB.

So this gathers on demand from the per-file shards, opening each shard once and
taking only the rows that shard owns. One pass over the shards, no intermediate
copy of the whole inventory, and the result is in INVENTORY order because the
row index is applied at the end rather than the beginning.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def materialize(files: list[str], row_index: np.ndarray, origin: np.ndarray,
                rows: np.ndarray, cap: int = 33, packed_width: int = 10,
                global_width: int = 16) -> dict[str, np.ndarray]:
    """Packed tokens and globals for `rows` of the inventory, in that order."""
    selected = np.asarray(row_index)[rows]
    if (selected < 0).any():
        raise ValueError(
            f"{int((selected < 0).sum())} of {len(rows)} requested inventory rows "
            "have no built input; resolve the join before materialising")

    where = origin[selected]                  # (n, 2) = shard index, row in shard
    packed = np.zeros((len(rows), cap, packed_width), dtype=np.float32)
    globals_ = np.zeros((len(rows), global_width), dtype=np.float32)

    order = np.argsort(where[:, 0], kind="stable")
    shard_ids = where[order, 0]
    boundaries = np.searchsorted(shard_ids, np.arange(len(files) + 1))
    opened = 0
    for shard in range(len(files)):
        lo, hi = boundaries[shard], boundaries[shard + 1]
        if lo == hi:
            continue
        opened += 1
        take = order[lo:hi]
        with np.load(files[shard]) as blob:
            tokens = blob["tokens"][where[take, 1]]
            add = blob["add_info"][where[take, 1]]
            glob = blob["globals"][where[take, 1]]
        packed[take] = np.concatenate([tokens, add], axis=2)
        globals_[take] = glob
    return {"packed": packed, "globals": globals_, "shards_opened": opened,
            "rows": len(rows)}
