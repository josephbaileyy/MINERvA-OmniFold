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

---

# LAUNCH AUTHORIZATION RECEIVED, AND NOT ACTED ON — the premise does not hold (2026-08-13)

Joseph, verbatim via the mediator: **"Launch it"**. Same transcription chain and same
approval-by-reference status as the disposition above; the summary it answers is the mediator's,
`[CLAUDE]`-class, and the mediator has stated that an error in that summary is its own and routes back
through it to him.

**Nothing was submitted. No flag was flipped. No artifact was touched.** Reasons, each measured:

## 1. There is nothing to launch — the annealed production nominal already exists

| evidence | value |
|---|---|
| `pet_fullevent_nominal_weights.npz` | 10,001,677 B, `.done` marked `2026-08-10T18:00:43Z`, job `56563761` |
| `pet_fullevent_floor_weights.npz` | 9,928,916 B, `.done` marked |
| completion receipt | `state/annealed-nominal-complete-56563761.json`, `.accounting.job_id 56563761` |
| arm | `.seed_policy.lr_schedule = fit-time-anneal-after-iteration-0` — **this is the annealed arm** |

## 2. Both launchers would be refused, and the named one was the wrong one

The instruction named `sbatch_pet_fullevent_nominal.sh`, which writes to `fullevent_nominal/`. **Job
`56563092` used exactly that launcher and was correctly refused** — the 2026-08-08 artifact there is
complete, and the driver will not overwrite a finished publication artifact. Its own header:
*"that guard was right and the refusal cost 1:12 instead of destroying the baseline that the
predeclaration, CLM-012's measured values, and the entire shape-validation chain are measured against."*

The annealed arm's launcher is `sbatch_pet_fullevent_nominal_annealed.sh`, and **it would be refused on the
same guard** — `.done` markers present, and it deliberately omits `--allow-overwrite`. **The only way to
force either through is `--allow-overwrite`, which destroys a completed publication artifact. Declined.**

Also, `lr_policy` **has no flag by design** (`sbatch_pet_fullevent_nominal_annealed.sh:52`); the arm comes
from the driver's declared `NOMINAL_SEED_POLICY`. So *"submit on the annealed arm"* was not an available
operation on the launcher named.

## 3. The decisive one — the selected artifact failed its predeclared reproduction test

```
.predeclared_reproduction.nominal.verdict        FINDING_CODE_PATHS_DISAGREE
.predeclared_reproduction.matched_floor.verdict  FINDING_CODE_PATHS_DISAGREE
.scope.artifact_promoted                         False
.scope.recovery_evaluated                        False
.status  COMPLETE_PREDECLARED_FINDING_CODE_PATHS_DISAGREE_NO_DOWNSTREAM
```

With the predeclaration's own formula `dev = (sum_w_push_reco/sum_w_reco)/R − 1`: **`dev = −0.0356090`**
against the predeclared PASS window **`[−0.021724, −0.001724]`** — missing the low edge by **0.0138850**,
where **−0.011724** was expected. Cross-checked against a second instrument: this equals the trajectory
receipt's annealed `iter2` end-to-end figure `0.9643910289626595` exactly.

**Correction against Session A, made before it left the session:** A first computed this as `+0.084053`
by taking `ratio − 1` instead of the predeclared `(push/R) − 1`, which overstates the miss by ~6×. The
error was caught by reading the predeclaration's formula rather than assuming the field was already a
deviation — the same defect class as reading `FIRST_LEG_ONLY` for `end_to_end`, one artifact over.

## So the operation Gate 4 needs is a PROMOTION, not a launch

The annealed launcher states it: *"Whether it ever becomes the canonical nominal is a PROMOTION decision
and Joseph's — he authorized the run, not a promotion."* **And that promotion would make canonical an
artifact carrying an unresolved predeclared finding** — materially different from the summary he answered,
which described training a nominal at *"low and reversible risk."* Training already happened; the exposure
is not a failed job but a canonical nominal with a FINDING on it. **Routed back to him through the
mediator as one question: promote as-is, or resolve `FINDING_CODE_PATHS_DISAGREE` first?** Neither needs a
GPU.

## `nominal_pet_training_allowed` needed no flip and never did

**`True` in all four Gate-4 code-gate receipts** — `20260810`, `20260810b`, `20260810c`, and the newest
`20260812` — since 2026-08-10. `KNOWN_ISSUES-ARCHIVE-2026-08.md` recorded that correction on 2026-08-11.
The `false` claims survive only in prose, **including a `PET_UQ_REMEDIATION_STATUS.md` line Session A
wrote earlier tonight from the status file instead of the gate.** Corrected there, in place, attributed.

## ADJUDICATING `FINDING_CODE_PATHS_DISAGREE` — the anchor is the outlier, and no rerun is needed

The promotion question is *promote `56563761` as-is, or resolve the finding first?* Evidence, all measured:

**There are THREE measurements of `push` on the annealed arm, not two.** The finding was written when only
two existed; the third came from job `56818470`, run 2026-08-12.

| source | `push` | `dev = (push/R) − 1` |
|---|---|---|
| anchor — `fe_s1lr2` `56534117`, **diagnostic wrapper** | 1.1109012166615733 | **−0.0117243** |
| production — `56563761`, **production driver** | 1.0840529523112135 | **−0.0356090** |
| trajectory — `56818470`, **step-1 decomposition harness** | 1.0840529523260116 | **−0.0356090** |

**Production and the trajectory harness agree to `1.48e-11`** — different code, same checkpoints, which is
exactly the comparison the finding names. **The anchor sits `0.026848` away, 1.8 × 10⁹ times that
agreement.** Two mutually-consistent production-path computations against one diagnostic-wrapper
measurement: **the outlier is the anchor, not production.**

**The band's anchor is annealed, so "the band is pre-anneal" is refuted.** `PREDECLARATION-20260810…:34`
names it: *"expected −0.011724 (**annealed arm 56534117**…)"*. What the predeclaration *does* distinguish,
at `:23`, is that the figure comes from a **different job** — the diagnostic wrapper, explicitly contrasted
with *"the production driver"*. The band was anchored on one path and applied to another, knowingly.

**And the band WIDTH is calibrated on pre-anneal scatter.** Its justification (`:39–42`) takes the only
available run-to-run scatter — the 2026-08-08 matched pair, push `0.7367462501305516` vs `0.740546`,
`0.003380` in deviation — and sets `±0.010` at ~3×. **But `push = 0.7367…` is the pre-anneal control
value**, confirmed as the control arm's `push_final` in `56818470`. Measured *annealed* same-path scatter is
`1.26775e-4`, so the band is **79× too wide** for the quantity it now guards, while its anchor is on the
wrong path. The observed gap is **188×** the annealed same-path scatter — systematic, not noise.

**So the finding is probably mislabelled.** Not *"the production path disagrees with itself"* but *"a
frozen band's single-measurement anchor disagrees with two mutually-consistent production-path
measurements."* Different remedies: the first needs a code fix, the second needs the anchor re-derived on
the production path — a predeclaration amendment, not an artifact change.

**Session A's recommendation: RESOLVE FIRST, and do not promote as-is** — not because production is likely
wrong (it is likely right) but because the record would then say *a predeclared check failed and we
promoted anyway*, and this campaign's credibility rests on that never being true. **Re-anchoring a band on
stated evidence is defensible; promoting past a red check is not, even when the check is the thing that is
wrong.**

**What closes it definitively, read-only and with no training:** run the diagnostic wrapper's fold-forward
computation over the **production** checkpoints. Reproducing `1.0840529…` shows the anchor is an artifact
of `56534117`'s own configuration and the band should be re-anchored; reproducing `1.1109…` shows a genuine
two-path discrepancy and promotion would canonicalize one side of it. **Not run — it writes into the
artifact's directory, and that needs authorization.**

### CORRECTION TO THE SECTION ABOVE — the finding was RETRACTED 2026-08-11, and my recommendation is withdrawn

**Session A wrote the adjudication above without opening `INDEX-retracted-and-superseded-values.md`, which
exists for exactly this.** The finding it adjudicates was already refuted on evidence two days earlier:
`535668d` (2026-08-11 05:22, *"RETRACTED: the code-path finding. Production sits inside the diagnostic's own
noise"*), `KNOWN_ISSUES.md:52` entry **41 | TRAP | RETRACTED**, and
`PREDECLARATION-20260810-designA-diagnostic-reproduction.md` §RESULT.

**The evidence, verified here rather than accepted.** Three runs of byte-identical code at identical seeds
through the diagnostic wrapper:

```
56534117  -0.011724321      <- the "anchor"
56586368  -0.007386682
56611394  -0.052174875
mean -0.023761959   sd 0.024701703   range 0.044788193
```

**Production sits 0.48 diagnostic sd from that mean** — recomputed both ways: two-arm mean `−0.0355456`
→ **0.477 sd**; nominal alone `−0.0356090` → **0.480 sd**. (The index's `−0.035546` is the mean of the
nominal and floor arms; A's `−0.0356090` is the nominal alone. Same conclusion either way.) **The
gap-by-denominator history is `188×` → `6.0×` → **`0.97×`** (gap ÷ the three-point diagnostic sd), and only
the last uses a population the anchor belongs to. **CORRECTED 2026-08-13: this read `0.48×`, which is the
*distance from the diagnostic mean* in sd, not a gap-over-denominator figure — `0.023884971 / 0.024701703 =
0.96694`.** Session A repeated the mislabel from `PREDECLARATION-20260810-designA…:116`, whose own line 115
used `0.48` correctly. Both values are real and both are under one sd, so no conclusion moves.**

**MY `79× TOO WIDE` IS THE SAME WRONG-POPULATION ERROR AS THE RETRACTED `188×`.** I divided the ±0.010 band
by the *production* same-path scatter (`1.26775e-4`). But that band guards a comparison against the
**diagnostic** configuration, whose own sd is `0.0247` — so the correct statement is that it was **~2.5×
too narrow**, not 79× too wide. I reproduced the retracted defect one row below the row that names it.
(Separately: the index's *"65× too narrow"* refers to a **different band** — Design A's `3 × 1.27e-4` — so
it never contradicted my figure; I had to read it to know that.)

**AND MY FRAMING WAS WRONG IN A WAY THAT MATTERS.** I called the anchor *"the outlier."* It is not an
outlier — **the configuration has no stable point value at all**, so there is nothing to be an outlier
from. Three identical-seed runs span `0.0448`. `−0.011724321` was one draw from an `sd ≈ 0.025`
distribution and was never a property of anything.

**RECOMMENDATION WITHDRAWN AND REPLACED.** *"Resolve first"* is satisfied — the resolution landed
2026-08-11. **What has not happened is the receipt catching up:**
`state/annealed-nominal-complete-56563761.json` still reads `FINDING_CODE_PATHS_DISAGREE` and
`status: COMPLETE_PREDECLARED_FINDING_CODE_PATHS_DISAGREE_NO_DOWNSTREAM`, with zero mention of the
retraction. **So the credibility argument points at bookkeeping, not at a new measurement:** make the
record say *the check was refuted on evidence and we promoted*, citing `535668d`, the `KNOWN_ISSUES`
entry, the three-run distribution, and A's `1.48e-11` two-path agreement as a complementary line. **That
is applying a documented refutation, not moving a tolerance after seeing a number** — the distinction A
drew, one level up.

**THE WRAPPER RECOMPUTATION A PROPOSED IS DECLINED, and the predeclaration itself declines it:** *"No
fourth run… A fourth run would refine `sd 0.0247` without changing any decision."* Adding a fourth
measurement to a settled question is the audit reflex the redirect was against. **Session A does not
consider the retraction insufficient — only unrecorded.**

**What survives from the section above:** production and the trajectory harness agreeing to `1.48e-11`
across different code paths on the same checkpoints. That is genuinely new tonight and it strengthens the
retraction from a direction the three-run spread does not cover — it shows the production family is stable
to machine precision, so whatever instability exists is entirely on the diagnostic side.

## VL101 — "ARM REJECTED" is on the ledger for the arm this record adopts, and this record omitted it

**Session D's `V23` (`acc4d53`) blocked on the record, not the physics, and it is right.**
`VALIDATION_LEDGER.md:1660` reads, live and unqualified:

```
| VL101 | recovery vs baseline | -0.034249724 | SECONDARY 0.546853 +/- 0.02 | **TRADE-OFF / ARM REJECTED** |
```

**This record adopted the annealed arm and mentioned VL101 zero times, `ARM REJECTED` zero times, and
`SECONDARY` zero times** — measured. It cites `0.546853` once, as full-LR's clearance, **while omitting that
the same comparison is on record as rejecting the arm being adopted.** `VALIDATION_LEDGER.md` is this repo's
canonical home for technote-quoted numbers, so as the record stood, anyone quoting the ledger for the
annealed arm quotes `ARM REJECTED` for it. D's framing: **`BEN-201` run backwards** — there a retraction
reached the index but not the point of use; here a decision reached the point of use but not the ledger, and
this direction is worse because the ledger is what the technote quotes.

**What overrode the SECONDARY reading, stated so the two stop standing silently side by side:** the
PRIMARY/SECONDARY split *was* the predeclared disagreement — `VL100` passes the adopted D2 criterion by
`0.018020876`, `VL101` rejects against the full-LR baseline — and **Joseph resolved it on physics grounds by
selecting the annealed arm.** So `VL101`'s arithmetic stands and its *adjudication has happened*. Neither
the measurement nor the arm is being called wrong.

**And one dependency that is NOT closed, per D:** `VL101` rejects against `0.546853`, the same operand
`56818470` probed. That job returned `REPAIRED`, establishing the sign inversion is a property of the
retired LR policy — **it does not establish that `0.546853` is uninflated.** Different claim, still open.
Not a reason to doubt the number; a reason not to call the SECONDARY comparison settled.

**Ownership note, because it is now structurally unresolvable.** `git blame` on `VL101` returns `1ec042e` —
**Session A's own VL re-id**, which added the leading `| VL101 |` cell to all 108 rows. **So the re-id made
Session A the last toucher of every ledger row and destroyed blame-based ownership for the file.** The
content author, found with `git log -S`, is `3dcb031` (2026-08-10) under the **shared pre-`BEN-160` git
identity** — so no lane can be resolved from history either. That is why this annotation is written by A
rather than routed: the inconsistency is between the ledger and *this* record, ownership is unresolvable in
both directions, and leaving a live `ARM REJECTED` on the adopted arm in the file the technote quotes is the
worse outcome. **Disclosed rather than done quietly.**

## OI-23 — configuration equivalence is ESTABLISHED; the obstacle is elsewhere and larger

D and C both left this UNRESOLVED for want of the cluster receipt: does `56552326`'s configuration match the
adopted nominal in **every** dimension, or only in the LR policy? D warned *"a reviewer checking only the LR
policy finds a match and stops."* Measured field-by-field, `56552326` against `56563761`:

| field | closure `56552326` | nominal `56563761` | |
|---|---|---|---|
| `batch_size` | 512 | 512 | match |
| `epochs` | 8 | 8 | match |
| `niter` | 3 | 3 | match |
| `estimator_seed` | 42 | 42 | match |
| `subsample_seed` | 0 | 0 | match |
| `estimator_fingerprint` | `pet-fullevent-fps-v1` | `pet-fullevent-fps-v1` | match |

**The LR policy matches too, across differently-named fields and a float32 boundary:** closure `base_lr`
`9.999999747378752e-05` = `float32(1e-4)` and nominal `iteration_0` *"two fits at 9.999999747378752e-05"*;
closure `annealed_lr` `1e-05` (float64 literal) against nominal `iterations_1_2` `9.999999747378752e-06` =
`float32(1e-5)` — **the same learning rate, one written as the literal and one as its realized float32.**
Fit counts agree: closure `2 + 4 = 6`, nominal two-plus-four with `records_per_arm: 6`.

**Fields present in only one are structural, not mismatches:** `split_seed: 7` and
`n_injected_rows: 1999920` exist only in the closure **because a closure has an A/B split and an injected
truth tilt and a nominal has neither.** Both carry `engine_edited: False`.

**So D's and C's configuration question resolves in favour of equivalence — and the real obstacle is one
neither of them could see without the cluster: the closure declares itself non-quotable.** Every
`56552326` artifact is prefixed **`NONQUOTABLE-DIAGNOSTIC.`**, and its receipt carries `quotable: False`
with the note: *"SHAPE VALIDATION of the annealed configuration. Threshold NOT modified. A clean result does
NOT authorize editing `omnifold.py` — that promotion is separate and Joseph's."*

**Stated carefully, because this is where over-reach would be easy:** that note scopes the non-quotability
to *not authorizing engine edits or promotion*. **Whether `VL100`'s recovery may itself be technote-quoted
is a question the receipt raises and does not answer** — and it is the PET lane's to answer, not Session
A's. What is now established is that **`OI-23` is not blocked on configuration mismatch**, which is what
both lanes suspected; it is blocked on the quotability status of the artifact that produced the number.
