# FINDING 2026-09-06 — the R5 spend meter under-counted requeued execution attempts

**CITABLE FOR:** the metered unit of R5 spend; the magnitude of the pre-repair under-count on one
preserved capture; the `sacct` query R5 metering requires; the receipt schema-2 fields and the
version-1 refusal; the 30-day `sacct` window follow-up.

**NOT CITABLE FOR:** any current campaign spend figure. The capture below is one waker job over one
window, not a campaign total, and no operational receipt is produced by this repair. It is also not
an authorization: R5 is a prohibition, and the meter authorizes nothing.

**Status:** open — three things are with the decision owner, not settled here: a dated follow-up on
the 30-day `sacct` window (§7); an alternative reading of R5 §3, named plainly so it can be
overturned in one function (§5); and a remedy this lane deliberately **declined** to apply, because
it would change how compute admission can ever be armed (§8).

**Read §8 before verifying this branch.** After this repair the runbook's former example produces a
receipt that is valid and armable, and committing it opens compute admission queue-wide. Verify with
`measure` and no `--write`, or `--write` to a scratch path.

---

## 1. The defect

`docs/orchestration/r5_meter.py` at `c71b319a` measured spend in two ways that both fail on a
**requeued** job. A requeued job keeps one `JobID` and runs many times; each run burns real wall
time on a real node.

1. **The query omitted `--duplicates`.** `_sacct_argv()` asked for `--parsable2 --noheader
   --starttime <t0> --endtime now --format=...` with no `-D`, so for a requeued job Slurm returns
   only the **most recent** record. Every earlier execution attempt was invisible to the meter.
2. **The parser keyed every row by `JobID` alone.** `_parse_sacct_dump()` kept the row with the
   largest `ElapsedRaw` for a repeated id, and raised `MeterError` when two rows sharing an id
   differed in `(partition, is_gpu, start)`. So with `-D` added but the parser unchanged, the same
   capture does not under-count — it **refuses outright**.

Both directions are wrong, and direction 1 is wrong in the fail-**open** sense: it reports a smaller
number against a prohibition.

## 2. Measured magnitude, on the preserved capture

One self-requeueing waker job, `57712764`, on Perlmutter, over the R5 window from t0:

| measurement | metered rows | CPU task-hours |
|---|---:|---:|
| plain query (no `-D`), fed to the landed meter | 1 row of 6 s | **0.0016667** |
| `sacct -X -D` over the same window, fed to the **repaired** meter | 952 attempts, 45 325 s | **12.590278** |
| `sacct -X -D` over the same window, fed to the **landed** meter | — | refusal (below) |

The landed meter's verbatim refusal on the `-D` capture:

```
R5 measurement failed: line 2: conflicting rows for task identity 57712764
```

The capture holds 953 records: one `JobID`, **952 execution attempts** carrying real `Start` values,
plus **1 PENDING** row whose `Start` is `Unknown` and which is not an attempt. Independently
re-derived for this repair: `ElapsedRaw` over the 952 sums to **45 325 s = 12.590278 CPU
task-hours**; `JobID`, `Partition` (`cron`) and `AllocTRES`
(`billing=2,cpu=2,mem=4G,node=1` — no `gres/gpu`, so GPU is **0.0**) are constant across all 953
rows; there are **zero** duplicate `(JobID, Start)` pairs, **zero** duplicate
`(JobID, Start, End)` triples and zero byte-repeated rows; and every attempt starts after t0
(earliest `2026-09-02T13:45:35`), so no t0 clip applies to this capture. `ElapsedRaw` is
**per-attempt, not cumulative** — the values fluctuate non-monotonically (9, 10, 19, 10, …), which a
running total cannot do — so `Start` is the only attempt discriminator this field list carries.

The under-count factor on this one job is **7554×**.

## 3. Evidence

Read-only capture directory (another session's scratchpad; every file immutable, none committed):

`/private/tmp/claude-501/-private-tmp-claude-501--Users-josephbailey-local-research-MINERvA-OmniFold-bda4fd06-8826-4742-a374-deae75a8dcbb-scratchpad-wt-z-spec/38a63c82-9e50-4988-bba1-c9e107a3dc4d/scratchpad/r5-evidence/`

| file | lines | sha256 | role |
|---|---:|---|---|
| `sacct-waker-dup8.psv` | 953 | `6952180b38150622eeddfa6a028767023ceaac12af649d346990e92832fe06c8` | the `-X -D` capture; source of the committed fixture |
| `sacct-r5-t0-to-now.dump1.psv` | 3 | `e91b2f1122309464b8d09b01c112a0a0aa8104f8c2d452c3b1aa5c3dac0ba076` | the plain query; the 0.0016667 figure |
| `sacct-hist-alloc.psv` | 3994 | `473ba7687ca7a73ddd54ce6e7bf30207c74eb83a2d1d40a653075b6c1d17bc53` | 9-field historical dump; **not** the meter's field layout. Used only as a source of realistic shapes for synthetic controls; not fed to the parser and not committed |
| `receipt-live.json` | 39 | `7f4c44402172ecb1697566382adcc2b6eed7e8bc17c93464af3ec2522b42b934` | pre-repair preflight receipt; superseded (§6) |
| `receipt-fromfile.json` | 39 | `808da435e4e94c524d0251327cb9065b8aae39ff05c51ab8ca2c645b0fc00577` | pre-repair preflight receipt; superseded (§6) |

All five digests were verified before reading each file and again at the end of the repair.

Two further captures in the same directory were pulled after the repair began. Neither is committed
as a fixture; both were re-derived from the bytes by this lane rather than accepted as reported.

| file | rows | sha256 | what it establishes |
|---|---:|---|---|
| `sacct-r5-window-ALL-dup8.psv` | 958 | `39883879f74a7afae6f3626781c5b062362cd3ef36491d5ea6ce1c47b8d024e4` | the same window queried for **all jobs** rather than `-j 57712764`, i.e. the form `_sacct_argv()` actually issues. Contains **exactly one** distinct job id, so the `-j`-scoped capture was complete in scope and nothing was missed |
| `sacct-arrays-dup8.psv` | 5942 | `ab0ee11f639e15dea57ded330807a8fcdf558dc15dad789a52a94224797d5e99` | a wider `-X -D` sweep, allocation level, user `josephrb` |

**Every total in this finding belongs to a pinned capture at a stated instant, and is not a campaign
spend figure.** The all-jobs capture, taken about twenty minutes after the `-j` one, meters **958
attempts and 12.606389 CPU task-hours** where the `-j` capture meters 952 and 12.590278. The
difference is five further waker firings, not a discrepancy: the corrected R5 CPU figure **grows by
roughly 0.05–0.07 task-hours per day** from the waker's ordinary cadence alone. Any assertion of a
fixed total must pin the capture rather than re-query, which is what the committed fixture does.

What the wider sweep establishes, each re-derived here from the committed bytes:

- **No requeued array task exists in the covered accounting** — zero of the 2 487 distinct
  `JobID_TaskID` ids appear more than once, in 5 942 rows of retained allocation-level accounting for
  user `josephrb`, across **three discontiguous windows totalling ≈28 days** between
  `2026-07-09T16:30:23` and `2026-09-01T06:41:58`, with absences of 22 days
  (`2026-07-19`→`2026-08-11`) and 3 days (`2026-08-20`→`2026-08-24`). The windows are three rather
  than one because of the 30-day span cap in §7. The claim is bounded by that covering search: it is
  not a claim about all time, all users, or step-level rows. **The array control in the test suite is
  therefore synthetic of necessity**, and is labelled as such — no preserved capture contains a
  requeued array task.
- **The defect is a pattern, not an anomaly.** Six distinct plain job ids in that sweep carry more
  than one attempt record: `56585597` ×1580, `57712764` ×612, `57575105` ×490, `57668375` ×354,
  `56139864` ×92, `57275989` ×9. All are `cron`-partition jobs of the same waker lineage. All but
  `57712764` fall outside the R5 window and move no R5 spend — but each would have been under-counted
  identically had it run after t0, and the smallest is named here deliberately, because a nine-attempt
  job is still a job the landed meter charged once.
- **Real `JobID` bracket spellings exceed what the fixtures exercised.** The sweep holds 55 bracket
  rows in three spellings — 46 of `N_[N-N%N]` carrying a `%` concurrency throttle
  (e.g. `55799900_[6-100%32]`), 6 of `N_[N-N]`, and 3 of single-element `N_[N]` — where
  `mixed.sacct` only ever held `20001_[1-100]`. `TASK_ID_RE` excludes all three correctly, so this is
  a **coverage** gap and not a defect; the point is that "correct against real spellings" and
  "correct against the spelling we imagined" were different claims and only the second was supported.
- **`None` is a real `Start` value**, not defensive coding: 112 of the 5 942 rows carry the literal
  string, against 5 830 timestamps. It is already in the skip set.
- **Zero duplicate `(JobID, Start, End)` triples across all 5 942 rows.** This is the strongest
  available support for the attempt identity at scale — and it also means **no preserved capture
  contains a byte-repeated observation**, so that test arm is synthetic and is labelled so.

**Provenance of the evidence.** The captures were committed by the capturing lane at `cd41ff41`,
`21b3d567` and `1422569c` on branch `lane/pm-root-inspection-20260906`, under
`docs/orchestration/state/preflight-20260906-r5/` (filenames there differ — `-dup8` is spelled
`-duplicates-8field` — with identical bytes and digests). That branch is **unpushed** and is **not an
ancestor of `main`** at this repair's base `c71b319a`; its own base is `641c6812`, which is pushed.
**The binding is the sha256 of each capture; the commit is only a locator**, and that holds whether
or not the branch ever lands.

The literal argv that produced `sacct-waker-dup8.psv`, with `TZ=UTC` and
`SLURM_TIME_FORMAT=%Y-%m-%dT%H:%M:%S` exported:

```
sacct -j 57712764 -X -D --parsable2 --noheader --starttime 2026-09-02T13:44:27 --endtime now \
  --format=JobID,JobName,State,ElapsedRaw,Partition,Start,End,AllocTRES
```

### The committed fixture

`docs/orchestration/test_fixtures_r5_meter/waker_requeue_attempts.sacct`

| | |
|---|---|
| original sha256 | `6952180b38150622eeddfa6a028767023ceaac12af649d346990e92832fe06c8` |
| transform | replace the byte string `/pscratch/sd/j/josephrb/` with `/pscratch/sd/u/anonuser/`, and nothing else. All 953 occurrences were confirmed to lie inside field 1 (`JobName`); no reordering, no trimming, no renumbering; length unchanged (174 679 bytes both sides) |
| sanitized sha256 | `529c54f16e2b3d319440b4be23160063afa2200353d6120eec740090faec5389` |
| totals agree | **yes** — the two inputs produce byte-equal `spend` objects. `JobName` is not an accounting field |

No other capture is committed.

## 4. The corrected semantics

- **The metered unit is an execution attempt**, identified by **`(JobID, Start, End)`**. `End` is
  carried so that a same-start/different-end pair cannot silently collapse.
- **Attempts are summed** per job id.
- **Deduplicated:** two rows agreeing on all three key fields are one observation of one attempt and
  are charged once (`mixed.sacct`'s `20001|duplicate` row keeps exactly this meaning). `.batch`,
  `.extern`, numbered steps and array-bracket summary rows are excluded outright — a step row is a
  *representation* of an execution, never an attempt. A row whose `Start` is `Unknown`/`N/A`/empty
  is skipped.
- **Fails closed:** two observations of one attempt disagreeing on `ElapsedRaw`, or on GPU
  classification, raise `MeterError` naming the job id and the field; a `schema_version` 1 receipt
  is refused by `r5_meter._validate_receipt`, by `r5_meter check` (exit 4) and by
  `campaignctl.validate_r5_receipt`; a missing, stale or malformed receipt remains a stop.
- **t0 rules are per attempt, not per job:** an attempt straddling t0 is clipped at t0, one that
  ended at or before t0 is excluded, and later attempts of the *same* id are still charged in full.
  A per-job clip gets this case wrong in both directions.
- **GPU classification is per attempt**, from `AllocTRES` `gres/gpu` with the partition prefix as a
  secondary signal, because a requeue can land on a different partition. CPU cores in a GPU
  allocation are still not also charged as CPU.
- The query is now `sacct --user <me> -X -D --parsable2 --noheader --starttime <t0> --endtime now
  --format=...` under `TZ=UTC` and `SLURM_TIME_FORMAT=%Y-%m-%dT%H:%M:%S`. `--allocations` and
  `--duplicates` were measured to compose on the real cluster.
- Unchanged: inclusive ceiling and date boundaries, OR trigger logic, `fired`, `headroom`, the
  atomic receipt write, and t0 = `2026-09-02T13:44:27Z` / stop = `2026-09-30T00:00:00Z` /
  500 GPU + 500 CPU task-hour ceilings.

### Receipt schema 2

`spend` keeps every previous key and gains two:

| field | question it answers |
|---|---|
| `task_count`, `metered_task_ids` | which SCHEDULER TASKS were counted — **bare** ids, `^[0-9]+(?:_[0-9]+)?$` |
| `attempt_count`, `attempts_by_task_id` | how many EXECUTION ATTEMPTS were charged, in total and per task id (sorted by key) |
| `by_state` | attempts per Slurm state, so it now sums to `attempt_count` rather than to `task_count` |

`metered_task_ids` keeps holding bare scheduler ids deliberately.
`campaignctl.py` pins the identical `TASK_ID_RE` and releases a queue item's spend reservation only
when a committed receipt lists that item's declared ids. Spelling an attempt into an id (say
`57712764#3`) would make every producer declaration unmatchable and release nothing. So
`metered_task_ids` answers "was this item's spend counted" and `attempts_by_task_id` answers "how
many of its executions were charged"; the release path reads only the first, because an item must
not become releasable, or stop being releasable, because its job requeued.

## 5. Why attempts are summed — and the reading this rejects

**The ruling text.** R5 §3 defines the unit as "sum of `ElapsedRaw` over **distinct task
identities**, `.batch`/`.extern` and array-bracket rows excluded", and separately rules that
"**failed and retried tasks** [are] **counted in full**" and that "**a failed task spends**".

**The adopted reading.** "Distinct task identities" sits in the same table cell as the exclusion of
`.batch`, `.extern` and array-bracket rows, which is what fixes its subject: it is there to stop the
several **representations** of one execution — `.batch`, `.extern`, numbered steps, array-bracket
summary rows, and a repeated observation of the same row — from being counted more than once. It
does not collapse several distinct **executions** of one job id. 952 requeue attempts each occupied
a real node for real wall time, and §3 says retried time counts in full, so the correct figure for
`57712764` is 12.590278 CPU task-hours.

**The alternative reading, named plainly so it can be overturned.** One could read "distinct task
identities" as the *accounting unit itself* — one charge per job id, whatever a requeue did. Under
that reading `57712764` is worth one attempt's elapsed time: 0.0016667 CPU task-hours as the plain
query reported it, or 8.628611 (the largest single attempt, 31 063 s) under the landed parser's
"keep the largest `ElapsedRaw`" tie-break. The repair here would then over-charge this job by a
factor of about 7554, or about 1.46, respectively.

**Why the adopted reading wins the tie.** Under-counting is the fail-**open** direction against a
prohibition: it buys headroom the campaign has not got. Over-counting refuses runs that R5 might
have permitted, which is recoverable by a decision; under-counting spends past a ceiling, which is
not. That, plus §3's explicit "counted in full" / "a failed task spends", settles it.

**Cost of overturning.** The summing step is isolated in one function,
`r5_meter._sum_charged_seconds`, precisely so a contrary ruling is a cheap change: charging one
attempt per job id would change that function and nothing else in the accounting path (the receipt's
`attempt_count` / `attempts_by_task_id` columns would then become descriptive rather than
load-bearing).

## 6. Receipts requiring replacement

- **There is no committed `docs/orchestration/state/r5-meter-receipt.json` at `c71b319a`.** Verified:
  `git cat-file -e c71b319a:docs/orchestration/state/r5-meter-receipt.json` → *does not exist*, and
  no path ending `r5-meter-receipt.json` appears anywhere in that tree. The only committed files
  matching `r5-meter-*.json` are the six `test_fixtures_campaign_contract/` receipt fixtures, which
  are test inputs and have been updated to schema 2 by this repair.
- **The only pre-repair receipts in existence are two uncommitted preflight files**, `receipt-live.json`
  (`7f4c4440…`) and `receipt-fromfile.json` (`808da435…`), in the read-only evidence directory in §3.
  Both are `schema_version` 1 and both are **superseded** by this repair. Neither was ever committed,
  so neither was ever admissible to `campaignctl` (which requires a tracked receipt byte-identical to
  its blob at `HEAD`), and no queue admission ever rested on them.
- **Nothing needs to be replaced, and nothing was.** No operational receipt was manufactured from an
  old capture, and `docs/orchestration/state/r5-meter-receipt.json` was **not** written: this host
  has no `sacct`, so a receipt produced here would be a false measurement. The first measurement
  under the repaired meter remains a Perlmutter act, per `R5-METER.md`.
- Consequently the campaign's compute-admission posture is unchanged by this repair: with no
  committed receipt, `campaignctl` already refuses every compute item, and `r5_meter check` already
  returns 4.

## 7. Follow-up for the decision owner — the 30-day `sacct` window

**Dated 2026-09-06. Not implemented here; out of scope by instruction.**

NERSC rejects any `sacct` window wider than 30 days:

```
sacct: error: Too wide of a date range in query
```

Measured by bisection: a 30-day span is accepted, a 31-day span is rejected, the limit is on the
**span** and not on the lookback, and `-j <jobid>` bypasses it.

`_sacct_argv()` queries **t0 → now**, so its span reaches 30 days at

> **2026-10-02T13:44:27Z**

which is **2 d 13 h 44 m 27 s after** the R5 stop date of `2026-09-30T00:00:00Z`. The meter is
therefore inside the limit for the entire campaign window. From that instant `sacct` errors, the
meter produces no receipt, and everything downstream fails **closed** (`check` returns 4;
`campaignctl` refuses compute).

**Chunking is deliberately not implemented.** One case still needs attention:

> R5 §3 lets jobs running at the stop **run to completion with their spend counted**. The final
> measurement of those jobs must therefore be taken **before 2026-10-02T13:44:27Z**, or the t0→now
> query can no longer be issued at all and that final spend cannot be metered by this tool. A job
> still running at the stop and finishing after that instant would need `sacct -j <jobid>` (which
> bypasses the span limit) or a chunked window.

*(Note on a figure: an earlier statement of this follow-up put the gap at "2 d 10 h". The 10 h there
is the remainder in `stop − t0 = 27 d 10 h 15 m 33 s`, not the gap after the stop. The firing instant
itself, `2026-10-02T13:44:27Z`, is unaffected.)*

## 8. What this repair makes possible — arming compute admission

**This repair writes no receipt, and landing it leaves compute admission exactly as shut as it is
today.** That is deliberate (§6). But it changes what the *documented* invocation produces, and that
is worth stating plainly rather than leaving for someone to discover.

**The conversion this repair performs.** Before it, the canonical command in `R5-METER.md` produced
the `0.0016667` receipt — the under-count this finding is about. Committing that would have armed
admission on a receipt that is visibly wrong and that a reader would likely catch. After this repair
the same command produces a **valid, complete, honestly armable** receipt: nothing about it is wrong
except that committing it is a queue-wide decision nobody made deliberately. The repair converts a
dud into live ammunition, which is why the runbook could not be left as it was.

**The sequence, and why neither step announces itself.** `campaignctl` requires the receipt
**committed** (`committed_r5_receipt`), so the write alone admits nothing. What completes it is an
ordinary commit of the state directory. Each fact below was verified in this tree:

| fact | verified |
|---|---|
| nothing ignores the receipt path | `git check-ignore -v docs/orchestration/state/r5-meter-receipt.json` → exit 1, no rule |
| committing that directory is routine | `git ls-files docs/orchestration/state/` → **150** tracked `.json` files |
| the runbook framed the write as hygiene | `R5-METER.md` said "atomically **refresh** the **default** receipt" — corrected by this repair |
| the commit requirement is load-bearing, not incidental | the `CAMPAIGN_R5_RECEIPT` override is repository-relative only and must be **tracked and byte-identical to its blob at `HEAD`** |
| the window is 24 hours | `R5_MAX_AGE` (`campaignctl.py:292`), measured from `measured_at_utc`, not from the commit |

So: run the documented command, then `git add -A`. **The exposed person is a careful reviewer
following the runbook to confirm the meter works** — following the instructions is the dangerous
path, which is a worse failure mode than a footgun, because the people most likely to trip it are the
ones being most diligent.

**Remedy taken.** `R5-METER.md`'s verification examples now use `measure` with no `--write`, or
`--write` to a scratch path; `--write` has no default, so neither can arm anything. The word
*refresh* is gone. A dedicated section states that writing and committing to the state path opens
compute admission queue-wide, and the runbook's closing disclaimer — "the meter authorizes nothing" —
is now marked as a statement about **authorization** that is **silent about admission**. That
sentence was worse than no disclaimer, because it discharged a careful reader's suspicion about the
adjacent question.

**Remedy NOT taken, and offered to the decision owner instead.** The gate path could be untracked or
ignored, which would close the second step outright. **This lane declined to do that.**
`committed_r5_receipt` *requires* the receipt committed, so ignoring the path changes **how admission
can ever be armed, for anyone, in any future** — a change to the admission mechanism wearing
documentation clothes, and not something to fold into a bounded accounting repair. It is recorded
here as a live option for the decision owner, with the 150-tracked-files fact that motivates it.

**A coupling worth seeing before choosing.** Where a decision is pending between granting a narrow
accounting exception and waiting for this repair so a complete receipt can be committed, those two
are not the same outcome reached with different patience. The first authorizes one declared item and
leaves the gate shut. The second **opens the gate for every compute item the queue holds or later
admits**. The second is the procedurally correct path and also the larger commitment, and it is
exactly the path that makes accidental arming both possible and undetectable, at the moment it
becomes procedurally available. It should be taken with the runbook already corrected, which this
repair does.

**The asymmetry, which is the reason none of this is merely tidy.** An accidental arming heals in 24
hours when the receipt goes stale. It heals the receipt. It does not heal the jobs admitted and run
inside that window. The commit is reversible; the compute is not.

**Operational instruction, for anyone verifying this branch.** Verify with `measure` and no
`--write`, or `--write` to a scratch path. Never run the state-path example as a smoke test, and do
not commit `docs/orchestration/state/` afterwards without looking at what is in it.

## 9. What landed

| file | change |
|---|---|
| `docs/orchestration/r5_meter.py` | attempt-keyed parser, per-attempt t0 clip, `_sum_charged_seconds`, `-X -D`, schema 2 + v1 refusal, extended `--self-test` |
| `docs/orchestration/campaignctl.py` | `R5_SPEND_KEYS` + exhaustive attempt-column validation, schema-2 requirement with a v1 refusal, identity reconciliation comments at `TASK_ID_RE`, `R5_SPEND_KEYS` and `ReceiptAccounting` |
| `docs/orchestration/test_fixtures_r5_meter/waker_requeue_attempts.sacct` | new — the sanitized real capture |
| `docs/orchestration/test_fixtures_campaign_contract/r5-meter-*.json` | six receipt fixtures bumped to schema 2 with consistent attempt columns |
| `docs/orchestration/test_r5_meter.py` | 18 new tests: the real capture, the ten synthetic controls, and the schema refusals |
| `docs/orchestration/test_campaignctl.py` | requeued receipt accepted, v1 receipt refused, and the cross-module id test strengthened so pattern equality cannot go vacuous |
| `docs/orchestration/R5-METER.md`, `OPERATOR-GUIDE.md` | corrected semantics, new `spend` fields, v1 refusal, the 30-day note; and the verification examples moved off the receipt path with a section stating that writing and committing there arms compute admission queue-wide (§8) |

The regression suite was confirmed load-bearing: with `r5_meter.py` alone reverted to its
`c71b319a` content, 18 of these tests fail — the real-capture test with the same
`line 2: conflicting rows for task identity 57712764` the defect produced.

The R5 decision record, `LIVE-STATE.md` and `state/live-state.json` were not modified.
