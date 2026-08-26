# PET Gate-6 method-development strategy — 2026-08-25

## Scope and answer

This is a **PET diagnostic and method-development strategy**, not a publication uncertainty,
central-value, or adoption proposal. The existing Gate-6 family remains
`BLOCK_GATE6_ML_ENSEMBLE` under its original rule regardless of every plot and interpretation in
this document. Nothing here reclassifies a member or loosens the old gate.

For future method development, strict step-by-step monotonicity plus a final ten-percent scalar
normalization band is **not the most informative convergence criterion**. It is a useful global
normalization guard, but:

1. zero-tolerance monotonicity penalizes stationary optimization noise;
2. the `0.10` came from an iteration-0 diagnostic-label branch in
   [`step1_increment_trajectory.py`](../../nd-unfolding/pet/step1_increment_trajectory.py), not a
   final-iteration tolerance calibrated against closure or a process floor; and
3. one global mean cannot establish local fold-forward agreement, classifier optimization,
   event-weight stationarity, calibration, or usable effective sample size.

The recommended *prospective* criterion is therefore a vector of measurements: optimization
adequacy for each reco/truth fit; stationarity of per-event log-weight increments; held-out
fold-forward response/calibration; effective sample size and cap occupancy; and global
normalization as a guard. Tolerances should be calibrated before a new family from fixed-policy
replicates and injected closure, rather than inferred from the five old members. That proposal
changes no historical verdict.

## Three questions that must not be collapsed

| question | measured object | what a positive result establishes | what it does **not** establish |
|---|---|---|---|
| **Training convergence** | losses, checkpoint dependence, iteration-to-iteration weight changes, response, ESS and global normalization for one frozen estimator | the finite optimizer has reached a prospectively defined stable regime | that weighted and literal resampling implement the same estimator; that any interval covers |
| **Estimator equivalence** | a controlled contrast between two implementations of the same declared resample | whether representation alone materially changes target, push or extraction | that either implementation has converged under other hyperparameters; that its intervals cover |
| **Interval coverage** | repeated pseudoexperiments from known truths, each running the frozen estimator and interval procedure | the repeated-sampling containment rate for the declared truths/regions | equivalence outside the tested contract; publication adoption or coverage under untested truths |

The implications run only within each row. A looser convergence diagnostic can improve method
development, but it cannot validate a PET uncertainty. Likewise, reproducing one fixed draw under two
representations cannot validate an interval. This separation is already demanded by the current
`OI-126` end-state: the pairing was declined, PET was demoted to method development, and any
reconsideration requires estimator-equivalence **and** coverage evidence; correctly assembling a
finite covariance is a different question.

## Control-plane observation and evidence boundary

- The required live-state freshness check was run first. The repository generator reported
  `STALE :: Git: 06efa653, HEAD e428a645, HEAD^ 415d056b`; no field from the stale generated view is
  used as evidence here.
- Direct scheduler checks were attempted. `squeue` timed out without a result and `sacct` could not
  connect to `slurmdbd_service.local:6819`. Scheduler state is therefore **not asserted**. Historical
  job accounting below comes only from committed terminal receipts.
- The governing work queue and exact `OI-123`, `OI-125`, and `OI-138` rows in
  [`CURRENT_WORK.md`](../CURRENT_WORK.md) and [`OPEN_ITEMS.md`](../OPEN_ITEMS.md) were read directly,
  along with [`ND_OMNIFOLD_STATUS.md`](../../nd-unfolding/ND_OMNIFOLD_STATUS.md),
  [`PET_UQ_REMEDIATION_STATUS.md`](../../nd-unfolding/PET_UQ_REMEDIATION_STATUS.md), the
  [Gate-6 predeclaration](PREDECLARATION-20260813-gate6-member-trajectories.md), and the exact
  [member receipt](state/gate6-member-trajectories-result-56847059.json).
- Peer Mesh was requested as an optional context check, but its callable MCP tools were not exposed
  in this session. No claim below rests on worker agreement or relayed evidence.

These exact receipt prohibitions remain live:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

At initial strategy drafting, no Slurm job, `srun`, GPU training, note edit, publication change, or
primary-checkout operation had been performed. The later explicitly authorized fixed-draw attempt
and its pre-materialization guard refusal are recorded in the execution update at the end of this
document; no GPU training occurred.

### Disposition of the additional hypothesis memo

The memo was treated as unverified guidance. Every supported point below was re-measured at branch
HEAD `000c8a5fc9f16edb4f700e59101820ec27de0f1a`; no `f5978fa`-era summary is used. The current
SHA-256 operands are `net.py f793e537…`, `omnifold.py 3a2022b0…`, `dataloader.py bed9e0b3…`,
`fullevent_fps_dataloader.py e1402370…`, `train_fullevent_replica.py c92c9cc0…`, and
`train_fullevent_nominal.py 91144bee…`.

| memo point | disposition from current first-party evidence |
|---|---|
| convergence is not uncertainty validity | integrated; the three-question table makes this a hard boundary |
| audit weighted Poisson versus literal resampling | supported as a real optimization seam, audited below; material impact is unmeasured |
| one fixed-draw equivalence test | preserved as a prospective PET-v2 prerequisite, not authorized and not a reopened `OI-126` probe |
| closure versus coverage | integrated; ordinary closure is a central-estimator test, not an interval-containment experiment |
| staged coverage pseudoexperiments | integrated as a future proposal with machinery validation before power; no sample count is proposed |
| freeze a PET-v2 estimand | integrated as a design label and contract below; it is not a new adopted fingerprint |
| repeat `OI-126` containment/localization | rebutted: those probes are closed and are neither repeated nor proposed |

## Existing evidence, replotted without a new verdict

![All committed Gate-6 and fixed-policy trajectories](figures/PET-GATE6-20260825-existing-trajectories.png)

![Committed scalar, floor, and limited loss diagnostics](figures/PET-GATE6-20260825-existing-diagnostics.png)

The deterministic renderer is
[`plot_pet_gate6_strategy_evidence.py`](plot_pet_gate6_strategy_evidence.py). It refuses to render if
the exact prohibitions, blocked family verdict, or non-licensing floor verdict change.

### Varied seed/subsample family

The first artifact is the committed Gate-6 result for array `56847059`; all five trajectory-readout
jobs completed in 13:44–14:00, but the family verdict is blocked.

| member `(estimator, subsample)` | `v[0], v[1], v[2]` | old receipt result | diagnostic observation only |
|---|---|---|---|
| 1 `(42,0)` | `1.519482, 1.124001, 0.980690` | PASS | Large directed movement; not evidence that a subset may be selected. |
| 2 `(43,1)` | `1.141819, 1.152498, 1.101483` | FAIL | Final band excess is only `0.001483`, but the tier-clean 0→1 rise also fails strict monotonicity. |
| 3 `(44,2)` | `1.056478, 1.041552, 1.042650` | FAIL | Final is inside the band; the `0.001098` rise crosses best-epoch to final-checkpoint tiers. |
| 4 `(45,3)` | `0.874795, 0.825847, 0.819792` | FAIL | Moves farther below one and ends outside the band. |
| 5 `(46,4)` | `0.761441, 0.771129, 0.753477` | FAIL | Ends far below one and is non-monotonic. |

At iteration 2, the varied-family range is `0.348006`, sample SD `0.147910`, and mean `0.939618`.
Those are scalar normalization measurements, not an ML covariance or an estimator uncertainty.

### Fixed-policy process floor

The independent-process control keeps `(42,0)`, `niter=3`, `epochs=8`, batch 512, and two million
events fixed. Its five final deviations are
`0.019310, 0.004480, 0.056880, 0.032366, 0.007650`; their median is `0.019310` and maximum is
`0.056880`. Across iterations, the process range contracts `0.780014 → 0.214470 → 0.064529` and the
sample SD contracts `0.300985 → 0.086361 → 0.025065`.

The controlling [floor receipt](state/gate6-floor-replication-result-56863958.json) calls this
`FLOOR_INTERMEDIATE`: neither its seed-determined nor process-determined branch fires, and no outcome
could have unblocked Gate 6. The contraction is interesting method-development evidence; it does not
license reinterpretation of the old family.

### What diagnostics exist

| diagnostic | committed availability | what can be concluded |
|---|---|---|
| all-member global trajectories | yes, three scalar points each | normalization path and old gate operands only |
| fixed-policy process trajectories | yes, five draws × three scalar points | process dispersion of the same scalar under one policy |
| full loss histories by member and fit | no tracked Gate-6 `.pkl` histories located | no claim about best epoch, overfit, or optimization plateau by member |
| archived loss text | one distinct preserved log, six values | only `hist.history['val_loss'][0]`, despite its `Last val loss` label; not best/final loss and not a five-member survey |
| per-event iteration weights/increments | not present in the routed summary artifacts | no event-weight stationarity or tail claim |
| held-out response/calibration curves | not present | global normalization cannot substitute for local response |
| ESS, cap occupancy, tail quantiles | not present | no weight-degeneracy diagnosis |

The archived log records 13,048 reco and 7,812 truth training steps and first validation-loss entries
that decrease with iteration (`0.2188 → 0.1200` reco; `1.0932 → 0.8775` truth). This is compatible
with continued learning, but it cannot distinguish adequate optimization from undertraining because
the full histories and best/final epochs are absent. Its single-copy provenance is documented in the
[retired-worktree archive record](runs/retired-worktree-archive-20260824/PROVENANCE.md).

## Evidence-backed hypothesis matrix

| hypothesis | supporting existing evidence | counterevidence or gap | next discriminating measurement | present status |
|---|---|---|---|---|
| H1. The zero-tolerance monotonic clause is a poor stationarity test. | Member 3 changes by only `+0.001098`; for exchangeable continuous noise three points have only `1/6` probability of appearing in the required order. | The points are neither exchangeable nor tier-homogeneous, so `1/6` is explanatory arithmetic, not a p-value. | Replicated, tier-clean late-iteration slopes and event-weight increments. | Supported as a criterion-design concern; old verdict unchanged. |
| H2. The final `0.10` band is not scientifically calibrated. | Code provenance traces it to an iteration-0 label branch; the fixed-policy final maximum is `0.056880`, while member 2 misses `0.10` by `0.001483`. | The global residual remains a useful guard, and no closure-calibrated replacement band exists. | Predeclare a band from fixed-policy replication plus closure sensitivity before a changed family. | Supported as a provenance concern; not grounds to relax the gate. |
| H3. Too many epochs per fit and too few feedback iterations contribute to the spread. | Current 3×8 policy devotes 24 epoch-units per leg to three feedback cycles; the implementation warm-starts models and anneals later fits. | No per-epoch histories or 6×4 result exists. | One fixed-policy 6×4 instrumented screen, then replication only if it is interpretable. | Plausible, untested. |
| H4. Reco and truth legs require different optimization budgets. | They are distinct networks/data problems and the archived log has 13,048 reco versus 7,812 truth steps, so equal epochs already means about 1.67× optimizer updates at reco. | One shared `epochs`/patience/LR control prevents a causal leg-specific comparison. | Add diagnostic-only separate controls, then a fixed-total-budget reco/truth epoch factorial. | Strongly motivated code hypothesis, untested scientifically. |
| H5. Seed/subsample policy contributes variation beyond the observed fixed-policy process floor. | Same-policy final process range `0.064529` is much smaller than varied-member `0.348006`. | The floor verdict is explicitly intermediate, only one seed policy was replicated, and early-iteration process ranges are large; the comparison does not apportion variance causally. | Replicate a changed policy across processes and at least two seed policies. | Suggested at the terminal scalar, not established as a mechanism. |
| H6. The best/final checkpoint seam explains member 3's small rise. | Its only increase is at the mixed-tier transition and is smaller than the previously measured checkpoint effect scale recorded by the retry plan. | No committed terminal tier-clean result was located; members 2, 4, and 5 have failures independent of this seam. | CPU/inference-only tier-clean reading under a separately authorized contract, if still scientifically useful. | Unresolved and non-unblocking. |
| H7. Weight-tail collapse or local response failure drives the scalar behavior. | These are mechanisms a global mean can hide. | No committed ESS, cap, calibration, or per-event-increment evidence exists. | Instrument all of them before spending on a family. | Open; no mechanism claim. |
| H8. Poisson multiplicities carried as weights are optimization-equivalent to literal resampling. | Their full-sample weighted objectives are related representations of the same empirical resample. | Current code retains zero-weight rows, averages loss over finite batches, changes weights without changing row count, and uses sequence-dependent Adam state; equality of trained estimators does not follow. | A fixed-draw, split-before-duplication equivalence test with a predeclared materiality rule. | Not established; a real causal seam exists. |
| H9. Ordinary closure or convergence establishes interval coverage. | Both can reveal bias or instability that would threaten coverage. | Neither measures repeated interval containment; unfolding literature demonstrates that regularized point estimation and bootstrap interval coverage can separate. | Staged known-truth pseudoexperiments of the complete frozen estimator-plus-interval procedure. | Rebutted as an implication; coverage remains unmeasured. |

## Prospective convergence criterion

The old rule remains the old rule. For a **new, separately predeclared diagnostic family**, measure:

1. **Fit adequacy by leg and iteration:** full train/validation histories, best and final epoch,
   best/final prediction difference, realized LR, and whether early stopping actually fired.
2. **Event-weight stationarity:** for accepted truth event `i`,
   `z_i(k) = log(w_i(k) / w_i(k-1))`; record the weighted median, central 68%, 90th and 99th
   percentiles of `|z|`, and their evolution over a late-iteration window. Convergence should mean a
   narrow distribution centered near zero, not a particular ordering of three noisy scalar means.
3. **Held-out fold-forward response:** predeclared response residuals or classifier diagnostics on a
   validation sample, including the regions used by the PET method-development question. This is
   distinct from aggregate normalization, consistent with the `OI-125` warning that recording
   consumption-time scalars is not closure by reconstructed values.
4. **Weight health:** truth/reco ESS `(sum w)^2 / sum(w^2)`, upper-tail quantiles, fraction of weight
   mass at the cap, and the maximum finite weight.
5. **Global guard:** retain `v_k = achieved/required` and its signed residual, but replace exact
   monotonicity with a prospectively calibrated late-window stationarity interval. Estimate that
   interval from replicated fixed-policy executions; do not tune it to the old five members.

A scientifically motivated *looser scalar-only fallback* would test whether the last-window slope is
statistically compatible with zero using the replicated process floor, while retaining a separately
calibrated terminal band. It is looser about harmless ordering noise and stricter about requiring an
uncertainty scale. It is still inferior to the vector criterion because it cannot detect compensating
local distortions or weight collapse.

## Code-path audit: what is configurable and what is entangled

| control or behavior | actual path | separately configurable? | causal consequence |
|---|---|---|---|
| OmniFold iterations | driver `--niter` → `MultiFold.niter` | yes, relative to epochs | More iterations add reco→truth feedback cycles, inference passes, and warm-started refits. |
| epochs | driver `--epochs` → one `MultiFold.EPOCHS` | iteration count yes; reco versus truth **no** | Both legs receive the same epoch count despite different step counts and loss scales. |
| early stopping | engine `early_stop=10`; no driver flag | **no**, shared | With the frozen eight epochs, the driver records that patience cannot fire; in-memory predictions are last epoch while ordinary checkpoints are best validation epoch. |
| learning rate | engine `LR`; diagnostic subclass changes fit-time compile after iteration 0 | iteration dependent, but reco versus truth **no** | Iteration 0 uses `1e-4`; later fits use `1e-5`. Extra iterations add low-LR fits, not replicas of iteration 0. |
| optimizer state | each fit calls `CompileModel` | no policy switch | Model weights warm-start, but Adam is recreated; 6×4 and 3×8 are not optimization-equivalent. |
| model state | `step1_models` and `step2_models` reused after iteration 0 | separate reco/truth models | Later fits start from prior iteration weights, causally coupling iteration count to optimization. |
| split/cache | `cached = i > start` for both legs | no driver switch | Later iterations reuse cached datasets/splits; more iterations repeatedly expose the same split. |
| architecture | two PET instances, each 2 transformer blocks, 2 heads, projection 32, local `K=3`; different input widths/coordinates | reco/truth inputs differ; hyperparameters shared | Representation is leg-specific at the input but not in depth/capacity controls. |
| checkpoint/history | best checkpoint each fit; `_final` only at last iteration; `.pkl` full history written locally | not sufficient for all-iteration causal audit | Historical trajectories mix best tiers at 0/1 with final at 2; routed artifacts omit the histories. |

The implementation evidence is
[`omnifold.py`](../../omnifold_nn/omnifold/omnifold.py),
[`train_fullevent_nominal.py`](../../nd-unfolding/pet/train_fullevent_nominal.py),
[`annealed_estimator.py`](../../nd-unfolding/pet/annealed_estimator.py), and
[`net.py`](../../omnifold_nn/omnifold/net.py). Any future executable must be a new diagnostic driver
or wrapper with its own receipt and tests; editing or repinning a receipt-bound launcher is out of
scope. `OI-123` and `OI-138` require fail-closed hash/source handling and an explicit code-root
supplier, and `OI-136` requires routing through
[`mnv_guarded_run.py`](../../nd-unfolding/mnv_guarded_run.py). `OI-125` requires end-of-run diagnostic
recording without overstating it as reconstructed closure.

### Poisson-multiplicity representation audit

The present coherent replica path draws integer Poisson factors and multiplies the signal reco/truth
weights by them in
[`fullevent_fps_dataloader.py`](../../nd-unfolding/pet/fullevent_fps_dataloader.py). The measured
target remains row-aligned to the original data-plus-background inventory and records its number of
zero-weight rows. In the vendored engine:

1. [`dataloader.py`](../../omnifold_nn/omnifold/dataloader.py) scales weights but does not delete
   zero-factor rows;
2. `MultiFold.cache` constructs an index over **all** rows, shuffles it, zips every row with its
   label and weight, then forms finite batches;
3. [`net.py`](../../omnifold_nn/omnifold/net.py) computes
   `reduce_mean(weight * binary_cross_entropy)` over the batch; and
4. the model uses Adam, early stopping/checkpointing, and fixed finite train/validation partitions.

Literal materialization of the same multiplicities deletes `k=0` rows and repeats a row `k` times.
It therefore changes the number and composition of batches, examples per epoch, validation
realization, and the gradient sequence entering Adam's moment state. Assigning unique-event
train/validation membership **before** duplication prevents leakage of one event into both partitions,
but it does not make the two optimizer paths identical. Even a constant rescaling of a full-batch
objective would not prove equality here because minibatch compositions differ.

This audit establishes a **mechanism for non-equivalence**, not a measured discrepancy in PET push or
cross section. It supports a controlled test; it does not license calling the current bootstrap
invalid.

### Freeze one PET-v2 estimator before tuning

`PET-v2` below is a strategy label only—not an implemented fingerprint, central value, or adopted
uncertainty. The memo calls the whole bundle an estimand; more precisely, the target and reporting
mask define the estimand, training/sampling/stopping semantics define the estimator, and the
bootstrap/interval construction defines the inference procedure. All three must be frozen together
in one analysis contract before tuning or equivalence work:

| contract axis | required frozen content |
|---|---|
| target | source/target digests, target construction and refinement, background treatment, class-ratio normalization, and coherent draw streams |
| loss normalization | exact weighted-BCE reduction, loader total-weight normalization, batch size, and treatment of zero weights |
| sampling semantics | weighted multiplicities with retained rows **or** literal delete/duplicate materialization; split-before-duplication rule if literal |
| stopping/optimization | reco/truth epoch budgets, patience and restore behavior, LR schedule, optimizer/reset semantics, warm starts, iteration count, checkpoint tier, and all seeds |
| feature contract | reco/truth features, normalization, point-cloud padding/mask semantics, coordinate columns, and PET architecture/pretraining state |
| estimand/extraction | truth domain, bin/projection definitions used for diagnostics, acceptance/native-miss policy, POT/flux normalization, central vector, and fixed reporting mask |
| interval procedure | resampled streams, centering, covariance/interval construction, finite-ensemble treatment, and intended pointwise or simultaneous coverage target |

The current code explicitly separates the feature fingerprint from the training policy. PET-v2 must
bind both plus the sampling and interval semantics, or two mechanically different estimators can
truthfully carry the same feature label.

### Fewer reco/truth epochs but more OmniFold iterations

The clean first comparison is 3×8 versus **6×4**, because both schedule 24 maximum epochs per leg.
It directly asks whether more feedback cycles are more useful than longer within-cycle fitting.
However, it is not a fixed-compute identity:

- reco has about 1.67× as many optimizer steps per epoch as truth in the archived run;
- 6×4 has five low-LR cycles after iteration 0, while 3×8 has two;
- each added cycle recreates optimizer state, performs full reco/truth reweight inference, and feeds
  the result forward; and
- patience 10 is inert in both schedules unless a new explicit early-stopping policy is introduced.

Thus 6×4 is a causal **iteration-versus-within-fit-budget intervention**, not merely a faster form of
3×8. It is the smallest useful changed screen. A later reco/truth epoch asymmetry test should only
follow after the driver exposes `epochs_reco`, `epochs_truth`, `patience_reco`, `patience_truth`, and
realized schedules separately.

## Prospective fixed-draw estimator-equivalence test

The current `OI-126` row already preserves this concept as an **explicit no-run/no-compute contingent
subtest**. Because `OI-126` is ruled and closed, this strategy does not activate that contingency or
reopen its containment, localization, target-factor, extraction, or occupancy probes. The design can
be reused only under a new PET-v2 method-development decision.

### Minimal design

- Freeze one complete Poisson draw `k` over data, signal and background inventories.
- **Arm W:** current representation—integer multiplicities enter the target/training path as weights;
  zero-weight rows remain present.
- **Arm L:** the identical `k` is materialized literally—delete `k=0`, duplicate each row `k` times.
  Assign each original unique event to train or validation **before** materialization.
- Hold the mathematical target recipe, feature contract, initialization, batch size, LR, optimizer,
  epoch/stopping policy, OmniFold iterations, extraction, and random streams fixed where the
  representation intervention permits. Batch composition and optimizer history are outcomes of the
  intervention and must not be forced equal after the fact.
- First run a deterministic CPU/small-fixture machinery test: factor replay, unique-event split
  integrity, duplicate aggregation, target normalization, extraction identity, and guards with
  positive/negative controls. It is not a scientific result.
- Only after that machinery passes, a separately authorized full fixed-draw comparison would record
  target summaries, every loss/checkpoint history, per-event push after mapping duplicates back to
  unique IDs, global normalization/ESS/tails, and extracted projections in three already-declared
  response regions: low `p_parallel < 6 GeV`, `6–20 GeV`, and `>20 GeV`. These fixed regions avoid a
  new localization search.

A numeric material-equivalence tolerance for push and each projection must be set **before** any
full run, using deterministic replay/numerical precision and a separately justified scientific
materiality scale. No threshold is invented here. Terminal readings are limited to
`EQUIVALENT_AT_PREDECLARED_RESOLUTION`, `MATERIALLY_DIFFERENT`, `MIXED`, or
`INVALID_OR_INCOMPLETE`. None validates coverage, selects a central, constructs a covariance, or
authorizes a family.

## Primary literature and implementation sources

Only primary papers and author-maintained implementation sources were used for this table.

| source | primary-source observation | implication here; not a prescription |
|---|---|---|
| [Original OmniFold paper, arXiv:1911.09107](https://arxiv.org/abs/1911.09107) | Defines the iterative detector/truth likelihood-ratio construction. | Iteration count is an algorithmic feedback control, not interchangeable with classifier epochs. |
| [Original authors' OmniFold implementation](https://github.com/ericmetodiev/OmniFold/blob/master/omnifold.py) | Exposes an iteration count, reuses step models across iterations, and applies common fit arguments to the two steps. | Warm starts and common leg controls are established implementation choices, not evidence that this MINERvA PET problem is optimized at 3×8. |
| [Neutrino OmniFold study, arXiv:2504.06857](https://arxiv.org/html/2504.06857) | Uses weighted BCE, Adam at `1e-4`, batch 1024, 80/20 train/validation, early stopping after 15 stagnant epochs with best-weight restoration, warm starts, and studies up to 50 iterations. It also proposes monitoring distributions of per-event weight changes over the last iterations when truth is unavailable. | Supports instrumented loss/best-weight handling and event-weight stationarity. Its truth-level χ² plateau and numerical hyperparameters are problem-specific and cannot be transplanted as a MINERvA gate. |
| [Maintained implementation vendored here](https://github.com/ViniciusMikuni/omnifold/blob/main/omnifold/omnifold.py) | Provides the shared `niter`, `epochs`, LR, and early-stop API that the local audited engine follows. | Confirms the present coupling is implementation-level; a leg-specific causal study requires an explicit wrapper or API extension. |
| [OmniLearn/PET paper, arXiv:2404.16091](https://arxiv.org/abs/2404.16091) and [author implementation](https://github.com/ViniciusMikuni/OmniLearn) | Establish the pretrained transformer/point-cloud model and fine-tuning implementation family. | Motivates PET initialization/architecture as a controlled hyperparameter axis; it does not provide a MINERvA-specific convergence band or epoch/iteration optimum. |
| [Efron's original bootstrap paper](https://doi.org/10.1214/aos/1176344552) | Defines resampling from the empirical distribution to estimate a statistic's sampling distribution. | The statistic/estimator must itself be fixed. It does not prove that two finite stochastic optimization implementations are the same statistic. |
| [Adam, arXiv:1412.6980](https://arxiv.org/abs/1412.6980) | Adam updates use adaptive estimates of gradient moments and are designed for noisy stochastic objectives. | A changed minibatch/gradient sequence can change optimizer state even with related aggregate objectives. |
| [Neyman's interval construction](https://doi.org/10.1098/rsta.1937.0005) | Defines confidence through repeated-sampling behavior. | Coverage is an ensemble property of the complete interval procedure, not a property of one closure or one covariance matrix. |
| [Kuusela–Panaretos unfolding UQ, arXiv:1505.04768](https://arxiv.org/abs/1505.04768) | Demonstrates in an unfolding problem that regularization bias can make standard bootstrap intervals miss nominal frequentist coverage, and evaluates a correction by simulation. | Primary reasoning evidence that central-estimator behavior and interval coverage must be checked separately; it is not a PET prescription or a note citation requirement. |
| [Simulation-based calibration, arXiv:1804.06788](https://arxiv.org/abs/1804.06788) | Validates Bayesian inference machinery through simulated data and rank diagnostics. | Only the workflow lesson is used here: validate machinery before scientific calibration. PET coverage remains a frequentist known-truth pseudoexperiment question, not Bayesian SBC. |

## Future interval-coverage proposal—not authorization

Ordinary closure asks whether the central estimator recovers a known or injected truth under a
specified response. It can expose bias and is necessary method validation, but it does not count how
often a constructed interval contains truth. A PET-v2 coverage campaign would instead proceed in
stages:

1. **Freeze the object.** Lock the PET-v2 estimator, truth-generating ensemble, interval construction,
   reporting mask, target coverage level, regions, and whether the claim is pointwise or simultaneous.
2. **Mechanics validation.** Use deterministic analytic/toy fixtures and a deliberately small number
   of end-to-end pseudoexperiments to prove seed replay, truth bookkeeping, target construction,
   interval endpoints, containment counting, masks, failure handling, and absence of train/validation
   leakage. This stage may find software defects; it must not report a coverage decision.
3. **Pilot for costing only.** Observe runtime, failure rate, interval degeneracy and variance needed
   for power design. Do not estimate or declare adequate coverage from the pilot.
4. **Power predeclaration.** Choose the smallest undercoverage worth detecting, allowable Monte Carlo
   error, multiplicity correction/region aggregation, and a binomial confidence-interval rule. Derive
   the required pseudoexperiment count from those operands. No sample count in a memo or this strategy
   authorizes compute.
5. **Adequately powered campaign.** For every known-truth pseudoexperiment, rerun the complete frozen
   target, training, extraction and interval construction; record containment indicators and failures.
   Report coverage with Monte Carlo uncertainty for every predeclared point/region and the simultaneous
   target if one was claimed.
6. **Independent replay.** A separate implementation verifies containment bookkeeping and a subset of
   end-to-end seeds before any scientific interpretation.

Every stage remains PET method development. Even nominal coverage on the chosen truth ensemble would
not by itself authorize publication adoption, `C_stat`, `C_ML`, a central move, or an uncertainty
claim outside the tested contract.

## Ranked prospective experiments

No item is authorized to launch by this document. The order is changed because tuning an estimator
whose sampling semantics remain open can optimize an object that is later redefined.

1. **Freeze PET-v2 and validate equivalence-test machinery on deterministic CPU fixtures.** No GPU;
   no coverage or scientific verdict.
2. **One fixed-draw weighted-versus-literal equivalence test.** Only after a numeric materiality rule,
   executable contract, resource estimate and Joseph's separate authorization. It precedes any new
   statistical or ML family and preferably precedes convergence tuning so the tuned estimator is the
   chosen one.
3. **SC-1: one fixed-policy 6×4 instrumented screen.** Same `(42,0)`, data, target, batch, and maximum
   24 epochs per leg as the old 3×8 policy. Measure every diagnostic in the contract below. Estimated
   resource: one A100 for `3.3–4.0 h` plus less than one CPU hour; the baseline estimate is the
   measured `3.25 h` mean for four fixed-policy training draws, with allowance for extra inference
   cycles and instrumentation.
4. **Replicate SC-1 across processes.** Only if SC-1 is valid and directionally promising, run enough
   identical-policy draws to estimate the new process floor. Start with three additional draws and
   predeclare whether five total are required for a terminal dispersion reading. Approximate cost:
   `10–16 A100 h`, depending on the required total.
5. **Reco/truth epoch factorial at fixed total budget.** Compare symmetric 6×4 with leg-asymmetric
   schedules such as `(reco, truth) = (2,6)` and `(6,2)`, holding iteration count and declared
   optimizer-update accounting fixed. This isolates which leg benefits from within-fit budget;
   schedule values must be finalized after SC-1 histories are seen, then frozen before running.
6. **Iteration-window scan with stationarity and response.** At a chosen epoch schedule, inspect
   iterations 3–8 using final-tier outputs each time and predeclared stopping diagnostics. This asks
   where weight increments and held-out response plateau; it does not search for a passing old-gate
   subset.
7. **Optimization/representation ablations.** Only after the prior experiments identify a leg and
   failure mode: active early stopping with best restoration, leg-specific LR, PET depth/heads/`K`,
   or initialization/fine-tuning. Change one causal axis at a time.
8. **Coverage machinery, pilot, power design and powered campaign.** These are four separate future
   decisions following the staged proposal above, not one campaign implicitly authorized by listing
   it here.

## Predeclaration-style contract for SC-1 (design only; do not launch)

### Identity and question

**Contract ID:** `PET-G6-SC1-6x4-DIAGNOSTIC-20260825`

**Question:** At fixed seed/subsample `(42,0)` and fixed maximum 24 epochs per leg, does redistributing
training from 3 OmniFold iterations × 8 epochs to 6 iterations × 4 epochs produce a stable,
well-instrumented late-iteration trajectory without evidence of loss, response, ESS, or cap
degradation?

This is a one-run method-development screen. It cannot establish convergence, coverage, or a family
uncertainty.

**Entry prerequisite:** PET-v2 sampling semantics and the estimator-equivalence disposition must be
frozen first. Otherwise SC-1 would tune a representation that a later equivalence result could
replace. Meeting this prerequisite still does not authorize SC-1 compute.

### Frozen controls and changed axis

| item | frozen value |
|---|---|
| input artifact | `nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz`, expected SHA-256 `fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625`; recompute and stamp before authorization |
| target | SHA-256 `544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9` |
| estimator/subsample seed | `(42,0)` |
| train events / batch | `2,000,000 / 512` |
| PET | separate reco/truth instances; 2 transformer blocks, 2 heads, projection 32, local `K=3`, existing coordinate policies |
| LR | iteration 0 `1e-4`; iterations 1–5 `1e-5`, asserted at every fit |
| epoch semantics | exactly 4 maximum epochs per reco and truth fit; patience at least 4 so early stopping cannot create an unequal budget in this screen |
| only scientific intervention | `niter: 3 → 6`, `epochs per fit: 8 → 4` |
| comparison | committed `(42,0)` 3×8 trajectory and five-draw process-floor receipt; no member selection or re-verdict |

Before any launch, the input digest, environment lock, guarded-run contract, unique output namespace,
and new diagnostic driver/launcher digests must be filled rather than inherited from frozen launcher
defaults. The executable must save a final in-memory checkpoint at **every** iteration and must not
overwrite any old artifact.

### Measured quantities

The primary method-development readout is the joint trajectory

`Q(k) = {v_k-1, median(z_i(k)), q90(|z_i(k)|), q99(|z_i(k)|), ESS_truth(k), ESS_reco(k), heldout_response(k)}`

for `k=0..5`, with `z_i(k)=log(w_i(k)/w_i(k-1))` for `k>0`. Record, without categorical substitution:

- signed `v_k-1`, `|v_k-1|`, and successive change;
- full train/validation loss histories, best and final epoch/loss, realized LR, checkpoint tier, and
  best-versus-final prediction discrepancy for every reco and truth fit;
- signed and absolute event-weight-increment quantiles, non-finite count, upper weight quantiles,
  maximum, cap count and cap-held weight fraction;
- truth and reco ESS and their fractional iteration-to-iteration changes;
- predeclared held-out fold-forward residuals/calibration using one hash-bound validation membership;
- end-of-run realized policy and code/data/target/environment provenance.

### Terminal interpretations

The receipt must choose exactly one data-quality branch first:

- **VALID_DIAGNOSTIC:** every provenance assertion passes, all six iterations complete, every
  in-memory-final checkpoint round-trips, and every listed quantity is finite and present.
- **INVALID_OR_INCOMPLETE:** otherwise. This supports only fixing the instrument or execution defect;
  it says nothing about the 6×4 scientific hypothesis.

For a `VALID_DIAGNOSTIC`, report one of these non-gating scientific readings:

- **SUPPORTS_REPLICATING_6x4:** terminal `|v_5-1|` is no larger than the existing fixed-policy maximum
  `0.056879520593924426`; late `q90(|z|)` narrows rather than expands; the signed increment median
  moves toward zero; held-out response does not worsen; and neither ESS nor cap diagnostics degrade
  over the last two iterations. These are a conjunction—one good scalar is insufficient.
- **DOES_NOT_SUPPORT_REPLICATING_6x4:** terminal normalization is outside that reference envelope or
  any late weight/response/ESS/cap diagnostic moves in the adverse direction.
- **MIXED_OR_UNRESOLVED:** the directions conflict or terminal changes are comparable to the measured
  process scale (`F_sd = 0.02506515073050877`). This does not default to success.

The `0.056880` envelope and `0.025065` scale are explicit comparisons to existing fixed-policy
measurements, not new convergence or physics tolerances. Even `SUPPORTS_REPLICATING_6x4` authorizes
only a request for a replicated diagnostic contract; it is not a pass.

### Resource estimate and stop conditions

- Planned request if later authorized: one A100, `4 h` walltime target with a separately justified
  safety margin, normal CPU/memory needs, and less than one CPU hour for receipt/plot validation.
- Stop without retry on any provenance mismatch, non-finite output, missing all-iteration final
  checkpoint, unasserted LR, output collision, source-root ambiguity, or guarded-run failure.
- A failed or timed-out run may be redesigned, but **must not be retried automatically or unchanged**.

### What every possible terminal result cannot authorize

Every result—valid, invalid, favorable, adverse, or unresolved—leaves Gate 6 blocked and cannot:

- select a passing subset;
- construct `C_ML` or any full-event total covariance;
- move or adopt a central value;
- start Leg 2;
- retry the old family unchanged;
- reclassify any member or retroactively reinterpret the old monotonic-plus-ten-percent gate;
- establish estimator coverage, publication uncertainty, or a publication claim;
- edit the note or change PET's diagnostic/method-development scope; or
- launch a replicated family or any further compute without Joseph's separate decision.

## Decision requested from Joseph before compute

Please decide the **sequence**, not a job count: (1) approve PET-v2 estimand freezing and the
deterministic CPU equivalence fixture; and (2) decide whether a separately predeclared one-draw
weighted-versus-literal equivalence test is required before SC-1 convergence tuning. The recommendation
is yes to both prerequisites because representation semantics can change the optimizer being tuned.
This request authorizes **no GPU run, no pseudoexperiment count, and no `C_stat`/`C_ML` campaign**;
resource and numeric equivalence thresholds must return for a separate decision before compute.

### Decision received 2026-08-25

Joseph approved the recommended sequence. The CPU-only first stage is now governed by
[`PET-V2-EQUIVALENCE-FIXTURE-CONTRACT-20260825.md`](PET-V2-EQUIVALENCE-FIXTURE-CONTRACT-20260825.md)
and its deterministic machinery receipt. The ordering decision means a separately contracted
fixed-draw equivalence comparison precedes SC-1; it does **not** authorize that full comparison.
Its numeric materiality rule, guarded executable operands, and measured resource estimate must
return to Joseph before any compute.

### Fixed-draw proposal returned and conditional compute authorized

The required proposal is now
[`PREDECLARATION-20260825-pet-v2-fixed-draw-equivalence.md`](PREDECLARATION-20260825-pet-v2-fixed-draw-equivalence.md).
It binds seed `50000`, independent `W_A/W_B` same-arm controls and one literal `L` arm; derives the
`0.0251` same-arm cap and `0.0502` cross-arm operational margin from the committed fixed-policy floor;
and measures a 13 A100-hour expected envelope (18 A100-hour allocation ceiling) from 50 completed
target and 50 completed training scheduler records. It also records the larger inherited `0.069592`
single-effect MDE as an annotation, not a gate, because the old floor is a global scalar rather than
a regional push/extraction calibration.

Joseph subsequently authorized the CPU target/readback work and the three A100 arms on 2026-08-26,
provided every guard works as specified. The five entrypoints are now implemented, CPU-tested, and
hash-bound; the authorized ceiling is 18 A100-hours and five CPU node-hours. The controller still
fails closed before `sbatch` unless its exact proposal, clean non-primary HEAD, explicit interpreter
and artifact suppliers, five implementation hashes, resource ceiling, authorization token, and five
live prohibitions all agree. A failed target, arm, evaluation, or validation blocks its dependencies
and has no retry path. This authorization remains one fixed-draw method diagnostic: it does not
authorize convergence tuning, a family, coverage work, `C_stat`, `C_ML`, central movement, Leg 2,
note edits, or any publication claim.

### Execution update: guarded attempt `57620796`

Freshness was rechecked immediately before action. The generator reported
`STALE :: Git: 06efa653, HEAD ed8244d3, HEAD^ 45d55f13`; no stale generated field was used.
Direct Slurm observation showed the shared Milan/GPU partitions recovering from a system-wide
drain/reboot event. Slurm accepted the exact requests as `shared_milan_ss11/shared` for the CPU
stages and `shared_gpu_ss11/gpu_shared` with `Features=gpu&a100&hbm80g` for the three training arms.

The immutable preflight passed all authorization, source/input, prohibition, and resource-ceiling
checks, then submitted target `57620796`, training array `57620797`, evaluation `57620798`, and
validation `57620799`. The first-party
[`attempt receipt`](state/pet-v2-fixed-draw-equivalence-attempt-57620796.json) records the terminal
state. The target ran on `nid004112` for 3 minutes 58 seconds and failed with exit `3:0` when
`mnv_guarded_run.py` refused a lazy `pet_bootstrap` import from the primary checkout. The first
causal source was the executed `fullevent_fps_dataloader.py`, whose hardcoded `_REPO` inserted that
other checkout at `sys.path[0]`. No target artifact was published, no scientific quantity was
measured, and no GPU was allocated. The dependency-stuck downstream jobs were cancelled and were
not retried.

This is an `INVALID_OR_INCOMPLETE` machinery result, not evidence about training convergence,
weighted-versus-literal estimator equivalence, closure, or coverage. It leaves Gate 6 blocked and
preserves all five exact prohibitions.

The narrow candidate repair preserves the receipt-bound loader and instead uses retry-specific
entrypoints to remap only its known primary-root insertion to the same relative path under the
mandatory immutable checkout; the ordinary OI-136 finder remains active for every other escape. It
changes neither sampling nor training policy and keeps both production loader bindings intact. A
guarded remap-plus-lazy-import regression passes. The separate
[`changed-retry predeclaration`](PREDECLARATION-20260826-pet-v2-fixed-draw-equivalence-changed-retry.md)
and [machine-readable proposal](state/pet-v2-fixed-draw-equivalence-changed-retry-proposal-20260826.json)
retain the same seed, measured quantities, `S=0.0251`, `M=0.0502`, deterministic/same-arm controls,
and 13 expected/18 ceiling A100-hours. Joseph explicitly authorized the named changed retry on
2026-08-26 after its bounded scope and preflight-before-submission sequence were restated. The
machine-readable proposal is therefore `launchable: true` only after every frozen guard passes from
a pushed clean non-primary checkout. The prior authorization remains exhausted, the new decision
covers this attempt only, and there is no further retry path.

### Authorized changed-retry submission

The final no-submit controller preflight passed at pushed head
`9bbd26ccb72ecabdd9698f679626aaa906be8faf`, including the authorization, source/input hashes,
five exact prohibitions, and resource ceilings. The ROOT worker shell then loaded successfully, and
the guarded retry target's observed checkout modules all resolved from the clean detached
non-primary checkout. The controller submitted exactly one dependency chain at
`2026-08-26T18:51:08.242459+00:00`: target `57626676`, training array `57626678`, evaluation
`57626679`, and read-only validation `57626680`. The exact
[`submission receipt`](state/pet-v2-fixed-draw-equivalence-changed-retry-submission-57626676.json)
records proposal SHA-256 `c1e63e90c720ef4b353e570c2a0735450712cc135850176cdb73ff4888acf43b`,
`no_retry_path: true`, and null `C_stat`/`C_ML`.

The initial direct scheduler observation found the target pending only for shared-Milan resources
during a system-side node drain; all downstream jobs were dependency-held and no allocation had
occurred. This is a submission event, not a PET result. A terminal attempt receipt and validation
are still required before any measured quantity is interpreted. Existing Gate 6 remains blocked
and all five prohibitions remain in force.

### Retry-1 terminal and authorized retry-2 design

After the shared-Milan drain released, target `57626676` ran for 4 minutes 15 seconds and failed
before publishing a target. The checkout-root repair itself worked: two paths were remapped, the
OI-136 guard did not refuse, and all six observed repository modules came from the detached
`9bbd26cc` checkout. The next import, `omnifold.dataloader`, executed `omnifold/__init__.py`; that
initializer imports the TensorFlow training engine, which is unavailable in the ROOT Python 3.11
environment. The three downstream jobs were cancelled with zero allocation. The committed
[`attempt receipt`](state/pet-v2-fixed-draw-equivalence-changed-retry1-attempt-57626676.json)
classifies this as `INVALID_OR_INCOMPLETE`: zero A100-hours, no target, and no scientific quantity.

This is an import-side-effect defect, not evidence that target materialization needs TensorFlow.
The exact `omnifold/dataloader.py` imports only NumPy. In the exact ROOT environment, ordinary
package import reproduces the TensorFlow failure, while a target-only package shell loads and
instantiates the same dataloader at SHA-256 `bed9e0b3…` with TensorFlow absent. The guarded retry-2
target `--help` path then passes with eight observed modules under one checkout root.

Joseph subsequently stated **“Retries are authorized.”** The separate
[`retry-2 predeclaration`](PREDECLARATION-20260826-pet-v2-fixed-draw-equivalence-changed-retry2.md)
and [machine contract](state/pet-v2-fixed-draw-equivalence-changed-retry2-proposal-20260826.json)
therefore authorize changed machinery retries within this one fixed-draw diagnostic and the
existing total ceiling, never unchanged or automatic retries. Retry 2 bypasses only the unnecessary
target package initializer, hash-loads the identical NumPy dataloader, and reuses the unchanged
training/evaluation wrappers. Every scientific control, threshold, resource limit, non-authorization,
and exact Gate-6 prohibition remains frozen.

At pushed head `27df34afa195da31ed4c82accdb9a875c894c295`, every retry-2 no-submit,
ROOT-target, learned-refiner, source/input, prohibition, resource, and scheduler preflight passed.
The controller submitted target `57629029`, training array `57629030`, evaluation `57629031`, and
validation `57629032` at `2026-08-26T20:58:17.689065+00:00`. Its exact
[`submission receipt`](state/pet-v2-fixed-draw-equivalence-changed-retry2-submission-57629029.json)
records `changed_retry_number: 2`, `unchanged_retry: false`, `automatic_retry: false`, and null
`C_stat`/`C_ML`. Initial direct observation found the target pending for priority with zero
allocation and every downstream stage dependency-held; this submission event is not a result.
