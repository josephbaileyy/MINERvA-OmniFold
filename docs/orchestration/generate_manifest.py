#!/usr/bin/env python3
"""Generate the in-place classification manifest for docs/orchestration.

Inventory is Git-defined: tracked files plus nonignored untracked files intended
for the current change. Ignored caches and build products are excluded. Tracking
state is emitted, so a proposed file cannot masquerade as committed inventory.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import subprocess
import sys
import tempfile
from collections import Counter, deque
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ORCHESTRATION = REPO / "docs" / "orchestration"
TARGET = ORCHESTRATION / "MANIFEST.tsv"
OVERRIDES = ORCHESTRATION / "MANIFEST-overrides.tsv"

COLUMNS = (
    "path",
    "tracking",
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


def inventory(committed_only: bool = False) -> tuple[list[Path], dict[str, str]]:
    """Git-defined inventory. `committed_only` drops the `intended` half entirely.

    OI-70, second half, measured 2026-08-20. Emitting `tracking` stops an uncommitted file
    MASQUERADING as committed, and that was the filed defect. It does not make the default
    inventory safe to publish from a SHARED checkout: this tree carried 49 nonignored untracked
    paths belonging to other lanes and other sessions, and the default run inventories all of
    them AND lets them drive `inbound_count` on 73 already-committed rows through
    `reference_sources()`. Row-count acceptance passes on that run -- 0 dropped, 50 added -- and
    passing it does not make one lane entitled to declare another's work-in-progress as
    repository inventory.

    So the row's OTHER prescribed remedy ("or exclude `intended` paths from the table") is
    available as an explicit mode rather than as a new default: the default is right for a lane
    generating from its own clean tree immediately before committing, which is what the
    docstring at the top of this file describes. `--committed-only` is right for a shared
    checkout, because it makes the emitted PATH SET a statement about `HEAD` alone.

    IT IS NOT A CLEAN-TREE SUBSTITUTE, and saying so here so nobody reads it as one: `lines`,
    `bytes` and `inbound_count` are still measured from WORKING-TREE bytes, so an uncommitted
    edit to a file that is already tracked still reaches the table. Generate from a tree whose
    inventory scope is clean; `main()` prints the dirty tracked paths for exactly this reason.
    """
    tracked = set(git_lines("ls-files", "--", "docs/orchestration"))
    intended = set() if committed_only else set(
        git_lines("ls-files", "--others", "--exclude-standard", "--", "docs/orchestration"))
    target_rel = repo_path(TARGET)
    tracked.add(target_rel)
    relpaths = sorted(tracked | intended)
    paths = [REPO / rel for rel in relpaths if (REPO / rel).is_file() or rel == target_rel]
    states = {rel: ("tracked" if rel in tracked else "intended") for rel in relpaths}
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


def derive_immutable(classification: str, rel: str, event_status: str) -> str:
    """Immutability follows the LIFECYCLE, not the directory.

    OI-73. `is_runs_or_state(rel)` alone answers "does this sit under `runs/` or `state/`?",
    which is a question about the DIRECTORY, and it returned `yes` for
    `state/live-state.json` -- the hand-authored INPUT that `generate_live_state.py` only ever
    READS. That is the deadlock the row names: the one file able to clear a dead blocker read
    `immutable yes` in the artifact `CLAUDE.md` calls the authority, so every lane correctly
    refused to touch it while the blocker could not be cleared by regenerating either. A
    GENERATED run/state record is immutable evidence; an AUTHORED input under those trees is
    not, and `event_status` is where that difference is already recorded.

    The former `tracking_state == "ignored"` branch is removed as PROVABLY DEAD, not as a
    behaviour change: `inventory()` emits only `tracked` and `intended`, and `--self-test`
    asserts exactly that (`set(states.values()) <= {"tracked", "intended"}`).
    """
    if classification in {"ARCHIVAL", "DEAD"}:
        return "yes"
    if is_runs_or_state(rel):
        return "yes" if event_status == "generated" else "no"
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


def classify_inventory_status(
        rows: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    """Split porcelain rows into observable hazards and intended untracked paths.

    The porcelain ``XY`` columns are load-bearing here.  A non-blank ``Y`` means the working
    tree differs from the index, so the bytes the generator reads are not the bytes staged for
    the prospective commit.  A non-blank ``X`` with a blank ``Y`` is the normal, fully-staged
    F-14 procedure and must not warn.  ``??`` paths are a separate default-mode disclosure:
    they are intentionally inventoried by default, but may belong to another lane in a shared
    checkout.
    """
    unstaged: set[tuple[str, str]] = set()
    intended: set[str] = set()
    for line in rows:
        if len(line) < 4:
            continue
        xy = line[:2]
        path = line[3:].split(" -> ")[-1]
        if xy == "??":
            intended.add(path)
        elif xy[1] != " ":
            unstaged.add((xy, path))
    return sorted(unstaged, key=lambda item: item[1]), sorted(intended)


def inventory_status() -> tuple[list[tuple[str, str]], list[str]]:
    """Return unstaged tracked changes and nonignored untracked paths in inventory scope."""
    rows = git_lines("status", "--porcelain", "--", "docs/orchestration")
    return classify_inventory_status(rows)


def status_warnings(
        unstaged: list[tuple[str, str]], intended: list[str],
        committed_only: bool) -> list[str]:
    """Render only warnings whose condition is observable in the current index/worktree."""
    warnings: list[str] = []
    if intended and not committed_only:
        warnings.append(
            f"WARNING: {len(intended)} nonignored untracked path(s) are INCLUDED as "
            "tracking=intended in default mode; they may be another lane's work and may "
            "make --check report OUT OF DATE without a committed-manifest defect: "
            f"{', '.join(intended[:6])}{' ...' if len(intended) > 6 else ''}"
        )
    if unstaged:
        details = ", ".join(
            f"{path} (XY={xy!r})" for xy, path in unstaged[:6]
        )
        warnings.append(
            f"WARNING: {len(unstaged)} tracked path(s) in the inventory scope have "
            "UNSTAGED working-tree changes, so their lines/bytes/inbound_count do not "
            "describe the staged index: "
            f"{details}{' ...' if len(unstaged) > 6 else ''}"
        )
    return warnings


def generate(committed_only: bool = False) -> tuple[
        bytes, Counter[str], int, int, Counter[str], list[str]]:
    paths, states = inventory(committed_only)
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
            # A three-column override row leaves `canonical_successor` MISSING, and
            # `csv.DictReader` fills a short row with None -- which `sanitize()` then
            # stringified, so three committed rows named a successor document called
            # `None`. Measured 2026-08-20 on the three `CONVENTION-*` rows.
            successor = override["canonical_successor"] or ""
            applied_overrides.add(rel)

        # OI-73 / BEN-321. This coercion used to run AFTER the override and reset it
        # UNCONDITIONALLY, so every `runs/` or `state/` override was applied and then
        # silently discarded -- while still being counted in `applied_overrides`, which kept
        # the dead entry out of the `unused_overrides` warning. Two consequences, and the
        # second is why this is a code change rather than a data change: the remedy `OI-73`
        # prescribes for the `live-state.json` misclassification was STRUCTURALLY INCAPABLE
        # of working, and a reader of the summary line could not tell a live override from an
        # inert one. The coercion is right for a GENERATED run/state artifact and wrong for an
        # AUTHORED control-plane input that happens to live under `state/`, so it now applies
        # only where the hand-maintained overrides file has declared nothing.
        if is_runs_or_state(rel) and override is None:
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
                "tracking": states[rel],
                "class": classification,
                "kind": derive_kind(path, rel),
                "campaign": derive_campaign(path, rel, data),
                "event_date": date_match.group(1) if date_match else "",
                "event_status": event_status,
                "canonical_successor": successor,
                "read_policy": read_policy,
                "consumer": ";".join(consumers),
                "immutable": derive_immutable(classification, rel, event_status),
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


def self_test() -> int:
    ignored_dir = ORCHESTRATION / "__pycache__"
    made_ignored_dir = not ignored_dir.exists()
    ignored_dir.mkdir(exist_ok=True)
    intended_path: Path | None = None
    ignored_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=ORCHESTRATION, prefix="manifest-selftest-",
                                         suffix=".md", delete=False) as handle:
            intended_path = Path(handle.name)
        with tempfile.NamedTemporaryFile(dir=ignored_dir, prefix="manifest-selftest-",
                                         suffix=".pyc", delete=False) as handle:
            ignored_path = Path(handle.name)
        paths, states = inventory()
        rels = {repo_path(path) for path in paths}
        # OI-73. The override-survival guard is asserted in the SOURCE as well as in
        # behaviour, because its failure mode is silent: delete `and override is None` and
        # every `runs/`+`state/` override goes inert again while this file still reports a
        # clean pass and `unused_overrides` still reads 0 (BEN-321's exact shape).
        source = Path(__file__).read_text(encoding="utf-8")
        authored = "docs/orchestration/state/authored-input-selftest.json"
        generated = "docs/orchestration/state/generated-record-selftest.json"
        fires_unstaged, _ = classify_inventory_status(
            [" M docs/orchestration/CATALOG.md"]
        )
        silent_staged, _ = classify_inventory_status(
            ["M  docs/orchestration/CATALOG.md"]
        )
        fires_staged_then_edited, _ = classify_inventory_status(
            ["MM docs/orchestration/CATALOG.md"]
        )
        direct_f14_shape, _ = classify_inventory_status([
            "M  docs/orchestration/CATALOG.md",
            " M docs/orchestration/MANIFEST.tsv",
        ])
        _, intended_paths = classify_inventory_status(
            ["?? docs/orchestration/peer-work-in-progress.md"]
        )
        fires_unstaged_messages = status_warnings(fires_unstaged, [], False)
        silent_staged_messages = status_warnings(silent_staged, [], False)
        fires_mm_messages = status_warnings(fires_staged_then_edited, [], False)
        direct_f14_messages = status_warnings(direct_f14_shape, [], False)
        intended_default_messages = status_warnings([], intended_paths, False)
        intended_committed_only_messages = status_warnings([], intended_paths, True)
        checks = (
            repo_path(intended_path) in rels,
            states.get(repo_path(intended_path)) == "intended",
            repo_path(ignored_path) not in rels,
            set(states.values()) <= {"tracked", "intended"},
            "tracking" in COLUMNS,
            "if is_runs_or_state(rel) and override is None:" in source,
            # an AUTHORED input under state/ is editable by its owner...
            derive_immutable("LIVE", authored, "open") == "no",
            # ...and a GENERATED record under state/ is still an immutable receipt.
            derive_immutable("MACHINE", generated, "generated") == "yes",
            derive_immutable("ARCHIVAL", "docs/orchestration/x.md", "terminal") == "yes",
            fires_unstaged == [(" M", "docs/orchestration/CATALOG.md")],
            silent_staged == [],
            fires_staged_then_edited == [("MM", "docs/orchestration/CATALOG.md")],
            direct_f14_shape == [(" M", "docs/orchestration/MANIFEST.tsv")],
            intended_paths == ["docs/orchestration/peer-work-in-progress.md"],
            len(fires_unstaged_messages) == 1 and "XY=' M'" in fires_unstaged_messages[0],
            silent_staged_messages == [],
            len(fires_mm_messages) == 1 and "XY='MM'" in fires_mm_messages[0],
            len(direct_f14_messages) == 1
            and "docs/orchestration/MANIFEST.tsv" in direct_f14_messages[0],
            len(intended_default_messages) == 1
            and "tracking=intended" in intended_default_messages[0],
            intended_committed_only_messages == [],
        )
        if not all(checks):
            print("manifest self-test: FAIL", file=sys.stderr)
            print(f"checks={checks}", file=sys.stderr)
            return 1
    finally:
        if intended_path is not None:
            intended_path.unlink(missing_ok=True)
        if ignored_path is not None:
            ignored_path.unlink(missing_ok=True)
        if made_ignored_dir:
            ignored_dir.rmdir()
    print("manifest self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit nonzero when MANIFEST.tsv differs from generated output",
    )
    parser.add_argument(
        "--committed-only",
        action="store_true",
        help="OI-70: inventory only tracked paths, so a shared checkout's foreign untracked "
             "files are neither published as inventory nor allowed to move inbound_count",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    try:
        output, counts, overridden, defaults, tracking, unused = generate(args.committed_only)
        unstaged, intended = inventory_status()
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
    if args.committed_only:
        summary += " mode=committed-only"
    if unused:
        summary += f" unused_overrides={len(unused)}"
    # DISCLOSED, never silent. An exclusion nobody is told about is how `MANIFEST-overrides.tsv`
    # went inert reporting as applied (BEN-321), and a transient published as repo state is
    # BEN-183. Both are announced on stdout beside the summary rather than left to be inferred.
    if args.committed_only:
        excluded = git_lines("ls-files", "--others", "--exclude-standard", "--",
                             "docs/orchestration")
        print(f"committed-only: {len(excluded)} nonignored untracked path(s) EXCLUDED from "
              f"both the table and the reference sources")
    for warning in status_warnings(unstaged, intended, args.committed_only):
        print(warning)

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
