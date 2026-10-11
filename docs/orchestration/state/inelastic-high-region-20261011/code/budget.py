"""Aggregate CPU budget for the inelastic high-region study (PLAN.md §2).

Every scientific run goes through ``run``. Before launch it refuses a run whose declared cap would take the
ledger past the aggregate limit. The child runs under ``ulimit -t <cap>``. Charged CPU is the child's
user+sys time (``RUSAGE_CHILDREN``) plus any remote CPU the child reports on a ``BUDGET_REMOTE_CPU_S=<s>``
stdout line; a run whose remote CPU was expected but not reported is charged its full cap.

Usage::

    python3 budget.py run --id R1 --cap-s 300 [--remote] --log ../logs/R1.log -- <command ...>
    python3 budget.py charge --id PRE --cpu-s 30 --note "pre-plan inspection"
    python3 budget.py total
"""
import argparse
import datetime as dt
import json
import os
import re
import resource
import shlex
import subprocess
import sys

LIMIT_S = 7200.0
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "logs", "budget_ledger.jsonl")
REMOTE_RE = re.compile(r"^BUDGET_REMOTE_CPU_S=([0-9.eE+-]+)\s*$", re.M)


def entries():
    if not os.path.exists(LEDGER):
        return []
    with open(LEDGER) as f:
        return [json.loads(line) for line in f if line.strip()]


def total():
    return sum(e["charged_cpu_s"] for e in entries())


def append(rec):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def cmd_run(a):
    spent = total()
    if spent + a.cap_s > LIMIT_S:
        sys.exit(f"REFUSED: spent {spent:.1f} + cap {a.cap_s:.1f} > limit {LIMIT_S:.0f} core-s")
    cmd = a.command[1:] if a.command and a.command[0] == "--" else a.command
    shell = f"ulimit -t {int(a.cap_s) + 1}; exec " + " ".join(shlex.quote(c) for c in cmd)
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = dt.datetime.now()
    p = subprocess.run(["/bin/bash", "-c", shell], capture_output=True, text=True)
    wall = (dt.datetime.now() - t0).total_seconds()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    local = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    m = REMOTE_RE.findall(p.stdout)
    remote = float(m[-1]) if m else None
    if a.remote and remote is None:
        charged, rule = float(a.cap_s), "remote CPU not reported: full cap charged"
    else:
        charged, rule = local + (remote or 0.0), "measured"
    if a.log:
        os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
        with open(a.log, "w") as f:
            f.write(f"# {now()} id={a.id} rc={p.returncode} cmd={' '.join(cmd)}\n")
            f.write(p.stdout)
            if p.stderr:
                f.write("\n[stderr]\n" + p.stderr)
    rec = {"id": a.id, "utc": now(), "cmd": cmd, "cap_s": a.cap_s, "rc": p.returncode, "wall_s": round(wall, 3),
           "local_cpu_s": round(local, 3), "remote_cpu_s": remote, "charged_cpu_s": round(charged, 3),
           "rule": rule, "cumulative_after_s": round(spent + charged, 3), "note": a.note}
    append(rec)
    sys.stdout.write(p.stdout[-4000:])
    if p.stderr:
        sys.stderr.write(p.stderr[-2000:])
    print(f"[budget] {a.id}: rc={p.returncode} charged {charged:.2f} s; cumulative {spent + charged:.2f} / {LIMIT_S:.0f}")
    sys.exit(p.returncode)


def cmd_charge(a):
    spent = total()
    if spent + a.cpu_s > LIMIT_S:
        sys.exit(f"REFUSED: spent {spent:.1f} + {a.cpu_s:.1f} > limit")
    append({"id": a.id, "utc": now(), "cmd": None, "cap_s": a.cpu_s, "rc": None, "wall_s": None,
            "local_cpu_s": None, "remote_cpu_s": None, "charged_cpu_s": a.cpu_s, "rule": "manual charge",
            "cumulative_after_s": round(spent + a.cpu_s, 3), "note": a.note})
    print(f"[budget] charged {a.cpu_s} s; cumulative {spent + a.cpu_s:.2f}")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run")
    r.add_argument("--id", required=True)
    r.add_argument("--cap-s", type=float, required=True)
    r.add_argument("--remote", action="store_true")
    r.add_argument("--log")
    r.add_argument("--note", default="")
    r.add_argument("command", nargs=argparse.REMAINDER)
    c = sp.add_parser("charge")
    c.add_argument("--id", required=True)
    c.add_argument("--cpu-s", type=float, required=True)
    c.add_argument("--note", default="")
    sp.add_parser("total")
    a = ap.parse_args()
    if a.cmd == "run":
        cmd_run(a)
    elif a.cmd == "charge":
        cmd_charge(a)
    else:
        print(f"{total():.3f} / {LIMIT_S:.0f} core-s over {len(entries())} entries")


if __name__ == "__main__":
    main()
