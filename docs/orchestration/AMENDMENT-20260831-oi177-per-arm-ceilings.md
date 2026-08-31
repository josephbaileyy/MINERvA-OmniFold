# AMENDMENT 2026-08-31 — `PROPOSAL-20260830-forward-only-rehearsal.md` §6 per-arm budgets
# PREPARED FOR SIGNATURE. **NOT RATIFIED. `OI-177` REMAINS OPEN.**

**CITABLE FOR:** the measured `aa67c426` actuals in §2 and the method that produced them; the
provenance of §6's current estimate column; and this table AS PROPOSED. **NOT CITABLE FOR:**
ratification — **this document does not amend anything and `OI-177` is not discharged by it**; any
gate movement; leg 6; the M(ii) family; or adoption. **Gate 2 remains FAIL.**

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
