#!/usr/bin/env python3
"""PILOT-FB's copy connect (PILOT-FB-BINDING-1 addendum C1, ruling 3 step 3; revision 2, the copy-connect read's
K1-K8): RS1's 21 A0 products and the sigma receipt, read O_NOATIME and copied into the stage the login-node smoke
created, as plain files of their own. Python 3.6-compatible. On a login node it is executed by the launcher's fixed
bootstrap, which reads these bytes from ssh's stdin, refuses (exit 10) unless their sha256 is the pin on its command
line, and executes exactly those bytes with the deploy as the one argument. It writes nothing but the stage's a0-refs/
(21 files) and assess_receipt.json, through descriptors anchored at the stage; nothing on CFS; no job and no sbatch.

    copy (on loginNN, via the bootstrap):  pfb_copy_remote.py <deploy>              (the manifest on stdout)
    verify (on the laptop, the same bytes): pfb_copy_remote.py verify <copy-manifest.json>

The production entry refuses (exit 2) if any PFB_COPY_* variable is set: tests use their own entry module
(tests/pfb_copy_testentry.py), which builds a Config of its own. copy refuses before it writes anything:
  - exit 3 if the platform has no O_NOATIME, or an O_NOATIME open is refused (EPERM);
  - exit 9 if sacct (/usr/bin/sacct, a fixed environment) is absent or fails, or any row lacks a field, or a job of a
    fenced family is in a non-terminal state (a 14-day read, each State classified);
  - exit 2 if the deploy is not an absolute /pscratch path or not a git checkout; if the stage, opened
    O_DIRECTORY|O_NOFOLLOW, is not physically the literal declared path; if its smoke-receipt.json is not a plain file
    of its own, not JSON, or does not name this stage, this deploy's pin, a production smoke and an INDEX sha256; or
    if the stage already holds a0-refs/ or assess_receipt.json;
  - exit 5 if a source is missing, a symlink, or not a regular file (opened O_NOFOLLOW);
  - exit 4 if a source's sha256 is not its pin;
  - exit 8 if a source's open descriptor's fstat (size, mtime_ns, ctime_ns, atime_ns, mode, nlink, ino, dev) moved
    during its read, or a path lstat before or after does not identify that descriptor;
  - exit 6 on any other I/O error while reading.
Then mkdir a0-refs and every O_CREAT|O_EXCL|O_NOFOLLOW create are made through the stage's descriptor (dir_fd), and
each copy is checked through its own descriptor: a plain file with one link, an inode that is not its source's,
physically at its literal declared path, and its sha256 read back at the pin. Any write-side I/O error or failed check
is exit 6, a STOP: a partial-state manifest names what was created, and it stays in place. The fence is read again at
the end (exit 9 if not clear). verify (exit 2 on any defect) requires a typed record for each of the 22 copies and
both fence reads with their rows.

MEASURES: nothing; it copies. CANNOT AUTHORIZE: the job, which needs the director's own go.
"""
import collections
import errno
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import time

STAGE_DECLARED = "/pscratch/sd/j/josephrb/pfb-20261117-stage"
A0_DIR_DECLARED = "/pscratch/sd/j/josephrb/rs1-a1-20261107/runs/A0"
DEPLOY_PREFIX = "/pscratch/sd/j/josephrb/"
SACCT_DECLARED = "/usr/bin/sacct"
GIT = "/usr/bin/git"
SIGMA_REL = "docs/orchestration/state/s5e/cand/assess_receipt.json"
SIGMA_NAME = "assess_receipt.json"
SIGMA_SHA256 = "84266e309d1aae0d2db1db315750b8164413a7d0125fcaa4a6c9b25834261a2c"  # rounding_mechanism_analyze.py:44
A0_PINS = {  # RS1's committed runs-SHA256SUMS (receipts/full-a1/read/), runs/A0/: the base and jitters 1-20
    "rs1_A0_b-_j-.npz": "fd9f4b353915916a4af97e9594ce0c6507ebc9698c31519a5488a0eb635af7b8",
    "rs1_A0_b-_j1.npz": "80c2a7104f5dabd9756716b75fb94f56aa63bbd2bd86efa725d3ba83e94f76da",
    "rs1_A0_b-_j2.npz": "b40cc42b963f006297d2c9d1e6edb927e71faabfd14335c03334d181f0c85bb7",
    "rs1_A0_b-_j3.npz": "096e8449f38bf3e6ea0a399923d0696cb982f8a13671dae78ede751985b948ac",
    "rs1_A0_b-_j4.npz": "b6ced604929961499cd023b283260901df25be5061591b5ea9e08be2072605e3",
    "rs1_A0_b-_j5.npz": "79d8bdc2eaeb399a0c477bbab3f1b1bc2c73e776d98c84c1f4f358fe946cff8c",
    "rs1_A0_b-_j6.npz": "f3b6a170b09210bddfaadabfe05f7941bfd89d64597fcde5fce42920a74d2f1c",
    "rs1_A0_b-_j7.npz": "c229bb1beaeddff8798156bea2f397f51ecb28ccbdc06a780663fa2ffba224aa",
    "rs1_A0_b-_j8.npz": "75a2d2c2500420df185a99db894b15c22fb4f5a3c3d580a954828a43f5d2dba5",
    "rs1_A0_b-_j9.npz": "02c9ef111f63bd14705d8e6664dc443f2c3e5651883ebe3dad4b94c944b4a2ed",
    "rs1_A0_b-_j10.npz": "3b572eda52444e66211ca60341fd9565f049d2247a7829875455382e1e395a75",
    "rs1_A0_b-_j11.npz": "ef85aa4c0703ad57074b3f44897aa1407bcc8fa8ef6b510ba51d45b74a88e491",
    "rs1_A0_b-_j12.npz": "208ceb24109ce8e0a19dc32ebced0d3d3c7cf26974c70fa277c69265ca5f20bd",
    "rs1_A0_b-_j13.npz": "12db3d05e6d649828648846368a7383bac7e3acf916b9b70602882f431a30306",
    "rs1_A0_b-_j14.npz": "fbf6219c48ce6fdb9c960c42daa78854b6c5a808ecebd61e8cd028aa179b61d2",
    "rs1_A0_b-_j15.npz": "2f6c8a084dc21a7eb18c1308767a131def01505e0b408811ffbf53df85e43630",
    "rs1_A0_b-_j16.npz": "50cff270565ab91f0d55f31699c111b57ce7a4af08d0b6e61836d47d5312e21a",
    "rs1_A0_b-_j17.npz": "a91ec82c491e41522f921b737ca0b9e65017008773221901b6bfc5c9bea8d5df",
    "rs1_A0_b-_j18.npz": "a3e6cd7538a9aaf1ef4bda78734e894e3b1bdfae4d6ca7e20297dec46a08db89",
    "rs1_A0_b-_j19.npz": "19a31f7b5188d87fd27290194ce09d7110ef5118ae6c5c974399f49bc2cbb3cf",
    "rs1_A0_b-_j20.npz": "965e901d7086cba9e332ca6cde9d0d0c3598920ad7d6b4763c0e3aafedb24aec",
}
FENCE = re.compile(r"^(cov2d|t2a|ll5d|e96data|rpd_|rsn_|rdx_|pfb_|ibukt-)")
TERMINAL = frozenset(("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "BOOT_FAIL",
                      "DEADLINE", "PREEMPTED", "REVOKED"))
CANCELLED_BY = re.compile(r"CANCELLED by \d+")
SHA_HEX = re.compile(r"[0-9a-f]{64}")
FD_KEYS = ("st_size", "st_mtime_ns", "st_ctime_ns", "st_atime_ns", "st_mode", "st_nlink", "st_ino", "st_dev")
USER = "josephrb"
SCHEMA = "pfb-copy/2"

Config = collections.namedtuple("Config", "stage a0_dir pins sacct deploy_prefix require_noatime")


def production_config():
    pins = dict(A0_PINS)
    pins[SIGMA_NAME] = SIGMA_SHA256
    return Config(STAGE_DECLARED, A0_DIR_DECLARED, pins, SACCT_DECLARED, DEPLOY_PREFIX, True)


class Stop(Exception):
    def __init__(self, rc, why):
        Exception.__init__(self, why)
        self.rc, self.why = rc, why


def fd_path(fd):
    """The physical path of an open descriptor: /proc/self/fd on Linux; F_GETPATH where there is no /proc."""
    try:
        return os.readlink("/proc/self/fd/%d" % fd)
    except OSError:
        import fcntl
        return fcntl.fcntl(fd, 50, b"\0" * 1024).split(b"\0", 1)[0].decode()


def terminal(state):
    return state in TERMINAL or bool(CANCELLED_BY.fullmatch(state))


def fence_read(sacct):
    cmd = [sacct, "-X", "-n", "-P", "-u", USER, "-S", "now-14days", "-o", "JobID,JobName,State"]
    rec = {"command": " ".join(cmd), "rows": [], "hits": []}
    if not os.path.isfile(sacct):
        return dict(rec, error="sacct is not at %s" % sacct, clear=False)
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                           env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "HOME": os.environ.get("HOME", "/"),
                                "USER": USER})
    except OSError as exc:
        return dict(rec, error="sacct could not run: %s" % exc, clear=False)
    rows = [ln for ln in p.stdout.splitlines() if ln.strip()]
    rec["rows"] = rows
    if p.returncode != 0:
        return dict(rec, error="sacct failed (rc %d): %s" % (p.returncode, p.stderr.strip()[:200]), clear=False)
    bad = [ln for ln in rows if len(ln.split("|")) != 3 or any(not f.strip() for f in ln.split("|"))]
    if bad:
        return dict(rec, error="sacct rows with a missing or blank field: %s" % bad[:5], clear=False)
    rec["hits"] = [ln for ln in rows if FENCE.match(ln.split("|")[1]) and not terminal(ln.split("|")[2].strip())]
    return dict(rec, clear=not rec["hits"])


def fstat_record(st):
    return dict((k, getattr(st, k)) for k in FD_KEYS)


def _read_all(fd):
    chunks = []
    while True:
        b = os.read(fd, 1 << 22)
        if not b:
            return b"".join(chunks)
        chunks.append(b)


def _write_all(fd, data):
    view = memoryview(data)
    while view:
        view = view[os.write(fd, view):]


def deploy_pin(deploy):
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
           "HOME": os.environ.get("HOME", "/")}
    try:
        p = subprocess.run([GIT, "-c", "core.fsmonitor=false", "-C", deploy, "rev-parse", "HEAD"], env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except OSError as exc:
        raise Stop(2, "git could not run: %s" % exc)
    if p.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", p.stdout.strip()):
        raise Stop(2, "the deploy %s is not a git checkout (%s)" % (deploy, p.stderr.strip()[:200]))
    return p.stdout.strip()


def open_stage(cfg):
    """The stage's descriptor, opened O_DIRECTORY|O_NOFOLLOW, physically at the literal declared path."""
    try:
        sfd = os.open(cfg.stage, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise Stop(2, "the stage %s cannot be opened as a real directory (%s)" % (cfg.stage, exc))
    if not stat.S_ISDIR(os.fstat(sfd).st_mode) or fd_path(sfd) != cfg.stage:
        raise Stop(2, "the stage descriptor is at %s, not the literal %s" % (fd_path(sfd), cfg.stage))
    return sfd


def smoke_binding(cfg, sfd, pin):
    """smoke-receipt.json, read through the stage's descriptor: a plain file of its own, naming this stage, this
    deploy's pin, a production smoke and an INDEX sha256."""
    try:
        fd = os.open("smoke-receipt.json", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=sfd)
    except OSError as exc:
        raise Stop(2, "the stage lacks the smoke's receipt (smoke-receipt.json): %s" % exc)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise Stop(2, "the smoke's receipt is not a plain file of its own")
        try:
            rec = json.loads(_read_all(fd).decode())
        except ValueError as exc:
            raise Stop(2, "the smoke's receipt is not JSON (%s)" % exc)
    finally:
        os.close(fd)
    if not isinstance(rec, dict):
        raise Stop(2, "the smoke's receipt is not a JSON object")
    why = []
    if rec.get("stage") != cfg.stage:
        why.append("its stage %r is not %s" % (rec.get("stage"), cfg.stage))
    if rec.get("pin") != pin:
        why.append("its pin %r is not the deploy's %s" % (rec.get("pin"), pin))
    if rec.get("local_test") is not False:
        why.append("it is not a production smoke's")
    if not (isinstance(rec.get("index_sha256"), str) and SHA_HEX.fullmatch(rec["index_sha256"])):
        why.append("it records no INDEX sha256")
    if why:
        raise Stop(2, "the smoke's receipt does not bind this copy: " + "; ".join(why))
    return {"stage": rec["stage"], "pin": rec["pin"], "index_sha256": rec["index_sha256"],
            "setup_env_sha256": rec.get("setup_env_sha256")}


def read_source(src, noatime):
    """(bytes, record) of one source: path lstat, descriptor fstat before and after the read, path lstat after."""
    try:
        p0 = os.lstat(src)
    except FileNotFoundError:
        raise Stop(5, "no source %s" % src)
    except OSError as exc:
        raise Stop(6, "lstat of %s failed: %s" % (src, exc))
    if not stat.S_ISREG(p0.st_mode):
        raise Stop(5, "the source %s is not a regular file (a symlink is refused)" % src)
    try:
        fd = os.open(src, os.O_RDONLY | os.O_NOFOLLOW | noatime)
    except PermissionError as exc:
        if noatime:
            raise Stop(3, "an O_NOATIME open of %s was refused (%s)" % (src, exc))
        raise Stop(6, "open of %s failed: %s" % (src, exc))
    except OSError as exc:
        raise Stop(5 if exc.errno == errno.ELOOP else 6, "open of %s failed: %s" % (src, exc))
    try:
        f0 = fstat_record(os.fstat(fd))
        data = _read_all(fd)
        f1 = fstat_record(os.fstat(fd))
    except OSError as exc:
        raise Stop(6, "read of %s failed: %s" % (src, exc))
    finally:
        os.close(fd)
    try:
        p1 = os.lstat(src)
    except OSError as exc:
        raise Stop(8, "the source %s vanished during its read (%s)" % (src, exc))
    moved = [k for k in FD_KEYS if f0[k] != f1[k]]
    if len(data) != f0["st_size"]:
        moved.append("length")
    for tag, p in (("path before", p0), ("path after", p1)):
        if (p.st_ino, p.st_dev) != (f0["st_ino"], f0["st_dev"]):
            moved.append(tag + " is another file")
    rec = {"source": src, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "source_fstat_before": f0,
           "source_fstat_after": f1, "source_inode": [f0["st_dev"], f0["st_ino"]],
           "source_path_inodes": [[p0.st_dev, p0.st_ino], [p1.st_dev, p1.st_ino]], "moved": moved}
    return data, rec


def manifest(cfg, deploy, pin, noatime, f, recs, created, binding, stop=None):
    m = {"schema": SCHEMA, "host": os.uname()[1], "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "stage": cfg.stage, "a0_dir": cfg.a0_dir, "deploy": deploy, "deploy_pin": pin, "smoke": binding,
         "o_noatime": bool(noatime), "fence": f, "files": recs, "created": created}
    if stop:
        m["stop"] = stop
    return m


def copy(cfg, deploy, out=None):
    """The copy; returns the exit status. The manifest goes to out (stdout) after any write."""
    out = out or sys.stdout
    noatime = getattr(os, "O_NOATIME", 0)
    created = []
    try:
        if cfg.require_noatime and not noatime:
            raise Stop(3, "this platform has no O_NOATIME")
        if not (os.path.isabs(deploy) and deploy.startswith(cfg.deploy_prefix) and ".." not in deploy.split("/")):
            raise Stop(2, "the deploy %r is not an absolute path under %s" % (deploy, cfg.deploy_prefix))
        f = fence_read(cfg.sacct)
        if not f["clear"]:
            raise Stop(9, f.get("error") or "fenced jobs are in a non-terminal state: %s" % f["hits"])
        pin = deploy_pin(deploy)
        sfd = open_stage(cfg)
        binding = smoke_binding(cfg, sfd, pin)
        for x in ("a0-refs", SIGMA_NAME):
            try:
                os.stat(x, dir_fd=sfd, follow_symlinks=False)
                raise Stop(2, "the stage already holds %s" % x)
            except FileNotFoundError:
                pass
        sources = [(n, os.path.join(cfg.a0_dir, n), "a0-refs/" + n) for n in sorted(cfg.pins) if n != SIGMA_NAME]
        sources.append((SIGMA_NAME, os.path.join(deploy, SIGMA_REL), SIGMA_NAME))
        got = []
        for name, src, rel in sources:  # every source read and checked before anything is written
            data, rec = read_source(src, noatime)
            rec.update(name=name, copy=cfg.stage + "/" + rel, pin=cfg.pins[name])
            if rec["sha256"] != cfg.pins[name]:
                raise Stop(4, "%s is not at its pin (%s, not %s)" % (src, rec["sha256"], cfg.pins[name]))
            got.append((rec, data, rel))
        moved = ["%s: %s" % (r["name"], r["moved"]) for r, _, _ in got if r["moved"]]
        if moved:
            raise Stop(8, "a source moved during its read: %s" % moved)
    except Stop as s:
        sys.stderr.write("refusing: %s\n" % s.why)
        return s.rc
    recs = [r for r, _, _ in got]
    bad = []
    try:
        os.mkdir("a0-refs", 0o755, dir_fd=sfd)
        created.append(cfg.stage + "/a0-refs/")
        afd = os.open("a0-refs", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=sfd)
        if fd_path(afd) != cfg.stage + "/a0-refs":
            raise Stop(6, "a0-refs is at %s, not %s/a0-refs" % (fd_path(afd), cfg.stage))
        for rec, data, rel in got:
            parent = afd if rel.startswith("a0-refs/") else sfd
            fd = os.open(os.path.basename(rel), os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=parent)
            created.append(rec["copy"])
            try:
                _write_all(fd, data)
                os.fsync(fd)
                st = os.fstat(fd)
                os.lseek(fd, 0, os.SEEK_SET)
                back = _read_all(fd)
                where = fd_path(fd)
            finally:
                os.close(fd)
            rec.update(copy_inode=[st.st_dev, st.st_ino], copy_nlink=st.st_nlink, copy_mode=st.st_mode,
                       copy_sha256=hashlib.sha256(back).hexdigest(), copy_fd_path=where)
            problems = []
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                problems.append("not a plain file of its own")
            if rec["copy_inode"] == rec["source_inode"]:
                problems.append("the source's inode")
            if where != rec["copy"]:
                problems.append("its descriptor is at %s, not the literal %s" % (where, rec["copy"]))
            if rec["copy_sha256"] != cfg.pins[rec["name"]]:
                problems.append("not at its pin when read back")
            rec["problems"] = problems
            if problems:
                bad.append(rec["name"])
    except (OSError, Stop) as exc:
        why = exc.why if isinstance(exc, Stop) else "%s (errno %s)" % (exc, exc.errno)
        m = manifest(cfg, deploy, pin, noatime, f, recs, created, binding, stop="I/O: " + why)
        out.write(json.dumps(m, indent=1, sort_keys=True) + "\n")
        out.flush()
        sys.stderr.write("STOP: a write-side failure (%s); the %d created paths stay in place\n" % (why, len(created)))
        return 6
    m = manifest(cfg, deploy, pin, noatime, f, recs, created, binding)
    m["fence_after"] = fence_read(cfg.sacct)
    out.write(json.dumps(m, indent=1, sort_keys=True) + "\n")
    out.flush()
    if bad:
        sys.stderr.write("STOP: the copies of %s failed their check (left in place)\n" % bad)
        return 6
    if not m["fence_after"]["clear"]:
        sys.stderr.write("STOP: the fence read after the copies is not clear\n")
        return 9
    return 0


def _int_record(r, keys):
    return isinstance(r, dict) and all(isinstance(r.get(k), int) and not isinstance(r.get(k), bool) for k in keys)


def _fence_ok(f):
    if not (isinstance(f, dict) and f.get("clear") is True and f.get("hits") == [] and isinstance(f.get("rows"), list)
            and isinstance(f.get("command"), str) and f["command"].startswith(SACCT_DECLARED + " ")):
        return False
    return all(isinstance(r, str) and len(r.split("|")) == 3 and all(x.strip() for x in r.split("|")) and
               not (FENCE.match(r.split("|")[1]) and not terminal(r.split("|")[2].strip())) for r in f["rows"])


def verify_problems(man):
    """Every defect of a production manifest (an empty list if none)."""
    cfg = production_config()
    p = []
    if not isinstance(man, dict):
        return ["the manifest is not a JSON object"]
    if man.get("schema") != SCHEMA:
        p.append("schema %r" % man.get("schema"))
    if man.get("stage") != STAGE_DECLARED or man.get("a0_dir") != A0_DIR_DECLARED:
        p.append("the stage or the A0 source directory is not the declared one")
    deploy = man.get("deploy")
    if not (isinstance(deploy, str) and deploy.startswith(DEPLOY_PREFIX) and ".." not in deploy.split("/")):
        p.append("the deploy %r is not under %s" % (deploy, DEPLOY_PREFIX))
        deploy = None
    pin = man.get("deploy_pin")
    smoke = man.get("smoke")
    if not (isinstance(pin, str) and re.fullmatch(r"[0-9a-f]{40}", pin)) or not isinstance(smoke, dict) \
            or smoke.get("pin") != pin or smoke.get("stage") != STAGE_DECLARED \
            or not (isinstance(smoke.get("index_sha256"), str) and SHA_HEX.fullmatch(smoke["index_sha256"])):
        p.append("the smoke binding (stage, deploy pin, INDEX sha256) is missing or does not match")
    if man.get("o_noatime") is not True:
        p.append("no O_NOATIME")
    if man.get("stop"):
        p.append("the copy stopped: %s" % man["stop"])
    for key in ("fence", "fence_after"):
        if not _fence_ok(man.get(key)):
            p.append("the %s read is missing, not clear, or has a row that is not clear" % key)
    files = man.get("files")
    if not isinstance(files, list) or len(files) != len(cfg.pins) \
            or sorted(r.get("name") for r in files if isinstance(r, dict)) != sorted(cfg.pins):
        p.append("the copies are not exactly the 22 declared names")
        files = [r for r in files if isinstance(r, dict)] if isinstance(files, list) else []
    for r in files:
        name = r.get("name")
        if name not in cfg.pins:
            continue
        want_src = os.path.join(A0_DIR_DECLARED, name) if name != SIGMA_NAME else (
            os.path.join(deploy, SIGMA_REL) if deploy else None)
        want_copy = STAGE_DECLARED + ("/a0-refs/" + name if name != SIGMA_NAME else "/" + SIGMA_NAME)
        why = []
        if r.get("source") != want_src or r.get("copy") != want_copy or r.get("copy_fd_path") != want_copy:
            why.append("its source or copy path is not the declared one")
        if r.get("pin") != cfg.pins[name] or r.get("sha256") != cfg.pins[name] or r.get("copy_sha256") != cfg.pins[name]:
            why.append("not at its pin")
        if not (_int_record(r.get("source_fstat_before"), FD_KEYS) and r.get("source_fstat_before") == r.get("source_fstat_after")):
            why.append("its source descriptor's stat records are missing or moved")
        si, ci = r.get("source_inode"), r.get("copy_inode")
        if not (isinstance(si, list) and isinstance(ci, list) and len(si) == len(ci) == 2
                and all(isinstance(x, int) for x in si + ci) and si != ci):
            why.append("the source and copy inodes are missing or not distinct")
        spi = r.get("source_path_inodes")
        if not (isinstance(spi, list) and spi == [si, si]):
            why.append("the source's path did not identify its descriptor")
        if r.get("copy_nlink") != 1 or r.get("moved") != [] or r.get("problems") != []:
            why.append("not a plain copy of its own, or its source moved")
        if why:
            p.append("%s: %s" % (name, "; ".join(why)))
    return p


def verify(path):
    try:
        with open(path) as fh:
            man = json.load(fh)
    except (OSError, ValueError) as exc:
        sys.stderr.write("refusing: the manifest is unreadable (%s)\n" % exc)
        return 2
    problems = verify_problems(man)
    for x in problems:
        sys.stderr.write("refusing: %s\n" % x)
    if not problems:
        print(json.dumps({"verified": len(man["files"]), "host": man.get("host"), "utc": man.get("utc")}))
    return 2 if problems else 0


def main(argv):
    switches = sorted(k for k in os.environ if k.startswith("PFB_COPY_"))
    if switches:
        sys.stderr.write("refusing: test switches are set in a production run: %s\n" % switches)
        return 2
    if argv[:1] == ["verify"] and len(argv) == 2:
        return verify(argv[1])
    if len(argv) != 1:
        sys.stderr.write("usage: pfb_copy_remote.py <deploy>  |  pfb_copy_remote.py verify <manifest>\n")
        return 2
    return copy(production_config(), argv[0])


if __name__ == "__main__":
    sys.exit(main([a for a in sys.argv[1:] if a != "-"]))
