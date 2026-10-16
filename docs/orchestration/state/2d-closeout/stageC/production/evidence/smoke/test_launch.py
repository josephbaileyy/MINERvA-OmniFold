#!/usr/bin/env python3
"""Offline tests of the packed submission path (DESIGN §14) with a mocked Slurm ledger and stubbed Slurm commands
(no real sacct, squeue, sbatch, scancel, scontrol or srun is called).

  python test_launch.py      (from anywhere; prints one line per case, then "RAN n, FAILED k"; exits 1 on any failure)

Cases (AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md §4):
  - compose(): chunking per class in the frozen order, held partial chunks, the class tail, started rows left out;
  - the enforced worst case of the whole table, packed;
  - node fit: member count, summed memory <= RealMemory 515100 MB (fires on a table that breaks it, silent on ours),
    duplicates, mixed classes, a cap that is not the members' cap;
  - member-level attempts: derived states of a TIMEOUT pack; retry fires only for a TIMEOUT member; a member with
    validated output is never re-run; DEADLINE / never-started CANCELLED packs owe their members, a started one does
    not; a pack job with no member record fails closed; redo owes only deadline-cancelled retries;
  - the gate's stop rule; --no-requeue, --deadline, --qos=regular, --exclusive and the summed --mem on every sbatch;
  - migrate: lists only never-started PENDING shared-QOS rows, cancels with --state=PENDING, refuses a stale --only;
  - sbatch_pack.sh (stubbed scontrol/srun/sacct): a good pack runs every member as `srun --exact -n1 -c -mem` with
    its explicit name and records each rc; it refuses before any step on a duplicated or unknown member, a mixed
    class, arguments that differ from the launcher's record, and billing 64 (accepts 256), QOS shared (accepts regular_1 and regular); one failing member does
    not stop the others; MEMBER_SHA equals sha256(sbatch_prod.sh);
  - sbatch_prod.sh refuses without --member, outside an srun step, at billing 64, and on a CPU mismatch.
"""
import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[1]
spec = importlib.util.spec_from_file_location("launch", PKG / "launch.py")
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
TABLE = L.table()
REAL_TABLE = L.table
REAL_RUN = subprocess.run   # L.subprocess IS this module: patches below are undone before the shell tests
REAL_LEDGER, REAL_QUEUED, REAL_PRE = L.ledger, L.queued, L.preconditions
FAILS, RAN = [], [0]


def case(name, ok):
    RAN[0] += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        FAILS.append(name)


def refused(fn, *a, want=""):
    try:
        fn(*a)
    except SystemExit as e:
        return want in str(e)
    return False


def R(jid, name, st, el=0, start="Unknown", end="Unknown", amount=0.0, tl="00:51:00"):
    kind = "in-flight at cap" if st in L.IN_FLIGHT else "charged"
    return L.Row(jid, name, st, el, kind, amount, start, end, tl)


def setup(rows, queue=(), done=0.0, fly=0.0, packs=None):
    """rows: ledger Rows; queue: (jid, name) pairs in squeue; packs: {jid: [members]} member records."""
    tmp = tempfile.mkdtemp()
    L.NS = tmp
    for d in ("out", "retries", "results", "logs", "tmp", "gatelog", "packs"):
        Path(tmp, d).mkdir()
    for jid, ms in (packs or {}).items():
        Path(tmp, "packs", f"{jid}.members").write_text(f"x\t00:51:00\t{','.join(ms)}\n")
    L.ledger = lambda: (done, fly, rows)

    def q():
        out = set()
        for jid, name in queue:
            out.update(L.members_of(jid) if L.is_pack(name) else {name})
        return out
    L.queued = q
    return tmp


def out(tmp, name):
    Path(tmp, "out", name).mkdir(exist_ok=True)
    Path(tmp, "out", name, "xsec.root").write_text("x")


def status(tmp, jid, lines, launched=True):
    head = f"#pack\tx\tx\t0\n" if launched else ""
    Path(tmp, "packs", f"{jid}.status").write_text(head + "".join(f"{m}\t{rc}\t{t}\n" for m, rc, t in lines))


def rows_of(batch):
    return [r for r in TABLE if r["batch"] == batch]


def done_rows(batches):
    """Ledger rows saying every row of these batches COMPLETED on the shared QOS."""
    return [R(str(100000 + i), r["name"], "COMPLETED", 900, "2026-10-15T10:00:00", "2026-10-15T10:15:00")
            for i, r in enumerate(r for r in TABLE if r["batch"] in batches)]


S1a, S1b = rows_of("S1a"), rows_of("S1b")
n1, n2, n3, n4 = (r["name"] for r in S1a[:4])
m4l = [n1, n2, n3, n4]
PRE = ["G0", "G1"]

# ---- compose() ------------------------------------------------------------------------------------------------------
setup(done_rows(PRE))
pk = L.compose("G2", L.ledger()[2], L.queued())
sizes = sorted(len(m) for m, _ in pk)
case("compose G2: 17 S4U pairs + 1 S4U single (class tail) + 1 pack of the 4 S4CV rows",
     sizes == [1] + [2] * 17 + [4] and {t for _, t in pk} == {"00:30:00", "00:51:00"})
case("compose G2: enforced 17 x 0.5 + 0.5 + 0.85 = 9.85", abs(sum(L.pack_enforced(t) for _, t in pk) - 9.85) < 1e-9)
setup(done_rows(PRE + ["G2"]))
pk = L.compose("S1a", L.ledger()[2], L.queued())
held = {r["name"] for r in S1a} - {r["name"] for m, _ in pk for r in m}
case("compose S1a: 12 full CV packs; the 2 rows of the partial chunk are held", len(pk) == 12 and all(
    len(m) == 4 for m, _ in pk) and held == {S1a[48]["name"], S1a[49]["name"]})
setup(done_rows(PRE + ["G2"]) + [R(str(300 + i), r["name"], "PENDING") for i, r in enumerate(S1a[:48])])
pk = L.compose("S1b", L.ledger()[2], L.queued())
case("compose S1b: 13 packs, the first carrying S1a's 2 held rows", len(pk) == 13 and [r["name"] for r in pk[0][0]][:2]
     == [S1a[48]["name"], S1a[49]["name"]])
late = [b for b in L.ORDER if b not in ("S4b",)]
rows = done_rows(late) + [R(str(200000 + i), r["name"], "COMPLETED", 900, "2026-10-15T10:00:00", "x")
                          for i, r in enumerate(rows_of("S4b")[:38])]
setup(rows)
pk = L.compose("S4b", L.ledger()[2], L.queued())
case("compose S4b (the CV class's last batch): the 2-row tail goes as a partial pack",
     len(pk) == 1 and len(pk[0][0]) == 2)
setup(done_rows(PRE + ["G2"]) + [R("7", n2, "RUNNING", 60, "2026-10-16T10:00:00")])
pk = L.compose("S1a", L.ledger()[2], L.queued())
names = [r["name"] for m, _ in pk for r in m]
case("compose: a shared job that started is left out of the packs", n2 not in names and len(names) == 48)
setup(done_rows(PRE + ["G2"]) + [R("8", n2, "CANCELLED", 0, "None"), R("9", n3, "CANCELLED", 40, "2026-10-16T10:00:00")])
names = [r["name"] for m, _ in L.compose("S1a", L.ledger()[2], L.queued()) for r in m]
case("compose: a never-started CANCELLED shared row is owed; a CANCELLED row that started is an attempt",
     n2 in names and n3 not in names)
setup(done_rows(PRE + ["G2"]), queue=[("31", "2dc_P_S1_005")])
names = [r["name"] for m, _ in L.compose("S1a", L.ledger()[2], L.queued()) for r in m]
case("compose: a row in the queue is never packed", "2dc_P_S1_005" not in names)

# ---- the worst case of the whole table, packed ------------------------------------------------------------------------
# G0 and G1 ran on the shared QOS at their row caps; every later row goes in packs, nothing run.
setup(done_rows(PRE))
allp = []
for b in L.ORDER[2:]:
    inflight = [R(str(9000 + i), m["name"], "PENDING") for i, m in enumerate(r for ms, _ in allp for r in ms)]
    allp += L.compose(b, done_rows(PRE) + inflight, set())
packed = sum(L.pack_enforced(t) for _, t in allp) + sum(L.enforced(r) for r in TABLE if r["batch"] in PRE)
rows_cap = sum(L.enforced(r) for r in TABLE)
case(f"worst case packed (G0, G1 shared; the rest packed) = row caps 117.8583 + 0.25 (S4U single): {packed:.4f}",
     abs(rows_cap - 117.8583) < 1e-3 and abs(packed - (rows_cap + 0.25)) < 1e-9 and
     sum(len(m) for m, _ in allp) == len(TABLE) - 12 and len(allp) == 19 + 120)

# ---- node fit -----------------------------------------------------------------------------------------------------------
cv4 = S1a[:4]
case("fit: 4 CV rows accepted", not refused(L.fit, cv4))
case("fit: 5 CV rows refused (count)", refused(L.fit, S1a[:5], want="exceed one"))
u = [r for r in TABLE if r["name"].startswith("2dc_P_S4U_")]
case("fit: 2 S4U rows accepted, 3 refused", not refused(L.fit, u[:2]) and refused(L.fit, u[:3], want="exceed one"))
case("fit: a duplicated member refused", refused(L.fit, [S1a[0], S1a[0]], want="repeats"))
case("fit: mixed classes refused", refused(L.fit, [S1a[0], u[0]], want="differ"))
case("fit: every class of jobs.tsv fits a node at full packing",
     all(L.per_node(r) * L.mem_mb(r["mem"]) <= L.NODE_MEM_MB and L.per_node(r) * int(r["cpus"]) <= L.NODE_CPUS
         for r in TABLE))
fake = [dict(S1a[i], name=f"2dc_P_S1_9{i:02d}", mem="180000M") for i in range(3)]
L.table = lambda: TABLE + fake
case("fit: summed memory 3 x 180000M > 515100M refused (the memory clause)",
     refused(L.fit, fake, want="summed member memory"))
case("fit: summed memory 2 x 180000M accepted", not refused(L.fit, fake[:2]))
L.table = REAL_TABLE
case("check_pack: a cap other than the members' cap refused", refused(L.check_pack, cv4, "01:00:00", want="common cap"))

# ---- member-level attempts -------------------------------------------------------------------------------------------
END = "2026-10-17T10:00:00"
end_s = int(L.epoch(END))
tmp = setup([R("50", "2dc_P_K4_S1_001", "TIMEOUT", 3060, "2026-10-17T09:09:00", END)], packs={"50": [n1, n2, n3, n4]})
out(tmp, n1)
status(tmp, "50", [(n1, 0, end_s - 900), (n3, 1, end_s - 2000), (n4, 137, end_s - 20)])
st = L.member_states(L.ledger()[2][0])
case("TIMEOUT pack: validated member COMPLETED, unfinished TIMEOUT, early rc 1 FAILED, killed-at-limit TIMEOUT",
     st == {n1: "COMPLETED", n2: "TIMEOUT", n3: "FAILED", n4: "TIMEOUT"})
status(tmp, "50", [(n1, 0, end_s - 900), (n3, 1, end_s - 200), (n4, 1, end_s - 60)])
st = L.member_states(L.ledger()[2][0])
case("TIMEOUT margin is 120 s before Start + TimeLimit: rc 1 at -200 s FAILED, at -60 s TIMEOUT",
     st[n3] == "FAILED" and st[n4] == "TIMEOUT")
status(tmp, "50", [(n1, 0, end_s - 900), (n3, 1, end_s - 2000), (n4, 137, end_s - 20)])
calls = []


def fake_run(cmd, **k):
    calls.append(cmd)
    if cmd[0] == "sbatch":
        return type("R", (), {"returncode": 0, "stdout": "424242\n", "stderr": ""})()
    return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()


L.subprocess.run = fake_run
L.deadline_arg = lambda now=None: ["--deadline=2026-10-20T23:00:00"]
real_pre = L.preconditions
L.preconditions = lambda *a: None


def run(argv):
    sys.argv = ["launch.py"] + argv
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            code = L.main()
        except SystemExit as e:
            code = str(e)
    return code, buf.getvalue()


calls.clear()
code, o = run(["submit", "S1a", "--retry", n2, "--time", "01:16:00"])
sb = [c for c in calls if c[0] == "sbatch"]
case("retry fires for a TIMEOUT member", code == 0 and len(sb) == 1 and Path(tmp, "retries", f"{n2}.time").is_file())
case("retry sbatch line: --qos=regular --exclusive --no-requeue --deadline --time=01:16:00 --mem=121920M, member arg",
     sb and all(x in sb[0] for x in ("--qos=regular", "--exclusive", "--no-requeue", "--deadline=2026-10-20T23:00:00",
                                     "--time=01:16:00", "--mem=121920M")) and sb[0][-1] == n2)
Path(tmp, "retries", f"{n2}.time").unlink()
code, o = run(["submit", "S1a", "--retry", n1, "--time", "01:16:00"])
case("retry refused for a member with validated output", isinstance(code, str) and "COMPLETED" in code)
code, o = run(["submit", "S1a", "--retry", n3, "--time", "01:16:00"])
case("retry refused for a FAILED member", isinstance(code, str) and "FAILED" in code)
tmp = setup([R("51", "2dc_P_K4_S1_001", "OUT_OF_MEMORY", 900, "2026-10-17T09:09:00", END)], packs={"51": [n1, n2, n3, n4]})
status(tmp, "51", [])
code, o = run(["submit", "S1a", "--retry", n2, "--time", "01:16:00"])
case("retry refused for a member of an OUT_OF_MEMORY pack", isinstance(code, str) and "OUT_OF_MEMORY" in code)
for st_, el, start, owed in (("DEADLINE", 0, "Unknown", True), ("CANCELLED", 0, "None", True),
                             ("CANCELLED", 30, "2026-10-17T09:09:00", False)):
    tmp = setup(done_rows(PRE + ["G2"]) + [R("52", "2dc_P_K4_S1_001", st_, el, start, END)], packs={"52": [n1, n2, n3, n4]})
    if el:
        status(tmp, "52", [])
    names = {r["name"] for m, _ in L.compose("S1a", L.ledger()[2], L.queued()) for r in m}
    case(f"{st_} pack (elapsed {el}): its members {'are' if owed else 'are NOT'} owed", ({n1, n2, n3, n4} <= names) == owed)
setup([R("53", "2dc_P_K4_S1_001", "COMPLETED", 900, "2026-10-17T09:09:00", END)])
case("a pack job with no member record fails closed", refused(L.attempts, L.ledger()[2], want="no member record"))
setup([R("55", "2dc_P_K4_S1_001", "FAILED", 3, "2026-10-17T09:09:00", "2026-10-17T09:09:03")], packs={"55": m4l})
case("a pack that ran but never launched its members (dispatcher refusal) is a STOP, not member attempts",
     refused(L.attempts, L.ledger()[2], want="STOP: pack 55"))
tmp = setup([R("56", "2dc_P_K4_S1_001", "FAILED", 900, "2026-10-17T09:09:00", END)], packs={"56": m4l})
status(tmp, "56", [(n1, 1, end_s - 500), (n2, 0, end_s - 400)])
out(tmp, n2)
case("a launched pack that FAILED: rc 1 member FAILED, validated member COMPLETED, members without rc FAILED",
     L.member_states(L.ledger()[2][0]) == {n1: "FAILED", n2: "COMPLETED", n3: "FAILED", n4: "FAILED"})
tmp = setup(done_rows(PRE + ["G2"]) + [R("54", "2dc_P_K4_S1_001", "COMPLETED", 900, "2026-10-17T09:09:00", END)],
            packs={"54": [n1, n2, n3, n4]})
for m in (n1, n2, n3, n4):
    out(tmp, m)
status(tmp, "54", [(m, 0, end_s - 10) for m in (n1, n2, n3, n4)])
names = {r["name"] for m, _ in L.compose("S1a", L.ledger()[2], L.queued()) for r in m}
case("members with validated output are never re-packed", not ({n1, n2, n3, n4} & names))

# redo: deadline-cancelled retry packs only
tmp = setup([R("60", "2dc_P_K4_S1_001", "TIMEOUT", 3060, "2026-10-17T09:09:00", END),
             R("61", "2dc_P_K1_S1_002", "DEADLINE", 0, "Unknown", "Unknown")],
            packs={"60": [n1, n2, n3, n4], "61": [n2]})
status(tmp, "60", [])
Path(tmp, "retries", f"{n2}.time").write_text("01:16:00\n")
pk = L.owed_retries("S1a", L.ledger()[2], L.queued())
case("redo: a deadline-cancelled retry is owed at its recorded cap, alone",
     len(pk) == 1 and [r["name"] for r in pk[0][0]] == [n2] and pk[0][1] == "01:16:00")
tmp = setup([R("60", "2dc_P_K4_S1_001", "TIMEOUT", 3060, "2026-10-17T09:09:00", END),
             R("62", "2dc_P_K1_S1_002", "TIMEOUT", 4560, "2026-10-18T09:09:00", "2026-10-18T10:25:00")],
            packs={"60": [n1, n2, n3, n4], "62": [n2]})
status(tmp, "60", [])
status(tmp, "62", [], )
Path(tmp, "retries", f"{n2}.time").write_text("01:16:00\n")
case("redo: a retry that ran is never owed", not L.owed_retries("S1a", L.ledger()[2], L.queued()))

# ---- pack (smoke) and records ----------------------------------------------------------------------------------------
setup(done_rows(PRE), queue=[("70", n1)])
code, o = run(["pack", ",".join([n1, n2, n3, n4])])
case("pack: a member still PENDING on the shared QOS is refused", isinstance(code, str) and n1 in code)
tmp = setup(done_rows(PRE) + [R(str(80 + i), m, "CANCELLED", 0, "None") for i, m in enumerate((n1, n2, n3, n4))])
calls.clear()
code, o = run(["pack", ",".join([n1, n2, n3, n4])])
sb = [c for c in calls if c[0] == "sbatch"]
rec = Path(tmp, "packs", "2dc_P_K4_S1_001.members")
case("pack: 4 never-started cancelled rows -> one sbatch of 2dc_P_K4_S1_001 at 00:51:00, --mem=487680M",
     code == 0 and len(sb) == 1 and "--job-name=2dc_P_K4_S1_001" in sb[0] and "--time=00:51:00" in sb[0]
     and "--mem=487680M" in sb[0] and sb[0][-4:] == [n1, n2, n3, n4] and "--no-requeue" in sb[0])
case("pack: the pre-sbatch and job-id member records are written and equal",
     rec.is_file() and Path(tmp, "packs", "424242.members").read_text() == rec.read_text())


def fail_sbatch(cmd, **k):
    calls.append(cmd)
    return type("R", (), {"returncode": 1, "stdout": "", "stderr": "boom"})()


tmp = setup([R("60", "2dc_P_K4_S1_001", "TIMEOUT", 3060, "2026-10-17T09:09:00", END)], packs={"60": [n1, n2, n3, n4]})
status(tmp, "60", [])
L.subprocess.run = fail_sbatch
code, o = run(["submit", "S1a", "--retry", n2, "--time", "01:16:00"])
case("sbatch failure: the retry record is removed", "sbatch failed" in str(code) and not Path(tmp, "retries", f"{n2}.time").exists())
L.subprocess.run = fake_run

# ---- verifier round 1 (M1, M2, M3, m1, m3, m4, m10) -----------------------------------------------------------------
# M1: redo through main(): the recorded retry cap is the pack cap
tmp = setup([R("60", "2dc_P_K4_S1_001", "TIMEOUT", 3060, "2026-10-17T09:09:00", END),
             R("61", "2dc_P_K1_S1_002", "DEADLINE", 0, "Unknown", "Unknown")], packs={"60": m4l, "61": [n2]})
status(tmp, "60", [])
Path(tmp, "retries", f"{n2}.time").write_text("01:16:00\n")
calls.clear()
code, o = run(["redo", "S1a"])
sb = [c for c in calls if c[0] == "sbatch"]
case("redo via main: a deadline-cancelled retry goes as one pack at its recorded cap 01:16:00",
     code == 0 and len(sb) == 1 and "--time=01:16:00" in sb[0] and sb[0][-1] == n2)
REAL_OR = L.owed_retries
L.owed_retries = lambda b, rl, q: [(pk[0], "01:20:00") for pk in REAL_OR(b, rl, q)]
calls.clear()
code, o = run(["redo", "S1a"])
case("redo via main: a pack cap that differs from the member's retry record is refused",
     "differs from a member's retry record" in str(code) and not [c for c in calls if c[0] == "sbatch"])
L.owed_retries = REAL_OR
# M2: frozen order: earlier batches may lead only as a held remainder
setup(done_rows(PRE))
case("M2: submit S1a with G2's rows owed is refused (frozen order)",
     refused(L.compose, "S1a", L.ledger()[2], L.queued(), want="submit G2 before S1a"))
setup(done_rows(PRE + ["G2"]) + [R("70", "2dc_P_K4_S1_001", "DEADLINE", 0)], packs={"70": m4l})
case("M2: a never-started S1a pack's 4 members are owed to S1a, not folded into S1b",
     refused(L.compose, "S1b", L.ledger()[2], L.queued(), want="submit S1a before S1b"))
L.preconditions = REAL_PRE
tmp = setup(done_rows(PRE))
code, o = run(["pack", ",".join(r["name"] for r in u[:2])])
case("real preconditions: no c0.json -> refused", "c0.json" in str(code) and "missing" in str(code))
import json as _json  # noqa: E402
Path(tmp, "results", "c0.json").write_text(_json.dumps({"C0": "PASS", "out_root": f"{tmp}/out"}))
calls.clear()
code, o = run(["pack", ",".join(r["name"] for r in u[:2])])
case("real preconditions: an S4U member without the uomni preflight -> refused",
     "preflight" in str(code) and not [c for c in calls if c[0] == "sbatch"])
Path(tmp, "preflight").mkdir()
Path(tmp, "preflight", "uomni.stat").write_text("1 2 3\n")
calls.clear()
code, o = run(["pack", ",".join(r["name"] for r in u[:2])])
case("real preconditions: with the preflight recorded and C0 PASS -> one S4U pack submitted",
     code == 0 and len([c for c in calls if c[0] == "sbatch"]) == 1)
Path(tmp, "results", "c0.json").write_text(_json.dumps({"C0": "FAIL", "out_root": f"{tmp}/out"}))
code, o = run(["pack", ",".join(r["name"] for r in S1a[4:8])])
case("real preconditions: C0 not PASS -> refused", "did not PASS" in str(code))
L.preconditions = lambda *a: None
# m1: a member with xsec.root but no rc line (classified TIMEOUT) is never retried
tmp = setup([R("57", "2dc_P_K4_S1_001", "TIMEOUT", 3060, "2026-10-17T09:09:00", END)], packs={"57": m4l})
status(tmp, "57", [])
out(tmp, n3)
code, o = run(["submit", "S1a", "--retry", n3, "--time", "01:16:00"])
case("m1: retry refused while out/<member>/xsec.root exists", "xsec.root exists" in str(code))
# m10: a failed job-id record write cancels the job and removes the retry record
tmp = setup([R("58", "2dc_P_K4_S1_001", "TIMEOUT", 3060, "2026-10-17T09:09:00", END)], packs={"58": m4l})
status(tmp, "58", [])
real_sp = L.sbatch_pack


def sp_fail(ms, t, dl):
    calls.append(["scancel", "999"])
    raise SystemExit("REFUSE: could not record pack")


L.sbatch_pack = sp_fail
code, o = run(["submit", "S1a", "--retry", n2, "--time", "01:16:00"])
case("m10: a record-write failure leaves no retry record behind",
     "could not record" in str(code) and not Path(tmp, "retries", f"{n2}.time").exists())
L.sbatch_pack = real_sp
# m3, m4: the real ledger() parse (TZ=UTC, billing floors) and queued()
SACCT = ("JobID|JobName|State|ElapsedRaw|AllocTRES|Timelimit|ReqTRES|Start|End\n"
         "1|2dc_P_K4_S1_001|PENDING|0||00:51:00|cpu=1,mem=487680M,node=1,billing=1|Unknown|Unknown\n"
         "2|2dc_P_K4_S1_005|COMPLETED|3000||00:51:00|cpu=1,mem=487680M,node=1,billing=1|2026-10-17T09:00:00|2026-10-17T09:50:00\n"
         "3|2dc_P_S1_009|COMPLETED|1800|cpu=64,mem=121920M,node=1,billing=64|00:51:00|billing=64|2026-10-17T09:00:00|x\n"
         "4|2dc_P_K4_S1_013|CANCELLED by 1|0||00:51:00|billing=1|None|2026-10-17T09:00:00\n"
         "5|other|COMPLETED|99|billing=256|01:00:00|billing=256|x|x\n")
envs = []


def sacct_run(cmd, **k):
    envs.append(k.get("env", {}).get("TZ"))
    if cmd[0] == "sacct":
        return type("R", (), {"returncode": 0, "stdout": SACCT, "stderr": ""})()
    if cmd[0] == "squeue":
        return type("R", (), {"returncode": 0, "stdout": "1|2dc_P_K4_S1_001\n31|2dc_P_S1_050\n", "stderr": ""})()
    return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()


tmp = setup([], packs={"1": m4l})
L.ledger, L.queued = REAL_LEDGER, REAL_QUEUED
L.subprocess.run = sacct_run
d, f, rl = L.ledger()
case("ledger: a pending pack whose ReqTRES says billing=1 is in flight at 256 x 00:51 / 256 = 0.85",
     abs(f - 0.85) < 1e-9)
case("ledger: a pack that ran with no AllocTRES billing is charged at 256 (3000 s -> 0.8333); a row at its 64",
     abs(d - (3000 * 256 + 1800 * 64) / 256 / 3600) < 1e-9 and [x.name for x in rl] == [
         "2dc_P_K4_S1_001", "2dc_P_K4_S1_005", "2dc_P_S1_009", "2dc_P_K4_S1_013"])
case("ledger: sacct is read with TZ=UTC and TimeLimit is kept", envs[0] == "UTC" and rl[1].tl == "00:51:00")
case("ledger: a never-started cancelled pack is not an attempt", L.never_started(rl[3].st, rl[3].el, rl[3].start))
case("queued: a queued pack contributes its members; a queued row itself", L.queued() == set(m4l) | {"2dc_P_S1_050"})
Path(tmp, "packs", "1.members").unlink()
case("queued: a queued pack with no member record fails closed", refused(L.queued, want="no member record"))
L.subprocess.run = fake_run
L.ledger = lambda: (0.0, 0.0, [])
L.queued = lambda: set()

# ---- gate stop rule -------------------------------------------------------------------------------------------------
setup(done_rows(PRE + ["G2"]), done=95.0, fly=0.0)
code, o = run(["gate", "S1a"])
case("gate refused with nothing in flight -> STOP wording", code == 3 and "Stop and report" in o)
setup(done_rows(PRE + ["G2"]) + [R("9", "2dc_P_S2_099", "PENDING")], done=80.0, fly=15.0)
code, o = run(["gate", "S1a"])
case("gate refused with jobs in flight -> wait", code == 3 and "Wait and re-check" in o)
setup(done_rows(PRE + ["G2"]), done=95.0)
calls.clear()
code, o = run(["submit", "S1a"])
case("submit refused -> stop, nothing submitted", code == 3 and "Stop and report" in o and not
     [c for c in calls if c[0] == "sbatch"])

# ---- migrate ----------------------------------------------------------------------------------------------------------
sq = "101|2dc_P_S1_001|shared\n102|2dc_P_K4_S1_005|regular\n103|2dc_P_S1_002|shared\n104|other_job|shared\n"


def sq_run(cmd, **k):
    calls.append(cmd)
    return type("R", (), {"returncode": 0, "stdout": sq if cmd[0] == "squeue" else "", "stderr": ""})()


tmp = setup([])
L.subprocess.run = sq_run
calls.clear()
code, o = run(["migrate", "--execute"])
sc = [c for c in calls if c[0] == "scancel"]
case("migrate: cancels exactly the PENDING shared-QOS rows, with --state=PENDING (packs and others left)",
     code == 0 and sc == [["scancel", "--state=PENDING", "101", "103"]] and
     any(Path(tmp, "gatelog").glob("migrate_*.tsv")) and any("-t" in c and "PENDING" in c for c in calls))
calls.clear()
code, o = run(["migrate", "--only", "2dc_P_S1_001,2dc_P_S1_003", "--execute"])
case("migrate --only: a name not PENDING now is refused, nothing cancelled",
     "2dc_P_S1_003" in str(code) and not [c for c in calls if c[0] == "scancel"])
calls.clear()
code, o = run(["migrate", "--only", "2dc_P_S1_001"])
case("migrate without --execute is a dry run", code == 0 and not [c for c in calls if c[0] == "scancel"])
L.subprocess.run = fake_run

# ---- deadline -------------------------------------------------------------------------------------------------------
import datetime as dt  # noqa: E402
spec2 = importlib.util.spec_from_file_location("launch2", PKG / "launch.py")
L2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(L2)
os.environ["TZ"] = "America/Los_Angeles"
if hasattr(__import__("time"), "tzset"):
    __import__("time").tzset()
case("deadline: --deadline=2026-10-20T23:00:00 in PDT before 06:00Z",
     L2.deadline_arg(dt.datetime(2026, 10, 17, tzinfo=dt.timezone.utc)) == ["--deadline=2026-10-20T23:00:00"])
case("deadline: refused between 06:00Z and the window's end",
     refused(L2.deadline_arg, dt.datetime(2026, 10, 21, 7, tzinfo=dt.timezone.utc), want="nothing is submitted"))

# ---- sbatch_pack.sh and sbatch_prod.sh with stubbed Slurm commands ---------------------------------------------------
subprocess.run = REAL_RUN
REAL_NS = "/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015"
sha_prod = hashlib.sha256((PKG / "sbatch_prod.sh").read_bytes()).hexdigest()
pack_src = (PKG / "sbatch_pack.sh").read_text()
case("sbatch_pack.sh MEMBER_SHA equals sha256(sbatch_prod.sh)", f"MEMBER_SHA={sha_prod}" in pack_src)


def sh_env(billing=256, qos="regular_1", tl="00:51:00", fail_member=None):
    t = Path(tempfile.mkdtemp())
    ns = t / "ns"
    pkg = ns / "repo_k/docs/orchestration/state/2d-closeout/stageC/production"
    pkg.mkdir(parents=True)
    for d in ("packs", "logs", "retries", "out"):
        (ns / d).mkdir()
    shutil.copy(PKG / "jobs.tsv", pkg / "jobs.tsv")
    shutil.copy(PKG / "sbatch_prod.sh", pkg / "sbatch_prod.sh")
    (t / "sbatch_pack.sh").write_text(pack_src.replace(REAL_NS, str(ns)))
    (t / "sbatch_prod.sh").write_text((PKG / "sbatch_prod.sh").read_text().replace(REAL_NS, str(ns)))
    b = t / "bin"
    b.mkdir()
    stubs = {
        "scontrol": f"#!/bin/bash\necho 'JobId=999 JobName=p QOS={qos} NumCPUs=256 TimeLimit={tl} "
                    f"AllocTRES=cpu=256,mem=487680M,node=1,billing={billing}'\n",
        "srun": "#!/bin/bash\necho \"$@\" >> \"$SRUN_LOG\"\n"
                f"for a in \"$@\"; do [ \"$a\" = \"--job-name={fail_member}\" ] && exit 1; done\nexit 0\n",
        "sacct": "#!/bin/bash\necho '999|p|COMPLETED|0:0|10'\n",
        "sleep": "#!/bin/bash\nexit 0\n",
    }
    for k, v in stubs.items():
        (b / k).write_text(v)
        (b / k).chmod(0o755)
    return t, ns


def run_pack(t, ns, members, record=None, name="2dc_P_K4_S1_001"):
    rec = record if record is not None else members
    (ns / "packs" / f"{name}.members").write_text(f"{name}\t00:51:00\t{','.join(rec)}\n")
    env = dict(os.environ, PATH=f"{t / 'bin'}:{os.environ['PATH']}", SLURM_JOB_ID="999", SLURM_JOB_NAME=name,
               SRUN_LOG=str(t / "srun.log"))
    p = subprocess.run(["bash", str(t / "sbatch_pack.sh"), *members], capture_output=True, text=True, env=env)
    log = (t / "srun.log").read_text().splitlines() if (t / "srun.log").exists() else []
    return p.returncode, p.stdout + p.stderr, log


m4 = [n1, n2, n3, n4]
t, ns = sh_env()
rc, o, log = run_pack(t, ns, m4)
st = (ns / "packs" / "999.status").read_text() if (ns / "packs" / "999.status").exists() else ""
case("dispatcher: a good pack starts 4 srun --exact -N1 -n1 -c 64 --mem=121920M steps, each named and --member'd",
     rc == 0 and len(log) == 4 and all(f"--exact -N1 -n1 -c 64 --mem=121920M --job-name={m} " in l and
                                       l.endswith(f"--member {m}") for m, l in zip(m4, sorted(log))))
case("dispatcher: each member's rc is recorded", all(f"{m}\t0\t" in st for m in m4) and "#step" in st)
for label, members, kw, rec, want in (
        ("a duplicated member", [n1, n1, n2, n3], {}, None, "repeats"),
        ("an unknown member", [n1, n2, n3, "2dc_P_S1_999x"], {}, None, "not exactly one jobs.tsv row"),
        ("a mixed class", [n1, u[0]["name"]], {}, None, "differ in class"),
        ("arguments that differ from the launcher's record", m4, {}, [n1, n2, n3, "2dc_P_S1_009"], "differ from"),
        ("billing 64", m4, {"billing": 64}, None, "billing '64' != pack billing 256"),
        ("QOS shared", m4, {"qos": "shared"}, None, "QOS shared is not regular"),
        ("a TimeLimit other than the cap", m4, {"tl": "01:00:00"}, None, "TimeLimit 01:00:00")):
    t, ns = sh_env(**kw)
    rc, o, log = run_pack(t, ns, members, record=rec)
    case(f"dispatcher refuses {label} before any step", rc == 4 and want in o and not log)
t, ns = sh_env(qos="regular")
rc, o, log = run_pack(t, ns, m4)
case("dispatcher accepts QOS regular as well as regular_1 (the name Slurm records)", rc == 0 and len(log) == 4)
t, ns = sh_env(fail_member=n2)
rc, o, log = run_pack(t, ns, m4)
st = (ns / "packs" / "999.status").read_text()
case("dispatcher: one failing member does not stop the others (4 steps, rc 1 recorded, pack exit 1)",
     rc == 1 and len(log) == 4 and f"{n2}\t1\t" in st and all(f"{m}\t0\t" in st for m in (n1, n3, n4)))


# dispatcher: a retry pack at its recorded cap is accepted; a member without the record (class differs) is refused
t, ns = sh_env(tl="01:16:00")
for m in m4:
    (ns / "retries" / f"{m}.time").write_text("01:16:00\n")
rc, o, log = run_pack(t, ns, m4)
case("dispatcher accepts a retry pack whose TimeLimit equals every member's retry record", rc == 0 and len(log) == 4)
t, ns = sh_env(tl="01:16:00")
for m in m4[:3]:
    (ns / "retries" / f"{m}.time").write_text("01:16:00\n")
rc, o, log = run_pack(t, ns, m4)
case("dispatcher refuses a retry pack where one member lacks the record", rc == 4 and "differ in class" in o and not log)
# dispatcher memory clause, on a jobs.tsv that breaks it (the pin re-set to that table in the test copy only)
t, ns = sh_env()
pkg = ns / "repo_k/docs/orchestration/state/2d-closeout/stageC/production"
hdr, *body = (PKG / "jobs.tsv").read_text().splitlines()
fake_rows = []
for i in range(3):
    f = body[0].split("\t")
    f[0], f[5] = f"2dc_P_S1_9{i:02d}", "180000M"
    fake_rows.append("\t".join(f))
(pkg / "jobs.tsv").write_text("\n".join([hdr] + body + fake_rows) + "\n")
fsha = hashlib.sha256((pkg / "jobs.tsv").read_bytes()).hexdigest()
src = (t / "sbatch_pack.sh").read_text()
(t / "sbatch_pack.sh").write_text(re.sub(r"^JOBS_SHA=[0-9a-f]{64}", f"JOBS_SHA={fsha}", src, flags=re.M))
fn = [r.split("\t")[0] for r in fake_rows]
rc, o, log = run_pack(t, ns, fn, name="2dc_P_K3_S1_900")
case("dispatcher refuses 3 x 180000M > 515100M (the memory clause) before any step",
     rc == 4 and "summed member memory 540000M exceeds" in o and not log)
rc, o, log = run_pack(t, ns, fn[:2], name="2dc_P_K2_S1_900")
case("dispatcher accepts 2 x 180000M on that table", rc == 0 and len(log) == 2)


def run_member(args, step="0", billing=256, cpus="64"):
    t, ns = sh_env(billing=billing)
    env = dict(os.environ, PATH=f"{t / 'bin'}:{os.environ['PATH']}", SLURM_JOB_ID="999", SLURM_JOB_NAME="x",
               SLURM_CPUS_PER_TASK=cpus, SRUN_LOG=str(t / "srun.log"))
    if step is not None:
        env["SLURM_STEP_ID"] = step
    else:
        env.pop("SLURM_STEP_ID", None)
    p = subprocess.run(["bash", str(t / "sbatch_prod.sh"), *args], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


rc, o = run_member([])
case("member runner refuses without --member", rc == 4 and "usage" in o)
rc, o = run_member(["--member", n1])
case("member runner: a good member passes every check (reaches the step log, no REFUSE)",
     "[prod] step 999.0" in o and "REFUSE" not in o)
rc, o = run_member(["--member", n1], step=None)
case("member runner refuses outside an srun step", rc == 4 and "srun step" in o)
rc, o = run_member(["--member", n1], step="batch")
case("member runner refuses in the batch step", rc == 4 and "srun step" in o)
rc, o = run_member(["--member", "2dc_P_S1_999x"])
case("member runner refuses an unknown member", rc == 4 and "not exactly one jobs.tsv row" in o)
rc, o = run_member(["--member", n1], billing=64)
case("member runner refuses billing 64", rc == 4 and "billing '64'" in o)
t2, ns2 = sh_env(qos="shared")
env = dict(os.environ, PATH=f"{t2 / 'bin'}:{os.environ['PATH']}", SLURM_JOB_ID="999", SLURM_STEP_ID="0",
           SLURM_CPUS_PER_TASK="64")
p = subprocess.run(["bash", str(t2 / "sbatch_prod.sh"), "--member", n1], capture_output=True, text=True, env=env)
case("member runner refuses QOS shared", p.returncode == 4 and "QOS shared is not regular" in p.stdout + p.stderr)
rc, o = run_member(["--member", n1], cpus="128")
case("member runner refuses a CPU mismatch", rc == 4 and "step CPUs '128' != 64" in o)

print(f"RAN {RAN[0]}, FAILED {len(FAILS)}")
sys.exit(1 if FAILS else 0)
