# DECISION 2026-08-24 — Joseph: eight dispositions on the PET lane's ranked next steps, and MNV_REPO ownership

**Recorded by the OI-126 free-reads lane on 2026-08-24.** This file exists because the ruling
arrived as a chat message relayed through an interpreter session, and `AGENTS.md` holds that a
relayed result is not quotable. Cite this path; do not cite a relay of it.

**THIS RECORD IS A TRANSCRIPTION OF A RELAY, NOT A FIRST-HAND GRANT.** Joseph is away from his
computer and is working through an interpreter session, which he established himself in a direct
turn to this session on 2026-08-23 (*"I will be using the interpreter still"*). That direct turn is
what makes the channel authorized; it does not make the relay first-hand. Anything resting on this
record inherits that qualification.

**Disclosure of interest.** I asked the question this answers, I wrote the ranked list it disposes
of, and item (6) assigns work to me. Item (8) authorizes a measurement I proposed. Nothing below is
my reading of a close call — the ruling is quoted verbatim and my own framings are separated from it.

---

## The ruling, verbatim

> "1. Yes PET should stay closed for now. 2-5. Yes do this. 6. PET mentor can own this. 7. Yes. 8. Yes do this"

The interpreter session supplied this mapping back to the numbered list, which I reproduce because
the ruling's numbers are only meaningful against it:

> (1) PET stays closed, confirmed. (2) add the pre-flight separation check for discriminator tests.
> (3) require a named noise statistic + unit next to every threshold. (4) new hard rule: never
> cancel/resubmit another lane's job without that lane's word. (5) work that must wait gets its own
> branch, not a verbal hold. (6) you personally own the MNV_REPO capture — Joseph is assigning it to
> you directly, so file the committed authorization/decision record naming yourself as owner.
> (7) deprioritize the receipt-hash classification and the GUARDED_LAUNCHERS literal→grep change,
> confirmed. (8) proceed with the permutation ensemble (n≈20-50) for replica_29, understanding it's
> diagnostic-only and does not reopen OI-126.

---

## (1) PET stays closed

`OI-126`'s 2026-08-20 ruling stands. Note the words: **"for now"**. This is a confirmation, not a
strengthening, and it does not add a new bar. Reconsideration still requires estimator-equivalence
**and** coverage, and neither has been tested. Nothing measured on 08-23/08-24 touches either;
cross-node numerical reproducibility is not coverage.

## (2)–(5) Four process rules — landed at `65d37e49`

Landed as **three amendments to existing playbook rules, not four new rows**, and the reason is
mechanical: `PLAYBOOK.md` caps active rules at 25 and `PB-01`…`PB-25` is exactly 25, so a new row
requires retiring one in the same change. `PB-20` independently prefers amendment. Nothing retired.
Evidence and measured operands: `FINDING-20260824-five-rules-from-the-r5-night.md`, `BEN-530`…`BEN-534`.

- (2) and (3) → **`PB-12`** (`BEN-531`, `BEN-530`)
- (4) → **`PB-18`** (`BEN-533`); its instrument half → **`PB-11`** (`BEN-532`)
- (5) → **`PB-18`** (`BEN-534`)

**One extension beyond the literal ruling, flagged as such.** Joseph approved (4) as an authority
rule — never act on another lane's job. I also recorded the *instrument* half on `PB-11`: that ssh
`ControlMaster` multiplexing pins repeated connections to one login node, so a process list answers
about that node while reading as corroborated. `PB-11` already said to use the scheduler; what is new
is why the wrong instrument looked adequate. This is a sharpening of an approved rule, not a new
obligation, and it is separable — strike `BEN-532` from `PB-11` and (4) is still fully implemented.

## (6) MNV_REPO capture — ownership

**Joseph named a role, not a session: "PET mentor can own this."** The interpreter resolved that to
this session. I am recording the resolution and its basis rather than assuming it, because a definite
description re-points and this one is load-bearing for who does the work.

- **Basis for the resolution.** The R5 receipt's `C2_DISCRIMINATOR_20260824` section, written by the
  PET worker lane, credits the no-discriminating-axis observation to *"PET mentor"*. That observation
  is this session's. So in the vocabulary of the lane Joseph has been hearing from, "PET mentor" is
  this session.
- **What would falsify it.** Another session identifying as PET mentor to Joseph. If that happens the
  work below still stands — it is additive and reversible — and ownership transfers by amending this
  file. No measurement depends on which session did it.
- **"Can own" is permissive.** The directive force comes from the interpreter's *"Joseph is assigning
  it to you directly"*, which is relay, not Joseph's words. Both are recorded above so a reader can
  weigh them separately.

**Why this record was the blocker and not the code.** The capture's spec has been complete and
portable since 2026-08-23. It stalled because `minerva-omnifold-9e` correctly declined a *relayed*
authorization and then retired, leaving the item unowned. A committed record removes the dependency
on a message being passed along — which is the failure mode that stalled it — and that is why Joseph
asked for one rather than just naming an owner in chat.

**THIS FILE IS A SHARED PROTECTED TOOL AND THIS LANE WAS PREVIOUSLY TOLD NOT TO EDIT IT.**
`docs/orchestration/state/oi126-successor-iteration-sweep-adjudication-20260823.json:36` says of exactly
this instrument: *"It is a shared protected tool, so proposing it is in scope and editing it is not.
To be routed by this lane; the executing lane was told not to patch it."* Item (6) names this change
in this file, from the authority that boundary answers to, so it **supersedes** that scope line for
this change only. Recording the supersession rather than assuming it, because a later reader meeting
the adjudication record first would otherwise be right to revert this.

**The parity question, measured, because I first stated it wrong.** I flagged this edit as breaking
the `--pair "${GUARD}=nd-unfolding/mnv_guarded_run.py"` check in
`nd-unfolding/pet/sbatch_gate5_data_only_{train,target}_array.sh`. It does not. That check compares
the **cluster working file** to the **cluster tree's own committed blob**, both inside `$CODE_ROOT`;
a local commit is not an operand of it. Measured 2026-08-24: cluster working and cluster committed are
both `sha256 57ba33f8…`, 12808 bytes, at cluster `HEAD b2d7d4ca`, which does not contain this lane's
commits. So those launchers pass today and this change does not alter that. The consequence is
deferred: when the cluster tree is synced to a commit containing this change, the deployed file must
be re-deployed with it — which is the step that launcher's own comment already requires (*"re-deploy,
because a re-deploy is required to get the fix anyway"*). **Syncing or re-deploying the cluster tree
is not authorized by this record and I have not done it.**

**Scope of the authorized change.** Record `MNV_REPO` and **whether it was SET or DERIVED from
`__file__`**, emitted under the existing `[oi136-inv]` stderr channel in `nd-unfolding/mnv_guarded_run.py`,
under the same failure isolation as the rest of that receipt — it must remain unable to change a
run's outcome. Plus tests, including one that fires on the capture's silent absence. This authorizes
no change to the guard's refusal logic, no change to any exit code, and no sweep of the 59 files that
carry the hardcoded root.

## (7) Deprioritized, confirmed

The receipt-hash `kind` classification (`historical` vs `enforced`) and the
`GUARDED_LAUNCHERS` literal→grep change are both deprioritized. The first is all-or-nothing by
construction: a partially classified table is worse than an unclassified one, because an unmarked row
then reads as either. The second remains the ratchet owner's call and is outside every authorization
in this file.

## (8) Permutation ensemble for `replica_29` — authorized, diagnostic only

Authorized at n≈20-50, for `replica_29`, explicitly **diagnostic-only and not a reopening path**.

**Deviation to flag: n=200, not 20-50.** `logits()` is a pure function of the row index, so computing
it once over all rows at each endpoint makes the marginal cost of a draw pure numpy — two forward
passes instead of 2n. A larger n is therefore free and buys the sd to about ±5% instead of ±15%. The
deviation is upward in precision at no cost, and it is recorded in the run's own artifact as a
deviation because it is one.

**What a terminal result there cannot authorize**, stated before the run and carried in the artifact:
nothing about `OI-126`. Row-set sampling of one diagnostic observable at fixed weights is neither
estimator-equivalence nor coverage. No PET covariance may be adopted, paired, or promoted on it, and
a "closed" reading closes an **anomaly**, not the ruling.

---

## What this record does not authorize

Any publication adoption, any pairing of `C_stat`, any construction of `C_ML`, any Gate-6 compute,
submission of the finalize launcher, or a change to `OI-126`'s status. Those remain reserved to
Joseph under `AGENTS.md` and none of them is touched by items (1)–(8).
