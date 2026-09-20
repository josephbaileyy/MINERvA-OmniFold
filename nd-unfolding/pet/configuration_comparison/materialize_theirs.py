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
                rows: np.ndarray, pass_reco: np.ndarray, cap: int = 33,
                packed_width: int = 10, global_width: int = 16,
                ) -> dict[str, np.ndarray]:
    """Packed tokens and globals for `rows` of the inventory, in that order.

    `pass_reco` is REQUIRED, because the two kinds of unmatched row are not the
    same thing. An unmatched **pass_reco** row is an event his arm cannot see
    and ours can, and that is an error. An unmatched **!pass_reco** row is
    expected: the event failed reconstruction, so no reconstructed object exists
    to build a token from, and it enters the comparison through the truth leg.

    An earlier version raised on ANY -1. The join legitimately produces 19.9M of
    them on the signal leg, so the first tuning task would have died minutes
    after the join passed its gate.

    Every `!pass_reco` row comes back ZERO, matched or not, via `zero_non_reco`
    -- the same rule the production loader applies to ours.
    """
    import theirs_loader_substitution as tls

    row_index = np.asarray(row_index)
    reco = np.asarray(pass_reco, dtype=bool)
    if reco.shape[0] != row_index.shape[0]:
        raise ValueError(
            f"pass_reco has {reco.shape[0]} rows and row_index "
            f"{row_index.shape[0]}; both index the same inventory")
    rows = np.asarray(rows)
    selected = row_index[rows]
    reco_ok = reco[rows]
    missing_with_reco = int(((selected < 0) & reco_ok).sum())
    if missing_with_reco:
        raise ValueError(
            f"{missing_with_reco} of {int(reco_ok.sum())} requested pass_reco "
            "rows have no built input; resolve the join before materialising")

    present = selected >= 0
    where = origin[np.where(present, selected, 0)]  # (n, 2) shard, row in shard
    packed = np.zeros((len(rows), cap, packed_width), dtype=np.float32)
    globals_ = np.zeros((len(rows), global_width), dtype=np.float32)

    order = np.argsort(np.where(present, where[:, 0], -1), kind="stable")
    order = order[present[order]]
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
    # HIS FEATURES, not the intermediate the shards store. The build writes
    # `[px, py, pz, log E, pid]` and raw millimetre positions, which is what
    # his `preprocessing` holds BEFORE `convert_to_eta_phi_pt` and
    # `preprocess_coords`. Feeding that to the model is not his configuration,
    # and measured (job 58602446) it diverges: raw momenta reach 8.2e4, the
    # first fit returned `Last val loss nan`, and the engine refused 10,000
    # non-finite logits.
    import theirs_token_schema as tts

    packed = tts.convert_packed(packed).astype(np.float32)
    packed, globals_ = tls.zero_non_reco(packed, globals_, reco_ok)
    return {"packed": packed, "globals": globals_, "shards_opened": opened,
            "rows": len(rows),
            "rows_without_reco": int((~reco_ok).sum()),
            "unmatched_without_reco": int(((selected < 0) & ~reco_ok).sum())}
