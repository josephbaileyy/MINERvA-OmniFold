#!/usr/bin/env python3
"""Admission and accounting for the scalar-5D campaigns: s5c (activated 2026-09-24) and its
successor s5n (``OI-191``, activated 2026-09-25).

Authority: ``docs/orchestration/AUTHORIZATION-20260924-scalar5d-campaign-activation.md``
§3 rows S1-S2 (Joseph's D2), carried forward to the successor by
``docs/orchestration/AUTHORIZATION-20260925-negweight-refined-successor.md`` §3 row N4.  For
these campaigns only, ``r5_meter.py`` is displaced by this meter; ``r5_meter.py`` itself and
every guard that calls it are untouched.

ONE METER, ONE LEDGER PER CAMPAIGN.  The budget's ``campaign_key`` selects the campaign and
its job-name prefix (``CAMPAIGNS``); each campaign has its own budget and ledger, and the
unregistered-job scan sees only its own prefix.  A successor's budget may declare a
``carried_forward`` block per pool (the prior envelope and the prior campaign's reconciled
charge): the meter then refuses a cap above the unspent portion, so a remaining balance can
never be re-read as a new grant.

UNITS ARE NATIVE BILLED UNITS, NOT TASK-HOURS.

* CPU pool (account ``m3246``): billed CPU node-hours
  ``= ElapsedRaw/3600 * billing/256 * qos_factor`` per execution attempt (256, not 128).
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

THE PRICE IS CHECKED AGAINST THE SCHEDULER, NOT TRUSTED.  Slurm's billing depends on
memory as well as CPUs (``--mem=90G`` with 32 CPUs bills 50), so the caller declares
``--billing`` and, immediately after ``sbatch``, the meter reads the job's own ``TRES``
from ``scontrol show job``.  A billing or GPU count above the declared one cancels the
job at once and refuses (exit 8); the ledger keeps the job id, so ``sacct`` still
accounts for anything it spent.

Exit codes: 0 admitted/ok, 3 refused by a cap, 4 refused by concurrency, 5 ledger or
budget integrity failure, 6 unregistered campaign job found, 7 sbatch failed (the
reservation is released), 8 scheduler billing exceeded the declared price (job
cancelled), 2 usage error.
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

CAMPAIGNS = {"s5c-20260924": "s5c-", "s5n-20260925": "s5n-"}  # campaign key -> job-name prefix
CAMPAIGN_KEY = "s5c-20260924"
JOB_PREFIX = CAMPAIGNS[CAMPAIGN_KEY]
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
    "--parsable",
)

MODELED_FLAGS = ("--mem", "--nodes", "--cpus-per-task", "--ntasks", "--gpus-per-task", "--gpus",
                 "--constraint", "--output", "--error", "--dependency", "--wrap")
UNPRICED_RESOURCE_FLAGS = ("--mem-per-cpu", "--mem-per-gpu", "--exclusive", "--ntasks-per-node",
                           "--cpus-per-gpu", "--gres")

EXIT_OK, EXIT_USAGE, EXIT_CAP, EXIT_CONCURRENCY = 0, 2, 3, 4
EXIT_INTEGRITY, EXIT_UNREGISTERED, EXIT_SBATCH, EXIT_UNDERPRICED = 5, 6, 7, 8


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
    if budget.get("campaign_key") not in CAMPAIGNS:
        raise MeterError(f"budget {path} names no known campaign ({sorted(CAMPAIGNS)})", EXIT_INTEGRITY)
    for pool in ("cpu", "gpu"):
        section = budget["pools"][pool]
        total = float(section["campaign_cap_node_hours"])
        stages = section["stages"]
        if sum(float(v) for v in stages.values()) > total + 1e-9:
            raise MeterError(f"{pool} stage allocations exceed the campaign cap", EXIT_INTEGRITY)
        carried = section.get("carried_forward")
        if carried is not None:
            unspent = float(carried["envelope_node_hours"]) - float(carried["prior_charged_node_hours"])
            if total > unspent + 1e-9:
                raise MeterError(
                    f"{pool} cap {total:.4f} exceeds the unspent carried-forward envelope {unspent:.4f}",
                    EXIT_INTEGRITY,
                )
    return budget


def job_prefix(budget: dict) -> str:
    return CAMPAIGNS[budget["campaign_key"]]


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
            folded[token] = dict(rec, job_id=None, released=False, raw_ids={})
        elif kind == "link":
            owner = [t for t, a in folded.items() if str(a.get("job_id")) == str(rec["job_id"])]
            if len(owner) != 1:
                raise MeterError(f"link for job {rec['job_id']} matches {len(owner)} admissions", EXIT_INTEGRITY)
            folded[owner[0]]["raw_ids"].update({str(k): str(v) for k, v in rec["raw_ids"].items()})
        elif kind in ("job", "release"):
            if token not in folded:
                raise MeterError(f"{kind} for unknown token {token}", EXIT_INTEGRITY)
            if kind == "job":
                folded[token]["job_id"] = rec["job_id"]
            else:
                folded[token]["released"] = True
        elif kind not in ("budget", "note"):
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
            out[token] = {"measured": 0.0, "closed": True, "charged": 0.0, "tasks_seen": 0, "underpriced": False}
            continue
        job = adm.get("job_id")
        raw = {v: f"{job}_{k}" for k, v in adm.get("raw_ids", {}).items()}
        mine = {}
        for tid, e in sacct_tasks.items():
            if job and base_job(tid) == str(job):
                mine[tid] = e
            elif tid in raw:  # an array task sacct records under its own raw job id
                mine.setdefault(raw[tid], e)
        measured = sum(task_node_hours(e, adm["qos"], adm["pool"]) for e in mine.values())
        terminal = all(
            e["states"] and all(s in TERMINAL_STATES for s in e["states"]) for e in mine.values()
        )
        closed = bool(mine) and len(mine) >= adm["ntasks"] and terminal
        charged = measured if closed else max(measured, adm["reservation_node_hours"])
        billed = [b for e in mine.values() for (_, b, _) in e["attempts"].values()]
        out[token] = {
            "measured": measured,
            "closed": closed,
            "charged": charged,
            "tasks_seen": len(mine),
            "underpriced": bool(billed) and max(billed) > adm["billing"],
        }
    return out


def unregistered(folded: dict[str, dict], sacct_tasks: dict[str, dict], prefix: str = JOB_PREFIX) -> list[str]:
    known = {str(a["job_id"]) for a in folded.values() if a.get("job_id")}
    known |= {raw for a in folded.values() for raw in a.get("raw_ids", {}).values()}
    return sorted(
        tid
        for tid, e in sacct_tasks.items()
        if e["name"].startswith(prefix) and base_job(tid) not in known
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
        carried = section.get("carried_forward")
        if carried is not None:
            prior = float(carried["prior_charged_node_hours"])
            summary[pool]["carried_forward"] = {
                "envelope_node_hours": float(carried["envelope_node_hours"]),
                "prior_charged_node_hours": prior,
                "envelope_charged_node_hours": prior + summary[pool]["charged_node_hours"],
            }
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
        if arg.startswith("--"):
            name = arg.split("=", 1)[0]
            # sbatch accepts any unambiguous abbreviation of a long option (--tim=, --qo=, --arr=)
            hit = [f for f in PRICED_FLAGS if f.startswith("--") and len(name) >= 3 and f.startswith(name)]
            if hit:
                raise MeterError(f"sbatch argument {name} (abbreviates {hit[0]}) is set by the meter", EXIT_USAGE)
            if name not in MODELED_FLAGS and any(u.startswith(name) and len(name) >= 4 for u in UNPRICED_RESOURCE_FLAGS):
                raise MeterError(f"sbatch argument {name} changes the price in a way the meter does not model", EXIT_USAGE)
        elif arg.startswith("-") and len(arg) >= 2 and arg[:2] in PRICED_FLAGS:
            # -t600, -qpremium, -a0-999: an attached value is still the flag
            raise MeterError(f"sbatch argument {arg[:2]} is set by the meter, not the caller", EXIT_USAGE)
    ntasks = _flag_value(sbatch_args, ("-n", "--ntasks"))
    if ntasks is not None and int(ntasks) > 1:
        raise MeterError("--ntasks > 1 per array element is not priced by this meter", EXIT_USAGE)


def salloc_argv(req: Request, extra_args: Sequence[str], prefix: str = JOB_PREFIX) -> list[str]:
    """A held allocation (``salloc --no-shell``) for QOS that refuse batch jobs (``interactive``)."""
    if req.ntasks != 1:
        raise MeterError("an allocation is one scheduler job; use --ntasks 1", EXIT_USAGE)
    minutes = int(math.ceil(req.timelimit_h * 60))
    return ["salloc", "--no-shell", f"--job-name={prefix}{req.label}",
            f"--account={POOL_ACCOUNT[req.pool]}", f"--qos={req.qos}", f"--time={minutes}",
            *extra_args]


def run_salloc(argv: list[str], ledger: "Ledger", token: str, wait_s: float) -> tuple[str | None, str]:
    """Start salloc, record the job id the moment it is printed (so a pending request is never
    unregistered), and wait for the grant. Returns (job_id, stderr text)."""
    proc = subprocess.Popen(argv, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    job, lines, t0 = None, [], time.time()
    assert proc.stderr is not None
    for line in proc.stderr:
        lines.append(line)
        match = re.search(r"job allocation (\d+)", line)
        if match and job is None:
            job = match.group(1)
            ledger.append({"kind": "job", "token": token, "utc": utc_now(), "job_id": job})
        if "Granted job allocation" in line or time.time() - t0 > wait_s:
            break
    granted = any("Granted job allocation" in x for x in lines)
    if not granted and job is not None:
        subprocess.run(["scancel", job], capture_output=True, text=True)
        lines.append(f"not granted within {wait_s:.0f} s; cancelled {job}\n")
    proc.wait(timeout=60)
    return (job if granted else None), "".join(lines)


def sbatch_argv(req: Request, sbatch_args: Sequence[str], prefix: str = JOB_PREFIX) -> list[str]:
    minutes = int(math.ceil(req.timelimit_h * 60))
    argv = [
        "sbatch",
        "--parsable",
        f"--job-name={prefix}{req.label}",
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


SHARED_MB_PER_CPU = 1843.2  # 90G->50, 64G->36, 80000M->44 billed CPUs on shared CPU jobs


def _flag_value(args: Sequence[str], names: Sequence[str]) -> str | None:
    longs = [n for n in names if n.startswith("--")]
    for i, arg in enumerate(args):
        if arg.startswith("--") and len(arg.split("=", 1)[0]) >= 4:
            head = arg.split("=", 1)[0]
            full = [n for n in longs if n.startswith(head)]
            if full and head not in names:  # an abbreviation: read it as the full option
                arg = full[0] + arg[len(head):]
                if "=" not in arg and i + 1 < len(args):
                    return args[i + 1]
        for name in names:
            if arg == name and i + 1 < len(args):
                return args[i + 1]
            if name.startswith("--") and arg.startswith(name + "="):
                return arg.split("=", 1)[1]
            if not name.startswith("--") and arg.startswith(name) and len(arg) > len(name):
                return arg[len(name):]
    return None


def _mem_mb(text: str) -> float:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([KMGT]?)B?", text.strip().upper())
    if not match:
        raise MeterError(f"cannot parse --mem {text!r}", EXIT_USAGE)
    scale = {"K": 1 / 1024, "": 1, "M": 1, "G": 1024, "T": 1024 * 1024}[match.group(2)]
    return float(match.group(1)) * scale


def predicted_billing(req: "Request", sbatch_args: Sequence[str]) -> float:
    """A conservative per-task billing from the sbatch arguments, never below the truth
    as measured on this site (shared CPU jobs bill max(cpus, mem/1843.2 MB) rounded up to
    a whole core; non-shared QOS bill whole nodes; one shared GPU bills 32)."""
    nodes = float(_flag_value(sbatch_args, ("-N", "--nodes")) or 1)
    if req.qos == "xfer":
        return 2.0
    if req.pool == "cpu":
        if req.qos != "shared":
            return 256.0 * nodes
        cpus = float(_flag_value(sbatch_args, ("-c", "--cpus-per-task")) or 1)
        mem = _flag_value(sbatch_args, ("--mem",))
        need = max(cpus, math.ceil(_mem_mb(mem) / SHARED_MB_PER_CPU) if mem else 0)
        return float(2 * math.ceil(need / 2))
    if req.qos not in ("gpu_shared", "shared"):  # `-q shared -C gpu` is how Perlmutter reaches gpu_shared
        return 128.0 * nodes
    return 32.0 * max(req.gpus_per_task, 1)


def scheduler_tres(job: str) -> dict[str, float]:
    """``billing`` and ``gres/gpu`` from ``scontrol show job -o <job>``: ``AllocTRES`` once the
    job has resources, else ``ReqTRES`` (which can understate a shared job's billing)."""
    proc = subprocess.run(["scontrol", "show", "job", "-o", job], capture_output=True, text=True)
    if proc.returncode != 0:
        raise MeterError(f"scontrol failed for {job}: {proc.stderr.strip()}", EXIT_INTEGRITY)
    first = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
    fields = dict(re.findall(r"(?:^|\s)(AllocTRES|ReqTRES|TRES)=(\S*)", first))
    def real(v):  # a pending job prints the literal AllocTRES=(null) (measured 2026-09-25)
        return v if v and v != "(null)" else None

    tres = real(fields.get("AllocTRES")) or real(fields.get("ReqTRES")) or real(fields.get("TRES"))
    if not tres:
        raise MeterError(f"no TRES field for job {job}", EXIT_INTEGRITY)
    out = {"billing": 0.0, "gpus": 0.0}
    for item in tres.split(","):
        key, _, value = item.partition("=")
        if key == "billing":
            out["billing"] = float(value)
        elif key == "gres/gpu":
            out["gpus"] = float(value)
    return out


def run_sacct(job_ids: Sequence[str], raw_ids: Sequence[str] = ()) -> str:
    """Queries: every admitted job id and every linked raw task id, WITHOUT a user filter (no
    window: ``-j`` defaults to epoch; measured 2026-09-25: ``-u josephrb -j 58856172`` returns
    nothing for a raw-id array task that plain ``-j 58856172`` returns); and the last 14 days of
    the user's jobs for the unregistered-``s5c-`` scan (sacct refuses much wider windows)."""
    fields = "JobID,JobName,State,ElapsedRaw,AllocTRES,Start"
    user = os.environ.get("USER", "josephrb")
    queries = [["-u", user, "-S", "now-14days", "-E", "now"]]
    ids = sorted(set(job_ids) | set(raw_ids))
    if ids:
        queries.append(["-j", ",".join(ids)])
    out = []
    for extra in queries:
        argv = ["sacct", "-P", "-n", "--duplicates", "-o", fields, *extra]
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
    raws = [raw for a in folded.values() for raw in a.get("raw_ids", {}).values()]
    text = sacct_text if sacct_text is not None else run_sacct(ids, raws)
    tasks = parse_sacct(text)
    orphans = unregistered(folded, tasks, job_prefix(budget))
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
    floor = predicted_billing(req, args.sbatch_args)
    if req.billing < floor:
        print(f"declared billing {req.billing:g} is below the predicted {floor:g} for these sbatch arguments", file=sys.stderr)
        return EXIT_USAGE
    ledger = Ledger(args.ledger)
    with ledger:
        budget, folded, charged, summary = state_of(args.budget, args.ledger, None)
        code, message = decide(budget, summary, req)
        print(message)
        if code != EXIT_OK:
            return code
        token = f"{utc_now()}-{os.getpid()}-{req.label}"
        prefix = job_prefix(budget)
        argv = salloc_argv(req, args.sbatch_args, prefix) if args.allocate else sbatch_argv(req, args.sbatch_args, prefix)
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
        if args.allocate:
            job, text = run_salloc(argv, ledger, token, args.allocate_wait_s)
            if job is None:
                if not any(r.get("token") == token and r.get("kind") == "job" for r in read_ledger(args.ledger)):
                    ledger.append({"kind": "release", "token": token, "utc": utc_now(), "reason": text[-500:]})
                print(f"salloc failed: {text.strip()}", file=sys.stderr)
                return EXIT_SBATCH
            proc = subprocess.CompletedProcess(argv, 0, stdout=job, stderr=text)
        else:
            proc = subprocess.run(argv, capture_output=True, text=True)
        job = proc.stdout.strip().split(";")[0]
        if proc.returncode != 0 or not job.isdigit():
            ledger.append(
                {"kind": "release", "token": token, "utc": utc_now(), "reason": proc.stderr.strip()[:500]}
            )
            print(f"sbatch failed rc={proc.returncode}: {proc.stderr.strip()}", file=sys.stderr)
            return EXIT_SBATCH
        if not args.allocate:  # run_salloc recorded it when salloc first printed it
            ledger.append({"kind": "job", "token": token, "utc": utc_now(), "job_id": job})
        tres = scheduler_tres(job)
        if tres["billing"] > req.billing or (req.pool == "gpu" and tres["gpus"] > req.gpus_per_task):
            subprocess.run(["scancel", job], capture_output=True, text=True)
            ledger.append(
                {"kind": "note", "token": token, "utc": utc_now(), "note": f"cancelled: scheduler TRES {tres} exceeds the priced request"}
            )
            print(f"JOB {job} CANCELLED: scheduler TRES {tres} exceeds declared billing {req.billing}", file=sys.stderr)
            return EXIT_UNDERPRICED
        print(f"JOB {job} (scheduler billing {tres['billing']:g}, gpus {tres['gpus']:g})")
        return EXIT_OK


def cmd_measure(args: argparse.Namespace) -> int:
    sacct_text = args.sacct_file.read_text() if args.sacct_file else None
    budget, folded, charged, summary = state_of(args.budget, args.ledger, sacct_text)
    receipt = {
        "campaign_key": budget["campaign_key"],
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


def parse_scontrol_links(text: str, job: str) -> dict[str, str]:
    """``ArrayTaskId -> JobId`` for the array tasks of ``job`` that carry their own job id."""
    links = {}
    for jid, ajid, task in re.findall(r"JobId=(\d+) ArrayJobId=(\d+) ArrayTaskId=(\d+)", text):
        if ajid == str(job) and jid != str(job) and int(task) < 4294967294:
            links[task] = jid
    return links


def cmd_link(args: argparse.Namespace) -> int:
    """Record, from the scheduler's own ``scontrol`` view (or a saved copy of it), which raw job
    ids belong to an admitted array -- sacct can record a task under its raw id alone."""
    text = args.from_file.read_text() if args.from_file else subprocess.run(
        ["scontrol", "show", "job", "-o", str(args.job)], capture_output=True, text=True).stdout
    links = parse_scontrol_links(text, str(args.job))
    if not links:
        print("no raw-id array tasks found", file=sys.stderr)
        return EXIT_USAGE
    with Ledger(args.ledger) as ledger:
        admissions(read_ledger(args.ledger) + [{"kind": "link", "job_id": str(args.job), "raw_ids": links}])
        ledger.append({"kind": "link", "utc": utc_now(), "job_id": str(args.job), "raw_ids": links,
                       "evidence": str(args.from_file) if args.from_file else "scontrol show job -o"})
    print(json.dumps(links))
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
    s.add_argument("--allocate", action="store_true",
                   help="hold an allocation with salloc --no-shell instead of sbatch (QOS interactive)")
    s.add_argument("--allocate-wait-s", type=float, default=900.0)
    s.add_argument("sbatch_args", nargs=argparse.REMAINDER)
    m = sub.add_parser("measure", help="reconcile the ledger against sacct")
    m.add_argument("--sacct-file", type=Path)
    m.add_argument("--out", type=Path)
    k = sub.add_parser("link", help="record array tasks that sacct keeps under their own raw job id")
    k.add_argument("--job", required=True)
    k.add_argument("--from-file", type=Path)
    r = sub.add_parser("rebind", help="bind the ledger to a (new) committed budget")
    r.add_argument("--reason", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "sbatch_args", None) and args.sbatch_args[:1] == ["--"]:
        args.sbatch_args = args.sbatch_args[1:]
    try:
        return {"submit": cmd_submit, "measure": cmd_measure, "rebind": cmd_rebind, "link": cmd_link}[args.cmd](args)
    except MeterError as exc:
        print(f"s5c_meter: {exc}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
