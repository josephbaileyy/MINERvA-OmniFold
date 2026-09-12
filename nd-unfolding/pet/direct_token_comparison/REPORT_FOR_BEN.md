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

## Next decision

Approve the bounded [execution proposal](EXECUTION_PROPOSAL.md) after reviewing
preparation. It tests routing on one million synthetic training events, eight
paired seeds, ordinary and injected closure, and a shuffle control, with frozen
truth representation and training budgets. Acceptance requires a material paired
closure improvement plus stability, tail and ESS gates; otherwise report
inconclusive or failed. Real-source training remains dependent on producer,
selection, weight and normalization prerequisites. Neither a synthetic pass nor
source mapping agreement authorizes a scientific estimator choice.

Execution update: the authorized retry passed 49 software tests plus 10 subtests
and an A100 operation check. The pooled calibration arm saved artifacts; the
direct arm failed because GPU `DenseBincount` does not support the required
determinism. The paired calibration is incomplete; no full jobs ran and no
routing-performance conclusion follows. [Exact terminal evidence](RETRY_RESULT-20260912.md).
