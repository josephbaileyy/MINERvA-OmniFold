"""J1's coverage reader: every executable line of each named file never executed, counting the hits of any traced copy
whose sha256 (recorded by the tracer at exit) equals the worktree file's, so a test's fixture deploy counts.
    python uncovered_j1.py <worktree> <trace dir> <repo-relative path> ..."""
import glob
import hashlib
import os
import sys

W, OUT, rels = sys.argv[1], sys.argv[2], sys.argv[3:]
raw, sha = {}, {}
for f in glob.glob(os.path.join(OUT, "*.txt")):
    for ln in open(f):
        if ln.startswith("#sha256 "):
            _, h, p = ln.rstrip("\n").split(" ", 2)
            sha.setdefault(p, set()).add(h)
            continue
        p, _, l = ln.rstrip().rpartition(":")
        raw.setdefault(p, set()).add(int(l))
for rel in rels:
    path = os.path.realpath(os.path.join(W, rel))
    src = open(path, "rb").read()
    want = hashlib.sha256(src).hexdigest()
    hits, copies = set(), 0
    for p, ls in raw.items():
        if p.endswith("/" + rel) and sha.get(p) == {want}:
            hits |= ls
            copies += 1
    lines = set()

    def walk(co):
        for _, _, l in co.co_lines():
            if l:
                lines.add(l)
        for k in co.co_consts:
            if hasattr(k, "co_lines"):
                walk(k)
    walk(compile(src, path, "exec"))
    text = src.decode().splitlines()
    miss = sorted(l for l in lines if l not in hits)
    print(f"{rel} (sha256 {want}): {len(lines)} executable lines, {len(miss)} never executed "
          f"(hits from {copies} byte-identical copies)")
    for l in miss:
        print(f"  {l}: {text[l - 1].strip()}")
