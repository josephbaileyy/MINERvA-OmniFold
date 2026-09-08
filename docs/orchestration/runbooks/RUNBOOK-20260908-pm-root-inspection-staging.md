# Runbook — staging `pm-root-inspection-20260908`

**Status: not executed.** This file is a plan and a checker. Nothing in it has been run.
Staging is the first write to `refs/campaign/r5-20260902-0836139b/queue`, and approval is
Joseph at a TTY. Neither has happened.

**What this runbook is for.** `campaignctl stage` defaults `--timeout-seconds` to **600**
(`campaignctl.py:4540`) and accepts anything up to `maximum_cost.wall_hours * 3600`
(`:2822`). At 600 the launcher is `SIGKILL`ed mid-wait: no cancellation, no terminal
verification, a submitted job left running with nobody holding its identity. That number is
not implied by the contract and appears nowhere in the approval prompt, so it has to be
caught by **inspecting the staged item before a human is asked to approve it**. That is a
mechanical check, so `nd-unfolding/pm_inspection/check_staged_item.py` performs it and this
runbook makes it a required step rather than a habit.

## Prerequisites, none of which this runbook satisfies

1. **An integrated checkout.** The launcher (`f2747e39`, review-cleared), the contract
   (`9f12c728`), the transport evidence and the authorization must all be landed and the
   staging host's HEAD must be that landed head. `stage` records `git_head` and requires
   every bound file and the contract to be byte-identical to HEAD (`:2769`), so a dirty tree
   or a stale branch refuses on its own.
2. **The right contract.** A **stale copy** of `CONTRACT-20260908-pm-root-inspection.json`
   rides on the launcher branch with a filesystem `output_namespace` and `--report`/`--out`
   literals in the validator argv. The reviewed one is `9f12c728`'s:
   `output_namespace: "queue-claim-run-directory"`, validator in `--campaign-mode required`.
   The checker refuses the stale one by name.
3. **The execution checkout re-pinned.** `--expect-root` must be the checkout the guard is
   pinned to. If `/pscratch/sd/j/josephrb/exec-20260907` is re-pinned to the landed head, the
   path in the argv and in `--expect-root` must be the re-pinned one, and the checker must be
   run with the same `--expect-root` it was staged with.
4. **The guard.** Both halves route through `nd-unfolding/mnv_guarded_run.py`; `stage`
   enforces this for `kind=compute` on the producer argv and again on the validator argv
   (`:2779`, `:2799`).
5. **Joseph's TTY approval, which is last and which no message substitutes for.**

## Step 1 — stage (a write to the campaign ref; do not run it early)

Run from the repo root of the integrated checkout:

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py stage \
  --id pm-root-inspection-20260908 \
  --kind compute \
  --description 'Bounded attended read-only ROOT inspection for PM-1/PM-3/PM-4/PM-5' \
  --contract docs/orchestration/contracts/CONTRACT-20260908-pm-root-inspection.json \
  --timeout-seconds 1560 \
  -- \
  /usr/bin/python3.11 nd-unfolding/mnv_guarded_run.py \
    --expect-root /pscratch/sd/j/josephrb/exec-20260907 \
    --label pm-root-inspection-launch \
    -- nd-unfolding/pm_inspection/pm_root_inspect.py \
      --mode launch \
      --bindings nd-unfolding/pm_inspection/INPUT-BINDINGS-20260908.json \
      --data-root /pscratch/sd/j/josephrb/MINERvA-OmniFold \
      --inner-python /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python \
      --expect-root /pscratch/sd/j/josephrb/exec-20260907 \
      --account m3246 \
      --qos debug \
      --minutes 15 \
      --comment pm-root-inspection-20260908
```

`--timeout-seconds 1560` is the whole point of this runbook. Every producer flag is written
out even where it equals a default, because the digest a human approves covers the argv: a
flag left to a default is a flag nobody approved.

**Where 1560 comes from.** The contract's `maximum_cost.wall_hours` (0.5) is 1800 s, and
`run_compute_item` (`:4018-4019`, `:4038`) makes that ONE deadline shared by the producer and
the terminal validator. 1560 leaves the validator 240 s. The launcher then takes 60 s of that
for controller start-up slack and runs on a 1500 s absolute budget, of which it holds 180 s
back for cancellation and its verification. The constants live in `pm_root_inspect.py`; the
checker imports them, so this runbook cannot drift from the code.

## Step 2 — inspect what was actually staged, before asking anyone to approve

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py show \
  --id pm-root-inspection-20260908 > /tmp/staged-item.json

/usr/bin/python3.11 nd-unfolding/pm_inspection/check_staged_item.py \
  --item /tmp/staged-item.json \
  --expect-head <the landed head that was reviewed> \
  --expect-root /pscratch/sd/j/josephrb/exec-20260907
```

The checker writes nothing, contacts no scheduler and touches no queue. It refuses on: a
`timeout_seconds` that is not 1560 (600 by name), a staged timeout that would leave the
validator nothing, a `wall_hours` smaller than the budget was sized against, the stale
contract, a validator not in `--campaign-mode required`, `--report`/`--out` literals, an argv
that is not the reviewed argv character-for-character, a `git_head` that is not the reviewed
head, and a missing digest. **Exit 0 is the only state in which approval may be requested**,
and it prints the `approve` line with the digest so nobody retypes it.

Omitting `--expect-head` checks nothing about HEAD. A PASS without it is not a statement that
the staged item was built from the reviewed tree.

## Step 3 — approval, which is Joseph's and nobody else's

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py approve \
  --id pm-root-inspection-20260908 --digest <from step 2>
```

`approve` requires an interactive TTY (`:3540-3541`), prints the item, and requires the exact
approval phrase typed by hand. A peer relaying that Joseph approved is not approval. The
digest must be the one step 2 printed; a mismatch is refused (`:3537`).

## If the checker refuses

Revoke and re-stage. Do not approve an item to fix it afterwards: approval is what admits it,
and `run_compute_item` reads `timeout_seconds` off the item, not off this runbook.

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py revoke --id pm-root-inspection-20260908
```

## What is still true after all of this

A PASS from the checker says the staged values match what was reviewed. It is not a
scientific grade, not a discharge of PM-1/PM-3/PM-4/PM-5, and not evidence about what G
consumed historically. The reservation is released only by a receipt listing the
`metered_task_ids` the run recorded; an item that runs and records no ids holds its
reservation until an operator releases it under a committed continuation decision.
