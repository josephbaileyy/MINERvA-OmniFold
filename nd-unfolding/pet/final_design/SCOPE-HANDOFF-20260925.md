# PET final-design selection study

## Purpose and activation

MINERvA-OmniFold uses particle-cloud classifiers inside iterative unfolding to
recover neutrino interaction distributions from detector measurements. This study
continues the completed PET improvement campaign. Its objective is to select and
validate a complete design for subsequent PET method development, including its
uncertainty procedure, rather than finish with an unranked collection of promising
components. PET remains diagnostic; selection here is not publication adoption.

This document is an execution brief, not evidence of a new result or a launch
authorization by itself. Submission of the accompanying
`GOAL-20260925-pet-final-design.txt` activates the new study and its scope below.
No experiments were performed in preparing this brief. Preserve the predecessor
campaign and its terminal disposition.

The governing preference is scientific performance first. Prefer the smaller
network only when its performance is demonstrably comparable and its measured
cost substantially lower. Otherwise use the larger or more expensive design when
the evidence supports it. Available compute may be used substantially; the small
network is a reference and contender, not the presumed winner.

"Best" means best among a declared, meaningfully tested candidate family under
the frozen scientific and cost criteria. It does not mean universally optimal.
Aim for a selected, validated design. An honest no-eligible-design or unresolved
comparison is a permitted terminal outcome only after the discriminating studies
and measured practical limits below have been addressed. Do not force a winner.

## Durable starting state and recovery

The completed improvement campaign is on `pet-improvement-20260922`, at verified
remote head `9368ec9e55eb486109498772753825fc24616851` when this brief was prepared.
It is not merged into main. Its predecessor is `pet-direct-token-comparison` at
`7090fcc12ce8119f7a5fc4fa05265a8486f9049a`. Verify remote heads again at startup.

Read current canonical `AGENTS.md`, `docs/CURRENT_WORK.md`, relevant records in
`docs/OPEN_ITEMS.md`, `KNOWN_ISSUES.md`, `nd-unfolding/ND_OMNIFOLD_STATUS.md`, and
the routed PET environment/execution contracts. Old orientation files on the
campaign branch do not override current canonical rulings. Use the predecessor
code as a pinned baseline in a new isolated branch/worktree, integrating current
guard fixes deliberately and recording their effect. Do not reset another tree.

On the pinned campaign branch, read these first, relative to
`nd-unfolding/pet/improvement_campaign/`:

1. `HANDOFF-pet-improvement-campaign.md` and `README.md` for recovery routes.
2. `REPORT-20260922.md`, especially sections 2, 5, 8 and 11-12.
3. `confirm/CONFIRM_RESULTS.md`, `confirm/results/confirm_results.json`, and the
   per-run score files and receipts that support them.
4. `REVIEW_DISPOSITION-ROUND2-20260925.md` and the first review disposition.
5. `PROTOCOL-20260922.md`, including all amendments, and `pools/POOL_MANIFEST.json`.
6. `phase_a/INTENDED_VS_EXECUTED-20260922.md`, runtime receipts, repaired runner,
   and explicit per-step configuration code.
7. `phase_f/AUSSIE_SCALAR_BENCHMARK-20260922.md` and its numerical ablation. Some
   narrative comparisons in that early memo overstate the table; prefer the
   scoped assessment in report section 8 and original measurements.

For representation details, read
`nd-unfolding/pet/configuration_comparison/CONFIGURATION_COMPARISON-20260918.md`,
`frozen_design.py`, and `receipts/model-capacity.json`. This inventory predates
the improvement study: its missing-checkpoint claim is superseded, and its
component preferences are hypotheses, not measured winners. The historical
pretrained checkpoint was recovered and entered actual fits.

Recover all required source inputs/checkpoints by committed manifests and receipt
routes. Verify hashes and access before planning dependent jobs. A local scratch
path or old scheduler observation is not a durable recovery guarantee. Bring this
handoff and goal into the new study branch; they are new specifications, not
already merged repository state.

## Findings that determine the next experiments

The predecessor's fresh-event confirmation used 12 replicates. Historical CTL at
three iterations recovered 0.316; the same recipe at ten recovered 0.505; B at ten
recovered 0.569; C at ten recovered 0.786. C's one-sided lower 95% bound was 0.763,
above the unchanged historical 0.5559785255 floor. These numbers describe the
planted energy tilt, not arbitrary physics changes.

- B changed both reconstructed-energy summaries and truth-side PDG encoding.
  Development comparisons isolated an energy-summary benefit; the final B-minus-A
  contrast does not isolate those two input changes.
- C used baseline features and changed step 2 to train on selected events and
  apply the learned truth ratio to all truth events. C was not B plus a miss-rule
  change. The combination remains to be tested.
- C at ten iterations had negative recovery under the proton stress on both
  replicates and under the neutron stress on one. B failed strongly under the
  neutron stress. Their PET-path mechanisms are not established.
- C at three iterations had mean recovery 0.570, lower bound 0.544, and positive
  recovery in all 12 observed stress cells. There were only two replicates per
  case; neutron-stress mean recovery was about 0.017. This is a reference
  candidate, not established robustness or substantive neutron recovery.
- Particle multiplicity is hidden from the scalar energy marginal, not absent
  from PET's truth inputs. The stored PDG codes contain the multiplicity used in
  the original distortions. Scalar failure explanations do not automatically
  explain PET's failure.
- A reco-level distinguishable distortion is not proof of an identifiable full
  truth distribution or an accurately learned detector ratio.
- No uncertainty coverage was run. No estimator or uncertainty product was adopted.
- The old comparison did not run the declared optimizer for the pretrained arm;
  its allegedly shared truth step also differed. The old between-arm advantage
  cannot isolate architecture, representation, or pretraining.
- The executed pretrained PET2-small has 2,758,702 parameters. The 890,130 count
  belongs to a different transformer in the earlier inventory. Our detector PET
  has 47,041 parameters. Measure actual new-model counts and costs at runtime.
- Carrying misses and iteration count had large measured effects. This does not
  establish that network choice is irrelevant.
- The historical adequacy reference is not an information or attainability bound.
  Preserve it for comparability; do not make it the only scientific criterion.

## Scope, authority and resources when activated

The study includes implementation, repairs, existing-source extraction, simulation
preprocessing, training, inference, scaling, new statistical/seed ensembles,
simulation-only bias and coverage validation, independent review, preservation,
commits, pushes and a draft PR. Parallel specialist work and independent reviewers
are in scope. Reviewers use isolated, read-only worktrees inspected afterward.
Do not contact collaborators through external messaging services.

Use existing authorized accounts and allocations. There is no new arbitrary
campaign GPU-hour cap. Substantial use of the compute available to this study is
appropriate when it resolves a scientific or selection uncertainty. Do not buy
resources, exceed quotas, exhaust a shared allocation, or cancel/reprioritize
other work. Measure remaining allocation, concurrent commitments and storage;
reserve enough budget for confirmation, coverage, review and preservation before
spending on architecture searches. Maintain actual charged CPU/GPU usage,
end-to-end wall time, storage and a forecast for remaining work. Revisit the
forecast after each substantial stage. Scarce resources should change the
experiment's information value per cost, not silently predetermine the winner.

Routine repairs, retries, scaling, extraction and prospective protocol amendments
within this study do not require repeated approval. Material changes to scientific
scope or resource ownership do. Follow the canonical freshness and direct
scheduler checks before compute, and launch through
`nd-unfolding/mnv_guarded_run.py`. Never disable provenance or numerical guards.

Excluded: real-data unfolding; publication adoption; changes to the adopted
scalar-5D covariance; production `C_stat`/`C_ML`; Gate-6 work; reopening OI-126;
note/primer/paper edits; merging the draft PR automatically. New simulated
validation ensembles are distinct from the declined historical PET pairing.

## Establish the experiment before searching

Create a new dated protocol and campaign namespace, preserving the old protocol
and verdict. Record exact quantities measured, candidate definitions, data access
boundaries, estimator scope and what a terminal outcome cannot authorize.

### Fresh-event capacity is a first-stage requirement

Inventory the identities actually consumed by all predecessor DEV, PILOT, FINAL,
STRESS and scaling runs. Previously inspected samples may support new development
but cannot be relabeled untouched final validation. A new hash salt or seed does
not create new events. Check any claimed untouched reserve against consumption
receipts, not just its label.

Establish adequate training, tuning, sizing, final-comparison, final-stress and
coverage populations before an expensive search. Extract additional existing
simulation where useful and authorized. Freeze their identity manifests and
access rules. Audit source-level overlap, not just serialized row indices.

Use independent pseudodata draws, separate MC event variation from estimator
seed variation, and pair contenders within each comparison replicate. A common
finite MC training bank or evaluation target induces dependence: declare it and
use an appropriate conditional or hierarchical analysis. Resampling a finite bank
does not establish independent new detector simulations. Never reduce the
precision requirement silently because disjoint pools run out. If available
sources cannot support the planned claim, quantify the limit and revise the claim
prospectively or report it as unresolved.

### Freeze decision tolerances before successor candidate results

The following are proposed methodological defaults activated with the goal:

- Preserve the historical mean-based aggregate and regional adequacy tests and
  report their confidence bounds separately. Do not reinterpret their old verdicts.
- Require the successor's selected configuration to clear the historical aggregate
  floor at a multiplicity-adjusted one-sided 95% lower bound, in addition to
  predeclared regional bias and robustness requirements. This is a new selection
  safeguard; C at three iterations is not grandfathered through it.
- "Comparable" on the historical endpoint means a simultaneous one-sided 95%
  lower bound on `R_small - R_large` greater than -0.02, not a nonsignificant
  difference. Retain +0.04 as the historical meaningful switching contrast when
  reporting improvement over the historical control. These margins do not define
  every stress metric or every new selection contrast.
- "Substantially cheaper" means at least a factor of two lower measured total
  cost to produce the prescribed validated result, including the selected
  uncertainty procedure, at matched event counts and target precision. Report
  recurring training/inference/ensemble cost separately from one-time development,
  data preparation and pretraining costs. State amortization and include measured
  cost uncertainty. Parameter count and one epoch's timing do not establish this.
- A smaller model earns a cost-based selection only after non-inferiority on the
  primary endpoint, predeclared tolerances on critical regional/topology endpoints,
  and equivalent eligibility under robustness and coverage. Savings cannot offset
  a failed physics requirement.

Complete a numeric decision table before successor performance is inspected.
Define acceptable absolute and regional bias, essential topology/joint endpoints,
non-inferiority margins for those endpoints, response sensitivity tolerances,
coverage tolerances, interval-width requirements, and treatment of near-zero
injections. Derive these from the intended diagnostic measurement precision and
known-function/null calibration, not candidate rankings. Document the physical
meaning of every tolerance. This is prospective study design, not authority to
change publication criteria. Amendments must precede affected evaluation; they
cannot rescue an observed final failure.

## Locate the multiplicity failure

Use already exposed events for development. Reproduce a small set of predecessor
results through the recovered runtime path, then instrument C and B under proton
and neutron distortions. Do not repeat completed central-value campaigns.

At each iteration measure detector ratio quality, weights pulled to truth, the
step-2 projection, and predictions on selected and missed events separately.
Include joint energy/topology residuals, species counts, weight tails, effective
sample size where valid, and variation across event and training seeds. Trace the
first deterioration. Aggregate reco energy closure alone is insufficient.

Use bounded interventions to distinguish plausible contributions:

- Truth-only learnability of known multiplicity weights, comparing raw identifiers
  with categorical PDG encoding and explicit truth multiplicity summaries.
- Detector ratio diagnostics in topology-sensitive observables and selected
  regions, including comparisons with a competent scalar baseline.
- Step-2 behavior given a controlled fixed input target, varying only truth
  representation, optimization effort or miss handling.
- Iteration trajectories and supported-region versus extrapolation behavior.
- Whole-event counts/energy and overflow information versus retained tokens.

Truth information is permitted for truth-step development and diagnostic oracles,
never as a detector input. An oracle intervention locates a limitation; its score
cannot enter the physical unfolding selection or an attainability claim.
Selection-probability or overlap diagnostics can delimit extrapolation, but they
must not erase low-acceptance events from the target. Treat clipping, damped ratio
updates, penalties and early stopping as new estimators requiring validation.

Do not require a complete causal theory before advancing a demonstrably robust
candidate. Conversely, do not call an intervention a mechanism proof merely
because its performance improves.

## Candidate development and fair comparisons

Keep CTL and C at three iterations as diagnostic anchors. The old C at ten and B
are useful failure controls. They need not consume a full large confirmation
budget after their role is established.

### Compact hybrid

Begin with controlled comparisons of C, C plus categorical truth-PDG encoding,
and that configuration plus reco energy summaries. Supply only detector-derived
quantities to the detector step. Retain muon kinematics and detector geometry.
These combinations are new candidates, not measured additive gains.

If diagnostics support them, add whole-event pre-cap energy/count summaries,
explicit validity flags, overflow summaries, and typed-object information. Check
typed-object energy coverage and overlap with cluster deposits before interpreting
an apparent gain; do not impose full energy conservation on this detector. Keep
periodic angular encoding and consistent, frozen preprocessing across legs.
Use categorical species encoding at truth level and distinguish padding from a
real species. Counts derived from a truncated truth cloud must be labeled as such.
Re-extract full counts when a whole-event claim needs them.

Test pooling versus individual routing only where information/cost measurements
justify it. The earlier synthetic pooling comparison did not settle physics
accuracy at production multiplicity. Do not inherit unreleased numerical regimes.

### Larger networks and pretraining

A genuine larger-model comparison is required; do not demote it to an optional
rerun because the compact model is convenient. Include a modestly enlarged
version of our PET and the recovered PET2-small, with enough optimization effort
to assess their performance. Escalate further in capacity, data or training when
learning curves and available resources support decision-relevant gains.

Separate causal experiments from best-package competition:

- To isolate pretraining, compare PET2 pretrained and randomly initialized with
  the same compatible inputs, architecture, truth-step policy and tuning
  opportunity. Verify initialization at the first optimizer step after cloning.
- To isolate detector representation or architecture, hold the truth-step
  configuration, split policy, initialization policy and miss rule fixed. Targets
  naturally differ after different detector fits; identical targets are not the
  requirement. Decouple random-number streams between steps.
- In the final package competition, permit each design an appropriate optimized
  recipe and representation. Do not handicap the large network with eight epochs
  simply because the old recipe used eight. Compare both trained-to-saturation
  behavior and performance at matched total compute where informative.
- A changed input schema may not fit the pretrained checkpoint directly. Preserve
  a compatible pretrained arm, document new adapters/heads and match them in the
  scratch control. Do not label incompatible or silently reinitialized weights
  a test of the original pretrained design.

Audit executed optimizers, schedules, clipping, decay, normalization, batches,
validation rows, checkpoint restoration and update counts. A declared training
recipe is not runtime evidence. Validate ratio quality; classifier accuracy or
validation-loss minimum alone cannot select an unfolding iteration or epoch.

The shared truth estimator may be a bottleneck. First establish controlled
detector comparisons; then allow justified truth-network improvements in the
complete candidates. A detector-only comparison does not settle the best complete
design, and the resulting truth architecture is our study design, not a truth-side
configuration supplied by Gregor's supervised work.

### Algorithmic alternatives

Retain topology-aware scalar GBDT/MLP and response-aware binned references as
controls with correctly matched selections, normalization and miss treatment.
They establish what the tested inputs/procedure can achieve, not universal bounds.

Give AUSSIE a bounded, correctly controlled stress comparison if the unresolved
problem involves iteration/projection or if its scalar promise remains relevant.
Match representation, miss handling, data and tuning opportunity. Its previous
tilt advantage did not establish robustness. Advance to PET only if measured
performance, stability or cost gives a reason; an early negative bounded result
can close this alternative. Do not discard it solely because it is unfamiliar.

Consider nuisance-aware unfolding only if detector-response mismatch is a
demonstrated binding problem and available independent response variations can
support inference. A reweighted generator histogram is not a new detector
simulation. Record the evidence for escalating or retiring each alternative.

Relevant primary starting points, to read and verify at execution time:

- https://arxiv.org/abs/2604.12364 (transfer learning in MINERvA)
- https://arxiv.org/abs/2504.06857 (neutrino unfolding and efficiency treatment)
- https://arxiv.org/abs/2507.09582 (practical unbinned unfolding guidance)
- https://arxiv.org/abs/2602.24282 (AUSSIE)
- https://arxiv.org/abs/2512.07074 (response nuisance parameters)

## Stopping, robustness and confirmation

Select a fixed iteration count or a fully specified data-dependent rule using
development simulations. The rule cannot inspect unknown truth during final
application. If simulation truth selects a fixed count in development, freeze
that count. If the rule uses held-out detector residuals, validate its ability to
avoid the observed truth failures rather than assume reco closure guarantees it.
Every adaptive operation must recur inside later coverage replicates.

Predeclare a finite search with milestone budgets and evidence-based escalation.
Maintain a decision table of hypotheses, contrasts, precision, measured cost and
disposition. Avoid a full Cartesian product when staged ablations answer the
question. Reserve enough resources to validate the strongest contenders properly.

The robustness library must include both signs and meaningful magnitudes of energy
tilts, energy bumps, proton/neutron changes, other relevant topology changes,
joint energy/topology distortions, generator/interaction variations, and separate
detector-response changes. Include exact matched controls for the formerly
unisolated energy-scale-plus-tilt case. Use the same response transformation in
identifiability diagnostics and PET runs. Preserve the old implemented NuWro
variant for reproduction; any corrected definition is a separately named test.

Old stress cases are development evidence now. Reserve fresh events and some
unseen distortion combinations for final stress. Do not choose the new test
family solely around failures already explained. Distinguish smooth histogram
reweightings, within-bin topology changes and actual independently simulated
responses. State which types of generator dependence remain unprobed.

Report both recovery and absolute/signed residuals. For tiny injected changes,
recovery ratios are unstable or undefined; use predeclared absolute residual
tolerances and null tests. Include uncertainty in finite-reference truth targets.
The unchanged prior cannot win simply by avoiding negative recovery. Require
useful accuracy on the designated energy, regional and topology endpoints.

Size event and seed repetitions for the decision margins, power and simultaneous
precision required. Two stress replicates per case are insufficient to establish
robustness. For a failure-probability criterion, specify the unit (case and
replicate), acceptable probability and its simultaneous upper confidence bound;
zero observed failures is not a zero failure probability. Use pilot variance
separately and do not pass pilot-selected observations off as fixed-design final
data. If sequential sampling is used, predeclare a valid sequential inference
rule rather than repeatedly checking ordinary confidence intervals.

Freeze a manageable final set, normally the strongest compact hybrid, the
strongest large/pretrained package, and any justified algorithmic challenger,
plus necessary anchors. Commit exact inputs, recipes, stopping, seeds, endpoint
definitions, hypotheses, correction for multiple comparisons and sizing before
reading final populations. Reject provenance-incomplete results before scoring.

## Coverage is part of the selected design

Construct a new simulation-only uncertainty procedure for each serious eligible
finalist. Specify conditional versus unconditional coverage, varied pseudodata
statistics, prior-MC uncertainty, training randomness, and any represented
response/model nuisance variation. Treat response sensitivities outside that
procedure separately; do not claim they are covered by a statistical interval.

Evaluate nominal 68% and 95% intervals, stating marginal versus simultaneous scope,
on the actual selected inputs, event scale, iteration/stopping rule and estimator
recipe. Rerun internal tuning, stopping or ensembling whenever it is part of the
declared estimator. Include bias, pull distributions, regional coverage and
interval widths. Trivially huge intervals cannot win a coverage contest.

Size the ensemble from binomial precision or an appropriate dependent-replicate
analysis. A nominal goal of five percentage points or better for a 95% confidence
interval half-width is a planning target, not a pass rule or a universal sample
count. Calculate the required count for the coverage acceptance inequalities and
simultaneous claims actually made; run more when the pass/fail boundary requires
it. Do not repeat the predecessor's mistake of treating available pool capacity
as adequate decision power.

If a candidate fails coverage, diagnose and repair only on development evidence,
then refreeze and validate on unused confirmation/coverage data. Do not reuse a
failed final set to certify its repaired replacement. Selection among several
coverage-tested candidates requires prespecified simultaneous inference or a
separate final validation. A coverage study at smaller scale or different k does
not certify the eventual design.

## Final selection and stopping the study

Apply eligibility before ranking: provenance, meaningful recovery, regional and
topology accuracy, stress behavior, numerical stability, and calibrated
uncertainty at the actual configuration must satisfy the frozen decision table.

Among eligible candidates:

1. Identify the strongest scientific performance using the predeclared primary
   and critical secondary endpoints. Do not average away a critical failure with
   a large gain on the easy tilt.
2. Select the smaller package on cost grounds only when its simultaneous
   non-inferiority requirements and factor-of-two saving are established. If a
   larger package is materially better, select it when feasible. There is no
   presumption in favor of the small network.
3. If candidates are scientifically equivalent but cost savings are less than
   twofold, report that equivalence and use a predeclared reproducibility/stability
   tie-break, then cost. Do not invent a scientific winner or force the large
   model to win because the savings threshold was missed.
4. If the contrast remains unresolved, spend additional justified compute on the
   discriminating contrast or precision, within the frozen sequential plan or a
   new untouched stage. A wide interval is not equivalence. Stop only at a stated
   information/resource limit, recording what additional evidence would resolve it.

The intended final deliverable is one executable recommended design with measured
limits and a validated uncertainty procedure. If no candidate qualifies, the
decision is "no eligible design" with completed discriminating evidence and a
bounded account of the failure. If several remain inseparable at the measured
limit, state the supported set and the practical default with its tie-break.
Neither outcome may be described as a unique best estimator.

Do not stop after diagnostics or a promising nominal mean while authorized
selection experiments remain feasible. Conversely, do not continue an unbounded
search to manufacture a positive conclusion. Close each alternative with evidence
or a quantified practical limitation, not preference.

## Required delivery and independent review

Preserve a reproducible entry point, frozen estimator and uncertainty configurations,
source/input/event/checkpoint/output manifests, runtime recipe assertions,
predeclared protocols, original per-run scores, resource ledger and recovery
instructions. Maintain required VALIDATION_LEDGER, RUN_LOG and STATUS records in
commits alongside quotable new results. Preserve negative results and corrections.

Commission independent read-only implementation, statistical and scientific-scope
review. Trace claims to original artifacts; agreement sharing the same measurement
origin is not independent validation. Inspect reviewer trees afterward. Correct
material findings before disposition and revalidate affected results.

Deliver a scientific report, updated comparison deck with editable source,
claim-to-evidence index, final decision record and cold-start handoff. The decision
record must specify the complete detector/truth representations, model identities,
checkpoint policy, training recipes, miss rule, normalization, stopping, background
and population scope, uncertainty construction, measured eligibility, cost,
remaining limitations, rejected alternatives and the exact next authorized use.

Push a new study branch and open a draft PR without merging. Verify remote heads
and recovery routes. Do not declare completion on job submission, an unreviewed
plot, a plan for coverage, or unpublished local artifacts. Final reporting must
distinguish study selection from publication adoption and must not imply a tested
background/real-data scope broader than the simulations actually evaluated.
