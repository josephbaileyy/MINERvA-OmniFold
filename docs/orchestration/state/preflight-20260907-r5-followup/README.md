# R5 preserved accounting snapshot — 2026-09-07

**⚠ THIS IS NOT THE OPERATIONAL ADMISSION RECEIPT AND MUST NOT BE MOVED TO ONE.**
`r5-snapshot-receipt-20260907.json` is deliberately **not** at
`docs/orchestration/state/r5-meter-receipt.json`. Committing a valid receipt to that path arms
compute admission queue-wide. Evidence capture does not authorize it — the decision owner said so
explicitly when ordering this snapshot.

## What this is

Obligation A of `FOLLOWUP-20260906-r5-sacct-window-and-post-stop-accounting.md`, performed **early**
as insurance, on the decision owner's instruction of 2026-09-07.

Captured with the record's own §4 command, on Perlmutter `login13`, and metered with the **landed
repaired meter** — `docs/orchestration/r5_meter.py` at `origin/main`, sha256
`383eec6695ef15a9b30aa7779615de29bda3976ad3dede1e0566a811fd6f0f8e`, byte-verified against the
committed source before execution and run from an isolated scratch directory. **The canonical cluster
checkout was not modified and does not carry the repair.**

| file | sha256 |
|---|---|
| `r5-window-preserved.psv` | `31c74b422aa1889e351042e93ab567035b5907bd0279362e3666fb6dbc246e86` |
| `r5-snapshot-receipt-20260907.json` | `ed86508e35b0f1dc0999cf95a3a6d1199682d8309bfc9475500039a876369b9b` |

## The measurement

Schema **2**. Measured `2026-09-07T01:54:09Z`.

| quantity | value |
|---|---:|
| GPU task-hours | `0.0` |
| **CPU task-hours** | **`13.064722222222223`** |
| distinct task ids | `1` |
| **execution attempts** | **`1155`** |
| GPU headroom | `500.0` |
| CPU headroom | `486.9352777777778` |
| `fired` | `date:false gpu:false cpu:false any:false` |

States: `1153 REQUEUED`, `2 NODE_FAIL`. All 1,155 attempts belong to one job id.

**This is the first R5 measurement taken with the repaired meter.** The superseded v1 meter reported
`0.0016667` CPU task-hours for the same subject, because it collapsed a requeued job's attempts to
one. The gap is the defect, not a change in what ran.

## §4.3 — outstanding JobIDs

**`57712764`** — the `cron`-partition waker, still `PENDING` at capture time, `Restarts` past 2100.
It is the sole non-terminal id and therefore the sole input to Obligation B.

**Zero rows carry `End=Unknown`** in this capture, so the §5 concatenation trap does **not** apply to
*this* file: there is no superseded `RUNNING` observation to remove. It will apply to any future
capture taken while an attempt is in flight.

## ⚠ This snapshot does NOT discharge Obligation A

It is an early preservation, not the final one. The R5 window runs to `2026-09-30T00:00:00Z` and
`57712764` keeps accruing attempts at roughly `0.65`–`0.69` CPU task-hours/day. **A final capture is
still required before `2026-10-02T13:44:27Z`**, and this file is insurance against losing the ability
to take it, not a substitute.

The follow-up record stays **OPEN**.
