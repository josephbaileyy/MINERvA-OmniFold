# DECLARATION COV2D, campaign (c): held-out-tune method coverage of the adopted 2D covariance, with the covariance remade at each tune (2026-11-02)

**By** the `cov2d` session, for a fresh Sonnet audit, then the director's binding.

**Under:**
- [`DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md`](../../../DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md)
  (#690), item 3(c), at `:81-82`: "A held-out-tune coverage ensemble for the 2D covariance, on 1B's staged design,
  with the covariance remade at each truth. It is priced first."
- [`DECISION-20261102-joseph-1b-redesign.md`](../../../DECISION-20261102-joseph-1b-redesign.md) (#700, on `main` at
  `7544822d`): first-order composition, the three additions, a second STOP ending the stage, and the paper's neutral
  wording. The director ruled (2026-11-02, by message) that (c) follows it on the 2D bank. Its item 3, option (a)
  (λ⁺ in the pseudo-data only), is superseded for (c) by the next decision.
- [`DECISION-20261103-joseph-coverage-clip-rule.md`](../../../DECISION-20261103-joseph-coverage-clip-rule.md) (#718):
  consistent clipping, in the pseudo-data and the graded truth alike (item 1), with the weakened-pass reading, the
  director's ruling recorded there (item 4). It rests on the clipping probe C2 (§9.2).
- The scoping [`COV2D-SCOPING.md`](COV2D-SCOPING.md) (#693, head `5004c7a3`), its §8 rulings, and the director's
  rulings of 2026-11-02 to this session, by message (§14 lists each).

**After:**
- 1B's staged design: [`FD-1B-STAGED-DECLARATION.md`](FD-1B-STAGED-DECLARATION.md) (revision 2),
  [`FD-1B-STAGED-AMENDMENT-1.md`](FD-1B-STAGED-AMENDMENT-1.md), its two bindings, the stage-1 STOP report (#696) and the
  redesign proposal (#697, head `883c26c4`);
- [`OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`](../../../OUTCOME-20261005-2d-fixed-truth-coverage-fail.md),
  whose verdict this campaign can never remove (§13).

**This declares:**
- the two controls, of which control (1) has run and passed (§2);
- the truths, the drawn natures, the pseudo-data path and the covariance remade at each truth (§4);
- the grading, fixed before any number is read (§5), and the descriptive readouts (§6);
- the retention plan against `$UNI`'s purge date (§7), the price (§8), the controls (§9), the order and schedule (§10);
- the code bound now, by blob digest, with tests and mutation receipts (§11), and the code still to come;
- what each outcome puts in the paper and the note (§12), and what the result can and cannot license (§13).

**It binds now** (§11): the `--data-file` hook in `re2_driver.py`, the pseudo-data writer, the composite-weight
receipt and the 205-cell null. **The amendment binds later** the toy, block and scorer code, then the pilot and the
bulk (the director's two-step ruling).

**MEASURES:** nothing about coverage. Control (1) and two metadata probes ran at 0 node-h (§2, §7).

**CANNOT AUTHORIZE:** any job before the director's binding; the bulk before the amendment's binding and the pilot's
readout; any change to E_R, Q_R, C_model or any reported number; any paper or note text, which the paper lane drafts
when a result lands (§12).

**NOT CITABLE FOR:** any coverage statement; anything about the earlier statistical band VL162 or its failed
fixed-truth test.

Paths: `$CV` = `/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root`;
`$UNI` = `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root`;
`RE2` = `docs/orchestration/state/2d-closeout/stageF/methods/re2`; `R` =
`fd/receipts-cov2d/` beside this file. Code citations are at `108040f8` unless a sha is given.

## 1. What is tested, and what is fixed

- **The adopted 2D result** is E_R with Q_R as its headline uncertainty, and C_model beside it
  (`DECISION-20261024-joseph-adopt-re2-2d-refined.md:30-32`). Q_R = S5_R + C_PL_R (`2d-unfolding/re2/partc/re2c_combine.py:180`);
  S5_R's total is C_univ + C_stat + C08 (`docs/orchestration/state/2d-closeout/stageC/production/s5_rollup.py:473`),
  with C_univ including the 1.4 % normalization (`2d-unfolding/re2/partc/re2c_rollup.py:263`).
- **The test.** At each of two GENIE v3 tunes held out of the analysis, natures are drawn about the tune's truth under
  the systematic model, each pseudo-dataset is unfolded once by the production procedure, and the procedure's
  covariance, remade at that truth, is graded against the errors.
- **Not under revision:** E_R, Q_R, C_model, the estimator and every reported number. No outcome inflates, replaces
  or re-weights a block (#690; 1B declaration §1).
- **Grading is per tune.** With two truths there is no coverage rate (1B declaration `:70`).

## 2. The two controls (scoping §8, ruling 1)

**Control (1), $UNI's CV columns equal $CV's: PASS** (`R/control1/`, commit `4139e2f4`).
- Login11, nice 19, 0 node-h, 2026-11-02T22:05:37Z, approved by the director as a scoping probe before binding.
- Every shared branch of every shared tree is bitwise equal: interpretation, dtype, entry count and every row's bytes,
  with equal per-column sha256. That is 17 branches over `data` (3; 4,119,797 rows), `mc_background` (4; 658,227),
  `mc_signal_reco` (7; 32,849,103) and `mc_truth_denom` (3; 32,849,103). Every CV branch exists on `$UNI`.
- Both files were read only through `O_NOATIME` descriptors, and atime was unchanged on both.
- Script `control1_content_check.py` (sha256 `1b1edc05…`), 15 tests and 3 subtests passed, 16 of 16 mutants killed.
- **So `$UNI` is a valid basis** for the natures: its CV columns are E_R's inputs, row for row.

**Control (2), end to end, before any toy** (the director's ruling 2 of 2026-11-02):
- **(2a) The writer, bitwise at the input.** `$CV`'s own data tree, written through `cov2d_writer.write_data_file`,
  must equal `$CV`'s data tree bitwise by control 1's `compare_tree`, imported unchanged, and its `dataPOTUsed` must
  equal `$CV`'s (`cov2d_writer.writer_control`). It runs on a login node at 0 node-h, after this binding.
  - Control 1's rule that all four trees exist is for whole omnifiles. The writer's file holds only `data` and
    `dataPOTUsed`, so the control calls `compare_tree` on `data` alone and refuses any other key.
- **(2b) The unfold reproduces E_R.** `re2_driver.py --omnifile $CV --data-file <that file>`, with E_R's argv
  (`RE2/run/partb_runs.tsv:2`), must reproduce E_R's `hXSec2D` to ≤ 1e-8 relative on the 205 reported cells, with
  the same reported cell set, under RE-2's equality rule. Bitwise equality is reported but does not decide, because
  configuration (a) is LightGBM's non-deterministic mode (`RE2/RE2-J0-REPORT.md:79-80`).
  - The reference is part B's `out/ER/xsec.root`. It still exists (probe 2, §7). Its sha256 must equal
    `a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef` (`re2c_rollup.py:110`), read through
    `O_NOATIME`, or the control is INVALID.
  - It runs in the pilot (§10). **If (2a) or (2b) fails, (c) stops** and goes to the director, as control (1) would
    have.

## 3. The tunes were held out

This carries 1B's record (1B declaration §3), whose queries cover C_model's builder, S1's assembly and the 5D
estimator. For 2D, the same holds by construction:
- E_R, Q_R and their code were produced by RE-2 parts B and C on 2026-10-23/24 (`RE2/RE2-PARTB-REPORT.md:52-63`), and
  2D C_model by the same part C (`RE2/RE2-PARTC-REPORT.md:242-258`). The tunes first enter code on 2026-10-27, in F1
  (1B declaration `:136-137`).
- The scoping's P1 search: `grep -rlE 'G18_10a|AR23_20i' 2d-unfolding` is empty, rc 1 (`COV2D-SCOPING.md`, P1).
- **"Held out" is not "independent"** (1B declaration `:153-159`). The 2D C_model uses the same three vertices, GENIE
  2.12 + MEC, NuWro and GiBUU (`2d-unfolding/pv2d/report_tables.py:31`). So G18's Valencia 2p2h shares the GENIE + MEC
  shift's family, and AR23 shares G18's Nieves quasielastic model. §6 reports the leave-out-MEC variant.

## 4. The design

### 4.1 The truths

| truth | definition | pin |
|---|---|---|
| **G18** | G18_10a_02_11b: F1's gated, k-normalised bridged ratio `bridged/genie_v3_g18.json`, applied per row by `s5e_deform.ratio_weight(gen, FINE, w_truth, ratio, 1.0)` | sha256 `25477aae…8c95b4`, F1's committed digest (`fd_1b_toys.committed_ratio_sha256`) |
| **AR23** | AR23_20i_00_000, the same with `bridged/genie_v3_ar23.json` | `eab33d6d…582fc2` |

- **On the 2D events.** `gen` is `(MC, MC_pz, MC_eavail, MC_q3, MC_W)` from `$UNI`, all in GeV (the event loop
  divides E_avail, q3 and W by 1000; `runEventLoopOmniFold.cpp:587-591`), on F1's 5D fine edges (`pvl_lib.FINE`).
  This is 1B's application exactly (`fd_1b_toys.py:338`): no projection onto (p_T, p_∥) is made (scoping §8 ruling 2).
- **One r_T per row.** r_T is computed once per tune with the CV `w_truth`, and its rescale constant comes from
  `mc_truth_denom`'s rows, the population whose cross section is graded. The same per-row factor applies to every
  `mc_signal_reco` row, by calling `ratio_weight` once on the concatenation (truth-denominator rows with their
  weight, signal rows with weight 0), so no second implementation is written.
- **Rows outside the 5D grid** (non-finite or out-of-range truth) get r = 1, as `ratio_weight` does. Background rows
  get r = 1: `mc_background` carries no truth kinematics, and 1B never reweights it.
<!-- absence-ok: a design choice of what (c) runs, not a claim that a result does not exist -->
- **No plug-in truth.** It would need a second driver hook to capture the push weights. The scoping priced it as
  optional; it is not run.

### 4.2 The natures: every group drawn

One toy is one nature, drawn from `numpy.random.default_rng([seed, DRAW_SALT])` by `cov2d.draw`, then unfolded once.

| group | the nature drawn | matches the block (`re2c_rollup.py`) |
|---|---|---|
| **Flux** | one of the 100 universes with probability w_u / Σw, the constraint weights | the weighted MAT covariance `wcov` (`build_repair.py:127-132`) with those weights (`re2c_rollup.py:203-232`) |
| **2p2h** | one of its 3 universes, ⅓ each | `band_cov`, unweighted, ÷3 |
| **the 36 other bands** (interaction, GEANT and MINOS efficiency weight bands) | one endpoint, ½ each | ÷2 = ¼ (x₀ − x₁)(x₀ − x₁)ᵀ |
| **lateral** (5 bands) | the declared surrogate: x̂ += Σ_b s_b Δ_b(T)/2, s_b = ±1, with Δ_b(T) the endpoint difference remade at T (§4.4), after X01 for Muon_Energy_MINOS | the same two-point form |
| **normalization** | x̂ × (1 + 0.014 z), z ~ N(0, 1) | (0.014 x)(0.014 x)ᵀ (`re2c_rollup.py:100, 262-263`) |
| **statistical** | Poisson pseudo-data at data size on every reco-passing signal row and every background row, at λ⁺ (below) | the three-stream bootstrap's data stream (§4.5) |
| **seed** | not drawn: estimator seed 42 for every unfold | C08 carried (§4.4) |

- **The bank** is RE-2 part B's universe block: 38 bands, 175 universes (Flux 100, 2p2h 3, 36 bands at 2). `cov2d.BANDS`
  is checked against part B's J2 run list by a test. Draw order: Flux, then the other 37 bands sorted.
- **Composition, first order** (DECISION-20261102-joseph-1b-redesign.md item 1). For each per-row array a ∈
  {`w_reco`, `w_truth`, `w_bkg`}, a_D = a_{u₁} + Σ_{j≥2} (a_{u_j} − a_CV), accumulated in draw order
  (`cov2d.compose`). For one universe it is a_{u₁} bitwise. Universe columns are `$UNI`'s
  `w_reco_<band>_<idx>` (signal), `w_truth_<band>_<idx>` (truth denominator) and `w_bkg_<band>_<idx>` (background),
  as the driver names them (`re2_driver.py:534-563`).
  - Non-finite weights are zeroed and counted, as 1B's loader does.
- **The Poisson counts** of toy t come from `numpy.random.default_rng([t's seed, DRAW_SALT, 1])`, a stream separate from
  its draw's `default_rng([seed, DRAW_SALT])`, through `cov2d_writer.draw_counts`: signal rows, then background rows.
  The realization d̃_T uses the same construction at its seed (§4.4). "At data size" means at the expected count Σλ⁺,
  at the POT scale. It is not forced to the data's 4,119,797 events; each toy records Σλ⁺ and its ratio to that.
- **The Poisson mean** on a signal row is λ = w_reco,D × r_T × s, and on a background row λ = w_bkg,D × s, with s the
  POT scale `dataPOTUsed / mcPOTUsed` that the driver itself applies (`re2_driver.py:780-781, 343`).
- **Negative composites are clipped consistently** (`DECISION-20261103-joseph-coverage-clip-rule.md` item 1, option
  (1)). Each tree is clipped row by row on its own composite, with `cov2d.lam_plus` for each:
  - the pseudo-data: λ⁺ = max(λ, 0) on every signal row (λ = w_reco,D × r_T × s) and every background row
    (λ = w_bkg,D × s);
  - the graded truth: max(w_truth,D × r_T × s, 0) on every `mc_truth_denom` row. r_T > 0 and s > 0, so this zeroes
    exactly the rows whose composite w_truth,D is negative.
  - This is the rule C2 measured: its residual R_c is the pseudo-data's clipped mass over the signed signal, minus the
    truth's clipped mass over the composite truth count (§9.2). A signal row whose reco composite is negative and whose
    truth composite is not, or the reverse, is clipped in one tree only. R_c measures the net offset that remains.
  - Each toy records Σλ, Σλ⁻ and the rows with λ < 0 for signal and background, the same for the truth weights,
    Σλ⁻ per reco cell for signal and for background, and per truth cell the four sums behind R_c (§6 (ii)).
- **Each toy's truth** is the nature's own: the clipped composite truth weights max(w_truth,D × r_T × s, 0) over
  `mc_truth_denom`'s rows in the driver's truth phase space (`re2_driver.in_truth_phase_space`), per (p_T, p_∥) cell,
  normalized by the driver's own `extract_cross_section_2d` with the nature's flux (the drawn Flux universe's integral, as
  `--universe Flux:IDX` uses it) and the CV completeness ≡ 1. A control (§9) makes this equal E_R's own `hTruthXSec2D`
  at the CV nature.
- **The error** is e = x̂ − x_true on E_R's 205 reported cells (`hXSec2D > 0`, `re2c_rollup.py:169`), after the
  lateral and normalization surrogates.

**Not drawn:** C_PL_R, which comes from the data's run-period groups (`re2c_playlist_term.py:27-34, 161-162`), and
C_model, which a fixed-truth draw cannot produce. C_model is what should cover each tune's departure.

**Known difference:** the toys do not resample the unfolding's own simulation. The driver's stream options
(`re2_driver.py:1512-1527`) offer no signal-and-background-MC stream without the data stream, and a data-stream
resample on top of fresh pseudo-data would double the statistical draw. So the toys hold the simulation-statistics
part of C_stat(T) out of their errors. That part can only widen C_T against the errors, so it cannot cause a flag
under the one-sided rule. The note states it.

### 4.3 The pseudo-data path (the director's ruling 1, option (2))

- **The hook.** `re2_driver.py --data-file PATH` reads the `data` TTree from PATH instead of `--omnifile`. The
  simulation trees and the POT metadata still come from `--omnifile`, and PATH's `dataPOTUsed` must equal it
  (21 lines, marked `# COV2D`). Without the flag the driver reads its own data tree as before.
- **Why not a file in `$CV`'s full schema** (the director's preferred option (1)). The driver reads all four trees
  and the POT from the one `--omnifile` (`re2_driver.py:1744-1750, 129-139`). A universe unfold reads its weight and
  lateral columns from the same file (`:534-590`), so remaking the universe block at T would need a full copy of
  `$UNI`, 159.4 GiB, per truth.
- **The writer** (`cov2d_writer`). A count k on a row becomes k identical rows of `(measured = sim, measured_pz =
  sim_pz, measured_pass = 1)`, since the data tree carries no weight. Signal rows come first, then background rows,
  each in row order. Leaves are `$CV`'s: `measured/D`, `measured_pz/D`, `measured_pass/b` (probe 2, §7).
- **The data tree cannot carry a mean.** It holds integer counts only, and the driver's closure path, which does take
  weighted pseudo-data, refuses `--universe` (`re2_driver.py:1698-1702`). So the blocks at T are remade from one
  declared Poisson realization of T, not from T's means (§4.4).

### 4.4 The covariance remade at each truth

**The realization d̃_T** (the director's ruling 3): one Poisson draw at data size of T's CV nature (no universe, r_T
applied, λ⁺), at seed 5,721,000 (G18) or 5,731,000 (AR23). **Every remade block at that truth uses the same
realization**, so its noise largely cancels within each universe shift. It is a methods fact for the note and the
report, not a paper caveat.

| block at T | how, by the reported procedure | unfolds per truth |
|---|---|---:|
| central x̂_T | `--omnifile $CV --data-file d̃_T`, E_R's argv | 1 |
| universe (38 bands) | `--omnifile $UNI --universe BAND:IDX --data-file d̃_T`, each of the 175 universes; blocks by `re2c_rollup.universe_block`'s formulas | 175 |
| lateral (5 bands) | each of the 10 lateral omnifiles `--data-file d̃_T`; ¼ ΔΔᵀ per band, with X01 for Muon_Energy_MINOS (`re2c_rollup.py:235-253`) | 10 |
| statistical | 300 three-stream bootstrap replicas of d̃_T (`--bootstrap-seed n --bootstrap-streams three`, n = 1–300), sample covariance, ddof 1 (`re2c_rollup.py:498-499`) | 300 |
| normalization | (0.014 x̂_T)(0.014 x̂_T)ᵀ | 0 |
| C08 (seed) | **carried**: diag(x̂_T / x_R) C08_R diag(x̂_T / x_R). Its median is 0.048 % per cell (scoping §1), and remaking it is 80 unfolds | 0 |
| C_model_abs | diag(x̂_T) C_model diag(x̂_T), with C_model's matrix sha256 `11fe6818…3470` (`RE2/RE2-PARTC-REPORT.md:250`) | 0 |
| C_PL_R | **not in the graded matrix** (not drawn) | 0 |

**486 unfolds per truth.** The blocks are computed by importing the rollup's functions (`band_cov`, `universe_block`,
`x01`), not copies. The rollup's CLI cannot be repointed: it pins part B's products by digest (`re2c_rollup.py:108-115,
459-460`). The amendment states the exact imports, and a control makes them reproduce part B's S5_R blocks from part B's
products.

- **The graded matrix** is C_T = C_univ(T) + C_lat(T) + C_norm(T) + C_stat(T) + C08(T) + C_model_abs(T). Its 205 × 205
  diagonal gives the per-cell interval.
- **What a pass carries over to.** C_PL_R(T) is positive semi-definite, so a cell that covers under C_T also covers
  under C_T + C_PL_R(T), the procedure's full covariance at T. The χ² region carries over only if both have the same
  ndf (1B declaration `:278-283`).
- **It does not carry over to Q_R at the data's point.** Nothing here relates C_T to the matrix made at the data
  (1B declaration `:284-286`).
- **The lateral block.** The director approved remaking the laterals, with the I/O priced (§8) and a fallback fixed
  now: **if staging the laterals is not complete by the bulk's latest submission date (§10), the lateral block is
  carried** in relative form, Δ_b(T) = Δ_b ∘ (x̂_T / x_R) from part B's lateral products, as 1B carries it
  (1B declaration §4.4). The surrogate then draws that Δ_b(T). The choice is made by the date, never after a coverage
  number is read.

### 4.5 Why it can fail

1B's argument carries over (1B declaration §4.5). A prior-independent estimator gives toy errors and remade shifts
that are equal and opposite at first order, band by band. The power comes from the estimator's dependence on the
simulation's truth distribution at fixed response, which enters the two with different weights once m_T ≠ m₀. For
2D, PV-2D measured the data-side prior dependence of the earlier estimator E_U at C_model's generator vertices
(`2d-unfolding/pv2d/pv2d_analyze.py:18`). It is not E_R's, and it is not used here as a power ground. No outcome is
predicted.
Search: `git grep -lE "prior_share|prior_mc|prior dependence|prior-dependence" -- 2d-unfolding docs/orchestration/state/2d-closeout` @ 4139e2f4 (one code hit, pv2d_analyze.py; the rest are notes and inventories)

## 5. Grading, fixed before any number is read

**One implementation.** Every threshold is computed by 1B's `nd-unfolding/fd_1b_null.py`, imported unchanged. Its
null, flag counts, size and attribution do not depend on the cell count. Its Bonferroni divisor is `len(p_use)` = 205
(`fd_1b_null.py:145-154`).

### 5.1 Statistics per tune, over its 300 toys

As 1B's §5.1, on 205 cells: the per-cell in-interval fraction p̂_c against the draw-matched null p_c(T); χ² on C_T's
non-null subspace (eigenvalues above 10⁻¹² of the largest), with the Cholesky equality checked if ndf = 205; the joint
in-region fraction q̂ against q(T); pulls; the bias-versus-width attribution of every flagged cell
(`fd_1b_null.attribute`); mean χ²/ndf; and the under-coverage factor s_c.

### 5.2 The rule, per tune

**The null** (`fd_1b_null.null_contents`), at each tune T after its blocks exist and **before any toy error is read**:
- one `Discrete` law per drawn band: the Flux universes' centred shift vectors at T with probabilities w_u / Σw, 2p2h's
  three at ⅓, each pair band's two endpoints at ½, and each lateral band's ±Δ_b(T)/2;
- one Gaussian with covariance C_stat(T) + C_norm(T) + C08(T) + C_model_abs(T);
- the components must sum to C_T to 10⁻¹² relative (`check_matched`), or the null refuses;
- 2,000,000 simulated vectors at seed 5,742,000. Flag counts are taken at the content minus 3 Monte Carlo standard
  errors.

| reading | condition |
|---|---|
| **cell c under-covers** | #{t : \|e_tc\| ≤ σ_c} ≤ k_c(T), the largest k with P(Bin(300, p_c(T)) ≤ k) < 0.025/205 |
| **joint under-coverage** | #{χ²_t in region} ≤ k_J(T), the largest k with P(Bin(300, q(T)) ≤ k) < 0.025 |
| **COVERS at T** | no cell under-covers and no joint under-coverage |
| **UNDER-COVERS at T** | otherwise; the report names each cell and whether the joint fraction is under too |
| **INVALID at T** | any §9 control fails for T; reported unrepaired |

- **A weakened pass** (the director's ruling, `DECISION-20261103-joseph-coverage-clip-rule.md` item 4, the consult's
  reading at `R/clip/consult/ANSWER-1.txt:56`). Clipping truncates the downward tail of each nature's shift, so in a
  cell where it narrows the spread the toys' errors are smaller than C_T describes, and a pass there is a weaker test.
  **A cell that is not flagged, at a tune where its clipped-composition variance ratio from C2 is below 0.9, reads
  "passes, weakened by clipping".** A flag in such a cell is read as any other flag. The ratio is C2's
  `variance_ratio.option_1_clipped` in `R/clip/c2-clip2.json` (sha256 `39e333c5…`), and the cells are
  `cov2d.weakened_cells` of it, fixed now, before any toy:
  - **G18, 10 cells** (flat index i·16 + j, p_T bin i, p_∥ bin j): 79, 95, 107, 111, 123, 127, 143, 159, 175, 191.
    Eight are at p_∥ 40–60 GeV/c (j = 15), and two at 9–10 GeV/c (j = 11). Smallest ratio 0.865, in cell 127.
  - **AR23, 54 cells:** 9, 10, 11, 12, 25, 26, 27, 28, 29, 32, 33, 41, 42, 43, 44, 45, 48, 49, 51, 57, 58, 59, 60,
    61, 64, 65, 74, 75, 76, 77, 80, 81, 91, 92, 93, 96, 97, 98, 99, 108, 109, 112, 113, 114, 115, 116, 124, 125, 140,
    141, 156, 157, 172, 173. They lie at p_T below 1.25 GeV/c, in two regions: p_∥ 7–20 GeV/c (j = 9–13) and p_∥
    1.5–4 GeV/c (j = 0–4). Smallest ratio 0.761, in cell 43.
  - No cell is in both lists.
  - **The ratio is a truth-level proxy:** the variance of the nature's truth count over the 300 draws, divided by the
    truth-level image of C_T's drawn blocks, Σ_b Var_b (`R/clip/clip_probe2.py:12-16`). It is not the variance of the
    error e = x̂ − x_true, which exists only after the toys.
  - **The toys use these same 300 draws per tune,** so the ratio is this ensemble's realized value, not an estimate of
    it. Against the population value (infinitely many draws) it carries a sampling error of about 0.08
    (`R/clip/c2_reading.txt`). AR23's first-order ratio, which is 1 in that limit, has median 0.953 and minimum 0.793
    over these draws. Part of what the label marks is therefore this draw set's own shortfall, and the toys see it too.
    The list is used as it stands (the director accepted it as fixed); it is not re-drawn after any toy.
  - **The label is per cell.** The joint reading carries no weakened label. The report gives, beside each tune's joint
    reading, the share of the 205 cells that are weakened at that tune (10 at G18, 54 at AR23).
  - The verdict per tune is unchanged by the label. The report gives the weakened cells beside it.
- **The outlier cell, named now:** flat cell 216 (`cov2d.OUTLIER_CELL`), p_T 2.5–4.5 GeV/c, p_∥ 6–7 GeV/c. In C2 its
  residual |R| reached 4.27 σ_Q at G18 and 4.27 σ_Q at AR23 in a few draws, while its median and 90th percentile were
  0. No other cell's maximum exceeds 0.40 σ_Q (G18) or 0.29 σ_Q (AR23). Its option (a) maximum, 4.23984232307767 σ_Q,
  is bit-identical at both tunes, so r_T cancels there: few rows, perhaps one, drive it (the auditor's inference; the
  row is not identified, which would need a read of `$UNI`). The pseudo-data job records, for this cell, the rows with
  a negative composite in each toy and their weights. The report gives its |R_c| maximum over each tune's toys in σ_c
  (§6 (ii)), and its reading, whatever it is.
- **One-sided.** Over-coverage is reported, not failed.
- **Size:** at most 0.025 + 0.025 = 0.05 per tune by the union bound, and 0.10 over both, **when the toys' errors
  follow the null's law.** `fd_1b_null.size` prints the exact value at each null. The toys depart from that law in
  known ways:
  - the Flux and pair-band draws are un-centred, while the null's laws are centred (§6 gives the predicted offset);
  - clipping truncates the shifts (§4.2, §6 (ii));
  - C08, C_model and the simulation-statistics part of C_stat are in C_T and in the null's Gaussian, but are not drawn
    (§4.2). This narrows the toys' errors against the null, so it can only lower the flag rate.

  The first two can move the flag rate either way. So 0.05 is the size under the null's law, and every report states
  these departures beside it.
- **Power** (arithmetic, `R/code/power.out`): at p_c = P₀ = 0.6827, k_c = 174. A cell is flagged with probability 0.26
  at a true content of 0.60, 0.52 at 0.58, 0.87 at 0.55 and 0.98 at 0.52. The joint count (k_J = 188) is flagged with
  probability 0.62 at 0.62 and 0.84 at 0.60. **So (c) resolves a per-cell deficit of about 0.10–0.13 in content, and
  about 0.08 jointly.** The coarser per-cell resolution than 1B's (0.10 at 16 cells) is the Bonferroni divisor 205.
  Smaller deficits can pass, and every report states the resolution.

## 6. Descriptive readouts, no verdict

- **The spread alone:** pulls and p̂ against C_T without C_model.
- **The bias:** the toys' mean error against σ_c per cell.
- **The predicted offset of the un-centred draws:** −Σ_b Σ_u p_u (x̂_u(T) − x̂_T), from the remade products (1B §5.4).
- **The leave-out-MEC variant** C_T⁻, with C_model⁻ from the NuWro and GiBUU shifts only, read exactly as 1B §5.4
  fixes it: it changes no verdict, and a tune that covers under C_T but is flagged under C_T⁻ reads "its coverage in
  cells [list] rests on the GENIE + MEC shift".
- **The realization check** (the director's ruling 3): x̂_T, the CV unfold of d̃_T, against T's truth, per cell in σ_c.
- **The three additions of the redesign decision, applied to 2D:**
  - **(i) Cross terms.** On a login node at 0 node-h, over the 600 declared draws, each reco cell's histogram under
    product composition against first order, in units of the cell's data-statistical σ (√ of its expected count).
  - **(ii) The clipping residual,** under consistent clipping (§4.2). The redesign decision asks for "the unfolded
    offset in σ_c from one mean unfold per truth". **2D cannot unfold at the mean** (§4.3), so the offset is taken at
    first order, as C2 took it, for every toy and read before grading. Per truth cell c, at the toy's nature's expected
    counts (before the Poisson draw):
    - S_c, the signed λ over the reco-passing signal rows whose truth lies in c, and m_seen,c, the |Σλ⁻| over them;
    - N_c, the unclipped composite truth count, and m_all,c, the |Σ| of its negative part;
    - R_c = m_seen,c / S_c − m_all,c / N_c, signed, in σ_c by R_c × x_true,c / σ_c.
    - The efficiency correction is in S_c: the unfolded offset of the pseudo-data's added mass is m_seen / S, not
      m_seen / N (`R/clip/C1-ERRATUM.txt`).
    - Also per toy: the background's added mass per reco cell over the signed signal λ of that cell, on the same-index
      cell's σ_c (C2's diagonal-response approximation, the same under either clip rule), and the coherent offset
      Rᵀ C_T⁻¹ R on C_T's non-null subspace, R = (R_c x_true,c).
    - **The reading, fixed before any clipping probe ran** (in this declaration's first draft, `fc2cd112`,
      2026-11-02, before C1's code at `d94d4820`): a flagged cell whose median |R_c| across its toys exceeds 0.5 σ_c
      reads "the clipping may explain this cell's flag", and the report says so beside the verdict. The verdict is
      unchanged. **C2 predicts this reading will not fire.** The toys' natures are C2's draws, and C2's largest per-cell
      median is 0.043 σ_Q at G18 and 0.042 σ_Q at AR23. It fires only if C_T's σ_c is about ten times smaller than
      Q_R's. The threshold is not changed after C2. Whether to keep it is the director's ruling (§14 item 2).
    - Where S_c ≤ 0 or N_c ≤ 0 in a toy, R_c is undefined. It is recorded as missing and counted per cell, the medians
      are over the toys where it is defined, and the report gives the count.
    - **The outlier cell 216** (§5.2): its |R_c| maximum and median over each tune's toys, in σ_c, are reported by name.
    - This first-order substitute for the mean unfold is for the director to rule on (§14).
  - **(iii) A second STOP ends (c)** unless Joseph rules otherwise. A STOP is any step this declaration or the
    amendment says stops the campaign.

## 7. Retention (scoping §8 ruling 3; the director's atime ruling)

Metadata probe 2 (`R/scoping2/meta_probe.{py,out}`, login11, 2026-11-02T22:34:13Z, 0 node-h, stat only; atime unchanged
on `$CV` and `$UNI`). The exposure date is atime + 8 weeks (`FD-CT-RETENTION.md` §2).

| input | where | size | atime (UTC) | exposed from | read by |
|---|---|---:|---|---|---|
| **`$UNI`** | pscratch | 171,117,087,867 B (159.4 GiB) | 2026-10-24 | **2026-12-19** | the receipt, the pseudo-data job, the universe unfolds |
| flux histogram `runEventLoopMC_MEFHC.root` | pscratch | 5,143 B | 2026-10-30 | 2026-12-25 | every unfold (`--mcfile`) |
| flux-universe integrals | pscratch | 6,396 B | 2026-10-30 | 2026-12-25 | Flux universe unfolds; each Flux nature's truth |
| Flux constraint file | pscratch | 25,403 B | 2026-11-01 | 2026-12-27 | the draws |
| F1 ratios G18 / AR23 | pscratch | 543,301 / 541,943 B | 2026-10-31 | 2026-12-26 | the truths |
| E_R `out/ER/xsec.root` | pscratch | 62,196 B | 2026-11-01 | 2026-12-27 | control (2b) |
| `$CV` | CFS | 2,144,008,221 B | — | not purged | toys, central, stat block |
| 10 lateral omnifiles | CFS | 538.4 GB in all | — | not purged | lateral unfolds |

- **The deadline is 2026-12-19,** set by `$UNI`. Every step that reads `$UNI` must finish before it, with margin (§10).
- **Reads by the bound driver move atime** (the director's ruling (a)). `re2_driver.py` opens its inputs with
  `ROOT.TFile.Open(path)` (`re2_driver.py:1744`), which cannot take `O_NOATIME`. The steps that read without it, stated
  in advance:
  - every unfold reads its `--omnifile` (`$CV` or its staged copy, `$UNI`, a lateral or its staged copy), its
    `--mcfile` flux histogram, its `--data-file`, and, for a Flux universe, the flux-universe file;
  - nothing else. The receipt, the writer, the pseudo-data job, the truths, the pins and every probe read through
    `O_NOATIME`.
- **The schedule and every gate plan against 2026-12-19 as if no read moved it.** Each report records the atime
  changes the campaign caused. No file is ever read or touched for retention. No LD_PRELOAD shim, and no staged copy of
  `$UNI`.
- **New pscratch files** (staged `$CV` and laterals, pseudo-data, products) are this lane's own, in a new directory, and
  each is exposed 8 weeks after its last read. They are not purge-critical for the result, which lands in commits and,
  after #685's deferral ends, on HPSS.

## 8. Price

**The units** are RE-2 part B's charges per run (`RE2/RE2-PARTB-REPORT.md:52-63`; scoping §3): central 0.0843,
universe 0.1220, lateral 0.1715, statistical replica 0.0489 node-h. A toy is a central-shaped unfold with a different
data file, bracketed by the replica and central rates.

| item, per truth | runs | node-h |
|---|---:|---:|
| central x̂_T | 1 | 0.08 |
| universe block | 175 | 21.35 |
| lateral block | 10 | 1.72 |
| statistical block | 300 | 14.67 |
| toys | 300 | 14.67–25.29 |
| **per truth** | **786** | **52.5–63.1** |

| step | node-h |
|---|---:|
| the receipt, control (2a), staging (DTN), the cross-term readout, the null, the readout | 0 |
| the pseudo-data job: one per truth, one node each, under 12 h | ≤ 6.0 reserved (2 × 3 node-h; basis below) |
| the pilot (§10) | ≤ 2.0 reserved |
| two truths at the units | 105.0–126.2 |
| **the cap: 1.25 × the upper estimate, plus the reserves** | **165.8** |

- **Packing** follows part B's layout, one exclusive node per job at its lanes, every job under 12 h: per truth, 4
  universe jobs (part B's J2a–d each took 5:17–5:24 for 43–44 runs), 3 replica jobs (J4a–c, 4:50–4:57 for 100 runs), 1
  lateral-and-central job (J3, 1:43 for 10), and 3 toy jobs.
- **The re-price trigger:** after the pilot, a run class above 1.25 × its part B wall per run is REPRICE, an amendment.
  A toy's baseline is the central run's part B wall per run, since a toy is a central-shaped unfold.
- **The pseudo-data reserve's basis:** one pass over `$UNI` took 44:45 on a login node for the receipt (§9.2), which
  composes all 600 draws. A job reads `$UNI` once for its truth and writes 301 data files. 3 node-h per job is a
  reservation, not a measurement. A job above it is REPRICE.
- **The balance.** The last read was 2,050.9 node-h at 2026-11-02T16:15Z (1B stop report §1), so half is 1,025.5. The
  cap is below half, so the price rule does not send it back to Joseph
  (`DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md:52-59`). The director reports it to Joseph at
  binding. The first connect re-reads `iris`.
- **Lateral I/O** (the director's condition). Part B staged `$CV` and the 10 laterals to pscratch from dtn01 in 7 minutes
  (504 G) and ran J3 from the copies at 0.1715 node-h per run (`RE2/RE2-PARTB-REPORT.md:119-127`). (c) does the same:
  staging at 0 node-h from a DTN, each copy hashed against `SHA256SUMS` beside the laterals and made read-only.
  - **Quota:** `myquota` on 2026-11-02 read 17.08 of 20.00 TiB (85.4 %). Staging adds 540.5 GB (0.49 TiB), to about
    87.9 %, under part B's 90 % condition. The staging step re-reads the quota and does not stage above 90 %.
  - **Without staging,** a lateral job would read CFS through DVS from compute. Its rate is measured by one lateral
    unfold in the pilot reading CFS directly, and printed beside the staged route. Staging is the declared route.
  - **The fallback** is §4.4's: laterals carried if staging is not done by the bulk's latest submission date.
- **Storage:** results and receipts in commits; products on pscratch, then HPSS after #685's deferral (2026-11-06).
  Nothing goes to CFS.

## 9. Controls

Any failure reads INVALID and is reported unrepaired.

1. **Control (1)**: PASS (§2).
2. **The composite-weight receipt** (the scoping's P2, the director's ruling: before the price is fixed),
   `cov2d_receipt.py`, login node, nice 19, 0 node-h. Over the 600 declared draws and **every row** of `w_reco`,
   `w_truth` and `w_bkg`:
   - **N1**, an exact float64 pass (the decision's §2d (ii)). Every (row, draw) numerator |a_D| is computed. A row whose
     largest numerator over the draws, divided by the smallest any draw's peak can be, is at most 10 × (1 − 10⁻⁹) is
     certified below the bound. Every other row is evaluated exactly, draw by draw, by `n1_chunk`'s own inline first-order
     sum in draw order and peak, the same arithmetic as `cov2d.compose` and `cov2d.peak` (its docstring, at
     `cov2d_receipt.py:11`, wrongly says it calls them; the synthetic-bank tests check its values). **A composite above
     10 on any row and draw is STOP.**
   - **The truth cells** (the decision's §2b). At each tune, every declared draw's composite truth histogram,
     Σ w_truth,D × r_T over the truth phase space per cell. **A cell where the CV histogram is positive and a draw's is
     not is STOP.**
   - Descriptive: rows above 10 under the all-draws bound, rows and pairs with a negative composite, non-finite weights
     zeroed, the single-universe ratios' largest |a_u / a_CV|, and r_T's range.
   - `$UNI`, the constraint file and the two ratio files are read through `O_NOATIME`, and an atime move is STOP.
   - It runs in `omnifold_py310` (uproot 5.6.9), which has no PyROOT. The driver's truth phase space and edges are
     compiled from `re2_driver.py`'s own source without its `import ROOT` (`cov2d_receipt.driver_phase_space`), and a
     test makes them equal the real import.
   - **Result: PASS** (connect R1, `R/receipt/`, approved by the director; login11, 2026-11-03T02:10:51Z to 02:55:35Z,
     nice 19, 0 node-h; deploy clean at `b4fb3c6c`, bound blobs equal then: `cov2d.py` sha256 `4b0744d7…`, now
     `0d852a69…`, whose diff adds only `WEAKENED_BELOW`, `OUTLIER_CELL`, `weakened_cells` and docstrings, none of them
     used by the receipt; wall 44:45, peak RSS 4.27 GB; `atime_moved: []`;
     `receipt.json` sha256 `d30e197e…`, the local copies equal the cluster's digests):

     | array | rows | evaluated exactly | above the all-draws bound | max composite | rows above 10 | rows negative in some draw | negative (row, draw) pairs | non-finite zeroed | largest single ratio |
     |---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
     | `w_reco` | 32,849,103 | 1,767 | 1,994 | 2.403 | 0 | 11,358,837 | 331,386,043 | 36 | 429.59 |
     | `w_truth` | 32,849,103 | 2,209 | 2,370 | 2.439 | 0 | 12,440,871 | 359,597,299 | 0 | 429.59 |
     | `w_bkg` | 658,227 | 380 | 389 | 2.241 | 0 | 258,026 | 7,525,869 | 0 | 44.77 |

     The truth cells: 205 of 224 cells have a positive CV, and no declared draw makes one non-positive (smallest ratio of
     a draw's cell to the CV's: 0.379 at G18, 0.369 at AR23). That minimum is finite, and `np.min` propagates NaN, so
     no truth-cell ratio was NaN. The run's argv had no `--no-pins` (`R/receipt/receipt.time`). The auditor found that
     `--no-pins` would still allow a PASS and that a NaN ratio would pass the `<= 0` test. Neither touched R1, and the
     receipt is not changed after its run; any rerun would be an amendment that fixes both first. r_T lies in [0.650, 2.575] at G18 and [0.610, 2.568] at
     AR23.
   - **The receipt's flag, and what answered it.** 34.6 % of `w_reco` rows, 37.9 % of `w_truth` rows and 39.2 % of
     `w_bkg` rows have a negative first-order composite in at least one declared draw (1.68 %, 1.82 % and 1.91 % of
     (row, draw) pairs). Under option (a), the pseudo-data clipped and the truth kept
     its negative weights, so each toy would carry a one-signed offset. The director approved two 0 node-h probes
     (`R/clip/`, both on login11, nice 19, every read through `O_NOATIME`, `atime_moved: []`):
     - **C1** (`clip_probe.py`, connect C1): descriptive counts. At most 88,052 truth rows (0.27 %; the per-universe
       counts summed) have some universe weight ≤ 0 where the CV is positive, against 12,440,871 rows negative in some
       draw. So most negative composites come from several downward shifts summing past −100 % with every universe
       positive. That is arithmetic; no band is named as a cause. C1's truth-cell offsets were m_seen / N_c,
       which understates the first-order unfolded offset by about 1/ε_c: my error, recorded in `C1-ERRATUM.txt` and
       superseded by C2.
     - **An independent Sonnet consult**, verbatim in `R/clip/consult/` (PROMPT, ANSWER-1, ERRATUM-RELAY, ANSWER-2).
     - **C2** (`clip_probe2.py`, sha256 `b95c5629…`; its reading `c2_reading.txt`, `b5b4fc4b…`, fixed before the run at
       `1a07b07c`; receipts at `bc4965c4`; wall 1:13:19, peak 9.52 GB, 0 node-h). In σ_Q, Q_R's relative per-cell σ,
       a labelled proxy for C_T's:

       | quantity, over 300 draws per tune | G18 | AR23 |
       |---|---:|---:|
       | control: first-order variance ratio within 1 ± 0.2 | 100 % of cells | 99.0 % |
       | unmatched rows, truth / signal tree | 0 / 0 of 32,849,103 | the same |
       | option (a), m_seen / S: largest per-cell median, largest p90 | 0.30, 0.58 | 0.30, 0.59 |
       | option (a), coherent bᵀQ_R⁻¹b, median per draw | 42.2 | 42.3 |
       | option (1), R_c: largest per-cell median, largest p90 | 0.043, 0.097 | 0.042, 0.090 |
       | option (1), R_c: cells with signed median > 0 | 202 of 205 | 203 of 205 |
       | option (1), coherent bᵀQ_R⁻¹b, median per draw | 1.45 | 1.33 |
       | option (1), largest \|R_c\| (cell 216) and the next largest | 4.27, 0.40 | 4.27, 0.29 |
       | background, either option: largest per-cell median | 0.037 | 0.030 |
       | clipped variance ratio within 1 ± 0.2; median | 100 %; 1.022 | 97.1 %; 0.922 |
       | cells with clipped variance ratio below 0.9 | 10 | 54 |
       | multiplicative composition: variance ratio within 1 ± 0.2 | 80.0 % | 97.6 % |
       | the fixed reading | option (1) | option (1) |

       The nominal efficiency ε_c over the 205 cells runs from 0.042 to 0.900, median 0.803.
     - **Joseph's ruling:** "Option 1, both tests (Recommended)" (`DECISION-20261103-joseph-coverage-clip-rule.md`),
       applied in §4.2, §5.2 and §6 (ii).
3. **Control (2a)**, the writer, and **(2b)**, E_R reproduced (§2).
4. **The truth computation.** At the CV nature (no universe, r = 1), the toys' truth code gives E_R's own
   `hTruthXSec2D` to 10⁻¹² relative, or INVALID.
5. **The blocks' code.** Applied to part B's own products, the imported block functions reproduce part B's S5_R blocks
   (`s5/production_cov.npz`, sha256 `631cf255…`, `RE2/RE2-PARTC-REPORT.md:131`) to 10⁻¹².
6. **The single-universe nature.** `cov2d.compose` with one universe gives that universe's arrays bitwise (a test now;
   a control in the amendment for MaRES_0, Flux_0 and GEANT_Pion_0 on the real bank).
7. **The null:** `check_matched` at 10⁻¹², computed and committed before the scorer opens any toy product.
8. **C_T** symmetric to 10⁻¹² and positive semi-definite at 10⁻¹² relative; ndf recorded.
9. **One code and one input set** across every product of a truth: driver sha256, data-file sha256 (the driver records
   it as `dataFileSha256`), argv, estimator seed. Every product names its truth, role and seed. The toys' seeds are
   exactly the declared ranges.
10. **The truth pins:** each ratio's sha256 equals F1's committed digest.
11. **The drawn pseudo-data's content,** in each pseudo-data job, for every file it writes. The file read back has
    exactly Σk rows; its per-reco-cell histogram equals the per-cell sum of the counts k; and every row's
    (`measured`, `measured_pz`) is a reco-passing row's (`sim`, `sim_pz`). At the CV nature (d̃_T), the total is also
    within 5 Poisson σ of Σλ⁺.
12. **The universe and lateral routes,** in the pilot. One universe unfold, `--omnifile $UNI --universe MaRES:0`, and
    one lateral unfold, the first lateral omnifile of part B's J3, each with `--data-file` set to control (2a)'s file
    (`$CV`'s own data), must reproduce part B's product for that run to ≤ 1e-8 relative on the 205 cells, under (2b)'s
    rule. Each part B product's sha256 is checked against `RE2/run/partb_readout/sums` before it is read, through
    `O_NOATIME`. A missing product is INVALID. About 0.3 node-h, inside the pilot's reserve.
13. **A failed run.** No toy or block run is dropped, replaced or re-seeded. A crash, OOM, kill or time-out is INVALID
    and goes to the director, as the standing rule says, who decides whether it is rerun with the same inputs.

## 10. Order, connects and schedule

The director is told before each connect and each submission.

1. **The receipt** (§9.2), on a login node, before the audit. Its result enters §9.2.
2. **The audit:** a fresh Sonnet subagent, its prompt and answer committed verbatim, findings answered.
3. **This binding** (binding 1). Then control (2a) on a login node, and staging from a DTN.
4. **The amendment:** the toy, block, truth, null-input and scorer code, with tests and a mutation receipt; then the
   audit and **binding 2**.
5. **The pilot** (≤ 2.0 node-h): controls (2b) and §9.12; x̂_T and one universe, one replica, one lateral and one toy at G18; one
   lateral reading CFS directly (§8). Its readout goes to the director before the bulk.
6. **The bulk:** both pseudo-data jobs first, then the universe jobs (the `$UNI` readers), then the rest.
7. **The readout, the report,** HPSS when available, and through the director to Joseph.

**The schedule against 2026-12-19:**

| step | target | latest |
|---|---|---|
| binding 1 | 2026-11-06 | 2026-11-20 |
| staging done | 2026-11-08 | the bulk's latest submission, 2026-12-01 (else laterals carried, §4.4) |
| binding 2 | 2026-11-16 | 2026-11-27 |
| pilot readout | 2026-11-18 | 2026-11-29 |
| **every `$UNI`-reading job submitted** | 2026-11-19 | **2026-12-01** |
| every `$UNI`-reading job done | 2026-11-22 | **2026-12-12**, a week before `$UNI`'s exposure |
| the rest done, readout | 2026-11-26 | 2026-12-18 |

- **If a `$UNI`-reading job cannot be submitted by 2026-12-01, (c) does not start its bulk** and reports that it cannot
  finish before 2026-12-19. No partial ensemble is graded.
- Binding 2's latest date is seven days after binding 1's. The amendment's code is written while binding 1 is pending,
  so those seven days are for its audit and binding only.
- The universe jobs take about 5.3 h each on one node (part B's J2). The latest dates allow about ten days of queue
  and one resubmission.

## 11. Code

**Bound now, by blob digest** (the digests are in the PR's last commit; the binding records them):

| file | what | tests | mutation |
|---|---|---|---|
| `2d-unfolding/re2/re2_driver.py` | the `--data-file` hook, 21 lines added to blob `4c7e9d75` (part B's, deploy `dbdad2f9`) | `re2/tests/test_re2_data_file.py`: 4 passed; `test_re2_driver.py`: 9 of 9 still pass (`R/hook/tests_hook.out`) | `R/hook/mutation_hook.{py,out}`: 8 of 8 killed |
| `2d-unfolding/cov2d/cov2d.py` | bank, draws, first-order composition, N1, λ⁺, the weakened cells and the outlier cell (§5.2) | `cov2d/tests/test_cov2d.py`; the three test files, 40 passed (`R/code/tests_cov2d.out`) | `R/code/mutation_cov2d.{py,out}`: 38 of 38 killed over the three files |
| `2d-unfolding/cov2d/cov2d_receipt.py` | the composite-weight receipt (§9.2) | the same file | the same |
| `2d-unfolding/cov2d/cov2d_writer.py` | the writer and control (2a) | `cov2d/tests/test_cov2d_writer.py` | the same |
| `nd-unfolding/fd_1b_null.py` | the null and the rule, imported unchanged at 205 cells | its own (1B), plus `cov2d/tests/test_null205.py` | 1B's `mutation_null.out` |

- **The hook's absent-flag path.** The test runs the pre-hook blob `4c7e9d75`, extracted from git, and the hooked
  driver on one synthetic omnifile in the production configuration. On the CV, a universe and a three-stream replica,
  every histogram is bitwise equal, and every record is equal except the driver's own path and digest and runConfig's
  new `"data_file": null`.
- **The hook's present-flag path.** Other data through `--data-file` gives every histogram bitwise equal to the
  pre-hook driver run on an omnifile whose data tree is that data (CV, universe, three-stream). The output records
  `dataFileSha256`. The guards refuse a missing or different `dataPOTUsed`, a missing data tree, and `--closure`.
- **The tests ran locally** under conda-forge ROOT 6.28/12, LightGBM 4.5.0, scikit-learn 1.5.1 and uproot 5.6.9. The
  binding re-runs them in the cluster's `root_6_28` environment.

**Still to come, in the amendment:** the pseudo-data job (truths, composition per draw, the writer, the truth per toy,
the clipping records), the block assembly (importing the rollup's functions), the null's inputs, the scorer, the
readouts of §6, and the job scripts. It imports `cov2d`, `cov2d_writer`, `fd_1b_null`, `s5e_deform`, `re2_driver` and
`re2c_rollup` rather than copying them. If any rule here proves unimplementable as written, that is an amendment, not a
silent change.

## 12. The paper and the note, in each outcome

The redesign decision (item 4) governs the wording: one neutral methods sentence, no "does not test" clause, the
required facts stated as description, and the text drafted by the paper lane when the result lands, read by a PRD
referee and by Joseph before merge. **What each outcome must say is fixed now:**

- **The method,** in every outcome: 300 pseudo-experiments at each of two held-out GENIE v3 tunes, the uncertainties
  propagated linearly as in the covariance's construction, and the covariance rebuilt by the same procedure at each
  tune.
- **The facts, as description,** in every outcome:
  - G18_10a_02_11b shares its 2p2h model family with one of the model term's generators;
  - the result concerns the procedure's covariance at those tunes, not the reported intervals at the data;
  - the run-period block was not drawn.
- **Both COVER:** each tune's χ²/ndf and per-cell content range.
- **One or both UNDER-COVER:** the tune, the flagged cells, the under-coverage factors, bias or width per cell, and the
  test's false-flag rate under its null's law (at most 0.05 per tune, 0.10 over both; §5.2 states the departures).
- **INVALID, a STOP, or no result:** the paper is unchanged.
- **In every outcome** the earlier fixed-truth failure stays in the consolidated Limitations statement (#690 item 2),
  and (c)'s result does not replace it (§13).
- **To the note** (redesign decision item 4): the ±1σ endpoint draws, the shared universes, the cross-term readout,
  the single realization behind the remade blocks, the toys' fixed simulation, C08 carried, and the resolution of §5.2.
- **To the note, from the clip-rule decision (item 4), in every outcome:**
  - the clipping rule: negative composites zeroed row by row in the pseudo-data, the graded truth and the background
    (§4.2), with C2's measured residual and the toys' (§6 (ii));
  - the outlier cell 216, p_T 2.5–4.5 GeV/c, p_∥ 6–7 GeV/c, named, with its |R| maximum from C2 (4.27 σ_Q at each
    tune) and from the toys;
  - the expected lean toward over-coverage where clipping narrows the spread, a false-pass risk, with the weakened
    cells of §5.2 and how each read.
  - None of these goes to the paper (redesign decision item 4).

## 13. What (c) can and cannot license (scoping §5–§6)

**MEASURES:** per tune, §5's statistics and reading; §6's readouts.

**CAN license**, if both tunes COVER: a sentence of the form "at two held-out generator tunes, the analysis procedure's
covariance, remade at each tune's truth with the model term included and the run-period term excluded, covered
pseudo-data drawn about that truth at least at the nominal rate, per bin and jointly", worded by the paper lane under
§12. Its limits, stated with it in the report and the note:
- **The graded matrix is C_T** (§4.4): the drawn blocks plus C08 and C_model_abs. C_model is not drawn. At the data it raises
  the median per-cell relative σ from 6.41 % (Q_R) to 7.90 % (`RE2/RE2-PARTC-REPORT.md:254-258`), about 23 %. So a
  pass can hide a shortfall of roughly that size in the drawn blocks. §6's
  spread-alone readout, against C_T without C_model, shows it, and the report gives it beside the verdict.
- **The test is one-sided**, so a pass bounds coverage from below only.
- Where cells pass weakened (§5.2), the report and the note say so beside it. The label does not change the verdict.

**CANNOT license:**
- **Removing the earlier fail.** The fixed-truth test of the earlier statistical band VL162 failed: C2 = 0.9121
  against the window [0.9281, 0.9722] at 100 toys (`OUTCOME-20261005-2d-fixed-truth-coverage-fail.md:35-42`). #690
  item 2 keeps it. (c) tests a different band under a different estimator and does not re-test it.
- **Coverage of Q_R at the data's point.** Q_R is made at the data, not at T.
- **A coverage rate,** or coverage at truths unlike these two.
- **Simultaneous coverage** beyond the declared joint region.
- **Anything about C_PL_R or C_model.** Neither is drawn.
- **Independence from the training rows.** In the director's words, carried verbatim: "A held-out tune moves the truth,
  not the sample." The natures are drawn on the same simulated rows the unfolding trains on (scoping P4).

## 14. For the director

1. **Your rulings of 2026-11-02, as applied here:** $UNI as the basis and control (1) first (§2); option (2), the hook,
   with the absent-flag path unchanged and pinned (§4.3, §11); the two-part control (§2); the blocks at T from one
   realization with its seed declared and the realization check (§4.4, §6); remade laterals with the I/O priced and
   the fallback fixed by date (§4.4, §8); option (a) for atime (§7); the two-step binding (§10–§11); no projection
   (§4.1).
2. **To rule on, at binding 1** (your message of 2026-11-03): §6 (ii)'s substitute for the mean unfold, which 2D
   cannot run, namely C2's first-order residual R_c taken per toy at the nature's expected counts, and its reading.
   The audit (finding 2) notes that C2 predicts the 0.5 σ_c reading will not fire. The threshold was fixed before any
   clipping probe ran, and I have not changed it after C2. Keeping it, or replacing it, is your ruling.
3. **To note:** the toys do not resample the simulation (§4.2), a known difference that can only widen C_T against the
   errors; C08 is carried (§4.4); no plug-in truth (§4.1).
4. **The receipt** (§9.2) ran before the audit, with your approval of the connect: PASS.
5. **The clipping probes and Joseph's ruling** (§9.2): C1 and C2 ran with your approval, C1's offsets carry my
   erratum, and C2's fixed reading gave option (1) at both tunes. Joseph ruled "Option 1, both tests (Recommended)"
   (#718). Applied: consistent clipping (§4.2); your weakened-pass reading below 0.9 with the cells fixed from C2
   (§5.2); the outlier cell named, with its |R| maximum reported (§5.2, §6 (ii)); the clipping, the outlier and the
   over-coverage lean to the note (§12).
6. **How "consistent" is read: confirmed by you** (2026-11-03, by message), with a clarification to the decision
   record to follow from you. The decision says "a signal row with a negative composite weight
   is zeroed in both the pseudo-data and the graded truth". The signal and truth trees are separate, row-matched trees
   (C2: 0 unmatched), and a row's reco composite w_reco,D and truth composite w_truth,D differ (the receipt counts
   11,358,837 rows negative in some draw for `w_reco` against 12,440,871 for `w_truth`; no cause is asserted). §4.2
   clips each tree on its own composite, which is what C2 measured as option (1) and what its R_c is the residual of.
   Zeroing both trees on the reco composite alone would be a different rule, and C2 did not compute it.
   Search: `git grep -lE "clip.*(reco composite|w_reco.*truth)|zero(ed)? (in )?both trees|clip-rule nature|clipcheck" -- docs nd-unfolding 2d-unfolding` @ bc4965c4 (one hit, 1B's mutation_mc.py, a mutant that clips w_truth; no record computes the reco-only rule)
7. **The rule in code.** `cov2d.py` now holds `WEAKENED_BELOW`, `OUTLIER_CELL` and `weakened_cells`, with tests on
   C2's committed record and new mutants (§11). The truth-side clipping itself is the amendment's truth code, through
   `cov2d.lam_plus`.
8. **The audit** (§10 step 2): a fresh Sonnet subagent, `R/audit/PROMPT.txt` and `ANSWER.txt` verbatim, verdict
   "READY AFTER MINOR FIXES", no BLOCKING finding. Each of its 12 findings has a disposition in `R/audit/DISPOSITIONS.md`.

Nothing is submitted, deposited or tagged.
