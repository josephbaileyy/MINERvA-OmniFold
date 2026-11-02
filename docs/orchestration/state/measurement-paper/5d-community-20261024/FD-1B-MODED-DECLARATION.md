# DECLARATION 1B redesigned test: mode D, with the grid check (2026-11-01)

**By** the measurement session `coverage-5b`, for `coverage-5b-audit` to review and the director to bind.

**Under:**
- `DECISION-20261101-joseph-1b-keep-block-redesign-test.md` (#654, main `b20d6deb`), item 3;
- `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`, for the cap;
- [`FD-1B-INV-I2-DIRECTOR-REVIEW.md`](FD-1B-INV-I2-DIRECTOR-REVIEW.md) and its consult (#652), for the labels.

**What it asks.** Does a pseudo-experiment in which nature is the universe, unfolded with the nominal simulation,
realize the object S1's interaction block describes?

Nothing runs before the director binds this. No connect is made before the binding, not even a stat-only one.

**Labels.** Following the review's §3:
- **B** is "response-only": the universe's reco-weight change with the truth held per fine cell.
- **A** is "S1's full universe at the nominal truth".
- **C** is "the cell-mean truth reweight".

"Prior part" is not used for any of them, because the data have not shown a prior.

## 1. Fixed by the decision, and unchanged here

- **The covariance.** The reported covariance keeps S1's full-universe interaction block. Mode D tests a toy design;
  it does not test the block.
- **Changes forbidden.** No toy, window or covariance change follows from D without Joseph. Changing any of them to
  make D pass is forbidden. No readout here feeds back into gate D, M_d, the window, the toys or the covariance.
- **If D passes,** the held-out-tune coverage ensemble may be declared, priced and bound, separately and after D's
  report. **Any other outcome** goes to Joseph.
- **Unchanged:** gate D's verdict, the diagnosis, I0, I2, every claim and number, and the paper's wording.

## 2. The object

For interaction universe u, mode D's pseudo-data are the simulation with u's event weights applied together.
- **The weights:** truth weights, reco weights, the completeness denominator and the background template become u's.
  These are exactly the arrays `s5p_universe.universe_inputs` gives S1's universe unfolds, which I2's mode A
  unfolded with, with non-finite weights zeroed as S1's loader does.
- **The draws:** every Poisson draw is at its mean.
- **The unfolding:** the nominal simulation is the unfolding MC (truth and reco weights, denominator and background
  template all CV). The estimator, configuration, iterations and seed are the derivation's and I2's: `unfold_negweight`
  with `toys.CONFIG`, `toys.ITERS` and `toys.ESTIMATOR_SEED`. I2's three CV controls showed these reproduce the
  derivation CV bitwise.
- **The product** stores the unfolded result x̂_D(u) and the universe's own truth T_u. T_u is `true_xsec` over u's
  truth weights and u's denominator, at the same truth weight r.

**The per-universe object is the error e(u) = U x̂_D(u) − U T_u, in the 16 reporting cells.**
- **The block** is formed from e(u) with S1's estimator, `s1_assemble.mat_cov` (mean-centred, 1/N), per band. It is
  then summed over the 33 interaction bands, as M is.
- **Why the error and not the raw shift** x̂_D(u) − x̂_D(CV):
  - the raw shift contains the universe's own truth movement T_u − T_CV. For an unbiased estimator it is all truth
    movement, and S1's block would then be zero;
  - the error is what a coverage ensemble with nature = universe grades (x̂ − T, decision item 4).
- **The raw-shift block and the truth-spread block** are printed beside it, as descriptive readouts (§6). The
  director may rule otherwise (§12, item 1).

**Expectation (inference, not measured).** To first order, swapping which side carries the universe flips the
error's sign and keeps its size:
- unfolding u's nature with the CV MC (D);
- unfolding the CV nature with u's MC (S1, and I2's A).

The pair estimator does not see the sign. The departure from this first-order picture is what D measures.

## 3. At which truth: the data-like truth for the rule, the nominal truth as a matched control

**The rule compares D at the data-like truth (Ddl) with M.** The reasons:
- **M is made at the data.** I2 measured S1's mechanism at the nominal truth against M, carried: F_truth = √(A/M) has
  median 0.683 and is outside the window in 15 of 16 cells.
- **So a D at the nominal truth would have no power to pass.** Even if it realized S1's mechanism exactly, it would
  be expected to depart from M by about F_truth, in 15 of 16 cells. Its comparison with M would measure the truth
  point, not the design.
- **The coverage ensemble** the decision names is drawn at a data-like truth. Ddl tests the object that ensemble
  would draw.

**The data-like truth.**
- **The factor:** each MC row whose truth lies in reporting cell c is weighted by r_c = f_c / (U x_T)_c, on truth and
  reco together. Here f is S1's data result (the S1 assembly) and x_T the nominal truth (the derivation CV product).
  Rows outside every reported cell keep weight 1. r_c is the same ratio f / x_T as gate D's carry g (I0's `g`). Here
  U is built from the definition, as in the job and the readout, so the two agree to the precision of U, not
  necessarily bitwise.
- **Its property:** a fine cell lies in exactly one reporting cell, and U sums fine-cell volumes. So the CV nature's
  truth equals f in every cell, exactly (a control, §8), and Ddl's object sits in the data's frame without a carry.
- **What stays nominal:** the within-cell truth shape, the detector response and the flux. **Not chosen:** a factor
  per fine cell from S1's unfolded fine result, which would put the fine result's statistical noise into the truth.

**The matched control: D at the nominal truth (Dnom) against I2's A,** uncarried (A / g², from `i2.json` and I0's `g`).
- Both are at the nominal truth. κ_c = √(Dnom_c / A_c) asks whether the swap reproduces S1's mechanism with the truth
  held equal. This is the comparison the consult proposed.
- κ has no verdict role of its own. Its fixed reading (§6) says what a non-PASS of the rule points to.

## 4. Readouts

**Per cell, interaction group:**
- **ρ_D = √(Ddl / M):** the rule's readout (§6).
- **κ = √(Dnom / A_uncarried):** the matched-truth reading (§6).

**Descriptive** (no verdict role):
- √(raw-shift block / M), and √(truth-spread block / M);
- √(Ddl / Dnom), D's own truth dependence, beside I2's F_truth = √(A/M);
- per band, √(Ddl_b / M_b);
- the largest off-diagonal difference between the correlation matrices of Ddl's full 16 × 16 block and M. The rule
  reads diagonals only; this shows the correlation structure.

## 5. The grid check

**The question.** It tests the consult's hypothesis (Q3) that B depends on the fine-cell grid on which its truth is
held. It feeds the note's label for B (decision item 1) and has no outcome role.

**The modes.**
- **What runs:** I2's B (response-only) and C (cell-mean truth reweight).
- **What changes:** only their factor grid, meaning B's truth-preserving factor g_f and C's fine-cell mean r.
- **What stays on the analysis grid:** the unfolding, C's denominator factor and the extraction.

**The grids, named in advance** (axes pt, pz, eavail, q3, W; `s5p_stage1_inspect.FINE`):

| grid | rule | cells |
|---|---|---:|
| coarse | every second fine edge, plus the last edge and every H2 edge, so that no coarse cell straddles a reporting cell | 7 × 8 × 4 × 4 × 4 = 3,584 |
| nominal | the fine grid; I2's own construction | 14 × 16 × 7 × 7 × 6 = 65,856 |
| fine | every fine cell halved at its midpoint on every axis | 65,856 × 32 = 2,107,392 |

**The six universes, named in advance:**
- MaRES_0, MvRES_0, Rvp2pi_0, Theta_Delta2Npi_0 and MaCCQE_0: the five bands with I2's largest per-band residual
  medians (I2 report §4.3);
- FrAbs_pi_0: among the smallest residuals (0.14), with A/M near 1.

**The runs.** Each of the six runs in B and C on all three grids: 36 unfolds.
- **The control:** the 12 nominal-grid products must equal I2's B and C products for the same universes bitwise
  (§8). The nominal grid therefore runs through the same code path as the other two.

**The readout,** per mode and per cell, over the six universes, with S = Σ_u (U x̂(u) − U x̂_CV)²:
- γ = √(S_coarse / S_nominal);
- φ = √(S_fine / S_nominal).

**The fixed reading:**
- **"Depends on the grid":** γ or φ is outside [0.9, 1.1] in at least 8 of 16 cells.
- **"Supports the sub-cell hypothesis":** γ > 1.1 in at least 8 cells AND φ < 0.9 in at least 8 cells. That is, B
  grows as the grid coarsens and shrinks as it refines.
- Otherwise the reading is "not shown to move with the grid at this level". C is read the same way.

## 6. The rules and the outcome table, fixed before any number is read

**Rule D.** It is read on ρ_D over the 16 cells, with the window [0.9, 1.1] and edges inside:

| rule D | condition | reading | next |
|---|---|---|---|
| **PASS** | ρ_D in the window in all 16 cells | at the data-like truth, nature = universe unfolded with the nominal simulation realizes S1's interaction block, cell by cell, on the diagonal | the coverage ensemble may be declared, priced and bound, after D's report |
| **PARTIAL** | in the window in 8 to 15 cells | it realizes S1's block except in the named cells | to Joseph |
| **FAIL** | in the window in fewer than 8 cells | it does not realize S1's block | to Joseph |
| **INVALID** | any control in §8 fails | none | reported unrepaired, to the director |

**The matched-truth reading.** It is fixed, it is printed with every outcome, and it is not a verdict:
- κ is **"matched"** if it is in the window in at least 8 of 16 cells, and **"unmatched"** otherwise.
- **With PARTIAL or FAIL and "matched":** the swap reproduces S1's mechanism at matched truth. The gap to M then
  follows the change of truth point: the data-like construction (§3) against the real data.
- **With PARTIAL or FAIL and "unmatched":** the swap does not reproduce S1's mechanism even at matched truth.
- **With PASS and "unmatched":** the PASS stands, and the report states the disagreement beside it.

**R00 and R05.** Both are graded as every other cell. Neither is exempt, and neither is counted twice. A cell out of
the window there makes a PARTIAL like any other.
- **What D covers there:** D tests the interaction group only. In gate D, the interaction group carried 0.57 of
  ρ_c² − 1 in R00 and 0.36 in R05 (I2 report §3), and the rest lies in other groups, chiefly flux.
- **So:** a D PASS in R00 or R05 says nothing about that rest. It stays open, and the coverage ensemble (which draws
  flux and detector universes too) is where it would be graded.
- **For R05 in addition:** R05 is I2's H3 cell (F_truth 0.632). The report prints R05's ρ_D, κ and √(Ddl/Dnom)
  beside its F_truth, as readouts.

**Estimator noise (inference).**
- D's pseudo-data are means, so D's block carries no draw noise. Its rounding noise is bounded by I0's.
- I0 found that removing every noise-consistent term moved ρ² by at most 0.029, on the data side, where the floor
  is largest.
- No noise correction is applied to ρ_D.

## 7. Price

**The measured costs, with their sources:**

| path | measured | source |
|---|---|---|
| a change on the pseudo-data side, nominal MC (D's path) | largest `seconds_unfold` 801.4 s; largest `seconds_load` 16.0 s | stage 2's derivation, [`FD-1B-STAGE2-REPORT.md`](FD-1B-STAGE2-REPORT.md) §2 |
| a change on the MC side (the grid check's B and C; also A) | 204 unfolds: median 725.1 s, max 849.6 s; peak RSS max 20,934,284 KiB | I2, `fd/receipts-1b/inv/i2/connect24-post-bulk.out` |
| I2's pilot, per item (A, B, C at MaRES_0: 837–850 s; CVs 691–693 s) | | `fd/receipts-1b/inv/i2/walls-i2-0.json` |

**The unit** is 1,062 s: 1.25 × 849.6 s, the largest measured on either path, with stage 2's 1.25 margin
(stage-2 report, the pilot median line). The RSS limit is stage 2's 44,040,192 KiB, 75 % of a lane's 56 GiB.

**The items:**
- 68 Ddl (67 universes and CV);
- 68 Dnom (67 and CV);
- 36 for the grid check.

That makes 172 in all, 8 lanes per node (32 CPUs, 56 G each), on CPU with QOS regular, `--exclusive --no-requeue`,
through the committed packer.

| step | nodes | items | limit | fullest lane at the unit | reserved = cap |
|---|---:|---:|---|---|---:|
| D-0, the pilot | 1 | 8, one per lane | 1:00:00 | 1,062 + 16 s | **1.0 node-h** |
| bulk | 3 | 164, at most 7 per lane | 2:30:00 | 7 × (1,062 + 16) = 7,546 s, 84 % of 9,000 s | **7.5 node-h** |

- **The cap is 8.5 node-h** in all, each step's reservation equal to its cap.
- **The expectation, as arithmetic at the measured median:** 172 × 725.1 s / 8 lanes is 4.33 node-h of lane time.
  Elapsed node-hours will be somewhat higher, because the lanes end unevenly.
- **The consult's estimate** of about 2 node-h is not used as a basis.
- **The re-price trigger:** after D-0, `fd_1b_moded.py walls` reads the eight pilot products. It returns PASS if the
  largest `seconds_unfold` is at most 1,062 s and the largest peak RSS at most 44,040,192 KiB. Otherwise it returns
  REPRICE, exit 1, and a REPRICE is an amendment. The pilot's eight items: Ddl CV, Dnom CV, Ddl MaRES_0, Ddl 2p2h_0,
  Ddl LowQ2_1, Dnom MaRES_0, B fine MaRES_0 and C fine MaRES_0. They count toward the 172 and are not rerun.
- **The balance.** The last read was `iris` at 2026-11-01 19:27Z (I2's connect 21): m3246 at 17,930.6 of 20,000.0
  charged, so 2,069.4 remain and half is 1,034.7. 8.5 node-h is far below that. The first connect re-reads it (§9).
  A balance under 17 node-h would make 8.5 more than half of it, and the campaign would go to Joseph, through the
  director, before any submission.
- **Storage:** an HPSS copy of the products, logs and readouts at each step's end, with `hpssquota` read before each
  put. I2's 204 products with their logs came to 44 MB. Nothing goes to CFS.

## 8. Controls

Any failure reads INVALID and is reported unrepaired.
- **Dnom at CV** equals the derivation CV product's `xsec_flat` bitwise.
- **Ddl at CV:** U T_CV / f − 1 is at most 10⁻¹² in every cell. In each Ddl job, U x_T of the run's own nominal truth
  equals the `U_xT` the factors were made against, exactly.
- **The nominal-grid B and C products** for the six universes equal I2's products bitwise.
- **M,** S1's interaction diagonal from the staged assembly, equals `i2.json`'s M bitwise.
- **One code and one input set** across all 172 products: `code_sha256`, the input, background and pins digests,
  configuration, iterations and estimator seed. Every Ddl product carries the data-like truth's digest.
- **Every product names its own** mode, grid, universe and truth.
- **The pins:** every universe's weight files carry the stage-2 pins file's digests.
- **Reads:**
  - every input not made by this lane is read with `O_NOATIME`, as are the staged copies and I2's products;
  - EPERM is raised, never retried as a plain read;
  - each job writes an atime sidecar and exits with 8 set if an atime moved, which is a deviation, reported
    unprompted and not restored.

## 9. Connects and order

1. **Connect 25 (after the binding):** `stat` of every input, `iris` and `hpssquota`. The inputs are:
   - I2's inputs: the inputs npz, the background dump, the 67 universes' weight files and `cv.npz`, the detector
     dump and the pins;
   - the staged S1 assembly and derivation CV copy in `fd-1b-inv-20261101/i0/in`;
   - I2's products in `fd-1b-inv-20261101/i2/unf`.
2. **Connect 26:**
   - a fresh clone detached at the binding's merge, with empty porcelain, under `$W = $P/fd-1b-moded-20261101`;
   - `dltruth` on login37 under `nice -n 19`;
   - the task tables, round-robin by mode, made by a committed generator;
   - D-0's submission, whose line goes to the director first.
3. **D-0's readout goes to `coverage-5b-audit` and the director before the bulk is submitted** (the director's
   ruling on #652). The bulk follows only on `walls` PASS.
4. **After the bulk:** `readout` on login37, then the HPSS copy, then D's report. D's report goes to the audit and
   the director before anything further is declared.

The rules are those of the binding I2 ran under:
- jobs under 12 h, CPU only, QOS regular, nothing to CFS;
- the director is told before each connect and each submission.

## 10. Code, tests and review

**The code:**
- `nd-unfolding/fd_1b_moded.py`, blob sha256 `66562a7789b23febcc324b1abea54b79e66200c9c10a161aaed2b09d0dffa85c`;
- it imports `fd_1b_inv.py`, unchanged at `71b3903a…`, which I2 ran;
- its subcommands are `dltruth`, `unfold` (Ddl, Dnom, B or C with `--grid`), `walls` and `readout`.

**The tests:** `nd-unfolding/tests/test_fd_1b_moded.py` has 30 tests. Each rule is tested in the direction it acts
and in the other:
- **grids:** coarse keeps every H2 edge and nests in the fine grid; fine halves every cell;
- **the grid check:** B and C at the nominal grid are I2's modes bitwise, and another grid changes them;
- **the D experiment:**
  - at CV and r = 1 it is the derivation's CV experiment bitwise;
  - its pseudo-data are the universe's weights × r, and its unfolding MC is the CV's;
  - the data-like factor rescales each cell's truth exactly;
- **the jobs:**
  - the Dnom CV product is the derivation's bitwise;
  - the Ddl job applies its factors, and refuses without them, with a wrong digest, or against another nominal
    truth;
  - each refusal is asserted by its message;
- **the rules at their edges,** with R00 and R05 not exempt;
- **the readout end to end:** D equal to S1 passes, and D at 1.2× S1 fails. Every control refuses, and the readout
  reads with `O_NOATIME` only.

**The mutation receipt.**
- [`fd/receipts-1b/moded/mutation.py`](fd/receipts-1b/moded/mutation.py) and `mutation.out`: 32 of 32 mutants are
  killed, and the unmutated suite passes 30 of 30.
- The first run had a survivor, "Ddl's factor not applied". It is killed by an added test that the Ddl job's CV
  truth is r_c × (U x_T)_c.
- The first run's runner also measured its "unmutated" line before restoring the source, so against the last
  mutant. The committed runner restores first.

The neighbouring suites `test_fd_1b_inv.py` and `test_fd_1b.py` pass, 117 tests.

## 11. What D's report will and will not be able to say

**MEASURES:** rule D on ρ_D, the matched-truth reading κ, the grid readings, and the descriptive readouts, all
labelled DERIVATION.

**CANNOT SUPPORT, whatever the outcome:**
- **Coverage, in either direction.** Only the held-out-tune ensemble can remove the qualification (decision item 4).
- **The flux and detector groups:** D draws neither.
- **The correlation structure:** the rule reads diagonals, and correlations are descriptive only.
- **That the data-like truth is the data:** only the per-cell truth is data-like. The within-cell shape, the detector
  and the flux are the simulation's.
- **That S1's block is right or wrong.** D tests a toy design.

## 12. For the director to rule

1. **The per-universe object.** The error e(u) = U x̂_D(u) − U T_u (§2), with the raw shift and the truth spread as
   descriptive readouts. Or the raw shift as the rule's object?
2. **The truth.** The rule at the data-like truth (Ddl against M), with Dnom against A as the matched control (§3).
   And the data-like truth's construction: a factor per reporting cell, r_c = g_c.
3. **The outcome table** (§6): PASS at 16 of 16; PARTIAL at 8 to 15; FAIL below 8; κ's reading; R00 and R05 graded
   as every cell.
4. **The grid check** (§5): the three grids, the six universes and the reading.
5. **The caps:** D-0 1.0 and bulk 7.5, so 8.5 node-h, with the unit 1,062 s and the re-price trigger.
6. **D-0's routing** (§9.3): once D-0's readout has reached both the audit and the director, is the bulk submitted on
   `walls` PASS without waiting for a reply? Or does it wait for the audit's acknowledgement?
