#!/usr/bin/python3.11
"""Approval-gated deterministic command queue for unattended campaign plumbing.

Staging is not authorization.  A staged item becomes runnable only after a
human reviews its complete digest and approves it from an interactive TTY.
The ticker executes at most one ready item per invocation, without a shell.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.resolve()
DEFAULT_STATE = HERE / "state" / "campaign-queue"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
PYTHON = Path("/usr/bin/python3.11")
ALLOWED_PYTHONS = {PYTHON, Path(sys.executable).resolve()}


class QueueError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inside(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise QueueError(f"path is outside repository: {path}") from exc
    return resolved


def atomic_json(path: Path, value: dict, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if exclusive:
            try:
                os.link(temporary, path)
            except FileExistsError as exc:
                raise QueueError(f"refusing to overwrite: {path}") from exc
        else:
            os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            temporary.unlink()


def read_object(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise QueueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise QueueError(f"expected JSON object: {path}")
    return value


class Queue:
    def __init__(self, repo: Path = REPO, state: Path = DEFAULT_STATE, clock=utc_now):
        self.repo = repo.resolve()
        self.state = state.resolve()
        self.clock = clock

    def path(self, family: str, item_id: str) -> Path:
        validate_id(item_id)
        return self.state / family / f"{item_id}.json"

    def item(self, item_id: str) -> dict:
        return read_object(self.path("items", item_id))

    def items(self) -> list[dict]:
        root = self.state / "items"
        if not root.is_dir():
            return []
        return [read_object(path) for path in sorted(root.glob("*.json"))]

    def git_head(self) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise QueueError(f"cannot resolve repository HEAD: {result.stdout.strip()}")
        return result.stdout.strip()


def validate_id(value: str) -> None:
    if not ID_RE.fullmatch(value):
        raise QueueError(f"invalid item id: {value!r}")


def resolve_repo_path(repo: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = repo / path
    return inside(path, repo)


def command_bindings(repo: Path, argv: list[str], explicit: list[str]) -> list[dict]:
    if not argv or not all(isinstance(x, str) and x for x in argv):
        raise QueueError("command must be a nonempty string array")
    executable = Path(argv[0])
    bound: list[Path] = []
    if executable.resolve() in ALLOWED_PYTHONS:
        if len(argv) < 2 or argv[1].startswith("-"):
            raise QueueError("python commands must name a repository .py file")
        script = resolve_repo_path(repo, argv[1])
        if script.suffix != ".py" or not script.is_file():
            raise QueueError(f"python target is not a repository .py file: {script}")
        argv[1] = str(script)
        bound.append(script)
    else:
        executable = resolve_repo_path(repo, argv[0])
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise QueueError(f"command is not an executable repository file: {executable}")
        argv[0] = str(executable)
        bound.append(executable)
    for value in explicit:
        path = resolve_repo_path(repo, value)
        if not path.is_file():
            raise QueueError(f"bound input is not a file: {path}")
        bound.append(path)
    unique = sorted(set(bound), key=lambda p: str(p))
    return [
        {"path": str(path.relative_to(repo)), "sha256": sha256_file(path)}
        for path in unique
    ]


def proposal_payload(item: dict) -> dict:
    keys = (
        "schema_version", "id", "description", "kind", "argv", "cwd",
        "depends_on", "bindings", "git_head", "timeout_seconds",
    )
    return {key: item[key] for key in keys}


def stage(
    queue: Queue,
    item_id: str,
    description: str,
    kind: str,
    cwd: str,
    depends_on: list[str],
    bind: list[str],
    argv: list[str],
    timeout_seconds: int,
) -> dict:
    validate_id(item_id)
    if not description.strip():
        raise QueueError("description is required")
    if timeout_seconds < 1 or timeout_seconds > 3600:
        raise QueueError("timeout must be between 1 and 3600 seconds")
    for dependency in depends_on:
        validate_id(dependency)
        if dependency == item_id:
            raise QueueError("an item cannot depend on itself")
        queue.item(dependency)
    command = list(argv)
    if command and command[0] == "--":
        command = command[1:]
    bindings = command_bindings(queue.repo, command, bind)
    cwd_path = resolve_repo_path(queue.repo, cwd)
    if not cwd_path.is_dir():
        raise QueueError(f"cwd is not a directory: {cwd_path}")
    item = {
        "schema_version": 1,
        "id": item_id,
        "description": description.strip(),
        "kind": kind,
        "argv": command,
        "cwd": str(cwd_path.relative_to(queue.repo)) or ".",
        "depends_on": sorted(set(depends_on)),
        "bindings": bindings,
        "git_head": queue.git_head(),
        "timeout_seconds": timeout_seconds,
        "created_at_utc": queue.clock(),
        "created_by": f"{os.environ.get('USER', 'unknown')}@{socket.gethostname()}",
    }
    item["proposal_digest"] = digest(proposal_payload(item))
    atomic_json(queue.path("items", item_id), item, exclusive=True)
    return item


def validate_unchanged(queue: Queue, item: dict) -> None:
    expected = item.get("proposal_digest")
    if expected != digest(proposal_payload(item)):
        raise QueueError("proposal JSON does not match its digest")
    if queue.git_head() != item["git_head"]:
        raise QueueError("repository HEAD changed after staging")
    for binding in item["bindings"]:
        path = resolve_repo_path(queue.repo, binding["path"])
        if not path.is_file() or sha256_file(path) != binding["sha256"]:
            raise QueueError(f"bound file changed after staging: {binding['path']}")


def state_of(queue: Queue, item: dict) -> str:
    item_id = item["id"]
    outcome_path = queue.path("outcomes", item_id)
    if outcome_path.exists():
        return str(read_object(outcome_path).get("status", "outcome"))
    if queue.path("claims", item_id).exists():
        return "outcome-unknown"
    if queue.path("revocations", item_id).exists():
        return "revoked"
    if queue.path("approvals", item_id).exists():
        return "approved"
    return "staged"


def summary(queue: Queue) -> dict:
    values = {"staged": 0, "approved": 0, "succeeded": 0, "failed": 0,
              "stale": 0, "revoked": 0, "outcome-unknown": 0}
    rows = []
    for item in queue.items():
        state = state_of(queue, item)
        values[state] = values.get(state, 0) + 1
        rows.append({"id": item["id"], "state": state, "digest": item["proposal_digest"]})
    return {"counts": values, "items": rows}


def approval_phrase(item: dict) -> str:
    return f"APPROVE {item['id']} {item['proposal_digest'][:12]}"


def approve(queue: Queue, item_id: str, supplied_digest: str, interactive: bool = True) -> dict:
    item = queue.item(item_id)
    if state_of(queue, item) != "staged":
        raise QueueError(f"item is not staged: {state_of(queue, item)}")
    validate_unchanged(queue, item)
    if supplied_digest != item["proposal_digest"]:
        raise QueueError("supplied digest does not match the staged proposal")
    if interactive:
        if not sys.stdin.isatty():
            raise QueueError("approval requires an interactive TTY")
        print(json.dumps(item, indent=2, sort_keys=True))
        phrase = approval_phrase(item)
        print(f"Type exactly: {phrase}")
        if input("> ").strip() != phrase:
            raise QueueError("approval phrase did not match")
    receipt = {
        "schema_version": 1,
        "id": item_id,
        "proposal_digest": supplied_digest,
        "approved_at_utc": queue.clock(),
        "approved_by": f"{os.environ.get('USER', 'unknown')}@{socket.gethostname()}",
        "interactive_tty": interactive,
    }
    atomic_json(queue.path("approvals", item_id), receipt, exclusive=True)
    return receipt


def revoke(queue: Queue, item_id: str, interactive: bool = True) -> dict:
    item = queue.item(item_id)
    if state_of(queue, item) not in {"staged", "approved"}:
        raise QueueError(f"item cannot be revoked from state {state_of(queue, item)}")
    if interactive:
        if not sys.stdin.isatty():
            raise QueueError("revocation requires an interactive TTY")
        phrase = f"REVOKE {item_id}"
        print(f"Type exactly: {phrase}")
        if input("> ").strip() != phrase:
            raise QueueError("revocation phrase did not match")
    receipt = {"schema_version": 1, "id": item_id, "revoked_at_utc": queue.clock()}
    atomic_json(queue.path("revocations", item_id), receipt, exclusive=True)
    return receipt


def dependencies_succeeded(queue: Queue, item: dict) -> bool:
    for dependency in item["depends_on"]:
        outcome_path = queue.path("outcomes", dependency)
        if not outcome_path.exists() or read_object(outcome_path).get("status") != "succeeded":
            return False
    return True


def ready_item(queue: Queue) -> dict | None:
    candidates = sorted(queue.items(), key=lambda x: (x["created_at_utc"], x["id"]))
    for item in candidates:
        if state_of(queue, item) == "approved" and dependencies_succeeded(queue, item):
            return item
    return None


def write_outcome(queue: Queue, item: dict, status: str, **extra: object) -> dict:
    value = {
        "schema_version": 1,
        "id": item["id"],
        "proposal_digest": item["proposal_digest"],
        "status": status,
        "completed_at_utc": queue.clock(),
        **extra,
    }
    atomic_json(queue.path("outcomes", item["id"]), value, exclusive=True)
    return value


def run_ready(queue: Queue) -> tuple[int, dict]:
    item = ready_item(queue)
    if item is None:
        unknown = [row for row in summary(queue)["items"] if row["state"] == "outcome-unknown"]
        if unknown:
            return 5, {"status": "outcome-unknown", "items": [x["id"] for x in unknown]}
        return 0, {"status": "idle"}
    approval = read_object(queue.path("approvals", item["id"]))
    if approval.get("proposal_digest") != item["proposal_digest"]:
        outcome = write_outcome(queue, item, "stale", error="approval digest mismatch")
        return 4, outcome
    try:
        validate_unchanged(queue, item)
    except QueueError as exc:
        outcome = write_outcome(queue, item, "stale", error=str(exc))
        return 4, outcome
    claim = {
        "schema_version": 1,
        "id": item["id"],
        "proposal_digest": item["proposal_digest"],
        "claimed_at_utc": queue.clock(),
        "owner": f"{socket.gethostname()}:{os.getpid()}",
    }
    try:
        atomic_json(queue.path("claims", item["id"]), claim, exclusive=True)
    except QueueError:
        return 5, {"status": "outcome-unknown", "id": item["id"]}
    log_path = queue.state / "logs" / f"{item['id']}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CAMPAIGN_QUEUE_ITEM_ID"] = item["id"]
    try:
        with log_path.open("w") as log:
            log.write(f"proposal_digest={item['proposal_digest']}\n")
            log.write(f"argv={canonical(item['argv'])}\n")
            log.flush()
            result = subprocess.run(
                item["argv"],
                cwd=resolve_repo_path(queue.repo, item["cwd"]),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                timeout=int(item["timeout_seconds"]),
            )
        status = "succeeded" if result.returncode == 0 else "failed"
        outcome = write_outcome(
            queue, item, status, returncode=result.returncode, log=str(log_path)
        )
        return (0 if result.returncode == 0 else 3), outcome
    except subprocess.TimeoutExpired:
        outcome = write_outcome(queue, item, "failed", error="command timed out", log=str(log_path))
        return 3, outcome
    except Exception as exc:
        outcome = write_outcome(queue, item, "failed", error=f"launcher error: {exc}", log=str(log_path))
        return 3, outcome


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", default=os.environ.get("CAMPAIGN_QUEUE_STATE_DIR", str(DEFAULT_STATE)))
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("stage")
    p.add_argument("--id", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--kind", choices=("read-only", "write", "compute"), required=True)
    p.add_argument("--cwd", default=".")
    p.add_argument("--depends-on", action="append", default=[])
    p.add_argument("--bind", action="append", default=[])
    p.add_argument("--timeout-seconds", type=int, default=600)
    p.add_argument("argv", nargs=argparse.REMAINDER)
    p = sub.add_parser("show")
    p.add_argument("--id", required=True)
    p = sub.add_parser("approve")
    p.add_argument("--id", required=True)
    p.add_argument("--digest", required=True)
    p = sub.add_parser("revoke")
    p.add_argument("--id", required=True)
    sub.add_parser("list")
    sub.add_parser("status").add_argument("--json", action="store_true")
    sub.add_parser("run-ready").add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    queue = Queue(state=Path(args.state_dir))
    try:
        if args.action == "stage":
            value = stage(queue, args.id, args.description, args.kind, args.cwd,
                          args.depends_on, args.bind, args.argv, args.timeout_seconds)
            print(json.dumps(value, indent=2, sort_keys=True))
            return 0
        if args.action == "show":
            print(json.dumps(queue.item(args.id), indent=2, sort_keys=True))
            return 0
        if args.action == "approve":
            print(json.dumps(approve(queue, args.id, args.digest), indent=2, sort_keys=True))
            return 0
        if args.action == "revoke":
            print(json.dumps(revoke(queue, args.id), indent=2, sort_keys=True))
            return 0
        if args.action in {"list", "status"}:
            value = summary(queue)
            if args.action == "status" and args.json:
                print(canonical(value))
            else:
                for row in value["items"]:
                    print(f"{row['id']}\t{row['state']}\t{row['digest'][:12]}")
                print("counts " + canonical(value["counts"]))
            return 0
        if args.action == "run-ready":
            rc, value = run_ready(queue)
            print(canonical(value) if args.json else json.dumps(value, indent=2, sort_keys=True))
            return rc
        raise QueueError(f"unknown action: {args.action}")
    except QueueError as exc:
        print(f"campaignctl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
