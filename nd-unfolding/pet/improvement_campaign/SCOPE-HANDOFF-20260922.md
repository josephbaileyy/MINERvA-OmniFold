# PET recovery improvement: execution handoff

This is the detailed brief for Joseph's PET-improvement `/goal`. It defines a new diagnostic and method-development campaign following the completed comparison with Gregor's pretrained PET2-small. Read it with the accompanying user prompt and current canonical repository instructions. The completed comparison is evidence to investigate; the proposed explanations below are hypotheses.

The objective is to diagnose and improve recovery, establish whether additional events help, and assess the scientific basis of the adequacy reference. Complete implementation, executed experiments, independent review, and reproducible delivery. A passing model is not guaranteed; a decision-resolving negative result is legitimate.

## 1. Authorization and resources

Joseph authorizes all CPU, GPU, memory, temporary storage, source extraction, preprocessing, training, inference, validation, and artifact-preservation work reasonably necessary for the campaign defined here, using his existing authorized computing accounts and allocations.

This includes:

- Runtime verification and repair of the comparison implementation, and corrected baseline runs.
- Independent event splits, pseudodata generation, feature and architecture ablations, optimization studies, iteration studies, and ensembling.
- Learning curves that separately vary pseudodata statistics, prior-MC statistics, and training effort.
- Physics stress tests and simulation-only bias/coverage experiments for promising new estimators.
- Conditional alternative-method evaluations when earlier diagnostics justify them.
- Necessary retries, checkpoint/resume, postprocessing, builds, preservation, and independent reproduction.
- Larger samples, up to the full relevant existing inventories where measured scaling justifies them.
- Extraction of additional existing source branches needed for the energy summaries, overflow information, object types, missingness, identity, selection, and truth-validation studies described below.

There is **no additional campaign-specific GPU-hour or CPU-hour ceiling**. This authorization supersedes the earlier PET comparison's task-specific 1,000 GPU-hour ceiling and narrower per-stage approvals for work within this new campaign. Ordinary stages, justified increases in scale, and necessary repairs do not require repeated permission.

This does not authorize purchasing new cloud resources, obtaining new allocations, exceeding site quotas, or interfering with another campaign. Observe current resource availability directly. Do not cancel, hold, reprioritize, or alter another lane's jobs. Existing priority commitments remain respected.

Use the resources efficiently:

- Measure the actual end-to-end execution path before projecting costs.
- Maintain cumulative CPU/GPU usage, storage usage, and estimated remaining cost.
- Eliminate unsupported hypotheses with small diagnostics before large campaigns.
- Size final comparisons and coverage studies for declared precision.
- Do not exhaust an allocation or conduct an unbounded search merely because no task-specific ceiling is imposed.

Joseph also authorizes isolated branches/worktrees, implementation and tests, parallel specialist agents, independent reviewers, campaign commits and pushes, and a draft PR to the existing repository. Record the new authorization and extend campaign-specific manifests/guards to represent it faithfully. Do not disable provenance or execution guards. Commit branch/source manifests before new extraction, naming the branches, population, and outputs; derive these from the scientific feature requirements rather than inventing unverified branch names.

### Scientific boundaries

- PET remains diagnostic and method development.
- New simulation-only statistical/seed ensembles and coverage calculations for new candidates are authorized.
- Production `C_stat`/`C_ML` construction, Gate-6 actions, publication adoption, changes to publication central estimators, and changes to the adopted scalar-5D covariance are outside this authorization.
- Do not reopen `OI-126` or repeat its completed historical probes.
- Do not unfold real measured data into a new central result. Develop and validate on simulated pseudodata.
- Do not change the note, primer, or paper for this campaign.
- Do not message collaborators through email, Slack, or Peer Mesh.
- Do not merge the final PR into `main` automatically.

## 2. Project and durable starting state

MINERvA-OmniFold develops unbinned neutrino cross-section unfolding. The relevant PET is a particle-cloud neural classifier integrated with the TensorFlow/Keras OmniFold engine. Production compute runs on Perlmutter.

Repository: <https://github.com/josephbaileyy/MINERvA-OmniFold>

The completed comparison is on the pushed branch `pet-direct-token-comparison`:

| Object | Commit |
|---|---|
| Comparison branch head, verified when this brief was prepared | `7090fcc12ce8119f7a5fc4fa05265a8486f9049a` |
| Report, TeX, and claim-index commit | `e957461a0edc221461be28346b9ba277387255ba` |
| Campaign code commit named by the report | `68cf9d29f8ab1b0f5acd933d4baec1962b29e34d` |

These are existing repository objects, not statements that the comparison branch is merged. Verify current remote heads. Recover inputs and results through their committed manifests and receipts; never depend on the continued existence of a particular local worktree or scratch directory.

The preceding assessment was read-only: no implementation repairs, new training, or new scientific validation were performed. This handoff describes work to do, not changes already delivered.

Read current canonical `AGENTS.md`, `docs/CURRENT_WORK.md`, the relevant workstream status/reference, `KNOWN_ISSUES.md`, governing `OI-*` records, and execution/environment rules. The comparison branch contains older orientation documents; current canonical rulings govern scientific scope. This is a new authorized campaign, not an inference that the older queue already authorized it.

Do not modify another lane's staged or unstaged files. Work in an isolated checkout, preserve the comparison branch, and inspect status afterward. Coordinate integration with current canonical code without silently changing the historical comparison object.

### Artifacts to read

Under `nd-unfolding/pet/configuration_comparison/` on the comparison branch:

- `campaign_report.json`
- `CLAIM_EVIDENCE_INDEX-final_comparison.md`
- `slides/final_comparison.tex`
- `slides/final_comparison.pdf` — ten pages
- `frozen_design.py`
- `run_arm_evaluation.py`
- `training_recipe.py`
- `theirs_omnifold_arm.py`
- `reference_calibration.py`
- `characterize_regions.py`
- `score_campaign.py`
- `selection_rule.py`
- `build_theirs_inputs.py`
- `theirs_token_schema.py`
- `pretrained_init.py`
- `r4_manifest.py`
- Relevant files in `receipts/`

Related implementation:

- `nd-unfolding/pet/annealed_estimator.py`
- `nd-unfolding/pet/fullevent_fps_dataloader.py`
- `nd-unfolding/pet/closure_powered_truth_reweight.py`
- `omnifold_nn/omnifold/omnifold.py`
- `omnifold_nn/omnifold/net.py`

Prior handoffs in the comparison directory contain retractions and pre-completion states. In particular, older claims that source tuples or the pretrained checkpoint were unavailable were superseded. The final committed products supersede old statements that no comparative result exists. Verify accessibility from original manifests and source inventories instead of repeating historical absence claims. A failed top-level glob is not a covering search.

## 3. What the completed report records

Recompute these from the committed report and original outputs where accessible before using them in a new result. They are campaign measurements, not publication adoption or independent verification.

Endpoint:

- Truth `E_avail` clipped exponential tilt, amplitude `0.35`.
- The standardized coordinate is clipped at `3.0`; do not instead clip the exponential weight.
- Seven `E_avail` bins with edges `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0]` GeV.
- On normalized spectra, `R = 1 - residual_L1 / injected_L1`.
- `R = 0` means no recovery; `R = 1` means exact recovery of that histogram. The score is bounded above by one, not below by zero. Overshoot requires a separate directional diagnostic.

| Recovery | Ours | Gregor's arm | Floor |
|---|---:|---:|---:|
| Overall mean | 0.3036748666 | 0.4165265834 | 0.5559785255 |
| Low acceptance | 0.05579 | 0.15261 | 0.00838 |
| Moderate acceptance | 0.22640 | 0.41421 | 0.46592 |
| Good acceptance | 0.53810 | 0.68862 | 0.58529 |

Eight final seed pairs give `ours - theirs = -0.1128517168`, with the reported 95% t interval `[-0.1471409874, -0.0785624463]`. Gregor's arm scores higher in every pair. The recorded verdict is `NEITHER_ELIGIBLE / NO_SELECTION`.

The low-acceptance region contains about 31.03% of truth mass. Retain and report it. Low acceptance is not proof of fundamental unresolvability. The moderate-acceptance failure also prevents explaining everything by the lowest-acceptance band.

The final prior half contains about 600,000 rows. The eight pairs vary estimator seeds on a fixed event sample. This is neither a sample-size scaling study nor a full statistical uncertainty assessment.

The aggregate floor is `0.8 * 0.6949731569`, using an acceptance reference at three iterations. Regional floors are `0.6` times each region's own reference. Its construction uses `1 - (1-a)^k` and explicitly says it is a reference model, not a proven attainability or information bound. It does not fully characterize energy smearing or information lost in the representation.

Preserve the original report, inputs, thresholds, and verdict. A future recalibration does not retroactively pass the old campaign.

## 4. Source findings requiring runtime verification

Two discrepancies were identified by reading source at the campaign's recorded code state. **Neither is an established cause of the recovery deficit.** Verify the actual executed objects and policies before reporting a defect or implementing its remedy.

### A. Intended versus executed optimizer

- `frozen_design.THEIRS_COMPLETE` specifies TorchAdamW, weight decay `0.01`, warmup/cosine scheduling, and global-norm clipping.
- `run_arm_evaluation.evaluate` constructs `make_annealed_multifold(MultiFold, ...)`.
- The engine's `get_optimizer` constructs Adam; `CompileModel` supplies it to the model.
- The wrapper appears to accept that optimizer.
- Custom optimizer/schedule implementations exist in `training_recipe.py`, but the campaign driver does not appear to connect them to actual training.

### B. The truth-side recipe is not demonstrably identical

- Both arms construct the same truth-side PET architecture and inputs.
- The driver passes batch size `512` for ours and `2048` for theirs into the engine.
- The engine uses that size for both steps, changing optimizer updates per epoch.
- Check whether arm-specific selected learning rates, random-number consumption, split construction, stopping, or optimizer state create further differences.

Trace actual module resolution and method calls. Capture optimizer types and settings, learning-rate trajectories, clipping, pretrained initialization after cloning, batches, update counts, and stopping. A text search, intended configuration, or port-equivalence test does not establish that the campaign ran the tested path.

If confirmed, preserve and label the historical as-executed configuration; repair the new path; reproduce corrected baselines; and measure whether the discrepancy affects recovery. Distinguish reproduction of the old intended comparison from a new experiment that holds truth-side training fixed.

Verify input semantics through the complete preprocessing path. Earlier raw-momentum versus `eta/phi/log-pT/log-E` defects were reportedly repaired; stale comments must not lead to reintroducing or re-reporting them.

Three differences from Gregor's source remain declared in the comparison:

- Muon presence from `muon_E > 0` rather than MINOS-match selection.
- `prong_dEdXMean` substituted for `prong_part_dEdXMean`.
- A locally defined proportional token-cap split.

Verify these, resolve them where possible, and otherwise retain an honest adapted-arm label. Do not silently redefine Gregor's configuration.

## 5. Execution phases

Complete these in order, adapting later work to earlier evidence. Record changes to a protocol before evaluating its affected test sample.

### Phase A — reproducible execution and corrected baselines

1. Establish repository, branch, input, and artifact identities; inspect workspace state and protect other lanes' changes.
2. Recover the comparison and recompute headline summaries from underlying outputs where available.
3. Verify the suspected recipe discrepancies at runtime. Add regression tests for confirmed defects.
4. Verify pretrained weights survive cloning and enter actual fits.
5. Verify event identity, dual-leg weights, normalization, selection, masks, feature units, and split isolation.
6. Route compute through `nd-unfolding/mnv_guarded_run.py` and the current environment rules. Re-measure live state and query the scheduler directly before acting.
7. Create a new campaign with fresh manifests and explicit per-step configurations; preserve historical outputs.
8. For causal reco-side comparisons, control truth-side architecture, inputs, initialization policy, batches, optimizer, schedule, stopping, and splits. The truth-side training targets legitimately differ when step 1 differs; identical weights or targets are not the requirement.
9. Measure costs under the actual engine. Bare-model/XLA timing does not automatically apply through the production optimizer path.

### Phase B — identify where recovery is lost

Execute the following, each on appropriate held-out events:

- Truth-only learning of a known `E_avail` tilt.
- Detector-level reweighting checks after step 1.
- Comparison of the pulled distribution with the truth-side step-2 output.
- Recovery trajectories across unfolding iterations.
- Learning trajectories versus classifier training duration.
- A scalar BDT or small MLP baseline with relevant physics inputs.

Separate representation loss, ratio-estimation error, optimization/stopping, finite samples, weak detector sensitivity, and reference-model assumptions. Measure what correction enters and leaves each step.

Truth-only known-weight access is a learnability diagnostic, not detector-level unfolding validation. Do not inject per-event truth weights into a detector-side oracle and call its score a physical recovery bound. Any conditional-expectation reference must respect what is observable, selection, normalization, and independent training/evaluation.

### Phase C — prioritized model improvements

The leading hypothesis is a particle-cloud model supplemented by explicit physics summaries. The existing truth-side globals are only `pt` and `pparallel`; the loader deliberately leaves available `eavail` and `q3` unused. This is a documented design choice to test, not an automatically established bug.

Start with four controlled feature arms:

1. Existing features.
2. Reco energy summaries added.
3. Truth energy summaries added.
4. Both added.

At minimum examine reconstructed `E_avail`/recoil information at step 1, true `E_avail` at step 2, existing muon kinematics, pre-truncation whole-event energy sums and multiplicities, and overflow energy/count summaries. True `E_avail` is legitimate input to the simulation-truth classifier. No truth quantities may enter the detector-side classifier.

Use the resulting evidence to rank subsequent ablations:

- Typed objects and categorical embeddings.
- Missingness and validity flags.
- Energy-preserving overflow treatment.
- Modest width/capacity changes.
- Duration, schedules, and regularization.
- Pretrained versus scratch initialization with matched inputs.
- Step-level or full-run ensembling.

Evaluate density-ratio performance, not classification ranking alone: weighted losses, held-out reweighting residuals, weight tails, effective sample size, regional recovery, and initialization sensitivity. For positive weights, `(sum w)^2 / sum(w^2)` is a useful ESS diagnostic; do not extend its interpretation to signed weights without justification.

Do not presume that capacity, weight decay, clipping, ensembling, or more iterations removes bias. Preserve detector geometry and the actual visible-energy definition. Do not impose collider symmetries or full-energy conservation constraints that do not apply to this detector and neutrino final state.

### Phase D — determine whether more events help

For the strongest few candidates vary separately:

1. Pseudodata statistics with prior MC fixed.
2. Prior-MC statistics with pseudodata fixed.
3. Training effort with both event counts fixed.

Use at least three informative sample sizes where feasible, independent event-draw repetitions, and a common untouched evaluation population. Distinguish fixed-compute scaling from sufficiently trained scaling: increasing events at fixed epochs also increases optimizer updates.

Seed repetitions are not new events. Do not infer infinite-data behavior from a few nested subsets of one draw. Report tested ranges and uncertainty. Increase events or repetitions when the achieved precision can resolve the alternatives. If a limit remains, quantify it rather than asserting that more data must fix it or cannot help.

### Phase E — physics robustness, reference calibration, and coverage

Predeclare distortions beyond the development tilt:

- Both signs and several magnitudes of an energy distortion.
- At least one different energy-shape distortion.
- Hadronic multiplicity/topology changes.
- Available generator or interaction-model variations, including relevant final-state effects.
- Joint distributions and regional behavior, not only the seven-bin marginal.

Separate truth-model changes from detector-response changes. Use independent alternatives where available; document origins and limitations. Same-response closure does not establish robustness to detector mismodeling.

Measure whether tested truth changes produce distinguishable selected reco distributions. Low acceptance by itself is not an identifiability measurement. A lack of measured power must not be reported as an impossibility result.

Assess the acceptance reference against actual response/migration and controlled high-statistics or known-function diagnostics. Preserve original thresholds for like-for-like comparison. Any new reference or threshold is a prospective recommendation tied to residual physics bias and coverage, not a retroactive adoption decision.

For a promising final estimator, execute simulation-only bias and coverage validation at the actual recommended configuration. Predeclare the ensemble construction, statistical/systematic sources varied, nominal coverage levels, and required Monte Carlo precision. Tests at reduced scale or a different estimator do not certify the final configuration. Do not spend a large coverage campaign on a candidate already demonstrably inadequate under the declared criteria.

These new validation ensembles are distinct from the declined historical pairing and are expressly authorized. They do not become adopted production uncertainty products.

### Phase F — conditional alternative methods

Read current primary papers and upstream implementations. If simpler changes leave a substantial unresolved deficit:

- Evaluate AUSSIE in a bounded representative benchmark if the diagnosis points to iteration or truth-projection limitations.
- Evaluate another backbone, such as ParticleViT, if representation/pretraining evidence supports it.
- Consider nuisance-aware/Profile OmniFold where response uncertainty is the demonstrated problem.

Advance to expensive evaluations only after a representative test supports doing so. Record the evidence for trying or deferring each alternative. Do not implement every published method simply to exhaust a list.

## 6. Statistical design and stopping

Before confirmatory evaluation:

- Freeze candidate identities, inputs, training policies, event splits, seeds, endpoints, reference definitions, and stopping rules.
- State the quantity being measured and what a terminal result cannot authorize.
- Reserve fresh final-validation events not used to select features, recipes, thresholds, or candidates.
- Separate development, pilot, and final inference.
- Size repetitions using a declared precision or detectable effect; do not reuse pilot observations as ordinary fixed-design final data after they chose the sample size.
- Account for adaptive selection and multiple candidates in the confirmatory design.
- Use paired comparisons where appropriate, preserving independent event-draw structure.
- Distinguish seed variation, event-sample variation, and systematic variation.

The old non-inferiority margin was `0.02` and switching margin `0.04` in recovery units. Preserve these for comparable analyses; do not widen them after seeing a result. Interval width alone does not settle superiority or non-inferiority: apply the relevant decision inequalities.

Calibrate pilots to the intended regime. Do not assume that variance measured on a smaller stage is automatically conservative for a larger sample without evidence.

Scientific completion means either a reproducible improvement satisfying declared validation, or a decision-resolving diagnosis with measured limitations and an evidence-supported next choice. Do not promise success. Do not stop at "both failed" while authorized discriminating experiments remain. Do not continue an unbounded search after hypotheses are resolved or their practical resolution limits are demonstrated.

## 7. Research starting points

Read the full current primary sources, inspect revisions, and distinguish their demonstrated tasks from this unfolding task:

- Gregor et al., *Cross-Domain Transfer with Particle Physics Foundation Models*: <https://arxiv.org/abs/2604.12364>
- *Machine Learning Assisted Unfolding for Neutrino Cross-Section Measurements*: <https://arxiv.org/abs/2504.06857>
- *A Practical Guide to Unbinned Unfolding*: <https://arxiv.org/abs/2507.09582>
- *Unfolding without Iterations, Adversaries, or Surrogates* (AUSSIE): <https://arxiv.org/abs/2602.24282>
- *Machine Learning-based Unfolding for Cross Section Measurements in the Presence of Nuisance Parameters*: <https://arxiv.org/abs/2512.07074>

The particularly relevant hypothesis is that directly supplied observables can improve recovery relative to forcing a network to derive them. Supervised regression/classification gains from pretraining do not by themselves establish calibrated density ratios or unfolding coverage.

## 8. Required delivery

Commit and preserve:

- Intended-versus-executed configuration audit, with runtime evidence.
- Confirmed repairs, regression tests, and executed validation.
- Reproducible campaign entry point and frozen configurations.
- Input, event-split, checkpoint, code, and output manifests.
- Machine-readable results carrying ingredients and measurements, not only verdicts.
- Cumulative resource accounting.
- A scientific report answering the questions below.
- A new versioned comparison PDF and editable TeX; retain the historical deck.
- Claim-to-evidence index.
- Applicable ledger/RUN_LOG/STATUS entries for new quotable findings.
- A cold-start handoff with durable branch/commit identifiers and tested recovery routes.

The report must answer:

1. What caused the observed shortfall, and what remains unestablished?
2. Which implementation/model changes improve recovery?
3. Does more data help, over what regime, and by how much?
4. Is the original adequacy reference/floor appropriate?
5. Does any candidate satisfy retained criteria and independent validation?
6. What physics or information limitations remain?

Arrange independent implementation, statistical, and scientific-scope review. Reviewers trace claims to original artifacts and actual execution in read-only isolated worktrees. Shared measurement origins count once. Inspect reviewer worktrees afterward; do not incorporate silent edits into verification receipts.

Retain negative results and withdrawals. Rewrite the new report's recommendations from current evidence instead of copying stale component tables. The original deck's component recommendations predate its final comparison and are not automatically current prescriptions.

Push to a new branch and open a draft PR. Report the verified remote head, PR URL, artifact locations, validation results, resource use, and remaining limitations. Keep the work resumable through queue waits and context resets. Do not declare completion merely because jobs were submitted or a plan was written.

Ask Joseph only for an action outside this authorization, unavailable credentials/resources, or a material scientific ambiguity that governing sources cannot resolve. Do not repeatedly seek routine permission to execute these authorized stages.
