# Runbook — staging `pm-root-inspection-20260909c`

**Status: not executed.** A plan and a checker. Staging writes to
`refs/campaign/r5-20260902-0836139b/queue`; approval is Joseph at a TTY. Neither has happened.

Supersedes `RUNBOOK-20260909b-pm-root-inspection-staging.md`, which is terminal and immutable
and is left byte-identical. **Everything in the predecessor still applies** — its prerequisites,
its `--timeout-seconds 1560` derivation, its "DO NOT REVOKE" section — and is not repeated
here. This file records only what is different for the fourth instance.

## Three ids are spent, for three unrelated reasons

| id | outcome | cause |
|---|---|---|
| `20260908` | revoked | staged before the R5 receipt was committed; committing it moved `HEAD`, the item went stale, and the only exit was revoke |
| `20260909` | failed | the OI-136 guard refused to install over its own propagation — it refused the run **because** propagation had worked |
| `20260909b` | failed | ROOT's cling shells out to `x86_64-conda-linux-gnu-c++` to find its include paths; that binary was not on `PATH`, so cling built an empty modulemap overlay and segfaulted |

All three are fixed on `main`. The third was present from the very first attempt — the earlier
two failures simply never reached `import ROOT`.

## What is different here

**The contract.** `CONTRACT-20260909c-pm-root-inspection.json`, sha256
`ea2d24c28733cce33a3de8cd26fadc8b1fab4f127f22b8d2d29c13315f4331cf`. One line differs from its
predecessor: `campaign_id`. The contract TEXT has not been edited since the 20260908 review;
only the id it pins has moved, three times.

**The inventory directory** is `/pscratch/sd/j/josephrb/pm-inspection-20260909c/` and must
exist before staging, for the reason the predecessor gives:

```
mkdir -p /pscratch/sd/j/josephrb/pm-inspection-20260909c
```

**The R5 receipt** is re-measured and lists `['57712764', '58106332', '58123269', '58124310']`.
Listing `58123269` is what releases the 0.5 task-hour reservation `20260909b` still held.
Commit it, and everything else, BEFORE `stage` — that ordering is what killed `20260908`.

**No producer change is needed beyond what is already landed.** `pm_root_inspect.launch()` now
puts the inner interpreter's own `bin/` on `PATH` before submitting, and `submit_one_job`
passes `--export=ALL`, so the batch job inherits it.

## What was proved off-scheduler before asking for approval

This is the part the three failed instances did not have. None of it is a measurement; all of
it ran outside the queue, under no contract.

| check | where | result |
|---|---|---|
| guard installs under propagation | login node, both interpreters | as-deployed RC 2, patched RC 0 |
| whole guarded READ path, real data root | login node | `exit_code 0, records 184, missing_read_records 0`, ~2 min |
| `import ROOT` with the conda bin absent | login node, no guard | segfault 139 |
| `import ROOT` with it present | login node, under the guard | `ROOT OK 6.28/12` |
| PATH survives `--export=ALL` onto a **compute node** | job 58124310, `debug`, 22 s | conda bin at index 2, compiler resolvable, `ROOT OK 6.28/12`, `TFile.Open` True |
| guard interception still first on the compute node | job 58124310 | `PATH[0]` = `mnv_guard_shim/bin` |

**Still not proved as a single unit:** the read half running on a compute node *through the
queue*. Every constituent link is measured; their composition is not. That is the residual risk
this instance carries, and it should be stated plainly rather than implied away.

## Steps

Identical to the predecessor with the id, contract and inventory path substituted:

```
/usr/bin/python3.11 docs/orchestration/campaignctl.py stage \
  --id pm-root-inspection-20260909c \
  --kind compute \
  --description 'Bounded attended read-only ROOT inspection for PM-1/PM-3/PM-4/PM-5' \
  --contract docs/orchestration/contracts/CONTRACT-20260909c-pm-root-inspection.json \
  --bind nd-unfolding/pm_inspection/INPUT-BINDINGS-20260908.json \
  --timeout-seconds 1560 \
  -- \
  /usr/bin/python3.11 nd-unfolding/mnv_guarded_run.py \
    --expect-root /pscratch/sd/j/josephrb/exec-20260907 \
    --label pm-root-inspection-launch \
    --inventory /pscratch/sd/j/josephrb/pm-inspection-20260909c/guard-inventory.jsonl \
    -- nd-unfolding/pm_inspection/pm_root_inspect.py \
      --mode launch \
      --bindings nd-unfolding/pm_inspection/INPUT-BINDINGS-20260908.json \
      --data-root /pscratch/sd/j/josephrb/MINERvA-OmniFold \
      --inner-python /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python \
      --expect-root /pscratch/sd/j/josephrb/exec-20260907 \
      --account m3246 \
      --qos debug \
      --minutes 15 \
      --comment pm-root-inspection-20260909c
```

Then `show --id pm-root-inspection-20260909c > /tmp/staged-item.json`, run
`check_staged_item.py` with `--expect-head` set to the landed head, and only on exit **0** ask
for approval.

## What a PASS still is not

A PASS says the staged item is what the committed tree produces. It is not a scientific grade,
not a discharge of PM-1/PM-3/PM-4/PM-5, and not evidence about what G consumed historically.
