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
  - **The program** is `2d-unfolding/oofvc/oofvc_dump.cpp`, one MC playlist per task. It is built in Test C's
    environment (`precharge-20261125/testC/build.sh`). It mirrors the 2D event loop's setup (`:1695-1750`): the same
    MinervaUniverse settings, the same Cutter (production reco cuts, signal definition and phase space, including
    `MaxPzMu` and `MaxPtMu`), and MnvTune v1 as the Model.
  - **Its rows:** every reco-tree entry the event loop selects (`isMCSelected`), with:
    - both routings:
      - the background loop's, `!(isSignal && isEfficiencyDenom)` in reco mode (`:1453-1456`);
      - the signal loop's, in truth mode (`:1134-1135`);
    - the signal loop's key-duplicate flag (`:1201-1218`);
    - the event key (`mc_run`, `mc_subrun`, `mc_nthEvtInFile`);
    - reco p_T and p∥ and the reco-mode weight, as the background loop computes `w_bkg` (`:1440-1445`) and the
      signal loop `w_reco`;
    - true p_T, p∥ and θ_μ and the truth-mode weight, as the signal loop computes `w_truth` (`:1131-1139`);
    - the neutrino PDG, the current, the true vertex, and MAT's vertex flag.
  - **One departure, for time.** `isMCSelected` is evaluated with weight 1, since the weight enters only the Cutter's
    statistics, and the weights are computed for selected entries only.
    - The duplicate flag is taken first, in the signal loop's order: the first occurrence of a key among all
      phase-space entries, selected or not, is kept.
    - C-JOIN and C-SIGW compare every weight bit for bit with the production trees, so any effect of the order is a
      STOP, not a result.
  - **The model** is the same five reweighters as production (`runEventLoopOmniFold.cpp:1745-1750`).
  - **The join** is `2d-unfolding/oofvc/oofvc_join.py`, with C-ROUTE, C-JOIN, C-SIGW and C-LAB (§2.2). Its output is
    the driver's `--oofvc-rows` file and a record of the class sizes.
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
  - its reco and true p_T and p∥;
  - its reco-mode weight (`w_bkg`) and its truth-mode weight, both before the POT scale.
  Only rows whose true muon is in the grid are included (step 3). Rows reconstructed in the grid and outside it are
  both listed.
- **Off (default):** every line runs as now. A test requires every histogram, parameter and record of the output to be
  bit-for-bit the unpatched driver's on the fixture omnifile. The exceptions are:
  - the run's paths (the driver, its helper and the output, which differ because the two test runs sit in different
    trees);
  - the driver's digest;
  - `runConfig`'s record of the two new options at their defaults (`signal_convention` "production", `oofvc_rows`
    null).
- **`minerva`:**
  1. Background (`fill_bkg_reco_2d`, `:263`). The listed entries are left out of the histogram and the negweight
     injection. The rest is unchanged. The list is exactly the ν_μ CC rows (`bkg_nuPDG == 14 && bkg_current == 1`, the
     truth signal definition as `truth::IsNeutrino`, `truth::IsCC`) whose true muon is in a cell of the grid.
     - **"In the grid" means in one of ROOT's cells** throughout this section: lower edges in, upper edges out (the
       last edge is overflow). That is how the binned M, T, O and the histograms place a value, so no row on an
       upper edge falls between the populations (codex-school r1 #3).
  2. Signal (`collect_signal_arrays_2d`, `:673`). The listed rows whose reco is in the grid are appended.
     - **Rows reconstructed outside the grid are not appended.** Under MINERvA's in-grid numerator they appear in
       neither the numerator nor the denominator. For IBU the choice cannot matter: the result is
       s_K · denominator / Σ_i M_ij, and T cancels (§2.1). For E_R, appending them as misses would add rows that
       MINERvA's construction does not have.
     - Under N they enter O_j (§2.1).
     Each appended row carries:
     - reco (p_T, p∥), with `pass_reco` true;
     - true (p_T, p∥) from route A's join or route B's branches;
     - `pass_truth` = the true rectangle only, with no θ_μ cut, because MINERvA's numerator has no phase-space cut;
     - weights as the signal loop sets them for its own rows: `w_reco` = `w_bkg` (reco mode, which is also the join
       key) and `w_truth` = the truth-mode weight from the dump, each × the POT scale.
     - **The loaders' own weight rules apply** (codex-school r1 #8).
       - An appended row needs the signal loader's 0 ≤ w < 1e4 on both weights.
       - A row reconstructed outside the grid needs the background loader's 0 ≤ w_reco < 1e6.
       - A row failing its rule is dropped and counted, as those loaders drop theirs, and the counts are recorded.
       A non-finite `w_truth` fails the signal rule. It is allowed in the rows file, because a row reconstructed
       outside the grid never uses it; every other column must be finite.
       - The option also requires `--use-weights`.
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
- **T cancels.** The driver's extraction then divides by the completeness c_j = T_j / D_j. D is
  `hOFTruthDenom2D`, and T is the same w_truth sum over `pass_truth` rows that the IBU's prior uses. So the IBU's
  cross section is s_K · D / Σ_i M_ij: MINERvA's "unfolded selected / (numerator / denominator)" with the in-grid
  numerator. T does not enter. REF-C2C1's C-SIM relies on the same consistency.
- N replaces ε_j by ε^N_j = (Σ_i M_ij + O_j) / T_j. O_j is the reco-mode weight × POT scale of the selected rows whose
  true muon is in cell j and whose reco lies outside the grid. There are two sources:
  - signal-tree rows with `sim_pass` whose reco has no cell (outside the grid, or on its upper edge, where M also
    puts it in the overflow);
  - under R, the moved rows reconstructed outside the grid. These are taken from the join output, because they are
    not appended (§1.3 step 2).
- So u^N_K = u_K · Σ_i M_ij / (Σ_i M_ij + O_j), per truth bin, at every K. Where Σ_i M_ij = 0 the factor is 1.
- **This is exactly the replay's construction** (`compare.py:128-129`: unfolded selected counts divided by numerator /
  generated). The out-of-grid selected events are counted as efficient. They are not unfolded, and the data outside
  the grid are not used. A unit test checks the identity numerically against `unfold_selected` on random problems.
- **Code.** The driver's signal loader (at M) returns one extra key, `selected` (each kept row's `sim_pass`), but only
  when called with `record_selected=True` or with moved rows. The production call passes neither.
- **The lane's runner, `oofvc_run.py`:**
  - wraps the loader to pass `record_selected=True` and keep its dict;
  - forms O_j;
  - lets REF-C2C1's `run_unit` (unchanged) run the unit. Its unfolder is RooUnfoldBayes, so C-ROO runs, and the driver's
    fill and extraction use u_K, as now;
  - keeps the unit's capture (M, T, the trajectory and the recorded extraction);
  - re-extracts u^N_K by `ref_c2c1.xsec_at_every_k`'s method.
  So c2_off and c2_R each give both D^· and D^·N from one driver run.
- **N's price is 0 node-h.**

**OmniFold has no counterpart to N.** Its efficiency is implicit in the misses and the completeness. Counting
out-of-grid selected events as efficient would need reco support outside the grid. **So E_R's N cell is "not
applicable", not "no change".**

### 2.2 Controls (each a STOP, before any operand is read)

- **C-ROUTE:** every dump row is routed to exactly one tree. The reco-mode routing (the background loop's) and the
  truth-mode routing (the signal loop's) agree on every row.
- **C-JOIN** (route A, `oofvc_lib.exact_join`): every `mc_background` entry of 43f8cc16 joins one-to-one with the
  dump's background-routed rows on the exact key (reco p_T, reco p∥, `w_bkg`), compared as float64 bit patterns.
  Ties follow the director's ruling of 2026-11-26:
  - A tie is allowed only when every row in the group carries the same dump event key (playlist, `mc_run`,
    `mc_subrun`, `mc_nthEvtInFile`) and bit-identical values, with equal counts on both sides. That is one event
    filled twice; all its background rows move, as production keeps them.
  - Any other tie, any count mismatch, or any unmatched row is a STOP.
  - So is a group of more than 2 copies, or tied groups weighing more than 0.1% of the moved weight.
  - The group count and weight are recorded.
  - After a STOP, route B comes back to the director priced. **C-EVL** applies under route B.
- **C-SIGW:** the selected `mc_signal_reco` rows (`sim_pass`) join one-to-one with the dump's signal-routed rows that
  the signal loop keeps, on (`sim`, `sim_pz`, `w_reco`). The same tie rule and bound apply, the bound relative to the
  joined weight. The kept rows exclude the key duplicates the signal loop drops (`:1201-1218`). The dump flags them
  as the signal loop does: the first occurrence among all phase-space entries, in entry order, before the selection.
  On every pair, (`MC`, `MC_pz`, `w_truth`) are bit-for-bit equal to the dump's. This shows the dump's truth-mode
  weight and true kinematics are the signal loop's, on the population where a reference exists.
  - **The truth-tree gate.** The signal loop also requires each key to be in the truth tree's denominator (`:1201-1212`).
    The dump does not re-evaluate that gate. Stage B's P4 census measured nG1 = 0 and nSigLoopNoTruth = 0 on this
    omnifile's per-playlist inputs, which are E_U's and E_R's (`2d-closeout/stageB/diagnostics/REPORT.md:45-62`). So
    the gate drops nothing here. The code comment's "~1.8%" predates that measurement, as Stage B records. Were the
    gate to drop a row, C-SIGW would STOP: an honest refusal, not a wrong result (agy r1 #1, codex-school r1 #1).
- **C-LAB:** the joined background's oflow categories (FAKE_PS, FAKE_VTX, OTHER), on the OLD 14×16 reco grid and
  POT-scaled, equal `oflow/split.json` cell by cell (relative 1e-9; absolute 1e-9 where split.json has 0), with equal
  counts. They are computed with oflow's own fiducial formula (`oflow/remote3.sh`) from the dump's true vertex and
  labels, so the check compares like with like. This replaces the 5D-file comparison of revision 2: the dump carries
  the labels, and split.json is their committed record. A non-finite cell on either side is a STOP.
- **C-BASE:** `er_off` and `c2_off` reproduce Tier 1's committed E units (`tier1/units/e/`):
  - hXSec2D, and c2's cross sections at every K, to ≤ 1e-8 relative (Tier 1's C-REF-OLD was 7.9e-12), with
    exact zeros wherever Tier 1's are zero, and the same K list;
  - D_ER to 2.121436 and D_IBU(K) to regenA3's set `e` at every K, each to ≤ 1e-6 relative.
- **C-MOVE:**
  - Per reco cell, the background removed (off minus R) equals the moved rows reconstructed in the grid that the
    background loader had filled (0 ≤ w < 1e6), POT-scaled.
    The tolerance is 1e-12 of that cell's production background, because the difference of two sums cancels.
  - R's signal arrays grow by exactly the number the driver reports appending, which is the moved rows with a reco
    cell less those its weight rule drops.
  - By construction (`oofvc_lib.moved_mask`), every moved row is ν_μ CC, so FAKE_VTX or FAKE_PS, and no OTHER row
    moves.
- **C-FIX:** under R, `hOFTruthDenom2D`, `hDataReco2D` and `hFlux_pt` (contents, errors and axis edges, overflow
  included), and the exposure, both flux integrals and the nucleon parameters, are bit-for-bit those of `off`. This
  holds for the E_R pair and the c2 pair alike.
- **C-SIM:** REF-C2C1's C-SIM, rerun under R. IBU on the MC's own folded truth returns the truth denominator's cross
  section through the full chain, to 1e-9. **C-ROO** and **C-FILL** run as in REF-C2C1. The scorer refuses a c2
  unit without C-ROO, so no numpy-unfolder test run can stand in.
- **C-NID:** with O set to zero, u^N_K equals u_K bit for bit, in both c2 units.
- **C-NSUM:** Σ_j (Σ_i M_ij + O_j) equals the reco-mode weight of the selected, truth-in-grid rows counted directly from
  the signal loader's rows, plus the moved part recomputed from the rows file (not the driver's), to ≤ 1e-12
  relative.
- **C-NMOVED:** under R, the driver's moved part of O equals, cell by cell, the one recomputed from the join's rows
  file (codex-school r1 #5).
- **C-PINS:** each unit process records the inputs (43f8cc16…, d40aea69…), libRooUnfold.so, the driver, the runner,
  the lane's library and the rows before and after. libRooUnfold.so is checked against its pin (0b34e1e3…) inside the
  process before any unit. The scorer requires each record to be unchanged and equal to the expected digests:
  - driver 9d11bd4b…, runner 285dd138…;
  - the lane's files as the tool commit has them (`git show`, not the scorer's checkout);
  - the join's rows, libRooUnfold.so 0b34e1e3…, and the staged inputs 43f8cc16… and d40aea69…;
  - every file each unit wrote (done-marker, npz, root, record, and `n.npz`), whose digests its own process
    recorded. The manifest must list exactly those files;
  - the join record the units ran beside (`--join-record`), whose digest each process pins and the scorer requires.
  Each condition is reported by name.
- **C-UNITS** (the scorer). Every unit's root and npz equal its done-marker's digests, and its recorded argv is its
  npz's. That argv is E_R's exactly: `--omnifile <stage>/runEventLoopOmniFold_MEFHC.root --mcfile
  <stage>/runEventLoopMC_MEFHC.root`, with <stage> the lane's staging root, then E_R's options; R adds the rows file
  `<stage>/oofvc_rows.npz`. So another seed, iteration count or file fails.
  - R units carry `--signal-convention minerva --oofvc-rows …/oofvc_rows.npz`, and off units carry neither option.
  - No unit used the numpy unfolder, and every c2 unit ran C-ROO.
  - N's controls passed (codex-school r1 #4).
- **C-KS:** every array the scorer reads has the same K list, which contains K = 10.
- **C-JOIN-RECORD** (the scorer). The join's record is PASS on exactly its four controls. Its rows digest is the
  scored rows file's, its omnifile digest is 43f8cc16…, and its split.json digest is the tool commit's.

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
| INTERMEDIATE | not HIGHER | No statement; the numbers are reported |

The rows are read in this order of precedence: a HIGHER for either estimator takes the HIGHER row, whatever the other
reads.

**Secondary (N, IBU only):**

| r_N | r_RN | the statement the result supports |
|---|---|---|
| LOWER | any | Counting selected events in the efficiency numerator wherever they reconstruct moves the binned IBU's distance down |
| LITTLE CHANGE | any | At this scale the binned IBU's distance does not depend on the numerator's scope |
| HIGHER | any | The numerator's scope increases the distance |
| INTERMEDIATE | any | No statement; the numbers are reported |

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

**The cluster steps.** The scripts are in `2d-unfolding/oofvc/launch/`. Each remote script runs from a clean clone of
this lane at the tool commit, and its sha256 is pinned in the bound launcher. `fill_pins.sh` writes `launch/bound/`
by command. Everything is written under `/pscratch/sd/j/josephrb/oofvc-20261126/`, and nothing is written to CFS. The
job names are `oofvc_dump` and `oofvc_units`, a new family, so a fence round goes out before the first submission.
1. **`dump-pilot`** (login node; it takes cov2d's LL5D atime-post, §2.7):
   - the lane root;
   - the tool clone;
   - the build;
   - one array task on 1L (shared, one core, 4 GB, `-t 01:00:00`).
2. **`dump-rest`** (login node). It runs only after the pilot is COMPLETED with `routing_disagree 0`.
   - The other eleven playlists' times are projected as the pilot's elapsed time × their MC reco entries over 1L's
     (`precharge-20261125/file-counts.txt`).
   - If any projection exceeds 1.75 h, nothing is submitted, and a resized request goes to the director.
   - Otherwise the eleven tasks go at `-t 02:00:00`.
3. **`units`** (login node, then one node). It runs only after all twelve dumps are done.
   - The CV omnifile and the flux file are staged from CFS by `dd iflag=noatime`, re-hashed against their pins, with
     the sources' atime recorded (Tier 1's form).
   - The deploy tree is built by `make_tree.sh` (clone mode), and libRooUnfold.so is checked against its pin.
   - `units.sbatch` is submitted (regular, one node, exclusive, `-t 00:45:00`). On that node:
     - the join runs first, and a STOP there runs no unit;
     - then the four units run at once, each `srun --exclusive -n1 -c 64` with E_R's thread environment.
4. **`post`** (login node): sacct, the charge, and `post.tar.gz` of the records. The staged copies and the dump ROOT
   files are hashed but not archived.
5. **`fetch`**, then scoring on the laptop (`oofvc_score.py`).

The staged copies and the dumps stay on scratch until a separate removal under its own GO.

### 2.7 Protected reads (the director's check of 2026-11-26)

`oofvc_dump.cpp` mirrors the event loop's setup, so it calls `SetNuEConstraint(true)` (`:69`). The flux reweighter
then opens the NuE constraint file plainly when it is constructed (MAT-MINERvA `weighters/FluxAndCVReweighter.h:32`,
as geanttw's declaration §6 records). The call cannot be dropped: without it the flux weights differ, and C-JOIN and
C-SIGW would STOP. OOFVC's reads were checked against cov2d's 36 protected paths
(`fd/rpd-reco/flux2-20261122/production-config.ready.json`, `cov2d_protected_paths`).

| read | protected | how it is read |
|---|---|---|
| `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt` | **yes** (cov2d's first entry) | plainly, once per dump task (12 tasks), by MAT. **The exception is REQUESTED**, as RDX's was granted and geanttw's requested |
| `/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root` (43f8cc16) | **yes** | once, by `dd iflag=noatime` into the staging root, with the source's atime recorded before and after (Tier 1's form, which had cov2d's ack) |
| the CFS flux file (d40aea69), the 12 MC manifests, the staged MINERvA101 sources, `setup_salloc_env.sh`, libRooUnfold.so, the AnaTuples | no | as §2.5 describes |
<!-- absence-ok: the protected-path check covers this lane's own reads against cov2d's committed list, not a claim that a result does not exist -->

**The conditions, as geanttw applied RDX's** (`geanttw-20261124/DECLARATION.md` §6, quoting
`fd/redump-f12i-20261112/RDX-DECLARATION.md:315-321`). The only change is the job prefix, `oofvc_`.
- **(a)** The first `oofvc_dump` job starts only after cov2d has taken the LL5D gates' atime-post.
  - `dump-pilot` takes that UTC time, as the director passes it on (the launcher's fourth argument). It refuses
    unless the time is given, well formed and already past.
  - It records the time in `gates/ll5d_atime_post.txt`, before any other write. `dump-rest` and every dump task
    require that record.
- **(b)** cov2d's atime-snapshot connects refuse while an `oofvc_` job is queued or running. That is enforced on
  cov2d's side, once the director's announcement names `oofvc_`.
- **(c)** Each dump task logs the NuE file's `atime_ns` and `mtime_ns`, with UTC, before and after its run, into
  `dump/<pl>.nue.log`. The logs go into post.tar.gz and the receipt. The task first refuses unless the file the
  environment resolves is the declared path.
- **The other binding terms** (`RDX-BINDING-1.md:148-150`):
  - every dump task checks the fence at its start and immediately before the binary;
  - each remote step checks it before each submit, and `units` also before staging;
  - the director announces `oofvc_` to the fenced lanes.
  The fence check: no live `cov2d` or `t2a` job, read from sacct, never squeue; any non-terminal or empty state
  counts as live.
- **There is no GO for step 1A** until the director's ruling and cov2d's no-objection are both on record. Both
  protected reads are named in the fence round.

Tests: `Shell` checks that the three scripts' fence functions are identical. It also exercises:
- refusal of a live, unknown-state or sacct-failed fence;
- the atime-post gate, both directions;
- the NuE path check and its order around the binary.
Mutants SH_FENCE_STATE, SH_FENCE_SACCT, SH_GATE_PAST, SH_NUE_ORDER and SH_NUE_PATH target those lines.

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
  - the file renamed from `OOFVC-DECLARATION-DRAFT.md`;
  - after 881f4dbc and before any read: moved rows reconstructed outside the grid are not appended; T's cancellation
    from the IBU result is stated; O_j's two sources are named.
- **Revision 7** (the director's check of 2026-11-26, before the pins): §2.7. The NuE read is declared, with cov2d's
  conditions (a)–(c) and the fence terms; the CV source's O_NOATIME staging is declared; and the launch scripts and
  their Shell tests and mutants are added. No number, control or reading changed.
- **Revision 6** (after r3, the last full round: codex-school 4 BLOCKERs, agy GO; `receipts/reads/r3/`):
  - exact staged paths in argv;
  - exact manifests;
  - the join record pinned by every unit process;
  - split.json at the tool commit;
  - one complete entry-count line per playlist;
  - C-BASE guarded against a mismatched K list;
  - each pin condition reported by name.
  After r3, the director's scope rule governs.
- **Revision 5** (after r2: codex-school 5 BLOCKERs, agy GO; `receipts/reads/r2/`):
  - every unit file covered by its process's recorded digests, `n.npz` included;
  - argv equal to E_R's;
  - C-FIX on the c2 pair;
  - C-MOVE counts only rows the background loader filled;
  - a non-finite `w_truth` allowed, then dropped by the signal rule;
  - pins against the tool commit and the staged inputs;
  - C-JOIN-RECORD's digests;
  - every playlist's entry count checked by name;
  - §1.2's duplicate rule corrected.
- **Revision 4** (after r1: codex-school `gpt-6.2-sol` and agy `gemini-4-hydrogen-high`, `receipts/reads/r1/`):
  - ROOT's cells in place of the closed rectangle;
  - the loaders' weight rules, with drops counted;
  - `--use-weights` required;
  - the dump's duplicate flag taken in the signal loop's order;
  - the dump's write checked;
  - C-SIGW's reliance on P4 stated;
  - O's signal part keyed on the binned reco;
  - C-NMOVED, C-UNITS and C-KS added;
  - C-NSUM made independent;
  - C-PINS checked against expected digests;
  - C-BASE's zero cells, C-FIX's edges and errors, and C-LAB's non-finite STOP;
  - zero tie weight passes the bound;
  - the batch scripts' exit statuses.
- **Revision 3** (with the code, before any read):
  - the director's tie rule and bound, from 2026-11-26, in C-JOIN and C-SIGW;
  - the dump defined as built, with its one ordering departure stated;
  - C-ROUTE added;
  - C-LAB compares the dump-derived categories with `oflow/split.json`, so no 5D file is staged;
  - C-MOVE's tolerance is stated relative to the cell's background, with the appended count;
  - the flag-off identity's exceptions named;
  - the readings tables' INTERMEDIATE rows and precedence written out;
  - C-ROO required of every c2 unit;
  - the cluster steps.
