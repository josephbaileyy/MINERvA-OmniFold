# Gregor PET2 OmniFold experimental preregistration

Frozen before the first campaign training result on 2026-07-23. This document
records the selection rules; later result documents may explain infeasible
comparisons but may not retroactively weaken a failed criterion.

## Evidence compartments

Every result must carry exactly one primary evidence label:

1. `code-contract`
2. `synthetic-fixture`
3. `public-gregor-dataset`
4. `recoil-input-pilot`
5. `publication-g2`

The campaign has no publication G2 NPZ. Results in compartments 1–4 cannot
establish publication closure, final covariance, final extraction, or an
architecture replacement.

## Arms and controlled differences

| Arm | Backend | Inputs | Declared comparison |
|---|---|---|---|
| A | existing TensorFlow/Keras PET | recoil cloud only | recoil-only baseline |
| B | existing TensorFlow/Keras PET | A plus reconstructed-muon globals | existing full-event baseline |
| C | independent PyTorch PET2-family | B-matched numeric footing, generic token category | architecture/framework/engine pilot |
| D-view | C | activate only the already-dumped reconstructed detector view | current-data categorical ablation |
| D-typed | C | real reco muon/photon/blob/prong types | unavailable until a symmetric dump exists |
| E-muon | D parent | add the reconstructed-muon block only | isolate the dominant global-feature effect |
| E-rich | E-muon | add only separately audited reco globals | richer-global incremental effect |
| F | bit-identical random parent plus eligible initialization | strict manifest-matched checkpoint | unavailable until weight license/hash/shape/preprocessing gates pass |

Muon-as-token is a separate representation ablation, never hidden inside D.
Current G2 lacks reco photon/blob/prong types; `view` is not relabeled as an
object type. C and D use the same parameter tensors; inactive categorical
inputs are masked rather than deleting capacity.

## Fixed pilot controls

- Synthetic master seed: `424242`.
- Estimator seeds: `[101, 202, 303]`.
- Split fractions: `0.70 / 0.15 / 0.15`, assigned once from stable row
  identities and reused by every compared arm.
- Default matched budget: two OmniFold iterations, eight epochs per step,
  batch size 512, identical train-row cap and identical epoch count.
- Optimizer: AdamW, learning rate `1e-4`, weight decay `1e-2`, unless a
  framework cannot express the same option. Any deviation is a named
  evidence downgrade.
- Early stopping may inspect only validation weighted BCE at fixed epoch
  boundaries. Closure, ESS, tails, or the held-out test set may not select an
  epoch or tune a hyperparameter.
- Selection seeds and final evaluation seeds must be separated if any arm is
  promoted. This campaign cannot promote an arm without publication G2, so
  its three pilot seeds remain feasibility/stability evidence only.
- Framework parameter counts, training rows, effective weighted class masses,
  optimizer steps, and wall/GPU budgets are reported. If exact B/C matching is
  impossible, the B/C result is labeled an engineering comparison rather than
  an architecture claim.

## Mandatory gates

All of the following are pass/fail:

- no truth, generator bookkeeping, target/source label, or audit category in
  Step 1;
- identical reco feature meaning for signal, data, and literal backgrounds;
- explicit boolean masks; pad category 0 distinct from every real category;
- no sentinel, NaN, or infinity reaches a physical token or normalizer;
- native misses excluded from Step 1, propagated without reordering, and
  included in Step 2;
- `pass_reco & !pass_truth` fails preflight;
- refined training weights finite and nonnegative, with signed provenance
  retained separately;
- class-mass convention is explicit and tested against a known unequal-mass
  analytic ratio; no renormalize-then-offset double correction;
- deterministic split/alignment and full-order extraction with
  `mc_indices == arange(N)`;
- permutation, padding, overflow, malformed-input, checkpoint-rejection, and
  save/load tests pass;
- arm manifests prove the intended one-factor difference.

Failure of a mandatory gate disqualifies the affected result regardless of
AUC or closure.

## Metrics and decision rules

Training AUC is diagnostic only. Report for every feasible arm and seed:

- validation/test weighted BCE;
- analytic/synthetic log-density-ratio bias and RMSE;
- ordinary and injected-conditional closure residuals;
- ratio/weight quantiles, maximum, nonfinite count, and logit-cap saturation
  by count and weight mass;
- global and tail effective sample size;
- sensitivity to declared logit caps;
- seed spread;
- important available 2D/3D/5D projections;
- runtime, peak GPU memory, throughput, and artifact reproducibility.

For a richer arm to be called **beneficial** in a pilot it must:

1. pass every mandatory gate;
2. improve the preregistered injected-closure residual by more than 5% versus
   its direct parent across the aggregate seed result;
3. not reduce global or named-tail ESS by more than 10%;
4. not materially increase extreme-tail/cap sensitivity; and
5. reproduce the direction of the effect across seeds.

An absolute difference at or below 5% in closure or ESS is **neutral** unless
the uncertainty excludes that band. Better closure with an ESS loss over 10%,
unstable seeds, worse tails, or increased clipping dependence is **harmful or
insufficiently validated**, not beneficial. A higher AUC cannot override
these rules.

Multiple tested alternatives are reported together; no uncorrected
single-seed significance claim is allowed. A formal promotion claim would
require fresh evaluation seeds and multiplicity control, neither of which is
available without G2.

## Explicit evidence downgrades known at freeze time

- Arms D-typed, fully rich E, and F are not executable on current publication
  inputs.
- The public Gregor dataset is MC-only prepared diagnostic data with no
  physics weights, stable event identities, pass flags, data, backgrounds, or
  misses. It can test token mechanics and preprocessing only.
- The recoil xps2 input lacks the G2 typed/global schema. It can test engine
  throughput, ratios, tails, and extraction mechanics, not typed-token
  superiority.
- Existing TF and new PyTorch engines differ in framework and normalization
  plumbing; B/C evidence is downgraded unless the analytic and cross-engine
  ratio tests establish equivalence on identical tensors.
