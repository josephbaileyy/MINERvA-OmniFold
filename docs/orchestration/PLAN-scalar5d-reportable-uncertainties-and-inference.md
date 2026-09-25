# Scalar-5D reportable uncertainties and calibrated generator inference

## Status and activation

**PROPOSED standing authorization, not an executed scientific decision.** This document answers
the request to prepare a complete, preapprovable plan. Writing it does not launch compute,
adopt an unknown product, amend an existing decision, or authorize publication.

To activate the whole plan, the project owner may state:

> I approve this plan, including its scope-specific supersession of previous holds, resource
> envelope, delegated scientific choices, conditional adoption rules, independent review,
> and commits, merges and pushes to both repositories. Execute through a final disposition
> without further routine approval. Journal/arXiv submission and external data publication
> remain separate decisions.

Record that actual approval, its date and this plan's Git blob identity in an executed decision
record before implementation. Do not describe the proposed approval above as something already said.
Commit the approved plan and retain that version unchanged; record its commit as well as its blob
identity. Put subsequent delegated choices in the campaign contract and state. A substantive
amendment outside the delegation needs its own actual authorization; do not silently alter the
approved version.
Subsequent executor choices must be recorded as executor choices, not quotations from the owner.
This plan concerns scalar GBDT unfolding; PET remains diagnostic and outside the campaign.

The scientific objective is a useful measurement with defensible uncertainties and a calibrated
joint-5D comparison with specified generators at a declared resolution. The `(E_avail,W)` plane
remains a reporting product and an inference fallback. A small p-value is not a success criterion;
a calibrated comparison that does not reject a generator is also a successful inference result,
with its power stated. Neither outcome guarantees sensitivity to every possible departure.

Track campaign disposition, reportable uncertainty scope, joint-5D inference and publication
readiness separately. Completing a bounded campaign does not establish the other three. The
paper-wide completion table in section 10 determines whether all retained publication claims
are ready; a projection-only result does not fulfill the joint-5D objective.

Deliver the measurement in a separately verifiable checkpoint: estimator, matched central values,
uncertainty construction, actual interval coverage and exact reporting scope. Cost joint inference
early, but protect the resources needed to complete that checkpoint. An unaffordable inference
method must not prevent an affordable, qualifying measurement from being completed and delivered.
Continue to joint inference when its feasibility and scientific gates permit; the checkpoint alone
does not complete the joint-5D objective or establish publication readiness.

## 1. Starting evidence and cold-start procedure

Read these exact routes; do not load the orchestration directory wholesale:

1. Root `AGENTS.md`, `docs/CURRENT_WORK.md`, the corresponding `docs/OPEN_ITEMS.md` records,
   and `docs/orchestration/PLAYBOOK.md`.
2. `VALIDATION_LEDGER.md` VL142–VL145 and their original product receipts.
3. `docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`, especially
   its four measurements; `CORRECTION-20260920-lower-bound-inference-withdrawn.md` and
   `CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md` in the same directory.
4. `docs/orchestration/DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md`,
   `SPEC-20260906-complete-scalar5d-successor-Z.md`, and `OPERATIVE-SHEET-scalar5d.md`.
5. `docs/orchestration/OUTCOME-20260922-L2-sproj-measured-and-the-pair-is-not-code-comparable.md`
   and the current review-residue report. Check for later committed dispositions before acting.
6. `KNOWN_ISSUES.md`, `nd-unfolding/ND_OMNIFOLD_STATUS.md`,
   `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`, and
   `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` for environment and workstream contracts.
7. `docs/analysis-note/README.md`, `app_release.tex`, the release-package README, and
   `docs/POST_PUBLICATION_REORG_PLAN.md`.

Existing adopted identities, to re-hash at use:

| Object | SHA-256 | Existing status |
|---|---|---|
| Scalar-5D `z-cv.npz` | `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5` | Adopted under byte-specific exception; metadata remains NON-PASSING / adoptable:false |
| Publication `(E_avail,W)` projection | `835828bf3e25bbd9f279088e5cc89b8b325d727446fec9fabbbc92fd7e71a54e` | Derived from that source; 42 destination cells; inherits its limitations |

The old 6.145% versus 5% seed-stability result remains a failure. Its nested-subset study at one
seed pair does not establish behavior at arbitrary ensemble size. The five formerly seed-pinned
bands were unprobed in either direction by that study. Seed changes also moved central values,
so covariance-only comparisons are insufficient. All four adoption measurements continue to
travel with products derived from those bytes.

Refresh repository heads, worktrees and staged changes. On canonical cluster main run the routed
live-state freshness check and independently query the scheduler. Record actual allocation,
storage and active-job commitments. A view, handoff or historic job ID is not current evidence.
Do not overwrite another lane's changes or infer ownership from the shared account.

If a preservation/simplification pass has completed, read its committed handoff and recovery
manifest, verify both draft documents against their recorded Git blobs, recheck current state,
and reuse its verified preparation. Compare the attached versions with those identities before
recording approval. An unexplained mismatch blocks activation of the disputed version, not
independent read-only preparation; do not silently approve whichever file is newest.
Do not repeat its archive or restart a general cleanup campaign. If no such pass has completed,
perform this plan's bounded Phase A; the absence of an optional handoff is not itself a scientific
gate. A missing input or recovery requirement blocks dependent work only; complete independent
authorized work and report the exact dependency.

## 2. Standing delegation after activation

The executor may perform the following without returning for routine permission:

| Area | Delegated scope |
|---|---|
| Cleanup | Local build/import fixes, input/output separation, targeted refactoring, documentation and test repairs needed by this campaign |
| Scientific design | Choose and freeze reporting partitions, masks, estimator candidates, seed policy, regularization, null model, nuisance treatment and calibration procedure under sections 5–8 |
| Estimator changes | Deterministic settings, thread policy, fresh seed ensembles, seed averaging and complete lateral seed propagation in new isolated candidates |
| Uncertainty work | Construct new scalar statistical, training-seed and systematic components; diagnose overlap; implement a justified new uncertainty model without double counting |
| Compute | Submit, monitor, resume, cancel and retry this campaign's own jobs inside section 3; no individual job approvals |
| Verification | Commission independent agents/reviewers in isolated read-only worktrees; repair findings and obtain required receipt reissues through legitimate verifier paths |
| Delivery | Branch, commit, push, resolve routine conflicts, open draft PRs, and merge passing in-scope work in the canonical and standalone note repositories |
| Scientific disposition | Apply section 9's conditional adoption to newly produced, independently verified results; record exact product digests and scopes |

Activation explicitly supersedes, **for this new campaign only**, the earlier exclusion of
generator significance from the completion path, holds on additional scalar seed/member studies,
reservation of the named estimator changes, and the requirement for another human adoption act
for a candidate satisfying section 9. It authorizes fresh paired rebuilds when code comparability
requires both members. It does not rewrite old decisions or reopen PET, OI-126, or Gate 6.
Before implementation, record a scoped mapping from each displaced record/clause to the newly
authorized action. Preserve the old records; this mapping cannot expand the delegation above.

The frozen Z specification remains frozen. Define any successor contract separately; a result
passing that contract is not a retroactive PASS under Z. Historical exceptions never transfer to
new bytes. Do not recover an accepted historical provenance gap by inventing provenance.

No external messages, purchases, credential changes, journal/arXiv submissions or public data
deposits are included. Commits and pushes to the two existing project repositories are explicitly
included. An unavailable collaborator response must not become an indefinite dependency: use
the documented scope, restrict claims when necessary, and report concrete missing evidence.

## 3. Compute envelope and resource accounting

These are proposed operating limits, not cost estimates or claims that the allocation is sufficient.
At activation establish each budget as the smaller of the absolute ceiling below and **10% of
the measured uncommitted remaining allocation** for its resource pool. Deduct queued/running
reservations first. Never infer CPU capacity from GPU capacity or convert node-hours to core-hours
without recording the scheduler's billing rule.

| Resource | Absolute campaign ceiling | Concurrency |
|---|---:|---:|
| CPU | 500 billed CPU node-hours | 2 nodes |
| GPU | 500 billed A100-equivalent GPU-hours | 4 GPUs |
| New temporary storage | 2 TiB, also limited to 10% of measured free quota | Campaign namespace only |

Use existing approved accounts and partitions; no purchases or allocation transfers. If the site
does not expose enough accounting information to establish an envelope, do local/zero-compute work
and return a resource-unavailable disposition rather than guessing. Site policy always controls.

Commit a machine-readable budget receipt in native accounting units. Charge pilots, failed jobs,
retries, calibration and verification against it. Reserve 20% for verification and repairs; reserve
the scheduler's maximum billable cost before every submission. Reconcile actual charges afterward.
Do not consume another lane's allocation or cancel its jobs.

Within this envelope, cost and reserve measurement development, its independent coverage/verification,
and inference separately, recording shared costs once. Protect the costed measurement-completion
reserve from inference expansion. The 20% verification/repair reserve is a floor, not a claim that
all required validation fits inside it; reserve the full priced validation cost if larger. Release
unused stage reservations only after that stage's disposition, without increasing the total cap.

Pilot costing precedes array expansion. Spend at most 5% on initial cost/variance pilots and at
most 10% on the targeted cleanup. At most two retries per task for a diagnosed infrastructure
failure; scientific failure never triggers an identical retry. A genuine code repair produces a
new version and invalidates dependent results. Retain enough budget to verify whatever is produced.

When a full method is unaffordable, follow the predeclared hierarchy: coarser joint-5D reporting,
then the `(E_avail,W)` projection, then fixed contrasts. A fixed-estimator conditional result
retains section 6's adoption restriction at every scope. If no defensible fallback fits, finish
with a resource-limited scientific disposition, measured costs, and a priced next increment.
Do not wait for permission to exceed the cap and do
not label budget exhaustion a scientific failure. Queue waits are not failures: maintain monitoring,
checkpoint progress and resume across sessions without duplicating submissions.

## 4. Phase A — bounded preparation and cleanup

Create an isolated campaign worktree and an immutable-input/new-output namespace. Inventory exact
data, simulation, event identities, weights, truth definitions, generators, masks, bin widths,
systematic bands and central/covariance pairings. Audit every publication figure's actual reader.
Distinguish fixed predictions from predictions tuned on these data and record finite-MC effects.
Initialize section 10's paper-wide completion table from the actual note, primer and paper,
including claims outside the scalar-5D campaign. Route dependencies to their governing records;
inventorying them does not authorize repeating completed studies or another lane's work.

Reuse existing implementations where their contracts fit:

- `nd-unfolding/mnv_guarded_run.py`: cluster execution and import-root checks.
- `project_cov_nd.py`: projection, variant enforcement, closed-file digest and row-map readback.
- `z_build.py`, `z_grade.py`, `z_contract.py`, `z_statistics.py`: existing construction/grade
  machinery, with historical grades kept intact.
- `bootstrap_nd.py`, `unified_throw.py`, `unified_throw_cov.py`: inspect actual sampling semantics
  before reuse; a file named bootstrap or throw is not proof of a valid null experiment.
- `run_p4_unfold_std.sh`, `p4_check_verifier_token.py` and associated receipts: preserve protected
  baseline and code bindings; obtain current verification rather than bypassing refusals.

Fix only defects that prevent a named campaign deliverable. Keep structural and scientific changes
in separate commits. Do not move entire directory trees, delete evidence, rewrite history, or
reformat unrelated code. No generic new framework is needed: use a configuration, reusable
measurement/inference functions, a runner and independently readable result receipts.

**Exit:** clean smoke build, verified immutable inputs, reproducible module resolution, isolated
outputs, functioning monitoring, and a minimal projection reproduced from stored operands.
Stop cleanup here; remaining unrelated issues go to the backlog.

## 5. Phase B — freeze the inference and measurement contract

Write and commit a machine-readable contract and short rationale before evaluating new observed
test statistics. Include exact versions/digests, all masks, partitions, generator predictions,
estimator seeds, reporting functionals, units, nuisance domains, test formulas, calibration design,
selection procedure, tolerances, multiplicity rules, resource stages and terminal branches.

For each reported measurement functional, also freeze the interval construction at 68% and 95%,
including centering, any bias treatment, boundaries and data-dependent choices. Identify which
matrix estimates sampling covariance, a second moment about a nominal result, or another declared
uncertainty object, with its normalization and use. None is an interval prescription by itself.
Do not assume that taking square roots of diagonal entries establishes either coverage level.

The data and localization have already been examined. Calling this contract predeclared does not
make the analysis blind. Inventory choices informed by data. For confirmatory inference either
reproduce their selection in each null experiment or use a genuinely untouched independent sample.
If neither is possible, label the resulting comparison exploratory; do not claim post-selection
calibration merely because the final formula was frozen later.

Default primary comparison: a coarse partition of the joint
`(p_T, p_parallel, E_avail, q3, W)` distribution. Cells must retain subdivisions in every coordinate
where physical support and detector resolution permit, with the physical constraints between
coordinates preserved. Freeze the cell map and its aggregation operator. This is a joint-5D test
at that resolution, not a validation of every fine bin or a claim of five independent degrees of
freedom. If support forces an axis to be integrated out, label the resulting scope accordingly.

Keep `(E_avail,W)` as a reporting product, a secondary comparison if calibrated, and the first
lower-dimensional fallback. It cannot replace the joint test without recording that the joint-5D
objective remains unmet. Keep total-rate and shape-only comparisons distinct. Fix the generator
list from the paper's traceable predictions; GENIE variants are separate hypotheses, not independent
confirmations. Freeze the family of generator, scope and rate/shape tests, including any fallback
selection, and use a fixed familywise procedure such as Holm for claims of rejection within it.

Choose a finite hierarchy of contiguous reporting partitions from existing physical bin edges,
support and detector resolution. Coarsen catch bins only with their actual widths and fiducial
meaning preserved. Set explicit support criteria from the inspected inputs. Never choose masks,
binning, modes or regularization by maximizing observed generator disagreement. Select the finest
partition satisfying the frozen gates using development simulations only, then lock it for
independent validation. Publish the hierarchy and rejected alternatives.

Include development and independent-validation alternatives that change cross-coordinate
dependence, including physically supported changes hidden by the `(E_avail,W)` marginal. Freeze
their amplitudes and numerical power requirements before independent validation. Report which
departures the joint statistic can detect; sensitivity only to rate or the two-dimensional marginal
does not satisfy the intended joint-5D sensitivity objective. These power requirements establish
usefulness for named alternatives, not universal sensitivity or a requirement for observed rejection.

For each required alternative, record the physical mechanism, the affected joint dependence,
its support/positivity constraints, and an independently justified amplitude scale. Acceptable
anchors include documented detector resolution or response uncertainty, externally motivated
physics variations, and traceable differences between specified generator predictions. State
whether an anchor was informed by these data; such an anchor is not independent merely because
it comes from a generator tune. Verify numerically any claim that a deformation preserves the
`(E_avail,W)` marginal. An alternative must remain physically admissible at every tested amplitude.

Every qualifying power alternative must be outside the tested null family, including its allowed
nuisance variations. Variations inside that family belong in false-positive validation, not
evidence of desirable rejection power. State how each alternative is distinguished from the null
after detector response and allowed nuisance treatment; changing a truth parameter alone does not
establish that distinction. If an alternative is observationally indistinguishable from an allowed
null member, it cannot qualify the power gate.

Freeze a power curve over amplitudes including the scientifically relevant scale, the required
power at that scale, and the confidence-bound rule for passing. Justify the numerical power target
by the intended scientific use before independent validation. A large, easily detected deformation
may be a positive control but cannot be the only qualifying alternative. Do not enlarge amplitudes
or lower the target after a failure; if meaningful amplitudes cannot be justified or detected,
record that the joint sensitivity objective remains unmet.

Preferred statistic: a quadratic residual statistic on that stable coarse representation, with
its inverse/regularization fixed by simulation-based calibration. Specify covariance of the actual
residual, including shared data/MC or tuning dependence where present; do not blindly sum two
covariances. Try coarser joint partitions before the projection and fixed-contrast fallbacks. Do not
invert the raw 5D covariance or assign degrees of freedom from a convenient pseudoinverse cutoff.
Calibrate the statistic's null distribution through section 7; a calibrated joint test need not
estimate or invert the full fine-bin covariance. Any alternative statistic must declare its joint
sensitivity, selection procedure and cost within this same contract.

### Feasibility decision before candidate production

Freeze a pilot contract first, including the proposed scopes, truth/nuisance grid, coverage and
tail targets, and independent sample splits. Within section 3's pilot allowance, measure at least
one complete candidate construction and one complete measurement-coverage experiment; also measure
a complete null experiment for each inference method proposed for production. A measurement-only
feasibility decision does not require unaffordable inference-only stages. Include
background treatment, unfolding, any uncertainty reconstruction inside each experiment, finite-MC
variation where required, and all seed averaging. Record native billed cost, wall time, memory,
storage and which costs are shared versus repeated. If the pilot cannot fit, record that limit;
do not infer a full-experiment price from an isolated fit or covariance assembly.

Before expanding arrays or beginning expensive candidate development, commit a feasibility receipt
for each proposed scope. It must contain:

- The number of reported functionals, null scenarios, generators and validation tests, with the
  simultaneous confidence-bound correction used in section 7.
- Exact binomial sample-size calculations for coverage, false-positive control and p-value
  precision, plus the planned probability of passing those checks under the stated design values.
  Use method-appropriate calculations where binomial assumptions do not apply. A nominal
  confidence level alone is not a sample-size or assurance calculation.
- The section 7 validity route: independently verified finite-sample justification or empirical
  calibration. For the former, identify which size-validation runs the justification replaces
  and price the implementation checks that remain. Do not omit coverage, physical-model checks,
  power measurement or requested p-value precision on the strength of a test-validity theorem.
- Separate development, calibration and fresh validation counts; the cost of seed studies,
  permitted revisions and independent reproduction; and the reserved verification/repair budget.
- A separately costed measurement-completion checkpoint and the additional cost of joint inference
  at each proposed precision tier. Identify which validation experiments can legitimately serve
  both tasks without compromising independence or changing their sampling populations.
- A total CPU/GPU/storage forecast with uncertainty and a conservative reservation margin,
  compared with the measured remaining envelope in each resource pool.
- Separate feasibility dispositions for the named measurement scope and inference method:
  feasible to attempt, infeasible within the envelope, or unresolved dependency. Identify joint-5D,
  restricted inference and measurement-only scopes explicitly. Feasibility is not a scientific PASS.

Lock the affordable scope and precision tier before evaluating new observed statistics. Re-cost
any changed estimator family or calibration method before expansion. Do not spend the development
budget first and discover afterward that independent validation is unaffordable. An unaffordable
joint test remains an unmet objective even when a projection campaign proceeds successfully.

If measurement coverage is affordable but joint inference is not, complete and independently verify
the measurement scope, then record the inference limitation and costed next increment. Assess the
already permitted shallower p-value tiers before abandoning joint inference. Do not widen the
measurement's validated scope or relax a scientific gate to make either forecast fit.

## 6. Phase C — establish reportable uncertainty scope

First reproduce the existing projection and numerical conditioning without redoing completed
central-value campaigns. Then distinguish construction correctness, algorithmic stability,
conditional repeated-experiment coverage and physical systematic scope in separate result fields.

Proceed only within section 5's costed feasibility decision. Choose candidates in this order:
existing fixed estimator on a stable reporting partition; a reproducible deterministic
implementation; a fixed seed-averaged estimator.
Keep at most these three families and at most two development revisions per family.
These are new candidates, not adopted by ancestry. A changed estimator requires its own matched
central value and uncertainty construction, plus relevant marginal/closure regression checks.
This is a bounded stabilization campaign, not an unrestricted architecture or hyperparameter search.
If these families fail, a different model-family campaign is a separately costed next increment.
Advance to a later family only for a recorded unmet requirement; do not exhaust all three after
one satisfies the selected scope's gates. A validation-driven revision uses fresh validation data
and counts against the same family/revision limits and budget.

For each candidate declare what each seed changes. Distinguish repeat-run reproducibility,
estimator sensitivity, and repeated-experiment coverage. Identical outputs from an unused seed
or deterministic execution establish reproducibility only; they do not replace the applicable
stability, closure/coverage or joint-power evidence. A deterministic candidate may qualify on its
actual scientific evidence; determinism is not itself a failure.

Use fresh, complete seed propagation through every affected stage, including all five lateral
bands. Paired comparisons must use a common pinned implementation and matched nuisance throws.
Run at least ten independent estimator seeds in development when estimating a seed-distribution
spread; two seeds or nested throw subsets do not estimate that distribution. For seed averaging,
validate independent groups of the declared size; do not count the individual seeds as independent
replicas of the averaged estimator. Treat the training-seed contribution according to the declared
estimator, avoiding duplication with any seed-randomized statistical ensemble.
Freeze the precise object and stage being averaged and apply that estimator consistently to the
nominal result, nuisance variations and repeated experiments. Averaging existing covariance
matrices is not by itself validation of the uncertainty of the averaged estimator.

Retain **5% maximum relative movement of projected standard deviations** as the default new
stability gate over the frozen functionals and tested complete seed ensemble. State its finite
tested scope, never an all-seeds guarantee. Record the central-value shifts on the same functionals.
The frozen functionals must cover the joint contrasts or retained modes used by the primary
statistic, not just individual cell variances or the `(E_avail,W)` projection. Define modes from
development inputs and compare all seeds in a common basis; do not rotate each candidate into
its own basis and call the resulting marginal agreement correlation stability. Stable diagonal
errors do not establish stable correlations or a stable inverse-covariance statistic.

For every comparison seeking inference qualification, additionally measure the seed sensitivity
of the complete test on matched development and validation experiments: the statistic, null
critical values, rejection behavior and power, at that comparison's named scope.
Freeze numerical tolerances and their Monte Carlo uncertainty treatment before independent
validation. Separate covariance movement from central-value movement and also evaluate their
combined effect. Joint-inference qualification requires these test-level gates as well as the
5% functional gate; a failed joint gate cannot be cleared by stable projected error bars. In Phase E,
report the observed comparison's seed sensitivity under the same frozen procedure without
selecting a favorable seed or refitting the tolerances.
Do not silently relax the threshold if it fails. A fully fixed-seed estimator can be evaluated for
conditional coverage, but this does not discharge seed robustness; any such result must explicitly
restrict its interpretation and cannot qualify for automatic adoption under section 9.

Build statistical, detector, flux, model and algorithmic contributions under an explicit sampling
or nuisance model. State which variations are probabilistic and which are deterministic alternatives.
Systematic universes are not automatically independent pseudoexperiments. Do not add an arbitrary
6.145% uncertainty, rescale until a desired p-value appears, or invoke Hartlap/Student-t formulas
without their sampling assumptions. Trace physical hadronic-response coverage to actual documented
variations; an unmodeled concrete response effect remains an identified gap, not a zero.

**Exit:** a frozen estimator and reporting scope with validated construction, matched central
values, seed-study receipt, complete declared nuisance inventory and no unidentified required input.
If all candidate families fail, preserve the adopted result and report that no successor qualified.

## 7. Phase D — independent calibration and coverage

### Measurement coverage and its checkpoint

Validate the actual frozen intervals against known truth, using a declared grid of physically
justified truth shapes and nuisance settings that includes departures from the training/nominal
generator. Include supported correlation deformations relevant to the claimed joint reporting
scope. Separate regularization bias relative to known truth from ensemble displacement about a
nominal estimate; one does not measure the other. Nominal-generator closure alone cannot qualify
coverage over the broader declared truth class.

State which quantities are fixed and which are regenerated in each experiment: data, finite MC,
training randomness, physical nuisances and auxiliary measurements. Distinguish coverage at fixed
nuisance settings from coverage averaged over a chosen nuisance distribution. A mixture-averaged
pass cannot establish fixed-nuisance coverage. Report the tested truth/nuisance domain explicitly;
neither a finite grid nor an uncertainty-band construction is a uniform guarantee outside it.
Generate the experiments at the event/reconstructed-data level and rerun the backgrounds, unfolding
and interval construction required by that sampling model. Independent development and validation
samples and the end-to-end requirements below apply to measurement coverage as well as inference.

Regularization bias can cause unfolding intervals to undercover even when estimator variability
is well estimated; see [Kuusela and Panaretos](https://arxiv.org/abs/1505.04768).
This motivates the truth-based interval check, without prescribing their estimator or correction.

Once the measurement meets sections 6, 7 and 9's applicable gates, commit an independently verified
measurement checkpoint and deliver its qualified scope under the delegated adoption rules. The
coverage thresholds below apply here; inference size, power and tail requirements remain separate.
Perform inference work within its remaining reservation; failure of that work does not retroactively
invalidate a measurement unless it reveals a defect in the measurement's own construction or scope.

### Inference experiments

Specify the null as a generator truth prediction plus the documented detector, nuisance and sampling
model. Generate repeated experiments at the event/reconstructed-data level and rerun all stochastic
or data-dependent analysis stages required by that model, including backgrounds, unfolding and
uncertainty estimation. Conditional treatment of finite MC must be explicit; unconditional claims
must include its variation and shared correlations. Use independent development, calibration and
validation seeds, and retain the split manifest.

Cheap draws from a multivariate Gaussian with the final covariance may test algebra. They cannot
by themselves establish unfolding coverage or calibrate the complete procedure. A surrogate is
permitted only after an independent end-to-end comparison meets frozen tail/coverage tolerances;
otherwise reduce the reporting scope or return an unresolved-calibration disposition.

### Finite-sample validity versus empirical calibration

Declare which route establishes test size before pricing production:

- **Verified finite-sample route.** A fully specified null with exact simulation and a valid
  exchangeable rank construction can establish finite-sample size control without a second
  large outer ensemble merely to re-estimate that same mathematical guarantee. Provide the
  applicable theorem or derivation and map each assumption to this implementation: observed
  and simulated data treatment, statistic construction, conditioning, independent randomness,
  ties, sample count/stopping rule, and any selection or fitting. Obtain independent verification
  of that mapping and exercise known-null, defect and innocent controls. A plug-in fitted null,
  approximate sampler, learned surrogate or fitted nuisance value does not qualify automatically.
- **Empirical/approximate route.** Where such a justification is unavailable, retain the
  independent size checks and tail-validation requirements below. Do not claim exchangeability
  from similar-looking simulated and observed distributions.

For a verified finite-sample route, the contract may replace the empirical size gates at 0.05,
0.01 and 0.001 with the verified guarantee at those levels. Name every replaced gate and its
remaining executable implementation checks in the feasibility and verification receipts. Failure
of an implementation check suspends this route; repair and re-verify it or use the empirical route.
For an ordinary independent Monte Carlo rank test, `(k+1)/(B+1)` and its tie convention belong
to the validity argument, not just a correction applied to an arbitrary approximate test.
Reference: [Phipson and Smyth, *Permutation p-values should never be zero*](https://arxiv.org/abs/1603.05766).

Finite-sample validity is conditional on the specified null and its assumptions. It does not
validate the detector model, systematic completeness, unfolding interval coverage, power or
composite-null nuisance treatment. Those obligations remain, as do the requested Monte Carlo
precision and reporting limits. A valid finite-simulation test is not an arbitrarily precise
estimate of an underlying tail probability.

Default validation targets, frozen before new validation runs (empirical size gates may be
replaced only through the verified finite-sample route above):

- Pointwise 68% and 95% interval coverage on every reported functional. Require simultaneous
  one-sided 95% binomial lower confidence bounds across the declared validation grid to exceed
  0.66 and 0.94 respectively. These are campaign tolerances, not proofs of exact nominal coverage.
  Simultaneous confidence in these validation bounds is distinct from simultaneous coverage of
  all measurement intervals; claim the latter only with its own construction and validation.
- At test level alpha=0.05, require simultaneous one-sided 95% upper confidence bounds on the
  false-positive fraction to be at most 0.06 across the declared null scenarios.
- Publish the scenario grid and its relation to the physical nuisance domain. Discrete grid
  validation alone is not a uniform guarantee over a continuous nuisance space.
- Report power and minimum detectable departures for fixed scientifically relevant alternatives;
  never select an alternative using observed significance. Low power is a measured limitation,
  not proof of generator agreement. Apply section 5's frozen power requirements for the joint
  correlation alternatives when deciding whether the joint-5D objective is met.

### P-value precision and tail scope

The default requested range for numerical p-values is `0.001 <= p <= 1`. These are proposed
reporting targets, not predictions of the observed result. For ordinary independent Monte Carlo
exceedances, use exact binomial intervals for the underlying tail probability alongside the
`(k+1)/(B+1)` test p-value. Require simultaneous 95% Monte Carlo intervals across the declared
reported comparisons. The maximum distance from the estimate to either interval endpoint must be
at most `0.005` for `p >= 0.05`, and at most `0.25 * p` for `0.001 <= p < 0.05`.
For weighted, composite-null or sequential methods, freeze a valid uncertainty construction for
that method instead of treating weighted or adaptively stopped draws as binomial counts.

Passing the empirical `alpha=0.05` size check does not validate smaller tails. For the empirical
route's default range, also validate rejection fractions at `alpha=0.01` and `0.001`, requiring simultaneous one-sided 95%
upper confidence bounds no larger than `1.2 * alpha` over the declared null scenarios. State that
these are finite-grid tolerances. For surrogate or asymptotic calibration, additionally freeze and
validate numerical tail-error bounds against independent end-to-end experiments throughout the
reported range; agreement at the three size checkpoints alone is insufficient.

The early feasibility receipt may select a shallower tier, with smallest reportable p-value
`0.01` or `0.05`, before new observed statistics are evaluated. Keep the same precision rules
where applicable and validate the size checkpoints within the selected range. Record any such
restriction in the contract and final result. A deeper tier needs its own frozen precision target,
tail validation and cost forecast within the envelope; no five-sigma reach is presumed.
For the verified finite-sample route, establish the size guarantee over the selected range instead
of repeating the replaced empirical checkpoints; the same numerical precision requirements apply.

If the observed result lies below the validated range, or the precision requirement fails, report
the Monte Carlo interval or a valid one-sided bound at its actual confidence level, with an explicit
precision limitation. Do not convert an unresolved tail to an exact significance. For a numerical
Gaussian-equivalent value, use the one-sided convention `Z = Phi^{-1}(1-p)` for `0 < p < 1`,
transform the p-value interval as well, and round to the supported precision. Endpoints at zero
or one yield bounds, not finite Z estimates. Report raw and multiplicity-adjusted
p-values separately and identify which is converted; a rejection claim must survive both the
declared multiplicity procedure and Monte Carlo uncertainty. None of these conventions equates
five-dimensional inference with five-sigma evidence.

Choose validation sample sizes from exact binomial precision calculations and the pilot cost
before production; there is no fixed minimum that overrides the confidence-bound requirements.
Use a fixed sample count, or an explicitly anytime-valid sequential confidence procedure. Do not
stop a conventional Monte Carlo test when it first reaches a desired p-value.

Distinguish nuisance-averaged calibration from frequentist size control for a composite null.
For the latter use a justified least-favorable construction or confidence-set method with its
coverage allowance, not merely the largest p-value from a handful of convenient variations.
If the nuisance domain cannot be defended, report a conditional comparison with that limitation
and do not promote it to a general generator-exclusion claim.

For exchangeable, fully specified Monte Carlo null tests use `(k+1)/(B+1)` with its assumptions
stated and a Monte Carlo uncertainty interval. Zero exceedances is not p=0. Account for any
parameters fitted to data by reproducing fitting in the calibration. Quote a Gaussian-equivalent
significance only with the tail convention and validated numerical precision; no unsupported tail
extrapolation or automatic five-sigma claim.

**Exit:** independent validation meets all relevant gates, or an explicit undercoverage,
miscalibration, insufficient-precision, insufficient-power, or resource-limited result.
Do not use independent validation failures to tune and re-test on the same sample. A permitted
development revision requires a fresh validation set and remains inside the campaign budget.

## 8. Phase E — evaluate the frozen comparisons

Only after the candidate and validation results are frozen, evaluate observed statistics for the
specified generators. Carry estimator and nuisance sensitivity, Monte Carlo precision and the
declared multiplicity correction into the results. Store the raw operands as well as derived p-values.
Identify each result as joint-5D at the frozen resolution, a projection, or a fixed contrast;
give its validated p-value range, achieved precision and power. The existing high-energy/high-mass
localization remains descriptive unless its selection is calibrated. A test of fixed generator
predictions is not automatically a test excluding every
possible tuning or the entire generator family.

If the approved scope permits several calibrated treatments, report their prespecified sensitivity
range. Call its maximum p-value a conservative bound only if the construction actually establishes
that property over the relevant model class. Do not call a range over arbitrary checks a confidence
interval. Preserve negative and null results with the same provenance as significant results.

## 9. Conditional adoption and terminal branches

Activation delegates adoption **only** when all applicable conditions below are met:

1. Exact new source and reporting-product bytes, aggregation maps, units, masks, estimator,
   nuisance model and matched central values are identified and independently reproduced.
2. The new frozen contract's construction, stability and coverage gates pass for the named scope.
   No old failed grade is edited, no inherited exception is used, and no required physical
   uncertainty remains unidentified or omitted without a justified restriction of the estimand.
3. An independent reviewer verifies the measurement from operands, confirms the scientific scope,
   and finds no unresolved result-changing defect. A second agent repeating the author's summary
   is not independent evidence. Corrections receive targeted fresh verification.
4. For every calibrated inference result, including a non-rejecting comparison, the test-level
   seed-stability gates in section 6 and the test-validity route, data-selection treatment,
   nuisance interpretation, multiplicity and tail precision in section 7 additionally pass for
   the named comparison. Joint-5D qualification additionally requires the joint seed-stability
   and section 5's physically anchored joint-power gates; a large-deformation positive control
   alone does not qualify it. A qualified projection comparison does not require a successful
   joint-5D test and does not fulfill the joint-5D objective.
5. The ledger, run log, status, release manifest and three deliverables state the same scope.

Measurement uncertainties may qualify separately from inference for exactly their validated
scope under conditions 1-3 and 5. The additional inference gates are not conditional on a small
p-value or on reporting a Gaussian-equivalent significance.

Record adoption through the existing decision mechanism, citing the owner's activation as the
delegation and explicitly labeling the act as delegated. Use the exact digest; never imply the
owner personally inspected future bytes. Keep the earlier adopted object recoverable and state
which reporting products, if any, the new adoption supersedes. Any new exception remains outside
this delegation; report the candidate without adopting it instead of asking for an exception.

| Outcome | Required final product |
|---|---|
| Uncertainties and joint-5D inference qualify | Adopt the exact validated reporting product under the delegation; report joint comparisons at the frozen resolution, their power and precision, whether significant or not |
| Uncertainties qualify, inference does not | Adopt only the qualified measurement scope; publish no uncalibrated significance; identify the remaining inference limitation |
| Only restricted projections or contrasts qualify | Adopt and report that scope and any separately calibrated comparison; the joint-5D objective remains unmet |
| No new candidate qualifies | Retain the prior adopted-under-exception state, disclose failures and scope, and provide a bounded next-step recommendation |
| Resource or external evidence unavailable | Finish the independent work; return an evidence-limited disposition with exact missing inputs and measured costs |

No branch requires a routine permission request. No branch guarantees a publishable significance.
The last two branches complete this campaign's disposition, not the scientific goal of reportable
successor uncertainties. Mark that distinction explicitly; do not claim the objective achieved.
Every branch must also report joint-5D inference status and section 10's paper-wide readiness
status. A qualified scalar result alone cannot close unrelated publication dependencies. Failure
to meet a frozen power requirement leaves the joint sensitivity objective unmet even if test size
is controlled; any reported p-value must retain that measured limitation.

## 10. Phase F — verification, delivery and release preparation

### Paper-wide completion table

Create this table during Phase A and reconcile it against all three deliverables before closeout.
Use one row per retained scientific claim or reporting product, splitting workstream rows wherever
central-value, uncertainty or inference status differs. The rows below are required categories,
not assertions that their gates currently pass.

| Required category | Completion evidence to enumerate |
|---|---|
| 2D reproduction | Retained central values, adopted matched uncertainties, interpretation of comparisons and supported reproduction routes |
| 3D extension | Retained central values, anchors/closures, uncertainty projections from the applicable adopted source and scope of comparisons |
| Scalar 4D/5D measurement | Each retained reporting partition, matched CV/uncertainties, physical nuisance scope, seed/coverage evidence and exact adoption |
| Joint-5D generator inference | Frozen joint map/statistic, hypotheses, selection treatment, nuisance interpretation, calibration, power, multiplicity and tail precision |
| Projection and contrast inference | Separate scope and validation for each retained comparison, with no substitution for joint-5D completion |
| PET/FPS material retained in the paper | Exact permitted diagnostic or measurement scope from governing records; PET remains diagnostic and this inventory reopens no campaign |
| Reproduction and release package | Every retained figure/table linked to available operands, allowed access, checksums and a tested reproduction matching the advertised scope |
| Note, primer and paper | Consistent claims and limitations, verified figures, clean builds, synchronized sources and both verified remote heads |

Each populated row records the claim and deliverable locations; required uncertainty and inference
scope (or justified not-applicable status); exact evidence/product digests; adoption or ruling;
independent verification; reproduction/package status; accountable owner; unresolved dependency
and its governing record; and an executable closure criterion. Use `READY`, `OPEN`,
`BLOCKED-EXTERNAL` or `EXCLUDED-BY-RECORDED-SCOPE` for readiness, separately from scientific
grades. Exclusion requires its actual scope decision and removal of dependent claims from all
deliverables; inability to finish is not itself authorization to exclude a claim.

Reuse valid committed evidence for completed studies. Close in-scope documentation, packaging
and verification dependencies under this plan; route out-of-scope scientific changes or external
decisions to their owners without reopening them. Any unresolved requirement for a retained claim
keeps publication readiness open. Classify review residue by whether it affects a retained claim,
its reproduction or a governing gate; an unrelated repository backlog is not a reason to repeat
completed scientific work.

Report four separate fields: `campaign_disposition`, `reportable_uncertainty_scope`,
`joint_5d_inference_status`, and `publication_readiness`. Mark publication readiness `READY` only
when every retained claim's row is ready, required publication blockers are closed, and the release
package and synchronized deliverables below are verified. If a required joint-5D result cannot be
delivered, record the unmet requirement; a narrower publication needs a recorded scope decision.
Public deposition, release tagging and submission remain separate acts after readiness.

### Verification and delivery

Reviewers work read-only in isolated worktrees and inspect status afterward. Limit review to the
contract and changed scientific/computational paths. Repair result-changing findings, rerun the
affected measurements and obtain targeted independent verification. Do not create an endless
repo-wide audit loop. A remaining material defect means the affected product cannot be adopted;
it does not prevent delivery of an honest final disposition.

Tests must exercise real risks: order/units/masks, CV centering, covariance/central pairing,
seed propagation, overwrite prevention, import roots, false-positive and innocent controls for
guards, calibration against known examples, and a true small end-to-end reproduction. Run the
existing relevant projector/Z/P4 tests and hooks. Never bypass a failing protected gate with
`--no-verify`, environment spoofing, or a silently altered receipt.

Prepare an external-ready package containing reporting edges, CVs, covariances, row maps,
joint-cell aggregation and projection matrices, masks, units, generator predictions,
model/seed/selection contracts, calibration operands and receipts, licenses/access restrictions,
checksums and a minimal reproduction example for each retained measurement and inference scope.
Include the full source covariance or explicitly limit the released reproduction claim to shipped
reporting representations. Distinguish recomputing a p-value from saved null statistics from
regenerating the null experiments. No claim of full reconstruction from a package that omits
required operands.
Resolve the existing `acceptance_question: UNDECLARED` for each newly promoted reporting product,
or withhold promotion for that scope. Test the package on a fresh checkout without private paths.

Build note, primer and paper with `build_all.sh` in both repositories; inspect logs for unresolved
references and genuine errors, verify fresh output timestamps, containment and rendered figures.
Also build the paper from a clean tree with the `output` job name used by Overleaf. Synchronize
sources and figures without overwriting unrelated changes. Commit and push both repositories,
verify actual remote heads and report them. A release manifest may be committed; final public
release tagging, data-host deposition and journal/arXiv submission remain separate acts.

## 11. Durable progress and recovery

The first implementation commit creates one campaign index and one structured state file. Record
phase, pinned contract, input/output digests, job IDs and owning worktree, remaining budget,
verification state and the next deterministic action. Register the work through the control-plane
source tables and an available OI identifier; regenerate views rather than hand-editing them.

Every compute receipt names the measured quantity and what its terminal result cannot authorize.
Commit evidence and required ledger/run-log/status updates before treating results as quotable.
Resume from committed receipts plus live scheduler observation; a missing session or a context
reset must not resubmit an existing job. Never use temporary local paths as the recovery route.

The executor may choose exact filenames and environment-specific commands after inspecting and
dry-running the current interfaces. This plan deliberately authorizes outcomes rather than inventing
untested launcher flags. Routine implementation uncertainty is delegated judgment; missing evidence
is a reported limitation, never a fabricated fact.

The final report gives the four separate status fields from section 10 and the completed paper-wide
table. State what uncertainty scope is reportable; whether joint-5D inference qualified and at what
resolution; which generator hypotheses were tested; calibrated p-values with their precision and
power, or why none qualify; every failed gate and retained limitation; measured resource use and
costed remaining work; adopted and superseded digests; reproducibility evidence; and both remote
heads. List unresolved publication dependencies explicitly. Name the next external decision if the
deliverables are ready for one; a terminal campaign report is not a publication-readiness certificate.
