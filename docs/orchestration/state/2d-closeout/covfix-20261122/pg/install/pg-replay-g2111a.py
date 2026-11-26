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
                 "shape_check.json", "host_check.json", "revision_end.json", "revision_compare.json",
                 "pin_hash_start.json", "pin_hash_end.json")
TRACES = tuple(n for n in REPLAY_CHECKS if n.startswith("trace_check"))
SPLINE_TRACES = tuple(n for n in TRACES if n != "trace_check_gntpc.json")
SHAPES = ("real_members_listing", "proc_fd_magic_link", "directory_open_recorded", "slot2_reduce_real_path")
HOST_CHECKS = ("st_dev_final_dir", "no_submounts", "result_anchor_real_strace")
# C18: the replay's identity, and what each trace must show: the role's own program first, and these files gated
IDENTITY = {"schema": "covfix-pg-replay-run/4", "tune": "G21_11a_00_000", "slot2": "G18_02a_00_000", "seed": 123456789,
            "events": 100}
PROGRAM = {"trace_check_reduce.json": "awk", "trace_check_reduce_slot2.json": "awk", "trace_check_graphs.json": "gspl2root",
           "trace_check_coverage.json": "gevgen", "trace_check_coverage_slot2.json": "gevgen",
           "trace_check_gevgen.json": "gevgen", "trace_check_gntpc.json": "gntpc"}
GATED = {"trace_check_reduce.json": ("gxspl-NUsmall.xml",), "trace_check_reduce_slot2.json": ("gxspl-NUsmall.xml",),
         "trace_check_graphs.json": ("G21_11a_00_000_CH.xml.gz", "ModelConfiguration.xml"),
         "trace_check_coverage.json": ("G21_11a_00_000_CH.xml.gz", "ModelConfiguration.xml", "Messenger_pg.xml"),
         "trace_check_coverage_slot2.json": ("G18_02a_00_000_CH.xml.gz", "ModelConfiguration.xml", "Messenger_pg.xml"),
         "trace_check_gevgen.json": ("G21_11a_00_000_CH.xml.gz", "ModelConfiguration.xml"), "trace_check_gntpc.json": ()}
DELETABLE = {"t0": ("genie_v3.gst.root", "gevgen.status", "input-flux.root"),   # the wrapper removes t0's GHEP
             "coverage_slot1": ("gevgen.log", "gevgen.status", "gntp.ghep.root", "input-flux.root"),
             "coverage_slot2": ("gevgen.log", "gevgen.status", "gntp.ghep.root", "input-flux.root"),
             "merged": ("genie_v3_g21_ALL.gst.root",)}
PINNED_BY = ("exact pin", "genie manifest", "private members")   # trace_check's own words, and no others
BOUND_BY = ("genie manifest", "system pin")


def _schema_ok(s):
    return (type(s) is dict and sorted(s) == ["keys", "streamer_sha256"] and type(s["keys"]) is list and s["keys"]
            and all(type(k) is list and len(k) == 3 and all(type(y) is str for y in k) for k in s["keys"])
            and _hex64(s["streamer_sha256"]))


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
                                          and x.get("pinned_by") in PINNED_BY for x in v) for v in g.values())):
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
            type(v) is list and v and all(type(e) is dict and all(type(e.get(k)) is str for k in ("path", "real"))
                                          and e.get("bound_by") in BOUND_BY
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
    if not _schema_ok(r.get("gst_schema")):
        p.append("gst schema")
    if not _schema_ok(r.get("gst_merged_schema")):
        p.append("gst merged schema")
    return p


def deleted_problems(d, r=None):
    """[problems] with deleted.json: each run's files, exactly the names it makes, typed records, each ROOT file
    decoded with its name and bytes apart, and each gst's schema the one the replay record carries (r)."""
    if not (type(d) is dict and sorted(d) == sorted(DELETABLE) and all(type(v) is dict for v in d.values())
            and all(sorted(d[k]) == sorted(DELETABLE[k]) for k in d)):
        return ["names"]
    r = r or {}
    p = [f"{k}/{n}: schema differs from the record's" for k, n, f in (("t0", "genie_v3.gst.root", "gst_schema"),
         ("merged", "genie_v3_g21_ALL.gst.root", "gst_merged_schema")) if (d[k][n] if type(d[k][n]) is dict else {}).get("schema") != r.get(f)]
    def root_ok(n, v):   # C4's positive control: each ROOT file decoded (inflated), the gst's schema recorded
        if not n.endswith(".root"):
            return True
        c = v.get("decoded")
        return (type(c) is dict and type(c.get("holds_seed")) is bool and type(c.get("name_holds_seed")) is bool
                and type(c.get("int32_count")) is int and type(c.get("codecs")) is dict
                and type(c.get("bytes_inflated")) is int and type(c.get("hits")) is list
                and type(c.get("seed_objects")) is list and all(   # R1: each object the seed was found in
                    type(o) is dict and type(o.get("class")) is str and type(o.get("inflated")) is bool
                    and o.get("kind") in ("int32-object", "inflated") for o in c["seed_objects"])
                and (not n.endswith(".gst.root") or _schema_ok(v.get("schema"))))
    bad = [f"{k}/{n}" for k in sorted(d) for n, v in sorted(d[k].items())
           if not (type(v) is dict and _hex64(v.get("sha256")) and type(v.get("bytes")) is int and v["bytes"] >= 0
                   and type(v.get("holds_public_seed")) is bool and root_ok(n, v))]
    # K6, the positive control: each coverage GHEP (the public seed its run number) has the seed in decoded bytes
    p += [f"{k}/gntp.ghep.root: the control's seed was not found decoded" for k in ("coverage_slot1", "coverage_slot2")
          if f"{k}/gntp.ghep.root" not in bad and not (
              d[k]["gntp.ghep.root"]["decoded"]["holds_seed"] is True and d[k]["gntp.ghep.root"]["decoded"]["bytes_inflated"] > 0
              and {"inflated", "int32-object"} & set(d[k]["gntp.ghep.root"]["decoded"]["hits"])
              and d[k]["gntp.ghep.root"]["decoded"]["seed_objects"] != [])]
    return p + bad


EVENT_DIRS = ("work/t0", "coverage/G21_11a_00_000", "coverage/G18_02a_00_000", "gst")


def leftovers(run_dir):
    """[relpath]: the public-seed event and status files still under the replay's run directory, each now unlinked
    (an unlink that fails is still listed); a directory the driver never made is empty."""
    out = []
    for d in EVENT_DIRS:
        try:
            names = os.listdir(os.path.join(run_dir, d))
        except FileNotFoundError:
            continue
        for n in names:
            if (n.endswith((".ghep.root", ".gst.root", ".status")) or n == "input-flux.root"
                    or (d.startswith("coverage") and n == "gevgen.log")):
                out.append(f"{d}/{n}")
                try:
                    os.unlink(os.path.join(run_dir, d, n))
                except OSError:
                    pass
    return out


def session_pids(sid, proc="/proc"):
    """[pid]: the live processes of session sid (zombies aside), from /proc on the node, or ps where there is none.
    A process whose state cannot be read counts unless getsid says it is gone."""
    if os.path.isdir(os.path.join(proc, "self")):
        pids = [int(d) for d in os.listdir(proc) if d.isdigit()]

        def state(p):
            try:
                with open(os.path.join(proc, str(p), "stat"), "rb") as f:   # the name is raw bytes: parse after it
                    return f.read().rsplit(b")", 1)[1].split()[0].decode("ascii", "replace")
            except (OSError, IndexError):
                return None
    else:
        r = subprocess.run(["ps", "-A", "-o", "pid=,stat="], capture_output=True, text=True)
        if r.returncode != 0:
            raise OSError("ps failed")
        st = {int(a): b for a, b in (ln.split()[:2] for ln in r.stdout.splitlines() if len(ln.split()) >= 2)}
        pids, state = list(st), st.get
    out = []
    for p in sorted(pids):
        if p == os.getpid() or (state(p) or "").startswith("Z"):
            continue
        try:
            if os.getsid(p) == sid:
                out.append(p)
        except (ProcessLookupError, PermissionError):
            pass
    return out


def quiesce(sid, seconds=30.0, scan=None, kill=os.kill, clock=None, sleep=None):
    """(KILLed, quiet): the driver's session (its own, by start_new_session; GNU timeout gives it a process group,
    not a session) KILLed until two scans in a row, 0.5 s apart, find it empty, for at most `seconds`."""
    import signal
    import time
    if not sid:
        return 0, True
    scan = scan or (lambda: session_pids(sid))
    clock, sleep = clock or time.monotonic, sleep or time.sleep
    end, empties, killed = clock() + seconds, 0, set()
    while True:
        own = scan()
        empties = 0 if own else empties + 1
        for q in own:
            killed.add(q)
            try:
                kill(q, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if empties >= 2 or clock() >= end:
            return len(killed), empties >= 2
        sleep(0.5)


def _run(argv, **k):
    """subprocess.run, keeping the child's pid: with start_new_session it is the driver's session id."""
    child = subprocess.Popen(argv, **k)
    child.wait()
    done = subprocess.CompletedProcess(argv, child.returncode)
    done.pid = child.pid
    return done


def replay(parent=REPLAY_PARENT, archive_b64=None, archive_sha=None, blobs=None, commit=None, ident=identity,
           run=_run, home=None, now=None):
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
            p = None
            try:
                p = run(["/usr/bin/nice", "-n", "19", "/usr/bin/timeout", str(WALL_CAP_S), "bash", driver,
                         "--workdir", os.path.join(w, "run")], cwd=os.path.join(w, "run"), env=env,
                        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            finally:                    # no writer outlives the driver: its session's stragglers are KILLed
                rec["quiesced"], rec["quiet"] = quiesce(getattr(p, "pid", None))
        if rec["quiesced"] or not rec["quiet"]:  # before the files are swept: a straggler could still write
            raise Stop(f"quiesce: {rec['quiesced']} processes outlived the driver"
                       + ("" if rec["quiet"] else ", and its session did not empty in 30 s"))
        rec["driver_rc"] = p.returncode
        with open(os.path.join(w, "driver.log"), "rb") as log:
            rec["driver_lines"] = [ln for ln in log.read().decode(errors="replace").splitlines()
                                   if ln.startswith("[replay]")][-40:]
        if p.returncode != 0:
            raise Stop(f"the replay driver exited {p.returncode}")
        with open(os.path.join(w, "run", "replay.json")) as f:
            r = json.load(f)
        rec["replay"] = r                       # whole: the launcher checks the same record (B3)
        probs = replay_problems(r)
        if probs:
            raise Stop(f"replay-record: {probs}")
        with open(os.path.join(w, "run", "deleted.json")) as f:
            rec["deleted"] = json.load(f)
        if deleted_problems(rec["deleted"], r):
            raise Stop(f"deleted-record: {deleted_problems(rec['deleted'], r)}")
    except (Stop, OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as e:
        rec["stops"].append(f"{type(e).__name__}: {e}")
    except Exception as e:                  # fail closed, with a reason no other test expects
        rec["stops"].append(f"internal-error: {type(e).__name__}")
    finally:                                # every terminal path: any public-seed event file left is removed, a STOP
        if rec.get("replay_dir"):
            left = leftovers(os.path.join(rec["replay_dir"], "run"))
            rec["left"] = len(left)
            if left:
                rec["stops"].append(f"Stop: deleted-record: {len(left)} event or status files were left, now removed")
    rec["verdict"] = "GO" if not rec["stops"] else "STOP"
    return rec


def main():
    rec = replay()
    print(f"verdict {rec['verdict']} stops {rec['stops']}")
    print("PG-RESULT " + json.dumps(rec, sort_keys=True))
    return 0 if rec["verdict"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
