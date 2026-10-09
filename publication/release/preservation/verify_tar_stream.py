#!/usr/bin/env python3
"""Read a tar stream on stdin and check every member's sha256 against a sha256sum-format list (read-back verify).

  hsi -q "get - : <archive.tar>" | python3 verify_tar_stream.py <SHA256SUMS> <member prefix>

Member names are <prefix>/<path in SHA256SUMS>; further sum lists may follow (e.g. the archive's own metadata files).
Exit 0 only if every listed file is present exactly once with its digest and the stream holds no other regular file,
except htar's own consistency-check member (/tmp/HTAR_CF_CHK_*), which is reported and not counted.
"""
import hashlib
import sys
import tarfile

sums, prefix, more = sys.argv[1], sys.argv[2].rstrip("/") + "/", sys.argv[3:]


def strip(s, pre):  # str.removeprefix, for the Python 3.6 on Perlmutter login nodes
    return s[len(pre):] if s.startswith(pre) else s

want = {}
for path in [sums] + more:
    for line in open(path):
        h, p = line.rstrip("\n").split(None, 1)
        want[strip(p.lstrip("*"), "./")] = h
htar_chk = []
seen, bad, extra = {}, [], []
with tarfile.open(fileobj=sys.stdin.buffer, mode="r|") as tar:
    for m in tar:
        if not m.isfile():
            continue
        if m.name.startswith("/tmp/HTAR_CF_CHK_"):
            htar_chk.append(m.name)
            continue
        rel = strip(m.name, prefix)
        h = hashlib.sha256()
        f = tar.extractfile(m)
        for block in iter(lambda: f.read(1 << 22), b""):
            h.update(block)
        if rel not in want:
            extra.append(rel)
        elif h.hexdigest() != want[rel]:
            bad.append(rel)
        seen[rel] = seen.get(rel, 0) + 1
missing = [p for p in want if p not in seen]
dups = [p for p, n in seen.items() if n > 1]
print(f"members {sum(seen.values())}; listed {len(want)}; missing {len(missing)}; digest mismatches {len(bad)}; "
      f"unlisted {len(extra)}; duplicates {len(dups)}; htar check members {len(htar_chk)}")
for label, lst in (("MISSING", missing), ("MISMATCH", bad), ("UNLISTED", extra), ("DUPLICATE", dups)):
    for p in lst[:20]:
        print(label, p)
sys.exit(0 if not (missing or bad or extra or dups) else 1)
