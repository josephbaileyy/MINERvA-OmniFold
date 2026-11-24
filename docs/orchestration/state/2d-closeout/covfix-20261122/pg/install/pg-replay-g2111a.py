"""B3: the login-node replay of slot 1 (G21_11a_00_000), from a git archive of the pinned commit carried in this file.

Run by pg-node-launch.py as `env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -` with this file on
stdin (state/2d-closeout/covfix-20261122/pg/PLAN-SLOT1-PROBE.md, B3, approved; the director's ruling on B3's
deploy). Standard library only. It touches no existing deploy, and writes only under a fresh REPLAY_PARENT/replay-<utc>.

0. Identity first (hostname login<NN>, /pscratch, /global/common, CVMFS). The replay directory must not exist.
1. ARCHIVE_B64 (git archive of COMMIT's ARCHIVE_PATHS, gzip -n) must hash to ARCHIVE_SHA256, or nothing is written.
2. It is unpacked into <replay>/deploy: directories and regular files only (a link, an absolute name or a '..' is a
   STOP), each file created with O_CREAT|O_EXCL|O_NOFOLLOW. Then the tree must be exactly BLOBS: each file's git blob
   hash equal to `git ls-tree -r COMMIT`'s, nothing missing, nothing extra.
3. <replay>/deploy/3d-unfolding/genie/pg_replay.sh runs under nice -n 19 and a wall cap, with HOME, PATH=/usr/bin:/bin
   and TMPDIR=<replay>/tmp: pg_generate.sh's checks before generation, then 100 events at the public seed 123456789,
   each traced and trace-checked (COVFIX rev 12 section 4.1, 783188cd). The event and status files are deleted unread.
4. The receipt carries the commit, the archive's sha256, the blob check, the driver's rc and its pass/STOP lines, and
   replay.json: each check's pass, each traced run's spline open, and the gated files each opened with their sha256.

The last line is `PG-RESULT <json>` (schema covfix-pg-replay/1). Exit 0 on GO, 3 on STOP.

MEASURES: conditions 2 and 3 for slot 1 on a login node. CANNOT AUTHORIZE: generation, or the compute-node trace the
bound binary must still show.
"""
import base64
import datetime
import hashlib
import io
import json
import os
import pwd
import re
import socket
import subprocess
import sys
import tarfile

SCHEMA = "covfix-pg-replay/1"
REPLAY_PARENT = "/pscratch/sd/j/josephrb/covfix-pg"
WALL_CAP_S = 7200
O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
COMMIT = None
ARCHIVE_PATHS = []
ARCHIVE_SHA256 = None
BLOBS_JSON = r'''{}'''
ARCHIVE_B64 = ""


class Stop(Exception):
    pass


def identity():
    host = socket.gethostname()
    checks = {"hostname login<NN>": bool(re.fullmatch(r"login\d{2}", host)),
              "/pscratch": os.path.isdir("/pscratch"), "/global/common": os.path.isdir("/global/common"),
              "CVMFS products": os.path.isdir("/cvmfs/larsoft.opensciencegrid.org/products")}
    return {"host": host, "checks": checks, "pass": all(checks.values())}


def git_blob(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def unpack(data, dest, blobs):
    """Write the archive's directories and files beneath dest, then check the tree is exactly blobs."""
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for m in tf:
            n = m.name.rstrip("/")
            parts = n.split("/")
            if not n or n.startswith("/") or ".." in parts or "" in parts:
                raise Stop(f"archive member {m.name!r}")
            path = os.path.join(dest, n)
            if m.isdir():
                os.makedirs(path, 0o755, exist_ok=True)
            elif m.isreg():
                if n not in blobs:
                    raise Stop(f"{n} is not a pinned blob")
                os.makedirs(os.path.dirname(path), 0o755, exist_ok=True)
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | O_NOFOLLOW, 0o755 if m.mode & 0o111 else 0o644)
                try:
                    b = tf.extractfile(m).read()
                    while b:
                        b = b[os.write(fd, b):]
                finally:
                    os.close(fd)
            else:
                raise Stop(f"{n} is neither a directory nor a regular file")
    seen = {}
    for d, dirs, files in os.walk(dest):
        for f in files:
            p = os.path.join(d, f)
            if os.path.islink(p):
                raise Stop(f"{p} is a link")
            with open(p, "rb") as fh:
                seen[os.path.relpath(p, dest)] = git_blob(fh.read())
    probs = [f"missing: {n}" for n in sorted(set(blobs) - set(seen))]
    probs += [f"extra: {n}" for n in sorted(set(seen) - set(blobs))]
    probs += [f"{n}: blob differs" for n in sorted(set(seen) & set(blobs)) if seen[n] != blobs[n]]
    if probs:
        raise Stop(f"the deploy differs from the commit's blobs: {probs}")
    return len(seen)


def replay(parent=REPLAY_PARENT, archive_b64=None, archive_sha=None, blobs=None, commit=None, ident=identity,
           run=subprocess.run, home=None, now=None):
    archive_b64 = ARCHIVE_B64 if archive_b64 is None else archive_b64
    archive_sha = archive_sha or ARCHIVE_SHA256
    blobs = blobs if blobs is not None else json.loads(BLOBS_JSON)
    commit = commit or COMMIT
    stamp = (now or datetime.datetime.now(datetime.timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    rec = {"schema": SCHEMA, "commit": commit, "archive_sha256_pin": archive_sha, "n_blobs": len(blobs), "stops": []}
    rec["identity"] = ident()
    try:
        if not rec["identity"]["pass"]:
            raise Stop("identity: not a Perlmutter login node; nothing was written")
        if not (commit and archive_sha and blobs and archive_b64):
            raise Stop("the archive, its sha256, its blobs or the commit is not embedded")
        data = base64.b64decode(archive_b64, validate=True)
        rec["archive_sha256"] = hashlib.sha256(data).hexdigest()
        if rec["archive_sha256"] != archive_sha:
            raise Stop("the archive differs from its pin; nothing was written")
        w = os.path.join(parent, f"replay-{stamp}")
        rec["replay_dir"] = w
        if os.path.lexists(w):
            raise Stop(f"{w} already exists")
        os.makedirs(parent, exist_ok=True)
        os.mkdir(w, 0o700)
        for d in ("deploy", "tmp", "run"):
            os.mkdir(os.path.join(w, d), 0o700)
        rec["n_files_checked"] = unpack(data, os.path.join(w, "deploy"), blobs)
        driver = os.path.join(w, "deploy", "3d-unfolding", "genie", "pg_replay.sh")
        env = {"PATH": "/usr/bin:/bin", "HOME": home or pwd.getpwuid(os.getuid()).pw_dir,
               "TMPDIR": os.path.join(w, "tmp"), "LC_ALL": "C"}
        with open(os.path.join(w, "driver.log"), "wb") as log:
            p = run(["/usr/bin/nice", "-n", "19", "/usr/bin/timeout", str(WALL_CAP_S), "bash", driver, "--workdir",
                     os.path.join(w, "run")], cwd=os.path.join(w, "run"), env=env, stdin=subprocess.DEVNULL,
                    stdout=log, stderr=subprocess.STDOUT)
        rec["driver_rc"] = p.returncode
        with open(os.path.join(w, "driver.log"), "rb") as log:
            rec["driver_lines"] = [ln for ln in log.read().decode(errors="replace").splitlines()
                                   if ln.startswith("[replay]")][-40:]
        if p.returncode != 0:
            raise Stop(f"the replay driver exited {p.returncode}")
        with open(os.path.join(w, "run", "replay.json")) as f:
            r = json.load(f)
        rec["replay"] = {k: r.get(k) for k in ("checks", "spline_opened", "gated", "pass")}
        if r.get("pass") is not True:
            raise Stop("the replay's checks did not all pass")
    except (Stop, OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as e:
        rec["stops"].append(f"{type(e).__name__}: {e}")
    rec["verdict"] = "GO" if not rec["stops"] else "STOP"
    return rec


def main():
    rec = replay()
    print(f"verdict {rec['verdict']} stops {rec['stops']}")
    print("PG-RESULT " + json.dumps(rec, sort_keys=True))
    return 0 if rec["verdict"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
