#!/usr/bin/python3.11
"""Approval-gated deterministic command queue for unattended campaign plumbing.

Staging is not authorization.  A staged item becomes runnable only after a
human reviews its complete digest and approves it from an interactive TTY.
The ticker executes at most one ready item per invocation, without a shell.
Compute items also require a committed campaign contract, a guarded producer,
an independently bound terminal validator, and a fresh R5 meter receipt. The
validator always runs after the producer and alone selects an exhaustive
terminal branch with a decision consequence.
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
from typing import Callable


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.resolve()
DEFAULT_STATE = HERE / "state" / "campaign-queue"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PYTHON = Path("/usr/bin/python3.11")
ALLOWED_PYTHONS = {PYTHON, Path(sys.executable).resolve()}
GUARD_PATH = Path("nd-unfolding/mnv_guarded_run.py")
DEFAULT_R5_RECEIPT = Path("docs/orchestration/state/r5-meter-receipt.json")
R5_STOP_DATE = dt.datetime(2026, 9, 30, tzinfo=dt.timezone.utc)
R5_CEILINGS = {"gpu_task_hours": 500.0, "cpu_task_hours": 500.0}
R5_MAX_AGE = dt.timedelta(hours=24)

CONTRACT_KEYS = frozenset(
    {
        "schema_version",
        "campaign_id",
        "scientific_question",
        "candidate",
        "inputs",
        "terminal_validator",
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
TERMINAL_VALIDATOR_KEYS = frozenset({"argv", "cwd"})
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
R5_RECEIPT_KEYS = frozenset(
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
    }
)
R5_SOURCE_KEYS = frozenset({"kind", "argv_or_path", "raw_sha256"})
R5_SPEND_KEYS = frozenset(
    {
        "gpu_task_hours",
        "cpu_task_hours",
        "task_count",
        "metered_task_ids",
        "by_state",
    }
)
R5_FIRED_KEYS = frozenset({"date", "gpu", "cpu", "any"})


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


def require_argv(value: object, *, field: str) -> list[str]:
    """Return a nonempty subprocess argument vector."""
    if not isinstance(value, list) or not value:
        raise QueueError(f"{field} must be a nonempty array")
    return [require_text(entry, field=f"{field} entry") for entry in value]


def parse_utc(value: object, *, field: str) -> dt.datetime:
    """Parse an offset-aware UTC timestamp."""
    text = require_text(value, field=field)
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise QueueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise QueueError(f"{field} must include a UTC offset")
    return parsed.astimezone(dt.timezone.utc)


def require_nonnegative_number(value: object, *, field: str) -> float:
    """Return a finite nonnegative numeric value."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QueueError(f"{field} must be numeric")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise QueueError(f"{field} must be finite and nonnegative")
    return number


def require_finite_number(value: object, *, field: str) -> float:
    """Return a finite numeric value."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QueueError(f"{field} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise QueueError(f"{field} must be finite")
    return number


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

    terminal_validator = require_object(
        contract["terminal_validator"],
        field="terminal_validator",
        keys=TERMINAL_VALIDATOR_KEYS,
    )
    require_argv(terminal_validator["argv"], field="terminal_validator.argv")
    validator_cwd = require_text(
        terminal_validator["cwd"], field="terminal_validator.cwd"
    )
    if Path(validator_cwd).is_absolute():
        raise QueueError("terminal_validator.cwd must be repository-relative")

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
        costs[key] = require_nonnegative_number(
            maximum_cost[key], field=f"maximum_cost.{key}"
        )
    if costs["wall_hours"] <= 0:
        raise QueueError("maximum_cost.wall_hours must be positive")
    if costs["gpu_task_hours"] == 0 and costs["cpu_task_hours"] == 0:
        raise QueueError("maximum_cost must allow positive GPU or CPU task-hours")

    require_text(contract["output_namespace"], field="output_namespace")
    producer = require_text(contract["producer"], field="producer")
    validator = require_text(
        contract["independent_validator"], field="independent_validator"
    )
    authority = require_text(
        contract["decision_authority"], field="decision_authority"
    )
    identities = [producer.casefold(), validator.casefold(), authority.casefold()]
    if len(set(identities)) != len(identities):
        raise QueueError(
            "producer, independent_validator, and decision_authority identities "
            "must be pairwise distinct"
        )
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
    def __init__(
        self,
        repo: Path = REPO,
        state: Path = DEFAULT_STATE,
        clock: Callable[[], str] = utc_now,
    ) -> None:
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
                f"bound file must be committed at repository HEAD: {relative}"
            )
        return hashlib.sha256(result.stdout).hexdigest()

    def require_committed_binding(self, binding: dict[str, str]) -> None:
        """Require a binding to match the corresponding blob at ``HEAD``."""
        path = resolve_repo_path(self.repo, binding["path"])
        committed_sha256 = self.committed_file_sha256(path)
        if (
            binding["sha256"] != committed_sha256
            or sha256_file(path) != committed_sha256
        ):
            raise QueueError(
                "bound file differs from the file committed at HEAD: "
                f"{binding['path']}"
            )


def validate_id(value: str) -> None:
    if not ID_RE.fullmatch(value):
        raise QueueError(f"invalid item id: {value!r}")


def resolve_repo_path(repo: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = repo / path
    return inside(path, repo)


def command_bindings(
    repo: Path,
    argv: list[str],
    explicit: list[str],
    *,
    require_guard: bool = False,
) -> list[dict[str, str]]:
    require_argv(argv, field="command")
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
            raise QueueError(
                f"command is not an executable repository file: {executable}"
            )
        argv[0] = str(executable)
        bound.append(executable)
    if require_guard:
        guard = (repo / GUARD_PATH).resolve()
        command_file_index = 1 if Path(argv[0]).resolve() in ALLOWED_PYTHONS else 0
        if Path(argv[command_file_index]).resolve() != guard:
            raise QueueError(
                "compute producer must route through "
                "nd-unfolding/mnv_guarded_run.py"
            )
        try:
            separator_index = argv.index("--", command_file_index + 1)
        except ValueError as exc:
            raise QueueError("guarded compute command requires '-- <script>'") from exc
        if separator_index + 1 >= len(argv):
            raise QueueError(
                "guarded compute command requires a target script after '--'"
            )
        target = resolve_repo_path(repo, argv[separator_index + 1])
        if target.suffix != ".py" or not target.is_file():
            raise QueueError(f"guarded target is not a repository .py file: {target}")
        argv[separator_index + 1] = str(target)
        bound.append(target)
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


def merge_bindings(*binding_groups: list[dict[str, str]]) -> list[dict[str, str]]:
    """Merge command binding groups while requiring identical repeated hashes."""
    merged: dict[str, str] = {}
    for bindings in binding_groups:
        for binding in bindings:
            previous = merged.setdefault(binding["path"], binding["sha256"])
            if previous != binding["sha256"]:
                raise QueueError(f"inconsistent binding hash: {binding['path']}")
    return [
        {"path": path, "sha256": merged[path]}
        for path in sorted(merged)
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
    bindings = command_bindings(
        queue.repo,
        command,
        bound_inputs,
        require_guard=kind == "compute",
    )
    if contract is not None:
        terminal_validator = contract["terminal_validator"]
        if not isinstance(terminal_validator, dict):
            raise QueueError("validated campaign contract lost terminal_validator")
        validator_command = list(
            require_argv(
                terminal_validator["argv"], field="terminal_validator.argv"
            )
        )
        validator_bindings = command_bindings(
            queue.repo, validator_command, [], require_guard=False
        )
        bindings = merge_bindings(bindings, validator_bindings)
        validator_cwd = resolve_repo_path(
            queue.repo,
            require_text(terminal_validator["cwd"], field="terminal_validator.cwd"),
        )
        if not validator_cwd.is_dir():
            raise QueueError(
                f"terminal validator cwd is not a directory: {validator_cwd}"
            )
        if kind == "compute":
            maximum_cost = contract["maximum_cost"]
            if not isinstance(maximum_cost, dict):
                raise QueueError("validated campaign contract lost maximum_cost")
            maximum_wall_seconds = float(maximum_cost["wall_hours"]) * 3600
            if timeout_seconds > maximum_wall_seconds:
                raise QueueError(
                    "producer and terminal validator timeout exceeds "
                    "maximum_cost.wall_hours"
                )
    if kind == "compute":
        for binding in bindings:
            queue.require_committed_binding(binding)
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
        if item.get("kind") == "compute":
            queue.require_committed_binding(binding)


def validate_r5_receipt(value: object) -> dict[str, object]:
    """Validate the complete R5 meter receipt and its internal accounting."""
    receipt = require_object(value, field="R5 meter receipt", keys=R5_RECEIPT_KEYS)
    if receipt["schema_version"] != 1:
        raise QueueError("R5 meter receipt schema_version must be 1")
    require_text(receipt["decision_record"], field="R5 meter decision_record")
    t0 = parse_utc(receipt["t0_utc"], field="R5 meter t0_utc")
    stop_date = parse_utc(
        receipt["stop_date_utc"], field="R5 meter stop_date_utc"
    )
    measured_at = parse_utc(
        receipt["measured_at_utc"], field="R5 meter measured_at_utc"
    )
    if stop_date != R5_STOP_DATE:
        raise QueueError("R5 meter stop_date_utc does not match the ruled stop")
    if measured_at < t0:
        raise QueueError("R5 meter measured_at_utc precedes t0_utc")

    ceilings = require_object(
        receipt["ceilings"],
        field="R5 meter ceilings",
        keys=MAXIMUM_COST_KEYS - {"wall_hours"},
    )
    spend = require_object(
        receipt["spend"], field="R5 meter spend", keys=R5_SPEND_KEYS
    )
    headroom = require_object(
        receipt["headroom"],
        field="R5 meter headroom",
        keys=MAXIMUM_COST_KEYS - {"wall_hours"},
    )
    for resource, ruled_ceiling in R5_CEILINGS.items():
        ceiling = require_nonnegative_number(
            ceilings[resource], field=f"R5 meter ceilings.{resource}"
        )
        spent = require_nonnegative_number(
            spend[resource], field=f"R5 meter spend.{resource}"
        )
        remaining = require_finite_number(
            headroom[resource], field=f"R5 meter headroom.{resource}"
        )
        if ceiling != ruled_ceiling:
            raise QueueError(
                f"R5 meter ceilings.{resource} does not match the ruled ceiling"
            )
        if not math.isclose(remaining, ceiling - spent, abs_tol=1e-9):
            raise QueueError(
                f"R5 meter headroom.{resource} is inconsistent with spend"
            )

    unit = require_text(receipt["unit"], field="R5 meter unit")
    # r5_meter.py writes the unit token followed by its definition ("task-hours: sum of
    # ElapsedRaw over distinct task identities; ..."); only the token is load-bearing here.
    if unit != "task-hours" and not unit.startswith("task-hours:"):
        raise QueueError("R5 meter unit must be 'task-hours'")
    require_text(receipt["measured_on_host"], field="R5 meter measured_on_host")
    source = require_object(
        receipt["source"], field="R5 meter source", keys=R5_SOURCE_KEYS
    )
    require_text(source["kind"], field="R5 meter source.kind")
    argv_or_path = source["argv_or_path"]
    if isinstance(argv_or_path, list):
        require_argv(argv_or_path, field="R5 meter source.argv_or_path")
    else:
        require_text(argv_or_path, field="R5 meter source.argv_or_path")
    raw_sha256 = require_text(
        source["raw_sha256"], field="R5 meter source.raw_sha256"
    )
    if not SHA256_RE.fullmatch(raw_sha256):
        raise QueueError(
            "R5 meter source.raw_sha256 must be 64 lowercase hexadecimal characters"
        )

    task_count = spend["task_count"]
    if (
        isinstance(task_count, bool)
        or not isinstance(task_count, int)
        or task_count < 0
    ):
        raise QueueError("R5 meter spend.task_count must be a nonnegative integer")
    metered_task_ids = require_text_list(
        spend["metered_task_ids"], field="R5 meter spend.metered_task_ids"
    )
    if len(metered_task_ids) != task_count:
        raise QueueError("R5 meter spend.task_count does not match metered_task_ids")
    by_state = spend["by_state"]
    if not isinstance(by_state, dict) or not all(
        isinstance(state, str)
        and state
        and isinstance(count, int)
        and not isinstance(count, bool)
        and count >= 0
        for state, count in by_state.items()
    ):
        raise QueueError(
            "R5 meter spend.by_state must map state names to nonnegative integers"
        )
    if sum(by_state.values()) != task_count:
        raise QueueError("R5 meter spend.by_state does not sum to task_count")

    fired = require_object(
        receipt["fired"], field="R5 meter fired", keys=R5_FIRED_KEYS
    )
    if any(not isinstance(fired[key], bool) for key in R5_FIRED_KEYS):
        raise QueueError("R5 meter fired fields must be booleans")
    if fired["any"] != (fired["date"] or fired["gpu"] or fired["cpu"]):
        raise QueueError("R5 meter fired.any is inconsistent with trigger fields")
    return receipt


def r5_refusal_reason(queue: Queue, item: dict) -> str | None:
    """Return the compute-prohibition reason, or ``None`` when R5 permits a run."""
    receipt_value = os.environ.get("CAMPAIGN_R5_RECEIPT")
    try:
        if receipt_value is None:
            receipt_path = queue.repo / DEFAULT_R5_RECEIPT
        elif Path(receipt_value).is_absolute():
            receipt_path = Path(receipt_value).resolve()
        else:
            receipt_path = resolve_repo_path(queue.repo, receipt_value)
    except QueueError as exc:
        return f"R5 receipt malformed: {exc}"
    if not receipt_path.is_file():
        return f"R5 receipt missing: {receipt_path}"
    try:
        receipt = validate_r5_receipt(read_object(receipt_path))
    except QueueError as exc:
        return f"R5 receipt malformed: {exc}"

    now = parse_utc(queue.clock(), field="queue clock")
    measured_at = parse_utc(
        receipt["measured_at_utc"], field="R5 meter measured_at_utc"
    )
    if now - measured_at > R5_MAX_AGE:
        return "R5 receipt stale: measured_at_utc is older than 24 hours"

    fired = receipt["fired"]
    if not isinstance(fired, dict):
        raise QueueError("validated R5 receipt lost fired")
    if fired["any"] is True:
        return "R5 stop fired: receipt fired.any is true"
    stop_date = parse_utc(
        receipt["stop_date_utc"], field="R5 meter stop_date_utc"
    )
    if now >= stop_date:
        return "R5 stop date reached: queue clock is at or after stop_date_utc"

    spend = receipt["spend"]
    ceilings = receipt["ceilings"]
    contract = item["campaign_contract"]
    if not all(isinstance(value, dict) for value in (spend, ceilings, contract)):
        raise QueueError("validated compute item lost R5 accounting fields")
    maximum_cost = contract["maximum_cost"]
    if not isinstance(maximum_cost, dict):
        raise QueueError("validated campaign contract lost maximum_cost")
    for resource in ("gpu_task_hours", "cpu_task_hours"):
        projected = float(spend[resource]) + float(maximum_cost[resource])
        if projected >= float(ceilings[resource]):
            return (
                f"R5 {resource} ceiling would be reached: spend plus maximum_cost "
                "is greater than or equal to the ceiling"
            )
    return None


def state_of(queue: Queue, item: dict) -> str:
    item_id = item["id"]
    outcome_path = queue.path("outcomes", item_id)
    if outcome_path.exists():
        outcome_status = str(read_object(outcome_path).get("status", "outcome"))
        if outcome_status != "refused":
            return outcome_status
    if queue.path("claims", item_id).exists():
        return "outcome-unknown"
    if queue.path("revocations", item_id).exists():
        return "revoked"
    if outcome_path.exists():
        return "refused"
    if queue.path("approvals", item_id).exists():
        return "approved"
    return "staged"


def summary(queue: Queue) -> dict:
    values = {"staged": 0, "approved": 0, "succeeded": 0, "failed": 0,
              "refused": 0, "stale": 0, "revoked": 0, "outcome-unknown": 0}
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
    if state_of(queue, item) not in {"staged", "approved", "refused"}:
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
        if state_of(queue, item) in {
            "approved",
            "refused",
        } and dependencies_succeeded(queue, item):
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
    outcome_path = queue.path("outcomes", item["id"])
    replace_refusal = False
    if outcome_path.exists():
        existing = read_object(outcome_path)
        replace_refusal = existing.get("status") == "refused"
        if not replace_refusal:
            raise QueueError(f"refusing to overwrite: {outcome_path}")
    atomic_json(outcome_path, value, exclusive=not replace_refusal)
    return value


def run_logged_command(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: int,
    log_path: Path,
    proposal_digest: str,
) -> tuple[int | None, str | None]:
    """Run one bound command and return its code plus any launch failure."""
    try:
        with log_path.open("w") as log:
            log.write(f"proposal_digest={proposal_digest}\n")
            log.write(f"argv={canonical(argv)}\n")
            log.flush()
            completed = subprocess.run(
                argv,
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        return completed.returncode, None
    except subprocess.TimeoutExpired:
        return None, "command timed out"
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return None, f"command could not be started: {exc}"


def normalized_terminal_validator(
    queue: Queue, contract: dict[str, object]
) -> tuple[list[str], Path]:
    """Resolve the validator command and working directory from a contract."""
    terminal_validator = contract["terminal_validator"]
    if not isinstance(terminal_validator, dict):
        raise QueueError("validated campaign contract lost terminal_validator")
    argv = list(
        require_argv(terminal_validator["argv"], field="terminal_validator.argv")
    )
    command_bindings(queue.repo, argv, [], require_guard=False)
    cwd = resolve_repo_path(
        queue.repo,
        require_text(terminal_validator["cwd"], field="terminal_validator.cwd"),
    )
    return argv, cwd


def run_compute_item(queue: Queue, item: dict, env: dict[str, str]) -> tuple[int, dict]:
    """Run a producer and its mandatory independent terminal validator."""
    contract = item["campaign_contract"]
    if not isinstance(contract, dict):
        raise QueueError("validated compute item lost its campaign contract")
    timeout_seconds = int(item["timeout_seconds"])
    logs_dir = queue.state / "logs"
    producer_log = logs_dir / f"{item['id']}.producer.log"
    validator_log = logs_dir / f"{item['id']}.validator.log"
    producer_returncode, producer_error = run_logged_command(
        item["argv"],
        cwd=resolve_repo_path(queue.repo, item["cwd"]),
        env=env,
        timeout_seconds=timeout_seconds,
        log_path=producer_log,
        proposal_digest=item["proposal_digest"],
    )

    validator_env = env.copy()
    validator_env["CAMPAIGN_PRODUCER_RETURNCODE"] = (
        str(producer_returncode)
        if producer_returncode is not None
        else "TIMEOUT_OR_NOT_STARTED"
    )
    try:
        validator_argv, validator_cwd = normalized_terminal_validator(queue, contract)
    except QueueError as exc:
        validator_returncode = None
        validator_error = f"command could not be started: {exc}"
        validator_log.write_text(validator_error + "\n")
    else:
        validator_returncode, validator_error = run_logged_command(
            validator_argv,
            cwd=validator_cwd,
            env=validator_env,
            timeout_seconds=timeout_seconds,
            log_path=validator_log,
            proposal_digest=item["proposal_digest"],
        )
    status = "succeeded" if validator_returncode == 0 else "failed"
    extra: dict[str, object] = {
        "producer_returncode": producer_returncode,
        "validator_returncode": validator_returncode,
        "producer_log": str(producer_log),
        "validator_log": str(validator_log),
        **terminal_plan(contract, validator_returncode),
    }
    if producer_error is not None:
        extra["producer_error"] = producer_error
    if validator_error is not None:
        extra["validator_error"] = validator_error
    outcome = write_outcome(queue, item, status, **extra)
    return (0 if validator_returncode == 0 else 3), outcome


def run_non_compute_item(
    queue: Queue, item: dict, env: dict[str, str]
) -> tuple[int, dict]:
    """Run a non-compute queue item with the legacy single-command outcome."""
    log_path = queue.state / "logs" / f"{item['id']}.log"
    returncode, error = run_logged_command(
        item["argv"],
        cwd=resolve_repo_path(queue.repo, item["cwd"]),
        env=env,
        timeout_seconds=int(item["timeout_seconds"]),
        log_path=log_path,
        proposal_digest=item["proposal_digest"],
    )
    if returncode is None:
        outcome = write_outcome(
            queue,
            item,
            "failed",
            error=error,
            log=str(log_path),
        )
        return 3, outcome
    status = "succeeded" if returncode == 0 else "failed"
    outcome = write_outcome(
        queue,
        item,
        status,
        returncode=returncode,
        log=str(log_path),
    )
    return (0 if returncode == 0 else 3), outcome


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
    if item["kind"] == "compute":
        refusal_reason = r5_refusal_reason(queue, item)
        if refusal_reason is not None:
            outcome = write_outcome(
                queue,
                item,
                "refused",
                reason=refusal_reason,
                consumed=False,
            )
            return 6, outcome
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
    (queue.state / "logs").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CAMPAIGN_QUEUE_ITEM_ID"] = item["id"]
    if item["kind"] == "compute":
        return run_compute_item(queue, item, env)
    return run_non_compute_item(queue, item, env)


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
