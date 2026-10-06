# PET and GBDT comparison using existing outputs

Prepared 2026-10-05 for a fresh Opus 5.5 session. This is a bounded analysis and cost assessment for deciding whether to advance PET toward a full real-data unfolding. The objective is PET completion if scientifically worthwhile, not a substitution of scalar publication work for PET. The accompanying goal supplies the proposed execution scope when issued; this handoff alone does not launch or authorize a campaign.

## Decision to answer

Use saved results from H2S1T24 K5, L128S1T24 K4 and relevant GBDT studies to establish what comparative accuracy, variability, topology recovery and uncertainty evidence actually exists. Deliver the strongest supported comparison, its missing operands, and a costed recommendation for the next PET action. Retain both PET finalists; neither is established as the best architecture.

The cost constraint is central: an expensive comparison is not automatically a prerequisite to doing the unfolding. If a proposed comparison would cost roughly as much as a useful full PET production effort, assess whether proceeding directly with staged production and embedded validation would buy more information. Do not default to a thousand-hour comparison merely because a formal ranking remains unresolved. Conversely, a nominal real-data curve cannot measure bias or validate intervals: price the construction and the necessary validation separately, then compare complete alternatives.

## Starting state and durable evidence

The numerical PET closeout is preserved at commit `9a9a7bfb8fe0ce646a9895090a8d7b6c09568866` on `pet-final-design-20260925`. The remote branch was subsequently measured at `bc356b0c0c5b56cb4877bdf2312d2d5dc6d1936d` while integration was being prepared. The latter updates ledger references for integration; do not treat the original branch-local ledger IDs as canonical main IDs. The predecessor is `pet-improvement-20260922` at `9368ec9e55eb486109498772753825fc24616851`.

Remote main was measured at `c64228dab8b4d55e3fec772b8c05c004268578b7` during preparation. These are discovery snapshots, not claims about the state at startup. PR #3 targeted `pet-direct-token-comparison`; PR #4 targeted `pet-improvement-20260922`. An integration worker may be changing these. Establish current remote heads, merge status and source identities before choosing an isolated analysis branch. Do not merge or retarget the PET PRs under this task or edit another worker's checkout.

The PET study finished with `NO_ELIGIBLE_DESIGN`. Its two independent review cycles are closed; this task is a new comparative analysis, not another review of that selection. The original rules, failures and sample roles remain unchanged. PET remains diagnostic and method development under the current publication scope.

Read these routes in order, using the pinned PET commit if its paths have not landed on main:

1. `AGENTS.md`, `docs/orchestration/CAMPAIGN-REVIEW-20260929.md`, `docs/CURRENT_WORK.md`, and the governing records for any active work encountered.
2. Under `nd-unfolding/pet/final_design/`: `REPORT-20260926.md`, `DECISION_RECORD-pet-final-design.md`, `REVIEW_DISPOSITION-DECISION-20261005.md`, `PROTOCOL-20260925.md` with its amendments, `CAPACITY-20260925.md`, and the current closeout handoff. The decision and report supersede stale next-action lists in historical handoff sections.
3. `VALIDATION_LEDGER.md` at the matching source commit. PET rows were VL142-VL145 on the closeout branch and are being integrated under new IDs. Resolve rows by subject and source identity, not just a number.
4. Under `nd-unfolding/pet/final_design/`: `DEVELOPMENT-20260926.md`, `scalar/SCALAR_AUSSIE_MATCHED-20260925.md`, `scalar/frozen_config.json`, `scalar/results/`, `resources/cost_fb_look1-20260930.json`, and the resource-ledger routes from the decision record.
5. Under `nd-unfolding/pet/improvement_campaign/`: `REPORT-20260922.md`, `phase_b/scalar/SCALAR_REFERENCES-20260922.md`, and `phase_d/SCALAR_SCALING-20260922.md`. Historical implementations and miss rules differ; these are context, not automatically a current production-GBDT baseline.
6. `nd-unfolding/gbdt_model_dependence/{README,DELIVERY,PROPOSAL}.md`, `docs/orchestration/CAMPAIGN-s5p-20260926-index.md`, and `docs/orchestration/CHECKLIST-20261001-s5p-terminal-and-claims.md`. The existing scalar synthesis is delivered. The s5p measurement branch was not admitted; its joint-test work does not construct a new total-uncertainty measurement. Do not repeat that synthesis or launch its deferred panel.
7. Before implementing reductions: `KNOWN_ISSUES.md`, the relevant status/reference, callers, tests and hash bindings. Follow repository code-delivery and language conventions.

## Findings to preserve

H2S1T24 K5 has stronger point estimates on several designated recovery endpoints and passed all frozen point-estimator rules. L128S1T24 K4 has lower measured run cost and a less extreme observed maximum truth weight. The study did not establish an overall ranking between them.

| Quantity | H2S1T24 K5 | L128S1T24 K4 |
| --- | ---: | ---: |
| Energy-tilt recovery | 0.895 | 0.863 |
| Proton-topology recovery | 0.391 | 0.348 |
| Joint energy and momentum-transfer recovery | 0.446 | 0.450 |
| Seed SD of primary recovery, development | 0.037 | 0.043 |
| Maximum observed truth weight | 90.2 | 33.4 |
| Median A100-hours per unfolding, final-bank cost receipt | 1.767919 | 1.517087 |

These numbers are conditional on the study's banks, signal-only simulation, response, sample size and configurations. Reproduce the values used in the new report from their exact receipts. The 0.306 historical comparator is old PET, not GBDT. Recovery 0.895 is the fraction of an injected histogram discrepancy removed under the specified metric, not general 89.5 percent accuracy.

L128's B2 value 0.0122 exceeds 0.010, while H2's is 0.0097. Both reported intervals cross the threshold. The original point-rule failure stands; it does not establish a robustness ordering. H2's six-member interval procedure failed aggregate calibration and width rules and under-covered low acceptance. L128's coverage was never measured. Its untested procedure is neither certified nor presumed to fail.

The shorter truth-training designs failed the seed-stability screen. Tested PET2 recipes failed the topology screen or stability requirements. An untested model might do better, but no new architecture search follows from these results. H2 uses the project's compact PET, categorical truth PDG, detector summaries, constant per-iteration learning rate and a 24-epoch truth step. It does not use the separately tested Gregor-derived PET2 pretrained backbone.

## Execution scope

One Opus 5.5 owner implements the analysis and report. The proposed goal permits one fresh read-only independent reviewer of consequential new reductions and the cost recommendation, with at most two focused review/repair cycles. The existing closed PET review is not restarted. A failure to establish comparative superiority or cost feasibility is a valid terminal result.

Start with existing committed operands and recoverable completed products. Reading/copying authorized completed cluster artifacts, checking identities and scheduler state, and lightweight reductions are permitted. No new PET training, extraction campaign, GPU allocation, coverage ensemble, architecture search, real-data unfolding or systematic production is part of this task. Do not launch CPU batch allocations either.

If an exact GBDT comparator is absent, the proposed goal allows a small CPU-only fill-in on already available matched samples: at most 8 CPU-core-hours of new GBDT fitting on local CPU, including retries, at most four fitting threads concurrently, no hyperparameter search. This is a proposed task ceiling, not a measured cost forecast. Check a bounded pilot against that ceiling before expanding; stop before exceeding it. Use a documented existing competitive recipe and common detector summaries, and keep these new results explicitly exploratory. A more expensive comparator becomes a costed request, while the existing-output analysis still finishes. Do not substitute a convenient weak comparator to satisfy the ceiling.

Ordinary reduction and plotting of saved outputs is separate from the new-fit ceiling and must remain modest; no full training is hidden inside a reduction. If inputs cannot be recovered, report the missing quantity and its recovery path without retraining PET. Never run heavy analysis on a cluster login node.

Leave PET integration, the scalar campaign, independent recomputation, the 2D coverage worker, their budgets and jobs with their current owners. No collaborator messages, publication adoption, Gate-6 work, reopening of OI-126, note/primer/paper edits or PR merges are included. Scientific records of genuinely new measurements must follow the repository's ledger/run-log/status rules without rewriting historical verdicts.

## Analysis sequence

### Establish which comparisons are possible

Build a compact manifest of available PET and GBDT products: source commit, producer, file digest, configuration, event identities, pseudo/prior selection, truth distortion and digest, normalization, miss rule, backgrounds, nuisance treatment, seed roles, iterations, feature definitions, histogram support and sample role. Recover raw paths from receipts. Check completeness directly; a missing local file is not evidence that a cluster product is lost.

Useful PET operands include `results/final/scored_fb/`, `results/final/evidence_look1.json`, `results/s3n/`, `results/final/coverage_dev/coverage_H2S1T24K5.json`, `results/final/scored_s5c/`, the completeness manifests, and producer-side `replicate_arrays.npz` and saved weights identified in receipts. Inspect schemas before assuming per-event weights or a particular histogram survive.

Classify comparisons as exact paired, comparable but unpaired, or incompatible. The final-design scalar references use HistGradientBoosting, not automatically the current LightGBM production estimator. Scalar s5p ensembles have different backgrounds, truth definitions and scopes. Do not splice them into a common ranking merely because the axis is called E_avail.

Freeze the analysis cases and metric definitions before any optional new GBDT fits. Reusing previously inspected PET final-bank results for this new question makes the comparison exploratory, not untouched confirmation. Keep reserve-bank access controls intact. Do not score blinded D4c coverage outputs or open new reserve selections.

### Compute the supported comparison

Use common observables and identical scoring definitions where possible: aggregate and regional E_avail, energy versus proton class, and energy versus q3. Include null and near-zero-injection cases when compatible saved products exist. Distinguish stored truncated-cloud species counts from full particle multiplicities.

Report signed bias, absolute residuals, empirical repeat spread and mean squared error where repeated comparable samples permit them. Preserve the distinction between fixed-population truth and each replicate's own truth; variation of estimate minus a moving target is not automatically unconditional estimator variance. Avoid recovery ratios for negligible injected changes. Report uncertainty of paired differences using the correct independent unit and bank conditioning, not bins as independent replicates.

Separate event variation from estimator-seed variation when the design permits; otherwise identify their mixture. Keep single-run and six-member-mean estimators separate. A comparison of single runs cannot certify the six-member package's precision, and member spread is not automatically the standard error of a member mean.

For coverage and width, compare only actually constructed intervals with compatible targets and repeated experiments. Existing point-estimator outputs cannot manufacture a GBDT uncertainty procedure. No total-coverage claim follows from statistical or training intervals. Treat GBDT versus PET representation differences explicitly: shared summary inputs help distinguish information effects from learner effects, but do not require stripping PET's cloud information from the practical comparison.

Produce a short report, reproducible reductions, machine-readable plot data and a few useful exported figures. Independently reproduce consequential metrics and audit a sample back to raw operands. Review the figure labels and actual exported figures. No new prose belongs in the publication deliverables under this task.

### Price the alternatives before recommending more experiments

Estimate the incremental resources and elapsed time for each route, with uncertainty ranges and a named source for each assumption:

| Route | Required distinction |
| --- | --- |
| Existing-output comparison | Reduction, retrieval and any bounded CPU GBDT fill-in; zero new PET GPU training |
| Small missing comparison | The exact unresolved decision, sample size needed to resolve it, training and review cost; reuse savings |
| Nominal real-data PET run | Input/scale readiness, backgrounds, normalization, training and extraction; diagnostic unless separately validated |
| Full PET uncertainty construction | Matched central definition, data/MC statistics, training variability, detector/flux/physics effects, model dependence, correlations and overlap |
| Validation and release | Coverage/bias tests at the claimed scale/domain, independent checks, provenance, reproducibility and integration |
| Direct production with embedded validation | Which products would serve both production and decision-making, early stop checkpoints, costs recoverable if the method fails |

Use task counts, training epochs, actual row counts, packing, I/O, startup, memory, retries and verification reserve. Distinguish A100-hours from GPU node-hours, CPU-core-hours from CPU node-hours, and hardware time from queue time. Do not copy a quota as a spending decision. Re-measure resource availability only when needed for a concrete proposal; do not quote an old balance as current.

The measured study cost is 1.77 A100-hours for H2 or 1.52 for L128 per run at 600,130 prior and 600,111 pseudodata rows, with two concurrent tasks per GPU. It is not a full-statistics production benchmark. The recorded H2 interval repair estimate is about 3,200 A100-hours and 12 days at prior throughput, for development calibration plus reserve-bank validation at the study scale. It does not include a full real-data total-uncertainty construction.

For scale only, three cases times 20 or 40 repeats of both PET single-run estimators would cost about 197 or 394 A100-hours at those rates, before reserve and CPU costs. Six members for every estimate would multiply that by six, to about 1,180 or 2,370. These are arithmetic illustrations, not selected designs or evidence of sufficient power. Do not launch them.

Before recommending a costly comparison, state what decision it could change and how its result would alter the subsequent spend. Compare total incremental costs of comparison-then-production and production-with-embedded-validation, avoiding double-counting reusable products. Similar GPU costs may favor direct staged production; different scientific information may still justify a small discriminating test. Neither conclusion is automatic. Unknown full-production costs should be reported with the exact missing benchmark and the smallest proposed way to obtain it, rather than padded with invented precision.

## Completion and stopping

Deliver:

1. Verified evidence manifest and compatibility/exclusion table.
2. Reproducible paired comparisons where supported, and explicit limits elsewhere.
3. A concise disposition for each finalist relative to the actual GBDT baseline tested, without proclaiming a universal winner.
4. A cost comparison of the routes above, including the marginal value of more comparisons versus doing production work directly.
5. One recommended next action with a concrete resource request and stop condition, or a supported no-go. Any future validation must define fresh assessment, scope and adoption requirements prospectively.
6. Committed and pushed analysis/report artifacts on an isolated branch, a draft PR, and a durable handoff with exact source/output commits and review disposition. Preserve this handoff and the issued goal in that branch. Do not merge other workers' work.

Stop this task when those deliverables are complete, even if evidence is insufficient to rank the methods. A missing comparison or a costly validation is a proposal, not permission for an automatic next campaign. At most two focused review/repair cycles; record any remaining material disagreement and the decision it prevents.

## Approaches not to repeat without new evidence

- Broad model search: the current question is practical value and uncertainty construction, not global architecture optimality.
- Selecting H2 because it is smaller or cheaper: the measured large-package runtime is lower, and neither finalist was selected.
- Declaring L128 robust because B2 is unresolved: its frozen point-rule failure stands; uncertainty in an ordering is not a pass.
- Shrinking every PET interval or dividing by sqrt(6) by assumption: shared sample effects and low-acceptance undercoverage make this an unvalidated repair.
- Treating a nominal real-data curve as an accuracy test: truth is unknown; required validation must be costed, even for a direct production route.
- Treating another comparison as inherently economical: it must justify its incremental information against a production route of comparable cost.
- Repeating completed scalar synthesis, changing the adopted scalar covariance, or reopening historical PET pairing campaigns: none answers this bounded comparison.
