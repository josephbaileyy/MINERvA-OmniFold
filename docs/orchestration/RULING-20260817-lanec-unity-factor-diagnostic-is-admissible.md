# RULING — the unity-factor run is **NOT vacuous**, is admissible as a **DIAGNOSTIC not a member**, and is the only DIRECT test of branch (a)

**By:** lane C (PET), owner of `SPEC-20260814-gate5-cstat-construction-v1.md` and `gate5_cstat_contract.json`.
**Asked by the mediator, put to me and to Assistant separately, neither reading the other first.**
**Nothing run; nothing authorized by this ruling.** `C_stat^data` is already submitted (`57194054` /
`57194055`) and nothing here touches it.

---

## Q2 first, because if it is vacuous the rest is moot — **IT IS NOT, and the algebra is incomplete at one specific place**

The vacuity argument is: *at unity factors the replica target is the nominal target × a scalar, the MC is
unthinned, `R` is nominal — so the replica MUST reproduce the nominal.* **Three of those four are right.**

- **`R`: identical.** Unity data factor → `n_data_eff = sum(ones) = n_data_rows`, the nominal value
  (`:945-951`). ✓
- **MC: unthinned.** `w_truth_full[imc] · ones`. ✓
- **`imc`: identical.** The replica driver reaches `nominal.main([...])` without `--estimator-seed`, so
  `subsample_seed = 0` from `NOMINAL_SEED_POLICY` — **the same 2,000,000-row subsample.** ✓

> **THE FOURTH IS NOT. The nominal CONSUMES the archived Gate-2 target; a unity-factor replica REBUILDS it
> through the trained Stay-Positive refinement.** `fullevent_fps_dataloader.py:1462-1487` is explicit that
> Gate 5 *"requires a negweight-refined target built PER REPLICA (ROOT)"*, and the production refinement is
> `u2d.refine_stay_positive` — **a fit, not the closed form.** So the two targets differ by the **refit
> residual**, which is not zero. *(**Magnitude SUPERSEDED — see §Q2b: `0.068%` was the shared SCALAR, not a residual; the measured per-row residual is median `0.0805%`, p99 `6.888%`. The argument's STRUCTURE is unchanged and its magnitude improves.*)

**So a unity-factor replica differs from the nominal by exactly two things: a target perturbation and one
process's nondeterminism. Not by nothing.** *(Magnitude per §Q2b, not the `0.068%` written below.)*

**Therefore the experiment asks a real question with a real answer:**

> **Does a `0.068%` input perturbation produce the band's `186.1%` displacement** (`nom/mean = 2.8610` →
> `|ratio − 1| = 186.1%`)?

~~**That is an amplification of `2.7 × 10³`.**~~ **SUPERSEDED: `2313×` at the median residual, `27×` at p99 (§Q2b).** It is not a check that cannot fail — **it is a check whose failure has a name.**

## Q2b — ⚠ **RE-RULED on the re-priced object. The `0.068%` was the SCALAR, not a residual — and that makes the experiment STRONGER**

**`FINDING-20260817-the-identity-claim-is-three-orders-too-strong.md` (`a17b8401`) is accepted.** Verified
here: `(1.000680923461914 − 1) × 100 = 0.0680923461914` **exactly** — so *"targets agree to 0.068%"* was the
**shared scalar**, not a residual bound, and the campaign carried it for two days as the latter. **My §Q2
used it as the latter too.**

**The measured per-row residual against the multiplicative identity is LARGER than the number I used, so the
required amplification FALLS:**

| | residual | amplification to `186.1%` |
|---|---|---|
| median | **`0.0805%`** | **`2313×`** |
| p90 | **`0.8286%`** | **`225×`** |
| p99 | **`6.888%`** | **`27×`** |

> **A `27×` amplification is enormously more plausible than the `2.7 × 10³` I quoted. So the correction
> strengthens the experiment's discriminating power rather than weakening it — the input perturbation is
> bigger than I said, and the hypothesis it tests is correspondingly cheaper to believe.**

### DISPUTED — *"the OI-126 target route is dead"* does not follow from draw-independence

The finding measures the residual as **draw-independent**: `8.047e-04` at `data_factor == 1` against
`8.022e-04` at `≥ 2`. **The inference drawn from it — that it cannot produce a family displacement — is the
type mismatch I named in `OI-126`'s original branch set, now inside the argument that retires the route.**

> **Draw-independence rules out a VARIANCE mechanism. The `OI-126` observation is a LOCATION failure — the
> NOMINAL sitting outside its own family, common-mode across all fifty replicas.** And a **draw-independent,
> common archived-vs-rebuilt offset is exactly the right SHAPE for a common nominal-vs-family
> displacement.** Nothing about the observation requires the offset to grow with the draw; the family's
> *width* is not what is anomalous.

**So the target route is not dead. It requires the amplification in the table above — which is precisely
what the unity-factor control measures.** The control **is** the target route's test, and the finding has
made that test cheaper to justify rather than unnecessary.

### Category re-pricing — accepted in part, and it settles `BEN-404` from a second direction

*"A Gate-2 reproducibility control, not an `OI-126` experiment"* — **these are the same run under two
descriptions, and a description does not change what a run measures.** What the re-pricing **does** settle:
**`BEN-404`'s third-product question definitively does not apply**, confirming from a second direction what
§Q1 ruled — a control that reproduces an archived target builds no covariance, so nothing trips.

**`U1`–`U4` stand unchanged, and `U2` matters MORE under the new description:** a Gate-2 control must not
write into **either** family root.

### Thresholds REVISED — before the run, and recorded as a revision

Per `BEN-403`, a threshold may be revised only before the result exists. **This is that moment.**

- **Vacuity floor `< 0.068%` → `< 0.0805%`**, the measured median per-row residual. The old floor was derived
  from a number now shown to be the scalar.
- **`REPRODUCES ≤ 5%` STANDS** — still `62×` the median input — **with a rider that is part of the
  threshold: the input's p99 is `6.888%`, so INDIVIDUAL CELLS CAN EXCEED 5% FROM THE INPUT ALONE. The
  statistic is the band MEDIAN, and per-cell excursions must not be read as failures.**
- **`≥ 50%` does not reproduce; between is indeterminate** — unchanged.

**And the caveat that must not travel is also the reason the thresholds are on the median:** the finding's
`">1%: 8.456%"` tail is **unconditioned and has a near-zero-denominator pathology (max `686`)**. **A tail
fraction would inherit that; a median does not.** Stated so the choice reads as principled rather than
lucky.

### And `BEN-383`'s backend candidate is retired on MECHANISM — which refines my own `BEN-402`

`G2_GATE2_TARGET_RUNTIME_RECEIPT.json` carries `max_mc_events: 200000` and `refinement_random_state: 45`
(**verified here**) — **identical to the replica builder. So no backend difference has a mechanism.**

> **This refines `BEN-402`, which I filed carrying `BEN-383`'s phrase *"the two arms use different
> Stay-Positive backends"*. That is RIGHT about CONSUME-versus-REBUILD and WRONG if read as
> DIFFERENT-ALGORITHM.** The rebuild-is-required claim stands and is the load-bearing half; the
> different-configuration reading is refuted. **Anyone quoting `BEN-402` for a config difference is quoting
> it for the half that died.**

## Q3 — the mechanism that would make it fail is **branch (a), as a FACT**

**A `0.068%` → `186%` amplification IS *"the estimator is honestly unstable at p‖ 6–20."*** So:

| outcome | what it establishes |
|---|---|
| **reproduces** | the replica path is faithful **and** the estimator is not catastrophically unstable at these cells — so the displacement must come from the FACTORS, i.e. from the draw |
| **does not reproduce** | **branch (a) MEASURED DIRECTLY** rather than inferred, or a replica-path construction defect independent of any statistical question |

**This is the only DIRECT test of (a) anyone has proposed**, and it is why the mediator could not name a
mechanism: **the mechanism is the hypothesis under test.** An inability to name a mechanism is evidence for
vacuity only when the hypothesis space is closed; here `(a)` sits in it unmeasured.

**And it survives my own ruling that `(a)` is incoherent AS A DISPOSITION.** *(a)-as-fact* and
*(a)-as-disposition* are different claims: publishing bands that do not contain their own central value is
incoherent **whether or not** the estimator is unstable. **So `(a)`'s factual limb was never refuted and is
still worth measuring.** I should have separated those two in the original ruling and did not.

## Q1 — the contract does NOT admit it as a MEMBER, and it does not need to be one

**Correct that `CSTAT-D4`, the reconciler's four pairwise-distinctness labels, and F7's *"one coherent Poisson
factor per inventory member"* all assume a genuine draw. A unity-factor artifact is not a family member and
must never be one.**

**But it is not a third PRODUCT either, and `BEN-404` does not make it one.** `BEN-404`'s subject is a guard a
new **product** trips deliberately. **A product is something a covariance is built from; this builds none, so
nothing trips.** It is a **diagnostic**, and its cost stays **one CPU target + one training**, not fifty.

**Admissible under four requirements, all mechanical:**

| | requirement |
|---|---|
| **`U1`** | its own tag — `diagnostic-unity-v1` — so `P1` and `T1` **reject** it by construction and it can never be read as a member of either product |
| **`U2`** | its own output root, disjoint from **both** family roots, so `L2`'s tag⟺root assertion rejects it from each |
| **`U3`** | **the reconciler never sees it**, and it is counted in no `n`. It is not a 51st member of anything |
| **`U4`** | the existing three-stream replay assertions **branch on `U1`'s tag** and assert unity, exactly as `T2`/`T3`/`T5` do for `C_stat^data` — **never skip** (`BEN-404`) |

## The pre-registered outcome thresholds, because `BEN-403` applies to my own non-vacuity argument

**A single replica has no family, so `z` is unavailable. The statistic is the per-cell ratio
`unity_replica / nominal`, band median of `|ratio − 1|`, on the band's existing 84 cell indices — not
re-selected.** Fixed **before** the run:

| outcome | condition | derivation |
|---|---|---|
| **REPRODUCES** | band median `|ratio − 1| ≤ 5%` | a generous multiple of `VL130`'s top-occupancy process floor `2.156%`; the band is high-occupancy (`26.5%` of reco-accepted truth mass) |
| **DOES NOT REPRODUCE** | band median `|ratio − 1| ≥ 50%` | a third of the observed `186.1%` |
| **INDETERMINATE** | between | the perturbation propagates but not fully — informative, and not a failure of the experiment |
| **⚠ VACUOUS AFTER ALL** | band median `|ratio − 1| < 0.068%` | **below the target refit residual, so the experiment resolved less than its own input perturbation.** Recorded as a possible outcome rather than counted as success |

**That last row is a pre-registered vacuity check on my own argument for non-vacuity** — because a
non-vacuity claim that cannot come out wrong is the same defect as the vacuity worry it answers.

## Q4 (invited) — `4.6σ` should be WITHDRAWN, and NOT replaced by `3.6σ` either

**The tracked, single-source, single-domain figures**
(`RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json`, `per_cell_z = (nominal − family
mean)/family sd`):

| region | `n` | median `z` | above all 50 |
|---|---|---|---|
| band cols 10–15 | 84 | **`+3.5546`** | **44** |
| the 63 | 63 | **`+3.8089`** | **44** |

**And `family_mean/nominal` on that receipt is `1/2.8610 = 0.3495`, NOT `0.246`.** So the `0.246` in the
`4.6σ` derivation is not the band's tracked value. **I could not locate `0.246` as a Gate-5 quantity in any
tracked receipt and I am not going to guess where it came from** — `0.2465231293324187` does occur in three
Gate-6 files, but as `THE_CRITERION/per_member_dev/m5` and `absolute_deviation_from_one[2]`, **Gate-6 ML
trajectory statistics with no relation to `family_mean/nominal`. A value match is evidence about the search,
not about the derivation** (`BEN-235`), so I record the coincidence and draw nothing from it.

**AND THE SHARPER CORRECTION, which makes the item smaller AND better-founded: a median of per-cell `z` over
84 correlated cells IS NOT A σ AT ALL.** Reporting it as `3.6σ` is a category slip of the same family as
sd-versus-variance. **The honest form is two statements, neither a significance:**

> **the median cell in the band sits `3.55` family-sd above the family mean, and the nominal exceeds all fifty
> members in `44` of `84` cells.**

**So the item is not "`3.6σ` instead of `4.6σ`". It is "a `3.55` family-sd median displacement, which is not
a σ and must not be reported as one."** `4.6σ` should be withdrawn wherever it travelled, **including from the
report to Joseph an hour ago** — third instance today of a figure assembled across receipts.

## Disposition

- **NOT vacuous** (Q2) — the nominal consumes the archived target while the replica rebuilds it; the gap is
  the measured `0.068%` refit residual plus process noise.
- **Admissible as a DIAGNOSTIC, not a member, not a third product** (Q1) — under `U1`–`U4`, cost one target +
  one training.
- **It is the only DIRECT test of `(a)`-as-fact** (Q3), and `(a)`-as-fact was never refuted — only
  `(a)`-as-disposition was.
- **Thresholds pre-registered above, including a vacuity outcome.** They must not be revised after the run.
- **`4.6σ` withdrawn; `3.6σ` not adopted in its place** (Q4).
- **I am NOT authorizing the ~3 A100-h.** It is Joseph's, with its unit, and this ruling says only that the
  experiment is sound and admissible — **not that it should be bought.**
- **Nothing run. `C_stat^data`'s submission is untouched.** Five Gate-6 prohibitions at `19585b7` live;
  `C_ML` prohibited; `§3` of `CRITERIA-20260811` operative; `M(ii)` stays `(B)`, magnitude UNMEASURED.

*Lane C (PET). Filed with `BEN-421`.*
