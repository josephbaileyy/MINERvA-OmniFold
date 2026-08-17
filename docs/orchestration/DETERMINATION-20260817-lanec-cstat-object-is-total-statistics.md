# DETERMINATION — `C_stat`'s object is TOTAL statistics, by specification, and `OI-94`'s denominator is wrong because of it

**By:** lane C (PET), as owner of `SPEC-20260814-gate5-cstat-construction-v1.md` and
`gate5_cstat_contract.json`. **Asked by the mediator 2026-08-17**, correctly identified as the spec owner's
call: *"whether `C_stat`'s object is DATA-STATISTICS-ONLY or TOTAL statistics. `SPEC-20260814` discusses the
signal factor's effects at `:419` and `:495` without stating intent."*

> **⚠ CITATION DEFECT IN THIS FILE'S OWN FIRST REVISION, recorded rather than silently fixed.** Both
> citations of the DAG were **bare** — `PET_UQ_REMEDIATION_STATUS.md:738-758` — from a document living in
> `docs/orchestration/`, where no such file exists. **A bare filename is a citation whose resolution depends
> on the reader's working directory**, and in a repo holding both `nd-unfolding/` and `nd-unfolding/pet/`
> the natural guess for a PET file is the wrong one by exactly one directory: the mediator looked in
> `nd-unfolding/pet/`, got nothing, and nearly reported the citation unresolvable before finding it one
> level up. **Now repo-relative in both places.** *(The exact string `nd-unfolding/pet/…` is the mediator's
> reconstruction and does not appear in my text — but the ambiguity that produced it is mine, and a
> citation that requires the reader to guess a directory is not better than one that names the wrong
> directory.)* **Third instance today of a citation landing near-but-not-on** — `:36` for `:37`, `OI-6` for
> `OI-3`, and this. **In all three the near-miss is what makes it expensive: a citation that lands nowhere
> gets checked and fixed; one that lands nearby gets believed or silently abandoned.**

**The mediator is right that the spec never states the intent.** Both cited passages
(`CSTAT-D0d`, `CSTAT-D3`) describe the signal factor's *effects on the mask* and neither states what the
object IS. **That gap is real and it is mine.** Nothing was run to produce this determination.

---

## 1. RULING: TOTAL statistics — and it is not the spec's choice, it is the DAG's

**`nd-unfolding/PET_UQ_REMEDIATION_STATUS.md:738-758`, Gate 5 F7's own text, *"For every replica, in this exact order"*:**

> 1. *"Enumerate complete, ordered **data, signal-MC, and background-MC** inventories before any training
>    subset."*
> 2. *"Draw one **coherent** Poisson factor per inventory member from a persisted, replayable replica seed
>    policy."*
> 3. *"Apply data factors to data weights, **signal factors everywhere signal MC is used**, and background
>    factors to the negative background injection."*
> 6. *"Reuse the exact applicable **signal/background** factors during full extraction and
>    completeness/count construction."*
>
> and, two paragraphs on: *"**Center `C_stat` on the accepted replica mean.**"*

**Signal-MC is named in three of the six steps. So three-stream resampling is SPECIFIED, not chosen** — by
the DAG, upstream of `SPEC-20260814`, which is why the spec records the signal factor's *effects* without
arguing for its *presence*: there was nothing for the spec to decide.

**Two consequences that settle the mediator's alternatives directly:**

- **The `OI-126` row's *"a Poisson bootstrap of the measured leg"* misdescribes the construction, and the
  misdescription is against the DAG rather than against the spec.** Assistant's point, and this locates it.
- **`CSTAT-D2`'s centring on the replica mean is ALSO specified** (*"Center `C_stat` on the accepted replica
  mean"*). **So the centring question I flagged as new and live in `RULING-...-oi126-branch-set-not-exhaustive`
  §3 is not a lane's open item** — reopening it means reopening Gate 5's text, which is a different act with
  a different owner. *(Moot in any case: the mechanism that would have biased the centring is refuted — §3
  of that ruling, now marked.)*

## 2. AND IT IS CORRECT BY DESIGN, not merely specified — because no other component carries it

**The declared budget has no MC-statistics component.** Measured over `SPEC-20260814` and
`nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`: `C_stat` (48), `C_syst` (12), `C_ML` (9), `C_retrain` (5), `C_train` (2),
`C_syst_joint` (1). **`C_MCstat` — or any spelling of it — occurs zero times.**

And `C_syst` cannot absorb it: systematic universes vary **physics parameters**, not **sample size**. A flux
or cross-section throw does not resample the MC inventory.

**So if `C_stat` did not carry the signal- and background-MC Poisson, NOTHING in the declared budget would,
and the analysis would be missing MC statistical uncertainty entirely.** That is the substantive argument,
and it is stronger than the specification: the three-stream construction is not just what Gate 5 says, it is
what the budget requires.

**The cost of the name, stated because it is real:** calling a total-statistics object `C_stat` invites
exactly the misreading the `OI-126` row committed, and `CSTAT-O2`'s closure of `OI-92` (*"`C_stat` is
correctly named"*) argued the name only on the **estimator** axis — that the seed is pinned so the object is
not `C_stat + C_train`. **The data-vs-MC axis was never addressed by that closure.** It is addressed here,
and the answer is that the name is defensible and the object should be stated wherever the name is used.

## 3. THE CONSEQUENCE I OWE: `OI-94`'s 90× USED A DATA-ONLY DENOMINATOR AGAINST A TOTAL-STATISTICS MEASUREMENT

`OI-94`, raised by me, states *"relative sd of the total cross section **4.478%** vs **0.0493%** Poisson on
`n_data = 4,116,128`"*, ratio **`90.8×`**. `1/√4,116,128 = 0.0493%` reproduces exactly, so the denominator
is confirmed **data-only**.

**But the numerator is the spread of a family that resamples three inventories.** The counting expectation
must therefore be over the same three:

| stream | `N` (from the family receipts' `n_*_full`) | `1/√N` |
|---|---|---|
| data | `4,116,128` | `0.0493%` |
| **signal MC** | `49,152,885` | `0.0143%` |
| **background MC** | **`564,591`** | **`0.1331%`** |
| **quadrature** | — | **`0.1426%`** |

**So the ratio is `31.4×`, not `90.8×` — the gap is 2.9× smaller than my own row says, from the denominator
alone.**

**And the dominant term is BACKGROUND MC**, at `0.1331%`, because `n_bkg` is by far the smallest inventory —
`564,591` rows, `12.06%` of the `4,680,719`-row measured leg. **Nine times the data term, and nobody has
been looking at the background stream.**

**LIMIT, stated rather than smoothed:** `1/√N` per stream is the raw counting fraction on a rate. The
background enters as a **negative injection** and the signal MC through the estimator, so neither propagates
to the total cross section with unit leverage. **The correction to the denominator's SET is certain; its
VALUE requires the propagation weights and this is not that calculation.** `31.4×` should be read as *"the
right denominator is at least 2.9× larger than the published one"*, not as a measured ratio.

**This is my named recurring failure — an asymmetric comparison — in the row I raised to record an
unexplained gap.** The gap was overstated by construction, and the overstatement is what made it look like
an estimator pathology.

## 4. What this means for the live route (E's), and what it does NOT license

**E's MC-thinning route is not a defect hunt under this determination.** Signal-MC thinning inside the
bootstrap is the **specified** behaviour, so a training-leg divergence it produces is **part of what `C_stat`
measures**, not evidence the construction is broken.

**But it does not explain the nominal's non-containment, and the reason is structural:** the nominal is built
at the **unthinned** signal MC while every replica is built at a **thinned** one, and the map from that
stream to the answer is a **trained network** — nonlinear, and unlike the Stay-Positive refinement it is
**active everywhere, including the band.**

### The `N_eff` arithmetic — verified, and it must NOT be read as the bootstrap being mis-scaled

The mediator reached the same conjecture independently within the hour, from arithmetic rather than
structure: `N_eff = N / E[w²]`, and for `Poisson(1)` weights `E[w²] = Var + mean² = 2`, so **`N_eff = N/2`**
and *"every replica trains at half the nominal's effective MC statistics."* **Verified numerically this
turn** at `N = 2×10⁶`: `E[w²] = 2.0005`, `N_eff/N = 0.50003`. **Two derivations, one from arithmetic and one
from structure, is corroboration rather than echo.**

**But one guard has to travel with it, and it is a spec-owner's guard.** `N_eff = N/2` is a property of
**every correct Poisson bootstrap**, not a defect of this one — the bootstrap's variance estimate is
consistent for a smooth functional **precisely because** the weights have variance 1. **So this must not be
read as showing `C_stat` is mis-normalized, and in particular it does not license a `√2` rescaling.** Anyone
who takes `N_eff = N/2` as evidence of mis-scaling will "fix" a construction that is correct.

**What the arithmetic DOES establish is sharper than the halving, and it is the part that bears on a trained
network:** with `Poisson(1)` weights, **`1/e` = 36.8% of rows receive weight exactly zero** (measured:
`0.36779`), so **each replica's training sees only 63.2% of the DISTINCT rows.** For a smooth functional the
distinct-row count is not a separate quantity — `N_eff` carries everything. **For a network trained to
convergence, coverage of the input space is a separate quantity from effective weight**, and a third of the
support being absent is not a first-order perturbation of the empirical measure.

**So the live claim is precisely the bootstrap's own regularity assumption:** the Poisson bootstrap is valid
for a **smooth functional of the empirical measure**, and whether a trained network is one — at the level
this bootstrap assumes — is exactly what is in question.

### AND THAT IS `(b)` REPAIRED, WHICH CHANGES THE ITEM'S STATE FROM "ALL THREE BROKEN"

`(b)` as written is *"a Poisson bootstrap of **the measured leg** is not a valid uncertainty proxy for this
estimator."* Repair the leg — three streams, not one, per §1 — and the claim becomes the smoothness claim
above. **And unlike `(b)`-as-written, the repaired form has a LOCATION limb: if the estimator is not smooth
in the empirical measure then `E[T(resample)] ≠ T(data)`, which is a statement about where the family mean
sits relative to the nominal. So the repaired `(b)` escapes my §1 type mismatch.**

**So the branch set was not so much MISSING a branch as UNDER-STATING one**, which is a more useful
conclusion than *"all three named branches are broken"* — and it is compatible with it: **`(b)`-as-written
stays refuted (wrong leg, and dispersion-only), and `(b)`-as-repaired is the live conjecture, which owes its
own prediction and does not inherit evidence from being identifiable with a branch.**

### THE FALSIFIER, AND IT IS THE CHECK I OWED `(c)` — RUN IT FIRST THIS TIME

**The mediator gave E one prediction: the effect must be *present but smaller* in the control regions, not
absent. I do not think that one can fail.** The controls already show `median z = −0.128` below 6 GeV —
small and nonzero — **so the prediction is satisfied by data already in hand, and a prediction that cannot
fail against what is already known is `BEN-403`'s defect arriving in the successor hypothesis.**

**Here is one that can fail, and it is the necessary condition of the mechanism rather than a consequence of
it.** Support thinning is **uniform**: every cell loses the same expected `36.8%` of its rows. **A mechanism
uniform in share cannot produce a band-confined effect unless it is locally amplified** — which is exactly
the objection that killed `(c)`. Losing `36.8%` of rows is harmless in a cell with many MC events and severe
in a cell with few. **So the mechanism REQUIRES the band to be the MC-sparse end of the grid.**

> **MEASURE per-cell signal-MC occupancy over the 231 live reco cells and ask whether the band is the sparse
> end. If it is not, the mechanism dies by availability exactly as `(c)` did.**

**And there is real reason to expect it might fail:** D established the 63 are the **highest-acceptance**
cells on the grid (median `a_b` `0.859` against `0.713` elsewhere) holding **26.5% of reco-accepted truth
mass**, and the band's background share sits **between** the two controls. **None of that is the profile of a
statistics-starved region.** `BEN-403`'s second rule applied to my own successor conjecture: **presence in
the construction is not activity in the region, and the availability check goes first.**

**That is the same shape as the refuted `(c)` on a different stage, and I am labelling it a CONJECTURE rather
than a branch, deliberately.** `(c)` failed partly because I let the observation write the mechanism's
predictions (`BEN-403`). **A same-shape hypothesis on a different stage is a NEW hypothesis and owes its own
independent prediction — not `(c)`'s, and not one read off the `−0.128 / +3.555 / −1.828` structure it would
be invented to explain.** Routed to E, whose probe already localises the divergence to the training leg;
**not annexed here, and not to be counted as `(c)` restored.**
