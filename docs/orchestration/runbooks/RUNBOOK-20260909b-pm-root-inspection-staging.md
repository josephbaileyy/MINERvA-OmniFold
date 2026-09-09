# Runbook — staging `pm-root-inspection-20260909b`

**Status: not executed.** This file is a plan and a checker. Nothing in it has been run.
Staging is a write to `refs/campaign/r5-20260902-0836139b/queue`, and approval is Joseph at a
TTY. Neither has happened.

Supersedes `RUNBOOK-20260908-pm-root-inspection-staging.md`, which is terminal and immutable
and is left exactly as it was. It carried two defects that this instance paid for, both fixed
below: it omitted the R5 receipt from its prerequisites, and its recovery advice was
impossible to follow.

## Why there is a third instance, and what killed the first two

- `pm-root-inspection-20260908` was **revoked**. Not for cause: the item was staged before the
  R5 receipt was committed, committing the receipt moved `HEAD`, and `validate_unchanged`
  refuses an item whose recorded `git_head` no longer matches. That is an ordering error and
  it cost a TTY approval.
- `pm-root-inspection-20260909` **ran and FAILED** — Slurm job 58106332, four seconds, exit
  2:0. The OI-136 guard refused to install because the propagated `sitecustomize` had already
  installed it, so `install()` found no bare `PathFinder`. The guard refused the run because
  its own propagation had worked. Fixed on `main` at 9dd282c4 and reproduced off-scheduler
  before and after.

**Both ids are unusable, for different reasons.** `revoke` writes a record keyed on the item
id and `state_of` reads it forever; a run that failed reports `failed` forever. Neither can
carry an item again, and the contract pins `campaign_id` to the id, so each instance costs a
new contract.

## Prerequisites

1. **An integrated checkout.** Everything landed, and the staging host's `HEAD` must BE that
   landed head. `stage` records `git_head` and requires every bound file and the contract to
   be byte-identical to `HEAD`.
2. **The reviewed contract, identified by digest.**
   `CONTRACT-20260909b-pm-root-inspection.json`, sha256
   `2d91f022d497506255078796782171ccbf28a95df83348e3bac79e53d7c22aac`. Its only difference
   from the 20260909 contract is `campaign_id` — verified by diff as one line removed and one
   added. Editing the contract must change `REVIEWED_CONTRACT_SHA256` in the checker, which
   means passing a reviewer.
3. **The execution checkout re-pinned** to the landed head. `--expect-root` names the
   repository root campaignctl runs from, by absolute path, exactly once before the `--`.
4. **The guard**, both halves routed through `nd-unfolding/mnv_guarded_run.py`.
5. **A COMMITTED R5 METER RECEIPT, MEASURED AFTER THE PREVIOUS ITEM'S OUTCOME, AND COMMITTED
   BEFORE STAGING.** This is the prerequisite the 20260908 runbook omitted and it is what
   burned that id. Two separate requirements hide here:
   - A compute item is admitted against the receipt's headroom, so a missing, stale or
     malformed receipt is a stop.
   - An item that RAN keeps reserving its full `maximum_cost` until a committed receipt lists
     every scheduler task id it recorded in `spend.metered_task_ids`. The receipt at the head
     this runbook is written against lists `['57712764', '58106332']`, so 58106332's
     reservation is released by it.
   **ORDER IS THE WHOLE POINT: commit the receipt, and everything else, BEFORE `stage`.** Any
   commit after staging moves `HEAD` and makes the item stale, and the only exit from stale is
   revoke, which is a one-way door.
6. **The guard inventory directory must exist.** `/pscratch/sd/j/josephrb/pm-inspection-20260909b/`
   `write_inventory` opens its file with `open(dest, "a")` and does NOT create directories, and
   the path must be writable from a COMPUTE node, not just from the login node.

   ```
   mkdir -p /pscratch/sd/j/josephrb/pm-inspection-20260909b
   ```
7. **Joseph's TTY approval, which is last and which no message substitutes for.**

## What changed in the staged argv, and why

`--inventory /pscratch/sd/j/josephrb/pm-inspection-20260909b/guard-inventory.jsonl` is new.

MEASURED on 2026-09-09: as the campaign stood, it captured **zero** structured guard records.
`_arm_child_environment` does `setdefault(INVENTORY_ENV, "")`, that empty string reaches the
batch job through `sbatch --export=ALL`, and the child shim reads it as `None` at startup. Only
the human-readable `[oi136-inv]` stderr block survived, so a refused arm left nothing
structured to cite. Passing `--inventory` to the OUTER producer fixes both levels, because
`main()` sets `INVENTORY_ENV` before `install()` and the batch job inherits the real path:

    no flag (as it stood)     0 records
    outer --inventory         3 records, including the inner job at depth=1 with its label

**Known residual, not fixed here.** If the inner job refuses an import, it exits through
`os._exit(3)` inside `find_spec`, `main()`'s `finally` never runs, and the shim's `atexit` hook
writes using the path it captured at startup — so the record lands but its `--label` is empty.
Repairing that means editing `mnv_guard_shim/sitecustomize.py`, which is digest-bound and is
the propagation path itself. Enforcement is unaffected: the refusal is correct, loud, exit 3.

## Step 1 — stage (reaches the origin and writes to the campaign ref)

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py stage \
  --id pm-root-inspection-20260909b \
  --kind compute \
  --description 'Bounded attended read-only ROOT inspection for PM-1/PM-3/PM-4/PM-5' \
  --contract docs/orchestration/contracts/CONTRACT-20260909b-pm-root-inspection.json \
  --bind nd-unfolding/pm_inspection/INPUT-BINDINGS-20260908.json \
  --timeout-seconds 1560 \
  -- \
  /usr/bin/python3.11 nd-unfolding/mnv_guarded_run.py \
    --expect-root /pscratch/sd/j/josephrb/exec-20260907 \
    --label pm-root-inspection-launch \
    --inventory /pscratch/sd/j/josephrb/pm-inspection-20260909b/guard-inventory.jsonl \
    -- nd-unfolding/pm_inspection/pm_root_inspect.py \
      --mode launch \
      --bindings nd-unfolding/pm_inspection/INPUT-BINDINGS-20260908.json \
      --data-root /pscratch/sd/j/josephrb/MINERvA-OmniFold \
      --inner-python /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python \
      --expect-root /pscratch/sd/j/josephrb/exec-20260907 \
      --account m3246 \
      --qos debug \
      --minutes 15 \
      --comment pm-root-inspection-20260909b
```

**`--bind` is not optional and is not implied by `--bindings`.** `--bindings` is an argv
*value*; without `--bind` the input-bindings file is not bound, and swapping it after staging
would not make the item stale.

**`--description` is compared character-for-character** by the checker, because it is part of
the proposal payload the digest covers.

**`--timeout-seconds 1560`.** `maximum_cost.wall_hours` (0.5) is 1800 s, and that is ONE
deadline shared by the producer and the terminal validator; 1560 leaves the validator 240 s.
The constants live in `pm_root_inspect.py` and the checker imports them, so this runbook cannot
drift from the code. At the 600 s default the launcher would be `SIGKILL`ed mid-wait: no
cancellation, no terminal verification, a submitted job left running with nobody holding its
identity.

## Step 2 — inspect what was actually staged, before asking anyone to approve

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py show \
  --id pm-root-inspection-20260909b > /tmp/staged-item.json

/usr/bin/python3.11 nd-unfolding/pm_inspection/check_staged_item.py \
  --item /tmp/staged-item.json \
  --repo . \
  --expect-head <the landed head that was reviewed> \
  --expect-root /pscratch/sd/j/josephrb/exec-20260907
```

The checker writes nothing, contacts no scheduler and reaches no network. It rebuilds the
derived fields from the committed tree with the controller's own helpers and requires the
staged item to equal what those produce, field for field, then recomputes the proposal digest
over the item's own payload so a forged digest fails even when every compared field matches.

Exit **0** is the only state in which approval may be requested, and it prints the `approve`
line with the digest so nobody retypes it. Exit **1** is a refusal. Exit **2** is CANNOT CHECK
— *not* a pass.

## Step 3 — approval, which is Joseph's and nobody else's

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py approve \
  --id pm-root-inspection-20260909b --digest <from step 2>
```

`approve` requires an interactive TTY, prints the item, and requires the exact approval phrase
typed by hand. A peer relaying that Joseph approved is not approval.

## If the checker refuses

**DO NOT REVOKE.** The 20260908 runbook said "revoke and re-stage" and that advice is
impossible to follow: `revoke` writes a record keyed on the item id, `state_of` reads it
forever, and `stage` has no `--force` or `--replace`. A revoked id can never carry an item
again, and because the contract pins `campaign_id`, recovering costs a new contract, a new
checker constant, a new commit and another TTY approval. That is exactly how 20260908 died.

Fix the tree instead, commit, and stage a NEW id. Only revoke when the item must be positively
withdrawn and you have already accepted that its id is spent. And do not approve an item
intending to fix it afterwards: approval is what admits it, and `run_compute_item` reads
`timeout_seconds` off the item, not off this runbook.

## What is still true after all of this

A PASS says the staged item is what the committed tree produces and that the committed contract
is the reviewed one. It is not a scientific grade, not a discharge of PM-1/PM-3/PM-4/PM-5, and
not evidence about what G consumed historically. The reservation is released only by a receipt
listing the `metered_task_ids` the run recorded; an item that runs and records no ids holds its
reservation until an operator releases it under a committed continuation decision.
