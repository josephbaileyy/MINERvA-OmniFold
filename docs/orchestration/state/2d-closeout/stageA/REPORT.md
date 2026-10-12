# 2D closeout Stage A: the candidate checklist for `E_U`, item by item

**CITABLE FOR:**
- the item-by-item Stage A candidate checklist of
  [`PLAN-20261011-2d-closeout.md`](../../../PLAN-20261011-2d-closeout.md) §4 for `E_U`, the quoted
  LightGBM seed-42 central value: cell identities, units, POT, target count, flux, purity and background
  inputs, completeness and effective seeds;
- the candidate's manifest, and an independent recomputation of its cells, integral and
  regeneration agreement;
- the Stage A exit verdict.

**NOT CITABLE FOR:**
- any uncertainty, covariance, coverage or calibration result;
- the publication consumers' cell-identity checks (KI 90): row 1 checks `E_U`'s own cell set only, and
  KI 90's closure needs a refusing same-size, different-cell negative control in those consumers;
- the flux-universe index identity (KI 91), the GENIE duplicate (KI 92), the universes' zero point
  (KI 93), background-template statistics (KI 94) or the seed-1/seed-42 pairing (`P07`). Those are Stage B
  or later;
- an adoption, a re-quote, a changed gate, a KI-85 lift or compute authority.

| field | content |
|---|---|
| `Owner` | 2D closeout executor (2d closer), directed by the paper-tighten lane under [`AUTHORIZATION-20261012-2d-closeout-delegation.md`](../../../AUTHORIZATION-20261012-2d-closeout-delegation.md) |
| `Deliverable` | A-2 of the director's 2026-10-12 assignment: the plan §4 Stage A candidate checklist |
| `Branch` / `Base` | `closeout/stage-a-checklist-20261012` / `origin/main` `7edb65fab817b9bf04749dcafb12971352b3c64f` (PR #93). The work was done at `37985acc` (PR #92); every cited path is byte-identical between the two |
| `Decision` | Is `E_U` one reproducible candidate with a complete manifest and an independent comparison (plan §4 Stage A exit)? |
| `Terminal outcomes` | EXIT MET, or STOP (reproduction failure, unexplained input drift, unavailable required receipt) |
| `Compute` | Login-node reads only (saul `login05`), plus scripts writing only under `/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/a2/`. **No Slurm job; 0 charged node-h.** No product or publication namespace was written |
| `Owner / reviewer` | Owner: Claude Opus 5.5 (`claude-opus-5-5`), a worker fork of the 2d-closer session. Reviewer: §7 |

`S` = `docs/orchestration/state/2d-closeout/stageA` (this record). Code citations are `file:line` at
`37985acc`.

## 1. Answer

**EXIT MET for the candidate procedure, via L0.** The plan's exit asks for "one reproducible candidate
with a complete manifest and an independent comparison". `E_U`'s own manifest is **not** complete: its
driver and helper bytes, environment, threads, input digest and effective seeds were never recorded
(decision record §3; §4 below). The complete manifest is that of its receipted regeneration L0 (XR, job
59660487), which plan §4 allows to supply the candidate ("a separately verified L0 delivery can supply the
candidate"). So:
- **The candidate procedure, frozen for Stages B and C,** is L0's: driver `3cc5adc7…`, helper
  `e9623412…`, CV omnifile `43f8cc16…`, flux `d40aea69…`, L0's recorded environment, 64 LightGBM threads,
  seeds 42/43/44, `--iters 5 --use-weights --estimator lgbm --seed 42`, `bkg_mode purity` (§4).
- **`E_U`** (`2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`, sha256
  `4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c`) is the quoted file. It passes every
  checklist item and is equivalent to that procedure's output under the frozen 1e-8 criterion: a
  recomputation from the product vectors, without the XR comparator, agrees with L0 to 1.4e-11.
- **Do not re-run `E_U`'s launcher** as the candidate producer. Its omnifile path now holds a different file
  (§4, §8).
- **Producer change.** Once the selective-I/O delivery merges (A-1), `main`'s driver is no longer
  `3cc5adc7…`. A Stage C producer on the new driver needs the plan §4 equivalence bridge to L0 first.

No Stop condition was met (§6). Stage A's other remainder, the selective-I/O delivery, is outside this
record's scope and is delivered separately (A-1).

| # | item | verdict | measured | comparison partner |
|---|---|---|---|---|
| 1 | 205 cell identities (`E_U`'s own set; not KI 90) | **VERIFIED** | 205 positive cells, 19 zero, 0 negative; edges and GlobalIDs equal the paper's | paper `bin_mapping.txt` and `data_result…txt`; XR `references.json` CV42 |
| 2 | units | **VERIFIED** | `hXSec2D` recomputed from its own ingredients to 4.4e-16; integral 3.0730230563866027e-38 cm²/nucleon | paper units; VL173 receipt (`integral_ours_all_bins` bitwise; `integral_ours_reported` 1 ulp away) |
| 3 | POT | **VERIFIED** | data 1.057394261158926e21, MC 4.978198462880827e21 | sums of the 12 playlists' `POTUsed`; both omnifiles; the flux file |
| 4 | target count | **VERIFIED** | 3.2352943296224835e30 | MAT `TargetUtils::GetTrackerNNucleons` re-run on the cluster (bitwise) |
| 5 | flux | **VERIFIED** (the flux this central uses) | `hFlux_pt` = flux file `d40aea69` exactly = the 12-playlist POT-weighted recombination to 2.2e-16 | flux file; per-playlist fluxes; six other products |
| 6 | purity / background inputs | **VERIFIED** | 4 saved inputs bitwise equal to L0 (`bkg_mode purity`), `E_C` and the July CV | L0 `runConfig`; driver purity rule |
| 7 | completeness | **VERIFIED** | max \|c − 1\| 1.6e-14 over the 205 cells; bitwise equal to L0 and `E_C` | omnifile tree counts |
| 8 | effective seeds | **VERIFIED BY CONTENT, NOT RECORDED IN THE FILE** | equals L0 (seeds 42/43/44) to 1.4e-11; every seedscan seed 1–10 differs in all 205 cells (median ≥ 1.6e-3) | L0 receipt; seedscan products |

## 2. Product identity

- **pscratch** `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`:
  55,531 B, mtime 2026-05-27 04:58 (PDT); sha256 `4f5a1b6d…` re-measured on `login05` on 2026-10-12.
- **CFS copy** `/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/uq/…`:
  the same size and sha256, and all 205 cells bitwise equal (`operands/analysis.json` `reproduction.E_U_cfs`).
- **Objects:** 25 keys: 16 histograms (13 `TH2D`, 3 `TH1D`), 7 `TParameter`s, and 2 `TNamed`
  (`fluxSource`, `hEffDenSource`). There is no
  `runConfig`, `runArgv` or driver digest: the file predates `971fc00c`. L0 carries all of them.

## 3. The checklist

Every number below is in [`operands/analysis.json`](operands/analysis.json), produced by
[`scripts/analyze.py`](scripts/analyze.py) from the cluster dumps in `operands/`. §5 lists the scripts and
digests.

### 3.1 Cell identities: VERIFIED

- `hXSec2D` is a `TH2D` of 14 p_T × 16 p_∥ bins. Its edges equal the paper's `bin_mapping.txt` exactly:
  p_T 0, 0.07, 0.15, …, 4.5 and p_∥ 1.5, 2.0, …, 60 GeV/c. The mapping's
  `GlobalID = (Ptbin−1)·16 + (P∥bin−1)` holds in all 224 rows.
- **205** cells are positive, **19** are exactly zero and **none** is negative. Under- and overflow sum to 0.
- The positive set equals the paper's reported set (`cross_section > 0` in
  `data_result_ptpl_2D_minerva_inclusive_6GeV.txt`) cell for cell. It also equals XR's frozen
  `references.json` CV42 list. The 19 unreported GlobalIDs are 144, 160, 161, 176–178, 192–196 and 208–215.
- **Limit.** This checks `E_U`'s own cell set. The two publication consumers' identity checks (KI 90)
  are a separate item in the plan's §3 issue map, outside the §4 Stage A candidate checklist that is A-2's
  scope. This row does not close KI 90.

### 3.2 Units: VERIFIED

- **Recomputation from the file's own ingredients.** Each of the 205 cells was rebuilt as
  `hUnfold2D / (hOFCompleteness2D · hFlux_pt[m⁻²/POT] · nNucleons · dataPOT · ΔpT · Δp∥) · 1e4`. This is the
  driver's formula (`2d-unfolding/unfold_2d_omnifold_unbinned.py:888–945`) and the MINERvA-101 `normalize`
  (`MINERvA101/MINERvA-101-Cross-Section/ExtractCrossSection.cpp:122–128`). It reproduces the stored
  `hXSec2D` to a maximum relative difference of **4.4e-16** (median 0).
- **Units.** The result is cm² (GeV/c)⁻² nucleon⁻¹. The data release's README states cm²/(GeV/c)²
  (`minerva_paper_anc/README`); "per nucleon" is the paper's and the MINERvA-101 normalization's convention.
- **Projections.** The stored `hXSec_pt` and `hXSec_pz` equal the bin-width-weighted 2D sums to
  4.3e-16 and 0.
- **Integral.** Σ x · ΔpT · Δp∥ over the 205 cells is **3.0730230563866027e-38** cm²/nucleon. Summing all
  224 cells gives the same value. In the VL173 receipt
  (`receipts/2d-lgbm42-20261011/RECEIPT-2d-agreement-windows-lgbm42-20261011.json`) it is bitwise equal to
  `integral_ours_all_bins`, and 1 ulp from `integral_ours_reported` (3.073023056386603e-38), a summation-order
  difference. `scripts/analyze.py` does not open the receipt; this comparison was made separately, and
  re-made by the reviewer (§7).
- **Ratio to the paper.** Against the paper's text file, rounded to three significant figures, the
  integral is 3.03950e-38, giving ratio 1.01103 and median bin ratio 1.00836. The receipt reads the
  paper's ROOT values (3.03901e-38) and gets 1.0112 and 1.0081. The difference comes from the text file's
  rounding. No quoted number moves.

### 3.3 POT: VERIFIED

- `dataPOT` = **1.057394261158926e21**. This equals the sum of the 12 ME-FHC playlists'
  `runEventLoopData_<pl>.root:POTUsed` (relative difference 0). It also equals `dataPOTUsed` in both
  omnifiles (§4) and `DataPOTUsedForFluxWeighting` in the flux file.
- `mcPOT` = **4.978198462880827e21**. This equals the sum of the 12 `runEventLoopMC_<pl>.root:POTUsed`
  (−2.2e-16, summation order) and both omnifiles' `mcPOTUsed`.
- `potScale` = `dataPOT/mcPOT` exactly.
- **Published exposure.** The paper quotes 10.61e20 POT, 0.34 % above this value. This known difference
  of production is recorded at
  `docs/publication/corrections-20261008/RECORD-20261008-release-audit-corrections.md:90`; it is not a
  defect of `E_U`.
- All seven normalization parameters are identical across `E_U`, its CFS copy, L0, L1, the July CV
  (`PN_CV`), the seed-1 central and `E_C`.

### 3.4 Target count: VERIFIED

- `nNucleons` = **3.2352943296224835e30**, equal to the driver constant
  `TRACKER_FIDUCIAL_N_NUCLEONS` (`2d-unfolding/unfold_2d_omnifold_unbinned.py:41`).
- **Recomputation.** MAT's `PlotUtils::TargetUtils::Get().GetTrackerNNucleons(5980, 8422,
  isMC=true, 850)`, re-run on `login05` with the canonical environment's MAT libraries, returns
  3.2352943296224835e30 bitwise (`operands/target_count.out`). This re-runs the call that produced the driver
  constant (driver `:38` comment), so it confirms the transcription rather than deriving the count
  independently. The call's parameters are those of the selection: `minZ=5980, maxZ=8422, apothem=850` at
  `runEventLoop.cpp:361` and in the omnifile producer `runEventLoopOmniFold.cpp:1708`. The `isMC=false` geometry gives
  3.234779999602547e30 (−0.016 %).
- **Convention.** The MC count is the MINERvA-101 convention: `runEventLoop.cpp:483` writes
  `GetTrackerNNucleons(minZ, maxZ, true, apothem)`, and `ExtractCrossSection.cpp:195` normalizes by it.
- The 1.4 % target-normalization uncertainty belongs to the Stage B source table.

### 3.5 Flux: VERIFIED (the flux this central uses)

- **The histogram.** `E_U`'s `hFlux_pt` equals `baseline_flux/runEventLoopMC_MEFHC.root:pTmu_reweightedflux_integrated`
  (sha256 `d40aea69…`, re-measured) exactly, bin for bin. The same `hFlux_pt` is in all six other products.
- **Recombination.** Rebuilding the data-POT-weighted average of the 12 per-playlist
  `pTmu_reweightedflux_integrated` histograms (the rule of `2d-unfolding/combine_flux_MEFHC.py`)
  reproduces the file to **2.2e-16**. The playlists differ from the combination by at most 0.77 %.
- **Values.** The histogram carries the integrated flux, **6.2433433768512e-4 m⁻²/POT**, broadcast to all
  14 p_T bins (as two adjacent doubles, 6.243343376851218e-4 and 6.243343376851219e-4).
  - `fluxIntegral_m2_per_POT` = 8.740680727591705e-3 is the sum of the 14 equal bins, i.e. 14 × Φ. It is
    metadata, not the integrated flux.
  - `fluxIntegral_cm2_per_POT` is that sum × 1e-4, exactly.
- **Observations, neither of which changes a value:**
  1. **`fluxSource` names a file that no longer exists.** The string reads
     `…/baseline_flux/runEventLoopMC_MEHFC.root`, the name before the rename in `c7ae2206`; `ls` of
     `baseline_flux/` shows no such file. The content identity was already measured (two-d-followup admission
     review B-7) and is re-measured here by the bitwise `hFlux_pt` equality. L0 records the `MEFHC` name.
  2. **The flux histogram's p_T edges are not the analysis edges.** The flux file's edges are
     0, 0.075, 0.15, 0.25, 0.325, 0.4, 0.475, … (`dansPTBins`, `runEventLoop.cpp:407`), against the
     paper's 0.07, 0.33 and 0.47 at three boundaries. The driver uses the histogram by bin index and checks
     only the bin count (`unfold_2d_omnifold_unbinned.py:126–142`). Since the 14 values are equal to 1 ulp,
     the mismatch has no numerical effect.
- **Out of scope (Stage B).** Flux universes, the PPFX index identity (KI 91) and the flux–muon-energy
  joint treatment (X01) are Stage B items. The flux model is not compared with the paper's here.

### 3.6 Purity and background inputs: VERIFIED

- **The saved inputs.** `E_U`'s `hDataReco2D` (Σ 4,091,707 events, inside the reco window),
  `hBkgReco2D` (Σ 119,132.37, 2.91 % of data), `hMeasSub2D` and `hMeasTrain2D` are bitwise equal to:
  - L0's, whose `runConfig` records `"bkg_mode": "purity"`, `"use_weights": true` and `"iters": 5`;
  - `E_C`'s;
  - the July CV's.
- **The purity rule.** The driver's purity mode is a per-reco-bin `max(0, (N_data − N_bkg)/N_data)`
  data down-weight (described at `unfold_2d_omnifold_unbinned.py:1488`; `hMeasSub2D` built at `:1472–1474`;
  weights from `build_measured_training_2d`, `:338`, called at `:1475`). In `E_U`:
  - `hMeasSub2D` equals `max(0, hDataReco2D − hBkgReco2D)` exactly;
  - `hMeasTrain2D`, the down-weighted training target, equals it to 2.7e-12 relative.
- **The truth side.** `hTruth2D`, `hEffNum` and `hEffDen` are also bitwise equal to L0's.
- **What this establishes.** `E_U` stores no `runConfig`. Its purity treatment is established by the
  bitwise equality of these inputs and by L0's 1.4e-11 regeneration under a recorded `bkg_mode purity`.
- **Out of scope.** Background-model variations (P06/C06) and background-template statistics (KI 94)
  are Stage B items.

### 3.7 Completeness: VERIFIED

- `hOFCompleteness2D`: max |c − 1| = **1.58e-14** over the 205 cells, and over every nonzero cell. The 19
  zero-completeness cells are exactly the 19 unreported cells. Global c = Σ`hOFInputTruth2D` /
  Σ`hOFTruthDenom2D` = 1 − 1e-16. It is bitwise equal to L0's and `E_C`'s.
- **Omnifiles.** Both (§4) have `mc_truth_denom` = `mc_signal_reco` = **32,849,103** entries,
  `nTruthOnlyMisses` 8,999,007, `mc_background` 658,227 and `data` 4,119,797.
  - `hasTruthOnlyMisses` is stored as 12: `hadd` summed the 12 playlists' flag. The driver reads it as a
    boolean (`unfold_2d_omnifold_unbinned.py:1348`).

### 3.8 Effective seeds: VERIFIED BY CONTENT, NOT RECORDED IN THE FILE

- **What `E_U` records.** Nothing about its seeds. Its launcher text passes `--seed 42`
  (`2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh:49`). That text was last changed in
  `069c3b84` (2026-08-01), after `E_U`'s mtime (2026-05-27), so it is evidence of intent, not of execution.
- **L0** (`state/next-preparation-20261009/xr-linux/results/outroot/L0/a1/receipt.json`):
  - 10 `LGBMClassifier` fits (random_state 42 at step 1, 43 at step 2) and 5 `LGBMRegressor` fits (44),
    following the driver's seed rule (`unfold_2d_omnifold_unbinned.py:1741–1744`);
  - 64 LightGBM threads at every fit and predict.
- **Independent comparison (`E_U` against L0's CFS copy, sha256 `75138024…`).**
  - Max relative difference **1.375e-11** (GlobalID 171), median 5.88e-12, integral 7.0e-13. All 205
    cells are under the frozen 1e-8 criterion, and none is bitwise equal.
  - This is the same as XR's `L0_vs_CV42` (1.4e-11, 5.9e-12, 7.0e-13) and was computed without XR's
    comparator or its reproduction script. It is independent of XR's code, not of the owner: it reads
    values through `GetBinContent`, as XR does. The reviewer's read, through `TH1::GetArray()` buffers,
    reproduced the same numbers exactly (§7).
- **Seed identification.** `E_U` against each LightGBM seedscan product, seeds 1–10 (sha256 in
  `operands/analysis.json` `seedscan_vs_E_U`):
  - every seed differs in all 205 cells, median 1.6e-3 to 2.3e-3 and max 1.5e-2 to 3.2e-2;
  - L1 (seed 1) and the seed-1 central agree with each other and differ from `E_U` by a median of 1.8e-3;
  - `E_C` differs by a median of 9.9e-3.

  The seed effect is about 10⁸ times the L0 agreement, so `E_U`'s effective seeds are 42/43/44 by content.
- **Threads.** `E_U`'s launcher requests 128 CPUs and `OMP_NUM_THREADS=128` (`…_CV.sh:8,21`); this was
  not recorded at run time. L0 used 64. The 1.4e-11 difference lies inside the pre-registered 5.8e-9
  thread prior (XR REPORT §1).

## 4. Manifest

| field | `E_U` (the candidate) | L0 (its receipted regeneration) |
|---|---|---|
| product | `4f5a1b6d…`, 55,531 B; pscratch and CFS | `XR-L0.root` `75138024…`, 60,691 B, CFS `/global/cfs/cdirs/m3246/josephrb/xr-linux-20261011/outputs/L0/a1/` |
| estimator | LightGBM, 100 trees, 8 leaves, lr 0.1, 5 iterations (decision record) | same; classes, seeds and threads in the receipt |
| driver | **not recorded** | `unfold_2d_omnifold_unbinned.py` sha256 `3cc5adc7…` (last change `355174fe`) |
| helper | **not recorded** | `unbinned_unfolding/python/omnifold.py` sha256 `e96234124a31…` |
| argv | launcher text only (`…_CV.sh:43–50`) | `--iters 5 --use-weights --estimator lgbm --seed 42`, recorded |
| MC/data input | **digest not recorded**. The launcher path `runEventLoopOmniFold_MEFHC_universes_full.root` now holds a file with mtime **2026-07-08**, after `E_U`'s 2026-05-27, so it is not `E_U`'s input as run (171,117,087,867 B; sha256 `220c479e…`, §8) | CV omnifile, CFS copy, sha256 `43f8cc16…`, 2,144,008,221 B; hashed at the start and end of the run |
| flux | `fluxSource` names the pre-rename `MEHFC` file; content equals `d40aea69…` | `baseline_flux/runEventLoopMC_MEFHC.root`, `d40aea69…` |
| normalization | the 7 parameters of §3.3–3.5 | identical |
| environment | **not recorded** | Python 3.11.14, ROOT 6.28/12, lightgbm 4.6.0, numpy 1.26.4, scipy 1.16.3, scikit-learn 1.8.0, joblib 1.5.3 |
| threads | 128 requested (launcher text) | 64, checked at every fit and predict |
| binning / cells | 14 × 16 paper edges, 205 reported cells | identical |

Both omnifiles carry the same POT, miss count and tree entry counts (§3.3, §3.7). The saved reco and
truth inputs of `E_U` and L0 are bitwise equal (§3.6).

## 5. Evidence

Cluster reads were made on 2026-10-12 on `login05`. The scripts open every product read-only and write
only to `/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/a2/`. Each output's sha256 was measured on
the cluster and again after the copy into `S`:

| file | sha256 | what |
|---|---|---|
| `scripts/read_products.py` | `24eeab22…` | the 7 products, the flux file, 2 omnifile headers → `operands/products.json` (`fe6f0d9a…`) |
| `scripts/read_inputs.py` | `7462fb5a…` | 12 playlists' POT and flux, omnifile tree counts → `operands/inputs.json` (`d192bbcb…`) |
| `scripts/read_seedscan.py` | `ed71e1ec…` | seedscan seeds 1–10 → `operands/seedscan.json` (`ce09b75a…`) |
| `scripts/target_count.py` | `692830d1…` | MAT `GetTrackerNNucleons` → `operands/target_count.out` (`4ba4b683…`) |
| `scripts/analyze.py` | `0eb4d312…` | local, numpy only → `operands/analysis.json` (`1fe7b04f…`) |

`read_inputs.py` and `target_count.py` need MAT's dictionaries. They were run after sourcing the
canonical checkout's `setup_salloc_env.sh`; the others under `root_6_28`. To re-derive the analysis:
`python3 S/scripts/analyze.py S/operands <repo root>`. Re-running it reproduced `analysis.json` byte for
byte.

## 6. Stop conditions

None was met.
- **Reproduction.** L0 reproduces `E_U` under the frozen criterion, re-measured here.
- **Input drift.** `E_U`'s actual input is unavailable (KI 93: "The May file and code revision are
  unavailable"), so drift cannot be excluded by digest. Its equivalence to L0's input `43f8cc16` is
  inferred: bitwise-equal binned saved inputs, and above all the 1.4e-11 output agreement (a different event
  sample would move LightGBM at about 1e-3). This is no unexplained drift, so no Stop. The July file at the
  launcher path belongs to Stage B's KI-93 reads.
- **Required receipts.** L0's receipt, admission record and comparator output are on `main`. `E_U`'s
  missing run log was disclosed before this checklist (decision record §3), and plan §4 accepts L0 in its
  place.

## 7. Independent review

**Setup.** One fresh read-only reviewer: a general-purpose Claude Opus 5.5 session, in its own detached
worktree at `8d086a20` (empty `git status` at start and end; removed). Cluster writes only under
`…/2d-closeout-stageAB-20261012/review-a2/`; no Slurm job. Budget: one review plus at most two focused
re-reviews (plan §5).

**Initial review of `8d086a20`: PASS WITH CHANGES** (1 MATERIAL, 4 MINOR, 9 NOTE), preserved verbatim at
[`review/review-8d086a20.md`](review/review-8d086a20.md). Its own reads (via `TH1::GetArray()` buffers, under
two environments) reproduced the `E_U` and L0 digests, the 205-cell set, the integral, `E_U` vs L0
(1.3751444427612114e-11, GlobalID 171), POT and the flux recombination. `analyze.py` re-ran byte for byte; 14
citations checked; both hygiene gates green.

**Repair batch 1 (cycle 1 of at most 2):**

| finding | disposition |
|---|---|
| M1: "EXIT MET" named `E_U` as having a complete manifest; no frozen producer declared | §1 now states the exit is met for the candidate procedure via L0, declares L0's manifest as the producer frozen for Stages B and C, and says not to re-run `E_U`'s launcher; CATALOG row says "via L0" |
| m1: integral "bitwise equal to `integral_ours_reported`" is 1 ulp off | §1 table and §3.2 now say bitwise equal to `integral_ours_all_bins`, 1 ulp from `integral_ours_reported` |
| m2: KI 90 missing from NOT CITABLE FOR; plan misquoted | added; §3.1 attribution corrected; row 1 labelled "`E_U`'s own set; not KI 90" |
| m3: §6 "None found" overstated | §6 now says the input is unavailable and its equivalence inferred |
| m4: the selective-I/O remainder unmentioned | §1 says it is outside this record and delivered as A-1 |
| N1 base; N2 key count; N3 flux doubles; N4 units source; N5 target count is a transcription check, with the parameters' sources; N6 purity citation; N7 omnifile digest; N8 independence of the comparison | all applied in place |
| N9 (a 0.35 % in another record) | not this record's; no change |

**Focused re-review:** see below.

**Same-model caveat.** Owner and reviewer are Claude Opus 5.5 sessions. Distinct sessions of one model are
not cross-provider independence (plan §5).

## 8. Limits

- `E_U`'s own execution provenance (driver, helper, environment, threads, input digest, seeds) is
  **NOT AVAILABLE**. Every "VERIFIED" above is about the file's contents and its agreement with L0's
  recorded execution.
- **Launcher-path omnifile digest:** the `sha256sum` started on `login05` at 08:07:38Z ended at 08:20:38Z:
  `220c479efa9751116fd396ea32398de5631f8b755e6b16a94ce090975f011418`
  (`/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/a2/eu_omnifile.sha256`; read by the reviewer). It
  describes the July file, not `E_U`'s input.
- The paper comparison of §3.2 uses the three-significant-figure text file, so it is descriptive. The
  quoted ratios come from the VL173 receipt.
- No item here tests an uncertainty.
