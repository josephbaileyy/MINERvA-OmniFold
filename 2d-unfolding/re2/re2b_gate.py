#!/usr/bin/env python3
"""RE-2 part B charge gate: may this job be submitted without the grant's room being exceeded at its limit?

    re2b_gate.py --jobs partb_jobs.tsv --j0-ledger j0_ledger.tsv --submissions submissions.log \
        --sacct sacct.psv --want J2a [--want J2b ...]

* ``room`` = 90 - J0's charge (the two J0 rows of ``j0_ledger.tsv``).
* Each part-B job already submitted (a ``job=<name> id=<slurm id>`` line of ``submissions.log``) counts its
  charge from ``sacct`` (``JobID|State|ElapsedRaw|AllocTRES``, billing / 256 node) if it has ended, and its whole
  cap (its limit on one exclusive node) if it has not. A submitted job missing from ``sacct`` counts its cap.
* A wanted job passes if that sum plus its own cap is at most ``room``. Wanted jobs are taken in order, each
  adding its cap to the sum. A job already submitted is refused.
* For the gated diagnostic (J7), the director's form is also printed: the charge ledgered so far plus J7's
  projected charge (RE2-DECLARATION-B.md §3.3). It is implied by the cap form.

The cap form is a bound: Slurm stops an exclusive job at its limit, so a job's charge cannot exceed its cap
(plus the scheduler's kill delay, seconds). Exit 0 if every wanted job passes, 1 if any is refused.

MEASURES: the grant's room at submission. CANNOT AUTHORIZE: a job (the director's BINDING does).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

GRANT = 90.0
TERMINAL = {"COMPLETED", "FAILED", "TIMEOUT", "CANCELLED", "OUT_OF_MEMORY", "NODE_FAIL", "DEADLINE", "PREEMPTED",
            "BOOT_FAIL"}


def hours(limit: str) -> float:
    h, m, s = (int(x) for x in limit.split(":"))
    return h + m / 60 + s / 3600


def charge(row: dict) -> float:
    billing = int(re.search(r"billing=(\d+)", row["AllocTRES"]).group(1))
    return int(row["ElapsedRaw"]) / 3600 * billing / 256


def decide(jobs: dict, j0_charge: float, submitted: dict, sacct: dict, wanted: list[str]) -> dict:
    room = GRANT - j0_charge
    used, ledgered, detail = 0.0, 0.0, {}
    for name, jid in submitted.items():
        row = sacct.get(jid)
        state = row["State"].split()[0] if row else "UNKNOWN"
        if row and state in TERMINAL:
            c = charge(row)
            used += c
            ledgered += c
            detail[name] = {"id": jid, "state": state, "charged": round(c, 4)}
        else:
            used += jobs[name]["cap"]
            detail[name] = {"id": jid, "state": state, "reserved": jobs[name]["cap"]}
    out = {"room": round(room, 4), "used_before": round(used, 4), "submitted": detail, "wanted": []}
    for w in wanted:
        if w not in jobs:
            raise SystemExit(f"{w} is not a partb_jobs.tsv row")
        row = {"job": w, "cap": jobs[w]["cap"]}
        if w in submitted:
            row.update(verdict="REFUSE", reason="already submitted")
        elif used + jobs[w]["cap"] > room:
            row.update(verdict="REFUSE", reason=f"{used:.4f} + cap {jobs[w]['cap']} > room {room:.4f}")
        else:
            used += jobs[w]["cap"]
            row.update(verdict="PASS", used_after=round(used, 4))
        if jobs[w]["gated"]:
            row["director_form"] = {"ledgered": round(ledgered, 4), "projected": jobs[w]["projected"],
                                    "ok": ledgered + jobs[w]["projected"] <= room}
        out["wanted"].append(row)
    out["verdict"] = "PASS" if all(r["verdict"] == "PASS" for r in out["wanted"]) else "REFUSE"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--jobs", type=Path, required=True)
    ap.add_argument("--j0-ledger", type=Path, required=True)
    ap.add_argument("--submissions", type=Path, required=True)
    ap.add_argument("--sacct", type=Path, required=True)
    ap.add_argument("--want", action="append", required=True)
    a = ap.parse_args(argv)
    jobs = {r["job"]: {"cap": float(r["cap_node_h"]), "projected": float(r["projected_node_h"]),
                       "gated": r["gated"] == "yes"} for r in csv.DictReader(open(a.jobs), delimiter="\t")}
    ledger = list(csv.DictReader(open(a.j0_ledger), delimiter="\t"))
    if len(ledger) != 2:
        raise SystemExit(f"{a.j0_ledger}: {len(ledger)} rows, expected the two J0 jobs")
    submitted = {}
    if a.submissions.exists():
        for line in a.submissions.read_text().splitlines():
            m = re.search(r" job=(\S+) id=(\d+)", line)
            if m:
                submitted[m.group(1)] = m.group(2)
    sacct = {}
    for line in a.sacct.read_text().splitlines():
        f = line.split("|")
        if len(f) >= 4 and "." not in f[0]:
            sacct[f[0]] = {"State": f[1], "ElapsedRaw": f[2], "AllocTRES": f[3]}
    out = decide(jobs, sum(float(r["charge_node_h"]) for r in ledger), submitted, sacct, a.want)
    print(json.dumps(out, indent=1))
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
