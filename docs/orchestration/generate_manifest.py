#!/usr/bin/env python3
"""Generate the in-place classification manifest for docs/orchestration.

The required output schema intentionally has no tracking-state column.  Git
tracking/ignore state is still derived here: tracked and intended-to-be-tracked
files participate in inbound-reference analysis, while ignored artifacts are
inventoried but do not create inbound references.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import re
import subprocess
import sys
from collections import Counter, deque
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ORCHESTRATION = REPO / "docs" / "orchestration"
TARGET = ORCHESTRATION / "MANIFEST.tsv"
OVERRIDES = ORCHESTRATION / "MANIFEST-overrides.tsv"

COLUMNS = (
    "path",
    "class",
    "kind",
    "campaign",
    "event_date",
    "event_status",
    "canonical_successor",
    "read_policy",
    "consumer",
    "immutable",
    "inbound_count",
    "lines",
    "bytes",
)
OVERRIDE_COLUMNS = ("path", "class", "event_status", "canonical_successor")
CLASSES = {"LIVE", "ARCHIVAL", "MACHINE", "DEAD"}
EVENT_STATUSES = {"open", "terminal", "superseded", "generated"}
READ_POLICIES = {"always", "route-only", "exact-path-only", "never"}
MACHINE_SUFFIXES = {".py", ".sh", ".json", ".tsv", ".lock", ".pyc"}
SCRIPT_SUFFIXES = {".py", ".sh"}
DATE_RE = re.compile(r"(?<!\d)(20\d{6})(?!\d)")
CAMPAIGN_RE = re.compile(r"\b([a-z0-9][a-z0-9-]*-campaign)\b")


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def inventory() -> tuple[list[Path], dict[str, str]]:
    tracked = set(git_lines("ls-files"))
    ignored = set(
        git_lines(
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "--",
            "docs/orchestration",
        )
    )

    paths: list[Path] = []
    for directory, dirnames, filenames in os.walk(ORCHESTRATION):
        dirnames.sort()
        for filename in sorted(filenames):
            candidate = Path(directory) / filename
            if candidate.is_file():
                paths.append(candidate)

    # The first generation must already describe its own eventual output.
    if TARGET not in paths:
        paths.append(TARGET)
    paths.sort(key=repo_path)

    states: dict[str, str] = {}
    for path in paths:
        rel = repo_path(path)
        if rel in tracked:
            states[rel] = "tracked"
        elif rel in ignored:
            states[rel] = "ignored"
        else:
            states[rel] = "intended"
    return paths, states


def load_overrides() -> dict[str, dict[str, str]]:
    try:
        handle = OVERRIDES.open(newline="", encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing overrides file: {repo_path(OVERRIDES)}") from exc

    with handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != OVERRIDE_COLUMNS:
            raise ValueError(
                f"override header must be exactly: {' '.join(OVERRIDE_COLUMNS)}"
            )
        result: dict[str, dict[str, str]] = {}
        for line_number, row in enumerate(reader, start=2):
            path = row["path"]
            if not path or path in result:
                raise ValueError(f"invalid or duplicate override path at line {line_number}")
            if row["class"] not in CLASSES:
                raise ValueError(f"invalid class at override line {line_number}")
            if row["event_status"] not in EVENT_STATUSES:
                raise ValueError(f"invalid event_status at override line {line_number}")
            result[path] = row
        return result


def is_runs_or_state(rel: str) -> bool:
    return rel.startswith("docs/orchestration/runs/") or rel.startswith(
        "docs/orchestration/state/"
    )


def is_cache(path: Path) -> bool:
    return any(part in {"__pycache__", ".pytest_cache"} for part in path.parts)


def default_class(path: Path, rel: str) -> str:
    if is_runs_or_state(rel) or is_cache(path) or path.suffix.lower() in MACHINE_SUFFIXES:
        return "MACHINE"
    return "ARCHIVAL"


def derive_kind(path: Path, rel: str) -> str:
    name = path.name
    upper = name.upper()
    suffix = path.suffix.lower()
    if is_cache(path):
        return "cache"
    if rel.startswith("docs/orchestration/runs/"):
        return "run-artifact"
    if rel.startswith("docs/orchestration/state/"):
        return "state-artifact"
    if name == ".DS_Store":
        return "filesystem-metadata"
    if suffix == ".pyc":
        return "bytecode-cache"
    if suffix == ".py":
        return "test-script" if name.startswith("test_") else "generator-script" if name.startswith("generate_") else "script"
    if suffix == ".sh":
        return "shell-tool"
    if suffix == ".json":
        return "machine-data"
    if suffix == ".tsv":
        return "tabular-data"
    if suffix == ".lock":
        return "lock"
    if suffix == ".md":
        if ".template." in name:
            return "template"
        prefixes = (
            ("FINDING-", "finding"),
            ("FOLLOWUP-", "followup-prompt"),
            ("START-", "start-prompt"),
            ("CONTINUITY-", "continuity-prompt"),
            ("HEARTBEAT-", "heartbeat-prompt"),
            ("PREDECLAR", "predeclaration"),
            ("PREDECLARE-", "predeclaration"),
            ("AUDIT-", "audit"),
            ("REVIEW-", "review"),
            ("VERDICT", "verdict"),
            ("PROCEDURE-", "procedure"),
            ("PLAN-", "plan"),
            ("RUNBOOK-", "runbook"),
            ("INDEX-", "index"),
            ("LIVE-", "live-status"),
        )
        for prefix, kind in prefixes:
            if upper.startswith(prefix):
                return kind
        if name in {"CLAIMS.md", "FINDINGS.md"}:
            return "ledger"
        if name == "CATALOG.md":
            return "router"
        return "document"
    return "artifact"


def derive_campaign(path: Path, rel: str, data: bytes) -> str:
    parts = Path(rel).parts
    if len(parts) >= 5 and parts[2] == "runs":
        return parts[3]
    if len(parts) >= 5 and parts[2] == "state":
        return parts[3]
    text = data.decode("utf-8", errors="ignore")
    match = CAMPAIGN_RE.search(text)
    return match.group(1) if match else ""


def derive_read_policy(classification: str, name: str) -> str:
    if classification == "MACHINE":
        return "exact-path-only"
    if classification == "DEAD":
        return "never"
    if classification == "ARCHIVAL":
        return "exact-path-only"
    if name in {"CATALOG.md", "LIVE-STATE.md"}:
        return "always"
    return "route-only"


def derive_immutable(classification: str, rel: str, tracking_state: str) -> str:
    if classification in {"ARCHIVAL", "DEAD"} or is_runs_or_state(rel):
        return "yes"
    if classification == "MACHINE" and tracking_state == "ignored":
        return "yes"
    return "no"


def build_match_index(
    basenames: set[bytes], source_paths: list[Path]
) -> dict[bytes, set[str]]:
    """Return basename -> source files containing it using Aho-Corasick."""
    transitions: list[dict[int, int]] = [{}]
    failures = [0]
    outputs: list[set[bytes]] = [set()]
    for pattern in sorted(basenames):
        state = 0
        for byte in pattern:
            next_state = transitions[state].get(byte)
            if next_state is None:
                next_state = len(transitions)
                transitions[state][byte] = next_state
                transitions.append({})
                failures.append(0)
                outputs.append(set())
            state = next_state
        outputs[state].add(pattern)

    queue: deque[int] = deque()
    for state in transitions[0].values():
        queue.append(state)
    while queue:
        state = queue.popleft()
        for byte, next_state in transitions[state].items():
            queue.append(next_state)
            fallback = failures[state]
            while fallback and byte not in transitions[fallback]:
                fallback = failures[fallback]
            failures[next_state] = transitions[fallback].get(byte, 0)
            outputs[next_state].update(outputs[failures[next_state]])

    matches: dict[bytes, set[str]] = {pattern: set() for pattern in basenames}
    for source in source_paths:
        try:
            data = source.read_bytes()
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            continue
        found: set[bytes] = set()
        state = 0
        for byte in data:
            while state and byte not in transitions[state]:
                state = failures[state]
            state = transitions[state].get(byte, 0)
            found.update(outputs[state])
        source_rel = repo_path(source)
        for pattern in found:
            matches[pattern].add(source_rel)
    return matches


def reference_sources(paths: list[Path], states: dict[str, str]) -> list[Path]:
    # All currently tracked files are authoritative reference sources.  Include
    # nonignored files in this new deliverable set so generation is stable
    # before and after they are added to Git.
    tracked = [REPO / path for path in git_lines("ls-files")]
    intended = [path for path in paths if states[repo_path(path)] == "intended"]
    unique = {path.resolve(): path for path in tracked + intended if path != TARGET}
    return sorted(unique.values(), key=lambda path: repo_path(path))


def sanitize(value: object) -> str:
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def render(rows: list[dict[str, object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: sanitize(row[column]) for column in COLUMNS})
    return stream.getvalue().encode("utf-8")


def generate() -> tuple[bytes, Counter[str], int, int, Counter[str], list[str]]:
    paths, states = inventory()
    overrides = load_overrides()
    basename_bytes = {path.name.encode("utf-8") for path in paths}
    matches = build_match_index(basename_bytes, reference_sources(paths, states))

    rows: list[dict[str, object]] = []
    applied_overrides: set[str] = set()
    for path in paths:
        rel = repo_path(path)
        if path == TARGET:
            data = b""
        else:
            data = path.read_bytes()

        classification = default_class(path, rel)
        event_status = "generated" if classification == "MACHINE" else "terminal"
        successor = ""
        override = overrides.get(rel)
        if override is not None:
            classification = override["class"]
            event_status = override["event_status"]
            successor = override["canonical_successor"]
            applied_overrides.add(rel)

        if is_runs_or_state(rel):
            classification = "MACHINE"
            event_status = "generated"
            successor = ""

        if classification not in CLASSES or event_status not in EVENT_STATUSES:
            raise ValueError(f"invalid generated classification for {rel}")
        read_policy = derive_read_policy(classification, path.name)
        if read_policy not in READ_POLICIES:
            raise ValueError(f"invalid read policy for {rel}")

        source_hits = matches[path.name.encode("utf-8")]
        inbound = len(source_hits - {rel})
        consumers = sorted(
            source
            for source in source_hits - {rel}
            if Path(source).suffix.lower() in SCRIPT_SUFFIXES
        )
        date_match = DATE_RE.search(path.name)
        rows.append(
            {
                "path": rel,
                "class": classification,
                "kind": derive_kind(path, rel),
                "campaign": derive_campaign(path, rel, data),
                "event_date": date_match.group(1) if date_match else "",
                "event_status": event_status,
                "canonical_successor": successor,
                "read_policy": read_policy,
                "consumer": ";".join(consumers),
                "immutable": derive_immutable(classification, rel, states[rel]),
                "inbound_count": inbound,
                "lines": data.count(b"\n"),
                "bytes": len(data),
            }
        )

    rows.sort(key=lambda row: str(row["path"]))
    target_row = next(row for row in rows if row["path"] == repo_path(TARGET))
    target_row["lines"] = len(rows) + 1
    target_row["bytes"] = 0
    for _ in range(20):
        output = render(rows)
        output_size = len(output)
        if target_row["bytes"] == output_size:
            break
        target_row["bytes"] = output_size
    else:
        raise ValueError("MANIFEST.tsv byte-count fixed point did not converge")
    output = render(rows)
    if target_row["bytes"] != len(output):
        raise ValueError("MANIFEST.tsv self-size is inconsistent")

    class_counts = Counter(str(row["class"]) for row in rows)
    tracking_counts = Counter(states.values())
    unused = sorted(set(overrides) - applied_overrides)
    return (
        output,
        class_counts,
        len(applied_overrides),
        len(rows) - len(applied_overrides),
        tracking_counts,
        unused,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit nonzero when MANIFEST.tsv differs from generated output",
    )
    args = parser.parse_args()

    try:
        output, counts, overridden, defaults, tracking, unused = generate()
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"generate_manifest.py: {exc}", file=sys.stderr)
        return 2

    summary = (
        f"rows={sum(counts.values())} "
        + " ".join(f"{name}={counts.get(name, 0)}" for name in sorted(CLASSES))
        + f" overrides={overridden} defaults={defaults}"
        + " tracking="
        + ",".join(f"{name}:{tracking[name]}" for name in sorted(tracking))
    )
    if unused:
        summary += f" unused_overrides={len(unused)}"

    if args.check:
        current = TARGET.read_bytes() if TARGET.exists() else None
        if current != output:
            print(f"OUT OF DATE: {repo_path(TARGET)}; {summary}", file=sys.stderr)
            return 1
        print(f"OK: {repo_path(TARGET)}; {summary}")
        return 0

    TARGET.write_bytes(output)
    print(f"wrote {repo_path(TARGET)}; {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
