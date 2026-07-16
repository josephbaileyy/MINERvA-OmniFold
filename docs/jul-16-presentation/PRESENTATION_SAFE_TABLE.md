# Presentation-safe results table — July 16, 2026 talk

The OPEN_ITEMS deliverable ("by 2026-07-15, produce a presentation-safe table
separating current central/closure results, corrected preliminary uncertainties
that pass every gate, and results still withheld"). One line per fact, with the
artifact or ledger source. Deck slide B7 states the same three tiers in bullet
form; this is the speaker's Q&A reference.

## Tier 1 — Current and quotable (central values, closure, 2D budget)

| Result | Number | Source |
|---|---|---|
| 2D reproduction: total σ OmniFold/published | 1.011 | `values.tex` |
| 2D median per-bin ratio / bins within 10% | 1.006 / 94.1% | `values.tex` |
| 2D per-bin standardized differences using published σ | mean 0.089, rms 0.60; descriptive because the results share data | `values.tex` |
| Indicative χ²/ndf distance vs paper covariance / summed covariance | 3.66 / 1.48; no cross-covariance, not a calibrated GoF | `values.tex` |
| 2D rebuilt budget vs published (median/bin) | 6.87% vs 6.86% | `values.tex` |
| 2D same-ensemble pull diagnostic | ⟨|r|⟩ = 0.794 vs unit-normal 0.798; Gaussianity check only, not coverage | note §Validation |
| Iteration stability 5→10 | 0.026% | `values.tex` |
| C2ST descriptive diagnostic | AUC 0.535 → 0.501; no calibrated p-value | note §Validation |
| Independent Keras-MLP / GBDT total σ | 1.0078 | `values.tex`; note fig `nn_vs_gbdt_full` |
| PET/GBDT central-value total ratio | 0.912 | `values.tex` |
| 5D-vs-2D anchor, low-recoil (2p2h) recovery, DIS-corner excess localization | shape-level statements | deck slides 15–18; note |
| Ascencio common-grid cross-check | indicative χ²/ndf distance 1.68/2; no formal p-value or GoF claim | `nd-unfolding/compare_ascencio_fullcov.py`; ledger 2026-06-10 |

## Tier 2 — Internal candidate uncertainties (do not quote as final)

| Result | Number | Source |
|---|---|---|
| GBDT 5D support-limited candidate block-sum | 13.36% median/bin; final selection-complete lateral replacement pending | `\gbdtFiveBlockMedian`; P3S/P4 |
| GBDT 5D candidate mean-centered covariance | √Tr C = 5.81e-38; not adopted for publication until P4 | `...combined_bkgaware_uthrow{,_cvcentered}.root` |
| Per-universe background effect (#13) | null, <0.3% (188 universes, both legs) | KNOWN_ISSUES #13; `CORRECTED_UQ_PRODUCTION_STATUS.md` |
| ML-band validation (AI1 estimator-seed scan) | est-only √Tr 1.306e-39 = 87.5% of the candidate split-varied band (1.493e-39) | `nd-unfolding/uq_cov_ai1est_5d.root` |
| Recoil-PET historical total | QUARANTINED: additive nuisance/retraining blocks omit cross terms; detector block is support-limited | `PET_UQ_REMEDIATION_STATUS.md`; P5B |

Caveats that ride with Tier 2:
- These values are useful internal diagnostics only; omit them from the main talk.
- Standard/FPS active-lateral event loops and the full-event PET replacement are running.
- Corrected 4D, 5D, FPS and PET covariances do not transfer automatically across estimators.

## Tier 3 — Withheld (do not quote, even if asked)

- **Every (E_avail, W)-plane / covariance-based generator significance** — the
  historical covariance is quarantined; the requote against the corrected 5D
  covariance (M C₅D Mᵀ with fresh 5-axis stat replicas) has not been run. This
  includes the old corner significances (GENIE 8.9σ, NuWro 15.6σ, GiBUU 22.4σ):
  unquotable.
- Old 4D/5D/FPS unified/adopted covariances and their inflation factors
  (pre-corrected-contract: one-sided endpoints, CV centering, jitter
  subtraction).
- Every recoil-PET total and PET-vs-GBDT precision verdict, including the later
  15.10% candidate: the full-event joint-nuisance replacement has not landed.
- Fine-grid Ascencio full-covariance χ² (Stage-2 fine-binning sweep not run).
- FPS/extended-phase-space uncertainties (pilot is central-value +
  prior-envelope only; backup B10 stays PRELIMINARY).
