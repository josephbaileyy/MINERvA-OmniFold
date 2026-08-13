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
