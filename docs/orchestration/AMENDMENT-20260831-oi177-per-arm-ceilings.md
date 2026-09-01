# AMENDMENT 2026-08-31 — `PROPOSAL-20260830-forward-only-rehearsal.md` §6 per-arm budgets
# ✅ **RATIFIED 2026-09-01 BY JOSEPH — *"I sign"*. `OI-177` DISCHARGED.**
# (Header before that date read: PREPARED FOR SIGNATURE. NOT RATIFIED. `OI-177` REMAINS OPEN.)

**CITABLE FOR:** the measured `aa67c426` and round-2 actuals in §2/§3d and the method that produced
them; the provenance of §6's original estimate column; §3e's three-unit reconciliation and two-round
floor/median comparison; and **the ratified per-arm ceilings — see §5.** **All hour figures in this
document are TASK-HOURS** per the 2026-09-01 ruling — bare `CPU-h`/`A100-h` cells mean task-hours
throughout. **NOT CITABLE FOR:** any gate movement; leg 6; the M(ii) family; adoption of any
covariance; or any authorization to launch. **Gate 2 remains FAIL, nothing is adopted, CAND `1 of 7`
/ QUOTED `0 of 7`.**

**⚠ READ §5 BEFORE §3.** Sections 0–4 were written *before* signature and argue toward a
recommendation; §3's proposed `40` for arm 5 is **dead** and §3b/§3d supersede it. §5 records what was
actually signed. One figure quoted at signature time — arm 4's *"12.4% headroom"* — used a different
denominator from every other headroom figure here; §5 states both and neither changes a decision.

## 0. Why §6 needs amending rather than re-reading

`OI-177` records that three arms' measured actuals exceed their §6 ceilings by **1.38 CPU task-h in
total**. The cause is not a slipped number, it is an **asymmetric comparison**, and it is verifiable
by reading two files side by side:

**§6's "measured or bounded estimate" column is inherited verbatim from
`PLAN-20260822-oneMember-mii-staged.md:220-224`** — `14.00`, `3.72`, `14.23`, `23.84`, `21.38`,
`22.02` appear in both, to the digit. That plan is a **2026-08-22 prior**, and §6 says its ceilings
are *"deliberately above the recorded estimates"* — above those priors, not above any measurement of
this rehearsal's arms.

**And §6's own detector row admits the population mismatch in passing:** it reads *"conservative prior
from the older 24-task population"* while declaring the arm as `0-18`, which is **19 tasks**. A
per-task prior scaled by the wrong task count is the whole defect. **So ratifying §6 as written would
bless numbers known to come from a different subject, and `OI-177` would refile itself after the next
run.**

## 1. Method, stated so it can be disputed

`sacct -j <id> --format=JobID,State,Elapsed`, on the `aa67c426` run, **summing `Elapsed` over
DISTINCT task identities** with `.batch`/`.extern` step rows and array-bracket rows excluded.

**Counting `sacct` ROWS instead of distinct task identities inflates the totals** — measured on the
round-2 arms, row-counting reported 447 completions against 374 declared tasks, because `sacct`
returns several rows per identity. Every figure below is a distinct-identity count.

§6's convention is applied unchanged: GPU-partition work in A100-hours (elapsed × 1 GPU/task),
CPU-partition work in CPU task-hours (elapsed × 1 task), auxiliary CPU cores on a GPU allocation not
double-counted. Under that convention both columns are simply summed elapsed hours.

**Every population was complete: 0 non-`COMPLETED` rows in all seven arms, and each task count equals
the declared array.** An actual measured over a short population would understate the budget, so this
is checked rather than assumed.

**Independently reproduced.** The personal-account producer session measured the same seven arms by
its own route and reported the same seven figures to two decimal places. Agreement is not
independence in general, but here the two routes were separate `sacct` queries on the same durable
accounting records, and the agreement is recorded rather than the second measurement being taken on
trust.

## 2. Measured actuals against the current ceilings

| arm | jobid | tasks | mean/task | **measured actual** | §6 estimate (prior) | §6 ceiling | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| 1 bootstrap | `57527866` | 100 | 9.2 min | **15.38 A100-h** | 14.00 | 20 GPU | inside |
| 2 seed split | `57527869` | 24 | 13.6 min | **5.43 CPU-h** | 3.72 | 5 CPU | **OVER by 0.43 (8.6%)** |
| 3 detector | `57527870` | 19 | 43.8 min | **13.88 A100-h** | 14.23 *(24-task prior)* | 20 GPU | inside |
| 4 sweep | `57527874` | 169 | 9.1 min | **25.54 A100-h** | 23.84 | 30 GPU | inside |
| 5 uthrow run | `57527872` | 40 | 46.4 min | **30.94 CPU-h** | 21.38 | 30 CPU | **OVER by 0.94 (3.1%)** |
| 6 uthrow block | `57527873` | 21 | 85.7 min | **30.01 CPU-h** | 22.02 | 30 CPU | **OVER by 0.01 (0.03%)** |
| 7 combine | `57527875` | 1 | 25.4 min | **0.42 CPU-h** | unmeasured | 5 CPU | inside |

**Total overrun 1.38 CPU task-h**, reconciling exactly with `OI-177`'s filed figure.

Note arm 5's prior was **21.38** against a measured **30.94** — a 45% underestimate — and arm 6's
**22.02** against **30.01**. The two largest errors are on the two arms whose priors came from the
plan's own "total" rows rather than from a per-task rate, which is where a population mismatch does
the most damage.

## 3. THE PROPOSED AMENDMENT — for Joseph's signature

**Minimal-change on purpose:** replace the estimate column with measured actuals for all seven arms,
and raise **only the three ceilings that are actually breached**. Arms 1, 3, 4 and 7 keep their
existing ceilings, which the measurements clear.

| arm | measured actual | current ceiling | **proposed ceiling** | headroom | change |
|---|---:|---:|---:|---:|---|
| 1 bootstrap | 15.38 A100-h | 20 GPU | **20 GPU** | 30% | unchanged |
| 2 seed split | 5.43 CPU-h | 5 CPU | **8 CPU** | 47% | **+3** |
| 3 detector | 13.88 A100-h | 20 GPU | **20 GPU** | 44% | unchanged |
| 4 sweep | 25.54 A100-h | 30 GPU | **30 GPU** | 17% | unchanged |
| 5 uthrow run | 30.94 CPU-h | 30 CPU | **40 CPU** | 29% | **+10** |
| 6 uthrow block | 30.01 CPU-h | 30 CPU | **40 CPU** | 33% | **+10** |
| 7 combine | 0.42 CPU-h | 5 CPU | **5 CPU** | very large | unchanged |
| **sums** | — | 70 GPU / 70 CPU | **70 GPU / 93 CPU** | — | CPU +23 |

**Both sums stay far under the delegated thresholds** of strictly-under-500 GPU-hours and
strictly-under-500 CPU-hours, so this remains inside the delegated authority's competence and does not
escalate to a new class of decision.

## 3b. ⚠ THE SECOND SAMPLE ARRIVED AND IT BREACHES THIS AMENDMENT'S OWN ARM-5 CEILING

Measured 2026-08-31 from round 2, which runs the identical launchers at identical populations. §4's
caveat was not caution; it was correct, and it now has numbers.

| arm | aa67c426 mean/task | round-2 mean/task | change | round-2 n |
|---|---:|---:|---:|---:|
| bootstrap | 9.2 min | 8.9 min | −3% | 75/100 |
| seed split | 13.6 min | 14.6 min | +7% | 14/24 |
| **detector** | **43.8 min** | **43.5 min** | **−0.7%** | **19/19 COMPLETE** |
| sweep | 9.1 min | 9.1 min | 0% | 24/169 |
| **uthrow run** | **46.4 min** | **69.5 min** | **+50%** | 13/40 |
| **uthrow block** | **85.7 min** | **99.5 min** | **+16%** | 11/21 |

**The detector arm is complete in BOTH runs at n=19 and agrees to 0.9% — 13.88 against 13.76
A100-h.** So the measurement method is sound and GPU-partition arms are highly reproducible.

**The CPU-partition arms are not.** Projecting round 2 at its observed mean:

- **arm 5 uthrow run: 69.5 min × 40 tasks ≈ 46.3 CPU-h, against this amendment's PROPOSED ceiling of
  40.** It would be **breached by the very next run**.
- arm 6 uthrow block: 99.5 × 21 ≈ 34.8 CPU-h — inside 40.
- arm 2 seed split: 14.6 × 24 ≈ 5.8 CPU-h — inside 8.

**So ratifying this table today would repeat §6's defect, at lower severity but in the same shape:** a
ceiling set from one sample, breached by the next run, and `OI-177` refiles itself. That is the outcome
§4 predicted before the data existed.

**PROJECTION, NOT MEASUREMENT — the honest limits.** Arm 5's figure rests on **13 of 40** completed
tasks, and early tasks in a `%40` array need not represent the whole population. The likely mechanism
for the CPU slowdown is contention: round 2 ran several of our own arms concurrently on shared
partitions, and the queue showed `(Resources)` repeatedly. **That is itself the argument against a
single-sample ceiling** — a budget must survive the scheduler it actually meets, not the quietest run
it was measured on.

**REVISED PROPOSAL for arm 5: 60 CPU-h**, not 40 — about 30% above the round-2 projection of 46.3 and
94% above the `aa67c426` measurement, which is wide but is the only figure covering both observed
regimes. Sums would become **70 GPU / 113 CPU**, still far inside strictly-under-500.

**AND THE RECOMMENDATION IS NOW TO WAIT**, not to ratify either number. Round 2 finishes on its own and
costs nothing to await: this row blocks no gate, and round 2 is running inside the CURRENT §6 ceilings
on every arm except the three already filed. Ratify from n=2 complete populations, not from n=1 plus a
13-task projection.

## 3c. ⚠ THE TWO ARM-5 FIGURES MAY BE TWO SCHEDULER REGIMES, NOT TWO SAMPLES OF ONE QUANTITY

Observed while round 2 finished, and it weakens §3b's projection as much as it weakens §6's prior.

Round 2's throughput over six consecutive hourly reads: **+29, +31, +70, +42, +3, +2** completed tasks.
The +70 hour is when `sweep5dBKGrun`'s `%48` array ran wide; the +3 and +2 hours are the tail, where
`squeue` showed **2 tasks RUNNING** and every remaining task `PENDING` with `Reason=Resources` while
`ArrayTaskThrottle` stood at 40, 10 and 24. **Nothing we control was throttling it — Slurm simply was
not allocating.**

**So elapsed-per-task on the CPU arms is partly a measurement of cluster contention, not of the
work.** `aa67c426` gave arm 5 46.4 min/task and round 2 gave 69.6 min/task; if those two runs met
different scheduler regimes, the pair is not two draws from one distribution and neither the 40 nor the
60 CPU-h ceiling is derived from a stable quantity. **A budget must survive the scheduler it actually
meets** — which argues for the higher figure, not the more precise one.

**The GPU arms are the control that makes this argument checkable rather than rhetorical:**
`det5dBKG` ran 19/19 in both runs and agreed to **0.9%** (13.88 against 13.76 A100-h), and `boot5dG`'s
mean moved only −3%. **GPU-partition arms reproduced; CPU-partition arms did not.** That asymmetry is
what a contention explanation predicts and a work-content explanation does not.

**CONSEQUENCE FOR RATIFICATION.** Ratifying any per-arm CPU ceiling from elapsed time alone bakes a
scheduler snapshot into a budget. Two honest options, neither chosen here: set the CPU ceilings from
the WORST observed regime and say so, or express them in a contention-independent unit — CPU-seconds
of actual work rather than wall-clock task-hours — which would need `sacct`'s `TotalCPU`/`CPUTime`
rather than `Elapsed` and is a change to §6's stated convention, so it is Joseph's call and not a
correction. **`Elapsed` was used throughout this document because it is §6's own convention; that
choice is now a known limitation rather than an assumption.**

## 3d. ✅ n=2 COMPLETE POPULATIONS — the run finished, so this is now ratifiable

Round 2 completed **374 of 374 with zero failures** on 2026-09-01T08:57:51Z
(`RECORD-20260901-k0r2-round2-outcome.md`). Every arm ran its **full declared population in both
runs**, so the comparison below is two complete measurements, not a measurement against a projection.

| arm | `aa67c426` | **round 2** | change | §6 ceiling | §3 proposed | **verdict on the PROPOSAL** |
|---|---:|---:|---:|---:|---:|---|
| 1 bootstrap | 15.38 | **14.86** | −3.4% | 20 GPU | 20 | holds, 35% headroom |
| 2 seed split | 5.43 | **5.83** | +7.4% | 5 CPU | 8 | holds, 37% headroom |
| 3 detector | 13.88 | **13.76** | **−0.9%** | 20 GPU | 20 | holds, 45% headroom |
| 4 sweep | 25.54 | **26.28** | +2.9% | 30 GPU | 30 | holds, **only 12.4%** |
| 5 uthrow run | 30.94 | **49.11** | **+58.7%** | 30 CPU | 40 | **BREACHED — 49.11 > 40** |
| 6 uthrow block | 30.01 | **31.01** | +3.3% | 30 CPU | 40 | holds, 29% headroom |
| 7 combine | 0.42 | **0.58** | +38% | 5 CPU | 5 | holds |

**THE 40 CPU-h FIGURE §3 PROPOSED FOR ARM 5 IS DEAD.** The measured round-2 actual is **49.11**. Had
this amendment been ratified when first written, it would have been breached by the run that was
already executing. §3b's revised **60 CPU-h** survives with 22% headroom and is the figure to ratify.

**§3b's projection was low, and honesty about that matters more than the 6%.** It projected 46.3 from
13 of 40 tasks; the truth is 49.11. Partial-array projections understate here, because the tasks that
complete first are the ones that got nodes first — a selection effect, not noise. **Do not project a
CPU ceiling from a partial array.**

**§3c's contention hypothesis is supported by the completed data.** GPU arms across two runs: −3.4%,
−0.9%, +2.9%. CPU arms: +7.4%, **+58.7%**, +3.3%, +38%. The one arm that moved enormously is the one
whose tail ran at two-way concurrency on `Reason=Resources` for eleven hours. **A work-content
explanation does not produce that split; contention does.** **⚠ §3e sharpens this and partly corrects
it:** the per-task *floor* reproduces to ±6% on every arm with n>1, which is the strong form of the
argument, but `TotalCPU` rose +50.4% alongside elapsed on arm 5 — so this is on-node interference that
*burns* CPU, not queue waiting. Read §3e before citing this paragraph, and do not read arm 6's +3.3%
as reproducibility.

**AND THE CPU SUM NOW EXCEEDS §6's DECLARED TOTAL:** 86.53 CPU-h against a stated sum of ceilings of
70. Every arm remains far inside the strictly-under-500 delegated thresholds, so no authority boundary
moves — but §6's sum row no longer describes this rehearsal and should be restated with the per-arm
figures.

**REVISED RECOMMENDATION, superseding §3b's "wait":** the reason to wait was the absence of a second
complete population. It now exists. **Ratify arm 2 at 8, arm 5 at 60, arm 6 at 40 CPU task-hours**,
restate the estimate column with the round-2 actuals, and restate the sum row as **70 GPU / 113 CPU**.
The one judgement left is arm 4: it holds at 30 with only 12.4% headroom on a rising trend, and this
document still does not propose raising an unbreached ceiling. **Unit per the 2026-09-01 ruling —
task-hours; see §3e, which also records that arm 6's figure is the least well-supported of the
three.**

## 3e. THE UNIT IS RULED, AND §3c's PROPOSED REMEDY IS NOW MEASURED AND REFUTED

**Joseph ruled the unit on 2026-09-01:** *"It is task hours"* — the delegated per-arm ceiling is the
sum of `ElapsedRaw` over the arm's tasks. Recorded by the personal-account orchestrator at
`DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`. **Every figure in this document is
already in that unit** (§1 states the convention at `:36-37`; the table cells write it bare as
`CPU-h`, which is why the question could be asked at all), so the ruling changes no number here. It
changes what they mean, and it is what makes them signable.

**Re-derived independently rather than relayed**, `sacct -X` over jobs `57753239`–`57753248`, all
seven arms, distinct identities only. All three units, so a later lane does not have to ask again:

| arm | AllocCPUS | **task-h (governing)** | core-h (`ElapsedRaw`×`AllocCPUS`) | `TotalCPU`-h (CPU actually consumed) |
|---|---:|---:|---:|---:|
| boot5dG | 32 | **14.86** | 475.64 | 311.74 |
| ssplit5d | 36 | **5.83** | 210.02 | 132.42 |
| det5dBKG | 32 | **13.76** | 440.37 | 70.82 |
| uthrow5d_runF | 50 | **49.11** | 2455.51 | 1528.40 |
| uthrow5d_block | 44 | **31.01** | 1364.33 | 922.64 |
| sweep5dBKGrun | 32 | **26.28** | 840.81 | 529.69 |
| uthrow5d_combF | 50 | **0.58** | 28.82 | 17.99 |

**THERE ARE THREE READINGS, NOT TWO, AND THE RULING SELECTS THE ONLY ONE UNDER WHICH THIS REHEARSAL
WAS INSIDE THE DELEGATION.** The decision record names task-hours and excludes core-hours. It does not
name `TotalCPU` — CPU seconds actually consumed, which is arguably the most literal reading of the
phrase *"CPU-hours"* — and under **that** reading `uthrow5d_runF` at `1528.40` and `uthrow5d_block` at
`922.64` are also over 500, by 3.1x and 1.8x. The ruling's **positive** clause settles it anyway
(*"the sum of `ElapsedRaw`"* admits no other reading), so this is a completeness note and not a
challenge to it. It is recorded here so that a later lane reaching for the literal reading finds it
already answered rather than believing it has found something.

### §3c asked for a contention-independent unit. `TotalCPU` is not one.

`:158` proposed expressing CPU ceilings in *"CPU-seconds of actual work rather than wall-clock
task-hours"* and left it unmeasured. **It is now measured, and it does not work.** Round 1 against
round 2, same arms, same populations, complete in both:

| arm | part | task-h R1 -> R2 | `TotalCPU`-h R1 -> R2 |
|---|---|---:|---:|
| boot5dG | GPU | 15.38 -> 14.86 (**-3.4%**) | 311.93 -> 311.74 (**-0.1%**) |
| det5dBKG | GPU | 13.88 -> 13.76 (**-0.9%**) | 70.57 -> 70.82 (**+0.4%**) |
| sweep5dBKGrun | GPU | 25.54 -> 26.28 (**+2.9%**) | 524.22 -> 529.69 (**+1.0%**) |
| ssplit5d | CPU | 5.43 -> 5.83 (**+7.4%**) | 116.50 -> 132.42 (**+13.7%**) |
| uthrow5d_runF | CPU | 30.94 -> 49.11 (**+58.7%**) | 1015.97 -> 1528.40 (**+50.4%**) |
| uthrow5d_block | CPU | 30.01 -> 31.01 (**+3.3%**) | 848.32 -> 922.64 (**+8.8%**) |

**Arm 5 moved +50.4% in the unit that was supposed to be immune.** A `TotalCPU` ceiling would have
been breached just as badly as an elapsed one, so switching units buys nothing and would cost a change
to §6's convention. **The honest option is the one §3c listed first: set the CPU ceilings from the
worst observed regime and say so.** That is what §3b's 60 does.

### The reproducible statistic is the per-task MINIMUM — and it must not be used as a ceiling

| arm | part | min R1 -> R2 | median R1 -> R2 | mean R1 -> R2 |
|---|---|---:|---:|---:|
| boot5dG | GPU | 8.9 -> 8.5 (**-3.9%**) | -3.6% | -3.4% |
| det5dBKG | GPU | 42.7 -> 41.9 (**-1.9%**) | -0.4% | -0.9% |
| sweep5dBKGrun | GPU | 8.6 -> 8.5 (**-1.4%**) | +2.2% | +2.9% |
| ssplit5d | CPU | 8.4 -> 8.5 (**+0.2%**) | **+22.0%** | +7.4% |
| uthrow5d_runF | CPU | 33.0 -> 34.7 (**+5.2%**) | **+75.1%** | **+58.7%** |
| uthrow5d_block | CPU | 39.4 -> 40.5 (**+2.8%**) | **+56.9%** | +3.3% |

Minutes per task. `uthrow5d_combF` is excluded: at n=1 its minimum *is* its mean, so it carries no
floor statistic — its +36.0% appears in all three columns and is one task, not a distribution.

**Every arm with n>1 reproduces its floor to within +/-6%, in both partitions, while the CPU arms'
medians move by +22% to +75%.** The fastest task in each arm is doing the same work it did before; the
distribution above it is what lengthened. **That is what makes the work-content explanation
untenable** — if each task were doing more work, the fastest task would slow too, and it did not.

**But this REFINES the contention claim rather than confirming the version stated earlier.** §3c and
`RECORD-20260901`:49 argued contention against work-content; the floor evidence supports that. What
the `TotalCPU` growth adds is that the interference **burns CPU** rather than merely delaying the
process — a descheduled task would show flat `TotalCPU` and rising elapsed, and arm 5 shows both
rising together. On a `shared` partition that is consistent with spin/poll or cache interference, not
with queue waiting. **The earlier wording implied waiting. It should be read as on-node interference.**

**The floor is a DIAGNOSTIC, never a ceiling.** A budget must cover the bill actually incurred, which
is mean x n, not min x n. Its use is to answer *"did this arm's work change, or only its
environment?"* — and here the answer is: only its environment.

### One correction to this document's own round-2 reading

**`uthrow5d_block`'s +3.3% is not reproducibility, and §3d should not be read as claiming it is.** Its
two distributions are far apart and their sums coincide: R1 min/median/max `39.4 / 52.2 / 518.3` min
against R2 `40.5 / 81.9 / 289.0`. Round 1's mean was carried by a single 8.6-hour outlier (sd `99.9`
min on a mean of `85.7`); round 2's median is 57% higher with a shorter tail. **Two unstable
distributions that happen to sum alike are not two agreeing measurements** — same shape as this
campaign's *two-quantities-agreeing-at-printed-precision* hazard. The proposed 40 CPU-h still covers
both observed sums (`30.01`, `31.01`), so the recommendation does not change; its **support** is
weaker than §3d implied and a third sample would be worth having before this arm's ceiling is treated
as well-founded.

## 4. What this does NOT settle, and one thing that will improve it

**Arm 4 is the thinnest margin at 17%** and is left unchanged deliberately: it is not breached, and
raising an unbreached ceiling widens an authorization for no measured reason. If a grader prefers
uniform headroom, 32 GPU-h would give arm 4 the same ~25% the others have — flagged as an option, not
proposed.

**Round 2 is running now and will supply a SECOND independent measurement** of the identical arms at
the identical populations. At the time of writing it is 153 of 374 tasks complete with 0 failures. If
these ceilings are ratified today they should be re-checked against round 2's actuals when it
finishes, because two runs of the same arms is a better basis than one — and this document's whole
complaint about §6 is that it generalized from a single prior drawn from elsewhere. **Ratifying on one
run repeats the shape of the defect, at lower severity.** The alternative is to hold `OI-177` until
round 2 completes, which costs nothing: the row blocks no gate, and round 2's arms are running inside
the *current* ceilings by a wide margin on every arm except the three named.

**`OI-177` IS NOT DISCHARGED BY THIS DOCUMENT.** Ratification is Joseph's signature, and the
producing lane that submitted the arms does not grade its own budget.

## 5. ✅ RATIFIED — Joseph, 2026-09-01

> *"I sign"*

His own turn, in response to the recommendation **arm 2 -> 8, arm 5 -> 60, arm 6 -> 40 task-hours, sum
70 GPU / 113 CPU**, put to him together with the disclosure that arm 6's figure is the least
well-supported of the three and that arm 4 was deliberately not proposed for change.

| arm | R1 | R2 | §6 ceiling | **RATIFIED** | headroom /actual |
|---|---:|---:|---:|---:|---:|
| 1 bootstrap | 15.38 | 14.86 | 20 GPU | **20 GPU** | 34.6% |
| 2 seed split | 5.43 | 5.83 | 5 CPU | **8 CPU** | 37.2% |
| 3 detector | 13.88 | 13.76 | 20 GPU | **20 GPU** | 45.3% |
| 4 sweep | 25.54 | 26.28 | 30 GPU | **30 GPU** | 14.2% |
| 5 uthrow run | 30.94 | **49.11** | 30 CPU | **60 CPU** | 22.2% |
| 6 uthrow block | 30.01 | 31.01 | 30 CPU | **40 CPU** | 29.0% |
| 7 combine | 0.42 | 0.58 | 5 CPU | **5 CPU** | 762% |
| **sum** | | | 70 / 70 | **70 GPU / 113 CPU** | |

**Every ratified ceiling exceeds BOTH observed actuals on its own arm**, checked per arm rather than
on the sums, since a sum can hold while a member is breached. `20+20+30 = 70`; `8+60+40+5 = 113`.

**Headroom here is `(ceiling − actual) / actual`, the convention of §3's table.** The `12.4%` quoted
for arm 4 at signature time was `(30 − 26.28) / 30`, divided by the **ceiling** — the same margin on
the other denominator. Both are recorded in
`DECISION-20260901-joseph-ratifies-oi177-per-arm-ceilings.md`; neither changes any decision, and arm 4
was not proposed for change under either reading.

**`PROPOSAL-20260830-forward-only-rehearsal.md` §6 IS NOT EDITED.** That file is `ARCHIVAL`,
`terminal`, `immutable:yes` with 14 inbound references; it stands as the record of what was authorized
on 2026-08-30, and this section supersedes its ceiling columns by reference from 2026-09-01.

**Full record, including what the signature does not reach:**
`DECISION-20260901-joseph-ratifies-oi177-per-arm-ceilings.md`. In short: no gate moves, leg 6 stays
prohibited, no covariance is adopted, no compute is authorized, and these ceilings are set from the
**worst observed regime** rather than from a forecast — §3c and §3e establish that CPU-partition arms
are not reproducible in either elapsed or `TotalCPU` across scheduler regimes, so a third run may
exceed them. That would be a new `OI-*`, not a defect in this signature.
