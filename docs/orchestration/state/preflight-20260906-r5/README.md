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
`2026-09-06T08:59Z` over 953 attempts, `12.606389` at `2026-09-06T09:20Z` over 958. The waker fires
about every five minutes, so the figure grows ~0.05–0.07 CPU task-hours/day on ordinary cadence, and
a single hang added 8.63 hours on 2026-09-03. **Attribute any total to a pinned capture and its
digest; never re-query to reproduce one.**

The magnitude was never the point. ~1.5 CPU task-hours over the remaining campaign against a 500
ceiling is not a ceiling risk. The point is that the instrument reported `0.0017` for work that had
actually spent `12.6` — wrong by four orders of magnitude — so a real production run would have been
mismeasured the same way.

**The defect is a pattern, not an anomaly.** Four earlier jobs in the same `cron` waker lineage show
the same shape — `56585597` (1,580 attempts), `57575105` (490), `57668375` (354), `56139864` (92) —
all CANCELLED and all outside the R5 window, so none of them move R5 spend. Had any run after t0 the
meter would have under-reported them identically.

## Provenance

Measured read-only on Perlmutter, `login31`, user `josephrb`, by session `preflight [e11e6d]`, from
worktree base `f98cce8a`. The meter run was byte-identical to `HEAD:docs/orchestration/r5_meter.py`
(sha256 `3ea13eb99645a30853bffb0c1191298d188f566aaef3c7f7e52df4d2cb4a3e8d`), copied to a scratch
directory and run from there — the deployed checkout was never written to. No job was submitted, no
credential created or changed, no unattended execution configured.
