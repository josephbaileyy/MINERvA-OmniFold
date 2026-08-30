#!/usr/bin/python3.11
"""Collect one self-describing status snapshot for the campaign dashboard.

Design rules, each of which exists because the naive version of it produced a wrong
reading on this cluster:

1.  **A failure to observe never renders as an observation.** Every panel entry carries
    a state that distinguishes "measured false" from "not measured", and every source
    carries `ok` plus `age_seconds`. Job classification is delegated to
    `slurm_array_status.build_snapshot()`, which already encodes this (its `UNOBSERVED`
    branch exists because leg F displayed ACTIVE for 24 h after finishing -- BEN-323).

2.  **Slurm prints local time with no offset, file mtimes are epoch, and the waker's
    receipts are UTC.** So every Slurm call is made with `TZ=UTC` forced into the
    environment (measured: the same scron job printed `2026-08-29T22:30:00` local and
    `2026-08-30T05:30:00` UTC -- reading the local string as UTC puts a future start
    time 7 h in the past), and every age is computed as an epoch difference.

3.  **tmux is node-local.** `tmux ls` on one login node answers for that node only, so
    the sweep visits every node in the `cron` partition individually and reports its own
    coverage. The node list is read from Slurm, not hardcoded.

4.  **A restarting job is not evidence its work is happening.** The ticker panel reports
    the tick receipt (authoritative), the scron job (schedule presence only) and any
    daemon locks (which record a daemon's START, not its liveness) as three separate
    facts. It never combines them into one green light.

No secret is ever read: this module does not open `notification-secrets.json`, and the
snapshot is assembled from an explicit field whitelist rather than by dumping state.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Iterable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import agentctl  # noqa: E402  (atomic_write_json -- reused, not reimplemented)
import slurm_array_status as sas  # noqa: E402  (job state classification -- CALLED, not retyped)

SCHEMA_VERSION = 1

# A source is stale when its data is older than this, in seconds.  Per-source so that a
# 5-minute ticker and a once-a-day agent session are not judged by one threshold.
DEFAULT_STALE_SECONDS = {
    "slurm_queue": 300,
    "login_sweep": 900,
    "waker_tick": 1800,
    "agent_sessions": 86400,
    # A codex window is read live; a Claude window comes from the status-line cache,
    # whose own policy calls it stale past 1800 s.  Judge the panel on the same scale.
    "llm_usage": 1800,
    "local_llm_sessions": 300,
}

# Runner signature: argv -> (returncode, stdout, stderr).  The streams stay SEPARATE
# because the ssh probe needs both independently: `tmux ls` output arrives on stdout
# while the login banner and the ssh diagnostic ("No route to host", pam_nologin's
# "System is going down") arrive on stderr.  Combining them forced a choice between
# suppressing the banner -- which also suppressed the reason a node was unreachable --
# and letting banner text into the session parser.  Injected so the tests can drive
# every branch without a cluster.
Runner = Callable[[list[str], float], "tuple[int, str, str]"]


class Clock:
    """Injectable epoch clock.  Ages are epoch differences, never parsed-string deltas."""

    def now(self) -> float:
        return time.time()


def utc_iso(epoch: float) -> str:
    return (
        dt.datetime.fromtimestamp(epoch, dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def run_command(argv: list[str], timeout: float = 30.0) -> tuple[int, str, str]:
    """Run a command with UTC forced, returning (rc, stdout, stderr).

    `TZ=UTC` is the whole reason this wrapper exists -- see rule 2 in the module
    docstring.  It must be applied to every Slurm call, so the wrapper applies it
    unconditionally rather than leaving it to each call site to remember.
    """
    env = dict(os.environ)
    env["TZ"] = "UTC"
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout:g}s: {' '.join(argv)}"
    except OSError as exc:
        return 127, "", f"{type(exc).__name__}: {exc}"
    return completed.returncode, completed.stdout or "", completed.stderr or ""


def both(result: tuple[int, str, str]) -> tuple[int, str]:
    """Collapse a runner result for callers that do not care which stream spoke.

    Slurm's own tools print errors on stderr and rows on stdout, and every parser below
    keys on line shape, so combining is safe for them -- unlike the ssh probe.
    """
    rc, out, err = result
    return rc, out + err


# ---------------------------------------------------------------------------
# Sources


class Source:
    """One measurement attempt, with an explicit outcome and an explicit age.

    `ok=False` means the measurement failed, which is different from a measurement that
    succeeded and found nothing.  `age_seconds=None` means the age itself is unknown,
    which the renderer must show rather than defaulting to 0.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.ok = False
        self.age_seconds: float | None = None
        self.error: str | None = None
        self.detail: dict = {}

    def succeed(self, age_seconds: float, **detail) -> "Source":
        self.ok = True
        self.age_seconds = max(0.0, round(age_seconds, 1))
        self.error = None
        self.detail.update(detail)
        return self

    def fail(self, error: str, age_seconds: float | None = None, **detail) -> "Source":
        self.ok = False
        self.error = error
        self.age_seconds = None if age_seconds is None else max(0.0, round(age_seconds, 1))
        self.detail.update(detail)
        return self

    def to_json(self, stale_after: dict[str, int]) -> dict:
        limit = stale_after.get(self.name)
        stale: bool | None
        if self.age_seconds is None or limit is None:
            stale = None  # not measured -- never render as fresh
        else:
            stale = self.age_seconds > limit
        return {
            "name": self.name,
            "ok": self.ok,
            "age_seconds": self.age_seconds,
            "error": self.error,
            "stale": stale,
            "stale_after_seconds": limit,
            "detail": self.detail,
        }


def file_age(path: Path, clock: Clock) -> tuple[float | None, str | None]:
    """Age of a file by mtime, in seconds.  Epoch arithmetic only."""
    try:
        return clock.now() - path.stat().st_mtime, None
    except OSError as exc:
        return None, f"{type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# Login-node list, read from Slurm rather than hardcoded


def expand_hostlist(spec: str) -> list[str]:
    """Expand a Slurm hostlist into names, keeping only `login*` entries.

    Reuses `slurm_array_status.expand_spec` for the numeric range logic instead of
    retyping it; this function only adds prefix handling and zero-padding.
    """
    hosts: list[str] = []
    for token in re.finditer(r"([a-zA-Z][a-zA-Z0-9_-]*)(?:\[([0-9,\-]+)\]|([0-9]+))?", spec):
        prefix, bracket, bare = token.group(1), token.group(2), token.group(3)
        if not prefix.startswith("login"):
            continue
        if bracket:
            width = len(bracket.split("-")[0].split(",")[0])
            hosts.extend(f"{prefix}{index:0{width}d}" for index in sas.expand_spec(bracket))
        elif bare:
            hosts.append(f"{prefix}{bare}")
        else:
            hosts.append(prefix)
    return sorted(set(hosts))


def login_nodes(runner: Runner) -> tuple[list[str], str | None]:
    rc, text = both(runner(["scontrol", "show", "partition", "cron"], 20.0))
    if rc != 0:
        return [], f"scontrol show partition cron rc={rc}: {text.strip()[:200]}"
    match = re.search(r"\bNodes=(\S+)", text)
    if not match:
        return [], "scontrol printed no Nodes= field for the cron partition"
    hosts = expand_hostlist(match.group(1))
    return hosts, None if hosts else f"no login* nodes in Nodes={match.group(1)[:80]}"


def maintenance_nodes(runner: Runner) -> tuple[set[str], str | None]:
    """Login nodes sitting in an ACTIVE MAINT reservation.

    This is why a node is unreachable, which is a different claim from whether it is.
    """
    rc, text = both(runner(["scontrol", "show", "reservation"], 20.0))
    if rc != 0:
        return set(), f"scontrol show reservation rc={rc}: {text.strip()[:200]}"
    nodes: set[str] = set()
    for block in re.split(r"\n(?=ReservationName=)", text):
        if "MAINT" not in block or "State=ACTIVE" not in block:
            continue
        found = re.search(r"\bNodes=(\S+)", block)
        if found:
            nodes.update(expand_hostlist(found.group(1)))
    return nodes, None


# ---------------------------------------------------------------------------
# tmux sweep


TMUX_NO_SOCKET = re.compile(r"error connecting to .*No such file or directory", re.I)
TMUX_NO_SERVER = re.compile(r"no server running on", re.I)
TMUX_SESSION = re.compile(r"^(?P<name>[^:]+):\s+(?P<windows>\d+)\s+window")
TMUX_CREATED = re.compile(r"\(created (?P<when>[^)]+)\)")


def parse_tmux_ls(text: str, clock: Clock) -> list[dict]:
    """Parse `tmux ls` output into sessions.

    `tmux ls` prints its creation time in the node's LOCAL zone with no offset, so it is
    not safely convertible to an epoch.  The string is therefore reported verbatim as
    `created_local_text` and no age is derived from it -- an unconvertible timestamp is
    surfaced, not guessed.
    """
    sessions: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        match = TMUX_SESSION.match(line)
        if not match:
            continue
        created = TMUX_CREATED.search(line)
        sessions.append(
            {
                "name": match.group("name")[:120],
                "windows": int(match.group("windows")),
                "created_local_text": created.group("when") if created else None,
                "age_seconds": None,
                "age_unavailable_reason": "tmux prints local time with no offset",
            }
        )
    return sessions


def is_local_node(node: str, hostname: str | None = None) -> bool:
    """Is `node` the machine we are running on?  Compared on the short name only."""
    host = (hostname if hostname is not None else socket.gethostname()).split(".")[0]
    return node.split(".")[0] == host


def probe_node(
    node: str,
    runner: Runner,
    clock: Clock,
    timeout: float,
    hostname: str | None = None,
) -> dict:
    """Probe one login node for tmux sessions.

    `-o ControlPath=none` is mandatory: with a ControlMaster in play every ssh collapses
    onto one node and the sweep silently measures that node 40 times.

    The node we are already running on is read WITHOUT ssh.  Measured 2026-08-30: the
    collector's own node (login03) appeared among the unmeasured ones with "timeout
    after 18s" because it was ssh-ing to itself under load -- a network round trip, and
    a failure mode, for a socket sitting in the local filesystem.
    """
    # Neither `-q` nor `LogLevel=ERROR`: both suppress the diagnostic that says WHY a
    # node could not be measured.  Measured on 2026-08-30: with them, login17 and
    # login19 both reported only "rc=255 with no output"; without them they report
    # "No route to host" and pam_nologin's "System is going down" respectively -- two
    # different causes that the dashboard should not conflate.  The banner they also
    # let through lands on stderr and never reaches the session parser.
    local = is_local_node(node, hostname)
    argv = ["tmux", "ls"] if local else [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", f"ConnectTimeout={int(timeout)}",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ControlPath=none",
        node,
        "tmux ls",
    ]
    started = clock.now()
    rc, out, err = runner(argv, timeout + 10.0)
    elapsed = clock.now() - started
    row = {
        "node": node,
        "probe_rc": rc,
        "probe_seconds": round(elapsed, 1),
        "sessions": [],
        "error": None,
        "probed_via": "local" if local else "ssh",
    }
    if rc == 0:
        row["state"] = "sessions"
        row["sessions"] = parse_tmux_ls(out, clock)
        if not row["sessions"]:
            # rc=0 with nothing parseable is not "no sessions"; it is an unparsed answer.
            row["state"] = "unparsed"
            row["error"] = f"tmux exited 0 but printed no session line: {out.strip()[:120]}"
        return row

    # tmux reports its own absence on stderr with rc=1.  Both spellings mean the node
    # WAS measured and has no server -- a different claim from not having been measured.
    tmux_said = out + err
    if TMUX_NO_SOCKET.search(tmux_said):
        row["state"] = "no_tmux_server"
        row["detail"] = "no socket: no tmux server has run for this uid on this node"
        return row
    if TMUX_NO_SERVER.search(tmux_said):
        row["state"] = "no_tmux_server"
        row["detail"] = "socket present, server gone: a tmux server exited here"
        return row

    row["state"] = "unmeasured"
    row["error"] = summarize_ssh_failure(err, rc)
    row["error_short"] = short_ssh_failure(err, rc)
    row["unreachable_cause"] = classify_ssh_failure(err)
    return row


BANNER_NOISE = re.compile(
    r"NOTICE TO USERS|Lawrence Berkeley|Department of Energy|law enforcement|"
    r"consents to such|LOG OFF IMMEDIATELY|Unauthorized or improper|expectation of privacy|"
    r"intercepted, monitored|disciplinary action|stated in this warning|conditions of use|"
    r"^\*+$|^\s*$|property of the United States|By using this system|"
    r"as well as authorized|recording, copying|of authorized site|this system you indicate",
    re.I | re.M,
)


def summarize_ssh_failure(err: str, rc: int) -> str:
    """The operative line of an ssh failure, with the login banner stripped.

    Every NERSC login node prints a 24-line legal banner before refusing, so the reason
    has to be extracted rather than truncated -- a plain [:160] slice returns banner.
    """
    lines = [
        line.strip()
        for line in err.splitlines()
        if line.strip() and not BANNER_NOISE.search(line)
    ]
    interesting = [
        line for line in lines
        if re.search(r"going down|not permitted|No route to host|Connection (closed|refused|"
                     r"timed out)|timed out|Permission denied|Host key|unreachable|timeout",
                     line, re.I)
    ]
    chosen = interesting or lines
    return " / ".join(chosen)[:200] or f"ssh rc={rc} with no diagnostic output"


def short_ssh_failure(err: str, rc: int) -> str:
    """The single most specific line, for a panel that must stay glanceable.

    The full text stays in `reason`; this is what the dashboard shows before you ask
    for detail.  Without it, one draining node contributes four lines and eight of them
    make the coverage panel taller than the rest of the page combined.
    """
    full = summarize_ssh_failure(err, rc)
    first = full.split(" / ")[0].strip()
    return (first[:77] + "...") if len(first) > 80 else first


def classify_ssh_failure(err: str) -> str:
    """Name the cause class, so 'draining' and 'off the network' stay distinguishable."""
    if re.search(r"going down|not permitted to log in|pam_nologin", err, re.I):
        return "draining"          # pam_nologin: node is being taken out of service
    if re.search(r"No route to host|Network is unreachable", err, re.I):
        return "no_route"
    if re.search(r"timed out|timeout", err, re.I):
        return "timeout"
    if re.search(r"Permission denied|Host key", err, re.I):
        return "auth"
    return "unknown"


def sweep_tmux(
    runner: Runner,
    clock: Clock,
    nodes: Iterable[str],
    timeout: float = 8.0,
    workers: int = 16,
) -> tuple[list[dict], dict]:
    nodes = list(nodes)
    rows: list[dict] = []
    if nodes:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(probe_node, node, runner, clock, timeout): node for node in nodes
            }
            for future in concurrent.futures.as_completed(futures):
                rows.append(future.result())
    rows.sort(key=lambda row: row["node"])
    measured = [row for row in rows if row["state"] != "unmeasured"]
    unmeasured = [row for row in rows if row["state"] == "unmeasured"]
    coverage = {
        "nodes_total": len(nodes),
        "nodes_measured": len(measured),
        "unmeasured": [
            {
                "node": row["node"],
                "reason": row["error"],
                "reason_short": row.get("error_short", row["error"]),
                "cause": row.get("unreachable_cause", "unknown"),
            }
            for row in unmeasured
        ],
        "complete": len(unmeasured) == 0 and bool(nodes),
    }
    return rows, coverage


# ---------------------------------------------------------------------------
# Jobs


DURATION = re.compile(r"^(?:(\d+)-)?(?:(\d+):)?(\d+):(\d+)$")


def parse_duration(text: str) -> int | None:
    """Slurm duration (`D-HH:MM:SS`, `HH:MM:SS`, `MM:SS`) to seconds, or None."""
    match = DURATION.match(text.strip())
    if not match:
        return None
    days, hours, minutes, seconds = match.groups()
    total = int(minutes) * 60 + int(seconds)
    if hours:
        total += int(hours) * 3600
    if days:
        total += int(days) * 86400
    return total


def parse_utc_stamp(text: str) -> float | None:
    """Parse a Slurm timestamp that we have forced to UTC.  Unknown forms return None."""
    text = text.strip()
    if not text or text in {"N/A", "Unknown", "None", "(null)"}:
        return None
    try:
        naive = dt.datetime.strptime(text, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    return naive.replace(tzinfo=dt.timezone.utc).timestamp()


def display_reason(reason: str) -> str:
    """Slurm's literal `None` reason means it gave none, which is not a blocker name.

    Rendering it verbatim produces "blocked on None", which reads as a cause.
    """
    return "no reason reported by Slurm" if reason.strip() in {"", "None"} else reason.strip()


def queue_rows(runner: Runner) -> tuple[list[dict], str | None]:
    """One row per queued task, with the fields the dashboard is allowed to show."""
    rc, text = both(runner(
        ["squeue", "--me", "-h", "-r", "-o", "%i|%j|%P|%T|%L|%M|%r|%N"],
        30.0,
    ))
    if rc != 0:
        return [], f"squeue --me rc={rc}: {text.strip()[:200]}"
    rows = []
    for line in text.splitlines():
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 8:
            continue
        token, name, partition, state, left, elapsed, reason, nodelist = parts
        rows.append(
            {
                "token": token,
                "name": name[:120],
                "partition": partition,
                "state": sas.normalize_state(state),
                "time_left_text": left,
                "time_left_seconds": parse_duration(left),
                "elapsed_seconds": parse_duration(elapsed),
                "reason": reason or "None",
                "nodelist": nodelist,
            }
        )
    return rows, None


def start_estimates(runner: Runner) -> tuple[dict[str, str], str | None]:
    rc, text = both(runner(["squeue", "--me", "-h", "-r", "--start", "-o", "%i|%S"], 30.0))
    if rc != 0:
        return {}, f"squeue --start rc={rc}: {text.strip()[:200]}"
    result = {}
    for line in text.splitlines():
        parts = [part.strip() for part in line.split("|")]
        if len(parts) == 2:
            result[parts[0]] = parts[1]
    return result, None


def classify_eta(rows: list[dict], starts: dict[str, str], now: float) -> dict:
    """Decide what, if anything, may be said about when this job finishes or starts.

    Slurm returns `N/A` from `squeue --start` for anything blocked on Priority or
    Dependency, which is most of this campaign's queue.  There is no ETA to show in that
    case and none is invented: the honest output is the blocking reason.
    """
    running = [row for row in rows if row["state"] == "RUNNING"]
    if running:
        known = [row["time_left_seconds"] for row in running if row["time_left_seconds"] is not None]
        if known:
            return {
                "kind": "time_left",
                "seconds": max(known),
                "text": max(running, key=lambda r: r["time_left_seconds"] or -1)["time_left_text"],
                "detail": (
                    f"walltime remaining for {len(known)} running task(s); "
                    "this is the Slurm limit, not a prediction of completion"
                ),
            }
        return {
            "kind": "unknown",
            "seconds": None,
            "text": None,
            "detail": "running, but Slurm reported no parseable TimeLeft",
        }

    reasons = sorted({display_reason(row["reason"]) for row in rows if row["state"] == "PENDING"})
    stamps = [parse_utc_stamp(starts.get(row["token"], "")) for row in rows]
    future = [stamp for stamp in stamps if stamp is not None and stamp > now]
    if future:
        return {
            "kind": "start_estimate",
            "seconds": round(min(future) - now),
            "text": utc_iso(min(future)),
            "detail": "Slurm's own start estimate; it moves as the queue changes",
        }
    past = [stamp for stamp in stamps if stamp is not None and stamp <= now]
    if past:
        return {
            "kind": "unknown",
            "seconds": None,
            "text": None,
            "detail": (
                f"Slurm's start estimate {utc_iso(max(past))} is in the past, so it is "
                "stale rather than an ETA"
            ),
        }
    named = [r for r in reasons if r != "no reason reported by Slurm"]
    if named:
        why = f"; blocked on {', '.join(named)}"
    elif reasons:
        why = "; Slurm reported no blocking reason"
    else:
        why = ""
    return {
        "kind": "unknown",
        "seconds": None,
        "text": None,
        "detail": "squeue --start returns N/A for these tasks" + why,
    }


def collect_jobs(runner: Runner, clock: Clock) -> tuple[list[dict], Source]:
    """Group my queued tasks into jobs and classify each via slurm_array_status."""
    source = Source("slurm_queue")
    started = clock.now()
    rows, error = queue_rows(runner)
    if error:
        return [], source.fail(error)
    starts, start_error = start_estimates(runner)

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        base = row["token"].split("_", 1)[0].split(".", 1)[0]
        grouped.setdefault(base, []).append(row)

    # build_snapshot() shells out itself, so give it a text runner with the same TZ=UTC
    # discipline.  It raises on a failed call, which its own observer_errors then carry.
    def text_runner(argv: list[str]) -> str:
        rc, text = both(runner(argv, 30.0))
        if rc != 0:
            raise subprocess.CalledProcessError(rc, argv, output=text)
        return text

    jobs = []
    for job_id, job_rows in sorted(grouped.items()):
        tasks: list[int] = []
        for row in job_rows:
            tasks.extend(sas.task_ids(job_id, row["token"]))
        tasks = sorted(set(tasks)) or [0]
        snapshot = sas.build_snapshot(job_id, tasks, runner=text_runner)
        jobs.append(
            {
                "job_id": job_id,
                "name": job_rows[0]["name"],
                "partition": job_rows[0]["partition"],
                # `overall` is slurm_array_status's classification, including UNOBSERVED.
                "overall": snapshot["overall"],
                "counts": snapshot["counts"],
                "tasks_total": len(tasks),
                "error_tasks": snapshot["error_tasks"],
                "unknown_tasks": snapshot["unknown_tasks"],
                "observer_errors": snapshot["observer_errors"],
                "nodelist": sorted({row["nodelist"] for row in job_rows if row["nodelist"]}),
                "blocking_reasons": sorted(
                    {display_reason(row["reason"]) for row in job_rows if row["state"] == "PENDING"}
                ),
                "elapsed_seconds": max(
                    (row["elapsed_seconds"] or 0 for row in job_rows), default=0
                ),
                "eta": classify_eta(job_rows, starts, clock.now()),
            }
        )
    source.succeed(clock.now() - started, jobs=len(jobs), tasks=len(rows))
    if start_error:
        source.detail["start_estimate_error"] = start_error
    return jobs, source


# ---------------------------------------------------------------------------
# Agents and the ticker


def collect_ticker(state_dir: Path, runner: Runner, clock: Clock) -> tuple[dict, Source]:
    """Report tick receipt, scron schedule and daemon locks as three separate facts.

    Combining them is the failure this panel exists to prevent: the scron job for this
    campaign's waker restarts on every scheduled run and its StdOut had not advanced in
    two days, while `last-tick.json` was seconds old and carried a constant pid on a
    different node -- i.e. the schedule was not what was doing the work.
    """
    source = Source("waker_tick")
    tick_path = state_dir / "last-tick.json"
    ticker: dict = {"receipt": None, "scron": None, "daemon_locks": []}

    age: float | None = None
    try:
        receipt = json.loads(tick_path.read_text())
        at_utc = str(receipt["at_utc"])
        stamp = dt.datetime.fromisoformat(at_utc.replace("Z", "+00:00"))
        age = clock.now() - stamp.timestamp()
        ticker["receipt"] = {
            "at_utc": at_utc,
            "age_seconds": round(age, 1),
            "node": str(receipt.get("node", "unknown")),
            "pid": receipt.get("pid"),
            "watch_errors": receipt.get("watch_errors"),
        }
        source.succeed(age)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        source.fail(f"unreadable tick receipt {tick_path}: {type(exc).__name__}: {exc}")

    # Schedule presence.  Never liveness.
    rc, text = both(runner(["squeue", "--me", "-h", "-r", "-o", "%i|%T|%r", "-p", "cron"], 20.0))
    if rc == 0:
        rows = [line for line in text.splitlines() if line.strip()]
        ticker["scron"] = {
            "jobs": [dict(zip(("job_id", "state", "reason"), line.split("|"))) for line in rows],
            "note": "presence of a cron job is not evidence that any tick ran",
        }
    else:
        ticker["scron"] = {"jobs": None, "error": f"squeue -p cron rc={rc}: {text.strip()[:160]}"}

    for lock in sorted(state_dir.glob("daemon-*.lock")):
        lock_age, lock_error = file_age(lock, clock)
        ticker["daemon_locks"].append(
            {
                "node": lock.name[len("daemon-") : -len(".lock")],
                "created_age_seconds": None if lock_age is None else round(lock_age, 1),
                "error": lock_error,
                "note": "a lock records when a daemon STARTED, not that it is still ticking",
            }
        )
    return ticker, source


def collect_agents(state_dir: Path, clock: Clock) -> tuple[list[dict], Source]:
    """LLM orchestration sessions, from the sessions index the waker already maintains."""
    source = Source("agent_sessions")
    path = state_dir / "agent-sessions-v2.json"
    try:
        document = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [], source.fail(f"unreadable {path}: {type(exc).__name__}: {exc}")

    agents = []
    ages = []
    for name, session in sorted((document.get("sessions") or {}).items()):
        updated = str(session.get("updated_at") or "")
        age: float | None = None
        try:
            age = clock.now() - dt.datetime.fromisoformat(updated.replace("Z", "+00:00")).timestamp()
            ages.append(age)
        except ValueError:
            age = None
        turns = session.get("turns") or []
        last_turn = turns[-1] if turns else {}
        agents.append(
            {
                # Whitelisted fields only.  Prompts and transcripts are deliberately absent:
                # this file can end up on a public web path.
                "name": name[:120],
                "provider": str(session.get("provider", "unknown"))[:40],
                "profile": str(session.get("profile", "unknown"))[:40],
                "cwd": str(session.get("cwd", ""))[:200],
                "updated_at_utc": updated or None,
                "age_seconds": None if age is None else round(age, 1),
                "turns": len(turns),
                "last_action": str(last_turn.get("action", "unknown"))[:40],
                "last_returncode": last_turn.get("returncode"),
            }
        )
    source.succeed(min(ages) if ages else 0.0, sessions=len(agents))
    return agents, source


# ---------------------------------------------------------------------------
# LLM accounts, and LLM sessions running on this machine


def collect_llm_accounts(runner: Runner, clock: Clock, timeout: float = 40.0) -> tuple[dict, Source]:
    """Per-account provider capacity, from `usagectl.py snapshot`.

    usagectl already owns every hard part of this -- the codex app-server call, the
    Claude status-line cache and its staleness policy, and `profile_account_groups`,
    which records that two profile names can be ALIASES OF ONE ACCOUNT whose capacity
    "must not be summed".  This function only reshapes its output for display; it
    computes no capacity of its own.
    """
    source = Source("llm_usage")
    started = clock.now()
    rc, text = both(runner(
        [sys.executable, str(HERE / "usagectl.py"), "snapshot", "--json",
         "--timeout", "25"], timeout))
    if "{" not in text:
        return {}, source.fail(f"usagectl snapshot rc={rc}: {text.strip()[:200]}")
    try:
        snapshot = json.loads(text[text.index("{"):])
    except (ValueError, json.JSONDecodeError) as exc:
        return {}, source.fail(f"usagectl printed non-JSON: {type(exc).__name__}: {exc}")

    accounts: list[dict] = []
    for name, profile in sorted((snapshot.get("profiles") or {}).items()):
        capacity = profile.get("capacity") or {}
        windows = []
        for window_name, window in sorted((profile.get("windows") or {}).items()):
            if not isinstance(window, dict):
                continue
            windows.append({
                "name": window_name,
                "remaining_percent": window.get("remaining_percent"),
                "used_percent": window.get("used_percent"),
                "resets_at_utc": window.get("resets_at_utc"),
                "resets_in_seconds": (
                    None if not window.get("resets_at_epoch")
                    else max(0, round(window["resets_at_epoch"] - clock.now()))
                ),
            })
        # `age_seconds` is usagectl's own age for a cached measurement (Claude); a live
        # one (codex) has none, so fall back to the snapshot's observation time.
        age = profile.get("age_seconds")
        if age is None:
            observed = profile.get("observed_at_utc") or snapshot.get("observed_at_utc")
            try:
                age = clock.now() - dt.datetime.fromisoformat(
                    str(observed).replace("Z", "+00:00")).timestamp()
            except (ValueError, TypeError):
                age = None
        accounts.append({
            "profile": name,
            "provider": str(profile.get("provider", "unknown"))[:24],
            "plan": str(profile.get("plan_type") or "")[:24] or None,
            "state": str(capacity.get("state", "UNKNOWN"))[:24],
            "reason": str(capacity.get("reason") or "")[:200] or None,
            "minimum_remaining_percent": capacity.get("minimum_remaining_percent"),
            "windows": windows,
            "age_seconds": None if age is None else round(age, 1),
            "measurement": str(profile.get("source") or "")[:120] or None,
            # Two profiles can be one account; the UI must not present them as two
            # independent budgets.
            "account_id": profile.get("account_id") or name,
            "shares_account_with": [
                alias for alias in (profile.get("account_aliases") or []) if alias != name
            ],
            "capacity_is_shared": bool(profile.get("capacity_is_shared")),
            "warnings": [str(w)[:160] for w in (profile.get("warnings") or [])][:4],
        })

    result = {
        "accounts": accounts,
        "gate_ok": snapshot.get("gate_ok"),
        "policy_violations": [str(v)[:200] for v in (snapshot.get("policy_violations") or [])][:8],
        "observed_at_utc": snapshot.get("observed_at_utc"),
    }
    source.succeed(clock.now() - started, accounts=len(accounts),
                   measured=sum(1 for a in accounts if a["state"] != "UNKNOWN"))
    return result, source


# Every Claude config directory this machine might run a session under.  Measured
# 2026-08-30: sessions live under ~/.claude, ~/.claude-personal and ~/.claude-school as
# separate CLAUDE_CONFIG_DIRs, plus the per-profile homes.  Scanning only ~/.claude
# reported "no local sessions" while two were live -- the covering-search trap.
LOCAL_SESSION_ROOTS = (
    "~/.claude",
    "~/.claude-personal",
    "~/.claude-school",
    "~/claude-homes/*/.claude",
)
LOCAL_SESSION_WINDOW = 86400.0


# A home prefix worth stripping so the useful part of a project name is visible.
HOME_PREFIX = re.compile(r"^-(Users|home|global-u2|global-homes)-[^-]+-")


def decode_project(encoded: str) -> str:
    """Shorten Claude Code's encoded project directory WITHOUT inventing a path.

    The encoding replaces '/' with '-', which is lossy: a directory whose own name
    contains a dash is indistinguishable from a separator.  Splitting on '-' turned
    `-Users-josephbailey-local-research-MINERvA-OmniFold` into "MINERvA/OmniFold",
    which reads as a real two-segment path and is not one.  So only the leading
    `-Users-<account>-` prefix is stripped -- unambiguous, since it is anchored -- and
    the rest is shown verbatim, dashes and all.
    """
    stripped = HOME_PREFIX.sub("", encoded)
    return (stripped or encoded)[:80]


def expand_root(pattern: str) -> list[Path]:
    """Expand one configured session root, which may contain a glob."""
    expanded = Path(pattern).expanduser()
    if not any(ch in pattern for ch in "*?"):
        return [expanded]
    parts = expanded.parts
    for index, part in enumerate(parts):
        if any(ch in part for ch in "*?"):
            base = Path(*parts[:index])
            return sorted(base.glob(str(Path(*parts[index:]))))
    return [expanded]


def collect_local_sessions(
    clock: Clock,
    roots: "tuple[str, ...]" = LOCAL_SESSION_ROOTS,
    window_seconds: float = LOCAL_SESSION_WINDOW,
) -> tuple[dict, Source]:
    """LLM sessions on THIS machine, from their transcript files.

    A transcript's mtime is when the session last WROTE, which is evidence of activity
    and not of a live process -- so that is what the field is called.  Only sessions
    inside `window_seconds` are listed, and the total scanned is reported beside the
    count, so a filtered view cannot be read as a complete one.
    """
    source = Source("local_llm_sessions")
    started = clock.now()
    rows, scanned, errors = [], 0, []
    for pattern in roots:
        for base in expand_root(pattern):
            projects = base / "projects"
            if not projects.is_dir():
                continue
            try:
                transcripts = list(projects.glob("*/*.jsonl"))
            except OSError as exc:
                errors.append(f"{projects}: {exc}")
                continue
            for transcript in transcripts:
                scanned += 1
                try:
                    stat = transcript.stat()
                except OSError:
                    continue
                age = clock.now() - stat.st_mtime
                if age > window_seconds:
                    continue
                rows.append({
                    # The config dir is the account the session runs under, which is
                    # what ties a session to a row in the LLM accounts panel.
                    "config_dir": base.name if base.name.startswith(".claude") else base.parent.name,
                    "project": decode_project(transcript.parent.name),
                    "session": transcript.stem[:8],
                    "last_write_age_seconds": round(age, 1),
                    "size_bytes": stat.st_size,
                })
    rows.sort(key=lambda row: row["last_write_age_seconds"])
    result = {
        "sessions": rows,
        "transcripts_scanned": scanned,
        "window_seconds": window_seconds,
        "roots": list(roots),
        "errors": errors,
    }
    source.succeed(clock.now() - started, shown=len(rows), scanned=scanned)
    if errors:
        source.detail["scan_errors"] = len(errors)
    return result, source


def collect_sweep(runner: Runner, clock: Clock, timeout: float) -> tuple[list[dict], dict, Source]:
    source = Source("login_sweep")
    started = clock.now()
    nodes, error = login_nodes(runner)
    if error:
        return [], {"nodes_total": 0, "nodes_measured": 0, "unmeasured": [], "complete": False}, source.fail(error)
    maint, maint_error = maintenance_nodes(runner)
    rows, coverage = sweep_tmux(runner, clock, nodes, timeout=timeout)
    for row in rows:
        row["in_maint_reservation"] = row["node"] in maint
    for entry in coverage["unmeasured"]:
        entry["in_maint_reservation"] = entry["node"] in maint
    coverage["maint_reservation_error"] = maint_error
    source.succeed(clock.now() - started, **{k: v for k, v in coverage.items() if k != "unmeasured"})
    if not coverage["complete"]:
        source.detail["partial"] = (
            f"{coverage['nodes_measured']}/{coverage['nodes_total']} login nodes measured"
        )
    return rows, coverage, source


# ---------------------------------------------------------------------------
# Snapshot


def build_local_status(clock: Clock | None = None, stale_after: dict[str, int] | None = None) -> dict:
    """The panels that can only be measured on the machine the user is sitting at.

    `dashboard_serve.py` runs this locally and merges it into the cluster snapshot, so
    each panel is labelled with where it was measured rather than implying one host saw
    everything.
    """
    clock = clock or Clock()
    stale_after = stale_after or DEFAULT_STALE_SECONDS
    local, source = collect_local_sessions(clock)
    generated = clock.now()
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": utc_iso(generated),
        "generated_at_epoch": int(generated),
        "measured_on": socket.gethostname(),
        "sources": [dict(source.to_json(stale_after), measured_on="this device")],
        "local_sessions": local,
    }


def build_status(
    state_dir: Path,
    runner: Runner = run_command,
    clock: Clock | None = None,
    sweep_timeout: float = 8.0,
    stale_after: dict[str, int] | None = None,
    with_usage: bool = True,
) -> dict:
    clock = clock or Clock()
    stale_after = stale_after or DEFAULT_STALE_SECONDS
    started = clock.now()

    jobs, jobs_source = collect_jobs(runner, clock)
    tmux_rows, coverage, sweep_source = collect_sweep(runner, clock, sweep_timeout)
    ticker, tick_source = collect_ticker(state_dir, runner, clock)
    agents, agent_source = collect_agents(state_dir, clock)
    sources = [jobs_source, sweep_source, tick_source, agent_source]
    llm: dict = {}
    if with_usage:
        llm, usage_source = collect_llm_accounts(runner, clock)
        sources.append(usage_source)
    generated = clock.now()
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": utc_iso(generated),
        "generated_at_epoch": int(generated),
        "collector": {
            "host": socket.gethostname(),
            "duration_seconds": round(generated - started, 1),
            "state_dir": str(state_dir),
        },
        "sources": [
            dict(source.to_json(stale_after), measured_on=socket.gethostname())
            for source in sources
        ],
        "llm_accounts": llm,
        "jobs": jobs,
        "tmux": tmux_rows,
        "coverage": coverage,
        "ticker": ticker,
        "agents": agents,
    }


# ---------------------------------------------------------------------------
# Alerts (for the things you should not have to be looking at the page to learn)


# Re-alert only after this long, by bucketing it into the notifyctl dedupe key.  Without
# a bucket a stable key alerts exactly once, ever; with a per-tick key it alerts every
# five minutes.
DEFAULT_ALERT_WINDOW_SECONDS = 6 * 3600

TICKER_ALERT_SECONDS = 1800
COVERAGE_ALERT_FRACTION = 0.6


def alert_conditions(status: dict) -> list[tuple[str, str]]:
    """(condition, subject) for each thing worth interrupting the user about.

    The subject must stand alone and must be safe to publish: this campaign's ntfy
    channel is configured `include_body: false` with a generic body, because an ntfy
    topic is a URL anyone holding it can read.  So no paths, no hostnames beyond a login
    node name, and never any state file contents.
    """
    conditions: list[tuple[str, str]] = []
    sources = {source["name"]: source for source in status.get("sources", [])}

    ticker = (status.get("ticker") or {}).get("receipt")
    tick_source = sources.get("waker_tick", {})
    if not tick_source.get("ok") or ticker is None:
        conditions.append(("ticker-unreadable",
                           "MNV: waker tick receipt unreadable - liveness unknown"))
    elif ticker.get("age_seconds", 0) > TICKER_ALERT_SECONDS:
        minutes = int(ticker["age_seconds"] // 60)
        conditions.append((f"ticker-stale-{minutes // 30}",
                           f"MNV: waker ticker stale, last tick {minutes} min ago"))

    errored = [job["job_id"] for job in status.get("jobs", []) if job.get("overall") == "ERROR"]
    if errored:
        conditions.append((f"job-error-{'-'.join(sorted(errored))}",
                           f"MNV: {len(errored)} job(s) in ERROR: {', '.join(sorted(errored))}"))

    failed = sorted(name for name, source in sources.items() if not source.get("ok"))
    if failed:
        conditions.append((f"source-failed-{'-'.join(failed)}",
                           f"MNV: dashboard source(s) failed: {', '.join(failed)}"))

    coverage = status.get("coverage") or {}
    total, measured = coverage.get("nodes_total") or 0, coverage.get("nodes_measured") or 0
    if total and measured / total < COVERAGE_ALERT_FRACTION:
        conditions.append(("coverage-low",
                           f"MNV: only {measured}/{total} login nodes measurable"))
    return conditions


def send_alerts(
    status: dict,
    state_dir: Path,
    window_seconds: int = DEFAULT_ALERT_WINDOW_SECONDS,
    dry_run: bool = False,
    clock: Clock | None = None,
) -> list[str]:
    """Hand each firing condition to notifyctl, which owns channels and de-duplication.

    Deliberately a subprocess call rather than an ntfy client: notifyctl already holds
    the topic secret, the 0600 mode check, the channel config and the sent-marker
    dedupe.  Reimplementing any of that here would be a second place to get it wrong.
    """
    clock = clock or Clock()
    bucket = int(clock.now() // window_seconds)
    sent: list[str] = []
    for condition, subject in alert_conditions(status):
        key = f"mnv-dashboard:{condition}:{bucket}"
        if dry_run:
            sent.append(f"[dry-run] key={key} subject={subject}")
            continue
        argv = [
            sys.executable, str(HERE / "notifyctl.py"),
            "--secrets", str(state_dir / "notification-secrets.json"),
            "send", "--key", key, "--subject", subject,
        ]
        try:
            completed = subprocess.run(
                argv, input="", capture_output=True, text=True, timeout=60, check=False
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            sent.append(f"FAILED {condition}: {type(exc).__name__}: {exc}")
            continue
        sent.append(
            f"sent {condition}" if completed.returncode == 0
            else f"FAILED {condition}: rc={completed.returncode} {completed.stderr.strip()[:120]}"
        )
    return sent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--state-dir",
        default=os.environ.get("WAKER_STATE_DIR", str(HERE / "state" / "waker")),
        help="waker state directory holding last-tick.json and agent-sessions-v2.json",
    )
    parser.add_argument("--out", help="write status.json here (atomically); default stdout")
    parser.add_argument("--sweep-timeout", type=float, default=8.0)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument(
        "--print-scrontab",
        action="store_true",
        help="print the scrontab block to install, and exit without collecting",
    )
    parser.add_argument("--interval-minutes", type=int, default=5)
    parser.add_argument(
        "--alert", action="store_true",
        help="after collecting, notify via notifyctl about conditions worth interrupting for",
    )
    parser.add_argument(
        "--alert-dry-run", action="store_true",
        help="print the alerts that would be sent, without sending them",
    )
    parser.add_argument("--alert-window-seconds", type=int, default=DEFAULT_ALERT_WINDOW_SECONDS)
    parser.add_argument(
        "--local-only", action="store_true",
        help="collect only what must be measured on this device (LLM sessions) and exit",
    )
    parser.add_argument("--no-usage", action="store_true",
                        help="skip the usagectl account-capacity call")
    parser.add_argument(
        "--keep-paths", action="store_true",
        help="do NOT shorten absolute filesystem paths (default is to shorten them, "
             "because portal.nersc.gov serves the output to the open internet)",
    )
    args = parser.parse_args()

    if args.print_scrontab:
        print("\n".join(scrontab_block(args, Path(args.state_dir))))
        return 0

    if args.local_only:
        print(json.dumps(build_local_status(), indent=2 if args.pretty else None, sort_keys=True))
        return 0

    status = build_status(
        Path(args.state_dir).expanduser(),
        sweep_timeout=args.sweep_timeout,
        with_usage=not args.no_usage,
    )
    if not args.keep_paths:
        status = redact_paths(status)
    if args.out:
        out = Path(args.out).expanduser()
        guard_output_path(out, Path(args.state_dir).expanduser())
        agentctl.atomic_write_json(out, status)
        # A web-served file must be world-readable; the directory mode is the operator's
        # job and is checked by the runbook's verification step.
        os.chmod(out, 0o644)
        print(f"wrote {out} ({len(status['jobs'])} jobs, "
              f"{status['coverage']['nodes_measured']}/{status['coverage']['nodes_total']} nodes)")
    else:
        print(json.dumps(status, indent=2 if args.pretty else None, sort_keys=True))

    # Alerting runs after the snapshot is durable, so a notification failure never costs
    # the collection.
    if args.alert or args.alert_dry_run:
        for line in send_alerts(
            status,
            Path(args.state_dir).expanduser(),
            window_seconds=args.alert_window_seconds,
            dry_run=args.alert_dry_run,
        ):
            print(line)
    return 0


ABSOLUTE_PATH = re.compile(r"(/(?:global|pscratch|tmp|home|homes|u2|usr|var|opt)/[^\s,;:'\"]*)")


def shorten_path(match: "re.Match[str]") -> str:
    """Reduce an absolute path to its FINAL segment only.

    Measured 2026-08-30: `portal.nersc.gov/cfs/<project>/` is served to the open
    internet with no authentication, so a path published there discloses the account
    name and the project's directory layout to anyone who has the URL.  Nothing the
    dashboard renders needs the full path.

    It keeps one segment, not two, because on this filesystem the account name is the
    SECOND-TO-LAST segment of a checkout root: keeping two turned
    `/pscratch/sd/j/josephrb/MINERvA-OmniFold` into `.../josephrb/MINERvA-OmniFold`,
    which is exactly the disclosure this function exists to prevent.
    """
    parts = [part for part in match.group(1).split("/") if part]
    return ".../" + parts[-1] if len(parts) > 1 else match.group(1)


def redact_paths(value):
    """Recursively shorten absolute filesystem paths in a snapshot.

    Applied by default even though the science gateway was declined and nothing is
    published, so that enabling any delivery path later cannot leak by omission.  Use
    `--keep-paths` for a local copy where the full paths are useful.
    """
    if isinstance(value, str):
        return ABSOLUTE_PATH.sub(shorten_path, value)
    if isinstance(value, list):
        return [redact_paths(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_paths(item) for key, item in value.items()}
    return value


def guard_output_path(out: Path, state_dir: Path) -> None:
    """Refuse to write the snapshot anywhere under the waker state directory.

    `state/` holds `notification-secrets.json`.  The dashboard's output is intended for a
    world-readable web path, so the two must never share a directory.
    """
    try:
        out.resolve().relative_to(state_dir.resolve())
    except (ValueError, OSError):
        return
    raise SystemExit(
        f"refusing to write {out}: it is inside the waker state directory {state_dir}, "
        "which holds notification-secrets.json and must never be web-readable"
    )


SCRON_BEGIN = "# BEGIN mnv-dashboard managed block"
SCRON_END = "# END mnv-dashboard managed block"


def scrontab_block(args, state_dir: Path) -> list[str]:
    """The scrontab lines to install.

    Deliberately printed rather than written: `wakerctl install-cron` replaces the ENTIRE
    table, and ISSUE-42 records that a failed listing there once meant silent deletion of
    every unmanaged line.  A second tool that rewrites the shared table is a second way to
    lose the other lane's entries, so this one emits text for the operator to paste and
    the runbook carries the save/install/diff procedure.

    Markers differ from wakerctl's, so `wakerctl install-cron` -- which strips only its own
    block -- preserves these lines.
    """
    log = state_dir / "logs" / "dashboard-collector.log"
    # Default to a private path on the cluster, NOT the project web space: the science
    # gateway would make m3246 publicly servable for the whole group, which is a posture
    # change nobody asked that group for.  dashboard_serve.py reads this over SSH.
    out = args.out or str(HERE / "state" / "dashboard" / "status.json")
    return [
        SCRON_BEGIN,
        "#SCRON -q cron",
        # The cron QOS caps MaxWall at 1-00:00:00 even though the cron PARTITION allows
        # 90 days, so a longer request is rejected.  A collection is seconds of work; a
        # tight wall means a wedged sweep is killed instead of holding the slot.
        "#SCRON -t 00:20:00",
        f"#SCRON -o {log}",
        "#SCRON --open-mode=append",
        f"*/{args.interval_minutes} * * * * {sys.executable} {HERE / 'dashboard_collector.py'} "
        f"--state-dir {state_dir} --out {out} --alert",
        SCRON_END,
    ]


if __name__ == "__main__":
    raise SystemExit(main())
