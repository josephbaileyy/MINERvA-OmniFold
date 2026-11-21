# AMENDMENT 2 to the staged 1B declaration: stage 1 redesigned, composed to first order (2026-11-02)

**By** the measurement session `coverage-5b`, for `coverage-5b-audit`, then the director for binding 3.

**Under:**
- [`DECISION-20261102-joseph-1b-redesign.md`](../../../DECISION-20261102-joseph-1b-redesign.md) (#700, `7544822d`);
- [`FD-1B-STAGED-REDESIGN-PROPOSAL.md`](FD-1B-STAGED-REDESIGN-PROPOSAL.md) (#697, revision 2, `883c26c4`);
- the consult `FD-1B-REDESIGN-CONSULT-ANSWER.txt` (#699);
- the director's rulings, which binding 3 will carry:
  - §2d (ii): an exact float64 pass over every row;
  - §2b: fail closed;
  - the receipt as a planned one-node job, at -t 02:00:00 and ≤ 2.0 node-h, outside the 73.0;
  - INVALID kept apart from STOP;
  - the exact screen, under conditions (a) and (b);
  - after cov2d's 2D receipt found a negative first-order composite on about 35–38 % of rows in some declared draw:
    the receipt's negative-composite extent, the S1-0b job, and the up-front `clipcheck` with its rule to Joseph;
  - after Joseph's `DECISION-20261102-joseph-bias-and-stabilisation-routes.md` (#714, "Probe, 1B waits"): the
    estimator and the clipping rule as named inputs, cov2d C1's clipping figures, and a declared slot for C2's.
- **1B stays on paper.** Stage 1 (S1-0b, `clipcheck`, the bulk) does not launch until the stabilisation probe has
  reported and the estimator is settled (#714). `clipcheck` is a hard stop before the bulk.

**After:**
- [`FD-1B-STAGED-STAGE1-STOP-REPORT.md`](FD-1B-STAGED-STAGE1-STOP-REPORT.md) (#696);
- declaration revision 2 and amendment 1, whose code this amends.

**This amends** `nd-unfolding/fd_1b_mc.py`, its tests, the stage-1 tables generator and the mutation receipt. Every
other bound module is unchanged: `fd_1b_score`, `s1_assemble`, `fd_1b_toys`, `fd_1b_inv`, `fd_1b_moded` and
`fd_1b_null`.

**MEASURES:** nothing. No job ran and no connect was made. The tests and the mutation receipt ran on this branch, at
0 node-h.

**CANNOT AUTHORIZE:**
- any job before binding 3;
- a change to the reported covariance, an interval or a claim;
- the paper's text, which the paper lane drafts when the result lands (§9).

## 1. What changes

| site | binding 2 (amendment 1) | amendment 2 |
|---|---|---|
| a drawn nature (§4.2) | a_D = a_{u₁} ⊙ Π_{j≥2} (a_{u_j}/a_CV), and the sum where a_CV = 0 | **a_D = a_{u₁} + Σ_{j≥2} (a_{u_j} − a_CV)**, summed in the draw's order, for every row and for the denominator per cell. k = 1 gives a_{u₁} bitwise, and rows with a_CV = 0 are unchanged term for term |
| a composite denominator cell | the product's | a cell with d_CV > 0 and d_D ≤ 0 **refuses**, in the toy and as a STOP in the receipt (§2b) |
| a negative expected count | `rng.poisson` raises (D2) | **λ⁺ = max(λ, 0) on the full product** in every Poisson draw, for toys and stat replicas, with the clipped mass recorded (§5) |
| the unfolded clipping offset | — | **`clipmean`**: one mean unfold per truth, giving o_c = U(x̂_clipmean − x̂_central)_c / σ_c, read by a rule fixed here (§5) |
| the receipt's N1 | an all-draws bound selecting ≤ 250,000 rows per array, then an exact pass | **every row, exactly, in float64**, over the 900 declared draws, behind a proven screen (§3), with no cap. It runs as a one-node job (§4) |
| N_clip | — | the declared draw with the largest clipped mass at r = 1, chosen by the receipt (§7) |
| cross terms | — | in the receipt, product against first order, U-mapped, in units of σ_c. A reco-space proxy and a truth-side counterpart, descriptive (§6) |
| the negative-composite extent | — | in the receipt, per array: the rows negative in some declared draw, the negative (row, draw) pairs, and the clipped fraction per draw (descriptive, §4) |
| the clipping offset, up front | — | **S1-0b**, one node after S1-0's readout: the clipmean at every truth and the central values S1-0 lacks. **`clipcheck`** then reads o_c against S1's reported σ, and any \|o_c\| ≥ 0.667 goes to Joseph before any bulk (§5b) |
| a second STOP | — | it ends stage 1 unless Joseph rules otherwise (§8) |
| the capture | — | it also records `push_min` and `push_negative` (the audit's O5) |
| the estimator | `fd_1b_toys.CONFIG = "R"`, fixed | **`--estimator`**, a required name from `s5e_candidate.CANDIDATES` (configuration (e) is `R`), installed and recorded in every product; the graders refuse a set with another or none (§2c) |
| the clipping rule | — | **`--clip-rule {data, nature}`**, a required named input: `data` is the decision's (a), and `nature` clips the nature in truth and reco together. Recorded and checked as the estimator is (§2c) |
| cov2d C1's clipping figures | — | in the receipt, carried by `clipcheck` by the receipt's digest (§5c) |
| cov2d C2's metrics | — | a declared **slot**, empty here, filled by addendum A2.1 from cov2d's own code, with Joseph's thresholds (§5d) |

## 2. The code, by change

`nd-unfolding/fd_1b_mc.py`:
- **`compose`:** the first-order rule. For two or more universes it applies §2b's refusal. N1's record adds
  `rows_negative_where_cv_positive`, which is descriptive.
- **`n1_ratio`:** N1's statistic, |a_D| / peak. The convention is 1 where both are 0, and +∞ where only the peak is 0.
- **`clip_draw`:** λ = w_reco·r on reco-passing rows and bkg_w on background rows.
  - The draw's weights are zeroed where λ < 0, so `fd_1b_toys.build_full` (unchanged) draws exactly λ⁺.
  - The nature's truth and denominator are untouched.
  - It returns Σλ, Σλ⁻ and n(λ < 0) for signal and background, plus |λ⁻| per 5D reco cell (signal and background)
    and per 5D truth cell (truth-passing signal rows).
- **`toy_experiment` and `stat_experiment`:** they draw through `clip_draw`. A stat replica's nature is the nominal
  one, so the clip is the identity wherever r ≥ 0, which is tested.
- **`clipmean_experiment` and the `clipmean` role:** d_T at its mean (`mean_experiment`, the nominal nature), plus the
  clipped mass |λ⁻| of N_clip as observed events at their counts, inside the analysis window. It is unfolded by S1's
  path, as `central` is.
- **`verified_weights`:** each weight file is read once through O_NOATIME, and its sha256 is taken over the very bytes
  loaded and checked against the pins (the audit's question on O4). It returns the as-loaded arrays and the
  zeroed arrays, the latter bitwise as `fd_1b_inv.universe_weights(..., "zero")` gives them.
- **The receipt's core:**
  - `draw_columns`, `screen_floor` and `screen_floor_check`;
  - `exact_n1`, `pinned_composite`, `no_screen_n1` and `validate_screen`;
  - `denominator_check`;
  - `crossterm`, `flat_cells` and `cross_z`;
  - `receipt`, built from them.
- **`clipping_readout`,** inside `readout`.
- **`clipped_fraction` and `_spread`:** the receipt's per-draw clipped fraction.
- **`pilot_b`, `walls_of` and `clipcheck`:** S1-0b's items, a walls check over any named products (`walls --stage
  s1-0b --clip-seed`), and the up-front offset step (§5b).
- **`InvalidReceipt`:** a `Refusal` raised whenever the receipt cannot decide (§4).

`stage1/tables/make_stage1_tables.py`:
- `clipmean` items, one per truth at the receipt's N_clip seed;
- the S1-0b table (`s1-0b-steps.tsv`, `tasks-s1-0b.tsv`): five items with the plug-in, three without, one per lane;
- the bulk, which excludes S1-0's and S1-0b's items: 1,576 items on 9 nodes with the plug-in (1,049 on 6 without), at
  most 22 per lane;
- the receipt's one-lane table (`receipt-steps.tsv`, `tasks-receipt.tsv`);
- the S1-0b and bulk tables wait for both the push digest and the N_clip seed.

### 2c. The estimator and the clipping rule, as named inputs

**Why.** Joseph's #714 puts a stabilisation probe first, and a different estimator may follow. cov2d's clipping
probe, going to Joseph, raises consistent clipping as an option. Either switch should then be a re-pin with a
record, not a redesign.

**The estimator.**
- `unfold --estimator <name>` is required, and the name must be in `s5e_candidate.CANDIDATES`. It is passed to
  `s5e_candidate.install` and recorded as the product's `config`.
- A winner that is a parameter override, as `R` is, is a new registry line and a re-pin.
- A winner that is new estimator code, such as cross-fitting, is a code change with its own tests before the re-pin.

**The clipping rule.** `--clip-rule` is required, one of `CLIP_RULES`, and passed to `clip_draw`. It is recorded as
the product's `clip_rule`.
- **`data`** is decision §2a (a): only the draw is clipped, and the truth keeps the nature's negatives.
- **`nature`** clips consistently: a signal row with λ < 0, or a truth-passing row with w_truth·r < 0, is zeroed in
  w_truth and w_reco alike. Background rows with bkg_w < 0 are zeroed. The draw and the truth then share one
  non-negative nature. The denominator, per cell, stays under §2b's fail-closed rule.

**Which rule the bulk runs: Joseph's ruling** (`DECISION-20261103-joseph-coverage-clip-rule.md`, #718, merged at
`1e74f819`, "Option 1, both tests"). This supersedes the audit's B1.
- **The gate.** The bulk runs `nature` (consistent clipping) **only if** 1B's own pre-bulk `clipcheck` reads "option
  (1)" under C2's fixed reading (`c2_reading.txt`, `b5b4fc4b…`, unchanged), with C2's quantities computed by cov2d's
  code through addendum A2.1.
- **Any other reading is a hard stop:** nothing launches, and 1B returns to Joseph.
- **In code** (`check_clip_gate`): `--clip-rule nature` refuses unless it is given A2.1's gate file (`--clip-gate`,
  `--expect-clip-gate-sha256`), and that file reads `{"step": "c2-clip-gate", "reading": "option (1)", "verdict":
  "PASS"}`. Nothing in this amendment writes that file, so `nature` cannot run until A2.1.
- **The "data" rule's offset** (`clipmean`, `clipcheck`'s o_c, the readout's clipping section) stays the descriptive
  figure, under `data`. These refuse `nature` (`NATURE_UNRULED`).
- **Grading a `nature` bulk is A2.1's.** That covers the relation of S1-0's pilot toy and stat items, which run under
  `data` before the gate, to a `nature` bulk, and the readout's clipping section under it.
- **Why the offset is not defined under `nature`** (the audit's C4 on #717). It zeroes positive truth on rows with
  λ < 0, and its completeness then uses the zeroed w_truth against an unzeroed per-cell denominator.

**The checks.**
- `null`, `readout` and `clipcheck` take both names. They refuse any product at a truth whose recorded `config` or
  `clip_rule` differs from, or lacks, the declared one (`refuse_mixed_estimator`).
- The tables generator takes both as arguments and writes them into every unfold step. The receipt unfolds nothing
  and takes neither.

**Deferred by the director until a winner is known:** whether stage 0 is re-run, and whether its PASS carries; and
whether S1 is re-run before the controls. Under a new estimator, the four procedure controls and the capture compare
with S1's products made by that estimator.

## 3. The screen: proposition and proof (the director's condition (a))

**N1's statistic,** per row and declared draw D = (u₁, …, u_k): r = |a_D| / P_D, with P_D = max_j |a_{u_j}|. The
convention is r = 1 where a_D = P_D = 0, and r = +∞ where P_D = 0 < |a_D|. A pair is above the bound if r > 10.

**The floor:** L = max over bands b of min over b's universes u of |a_u|, per row (`screen_floor`).

**Proposition.** If every declared draw holds exactly one universe of every band, then no (row, draw) with
|a_D| ≤ 10 L has r > 10.

**Proof.**
1. D holds some u_b ∈ b for every band b, so P_D ≥ |a_{u_b}| ≥ min_{u∈b} |a_u| for every b. Hence P_D ≥ L.
2. If L > 0, then P_D > 0, so r = |a_D| / P_D ≤ |a_D| / L ≤ 10.
3. If L = 0, then |a_D| ≤ 0, so a_D = 0, and r = 0 (where P_D > 0) or r = 1 (where P_D = 0). Both are ≤ 10. ∎

The premise is checked at run time: `draw_columns` raises INVALID on any draw that does not hold one universe of
every band.

**How it is used.**
- **The margin** (the audit's C3 on #717). The code compares the matmul's |a_D|, which is rounded, so it screens out
  only pairs with |a_D| ≤ 10 L (1 − 10⁻⁹). A pair the proposition covers can then never be screened out by rounding.
- Every pair past the screen gets the exact peak, gathered over the draw's universes, and its exact r.
- Every pair at or below 10 L is proven not above.
- So every row's N1 outcome is decided exactly. There is no estimate and no cap.

**The arithmetic.**
- a_D for a block of draws is S·V − (k − 1)·a_CV, in float64 BLAS. Here S is the draws' 0/1 universe matrix and V
  the [175 × rows] weights.
- Its rounding near r = 10 is about k·ε·P_D / |a_D|, roughly 9 × 10⁻¹⁶ relative for k = 40 (the audit's figure).
- Pairs with |r − 10| ≤ 10⁻⁹ · 10 are recomputed in `compose`'s pinned order (`pinned_composite`) and decided by that.

**The director's condition (b), tests in both directions:**
- **Screen against no-screen, exhaustively on the fixture** (`ExactN1`). Every row and every draw of a small bank
  with all its draws enumerated:
  - the proposition holds on every screened-out pair;
  - the screened outcome equals the no-screen one in pairs above, rows above and each row's worst.
- **A tightened floor is caught.** A floor raised just enough to screen out a real pair above 10 is caught by the
  validation and by `screen_floor_check`. Mutants that tighten the floor (min → max), raise the screen to 1.5 L, or
  disable either check are killed (§10).
- **In the job:** the full no-screen computation on a seeded random 0.5 % of real rows (`VALIDATE_SEED` = 3,659,001),
  across all 900 draws, must equal the screened outcome pair for pair and row for row. Any disagreement is INVALID.
  - **The seed is unused elsewhere.** `git grep` for 3659001 in any spelling finds only `fd_1b_mc.py` and two
    floating-point digit runs in PET result files, which are not seeds.
- **Also in the job, on every row:** `screen_floor_check` recomputes L band by band with an explicit loop and compares
  it exactly. The 0.5 % sample may hold no row above 10, so a wrong floor must also be caught where the sample cannot
  see it.

## 4. The receipt job

**Why a job** (the director's ruling).
- There are 16,424,551 signal and 310,773 background rows (the audit's count).
- V for `wt` and `wr` is 23.0 GB each in float64.
- With the cross-term work arrays and the blocks, the working set is about 100–170 GB at its peak. That is beyond a
  login node, and within one CPU node's 512 GB.

**The line,** after binding 3, from a fresh deploy at binding 3's merge, sent to the director first:
```
sbatch -A m3246 -q regular -C cpu -t 02:00:00 -J fd1b_mc_receipt_a2 -o $W1/logs/%x_%j.out \
  $DD/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh \
  $DD <M3> $W1/tables/tasks-receipt.tsv $W1/a2/lanes 256 480G 0 0 inherit
```
- The wrapper's own `#SBATCH` lines set one node, `--exclusive` and `--no-requeue`.
- The step runs through `s5c_array.sh` and `mnv_guarded_run.py`, as every stage-1 step does.
- The output is `$W1/a2/receipt.json`, which must not already exist.

**The read volume,** from the files each pass loads:
- one O_NOATIME read of each of the 700 pinned universe files, 68.4 GB, hashed in memory from the same bytes;
- the inputs (1.55 GB), bank CV (2.16 GB), background, pins, constraint and staged assembly.

That is about 72 GB, half of a hash-then-load design.

**The wall** (an inference, to be replaced by the job's own sacct):
- **I/O:** connect 32 read 208 GB in 1:26:25 on a login node, which bounds 72 GB at about 30 min there. A compute node
  is expected to be faster.
- **Compute:**
  - the screen's two matmul sweeps and the cross-term matmuls, about 10¹³–10¹⁴ FLOP;
  - the bincounts, the gathers past the screen and the validation, minutes each on a laptop at these sizes.
- **Total:** under 2:00:00 is expected, but that is not measured. <!-- absence-ok: an estimate of the receipt job's wall time before it runs, not a claim that a result does not exist -->

**INVALID versus STOP** (the audit's P1, the director's ruling):
- **STOP** is only N1 (`exact.*.rows_above` > 0) or §2b (`denominator.draws_with_nonpositive_cells` non-empty), on a
  receipt that completed and wrote `receipt.json`.
- **INVALID** is anything that stops the receipt from deciding. It writes no `receipt.json`, costs only its job, and
  may be rerun under a new ruling. Its causes:
  - a timeout or out-of-memory (the director: a stop for his ruling, not (iii)'s second STOP);
  - more than `MAX_PAIRS` = 50,000,000 pairs past the screen, counted and printed before any gather (P3);
  - a disagreement in the validation or the floor check;
  - a draw missing a band;
  - a digest refusal.

**The negative-composite extent** (the director's request), per array, from the same matmul blocks, labelled
descriptive:
- `negative_composite.rows_in_some_draw`: rows with a_D < 0 where a_CV > 0, in at least one declared draw;
- `negative_composite.pairs`: (row, draw) pairs with a_D < 0 where a_CV > 0;
- `negative_composite.clipped_fraction_per_draw`: |Σ min(a_D, 0)| / Σ a_D per draw, as min, median, 95 % and max.
  This is over reco-passing rows for `wr`, and over all rows for `wt` and `bkgw`;
- `clipped_fraction_signal_plus_background_per_draw`: the same for `wr` and `bkgw` together, as N_clip uses them.

**N1 on the denominator** (the audit's C2 on #717). `compose`'s record and `n1` also stop on the per-cell
denominator, so the receipt evaluates it exactly, in compose's order, for every cell and every declared draw
(`denominator_check`'s `n1`). Any cell above 10 is a STOP reason, as for the per-row arrays.

**§2b in compose's pinned order** (the audit's P2). Cells × draws is small, so the denominator check runs exactly in
compose's order, not by matmul.

The negative-composite counts and N_clip's clipped mass are matmul figures. They are labelled "matmul, descriptive"
and decide nothing.

## 5. Clipping (decision item 3, consult (ii), the audit's R1–R3)

**The draw:** λ⁺ = max(λ, 0) on the full product.
- That is w_reco·r·f_s for signal and bkg_w·f_b for background, with f_s = f_b = 1.
- It is identical to the mean path: at its mean, the toy's draw equals `build_full(expectation=True)` on the **same
  nature**, bitwise, because that path also keeps only rows with n > 0 (R1, tested).
- The truth keeps the nature's negative weights.

**Recorded per toy, read before grading:**
- Σλ, Σλ⁻ and n(λ < 0), for signal and background;
- `clip_reco_flat` and `clip_truth_flat`, the clipped mass per 5D cell, mapped by U in the readout.

**Recorded per stat replica:** the same sums, in its meta.

**The offset (ii).**
- **The mean unfold:** one per truth, the `clipmean` item. Its data are d_T plus N_clip's |λ⁻| (§7). The clipped data
  equal the signed data plus |λ⁻|, and the signed data cannot be unfolded, since the estimator drops non-positive
  counts. So this unfolds the response to the clipped mass around d_T.
- **The offset:** o_c = U(x̂_clipmean − x̂_central)_c / σ_c, with σ_c from C_T. Both unfolds use S1's path at seed 42.

**The reading, fixed now, before any number is read.**
- **The rule.** A cell flagged at T (§5.1's cell flag) with |o_c| ≥ δ* = 0.667 is read "the flag may be the clipping
  artefact".
- **Where δ\* comes from.** It is the offset that lowers a unit Gaussian's ±1σ content by §5.2's per-cell resolution,
  0.10 (0.6827 → 0.5827). The audit checked it.
- **What it cannot do.** The verdict and clause F stand either way: the reading cannot un-flag. Cells not flagged get
  no reading.
- **Beside it, the readout reports:**
  - o_c for every cell;
  - the toys' clipped fraction |Σλ⁻| / Σλ per truth (min, median, max) for signal and background;
  - the toys' per-cell clipped mass relative to N_clip's (median and max), so the offset can be scaled.

## 5b. The clipping offset up front: S1-0b and `clipcheck` (the director's ruling)

**Why.** cov2d's 2D receipt, on the same first-order rule, finds a negative composite on about 35–38 % of rows in some
declared draw (1.7–1.8 % of pairs). Its single-ratio maxima (429.59, 44.77) mirror this bank's. So each toy may carry
a one-signed clipping offset that is not small, and it is read before the bulk, not after it.

**S1-0b:** one node at 1:00:00, 1.0 node-h, after S1-0's readout and before the bulk.
- **Its items** (`pilot_b`): the clipmean at g18, ar23 and plugin, at N_clip's seed, and the central value at ar23
  and plugin. G18's central value is S1-0's.
- **Its own walls check:** `walls --stage s1-0b --clip-seed <seed>`, by the same unit and RSS limits.
- **The plug-in's items** need the push, so S1-0b follows S1-0.

**`clipcheck`,** after S1-0b:
- **The offset, per truth:** o_c = U(x̂_clipmean − x̂_central)_c / σ_c.
- **σ_c's proxy.** Here σ_c is S1's **reported** σ at the data (`fd_1b_score.reported_matrix`, the data product's
  `C_total_plus_C_resp`), because C_T exists only after the bulk. The final readout recomputes o_c with C_T, as in §5.
- **The rule, fixed now.** If any cell at any truth has |o_c| ≥ 0.667 (δ\*), the verdict is `TO_JOSEPH`, and the case
  goes to Joseph before any bulk is submitted. Below that, the verdict is `PROCEED`, and the bulk follows under the
  existing conditions.
- **Reported either way:** o_c at every cell and truth, and N_clip's clipped record.
- **The seed must match** (the audit's C5 on #717). `clipcheck` refuses a clipmean whose N_clip seed is not the
  digest-pinned receipt's.

## 5c. cov2d C1's clipping figures (the director's request)

The receipt computes these at r = 1 over the 900 declared draws, first order, by matmul. They are descriptive, and
each is U-mapped to the reporting cells. `clipcheck` carries them by the receipt's digest.
- **The source split, per array:**
  - rows with some universe weight ≤ 0 (where a_CV > 0);
  - rows negative in some draw that have such a universe;
  - rows negative in some draw that have none, which are composite-only.
- **The clipped fraction per draw,** |Σλ⁻| / Σλ, for signal (reco-passing rows) and background: min, median, p90,
  q95 and max.
- **Per truth cell, the clipped signal rows' truth content** (`clipped_rows_truth_xsec_over_sigma_c` and
  `_over_sigma_stat`). That is |a_D(w_truth)| of the rows `clip_draw` clips (reco-passing, with a negative w_reco
  composite; the audit's C1 on #717 added the reco mask), and truth-passing, at their truth cells, converted to cross section by `xsec_nd`'s per-cell factor at the CV's
  completeness. It is reported over σ_c (the reported σ) and over σ_stat (S1's stat block), as the median and max
  over draws.
  - **Unverified:** the conversion divides by the completeness ε_c. Whether this equals C2's efficiency-corrected
    m_seen/S_c is **unverified until A2.1's equality test**. It is not claimed here.
- **Per reco cell,** |Σλ⁻| / √Σλ⁺, as the median and max over draws. It is a reco-space proxy, mapped by U.

## 5d. The C2 slot and the thresholds (declared, empty)

The director asked for the following, to be **cov2d's C2 definitions** so that the two tests measure the same
objects:
- the efficiency-corrected offset m_seen/S_c in σ_c;
- the option (1) residual R_c = m_seen/S_c − m_all/N_c, signed;
- var_natures(truth_c) / C_T,cc under first-order, clipped and multiplicative composition;
- the reco/truth row mismatch;
- bᵀC⁻¹b.

**Not retyped here.** C2's code exists, on origin/decl/cov2d-20261102 at `1a07b07c`:
`fd/receipts-cov2d/clip/clip_probe2.py`, sha256 `b95c5629…`, with `c2_reading.txt` and `test_clip_probe2.py`. It is
not on main.

**Addendum A2.1** fills the slot:
- It imports cov2d's function where it can, or copies it verbatim with a test that pins equality on a shared fixture.
- It is pinned to the sha that lands on main, not to the branch.
- It adds `clipcheck`'s C2 block and A2.1's own equality test of §5c's truth-cell conversion against C2's.

**The thresholds** for `clipcheck`'s C2 reading are **the ones Joseph rules for cov2d**. This slot is empty, and
nothing is invented. Until A2.1 and that ruling land, `clipcheck` reads only §5b's δ\* rule, and it remains a hard
stop before the bulk.

**The plug-in's push (O5).** The capture records `push_min` and `push_negative`. S1-0's readout reports them,
descriptive.

## 6. Cross terms (consult (i))

**What is computed.** For each of the 900 declared draws, the receipt builds the U-mapped histogram of a_D over rows
in their 5D cell, under the product rule (binding 2's) and under first order.
- **The reco-space proxy:** signal w_reco on reco-passing rows at MCreco, plus the background template at bkg_reco.
  It is a reco histogram mapped by U, a truth-cell map, and it is labelled so (the audit's A1).
- **The truth-side counterpart** (`truth_weight_histogram`): w_truth on truth-passing rows at MCgen, which is what
  x_true sees. It is a different object from §5c's clipped-rows truth content, and is named apart from it.

**The figure:** z_c = [(H_product − H_first-order) / H_CV]_c ÷ (σ_c / x̂_c).
- x̂ is S1's data result, the staged assembly's `f`, read through O_NOATIME.
- σ_c is from the reported covariance: `fd_1b_score.reported_matrix`, the committed data product's
  `C_total_plus_C_resp` at sha256 `b79556f0…`, read from the deploy. It is reported per cell as the median |z|, the 95 % |z|, the max |z| and the median signed z, over
the draws. Descriptive only.

**A placement change from the decision.** The decision places (i) on the login node at 0 node-h. It now runs inside
the receipt job, which the director moved to one node for memory. Its marginal cost in that job is minutes, within
the job's ≤ 2.0 node-h.

## 7. N_clip, by rule (the audit's O2)

**The rule.** N_clip is the declared draw with the largest total clipped mass at r = 1: |Σ_{reco rows} min(a_D, 0)|
for `wr` plus |Σ min(a_D, 0)| for `bkgw`. The receipt computes it before the bulk, by matmul, and it is labelled
descriptive. Ties go to the first draw.

**How it is used.** Its seed goes into the bulk table's three `clipmean` items. It is the **reference case** of the
offset, not claimed to be the largest clipping case. The toys' per-cell ratios to it are reported.

## 8. A second STOP

A STOP of the new receipt, or of `n1` at any truth, ends stage 1 unless Joseph rules otherwise (decision item 2
(iii)). It goes to the director and to Joseph unrepaired, with no further redesign. An INVALID receipt is not a STOP
(§4).

## 9. The wording (decision item 4)

The decision fixes the basis for both the paper and the note.

**The paper: one neutral methods sentence.** It says:
- 300 pseudo-experiments at each of two held-out tunes;
- the uncertainties propagated linearly, as in the covariance's construction;
- the covariance rebuilt by the same procedure at each tune;
- then the result.

It carries no "does not test" clause and no paper-side CANNOT SUPPORT line. Two facts are stated as description, not
as qualifiers:
- G18 shares its 2p2h model family with one of the model term's generators;
- the result concerns the procedure's covariance at those tunes, not the reported intervals at the data.

**The note and the report:**
- negative expected counts clipped to zero, with the measured clipped fraction and the per-cell offset;
- the ±1σ endpoint draws;
- the shared universes, so that sources absent from the bank are not probed;
- the cross-term readout;
- that nothing is shown about multiplicative composition.

**Who writes the paper text:** the paper lane, when the result lands, through the PRD-referee read, with Joseph's read
before merge. Declaration §12's clauses M and S, and §13's line, are superseded by this basis.

## 10. Tests and mutation

**The test file** is `nd-unfolding/tests/test_fd_1b_mc.py`. On this branch: `test_fd_1b_mc`, `test_fd_1b_null` and
`test_fd_1b_moded` give 164 passed (107 in `test_fd_1b_mc`), under a fixed and under 14 varied hash seeds.

**New or rewritten tests:**
- **Compose:** first order in the draw's order, bitwise, for two and three universes. The denominator per cell. §2b in
  both directions: d_D = 0 refuses, just above 0 passes, and k = 1 is exempt.
- **Clipping:**
  - D2 reproduced: binding 2's path raises, and the new one draws;
  - the draw is `build_full`'s on the clipped weights, bitwise;
  - R1's mean identity on the same nature;
  - R2's sign cases;
  - R3's per-cell mass;
  - `clipmean`'s added mass, and its identity with d_T when nothing clips;
  - stat replicas unchanged where r ≥ 0.
- **ExactN1:** §3's proposition on every pair, and screen against no-screen exhaustively. Also:
  - the tightened floor caught;
  - block invariance;
  - the pair budget as INVALID;
  - the near-bound recompute;
  - a missing band;
  - the pinned-order denominator check;
  - `flat_cells` against `np.histogramdd`;
  - the cross-term histograms against a direct product and first-order build.
- **Receipt** (the toy bank): the singles against the raw weights; the exact pass against `compose`'s own per-draw
  record, summed; the validation; N_clip against `clip_draw`; PASS and STOP; and `verified_weights`, which opens each
  file once, matches `universe_weights` bitwise and refuses bytes that are not the pinned file.
- **Pipeline:** the clipping readout, covering o_c, the fractions, the per-cell ratios, the reading rule (a flagged cell
  below δ\* is not listed) and the refusal of two clipmean products. Also `clipcheck` both ways (`TO_JOSEPH` at
  |o_c| ≥ δ\*, `PROCEED` below), with its own refusal of two clipmean products, and S1-0b's walls (missing product,
  complete, no seed).
- **The clip gate** (#718): `--clip-rule nature` refuses with no gate file, with a gate file reading STOP or option
  (2), and with a wrong digest; it passes on the pinned option-(1) file; `data` needs none (amendment 2's interim).
- **Named inputs:**
  - `unfold` installs and records exactly the named estimator, and refuses an unknown or missing one;
  - the graders refuse a product set with a mixed or missing estimator or clip rule, and grade again once it is
    restored;
  - the `nature` rule zeroes truth and reco together while `data` clips only the draw, with the toy's truth equal to
    `build_full` on the clipped nature;
  - an unknown rule refuses.
- **C1's figures:** `clip_cells` against a direct per-draw build. In the receipt, the source split against a direct
  count over every universe. `clipcheck` carries the receipt's block and refuses a wrong digest or a STOP receipt.
- **ExactN1, the extent:** the negative-composite rows, pairs, sums and clipped fractions against compose's order. In
  the receipt, the pairs against compose's own per-draw count.

**The fixture's denominators** now agree with its bank as the real ones do:
- the CV's is the bank's truth rows at tdw = 1;
- each detector universe's is the CV's within 5 %.

The toy world's denominators were unrelated random histograms, which the product rule's ratios hid and first order
exposes.

**The fixture is also deterministic in its denominators.** The toy world seeds its bank weights by `hash()`, which
varies per process.
- **The failure seen.** Under one hash seed (16), first order's sum of about 37 per-universe `tdw` departures, each
  uniform within ±10 %, drove a sparse cell's composite denominator to ≤ 0. The receipt then STOPped on §2b, and two
  tests failed.
- **The fix.** The fixture now maps each bank universe's `tdw` to a factor within ±2 %, and each detector universe's
  `denom_nd` to the CV's within ±5 %, both seeded by the tag (`zlib.crc32`).
- **The check.** The suite passes under 14 hash seeds.
- **What it says about the real bank.** The same mechanism could operate there in sparse cells. §2b then fails
  closed, and the receipt reports it as a STOP, as designed. That is a property to report, not to test away.
- **The harness** pins `PYTHONHASHSEED=0` for every child, so the receipt reproduces.

**The mutation receipt** is `fd/receipts-1b/staged/mutation_mc_a2.py`, with its output in `mutation_mc_a2.out`. It
carries binding 2's 79 mutants, and prints those whose target code amendment 2 replaced as N/A, by name. It adds 101
for amendment 2: 76 of mine (the director's additions included), 11 of `coverage-5b-audit`'s mut717.py
(carried, two re-anchored), 9 for the fixes of its review of #717 (C1–C5), and 5 for #718's clip gate
(`check_clip_gate`: never called, always open, no digest check, any reading, no file). **170 of 170 applicable
mutants are killed**; the 10 named replacements are N/A; 180 in all. The unmutated suite: 107 passed, and 0 `.pyc`
after the run. The receipt's digests: `fd_1b_mc.py` `3d22a591…`, the tests `2ae68009…`.

**A defect in the harness, found and fixed here.**
- **The defect.** Binding 2's harness spawned `python -m pytest` without `-B` or `PYTHONDONTWRITEBYTECODE`. A
  mutant written within the same second as the file before it, at the same size, could then be imported from a stale
  `__pycache__` entry, in either direction.
- **What was observed.** Amendment 2's first full run ended "unmutated: 2 failed, 76 passed". The same suite gives
  78 passed in direct runs under six `PYTHONHASHSEED` values. Both `__pycache__` entries were present afterwards.
- **The fix.**
  - Every child runs with `-B -p no:cacheprovider` and `PYTHONDONTWRITEBYTECODE=1`.
  - Both `__pycache__` directories are purged before each mutant and before the unmutated run.
  - `find nd-unfolding -name '*.pyc'` counts 0 after the run. That check is run outside the harness, so it is not
    in the `.out`.
- **The rerun under the fix** gave "unmutated: 78 passed". Its survivors are all test gaps, each closed by a test,
  with no code change.
- **N/A is a named list, not an inference.** An earlier pass labelled a carried mutant N/A whenever its target
  string was missing. Two of the D1 O_NOATIME mutants (null and readout) were then mislabelled, because an inserted
  `refuse_mixed_estimator` line had moved their anchor. They are re-anchored and run.
  - The harness now holds an explicit `REPLACED` set of the ten mutants whose code amendment 2 replaced: the product
    composition and `composite_n1`.
  - Any other missing target stops the run.
  - Two mutants were added for the new O_NOATIME reads of the staged assembly, in `receipt` and `clipcheck`, each with
    a NoAtime test.
- **Binding 2's receipt stands.** `coverage-5b-audit` reran binding 2's `mutation_mc.py` cleanly at M2: 79 of 79
  killed, and the output is identical to the committed one except for wall time (#673,
  issuecomment-6593667763).

## 11. Price

| item | node-h | note |
|---|---:|---|
| the receipt job | ≤ 2.0 | one node at -t 02:00:00, outside the 73.0 (the director). A timeout is INVALID |
| S1-0 | 1.0 | unchanged |
| S1-0b | 1.0 | one node at 1:00:00: three clipmeans and two central values (§5b) |
| the bulk with the plug-in | 72.0 | 1,576 items on 9 one-node jobs of 8:00:00, unchanged |
| **exposure** | **≤ 76.0** | 73.0, plus the receipt's ≤ 2.0, plus S1-0b's 1.0 (the director). The balance read at connect 32 was 2,050.9 node-h, half of it 1,025.5 |

## 12. Order after binding 3

0. **The gate (#714):** nothing below launches until the stabilisation probe has reported and the estimator is
   settled, on the winner if Joseph adopts one, otherwise on `R`. A switch is a re-pin under §2c, priced then.
1. **One connect:** a fresh deploy at binding 3's merge, with the balance gate, the stat-before over the widened list
   and the tables, then the receipt job's submission. Its script and line go to the director first.
2. **The receipt's readout** goes to the audit and the director:
   - PASS, STOP or INVALID;
   - the validation, the floor check and the pair count;
   - N_clip;
   - the cross terms;
   - the stat-after.

   A STOP ends stage 1 (§8).
3. **S1-0** follows, as binding 2 ruled. Its readout adds O5's push sign, and the clipping record of its one toy
   (G18 3,620,000 draws both HighQ2_1 and LowQ2_1).
4. **S1-0b,** with its line sent to the director first. Then its walls, then `clipcheck`. A `TO_JOSEPH` verdict goes
   to Joseph before any bulk (§5b).
5. **The bulk** is submitted after S1-0's walls PASS, every control passes, S1-0b's walls PASS, `clipcheck` reads
   `PROCEED` (or Joseph rules), and the audit's written acknowledgement. Its table is made with the push digest and
   N_clip's seed.
6. **Per truth:** `n1`, then `null`, then `readout` with the clipping section, then the report.

## 12b. What binding 3 binds (Joseph's #718, superseding the audit's B1)

- **`--estimator R`, provisionally.** The B4 gate (#714) still holds: nothing launches before the stabilisation probe
  reports and the estimator is settled.
- **No clip rule for the bulk.** Binding 3 binds the gate instead: the pre-bulk `clipcheck` with C2's reading (A2.1)
  selects `nature` on "option (1)", and stops otherwise (§2c).
- **The "data" rule** for everything before the gate: the receipt, S1-0, S1-0b and `clipcheck`'s descriptive offset.

## 13. For the audit and the director

- **The proof of §3,** and the in-job checks it rests on: the floor recomputation on every row, and the 0.5 %
  no-screen sample.
- **The receipt job's line and budgets,** and the INVALID/STOP split (§4).
- **The clipping reading's δ\* = 0.667,** fixed here (§5).
- **The cross-term placement change** (§6).
- **N_clip's rule** (§7).
- **The negative-composite extent, S1-0b and `clipcheck`'s rule** (§4, §5b), as the director ruled them.
- **The named inputs** (§2c), **C1's figures,** with the truth-cell conversion's match to C2 unverified (§5c), and
  **the C2 slot,** empty until A2.1 (§5d).
