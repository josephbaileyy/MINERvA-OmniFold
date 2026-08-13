# AUTHORIZATION RECORD — Gate-4 estimator disposition: the ANNEALED arm (2026-08-13)

**Why this file exists, given the standing instruction to stop producing artifacts.** Joseph's redirect
tonight was *"no new receipts, findings, or convention documents unless a gate requires the artifact."*
**Gate 4 requires exactly this one.** Its blocker text, verbatim from `PET_UQ_REMEDIATION_STATUS.md`:
*"Gate 4 remains blocked on Joseph's explicit estimator disposition and subsequent nominal-launch
authorization."* This record **is** the first of those two, so writing it is gate work rather than beside it.
Nothing else is being written up.

## The authorization, verbatim and complete

> Okay do the annealed

**Transcription provenance.** Transcribed by `personal-orchestrator`, session
`5f7d4b75-b1dd-4c6e-8f95-912b3b045c66`, from Joseph's typed message immediately preceding its dispatch —
no intermediate storage, no paraphrase step. Session A copy-pasted the block and **cannot see the
original**; it attests only that the text above matches the message it received. Same chain and same
division of attestation as the three 2026-08-12 receipts.

## THIS IS APPROVAL BY REFERENCE. THE PHYSICS ARGUMENT IS NOT HIS.

His four words carry his authority. **They do not carry the reasoning.** He asked what action made most
sense from a physics perspective; the argument below is the **mediator's**, marked `[CLAUDE]`-class by its
own declaration, and he **endorsed** it rather than authored it.

**Consequence, stated so no lane resolves it locally:** if the argument turns out to contain an error, the
error is the mediator's, and the disposition routes back through the mediator to Joseph rather than being
re-decided by a lane.

### The referent — `[CLAUDE]`-CLASS, reproduced as he read it

> Take the annealed arm. Tail collapse means the classifier loses the ability to express large likelihood
> ratios — weights pulled toward unity. The Gate 7–8 systematic universes *are* shape perturbations, so a
> suppressed-response estimator pulls every universe toward nominal, shrinking the spread and therefore the
> covariance. The covariance is the deliverable. The asymmetry decides it: full-LR wrong means systematics
> understated across ~100 universes, unbounded and invisible until review; annealed wrong means 6% less
> recovery on one closure, bounded and visible. Recovery is measured against one *known* injected reweight;
> the publication faces unknown data and many unknown shape perturbations.

## WHAT THIS SETTLES, AND WHAT IT EXPLICITLY DOES NOT

**Settles — the estimator disposition.** The **annealed** arm is selected. This retires the predeclared
disagreement standing since 2026-08-10.

**Does NOT settle — the nominal-launch authorization.** Gate 4 names **two** requirements and this is the
first only. *"Do the annealed"* selects an arm; **it is not permission to launch training.**
`nominal_pet_training_allowed: false` **stays false.** The mediator is putting the launch question to him
separately. **No lane may read this record as a launch authorization**, and Branch C stays closed.

**Does NOT jump Gate 2's promotion.** Gate 2 is a prerequisite, not a parallel track. As of this record:
requirement 2 (ledger + RUN_LOG + STATUS) is **committed by Session C** — `STATUS` now reads *"Current
(2026-08-13): RE-ISSUED AND PASSED under D1/D2. Runtime PASS; independent review is the only open
promotion requirement."* Requirement 1, **independent receipt review, is open and assigned to Session D**
and **is not waivable** — a lane cannot review the gate it is promoting, and `CLAUDE.md` states that worker
agreement is not verification.

## THE MARGIN HE WAS SHOWN — carried forward because it is what will bite later

Re-derived in this turn rather than quoted:

| quantity | value |
|---|---|
| adopted D2 criterion | `0.80 × 0.618228` = **`0.494582`** |
| full-LR recovery | `0.546853` — clears by **`0.052271`** |
| annealed recovery | `0.512603276` — clears by **`0.018021`** |
| annealed below full-LR by | `0.034250` |

**He chose the thinner margin knowingly.** The mediator states it put these numbers in front of him
explicitly, as the counterweight, and he chose the annealed arm anyway. **Recorded so that if the annealed
recovery later drifts downward, it is clear this decision was made with the margin visible rather than in
ignorance of it.** The annealed arm has roughly **2.9×** less headroom above the criterion than full-LR.

## JOB `56818470` IS NOW INFORMATIONAL, NOT DECISIVE

The annealed step-1 trajectory job was submitted to *inform* this choice. **The choice is made, so nothing
waits on it.** State at the time of writing: `RUNNING` since `2026-08-12T18:00:43`, 4 h limit, `nid008264`.

**How to read its return, predeclared here so a convenient reading cannot be adopted later:**

- Its own `PREDECLARATION-20260811-annealed-step1-trajectory.md` names **UNRESOLVED as the most likely
  single outcome** — specifically domain-of-validity failure, where near `push ≈ R` the required correction
  goes to 1 and sign stops discriminating, returning *no information* rather than *pass*. **An UNRESOLVED
  return is therefore not a problem and must not be reported as one.**
- **If it returns something that CONTRADICTS the annealed choice, that is a real finding** and goes straight
  to the mediator and to Joseph. Anything else is a note.
- Read on `end_to_end_achieved_over_required` and `end_to_end_sign_is_wrong` — **not** on
  `r1_achieved_over_required_FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE`, which the existing `56525829` ledger row
  quotes under a like-for-like heading (`BEN-077`'s class).
- **If Arm 1's reproduction gate fails** (`rel_dev > REPRO_RTOL = 0.02`), **Arm 2 is not read at all**,
  whatever it printed.
- **Materiality floor:** `REPRO_RTOL` is `0.02` and the best-epoch-vs-final checkpoint gap is ~1.3%
  (`BEN-043`), so no sub-2% difference between arms is claimable as an effect.

## Corroboration noticed rather than arranged

The Gate-2 runtime receipt's `R = 1.1240802949941018` is **the same operand** the trajectory
predeclaration quotes as `1.1240803` for the annealed arm's no-information proximity — two documents
written days apart, one number, reconciling. That is independent support for the `w_reco` denominator from
a direction nobody set up.

## Not authorized by this

Launching nominal training. Any Gate-4 promotion. Any engine edit. Any cluster P4 run — Joseph's hold
stands and `p4_evidence.py:25` still reads `REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"`, measured
this turn. Any move, deletion or new archiving on HPSS — that decision is closed in favour of the
allocation increase.

---

# RESULT — job `56818470` returned **Branch REPAIRED**, and it corroborates the disposition (2026-08-13)

`COMPLETED`, exit `0:0`, elapsed `00:21:05`, `nid008264`. The reading below applies the branch set
predeclared above, in its prescribed order, **before** looking at the arm's own verdict string.

## Gates first, because they license reading anything else

| gate | result |
|---|---|
| **Arm 1** reproduction (`increment1`, `push_prev`, `push_final`) | **PASS — `rel_dev = 0.0` on all three**, bit-exact against the committed `56525829` receipt |
| **Arm 2** reproduction | **PASS — `rel_dev = 0.0` on all three** |
| **Gate A** | `A1_mc_indices_bit_exact: true` (0 differing rows), `A2_truth_norm_bit_exact: true` |
| **Gate B** | `Bi_pass: true`, `rel_dev` 0.0 at max/median/p90/p99; `Bii_off_shell_exactly_one: true`, 72 off-shell of 1,999,928 |
| overall | `verdict: GATE_AB_PASSED` |

So UNRESOLVED cases 4 and 5 do not fire, and Arm 2 may be read.

## The predeclared fields, both arms

| arm / iteration | `e2e/required` | abs dev | `end_to_end_sign_is_wrong` | abs(`r1_required_mean` − 1) |
|---|---|---|---|---|
| **control** iter0 | 0.9721159 | 0.0279 | False | 0.1241 |
| **control** iter1 | 0.8608448 | 0.1392 | **True** | 0.0287 |
| **control** iter2 | 0.6554214 | 0.3446 | **True** | 0.1616 |
| **annealed** iter0 | 1.1100740 | 0.1101 | False | 0.1241 |
| **annealed** iter1 | 1.0329083 | 0.0329 | False | 0.0992 |
| **annealed** iter2 | 0.9643910 | 0.0356 | False | 0.0319 |

**Domain of validity holds everywhere** — no iteration in either arm has `|r1_required_mean − 1| < 0.02`
(closest is control iter1 at 0.0287). **So the predeclared most-likely outcome did NOT occur**, and the
criterion carries information at every point read.

**Iteration indexing resolved from the predeclaration rather than assumed:** line 41 names the checkpoint
inventory `iter0/1/2`, so *"both iterations 1 and 2"* means **iter1 and iter2**. `iter0` is excluded by
design — the defect was localized to *"iteration dynamics after initial feedback."*

## Verdict: **Branch REPAIRED**

`end_to_end_sign_is_wrong == False` at iter1 **and** iter2, with absolute deviation of **0.0329** and
**0.0356**, both inside the 0.10 tolerance and both above the 0.02 materiality floor.

**The control earns the contrast rather than assuming it:** the pre-anneal arm inverts at iter1 and iter2
and degrades monotonically (0.972 → 0.861 → 0.655). The annealed arm never inverts and stays within 3.6%
(1.110 → 1.033 → 0.964). Predeclared reading: *the dead LR anneal was the dominant mechanism of the Branch
C defect, and the defect is a property of the retired LR policy rather than of iteration dynamics as such.*

**This CORROBORATES the annealed disposition.** It was predeclared as informational, not decisive, and it
did not contradict — so it escalates as a note, not as a finding.

## THE HONEST TRADE, which a REPAIRED headline would hide

**The anneal fixed the inversion and made `iter0` worse.** Control iter0 deviates by **0.0279**; annealed
iter0 by **0.1101** — **3.95×** worse, and outside the 0.10 tolerance the later iterations clear. That is
the arm's own verdict, `UNDER_ACHIEVES_AT_ITER0_SAME_SIGN`: *"step 1 under-achieves at iteration 0 but with
the CORRECT sign, so the sign inversion is an iteration effect layered on a step-1 capacity/convergence
shortfall present from the start."* Both readings are true and neither supersedes the other: **the sign
inversion does not survive the anneal; a step-1 capacity shortfall at iter0 does, and is larger.**

Had `iter0` been inside the REPAIRED criterion, this run would have returned UNRESOLVED case 2.

## THE PREDECLARATION EARNED ITS KEEP, and this is the measurable part

Reading the **forbidden** field flips the verdict on the same data:

- `r1_achieved_over_required_FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE` at annealed **iter1 = 1.1811038** →
  absolute deviation `0.1811 > 0.10` → **UNRESOLVED case 2.**
- `correction_sign_is_wrong` at annealed **iter1 = True** → reads as **PERSISTS.**

Both are in the same receipt, one line from the correct fields. **The predeclaration named
`end_to_end_*` as load-bearing two days before the data existed, and named the first-leg field as the trap
because the `56525829` ledger row quotes it under a like-for-like heading (`BEN-077`).** Without that, the
most natural field to read gives the opposite answer.

## DOMAIN-OF-VALIDITY GUARD, MEASURED FROM THE FIELD — REPAIRED stands, and the proxy inverted the comparison

Session D challenged the verdict (`V22`, `e41e760`), correctly identifying that the check separating
REPAIRED from UNRESOLVED is **not** the iteration indexing but **UNRESOLVED condition 1** — any iteration
with `|r1_required_mean − 1| < 0.02` returns *no information*. D could not read the field (receipts are on
`/pscratch`) and said so, using `R/push` as an explicit proxy. **Measured from the field, per iteration:**

| arm | iter0 | iter1 | iter2 | tightest | clears 0.02 by |
|---|---|---|---|---|---|
| control (pre-anneal) | 0.1240803 | **0.0286840** | 0.1616496 | iter1 | **1.434×** |
| annealed (treatment) | 0.1240803 | 0.0991592 | **0.0318599** | iter2 | **1.593×** |

**All six iterations clear the threshold. UNRESOLVED condition 1 does not fire, and `REPAIRED` stands on
its own predeclared terms.** The margin D asked to have published beside it: **1.593×** on the deciding
iteration (`iter2`), and `4.958×` at `iter1`.

**And the comparison inverts.** D's reading was that *"the anneal moved this measurement an order of
magnitude closer to the point where its own criterion stops discriminating"* — 1.85× on the promoted arm
against 26.3× on the retired one. **From the field it is the opposite: the annealed arm's tightest
iteration is FARTHER from the no-information point (0.0318599) than the control's tightest (0.0286840).**
The arm being retired was the tighter one.

**Why the proxy failed, and it is `BEN-077`'s shape applied to D's own instrument.** `R/push` is an
aggregate over the whole trajectory; `r1_required_mean` is per iteration. The two diverge, and **they
diverge by different amounts on each arm** — the proxy overstates the control's clearance by **18.3×**
(26.287 against 1.434) and the annealed arm's by only **1.16×** (1.846 against 1.593). A proxy that is
wrong by unequal factors on the two things being compared does not merely add noise: **it reverses the
ordering.** D flagged it as a proxy rather than the field, which is the only reason this was catchable.

**One correction against Session A, which D found:** A cited *line 41* for the `iter0` exclusion. Line 41
is a checkpoint-**inventory** row in the two-artifact comparison table and carries no scope claim. **The
exclusion is at line 70** — *"Branch REPAIRED — for both iterations 1 and 2"* — with its rationale at
lines 8–9 (`56525829` localized the defect to iteration dynamics *after initial feedback*). D also
established the predeclaration predates the result by **26 hours** in a single never-edited commit
(`831043d` 2026-08-11 18:31:53 −0400 against submission `02dfb68` 2026-08-12 20:39:52 −0400). **So the
exclusion is a predeclared scope boundary, not an interpretation** — better supported than A claimed, from
a different line than A cited.

**Unchanged: annealed `iter0` at 0.1101 is a real trade and outside the predeclared scope.** Both remain
true.

### Structural corroboration of the table above — Session D's check, verified exactly

D supplied an analytic check neither of us had run, and it matters because the table is now load-bearing
for the disposition. **At `iter0` there has been no reweighting, so `push = 1` and `r1_required_mean` must
equal `R` exactly — and identically in both arms.** Measured:

| check | result |
|---|---|
| `r1_required_mean[iter0] == R`, control | **True**, bit-for-bit |
| `r1_required_mean[iter0] == R`, annealed | **True**, bit-for-bit |
| `R` identical across arms | **True** |
| `iter0` field identical across arms | **True** |
| `R − 1` vs `abs(field − 1)` | equal bit-for-bit, **0 ulps apart** |

D estimated 1 ulp from float64 cancellation in its own subtraction; measured, it is **0** — the values are
exactly equal. **Two arms agreeing bit-for-bit at the one iteration where they analytically must is an
independent witness that these are per-iteration field values rather than a summary broadcast across
iterations** — which is precisely the failure the proxy above suffered from.

**D's reframing of the lesson, adopted because it is better than Session A's.** A had it as *"the label is
what made this catchable."* D corrected that against its own credit: it could not reach `/pscratch`, so
UNRESOLVED was the only honest verdict available — the label was not evidence of care. **The generalisable
form is: a proxy stated as a proxy costs one command to refute; a proxy stated as a measurement costs a
retraction.** D got the cheap failure because the expensive one was not available to it.
