#!/usr/bin/env python3
"""Measure and enforce the R5 date and task-hour stop boundaries."""

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
    "task-hours: sum of post-t0 ElapsedRaw over distinct task identities; "
    "tasks straddling t0 are clipped at t0; .batch/.extern/step and "
    "array-bracket rows excluded"
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
class TaskRecord:
    """One distinct, metered Slurm task identity.

    Parameters
    ----------
    task_id : str
        Plain Slurm job ID or concrete array-task ID.
    state : str
        Normalized Slurm state.
    elapsed_seconds : float
        Elapsed wall-clock seconds charged to this task.
    partition : str
        Slurm partition, used as a secondary GPU classification signal.
    is_gpu : bool
        Whether AllocTRES or the partition identifies a GPU allocation.
    start : datetime
        Task start instant in UTC.
    """

    task_id: str
    state: str
    elapsed_seconds: float
    partition: str
    is_gpu: bool
    start: datetime


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


def _parse_sacct_dump(raw_text: str) -> dict[str, TaskRecord]:
    tasks: dict[str, TaskRecord] = {}
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
            _,
            alloc_tres,
        ) = row
        if TASK_ID_RE.fullmatch(job_id) is None:
            continue

        start = _parse_sacct_start(start_text, line_number=line_number)
        if start is None:
            continue

        elapsed_seconds = _parse_elapsed(elapsed_text, line_number=line_number)
        if start < T0_UTC:
            elapsed_seconds = max(
                0.0,
                elapsed_seconds - (T0_UTC - start).total_seconds(),
            )
            if elapsed_seconds == 0.0:
                continue

        is_gpu = _alloc_tres_has_gpu(
            alloc_tres,
            line_number=line_number,
        ) or partition.lower().startswith("gpu")

        record = TaskRecord(
            task_id=job_id,
            state=_normalize_state(state_text, line_number=line_number),
            elapsed_seconds=elapsed_seconds,
            partition=partition,
            is_gpu=is_gpu,
            start=start,
        )
        existing = tasks.get(job_id)
        if existing is None:
            tasks[job_id] = record
            continue
        if (existing.partition, existing.is_gpu, existing.start) != (
            record.partition,
            record.is_gpu,
            record.start,
        ):
            raise MeterError(
                f"line {line_number}: conflicting rows for task identity {job_id}"
            )
        if record.elapsed_seconds > existing.elapsed_seconds:
            tasks[job_id] = record
    return tasks


def _calculate_spend(tasks: dict[str, TaskRecord]) -> dict[str, object]:
    gpu_seconds = 0
    cpu_seconds = 0
    by_state: Counter[str] = Counter()
    for task in tasks.values():
        if task.is_gpu:
            gpu_seconds += task.elapsed_seconds
        else:
            cpu_seconds += task.elapsed_seconds
        by_state[task.state] += 1

    task_ids = sorted(tasks)
    return {
        "gpu_task_hours": gpu_seconds / 3600.0,
        "cpu_task_hours": cpu_seconds / 3600.0,
        "task_count": len(task_ids),
        "metered_task_ids": task_ids,
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
        Schema-version-1 measurement receipt.

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
        "schema_version": 1,
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
    return [
        "sacct",
        "--user",
        getpass.getuser(),
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
        Schema-version-1 measurement receipt.
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
        raise MeterError(f"{location} does not have the schema-version-1 keys")
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
    if type(top["schema_version"]) is not int or top["schema_version"] != 1:
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
            "metered_task_ids",
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
    if sum(state_counts.values()) != task_count:
        raise MeterError("spend.by_state counts do not match task_count")

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
        spend["task_count"] == 3
        and spend["gpu_task_hours"] == (3600 + 3599) / 3600.0
        and spend["cpu_task_hours"] == 0.5
        and spend["by_state"] == {"COMPLETED": 2, "FAILED": 1}
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
    return positive_control and negative_control and malformed_rejected


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
