#!/usr/bin/python3.11
"""Approval-gated deterministic command queue for unattended campaign plumbing.

Staging is not authorization.  A staged item becomes runnable only after a
human reviews its complete digest and approves it from an interactive TTY.
The ticker executes at most one ready item per invocation, without a shell.
Compute items also require a committed campaign contract whose terminal
branches all resolve to a decision consequence.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import math
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
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PYTHON = Path("/usr/bin/python3.11")
ALLOWED_PYTHONS = {PYTHON, Path(sys.executable).resolve()}

CONTRACT_KEYS = frozenset(
    {
        "schema_version",
        "campaign_id",
        "scientific_question",
        "candidate",
        "inputs",
        "terminal_branches",
        "maximum_cost",
        "output_namespace",
        "producer",
        "independent_validator",
        "decision_authority",
        "validator_version",
        "preservation_behavior",
        "retry_policy",
    }
)
ARTIFACT_IDENTITY_KEYS = frozenset({"id", "uri", "sha256"})
TERMINAL_BRANCH_KEYS = frozenset(
    {"id", "return_codes", "condition", "decision", "unlocks", "forbids"}
)
MAXIMUM_COST_KEYS = frozenset(
    {"gpu_task_hours", "cpu_task_hours", "wall_hours"}
)
PRESERVATION_KEYS = frozenset({"mode", "artifacts"})
RETRY_POLICY_KEYS = frozenset(
    {"automatic_retraining", "requires_new_authorization"}
)


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


def require_object(
    value: object,
    *,
    field: str,
    keys: frozenset[str],
) -> dict[str, object]:
    """Return an object after checking its complete key set."""
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise QueueError(f"{field} must be an object")
    actual = set(value)
    missing = sorted(keys - actual)
    unknown = sorted(actual - keys)
    if missing:
        raise QueueError(f"{field} is missing required field(s): {', '.join(missing)}")
    if unknown:
        raise QueueError(f"{field} has unknown field(s): {', '.join(unknown)}")
    return value


def require_text(value: object, *, field: str) -> str:
    """Return a nonempty text field with surrounding whitespace removed."""
    if not isinstance(value, str) or not value.strip():
        raise QueueError(f"{field} must be a nonempty string")
    return value.strip()


def require_text_list(value: object, *, field: str) -> list[str]:
    """Return an explicit list whose entries are nonempty strings."""
    if not isinstance(value, list):
        raise QueueError(f"{field} must be an array")
    values = [require_text(entry, field=f"{field} entry") for entry in value]
    if len(values) != len(set(values)):
        raise QueueError(f"{field} contains duplicate entries")
    return values


def validate_artifact_identity(value: object, *, field: str) -> dict[str, object]:
    """Validate an immutable candidate or input identity."""
    artifact = require_object(value, field=field, keys=ARTIFACT_IDENTITY_KEYS)
    require_text(artifact["id"], field=f"{field}.id")
    require_text(artifact["uri"], field=f"{field}.uri")
    sha256 = require_text(artifact["sha256"], field=f"{field}.sha256")
    if not SHA256_RE.fullmatch(sha256):
        raise QueueError(f"{field}.sha256 must be 64 lowercase hexadecimal characters")
    return artifact


def validate_campaign_contract(
    value: object,
    *,
    expected_campaign_id: str | None = None,
) -> dict[str, object]:
    """Validate the complete pre-execution contract for a compute campaign.

    Parameters
    ----------
    value : object
        Decoded JSON value to validate.
    expected_campaign_id : str or None, optional
        Queue item identifier that the contract must name when supplied.

    Returns
    -------
    dict[str, object]
        The validated contract object.

    Raises
    ------
    QueueError
        If a required field or cross-field safety rule is not satisfied.
    """
    contract = require_object(value, field="campaign contract", keys=CONTRACT_KEYS)
    if contract["schema_version"] != 1:
        raise QueueError("campaign contract schema_version must be 1")

    campaign_id = require_text(contract["campaign_id"], field="campaign_id")
    validate_id(campaign_id)
    if expected_campaign_id is not None and campaign_id != expected_campaign_id:
        raise QueueError(
            f"campaign contract id {campaign_id!r} does not match queue item "
            f"{expected_campaign_id!r}"
        )
    require_text(contract["scientific_question"], field="scientific_question")
    validate_artifact_identity(contract["candidate"], field="candidate")

    inputs = contract["inputs"]
    if not isinstance(inputs, list) or not inputs:
        raise QueueError("inputs must be a nonempty array")
    input_identities = [
        validate_artifact_identity(entry, field=f"inputs[{index}]")
        for index, entry in enumerate(inputs)
    ]
    input_ids = [str(identity["id"]) for identity in input_identities]
    input_uris = [str(identity["uri"]) for identity in input_identities]
    if len(input_ids) != len(set(input_ids)):
        raise QueueError("inputs contain duplicate ids")
    if len(input_uris) != len(set(input_uris)):
        raise QueueError("inputs contain duplicate uris")

    terminal_branches = contract["terminal_branches"]
    if not isinstance(terminal_branches, list) or not terminal_branches:
        raise QueueError("terminal_branches must be a nonempty array")
    branch_ids: set[str] = set()
    claimed_return_codes: set[int] = set()
    fallback_count = 0
    for index, value_branch in enumerate(terminal_branches):
        field = f"terminal_branches[{index}]"
        branch = require_object(value_branch, field=field, keys=TERMINAL_BRANCH_KEYS)
        branch_id = require_text(branch["id"], field=f"{field}.id")
        validate_id(branch_id)
        if branch_id in branch_ids:
            raise QueueError(f"duplicate terminal branch id: {branch_id}")
        branch_ids.add(branch_id)

        return_codes = branch["return_codes"]
        if return_codes == "otherwise":
            fallback_count += 1
        elif isinstance(return_codes, list) and return_codes:
            if any(
                isinstance(code, bool) or not isinstance(code, int)
                for code in return_codes
            ):
                raise QueueError(f"{field}.return_codes must contain only integers")
            if len(return_codes) != len(set(return_codes)):
                raise QueueError(f"{field}.return_codes contains duplicates")
            overlap = claimed_return_codes.intersection(return_codes)
            if overlap:
                raise QueueError(
                    "return code(s) assigned to multiple terminal branches: "
                    + ", ".join(str(code) for code in sorted(overlap))
                )
            claimed_return_codes.update(return_codes)
        else:
            raise QueueError(
                f"{field}.return_codes must be a nonempty integer array or 'otherwise'"
            )

        require_text(branch["condition"], field=f"{field}.condition")
        require_text(branch["decision"], field=f"{field}.decision")
        require_text_list(branch["unlocks"], field=f"{field}.unlocks")
        require_text_list(branch["forbids"], field=f"{field}.forbids")
    if fallback_count != 1:
        raise QueueError(
            "terminal_branches must contain exactly one 'otherwise' branch so every "
            "possible terminal result has a decision consequence"
        )

    maximum_cost = require_object(
        contract["maximum_cost"], field="maximum_cost", keys=MAXIMUM_COST_KEYS
    )
    costs: dict[str, float] = {}
    for key in sorted(MAXIMUM_COST_KEYS):
        amount = maximum_cost[key]
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise QueueError(f"maximum_cost.{key} must be numeric")
        costs[key] = float(amount)
        if not math.isfinite(costs[key]) or costs[key] < 0:
            raise QueueError(f"maximum_cost.{key} must be finite and nonnegative")
    if costs["wall_hours"] <= 0:
        raise QueueError("maximum_cost.wall_hours must be positive")
    if costs["gpu_task_hours"] == 0 and costs["cpu_task_hours"] == 0:
        raise QueueError("maximum_cost must allow positive GPU or CPU task-hours")

    require_text(contract["output_namespace"], field="output_namespace")
    producer = require_text(contract["producer"], field="producer")
    validator = require_text(
        contract["independent_validator"], field="independent_validator"
    )
    if producer.casefold() == validator.casefold():
        raise QueueError("producer and independent_validator identities must differ")
    require_text(contract["decision_authority"], field="decision_authority")
    require_text(contract["validator_version"], field="validator_version")

    preservation = require_object(
        contract["preservation_behavior"],
        field="preservation_behavior",
        keys=PRESERVATION_KEYS,
    )
    if preservation["mode"] != "preserve-first":
        raise QueueError("preservation_behavior.mode must be 'preserve-first'")
    preserved_artifacts = require_text_list(
        preservation["artifacts"], field="preservation_behavior.artifacts"
    )
    if not preserved_artifacts:
        raise QueueError("preservation_behavior.artifacts must be nonempty")

    retry_policy = require_object(
        contract["retry_policy"], field="retry_policy", keys=RETRY_POLICY_KEYS
    )
    if retry_policy["automatic_retraining"] is not False:
        raise QueueError("retry_policy.automatic_retraining must be false")
    if retry_policy["requires_new_authorization"] is not True:
        raise QueueError("retry_policy.requires_new_authorization must be true")
    return contract


def terminal_plan(
    contract: dict[str, object], returncode: int | None
) -> dict[str, object]:
    """Resolve a process result to its required preservation and decision actions."""
    branches = contract["terminal_branches"]
    if not isinstance(branches, list):
        raise QueueError("validated campaign contract lost terminal_branches")
    selected: dict[str, object] | None = None
    fallback: dict[str, object] | None = None
    for value_branch in branches:
        if not isinstance(value_branch, dict):
            raise QueueError("validated campaign contract has a non-object branch")
        if value_branch["return_codes"] == "otherwise":
            fallback = value_branch
        elif returncode in value_branch["return_codes"]:
            selected = value_branch
            break
    branch = selected or fallback
    if branch is None:
        raise QueueError("validated campaign contract has no fallback branch")

    preservation = contract["preservation_behavior"]
    retry_policy = contract["retry_policy"]
    if not isinstance(preservation, dict) or not isinstance(retry_policy, dict):
        raise QueueError("validated campaign contract lost terminal policy objects")
    return {
        "terminal_branch": branch["id"],
        "decision_consequence": branch["decision"],
        "unlocks": branch["unlocks"],
        "forbids": branch["forbids"],
        "required_actions": [
            {
                "action": "preserve",
                "mode": preservation["mode"],
                "artifacts": preservation["artifacts"],
            },
            {
                "action": "refer-decision",
                "authority": contract["decision_authority"],
                "consequence": branch["decision"],
            },
        ],
        "automatic_retraining": retry_policy["automatic_retraining"],
        "retry_requires_new_authorization": retry_policy[
            "requires_new_authorization"
        ],
    }


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

    def committed_file_sha256(self, path: Path) -> str:
        """Return the SHA-256 of a file as committed at the queue's HEAD."""
        relative = inside(path, self.repo).relative_to(self.repo).as_posix()
        result = subprocess.run(
            ["git", "-C", str(self.repo), "show", f"HEAD:{relative}"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise QueueError(
                "campaign contract must be committed at repository HEAD: "
                f"{relative}"
            )
        return hashlib.sha256(result.stdout).hexdigest()


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
    payload = {key: item[key] for key in keys}
    for key in ("campaign_contract_path", "campaign_contract"):
        if key in item:
            payload[key] = item[key]
    return payload


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
    campaign_contract: str | None = None,
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

    contract: dict[str, object] | None = None
    contract_path: Path | None = None
    if campaign_contract is None:
        if kind == "compute":
            raise QueueError("compute items require a committed campaign contract")
    else:
        contract_path = resolve_repo_path(queue.repo, campaign_contract)
        if not contract_path.is_file():
            raise QueueError(f"campaign contract is not a file: {contract_path}")
        contract = validate_campaign_contract(
            read_object(contract_path), expected_campaign_id=item_id
        )
        committed_sha256 = queue.committed_file_sha256(contract_path)
        if sha256_file(contract_path) != committed_sha256:
            raise QueueError(
                "campaign contract differs from the file committed at HEAD"
            )

    command = list(argv)
    if command and command[0] == "--":
        command = command[1:]
    bound_inputs = list(bind)
    if contract_path is not None:
        bound_inputs.append(str(contract_path))
    bindings = command_bindings(queue.repo, command, bound_inputs)
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
    if contract is not None and contract_path is not None:
        item["campaign_contract_path"] = str(contract_path.relative_to(queue.repo))
        item["campaign_contract"] = contract
    item["proposal_digest"] = digest(proposal_payload(item))
    atomic_json(queue.path("items", item_id), item, exclusive=True)
    return item


def validate_unchanged(queue: Queue, item: dict) -> None:
    expected = item.get("proposal_digest")
    if expected != digest(proposal_payload(item)):
        raise QueueError("proposal JSON does not match its digest")
    if queue.git_head() != item["git_head"]:
        raise QueueError("repository HEAD changed after staging")
    contract = item.get("campaign_contract")
    if item.get("kind") == "compute" and not isinstance(contract, dict):
        raise QueueError("compute items require a committed campaign contract")
    if contract is not None:
        if not isinstance(contract, dict):
            raise QueueError("embedded campaign contract must be an object")
        validate_campaign_contract(contract, expected_campaign_id=item["id"])
        contract_path = item.get("campaign_contract_path")
        if not isinstance(contract_path, str):
            raise QueueError("campaign contract path is missing")
        if read_object(resolve_repo_path(queue.repo, contract_path)) != contract:
            raise QueueError("embedded campaign contract differs from its bound file")
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
        contract = item.get("campaign_contract")
        contract_fields = (
            terminal_plan(contract, result.returncode)
            if isinstance(contract, dict)
            else {}
        )
        outcome = write_outcome(
            queue,
            item,
            status,
            returncode=result.returncode,
            log=str(log_path),
            **contract_fields,
        )
        return (0 if result.returncode == 0 else 3), outcome
    except subprocess.TimeoutExpired:
        contract = item.get("campaign_contract")
        contract_fields = (
            terminal_plan(contract, None) if isinstance(contract, dict) else {}
        )
        outcome = write_outcome(
            queue,
            item,
            "failed",
            error="command timed out",
            log=str(log_path),
            **contract_fields,
        )
        return 3, outcome
    except Exception as exc:
        contract = item.get("campaign_contract")
        contract_fields = (
            terminal_plan(contract, None) if isinstance(contract, dict) else {}
        )
        outcome = write_outcome(
            queue,
            item,
            "failed",
            error=f"launcher error: {exc}",
            log=str(log_path),
            **contract_fields,
        )
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
    p.add_argument("--contract")
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
            value = stage(
                queue,
                args.id,
                args.description,
                args.kind,
                args.cwd,
                args.depends_on,
                args.bind,
                args.argv,
                args.timeout_seconds,
                args.contract,
            )
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
