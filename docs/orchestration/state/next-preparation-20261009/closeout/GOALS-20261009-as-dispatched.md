# Next sessions: closeout, engineering, and successor feasibility

These are dispatch prompts for MINERvA-OmniFold. Copy the shared contract and one numbered goal into each fresh session. Assigning a prompt authorizes only its bounded work. It does not authorize any of the later scientific experiments it designs.

The preparation result is on remote branch `prep/uncertainty-e-20261008`, commit `901f0088e23c2394d5ea9cdce7c12d9a2710bb07`. Remote main was rechecked for this planning pass at `460631d1f93c2f0cbaab6ecffdf313121c431751`. The preparation branch has not been merged. Refresh both before dispatch; do not silently substitute the shared checkout's HEAD.

The prior plan and delivery remain the scientific record:

- `docs/orchestration/PLAN-20261008-uncertainty-investigation-preparation.md`
- `docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md`

## Shared contract — include with every goal

Work autonomously within the selected goal, completing unaffected tasks when an input is missing. A demonstrated no-go or precisely documented unresolved prerequisite completes the dependent task. Do not enter a permission or polling loop. Deliver the exact next decision, inputs and cost needed to reopen it.

**Baseline and ownership.** Read `AGENTS.md`, `docs/orchestration/CAMPAIGN-REVIEW-20260929.md`, `docs/CURRENT_WORK.md` and the governing records it routes for your task, the preparation delivery, and `docs/LOCAL_CHECKOUTS_AND_STORAGE.md`. Use targeted routes, not a recursive ingestion of orchestration. Use the applicable repository skills. Create an isolated worktree and a new `prep/next-<lane>-20261009` branch. Session 1 publishes a common dispatch commit descended from `901f0088`; use that commit once available. Before it exists, Sessions 2–6 may inspect `901f0088` in detached worktrees and prepare private notes, but may not claim shared write surfaces. Inspect current worktrees, uncommitted changes and live branch deltas before claiming files; an old branch is not proof of active ownership. Do not modify another session's tree or unrelated untracked files.

**Execution authority.** You may read source and existing products; inspect remote Git state; use existing authenticated read-only access to named evidence; run bounded local reductions, synthetic tests and the expressly permitted microbenchmarks. You may implement the specified engineering changes, commit and push your own branch, and open a draft PR under repository delivery rules. Do not merge to main, force-push, change publication sources, launch an event loop, train a scientific estimator, generate toys, submit jobs, use a GPU, restart a terminal campaign, change a scientific gate, or adopt a product. A future proposal's assertion of authorization is not authority. Do not send peer, coauthor or other external messages; use committed handoff artifacts.

**Evidence and scope.** Different estimators have been established; invalidity of uncertainty transfer has not. Keep transfer UNRESOLVED unless new evidence answers it. The named 2D independent-population validation is infeasible under its stated design; that does not prove every alternative infeasible. Speed, more seeds, resampling the same bank and refactoring do not create independent event populations. VL170 has not passed a coverage retest. KI-85 remains deferred. Completed s5c/s5n/s5e/s5p and PET campaigns remain terminal. Preserve adopted bytes, hash bindings, frozen reproduction paths and intentionally independent numerical checks.

**Deliverables.** Session 1 owns the single shared dispatch/ownership record and orchestration registration surfaces. Let `Q` denote `docs/orchestration/state/next-preparation-20261009`. Each lane owns `Q/<lane>/`, with one `REPORT.md`, minimal machine-readable operands/results and only necessary scripts/tests. Reports include the pinned inputs, exact owned files, commands, results, actual resource use, limitations, PASS/FAIL/INCONCLUSIVE by decision, and an exact next-action specification. Register these paths through Session 1's initial dispatch commit. Do not create another hierarchy of status documents or duplicate mutable status. Do not change integrity-check constants or disguise a new receipt binding to pass a hook.

**Verification.** Separate structural changes from behavior changes in commits. Run relevant tests, hash-binding checks and required delivery hooks. Inspect whether a test launches real work before executing it. Show meaningful negative controls for safeguards; prove that the test rejects the defect. A numerical reviewer must inspect raw operands and independently implement consequential reductions, rather than rerun the author's script. Distinguish a passed engineering check from a scientific validation.

**Review and stopping.** One owner and at most one fresh read-only reviewer per goal; assignment of this prompt explicitly permits that one reviewer. Give the reviewer a fixed commit in an isolated clean worktree. Allow one initial review and one focused re-review after one repair batch, within the stated time and CPU caps. Session 1's review is a final closeout-delta review, not a restart of A–E's scientific review. No further worker agents or review loops. If the reviewer is unavailable, deliver INCONCLUSIVE for independent review and complete all other work. An unresolved material finding ends the affected task as FAIL or INCONCLUSIVE. Explain what could reopen it. Report model/effort only as actually observable.

**Resource caps.** Caps include review, retries and verification. Count CPU across all subprocesses and threads. Limit each local command to two compute threads and 8 GiB RAM. Use dated scratch directories; preserve required logs and remove only your own disposable scratch. Each lane may add at most 10 MiB of tracked evidence unless an existing contract demands less. The disk caps below cover new scratch/data beyond its worktree; check free space before copying. If an input exceeds the cap, stream selected operands or deliver a precise missing-evidence item. No credential repair or bulk download campaign. No local performance measurement may be reported as measured Perlmutter throughput.

| Lane | Active elapsed effort, including review | Local CPU core-hours | New scratch/data | Cluster/GPU/training |
|---|---:|---:|---:|---:|
| 1 closeout | 4 h | 2 | 1 GiB | 0 |
| 2 guard | 8 h | 4 | 2 GiB | 0 |
| 3 structure | 6 h | 3 | 1 GiB | 0 |
| 4 speed | 6 h | 4 | 2 GiB | 0 |
| 5 gbdt | 6 h | 2 | 2 GiB | 0 |
| 6 pet | 6 h | 3 | 2 GiB | 0 |

Protect the final quarter of each time/CPU budget for verification and delivery. Stop exploratory work at that boundary. These are ceilings, not targets. At a cap, write the terminal disposition from available evidence; do not extend the budget yourself.

## Goal 1 — Preparation closeout and shared ownership

**Decision:** Is the completed A–E preparation accurately documented and ready for Joseph's merge decision, with a concrete description of the remaining scientific choices?

**Inputs:** The preparation plan and delivery; frozen review at `ee61fb223668252dc571327af7678d40c3d47aee`; `Q` as defined above; `docs/orchestration/state/uncertainty-preparation-20261008/e/review.md` and `review-cycle1.md`; A's pairing assessment, B's statistical design, C's total-feasibility assessment, and D's disposition. Inspect the full delta from the reviewed commit through `901f0088`, including upstream merge `460631d1`.

**First deliverable, within 30 minutes of active work:** Publish a small dispatch commit with the common base and exact writer table. Pre-register the six report paths and required metadata using the existing mechanisms. Confirm prior lane/publication ownership from observable state. If a surface remains actively owned, exclude it and name the conflict; do not wait indefinitely or overwrite it. Publish the SHA for the other sessions to use. This bootstrap does not require finishing closeout first.

**Owned surfaces:** `Q/closeout/` and the shared writer/dispatch record; `docs/orchestration/CATALOG.md`, `MANIFEST-overrides.tsv` and generated `MANIFEST.tsv`; the existing preparation DELIVERY, A ASSESSMENT, B DESIGN and C ASSESSMENT, but only the closeout corrections below. Do not edit preserved reviewer reports or numerical receipts. Other lanes own their report subtrees and explicitly allocated source files. Publication files remain with their existing owner.

I authorize a new, narrowly scoped closeout correction of the following text, even where an old lane has exhausted its own repair allowance. This does not reopen that lane's scientific design:

1. Correct B's residual statement that N1's truth-free variant is “not ruled out.” Explain the fixed outer training bank versus both-stream inner bootstrap mismatch and the change needed to become a data-only N2-type diagnostic. Inspect the numerical premises; do not upgrade N2 to coverage validation.
2. Replace C's unsplit P09 references with the appropriate P09a estimator-identity or P09b transfer question.
3. Label A's P05 cost by its timing assumption and reconcile its interpretation with C's universe/CV-rate extrapolation. Preserve the difference between measured timings and forecasts; do not manufacture a single precise price.
4. Update DELIVERY's final upstream/merge references and assertions of file identity to describe the actual delivery tree. Check E's post-review wording changes against the reviewed evidence.
5. Prepare, in your report, exact proposed publication wording for the “keep and disclose” option, with evidence links and the relevant existing manuscript location. It must state both the distinct central/uncertainty estimators and unmeasured transfer. Do not choose that scientific/publication option for Joseph, edit the manuscript, or treat a proposed qualification as publication readiness.

**Verification:** Independently check changed factual statements against their first operands/records; verify the final diff is limited to the declared fixes. Run required hooks, route/link checks and hash bindings; regenerate the manifest from source at closeout. Give one fresh reviewer the fixed final delta, including E's previously unreviewed wording. Preserve the existing no-go and terminal campaign outcomes unless a correction to the underlying evidence is demonstrated and explicitly reported.

**Delivery and terminal:** Push the closeout branch and provide a reviewable PR, its actual base/head, remaining blockers and a short decision list. PASS means the preparation record is merge-ready within its existing scientific limits; FAIL means a demonstrated inconsistency remains; INCONCLUSIVE means a necessary source/review is unavailable. The guard and successor studies are not prerequisites for completing this PR. End after the finite review budget. No main merge, new compute, KI-85 lift, publication decision or uncertainty adoption follows.

## Goal 2 — Import safeguards and an unlaunched N2 harness

**Decision:** Can a future 2D diagnostic demonstrably execute the reviewed implementation and record its provenance, while the repository detects new checkout-hijacking imports?

**Inputs:** KI-89 and OI-136 governing records; `AUTHORIZATION-20260903-oi136-failopen-repair.md`; preparation DELIVERY §5; A's implementation and provenance tests; B's DESIGN §16.1; the two OI-136 ratchet tests; `nd-unfolding/mnv_guarded_run.py`; `docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py`. Re-measure the inventory; do not inherit a count.

**Specific authorization on dispatch:** Own the engineering disposition of the nine additional October sites identified by the preparation review. You may repair the following two live paths, their directly relevant tests, and add a new N2 harness with synthetic fixtures under `2d-unfolding/uq/coverage_fixed_truth/n2/`:

- `2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py`
- `2d-unfolding/uq/coverage_fixed_truth/ki85_compare.py`

You may make narrowly justified classification/inventory changes to `nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py` and `test_oi136_failopen_inventory_ratchet.py`. Preserve the following seven historical scripts byte-for-byte, recording their frozen role and the reason each remains exceptional:

- `docs/orchestration/state/ki84-adopt-20261006/purity_datastream_check.py`
- `docs/orchestration/state/ki84-adopt-20261006/recompute_2d_budget.py`
- `docs/orchestration/state/ki84-rebuild-20261006/boot_spreads_vl170.py`
- `docs/orchestration/state/ki84-rebuild-20261006/compare_ki84_band.py`
- `docs/orchestration/state/ki84-rebuild-20261006/predict_ki84.py`
- `docs/orchestration/state/note-boot-20261003/boot_spreads.py`
- `docs/orchestration/state/uqpaper-median-20261006/paper_median.py`

Keep the 2D driver's rooted insertion inside `main()` and the pinned `unbinned_unfolding/python/omnifold.py` bytes unchanged. Do not extend this goal to other old exceptions, edit the scanner's historical receipt, or weaken a receipt-binding verifier. If the live files themselves have newly discovered immutable bindings, implement a separate prospective entry point and preserve those files; report the narrower outcome.

**Work:** Restore an exact, explained inventory with separate frozen/live dispositions. Derive prospective module paths from the admitted checkout, use the existing guarded-execution interface, and record the actual imported module path, digest, implementation commit, effective estimator arguments and input identity metadata for each producer. Explicitly handle pre-imported modules and mismatches: fail closed before producing scientific output. A hash of a file at write time alone does not prove which code executed.

Build the N2 harness only to synthetic-test readiness. It must distinguish data resampling from conditioned MC, check event identity/disjointness and the split manifest, preserve fixed estimator settings, reject missing IDs/overlap, record missing/failed members without success-only filtering, protect existing outputs, and require an explicit admitted design/input manifest for a real launch. Do not run the identity-carrying event-loop rebuild or any statistical experiment. N2 remains a narrow data-statistics diagnostic, not total-UQ or full coverage validation.

**Verification:** Both OI-136 ratchets must pass for a reasoned inventory and fail on an injected new live rooted-insert site. Test a conflicting checkout/module, changed helper bytes, a pre-imported wrong module, missing provenance, overlapping event IDs and an overwrite attempt. Synthetic positive controls must execute the intended module and reproduce expected small-array results. Re-run KI-84 regression and relevant shared-caller tests. Inspect bindings before/after. Keep behavior and classification changes separately reviewable.

**Owned outputs:** `Q/guard/`, the named live files/tests and new `n2/` subtree. Propose any necessary guard-core change before touching it in the writer record; Session 3 cannot claim it. Supply a KI-89/OI-136 status patch in the report for the shared-document owner, not a concurrent edit.

**Terminal:** PASS means guarded synthetic execution and discriminating ratchets are demonstrated; FAIL means a reproducible bypass remains; INCONCLUSIVE means a dependency prevents demonstration. Price and name any required follow-up, then stop. No N2 registration/admission, KI-85 lift, cluster work, driver/helper re-pin or scientific claim follows.

## Goal 3 — Targeted repository consolidation

**Decision:** Which small structural changes materially simplify supported development and reproduction without changing scientific behavior or destroying independent verification?

**Inputs:** README's workstream and historical routes; `docs/POST_PUBLICATION_REORG_PLAN.md`; D's `disposition.md` and `dependencies.tsv` under the preparation state directory; the relevant entry points, actual callers and hash-binding tests. Start from D's completed findings: do not repeat its navigation census or claim it already consolidated source code. It made documentation changes only.

**Owned outputs:** `Q/structure/`, `README.md`, `docs/POST_PUBLICATION_REORG_PLAN.md`, `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`; at most two consolidation families and six existing non-frozen implementation files, plus small relevant tests. Before editing code, publish the exact file list and caller analysis in your owned report. Claim no Session-2 path, 2D production driver, pinned OmniFold helper, publication producer, receipt-bound script or other lane's namespace. If ownership is unresolved, finish the analysis and unaffected changes; do not broaden the write set.

**Work:** Quantify semantic duplication, not merely `.py`/`.sh`/`.md` counts. Trace repeated bin identities/order, normalization/flux, selection, bootstrap seed conventions, covariance centering, loader semantics and launcher arguments. Classify duplicates as shared scientific logic, intentionally independent checker, experiment-specific implementation, supported entry point, historical evidence or generated product. Measure imports and callers, including dimensional cross-imports, generator code in dimensional directories and hardcoded checkout assumptions.

Choose at most two safe, high-impact consolidations using that evidence. Prefer removing duplicated mutable defaults/conventions behind stable interfaces or making an existing entry point explicit. Preserve the mathematical and random-number behavior, public CLI and output schema. Keep wrappers where needed for supported paths. Do not introduce a universal-dimensional driver or a new abstraction merely to reduce file count. If proposed logic differs scientifically, record the difference and propose a separate behavior change rather than merging it away.

Give particular attention to D's reported-bin alignment finding: equal counts do not establish equal cell identities. Design the explicit identity contract and a permutation/omission negative control. If its implementation requires changing a pinned publication producer or regenerating scientific products, deliver that exact change specification and prerequisites; do not apply it in this structural lane. Do not silently accept legacy count-only alignment as verified identity.

For deferred directory moves/removals, update the existing reorganization plan with exact path families, inbound imports/launchers, hash/reproduction constraints, compatibility wrappers, recovery test and migration sequence. Keep the gen5d frozen predictor route discoverable. Broad layout moves remain postponed until publication freeze, and historical-family deletion requires separate family-specific authority. No file-count target and no bulk archiving.

**Verification:** Compare old/new implementations on representative existing small operands and synthetic edge cases; require identical cell identities, dimensions, normalization and seed behavior, with bitwise equality where deterministic and an explicitly justified tolerance otherwise. Preserve independent checker implementations. Demonstrate that a fresh reader can find the central producer, adopted uncertainty producer, supported prospective entry point and recovery route using the existing canonical documents. Run relevant caller tests and hash checks.

**Terminal:** PASS for a measured workflow improvement and all prioritized findings disposed as implemented or precisely deferred; FAIL for an observed semantic regression; INCONCLUSIVE for insufficient equivalence evidence. No safe consolidation is a valid terminal finding if supported by dependency/binding evidence. Deliver structural commits and a bounded remaining backlog; no broad reorganization, historical removal, scientific repair claim or publication adoption follows.

## Goal 4 — Performance feasibility before a language rewrite

**Decision:** Could an implementation change substantially reduce the cost of a specifically named future uncertainty procedure while preserving its estimator, and what is the smallest credible acceleration experiment?

**Inputs:** A's actual exact-GBT/LightGBM estimator identities, B/C's operation counts and timing operands; existing scheduler/timing/profile logs for those implementations; PET's final-design runtime records and actual TensorFlow/native backend; relevant Python and native library versions. Read official performance documentation for the actual stack. Do not infer execution language from the driver's `.py` suffix.

**Owned outputs and execution:** `Q/speed/` only. Production code, dependencies, compilers and environments remain unchanged. You may run local synthetic non-training microbenchmarks, and prototype at most two measured candidate kernels under your own namespace using already available toolchains. Cap prototype work at two active hours within the six-hour total. No scientific fits, GPU timing, cluster profiling or full transpilation. If representative profiles are absent, separate the analytical ceiling from measured evidence and specify the exact later profiling job needed.

**Work:** Decompose end-to-end cost into input loading, feature/preprocessing, classifier training, prediction, weight updates, bootstrap/nuisance orchestration, covariance reductions, process startup and storage. Identify which work already runs in compiled libraries. Assess Rust/C++ kernel replacement against simpler options such as avoiding repeated I/O, array allocation, reusable deterministic preprocessing and appropriate job packing. Caches must be keyed by every scientific input; never cache across genuinely distinct random/nuisance experiments as though they were identical.

For each candidate report measured accelerated fraction `f`, measurement regime, speedup `s`, and the Amdahl estimate `1 / ((1-f) + f/s)`. If `f` is unknown, report a range/upper bound, not an observed end-to-end gain. Show full-procedure cost at 2x, 5x, 10x and 100x speedups, including setup, memory, concurrency/billing, retries, nested replicas and independent verification. Distinguish shorter wall time from lower billed node-hours. Include development/verification cost and the repeat count at which it pays back.

Keep three categories explicit: behavior-preserving implementation acceleration; estimator/backend/precision changes needing scientific revalidation; and a different uncertainty algorithm needing a new design. Frontier code-generation capability is not performance evidence or equivalence evidence. Replacing exact GBT with histogram boosting is already an estimator change here.

**Verification:** Benchmarks use identical operands, warmup/repeats, recorded thread count and environment; verify outputs before comparing time. Independently recompute consequential speed/cost arithmetic. Rank at most two opportunities and specify a concrete follow-up benchmark with inputs, correctness tolerances, hardware, cost cap, abort rule and success threshold. Report whether even the optimistic gain changes feasibility after population and methodology constraints are reapplied.

**Terminal:** PASS for a bounded acceleration opportunity supported by representative measurements; FAIL if the measured/analytical ceiling cannot meet the stated cost target; INCONCLUSIVE if representative profiling is unavailable. A useful negative finding is completion. No blanket rewrite, production replacement, scientific equivalence claim or cluster allocation follows.

## Goal 5 — 5D GBDT successor: choose a discriminating next design

**Decision:** What new evidence could distinguish repairable estimator bias from weakly constrained truth directions, and is one small successor development experiment justified?

**Inputs:** `nd-unfolding/gbdt_model_dependence/README.md`, `PROPOSAL.md`, `definition.json`, selected `inputs/operands.npz` and inventory; terminal s5c/s5n/s5e/s5p routes and their precise prohibitions; the reconciled `PROPOSAL-20261005-scalar-measurement-successor.md`; A/B/C's preparation conclusions. The old proposal's dependency on s5p being terminal is now satisfied; it does not make the proposal authorized. Read the fine-bin confidence-set paper at https://arxiv.org/abs/2111.01091 if evaluating that alternative.

**Owned outputs:** `Q/gbdt/` only, including bounded saved-output reductions and one preregistration-ready proposal. Do not edit the old terminal records, production estimators, existing proposal or successor synthesis concurrently with its owner. No fits, toys, oracle-substitution runs or hyperparameter trials. Existing inspected outputs are development evidence.

**Work:** Define the endpoint as a joint `(pT, p_parallel, E_avail, q3, W)` measurement, with matched uncertainties and useful precision; marginals alone cannot satisfy it. Treat median total 68% half-width <=10% and model allowance <=5% as prospective development targets, not ratified gates. Verify historical operands and corrected generator inputs, distinguishing repeat variance from bias and the historical recovery proxy from an actual recovered fraction.

Use saved evidence to rank at most three explanations: classifier ratio approximation/calibration; truth propagation/acceptance/background bookkeeping; and weak identifiability of the reporting functionals. For each, specify one discriminating observation and the interpretation of either outcome. Truth-informed conditional-ratio substitutes must be estimable on independent samples and are diagnostic oracles, not deployable estimators. A finite unsuccessful ambiguity search cannot prove identifiability.

Select a minimal next diagnostic, not an automatic rerun of the roughly 70-node-hour panel. At most two intervention candidates may be specified after tying each to a measured failure; do not execute them. State exact baseline settings, independent sample roles and event IDs, fixed population truth, production-size equivalence, response/background conditioning, reporting cells, paired random draws, bias/variance/MSE/tail metrics, numerical tolerances, missing-result rules and stopping conditions. Specify which physical departures remain genuinely uninspected and what to do if none exist. New seeds on familiar departures are not untouched model validation.

If confidence-set intervals are considered, map the paper's response, constraint, noise and coverage assumptions to this problem. Identify the needed changes for uncertain response, backgrounds, high-dimensional functionals and finite MC. Treat it as a methodological benchmark or separately defined interval procedure, not an already validated rescue of GBDT.

Recompute costs from actual fit counts and timings, including sample construction, guard/identity work, calibration, confirmation, multiplicity-adjusted coverage assurance and review. Reserve 20% of the final admitted total: a subtotal `T` becomes `T/0.8`, not `1.2*T`. Keep old forecasts, measured timings and unknown costs separate. Design final coverage for intervals reconstructed by the frozen procedure in each experiment; fixed-band transfer would answer a separate question. Independently verify consequential arithmetic.

**Terminal:** PASS means one named development experiment has a defensible purpose, available inputs and a complete design ready for a separate resource decision; FAIL means existing evidence rejects the proposed route; INCONCLUSIVE means missing populations, method or measurements prevent admission. Supply an exact no-go/reopening condition when appropriate. No endpoint has been achieved, old campaign reopened, gate ratified, total covariance commissioned or compute authorized.

## Goal 6 — PET saved-output diagnosis and interval feasibility

**Decision:** Can the uncertainty of the declared PET point estimator be diagnosed from existing outputs, and what smallest new experiment would distinguish viable repairs from an unaffordable or inadequate procedure?

**Inputs:** `nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md` and its protocol/amendments; `nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md`; `nd-unfolding/pet/generator_diagnosis/REPORT-20261006.md` and its review disposition; saved member/experiment summaries and their manifests; `PET_UQ_REMEDIATION_STATUS.md`; OI-126's ruling and the Gate-6 receipt `docs/orchestration/state/gate6-member-trajectories-result-56847059.json`.

Retain the exact Gate-6 prohibition keys when discussing that family: `do_not_select_passing_subset`, `do_not_construct_C_ML`, `do_not_move_central`, `do_not_start_leg_2`, `do_not_retry_unchanged`. This is a new saved-evidence/successor-design task, not a resumption of Gate 6 or the final-design campaign.

**Owned outputs and execution:** `Q/pet/` only. Local reductions of existing, already inspected outputs are allowed within the caps. No training, new pseudo-experiments, crossed pilot, architecture search, GPU use or reconstruction of missing products by refitting. Do not open sealed reserve data or relabel previously inspected final cases as untouched validation. If raw members are unavailable within the data cap, use available summaries for the questions they actually identify and record what remains unresolved.

**Work:** Treat H2S1T24 at iteration 5 as a starting candidate, not a selected default or a broadly qualified winner. Reconcile its original point-rule outcomes with their uncertainty/dependence qualifications and the later generator diagnosis. The latter measured detector-step fitting and missed-event extrapolation deficits. The interval task must not assume those biases disappear when widths are fixed.

Reconstruct the exact six-member central and interval formulas, including bootstrap streams, seed sharing, finite-member factors, transformations, normalization and conditioning. Reanalyse between-experiment signed residuals and widths, within-experiment member variation, asymmetry and misses by aggregate/good/moderate/low-acceptance regions. Distinguish fixed population truth from each experiment's fluctuating finite-sample truth. Quantify which terms are identifiable from the existing design. The law of total variance does not justify dividing widths by sqrt(6); member dependence, bootstrap design and bias matter.

Propose at most two interval strategies for an explicitly fixed estimator. One benchmark should explain what bootstrapping the whole reported six-member estimator entails. A reusable signed-error/scale calibration is allowed as a proposal only with independent calibration data, calibration uncertainty and comparison to the full procedure. Consider asymmetric intervals or bias correction only with their assumptions and validation specified. The unfolding bias-correction precedent at https://arxiv.org/abs/1505.04768 is motivation, not validation of PET.

Design the smallest crossed experiment that distinguishes the relevant internal-randomness component from data/MC sampling. Assess the suggested 24 six-member experiments plus eight repeated ensembles; derive whether those counts can answer the variance/interval question before recommending them. Reprice its 192 unfolds from the relevant measured timing and packing, with a protected 20%-of-total verification reserve. Do not run it. Also price the next calibration and final-validation stages, including full nesting, multiple physical/response cases and failed members; a cheap pilot cannot stand in for an affordable final procedure.

Specify independent population/event-identity construction, sample-size equivalence, background/response conditioning, low-acceptance targets, exact proposed coverage/width gates and multiplicity-adjusted assurance. The suggested 0.63/0.92 lower bounds are proposed tolerances, not existing rules. If low acceptance fails, a full-domain candidate fails; a restricted fiducial result is a different endpoint requiring explicit scope approval. Distinguish a signal-only simulation milestone from a data measurement with total uncertainty.

**Verification and terminal:** Independently reproduce consequential saved-output reductions, variance/cost arithmetic and sample-size calculations from operands. PASS means a specific interval question and feasible discriminating experiment are ready for separate authorization, with point-estimator limitations carried forward. FAIL means a demonstrated incompatibility or unaffordable complete procedure; INCONCLUSIVE means the needed components cannot be identified from available outputs/populations. Finish with that conclusion and exact reopening conditions. No PET adoption, claim of useful total uncertainty, new training or revival of the terminal campaigns follows.

## Execution order and writer map

Start Session 1 first. Once it pushes its small baseline/ownership commit, Sessions 2–6 can proceed concurrently in separate worktrees. They do not wait for the closeout PR to merge. Read-only inspection can begin sooner at `901f0088`. Serialize shared-code ownership and integration, not all investigation.

| Session | Can start with | Dependency before finalizing | Exclusive writes beyond own report subtree |
|---|---|---|---|
| 1 closeout | `901f0088`, refreshed remote state | Fixed closeout delta and fresh review | Preparation text corrections; shared dispatch, catalog and manifest surfaces |
| 2 guard | Common dispatch pin | Binding/owner audit; synthetic guard evidence | Two live October producers, named ratchets/tests, prospective N2 subtree |
| 3 structure | Common dispatch pin and D's inventory | Exact source ownership; equivalence evidence | Three named navigation/reorg docs and at most two recorded code families |
| 4 speed | Common dispatch pin and A–C timing records | Actual stack/profiles; full-procedure cost; retain unresolved input gates | Its own prototype/benchmark namespace only |
| 5 gbdt | Common dispatch pin and terminal GBDT records | Independence/identity audit; guard requirements; cost sensitivity from 4 if available | Its own analysis/proposal namespace only |
| 6 pet | Common dispatch pin and terminal PET plus later diagnosis | Saved-member availability; independent-population design; cost sensitivity from 4 if available | Its own analysis/proposal namespace only |

Sessions 5 and 6 may use baseline timing forecasts if Session 4 has not finished. Label them and state the speedup needed; missing speed results do not require waiting. Sessions 2 and 3 may share findings through pushed reports but may not silently take each other's files. Session 1 finishes its closeout without waiting for all successor investigations, and later integration remains with that designated owner, through a separate bounded dispatch if needed. None of the six becomes an indefinite coordinator.

All six can be open, but run at most three CPU/data-heavy commands across them at once on this laptop; budget at most six compute threads and 24 GiB combined RAM. If coordination cannot enforce this, run the benchmark/reduction parts of 4, 5 and 6 sequentially. Read-only source/design work can continue in parallel. Check actual free disk and memory before choosing concurrency.

## Final decision rubric

A later integration owner evaluates fixed outputs, not conversational summaries:

1. **Record integrity:** closeout reconciles the reviewed tree and actual delivered commit; routes and bindings pass; no unresolved material claim is hidden.
2. **Executable provenance:** prospective producers prove which implementation ran; a conflicting checkout, wrong digest or missing identity fails closed.
3. **Estimator definition:** central and uncertainty refer to the same declared procedure, or a specifically identified transfer remains an explicit unmeasured question.
4. **Independent inputs:** the proposed experiment has genuine population/identity separation at the required scale, or its conditional/narrower scope is explicit. Random seeds are not an independence certificate.
5. **Statistical claim:** each experiment gets its own defined interval, unless fixed-band transfer is deliberately the target; fixed truth, nuisance conditioning, region claims, missing results and assurance are specified.
6. **Feasibility:** counts, measured/extrapolated timings, billed resources, full nesting, storage and protected verification reserve are priced. An implementation speedup is applied only to the portion it actually accelerates.
7. **Structural preservation:** supported workflows are clearer, equivalent behavior is demonstrated, and independent checks/frozen paths survive.
8. **Review:** one independent fixed-artifact review and bounded repair have resolved material findings, or the outcome is explicitly inconclusive.

The integrated conclusion is one of: ready to request authorization for an exactly named benchmark/development experiment; not ready because of named defects; or infeasible under stated constraints. A preparation PASS is never scientific adoption. The publication pairing decision, lifting KI-85, new compute, new scientific gates, broad layout changes and historical-family removals remain separate decisions.
