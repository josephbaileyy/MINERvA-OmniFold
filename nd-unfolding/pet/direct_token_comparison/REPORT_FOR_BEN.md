# PET representation comparison for Ben

**11 September 2026 · preparation for diagnostic method development**

We propose testing individual typed objects in attention while retaining the
current field definitions, masks and raw-row membership. There is **no measured
learning-performance winner**. The current typed adapter pools trainable
per-object embeddings before conditioning PET; Gregor's approach allows objects
to interact through attention before event reduction. This is a useful hypothesis
to test, not a reason to replace the estimator. PET remains diagnostic and
method-development; publication adoption, covariance construction and Gate 6 are
outside this work.

The reference is `pet-prong-semantics` remote head
`57b707b737ce817c1ef8d8bd0f0a39ce4becb7ba`, checked on 11 September. The current
adapter produces **13 event + 3 × (16 pooled features + 1 count) = 64 columns**.
C0 zeros the 51 typed columns and C1 enables them: these controls do not compare
pooling against object attention. The direct candidate below is an isolated
Keras implementation, not Gregor's network or a pretrained checkpoint.

## Proposed choices, distinguished from measurements

| Disposition | Element | Reason and boundary |
|---|---|---|
| **Keep** | Individual reconstructed objects, family/type information, continuous detector features and event context | Object-level attention can learn interactions before compression. Both arms receive exactly the same available information. A Deep Sets representation can also learn interactions through its event network; no intrinsic capacity ordering is asserted. |
| **Modify** | Token routing | Compare family sums before attention with individual embeddings before the **same** attention layers. Retain raw counts in both. Verify pooled embeddings against the current C1 adapter, then keep the change of downstream architecture as a separate bridge, not part of the routing effect. |
| **Modify** | Padding, missing fields, category semantics | Use structural presence and per-field masks, independent of energy or normalized values. Keep v2 raw PID categories; charge applies only to valid PID 3, with raw codes 0/1/2; undefined score/mass −1 remain masked. Scores keep their native scale. Family encoders carry type information without assigning a real particle to a padding embedding. |
| **Keep provisionally** | Raw prong rows, including prong zero; separate event muon | This is the implemented membership contract. Removing primary-like rows, choosing hypotheses, applying PID/energy cuts or deduplicating objects would change membership and requires its own comparison. Retention is not a claim that these are disjoint physical particles. |
| **Exclude from this comparison** | Truth labels in reconstructed inputs, event IDs/source labels as features, inferred-value attention masks, silent truncation | Labels/IDs belong to loss or provenance only. The pinned PET2 forward code rebuilds masks from a kinematic channel and has `padding_idx=0`; copying those conventions would confound valid objects with padding. Our candidate has no typed-object cap. |
| **Unresolved** | Photon/blob meaning and calibration; prong hypotheses; shared objects/primary lepton; exact tuple release and time range | Mechanical mapping does not supply producer semantics. Existing producer questions remain unsent. No dependent real-input fitting or training may begin on these fields until the required evidence is resolved. |
| **Unresolved / separate experiments** | Muon token, richer globals, coordinate/log transforms, count scaling, mean pooling, filtering and overflow aggregates | These alter information, normalization or membership. The primary routing contrast changes none of them. Missingness/overlap can be source shortcuts. A count/mean sensitivity is useful later, not silently substituted for the current sum/raw-count control. |
| **Unresolved / separate experiments** | PET2 architecture, PyTorch and pretraining | First compare random initializations within one framework. Later architecture and framework bridges need equal tensors and ratio conventions; initialization needs compatible, licensed, hash-bound weights. Historical unavailability is not evidence of present unavailability or inferior transfer. |

## What has actually been measured

The completed audit read **4,096 data and 4,096 MC rows**, unselected convenience
samples from the two UUID-bound files. Mapping passed; release remains unverified
and all four object-family verdicts remain unresolved. The following extension
counts exclude the historical first 16 rows of each source. They come from the
committed receipt and telemetry, not a new ROOT read.

| Observation | Data | MC | Interpretation |
|---|---:|---:|---|
| PID −999 or 0, retained by our mapper | **429/6,050 prongs** | **732/7,140 prongs** | Lower bounds on removal by Gregor's PID-or-energy filter. Energy overlap/union is not measured by these histograms. |
| Masked prong dE/dx | **4,614/6,050** | **5,080/7,140** | Masks carry substantial information; masked values must not become physical zeros. |
| Masked hypothesis mass | **1,482/6,050** | **2,262/7,140** | This field is hypothesis-dependent, not an independent mass measurement. |
| Prong-zero four-vector matches event lepton under the audit check | **4,073/4,080 rows** | **2,898/4,080 rows** | Numerical correspondence only; not an association or duplicate-particle determination. |
| Finite prong time above correspondence's unverified 10,000 bound | **4/6,050** | **1/7,140** | Preserve all five exceptions; neither cut them nor infer a cause. |
| Blob count in the separate historical 16-row anchor | **208/16 rows; max 90** | **155/16 rows; max 42** | Multiplicity matters. A hypothetical cap of 20 would discard at least 70 and 22 blobs respectively; this is a bound, not measured Gregor overflow. |

The source receipt SHA-256 is `5e8d545b…53b3da`. Full hashes, derivations and
30 checked historical per-arm receipt hashes are in [evidence.json](evidence.json),
reproducible with [reproduce_evidence.py](reproduce_evidence.py). The v1 anchor's
old validity counts must not be relabeled as v2 mask measurements.
[Source result](../SOURCE_AUDIT_REPAIRED_RESULT-20260910.md),
[semantic follow-up](../SOURCE_AUDIT_SEMANTIC_FOLLOWUP-20260911.md),
[fixed-sample packet](../../../docs/orchestration/PACKET-20260901-pet-typed-descriptor-semantic-evidence.md).

Gregor's [paper v2](https://arxiv.org/abs/2604.12364v2) studies supervised regression
and pion classification, not OmniFold closure. Its representation has four
kinematic scalars, a type channel and five auxiliary token fields; it describes
15 globals. The [pinned implementation](https://github.com/gregorkrz/minerva-ml/tree/78ebc0d6af04a5b6ab8114a9560dcc9c2a0b99bb)
can build 16 globals (7 base + 3 extras + 6 type-energy sums), supports a default
150-object cap and optional family aggregation, and filters prongs with PID −999,
PID 0 or energy ≤10⁻⁶. These are consumer conventions, not release attestation.
The exact paper-run tensor width and cap remain to be bound to its run artifacts.
The contradictory downstream PID labels do not override the curated
reconstruction correspondence. [Preprocessing](https://github.com/gregorkrz/minerva-ml/blob/78ebc0d6af04a5b6ab8114a9560dcc9c2a0b99bb/src/dataset/preprocessing.py),
[PET2 forward](https://github.com/gregorkrz/minerva-ml/blob/78ebc0d6af04a5b6ab8114a9560dcc9c2a0b99bb/src/models/omnilearned/network.py).

The [historical assessment at b65f9ff2](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/b65f9ff2/docs/GREGOR_PET2_OMNIFOLD_ASSESSMENT.md)
used a different source pin and 100,000-event synthetic pilots. Its first target
was already visible to the parent, so inconclusive feature ablations cannot
establish inferiority. The later typed-carrier stress test improved mean push
log-ratio RMSE **27.915% over three seeds (101/202/303)**, but failed the frozen
≥30% improvement and ≤0.25 enriched-RMSE requirements. Across five carrier families,
all **5/5** failed that compound gate. This is limited harness-capacity evidence,
not a real-data learning result or a pooled-versus-direct comparison. The exact
aggregate and per-seed receipts survive under
`evidence/prepublication-excluded-gregor-b65f9ff2`; the new evidence file verifies
their hashes without promoting them.

## The three-way answer, as of 15 September 2026

Ben asked whether we should adopt individual typed-object tokens, Gregor's
aggregate-overflow setup, or other separately tested changes. Taking them in turn,
and separating what is measured from what is still open:

### 1. Individual typed-object tokens — do not adopt yet; the question is still unmeasured

**There is no learning-performance evidence either way.** The 24-job paired matrix
that would answer it has never run. Every GPU attempt so far has stopped in software
equivalence checking, before any training comparison.

A new and concrete obstacle emerged on 15 September: the direct (individual-token)
route **does not currently reproduce across CPU and GPU in the variable-multiplicity
case**. After two Adam steps the attention `query/kernel` diverges by `1.55e-04`
against an unchanged `atol=1e-5, rtol=1e-4` tolerance, while the same model's
`pooled` route in the same case stays within tolerance. Details and limits in
[the terminal record](AMENDED_RESULT-20260915.md).

This is a numerical-reproducibility obstacle, not a verdict on the representation.
But it bears directly on the recommendation: variable multiplicity with individual
tokens is precisely the configuration the science needs, and we cannot yet run a
trustworthy paired comparison in it. The reasonable next step is a diagnostic that
establishes whether the divergence comes from padded-width-dependent reduction order
in the ragged repacking — a hypothesis we have **not** yet tested — and whether a
deterministic packing order is reachable without changing the model being compared.

Two things argue for keeping the hypothesis alive rather than dropping it: the
forward pass is unaffected (predictions agree to ~1e-6 in all four cases measured,
including the failing one), and no optimizer slot diverged anywhere. So the issue
looks localized to weight updates in one routing/multiplicity combination, not to the
representation's viability.

### 2. Aggregate overflow — adopting it as an improvement would be backwards

This is where the position changed most, and it does **not** depend on any learning
result. We read the pinned upstream code rather than the paper's description, verified
it byte-for-byte against the digests already recorded here, and executed its
aggregation function. Full measurements in
[the overflow specification](OVERFLOW_SPECIFICATION-20260915.md), §2.

Three findings reframe the question:

- **Aggregate overflow is not Gregor's default.** In the pinned code the defaults are
  `max_objects=150`, `max_blobs=-1`, `max_prongs=-1`. The default path is
  **energy-ordered truncation** at 150 objects; per-family aggregation is opt-in and
  requires *both* `max_blobs` and `max_prongs` > 0, at which point `max_objects` is
  ignored. So "Gregor's setup" names two different behaviours and we should say which.
- **Our implementation applies no cap at all.** Every object is retained individually,
  padding is per-batch and nothing is truncated. Relative to *either* upstream path we
  currently keep strictly more information.
- Therefore aggregate overflow is a **mitigation for a cap we do not have**. Adopting
  it as an enhancement over our current state would mean first introducing a cap and
  then partially compensating for it. That is a cost/memory decision, not an accuracy
  improvement, and nothing we have measured suggests we need it.

**If a cap ever becomes necessary**, the measured properties do give a clear
preference, and this is the actionable part:

- Prefer **aggregation over truncation**: aggregation conserves total four-momentum
  exactly (verified across every multiplicity we tried), whereas truncation discards
  the tail's energy from both the token sequence *and* the per-PID energy-sum globals,
  because upstream computes those sums after truncating.
- **Add an explicit merged-count feature**, which upstream lacks. Its aggregate token
  erases multiplicity: 21, 30 and 90 objects all collapse to exactly 20 tokens, with
  the merged count recoverable only indirectly through the summed energy.
- Expect to **lose per-object tail structure regardless**: the merged `[dE/dx, x, y,
  z, t]` block is an arithmetic *mean*, so the tail survives only as a centroid.
- Implement the **code, not the docstring**. When the cap binds, the function returns
  exactly `n_keep` tokens (`n_keep - 1` individual plus one aggregate), not the
  `min(n_keep+1, n_blobs)` its docstring advertises.

On whether a cap would bind on real data: the completed audit's separate historical
16-row anchor recorded blob counts up to **90** (data) and **42** (MC), so a
20-object per-family cap would bind and a hypothetical cap of 20 would discard at
least 70 and 22 blobs respectively. That is a bound from a small unselected anchor,
not a measurement of Gregor's overflow rate, and the v1 anchor's counts must not be
relabelled as v2 mask measurements.

### 3. Other differences — each needs its own isolated evidence

The keep/modify/exclude/unresolved table above is unchanged by this work; no entry in
it has been revised by a measurement. Two items are worth Ben's attention because
they are cheap to get wrong by copying upstream conventions:

- **Do not copy the padding convention.** The pinned PET2 forward code has
  `padding_idx=0` while upstream also uses PID 0 for a real category, so copying it
  would merge valid objects with padding. Keep index 0 reserved for padding only.
- **The upstream prong filter (PID −999, PID 0, or energy ≤ 1e-6) is a membership
  change**, not a representation change, and our audit gives only lower bounds on
  what it would remove (429/6,050 data and 732/7,140 MC prongs). It needs its own
  comparison before adoption.

A swap of the whole network or preprocessing pipeline would confound all of these at
once and could not attribute any difference to a cause; each candidate change needs
isolated evidence.

### What none of this establishes

Everything above is synthetic method development or a reading of upstream source.
None of it is a real-data result, and none of it authorizes publication adoption, a
covariance, a statistical pairing, a coverage claim or any Gate-6 action. PET remains
diagnostic and method-development. The source-semantic prerequisites are still
unresolved — photon/blob meaning and calibration, prong hypotheses, shared objects
and the primary lepton, and the exact tuple release and time range — and no
representation choice can be settled on real data while they are. Producer questions
remain unsent.

## Execution history

Execution update: the authorized retry passed 49 software tests plus 10 subtests
and an A100 operation check. The pooled calibration arm saved artifacts; the
direct arm failed because GPU `DenseBincount` does not support the required
determinism. The paired calibration is incomplete; no full jobs ran and no
routing-performance conclusion follows. [Exact terminal evidence](RETRY_RESULT-20260912.md).

**13 September compatibility update:** the deterministic packing repair matches
its frozen CPU implementation exactly in all eight model/case comparisons,
including gradients and updated weights; 73 tests plus 10 subtests pass locally.
[Exact evidence and patch](COMPATIBILITY_REPAIR-20260913.md). The approved GPU attempt subsequently failed the first pooled CPU/GPU
embedding tolerance check; calibration did not start.
[Terminal evidence and resource accounting](COMPATIBILITY_RESULT-20260913.md).
Direct-model GPU validation and paired calibration remain incomplete. These software checks do not change any keep/modify/exclude/unresolved
recommendation or supply a learning-performance winner.

**14 September numerical update:** a controlled TF32 on/off diagnostic reproduced
the pooled CPU/GPU discrepancy. At unchanged tolerance, 112/192 pooled components
fail with TF32 enabled and 0/192 fail with it disabled; maximum differences are
4.89235e-4 and 2.38419e-7 respectively. The first discrepancy occurs in a Dense
matrix product before pooling. [Exact measurements and provenance limits](NUMERICAL_RESULT-20260914.md).
This supports a future explicit full-FP32 compatibility check, not a representation
winner. Direct-model GPU validation and paired training remain incomplete.

**15 September full-FP32 update:** both nominal pooled/direct GPU cases pass,
but the variable pooled case fails a CPU/GPU weight comparison after two Adam
updates (reported maximum `1.20454e-5`; cause unresolved). Calibration and the
learning matrix did not run. Thus there is still no measured learning-performance
winner or basis to revise representation choices from this attempt.
[Terminal evidence and qualifications](FP32_RESULT-20260915.md).

**15 September optimizer follow-up:** the new diagnostic completes both routes
in all four cases. Two attention key-bias components fail raw CPU/GPU weight
agreement; identical-gradient Adam replay passes (maximum difference `2.98e-8`),
and all prediction checks pass (maximum `7.75e-7`). Float64 replay explains the
captured discrepancy as amplification of tiny gradient differences in a redundant
attention parameter. This supports a specific proposed software-gate amendment,
not a routing-performance claim. The earlier failure is not yet reproduced:
checkpoint interleaving changes initialization after the first model pair.
[Exact evidence and qualification](OPTIMIZER_RESULT-20260915.md). No learning
comparison has run, and keep/modify/exclude recommendations remain unchanged.

**15 September amended preflight — terminal failure.** The approved key-bias gate was
implemented and locally validated, then deployed and run in one authorized allocation,
job `58354898`. On the cluster the suite passed **69 tests + 10 subtests** and the
**25** adversarial gate controls, the original-sequence CPU initialization capture
covered **all eight** case/routing pairs, and every import-guard record reported
inspected repository origins with no allowances.

The GPU preflight then reached four of the eight pairs. Three passed and wrote gate
records — `nominal/pooled`, `nominal/direct`, `variable/pooled` — and the fourth,
`variable/direct`, **failed**: Slurm `FAILED`, ExitCode `1:0`, **279 s**. The failing
tensor is `weight_24`, which the run's own saved inventory names
`multi_head_attention/query/kernel`, at `max_abs=1.443e-04` on step 1 and
`1.549e-04` on step 2. It is *not* the exempted tensor. The approved exemption covers
only the key **bias**, and only because a key bias cancels from softmax by exact shift
invariance; a query **kernel** has no such invariance, and the proposal explicitly
declined to exclude it. So this is a real stop, not a candidate for the same
treatment.

Calibration never started. Consequently the 20% resource-headroom gate was never
evaluated, the frozen 24-job matrix stays unreleased, and the specified overflow
contrast cannot execute because it is conditioned on measured calibration headroom
that does not exist. No retry was submitted and none is authorized. Conservative
charge is now **1,021 s** (742 prior + 279), and all aggregate ceilings remain far
from binding — the constraint here was a technical failure, not budget.

One incidental confirmation, with its limit: the `variable/pooled` key-bias
discrepancy measured `1.204535385568306e-05`, agreeing to six significant figures
with the FP32 attempt's reported `1.20454e-5`. That is strong evidence the earlier
failure involved the same redundant parameter, but it remains magnitude agreement
rather than reproduction, because the earlier run's failing weights were never saved.
[Terminal evidence, resource accounting and the untested mechanism](AMENDED_RESULT-20260915.md).
