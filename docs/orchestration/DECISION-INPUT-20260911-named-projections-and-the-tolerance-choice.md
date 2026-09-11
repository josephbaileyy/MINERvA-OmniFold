# Decision input: the named projections (item 1), and `δ_proj` withdrawn (item 3)

**Owner:** `z-criteria-owner` lane. **Base of measurement:** `6f24fb00`. **Companion:**
`PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md` at this lane's tip — read
that for evidence, this for the two decisions.

> **NOT CITABLE FOR:** any adoption, grade or release. **Gate 2 FAIL. `cause3_corr` WITHHELD. Cause
> 3 non-passing. `δ_proj` NOT ADOPTED and its rule WITHDRAWN below.** Item 2's "reuse retained" is
> **provisional and measurement-only**; A-6(a), A-6(b), the excluded producing execution and the
> three-or-four block population all **stand undischarged**.

---

## ITEM 3 — `δ_proj`'s DERIVATION IS WITHDRAWN. Joseph's objection is correct.

**I ran the regrouping test. The threshold moves `102.6×` on one covariance, regrouped only.**
One bin, total variance identical in every row:

| declaration | `f_min` | `δ_proj` |
|---|---:|---:|
| `[90, 9, 1]` | 0.0100 | **0.5013%** |
| split the **largest** → `[45, 45, 9, 1]` | 0.0100 | 0.5013% — *unchanged* |
| split the **smallest** → `[90, 9, .5, .5]` | 0.0050 | 0.2503% |
| merge the two small → `[90, 10]` | 0.1000 | **5.1317%** |
| split the smallest ten ways | 0.0010 | 0.0500% |

**The dependence is entirely on the granularity of the TAIL of the component list.** Splitting the
largest changes nothing; splitting or merging the smallest changes everything. **So the criterion is
a property of the bookkeeping, not of the construction or the physics.**

### The one defence available, and it fails on evidence from my own packet

The defence would be that the declared grouping is *itself* meaningful — a component being, by
definition, the smallest unit anyone would attribute to. **That fails, and the counterexample is one
I recorded myself in rev. 4 and refused to merge: this repository declares the SAME `C_syst` at TWO
different granularities** — `adopt_unified_5d.VERT_BANDS` (**13**) and `analyze_universes_5d`'s
band census (**45** classes: 42 `±` pair bands, `2p2h`, `Flux`, `__Normalization_flat`).

**Measured on one illustrative bin shape: 13-band declaration → `0.985%`; 45-band declaration →
`0.280%`.** Same object, both declarations live in the tree, **3.5× apart.** There is no privileged
grouping to appeal to, so there is no granularity-invariant reading of "the smallest component."

**WITHDRAWN. Joseph's reasoning is exactly right and I want the concession stated precisely:** his
sentence licenses **attribution** to the declared set — a reader may attribute the bar to any
declared component. **It does not say the declaration's GRANULARITY sets an accuracy requirement.**
That step was mine, it was not in his words, and the regrouping test is what breaks it. **The claim
that the rule *follows from his statement* is withdrawn in full.**

### The remaining accuracy requirement, as an explicit CHOICE

**There is no derivation available. What follows is a scientific choice, presented as one.** The
invariance test above gives the one hard constraint on any candidate: **the yardstick must be a
NAMED object, not a selector over the grouping.** *"The smallest component"* is defined by the
grouping; a named block survives regrouping.

| # | candidate yardstick | scientific meaning | grouping-invariant? |
|---|---|---|---|
| **A** | **the statistical block `C_stat`'s contribution to that bar** — `δ = min_i [1 − sqrt(1 − f_stat,i)]` | *an undeclared analysis choice may not move the released uncertainty by more than the data's own statistical component contributes to it* | **YES** — `C_stat` is one named summand of `z_assembly.py:4`, not a selector |
| **B** | a declared fraction of the **released bar itself** | *the bar is determined to within `x%`* | YES, but `x` is a number from nowhere — it reintroduces exactly the invention this campaign has refused five times |
| **C** | the **largest** declared component | invariant under splitting the tail, but **it is still a selector**, and it is the *weakest* possible standard — it would admit almost any movement | YES, and useless |

**MY RECOMMENDATION: (A), the statistical block.** Four reasons, and the second is the one I would
defend hardest:

1. **It is named, unique and grouping-invariant.** `C_stat` appears as its own summand in the
   construction formula; no regrouping of the systematic bands touches it.
2. **It has a physical referent rather than a bookkeeping one.** *"An undeclared estimator choice
   should not move the released uncertainty by more than the measurement's own statistical
   precision contributes"* is a determinacy standard a physicist can argue with. *"…more than the
   smallest thing I happened to list"* is not.
3. **It is computable at build time from the `k = 0` baseline alone**, with no new compute, and it
   reads a block the construction already isolates.
4. **It fails in the informative direction.** If estimator-baseline variation exceeds the
   statistical contribution, the released bar's scale is set by an analysis choice rather than by
   the data — which is precisely what *"under the stated construction"* denies.

**⚠ AND ITS HONEST WEAKNESSES, because this is a choice and Joseph should price both sides.**
`C_stat` is **provisional and reused** under item 2, and its own adequacy is **not approved** — so
(A) pins a tolerance to an object still under review, and the tolerance moves if `C_stat` is ever
regenerated. It is also **not derivable from the intended-use statement** — it is a judgement about
what determinacy should mean, offered for his decision, not a consequence of anything he has said.

---

## ITEM 1 — THE NAMED PROJECTIONS: smallest complete list for the endpoint-A deliverables

**Method, stated because he constrained it:** the list is derived from **what the deliverables
display**, by enumerating every released figure that carries an **uncertainty band** on a non-2D
object. **It is not selected by which projections would pass any criterion** — no criterion was
evaluated in building it, and `δ_proj` is withdrawn in any case.

| # | axes | support | released quantity | builder | revision |
|---|---|---|---|---|---|
| **P1** | `(E_avail, W)` — 2D | destination cells receiving ≥1 reported 5D bin (`ew_coverage_report`) | per-cell `sqrt(diag)` band, and `sqrt(trace)` as an audit descriptor | `nd-unfolding/eavailW_covariance.py` (projects at `:442`, reduces at `:463`); figure overlay `3d-unfolding/genie/overlay_eavailW_band.py` | ⚠ **TO BE PINNED** — see below |
| **P2** | `E_avail` — 1D | reported `E_avail` bins; wide catch bin **omitted from the axis** (`sec_3d.tex:216`) | grouped fractional systematic band | `3d-unfolding/uq_3d/analyze_universes_3d.py` (`:23`, `uq_universe_3d_band_eavail`) | ⚠ TO BE PINNED |
| **P3** | `p_T` — 1D | reported `p_T` bins | grouped fractional systematic band | same, `uq_universe_3d_band_pt` | ⚠ TO BE PINNED |
| **P4** | `p_∥` — 1D | reported `p_∥` bins | combined-covariance systematic band on the generator overlay (`sec_3d.tex:193`, `:209-215`) | figure `generators_vs_unfolded_band`; **⚠ builder not determined — see F2 below** | ⚠ TO BE PINNED |

**Four, and I believe that is complete and minimal.** Complete: every non-2D released **band** in
the note resolves to one of these four axes. Minimal: dropping any one removes a displayed band.
**Deliberately EXCLUDED, each by name:**

- **`compare_3d_fullcov`** — a **quarantined** truncated-spectral χ² scan; `sec_3d.tex:232-236`
  says *"no value is interpreted"*. Not a released bar.
- **the 4D marginal** (`project_cov_nd.py:26`'s `cov_5d_to_4d_marginal.root`) — a **candidate
  product**, displayed nowhere. ⚠ **If any deliverable is intended to quote it, it is P5 and I have
  missed it; that is a declaration I cannot make.**
- **`C6` (`coverage_valid_nd.py`)** — a diagnostic, not a released product.
- **`C7` (`mii_anchor_comparator.py`)** — Gate-2 blocked and unquotable.
- central-value-only figures (`excess_eavail_W`, `eavail_spectrum`, `q3_excess_projection`,
  `mode_decomp_eavail`, …) — no band, so no projected uncertainty to govern.

### ⚠ THE "REVISION" COLUMN IS EMPTY ON PURPOSE, AND THAT IS ITEM 1's REAL FINDING

**No released projection currently names its builder and commit.** That is the assessor's
pre-registered **F2**, and it is why the column reads *TO BE PINNED* rather than carrying a sha:
**I can name the builders, but I cannot certify which revision produced any displayed band**, and
inventing one would be the defect this packet has corrected twice already.

**It is not a formality.**
`FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md`, **on `main`**,
records **four non-equivalent builders** that **agree on weights and diverge on refusal** — so
naming *which* builder and *which* revision is a live distinction, and **P4's builder is the one I
could not determine at all.**

**So item 1's deliverable is two things, and the second is a requirement rather than a list:**
**(1)** the four projections above, for approval; **(2)** each released band must carry its
**builder path and commit** at the point of release — which discharges F2 and is a precondition for
`U` being identified at all, since `s_proj`'s functional set is *defined* by these projections'
`M` rows.

---

## What I am NOT doing

Not adopting anything; not proposing `q` (deferred — recommendation `0.99` stands as a
recommendation); not treating item 2's provisional reuse as discharging A-6(a), A-6(b), the excluded
producing execution, or the three-or-four block population; and **not confusing *not applicable*
with *passed*** — item 4 makes requirement (i) a ruling, and the packet's §8.9 carries it as one.
