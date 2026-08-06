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
    """Every npz belonging to a throw/block slab set, plus the small bank tables the re-roll reads.

    SELECTION IS DIRECTORY-AWARE, and the first version of this function was not -- which silently
    under-protected the set by a third. It matched `"slab" in filename`, but the BLOCK slabs are named
    `block5d_flux_17.npz` and `blockfps_*.npz`, with no "slab" in the filename; only their *directory*
    (`block_slabs_5d_sb/`, `uthrow_slabs_fps_neutral/`) says what they are. That filter found 365 of
    542 files and reported "365 readable, 0 unreadable", which reads as complete. The block slabs are
    not optional: `rescale_flux_universes.py` rebuilds `C_blocksum` from them, so protecting the throw
    slabs alone would have left Step 1 unrunnable after a purge while the manifest said otherwise.
    The plan's own "365 slabs" precondition came from this same filter and is corrected with it.

    Also included: `flux_univ_ratio.npy` from each bank (11 KB, and the r_u table the whole correction
    is defined by). NOT included: the 26-37 GB of per-universe `sig_*`/`td_*` arrays, which are inputs
    to a re-THROW, not to this rescale; and `cv.npz` (2.9 GB each), which the rescale does read and
    which is handled by --extra rather than swept in, so a multi-GB copy is always an explicit choice.
    """
    hits = []
    for dirpath, _dirnames, filenames in os.walk(os.path.join(root, "nd-unfolding")):
        in_slab_dir = "slab" in os.path.basename(dirpath).lower()
        for fn in filenames:
            if fn.endswith(".npz") and ("slab" in fn.lower() or in_slab_dir):
                hits.append(os.path.relpath(os.path.join(dirpath, fn), root))
            elif fn == "flux_univ_ratio.npy":
                hits.append(os.path.relpath(os.path.join(dirpath, fn), root))
    return sorted(hits)


def _describe(a):
    return {"shape": list(a.shape), "dtype": str(a.dtype),
            "finite": bool(np.isfinite(a).all()) if a.dtype.kind == "f" else None}


def _read(abspath, allow_pickle):
    # A bare .npy loads to an ndarray, which is NOT a context manager and has no .files -- treating it
    # like an npz would report every bank ratio table as unreadable, a false alarm on a file that is
    # perfectly fine.
    if abspath.endswith(".npy"):
        return {os.path.basename(abspath): _describe(np.load(abspath, allow_pickle=allow_pickle))}
    with np.load(abspath, allow_pickle=allow_pickle) as d:
        return {k: _describe(d[k]) for k in d.files}   # indexing forces the read/decompress


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
    ap.add_argument("--extra", action="append", default=[], metavar="RELPATH",
                    help="additional repo-relative file to protect. Multi-GB inputs (the banks' "
                         "cv.npz, 2.9 GB each) go here rather than in the sweep, so that copying "
                         "gigabytes is always an explicit choice and never a surprise. Repeatable.")
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
    for extra in a.extra:
        p = os.path.join(a.root, extra)
        if not os.path.isfile(p):
            sys.exit(f"FATAL: --extra {extra} does not exist -- refusing to record a protection "
                     f"run that silently skipped a file it was told to protect")
        if extra not in rels:
            rels.append(extra)
    rels = sorted(rels)
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
        "selection": ("npz whose FILENAME contains 'slab' OR whose immediate DIRECTORY name does, plus "
                      "every bank flux_univ_ratio.npy, plus any --extra. The directory clause is "
                      "load-bearing: block slabs are named block5d_*.npz / blockfps_*.npz and a "
                      "filename-only filter finds 365 of 542 while still reporting '0 unreadable'. "
                      "Deliberately EXCLUDED: the banks' per-universe sig_*/td_* arrays (26-37 GB "
                      "each), which are re-THROW inputs, not inputs to this post-hoc rescale."),
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
