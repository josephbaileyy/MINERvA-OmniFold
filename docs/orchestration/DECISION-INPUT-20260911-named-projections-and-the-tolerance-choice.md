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

> ⚠⚠ **SUPERSEDED BY ADDENDUM 2 — `p4_lib` CANNOT BUILD ANY OF P1-P4.** It marginalizes **one**
> axis and hardcodes a 5-axis input (`:1354`, `:1361`); none of the four is a single-axis drop. The
> **selection ARGUMENT below stands**; the claim that this function delivers it **does not**.
> **Producer is now `project_cov_nd.build_projection` plus a `dropped == 0` gate.** Read addendum 2.
>
> ~~**SELECTED: the REFUSING builder (`p4_lib`'s map construction), for all four projections.**~~
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

---

# ADDENDUM 2 — the builder claim was WRONG, and the manifest completed

## ⚠⚠ THE VERIFICATION FAILED, AND NEITHER CANDIDATE IS ADEQUATE

**Joseph required verification that the selected builder implements every proposed map.** I ran it.
**It does not — and the correct answer is not the other builder either.**

| builder | can it build P1–P4? | does it refuse on discarded support? |
|---|---|---|
| **`p4_lib.build_projection_M`** (`:1353`) | ⚠ **NO, none of them.** Docstring: *"marginalization of **one** axis"*; `drop_axis` is a single int; and `require(len(nb) == 5)` at `:1361` **hardcodes a 5-axis input** | **YES** — `:1380` |
| **`project_cov_nd.build_projection`** (`:79`) | **YES, all four in ONE call.** `drop_axes = [a for a in src_axes if a not in keep_axes]` — arbitrary keep-axis subsets, same width-weighted convention | ⚠ **NO** — it **counts** them: `dropped = int((~keep).sum())` at `:99-100`, and returns |

**None of P1–P4 is a single-axis drop** — P1 drops three axes, P2/P3/P4 drop four — **so `p4_lib`
implements none of them as specified.** And composition is not a free repair: `:1361` means it
**cannot be called on its own 4D output**, and a chain of per-stage support checks is a **different
predicate** from one end-to-end check — which matters precisely because the support check was my
entire stated reason for selecting it.

**⚠ MY SELECTION ARGUMENT STANDS; MY IMPLEMENTATION CLAIM IS WITHDRAWN.** *"A criterion cannot
police a map that drops its own operand"* is still right, and refusal is still the property to
require. **What I asserted without checking is that this function delivers it for these maps.** I
selected a producer on a property and never verified capability — the same shape as selecting a
yardstick on an intuition and never checking the algebra, two deliverables running.

### RESOLUTION: the third option, and it is a PROMOTION rather than a new implementation

> ⚠⚠ **ONE-ARMED — SUPERSEDED BY ADDENDUM 3.** `dropped` is **source-side only** and cannot see
> orphan DESTINATION rows; a `dropped == 0` gate **passes** while a destination row is all-zero.
> **Two arms are specified in addendum 3.** The producer choice stands.
>
> ~~**Producer: `project_cov_nd.build_projection` — the only candidate that implements all four
> maps. Plus one gate: PROMOTE its existing `dropped` count to a REFUSAL.**~~

**`dropped` already exists at `:99-100` and is already computed.** The change is to require
`dropped == 0` against the declared support and **fail closed** otherwise — so the refusal property
is obtained by **binding an existing measurement to an outcome**, not by re-implementing a check.
*(A retyped rule is a second implementation; this campaign has that catalogued, and `project_cov_nd`
already refuses on edge drift at `:64` and on axis subset/order at `:121-124`, so the fail-closed
idiom is the file's own.)* **⚠ This is a code change I am specifying, not making.**

## MANIFEST COMPLETION — Joseph's five items

**1. Bar types, all four explicit and justified.**

| | bar type | ground |
|---|---|---|
| **P1** | **TOTAL** | `eavailW_covariance.py` sums `C_stat` (`:442`) **and** the lateral block (`:456-460`) into the released object |
| **P2, P3** | **SYSTEMATIC-ONLY** | `sec_3d.tex:262` — *"Grouped fractional **systematic** bands"* |
| **P4** | **TOTAL** | `sec_3d.tex:193` — the *"**combined**-covariance systematic band"*, i.e. `C_syst + C_stat + C_ML` per `:245-248` |

**2. Dropped axes, per map.** Source order is the C-order ravel `(p_T, p_∥, E_avail, q_3, W)`.

| | kept | **dropped** | count |
|---|---|---|---|
| **P1** | `E_avail, W` | **`p_T, p_∥, q_3`** | 3 |
| **P2** | `E_avail` | **`p_T, p_∥, q_3, W`** | 4 |
| **P3** | `p_T` | **`p_∥, E_avail, q_3, W`** | 4 |
| **P4** | `p_∥` | **`p_T, E_avail, q_3, W`** | 4 |

**3. Q1 and Q2 retained axes.** **Q1** retains `(p_T, p_∥, E_avail, q_3)`, drops `W` — **the one
single-axis drop in either list, and therefore the only map `p4_lib` could build.** **Q2** retains
`(p_T, p_∥, E_avail)`, drops `q_3, W`.

**4. Source and destination bindings — and ⚠ the source CANNOT be bound yet, which is a statement
about Z and not an omission.**

| field | source | destination |
|---|---|---|
| **artifact** | ⚠ **`C_Z` — DOES NOT EXIST.** `SPEC` §1.6: *"PATHS, RECEIPT SCHEMA/VERSION, AND PRODUCING REVISION DO NOT EXIST."* **A forward binding, to be pinned at build** | the frozen lower-D CV products, by path — `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` and the 4D/3D siblings |
| **key** | the assembled trunk's covariance key, declared with the receipt schema | `hXSecND_flat` (`project_cov_nd.py:19`) / `hXSec3D` for 3D |
| **edges** | Z's own 5D grid | **P2's are CITABLE NOW: `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100] GeV`, `sec_3d.tex:97`.** Otherwise `--dst-cv`, which takes mask **and shape** from the frozen product |
| **units** | `d⁵σ/…` density per unit bin-volume (`xsec_nd.extract_cross_section_nd` divides by `Π dx_a`) | as tabled in addendum 1 |
| **support** | Z's reported mask | `CV > 0` on the destination product |
| **builder revision** | `project_cov_nd.py` **+ the `dropped == 0` gate**, pinned at the approving commit | same |

**⚠ AND THE DESTINATION PRODUCTS ARE NOT IN THIS CHECKOUT** — `products/*/xsec_*.root` matches
nothing here; they are untracked build outputs. **So "bound" means path + digest recorded at build
time**, and I am naming paths I cannot digest today rather than implying I have.

**5. Declared exclusions vs silently discarded support — TWO LEDGERS, never one.**

| | ledger |
|---|---|
| **DECLARED EXCLUSIONS** | intentional, enumerated, each with its reason. **Worked example: P2's wide `[3, 100] GeV` catch bin**, excluded from `fig:eavail`'s axis (`sec_3d.tex:113`, `:216`) — it is the **7th** `E_avail` bin of the edge list above. **Declared, accounted, and still part of the support** |
| **DISCARDED SUPPORT** | `project_cov_nd`'s `dropped` count. **Must be `0`.** Anything else is a construction defect and the new gate refuses it |

**Conflating the two is the failure mode this item exists to prevent:** a declared exclusion is a
**scientific** choice with a reason attached; a dropped bin is a **map** defect with none. **They
must never be summed into one number**, because a nonzero total would then have two possible
meanings and no way to tell which.

## ⚠ AND ONE FRAMING OF MINE WITHDRAWN: "per-functional rather than global-min" IS NOT A CHOICE

**Joseph is right and I am not restating it.** With a **uniform** limit, `∀i: s_i ≤ 1%` **is** the
same condition as `max_i s_i ≤ 1%`. **There is no choice to present.** It was substantive only for
**(A)**, where the *threshold itself* varied per functional and the reduction was a **min over
thresholds** — and (A) is withdrawn. **The recommendation is therefore simply `s_proj ≤ 1%`**, with
the max over `K` and both argmaxes reported, and the reporting of argmaxes is a **diagnostic
obligation, not part of the condition.**

---

# ADDENDUM 3 — the gate was one-directional. Both arms, named, with what each catches.

## ⚠⚠ `dropped == 0` IS HALF A GATE, and the missing half has a recorded real-product incident

**Replicated on a toy where one destination row is reachable by no source bin:**

    dropped (SOURCE-side)      = 0   <- my gate PASSES
    all-zero DESTINATION rows  = 1   <- UNCAUGHT
    M row sums                 = [2. 2. 0.]

`dropped = int((~keep).sum())` counts **source columns whose destination row is `-1`**. It cannot
see **destination rows no source column reaches** — those are all-zero rows of `M`, invisible to that
count **by construction**.

**And the masking mechanism reproduces.** Feeding those row sums to a central comparison against a
nonzero frozen value gives per-row `rel = [0, 0, 1.0]` — **`max rel = 1.0`, contributed by the
orphan alone.** `p4_lib:1382-1391` records the real-product incident verbatim: 5 orphan bins
carrying `0.0000%` of the 4D total produced *"projection mutates central (max rel 1.00e+00)"* and
**hid the actual result — 62% of bins over tolerance at a median of 4.4% — behind a number
contributed by bins nobody would care about.** *"An error that is loudest about the least important
thing is worse than no error, because it redirects the investigation."*

**So the property I selected a builder FOR — refusal rather than silent discard — is exactly the
property my bridge only half delivered, and the missing half is the one with the incident.**

### ⚠ AND THIS IS THE SAME SHAPE A THIRD TIME. The diagnosis is the relayed one and it is sharper than mine.

| # | instrument | property I selected it for | what it actually measures |
|---|---|---|---|
| 1 | `p4_lib.build_projection_M` | *"it refuses"* | refuses — **but is rigidly 5→4 and builds none of P1–P4** |
| 2 | `1 − sqrt(1 − f_stat)` | *"the statistical contribution"* | the **variance-share** comparison, not the SD share my prose claimed |
| 3 | `dropped` | *"the count already exists"* | **source-side only** |

**The pattern: selecting an instrument by the property it ADVERTISES rather than by what it
MEASURES.** In all three the advertised property was real — it just was not the one the claim needed.

## THE SPECIFICATION: two arms, and which one catches what

> **ARM 1 — SOURCE-SIDE.** `dropped == 0`, from `project_cov_nd.build_projection`'s existing
> `dropped = int((~keep).sum())` (`:99-100`).
> **Catches:** a reported **source** bin that lands in **no** reported destination row — i.e. support
> silently discarded out of the map.
>
> **ARM 2 — DESTINATION-SIDE.** `empty = np.nonzero(~M.any(axis=1))[0]`, `require(empty.size == 0, …)`
> — **lifted verbatim from `p4_lib:1395-1400`, not retyped**, with its orphan-index diagnostic.
> **Catches:** a reported **destination** row reached by **no** source bin — an all-zero row of `M`
> that would reach a central comparison as an exact zero and report `rel = 1.0` regardless of how
> small the bin is.
>
> **Both run at CONSTRUCTION**, per that file's own instruction — *"Fail here, at construction, where
> the diagnosis is the orphan list itself"* — **not at the central comparison**, which is where the
> masking happens.

**Neither arm subsumes the other, and the asymmetry is why:** arm 1 quantifies over source columns,
arm 2 over destination rows. A map can be perfect in one direction and defective in the other, which
is exactly the toy above. **A filter needs an arm in the direction it acts; mine had one.**

## THE THREE OPTIONS, AND I AM CHOOSING — the assessor declined to, and it is my call

**Its general form is correct and sharper than the instance: arity and refusal are SEPARATED in this
tree and no existing builder has both.** `p4_lib` refuses both ways and is rigidly 5→4;
`project_cov_nd` takes arbitrary keep-axis subsets and drops **by design** (`:81-82`,
*"or −1 to drop"*), with the `FINDING` on main recording it performs **neither** orphan check.

> **CHOSEN: EXTEND, single-call.** `project_cov_nd.build_projection` with **both arms** added.
> **Not composed, and not giving up a property.**

**Why not COMPOSE** — two reasons, and the second is the one that decides it:
1. It triggers the assessor's **condition 6** (below), adding a declaration that a single call does
   not need.
2. **It converts one end-to-end support predicate into a CHAIN of per-stage ones** — a different
   predicate, which I flagged against `p4_lib` in addendum 2 and would be adopting here if I
   composed. **Rejecting an option for a reason and then choosing it is the failure I would be
   repeating.**

**Why not GIVE UP A PROPERTY:** nothing needs giving up. **Both arms exist as one-liners** in a
file in this tree, and arity already exists in the other. **The extension adds no new mathematics
and no new check — it moves two existing predicates to the only producer that can build the maps.**

### Condition 6 — composition ORDER: DOES NOT BIND, and here is the condition under which it would

**Single-call, so no composition order exists to declare.** Recorded because it is a live constraint
on the option I rejected: the width weights compose exactly (`w_a·w_b`) so the **mathematics** is
order-independent, but the **arithmetic** is not — measured at band-assembly scale, pairwise-vs-
sequential is bit-identical while **reversing the order moves the result by ~`5e-16`–`1.3e-15`
relative** (probe §14 measured the same mechanism at `4.3e-16`). **A composed projection is a
summation over dropped-axis cells, so an undeclared order is an undeclared perturbation at exactly
the scale a reproducibility gate sits at.** ⚠ **If anyone later composes any of P1–P4, the order
becomes a required declaration.**

## AND THE SCALE ARGUMENT IS WHY ARM 2 IS NOT A CORNER CASE

Measured by the assessor: **P1 has 42 destination bins at mean row support 254.6; P2 has 7
destination bins at mean row support 1527.7** — roughly **1.17 million off-diagonal entries entering
a single released bar.**

**Two consequences, and the first is worse than "harder to see":**

- **A single orphan row in P2 is `1/7` of the released figure** — **14% of the deliverable reading
  as an exact zero**, and by the masking mechanism `max rel = 1.0` would hide every other result
  behind it. **Arm 2 is not a tail case for P2; it is an eighth of the figure.**
- **A silent discard inside a 1,528-cell row is invisible in a way it is not inside a 254-cell one.**
  This is the argument for how hard §item-5's **two ledgers, never one** has to hold: at P2's row
  support, a discard summed into a declared-exclusion total would be undetectable by inspection.

**So arm 2's priority is inverse to destination-bin count** — the fewer destination bins, the larger
the fraction one orphan destroys, and P2/P3 have the fewest.
