# A deletion can retroactively break BEN-077 for an artifact that was compliant when written

**Mediator, 2026-08-18. `BEN-306`.** `CONVENTION-receipt-ingredients.md` requires every derived quantity in a
receipt to ship its ingredients, so the reported numbers can contradict each other. **The convention says
nothing about deletion**, and checked at HEAD it contains no occurrence of *delete*, *purge*, *retain*, or
*retention*. That omission is not cosmetic: a receipt is checked **when written**, and a purge happens **later**,
so nothing in the convention's own enforcement window can see the failure this finding names.

## The instance

The M(ii) scan retains three products per member (4.46 GB) and releases a 41.44 GB intermediate,
`uq_universe_5d_covariance_combined_bkgaware.root`. The release was ruled on the finding that *"the bar's
operands live downstream of the intermediate, in the retained 892 MB adopted roots."*

That sentence is true of one operand and false of the other:

| scalar | ingredient | ingredient retained? |
|---|---|---|
| `sqrt_tr_new` | `hCov_combined5d_total_uthrow` | yes — in the retained 892 MB root |
| **`sqrt_tr_old`** | **`hCov_combined5d_total`** | **no — only in the released 41.44 GB intermediate** |

`sqrt_tr_old = 4.357790406860002e-38` is the **predeclared bar's operand**. Verified at `origin/main`:
`adopt_unified_5d.py:124-127` opens `args.combined`, reads `hCov_combined5d_total`, and forms
`sqrt_tr_comb = sqrt(trace(C_new))`; `sbatch_adopt_stamped_footing.sh:33` sets `COMBINED` to the intermediate.

So after the deletion the **scalar survives and its ingredient does not**. A receipt that shipped its
ingredients becomes a verdict-only receipt — permanently, silently, and after it passed every check that
existed to catch exactly that.

## The general defect

> **A retention policy must be tested against every derived quantity that SURVIVES the deletion, not against
> the ones the deletion is for.**

The question asked was *"are the bar's operands downstream of the intermediate?"* — yes. The question not asked
was *"are the surviving scalars' ingredients downstream too?"* These are different questions, and **only the
second is about deletion.** The first is about what the deletion is *for*; the second is about what the
deletion *does to everything left behind*.

## Why it is a convention gap and not a scan bug

`BEN-077` is enforced at write time. A purge is a later, separate act, usually by a different party, often for
storage reasons unconnected to the receipt. There is no point in the convention's lifecycle at which the
question above is asked, and the artifact that becomes non-compliant is **not modified** — its bytes are
unchanged and it still validates against itself. Only its *derivability* is destroyed, and nothing re-checks
that.

This generalises past M(ii): any campaign that publishes a receipt and later reclaims storage can walk into it.

## The remedy, and why it is cheap here

`trace(C) == sum(diag(C))`, so shipping `diag(C_old)` makes the operand recomputable forever.
**`adopt_unified_5d.py:128` already computes it** — `diag_comb = np.clip(np.diag(C_new), 0, None).copy()`, in
memory at the moment `sqrt_tr_comb` is formed. So the remedy is a **write, not a computation**, and not even an
extra read of the 41 GB file. With the two adoption operands it is 3 × 65,856 doubles = **1.58 MB**, 0.035% of
a retained member, against 41.44 GB released — a 26,219:1 trade.

**Ruled as a sequencing constraint rather than a reversal:** nothing is deleted before the survivors'
ingredients are retained elsewhere.

## Two riders that came out of the same review

- **A release must enumerate every reader, not only those on the workflow's own path.** A third consumer of
  `hCov_combined5d_total` exists at `p4_build_components.py:114`. It turned out to be unaffected — because the
  release covers *member* intermediates and the archive's copy is frozen — but that was **luck**, not analysis.
- **Scope ambiguity is itself the hazard.** "Delete the 41 GB file" was readable as touching the archive. It
  was not intended that way, and the clarification had to be issued separately. A release rule must name the
  instances it releases, not the filename.

## Attribution

The instance was found by lane B, **by writing the comparator** — reading had not found it, and this is the
fifth time in one session an instrument found what inspection could not. The generalisation above is lane C's,
which also declined to split the blame and identified the unasked question as its own. **The defective report
that carried "the operands are downstream" without distinguishing the two operands was mine** — a property of a
pair asserted where it holds of only one member of it, which is `BEN-305`'s relay defect in a new form: not an
unverified claim forwarded, but a *verified* claim forwarded at the wrong granularity.

## Related

`BEN-077` (receipt ingredients — the convention this extends), `BEN-305` (a relay launders a hypothesis into a
campaign fact), `BEN-072` (the ingredient was there and nobody compared it — this rule failing in the other
direction).
