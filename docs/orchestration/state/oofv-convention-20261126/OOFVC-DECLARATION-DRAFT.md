# OOFVC: the 2D central values under MINERvA's counting convention. Inventory and DRAFT declaration (nothing run)
<!-- absence-ok: the lane's own status (no job of this study has run), not a claim that a result does not exist -->

**By** the `ibu-chi-squared-issue` session for the director, on Joseph's request of 2026-11-26. **Status: DRAFT.**
Nothing has run, and nothing has touched NERSC. No number in this file comes from a new computation. Every value
below is copied from a committed record, and its path is given.
- Repository state read: main at `59ffb4643`. The exploratory branch `analysis/ibu-oofv-convention-20261126` was read
  at `0a6e3f4e`.
- The deploy commit for any rerun is M = `77d76cfc`. That is REF-C2C1's deploy, where Tier 1 ran. At M,
  `re2_driver.py` is `938c53c5…` (equal to `ref_c2c1/config.json`'s pin) and `ref_c2c1.py` is `285dd138…` (unchanged
  on main). Main's `re2_driver.py` is `e226daf3…` and no longer matches the pin, as Tier 1 found.

## 0. The question

What do the central values give under MINERvA's counting convention, against the published result with the note's
metric?
- **(a)** Ten-iteration binned IBU: the note's `c2c1-dibu` quantity.
- **(b)** The 2D OmniFold central value (E_R's estimator).

Same inputs and the same estimator settings otherwise. Central values only, with no covariance and no universes.

## 1. Inventory

### 1.1 The two conventions, from the code

| | this analysis (production) | MINERvA's 2021 code |
|---|---|---|
| selected event that is ν_μ CC and in the phase space | signal: migration and numerator | signal: migration and numerator |
| selected ν_μ CC event failing the phase space (true vertex outside the fiducial volume, or θ_μ ≥ 20°, or p∥ outside 1.5–60 GeV/c, or p_T ≥ 4.5 GeV/c) | **background**, subtracted (`runEventLoopOmniFold.cpp:1453-1456` @ 57792e42: `if(isSignal && inPS_bkg) continue;`) | **signal**: it fills the efficiency numerator at its true (p_T, p∥) and the migration |
| selected event that is not ν_μ CC (NC, ν̄_μ, ν_e) | background | background |
| efficiency denominator | ν_μ CC in the phase space (`mc_truth_denom`) | ν_μ CC in the phase space (`isEfficiencyDenom`) |

MINERvA's side comes from the cited code, downloaded on 2026-11-26 into the lane's scratch (sha256 in brackets).
1. **`MAT/PlotUtils/Cutter.cxx` @ 0111c79de** (5c672d86…). `isSignal` (`:131-134`) tests only the signal definition.
   `isEfficiencyDenom` (`:143-148`) tests `isSignal && isPhaseSpace`.
2. **`MAT-MINERvA/calculators/CCInclusiveSignal.h` @ f790cc794** (2fcac404…).
   - The signal definition (`:125-133`) is `IsNeutrino`, `IsCC`.
   - The phase space (`:112-122`) is `ZRange` 5980–8422, `Apothem` 850, `MuonAngle` 20, `PZMuMin` 1500.
3. **`MINERvA-101-Cross-Section/runEventLoop.cpp` @ bb6c1634** (edda04b6…, `:205-232`). It fills the 2D
   `efficiencyNumerator` at true values when `isMCSelected && isSignal`.
4. **The vendored tutorial loop** (`MINERvA101/MINERvA-101-Cross-Section/runEventLoop.cpp:128-157`) fills the numerator
   and the migration under `isSignal`. Everything else goes to the background.

The exploratory README's caution stands: this is the convention of MINERvA's released comparison code. Parity with
the 2021 publication's final production histograms has not been established.

### 1.2 What the existing dumps carry (question 1)

**Production omnifile** `runEventLoopOmniFold_MEFHC.root`, sha256 43f8cc16…, the CV input of E_R, REF-C2C1 and Tier 1.
<!-- absence-ok: statements about the branches this analysis's own event loop writes, each with its source record, not a claim that a result does not exist -->
- **Its `mc_background` tree has no truth labels.** The oflow probe found this before reading any number
  (`ibu-chi2-20261123/oflow/DECLARATION.txt`, amendment 1).
- **The labels are in a second file.** The 5D file `nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root`
  carries `bkg_nuPDG`, `bkg_current`, `bkg_inttype` and `bkg_vtx_{x,y,z}` (`runEventLoopOmniFold.cpp:1367-1372`, filled
  at `:1466-1472`).
- **The two files line up row for row.** Its `mc_background` reco columns and weights equal 43f8cc16's event by event
  (C-SAME, 658,227 rows each; `oflow/split.json`).
- **No `mc_background` tree carries the true muon kinematics,** in either file. The background loop books reco
  kinematics, the weight, those labels and, under `MNV101_DUMP_POINTCLOUD` only, reco muon fields and the event key
  (`:1360-1393`). It books no true p_T, p∥ or θ_μ.
- **So the reclassification cannot be done offline from the existing dumps.** A row can be identified as ν_μ CC and
  out-of-fiducial, but it cannot be placed in the migration or the numerator, because both need its true (p_T, p∥).
- **The size of what moves.** These are the oflow categories, weighted and POT-scaled, on our 14×16 reco grid
  (`oflow/split.json`).

| category (oflow) | rows | weighted sum | MINERvA's convention |
|---|---:|---:|---|
| FAKE_VTX: ν_μ CC, true vertex outside the fiducial volume | 505,515 | 98,861.2 | signal |
| FAKE_PS: ν_μ CC, fiducial vertex, true muon outside the phase space | 68,175 | 11,832.6 | signal |
| OTHER: NC, ν̄_μ, ν_e | 47,857 | 8,438.6 | background |

- **Precharge's tables are partial.** `precharge-20261125/inputs/events/*_MC.csv.gz` (from `measure.cpp`) carry true
  p_T, p∥, PDG, current and a fiducial flag for selected MC. They cover only reco p∥ ≥ 20 GeV/c and reco p_T < 4.5
  (`measure.cpp:63-66`), and they omit the reco charge cut (`reco::IsNeutrino`, production `:1715`). The exploratory
  replay is partial for that reason (its README).

**Two ways to obtain the true muon kinematics** (the smallest change is A):
- **A. An AnaTuple pass and an exact join; the omnifile is unchanged.**
  - The program is `precharge-20261125/measure.cpp` with five changes:
    1. no 20 GeV skip and no reco-p∥ window;
    2. the production reco cuts exactly (`:1710-1715`), with `reco::IsNeutrino` added;
    3. the production signal definition and phase space (`:1717-1741`);
    4. it writes only selected ν_μ CC rows that fail the phase space;
    5. its columns are the event key (`mc_run`, `mc_subrun`, `mc_nthEvtInFile`), reco p_T and p∥, true p_T, p∥ and
       θ_μ, the vertex, and the MnvTune v1 weight.
  - The model is the same five reweighters as production (`measure.cpp:34-39` = `runEventLoopOmniFold.cpp:1745-1750`).
  - Its rows are joined to 43f8cc16's `mc_background` rows on the exact triple (reco p_T, reco p∥, `w_bkg`).
  - **C-JOIN:** every ν_μ CC background row of 43f8cc16 (labelled through C-SAME) matches exactly one dump row, and
    vice versa. If not, STOP, and fall back to B, declared here and not chosen after.
  - **Its advantage:** flag-off runs read the very file Tier 1 read, so the baseline is Tier 1's own numbers.
- **B. An event-loop flag.** It is new, env-gated and default off: `MNV101_DUMP_BKG_TRUTHMU`. It writes
  `bkg_mu_true_pt`, `bkg_mu_true_pz` and `bkg_mu_true_theta` on `mc_background` from the truth accessors the signal
  loop uses, and nothing else changes.
  - It needs a rerun of the 2D event loop over the 12 playlists and the `hadd` merge
    (`2d-closeout/stageA/REPORT.md:201`).
  - **C-EVL:** every existing tree's entry count, and every existing branch row by row, equals 43f8cc16's. Otherwise
    STOP: a reordered input changes the LightGBM runs, and with them the baseline.

### 1.3 The code behind the two quantities (question 2)

**`c2c1-dibu` = 0.54.** It is D_IBU at K = 10 on the paper's p_T edges: 0.538050 in `ibu-chi2-20261123/regenA3/out/ladder.json`
(565d1f99), set `e`, read by `make_values_fived16.py:1934-1948`. Its chain:
- **Tier 1** (`ibu-chi2-20261123/tier1/`, job 61928141, about 0.18 node-h) ran REF-C2C1's runner at M. The runner is
  `2d-unfolding/ref_c2c1/ref_c2c1.py`, REF-C2C1's code and limitation-resolver's lane.
  - Its unit `c2_central` replaces the driver's one OmniFold call with binned D'Agostini IBU on the same arrays.
  - That means the response from `w_reco` over `w_truth` (`ref_c2c1.py:244-259`).
  - The measured histogram is E_R's refined per-event weights summed per reco bin.
  - The efficiency comes through the driver's misses and its own completeness and extraction (`:360-420`).
  - The patch was `re2_driver.py:44`'s three p_T edges (`tier1/receipts/tier1_deploy_e.diff`, driver pin 677ac75f…).
- **Scoring:** `tier1/score_t1.py` → `score.out`. That is χ²(ours − published)/205 under the published TotalCovariance,
  by `compare_to_paper_fullcov.chi2_with_cov` (ndf = `n_keep` = 205).
- **regenA3's ladder.py** re-read those units for every K (0 node-h).

**The 2D OmniFold central value.** E_R's estimator is `2d-unfolding/re2/re2_driver.py` with E_R's argv (`ref_c2c1/config.json` `e_r.argv`:
`--iters 5 --use-weights --estimator lgbm --seed 42 --branch-select all --bkg-mode negweight-refined
--refine-n-estimators 400 --refine-num-leaves 31`, 64 threads). On the paper's edges it is Tier 1's unit `er`:
D_ER = 2.121436 (`tier1/score.out`; `c2c1-der` = 2.12).

**The smallest rerun with the convention as a flag.** One driver option, `--signal-convention {production,minerva}`,
defaults to `production`. It is a patch to `re2_driver.py` at M, on top of Tier 1's edge patch. `ref_c2c1.py` is
unchanged, and the deploy config adds the option to E_R's argv and re-pins the driver.
- **Off (default):** every line runs as now. A test requires the output to be byte-identical to the unpatched driver's
  on the fixture omnifile.
- **`minerva`:**
  1. Background (`fill_bkg_reco_2d`, `:263`). Rows with `bkg_nuPDG == 14 && bkg_current == 1` (the truth signal
     definition, as `truth::IsNeutrino`, `truth::IsCC`) are left out of the histogram and the negweight injection.
     The rest is unchanged.
  2. Signal (`collect_signal_arrays_2d`, `:673`). Those rows are appended with:
     - reco (p_T, p∥) and `pass_reco` = `sim_background_pass` and the reco rectangle;
     - true (p_T, p∥) from route A's join or route B's branches;
     - `pass_truth` = the true rectangle only, with no θ_μ cut, because MINERvA's numerator has no phase-space cut;
     - `w_truth` = `w_reco` = `w_bkg` × the POT scale, the same weight the background used.
  3. **Moved rows with a true muon outside the grid stay in the background.** The grid has no true overflow bin. This
     is a declared choice, the exploratory replay's "all in-grid true muons".
  4. The truth denominator (`mc_truth_denom`), the data and the flux are untouched.
     - The completeness `hOFInputTruth / hOFTruthDenom` (`compute_omnifold_completeness_2d`) then exceeds 1 where
       rows feed in.
     - The extraction divides by it. That is the OmniFold counterpart of MINERvA's ε = numerator / denominator.
- **c2** inherits the same change through the seam: IBU's T, M and y are built from the driver's arrays.
- **Coordination:** `ref_c2c1.py`'s seam is used as it stands; limitation-resolver is told, but no time is asked of
  that lane.

### 1.4 What the exploratory numbers are (a re-read of committed output)

`precharge-20261125/ibu-convention/replay.txt` (branch `0a6e3f4e`) varies two things. One is the reclassification
(R). The other is the efficiency numerator's scope (N): `in_grid` counts selected events reconstructed in the grid,
and `anywhere` counts every selected event wherever it is reconstructed.

| replay row | χ²/205 | true 40–60 column ratio |
|---|---:|---:|
| unchanged, in_grid (the baseline) | 0.4736 | 1.1307 |
| unchanged, anywhere (N only) | 0.2939 | 1.0561 |
| all in-grid true muons, in_grid (R only) | 0.3493 | 1.0937 |
| all in-grid true muons, anywhere (R and N) | 0.3727 | 1.0257 |
| true 40–60 only, anywhere | 0.2748 | 1.0269 |

**The reference distance differs too.** This replay's IBU subtracts a binned background and its baseline is 0.4736.
The note's c2 subtracts E_R's refined per-event background, and Tier 1 has it at 0.5381. The two baselines are
different machinery.

**Where the motivating figures come from.**
- **The "+13.1% → about +2.7%" and "0.27–0.29":** these come from `anywhere` rows.
- **The reclassification alone,** at the production numerator scope, gives 0.3493 and +9.4% in this partial replay.
- **N alone** gives 0.2939.

This file reads no cause into this. It records which change each printed number belongs to.

## 2. Draft declaration

### 2.1 Primary (the director's question): R in both estimators

| unit | driver | convention | edges | role |
|---|---|---|---|---|
| `er_off` | E_R's argv | production | paper's | C-BASE: equals Tier 1's `er` |
| `c2_off` | E_R's argv, IBU seam | production | paper's | C-BASE: equals Tier 1's `c2_central` |
| `er_R` | E_R's argv | minerva | paper's | operand (b) |
| `c2_R` | E_R's argv, IBU seam | minerva | paper's | operand (a), K scan 1–20 as REF-C2C1 |

- **N is not in the primary.** In c2, N would mean treating selected rows reconstructed outside the grid as
  efficiency-counted. That needs a reco overflow bin in M and in y, which the driver's data arrays do not carry.
- **OmniFold has no N counterpart** without extending its reco support. N is listed in §2.6 for the director to rule
  on; it is not part of what this draft binds.

### 2.2 Controls (each a STOP, before any operand is read)

- **C-JOIN** (route A) or **C-EVL** (route B), as in §1.2.
- **C-BASE:** `er_off` and `c2_off` reproduce Tier 1's E units. hXSec2D must match to ≤ 1e-8 relative (Tier 1's
  C-REF-OLD was 7.9e-12). D_ER must equal 2.121436 and D_IBU(K) must equal regenA3's set `e` at every K, each to
  ≤ 1e-6 relative.
- **C-MOVE:** the weight removed from the background equals the weight added to the selected signal, per reco cell, to
  ≤ 1e-12 relative. Total selected MC per reco cell is unchanged. In the oflow categories, every moved row is FAKE_VTX
  or FAKE_PS, and no OTHER row moves.
- **C-FIX:** under `minerva`, `hOFTruthDenom2D`, the data histogram and the flux bins are bit-for-bit those of `off`.
- **C-SIM:** REF-C2C1's C-SIM, rerun under `minerva`. IBU on the MC's own folded truth returns the truth
  denominator's cross section through the full chain, to 1e-9.
- **C-PINS:** the inputs (43f8cc16…, d40aea69…), the library (0b34e1e3…), the driver and the runner each match their
  pins before and after.

### 2.3 Operands

- **D_X^0 and D_X^R:** χ²/205 of X ∈ {IBU K = 10, E_R} against the published result under the published
  TotalCovariance, on the paper's edges. The ratio is r_X = D_X^R / D_X^0.
- **Descriptive only:** D_IBU at every K; the true 40–60 column ratio (ours / published, area-weighted as in the
  replay) for both estimators; the completeness where it exceeds 1.

### 2.4 Readings, fixed before any number

For each estimator X separately:
- **LOWER:** r_X ≤ 0.80.
- **HIGHER:** r_X ≥ 1.25.
- **LITTLE CHANGE:** 0.95 ≤ r_X ≤ 1/0.95.
- **INTERMEDIATE:** otherwise.

What each joint outcome means. None names a cause, and none says the analysis is or is not "MINERvA-like".

| IBU | E_R | the statement the result supports |
|---|---|---|
| LOWER | LOWER | Under MINERvA's counting convention, both central values are closer to the published result by this metric |
| LOWER | LITTLE CHANGE or INTERMEDIATE | The convention moves the binned IBU's distance; at this scale it does not move the OmniFold central value's |
| LITTLE CHANGE | any | At this scale the binned IBU's distance does not depend on the convention; the exploratory replay's direction is not reproduced on the note's c2 |
| HIGHER (either) | any | The convention increases that distance |

Descriptive, read by no rule:
- whether D_IBU^R moves in the partial replay's direction (down);
- whether the IBU true 40–60 column ratio falls within ±5% of 1.

**What no reading licenses:**
- naming the cause of E_R's remaining distance;
- changing this analysis's production convention, the background template, or any printed number;
- any claim of parity with MINERvA's production.

Adopting a convention, and any wording in the note, are Joseph's.

### 2.5 Price (question 3), against the stated balance of 488 node-h

| step | where | expected | cap | basis |
|---|---|---:|---:|---|
| 0: code, tests, mutants, two reads | laptop | 0 | 0 | |
| 1A: AnaTuple pass, 12 MC playlists, one-core shared array | CPU | about 0.1 | 0.4 | Test C's 12-playlist reco and truth array charged 0.0142 node-h with the 20 GeV skip (`precharge-20261125/testC/sacct.txt`); the full p∥ range is assumed at most 10× that; cap 12 tasks × 2 h × 2/128 |
| 1B (fallback, only if C-JOIN fails): event loop, 12 playlists, plus `hadd` | CPU shared | about 0.8 | 1.5 | `ibuchi_evl` 61885471: 25.8 task-h at 16 GB, about 0.81 node-h, longest task 5:02 (`ibu-chi2-20261123/evloop/results/run_record.txt`) |
| 2: four driver units on one node | CPU | about 0.18 | 0.5 | Tier 1's four units, 10:33 on one node |
| 3: scoring | laptop | 0 | 0 | as regenA3 |

- **Expected:** about 0.3 node-h by route A, about 1.0 if route B is needed.
- **Cap:** 2.0 node-h in all, about 0.4% of the balance.
- **Wall time:** step 1A takes under an hour once queued; 1B's longest task took 5 h; step 2 takes 11 minutes.

### 2.6 For the director to rule on

1. **Route A** with B as the declared fallback, as above, or B outright.
2. **N.** Include an IBU-only N variant, or leave N out. In c2 it is a reco overflow bin in M and y, which needs data
   outside the grid. It is not in this draft's price.
3. **Moved rows with true muons outside the grid** stay in the background (§1.3 step 3), or go elsewhere.
4. **The reader set** (codex-school and claude-personal Sonnet, as for EVW5D) and the scope rule after r3.
