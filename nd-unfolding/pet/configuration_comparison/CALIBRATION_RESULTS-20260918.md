# Calibration milestone: measured results

**CITABLE FOR:** the measured throughput ratio, and the characterization of the candidate
`E_avail` endpoint.
**NOT CITABLE FOR:** any ratified threshold, any closure result, or any adoption. The
reference values below are a **reference model, not a proven bound**.

Receipts: `receipts/20260918-calibration/`. Jobs **58527080** (GPU) and **58527254**
(CPU), both `COMPLETED`.

---

## 1. Cost calibration — the ratio is measured

One **NVIDIA A100-SXM4-80GB**, both arms on the **same physical GPU** verified by UUID
(`gpu.csv`, and the reducer matched on `primary_uuid`). Our arm ran under
`tensorflow 2.15.0 / keras 2.15.0`; his under `pytorch/2.6.0`, with the upstream source
pinned by tree digest `bd832627…`.

| tokens | ours @512 | ours µs/example | his @512 | his µs/example | **r (matched)** | r (his native 2048) |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 18.71 ms | 36.55 | 52.75 ms | 103.02 | **2.82** | 2.47 |
| 33 | 28.37 ms | 55.41 | 122.07 ms | 238.42 | **4.30** | unavailable |

**Three things this settles.**

1. **`r` is single-digit, not 1 and not 80.** The 58.7× parameter ratio was a bad proxy
   and the earlier CPU figure was overhead-dominated, as its own two-batch control
   showed. The complete comparison is affordable — see `ROUTE_TO_PRETRAINED_COMPARISON`.
2. **`r` grows with token count**, 2.82 → 4.30. Pricing the completion configuration
   (Gregor's 33-token cap) at our current 12-token cap would have understated it by
   about half. This is why the plan promised both.
3. **His native batch 2048 is not always runnable.** It ran at 12 tokens and raised
   `CUDA error: invalid configuration argument` inside PyTorch's
   `scaled_dot_product_attention` at 33. Projections therefore use the **matched-batch**
   ratio — same batch, same tokens for both arms — so the number is not a batch artifact
   and the missing cell degrades reporting rather than costing.

**The cross-framework qualification stands.** Ours is TensorFlow and his is PyTorch,
because the Keras port does not exist yet. These are **device-matched and
framework-unmatched** figures; a same-framework `r` needs the port.

**Measured and projected are separate.** The table above is clock readings. Evaluation
GPU-hours are derived from the budget model and carry the fit-only caveat: our 0.97
GPU-h at 12 tokens sits just under the contract's 1.1–1.3 for a nominal train, the
difference being the fixture build, normalization, reweight-all inference and
serialization, which do not scale with the backbone.

---

## 2. The candidate `E_avail` endpoint — characterized

Read of `G2_FPS_MEFHC_P12.npz`, digest **verified** against the committed receipt.
**49,152,885** rows; **49,150,928** truth-passing; **20,573,521** reco-passing; **zero**
non-finite `E_avail`. Candidate choices were committed before the job ran.

**Distribution and tilt.** p25 **0.531**, p50 **1.459**, p75 **3.160** GeV, IQR **2.629**.
The candidate tilt (amplitude 0.35, clip 3.0, imported from the frozen closure driver)
produces per-event weights in **[0.712, 2.471]**.

**Per-bin acceptance** on the campaign's canonical `E_avail` axis:

| bin (GeV) | 0–0.1 | 0.1–0.2 | 0.2–0.4 | 0.4–0.8 | 0.8–1.5 | 1.5–3.0 | 3.0–100 |
|---|---:|---:|---:|---:|---:|---:|---:|
| acceptance | 0.671 | 0.717 | 0.673 | 0.592 | 0.474 | 0.331 | **0.219** |
| displacement | 0.015 | 0.014 | 0.026 | 0.035 | 0.031 | 0.015 | **0.137** |

Acceptance falls monotonically above 0.2 GeV, and **half the injected displacement sits
in the last bin, which has the worst acceptance**. That is the regime a better hadronic
representation would be expected to help, and it is where the endpoint puts its weight.

### 2.1 The pT reference does not transfer — now with the actual number

| domain | reference model, k=3 |
|---|---:|
| `E_avail`, displacement-weighted | **0.7131** |
| `E_avail`, truth-mass-weighted | 0.7552 |
| (pT, p‖), displacement-weighted | 0.6950 |
| *pT endpoint's adopted value, for contrast* | *0.618228* |

The earlier argument was that the reference spans 0.017–0.973 across weightings and so
cannot be inherited. It is now concrete: **the candidate endpoint's reference is 0.713,
not 0.618.** An adequacy criterion built on the inherited value would have been wrong by
0.095 in recovery units — about five times the non-inferiority margin under discussion.

**It remains a reference MODEL, not a proven bound.** It assumes displacement reaches a
cell only through that cell's acceptance; `omnifold.py:218-220` lets a smooth learner
transport a tilt across cells, and BEN-038 measured a band at `E_w[r] = 1.0333`, above
the modelled reachable value. Graded ASSUMED.

### 2.2 Scoring off-variable loses 42 % of the injected shape

Total injected displacement is **0.2733** on the `E_avail` axis and **0.1574** on the
(pT, p‖) reporting grid. **The reporting grid sees 57.6 % of the injected shape; 42.4 %
is lost to projection.** That is the quantitative form of "score where you injected",
and it is the reason the `E_avail` domain is primary and the reporting grid is a
co-reported diagnostic with no decision weight.

### 2.3 A caveat that cuts against the binning, and must not be read the other way

The acceptance-stratified census finds **no `E_avail` bin below 0.05** — minimum
acceptance 0.219 — where the (pT, p‖) grid has 37 cells below 0.01 holding 25.9 % of
truth mass.

**This is not the binning hiding poorly accepted regions, and it is not the binning
being better.** It is 1-D projection **averaging over** them: each `E_avail` bin
integrates (pT, p‖) cells whose acceptance ranges from 0.004 to 0.89. The poorly accepted
regions are still in the truth mass; they are no longer resolved.

Two consequences, both stated rather than resolved here:

* the (pT, p‖) co-report is **necessary**, not decorative — it is the only place the
  low-acceptance structure stays visible;
* a **2-D domain** (`E_avail` × p‖, or `E_avail` × acceptance stratum) should be
  considered, so the region is resolved rather than averaged. That is a scientific choice
  and belongs with U3, not with this measurement.

Strata as measured: 3 bins in acceptance [0.05, 0.5) carrying **67.0 %** of truth mass,
4 bins in [0.5, 1.0] carrying **33.0 %**.

---

## 3. Spend

| | GPU device-hours | CPU core-hours |
|---|---:|---:|
| 58526592, 58526558, 58526214, 58526817 — repairs and cancellations that measured nothing | 0.027 | <0.01 |
| **58527080** cost calibration, COMPLETED 00:01:18 | **0.022** | — |
| **58527254** `E_avail` characterization, COMPLETED 00:00:56, 10 cores | — | **0.16** |
| **milestone total** | **0.049 of 2 authorized** | **0.16 of 8 authorized** |
| cumulative campaign | **≈16.05 of 600** | |

Four submissions measured nothing and each is counted: two were my own defects
(`TF_USE_LEGACY_KERAS` hardcoded, then the whole arm lost to one unrunnable cell), and
two were the consequence of moving the deployed checkout out from under a pending job's
HEAD check — twice. The GPU job now runs from its own checkout so the two cannot collide.

---

## 4. What this does not establish

* No threshold is ratified. U1–U8 remain open and are Joseph's.
* No closure, recovery or accuracy result exists for either arm.
* The timing is **cross-framework**; the same-framework ratio needs the Keras port.
* The calibration timed the **scratch** backbone. A pretrained checkpoint changes initial
  weights and not the architecture, so per-step cost should carry over — an expectation
  from identical architecture, not a measurement.
* Nothing here discharges `OI-71`.
