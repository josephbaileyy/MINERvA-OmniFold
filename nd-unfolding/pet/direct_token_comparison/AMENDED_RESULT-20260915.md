# Amended GPU preflight: terminal failure — 15 September 2026

**CITABLE FOR:** the terminal state of job `58354898`, the named tensor that failed
the unchanged acceptance tolerance, and the resource charge.
**NOT CITABLE FOR:** any calibration measurement, any resource-headroom verdict, any
routing or representation performance claim, and any statement that the amended gate
was wrong or that a further exemption is warranted.

## Terminal state

| field | measured value |
|---|---|
| job | `58354898` (`pet-amended-calibration`) |
| Slurm state | **FAILED**, ExitCode **1:0** |
| elapsed | `00:04:39` = **279 s** (parent, `.batch` and `.extern` rows all 279 s) |
| window | 2026-09-15T12:46:56Z → 12:51:35Z |
| launcher terminal marker | `FAILED`, `exit-code.txt` = `1` |
| execution commit | `604337880b3e414db8a9f4dd49340e85e4db3705` |
| device | real GPU (`/job:localhost/replica:0/task:0/device:GPU:0`) |

This was a single authorized allocation. **No retry was submitted and none is
authorized.** Calibration never started, so no full job, no frozen matrix and no
overflow compute followed.

## What passed before the stop

- Cluster test suite: **`69 passed, 10 subtests passed`** (40.49 s) and the
  **`25 passed`** adversarial gate controls, with zero failure signatures. These are
  the exact strings the resource gate requires.
- Original-sequence CPU initialization capture: **all eight** case/routing pairs.
- Import-guard records: `tests-guard.json` (4 records), `initialization-guard.json`
  (2), `preflight-guard.json` (1) — every one `REPOSITORY-ORIGINS-INSPECTED` with no
  allowances, and one checkout root, so no `OI-136` path hijack.
- GPU preflight: **three of the four cases it reached passed** and wrote `gate.json` —
  `nominal/pooled`, `nominal/direct`, `variable/pooled`.

The GPU preflight reached only **four of the eight** required pairs. `empty` and
`masked`, both routings, never ran. So the preflight is both **incomplete and failed**;
neither condition alone describes it.

## The failure, with its operand named

The stop is at `optimizer_equivalence.py:85`, the loop that compares the two native
trajectories' complete optimizer state at Adam steps 1 and 2 across 128 tensors
(42 weights + 86 slots), with the single approved exemption applied:

```python
for step in (1, 2):
    a, b = (t["states"][step] for t in traces)
    compare_named(a, b, exact=exact_cpu, excluded=None if exact_cpu else f"weight_{index}")
```

`AssertionError: Equivalence failed: exact=False, max_abs=0.0001443326473236084`.

The failing tensor is **`weight_24`**, which the run's own saved inventory
(`preflight/variable-direct/cpu/variables.json`) records as
`multi_head_attention/query/kernel`, shape `[32, 4, 8]`. It is **not** the exempted
tensor: `weight_27` is `multi_head_attention/key/bias`, shape `[4, 8]`.

This matters because of *why* the exemption exists. The approved amendment rests on
**exact softmax shift invariance** — a key bias adds the same constant to every
allowed key for a given query, so it cancels from softmax in exact arithmetic. The
query *kernel* has no such invariance: it changes the query vector itself and moves
the attention logits directly. The proposal said in terms, "Do not exclude query
bias, other biases or optimizer slots." So this divergence is outside the approved
scope and is a genuine stop, not a candidate for the same treatment.

## Measured pattern across the four reached cases

Re-derivable from the preserved arrays with
[analyze_amended_failure.py](analyze_amended_failure.py); receipt at
[local_validation/20260915-amended-failure/failure-accounting.json](local_validation/20260915-amended-failure/failure-accounting.json).
Tolerance is the unchanged `atol=1e-5, rtol=1e-4`.

| case | prediction max_abs | worst optimizer slot | worst **non-exempt** weight | verdict |
|---|---|---|---|---|
| `nominal/pooled` | 2.38e-07 | 2.24e-08 | 4.17e-07 | WITHIN |
| `nominal/direct` | 8.34e-07 | 1.06e-07 | 3.73e-06 | WITHIN |
| `variable/pooled` | 5.22e-07 | 1.53e-07 | 2.86e-06 | WITHIN |
| `variable/direct` | 8.34e-07 | 2.52e-06 | **1.55e-04** | **OUTSIDE** |

Three further measurements, each of which narrows what the failure is:

1. **Predictions agree to ~1e-6 in every case, including the failing one.** The
   model's output is reproducible across devices; only post-Adam weights diverge.
2. **No optimizer slot exceeded tolerance anywhere** — the worst slot error across
   all four cases and both steps is 2.52e-06.
3. The worst non-exempt error grows monotonically across configurations, from
   4.17e-07 at `nominal/pooled` to 1.55e-04 at `variable/direct` — a factor of
   roughly 370 — and the query kernel is the worst non-exempt tensor in three of the
   four cases.

The exempted key bias is also larger in the failing case (4.58e-05 at step 1,
1.10e-04 at step 2) than in `variable/pooled` (1.20e-05), so the two tensors grow
together rather than independently.

### A hypothesis that has not been tested

The pattern is consistent with the direct route's ragged-to-dense repacking:
`route_tokens` builds per-batch padded token sequences via `packed_row_splits` and
`RaggedTensor.from_row_splits(...).to_tensor()`, so with variable multiplicity the
padded width — and therefore the reduction order of the attention sums — differs
from the pooled route's fixed one-token-per-family layout.

**This mechanism is a hypothesis, not a determined cause.** No command in this run
varied padding width, reduction order or token layout while holding everything else
fixed, so nothing here measures it. It is recorded to direct a future diagnostic, and
it must not be quoted as the established explanation. A prior campaign already
published a mechanism that later proved wrong; the discipline is to leave this
labelled until something measures it.

## Relationship to the earlier FP32 failure, and its limit

The `variable/pooled` key-bias discrepancy measured here at step 2 is
`1.204535385568306e-05`. The FP32 attempt reported its `variable` pooled failure as
`1.20454e-5`. These agree to six significant figures, which is strong evidence that
the earlier failure was this same redundant parameter in this same case.

It remains **magnitude agreement, not reproduction**: the earlier run's failing
weights were never saved, so no byte-level comparison is possible and the historical
reconstruction limit recorded in the handoff still stands. The amended gate passing
`variable/pooled` does not retroactively convert the earlier failed gate into a pass.

## Resource accounting

| quantity | value |
|---|---|
| this allocation | **279 s** (parent, `.batch`, `.extern` all equal) |
| prior conservative charge, remeasured | **742 s** |
| new conservative total | **1,021 s** = 0.283611 GPU-hours |
| reserved CPU-hours consumed | 1,021 s × 32 / 3600 = **9.0756** |
| preserved output | 25,504 KiB across 243 files, far under the 4 GiB cap |
| archive | `pet-amended-failure-20260915.tar.gz`, 15,564,745 bytes, SHA-256 `ad27ca25fe774665c93a06c1d66efbfe5b43f11f265c9ded4b39baf6ace0eb7d` |

The prior charge was remeasured before submission rather than carried forward:
parent `ElapsedRaw` values `79, 111, 95, 105, 128, 216` sum to 734, and the
conservative per-allocation maximum of parent and step rows, `79, 114, 97, 105, 128,
219`, sums to 742. A covering sweep of all 101 account rows since 2026-09-01 found
exactly six carrying `gres/gpu`, and they are exactly the six bound jobids; the later
`z_pilot5d` jobs are CPU-only and belong to a different lane.

Aggregate ceilings are unchanged and remain far from binding: 290 GPU-hours, 9,296
reserved CPU-hours including the 16-hour preparation allowance, 200 GiB. Cap headroom
was never the constraint here — a technical failure was.

## Consequences

- **The 20% resource-headroom gate was never evaluated.** `evaluate_calibration.py`
  fails closed on absent calibration evidence, and there is none. No headroom verdict,
  favourable or otherwise, may be quoted.
- **The frozen 24-job matrix stays unreleased.** It required calibration to pass every
  integrity and headroom gate.
- **The overflow contrast cannot execute.** Its specification is bound in
  [OVERFLOW_SPECIFICATION-20260915.md](OVERFLOW_SPECIFICATION-20260915.md), but that
  document conditions execution on measured calibration and remaining headroom, and
  neither exists. The specification stands as a specification only.
- **No learning-performance result exists** for pooled versus direct routing, for
  overflow handling, or for any representation choice. That position is unchanged
  from before this allocation.
- Shrinking the matrix, loosening a tolerance, exempting the query kernel, or
  replacing a seed are all outside the current authorization. A new decision would be
  needed, and it should be informed by a diagnostic that actually measures the
  mechanism rather than by another exemption.

## What a future diagnostic would need to establish

Stated as requirements, not as an authorized plan:

1. Whether the `variable/direct` divergence is caused by padded-width-dependent
   reduction order, by varying the padding layout while holding initialization,
   operands and gradients fixed.
2. Whether the query-kernel divergence, unlike the key bias, changes predictions or
   the trained model in any way that matters — the measured prediction agreement at
   ~1e-6 suggests the forward pass is unaffected, but two Adam steps are not training.
3. Whether the remaining four pairs (`empty`, `masked` × both routings) pass at all,
   since the run never reached them.
4. Whether a deterministic packing/reduction order for the direct route is achievable
   without changing the scientific model, which is the only remedy that would not
   alter the experiment being compared.
