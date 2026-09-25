#!/usr/bin/env python3
"""Admission and accounting for the scalar-5D campaign activated 2026-09-24 ("s5c").

Authority: ``docs/orchestration/AUTHORIZATION-20260924-scalar5d-campaign-activation.md``
§3 rows S1-S2 (Joseph's D2).  For this campaign only, ``r5_meter.py`` is displaced by
this meter; ``r5_meter.py`` itself and every guard that calls it are untouched.

UNITS ARE NATIVE BILLED UNITS, NOT TASK-HOURS.

* CPU pool (account ``m3246``): billed CPU node-hours
  ``= ElapsedRaw/3600 * billing/256 * qos_factor`` per execution attempt.
* GPU pool (account ``m3246_g``): billed GPU node-hours
  ``= ElapsedRaw/3600 * billing/128 * qos_factor``; the campaign ceiling is stated in
  A100-equivalent GPU-hours ``= 4 * GPU node-hours``.

``billing`` is read from ``AllocTRES``.  The whole-node denominators are the nodes'
``CfgTRES`` billing, measured 2026-09-25 with ``scontrol show node``: a CPU node
(``regular_milan_ss11``, 256 hardware threads) bills 256, a GPU node (``gpu_ss11``,
4 x A100, 128 threads) bills 128.  The QOS factor table assumes no discount and
``premium``/``overrun`` are refused outright.

ADMISSION IS A RESERVATION OF THE MAXIMUM BILLABLE COST.  A submission reserves
``ntasks * timelimit_h * billing/128 * qos_factor`` in its pool.  Until the job's every
task is terminal in ``sacct`` its charge is ``max(reservation, measured)``; afterwards it
is the measured value (reconciliation).  A submission is admitted only if, after adding
its reservation, both its STAGE allocation and the campaign TOTAL in that pool hold, and
the concurrency limits (2 CPU nodes, 4 GPUs) hold over every open admission.

WHAT FAILS CLOSED.  A ledger line that does not parse; a budget file whose sha256 differs
from the one the ledger was opened with; an ``s5c-`` job in ``sacct`` that the ledger
never admitted (``measure`` refuses, because an unregistered job is unmetered spend);
a submission whose sbatch arguments try to override the job name, requeue policy,
account, QOS, time limit or array throttle the meter priced.

Exit codes: 0 admitted/ok, 3 refused by a cap, 4 refused by concurrency, 5 ledger or
budget integrity failure, 6 unregistered campaign job found, 7 sbatch failed (the
reservation is released), 2 usage error.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

CAMPAIGN_KEY = "s5c-20260924"
JOB_PREFIX = "s5c-"
WHOLE_NODE_BILLING = {"cpu": 256.0, "gpu": 128.0}
A100_PER_GPU_NODE = 4.0
POOL_ACCOUNT = {"cpu": "m3246", "gpu": "m3246_g"}
QOS_FACTOR = {
    "regular": 1.0,
    "shared": 1.0,
    "debug": 1.0,
    "interactive": 1.0,
    "preempt": 1.0,
    "xfer": 1.0,
    "gpu_regular": 1.0,
    "gpu_shared": 1.0,
    "gpu_debug": 1.0,
    "gpu_preempt": 1.0,
}
REFUSED_QOS = ("premium", "overrun")
CONCURRENCY = {"cpu": 2.0, "gpu": 4.0}  # CPU in whole nodes, GPU in GPUs
TERMINAL_STATES = (
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    "TIMEOUT",
    "OUT_OF_MEMORY",
    "NODE_FAIL",
    "PREEMPTED",
    "BOOT_FAIL",
    "DEADLINE",
)
PRICED_FLAGS = (
    "-J",
    "--job-name",
    "--requeue",
    "--no-requeue",
    "-A",
    "--account",
    "-q",
    "--qos",
    "-t",
    "--time",
    "-a",
    "--array",
    "-N",
    "--nodes",
    "-G",
    "--gpus",
    "-c",
    "--cpus-per-task",
    "-C",
    "--constraint",
)

EXIT_OK, EXIT_USAGE, EXIT_CAP, EXIT_CONCURRENCY = 0, 2, 3, 4
EXIT_INTEGRITY, EXIT_UNREGISTERED, EXIT_SBATCH = 5, 6, 7


class MeterError(RuntimeError):
    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Request:
    stage: str
    pool: str
    qos: str
    ntasks: int
    throttle: int
    timelimit_h: float
    billing: float
    gpus_per_task: int
    label: str

    @property
    def node_fraction(self) -> float:
        return self.billing / WHOLE_NODE_BILLING[self.pool]

    def reservation(self) -> float:
        """Maximum billable node-hours in this request's pool."""
        return self.ntasks * self.timelimit_h * self.node_fraction * QOS_FACTOR[self.qos]

    def concurrency(self) -> float:
        width = min(self.ntasks, self.throttle)
        if self.pool == "cpu":
            return width * self.node_fraction
        return float(width * self.gpus_per_task)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_budget(path: Path) -> dict:
    budget = json.loads(path.read_text())
    if budget.get("campaign_key") != CAMPAIGN_KEY:
        raise MeterError(f"budget {path} is not for {CAMPAIGN_KEY}", EXIT_INTEGRITY)
    for pool in ("cpu", "gpu"):
        section = budget["pools"][pool]
        total = float(section["campaign_cap_node_hours"])
        stages = section["stages"]
        if sum(float(v) for v in stages.values()) > total + 1e-9:
            raise MeterError(f"{pool} stage allocations exceed the campaign cap", EXIT_INTEGRITY)
    return budget


def read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise MeterError(f"{path}:{number}: unparseable ledger line", EXIT_INTEGRITY) from exc
    return records


def admissions(records: Iterable[dict]) -> dict[str, dict]:
    """Fold the ledger into one entry per admission token."""
    folded: dict[str, dict] = {}
    for rec in records:
        kind, token = rec.get("kind"), rec.get("token")
        if kind == "open":
            if token in folded:
                raise MeterError(f"token {token} opened twice", EXIT_INTEGRITY)
            folded[token] = dict(rec, job_id=None, released=False)
        elif kind in ("job", "release"):
            if token not in folded:
                raise MeterError(f"{kind} for unknown token {token}", EXIT_INTEGRITY)
            if kind == "job":
                folded[token]["job_id"] = rec["job_id"]
            else:
                folded[token]["released"] = True
        elif kind != "budget":
            raise MeterError(f"unknown ledger record kind {kind!r}", EXIT_INTEGRITY)
    return folded


def check_budget_binding(records: list[dict], budget_sha: str) -> None:
    bound = [r["budget_sha256"] for r in records if r.get("kind") == "budget"]
    if bound and bound[-1] != budget_sha:
        raise MeterError(
            f"budget sha256 {budget_sha[:12]} differs from the ledger's {bound[-1][:12]}; "
            "a changed budget needs a new ledger 'budget' record written by `rebind`",
            EXIT_INTEGRITY,
        )


# ---------------------------------------------------------------- sacct accounting


def _expand_bracket(job_id: str) -> list[str]:
    """``123_[0-3,7%2]`` -> ``['123_0', ..., '123_3', '123_7']``."""
    base, _, rest = job_id.partition("_[")
    body = rest.rstrip("]").split("%", 1)[0]
    out = []
    for part in body.split(","):
        lo, _, hi = part.partition("-")
        out += [f"{base}_{i}" for i in range(int(lo), int(hi or lo) + 1)]
    return out


def parse_sacct(text: str) -> dict[str, dict]:
    """Parse ``sacct -P -n --duplicates -o JobID,JobName,State,ElapsedRaw,AllocTRES,Start``.

    Returns, per scheduler task id (each array task is its own id), its attempts keyed
    by ``Start``.  Step rows are dropped.  An array-bracket row is kept only when its
    state is terminal (tasks cancelled before starting), as zero-cost terminal tasks;
    a pending bracket row carries no task that could have spent.
    """
    tasks: dict[str, dict] = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith("JobID|"):
            continue
        fields = line.split("|")
        if len(fields) < 6:
            raise MeterError(f"malformed sacct row: {line!r}", EXIT_INTEGRITY)
        job_id, name, state, elapsed, tres, start = fields[:6]
        state = state.split()[0] if state.strip() else "UNKNOWN"
        if "." in job_id:
            continue
        if "[" in job_id:
            if state in TERMINAL_STATES:
                for tid in _expand_bracket(job_id):
                    entry = tasks.setdefault(tid, {"name": name, "attempts": {}})
                    entry["attempts"].setdefault("NEVER-STARTED", (0, 0.0, state))
            continue
        match = re.search(r"billing=(\d+)", tres)
        billing = float(match.group(1)) if match else 0.0
        entry = tasks.setdefault(job_id, {"name": name, "attempts": {}})
        key = start if start and start not in ("Unknown", "None") else "NOT-STARTED"
        attempt = (int(elapsed or 0), billing, state)
        previous = entry["attempts"].get(key)
        if previous is not None and previous[2] in TERMINAL_STATES:
            if attempt[2] in TERMINAL_STATES and previous[:2] != attempt[:2]:
                raise MeterError(f"conflicting terminal rows for attempt {job_id}@{key}", EXIT_INTEGRITY)
            continue
        entry["attempts"][key] = attempt
    for entry in tasks.values():
        entry["states"] = {a[2] for a in entry["attempts"].values()}
    return tasks


def task_node_hours(entry: dict, qos: str, pool: str) -> float:
    return sum(
        elapsed / 3600.0 * billing / WHOLE_NODE_BILLING[pool] * QOS_FACTOR.get(qos, 1.0)
        for elapsed, billing, _ in entry["attempts"].values()
    )


def base_job(task_id: str) -> str:
    return task_id.split("_", 1)[0]


def charges(folded: dict[str, dict], sacct_tasks: dict[str, dict]) -> dict[str, dict]:
    """Per admission: measured node-hours, whether closed, and the charged value."""
    out = {}
    for token, adm in folded.items():
        if adm["released"] and not adm["job_id"]:
            out[token] = {"measured": 0.0, "closed": True, "charged": 0.0, "tasks_seen": 0}
            continue
        job = adm.get("job_id")
        mine = {tid: e for tid, e in sacct_tasks.items() if job and base_job(tid) == str(job)}
        measured = sum(task_node_hours(e, adm["qos"], adm["pool"]) for e in mine.values())
        terminal = all(
            e["states"] and all(s in TERMINAL_STATES for s in e["states"]) for e in mine.values()
        )
        closed = bool(mine) and len(mine) >= adm["ntasks"] and terminal
        charged = measured if closed else max(measured, adm["reservation_node_hours"])
        out[token] = {
            "measured": measured,
            "closed": closed,
            "charged": charged,
            "tasks_seen": len(mine),
        }
    return out


def unregistered(folded: dict[str, dict], sacct_tasks: dict[str, dict]) -> list[str]:
    known = {str(a["job_id"]) for a in folded.values() if a.get("job_id")}
    return sorted(
        tid
        for tid, e in sacct_tasks.items()
        if e["name"].startswith(JOB_PREFIX) and base_job(tid) not in known
    )


# ---------------------------------------------------------------- admission


def summarize(budget: dict, folded: dict[str, dict], charged: dict[str, dict]) -> dict:
    summary = {}
    for pool in ("cpu", "gpu"):
        section = budget["pools"][pool]
        by_stage: dict[str, float] = {s: 0.0 for s in section["stages"]}
        concurrency = 0.0
        for token, adm in folded.items():
            if adm["pool"] != pool:
                continue
            by_stage.setdefault(adm["stage"], 0.0)
            by_stage[adm["stage"]] += charged[token]["charged"]
            if not charged[token]["closed"] and not adm["released"]:
                concurrency += adm["concurrency"]
        summary[pool] = {
            "cap_node_hours": float(section["campaign_cap_node_hours"]),
            "charged_node_hours": sum(by_stage.values()),
            "charged_by_stage": by_stage,
            "stage_allocations": {k: float(v) for k, v in section["stages"].items()},
            "open_concurrency": concurrency,
        }
        if pool == "gpu":
            summary[pool]["charged_a100_hours"] = A100_PER_GPU_NODE * summary[pool]["charged_node_hours"]
    return summary


def decide(budget: dict, summary: dict, req: Request) -> tuple[int, str]:
    pool = summary[req.pool]
    if req.stage not in pool["stage_allocations"]:
        return EXIT_CAP, f"stage {req.stage!r} has no allocation in the {req.pool} pool"
    need = req.reservation()
    stage_after = pool["charged_by_stage"].get(req.stage, 0.0) + need
    total_after = pool["charged_node_hours"] + need
    if stage_after > pool["stage_allocations"][req.stage] + 1e-9:
        return EXIT_CAP, (
            f"stage {req.stage} would reach {stage_after:.3f} of "
            f"{pool['stage_allocations'][req.stage]:.3f} {req.pool} node-h"
        )
    if total_after > pool["cap_node_hours"] + 1e-9:
        return EXIT_CAP, f"campaign {req.pool} total would reach {total_after:.3f} of {pool['cap_node_hours']:.3f}"
    conc_after = pool["open_concurrency"] + req.concurrency()
    if conc_after > CONCURRENCY[req.pool] + 1e-9:
        return EXIT_CONCURRENCY, (
            f"{req.pool} concurrency would reach {conc_after:.3f} of {CONCURRENCY[req.pool]}"
        )
    return EXIT_OK, f"admitted: reserve {need:.4f} {req.pool} node-h; stage after {stage_after:.3f}"


def validate_request(req: Request, sbatch_args: Sequence[str]) -> None:
    if req.pool not in POOL_ACCOUNT:
        raise MeterError(f"unknown pool {req.pool}", EXIT_USAGE)
    if req.qos in REFUSED_QOS or req.qos not in QOS_FACTOR:
        raise MeterError(f"QOS {req.qos} is refused or unpriced", EXIT_USAGE)
    if req.ntasks < 1 or req.throttle < 1 or req.timelimit_h <= 0 or req.billing <= 0:
        raise MeterError("ntasks, throttle, timelimit and billing must be positive", EXIT_USAGE)
    if req.pool == "gpu" and req.gpus_per_task < 1:
        raise MeterError("a GPU-pool request needs --gpus-per-task >= 1", EXIT_USAGE)
    if not re.fullmatch(r"[a-z0-9][a-z0-9_.]{0,40}", req.label):
        raise MeterError("label must be [a-z0-9_.], <= 41 chars", EXIT_USAGE)
    for arg in sbatch_args:
        flag = arg.split("=", 1)[0]
        if flag in PRICED_FLAGS:
            raise MeterError(f"sbatch argument {flag} is set by the meter, not the caller", EXIT_USAGE)


def sbatch_argv(req: Request, sbatch_args: Sequence[str]) -> list[str]:
    minutes = int(math.ceil(req.timelimit_h * 60))
    argv = [
        "sbatch",
        "--parsable",
        f"--job-name={JOB_PREFIX}{req.label}",
        "--no-requeue",
        f"--account={POOL_ACCOUNT[req.pool]}",
        f"--qos={req.qos}",
        f"--time={minutes}",
    ]
    if req.ntasks > 1:
        argv.append(f"--array=0-{req.ntasks - 1}%{req.throttle}")
    return argv + list(sbatch_args)


class Ledger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path.with_suffix(".lock"), "a")

    def __enter__(self) -> "Ledger":
        fcntl.flock(self._fh, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc: object) -> None:
        fcntl.flock(self._fh, fcntl.LOCK_UN)
        self._fh.close()

    def append(self, record: dict) -> None:
        with open(self.path, "a") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())


def run_sacct(job_ids: Sequence[str]) -> str:
    """Two queries: every admitted job id (no window: ``-j`` defaults to epoch), and the
    last 14 days of the user's jobs for the unregistered-``s5c-`` scan (sacct refuses
    much wider windows)."""
    fields = "JobID,JobName,State,ElapsedRaw,AllocTRES,Start"
    user = os.environ.get("USER", "josephrb")
    queries = [["-S", "now-14days", "-E", "now"]]
    if job_ids:
        queries.append(["-j", ",".join(sorted(set(job_ids)))])
    out = []
    for extra in queries:
        argv = ["sacct", "-P", "-n", "--duplicates", "-u", user, "-o", fields, *extra]
        proc = subprocess.run(argv, capture_output=True, text=True)
        if proc.returncode != 0:
            raise MeterError(f"sacct failed rc={proc.returncode}: {proc.stderr.strip()}", EXIT_INTEGRITY)
        out.append(proc.stdout)
    return "\n".join(out)


def state_of(budget_path: Path, ledger_path: Path, sacct_text: str | None) -> tuple[dict, dict, dict, dict]:
    budget = load_budget(budget_path)
    records = read_ledger(ledger_path)
    check_budget_binding(records, sha256_file(budget_path))
    folded = admissions(records)
    ids = [str(a["job_id"]) for a in folded.values() if a.get("job_id")]
    text = sacct_text if sacct_text is not None else run_sacct(ids)
    tasks = parse_sacct(text)
    orphans = unregistered(folded, tasks)
    if orphans:
        raise MeterError(f"unregistered campaign jobs in sacct: {orphans}", EXIT_UNREGISTERED)
    charged = charges(folded, tasks)
    return budget, folded, charged, summarize(budget, folded, charged)


def cmd_submit(args: argparse.Namespace) -> int:
    req = Request(
        stage=args.stage,
        pool=args.pool,
        qos=args.qos,
        ntasks=args.ntasks,
        throttle=args.throttle or args.ntasks,
        timelimit_h=args.timelimit_h,
        billing=args.billing,
        gpus_per_task=args.gpus_per_task,
        label=args.label,
    )
    validate_request(req, args.sbatch_args)
    ledger = Ledger(args.ledger)
    with ledger:
        budget, folded, charged, summary = state_of(args.budget, args.ledger, None)
        code, message = decide(budget, summary, req)
        print(message)
        if code != EXIT_OK:
            return code
        token = f"{utc_now()}-{os.getpid()}-{req.label}"
        argv = sbatch_argv(req, args.sbatch_args)
        ledger.append(
            {
                "kind": "open",
                "token": token,
                "utc": utc_now(),
                "stage": req.stage,
                "pool": req.pool,
                "qos": req.qos,
                "ntasks": req.ntasks,
                "throttle": req.throttle,
                "timelimit_h": req.timelimit_h,
                "billing": req.billing,
                "gpus_per_task": req.gpus_per_task,
                "reservation_node_hours": req.reservation(),
                "concurrency": req.concurrency(),
                "label": req.label,
                "measures": args.measures,
                "cannot_authorize": args.cannot_authorize,
                "argv": argv,
            }
        )
        if args.dry_run:
            ledger.append({"kind": "release", "token": token, "utc": utc_now(), "reason": "dry-run"})
            print("DRY-RUN", " ".join(argv))
            return EXIT_OK
        proc = subprocess.run(argv, capture_output=True, text=True)
        job = proc.stdout.strip().split(";")[0]
        if proc.returncode != 0 or not job.isdigit():
            ledger.append(
                {"kind": "release", "token": token, "utc": utc_now(), "reason": proc.stderr.strip()[:500]}
            )
            print(f"sbatch failed rc={proc.returncode}: {proc.stderr.strip()}", file=sys.stderr)
            return EXIT_SBATCH
        ledger.append({"kind": "job", "token": token, "utc": utc_now(), "job_id": job})
        print(f"JOB {job}")
        return EXIT_OK


def cmd_measure(args: argparse.Namespace) -> int:
    sacct_text = args.sacct_file.read_text() if args.sacct_file else None
    budget, folded, charged, summary = state_of(args.budget, args.ledger, sacct_text)
    receipt = {
        "campaign_key": CAMPAIGN_KEY,
        "measured_utc": utc_now(),
        "budget_sha256": sha256_file(args.budget),
        "ledger_sha256": sha256_file(args.ledger) if args.ledger.exists() else None,
        "unit": "billed node-hours = ElapsedRaw/3600 * billing/(256 CPU | 128 GPU) * qos_factor; GPU A100-h = 4 x GPU node-h",
        "summary": summary,
        "admissions": {
            token: {
                "stage": adm["stage"],
                "pool": adm["pool"],
                "job_id": adm.get("job_id"),
                "released": adm["released"],
                "reservation_node_hours": adm["reservation_node_hours"],
                **charged[token],
            }
            for token, adm in folded.items()
        },
    }
    text = json.dumps(receipt, indent=1, sort_keys=True)
    if args.out:
        args.out.write_text(text + "\n")
    print(text)
    return EXIT_OK


def cmd_rebind(args: argparse.Namespace) -> int:
    load_budget(args.budget)
    with Ledger(args.ledger) as ledger:
        ledger.append(
            {
                "kind": "budget",
                "utc": utc_now(),
                "budget_sha256": sha256_file(args.budget),
                "reason": args.reason,
            }
        )
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--budget", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("submit", help="admit, reserve and sbatch")
    s.add_argument("--stage", required=True)
    s.add_argument("--pool", choices=sorted(POOL_ACCOUNT), required=True)
    s.add_argument("--qos", required=True)
    s.add_argument("--ntasks", type=int, required=True)
    s.add_argument("--throttle", type=int, default=0)
    s.add_argument("--timelimit-h", type=float, required=True)
    s.add_argument("--billing", type=float, required=True, help="AllocTRES billing per task")
    s.add_argument("--gpus-per-task", type=int, default=0)
    s.add_argument("--label", required=True)
    s.add_argument("--measures", required=True, help="the quantity this job measures")
    s.add_argument("--cannot-authorize", required=True, help="what its terminal result cannot authorize")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("sbatch_args", nargs=argparse.REMAINDER)
    m = sub.add_parser("measure", help="reconcile the ledger against sacct")
    m.add_argument("--sacct-file", type=Path)
    m.add_argument("--out", type=Path)
    r = sub.add_parser("rebind", help="bind the ledger to a (new) committed budget")
    r.add_argument("--reason", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "sbatch_args", None) and args.sbatch_args[:1] == ["--"]:
        args.sbatch_args = args.sbatch_args[1:]
    try:
        return {"submit": cmd_submit, "measure": cmd_measure, "rebind": cmd_rebind}[args.cmd](args)
    except MeterError as exc:
        print(f"s5c_meter: {exc}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
