# BRIEF — `arXiv:2608.28449` (Greif thesis): what it gives the scalar-5D / GBDT covariance lane

**Filed 2026-09-01. Repo claims measured at `HEAD = b7612e6adf67a459e4c86b927355140645da214a`.**

**Source.** Kevin Greif, *A High- and Variable-Dimensional Measurement of the Z+jets Differential
Cross Section with the ATLAS Experiment and Artificial Intelligence*, PhD thesis, UC Irvine,
submitted 28 Aug 2026, 313 pp. ATLAS Z(→μμ)+jets, full charged-particle phase space, 140.1 fb⁻¹.

**This is a literature brief. It adopts nothing, discharges no quarantine cause, moves no gate,
touches no covariance or published number, and authorizes no compute.**

**Citability:** §6.1 (p. 172) — the analysis is *in ATLAS review*, paper expected September 2026, and
a conference note has been released. Most figures I read carry **ATLAS Internal** watermarks.
**Method is citable from the thesis; numbers are not.** See §0 of the companion PET brief
[`BRIEF-20260901-greif-fps-thesis-implications-for-pet.md`](BRIEF-20260901-greif-fps-thesis-implications-for-pet.md).

---

## 1. The item that most directly serves this lane

`LITERATURE_NOTES.md:164-168` records a referee concern in these words: *"all published OmniFold uses
NNs; this uses LightGBM."* The repo's answer to it today is our own classifier-calibration study
(`2d-unfolding/uq/classifier_calibration.py`) — a good empirical answer, but an internally generated
one.

**There is now an external one, from an ATLAS thesis, in the OmniFold properties section itself**
(§5.6.3, pp. 170–171), quoted verbatim:

> ***"Flexibility in classifier choice.** Neural networks are used to estimate the likelihood ratios
> in Chapter 6, but in many applications, especially low- and fixed-dimensional measurements, they are
> not required and may even be sub-optimal. Simpler and computationally cheaper methods such as
> boosted decision trees can also be used to estimate likelihood ratios in these cases."*

This is stronger than "GBDTs are permissible": it says NNs *may even be sub-optimal* in exactly the
regime this lane works in. Our own measurement agrees with it — the calibration study found the GBDT
recovered the true binned data/MC ratio to 4.7% median against the MLP's 20.9%, with
`corr(reweight_GBDT, reweight_NN) = 0.92`.

**Read the scope clause, though, because it is load-bearing in both directions.** The endorsement is
explicitly for *"low- and fixed-dimensional measurements."* The scalar-5D unfold is exactly that, so
it lands. It does **not** extend to the full-event PET case, where the same author's measurement uses
transformers throughout. **Do not let this quote migrate into a PET-side justification for GBDTs** —
it would be a scope error, and it is the kind that survives review because the sentence looks
general until you read the qualifier.

---

## 2. Their systematics prescription, and how it differs from the unified throw

Their construction (§6.4, pp. 206–207):

- For each source `u`, perturb the simulation or the data and **re-run the full OmniFold procedure
  from scratch** on the perturbed input.
- The uncertainty in bin `k` is the **signed difference** `Δ_ku = σ̂_ku − σ̂_k`.
- The total is the **quadrature sum over the uncorrelated sources `u`**.
- **12 experimental** and **9 theoretical** sources are propagated this way.

**This is a block sum over sources, with a per-source re-unfold.** It is *not* a unified throw: their
sources are combined in quadrature under an explicit assumption that they are uncorrelated, so
cross-source correlation is not captured by construction. Our `assemble_gbdt5d_adopted.py` docstring
describes the unified throw as capturing precisely what quadrature drops — *"so cross-band
correlations are captured … which also carries their cross-correlations + the retraining
nonlinearity."*

**So this thesis is precedent for the structure, not an argument against the unified throw.** What it
supplies is a clean statement of the field-standard baseline our candidate is trying to improve on,
from a measurement at LHC scale — useful for motivating the unified-throw design in prose, and
useful for knowing what a referee will treat as the default.

**One rule of theirs is worth lifting regardless of which candidate is adopted** (§6.4.2): the
per-member ensemble binning is done **for the nominal only**; every systematic variation uses the
**ensemble-mean weights**. That is where the combinatorics of (sources × seeds × iterations) is cut,
and it is a defensible place to cut it.

---

## 3. Their lateral/vertical split, and a claim about priors worth having on file

§6.4 draws exactly our lateral-vs-vertical distinction, in their own vocabulary:

- **Experimental** uncertainties *"do not shift the particle-level quantities, so they can be thought
  of as uncertainties on the response matrix (or the unbinned equivalent of the response matrix)."*
  Our nine detector-lateral bands.
- **Theoretical** uncertainties *"shift both the particle-level and detector-level distributions …
  This can be thought of as a shift in the particle-level prior provided to the unfolding rather than
  a shift in the response matrix."* Our vertical reweight universes.

Then the claim (same page), which is the citable part:

> *"The prior shifts can be large, for example altering the QCD factorization scales can result in
> shifts of up to 10% … but unfolding is broadly insensitive to choice of prior so the theory
> uncertainties are all sub-leading."*

with their footnote 38: *"The practice of interpreting theory uncertainties as a shift in the
pre-unfolding prior rather than a full uncertainty to be applied to the detector-level distributions
is the reason some unfolded measurements can actually be more accurate than forward folded
measurements."*

**Why this matters here.** It is an independent, LHC-scale statement that the prior-shift family is
expected to be sub-leading *when it is treated as a prior shift*. If our vertical bands are **not**
sub-leading relative to the lateral ones, that is either a real physics difference (a neutrino flux
and interaction-model prior is a far heavier object than a QCD scale variation, and there is a good
argument that it should dominate) or a signal that something is being double-counted. **This brief
does not claim which.** It flags that the comparison is now available and has a clear expected sign,
and that whichever way it comes out is worth a sentence in the note.

Also from their §6.5.1: in their budget, *"the unfolding uncertainties are leading, followed by the
tracking uncertainties and then the remaining uncertainties are generally negligible."* Their
**unfolding** uncertainty — method bias plus hidden variables — is the biggest block. We have no
direct counterpart to their data-driven unfolding uncertainty in the adopted 5D assembly.

---

## 4. Mean-centering: why theirs is unobjectionable and ours is a live question

`AGENTS.md` records that **mean-centering alone is disqualified** for the corrected 5D candidates, and
`values.tex:113-115` carries all three objects: `\gbdtFiveAdoptTrace` (mean-centered),
`\gbdtFiveCVTrace` (CV-centered), and `\gbdtFiveMeanShift` (the joint mean-shift norm, reported
separately).

Greif mean-centers too, and it raises no question there. §6.4 (p. 208): the statistical uncertainty is
*"the variance in the result produced by this ensemble of bootstraps"* — variance about the ensemble
mean. §6.4.2: the central value **is** the event-by-event mean over the seed ensemble.

**The structural difference is the whole point.** When the reported central value is defined as the
mean of the family that supplies the spread, mean-centering and CV-centering are the same operation
and there is nothing to choose between. When the nominal is a separate draw, the two centerings
differ by the nominal-to-mean offset, and that offset is a real quantity someone has to account for
rather than absorb.

**That is a reframing, not a remedy, and it does not discharge anything.** It says the disqualification
of mean-centering here is not a disagreement with field practice — it follows from our nominal not
being the ensemble mean. Two consequences worth weighing, both decisions and neither this lane's to
take alone: either the centering question is settled downstream by defining the central value as the
ensemble mean (which is what `LITERATURE_NOTES.md`'s ensemble-mean audit finding already recommends,
on T2K and Practical Guide grounds, and which this thesis independently supports), or the offset stays
and must keep being reported as its own object — which is what `\gbdtFiveMeanShift` already does.

> **MEASURED AND ANSWERED 2026-09-01 — THIS SECTION IS NOT A ROUTE TO MEAN-CENTERING.** A reader
> could take §4 as opening the option of redefining the 5D central value as an ensemble mean, which
> would make the two centerings coincide as they do for Greif. **They do not coincide here, and the
> governing test is predeclared.** `uq_math.py:119-138` records the F7 rule from
> `CORRECTED_UQ_PRODUCTION_STATUS.md`, set before the data: `||mean_shift||` against the sampling
> floor `sqrt(Tr C)/sqrt(N)`, threshold `F7_FLOOR_MULTIPLE = 2.0`. Measured on the candidate's own
> stamps, **`4.510x` the floor — `f7_cv_centered_required` returns `True`.** So mean-centering alone
> is disqualified for the CANDIDATE too, not only for the July artifact.
>
> **And the analogy itself fails at the ensembles.** Greif centers over a BOOTSTRAP/SEED ensemble, a
> nuisance one legitimately averages over; our shift is against the joint **SYSTEMATIC THROW**
> ensemble (`unified_throw_cov.py:288`: *"Systematic throws all use the SAME estimator seed"*).
> Defining a central value as the mean over systematic throws would fold systematics into the central
> value, which is not what the thesis does. Full measurement, including a 24-member seed-ensemble pull
> that rules out ML stochasticity as the offset's cause:
> [`FINDING-20260901-f7-floor-ratio-and-seed-pull-measured.md`](FINDING-20260901-f7-floor-ratio-and-seed-pull-measured.md).
> §4's reframing stands as a reframing; it is not a remedy, exactly as the section itself says.

**Explicit non-claim:** none of this bears on the `OI-126` **ruling**. Greif's bootstrap treatment is
one paragraph and five mentions in 313 pages, with **no** discussion of a nominal sitting outside its
bootstrap family and **no** centering diagnostic — nothing here addresses that anomaly. **One
qualification, because the flat version is too strong:** the coverage finding (PET brief §8) does
bear on how the coverage condition for any future reconsideration is DESCRIBED — that bar is one this
campaign set above field practice, not a deficiency measured against it.

---

## 5. The validation instrument an adopted covariance would need

Their closure test (§6.5.1) is the most transferable thing in the thesis for an adoption gate. It is a
**binned χ² against the pseudodata truth using the full covariance**, run across **26 observables**,
reported as a p-value each, and it *"allows the method bias and uncertainty model to be **jointly
assessed**."* One statistic tests the central value and the covariance together — which is the shape
of question an adoption gate asks.

Three details that a re-implementation would get wrong by default:

1. **Exclude from Σ any systematic whose nuisance parameters were held at nominal in the pseudodata.**
   They exclude the experimental block for exactly this reason. Including non-varied uncertainties
   inflates Σ and buys a pass the construction did not earn.
2. **Smooth an uncertainty band built from an independent sample before it fills Σ** — theirs is
   Gaussian-kernel smoothed — **but not when the band has real sharp structure.** They exempt the
   jet-mass observables because smoothing distorted a genuinely sharp shape. The exception is
   documented rather than hidden, which is the part to copy.
3. **Judge on the correlated χ², not per bin.** In their `mj1` the method bias exceeds the total
   uncertainty in several bins and the observable still returns p ≈ 0.26.

Their result: 26 of 26 observables above p = 0.05, minimum 0.0556. *(Table 6.3 is at least internally
consistent — five of its p-values recomputed from its own χ² and DoF reproduce to four decimals.)*

**Relation to what we already have.** Our GoF is the binned truncated-spectral χ² on a rank-deficient
covariance, and `LITERATURE_NOTES.md` files binning-independent GoF as an open problem. Greif does not
solve that either — he uses the binned χ² and says a true frequentist check is computationally
infeasible (`coverag` appears **once** in the whole thesis, and it is about detector acceptance;
covering control in the PET brief §8). What
he adds is **breadth**: the same test in 26 projections rather than one, which is a cheap and
meaningful strengthening for a 5D product that must project into many spaces.

---

## 6. Reference points, for calibration only

| quantity | ATLAS FPS (this thesis) |
|---|---|
| dimensions | 6 min / **843 max** / 150 mean per event |
| data events in selection | 247k |
| OmniFold iterations | 7 |
| seed ensemble | **10** (previous round: 100; reduced by pretraining) |
| data-statistics bootstraps | 100 (Poisson λ=1 on event weights) |
| MC-statistics bootstraps | 25 |
| experimental systematics | 12 |
| theoretical systematics | 9 |
| closure observables | 26, all p > 0.05 |
| compute | ~25,000 transformer fine-tunings, ~400,000 A100 GPU-hours |

All as stated in the thesis; none of it is approved ATLAS material.

---

## 7. What this brief does not do

No adoption, no discharge, no gate movement, no covariance change, no compute. §1 is usable in the
note's prose as an external citation once the ATLAS paper or conference note is the citable object.
§3 and §5 name comparisons that can be made against existing artifacts without running anything.
§4 is a reframing of a decision that remains Joseph's.
