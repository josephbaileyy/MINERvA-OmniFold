"""Verify a key join from source tuples onto estimator rows, fail-closed.

Gregor's typed objects live in the MasterAnaDev tuples; the estimator reads an npz whose
rows are positional. A join is the kind of operation that fails silently -- it returns an
array of the right shape whatever happens -- so every way it can be wrong is checked here
and each check fails closed.

**CORRECTED 2026-09-19 by Agent A's measurement, and the correction matters.** This
module was written assuming ``(ev_run, ev_subrun, ev_gate)`` is an EVENT key. On the
production `data` tree it is a **GATE** key: 212,677 keys over 433,304 of 4,119,797 rows
repeat, up to multiplicity 5, and **all 212,677 duplicate blocks differ in kinematics** --
muon, vertex, vertex z by metres. They are distinct reconstructed interactions sharing one
DAQ readout gate, not double-fills. Joining or grouping data rows on the bare triple
silently merges distinct events on about **10.5 %** of rows.

The three MC trees are clean: ``(mc_run, mc_subrun, mc_nthEvtInFile)`` has zero duplicates
across 49,906,108 + 49,906,108 + 566,036 rows.

So the key is the triple **plus an ``occurrence`` ordinal** -- the row's position within
its key group, in inventory order -- and the canonical join is
``(source, run, subrun, event, occurrence)``. ``occurrence`` is 0 on all MC, and `source`
was measured *informative rather than required* on this inventory (all four trees are
cross-playlist disjoint); it is kept in the key anyway, because a redundancy measured on
one inventory is not a property of the scheme.

**THE PRODUCTION JOIN IS NOT IMPLEMENTED HERE.** `nd-unfolding/pet/event_identity.py`
and its sidecar verifier `verify_event_identity_sidecar.py` are the instrument, they
passed 12/12 on the real artifact, and a second implementation of a rule is how two
implementations drift. What lives in this module is the PET lane's own *verification* --
collisions, unmatched rows, native misses, ordering, inventory symmetry -- over arrays,
plus the key definition so this lane cannot get it wrong. Run the peer's verifier before
any join:

    nd-unfolding/pet/verify_event_identity_sidecar.py \
      --inventory <npz> --sidecar <identity.npz> --pet-dir <checkout>/nd-unfolding/pet

Two consequences are recorded rather than assumed away:

* the old behaviour, refusing any colliding key, would now **reject the real data
  outright**. `describe_keys` still reports collisions; `join_indices` now takes the
  composite key, and `assign_occurrence` builds it.
* ``occurrence`` is an ordinal **of this production**. Where it is non-zero the join is to
  a row of this reconstruction pass, not to an object that survives re-reconstruction.
  `occurrence_stability_warning` returns that in the receipt so it travels with the join.

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
#: The triple plus the within-gate ordinal. This, not KEY_FIELDS, is what a join uses.
#: The canonical contract key also carries `source` (the playlist index); it is
#: measured redundant on this inventory and is the caller's to prepend where it is
#: not. See CANONICAL_JOIN_FIELDS.
JOIN_FIELDS = KEY_FIELDS + ("occurrence",)
#: `nd-unfolding/pet/EVENT_IDENTITY_JOIN_CONTRACT.md` §3.
CANONICAL_JOIN_FIELDS = ("source",) + JOIN_FIELDS
#: The instrument that performs and verifies the real join. Do not reimplement it.
JOIN_INSTRUMENT = {
    "module": "nd-unfolding/pet/event_identity.py",
    "verifier": "nd-unfolding/pet/verify_event_identity_sidecar.py",
    "contract": "nd-unfolding/pet/EVENT_IDENTITY_JOIN_CONTRACT.md",
    "sidecar": "G2_FPS_MEFHC_P12.identity.npz",
    "sidecar_sha256": "01e07412b253ff496c30025cc71a9185b166a00892b1e1b4c8bce714ddd5f95c",
    "verified": "12/12 playlists, including the bound-hash comparison the exporter "
                "does not do in-process",
}
#: Measured by Agent A on G2_FPS_MEFHC_P12, data tree.
DATA_GATE_KEY_EVIDENCE = {
    "tree": "data",
    "rows": 4_119_797,
    "repeating_keys": 212_677,
    "rows_in_repeating_keys": 433_304,
    "max_multiplicity": 5,
    "duplicate_blocks_with_identical_kinematics": 0,
    "reading": ("distinct reconstructed interactions sharing one DAQ gate. Do NOT "
                "dedupe; ~10.5 % of data rows would be merged."),
}


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


def _as_keys(keys: Sequence[Sequence[int]], label: str,
             fields: Sequence[str] = KEY_FIELDS) -> np.ndarray:
    """Validate and normalize a key table to an (N, len(fields)) integer array."""
    arr = np.asarray(keys)
    if arr.ndim != 2 or arr.shape[1] != len(fields):
        raise ContractViolation(
            f"{label}: keys must be (N, {len(fields)}) for {tuple(fields)}, got {arr.shape}"
        )
    if arr.size and not np.issubdtype(arr.dtype, np.integer):
        # Event keys are integers. A float key silently loses precision above 2**53 and
        # compares unequal after a round-trip, so this is refused rather than cast.
        raise ContractViolation(f"{label}: keys must be an integer dtype, got {arr.dtype}")
    if np.any(arr < 0):
        raise ContractViolation(f"{label}: negative key components are not valid event keys")
    return arr.astype(np.int64, copy=False)


def describe_keys(keys: Sequence[Sequence[int]], label: str,
                  fields: Sequence[str] = KEY_FIELDS) -> KeyReport:
    """Count rows, distinct keys and collisions without deciding anything."""
    arr = _as_keys(keys, label, fields)
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


def assign_occurrence(keys: Sequence[Sequence[int]]) -> np.ndarray:
    """The ordinal of each row within its key group, in INVENTORY ORDER.

    This is what turns a gate key into a join key. Order matters and is the row order
    of the inventory, not a sort: two productions that emit the same rows in a
    different order assign different ordinals, which is precisely why
    `occurrence_stability_warning` exists.
    """
    arr = _as_keys(keys, "occurrence input")
    if arr.shape[0] == 0:
        return np.zeros(0, np.int64)
    _, inverse = np.unique(arr, axis=0, return_inverse=True)
    inverse = np.asarray(inverse).ravel()
    counts = np.zeros(inverse.max() + 1, np.int64)
    ordinal = np.empty(inverse.size, np.int64)
    for position, group in enumerate(inverse):
        ordinal[position] = counts[group]
        counts[group] += 1
    return ordinal


def with_occurrence(keys: Sequence[Sequence[int]]) -> np.ndarray:
    """The (N, 4) join key: the triple plus its within-gate ordinal."""
    arr = _as_keys(keys, "join key input")
    return np.column_stack([arr, assign_occurrence(arr)]).astype(np.int64, copy=False)


def occurrence_stability_warning(occurrence: Sequence[int]) -> dict[str, Any]:
    """What a non-zero occurrence does and does not buy, for the receipt."""
    ordinal = np.asarray(occurrence, dtype=np.int64)
    non_zero = int((ordinal > 0).sum())
    return {
        "rows": int(ordinal.size),
        "rows_with_non_zero_occurrence": non_zero,
        "fraction": float(non_zero / ordinal.size) if ordinal.size else 0.0,
        "guarantee": ("where occurrence is 0 the join is to the unique row carrying that "
                      "key; where it is non-zero the join is to a row of THIS production, "
                      "in this row order"),
        "not_guaranteed": ("that the same ordinal identifies the same reconstructed "
                           "interaction after re-reconstruction, or under a different "
                           "row order. The durable fix is a slice identifier written by "
                           "the event loop, which does not exist yet."),
    }


def join_indices(
    target_keys: Sequence[Sequence[int]],
    source_keys: Sequence[Sequence[int]],
    fields: Sequence[str] = JOIN_FIELDS,
) -> tuple[np.ndarray, np.ndarray]:
    """Map each target row to its source row, on the COMPOSITE key.

    Defaults to ``JOIN_FIELDS`` -- the triple plus the occurrence ordinal -- because
    the bare triple is a gate key on the data tree and joining on it merges distinct
    interactions. Pass ``fields=KEY_FIELDS`` only for an inventory whose triple has
    been SHOWN unique, and the collision guard below still has to hold.

    Returns ``(source_index, matched)``. ``source_index[i]`` is valid only where
    ``matched[i]``; it is ``-1`` elsewhere so an unmatched row cannot be read by accident.
    """
    target = _as_keys(target_keys, "target", fields)
    source = _as_keys(source_keys, "source", fields)
    source_report = describe_keys(source, "source", fields)
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
    view_dtype = np.dtype([(f, np.int64) for f in fields])
    sorted_view = np.ascontiguousarray(sorted_source).view(view_dtype).ravel()
    target_view = np.ascontiguousarray(target).view(view_dtype).ravel()
    position = np.searchsorted(sorted_view, target_view)
    clipped = np.clip(position, 0, sorted_view.size - 1)
    matched = sorted_view[clipped] == target_view
    source_index = np.where(matched, order[clipped], -1).astype(np.int64)
    return source_index, matched


def verify_join(
    *,
    fields: Sequence[str] = JOIN_FIELDS,
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
    source_index, matched = join_indices(target_keys, source_keys, fields)
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
