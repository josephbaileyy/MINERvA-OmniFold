#!/usr/bin/env python3
"""Measure and enforce the R5 date and task-hour stop boundaries.

THE METERED UNIT IS AN EXECUTION ATTEMPT, NOT A JOB ID.  A requeued job keeps one
`JobID` and runs many times, and each run burns real wall time on a real node.  An
attempt is identified by ``(JobID, Start)`` -- with this field list ``Start`` is the
only attempt discriminator ``sacct`` returns -- and `ElapsedRaw` on those rows is
per-attempt, not cumulative.

* ATTEMPTS ARE SUMMED.  R5 §3 counts a retried task "in full" and says "a failed task
  spends", so every attempt of one job id is added.  "Distinct task identities" in §3's
  unit exists to stop the several REPRESENTATIONS of one execution -- ``.batch``,
  ``.extern``, numbered steps, array-bracket summary rows, and a repeated observation
  of one row -- from being counted twice.  It does not collapse several distinct
  EXECUTIONS of one job id.  See
  ``FINDING-20260906-r5-meter-undercounted-requeue-attempts.md``, which also records
  the reading this rejects, so the decision owner can overturn it in one place.
* WHAT IS DEDUPLICATED.  Two identical rows are one observation of one attempt and are
  counted once.  Step and array-bracket rows are excluded outright.  Rows whose
  ``Start`` is unknown -- a PENDING job -- are skipped.
* WHAT FAILS CLOSED.  Two rows sharing ``(JobID, Start)`` that disagree about ``End``,
  ``ElapsedRaw`` or GPU classification raise `MeterError` -- including the RUNNING
  snapshot plus later COMPLETED row that concatenating two query windows produces; the query needs
  ``--duplicates`` or a requeued job's earlier attempts are invisible; a
  schema-version-1 receipt is refused outright because it counted at most one attempt
  per job id; and a missing, stale or malformed receipt is a stop.

`spend` reports both identities: ``metered_task_ids`` answers "was this scheduler task
counted", and ``attempts_by_task_id`` with ``attempt_count`` answer "how many of its
executions were charged".
"""

from __future__ import annotations

import argparse
import csv
import getpass
import hashlib
import io
import json
import math
import os
import re
import shlex
import socket
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence, cast


DECISION_RECORD = (
    "docs/orchestration/"
    "DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md"
)
# Derived from `git log -1 --format=%cI 9ce59a59`: the decision landed at
# 2026-09-02T15:44:27+02:00, which is 2026-09-02T13:44:27Z.
T0_UTC_TEXT = "2026-09-02T13:44:27Z"
T0_UTC = datetime(2026, 9, 2, 13, 44, 27, tzinfo=timezone.utc)
# R5 names 2026-09-30 UTC inclusively, so the first firing instant is
# the beginning of that date in UTC.
STOP_DATE_UTC_TEXT = "2026-09-30T00:00:00Z"
STOP_DATE_UTC = datetime(2026, 9, 30, tzinfo=timezone.utc)
# R5's selected backstops are inclusive: spend equal to either 500
# task-hour ceiling has already fired the stop.
GPU_TASK_HOURS_CEILING = 500.0
CPU_TASK_HOURS_CEILING = 500.0
UNIT = (
    "task-hours: sum of post-t0 ElapsedRaw over every execution attempt, with the "
    "attempts of one job id summed; an attempt is (JobID, Start, End) and a repeated "
    "observation of one attempt is counted once; attempts straddling t0 are clipped "
    "at t0; .batch/.extern/step and array-bracket rows excluded"
)
DEFAULT_RECEIPT_PATH = Path("docs/orchestration/state/r5-meter-receipt.json")
SACCT_FIELDS = (
    "JobID",
    "JobName",
    "State",
    "ElapsedRaw",
    "Partition",
    "Start",
    "End",
    "AllocTRES",
)
TASK_ID_RE = re.compile(r"^[0-9]+(?:_[0-9]+)?$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class MeterError(ValueError):
    """Report invalid accounting input or an invalid meter receipt."""


@dataclass(frozen=True)
class AttemptRecord:
    """One metered EXECUTION ATTEMPT of a Slurm task.

    A requeued job keeps one `task_id` across every attempt, so this is not one per
    scheduler task: `AttemptKey` identifies the attempt, `task_id` identifies the task
    it belongs to.

    Parameters
    ----------
    task_id : str
        Plain Slurm job ID or concrete array-task ID. Shared by every attempt of
        a requeued job.
    state : str
        Normalized Slurm state of this attempt.
    elapsed_seconds : float
        Wall-clock seconds CHARGED to this attempt, after any clip at t0.
    raw_elapsed_seconds : int
        `ElapsedRaw` exactly as the row reported it, before the t0 clip. Two
        observations of one attempt are compared on this rather than on the
        charged value, because a clip can drive two disagreeing rows to a
        matching zero.
    partition : str
        Slurm partition, the secondary GPU classification signal already folded
        into `is_gpu`.
    is_gpu : bool
        Whether AllocTRES or the partition identifies a GPU allocation. Attempts
        of one job id can differ here, because a requeue may land elsewhere.
    start : datetime
        Attempt start instant in UTC.
    end : str
        `End` exactly as the row reported it, including ``Unknown`` for an attempt
        still running. NOT part of the attempt identity -- it is compared between two
        observations of one attempt, and a disagreement refuses the dump.
    counted : bool
        False only for an attempt whose whole span precedes t0. Such an attempt is
        still recorded, so a later contradicting observation of it is refused
        rather than waved through.
    """

    task_id: str
    state: str
    elapsed_seconds: float
    raw_elapsed_seconds: int
    partition: str
    is_gpu: bool
    start: datetime
    end: str
    counted: bool


#: One execution attempt: ``(JobID, Start)``.  Slurm returns one record per attempt
#: under ``--duplicates``, and with this field list ``Start`` is the ONLY discriminator
#: between them.  Job id alone is not an attempt identity -- keying on it is the defect
#: this repair closes.
#:
#: ``End`` is deliberately NOT part of the key.  Two rows sharing ``(JobID, Start)`` and
#: differing in ``End`` are far more likely to be two OBSERVATIONS of one execution --
#: a RUNNING snapshot with ``End`` ``Unknown`` and the later COMPLETED row, which is
#: exactly what concatenating two query windows produces -- than two executions that
#: began in the same second.  Keying on ``End`` charged such a pair twice.  Since this
#: field list cannot tell the two situations apart, the pair is REFUSED rather than
#: resolved by guessing which reading was meant.
AttemptKey = tuple[str, datetime]


def parse_iso_utc(value: str) -> datetime:
    """Parse an ISO-8601 instant and normalize it to UTC.

    Parameters
    ----------
    value : str
        ISO-8601 timestamp with an explicit UTC offset or ``Z`` suffix.

    Returns
    -------
    datetime
        Timezone-aware timestamp normalized to UTC.

    Raises
    ------
    MeterError
        If the value is not a valid, timezone-aware ISO timestamp.
    """
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise MeterError(f"invalid ISO timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MeterError(f"timestamp must include a UTC offset: {value!r}")
    return parsed.astimezone(timezone.utc)


def format_iso_utc(value: datetime) -> str:
    """Format a timezone-aware instant as an ISO timestamp ending in ``Z``.

    Parameters
    ----------
    value : datetime
        Timezone-aware instant.

    Returns
    -------
    str
        UTC ISO-8601 timestamp.

    Raises
    ------
    MeterError
        If `value` is timezone-naive.
    """
    if value.tzinfo is None or value.utcoffset() is None:
        raise MeterError("cannot format a timezone-naive timestamp")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_sacct_start(value: str, *, line_number: int) -> datetime | None:
    if value in {"", "Unknown", "N/A", "None"}:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError as exc:
        raise MeterError(
            f"line {line_number}: invalid UTC Start value {value!r}"
        ) from exc


def _normalize_state(value: str, *, line_number: int) -> str:
    if not value.strip():
        raise MeterError(f"line {line_number}: State is empty")
    return value.split()[0].rstrip("+")


def _parse_elapsed(value: str, *, line_number: int) -> int:
    try:
        elapsed = int(value)
    except ValueError as exc:
        raise MeterError(
            f"line {line_number}: invalid ElapsedRaw value {value!r}"
        ) from exc
    if elapsed < 0:
        raise MeterError(f"line {line_number}: ElapsedRaw cannot be negative")
    return elapsed


def _alloc_tres_has_gpu(value: str, *, line_number: int) -> bool:
    if not value.strip():
        return False

    for entry in value.split(","):
        key, separator, count_text = entry.strip().partition("=")
        normalized_key = key.strip().lower()
        if normalized_key != "gres/gpu" and not normalized_key.startswith(
            "gres/gpu:"
        ):
            continue
        if not separator:
            raise MeterError(
                f"line {line_number}: invalid AllocTRES GPU entry {entry!r}"
            )
        try:
            count = int(count_text.strip())
        except ValueError as exc:
            raise MeterError(
                f"line {line_number}: invalid AllocTRES GPU count {count_text!r}"
            ) from exc
        if count < 0:
            raise MeterError(
                f"line {line_number}: AllocTRES GPU count cannot be negative"
            )
        if count > 0:
            return True
    return False


def _parse_sacct_dump(raw_text: str) -> dict[AttemptKey, AttemptRecord]:
    attempts: dict[AttemptKey, AttemptRecord] = {}
    reader = csv.reader(io.StringIO(raw_text), delimiter="|")
    for line_number, row in enumerate(reader, start=1):
        if not row or all(not field for field in row):
            continue
        if len(row) == len(SACCT_FIELDS) + 1 and row[-1] == "":
            row = row[:-1]
        if len(row) != len(SACCT_FIELDS):
            raise MeterError(
                f"line {line_number}: expected {len(SACCT_FIELDS)} fields, "
                f"found {len(row)}"
            )

        (
            job_id,
            _,
            state_text,
            elapsed_text,
            partition,
            start_text,
            end_text,
            alloc_tres,
        ) = row
        # A step or array-bracket row is a REPRESENTATION of an execution, never an
        # attempt, so it is excluded before any attempt is formed.
        if TASK_ID_RE.fullmatch(job_id) is None:
            continue

        start = _parse_sacct_start(start_text, line_number=line_number)
        if start is None:
            continue

        raw_elapsed = _parse_elapsed(elapsed_text, line_number=line_number)
        is_gpu = _alloc_tres_has_gpu(
            alloc_tres,
            line_number=line_number,
        ) or partition.lower().startswith("gpu")

        key: AttemptKey = (job_id, start)
        existing = attempts.get(key)
        if existing is not None:
            # One attempt observed twice.  Identical rows are one observation and are
            # charged once.  Rows that disagree about when it ENDED, about what it
            # spent, or about which ceiling it spent against cannot all be true of one
            # execution, and this field list cannot tell "two observations of one
            # execution" from "two executions that started in the same second".
            # Choosing between them would be a measurement nobody made, so the whole
            # dump is refused.  The common cause is a dump assembled from more than one
            # query window, where a job appears once RUNNING (End Unknown) and again
            # COMPLETED: re-query it in a single window, or with `-j <jobid>`.
            for field, recorded, observed in (
                ("End", existing.end, end_text),
                ("ElapsedRaw", existing.raw_elapsed_seconds, raw_elapsed),
                ("GPU classification", existing.is_gpu, is_gpu),
            ):
                if recorded != observed:
                    raise MeterError(
                        f"line {line_number}: conflicting {field} for execution "
                        f"attempt of task identity {job_id} started {start_text}: "
                        f"{recorded!r} then {observed!r}. Two observations of one "
                        f"execution and two executions starting in the same second "
                        f"are indistinguishable in these fields, so this dump is "
                        f"refused rather than guessed at"
                    )
            continue

        # The clip is per ATTEMPT: a requeued job can have one attempt straddling t0
        # and later attempts wholly after it, and clipping the job would charge the
        # wrong span for every one of them.
        charged_seconds = float(raw_elapsed)
        counted = True
        if start < T0_UTC:
            charged_seconds = max(
                0.0,
                charged_seconds - (T0_UTC - start).total_seconds(),
            )
            # An attempt that ended at or before t0 spent nothing R5 meters.  It is
            # still RECORDED so a contradicting observation of it is still refused.
            counted = charged_seconds > 0.0

        attempts[key] = AttemptRecord(
            task_id=job_id,
            state=_normalize_state(state_text, line_number=line_number),
            elapsed_seconds=charged_seconds,
            raw_elapsed_seconds=raw_elapsed,
            partition=partition,
            is_gpu=is_gpu,
            start=start,
            end=end_text,
            counted=counted,
        )
    return attempts


def _sum_charged_seconds(
    attempts: Sequence[AttemptRecord],
) -> tuple[float, float]:
    """Sum charged wall-clock seconds over attempts, splitting GPU from CPU.

    THIS IS THE WHOLE SUMMING STEP.  R5 §3 counts a retried task "in full" and says
    "a failed task spends", so every execution attempt of one job id is ADDED: 952
    requeue attempts each burned real wall time on a real node.  A contrary ruling --
    that "distinct task identities" collapses a job id's attempts to one figure
    rather than only its several representations -- would change this function and
    nothing else.

    The GPU/CPU split is per attempt, not per job id, because a requeue can land on
    a different partition than the attempt before it.
    """
    gpu_seconds = 0.0
    cpu_seconds = 0.0
    for attempt in attempts:
        if attempt.is_gpu:
            gpu_seconds += attempt.elapsed_seconds
        else:
            cpu_seconds += attempt.elapsed_seconds
    return gpu_seconds, cpu_seconds


def _calculate_spend(
    attempts: dict[AttemptKey, AttemptRecord],
) -> dict[str, object]:
    charged = [attempt for attempt in attempts.values() if attempt.counted]
    gpu_seconds, cpu_seconds = _sum_charged_seconds(charged)
    by_state: Counter[str] = Counter()
    attempts_by_task_id: Counter[str] = Counter()
    for attempt in charged:
        by_state[attempt.state] += 1
        attempts_by_task_id[attempt.task_id] += 1

    task_ids = sorted(attempts_by_task_id)
    return {
        "gpu_task_hours": gpu_seconds / 3600.0,
        "cpu_task_hours": cpu_seconds / 3600.0,
        "task_count": len(task_ids),
        "attempt_count": len(charged),
        "metered_task_ids": task_ids,
        "attempts_by_task_id": {
            task_id: attempts_by_task_id[task_id] for task_id in task_ids
        },
        # Per ATTEMPT, so these sum to attempt_count rather than to task_count: a
        # requeued job is REQUEUED many times and NODE_FAIL once, and collapsing that
        # to one state per job id would have to invent which attempt spoke for it.
        "by_state": dict(sorted(by_state.items())),
    }


def _fired_status(
    *, now: datetime, gpu_task_hours: float, cpu_task_hours: float
) -> dict[str, bool]:
    date_fired = now >= STOP_DATE_UTC
    gpu_fired = gpu_task_hours >= GPU_TASK_HOURS_CEILING
    cpu_fired = cpu_task_hours >= CPU_TASK_HOURS_CEILING
    return {
        "date": date_fired,
        "gpu": gpu_fired,
        "cpu": cpu_fired,
        "any": date_fired or gpu_fired or cpu_fired,
    }


def build_receipt(
    raw_text: str,
    *,
    now: datetime,
    source_kind: str,
    source_location: str,
) -> dict[str, object]:
    """Build an R5 receipt from raw `sacct` text.

    Parameters
    ----------
    raw_text : str
        Headerless, pipe-delimited output using `SACCT_FIELDS` in order.
    now : datetime
        Timezone-aware measurement instant.
    source_kind : str
        Either ``"sacct"`` or ``"file"``.
    source_location : str
        Executed command or input file path recorded as provenance.

    Returns
    -------
    dict[str, object]
        Schema-version-2 measurement receipt.

    Raises
    ------
    MeterError
        If the source metadata or accounting dump is invalid.
    """
    if source_kind not in {"sacct", "file"}:
        raise MeterError(f"invalid source kind: {source_kind!r}")
    if not source_location:
        raise MeterError("source location cannot be empty")
    now_utc = parse_iso_utc(format_iso_utc(now))
    spend = _calculate_spend(_parse_sacct_dump(raw_text))
    gpu_hours = float(spend["gpu_task_hours"])
    cpu_hours = float(spend["cpu_task_hours"])
    return {
        # 2: attempts are metered and summed, and `spend` carries attempt_count and
        # attempts_by_task_id.  A version-1 receipt counted at most one attempt per
        # job id, so it is refused rather than migrated -- see `_validate_receipt`.
        "schema_version": 2,
        "decision_record": DECISION_RECORD,
        "t0_utc": T0_UTC_TEXT,
        "stop_date_utc": STOP_DATE_UTC_TEXT,
        "ceilings": {
            "gpu_task_hours": GPU_TASK_HOURS_CEILING,
            "cpu_task_hours": CPU_TASK_HOURS_CEILING,
        },
        "unit": UNIT,
        "measured_at_utc": format_iso_utc(now_utc),
        "measured_on_host": socket.gethostname(),
        "source": {
            "kind": source_kind,
            "argv_or_path": source_location,
            "raw_sha256": hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
        },
        "spend": spend,
        "fired": _fired_status(
            now=now_utc,
            gpu_task_hours=gpu_hours,
            cpu_task_hours=cpu_hours,
        ),
        "headroom": {
            "gpu_task_hours": GPU_TASK_HOURS_CEILING - gpu_hours,
            "cpu_task_hours": CPU_TASK_HOURS_CEILING - cpu_hours,
        },
    }


def _sacct_argv() -> list[str]:
    # `-X` (--allocations) keeps step rows out, and `-D` (--duplicates) is what makes
    # a requeued job's EARLIER execution attempts visible at all: without it Slurm
    # returns only the most recent record, which under-counted one self-requeueing
    # waker job as 6 s instead of 45 325 s.  The two compose on Perlmutter.
    #
    # NERSC refuses any sacct window wider than 30 days ("Too wide of a date range in
    # query"; the limit is on the SPAN, not the lookback).  This query spans t0 -> now,
    # so it crosses 30 days at 2026-10-02T13:44:27Z -- 2 d 13 h 44 m 27 s AFTER the R5
    # stop date, i.e. outside the campaign window.  After that instant sacct errors and
    # the meter fails CLOSED (no receipt, `check` returns 4).  Chunking is deliberately not
    # implemented; see FINDING-20260906-r5-meter-undercounted-requeue-attempts.md for
    # the one act that must happen before it: the final measurement of jobs still
    # running at the stop.
    return [
        "sacct",
        "--user",
        getpass.getuser(),
        "-X",
        "-D",
        "--parsable2",
        "--noheader",
        "--starttime",
        T0_UTC.strftime("%Y-%m-%dT%H:%M:%S"),
        "--endtime",
        "now",
        f"--format={','.join(SACCT_FIELDS)}",
    ]


def _read_source(from_file: Path | None) -> tuple[str, str, str]:
    if from_file is not None:
        try:
            raw_bytes = from_file.read_bytes()
        except OSError as exc:
            raise MeterError(f"cannot read accounting dump {from_file}: {exc}") from exc
        try:
            raw_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise MeterError(f"accounting dump is not UTF-8: {from_file}") from exc
        return raw_text, "file", str(from_file)

    argv = _sacct_argv()
    environment = os.environ.copy()
    environment.update(
        {
            "TZ": "UTC",
            "SLURM_TIME_FORMAT": "%Y-%m-%dT%H:%M:%S",
        }
    )
    try:
        result = subprocess.run(
            argv,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
        )
    except FileNotFoundError as exc:
        raise MeterError("sacct is not available on this host") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip()
        raise MeterError(f"sacct failed: {detail or f'exit {exc.returncode}'}") from exc
    try:
        raw_text = result.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MeterError("sacct output is not UTF-8") from exc
    return raw_text, "sacct", shlex.join(argv)


def _atomic_write_json(path: Path, receipt: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(receipt, indent=2) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            temporary_name = handle.name
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass


def measure(
    *,
    from_file: Path | None,
    now: datetime,
    write_path: Path | None,
) -> dict[str, object]:
    """Measure cumulative R5 spend and optionally persist its receipt.

    Parameters
    ----------
    from_file : pathlib.Path or None
        Captured `sacct` dump. If omitted, query `sacct` for the current user.
    now : datetime
        Timezone-aware measurement instant.
    write_path : pathlib.Path or None
        Destination for an atomic JSON write. No file is written when omitted.

    Returns
    -------
    dict[str, object]
        Schema-version-2 measurement receipt.
    """
    raw_text, source_kind, source_location = _read_source(from_file)
    receipt = build_receipt(
        raw_text,
        now=now,
        source_kind=source_kind,
        source_location=source_location,
    )
    if write_path is not None:
        _atomic_write_json(write_path, receipt)
    return receipt


def _require_exact_keys(
    value: object, keys: set[str], *, location: str
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise MeterError(f"{location} does not have the schema-version-2 keys")
    return value


def _require_number(value: object, *, location: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MeterError(f"{location} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise MeterError(f"{location} must be a finite number")
    return number


def _validate_receipt(receipt: object) -> tuple[datetime, float, float]:
    top = _require_exact_keys(
        receipt,
        {
            "schema_version",
            "decision_record",
            "t0_utc",
            "stop_date_utc",
            "ceilings",
            "unit",
            "measured_at_utc",
            "measured_on_host",
            "source",
            "spend",
            "fired",
            "headroom",
        },
        location="receipt",
    )
    version = top["schema_version"]
    # A version-1 receipt is not merely an older shape: it keyed spend by job id and
    # therefore counted at most ONE execution attempt per requeued job.  Accepting one
    # would admit an under-count against a prohibition, so it is refused, not migrated.
    if type(version) is int and version == 1:
        raise MeterError(
            "receipt schema_version 1 is refused: it counted at most one execution "
            "attempt per job id, so it under-counts every requeued job and is not "
            "valid R5 accounting; re-measure with this version of the meter"
        )
    if type(version) is not int or version != 2:
        raise MeterError("receipt schema_version does not match the R5 schema")
    fixed_values = {
        "decision_record": DECISION_RECORD,
        "t0_utc": T0_UTC_TEXT,
        "stop_date_utc": STOP_DATE_UTC_TEXT,
        "unit": UNIT,
    }
    for key, expected in fixed_values.items():
        if top[key] != expected:
            raise MeterError(f"receipt {key} does not match the R5 schema")

    ceilings = _require_exact_keys(
        top["ceilings"],
        {"gpu_task_hours", "cpu_task_hours"},
        location="ceilings",
    )
    if (
        _require_number(ceilings["gpu_task_hours"], location="GPU ceiling")
        != GPU_TASK_HOURS_CEILING
        or _require_number(ceilings["cpu_task_hours"], location="CPU ceiling")
        != CPU_TASK_HOURS_CEILING
    ):
        raise MeterError("receipt ceilings do not match R5")

    if not isinstance(top["measured_on_host"], str) or not top["measured_on_host"]:
        raise MeterError("measured_on_host must be a non-empty string")
    if not isinstance(top["measured_at_utc"], str):
        raise MeterError("measured_at_utc must be an ISO timestamp string")
    measured_at = parse_iso_utc(top["measured_at_utc"])

    source = _require_exact_keys(
        top["source"], {"kind", "argv_or_path", "raw_sha256"}, location="source"
    )
    if source["kind"] not in {"sacct", "file"}:
        raise MeterError("source kind must be sacct or file")
    if not isinstance(source["argv_or_path"], str) or not source["argv_or_path"]:
        raise MeterError("source argv_or_path must be a non-empty string")
    if not isinstance(source["raw_sha256"], str) or SHA256_RE.fullmatch(
        source["raw_sha256"]
    ) is None:
        raise MeterError("source raw_sha256 must be a lowercase SHA-256 digest")

    spend = _require_exact_keys(
        top["spend"],
        {
            "gpu_task_hours",
            "cpu_task_hours",
            "task_count",
            "attempt_count",
            "metered_task_ids",
            "attempts_by_task_id",
            "by_state",
        },
        location="spend",
    )
    gpu_hours = _require_number(
        spend["gpu_task_hours"], location="spend.gpu_task_hours"
    )
    cpu_hours = _require_number(
        spend["cpu_task_hours"], location="spend.cpu_task_hours"
    )
    if gpu_hours < 0.0 or cpu_hours < 0.0:
        raise MeterError("receipt spend cannot be negative")
    task_count = spend["task_count"]
    if (
        isinstance(task_count, bool)
        or not isinstance(task_count, int)
        or task_count < 0
    ):
        raise MeterError("spend.task_count must be a non-negative integer")
    task_ids = spend["metered_task_ids"]
    if (
        not isinstance(task_ids, list)
        or any(not isinstance(task_id, str) for task_id in task_ids)
        or task_ids != sorted(set(task_ids))
        or any(TASK_ID_RE.fullmatch(task_id) is None for task_id in task_ids)
        or len(task_ids) != task_count
    ):
        raise MeterError("metered_task_ids must be sorted, unique task identities")
    # SCHEDULER TASK IDENTITY vs EXECUTION-ATTEMPT IDENTITY.  `metered_task_ids` and
    # `task_count` answer "was this scheduler task's spend counted" -- the question
    # campaignctl's reservation release asks, which is why the ids stay BARE.
    # `attempts_by_task_id` and `attempt_count` answer "how many of its executions
    # were charged".  One job id may now carry many attempts, so the second is not
    # derivable from the first.
    attempt_count = spend["attempt_count"]
    if (
        isinstance(attempt_count, bool)
        or not isinstance(attempt_count, int)
        or attempt_count < 0
    ):
        raise MeterError("spend.attempt_count must be a non-negative integer")
    attempts_by_task_id = spend["attempts_by_task_id"]
    if (
        not isinstance(attempts_by_task_id, dict)
        or list(attempts_by_task_id) != task_ids
        or any(
            isinstance(count, bool) or not isinstance(count, int) or count < 1
            for count in attempts_by_task_id.values()
        )
        or sum(cast(dict[str, int], attempts_by_task_id).values()) != attempt_count
    ):
        raise MeterError(
            "spend.attempts_by_task_id must map every metered task id, in sorted "
            "order, to a positive attempt count summing to attempt_count"
        )
    by_state = spend["by_state"]
    if not isinstance(by_state, dict) or any(
        not isinstance(state, str)
        or not state
        or isinstance(count, bool)
        or not isinstance(count, int)
        or count < 0
        for state, count in by_state.items()
    ):
        raise MeterError("spend.by_state must contain non-negative integer counts")
    state_counts = cast(dict[str, int], by_state)
    # Per attempt, so this ties to attempt_count.  A requeued job contributes one
    # entry per execution.
    if sum(state_counts.values()) != attempt_count:
        raise MeterError("spend.by_state counts do not match attempt_count")

    expected_fired = _fired_status(
        now=measured_at,
        gpu_task_hours=gpu_hours,
        cpu_task_hours=cpu_hours,
    )
    fired = _require_exact_keys(
        top["fired"], {"date", "gpu", "cpu", "any"}, location="fired"
    )
    if any(type(value) is not bool for value in fired.values()):
        raise MeterError("receipt fired flags must be booleans")
    if fired != expected_fired:
        raise MeterError("receipt fired flags are inconsistent with its measurement")

    headroom = _require_exact_keys(
        top["headroom"],
        {"gpu_task_hours", "cpu_task_hours"},
        location="headroom",
    )
    gpu_headroom = _require_number(
        headroom["gpu_task_hours"], location="headroom.gpu_task_hours"
    )
    cpu_headroom = _require_number(
        headroom["cpu_task_hours"], location="headroom.cpu_task_hours"
    )
    if not math.isclose(
        gpu_headroom,
        GPU_TASK_HOURS_CEILING - gpu_hours,
        rel_tol=0.0,
        abs_tol=1e-12,
    ) or not math.isclose(
        cpu_headroom,
        CPU_TASK_HOURS_CEILING - cpu_hours,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise MeterError("receipt headroom is inconsistent with its spend")
    return measured_at, gpu_hours, cpu_hours


def check_receipt(
    receipt_path: Path,
    *,
    now: datetime,
    max_age_hours: float,
    proposed_gpu_task_hours: float,
    proposed_cpu_task_hours: float,
) -> int:
    """Check whether R5 permits another submission under declared maximum cost.

    Parameters
    ----------
    receipt_path : pathlib.Path
        Measurement receipt to validate.
    now : datetime
        Timezone-aware check instant.
    max_age_hours : float
        Greatest permitted receipt age in hours.
    proposed_gpu_task_hours : float
        Declared maximum GPU task-hours for the proposed run.
    proposed_cpu_task_hours : float
        Declared maximum CPU task-hours for the proposed run.

    Returns
    -------
    int
        ``0`` if submission remains possible, ``3`` if the stop fired,
        ``4`` for a missing, stale, or malformed receipt, or ``5`` if the
        proposal would reach a ceiling.

    Notes
    -----
    A zero result only evaluates the R5 boundary. It grants no authority.
    """
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        measured_at, gpu_hours, cpu_hours = _validate_receipt(receipt)
    except (OSError, UnicodeError, json.JSONDecodeError, MeterError) as exc:
        print(f"R5 check failed closed: {exc}", file=sys.stderr)
        return 4

    now_utc = parse_iso_utc(format_iso_utc(now))
    age = now_utc - measured_at
    if age < timedelta(0):
        print("R5 check failed closed: receipt is dated in the future", file=sys.stderr)
        return 4
    if age > timedelta(hours=max_age_hours):
        print("R5 check failed closed: receipt is stale", file=sys.stderr)
        return 4

    if _fired_status(
        now=now_utc,
        gpu_task_hours=gpu_hours,
        cpu_task_hours=cpu_hours,
    )["any"]:
        print("R5 stop has fired", file=sys.stderr)
        return 3

    if (
        gpu_hours + proposed_gpu_task_hours >= GPU_TASK_HOURS_CEILING
        or cpu_hours + proposed_cpu_task_hours >= CPU_TASK_HOURS_CEILING
    ):
        print("R5 proposal would reach or exceed a ceiling", file=sys.stderr)
        return 5
    return 0


def _non_negative_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if not math.isfinite(parsed) or parsed < 0.0:
        raise argparse.ArgumentTypeError("must be a finite, non-negative number")
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run bundled positive and negative controls",
    )
    subparsers = parser.add_subparsers(dest="command")

    measure_parser = subparsers.add_parser("measure", help="measure cumulative spend")
    measure_parser.add_argument("--from-file", type=Path)
    measure_parser.add_argument("--now", type=parse_iso_utc)
    measure_parser.add_argument("--write", type=Path)

    check_parser = subparsers.add_parser("check", help="check the stop boundary")
    check_parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT_PATH)
    check_parser.add_argument("--now", type=parse_iso_utc)
    check_parser.add_argument(
        "--max-age-hours", type=_non_negative_float, default=24.0
    )
    check_parser.add_argument(
        "--gpu-task-hours", type=_non_negative_float, default=0.0
    )
    check_parser.add_argument(
        "--cpu-task-hours", type=_non_negative_float, default=0.0
    )
    return parser


def _run_self_test() -> bool:
    rows = [
        "1|at-boundary|COMPLETED|3600|regular|2026-09-02T13:44:27|"
        "2026-09-02T14:44:27|cpu=32,gres/gpu=1",
        "1|duplicate|COMPLETED|3600|regular|2026-09-02T13:44:27|"
        "2026-09-02T14:44:27|cpu=32,gres/gpu=1",
        "1.batch|step|COMPLETED|3600|regular|2026-09-02T13:44:27|"
        "2026-09-02T14:44:27|cpu=32,gres/gpu=1",
        "2_7|failed|FAILED|1800|regular|2026-09-02T13:44:28|"
        "2026-09-02T14:14:28|cpu=1",
        "3|straddling|COMPLETED|3600|regular|2026-09-02T13:44:26|"
        "2026-09-02T14:44:26|gres/gpu:a100=1",
        "4|pending|PENDING|0|regular|Unknown|Unknown|cpu=1",
        "5|requeued-first|REQUEUED|60|regular|2026-09-02T14:00:00|"
        "2026-09-02T14:01:00|cpu=2",
        "5|requeued-again|NODE_FAIL|120|regular|2026-09-02T15:00:00|"
        "2026-09-02T15:02:00|cpu=2",
    ]
    receipt = build_receipt(
        "\n".join(rows) + "\n",
        now=parse_iso_utc("2026-09-10T00:00:00Z"),
        source_kind="file",
        source_location="self-test.sacct",
    )
    spend = receipt["spend"]
    if not isinstance(spend, dict):
        return False
    positive_control = (
        spend["task_count"] == 4
        and spend["attempt_count"] == 5
        and spend["gpu_task_hours"] == (3600 + 3599) / 3600.0
        # Job id 5 requeued once: BOTH attempts are charged, so 1800 + 60 + 120.
        and spend["cpu_task_hours"] == (1800 + 60 + 120) / 3600.0
        and spend["attempts_by_task_id"] == {"1": 1, "2_7": 1, "3": 1, "5": 2}
        and spend["by_state"]
        == {"COMPLETED": 2, "FAILED": 1, "NODE_FAIL": 1, "REQUEUED": 1}
    )
    negative_control = not _fired_status(
        now=parse_iso_utc("2026-09-29T23:59:59Z"),
        gpu_task_hours=499.999,
        cpu_task_hours=499.999,
    )["any"] and _fired_status(
        now=parse_iso_utc("2026-09-30T00:00:00Z"),
        gpu_task_hours=0.0,
        cpu_task_hours=0.0,
    )["any"]
    try:
        _parse_sacct_dump("invalid|row\n")
    except MeterError:
        malformed_rejected = True
    else:
        malformed_rejected = False
    try:
        # One attempt, two observations that disagree about what it spent.
        _parse_sacct_dump(
            "6|a|COMPLETED|60|regular|2026-09-02T14:00:00|"
            "2026-09-02T14:01:00|cpu=1\n"
            "6|b|COMPLETED|61|regular|2026-09-02T14:00:00|"
            "2026-09-02T14:01:00|cpu=1\n"
        )
    except MeterError:
        conflict_rejected = True
    else:
        conflict_rejected = False
    version_one = dict(receipt)
    version_one["schema_version"] = 1
    try:
        _validate_receipt(version_one)
    except MeterError as exc:
        version_one_refused = "schema_version 1 is refused" in str(exc)
    else:
        version_one_refused = False
    return (
        positive_control
        and negative_control
        and malformed_rejected
        and conflict_rejected
        and version_one_refused
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line meter.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Arguments without the program name. Defaults to `sys.argv[1:]`.

    Returns
    -------
    int
        Process exit code.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        if args.command is not None:
            parser.error("--self-test cannot be combined with a command")
        passed = _run_self_test()
        print(f"r5_meter self-test: {'PASS' if passed else 'FAIL'}")
        return 0 if passed else 1
    if args.command is None:
        parser.error("a command is required")

    now = args.now or datetime.now(timezone.utc)
    if args.command == "measure":
        try:
            receipt = measure(
                from_file=args.from_file,
                now=now,
                write_path=args.write,
            )
        except (MeterError, OSError) as exc:
            print(f"R5 measurement failed: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(receipt, indent=2))
        return 0
    return check_receipt(
        args.receipt,
        now=now,
        max_age_hours=args.max_age_hours,
        proposed_gpu_task_hours=args.gpu_task_hours,
        proposed_cpu_task_hours=args.cpu_task_hours,
    )


if __name__ == "__main__":
    sys.exit(main())
