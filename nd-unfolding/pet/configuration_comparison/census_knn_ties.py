"""Exact coordinate ties among REAL tokens, on the production cloud.

Why this is a gate and not a curiosity. The local block picks each token's `K`
nearest neighbours with `top_k`. When two candidate neighbours sit at exactly the
same coordinates, which one lands in the top-k is implementation-defined, and two
engines -- or two compilations of one engine -- may choose differently. The
downstream values are then different neighbours' features, not a round-off
difference, and no tolerance covers it.

Padded tokens all sit at the same place by construction and tie with each other
constantly. That is harmless: their contributions are multiplied by a zero mask.
A tie between two REAL tokens is the one that matters, and this counts it on the
real inventory rather than on a synthetic fixture where it never occurred.

Method, vectorized so it can cover the whole inventory rather than a sample: the
two coordinate columns of each token are reinterpreted as their raw float32 bit
patterns and packed into one uint64 key, so "exactly equal" is exact rather than a
tolerance. Padded slots get a unique key each, so they cannot tie with anything.
Keys are sorted within each event and adjacent equal pairs are counted.

`-0.0 == 0.0` in arithmetic but differs in bits, so negative zero is normalized
first: two tokens at (0.0, -0.0) and (0.0, 0.0) ARE at the same place and must be
counted as a tie.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

CHUNK = 200_000


def _keys(coords: np.ndarray, real: np.ndarray, offset: int) -> np.ndarray:
    """One uint64 key per token; padded slots get unique keys so they never tie."""
    flat = np.ascontiguousarray(coords.astype(np.float32))
    flat[flat == 0.0] = 0.0                       # normalize -0.0 to +0.0
    bits = flat.view(np.uint32).astype(np.uint64)
    key = (bits[..., 0] << np.uint64(32)) | bits[..., 1]
    rows, tokens = key.shape
    unique = (np.uint64(1) << np.uint64(63)) + np.arange(
        offset, offset + rows * tokens, dtype=np.uint64).reshape(rows, tokens)
    return np.where(real, key, unique)


# `fullevent_fps_dataloader._scale_clean`, replicated rather than imported so this
# runs without TensorFlow. Division by a constant preserves exact equality, so it
# cannot destroy a tie -- but `nan_to_num` maps a non-finite coordinate to 0.0 and
# CAN create one, between a token whose coordinate was NaN and a token genuinely
# at zero. The census therefore runs on the CLEANED coordinates, which is what the
# k-NN actually sees.
LOADER_SCALE = 1000.0


def _scale_clean(a: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(a, np.float32) / LOADER_SCALE,
                         nan=0.0, posinf=0.0, neginf=0.0)


# The three token clouds, by their ACTUAL array names in the production dump. The
# data leg is `measured_pc`, not `data_part_reco`; guessing the name by prefix
# would have silently censused two inventories out of three and reported the
# result as the inventory's.
PRODUCTION_CLOUDS = {
    "mc_signal_reco": "part_reco",
    "mc_background": "bkg_part_reco",
    "data": "measured_pc",
}


def _boundary_ties(coords: np.ndarray, real: np.ndarray, k: int) -> tuple[int, int]:
    """Ties that could actually change a neighbour SET, and events at risk.

    A tie only matters if it straddles the k-th boundary. Inside the selected
    set the local block REDUCES BY SUM, which is order-independent up to
    round-off, so swapping two equidistant neighbours that are both selected
    changes nothing that a tolerance does not already cover. What changes the
    mathematics is one tied token being selected and its twin excluded, and that
    requires the event to have MORE real tokens than the centre can take.

    For each centre, distances to the other real tokens are sorted and the k-th
    and (k+1)-th compared. Padded tokens are pushed to infinity so they can
    never occupy a neighbour slot.
    """
    rows, tokens, _ = coords.shape
    diff = coords[:, :, None, :] - coords[:, None, :, :]
    distance = np.sum(diff * diff, axis=-1)
    pair_real = real[:, :, None] & real[:, None, :]
    distance = np.where(pair_real, distance, np.inf)
    eye = np.eye(tokens, dtype=bool)[None, :, :]
    distance = np.where(eye, np.inf, distance)           # drop self
    ordered = np.sort(distance, axis=2)
    n_real = real.sum(axis=1)
    # A boundary exists only where a centre has more than k other real tokens.
    has_boundary = (n_real[:, None] - 1 > k) & real
    if k >= tokens - 1:
        return 0, 0
    straddles = (ordered[:, :, k - 1] == ordered[:, :, k]) & np.isfinite(
        ordered[:, :, k]) & has_boundary
    return int(straddles.sum()), int(straddles.any(axis=1).sum())


def census(path: Path, prefixes: list[str], coord_columns: tuple[int, int],
           mask_column: int, limit: int | None = None,
           clean: bool = True, k_values: tuple[int, ...] = (3, 10)) -> dict[str, Any]:
    report: dict[str, Any] = {
        "inventory": str(path),
        "coordinate_columns": list(coord_columns),
        "mask_column": mask_column,
        "mask_rule": f"token is REAL when column {mask_column} != 0",
        "cleaned": clean,
        "clean_rule": ("coordinates pass through the loader's `_scale_clean` "
                       "(/1000, non-finite -> 0) before comparison, because that "
                       "is what the k-NN sees and because nan_to_num can CREATE "
                       "a tie") if clean else "raw coordinates",
        "chunk": CHUNK,
        "blocks": {},
    }
    with np.load(path, mmap_mode="r") as blob:
        available = set(blob.files)
        for prefix in prefixes:
            name = PRODUCTION_CLOUDS.get(prefix, prefix)
            if name not in available:
                report["blocks"][prefix] = {"present": False}
                continue
            array = blob[name]
            rows = array.shape[0] if limit is None else min(limit, array.shape[0])
            tie_pairs = 0
            events_with_ties = 0
            real_tokens = 0
            offset = 0
            boundary = {k: [0, 0] for k in k_values}
            for start in range(0, rows, CHUNK):
                stop = min(start + CHUNK, rows)
                block = np.asarray(array[start:stop])
                if clean:
                    block = _scale_clean(block)
                coords = block[:, :, list(coord_columns)]
                real = block[:, :, mask_column] != 0
                real_tokens += int(real.sum())
                key = _keys(coords, real, offset)
                offset += key.size
                ordered = np.sort(key, axis=1)
                equal = ordered[:, 1:] == ordered[:, :-1]
                per_event = equal.sum(axis=1)
                tie_pairs += int(per_event.sum())
                events_with_ties += int((per_event > 0).sum())
                # EVERY event, not only those with a coordinate tie. Two tokens
                # at DIFFERENT coordinates can be exactly EQUIDISTANT from a
                # centre -- (+4, -4) is the simplest case -- and that is the
                # ambiguity top-k actually sees. Filtering to coordinate ties
                # would measure a subset and report it as the rate.
                for k in k_values:
                    centres, events = _boundary_ties(coords, real, k)
                    boundary[k][0] += centres
                    boundary[k][1] += events
            report["blocks"][prefix] = {
                "present": True,
                "array": name,
                "rows_scanned": int(rows),
                "rows_total": int(array.shape[0]),
                "real_tokens": real_tokens,
                "real_token_tie_pairs": tie_pairs,
                "events_with_at_least_one_tie": events_with_ties,
                "fraction_of_events_with_a_tie": (events_with_ties / rows) if rows else 0.0,
                "boundary_straddling_by_k": {
                    str(k): {"centres": boundary[k][0], "events": boundary[k][1]}
                    for k in k_values},
                "boundary_note": (
                    "a tie changes the neighbour SET only when it straddles the "
                    "k-th boundary; within the selected set the block sums, which "
                    "is order-independent up to round-off"),
            }
    total = sum(b.get("real_token_tie_pairs", 0) for b in report["blocks"].values())
    report["total_real_token_tie_pairs"] = total
    consequential = {
        str(k): sum(b.get("boundary_straddling_by_k", {}).get(str(k), {}).get("centres", 0)
                    for b in report["blocks"].values())
        for k in k_values}
    report["consequential_by_k"] = consequential
    report["k_values"] = list(k_values)
    report["consequential_verdict"] = (
        "NO tie can change a neighbour set at any k measured: every tie lies "
        "inside a selected set, where the block sums"
        if all(v == 0 for v in consequential.values()) else
        f"ties straddle the k-th boundary: {consequential}. Those events' "
        "neighbour SETS are engine-defined and must be resolved, not bounded"
    )
    report["verdict"] = (
        "NO consequential ties: top-k ordering is determined by the coordinates "
        "alone on this inventory" if total == 0 else
        "TIES PRESENT: top-k ordering is engine-defined for the affected events, "
        "and the comparison must either break ties deterministically or bound the "
        "effect before training"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--prefixes", default="mc_signal_reco,mc_background,data",
                        help="inventory names from PRODUCTION_CLOUDS, or raw "
                             "array names")
    parser.add_argument("--coord-columns", default="1,2",
                        help="our incumbent's reco coord_idx")
    parser.add_argument("--mask-column", type=int, default=0,
                        help="our loader masks on energy, column 0")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--k", default="3,10",
                        help="our incumbent's K=3 and his K=10")
    parser.add_argument("--raw", action="store_true",
                        help="skip the loader's _scale_clean; reports what the "
                             "dump holds rather than what the k-NN sees")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    columns = tuple(int(c) for c in args.coord_columns.split(","))
    if len(columns) != 2:
        raise SystemExit("--coord-columns needs exactly two")
    report = census(args.inventory, args.prefixes.split(","), columns,
                    args.mask_column, args.limit, clean=not args.raw,
                    k_values=tuple(int(v) for v in args.k.split(",")))
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    for name, block in report["blocks"].items():
        if not block.get("present"):
            print(f"{name}: absent"); continue
        print(f"{name}: {block['real_token_tie_pairs']:,} tie pairs over "
              f"{block['real_tokens']:,} real tokens in {block['rows_scanned']:,} "
              f"events ({block['fraction_of_events_with_a_tie']:.3%} of events)")
    print(report["verdict"])
    print(report["consequential_verdict"])


if __name__ == "__main__":
    main()
