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
