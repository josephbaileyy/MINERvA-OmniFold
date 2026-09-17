# Scalar-5D covariance and downstream-inference audit — 2026-09-18

## Conclusion and scope

The next decisive work is to complete the scientific acceptance contract and the
independent evidence for the scalar-5D trunk. The completed Z pilot is construction
evidence, not an adopted uncertainty. Exact projections, calibrated inference,
and a supported reproduction path remain separate obligations.

This ranking preserves both halves of [OI-187's ruling](../orchestration/DECISION-20260901-joseph-oi187-upgrade-not-blocker.md):
the covariance enables a significance upgrade beyond the Letter's central-value
scope, **and the intention remains to finish uncertainties before publication**.
This audit neither authorizes submission nor makes that intention optional.

The audit is read-only except for this report, on isolated branch
`audit/scalar-5d-publication-gaps`, based on main
`07ccc4f0671945eeb6516d52ddc4e414129d7b45`. Analysis code, scientific products,
receipts, ledgers, OI dispositions, and manuscript sources are unchanged. No
scientific compute, projection, inversion, training, cluster submission, or
scheduler action was performed. Recommendations below are proposed next actions,
not new authorizations or grades.

[AGENTS.md](../../AGENTS.md), [CURRENT_WORK](../CURRENT_WORK.md), the relevant
[OI records](../OPEN_ITEMS.md), and the
[September 17 literature review](2026-09-17-review-and-incorporation.md) were
read. CURRENT_WORK supplies routing, not evidence that its next-action prose is
still scientifically sufficient. OI-93 concerns PET; **OI-137 is the scalar-5D
finite-ensemble route**. OI-126 is settled: PET remains diagnostic/method-development,
its central/statistical pairing is declined, and no PET total covariance is
adopted. Neither its completed investigations nor Gate 6 is reopened here.

## Evidence boundary and versioned sources

Local source inspection and committed JSON readback establish what the code and
records say. They do not independently verify cluster-resident ROOT/NPZ payloads.
No current scheduler, quota, remote-head, or artifact-availability assertion is
made. The Perlmutter freshness/scheduler procedure was not run because this audit
neither monitors nor launches jobs; any future execution must perform it afresh.

The [Z navigation record](../orchestration/NAVIGATION-20260917-z-pilot-outcome-route.md)
was followed to these actual committed blobs, not treated as evidence itself:

| Reference used below | Exact evidence read | What it establishes here |
|---|---|---|
| Z specification | [SPEC](../orchestration/SPEC-20260906-complete-scalar5d-successor-Z.md), rev. 22 at the audit base | Construction, per-cause requirements, falsifiers, and outstanding decisions; older completion language is read with its later corrections. |
| Z outcome | `1b2873a8e9b3c78568725494799a3df6234a39d5:nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`, September 17 entry | Producer's committed account of the completed pilot, including exact receipt fields. Heavy products and cluster-side receipts were not reopened by this audit. |
| Z reconciliation | `df10748b78f619e72302e80cd2d9de3cf64e00ee:docs/orchestration/DECISION-SUPPORT-20260916-z-to-adopted-5d-covariance.md`, §§10, 13, 15 | Latest routed reconciliation. §15 updates §13; §11 is withdrawn. Its repeated product figures share the producer's origin. |
| Independent assessment | `5a6d32fb34b99da2f3974e46e22082be0a746d3d:docs/orchestration/ASSESSMENT-20260917-theta-and-the-propagation-argument.md` | Independent source/mathematical critique, **not** independent cluster-payload verification; the record explicitly labels those figures relayed. |
| B design | `78a8c2ee42c71db1e300e4cfe3735554101bf8ce:docs/orchestration/PREDECLARATION-20260916-B-estimator-and-coverage.md` | A proposed estimator/repeat design exists. It does not establish B or authorize execution; its older “barred” fallback language is superseded by reconciliation §13.1's **unruled**. |
| Historical candidate evidence | [candidate stamps](../../nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json), [endpoint census](../../nd-unfolding/uq_5d/receipt_cause1_endpoint_census_5d.json), [construction contract](../../nd-unfolding/uq_5d/receipt_construction_contract_5d.json), [ledger](../../VALIDATION_LEDGER.md) | Dated measurements on their named products; they neither transfer automatically to Z nor constitute adoption. |

For branch-only sources, `git show <full-commit>:<path>` recovers the exact text.
Their branch names and full identities are also retained in the navigation record.
This audit does not merge their analysis code or regenerate their records.

**Observed documentation conflict:** the N-D status's older “Current quotable
results” table still presents corrected covariance scales and an inferential GoF
PASS. Its later Z paragraph, the ledger's quarantine and statistical-validation
repair, and the OI rulings qualify or supersede those readings. The same is true
of the older dependency map's publication-PET and independent-4D routes: they
cannot override the PET ruling or the final adopted-5D projection requirement.

## Ranked unresolved gaps

Ranks reflect publication impact and dependency, not elapsed-time estimates.
Ranks 1–5 govern the intended uncertainty completion; ranks 6–8 govern what can
be inferred or released from it. Rank 9 includes obligations for the current
written claims, even if the Letter keeps its central-value scope.

| Rank | Gap and publication consequence | Existing evidence | Smallest decisive next action and completion evidence |
|---|---|---|---|
| **1** | **No complete null/reproducibility acceptance contract.** Neither a small observed null nor construction success qualifies the trunk. | SPEC §§3.6a, 3.7a, 6.4, 7 item 4; Z reconciliation §§13, 15. B and full S are open; epsilon is proposed/ungraded, and `null_epsilon` is withheld. The precursor persistence obligation is already met according to the outcome record. | **Decision/design first:** route the exact current S residue and B proposal to the eligible independent assessor, then obtain the §6.4 subject decision governing the control routes. Specify the execution envelope, justified B, scientifically justified S, feasibility B ≤ S, and epsilon within that interval. The deliverable is an approved argument with an explicit falsifier and named evidence needed; only then request the bounded missing control. Do not repeat the completed precursor/pilot. |
| **2** | **Cause-3 joint-baseline sensitivity has no approved full acceptance packet.** Stable trace/diagonals alone cannot qualify a covariance used through correlations. | SPEC §§3.6b, 3.7b, 3.7d, 6.3; `z_contract.Z_BOUNDARIES`; Z reconciliation §10.3. `cause3_agg`, `cause3_med`, `cause3_corr` remain withheld. A member/design proposal exists, so the gap is not “no design.” | **Specify the scientific loss first:** bind all varying estimator legs and their draw seeds, member set, aggregate statistic, per-bin movement **and acceptable fraction**, and a correlation-sensitive criterion for the declared projections. Have those independently assessed and approved before asking to build members. Successful construction of members would supply measurements, not adoption. |
| **3** | **Lineage, component compatibility, and endpoint completeness remain unverified on the final object.** Matching hashes cannot prove that the named parent/CV is the right one. | SPEC §§1.3d, 1.5, 2.7; Z reconciliation §10.1/10.4. The pilot binds inputs and reconstructed row/mask footing, but reports `parent.lineage_status: UNVERIFIED`; the external CV cross-check is unperformed. Endpoint `globalCompleteness > 1` remains unresolved in the reconciliation. | **Independent readback packet:** trace G to its actual combined source and production CV; verify reconstructed row order and mask elementwise, then each component's estimator, units, normalization, background mode, seeds, and support. Inventory the completeness numerator/denominator semantics and obtain their disposition; do not normalize them into range. Completion is a source-bound compatibility verdict and explicit unresolved cells, not a new matching digest. |
| **4** | **The remaining cause-specific measurements, independent grades, and disclosure have not all landed for Z.** Historical G/X/S grades do not close Z cells. | SPEC §2 and §6; historical scoreboard; OI-172/173; Z reconciliation §10. See the seven-cause table below. | Prepare a **Z-specific evidence checklist** separating already available operands, source-only checks, and missing counterfactuals. Commission only the missing measurements after their criteria and authorization exist; independent grading and the required note disclosure follow. A single “all causes repaired” summary is insufficient. |
| **5** | **Final 5D-to-lower-D covariance products and their identity/support proof are missing from the adoption chain.** Central-value anchors cannot replace them. | SPEC §2.6c; [3D covariance override](../../3d-unfolding/3D_OMNIFOLD_STATUS.md); [project_cov_nd.py](../../nd-unfolding/project_cov_nd.py); [p4_project_4d.py](../../nd-unfolding/p4_project_4d.py); OI-129. Existing projectors use width-weighted maps and record support exclusions, but the P4 writer still hashes the in-memory row vector and omits an output-file digest. | **Freeze the consumer map now:** enumerate 5D→4D, 5D→3D, E_avail and (E_avail,W), their units, bin widths, masks, ordering and orphan policy. Plan the OI-129 repair with its owning re-verification. After trunk adoption and projection authorization, require closed-file row readback, output and parent digests, both-direction support census, and C_low = M C_5D Mᵀ checks. Do not demand equality to an independently unfolded central estimator. |
| **6** | **A covariance and an inverse do not yet define a calibrated generator significance.** Finite-ensemble precision, rank choice, normalization fitting and region selection need a single consumer contract. | OI-137 and its [declaration-(v) record](../orchestration/PROVENANCE-20260822-declaration-v-scalar5d-blocks.md); [statistics appendix](../analysis-note/app_statmethods.tex), “Covariance-aware chi-square” and “Inference from unfolded events”; LIT-01/02. | Before inspecting a new significance, specify the residual/null, covariance product, retained subspace/rcond and scan, block ensemble conventions, fitted parameters, data reuse, and normalization treatment. Identify whether the high-E_avail/high-W choice is exploratory or give a selection-aware calibration design. Deliver an approved statistic/null specification; do not apply a generic Hartlap factor or call rank alone a calibrated ndf. |
| **7** | **Coverage for the reported scalar-5D uncertainty/functionals is not established by the routed evidence.** Closure, pull Gaussianity, independent assembly checks and exact projection are different tests. | [STATVAL_REPAIR](../STATVAL_REPAIR.md), WS1 and final verdicts; ledger “Validation Diagnostics” and July 16 repair; LIT-01; statistics appendix. The existing 2D pull exercise is not coverage, and FPS's fixed-seed containment diagnostic cannot certify the scalar-5D total band. | **Write the functional-coverage assumptions table:** fixed truth and independent interval calibration, forward/noise model, nuisance and finite-MC treatment, estimator randomness, declared functionals, marginal versus simultaneous target, and precision/power objective. Mark which assumptions are unestablished. This is a design deliverable; a benchmark study needs separate authorization and cannot substitute for trunk adoption. No completed 2D central campaign is reopened. |
| **8** | **Unbinned GoF and arbitrary event-level fits lack a demonstrated correlated null/uncertainty interface.** A held-out classifier split does not exclude the same events from weight fitting. | Direct trace of [unbinned_gof.py](../../nd-unfolding/unbinned_gof.py) to [omnifold_nn_core.py](../../nd-unfolding/omnifold_nn_core.py); STATVAL_REPAIR WS2; ledger's descriptive-only disposition; LIT-02/10. | Preserve the existing diagnostic-only status. For an inferential upgrade, first specify a fixed excluded-fold design and a full-estimator null (or justify an alternative calibration), including all fitting and selection. For release, bind coherent replica/family identities to stable event rows and document supported consumers. Nominal weights or independent resampling of unfolded rows do not satisfy this. |
| **9** | **Publication disclosure, durable evidence mapping, and final approval remain separate deliverables.** Source builds and scope rulings cannot prove evidentiary completeness. | OI-172 note obligation; OI-130 preservation inventory; OI-6 pre-submission purity revisit; OI-29 collaboration endorsement; September 17 manuscript verification. | Reconcile the outstanding disclosure with actual note text, finish the quoted-value→artifact→preservation map, and obtain the retained pre-submission decisions. Correct stale status/finite-N wording through its owners. Any manuscript edit must build note/primer/paper, synchronize and build the standalone repository, commit/push both, and record both remote heads. The audit does not assert those future acts are done. |

In rank 1, “epsilon” is the fixed-seed null bound. A per-bin uncertainty
consequence tolerance theta is a different quantity and cannot replace it.
The latest independent recommendation is **do not adopt the proposed theta as a
scientific ceiling on its present derivation**. That recommendation is not itself
an adoption ruling. Full S remains open; the F7-channel argument alone is narrower.

## Z construction and all seven causes

The construction contract is

    C_Z = D (sum of V bands) D + sum of R bands + sum of A bands + C_stat + C_ML

V is the covered vertical set; A the five selection-complete active lateral
bands; R the complement. The partition must be disjoint and exhaustive. The
joint-throw covariance supplies the **diagonal inflation**, not an additional
matrix block. A seed-sensitivity diagnostic is not an additional budget block.
Both mean- and CV-centered variants must exist; producing both does not authorize
choosing either. Source: SPEC §1.3a and `z_assembly.py`.

| Cause | Existing evidence and decisive qualification | Smallest remaining action for Z |
|---|---|---|
| **1: one-sided endpoints** | The committed census contains both endpoints for the pair bands and a **diagonal-only** counterfactual; OI-172 requires a note statement. SPEC §6.2 permits Z measure-and-disclose closure after independent verification, irrespective of magnitude. | Compare both one-sided choices with the actual two-endpoint construction on Z's bank, including off-diagonals and below-one tails; state denominators. Carry Flux, 2p2h and normalization unchanged and explicitly account for them—do not invent pair endpoints. Obtain independent verification and complete disclosure. |
| **2: CV centering** | Candidate F7 evidence exists in the ledger/receipts; the pilot records operands for both variants. Mean-centering alone is not revived by assembly. OI-186/188 show why population identity must accompany any inherited F7 ratio. | Independently evaluate the F7 argument and operand identities on Z itself, reporting the shift either way. Reconcile historical population wording separately; do not reuse a historical grade as Z's. |
| **3: estimator seeds** | Old composite seed descriptions were corrected in VL141; the newer design must bind the actual complete leg set. Boundary values remain withheld. | Complete rank 2 before the joint-baseline measurement. Keep fixed-seed numerical reproducibility distinct from changing estimator-seed sensitivity. |
| **4: jitter subtraction** | OI-173's stamped-candidate referent and permanent unmeasurability disposition concern that historical subject. SPEC §§2.4/6.5 requires Z's single-draw counterfactual; the multi-draw proposal was withdrawn. | Bind the seed, operands and print-only add-back comparison for Z under the exact specification; do not subtract a scalar jitter estimate from its covariance or reopen historical log sweeps. |
| **5: frozen PET weights** | Artifact-specific inapplicability is available under SPEC §6.1. The pilot's consumed-input inventory now exists, but construction does not dispose of this cell. | Independently trace the invoked construction and consumed inputs, including the adoption/inflation path, for absence of the PET frozen-map route; apply only the Z-specific ruling. This is not a PET study or a reconsideration of OI-126. |
| **6: incomplete statistical projection** | Correct full-matrix projectors and bidirectional coverage guards already exist; SPEC §2.6 withdrew claims that these guards were missing. The unresolved object is the corrected projection product plus the component-footing decision. | Specify the operator and both coverage populations; decide stat/ML reuse from compatibility evidence rather than assume reruns. Under authorization, produce the exact projection and the same-input legacy-versus-correct counterfactual. The scope of operator versus ensemble grading must be explicit. |
| **7: support-limited lateral selection** | The pilot records five active bands and an exhaustive partition. This does not independently verify ten endpoint identities, selection migrations or the five-of-nine scope on G's own source. | Verify identities, migration censuses and policy; justify the four weight-only bands' exclusion from the active swap on the actual source. Measure active-versus-support lateral blocks on identical footing. C_Z − C_G mixes several changes and is not this cause's magnitude. |

The historical [scoreboard](../orchestration/SCOREBOARD-20260817-quarantine-seven-causes.md)
was read with its corrections and OI-172/173/188. Its candidate/quoted counts
are neither Z's count nor a remaining-work estimate. No count or cell changes here.

## Pilot requirement reconciliation: completion is narrower than the checklist

`nd-unfolding/z_build.py:REQUIREMENTS` contains fourteen keys and emits them
unconditionally. Their presence is not fourteen independent failures. Conversely,
a completed subrequirement does not close its containing requirement. All keys
are accounted for below against Z reconciliation §10 and the outcome record.

| Requirement key | Evidence already recorded | Residual / ranked gap |
|---|---|---|
| `parent_lineage` | Parent and combined-source files digest-bound | Actual parent/CV relationship still unverified; rank 3. |
| `component_footing` | Single reconstructed mask/row footing bound | Per-component scientific compatibility not independently established; rank 3. |
| `cause1` | Prior census and specification | Z counterfactual, off-diagonals, independent verification and disclosure; ranks 4/9. |
| `cause2` | Both variants and F7 operands bound | Independent argument/grade; rank 4. |
| `cause3` | Proposed member construction and statistics | Approved boundaries, correlation criterion and all measured members; rank 2. |
| `cause4` | Specified print-only counterfactual | Z seed/operand-bound measurement and assessment; rank 4. |
| `cause5` | Consumed-input inventory | Independent path trace and artifact-specific disposition; rank 4. |
| `cause6` | Correct operator machinery exists | Defined operator, exact products, both support censuses, compatible blocks; ranks 3/5. |
| `cause7` | Active membership and exhaustive partition recorded | Endpoint/migration/scope verification and isolated counterfactual; ranks 3/4. |
| `null` | Internal same-run vectors and support predicate persisted | B, full S, feasibility, approved epsilon; external CV identity unresolved; ranks 1/3. |
| `code_and_run` | Producing revision and measured import digests recorded | Independent real-input/environment verification and supported reproduction; ranks 1/3. |
| `endpoint_completeness` | Above-one readings identified | Scientific interpretation/disposition on the actual endpoint population; rank 3. |
| `runtime` | Real construction and exact eigenspectrum timings recorded | Future work must use measured memory/runtime and fresh resource state; historical sizing is not current capacity or authorization. |
| `authorization` | One pilot authorization consumed | No authority inferred for another submission, production, grading, adoption or publication use. |

The outcome records explicitly distinguish structural PSD/identity tolerances
from scientific thresholds. This audit does not independently revalidate the
spectra. The recorded `G3R.stored_cv_cross_checked: false` and external CV
`UNPERFORMED`/`UNRESOLVED` are non-checks, not passes. Persistence itself is not
listed as work to repeat.

## Downstream inference: what the evidence does and does not support

### Projection semantics and precision

`project_cov_nd.build_projection` multiplies by widths of integrated axes, which
is required for differential-density covariance. `p4_project_4d.py` explicitly
uses reachable support and records unreachable destination indices. It writes
`hRowIndex4D`, then computes its receipt digest from the same in-memory indices;
it does not reopen that stored object or digest the resulting covariance file.
This confirms OI-129's residual at the audited revision, without modifying its
pin-bound implementation.

A successful map identity proves propagation of its input covariance. It does
not establish calibration, supply missing support, or turn a different direct
4D/3D estimator into the marginal of the 5D estimator. A downstream packet must
bind the central estimate paired with the projected covariance explicitly.

The proposed inflation-sensitivity argument also needs a projection-specific
check. A norm bound on a matrix perturbation does not generally give the same
**relative** bound after a projection nearly annihilates its denominator.
The latest assessment and reconciliation withdraw the universal-projection
claim. Enumerating the declared maps is source-only work; evaluating their
actual cancellation sensitivity requires the bound component evidence. Do not
label that numerical verification already done or infer it from nonnegative
bin-width weights.

### Finite ensembles: distinguish the objects before correcting anything

The [declaration-(v) record](../orchestration/PROVENANCE-20260822-declaration-v-scalar5d-blocks.md)
was checked against the current writer and projection sources:

| Object | Available convention/evidence | Remaining qualification |
|---|---|---|
| Joint-throw ensemble | `receipt_construction_contract_5d.json` records throw-root `n_throws`; the candidate-stamp receipt records propagated `upstream_n_throws`. MAT mean-centering uses 1/N. | It enters the final construction through diagonal inflation, not as a fourth covariance block. Its rank bound is not the rank of the total. |
| Scalar statistical/ML blocks | `combine_cov_nd.py` validates expected replica IDs, mean-centers, divides by N−1, and writes the covariance. Existing launcher ranges are 100 and 24. | The writer still stores no ensemble-count scalar. Bind actual members/counts and their provenance to final inputs; the launcher range is not independent readback of a particular product. These are scalar blocks, not PET's declined family. |
| Systematic bands | Endpoint census distinguishes pair bands, Flux and 2p2h; normalization is a separate deterministic contribution. | Do not treat every endpoint band as a Gaussian random sample or assign one ensemble size to the sum. |
| Downstream inverse | Appendix declarations (i)–(v) require covariance identity, inverse/rcond, retained rank, scan and per-block finite-N treatment. | A new Z significance needs its own specified inverse and calibration. The old P4 rank does not determine Z's rank or null law. |

OI-137's apply-or-disclose question was already decided: **disclose, do not
correct**, [August 22 ruling 11](../orchestration/DECISION-20260822-joseph-b1-lift-and-clause-c.md).
Do not route it as an unanswered choice. A new uncertainty-model change would
require its own decision. The appendix still contains the broad phrase “this
analysis's biased 1/N production convention” beside the ambiguous “unified-throw
5D candidate” example. Its owner should scope those phrases to the actual
MAT/joint-throw ensemble and distinguish the N−1 stat/ML blocks, as the existing
provenance record already requests. This is a wording gap, not a newly measured
precision bias.

### Historical significance consumers need more than a replacement filename

Direct source inspection confirms concrete migration work behind rank 6.
[eavail_generator_significance.py](../../nd-unfolding/eavail_generator_significance.py)
defaults to the historical independent 4D covariance, forms the width-weighted
E_avail marginal, calls `np.linalg.pinv` without an explicit `rcond`, and uses
the number of selected bins as chi-square degrees of freedom. Its high-energy
subset is fixed in code at E_avail >= 0.8 GeV; that does not establish that the
choice preceded inspection of the data. It prints eigenvalues, but does not
implement the required retained-rank declaration, truncation scan or null
calibration.

[eavailW_covariance.py](../../nd-unfolding/eavailW_covariance.py) constructs its
own historical component sum and evaluates full/corner quadratic forms using
`pinv` and bin counts as degrees of freedom. These paths are not an implementation
of consuming the final adopted Z trunk. Neither script was run and no historical
significance is reinstated. The smallest next action is to specify a replacement
consumer contract tied to the adopted trunk, central pairing and support; changing
only an input path would leave the inference assumptions unresolved. The source
inspection establishes missing declarations/calibration, not the actual rank or
numerical bias of a future projected covariance.

### GoF call trace and existing disposition

1. `unbinned_gof.main` either loads `w_pull` without a fold/provenance contract or
   invokes `omnifold_loop` on the full supplied measured/MC arrays.
2. The called core defaults to `train_frac=1.0`; its optional split is a random
   per-step/per-iteration training subset, not a permanently excluded outer fold.
3. `c2st` subsamples, normalizes class weights, shuffles and halves the rows only
   after weights have been obtained; it trains one classifier on the first half.
4. It computes effective sample size from test weights and an analytic Gaussian
   accuracy null. It does not refit the unfolding/classifier under null replicas
   or permutations. Its printed PASS is therefore not evidence of calibrated
   inference under the project's own WS2 contract.

This is **confirmation of an existing limitation**, not a new discovery from
LIT-02. The ledger's “Validation Diagnostics” and July 16 repair already retain
accuracy/AUC as descriptive and reject the analytic inferential interpretation.
No historical p-value is promoted here, and no numerical calibration error is
estimated. The old N-D status entry and executable's presentation need owner-led
reconciliation with that disposition; the completed central/closure validations
remain intact.

### Coverage and release assumptions to settle before another study

The September 17 [literature record](2026-09-17-review-and-incorporation.md)
correctly records proposed studies as unperformed. The new paragraph in
`app_statmethods.tex`, “Inference from unfolded events and selected projections,”
is present; a bibliography or paragraph is not the study's completion evidence.

| Required declaration | Available evidence | Still needed for the requested use |
|---|---|---|
| Target and estimator | Frozen scalar central results and SPEC's fixed-footing contract | Exact pairing of nominal estimator and uncertainty procedure, including any averaging location, seed/split policy and bias treatment. Smaller seed spread alone is insufficient. |
| Truth/noise/forward model | Closure studies; STATVAL_REPAIR distinguishes fixed truth from fluctuated MC truth | Independent truth and calibration/evaluation construction covering the noise sources the proposed interval claims, including finite MC and relevant nuisances. |
| Functionals and coverage family | Publication axes and existing width-weighted projectors | Units/support, explicit integrals or contrasts, marginal or simultaneous claim, and treatment of data-selected regions. |
| Calibration precision | Historical toys/diagnostics with stated limits | Prespecified size/power or Monte Carlo precision and an uncertainty treatment respecting within-toy correlations; no pooled bin–toy binomial error. |
| Reusable event release | LIT-10 schema proposal and the appendix's correlation warning | Stable row/event identities; nominal and family/member IDs; units, support, normalization, centering/divisors, digests, coherent replica correspondence; one supported reproduction example and explicit limits on arbitrary new projections/fits. |

Primary abstract pages were checked on the audit date. [Desai et al.](https://arxiv.org/abs/2504.14072v2)
report that omitting unfolding-induced event correlations can underestimate
parameter uncertainties. [Stanley et al.](https://arxiv.org/abs/2502.02674v2)
require an evaluable forward model, known noise distribution and constraints for
their functional-interval construction; [Batlle et al.](https://arxiv.org/abs/2510.11708)
address simultaneous functional calibration. These motivate the assumptions
review; they do not verify this analysis's implementation or transfer coverage
guarantees to its learned estimator. No full-method equivalence audit of these
papers was performed here.

LIT-07's symbolic background/acceptance mapping is a useful design task alongside
OI-6, not grounds to replace the settled purity footing. OI-6 still requires a
pre-submission reaffirmation or a separately commissioned matched comparison.
LIT-06 ensemble placement, LIT-08 profiling and LIT-09 alternative estimators
would change or compare inference procedures; none is a missing mandatory
production implementation. PET comparisons remain outside this publication-UQ
completion path.

## Recommended sequence and audit verification

1. Resolve the scientific contract first: full S assessment, §6.4 subject decision,
   B/repeat design and the cause-3 correlation/coverage criteria. Preserve explicit
   unresolved outcomes; do not use observed pilot agreement to choose thresholds.
2. In parallel with that design work, assemble the source-bound lineage/component
   and seven-cause evidence packet, the projection/consumer inventory, and the
   preservation/disclosure checklist. Source inspection may finish some checks;
   payload-dependent checks must remain labeled unverified until read.
3. Obtain only the named missing measurement authorizations, with fresh execution
   and resource observations. Grade independently, adopt explicitly, and then
   produce the bound projections and the particular calibrated inference claimed.
4. Complete manuscript/release synchronization and retained submission decisions.
   Do not turn the covariance upgrade ruling into a declaration of publication
   readiness or repeat completed central campaigns.

The report's closure test is deliberately different from the scientific gates:
it covers all fourteen Z requirement keys, all seven causes, the selected
literature's covariance/inference implications, and the governing dispositions,
with an evidence route and smallest next action for every ranked gap. It does
not certify the candidate or close any OI. Validation of this documentation
change consists of source/link checks, the repository commit hooks, and a Git
diff/status check establishing that only this report was added. No manuscript
build or analysis test is needed to validate an added Markdown audit that is not
included by the manuscript or analysis code.
