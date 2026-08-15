# AUTHORIZATION 2026-08-15 — standing compute grant, two-key

**Granted by Joseph Bailey, 2026-08-15, in conversation with the personal-account mediator.**
Recorded here because a decision that exists only in a chat transcript is `BEN-201`'s failure shape.

## The grant, verbatim and complete

> "Yes I authorize that and anything in the future that is under 12 hours that the assistant and you agree upon"

The leading "that" refers to the `live-state.json` blocker correction (see the commit landing
`docs/orchestration/state/live-state.json`; five stale fields, three of them false). Everything after
"and anything" is the standing part.

## What it authorizes

**Compute jobs whose cost is under 12 hours, where BOTH the `Assistant` lane and the mediator agree
the job should run.** Either party withholding agreement means it does not run.

## What it does NOT authorize

Read this section before invoking the grant. It was written by the mediator at the time of the grant,
not reconstructed later.

1. **It is a compute-budget grant, not a permission expansion.** It changes nothing about what any
   lane is permitted to touch. Every campaign constraint stands: the frozen
   `/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059`, no `scancel` / resubmit /
   `scontrol update`, no repinning of receipt-bound launchers, no pulling the cluster science repo.
2. **It does not touch the Gate-6 prohibitions** recorded at `19585b7` as `prohibitions_applied`:
   `do_not_select_passing_subset`, `do_not_construct_C_ML`, `do_not_move_central`,
   `do_not_start_leg_2`, `do_not_retry_unchanged`. Those are cited by key precisely so that no
   paraphrase can drop a qualifier. A changed retry remains authorized at `043d572`; an unchanged
   one remains prohibited.
3. **Promotion is not compute and is not covered.** Designating a product quotable, promoting an
   artifact, or ratifying a convention are all outside the grant regardless of what they cost.
4. **Nothing irreversible or outward-facing.** Deletions, top-level reorgs (frozen behind
   `docs/POST_PUBLICATION_REORG_PLAN.md`), and anything leaving this machine — mail to collaborators,
   HPSS allocation requests — remain Joseph's alone.
5. **It is not retroactive** and it does not ratify anything previously declined.

## How the two keys are to be held

**Agreement must be capable of being withheld, or the two-key design collapses into one key.** The
mediator proposes; the `Assistant` lane is expected to object when it disagrees. On the day this was
granted, lanes overturned the mediator four times — on the repair-defect count (six → fourteen), on
the reporting-tier ordering, on the `live-state.json` reword-or-delete framing, and on the claim that
`C_stat` was "verified". That rate is the reason the second key exists.

**Standing decision already inside the grant, deliberately not spent:** arm 1 of the fold-forward
closure (`57012031_[3-5]`, 5.9 GPU-h). Both parties independently recommended against resubmitting
it — nothing lists it as a blocker, and `§6` of its predeclaration bounded it in advance as a
sensitivity to a ~1% rescale. **A budget grant is not a reason to spend.** It stays parked unless the
reasoning changes.

## Related

- `OI-120` — the row that exists because decisions reached Joseph in conversation and nowhere else.
- `CONVENTION-receipt-ingredients.md` — applies to anything this grant funds.
- `docs/OPEN_ITEMS.md` — the costed items still requiring Joseph personally are decisions, not
  compute: `OI-31` (the 1.17 rationale), `OI-29` (collaboration endorsement), `OI-56` (the `E_avail`
  definition), plus `OI-51` / `OI-52` on the separate irreplaceable-data clock.
