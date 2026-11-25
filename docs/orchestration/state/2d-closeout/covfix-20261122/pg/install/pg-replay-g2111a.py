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


REPLAY_CHECKS = ("tool_check_strace.json", "revision_start.json", "members_check.json", "dbconfig_check.json",
                 "exe_check.json", "reduce_check.json", "argv_check.json", "trace_check_reduce.json",
                 "trace_check_graphs.json", "messenger_check.json", "trace_check_coverage.json", "coverage_check.json",
                 "trace_check_gevgen.json", "trace_check_gntpc.json", "trace_check_reduce_slot2.json",
                 "reduce_check_slot2.json", "trace_check_coverage_slot2.json", "coverage_check_slot2.json",
                 "shape_check.json", "host_check.json", "revision_end.json", "revision_compare.json")
TRACES = tuple(n for n in REPLAY_CHECKS if n.startswith("trace_check"))
SPLINE_TRACES = tuple(n for n in TRACES if n != "trace_check_gntpc.json")
SHAPES = ("real_members_listing", "proc_fd_magic_link", "directory_open_recorded", "slot2_reduce_real_path")
HOST_CHECKS = ("st_dev_final_dir", "no_submounts", "result_anchor_real_strace")
# C18: the replay's identity, and what each trace must show: the role's own program first, and these files gated
IDENTITY = {"schema": "covfix-pg-replay-run/3", "tune": "G21_11a_00_000", "slot2": "G18_02a_00_000", "seed": 123456789,
            "events": 100}
PROGRAM = {"trace_check_reduce.json": "awk", "trace_check_reduce_slot2.json": "awk", "trace_check_graphs.json": "gspl2root",
           "trace_check_coverage.json": "gevgen", "trace_check_coverage_slot2.json": "gevgen",
           "trace_check_gevgen.json": "gevgen", "trace_check_gntpc.json": "gntpc"}
GATED = {"trace_check_reduce.json": ("gxspl-NUsmall.xml",), "trace_check_reduce_slot2.json": ("gxspl-NUsmall.xml",),
         "trace_check_graphs.json": ("G21_11a_00_000_CH.xml.gz", "ModelConfiguration.xml"),
         "trace_check_coverage.json": ("G21_11a_00_000_CH.xml.gz", "ModelConfiguration.xml", "Messenger_pg.xml"),
         "trace_check_coverage_slot2.json": ("G18_02a_00_000_CH.xml.gz", "ModelConfiguration.xml", "Messenger_pg.xml"),
         "trace_check_gevgen.json": ("G21_11a_00_000_CH.xml.gz", "ModelConfiguration.xml"), "trace_check_gntpc.json": ()}
DELETABLE = {"t0": ("genie_v3.gst.root", "gevgen.status", "gntp.ghep.root", "input-flux.root"),
             "coverage_slot1": ("gevgen.log", "gevgen.status", "gntp.ghep.root", "input-flux.root"),
             "coverage_slot2": ("gevgen.log", "gevgen.status", "gntp.ghep.root", "input-flux.root")}


def _hex64(x):
    return type(x) is str and re.fullmatch(r"[0-9a-f]{64}", x) is not None


def _all_true(d, keys):
    return type(d) is dict and sorted(d) == sorted(keys) and all(v is True for v in d.values())


def replay_problems(r):
    """[problems] with pg_replay.sh's replay.json: every named check, spline open, gated list, real shape and host
    check present, exactly, and true; typed records only."""
    p = []
    if r.get("pass") is not True:
        p.append("pass")
    if not _all_true(r.get("checks"), REPLAY_CHECKS):
        p.append("checks")
    if not _all_true(r.get("spline_opened"), SPLINE_TRACES):
        p.append("spline opens")
    g = r.get("gated")
    if not (type(g) is dict and sorted(g) == sorted(TRACES) and all(
            type(v) is list and v and all(type(x) is dict and type(x.get("path")) is str and _hex64(x.get("sha256"))
                                          and type(x.get("pinned_by")) is str for x in v) for v in g.values())):
        p.append("gated files")
    if not _all_true(r.get("real_shapes"), SHAPES):
        p.append("real shapes")
    if not _all_true(r.get("host"), HOST_CHECKS):
        p.append("host checks")
    c = r.get("coverage_log_sha256")
    if not (type(c) is dict and sorted(c) == ["coverage_check.json", "coverage_check_slot2.json"]
            and all(_hex64(v) for v in c.values())):
        p.append("coverage log hashes")
    p += [f"identity {k}" for k, v in IDENTITY.items() if not (type(r.get(k)) is type(v) and r.get(k) == v)]
    x = r.get("execs")
    if not (type(x) is dict and sorted(x) == sorted(TRACES) and all(
            type(v) is list and v and all(type(e) is dict and all(type(e.get(k)) is str for k in ("path", "real", "bound_by"))
                                          and _hex64(e.get("sha256")) for e in v)
            and v[0]["path"].rsplit("/", 1)[-1] == PROGRAM[n] for n, v in x.items())):
        p.append("execs")
    rv = r.get("revision")
    if not (type(rv) is dict and sorted(rv) == ["end", "start"] and all(
            type(v) is dict and all(type(v.get(k)) is str and v[k].strip() for k in ("revision", "root_hash"))
            for v in rv.values())):
        p.append("revision values")
    if type(g) is dict and sorted(g) == sorted(TRACES):
        p += [f"gated {n}: {b}" for n, bs in sorted(GATED.items()) for b in bs
              if not any(type(e) is dict and str(e.get("path", "")).rsplit("/", 1)[-1] == b for e in g[n])]
    s = r.get("gst_schema")
    if not (type(s) is dict and sorted(s) == ["keys", "streamer_sha256"] and type(s["keys"]) is list and s["keys"]
            and all(type(k) is list and len(k) == 3 and all(type(y) is str for y in k) for k in s["keys"])
            and _hex64(s["streamer_sha256"])):
        p.append("gst schema")
    return p


def deleted_problems(d):
    """[problems] with deleted.json: the three runs, the t0 gst among them, only deletable names, typed records."""
    if not (type(d) is dict and sorted(d) == sorted(DELETABLE) and all(type(v) is dict for v in d.values())
            and "genie_v3.gst.root" in d["t0"] and all(set(d[k]) <= set(DELETABLE[k]) for k in d)):
        return ["names"]
    def root_ok(n, v):   # C4's positive control: each ROOT file decoded (inflated), the gst's schema recorded
        if not n.endswith(".root"):
            return True
        c = v.get("decoded")
        return (type(c) is dict and type(c.get("holds_seed")) is bool and type(c.get("int32_count")) is int
                and type(c.get("codecs")) is dict and type(c.get("bytes_inflated")) is int
                and (n != "genie_v3.gst.root" or type(v.get("schema")) is dict))
    return [f"{k}/{n}" for k in sorted(d) for n, v in sorted(d[k].items())
            if not (type(v) is dict and _hex64(v.get("sha256")) and type(v.get("bytes")) is int and v["bytes"] >= 0
                    and type(v.get("holds_public_seed")) is bool and root_ok(n, v))]


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
        rec["replay"] = {k: r.get(k) for k in ("checks", "spline_opened", "gated", "real_shapes", "host",
                                               "coverage_log_sha256", "pass")}
        probs = replay_problems(r)
        if probs:
            raise Stop(f"replay-record: {probs}")
        with open(os.path.join(w, "run", "deleted.json")) as f:
            rec["deleted"] = json.load(f)
        left = [n for d in ("work/t0", "coverage/G21_11a_00_000", "coverage/G18_02a_00_000")
                for n in os.listdir(os.path.join(w, "run", d))
                if n.endswith((".ghep.root", ".gst.root", ".status")) or n == "input-flux.root"
                or (d.startswith("coverage") and n == "gevgen.log")]
        if deleted_problems(rec["deleted"]) or left:
            raise Stop(f"deleted-record: {deleted_problems(rec['deleted'])}, left {left}")
    except (Stop, OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as e:
        rec["stops"].append(f"{type(e).__name__}: {e}")
    except Exception as e:                  # fail closed, with a reason no other test expects
        rec["stops"].append(f"internal-error: {type(e).__name__}")
    rec["verdict"] = "GO" if not rec["stops"] else "STOP"
    return rec


def main():
    rec = replay()
    print(f"verdict {rec['verdict']} stops {rec['stops']}")
    print("PG-RESULT " + json.dumps(rec, sort_keys=True))
    return 0 if rec["verdict"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
