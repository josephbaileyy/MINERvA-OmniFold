#!/usr/bin/env python3
"""Hash SB1's input files and record their identity, for the bracketing hash jobs H0 and H1.

    python3 sb1_hash.py --out RECORD.json FILE [FILE ...]

Writes ``{"schema": "sb1-hashes/1", "files": {abspath: {sha256, size, mtime_ns, ino, seconds}}}``.
Each file is stat'ed before and after it is read; a change refuses (exit 3) and no record is
written. Standard library only, one stream per file, 4 MiB blocks. The benchmark jobs never hash
the 171 GB universe file themselves: reading it on their node would warm that node's page cache
before the timed read (and cost about 0.05-0.1 node-h each). They compare size, mtime and inode
with H0's record at their start and end instead (``sb1_run.py --input-hashes``).
"""

import argparse
import datetime
import hashlib
import json
import os
import socket
import sys
import time


def stat(path):
    st = os.stat(path)
    return {"size": st.st_size, "mtime_ns": st.st_mtime_ns, "ino": st.st_ino}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("files", nargs="+")
    a = ap.parse_args(argv)
    if os.path.lexists(a.out):
        print(f"[REFUSED] {a.out} exists", file=sys.stderr)
        return 3
    rec = {"schema": "sb1-hashes/1", "host": socket.gethostname(),
           "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
           "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "files": {}}
    for path in a.files:
        full = os.path.realpath(path)
        before = stat(full)
        t0 = time.perf_counter()
        h = hashlib.sha256()
        with open(full, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 22), b""):
                h.update(block)
        seconds = time.perf_counter() - t0
        if stat(full) != before:
            print(f"[REFUSED] {full} changed while it was hashed", file=sys.stderr)
            return 3
        rec["files"][full] = dict(before, sha256=h.hexdigest(), seconds=round(seconds, 3))
        print(f"[sb1-hash] {h.hexdigest()}  {before['size']} B  {seconds:.1f} s  {full}",
              flush=True)
    rec["ended_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(a.out, "x") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
