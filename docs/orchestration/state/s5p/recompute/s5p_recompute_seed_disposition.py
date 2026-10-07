"""s5p recompute lane: the disposition of every missing seed, from the submission records (report side, read-only).

The recompute's ``seed_gaps`` report (``s5p_recompute.py``, reviewed at ``0142a228``) infers the submitted batches
from the per-look status files, so a batch refused by the meter after a look that continued is counted as submitted,
and its 200 seeds read as "missing". This script qualifies that report; it is NOT part of the reviewed evaluator or
comparer and feeds no p-value, decision or comparison verdict.

For every seed of every batch that was either admitted by the meter or counted by the recompute, and that has no
finished product, it reads the submission records and assigns one disposition:

* ``not_submitted_no_admission``: the ledger has no ``open`` record for the batch's task table (refused by the
  meter, or never reached);
* ``not_submitted_released``: an ``open`` record whose submission failed (``release``) and no ``job`` record;
* ``submitted_task_no_log``: a job exists, the seed's task left no log, and ``sacct`` shows the task terminal
  (never ran, e.g. cancelled while pending);
* ``submitted_task_not_yet_run``: no log, and ``sacct`` shows the task PENDING or RUNNING (not lost);
* ``submitted_task_no_log_unverified``: no log and no ``sacct`` state for the task (not counted as lost);
* ``submitted_interrupted``: the seed was running when its task was killed (the first unfinished seed of a task
  whose log ends in a Slurm cancellation);
* ``submitted_never_started``: a later seed of such a task;
* ``submitted_failed_rc``: the log records the seed with a nonzero ``rc``;
* ``submitted_finished_no_product``: the log records ``rc`` 0 but no finished product exists (an anomaly);
* ``submitted_unaccounted``: a log exists and none of the above applies (e.g. the task is still running).

Only the dispositions in ``LOST`` describe lost work. Power sets are treated
the same way over their declared tables.

Inputs are read, never written: the design, the frozen task tables of the deploy that submitted the jobs, the meter
ledger, the Slurm task logs, and optionally a saved ``sacct -X -n -P -o JobID,State -j <ids>`` output (``--sacct``;
the jobs are those in the ledger). Output: ``--out`` (JSON) and a summary on stdout.
Exit 0 written; 2 an input is missing or unreadable.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

BATCH = 200
NULL_ORDER = ["MnvTune_v1", "GENIE_2_12_10_CV", "GENIE_2_12_10_MEC", "NuWro_21_09", "GiBUU_2019"]
SEED_RE = re.compile(r"_s(\d+)\.npz$")
OUT_RE = re.compile(r'^\{"out": "[^"]*_s(\d+)\.npz", "rc": (-?\d+)')
HEADER_RE = re.compile(r"^\[s5c\] task=\d+ name=(\S+) job=(\d+)")
CANCEL_RE = re.compile(r"CANCELLED AT \S+( DUE TO (.+?))? \*\*\*")
LOST = ("submitted_task_no_log", "submitted_interrupted", "submitted_never_started", "submitted_failed_rc",
        "submitted_finished_no_product")


def finished_seeds(pattern: str) -> set[int]:
    out = set()
    for p in glob.glob(pattern):
        name = os.path.basename(p)
        m = SEED_RE.search(name)
        if m and ".partial" not in name:
            out.add(int(m.group(1)))
    return out


def partial_seeds(pattern: str) -> set[int]:
    return {int(m.group(1)) for p in glob.glob(pattern)
            if ".partial" in os.path.basename(p) and (m := re.search(r"_s(\d+)\.partial", os.path.basename(p)))}


def read_table(path: str) -> list[tuple[str, list[int]]]:
    """Task rows of a frozen table: (task name, its seeds in order) from ``--pseudo-seeds a:b``."""
    rows = []
    for line in open(path):
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.rstrip("\n").split("\t")
        a, b = cols[cols.index("--pseudo-seeds") + 1].split(":")
        rows.append((cols[0], list(range(int(a), int(b) + 1))))
    return rows


def ledger_batches(ledger: str) -> dict[str, dict]:
    """Per task-table basename: its admissions, job ids and releases."""
    recs = [json.loads(line) for line in open(ledger) if line.strip()]
    by_token = {}
    for r in recs:
        if r.get("kind") == "open":
            table = next((a for a in r.get("argv", []) if a.endswith(".tsv")), None)
            if table:
                by_token[r["token"]] = {"table": os.path.basename(table), "utc": r.get("utc")}
    out: dict[str, dict] = {}
    for tok, info in by_token.items():
        out.setdefault(info["table"], {"admissions": [], "jobs": [], "released": []})["admissions"].append(tok)
    for r in recs:
        tok = r.get("token")
        if tok in by_token:
            rec = out[by_token[tok]["table"]]
            if r.get("kind") == "job":
                rec["jobs"].append(str(r["job_id"]))
            elif r.get("kind") == "release":
                rec["released"].append(tok)
    return out


def sacct_states(path: str | None) -> dict[tuple[str, int], str]:
    """(array job id, task index) -> State, from ``sacct -X -n -P -o JobID,State``; a pending bracket row
    ``J_[a-b,c%t]`` gives every index it names."""
    out: dict[tuple[str, int], str] = {}
    if not path:
        return out
    for line in open(path):
        parts = line.strip().split("|")
        if len(parts) < 2 or "_" not in parts[0]:
            continue
        jid, idx = parts[0].split("_", 1)
        state = parts[1].split()[0] if parts[1] else ""
        if idx.startswith("["):
            for rng in idx.strip("[]").split("%")[0].split(","):
                a, _, b = rng.partition("-")
                for i in range(int(a), int(b or a) + 1):
                    out[(jid, i)] = state
        elif idx.isdigit():
            out[(jid, int(idx))] = state
    return out


def task_logs(logs_dir: str, job_ids: list[str]) -> dict[str, dict]:
    """Per task name: the seeds finished with their rc, and the cancellation line if any (over every job id)."""
    out: dict[str, dict] = {}
    for jid in job_ids:
        for path in sorted(glob.glob(os.path.join(logs_dir, f"*-{jid}_*.out"))):
            name, done, cancel = None, {}, None
            for line in open(path, errors="replace"):
                if name is None and (m := HEADER_RE.match(line)):
                    name = m.group(1)
                elif m := OUT_RE.match(line):
                    done[int(m.group(1))] = int(m.group(2))
                elif "CANCELLED AT" in line and (m := CANCEL_RE.search(line)):
                    cancel = m.group(2) or "cancelled"
            if name is None:
                continue
            rec = out.setdefault(name, {"logs": [], "done": {}, "cancel": None})
            rec["logs"].append(path)
            rec["done"].update(done)
            rec["cancel"] = rec["cancel"] or cancel
    return out


def dispose(table_rows, batch_rec, logs, present: set[int], states=None) -> dict[int, dict]:
    """The disposition of every seed of one batch that has no finished product."""
    out = {}
    states = states or {}
    for task, seeds in table_rows:
        index = int(task.rsplit("_", 1)[1])  # the array index is the task name's suffix (log header task=<i>)
        missing = [s for s in seeds if s not in present]
        if not missing:
            continue
        if not batch_rec or not batch_rec["admissions"]:
            for s in missing:
                out[s] = {"task": task, "disposition": "not_submitted_no_admission"}
            continue
        if not batch_rec["jobs"]:
            kind = "not_submitted_released" if batch_rec["released"] else "not_submitted_no_admission"
            for s in missing:
                out[s] = {"task": task, "disposition": kind, "admissions": batch_rec["admissions"]}
            continue
        lg = logs.get(task)
        if lg is None:
            st = [states[(j, index)] for j in batch_rec["jobs"] if (j, index) in states]
            if not st:
                kind = "submitted_task_no_log_unverified"
            elif any(x in ("PENDING", "RUNNING", "REQUEUED", "SUSPENDED") for x in st):
                kind = "submitted_task_not_yet_run"
            else:
                kind = "submitted_task_no_log"
            for s in missing:
                out[s] = {"task": task, "disposition": kind, "jobs": batch_rec["jobs"], "sacct_states": st}
            continue
        first_unfinished = next((s for s in seeds if s not in lg["done"]), None)
        for s in missing:
            if s in lg["done"]:
                kind = "submitted_failed_rc" if lg["done"][s] != 0 else "submitted_finished_no_product"
            elif lg["cancel"]:
                kind = "submitted_interrupted" if s == first_unfinished else "submitted_never_started"
            else:
                kind = "submitted_unaccounted"
            out[s] = {"task": task, "disposition": kind, "cancel": lg["cancel"], "logs": lg["logs"]}
    return out


def summarize(disp: dict[int, dict]) -> dict:
    counts: dict[str, int] = {}
    for d in disp.values():
        counts[d["disposition"]] = counts.get(d["disposition"], 0) + 1
    return {"counts": dict(sorted(counts.items())),
            "lost_work": sum(v for k, v in counts.items() if k in LOST),
            "not_submitted": sum(v for k, v in counts.items() if k.startswith("not_submitted")),
            "unaccounted": counts.get("submitted_unaccounted", 0)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--design", required=True)
    ap.add_argument("--tables", required=True, help="the frozen task tables of the submitting deploy")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--logs", required=True, help="the Slurm task logs (runs/prod/logs)")
    ap.add_argument("--sacct", help="saved `sacct -X -n -P -o JobID,State -j <ids>` output for the ledger's jobs")
    ap.add_argument("--recompute", help="recompute.json: its seed_gaps are compared with this disposition")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        design = json.load(open(a.design))
        batches = ledger_batches(a.ledger)
        states = sacct_states(a.sacct)
        rec_json = json.load(open(a.recompute)) if a.recompute else None
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    report = {"schema": "s5p-recompute-seed-disposition/1", "not_part_of_reviewed_code": True,
              "inputs": {"design": a.design, "tables": a.tables, "ledger": a.ledger, "logs": a.logs,
                         "recompute": a.recompute, "sacct": a.sacct},
              "lost_work_dispositions": list(LOST), "nulls": {}, "power": {}}
    for key, spec in design["nulls"].items():
        base = 1200000 + 20000 * NULL_ORDER.index(key)
        present = finished_seeds(spec["calibration_glob"])
        gaps = (rec_json or {}).get("nulls", {}).get(key, {}).get("calibration", {}).get("seed_gaps")
        counted = int(gaps["batches_submitted"]) if gaps else 0
        disp, per_batch = {}, {}
        for b in range(-(-int(spec["calibration_n"]["max"]) // BATCH)):
            table = f"cal-{key}-b{b}.tsv"
            brec = batches.get(table)
            if not brec and b >= counted:
                continue
            rows = read_table(os.path.join(a.tables, table))
            logs = task_logs(a.logs, brec["jobs"]) if brec else {}
            d = dispose(rows, brec, logs, present, states)
            per_batch[str(b)] = {"admitted": bool(brec and brec["admissions"]), "jobs": brec["jobs"] if brec else [],
                                 "counted_by_recompute": b < counted, **summarize(d)}
            disp.update(d)
        rec = {"seed_base": base, "products": len(present),
               "partials": sorted(partial_seeds(spec["calibration_glob"])),
               "batches": per_batch, "seeds": {str(s): disp[s] for s in sorted(disp)}, **summarize(disp)}
        if gaps is not None:
            mine = sorted(int(s) for s in gaps["missing_seeds"])
            rec["recompute_missing_seeds_equal"] = mine == sorted(disp)
            rec["recompute_missing_not_disposed"] = sorted(set(mine) - set(disp))
            rec["disposed_not_in_recompute_missing"] = sorted(set(disp) - set(mine))
        report["nulls"][key] = rec
    for sk, spec in design.get("power", {}).items():
        table = f"pow-{sk}.tsv"
        brec = batches.get(table)
        present = finished_seeds(spec["glob"])
        if not brec:
            report["power"][sk] = {"admitted": False, "products": len(present), "n_declared": spec["n"]}
            continue
        d = dispose(read_table(os.path.join(a.tables, table)), brec, task_logs(a.logs, brec["jobs"]), present, states)
        report["power"][sk] = {"admitted": True, "jobs": brec["jobs"], "products": len(present),
                               "n_declared": spec["n"], "seeds": {str(s): d[s] for s in sorted(d)}, **summarize(d)}
    Path(a.out).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    for key, r in report["nulls"].items():
        print(f"{key}: products {r['products']} lost_work {r['lost_work']} not_submitted {r['not_submitted']} "
              f"unaccounted {r['unaccounted']} {r['counts']}")
    for sk, r in report["power"].items():
        print(f"power {sk}: products {r['products']} " + (f"lost_work {r['lost_work']} {r['counts']}"
                                                          if r.get("admitted") else "not admitted"))
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
