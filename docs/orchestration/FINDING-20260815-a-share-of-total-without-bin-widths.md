# A share-of-total computed without bin widths, in a receipt whose own totals are width-weighted

**`BEN-340`.** Peer session B (sparse-edge-cell / tiering lane), 2026-08-15, found while executing the
mediator's dispatch to characterise the 63-cell tail of
`state/p5a-nominal-vs-cstat-family-percell-20260815.json`. **The receipt's author verified it
independently before accepting it and supplied the transferable qualifier in §4.**

Every operand is in `state/RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json`. No point
value is restated here that the receipt does not carry with its derivation (`BEN-227`).

## What happened

The receipt reports two totals and a ratio between them, then says the ratio *overstates* because the two
scalars are on different domains, and offers a **same-domain** ratio in its place. It then reports the
tail's *"share of the cross-section"*.

**Three of those four moves are sound. The fourth is a unit error, and it propagated into a handoff
heading that says `do not re-investigate`.**

- The two headline totals are **width-weighted integrals** — `sum(v·Δp_T·Δp_∥)`.
- The *"same-domain"* ratio is a ratio of **unweighted density sums** — `sum(v)/sum(v)`.
- Both are over the **same 257 cells**. The domain was never the difference; the **bin widths** were.
- The two *"share of total"* figures divide an unweighted density sum by an unweighted density sum,
  **on the family mean rather than on the nominal**, and are presented as shares of the cross section.

`width_weighting_applied = false` is recorded in the covariance artifact, so the arrays are densities and
an unweighted sum of them is not a cross section. The grid's widths span more than two orders of
magnitude (`Δp_∥` from 0.5 to 60 GeV), so nothing about the error is small.

## How it was caught, and this is the part worth keeping

**By trying to re-derive a published ratio from published operands, and failing.** The receipt ships its
per-cell arrays. Reconstructing the nominal from them and summing it two ways gives two different
answers, only one of which reproduces the receipt's own `nominal_total`:

| reconstruction | agreement with the receipt's own `nominal_total` |
|---|---|
| `sum(nom·width)` | `2.9e-5` |
| `sum(nom)` unweighted | **11.3x off** |

The residual `2.9e-5` is itself explained rather than tolerated: it is the 5 flicker cells excluded from
the 257, predicted from the covariance artifact's own `mean` vector and agreeing to **0.7%**. The
extraction's `total_sigma_cm2_per_nucleon` then confirms the same thing at source.

**This is `CONVENTION-receipt-ingredients.md` (`BEN-077`) working exactly as designed** — a verdict-only
receipt would have been unfalsifiable, and nobody suspected a defect. It is the second time in one day
that convention caught something nobody was looking for. **Record it as evidence FOR the convention, not
merely against the receipt.**

## The transferable qualifier: the defect is invisible in a ratio

`sum(nom)/sum(mean)` **looks dimensionally innocent**, because the widths appear to cancel. They only
fail to cancel because the numerator and the denominator **weight the cells differently** — the two
arrays have different shapes over the grid, so a width-free sum is a different linear functional of each.

**So the reasoning that produces this defect is *"it's a ratio, the units drop out."*** That reasoning is
correct for a scalar and wrong for a ratio of sums over unequal bins, and it is why the error survived a
receipt that was otherwise careful enough to flag its own overstatement.

MINERvA's own data release states the same trap from the other side, unprompted
(`2d-unfolding/minerva_paper_anc/README`):

> *"IMPORTANT: All cross sections and uncertainties in these files are differential cross sections and as
> such are divided by bin areas(width). IF you want to make Figures 9 and 10 in the paper you will need to
> remove the area(width) normalization and integrate over the perpendicular axis."*

A published data release considers this worth an `IMPORTANT` block. Treat any density array the same way.

## Rule

**Before dividing two sums over a binned grid, state whether the array is a density or an integral, and
check the denominator you are dividing by is the one you named.** Concretely:

1. **Reproduce a reported total from the shipped per-cell array before quoting any share of it.** If the
   reproduction needs bin widths, every share of that total needs them too.
2. **A "share of the cross-section" must be a share of the object that will be published** — here the
   nominal, not the ensemble mean. The receipt's two shares were computed on the family mean, which is a
   different object from the one the sentence names.
3. **"It's a ratio, units cancel" is not an argument** unless the numerator and denominator weight the
   cells identically. Say which functional each sum is.

## What this finding is NOT

**It does not overturn the receipt's conclusion.** The median per-cell ratio is weighting-independent and
stands; the offset is concentrated rather than global, and the corrected numbers make that case *more*
strongly than the receipt did — dropping the 63 cells moves the width-weighted total ratio to `0.99471`.
**What collapsed is the `3.1%`, the "same-domain" framing, and a handoff heading reading `do not
re-investigate`.**

## The second-order cost, which is why this is filed at finding length

The wrong figures reached **`HANDOFF-20260815-0455Z.md`'s `RESOLVED TONIGHT — do not re-investigate`
section**. A handoff exists so a session that has lost its context can trust it; a wrong *"do not
re-investigate"* is not a wrong number, it is **an instruction not to look**, and it is the cheapest
possible way to make a live defect permanent. Corrected in place there, with the superseded sentence
retained beside its correction per this directory's convention.

**Related:** `BEN-077` (the convention that caught it), `BEN-227` (retract the point value, keep the
derivation — followed here: the two shares are marked `RETRACTED` in the receipt and their corrected
values live with their operands in the correcting receipt), `BEN-228` (the receipt's `OPEN_ITEMS:430-438`
pointer is stale in five artifacts).
