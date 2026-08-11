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
- Build state: all three build clean (no undefined refs / duplicate labels / missing
  files, converged). Overfull \hbox FIXED 2026-07-16 (app_statmethods
  `\texttt{...CalcCovMx}` given `\allowbreak` break points → **0 overfull boxes**).
  The `\textlangle invalid in math mode` warnings from bib titles with
  `$\langle E_\nu\rangle$` are a PRE-EXISTING, benign biblatex sentence-casing quirk
  (biblatex maps `\langle`→`\textlangle` while case-changing the title, landing in
  math mode); non-fatal, **no visible output effect** (bibliography renders fine).
  Standard fixes tried and did NOT clear it (brace-wrapping the math; hyperref
  `\pdfstringdefDisableCommands`) → confirmed it is biblatex-internal, not
  hyperref/bookmark. ACCEPTED as cosmetic; a proper fix needs a biblatex title
  field-format override (follow-up). Harmless T1/cmtt font substitutions also remain.

## Manuscript-correctness issues — final status
| # | Issue | Status | What was done / gate |
|---|---|---|---|
| 1 | False "first triple-differential" novelty | **DONE** | Narrowed every claim to "first **unbinned** simultaneous multi-observable unfold"; cite prior binned triple-differential MINERvA `\cite{MINERvA:2022qe}` (arXiv:2203.08022, verified). Edited: sec_execsummary, main_note, sec_summary, main_paper, paper_body (×3), primer_body. |
| 2 | Distinguish estimators/backends | **DONE (registry) / PARTIAL prose** | `ESTIMATOR_REGISTRY.md` maps all 8 estimators + rules. Backends already named in prose. Minor open: add explicit "headline = exact-GBT" note at sec_3d:78 / sec_results:122 (3 backends listed w/o headline flag). |
| 3 | Central paired with wrong estimator's covariance | **DONE** | sec_eavailw clarified: frozen-reweighter *technique* (not PET matrix) on GBDT central. Registry rule #1. No hard mismatch found elsewhere. |
| 4 | Stale appendix values → macros | **DONE** | RECOMPUTED on interactive alloc (compare_to_paper_fullcov.py, flux-fix `hCov_combined` [incl. bootstrap] + ML): combined χ²/ndf **1.481**, log-normal **1.468**, subtract-stat **11.560** (over-corrects) — confirms ledger. Appendix's pre-flux-fix **1.699/1.688/23.96** were STALE → replaced with macros `\chiCombined`/`\chiCombinedLog`/`\chiCombinedSubStat` (new in values.tex); "−54%" drop → "−60%". Residual: still-hardcoded 6.86%/3.66/1.011 duplicates + the appendix pull mean/RMS 0.069/0.466 (vs body 0.089/0.598 vs ledger 0.051/0.409) — separate follow-up (below). |
| 5 | 3D closure overclaim | **DONE** | sec_3d "method is therefore unbiased on the new axis" → "No nonclosure is observed for this tested deformation (single injected +30% Gaussian bump)". |
| 6 | Valencia/generator ratios recompute | **GATED (number)** | Ratios at sec_3d (142/167-176/254/264/337-346), sec_eavailw:64 (1.54/1.58/1.56) must be recomputed from tracked arrays via a labeled num/denom script. Number-dependent → placeholder/gate. **2026-08-02 (J27.3), sec_eavailw PARTIALLY CLOSED:** the three ratios provably come from the 2026-06-08 *three*-generator band run (`ND_OMNIFOLD_RUN_LOG.md:988-990`, which reads "All three" and "GiBUU excluded (FinalEvents.dat lacks per-event Enu)"); the note said "All four", attaching three magnitudes to four generators. Prose now attributes them to the three that produced them. Reduction recovered and recorded as a comment in `sec_eavailw.tex`: corner-*integrated* ratio over Eavail≥0.8 × W≥1.8 (3×3=9 cells), `overlay_eavailW_band.py:88-108` — **not** the Eavail≥0.8 1-D block in `eavail_generator_significance.py`, and **not** the 12-cell Eavail≥0.4 χ² sub-block. GiBUU's corner ratio remains UNCOMPUTED: recover by re-running `make_figures.sh:55` (it already passes `--gen GiBUU`) and reading the `hiE-hiW corner ... data/gen=` stdout line. Blocked on Perlmutter `/pscratch` — note the sshproxy cert expired 2026-02-28, which is a *separate* blocker from the 07-22→08-03 outage. |
| 7 | Ascencio fingerprint/citation | **NOTED** | Bib `MINERvA:2022incl` = arXiv:2110.13372 (correct Ascencio low-recoil paper) but `collaboration={MINERvA}`, no author field; prose says "Ascencio et al." Add author or `note` field for fingerprint. Low risk. |
| 8 | "4D model dominated" + 4D error bars | **DONE (gated)** | sec_summary "shifts budget flux→model-dominated (§4d)" removed; replaced with explicit "4D systematic-budget composition not quoted — no corrected 4D covariance adopted". Consistent with sec_3d:398-403 which already withholds the 4D budget. |
| 9 | "no dimensional cost" scalability | **DONE** | sec_3d: added qualifier — removes binning penalty but training/support/sparsity/UQ all become more demanding; "not free of a dimensional cost". |
| 10 | Statistical-efficiency causal language | **DONE (main body)** | sec_systematics recast as an *observed* covariance difference, "not a demonstrated causal efficiency advantage". Appendix app_statmethods:773/791/854 efficiency-vs-D'Agostini wording still causal — follow-up. |
| 11 | "dropped softest mesons" | **DONE** | sec_pet → "lowest-energy stored final-state hadrons" (species unverified). |
| 12 | GiBUU constrained subspace | **NOTED (already ~ok)** | sec_3d:175-178 already separates the 23.5% out-of-subspace residual from the normalization offset. Optional: sharpen "in-subspace residual vs uncaptured covariance fraction". |
| 13 | Same-data χ² / non-cross-fitted C2ST | **DONE** | sec_validation C2ST relabeled a "descriptive binning-free diagnostic ... trained and evaluated on the same unfolded sample without cross-fitting ... not a calibrated hypothesis test; cross-fitted C2ST deferred". app_statmethods:952 same-data χ² already hedged. |
| 14 | Legacy / corrected recoil / full-event PET | **DONE (registry) / mostly ok prose** | Registry keeps `pet-recoil-legacy` / `pet-recoil-bkgsub` / `pet-fullevent-fps-v1` distinct. Note already separates recoil-only (current) from full-event (future). Optional: make legacy-vs-corrected *recoil* explicit in sec_pet (currently only app_codebase:31). |

## Claims GATED on unfinished computation (placeholder only — do NOT quote)

> **Every row re-verified 2026-08-11 by the uncertainty-construction lane. One row was stale and is
> struck below; one row's stated *reason* had decayed while its verdict stood; the binding publication
> gate was **missing from this list entirely** and is now the first row.** Rows are annotated with the
> artifact they gate, because two of them were previously readable as gating a product they do not.
> A gate list that names satisfied gates trains its reader to skip the list — and so does one that
> omits the gate that actually binds.

- **THE BINDING GATE, and it was absent from this list until 2026-08-11: the 2026-07-12
  uncertainty-remediation quarantine** (`VALIDATION_LEDGER.md:65-88`), seven construction causes, of
  which **zero are discharged for the 5D GBDT covariance** — see the next row. It gates the four
  `\gbdtFive*` macros (`values.tex:57-60`, consumed only at `sec_systematics.tex:162-173`) and every
  covariance-dependent claim in the note. Per-cause written discharge criteria, the artifact that
  satisfies each, and the honest per-leg state:
  [`orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`](orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md).
  **No verification pass opens it** (`orchestration/PROMPTS-20260811-four-session-closeout.md` §3, and
  the withdrawal at `a0285c4`); adoption is withdrawn as unactionable, and
  `orchestration/PROCEDURE-gbdtFive-macro-update.md` is correct and deliberately unused.
- **5D GBDT lateral: STILL LIVE — do not strike this on the strength of the 2026-08-07 five-band
  entry.** Support-limited until `KNOWN_ISSUES` #16 five-band coverage (publication gate); #16's own
  status is **OPEN**. **Checked 2026-08-11 because this row was reported to be stale, and it is not.**
  The five-band active lateral discharged at `VALIDATION_LEDGER.md:90-118` is adopted into the **FPS**
  covariance (`uq_fps/corrected/universe_stage2_fps/…_activelat.root`, **266** reported bins). This row
  gates the **5D GBDT** covariance — a different object on a different grid, **10,694 of `GRID_NBINS =
  65856`** (`nd-unfolding/p4_lib.py:22`) — whose **P4-5D lateral has not been built**
  (`docs/OPEN_ITEMS.md:92-101`), and whose lateral endpoint inputs are purity-footed, unreceipted, and
  from a retired launcher (`KNOWN_ISSUES` #20). `ESTIMATOR_REGISTRY.md:29` carries the identical #16
  caveat on `omnifold-5d-lgbm`, which is this product. 266 ≠ 10,694 is the whole check.
- **4D adopted covariance + error bars** (#8): gated on Agent A committed standard
  lateral block + unified-throw inflation. Registry `omnifold-4d-lgbm` = CANDIDATE.
  Also gated on the binding row above, and separately blocked upstream — the 4D unified throw wants a
  3D universe omnifile that is missing (`nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`, "Pending
  decisions / gates" item 3).
- **(E_avail,W) generator significances** (#6, #8): reported at central-value level
  only in the note (already gated in prose); numeric ratios need recompute.
  Two distinct preconditions, both open: **no `(E_avail,W)` covariance has been rebuilt** since either
  fix landed (`KNOWN_ISSUES.md:357`), and the sixth J28 flux site lives in this same script,
  code-fixed 2026-08-06 with **no number produced** (`KNOWN_ISSUES.md:338-349`). The GiBUU corner ratio
  is separately UNCOMPUTED — recover by re-running `make_figures.sh:55` (it already passes
  `--gen GiBUU`) and reading the `hiE-hiW corner … data/gen=` stdout line.
- **Full-event PET** any result (#14): gated on KNOWN_ISSUES #19 — **verdict stands, and the reason is
  sharpened 2026-08-11 by the PET lane because "no products exist" has been read one level too broadly.**
  No full-event PET *product* exists (weights that are canonical, cross section, covariance) and that is
  what gates the claims. The full-event **inputs** are a different matter and they DO exist: the 120
  selection-shifted full-event lateral endpoint ROOTs (`nd-unfolding/p3f_pet_fullevent/final/`, 5 band ×
  2 endpoint × 12 playlist, 1.1 TB) are `g2-fullevent-v1` schema and were promoted
  **`GATE3_PROMOTED_PASS` on 2026-07-20**, all 120 receipts `PASS`
  (`state/p3f-pet-gate3-promotion-56169838.json`). Inputs and products are different objects, and
  conflating them mis-sizes the remaining work by a 120-endpoint C++ event-loop dump.
  See `docs/orchestration/DETERMINATION-20260811-cause5-binding-half.md`.
- **FPS covariance-dependent** claims: gated — **verdict stands, stated reason corrected 2026-08-11.**
  The old reason, *"corrected FPS UQ pending"*, has decayed: the selection-complete five-band FPS
  lateral **exists and passed its full gate chain** (job `56431823`, `VALIDATION_LEDGER.md:90-118`).
  What still gates these claims is the binding row above — the ledger's own scope note says *"The
  2026-07-12 quarantine above is **not** lifted by this entry"* and that the `+10.96%` **must not be
  applied as a uniform scale** (per-bin σ ratio 0.79 → 1.44).
- **PET 100-replica C_stat**: 20 replicas only; recoil-only cross-check. **Verdict stands as a gate on
  the PRODUCT; the row's implied claim-defect does not exist — corrected 2026-08-11 by the PET lane,
  which owns it.** This row has been read as *"the note quotes C_stat as if it had 100 replicas."*
  Checked, both halves:
  - The note quotes **no PET `C_stat` magnitude at all** — `7.439e-39` appears in **zero** `.tex` files
    under `docs/analysis-note/`, and `values.tex` defines no PET statistical macro.
  - The note's only statement about it is already self-disclosing (`sec_pet.tex:110-112`): *"The
    `C_stat` estimate is based on **20** coherent replicas, so its finite-ensemble precision is more
    limited than the 100-replica **target**."* 100 is named as a target, 20 is stated as the fact, and
    the next sentence scopes the whole paragraph to the recoil-only estimator.

  So there is no sentence to repair. **The disposition is therefore "change the claim", and the claim
  that needed changing was this row** — not the note. *Producing* the 100 is the wrong spend, and
  deliberately so rather than for cost alone: each replica is a full PET retrain (`sec_pet.tex:99-101`,
  one GPU job per replica, `sbatch_pet_bootstrap_replica.sh` requests 6 h), so 80 more replicas is an
  80-job GPU campaign — spent to sharpen a number that (i) is **not quoted anywhere**, (ii) is a
  component of the quarantined recoil `C_total` (`values.tex:70` `\petTotalTrace` is marked
  *"QUARANTINED"* at its own point of definition), and (iii) belongs to a **superseded estimator**: per
  the 2026-08-01 full-event landing every pre-08-01 PET number is a *different estimator*, not a stale
  value. The 100-replica ensemble is a **full-event deliverable**, which the note already requires
  independently — cause 5's replacement *"receives a fresh statistical and ML ensemble"*
  (`sec_pet.tex:133-134`) — so topping up the recoil ensemble would buy a sharper number for an
  estimator the note does not quote and then throw it away. **Not scheduled, and this is the record of
  why** (never silently dropped).
- ~~**χ²/ndf 1.699 (appendix)** (#4): reconcile vs ledger 1.481 — needs recompute.~~
  **STALE — struck 2026-08-11. This row was the genuinely dead one.** The recompute landed **2026-07-16**
  and this same file records it twice: issue **#4 is marked DONE** in the table above, and the
  Deliverables list says *"#4 χ² reconcile (recomputed + macro-sourced) … DONE 2026-07-16"*. Verified in
  the note rather than inferred from the checklist: `values.tex:35-37` defines
  `\chiCombined` `1.481` / `\chiCombinedLog` `1.468` / `\chiCombinedSubStat` `11.56`, consumed at
  `app_statmethods.tex:674,675,679,694,930,935,959,1337,1351` and `sec_results.tex:59`; and
  `grep -rn '1\.699' docs/analysis-note/*.tex` returns **one** hit, the `values.tex:39` comment saying
  the pre-flux-fix `1.699/1.688/23.96` are superseded. So there is no `1.699` left in any build to
  reconcile. Struck rather than deleted, per this repo's convention of keeping the record readable.

## Verified / quotable (ledger) — safe to keep
- 2D σ_total 3.073e-38, Phase-18.2 paper reproduction (`omnifold-2d-sklearn`).
- 3D covariance √tr 5.724e-39; 4D central 3.0665e-38.
- ~~Corrected 5D GBDT adopted covariance 5.8077e-38 (mean) / 6.2367e-38 (cv).~~
  **NOT QUOTABLE — this entry was filed under "safe to keep" in error.** Both scales are
  quarantined, on two independent grounds:
  1. The **2026-07-12 uncertainty-remediation quarantine** (`VALIDATION_LEDGER.md:20-30`) makes
     the 4D/5D/FPS unified-throw adoptions "SUPERSEDED AND UNQUOTABLE". The ledger lines that
     these two numbers are copied from already say so at the point of use
     (`VALIDATION_LEDGER.md:294,297`, each annotated *"(quarantined)"*), so this checklist
     contradicted its own cited source.
  2. **J28** (`docs/orchestration/AUDIT-FINDINGS-20260731.md:478-530`, tier A) — PPFX flux
     universes divided by the CV flux integral at five ND/5D sites plus a fail-open. It is "the
     only finding that reaches an already-adopted product", and its explicit recommendation is
     to "quarantine the adopted 5D covariance scales now (`5.8077e-38`, `6.2367e-38`)". Code
     fixed in `081ae4a`; **the numbers have not been re-rolled.**
  **No replacement magnitude is written here on purpose.** The J28 re-roll measurement
  (`VALIDATION_LEDGER.md:345-360`) is a measurement and not an adoption, and the ledger states
  the quarantine "STAYS IN FORCE ... Lift it by adopting, in a commit that replaces the numbers".
  A candidate scale quoted here before that adoption would recreate exactly the defect this line
  is being corrected for. What survives unaffected: the **central** 5D results, which this
  quarantine never invalidated.
  See also `docs/analysis-note/values.tex` `\gbdtFiveAdoptTrace` / `\gbdtFiveCVTrace`, which quote
  these scales into the note and inherit the quarantine; they are owned by the GBDT close-out lane
  and are deliberately **not** edited here.
- ~~Corrected recoil PET C_total 3.8777e-38 (recoil-only cross-check).~~
  **NOT QUOTABLE — and this one contradicts the note's own macro file, which is why it is worse
  than the entry above.** `docs/analysis-note/values.tex:70` carries this same value as
  `\newcommand{\petTotalTrace}{3.878e-38}` with the inline comment
  *"historical recoil-PET candidate; QUARANTINED"*. So the note already marks it dead, while this
  checklist listed it under a heading that is an explicit safety claim. **No inference about
  quarantine scope is needed here** — unlike `\petRatio`, whose coverage I could not source, this
  value is marked quarantined at its own point of definition.
  It also falls inside the 2026-07-12 class by description: *"PET statistical/total budgets and
  precision comparisons"* (`VALIDATION_LEDGER.md:20-30`).
  **No replacement is written here on purpose.** Same reason as the entry above: a candidate
  magnitude quoted under "safe to keep" before an adoption recreates the defect being corrected.
  What survives: nothing from this line — it is a *recoil-only* cross-check, and per the
  2026-08-01 full-event landing, pre-08-01 PET numbers are a different estimator besides.
  Indexed at `docs/orchestration/INDEX-retracted-and-superseded-values.md`; found while sourcing
  the `:61` row rather than reported, so the neighbouring line is the reason it surfaced at all.

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
- [x] #4 χ² reconcile (recomputed + macro-sourced) + cosmetics (bib math-mode, overfull box) — DONE 2026-07-16
- [ ] FOLLOW-UP (number-dependent / other agents): #6 Valencia/generator-ratio recompute;
      pull mean/RMS inconsistency (appendix 0.069/0.466 vs body \pullMean/\pullRMS 0.089/0.598
      vs ledger 0.051/0.409 — determine the correct combined-cov pull + macro-source);
      appendix efficiency wording (app_statmethods:773/791/854); remaining hardcoded
      6.86%/3.66/1.011 duplicates → macros; full figure-by-figure provenance index;
      minor #2/#7/#12/#14 prose sharpening
