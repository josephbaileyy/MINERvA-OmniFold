# PET representation comparison for Ben

**Drafted 11 September 2026 · last measured 17 September 2026 · diagnostic method
development, not a publication product**

## Recommendation

*Plain language, up front. Both parts are now measured.*

**On individual typed-object tokens versus family pooling: don't adopt them on this
evidence — but don't rule them out either, because the experiment could not settle it.**

Across eight paired seeds on the synthetic fixture, individual-object attention gave a
median closure improvement of **+9.7%** and a mean of **+0.8%**, with six of eight seeds
favouring it. But the seed-to-seed scatter is enormous — a standard deviation of **25.8
percentage points**, from **+26.7%** at best to **−47.6%** at worst — so the 95%
interval on the mean is **[−20.7%, +22.4%]**, straddling zero. A paired t-test gives
**p = 0.50** and Wilcoxon **p = 0.55**. There is no measurable accuracy difference here,
in either direction.

The honest diagnosis is that **the experiment was underpowered, not that the
representations are equivalent.** With the observed scatter, resolving even the +5%
effect the acceptance criteria demand would need roughly **209 paired seeds**; we ran
eight. That is the single most useful number in this report: if we care about this
question, the answer is a better-powered experiment, not a different representation.

What *is* clean is the price, and it is now measured on both sides. Individual-object
tokens cost **≈12% more training time** (per-job ratio **1.118** median across all 24
jobs, 1.026–1.137, **p = 1.2 × 10⁻⁷**) and **≈28% more inference time** (**1.283×**,
12,676 → 9,882 events/second, consistent to three decimals across three trained
models). So on this fixture we would pay a reliable ~12% to train and ~28% to run, to
buy an accuracy change we cannot detect.

**Practical recommendation:** keep family pooling as the default for now. Revisit only
with either a materially better-powered comparison or a fixture where the question
matters more — in particular high object multiplicity, which this fixture never
exercises. Two things I want to be explicit about: six of eight seeds favouring the
direct arm is *suggestive* and I am not dismissing it, and the two negative seeds arose
because **pooling did unusually well there**, not because individual tokens did badly
— but with n = 8 neither observation survives a significance test, so neither is a
finding.

**On aggregate-overflow tokens: don't adopt them as an upgrade — we don't have the
problem they solve.** Gregor's code caps how many objects an event may carry; ours
doesn't cap at all. His cap has two modes, and the one that runs by default simply
throws away the lowest-energy objects past a limit of 150. The aggregate-overflow mode
he also offers is better than that, because it keeps the discarded objects' total
energy in one summary token — but both modes are ways of coping with a cap, and we
currently keep everything. So adopting overflow tokens would mean introducing a cap
first and then partly compensating for it.

That said, **keeping more information is not the same as performing better.** Fewer
tokens is cheaper to train and might even generalise better, so if we ever do need a
cap — for memory or speed — the measurements say: prefer aggregation over truncation,
add an explicit count of how many objects were merged (his version loses that), and
expect the merged objects' positions and timing to survive only as an average. Whether
compression helps or hurts in practice is a separate question we have **not** measured.

One caveat that applies to both halves: the numerical CPU/GPU disagreement we hit along
the way is a floating-point reproducibility property of longer attention sequences —
**not** evidence that individual tokens are scientifically worse. The frozen fixture
never produces the geometry where it appears.

## Measured result of the paired routing matrix

Scope: this compares family-pooled against individual-object attention on the specified synthetic fixture, with information content, model size, training budget, initialization and seeds held identical between arms. It does not compare our complete pipeline against Gregor's, does not settle high-multiplicity overflow performance (the fixture gives every event four objects, so a cap never binds), and says nothing about real data.

### Closure accuracy

Decision under the unchanged frozen criteria: **NO_PASS**.

Paired injected improvement, direct over pooled: mean 95% interval **[-20.730%, 22.365%]** across 8 seeds.

The paired improvement is **inconclusive**: `favorable_seeds`, `material_paired_gain` did not hold, so the measured effect does not clear the frozen thresholds. That is not evidence that either representation is worse.

**Separately**, a safeguard failed: `shuffle-71/projection0`, `shuffle-71/projection1`. A safeguard failure means that part of the run is not interpretable as a clean comparison. It is an additional problem, not an explanation for the inconclusive result above.

### Stability across seeds

| seed | paired improvement (%) |
|---|---:|
| 17 | +17.115 |
| 29 | +18.847 |
| 43 | +8.724 |
| 59 | +10.690 |
| 71 | +0.931 |
| 89 | +26.746 |
| 101 | -47.572 |
| 113 | -28.941 |

Favourable in **6 of 8** seeds; median **+9.707%**, full spread **74.318** percentage points (min -47.572, max +26.746).
Seed-to-seed standard deviation is **25.774** percentage points; compare that against the mean before reading the sign of any single seed as meaningful.

### Compute cost

| quantity | pooled | direct |
|---|---:|---:|
| total training seconds | 9203 | 10166 |
| median per job | 373 | 414 |

Paired direct/pooled training-cost ratio across 24 jobs: median **1.118** (min 1.026, max 1.137). Total job wall time 47778 s.

The frozen producer instruments per-arm **training** only; the non-fit remainder of each job's wall time also contains one shared fixture build, normalization and serialization and does not separate by arm. Inference was therefore measured separately.

#### Inference

| seed | pooled events/s | direct events/s | direct/pooled time |
|---|---:|---:|---:|
| ordinary-17 | 12,676 | 9,882 | 1.283 |
| ordinary-29 | 12,692 | 9,905 | 1.281 |
| ordinary-43 | 12,650 | 9,858 | 1.283 |

Measured on a real GPU over 50,000 held-out events per pass, batch 1024, 3 warm-up passes discarded and 10 timed passes per arm. Individual tokens cost **1.283x** pooled at inference — a larger penalty than at training. Timing was stable: the worst coefficient of variation across all arms and seeds was 0.0203.

Excluded from throughput and reported separately: the shared preprocessing build at 18.7 s once, and model loading at roughly 0.17-0.25 s per model. One first-load reading of 1.6 s is library initialization, not a property of that arm.

Cost is reported, never gated: it does not enter the acceptance criteria, and a cheaper arm does not thereby become the better one.

### The one safeguard that failed, and what it does and does not mean

`shuffle-71` failed both truth-projection checks. The `shuffle` mode is the
label-destroying control: the target is scrambled, so a healthy run should reweight to
near-identity. In that job the direct arm's projection error exceeded the pooled arm's
by **0.0119** and **0.0118** against a **0.01** limit on the difference — a marginal
miss, roughly 19% over. The **absolute** errors (0.0131) sit well inside their own
0.05 bound, and the other seven shuffle seeds pass.

So: one of eight null-control jobs shows the two arms diverging slightly more than the
criteria permit. It is localised and marginal, it does not explain the inconclusive
accuracy result, and it is not evidence about either representation. It does mean this
run is not a clean sweep, and under the frozen criteria that contributes to `NO_PASS`.

I checked whether it pointed to something systematic — whether the direct arm fits
noise more readily, which would have undercut any apparent advantage. It does not
survive testing: across the eight shuffle seeds the direct arm's mean deviation is
higher (0.0065 vs 0.0050) but with Wilcoxon **p = 0.46**, and direct is worse in only
**4 of 8** seeds, a coin flip. I am reporting that as no finding rather than as a
caveat with a number attached.

### Reproducing these numbers

Every figure above comes from the 24 committed receipts, reduced by the unchanged
frozen criteria in [summarize_runs.py](summarize_runs.py) and formatted by
[present_matrix_results.py](present_matrix_results.py). The reducer output and the
statistical analysis, including the power calculation, are committed at
`local_validation/20260917-matrix/`. All 24 jobs verified `COMPLETED 0:0` with matching
terminal markers, 144 artifacts with matching digests, 24 import-guard records
reporting inspected repository origins with no allowances, and `covered_geometry`
confirming zero padded positions in every job.

## What this tests, and what it does not

**It tests one thing:** family-pooled attention versus individual-object attention, on
a specified synthetic fixture, with the information content, model size, training
budget, initialization and seeds held identical between the two arms.

**It does not:**

- **compare our complete pipeline against Gregor's.** His objective (supervised
  regression and pion classification), his event selection, and his metrics all differ
  from ours, so no number here is a head-to-head. What a real comparison would require
  is set out separately in
  [MATCHED_COMPARISON_LADDER-20260916.md](MATCHED_COMPARISON_LADDER-20260916.md).
- **settle high-multiplicity overflow performance.** The fixture gives every event
  exactly four objects, so a cap never binds and compression is never exercised. The
  overflow findings in this report are properties of the *implementation*, established
  by reading and running the pinned code — not measurements of how compression performs.
- **say anything about real data.** This is synthetic method development. Publication
  adoption, uncertainty construction, covariance, statistical pairing, coverage and
  Gate 6 are all outside it, and the outstanding source-semantic questions — photon and
  blob meaning and calibration, prong hypotheses, shared objects and the primary lepton,
  the exact tuple release and time range — remain unresolved.

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

### 1. Individual typed-object tokens — measured, and inconclusive

The 24-job paired matrix ran to completion. Its result is above: a median closure
improvement of **+9.7%** favouring individual tokens, six of eight seeds favourable,
but a 95% interval of **[−20.7%, +22.4%]** and **p = 0.50**, against a reliable **~11%**
training-cost premium. **No accuracy difference is measurable in either direction**,
and the design would need roughly **209 paired seeds** to resolve the effect its own
criteria require.

The earlier cross-device obstacle turned out not to bear on this. The
`variable/direct` CPU/GPU divergence (`query/kernel`, `1.55e-04`) was diagnosed as
Adam amplifying ordinary float32 rounding in a small-gradient parameter, scaling with
attention sequence length — not a defect, and **not evidence that individual tokens
are worse**. Crucially, the frozen fixture never produces that geometry: every event
carries exactly four objects with no padding, which the runtime guard confirmed in all
24 jobs. The stress case was exempted on that basis and is recorded as a failed stress
check rather than waved through.
[Diagnosis](CROSSDEVICE_D1_RESULT-20260915.md); [gate scope](STRESS_SCOPE_AUTHORIZATION-20260916.md).

What the comparison genuinely leaves open is whether individual tokens help where they
should matter most — **high, variable object multiplicity** — which this fixture does
not exercise at all.

### 2. Aggregate overflow — its implementation properties are settled; whether it helps is not

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
- Therefore aggregate overflow is, relative to our current state, a **compression
  scheme rather than an addition**: adopting it means introducing a cap and then
  partially compensating for it.

**A distinction this report must not blur.** Everything above is about *information
retention*, which is an established implementation property. It is **not** a claim
that retaining more information learns better, closes better, or costs less. All three
of those are open, and compression could plausibly help on any of them — fewer tokens
means less padding waste and cheaper attention, so more epochs per unit compute, and a
summed tail token is a coarser but possibly more robust input. Whether compression
improves practical performance is a separate question that we have not measured and
that this report does not answer. What the measurements do support is narrower and
conditional: *if* a cap is imposed, aggregation dominates truncation on information
grounds, and the specific properties below say how to implement it.

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
