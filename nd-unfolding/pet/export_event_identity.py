#!/usr/bin/env python3
"""Export row-aligned event identity for the G2 full-event inventories as a SIDECAR NPZ.

WHY A SIDECAR. The production NPZ (`dump_pointcloud_inputs.py --g2`) and every receipt that
digests it stay byte-identical: this tool writes a NEW file beside the existing one and modifies
no production artifact. The price is that the sidecar must PROVE it belongs to its target, which
it does by re-deriving the target's own stored inventory order hashes from the same ROOT and
refusing to write unless they match (signal and background exactly; data by row count plus the
stored hash, whose evidence array is the padded cloud this tool does not rebuild).

WHAT IS PRESERVED. Selection and row order are not re-specified here: the retained-row predicates
are IMPORTED from `dump_pointcloud_inputs` and applied per row in the same entry order, so a
change to the production selection moves this exporter with it and cannot silently desynchronise.
Native misses are retained exactly as the dumper retains them (`pass_truth` true, `pass_reco`
false) and carry the truth-denom-cached `mc_*` identity the event loop wrote for them.

IDENTITY. `(source, run, subrun, event, occurrence)` -- see `event_identity` and
`EVENT_IDENTITY_JOIN_CONTRACT.md`. `source` is the playlist; `occurrence` is the ordinal among
rows sharing the tuple, computed over the FULL tree in entry order (never over the selection), and
is what makes the identity unique where the files' own tuple is not.

Needs PyROOT on a compute node. Example:

    python3 export_event_identity.py \
        --omnifile .../runEventLoopOmniFold_G2_FPS_MEFHC.root \
        --target-npz .../of_inputs_fullevent.npz \
        --identity-audit .../EVENT_IDENTITY_AUDIT_MEFHC.json \
        --out .../of_inputs_fullevent.identity.npz
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


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _import_production_selection(pet_dir):
    """Import the production row predicates from a NAMED directory, and prove they came from it.

    Which tree's predicates ran is the whole provenance question, so it is an explicit argument
    rather than "whatever directory this file happens to sit in". The exporter may be deployed
    anywhere; the selection must be the one that built the target NPZ.

    Two things make that checkable rather than assumed:

    * `dump_pointcloud_inputs` inserts a HARDCODED cluster root at `sys.path[0]` on import. That
      is the OI-136 shape -- run from another checkout and the predicates come from the pinned
      tree while every path report says otherwise, and `PYTHONPATH` cannot outrank position 0.
      So the resolved `__file__` is compared against `pet_dir` and the run fails closed on a
      mismatch.
    * The resolved path AND its sha256 are returned for the provenance record, so a later reader
      can tell exactly which selection produced a sidecar instead of inferring it from a
      directory name.

    Returns (module, {"path": ..., "sha256": ...}).
    """
    pet_dir = os.path.abspath(pet_dir)
    if not os.path.isfile(os.path.join(pet_dir, "dump_pointcloud_inputs.py")):
        raise SystemExit(f"[IDENTITY-EXPORT] FAIL: no dump_pointcloud_inputs.py in {pet_dir}; "
                         f"--production-pet-dir must name the checkout whose selection built the "
                         f"target NPZ")
    sys.path.insert(0, pet_dir)
    import dump_pointcloud_inputs as dpi
    resolved = os.path.abspath(dpi.__file__)
    got = os.path.dirname(resolved)
    if got != pet_dir:
        raise SystemExit(
            f"[IDENTITY-EXPORT] FAIL: imported dump_pointcloud_inputs from {got}, not the "
            f"requested {pet_dir}. A hardcoded sys.path[0] has shadowed it (OI-136); the "
            f"selection predicates would not be the ones you named.")
    return dpi, {"path": resolved, "sha256": _sha256(resolved)}


# --- Inventory descriptions -------------------------------------------------------------------
# Each inventory names its tree, the scalar branches its retention predicate reads, and the
# branches whose values reproduce the target NPZ's stored order hash.
INVENTORIES = ("sig", "data", "bkg")
INVENTORY_TREE = eid.INVENTORY_TREE


def _read_scalars(path, tree, branches, pass_branch):
    """Read the scalar columns a retention predicate needs, plus the UChar_t pass flag as int."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    df = ROOT.RDataFrame(tree, path)
    df = df.Define("_pass_i", f"(int){pass_branch}")
    cols = df.AsNumpy(list(branches) + ["_pass_i"])
    out = {b: np.asarray(cols[b], dtype=np.float64) for b in branches}
    out["_pass"] = np.asarray(cols["_pass_i"], dtype=np.int64)
    return out


def _read_identity(path, tree):
    """Read a tree's identity columns as an (n, 3) int64 array in entry order."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    fields = eid.TREE_IDENTITY_FIELDS[tree]
    cols = ROOT.RDataFrame(tree, path).AsNumpy(list(fields))
    return np.column_stack([np.asarray(cols[c], dtype=np.int64) for c in fields])


def signal_retention(dpi, path):
    """Per-row keep / pass_reco / pass_truth for `mc_signal_reco`, from the PRODUCTION predicate.

    Returns (keep, pass_reco, pass_truth, w_truth) as full-length arrays in entry order.
    `dpi.select_signal_row` is applied row by row rather than vectorised: a vectorised rewrite
    would be a second implementation of the retention rule, and the two could disagree exactly
    where it matters (non-finite and boundary values).
    """
    tree = "mc_signal_reco"
    cols = _read_scalars(path, tree, ("sim", "sim_pz", "MC", "MC_pz", "w_truth"), "sim_pass")
    n = cols["sim"].size
    keep = np.zeros(n, bool)
    pass_reco = np.zeros(n, bool)
    pass_truth = np.zeros(n, bool)
    sim, sim_pz, mc, mc_pz, sp = (cols["sim"], cols["sim_pz"], cols["MC"], cols["MC_pz"],
                                  cols["_pass"])
    for i in range(n):
        k, pr, pt = dpi.select_signal_row(sim[i], sim_pz[i], sp[i], mc[i], mc_pz[i])
        keep[i] = k
        pass_reco[i] = pr
        pass_truth[i] = pt
        if i and i % 5000000 == 0:
            print(f"  [identity] signal retention {i}/{n}", flush=True)
    return keep, pass_reco, pass_truth, cols["w_truth"]


def _flat_retention(dpi, path, tree, pt_branch, pz_branch, pass_branch, extra=()):
    """Per-row keep for `data` / `mc_background`: reco-selected AND inside the retained FPS box.

    This is the dumper's own two-clause gate, with `in_fps_domain` imported rather than restated.
    """
    cols = _read_scalars(path, tree, (pt_branch, pz_branch) + tuple(extra), pass_branch)
    pt, pz, sp = cols[pt_branch], cols[pz_branch], cols["_pass"]
    n = pt.size
    keep = np.zeros(n, bool)
    for i in range(n):
        keep[i] = int(sp[i]) != 0 and dpi.in_fps_domain(pt[i], pz[i])
    return keep, cols


# --- Order-hash re-derivation -------------------------------------------------------------------
def rederive_order_hashes(order_hash_fn, sig, bkg):
    """Recompute the target NPZ's own stored order hashes from this re-read.

    `sig_identity_hash` is `inventory_order_hash(w_truth, pass_truth)` and `bkg_identity_hash` is
    `inventory_order_hash(w_bkg, bkg_indices)` in `dump_pointcloud_inputs.finalize_g2_arrays`; both
    are reproducible from scalars, so matching them proves this exporter retained the SAME ROWS in
    the SAME ORDER as the dump it is being joined to. `data_identity_hash` is taken over the padded
    point cloud, which this tool does not rebuild -- the data binding is row count plus the stored
    value, and the contract doc says so rather than implying an equal check.
    """
    return {
        "sig_identity_hash": order_hash_fn(np.asarray(sig["w_truth"], np.float32),
                                           np.asarray(sig["pass_truth"], bool)),
        "bkg_identity_hash": order_hash_fn(np.asarray(bkg["w_bkg"], np.float32),
                                           np.arange(bkg["w_bkg"].size, dtype=np.int64)),
    }


def _stored(npz, key):
    return str(np.asarray(npz[key]).item())


# --- Source resolution ---------------------------------------------------------------------------
def resolve_sources(args, tree, n_rows):
    """Return (labels, per-row source index) for `tree` in the ROOT being read.

    Single-playlist file: one label, all rows source 0. Merged file: the per-source counts and
    order come from the identity-audit receipt, which measured them on these exact files; the
    boundary sum is checked against the tree's own entry count and fails closed on disagreement.
    """
    if args.source_label:
        return [args.source_label], np.zeros(int(n_rows), dtype=np.int16)
    with open(args.identity_audit) as fh:
        audit = json.load(fh)
    if audit.get("truncated_read"):
        raise SystemExit(f"[IDENTITY-EXPORT] the audit receipt was produced with --max-entries "
                         f"{audit.get('max_entries')}; its per-source counts describe a prefix, "
                         f"not these files, and the row -> source map built from them would be "
                         f"wrong (fail closed)")
    labels = list(audit["source_order"])
    merged = (audit.get("merged") or {}).get("trees", {}).get(tree)
    if not merged:
        raise SystemExit(f"[IDENTITY-EXPORT] audit receipt has no merged entry for tree {tree!r}; "
                         f"it cannot describe this file's row -> source assignment")
    counts = [int(merged["per_source_counts"][l]) for l in labels]
    eid.check_boundaries(counts, n_rows)
    if not merged.get("concatenation_order_verified"):
        raise SystemExit(f"[IDENTITY-EXPORT] audit did not VERIFY the concatenation order for "
                         f"{tree!r}; row -> source would be an assumption (fail closed)")
    return labels, eid.source_index_from_boundaries(counts)


def audit_verdict(args, tree):
    """The measured uniqueness verdict for `tree`, or `None` when no audit was supplied."""
    if not args.identity_audit:
        return None
    with open(args.identity_audit) as fh:
        return json.load(fh).get("verdict_by_tree", {}).get(tree)


# --- Driver ----------------------------------------------------------------------------------------
def build_sidecar(args):
    """Read the ROOT, re-derive the retained rows, and return the sidecar array dict."""
    dpi, dpi_prov = _import_production_selection(args.production_pet_dir)
    import fullevent_fps_dataloader as ffd
    inventory_order_hash = ffd.inventory_order_hash
    hash_prov = {"path": os.path.abspath(ffd.__file__),
                 "sha256": _sha256(os.path.abspath(ffd.__file__))}

    npz = np.load(args.target_npz, allow_pickle=False)
    n_target = {"sig": int(np.asarray(npz["w_truth"]).shape[0]),
                "data": int(np.asarray(npz["measured_pc"]).shape[0]),
                "bkg": int(np.asarray(npz["w_bkg"]).shape[0])}

    arrays = {eid.CONTRACT_VERSION_KEY: np.asarray(eid.IDENTITY_CONTRACT_VERSION)}
    verdicts, labels_seen = {}, None

    print("[identity] signal inventory", flush=True)
    keep_s, pass_reco, pass_truth, w_truth = signal_retention(dpi, args.omnifile)
    sig = {"w_truth": w_truth[keep_s], "pass_truth": pass_truth[keep_s]}

    print("[identity] background inventory", flush=True)
    keep_b, bcols = _flat_retention(dpi, args.omnifile, "mc_background", "sim_background",
                                    "sim_background_pz", "sim_background_pass", ("w_bkg",))
    bkg = {"w_bkg": bcols["w_bkg"][keep_b]}

    print("[identity] data inventory", flush=True)
    keep_d, _ = _flat_retention(dpi, args.omnifile, "data", "measured", "measured_pz",
                                "measured_pass")

    kept = {"sig": keep_s, "data": keep_d, "bkg": keep_b}
    for inv, k in kept.items():
        if int(k.sum()) != n_target[inv]:
            raise SystemExit(
                f"[IDENTITY-EXPORT] FAIL: re-derived {inv} retention keeps {int(k.sum())} rows, "
                f"the target NPZ has {n_target[inv]}. The sidecar would be misaligned; refusing "
                f"to write.")

    rederived = rederive_order_hashes(inventory_order_hash, sig, bkg)
    for key, got in rederived.items():
        want = _stored(npz, key)
        if got != want:
            raise SystemExit(
                f"[IDENTITY-EXPORT] FAIL: re-derived {key} {got[:12]}... != the target NPZ's "
                f"{want[:12]}.... Same row count, different rows or order; refusing to write.")
    print(f"[identity] order-hash re-derivation matched: {sorted(rederived)}", flush=True)

    for inv in INVENTORIES:
        tree = INVENTORY_TREE[inv]
        values_all = _read_identity(args.omnifile, tree)
        labels, src_all = resolve_sources(args, tree, values_all.shape[0])
        labels_seen = labels if labels_seen is None else labels_seen
        keys_all = eid.pack_identity(values_all[:, 0], values_all[:, 1], values_all[:, 2])
        # Occurrence over the FULL tree, then subset: identity must not depend on the selection.
        occ_all = eid.occurrence_index(keys_all, src_all)
        m = kept[inv]
        bound = _stored(npz, f"{inv}_identity_hash")
        arrays.update(eid.build_identity_block(
            inv, values_all[m], src_all[m], occ_all[m],
            eid.TREE_IDENTITY_FIELDS[tree], bound, inventory_order_hash))
        verdicts[tree] = audit_verdict(args, tree)
        print(f"[identity] {inv}: {int(m.sum())} rows, verdict {verdicts[tree]}, "
              f"occurrence>0 on {int((occ_all[m] > 0).sum())} rows", flush=True)

    arrays[eid.SOURCE_LABELS_KEY] = np.asarray(labels_seen)
    arrays[eid.UNIQUENESS_KEY] = np.asarray(json.dumps(verdicts, sort_keys=True))
    arrays["identity_provenance"] = np.asarray(json.dumps({
        "omnifile": os.path.abspath(args.omnifile),
        "target_npz": os.path.abspath(args.target_npz),
        "identity_audit": os.path.abspath(args.identity_audit) if args.identity_audit else None,
        "selection_module": dpi_prov,          # WHICH selection retained these rows
        "order_hash_module": hash_prov,        # WHICH inventory_order_hash bound them
        "rederived_order_hashes": rederived,
        "written_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }, sort_keys=True))
    return arrays, n_target, inventory_order_hash


def write_atomic(path, arrays):
    """Write the sidecar with the dumper's transactional idiom: temp file, then atomic rename."""
    import tempfile
    d = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".identity_", suffix=".npz", dir=d)
    os.close(fd)
    try:
        np.savez_compressed(tmp, **arrays)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--omnifile", required=True, help="the G2 full-event ROOT the NPZ was built from")
    ap.add_argument("--target-npz", required=True, help="the inventory NPZ this identity joins to")
    ap.add_argument("--out", required=True, help="sidecar identity NPZ to write")
    ap.add_argument("--identity-audit", default=None,
                    help="audit receipt from audit_event_identity.py; REQUIRED for a merged "
                         "multi-playlist ROOT (it supplies and verifies the row -> playlist map)")
    ap.add_argument("--source-label", default=None,
                    help="single-playlist ROOT: the one source label for every row")
    ap.add_argument("--production-pet-dir", default=_HERE,
                    help="directory holding the PRODUCTION dump_pointcloud_inputs.py whose "
                         "selection built the target NPZ (default: this file's directory). Its "
                         "resolved path and sha256 are recorded in the sidecar's provenance.")
    args = ap.parse_args(argv)
    if not args.source_label and not args.identity_audit:
        ap.error("one of --source-label (single playlist) or --identity-audit (merged) is required")

    arrays, n_target, order_hash_fn = build_sidecar(args)
    for inv in INVENTORIES:
        eid.verify_identity_block(inv, arrays, n_target[inv], order_hash_fn)
    write_atomic(args.out, arrays)
    print(f"[identity] wrote {args.out} for {n_target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
