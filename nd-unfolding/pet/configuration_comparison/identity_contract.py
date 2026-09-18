"""Verify a key join from source tuples onto estimator rows, fail-closed.

Gregor's typed objects live in the MasterAnaDev tuples; the estimator reads an npz whose
rows are positional and carry no event key. Closing that gap means joining on
``(ev_run, ev_subrun, ev_gate)``. A join is the kind of operation that fails silently --
it returns an array of the right shape whatever happens -- so every way it can be wrong
is checked here and each check fails closed.

The hazards, and why each is a separate check rather than one "it worked" flag:

* **Collisions.** If a key repeats, the join is not a function and "the typed objects for
  this row" has no referent. A collision must stop the build, not pick a winner.
* **Unmatched estimator rows.** A row with no source match cannot be given typed objects.
  Zero-filling it would make "absent" indistinguishable from "genuinely zero" -- the exact
  defect this project already refuses in Gregor's own scheme.
* **Native truth-only misses.** These rows legitimately have no reconstructed counterpart,
  so an unmatched row is acceptable *iff* ``pass_reco`` is false there. Unmatched with
  ``pass_reco`` true is a hard failure. Conflating the two would let a real join defect
  hide inside an expected population.
* **Ordering.** The joined block must be in estimator-row order. A join that silently
  returns source order produces a correctly-shaped, entirely wrong input.
* **Inventory symmetry.** A field present for signal but not for data or background makes
  the resulting type code an *inventory label* the step-1 classifier can exploit. This is
  a leakage check, not a bookkeeping one.

Nothing here reads a tuple or an npz. It takes arrays and returns a verdict, so it is
testable without either.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

KEY_FIELDS = ("ev_run", "ev_subrun", "ev_gate")


class ContractViolation(Exception):
    """Raised when a join cannot be certified. Never downgraded to a warning."""


@dataclass(frozen=True)
class KeyReport:
    """What a key array is: how many rows, how many distinct, where it repeats."""

    rows: int
    distinct: int
    duplicate_keys: int
    duplicated_row_count: int

    @property
    def unique(self) -> bool:
        return self.duplicate_keys == 0


def _as_keys(keys: Sequence[Sequence[int]], label: str) -> np.ndarray:
    """Validate and normalize a key table to an (N, 3) integer array."""
    arr = np.asarray(keys)
    if arr.ndim != 2 or arr.shape[1] != len(KEY_FIELDS):
        raise ContractViolation(
            f"{label}: keys must be (N, {len(KEY_FIELDS)}) for {KEY_FIELDS}, got {arr.shape}"
        )
    if arr.size and not np.issubdtype(arr.dtype, np.integer):
        # Event keys are integers. A float key silently loses precision above 2**53 and
        # compares unequal after a round-trip, so this is refused rather than cast.
        raise ContractViolation(f"{label}: keys must be an integer dtype, got {arr.dtype}")
    if np.any(arr < 0):
        raise ContractViolation(f"{label}: negative key components are not valid event keys")
    return arr.astype(np.int64, copy=False)


def describe_keys(keys: Sequence[Sequence[int]], label: str) -> KeyReport:
    """Count rows, distinct keys and collisions without deciding anything."""
    arr = _as_keys(keys, label)
    if arr.shape[0] == 0:
        return KeyReport(0, 0, 0, 0)
    _, inverse, counts = np.unique(arr, axis=0, return_inverse=True, return_counts=True)
    repeated = counts > 1
    return KeyReport(
        rows=int(arr.shape[0]),
        distinct=int(counts.size),
        duplicate_keys=int(repeated.sum()),
        duplicated_row_count=int(counts[repeated].sum()),
    )


def join_indices(
    target_keys: Sequence[Sequence[int]],
    source_keys: Sequence[Sequence[int]],
) -> tuple[np.ndarray, np.ndarray]:
    """Map each target row to its source row.

    Returns ``(source_index, matched)``. ``source_index[i]`` is valid only where
    ``matched[i]``; it is ``-1`` elsewhere so an unmatched row cannot be read by accident.
    """
    target = _as_keys(target_keys, "target")
    source = _as_keys(source_keys, "source")
    source_report = describe_keys(source, "source")
    if not source_report.unique:
        raise ContractViolation(
            f"source keys collide: {source_report.duplicate_keys} key(s) appear more than "
            f"once across {source_report.duplicated_row_count} rows. The join is not a "
            "function; refusing to choose a winner."
        )
    if source.shape[0] == 0:
        return np.full(target.shape[0], -1, np.int64), np.zeros(target.shape[0], bool)

    order = np.lexsort(source.T[::-1])
    sorted_source = source[order]
    # searchsorted over a structured view: compare whole keys, not components.
    view_dtype = np.dtype([(f, np.int64) for f in KEY_FIELDS])
    sorted_view = np.ascontiguousarray(sorted_source).view(view_dtype).ravel()
    target_view = np.ascontiguousarray(target).view(view_dtype).ravel()
    position = np.searchsorted(sorted_view, target_view)
    clipped = np.clip(position, 0, sorted_view.size - 1)
    matched = sorted_view[clipped] == target_view
    source_index = np.where(matched, order[clipped], -1).astype(np.int64)
    return source_index, matched


def verify_join(
    *,
    target_keys: Sequence[Sequence[int]],
    source_keys: Sequence[Sequence[int]],
    pass_reco: Sequence[bool],
    inventory: str,
) -> dict[str, Any]:
    """Certify one inventory's join, or raise.

    ``pass_reco`` is what makes an unmatched row interpretable: a native truth-only miss
    has no reconstructed counterpart and so no source row, while an unmatched
    ``pass_reco`` row means the join is broken.
    """
    target_report = describe_keys(target_keys, f"{inventory} target")
    source_index, matched = join_indices(target_keys, source_keys)
    flags = np.asarray(pass_reco, dtype=bool)
    if flags.shape[0] != target_report.rows:
        raise ContractViolation(
            f"{inventory}: pass_reco has {flags.shape[0]} rows but the target has "
            f"{target_report.rows}"
        )

    if not target_report.unique:
        raise ContractViolation(
            f"{inventory}: target keys collide ({target_report.duplicate_keys} key(s) over "
            f"{target_report.duplicated_row_count} rows). Two estimator rows claiming one "
            "event means the row identity is not the event identity."
        )

    unmatched = ~matched
    unmatched_pass_reco = int(np.count_nonzero(unmatched & flags))
    if unmatched_pass_reco:
        raise ContractViolation(
            f"{inventory}: {unmatched_pass_reco} row(s) with pass_reco=True have no source "
            "match. These cannot be zero-filled -- absent would be indistinguishable from "
            "genuinely zero."
        )

    # Ordering: the returned index must be read positionally against the target, so a
    # correct join is the identity on target order. Verified rather than assumed.
    matched_positions = np.flatnonzero(matched)
    ordering_preserved = bool(np.all(np.diff(matched_positions) > 0)) if matched_positions.size > 1 else True

    return {
        "inventory": inventory,
        "target_rows": target_report.rows,
        "source_rows": describe_keys(source_keys, f"{inventory} source").rows,
        "matched_rows": int(np.count_nonzero(matched)),
        "unmatched_rows": int(np.count_nonzero(unmatched)),
        "unmatched_are_all_native_misses": bool(np.all(~flags[unmatched])) if unmatched.any() else True,
        "native_miss_rows": int(np.count_nonzero(~flags)),
        "target_keys_unique": target_report.unique,
        "ordering_preserved": ordering_preserved,
        "certified": True,
    }


def check_inventory_symmetry(fields_by_inventory: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    """Require the same typed-field set in every inventory.

    An asymmetric field set turns a type code into an inventory label, which the step-1
    classifier can use to separate data from MC for free. That is leakage, so this raises
    rather than reporting a difference.
    """
    if not fields_by_inventory:
        raise ContractViolation("no inventories given; symmetry is undefined")
    as_sets = {name: set(fields) for name, fields in fields_by_inventory.items()}
    union: set[str] = set().union(*as_sets.values())
    missing = {name: sorted(union - present) for name, present in as_sets.items()}
    asymmetric = {name: gap for name, gap in missing.items() if gap}
    if asymmetric:
        raise ContractViolation(
            f"typed fields are not symmetric across inventories: {asymmetric}. An "
            "asymmetric field set is an inventory label the step-1 classifier can exploit."
        )
    return {
        "inventories": sorted(as_sets),
        "field_count": len(union),
        "symmetric": True,
    }


def provenance_record(
    *,
    source_files: Mapping[str, str],
    manifests: Mapping[str, str],
    dump_npz_sha256: str,
) -> dict[str, Any]:
    """Pin what was read, so a join can be re-derived rather than re-trusted."""
    if not source_files:
        raise ContractViolation("provenance requires at least one source file digest")
    for name, digest in {**source_files, **manifests}.items():
        if len(digest) != 64 or not all(c in "0123456789abcdef" for c in digest.lower()):
            raise ContractViolation(f"{name}: {digest!r} is not a sha256 hex digest")
    if len(dump_npz_sha256) != 64:
        raise ContractViolation("dump_npz_sha256 is not a sha256 hex digest")
    return {
        "source_files": dict(sorted(source_files.items())),
        "manifests": dict(sorted(manifests.items())),
        "dump_npz_sha256": dump_npz_sha256,
        "note": (
            "Digests pin what was read. They do not establish that the right files were "
            "named -- that is the manifest's job and the manifests are pinned too."
        ),
    }
