# FINDING 2026-08-14 — A matching count is not a matching set, and the match was not even stable

**`BEN-236`.** Constraint from lane B; sizes and set relations measured by lane C (PET).
**Status:** handled in `SPEC-20260814-gate5-cstat-construction-v1.md` `CSTAT-D0f` and `CSTAT-D0f(i)`.
**Evidence:** [`state/gate5-cstat-spec-measurements-20260814/`](state/gate5-cstat-spec-measurements-20260814/)
— `flicker.out` (N=14/18) and `flicker_n50.out` (N=50).

---

## The trap

Two different quantities in this campaign both had **259** cells:

- the **training** artifacts' `reported_bin_mask`, **union** over 50 members;
- the Gate-5 extraction family's **intersection** — cells reported in every member.

**They were never the same 259.** Measured at `N=18`: training-union ⊂ extraction-union correctly, but
the extraction union held **three cells the training union did not** — flat `{254, 281, 284}`, and `254`
was already one of the flickering cells of `CSTAT-D3`.

So a consumer picking whichever mask was at hand *because the count matched* would have been wrong by
three cells, **with every structural check passing**: same length, same dtype, same grid, a covariance
that is symmetric and positive-semidefinite either way. Nothing in the shape tells you.

## And the training mask is not even a constant

Measured across all 50 training artifacts, `reported_bin_mask.sum()` takes **three different values**:

```
{257: 3 members, 258: 21 members, 259: 26 members}    union 259, intersection 256
```

So "the training mask is 259 cells" is its **union**, or equivalently its modal value — not a property
of the object. That makes it the fourth per-member-varying mask in this campaign, alongside `BEN-231`'s
reporting mask, `n_cells_populated` (260/261/262), and `n_cells_masked_zero_acceptance` (2–6).

## The part that makes this more than a coincidence: the match dissolved

**Re-measured at 50/50 on 2026-08-14, the extraction intersection is 257, not 259.**

| | `N=14` | `N=18` | **`N=50`** |
|---|---|---|---|
| extraction union | 262 | 262 | **262** |
| extraction **intersection** | 259 | 259 | **257** |
| training-mask union | — | 259 | **259** |
| counts collide? | — | **yes** | **no** |

**The numeric match was `N`-dependent.** It held while the family was partial and dissolved as members
accumulated, because the intersection shrinks whenever any new member fails to report a cell — the
flicker set grew from 3 cells to 5 (`209` at 47/50, `254` at 44/50, `255` at **24/50**, `256` at 49/50,
`281` at 49/50).

**So the failure mode is worse than "two things happen to have the same size."** Anyone who had equated
the two sets *because the counts agreed* would now hold a domain that silently changed under them, and
**nothing would have raised an error at any point** — not at the moment of the wrong equation, and not
at the moment the ground moved. A count that matches is not evidence today, and it is not even a stable
non-evidence.

Note also that `281` — newly flickering at 50/50 — is one of the very three cells that distinguished the
two masks at `N=18`. The cells where two reporting domains disagree are the same cells that flicker,
which is not a coincidence: both are the thinly-populated edge of the grid.

## The rule

**`CSTAT-D0f(i)`, in the spec as a prohibition rather than advice:** a consumer MUST identify a
reporting domain by **set identity** — `np.array_equal` against the named mask, or the
`layout_fingerprint` of `CSTAT-R6` — and MUST NOT select, match, or validate one by `n_reported`,
`sum(mask)`, `len(indices)`, or `sum(diag > 0)`. A receipt that reports a mask MUST publish the mask or
its fingerprint, **never only its size.**

And B's original constraint stands, adopted: **no consumer may take a training artifact's
`reported_bin_mask` as the reporting domain.** The reason is now sharper than when B gave it — not
merely that it is a different object, but that it is a *varying* one whose summary statistic collided
with another object's summary statistic for a stretch of the campaign.

## Why this is the same class as the covariance itself

This is `D`'s result about scalar summaries, one level down. There, agreement between two
implementations on a scalar proved nothing about the object. Here, agreement between two *masks* on a
scalar proved nothing about the domain — and in both cases the summary was the only thing anyone
compared, because it was the only thing cheap to compare.

The generalisation worth keeping: **when a check compares a summary, ask what the summary integrates
away.** For `n_reported` it is *which cells*. For the fold-forward `dev` of `CSTAT-O4` it is *where in
the grid* (`pet_diagnostic_quarantine.py:104-120` forms it from two sums over the whole reco leg). Both
were caught the same way — by someone computing the thing the summary had discarded.
