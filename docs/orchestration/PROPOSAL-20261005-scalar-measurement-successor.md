# Scalar measurement successor: a bounded 2D admission check

**Recommendation: narrow the proposed publication measurement to the existing
2D muon-kinematic estimator, and stop new measurement production for now.**
The next step is an existing-product audit of whether its central estimate and
uncertainty recipe represent the same estimator. A small development pilot is
priced below, conditional on that audit and on an affordable total-interval
design. Neither condition is established today. This is a concrete **NO-GO for
immediate new compute**, not a claim that scalar OmniFold cannot work.

The scalar-5D measurement remains **NOT ADMITTED**, its governing publication
readiness remains **NOT READY**, and PET remains **NO_ELIGIBLE_DESIGN**, paused.
Successful joint inference, source synchronization, and document builds do not
certify a measurement or its total uncertainties. Narrowing to 2D would leave
the original joint-5D measurement objective unmet; it requires a publication
scope decision and is not a retrospective pass for that objective.

## 1. Decision, authority, ownership, and current evidence

This proposal answers whether existing evidence supports a small next action
toward a useful central value with matched total uncertainty. The authorized
work is existing-evidence analysis, a proposal, commits and pushes on an
isolated branch, and one fresh read-only independent review with at most two
focused review/repair cycles. There is no authorization here for training,
ensembles, new allocations, or scientific adoption. A reviewed no-go is a
terminal deliverable of this proposal task.

The proposal has one owner and one fresh reviewer without the owner's analysis
context. The reviewer examines a fixed commit in a detached, isolated worktree;
only the owner edits. This follows the bounded-artifact approach in the
[campaign review](CAMPAIGN-REVIEW-20260929.md), without claiming a controlled
model advantage. Findings that remain material after two cycles leave the
proposal not executable. The proposal review does not replace any campaign's
required independent numerical verification.

[Evidence snapshot](EVIDENCE-20261005-scalar-measurement-successor.md) records
the remote heads and direct observations. The current baseline is canonical
`main` `1fc9d8ce52842eab849db4408e0d4f5f22c923c0`, observed directly at
19:51 UTC. The initial draft used `c64228da`. The last successful direct
scheduler observation at 14:53 UTC found both CPU campaigns active. Later
committed scalar state records four of five nulls final; neither campaign
has a committed independently verified terminal result in the inspected refs.
The attempted live refresh was unavailable, so those records are not
represented as a new scheduler observation.

| Work | Owner and preserved responsibility | Governing route |
|---|---|---|
| Scalar joint inference | `scalar5d campaign`, local branch `campaign/s5p-precision-20260926`, publishing to `main`; its independent recomputation lane remains responsible for terminal verification | [campaign index](CAMPAIGN-s5p-20260926-index.md), [cold-start handoff](HANDOFF-20260929-s5p-campaign-cold-start.md), [terminal checklist](CHECKLIST-20261001-s5p-terminal-and-claims.md), `OI-193` |
| 2D statistical coverage | Owner of `study/2d-coverage-test-20261005`; its own fresh reviewer and independent numerical recomputation remain required | [pinned preregistration and amendments 1-2](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/ae1f91f37436bc3de7e3d5de33dbb811919ad20f/docs/orchestration/PREREG-20261005-2d-fixed-truth-coverage.md) |
| PET | Final-design owner retains its terminal record; development is paused | [pinned terminal decision](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9a9a7bfb8fe0ce646a9895090a8d7b6c09568866/nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md) |

The scalar CPU pool is 341.434 node-hours, with production 234.647 and a
68.287 verification/repair floor under budget revision 7; the cumulative
ceiling is 376.52 including predecessors. Its GPU pool is 114.904 node-hours,
with a 22.981 verification reserve. These are contract ceilings, not an
observation of remaining credit. The 2D worker has a separate 60 CPU-node-hour
cap. None is funding for this proposal. Jobs, runners, throttles, budgets,
seeds, selections, pinned deployments, STOP files, and frozen decisions stay
with those owners. No operational message or instruction was sent to them.

## 2. Supported claims and remaining obstacles

| Component | Supported claim | What prevents a stronger measurement claim |
|---|---|---|
| 2D central value | Phase-18.2 five-iteration LightGBM result, 205 paper-reported bins, integrated cross section `3.073e-38 cm2/nucleon`; established reproduction and extraction checks | Those checks do not measure total-interval coverage or robustness to an arbitrary truth/response |
| 2D uncertainty construction | Internally matched-CV, flux-fixed 187-universe systematic construction plus statistical and ML blocks; recorded median relative combined standard deviation 6.87% | MAT agreement verifies a covariance recipe. It does not establish coverage, independence of all blocks, or a model-bias bound. Systematic and statistical launchers use different estimator seeds; the coverage study identifies a further normalization question below |
| 2D statistical band | VL162 reproduces the 300-replica rollup: median relative spread 0.5494%, fixed estimator seed, data and signal-MC Poisson streams | The ongoing study tests a transferred statistical band at prior-equals-truth, with same-population MC and closure background limitations. Even a verified PASS would not cover systematics, model dependence, 5D, or total intervals |
| 3D/4D/5D central components | Existing central results, dimensional anchors, and injected-variable closure records support their stated finite tests | Central closure cannot qualify quarantined historical covariances or guarantee response to other departures |
| Adopted scalar-5D trunk | One digest was adopted under a byte-scoped exception; its projection and pairing are identified | Adoption does not change `NON-PASSING` / `adoptable: false`, discharge cause 3, or transfer to candidate R. See the four measurements below |
| R-family scalar development | Refinement-capacity change repairs the measured nominal background bias; tested rounding variability is absorbed by R's refit bootstrap under the paired design | R retains `A_FAIL`; small nominal or repeat spread is not evidence of small departure bias. No candidate-specific total measurement construction was run |
| Joint-5D inference | A frozen, separately calibrated generator-test construction is in production | Terminal evaluation, missing-seed sensitivity, power and independent recomputation belong to its owners. It constructs no new measurement covariance |

Sources: [2D status](../../2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md),
[2D reference](../../2d-unfolding/2D_OMNIFOLD_REFERENCE.md),
[ledger](../../VALIDATION_LEDGER.md) VL146-VL155 and VL162-VL163,
[3D status](../../3d-unfolding/3D_OMNIFOLD_STATUS.md), and
[N-D status](../../nd-unfolding/ND_OMNIFOLD_STATUS.md). Older status prose about
2D coverage is superseded by the current preregistration's fixed-truth
question; the old fluctuating-truth number is not used as coverage evidence.

The [adoption record](DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
attaches four measurements to `3d7465f6...`, with the subsequent
[finite-ensemble correction](CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md):

1. M1: projected uncertainty movement is 6.145% against a 5% bound.
2. M2: movement stayed about 6% over the tested nested N=40, 80, 160 subsets
   at one seed pair, while the same-seed resampling floor fell from 20.91%
   to 7.57% between N=40 and 80. Larger N and seed-pair width are unmeasured.
3. M3: five seed-pinned bands, 6.75% of the trace (26.0% of square-root trace),
   contribute zero movement by construction. Releasing them is unprobed in
   either direction; this is not a lower bound on the total movement.
4. M4: central-value movement on the 43 projection functionals has median
   0.104% and maximum 0.761%, or maximum 6.02% of their own uncertainty.
   Individual 5D-bin movement reaches 49.8% of its own uncertainty.

No adopted uncertainty is borrowed to qualify the proposed 2D construction.

The decisive scalar limitation is empirical, with a restricted scope.
[Amendment 4](state/s5p/contract-amendment-4-stage2-decisions.json) records no
admissible reporting definition at the frozen usefulness targets.
[Amendment 6](state/s5p/contract-amendment-6-review1-repairs.json) preserves that
decision after independent review and corrects two tempting interpretations:

- The prior-shift envelope is **not a per-cell bias bound**. Shifts exceed the
  corresponding bias in only about 52-78% of cells in the checked comparisons;
  membership of the true shape in a generator-vertex hull is unproved.
- Averaging bootstrap widths from six experiments does **not** verify the
  actual interval using each experiment's own width; the initial attribution
  of all calibration failures to the width estimate was overstated.

The historical envelope without D1 has medians 11.25% (J), 4.28% (H2), and
9.90% (EW). J/EW still failed the historical width criterion once the 1.4%
normalization floor was included; W3 failed the historical recovery proxy on
J/H2. These are historical ratios, not a completed flux-repaired prior scan.
The proxy uses different truth and nominal denominators, so its complement
is not an exact recovered fraction. The decision stands under its original
contract; the old amplitudes are not asserted as present generator differences.

The [existing-data synthesis](../../nd-unfolding/gbdt_model_dependence/README.md)
and [delivery](../../nd-unfolding/gbdt_model_dependence/DELIVERY.md) report that
matched repeat variance across settings is missing. For example, historical
W3 J median absolute residual changes from 5.573% at K=5 to 6.573% at K=200,
while at R5 EW29 has a 23.665% mean residual and 0.558% repeat SD over 20
experiments. These are scoped development observations, not a universal
impossibility or a measured bias/variance tradeoff. The new synthesis's
independent-review limitation also remains; this proposal review does not
independently certify all its reductions.

## 3. The one proposed successor and why it addresses a measured failure

**Candidate:** use the published-phase-space 2D five-iteration LightGBM
point-estimator recipe, including the existing purity/fake subtraction,
truth-pass selection, event weights, flux and target normalization, and
fixed estimator seed 1. This seed matches the quoted 300 statistical replicas
and the current coverage worker's estimator. It defines a proposed successor
central value, not an assertion that the historical quoted central value or
the systematic sweep's CV was produced at seed 1. Require its own matching
data central product; do not substitute an exact-GBT result, ensemble mean,
or 5D marginal. No new tuning, iteration selection, classifier family, or
bias correction is proposed. Replacing a quoted central value would require
separate adoption, even if its numerical movement proved small.

**Additional measured matching obstacle:** the full systematic sweep and
its matched-CV launcher both specify `--seed 42`; the statistical scale-up
launcher specifies `--seed 1`. Internally matched systematics are not thereby
matched to the entire proposed seed-1 measurement. Stage A must trace the
actual products to their producer flags and backend, and find compatible
seed-1 systematics or evidence adequate to justify a declared transfer.
If neither exists, same-seed systematic production must be costed in a new
request and Stage A stops with **PAIRING NOT ESTABLISHED**. Completeness
rescaling cannot change an estimator seed. Likewise, a seedscan directory's
label cannot establish its backend: inspect actual producer records.

**Reporting domain:** the 205 cells selected by the paper's reported-bin mask
within `0 <= pT <= 4.5` and `1.5 <= p_parallel <= 60 GeV/c`, plus their
area-weighted integral. Establish equality of this mask with every input's
row map before use; `mean > 0` is a check, not a new mask definition. All
boundary migrations and truth-only misses remain in the unfolding domain.
Unreported cells must be disclosed, not silently assigned zero. The reported
integral is the integral of the reported domain; a full-domain total would
be a separate estimand and would enlarge the validation family.

**Intended use:** a muon-kinematic inclusive cross-section benchmark and
reproduction, with propagatable probabilistic covariance and an explicitly
separate model-dependence allowance. It does not resolve joint hadronic
dependence, supply a new 3D/5D uncertainty, or inherit the joint-test p-values.

**Measured reason to start with pairing:** amendment 1 of the 2D coverage
preregistration identifies bootstrap cross sections of the form
`X_old[r,b] = U[r,b] / c[r,b]`, where `c=P[r,b]/T[b]` fluctuates through the
signal-MC bootstrap but its denominator is held fixed. The unflagged central
path has completeness one. The code confirms the order: bootstrap signal
weights, calculate completeness against `mc_truth_denom`, then divide the
unfolded yield by completeness. The coverage owner added a secondary
replica-form diagnostic; its final attribution remains that owner's work.

The successor first tests the exact algebraic candidate
`X_match[r,b] = X_old[r,b] * c[r,b] / c_CV[b]` from saved histograms. It is
only valid as a repair if event identities prove numerator and denominator
represent the same Phase-18.2 truth population and the intended bootstrap
resamples the complete estimator consistently. An algebraic cancellation
alone does not decide whether MC-normalization conditioning was intended.
If identities, normalization convention, or extraction sufficient statistics
are missing, stop. Do not reconstruct `c` from a mislabeled closure truth
histogram or silently assume the correction is warranted.

The algebra changes the proposed statistical sampling construction at a fixed
seed; it is not a change to the point-estimator algorithm. The old 300
replicas, original covariance and current coverage
verdict remain preserved. Any resulting shadow covariance is unadopted
development evidence, requiring its own review and subsequent authorization
before it could replace a quoted block. A small statistical component does
not excuse incorrect matching.

The [deferred 70-node-hour panel](../../nd-unfolding/gbdt_model_dependence/PROPOSAL.md)
is **not requested**. It would estimate a local R5/R20/capacity bias/variance
relationship on matched scalar functionals. It supplies neither a proven
bias allowance nor a matched total interval, and does not answer this 2D
pairing decision. It becomes necessary only if a future, explicitly selected
5D measurement design requires one of those setting contrasts and states how
its outcome changes admission. Campaign completion alone is not that reason.

## 4. Proposed total-uncertainty construction and its unresolved gate

The candidate recipe is a probabilistic covariance **plus** a signed bounded
model allowance. For cell or integral `f`, report

`I68(f) = [X(f) - sigma_prob(f) - Bminus(f), X(f) + sigma_prob(f) + Bplus(f)]`

and replace `sigma_prob` by `1.96*sigma_prob` for I95. The Gaussian multipliers
are a proposed reporting rule, not an assumption that guarantees coverage.
Validation below tests that rule. A covariance alone cannot encode B.

The ingredients must be matched to the same estimator, domain and source
identities:

| Ingredient | Proposed treatment and admission requirement |
|---|---|
| Data and signal-MC statistics | Replica covariance, sample-centered with `ddof=1`, from the paired estimator after the completeness question is resolved; distinguish MC population conditioning from unconditional finite-MC inference |
| Background and finite template statistics | Include them under the purity/fake algorithm wherever they enter; present replicas do not fluctuate background MC. Verify negligible effect against a declared threshold or construct the missing component; omission cannot be called total |
| Flux, detector, response and interaction nuisance parameters | Reuse the 187-universe flux-fixed MAT construction only after endpoint support, estimator-seed/backend matching or a justified transfer, matching CV, centering, flux-index and physical-source checks. No such seed transfer is established here. The 1.4% target-normalization block enters once. Interaction knobs concern response/efficiency and background, distinct from the truth-shape allowance |
| Estimator and numerical variability | Reassess seedscan pairing and what the statistical resampling already includes. Add a separate component only with an independence or joint-draw argument. R5's rounding-containment result does not transfer to 2D |
| Dependence between probabilistic blocks | State the physical joint nuisance law. Use coherent joint throws or measured cross terms when sources overlap; different RNG seeds do not prove physical independence. The old block sum is a candidate, not a coverage theorem |
| Unfolding-model dependence | On fixed development truths, calculate signed mean residuals; Bminus covers positive estimator bias and Bplus negative bias, using simultaneous upper confidence limits on those magnitudes. Freeze cellwise maxima over that finite development set before validation. Prior variations are sensitivity diagnostics only; never convert them directly to a covariance, probability law or guaranteed bias bound |

The candidate's model domain starts with the Tune-v1 population and corrected
generator-reweighted alternatives at the fixed simulated detector response.
The exact ratios must come from flux-repaired, target-compatible inputs,
with positive weights, adequate support, declared energy range and checked
normalization. No old D1/W1/W3 ratio may substitute. Truth directions and
response nuisances must be varied separately; truth reweighting alone does
not test an altered detector response. Calibration is nuisance-averaged
under an explicit law, not uniform over all nuisance values or all shapes.

Finite validation points can falsify the B construction and test coverage
at those points. They cannot prove that it bounds an entire interpolating
truth hull or the actual unknown data truth. Publication must state the
tested domain and response assumptions. A claim of uniform coverage would
need an additional analytic argument or a costed worst-case search.

**Gate presently missing:** there is no complete, reviewed implementation
and affordable per-experiment repetition of this total recipe. Every
data-dependent width, refinement, nuisance fit and model-selection operation
must recur in validation; a width fitted once to real data and applied to
toys is a different procedure. A surrogate or reusable independent
calibration library could reduce cost, but must first be specified and
checked against the full recipe on development experiments. Its predictive
error must be included in the uncertainty. No such validated shortcut is
claimed here. Without one or a feasible full recomputation budget, the
successor stops before the pilot, with **TOTAL DESIGN NOT ADMITTED**.

## 5. Development, untouched validation, and decision rules

These are **proposed successor requirements**, not amendments to either
worker's frozen criteria. They must be accepted and committed before new
results are seen. No old failed result changes label.

**Development:** all already-read s5c/s5n/s5e/s5p products, the synthesis,
existing 2D products, and the current 2D coverage study are development
evidence for this successor. The current worker's toys keep their original
role for that worker, but cannot become untouched validation of a successor
chosen after seeing them. Audit split keys, event IDs and all seed streams;
new RNG integers alone do not create independent MC populations.

The conditional small pilot has exactly three development truths: Tune v1,
the corrected GENIE+MEC/Tune-v1 full truth ratio, and the corrected
NuWro/Tune-v1 full truth ratio. Freeze their support, event weights and
target convention before launching. At each truth run one expectation
unfold, its event-order control, and six background-inclusive experiments
with paired data/MC/nuisance draws: 24 unfolds in total, one configuration.
The expectation runs target departure bias and numerical reproducibility;
the six repeats test implementation and cost. Neither six nor 24 certifies
coverage, a per-cell bias limit, or a model-dependence bound. They can expose
a large failure and terminate early. A missing input is INCONCLUSIVE, not
permission to replace a truth or drop a cell.

**Untouched validation:** no available ensemble is designated untouched.
Before any release, an independent custodian must freeze four cases:
nominal, two physically motivated truth/response perturbations not used to
fit B or choose the recipe, and one combined truth-and-response perturbation.
Their numerical definitions, amplitudes, fixed-population targets, independent
source/template construction, MC-size equivalence, nuisance law, digests,
and seed manifest are admission artifacts. Authors may know the scientific
definitions but may not inspect their outcomes before the recipe is frozen.
If the available events/response variations cannot support this separation,
record **NO UNTOUCHED VALIDATION DOMAIN** and stop; fresh seeds on a tested
historical truth are not a new physical validation case.

**Accuracy:** use fixed, unfluctuated truth integrals at each validation case.
For all 206 functionals, simultaneous 95% bounds on mean bias must fit inside
`min(0.02*truth, 0.25*median(sigma_prob))`. This is a proposed tolerance for
a 2D benchmark, not the old scalar recovery proxy. Also report the exact
signed recovered change relative to nominal where the injected change is
at least 1% of the nominal truth; require at least 75% recovery of the
change without sign reversal. Do not divide by a near-zero departure.
Statistical uncertainty on accuracy must account for toy-level correlations
and finite reference samples. The accuracy sample-size/assurance calculation
requires development fourth moments and correlations; coverage sizing alone
does not establish its power. Failure to price both is an admission failure.

**Coverage:** require every functional at every validation point to have
simultaneous exact binomial bounds inside [0.60, 0.80] for I68 and
[0.90, 0.99] for I95, familywise 95%. Resample complete experiments for any
secondary pooled summary, never individual bins. There are
`206 * 4 * 2 = 1648` coverage probabilities; two-sided Bonferroni
Clopper-Pearson bounds use tail probability `0.05/(2*1648)`. Cross-bin
independence is unnecessary for Bonferroni; independent experiments at each
fixed case are necessary for the binomial model. Missing or outcome-dependent
failed draws cannot be silently excluded; unresolved selection makes the
result INCONCLUSIVE.

At a fixed N=2400 per case, acceptance hit counts are 1540-1836 for I68
and 2220-2352 for I95. At exactly nominal probabilities 0.682689 and 0.95,
an exact-binomial union-bound calculation gives at least 0.9927 probability
of passing all these coverage requirements, irrespective of within-toy bin
dependence. This is planning under specified true coverages, **not** measured
coverage, and gives no assurance for accuracy, width, or distribution shift.
The [evidence record](EVIDENCE-20261005-scalar-measurement-successor.md) gives
the independently checkable calculation. Use one final look; no extensions,
criterion changes or validation-guided repair. A future early futility rule
would need prospective error accounting before release, not invention mid-run.

**Width/usefulness:** at each validation case and for the final data result,
require median relative I68 half-width <=10% and its 90th percentile <=25%
over the 205 cells, plus <=10% for the reported-domain integral. Here
half-width means `(upper-lower)/2`, so B counts. Require median relative
model allowance `(Bminus+Bplus)/2` <=5%; report maxima, low-acceptance
regions and every cell, not just medians. The 10% target is motivated by
the existing roughly 6.87% constructed 2D budget leaving limited room for
missing sources; it is not a new sensitivity or generator-separation claim.
If these bounds are too weak for the intended physics use, narrow the
scientific claim rather than declaring model discrimination.

**Terminal states:** PASS requires matching, all-source accounting, accuracy,
coverage, usefulness, independently reproduced results, and preservation.
FAIL records a violated frozen criterion. INCONCLUSIVE records inadequate
precision, missing inputs, failed equivalence, insufficient independent
samples, or exhausted resources. All terminate the bounded stage. A
development pilot pass only permits a new admission decision; validation
failure consumes those validation samples. No outcome adopts a product or
restarts either current worker's campaign automatically.

## 6. Smallest staged resource request

| Stage | Concrete work and ceiling | Release / stop |
|---|---|---|
| A: existing-product admission | **0 new cluster node-hours, 0 GPUs, 0 training.** At most 2 local CPU-hours, 8 GiB RAM and 2 GiB derivative storage for inventory, matching algebra, covariance/row-map checks and design costing; reserve 0.5 CPU-hour for independent numerical checks. Raw event inputs stay at their original routes | Use stable copies; final worker records are required before acting on their result. Stop on missing completeness operands, inconsistent event identity or no affordable total recipe. No change to a quoted covariance |
| B: conditional development pilot | **8 billed CPU node-hours total, zero GPUs, at most one CPU node, 10 GiB new products.** Of this, <=6 node-hours for the 24-run pilot and >=2 node-hours held for verification/diagnosed repair | A passes, both campaigns finish their required terminal verification, separate authorization, frozen executable design, and available resources remeasured. The present recommendation does not release B |
| C: total construction and untouched validation | **No allocation requested or admitted.** The N=2400, four-case design alone entails 9600 complete experimental procedures | Require a costed implementation of the entire recipe, adequate accuracy power and complete funding with >=20% verification reserve before releasing any untouched sample. If unaffordable, stop or seek a newly scoped publication decision |

Measured timing basis for B is the 2D owner's committed pilot accounting:
660, 750 and 730 seconds on one billed node, mean 713.333 s or 0.19815
node-hours per toy. Thus 24 runs cost 4.756 node-hours at that mean;
an explicit 25% planning allowance gives 5.944, leaving the 2-node-hour
reserve inside an 8-node-hour ceiling. This is an extrapolation from
nominal statistical toys to background/nuisance/departure workloads;
the allowance is not a measurement of those new workloads. Scalar R timing
(about 294 s at 32 threads) and eight-way packing are not used to price 2D.
The worker's later operational amendment measured one shared-lane toy at
1091 s with billing 64/256 (about 0.076 node-hours), but changed its thread
count from 128 to 64 and did not establish bitwise equivalence. This proposal
retains the measured 128-thread baseline and does not import that saving
into a different workload without an equivalence and throughput check.

Bill elapsed time using the actual scheduler billing fraction and QOS factor,
and admit only if spent plus all open worst-case reservations plus protected
reserve stays within 8. Run sequentially, regular/shared/debug only, no
premium or overrun. A one-hour task limit does not promise 24 completions:
if the remaining 6-node-hour work envelope cannot finish the manifest, stop
INCONCLUSIVE. One diagnosed infrastructure retry, identical seeds, may use
the repair reserve; a scientific failure never triggers a retry. Review
compute has first claim on the 2-node-hour reserve. No automatic cap increase,
sample thinning, packing change, or transfer from either worker's budget.

For C, merely **one unfold per experiment** at the measured nominal rate
would cost 1902.2 node-hours, or 2972.2 with the same 25% allowance and a
20%-of-total reserve. This omits uncertainty construction, all new input
preparation, calibration, source handling, and verification of a surrogate.
It is a workload illustration, not a rigorous lower bound on every future
implementation or a funding request. Repeating the existing 300 statistical,
187 systematic and 10 seed members plus a central unfold naively would
multiply the unfold count by 498; identical timing would imply about
1.48 million node-hours including those margins. Members have different
costs and some inputs are reusable, so this is explicitly an extrapolation,
not a measured quote. It explains why an affordable total recipe is a gate,
and why the 8-node-hour pilot cannot be sold as a path already funded to
publication.

## 7. Disposition

Proceed with the reviewed existing-evidence proposal and the bounded matching
admission work when its inputs are stable. Recommend a **2D-only candidate
publication scope**, contingent on resolving the matching and all-source
validation gaps. Request **zero new cluster compute now**; retain the
conditional 8-node-hour pilot as the first separately decidable increment.
Without an affordable complete total-interval recipe, stop at the admission
gate with a defensible no-go rather than purchase more bias/variance points.

Current deliverables can support the established 2D reproduction and scoped
method-development findings, and eventually the owners' independently
verified joint-test and statistical-coverage results. They do not yet support
claiming this proposed matched total-uncertainty measurement complete.
Neither the 5D exception nor PET's terminal outcome is changed. Manuscript
scope changes, adoption, and standalone-note synchronization are later acts;
this proposal edits no analysis-note sources and declares no publication ready.
