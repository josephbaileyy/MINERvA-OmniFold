# Runbook — staging `pm-root-inspection-20260908`

**Status: not executed.** This file is a plan and a checker. Nothing in it has been run.
Staging is a write to `refs/campaign/r5-20260902-0836139b/queue`, and approval is Joseph at a
TTY. Neither has happened.

**What this runbook is for.** `campaignctl stage` defaults `--timeout-seconds` to **600**
(`campaignctl.py:4540`) and accepts anything up to `maximum_cost.wall_hours * 3600` (`:2822`).
At 600 the launcher is `SIGKILL`ed mid-wait: no cancellation, no terminal verification, a
submitted job left running with nobody holding its identity. That number is not implied by the
contract and appears nowhere in the approval prompt, so it has to be caught by **inspecting
the staged item before a human is asked to approve anything** —
`nd-unfolding/pm_inspection/check_staged_item.py`.

**Staging is not a local operation.** `stage` runs inside `queue_operation`, which refreshes
against the pinned origin (`:2719`, `:2353`, `:2105`). Step 1 reaches the network and writes.

## Prerequisites, none of which this runbook satisfies

1. **An integrated checkout.** The launcher (`f2747e39`, review-cleared), the contract
   (`9f12c728`, limited PASS), the transport evidence and the authorization must all be landed,
   and the staging host's HEAD must be that landed head. `stage` records `git_head` and
   requires every bound file and the contract to be byte-identical to HEAD (`:2769`).
2. **The reviewed contract, identified by digest.** A **stale copy** rides on the launcher
   branch with a filesystem `output_namespace` and `--report`/`--out` literals in the
   validator argv. The reviewed one digests to
   `5351d9da730349ef59a3690d2b1367f026ee95fe74b40a53c08e41c15cf752d7`. Comparing the staged
   item to the *committed* contract only proves they agree; the checker therefore pins that
   digest, so editing the contract means changing a constant, which means passing a reviewer.
3. **The execution checkout re-pinned.** `--expect-root` must name the repository root
   campaignctl runs from, by absolute path, exactly once before the `--` (`validate_guarded_argv`).
   If `/pscratch/sd/j/josephrb/exec-20260907` is re-pinned, every occurrence changes together
   and the checker must be run with the same `--expect-root`.
4. **The guard.** Both halves route through `nd-unfolding/mnv_guarded_run.py`; `stage`
   enforces this for `kind=compute` on the producer argv and again on the validator argv
   (`:2779`, `:2799`).
5. **Joseph's TTY approval, which is last and which no message substitutes for.**

## Step 1 — stage (reaches the origin and writes to the campaign ref)

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py stage \
  --id pm-root-inspection-20260908 \
  --kind compute \
  --description 'Bounded attended read-only ROOT inspection for PM-1/PM-3/PM-4/PM-5' \
  --contract docs/orchestration/contracts/CONTRACT-20260908-pm-root-inspection.json \
  --bind nd-unfolding/pm_inspection/INPUT-BINDINGS-20260908.json \
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

**`--bind` is not optional and is not implied by `--bindings`.** `--bindings` is an argv
*value*; `command_bindings` binds the executable, the guard, the guarded target and the shim
files, plus whatever `--bind` names explicitly (`:2668`). Without it the input-bindings file
is not bound, and swapping it after staging would not make the item stale.

**`--description` is compared character-for-character** by the checker, because it is part of
the proposal payload the digest covers.

**`--timeout-seconds 1560` is the point of this runbook.** Every producer flag is written out
even where it equals a default: the digest a human approves covers the argv, so a flag left to
a default is a flag nobody approved.

**Where 1560 comes from.** `maximum_cost.wall_hours` (0.5) is 1800 s and `run_compute_item`
(`:4018-4019`, `:4038`) makes that ONE deadline shared by the producer and the terminal
validator. 1560 leaves the validator 240 s. The launcher takes 60 s of that for controller
start-up slack and runs on a 1500 s absolute budget, holding 180 s back for cancellation and
its verification. The constants live in `pm_root_inspect.py` and the checker imports them, so
this runbook cannot drift from the code.

## Step 2 — inspect what was actually staged, before asking anyone to approve

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py show \
  --id pm-root-inspection-20260908 > /tmp/staged-item.json

/usr/bin/python3.11 nd-unfolding/pm_inspection/check_staged_item.py \
  --item /tmp/staged-item.json \
  --repo . \
  --expect-head <the landed head that was reviewed> \
  --expect-root /pscratch/sd/j/josephrb/exec-20260907
```

The checker writes nothing, contacts no scheduler and reaches no network. It does **not**
compare the item against a list of things somebody thought to look at: it rebuilds the derived
fields from the committed tree with the controller's own helpers — `command_bindings`,
`merge_bindings`, `validate_campaign_contract`, `proposal_payload`, `digest` — loading the
`campaignctl` of the checkout under inspection, and requires the staged item to equal what
those produce, field for field. It then recomputes the proposal digest over the item's own
payload, so a forged digest fails even when every compared field matches, and asks the
controller whether every bound file is committed-and-identical.

Exit **0** is the only state in which approval may be requested, and it prints the `approve`
line with the digest so nobody retypes it. Exit **1** is a refusal. Exit **2** is CANNOT
CHECK — *not* a pass.

`--expect-head` is checked in addition to the checkout's actual HEAD; omitting it still
compares the item against the checkout it was staged from.

## Step 3 — approval, which is Joseph's and nobody else's

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py approve \
  --id pm-root-inspection-20260908 --digest <from step 2>
```

`approve` requires an interactive TTY (`:3540-3541`), prints the item, and requires the exact
approval phrase typed by hand. A peer relaying that Joseph approved is not approval. A digest
that does not match the staged proposal is refused (`:3537`).

## If the checker refuses

Revoke and re-stage. Do not approve an item intending to fix it afterwards: approval is what
admits it, and `run_compute_item` reads `timeout_seconds` off the item, not off this runbook.

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py revoke --id pm-root-inspection-20260908
```

## What is still true after all of this

A PASS says the staged item is what the committed tree produces and that the committed
contract is the reviewed one. It is not a scientific grade, not a discharge of
PM-1/PM-3/PM-4/PM-5, and not evidence about what G consumed historically. The reservation is
released only by a receipt listing the `metered_task_ids` the run recorded; an item that runs
and records no ids holds its reservation until an operator releases it under a committed
continuation decision.
