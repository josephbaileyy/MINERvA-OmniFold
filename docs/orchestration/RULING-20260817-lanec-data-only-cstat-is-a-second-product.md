# RULING — the data-only ensemble is **(A) a second product**, and `(B)` is not merely a heavier bar but substantively wrong

**By:** lane C (PET), as owner of `SPEC-20260814-gate5-cstat-construction-v1.md` and
`gate5_cstat_contract.json`. **Step 1 of the mediator's dispatch on
`AUTHORIZATION-20260817-data-only-cstat-second-ensemble.md` (`9dae576`), Joseph's *"Do it. I authorize
both."*** **Nothing is written or submitted. E's step 2 does not start until this lands.**

**Nothing was run to produce this ruling.** Everything below is read from committed code and receipts.

---

## 0. RULING: **(A)**, and it is FORCED rather than chosen

**Joseph's argument and mine are about different objects, which is why both can be right.** Mine: the
declared budget has nowhere else to put MC statistics (`C_MCstat` occurs zero times; `C_syst` universes
vary physics **parameters**, not sample size). His: *"statistical"* must mean what the field means, and an
error that is ~88% MC statistics by variance is neither comparable to MINERvA's own nor profilable as a
nuisance in a global fit — **and is reducible by generating more MC, which is precisely what `σ_stat` is
not.** **Neither refutes the other. Two arguments about two objects entail two objects.**

**And `(B)` is not just a DAG amendment needing its own bar — it is WRONG on the merits.** Amending Gate 5
F7 to data-only would **discard the only component in the declared budget that carries MC statistics**, so
MC statistics would vanish from `C_total` entirely. **That is the defect my own §2 identified, enacted.**
So `(B)` is unavailable independent of whether a DAG amendment could clear its bar, and the answer to
*"is the amendment warranted"* is **no** — the second ensemble is wanted **because** the first one measures
something real that the field will not accept under that name.

**The existing three-stream family is NOT superseded, NOT discarded, NOT re-verdicted.** The mediator's
assumption in the authorization is correct.

## 1. The stated relationship — and the difference IS the missing component

**Names, because `C_stat` is now ambiguous and the ambiguity is what the `OI-126` row already tripped on:**

| product | what varies | role |
|---|---|---|
| **`C_stat^data`** | data factors only; signal and background factors **exactly 1** | **the published `σ_stat`** — field-comparable, not reducible by generating MC |
| **`C_stat^total`** | all three, as Gate 5 F7 specifies | **existing, unchanged**, `GATE5_CSTAT_N50.npz` |
| **`C_MCstat`** | *(derived)* | the component the budget has no name for |

**`C_MCstat := C_stat^total − C_stat^data`, and this subtraction carries a REQUIREMENT, not a convenience.**

> **The difference of two covariances is not a covariance. It must be checked PSD before it is called one,
> and if it is not PSD it must not be published as a covariance under any name.**
>
> **Why this is not pedantry:** the two families' estimates pass through **the same trained network**, so
> the data-stream and MC-stream perturbations are **not independent**, and `C_total ≠ C_data + C_MC` in
> general. **I am naming this before it happens because I committed the same error family this afternoon** —
> a quadrature step whose independence assumption `VL130` says `n=4` cannot test (`BEN-403`). **The
> arithmetic of subtraction is not the physics of decomposition.**
>
> **The PSD check is the gate on cost.** If `C_stat^total − C_stat^data` is PSD, the subtraction is the
> cheap route and no third product is needed. **If it is not, defining `C_MCstat` as a covariance requires
> an MC-only ensemble (data factors pinned, signal and background drawn) — a THIRD product at a third
> spend. I am NOT proposing it and it must not be pre-authorized by this ruling.** The PSD check costs
> nothing and decides.

## 2. Q1 — DATA ONLY. The background stream is MC, and that is decisive rather than conventional

**The mediator's argument for including background is that background-subtraction uncertainty is
conventionally statistical *when the background is measured*. Here it is not measured.**

`nd-unfolding/pet/fullevent_fps_dataloader.py`, read this turn:

- `:568` — *"F7 — coherent estimator-bootstrap over THREE inventories (data, signal-MC, **background-MC**)"*
- `:615` — *"Three GLOBAL Poisson(1) factors over the full data / signal-MC / **background-MC**
  inventories"*
- `:679`, `:879` — the background factor multiplies the **negative injection weight**, POT-scaled
  (`:1292`), i.e. an MC prediction scaled to exposure, not a sideband count.

**So the background stream's Poisson is MC statistics: it is reducible by generating more background MC,
which is the exact property Joseph's objection is about.** Including it in `C_stat^data` would put **87% of
the counting floor** back into the published `σ_stat` and **defeat the product's entire purpose.**

**`C_stat^data` varies the DATA factor only.** *(This is the highest-leverage of the three questions —
87.06% of the counting-floor variance turns on it — and it is settled by what the background IS, not by a
convention about what backgrounds usually are.)*

## 3. Q2 — the centring carries over DELIBERATELY, and the containment gap is PROMOTED to a reported result

**Center `C_stat^data` on its own accepted replica mean**, matching Gate 5 F7's *"Center `C_stat` on the
accepted replica mean"* and `CSTAT-D2`. **The reason is comparability of the two products, not deference:**
if the two families are centred differently, the difference between them is no longer attributable to the
streams alone, and `C_MCstat` stops meaning anything.

**And the mediator is right that the nominal-vs-replica-mean gap is itself a result — so it is REQUIRED
OUTPUT, not a diagnostic.** Report, on the same domain and with the same estimator as the existing family:
per-cell `z = (nominal − family mean)/family sd`, `n_nominal_above_all_50`, and `median z` by region.

## 4. Q3 — the `OI-126` decision rule, DERIVED, PREDECLARED, and correcting the premise it was handed

### ⚠ First, the premise is false, and it changes the rule

The dispatch says *"a data-only family has NO nominal/replica training asymmetry."* **It does.** The **data**
factors are `Poisson(1)` too, so **36.8% of DATA rows receive weight exactly zero** in every replica
(`1/e`, measured `0.36779` — determination §4). The measured leg is what the OmniFold step-1 classifier
trains against, **so a data-only family still trains on a thinned support; only the MC part of the
asymmetry is removed.**

**Therefore `"nominal inside ⇒ it was MC-thinning"` is NOT a valid rule.** The rule must be **ordinal in
the displacement**, and all three outcomes must be informative.

### The rule, derived from the mechanism

Under support thinning, the displacement should scale with **how much of the estimator's information is
being thinned**. `C_stat^data` thins the data stream only; `C_stat^total` thins all three. **So the
mechanism predicts the displacement DECREASES and does NOT vanish.** *(An sd-proportional expectation from
the counting-floor shares would be ≈`0.346` of the current value — **stated as ORDINAL ONLY**, because
those shares are raw `1/√N` fractions and the mediator and I have both labelled them indicative. No
threshold below is set from that number.)*

### PREDECLARED — statistic, domain, regions, thresholds. Fixed BEFORE submission

- **Statistic:** `z = (nominal − family mean) / family sd`, per cell, `ddof=1`, on **`xsec`**.
- **Domain:** the intersection `(X > 0).all(axis=0)` over the new family's members, reported alongside the
  existing 257 so the two are compared as SETS and not as counts (`BEN-236`).
- **Regions, unchanged:** p‖ < 6 (128 cells) / band cols 10–15 (84) / p‖ > 20 (45), and the 63 tail cells
  **by their existing indices**, not re-selected.
- **Reference values, from `RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json`:** band
  `median z = +3.555`, `n_above_all_50 = 44` of 84.
- **Thresholds, derived from the family's own `N=50` precision** — per-sd fractional uncertainty
  `1/√(2·49) = 10.102%` (`CSTAT-R7`), so `1σ` on a `z` of `3.555` is `0.359` and `2σ` is `0.718`:

| outcome | condition (band cols 10–15) | what it means |
|---|---|---|
| **UNCHANGED** | `median z ≥ 2.837` (within `2σ` of `+3.555`) **or** `n_above_all_50 ≥ 35` | **stream-proportionality is REFUTED, and BOTH surviving conjectures die** — the displacement does not track which streams are thinned |
| **VANISHED** | `median z ≤ 2.0` **and** `n_above_all_50 = 0` | data-stream thinning contributes nothing; the mechanism is **specific to the MC legs**. Narrows, does not confirm |
| **REDUCED BUT PRESENT** | between the two | consistent with support thinning, and the RATIO becomes a measurement of its stream attribution |

**No branch is read off the `−0.128 / +3.555 / −1.828` structure** — the three exhaust the ordinal
possibilities, and the one that would be most convenient (`REDUCED`) is the only one that neither kills nor
narrows. **`BEN-403`'s rule satisfied: the predictions come from the mechanism, and `UNCHANGED` can and
would kill the hypothesis I myself am carrying.**

## 5. Buildability — a specification constraint, stated because a launcher author would otherwise decide it

**Not E's step 2, which is the code route. These are the constraints that route must satisfy.**

> ### ⚠ **CONSTRAINT (i) IS FALSIFIED. `Route A` IS NOT EXPENSIVE — IT IS SILENTLY WRONG.** Found by lane E, verified here from the tree.
>
> **The loader applies `sig_factor` ITSELF, before returning.** `fullevent_fps_dataloader.py:1321-1325`,
> inside `if bootstrap_seed is not None:`
>
> ```
> data_factor, sig_factor, bkg_factor = coherent_bootstrap_factors(M, N, n_bkg_full, int(bootstrap_seed))
> w_truth = (w_truth_full[imc] * sig_factor[imc]).astype(np.float32)
> w_reco  = (w_reco_full[imc]  * sig_factor[imc]).astype(np.float32)
> ```
>
> **So setting `sig_factor = 1` in the replica driver changes NOTHING — the thinning has already happened
> upstream of the place I prescribed the override. And it cannot be undone afterwards: 36.8% of the factors
> are exactly zero, so the multiply DESTROYS information rather than scaling it.**
>
> **`train_fullevent_replica.py:202` re-derives the factors to VERIFY the loader's, not to apply them** —
> a checker (`raise SystemExit("[gate5-train] loader bootstrap evidence carries the wrong seed")`), not an
> applier. **I read the mention and inferred the operation.**
>
> **THE ROUTE WOULD HAVE PRODUCED A FAMILY WHOSE RECEIPTS CLAIM UNITY WHILE THE TRAINING CONSUMED THINNED
> MC — a false receipt, and exactly the class this campaign spent the day refusing to ship.**
>
> **And the instrument that should catch it documents that it cannot.** `reconcile_gate5_family.py:526-530`,
> its own note, verbatim: *"it compares the BUILDER's recomputation to this tool's redraw, so it is **blind
> to what the LOADER applied**."* **The guard names its own blind spot and the blind spot is exactly where
> `Route A` would have lived.**
>
> **MY CONSTRAINT WAS RIGHT AS A PRINCIPLE AND WRONG AS A ROUTE, and the distinction is the finding:** keep
> the diff off a file pinned 25 ways — sound. *Put it in the driver* — wrong, because **the operation is not
> where the mention is.**
>
> **AND IT IS MY OWN `BEN-403(ii)` VIOLATED ONE COMMIT AFTER FILING IT.** That rule reads *"presence in the
> construction is not activity in the region — check availability where the effect is, not where the code
> is."* I filed it for a physics mechanism and then, in the next ruling, **observed that the driver MENTIONS
> the factors and inferred that it APPLIES them.** Same rule, different domain. **E's added rule — *when
> routing an edit away from a pinned file, verify the destination PERFORMS the operation rather than merely
> mentioning it* — is the code-domain statement of it, and E's second half is the part I could not have
> supplied: PREFER THE LOUD FAILURE.** `OI-61(b)` died to an `argparse choices` list — exit 2, immediate.
> **This one ships a false receipt and passes its own reconciler.**
>
> **THE VIABLE ROUTE, and E explicitly does not call it cheap:** call the loader with `bootstrap_seed=None`.
> The else-branch at `:1332-1334` returns genuinely unthinned MC (`w_truth_full[imc]`, `w_reco_full[imc]`,
> `meta["bootstrap"] = None` — verified), the driver already intercepts the loader call, and the
> measured-side helpers already default `data_factor=None` to ones (`:696`, `:945-948`), so the data stream
> can be supplied separately. **Four sites, one of them a new verdict path in the pin-exposed reconciler.**
> **E's caveat, carried: `Route A` looked viable on exactly this kind of inspection until the loader's own
> multiply was read. So `Route B` gets an EXECUTION check, not another inspection.**
>
> ### AND `Route B` HAS A SPECIFICATION CONSEQUENCE THAT MUST BE SETTLED BEFORE IT IS BUILT
>
> With `bootstrap_seed=None` the loader sets **`meta["bootstrap"] = None`** — and the reconciler reads
> `data_factor_sha256` out of exactly that dict (`bs.get("data_factor_sha256")`). **So the receipt path that
> carries the varying stream's provenance is the one `Route B` empties.** And `:527-530`'s own note calls
> `data_factor` **"THE STREAM NOTHING ELSE CHECKS — no stage persists or array-compares it."**
>
> **That is the most dangerous possible combination: in `C_stat^data` the ONLY stream that varies is the one
> the pipeline persists least.** **REQUIREMENT: the data-only verdict path must assert that the data factor
> is persisted AND array-comparable under a named key of its own, and must FAIL CLOSED if it is absent.**
> A `bootstrap: None` receipt that silently carries no data-factor hash is `Route A`'s false receipt in a
> different disguise — unity claimed by omission instead of by assertion.
> **REV-3 SHARPENING BELOW: this is right about the CLASS and wrong about WHERE the silence lives.**
>
> #### ⚠ REV 3 — the mechanism is a DEFENSIVE IDIOM, and one half of my own warning was wrong
>
> **The mediator established it.** `train_fullevent_replica.py:196` is
> `bootstrap = dict(meta.get("bootstrap") or {})` — **and the same `or {}` at `:220` and `:253`.** Python
> makes the two shapes differ, verified this turn:
>
> ```
> {"bootstrap": None}.get("bootstrap", {})  -> None -> .get(...) raises AttributeError   LOUD
> key absent, or {}                          -> {}   -> .get(...) returns None            SILENT
> ```
>
> **A `.get` default fires only when the KEY IS ABSENT, never when its value is `None`** — so `or {}` at the
> **writer** converts `ABSENT` into `EMPTY` and disarms the crash the reader would otherwise have. **A guard
> written to make a reader robust to a missing dict is what suppresses the loud failure**, and `{}` is *empty
> in content and present in type* — the one shape that defeats both a presence check and an exception.
>
> **BUT `Route B` THROUGH THE DRIVER AS IT STANDS FAILS LOUDLY, AND THAT CORRECTS MY FRAMING.** `:197` is
> `if int(bootstrap.get("bootstrap_seed", -1)) != int(args.bootstrap_seed): raise SystemExit(...)`. With
> `meta["bootstrap"] = None` the block is `{}`, the get defaults to `-1`, and for any real replica seed
> (`50000 + i`) **`-1 != 50000+i` fires and the artifact is never written.** So the silence is in the
> **reconciler**, not in the pipeline as built: **`Route B` does not currently ship a false receipt.**
>
> **The silent path is the DRIVER EDIT `Route B` REQUIRES.** `Route B` must make `:197` accept a run with no
> bootstrap block, and **the smallest-looking way to do that is to relax `:197` — exactly the edit that arms
> the reconciler's `:355`.** One relaxation converts the loud failure into the silent one.
>
> > **REQUIREMENT, replacing the weaker form above: the driver edit must BRANCH ON THE PRODUCT, never relax
> > `:197`.** The three-stream assertion stays byte-identical; the data-only path asserts a **different
> > positive** condition of its own. **`BEN-404`'s rule with a second instance and a line number — and now the
> > FIRST line of defence rather than the third.**
>
> #### AND A LATENT VACUOUS PASS THAT NEEDS NO EDIT AT ALL — `BEN-405`
>
> **`:197`'s absent-default is `-1`, and `-1` is this pipeline's own sentinel for "no bootstrap"** —
> `VL130`'s verified floor premises are *"identical inputs, identical 2,000,000-row `mc_indices`,
> **`bootstrap_seed = -1`**"*. **So a run invoked with `--bootstrap-seed -1` against an empty block compares
> `-1 != -1`, which is False, and the guard PASSES VACUOUSLY** (verified).
>
> It then dies five lines on at `:202` with `ValueError: expected non-negative integer` from
> `np.random.default_rng(-1)` (verified). **Loud, but MISATTRIBUTED — the message names an RNG problem, so a
> reader debugging it looks at numpy and not at the missing loader evidence.** **A guard whose absent-default
> collides with a meaningful domain value stops guarding exactly when that value is in use, and the failure it
> lets through resurfaces wearing someone else's name.** One-line fix, unrelated to this product: **the
> absent-default must be a value no legal seed can take** — `None` with an explicit `is None` check, not `-1`.
>
> #### THE CLEAN SPECIFICATION ANSWER, which avoids the class rather than guarding it
>
> **`C_stat^data` must NOT reuse the `bootstrap` receipt key.** Its empty form is indistinguishable from its
> absent form at **three writer sites** where `or {}` is doing what it was written to do, so any guard on it
> guards a distinction the writers have already erased. **Give the data-only product its own top-level block
> with its own required keys** — product tag, data-factor sha256, and the unthinned-MC assertion — **and leave
> `bootstrap` meaning exactly what it means today.**
>
> #### AND AN EXECUTION CONDITION, which is now a CONDITION rather than a suggestion
>
> **Whatever route lands must demonstrate on ONE replica, FROM THE ARTIFACT rather than from the code path,
> that the MC weights entering training are bit-identical to the unthinned arrays:** a `hash_array` of
> `w_truth` against `w_truth_full[imc]`, **one key in the built receipt, failing loudly.** *(The record is the
> reason: `Route A` survived inspection until someone read a multiply four hundred lines away; `Route B` has
> survived two inspections and acquired a defect in the second. **An execution check is the only thing that
> has caught anything on this item.**)*
>
> ### THE RECONCILER PROFILE IS WORSE THAN I SAID, WHICH STRENGTHENS THE "NO RELAXATION" LINE
>
> I named `:837-845`'s four distinctness labels. **E found `:519-530` ALSO replay-redraws all three streams
> and compares hashes**, so unity mismatches there **before distinctness is ever reached.** **The real
> profile is 2 of 4 distinctness PLUS 2 of 3 replay** — a shorter-looking exemption than I anticipated, and
> **the shorter it looks the more important it is that `C_stat^data` gets its own verdict path rather than a
> relaxation.** E is holding that line and it is the right line.

**(i) ~~The substitution is a VALUE change, and it must not become a pinned-file edit.~~ SUPERSEDED — see
the box above. Left as written because the reasoning is the finding.**
`coherent_bootstrap_factors(n_data, n_sig, n_bkg, seed)` (`:614-625`) returns three **arrays**, and
`reconcile_gate5_family.py` already hashes them separately (`factor_sha256` for `data`/`signal`/
`background`). **So a data-only replica is the same construction with two of three factor arrays set to
exactly `1`** — and the override belongs in the **replica driver**, which is not the pinned nominal driver,
**never inside `coherent_bootstrap_factors` itself.** Per `BEN-384` I am not costing this; I am forbidding
one route to it.

**(ii) `PREDECLARATION-20260813:58` says *"`fullevent_fps_dataloader.py` is NOT pinned"* and that is STALE.**
`BEN-384` found it pinned at `e1402370…` in `run_gate2_target_validator.sh:49` and the Gate-2 runtime
receipt, and the dispatch counts 25 digest sites. **The sentence that made loader-side work look free of the
gate no longer holds, and anyone planning this product from that predeclaration will mis-scope it.**

**(iii) THE EXISTING RECONCILER WILL FAIL THIS FAMILY BY DESIGN, AND THAT GUARD MUST NOT BE WEAKENED.**
`reconcile_gate5_family.py:837-845` requires `{label}_sha_all_distinct_across_family` for **all four**
labels, *"because identical values here would look like a small statistical component rather than a failed
draw"*. With signal and background factors set to `1`, **`signal_factor` and `background_factor` shas are
IDENTICAL across all 50 members — the exact pattern that check exists to catch, except here the collapse is
INTENDED.**

> **So `C_stat^data` needs its own verdict path with its own distinctness contract — `data_factor` and
> `target` distinct, `signal_factor` and `background_factor` required IDENTICAL — and NOT a relaxation of
> the existing checker.** Weakening a guard whose stated purpose is to catch the reassuring failure, in
> order to admit a family that trips it deliberately, would leave the three-stream family unprotected
> against the failure it was written for. *(`target_sha_all_distinct` still PASSES:
> `build_negweight_refined_target` (`:641-655`) varies the refined target through `data_factor` alone, so
> per-replica targets stay distinct even with `bkg_factor = 1`.)*

## 6. One thing that strengthens D's refutation of `(c)`, found while reading this code

`stay_positive_refine_binned` (`:628-638`) is `clip(|w| · (2g − 1), 0, None)` with `g = D/(D+B)` per cell.
**The clip — the non-affine part — is active only where `2g − 1 < 0`, i.e. `B > D`, i.e. exactly D's
`"background mass > data count"` criterion**, which is `0` of 86 band cells. **So D's proxy was not a proxy
for the mechanism; it was the mechanism's activation condition, read exactly.**

Residual nonlinearity survives through `g` itself (a ratio of sums, so `refine` is not linear in `w` even
unclipped) — **but numerator and denominator fluctuate coherently, so the leading Jensen term largely
cancels, which is why the total-level test came back at `0.03 SE` rather than merely small.** `(c)` is
properly dead, and now for a stated reason rather than an empirical one.

## 7. Disposition

- **(A). A second product under its own specification. `(B)` is refused on the merits, so no DAG amendment
  is sought and Gate 5 F7 is untouched.**
- **`C_stat^data` varies the DATA factor only** (§2). **Centred on its own replica mean** (§3), with the
  containment gap as **required output**.
- **`C_MCstat := C_stat^total − C_stat^data` is DEFINED, and it is not a covariance until the PSD check
  passes.** No third ensemble authorized or implied.
- **The `OI-126` rule is predeclared above and is fixed as of this commit. It must not be revised after the
  family lands** — and its `UNCHANGED` branch kills the conjecture I am carrying.
- **§5 constrains the build without costing it.** E's step 2 owns the route; the reconciler needs its own
  verdict path, not a weakened check.
- **This ruling authorizes no spend, lifts nothing, and writes nothing into the analysis note.** The five
  Gate-6 prohibitions at `19585b7` stay live; `C_ML` construction remains prohibited; `§3` of
  `CRITERIA-20260811` as written stays operative; `M(ii)` stays `(B)` with the magnitude UNMEASURED.

*Lane C (PET). Filed with `BEN-404`.*
