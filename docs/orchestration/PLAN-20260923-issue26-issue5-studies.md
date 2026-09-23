# PLAN 2026-09-23 — KNOWN_ISSUES #26 (1.17 E_avail scale) and #5 (low-p∥ sum-ratio gradient)

**Authorization.** Joseph approved both studies on 2026-09-23 (relayed by the orchestrating
session): #26 as a SENSITIVITY STUDY, #5 as INVESTIGATE NOW. Every job below is < 12 h, under the
standing single-job approval. This plan is committed **before** anything is submitted; the verdict
rules are fixed here and applied by code, not by hand.

**What neither study can authorize.** No central value, covariance, or note text changes. A
"proposed systematic" is a proposal for Joseph. All study outputs are `NONQUOTABLE-DIAGNOSTIC.*`.

---

## 1. Issue #26 — sensitivity to the reco-E_avail scale 1.17

### 1.1 Where the constant enters (read, not assumed)

`CVUniverse::NewEavail()` (`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:185-193`)
returns `1.17 × (tracker + ECAL recoil − muon fuzz)`. In `runEventLoopOmniFold.cpp` it feeds
exactly three stored branches — `sim_eavail` (:1178, reco-passing signal only, else `-9999`),
`sim_background_eavail` (:1460), `measured_eavail` (:1591) — and **no cut and no other variable**
(reco `q3` and `W` use `<tree>_recoil_E`, not `NewEavail`). Truth `MC_eavail` is
`GetEAvailableTrue()` and is untouched. So changing `1.17 → k` is **exactly** multiplying those three
columns by `r = k/1.17` after reading. No event-loop rerun is needed.

In the 3D and 5D drivers (`3d-unfolding/unfold_3d_omnifold_unbinned.py`,
`nd-unfolding/unfold_nd_omnifold_unbinned.py`, both `--estimator lgbm`, default `purity` background
mode) reco E_avail enters in two places only:

1. the step-1 classifier feature (data vs MC reco) — a GBDT is invariant to a common positive rescale
   of a feature up to histogram-binning/rounding, and a common rescale of data and MC is a common
   rescale of the feature;
2. the purity down-weight `max(0, data − bkg)/data` binned in reco `(p_T, p∥, E_avail[, q3, W])` on the
   fixed `E_avail` edges `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100]` GeV — **not** scale-invariant, because
   events migrate between fixed reco bins; its size is bounded by the ~0.35 % background fraction.

**Prediction (stated before running):** a common rescale is inert to within the run-to-run floor plus
a small purity-binning term. This is a prediction to test, not a result.

### 1.2 Runs (one array, `nd-unfolding/sbatch_eavail_scale_study.sh`, 12 tasks)

Each task runs the unmodified production driver via `nd-unfolding/eavail_scale_study.py`, which
scales the three columns (reco-passing entries only; the `-9999` sentinel is kept), counts that each
patched reader ran exactly once, checks `Σ after = r Σ before`, and logs which module files executed.
Launched through `nd-unfolding/mnv_guarded_run.py --expect-root <study checkout>` (OI-136).

| task | tag | product | r_MC | r_data | meaning |
|---|---|---|---|---|---|
| 0 | `c3_ctrl` | 3D (seed 1) | 1 | 1 | control |
| 1 | `c3_rep` | 3D | 1 | 1 | identical repeat → run-to-run floor |
| 2 | `c3_k100` | 3D | 1/1.17 | 1/1.17 | k = 1.00 (no calibration factor) |
| 3 | `c3_m10` | 3D | 0.9 | 0.9 | k = 1.053 (−10 %) |
| 4 | `c3_p10` | 3D | 1.1 | 1.1 | k = 1.287 (+10 %) |
| 5 | `c3_pow` | 3D | 1 | 1/1.17 | **power control** (data-only) |
| 6–11 | `c5_*` | 5D `eavail,q3,W` (seed 42) | same pattern | | same six roles |

3D config = the frozen 3D production (`3d-unfolding/sbatch_unfold_3d.sh`: MEFHC 3D omnifile, 5 iter,
lgbm, seed 1, `--use-weights`). 5D config = the 5D central (`docs/ESTIMATOR_REGISTRY.md`
`omnifold-5d-lgbm`: `runEventLoopOmniFold_5D_MEFHC.root`, 5 iter, lgbm, seed 42). The frozen
products are compared against `*_ctrl` for information only; the decision uses only this campaign's
matched runs, so no cross-deployment drift enters the verdict.

**Why these values.** No calibration rationale for 1.17 exists (OI-31), so no range can be derived
from one. `k = 1.00` is the extreme "remove the factor" point (−14.5 %); ±10 % is an **assumed** stress.
Because the prediction is scale invariance, the three points test whether the answer depends on the
magnitude at all. The data-only power control is **not** a response systematic and is not quoted as
one — it exists to show the pipeline responds to reco E_avail, so a null is informative. (The
separate response-mismatch closure in `nd-unfolding/RESPONSE_MISMATCH_CLOSURE.md` is not run here.)

### 1.3 Cost

32 CPUs (1/8 node), 96 GB, 6 h wall cap per task, `shared` QOS. Cap: 12 × 6 h × 1/8 = **9 node-h**.
Expected: the 3D production took ~14 min on a full node; 5D sweep legs are allotted 4 h on 32 CPUs.
Expected total ≈ 12 × 1.5 h × 1/8 ≈ **2–3 node-h**.

### 1.4 Comparison (`nd-unfolding/compare_eavail_scale.py`)

Histograms: 3D `hXSec3D, hXSec_eavail, hXSec2D`; 5D `hXSecND_flat, hXSec_eavail, hXSec_W, hXSec2D`.
Per bin on the control's positive support: `|variant/control − 1|` median, p95, max, and the
integral ratio (contents × bin volume).

### 1.5 Verdict rule (applied by the comparison script)

With `F` = the control-vs-repeat metrics and `m_ML = 0.0045` (the 3D lgbm per-bin seed band quoted in
`3d-unfolding/3D_OMNIFOLD_STATUS.md`; used for 5D too, which is conservative since a 5D band is not
smaller):

* **INERT** iff for every histogram: median ≤ max(2 F_median, 0.1 m_ML), p95 ≤ max(2 F_p95, 0.1 m_ML),
  and |integral − 1| ≤ max(2 |F_int − 1|, 1e-4).
* else **SENSITIVE**.
* The power control must come out **SENSITIVE**; if it does not, the study is uninformative (exit 4).

**What is proposed from each outcome.** INERT for all three common-scale points → propose that the
common 1.17 factor carries **no** uncertainty on the unfolded result, recording the measured maximum
shift as the bound; state explicitly that a data/MC *relative* E_avail response uncertainty is a
different quantity, not covered. SENSITIVE → propose a systematic equal to the per-bin envelope of the
±10 % variants (k = 1.00 reported alongside), as a proposal only.

---

## 2. Issue #5 — does the low-p∥ sum-ratio gradient persist?

### 2.1 What the record says

The "sum-ratio" is the per-p∥-strip ours/paper cross-section ratio (Phase 10, 2026-04-25, evidence
tag `prepublication-2026-08-20-0b329e8a:2d-unfolding/2D_OMNIFOLD_RUN_LOG_ARCHIVE.md:153-240`: 0.60 at
p∥ 1.5–2 rising to 1.00 above 20 GeV/c after the MINOS-match fix). The same archive's Phase 16
(2026-05-08/09, :441-775) found an efficiency-denominator (OmniFold input-completeness) bug and says
the gradient **"is gone"** after the fix; Phases 17–18 then replaced the completeness division with
native misses (c = 1 exactly). `2D_OMNIFOLD_REFERENCE.md:292-326` and the 2026-06-10 quality-cut
diagnostic still describe the April numbers as current. **No committed receipt measures the strip
ratio on the frozen Phase-18.2 product.** That is the gap this study closes.

### 2.2 Run (login node, seconds; no batch job)

`2d-unfolding/strip_ratio_receipt.py` on the frozen production
`2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root` (sha256 `142a45b0…`, the input of
`receipt_model_chi2_2d.json`) and, as a second estimator, the 3D production's E_avail marginal
`hXSec2D`. Masks: 205 reported bins and the 185-bin strict interior of the historical metric. Both
area-weighted and bare-sum strip ratios are printed. **Power control built in:** the same instrument
is run on ours × the historical gradient; if that is not flagged, exit 4 and no verdict.

### 2.3 Verdict rule (in the script)

On the 185-bin interior: **GRADIENT ABSENT** iff (a) `R(1.5–2.5) − R(20–60)` is within 2σ of its
paper-TotalCov error, and (b) each p∥ < 2.5 strip has |R − 1| ≤ 2σ_strip + 0.05. Otherwise PRESENT.

**Outcomes.** ABSENT → issue #5's premise does not hold on the frozen product; the cause is the
Phase-16 denominator bug, already fixed; record as FIXED-BY-PRIOR-CHANGE with this receipt.
PRESENT → proceed to a cause search (MINOS-match efficiency vs p∥ by playlist, from the omnifile)
under a separate plan amendment committed before any job.

Receipts land in `docs/orchestration/RESULT-20260923-issue26-issue5.md` and
`docs/orchestration/state/result-20260923-issue26-issue5/`.
