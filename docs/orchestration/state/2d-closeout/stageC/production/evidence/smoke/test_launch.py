#!/usr/bin/env python3
"""Offline tests of launch.py's guards with a mocked Slurm ledger (no sacct, squeue or sbatch is called).

  python test_launch.py      (from anywhere; prints one line per case and exits 1 on any failure)

Cases: redo's three owed kinds and its refusals; the TIMEOUT-only walltime retry; the gate's stop rule (a pre-check
that does not admit is a wait only while 2dc_P_* jobs are in flight); --no-requeue on every sbatch line.
"""
import contextlib
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("launch", HERE.parents[1] / "launch.py")
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
FAILS = []


def case(name, ok):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        FAILS.append(name)


def setup(rows, queue=(), done=0.0, fly=0.0):
    tmp = tempfile.mkdtemp()
    L.NS = tmp
    for d in ("out", "retries", "results", "logs", "tmp", "gatelog"):
        Path(tmp, d).mkdir()
    L.ledger = lambda: (done, fly, rows)
    L.queued = lambda: set(queue)
    return tmp


S1a = [r for r in L.table() if r["batch"] == "S1a"]
n1, n2, n3 = S1a[0]["name"], S1a[1]["name"], S1a[2]["name"]

# (a) never-started DEADLINE rows are owed at their cap; rows that ran are not
setup([("1", n1, "DEADLINE", 0, "charged", 0.0), ("2", n2, "COMPLETED", 900, "charged", 0.06)])
br, t = L.owed(S1a)
case("redo (a): DEADLINE-only row owed at its cap; a COMPLETED row not owed",
     [r["name"] for r in br if r["name"] in (n1, n2)] == [n1] and t[n1] == "00:51:00")
# (c) a batch half-submitted by an sbatch failure: the never-submitted rows are owed
setup([("2", n2, "COMPLETED", 900, "charged", 0.06)])
br, t = L.owed(S1a)
case("redo (c): partial batch -> the 49 never-submitted rows are owed", len(br) == 49 and n2 not in t)
# a batch never submitted at all is not 'partial': redo owes nothing (use submit)
setup([])
br, t = L.owed(S1a)
case("redo: an unsubmitted batch owes nothing (submit, not redo)", br == [])
# (b) a deadline-cancelled walltime retry is owed at its recorded cap
tmp = setup([("1", n1, "TIMEOUT", 3060, "charged", 0.2125), ("3", n1, "DEADLINE", 0, "charged", 0.0)])
Path(tmp, "retries", f"{n1}.time").write_text("01:16:00\n")
br, t = L.owed(S1a)
case("redo (b): deadline-cancelled retry owed at the recorded cap", n1 in t and t[n1] == "01:16:00")
# a retry that ran (second attempt) is never owed
tmp = setup([("1", n1, "TIMEOUT", 3060, "charged", 0.2), ("3", n1, "TIMEOUT", 4560, "charged", 0.3)])
Path(tmp, "retries", f"{n1}.time").write_text("01:16:00\n")
br, t = L.owed(S1a)
case("redo: a retry that ran is never owed", n1 not in t)
# a queued row or a row with output is never owed
tmp = setup([("1", n1, "DEADLINE", 0, "charged", 0.0)], queue={n1})
case("redo: a queued row is never owed", n1 not in L.owed(S1a)[1])
tmp = setup([("1", n1, "DEADLINE", 0, "charged", 0.0)])
Path(tmp, "out", n1).mkdir()
Path(tmp, "out", n1, "xsec.root").write_text("x")
case("redo: a row with output is never owed", n1 not in L.owed(S1a)[1])


def run(argv):
    sys.argv = ["launch.py"] + argv
    buf = io.StringIO()
    code = None
    with contextlib.redirect_stdout(buf):
        try:
            code = L.main()
        except SystemExit as e:
            code = str(e)
    return code, buf.getvalue()


L.deadline_arg = lambda now=None: []
calls = []
L.subprocess.run = lambda cmd, **k: (calls.append(cmd), type("R", (), {"returncode": 0, "stdout": "Submitted", "stderr": ""})())[1]
L.preconditions = lambda b: None
# walltime retry only after exactly one TIMEOUT
for st, want in (("TIMEOUT", True), ("OUT_OF_MEMORY", False), ("FAILED", False), ("CANCELLED", False)):
    setup([("1", n3, st, 100, "charged", 0.01)])
    calls.clear()
    code, out = run(["submit", "S1a", "--retry", n3, "--time", "01:16:00"])
    case(f"retry after {st}: {'allowed' if want else 'refused'}", (code == 0 and len(calls) == 1) == want)
setup([("1", n3, "TIMEOUT", 100, "charged", 0.01)])
calls.clear()
run(["submit", "S1a", "--retry", n3, "--time", "01:16:00"])
case("sbatch line has --no-requeue and --time=01:16:00",
     len(calls) == 1 and "--no-requeue" in calls[0] and "--time=01:16:00" in calls[0])
# gate stop rule
setup([], done=95.0, fly=0.0)
code, out = run(["gate", "S1a"])
case("gate pre-check refused with nothing in flight -> STOP wording", code == 3 and "Stop and report" in out)
setup([("9", "2dc_P_S1_999", "PENDING", 0, "in-flight at cap", 0.0)], done=80.0, fly=15.0)
code, out = run(["gate", "S1a"])
case("gate pre-check refused with jobs in flight -> wait", code == 3 and "Wait and re-check" in out)
setup([], done=95.0, fly=0.0)
calls.clear()
code, out = run(["submit", "S1a"])
case("submit refused -> stop, nothing submitted", code == 3 and "Stop and report" in out and not calls)
sys.exit(1 if FAILS else 0)
