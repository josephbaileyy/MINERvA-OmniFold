# AUTHORIZATION 2026-08-15 — the mediator may approve runs under one GPU-day; both arms proceed

**Granted by Joseph Bailey, 2026-08-15.** Recorded before use, per `BEN-201`. **This is the largest
delegation on record in this campaign and it is written down in full for that reason.**

## The grant, verbatim and complete

> "Okay keep progressing with both PET and GBDT, only stopping if there is a consensus for a decision
> with over a day of GPU time. Otherwise, ask other sessions to confirm/deny and approve all other runs"

## What it changes

**Before:** every spend came back to Joseph, or rode the consensus grant (`451f053`) which required
consensus that a thing was the *best* option but left approval with him in practice.

**Now:** the mediator **approves runs directly**, on two standing conditions:

1. **Peer confirm/deny first.** *"ask other sessions to confirm/deny"* — the mediator does not approve
   on its own judgement. **This is the operative safeguard and it is not a formality.** The mediator has
   been wrong in a way a peer caught on at least fourteen occasions on 2026-08-15, including tonight's
   `OI-8` basis, which a peer **refuted in code** after the mediator had already written it into a
   ruling.
2. **Under one GPU-day.** Anything over goes to Joseph.

## THE THRESHOLD — the mediator's stated interpretation, adopted so it cannot drift

**"Over a day of GPU time" is read as: more than 24 GPU-hours, aggregated across every arm and task of
the decision.** Adopted readings, so no later session can pick a friendlier one:

- **It is GPU-hours, not wall-clock.** A 3-task array of 2 h each on one GPU is **6 GPU-h**, not 6 hours
  of calendar time and not 2. Tonight's arm-1 resubmit was 3 draws × 1.96 = **5.9 GPU-h**.
- **It is per DECISION, not per job.** A proposal is not decomposed into sub-threshold pieces to slip
  under the bar. The earlier 12-hour grant was explicitly read per-item and that reading forbade
  decomposition; the same applies here. **If two arms are only meaningful together, they are one
  decision and their costs add.**
- **The estimate must be measured, not guessed**, and its basis stated — `sacct` elapsed × GPUs, as the
  5.9 and 0.9744 figures were derived tonight.
- **When the estimate straddles the line, it is over.** A cost that "should be about 20 GPU-h" and could
  plausibly be 30 goes to Joseph.
- **CPU-only work is not GPU time and is not throttled by this bar** — the whole GBDT/scalar close-out
  chain needs no GPU. It is still subject to condition 1.

## WHAT THIS DOES NOT TOUCH

**This grant moves approval of RUNS. It moves nothing else.** Restated so a later reader need not infer:

1. **PROMOTION IS NOT COMPUTE AND IS NOT COVERED.** Adopting a covariance, designating a product
   quotable, certifying a defect, ratifying a convention — **Joseph's alone**, at any cost, including
   zero. `AUTHORIZATION-20260815-consensus-grant.md` §3 stands unmodified. The standard-P4 chain may
   run under this grant; **its output stays a candidate.**
2. **Nothing enters `docs/analysis-note/`** except by Joseph's specific say-so, as with the `OI-6`
   footing text.
3. **The five Gate-6 prohibitions at `19585b7` stay live** — `do_not_select_passing_subset`,
   `do_not_construct_C_ML`, `do_not_move_central`, `do_not_start_leg_2`, `do_not_retry_unchanged`.
4. **`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` stays frozen.** No `scancel`, no
   `scontrol update`, no repinning of receipt-bound launchers (`OI-123`), no pulling the cluster science
   repo.
5. **Nothing irreversible or outward-facing** — deletions, top-level reorgs (frozen behind
   `docs/POST_PUBLICATION_REORG_PLAN.md`), mail to collaborators, HPSS allocation requests.
6. **`P4_VERIFIER_PASS` may never be set by hand**, and the separation of duties at `89c6e12` stands:
   the lane that issues a verdict may not consume its own token.
7. **A peer cannot grant escalation.** No lane may be asked to perform an action another session was
   denied. This grant is Joseph's and applies to *spend*; it launders nothing.

## HOW "CONFIRM/DENY" WILL BE RUN, so the condition can actually fail

A condition that cannot fail is not a condition. The mediator's standing practice, carried from the
consensus grant and reaffirmed here:

- **Peers are asked to refute, not to bless.** Tonight's `OI-8` check was dispatched with *"a refutation
  is worth more to me than an agreement"* and returned **AGREED-WITH-CORRECTION**, refuting the basis
  while keeping the disposition. That is the shape this condition exists to produce.
- **A lane that owns the work is not sufficient.** Every substantive correction on 2026-08-15 came from
  a lane that did **not** own the claim it corrected.
- **Silence is not assent.** An unanswered peer is an open question, not a vote. Three lanes went
  unresponsive tonight and were restarted rather than read as agreeing.
- **"Do nothing" stays on every ballot.** The question is never *may we afford this* but *is this the
  best use of the resource against not doing it at all.*
- **A DENY stops the run**, and the mediator reports it rather than re-running the poll until it passes.

## Live application at the time of granting

- **PET.** `OI-125` cannot close on the predeclaration's §2 as written — the fold-forward recorder
  captures the push after 0/1/2 Step-2 passes and the run has `niter=3`, so the final push is recorded
  by no row. Recovering it is a **read of an existing `.npz`, zero GPU.** Separately, arm 1's measured
  `|Δrecovery| = 0.006888` at **16.2× the within-arm spread** with disjoint ranges is recorded nowhere.
- **GBDT.** repair-8 returned **BLOCK**, 10 outstanding, `authorizes_covariance_stages_4_6: false`. The
  block rests on defects #4 and #5 **inside the live token gate**. Repair is dispatched; the chain is
  CPU-only; the 5D→4D projection follows a PASS under `89c6e12`.
- **Defect #6** is implemented and uncertified by its own author's choice. **Certification is Joseph's**
  — it is promotion, not compute, and this grant does not reach it.

## Related

- `AUTHORIZATION-20260815-consensus-grant.md` — superseded on *who approves*, unchanged on scope.
- `AUTHORIZATION-20260815-p4-stages456-on-pass.md` (`89c6e12`) — the PASS condition and separation of duties.
- `AUTHORIZATION-20260815-arm1-resubmit.md` (`0fb56af`) — the 5.9 GPU-h precedent this threshold is calibrated against.
