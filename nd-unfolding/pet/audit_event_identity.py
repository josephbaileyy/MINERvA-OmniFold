#!/usr/bin/env python3
"""Measure whether run/subrun/(nthEvtInFile|gate) is a usable event identity for the G2
full-event inventories, and emit a receipt.

READ-ONLY. Opens ROOT files for reading and writes one JSON receipt. It changes no production
artifact, launches nothing, and adopts nothing -- it establishes a fact the export depends on.

What it measures, per tree, for each named source file:
  * the observed range of every identity component (the bit-field widths in `event_identity` are
    a declared contract; this is the check that the declaration still covers the data);
  * duplication of the packed identity WITHIN that file;
  * for `mc_signal_reco`, whether rows WITHOUT RECO carry a populated identity. `sim_pass == 0`
    is the union of appended truth-only misses and reco-loop rows that failed the reco gate --
    NOT the C++ `nTruthOnlyMisses` count, which is the first of those alone. The event loop
    copies identity onto the appended rows from the truth-denom cache; an all-zero identity on
    any of them would mean such rows are exportable but not joinable;
  * collisions of the C++ `makeEventKey` wrapped key, which is how the event loop's own dedupe
    and miss-append membership test are keyed.

Across sources it measures pairwise overlap of the distinct key sets, which is what decides
whether a `source` (playlist) column is REQUIRED in the identity or merely informative.

With `--merged`, it additionally checks that the merged file's per-tree entry count equals the sum
over the named per-source files, and that the identity of the rows in each source's declared row
range matches that source's own file -- i.e. that the hadd concatenation order used to derive
`source` for the merged file is the real one.

Needs PyROOT (`source setup_salloc_env.sh` on Perlmutter). Example:

    python3 audit_event_identity.py \
        --root 1A=.../runEventLoopOmniFold_G2_FPS_1A.root \
        --root 1B=.../runEventLoopOmniFold_G2_FPS_1B.root \
        --merged .../runEventLoopOmniFold_G2_FPS_MEFHC.root \
        --out .../EVENT_IDENTITY_AUDIT.json
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import event_identity as eid  # noqa: E402  (login-safe: no ROOT/TF)

DEFAULT_TREES = ("mc_signal_reco", "mc_truth_denom", "mc_background", "data")
MISS_FLAG_BRANCH = {"mc_signal_reco": "sim_pass"}

# Witness columns compared across the rows of a repeated identity. A duplication count alone
# cannot be acted on: identical rows are an upstream double-fill (remedy: dedupe), differing rows
# are distinct physical events sharing the tuple (remedy: more identity). These are the cheapest
# columns that separate those two readings -- kinematics that no two distinct events share.
WITNESS_BRANCHES = {
    "mc_signal_reco": ("MC", "MC_pz", "sim", "sim_pz", "w_truth"),
    "mc_truth_denom": ("MC", "MC_pz", "w_truth"),
    "mc_background": ("sim_background", "sim_background_pz", "w_bkg"),
    "data": ("measured", "measured_pz", "mu_reco_E", "vtx_reco_z"),
}


def _identity_arrays(path, tree, max_entries=None):
    """Return (n_entries, (n,3) int64 identity columns, miss-flag int array, witness columns).

    The `UChar_t` pass flag is cast to `int` in C++ via `Define` rather than after `AsNumpy`:
    this ROOT build hands `UChar_t` back as a dtype-object array of one-character Python strings,
    so `astype(int)` parses it as TEXT and raises on `'\\x00'`.
    """
    import ROOT
    ROOT.gROOT.SetBatch(True)
    fields = eid.TREE_IDENTITY_FIELDS[tree]
    flag = MISS_FLAG_BRANCH.get(tree)

    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise SystemExit(f"[IDENTITY-AUDIT] cannot open {path}")
    t = f.Get(tree)
    if not t:
        f.Close()
        return None
    n = int(t.GetEntries())
    f.Close()

    df = ROOT.RDataFrame(tree, path)
    if max_entries is not None and max_entries < n:
        df = df.Range(0, int(max_entries))
        n = int(max_entries)
    want = list(fields)
    if flag:
        df = df.Define("_miss_flag_i", f"(int){flag}")
        want.append("_miss_flag_i")
    witness = [c for c in WITNESS_BRANCHES.get(tree, ()) if c in set(df.GetColumnNames())]
    want += witness
    cols = df.AsNumpy(want)
    values = np.column_stack([np.asarray(cols[c], dtype=np.int64) for c in fields])
    miss_flag = np.asarray(cols["_miss_flag_i"], dtype=np.int64) if flag else None
    wit = (np.column_stack([np.asarray(cols[c], dtype=np.float64) for c in witness])
           if witness else None)
    return n, values, miss_flag, wit


def _component_ranges(values, fields):
    return {f: {"min": int(values[:, i].min()), "max": int(values[:, i].max())}
            for i, f in enumerate(fields)}


def audit_one(path, tree, max_entries=None, n_examples=5):
    """Full per-file, per-tree identity measurement. Returns a report dict (or None if absent)."""
    got = _identity_arrays(path, tree, max_entries)
    if got is None:
        return None
    n, values, miss_flag, witness = got
    fields = eid.TREE_IDENTITY_FIELDS[tree]
    rep = {"tree": tree, "n_entries": n, "identity_fields": list(fields),
           "component_ranges": _component_ranges(values, fields)}
    try:
        keys = eid.pack_identity(values[:, 0], values[:, 1], values[:, 2])
    except eid.IdentityRangeError as exc:
        rep["packable"] = False
        rep["pack_error"] = str(exc)
        return rep
    rep["packable"] = True
    rep["uniqueness"] = eid.uniqueness_report(keys, n_examples=n_examples)
    if not rep["uniqueness"]["is_unique"] and witness is not None:
        rep["duplicate_character"] = eid.duplicate_block_character(keys, witness)
        rep["duplicate_character"]["witness_branches"] = list(WITNESS_BRANCHES.get(tree, ()))
    # (source, key, occurrence) is unique by construction; what the receipt records is how much
    # work `occurrence` is doing -- 0 everywhere means the tuple already identified.
    occ = eid.occurrence_index(keys)
    rep["occurrence"] = {"max": int(occ.max()) if occ.size else 0,
                         "n_rows_needing_occurrence": int((occ > 0).sum())}

    wrapped = eid.cxx_wrapped_key(values[:, 0], values[:, 1], values[:, 2])
    n_distinct_wrapped = int(np.unique(wrapped).size)
    rep["cxx_wrapped_key"] = {
        "n_distinct": n_distinct_wrapped,
        "n_distinct_exact": rep["uniqueness"]["n_distinct"],
        # Collisions the C++ key suffers that the exact key does not: the event loop's dedupe and
        # its miss-append membership test both key on the wrapped value, so a nonzero count here
        # means the loop conflated two genuinely distinct events.
        "collisions_beyond_exact": rep["uniqueness"]["n_distinct"] - n_distinct_wrapped,
    }
    if miss_flag is not None:
        # `sim_pass == 0` is NOT the appended-native-miss count and must not be reported as one.
        # It is the union of (a) truth-only misses appended by AppendTruthOnlyMisses and (b)
        # reco-loop rows that failed the reco gate. The C++ reports (a) separately as
        # `nTruthOnlyMisses` in the merge receipt; conflating the two overstates it by ~44% at
        # MEFHC scale. What matters for the join is the same either way, and (a) is a subset of
        # what is checked here: no row lacking reco may carry an all-zero identity.
        no_reco = miss_flag == 0
        n_no_reco = int(no_reco.sum())
        zero_id = (values == 0).all(axis=1)
        rep["rows_without_reco"] = {
            "n_rows_without_reco": n_no_reco,
            "includes": "appended truth-only misses AND reco-loop rows failing the reco gate",
            "n_without_reco_with_zero_identity": int((no_reco & zero_id).sum()),
            "n_with_reco_with_zero_identity": int((~no_reco & zero_id).sum()),
            "identity_populated": bool(n_no_reco and not (no_reco & zero_id).any()),
        }
    rep["_keys"] = keys      # stripped before serialization; used for cross-source work
    return rep


def _strip_arrays(report):
    """Remove the in-memory key arrays the receipt must not carry."""
    if isinstance(report, dict):
        return {k: _strip_arrays(v) for k, v in report.items() if not k.startswith("_")}
    if isinstance(report, list):
        return [_strip_arrays(v) for v in report]
    return report


def audit_sources(sources, trees, max_entries=None):
    """Per-source, per-tree audit plus the cross-source overlap and the resulting verdict."""
    per_source, distinct = {}, {t: {} for t in trees}
    for label, path in sources:
        per_source[label] = {"path": path, "trees": {}}
        for tree in trees:
            rep = audit_one(path, tree, max_entries)
            if rep is None:
                per_source[label]["trees"][tree] = None
                continue
            if rep.get("packable"):
                distinct[tree][label] = np.unique(rep["_keys"])
            per_source[label]["trees"][tree] = rep
            print(f"[IDENTITY-AUDIT] {label} {tree}: {rep['n_entries']} entries, "
                  f"unique={rep.get('uniqueness', {}).get('is_unique')}", flush=True)

    # Cross-inventory, within each source file: whether an identity says which inventory it came
    # from, and whether signal and truth-denom are the same event set (see `inventory_overlap`).
    cross_inventory = {}
    for label, _ in sources:
        pairs = {}
        for a, b in (("mc_signal_reco", "mc_truth_denom"),
                     ("mc_background", "mc_signal_reco"),
                     ("mc_background", "mc_truth_denom")):
            ra = per_source[label]["trees"].get(a)
            rb = per_source[label]["trees"].get(b)
            if not ra or not rb or "_keys" not in ra or "_keys" not in rb:
                continue
            pairs[f"{a}|{b}"] = eid.inventory_overlap(ra["_keys"], rb["_keys"])
        if pairs:
            cross_inventory[label] = pairs
            sd = pairs.get("mc_signal_reco|mc_truth_denom")
            if sd:
                print(f"[IDENTITY-AUDIT] {label} signal vs truth_denom: sets_equal="
                      f"{sd['sets_equal']} (only_signal={sd['n_only_a']}, "
                      f"only_truth={sd['n_only_b']})", flush=True)

    cross, verdicts = {}, {}
    for tree in trees:
        if not distinct[tree]:
            continue
        cross[tree] = eid.cross_source_overlap(distinct[tree])
        within_unique = all(
            per_source[l]["trees"][tree]["uniqueness"]["is_unique"]
            for l in distinct[tree])
        verdicts[tree] = eid.verdict_from(within_unique, cross[tree]["disjoint"])
        print(f"[IDENTITY-AUDIT] {tree}: verdict {verdicts[tree]} "
              f"({cross[tree]['n_overlapping_pairs']} overlapping source pairs)", flush=True)
    return per_source, cross, verdicts, distinct, cross_inventory


def audit_merged(merged_path, sources, trees, per_source, max_entries=None):
    """Check the merged file's counts and per-source row ranges against the per-source files.

    The row-range check compares the SORTED distinct key set of each declared range against the
    source file's own, so it detects a wrong concatenation order (which would otherwise produce a
    plausible source column with no symptom). It does not re-check duplication, which
    `audit_one` already measured on the merged file itself.
    """
    out = {"path": merged_path, "trees": {}}
    for tree in trees:
        counts = []
        for label, _ in sources:
            rep = per_source[label]["trees"].get(tree)
            counts.append(0 if rep is None else int(rep["n_entries"]))
        merged_rep = audit_one(merged_path, tree, max_entries)
        if merged_rep is None:
            out["trees"][tree] = None
            continue
        entry = {"n_entries": merged_rep["n_entries"],
                 "sum_of_sources": int(sum(counts)),
                 "per_source_counts": {l: c for (l, _), c in zip(sources, counts)},
                 "uniqueness": merged_rep["uniqueness"],
                 "component_ranges": merged_rep["component_ranges"],
                 "cxx_wrapped_key": merged_rep["cxx_wrapped_key"]}
        entry["counts_agree"] = entry["n_entries"] == entry["sum_of_sources"]
        if entry["counts_agree"] and merged_rep.get("packable"):
            keys = merged_rep["_keys"]
            src_idx = eid.source_index_from_boundaries(counts)
            eid.check_boundaries(counts, keys.size)
            mismatches = []
            for i, (label, _) in enumerate(sources):
                own_rep = per_source[label]["trees"].get(tree)
                if own_rep is None or "_keys" not in own_rep:
                    # No per-source keys to compare against: the range is UNVERIFIED, which is
                    # not the same as verified-and-matching, so it counts as a mismatch.
                    mismatches.append(label)
                    continue
                rng = np.unique(keys[src_idx == i])
                own = np.unique(own_rep["_keys"])
                if not np.array_equal(rng, own):
                    mismatches.append(label)
            entry["concatenation_order_verified"] = not mismatches
            entry["range_mismatch_sources"] = mismatches
            # Uniqueness of (source, key) on the merged file: the operative question for a
            # consumer joining against the merged NPZ.
            entry["uniqueness_with_source"] = eid.uniqueness_report(keys, sources=src_idx)
        else:
            entry["concatenation_order_verified"] = False
            entry["range_mismatch_sources"] = None
        out["trees"][tree] = entry
        print(f"[IDENTITY-AUDIT] merged {tree}: counts_agree={entry['counts_agree']} "
              f"order_verified={entry['concatenation_order_verified']}", flush=True)
    return out


def _parse_source(spec):
    if "=" not in spec:
        raise argparse.ArgumentTypeError(f"--root expects LABEL=PATH, got {spec!r}")
    label, path = spec.split("=", 1)
    if not label or not path:
        raise argparse.ArgumentTypeError(f"--root expects LABEL=PATH, got {spec!r}")
    return label, path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", action="append", type=_parse_source, default=[], metavar="LABEL=PATH",
                    help="a per-source (per-playlist) G2 ROOT; repeat, in MERGE INPUT ORDER")
    ap.add_argument("--merged", default=None,
                    help="the hadd-merged G2 ROOT to cross-check against the per-source files")
    ap.add_argument("--trees", default=",".join(DEFAULT_TREES),
                    help="comma-separated trees to audit")
    ap.add_argument("--max-entries", type=int, default=None,
                    help="read only the first N entries per tree (SMOKE ONLY; a truncated read "
                         "cannot establish uniqueness and the receipt records it)")
    ap.add_argument("--out", required=True, help="receipt JSON path")
    args = ap.parse_args(argv)

    if not args.root:
        ap.error("at least one --root LABEL=PATH is required")
    trees = [t.strip() for t in args.trees.split(",") if t.strip()]
    unknown = [t for t in trees if t not in eid.TREE_IDENTITY_FIELDS]
    if unknown:
        ap.error(f"unknown tree(s) {unknown}; known: {sorted(eid.TREE_IDENTITY_FIELDS)}")

    per_source, cross, verdicts, _, cross_inventory = audit_sources(
        args.root, trees, args.max_entries)
    merged = audit_merged(args.merged, args.root, trees, per_source,
                          args.max_entries) if args.merged else None

    receipt = {
        "contract_version": eid.IDENTITY_CONTRACT_VERSION,
        "measured_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "truncated_read": args.max_entries is not None,
        "max_entries": args.max_entries,
        "source_order": [l for l, _ in args.root],
        "per_source": _strip_arrays(per_source),
        "cross_source_overlap": cross,
        "cross_inventory_overlap": cross_inventory,
        "verdict_by_tree": verdicts,
        "merged": _strip_arrays(merged) if merged else None,
    }
    tmp = args.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
    os.replace(tmp, args.out)
    print(f"[IDENTITY-AUDIT] wrote {args.out}")
    print(json.dumps(verdicts, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
