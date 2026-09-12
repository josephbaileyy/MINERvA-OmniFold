# Deterministic direct-token packing repair

**Prepared and CPU-validated; GPU compatibility remains unverified. No new
allocation was submitted.** The second technical failure and partial pooled
outputs remain preserved in [the terminal record](RETRY_RESULT-20260912.md),
excluded from performance comparisons. The new [bounded proposal](COMPATIBILITY_PROPOSAL-20260913.md)
requires explicit approval before allocation.

## Patch and preserved semantics

The production candidate change is confined to `typed_token_comparison.py`:
replace both `RaggedTensor.from_value_rowids` calls with `from_row_splits` using
one shared integer partition. For sorted segment IDs `s`, compute
`length[r] = sum(s == r)` over **all stored slots**, then
`split = [0, cumsum(length)]`. Integer segment summation and cumulative summation
are explicitly placed on CPU. Projected embeddings and their gradients stay
outside that placement context. Validation rejects negative/out-of-range or
unsorted IDs and retains empty leading, internal and trailing events.

Active-object counts cannot be used as row lengths: a masked stored slot still
occupies its original position. This construction preserves membership, family
and within-event ordering, token/feature masks, padding, enabled flags and raw
counts. It neither filters nor truncates objects. Feature preparation, pooled
summation, all model layers/configuration/parameters, optimizer, normalization,
truth-side model and training loop are unchanged. Determinism stays enabled.

The pinned [TensorFlow 2.16.2 row-partition source](https://github.com/tensorflow/tensorflow/blob/v2.16.2/tensorflow/python/ops/ragged/row_partition.py)
constructs value-row-ID partitions through `bincount`, followed by cumulative
row lengths. This matches the failed GPU stack. Placing the original constructor
on CPU is an alternative; it is exercised as the reference. Explicit CPU integer
row splits avoid that constructor's `DenseBincount` dependency while leaving
floating embeddings on their existing device. The repaired partition graph has
no Bincount node. Other GPU operations still require the proposed smoke test.

The complete executable diff against `e0082154` is
[deterministic-packing.patch](deterministic-packing.patch) (apply to the base with
`git apply --unidiff-zero`); `repair-manifest.json`
binds every executable file, frozen run card, criteria and this proposal. The
historical CPU model is copied **byte-for-byte** from
`46fe3d7cd3c88570d7449a884adc4f8ffc44f041:nd-unfolding/pet/typed_token_comparison.py`,
SHA-256 `905aac2dcad3eeb34dd4e21c2196af1ced6d2a58aaa68b7dc328ad737e332b95`,
into `reference/typed_token_comparison_cpu.py`. Its hash is checked before import;
it is registered in the guard inventory and used only on CPU. It is not another
scientific arm. No source reader, receipt-bound legacy code or guard is modified.

## Measured local validation

Evidence: [validation summary](local_validation/20260913/validation.json),
[full preflight receipt](local_validation/20260913/preflight.json), and
[original artifacts/log archive with readback inventory](local_validation/20260913/preservation.json).
The CPU run used macOS arm64 with the five pinned library versions; it is not
evidence about the pinned Linux CUDA runtime. No new GPU or Slurm CPU time was
consumed. Local process CPU consumption was not separately metered.

| Check | Measured result / denominator |
|---|---|
| Regression, compatibility and synthetic source-smoke suites | **73 tests + 10 subtests passed**, 16.74 s; the allocation's narrower suite is 60 + 10 |
| Low-level partitions: zero events, empty collections, variable/trailing-empty rows, 90 blobs | **16/16 exact** split/value/mask/weighted-gradient comparisons; max absolute difference **0** |
| Invalid partitions | **4/4 rejected** (unsorted, negative, out-of-range IDs; negative row count) |
| Model equivalence: 4 cases × pooled/direct | **8/8 exact** routed CPU tokens/counts/masks, initial outputs/loss/parameter and input gradients, updated parameters and predictions |
| Parameter footing | **17,329 per model**, unchanged shapes and exactly copied initial arrays in all 8 comparisons |
| Optimizer and masking | **2 updates per model/case** (eager and traced); finite connected gradients; masked input gradients exactly zero; repeated eager outputs/gradients exact |
| Eager versus traced execution | All 8 within frozen tolerance; maximum absolute difference **2.980232238769531e-7** |
| Save/reload | **8/8** same-process exact predictions and weights; **8/8** fresh-process predictions passed |
| Partition placement | Integer `UnsortedSegmentSum` and `Cumsum` both on CPU; no Bincount in the traced partition graph |
| Complete preflight | **50.484469 s**, including fresh-process reload; parent/child guards passed without allowances |
| Static checks | Black, Ruff, Linux-target mypy on all five edited/new Python implementation/test files; launcher `bash -n` and patch whitespace checks pass |

These are paired implementation-equivalence measurements, not independent
scientific validation or learning-performance results. The CPU reference shares
unchanged layers and feature preparation by design. A preliminary masked fixture
used nonfinite typed payloads and was correctly rejected by the original CPU
contract. The final fixture uses finite sentinels behind typed masks; masked
NaNs are tested only in the generic cloud, where the existing contract permits
them. Neither contract was changed. Development smoke outputs are not campaign
outputs; only the final source-bound local receipt above is quotable.

## Stronger preflight and remaining gate

`compatibility_preflight.py --device gpu` requires an A100, checks package pins,
enables determinism and exercises both arms before calibration. It does not import
CPU-only pytest fixtures. Exact packing/order/mask checks are separate from full
floating model comparisons. GPU-versus-CPU tolerance is frozen at atol `1e-5`,
rtol `1e-4`; CPU equivalence, copied arrays, same-device repeatability and masked
zero gradients require exact equality. It checks eager/traced forward, gradients,
Adam updates, save/reload and fresh-process reload for all four cases. PASS is
written only after completion and artifact/source hashing; source mutation stops.

Calibration now requires that complete GPU receipt. CPU-only, incomplete, stale,
changed-artifact or wrong-runtime receipts fail closed; 11 added tests exercise
packing and receipt contracts. The evaluator verifies the new guard evidence and
binds the calibration back to its smoke receipt. Calibration starts in a fresh
process, so smoke model initialization, training and checkpoints cannot alter
its seed/weight state. The original resource extrapolation and all scientific
acceptance criteria remain intact.

The pending 110-minute proposal counts both failed allocations and retains all
24 frozen jobs within the aggregate ceilings. Neither local PASS nor eventual
GPU smoke PASS releases the full campaign without completed calibration and
its unchanged integrity/headroom gates. No result authorizes real-source work,
publication adoption, covariance or Gate 6. PET remains diagnostic and
method-development; source semantics remain prerequisites for real-data work.
