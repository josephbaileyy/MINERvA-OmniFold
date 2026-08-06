#!/usr/bin/env python3
"""Step 0 of PLAN-20260806-niter3-budget-and-J28-reroll: protect the throw slabs.

WHY. The J28 flux re-roll is a cheap post-hoc rescale *provided the throw slabs still exist*
(`rescale_flux_universes.py` corrects a saved universe in place along pT, an identity, no
re-unfolding). If `/pscratch` is purged first, that cheap correction becomes a full re-throw
campaign. The plan calls the slabs the single largest schedule risk for exactly this reason.

WHAT "PROTECT" MEANS HERE, and why a byte copy alone is not enough. The plan asks for the slabs to be
verified "readable, not merely present". A byte-identical copy of a truncated or corrupt `.npz` is
still a corrupt `.npz`, and `find` reports it as present either way -- so this opens every file with
`np.load` and touches each array, which is the only check that distinguishes a usable slab from a
file of the right size. Integrity (sha256, both sides) and readability (`np.load`) are different
questions and both are asked.

WHAT IT WRITES. A manifest of every slab with its sha256, size, array names and shapes. The manifest
is the durable half of this step: it is small, it belongs in git, and it lets anyone later prove that
a restored or re-copied slab is the same slab the budget was built from. The copy on CFS is the other
half and is deliberately dumb -- same relative layout under a single root, so a restore is one rsync.

The slabs total ~62 MiB across 365 files, so this is not a heavy sweep and does not need a compute
node; it is closer to a `git status` than to a throw pass.

usage:
  protect_throw_slabs.py --dest /global/cfs/cdirs/m3246/josephrb/slab-protect-20260806 \
                         --manifest nd-unfolding/products/slab_manifest_20260806.json
  protect_throw_slabs.py --verify-only --manifest <path>     # re-check against a written manifest
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

import numpy as np

SLAB_GLOB = "*slab*.npz"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def find_slabs(root):
    hits = []
    for dirpath, _dirnames, filenames in os.walk(os.path.join(root, "nd-unfolding")):
        for fn in filenames:
            if fn.endswith(".npz") and "slab" in fn:
                p = os.path.join(dirpath, fn)
                hits.append(os.path.relpath(p, root))
    return sorted(hits)


def _read(abspath, allow_pickle):
    with np.load(abspath, allow_pickle=allow_pickle) as d:
        arrays = {}
        for k in d.files:
            a = d[k]                          # forces the actual read/decompress
            arrays[k] = {"shape": list(a.shape), "dtype": str(a.dtype),
                         "finite": bool(np.isfinite(a).all()) if a.dtype.kind == "f" else None}
        return arrays


def inspect(abspath):
    """Open the slab and touch every array. Returns (ok, detail, arrays).

    Tries allow_pickle=False first, because loading pickles is the unsafe default and most slabs are
    pure numeric. A slab carrying pickled metadata raises ValueError under that setting, which is NOT
    corruption -- reporting it as unreadable would be a false alarm, and a false alarm here costs more
    than the check is worth. So the pickle case is retried and recorded as what it is.
    """
    try:
        return True, "ok", _read(abspath, False)
    except ValueError as e:
        if "allow_pickle" not in str(e):
            return False, f"ValueError: {e}", {}
        try:
            return True, "ok (contains pickled objects; re-read with allow_pickle=True)", \
                _read(abspath, True)
        except Exception as e2:               # noqa: BLE001
            return False, f"{type(e2).__name__}: {e2}", {}
    except Exception as e:                    # noqa: BLE001 -- any other failure means unusable
        return False, f"{type(e).__name__}: {e}", {}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--dest", help="off-scratch destination root (omit to inventory only)")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--verify-only", action="store_true",
                    help="re-check the tree against an existing manifest; writes nothing")
    a = ap.parse_args()

    if a.verify_only:
        man = json.load(open(a.manifest))
        bad, missing, moved = [], [], 0
        for rel, rec in man["slabs"].items():
            p = os.path.join(a.root, rel)
            if not os.path.isfile(p):
                missing.append(rel)
                continue
            if sha256(p) != rec["sha256"]:
                bad.append(rel)
            moved += 1
        print(f"verified {moved} of {len(man['slabs'])} recorded slabs")
        print(f"  {len(missing)} MISSING, {len(bad)} DIGEST MISMATCH")
        for r in missing[:10]:
            print(f"    missing  {r}")
        for r in bad[:10]:
            print(f"    mismatch {r}")
        print("\n" + ("*** SLAB SET DIVERGED ***" if (missing or bad) else "SLAB SET INTACT"))
        return 1 if (missing or bad) else 0

    rels = find_slabs(a.root)
    if not rels:
        sys.exit("FATAL: no slabs found -- refusing to write an empty manifest, which would "
                 "record 'nothing to protect' as a success")

    slabs, unreadable, total = {}, [], 0
    for rel in rels:
        src = os.path.join(a.root, rel)
        size = os.path.getsize(src)
        digest = sha256(src)
        ok, detail, arrays = inspect(src)
        total += size
        slabs[rel] = {"sha256": digest, "bytes": size, "readable": ok,
                      "detail": detail, "arrays": arrays}
        if not ok:
            unreadable.append((rel, detail))
        if a.dest:
            dst = os.path.join(a.dest, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            # copy2 preserves mtime, which keeps the provenance of when the throw was produced
            shutil.copy2(src, dst)
            if sha256(dst) != digest:
                sys.exit(f"FATAL: copy verification failed for {rel} -- destination digest differs")

    man = {
        "purpose": ("Step 0 of PLAN-20260806-niter3-budget-and-J28-reroll: the throw slabs the J28 "
                    "re-roll and the niter=3 budget recompute both consume. A purge of /pscratch "
                    "before the re-roll converts a cheap post-hoc rescale into a full re-throw."),
        "generated_by": "nd-unfolding/protect_throw_slabs.py",
        "source_root": a.root,
        "offscratch_copy": a.dest or None,
        "copy_verified": ("every destination file re-hashed and compared to its source digest"
                          if a.dest else "no copy requested; inventory only"),
        "readability_check": ("np.load on every slab with every array materialised; a byte-identical "
                              "copy of a corrupt npz is still corrupt, so presence and digests alone "
                              "do not answer this"),
        "count": len(slabs),
        "total_bytes": total,
        "unreadable_count": len(unreadable),
        "slabs": slabs,
    }
    os.makedirs(os.path.dirname(os.path.join(a.root, a.manifest)), exist_ok=True)
    with open(os.path.join(a.root, a.manifest), "w") as fh:
        json.dump(man, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print(f"{len(slabs)} slabs, {total / 2**20:.1f} MiB")
    print(f"  readable: {len(slabs) - len(unreadable)}   UNREADABLE: {len(unreadable)}")
    for rel, detail in unreadable:
        print(f"    {rel}: {detail}")
    print(f"  off-scratch copy: {a.dest or 'NOT REQUESTED'}")
    print(f"  manifest: {a.manifest}")
    return 1 if unreadable else 0


if __name__ == "__main__":
    sys.exit(main())
