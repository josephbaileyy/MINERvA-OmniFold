# DRAFT — statistical-covariance limitation statement for the analysis note (Track B)

> **STATUS: DRAFT FOR REVIEW. NOT IN THE NOTE AND NOT TO BE COPIED INTO IT FROM HERE.** Authorized by
> Joseph (*"Yes I authorize both"*, recorded at `ae70c3f`) as Track B of two; the mediator reviews this
> text and Joseph sights it before any of it goes near `docs/analysis-note/`. Track A — the clean
> `Exponential(1)` vs `Poisson(1)` contrast — is the `Assisstant` lane's and **its outcome is not
> anticipated anywhere below.**
>
> **Every figure here was re-derived from committed artifacts at `7ceb18c`, not recalled.** Provenance is
> in §7. **Exactly two facts in this document are STALE-ABLE BY CONSTRUCTION and are marked
> `⟨RE-DERIVE⟩` at the point of use — the Track A submission status in §5 and the provenance commit hash in
> §7.** They must be recomputed at the moment the note is built, not copied (`BEN-228`). *(The marker also
> appears in this header and in drafting note 3, which are references to those two rather than further
> instances.)*

---

## 1. What the statistical covariance is, and the method choice it rests on

The statistical covariance `C_stat` for this measurement is built from a **50-member replica family**. Each
member repeats the full analysis — background-subtracted target construction, estimator training, and
cross-section extraction — on a **`Poisson(1)` bootstrap of the measured leg**: every measured event
(data and background-subtraction rows alike) is reweighted by an independent `Poisson(1)` draw, so a
member's target is the nominal target multiplied by that draw. The covariance is the sample covariance of
the 50 resulting cross-sections about their own mean, normalised `1/(N-1)`, on the density (not
width-weighted) scale.

**This is a method choice and we state it as one.** A `Poisson(1)` bootstrap of the measured sample is a
standard proxy for measured-statistics uncertainty, but it is a proxy: it is not the same object as an
analytic propagation of counting errors, and for a **non-linear, learned** estimator it is not guaranteed
to inherit the properties it has for a linear one. Nothing in this analysis has established that it does.
That reservation is the subject of §4 and it is not rhetorical — it has a measured consequence.

We verified that the replica targets are what this construction says they are: the multiplicity
distribution reproduces the `Poisson(1)` probability mass function for `k = 0…5` to better than 0.5%, the
zero-weight fraction is `e^-1` to `2.4 × 10⁻⁴` pooled and lies within `1.9 σ` of `e^-1` in **every one of
the 18 populated longitudinal-momentum columns**, and the members' Stay-Positive refinement agrees with the
nominal's to **0.068%** on the rows both retain. **The construction is doing what it claims.** The question
in §4 is whether what it claims is the right thing to do.

## 2. The measured spread, reported family-typical rather than best-draw

Across most of the reported plane the replica family is tight and the central value sits comfortably inside
it. In the region `6 < p_∥ < 20 GeV/c` it is neither.

| quantity | value |
|---|---|
| median per-cell replica relative standard deviation, `6 < p_∥ < 20 GeV/c` | **`67.1%`** |
| median per-cell replica relative standard deviation, elsewhere | **`8.5%`** |
| nominal-to-member ratio of unfolded yield in that band, **family mean over 50 members** | **`3.5969`** |
| standard deviation of that ratio across the 50 members (`ddof = 1`) | **`1.6091`** |
| range across the 50 members | **`1.0859` – `6.8865`** |
| median per-cell nominal-to-family-mean ratio over the whole reported plane | **`1.000323`** |

**The last row is the context for the others and must not be dropped when they are quoted.** Over the
reported plane as a whole the central value and the replica mean agree to `0.03%` per cell; the disagreement
is concentrated, not global. The affected band carries **`15.5%`** of the reported cross-section integral.

**A note on how these numbers must be quoted.** An earlier internal statement of the band ratio used a
single member's value, `5.0467`. That member is at the **70th percentile** of the 50 (`z = +0.90`) and is
**not typical**; the family-typical value is `3.5969` with the spread given above. **The single-draw figure
must not reappear as a headline.** We record the correction here because the distinction between a draw and
a family is exactly the distinction this section exists to make.

## 3. What is established

**The discrepancy is localised to the estimator's training, and the extraction is faithful.** Comparing the
per-cell unfolded yield before extraction (the pushed weights binned in truth) against the extracted
cross-section, for the nominal and for a member:

- in the control region `p_∥ < 6 GeV/c`, the two ratios agree to a median **`0.139%`**;
- in the affected band, the ratio of ratios is **`1.0000`**;
- the deficit is separable in longitudinal momentum alone, and this holds **separately for two different
  quantities** — the figures below are **four distinct fits, not one pair repeated**:

  | quantity fitted | variance explained by `p_∥` alone | by `p_T` alone |
  |---|---|---|
  | the **extracted** cross-section ratio | `R² = 0.868` | `R² = 0.018` |
  | the **pushed** (pre-extraction) yield ratio | `R² = 0.839` | `R² = 0.030` |

  The two rows are close *because* the extraction is faithful — that is the point of §3, not a duplication.
  **Whoever transfers this into the note must keep both rows and their labels**; collapsed to a single pair
  it reads as a transcription error, and dropped to one row it loses the only evidence that the separability
  is a property of the training rather than of the extraction.

So the extraction machinery introduces essentially none of the effect and carries it faithfully. Two
candidate mechanisms are **retired by measurement, not by argument**: the replica targets themselves (§1),
and the Gate-5 signal factor applied to truth counts, which the extraction comparison excludes.

**The affected cells are not sparse or peripheral.** They form a single contiguous band spanning nearly the
full transverse-momentum range, with **median reconstruction acceptance `0.859`** — the highest on the grid
— carrying **`26.5%`** of all reconstructed-and-accepted signal. **None** of them falls below the
low-acceptance threshold that defines this analysis's model-dependent reporting tier. Whatever the
explanation is, it is not that the measurement is starved there.

**And an external comparison is available.** MINERvA's own published double-differential inclusive
measurement reports **all 84 bins** of this longitudinal-momentum range at a **median fractional
statistical uncertainty of `1.55%`** (its worst reported bin anywhere is `13.1%`). Our replica family gives
`67.1%` in the same bins. *The two are not the same object — that is data-statistics on a
standard-selection sample against a bootstrap over a learned estimator on an extended phase space — and we
do not treat the comparison as decisive. We state it because a reader is entitled to it.*

## 4. What is not established: two branches, and we do not choose between them

The replica family disagrees with the central value by a factor of order three, coherently, in the
best-accepted region of the plane. **There are two readings and this analysis does not currently
distinguish them.**

**Branch (a) — the spread is real.** The estimator is genuinely this sensitive to the measured sample in
this region: with a learned, iterative reweighting, a region whose constraint comes from a steeply falling
part of the flux may be legitimately unstable, and a bootstrap is correctly reporting it. **Under (a) the
covariance is right and the quoted uncertainties in `6 < p_∥ < 20 GeV/c` really are of order `67%`
per cell.** They should be published at that size and interpreted as a statement about how much this
estimator can be constrained there.

**Branch (b) — the proxy is wrong.** `Poisson(1)` resampling gives `36.8%` of measured rows zero weight,
and a learned estimator confronted with that much removed support may respond in a way that is a property
of the *perturbation*, not of the measurement. **Under (b) the covariance overstates the statistical
uncertainty in that band and the construction needs replacing**, which would reopen the choice of
resampling scheme rather than merely rescaling the result.

**We have no measurement that separates these, and neither is favoured here.** The evidence in §3 is
equally consistent with both: a genuinely unstable estimator and an invalid perturbation both act during
training, both produce a coherent effect concentrated where information is scarcest, and both leave the
extraction faithful. Arguments that appear to favour one — including the external comparison in §3 — do not
survive the observation that the two branches predict the same sign and the same shape.

## 5. A discriminating experiment exists and is authorized

The two branches differ in exactly one respect that can be isolated. `Exponential(1)` and `Poisson(1)`
have the same mean and the same variance and differ only in `P(X = 0)`, which is `0` and `e^-1`
respectively. Rebuilding members with `Exponential(1)` measured-leg weights therefore holds the variance of
the perturbation fixed while removing its zero-support, and the band ratio has **opposite predictions**
under the two branches: it remains near the family-typical value under (a) and collapses toward unity under
(b).

That experiment is authorized. Its design, decision boundary and sample size are predeclared before it
runs, with an explicit `UNRESOLVED` outcome that does not default to either branch.

> **⟨RE-DERIVE⟩ Status at the time the note is built.** As of `2026-08-15T16:59:18Z`, verified by
> `squeue`, the contrast **has not been submitted** — its predeclaration is pending. **Do not copy this
> sentence forward.** Whether the experiment is pending, running or complete is machine-derivable and must
> be re-derived when the note is built; a stale claim that an experiment "is running" is worse than no
> claim (`BEN-228`).

**This section exists so that a reader knows the question is open and being measured, not abandoned.** It is
not a promise about the outcome, and §4's two branches remain live regardless of what the contrast returns.

## 5A. AMENDMENT, 2026-08-15 — the contrast will not run, and the `67%` is characterized rather than adjudicated

> **This section supersedes part of §4 and most of §5. Those sections are left exactly as written.** They
> record what was believed and what was open at the moment they were reviewed and approved, and per this
> document's own standing instruction an update of this kind must be **visible as a change against a version
> already read**, never an in-place edit. **§4's fork was genuinely open when §4 was written.** What follows
> is why it is now narrower.

**The discriminating contrast was authorized and will not be run.** Four lanes independently recommended
against it, unanimously, and that recommendation was accepted. The reason is publishable and is the honest
one: **neither outcome would have changed what we publish.** If the contrast had shown the zero-support atom
to be unimportant, we publish the covariance as it stands. If it had shown the atom to be decisive, the
remedy would have required replacing the resampling scheme with a zero-free one — **which is choosing the
noise model that yields the smaller uncertainty**, and that is not a defensible basis for tightening an
error bar. The question was examined and closed on argument; it was not abandoned for cost.

**And the argument that closed it narrows §4's second branch.** §4 offered branch **(b)**: that a
`Poisson(1)` bootstrap is an invalid proxy for measured-statistics uncertainty, so the band entries
*overstate*. On examination that branch is **substantially weakened on physical grounds**:

- The resampled objects are **individual reconstructed events** — 4,680,719 rows. A `Poisson(1)` multiplicity
  on a row states that, were the data retaken, that event occurred `k` times; **multiplicity zero states that
  it did not occur, which is precisely what counting noise does to an event observed once.** The zero atom
  is not an artifact of the method.
- Independent `Poisson(1)` row multiplicities **reproduce exact Poisson fluctuations in every aggregate of
  those rows** — any bin content, any weighted sum. That is the property for which the scheme is used, and it
  is not shared by variance-matched continuous alternatives, which match the first two moments of those
  aggregates and get the discreteness wrong.

**So the resampling scheme is the sampling distribution, not a stand-in that might be the wrong one**, and
"the proxy is invalid" is not available as a reading of the band.

### What the band figure therefore is

**The `67%` is the spread of a *refit* estimator under *correct* measured-statistics resampling.** Two
consequences, and both belong beside the number wherever it is quoted:

1. **It is the sampling uncertainty of *this estimator*** — a learned, iterative reweighting refit on every
   replica — and not a property of the data alone. It includes the estimator's own sensitivity to which
   events are present.
2. **It is therefore an *upper bound* on how poorly the data constrain the cross-section in that region.** A
   differently regularised estimator could do better on the same data; none could do worse purely for want of
   information. *(Upper bound on the **statistical** component only; it says nothing about systematics.)*

**This is more useful to a reader than either of §4's branches**, because it says what the number *is*
rather than ruling on whether it is "right", and it is defensible whichever way the underlying question
eventually settles.

### The status of this amendment, stated precisely

**This is an argument, not a ratified result.** It has survived four independent lanes including the one
that proposed the instrument it retired, which is the strongest support an argument of this kind has had on
this analysis — **and that is still not a measurement.** Ratification belongs to the PET lane and to the
covariance-construction reviewer, and **`OI-126` remains open.** Nothing here licenses promoting the central
value, quoting the covariance as verified, or treating the region as settled.

### One bookkeeping consequence

**§5's `⟨RE-DERIVE⟩` mark is now DISCHARGED, not outstanding.** It instructed a future editor to re-derive
whether the contrast was pending, running or complete; **the answer is settled and will not change — it will
not run.** Do not re-check `squeue` for it. **The provenance commit hash in §7 is therefore the only live
`⟨RE-DERIVE⟩` in this document**, which supersedes the count given in the header.

## 6. Limitations of the covariance object itself, independent of §4

These hold whichever branch of §4 is correct, and a limitation statement that omitted them would be
incomplete.

**The covariance was built by one implementation, and is therefore not independently verified.** The
construction scope originally called for two blind builders; **the dual-build design was dropped by
Joseph on 2026-08-14 — a recorded decision, not an omission or an unmet requirement.** One builder was
produced accordingly. Its 19 specification clauses are abort-on-failure assertions **inside that same
builder**, which makes them a self-check rather than an independent verification, and the regression
against the in-tree recipe has power over arithmetic and ordering only — not over the choice of domain or
centring. **So no claim of independent construction or independent verification is made for this object,
and none should be inferred from the clause count.** *(Stated this way deliberately: a reader who sees
"not independently verified" without the decision behind it reads an outstanding action item and asks for
the second build.)*

**Every estimated standard deviation carries a `10.1%` fractional uncertainty of its own**, from the family
size alone: `N = 50` gives `1/√(2(N−1)) = 1/√98`. The retired design document that specified `N = 100`
labelled a family of this size insufficient, and that label stands in the record as committed.

**The reporting domain and the invertible domain are different, and quoting one for the other is an error.**
The measurement is reported on **262 cells** (those with non-zero reconstruction acceptance). The covariance
is provided on the same 262-cell domain, but its **invertible sub-block is 257 cells**: five cells are
excluded because they enter the reported set in some members and not others, so their apparent variance is
partly the reporting mask switching rather than the cross-section moving. One of the five, cell `255`, is
reported in only **24 of the 50** members. The excluded cells are `[209, 254, 255, 256, 281]`; they are
published and flagged, and they are not used in any inversion or goodness-of-fit. **The rank of the
covariance is `49 = N − 1`**, far below `262`, so any use requiring an inverse requires a declared
regularisation that this analysis does not silently supply.

**The covariance is on the density scale** (`width_weighting_applied = false`) and is centred on the
**replica mean**, not on the published central value. Both matter to a user: integrating it requires bin
areas, and the centring choice means it does not by itself express the offset described in §2.

## 7. How to disagree with us

Every number above is derived from committed artifacts, and the per-cell arrays behind the aggregates are
published with them, so a reader can recompute the aggregates and reach a different conclusion.

| claim in this section | artifact |
|---|---|
| **the two per-cell replica relative standard deviations of §2 — `67.1%` in band and `8.5%` elsewhere** | `state/p5a-nominal-vs-cstat-family-percell-20260815.json`, fields `the_tail.median_family_rel_sd_in_tail` and `…_elsewhere`. **Both are recomputable from that receipt's own shipped `per_cell_family_rel_sd` array (257 values), whose cell-by-cell binding was independently proven against `sqrt(diag C)/mean` to `5.5e-16`.** ⚠ **That receipt carries two RETRACTED fields** — `the_tail.their_share_of_total` and `the_tail.top20_share_of_total`, both marked in place with the reason. **Neither of the two relative-sd fields used here is among them**, and no share-of-total figure from that receipt is used anywhere in this section. |
| family spread, per-replica values for all 50 | `state/probe-oi126-band-Rpush-sigma-20260815.{py,json}` |
| training-vs-extraction split, control and band | `state/probe-oi126-push-vs-extraction-20260815.{py,json}`, `state/RECEIPT-…-push-vs-extraction-RESULT.json` |
| predeclared thresholds, fixed before that run | `PREDECLARATION-20260815-oi126-push-vs-extraction.md` (`449ec52`) |
| target is a `Poisson(1)` draw; refinements agree to 0.068% | `state/RECEIPT-20260815-oi126-mechanism-narrowing.json` |
| zero fraction is `e^-1` per column | `state/probe-oi126-zero-fraction-per-column-20260815.{py,json}` |
| band geometry, acceptance, share of integral, external comparison | `state/RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json` |
| decision-boundary feasibility and the sample size it implies | `state/RECEIPT-20260815-oi126-boundary-feasibility.json` |
| covariance object, domain, rank, centring, one-builder record | `GATE5_CSTAT_N50.npz`, its receipt, and the `VL132` ledger row |
| **the input file the 50 members were built from** | `state/gate5-source-npz-verified-20260813.json`, which carries an out-of-band **measurement** of the source identity. ⚠ **Do not cite the members' own `inputs_sha256` for this.** That field is a *copied claim* rather than a measurement on the replica path, and no downstream validator re-checks it — the Gate-4 independent hash fails closed on any `bootstrap_seed != -1` and so never sees a replica (`OI-58`). Gate 5's execution is unaffected; **the source file is genuinely correct.** This row is what makes the family's source identity a recoverable measured operand rather than a restatement. |

**⟨RE-DERIVE⟩** the commit hash quoted for provenance when the note is built.

---

## Drafting notes for the reviewer — NOT part of the statement

1. **Both branches are written to the same depth and with the same specificity, deliberately.** Each gets a
   mechanism, a consequence for the published numbers, and a named implication for what would have to
   change. If Track A returns (b), §4's branch (b) needs no rewriting, and §3's external comparison is
   already fenced with the reason it is not decisive.
2. **The single-draw band figure appears exactly once in the statement body — §2, as the figure being
   corrected — and never as a headline.** *(It appears a second time in this drafting note, which is not
   part of the statement; a `grep` of the whole file therefore returns two hits, and that is the reason.
   Stated because "appears exactly once" is a checkable claim and it must survive being checked.)*
3. **§5 does not say the experiment is running**, because at the time of writing it is not — verified by
   `squeue` at `16:59:18Z` rather than relayed. The status is marked `⟨RE-DERIVE⟩` instead of asserted, so
   the note cannot inherit a false present tense.
4. **Nothing here closes `OI-126`.** The statement declares the fork; it does not resolve it, and §4 says
   so in terms.
5. **Two things I flag as the reviewer's call, not mine.** (i) Whether §3's MINERvA comparison belongs in
   the note at all — it is the most rhetorically forceful number available and also the least like-for-like,
   and I have fenced it rather than dropped it; a reviewer may reasonably want it cut. (ii) Whether §6's
   one-builder paragraph belongs in this section or in a construction section — it is a provenance
   limitation rather than a statistical one, and it is here because the dispatch required it.
6. **Numbers I did not put in and could:** the 44-of-63 cells where the central value exceeds every member,
   and the `+3.81` median per-cell z-score. They are the sharpest statement of the anomaly, and I left them
   out because per-cell z-scores against a 50-member family invite over-reading. Available if wanted.
   **Reviewed and the omission was upheld**; §7 routes a reader to them with full context.

## Review disposition, 2026-08-15 — recorded so the next editor inherits the rulings, not just the text

Reviewed by the mediator; **approved for Joseph's sight subject to the `8.5%` provenance row, which is now
added.** Three asks were ruled on and the rulings are recorded here because each one is a decision a later
editor could silently reverse:

- **The MINERvA comparison STAYS, unchanged.** A referee will find `1.55%` against `67.1%` independently,
  and finding it unaddressed is worse than finding it stated; §4 already neutralises it **by name**. **Do
  not quietly drop it** — omitting it is the choice that would need defending.
- **§6's one-builder paragraph STAYS WHERE IT IS**, and may additionally appear in a construction section.
  It must appear **at the point of use**: a reader deciding whether to trust this covariance needs to know
  it was built once and self-checked *at the moment they are deciding*. **Misplaced and read beats correctly
  placed and missed.**
- **The sharp per-cell numbers STAY OUT** (see note 6).

**AND A STANDING INSTRUCTION ON HOW THIS TEXT MAY BE UPDATED.** When Track A's contrast returns, **do not
fold its outcome into this document by editing it in place.** The update must be visible as a change against
a version that has already been read and approved — a silent improvement to reviewed text destroys the only
record that the fork was genuinely open when it was written, which is the whole evidential value of §4.

**That instruction was then applied to its own author.** The contrast was declined rather than returning a
result, and the consequence is §5A: **an added, dated, superseding section, with §4 and §5 left untouched.**
Written that way deliberately, and it is the one structural feature of this document a later editor is most
likely to "tidy" away.

## Do not resurrect this argument — it was refuted, 2026-08-15

In arguing against running the contrast, this lane offered the following and **it is wrong**: that
`Poisson(1)` and `Exponential(1)` have identical effective sample size (`ESS = (Σw)²/Σw² = N/2` for both,
which is arithmetically exact), and that the two arms therefore carry refit sensitivity equally, so a
null result would not have been diagnostic.

**The `Assisstant` lane refuted the inference while conceding the vote.** `ESS` is a scalar summary of the
weight *distribution* and says nothing about **support**: a thin neighbourhood is emptied entirely by
`Poisson` with probability `e^{-n}` — `0.368` at one row, `4.5e-5` at ten — and by `Exponential` with
probability exactly `0` for every `n`. **Dropping an event and downweighting it are different operations for
a weighted loss**, so matched `ESS` does not imply matched refit sensitivity.

**The conclusion (do not run) stands on the other grounds in §5A; this argument is not one of them.** It is
recorded here so that it cannot be picked up from the discussion history and cited as a reason, and **it must
not appear anywhere in the note.**
