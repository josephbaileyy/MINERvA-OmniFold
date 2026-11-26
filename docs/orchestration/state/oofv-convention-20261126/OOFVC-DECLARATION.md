# OOFVC: the 2D central values under MINERvA's counting convention. Inventory and declaration (nothing run)
<!-- absence-ok: the lane's own status (no job of this study has run), not a claim that a result does not exist -->

**By** the `ibu-chi-squared-issue` session for the director, on Joseph's request of 2026-11-26.
- **Revision 2.** It takes in the director's rulings on the draft's §2.6 (fdcf7b8b): route A with B as the fallback; N
  added as an IBU-only secondary; out-of-grid rows kept in the background as an approximation; the readers and the
  scope rule. What changed is listed in §3.
- Nothing has run, and nothing has touched NERSC. No number in this file comes from a new computation. Every value
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
       θ_μ, the vertex, and the MnvTune v1 weight twice:
       - in reco mode, as the background loop computes `w_bkg` (`:1440-1445`);
       - in truth mode, as the signal loop computes `w_truth` (`:1131-1132`, true p_T and p∥ at `:1138-1139`).
    6. It also writes every selected ν_μ CC row inside the phase space. This is for the control C-SIGW (§2.2), not as
       an operand.
  - The model is the same five reweighters as production (`measure.cpp:34-39` = `runEventLoopOmniFold.cpp:1745-1750`).
  - Its rows are joined to 43f8cc16's `mc_background` rows on the exact triple (reco p_T, reco p∥, `w_bkg`).
  - **C-JOIN (the director's ruling 1):**
    - The join is one-to-one on the exact key. Every ν_μ CC background row of 43f8cc16 (labelled through C-SAME)
      matches exactly one dump row, and every dump row that fails the phase space matches exactly one such background
      row.
    - Any tie (a key shared by two rows on either side) or any unmatched row is a STOP.
    - After a STOP, route B comes back to the director, priced, before it runs. The fallback is declared here, not
      chosen after the fact.
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
defaults to `production`. Under `minerva` it requires `--oofvc-rows <npz>`, the join's output. It is a patch to
`re2_driver.py` at M, on top of Tier 1's edge patch. `ref_c2c1.py` is unchanged, and the deploy config adds the
option to E_R's argv and re-pins the driver.
- **The join's output** is one row per moved event:
  - its `mc_background` entry index;
  - its true p_T and p∥;
  - its truth-mode weight, before the POT scale.
  Only rows whose true muon is in the grid are included (step 3).
- **Off (default):** every line runs as now. A test requires the output to be byte-identical to the unpatched driver's
  on the fixture omnifile.
- **`minerva`:**
  1. Background (`fill_bkg_reco_2d`, `:263`). The listed entries are left out of the histogram and the negweight
     injection. The rest is unchanged. The list is exactly the ν_μ CC rows (`bkg_nuPDG == 14 && bkg_current == 1`, the
     truth signal definition as `truth::IsNeutrino`, `truth::IsCC`) whose true muon is in the grid.
  2. Signal (`collect_signal_arrays_2d`, `:673`). Those rows are appended with:
     - reco (p_T, p∥) and `pass_reco` = `sim_background_pass` and the reco rectangle;
     - true (p_T, p∥) from route A's join or route B's branches;
     - `pass_truth` = the true rectangle only, with no θ_μ cut, because MINERvA's numerator has no phase-space cut;
     - weights as the signal loop sets them for its own rows: `w_reco` = `w_bkg` (reco mode, which is also the join
       key) and `w_truth` = the truth-mode weight from the dump, each × the POT scale.
  3. **Moved rows with a true muon outside the grid stay in the background** (the director's ruling 3).
     - This is an approximation to MINERvA's truth-overflow handling. MINERvA's loop fills those events into the
       numerator's and the migration's truth overflow. This grid has no true overflow bin.
     - The weighted size of the class is reported: its sum of `w_bkg` × POT scale in the reco grid, split
       out-of-fiducial / fiducial.
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

**Where the motivating figures come from** (as re-read from `replay.txt`; distance χ²/205, then the true 40–60
column's excess over the published result):
- **The motivating "+13.1% → about +2.7%" and "0.27–0.29"** are `anywhere` rows.
- **N alone:** 0.294, +5.6%.
- **Reclassification alone,** at the production numerator scope: 0.349, +9.4%.
- **Both:** 0.373, +2.6%.

**The replay and c2 handle the background differently.** The replay subtracts a binned background. c2 uses E_R's
refined per-event background.

This file reads no cause into any of this. It records which change each printed number belongs to.

## 2. Declaration

### 2.1 Units and the two conventions

R is the reclassification of §1.3. N is the efficiency numerator's scope: selected events count in the numerator
wherever they reconstruct. N is applied to IBU only.

| unit | driver | R | edges | operands it yields |
|---|---|---|---|---|
| `er_off` | E_R's argv | off | paper's | D_ER^0 (C-BASE: equals Tier 1's `er`) |
| `c2_off` | E_R's argv, IBU seam | off | paper's | D_IBU^0 (C-BASE: equals Tier 1's `c2_central`), and D_IBU^N |
| `er_R` | E_R's argv | on | paper's | D_ER^R, primary (b) |
| `c2_R` | E_R's argv, IBU seam | on | paper's | D_IBU^R, primary (a), and D_IBU^RN; K scan 1–20 as REF-C2C1 |

**N in the IBU path (the director's ruling 2).** It needs no reco overflow bin in M or in the measured histogram.
- REF-C2C1's unfolder updates u ← u · Rᵀ(y / R u) / ε with R = M / T and ε_j = Σ_i M_ij / T_j (`ref_c2c1.py:262-275`).
  By induction on the iterations, its K-th result is u_K = s_K / ε, where s_K is IBU "to selected events": prior
  Σ_i M_ij, response M_ij / Σ_i M_ij, as `compare.py`'s `unfold_selected`.
- N replaces ε_j by ε^N_j = (Σ_i M_ij + O_j) / T_j. O_j is the reco-mode weight of the selected rows (`sim_pass`)
  whose true muon is in cell j and whose reco lies outside the grid. So u^N_K = u_K · Σ_i M_ij / (Σ_i M_ij + O_j),
  per truth bin, at every K. Where Σ_i M_ij = 0 the factor is 1.
- **This is exactly the replay's construction** (`compare.py:128-129`: unfolded selected counts divided by numerator /
  generated). The out-of-grid selected events are counted as efficient. They are not unfolded, and the data outside
  the grid are not used. A unit test checks the identity numerically against `unfold_selected` on random problems.
- **Code.** The driver (at M) adds one key, `selected`, to `collect_signal_arrays_2d`'s returned dict: the row's
  `sim_pass`, for every kept row. No current consumer reads it, and the flag-off byte-identity test covers it.
- **The lane's runner `oofvc_run.py`:**
  - captures that dict;
  - forms O_j;
  - passes REF-C2C1's runner (unchanged) its own unfolder, which records u_K and u^N_K. The driver's fill and
    extraction use u_K, as now;
  - re-extracts u^N_K by the recorded extraction (`ref_c2c1.xsec_at_every_k`'s method).
  So c2_off and c2_R each give both D^· and D^·N from one driver run.
- **N's price is 0 node-h.**

**OmniFold has no counterpart to N.** Its efficiency is implicit in the misses and the completeness. Counting
out-of-grid selected events as efficient would need reco support outside the grid. **So E_R's N cell is "not
applicable", not "no change".**

### 2.2 Controls (each a STOP, before any operand is read)

- **C-JOIN** (route A), as in §1.2: one-to-one on the exact key (reco p_T, reco p∥, `w_bkg`). Any tie or unmatched row
  is a STOP, and route B then goes back to the director priced. **C-EVL** applies under route B.
- **C-SIGW** (route A). The dump's in-phase-space ν_μ CC rows join one-to-one with 43f8cc16's selected
  `mc_signal_reco` rows on (`sim`, `sim_pz`, `w_reco`). On every joined row, (`MC`, `MC_pz`, `w_truth`) are
  bit-for-bit equal. This shows the dump's truth-mode weight and true kinematics are the signal loop's, on the
  population where a reference exists.
- **C-LAB:** the dump's ν_μ CC / non-ν_μ CC split of the joined background rows equals the 5D bkgaware file's labels
  (C-SAME alignment) on every row.
- **C-BASE:** `er_off` and `c2_off` reproduce Tier 1's E units:
  - hXSec2D to ≤ 1e-8 relative (Tier 1's C-REF-OLD was 7.9e-12);
  - D_ER to 2.121436 and D_IBU(K) to regenA3's set `e` at every K, each to ≤ 1e-6 relative.
- **C-MOVE:**
  - The weight removed from the background equals the weight added to the selected signal, per reco cell, to
    ≤ 1e-12 relative, and total selected MC per reco cell is unchanged.
  - Every moved row is oflow FAKE_VTX or FAKE_PS, and no OTHER row moves.
- **C-FIX:** under R, `hOFTruthDenom2D`, the data histogram and the flux bins are bit-for-bit those of `off`.
- **C-SIM:** REF-C2C1's C-SIM, rerun under R. IBU on the MC's own folded truth returns the truth denominator's cross
  section through the full chain, to 1e-9.
- **C-NID:** with O set to zero, u^N_K equals u_K bit for bit, in both c2 units.
- **C-NSUM:** Σ_j O_j equals the reco-mode weight of the selected, truth-in-grid, reco-outside rows counted directly
  from the captured dict, to ≤ 1e-12 relative.
- **C-PINS:** the inputs (43f8cc16…, d40aea69…), the library (0b34e1e3…), the driver, the runner and the dump each
  match their pins before and after.

### 2.3 Operands

- **Primary:**
  - D_IBU^0 and D_IBU^R at K = 10;
  - D_ER^0 and D_ER^R.
  Each is χ²/205 against the published result under the published TotalCovariance, on the paper's edges, by
  `compare_to_paper_fullcov.chi2_with_cov`.
- **Secondary (IBU only):** D_IBU^N and D_IBU^RN at K = 10.
- **Ratios:**
  - r_X = D_X^R / D_X^0 for X ∈ {IBU, E_R};
  - r_N = D_IBU^N / D_IBU^0;
  - r_RN = D_IBU^RN / D_IBU^0.
- **Reported, read by no rule:**
  - every D at every K;
  - the true 40–60 column ratio (ours / published, area-weighted as in the replay) for each unit and N variant;
  - the completeness where it exceeds 1;
  - the weighted size of the moved class and of the out-of-grid class kept in the background (ruling 3), each split
    out-of-fiducial / fiducial.

### 2.4 Readings, fixed before any number

For each ratio r separately:
- **LOWER:** r ≤ 0.80.
- **HIGHER:** r ≥ 1.25.
- **LITTLE CHANGE:** 0.95 ≤ r ≤ 1/0.95.
- **INTERMEDIATE:** otherwise.

None names a cause, and none says the analysis is or is not "MINERvA-like".

**Primary (R):**

| IBU (r_IBU) | E_R (r_ER) | the statement the result supports |
|---|---|---|
| LOWER | LOWER | Under MINERvA's reclassification, both central values are closer to the published result by this metric |
| LOWER | LITTLE CHANGE or INTERMEDIATE | The reclassification moves the binned IBU's distance; at this scale it does not move the OmniFold central value's |
| LITTLE CHANGE | any | At this scale the binned IBU's distance does not depend on the reclassification |
| HIGHER (either) | any | The reclassification increases that distance |

**Secondary (N, IBU only):**

| r_N | r_RN | the statement the result supports |
|---|---|---|
| LOWER | any | Counting selected events in the efficiency numerator wherever they reconstruct moves the binned IBU's distance down |
| LITTLE CHANGE | any | At this scale the binned IBU's distance does not depend on the numerator's scope |
| HIGHER | any | The numerator's scope increases the distance |

- r_RN is read with the same bands and reported beside r_N.
- **E_R under N: not applicable.** There is no OmniFold counterpart (§2.1).

**Descriptive, read by no rule:**
- whether D_IBU^R, D_IBU^N and D_IBU^RN move in the partial replay's directions;
- whether the IBU true 40–60 column ratio falls within ±5% of 1 under each.

**What no reading licenses:**
- naming the cause of E_R's remaining distance;
- changing this analysis's production convention, the background template, or any printed number;
- any claim of parity with MINERvA's production.

Adopting a convention, and any wording in the note, are Joseph's.

### 2.5 Price, against the stated balance of 488 node-h

| step | where | expected | cap | basis |
|---|---|---:|---:|---|
| 0: code, tests, mutants, reads | laptop | 0 | 0 | |
| 1A: AnaTuple dump, 12 MC playlists, one-core shared array | CPU | about 0.1 | 0.4 | Test C's 12-playlist reco and truth array charged 0.0142 node-h with the 20 GeV skip (`precharge-20261125/testC/sacct.txt`); the full p∥ range is assumed at most 10× that; cap 12 tasks × 2 h × 2/128 |
| 1B (fallback, only after a C-JOIN STOP and the director's ruling): event loop, 12 playlists, plus `hadd` | CPU shared | about 0.8 | 1.5 | `ibuchi_evl` 61885471: 25.8 task-h at 16 GB, about 0.81 node-h, longest task 5:02 (`ibu-chi2-20261123/evloop/results/run_record.txt`) |
| 2: the join, its controls, then four driver units on one node | CPU | about 0.18 | 0.5 | Tier 1's four units, 10:33 on one node; the join reads two trees of 43f8cc16 |
| N | inside step 2's c2 units | 0 | 0 | a per-bin factor and a re-extraction |
| 3: scoring | laptop | 0 | 0 | as regenA3 |

- **Expected:** about 0.3 node-h by route A, about 1.0 if route B is needed.
- **Cap:** 2.0 node-h in all, N included, about 0.4% of the balance.
- **Wall time:** step 1A takes under an hour once queued; 1B's longest task took 5 h; step 2 takes about 11 minutes.

### 2.6 Rulings (the director, 2026-11-26) and reads

1. Route A, with B as the declared fallback. C-JOIN is one-to-one on the exact key. Any tie or unmatched row is a
   STOP. If A STOPs, B comes back priced before it runs.
2. The IBU-only N variant is a declared secondary. Its readings use the same bands. E_R's N cell is "not applicable".
3. Rows whose true muon falls outside the grid stay in the background, declared as an approximation, with the class's
   weighted size reported.
4. **Readers:**
   - one codex read of the declaration and the code, on codex-school (`gpt-6.2-sol`, high). The director amended
     this at Joseph's word, 2026-11-26: no waiting for codex-school2. The account is shared, with about 16% weekly
     left, so `openusage` runs before each read and each read's token count is reported;
   - one agy `gemini-4-hydrogen-high` read of the code.
   - **The last round is r3.** After it, a finding blocks only if it could change a printed number or a gate's
     acceptance, or cause a false STOP of a correct run.
   - Each runner's sha goes to the director before any NERSC step, and a fence round goes to the peers.

## 3. Revisions

- **Revision 1** (fdcf7b8b): the inventory and the draft, sent for rulings.
- **Revision 2** (this file):
  - the rulings of §2.6;
  - N defined, by the identity of §2.1, with its controls C-NID and C-NSUM;
  - C-SIGW and C-LAB added;
  - the moved rows' weights set as the signal loop sets its own;
  - the join's output defined;
  - the motivating replay figures named as re-read;
  - the file renamed from `OOFVC-DECLARATION-DRAFT.md`.
