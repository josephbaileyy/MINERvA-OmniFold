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
           rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """His packed tokens and globals for the given inventory rows.

    `row_index` maps inventory row -> built row, with -1 for unmatched. A -1
    reaching this function is an error rather than a zero-filled event: an event
    his arm cannot see is not an event his arm scores badly on, it is an event
    the comparison must not include for either arm.
    """
    selected = np.asarray(row_index)[rows]
    missing = int((selected < 0).sum())
    if missing:
        raise UnmatchedRows(
            f"{missing} of {len(rows)} inventory rows have no built input. "
            "Zero-filling them would feed his arm empty events and score them "
            "as failures; dropping them would give the arms different "
            "populations. Resolve the join first."
        )
    packed = theirs["packed"][selected]
    globals_ = theirs["globals"][selected]
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
