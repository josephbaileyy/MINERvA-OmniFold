#!/usr/bin/env python3
"""Stage C production launcher: the grant's charge gate, then sbatch with the frozen job table (jobs.tsv).

  python launch.py gate  <batch> [--retry NAME --time HH:MM:SS]   print the gate arithmetic; submit nothing
  python launch.py submit <batch> [--retry NAME --time HH:MM:SS]  gate, preconditions, then sbatch each job
  python launch.py redo <batch>                                   submit the batch's rows owed a submission: never
                                                                  started (DEADLINE), a deadline-cancelled retry, or
                                                                  never submitted after an sbatch failure (owed())
  python launch.py simulate {mean,p84,cap}                        the worked example of DESIGN §6 (no Slurm)

Runs on a NERSC login node from the deployed package ($NS/repo/docs/orchestration/state/2d-closeout/stageC/production).
Adapted from the pilot's launch.py (stageC/pilot, v2 a2ea0d6a): same gate, same guards; production names, ceiling,
namespace, preconditions and the maintenance deadline.

GATE (AUTHORIZATION-20261015-2d-closeout-stageC-production.md §3): before each batch,
    charges of terminal 2dc_P_* jobs from sacct (ElapsedRaw x billing / 256 / 3600)
  + the FULL enforced worst case of every 2dc_P_* job still PENDING or RUNNING (billing x TimeLimit / 256)
  + the batch's enforced worst case (billing x cap / 256, from jobs.tsv; a retry uses its re-projected cap)
  <= 100.0 charged node-h, otherwise REFUSE. `gate` only prints (the executor waits and re-checks); a refusal by
`submit` is a stop-and-report (grant §3). If sacct cannot be read, the gate refuses: an unreadable ledger is not zero.

MAINTENANCE (grant §3): Perlmutter maintenance runs 2026-10-21 06:00 to 2026-10-28 06:00 UTC. Every job submitted
before the window carries --deadline at its start, so Slurm never starts a job that could not end before it
(state DEADLINE, never started, charge 0). Such a job is not an attempt: it may be submitted again after the window,
under its own name, through the gate. Nothing is submitted while the window is open.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 9):
    raise SystemExit("REFUSE: launch.py needs Python >= 3.9; source setup_salloc_env.sh first (root_6_28 has 3.11)")
HERE = Path(__file__).resolve().parent
CEILING = 100.0
PREFIX = "2dc_P_"
WINDOW_START = "2026-10-15T00:00:00"
NS = "/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015"
SBATCH = f"{NS}/repo/docs/orchestration/state/2d-closeout/stageC/production/sbatch_prod.sh"
MAINT_START = dt.datetime(2026, 10, 21, 6, 0, tzinfo=dt.timezone.utc)
MAINT_END = dt.datetime(2026, 10, 28, 6, 0, tzinfo=dt.timezone.utc)
IN_FLIGHT = ("PENDING", "RUNNING", "REQUEUED", "RESIZING", "SUSPENDED", "CONFIGURING", "COMPLETING")
ORDER = ["G0", "G1", "G2", "S1a", "S1b", "S1c", "S1d", "S1e", "S1f", "S2a", "S2b", "S4a", "S4b"]


def hours(t):
    d = 0
    if "-" in t:
        dd, t = t.split("-")
        d = int(dd)
    p = [int(x) for x in t.split(":")]
    while len(p) < 3:
        p.insert(0, 0)
    return d * 24 + p[0] + p[1] / 60 + p[2] / 3600


def table():
    with open(HERE / "jobs.tsv") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def enforced(row, time=None):
    return int(row["billing"]) * hours(time or row["time"]) / 256


def ledger():
    """Every 2dc_P_* job since the window start: (completed charge, in-flight enforced, rows).

    An in-flight job's liability uses the larger of its jobs.tsv billing and any billing Slurm reports
    (AllocTRES, else ReqTRES); sbatch_prod.sh refuses at start a job whose allocated billing differs."""
    tbl = {r["name"]: int(r["billing"]) for r in table()}
    cmd = ["sacct", "-X", "-P", "-S", WINDOW_START, "-E", "now", "-u", os.environ.get("USER", "josephrb"),
           "-o", "JobID,JobName,State,ElapsedRaw,AllocTRES,Timelimit,ReqTRES"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    lines = r.stdout.strip().splitlines()
    if r.returncode != 0 or not lines or not lines[0].startswith("JobID|"):
        raise SystemExit(f"REFUSE: sacct unreadable (rc {r.returncode}); the gate does not treat that as zero")
    done = fly = 0.0
    rows = []
    for ln in lines[1:]:
        jid, name, state, el, alloc, tl, req = ln.split("|")
        if not name.startswith(PREFIX):
            continue
        tres = alloc if "billing=" in alloc else req
        bill = int(tres.split("billing=")[1].split(",")[0]) if "billing=" in tres else None
        st = state.split()[0]
        if st in IN_FLIGHT:
            cands = [x for x in (bill, tbl.get(name)) if x is not None]
            if not cands:
                raise SystemExit(f"REFUSE: no billing for in-flight job {jid}")
            liab = max(cands) * hours(tl) / 256
            fly += liab
            rows.append((jid, name, st, int(el), "in-flight at cap", round(liab, 4)))
        else:
            ch = int(el) * (bill or 0) / 256 / 3600
            done += ch
            rows.append((jid, name, st, int(el), "charged", round(ch, 4)))
    return done, fly, rows


def queued():
    """Job names this user has in the Slurm queue now (squeue sees a submission before sacct may)."""
    r = subprocess.run(["squeue", "-h", "-u", os.environ.get("USER", "josephrb"), "-o", "%j"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"REFUSE: squeue unreadable (rc {r.returncode})")
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith(PREFIX)}


def attempts(rows):
    """jobs.tsv name -> list of sacct states of its attempts. A DEADLINE row that never started (ElapsedRaw 0) is
    not an attempt (module docstring, MAINTENANCE)."""
    out = {}
    for jid, name, st, el, _, _ in rows:
        if st == "DEADLINE" and el == 0:
            continue
        out.setdefault(name, []).append(st)
    return out


def gate(batch_rows, times, verbose=True):
    """times: job name -> the cap it is submitted with (the row's, or its retry record's)."""
    done, fly, rows = ledger()
    b = sum(enforced(r, times[r["name"]]) for r in batch_rows)
    total = done + fly + b
    if verbose:
        for x in rows:
            print("  ", *x)
        print(f"GATE completed {done:.4f} + in-flight at cap {fly:.4f} + batch {b:.4f} = {total:.4f} "
              f"vs ceiling {CEILING}")
    return total <= CEILING + 1e-12, total, fly


def owed(batch_rows):
    """redo: the batch's rows that are owed a submission, with the cap each is submitted with.
      (a) a row whose only record is a never-started DEADLINE row: at its jobs.tsv cap;
      (b) a walltime retry cancelled by the deadline before it started (records: one TIMEOUT attempt, a never-started
          DEADLINE row, and its retries/<name>.time): at the recorded cap;
      (c) a row never submitted while other rows of the batch were (an sbatch failure mid-batch): at its cap.
    Nothing that ran, nothing queued, and nothing with a second attempt is ever owed."""
    _, _, rl = ledger()
    dead = {name for _, name, st, el, _, _ in rl if st == "DEADLINE" and el == 0}
    seen = {name for _, name, _, _, _, _ in rl}
    att, inq = attempts(rl), queued()
    partial = any(r["name"] in seen or r["name"] in inq for r in batch_rows)
    out, times = [], {}
    for r in batch_rows:
        n, prior = r["name"], att.get(r["name"], [])
        rec = Path(NS, "retries", f"{n}.time")
        if n in inq or any(Path(NS, "out", n).glob("*")):
            continue
        if n in dead and not prior and not rec.exists():
            out.append(r); times[n] = r["time"]
        elif n in dead and prior == ["TIMEOUT"] and rec.exists():
            out.append(r); times[n] = rec.read_text().strip()
        elif partial and n not in seen:
            out.append(r); times[n] = r["time"]
    return out, times


def load_result(f):
    p = Path(NS, "results", f)
    if not p.is_file():
        raise SystemExit(f"REFUSE: precondition {p} missing")
    return json.load(open(p))


def preconditions(batch):
    """Order rules (DESIGN §6). Each reads a result written by the frozen analysis (analyze_prod.py)."""
    if batch == "G0":
        return
    c0 = load_result("c0.json")
    if c0.get("out_root") != f"{NS}/out":
        raise SystemExit("REFUSE: c0.json was not computed from the production outputs ($NS/out)")
    if c0.get("C0") != "PASS":
        raise SystemExit("REFUSE: the controls (C0) did not PASS; production stops (grant §3)")
    if batch == "G2" and not Path(NS, "preflight", "uomni.stat").is_file():
        raise SystemExit("REFUSE: the universe-omnifile preflight (preflight_uomni.sh) is not recorded")
    i = ORDER.index(batch)
    names = {r["name"] for r in table() if r["batch"] in ORDER[:i]}
    seen = set(attempts(ledger()[2])) | queued()
    if not names <= seen:   # batches go in the frozen order; a DEADLINE-only row must be resubmitted first
        raise SystemExit(f"REFUSE: {batch} follows {ORDER[:i]}; {len(names - seen)} earlier jobs not yet submitted")


def deadline_arg(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    if MAINT_START <= now < MAINT_END:
        raise SystemExit("REFUSE: the maintenance window is open (grant §3); nothing is submitted until it ends")
    if now < MAINT_START:   # Slurm reads --deadline in the cluster's local time; pass an explicit UTC-derived value
        local = MAINT_START.astimezone()   # the login node's local zone
        return [f"--deadline={local.strftime('%Y-%m-%dT%H:%M:%S')}"]
    return []


def simulate(mode):
    """Worked example (DESIGN §6): batches in the frozen order, each admitted against the charges of every earlier
    batch, with no overlap (the floor of the gate's totals) and costs per job at the pilot's measured mean, p84
    (u_CV) / max (u_U,sel, u_A), or the cap."""
    unit = {"mean": {"cv": 0.0754, "u": 0.1418, "a": 0.3293},
            "p84": {"cv": 0.0933, "u": 0.2232, "a": 0.3889}}
    rows = table()
    spent = 0.0
    print(f"mode={mode}  ceiling={CEILING}")
    for b in ORDER:
        br = [r for r in rows if r["batch"] == b]
        cap = sum(enforced(r) for r in br)
        ok = spent + cap <= CEILING + 1e-12
        if mode == "cap":
            cost = cap
        else:
            k = lambda r: "a" if r["item"] == "S3" else "u" if r["name"].startswith("2dc_P_S4U_") else "cv"
            cost = sum(unit[mode][k(r)] for r in br)
        print(f"  {b:4s}: {len(br):3d} jobs  gate {spent:.4f} + {cap:.4f} = {spent + cap:.4f}  "
              f"{'OK' if ok else 'REFUSE'}  then charged {cost:.4f}")
        if not ok:
            print(f"  first refusal at {b}")
            return
        spent += cost
    print(f"  all batches admitted; total charged {spent:.4f}; unused at the ceiling {CEILING - spent:.4f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["gate", "submit", "redo", "simulate"])
    ap.add_argument("arg")
    ap.add_argument("--retry")
    ap.add_argument("--time")
    a = ap.parse_args()
    if a.action == "simulate":
        return simulate(a.arg)
    rows = table()
    if a.retry:
        br = [r for r in rows if r["name"] == a.retry]
        if len(br) != 1 or not a.time or hours(a.time) >= 12:
            raise SystemExit("REFUSE: --retry needs one jobs.tsv name and a re-projected --time under 12 h")
    else:
        br = [r for r in rows if r["batch"] == a.arg]
        if not br:
            raise SystemExit(f"REFUSE: no batch {a.arg}")
    for d in ("logs", "results", "retries", "out", "tmp", "gatelog"):
        Path(NS, d).mkdir(parents=True, exist_ok=True)
    times = {r["name"]: (a.time if a.retry else r["time"]) for r in br}
    if a.action == "redo":
        if a.retry:
            raise SystemExit("REFUSE: redo takes a batch, not --retry")
        br, times = owed(br)
        if not br:
            raise SystemExit(f"REFUSE: batch {a.arg} has no rows owed a submission (see owed())")
    done, fly, rows_l = ledger()
    att = attempts(rows_l)
    inq = queued()
    for r in (br if a.action != "redo" else []):
        prior = att.get(r["name"], [])
        if r["name"] in inq:
            raise SystemExit(f"REFUSE: {r['name']} is in the Slurm queue now; no double submission")
        if a.retry:
            if prior != ["TIMEOUT"]:
                raise SystemExit(f"REFUSE: {r['name']} has attempts {prior}; a walltime retry needs exactly one "
                                 "TIMEOUT attempt (grant §3). Out of memory is a stop; any other failure needs a "
                                 "diagnosed infrastructure cause and the director")
            if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", a.time):
                raise SystemExit("REFUSE: --time must be HH:MM:SS (scontrol's TimeLimit format)")
            if Path(NS, "retries", f"{r['name']}.time").exists():
                raise SystemExit(f"REFUSE: {r['name']} already has a retry record")
            if any(Path(NS, "out", r["name"]).glob("*")):
                raise SystemExit(f"REFUSE: move out/{r['name']} aside (sha-verified) before the retry")
        elif prior:
            raise SystemExit(f"REFUSE: {r['name']} was already submitted ({prior}); no double submission")
    dl = deadline_arg()
    ok, total, fly = gate(br, times)
    if not ok:
        if a.action == "gate" and fly > 0:
            print("NOT ADMITTED: the batch would exceed the ceiling with jobs still in flight. Wait and re-check.")
        else:   # a submit refusal, or a pre-check refusal with nothing in flight (waiting cannot help): a stop
            print("REFUSE: the batch would exceed the ceiling. Stop and report to the director (grant §3).")
        return 3
    if a.action == "gate":
        return 0
    preconditions(br[0]["batch"])
    rec = Path(NS, "retries", f"{a.retry}.time") if a.retry else None
    if rec is not None:   # written before sbatch (the job reads it at start), removed if sbatch fails
        rec.write_text(a.time + "\n")
    for r in br:
        cmd = ["sbatch", f"--job-name={r['name']}", f"--qos={r['qos']}", f"--cpus-per-task={r['cpus']}",
               f"--mem={r['mem']}", f"--time={times[r['name']]}", "--no-requeue", *dl, SBATCH]
        print("+", " ".join(cmd))
        s = subprocess.run(cmd, capture_output=True, text=True)
        print(s.stdout.strip(), s.stderr.strip())
        if s.returncode != 0:
            if rec is not None:
                rec.unlink()
            raise SystemExit(f"sbatch failed for {r['name']}; nothing further submitted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
