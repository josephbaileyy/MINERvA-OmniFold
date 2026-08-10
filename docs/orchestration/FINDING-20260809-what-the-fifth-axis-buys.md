# FINDING 2026-08-09 — What the fifth axis buys: W is 69 % redundant with (E_avail, q3), and the residual is measurable

**Why this is its own finding.** It arrived as a by-product of refuting a mechanism (BEN-064), and
it should not stay one. *What does the fifth axis buy?* is a question a referee **will** ask of a
5D analysis, and it is much better measured by us than asked of us. This is that measurement, plus
the disposition of the 4.4 % marginal-vs-independent-4D difference that falls out of it — which,
as of 2026-08-10, is axis-dependence, with the interpretation that once accompanied it retired.

**Status:** measurement VERIFIED-NUMERIC from the frozen 5D product. The interpretation this
finding originally carried is RETIRED (§3); the axis-dependence result (§3b) replaces it.

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

## 3. RETIRED: "the 4.4 % measures W's independent content" (proposed, tested, dropped)

**The candidate is gone; the record of the attempt stays.** It was carried for one revision as a
labelled, unadopted interpretation. That was the wrong disposition — a half-alive hypothesis sitting
in a document is one a future reader promotes — so it is deleted rather than qualified.

**What it said.** If W were fully redundant with `(pT, p∥, E_avail, q3)`, a 4D unfold and the
W-marginal of a 5D unfold would estimate the same object and agree. They differ by a median 4.4 %,
so the difference might *measure the independent content of W* — the part the other four
coordinates do not determine.

**Why it is dropped.** Two obstacles, and no successful prediction to set against them:

1. **The `n_W` gradient.** Cells with *more* W freedom agree *better* (Spearman −0.22, monotone from
   0.0572 at `n_W=1` to 0.0190 at `n_W=5`). A reading in which the difference measures residual
   freedom predicts the opposite sign.
2. **The axis ordering (§3b), which is decisive.** `q3` is *strongly* constraining of W — the
   redundancy table in §1 is a kinematic triangle precisely because `(E_avail, q3)` fixes W's
   range — so `q3` is itself highly non-redundant. An independent-content reading therefore predicts
   that dropping `q3` should cost **at least** as much as dropping W. **Measured, it costs half:
   2.30 % against 4.43 %.** The prediction is not merely unsupported, it is inverted.

An interpretation that has been contradicted twice and has never predicted anything correctly is not
a live hypothesis. **Retired 2026-08-10.** The measurement in §1 stands on its own and does not
depend on it; §3b's axis-dependence disposition is what replaces it.

## 3b. MEASURED 2026-08-10: it is AXIS-dependence, not dimension-independence

The §3 interpretation was tested by measuring a second marginalisation rung from products that
already existed. **No new production was run, and none should be:** a third rung costs a run and
changes no adopted result.

| rung | axis dropped | median \|rel\| | integral ratio |
|---|---|---|---|
| 5D → 4D | **W** | **4.4282 %** | 1.005578 |
| 4D → 3D | **q3** | **2.2972 %** | 1.000258 |
| 3D → 2D | eavail | ~4.4 % *(quoted at `sec_3d.tex:81`; a "per-bin scatter", **not** recomputed as this statistic)* | — |

Generator: `runs/standard-p4-verifier/20260810T0700Z-marginalisation-ladder.py`, reading
`products/5d/`, `products/4d/` and `3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root`.

### What this retires

**A "ladder" — a roughly dimension-independent constant — is NOT supported and that framing is
withdrawn.** Two rungs measured with the *same* statistic differ by a factor of **1.9** (4.43 % vs
2.30 %), and their integral ratios differ by ~20× (0.56 % vs 0.026 %). Three points would not have
rescued it: the third is a different statistic from a different document and could only be made
comparable by a run we are not doing.

### What this supports

**The magnitude tracks WHICH axis is marginalised, not how many dimensions remain.** Dropping W
costs 4.43 %; dropping q3 from one dimension lower costs 2.30 %. If the effect were a property of
dimensional reduction as such, the two would be comparable; they are not. So the quantity to
attribute it to is the *axis*, not the *step*.

**And the refutation of W-specificity stands, independently.** The 3D → 2D rung drops `eavail`, has
nothing to do with W, and still shows a few-percent effect. So:

- *"peculiar to the fifth axis"* — **refuted** (an effect appears when dropping `eavail` too);
- *"a dimension-independent property of marginalising an unfolded distribution"* — **not supported**
  (1.9× between the two comparable rungs);
- *"axis-dependent, at the few-percent level"* — **what the two measured rungs support**, and the
  honest statement.

### What it does to the retired interpretation

The axis ordering is the second and decisive obstacle that retired §3. It is recorded there rather
than here, so the retirement is stated once, in the place a reader looking for the hypothesis will
land.

**Referee-facing consequence:** the estimator dependence should be reported per-axis with the
measured numbers, not as a single global figure and not as a claimed regularity. Two rungs is
enough to say "it depends on the axis" and not enough to say what the dependence is.

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
