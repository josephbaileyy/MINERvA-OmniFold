# Gregor PET2 conditional-information stress preregistration

Frozen before continuation implementation and before any continuation training
result. This amendment does not alter the original
`EXPERIMENT_PREREGISTRATION.md` or its completed products.

## Scientific correction and evidence boundary

The completed 100k matrix injects its analytic ratio only through reconstructed
`mu_pt` and total recoil-token energy. Both are visible to arm C. It is
therefore a **baseline-sufficient null-feature test**: useful safety evidence
for adding irrelevant/noise channels, but not a test of whether unique
detector-view, reconstructed-type, rich-global, distinguished-muon, or
pre-truncation-overflow information can be learned.

This continuation tests only whether each feature channel can transmit a
known conditional density ratio through the complete experimental OmniFold
harness. Its evidence label is `synthetic-fixture`. Every product must set
`g2_validation_claim=false` and `publication_promotion_permitted=false`.
Passing is necessary channel-capacity evidence, not evidence that the
conditional exists in MINERvA data and not a reason to adopt a feature.

## Common counterfactual construction

All five families and all controls use:

- 100,000 signal rows and 10,000 literal-background rows;
- fixture seed `424242`, split seed `424242`, estimator seeds
  `[101, 202, 303]`;
- the original stable `0.70 / 0.15 / 0.15` partition;
- two OmniFold iterations, eight epochs per step, batch size 512, AdamW
  `lr=1e-4`, weight decay `1e-2`;
- seven stored tokens, the same model capacity, and the same frozen Step-2
  arm as the completed matrix.

The base dataset is generated once. The hidden sign `h ∈ {-1,+1}` is assigned
from the existing truth-muon-pT ordering within each split, without changing
the truth tensor, truth weights, pass masks, or event keys. Within each split,
one low-`pT` and one high-`pT` selected row form a deterministic pair.
Unpaired selected rows have `h=0`.

For every pair:

1. all direct-parent model inputs are made byte-identical;
2. the two `w_reco` values are replaced by their common arithmetic mean;
3. only the declared enriched carrier differs and decodes `h`;
4. pseudo-data is the exact selected-reco inventory;
5. the signal target ratio is `r(h)=1+0.5h`, hence exactly 0.5 or 1.5;
6. unpaired selected rows and native misses have ratio one;
7. literal backgrounds retain signed-negative provenance and zero refined
   training mass.

Equal pair masses make the exact parent-conditional target ratio one:
`(0.5w + 1.5w)/(w+w)=1`. The parent cannot recover the eventwise sign, while
the enriched carrier identifies it. The ratio remains positive, has no
extreme tail, and has an exact pair-weighted mean of one. Its expected
eventwise parent log-RMSE is approximately 0.568, over eighty times the
completed C-arm seed-spread scale; no model-result calibration is permitted.

The truth inventory is never modified by a carrier or control. Because `h` is
defined from an existing truth coordinate, the common truth-frozen Step 2 can
learn the transferred pull when and only when Step 1 recovers it. The truth
tensor/row hash, truth arm, Step-2 model configuration, and Step-2
preprocessing footing must be single-valued across the parent/enriched arms
and all five feature families.

## Five isolated feature families

| Family | Direct parent | Enriched arm | Sole carrier |
|---|---|---|---|
| detector view | C | D-view | first real token uses one of two real X/U/V categories according to `h`; token kinematics, count, mask, order and globals are paired-identical |
| reconstructed type | C | D-typed | first real token is reconstructed cluster or track according to `h`; all continuous/view/global inputs are paired-identical |
| rich globals | E-muon | E-rich-no-charge | paired `vertex_z` sign/magnitude carries `h`; every E-muon global and all token inputs are paired-identical |
| distinguished muon | E-muon-global | E-muon-global-plus-token | an appended, explicitly masked muon token carries muon-to-recoil neighborhood geometry; E-muon globals, muon continuous values and the recoil cloud are paired-identical |
| pre-truncation overflow | C with the aggregate masked | C plus overflow aggregate | the last physical aggregate token carries discarded energy according to `h`; retained tokens, globals, count visible to the parent, and ordering are paired-identical |

The distinguished-muon result is specifically a test of the **additional
relational token/coordinate channel**. It is not a pure same-information
global-versus-token comparison. The child retains the parent's E-muon globals
and adds the token; it may not silently delete the parent globals. The fixture
must define nonzero, finite muon coordinates and two recoil neighborhoods with
different continuous content so the KNN channel can express the relation.

Overflow construction must conserve the declared pre-truncation energy. The
parent must not receive a total-energy global from which discarded energy can
be reconstructed.

## Mechanical exclusivity certificates

Before training, every family must produce a machine-readable certificate:

- pair members have identical materialized parent tensors for
  `continuous`, `coords`, `token_mask`, `type_id`, `view_id`, and `globals`;
- classifier bookkeeping (`row_index`, event key, weights, pass flags, pair
  ID, `h`, target ratio, and source labels) is absent from model tensors;
- the enriched carrier decodes `h` exactly on paired rows;
- any deterministic parent score ties within every pair, giving analytic
  carrier AUC 0.5, while the declared enriched decoder gives AUC 1.0;
- carrier counts are balanced within each train/validation/test partition;
- the refined target dependence on `h` equals the declared pre-refinement
  dependence;
- data, signal and literal background expose identical tensor schemas;
- native misses are zero/masked at reco and unchanged at truth;
- `pass_reco & !pass_truth` remains forbidden.

Failure of a certificate is a fixture BLOCKER, irrespective of a training
result.

## Frozen controls

Each family is run in three modes with identical rows and budgets:

1. `signal`: carrier decodes `h`, target is `1+0.5h`;
2. `unity-sham`: carrier decodes `h`, target is exactly one;
3. `carrier-shuffle`: target remains `1+0.5h`, but the carrier is
   deterministically permuted within each split so its analytic AUC for `h`
   is within 0.02 of 0.5.

The sham tests spurious reweighting from added capacity. The shuffle tests
whether an undeclared nuisance or bookkeeping path transmits the label.
Neither negative control may be replaced after outcomes are seen.

## Metrics and fixed channel-capacity gates

Report per arm, family, mode, and seed:

- pull and push log-ratio bias, MAE and RMSE against the aligned analytic
  ratio;
- hidden-sign group calibration and 2D/3D truth-projection residuals;
- predicted versus expected global and declared-tail ESS;
- ratio and reweighted-weight quantiles/maxima;
- cap-10 and cap-30 saturation by count and weight mass, plus ESS sensitivity;
- split, row, target, parent-tensor, truth, model, preprocessing, parameter,
  control and recipe fingerprints;
- runtime, throughput and peak GPU memory.

The `signal` enriched arm passes only if:

1. every mandatory contract and exclusivity certificate passes;
2. every seed has push log-ratio RMSE at most 0.30 and the three-seed mean is
   at most 0.25;
3. mean RMSE improves by at least 30% versus the direct parent and the
   direction is favorable in all three seeds;
4. the parent's mean RMSE is at least 0.35;
5. predicted global and declared-tail ESS differ from analytic expected ESS
   by at most 10%;
6. the maximum declared projection relative L1 is at most 0.25;
7. no weight is nonfinite, no cap-10/cap-30 value saturates, and cap choice
   changes ESS by less than 1%.

For `unity-sham`, both arms must have mean RMSE at most 0.15, no saturation,
and expected-ESS agreement within 10%. For `carrier-shuffle`, the enriched
arm must not improve mean RMSE by 15% or more versus its parent and the
carrier certificate must be within 0.02 of chance. A negative-control failure
invalidates that family's positive result.

An enriched-arm failure with all mechanical controls passing is a
harness/optimization defect for that channel, not physics evidence that the
feature is harmful. A pass establishes channel capacity only.

## Production-G2 conversion/loader code-contract gates

The literal production G2 remains unavailable. The continuation may implement
and test only a synthetic-mini-packet conversion seam:

- bind the compressed input by SHA-256, size, schema markers and estimator
  fingerprint;
- stream each safe non-object NPY member from the ZIP entry with a declared
  bounded byte buffer into an immutable `.npy` file;
- receipt every array's name, dtype, shape, order, row family, units and
  output SHA-256;
- recompute signal/data/background row counts and legacy ordered-inventory
  hashes;
- use a stable partial directory, per-array content-verified progress journal,
  final manifest and atomic publish;
- make restart idempotent and re-convert partial or content-mismatched members;
- make the loader reject stale input, missing completion marker, missing
  array, mutated bytes, dtype/shape/order/count mismatch, or identity mismatch;
- open memmaps read-only and expose bounded row windows/chunks rather than
  materializing the production inventory.

Tests must exercise successful conversion, bounded reads, idempotent resume,
interrupted resume, stale input, missing member, byte mutation, receipt
mutation, row-family mismatch, object-dtype rejection, and read-only memmaps.
The products must say that code-contract tests on a generated packet are not
G2 availability or validation evidence.

## Checkpoint-compatible design boundary

A future Gregor-exact backend is a separate namespace and estimator
fingerprint from `independent-pet2-small-concept-match-v1`. A design may be
documented now, but no backend, initialization result, or transfer claim is
authorized without licensed, accessible, immutable-hash-bound weights.

The design must freeze source SHA, exact PET2 preset/configuration, tensor and
state-dict schemas, preprocessing transforms and units, categorical
vocabulary, mask/padding policy, safe loader, per-key load/remap manifest,
weight license and checksum. Legacy-exact reproduction and corrected
PID/mask behavior are different architecture fingerprints. Silent partial
loading, `strict=False`, random fallback, and cross-loading into the
independent backend are forbidden.

