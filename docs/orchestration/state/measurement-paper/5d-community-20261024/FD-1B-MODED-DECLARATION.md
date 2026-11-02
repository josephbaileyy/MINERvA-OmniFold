# DECLARATION 1B redesigned test: mode D, revision 1 — the symmetry test κ, with the grid check (2026-11-01)

**By** the measurement session `coverage-5b`, for `coverage-5b-audit` to review and the director to bind. Under the
director's ruling on B1, the choice of rule goes to Joseph with its price before anything runs (§12).

**Under:**
- `DECISION-20261101-joseph-1b-keep-block-redesign-test.md` (#654, main `b20d6deb`), item 3;
- `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`, for the cap;
- [`FD-1B-INV-I2-DIRECTOR-REVIEW.md`](FD-1B-INV-I2-DIRECTOR-REVIEW.md) and its consult (#652), for the labels.

**What changed from revision 0** (head `78816d81`), after `coverage-5b-audit`'s review on #655 and the director's
rulings:
- **B1.** The rule is no longer D at a data-like truth against S1's block M.
  - §3 shows that no nature construction compared with M has first-order power to pass: the swap identity holds at
    first order only on the closure diagonal, and M is made off it.
  - The rule is now **κ: D at the nominal truth against I2's mode A**, where first order fixes κ = 1 if the toy
    realizes S1's mechanism.
  - D at the data-like truth (Ddl) is an **option**, descriptive only, priced separately (§3.4).
- **M1.** κ is read per cell, and every outcome goes to Joseph.
- **M2.** The grid check prints its occupancy and does not count reporting cells where B vanishes by construction.
- **Minor.** m1: the mutation receipt records its digests and counts a kill only on a test failure. m2: the
  background is named in what the data-like truth leaves unchanged.
- **The director's rulings 4 and 6:** a grid-control failure is INVALID for the grid part only, and the bulk waits
  for the audit's written acknowledgement.

**Nothing has run, and no connect has been made.**

**Labels.** Following the review's §3, "prior part" is not used:
- B is "response-only": the universe's reco-weight change with the truth held per fine cell.
- A is "S1's full universe at the nominal truth".
- C is "the cell-mean truth reweight".

## 1. Fixed by the decision, and unchanged here

- **The covariance.** The reported covariance keeps S1's full-universe interaction block. Mode D tests a toy design;
  it does not test the block.
- **Changes forbidden.** No toy, window or covariance change follows from D without Joseph. Changing any of them to
  make D pass is forbidden. No readout here feeds back into gate D, M_d, the window, the toys or the covariance.
- **Any coverage ensemble** needs its own declaration and binding, and Joseph's decision first (§6).
- **Unchanged:** gate D's verdict, the diagnosis, I0, I2, every claim and number, and the paper's wording.

## 2. The object

For interaction universe u, mode D's pseudo-data are the simulation with u's event weights applied together.
- **The weights:** truth weights, reco weights, the completeness denominator and the background template become u's.
  These are exactly the arrays `s5p_universe.universe_inputs` gives S1's universe unfolds, which I2's mode A
  unfolded with, with non-finite weights zeroed as S1's loader does.
- **The draws:** every Poisson draw is at its mean.
- **The unfolding:** the nominal simulation is the unfolding MC. The estimator, configuration, iterations and seed
  are the derivation's and I2's (`unfold_negweight`, `toys.CONFIG`, `toys.ITERS`, `toys.ESTIMATOR_SEED`).
- **The product** stores x̂_D(u) and the universe's own truth T_u: `true_xsec` over u's truth weights and u's
  denominator.

**The per-universe object is the error e(u) = U x̂_D(u) − U T_u, in the 16 reporting cells.**
- **The block** is formed from e(u) with S1's estimator, `s1_assemble.mat_cov`, per band, then summed over the 33
  interaction bands.
- **Why the error** (the director's ruling 1): the raw shift x̂_D(u) − x̂_D(CV) contains the universe's own truth
  movement. For an unbiased estimator it is all truth movement, and S1's block would then read zero.
- **The raw-shift and truth-spread blocks** are descriptive.

## 3. Which comparison has power, and why the rule is κ

### 3.1 The identity

Take the readouts' definitions:
- ρ_D = √(Ddl / M);
- κ = √(Dnom / A_unc), with A_unc = A / g²;
- I2's F_truth = √(A / M), with A carried by g = f / x_T;
- λ = √(Ddl / (g² · Dnom)).

Then, exactly, **ρ_D = λ · κ · F_truth** (audit B1). The readout checks it to 10⁻¹².

### 3.2 First order: the swap holds only on the closure diagonal (inference, not measured)

**The closure identity.** Write the unfolding of reco d with simulation m as U(d; m), and the reco a model m predicts
as d(m). The estimator closes on its own simulation: U(d(m); m) = T(m) for every m.

**On the diagonal** (nature = simulation = the nominal m₀), take a universe Δ. Linearising the closure gives
∂_d U · Δd + ∂_m U · Δm = ΔT. So:
- D's error, ∂_d U · Δd − ΔT, is −∂_m U · Δm;
- that is minus S1's mechanism at the nominal truth, which is I2's A shift.

**So κ = 1 at first order if the toy realizes S1's mechanism.** Departures are of second order in the universe's
size, the ±1σ non-linearity. The pair estimator does not see the sign.

**Off the diagonal.** M is made at (real data, m₀), where the data are not the simulation. The closure identity
constrains U only on the diagonal, so it fixes no first-order relation between D's error and S1's shift there.
- Their relation is set by second-order terms times the data's distance from m₀. That is the same order as whatever
  makes F_truth depart from 1.
- **In the linear limit** (every second-order term zero), λ = κ = 1 and F_truth = g, so ρ_D = g. A universe moves
  S1's simulation at the simulation's scale, but moves a data-like nature at the nature's scale, and the two differ
  by g per cell.
- **Arithmetic on I0's committed `g`:** 4 of 16 cells lie in [0.9, 1.1]. So even an estimator with no second-order
  term would read FAIL against M, from the scale alone.

### 3.3 What a nature construction could reach (the audit's checklist)

F_truth's departure can come from three places:
- **(i)** the truth shape within cells;
- **(ii)** data-versus-simulation differences at reco level that the truth does not explain;
- **(iii)** the shift's dependence on the data's particular draw.

| construction | (i) | (ii) | (iii) | status |
|---|---|---|---|---|
| per-reporting-cell reweight r_c = g_c (revision 0) | no | no | no | built; it moves cell totals only |
| the unfolding's final truth-level weights at S1's data result (the director's candidate a) | yes | only as far as the unfolding's own fit | no: pseudo-data at means | not available: `unfold_negweight` returns only the binned result and its parameters, so building it needs a change to the production unfold core (`s5c_unfold.unfold`) |
| any construction at means | — | — | no | (iii) is out of reach of every pseudo-data at means |

**What this leaves.**
- None of I0's or I2's declared readouts separates (i), (ii), (iii) and the second-order term in F_truth. So I cannot
  say that F_truth comes mostly from what any construction reaches. <!-- absence-ok: scoped to the declared readouts
  of I0 and I2, which their reports list in full (FD-1B-INV-I0-REPORT.md, FD-1B-INV-I2-REPORT.md); no search claim -->
- Even a construction reaching (i) and (ii) would leave §3.2's off-diagonal argument and the linear-limit scale g
  standing.
- **So no construction compared with M has first-order power to pass.** Under the director's ruling, the rule
  becomes **Dnom against A only: κ, the symmetry question**.
- **The final-weights construction** is not built. Revision 0's objection would also apply to it: the weights carry
  the data's draw into the truth. That noise is common to all universes, and how far the pair estimator cancels it
  would itself need a control.

### 3.4 The Ddl option (descriptive, no verdict)

**What it is.** D at the data-like truth r_c = f_c / (U x_T)_c, the same ratio as gate D's carry g. It is built,
tested and kept as an option. It adds 68 unfolds.

**Its readouts,** with no verdict role:
- ρ_D, λ and the identity, per cell;
- λ's reading: "carry-like" if λ is in the window in at least 8 cells, "beyond the carry" otherwise;
- the correlation difference from M;
- per band, √(Ddl_b / M_b).

**What it would add.** λ says whether a per-cell data-like reweight acts as the carry. That is what any later
ensemble drawn at a per-cell data-like truth would rest on.

**What it would not add:** a test of the design (§3.2).

**What stays as the simulation's in Ddl:** the within-cell truth shape, the detector response, the flux, and the
background. r is applied to signal rows only, and the background is u's template.

**The control:** the CV nature's truth equals f in every cell to 10⁻¹², a hard INVALID (the director's ruling 2).

### 3.5 What κ can and cannot say

**A κ PASS shows** that the new toy, with nature as the universe, realizes S1's mechanism at the nominal truth. This
is the design question, at the one point where first order fixes the answer.

**It does not reach M.**
- The gap F_truth between S1's mechanism on the nominal pseudo-data and on the data remains. It is a property of S1's
  mechanism between the two points, and no pseudo-data at means reaches all of it (§3.3).
- Any coverage ensemble at a data-like truth would carry this gap. Whether to declare one is Joseph's decision.

## 4. Readouts

**Per cell, interaction group:**
- **κ = √(Dnom / A_unc):** the rule's readout (§6). A_unc is I2's A / g², from `i2.json` and I0's `g`.
- **I2's F_truth,** printed beside κ in every cell, with whether each lies in the window (M1).

**Descriptive:**
- √(raw-shift block / A_unc) and √(truth-spread block / A_unc), for Dnom;
- Dnom's diagonal per band;
- with the option, §3.4's readouts.

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
- **The control:** the nominal-grid products must equal I2's bitwise. A failure, or occupancy that differs between
  universes, makes the grid part INVALID and leaves rule K standing (the director's ruling 4).

**Occupancy (M2).** In a factor cell holding one truth-passing row, g_f = 1/k_wt, so B's factor there is k_wr/k_wt.
Where the universe's reco and truth ratios agree, B vanishes there by construction. Every grid product records:
- the occupied cells;
- the distribution of rows per occupied cell;
- the fraction of rows alone in their cell;
- per reporting cell, the fraction of its truth-passing rows that are alone;
- the per-row distribution of k_wr/k_wt, and the fraction of rows where it differs from 1.

**The readout,** per mode and per cell, over the six universes, with S = Σ_u (U x̂(u) − U x̂_CV)²:
- γ = √(S_coarse / S_nominal);
- φ = √(S_fine / S_nominal).

**The fixed reading:**
- **Construction-limited cells are not counted.** A reporting cell is construction-limited on a grid if more than
  half of its truth-passing rows are alone in their factor cell there.
- **"Depends on the grid":** γ or φ is outside [0.9, 1.1] in at least half of that grid's counted cells.
- **"Supports the sub-cell hypothesis":** γ > 1.1 in at least half of the coarse grid's counted cells AND φ < 0.9 in
  at least half of the fine grid's. A grid with no counted cell supports nothing.
- **The qualification:** φ < 0.9 is still expected partly from construction as occupancy falls, in the counted
  cells too. The coarse leg is the one less exposed to it. C is read the same way.

## 6. Rule K and the outcome table, fixed before any number is read

**Rule K.** It is read on κ over the 16 cells, with the window [0.9, 1.1] and edges inside:

| rule K | condition | reading | next |
|---|---|---|---|
| **PASS** | κ in the window in all 16 cells | nature = universe, unfolded with the nominal simulation, realizes S1's mechanism at the nominal truth, cell by cell, on the diagonal | to Joseph |
| **PARTIAL** | in the window in 8 to 15 cells | it does so except in the named cells | to Joseph |
| **FAIL** | in the window in fewer than 8 cells | it does not | to Joseph |
| **INVALID** | any control in §8 fails, except the grid part's | none | reported unrepaired, to the director |

**Every outcome goes to Joseph.** No outcome opens a coverage ensemble by itself: a PASS establishes the design at
the nominal truth, not the object M (§3.5).

**Per cell.** For every cell, the report states whether κ and F_truth each lie in the window.

**R00 and R05.** Both are graded as every other cell. Neither is exempt, and neither is counted twice.
- **What κ covers there:** κ tests the interaction group only. In gate D, the interaction group carried 0.57 of
  ρ_c² − 1 in R00 and 0.36 in R05 (I2 report §3). The rest lies in other groups, chiefly flux, which D does not draw.
  The report states that remainder.
- **For R05 in addition:** R05 is I2's H3 cell (F_truth 0.632). Its κ and F_truth are printed side by side.

**Estimator noise (inference).**
- Dnom's pseudo-data are means, so its block carries no draw noise.
- I0 measured the nominal rounding floor at σ_J/f median 0.011 %, against 0.133 % on the data. Even at the data's
  floor, removing every noise-consistent term moved ρ² by at most 0.029 (I0 report §4).
- No noise correction is applied.

## 7. Price

**The measured costs, with their sources:**

| path | measured | source |
|---|---|---|
| a change on the pseudo-data side, nominal MC (D's path) | largest `seconds_unfold` 801.4 s; largest `seconds_load` 16.0 s | stage 2's derivation, [`FD-1B-STAGE2-REPORT.md`](FD-1B-STAGE2-REPORT.md) §2 |
| a change on the MC side (B and C, also A) | 204 unfolds: median 725.1 s, max 849.6 s; peak RSS max 20,934,284 KiB | `fd/receipts-1b/inv/i2/connect24-post-bulk.out` |

**The unit** is 1,062 s: 1.25 × 849.6 s, the largest measured on either path, with stage 2's 1.25 margin. The RSS
limit is stage 2's 44,040,192 KiB. The run uses 8 lanes per node (32 CPUs, 56 G each), CPU only, QOS regular,
`--exclusive --no-requeue`, through the committed packer.

**As declared (κ and the grid check):** 104 items, 68 Dnom (67 universes and CV) plus 36 grid.

| step | nodes | items | limit | fullest lane at the unit | reserved = cap |
|---|---:|---:|---|---|---:|
| D-0, the pilot | 1 | 8, one per lane | 1:00:00 | 1,078 s | **1.0 node-h** |
| bulk | 2 | 96, at most 6 per lane | 2:15:00 | 6 × 1,078 = 6,468 s, 80 % of 8,100 s | **4.5 node-h** |

- **The cap is 5.5 node-h.**
- **The expectation, as arithmetic at the measured median:** 104 × 725.1 s / 8 lanes is 2.62 node-h of lane time.

**With the Ddl option:** 172 items. The bulk becomes 164 items on 3 nodes, at most 7 per lane, with a 2:30:00 limit
(7 × 1,078 = 7,546 s, 84 %). It reserves 7.5, so the cap is **8.5 node-h**, and the expectation is 4.33 node-h.

**The re-price trigger.** After D-0, `fd_1b_moded.py walls` reads the eight pilot products. It returns PASS if the
largest `seconds_unfold` is at most 1,062 s and the largest peak RSS at most 44,040,192 KiB. Otherwise it returns
REPRICE, exit 1, and a REPRICE is an amendment.
- **The pilot's items:** Dnom CV, Dnom MaRES_0, Dnom 2p2h_0, Dnom LowQ2_1, and B and C at MaRES_0 on the fine and
  coarse grids. The fine and coarse paths are the only ones not measured before.
- They count toward the total and are not rerun.

**The balance.** The last read was `iris` at 2026-11-01 19:27Z: m3246 at 17,930.6 of 20,000.0 charged, so 2,069.4
remain. The first connect re-reads it. A campaign above half the balance goes to Joseph, through the director,
before any submission.

**Storage:** an HPSS copy at each step's end, with `hpssquota` read before each put. Nothing goes to CFS.

## 8. Controls

Any failure reads INVALID and is reported unrepaired.
- **Dnom at CV** equals the derivation CV product's `xsec_flat` bitwise.
- **M,** S1's interaction diagonal from the staged assembly, equals `i2.json`'s M bitwise. The readout reads A and F
  from the same committed `i2.json`.
- **One code and one input set** across every product: `code_sha256`, the input, background and pins digests,
  configuration, iterations and estimator seed.
- **Every product names its own** mode, grid, universe and truth.
- **The pins:** every universe's weight files carry the stage-2 pins file's digests.
- **The grid part:** the nominal-grid B and C equal I2's bitwise, and occupancy is identical across the six
  universes. A failure is INVALID for the grid part only.
- **The Ddl option:**
  - the CV nature's truth equals f to 10⁻¹², a hard INVALID;
  - each Ddl job's U x_T equals the `U_xT` its factors were made against;
  - every Ddl product carries the data-like truth's digest.
- **Reads:**
  - every input not made by this lane, the staged copies and I2's products, is read with `O_NOATIME`;
  - EPERM is raised, never retried;
  - each job writes an atime sidecar and exits with 8 set if an atime moved, which is a deviation, reported
    unprompted and not restored.

## 9. Connects and order

1. **Connect 25, after the binding:** `stat` of every input, `iris` and `hpssquota`. The inputs are:
   - I2's inputs and the definition;
   - the staged S1 assembly and derivation CV copy in `fd-1b-inv-20261101/i0/in`;
   - I2's products in `fd-1b-inv-20261101/i2/unf`.
2. **Connect 26:**
   - a fresh clone detached at the binding's merge, with empty porcelain, under `$W = $P/fd-1b-moded-20261101`;
   - with the option, `dltruth` on login37;
   - the task tables, round-robin by mode, made by a committed generator;
   - D-0's submission, whose line goes to the director first.
3. **D-0's readout goes to `coverage-5b-audit` and the director.** The bulk is submitted only after:
   - `walls` reads PASS; **and**
   - the audit's written acknowledgement, as a PR comment or a message (the director's ruling 6).

   If no acknowledgement arrives within 2 h, the director is told and nothing is submitted.
4. **After the bulk:** `readout` on login37, then the HPSS copy, then D's report. D's report goes to the audit and
   the director before anything further is declared.

The rules are those of the binding I2 ran under: jobs under 12 h, CPU only, QOS regular, nothing to CFS. The director
is told before each connect and each submission.

## 10. Code, tests and review

**The code:**
- `nd-unfolding/fd_1b_moded.py`, blob sha256 `4bfc6e71eae9bfe694d0da59361b172807a4cba4c717a59615e43e89c4a93a43`;
- it imports `fd_1b_inv.py`, unchanged at `71b3903a…`, which I2 ran;
- its subcommands are `dltruth`, `unfold` (Dnom, Ddl, or B and C with `--grid` and `--definition`), `walls` and
  `readout` (with `--dl` for the option).

**The tests:** `nd-unfolding/tests/test_fd_1b_moded.py`, blob sha256
`a1110a3843773027fa35b1853fce2f78745eec748e5a922dd3ca5eb84ef7037a`, has 34 tests. Each rule is tested in the
direction it acts and in the other:
- **the grids,** with their cell counts and nesting;
- **the grid check:**
  - B and C at the nominal grid are I2's bitwise, and another grid changes them;
  - the occupancy statistics, including a third of the rows alone where half the occupied cells are;
  - construction-limited cells are not counted;
- **the D experiment,** at CV and for a universe, with the data-like factor rescaling each cell's truth exactly;
- **the jobs:**
  - the Dnom CV product is the derivation's bitwise;
  - Ddl applies its factors and refuses without them, with a wrong digest, or against another nominal truth;
  - the grid check refuses without `--definition` or outside its six universes;
  - every refusal is asserted by its message;
- **rule K at its edges,** with R00 and R05 not exempt, and every outcome to Joseph;
- **the readout end to end:**
  - κ = 1 passes and κ = 1.2 fails;
  - the fixture's A is four times M, so κ cannot be read against M by mistake;
  - the Ddl option keeps the identity to 10⁻¹²;
  - every control refuses, and the grid part's failures leave rule K standing;
  - reads are `O_NOATIME` only.

**The mutation receipt.**
- [`fd/receipts-1b/moded/mutation.py`](fd/receipts-1b/moded/mutation.py) and `mutation.out` record the digests of the
  code and tests they ran against.
- A mutant counts as KILLED only if the suite exits 1 (a test failed); any other exit reads ERROR. 41 of 41 are
  killed, and the unmutated suite passes 34 of 34.
- **Disclosed:**
  - in revision 0's first run, "Ddl's factor not applied" survived, and an added test now kills it;
  - in this revision, "rows alone counted by cell" and "rule K read against M" survived first. Each is killed by a
    sharpened test: the shared-pair occupancy case, and the fixture with A = 4M;
  - revision 0's first runner measured its "unmutated" line before restoring the source.

The neighbouring suites `test_fd_1b_inv.py` and `test_fd_1b.py` pass, 117 tests.

## 11. What D's report will and will not be able to say

**MEASURES:** rule K on κ per cell, the grid readings with their occupancy, and, with the option, the descriptive Ddl
readouts. All are labelled DERIVATION.

**CANNOT SUPPORT, whatever the outcome:**
- **Coverage, in either direction.**
- **That the toy realizes S1's block M.** κ is read at the nominal truth (§3.5).
- **The flux and detector groups.**
- **The correlation structure.**
- **That S1's block is right or wrong.**

## 12. For the director, and through the director for Joseph

1. **The rule (B1).** No nature construction compared with M has first-order power to pass (§3.2, §3.3). The rule is
   therefore κ, Dnom against A, at a cap of **5.5 node-h**, for Joseph to choose to run or not.
2. **The Ddl option** (§3.4): descriptive only, +3.0 node-h of cap (8.5 in all).
   - **My recommendation:** add it only if a later ensemble at a per-cell data-like truth is in view. Its λ is what
     such a design would rest on, and it tests nothing about the toy.
3. **The grid check** (§5), with M2's occupancy readouts and the construction-limited exclusion.
4. **The caps, the unit and the trigger** (§7).
5. **The earlier rulings, as now applied:**
   - ruling 1, the error object, is kept;
   - ruling 2, the data-like truth's hard control, applies to the option;
   - ruling 3, the outcome table, is replaced by rule K's in §6;
   - ruling 4, the grid part's own INVALID, is in the code;
   - ruling 5, the caps, is in §7;
   - ruling 6, the audit's acknowledgement before the bulk, is in §9.3.
