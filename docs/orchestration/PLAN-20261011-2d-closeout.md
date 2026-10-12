# 2D closeout plan: reproducible estimator, complete uncertainties and supported claims

**Status: proposal for review, 2026-10-11.** Preparation is authorized by Joseph's request to make a
plan. This document authorizes no implementation, compute, estimator adoption, KI-85 lift,
publication change or release. It preserves the original publication objective. It does not
replace an existing campaign contract or restart a terminal campaign.

**Baseline:** canonical `main` `3892e769043cddebfd58ec19e1ab1a567eb01784`, rechecked against
`origin/main` during preparation. Scientific findings below come from committed routed records,
not from this plan. Unmerged branch observations are identified separately in §2.

## 0. Status update, 2026-10-12 (committed by the paper-tighten lane at Joseph's request)

This plan was written on 2026-10-11 against `3892e769` and left untracked. It is committed unchanged below
this section (sha256 of the untracked file `4e98aa13ce03495c…`). Since then, on `main`:

- **Stage A's candidate decision is made.** On 2026-10-11 Joseph adopted the recommended candidate,
  LightGBM seed 42, as the quoted 2D central value. The record is
  [`DECISION-20261011-joseph-2d-central-lightgbm-seed42.md`](../publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md);
  PR #87 and ledger VL173 hold the re-measured comparisons. The adoption covers the *central value only*.
  The quoted uncertainty is still the existing construction, with its limits disclosed (KI 85, 88, 90–94;
  P07).
- **Stage A's reproducibility evidence has landed.** The XR Linux delivery was integrated in PR #91. L0
  regenerates CV42 to 1.4e-11 with a full receipt, and L1 regenerates the seed-1 central to 2.4e-12. The
  exact-split estimator is seed-dependent (X1 vs X0 median 0.18 %; VL174, χ²/ndf 3.565 vs 3.661).
- **Stage A remainder.** The candidate checklist of §4 (205 cell identities, units, POT, target count, flux,
  purity/background inputs, completeness, effective seeds) has not been run item by item; the XR
  reproduction covers it only implicitly. Close it as the first task of execution. The selective-I/O
  delivery (`impl/selective-io-20261010`) has not been received.
- **Stages B–F are untouched.** The next bounded action is unchanged: Stage B's input and recipe
  assessment, with a resource request.
- **Execution authority.** On 2026-10-12 Joseph delegated compute authorization for this plan to the
  paper-tighten lane. The bounds are in
  [`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md).
  Adoption, claim, KI-85 and publication decisions remain Joseph's, as §6 states.

## 1. What completion means

The objective is a publication-ready 2D measurement with one reproducible central estimator,
matched uncertainty construction and validation supporting the claims actually made. Keep the
205 reported cells, their area-weighted integral and 30 projections: **236 functionals**. A claim
about marginal intervals does not establish simultaneous coverage or calibrate a covariance-based
generator test.

The recommended estimator candidate is **LightGBM, seed 42, five iterations**, with the same
ME-FHC selection, weights, normalization and purity treatment as the audited production. Freeze
the driver, helper, library versions, effective thread counts, binning behavior and inputs. The
seed is chosen to match existing systematic products, not because its central value looks better.
Adoption remains Joseph's decision after verification. A change to purity, bin mappers, seed
averaging or interval construction is a new procedure and needs its own declared contract.

There are three separate milestones:

| milestone | required evidence | permissible conclusion |
|---|---|---|
| Engineering complete | guarded production path, provenance, reproducibility, cell identity and supported replay | the central and calculations reproduce |
| Construction complete | every required source is propagated once, on the adopted estimator and population, with correlations and approximation errors accounted for | a matched uncertainty construction exists under its declared assumptions |
| Scientific closeout | independent validation supports interval, bias and covariance claims over the frozen validation domain; publication adoption and all deliverables completed | the stated 2D publication endpoint is achieved |

The first two milestones do not imply the third. "As robust as currently achievable" means the
known construction defects are repaired, material tests have power, and the assumptions and domain
are explicit. It cannot mean protection against every unknown detector or interaction model.
If scientific evidence remains unavailable, the full endpoint stays **NOT ACHIEVED**; a limitation
or a scope decision must not be recorded as a successful coverage test.

## 2. Evidence to inherit and work to avoid duplicating

Read these records before dispatch; remeasure volatile state at execution time:

- [Campaign review](CAMPAIGN-REVIEW-20260929.md): bounded ownership, terminal outcomes and review budgets.
- [Estimator pairing](ASSESSMENT-20261008-2d-estimator-pairing.md), especially §2–§3:
  exact-GBT central; LightGBM statistical seed 1, systematic seed 42, ML seeds 1–10.
- [Component inventory and feasibility](ASSESSMENT-20261008-2d-total-uncertainty-feasibility.md),
  §3 and its `c/components.tsv`: missing sources and dependence terms.
- [Latest integrated 2D follow-up](state/next-preparation-20261009/two-d-followup/REPORT.md),
  A2, A4, A5 and E.2: conditional width agreement is not repeated-sampling coverage;
  new inputs are necessary for the original objective.
- [XR recovery](state/next-preparation-20261009/xr-recovery/REPORT.md) and
  [integration](state/next-preparation-20261009/xr-sb1-integration/REPORT.md): failed attempts and
  ownership of the successor reproducibility and selective-I/O work.
- [2D reference](../../2d-unfolding/2D_OMNIFOLD_REFERENCE.md),
  [status](../../2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md),
  [known issues](../../KNOWN_ISSUES.md), and each result's original receipt and ledger entry.

**Unmerged observations, not a new scheduler measurement or final verification:** after fetching
refs during preparation, `run/xr-linux-20261010` is at
`9be8bfb4d4acace2ec64273970130d6404f1813c`. Its committed interim report records a passing Linux
preflight and completed L0/L1 runs; the exact arms are unfinished in that record and final
independent verification is not supplied. `impl/selective-io-20261010` is at
`9dfd8d6eae5a1f4a52b32f5032348744cb012c47`, with a locally reviewed opt-in implementation.
Recover each report with `git show <full-sha>:docs/orchestration/state/next-preparation-20261009/<lane>/REPORT.md`.
Receive and verify these lanes' final deliveries rather than repeating them or editing their
packages. Do not infer their current scheduler state from this snapshot.

Retain completed central-value, closure, completeness and iteration studies as evidence. Check
their applicability to the frozen LightGBM candidate; add a targeted test only when an estimator,
input or uncertainty change breaks that applicability. Do not rerun the entire historical campaign.
PET and the terminal scalar campaigns remain outside this plan.

## 3. Issue-to-evidence map

All criteria below are proposed requirements; numerical tolerances must be reviewed and frozen
before the relevant new production. Existing contracts keep their original criteria.

| issue | remedy | evidence required to close it |
|---|---|---|
| Backend mismatch, KI-88 | adopt the verified seed-42 LightGBM candidate and build its uncertainties | estimator and input manifest for each block; central adoption record; comparisons recomputed |
| Seed-1 statistics versus seed-42 systematics, P07 | build statistical replicas at seed 42 | every effective fit seed recorded; no transfer of the old band assumed |
| Reproducibility and OI-136 | inherit the XR Linux delivery; keep verified module loading and effective thread checks | complete receipts, passing reference comparisons and independent recomputation; no guard widening |
| Latent cell misalignment, KI-90 | finish the two publication consumers' identity checks | same-sized, different-cell negative control refuses; adopted outputs remain equivalent |
| Flux ordering, KI-91 | trace the common PPFX index through event weights and flux integral production | committed code-path identity proof with numeric cross-check; correlation alone is insufficient |
| Duplicate GENIE shift, KI-92 | count Rvn1pi/Rvp1pi once under the adopted nuisance definition | exact weight identity; band inventory; independently rebuilt covariance difference |
| May truth-input mismatch, KI-93 | retire the May sweep from the new construction; qualify July products or rebuild affected universes | universe/CV deterministic-input equality; no-op universes reproduce their own CV within a frozen envelope |
| Frozen background-model variations, P06/C06 | use verified background-aware universe propagation | saved varied background and measured-training inputs agree with the declared nuisance recipe |
| Missing background statistics, KI-94/C03 | propagate a background-template sampling stream through purity and unfolding, or demonstrate an adequate unfolded bound | output-level contribution for every functional; data, signal and background dependence accounted for |
| Selection-limited lateral bands, C05a | qualify active-universe inputs for 2D or produce selection-complete inputs | cut-by-cut CV equivalence, entering/leaving event census and finite-support closure |
| Flux–muon-energy correlation, X01 | establish a joint nuisance treatment from the applicable constraint | joint source provenance; cross term counted once; resulting covariance is valid; transferred paper correlation is not independent evidence |
| Training variability and overlap, C08/X02/X03 | measure resampling × seed and nuisance × seed effects on a bounded development panel | variance decomposition and uncertainty of interaction estimates; no automatic independent addition or noise subtraction |
| Statistical calibration, KI-85/P17 | independent-production test or validated generative route at the final procedure's operating point | coverage/width evidence for the claimed sampling law; old VL169 results do not grade the new band |
| Model and response sensitivity, C09/C10 | untouched validation truths and response departures; freeze a scoped bias treatment on development samples | successful held-out assessment over the declared domain; extrapolation assumptions remain explicit |
| Total intervals and covariance use | validate the complete frozen procedure and each proposed test statistic | marginal coverage by functional; separate simultaneous/test calibration if claimed; rank and finite-ensemble effects reported |
| Publication and recovery | rebuild all comparisons and deliverables from the adopted products | claims-to-evidence map, ledger/RUN_LOG/STATUS, supported clean replay, three builds and standalone sync |

The old statistical replicas and ML scan remain development/reference evidence. Reuse of a
numerically verified covariance is conditional on the new procedure, its sampling target and
the overlap analysis. Reusing all existing matrices unchanged is not the default.

## 4. Execution sequence and stopping rules

### Stage A — finish reproducibility and freeze the candidate

Receive the final XR Linux and selective-I/O deliveries. Verify their commits, receipts, reviews
and current ownership; integrate through their existing owners. Preserve frozen historical packages
and evaluate their consistency at their own commits. Do not change XR's pinned driver while it runs.

The LightGBM central decision need not wait for XR's slower exact-backend arms. A separately
verified L0 delivery can supply the candidate while the other arms continue under their own
contract. Receive it through the existing owner and the applicable review scope; no duplicate
central run is needed merely because XR is unfinished. The final whole-campaign delivery remains
necessary for closing XR itself, not for establishing the LightGBM candidate's reproducibility.

For the candidate central, verify the 205 cell identities, units, POT, target count, flux,
purity/background inputs, completeness and effective seeds. The existing XR comparator uses
`1e-8` maximum relative tolerance; preserve it for that task. If the final producer differs from
XR's producer, a small equivalence check must bridge them before a large ensemble starts.

**Exit:** one reproducible candidate with a complete manifest and independent comparison.
**Stop:** reproduction failure, unexplained input drift or an unavailable required receipt. Diagnose
the cause before any replacement ensemble; do not loosen the tolerance after seeing a failure.
Exact-backend reproduction is historical continuity evidence, not a prerequisite to accepting a
verified LightGBM candidate and not an instruction to restart completed exact runs.

### Stage B — resolve inputs and define the complete uncertainty recipe

Perform the saved-product and code-path reads first: flux identity, duplicate band, July/CV truth
inputs, background variations and selection-complete lateral eligibility. Write one source table
covering C01–C10 and X01–X03, updated with KI-92–94. Each row names its input, sampling or nuisance
law, conditioning, propagation, correlation partners, and source of independent evidence.

Use July products only after those checks establish the required pairing. The May sweep is not
the fallback for a claim of complete matched uncertainties. If selection-complete inputs cannot
be recovered, name the necessary event-loop production and its resource estimate.

Define background propagation explicitly: fluctuating the template must change its derived purity
and training weights as the final recipe specifies. Preserve shared truth/reco draws for the same
signal event. Establish whether background and signal-fake rows share events or simulation
dependencies; do not invent independent streams for correlated objects. The treatment of data's
appearance in the purity denominator must be part of the estimator contract.

For flux–muon-energy dependence, first check whether the flux actually used inherits the relevant
low-recoil constraint. Obtain the applicable joint constraint or a justified derived construction.
Do not insert a paper-derived correlation into a different flux model by default.

Specify the role of `C_ML`: fixed-seed reproducibility, seed arbitrariness and sampling variability
are different objects. A factorial development panel tests their interaction with statistical
resampling and small nuisance shifts. Paired seeds are controls, not evidence of independence.
An estimator change to stabilize bin mappers is a separate option if needed; it resets matching
and validation, rather than silently improving the candidate after assessment.

**Exit:** no unassigned or omitted material source; feasible inputs and a reviewed final recipe.
**Stop:** missing selection support, joint-law evidence or required populations. Record the specific
missing input and acquisition route; disclosure alone does not close a missing-source defect.

### Stage C — pilot, then construct the matched products

After admitting the final recipe, run a small representative pilot that covers the central,
statistical streams, a no-op universe and selection-changing/large-flux cases. Check the whole
guarded Linux path, including fits and predictions, and record measured charged time and memory.
Freeze a production budget with at least 20% reserved for verification and failures before scale-up.

Build the seed-42 statistical ensemble; **300 replicas is the initial planning size**, not a proof
of covariance accuracy. Background propagation is included according to Stage B. Qualify/reuse
eligible July systematic products, replacing defective or unmatched bands and selection-limited
laterals. Deduplicate the GENIE shift and include the adopted cross-source treatment. Add the
1.4% target normalization once, scaled to the final central.

Recompute matrices independently from replica/universe vectors. Report centering conventions,
cell identities, numerical symmetry/PSD, rank, and ensemble error in widths and in the modes used
for inference. Check the integral and projections directly from vectors. Assess covariance
convergence with uncertainty estimates; nested subset agreement is descriptive and is not an
infinite-ensemble guarantee. Freeze any truncation, shrinkage or test-statistic convention before
final assessment. An inability to resolve a proposed tolerance is **NO POWER**, not PASS.

**Exit:** a complete, numerically verified construction for the frozen candidate.
**Stop:** failed identity, propagation, completeness, PSD or precision requirement. At most one
bounded diagnostic/repair batch under the admitted budget; substantive changes need a new recipe.
Do not promote construction success to coverage success.

### Stage D — acquire independent evidence and design affordable validation

This is a necessary dependency, not an optional finishing test. Stage B may investigate input
availability while Stage A completes; expensive production waits for the recipe to be frozen.

The integrated follow-up, A5/E.2, establishes **no feasible route to the full objective with current
inputs**. A reopening must obtain:

1. Fresh, identity-carrying MC banks or a generative law independently validated for the claimed
   quantities. Fresh productions change row samples and LightGBM bin mappers; retained-row
   bootstraps and complementary half-splits do not probe that variability. Declare the MC
   production law and reference-truth error. Include a calibration bank if the procedure uses one.
2. A validated continuous nuisance generator, including selection changes, varied backgrounds,
   coherent flux normalization and the applicable dependence structure. Drawing pseudo-data from
   the same universe law cannot establish the physical adequacy of that law.
3. Untouched truth/response departures, including independent-generator evidence or an explicitly
   limited alternative. A projection of an already inspected 5D generator sample is not a fresh
   validation domain. Match target, phase space and flux, and address independent-generator
   predictions' finite-sample error. Truth warps under one response are partial evidence only.

Obtain availability and prices before commissioning these inputs. Reserve assessment populations
with an independent custodian. Freeze development and assessment roles, identities, exposure,
sample sizes, criteria, multiplicity treatment and power. Test the final full-size procedure;
if a reduced-size proxy is proposed, independently establish the scaling rather than assuming it.
Lift KI-85 explicitly only for the named authorized test.

Choose a validation strategy with a measured affordable interval cost. The existing fully nested
bootstrap-plus-universe design is a NO-GO at its forecast cost. Candidate cheaper propagation or
linearized interval procedures need independent equivalence/error evidence and their own validation;
they are method development, not discounts automatically applied to the old estimate. A fixed-band
test answers a narrower question than validation of data-dependent interval reconstruction.

**Exit:** new inputs exist, the final procedure is frozen, and a costed powered design is reviewed.
**Stop:** unavailable populations, an unvalidated forward generator, no untouched domain or an
unaffordable interval procedure. Report **full scientific closeout NOT ACHIEVED**. Conditional
width diagnostics may be useful separately, but do not substitute for the missing evidence.

### Stage E — perform the final independent assessment

On untouched populations, assess bias, widths and nominal I68/I95 coverage for every claimed
functional and departure case. Reconstruct each experiment's own intervals when that is the
publication procedure. Carry reference-truth uncertainty and non-Gaussian effects in the design.
Proposed tolerances must be scientifically motivated and tested for false-fail probability and
power before they are frozen; earlier design windows and sample counts are not inherited unchanged.

Distinguish data-only, finite-MC, background, total and model-dependent claims. Test integral and
projection uncertainties as correlated sums. If simultaneous intervals or covariance-based
generator p-values are claimed, validate those objects separately, including rank, estimated
covariance effects and shared uncertainties with the reference analysis. The paper-plus-ours
covariance sum does not become an independent goodness-of-fit claim.

For bias, define the allowance or correction on development data, then assess it on the untouched
domain. Keep an empirical development envelope distinct from a guaranteed bound. No finite test
set establishes correctness outside its declared physical and detector domain.

**Exit:** independent recomputation and scientific review agree that the frozen claims are supported.
**Stop:** material failure, insufficient power or a missing domain. Assessment samples are consumed
by inspection. A redesign needs fresh assessment samples and a new grant; it cannot be tuned until
the same sample passes.

### Stage F — adopt, publish the evidence and verify recovery

Joseph makes the central/uncertainty/claim adoption decision on the reviewed products. Rebuild totals,
ratios, budgets, comparisons, all affected figures, and the article claims map using one central
denominator and the adopted covariances. Record the exact completed evidence in the validation ledger,
2D RUN_LOG, STATUS and reference; close KI-88/90–94 only to the extent their required evidence landed.
Record KI-85's actual outcome and any surviving physical-domain assumption.

Build note, primer and paper with `build_all.sh`. Synchronize the corresponding sources to the
standalone Analysis-Note repository, build there, commit and push both source deliveries under their
authorization, and record both remote heads. Provide clean-checkout replay at the supported tiers,
durable input/output hashes and recovery routes. Obtain one independent final claims-to-evidence
review. Submission, deposit, tagging and coauthor contact remain separately authorized acts.

**Exit:** no unresolved blocker to the specific adopted publication claims, complete reproducibility
and synchronized deliverables. If Stage D/E is incomplete, the package must say so and cannot be
called full scientific closeout.

## 5. Ownership, review and resource limits

**Proposed execution setup:** one scientific construction owner, one fresh independent numerical/
statistical reviewer and Joseph as adopter. Choose a capable scientific implementation model and
a reviewer suited to consequential statistical claims from the available models at dispatch,
informed by the campaign review. Distinct model names do not establish independent evidence.
The reviewer uses an isolated read-only worktree and separate recomputation; the writer alone repairs.
The plan was prepared by one session without delegated review. No reviewer or compute lane is
dispatched by this document.

For each stage, allow one initial review and at most two focused repair/re-review cycles. Stop and
reassess a strategy that cannot resolve a material finding within that budget. Minor documentation
changes do not start another campaign. Before a run, bind its quantity, input/product digests,
ceilings, stop time, attempt count and terminal outcomes in the existing stage record. No terminal
result authorizes the next stage, adoption or a scope change automatically.

| work | current planning basis | resource status |
|---|---|---|
| Existing XR work | inherit its own grant, accounting and terminal delivery | no duplicate grant or runs proposed here |
| Central unfold | historical LightGBM timing 13m24s; saved candidates exist | small component; queue, review and integration are additional |
| Seed-42 statistical matching | prior L42 forecast 25.5–93.2 charged CPU node-h for 300 replicas | forecast, not a grant; excludes new background recipe and other repairs; reprice from the pilot |
| Construction repairs | prior feasibility setup 79–469 node-h before its 20% reserve | historical forecast only; scope changes and selective I/O require a new estimate; do not add blindly to matching |
| Original total-coverage reconstruction | prior P1 forecast 0.29–1.21 million admitted node-h | NO-GO; inputs also missing; cannot be sold as one unfold per experiment |
| Earlier L42 split-sample program | 303–1,131 admitted node-h | supports a different, conditional claim; not a price for full closeout and not recommended as a coverage substitute |
| New independent inputs and an affordable full-validation method | availability, production and method cost not established | unpriced; the main critical path |

Sources: 2D STATUS runtime table; two-d-path REPORT §9; total-uncertainty feasibility §2, §6 and §8;
two-d-followup A5/E.2. Counts and prices belong to those designs, not to a newly admitted campaign.
SB1 measured one lateral-pair I/O improvement; it does not price the whole sweep or validation.

**Planning calendar, estimates rather than commitments:** Stage A integration/manifest work about
0.5–1 working day after its deliveries; Stage B input audit and recipe about 2–3 days; Stage C
implementation, pilot and construction review about 3–5 days plus approved queue/compute time;
Stage F about 1–2 days after scientific adoption. These are active-work estimates, not serial
elapsed guarantees. Roughly one to two working weeks is a plausible construction effort if inputs
can be reused and the recipe is stable. **There is no defensible completion date for Stages D/E**
until independent inputs, the affordable interval method and the powered design are obtained.

## 6. Decisions required to turn this proposal into execution

The next bounded action is to receive the existing reproducibility delivery and prepare Stage B's
input/recipe assessment with a resource request. Before scientific production, Joseph must decide
on the LightGBM candidate, the repaired uncertainty recipe, exact claims and stage budgets. The
KI-85 deferral, estimator/uncertainty adoption and any new independent production require their
named decisions. The current request is for a plan and does not lift those holds.

Maintain the full objective as the default. If new independent evidence is unavailable, present
Joseph with the concrete missing inputs and two explicit outcomes: keep the full endpoint open
while acquiring them, or separately adopt narrower conditional/convention claims. The latter is a
different publication endpoint. It is not "all issues closed" and is not assumed by this plan.
