#!/usr/bin/env python3
"""Run one pilot step under the authorized caps and record it in the budget ledger.

Caps (authorization of 2026-10-11): 36,000 CPU core-seconds of scientific
computation and 10,000 generated events in total, across every run, failure,
review and rerun. ``--cpu-cap`` / ``--event-cap`` may only lower them.

Budget is reserved before launch (repair of 2026-10-11, after review found that
``ulimit -t`` alone is a per-process limit, not a cap on a process tree):

* Under an exclusive ``flock`` on ``<ledger>.lock`` the launcher sums the ledger,
  counting every reservation that has no settlement at its full reserved amount,
  refuses if the request would exceed either cap, and appends a ``reserve``
  record with ``fsync`` before anything is launched. Concurrent requests
  serialize on the lock, so they cannot both pass on the same totals.
* A reservation is released only by a ``settle`` record written after the job
  has been waited for. If the launcher crashes or is killed, nothing settles and
  the full reservation stays charged. A launcher that is interrupted by a signal
  kills the job and settles at the full reservation. A ledger line that does not
  parse, an unknown record kind, or a settlement without its reservation stops
  every launch until a person inspects the ledger.

Aggregate CPU bound. One execution mode is supported: a single process.
``sandbox-exec`` (macOS) denies ``process-fork`` (fork, vfork and posix_spawn),
so the job cannot create children itself. The profile otherwise allows default
operations, so processes started on the job's behalf by launchd, XPC or other
system services are outside this bound (not relevant to NuWro, not tested); a preflight probe must show the fork denied
inside the same profile, and any other platform is refused. A job that needs
children fails closed inside its reservation. The job's CPU is then bounded in
two layers:

1. While the launcher lives, a watchdog polls the job's CPU time (``ps``) and
   SIGKILLs it once job CPU plus the launcher's own measured child CPU (preflight
   and ``ps`` calls) reaches N = ``--cpu-seconds``. The poll interval shrinks as
   the remainder shrinks, so the overshoot should be at most about one minimum
   interval on every core; ``WATCHDOG_MARGIN_S`` is an engineering margin, not a
   derived bound (measured overshoots: 0.02-0.03 s single-threaded, 0.25 s for a
   10-thread job in the repair review). SIGKILL cannot be caught.
2. ``ulimit -t N`` (RLIMIT_CPU) stays set. The macOS kernel enforces it only by
   SIGXCPU: a process that ignores, catches or blocks SIGXCPU is not stopped at
   either the soft or the hard limit (REPAIR.md, check L5 and probe P1).

The reservation is N + ``WATCHDOG_MARGIN_S``. If the launcher dies, its
reservation stays charged in full and a ``start`` record names the job; every
later launch is refused while that job is still alive (or while its liveness
cannot be determined). SIGINT/TERM/HUP are blocked between ``Popen`` and the
``start`` record; a SIGKILL of the launcher inside that window leaves a job with
no ``start`` record, whose reservation still counts in full. The orphan itself is
then bounded only by layer 2, i.e. only if it leaves SIGXCPU at its default
action. That residual is not certified.

After the job, the measured user+sys CPU of the waited children (the job is one
process, so this is exact) and the sampled events (dump lines; the full
allotment when the count is unknown) are settled.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import resource
import shlex
import shutil
import signal
import subprocess
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path

CPU_CAP_S = 36_000.0
EVENT_CAP = 10_000
NCPU = os.cpu_count() or 1
POLL_MIN_S, POLL_MAX_S = 0.05, 1.0
# engineering margin: one minimum poll interval (plus ps latency, taken equal) on every
# core, and 0.5 s slack; not a derived bound
WATCHDOG_MARGIN_S = NCPU * 2 * POLL_MIN_S + 0.5
SANDBOX_EXEC = "/usr/bin/sandbox-exec"
SANDBOX_PROFILE = "(version 1)(allow default)(deny process-fork)"


class LedgerError(RuntimeError):
    """The ledger cannot be read unambiguously; every launch is refused."""


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


@contextmanager
def locked(ledger: Path):
    fd = os.open(f"{ledger}.lock", os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)  # closing the descriptor releases the lock, also on crash


def append_durable(ledger: Path, rec: dict) -> None:
    """One ``write`` of one full line, then ``fsync`` (and the directory on creation)."""
    new = not ledger.exists()
    fd = os.open(ledger, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, (json.dumps(rec) + "\n").encode())
        if hasattr(fcntl, "F_FULLFSYNC"):  # macOS: plain fsync does not reach stable storage
            fcntl.fcntl(fd, fcntl.F_FULLFSYNC)
        else:
            os.fsync(fd)
    finally:
        os.close(fd)
    if new:
        dfd = os.open(ledger.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)


def ledger_totals(ledger: Path) -> tuple[float, int, list[tuple[str, tuple[int, str] | None]]]:
    """Charged CPU-s and events, with the unsettled reservations and their job (pid, start).

    Legacy records (no ``kind``; written before the repair) are settled runs.
    An unsettled reservation counts at its full reserved amount.
    """
    cpu, events = 0.0, 0
    open_res: dict[str, dict] = {}
    settled: set[str] = set()
    if not ledger.exists():
        return cpu, events, []
    for n, line in enumerate(ledger.read_text().split("\n"), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
            kind = rec.get("kind")
            if kind is None:
                cpu += float(rec["cpu_charged_s"])
                events += int(rec["events_charged"])
            elif kind == "reserve":
                rid = rec["reservation_id"]
                if rid in open_res or rid in settled:
                    raise LedgerError(f"line {n}: duplicate reservation {rid}")
                open_res[rid] = rec
            elif kind == "start":
                rid = rec["reservation_id"]
                if rid not in open_res or "_start" in open_res[rid]:
                    raise LedgerError(f"line {n}: start record without open reservation {rid}")
                open_res[rid]["_start"] = (int(rec["job_pid"]), str(rec["job_lstart"]))
            elif kind == "settle":
                rid = rec["reservation_id"]
                if rid not in open_res:
                    raise LedgerError(f"line {n}: settlement without open reservation {rid}")
                del open_res[rid]
                settled.add(rid)
                cpu += float(rec["cpu_charged_s"])
                events += int(rec["events_charged"])
            else:
                raise LedgerError(f"line {n}: unknown record kind {kind!r}")
        except LedgerError:
            raise
        except (ValueError, KeyError, TypeError) as exc:
            raise LedgerError(f"line {n}: unreadable ledger record ({exc})") from exc
    for rec in open_res.values():
        cpu += float(rec["cpu_reserved_s"])
        events += int(rec["events_reserved"])
    return cpu, events, sorted((rid, rec.get("_start")) for rid, rec in open_res.items())


def reserve(ledger: Path, run_id: str, cpu_s: float, n_events: int, cpu_cap: float,
            event_cap: int, extra: dict | None = None) -> dict:
    """Append a reservation under the lock, or raise PermissionError."""
    with locked(ledger):
        used_cpu, used_events, unsettled = ledger_totals(ledger)
        alive = [(rid, job) for rid, job in unsettled if job is not None and job_alive(*job)]
        if alive:
            raise PermissionError(f"REFUSED {run_id}: the job of unsettled reservation(s) is still "
                                  f"running: {alive}")
        if used_events + n_events > event_cap or used_cpu + cpu_s > cpu_cap:
            raise PermissionError(
                f"REFUSED {run_id}: charged {used_events} events / {used_cpu:.3f} s "
                f"({len(unsettled)} unsettled reservations at full value); request "
                f"{n_events} / {cpu_s:.3f} s; caps {event_cap} / {cpu_cap:.3f} s")
        rec = {"kind": "reserve", "reservation_id": uuid.uuid4().hex, "run_id": run_id,
               "time_utc": now(), "launcher_pid": os.getpid(),
               "cpu_reserved_s": cpu_s, "events_reserved": n_events, **(extra or {})}
        append_durable(ledger, rec)
        return rec


def settle(ledger: Path, res: dict, cpu_s: float, n_events: int, extra: dict) -> dict:
    with locked(ledger):
        rec = {"kind": "settle", "reservation_id": res["reservation_id"], "run_id": res["run_id"],
               "time_utc": now(), "cpu_charged_s": round(cpu_s, 3), "events_charged": n_events,
               **extra}
        append_durable(ledger, rec)
        return rec


def count_events(dump: Path | None) -> int | None:
    if dump is None or not dump.exists():
        return None
    with dump.open() as fh:
        return sum(1 for line in fh if line.strip() and not line.startswith("#"))


def _ps(pid: int, field: str) -> str:
    return subprocess.run(["/bin/ps", "-o", f"{field}=", "-p", str(pid)],
                          capture_output=True, text=True).stdout.strip()


def job_cpu(pid: int) -> float | None:
    """CPU time of a live process from ``ps -o time`` ([[D-]H:]M:SS.cc), or None."""
    out = _ps(pid, "time")
    if not out:
        return None
    secs = 0.0
    for part in out.replace("-", ":").split(":"):
        secs = secs * 60 + float(part)
    return secs


def job_alive(pid: int, lstart: str) -> bool:
    """True if the recorded process may still be running; fails closed.

    Dead only if the pid does not exist, or exists with a different start time."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass  # exists, owned by someone else
    now_lstart = _ps(pid, "lstart")
    return now_lstart == lstart or not now_lstart


def record_start(ledger: Path, res: dict, pid: int) -> None:
    with locked(ledger):
        append_durable(ledger, {"kind": "start", "reservation_id": res["reservation_id"],
                                "run_id": res["run_id"], "time_utc": now(), "job_pid": pid,
                                "job_lstart": _ps(pid, "lstart")})


def children_cpu() -> float:
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    return ru.ru_utime + ru.ru_stime


class Interrupted(Exception):
    pass


def _raise_interrupted(signum, _frame):
    raise Interrupted(signal.Signals(signum).name)


def fork_denied_preflight() -> bool:
    """True only if the profile runs a non-forking command but denies a fork."""
    def rc(argv):
        return subprocess.run([SANDBOX_EXEC, "-p", SANDBOX_PROFILE, *argv],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    return rc(["/usr/bin/true"]) == 0 and rc(["/bin/sh", "-c", "/usr/bin/true; /usr/bin/true"]) != 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--events", type=int, required=True, help="event allotment (0 for no sampling)")
    ap.add_argument("--cpu-seconds", type=int, required=True, help="CPU allotment (integer ulimit)")
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--dump", type=Path, help="event dump whose lines count sampled events")
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--cpu-cap", type=float, default=CPU_CAP_S, help="may only lower the cap")
    ap.add_argument("--event-cap", type=int, default=EVENT_CAP, help="may only lower the cap")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)
    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        ap.error("no command")
    if args.cpu_seconds < 1 or args.events < 0:
        ap.error("--cpu-seconds must be >= 1 and --events >= 0")
    cpu_cap = min(args.cpu_cap, CPU_CAP_S)
    event_cap = min(args.event_cap, EVENT_CAP)
    if sys.platform != "darwin" or not Path(SANDBOX_EXEC).exists() or shutil.which("bash") is None:
        print("[pilot_run] REFUSED: unsupported execution mode (needs macOS sandbox-exec)", file=sys.stderr)
        return 4

    cpu_reserved = args.cpu_seconds + WATCHDOG_MARGIN_S
    try:
        res = reserve(args.ledger, args.run_id, cpu_reserved, args.events, cpu_cap, event_cap,
                      {"cpu_ulimit_s": args.cpu_seconds, "cmd": cmd, "workdir": str(args.workdir)})
    except (PermissionError, LedgerError) as exc:
        print(f"[pilot_run] {exc}", file=sys.stderr)
        return 3

    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, _raise_interrupted)
    before = children_cpu()
    proc = None
    try:
        if not fork_denied_preflight():
            settle(args.ledger, res, children_cpu() - before, 0,
                   {"rc": None, "basis": "measured", "status": "refused: fork-denial preflight forked"})
            print("[pilot_run] REFUSED: the sandbox profile did not deny fork", file=sys.stderr)
            return 4
        env = dict(os.environ)
        env["NUWRO_PILOT_EVENT_CAP"] = str(args.events)
        if args.dump:
            env["NUWRO_PILOT_DUMP"] = str(args.dump.resolve())
        shell = (f"ulimit -t {args.cpu_seconds} || exit 125; "
                 f"exec {SANDBOX_EXEC} -p {shlex.quote(SANDBOX_PROFILE)} {shlex.join(cmd)}")
        args.workdir.mkdir(parents=True, exist_ok=True)
        start = dt.datetime.now(dt.timezone.utc)
        status = "completed"
        with args.log.open("w") as log:
            blocked = {signal.SIGINT, signal.SIGTERM, signal.SIGHUP}
            signal.pthread_sigmask(signal.SIG_BLOCK, blocked)
            try:
                proc = subprocess.Popen(["/bin/bash", "-c", shell], cwd=args.workdir, env=env,
                                        stdout=log, stderr=subprocess.STDOUT,
                                        preexec_fn=lambda: signal.pthread_sigmask(signal.SIG_UNBLOCK, blocked))
                record_start(args.ledger, res, proc.pid)
            finally:
                signal.pthread_sigmask(signal.SIG_UNBLOCK, blocked)  # a pending signal lands here
            interval = POLL_MIN_S
            while True:  # watchdog (layer 1)
                try:
                    rc = proc.wait(timeout=interval)
                    break
                except subprocess.TimeoutExpired:
                    pass
                used = (job_cpu(proc.pid) or 0.0) + children_cpu() - before
                if used >= args.cpu_seconds:
                    proc.kill()
                    rc = proc.wait()
                    status = "killed by watchdog: CPU allotment reached"
                    break
                interval = min(POLL_MAX_S, max(POLL_MIN_S, (args.cpu_seconds - used) / (2 * NCPU)))
        end = dt.datetime.now(dt.timezone.utc)
    except Interrupted as exc:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait()
        rec = settle(args.ledger, res, cpu_reserved, args.events,
                     {"rc": None, "basis": "full-reservation", "status": f"interrupted by {exc}"})
        print(json.dumps(rec))
        return 130
    cpu = children_cpu() - before
    sampled = count_events(args.dump)
    events_charged = args.events if (sampled is None and args.events > 0) else (sampled or 0)
    rec = settle(args.ledger, res, cpu, events_charged, {
        "rc": rc, "basis": "measured",
        "status": status if (status != "completed" or rc >= 0) else f"killed by signal {-rc}",
        "start_utc": start.isoformat(timespec="seconds"), "end_utc": end.isoformat(timespec="seconds"),
        "wall_s": round((end - start).total_seconds(), 3), "events_sampled_dumped": sampled,
        "cpu_reached_allotment": cpu >= args.cpu_seconds})
    print(json.dumps(rec))
    return rc


if __name__ == "__main__":
    sys.exit(main())
