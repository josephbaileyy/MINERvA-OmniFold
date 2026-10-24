#!/usr/bin/env python3
"""RE-2 part B charge gate: may this job be submitted without the grant's room being exceeded at its limit?

    re2b_gate.py --jobs partb_jobs.tsv --j0-ledger j0_ledger.tsv --submissions submissions.log \
        --sacct sacct.psv --want J2a [--want J2b ...]

* ``room`` = 90 - J0's charge (the two J0 rows of ``j0_ledger.tsv``).
* Every attempt of a part-B job counts: each ``sacct`` row (``JobID|JobName|State|ElapsedRaw|AllocTRES``) named
  ``re2b-<job>``, and each ``job=<name> id=<slurm id>`` line of ``submissions.log`` not yet in ``sacct``. An ended
  attempt counts its charge (ElapsedRaw x billing / 256); one that has not ended counts its whole cap (its limit on
  one exclusive node). An attempt that never started (empty AllocTRES, ElapsedRaw 0) counts 0.
* A wanted job passes if that sum plus its own cap is at most ``room``. Wanted jobs are taken in order, each
  adding its cap to the sum. A job with any attempt is refused: a resubmission needs a declared amendment.
* For J7 the director's form is also printed: the charge ledgered so far plus J7's projected charge ("j7_form").
  It is implied by the cap form, and J7 is not otherwise held behind the core (RE2-DECLARATION-B.md §3.3).

The cap form is a bound: Slurm stops an exclusive job at its limit, so an attempt's charge cannot exceed its cap
(plus the scheduler's kill delay, seconds). Exit 0 if every wanted job passes, 1 if any is refused. It runs under
the login node's system Python (3.6) as well as the analysis environment.

MEASURES: the grant's room at submission. CANNOT AUTHORIZE: a job (the director's BINDING does).
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

GRANT = 90.0
TERMINAL = {"COMPLETED", "FAILED", "TIMEOUT", "CANCELLED", "OUT_OF_MEMORY", "NODE_FAIL", "DEADLINE", "PREEMPTED",
            "BOOT_FAIL"}


def hours(limit):
    h, m, s = (int(x) for x in limit.split(":"))
    return h + m / 60 + s / 3600


def charge(row):
    """Node-h of an ended attempt. A missing billing with time elapsed is charged as a full node."""
    elapsed = int(row["ElapsedRaw"] or 0)
    m = re.search(r"billing=(\d+)", row["AllocTRES"] or "")
    billing = int(m.group(1)) if m else (256 if elapsed > 0 else 0)
    return elapsed / 3600 * billing / 256


def attempts(jobs, logged, sacct):
    """job name -> list of (slurm id, sacct row or None): every attempt sacct names, plus logged ids it lacks."""
    out = {}
    for jid, row in sacct.items():
        name = row["JobName"][len("re2b-"):] if row["JobName"].startswith("re2b-") else None
        if name in jobs:
            out.setdefault(name, []).append((jid, row))
    for name, jid in logged:
        if name in jobs and jid not in {j for j, _ in out.get(name, [])}:
            out.setdefault(name, []).append((jid, sacct.get(jid)))
    return out


def decide(jobs, j0_charge, logged, sacct, wanted):
    room = GRANT - j0_charge
    used, ledgered, detail = 0.0, 0.0, {}
    tried = attempts(jobs, logged, sacct)
    for name, rows in sorted(tried.items()):
        for jid, row in rows:
            state = row["State"].split()[0] if row else "UNKNOWN"
            if row and state in TERMINAL:
                c = charge(row)
                used += c
                ledgered += c
                detail.setdefault(name, []).append({"id": jid, "state": state, "charged": round(c, 4)})
            else:
                used += jobs[name]["cap"]
                detail.setdefault(name, []).append({"id": jid, "state": state, "reserved": jobs[name]["cap"]})
    out = {"room": round(room, 4), "used_before": round(used, 4), "attempts": detail, "wanted": []}
    for w in wanted:
        if w not in jobs:
            raise SystemExit(w + " is not a partb_jobs.tsv row")
        row = {"job": w, "cap": jobs[w]["cap"]}
        if w in tried:
            row.update(verdict="REFUSE", reason="already submitted ({} attempt(s)); a resubmission needs a declared "
                                                "amendment".format(len(tried[w])))
        elif used + jobs[w]["cap"] > room:
            row.update(verdict="REFUSE", reason="{:.4f} + cap {} > room {:.4f}".format(used, jobs[w]["cap"], room))
        else:
            used += jobs[w]["cap"]
            row.update(verdict="PASS", used_after=round(used, 4))
        if jobs[w]["gated"]:
            row["j7_form"] = {"ledgered": round(ledgered, 4), "projected": jobs[w]["projected"],
                              "ok": ledgered + jobs[w]["projected"] <= room}
        out["wanted"].append(row)
    out["verdict"] = "PASS" if all(r["verdict"] == "PASS" for r in out["wanted"]) else "REFUSE"
    return out


def read_sacct(path):
    rows = {}
    for line in Path(path).read_text().splitlines():
        f = line.split("|")
        if len(f) >= 5 and f[0] and "." not in f[0]:
            rows[f[0]] = {"JobName": f[1], "State": f[2], "ElapsedRaw": f[3], "AllocTRES": f[4]}
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--jobs", type=Path, required=True)
    ap.add_argument("--j0-ledger", type=Path, required=True)
    ap.add_argument("--submissions", type=Path, required=True)
    ap.add_argument("--sacct", type=Path, required=True)
    ap.add_argument("--want", action="append", required=True)
    a = ap.parse_args(argv)
    jobs = {r["job"]: {"cap": float(r["cap_node_h"]), "projected": float(r["projected_node_h"]),
                       "gated": r["gated"] == "yes"} for r in csv.DictReader(open(str(a.jobs)), delimiter="\t")}
    ledger = list(csv.DictReader(open(str(a.j0_ledger)), delimiter="\t"))
    if len(ledger) != 2:
        raise SystemExit("{}: {} rows, expected the two J0 jobs".format(a.j0_ledger, len(ledger)))
    logged = []
    if a.submissions.exists():
        for line in a.submissions.read_text().splitlines():
            m = re.search(r" job=(\S+) id=(\d+)", line)
            if m:
                logged.append((m.group(1), m.group(2)))
    out = decide(jobs, sum(float(r["charge_node_h"]) for r in ledger), logged, read_sacct(a.sacct), a.want)
    print(json.dumps(out, indent=1))
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
