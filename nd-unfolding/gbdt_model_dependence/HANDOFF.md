# GBDT model dependence, variability and resolution: analysis and note handoff

Prepared 2026-10-03. This is a new evidence-synthesis and documentation task, not a takeover of the running scalar-5D campaign.

## Objective and completion

MINERvA-OmniFold develops unbinned neutrino cross-section unfolding. Its scalar five-dimensional estimator uses LightGBM classifiers and a regression treatment of missed events. Existing studies measure incomplete recovery of physical truth deformations, prior sensitivity, statistical variability, numerical sensitivity and the effects of iterations, capacity and reporting resolution.

Use those existing products to determine what relationship between model dependence, variability, resolution and cost is actually supported. Produce reproducible figures and tables, add the supported findings in the appropriate place in the analysis note, and identify the smallest additional measurements needed for stronger claims. Do not assume a monotonic bias-variance tradeoff or a successful precision measurement. A plateau, deterioration, unresolved relationship or insufficient evidence is a valid result.

Completion requires:

1. A verified inventory and claim-to-evidence table, including exclusions and inaccessible operands.
2. Reproducible reductions, machine-readable plot data, figures and a concise scientific interpretation.
3. The analysis note updated with the findings and their limits; related primer and paper wording consistent with the evidence.
4. All three documents built and inspected in both the canonical and standalone note repositories, corresponding sources committed and pushed, and both remote branch heads recorded.
5. A prioritized, costed missing-data proposal, separating essential measurements from optional extensions and distinguishing statistical from total-uncertainty claims.

The task permits implementation and testing of analysis/plotting code, reading and reducing existing authorized products, note edits, repository records, and the commits and pushes necessary to deliver and synchronize them. It does not authorize new extraction, unfolding, training, resampling ensembles or batch allocations. Identify those as proposals; do not launch them. Do not stop the existing-data analysis or note work merely because a proposed extension needs a separate compute decision.

One analyst owns the reductions and manuscript changes. Existing independent reviews are evidence for their stated operands only. Independently reproduce consequential reductions and check figure operands against receipts. A fresh read-only reviewer may be used if separately authorized and available; do not infer delegation authority from this handoff. State any outstanding independent-review requirement honestly. Budget at most two focused review/repair cycles before recording the remaining issue and deciding whether further review would answer a material question. The terminal condition is delivery of the existing-data result and the missing-data proposal, even when no tradeoff curve or qualifying measurement is established.

## Durable starting point and required reading

Canonical repository: the repository containing this document. Remote `origin/main` was measured at `556d16373ae859e449b3fb71c1f61b14b7b61891`. Establish the current remote head anew; use an isolated branch/worktree from it. Do not update or edit another session's checkout. The branch `s5p-parallel-recompute-20260928` was at `2a696072735cc32b7c6afceb6fae9b360ffe5e2d`; it belongs to the running campaign's independent verification, not this task.

Standalone note repository: use the configured `analysis-note` remote, whose `main` was measured at `9191693249d5af2dec8ddf20561119f8f1d84286`. Re-measure its current head and inspect its own instructions before writing. These hashes are discovery baselines, not freshness claims. No analysis or note change specified here has been implemented yet.

Read these routes before analysis or manuscript edits:

- `AGENTS.md`, `docs/orchestration/CAMPAIGN-REVIEW-20260929.md`, `docs/CURRENT_WORK.md`, and the exact `OI-193` row in `docs/OPEN_ITEMS.md`.
- `KNOWN_ISSUES.md`, `nd-unfolding/ND_OMNIFOLD_STATUS.md`, the routed workstream reference, and ledger rows `VL153`-`VL155` plus their original receipts and reviews. Later corrections outrank older summaries.
- `docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md`.
- `docs/orchestration/RECORD-20260927-s5p-stage2-exit.md`.
- `docs/orchestration/REVIEW-20260927-s5p-round1-stage2-exit-and-joint-design.md` and the subsequent repair/admission records.
- `docs/orchestration/state/s5p/contract.json` and amendments 1, 2, 3, 4, 7 and 8.
- `docs/orchestration/CHECKLIST-20261001-s5p-terminal-and-claims.md`.
- `docs/orchestration/HANDOFF-20260928-s5p-analysis-note-sync.md` for the synchronization procedure. Its old heads and ownership are historical.

Use existing routed handoffs for operational history rather than recreating it. On the cluster, run the canonical live-state freshness check, then observe relevant sources directly. Do not load the orchestration tree wholesale. Apply the repository's import-origin guard: a pinned source tree is insufficient if imports resolve to another checkout.

## Scientific interpretation to preserve

The s5p measurement branch was not admitted. Its tested configurations and reporting definitions could not meet the frozen usefulness requirements within the supported design and budget. The running branch constructs calibrated joint generator tests at one estimator setting; it constructs no new measurement covariance or reportable total uncertainty. Its terminal publication-readiness field remains NOT READY under its governing contract, whatever the test result.

This does not prohibit reporting a carefully supported methodological limitation. A diagnostic account of bias, variability and resolution is a distinct scientific contribution. Preserve the original failed verdict; do not rename it a passing measurement or weaken its criteria retrospectively.

Distinguish three quantities throughout:

- Bias and recovery at known simulated truth.
- Statistical/algorithmic variability under a specified repeat or resampling construction.
- Prior sensitivity or a proposed allowance for model dependence.

A prior-variation envelope is not automatically a probability distribution, covariance or guaranteed bound on bias. Adding it to a statistical interval does not establish total coverage. A smaller ensemble spread can accompany larger bias; wider intervals can remain invalid. Do not claim the classical bias-variance pattern unless both sides are measured for comparable settings.

The scalar-5D adopted trunk and its byte-scoped exception are outside this task. If its uncertainty is used as a contextual reference, open the adoption record and carry its four measurements and exact estimator pairing. Prefer comparing quantities from the studied candidate itself. No adoption, central-estimator replacement, regrading of historical products, publication-complete claim, PET uncertainty work or reopening of OI-126 is authorized here.

## Existing evidence and its recovery routes

All paths below are repository-relative. Raw cluster paths and input digests are recorded inside the named receipts; resolve them there rather than copying a session-local path or guessing a namespace. Check access, identities, completed counts and metadata before reuse. Preserve originals. Generate new outputs in a separate namespace.

| Evidence | Canonical operands | What it can establish and what to check |
|---|---|---|
| Iterations and capacity | `docs/orchestration/state/s5p/stage2/stage2_receipt.json`, section `study_K`; `nd-unfolding/s5p_converge.py` | Committed snapshot has baseline nominal and W3 traces through 200 iterations; GiBUU/W1 through 40 and q3 through 30; capacity 400 trees/31 leaves through 10 on three truths. Some are partial checkpoints with explicitly recorded iteration counts. Do not imply every truth or capacity ran to 200. Noise-free construction measures recovery, not sampling variance. |
| Candidate and pseudo-experiment assessment | `docs/orchestration/state/s5e/cand/dev_receipt.json`, `assess_receipt.json`, and `state/s5e/cand/review-round-2.md`; `nd-unfolding/s5e_candidate.py` | R repairs nominal background bias. Assessment has 40 nominal and 20 each at five departure points. Per-functional bias, pull and interval diagnostics are available. Original A_FAIL remains; pooled checks do not certify every cell or total intervals. Reused assessment truths are now development evidence. |
| Numerical and bootstrap overlap | `state/s5p/stage2/stage2_receipt.json`, sections `study_N` and `study_C`; `state/s5p/contract-amendment-2-stage2-studies.json`; `nd-unfolding/s5p_numerics.py` | Data jitters paired with bootstrap replicas; two pseudo-data points with similar controls; 160 nominal experiments assembled for calibration checks. Identify which variation each repeat actually includes and whether the samples are independent. The tested R bootstrap absorbs the rounding component under this design; do not add that component twice or generalize this result to another estimator. |
| Prior sensitivity | `state/s5p/stage3/envelope-receipt.json`; `state/s5p/contract-amendment-3-stage2-supplement.json`; `nd-unfolding/s5p_envelope.py` | Data prior variations, cell-level shifts, correlations with simulated bias, and envelope with/without D1. Review found incomplete per-cell bounding and an assumed truth hull. D1 used a problematic generator comparison; report its historical status and use corrected/excluded comparisons appropriately. Other older ratios also require provenance checks before interpretation as current generator differences. |
| Reporting resolution | `state/s5p/contract-amendment-1-use-case-and-targets.json`, `state/s5p/stage1/stage1_inspect.json` | Supported finer J cells, coarser H2 cells and EW projection. Reaggregate compatible saved fine-grid products to each map; verify support, cell integrals, units, rate and boundary handling. Different cells estimate different functionals: do not equate a precision improvement from aggregation with improvement on an unchanged estimand. |
| Cost | `state/s5p/stage2/forecast.json`, `forecast-inputs.json`, measured costs in the receipts and execution records | Measured timings and provisional forecasts can support a limited cost comparison. Distinguish reserved and billed time, packing, threads, workload and incomplete runs. Forecasts are not measured costs. |
| Current joint-test ensembles | `state/s5p/contract-amendment-7-production-admission.json`, `state/s5p/prod/design.json`, `nd-unfolding/s5p_nullexp.py` and the terminal checklist | Products include `xsec_flat`, `xtrue_flat` and metadata. They evaluate a five-iteration setting with their own nuisance/split construction. Await the campaign's committed terminal results for scientific claims. Their large count does not provide a scan over estimator settings; raw products may support later descriptive reductions only with their proper conditioning and selection rules. |

Paths beginning `state/` in this table are under `docs/orchestration/`. Locate raw products from the receipts' namespace and product records. Do not rely on old counts printed in handoffs. Existing raw convergence, prior, numerical and candidate-assessment products were accessible during preparation, but accessibility is volatile and preservation still needs checking.

Before pooling any files, build an input inventory containing repository commit, producer, digest, pseudo seed, estimator seed, bootstrap/jitter seed if relevant, truth definition/digest/amplitude, background treatment, nuisance construction, iteration count, classifier and regression settings, dtype, MC split, reporting map, units, role and completion status. Count shared origins once. Lost, partial, obsolete and unestablished products must be visible, not silently dropped.

## Work sequence

### Establish the evidence and recover what is usable

Freeze the actual baseline and source identities in the task report. Audit the inventory against receipts and readbacks. Determine whether saved per-iteration outputs support reaggregation and whether raw candidate ensembles contain the required per-functional quantities. Recompute selected values independently before generating the whole table. Record access/preservation gaps as such; a missing local glob is not evidence that the cluster product does not exist.

For missing raw operands, use committed summaries only at their supported precision and label figures as receipt-based. Do not fabricate distributions from summary statistics. Do not rerun training merely to replace a missing file without a separate compute authorization.

### Produce the figures supported by existing data

Create a compact analysis package with explicit inputs and a reproducible command. Prefer a new script/module and output directory rather than modifying receipt-bound production code. Apply the repository's Python and delivery conventions. Meaningful controls should exercise aggregation, identities, exclusions and metrics; do not create tests that merely repeat implementation.

Candidate figures, subject to the inventory:

1. Recovery bias versus iteration, by known truth and reporting resolution. Show actual available ranges, signed residuals where useful and physically relevant tails/regions alongside medians. State the denominator and departure threshold for any normalized recovery metric. Avoid dividing by tiny injected departures.
2. Bias versus repeat variability at the existing setting, with uncertainty on both estimates. Use matched ensembles wherever available. Distinguish empirical repeat variance, bootstrap width and rounding sensitivity. Do not manufacture a cross-configuration frontier from different truths or sampling schemes.
3. Prior sensitivity beside statistical width and simulated recovery bias, with construction and truth identities visible. Report the imperfect relationship instead of calling prior shifts measured real-data bias.
4. Coverage and width diagnostics for existing interval constructions, by functional/region and truth. Use the historical interval as actually defined. Mark sample sizes and development status. Do not borrow an adopted covariance to relabel these as total-coverage tests.
5. A compact measured-cost table if comparable timing records exist.

Keep plot-data tables, exclusions and uncertainty estimates with the package. PDF or SVG figures and a script for regenerating them are required. Inspect the exported figures and their rendered manuscript pages. Include a caption identifying estimator, truth, sample role, interval meaning, support and limitations. A figure whose premise is unsupported should be omitted with a concrete reason.

The scientific report must answer: what actually moves when iterations, capacity or resolution change; what persists; whether variability was measured for those same settings; and whether the evidence supports a tradeoff, a plateau, or only separate observations. Reconcile apparent contradictions across earlier diagnoses by their operands and conditions. Do not turn a finite scan into an algorithm-wide impossibility or an infinite-iteration statement.

### Put the supported account in the note

Read `docs/analysis-note/main_note.tex`, `sec_validation.tex`, `sec_eavailw.tex`, `app_statmethods.tex`, `paper_body.tex` and `primer_body.tex` at the current baseline.

The preferred main location is a clearly named subsection in `sec_validation.tex`, adjacent to the existing scalar-5D departure-response and refinement-candidate paragraphs and before the unbinned C2ST diagnostic. Explain the experimental setup and result there; retain the distinction between methodological diagnostics and the reported cross-section construction. Put detailed definitions and repeat/interval procedures in a nearby subsection of `app_statmethods.tex` if needed, with cross-references from the main discussion. Use `sec_eavailw.tex` for a short implication/reference rather than duplicating all results. Change this placement if the current structure has evolved, and explain the chosen location in the delivery record.

Remove direct duplication introduced by the new section, but do not perform general manuscript cleanup. Inspect related paper and primer sentences for contradictions. In particular, some existing wording says bootstrap containment of rounding noise is unestablished; the subsequent s5p study supports containment for its specified R construction. Explain that narrower result without assigning it to the adopted uncertainty or erasing the older estimator's failure. Keep the paper and primer concise; detailed new figures need not appear in every document.

Cite original evidence and literature accurately. Useful literature discovery routes are arXiv:1910.14654 (bias, variance and coverage comparisons) and arXiv:1505.04768 (regularization bias and interval construction). Read the originals before quoting, and do not imply that they establish this repository's empirical relationship.

Scientific claims become reportable only with committed evidence and the required ledger, run-log and workstream status records. Use existing review and result routes; add a clearly scoped synthesis record and any genuinely new measured reductions under the repository's conventions. Do not rewrite historical verdicts or hand-edit generated routing views. Keep orchestration terminology out of scientific exposition unless necessary to identify evidence.

Run `bash docs/analysis-note/build_all.sh` for note, primer and paper. Follow the current standalone synchronization procedure, including its declared sources, bibliography, figures and repository-specific wrappers. Read the source differences since the last sync, reconcile standalone-only edits, preserve its own instructions and ignore rules, build there too, and compare rendered/extracted text. Never overwrite another writer's edits. Commit explicit paths and push corresponding source snapshots to both repositories. Use the applicable branch/PR workflow; do not force-push or assume permission to merge protected/main branches. Record both remote branch names and full heads, source correspondence, build outcomes and any merge still pending. A canonical-only edit is not complete.

### Determine the missing data after analyzing what exists

Produce a gap table with: proposed claim, evidence already available, exact missing quantity, minimal study, precision target, estimated cost/basis, reuse opportunities and decision it would resolve.

For a genuine bias-variance relationship, assess a small paired experiment panel rather than a broad hyperparameter search. Candidate settings are a few iteration counts plus one targeted capacity contrast; select them from the observed trends and state that this is development-informed. The same pseudo-data, nuisance draws and MC splits should be used across settings. Keep estimator-seed effects distinguishable from event/noise variability. Reaggregate shared fine-grid outputs for reporting-resolution comparisons where valid.

Freeze corrected physical truth definitions, sample roles and estimands before any future confirmation. Include nominal and contrasting physical departures; reserve fresh seeds/truths for confirmation of a selected relationship. Existing assessment/development truths cannot become untouched validation again.

Measure ensemble bias, variance, correlations and mean squared error for each common functional, alongside detector-level agreement and cost. Noise-free bias alone cannot supply the variance axis. For interval claims, additionally specify how each experiment obtains its statistical and model-dependence interval, and evaluate width and per-functional/region coverage on the same experiments. A variance scan does not require nested bootstraps merely to estimate empirical spread; validation of a reported bootstrap interval may. Price these separately. A fixed-response truth-reweighting study does not establish robustness to a different detector response.

An initial panel around 100 paired repeats per truth is a planning example, not a frozen prescription or coverage validation. Choose sample sizes from the smallest effect worth resolving, precision of bias/spread estimates, dependence and multiplicity, and the intended coverage claim. Include sampling uncertainty and any sequential rule before confirmation. Benchmark only if separately authorized; otherwise cost from comparable measured timings with explicit extrapolation limits. Include preprocessing, storage, nuisance/interval work, verification and a repair reserve. Do not promise a precise cost from the old campaign's forecast.

Prioritize the smallest decisive measurement. New full-systematic coverage, response variations, classifier families or extensive searches are optional extensions unless the intended claim needs them. State what a null, plateau or inconclusive result would establish and terminate. Provide a concrete compute request for the selected extension; no new compute is launched under this handoff.

## Keep the running campaigns independent

The scalar campaign and its independent recomputation retain operational ownership. Do not stop, restart, requeue or alter their jobs, runners, seed sets, STOP/status files, frozen designs, production selections or pinned deployments. Do not edit their checkouts or receipt-bound code to facilitate plotting. Reduce stable copies or explicitly completed products, recording selection time and identities; never treat a growing directory as a frozen ensemble. Leave final joint claims to the terminal evaluation and verification contract.

PET, Gate 6 and declined statistical pairings are outside this task. Do not read or score blinded PET coverage outputs. No collaborator messages, publication submission, public data deposit, release tag, purchases or allocation transfers are authorized.

## Final delivery

Deliver the evidence inventory and exclusions, reproducible commands and figure/table artifacts, supported conclusions and unresolved interpretations, note locations, synchronized remote heads and build evidence, and the prioritized missing-data proposal with cost/precision assumptions. State separately whether this task's methodological synthesis is delivered, whether further empirical work is proposed, and that the original precision-measurement objective remains unmet. Do not claim acceptance by a journal or paper-wide readiness from a successful documentation build.
