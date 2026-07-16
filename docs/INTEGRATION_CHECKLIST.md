# Publication integration checklist (Agent D)

Sole integration owner of `docs/analysis-note/` + canonical provenance while
Agents A–C run compute. Numbers live only in `VALIDATION_LEDGER.md`; candidate/
uncommitted values are not quotable. Companion: `docs/ESTIMATOR_REGISTRY.md`.
Last updated 2026-07-16.

## Build environment (task #10)
- `module load texlive/2024` is a **no-op on this login node**. Use the direct path:
  `export PATH=/global/common/software/nersc9/texlive/2024/bin/x86_64-linux:$PATH`
  (+ `export HOME=/global/homes/j/josephrb` for TeX caches under the school account).
- Build: `latexmk -pdf -interaction=nonstopmode -halt-on-error <target>.tex`.
- **Trap:** a SIGTERM'd (timed-out) latexmk leaves a **truncated `.aux`** →
  next build dies with `File ended while scanning use of \@newl@bel`. Fix:
  `latexmk -C <target>.tex` then rebuild. Always run the build in the background
  (it exceeds the 120 s foreground limit).
- Build state after fixes: main_primer/main_paper build clean; main_note rebuilt
  after aux clean. No undefined refs / duplicate labels / missing files.
  Residual cosmetic: 1 overfull \hbox (~23.7pt, main_note lines 280–287) and
  ~dozens of `\textlangle invalid in math mode` from bib titles (technote.bib
  344/361/395/428/441 `$\langle E_\nu\rangle$`) + T1/cmtt font-shape substitutions.

## Manuscript-correctness issues — final status
| # | Issue | Status | What was done / gate |
|---|---|---|---|
| 1 | False "first triple-differential" novelty | **DONE** | Narrowed every claim to "first **unbinned** simultaneous multi-observable unfold"; cite prior binned triple-differential MINERvA `\cite{MINERvA:2022qe}` (arXiv:2203.08022, verified). Edited: sec_execsummary, main_note, sec_summary, main_paper, paper_body (×3), primer_body. |
| 2 | Distinguish estimators/backends | **DONE (registry) / PARTIAL prose** | `ESTIMATOR_REGISTRY.md` maps all 8 estimators + rules. Backends already named in prose. Minor open: add explicit "headline = exact-GBT" note at sec_3d:78 / sec_results:122 (3 backends listed w/o headline flag). |
| 3 | Central paired with wrong estimator's covariance | **DONE** | sec_eavailw clarified: frozen-reweighter *technique* (not PET matrix) on GBDT central. Registry rule #1. No hard mismatch found elsewhere. |
| 4 | Stale appendix values → macros | **GATED (number)** | `\chiCombined`=**1.481** (body/ledger) vs **1.699** printed in app_statmethods (588/593/837/842/862/1225/1237). Different covariance combos (ledger: 1.481 = matcorr_fluxfix+ML; appendix 1.699 = +bootstrap-300; ledger warns that combo double-counts → 1.341). NEEDS RECOMPUTE + reconcile before quoting; do not guess. Also macro-duplicated literals (6.86%, 3.66, 1.011) — convert to macros. |
| 5 | 3D closure overclaim | **DONE** | sec_3d "method is therefore unbiased on the new axis" → "No nonclosure is observed for this tested deformation (single injected +30% Gaussian bump)". |
| 6 | Valencia/generator ratios recompute | **GATED (number)** | Ratios at sec_3d (142/167-176/254/264/337-346), sec_eavailw:64 (1.54/1.58/1.56) must be recomputed from tracked arrays via a labeled num/denom script. Number-dependent → placeholder/gate. |
| 7 | Ascencio fingerprint/citation | **NOTED** | Bib `MINERvA:2022incl` = arXiv:2110.13372 (correct Ascencio low-recoil paper) but `collaboration={MINERvA}`, no author field; prose says "Ascencio et al." Add author or `note` field for fingerprint. Low risk. |
| 8 | "4D model dominated" + 4D error bars | **DONE (gated)** | sec_summary "shifts budget flux→model-dominated (§4d)" removed; replaced with explicit "4D systematic-budget composition not quoted — no corrected 4D covariance adopted". Consistent with sec_3d:398-403 which already withholds the 4D budget. |
| 9 | "no dimensional cost" scalability | **DONE** | sec_3d: added qualifier — removes binning penalty but training/support/sparsity/UQ all become more demanding; "not free of a dimensional cost". |
| 10 | Statistical-efficiency causal language | **DONE (main body)** | sec_systematics recast as an *observed* covariance difference, "not a demonstrated causal efficiency advantage". Appendix app_statmethods:773/791/854 efficiency-vs-D'Agostini wording still causal — follow-up. |
| 11 | "dropped softest mesons" | **DONE** | sec_pet → "lowest-energy stored final-state hadrons" (species unverified). |
| 12 | GiBUU constrained subspace | **NOTED (already ~ok)** | sec_3d:175-178 already separates the 23.5% out-of-subspace residual from the normalization offset. Optional: sharpen "in-subspace residual vs uncaptured covariance fraction". |
| 13 | Same-data χ² / non-cross-fitted C2ST | **DONE** | sec_validation C2ST relabeled a "descriptive binning-free diagnostic ... trained and evaluated on the same unfolded sample without cross-fitting ... not a calibrated hypothesis test; cross-fitted C2ST deferred". app_statmethods:952 same-data χ² already hedged. |
| 14 | Legacy / corrected recoil / full-event PET | **DONE (registry) / mostly ok prose** | Registry keeps `pet-recoil-legacy` / `pet-recoil-bkgsub` / `pet-fullevent-fps-v1` distinct. Note already separates recoil-only (current) from full-event (future). Optional: make legacy-vs-corrected *recoil* explicit in sec_pet (currently only app_codebase:31). |

## Claims GATED on unfinished computation (placeholder only — do NOT quote)
- **4D adopted covariance + error bars** (#8): gated on Agent A committed standard
  lateral block + unified-throw inflation. Registry `omnifold-4d-lgbm` = CANDIDATE.
- **(E_avail,W) generator significances** (#6, #8): reported at central-value level
  only in the note (already gated in prose); numeric ratios need recompute.
- **Full-event PET** any result (#14): gated on KNOWN_ISSUES #19 (no products exist).
- **FPS covariance-dependent** claims: gated (corrected FPS UQ pending).
- **5D lateral**: support-limited until #16 five-band coverage (publication gate).
- **PET 100-replica C_stat**: 20 replicas only; recoil-only cross-check.
- **χ²/ndf 1.699 (appendix)** (#4): reconcile vs ledger 1.481 — needs recompute.

## Verified / quotable (ledger) — safe to keep
- 2D σ_total 3.073e-38, Phase-18.2 paper reproduction (`omnifold-2d-sklearn`).
- 3D covariance √tr 5.724e-39; 4D central 3.0665e-38.
- Corrected 5D GBDT adopted covariance 5.8077e-38 (mean) / 6.2367e-38 (cv).
- Corrected recoil PET C_total 3.8777e-38 (recoil-only cross-check).

## Provenance index (result → estimator → committed input)
See `docs/ESTIMATOR_REGISTRY.md` for the full estimator→product→covariance→commit map.
Figure/table provenance (note → source):
- `fig:xsec` (2D reproduction) → `omnifold-2d-sklearn`, 2d_crossSection_omnifold_MEFHC_5iter.root.
- `fig:3dmodels`, sec_3d generator comparisons → `omnifold-3d-lgbm` / `omnifold-4d-lgbm` centrals + generator spectra.
- `fig:eavailWband` → GBDT central + frozen-reweighter (E_avail,W) cov (central-value-level; significances gated).
- `fig:pcvalid`, `fig:petgbdt`, PET figures → `pet-recoil-bkgsub` (recoil-only cross-check), `of_inputs_pc_fullcloud.npz`.
- `fig:calibration` (NN vs GBDT) → `omnifold_nn_core` cross-check.
- Full figure-by-figure index vs `make_figures.sh` outputs: FOLLOW-UP (needs figure-generator cross-ref).

## Deliverables status
- [x] Estimator registry (`docs/ESTIMATOR_REGISTRY.md`, committed f75cb60)
- [x] Manuscript textual fixes: #1,#3,#5,#8,#9,#10,#11,#13 DONE; #2,#7,#12,#14 noted/registry; #4,#6 GATED (number)
- [x] Build main_note/primer/paper — clean (no undefined refs/dup labels); cosmetic residuals noted
- [x] Provenance index (above) + gated-claim list
- [ ] FOLLOW-UP (number-dependent / other agents): #4 χ² reconcile, #6 ratio recompute, appendix efficiency wording, bib math-mode + overfull-box cosmetics, full figure index
