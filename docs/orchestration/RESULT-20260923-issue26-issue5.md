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

## Issue #26 — sensitivity to the 1.17 reco-E_avail scale: **QUANTIFIED — SENSITIVE by the predeclared rule, at the estimator-noise scale**

**Runs.** Array `58794336`, all 12 tasks `COMPLETED 0:0` (sacct; 11–23 min each, 32 CPUs,
≈ 0.4 node-h total). Script `nd-unfolding/sbatch_eavail_scale_study.sh`, study clone
`/pscratch/sd/j/josephrb/MINERvA-OmniFold-eavailscale-20260923` at `68a266a5` (driver blobs identical
to `main`). Every task's log (`state/.../scale-logs/*.json`) shows each patched reader called exactly
once, `Σ after = r·Σ before` for signal-MC, background-MC and data, sentinel counts preserved, and
`omnifold`/driver modules loaded from the study clone (OI-136 guard: 0 outside-root origins).

**Receipts.** `state/result-20260923-issue26-issue5/compare_3d.json` (sha256 `69e27ea3…ad38`) and
`compare_5d.json` (`77807229…7896`), with console output. Every output ROOT sha256 is listed in the
console output of the cluster run; control roots: 3D `ca0fecca…8f4b`, 5D `ada533fe…2783`.

**Measured** (|variant/control − 1| over the control's positive support; integral = Σ content × volume):

| product / hist | repeat floor (median) | k = 1.00 median / p95 / max | k = 1.053 (−10 %) median / p95 | k = 1.287 (+10 %) median / p95 | integral ratio (k=1.00 / −10 / +10) |
|---|---|---|---|---|---|
| 3D `hXSec3D` (1431 bins) | 4e-14 | 0.47 % / 3.2 % / 9.8 % | 0.53 % / 2.5 % | 0.42 % / 2.8 % | 0.99972 / 0.99972 / 0.99999 |
| 3D `hXSec_eavail` (7) | 1e-14 | 0.11 % / 0.30 % / 0.33 % | 0.08 % / 0.29 % | 0.08 % / 0.15 % | same |
| 3D `hXSec2D` marginal (205) | 3e-14 | 0.21 % / 1.2 % / 3.4 % | 0.17 % / 0.88 % | 0.24 % / 1.3 % | same |
| 5D `hXSecND_flat` (10694) | 6e-14 | 0.58 % / 2.8 % / 9.9 % | 0.54 % / 2.6 % | 0.67 % / 2.7 % | 0.99999 / 1.00023 / 1.00006 |
| 5D `hXSec_eavail` (7) | 4e-14 | 0.03 % / 0.22 % / 0.28 % | 0.05 % / 0.18 % | 0.06 % / 0.23 % | 0.99993 / 0.99993 / 1.00000 |
| 5D `hXSec_W` (6) | 3e-14 | 0.09 % / 0.24 % / 0.26 % | 0.06 % / 0.26 % | 0.02 % / 0.10 % | same |

**Power control** (data only at k = 1.00, MC at 1.17): 3D `hXSec3D` median 18.9 %, integral 0.9894;
5D `hXSec_eavail` median 11.9 %, integral 0.9519. **The pipeline responds strongly to a *relative*
data/MC E_avail scale**, so the common-scale result is not a blind null.

**Controls.** The seed-fixed repeat reproduces the control to ~1e-13, so the floor is float rounding,
not estimator noise. The 3D control reproduces the frozen 3D product (`xsec_3d_MEFHC_5iter_lgbm.root`)
to 3e-13. The 5D control does **not** reproduce the frozen 5D central (`products/5d/xsec_5d_MEFHC_5iter_lgbm.root`):
median 0.58 %, integral 1.0003. That product was made by an earlier deployment (Jun 6) and this study
does not explain the difference. It does not enter the verdict, which uses only matched runs.

**Verdict (predeclared rule, applied by `compare_eavail_scale.py`): SENSITIVE for all three
common-scale points in both products.** The floor is a deterministic rerun (~1e-13), so the tolerance
fell to its `0.1 × m_ML = 0.045 %` term, and every per-bin median exceeds that.

**Reading, and what is still open.** A common rescale is *not* exactly inert in this pipeline. The
per-bin shifts have three properties: (i) they are the same size as the lgbm estimator-seed band
(3D 0.45 %/bin) and as the unexplained 5D control-vs-frozen difference; (ii) they do **not** grow with
the size of the rescale (k = 1.00, i.e. −14.5 %, is no larger than ±10 %); (iii) the integrals move
≤ 0.03 %. Together these look like the rescale re-drawing the GBDT's histogram binning and the
fixed-edge purity reco binning, which would make this a realization effect rather than a physical
response to the value of 1.17. That mechanism is **not demonstrated**: separating the classifier term
from the purity-binning term would take a further run (scale only the purity-binning input), which is
not in this plan.

**Proposed systematic (proposal only, for Joseph).** Following the predeclared SENSITIVE branch: a
per-bin symmetric band equal to the envelope `max(|m10 − ctrl|, |p10 − ctrl|)` from `compare_*.json`
inputs (3D `hXSec3D` median 0.5 %, p95 ≈ 3 %; 5D `hXSecND_flat` median ≈ 0.6 %, p95 ≈ 2.7 %;
integrated ≤ 0.03 %), with k = 1.00 reported alongside it (same size). **Caveat for adoption:**
because its size matches the estimator-seed band, adding it to a covariance that already carries an
ML/seed block may partly double-count it. That overlap is unmeasured. This study also does **not**
cover a data/MC *relative* E_avail response uncertainty, which the power control shows is large
(percent-level integrals). That is the separate, unrun `RESPONSE_MISMATCH_CLOSURE.md` question.
