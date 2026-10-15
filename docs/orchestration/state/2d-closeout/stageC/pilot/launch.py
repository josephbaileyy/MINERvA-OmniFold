#!/usr/bin/env python3
"""Stage C pilot launcher: the director's charge gate, then sbatch with the frozen job table (jobs.tsv).

  python launch.py gate  <batch> [--retry NAME --time HH:MM:SS]   print the gate arithmetic; submit nothing
  python launch.py submit <batch> [--retry NAME --time HH:MM:SS]  gate, preconditions, then sbatch each job
  python launch.py simulate {median,cap}                          the worked example of DESIGN §4 (no Slurm)

Runs on a NERSC login node from the deployed package ($NS/repo/docs/orchestration/state/2d-closeout/stageC/pilot).

GATE (director, 2026-10-13; AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md and its binding addendum): before
each batch,
    charges of COMPLETED (terminal) 2dc_C_* jobs from sacct (ElapsedRaw x billing / 256 / 3600)
  + the FULL enforced worst case of every 2dc_C_* job still PENDING or RUNNING (billing x TimeLimit / 256)
  + the batch's enforced worst case (billing x cap / 256, from jobs.tsv; a retry uses its re-projected cap)
  <= 20.0 charged node-h, otherwise REFUSE: stop and report to the director. A running job's partial charge is
not its liability. The same gate is P2-G2's seed-43 pre-declared actual-charge check. A refusal never shrinks a
declared batch (P1 stays 20 + 20 + 20 unless the director records otherwise before data).

Every sacct row since the window start counts, whatever its state (cancelled, failed, timed out, retries,
controls). If sacct cannot be read (no header, rc != 0), the gate refuses: an unreadable ledger is not zero.
"""
import argparse
import csv
import json
import re
import os
import subprocess
import sys
from pathlib import Path

if sys.version_info < (3, 9):
    raise SystemExit("REFUSE: launch.py needs Python >= 3.9; source setup_salloc_env.sh first (root_6_28 has 3.11)")
HERE = Path(__file__).resolve().parent
CEILING = 20.0
WINDOW_START = "2026-10-13T00:00:00"
NS = "/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013"
SBATCH = f"{NS}/repo/docs/orchestration/state/2d-closeout/stageC/pilot/sbatch_pilot.sh"
TERMINAL_RUNNING = ("PENDING", "RUNNING", "REQUEUED", "RESIZING", "SUSPENDED", "CONFIGURING", "COMPLETING")


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
    """Every 2dc_C_* job since the window start: (completed charge, in-flight enforced, rows).

    An in-flight job's liability uses the larger of its jobs.tsv billing and any billing Slurm reports
    (AllocTRES, else ReqTRES), so a pending job's ReqTRES cannot understate it; sbatch_pilot.sh refuses at start
    a job whose allocated billing differs from jobs.tsv."""
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
        if not name.startswith("2dc_C_"):
            continue
        tres = alloc if "billing=" in alloc else req
        bill = int(tres.split("billing=")[1].split(",")[0]) if "billing=" in tres else None
        st = state.split()[0]
        if st in TERMINAL_RUNNING:
            b = max(x for x in (bill, tbl.get(name)) if x is not None) if (bill or tbl.get(name)) else None
            if b is None:
                raise SystemExit(f"REFUSE: no billing for in-flight job {jid}")
            liab = b * hours(tl) / 256
            fly += liab
            rows.append((jid, name, st, "in-flight at cap", round(liab, 4)))
        else:
            ch = int(el) * (bill or 0) / 256 / 3600
            done += ch
            rows.append((jid, name, st, "charged", round(ch, 4)))
    return done, fly, rows


def queued():
    """Job names this user has in the Slurm queue now (squeue sees a submission before sacct may)."""
    r = subprocess.run(["squeue", "-h", "-u", os.environ.get("USER", "josephrb"), "-o", "%j"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"REFUSE: squeue unreadable (rc {r.returncode})")
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("2dc_C_")}


def attempts(rows):
    """jobs.tsv name -> list of sacct states of its attempts (array tasks are not used by this package)."""
    out = {}
    for jid, name, st, _, _ in rows:
        out.setdefault(name, []).append(st)
    return out


def gate(batch_rows, retry=None, time=None, verbose=True):
    done, fly, rows = ledger()
    b = sum(enforced(r, time if retry else None) for r in batch_rows)
    total = done + fly + b
    if verbose:
        for x in rows:
            print("  ", *x)
        print(f"GATE completed {done:.4f} + in-flight at cap {fly:.4f} + batch {b:.4f} = {total:.4f} "
              f"vs ceiling {CEILING}")
    return total <= CEILING + 1e-12, total


def preconditions(batch):
    """Order rules (DESIGN §4). Each reads a result written by the frozen analyses on the namespace."""
    res = Path(NS, "results")

    def load(f):
        p = res / f
        if not p.is_file():
            raise SystemExit(f"REFUSE: precondition {p} missing")
        return json.load(open(p))
    if batch == "B0":
        return
    if load("p0.json").get("P0") != "PASS":
        raise SystemExit("REFUSE: P0 did not PASS; the pilot stops (record §3)")
    if batch in ("B1", "B2", "B3") and not Path(NS, "preflight", "uomni.stat").is_file():
        raise SystemExit("REFUSE: the universe-omnifile preflight (preflight_uomni.sh) is not recorded")
    if batch in ("B2", "B3"):
        if not Path(NS, "out", "2dc_C_P2_Flux23", "xsec.root").is_file():
            raise SystemExit("REFUSE: run a of P2-G2 (out/2dc_C_P2_Flux23/xsec.root) is missing")
        if load("p2.json").get("P2-EQ_derived_vs_default", {}).get("verdict") != "PASS":
            raise SystemExit("REFUSE: P2-EQ did not PASS; the derived line (P2-G2) stops (DESIGN §5)")
    if batch == "B3" and load("g2_s42.json").get("routing") not in ("MATERIAL", "NOT RESOLVED ABOVE TRAINER NOISE"):
        raise SystemExit("REFUSE: seed 42 did not route MATERIAL or NOT RESOLVED; no seed-43 pair")
    if batch in ("B4", "B5", "B6", "B7") and load("p1_unit.json").get("b_eq_1", {}).get("verdict") != "PASS":
        raise SystemExit("REFUSE: the b = 1 control did not PASS; P1 stops")
    if batch == "B8":   # P3 runs last (DESIGN §4): every P1 replica job must already have been submitted
        names = {r["name"] for r in table() if r["batch"] in ("B4", "B5", "B6", "B7")}
        seen = set(attempts(ledger()[2])) | queued()
        if not names <= seen:
            raise SystemExit(f"REFUSE: B8 (P3) runs after B4-B7; {len(names - seen)} P1 jobs not yet submitted")


def simulate(mode):
    """Worked example: batches in order, each launched when the previous has finished (no overlap), costs at the
    measured medians or at the caps. Overlap only moves charge from 'completed' to 'in-flight at cap', which is
    never smaller, so the no-overlap walk is the floor of the gate's totals; the cap walk is also its ceiling."""
    med = {"P0": 836, "P2": 905, "P2def": 2548, "P1unit": 839, "G2on": 1699, "G2off": 905, "P3": 1330, "P1": 839}
    key = lambda r: ("P2def" if r["name"].endswith("MINOS0def") else "P1unit" if r["name"].endswith("unit")
                     else "G2on" if "_on" in r["name"] else "G2off" if "G2_off" in r["name"]
                     else r["item"].replace("-", "").replace("P2G2", "G2on"))
    rows = table()
    order = ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
    spent = 0.0
    print(f"mode={mode}  ceiling={CEILING}")
    for b in order:
        br = [r for r in rows if r["batch"] == b]
        cap = sum(enforced(r) for r in br)
        ok = spent + cap <= CEILING + 1e-12
        cost = cap if mode == "cap" else sum(int(r["billing"]) * med[key(r)] / 256 / 3600 for r in br)
        print(f"  {b}: {len(br):2d} jobs  gate {spent:.4f} + {cap:.4f} = {spent + cap:.4f}  "
              f"{'OK' if ok else 'REFUSE'}  then charged {cost:.4f}")
        if not ok:
            print(f"  first refusal at {b}")
            return
        spent += cost
    print(f"  all batches admitted; total charged {spent:.4f}; unused at the ceiling {CEILING - spent:.4f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["gate", "submit", "simulate"])
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
    for d in ("logs", "results", "retries", "out", "tmp"):
        Path(NS, d).mkdir(parents=True, exist_ok=True)
    done, fly, rows_l = ledger()
    att = attempts(rows_l)
    inq = queued()
    for r in br:
        prior = att.get(r["name"], [])
        if r["name"] in inq:
            raise SystemExit(f"REFUSE: {r['name']} is in the Slurm queue now; no double submission")
        if a.retry:
            if len(prior) != 1 or prior[0] in TERMINAL_RUNNING or prior[0] == "COMPLETED":
                raise SystemExit(f"REFUSE: {r['name']} has attempts {prior}; a retry needs exactly one ended, "
                                 "failed attempt (one retry per job, record §3)")
            if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", a.time):
                raise SystemExit("REFUSE: --time must be HH:MM:SS (scontrol's TimeLimit format)")
            if Path(NS, "retries", f"{r['name']}.time").exists():
                raise SystemExit(f"REFUSE: {r['name']} already has a retry record")
            if any(Path(NS, "out", r["name"]).glob("*")):
                raise SystemExit(f"REFUSE: move out/{r['name']} aside (sha-verified) before the retry")
        elif prior:
            raise SystemExit(f"REFUSE: {r['name']} was already submitted ({prior}); no double submission")
    ok, total = gate(br, a.retry, a.time)
    if not ok:
        print("REFUSE: the batch would exceed the ceiling. Stop and report to the director.")
        return 3
    if a.action == "gate":
        return 0
    preconditions(br[0]["batch"])
    rec = Path(NS, "retries", f"{a.retry}.time") if a.retry else None
    if rec is not None:   # written before sbatch (the job reads it at start), removed if sbatch fails
        rec.write_text(a.time + "\n")
    for r in br:
        cmd = ["sbatch", f"--job-name={r['name']}", f"--qos={r['qos']}", f"--cpus-per-task={r['cpus']}",
               f"--mem={r['mem']}", f"--time={a.time or r['time']}", SBATCH]
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
