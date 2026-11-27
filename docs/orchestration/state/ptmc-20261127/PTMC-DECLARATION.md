# PTMC DECLARATION (DRAFT r4): REF-C2C1's paired test, binned IBU against 2D OmniFold, under OOFVC's R reclassification (2026-11-27)

**Status: DRAFT r4.** It is not audited and not bound, and nothing runs from it.
- The director ruled on D1–D5 and on r2's two ruling-touching changes (§8).
- r3 answered the round-2 reads (`reads/r2/`). r4 answers round 3 (`reads/r3/`), the last declaration round, under the
  director's scope rule: only a wrong printed number or over-reaching statement, a gate that would pass a defective
  run, or a false STOP of a correct run blocks.
- The scoping, price and calendar are in `PTMC-SCOPING.md`.

**Asked for by** Joseph, through the director (2026-11-27). **Drafted by** ibu-chi-squared-issue, read-only on
origin/main `e726cb876`.

**CITABLE FOR:** the design, the controls, the readings fixed before any number, and the licences.

**NOT CITABLE FOR:** any result, cause, physics claim or note wording. The result goes to Joseph before any note text
uses it.

## 0. The question, and what is on record

**The question.** Do binned IBU and 2D OmniFold stay statistically distinguishable, by REF-C2C1's paired test, once
the MC counting convention is OOFVC's R?

**On record (production convention).**
- `OUTCOME-20261106-ref-c2c1-read.md`, readout.json `0ee21301…`. At K = 10, C2-R1 reads **differ**:
  - T_δ = 382.8, against q̂₉₅ = 123.6 and max̂ = 138.5;
  - N = 300 Q_R replicas at rank 75, on the analysis grid.
- At K = 5 it also reads differ.

**R** is OOFVC's reclassification (`OOFVC-DECLARATION.md` §1.3). It follows the counting of MINERvA's released 2021
comparison code. The rows are r3's join output, `oofvc_rows.npz` `cbf34bd8…`, with join record `13674f6d…`. On
r3's record:
- **544,162** νμ CC mc_background entries whose true muon is in the grid are skipped by the background loader;
- **536,518** of them, reconstructed in a cell of the grid, are appended to the selected signal;
- **7,644**, reconstructed outside the grid, enter neither population.

Three caveats carry over from OOFVC:
- (i) νμ CC rows whose true muon is outside the grid stay in the background, as an approximation (OOFVC ruling 3);
- (ii) parity with the publication's final production histograms is not established;
- (iii) OOFVC's IBU-only numerator variant, N, is not part of this design.

At the central value, OOFVC read r_IBU LOWER and r_ER LITTLE CHANGE. That was on Tier 1's p_T edges (0.075 / 0.325 /
0.475 GeV/c). This declaration asks a different question, on a different grid (§2.5).

**The primary answer is PTMC-R1, the R test alone.** B, REF-C2C1's own products at the same seeds, N and rank, is a
seed-matched historical benchmark. It was made with a different refinement protocol (§2.1). It gives context and does
not isolate the convention.

## 1. Operands and pins

The R operands are checked by C-IN, and any mismatch is refused. The baseline is checked by C-D4, with the
disposition of §3.3. Every pin below is recorded by every unit and by the scorer (C-PINS).

| operand | identity |
|---|---|
| CV omnifile, flux file | `43f8cc16…`, `d40aea69…` (REF-C2C1 `config.json`), staged by an O_NOATIME DTN copy |
| moved rows; join record | `oofvc_rows.npz` `cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03` (r3), staged by an O_NOATIME copy; join record `13674f6d…` (r3's `score.json`, `inputs.join_sha256`) |
| driver | M's (`77d76cfc`) `re2_driver.py` `938c53c5…`, plus `oofvc_driver.diff` `6e836e05…` (giving `3ee2172b…`), plus PTMC's hunk (§2.2). The result is pinned at the tool commit. **Tier 1's edge patch is not applied** |
| code imported unchanged | `ref_c2c1.py` `285dd138…`, `ref_c2c1_read.py` `0412401b…`, `oofvc_lib.py` `a3df5569…`. At M: `omnifold.py` `e9623412…`, `compare_to_paper_fullcov.py` `1dd5ff52…` and `uq/reported_cells.py` `2ddf7c9f…` |
| new code | PTMC's runner, library, scorer, config and build script, pinned at the tool commit |
| RooUnfold | `libRooUnfold.so` `0b34e1e3…` (REF-C2C1 config) |
| publication | `6c6dce72…`, with REF-C2C1's committed `cells.root` `f06e4a26…` (`receipts-ref-c2c1/step2/cells/`). They are used only for C-CELLS, C-PUB and the descriptive D values |
| runtime | Python, numpy, ROOT, LightGBM and scikit-learn versions, recorded by every unit; the scorer refuses a mixed set |

**On compare_to_paper_fullcov.py's pin.** `git show 77d76cfc:2d-unfolding/ref_c2c1/config.json` and the same file at
M' (`af70e9c4`, REF-C2C1's read) both pin `1dd5ff52…`, the file's bytes at M. Main's `config.json` was later re-pinned
to `7e641754…`, a later version. PTMC deploys M, so `1dd5ff52…` is the file it runs.

**The baseline products (D4).** Each is read through REF-C2C1's `Staged` (an O_NOATIME copy) under
`ref_c2c1.read_guards`. Every later read opens only the checked copy.

| product | role | binding |
|---|---|---|
| E_R central, `read-2/inputs/001_xsec.root` | **mandatory** (C-BASE, C-PUB, C-GRID) | sha256 `a5c13fc3…` |
| REF's IBU central, `units/c2_central.npz` | optional (B; C-BASE's vector half) | npz sha256 = the `sha256` field of the committed `units-centrals/c2_central.done` (`unit` = `c2_central`, `verdict` = `PASS`); the marker file's own sha256 is `929d0e78…` |
| REF's IBU replicas, `units/c2_replica_b{b}.npz`, b = 1..200 | optional (B) | npz sha256 = the `sha256` field of its committed marker (`unit` = `c2_replica_b{b}`, `verdict` = `PASS`). Main holds 300 such markers under `receipts-ref-c2c1/step2/units-replicas/`, one per unit |
| Q_R replicas, `read-2/inputs/{(b+1):03d}_xsec.root`, i.e. `002`..`201` | optional (B) | sha256 = readout.json's `staged_sha256` for `…/partb/out/S1_{b:03d}/xsec.root`. The reader staged the publication as 000, E_R as 001, then S1_001.. (`ref_c2c1_read.py:81, 233, 249, 303`) |

## 2. The design (frozen)

### 2.1 The paired unit

One in-process run of E_R's driver:
- E_R's argv (`config.json` `e_r.argv`), with `--omnifile` and `--mcfile` at the staged copies;
- on an R unit, `--signal-convention minerva --oofvc-rows <staged rows>`;
- on a replica unit, `--bootstrap-seed b --bootstrap-streams three`, and on a central neither;
- 64 CPUs, with `OMP_NUM_THREADS=64`, `MKL_NUM_THREADS=1` and `OPENBLAS_NUM_THREADS=1`;
- `--unit-factors` is refused.

**The two methods:**
- **OmniFold.** The driver's own `omnifold` call is observed, not replaced. The unit's `hXSec2D` is OmniFold's, and
  **no IBU control reads it.**
- **IBU.** Inside that call, before OmniFold runs, IBU is solved on the identical inputs:
  - REF-C2C1's `binned_problem` on the arguments OmniFold receives;
  - `roounfold_bayes` (the bound library) at K ∈ {1, 2, 3, 4, 5, 10, 15, 20}.
- **IBU's cross section.** After the driver returns, IBU's cross sections come from `xsec_at_every_k`, a separate
  extraction call with the same arguments as the driver's recorded one. Those arguments include the completeness the
  driver's own extraction consumed.

**Products.** `<unit>.root` (the driver's) and `<unit>.npz`, which holds:
- the IBU cross section and unfolded vector per K, at the top level as `ks`, `xsec` and `unfolded`;
- M, T and y;
- the digests of the arrays the OmniFold call received;
- the draw, completeness and support records of §2.2;
- argv, the environment, the runtime versions and the pins.

A done-marker records the verdict and both products' sha256.

**The pairing is tighter than REF-C2C1's, and that is better (the director's ruling D3).**
- REF-C2C1 ran its IBU replicas and E_R's Q_R replicas as separate driver runs. Each refitted the refinement on the
  same resampled input with the same `random_state`, and LightGBM is not deterministic at 64 threads.
- Here both methods consume one w̃, so δ carries no refit-to-refit noise. One driver run per replica also keeps the
  price under the cap.
- **The consequence for B (the round-2 reads).** B's products were made the separate way. The protocol difference
  between R and B is not bounded in the rank-50 metric the statistic uses: a per-cell bound cannot bound
  retained-mode errors, and five seeds do not bound the covariance or the leave-one-out bars.
  - So **no statement uses "all else held fixed"**, and B is reported with its protocol named.
  - C-PROTO (§3.2) is a printed diagnostic only.

### 2.2 The bootstrap under R (PTMC's driver hunk)

- **The refusal is lifted for one case.** The present diff refuses `--bootstrap-seed` with `minerva`. That refusal is
  lifted only for `--bootstrap-streams three` on the negweight-refined path, with `--use-weights` and without
  `--unit-factors`. Closure, universe and `--data-file` stay refused.
- **Data factors:** unchanged, Poisson(1) from `default_rng(b)` over the data rows. The data are not reclassified.
- **Original signal rows:** Poisson(1) from `default_rng(b + 10,000,000)`, over exactly the off-convention signal rows,
  in their order. The appended rows are not in that draw.
- **A moved row keeps its own draw (D2).**
  - `append_oofvc_rows` returns the mc_background entry of each row it appends, in append order. These go to the end
    of the signal arrays, which the driver only reads between the loader and the bootstrap block.
  - An appended row's factor is b_bkg[entry]: the background stream's Poisson(1) factor, from
    `default_rng(b + 20,000,000)` over every mc_background entry.
  - Every listed entry is skipped by the background fill before its fill row is recorded, so it never reaches
    `re2_injected_entries`. An appended row's factor is used once, on the signal side.
  - The 7,644 rows reconstructed outside the grid carry no factor in the active estimator.
  - The reco and truth weights of an appended row ride its factor together, as for every MC row.
- **The background stream** is unchanged over the rows that remain in the background.

**Completeness under R.** On an R replica it is resampled consistently. The production path is untouched.
- **The premise is production's own, and PTMC adds none** (KNOWN_ISSUES 84; `re2_driver.py:2432-2448` at M).
  - Production freezes a replica's completeness at c_CV. That is the consistent bootstrap only because, on a Phase-17
    input, the canonical denominator D and the original truth-passing signal rows T_orig are the same events with
    the same weights; then D*_j / T*_orig,j = D_CV,j / T_orig,CV,j.
  - Event identity cannot be verified from the loaded branches, and the driver's own truth gate omits the
    truth-vertex cuts that the event loop applies to mc_truth_denom (`re2_driver.py:66-79`).
  - So the premise is **gated, exactly**, by C-COUPLE (§3.1), in `p_off_c` and in `p_R_c`'s original rows. Per truth
    cell, the multiset of (truth p_T, truth p∥, w_truth) over the canonical denominator's rows must equal the multiset
    over the original truth-passing signal rows. Rows with w_truth = 0 are left out because they enter no sum, and
    every weight must be non-negative.
  - Equal multisets give a bijection: each denominator row takes the factor of its value-identical signal row. Then
    D*_j = T*_orig,j exactly, with no float tolerance.
  - The hunk also asserts that the input's `hasTruthOnlyMisses` is non-zero, as the driver reads it
    (`bool(int(...))`), and that the canonical denominator is present. On 43f8cc16 the flag reads 12, because hadd
    sums the per-playlist flag over 12 playlists. "= 1" would be a false STOP.
  - **Measured on the real input** (`receipts/couple/run2/`; the director's GO; cov2d's ack; 2026-11-27T17:31–17:35Z,
    login04, 0 node-h):
    - on 43f8cc16, read from r3's staged copy, the identity holds exactly;
    - 32,849,103 denominator rows and 32,849,103 truth-passing signal rows, with no row dropped by either loader's rules;
    - 0 per-cell count mismatches, 0 one-sided cells and 0 deviation in pT, p∥ or w;
    - every signal tuple has an exact twin in the denominator;
    - neither tree has event-ID branches.
  - Run 1 crashed at `import ROOT` before reading anything, because the conda environment was not activated
    (`receipts/couple/run1/`). The launcher was fixed (4cf2d915 → 584c7c8a) and re-approved before run 2.
  - If the gate fails, nothing is read, and the mismatch (cells, counts) goes to the director.
- **The replica completeness**, per truth cell j, with T the summed w_truth of truth-passing signal rows (the original
  rows, or all rows), * the resampled weights and CV the un-resampled ones:

  c*_j = (T*_all,j / T*_orig,j) · (T_orig,CV,j / D_CV,j)

  Under C-COUPLE's bijection, T_orig,CV,j / D_CV,j is 1 up to summation order. So this is T*_all,j / D*_j with
  D*_j = T*_orig,j, the denominator resampled with its own rows' factors. Both methods divide by the same c* through
  the same extraction arguments. The CV value of the same functional is OOFVC's R completeness.
- **The cell table** (D_CV,j, T_orig,CV,j, T*_orig,j), in order:

  | case | rule |
  |---|---|
  | D_CV,j = 0 and T_orig,CV,j = 0 (a structural zero, e.g. a θ_μ ≥ 20° corner) | c*_j = ROOT's `Divide` value, 0, exactly as at the CV. The extraction (which gives 0 where c ≤ 0) suppresses the cell in both. Cells where moved truth weight is so suppressed are counted and printed |
  | exactly one of D_CV,j and T_orig,CV,j is 0 | excluded by C-COUPLE; if met, a **STOP** |
  | both positive, T*_orig,j > 0 | the formula |
  | both positive, T*_orig,j = 0 (lost support: the weighted sum over the cell's original rows is 0, i.e. every original row of positive weight drew 0) | then D*_j = 0, so the consistent value is x*_j = 0. The hunk sets c*_j = 0, and the extraction (c ≤ 0 gives 0) returns 0 for both methods. Production's replica also gives x*_j = 0 there, since its unfolded count is 0. Under R the unfolded count can stay positive when moved rows survive, and it is c*_j = 0 that makes x*_j = 0. Counted per replica, with the cells that keep moved weight counted separately, and printed. All seeds are kept, and no replica is conditioned on support |

- **C-SUPPORT (printed, read by nothing).** In `p_R_c`, for every seed b = 1..200, the runner draws the original-row
  signal factors and lists the lost-support cells by the weighted sum, before any replica launches. The table shows
  how often the last case occurs. No seed is substituted.
- **The record per unit:**
  - the data, original-row, appended-row and injected-row factor vectors' sums and sha256;
  - the appended entry list's sha256;
  - c* and the cell-table counts.

### 2.3 Units

| unit | convention | seed | role |
|---|---|---|---|
| `p_off_c` | production | — | C-BASE, C-COUPLE, C-FIX, C-SIM |
| `p_off_b{1..5}` | production | 1..5 | C-REPOFF (b = 1); C-PROTO (diagnostic) |
| `p_R_c` | R | — | δ_R; C-MOVE, C-FIX, C-SIM, C-COUPLE; C-SUPPORT's table |
| `p_R_b{1..200}` | R | 1..200 | C_δ and the null |

That is 207 units.

### 2.4 The statistic

This is REF-C2C1 §1.4's statistic, by its reader's own `t_and_null`, `rank_for` and `classify_t`, after C-SHAPE:
- **The vectors:** the full 224-cell vector at K = 10, in GlobalID = (p_T bin − 1)·16 + (p∥ bin − 1) order. K = 5 is
  computed identically and is not primary.
- **R:**
  - δ_R = x_IBU,R − x_E_R,R on `p_R_c`;
  - D_b = x_IBU − x_E_R on `p_R_b`, for b = 1..200;
  - T = δᵀ C⁺ δ, with C⁺ the rank-50 pseudo-inverse of the ddof-1 covariance of the D_b (`pinv_rank`, r = ⌊200/4⌋);
  - the null is leave-one-out, with q̂₉₅ its 95th percentile and max̂ its maximum.
- **B:** the same functions on REF-C2C1's products at seeds 1..200:
  - δ_off = `c2_central` − E_R (001);
  - D_b,off = `c2_replica_b{b}` − Q_R S1_b.

**The bars are prespecified empirical thresholds.**
- A simulation in coverage-5b-audit (#767 Q1), quoted in REF-C2C1 §1.4, used p = 224, replicas centred on δ_data and
  a truncated pseudo-inverse at ⌊N/4⌋. At N = 200 it found a "differ" rate of 0.003, against 1/(N + 1) ≈ 0.005.
- It does not validate the R pipeline, and no calibrated R false-positive rate is claimed.
- The reference null is exact agreement: "differ" says a difference is detectable at this noise in the retained
  modes, not that it is large.
- The statistic is blind to any component of δ wholly in the discarded subspace.

### 2.5 The grid

M's driver grid, which is E_R's and REF-C2C1's:
- p_T edges 0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50 GeV/c;
- p∥ edges 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60 GeV/c;
- 14 × 16 cells.

This is not Tier 1's grid (interior p_T edges 0.075, 0.325, 0.475). r3's rows file is reused: its only grid test,
"true muon in a cell of the grid", depends on the outer extents, which the two grids share (C-GRID).

## 3. Controls

**The numerical rule for every comparison below.** Operands are validated for shape, axes, GlobalID order and
finiteness before any arithmetic. "Relative to r" means |a/b − 1| ≤ r where b ≠ 0, and a = 0 exactly where b = 0. Any
non-finite value fails, and reductions never skip a NaN.

### 3.1 The R controls (each must pass, or nothing is read and it goes to the director)

- **C-IN:** every §1 R pin, checked on the bytes that are used (the staged copies, the deploy tree, the scorer's
  files). The mandatory E_R central is present and equal to `a5c13fc3…`.
- **C-GRID:**
  - the driver's PT_EDGES and PZ_EDGES equal §2.5's exactly;
  - both axes' outer edges equal Tier 1's grid;
  - every unit's output axes, and the mandatory E_R central's, equal §2.5's.
- **C-UNITS:** an exact inventory of the 207 units, with no missing, extra or duplicate name or seed. For each unit:
  - the npz and root sha256 equal its done-marker's, and the verdict is PASS;
  - argv equals §2.1's for its row: the staged input paths, the convention flags on R units only, and the bootstrap
    flags with seed b on replica units only;
  - the top-level `ks` is exactly the scan, and the unfolder is RooUnfold at the bound library;
  - the CPU count is 64, the thread environment is §2.1's literals, and the runtime versions are the same across all
    units.
- **C-PINS:** every unit and the scorer record every §1 pin, each equal to §1's.
- **C-MOVE** (OOFVC's rule, `OOFVC-DECLARATION.md:309-314`, on M's grid):
  - **the sets, in `p_R_c`:** the rows file's 544,162 entries split into the appended set (536,518, the in-grid rows
    passing the weight rule) and the reco-outside set (7,644), which are disjoint;
  - **the sets, in every R replica:** the background fill rows and the injected entries are both disjoint from the
    rows file's entries. The fill-row entry set equals `p_off_b1`'s minus the rows file's entries, since fill rows do
    not depend on the seed;
  - **the removal** (`p_R_c` against `p_off_c`):
    per reco cell, the background removed equals the moved rows reconstructed in the grid that the background loader
    had filled (0 ≤ w < 1e6, POT-scaled), recomputed from the rows file. The tolerance is 1e-12 of the cell's
    production background, with an exact zero where that background is zero;
  - **the counts:** the signal arrays grow by exactly 536,518, with `dropped_appended_weight` = 0 and
    `dropped_outside_weight` = 0;
  - **upper edges:** listed rows whose reco lies exactly on a last upper edge are counted and printed. Production's
    closed fiducial test can inject such a row, and ROOT bins it as overflow;
  - **finiteness** is required of every operand used.
- **C-FIX** (OOFVC's list): `hOFTruthDenom2D`, `hDataReco2D`, `hFlux_pt`, dataPOT, mcPOT, potScale, both flux integrals
  and nNucleons are equal bit for bit, with bin errors and overflow, between `p_R_c` and `p_off_c`.
- **C-COUPLE:** §2.2's exact multiset identity, in `p_off_c` and in `p_R_c`'s original rows, with the
  assertions that `hasTruthOnlyMisses` is non-zero (as the driver reads it) and that the denominator is present. If it
  fails, nothing is read. Measured on 43f8cc16 before binding: exact (§2.2). The cell sums' agreement is printed
  beside it.
- **C-NORM:** in every unit, the extraction's fixed arguments as consumed (the flux vector, data POT, nucleon count and
  both edge arrays) have the same digest as `p_off_c`'s. C-FIX checks `p_off_c`'s against the CV inputs. A
  replica cannot pass with a different normalization.
- **C-REFINE:** in every unit, the refinement's returned weights are, bit for bit, the measured weights both methods
  received.
- **C-FILL-IBU:** in every unit and at every K, IBU's event-level route equals its direct route, relative to 1e-9.
  - The event-level route is `ref_c2c1.filled`, then the recorded extraction; the direct route is `xsec_at_every_k`.
  - The unit's own `hXSec2D` is never compared, because it is OmniFold's.
- **C-PAIR:** in every unit, inside the observed call:
  - the coordinates, masks, MC weights and w̃ that the real OmniFold receives are the arrays IBU binned (sha256 on both
    sides, equal);
  - y is rebuilt independently: the half-open in-grid sample (lower edges in; a value on the last upper edge is
    overflow, as ROOT and `binned_problem` place it), summed by `np.histogram2d` over the driver's edges. It equals
    IBU's y relative to 1e-9, since summation order is the only difference.
- **C-DRAW-R**, row level, in every replica unit. The runner regenerates the data, original-signal and background
  factor vectors from b with the driver's offsets, and checks exactly at two points:
  - **at the refinement's entry:** the signed sample equals [b_data; −w_inj,CV · b_bkg[e_inj]]. The ordered injected
    entries e_inj are recomputed independently from the background fill rows by the driver's fiducial rule, and
    must equal those the driver used. The sample's coordinates equal the data's and the injected rows';
  - **at OmniFold's entry:** the MC truth and reco weights equal the CV weights times [b_signal; b_bkg[appended
    entries]].

  The appended entry list must also equal the rows file's in-grid, weight-passing list, in order. The appended rows
  at the end of the signal arrays must be those rows: their reco and truth coordinates exactly, their weights as the
  driver forms them (w × POT scale), and both masks true. In the scorer, for
  every b in 1..200 whose Q_R copy C-D4 accepted, `p_R_b`'s data, original-signal and background stream lengths and
  sums must equal Q_R S1_b's `p1Streams` record exactly; these are aggregate checks.
- **C-COMP:** in every unit, on the completeness histogram the extraction consumed (the recorded call's argument):
  - on an R replica, it equals c* recomputed independently from the CV rows, the seen weights and D_CV under §2.2's
    table, relative to 1e-12;
  - on every other unit, it equals c from the CV weights, relative to 1e-12. In production units that is KNOWN_ISSUES
    84's frozen value.
- **C-SIM, C-ROO** (REF-C2C1's, at 1e-9, under §3's numerical rule):
  - C-SIM covers, by index, every one of the 205 reported cells, on `p_R_c` and `p_off_c`;
  - C-ROO runs on every unit with the bound library.
- **C-BASE:** `p_off_c` reproduces E_R's `hXSec2D` (the mandatory 001), per bin relative to 1e-8.
  - If `c2_central.npz` is accepted by C-D4, `p_off_c` also reproduces its IBU cross section at every K, relative to
    1e-8. If it is cleanly absent, `p_off_c`'s D_IBU at every K is compared with readout.json's to 1e-6 instead, and the
    fallback is recorded.
  - The tolerances are prespecified acceptance targets. 1e-8 is RE-2's rule; the 9.2×10⁻¹² that C-CV measured is a
    central OmniFold refit, not a bound on IBU or on replicas. 1e-6 is OOFVC's tolerance for distances.
- **C-CELLS, C-PUB** (REF-C2C1's):
  - the 205 cells from the bound precision ROOT, equal by index to the committed `cells.root`, against both
    publication masks (StatOnlyCovariance's diagonal and TotalCovariance's), as REF-C2C1's reader checks;
  - χ² = 465.41527219152636 over 205 for the mandatory E_R central, to 1e-8. The target is main's full-precision
    `c_pub` (REF-C2C1 `config.json`, the director's ruling of 2026-11-06); REF-C2C1's read observed
    465.4152721915331.
- **C-SHAPE**, the scorer's gates. They run on each arm's raw operands before subtraction, and on δ and D before
  C-PROTO and before classification:
  - each operand is a finite 224-vector on §2.5's axes;
  - δ is a finite 224-vector and D a finite 200 × 224 matrix, rows in seed order;
  - in the full covariance and in each of the 200 leave-one-out covariances, the 50 leading eigenvalues are strictly
    positive. That is `pinv_rank`'s own criterion (`ref_c2c1_read.py:115-120`), checked here before it can raise;
  - the covariances, T, q̂₉₅ and max̂ are finite.

  Any failure refuses. A non-finite T is never classified.

### 3.2 The baseline controls (C-D4, C-REPOFF, C-PROTO)

- **C-D4**, for each optional product (§1):
  - present as a regular file, copied through `Staged` under the read guards;
  - its sha256 equals its independent binding;
  - an REF npz has top-level `ks` equal to the scan, and meta unit `c2_replica_b{b}` (or `c2_central`) with argv
    carrying `--bootstrap-seed b --bootstrap-streams three` (or neither);
  - a Q_R copy's recorded `p1Streams` has seed b, streams three, `unit_factors` false and the driver's offsets;
  - malformed files, copy failures, permission errors and duplicate markers fail.
- **C-REPOFF** (formation): `p_off_b1` reproduces Q_R S1_001's `hXSec2D`, and `c2_replica_b1`'s cross section at
  K = 10 and 5, per bin relative to 1e-8.
  - Its refinement record matches S1_001's: `params`, `signed_sum`, `n_data` and `n_injected` exactly;
    `refined_sum` and `clipped_fraction` relative to 1e-8.
  - It is seed-1 reproduction evidence of the replica path, not a bound for other seeds.
- **C-PROTO** (a diagnostic, read by nothing), for b = 1..5 and for the centrals:
  - Δ_b = D_b,paired − D_b,B, with D_b,paired from `p_off_b`;
  - Δ_c = δ_off,paired − δ_off, with δ_off,paired from `p_off_c`;
  - printed: ε (the maximum over cells with C_bb,B > 0 of |Δ| / √C_bb,B, and any difference in a zero-variance cell)
    and the whitened norms (Δᵀ C_B⁺ Δ)^½ at rank 50.

### 3.3 The disposition, in this order

The first stage records operand acceptance and B's availability before any T is formed. The second stage applies
C-SHAPE's score-dependent refusals after T and the bars are computed and before any classification. Each outcome is
recorded with its reason. A permission, staging or copy error is a failure, never a clean absence.
1. Any R control fails, or the mandatory E_R central is absent or mismatched: **STOP**, nothing read.
2. Any optional product present but failing C-D4, or C-REPOFF failing on an accepted seed-1 pair: **STOP**, nothing
   read.
3. Any optional product cleanly absent, and everything present passing: **B unavailable**. The checks that need the
   absent products are skipped and listed, and R is read alone.
4. Every optional product accepted and C-REPOFF passing: **B formed**. Both arms are read, with their protocols named.
5. After the scores: a C-SHAPE failure in any formed arm (a non-finite T, bar or covariance) is a **STOP**, with
   nothing classified.

STOP produces no statement.

## 4. Readings, fixed before any number

**PTMC-R1** (primary, K = 10). This is REF-C2C1's C2-R1 rule on R:

| T_R | reading |
|---|---|
| T_R ≤ q̂₉₅ | **agree** |
| q̂₉₅ < T_R ≤ max̂ | **marginal** |
| T_R > max̂ | **differ** |

**PTMC-B:** the same rule on B, when B is formed. **K = 5** is reported in the same form. Only K = 10 enters §5.

**Printed beside the readings, read by nothing:**
- T / q̂₉₅ per arm (undefined if q̂₉₅ = 0);
- the Hartlap factor (N − r − 2)/(N − 1) = 148/199 ≈ 0.7437;
- D_IBU at every K and D_E_R under R, on the analysis grid;
- the per-replica ρ_b = D_IBU,b / D_E_R,b at K = 10 and 5. Its central 90 % interval is taken over the defined, finite
  ratios, with their count; it is undefined if none is defined;
- per-cell δ_R / √C_bb, with zero-variance cells undefined;
- C-PROTO's ε and whitened norms;
- C-MOVE's upper-edge count, §2.2's suppressed-moved-support count, and C-SUPPORT's lost-support table.

## 5. Statements and licences

Every statement concerns **statistical detectability in the retained rank-50 modes, at K = 10.** When B is read, it is
named as "the production convention, in REF-C2C1's separate-refit protocol".

| PTMC-R1 | B | statement |
|---|---|---|
| differ | formed, differ | **"Under OOFVC's R reclassification, binned IBU and 2D OmniFold stay distinguishable by the paired test: it reads differ under R (one shared refinement), as it does under the production convention in REF-C2C1's separate-refit protocol on the same draws, N and rank."** |
| marginal or agree | formed, differ | **"Under R (one shared refinement), the paired test reads ⟨marginal / agree⟩, where under the production convention in REF-C2C1's separate-refit protocol, on the same draws, N and rank, it reads differ. The two arms also differ in refinement protocol, so the change of reading is not isolated to the convention."** |
| any | formed, marginal or agree | The R reading as measured, with both triples. No statement about a change of reading: the matched baseline does not reproduce the original's differ |
| any | unavailable | "Under R, the paired test reads ⟨reading⟩ at N = 200." It is **not** compared with the original's differ at N = 300 or rank 75 |

The rows partition the twelve (PTMC-R1, B) pairs exactly once. A change of reading is an observed crossing of each
arm's own bar, not a test that the discrepancy itself changed: each arm has its own covariance, retained modes and
bars.

**Licenses:** the statement in its row, with T, q̂₉₅ and max̂ for each arm read.

**Does not license:**
- "all else held fixed", or attributing a change of reading to the convention alone;
- that the methods are equivalent or equal (the null is exact agreement);
- that the convention is the cause of the IBU-OmniFold difference;
- which method is right;
- any statement that this analysis's inputs, intermediate stages or R equal MINERvA's production histograms (caveat
  (ii); REF-C2C1 §1.5's last row);
- anything about the out-of-grid νμ CC rows left in the background (caveat (i)), or about OOFVC's N variant (caveat
  (iii));
- anything from K = 5 or from §4's printed quantities;
- any change to E_R, Q_R or the note's adopted results.

## 6. Admissibility

- No R product becomes a reported result.
- No follow-up run is made because of these outcomes unless a new declaration binds it.

## 7. Cost and the launch rule

- **A job's charged node-h** is its sacct `Elapsed` times its node count. The pilot's charge is the pilot job's.
- **Every unit runs as its own named `srun` step**, so step-level sacct isolates it.
- **t_R** is the step-level sacct `Elapsed` of the pilot's R replica `p_R_b1`. Each unit's own `seconds` is recorded
  beside it.
- **o** is the pilot's per-node overhead: its job `Elapsed` minus its longest step `Elapsed`.
- **The replica layout is fixed:** 5 nodes, 4 lanes of 64 CPUs each, and 10 units per lane in sequence, which gives
  200 slots for 199 replicas.
- **The projection** is the pilot's charge plus 5 × (10 × t_R + o) node-h. At the scoped 0.0489 node-h per replica
  (t_R ≈ 704 s with four lanes per node), that is about 10.2.
- **STOP before the replicas** if the projection exceeds 11.5 node-h. The replicas also do not launch before every
  pilot control passes, C-COUPLE included.
- **The hard cap is 12.5 node-h for the whole campaign,** pilot and retries included. No job is submitted whose node
  count times time limit exceeds the cap left. The replica jobs' time limit is 1.5 × (10 × t_R) + o. A retry reruns only a unit that failed for a non-deterministic reason
  (for example a node failure or a timeout); a control failure is not retried, and goes to the director.

## 8. Rulings and records

**The director's rulings, 2026-11-27, on the scoping's D1–D5:**
- D1: seeds 1..200;
- D2: a moved row keeps its own background-stream factor;
- D3: the paired unit, with the tighter pairing stated as better (§2.1);
- D4: the matched N = 200 baseline, whose stat connect gets its own GO;
- D5: M's driver grid, with C-GRID, and C-MOVE against r3's counts.

The STOP rule stands (§7).

**The director, 2026-11-27, on r2's two changes:**
- C-PROTO's four extra production replicas are confirmed. r3 makes C-PROTO a diagnostic and uses no "held fixed"
  wording at all. That is stricter than the ruling, which allowed the wording at ε ≤ 1e-3, and follows both round-2
  reads.
- The consistent completeness resampling on R replicas is confirmed, reducing to c_CV when nothing moves, with C-COMP
  on every replica. r3 adds C-COUPLE.
  - **The confirmed "STOP on T*_orig = 0" is replaced by the defined value c*_j = 0** (§2.2's table), which gives 0
    for both methods, production's own replica value there. The reason: that STOP cannot be retried on a fixed seed,
    and the fixture showed it firing on seed 1.
  - **The director accepted this (2026-11-27):** "Drop the T*_orig = 0 STOP. It would be a false STOP of a correct
    run, and setting c*_j = 0 matches what production's own replica and extract_cross_section_2d already do."
    C-SUPPORT is printed as a preflight table, and every replica's lost-cell count is in the receipt.
- Round 3 is the last declaration round. After it, only scope-rule findings block: a printed number, a gate's
  acceptance, or a false STOP of a correct run.

**The calendar.** This goes in note v1 only if its receipt merges, with full reads, before the note's last sync.
Otherwise it is v2. No step is shortened for the date.

**D4's stat connect** ran on 2026-11-27 at 10:08:52Z on login04, on the director's GO and with cov2d's ack. Its
receipt is `receipts/stat-d4/` in this PR.
- It found 604 of 604 expected files: `c2_central` and `c2_replica_b1..200` (.npz and .done), the publication copy,
  and `001..201_xsec.root`.
- The oldest file atime is 2026-11-06T07:31Z. Under /pscratch's purge policy of about eight weeks without access,
  the window runs to about 2027-01-01.

**Reads** (verbatim, with dispositions, under `reads/`):
- round 1, on r1 at `8040eedba`: codex-school2 5 / 8 / 3 and agy `gemini-4-hydrogen-high` 4 / 3 / 1 (blockers / major /
  minor);
- round 2, on r2 at `783a73a10`: codex-school2 6 / 5 / 2 and agy 5 / 2 / 2;
- round 3, on r3 at `ea1004efa`, under the scope rule: codex-school2 6 / 3 / 1 and agy 2 / 0 / 3. Both readers' blockers
  are the same two, the C-COUPLE premise and §7's lane division. codex's other four (the weighted lost-support
  trigger; a moved entry reused in a replica; a replica's normalization; the C-COUPLE float tolerance) are answered in
  r4 (`reads/r3/DISPOSITION.md`).
