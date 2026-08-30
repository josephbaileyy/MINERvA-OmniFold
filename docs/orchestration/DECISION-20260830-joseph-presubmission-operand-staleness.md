# DECISION 2026-08-30 — Joseph: the pre-submission operand's 47-minute age is accepted

**CITABLE FOR:** what "immediately before submission" means for the F-17 pre-submission operand pair.
**NOT CITABLE FOR** any gate movement, submission authorization, or claim about the operand's
content. Gate 2 remains FAIL; readiness and Gate 1 have not run.

## The question, and why it was put to Joseph rather than settled in a commit message

Proposal §3 asks for the canonical operand measured *"as it actually stands immediately before
submission"*. Measured 2026-08-30: producing it costs **46 m 40 s**, because `M-3` runs
`verify_hash_bindings.py` unbounded over the canonical tree's products (`OI-174`). Readiness and
Gate 1 both have to happen after it and will take longer than that. **So by the time submission is
authorized, the operand cannot be "immediately before" anything**, and the phrase has no achievable
reading left.

Three dispositions were put to him: accept the age; re-take the operand after Gate 1 passes; or
freeze the canonical checkout for the window. His words, verbatim:

> *"Do the first, accept it"*

**The scope wording here is this lane's drafting, ratified by him**, in the same shape as
`DECISION-20260824` and today's earlier records. He did not type it into the repository.

## The ruling

**The operand is pre-submission in the sense that governs: it precedes any `sbatch` and it is
committed before one.** That is the property `OI-123` and the forward-only rule actually protect
against — a *reconstruction* of the pre-submission column after the fact. An operand taken early,
committed, and left unmodified is not a reconstruction, and its age does not make it one.

Recorded at `e7a32d72`: `f17a-k0-7ac0edec-20260830T000215Z-{deploy,canonical}.json`.

## What this ruling deliberately does NOT license

- **It does not license re-taking, editing, or regenerating those operands.** If either is replaced,
  the replacement is a new operand with its own commit and the old one stays where it is.
- **It does not license the canonical tree being changed during the window.** The ruling accepts
  that the operand may *age*; it does not accept that its subject may *move*. If the canonical
  checkout is altered before submission — a pull, a checkout, a branch repoint — the operand no
  longer describes the tree that ran, and that is a materially different situation this ruling does
  not cover. **Re-take it in that case, and say why.**
- It does not weaken the post-path half. The comparison still runs against these exact bytes.

## Why it is written down at all

The proposal's phrase is now known to be unachievable as literally worded, and a future lane reading
§3 alone will conclude the sequence was performed wrongly. That is precisely the stale-blocker shape
this campaign has hit five times in a week. This record is the answer such a lane should find.
