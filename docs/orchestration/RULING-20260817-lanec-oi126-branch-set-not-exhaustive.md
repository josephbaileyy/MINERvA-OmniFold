# RULING — `OI-126`: `{(a), (b)}` is NOT exhaustive — and the third branch I offered is now REFUTED too

**Asked of:** lane C (PET), as owner of `SPEC-20260814-gate5-cstat-construction-v1.md` and
`gate5_cstat_contract.json`. **Put to quorum, not to Joseph**, under his 2026-08-17 grant that two agreeing
sessions can decide. Assistant is answering the same three questions independently and neither of us read
the other first.

**ANSWER TO Q1: NO, the binary is not exhaustive** — for two independent reasons, the second of which
disposes of `(a)` whether or not `(a)` is true. **Q2 therefore does not fire. Q3: the discriminating
measurement compares TARGETS, not unfoldings, and the arrays are already on disk and already inventoried
by sha.** Nothing was run to produce this ruling.

> ### ⚠ STATUS AFTER LANE D'S MEASUREMENTS, 2026-08-17 — READ THIS FIRST
>
> **`(c)`, the third branch offered below, is REFUTED** (§3): its mass-addition limb measured null with
> power (`+0.000179%`, `0.03 SE`, 19/50 above), and its redistribution limb requires a nonlinearity that
> **is not active in the band at all** (`0` of 86 band cells have background mass exceeding the data count).
> **And my Q3 refutation rule was self-contradictory** — D caught it and declined to cash it (`BEN-403`).
>
> **§1 and §2 are untouched, and D says so explicitly rather than letting the death of its own assigned
> hypothesis read as support for a rival.** `(b)`'s premise separately misdescribes the construction as
> measured-leg-only — Assistant's point, located in
> [`DETERMINATION-20260817-lanec-cstat-object-is-total-statistics.md`](DETERMINATION-20260817-lanec-cstat-object-is-total-statistics.md).
>
> **So all three named branches now have a problem. That is the honest state of `OI-126` and it is harder
> than before, not easier.** What is live is the MC-thinning route in the TRAINING leg, which is lane E's.

**Constraints honoured, both from my own prior work:** nothing here rests on the floor **decomposing** the
family spread (`VL130`'s independence assumption forbids it), and nothing here uses the sd ratio as an
explanatory share (it is the maximum-correlation bound, and separately disqualified on units). **The floor
enters only as an EXCLUSION of one candidate cause, which is not a decomposition** — and the argument below
does not depend on it at all.

---

## 1. Why the binary cannot be exhaustive: a type mismatch

| | proposition | object | quantity |
|---|---|---|---|
| **(a)** | the estimator is honestly unstable at p‖ 6–20, so publish the large bands as-is | the family | its **dispersion** |
| **(b)** | a Poisson bootstrap of the measured leg is not a valid uncertainty proxy | the family | its **dispersion**'s validity |
| **the evidence** | the nominal sits outside its own 50-member family, **spatially organised, sign-reversing** | the **nominal** | its **location** relative to the family |

**Both branches are propositions about the family's WIDTH. The load-bearing evidence is about the nominal's
LOCATION.** Re-read from `RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json` this turn
rather than from any summary:

| region | `n` | median `z` | nominal above **all 50** |
|---|---|---|---|
| p‖ < 6 GeV | 128 | **`−0.128`** | 0 |
| band cols 10–15 (p‖ 6–20) | 84 | **`+3.555`** | **44** |
| the 63 tail cells | 63 | **`+3.809`** | **44** |
| p‖ > 20 GeV | 45 | **`−1.828`** | 0 |

plus `nominal / family_mean` in the band = **`2.861`** (`nom/median` = `3.058`, so **not** a mean-vs-median
artefact, stated in the receipt), `median(nominal / family MAXIMUM)` over the 63 = **`1.209`**,
`min_members_below_nominal` over the 63 = **`45`**, and the nominal **total** at the **98th percentile**.

**A family can have perfectly honest width and still fail to contain a central value produced by a
different construction. No proposition about width is confirmed or refuted by a location failure.** So the
containment evidence — which is the whole of the case — bears on neither branch.

**And the structure is more specific than "outside":** the displacement **reverses sign** across a
kinematic boundary while the total stays inside the family range. **That is mass REDISTRIBUTED across p‖,
not mass added.** Neither `(a)` nor `(b)` predicts a sign flip; both are silent on where the nominal sits.

## 2. `(a)` is incoherent AS A DISPOSITION, independent of whether the estimator is unstable

**This is the part that should settle Q2 even for a reader who rejects §1.** `(a)`'s disposition is *"the
published uncertainties there are enormous and must be quoted as such."* Apply it:

> The nominal exceeds **every one of the 50 members** in 44 of 63 cells, and exceeds the family
> **maximum** by **21%** at the median tail cell.

**So publishing the large bands as-is publishes a central value OUTSIDE ITS OWN ERROR BARS in 44 of 63
cells.** Widening a band does not capture a point above the band's own maximum. **`(a)` does not dispose of
the problem it is offered for** — it is not a conservative reading of the evidence, it is a reading that
leaves the measurement self-inconsistent. **Whatever is true about estimator stability at p‖ 6–20, `(a)`
cannot be the disposition.**

## 3. The third branch — ⚠ **REFUTED BY MEASUREMENT 2026-08-17, TWICE, AND ONE OF THE TESTS WAS MINE AND WAS BROKEN**

> **`(c)` IS DEAD. Both limbs, independently, by lane D. The code reading below stands; the EXPLANATION does
> not.**
>
> **LIMB 1 — mass addition, measured with power established FIRST.** `sum(nominal_target)` =
> `1.124080587652e+06` against `mean_i sum(replica_target_i)` = `1.124082601268e+06`: gap **`+2.01`**,
> **`+0.000179%`**, **`0.03 SE`**, **19 of 50** replicas above. D checked the test could discriminate before
> running it — replica sums span `1.1226e6`–`1.1253e6`, `sd = 5.68e2`, so not pinned to a constant.
> **No mass-addition signature.**
>
> **LIMB 2 — the mechanism is not merely weak in the band, it is ABSENT.** Background share of the measured
> leg, median per reco cell: **`9.604%`** at p‖ < 6 (100 cells), **`9.840%`** in the band (86),
> **`11.368%`** at p‖ > 20 (45). **The band sits BETWEEN the two control regions, not at a peak.** And
> **`0` of the 86 band cells** have background mass exceeding the data count (3 of 231 live overall), so
> **the cell-level signed sum never goes negative in the band at all. Stay-Positive is not clipping there.**
> **A nonlinearity that is inactive where the effect is cannot be the effect's mechanism.**
>
> *(D's limits, carried rather than smoothed: this is RECO space, because data rows carry no truth
> coordinate so a truth-cell negative fraction is not a defined quantity; `"bkg mass > data count"` is a
> cell-level proxy and finer clipping inside net-positive cells is not excluded; the uniform ~10% share is
> the robust half and holds at any granularity.)*
>
> ### AND MY OWN Q3 DECISION RULE WAS SELF-CONTRADICTORY — D CAUGHT IT AND DECLINED TO EXPLOIT IT
>
> §4 said *"a nonzero one-signed gap is the Jensen signature; **zero refutes `(c)` at the total level**."*
> §3 said `(c)` was *"redistribution, not inflation, **with the total nearly conserved**."* **If `(c)`
> predicts conservation, a zero total gap is what `(c)` PREDICTS, not what refutes it.** D declined to
> return `REFUTED` against a rule whose own hypothesis expected the observed outcome — **the right call, and
> it caught my defect instead of cashing it.**
>
> **The mediator's repair is right and I would go one step further, because the contradiction is the symptom
> and not the cause.** The repair: Jensen on an elementwise convex map **adds** mass and the addition does
> not cancel under summation, so a strict Jensen mechanism predicts a **positive total gap** as well as
> redistribution — which makes Limb 1 informative rather than silent. **The cause: `"total nearly
> conserved"` was never a prediction of the Jensen mechanism at all. It was a description of the
> OBSERVATION** (the nominal's total at the 98th percentile) **that I imported into the mechanism's
> predictions.** So one limb was made unfalsifiable by the very evidence it was invented to explain, and the
> two limbs then contradicted each other. **Filed as `BEN-403`.**
>
> ### WHAT SURVIVES AND WHAT DOES NOT
>
> | | status |
> |---|---|
> | §1 type mismatch — both branches are dispersion propositions, the evidence is location | **STANDS** (D says so explicitly) |
> | §2 `(a)` incoherent as a disposition | **STANDS** |
> | §3 code reading — the per-replica refinement is REQUIRED, harmonising destroys `C_stat` (`BEN-402`) | **STANDS** — it is a fact about the construction |
> | §3 Jensen as the EXPLANATION of the band structure | **REFUTED** |
> | §3 the `CSTAT-D2` centring question | **MOOT**, and separately **SPECIFIED** upstream — Gate 5 F7's own text says *"Center `C_stat` on the accepted replica mean"* (`DETERMINATION-20260817-lanec-cstat-object-is-total-statistics.md` §1) |
> | §4 Test 1 as a REFUTATION rule | **WITHDRAWN** — it was inverted; as a test of the mass-addition limb (the mediator's reading) it is sound and it ran |
>
> **All three named branches now have a problem. That is the honest state and it should not be smoothed into
> whichever branch is least damaged.**

## 3. The third branch, as originally argued — the code reading stands, the explanation does not

**`(c)` THE NEGWEIGHT REFINEMENT IS INSIDE THE BOOTSTRAP AND IT IS NONLINEAR, SO THE FAMILY MEAN IS NOT AN
ESTIMATOR OF THE NOMINAL AND NON-CONTAINMENT IS EXPECTED.**

**Read from the loader, not inferred.** `nd-unfolding/pet/fullevent_fps_dataloader.py:1462-1487`, the
Gate-5 amendment to the precomputed-target guard, and its refusal text:

> *"**GATE 5 (2026-08-13).** This guard used to refuse EVERY precomputed target under a bootstrap seed.
> That is right for the NOMINAL array and it made the adopted replica architecture impossible: **Gate 5
> requires a negweight-refined target built PER REPLICA (ROOT)** and then consumed by that replica's
> training job (TF), because no Perlmutter interpreter carries both."*
>
> *"a precomputed target is the NOMINAL target; **a bootstrap replica draws its own data/background
> factors, so consuming the nominal array here would silently give every replica the nominal's measured
> weights and COLLAPSE THE MEASURED-SIDE VARIANCE** (fail closed)."*

**And it is enforced, not merely intended.** `reconcile_gate5_family.py:837-845` requires all 50
`target_sha256_measured` to be **pairwise distinct**, with the stated reason *"identical targets would
collapse the measured-side variance and read as a SMALL `C_stat` rather than as a failed draw — the
reassuring failure"*; `:847-850` requires `no_replica_target_equals_the_nominal_target`.

### What follows, and it is a Jensen argument

- **nominal** = `refine(w_measured)` — the certified Gate-2 array, i.e. **refine applied AT the mean**.
- **member `i`** = `refine(w_draw_i)` — refine applied to that replica's Poisson draw.
- **family mean** ≈ `E[refine(w_draw)]`.

**`refine` is not affine.** Stay-Positive (arXiv:2505.03724) maps possibly-negative measured weights to
non-negative ones — the loader rejects a precomputed target carrying any negatives (`:1507`, *"precomputed
target has {n_neg} negative weights"*), which is the property being enforced. A map onto the non-negative
cone from a domain containing negatives has a kink at the boundary.

**Therefore `E[refine(w)] ≠ refine(E[w])`, systematically, and one-signed wherever the curvature is
one-signed.** The gap is largest where the refinement bites hardest — where raw weights go most negative —
which is a **kinematically localised** region, and positivity enforcement moves mass **out of** those
regions **into** adjacent ones, so **the sign of the transfer flips across the boundary.**

**That is the observed structure, term for term:** `−0.128 → +3.555 → −1.828` with the total nearly
conserved (98th percentile) and `nominal/family_mean = 2.861` where the transfer lands. **A nonlinear
projection inside the bootstrap predicts a sign-reversing spatial redistribution. Neither `(a)` nor `(b)`
predicts anything about sign or location.**

### `BEN-383`'s candidate is right as an observation and wrong as a diagnosis

`BEN-383` names *"the two arms use different Stay-Positive backends"* and reads it as a **discrepancy
between two arms**, with other differences ruled out. **The loader says the difference is REQUIRED.** It is
not an accident to be harmonised — **harmonising it destroys `C_stat`**, and the reconciler carries a check
whose explicit purpose is to catch that as *"the reassuring failure."*

**So `(c)` is not "a backend offset that pairs badly." It is: the estimator whose statistical uncertainty
`C_stat` measures INCLUDES a nonlinear refinement, and the bootstrap correctly propagates the draw through
it. The family is right, the nominal is right, and the INFERENCE FROM NON-CONTAINMENT is what is wrong.**

### What `(c)` leaves standing, and what it costs

- **`C_stat`'s validity is untouched.** `CSTAT-D4`'s disjointness proof holds unchanged: only the coherent
  Poisson draw varies, estimator seed pinned at `42`, defaulted at `train_fullevent_nominal.py:335`,
  fail-closed on drift at `train_fullevent_replica.py:275`, measured `50/50`. **`OI-121`/`OI-122` do not
  reopen and `GATE5_CSTAT_N50.npz` is not discarded.**
- **What `(c)` DOES cost, and it is not free:** the family mean is a **biased** estimator of the nominal by
  the Jensen gap, so **`C_stat` centred on the replica mean (`CSTAT-D2`) is a covariance about a point the
  nominal is not at.** That is a real open question about the *centring*, not about the *construction* —
  and it is narrower than either offered branch. **I am not ruling on it here; it is downstream and it is
  new.**
- **`(b)` is nearer the mechanism than `(a)`** — it is at least about the measured leg's bootstrap — **and
  its remedy is still wrong.** `(c)` is `(b)`'s premise with a different conclusion, which is precisely why
  forcing the binary is expensive: it would discard a built artifact and reopen two items **for a reason
  that is false under `(c)`.**

## 4. Q3 — what would settle it, and it compares TARGETS rather than unfoldings

**The mechanism in `(c)` lives entirely in the refinement, so it is testable WITHOUT any unfolding, any
training, any GPU, and without touching the promoted arm.** The arrays already exist and are already
inventoried: 50 per-replica refined targets with recorded `target_sha256_measured`, plus the certified
Gate-2 nominal target, proven pairwise distinct by the reconciler.

**Test 1 — scalar, no grid work.** Compare `sum(nominal_target)` against
`mean_i sum(replica_target_i)`. Positivity enforcement **adds** mass where raw weights were negative, and
how much it adds depends on how many negatives that draw produced. **A nonzero one-signed gap is the Jensen
signature; zero refutes `(c)` at the total level.** 51 arrays, one loop.

**Test 2 — spatial, still no jobs.** Histogram both into the reco grid using an assignment
**RECONSTRUCTED BY THE CONSUMER** from the loader's canonical edges — `CANONICAL_PT_EDGES`,
`CANONICAL_PPARALLEL_EDGES` and `SCALAR_COLS` imported, not restated, and the grid asserted by the loader's
own `assert_extended_fps_edges` — and ask whether the **target-level** gap reproduces the
`−0.128 / +3.555 / −1.828` structure.

> **⚠ CORRECTED 2026-08-19 — THIS SENTENCE NAMED A MECHANISM THAT DOES NOT EXIST, AND ITS ABSENCE IS A
> DESIGN PROPERTY.** It read *"using the loader's own per-event assignment"*. **The loader performs no
> binning at all** — zero `digitize`/`searchsorted`/`ravel_multi_index` — and **production refinement is the
> LEARNED UNBINNED classifier on continuous reco features**, so no per-event cell index exists anywhere on
> the production path. `stay_positive_refine_binned` RECEIVES `cell` and is labelled FIXTURE-ONLY in the
> loader's own comment; `build_reco_cloud`'s `coord_idx = (1, 2)` is the point cloud's KNN (pos, z) columns
> and is **not** a bin index, which is the specific way this phrase misleads. The assignment is therefore a
> **construction introduced by the consumer**, admissible as such and required to be described as such.
> **Full ruling, including the no-clip requirement and the `-1` reporting condition that make a Test 2
> number quotable: `RULING-20260819-lanec-reconstructed-cell-assignment-admissible.md`.** Found by lane B,
> escalated by the mediator, corrected by lane C as the author. *The original phrasing is quoted above
> rather than deleted, because it propagated into other artifacts and a reader who met it there needs to
> find it here.*

- **If it does: `(c)` is established, neither `(a)` nor `(b)` is needed, and the live question becomes the
  narrow centring question in §3.**
- **If it does not: `(c)` is refuted at the target level, and `(a)` vs `(b)` becomes rulable on whatever
  difference survives** — which is the first time either would be answerable on evidence.

**This is NOT the blocked re-extraction route.** It runs no unfolding, retrains nothing, needs no GPU, and
writes nothing inside the promoted arm — so the four fail-closed guards it must not force are not on its
path. **But per `BEN-384` I am explicitly NOT costing it from this row: its runnability must be established
by writing the invocation and running `verify_hash_bindings.py` against it, not by reading this
paragraph.** An item's cost is a property of where its code lives.

## 5. Disposition

- **Q1: `{(a), (b)}` is NOT exhaustive.** Both are propositions about dispersion; the evidence is about
  location. **`(c)` is the branch the code's own design comment predicts.**
- **Q2: does not fire.** And if forced: **neither.** `(a)` is incoherent as a disposition (§2); `(b)`'s
  premise is nearer the truth and its remedy is wrong (§3).
- **Q3: settleable, cheaply, at the target level** (§4) — and the answering arrays are already on disk.
- **Not ruled, and new:** whether `CSTAT-D2`'s centring on the replica mean is right if the family mean is
  a Jensen-biased estimator of the nominal. **Narrower than either branch and it is the question `(c)`
  leaves live.**
- **Nothing run. `§3` of `CRITERIA-20260811` as written stays operative; `M(ii)` stays `(B)` with the
  magnitude UNMEASURED; the five Gate-6 prohibitions at `19585b7` stay live; `C_ML` construction remains
  prohibited; nothing enters `docs/analysis-note/`.**

*Lane C (PET). `BEN-402` files the reusable half: a difference between two arms that the construction
REQUIRES will be read as a discrepancy by anyone comparing them, and the natural remedy destroys the
measurement.*
