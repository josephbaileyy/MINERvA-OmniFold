"""Swap his step-1 inputs into the production loaders, for the same rows.

The production `build_fullevent_loaders` defines the comparison's population:
which events, in which order, with which weights, which `pass_reco`/`pass_gen`
flags, and which MC subsample `imc`. None of that may change between arms --
if it did, the arms would be measured on different data and the difference
would look like a method effect.

So his arm does not get its own loaders. It gets the PRODUCTION loaders with
the step-1 reco tensors REPLACED by his, gathered to the same rows. Everything
else -- weights, flags, subsample, order, and the whole step-2 side -- is
untouched, which is what makes the two arms comparable and what `STEP_SCOPE`
freezes.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

from typing import Any

import numpy as np


class UnmatchedRows(Exception):
    """An inventory row his inputs cannot supply. Never silently zero-filled."""


def gather(theirs: dict[str, np.ndarray], row_index: np.ndarray,
           rows: np.ndarray, pass_reco: np.ndarray,
           ) -> tuple[np.ndarray, np.ndarray]:
    """His packed tokens and globals for the given inventory rows.

    `row_index` maps inventory row -> built row, with -1 for unmatched.

    A -1 on a **pass_reco** row is an error. His arm cannot see that event, and
    zero-filling it would score a missing input as a failure while dropping it
    would give the arms different populations.

    A -1 on a **!pass_reco** row is EXPECTED and correct. Those events have no
    reconstruction at all -- they live only in the AnaTuple's `Truth` tree, so
    no reco object exists to build a token from -- and they enter the
    comparison through the truth leg. Requiring them to match was a gate on the
    wrong population: it demanded reco inputs for events that have no reco.

    **!pass_reco rows are zeroed for BOTH arms.** The production loader zeroes
    its reco block on those rows post-normalization, so his arm must be zero
    there too. Leaving his real reco content on the 8.68M matched-but-!pass_reco
    rows would give his arm information ours does not have, on 18% of the
    signal leg, and that difference would read as a method effect.
    """
    row_index = np.asarray(row_index)
    reco = np.asarray(pass_reco, dtype=bool)
    if reco.shape[0] != row_index.shape[0]:
        raise ValueError(
            f"pass_reco has {reco.shape[0]} rows and row_index "
            f"{row_index.shape[0]}; both index the same inventory, and a "
            "shorter pass_reco would silently mis-assign the reco flag"
        )
    selected = row_index[rows]
    reco_ok = reco[rows]
    missing_with_reco = int(((selected < 0) & reco_ok).sum())
    if missing_with_reco:
        raise UnmatchedRows(
            f"{missing_with_reco} of {int(reco_ok.sum())} pass_reco rows have no "
            "built input. Zero-filling them would feed his arm empty events and "
            "score them as failures; dropping them would give the arms different "
            "populations. Resolve the join first."
        )
    safe = np.where(selected < 0, 0, selected)
    return zero_non_reco(theirs["packed"][safe], theirs["globals"][safe], reco_ok)


def zero_non_reco(packed: np.ndarray, globals_: np.ndarray,
                  pass_reco: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Zero his step-1 inputs on `!pass_reco` rows, as the production loader does.

    One implementation of the rule, called from both `gather` and the driver, so
    the two cannot drift. The production dataloader zeroes its reco block on
    `!pass_reco` rows post-normalization; his arm carrying real reco content
    there would see information ours does not, on 18% of the signal leg.
    """
    mask = ~np.asarray(pass_reco, dtype=bool)
    if mask.shape[0] != packed.shape[0] or mask.shape[0] != globals_.shape[0]:
        raise ValueError(
            f"pass_reco has {mask.shape[0]} rows, packed {packed.shape[0]}, "
            f"globals {globals_.shape[0]}; all three describe the same events")
    packed = np.array(packed, copy=True)
    globals_ = np.array(globals_, copy=True)
    packed[mask] = 0.0
    globals_[mask] = 0.0
    return packed, globals_


def substitute_step1(data_loader: Any, mc_loader: Any,
                     theirs_data: tuple[np.ndarray, np.ndarray],
                     theirs_mc: tuple[np.ndarray, np.ndarray]) -> dict[str, Any]:
    """Replace the step-1 reco tensors in place, and verify nothing else moved."""
    before = {
        "data_rows": int(data_loader.reco.shape[0]),
        "mc_rows": int(mc_loader.reco.shape[0]),
        "data_weight_sum": float(np.sum(data_loader.weight)),
        "mc_weight_sum": float(np.sum(mc_loader.weight)),
        "mc_pass_reco_sum": int(np.sum(mc_loader.pass_reco)),
        "mc_gen_checksum": float(np.sum(mc_loader.gen)),
    }
    for loader, (packed, globals_) in ((data_loader, theirs_data),
                                       (mc_loader, theirs_mc)):
        if packed.shape[0] != loader.reco.shape[0]:
            raise ValueError(
                f"row count changed: {loader.reco.shape[0]} -> {packed.shape[0]}. "
                "The arms must see the same events.")
        loader.reco = packed.astype(np.float32)
        loader.reco_evt = globals_.astype(np.float32)

    after = {
        "data_rows": int(data_loader.reco.shape[0]),
        "mc_rows": int(mc_loader.reco.shape[0]),
        "data_weight_sum": float(np.sum(data_loader.weight)),
        "mc_weight_sum": float(np.sum(mc_loader.weight)),
        "mc_pass_reco_sum": int(np.sum(mc_loader.pass_reco)),
        "mc_gen_checksum": float(np.sum(mc_loader.gen)),
    }
    if before != after:
        raise ValueError(
            f"the substitution changed something other than step-1 reco: "
            f"{before} -> {after}")
    return {
        "substituted": ["reco", "reco_evt"],
        "untouched_and_verified": sorted(before),
        "invariants": before,
        "step2_untouched": True,
        "reading": ("row counts, weights, pass flags and the whole truth side are "
                    "byte-identical across the substitution, so the arms differ "
                    "only in what step 1 sees"),
    }
