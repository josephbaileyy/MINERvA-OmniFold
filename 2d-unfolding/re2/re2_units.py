#!/usr/bin/env python3
"""RE-2 J0 readout: the measured refined units, and the production projection with the rule fixed in advance.

    sacct -j J0A,J0B -n -P -o JobID,JobName,ElapsedRaw,AllocCPUS,State > steps.psv
    re2_units.py --runs j0_runs.tsv --steps steps.psv --result units.json

A run's node-h is its srun step's ElapsedRaw x AllocCPUS / 256 / 3600: its share of the exclusive node. The
refined unit of each production class is the MAXIMUM over the J0 runs of that class, not the mean, so the
projection is conservative where J0 has few runs. Production counts are those of RE2-PLAN §4.2 (J1-J8).

The rule (RE2-DECLARATION.md §5, fixed before J0):
* ``core_worst`` = 1.25 x the projected core (J1, J2, J3, J4, J6, J8); ``diag_worst`` adds J5 and J7.
* core_worst <= 90: part B may be declared within the 90 node-h grant. The diagnostics are included only if
  diag_worst <= 90.
* core_worst > 90: production does not start; the projection goes back to the director (a fresh binding,
  RE2-PLAN-RULINGS item 2).

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
    "period": (["RF_PA"], 37, "J8"),
    "bkg_only": ([f"RB_{i:03d}" for i in range(1, 9)], 100, "J5"),
    "seed_panel": (["F_MaCCQE0", "F_Flux23", "F_MaRES0", "F_NormDISCC0"], 39, "J7"),
}
CORE = ("J1", "J2", "J3", "J4", "J6", "J8")
DIAG = ("J5", "J7")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--steps", type=Path, required=True)
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
    per_run = {k: dict(v, node_h=v["elapsed_s"] * v["cpus"] / 256 / 3600) for k, v in steps.items()}
    out = {"schema": "re2-j0-units/1", "runs": per_run, "missing_steps": missing, "classes": {}, "jobs": {}}
    for name, (labels, count, job) in CLASSES.items():
        got = [per_run[l]["node_h"] for l in labels if l in per_run and per_run[l]["state"] == "COMPLETED"]
        if not got:
            out["classes"][name] = {"unit_node_h": None, "count": count, "job": job}
            continue
        unit = max(got)
        out["classes"][name] = {"unit_node_h": unit, "n_measured": len(got), "count": count, "job": job,
                                "projected_node_h": unit * count}
        out["jobs"][job] = out["jobs"].get(job, 0.0) + unit * count
    if any(out["classes"][c]["unit_node_h"] is None for c in out["classes"]) or missing:
        out["verdict"] = "INCOMPLETE: a class or step was not measured; production does not start"
    else:
        core = sum(out["jobs"][j] for j in CORE)
        diag = core + sum(out["jobs"][j] for j in DIAG)
        out.update(core_projected=core, core_worst=FACTOR * core, diag_projected=diag, diag_worst=FACTOR * diag)
        if FACTOR * core > GRANT:
            out["verdict"] = "RETURN TO DIRECTOR: core worst case exceeds the 90 node-h grant"
        elif FACTOR * diag > GRANT:
            out["verdict"] = "CORE ONLY within 90; diagnostics J5/J7 excluded"
        else:
            out["verdict"] = "CORE AND DIAGNOSTICS within 90"
    a.result.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out.get(k) for k in ("verdict", "core_projected", "core_worst", "diag_worst")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
