#!/usr/bin/env python3
"""Read-only check of a STAGED campaign item, to be run before approval is requested.

WHY THIS EXISTS.  ``campaignctl stage`` defaults ``--timeout-seconds`` to 600
(campaignctl.py:4540) and accepts any value up to ``maximum_cost.wall_hours * 3600``.  At 600
the launcher is SIGKILLed mid-wait, which is exactly the failure the launcher's absolute budget
was built to make impossible -- and nothing in the contract, the queue, or the approval prompt
would say so.  The wrong number has to be caught by INSPECTING THE STAGED ITEM, before a human
is asked to approve anything.  That is a mechanical check, so it is one.

WHAT IT IS NOT.  It writes nothing, contacts no scheduler, touches no queue, and reads no
remote.  It is not an authorization, it does not approve, and a PASS here is not a statement
that the item should run -- only that what is staged is what was reviewed.

USE:
    campaignctl ... show --id pm-root-inspection-20260908 > staged-item.json
    check_staged_item.py --item staged-item.json --expect-head <reviewed integrated HEAD>

Exit 0 only when every check passes; the approve line is printed only then.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pm_root_inspect as producer  # noqa: E402

CAMPAIGN_ID = "pm-root-inspection-20260908"
CONTRACT_PATH = "docs/orchestration/contracts/CONTRACT-20260908-pm-root-inspection.json"
BINDINGS_PATH = "nd-unfolding/pm_inspection/INPUT-BINDINGS-20260908.json"
DATA_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
INNER_PYTHON = "/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python"
OUTER_PYTHON = "/usr/bin/python3.11"
DEFAULT_EXPECT_ROOT = "/pscratch/sd/j/josephrb/exec-20260907"


def expected_argv(expect_root: str) -> list[str]:
    """The producer argv this campaign is allowed to stage, spelled out in full.

    Every value is a literal because the digest a human approves covers the argv: a flag left
    to a default is a flag nobody approved.  ``--minutes`` comes from the launcher itself so
    the two cannot drift apart silently.
    """
    return [
        OUTER_PYTHON,
        "nd-unfolding/mnv_guarded_run.py",
        "--expect-root", expect_root,
        "--label", "pm-root-inspection-launch",
        "--",
        "nd-unfolding/pm_inspection/pm_root_inspect.py",
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


def check_item(item: dict, *, expect_head: str | None = None,
               expect_root: str = DEFAULT_EXPECT_ROOT) -> list[str]:
    """Return the list of findings. Empty means every check passed."""
    bad: list[str] = []

    def want(condition: bool, finding: str) -> None:
        if not condition:
            bad.append(finding)

    want(item.get("id") == CAMPAIGN_ID,
         f"item id is {item.get('id')!r}, not {CAMPAIGN_ID!r}")
    want(item.get("kind") == "compute",
         f"kind is {item.get('kind')!r}; this item must be staged as compute")

    # -- the finding this file exists for -------------------------------------------------
    staged = item.get("timeout_seconds")
    want(staged == int(producer.STAGED_TIMEOUT_SECONDS),
         f"timeout_seconds is {staged!r}, not {int(producer.STAGED_TIMEOUT_SECONDS)}. "
         "campaignctl defaults this to 600, at which the launcher is killed mid-wait "
         "and its cleanup never runs. Re-stage; do NOT approve this item.")

    contract = item.get("campaign_contract")
    if not isinstance(contract, dict):
        bad.append("item carries no campaign_contract; a compute item must")
        return bad

    cost = contract.get("maximum_cost")
    if not isinstance(cost, dict):
        bad.append("contract carries no maximum_cost")
    else:
        wall = float(cost.get("wall_hours", 0)) * 3600
        want(wall == producer.CONTROLLER_WALL_SECONDS,
             f"maximum_cost.wall_hours gives {wall:g}s, not "
             f"{producer.CONTROLLER_WALL_SECONDS:g}s; the launcher's budget was sized "
             "against the larger number")
        if isinstance(staged, int):
            want(staged + producer.VALIDATOR_RESERVE_SECONDS <= wall,
                 f"staged {staged}s plus the validator's "
                 f"{producer.VALIDATOR_RESERVE_SECONDS:g}s reserve exceeds the {wall:g}s "
                 "the producer and validator share; the validator would not be started")
        want(float(cost.get("gpu_task_hours", -1)) == 0.0,
             f"gpu_task_hours is {cost.get('gpu_task_hours')!r}, not 0.0")

    # A stale copy of this contract exists on the launcher branch with a filesystem
    # output_namespace and --report/--out literals. Staging that one would put the report
    # where the validator does not look.
    want(contract.get("output_namespace") == "queue-claim-run-directory",
         f"output_namespace is {contract.get('output_namespace')!r}; the claim-derived "
         "contract is the one that was reviewed")
    accounting = contract.get("accounting")
    want(isinstance(accounting, dict) and accounting.get("expects_scheduler_tasks") is True,
         "accounting.expects_scheduler_tasks is not true; the launcher records job ids and "
         "the reservation is released against them")

    validator = contract.get("terminal_validator")
    if not isinstance(validator, dict):
        bad.append("contract carries no terminal_validator")
    else:
        vargv = list(validator.get("argv") or [])
        want("--campaign-mode" in vargv and "required" in vargv,
             "terminal_validator.argv does not carry --campaign-mode required")
        want("--report" not in vargv and "--out" not in vargv,
             "terminal_validator.argv carries --report/--out literals; the reviewed "
             "validator derives both from the queue claim")
        want("nd-unfolding/mnv_guarded_run.py" in vargv,
             "terminal_validator.argv is not routed through the guard")

    want(item.get("campaign_contract_path") == CONTRACT_PATH,
         f"campaign_contract_path is {item.get('campaign_contract_path')!r}, "
         f"not {CONTRACT_PATH!r}")

    argv = list(item.get("argv") or [])
    wanted = expected_argv(expect_root)
    if argv != wanted:
        bad.append("staged argv is not the reviewed argv.\n"
                   f"  staged:   {json.dumps(argv)}\n"
                   f"  reviewed: {json.dumps(wanted)}")

    bindings = item.get("bindings")
    want(isinstance(bindings, list) and bindings,
         "item records no bindings; a compute item binds its committed inputs")

    if expect_head is not None:
        want(item.get("git_head") == expect_head,
             f"git_head is {item.get('git_head')!r}, not the reviewed "
             f"{expect_head!r}")

    want(bool(item.get("proposal_digest")),
         "item carries no proposal_digest, so there is nothing to approve against")
    return bad


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--item", type=Path, required=True,
                        help="JSON from `campaignctl show --id ...`")
    parser.add_argument("--expect-head",
                        help="the integrated HEAD that was reviewed; checked when given")
    parser.add_argument("--expect-root", default=DEFAULT_EXPECT_ROOT,
                        help="the execution checkout the guard is pinned to")
    args = parser.parse_args(argv)

    item = json.loads(args.item.read_text())
    findings = check_item(item, expect_head=args.expect_head,
                          expect_root=args.expect_root)
    if findings:
        print(f"REFUSED: {len(findings)} finding(s). Do not request approval.")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print("Every staged value matches what was reviewed.")
    print(f"  timeout_seconds  {item['timeout_seconds']}")
    print(f"  git_head         {item['git_head']}")
    print(f"  proposal_digest  {item['proposal_digest']}")
    print("\nThis is NOT an approval and NOT an authorization to run. The next step is a "
          "human at a TTY:")
    print(f"  campaignctl approve --id {CAMPAIGN_ID} --digest {item['proposal_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
