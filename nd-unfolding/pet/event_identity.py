#!/usr/bin/env python3
"""Event-identity contract for the G2 full-event inventories: field names, exact keying,
uniqueness measurement, and the source (playlist) resolution used when identity alone does not
separate rows.

PURE: no ROOT, no TensorFlow, no I/O. Login-node importable and unit-testable with fake arrays.
The PyROOT readers live in `export_event_identity.py` (row-aligned sidecar export) and
`audit_event_identity.py` (uniqueness measurement); both import their definitions from here so the
contract has exactly one implementation.

WHAT THE SOURCE ROOTS CARRY (measured 2026-09-18 on the production merged G2 ROOT
`nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root`, sha256
9a16331f1c02103e3b5de5e6c00139aa39393ee11eb34881bea0b9a890344e2f per its merge receipt):

  tree              entries       identity branches (all Int_t)
  mc_truth_denom    49,906,108    mc_run, mc_subrun, mc_nthEvtInFile
  mc_signal_reco    49,906,108    mc_run, mc_subrun, mc_nthEvtInFile
  mc_background        566,036    mc_run, mc_subrun, mc_nthEvtInFile
  data               4,119,797    ev_run, ev_subrun, ev_gate

They are written by `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp` under
`MNV101_DUMP_POINTCLOUD`, which is the flag the G2 FPS production used. This CORRECTS
`fullevent_fps_dataloader.inventory_order_hash`'s docstring ("The FPS ROOTs carry NO stable event
keys"): they do. The order hash remains a valid ORDER witness and this module does not replace it;
it adds the identity the order hash was standing in for.

KEYING. `pack_identity` uses BIT-FIELD packing with declared widths, not the decimal packing of the
C++ `makeEventKey` (`(run*1e8 + subrun)*1e8 + nth`). The decimal form OVERFLOWS uint64 for real
MINERvA run numbers -- run 111353 gives 1.11e21 against a uint64 ceiling of 1.84e19 -- so it is a
wrapped key, injective only by arithmetic accident of the observed ranges. Whether that accident
holds on the production files is a MEASUREMENT, reported by `audit_event_identity.py` as
`cxx_wrapped_key_collisions`; `cxx_wrapped_key` below reproduces the C++ value exactly (including
the wrap) so that measurement compares like with like. Nothing here depends on the answer: the
bit-field key range-checks every field and raises rather than wrapping.
"""
from __future__ import annotations

import numpy as np

IDENTITY_CONTRACT_VERSION = "event-identity-v1"

# --- Identity fields, per tree role ----------------------------------------------------------
# MC and data identities are DIFFERENT TUPLES over different namespaces. They are never mixed and
# never compared: an `ev_gate` is a DAQ gate number, an `mc_nthEvtInFile` is an index within a
# generated file. "run/subrun/gate" names the data tuple only.
MC_IDENTITY_FIELDS = ("mc_run", "mc_subrun", "mc_nthEvtInFile")
DATA_IDENTITY_FIELDS = ("ev_run", "ev_subrun", "ev_gate")

TREE_IDENTITY_FIELDS = {
    "mc_truth_denom": MC_IDENTITY_FIELDS,
    "mc_signal_reco": MC_IDENTITY_FIELDS,
    "mc_background": MC_IDENTITY_FIELDS,
    "data": DATA_IDENTITY_FIELDS,
}

# Inventory -> (tree, export key prefix). The three inventories the G2 NPZ carries, plus the
# truth denominator, which is not an NPZ inventory but IS a join endpoint (see the contract doc).
INVENTORY_TREE = {"sig": "mc_signal_reco", "data": "data", "bkg": "mc_background"}

# --- Bit-field packing -----------------------------------------------------------------------
# Widths are a DECLARED contract, checked against every value packed. They are not derived from a
# sample: a width inferred from the data would silently widen the day a larger run appears, which
# is the failure this check exists to catch. 24/16/24 covers run < 16.7M, subrun < 65536,
# nth/gate < 16.7M and leaves the top 0 bits of a signed int64 free, so the key is a safe int64.
RUN_BITS, SUBRUN_BITS, EVENT_BITS = 24, 16, 24
KEY_BITS = RUN_BITS + SUBRUN_BITS + EVENT_BITS          # 64 -> packed into uint64
_RUN_MAX = (1 << RUN_BITS) - 1
_SUBRUN_MAX = (1 << SUBRUN_BITS) - 1
_EVENT_MAX = (1 << EVENT_BITS) - 1


class IdentityRangeError(ValueError):
    """A run/subrun/event value does not fit the declared bit-field width (fail closed)."""


def pack_identity(run, subrun, event):
    """Pack (run, subrun, event) into one exact uint64 key, element-wise.

    `event` is `mc_nthEvtInFile` for an MC inventory and `ev_gate` for data. Every field is
    range-checked; an out-of-range or negative value raises `IdentityRangeError` rather than
    wrapping, so a key returned by this function is injective on its inputs by construction.

    Parameters
    ----------
    run, subrun, event : array_like of int
        Broadcastable integer arrays (or scalars) of identity components.

    Returns
    -------
    numpy.ndarray of uint64
        The packed keys, same shape as the broadcast inputs.

    Raises
    ------
    IdentityRangeError
        If any component is negative or exceeds its declared width.
    """
    run = np.asarray(run, dtype=np.int64)
    subrun = np.asarray(subrun, dtype=np.int64)
    event = np.asarray(event, dtype=np.int64)
    for name, arr, hi in (("run", run, _RUN_MAX), ("subrun", subrun, _SUBRUN_MAX),
                          ("event", event, _EVENT_MAX)):
        if arr.size and (int(arr.min()) < 0 or int(arr.max()) > hi):
            raise IdentityRangeError(
                f"[IDENTITY] {name} out of declared range [0, {hi}]: "
                f"observed [{int(arr.min())}, {int(arr.max())}]. The packed key would not be "
                f"injective; widen the declared bit fields deliberately, do not wrap.")
    return ((run.astype(np.uint64) << np.uint64(SUBRUN_BITS + EVENT_BITS))
            | (subrun.astype(np.uint64) << np.uint64(EVENT_BITS))
            | event.astype(np.uint64))


def unpack_identity(key):
    """Inverse of `pack_identity`; returns (run, subrun, event) as int64 arrays."""
    key = np.asarray(key, dtype=np.uint64)
    run = (key >> np.uint64(SUBRUN_BITS + EVENT_BITS)).astype(np.int64)
    subrun = ((key >> np.uint64(EVENT_BITS)) & np.uint64(_SUBRUN_MAX)).astype(np.int64)
    event = (key & np.uint64(_EVENT_MAX)).astype(np.int64)
    return run, subrun, event


def cxx_wrapped_key(run, subrun, event):
    """Reproduce `runEventLoopOmniFold.cpp::makeEventKey` EXACTLY, wrap included.

    The C++ computes `(run*1e8 + subrun)*1e8 + nth` in uint64. For MINERvA run numbers that
    product exceeds 2**64 and wraps. This function is here so the audit can measure whether the
    wrap actually collides on the production files -- it is a measurement instrument, never the
    key this contract exports. Do not join on it.
    """
    run = np.asarray(run, dtype=np.uint64)
    subrun = np.asarray(subrun, dtype=np.uint64)
    event = np.asarray(event, dtype=np.uint64)
    with np.errstate(over="ignore"):
        return (run * np.uint64(100000000) + subrun) * np.uint64(100000000) + event


# --- Export key names ------------------------------------------------------------------------
def export_keys(prefix):
    """Return the NPZ key names an inventory's identity block occupies, for `prefix` in
    {"sig", "data", "bkg"}."""
    return {
        "fields": f"{prefix}_identity_fields",      # (3,) unicode: the branch names, in column order
        "values": f"{prefix}_event_id",             # (n, 3) int32: the raw identity columns
        "source": f"{prefix}_event_source",         # (n,) int16: index into identity_source_labels
        "occurrence": f"{prefix}_event_occurrence",  # (n,) int32: ordinal within (source, key)
        "key": f"{prefix}_event_key",               # (n,) uint64: pack_identity of the 3 columns
        "digest": f"{prefix}_event_id_hash",        # order+content digest of the block
        "bound_to": f"{prefix}_bound_identity_hash",  # the target NPZ's own inventory order hash
    }


SOURCE_LABELS_KEY = "identity_source_labels"        # (n_sources,) unicode playlist labels
CONTRACT_VERSION_KEY = "identity_contract_version"
UNIQUENESS_KEY = "identity_uniqueness"              # the verdict string carried with the export

# Verdicts. The export records which one the producing audit measured, so a consumer never has to
# assume uniqueness it did not check.
UNIQUE_WITHOUT_SOURCE = "unique-without-source"     # (run, subrun, event) alone separates all rows
UNIQUE_WITH_SOURCE = "unique-with-source"           # (source, run, subrun, event) is needed
NOT_UNIQUE = "not-unique"                           # duplicates survive even with source
VERDICTS = (UNIQUE_WITHOUT_SOURCE, UNIQUE_WITH_SOURCE, NOT_UNIQUE)


# --- Source resolution for concatenated (hadd) files -------------------------------------------
def source_index_from_boundaries(counts):
    """Per-row source index for a tree that is the ORDERED CONCATENATION of per-source trees.

    `hadd`/TFileMerger appends each input's entries in input order, so row `i` of the merged tree
    belongs to source `s` where `i` falls in `s`'s half-open count range. `counts` must be the
    per-source entry counts of THAT tree in the merge's declared input order (the
    `ordered_inputs` list of the merge receipt), not a directory listing -- an alphabetical
    re-ordering produces a plausible, wrong answer with no symptom.

    Parameters
    ----------
    counts : sequence of int
        Per-source entry counts, in merge input order.

    Returns
    -------
    numpy.ndarray of int16
        Length ``sum(counts)``; entry ``i`` is the index of the source owning merged row ``i``.
    """
    counts = [int(c) for c in counts]
    if any(c < 0 for c in counts):
        raise ValueError(f"[IDENTITY] negative source count in {counts}")
    if len(counts) > np.iinfo(np.int16).max:
        raise ValueError(f"[IDENTITY] {len(counts)} sources exceeds the int16 source-index width")
    return np.repeat(np.arange(len(counts), dtype=np.int16), counts)


def check_boundaries(counts, n_rows):
    """Fail closed unless the per-source counts sum to the merged tree's own entry count."""
    total = int(sum(int(c) for c in counts))
    if total != int(n_rows):
        raise ValueError(
            f"[IDENTITY] source boundaries sum to {total} but the tree has {n_rows} entries. The "
            f"merge input list does not describe this file; row->source assignment would be "
            f"silently wrong.")
    return True


# --- Uniqueness measurement --------------------------------------------------------------------
def uniqueness_report(keys, sources=None, n_examples=5):
    """Measure duplication of an identity key array, optionally after qualifying it by source.

    Reports the count of rows that share a key with another row (`n_duplicated_rows`), not the
    count of distinct offending keys -- a single key repeated 1102 times is 1102 rows and 1 key,
    and both numbers are carried because either alone misreads the join hazard.

    Parameters
    ----------
    keys : array_like of uint64
        Packed identity keys, one per row.
    sources : array_like of int, optional
        Per-row source index. When given, uniqueness is measured over the (source, key) pair.
    n_examples : int
        How many colliding keys to include verbatim in the report.

    Returns
    -------
    dict
        ``n_rows``, ``n_distinct``, ``n_duplicated_keys``, ``n_duplicated_rows``,
        ``max_multiplicity``, ``is_unique``, ``examples``.
    """
    keys = np.asarray(keys, dtype=np.uint64).ravel()
    if sources is None:
        probe = keys
    else:
        sources = np.asarray(sources, dtype=np.int64).ravel()
        if sources.shape != keys.shape:
            raise ValueError(f"[IDENTITY] sources {sources.shape} != keys {keys.shape}")
        probe = np.empty(keys.size, dtype=[("s", np.int64), ("k", np.uint64)])
        probe["s"] = sources
        probe["k"] = keys
    uniq, counts = np.unique(probe, return_counts=True)
    dup = counts > 1
    n_dup_keys = int(dup.sum())
    examples = []
    if n_dup_keys:
        for u, c in zip(uniq[dup][:n_examples], counts[dup][:n_examples]):
            k = np.uint64(u["k"]) if sources is not None else np.uint64(u)
            run, subrun, event = (int(v) for v in unpack_identity(k))
            row = {"run": run, "subrun": subrun, "event": event, "multiplicity": int(c)}
            if sources is not None:
                row["source"] = int(u["s"])
            examples.append(row)
    return {
        "n_rows": int(keys.size),
        "n_distinct": int(uniq.size),
        "n_duplicated_keys": n_dup_keys,
        "n_duplicated_rows": int(counts[dup].sum()) if n_dup_keys else 0,
        "max_multiplicity": int(counts.max()) if counts.size else 0,
        "is_unique": n_dup_keys == 0,
        "examples": examples,
    }


def occurrence_index(keys, sources=None):
    """0-based ordinal of each row among the rows sharing its (source, key), in ARRAY ORDER.

    This is the "additional event identity" of the contract: it is what makes
    ``(source, run, subrun, event, occurrence)`` unique by construction even where the tuple the
    files carry is not. It is 0 everywhere when the key is already unique, so carrying it costs
    nothing in the unique case and is the only thing that separates rows in the non-unique one.

    It MUST be computed over the FULL source tree in entry order, never over a selected subset:
    an ordinal computed after selection changes when the selection changes, which would make a
    row's identity a function of the cut rather than of the event.

    Parameters
    ----------
    keys : array_like of uint64
        Packed identity keys in source-tree entry order.
    sources : array_like of int, optional
        Per-row source index; occurrences are counted within a source.

    Returns
    -------
    numpy.ndarray of int32
        The per-row occurrence ordinals, in the input order.
    """
    keys = np.asarray(keys, dtype=np.uint64).ravel()
    n = keys.size
    if n == 0:
        return np.zeros(0, dtype=np.int32)
    if sources is None:
        order = np.argsort(keys, kind="stable")
        same = keys[order][1:] == keys[order][:-1]
    else:
        sources = np.asarray(sources, dtype=np.int64).ravel()
        if sources.shape != keys.shape:
            raise ValueError(f"[IDENTITY] sources {sources.shape} != keys {keys.shape}")
        order = np.lexsort((keys, sources))
        same = ((keys[order][1:] == keys[order][:-1])
                & (sources[order][1:] == sources[order][:-1]))
    # Ordinal within each run of equal adjacent entries: a running count that resets at each
    # boundary, computed as (position) - (position of the run's first element).
    pos = np.arange(n, dtype=np.int64)
    boundary = np.concatenate(([True], ~same))
    run_start = np.maximum.accumulate(np.where(boundary, pos, 0))
    ordinal = (pos - run_start).astype(np.int32)
    out = np.empty(n, dtype=np.int32)
    out[order] = ordinal
    return out


def duplicate_block_character(keys, witness):
    """For every key that repeats, do its rows AGREE on `witness`, or differ?

    Identical rows mean an upstream double-fill and the remedy is a dedupe. Differing rows mean
    several distinct physical events share the tuple, and the remedy is more identity -- the two
    have opposite fixes, so a duplication count alone cannot be acted on.

    Parameters
    ----------
    keys : array_like of uint64
    witness : array_like, shape (n, k)
        Per-row witness columns (kinematics, weights) compared exactly.

    Returns
    -------
    dict
        ``n_duplicated_keys``, ``n_blocks_all_identical``, ``n_blocks_with_difference``.
    """
    keys = np.asarray(keys, dtype=np.uint64).ravel()
    witness = np.atleast_2d(np.asarray(witness))
    if witness.shape[0] != keys.size:
        witness = witness.T
    if witness.shape[0] != keys.size:
        raise ValueError(f"[IDENTITY] witness rows {witness.shape} != keys {keys.size}")
    order = np.argsort(keys, kind="stable")
    ks, ws = keys[order], witness[order]
    if ks.size < 2:
        return {"n_duplicated_keys": 0, "n_blocks_all_identical": 0,
                "n_blocks_with_difference": 0}
    same_key = ks[1:] == ks[:-1]
    differs = ~np.all(ws[1:] == ws[:-1], axis=1)
    n_dup_keys = int(np.unique(ks[1:][same_key]).size)
    n_diff = int(np.unique(ks[1:][same_key & differs]).size)
    return {"n_duplicated_keys": n_dup_keys,
            "n_blocks_all_identical": n_dup_keys - n_diff,
            "n_blocks_with_difference": n_diff}


def cross_source_overlap(distinct_by_source):
    """Pairwise and global collision counts between the DISTINCT key sets of different sources.

    A nonzero pairwise overlap is what forces `source` into the identity: two playlists reusing a
    (run, subrun, event) triple cannot be told apart by identity alone.

    Parameters
    ----------
    distinct_by_source : mapping of str to array_like of uint64
        Source label -> that source's distinct packed keys.

    Returns
    -------
    dict
        ``pairs`` (list of ``{a, b, n_shared}`` for every overlapping pair),
        ``n_overlapping_pairs``, ``n_keys_in_more_than_one_source``, ``disjoint`` (bool).
    """
    labels = list(distinct_by_source)
    sets = {s: np.unique(np.asarray(distinct_by_source[s], dtype=np.uint64).ravel())
            for s in labels}
    pairs = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            n_shared = int(np.intersect1d(sets[a], sets[b], assume_unique=True).size)
            if n_shared:
                pairs.append({"a": a, "b": b, "n_shared": n_shared})
    if sets:
        stacked = np.concatenate([sets[s] for s in labels])
        _, counts = np.unique(stacked, return_counts=True)
        n_multi = int((counts > 1).sum())
    else:
        n_multi = 0
    return {
        "pairs": pairs,
        "n_overlapping_pairs": len(pairs),
        "n_keys_in_more_than_one_source": n_multi,
        "disjoint": n_multi == 0,
    }


def inventory_overlap(a_keys, b_keys):
    """Set relationship between two inventories' identities, within one source file.

    Two different questions ride on this and they have different answers:

    * `mc_signal_reco` vs `mc_truth_denom` -- the Phase-18.2 `c`-invariant makes their entry
      COUNTS equal by construction. Whether their identity SETS are equal is a separate fact, and
      only if they are can a signal row be joined to its truth-denominator row on identity.
    * `mc_background` vs either MC tree -- background rows are reco-selected non-signal events, so
      the sets are expected DISJOINT. Overlap would mean an identity alone does not say which
      inventory a row came from, and a cross-inventory join would be ambiguous.

    Returns
    -------
    dict
        ``n_a``, ``n_b``, ``n_shared``, ``n_only_a``, ``n_only_b``, ``sets_equal``, ``disjoint``.
    """
    a = np.unique(np.asarray(a_keys, dtype=np.uint64).ravel())
    b = np.unique(np.asarray(b_keys, dtype=np.uint64).ravel())
    n_shared = int(np.intersect1d(a, b, assume_unique=True).size)
    return {
        "n_a": int(a.size), "n_b": int(b.size), "n_shared": n_shared,
        "n_only_a": int(a.size) - n_shared, "n_only_b": int(b.size) - n_shared,
        "sets_equal": n_shared == a.size == b.size,
        "disjoint": n_shared == 0,
    }


def verdict_from(within_source_unique, sources_disjoint):
    """Map the two measured facts onto a `VERDICTS` value.

    `within_source_unique` is "no source's own key set has a duplicate"; `sources_disjoint` is "no
    key appears under two sources". Both are required for `UNIQUE_WITHOUT_SOURCE`; duplication
    WITHIN a source cannot be repaired by adding source, hence `NOT_UNIQUE`.
    """
    if not within_source_unique:
        return NOT_UNIQUE
    return UNIQUE_WITHOUT_SOURCE if sources_disjoint else UNIQUE_WITH_SOURCE


# --- Export block assembly and validation -------------------------------------------------------
def build_identity_block(prefix, values, source, occurrence, fields, bound_identity_hash,
                         order_hash_fn):
    """Assemble one inventory's identity block for the NPZ, keyed per `export_keys(prefix)`.

    `values` is the (n, 3) raw identity column stack IN INVENTORY ROW ORDER -- the same order, and
    the same retained rows, as the inventory it accompanies. `occurrence` must have been computed
    by `occurrence_index` over the FULL source tree and then subset to the retained rows, so it
    identifies the event rather than its position in the selection. `bound_identity_hash` is the
    target NPZ's own stored order hash for that inventory, copied in so a consumer can refuse a
    sidecar that belongs to a different dump. `order_hash_fn` is
    `fullevent_fps_dataloader.inventory_order_hash`, passed in rather than imported so this module
    stays free of the dataloader's import chain.
    """
    keys = export_keys(prefix)
    values = np.asarray(values, dtype=np.int32)
    if values.ndim != 2 or values.shape[1] != 3:
        raise ValueError(f"[IDENTITY] '{prefix}' values must be (n, 3), got {values.shape}")
    n = values.shape[0]
    source = np.asarray(source, dtype=np.int16)
    occurrence = np.asarray(occurrence, dtype=np.int32)
    if source.shape != (n,):
        raise ValueError(f"[IDENTITY] '{prefix}' source {source.shape} != rows {n}")
    if occurrence.shape != (n,):
        raise ValueError(f"[IDENTITY] '{prefix}' occurrence {occurrence.shape} != rows {n}")
    if tuple(fields) not in (MC_IDENTITY_FIELDS, DATA_IDENTITY_FIELDS):
        raise ValueError(f"[IDENTITY] '{prefix}' unknown identity field set {tuple(fields)}")
    packed = pack_identity(values[:, 0], values[:, 1], values[:, 2])
    block = {
        keys["fields"]: np.asarray(list(fields)),
        keys["values"]: values,
        keys["source"]: source,
        keys["occurrence"]: occurrence,
        keys["key"]: packed,
        keys["bound_to"]: np.asarray(str(bound_identity_hash)),
    }
    block[keys["digest"]] = np.asarray(order_hash_fn(values, source, occurrence, packed))
    return block


def verify_identity_block(prefix, arrays, n_rows, order_hash_fn, bound_identity_hash=None):
    """Fail closed unless an identity block is present, complete, row-aligned and self-consistent.

    Checks, in order: every key present; row count equals the inventory's; the packed key column
    is exactly `pack_identity` of the stored columns (so the key cannot have been written from a
    different source than the values); the digest recomputes; and, when `bound_identity_hash` is
    supplied, that the block was built against THAT inventory.
    """
    keys = export_keys(prefix)
    present = set(arrays.files) if hasattr(arrays, "files") else set(arrays)
    missing = [k for k in keys.values() if k not in present]
    if missing:
        raise ValueError(f"[IDENTITY] '{prefix}' block incomplete, missing {missing} (fail closed)")
    values = np.asarray(arrays[keys["values"]])
    source = np.asarray(arrays[keys["source"]])
    occurrence = np.asarray(arrays[keys["occurrence"]])
    packed = np.asarray(arrays[keys["key"]], dtype=np.uint64)
    if values.shape != (int(n_rows), 3):
        raise ValueError(f"[IDENTITY] '{prefix}' values {values.shape} != ({n_rows}, 3); the "
                         f"identity is not row-aligned with its inventory")
    if any(a.shape != (int(n_rows),) for a in (source, occurrence, packed)):
        raise ValueError(f"[IDENTITY] '{prefix}' source/occurrence/key not row-aligned with its "
                         f"inventory")
    want_packed = pack_identity(values[:, 0], values[:, 1], values[:, 2])
    if not np.array_equal(packed, want_packed):
        raise ValueError(f"[IDENTITY] '{prefix}' packed key disagrees with its own identity "
                         f"columns (fail closed)")
    # Structured, not int64-stacked: a uint64 key above 2**63 would silently wrap in a signed
    # stack and two distinct identities could compare equal.
    probe = np.empty(int(n_rows), dtype=[("s", np.int16), ("k", np.uint64), ("o", np.int32)])
    probe["s"], probe["k"], probe["o"] = source, packed, occurrence
    if np.unique(probe).size != int(n_rows):
        raise ValueError(f"[IDENTITY] '{prefix}' (source, key, occurrence) is not unique over the "
                         f"exported rows; the identity does not identify (fail closed)")
    want_digest = order_hash_fn(values.astype(np.int32), source.astype(np.int16),
                                occurrence.astype(np.int32), packed)
    got_digest = str(np.asarray(arrays[keys["digest"]]).item())
    if got_digest != want_digest:
        raise ValueError(f"[IDENTITY] '{prefix}' digest mismatch (reordered/tampered; fail closed)")
    if bound_identity_hash is not None:
        got_bound = str(np.asarray(arrays[keys["bound_to"]]).item())
        if got_bound != str(bound_identity_hash):
            raise ValueError(
                f"[IDENTITY] '{prefix}' identity block was built against inventory "
                f"{got_bound[:12]}... but is being joined to {str(bound_identity_hash)[:12]}...; "
                f"these are different dumps (fail closed)")
    return True
