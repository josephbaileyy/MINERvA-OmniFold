#!/usr/bin/env python3
"""Admission accounting: charged spend PLUS the maximum remaining exposure of admitted tasks.

Joseph's requirement, verbatim: *"implement or reuse admission accounting that bounds charged
expenditure plus the maximum remaining exposure of admitted tasks, including queued jobs and
retries. Do not rely on elapsed-so-far checks alone. Preserve R5's rule for jobs already running
at the stop."*

`r5_meter.py` IS REUSED, NOT REIMPLEMENTED. A rule retyped is a second implementation and this
repository has already paid for that; the charged half of every number below comes from
`r5_meter`'s own parser and its own receipt validator. What is added here is the half the meter
structurally cannot supply.

WHAT THE METER ALREADY DOES, re-measured rather than assumed:
  * IT CHARGES RUNNING ATTEMPTS. A RUNNING row carries a `Start`, and `_parse_sacct_start` skips a
    row only on that field. Measured: one COMPLETED 3600 s + one RUNNING 7200 s + one PENDING gives
    `cpu_task_hours == 3.0` and `attempt_count == 2`. So the cap cannot be overshot by an
    UNCOUNTED in-flight population, and this module does not pretend otherwise.
  * IT CHARGES EVERY ATTEMPT. Measured on the live window: 1893 attempts across 10 task ids, of
    which 1882 are REQUEUED. Retries are not a hypothetical term here, they are almost the whole
    population -- which is exactly why `--max-retries` below has NO DEFAULT.

THE TWO THINGS IT STRUCTURALLY CANNOT SUPPLY, and they are the reason this module exists:

  1. COMMITTED, NOT ELAPSED. The meter charges elapsed-so-far. At `--array=0-39%40` with
     `--time=06:00:00` up to 240 CPU task-hours are committed-but-unmetered in flight. R5
     CONTEMPLATES this -- *"jobs running at the stop run to completion, spend counted"* -- so it is
     the ruling's design and not a meter defect, and it is PRESERVED: nothing here cancels a
     running job. What changes is that a NEW admission is priced against the committed maximum.

  2. QUEUED JOBS ARE INVISIBLE TO IT. `_parse_sacct_dump` skips any row whose `Start` is `Unknown`,
     so a PENDING task is not an `AttemptRecord` at all -- measured in the same fixture above. The
     admitted population therefore CANNOT be derived from the meter and MUST be declared. The
     undeclared-arm guard below is necessary and NOT sufficient for that reason, and saying so is
     part of the interface.

THE SPEND BASIS IS DECLARED, NEVER INFERRED, AND THIS IS MEASURED. `r5_meter._sacct_argv` emits a
NAIVE `--starttime` via `strftime`, and every Perlmutter login node defaults to PDT (`date +%Z` =
PDT on login40, re-measured). I measured the effect directly, back to back on one login node:

    TZ=UTC sacct ... --starttime 2026-09-02T13:44:27 ...  ->  1894 rows
          sacct ... --starttime 2026-09-02T13:44:27 ...  ->  1832 rows

`sacct` honours `TZ` when it parses a naive `--starttime`, so the naive window starts 7 h late and
is 62 rows narrower. TWO CONSEQUENCES, and they point opposite ways:

  * `_read_source:552-557` DOES set `TZ=UTC` in the child environment, so the meter's LIVE `sacct`
    path already reads the UTC basis. "The meter's window starts 7 h late" is FALSE of that path.
  * BUT THE RECEIPT CANNOT PROVE IT. `source.argv_or_path` records `shlex.join(argv)`, which does
    not contain the `TZ` assignment, and the `--from-file` path records only a file path -- I
    measured a real receipt whose entire basis provenance is `kind: "file"`. So a receipt's own
    fields cannot establish which basis produced it, and a hand-captured dump is silently the
    narrow one.

Hence `--spend-basis` is REQUIRED with no default and `naive`/`unknown` REFUSE. That adopts no
number: the 0.4858 task-hour under-read is not encoded anywhere here, because encoding it would be
adopting a threshold and would also be wrong the moment the offset changes. Fixing the meter's
timezone is routed to the meter's owner and is deliberately not done here.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = str(Path(__file__).resolve().parents[1])
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding", f"{_REPO}/docs/orchestration"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import r5_meter                     # noqa: E402  the charged half, REUSED
import z_precursor                  # noqa: E402  the arm declarations, DERIVED from #SBATCH

require = z_precursor.require
PrecursorError = z_precursor.PrecursorError

#: Basis values. Only `utc` proceeds. `unknown` exists so a caller can say so rather than guess,
#: and it refuses -- a check that could not establish its operand is not a check that passed.
SPEND_BASES = ("utc", "naive", "unknown")

#: Slurm states from which NO further attempt of that TASK can follow. Everything else is treated
#: as non-terminal, so an unrecognised state fails closed towards having exposure.
#:
#: ⚠ LIVENESS IS A PROPERTY OF THE TASK, NOT OF AN ATTEMPT, AND THE FIRST VERSION OF THIS GUARD GOT
#: IT WRONG IN THE DIRECTION THAT REFUSES EVERYTHING. `REQUEUED` is non-terminal as an ATTEMPT
#: state -- the attempt ended but the task continues and will burn another wall ceiling -- so I
#: classified any task with a REQUEUED attempt as live. Run against the real accounting window that
#: refused immediately: task `57712764` carries 1885 attempts, 1882 of them REQUEUED, and its
#: FINAL row is `CANCELLED`. The task is finished and has zero remaining exposure, but 1882
#: historical requeues read as live exposure and the guard fired on a correct state. A guard that
#: fires on every correct run is not a guard.
#:
#: So the test is: a task is LIVE iff the dump contains NO terminal row for it. That question is
#: asked of the RAW rows rather than of the meter's attempts, and deliberately -- the terminal row
#: here has `Start` `None`, so `r5_meter._parse_sacct_start` drops it and the meter's attempt set
#: cannot see the very row that settles liveness. The meter stays the sole authority for CHARGED
#: HOURS; only state PRESENCE is read from the raw text.
TERMINAL_STATES = frozenset({"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY",
                             "NODE_FAIL", "BOOT_FAIL", "DEADLINE", "PREEMPTED", "REVOKED",
                             "SPECIAL_EXIT"})


def committed_task_hours(arm, max_retries):
    """The MAXIMUM an arm can ever charge: every task, every allowed attempt, at the wall ceiling.

    ``n_tasks * (1 + max_retries) * time_limit_hours``. The throttle (`%40`) does NOT appear: it
    bounds CONCURRENCY, not total spend, and a throttled array charges exactly as much in the end.
    Reading `%40` as a population is the `sacct` bracket error one level up.
    """
    require(max_retries >= 0, f"max_retries must be >= 0, got {max_retries}")
    return arm["n_tasks"] * (1 + int(max_retries)) * arm["time_limit_hours"]


def _row_task_id(job_id):
    """The task id a raw `JobID` belongs to, ignoring step and bracket suffixes.

    Deliberately permissive: this is used only to GROUP rows for the liveness question, never to
    decide what is charged. A row this misgroups would at worst make a task look live.
    """
    return job_id.split(".", 1)[0]


def _live_tasks(raw_text):
    """Task ids with NO terminal row in the dump, and the job name each id was seen under.

    Read from the RAW rows, not from `r5_meter`'s attempts, because the row that settles liveness
    can be one the meter drops: the measured case is a `CANCELLED` row whose `Start` is `None`.
    See `TERMINAL_STATES` for the incident.
    """
    seen_name = {}
    terminal = set()
    all_ids = set()
    for line in raw_text.splitlines():
        fields = line.split("|")
        if len(fields) != len(r5_meter.SACCT_FIELDS):
            continue
        job_id, name, state = fields[0], fields[1], fields[2]
        task = _row_task_id(job_id)
        all_ids.add(task)
        seen_name.setdefault(task, name)
        # Slurm decorates some states, e.g. `CANCELLED by 12345`. Compare on the first token.
        tokens = state.split()
        if tokens and tokens[0].upper() in TERMINAL_STATES:
            terminal.add(task)
    live = {task: seen_name.get(task, "") for task in sorted(all_ids - terminal)}
    return live, seen_name


def _charged_by_name(raw_text):
    """Per-`JobName` charged task-hours, plus the LIVE task ids grouped by name.

    The meter's `AttemptRecord` deliberately drops `JobName`, so the name has to come from the
    rows. The ATTEMPT SET does not: it is `r5_meter._parse_sacct_dump`'s, so a row the meter
    excluded -- a step row, an array bracket, a pre-t0 attempt, a duplicate observation -- is
    excluded here too. Re-splitting the text for names while re-deriving the attempt set would be
    a second implementation of the meter's exclusion rules, and the two would disagree.
    """
    attempts = r5_meter._parse_sacct_dump(raw_text)
    live, seen_name = _live_tasks(raw_text)
    per_name = {}
    for (task_id, _start), record in attempts.items():
        name = seen_name.get(task_id) or seen_name.get(_row_task_id(task_id), "")
        bucket = per_name.setdefault(name, {"cpu_task_hours": 0.0, "gpu_task_hours": 0.0,
                                            "attempts": 0, "states": {}})
        if record.counted:
            key = "gpu_task_hours" if record.is_gpu else "cpu_task_hours"
            bucket[key] += record.elapsed_seconds / 3600.0
            bucket["attempts"] += 1
        bucket["states"][record.state] = bucket["states"].get(record.state, 0) + 1
    live_by_name = {}
    for task_id, name in live.items():
        live_by_name.setdefault(name, []).append(task_id)
    return per_name, live_by_name


def admission_report(*, raw_text, admitted, proposed, max_retries, spend_basis, now,
                     receipt=None):
    """Decide whether one more arm may be admitted, bounding committed exposure.

    Parameters
    ----------
    raw_text : str
        The `sacct` dump the charged half is measured from, in `r5_meter.SACCT_FIELDS` order.
    admitted : sequence of dict
        `z_precursor.parse_sbatch_arm` results for every arm ALREADY admitted -- queued or running.
    proposed : sequence of dict
        Same shape, for the arm(s) being asked about. May be empty, which asks whether the
        already-admitted set alone is within the cap.
    max_retries : int
        Allowed requeues per task. NO DEFAULT at the CLI: a default of 0 would price a
        requeue-prone arm at zero remaining exposure, and 1882 of 1893 measured attempts are
        requeues.
    spend_basis : str
        One of `SPEND_BASES`. Only `utc` proceeds; see this module's docstring for the measurement.
    now : datetime
        Timezone-aware decision instant, passed through to `r5_meter`.

    Returns
    -------
    dict
        The full decision, including every term, so a reader can re-add them.
    """
    require(spend_basis in SPEND_BASES,
            f"spend_basis must be one of {SPEND_BASES}, got {spend_basis!r}")
    if spend_basis != "utc":
        raise PrecursorError(
            f"spend_basis={spend_basis!r}: REFUSED. The charged half must be measured on an "
            f"explicitly UTC window. Measured on login40, back to back: `TZ=UTC sacct "
            f"--starttime 2026-09-02T13:44:27` returns 1894 rows and the same call without TZ "
            f"returns 1832 -- the naive window starts 7 h late because the login default is PDT, "
            f"so it under-reads spend. The meter's LIVE path sets TZ=UTC in the child and is "
            f"safe, but its receipt does not record that, so the basis cannot be inferred and is "
            f"declared instead. No margin is added for the naive case: adopting a number here "
            f"would be adopting a threshold, and it would be the wrong number the moment the "
            f"offset changes.")

    meter_receipt = r5_meter.build_receipt(raw_text, now=now, source_kind="file",
                                           source_location="<admission accounting input>")
    charged_cpu = float(meter_receipt["spend"]["cpu_task_hours"])
    charged_gpu = float(meter_receipt["spend"]["gpu_task_hours"])
    per_name, live_by_name = _charged_by_name(raw_text)

    admitted = list(admitted)
    proposed = list(proposed)
    declared_names = {a["job_name"] for a in admitted} | {p["job_name"] for p in proposed}

    # BOTH DIRECTIONS. A DECLARED arm with no rows yet is fine and expected -- a queued array has
    # not started. An OBSERVED non-terminal arm that was never declared is a refusal: its wall
    # ceiling is unknown here, so its remaining exposure is UNBOUNDED and no bound can be stated.
    undeclared = sorted(n for n in live_by_name if n and n not in declared_names)
    if undeclared:
        raise PrecursorError(
            f"REFUSED: {len(undeclared)} job name(s) have non-terminal attempts but were not "
            f"declared as admitted: {undeclared[:10]}. Their `--time` ceilings are not knowable "
            f"from this dump, so their remaining exposure is unbounded and the total cannot be "
            f"bounded at all. NOTE this guard is necessary and NOT sufficient: "
            f"r5_meter._parse_sacct_dump drops rows whose Start is Unknown, so a PENDING task is "
            f"invisible to it and a wholly-queued undeclared arm would not appear here. That is "
            f"why the admitted set is DECLARED rather than derived.")

    def exposure(arms, label):
        rows = []
        for arm in arms:
            committed = committed_task_hours(arm, max_retries)
            already = float((per_name.get(arm["job_name"]) or {}).get("cpu_task_hours", 0.0))
            remaining = max(0.0, committed - already)
            rows.append({
                "role": label, "job_name": arm["job_name"], "launcher": arm["launcher"],
                "n_tasks": arm["n_tasks"], "throttle": arm["throttle"],
                "time_limit_hours": arm["time_limit_hours"], "max_retries": int(max_retries),
                "committed_max_cpu_task_hours": committed,
                "already_charged_cpu_task_hours": already,
                "remaining_exposure_cpu_task_hours": remaining,
                "live_task_ids_observed": sorted(live_by_name.get(arm["job_name"], [])),
            })
        return rows

    admitted_rows = exposure(admitted, "admitted")
    proposed_rows = exposure(proposed, "proposed")
    admitted_exposure = sum(r["remaining_exposure_cpu_task_hours"] for r in admitted_rows)
    proposed_exposure = sum(r["remaining_exposure_cpu_task_hours"] for r in proposed_rows)

    # THE BOUND. `charged_cpu` already contains each arm's own charged hours, and each arm's
    # remaining exposure is `committed - already`, so the sum is
    # (spend outside these arms) + (every declared arm at its FULL committed maximum).
    # No term is counted twice, and every admitted task is priced at its ceiling rather than at
    # what it has burned so far.
    bound = charged_cpu + admitted_exposure + proposed_exposure
    ceiling = r5_meter.CPU_TASK_HOURS_CEILING
    fired = meter_receipt["fired"]

    if fired["any"]:
        decision, code = "REFUSED_STOP_FIRED", 3
    elif bound >= ceiling:
        decision, code = "REFUSED_BOUND_EXCEEDS_CEILING", 5
    else:
        decision, code = "PERMITTED", 0

    return {
        "decision": decision,
        "exit_code": code,
        "spend_basis": spend_basis,
        "ceilings": {"cpu_task_hours": ceiling,
                     "gpu_task_hours": r5_meter.GPU_TASK_HOURS_CEILING},
        "charged": {"cpu_task_hours": charged_cpu, "gpu_task_hours": charged_gpu,
                    "attempt_count": meter_receipt["spend"]["attempt_count"],
                    "task_count": meter_receipt["spend"]["task_count"],
                    "by_state": meter_receipt["spend"]["by_state"]},
        "admitted": admitted_rows,
        "proposed": proposed_rows,
        "admitted_remaining_exposure_cpu_task_hours": admitted_exposure,
        "proposed_remaining_exposure_cpu_task_hours": proposed_exposure,
        "bound_cpu_task_hours": bound,
        "headroom_after_bound_cpu_task_hours": ceiling - bound,
        "r5_fired": fired,
        # R5'S RULE, PRESERVED AND STATED IN THE OUTPUT. This module never recommends cancelling a
        # running job: a job running at the stop runs to completion and its spend is counted. The
        # only thing it refuses is a NEW admission. Recording the policy in the artifact means a
        # consumer cannot read a refusal as an instruction to kill anything.
        "running_at_stop_policy": ("R5: jobs already running at the stop RUN TO COMPLETION and "
                                   "their spend is counted. This accounting refuses new "
                                   "ADMISSION only; it never cancels an admitted task."),
        "meter_reuse": {"module": "docs/orchestration/r5_meter.py",
                        "unit": meter_receipt["unit"],
                        "t0_utc": meter_receipt["t0_utc"]},
        "limits": [
            "queued (PENDING) tasks are invisible to r5_meter._parse_sacct_dump, so the admitted "
            "set is DECLARED, not derived; the undeclared-arm guard cannot see a wholly-queued arm",
            "exposure is bounded per ARM from its #SBATCH --time and --array; a launcher edited "
            "after submission would make the declaration describe a different arm",
        ],
        "receipt": receipt,
    }


def _build_parser():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sacct-dump", type=Path, required=True,
                        help="captured sacct dump in r5_meter.SACCT_FIELDS order")
    parser.add_argument("--spend-basis", required=True, choices=SPEND_BASES,
                        help="REQUIRED, no default. Only 'utc' proceeds; see the module docstring "
                             "for the 1894-vs-1832-row measurement behind that.")
    parser.add_argument("--admitted-launcher", action="append", default=[],
                        help="launcher PATH of an already-admitted arm (repeatable)")
    parser.add_argument("--proposed-launcher", action="append", default=[],
                        help="launcher PATH of an arm being proposed (repeatable)")
    parser.add_argument("--max-retries", type=int, required=True,
                        help="REQUIRED, no default: 1882 of 1893 measured attempts are requeues, "
                             "so a defaulted 0 would price the dominant term at nothing")
    parser.add_argument("--now", type=r5_meter.parse_iso_utc, required=True)
    parser.add_argument("--json", action="store_true", help="emit the full decision as JSON")
    return parser


def main(argv=None):
    args = _build_parser().parse_args(argv)
    try:
        raw = args.sacct_dump.read_text(encoding="utf-8")
        report = admission_report(
            raw_text=raw,
            admitted=[z_precursor.parse_sbatch_arm(p) for p in args.admitted_launcher],
            proposed=[z_precursor.parse_sbatch_arm(p) for p in args.proposed_launcher],
            max_retries=args.max_retries, spend_basis=args.spend_basis, now=args.now)
    except (PrecursorError, r5_meter.MeterError) as exc:
        print(f"[admission] FAIL: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"[admission] FAIL: cannot read the dump: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"[admission] {report['decision']}: charged "
              f"{report['charged']['cpu_task_hours']:.4f} + admitted exposure "
              f"{report['admitted_remaining_exposure_cpu_task_hours']:.4f} + proposed "
              f"{report['proposed_remaining_exposure_cpu_task_hours']:.4f} = bound "
              f"{report['bound_cpu_task_hours']:.4f} CPU task-h against ceiling "
              f"{report['ceilings']['cpu_task_hours']:.1f}")
        print(f"[admission] {report['running_at_stop_policy']}")
    return int(report["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
