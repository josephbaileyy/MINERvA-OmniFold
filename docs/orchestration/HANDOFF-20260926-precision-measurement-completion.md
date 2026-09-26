# Scalar precision measurement: completion handoff

## Purpose and activation

MINERvA-OmniFold develops multidimensional neutrino cross sections with unbinned
GBDT unfolding. The objective is a useful, reproducible measurement with justified
total uncertainties and a calibrated joint-5D generator comparison at a declared
resolution. Neither zero bias nor significant generator disagreement is required.
An estimator being the best tested does not establish uncertainty validity.

This is a draft successor specification, not an executed authorization. The owner
activates it by sending GOAL-20260926-precision-measurement-completion.txt. Record
the actual approval, date, approved document blobs and commits before implementation.
The attachments are initially uncommitted. Preserve their approved versions; put
delegated choices in a separate frozen contract and progress in structured state.

The campaign must attempt all seven stages below that remain scientifically and
financially feasible. A failed branch does not stop independent authorized work.
An honest terminal report completes the bounded campaign even if the scientific
objective remains unmet. Never equate those two statuses.

## Durable baseline and evidence routes

Verified remote heads when this handoff was prepared:
- Main: b30752864c70c76da3a888136e52c3dea4b615b7.
- Standalone analysis note: b1410fc32d1269ad9ea44a4f9f042312bb8276a8.

Refresh both. The shared local main can lag; use an isolated worktree from verified
origin/main. Do not pull over other sessions' untracked plans or alter their jobs.

Read AGENTS.md, routed CURRENT_WORK/OPEN_ITEMS and PLAYBOOK, then the following
paths under docs/orchestration, following their exact receipt links:
- OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md and
  DIAGNOSIS-20260926-s5e-oi192-estimator.md.
- CAMPAIGN-s5e-20260925-index.md; state/s5e/contract.json and its amendments;
  state/s5e/cand/review-round-2.md; state/s5e/cand/next_design.json.
- OUTCOME-20260925-s5n-stage1-development-fail.md and
  OUTCOME-20260925-s5c-tier-s-futility-fail.md.
- AUTHORIZATION-20260924-scalar5d-campaign-activation.md,
  AUTHORIZATION-20260925-negweight-refined-successor.md and
  AUTHORIZATION-20260925-oi192-estimator-diagnosis.md.
- PLAN-scalar5d-reportable-uncertainties-and-inference.md, approved historical
  blob 8b0617b6e044a55a9b5870b46e5d90a15a6ced7a. Keep it unchanged.
- HANDOFF-20260924-preparation-for-scalar5d-campaign.md, its recovery manifest,
  and RECEIPT-20260925-d3-hpss-backup-of-nine-sole-copy-objects.md.

Also read OI-193, VALIDATION_LEDGER VL146-VL154, KNOWN_ISSUES 75-80, current
workstream references, and the analysis-note build/release instructions. Reuse
completed preservation and valid evidence. Do not repeat a general audit campaign.

## Established findings and their limits

The historical standard scalar measurement uses purity subtraction. The s5n and
s5e candidate studies actually use negweight-refined. Candidate R increases only
the Stay-Positive refinement classifier to 400 trees and 31 leaves. It passed
nominal background-inclusive closure on fresh development-scale experiments.
That repair is measured, not adopted; historical central values remain unchanged.

Physical truth departures still produce sizable unfolding residuals on both
driver and NPZ paths. No unique mechanism or optimality limit was established.
The E_avail residual decreases slowly through 30 iterations while the q3 case
worsens. Matching most detector-level variation does not prove truth-level
identifiability or that the remaining detector-level discrepancy is negligible.

R fails the historical A3 numerical-stability screen: edge-safe rounding-scale
perturbations move data functionals by median 0.78 and maximum 2.58 data-bootstrap
sigma. Whether refitting in the bootstrap already absorbs this variation is
unknown. Arbitrary jitter is not automatically a probability model or a covariance.

Aggregate nominal calibration passed, but six functionals were miscalibrated.
The 20-of-42 reporting-cell screen depends on the chosen deformation set; it is
not a validated reduced fiducial measurement. The old 5% projected-sigma movement
statistic was not computed in s5e. No new uncertainty product qualified.

The historical adoption remains byte-specific with all required measurements and
later documented limitations. Do not infer validity of a successor from it.
The 2D standalone result remains its own validated result. PET stays diagnostic.

## Standing execution boundaries after activation

The goal delegates OI-193's listed work and all seven completion stages. Record
the exact scoped supersessions: earlier diagnosis-only limits, exclusions of
model-uncertainty construction, prohibitions on full coverage/inference production,
spent family/revision limits, and reserved adoption acts for qualifying scalar
successors. They remain intact for historical campaigns and other workstreams.

This successor may define new qualification criteria for the COMPLETE measurement,
including treatment of residual bias and numerical sensitivity. It need not force
physical-model residuals inside a statistical-only interval. Criteria must follow
the intended use and a stated probabilistic or bounded-nuisance interpretation;
independent review precedes fresh validation. No historical FAIL becomes PASS.
List changes from the old 5%/A3, coverage, width and p-precision rules explicitly,
including their retrospective motivation. Do not call a choice uninformed by data
when existing results motivated it. Never tune it on the new validation results.

Preserve applicable normalization, event identity, import-root, mask/order,
physical-nuisance, overwrite, receipt and reproduction protections. No bypass of
protected guards, unsupported provenance claims, or silent adoption exceptions.

Resources are cumulative, not reset. Retain the combined ceiling of 345.27 billed
CPU node-hours and 500 A100-equivalent GPU-hours across s5c, s5n, s5e and this work.
Reconcile all actual charges and outstanding reservations. At the s5e closeout,
CPU expenditure was 35.086 node-hours; GPU expenditure from s5c/s5n was 40.38
A100-hours. These are dated measurements, not permission to spend an assumed balance.
Each new pool is additionally capped at 10% of current uncommitted allocation
after existing reservations. No transfers, purchases or automatic budget reset.

Retain 20% of each new pool for verification/repairs, at most two CPU nodes and
four GPUs concurrently, and applicable previous storage/retry limits. Re-measure
quota. Carry forward campaign-specific replacement of R5 task-hour/calendar limits
through explicit admission mapping; do not disable other campaigns' meters.
Cost pilots, failed runs, all replicas and independent compute verification.
Reconcile after each allocation. Preserve other users' allocations and jobs.

## Stage 1: define the useful measurement

Write a short physics-use case and numerical precision targets before candidate
selection: what cross sections and joint dependence must a user distinguish?
Set targets for total uncertainty, bias control, numerical stability, useful
interval width, coverage and joint-test power. Justify them scientifically, not
by making existing results pass. Do not require an observed rejection.

Identify the intended generator comparisons, null hypotheses, nuisance domains
and physically meaningful power alternatives for the candidate reporting scopes.
The alternatives must probe joint structure beyond the EW marginal. Develop this
inference design alongside the measurement and freeze it with the total-uncertainty
model in Stage 3; Stage 7 executes and verifies that design.

Inspect efficiency, migration, resolution, background fraction and effective
sample size over the existing domain. Distinguish physical detector volume,
kinematic fiducial definition, reporting region and reporting binning.

Consider at most three physically motivated reporting definitions, including the
baseline. Prefer contiguous regions and coarser resolution over a list of cells
selected from favorable residuals. Keep a broader unfolding domain when needed
for boundary migrations. Any narrower fiducial definition changes the estimand;
recompute selection, normalization, affected systematics and generator predictions.
Geometrical volume changes need direct evidence and a costed input-production path.

Retain subdivisions in all five coordinates where physical support permits to
qualify joint-5D. Lower-dimensional fallback may qualify separately but cannot
fulfill the larger joint objective. Freeze a reporting-selection procedure using
development data, then lock the selected scope before independent assessment.
Record any real-data-informed choices and treat selection in later inference.

Exit: a frozen useful-precision specification, candidate scope hierarchy and
initial joint-inference design.

## Stage 2: resolve the construction questions

Start with R's negweight-refined background treatment. Verify actual execution
and metadata, not just launcher flags. Reuse its nominal-closure evidence.

Measure numerical sensitivity and its overlap with the bootstrap using matched
resampling/perturbation controls. Keep physical statistical fluctuations separate
from coordinate representation and algorithmic effects. Preserve grid membership
in rounding diagnostics. A covariance sum needs justified independence or measured
cross terms; a numerical spread needs a defensible interpretation before adoption.

Address the six known s5e per-functional calibration failures explicitly. Trace
them from the assessment receipt and independent review to the proposed reporting
quantities, including any changed binning. Investigate bias and interval scale
separately, and check the proposed interval construction on development experiments.
Distinguish checks of statistical components from checks of total intervals.
Record how the failures are addressed or remain unresolved before costly fresh
validation. Resolving numerical sensitivity alone does not discharge them, and a
pooled pass cannot do so. These checks inform development, not final qualification.

Run a fixed convergence study, potentially through 200 iterations, on E_avail
and q3 alternatives with detector-level checks. Measure both improvement and
deterioration. Test whether relevant truth alternatives remain distinguishable
after detector response and at the actual exposure. Do not assert optimality
from a finite unsuccessful scan.

Choose at most three estimator configurations, including R, with at most two
development revisions each. Permit supported changes to stopping, capacity,
regularization, missed-event regression, refinement and resampling. No broad
architecture search. Freeze and cost choices before execution; failed independent
validation may inform a permitted revision only with wholly fresh validation.

Use no more than 15% of each new resource pool on stages 1-2. An explicit exit
milestone is at least one scientifically justified validation method with a
provisional sample-size, assurance and complete remaining-work cost calculation
that fits the reconciled budget. Include required verification and repair reserves;
separate measurement costs from joint inference. Historical validation forecasts
do not establish successor feasibility. Update this calculation and independently
review it at the Stage-3 production-admission gate. If no useful affordable design
is supported, finish independent work and record the limitation.

Exit: a selected estimator, development calibration results, an explicit map of
unresolved uncertainty sources and a provisionally affordable validation path.

## Stage 3: define residual model dependence and admit production

Use physically supported alternative truths to measure residual bias and its
correlations in the selected reporting quantities. Include cross-coordinate
deformations; one-dimensional generator ratios are not complete joint coverage.
Verify all positivity, support, normalization and marginal-preservation claims.

Separate alternatives used for development/construction from withheld validation.
Define whether each source is probabilistic, a profiled nuisance or a deterministic
bounded alternative. Generator choices are not independent random universes by
default. An outer product of a closure residual is not automatically a valid
covariance. A correction must be part of the data estimator and tested for transfer.

Select a justified correction, model component or explicitly limited envelope.
Preserve correlated directions and physical assumptions. Quantify usefulness of
the resulting precision. Do not manufacture a statistical label for a model band.

Complete the joint-inference design alongside this model. Freeze generator nulls,
nuisance domains, test statistics and physically meaningful power alternatives
outside the null families. Distinguish nuisance-averaged from uniform composite-null
calibration and total-rate from shape-only tests. Specify shared-input correlations,
data-informed selection, multiplicity and separate development, calibration and
validation operands. Check whether the proposed uncertainty treatment preserves
the joint sensitivity required by Stage 1.

Carry each uncertainty source's interpretation through the reported intervals and
the joint test. A deterministic bounded envelope must enter through a declared
bounded-nuisance procedure; a profiled nuisance must retain its declared treatment.
Neither becomes a random covariance term without a justified probability model.
Specify how these terms combine with probabilistic components and how the combined
procedure will be calibrated.

Freeze test and p-value precision appropriate to the physics-use case before new
observed tests. The old +/-0.005 rule for p >= 0.05 is not immutable for this
successor. Defend any replacement independently of the desired observed result.
Account for earlier data-driven selection/localization; a later freeze does not
make the analysis blind.

Before any Stage-4 production, obtain independent scientific review and freeze
a production-admission record containing:

- the reporting scope, estimator, total-uncertainty/interval construction and
  exact scientific claims, including truth/nuisance domain and conditioning;
- development evidence addressing the known per-functional calibration failures,
  useful width and expected joint sensitivity, with unresolved findings explicit;
- a concrete validation method with sample sizes, assurance, Monte Carlo precision,
  per-functional and joint criteria, multiplicity control, and frozen stopping,
  futility, stability and width/usefulness rules;
- the joint-inference design and its calibration and power requirements;
- the reconciled cost of all remaining construction, validation, verification,
  repair, inference and delivery work, with protected reserves. Separate required
  measurement resources from feasible or infeasible inference resources.

Do not admit a construction whose required validation cannot fit. An infeasible
joint test permits an otherwise qualified measurement checkpoint, with the joint
objective explicitly unmet and a priced next increment. Failed admission stops
the affected production branch; complete independent authorized work.

Exit: independently reviewed, frozen measurement and inference contracts and an
explicit production-admission disposition.

## Stage 4: construct matched products

Enter only under the Stage-3 production admission. Build nominal, statistical,
background, detector, flux, model and algorithmic components on one declared
estimator/background footing and with their frozen interpretations. Recompute
Stay-Positive refinement inside each applicable resampling/nuisance variation.
Distinguish observed-mixture fluctuations from finite background-template MC and
physical nuisance uncertainty, preserving correlations and avoiding double counts.

Use fresh output namespaces and common row maps, support, units, bin volumes,
normalization, seed policy and projection operators. Preserve selection-complete
lateral treatment and all five formerly seed-pinned bands. Validate actual
production imports, mode propagation and metadata at readback. Frozen-map reuse
needs a scope-specific justification; do not splice purity covariance blocks
onto a negative-weight central result merely because their dimensions agree.

Run relevant central/marginal regressions without reopening completed studies
unrelated to the changed estimator. A projection of a new 5D central is a new
product; do not pair its covariance with an old independently unfolded central
without establishing that pairing.

Exit: a reproducible matched candidate, not yet adopted.

## Stage 5: validate what will be reported

Execute the validation design independently reviewed and frozen at Stage 3.

Validate the exact estimator and interval construction applied to real data,
using background-inclusive event-level pseudo-experiments, fresh seeds and
withheld physical alternatives. Include finite-MC effects for unconditional claims;
otherwise name the conditioning. Evaluate per-functional and relevant joint
behavior. Pooled calibration cannot certify an individually failing functional.

Apply the frozen sample sizes, Monte Carlo precision, multiplicity control and
assurance design. The Stage-3 review may approve replacement of the historical
all-functional binomial certification or statistical-only gate when the coverage
claim and error control are justified before fresh assessment. Publish achieved
bounds and limitations. A finite grid is not uniform coverage over every model.
Exact finite-sample guarantees require verified assumptions, including nuisance
and selection handling. A final-covariance Gaussian toy does not validate unfolding.

Use the frozen fixed sample counts or justified sequential procedure and futility
rules. Apply the frozen width/usefulness conditions as well as coverage so
arbitrarily wide bands cannot qualify as a precision result. If validation fails,
use only permitted revisions with fresh validation or stop the affected branch.
Any permitted revision affecting the frozen construction or validation design
must return through Stage-3 review before new production or fresh assessment.

Exit: independently supported measurement scope or a documented terminal failure.

## Stage 6: conditional adoption and publication scope

Delegated adoption requires identified immutable product bytes, independently
reproduced construction, passed applicable validation and precision criteria,
complete required physical uncertainty scope, correct pairing, and no unresolved
result-changing defect. Obtain an independent scientific review of these operands
and claims. Record adoption as delegated under the actual activation, not as the
owner personally inspecting future bytes. No new exception is authorized.

Adopt only the qualified scope. Statistical qualification does not adopt total
covariance; nominal closure does not establish departure coverage. New scalar
projections may qualify under these same conditions. Preserve prior adopted bytes
and identify exactly what is superseded. Update every dependent claim consistently.

A reduced joint-5D domain may satisfy the objective if its declared precision and
joint sensitivity meet the frozen physics-use case. A projection-only product is
a valid partial deliverable, not joint-5D completion. If a removed region supported
a headline physics claim, remove or explicitly demote that claim in all deliverables.

Exit: exact adopted products/scopes or an explicit non-adoption disposition.

## Stage 7: joint inference, reproduction and release preparation

Execute and independently verify the joint-inference design frozen at Stage 3.
Construct missing generator predictions on the actual joint reporting domain and
flux; record input identities, finite-MC uncertainties and any tuning dependence.
Construct the declared residual covariance for probabilistic terms, including
shared inputs, and apply profiled or bounded contributions as contracted. Do not
assume independent errors or infer degrees of freedom from a pseudoinverse cutoff.

Use the separate development, calibration and validation operands specified in
the contract. Independently verify test size, numerical precision, seed/numerical
stability and required joint power. Apply the frozen precision tier and report
Monte Carlo bounds when exact numerical precision is unavailable. Never report
zero p or extrapolate an unvalidated tail. Non-rejection can qualify; low power
is not evidence for generator agreement.

Proceed through feasible inference after measurement qualification without another
routine approval. If it cannot fit, preserve the measurement checkpoint and report
the joint objective unmet with a priced next increment; do not consume protected
measurement-validation resources first. Public submission remains separate.

Finish the existing paper-wide completion table. Package reported central values,
uncertainties, maps, units, hypotheses, calibration operands, licenses/restrictions,
checksums and executable reproduction examples. Test the advertised reproduction
scope from a fresh checkout without private paths. Distinguish replay of stored
statistics from full regeneration. Complete in-scope blockers; retain explicit
out-of-scope or external dependencies rather than inventing evidence.

Build note, primer and paper in both repositories, including the Overleaf-style
paper target, inspect figures/references, synchronize sources/assets, commit and
push without overwriting others' work, and verify actual remote heads. Prepare
the release manifest. No external messages, public deposit, final publication
tag or journal/arXiv submission is included.

## Continuity, review and finish

Use one campaign index and structured state with exact contract/input/output
identities, job ownership, reservations/spend, review status and next action.
Register work through source tables. On resumption observe the scheduler before
submitting; neither a context reset nor silence authorizes duplicate jobs.

Independent reviewers use isolated read-only worktrees and their own operand
checks; inspect their status afterward. Review changed scope, not the entire
repository. Allow at most two targeted repair/reverification cycles per frozen
stage or candidate; an unresolved material finding blocks its qualification.
Preserve independent negative results and record honest non-adoption if needed.

Final fields: campaign_disposition, reportable_uncertainty_scope,
joint_5d_inference_status, publication_readiness. Include exact failed/met gates,
adopted/superseded digests, precision/domain limits, paper-wide table, reproducibility,
spend, remote heads and costed remaining requirements. READY needs all retained
claims and the required joint result; bounded campaign completion alone does not.

No repeat preservation or generic cleanup. No PET reopening. No unsupported
upgrade of the 20-cell screen, model residuals, rounding probes or historical
exceptions into coverage. Return for decisions only outside the explicit scope;
complete independent authorized work before reporting a terminal dependency.
