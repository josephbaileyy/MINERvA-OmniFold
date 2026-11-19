#!/usr/bin/env python3
"""PILOT-FB's copy connect (PILOT-FB-BINDING-1 addendum C1, ruling 3 step 3): RS1's 21 A0 products and the sigma
receipt, read O_NOATIME and copied into the stage the login-node smoke created, as plain files of their own. Python
3.6-compatible: on a login node it runs under /usr/bin/python3, fed through ssh's stdin, with the deploy as its only
argument. It writes nothing but the stage's a0-refs/ (21 files) and assess_receipt.json, and nothing on CFS; it runs no
job and calls no sbatch.

    copy (on loginNN):     /usr/bin/python3 - <deploy> < pfb_copy_remote.py > copy-manifest.json
    verify (on the laptop): python3 pfb_copy_remote.py verify <copy-manifest.json>

copy refuses, before it writes anything:
  - exit 3 if the platform has no O_NOATIME;
  - exit 9 if sacct fails, prints a malformed row, or shows a job of a fenced family in a non-terminal state (a
    14-day read, each State classified; sacct only, never squeue);
  - exit 2 if the stage is not the declared one (an existing real directory at its own physical path), lacks the
    smoke's receipt (smoke-receipt.json, a plain file of its own), or already holds a0-refs/ or assess_receipt.json;
    or if the deploy is not an absolute /pscratch path;
  - exit 5 if a source is missing, a symlink, or not a regular file (sources are opened O_NOFOLLOW);
  - exit 4 if a source's sha256 is not its pin (RS1's runs-SHA256SUMS, and rounding_mechanism_analyze's sigma pin);
  - exit 8 if any source's stat (size, mtime_ns, atime_ns, ino, dev) moved during its read.
Then it creates a0-refs/ and each copy O_CREAT | O_EXCL | O_NOFOLLOW, and checks each copy: a plain file with one link,
an inode that is not its source's, physically at its own path inside the stage, and its sha256 at the pin (exit 6
otherwise, a STOP: the copies stay for the director). The fence is read again at the end (exit 9 if not clear). The
manifest on stdout records every source and copy, both stats, both inodes and both fence reads.
verify (exit 2 on any defect) checks the manifest: the declared stage, exactly the 22 names at their pins, O_NOATIME,
no moved stat, copies with new inodes and one link, and both fence reads clear.

MEASURES: nothing; it copies. CANNOT AUTHORIZE: the job, which needs the director's own go.
"""
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import time

TEST = os.environ.get("PFB_COPY_TEST_ROOT")  # tests only: substitute roots and pins; the laptop verify refuses them
STAGE_DECLARED = "/pscratch/sd/j/josephrb/pfb-20261117-stage"
A0_DIR_DECLARED = "/pscratch/sd/j/josephrb/rs1-a1-20261107/runs/A0"
STAGE = os.path.join(TEST, "stage") if TEST else STAGE_DECLARED
A0_DIR = os.path.join(TEST, "rs1", "runs", "A0") if TEST else A0_DIR_DECLARED
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
STAT_KEYS = ("st_size", "st_mtime_ns", "st_atime_ns", "st_ino", "st_dev")
USER = "josephrb"
SCHEMA = "pfb-copy/1"


def refuse(rc, why):
    sys.stderr.write("refusing: %s\n" % why)
    sys.exit(rc)


def pins():
    """{name: sha256} of the 22 copies (21 A0 products and the sigma receipt); a test substitutes its own."""
    if TEST:
        with open(os.path.join(TEST, "pins.json")) as fh:
            return json.load(fh)
    out = dict(A0_PINS)
    out[SIGMA_NAME] = SIGMA_SHA256
    return out


def terminal(state):
    return state in TERMINAL or bool(CANCELLED_BY.fullmatch(state))


def fence_read():
    cmd = ["sacct", "-X", "-n", "-P", "-u", USER, "-S", "now-14days", "-o", "JobID,JobName,State"]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except OSError as exc:
        return {"command": " ".join(cmd), "error": "sacct could not run: %s" % exc, "clear": False}
    if p.returncode != 0:
        return {"command": " ".join(cmd), "error": "sacct failed (rc %d): %s" % (p.returncode, p.stderr.strip()[:200]),
                "clear": False}
    rows = [ln for ln in p.stdout.splitlines() if ln.strip()]
    bad = [ln for ln in rows if len(ln.split("|")) != 3 or not ln.split("|")[0].strip()]
    if bad:
        return {"command": " ".join(cmd), "rows": rows, "error": "malformed sacct rows: %s" % bad[:5], "clear": False}
    hits = [ln for ln in rows if FENCE.match(ln.split("|")[1]) and not terminal(ln.split("|")[2].strip())]
    return {"command": " ".join(cmd), "rows": rows, "hits": hits, "clear": not hits}


def stat_record(st):
    return dict((k, getattr(st, k)) for k in STAT_KEYS)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def stage_problem(stage):
    """The stage the smoke created: an existing real directory at its own physical path, holding the smoke's receipt
    as a plain file of its own, and no copies yet."""
    if os.path.islink(stage) or not os.path.isdir(stage):
        return "the stage %s is not an existing directory" % stage
    if os.path.realpath(stage) != stage:
        return "the stage %s resolves to %s" % (stage, os.path.realpath(stage))
    receipt = os.path.join(stage, "smoke-receipt.json")
    try:
        st = os.lstat(receipt)
    except OSError:
        return "the stage lacks the smoke's receipt (smoke-receipt.json): the smoke has not run"
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        return "the smoke's receipt is not a plain file of its own"
    for x in ("a0-refs", SIGMA_NAME):
        if os.path.lexists(os.path.join(stage, x)):
            return "the stage already holds %s" % x
    return None


def read_source(path, noatime):
    """(bytes, stat before, stat after, fstat) of one source, opened O_RDONLY | O_NOFOLLOW (| O_NOATIME)."""
    st0 = os.lstat(path)
    if not stat.S_ISREG(st0.st_mode):
        refuse(5, "the source %s is not a regular file (a symlink is refused)" % path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | (noatime or 0))
    with os.fdopen(fd, "rb") as fh:
        fst = os.fstat(fh.fileno())
        data = fh.read()
    st1 = os.lstat(path)
    return data, stat_record(st0), stat_record(st1), fst


def copy(deploy):
    noatime = getattr(os, "O_NOATIME", None)
    if noatime is None and not TEST:
        refuse(3, "this platform has no O_NOATIME")
    if not (os.path.isabs(deploy) and (TEST or deploy.startswith("/pscratch/"))):
        refuse(2, "the deploy %r is not an absolute /pscratch path" % deploy)
    f = fence_read()
    if not f["clear"]:
        refuse(9, f.get("error") or "fenced jobs are in a non-terminal state: %s" % f["hits"])
    why = stage_problem(STAGE)
    if why:
        refuse(2, why)
    want = pins()
    sources = [(n, os.path.join(A0_DIR, n), os.path.join("a0-refs", n)) for n in sorted(want) if n != SIGMA_NAME]
    sources.append((SIGMA_NAME, os.path.join(deploy, SIGMA_REL), SIGMA_NAME))
    got = []
    for name, src, rel in sources:  # every source read and checked before anything is written
        if not os.path.lexists(src):
            refuse(5, "no source %s" % src)
        data, st0, st1, fst = read_source(src, noatime)
        rec = {"name": name, "source": src, "copy": os.path.join(STAGE, rel), "bytes": len(data),
               "sha256": sha256_bytes(data), "source_stat_before": st0, "source_stat_after": st1,
               "source_inode": [fst.st_dev, fst.st_ino]}
        rec["moved"] = [k for k in STAT_KEYS if st0[k] != st1[k]] + (["length"] if len(data) != st0["st_size"] else [])
        if rec["sha256"] != want[name]:
            refuse(4, "%s is not at its pin (%s, not %s)" % (src, rec["sha256"], want[name]))
        got.append((rec, data))
    moved = [r["name"] for r, _ in got if r["moved"]]
    if moved:
        refuse(8, "the stat of %s moved during its read" % moved)
    os.mkdir(os.path.join(STAGE, "a0-refs"), 0o755)
    bad = []
    for rec, data in got:
        dst = rec["copy"]
        fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        st = os.lstat(dst)
        rec["copy_inode"] = [st.st_dev, st.st_ino]
        rec["copy_nlink"] = st.st_nlink
        with open(dst, "rb") as fh:
            rec["copy_sha256"] = sha256_bytes(fh.read())
        lexical = os.path.join(os.path.realpath(STAGE), os.path.relpath(dst, STAGE))
        problems = []
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            problems.append("not a plain file of its own")
        if rec["copy_inode"] == rec["source_inode"]:
            problems.append("the source's inode")
        if os.path.realpath(dst) != lexical:
            problems.append("not physically at its own path in the stage")
        if rec["copy_sha256"] != want[rec["name"]]:
            problems.append("not at its pin after the copy")
        rec["problems"] = problems
        if problems:
            bad.append(rec["name"])
    man = {"schema": SCHEMA, "host": os.uname()[1], "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "stage": STAGE, "a0_dir": A0_DIR, "deploy": deploy, "o_noatime": noatime is not None, "fence": f,
           "files": [r for r, _ in got], "fence_after": fence_read()}
    sys.stdout.write(json.dumps(man, indent=1, sort_keys=True) + "\n")
    sys.stdout.flush()
    if bad:
        sys.stderr.write("STOP: the copies of %s failed their check (left in place for the director)\n" % bad)
        return 6
    if not man["fence_after"]["clear"]:
        sys.stderr.write("STOP: the fence read after the copies is not clear\n")
        return 9
    return 0


def verify(path):
    with open(path) as fh:
        man = json.load(fh)
    want = dict(A0_PINS)
    want[SIGMA_NAME] = SIGMA_SHA256
    problems = []
    if man.get("schema") != SCHEMA:
        problems.append("schema %r" % man.get("schema"))
    if man.get("stage") != STAGE_DECLARED or man.get("a0_dir") != A0_DIR_DECLARED:
        problems.append("the stage or the A0 source directory is not the declared one")
    if not man.get("o_noatime"):
        problems.append("no O_NOATIME")
    if not man.get("fence", {}).get("clear") or not man.get("fence_after", {}).get("clear"):
        problems.append("a fence read was not clear")
    files = {r.get("name"): r for r in man.get("files", [])}
    if set(files) != set(want) or len(man.get("files", [])) != len(want):
        problems.append("the copies are not exactly the 22 declared names")
    for name, r in sorted(files.items()):
        if name not in want:
            continue
        if r.get("sha256") != want[name] or r.get("copy_sha256") != want[name]:
            problems.append("%s: not at its pin" % name)
        if r.get("moved") or r.get("source_stat_before") != r.get("source_stat_after"):
            problems.append("%s: its source's stat moved" % name)
        if r.get("copy_inode") == r.get("source_inode") or r.get("copy_nlink") != 1 or r.get("problems"):
            problems.append("%s: the copy is not a plain file of its own with a new inode" % name)
    for p in problems:
        sys.stderr.write("refusing: %s\n" % p)
    if not problems:
        print(json.dumps({"verified": len(files), "host": man.get("host"), "utc": man.get("utc")}))
    return 2 if problems else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["verify"] and len(sys.argv) == 3:
        sys.exit(verify(sys.argv[2]))
    args = [a for a in sys.argv[1:] if a != "-"]
    if len(args) != 1:
        refuse(2, "usage: python3 - <deploy> < pfb_copy_remote.py  |  pfb_copy_remote.py verify <manifest>")
    sys.exit(copy(args[0]))
