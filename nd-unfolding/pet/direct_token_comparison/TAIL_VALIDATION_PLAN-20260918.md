# GPU-only tail validation: plan, allocation, and stop conditions

**Criteria frozen 2026-09-18 in `VALIDATION_CRITERIA-20260918.json`**, sha256
`e8c7c432b80aa3b138d751bb80ab267f76ae2d6c3443714c18e32a21aeabc659`. Every threshold
below is read from that file at run time and its digest is recorded in every receipt, so
a threshold relaxed after seeing a failure changes the digest and is visible in the
evidence rather than silent.

**Authorized 2026-09-18** for implementation and execution within ≤1.5 GPU-hours, ≤4
submissions, ≤45 minutes per submission, ≤5 GiB, with repaired submissions counting as
retries. The
design below is specified to the point where it can be implemented without further
choices; the bounds and the allocation are what need ratifying first.

Chosen by Joseph on 2026-09-18: validate GPU-only training across the **intended
multiplicity range** rather than restrict the study to low multiplicities. Not a blanket
exemption — release is per width, and a width that fails any check is not released.

## 0. Four corrections, applied before anything below is read

These came from Joseph and two of them withdraw claims I made in the go/no-go packet.

1. **Neither direction nor magnitude transfers automatically** from a synthetic effect
   to production. I had claimed direction transfers. It does not: in the fixture all
   signal is typed, in production typed objects supplement an informative cluster cloud,
   and a routing that wins when typed objects are the whole signal can lose when they
   are largely redundant with it. Sign reversal is available. Corrected in
   `COMPARISON_PROPOSAL-20260917.md` §2.5.
2. **Noise-only generic inputs do not establish an upper bound.** My argument was that
   free attention capacity maximises the typed effect. The opposite argument is equally
   available — under production's fixed attention budget the model must tell similar
   objects apart, which could make per-object resolution matter *more*. No monotone
   relation exists, so the bound was unjustified and is withdrawn.
3. **A null P3 does not make P1 irrelevant.** P3 (B−A) asks whether *pooled* typed
   objects help. If pooling is the wrong routing, P3 can be null precisely because of
   the effect P1 tests. P3 null with P1 positive is coherent and informative: typed
   objects help only if routed individually. The three contrasts are read **together**,
   not in sequence, and the "P3 is read first" line in the packet is withdrawn.
4. **The 25.8-point scatter is a planning assumption, not measured power for this
   endpoint.** It came from the four-object fixture, two arms, and a ratio to the pooled
   arm rather than to arm A. Every table that uses it is relabelled; the sd that sizes
   Stage 2 is the one the pilot measures here, and it may be larger.

## 1. Exactly which requirement changes

One clause, plus the three that share its nature. In `optimizer_equivalence.validate`:

**Release is two-tier, corrected 2026-09-18.** Cross-device checking is not dropped
wholesale. Every width is run through the **full** cross-device comparison first:

* **Tier 1** — the cross-device gate passes → the width is released under the
  **unchanged** criteria, with nothing dropped. Measured: this covers widths up to 18
  objects in a family.
* **Tier 2** — a cross-device sub-check fails → the width is released only if every
  failing sub-check is in the predeclared exempt list, the whole GPU-only battery
  passes, and the receipt flags the width tier 2 so later results carry that scope.

Anything failing **outside** the exempt list is a hard stop, including the
device-independent identity of initial weights. And a cross-device sub-check that
**passes** at a tier-2 width is required to keep passing: a regression there is a hard
stop, not a newly granted exemption. So the table below describes what may be exempted
at tier 2, not what is discarded everywhere.

| lines | clause | status under GPU-only |
|---|---|---|
| **83-97** | **the CPU-vs-GPU comparison of post-Adam-step weights**, `compare_named(a, b, exact=exact_cpu, excluded=weight_{key_bias})`, with the key-bias error recorded separately | **exemptible at tier 2 only**, and recorded as a measurement either way (V6) |
| 78 | initial weights identical across devices, `exact=True` | **retained** — it is a seeding property, not a device property, and costs nothing |
| 80 | gradients agree across devices | exemptible at tier 2 only; **recorded** (V6) |
| 81 | predictions agree across devices | exemptible at tier 2 only; **recorded** (V6) |
| 125 | common-operand Adam replay agreeing across devices | exemptible at tier 2 only; **recorded** (V6) |
| 76 | same-device repeatability, `initial` vs `repeated`, `exact=True` | **retained unchanged, and strengthened** (V2) |
| 77 | eager vs `tf.function` agreement | **retained unchanged** (V3) |
| 127 | float64 Adam reference, **key-bias weight only** | **retained and extended to all 42 weights** (V4) |

Nothing else in the gate changes, and the campaign's tolerances are reused rather than
replaced: `ATOL = 1e-5`, `RTOL = 1e-4` (`compatibility_preflight.py:32-33`).

## 2. Why the cross-device updated-weight requirement is not necessary here — and what it was doing

**The endpoint is a paired difference between arms computed on one device**, from one
fixture, one shared initialization and one shared batch plan. "Would a different device
reproduce these weights" is a *portability* property. What the contrast's validity
actually needs is that the only systematic difference between arms is the
representation, that the optimizer does what its formula says, and that a re-run
reproduces the numbers.

That said, the requirement was not decorative. It was doing three jobs, and each needs
replacing rather than assuming away:

| what it protected | why the replacement is adequate |
|---|---|
| **(a) the gradient computation itself** — a second implementation recomputing the same derivatives | the float64 reference cannot do this, because it *inherits* the captured float32 gradients as operands. Replaced instead by a **finite-difference check** (V5), by **permutation invariance** (V7), and by continuing to **measure** the cross-device gradient difference without requiring it (V6) |
| **(b) an independent second opinion on the Adam step** | replaced by something stronger and different in kind: the **float64 evaluation of the pinned Adam formula on identical operands** (V4), extended from one weight to all 42. Two float32 implementations agreeing does not show either is right — they can share a systematic error, which is exactly why the gate already exempts the key-bias weight. A float64 reference is a direct statement of distance from exact arithmetic |
| **(c) device- or shape-specific artefacts** that could favour one arm | replaced by **arm-symmetry of the numerical residual** (V8), **permutation invariance at high multiplicity** (V7), and **overlap calibration** against the cross-device gate where it still passes (V9) |

**What remains unprotected — corrected 2026-09-18.** The first draft said an error
surviving every check would be arm-symmetric and would therefore **cancel** in a paired
contrast. That was not established and is withdrawn. An undetected error can be
arm-correlated *below the resolution of V8*, and nothing here propagates a weight-space
residual into the closure statistic, so "cancels" was an assumption wearing the clothes
of an argument.

What is claimed instead is bounded and measured:

* residuals are bounded at the stated tolerances;
* their **measurable** arm-asymmetry is bounded by V8, at V8's own resolution and no
  finer;
* **V13 bounds spurious contrast end to end, in the endpoint's own units**: two arms
  configured *identically* must produce the same closure to within repeatability, and
  the measured difference is a direct bound on how much contrast the pipeline can
  manufacture. This is the check that replaces the withdrawn cancellation claim, and it
  exists precisely because no rigorous weight-space-to-closure propagation is available.

Residual risk below those bounds is **acknowledged, not argued away**. Absolute closure
values additionally keep a device-dependence caveat that the contrasts do not, and it is
recorded on every absolute number the campaign later quotes.

## 3. The checks

Each is a predeclared bound, and each says what it does when it fires. "Not released"
means the width is excluded from the fixture ladder; "hard stop" means the route fails
and I return to Joseph.

| id | check | bound | on failure |
|---|---|---|---|
| **V1** | same-device repeatability, in-process: `initial` vs `repeated` | bitwise | hard stop |
| **V2** | same-device repeatability **across fresh processes**: all 42 weights after N steps from the same seed | bitwise | hard stop — a paired-seed design whose runs are not reproducible is unsound |
| **V3** | eager vs `tf.function` | ATOL/RTOL | hard stop |
| **V4** | **float64 Adam reference, all 42 weights** (today: the key bias only) | ATOL/RTOL | width not released |
| **V5a** | finite-difference **plateau**: the estimate at h ∈ {3e-2, 1e-2, 3e-3} must agree within 20% | no plateau → the estimate is uninformative at that width | width not released |
| **V5b** | finite-difference accuracy at the measured optimum `h = 1e-2·max(abs(θ), 1)`, over sampled coordinates with `abs(grad) ≥ 1e-3` | **max relative error ≤ 5e-3**, set from measurement (below) | width not released |
| **V6** | cross-device gradient, prediction and updated-weight differences — **measured and recorded, not required** | none; reported per width | never fails; it is the evidence that quantifies what was dropped |
| **V7** | permutation invariance: permute objects within each family, compare predictions | ATOL/RTOL | width not released |
| **V8** | **arm symmetry** of the V4 residual: arm-to-arm difference in mean and max residual | within ATOL/RTOL | **hard stop for the whole route** — an arm-correlated numerical bias is the one failure this substitution cannot absorb |
| **V9** | overlap calibration: at widths where the cross-device gate **passes** (measured: ≤18 objects in a family), the GPU-only battery must also pass | one-directional | hard stop — the substitute is miscalibrated |
| **V10** | checkpoint save and reload: reloaded predictions vs original | bitwise, as the frozen preflight requires | hard stop |
| **V11** | input/mask correctness: counts equal segment-id bincounts; token masks all true within a bucket; `enabled` flags match the arm's declaration; and **masked-slot invariance** — perturb values under inactive masks and require bitwise-identical predictions | bitwise for the invariance | hard stop |
| **V12** | finiteness: all gradients, predictions and weights finite; gradient norms recorded per arm per width | non-finite fails | hard stop |
| **V13** | **duplicate-arm null**: two arms configured identically must give the same closure | spurious contrast ≤ **δ/10 = 1.0 point** | hard stop — this is the end-to-end bound that replaces the withdrawn cancellation claim |

**V5's bound is measured, not asserted.** The first draft asserted 2e-2. A step-size
sweep (`measure_finite_difference_scale.py`, receipt at
`local_validation/20260918-fd/fd-scale.json`) shows the accuracy curve is V-shaped as
expected — truncation falling as h², cancellation growing as eps/h — with the floor at
**h = 1e-2**:

| configuration | p90 relative at optimum | max relative at optimum |
|---|---:|---:|
| pooled, 4 typed objects | 8.40e-05 | 5.44e-04 |
| direct, 4 typed objects | 8.65e-05 | 4.53e-04 |
| direct, 34 typed objects | 5.88e-04 | 6.14e-04 |

So **2e-2 was about thirty times looser than the achievable floor** — a guard no
realistic error could have tripped. The frozen bound is **5e-3**: roughly eight times
the worst measured maximum, which leaves room for degradation at widths beyond those
measured while staying four times tighter than the asserted value. The gradient floor
of 1e-3 exists because relative error on a near-zero gradient measures the denominator
rather than correctness, and V5a re-establishes the plateau **at each width** so the
tolerance is justified there rather than extrapolated from here.

**Why V1's bound is bitwise.** Repeatability should be exact under
`determinism_enabled: true` and `TF_DETERMINISTIC_OPS=1`, so anything short of bitwise
is a real finding.

**Why V7 is not bitwise.** Floating-point addition is not associative, so
`unsorted_segment_sum` over a permuted order legitimately differs in the last places.
ATOL/RTOL is the right bar, and the measured max_abs is recorded so a drift with
multiplicity is visible.

## 4. Integration into the execution path

The width probe cannot release training and will not be asked to. Three mechanisms:

1. **The battery lives in the training producer, not beside it.** A `ValidationBattery`
   is constructed by the four-arm runner and invoked at fixed points of the real run:
   V11 on the actual first batches, V1/V3/V5/V7/V12 at step 0, V4/V6 after the first and
   second optimizer steps, V10 at the end, V2 from a re-executed short run.
2. **Validation runs through the runner's own entry point.** The runner gains
   `--validate-only N`: it builds the real fixture, the real bucket plan, the real
   guard, the real model and the real optimizer, runs N steps, executes the battery and
   stops. The path that gets validated is therefore the path that trains — the only
   difference is where it stops.
3. **Training refuses to start without a covering validation receipt.** The runner gains
   a required `--validation-receipt`; it verifies the receipt's digest and its recorded
   commit against `HEAD`, constructs `WidthSetGuard` from the receipt's **released**
   width set, and fails closed if any bucket in its plan has a width outside it. A
   receipt from a different commit, or one that does not cover the plan, stops the job
   before the first step.

## 5. The validation ladder: the intended multiplicity range

The intended range is what A1 measured: blobs 0-160 (observed max 158 data, 153 MC),
prongs 1-12 (observed max 12), photons 0-2 (the source provides only two).

| widths (photons, blobs, prongs) | why |
|---|---|
| (0,0,1), (0,6,2), (0,12,2) | below and at the measured mean |
| (0,18,2) | the last width the cross-device gate passed — the overlap point for V9 |
| (0,24,2), (0,32,2), (0,48,2), (0,64,2) | the region where the cross-device gate failed, with its max_abs already measured at 1.35e-5 to 4.88e-4 |
| (0,96,2), (0,128,2), (0,160,2) | the tail, to the observed maximum |
| (2,160,12) | the corner: every family at its observed maximum simultaneously |
| (2,12,4) | the operating point with photons and prongs present |

13 widths. Arms **B** and **C** are run at all 13, because their typed geometry varies.
Arms **A** and **D** disable the typed families, so their graph does not change with
multiplicity; they are run at one width, and the receipt records that as the reason
rather than leaving it to inference. Total **28 runs**, plus a re-executed short run at
6 widths for V2, plus the cross-device capture for V6 inside each B/C run.

## 6. Allocation, and how failed submissions count

| item | value |
|---|---|
| expected consumption | **0.8 GPU-hours** |
| **hard ceiling** | **1.5 GPU-hours** |
| wall clock per submission | ≤ 45 minutes |
| expected submissions | 2 |
| **submission cap** | **4** |
| CPU | none beyond the job's own allocation |
| storage | ≤ 5 GiB of receipts and checkpoints |

**Accounting, stated because the last round needed it.** The allocation is measured as
`ElapsedRaw × gpus` summed over **every submission that reaches RUNNING**, receipt or
not. A submission that ends without a receipt is a technical failure: it consumes
allocation and produces no evidence. A repaired launcher is a **new submission, not a
retry**, and it counts the same. The A3 probe's 0.434 GPU-hours are not charged here;
the two are reported separately.

**Stop conditions:**

* **Two consecutive receipt-less submissions** → stop, report, return for a new
  decision. No automatic retries.
* **The submission cap of 4, or the 1.5 GPU-hour ceiling** → stop, whichever comes
  first, even mid-ladder. A partial ladder is reported as partial.
* **Any hard-stop check above (V1, V2, V3, V8, V9, V10, V11, V12)** → stop the route and
  report. In particular a V8 failure ends the GPU-only route, because an arm-correlated
  numerical bias is exactly what this substitution cannot absorb.
* **V4, V5 or V7 failing at a width** → that width is not released; the ladder
  continues. The released set is whatever survives.
* **A partially released range is not self-approving.** If the tail does not validate,
  the outcome is a report and your decision, not a quiet fallback to low multiplicities
  — that is the thing you said you did not want.

## 7. What this cannot establish

It cannot show that GPU-only results are portable; it shows that the paired contrast
does not depend on the property being dropped, and it quantifies what was dropped
instead of assuming it away. It says nothing about closure, nothing about whether the
pilot is worth running, and nothing about transfer to production. Absolute closure
values from any later run carry a device-dependence caveat that the contrasts do not.
