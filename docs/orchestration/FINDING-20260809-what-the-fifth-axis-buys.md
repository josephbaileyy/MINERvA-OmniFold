# FINDING 2026-08-09 — What the fifth axis buys: W is 69 % redundant with (E_avail, q3), and the residual is measurable

**Why this is its own finding.** It arrived as a by-product of refuting a mechanism (BEN-064), and
it should not stay one. *What does the fifth axis buy?* is a question a referee **will** ask of a
5D analysis, and it is much better measured by us than asked of us. This is that measurement, plus
an explicitly-labelled interpretation of the 4.4 % marginal-vs-independent-4D difference that falls
out of it.

**Status:** measurement VERIFIED-NUMERIC from the frozen 5D product; interpretation labelled as
interpretation and not adopted.

---

## 1. The measurement

W is not an independent coordinate. Kinematically `W² = M² + 2M·E_avail − Q²`, and `q3` constrains
`Q²`, so given `(E_avail, q3)` the physical range of W is narrow. That shows up directly in the
binning of the frozen 5D central product:

**W bins reachable per `(E_avail, q3)` cell**, counted over the whole pT–p∥ plane (6 W bins exist):

```
                       q3 bin ->
      E_avail 0 :  2  2  3  3  3  4  6
      E_avail 1 :  2  2  3  3  3  4  6
      E_avail 2 :  2  2  3  3  3  4  6
      E_avail 3 :  0  1  2  3  3  4  6
      E_avail 4 :  0  0  0  1  3  4  6
      E_avail 5 :  0  0  0  0  0  3  6
      E_avail 6 :  0  0  0  0  0  0  6
```

- **median 3 of 6** W bins reachable per `(E_avail, q3)` cell;
- the zero block is the kinematic boundary, not sparsity — those `(E_avail, q3)` combinations do not
  correspond to physical W;
- per reported 4D cell (i.e. also fixing pT and p∥), **69.3 % — 3345 of 4825 — span ≤ 2 of 6 W
  bins**, and 27.1 % span exactly one.

**So most of the W axis is determined by the other four coordinates.** The fifth axis is not adding
an independent dimension over most of the phase space; it is resolving a residual.

## 2. What that means for the 5D analysis, stated plainly

The honest reading cuts both ways and both halves should be said:

- **Against:** over ~69 % of reported cells the fifth axis has ≤ 2 bins to distribute content
  between, so the marginal information W adds there is small. A referee asking "why 5D?" is
  entitled to this table.
- **For:** the redundancy is *not* total. It is concentrated — the `q3 = 6` column reaches all 6 W
  bins at every `E_avail`, and the high-`E_avail` region is reachable only at high `q3`. The cells
  where W is genuinely free are exactly the high-`E_avail`/high-`q3` corner **where the campaign
  reports its data-minus-generator excess**. The fifth axis buys resolution precisely where the
  physics claim lives, and buys little elsewhere.

That second point is the answer to the referee question, and it is stronger than a generic appeal
to dimensionality because it is specific and checkable from the table above.

## 3. INTERPRETATION (labelled, not adopted): the 4.4 % may measure W's independent content

`FINDING-20260809-stage6-central-gate-cannot-pass.md` records that the 5D→4D marginal and an
independent direct 4D unfold differ by a median of 4.4 % in shape while agreeing to 0.56 % in
normalisation, with four candidate mechanisms excluded and none established.

The redundancy measurement suggests a framing for it, which **Joseph proposed and which is offered
here as interpretation, explicitly not as a result**:

> If W were *fully* redundant with `(pT, p∥, E_avail, q3)`, a 4D unfold and the W-marginal of a 5D
> unfold would be estimating the same object and should agree. They do not agree, at a median of
> 4.4 %. On that reading the disagreement is plausibly **a measure of the independent content of
> W** — the part of the fifth axis the other four do not determine.

**Why it is only an interpretation.** Three things would have to hold and none is established:

1. that the two unfolds differ *only* through W's independent content, rather than also through
   regularisation, binning granularity, or iteration dynamics at different dimensionality;
2. that the difference scales with the *degree* of residual freedom — which is **in tension with the
   measured `n_W` gradient**, since cells with more W freedom agree *better* (Spearman −0.22), the
   opposite of what a naive version of this framing predicts;
3. that the constraint recorded alongside it — the deviation's sign varies across W *within* a cell,
   since it dilutes under summation — is compatible with an "independent content" reading rather
   than with a redistribution the marginal and the 4D handle differently.

Point 2 is the serious one and it is why this is not adopted: the same `n_W` gradient that refuted
the W-mixing mechanism also complicates this framing. Both cannot be waved past. **Recorded so the
idea is not lost and so its obstacle is recorded with it.**

## 4. Rules

1. **Measure what your extra dimension buys before a referee asks.** The answer here took one pass
   over a product already on disk, and it is far better to present the redundancy table with the
   corner where W is free than to have the question posed adversarially.
2. **A by-product that answers a question outside the investigation should be promoted out of the
   finding that produced it.** This spent one revision as a parenthetical inside a mechanism
   refutation, where nobody looking for "what does 5D buy" would ever have found it.
3. **When recording an interpretation, record its obstacle in the same paragraph.** An interpretation
   filed without the measurement that complicates it will be picked up later as though it were
   clean.
