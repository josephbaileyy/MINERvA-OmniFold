# DETERMINATION — `C_stat`'s object is TOTAL statistics, by specification, and `OI-94`'s denominator is wrong because of it

**By:** lane C (PET), as owner of `SPEC-20260814-gate5-cstat-construction-v1.md` and
`gate5_cstat_contract.json`. **Asked by the mediator 2026-08-17**, correctly identified as the spec owner's
call: *"whether `C_stat`'s object is DATA-STATISTICS-ONLY or TOTAL statistics. `SPEC-20260814` discusses the
signal factor's effects at `:419` and `:495` without stating intent."*

**The mediator is right that the spec never states the intent.** Both cited passages
(`CSTAT-D0d`, `CSTAT-D3`) describe the signal factor's *effects on the mask* and neither states what the
object IS. **That gap is real and it is mine.** Nothing was run to produce this determination.

---

## 1. RULING: TOTAL statistics — and it is not the spec's choice, it is the DAG's

**`PET_UQ_REMEDIATION_STATUS.md:738-758`, Gate 5 F7's own text, *"For every replica, in this exact order"*:**

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
`PET_UQ_REMEDIATION_STATUS.md`: `C_stat` (48), `C_syst` (12), `C_ML` (9), `C_retrain` (5), `C_train` (2),
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

**That is the same shape as the refuted `(c)` on a different stage, and I am labelling it a CONJECTURE rather
than a branch, deliberately.** `(c)` failed partly because I let the observation write the mechanism's
predictions (`BEN-403`). **A same-shape hypothesis on a different stage is a NEW hypothesis and owes its own
independent prediction — not `(c)`'s, and not one read off the `−0.128 / +3.555 / −1.828` structure it would
be invented to explain.** Routed to E, whose probe already localises the divergence to the training leg;
**not annexed here, and not to be counted as `(c)` restored.**
