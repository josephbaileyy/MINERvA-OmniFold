# Bounded execution proposal: PET typed-token routing

**Prepared; not authorized.** The source-audit grant is exhausted. This proposal
requests one new grant for the synthetic campaign below. It includes no ROOT
access, source normalization, real-data training, producer correspondence,
publication adoption, covariance construction, or Gate-6 action. After approval,
covered jobs, accounting, verification and preservation can proceed without
repeated permission requests. A failed gate stops its dependent work.

## Question and controlled contrasts

Does retaining individual typed embeddings through attention improve known-ratio
recovery compared with reducing those same embeddings to family sums first?

* **C1 reference:** the existing v2 family token MLPs, sum pooling, raw counts,
  13 event columns and 51 typed columns. Existing C0/C1 is only enable/disable.
* **P bridge:** the exact same 16-wide family embeddings and raw counts; three
  family-sum tokens, a token containing the 13 globals and three counts, and
  the unchanged generic cloud enter one attention block.
* **D candidate:** identical to P except that individual typed embeddings replace
  the three sum tokens. Explicit masks, normalization and membership are identical.
  Both have 17,329 parameters at width 32. Initial trainable arrays are copied
  exactly, not merely created with the same random seed.

The implemented reference test equates P's concatenated family sums/counts with
C1's 51 columns. **P–D isolates the routing operation within a new attention
bridge. C1–P additionally changes downstream architecture.** There is no runnable
integration into `m_reco` here and no claim that P–D measures the full current-PET
versus Gregor-network difference. This deliberate staged comparison is needed
before such a result could be interpreted.

Later factorial contrasts, not included in this requested execution: (1) raw
membership versus explicit PID/energy filtering crossed with P/D; (2) prong-zero
retention versus removal and separate muon-token treatment, after associations
are known; (3) sum/raw-count versus mean/scaled-log-count; (4) matched explicit
masks versus documented upstream behavior as a diagnostic only; (5) identical
feature tensors through current PET and an audited PET2 implementation; (6) a
licensed compatible checkpoint versus random initialization of that exact model.
Change one axis at a time and publish each contrast independently. Never infer
membership effects from P–D or pretraining effects from framework changes.

## Runnable campaign

Entry point: `../run_typed_token_comparison.py`. `run-card.json` lists all 24
jobs and arguments. Each job runs both arms, with no winner-dependent selection.

| Item | Frozen choice |
|---|---|
| Inventories | 1,000,000 synthetic training rows; 250,000 disjoint test rows, shared by all arms/seeds |
| Fixture seeds | 2401 training, 2402 test; each synthetic row is one independent group |
| Model seeds | 17, 29, 43, 59, 71, 89, 101, 113; eight paired comparisons |
| Reco | 13 independent nuisance globals; 12×5 nuisance generic cloud; one synthetic photon, one blob, two typed prongs; prong time carries noisy latent coordinates |
| Truth | Same two latent standard-normal coordinates for every arm; fixed 32/32 tanh MLP; reco noise SD 0.15; no truth values in reco inputs |
| Ordinary closure | Unit target weight |
| Injected closure | Truth target `exp(0.4*tanh(z0*z1))`; known range `[exp(-0.4),exp(0.4)]`; requires a two-object relation, not event/global inputs |
| Negative control | Split-local shuffled training target weights; held-out conditional target equals their fixed training mean |
| Selection and weights | Synthetic all-pass, unit nominal weights; identical target weights; no real backgrounds or native misses. This limits transfer to a selected real analysis. |
| Fits | 3 OmniFold iterations × 2 steps × 5 epochs per fit; final checkpoint; reset to the same initial arrays at each fit |
| Optimizer | Adam, LR 0.001; batch 1,024; equal paired minibatch order; equal sampling priors, unnormalized positive/negative class weights; odds `exp(logit)` |
| Normalization | Fit once from training synthetic tokens only; shared by arms/seeds; v2 native score identity; never use held-out values to tune |
| Selection of models | Fixed architecture, epochs and final checkpoint. No hyperparameter tuning or validation-based selection; test rows are evaluated only for the frozen diagnostics. |

The target is a synthetic channel-capacity challenge, not a guaranteed
information-theoretic separation: a trained pooled encoder might retain the
needed relation. No result can prove that real data contains such a relation.
The fixed four-object multiplicity is a power-study convenience, not a measured
MINERvA distribution. Empty, unknown, masked and 90-blob cases are software tests;
this campaign cannot measure high-multiplicity learning performance.

The runner saves per-iteration metrics, both final reconstructed and truth
models, test predictions, truth targets and final training push weights. It
records the end-of-run fold-forward sums after the last Step 2, as distinct from
an intermediate consumption-time reduction. Store stdout/stderr, code and schema
hashes, full input/normalization fingerprints, environment, scheduler accounting,
closed-file checksums and an explicit terminal result alongside each job.

## Resources and hard stops

**Estimated cost: 50–240 A100 GPU-hours; hard grant ceiling 290 GPU-hours.**
This is a planning range, not a benchmark. There are 1.44 billion row-fit visits
(24 paired jobs × 2 arms × 3 iterations × 2 steps × 5 epochs × 1 million rows).
Assumed aggregate 2,000–10,000 row-fit visits/s gives 40–200 GPU-hours before
inference, initialization and preprocessing overhead. Actual throughput of the
new implementation has not been measured on A100.

* First run one calibration allocation: one A100, eight CPUs, 64 GiB, ≤2 hours;
  synthetic 32,768 training/8,192 test rows, seed 17, injected, one iteration,
  one epoch, batch 1,024. Also run the synthetic test suite. This is budget and
  execution validation, excluded from the scientific seed comparison.
* Then at most 24 jobs, each one A100/eight CPUs/64 GiB and ≤12 hours, ≤2 jobs
  concurrently. Full campaign ceiling 288 GPU-hours plus calibration 2.
* CPU reservation ceiling: **2,320 core-hours** accompanying GPUs, plus **16
  core-hours** for local preparation/accounting/reduction: **2,336 core-hours**.
  Reservation counts, not application CPU time, govern the grant.
* Storage: ≤4 GiB/job and ≤100 GiB total new output, plus ≤100 GiB independently
  verified durable copy; ≤200 GiB aggregate additional storage. No source copies.
  This is a ceiling; saved prediction arrays/models are expected to be much smaller.
* Require Linux Python 3.11, NumPy 1.26.4, TensorFlow 2.16.2/Keras 3.15.1 and the
  appropriate pinned GPU runtime; record actual versions and determinism settings.
  Use `mnv_guarded_run.py` from the frozen execution checkout. Check canonical
  live-state freshness and scheduler directly before allocation. An import or
  environment mismatch stops rather than changing checkouts or pins.

Calibration proceeds to the full matrix only if extrapolated completion, memory
and storage fit the remaining grant with ≥20% headroom. Use measured training
and inference timings separately. If not, stop with a revised cost estimate;
do not shrink event counts, drop seeds or change batching to rescue completion.
Stop on any code/input mismatch, non-finite loss/gradient/weight, absolute
log-odds >50, OOM, failed test, missing artifact, source access attempt, or
allocation/budget overrun. Slurm enforces each allocation's memory and wall
limit; the executor meters aggregate reservation and output growth between jobs
and at least every minute during execution. Cancel remaining jobs on a technical
failure. Preserve partial outputs without retry or replacement. Scientific
failure alone does not suppress other predeclared seeds; complete the matrix
within budget and report all results.

## Acceptance and statistical precision

Freeze these criteria before calibration. Do not use calibration's learning
scores to tune them.

1. **Integrity:** all tests and 24 jobs complete; common row/feature/mask/weight/
   truth hashes and per-seed initial arrays match; no missing seed, clipping,
   reordering, truncation or adaptive epoch selection. Any missing job makes
   the comparison incomplete.
2. **Primary injected endpoint:** per-seed final push log-ratio RMSE reduction
   `100*(RMSE_P-RMSE_D)/RMSE_P`. Require at least 7/8 favorable seeds and the
   two-sided 95% Student-t interval for its paired mean to lie wholly above
   **5%**. Also require D's final RMSE ≤0.10 in every seed; this is one quarter
   of the maximum injected log-ratio amplitude, an absolute recovery safeguard.
3. **Ordinary/shuffle:** final log-ratio RMSE ≤0.10 and normalization within 2%
   for both arms in every seed; no more than 0.02 absolute RMSE deterioration
   for D. This prevents accepting an apparent injected gain from a generally
   unstable ratio model.
4. **Stability:** every final D/P global and target-defined upper-decile ESS
   ratio ≥0.90; both arms' ESS and tail ESS also within 10% of known-target ESS.
   For both truth-coordinate projections (edges −2,−1,0,1,2 with under/overflow),
   relative L1 residual ≤0.05; D deterioration ≤0.01. Record bin denominators.
5. **Tails:** report median/99th/99.9th/max, cap exceedance count and weighted
   mass for caps 10/30; no saturation permitted for this bounded target, and
   cap sensitivity in ESS <1%. Report all iteration trajectories; the declared
   endpoint is iteration 3, never the best iteration.

Eight seeds give a paired interval half-width `2.365*s/sqrt(8)`, approximately
4.2 percentage points if seed SD is five points. Thus a measured mean gain around
10% can clear the 5% materiality margin under that variance assumption. Precision
is not guaranteed: wider intervals produce **inconclusive**, not equivalence or
inferiority. Test-row sampling precision and seed variation are distinct; report
projection denominators and descriptive bin residuals without calling seed
spread a physics uncertainty or constructing a covariance. The single primary
endpoint plus mandatory safeguards avoids choosing among many favorable metrics.

## Real-source prerequisites and subsequent matched design

These are **blocking prerequisites**, not satisfied by this proposal's approval:

* Producer evidence bound to the two audited UUIDs must address release/filler/
  PID definitions, time range and all four unresolved object-family questions.
  Use the existing unsent inquiry; no message to anyone is authorized here.
* Establish row/group meaning and dependencies. Keep `(role,playlist,run,subrun,
  gate)` groups intact; reserve every group touching historical entries `[0,16)`.
  Repeated grouping keys are not grounds for deduplication.
* Bind source-row-aligned `pass_reco`, `pass_truth`, reco/truth linkage, positive
  physics weights and literal background/miss handling to their producers.
  The audited 75-branch mapper has none of those selection/weight/truth legs.
  Do not fabricate an all-true real sidecar or use Gregor's MC-only prepared rows.
* Freeze a selected multi-file data/signal/background inventory, source release
  strata, train/validation/test group hashes and training-only normalization.
  Target at least one million selected training signal rows, 250,000 independent
  test signal rows and adequate selected background support; actual available
  counts and exact source bounds must be measured before a real run card exists.
* Real paired arms must use identical data, signal/background events, selections,
  weights, backgrounds and native misses, generic cloud, event block, normalization
  and truth model. Compare ordinary and injected MC closure before data/MC
  reweighting; stratify by release/playlist, missingness and multiplicity. Do not
  fit a discriminator to the two convenience files and call it representation
  performance.

Consequently no honest exact real-source CPU/GPU estimate or executable real
launcher can yet be bound. The concrete request above is the independently
useful synthetic experiment. Producer resolution and source inventory preparation
must precede a separately concrete real-source execution proposal; this does
not renew the previous audit, or permit dependent experiments by default.

**Terminal authority:** results can support only a diagnostic routing conclusion
on the declared synthetic fixture. They cannot authorize publication adoption,
central/statistical pairing, real-source training, calibration, uncertainty
coverage, covariance construction, PET-versus-scalar precision claims or Gate 6.
