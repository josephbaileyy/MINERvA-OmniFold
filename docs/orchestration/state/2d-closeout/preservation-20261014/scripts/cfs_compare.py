"""Compare the CFS data copy's file listing with the committed checksum manifest (names and bytes).

Usage: python3 -I cfs_compare.py MANIFEST CFS_FILES_TSV OUT_JSON

MANIFEST: publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv
CFS_FILES_TSV: cfs_facts.sh output (relpath, bytes, mtime) for
  /global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/anatuple-data-20261009
Population: every manifest row under Data/, MATFluxAndReweightFiles/ or MParamFiles/.
This checks presence and byte count only; the sha256 verification is the 2026-10-09/10 copy records.
"""
import json
import os
import sys

DEST = "/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/anatuple-data-20261009"
TREES = ("Data/", "MATFluxAndReweightFiles/", "MParamFiles/")


def main(manifest, listing, out):
    want = {}
    with open(manifest) as fh:
        next(fh)
        for line in fh:
            sha, size, mtime, rel = line.rstrip("\n").split("\t")
            if rel.startswith(TREES):
                want[rel] = (int(size), mtime)
    have = {}
    with open(listing) as fh:
        for line in fh:
            rel, size, mtime = line.rstrip("\n").split("\t")
            have[rel] = (int(size), mtime)
    per = {}
    for t in TREES:
        rows = [r for r in want if r.startswith(t)]
        per[t.rstrip("/")] = {
            "manifest_files": len(rows),
            "manifest_bytes": sum(want[r][0] for r in rows),
            "present_same_bytes": sum(r in have and have[r][0] == want[r][0] for r in rows),
            "present_same_bytes_and_mtime": sum(r in have and have[r] == want[r] for r in rows),
            "cfs_bytes_of_present": sum(have[r][0] for r in rows if r in have),
        }
    missing = sorted(f"{DEST}/{r}" for r in want if r not in have)
    size_diff = sorted(f"{DEST}/{r}" for r in want if r in have and have[r][0] != want[r][0])
    extra = sorted(f"{DEST}/{r}" for r in have if r not in want)
    res = {
        "dest": DEST,
        "manifest": os.path.abspath(manifest),
        "listing": os.path.abspath(listing),
        "per_tree": per,
        "manifest_files_total": len(want),
        "manifest_bytes_total": sum(v[0] for v in want.values()),
        "missing": missing,
        "size_differs": size_diff,
        "extra_files_not_in_manifest": extra,
        "cfs_files_total": len(have),
        "cfs_bytes_total": sum(v[0] for v in have.values()),
    }
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "extra_files_not_in_manifest"}, indent=1))
    print("extra:", len(extra), extra[:20])


if __name__ == "__main__":
    main(*sys.argv[1:4])
