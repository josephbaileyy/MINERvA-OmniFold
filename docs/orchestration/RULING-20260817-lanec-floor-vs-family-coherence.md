# RULING — does the Gate-6 fixed-seed floor bound the Gate-5 `C_stat` family's refit noise?

**Asked of:** lane C (PET), as owner of `SPEC-20260814-gate5-cstat-construction-v1.md` and
`gate5_cstat_contract.json`. **Dispatched by the mediator, 2026-08-17**, as item 3 of the fixed-net
proposal's own precondition list — *"whether the comparison is coherent under the `C_stat` contract … is a
spec question, not a compute question."*

**The number under test:** family per-cell `rel_sd` median in the 63-cell tail **`67.1164%`** against a
floor median **`8.6088%`** (`7.80×`), or **`9.344%`** bias-corrected (`7.18×`).

**ANSWER: NO — not as an identity, and not as a bound in either direction. But the specific incoherence
the dispatch names is NOT the one that is present, and the underlying question has a robust answer that
survives every defect below.** Nothing was run to produce this ruling; it is read from committed
artifacts and code.

---

## 1. The worry as posed — "a Gate-6-ML-config floor vs the Gate-5 family" — DISSOLVES

There is **no estimator-config difference.** Both sides are the same driver at the same pinned policy,
verified at five sites this turn rather than recalled:

| | floor draws | `C_stat` family members |
|---|---|---|
| driver | `sbatch_pet_fullevent_floor_replicate_array.sh:56` → `train_fullevent_nominal.py` | `train_fullevent_replica.py:236` → `nominal.main([...])` |
| estimator seed | `:49` `EST=42`, passed `:185-186` | defaulted from `NOMINAL_SEED_POLICY` (`train_fullevent_nominal.py:69` = `42`, `:335`) |
| subsample seed | `:50` `SUB=0`, passed `:185-186` | same policy, `subsample_seed: 0` |
| config | `niter: 3, epochs: 8` (`NOMINAL_SEED_POLICY`) | identical policy, **fail-closed** on drift at `train_fullevent_replica.py:275` |
| seeding call | `train_fullevent_nominal.py:376` `tf.keras.utils.set_random_seed(...)` | same line, same call |

And it is **measured, not merely configured**: `gate5_cstat_contract.json`'s
`measurements_at_50of50.seed_policy_holds_50_of_50 = True`, and all 50 `GATE5_REPLICA_WEIGHTS.npz` carry
exactly one `seed_policy` with `estimator_seed: 42`.

**So `7.80×` is not a ratio between two different noise sources in the sense the dispatch feared.** That
half of the worry is answered and should be dropped rather than carried as a caveat.

## 2. What IS incoherent, in order of how much it costs

### (a) THE FLOOR IS ON `central_vector`; THE FAMILY IS ON `xsec`. Different keys, and the mismatch has a KNOWN DIRECTION.

> **CONFIRMED IN CODE 2026-08-17, not conjectured — and the confirming file predated the question.**
> `docs/orchestration/state/probe-oi126-tail-floor-20260817.py`, the probe that produced the `8.6088%`
> itself, does both halves in one file:
>
> ```
> :21   X = np.array([np.load(p)["xsec"].ravel(order="C") for p in ... GATE5_REPLICA_XSEC.npz])   # family
> :30   F.append(np.asarray(z["central_vector"]))                                                  # floor
> :38   rsd = A.std(0, ddof=1) / mu                                                                # same fn, both
> ```
>
> **So the ratio is `rel_sd` of `xsec` over `rel_sd` of `central_vector`, established from the producing
> code rather than inferred.** And the probe's docstring is *titled* `COMPARABILITY` — it caught the
> `range/mean` vs `rel_sd` trap and concluded *"only `rel_sd` is comparable to the family's."* **That is
> true of the statistic and false of the quantity: a `rel_sd` of a different key is still not comparable.
> A comparability check that ran on one axis licenses nothing on another** (`BEN-386`'s shape).

`docs/orchestration/state/probe-oi120a-csyst-k-20260814.py:29` — the probe that produced `VL130` —
reads the same **`z["central_vector"]`**. `VL130`'s own ledger text states the consequence:

> **"SHAPE ONLY** — `central_vector` sums to 1 by construction, so it is blind to normalization and
> **understates** the absolute noise."

The family's `67.1164%` is per-cell `rel_sd` of **`xsec`** — the density this spec pins as the covaried
key (`CSTAT-D0`), carrying normalization by construction. **A shape-constrained `rel_sd` in the
denominator against an absolute-scale `rel_sd` in the numerator is a cross-unit ratio.**

**And the direction is the load-bearing part: the denominator is too small by an unmeasured amount, so
`7.18×` is an UPPER bound on the true ratio and the floor's share is UNDERSTATED.** That is the same
direction as the reading the dispatch offers under its branch (1) — *"the floor explains about one
seventh, which points away from process noise"* — so **the defect biases toward the conclusion being
drawn from it.** That is the reason this cannot travel as-is, independent of how large the bias is.

### (b) `FLOOR_INTERMEDIATE` IS THE WRONG BRAKE — it belongs to a different functional.

The dispatch's item 3 attaches `56863958`'s `FLOOR_INTERMEDIATE` verdict to the `8.6088%`. **They are two
different measurements on the same draws:**

- **`VL128`** — `F_range[2] = 0.06452911345365375` on the **iteration-2 trajectory scalar `v`**, against
  frozen thresholds `0.05` and `0.174002988730091`. **This** is what returned `FLOOR_INTERMEDIATE`, and
  its own prohibition list says the verdict *"licenses nothing."*
- **`VL130`** — per-bin fractional noise on `central_vector`, `n=5` TERMINAL, `PROVISIONAL`, shape-only.
  **This** is the per-cell floor. `FLOOR_INTERMEDIATE` says nothing about it.

**So the per-cell floor's brake is not `FLOOR_INTERMEDIATE`; it is `VL130`'s own:** `PROVISIONAL`,
shape-only. **And the tail floor is a DIFFERENT POPULATION from `VL130`'s**: `probe-oi126-tail-floor-20260817.py:28`
iterates `for n in (2, 3, 4, 5)` over `fullevent_floor_42_0/draw_{n}` — **`n=4`**, excluding draw 1, which
the `56863958` receipt records as *"EXISTING `member_1` artifact, reused unmodified, NOT retrained"* and
which lives under `fullevent_ml_ensemble/`, outside the floor directory. So the applicable per-sd
fractional uncertainty is `1/√(2·3)` = **`40.82%`**, the `n=4` figure, not `VL130`'s `35.36%`. **On the
denominator alone that puts `7.18×` at `5.10×`–`12.13×`.** *"About one seventh"* is really *"between a
tenth and a fifth"* before anything else in this section.

> **RIDER WITHDRAWN, and the withdrawal is the more useful record.** I raised, as a question, that the
> dispatch bias-corrected with `c4(n=4) = 0.9213` while `VL130` is `n=5` TERMINAL. **`n=4` is correct** —
> `:28` reads four draws, for the good reason above. **The question was already answered in the file that
> produced the number, which landed at `a80b167`, `2026-08-17T14:42:36-04:00`, and this ruling at
> `15:02:20-04:00` — twenty minutes later.** So I asked instead of reading, and the artifact was there.
> **That is `BEN-239` — evidence sitting unread — committed ONE COMMIT after I filed it** (`0eb1f80`).
> The finding's own rule applied to itself: *"no document I read answers this" is a claim about the
> reader.* Recorded here rather than in the row, because the row already states the class and what this
> adds is that stating a class does not inoculate the stater.

### (c) THE TWO SIDES ARE STRATIFIED BY DIFFERENT VARIABLES, so a single median over the tail averages over the axis each one depends on.

- **The floor depends on OCCUPANCY.** `VL130`: `corr(frac, log occupancy) = −0.6249`, spanning
  **`2.156%`** (top quartile, 71.20% of the spectrum) to **`26.79%`** (lowest quartile, 0.51%) — a
  **`12.4×`** swing. Its unweighted per-bin median is `6.288%`, and the ledger says quoting *that* would
  be *"2.5× the number that matters."*
- **The family's tail spread depends on ACCEPTANCE, in the opposite sense.** `RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json`:
  median `rel_sd` is `4.97%` where `a_b < 0.05` and `24.34%` where `a_b > 0.5`, *"because where acceptance
  is ~0 the answer is the prior and the prior does not fluctuate across replicas."*

**The 63 are the highest-acceptance cells on the grid** (median `a_b` `0.8586` vs `0.7130` for the other
194; `26.51%` of reco-accepted truth mass; one 4-connected component, `p‖ 6–20 GeV`). **So my own prior
that they were sparse edge cells is refuted** — B established that, and it inverts which end of `VL130`'s
occupancy range is the relevant one.

**What this leaves unsettled:** `8.6088%` is ~4× `VL130`'s top-quartile median (`2.156%`) and ~1.4× its
unweighted median. **Whether that is consistent requires placing the 63 in `VL130`'s OWN occupancy strata**
— which needs the probe's `occ` array, not B's truth-mass shares, because they are different occupancy
measures. **One command for whoever holds the arrays; not resolvable from the committed receipts.**

**Domain footnote:** the floor's domain is the training artifact's `reported_bin_mask` (`h_prior > 0` on
the 2M subsample, **259** cells); the family arrays are the **257** quotable cells (262 union minus the 5
flicker cells, `CSTAT-D3c`). `VL130`'s own note says **"no consumer may take a training artifact's mask as
the reporting domain."** All 63 tail cells are covered by both, so the tail comparison survives — but
`VL130`'s quartile boundaries are computed over its 259, not over the 257.

### (d) DATA-DEPENDENCE — the floor is measured on UNPERTURBED data and applied to PERTURBED members. This is `CSTAT-O2a`, and it is HELD, not unnoticed.

The floor draws run at **`bootstrap_seed = -1`** on identical inputs and identical 2,000,000-row
`mc_indices`. The family members run at **`bootstrap_seed = 50000 + replica_index`** on perturbed data.
`gate5_cstat_contract.json`, `CSTAT-O2a`, verbatim:

> *"Leg F measures the floor **ON THE NOMINAL**. `CSTAT-O2a` would measure it on a **BOOTSTRAP-PERTURBED**
> dataset, which is the condition that actually obtains inside this family. **If the floor is
> data-dependent, subtracting the nominal's floor from the family's spread is an APPROXIMATION, not an
> identity.** Use `VL130` now; run `CSTAT-O2a` only if the subtraction proves sensitive to that
> difference."*

**Direction unmeasured. So it is an approximation with a named, untested sensitivity — which is why the
answer to "does it bound" is `no` rather than `yes with a caveat`.**

**AND THE PROBE ALREADY BRAKED ITSELF, which should travel with the number:**
`probe-oi126-tail-floor-20260817.py:61-62` prints *"TRAP 1 STILL APPLIES: n=4 against n=50. An sd from four
draws is a noisy estimate; the direction of any bias is NOT established here and **this ratio is indicative
only**."* **The producing code labelled its own output indicative-only. Nothing in §2 contradicts that
label — §2 says why the label cannot be lifted by adding draws**, since more draws fix `n` and fix neither
the key mismatch nor the stratification gap.

**AND A CORRECTION TO THE DISPATCH'S GROUNDING, which changes what the ask to Joseph would be.** The
dispatch's branch (2) calls a Gate-5-condition identical-seed repeat *"`INV-129`'s mandate for the
`C_stat` half, never run."* **`INV-129` does not say that.** Read at
`COVERAGE-SURVEY-20260802.md:1343-1346`, its mandate is *"GPU FLOOR: **1 identical-seed repeat**; record
before interpreting `C_stat`/`C_ML`"*, and its stated checkability requirement is *"a floor receipt whose
`seed_policy` is compared byte-for-byte against the nominal's."* **Leg F is that, four times over, and
`VL130` verified exactly those premises.** `INV-129` says nothing about the perturbed condition.

**So the gap is not an unmet invariant — it is `CSTAT-O2a`, a held approximation with a predeclared
trigger.** That matters for the ask: *"an invariant is unsatisfied"* reads as a compliance failure that
must be cured; *"a held approximation's sensitivity has never been tested"* is a judgement call whose
trigger condition is already written down. **This ratio is arguably that trigger firing.**

**What `INV-129` IS still missing is its check, not its measurement** — the survey's *"nothing asserts the
floor run used identical seeds"* remains true as a mechanism even though `VL130` asserts and verifies it in
prose. `CLAUDE.md`'s own preference applies: *prefer the executable form of any rule you are tempted to
write down.*

## 3. THE UNDERLYING QUESTION HAS A ROBUST ANSWER, AND IT IS NOT THE RATIO

The ratio is the wrong statistic for the word *"explains."* **Noise adds in quadrature** — `VL130`'s own
ledger uses `δ_meas² = δ_phys² + (f/√k)²` — so the floor's *share of the tail spread* is a **variance**
share, not an sd ratio:

| floor used | sd ratio | **variance share** | tail after quadrature subtraction | reduction |
|---|---|---|---|---|
| `8.6088%` as reported | `7.80×` | **`1.65%`** | `67.1164% → 66.5620%` | `0.83%` |
| `9.344%` as bias-corrected | `7.18×` | **`1.94%`** | `→ 66.4628%` | `0.97%` |
| `9.1583%` at `c4(n=5)` | `7.33×` | **`1.86%`** | `→ 66.4887%` | `0.94%` |
| **`4×` the reported floor** (`34.44%`) | `1.95×` | `26.32%` | `→ 57.6093%` | `14.17%` |
| `VL130` lowest-occupancy median `26.79%` | `2.51×` | `15.94%` | `→ 61.5367%` | `8.31%` |

**`"the floor explains about one seventh"` is true of the sd ratio and false of the thing the word
`explains` names: the floor accounts for `1.9%` of the tail VARIANCE — one fifty-second, not one
seventh.** Removing it entirely moves the tail spread from `67.1164%` to `66.46%`.

**And that conclusion is robust to every defect in §2.** Even understating the floor by `4×` — far beyond
the `35.36%` uncertainty, the shape-only bias and the stratification gap combined — leaves it at `26%` of
the variance and the tail spread above `57%`. **So: the RATIO is not a legitimate quantity as posed, and
the QUESTION it was asked to settle has an answer that survives fixing it.** The floor is not the
explanation for the tail spread.

**What I am NOT saying**, and it is the dispatch's own boundary, kept: this does not adjudicate branch (a)
vs (b). *"Not process noise"* is one input to that and the residual-bias question is another; the
adjudication belongs to whoever owns the physics, and not on a single ratio.

## 4. Disposition

- **The `7.80×` / `7.18×` ratio: DO NOT QUOTE.** Cross-unit (`central_vector` vs `xsec`), biased in the
  direction of the conclusion, wrong brake attached, `n` unstated, and `±35%` on its denominator alone.
- **The finding it was reaching for: STANDS, on the variance share** — `1.9%`, robust to a `4×` floor
  error. **State it in quadrature with its operands, never as an sd ratio.**
- **`CSTAT-O2a`: STAYS HELD.** Its trigger is *"only if the subtraction proves sensitive to that
  difference"*, and §3 shows the subtraction is **insensitive** — a `4×` change in the floor moves the
  tail spread by `9.5` percentage points and changes no conclusion. **So this ratio does not fire the
  trigger, and the ask to Joseph in the dispatch's branch (2) is NOT yet warranted.** That is the
  cheapest of the available answers and it is the one the evidence supports.
- **Open and one command for whoever holds the arrays:** the 63's placement in `VL130`'s own occupancy
  strata. It cannot change §3's conclusion; it can change whether `8.6088%` is the right floor to have
  reported.
- **Nothing run. `§3` of `CRITERIA-20260811` as written stays operative; `M(ii)` stays `(B)`, magnitude
  UNMEASURED; the five Gate-6 prohibitions at `19585b7` stay live; `C_ML` construction remains
  prohibited.**

*Lane C (PET). Assistant reviewed the statistic and the residual-bias direction independently and neither
of us read the other's answer before forming ours — the mediator's instruction, and the reason two
accounts of this number are worth having.*
