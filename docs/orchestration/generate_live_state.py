#!/usr/bin/python3.11
"""Generate the concise orchestration dashboard from live and machine sources."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Any

from slurm_array_status import build_snapshot, expand_spec


HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_CONFIG = HERE / "state" / "live-state.json"
DEFAULT_OUTPUT = HERE / "LIVE-STATE.md"
MAX_LINES = 120
# Kinds whose watch has a SLURM SUBJECT that can be checked for existence.
WATCH_SUBJECT_KINDS = {"slurm-job", "slurm-array"}
# Used only when the managed scrontab block cannot be read or parsed, and always
# rendered with the word "assumed" so it is never mistaken for an observation.
# It matches `wakerctl cron --interval-minutes`' default (wakerctl.py argparse).
ASSUMED_TICK_INTERVAL_MINUTES = 5
# Three severities, because two are not enough: a check that can only say
# PASS/FAIL has to call "I could not look" one of them, and BEN-323 is what
# happens when it picks PASS.
QUIET, NO_EVIDENCE, LOUD = "quiet", "no-evidence", "loud"
# Where each probe's last MEASURED value is kept. Tracked and committed on
# purpose: the whole point of OI-144 is that the cluster's Slurm measurement
# survives into a snapshot regenerated from a laptop, and the laptop's provider
# capacity survives into one regenerated from a login node. A store that did not
# travel through git could not do that.
LAST_KNOWN_PATH = HERE / "state" / "live-state-last-known.json"
LEGACY_PROSE_FIELDS = frozenset(
    {"current_dag_node", "state", "next_authorized_action"}
)
# The structured-routing interface frozen 2026-09-03
# (INTEGRATION-20260903-wave1-routing-freeze-and-ledger.md §1). The lifecycle and queue
# vocabularies are OWNED by control-plane/policy.json `routing`, which the registry config names
# as `policy`; the generator reads them from there rather than restating them (reviewer round 2:
# two copies of the schema enforced different subsets). Promotion has no policy field; it is the
# register's own two-token vocabulary, mirrored from control_plane_lint.py.
ROUTED_LIFECYCLE = "active"
ROUTED_PROMOTION = "promoted"
PROMOTION_TOKENS = frozenset({"promoted", "backlog"})
UNSET = "-"
ROUTE_REGISTRY_KEYS = frozenset({"work_items", "source_inventory", "open_items", "policy"})
WORK_ITEM_COLUMNS = (
    "item",
    "source_record",
    "lifecycle",
    "queue",
    "promotion",
    "owner_id",
    "impact",
    "urgency",
    "artifact",
    "next_action",
    "authority",
    "terminal_criterion",
    "evidence",
    "state_digest",
)
SOURCE_INVENTORY_COLUMNS = (
    "source_record",
    "lifecycle",
    "queue",
    "classification_rule",
    "source_row_sha256",
    "state_prefix",
)


@dataclass(frozen=True)
class Route:
    """One current-work route resolved from the structured registry."""

    item: str
    queue: str
    source_record: str


@dataclass(frozen=True)
class RouteSnapshot:
    """Measured consistency and routes for the current-work registry."""

    health: str
    detail: str
    routes: tuple[Route, ...] = ()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def validate_config(config: dict[str, Any]) -> None:
    """Validate the closed version-2 measurement configuration.

    The checked-in JSON Schema is the public contract. This standard-library
    validator enforces the safety-critical portion at runtime, including the
    prohibition on legacy authored operational prose.
    """
    allowed = {
        "schema_version",
        "measurement_ttl_seconds",
        "route_registry",
        "evidence_routes",
        "jobs",
        "wake",
    }
    unknown = set(config) - allowed
    legacy = set(config) & LEGACY_PROSE_FIELDS
    if legacy:
        raise ValueError(
            "legacy authored operational prose is forbidden: "
            + ", ".join(sorted(legacy))
        )
    if unknown:
        raise ValueError("unknown live-state fields: " + ", ".join(sorted(unknown)))
    if config.get("schema_version") != 2:
        raise ValueError("schema_version must be 2")

    ttl = _require_mapping(config.get("measurement_ttl_seconds"), "measurement_ttl_seconds")
    if set(ttl) != {"compute", "wake", "provider_capacity"}:
        raise ValueError("measurement_ttl_seconds has unexpected or missing fields")
    for name, value in ttl.items():
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"measurement_ttl_seconds.{name} must be a positive integer")

    registry = _require_mapping(config.get("route_registry"), "route_registry")
    if set(registry) != ROUTE_REGISTRY_KEYS:
        raise ValueError("route_registry has unexpected or missing fields")
    if not all(isinstance(value, str) and value for value in registry.values()):
        raise ValueError("route_registry paths must be non-empty strings")

    routes = config.get("evidence_routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError("evidence_routes must be a non-empty array")
    for index, route in enumerate(routes):
        route = _require_mapping(route, f"evidence_routes[{index}]")
        if not {"label", "path"} <= set(route) or set(route) - {
            "label",
            "path",
            "json_field",
        }:
            raise ValueError(f"evidence_routes[{index}] has unexpected or missing fields")
        if not all(isinstance(route[key], str) and route[key] for key in route):
            raise ValueError(f"evidence_routes[{index}] values must be non-empty strings")

    jobs = config.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("jobs must be an array")
    required_job = {"job_id", "tasks", "receipt"}
    allowed_job = required_job | {"leg", "single_job"}
    for index, job in enumerate(jobs):
        job = _require_mapping(job, f"jobs[{index}]")
        if not required_job <= set(job) or set(job) - allowed_job:
            raise ValueError(f"jobs[{index}] has unexpected or missing fields")
        if not str(job["job_id"]).isdigit():
            raise ValueError(f"jobs[{index}].job_id must contain digits only")

    wake = _require_mapping(config.get("wake"), "wake")
    if wake != {"waker": True}:
        raise ValueError("wake must select the measured waker source")


def _read_tsv(path: pathlib.Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != columns:
            raise ValueError(
                f"{path}: columns {reader.fieldnames!r}, expected {list(columns)!r}"
            )
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
        ]


def _source_rows(path: pathlib.Path) -> dict[str, tuple[str, str]]:
    matches: list[tuple[str, str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*(OI-\d+)\s*\|\s*([^|]+)\|", line)
        if match:
            state = re.sub(r"\s+", " ", re.sub(r"[*`~]", "", match.group(2)))
            matches.append((match.group(1), state.strip()[:120].rstrip(), line))
    totals: dict[str, int] = {}
    for item, _, _ in matches:
        totals[item] = totals.get(item, 0) + 1
    seen: dict[str, int] = {}
    records: dict[str, tuple[str, str]] = {}
    for item, state_prefix, line in matches:
        seen[item] = seen.get(item, 0) + 1
        key = f"{item}#{seen[item]}" if totals[item] > 1 else item
        records[key] = (hashlib.sha256(line.encode()).hexdigest(), state_prefix)
    return records


def _routing_vocabulary(policy_path: pathlib.Path) -> tuple[frozenset[str], frozenset[str]]:
    """Return (lifecycles, queues) declared by policy.json's `routing` block."""
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    routing = policy.get("routing") if isinstance(policy, dict) else None
    if not isinstance(routing, dict):
        raise ValueError(f"{policy_path}: no `routing` block")
    vocab = []
    for key in ("lifecycles", "queues"):
        values = routing.get(key)
        if (
            not isinstance(values, list)
            or not values
            or not all(isinstance(v, str) and v and v != UNSET for v in values)
        ):
            raise ValueError(f"{policy_path}: routing.{key} must be a non-empty list of tokens")
        vocab.append(frozenset(values))
    return vocab[0], vocab[1]


def inspect_route_registry(
    *,
    work_items_path: pathlib.Path,
    source_inventory_path: pathlib.Path,
    open_items_path: pathlib.Path,
    policy_path: pathlib.Path,
) -> RouteSnapshot:
    """Measure route-registry availability and internal consistency."""
    try:
        work_items = _read_tsv(work_items_path, WORK_ITEM_COLUMNS)
        inventory_rows = _read_tsv(source_inventory_path, SOURCE_INVENTORY_COLUMNS)
        source_rows = _source_rows(open_items_path)
        lifecycles, queues = _routing_vocabulary(policy_path)
    except (OSError, ValueError, csv.Error) as exc:
        return RouteSnapshot("UNAVAILABLE", f"{type(exc).__name__}: {exc}")

    contradictions: list[str] = []
    inventory: dict[str, dict[str, str]] = {}
    for row in inventory_rows:
        key = row["source_record"]
        if not key or key in inventory:
            contradictions.append(f"duplicate or empty source record {key!r}")
        inventory[key] = row
        source = source_rows.get(key)
        if source and source[0] == row["source_row_sha256"]:
            _, actual_prefix = source
            if actual_prefix != row["state_prefix"]:
                contradictions.append(
                    f"{key}: inventory state prefix contradicts its hashed source row"
                )

    # Completeness in both directions, so an omission cannot read as HEALTHY: every source record
    # in OPEN_ITEMS must be inventoried, and every inventoried record must have a register row.
    # (Reviewer mutations 2026-09-03: an unregistered OI and a deleted register row both rendered
    # HEALTHY before this check existed.)
    unregistered = sorted(set(source_rows) - set(inventory))
    if unregistered:
        contradictions.append(
            f"{len(unregistered)} source record(s) absent from the inventory: "
            + ", ".join(unregistered[:5])
            + ("" if len(unregistered) <= 5 else f" and {len(unregistered) - 5} more")
        )
    registered = {row["source_record"] for row in work_items}
    unrouted = sorted(set(inventory) - registered)
    if unrouted:
        contradictions.append(
            f"{len(unrouted)} inventory record(s) with no register row: "
            + ", ".join(unrouted[:5])
            + ("" if len(unrouted) <= 5 else f" and {len(unrouted) - 5} more")
        )

    routes: list[Route] = []
    seen_items: set[str] = set()
    for row in work_items:
        item = row["item"]
        source = row["source_record"]
        if not item or item in seen_items:
            contradictions.append(f"duplicate or empty work item {item!r}")
        seen_items.add(item)
        record = inventory.get(source)
        if record is None:
            contradictions.append(f"{item}: source record {source!r} is absent")
            continue
        parent = re.match(r"OI-\d+", item)
        if parent is None or source.split("#", 1)[0] != parent.group(0):
            contradictions.append(f"{item}: source record {source!r} has a different parent")
        # Lifecycle is a property of the SOURCE RECORD. A sub-item row (`OI-131(a)`) carries
        # UNSET and inherits its record's lifecycle; a record's own row must agree with the
        # inventory, which control_plane_lint.py --write derives from the same register.
        # Every token is validated against the frozen vocabulary BEFORE any row is skipped, so a
        # misspelt token ("promtoed", "activ") is a contradiction and never a silent non-route
        # (reviewer round 2 mutations).
        lifecycle, promotion, queue = row["lifecycle"], row["promotion"], row["queue"]
        if lifecycle != UNSET and lifecycle not in lifecycles:
            contradictions.append(f"{item}: invalid lifecycle {lifecycle!r}")
            continue
        if promotion != UNSET and promotion not in PROMOTION_TOKENS:
            contradictions.append(f"{item}: invalid promotion {promotion!r}")
            continue
        if queue != UNSET and queue not in queues:
            contradictions.append(f"{item}: invalid queue {queue!r}")
            continue
        if record["lifecycle"] not in lifecycles:
            contradictions.append(f"{item}: inventory lifecycle {record['lifecycle']!r} invalid")
            continue
        if lifecycle != UNSET and lifecycle != record["lifecycle"]:
            contradictions.append(
                f"{item}: register lifecycle {lifecycle!r} contradicts inventory "
                f"{record['lifecycle']!r}"
            )
        if record["lifecycle"] != ROUTED_LIFECYCLE:
            if (promotion, queue) != (UNSET, UNSET):
                contradictions.append(
                    f"{item}: non-active row must carry '-' promotion and queue"
                )
            continue  # deferred/retired rows are inventory, never routes
        if promotion == UNSET or queue == UNSET:
            contradictions.append(f"{item}: active row must declare promotion and queue")
            continue
        if promotion != ROUTED_PROMOTION:
            continue  # backlog rows are inventory, never routes
        if item == source and queue != record["queue"]:
            contradictions.append(
                f"{item}: register queue {queue!r} contradicts inventory {record['queue']!r}"
            )
        routes.append(Route(item, queue, source))

    if contradictions:
        return RouteSnapshot("CONTRADICTORY", "; ".join(contradictions))

    stale = [
        key
        for key, record in inventory.items()
        if source_rows.get(key, (None, None))[0] != record["source_row_sha256"]
    ]
    if stale:
        preview = ", ".join(stale[:5])
        suffix = "" if len(stale) <= 5 else f" and {len(stale) - 5} more"
        return RouteSnapshot(
            "STALE",
            f"{len(stale)} source row hash mismatch(es): {preview}{suffix}",
        )

    return RouteSnapshot(
        "HEALTHY",
        f"{len(routes)} promoted route(s) agree with {len(inventory)} source record(s)",
        tuple(routes),
    )


def _repo_path(repo_root: pathlib.Path, value: str) -> pathlib.Path:
    path = pathlib.Path(value)
    if path.is_absolute():
        raise ValueError(f"repository route must be relative: {value}")
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"repository route escapes the checkout: {value}") from exc
    return resolved


def route_registry_snapshot(config: dict[str, Any], repo_root: pathlib.Path) -> RouteSnapshot:
    registry = config["route_registry"]
    try:
        paths = {
            key: _repo_path(repo_root, value) for key, value in registry.items()
        }
    except ValueError as exc:
        return RouteSnapshot("CONTRADICTORY", str(exc))
    return inspect_route_registry(
        work_items_path=paths["work_items"],
        source_inventory_path=paths["source_inventory"],
        open_items_path=paths["open_items"],
        policy_path=paths["policy"],
    )


def run_text(command: list[str], *, check: bool = True) -> str:
    result = subprocess.run(command, cwd=REPO, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}: {result.stderr.strip()}")
    return result.stdout


def usage_snapshot() -> tuple[dict[str, Any], int]:
    result = subprocess.run(
        [sys.executable, str(HERE / "usagectl.py"), "snapshot", "--json"],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    try:
        return json.loads(result.stdout), result.returncode
    except json.JSONDecodeError:
        return {"gate_ok": False, "warnings": [f"usage snapshot unavailable (rc={result.returncode})"]}, result.returncode


def rel_link(repo_path: str) -> str:
    if repo_path == "superseded followup prompts":
        return repo_path
    target = pathlib.Path(repo_path)
    return os.path.relpath(REPO / target, HERE)


def codex_capacity(usage: dict[str, Any], profile: str) -> str:
    record = usage.get("profiles", {}).get(profile, {})
    window = record.get("windows", {}).get("seven_day", {})
    remaining = window.get("remaining_percent", "unknown")
    reset = window.get("resets_at_utc", "unknown")
    credits = record.get("reset_credits", {})
    available = credits.get("valid_available_full_reset_count", "unknown")
    protected = credits.get("protected_reserve", "unknown")
    return f"{remaining}% weekly remaining; reset {reset}; Full resets {available} available/{protected} protected"


# ---------------------------------------------------------------------------
# Carry-forward for probes THIS host cannot run (OI-144).
#
# Until 2026-08-21 every field this generator could not measure was OVERWRITTEN
# with the local non-observation, so no single host could produce a fully
# measured LIVE-STATE.md. Measured that day at one commit: from a laptop the
# Slurm rows blanked while the usage section was real; from a Perlmutter login
# node Slurm was real while the usage helper could not read a single profile
# home, so `Usage gate` degraded to BLOCKED/UNKNOWN and every percentage became
# `unknown`. Each regeneration traded one section's truth for another's, and
# nothing in the output separated "measured as absent" from "this host could not
# look" -- BEN-323's conflation one level up, at the scale of a whole section.
#
# THE RULE HERE, and every renderer below obeys it:
#   * a probe that RAN records its value with the host and UTC time that
#     measured it, into a tracked store that travels through git;
#   * a probe that COULD NOT RUN renders the last recorded value, attributed and
#     aged, and NEVER in the vocabulary of a current verdict.
# A carried value is history. It is not evidence that anything is true now, so
# no carried render may emit a live state word (`ACTIVE`, `FRESH`, `PASS`,
# `subject OBSERVED`) in the position a reader takes as this snapshot's finding.
# That is why the formatters below re-word rather than replay the live text.


def hostname() -> str:
    try:
        return socket.gethostname() or "unknown-host"
    except OSError:
        return "unknown-host"


def parse_stamp(value: Any) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def age_between(then: Any, now: Any) -> str:
    """`age_phrase` across two ISO stamps, or "" if either one cannot be parsed.

    Returns "" rather than a guess: an age that cannot be computed must not be
    rendered as a small one, which is the same failure as rendering an
    unreachable scheduler as ACTIVE.
    """
    start, end = parse_stamp(then), parse_stamp(now)
    if start is None or end is None:
        return ""
    return age_phrase((end - start).total_seconds())


class LastKnown:
    """Per-probe last MEASURED value, with the host and timestamp that measured it.

    `record` is called ONLY on a real observation and `get` is read ONLY where
    this host could not observe; keeping those two callers disjoint is what stops
    a carried value from laundering itself into a measurement. An instance built
    with `path=None` -- the default inside `render`, and therefore what every
    unit test gets -- neither loads nor persists anything, so a caller that
    passes no store carries nothing and writes nothing.
    """

    def __init__(
        self,
        path: pathlib.Path | None = None,
        *,
        host: str | None = None,
        observed_at: str | None = None,
        head: str | None = None,
    ) -> None:
        self.path = path
        self.host = host or hostname()
        self.observed_at = observed_at
        self.head = head
        self.probes: dict[str, Any] = {}
        self.changed = False
        if path is not None and path.exists():
            try:
                loaded = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError):
                # A corrupt store must degrade to "no history", never take the
                # dashboard down: the whole feature exists for degraded hosts.
                loaded = {}
            if isinstance(loaded, dict) and isinstance(loaded.get("probes"), dict):
                self.probes = loaded["probes"]

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self.probes.get(key)
        return entry if isinstance(entry, dict) and "value" in entry else None

    def record(self, key: str, value: Any) -> None:
        self.probes[key] = {
            "value": value,
            "host": self.host,
            "at_utc": self.observed_at,
            "git_head": self.head,
        }
        self.changed = True

    def save(self) -> bool:
        """Persist iff something was actually measured this run. Returns whether it wrote."""
        if self.path is None or not self.changed:
            return False
        payload = {
            "schema_version": 1,
            "_what": (
                "GENERATED by generate_live_state.py; do not hand-edit. One entry per probe: the"
                " last value actually MEASURED, plus the host and UTC time that measured it. A"
                " host that cannot run a probe carries the entry into LIVE-STATE.md as attributed"
                " history instead of overwriting the field (OI-144). An entry here becomes a"
                " published statement about what some host observed, so editing one by hand"
                " fabricates an observation."
            ),
            "probes": dict(sorted(self.probes.items())),
        }
        atomic_write(self.path, json.dumps(payload, indent=2) + "\n")
        return True


def measured_by(entry: dict[str, Any], observed_at: str) -> str:
    host = entry.get("host") or "an unrecorded host"
    at = entry.get("at_utc") or "an unrecorded time"
    text = f"measured on `{host}` at `{at}`"
    age = age_between(at, observed_at)
    if age:
        text += f", {age} before this snapshot"
    head = entry.get("git_head")
    if head:
        text += f", at commit `{head}`"
    return text


def carried(entry: dict[str, Any] | None, observed_at: str, formatter, what: str) -> str:
    """Render a probe this host could not run, from the last host that could.

    An absent entry is its own answer and says so: "no history" and "history I am
    withholding" must not render the same way either.
    """
    if entry is None:
        return (
            f"NO LAST-KNOWN VALUE EITHER: no host has ever recorded {what} in"
            " `state/live-state-last-known.json`, so this snapshot has no history to offer."
        )
    return (
        f"LAST KNOWN, NOT MEASURED HERE: {formatter(entry.get('value'))}"
        f" -- {measured_by(entry, observed_at)}. THIS HOST COULD NOT LOOK, so that is history,"
        " not a claim about now."
    )


def _fmt_compute(value: Any) -> str:
    value = value if isinstance(value, dict) else {}
    return (
        f"job state was {value.get('overall', 'unknown')} with counts"
        f" {value.get('counts', 'unknown')}; errors {value.get('errors', 'unknown')}"
    )


def _fmt_watches(value: Any) -> str:
    value = value if isinstance(value, dict) else {}
    armed = value.get("armed") or []
    listed = ", ".join(f"`{item}`" for item in armed) if armed else "none armed"
    return (
        f"{value.get('count', '?')} watch record(s), {len(armed)} armed ({listed}); worst"
        f" severity recorded then: {value.get('worst', 'unknown')}"
    )


def _fmt_events(value: Any) -> str:
    value = value if isinstance(value, dict) else {}
    return f"{value.get('count', '?')} event record(s): {value.get('summary', 'unknown')}"


def _fmt_tick(value: Any) -> str:
    value = value if isinstance(value, dict) else {}
    return (
        f"tick receipt `{value.get('at_utc', 'unknown')}` on `{value.get('node', 'unknown')}`,"
        f" which the last host that could judge it classified `{value.get('verdict', 'unknown')}`"
    )


def _fmt_gate(value: Any) -> str:
    value = value if isinstance(value, dict) else {}
    return f"the usage gate read {value.get('verdict', 'unknown')} (helper rc={value.get('rc', '?')})"


def _fmt_text(value: Any) -> str:
    return str(value)


# ---------------------------------------------------------------------------
# Wake-section health.
#
# EVERY verdict below is computed by calling wakerctl's own checks -- never by
# reimplementing them here. The renderer and the evaluator must not be able to
# disagree about whether a watch's subject exists or whether the ticker is
# alive; two implementations of one predicate diverge, and the divergence is
# invisible precisely because both look right in isolation. So this module owns
# the WORDS and wakerctl owns the JUDGEMENT.


def _wakerctl():
    """Imported lazily: the non-waker wake path must not pay for it."""
    import wakerctl

    return wakerctl


def classify_problems(problems: list[str]) -> str:
    """QUIET (no problems) / NO_EVIDENCE (only unobservability) / LOUD (a finding).

    A `NO EVIDENCE:` line means the check could not run. Silence and NO EVIDENCE
    must never render the same way -- that conflation is BEN-323, where an
    unreachable Slurm rendered as **ACTIVE** for 24 h.
    """
    wakerctl = _wakerctl()
    if not problems:
        return QUIET
    if all(str(item).startswith(wakerctl.NO_EVIDENCE_PREFIX) for item in problems):
        return NO_EVIDENCE
    return LOUD


def safe_health_call(function, *args) -> list[str]:
    """Run a wakerctl health check, converting unreachability into NO EVIDENCE.

    This generator is routinely run from a Mac with no `squeue`, `sacct` or
    `scrontab` on PATH, and wakerctl's checks call `ctx.runner` directly, so a
    missing binary surfaces as FileNotFoundError rather than a return code. A
    crash here would take the whole dashboard down; a swallowed exception would
    render as health. Neither is acceptable, so it becomes NO EVIDENCE.
    """
    wakerctl = _wakerctl()
    try:
        return list(function(*args))
    except OSError as exc:
        return [wakerctl.no_evidence(f"{type(exc).__name__}: {exc} (this host cannot query the scheduler)")]
    except Exception as exc:  # noqa: BLE001 -- an unassessable check is NO EVIDENCE, never PASS
        return [wakerctl.no_evidence(f"check raised {type(exc).__name__}: {exc}")]


def age_phrase(seconds: float) -> str:
    if abs(seconds) >= 7200:
        return f"{seconds / 3600.0:.1f} h"
    return f"{seconds / 60.0:.0f} min"


def watch_subject_text(watch: dict[str, Any]) -> str:
    """The watch's SUBJECT: job id, the `tasks` spec AS WRITTEN, and its expansion.

    Until 2026-08-19 a watch rendered as `id`(kind:state) and nothing else, so
    `gate5-do-train-57266000-r2` displayed as `armed` for ~45 h while its
    params were {"job_id": "57266000", "tasks": "1"} against an array whose only
    task is index 0. `tasks` is a task-id SPEC and never a count --
    expand_spec("1") == [1] -- and the expansion is printed here because that
    single fact is what nobody could see. A stored `state` field is not a
    liveness claim (BEN-456, BEN-478).
    """
    kind = watch.get("kind")
    if kind not in WATCH_SUBJECT_KINDS:
        return ""
    params = watch.get("params")
    if not isinstance(params, dict):
        # wakerctl.status() projects watches to six keys and `params` is not one
        # of them, so this is what a status-only record looks like.
        return "; subject=UNKNOWN (this record carries no `params`)"
    job_id = str(params.get("job_id", "")).strip() or "<missing>"
    if kind != "slurm-array":
        return f"; subject=job {job_id}"
    raw = str(params.get("tasks", ""))
    try:
        expanded = expand_spec(raw)
    except ValueError as exc:
        return f"; subject=job {job_id} tasks={raw!r} INVALID SPEC ({exc})"
    return f"; subject=job {job_id} tasks={raw!r} -> task ids {expanded}"


def watch_subject_verdict(watch: dict[str, Any], waker_ctx) -> tuple[str, str]:
    """Is this watch's subject OBSERVABLE? Delegated to wakerctl entirely.

    `wakerctl.watch_subject_problems` builds its snapshot with
    `slurm_array_status.build_snapshot`, the same function `evaluate()` uses, so
    the render cannot disagree with the evaluator.
    """
    if waker_ctx is None:
        return NO_EVIDENCE, "NO EVIDENCE its subject exists: Slurm was not asked in this run"
    wakerctl = _wakerctl()
    problems = safe_health_call(wakerctl.watch_subject_problems, waker_ctx, watch)
    severity = classify_problems(problems)
    detail = " | ".join(str(item) for item in problems)
    if severity == QUIET:
        return QUIET, "subject OBSERVED in Slurm"
    if severity == NO_EVIDENCE:
        return NO_EVIDENCE, f"{detail} -- NOT a claim the subject exists"
    return LOUD, f"**\u26a0 {detail}**"


def _watch_store_readable(ctx: Any) -> bool:
    """True only if this host can actually enumerate the watch store.

    Distinguishes "I looked and there are none" from "I could not look". The
    caller renders the first as `none` and the second as NO EVIDENCE.
    """
    try:
        store = pathlib.Path(ctx.state_dir) / "watches"
        return store.is_dir() and os.access(store, os.R_OK)
    except Exception:
        return False


def _events_dir_readable(ctx: Any) -> bool:
    """True only if this host can actually enumerate the event store.

    `wakerctl.status()` returns `events: []` when `ctx.events_dir` is not a
    directory, exactly as it returns `watches: []` -- and the events line
    rendered that as `none` long after the watches line had been fixed to say
    NO EVIDENCE. Same defect, same section, one bullet apart.
    """
    try:
        store = pathlib.Path(ctx.events_dir)
        return store.is_dir() and os.access(store, os.R_OK)
    except Exception:
        return False


def render_watch(watch: dict[str, Any], waker_ctx) -> tuple[str, str]:
    """(severity, rendered) for one watch. Never renders `state` alone."""
    wakerctl = _wakerctl()
    watch_id = watch.get("watch_id") or "<no-watch_id>"
    kind = watch.get("kind")
    state = wakerctl.watch_state(watch) or "<no-state>"
    body = f"`{watch_id}`({kind}:{state}{watch_subject_text(watch)}"
    if kind not in WATCH_SUBJECT_KINDS:
        return QUIET, body + ")"
    # WHOLE-FIELD equality, never a substring: "disarmed" CONTAINS "armed", and a
    # `grep -c '<job>.*armed'` health check has already reported 2 armed watches
    # for a job that had one armed and one disarmed (2026-08-19).
    if not wakerctl.is_armed(watch):
        return QUIET, body + "; not armed, so its subject was not probed)"
    severity, verdict = watch_subject_verdict(watch, waker_ctx)
    return severity, f"{body}; {verdict})"


def safe_load_watches(waker_ctx) -> list[dict[str, Any]]:
    try:
        return _wakerctl().load_watches(waker_ctx)
    except OSError:
        return []


def tick_interval_minutes(waker_ctx) -> tuple[int, str]:
    """(minutes, how we know) -- parsed from the managed scrontab block if readable."""
    wakerctl = _wakerctl()
    fallback = (
        ASSUMED_TICK_INTERVAL_MINUTES,
        f"{ASSUMED_TICK_INTERVAL_MINUTES} m ASSUMED (the managed scrontab block was not readable here)",
    )
    if waker_ctx is None:
        return fallback
    try:
        lines, _ = wakerctl.read_scrontab_lines(waker_ctx)
    except OSError:
        return fallback
    if lines is None:
        return fallback
    interval = wakerctl.cron_interval_minutes(lines)
    if interval is None:
        return fallback
    return interval, f"{interval} m from the managed scrontab block"


def tick_line(last_tick: dict[str, Any], waker_ctx) -> tuple[str, str]:
    """(severity, the `Last tick:` bullet) -- a VERDICT, not a transcription.

    Before 2026-08-19 this printed `Last tick: {at_utc}` verbatim. On that day it
    would have read 2026-08-17T15:05:14+00:00 against a wall clock of
    2026-08-19T12:40Z: the number that proved the supervision net was dead had
    been on the repo's first-read page, unjudged, for two days (ISSUE-52 --
    WAKER.md:52 already stated the rule in prose, and a rule that exists only as
    prose is not a control).

    BEN-199 governs the shape: the FRESH case is quiet and unalarming, because a
    check with no passing state is a check nobody reads.
    """
    wakerctl = _wakerctl()
    stamp = last_tick.get("at_utc", "never")
    node = last_tick.get("node", "unknown")
    prefix = f"- Last tick: {stamp} on {node}"
    suffix = " (scrontab is the supervision net; see WAKER.md)"
    interval, interval_source = tick_interval_minutes(waker_ctx)
    multiplier = wakerctl.DEFAULT_CRON_STALE_MULTIPLIER
    if waker_ctx is not None:
        multiplier = float(waker_ctx.config.get("cron_stale_multiplier", multiplier))
    bound = f"bound {interval * multiplier:.0f} min = {interval_source} x {multiplier:g}"

    age = None
    if waker_ctx is not None and stamp not in (None, "", "never"):
        try:
            age = waker_ctx.now() - wakerctl.parse_utc(str(stamp))
        except (TypeError, ValueError):
            age = None
    age_text = f"{age_phrase(age)} old" if age is not None else "age NOT COMPUTABLE from this stamp"

    if waker_ctx is None:
        return NO_EVIDENCE, (
            f"{prefix} -- **NO EVIDENCE ABOUT THE TICKER, AND THAT IS NOT A LIVENESS CLAIM**: this"
            f" run had no waker state dir, so neither the tick receipt nor the scrontab was read"
            f" and this timestamp is UNJUDGED.{suffix}"
        )
    # One call covers all three a0a31176 control-plane checks that bear on the
    # ticker: the managed block's presence, `check_cron_job_runnable` (is the
    # scron job RUNNABLE in Slurm, not merely scheduled), and
    # `check_tick_freshness` (is the heartbeat younger than its own interval).
    problems = safe_health_call(wakerctl.check_cron_ticker, waker_ctx)
    severity = classify_problems(problems)
    if severity == QUIET:
        return QUIET, f"{prefix} -- FRESH, {age_text}; {bound}; scron tick job runnable.{suffix}"
    detail = " | ".join(str(item) for item in problems)
    if severity == NO_EVIDENCE:
        return NO_EVIDENCE, (
            f"{prefix} -- **NO EVIDENCE ABOUT THE TICKER -- NOT A LIVENESS CLAIM** ({age_text};"
            f" {bound}): {detail}{suffix}"
        )
    return LOUD, (
        f"{prefix} -- **\u26a0 SUPERVISION NET NOT HEALTHY: {age_text}; {bound}. {detail}"
        f"**{suffix}"
    )


def _ttl_text(seconds: int) -> str:
    if seconds % 3600 == 0:
        return f"{seconds // 3600} h from observed time"
    if seconds % 60 == 0:
        return f"{seconds // 60} min from observed time"
    return f"{seconds} s from observed time"


def _render_evidence_route(
    route: dict[str, str], repo_root: pathlib.Path
) -> tuple[str, str]:
    value = route["path"]
    try:
        path = _repo_path(repo_root, value)
        if not path.is_file():
            return "UNAVAILABLE", "path does not exist"
        field = route.get("json_field")
        if not field:
            return "AVAILABLE", "commit-bound path"
        payload = load_json(path)
        field_value = payload.get(field)
        if not isinstance(field_value, list) or not all(
            isinstance(item, str) for item in field_value
        ):
            return "UNAVAILABLE", f"JSON field {field!r} is absent or not a string array"
        return "AVAILABLE", ", ".join(f"`{item}`" for item in field_value)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return "UNAVAILABLE", f"{type(exc).__name__}: {exc}"


def render(
    config: dict[str, Any],
    sessions: dict[str, Any],
    usage: dict[str, Any],
    usage_rc: int,
    jobs: list[dict[str, Any]],
    git_state: dict[str, Any],
    wake_state: dict[str, Any],
    observed_at: str,
    waker_ctx=None,
    last_known: LastKnown | None = None,
    route_snapshot: RouteSnapshot | None = None,
    repo_root: pathlib.Path = REPO,
) -> str:
    del sessions
    # No store passed means carry nothing and persist nothing (OI-144). Rendering
    # must never be the thing that decides to write a measurement record.
    store = last_known if last_known is not None else LastKnown()
    host = git_state.get("host") or store.host
    ttl = config.get(
        "measurement_ttl_seconds",
        {"compute": 300, "wake": 300, "provider_capacity": 3600},
    )
    route_state = route_snapshot or RouteSnapshot(
        "UNAVAILABLE", "route registry was not inspected"
    )
    lines = [
        "# Live orchestration measurements",
        "",
        "> GENERATED by `generate_live_state.py`; do not hand-edit. This file is a measurement"
        " and routing view, never evidence or authorization.",
        "",
        "## Snapshot health",
        "",
        "| Source | Observed | Health | TTL | Detail |",
        "|---|---|---|---|---|",
        f"| Git checkout | `{observed_at}` on `{host}` | **MEASURED** | commit-bound |"
        f" Git: `{git_state['head']}`; {git_state['dirty_count']} local worktree entries |",
        f"| Route registry | `{observed_at}` on `{host}` | **{route_state.health}** |"
        f" commit-bound | {route_state.detail} |",
        "",
        "## Current-work routes",
        "",
    ]
    if route_state.health == "HEALTHY":
        lines.extend(["| Item | Queue | Governing source |", "|---|---|---|"])
        for route in route_state.routes:
            lines.append(
                f"| `{route.item}` | `{route.queue}` |"
                f" [`{route.source_record}`](../OPEN_ITEMS.md) |"
            )
    else:
        lines.append(
            f"- **CURRENT ROUTE UNKNOWN:** registry health is `{route_state.health}`."
        )
    lines.extend(["", "## Compute measurements", ""])
    # If this generator ran somewhere without Slurm, EVERY row below is a non-observation.
    # Say so above the table, because a per-row caveat is read after the eye has already
    # taken the bolded state. BEN-323.
    lines.extend(
        [
            "| Job | Observed | Health / TTL | State counts | Errors | Declaration |",
            "|---|---|---|---|---|---|",
        ]
    )
    for job in jobs:
        receipt = job["receipt"]
        counts = ", ".join(f"{key}={value}" for key, value in job["snapshot"].get("counts", {}).items()) or "unknown"
        errors = ",".join(str(x) for x in job["snapshot"].get("error_tasks", [])) or "none"
        placement = "batch job" if job.get("single_job") else "batch array"
        resources = f"{receipt.get('cpus_per_task','?')} CPU, {receipt.get('memory_per_task','?')}, {receipt.get('time_limit','?')}; {receipt.get('qos','?')} {placement}"
        label = job["job_id"] if job.get("single_job") else f"{job['job_id']}_[{job['tasks']}]"
        overall = job["snapshot"].get("overall", "UNOBSERVED")
        # `observer_errors` was computed and RETURNED by build_snapshot and then dropped
        # here, so the one piece of evidence proving Slurm was never reached did not
        # reach the reader. It is now the Errors cell whenever the state is UNOBSERVED.
        # BEN-323.
        # OI-144: the row for a job this host cannot see used to carry ONLY the
        # local non-observation, so a laptop regeneration destroyed the cluster's
        # last real reading of the same job at the same commit. It is recorded on
        # the observing host and carried here instead.
        key = f"compute:{job['job_id']}"
        if overall == "UNOBSERVED":
            why = "; ".join(str(x) for x in job["snapshot"].get("observer_errors", []))
            errors = f"NOT OBSERVED: {why}" if why else "NOT OBSERVED: no Slurm reply"
            resources = f"declared (not observed): {resources}"
            history = carried(store.get(key), observed_at, _fmt_compute, f"job {job['job_id']}'s Slurm state")
            lines.append(
                f"| `{label}` | `{observed_at}` on `{host}` | **UNAVAILABLE** /"
                f" {_ttl_text(ttl['compute'])} | {counts}. {history} | {errors} |"
                f" {resources} |"
            )
        else:
            store.record(key, {"overall": overall, "counts": counts, "errors": errors})
            lines.append(
                f"| `{label}` | `{observed_at}` on `{host}` | **MEASURED** /"
                f" {_ttl_text(ttl['compute'])} | **{overall}**: {counts} | {errors} |"
                f" {resources} |"
            )
    lines.extend(["", "## Wake measurements", ""])
    lines.append(
        f"- Observed: `{observed_at}` on `{host}`; TTL"
        f" {_ttl_text(ttl['wake'])}."
    )
    if "waker_status" in wake_state:
        waker = wake_state["waker_status"]
        # `wakerctl.status()` projects each watch to six keys and `params` is NOT
        # among them, so the full records are re-read here: without them this
        # section can only ever show `state`, which is the defect being fixed.
        full: dict[str, dict[str, Any]] = {}
        if waker_ctx is not None:
            for record in safe_load_watches(waker_ctx):
                full[str(record.get("watch_id"))] = record
        rendered, severities, armed_ids = [], [], []
        for projected in waker.get("watches", []):
            watch = full.get(str(projected.get("watch_id"))) or projected
            severity, text = render_watch(watch, waker_ctx)
            severities.append(severity)
            rendered.append(text)
            if _wakerctl().is_armed(watch):
                armed_ids.append(str(watch.get("watch_id") or "<no-watch_id>"))
        # An ABSENT state dir must not render as "none". "none" is a claim about the
        # world ("there are no watches"); absence is a fact about this HOST. Rendering
        # the second as the first is the defect this whole section exists to prevent --
        # on 2026-08-19 exactly one watch was armed on the cluster while a Mac
        # regeneration would have printed "none" under a banner nobody had to read.
        #
        # READABILITY, not `rendered`, is what licenses a RECORD (OI-144). A
        # status-only projection renders watch text with no state dir behind it and
        # every verdict NO EVIDENCE; recording that would write a non-observation
        # into the store as though some host had measured it.
        store_readable = waker_ctx is not None and _watch_store_readable(waker_ctx)
        if rendered:
            watches = ", ".join(rendered)
            if store_readable:
                worst = LOUD if LOUD in severities else (NO_EVIDENCE if NO_EVIDENCE in severities else QUIET)
                store.record("waker:watches", {"count": len(rendered), "armed": armed_ids, "worst": worst})
        elif not store_readable:
            watches = _wakerctl().no_evidence(
                "the waker state dir is not present or not readable on this host, so this "
                "host knows of NO watches -- that is NOT the same as there being none."
            ) + " " + carried(store.get("waker:watches"), observed_at, _fmt_watches, "the waker watch store")
            severities.append(NO_EVIDENCE)
        else:
            watches = "none (state dir readable; 0 watch records present)"
            store.record("waker:watches", {"count": 0, "armed": [], "worst": QUIET})
        # The events bullet had the SAME defect the watches bullet above was fixed
        # for, one line down and unnoticed: `... or "none"` turned an unreadable
        # events dir into the claim that no events exist.
        event_records = waker.get("events", []) or []
        events_readable = waker_ctx is not None and _events_dir_readable(waker_ctx)
        if event_records:
            events = ", ".join(f"`{e['event_id']}`:{e['state']}" for e in event_records)
            if events_readable:
                store.record("waker:events", {"count": len(event_records), "summary": events})
        elif not events_readable:
            events = _wakerctl().no_evidence(
                "the waker events dir is not present or not readable on this host, so this host "
                "knows of NO events -- that is NOT the same as there being none."
            ) + " " + carried(store.get("waker:events"), observed_at, _fmt_events, "the waker event store")
            severities.append(NO_EVIDENCE)
        else:
            events = "none (events dir readable; 0 event records present)"
            store.record("waker:events", {"count": 0, "summary": "none"})
        last_tick = waker.get("last_tick") or {}
        tick_severity, tick_text = tick_line(last_tick, waker_ctx)
        tick_entry = store.get("waker:last-tick")
        if tick_severity == NO_EVIDENCE:
            tick_text += " " + carried(tick_entry, observed_at, _fmt_tick, "a waker tick receipt")
            recorded = tick_entry.get("value") if isinstance(tick_entry, dict) else None
            stamp_age = age_between((recorded or {}).get("at_utc"), observed_at) if isinstance(recorded, dict) else ""
            if stamp_age:
                tick_text += (
                    f" Arithmetic on that carried stamp alone puts it {stamp_age} behind this"
                    " snapshot's clock -- arithmetic ONLY, and deliberately not a verdict: this"
                    " host read neither the scrontab bound nor whether the scron tick job is"
                    " runnable, and both are required before the ticker can be called healthy or"
                    " dead."
                )
        else:
            store.record(
                "waker:last-tick",
                {
                    "at_utc": str(last_tick.get("at_utc", "never")),
                    "node": str(last_tick.get("node", "unknown")),
                    "verdict": tick_severity,
                },
            )
        if LOUD in severities or tick_severity == LOUD:
            lines.extend([
                "- Wake health: **UNHEALTHY** at the observed time; at least one measured watch"
                " or ticker check was unhealthy.",
                "",
            ])
        elif NO_EVIDENCE in severities or tick_severity == NO_EVIDENCE:
            lines.extend([
                "- Wake health: **UNKNOWN** at the observed time; at least one required source"
                " was unavailable on this host.",
                "",
            ])
        lines.extend(
            [
                f"- wakerctl watches: {watches}",
                f"- wakerctl events: {events}",
                tick_text,
            ]
        )
    else:
        lines.extend(
            [
                f"- tmux `{config['wake']['tmux_session']}`: **{wake_state['tmux']}**",
                f"- Event/invoked/done markers: {wake_state['event']} / {wake_state['invoked']} / {wake_state['completed']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Provider-capacity measurements",
            "",
            f"- Observed: `{observed_at}` on `{host}`; TTL"
            f" {_ttl_text(ttl['provider_capacity'])}.",
        ]
    )
    # OI-144, the mirror image of the Compute table above. `usagectl.py` turns a
    # profile it could not READ into `status: "error"` with a policy violation, and
    # a policy violation makes `gate_ok` false -- so on a Perlmutter login node,
    # where no Codex/Claude profile home exists, an UNREADABLE profile rendered as
    # a BLOCKED gate and every percentage as `unknown`. "This host cannot see the
    # accounts" and "the accounts are over policy" are opposite findings and had
    # one rendering. A gate cannot pass or fail on evidence nobody collected.
    profiles = usage.get("profiles") if isinstance(usage.get("profiles"), dict) else {}
    unreadable = sorted(
        name for name, record in profiles.items()
        if isinstance(record, dict) and record.get("status") == "error"
    )
    helper_ran = usage_rc in (0, 3) and bool(profiles)
    if helper_ran and not unreadable:
        verdict = "PASS" if usage.get("gate_ok") else "BLOCKED/UNKNOWN"
        lines.append(f"- Usage gate: **{verdict}** (helper rc={usage_rc})")
        store.record("usage:gate", {"verdict": verdict, "rc": usage_rc})
    else:
        why = (
            f"{len(unreadable)} of {len(profiles)} profiles could not be READ on this host"
            f" ({', '.join(unreadable)}), so `gate_ok` is false for a reason about the host"
            if unreadable
            else f"the usage helper produced no profile snapshot here (rc={usage_rc})"
        )
        lines.append(
            "- Usage gate: **NOT ASSESSABLE ON THIS HOST — NEITHER A PASS NOR A BLOCK** (helper"
            f" rc={usage_rc}): {why}. "
            + carried(store.get("usage:gate"), observed_at, _fmt_gate, "the usage gate")
        )
    for label, profile_name in (("Codex personal", "codex-personal"), ("Codex school", "codex-school")):
        key = f"usage:{profile_name}"
        if profile_name in unreadable:
            lines.append(
                f"- {label}: "
                + carried(store.get(key), observed_at, _fmt_text, f"`{profile_name}` capacity")
            )
            continue
        capacity = codex_capacity(usage, profile_name)
        lines.append(f"- {label}: {capacity}")
        if (profiles.get(profile_name) or {}).get("status") == "ok":
            store.record(key, capacity)
    school = usage.get("accounts", {}).get("claude-school", {})
    agy = usage.get("profiles", {}).get("agy", {})
    claude_unreadable = [
        name for name in unreadable if (profiles.get(name) or {}).get("provider") == "claude"
    ]
    if claude_unreadable:
        lines.append(
            "- Claude school shared account: "
            + carried(
                store.get("usage:claude-school"), observed_at, _fmt_text,
                "the shared Claude account's status",
            )
        )
    else:
        school_status = school.get("status", "unknown")
        lines.append(f"- Claude school shared account: {school_status}")
        if school_status not in (None, "", "unknown"):
            store.record("usage:claude-school", school_status)
    # agy is NOT carried: `unknown` here is a measured property of the installed
    # CLI, which has no usage API on any host. Carrying it would replace a real
    # finding with an older copy of the same finding.
    lines.append(
        f"- agy/Gemini: {agy.get('status','unknown')} (no percentage API in the installed CLI, so"
        " `unknown` is a MEASURED absence here and not a host limitation; heartbeat/cap evidence"
        " only)"
    )
    warnings = usage.get("warnings", [])
    if warnings or unreadable:
        lines.append(
            f"- Capacity warnings: {len(warnings)} measured;"
            f" {len(unreadable)} profile source(s) unavailable on this host."
        )
    lines.extend(
        [
            "",
            "## Stable evidence routes",
            "",
            "| Route | Health / TTL | Source | Structured detail |",
            "|---|---|---|---|",
        ]
    )
    for route in config.get("evidence_routes", []):
        health, detail = _render_evidence_route(route, repo_root)
        lines.append(
            f"| {route['label']} | **{health}** / commit-bound |"
            f" [{route['path']}]({rel_link(route['path'])}) | {detail} |"
        )
    lines.append("")
    if len(lines) > MAX_LINES:
        raise RuntimeError(f"dashboard exceeds {MAX_LINES} lines: {len(lines)}")
    return "\n".join(lines)


def atomic_write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check_freshness(repo_root) -> int:
    """Exit 0 if LIVE-STATE.md is fresh, 1 if stale, 2 if it cannot be read.

    FRESH means: HEAD == the recorded `Git:` sha, OR the recorded sha is HEAD's parent. The second
    disjunct is not slack -- it is the normal state, because the commit that carries the snapshot moves
    HEAD after the generator read it. BEN-199: the orchestrator prescribed `Git:` vs `HEAD` as "the only
    freshness test" and it has NO passing state, so it fired on a maximally fresh file and could not
    separate born-stale-by-one from dangerously-stale-by-five, which was the condition it existed to
    detect. Found by the personal-account verifier session re-deriving the rule against the file.
    """
    import subprocess
    live = pathlib.Path(repo_root) / "docs/orchestration/LIVE-STATE.md"
    if not live.exists():
        print("CANNOT CHECK :: LIVE-STATE.md absent")
        return 2
    m = re.search(r"Git: `([0-9a-f]+)`", live.read_text(encoding="utf-8"))
    if not m:
        print("CANNOT CHECK :: no `- Git:` line in LIVE-STATE.md")
        return 2
    recorded = m.group(1)
    def rev(spec):
        r = subprocess.run(["git", "-C", str(repo_root), "rev-parse", "--short", spec],
                           capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    def _scope_of_a_green():
        print("  SCOPE OF THIS GREEN: only the recorded Git relationship is checked.")
        print("        Probe TTLs and route-registry health remain separate fields in the file.")

    head, parent = rev("HEAD"), rev("HEAD^")
    if recorded == head:
        print(f"FRESH :: Git: {recorded} == HEAD")
        _scope_of_a_green()
        return 0
    if parent and recorded == parent:
        print(f"FRESH :: Git: {recorded} is HEAD's parent ({head}) -- the normal born-stale-by-one state")
        _scope_of_a_green()
        return 0
    print(f"STALE :: Git: {recorded}, HEAD {head}, HEAD^ {parent}.")
    print("  NOTE: regeneration refreshes only measurable sources; unavailable probes stay explicit.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--check-freshness", action="store_true",
                        help="Exit 0 fresh / 1 stale / 2 cannot-check; writes nothing. BEN-199: the "
                             "rule is HEAD == Git: OR Git: is HEAD's parent, because the commit "
                             "carrying this file moves HEAD after the generator read it.")
    args = parser.parse_args()

    if args.check_freshness:
        return check_freshness(HERE.parent.parent)

    config = load_json(args.config)
    validate_config(config)
    routes = route_registry_snapshot(config, REPO)
    usage, usage_rc = usage_snapshot()
    jobs = []
    for job in config["jobs"]:
        receipt = load_json(REPO / job["receipt"])
        if receipt.get("job_id") != job["job_id"]:
            raise RuntimeError(f"job receipt mismatch for {job['job_id']}")
        jobs.append(
            {
                **job,
                "receipt": receipt,
                "snapshot": build_snapshot(job["job_id"], expand_spec(job["tasks"])),
            }
        )
    wake = config["wake"]
    waker_ctx = None
    if wake.get("waker"):
        import wakerctl

        waker_ctx = wakerctl.Ctx()
        wake_state = {"waker_status": wakerctl.status(waker_ctx)}
    else:
        tmux_rc = subprocess.run(["tmux", "has-session", "-t", wake["tmux_session"]], capture_output=True).returncode
        wake_state = {
            "tmux": "ACTIVE" if tmux_rc == 0 else "INACTIVE",
            "event": "present" if (REPO / wake["event"]).exists() else "absent",
            "invoked": "present" if (REPO / wake["invoked"]).exists() else "absent",
            "completed": "present" if (REPO / wake["completed"]).exists() else "absent",
        }
    git_state = {
        "head": run_text(["git", "rev-parse", "--short", "HEAD"]).strip(),
        # A count of THIS checkout's uncommitted entries, and labelled as such in
        # the render. It is not campaign state and never was (OI-144, BEN-183).
        "dirty_count": len(run_text(["git", "status", "--short"]).splitlines()),
        "host": hostname(),
    }
    observed_at = utc_now()
    last_known = LastKnown(
        LAST_KNOWN_PATH,
        host=git_state["host"],
        observed_at=observed_at,
        head=git_state["head"],
    )
    output = render(
        config,
        {},
        usage,
        usage_rc,
        jobs,
        git_state,
        wake_state,
        observed_at,
        waker_ctx=waker_ctx,
        last_known=last_known,
        route_snapshot=routes,
    )
    if args.stdout:
        # --stdout is the read-only rehearsal path, so it must not move the record
        # of what any host has measured either.
        print(output)
    else:
        atomic_write(args.output, output)
        print(f"wrote {args.output} ({len(output.splitlines())} lines)")
        if last_known.save():
            print(
                f"updated {LAST_KNOWN_PATH}: this host's measurements are now the last known"
                " values other hosts will carry. COMMIT IT WITH THE DASHBOARD -- an uncommitted"
                " store is a measurement no other host can reach."
            )
        else:
            print(
                f"{LAST_KNOWN_PATH} unchanged: no probe on this host produced a measurement"
                " to record, so nothing here can be carried forward for another host."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
