# AUTHORIZATION 2026-08-15 — the consensus grant (supersedes the 12-hour grant's ceiling)

**Granted by Joseph Bailey, 2026-08-15.** Recorded before it is used, per `BEN-201`.

## The grant, verbatim and complete

> "Okay I authorize anything for any length of time as long as there is consensus that it is the best option"

## What changed, and what did not

**Changed:** the cost ceiling is removed. The earlier grant
(`AUTHORIZATION-20260815-standing-compute-grant.md`) capped items at 12 h and was read per-item, so
several cheap items summing past 12 h went back to Joseph. **That ceiling no longer binds.**

**Not changed:** every boundary in that grant survives, because this one relaxes *cost*, not *scope*.
Restated so a later reader does not have to infer them:

1. **A compute grant, not a permission expansion.** No campaign constraint moves. The frozen
   `/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` stays frozen; no `scancel`, resubmit, or
   `scontrol update`; no repinning of receipt-bound launchers outside an authorized re-issue; no
   pulling the cluster science repo.
2. **The five Gate-6 prohibitions at `19585b7` are untouched** — `do_not_select_passing_subset`,
   `do_not_construct_C_ML`, `do_not_move_central`, `do_not_start_leg_2`, `do_not_retry_unchanged`,
   cited by key so no paraphrase can drop a qualifier.
3. **Promotion is not compute and is not covered.** Designating a product quotable, promoting an
   artifact, ratifying a convention, or placing text in `docs/analysis-note/` remain Joseph's
   regardless of what they cost.
4. **Nothing irreversible or outward-facing.** Deletions, top-level reorgs (frozen behind
   `docs/POST_PUBLICATION_REORG_PLAN.md`), and anything leaving this machine — mail to
   collaborators, HPSS allocation requests — remain Joseph's alone.
5. **A spec ruling is not a spend.** Where a lane owns a contract, its ruling still gates the work.
   Joseph's authorization covers money, not spec interpretation. `OI-126`'s Track A is blocked on
   Lane C (PET)'s ruling on whether a reduced-n diagnostic is coherent under
   `gate5_cstat_contract.json`, and **this grant does not clear it.**

## The condition IS the grant: "consensus that it is the BEST option"

**Read literally, and this is the mediator's standing interpretation:**

- **"Best", not "acceptable".** The question is never *may we afford this?* — it is *is this the
  best use of the resource, against the alternative of not doing it at all?* **"Do nothing" is
  always on the ballot** and must be costed alongside every option.
- **Consensus must be capable of failing.** If agreement is assumed, the condition is not a
  condition. The evidence that it works is that it repeatedly failed on 2026-08-15: the `Assistant`
  lane refused the mediator's proposed tiebreak; lane B retired its own instrument; lane C refused a
  spec authority it did not hold; lane A retracted a recommendation before it was acted on.
- **The lane that owns the work is not sufficient for consensus.** Every substantive correction on
  2026-08-15 came from a lane that did *not* own the claim it corrected. A proposal endorsed only by
  its author has not met this bar.
- **Silence is not assent.** An unanswered lane is an open question, not a vote.
- **Removing the ceiling raises the bar rather than lowering it.** A grant that makes spending
  easier makes the discipline about spending more important, not less.

## Live application at the time of granting

The decision in front of Joseph when he granted this, with power verified by the mediator against a
non-central t:

| option | cost (both arms) | power if (a) is exactly true |
|---|---|---|
| do not run; Track B publishes the fork stated | 0 | — |
| n=9 | 58.6 GPU-h | **0.566** |
| n=15 | 97.6 GPU-h | 0.828 |
| n=19 | 123.7 GPU-h | 0.914 |

**n=9 was withdrawn by the mediator before this grant.** The sizing rule `t*sd/sqrt(n) < distance`
substitutes true parameters for realized sample ones, which is approximately a **50%-power**
condition, not a power calculation — found by lane B while checking, within a deliberately narrowed
scope, whether its own measured `sd` was being used correctly.

**Two caveats that survive any n**, both from lane B: the boundary is the midpoint of one *measured*
mean (`3.5969`) and one *assumed* null (`1.0`), so if (b) lands near `1.3` the midpoint moves and
power falls on its own; and the tabulated power is for the side that borrows the *Poisson* arm's
spread, the untested arm's being unmeasured by construction.

## Related

- `AUTHORIZATION-20260815-standing-compute-grant.md` — the two-key grant this supersedes on cost.
- `AUTHORIZATION-20260815-oi126-fork-both-tracks.md` — Track A / Track B, and the binding conditions
  on Track A's predeclaration, which this grant does not relax.
- `OI-126` — open. Neither track closes it; Track A is what would.
