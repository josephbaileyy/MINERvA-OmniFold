# FREEZE 2026-08-30 — the canonical checkout is quiesced for this rehearsal's operand window

**CITABLE FOR:** the rule below and its window.
**NOT CITABLE FOR** any gate movement, submission authorization, or a general policy about the
canonical checkout. Gate 1 is **BLOCK**; Gate 2 remains **FAIL**; no scalar-5D covariance is adopted.

## Authority

Joseph, 2026-08-30, choosing between quiescing the canonical checkout, repointing the operand at a
quiescent tree, or amending `F-17(a)` to treat the canonical `M-4` population as perishable:

> *"Yes do 1 for this rehearsal"*

**The rule text below is this lane's drafting, ratified by him**, in the same shape as
`DECISION-20260824`. He did not type it into the repository. The phrase *"for this rehearsal"* is
his and is load-bearing: **this is not a standing policy.**

## Why it exists

`GATE1-VERDICT-20260830-k0-7ac0edec.md` returned **BLOCK**, 17 PASS / 1 FAIL, on `F-17(a)` alone. The
committed operand recorded the canonical checkout at HEAD `32e403b8`, branch `main`, porcelain
**722**; direct remeasurement found the same HEAD and branch and porcelain **726**. Four entries are
newer than the operand — `dashboard_collector.py`, `dashboard.html`, `test_dashboard_collector.py`
and `state/dashboard/` — written by an unrelated dashboard lane at `06:14:53–06:15:10Z`, 45 minutes
after capture completed. `OI-175` routes it.

**The structural cause, which is the point of this rule:** the deploy tree is frozen and the
canonical tree is not. `F-17` compares a protected subject against an unprotected one that other
lanes actively write to, so **any operand over the canonical side is stale the moment a peer works.**
Retaking without quiescing would reproduce the same failure.

## THE RULE

> **For the k=0 rehearsal `k0-7ac0edec-20260830T000215Z` only, the canonical cluster checkout
> `/pscratch/sd/j/josephrb/MINERvA-OmniFold` is QUIESCED from the start of the F-17 canonical operand
> capture until that rehearsal's submission is authorized or abandoned.**
>
> **No lane may create, modify or delete any path under it that `git status --porcelain` would
> report** — tracked or untracked-and-not-ignored. Committing to the repository from a DIFFERENT
> checkout is unaffected; it is the working tree at that path that must not change.
>
> **Gitignored runtime state is EXCLUDED and may continue.** In particular the waker's
> `state/waker/` ticks, which write every five minutes and do not enter the porcelain population.
> Measured 2026-08-30: `last-tick.json` was the only file written in the preceding five minutes and
> the porcelain count did not move.
>
> **It expires when submission is authorized or the rehearsal is abandoned — not when the capture
> finishes**, because the operand must still describe its subject at `sbatch` time, which is the
> property `F-17(a)` actually tests.

## Enforcement is by convention, and this is said out loud

This is a **prose hold**, preventive by convention and detective by `F-17(a)`. It is not a mechanical
guarantee: nothing prevents a lane from writing, and `F-17(a)` will *catch* a violation rather than
*prevent* it — the same shape `§7.0.19` records about the deployment's position. A hold that exists
only as one lane's intention is not a hold, which is why it is written here and why the peer lane was
asked directly rather than assumed to have stopped.

## Correction to the earlier staleness ruling

`DECISION-20260830-joseph-presubmission-operand-staleness.md` says the ruling accepts that the
operand may *age* but not that its subject may *move*, and then enumerates moves as *"a pull, a
checkout, a branch repoint"* — **all commit-level. That enumeration was incomplete, and this is the
correction.** The commit never moved here; the working tree did, and the operand still stopped
describing its subject. **Read "move" as any change to the porcelain population, not only a change
of HEAD.** The Gate-1 grader applied it correctly against the narrower wording; the wording was this
lane's drafting error, not the grader's reading error.

## What this does not do

It does not retake the operand, unblock `F-17(a)`, move Gate 1 or Gate 2, authorize submission, or
establish policy for any future rehearsal. It makes a correct retake *possible*; the retake, a fresh
Gate-1 grade, and the decisions after them remain to be done.
