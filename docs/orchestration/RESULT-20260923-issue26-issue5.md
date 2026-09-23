# RESULT 2026-09-23 — KNOWN_ISSUES #5 and #26 studies

Plan and verdict rules (committed before any submission): `PLAN-20260923-issue26-issue5-studies.md`
(commit `68a266a5`). Receipts: `docs/orchestration/state/result-20260923-issue26-issue5/`.
This is a receipt document, not a ledger row; nothing here changes a central value, covariance or
note text. A proposed systematic below is a proposal for Joseph.

---

## Issue #5 — low-p∥ sum-ratio gradient: **ABSENT on the frozen product; FIXED by a prior change**

**Instrument.** `2d-unfolding/strip_ratio_receipt.py` at commit `5760a785`, run on a Perlmutter
login node (seconds, no batch job) from the clean clone
`/pscratch/sd/j/josephrb/MINERvA-OmniFold-strip-20260923` under `mnv_guarded_run.py`
(`outside_expect_root=0`). The first attempt at `68a266a5` refused (exit 3): the paper TH2D axis
edges are cosmetic rounding (max area deviation 7.1 % from the authoritative `bin_mapping` edges),
so strip areas now come from the authoritative edges; the verdict rule did not change.

**Inputs (sha256).**
- ours, 2D production `2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root:hXSec2D` — `142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5`
- second estimator, 3D E_avail marginal `3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root:hXSec2D` — `0dd94830821576a3b060fae2d4a20564610c535ed06046cd1eb05cd11885dd59`
- paper `minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root` — `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3`

**Receipt.** `state/result-20260923-issue26-issue5/strip_ratio_receipt.json`, sha256
`68324ee95e50942b05c6d102b1ea084b63c6909a995d1fef9a50def46716f935` (plus its console log).

**Measured (185-bin strict interior, area-weighted strip integral, ± paper TotalCov):**

| p∥ strip (GeV/c) | 2D production R | 3D marginal R | April 2026 (Phase 11, post-MINOS fix) |
|---|---|---|---|
| 1.5–2.0 | 1.091 ± 0.125 | 1.065 ± 0.125 | 0.60 |
| 2.0–2.5 | 1.013 ± 0.068 | 1.014 ± 0.068 | 0.61 |
| 5.0–6.0 | 1.014 ± 0.046 | 1.015 ± 0.046 | 0.85 |
| 10–15 | 1.010 ± 0.049 | 1.011 ± 0.049 | 0.90 |
| 20–40 | 1.053 ± 0.050 | 1.120 ± 0.050 | 1.00 |

Contrast `R(1.5–2.5) − R(20–60)`: 2D **−0.013 ± 0.085 (−0.16σ)**; 3D −0.064 ± 0.086 (−0.74σ).
Both masks (205 reported, 185 interior) and both estimators: **GRADIENT ABSENT** (both clauses of the
predeclared rule hold). **Power control:** the same instrument on the 2D product × the historical
gradient returns GRADIENT PRESENT at **−6.8σ** (3D: −7.4σ), so the null is not blindness.

**Cause.** The 0.6→1.0 gradient was measured 2026-04-25 on a pre-Phase-16 product. The Phase-16
input-completeness (efficiency-denominator) bug, found and fixed 2026-05-08/09
(`evidence/prepublication-2026-08-20-0b329e8a:2d-unfolding/2D_OMNIFOLD_RUN_LOG_ARCHIVE.md:441-775`,
which already records "the strip-by-strip σ/paper gradient … is gone"), was the cause; Phases 17–18
replaced the division with native misses (c = 1). The row and `2D_OMNIFOLD_REFERENCE.md:292-326` kept
describing the April state, and the 2026-06-10 quality-cut diagnostic tested that stale premise.
This commit adds a dated re-measurement note to the reference; it does not edit `KNOWN_ISSUES.md`.

**Status for the row owner:** FIXED (by the Phase-16 change), now receipted. No systematic is proposed:
the residual strip deviations are within the paper's own strip uncertainties. What this does *not*
cover: the FPS p∥ < 1.5 region (no paper reference exists there) and any reco-level MINOS-match
efficiency modelling question beyond its effect on this ratio.

---

## Issue #26 — sensitivity to the 1.17 reco-E_avail scale: **IN FLIGHT**

Array `58794336` (12 tasks, `nd-unfolding/sbatch_eavail_scale_study.sh`, study checkout
`/pscratch/sd/j/josephrb/MINERvA-OmniFold-eavailscale-20260923` at `68a266a5`, outputs in
`/pscratch/sd/j/josephrb/eavail_scale_20260923/`). Results are recorded below when the tasks finish.
