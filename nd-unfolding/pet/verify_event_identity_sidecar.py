#!/usr/bin/env python3
"""Verify an event-identity sidecar against the inventory NPZ it claims to describe.

This is the check a CONSUMER runs before joining, and it is deliberately a separate program from
the exporter: a producer that validates its own output proves the producer self-consistent, not
the artifact correct. Nothing here imports ROOT or re-reads the source ROOT — it reads the two
NPZs and nothing else, so it can run anywhere and cannot be satisfied by re-deriving from the
same upstream state the exporter used.

Checks, per inventory:
  1. the identity block is present, complete and row-aligned with the inventory;
  2. the packed key column is exactly `pack_identity` of the stored identity columns;
  3. the block digest recomputes;
  4. `(source, key, occurrence)` is unique over the exported rows -- the identity identifies;
  5. the block is BOUND to this inventory: its `*_bound_identity_hash` equals the inventory's own
     stored `*_identity_hash`. This is the step that makes row i of one file mean row i of the
     other, and the exporter's in-process check does not perform it.

Plus, for the signal inventory, the two properties the join contract promises about misses:
  6. no retained row carries an all-zero identity;
  7. rows with `pass_reco == False` are present and carry identity like any other row.

    python3 verify_event_identity_sidecar.py --inventory G2_FPS_MEFHC_P12.npz \\
        --sidecar G2_FPS_MEFHC_P12.identity.npz
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import event_identity as eid  # noqa: E402

ROW_COUNT_KEY = {"sig": "w_truth", "data": "measured_pc", "bkg": "w_bkg"}


def verify(inventory_path, sidecar_path, pet_dir=_HERE, verbose=True):
    """Run every check; return (n_passed, failures).

    `pet_dir` names the checkout supplying `inventory_order_hash`. It must be the same function
    the dump used to write the stored hashes -- a different implementation would make every
    digest mismatch, so which tree it comes from is part of the check, not an import detail.
    """
    pet_dir = os.path.abspath(pet_dir)
    if pet_dir not in sys.path:
        sys.path.insert(0, pet_dir)
    import fullevent_fps_dataloader as ffd
    inventory_order_hash = ffd.inventory_order_hash
    if os.path.dirname(os.path.abspath(ffd.__file__)) != pet_dir:
        raise SystemExit(f"[verify] FAIL: fullevent_fps_dataloader resolved to "
                         f"{os.path.abspath(ffd.__file__)}, not {pet_dir}")

    inv = np.load(inventory_path, allow_pickle=False)
    side = np.load(sidecar_path, allow_pickle=False)
    failures, passed = [], 0

    def ck(name, cond, detail=""):
        nonlocal passed
        if cond:
            passed += 1
        else:
            failures.append(f"{name}: {detail}")
        if verbose:
            print(f"  [{'PASS' if cond else 'FAIL'}] {name}{(' -- ' + detail) if detail else ''}")

    ck("contract version",
       str(np.asarray(side[eid.CONTRACT_VERSION_KEY]).item()) == eid.IDENTITY_CONTRACT_VERSION,
       str(np.asarray(side[eid.CONTRACT_VERSION_KEY]).item()))

    for prefix in ("sig", "data", "bkg"):
        n_rows = int(np.asarray(inv[ROW_COUNT_KEY[prefix]]).shape[0])
        bound = str(np.asarray(inv[f"{prefix}_identity_hash"]).item())
        try:
            eid.verify_identity_block(prefix, side, n_rows, inventory_order_hash,
                                      bound_identity_hash=bound)
            ck(f"{prefix}: block verifies and is BOUND to this inventory", True,
               f"{n_rows} rows, bound {bound[:12]}...")
        except ValueError as exc:
            ck(f"{prefix}: block verifies and is BOUND to this inventory", False, str(exc))
            continue

        keys = eid.export_keys(prefix)
        values = np.asarray(side[keys["values"]])
        ck(f"{prefix}: no retained row has an all-zero identity",
           not (values == 0).all(axis=1).any(),
           f"{int((values == 0).all(axis=1).sum())} all-zero rows")

        occ = np.asarray(side[keys["occurrence"]])
        packed = np.asarray(side[keys["key"]], dtype=np.uint64)
        n_needing = int((occ > 0).sum())
        bare_unique = eid.uniqueness_report(packed)["is_unique"]
        ck(f"{prefix}: occurrence usage is consistent with bare-key uniqueness",
           bare_unique == (n_needing == 0),
           f"bare key unique={bare_unique}, rows needing occurrence={n_needing}")

    # Miss preservation: the signal inventory must still contain its no-reco rows, and they must
    # be identified like any other row.
    pass_reco = np.asarray(inv["pass_reco"])
    pass_truth = np.asarray(inv["pass_truth"])
    miss = (~pass_reco) & pass_truth
    n_miss = int(miss.sum())
    ck("sig: native misses are present in the inventory", n_miss > 0, f"{n_miss} rows")
    sig_values = np.asarray(side[eid.export_keys("sig")["values"]])
    ck("sig: every native miss carries a populated identity",
       n_miss > 0 and not (sig_values[miss] == 0).all(axis=1).any(),
       f"{int((sig_values[miss] == 0).all(axis=1).sum())} misses with an all-zero identity")

    if verbose and "identity_provenance" in set(side.files):
        prov = json.loads(str(np.asarray(side["identity_provenance"]).item()))
        print("\n  provenance:")
        for k in ("omnifile", "target_npz", "identity_audit", "written_utc"):
            print(f"    {k}: {prov.get(k)}")
        for k in ("selection_module", "order_hash_module"):
            m = prov.get(k) or {}
            print(f"    {k}: {m.get('path')}  sha256 {str(m.get('sha256'))[:16]}...")
        print(f"    uniqueness verdicts: {str(np.asarray(side[eid.UNIQUENESS_KEY]).item())}")
        print(f"    source labels: {list(np.asarray(side[eid.SOURCE_LABELS_KEY]))}")
    return passed, failures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--sidecar", required=True)
    ap.add_argument("--pet-dir", default=_HERE,
                    help="checkout supplying inventory_order_hash (default: this file's "
                         "directory); must be the one whose dump wrote the stored hashes")
    args = ap.parse_args(argv)
    passed, failures = verify(args.inventory, args.sidecar, args.pet_dir)
    print(f"\n[verify] {passed} checks passed, {len(failures)} failed")
    for f in failures:
        print(f"  FAILED {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
