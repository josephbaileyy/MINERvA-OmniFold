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

> ## ⚠⚠ SUPERSEDED BY THE ADDENDUM — (A) IS WITHDRAWN AS THE RECOMMENDATION
>
> **Read the addendum before citing anything below.** (A) is **unsatisfiable on P2 and P3**, which
> are **systematic-only** by their own caption (`sec_3d.tex:262`): at `f_stat = 0` its threshold is
> **exactly 0**, so it voids on half the set Joseph approved. **And my verbal justification for it
> described `sqrt(f_stat)` while the formula computed the variance-share comparison** — the same
> prose-vs-algebra gap that killed the smallest-component rule, one layer in.
> **The recommendation is now (B), a fixed fraction.** Row (B)'s dismissal below — *"a number from
> nowhere… the invention this campaign has refused five times"* — **is also withdrawn**: those
> refusals were against **formatting-derived** and **results-selected** numbers, and a declared
> fraction is neither. **The four reasons below are left standing as the record of what (A) had
> going for it, not as a live recommendation.**

**SUPERSEDED RECOMMENDATION — (A), the statistical block.** Four reasons, and the second is the one
I would have defended hardest:

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

---

# ADDENDUM — the prospective projection manifest, and the accuracy choice re-answered

*Added after Joseph approved **P1–P4** and corrected what `1 − sqrt(1 − f_stat)` measures. The
smallest-component investigation is **closed** and is not reopened here.*

## DELIVERABLE 1 — the prospective Z projection manifest

**Method, and it is not inheritance.** Historical plotting code is evidence about **presentation**.
The prospective producer is selected below **on its refusal semantics**, and the maps are specified
by **naming the single authoritative source for each field** rather than transcribing edges into
prose — a transcribed edge list is a second implementation, and this campaign has paid for that.

### The builder, selected rather than inherited — and the selection criterion is refusal

`FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md` (on `main`):
four builders **agree on the weights** and carry **opposite refusal semantics** — *"`p4_lib`
refuses to build a map that would discard reported"* (`p4_lib.py:1380`), while the permissive path
returns with drops.

> **SELECTED: the REFUSING builder (`p4_lib`'s map construction), for all four projections.**
> **Reason, and it is the whole point:** a map that silently **discards reported bins** produces a
> released bar over a support that is not the declared support — and `s_proj`'s functional set `U`
> **is** the rows of that map. **The permissive builder is what `s_proj` would otherwise reach**, and
> it would make `U` silently narrower than the declaration. **A criterion cannot police a map that
> drops its own operand.** ⚠ **Revision to be pinned at the commit Joseph approves this manifest
> at**, before anything runs — for prospective maps this is a requirement I can meet, unlike the
> historical bands.

### The four maps

| | axes kept | dropped axes (integrated) | integration weight | support | units of the released bar | bar type |
|---|---|---|---|---|---|---|
| **P1** | `(E_avail, W)` | `p_T, p_∥, q_3` | product of dropped-axis bin widths — `project_cov_nd.py:5-8`'s width-weighted sum, **not unit weight** | destination cells receiving ≥1 reported 5D bin; predicate `eavailW_covariance.ew_coverage_report` | `d²σ/(dE_avail dW)`, same units as the CV it bands | **TOTAL** (`C_stat` + lateral + vertical) |
| **P2** | `E_avail` | `p_T, p_∥` | same convention | reported `E_avail` bins; **wide catch bin excluded from the axis** (`sec_3d.tex:216`) | `dσ/dE_avail` | ⚠ **SYSTEMATIC-ONLY** (`sec_3d.tex:262`) |
| **P3** | `p_T` | `p_∥, E_avail` | same convention | reported `p_T` bins | `dσ/dp_T` | ⚠ **SYSTEMATIC-ONLY** |
| **P4** | `p_∥` | `p_T, E_avail` | same convention | reported `p_∥` bins | `dσ/dp_∥` | **TOTAL** (combined-covariance band, `sec_3d.tex:193`) |

**Edges: not transcribed, by design.** The single authoritative source is the frozen CV product's
own binning — `--dst-cv` in `project_cov_nd.py:23`, which takes the destination mask **and shape**
from the frozen lower-D central product *"so masks match a real result"*. **The manifest's edge
field is therefore a POINTER — the CV product path and its commit — not a number**, and the
producer must **fail closed** if the destination mask it derives disagrees with that product.

**⚠ P4's historical builder remains UNDETERMINED and that disclosure stands** (§item 1). It no
longer blocks: P4's **prospective** producer is the selected refusing builder, same as P1–P3.

**All four derive from `Z` through these exact maps. No new uncertainty derives from any other
object** — which is what makes the *"not automatically the future producer"* constraint binding
rather than stylistic.

### The SECOND, DISJOINT LIST — covariance products required for their own sake

**Not displayed bands. Enumerated separately, as instructed.**

| | product | why it is required independently of any figure |
|---|---|---|
| **Q1** | the **4D marginal** (drop `W`) — `project_cov_nd.py:26`'s `cov_5d_to_4d_marginal.root` | ⚠ **Reclassified: it is NOT P5.** Displayed nowhere, so it is not a band; but it is the operand the 4D-consuming paths read, and `app_statmethods.tex` clause (iv) requires saying *which* covariance is meant *because* the 5D candidate, its 4D projection and the 2D block have different ranks |
| **Q2** | the **3D projection** (`p_T, p_∥, E_avail`) | `sec_3d.tex:252-256`: *"the quotable 3D covariance is the exact projection of the final adopted 5D covariance… all covariance-dependent 3D comparisons are gated on that product."* **Required by that gate, not by a figure** |
| **Q3** | the **assembled 5D trunk** `C_Z` itself, with its rank declaration | A-2 clause (iv); it is the parent every P and Q derives from |

**Deliberately still excluded, and each still by name:** `compare_3d_fullcov` (quarantined; *"no
value is interpreted"*), `C6`/`coverage_valid_nd.py` (diagnostic), `C7`/`mii_anchor_comparator.py`
(Gate-2 blocked), and the central-value-only figures. **⚠ Q1–Q3 are a list I can propose and not
one I can close** — a product required "for its own sake" is required by a *consumer*, and §1.1's
C6 condition is still unmeasured, so a fourth may exist.

---

## DELIVERABLE 2 — the accuracy choice. Joseph's correction lands, and it changes my recommendation.

### (i) Which quantity I intend: the VARIANCE-share comparison. The formula was right; my words were wrong.

**His correction is exact and I verified the table.** `1 − sqrt(1 − f_stat)` is the fractional
reduction in the total SD when the statistical variance is **removed**; `sqrt(f_stat)` is the
statistical **SD's share** of the total. They differ by **63× / 20× / 6.2× / 2.4×** at
`f_stat = 0.001 / 0.01 / 0.1 / 0.5`.

**What I intend, stated once:** *an undeclared estimator choice must not contribute more VARIANCE to
the released bar than the statistical component does.* **That is what the formula implements**, and
here is the identity that shows it — an undeclared component of variance share `f` moves the bar by
`sqrt(1 + f) − 1`:

| `f` | `sqrt(1+f) − 1` (what an undeclared share `f` does) | `1 − sqrt(1−f)` (the rule) |
|---:|---:|---:|
| 0.001 | 0.049988% | 0.050013% |
| 0.010 | 0.498756% | 0.501256% |
| 0.100 | 4.880885% | 5.131670% |

**So the rule is the variance-share comparison to within a fraction of a percent, and `sqrt(f_stat)`
is a DIFFERENT standard** — it compares a relative bar movement to an SD share, which would admit an
undeclared component roughly `2·sqrt(f_stat)` in variance, i.e. **far larger than the declared
statistical component.** ⚠ **My earlier gloss — *"by more than the measurement's own statistical
precision contributes"* — described `sqrt(f_stat)` while the formula computed the variance
comparison. The gap Joseph identified is real, it is in my prose, and the same failure mode as the
smallest-component derivation: a verbal justification that did not match the algebra.**

### (ii) The zero case is structural and it KILLS (A) on two of the four approved projections

At `f_stat = 0` the threshold is **exactly 0**. With a **global minimum** over functionals, one
systematic-only bin sets `δ_proj = 0` and **no member may move any bar at all — unsatisfiable.**

⚠ **AND THIS IS NOT HYPOTHETICAL: P2 AND P3 ARE SYSTEMATIC-ONLY BY THEIR OWN CAPTION**
(`sec_3d.tex:262`, *"Grouped fractional **systematic** bands"*). **So (A) yields `δ_proj = 0` for
half of the set Joseph just approved.**

**Global-minimum vs per-functional, both stated with consequences, because the min is what
propagates one zero:**

| | consequence |
|---|---|
| **global min over functionals** | one systematic-only bin → `δ_proj = 0` → **the whole criterion is unsatisfiable**, including on P1 and P4 where it would otherwise be meaningful |
| **per-functional `δ_i`** | P1/P4 get workable thresholds; **P2/P3 get `δ_i = 0` and remain unsatisfiable.** Contains the damage; does not repair it |

**Neither repairs it, because the defect is in the yardstick and not in the reduction. (A) cannot be
the appropriate standard for a systematic-only band: it measures the bar against a component that
band does not contain.**

### (iii) The fixed fractional-precision option, in its strongest form

**Presented on its merits, not as a fallback — and Joseph is right that (A) embodies a judgement
too.** ⚠ **My earlier grounds for refusing a chosen scalar do not transfer:** they were against
deriving a number from **formatting** and against **selecting it from observed results**. A
scientifically justified fixed fraction requires **neither**.

> **(B) `s_proj ≤ δ_proj` with `δ_proj` a single declared fraction, uniform across every released
> bar.**

| property | (A) statistical-share | **(B) fixed fraction** |
|---|---|---|
| grouping-invariant | yes | **yes** |
| defined at `f_stat = 0` | ⚠ **no — it is 0** | **yes** |
| identical across total / systematic-only / component-specific | ⚠ **no — undefined for systematic-only** | **yes, by construction** |
| pinned to an object still under review | ⚠ **yes — `C_stat` is provisional, adequacy not approved** | **no** |
| embodies a judgement | **yes** (which component, which reduction) | **yes** (the value) |

**And the admissible range is DERIVED even though the value is not:**

- **lower bound — `B'`**, the band-assembly reproducibility floor. Below it the criterion is
  unenforceable. Measured at toy scale `~4e-16` relative; **unmeasured on Z's real assembly**.
- **upper bound — `~37.8%`**, the released-bar movement SPEC §3.7d demonstrates from a
  correlation-only change. **At or above this the criterion admits the exact failure A-7 exists to
  catch.**

**RECOMMENDED: `δ_proj = 1%`, uniform, with the reasoning stated as a judgement.** It sits **~1.6
orders below** the demonstrated failure scale and far above the reproducibility floor, leaving
margin on both sides; it is **uniform across all three bar types and all four projections**, which
is the property (A) structurally lacks; and it is **round** — chosen for being round rather than
fitted, which is itself evidence it was not selected from observed results. **I have not evaluated
`s_proj` on any member, so this cannot have been chosen to make an outcome pass.**

**⚠ What (B) gives up, so the choice is priced on both sides:** it has **no physical referent**. It
does not say *why* 1% rather than 0.5% or 2%, and no measurement in this tree distinguishes them.
(A)'s appeal was exactly that referent — and (A) is unsatisfiable on half the approved set, which is
why I am recommending against my own earlier preference.

### (iv) ONE coherent rule, recommended

> **`s_proj ≤ 1%`, evaluated per declared functional over the rows of the four approved projection
> maps, with the maximum over the declared offset set `K` reported together with its argmax offset
> and argmax functional. Uniform across total, systematic-only and component-specific bars.**
> **`B'` reported beside it as the enforceability floor** — and **NOT APPLICABLE**, never
> *satisfied*, in the reuse branch (item 4's ruling).

**Per-functional, not global-min** — so a single pathological bin reports as one failing functional
rather than voiding the criterion, which is the F13 lesson applied to my own reduction.
