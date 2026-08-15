# FINDING 2026-08-13 — `sstat` silently returns ONE task for every task of an array, and five identical rows read as five healthy members

**Status:** measured, live. **Lane:** A (orchestrator).
**NO `BEN-*` ROW — lane A's block `190`–`199` is exhausted (all ten filed, recomputed against
`FINDINGS.md` at the moment of writing).** Borrowing from `200+` or another lane's block is
`BEN-080`/`BEN-082`'s exact shape, so this is filed as long-form and indexed only. **That makes it
`BEN-167`'s defect by construction: a finding with no id is invisible to the allocator.** The range
allocation is a convention change and routes to Joseph; it needs deciding *before* the next A
finding, not after. This is the second A finding tonight with nowhere to go.

## What happened

Judging Gate 6 array `56834281_[1-5]` liveness under `BEN-028` (never judge by log growth; use `sstat`
CPU time and produced artifacts). Logs were block-buffered and identical in size, and no member
artifacts existed yet, so `sstat` was the only instrument left. Ran:

```
for t in 1 2 3 4 5; do sstat -j 56834281_${t}.batch --format=AveCPU,MaxRSS,TRESUsageInTot -P -n; done
```

All five rows came back **byte-identical**: `AveCPU 01:28:34`, `MaxRSS 18551028K`, `gpuutil=52`,
`fs/disk=30756611591` — and the same `energy` on four of five, differing on the fifth only because it
was sampled a second later.

## Why that is impossible, and why it nonetheless looks like a pass

The five members had elapsed times of `01:47`, `01:47`, `01:39`, `01:37`, `01:17` at the moment of
measurement. **A member running thirty minutes less than another cannot have consumed identical CPU
seconds.** The identity is the tell, and it is the only tell — every individual value was plausible.

**Five identical healthy-looking rows is a reading a tired reader accepts.** It parses as *"the
ensemble members are doing the same work at the same rate,"* which is exactly what an ensemble of five
same-configuration trainings is *supposed* to look like. The wrong answer here is more persuasive than
the right one.

## The mechanism

`sstat` ignored the `_<task>` suffix and returned job `56834281` five times. It could do that because
**for this array the master job id and one task's raw id are THE SAME NUMBER**:

```
JobID          JobIDRaw     Start                 Elapsed
56834281_1  -> 56834282     2026-08-12T21:36:12   01:47:00
56834281_2  -> 56834283     2026-08-12T21:36:12   01:47:00
56834281_3  -> 56835083     2026-08-12T21:43:48   01:39:24
56834281_4  -> 56835084     2026-08-12T21:46:03   01:37:09
56834281_5  -> 56834281     2026-08-12T22:06:03   01:17:09   <-- raw id == array id
```

So `56834281_5` *is* `56834281`, and every `56834281_<t>.batch` query resolved to member 5. The
returned CPU `01:28:34` matches member 5's own later reading of `01:29:03` — same job, sampled twice.

Note the array's raw ids are **not contiguous and not ordered**: tasks 3 and 4 got `56835083`/`56835084`
from a different part of the id space than tasks 1, 2 and 5. Any code inferring a task's raw id by
arithmetic on the array id is wrong on this array.

## The fix

**Resolve the raw id first and query that.** `sacct -X` is the authority for the mapping — and it must
be read as a **PAIR**, `JobID` alongside `JobIDRaw`:

```
sacct -X -n -P -j <ARRAYID> --format=JobID,JobIDRaw | while IFS='|' read -r task raw; do
  printf "%-14s raw=%-10s " "$task" "$raw"
  sstat -j "${raw}.batch" --format=AveCPU,MaxRSS -P -n 2>/dev/null | head -1
done
```

**CORRECTED 2026-08-13, and the first version of this fix was itself defective.** It read
`--format=JobIDRaw` alone and looped over the bare ids. That returns five *distinct* readings — so it
looks fixed, and the uniformity tell that exposed the original bug is gone — but it **cannot say which
member each reading belongs to**, and attribution is the entire purpose. Per-member seed_policy
verification and any per-member liveness claim need the pairing. Caught by Session C re-arming its own
watch against this finding and noticing the recipe it inherited could not answer the question it was
armed to ask.

**That is worth more than the original finding.** A fix that removes the *symptom* the bug was detected
by, while leaving the underlying question unanswerable, is harder to catch than the bug — the second
reading is plausible, non-uniform, and wrong in a way nothing tells you about.

**Ship the distinctness assertion with it,** since a per-entity sweep that silently collapses is the
failure mode:

```
n=$(sacct -X -n -P -j <ARRAYID> --format=JobIDRaw | while read -r r; do
      sstat -j "${r}.batch" --format=AveCPU -P -n 2>/dev/null | head -1; done | sort -u | wc -l)
[ "$n" -gt 1 ] || die "per-task query returned identical rows -- suspect id aliasing"
```

Measured on this array: 5 distinct values, and CPU advances between samples (member 1: `02:05:47` ->
`02:12:03` six minutes later), which is the liveness reading itself rather than a proxy for it.

Re-measured that way the five members are distinct and physically sensible — CPU/elapsed ratios of
1.17, 1.20, 1.17, 1.16, 1.15, monotonic with elapsed time, all consistent with a 32-CPU threaded
trainer. **That is the liveness verdict `BEN-028` asks for; the first reading could not have supplied
it in either direction.**

## The check that would have caught it, and it is cheap

**Assert the rows DIFFER.** Any per-entity sweep whose entities are genuinely distinct should refuse a
result set that is uniform:

```
[ "$(sort -u <<<"$rows" | wc -l)" -gt 1 ] || die "per-task query returned identical rows -- suspect id aliasing"
```

This generalises past `sstat`. **A per-entity query that returns N copies of one entity is
indistinguishable from N entities that agree**, and uniformity is the only signal available. It is the
same shape as the `28,672 B x 240` uniformity tell that caught the HPSS digest defect, and the same
shape as a path check that stat'd one directory 240 times — **both already recorded, both found by
noticing sameness rather than by a verdict.** Tonight makes three.

## Second instance tonight of a different shape: the tree already knew

`wakerctl` was asserted DEAD ("crashing on every tick since 2026-07-20") in a scheduled wakeup block
and independently repeated by Session C from a prior handoff. **It is alive** — three ticks from three
different login nodes (`login05` 06:00:08Z, `login11` 06:04:16Z, `login22` 06:20:14Z), scrontab job
`56585597` queued, and a watch armed this session evaluates clean (`scan` -> `[]`, `unreliable: 0`).

**The correction was already in this directory and had been for nine days:**
`FINDING-20260804-wakerctl-tick-correction.md`, titled *"CORRECTION: the waker tick is not broken; it
runs clean."* Two agents restated the superseded claim anyway, one of them while invoking
existence-versus-operation as a principle.

**So the defect is not that nobody measured — it is that a correction filed in the canonical place did
not reach the readers who needed it.** An indexed long-form finding is necessary and was not
sufficient. Worth weighing against the standing preference for the executable form of a rule: a check
costs zero and cannot be skipped, whereas this document was skipped twice.

**CLOSED END-TO-END 2026-08-13T08:10:08Z, and this is the strongest available refutation.** The earlier
evidence showed `wakerctl` *ticks* and *scans*. The Gate 6 watch has now completed the full path on a
real event: `watch-armed` 06:04:04Z (login11) -> `event-emitted` 08:10:08Z (login16), payload
`overall: COMPLETE` with all five tasks `0:0` read from `sacct` -> `invoked`. Emitted from a **third**
login node, two hours after arming, by the cron net alone. **A subsystem that arms, evaluates, fires,
claims and dispatches is not dead in any sense of the word**, and the claim that it had been dead since
2026-07-20 is now refuted by operation rather than by inspection.

**AND THE FIRED EVENT EXPOSES A GAP IN MY OWN GUARD, which is worth more than the confirmation.** The
event records `head_at_event: 683bdcc` — the **cluster** HEAD, 309 commits behind. The resume prompt I
armed tells the resumed thread to *"look for a Gate 6 receipt/RUN_LOG entry landed after the array
terminal time and do not duplicate it."* **That receipt (`92551a4`) is on `origin/main` and is NOT in
the cluster checkout**, which is deliberately unsynced as policy rather than as a technical limit. So a
resumed thread reading the cluster tree would look for the guard's evidence in the one tree that cannot
contain it, conclude nothing had been done, and duplicate the reconciliation. **A guard that names an
artifact must also name the tree the artifact lives in** — on a repo with a deliberate fork, "look for
a commit" is underspecified, and the failure is silent in the direction of doing the work twice.

**A real caveat on the live-and-well verdict, which is not a reprieve:** the cluster checkout is 309
commits behind at `683bdcc`, so it runs the pre-2026-08-11 `wakerctl.py` whose `scan()` has no
per-watch `try/except`. One malformed watch aborts the loop and skips dispatch silently, and
`last-tick.json` there carries no `watch_errors` key — confirmed by absence. **The net operates today
and is one bad watch away from silent, with no field that would say so.** Reconciling that fork is
forbidden during closeout, so this is recorded as known exposure rather than fixed.

---

# THE ALIASING CAUGHT LIVE, WITH ITS MECHANISM, AND IT EXPLAINS A `squeue`/`sacct` DISAGREEMENT (2026-08-15)

**`BEN-229`, and it invalidates `BEN-210`'s prescribed remedy in one specific regime.** `229` is the last free
id in lane A's `220-229` block; the next lane-A filing takes a fresh closed ten-block per `FINDINGS.md`'s
self-allocation rule.

**A correction made while filing this, against this very file's index entry.** Lane A first wrote that this
file *"had no ledger row until now"*, taking `FINDINGS.md`'s index line at face value: *"**NO BEN ROW** — lane
A's block 190-199 is exhausted."* **That note is stale.** This file has carried `BEN-210` — and `BEN-211` for
the defective fix — since 2026-08-13, filed out of A's `210-219` block after the note was written. The note was
never updated. **Whether a finding has a row is machine-derivable** (grep the filename across the rows), so a
prose note asserting it is `BEN-228`'s general form exactly: *a hand-maintained index of a machine-derivable
fact goes stale silently*. Corrected in the index in the same commit as this section.

**Found while verifying a report, not while debugging a failure.** The mediator checked lane A's Leg-0
submission and observed that two tools disagreed about the size of the same array **in the same second**:

```
2026-08-15T04:33:48Z .. 04:33:50Z   (one 2-second window, one job id)
squeue -j 56993778 -r   ->  _1 _2 _3 _4 _5    all PENDING     FIVE tasks
squeue -j 56993778      ->  56993778_[1-5]    PENDING
sacct  -j 56993778 -X   ->  56993778_[3-5]    PENDING         THREE
sacct  -j 56993778 -X -D ->  56993778_[3-5]   PENDING         (--duplicates: same)
```

**`sacct` under-reported a live array by two tasks.** Reproducible, same id, same second, no lag argument
available.

## The mechanism, which refines the first reading rather than confirming it

The natural reading — the mediator's, and lane A's before measuring — is *"`sacct` is collapsing the range and
dropping the head of it."* **That describes the symptom and gets the cause backwards.** Two more queries
settle it:

```
sacct -j 56993778_1   ->  (empty)
sacct -j 56993778_2   ->  (empty)
sacct -j 56993778_3   ->  (empty)      <- INSIDE sacct's own reported [3-5]
```

**`sacct` returns nothing for ANY individual pending task, including one it claims to be reporting.** So it is
not dropping a head; it has **no per-task records at all**. Then `scontrol`, which does:

| array task | raw `JobId` |
|---|---|
| `56993778_1` | `56993779` |
| `56993778_2` | `56993780` |
| **`56993778_3`** | **`56993778`** |
| **`56993778_4`** | **`56993778`** |
| **`56993778_5`** | **`56993778`** |

**Slurm splits array tasks off the parent record one at a time as it prepares to schedule them.** Tasks 1 and
2 have been split and carry new raw ids; **tasks 3, 4 and 5 are still collapsed under the array's own id.** So
`sacct`'s `[3-5]` is the **unsplit remainder** — the only record that exists under job id `56993778` — and
tasks 1 and 2 are absent because their new raw ids have no accounting rows until they start. The range shrinks
from the *head* as tasks are split, which is why it looked like a dropped head.

## Why this is worse than `BEN-210`, and why it BREAKS `BEN-210`'s REMEDY

`BEN-210` was *"the array id equals ONE task's raw id, so five byte-identical `sstat` rows read as five healthy
members,"* and its prescription is explicit: **"Resolve the PAIR via `sacct -X --format=JobID,JobIDRaw`."**

**That remedy returns NOTHING here.** `sacct -j 56993778_<t>` is empty for every task, so on an array that has
not started, the instrument `BEN-210` tells you to use cannot answer the question `BEN-210` tells you to ask.
The remedy is correct **after** tasks start and silently unavailable **before** — and *silently* is the
problem, because an empty `sacct` result looks like "no aliasing found" rather than "this tool cannot see the
array yet." **A resolver written to `BEN-210`'s prescription returns an empty mapping on a pending array and
its caller cannot distinguish that from a clean one.** This is the third correction in the `BEN-210` lineage
after `BEN-211`, and the same shape: **the fix removed the symptom the bug was detected by.**

Two further ways this instance is worse than the original:

- **Three tasks alias simultaneously**, not one, so a query keyed on `56993778` represents tasks 3, 4 and 5
  with a single row.
- **The aliasing set is NOT STABLE — it shrinks as tasks are split.** A mapping resolved early and cached is
  wrong later, in the direction that silently *over*-reports health, because one live row stands in for
  several tasks. `BEN-210`'s remedy assumes the pairing is a fact to be looked up once; it is a snapshot.

## The checks

> **`sacct` IS NOT AUTHORITATIVE FOR AN ARRAY THAT HAS NOT STARTED.** Before a task starts there is no
> accounting row; `sacct` reports only the unsplit remainder and will under-count. **Use `squeue -r` for
> pending state** (it expands every task and is the only tool here that got the count right), and **`scontrol
> show job <array>_<task>`** to resolve the raw id.
>
> **Never key a per-task query on the array id.** Resolve `ArrayJobId`/`ArrayTaskId`→`JobId` per task and
> assert the raw ids are **distinct** before believing per-task rows. Re-resolve rather than caching: the
> aliasing set changes as tasks are split.
>
> **A count from `sacct` and a count from `squeue` are not the same measurement.** Publishing either without
> naming the tool is `BEN-027`'s shape — *"every ID, rank, count and queue name in a status report must come
> from a command run in the same turn"* — and this instance shows the same turn is not sufficient. **The tool
> is part of the measurement.**

**Lane A's own report survived this** — it said `[1-5]` and read the count from `squeue`, which is correct.
**It survived by luck of tool choice, not by knowing this**, and anyone verifying that record with `sacct`
alone would have concluded the array size was mis-stated. That asymmetry is the reason this is written down.

**Incidental, and consistent with `OI-74`:** `scontrol` also showed `Reason=Priority` on task 1, so this array
is priority-starved rather than merely queued — the same contention Leg F's tasks 4 and 5 hit.
