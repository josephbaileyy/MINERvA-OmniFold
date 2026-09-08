#!/usr/bin/env python3
"""Read-only check of a STAGED campaign item, to be run before approval is requested.

WHY THIS EXISTS.  ``campaignctl stage`` defaults ``--timeout-seconds`` to 600
(``campaignctl.py:4540``) and accepts anything up to ``maximum_cost.wall_hours * 3600``
(``:2822``).  At 600 the launcher is ``SIGKILL``ed mid-wait: no cancellation, no terminal
verification, a submitted job left running with nobody holding its identity.  That number is
not implied by the contract and appears nowhere in the approval prompt, so it has to be caught
by inspecting the staged item BEFORE a human is asked to approve anything.

HOW IT CHECKS, and why the first version of this file was wrong.  It does not compare the item
against a list of things somebody thought to look at.  It REBUILDS the derived fields from the
committed tree using the controller's own helpers -- ``command_bindings``, ``merge_bindings``,
``validate_campaign_contract``, ``proposal_payload``, ``digest`` -- and requires the staged item
to equal what those produce.  A partial whitelist passes everything nobody listed: the first
version accepted a forged ``proposal_digest``, unrelated bindings, a raised ``cpu_task_hours``,
a validator pointed at another script, and ``--campaign-mode standalone`` whenever the word
``required`` appeared anywhere else in the argv.  It also compared the argv against RELATIVE
paths, while ``command_bindings`` rewrites the guard target and the script to absolute
(``:2621``, ``:2650``) -- so it would have rejected the real staged item and passed a forged one.

The controller it imports is the one in the checkout being inspected, because that is the
controller that will run the item.

WHAT IT IS NOT.  It writes nothing, contacts no scheduler, reaches no network, and makes no
queue writes.  It is not an authorization and it does not approve.  A PASS says only that what
is staged is what the committed tree produces.

USE:
    campaignctl ... show --id pm-root-inspection-20260908 > staged-item.json
    check_staged_item.py --item staged-item.json --repo <integrated checkout> \
        --expect-head <the reviewed head>

Exit 0 only when every check passes; the approve line is printed only then.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pm_root_inspect as producer  # noqa: E402

CAMPAIGN_ID = "pm-root-inspection-20260908"
CONTRACT_PATH = "docs/orchestration/contracts/CONTRACT-20260908-pm-root-inspection.json"
BINDINGS_PATH = "nd-unfolding/pm_inspection/INPUT-BINDINGS-20260908.json"
PRODUCER_PATH = "nd-unfolding/pm_inspection/pm_root_inspect.py"
GUARD_PATH = "nd-unfolding/mnv_guarded_run.py"
DATA_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
INNER_PYTHON = "/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python"
OUTER_PYTHON = "/usr/bin/python3.11"
DEFAULT_EXPECT_ROOT = "/pscratch/sd/j/josephrb/exec-20260907"
DESCRIPTION = (
    "Bounded attended read-only ROOT inspection for PM-1/PM-3/PM-4/PM-5")

#: The reviewed cost envelope, pinned here so a later edit to the committed contract has to
#: pass a reviewer rather than only a JSON parser.
REVIEWED_MAXIMUM_COST = {"gpu_task_hours": 0.0, "cpu_task_hours": 0.5, "wall_hours": 0.5}

#: sha256 of the contract that was reviewed (commit 9f12c728). Comparing the staged item to
#: the COMMITTED contract only proves they agree; it does not say WHICH contract is committed.
#: A stale copy with a filesystem output_namespace and --report/--out literals rides on the
#: launcher branch, and an item staged from it would agree with itself perfectly. Editing the
#: contract must therefore change this constant, which means passing a reviewer.
REVIEWED_CONTRACT_SHA256 = (
    "5351d9da730349ef59a3690d2b1367f026ee95fe74b40a53c08e41c15cf752d7")


class CheckError(Exception):
    """The check could not be completed. Never a PASS."""


def literal_argv(expect_root: str) -> list[str]:
    """The producer argv the runbook stages, exactly as typed, before normalization.

    Every value is written out even where it equals a default, because the digest a human
    approves covers the argv: a flag left to a default is a flag nobody approved.
    ``--minutes`` comes from the launcher itself, so the two cannot drift apart silently.
    """
    return [
        OUTER_PYTHON,
        GUARD_PATH,
        "--expect-root", expect_root,
        "--label", "pm-root-inspection-launch",
        "--",
        PRODUCER_PATH,
        "--mode", "launch",
        "--bindings", BINDINGS_PATH,
        "--data-root", DATA_ROOT,
        "--inner-python", INNER_PYTHON,
        "--expect-root", expect_root,
        "--account", "m3246",
        "--qos", "debug",
        "--minutes", str(producer.DEFAULT_MINUTES),
        "--comment", CAMPAIGN_ID,
    ]


def load_controller(repo: Path):
    """Import the campaignctl of the checkout under inspection, not of this file's tree."""
    path = repo / "docs/orchestration/campaignctl.py"
    if not path.is_file():
        raise CheckError(f"no controller to check against at {path}")
    spec = importlib.util.spec_from_file_location("campaignctl_under_check", path)
    if spec is None or spec.loader is None:
        raise CheckError(f"controller at {path} could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def head_of(repo: Path) -> str:
    result = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                            capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise CheckError(f"could not read HEAD of {repo}: {result.stderr.strip()}")
    return result.stdout.strip()


def rebuild(repo: Path, ctl, *, expect_root: str, timeout_seconds: int) -> dict:
    """Rebuild the item's derived fields from the committed tree, the controller's way."""
    contract_file = repo / CONTRACT_PATH
    if not contract_file.is_file():
        raise CheckError(f"no committed contract at {contract_file}")
    contract = ctl.validate_campaign_contract(
        ctl.read_object(contract_file), expected_campaign_id=CAMPAIGN_ID)

    argv = literal_argv(expect_root)          # command_bindings normalizes this IN PLACE
    producer_bindings = ctl.command_bindings(
        repo, argv, [BINDINGS_PATH, CONTRACT_PATH], require_guard=True)
    validator_bindings = ctl.command_bindings(
        repo, list(contract["terminal_validator"]["argv"]), [],
        require_guard=True, role="compute terminal validator")
    return {
        "schema_version": 1,
        "id": CAMPAIGN_ID,
        "description": DESCRIPTION,
        "kind": "compute",
        "argv": argv,
        "cwd": ".",
        "depends_on": [],
        "bindings": ctl.merge_bindings(producer_bindings, validator_bindings),
        "repo_path": str(repo),
        "timeout_seconds": timeout_seconds,
        "campaign_contract_path": CONTRACT_PATH,
        "campaign_contract": contract,
    }


def adjacent(argv: list[str], flag: str, value: str) -> bool:
    """True only when ``value`` is the element after ``flag``.

    The first version of this file asked whether both strings appeared anywhere in the argv,
    so ``--campaign-mode standalone`` passed whenever the word ``required`` appeared
    elsewhere. A flag's value is the element after it, and nothing else is.
    """
    return any(argv[i] == flag and argv[i + 1] == value for i in range(len(argv) - 1))


def check_item(item: dict, *, repo: Path, expect_head: str | None = None,
               expect_root: str = DEFAULT_EXPECT_ROOT, ctl=None,
               expect_contract_sha256: str | None = REVIEWED_CONTRACT_SHA256) -> list[str]:
    """Return the findings. Empty means the staged item is what the committed tree produces."""
    repo = Path(repo).resolve()
    if ctl is None:
        ctl = load_controller(repo)
    bad: list[str] = []

    staged_timeout = int(producer.STAGED_TIMEOUT_SECONDS)
    if item.get("timeout_seconds") != staged_timeout:
        bad.append(
            f"timeout_seconds is {item.get('timeout_seconds')!r}, not {staged_timeout}. "
            "campaignctl defaults this to 600, at which the launcher is killed mid-wait and "
            "its cleanup never runs. Re-stage; do NOT approve this item.")

    try:
        expected = rebuild(repo, ctl, expect_root=expect_root,
                           timeout_seconds=staged_timeout)
    except CheckError:
        raise
    except Exception as error:                       # QueueError and anything it wraps
        raise CheckError(
            f"the committed tree does not produce a stageable item: "
            f"{type(error).__name__}: {error}") from error

    # Field-for-field against what the controller would build. Anything not named here is
    # covered by the digest check below, which recomputes over the whole proposal payload.
    for field in ("schema_version", "id", "description", "kind", "argv", "cwd",
                  "depends_on", "bindings", "repo_path", "campaign_contract_path",
                  "campaign_contract"):
        if item.get(field) != expected[field]:
            bad.append(
                f"{field} is not what the committed tree produces.\n"
                f"      staged: {json.dumps(item.get(field), sort_keys=True)[:400]}\n"
                f"    expected: {json.dumps(expected[field], sort_keys=True)[:400]}")

    # Which contract is committed, not merely whether the item agrees with it.
    if expect_contract_sha256 is not None:
        try:
            on_disk = ctl.sha256_file(repo / CONTRACT_PATH)
        except Exception as error:
            bad.append(f"could not digest the committed contract: {error}")
        else:
            if on_disk != expect_contract_sha256:
                bad.append(
                    f"the contract at {CONTRACT_PATH} digests to {on_disk}, not the reviewed "
                    f"{expect_contract_sha256}. A stale copy of this contract exists with a "
                    "filesystem output_namespace and --report/--out literals; an item staged "
                    "from it would agree with itself. Re-review before changing this pin.")

    validator_argv = list(
        ((item.get("campaign_contract") or {}).get("terminal_validator") or {}).get("argv")
        or [])
    if not adjacent(validator_argv, "--campaign-mode", "required"):
        bad.append("terminal_validator.argv does not pass --campaign-mode required as an "
                   "adjacent flag/value pair; a validator in standalone mode does not refuse "
                   "a producer that never ran")

    # The reviewed cost envelope, pinned so an edited committed contract does not pass here
    # merely because the item matches it.
    cost = (item.get("campaign_contract") or {}).get("maximum_cost")
    if cost != REVIEWED_MAXIMUM_COST:
        bad.append(f"maximum_cost is {json.dumps(cost, sort_keys=True)}, not the reviewed "
                   f"{json.dumps(REVIEWED_MAXIMUM_COST, sort_keys=True)}")
    else:
        wall = float(cost["wall_hours"]) * 3600
        # On the ITEM's own value, not on the constant: checking the constant against a
        # constant is a tautology that can never fire, which is what it was doing.
        actual = item.get("timeout_seconds")
        if isinstance(actual, int) and actual + producer.VALIDATOR_RESERVE_SECONDS > wall:
            bad.append(
                f"staged {actual}s plus the validator's "
                f"{producer.VALIDATOR_RESERVE_SECONDS:g}s reserve exceeds the {wall:g}s the "
                "producer and validator share; the validator would not be started")

    # Every bound file must be committed at HEAD and identical in the working tree. This is
    # the controller's own rule, asked of the controller rather than reimplemented.
    with tempfile.TemporaryDirectory() as scratch:
        queue = ctl.Queue(repo=repo, state=Path(scratch))
        for binding in item.get("bindings") or []:
            try:
                queue.require_committed_binding(binding)
            except Exception as error:
                bad.append(f"binding {binding.get('path')!r} is not committed-and-identical: "
                           f"{error}")
        try:
            actual_head = queue.git_head()
        except Exception as error:
            actual_head = None
            bad.append(f"could not read HEAD of the checkout under inspection: {error}")

    if actual_head is not None and item.get("git_head") != actual_head:
        bad.append(f"git_head is {item.get('git_head')!r}, but the checkout under inspection "
                   f"is at {actual_head!r}")
    if expect_head is not None and item.get("git_head") != expect_head:
        bad.append(f"git_head is {item.get('git_head')!r}, not the reviewed {expect_head!r}")

    # A digest recomputed over the staged item's own payload. A forged digest fails here even
    # when every field above matches, and a field this file forgot to name fails here too.
    try:
        recomputed = ctl.digest(ctl.proposal_payload(item))
    except Exception as error:
        bad.append(f"the item has no recomputable proposal payload: {error}")
    else:
        if item.get("proposal_digest") != recomputed:
            bad.append(
                f"proposal_digest is {item.get('proposal_digest')!r}, but the item's own "
                f"payload digests to {recomputed!r}. Approval binds the digest, so this item "
                "would admit something other than what it displays.")
    return bad


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--item", type=Path, required=True,
                        help="JSON from `campaignctl show --id ...`")
    parser.add_argument("--repo", type=Path, default=Path.cwd(),
                        help="the integrated checkout the item was staged from")
    parser.add_argument("--expect-head",
                        help="the reviewed head; checked in ADDITION to the checkout's HEAD")
    parser.add_argument("--expect-root", default=DEFAULT_EXPECT_ROOT,
                        help="the execution checkout the guard is pinned to")
    parser.add_argument("--expect-contract-sha256", default=REVIEWED_CONTRACT_SHA256,
                        help="digest of the reviewed contract; changing it needs a reviewer")
    args = parser.parse_args(argv)

    item = json.loads(args.item.read_text())
    try:
        findings = check_item(item, repo=args.repo, expect_head=args.expect_head,
                              expect_root=args.expect_root,
                              expect_contract_sha256=args.expect_contract_sha256)
    except CheckError as error:
        print(f"CANNOT CHECK: {error}")
        print("This is NOT a pass. Do not request approval.")
        return 2
    if findings:
        print(f"REFUSED: {len(findings)} finding(s). Do not request approval.")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print("Every staged field is what the committed tree produces.")
    print(f"  timeout_seconds  {item['timeout_seconds']}")
    print(f"  git_head         {item['git_head']}")
    print(f"  proposal_digest  {item['proposal_digest']}")
    print("\nThis is NOT an approval and NOT an authorization to run. The next step is a "
          "human at a TTY:")
    print(f"  campaignctl approve --id {CAMPAIGN_ID} --digest {item['proposal_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
