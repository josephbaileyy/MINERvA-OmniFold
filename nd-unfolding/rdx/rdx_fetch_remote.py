#!/usr/bin/env python3
"""RDX's read-only fetch (RDX-BINDING-1 addendum J7, ruling 2): the 15 stage-3 products, their 15 inventories and the
two job logs, read O_NOATIME on a login node and streamed to the laptop as one tar on stdout. Python 3.6-compatible:
on the login node it runs under /usr/bin/python3 (3.6.15), fed through ssh's stdin, so nothing is staged or written on
the cluster, not even under /dev/shm.

    fetch (on loginNN, no arguments):  /usr/bin/python3 - < rdx_fetch_remote.py > fetch.tar
    unpack (on the laptop):            python3 rdx_fetch_remote.py unpack <fetch.tar> <new empty dir>

fetch refuses before writing anything to stdout:
  - exit 3 if the platform has no O_NOATIME;
  - exit 9 if sacct fails, or if any job of the fenced families is in a non-terminal state (STATES: pending,
    configuring, running, completing, requeued, resizing, suspended; sacct only, never squeue);
  - exit 4 if a file is missing.
It then streams each file with its manifest: bytes, sha256, and the file's stat before and after its read (size,
mtime_ns, atime_ns, ino, dev). The manifest is the last member. It exits 8 if any file's stat moved during its read or
its length is not the stat's size (an atime, or a rewrite of the same length: a STOP for the director). The fence is
read again after the last file; a job seen then exits 9. The tar is complete in both cases, and unpack refuses it.
unpack refuses (exit 2) unless the tar holds exactly the declared 32 files and manifest.json, every member is a plain
file at a declared relative path, the root read is the declared one, every sha256 matches the manifest, O_NOATIME was used, every file's two stats are
equal, and both fence reads were clear. It writes the files under <dir>/ and nothing else.

MEASURES: nothing; it copies. CANNOT AUTHORIZE: a reading.
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import time

DECLARED_ROOT = "/pscratch/sd/j/josephrb/rdx-20261112b/out"
ROOT = os.environ.get("RDX_FETCH_TEST_ROOT") or DECLARED_ROOT
TASKS = ("X0", "X0_lat", "X1", "X1p", "X1w", "X1t", "X0c", "X1c", "X1pc", "X1wc", "X0t", "X0g", "X1g", "X0q", "X1q")
LOGS = ("logs/rdx_s3_a_61478320.out", "logs/rdx_s3_b_61481240.out")
FILES = tuple("products/%s.npz" % t for t in TASKS) + tuple("inventory/%s.jsonl" % t for t in TASKS) + LOGS
FENCE = re.compile(r"^(cov2d|t2a|ll5d|e96data|rpd_|rsn_|rdx_|pfb_|ibukt-)")
STATES = "PD,CF,R,CG,RQ,RS,S"  # sacct's non-terminal job states: a completing or configuring job can still write
STAT_KEYS = ("st_size", "st_mtime_ns", "st_atime_ns", "st_ino", "st_dev")
USER = "josephrb"
SCHEMA = "rdx-fetch/1"


def refuse(rc, why):
    sys.stderr.write("refusing: %s\n" % why)
    sys.exit(rc)


def fence_read():
    """One sacct read: {"command", "rows", "hits", "clear"}; "error" instead of rows if sacct failed."""
    cmd = ["sacct", "-X", "-n", "-P", "-u", USER, "-s", STATES, "-o", "JobID,JobName,State"]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except OSError as exc:
        return {"command": " ".join(cmd), "error": "sacct could not run: %s" % exc, "clear": False}
    if p.returncode != 0:
        return {"command": " ".join(cmd), "error": "sacct failed (rc %d): %s" % (p.returncode, p.stderr.strip()[:200]),
                "clear": False}
    rows = [ln for ln in p.stdout.splitlines() if ln.strip()]
    hits = [ln for ln in rows if len(ln.split("|")) > 1 and FENCE.match(ln.split("|")[1])]
    return {"command": " ".join(cmd), "rows": rows, "hits": hits, "clear": not hits}


def fence():
    f = fence_read()
    if not f["clear"]:
        refuse(9, f.get("error") or "fenced jobs are in a non-terminal state: %s" % f["hits"])
    return f


def stat_record(path):
    st = os.stat(path)
    return dict((k, getattr(st, k)) for k in STAT_KEYS)


def fetch():
    noatime = getattr(os, "O_NOATIME", None)
    test = bool(os.environ.get("RDX_FETCH_TEST_ROOT"))
    if noatime is None and not test:
        refuse(3, "this platform has no O_NOATIME")
    f = fence()
    for rel in FILES:
        if not os.path.isfile(os.path.join(ROOT, rel)):
            refuse(4, "no %s" % os.path.join(ROOT, rel))
    out = sys.stdout.buffer
    tf = tarfile.open(fileobj=out, mode="w|")
    man = {"schema": SCHEMA, "root": ROOT, "host": os.uname()[1], "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "o_noatime": noatime is not None, "fence": f, "files": []}
    moved = []
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        st0 = stat_record(p)
        fd = os.open(p, os.O_RDONLY | (noatime or 0))
        with os.fdopen(fd, "rb") as fh:
            data = fh.read()
        st1 = stat_record(p)
        info = tarfile.TarInfo(rel)
        info.size, info.mtime, info.mode = len(data), st0["st_mtime_ns"] // 10 ** 9, 0o600
        tf.addfile(info, io.BytesIO(data))
        rec = {"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
               "stat_before": st0, "stat_after": st1}
        rec["moved"] = [k for k in STAT_KEYS if st0[k] != st1[k]] + (["length"] if len(data) != st0["st_size"] else [])
        if rec["moved"]:
            moved.append(rel)
        man["files"].append(rec)
    man["atime_moved"] = moved  # every file whose stat moved during its read (the name is the schema's)
    man["fence_after"] = fence_read()
    blob = (json.dumps(man, indent=1, sort_keys=True) + "\n").encode()
    info = tarfile.TarInfo("manifest.json")
    info.size, info.mtime, info.mode = len(blob), int(time.time()), 0o600
    tf.addfile(info, io.BytesIO(blob))
    tf.close()
    out.flush()
    if not man["fence_after"]["clear"]:
        sys.stderr.write("STOP: the fence read after the last file is not clear: %s\n"
                         % (man["fence_after"].get("error") or man["fence_after"]["hits"]))
        return 9
    if moved:
        sys.stderr.write("STOP: the stat of %s moved during its read\n" % moved)
        return 8
    return 0


def unpack(tar_path, dest):
    want = set(FILES) | {"manifest.json"}
    if not os.path.isdir(dest) or os.listdir(dest):
        refuse(2, "%s is not a new empty directory" % dest)
    members = {}
    with tarfile.open(tar_path, mode="r:") as tf:
        for m in tf.getmembers():
            if not m.isfile() or m.name not in want or m.name in members:
                refuse(2, "an unexpected, repeated or non-file member: %r" % m.name)
            members[m.name] = tf.extractfile(m).read()
    if set(members) != want:
        refuse(2, "missing members: %s" % sorted(want - set(members)))
    man = json.loads(members["manifest.json"].decode())
    if man.get("schema") != SCHEMA or not man.get("o_noatime") or man.get("atime_moved") or not man["fence"].get("clear") \
            or not man.get("fence_after", {}).get("clear"):
        refuse(2, "the manifest records no O_NOATIME, a moved atime or stat, or a fence that was not clear")
    if man.get("root") != (os.environ.get("RDX_FETCH_TEST_ROOT") or DECLARED_ROOT):
        refuse(2, "the manifest's root %r is not the declared %s" % (man.get("root"), DECLARED_ROOT))
    recs = {r["path"]: r for r in man["files"]}
    if set(recs) != set(FILES):
        refuse(2, "the manifest does not list exactly the declared files")
    for rel in FILES:
        r = recs[rel]
        if r.get("stat_before") != r.get("stat_after") or not r.get("stat_before") \
                or r["stat_before"].get("st_size") != r["bytes"]:
            refuse(2, "%s: its stat moved during the read" % rel)
        if hashlib.sha256(members[rel]).hexdigest() != recs[rel]["sha256"] or len(members[rel]) != recs[rel]["bytes"]:
            refuse(2, "%s does not match its manifest sha256" % rel)
    for rel, data in members.items():
        p = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(p) or dest, exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(data)
    print(json.dumps({"unpacked": len(FILES), "host": man["host"], "utc": man["utc"], "fence_rows": len(man["fence"]["rows"])}))
    return 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["unpack"] and len(sys.argv) == 4:
        sys.exit(unpack(sys.argv[2], sys.argv[3]))
    if len(sys.argv) > 1 and sys.argv[1:] != ["-"]:
        refuse(2, "usage: python3 - < rdx_fetch_remote.py  |  rdx_fetch_remote.py unpack <tar> <dir>")
    sys.exit(fetch())
