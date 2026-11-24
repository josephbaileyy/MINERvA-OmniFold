#!/usr/bin/env python3
"""Supervise one P0 step: the worker runs in its own session and process group, and this process stays outside it.

usage: p0_supervise.py DEADLINE RESULT_JSON -- COMMAND [ARG ...]

DEADLINE is an absolute time.monotonic() value, the one deadline the runner computed for the whole chain, so a step
never gets more time than the chain has left. Each pass of the loop reads the clock before it polls the worker and
sleeps only until the next event, so the worker group gets SIGTERM at DEADLINE - TERM_LEAD seconds and SIGKILL at
DEADLINE. A worker reaped at or after DEADLINE never counts as clean. A SIGTERM, SIGINT or SIGHUP sent to this process
is forwarded to the worker group as SIGTERM, with SIGKILL TERM_LEAD seconds later (or at the deadline, if sooner).

The worker is forked by this process and execs only after its group id is in RESULT_JSON.pgid, so the runner can kill
the group if this process is itself killed; if this process dies before that, the child exits without running anything.
On Linux the worker also gets PR_SET_PDEATHSIG SIGKILL (prctl's return checked), so it dies with this process.
After the worker is reaped, anything left in its group is killed with SIGKILL, and this process waits (up to
GROUP_WAIT seconds) until the group is gone. RESULT_JSON is then written atomically, last:
  rc                     the worker's returncode (negative: killed by that signal)
  signal                 the name of the signal that ended the worker, or null
  deadline_signalled     true if killpg succeeded for a deadline TERM or KILL (EPERM is not delivery)
  past_deadline          true if the worker was reaped at or after the deadline
  forwarded              the name of the signal this process received and forwarded, or null
  peak_rss_bytes         the reaped children's peak RSS (ru_maxrss of RUSAGE_CHILDREN, in bytes)
  leftover_group_killed  true if processes were still in the worker's group after it was reaped
  group_gone             true if the group was empty before this record was written
  pgid, deadline, started, ended
Exits 0 only if the worker returned 0 with no deadline signal, no forwarded signal, no leftover, the group gone and the
deadline not passed; otherwise 1. Exits 2 on a usage error or if the deadline has already passed (no worker is
started), and writes no result.
"""

from __future__ import annotations

import json
import os
import resource
import signal
import sys
import time

TERM_LEAD = 30.0
POLL = 0.2
GROUP_WAIT = 10.0
PR_SET_PDEATHSIG = 1
if sys.platform.startswith("linux"):
    import ctypes

    LIBC = ctypes.CDLL(None, use_errno=True)
else:
    LIBC = None


def signal_group(pgid: int, sig: int) -> str:
    """Signal the whole group: "sent" if killpg succeeded, "absent" on ESRCH (no member left), "denied" on EPERM."""
    try:
        os.killpg(pgid, sig)
    except ProcessLookupError:
        return "absent"
    except PermissionError:
        return "denied"
    return "sent"


def group_alive(pgid: int) -> bool:
    """True if the group still has a member. EPERM means a member that cannot be signalled, so the group counts as
    alive, except on macOS, where EPERM is what killpg returns for a group whose only member is an unreaped zombie."""
    answer = signal_group(pgid, 0)
    return answer == "sent" or (answer == "denied" and sys.platform != "darwin")


def wait_group_gone(pgid: int, seconds: float) -> bool:
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if not group_alive(pgid):
            return True
        time.sleep(0.05)
    return not group_alive(pgid)


def peak_rss_bytes() -> int:
    peak = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return peak if sys.platform == "darwin" else peak * 1024  # bytes on macOS, KiB on Linux


def write_atomic(path: str, text: str) -> None:
    with open(path + ".partial", "w", encoding="utf-8") as handle:
        handle.write(text)
    os.replace(path + ".partial", path)


def start_worker(command: list[str], pgid_file: str, deadline: float) -> int:
    """Fork the worker into its own session and group and return its pid (= its pgid).

    The child resets the three forwarded signals, calls setsid, and on Linux sets PR_SET_PDEATHSIG SIGKILL (checking
    prctl's return and that its parent is still this process). It then waits for one byte on a pipe before it execs.
    This process writes that byte only after the child leads its own group and PGID_FILE holds its pgid. If this
    process dies first, the pipe closes and the child exits 127 without running anything, so no worker process exists
    before its group can be found. If the deadline has passed by the time the pgid is published, the byte is not sent
    either; and the child checks the deadline again after the byte arrives, immediately before execvp, so a pause
    between the parent's check and its write cannot start the work late. Either way the child exits 127 and the step
    is reaped after the deadline (a wall-cap STOP)."""
    parent = os.getpid()
    read_end, write_end = os.pipe()
    pid = os.fork()
    if pid == 0:
        try:
            os.close(write_end)
            for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
                signal.signal(number, signal.SIG_DFL)
            os.setsid()
            if LIBC is not None and LIBC.prctl(PR_SET_PDEATHSIG, signal.SIGKILL, 0, 0, 0) != 0:
                os._exit(127)
            if os.getppid() != parent or os.read(read_end, 1) != b"g":
                os._exit(127)
            os.close(read_end)
            if time.monotonic() >= deadline:  # released late (a pause after the parent's check): never start the work
                os._exit(127)
            os.execvp(command[0], command)
        finally:
            os._exit(127)
    os.close(read_end)
    try:
        end = time.monotonic() + 5.0
        while os.getpgid(pid) != pid:  # the child has not called setsid yet
            if time.monotonic() >= end:
                raise RuntimeError("the worker did not lead its own group within 5 s")
            time.sleep(0.001)
        write_atomic(pgid_file, f"{pid}\n")
        if time.monotonic() < deadline:  # never release a worker into an expired step
            os.write(write_end, b"g")
    finally:
        os.close(write_end)
    return pid


def reap(pid: int) -> int | None:
    """The worker's returncode once it has exited (negative: killed by that signal), else None; never blocks."""
    done, status = os.waitpid(pid, os.WNOHANG)
    return os.waitstatus_to_exitcode(status) if done == pid else None


def supervise(deadline: float, result: str, command: list[str]) -> int:
    received: list[int] = []

    def on_signal(number: int, _frame: object) -> None:
        received.append(number)

    for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(number, on_signal)
    started = time.monotonic()
    pgid = start_worker(command, result + ".pgid", deadline)
    term_at = deadline - TERM_LEAD
    deadline_signalled = False
    term_sent = False
    kill_sent = False
    forwarded: int | None = None
    kill_at: float | None = None
    while True:
        now = time.monotonic()
        if received and forwarded is None:
            forwarded = received[0]
            signal_group(pgid, signal.SIGTERM)
            if not kill_sent:
                kill_at = min(now + TERM_LEAD, deadline)
        if now >= term_at and not term_sent:
            term_sent = True
            deadline_signalled |= signal_group(pgid, signal.SIGTERM) == "sent"
        if now >= deadline and not kill_sent:
            kill_sent = True
            kill_at = None  # the deadline KILL also serves a pending forwarded escalation
            deadline_signalled |= signal_group(pgid, signal.SIGKILL) == "sent"
        elif kill_at is not None and now >= kill_at:
            signal_group(pgid, signal.SIGKILL)
            kill_at = None
        returncode = reap(pgid)
        if returncode is not None:
            break
        now = time.monotonic()  # the poll took time: never sleep past an event that came due during it
        pending = (term_at if not term_sent else None, kill_at, deadline if not kill_sent else None)
        due = [t - now for t in pending if t is not None]
        if any(d <= 0 for d in due):
            continue
        time.sleep(min([POLL] + due))
    past_deadline = time.monotonic() >= deadline
    leftover = group_alive(pgid)
    signal_group(pgid, signal.SIGKILL)
    gone = wait_group_gone(pgid, GROUP_WAIT)
    record = {
        "rc": returncode,
        "signal": signal.Signals(-returncode).name if returncode < 0 else None,
        "deadline_signalled": deadline_signalled,
        "past_deadline": past_deadline,
        "forwarded": signal.Signals(forwarded).name if forwarded is not None else None,
        "peak_rss_bytes": peak_rss_bytes(),
        "leftover_group_killed": leftover,
        "group_gone": gone,
        "pgid": pgid,
        "deadline": deadline,
        "started": started,
        "ended": time.monotonic(),
    }
    write_atomic(result, json.dumps(record, sort_keys=True) + "\n")
    clean = (
        returncode == 0 and not deadline_signalled and not past_deadline and forwarded is None and not leftover and gone
    )
    return 0 if clean else 1


def main(argv: list[str]) -> int:
    if len(argv) < 5 or argv[3] != "--":
        print(__doc__, file=sys.stderr)
        return 2
    try:
        deadline = float(argv[1])
    except ValueError:
        print(f"p0_supervise: deadline {argv[1]!r} is not a number", file=sys.stderr)
        return 2
    if time.monotonic() >= deadline:
        print("p0_supervise: the deadline has passed; no worker started", file=sys.stderr)
        return 2
    return supervise(deadline, argv[2], argv[4:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
