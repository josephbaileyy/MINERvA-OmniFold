"""COV2D staging (COV2D-DECLARATION.md §8, "Lateral I/O"; §7): $CV and the 10 active laterals copied from CFS to this
lane's own new pscratch directory, on a DTN. Each source is read through O_NOATIME (§7: everything but the bound
driver reads that way), and its atime is checked unchanged. Each copy is written as <name>.partial, flushed, re-read
through O_NOATIME and hashed. Its stat must agree before and after the hash, and its sha256 must equal the declared
digest: the CFS SHA256SUMS row for a lateral, CV_SHA for $CV. Then it is renamed and made read-only (0440).

  python3 cov2d_stage.py <manifest tsv: source<TAB>destination<TAB>sha256> <record out> [workers]

The record has part B's format, "sha256 size mtime inode path", one row per copy, in manifest order. Exit 0 when
every copy passes, 4 on any failure. A failed copy is left as <name>.partial for the director and never renamed.
"""
from __future__ import annotations

import hashlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor

CHUNK = 64 << 20


def sha256_noatime(path: str) -> str:
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    try:
        while True:
            b = os.read(fd, CHUNK)
            if not b:
                break
            h.update(b)
    finally:
        os.close(fd)
    return h.hexdigest()


def stat3(path: str) -> str:
    s = os.stat(path)
    return f"{s.st_size} {int(s.st_mtime)} {s.st_ino}"


def one(src: str, dst: str, want: str) -> tuple[bool, str, str]:
    """Copy, hash and seal one file. Returns (ok, record row or "", log line)."""
    part = dst + ".partial"
    a0 = os.stat(src).st_atime_ns
    fi = os.open(src, os.O_RDONLY | os.O_NOATIME)
    fo = os.open(part, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o640)
    try:
        while True:
            b = os.read(fi, CHUNK)
            if not b:
                break
            view = memoryview(b)
            while view:
                view = view[os.write(fo, view):]
        os.fsync(fo)
    finally:
        os.close(fi)
        os.close(fo)
    a1 = os.stat(src).st_atime_ns
    before = stat3(part)
    got = sha256_noatime(part)
    after = stat3(part)
    src_size = os.stat(src).st_size
    log = (f"{os.path.basename(dst)}: src_atime_ns {a0} -> {a1}; size src {src_size} copy {before.split()[0]}; "
           f"sha256 {got}; declared {want}")
    if a1 != a0:
        return False, "", log + "; FAIL the source's atime moved"
    if before != after:
        return False, "", log + "; FAIL the copy changed while hashed"
    if int(before.split()[0]) != src_size:
        return False, "", log + "; FAIL size differs from the source"
    if got != want:
        return False, "", log + "; FAIL sha256 differs from the declared digest"
    os.rename(part, dst)
    os.chmod(dst, 0o440)
    return True, f"{got} {stat3(dst)} {dst}", log + "; ok"


def main(argv: list[str]) -> int:
    manifest, record = argv[0], argv[1]
    workers = int(argv[2]) if len(argv) > 2 else 4
    rows = [line.rstrip("\n").split("\t") for line in open(manifest) if line.strip()]
    if any(len(r) != 3 or len(r[2]) != 64 for r in rows):
        print("REFUSE the manifest needs source, destination and a 64-hex sha256 on every row")
        return 4
    if os.path.exists(record):
        print(f"REFUSE {record} exists")
        return 4
    for _, dst, _ in rows:
        if os.path.exists(dst) or os.path.exists(dst + ".partial"):
            print(f"REFUSE {dst} or its .partial exists")
            return 4
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda r: one(*r), rows))
    for ok, _, log in results:
        print(log, flush=True)
    good = [row for ok, row, _ in results if ok]
    if len(good) != len(rows):
        print(f"STAGE FAIL {len(rows) - len(good)} of {len(rows)} copies failed; no record written")
        return 4
    with open(record + ".partial", "w") as f:
        f.write("\n".join(good) + "\n")
    os.rename(record + ".partial", record)
    os.chmod(record, 0o440)
    print(f"STAGE PASS {len(good)} of {len(rows)} copies; record {record} sha256 {sha256_noatime(record)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
