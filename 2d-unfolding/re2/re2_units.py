#!/usr/bin/env python3
"""RE-2 J0 readout: the measured refined units, and the production projection with the rule fixed in advance.

    sacct -j J0A,J0B -n -P -o JobID,JobName,ElapsedRaw,AllocCPUS,State > steps.psv
    re2_ledger.sh J0A J0B > j0_ledger.tsv
    re2_units.py --runs j0_runs.tsv --steps steps.psv --ledger j0_ledger.tsv --result units.json

A run's node-h is its srun step's ElapsedRaw x AllocCPUS / 256 / 3600: its share of the exclusive node. The
refined unit of each production class is the MAXIMUM over the J0 runs of that class, not the mean, so the
projection is conservative where J0 has few runs. Production counts are those of RE2-PLAN §4.2 (J1-J8).

The rule (RE2-DECLARATION.md §5.3, fixed before J0). J0 is booked inside the same 90 node-h, so what is left
for part B is ``room = 90 - J0's charge`` (the jobs' ``charge_node_h`` from ``re2_ledger.sh``):
* ``core_worst`` = 1.25 x the projected core (J1, J2, J3, J4, J6, J8).
* core_worst <= room: part B may be declared within the grant. Then J7 (S4(ii), a genuinely omitted term,
  RE2-PLAN R10) is added if it still fits, and then J5 (S2, already inside S1) only if J7 was added and J5
  fits too.
* core_worst > room: production does not start; the projection goes back to the director (a fresh binding,
  RE2-PLAN-RULINGS item 2).
* any J0 step not COMPLETED, or any class unmeasured: INCOMPLETE; production does not start.

MEASURES: J0's unit times. CANNOT AUTHORIZE: a production job.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

GRANT = 90.0
FACTOR = 1.25
# production class -> (J0 labels that measure it, count in production, job)
CLASSES = {
    "central": (["D_cv"], 3, "J1"),
    "universe": (["F_MaCCQE0", "F_Flux23", "F_MaRES0", "F_NormDISCC0"], 175, "J2"),
    "lateral": (["FL_BAX0", "FL_BAX0_rep"], 10, "J3"),
    "replica": ([f"RB_{i:03d}" for i in range(1, 9)] + ["RB_001_rep", "D_unit"], 300, "J4"),
    "replica_seed": ([f"RB_{i:03d}" for i in range(1, 9)], 80, "J6"),
    "period": (["RF_PA", "RPR_PA_b01"], 37, "J8"),
    "bkg_only": ([f"RB_{i:03d}" for i in range(1, 9)], 100, "J5"),
    "seed_panel": (["F_MaCCQE0", "F_Flux23", "F_MaRES0", "F_NormDISCC0"], 39, "J7"),
}
CORE = ("J1", "J2", "J3", "J4", "J6", "J8")
DIAG_ORDER = ("J7", "J5")      # J7 first (R10)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--steps", type=Path, required=True)
    ap.add_argument("--ledger", type=Path, required=True, help="re2_ledger.sh output for the J0 jobs")
    ap.add_argument("--result", type=Path, required=True)
    a = ap.parse_args(argv)
    runs = {r["label"]: r for r in csv.DictReader(open(a.runs), delimiter="\t")}
    steps = {}
    for line in open(a.steps):
        f = line.rstrip("\n").split("|")
        if len(f) < 5 or f[1] not in runs:
            continue
        if f[1] in steps:
            raise RuntimeError(f"two steps named {f[1]}")
        steps[f[1]] = {"jobid": f[0], "elapsed_s": int(f[2]), "cpus": int(f[3]), "state": f[4]}
    missing = sorted(set(runs) - set(steps))
    not_completed = sorted(k for k, v in steps.items() if v["state"] != "COMPLETED")
    ledger = list(csv.DictReader(open(a.ledger), delimiter="\t"))
    if len(ledger) != 2:  # exactly the two J0 jobs; an empty ledger must never read as a charge of 0
        raise RuntimeError(f"{a.ledger}: {len(ledger)} job rows, expected the two J0 jobs")
    j0_charge = sum(float(r["charge_node_h"]) for r in ledger)
    per_run = {k: dict(v, node_h=v["elapsed_s"] * v["cpus"] / 256 / 3600) for k, v in steps.items()}
    out = {"schema": "re2-j0-units/2", "runs": per_run, "missing_steps": missing, "not_completed": not_completed,
           "j0_charge_node_h": j0_charge, "room_node_h": GRANT - j0_charge, "classes": {}, "jobs": {}}
    for name, (labels, count, job) in CLASSES.items():
        got = [per_run[l]["node_h"] for l in labels if l in per_run]
        if not got:
            out["classes"][name] = {"unit_node_h": None, "count": count, "job": job}
            continue
        unit = max(got)
        out["classes"][name] = {"unit_node_h": unit, "n_measured": len(got), "count": count, "job": job,
                                "projected_node_h": unit * count}
        out["jobs"][job] = out["jobs"].get(job, 0.0) + unit * count
    room = GRANT - j0_charge
    if any(out["classes"][c]["unit_node_h"] is None for c in out["classes"]) or missing or not_completed:
        out["verdict"] = "INCOMPLETE: a step was not measured or not COMPLETED; production does not start"
    else:
        core = sum(out["jobs"][j] for j in CORE)
        out.update(core_projected=core, core_worst=FACTOR * core)
        if FACTOR * core > room:
            out["verdict"] = "RETURN TO DIRECTOR: core worst case exceeds the grant left after J0"
        else:
            total, included = core, []
            for j in DIAG_ORDER:  # J7, then J5 only if J7 is in (R10)
                if FACTOR * (total + out["jobs"][j]) > room:
                    break
                total += out["jobs"][j]
                included.append(j)
            out.update(included_diagnostics=included, total_projected=total, total_worst=FACTOR * total)
            out["verdict"] = "WITHIN GRANT: core" + "".join(f" + {j}" for j in included)
    a.result.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out.get(k) for k in ("verdict", "room_node_h", "core_projected", "core_worst",
                                                "included_diagnostics")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
