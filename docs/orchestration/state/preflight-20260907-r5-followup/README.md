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

## Independent re-derivation, and a third whole-day cadence measurement

Both checks below run `awk` over the committed PSV, not `r5_meter.py`, so the receipt and the check
do not share code.

**1. The receipt is re-derivable from the preserved bytes.** Summing field 4 (`ElapsedRaw`) across
all 1,155 rows gives 47,033 s = `13.064722222` CPU task-hours, reproducing the receipt's
`13.064722222222223`. The file has a single field count (8), one distinct job id, **zero** duplicate
`(JobID, Start)` pairs, and **zero** `End=Unknown` rows — so no attempt is observed twice and none is
metered in flight.

**2. Per calendar day**, attributing each attempt to the day of its `Start`:

| day | ticks (of 288) | charged | s/attempt | character |
|---|---:|---:|---:|---|
| 2026-09-02 | 99 | 0.728889 h | 26.505 | partial — t0 is 13:44:27Z — and holds a 453 s startup attempt |
| 2026-09-03 | 180 | 10.263611 h | 205.272 | **outlier**: one 31,063 s hang |
| 2026-09-04 | 277 | 0.652778 h | 8.484 | 11 ticks lost to the hang's recovery |
| **2026-09-05** | **288** | **0.690556 h** | 8.632 | clean |
| **2026-09-06** | **288** | **0.672222 h** | 8.403 | clean |
| 2026-09-07 | 23 | 0.056667 h | 8.870 | partial — capture at 01:54:09Z |

The 09-03, 09-04 and 09-05 rows reproduce the cadence table in §3 of
`FINDING-20260906-r5-meter-undercounted-requeue-attempts.md` **exactly**, from a different capture
taken a day later. **2026-09-06 is a full day the earlier fixture did not cover**, and it is a third
independent whole-day measurement landing in the same band — against the first-published figure of
0.05–0.07 h/day, which was wrong by an order of magnitude and is the figure that reached the decision
owner first.

**Two refinements to the band.** Only 2026-09-05 and 2026-09-06 are simultaneously complete
(288/288 ticks), outlier-free (longest attempt 15 s and 14 s), and free of any midnight-straddling
attempt. The defensible ordinary cadence is therefore **0.67–0.69 CPU task-hours/day**, not
0.65–0.69. And 2026-09-04 is not quite "a full ordinary day": it lost 11 ticks, and under the
Start-day convention it is credited none of the 3,183 s (`0.884167 h`) of the 09-03 hang that
physically elapsed after midnight on 09-04. **Exactly one** attempt in the capture straddles midnight
(`2026-09-03T16:15:20 → 2026-09-04T00:53:03`), so the convention moves that one day and nothing else.

The quantity that is actually stable is the **per-tick cost, 8.40–8.87 s**, which is immune to missed
ticks. At the configured 5-minute cadence — 288 ticks/day — that is ≈0.67–0.71 CPU task-hours/day.

**A projection, not a measurement.** At 0.67–0.69 h/day the 22.92 days remaining from this snapshot
to the stop add ≈15.4–15.8 h, putting the campaign near **28–29 CPU task-hours against a 500-hour
ceiling**, absent further hangs. A single hang like 09-03's adds ~10 h by itself. Nothing here is a
measurement of spend that has not yet happened.

## ⚠ This snapshot does NOT discharge Obligation A

It is an early preservation, not the final one. The R5 window runs to `2026-09-30T00:00:00Z` and
`57712764` keeps accruing attempts at `0.67`–`0.69` CPU task-hours/day (see above). **A final capture is
still required before `2026-10-02T13:44:27Z`**, and this file is insurance against losing the ability
to take it, not a substitute.

The follow-up record stays **OPEN**.
