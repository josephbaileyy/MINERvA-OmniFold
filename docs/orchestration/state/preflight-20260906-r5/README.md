# R5 preflight evidence — 2026-09-06

**⚠ THE RECEIPTS IN THIS DIRECTORY ARE INCOMPLETE AND ARE NOT ADMISSION EVIDENCE.**

They are deliberately **not** at `docs/orchestration/state/r5-meter-receipt.json`. That path is the
input to `campaignctl`'s compute-admission gate (`campaignctl.py:271`, `:3080-3111`, `:3338-3342`).
Placing these bytes there would arm admission. Joseph ruled on 2026-09-06:

> *"Label the existing R5 receipt explicitly as incomplete because it omits requeue expenditure; do
> not present it as valid admission evidence."*

So they are committed here, under a name that carries the label, for evidence and audit only.

## Why they are incomplete

Both receipts report **`0.0016666…` CPU task-hours** against the 500/500 ceilings. That is what the
landed meter measures, and the measurement is honest for what it queried. It is **not** the R5
window's actual expenditure.

`r5_meter._sacct_argv()` (`r5_meter.py:380-392`) omits `--duplicates`, so `sacct` returns only the
most recent instance of a requeued job id. The only in-window task, `57712764`, is a self-requeueing
`cron` waker with `Restarts=1990`. Queried **with** `--duplicates` over the identical window:

| reading | instances | elapsed | CPU task-hours |
|---|---:|---:|---:|
| what these receipts record | 1 | 6 s | `0.0016667` |
| what actually ran post-t0 | **953** | 45,325 s | **`12.5903`** |

`--duplicates` is not a drop-in repair: fed that capture the landed meter *fails* with
`conflicting rows for task identity 57712764`, because `_parse_sacct_dump` keys on job id alone and
keeps the maximum elapsed rather than summing attempts.

**Whether 953 requeue attempts are 953 charges or one is a specification question, not an
implementation one**, and it is unresolved. The meter's `UNIT` says "over distinct task identities";
R5 §3 says failed and retried tasks count in full. Under the implementation the answer is `0.0016667`;
under a plain reading of §3 it is `12.5903`. **Nothing here adjudicates it.** The repair is owned by
the integration lane; the ruling is Joseph's.

## Receipt bytes are unaltered

Neither receipt has been edited. They are byte-for-byte as `r5_meter.py measure` emitted them, and
their digests below are the digests of the meter's own output. The INCOMPLETE label lives in the
filename, this README and the authorization record — **never inside the measurement**. Editing a
measurement to carry a caveat would destroy the thing that makes it evidence.

## Contents

| file | what it is |
|---|---|
| `r5-meter-receipt-INCOMPLETE-live.json` | receipt from a live `sacct` query, `login31`, `2026-09-06T08:54:17.695700Z` |
| `r5-meter-receipt-INCOMPLETE-fromfile.json` | same measurement re-derived from the preserved raw dump |
| `sacct-r5-t0-to-now.psv` | the raw dump both receipts parse; its sha256 is the `source.raw_sha256` the live receipt recorded independently |
| `sacct-waker-duplicates-8field.psv` | the `--duplicates` capture, 953 rows, that the landed meter cannot parse |
| `sacct-hist-alloc-20260701-to-20260906.psv` | 3,994 allocation-level rows, chunked in ≤30-day windows (NERSC rejects wider queries) |
| `sacct-r5-window-ALL-duplicates-8field.psv` | the R5 window with `--duplicates` over **all jobs** (no `-j` scoping) — the form `_sacct_argv()` actually issues. 958 attempts, one distinct job id, **`12.606389` CPU / `0.0` GPU task-hours** at `2026-09-06T09:20Z` |
| `sacct-arrays-duplicates-8field.psv` | `-X -D` over three windows spanning 2026-07-10→2026-09-01, 5,942 rows. Establishes a NEGATIVE result: **zero requeued array tasks** in retained accounting |
| `R5-PREFLIGHT-EVIDENCE.md` | the full preflight report |
| `DIGESTS.txt` | sha256 of every file above |

## A total belongs to a capture, not to the campaign

`12.5903` and `12.606389` are not two versions of one number and neither is "the R5 CPU spend". Each
is the spend measurable in a specific capture at a specific instant: `12.590278` at
`2026-09-06T08:59Z` over 953 attempts, `12.606389` at `2026-09-06T09:20Z` over 958.
**Attribute any total to a pinned capture and its digest; never re-query to reproduce one.**

**⚠ CORRECTED: the cadence figure in an earlier revision of this file was wrong by an order of
magnitude.** It said ~`0.05`–`0.07` CPU task-hours/day. Re-derived per calendar day from
`sacct-r5-window-ALL-duplicates-8field.psv`:

| day | CPU task-hours | note |
|---|---:|---|
| 2026-09-02 | `0.728889` | partial — from t0 at 13:44:27Z |
| 2026-09-03 | **`10.263611`** | **the 31,063 s hang — an outlier, not a rate** |
| 2026-09-04 | `0.652778` | full day |
| 2026-09-05 | `0.690556` | full day |
| 2026-09-06 | `0.270556` | partial — to the measurement instant |

**Ordinary cadence is ≈`0.65`–`0.69` CPU task-hours/day**, from the two complete non-outlier days.
The error was scaling a 21-minute delta instead of measuring whole days, and averaging across a day
that contained an 8.6-hour hang. **A rate taken from a window containing an outlier is not a rate.**

Consequently the projection was also wrong: over the ~23.6 days remaining to the R5 stop, the waker's
ordinary cadence implies **≈15–16 CPU task-hours**, not the ~1.5 an earlier revision stated — plus
hang risk, which one 09-03 event alone shows can add ~8.6 in a day.

**The magnitude was still never the point.** Even 15–16 task-hours against a 500 ceiling is ~3% and
not a ceiling risk. The point is that the instrument reported `0.0017` for work that had actually
spent `12.6` — wrong by four orders of magnitude — so a real production run would have been
mismeasured the same way.

### These captures are multi-window, and that shape has a known hazard

`sacct-hist-alloc-20260701-to-20260906.psv` is assembled from three queries (the 30-day span cap), and
a dump assembled from more than one window can contain **two observations of one execution**. Measured
in this file: exactly **2 byte-identical duplicate lines** out of 3,994 — jobs `57575105` and
`57644537`, each appearing twice with every field equal. `57575105` ran `08-27T15:00 → 08-28T01:59`
and straddles the `08-28T00:00` window boundary, which explains it; **`57644537` ran entirely inside
one window and its duplication is unexplained** — recorded as unexplained rather than given a cause.

Both are the benign form: rows sharing `(JobID, Start)` that agree on every field, so any meter keying
on that pair collapses them to one. The dangerous form — a `RUNNING` row with `End=Unknown` beside a
later `COMPLETED` row for the same start — **does not occur in any capture here**: `End=Unknown` rows
number **0** in all three. `sacct-arrays-duplicates-8field.psv` has **0** duplicate `(JobID, Start)`
pairs despite also being multi-window.

**The defect is a pattern, not an anomaly.** **Five** earlier jobs in the same `cron` waker lineage
show the same shape — `56585597` (1,580 attempts), `57575105` (490), `57668375` (354), `56139864`
(92) and `57275989` (9) — all `cron` partition, all `TimeLimit=12:00:00`, all CANCELLED, and all
outside the R5 window, so none of them move R5 spend. Had any run after t0 the meter would have
under-reported them identically. With the live waker `57712764` that is **six** requeueing jobs.

An earlier revision of this file said four. `57275989`, the smallest at nine attempts, was dropped
between the measurement output and the prose — the measurement was right and the summary was not.
It is named rather than rounded away, because a nine-attempt job is still a job the landed meter
would charge once.

### The arrays sweep's covering search is DISCONTIGUOUS — state it that way

`sacct-arrays-duplicates-8field.psv` is **three separate queries**, not one range:
`2026-07-10→2026-07-20`, `2026-08-12→2026-08-20`, `2026-08-25→2026-09-01` — three because NERSC
rejects any `sacct` window wider than 30 days. Observed `Start` values run `2026-07-09T16:30:23` to
`2026-09-01T06:41:58`, the earliest preceding the first window because `sacct` returns jobs running
*during* a window. **But the coverage inside that range has two holes:** `2026-07-20`–`2026-08-10`
(≈22 days) and `2026-08-21`–`2026-08-23` (≈3 days). Roughly 28 of those ≈54 days are covered.

So the negative result is: **zero requeued array tasks in 5,942 rows of retained allocation-level
accounting for user `josephrb`, across three discontiguous windows covering ≈28 days between
2026-07-09 and 2026-09-01.** Describing it as "spanning 2026-07-09 to 2026-09-01" would assert a
covering search that was not performed. A negative claim is only as good as its stated boundary, and
this campaign has already corrected one absence claim made without a covering search.

## Provenance

Measured read-only on Perlmutter, `login31`, user `josephrb`, by session `preflight [e11e6d]`, from
worktree base `f98cce8a`. The meter run was byte-identical to `HEAD:docs/orchestration/r5_meter.py`
(sha256 `3ea13eb99645a30853bffb0c1191298d188f566aaef3c7f7e52df4d2cb4a3e8d`), copied to a scratch
directory and run from there — the deployed checkout was never written to. No job was submitted, no
credential created or changed, no unattended execution configured.
