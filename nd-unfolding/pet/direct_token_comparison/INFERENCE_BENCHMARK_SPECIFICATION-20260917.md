# Per-arm inference benchmark: specification and criteria

**CITABLE FOR:** the predeclared design of a per-arm inference timing measurement.
**NOT CITABLE FOR:** any result — none exists when this is written — and for nothing
about closure, accuracy or representation quality. This measures **cost only**.

Authorized by Joseph on 2026-09-17, verbatim:

> Yes, I authorize a small, bounded per-arm inference benchmark within the remaining
> resource grant, after the matrix completes. Use the saved trained models, identical
> held-out inputs, the same GPU and precision settings, warm-up, and repeated timings.
> Report throughput and timing variability, with preprocessing and model-loading costs
> identified separately. No retraining or changes to the learning comparison.
>
> Finish and report the matrix results regardless of the timing benchmark.

The second sentence governs sequencing: **the matrix result is reported whether or not
this benchmark runs or succeeds.** This is an addendum, never a gate on the comparison.

## Why it exists

The frozen producer instruments per-arm **training** (`reco_fit_seconds`,
`truth_fit_seconds`) and one per-job `wall_seconds`. Per-arm **inference** is not
derivable from the matrix: the non-fit remainder of wall time also contains one shared
fixture build, normalization and serialization, and does not separate by arm. So the
number is measured here or not at all.

## Design

| element | choice |
|---|---|
| models | the **saved trained reco models** from completed matrix jobs, `<stem>.pooled.keras` and `<stem>.direct.keras`. Nothing is retrained. |
| inputs | the **identical held-out split**, built **once** by `make_fixture(rows, 2402)` — the same call the matrix used — and shared across arms and seeds, so identical inputs are true by construction rather than by trusting a rebuild |
| batch size | **1,024**, unchanged from the matrix, since throughput depends on it |
| device & precision | one A100, and the bound `PRECISION_POLICY` — `tf32_enabled: false`, `determinism_enabled: true`, `float32` — asserted at runtime, not assumed |
| warm-up | **3** full passes per arm, discarded, so kernel autotuning and graph tracing are excluded from the reported numbers |
| repeats | **10** timed passes per arm, reported individually |
| seeds | seed **17** as the primary, plus **29** and **43** as model-to-model checks, so a single trained model's quirk is visible |
| ordering | arms measured **alternately** (pooled, direct, pooled, …) rather than in blocks, so any monotonic drift in machine state cannot load onto one arm |

### Sizing, revised after a timeout — 2026-09-17

The first attempt (job `58461843`) **FAILED on `timeout`, exit 124, after 35 minutes**,
with no receipt written. This was a sizing error of mine, not a scientific failure, and
the matrix receipts were verified untouched afterwards.

Measured cause: building the split costs **~407 µs/row**, so ~100 s per call at 250,000
rows, and the script called it **four times** (~6.6 min); the remaining ~28 min went to
**78 full inference passes** (3 seeds × 13 passes × 2 arms) at ~20 s each. Total ≈33 min
against a 2,100 s limit.

Two changes, neither of which weakens the measurement:

* The split is now built **once and shared**, which also upgrades "identical inputs" from
  an assumption about determinism to a property of construction.
* The measurement size is **50,000 rows** rather than 250,000. Throughput is a per-event
  quantity and 49 batches of 1,024 measure it as stably as 245 do; the reported figure is
  events/second with the measurement size stated. Warm-up, repeats and seeds are
  unchanged, because those are what Joseph asked for and what variability needs.

Revised estimate: one ~20 s build plus 78 passes at ~4 s ≈ **6 minutes**.

## What is reported, and separately

1. **Throughput** per arm: events/second, from timed passes only.
2. **Timing variability** per arm: mean, standard deviation, min, max, and the
   coefficient of variation across the 10 repeats.
3. **Model-loading cost**, timed separately and excluded from throughput — it is a
   one-off per process, not a per-event cost.
4. **Preprocessing cost**, timed separately and excluded from throughput — building
   and packing the fixture is shared work that would otherwise inflate both arms.
5. The measured `PRECISION_POLICY` and device string, so the numbers are attributable.

## Acceptance criteria

These decide whether the *measurement* is trustworthy, not whether an arm is better.

| id | requirement |
|---|---|
| B1 | Both arms produce predictions on identical inputs; the input digest is recorded and identical across arms |
| B2 | The measured precision policy equals the bound `PRECISION_POLICY`, and the device string names a GPU |
| B3 | Coefficient of variation across the 10 timed passes is **< 10%** per arm; above that, the machine was too noisy and the numbers are reported as indicative only rather than quoted |
| B4 | The three seeds agree on the **direction** of any per-arm difference; if they disagree, report no direction |
| B5 | Model loading and preprocessing are reported as separate line items, never folded into throughput |

Failing B3 or B4 does not invalidate the matrix result, and does not become a claim
about either representation. It means the cost comparison is inconclusive and is
reported as such.

## Boundaries

- **No retraining, no refitting, no change to any learning artifact or receipt.** The
  benchmark opens saved models read-only and writes only its own timing output.
- It cannot alter, re-reduce or re-interpret the frozen comparison, and its numbers do
  not enter the acceptance criteria.
- Cost is not quality: a faster arm is not thereby better, and this document must not
  be cited as evidence about accuracy.
- Bounded to one short allocation inside the remaining grant, which after the matrix
  is roughly 229 GPU-hours against a 290 ceiling. No simultaneous PET allocation.
- A technical failure stops it and is reported; the matrix result proceeds regardless.
- Synthetic only. No real-source reads, no adoption, no covariance, no Gate-6 action.
