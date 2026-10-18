# Phase 2 site inventory: VL175 → Q (S5 total + C_PL) in the 2D deliverables

Read-only inventory. Worktree `wt-phase2` at `origin/main` `ae198cc1`. Nothing in it was edited. Line numbers are at
`ae198cc1`. Every Q value below is read from the committed phase-1 receipts in
`docs/orchestration/state/2d-closeout/stageF/rebuild/outputs/` (abbreviated `rb/`). VL175 values come from
`state/2d-closeout/c04-repair/products/budget.json` (`repaired`), its `chi2/` logs, or the current text.

**How sites were found.**
1. The `\input` closure of each driver.
2. Macro-usage maps for every 2D-covariance macro.
3. A number-and-keyword grep over all 55 note sources and `make_figures.sh`. It used several precisions:
   6.09/6.090/6.0898, 3.65/3.655, 4.23, 0.994, 1.014, 5.80, 0.406, 0.048, 24.4, 2.91x, 2.92, 0.674, 6.87, 6.058, 99.6,
   bootstrap, seed scan, ML, VL15x–VL17x, c04, hCov_combined, block sum, std/mean, 187.
4. Full reads of every file region with a hit.
5. As a template, the VL172 → VL175 commit `5b24ca2e`. It touched 22 files. Every deliverable file it touched is
   covered here.

**Status codes.**
- **NUM**: replace from the named receipt.
- **NR**: not recomputed, with the reason (SPEC §3a).
- **J**: claim or disclosure wording. Leave it for J3/J4. The DRAFT-disclosures item (`stageF/DRAFT-disclosures.md` D0–D12) is named where one exists.
- **FACT**: the construction fact the sentence states is no longer true of Q. The words are J3/J4, but phase 2 cannot leave the sentence as is.
- **DER**: derivable from receipt fields but not itself a receipt field (flag it if printed).
- **FIG / TOOL**: a figure or build-tool site.
- **OK**: checked, unaffected.

---

## 0. Build map: which PDF is built from which sources

| PDF | driver | inputs (from the `\input` closure) | 2D-covariance content |
|---|---|---|---|
| `main_note.pdf` (118 pp) | `main_note.tex` | `preamble`, `values`, `values_inference`, `sec_execsummary` (→ `result_status_rows`), `sec_intro`, `sec_experiment` (→ `selection_features`), `sec_method`, `sec_systematics`, `sec_validation`, `sec_results`, `sec_3d` (→ `scalar_kinematics`), `sec_eavailw`, `sec_5d`, `sec_joint`, `sec_fps`, `sec_summary`, `app_guide`, `app_statmethods`, `app_statmethods_nd`, `app_negweight`, `app_response_mismatch`, `app_landscape`, `app_pet_pointer`, `app_provenance`, `app_release`, `app_codebase`, `app_history` | most sites |
| `main_paper.pdf` (11 pp, RevTeX PRD) | `main_paper.tex` | **`values`, `values_inference`, `paper_body` only** (no `preamble`; own macros at l.24–29) | `paper_body` §`sec:repro2d`/`sec:uq2d`, Fig. 1, the conclusions; plus `main_paper.tex` Data availability. `paper_body.tex` is a rewrite, not an extract, so note edits do not reach it |
| `main_primer.pdf` (12 pp) | `main_primer.tex` | `preamble`, `values`, `primer_body` only | the primer's 2D paragraphs |
| `pet_note.pdf` (26 pp) | `pet_note.tex` | `preamble`, `values`, `sec_pet` (→ `sec_pet_campaigns`), `app_cstat`, `app_provenance_pet`, `app_history_pet` | one wording site (`app_cstat.tex:47`); title-based `\notesec{}` references to note sections |

`values.tex` is read by all four builds. Defining a macro does not print it; the usage maps are in the tables below.
**Figures**: `\graphicspath{figures/}`, PDF only. The paper's Fig. 1 `figures/paper_fig1_validation.pdf` is NOT made by
`make_figures.sh`. It comes from `publication/release/figs/make_figs.py` via the receipt-side wrappers
(`receipts/2d-c04-adopt-20261012/make_fig1_vl175.py`, now `rebuild/scripts/make_fig1_q.py`).

**Build commands.** From `docs/analysis-note/`: `bash build_all.sh`.
- It builds all four with `latexmk -g -pdf -interaction=nonstopmode -halt-on-error`.
- It then runs `check_dead_containment.py --self-test` and then without arguments, then `check_sec4_receipts.py --self-test` and then without arguments, then the page counts.
- The header says NERSC login node with `module load texlive/2024`.
- A single target: `latexmk -pdf main_paper.tex` (the driver's header).
- After the build: sync, build and commit the standalone `MINERvA-OmniFold-Analysis-Note` repository. Its local
  checkout is at `/Users/josephbailey/local-research/MINERvA-OmniFold-Analysis-Note`, head `95b3474` (2026-10-13), and
  pushing it needs J6.

**Local build (measured 2026-10-18, in a scratch copy, not in the tree).** I copied `docs/analysis-note/` without
`archive/` to `scratchpad/buildcopy/repo/docs/analysis-note/` and symlinked `docs/orchestration/state` so that the
canonical-layout receipts check runs. Results:
- `latexmk -g` gave rc 0 for all four targets (note 118 pp, PET note 26, paper 11, primer 12), with no
  "There were undefined" lines.
- `check_dead_containment.py --self-test` and the plain run: rc 0, PASS.
- `check_sec4_receipts.py --self-test` and the plain run: rc 0, PASS 14/14.
- The local TeX Live has `latexmk`, `biber`, `pdftotext`, `gs` and `pdfinfo`. Paper plus primer took about 30 s.

So **all four PDFs build locally**. The biber PAR-cache failure did not occur this time. `make_figures.sh` does not
run locally: it hardcodes `REPO=/pscratch/...` and needs root_6_28.

---

## 1. The replacement key (Q values, receipts)

`B` = `rb/outA/budget_Q.json.gz` (uncompressed sha256 `e7e3f24c…`; field path given). Relative σ is in % of `E_U`.

| ID | quantity | VL175 | Q | receipt |
|---|---|---|---|---|
| K1 | total per-cell median | 6.0898 (6.09 / 6.090) | **6.4479** → 6.45 / 6.448 | `B.Q.median_pct`; `rb/fig1/uqmedian.tex` = `\uqMedian{6.45}` |
| K2 | total p84 / max | 9.024 / 23.106 | 9.184 / 23.64 | `B.Q.p84_pct`, `.max_pct` |
| K3 | width-weighted total σ (integral) | 4.2303 (4.23) | **4.755** | `B.Q.integral_sigma_pct` |
| K4 | total √Tr | 2.917e-39 | 2.866e-39 | `B.Q.sqrt_trace` |
| K5 | systematic (universe incl. norm) median / √Tr | 6.043 / 2.910e-39 | 5.969 / 2.735e-39 | `B.universe.*` |
| K6 | statistical median / √Tr / integral | 0.674 / 1.931e-40 / 0.058 | 0.684 / 1.984e-40 / 0.061 | `B.stat.*` |
| K7 | training seed (ML → c08) median / √Tr / integral | 0.166 / 5.061e-41 / 0.0055 | 0.057 / 1.989e-41 / 0.0025 | `B.c08.*` |
| K8 | run period C_PL median / √Tr / integral (new) | — | 2.137 / 8.344e-40 / 1.968 | `B.C_PL.*` |
| K9 | universe + stat ("before ML") median | 6.084 | 6.040 (S5 total 6.041) | `B.universe_plus_stat.median_pct`, `B.S5_total.median_pct` |
| K10 | total median against `E_C` | 6.058 | 6.410 | `B.Q_vs_EC.median_pct` |
| K11 | `\fluxBand` (Flux band median) | 3.6549 (3.65 / 3.655) | **3.747** → 3.75 | `B.bands.Flux.median_pct`; `B.flux.band_Flux_median_pct` |
| K12 | top bands MINOS / MINERvA / MinosEff / MaRES / MvRES / MaCCQE | 2.281 / 1.285 / 1.472 / 0.548 / 0.377 / 0.357 | 2.390 / 1.376 / 1.578 / 0.600 / 0.374 / 0.368 | `B.bands.<band>.median_pct` |
| K13 | grouped medians: Muon reco / Models / Flux / Hadronic / Stat / Norm (+ new) | 3.421 / 1.479 / 3.655 / 0.758 / 0.674 / 1.400 | 3.455 / 1.581 / 3.747 / 0.799 / 0.684 / 1.400; Training seed 0.057; Run period 2.137 | `B.groups.median_pct` |
| K14 | χ²/ndf combined (`\chiCombined`) | 0.994 | **0.964** (197.59/205) | `rb/chi2/chi2_Q_std.txt` |
| K15 | log-normal (`\chiCombinedLog`) | 1.014 | **0.987** (202.33/205) | `rb/chi2/chi2_Q_lognormal.txt`. Definition: δ = ln E_U − ln p, C_ln = (Total+Q)/(p_i p_j) (REPORT §5) |
| K16 | stat-subtracted (`\chiCombinedSubStat`) | 5.80 (5.803) | **6.012** | `rb/chi2/chi2_Q_substat.txt` |
| K17 | combined pull mean / RMS | 0.048 / 0.406 | **0.042 / 0.398** | `chi2_Q_std.txt` "pull mean / rms". The "RMS" is the SD about the mean; the true RMS is 0.400 (REPORT §4) |
| K18 | ours-only direct inverse | 24.4 (universe + boot) | universe+stat **23.57** (cond 8.17e11); Q 23.23 (cond 8.63e11); universe alone meaningless (rank 137, negative χ²) | `rb/chi2/ours_only_*.txt` |
| K19 | ranks / conditions (eigenvalues of (C+Cᵀ)/2 > t·λmax) | C_syst 140/205, cond 8.7e8; C_syst+C_boot 204, cond 1.0e12; "rank 201" (C_ours) | universe 137 (1e-12) / 123 (1e-10), cond 4.93e11 / 9.93e9; universe+stat and Q 205 / 197, cond 8.17e11 / 8.63e11 at 1e-12 | `B.ranks` |
| K20 | our stat against the paper StatOnly (√Tr ratio, inverse, trace) | 0.416 = 1/2.40; "5.8 in trace"; elsewhere "≈2.55" | 0.428 → 1/2.34; trace 5.47 (DER); median σ ratio 0.435 | `B.paper_ratios` |
| K21 | √Tr(Q)/√Tr(paper Total) | (not printed) | 1.071 | `B.paper_ratios` |
| K22 | paper √Tr StatOnly / Total (205) | 4.639e-40 / 2.676e-39 | unchanged | `B.paper_ratios` |
| K23 | stat-block centring | "0.30 of σ_stat (0.18%)", the seed-1 central against the seed-42 central | replica mean offset: median 4.43 σ/√300 = 0.26 σ (a **different quantity**) | `B.s5_copied.stat_centring_offset`; REPORT §3 |
| K24 | MAT agreement | 5.5e-17 (the unweighted MnvH1D check); "≤ 1e-12 (VL175)" | 3.4e-16 (`mat_universe_block_le_1e-12`) | `B.s5_copied.mat_agreement` |
| K25 | ensemble counts | 44 bands / 187 universes; ML n=10; boot N=300 | 43 bands + norm (44 entries; Rvp1pi dropped, KI-92); 300 S1 replicas; 5 seed triplets; c08 rank 4 | `B.s5_copied.ensemble`, `.derived_counts_not_copied`. Universe count after the drop: OPEN (Q1) |
| K26 | variance shares of Q (per-cell median / integral) | — | universe 0.871 / 0.828; C_PL 0.099 / 0.171; stat 0.0094 / 0.00016; c08 6e-5 / 3e-7 | `B.block_shares` |
| K27 | `\rhoFluxMuon` | 0.900 | 0.900 (does not depend on Q) | `B.flux.rhoFluxMuon` |
| K28 | Muon_Energy_MINOS integral σ | 0.37 (after the KI-96 repair; 0.11 before) | 0.306 (the "before" value has no S5 counterpart) | `B.bands.Muon_Energy_MINOS.integral_sigma_pct` |
| K29 | stat ensemble error on σ | — | 4.1% | `B.s5_copied.ensemble.stat_rel_se_of_sigma` |

---

## 2. Inventory by file

### 2.1 `values.tex` (all builds)

| line | current text (short) | quantity | VL175 | Q / receipt | status |
|---|---|---|---|---|---|
| 126 | `\chiCombined{0.994}` + comment (c04-repair repaired_std) | combined χ²/ndf | 0.994 | 0.964, K14 | NUM; rewrite the comment to name `rb/chi2/chi2_Q_std.txt` and keep the history chain |
| 127 | `\chiCombinedLog{1.014}` + comment | log-normal | 1.014 | 0.987, K15 | NUM; add the definition to the comment |
| 128 | `\chiCombinedSubStat{5.80}` + comment | stat-subtracted | 5.80 | 6.01 (6.012), K16 | NUM |
| 129–130 | comment: "All three recomputed 2026-07-16 (… flux-fix hCov_combined [already incl. bootstrap] + ML)" | provenance comment | stale | → hCov_Q in `uq_adopted_covariance.root` | NUM (comment) |
| 133–135 | `\uqMedian{6.09}` + comment (6.0898, VL175, budget.json) | total median | 6.09 | 6.45, K1 | NUM. **Coupled**: `check_sec4_receipts.py:105` regex, `make_figs.py` regex, Fig. 1 inset |
| 136–137 | `\uqPaper{6.85}` | published median | — | unchanged | OK |
| 138 | `\fluxBand{3.65}` (3.6549, VL175, KI 95; "was 4.993 unweighted") | Flux band | 3.65 | 3.75, K11 | NUM; the comment's "unweighted 4.993" is VL-era history |
| 139 | `\rhoFluxMuon{0.900}` | flux–muon ρ | 0.900 | unchanged, K27 | OK |
| 87–89 | `\pullMean 0.074`, `\pullRMS 0.564` | paper-σ-only pulls | — | unaffected (SPEC §3a) | OK |
| 97–119 | `\covTwoD*` family (VL169 fixed-truth coverage) | coverage of the superseded VL162 band | — | **NR**: not a property of Q; S5's stat block is a different, untested ensemble (KI-85) | J (D2) |
| 120–121 | `\pullFrac 68.71`, `\pullMeanAbs`, `\pullGauss` | same-ensemble 200-toy diagnostic | — | NR (not a property of Q) | J |
| 122–125 | `\chiPaper`, `\chiPaperExact`, `\chiPaperExactSeeded` | paper-covariance χ² | — | unaffected | OK |

### 2.2 `sec_systematics.tex` (note build)

| line | current text (short) | quantity | VL175 | Q / receipt | status |
|---|---|---|---|---|---|
| 1 | section title "constructing the covariance blocks" | — | — | — | OK |
| 4–6 | "sums three blocks from systematic universes, statistical bootstraps, and ML training-seed variation" | composition | 3 blocks | 4 blocks: universe + stat + training seed (c08) + run period (C_PL) | FACT; J (D0, D5) |
| 7–10 | "computed with the LightGBM estimator …, at different training seeds; the pairing of the statistical block's seed … not otherwise measured" | seed pairing | stat seed 1 | S1 is at **seed 42** (production DESIGN l.93, `--seed 42 --bootstrap-streams three`). The pairing is matched; replica-mean offset 0.26 σ (K23) | FACT; J (D10 KI-88) |
| 18–20 | "44 error bands and 187 universes …" | ensemble | 44 / 187 | July sweep 44 bands / 187 universes as input; Rvp1pi dropped → 43 + norm in the rollup (K25) | FACT/NUM; universe count is Q1 |
| 20–24 | "re-unfolded … seed 42 …; the adopted sweep's truth input differs from this reference" | May-sweep truth mismatch | true of VL175 | S5 uses the **July** sweep (DESIGN l.273; S4(ii) "July identity at seed 42, 7/7") | FACT; J (D10 KI-93) |
| 30–34 | "Top 2D bands: Flux `\fluxBand` (… 4.99 without them, KI 95), Muon_Energy_MINOS 2.28, MinosEfficiency 1.47, Muon_Energy_MINERvA 1.29" | band medians | 3.65 / 2.28 / 1.47 / 1.29 | 3.75 / 2.39 / 1.58 / 1.38 (K11, K12). "4.99 unweighted": NR (no S5 unweighted flux; VL-era history) | NUM; NR |
| 43–46 | Fig. `fig:uqbands` caption: groups "flux, interaction models, normalization, hadronic response, muon reconstruction, and the statistical band" | block list in caption | 6 groups | Q figure adds "Training seed" and "Run period" (labels provisional, J4) | NUM/J |
| 50–56 | "Flux band 4.99 without … (`\fluxBand` with them) … ∼1% when … CV Φ, and a standalone combined budget of `\uqMedian`" | flux paragraph | — | macros update. The 4.99 and ∼1% are VL-era diagnostics (NR) | NUM; NR |
| 56 | "Target-nucleon normalization … rank-1 band of 1.4%" | norm | 1.4 | 1.400 (`B.bands.__Normalization_flat`) | OK |
| 57–60 | "Muon_Energy_MINOS … divided by its own flux (KI 96); raises that band's integral σ from 0.11% to 0.37%" | MINOS integral | 0.11 → 0.37 | S5 0.306 (K28). The "before" value is NR in S5 | NUM/NR; J |
| 60–62 | "participation-ratio effective rank ≈1; one coherent normalization mode carries **99.6%**" | flux leading-mode share | 99.6 | **NR**: no committed producer (SPEC §3a); remove or label as historical | NR |
| 62–70 | `\rhoFluxMuon`; "ρ=0.87–0.90"; cross block not added | flux×muon | — | unaffected (K27) | OK |
| 72–89 | §`sec:uq-boot` "300 per-event Poisson(1) … two independent sub-RNGs … Pinning the GBDT seed per replica …" | stat construction | VL170: seed 1, data+MC streams | S1: seed 42, three streams (data, signal MC, background MC; KI-94). The stat ensemble is a new 300-replica set | FACT; J (D2, D8, D10 KI-94) |
| 79–81 | "bootstrap block … smaller than the published … (**≈2.55×** in √trace)" | √Tr ratio | 2.55 (stale even for VL175, which gives 2.40) | 1/0.428 = **2.34×** (K20) | NUM |
| 82–85 | "data-only stream … C_data/StatOnly = **0.356**" | split-bootstrap data stream | 0.356 | **NR**: a VL170-era split bootstrap; no S5 counterpart | NR |
| 85–89 | "The fixed-truth coverage test … found that the earlier statistical band undercovered …; The rebuilt band has not been independently re-tested" | coverage | — | the quoted stat block is now S1, not the rebuilt VL170 band; untested (KI-85) | J (D2, J5) |
| 93–97 | Fig. `fig:bootstrap` (`uq_spread_2d`, `uq_corr_2d`); caption "300-replica Poisson bootstrap per-bin relative spread …" | stat figures | VL170 | `rb/stat/uq_spread_2d.pdf`, `uq_corr_2d.pdf` (from `block_stat.root`). The colorbar "std/mean" now means σ/`E_U` (SPEC §2): caption item | FIG; J |
| 101–115 | §`sec:uq-ml`: "ML block … 10 independent estimator seeds …; median **0.166%** …; split variant **1.24×** …; ten-seed mean differs from exact-split by **0.99%**, about **five times** this block's σ …; reseeded exact-split 0.18% (max 1.6%)" | ML block | 10 seeds, 0.166 | the training-seed block is now c08: the 5-triplet seed main effect, median 0.057 (K7), rank 4. 0.166 / 1.24× / "five times": **NR** (the seed scan is not recomputed; C08 replaces it). Learner 0.98% (D3); 0.98/0.057 ≈ 17× (DER) | FACT; NR; J (D3, D11) |
| 120–127 | Fig. `fig:seedscan` (`seedscan_spread_2d`, `seedscan_band_pt`), "ML training-seed variation over 10 estimator seeds" | seed-scan figures | VL-era | **NR**: no Q replacement produced; phase 2 removes it or relabels it historical | FIG; NR |
| 131–139 | "The adopted May systematic sweep uses a different simulated truth input …; The July sweep does not have this mismatch" | construction finding | true of VL175 | S5 universe = July sweep | FACT; J (D10 KI-93) |
| 141–147 | "Rvn1pi and Rvp1pi … counting it twice … 0.088% band" | double count | true of VL175 | S5 drops Rvp1pi (KI-92; DESIGN l.273). Rvn1pi median 0.088 (`B.bands.Rvn1pi`) | FACT; J (D10 KI-92) |
| 149–153 | "Background-template statistics still require propagation …" | bkg stat | unpropagated | S1 has its own background stream (KI-94; D8, D10) | FACT; J |
| 153–155 | "Selection-complete 2D lateral variations and the identity of the PPFX universe indices … require verification" | laterals, flux index | open | S5: the 5 lateral bands come from S3 selection-complete outputs (DESIGN l.273); flux-index identity is established (KI-91, D10) | FACT; J |
| 155–156 | "These findings leave the printed budget unchanged …" | — | — | stale under Q | J |
| 160–163 | "The nominal covariance is the block sum C = C_syst + C_stat + C_ML" | equation | 3 terms | + C_PL (and c08 for C_ML) | FACT/J |
| 179–182 | "reframes the block sum as an approximation …" | generic | — | — | OK (check after J4) |
| 186–238 | §`sec:uq-higherdim` (5D lateral, 5D ML, 187-universe bkg 0.28%/0.18%) | 5D products | — | unaffected (5D/J28) | OK |

### 2.3 `sec_results.tex` (note)

| line | current text | quantity | VL175 | Q / receipt | status |
|---|---|---|---|---|---|
| 5–7 | "error bars give the total uncertainty …, combining systematic universes, statistical bootstraps, and ML training-seed variation" | composition; also an error-bar claim | 3 blocks | + run period. **Also**: Figs. `fig:xsec`/`fig:ptslices` draw `hXSec2D.GetBinError` (`plot_2d_threeway_fig13.py:102`, `plot_2d_cross_section.py:92`), not any covariance (Q2) | FACT; J |
| 56–58 | "combined covariance, including our uncertainty (`\chiCombined`)" | χ² | macro | K14 | NUM (via macro) |
| 61–66 | "combined … = `\chiCombined` double-counts …; we quote per-bin pulls, the **regularization scan**, and the truncated result" | regularization scan | exact-split | NR (no producer; exact-split; SPEC §3a) | NR; J |
| 85 | tab:compare row "paper + ours `\chiCombined`" | χ² | macro | K14 | NUM (macro) |
| 135–142 | "standalone combined budget … `\uqMedian` against `\uqPaper` … flux-dominated … smaller than the published total; part … flux band (`\fluxBand` …, against 4.01 …)" | budget prose | 6.09 < 6.85 | 6.45 < 6.85 still smaller; Flux group 3.75 is still the largest group (K13) | NUM (macros); J (D10 flux sentence) |
| 143–145 | "an earlier version omitted them and quoted **6.87%** (KI 95)" | history | 6.87 | add VL175 (6.09) as the predecessor? | J |
| 145–147 | "systematic block dominates; statistical and ML blocks together contribute under a tenth of the combined √Tr" | √Tr shares | — | stat+c08 = 0.070 of √Tr(Q) (DER from K4, K6, K7); C_PL is 0.29 of √Tr and 0.171 of the integral variance (K26) | NUM/DER; J |
| 147–150 | "Every block is computed with the LightGBM estimator …; divide by … seed-42 central value" | estimator | — | true; now also matched seed | OK/J |
| 150–152 | "exact-split cross-check … combined median of **6.058%**" | median against E_C | 6.058 | 6.410 (K10) | NUM |
| 153–156 | comment (VL175 6.0898 / 6.0577 …) | provenance comment | — | → `B.Q.median_pct`, `B.Q_vs_EC` | NUM (comment) |
| 158–178 | **tab:uq**: rows ML 10 / 5.06e-41 / 0.166; Statistical 300 / 1.93e-40 / **0.674**; Systematic 187+1 / 2.91e-39 / 6.043; **Combined (block sum)** — / **2.92e-39** / **6.090**; Paper 2.68e-39 / `\uqPaper`. Caption "flux band carries MAT's constraint weights (VL175) … (**6.090%**) is below the published total" | budget table | as listed | universe 2.735e-39 / 5.969; stat 300 / 1.984e-40 / 0.684; training seed (c08) 5 triplets / 1.989e-41 / 0.057; **run period (new row)** 8.344e-40 / 2.137; Q 2.866e-39 / 6.448; paper 2.676e-39 unchanged (K4–K8, K22) | NUM; row labels J4 |
| 179–210 | §`sec:results-tension` (`\chiPaper`, 0.32, 544, …) | paper-σ only | — | unaffected | OK |
| 237–238 | model χ² "33.0, 29.8, 26.5" | paper TotalCov only (`compare_to_models.py:118–130`) | — | unaffected | OK |

### 2.4 `app_statmethods.tex` (note)

| line | current text | quantity | VL175 | Q / receipt | status |
|---|---|---|---|---|---|
| 5 | intro: "training-seed, bootstrap, and universe estimators" | composition | — | + run-period block | J |
| 27–28 | "Stage-2 bootstrap (N=300>205) is full-rank" | stat rank | — | S1 stat rank 205 (production REPORT l.108) | OK |
| 59–62 | "summarizes the **three** variance sources" | composition | 3 | 4 (+ C_PL) | FACT/J |
| 75–78 | tab:variance-sources ML row: "seeds (N,N+1,N+2), N∈{1..10}; n=10; median 0.166%" | ML block | 10 seeds, 0.166 | c08: 5 seed triplets, the seed main effect, median 0.057 (K7, K25) | NUM/FACT |
| 79–82 | Bootstrap row: "data (k) and MC (k+10^7) sub-RNGs; … GBDT seed pinned; N=300 (Stage-1: N=50); median 0.674%" | stat block | 0.674 | S1: seed 42, three streams; N=300; 0.684 (K6) | NUM/FACT |
| 83–86 | Universes row: "187 universes, 44 bands, + norm; median 6.043%" | universe | 6.043 | 5.969; 43 bands + norm (K5, K25) | NUM; Q1 |
| 87–90 | MAT reference row: "max rel. diff 5.5e-17" | MAT check | 5.5e-17 | S5 MAT universe check 3.4e-16 (K24); a different check | NUM/J |
| 91–94 | Block-sum row: "sum of the three independent blocks … median 6.090%" | total | 6.090 | four blocks; 6.448 (K1) | NUM/FACT |
| 97–98 | caption + `variance-sources` code pointers (see app_provenance) | — | — | — | see 2.10 |
| 102–119 | §`sec:seedscan`: "n=10 … total-σ spread **0.0055%**, per-bin **0.166%**, √Tr **5.061e-41**; ≈**2.4%** of paper's median; n=4→10 converged" | seed scan | as listed | **NR** (seed scan); the c08 replacements: integral 0.0025, median 0.057, √Tr 1.989e-41 (K7); 0.057/6.85 = 0.83% (DER) | NR/NUM; J |
| 121–162 | §`sec:bootstrap`: two sub-RNGs; "N=300 varies only the bootstrap seed"; 50→300: 0.062→**0.058**, 0.644→**0.674**, p84 1.543→1.664; "≈4.1× the training-seed value (0.166%)"; 1A 1.46% | stat block | VL170 | Q: integral 0.061, median 0.684, p84 1.712 (K6). The 50→300 convergence: NR (S5 has a nested 150/300 ratio 1.001, D2, not a `budget_Q` field); 0.684/0.057 = 12× (DER); 1A: NR | NUM/NR; FACT (three streams, seed 42) |
| 183–193 | §`sec:universes` "187 universes across 44 bands …" | ensemble | 44/187 | 43 + norm (K25); laterals from S3 | NUM/FACT |
| 216–232 | the `\mathbf{C}^{syst}` equations; "Independence … one known correlated exception" | — | — | unchanged algebra | OK |
| 255–278 | **tab:band-medians**: MINOS 2.281, MINERvA 1.285, MinosEff 1.472, Flux 3.655, MaRES 0.548, MvRES 0.377, MaCCQE 0.357; "Systematic total (44 bands + norm) **6.043%**, √Tr **2.910e-39**"; caption "full matcorr sweep … (VL175 …)" | band table | as listed | 2.390 / 1.376 / 1.578 / 3.747 / 0.600 / 0.374 / 0.368; 5.969, 2.735e-39; "43 bands + norm"; caption → S5 universe block (July sweep, S3 laterals, Rvp1pi dropped) (K5, K11, K12) | NUM; FACT (caption) |
| 279 | comment: rollup path `…_full_matcorr_fluxfix/uq_universe_summary.txt` | provenance | — | → `B.bands` | NUM (comment) |
| 280–293 | grouped: "VL175 medians are: Muon reco 3.421, Models 1.479, Flux 3.655, Hadronic 0.758, Statistical 0.674, Normalization 1.400 …; muon-reconstruction median rises slightly although MINOS band's falls …" | grouped medians | as listed | 3.455 / 1.581 / 3.747 / 0.799 / 0.684 / 1.400, + Training seed 0.057, Run period 2.137 (K13). The "rises although MINOS falls" sentence explains VL172→VL175: drop or rewrite | NUM; J |
| 288–290 | comment (group_medians.py, 7927c51e) | provenance | — | → `B.groups` | NUM (comment) |
| 358–360 | the paper's log-normal χ² variant (the paper's Table I) | describes the paper | — | — | OK; the definition goes at 535/571 |
| 375–385 | MAT byte-for-byte: "44 bands / 187 universes … 5.5e-17 … Flux … agrees with MAT's weighted CalcCovMx to ≤1e-12 (VL175)" | MAT check | — | S5: `mat_universe_block_le_1e-12` = 3.4e-16 (K24) | NUM/J |
| 392 | "systematic-only rank 120<140" | paper V rank against ours | 140 | ours: universe 137 (1e-12) (K19); the paper's 120 is unchanged | NUM |
| 408–415 | §`sec:combine`: "bootstrap … distinct data and MC sub-RNGs; … seeds 1–10; … three Monte Carlos …; different LightGBM seeds (1 for the bootstrap, 42 for the universes) … not measured" | composition/seed | — | four blocks; stat at seed 42; c08 = 5 triplets; C_PL from run-period differences | FACT; J (D10 KI-88) |
| 416–421 | eq:blocksum C^tot = C^ML + C^stat + C^syst | equation | 3 terms | + C_PL | FACT |
| 425–426 | "C^ML is over an order below both other blocks … numerically negligible" | — | — | c08 is two orders below stat in √Tr (DER) | NUM/J |
| 428–446 | **tab:combine**: ML 5.061e-41 / 0.166; Statistical 1.931e-40 / 0.674; Systematic (fluxfix sweep + norm, VL175) 2.910e-39 / 6.043; **Combined 2.917e-39 / 6.090**; Paper 2.676e-39 | budget table | as listed | c08 1.989e-41 / 0.057; stat 1.984e-40 / 0.684; universe 2.735e-39 / 5.969; **C_PL row** 8.344e-40 / 2.137; Q 2.866e-39 / 6.448; optionally S5 total 2.742e-39 / 6.041 | NUM |
| 447–449 | "The per-bin median **6.090%** cannot be reconstructed …" | total | 6.090 | 6.448 | NUM |
| 450–454 | "exact-split … **6.058%**. All three blocks are LightGBM ensembles, at different training seeds" | E_C median; seeds | 6.058 | 6.410 (K10); seeds matched (stat 42; c08 5 triplets incl. 42) | NUM; FACT |
| 455–456 | "repaired rollup also reports **6.084%** for universe + bootstrap before ML" | before ML | 6.084 | universe+stat 6.040 (K9) | NUM |
| 457–460 | comment (recompute_2d_budget.py VL172) | provenance | — | → budget_Q | NUM (comment) |
| 462–464 | "Tables … quote the flux-fixed product" | — | — | → Q / S5 | J |
| 509–511 | "Options add OmniFold covariances … or subtract the paper's stat block to avoid counting it alongside the bootstrap" | generic | — | — | OK |
| 515–524 | truncation scan 0.41→…→2.65 (paper V only) | paper-only | — | unaffected | OK |
| 532 | worked example "Width-weighted total σ … 4.61% | **4.23%**" | integral | 4.23 | **4.755** (K3) | NUM |
| 533 | "Per-bin median … `\uqPaper` | **6.090%**" | total | 6.090 | 6.448 | NUM |
| 534–535 | `\chiCombined`, `\chiCombinedLog` in the table | χ² | macros | K14, K15 | NUM (macro); **the log-normal definition must go next to the number** (REPORT §5) |
| 539–541 | "lowers … from `\chiPaper` to `\chiCombined`, about **63%** (exact-split 3.661 to **1.472**)" | reduction | 63 | **64%** (1 − 197.59/544.12 = 0.637; DER from chi2_Q_std.txt). Exact-split 1.472: NR (no E_C combined χ² against Q) | DER; NR |
| 561–563 | "the quoted `\chiCombined` is such a realization; the exact-split cross-check's **1.47** alone …" | — | 1.47 | NR (VL172 exact-split) | NR/J |
| 565–569 | "only 2D coverage test … statistical band … undercovers …; the statistical block's training seed differs from the central value's" | coverage; seed | — | S1 is at seed 42 (matched) | FACT; J (D2, D10) |
| 571–572 | "log-normal variant … gives essentially identical `\chiCombinedLog`" | log-normal | 1.014 against 0.994 | 0.987 against 0.964. **State the definition** (δ = ln E_U − ln p; C_ln = (Total+Q)/(p_i p_j)); it is definition-dependent (1.197 / 0.958 / 0.963 / 1.015 under the alternatives, REPORT §5) | NUM; J |
| 574–575 | "larger by **≃2.5** in √trace, and thus by **2.55²≃6.5** in trace" | stat ratio | 2.5 / 6.5 (stale even for VL175: 2.40/5.8) | 2.34 / 5.47 (K20) | NUM/DER |
| 577–583 | "our finite-N blocks fill C^syst's null space (rank **140→201**) and yield χ²/ndf=**252**" | rank; pinv χ² | 140→201; 252 | ranks 137→205 at 1e-12 (K19); 252: NR (earlier bootstrap pinv; not re-derived) | NUM; NR |
| 585–607 | edge-bin table (exact-split, paper cov) | paper-only | — | unaffected | OK |
| 616–627 | §`sec:pull` "combined covariance (paper TotalCov + flux-fixed matcorr universe + bootstrap-300 + ML; VL175) gives mean **0.048** … RMS **0.406** (before the flux-constraint repair 0.041 and 0.386; exact-split 0.051 and 0.405)" | combined pulls | 0.048 / 0.406 | 0.042 / 0.398 (K17); the composition text → paper + Q; the history clause gains VL175 | NUM; J |
| 629–631 | "No reported bin has \|pull\|>3" | combined pulls | — | not in the receipt as a max; `chi2_Q_std` prints only the mean/rms. NR unless re-read from the pull array (Q3) | NR |
| 633–634 | paper-only pulls `\pullMean`/`\pullRMS` | paper-only | — | unaffected | OK |
| 664–671 | shape χ² 3.596 (exact-split, paper cov) | paper-only | — | unaffected | OK |
| 677–683 | "C^ours = C^syst + C^boot + C^ML … rank(C^syst)=**140**/205, cond=**8.7e8**" | rank/cond | 140, 8.7e8 | universe 137 / cond 4.93e11 at 1e-12 (123 / 9.93e9 at 1e-10) (K19). The convention behind 8.7e8 is unclear (Q4) | NUM |
| 685–689 | "PPFX … **99.6%** of its variance in one normalization mode"; "The **44** bands cannot span 205 bins" | flux mode; band count | 99.6; 44 | 99.6: **NR** (no producer); 43 + norm | NR; NUM |
| 690–692 | "paper's systematic-only … rank 120, below our **140**" | rank | 140 | 137 (K19) | NUM |
| 696–700 | "300-replica bootstrap similarly gives rank(C^syst+C^boot)=**204** (>1e-12), cond=**1.0e12**" + comment (VL172) | rank/cond | 204, 1.0e12 | universe+stat 205, cond 8.17e11 (K19) | NUM |
| 703 | "Even at rank **201** a defensible …" | rank | 201 | 205 | NUM |
| 704–708 | "smaller … by a factor **2.40** in √trace (√Tr C^boot = **1.931e-40** vs √Tr StatOnly = 4.639e-40), about **5.8** in trace … not … uniform **5.8**-fold" | stat ratio | 2.40 / 1.931e-40 / 5.8 | 2.34 / 1.984e-40 / 5.47 (K6, K20) | NUM/DER |
| 711–715 | "naive pseudo-inverse gave χ²/ndf=**252** … earlier bootstrap …; not re-derived for the rebuilt one, whose direct inverse gives **24.4**" | ours-only | 24.4 | universe+stat **23.57**; Q 23.23 (K18). 252: NR | NUM; NR |
| 717–719 | "our bootstrap already draws independent Poisson(1) multipliers on both data and MC per replica" | stat streams | 2 streams | S1: 3 streams (data, signal, background) | FACT |
| 728–744 | split bootstrap: closure **1.07**, **77/23**, **0.95**, **0.356**, "(C^boot/StatOnly=**0.416**=1/2.40)" | split bootstrap | as listed | 0.416 → **0.428** (K20); the others are **NR** (VL170-era split bootstrap) | NUM/NR |
| 745–751 | "our stat block is correlated (mean \|ρ\|=**0.108**, overlap **0.46**) …; scaling … left χ²/ndf=**76.7**" | stat structure | as listed | NR (not in `budget_Q`) | NR |
| 753–765 | interpretation of (ii); fixed-truth test of the earlier band | coverage | — | — | J (D2) |
| 767–771 | "Ours-only … truncated-spectral (retain λ>1e-10 λmax)" | convention | — | at 1e-10: universe+stat and Q rank 197 (K19) | OK/NUM |
| 773–798 | **regularization scan** table (exact-split; ranks {19,49,82}, χ² {0.13,1.12,3.08}, ridge {0.35,1.38,4.30}, shrinkage 178→204, 1.3e11, 3.29) | regularization scan | exact-split | **NR**: no committed producer (SPEC §3a); keep labelled as a historical exact-split diagnostic, or remove | NR |
| 800–812 | §bootstrap/paper-stat double-count: `\chiCombined → \chiCombinedSubStat`; "our √Tr C^boot=**1.931e-40** is **2.40×** smaller than … 4.639e-40" | sub-stat; ratio | 1.931e-40 / 2.40 | 1.984e-40 / 2.34 (K6, K20); macros K14/K16 | NUM |
| 814–819 | "The 2D headline therefore retains the block sum, with the cross term diagnostic" | composition | — | the block sum now includes C_PL | J |
| 830–837 | "What is reported": `\chiCombined`; "Ours-only truncated-spectral χ² uses C^ours (rank **201**)" | rank | 201 | 205 (1e-12) / 197 (1e-10) (K19) | NUM |
| 935–959 | estimator table (paper-cov χ² 2.65–2.70; "±0.04 ML-seed jitter") | paper-only | — | unaffected | OK |
| 983–988 | closures: "threshold comfortably above the **0.166%** ML floor" | ML floor | 0.166 | the seed-scan floor is NR; c08 0.057 is a different estimator. Keep it as the 10-seed scan measurement (historical) or reword | NR/J |
| 1059–1063 | §`sec:assemble`: "χ²/ndf = `\chiCombined` and pull mean/RMS **0.048/0.406** …; the **0.166%** ML floor …" | pulls; ML | 0.048/0.406; 0.166 | 0.042/0.398 (K17); 0.166 NR (see above) | NUM; NR |
| 1072–1078 | audit table: "Eq. chi2 with C^paper + C^syst + C^stat + C^ML"; "C^syst 187 universes …"; "C^stat Poisson bootstrap 300"; "C^ML lgbm training-seed variation, n=10" | block list | 3 blocks | + C^PL row; c08 (5 triplets); stat S1 | FACT/NUM |
| 1080–1083 | "Pull RMS = **0.406**"; "Combined median rel. = **6.090%**" | — | 0.406; 6.090 | 0.398; 6.448 | NUM |
| 1084–1087 | "Fixed-truth C_2 = `\covTwoDCTwo`"; "Same-ensemble 68.71%" | coverage rows (SPEC "the audit-table C2 row") | — | NR (not a property of Q) | J (D2) |
| 1097–1102 | standing assumption 2: "requires no cross-correlations between ML, statistical, and systematic. The bootstrap pins the GBDT seed …; the training-seed variation pins the bootstrap" | independence | 3 blocks | four blocks; c08 includes the 1/20 X02 share; X02/X03 reported, not added (D11) | FACT; J |
| 1103–1107 | "fixed-truth test … first-built C^stat …; rebuilt band has not been independently re-tested" | coverage | — | the quoted block is S1 (untested) | J (D2, J5) |

### 2.5 `paper_body.tex` (paper build only)

| line | current text | quantity | VL175 | Q / receipt | status |
|---|---|---|---|---|---|
| 58–60, 68 | intro: ratio, `\binsTen`; "untested coverage limit the construction" | — | — | — | OK / J |
| 185–186 | "the two-dimensional one is the central value of its systematic-universe ensemble, so its covariance is built with the same estimator" | estimator | — | still true; now the stat block is also seed 42 | OK/J |
| 221–226 | `\pullRMS`, `\chiPaper`, `\chiPaperExact*` | paper-only | — | unaffected | OK |
| 229–230 | "learner … per-bin median 0.98%, and no block of the covariance includes this learner dependence" | learner | 0.98 | unchanged (D3) | OK |
| 239 | `\includegraphics{paper_fig1_validation}` | Fig. 1 | `49766e26…` (VL175) | `rb/fig1/fig1_validation.pdf` `82665808…`; inset 6.45% against 6.85% | FIG |
| 240–249 | Fig. 1 caption: "this analysis: statistical, systematic-universe, normalization and training-seed covariance, Sec. uq2d; it omits the learner dependence …" | block list in the caption | 4 items | add run-period (C_PL); "training-seed" is now c08 (CHECKLIST R3) | J (D0, D5) |
| 256–257 | "standalone covariance combines systematic-universe, statistical, and training-seed blocks, all built with the central value's LightGBM estimator" | composition | 3 | + run-period block | FACT; J (D0, D5) |
| 258–259 | `\uqMedian` against `\uqPaper` | total | 6.09 | 6.45 | NUM (macro) |
| 259–262 | "flux block applies … constraint weights …; an earlier version … quoted **6.87%**" | history | 6.87 | add VL175 6.09 as the predecessor? | J |
| 262–264 | "published flux block (4.01% median) is larger than ours (`\fluxBand`) …" | flux | 3.65 | 3.75 (K11); D10 flux sentence | NUM (macro); J |
| 264–268 | "**The blocks use different training seeds**: systematic that of the central value, statistical another, training-seed block ten. The central value differs from the statistical block's own central value by a per-bin median of **0.30** of that block's σ (**0.18%**)" | seeds; pairing | 0.30, 0.18% | FALSE under Q: S1 at seed 42; c08 = 5 triplets. Replacement fact: replica mean 0.26 σ from `E_U` (K23, D2, D10 KI-88); 0.18%: NR | FACT; J |
| 268–269 | "Coverage of the total remains untested" | — | — | still true | J (D1) |
| 271–275 | `\covTwoDNtoy`, `\covTwoDCTwoPctOne`, 95.4 | VL169 coverage | — | NR (SPEC §3a) | J (D2). **Coupled**: `check_sec4_receipts.py` (3 rows) |
| 275–278 | "main cause … removed. **The rebuilt band, now the quoted one**, has a median statistical uncertainty of **0.674%**" | stat median; identity | 0.674 | FALSE under Q: the quoted stat block is S1, 0.684 (K6). **Coupled**: `check_sec4_receipts.py:113–114` regex "median statistical uncertainty of \SI{…}" bound to the VL170 receipt; `test_check_sec4_receipts.py:35` fixture `0.674` | FACT; NUM; TOOL |
| 279–285 | rescoring 97.7 / 78.1 "against it … has not been independently re-tested" | post-hoc rescoring of VL170 | — | **NR** (SPEC §3a: superseded band). **Coupled**: `check_sec4_receipts.py` row "rescoring against the rebuilt band" | J (D2) |
| 285–291 | "construction defects, among them a **truth-input mismatch** between the adopted systematic sweep and its reference and **unpropagated background-template statistics** …; the printed budget includes the flux-constraint repair but not these" | construction findings | true of VL175 | under Q: July sweep (no mismatch); background stream propagated (KI-94). Sentence obsolete | FACT; J (D10) |
| 292–306 | source comments (VL169/VL170/VL172, 6.87% chain, KI 88 "Transfer UNRESOLVED") | provenance comments | — | → Q receipts; KI-88 pairing met (D10) | NUM (comments) |
| 338 | 5D "data-bootstrap statistical uncertainty" | 5D | — | unaffected | OK |
| 482–486 | joint-test nuisance model (5D) | 5D | — | unaffected | OK |
| 765–768 | conclusions: "the **rebuilt two-dimensional statistical band** awaits an independent coverage test" | claim | — | the quoted stat block is S1 (untested; KI-85) | J (D2, J3) |

**Sec. IV receipt binding.** In the paper, `check_sec4_receipts.py` binds these rows:
- `\uqMedian`;
- the three coverage values at 271–275;
- "two-sigma nominal" at 274;
- the stat median at 278;
- the rescoring at 280–281.

See 2.11.

### 2.6 `main_paper.tex` (paper driver)

| line | current text | status |
|---|---|---|
| 129–135 | Data availability: "Fig. `fig:validation` and its numbers were instead regenerated with the release's plotting code, extended to draw this analysis's band, from the committed LightGBM values and covariance" | still true with Q, if the figure is replaced by the phase-1 output; check the wording points to Q (J) |
| 136–155 | comments (RC7 etc.) | OK |

### 2.7 `primer_body.tex` (primer build only)

| line | current text | quantity | Q | status |
|---|---|---|---|---|
| 103–105 | "its error budget was built with the same tree learner. **The rebuilt statistical band** awaits an independent coverage test" | claim | the quoted stat block is S1 | J (D2) |
| 205–207 | "our uncertainties … close in size to the published ones (`\uqMedian` versus `\uqPaper` typical). Ours are a little smaller" | total | 6.45 < 6.85: still smaller | NUM (macro); J |
| 207–211 | "partly because our flux uncertainty comes out below the published one …; An earlier version left that constraint out and quoted **6.87 percent**" | history | add VL175? | J |
| 211–212 | "its error bars are close in size to the published ones" | — | — | OK/J |
| 217–226 | coverage test of the statistical bars `\covTwoDCTwoPct`; "the main cause was found and removed, and **the rebuilt bars, which are the ones quoted**, have not been re-tested" | identity of the quoted stat block | FALSE under Q (S1 is quoted) | FACT; J (D2) |
| — | no sentence about the run-period block | — | — | J (D5): primer omission |

### 2.8 `sec_execsummary.tex`, `result_status_rows.tex`, `sec_summary.tex`, `main_note.tex` (note)

| file:line | current text | Q / status |
|---|---|---|
| sec_execsummary.tex:26 | "separately reconstructed median per-bin uncertainty (`\uqMedian`) comparable to `\uqPaper`; its flux band … which an earlier version omitted (**6.87 %**) …; The central value and that uncertainty use the same LightGBM estimator" | NUM (macro → 6.45); the history literal 6.87 (add VL175?) J; composition and run-period not mentioned: J (D5) |
| sec_execsummary.tex:64 | "standard covariance sums single-source systematic matrices …" (5D methodological) | OK |
| sec_execsummary.tex:94 | "The earlier 2D statistical band undercovers …; **the rebuilt, currently quoted band** has not been independently re-tested" | FACT (S1 is quoted); J (D2) |
| result_status_rows.tex:12 | rsB "LightGBM systematic, statistical and seed ensembles, **at different seeds**"; rsC "Earlier statistical band failed …; rebuilt band lacks independent re-test"; rsD "**Seed pairing of the statistical block unmeasured**" | FACT: stat at seed 42 (pairing matched, 0.26 σ offset); + run-period block; J (D2, D10). Note-only (`sec_execsummary.tex:77`); the paper has no status table |
| sec_summary.tex:8–16 | "reproduces … and its uncertainty scale …; the first-built statistical band failed …; **the rebuilt band has not been re-tested**" | J (D2) |
| main_note.tex:49–52 (abstract) | "that uncertainty is computed with a **different tree-learning implementation** from the central value, and whether it describes the central value has not been measured" | FACT (stale since 2026-10-11; under Q the estimator and seed are matched); J (D10 KI-88, J3) |

### 2.9 `sec_method.tex`, `sec_validation.tex`, `sec_intro.tex` (note)

| file:line | current text | Q / status |
|---|---|---|
| sec_method.tex:80–82 | "its uncertainty ensembles — the systematic universe sweep, the Poisson bootstrap and the training-seed scan — all use LightGBM" | the ensembles are now universe, S1 stat, c08 (S4B seed triplets), plus C_PL (built from run-period unfolds). FACT/J |
| sec_method.tex:87–90 | "systematic block shares its estimator and seed; the adopted universes were unfolded on a **different truth input**" | FACT (July sweep in S5); J (D10 KI-93) |
| sec_method.tex:90–98 | "The statistical bootstrap uses **seed 1** and the ML band seeds 1–10 …; seed-42 vs seed-1 median **0.18%** (max 1.79), or **0.30** (max 1.28) of the stat σ; pairing … unmeasured" | FACT; replacement fact K23 (0.26 σ, replica mean); J (D10 KI-88) |
| sec_method.tex:103–105 | "Seed 42 was chosen because a matched seed-42 statistical band was the cheaper …; **that band has not been built**" | FACT: it is now built (S1, 300 replicas, seed 42). J |
| sec_method.tex:128–129 | exact-split "has no matched covariance: no exact-split bootstrap, universe sweep or seed scan exists" | OK |
| sec_method.tex:175–176 | "explicit training-seed variation band for residual ML stochasticity" | OK (c08) / J |
| sec_validation.tex:213–222 | §`sec:coverage`: "whether the **production** 2D statistical band (§`sec:bootstrap`) covers …"; "the learner of the quoted central value at a different seed" | J: the band tested is VL162, and the production band is now S1 (D2) |
| sec_validation.tex:226–258 | `\covTwoD*` results | NR (SPEC §3a) / J |
| sec_validation.tex:260–269 | "That term was removed …; **the rebuilt band is the quoted one** …" | FACT; J (D2) |
| sec_validation.tex:271–291 | rescoring 0.977 / 0.781 / pull RMS 0.84; "1.6×"; KI-85 | NR (superseded band); J (D2, J5) |
| sec_validation.tex:293–300 | Scope: "It tests the LightGBM statistical estimator at the band's training seed (**seed 1**), not at the quoted central value's seed 42" | still true of the test; the contrast with "the quoted" needs J wording |
| sec_validation.tex:319–351 | same-ensemble pulls `\pullFrac` etc. | NR; OK as a historical diagnostic |
| sec_validation.tex:142–146, 203–204 | "1.014", "23.1%" | false positives (4D q3 closure mean weight; injected size) — OK |
| sec_intro.tex:47–49, 69–72 | "the bootstrap statistical block …"; "training-seed variation band"; "complete 2D uncertainty budget" | J (generic; the run-period block is not named) |

### 2.10 `app_provenance.tex`, `app_codebase.tex`, `app_release.tex`, `app_history.tex` (note)

| file:line | current text | Q / status |
|---|---|---|
| app_provenance.tex:62–63, 146–156 | `variance-sources` code pointers: `seedscan/analyze_seedscan.py`; `uq/seedscan_lgbm_ml/uq_covariance_ml.root`; `uq/bootstrap_MEFHC_300/uq_covariance_boot300.root` (the **VL162** path, stale even for VL175); `uq/analyze_universes.py`; `compare_to_paper_fullcov.py --omnifold-cov` | NUM/pointer: → `state/2d-closeout/stageC/production/s5_rollup.py` (S5), `playlist-term/` (C_PL), `stageF/rebuild/scripts/build_q_products.py` → `uq_adopted_covariance.root:hCov_Q` (CFS `2d-closeout-stageF-rebuild-20261018/`). Consider a new provenance tag for Q (DECISION-20261017) |
| app_provenance.tex:100–111 | `coverage-fixed-truth`: "band scored is VL162 …, since superseded by VL170 (rollup VL172)" | J: add "the quoted stat block is now S1 (Q)" |
| app_codebase.tex:33–35 | "Scripts … call training-seed variation `seedscan`" | J/OK: c08 is not `seedscan`; amend if the seed scan is removed |
| app_codebase.tex:25–27 | "LightGBM central value and uncertainty ensembles" | OK |
| app_release.tex:15–17 | "regenerates the article's first three figures from packaged arrays" | pre-existing: RC7 arrays lack `cov_ours`, so Fig. 1's own band is not in RC7 (true for VL175 too). J/OK |
| app_release.tex:30, 34 | "do not reproduce this analysis's unfolded 2D uncertainty construction … Nor … the 2D uncertainty and coverage figures" | OK |
| app_history.tex:23–64 | **errata table** (`app:history-errata`): rows 58–64 carry the VL175 replacements (6.090, 6.043, 2.910e-39, 2.917e-39, 6.084, 3.655, 2.281, 0.994, 1.014, 5.80, 0.406, 6.058, 3.421, 1.479, 0.048, 63%, 4.23) as the "Replacement (when struck)" | **add the VL175 → Q rows** (SPEC §3a), striking: 6.090 (6.09); 6.043; 2.910e-39; 2.917e-39; 6.084; 6.058; 3.655 (3.65); 2.281; 1.285; 1.472; 0.548/0.377/0.357; 3.421; 1.479; 0.758; 0.674; 1.931e-40; 0.166; 5.061e-41; 0.994; 1.014; 5.80; 0.048; 0.406; 63%; 4.23; 2.40/0.416; 140; 204; 1.0e12; 201; 24.4; 0.30/0.18%. Replacements from K1–K23. **Hazard**: `check_dead_containment.py` derives struck literals from `\dead{}` and fails any outward build that prints one as a whole token. The paper and primer print none of these literals (they use macros), but recheck after editing |
| app_history.tex:48–52, 55–57 | older rows whose "Replacement (when struck)" is 0.674 / 1.931e-40 / 2.40, 0.416, 204, 1.0e12 | OK (they are "when struck" values); the new rows supersede them |
| app_history.tex:92–98 | "From §`sec:bootstrap`": the seed-pinning history | OK (history) |
| app_history.tex:150–157 | "From §`sec:pull`": "the live pair is the flux-fixed one recorded in VALIDATION_LEDGER" | J: "live pair" is now Q's 0.042/0.398 |
| app_history.tex:174–187 | provenance note: "[Superseded 2026-10-12: the quoted budget is 6.090% (VL175), below the published total …]" | add "[Superseded 2026-10-17/18: Q, 6.448%]" |
| app_history.tex:189–215 | the history of the flux-fix and bootstrap rebuild | OK (history) |
| app_history.tex:340–346, 373 | 3D historical budget | OK |

### 2.11 Build tooling coupled to these numbers

| file:line | what | needed change |
|---|---|---|
| `check_sec4_receipts.py:44–47` | `stat_median()` reads `ki84-adopt-20261006/recompute_2d_budget.json` `VL170.boot.median_pct` | rebind to `B.stat.median_pct` (0.684), or change the paper phrase it matches |
| `check_sec4_receipts.py:50–52` | `total_median()` reads `c04-repair/products/budget.json` `repaired.block_sum.median_pct` | rebind to `budget_Q` `Q.median_pct`. **`receipt()` (l.34–35) does `json.loads(read_text())`, and `budget_Q.json` is committed gzipped**: add gzip support or commit an uncompressed receipt |
| `check_sec4_receipts.py:105` | label "total median uncertainty (VL175)" | relabel |
| `check_sec4_receipts.py:106–110` | coverage rows bound to `coverage-2d-20261005/interim_score.json` | unchanged if the coverage sentences stay (J); they fail closed if the phrases are removed |
| `check_sec4_receipts.py:113–117` | regexes "median statistical uncertainty of \SI{…}" and "removes the tail undercoverage: …" bound to VL170 receipts | must follow the phase-2 wording of `paper_body.tex:277–281`, or the build fails (a missing printed value is a failure) |
| `test_check_sec4_receipts.py:35` | perturbation fixture `\SI{0.674}{\percent}` → 0.664 | update to the new printed value (0.684), or drop it if the phrase goes |
| `check_dead_containment.py` | struck literals derived from `\dead{}` | no edit; re-run (see the errata hazard) |
| `publication/release/figs/make_figs.py:10–12` | docstring "(the VL170/VL172 2D budget) … read from values.tex (macro uqMedian)" | stale comment; the regex at l.212 reads `\uqMedian`. Editing the file changes its pinned digest `9c4dbf24…` (SPEC §1, RUN-fig1): leave it, or re-pin |
| `publication/release/figs/_data/fig_arrays.npz.manifest.json` | producer digest note | **done in phase 1** (`01f70c37`) |

### 2.12 `make_figures.sh` and figures

| line / file | current | Q replacement | status |
|---|---|---|---|
| make_figures.sh:44–53 | comments: VL170 adoption; VL175 Fig. 6/7 drawn by `c04-repair/scripts/run_repair.sh` | rewrite for Q (SPEC §6) | TOOL |
| make_figures.sh:54 | `plot_uncertainty_fig6_7_style.py --universe-root "$UFLX/…fluxfix.root" --bootstrap-root …bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root --paper-root … --include-ml always --out-prefix "$UFLX/MEFHC_fig6_7_uncertainty"`. This is the **VL172 recipe**: it does not even pass `--xsec-root` (E_U) or a VL175 universe | SPEC §6: `--xsec-root <E_U> --universe-root uq_adopted_covariance.root --bootstrap-root block_stat.root --ml-root block_c08.root --include-ml always --ml-label "Training seed" --extra-block block_playlist.root:hCov2D_reported:"Run period" --paper-root <anc> --out-prefix … --projections-json …` (inputs on CFS `2d-closeout-stageF-rebuild-20261018/`) | TOOL |
| make_figures.sh:56–57 | `plot_bootstrap_figs.py --cov bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root` | `--cov block_stat.root --outdir …` (SPEC §6) | TOOL |
| make_figures.sh:58 | `seedscan/analyze_seedscan.py` → `seedscan_spread_2d` | remove, or keep as historical with the note's decision on `fig:seedscan` | TOOL/NR |
| make_figures.sh:142–149 | sync loop: copies any `$REPO/{2d,3d,nd}-unfolding/**/<basename>.pdf` **newer** than the figure | **hazard**: the Q outputs live outside `$REPO` (`/pscratch/…/tmp-2d-rebuild-20261018/`, CFS), so the loop never syncs them. If lines 54/57 are left unchanged, a rebuild regenerates the VL170-era PDFs under `2d-unfolding/uq/` and overwrites the committed Q figures. Phase 2 must change 54/57 and either point their outputs inside `$REPO` or install the Q figures by an explicit copy | TOOL |
| make_figures.sh:35–42 | fig13, projections, slices, pull_full (no `--omnifold-cov`), model_comp, tension | unaffected by Q (error bars are `hXSec2D` bin errors or paper σ; see Q2) | OK |
| `figures/paper_fig1_validation.pdf` (`49766e26…`, VL175) | paper Fig. 1 | ← `rb/fig1/fig1_validation.pdf` `82665808…` (inset 6.45 against 6.85) | FIG |
| `figures/MEFHC_fig6_7_uncertainty_pt.pdf` `65db5b0b…`, `_pz.pdf` `4d659851…` (VL175) | note Fig. `fig:uqbands` | ← `rb/fig67/MEFHC_fig6_7_uncertainty_{pt,pz}.pdf`. Legend "Training seed", "Run period" provisional (J4) | FIG |
| `figures/uq_spread_2d.pdf` `fa175255…`, `uq_corr_2d.pdf` `d6cf0adb…` (VL170) | note Fig. `fig:bootstrap` | ← `rb/stat/uq_spread_2d.pdf`, `uq_corr_2d.pdf`. Colorbar "std/mean" = σ/`E_U`: caption | FIG |
| `figures/seedscan_spread_2d.pdf` `ee72097b…`, `seedscan_band_pt.pdf` `47521d29…` | note Fig. `fig:seedscan` | NR: no Q version (C08 replaces the seed scan); remove or relabel as historical | FIG/NR |
| `figures/paper_validation_residual.pdf` | crop of `MEFHC_5iter_pull_full` | not included by any driver; paper-σ only | OK |
| regularization scan | a table, not a figure (`app_statmethods.tex:773–798`) | NR | — |

### 2.13 PET note

| file:line | text | status |
|---|---|---|
| app_cstat.tex:47 | "the 2D bootstrap's data/MC streams (`\notesec{Poisson bootstrap}`) because background enters" | FACT: S1 has three streams with background its own (KI-94); J |
| app_cstat.tex:35, app_history_pet.tex:166 | `\notesec{Multinomial → independent Poisson bootstrap limit}`, `\notesec{Poisson bootstrap}`, reference by section **title** (`preamble.tex:10`) | **hazard**: renaming `sec:bootstrap`'s title ("Poisson bootstrap") or the multinomial subsection breaks these silently (plain text, so no LaTeX warning) |

---

## 3. Checked and unaffected

These are paper-σ-only by construction (SPEC §3a), or the hits were not 2D covariance:
- **Paper-σ-only:** `\chiPaper`, `\chiPaperExact`, `\chiPaperExactSeeded`, `\pullMean`, `\pullRMS`, `\pullRMSr`; the tension anatomy (`sec_results.tex:179–229`, `app_statmethods.tex:842–975`); the model χ² 33.0/29.8/26.5 (`compare_to_models.py` uses paper TotalCov); the shape χ² 3.596; the edge-bin table; the truncation scan 0.41→2.65; `\rhoFluxMuon`; `\uqPaper`; the paper's 4.01 flux block, 4.61 integral, rank 120/204, cond 1.5e12.
- **Central-value figures:** `MEFHC_5iter_fig13`, `_xsec_proj_*`, `_paper_*_slices`, `_pull_full`, `model_comp_*`, `tension_*`.
- **Not 2D covariance (5D/3D/PET/negweight):** `sec_5d`, `sec_3d`, `sec_eavailw`, `app_negweight` (187-universe negweight study), `app_statmethods_nd`, `sec_pet*`. Also the 1.014 / 23.1 hits in `sec_validation.tex` (4D q3 closure).
- **`\gbdt*`:** these macros are 5D-candidate values.

---

## 4. Counts

- **Files with at least one site:** 21, of which 17 note sources (including `values.tex`, `make_figures.sh`, the sec4 checker and its test) and `publication/release/figs/make_figs.py` (comment only). The other three deliverable sources:
  - `paper_body.tex` and `main_paper.tex` (paper);
  - `primer_body.tex` (primer);
  - `app_cstat.tex` (PET note).
- **Sites, about 190 rows above**, by status:
  - NUM (direct receipt replacement): about 95 values;
  - NR (not recomputed, with a reason): about 30;
  - FACT (construction fact changed, wording J): about 30;
  - pure J (claim/disclosure): about 25;
  - FIG: 4 figure files plus 1 NR pair;
  - TOOL: 9.
- **Macros to change:** 5. They are `\uqMedian`, `\fluxBand`, `\chiCombined`, `\chiCombinedLog` and `\chiCombinedSubStat`. None of the coverage macros changes.
- **Tables to rebuild:** tab:uq, tab:combine, tab:band-medians, tab:variance-sources, the worked-example table (`app_statmethods.tex:527–538`), the audit table (`:1067–1090`), and the app_history errata (new rows).
- **Figures to replace:** paper Fig. 1, note Figs. 6/7 (two files), note `fig:bootstrap` (two files). `fig:seedscan` has no replacement.

---

## 5. Open questions for the director

- **Q1. Universe count.** S5 drops Rvp1pi: 43 bands + norm, versus VL175's 44 + norm. `s5.json` records the check
  `july_44_bands_187_universes` with `value: null`, and `budget_Q` gives no universe count for the rollup. Should the
  text say 187, or 185 (187 − the two Rvp1pi universes)? This needs a receipt field.
- **Q2. Error-bar claim.** `sec_results.tex:5–7` says the unfolded-point error bars are the total uncertainty. But
  `fig:xsec` (`plot_2d_threeway_fig13.py`, `plot_2d_cross_section.py`) draws `hXSec2D.GetBinError`, a per-histogram
  error and not any covariance. The claim was not true of VL175 either. Q changes nothing here, but phase 2 should not
  leave the sentence implying Q.
- **Q3. Combined |pull|.** `app_statmethods.tex:631` "No reported bin has |pull|>3" (combined). The Q logs print
  only the mean and RMS. The max needs a re-read of the pull array, or the sentence goes.
- **Q4. Condition-number conventions.** The old cond `8.7e8` for C_syst does not match either `budget_Q` threshold
  (universe cond 9.93e9 at 1e-10, 4.93e11 at 1e-12). Also, the note's "rank 140" corresponds to Q's 137 at 1e-12. The
  phase-2 text must name the threshold.
- **Q5. Learner dependence against the seed block.** "The learner dependence is about five times the seed block's σ"
  (`sec_systematics.tex:109–111`) becomes about 17× against c08 (0.98/0.057, derived). The receipts give no
  per-bin ratio. Print a derived number, or drop the comparison?
- **Q6. Seed-scan material.** This covers the seed-scan figures, §`sec:seedscan`, the 0.166% "ML floor" (used as a
  closure-threshold reference), the 1.24× split variant and the n=4→10 convergence. Should it be kept as history,
  moved to `app_history`, or removed? (SPEC §3a leaves it to phase 2.)
- **Q7. Retired stat-block material.** This covers the VL170-era split-bootstrap numbers (1.07, 77/23, 0.95, 0.356,
  0.108, 0.46, 76.7, 252), the 50→300 convergence and 1A 1.46%. None has an S5 counterpart. Should they be labelled
  "earlier bootstrap" or removed? Only 0.416 → 0.428 has a receipt.
- **Q8. History clause.** Should the "an earlier version quoted 6.87 %" sentences (`sec_execsummary.tex:26`,
  `sec_results.tex:144`, `paper_body.tex:262`, `primer_body.tex:211`) gain a VL175 6.09 % step, or drop the history
  entirely? This is J4 register.
- **Q9. Sec. IV checker.** `check_sec4_receipts.py` cannot read the gzipped `budget_Q.json.gz`. Should phase 2 add
  gzip support (a code change to a build gate, needing review) or commit an uncompressed copy?
- **Q10. Missing log.** REPORT §1 cites `outputs/logs/stepA.log`, but there is **no `logs/` directory** under
  `rebuild/outputs/` on `ae198cc1` (it is in neither git nor the tree). It is on CFS only: `SHA256SUMS.cfs:112`
  `366c5728…  ./logs/stepA.log`, with `fig67_Q.log` and `stat_figs.log` beside it. The REPORT link is dead in the repo.
  Commit the logs, or reword the link.
- **Q11. `make_figs.py` docstring.** It is stale ("VL170/VL172"). Editing it changes the pinned digest `9c4dbf24…`
  used by `make_fig1_q.py`/RUN-fig1. Leave it?
- **Q12. Flux sentences.** "Ours a little smaller … partly because of the flux" and "4.99 % without the
  constraint weights": the S5 flux is 3.75 % against the published 4.01 %, so the direction holds. The unweighted
  4.99 % is VL-era and has no S5 counterpart.
- **Q13. Records outside the deliverables, for K1–K4.** These are not deliverable sites, listed so they are not
  missed:
  - `AGENTS.md` scientific-picture row (6.09 %, VL175);
  - `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md`;
  - `docs/publication/audit-20261008/CLAIM-TABLE-20261008.tsv` and `notes/claims-skeleton.tsv`;
  - the claims map `docs/publication/CLAIMS-20261005-claim-to-evidence.md` (R5).
