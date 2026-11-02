# DECLARATION 1B staged method coverage, revision 0: stage 0 κ as the hard gate, then held-out-tune coverage with the covariance remade at each truth (2026-11-01)

**By** the measurement session `coverage-5b`, for `coverage-5b-audit` to review and the director to bind.

**Under** [`DECISION-20261101-joseph-1b-staged-method-coverage.md`](../../../DECISION-20261101-joseph-1b-staged-method-coverage.md)
(#663; Joseph: "Staged method-coverage (Recommended)"), every item, and the director's brief of 2026-11-01. The consult
behind it is `FD-1B-MODED-CONSULT-{PROMPT,ANSWER}.txt` (#660).

**After:**
- mode D's declaration, [`FD-1B-MODED-DECLARATION.md`](FD-1B-MODED-DECLARATION.md), revision 1 at #655 head `55435ec0`,
  acknowledged by `coverage-5b-audit`. It is carried here byte-identical as the record of the design finding (§14);
- the original 1B protocol, [`FD-1B-DECLARATION.md`](FD-1B-DECLARATION.md), whose draws, surrogates and transfer
  rule stage 1 reuses where §4 says so;
- S1's assembly (`nd-unfolding/s1_assemble.py`, `S1-REPORT.md`), whose procedure stage 1 reruns at each truth.

**This declares:**
- stage 0, carried unchanged from #655 (§2);
- the record that neither tune entered C_model, the estimator or any tuning (§3);
- stage 1's design (§4) and grading (§5), fixed before any number is read;
- the plug-in truth (§6) and the truth-dependence readouts (§7);
- the price (§8), the controls (§9), the order (§10) and the code still to come (§11);
- the paper's text in each outcome, fixed now (§12).

**MEASURES:** nothing. No job ran and no connect was made. The arithmetic is
`fd/receipts-1b/staged/arith.py`, with its output in `arith.out`. The record queries are `provenance.py`, with their
output in `provenance.out`. Both ran on this branch from `a4cd6ffc`, at 0 node-h.

**CANNOT AUTHORIZE:** any job before the director's binding, or stage 1 before stage 0's PASS and the binding of
§11's code. It cannot authorize any change to the reported covariance, an interval, a claim or the paper's wording,
except the text §12 fixes for Joseph, and only after a result lands.

## 1. Fixed by the decision, and unchanged here

- **The reported covariance is not under revision.** No outcome inflates, replaces or re-weights a block without
  Joseph (decision item 5).
- **Stage 0 is κ, with a hard gate** (decision item 1, item 6).
- **Stage 1** is held-out-tune method coverage at G18_10a_02_11b and AR23_20i_00_000:
  - every uncertainty group is drawn;
  - each pseudo-dataset is unfolded with the nominal simulation by the production procedure;
  - the covariance is remade at each tune's truth by the reported procedure.
- **Grading is per tune.** With two truths there is no coverage rate (decision item 2).
- **The truth dependence is a readout,** not a verdict (decision item 3).
- **Unchanged:** gate D's verdict, I0, I2, every claim and number, and the paper. Until a result lands, the paper's
  stopped-attempt disclosure stays (decision item 5).

## 2. Stage 0: κ, carried from #655

**Carried byte-identical from #655 at `55435ec0`.** `git checkout 55435ec0 -- <path>`, so the blobs are #655's:

| file | sha256 (prefix) | status |
|---|---|---|
| `nd-unfolding/fd_1b_moded.py` | `42008843…` | unchanged |
| `nd-unfolding/tests/test_fd_1b_moded.py` | as at `55435ec0` | 34 passed on this branch |
| `fd/receipts-1b/moded/mutation.{py,out}` | as at `55435ec0` | 41 of 41 killed, recorded there |
| `FD-1B-MODED-DECLARATION.md` | as at `55435ec0` | the design record (§14) |

**What stage 0 runs** is #655's "κ only" option exactly, as its §6–§9 declare it:
- rule K on κ = √(Dnom / A_unc) per cell, with the window [0.9, 1.1];
- the grid check, descriptive, with its own INVALID;
- the pilot D-0 (1.0 node-h), then the bulk (4.5 node-h), for a cap of **5.5 node-h**;
- the bulk waits for walls PASS and the audit's written acknowledgement of D-0.

**The Ddl option is not run.** <!-- absence-ok: a design choice of what stage 0 runs, not a claim that a result does not exist --> The decision folds mode D into stage 0 as κ alone (item 6), and the plug-in truth (§6)
supersedes Ddl's data-like truth.

**The gate, fixed now:**

| rule K | stage 0 reads | next |
|---|---|---|
| **PASS**, 16 of 16 | the toy's interaction construction has the full universe's symmetry under the swap at the nominal truth | stage 1, after the audit's acknowledgement of stage 0's report and the binding of §11's code. Joseph is told |
| **PARTIAL**, 8–15 | the construction departs in the named cells | **stage 1 waits for Joseph.** Stage 1 uses the same construction, so a departure is a defect stage 1 would inherit. For the director to rule (§14.2) |
| **FAIL**, below 8 | it departs | **the campaign stops,** and the result goes to Joseph (decision item 1) |
| **INVALID** | none | reported unrepaired, to the director |

**Why κ gates stage 1.** Stage 1's interaction draws are mode D's nature construction (§4.2). κ is that
construction's only check at a point where closure fixes the answer at first order (#655 §3.2). The expectation is
unchanged: closure fixes κ = 1 at first order, so a PASS is the expected outcome (#655 §6).

## 3. The tunes were held out: the records

`provenance.py` runs each query below and prints its exit status. An empty search is scoped to its pattern and paths.

**(1) C_model.** C_model,5D is built from three generator vertices: GENIE 2.12 + MEC, NuWro 21.09.1 and GiBUU 2019.
Each is a reweighting of the prior, about the tune-v1 unfold.
- `nd-unfolding/pv-ladder/build_cmodel5d.py:9`: "for k in (GENIE+MEC, NuWro, GiBUU); X_0 is L-5D-PV_e_tune_v1".
- `build_cmodel5d.py:47`: `VERTICES = ("genie_mec", "nuwro", "gibuu")`.
- The vertex labels are at `nd-unfolding/pv-ladder/config.json:54`, `:59` and `:64`.
- The builder, its config, its readout `cmodel_5d.json` and the cell definition were first added and last changed on
  **2026-10-24** (`dfcbb2c6`, `06436fb3`, `3aadb536`, `5c440914`).
- `git grep -E 'G18|AR23|g18|ar23|G1810a|AR2320i'` over those four files is empty, rc 1.

**(2) S1's assembly.** `nd-unfolding/s1_assemble.py` was first added on 2026-10-24 (`6dbc8d20`) and last changed on
2026-10-24 (`fe5d79c6`). It takes C_model as a pinned input (`s1_assemble.py:292–293`:
`--cmodel` and `--cmodel-sha256`). The same tune grep over it is empty.

**(3) The estimator.** The production path is:
- `s5e_candidate.py`: candidate R, first and last changed 2026-09-25 (`700797e3`);
- `s5n_pseudo.py`: last changed 2026-09-25 (`82dc1517`);
- `s5c_unfold.py`: 2026-09-24 (`50402c0a`);
- `s5c_pseudo.py`: 2026-09-25 (`55759309`);
- `omnifold_nn_core.py`: 2026-06-04 (`7916931f`).

The toys' configuration is `CONFIG, ESTIMATOR_SEED, ITERS = "R", 42, 5` (`nd-unfolding/fd_1b_toys.py:73`). The tune
grep over these files, `xsec_nd.py`, `s5p_universe.py` and `s5p_nullexp.py` is empty, rc 1.

**(4) Where the tunes enter.**
- **First in code** on 2026-10-27: `3d-unfolding/genie/gen5d_v3.py` and `nd-unfolding/fd_f1_prep.py`, both first
  added in `b40761c1` (the F1 declaration).
- **Joseph chose them** for F1 (`FD-F1-DECLARATION.md:45`; `67050098`, 2026-10-27).
- **Later uses:** F1's bias test, which graded against the reported C_total + C_resp and "CANNOT AUTHORIZE: a reading,
  a claim, paper text, or any statement about coverage" (`FD-F1-REPORT.md:12–13`); 1B's arms; and the paper's statement (`paper_body.tex:190`): "generated
  for this test and held out of the analysis".
- **No record feeds back.** Every F1 and 1B record that names the tunes post-dates items (1)–(3), and none changes
  them.

**(5) An earlier mention, reported as found.** The tunes are first named on 2026-10-11, in the inelastic high-region
memo (`f0352ea4`). Its V2 proposal names them (`state/inelastic-high-region-20261011/REPORT.md:19`), and the memo
"authorizes nothing, adopts nothing" (`REPORT.md:5–6`).
- `git grep -l inelastic-high-region-20261011 -- docs/orchestration/DECISION-* nd-unfolding` is empty, rc 1. No
  decision record or measurement code in those paths cites it.
- Between 2026-10-12 and 2026-10-25, documents in the research, 2D-closeout and FD-plan lanes mention them
  (`provenance.out`, `-S` lists). None is in C_model's, S1's or the estimator's files.

**(6) "Held out" is not "independent".** F1's declaration records two overlaps (`FD-F1-DECLARATION.md:292–300`):
- **G18_10a carries the Valencia 2p2h** (`NievesSimoVacasMECPXSec`). C_model's GENIE + MEC vertex is GENIE 2.12 +
  Valencia MEC, so part of G18's departure lies along a direction C_model already holds.
- **AR23_20i uses SuSAv2 2p2h,** not Valencia. It shares G18's CCQE model, `NievesQELCCPXSec`, so **the two truths
  are not independent of each other.**
- **So,** as F1 did, stage 1 reports a descriptive C_model variant without the GENIE + MEC vertex (§5.4). Every report
  states both overlaps.

**(7) Tuning.** The nominal simulation is MnvTune v1.
- No search here shows either tune entering it, and the estimator was fixed before either tune was generated (items
  3–4). <!-- absence-ok: scoped to items (1)-(5)'s queries, which provenance.out prints with their exit status -->
- Whether the GENIE collaboration's AR23 fit used MINERvA data is outside these records and is not claimed either way.
  For method coverage, what matters is that neither tune entered this analysis's construction.

**The paper's qualifier** is at `paper_body.tex:81` at `a4cd6ffc`: "its coverage at truths held out of its
construction has not been validated". The decision cites it as line 80, and the sentence is on line 81 there too. <!-- absence-ok: quotes the paper's existing qualifier (paper_body.tex:81) that a pass would replace -->

## 4. Stage 1: the design

### 4.1 The truths

| truth | definition | pin |
|---|---|---|
| **G18** | G18_10a_02_11b, F1's gated, k-normalised bridged ratio, applied as `s5n_pseudo.truth_weight("ratio_nd", …, 1.0, ratio)`, as the original 1B toys apply it (`fd_1b_toys.truth_ratio`, `truth_model`) | the committed `f1-prep-SHA256SUMS` digest, checked by `fd_1b_toys.truth_ratio` |
| **AR23** | AR23_20i_00_000, the same | the same |
| **plug-in** (optional, §6) | the unfolding's own final truth weights at the data | the capture product's digest |

### 4.2 The pseudo-data: every group drawn

One toy is one nature, drawn from `numpy.random.default_rng([seed, DRAW_SALT])` in `fd_1b_toys.draw`'s order, then
unfolded once.

| group | the nature drawn | as in |
|---|---|---|
| stat | Poisson pseudo-data at data size on every reco-passing MC row and every background row, plus set A's MC and template Poisson(1) streams at the toy's seed | `fd_1b_toys.build_full`, `mc_template_streams` |
| flux | one of the 100 PPFX universes, with probability w_u / Σw. Nature's flux, truth weights, reco weights, denominator and background are u's | S1's flux block (weights from `s1_assemble.flux_weights`); u's arrays as `s5p_universe.universe_inputs` gives them |
| interaction | each of the 33 bands at one of its universes, uniformly: a pair band at either endpoint with probability ½, 2p2h at one of 3. **Nature = universe:** truth weights, reco weights, denominator and background all become the universe's, **not** truth-preserving | mode D (#655 §2), which κ gates. This replaces the original toys' truth-preserving g_f, the cause of gate D's mismatch |
| detector | the 4 weight-only bands, each at endpoint 0 or 1 with probability ½, from the detector dump (reco and background weights) | the original toys; S1 choice 7 |
| lateral | the declared surrogate: x̂ += Σ_b s_b Δ_b(T) / 2 with s_b = ±1, and Δ_b(T) S1's lateral endpoint difference transferred to the truth (§4.4) | `fd_1b_score.surrogate`; `FD-1B-DECLARATION.md` §3 |
| normalization | x̂ × (1 + 0.014 z), z ~ N(0, 1) | S1's 1.4 % |
| seed | not drawn. The estimator seed is 42, and S1 measured the block as exactly zero | S1-REPORT §7 |

**Composition.** When several universes are drawn together, their weight ratios to the CV multiply, row by row: truth
weight, reco weight, background weight and the denominator's per-event weight (tdw). This is how
`ne.ModelCache.product` already composes reco and truth factors. There is at most one flux universe, and it sets the
flux histogram. Non-finite weights are zeroed, as S1's loader does.

**Each toy's truth** is the nature's own: `true_xsec` over the composite truth weights × r_T, with the composite
denominator and the nature's flux. The error is **e = U x̂ − U x_true**, after the lateral and normalization
surrogates.
- So coverage is graded over natures drawn about T under the systematic model, each against its own truth. At T =
  nominal, this is κ's construction, with the other groups and the Poisson draws added.

**Toys:** 300 per truth, at seeds 3,620,000–3,620,299 (G18), 3,630,000–3,630,299 (AR23) and 3,640,000–3,640,299
(plug-in). `arith.py` checks these ranges and the stat-realization seeds of §4.3 against every `.tsv`, `.py`, `.sh`,
`.json` and `.md` file: none occurs (`declared_seeds_found_in_repo: []`).
- A first choice, 2,72x,xxx, collided with an unrelated index (`2720019`, in a G2 receipt), and was moved.

**Not drawn:**
- C_model: a fixed-truth draw cannot produce it. Nature's departure from the MC is real here, and C_model is what
  should cover it;
- C_resp: the decision's nominal-response scope;
- C_PL,5D: built from the data's run-period groups, which no simulation draw produces.

### 4.3 The covariance remade at each truth

**The reported procedure** is `s1_assemble.py`:
- C_e = C_stat + Σ_b C_b + C_norm + C_seed, with C_total = C_e + C_model_abs;
- the reported covariance adds C_resp and C_PL,5D (`paper_body.tex:81`).

**At truth T, the data are replaced by T's pseudo-data at their means** (nominal response, every Poisson draw at its
mean): d_T. Each block is then remade as S1 made it from the data:

| block | at T | unfolds per truth |
|---|---|---:|
| central x̂_T | d_T unfolded with the nominal MC | 1 |
| flux | d_T unfolded with each Flux universe's MC (`universe_inputs`, flux file), constraint-weighted `mat_cov` | 100 |
| interaction | d_T with each interaction universe's MC, MAT mean-centred per band (`mat_cov`), summed over 33 bands. This is I2's mode A, at T instead of the nominal truth | 67 |
| detector | d_T with each of the 8 detector universes' MC | 8 |
| stat | set A's procedure applied to **one** Poisson realization of T (seed 3,621,000 / 3,631,000 / 3,641,000): replicas b = 1–50 by `s5n_pseudo.bootstrap_replica`, the refinement refit per replica, the per-replica index j = 100 + b that set A's product names carry (`data_b<b>_j<100+b>`), sample covariance (ddof 1). A bootstrap needs integer counts, so it cannot run on d_T | 50 |
| seed | **not remade.** S1's C_seed is 100 unfolds that measured exactly zero. One check per truth instead: x̂_T at estimator seed 45 must equal seed 42 bitwise, or INVALID | 1 |
| normalization | (0.014 x̂_T)(0.014 x̂_T)ᵀ: the procedure itself, at T | 0 |
| C_model_abs | diag(x̂_T) C_model diag(x̂_T): the procedure itself, with f → x̂_T, using the pinned fractional C_model,5D | 0 |
| lateral | **carried, not remade** (§4.4) | 0 |

That is **227 unfolds per truth.**
- **d_T at its means** is the procedure's expected block at T. A block remade per toy, as a strict "same procedure"
  would need, is 300 × 226 unfolds per truth and is not priced. Its toy-to-toy variation is the data draw's
  effect (#655 §3.3 (iii)), which no means construction reaches. The report states this.
- **The graded matrix is C_T = C_e(T) + C_model_abs(T).** Its 16 × 16 diagonal gives the per-cell interval.

**Why C_resp and C_PL,5D are left out of the graded matrix.** Neither is drawn, so adding them would credit intervals
with covering errors the toys never contain.
- Both are positive semi-definite. Adding them makes every per-cell interval wider and every χ² smaller
  ((C + P)⁻¹ ≼ C⁻¹).
- **So a cell or a χ² region that covers under C_T also covers under the reported covariance at T.** An under-coverage
  under C_T is not shown to persist under the reported covariance. Every report says so.

### 4.4 The lateral block, carried

The 5D lateral dumps no longer exist, so the lateral bands cannot be remade at any truth (`FD-1B-DECLARATION.md` §3,
`fd/receipts-1b/stage1/cluster-reads.out` of 2026-10-30).
- **At T,** S1's lateral blocks are transferred in relative form, as the original 1B rule does (its §2): Δ_b(T) =
  Δ_b ∘ (x̂_T / f) per cell, and C_lat,b(T) = ¼ Δ_b(T) Δ_b(T)ᵀ.
- **In the toys,** the surrogate draws the same Δ_b(T).
- **So the lateral block is carried at each truth, not tested.** Its share of S1's C_total trace is 0.1406
  (`FD-1B-DECLARATION.md` §3). Every report and the paper text (§12) state this.

### 4.5 Why stage 1 can fail (inference, not measured)

Write the estimator to first order about the nominal MC m₀ as U(d; m) ≈ T(m) + R(m)(d − d(m)). Take a universe u,
with δ = m_u − m₀.
- **At T = nominal,** S1's shift and the toy's error are equal and opposite (#655 §3.2). That is why κ = 1 at first
  order.
- **At T ≠ nominal,** the remade block's shift carries an extra term, δR · (d_T − d(m₀)): the response's change times
  the truth's departure. The toy's error is R₀ Δd_T − ΔT_T, with both Δs at T.
- **Closure fixes no first-order relation between them** off the diagonal, so stage 1 is a test with power to fail
  in either direction.
- **No outcome is predicted.** I2's F_truth (median 0.68 between the nominal and data points) shows that the
  interaction block moves materially with the truth, and that is all this inference rests on.

## 5. Grading, fixed before any number is read

All thresholds are computed by `arith.py` and committed in `arith.out`. They are not retyped by hand in code: §11's
scorer imports them or recomputes them with the same function and checks the values.

### 5.1 Statistics per truth T, over its 300 toys

- **Per-cell in-interval fraction** p̂_c = #{t : |e_tc| ≤ σ_c} / 300, with σ_c = √(C_T)_cc. The nominal content is
  P₀ = erf(1/√2) = 0.682689.
  - It is reported with its Clopper–Pearson interval at 95 %, two-sided.
- **χ² on the non-null subspace.** Eigendecompose C_T and keep the eigenvalues above 10⁻¹² of the largest (S1's
  rank convention, S1-REPORT §4). Then χ²_t = Σ_k (v_kᵀ e_t)² / λ_k over the kept k, with ndf the number kept.
  - If ndf = 16, the code checks that χ²_t equals the Cholesky χ² the paper uses (`paper_body.tex`, "Every χ² …
    by Cholesky decomposition") to 10⁻⁹ relative, or INVALID.
- **The joint in-region fraction** q̂ = #{t : χ²_t ≤ F⁻¹_{χ²(ndf)}(P₀)} / 300, with its Clopper–Pearson interval.
- **Pulls,** per cell: the mean and standard deviation of e_tc / σ_c, with their standard errors. These are
  descriptive.
- **Mean χ²/ndf** with its standard error (0.020 at ndf 16 for an exact χ²). Descriptive.
- **The under-coverage factor,** per cell: k_c = Q_{P₀}(|e_tc|) / σ_c, the scale σ_c would need for the content P₀.
  Descriptive. It is the "by a factor" of §12's failure text.

### 5.2 The rule, per truth

| reading | condition |
|---|---|
| **cell c under-covers** | #{|e_tc| ≤ σ_c} ≤ **181** of 300. Equivalently, the one-sided Clopper–Pearson upper bound at 1 − 0.05/16 = 0.996875 is below P₀ (Bonferroni over the 16 cells) |
| **joint under-coverage** | #{χ²_t in region} ≤ **190** of 300. Equivalently, the one-sided upper bound at 0.95 is below P₀ |
| **COVERS at T** | no cell under-covers, and there is no joint under-coverage |
| **UNDER-COVERS at T** | otherwise. The report names each cell and states whether the joint fraction is under too |
| **INVALID at T** | any §9 control fails for T. Reported unrepaired; the other truths are still graded if their controls pass |

**The rule is one-sided.** Over-coverage is reported, but it is not a failure:
- a cell **over-covers** if its count is at least **227** (the lower bound at 0.996875 is above P₀);
- C_model is an unscaled envelope, so over-coverage where it dominates is expected, and the paper text states the
  fractions (§12).

**Size and power** (`arith.out`):
- At true content P₀, the chance of a cell flag is 0.0022 per cell, and 0.035 over 16 independent cells. A joint flag
  has chance 0.039.
- A cell is flagged with probability 0.57 at true content 0.60, 0.81 at 0.58 and 0.97 at 0.55.
- The joint fraction is flagged with probability 0.70 at 0.62 and 0.89 at 0.60.
- **So stage 1 resolves under-coverage of about 0.08–0.10 in content per cell, or 0.06 jointly.** Smaller deficits can
  pass, and the report states the resolution beside any COVERS.

### 5.3 What is graded where

- **G18 and AR23:** §5.2's rule. These are the decision's held-out tunes.
- **Plug-in** (if run): the same rule. Its reading is labelled "at a truth made from the data". The truth is not held
  out of the data, but it is held out of the construction of C_model and the estimator.

### 5.4 Descriptive readouts, no verdict

- **The spread alone:** pulls and p̂ against C_e(T), without C_model. It shows how much of the coverage is C_model's
  doing.
- **The bias:** the toys' mean error, U-weighted, against σ_c, per cell. It is F1's bias at the nature-drawn truth, as
  a check against F1 (`FD-F1-REPORT.md:39`, |z| ≤ 0.644).
- **The leave-out-MEC variant:** §5.1's statistics with C_model rebuilt from NuWro and GiBUU only, as F1's descriptive
  variant (§3 (6)). It is read for G18 especially.
- **4A-style correlation:** the toys' 16 × 16 sample covariance against C_e(T), as eigen-direction variance ratios.
  Descriptive only, since the addendum's 4A belongs to the superseded design.

## 6. The plug-in truth (optional, priced separately)

**What it is:** the nominal MC's truth reweighted by the unfolding's own final per-event push weights at the data. It
is the unfolding's estimate of nature, made by the production run on the data, the consult's first choice.

**The code change is small and does not touch production code.**
- `s5c_unfold.unfold` takes the push weights from `onc.omnifold_loop` (`s5c_unfold.py:124`), where `onc` is the module
  `omnifold_nn_core`, imported by name (`s5c_unfold.py:47`). It discards them after the histogram
  (`s5c_unfold.py:138`).
- `s5n_pseudo.unfold_negweight` accepts an `unfold_fn` (`s5n_pseudo.py:330`).
- **The capture** is an `unfold_fn` that calls `s5c_unfold.unfold` unchanged while `s5c_unfold.onc.omnifold_loop` is
  wrapped for that one call. The wrapper returns `(w_pull, w_push)` untouched (`omnifold_nn_core.py:268`) and keeps a
  copy of w_push.
  - `omnifold_nn_core.py` has no `subprocess`, `multiprocessing` or `Pool(` (count 0), so the call runs in-process,
    and a module-attribute wrap is not bypassed by a from-import.
  - It is about 30 lines, plus tests.
- **The run:** one unfold of the **real data** by S1's central path (candidate R, `s5n_pseudo --data`) with the
  capture. This re-reads the data inputs S1 read. The data have been read before, and nothing new is unblinded. It is
  flagged for the director (§14.4).

**Its controls,** each a hard INVALID for the plug-in only:
- **(a)** the captured run's x̂ equals S1's central product (`CENTRAL_SHA256 fb5cc679…`) bitwise;
- **(b)** the plug-in truth is r_i = w_push,i on truth-passing rows (1 elsewhere), with the denominator reweighted
  cell by cell as `s5p_universe.prior_inputs` does. Its U x_T must equal U f to 10⁻¹², as Ddl's control did (#655 §8);
- **(c)** the weights' digest is in every plug-in product.

**What it adds and what it cannot:**
- it reaches the data's truth shape within cells, (i), and the reco-level shape as far as the unfolding's own fit,
  (ii) (#655 §3.3);
- at means, it does not reach the data's draw, (iii);
- the weights carry the data's draw into the truth. Its toys then draw fresh noise about that truth, and the report
  states this.

**The price:** 528 unfolds (§8).

## 7. The truth dependence: readouts beside the coverage result

All are fractional, so the carry cancels: for a block B at truth T with central x̂_T, b_c = √B_cc / x̂_T,c.
- **A_T / A_nom** per cell, interaction group: b_c of the remade interaction block at T against b_c of I2's A at the
  nominal truth. The latter is from the committed `i2.json` with its own U x_T, and A/f² is carry-invariant (#655
  §3.1).
- **Each group at T against M,** per cell: b_c(T) / (√M_cc / f_c) for flux, interaction, detector and stat. M is S1's
  block at the data, from the staged S1 assembly.
- **M′ against M** (plug-in only): the same per group, with M′ remade at the plug-in truth. Its interaction-group
  ratio against I2's F_truth shows how much of the block's truth dependence the plug-in reproduces.

They are stated as facts, with no window and no verdict (decision item 3).

## 8. Price

**The measured costs:**

| path | measured | source |
|---|---|---|
| a change on the MC side (all remade blocks) | max 849.6 s, median 725.1 s per unfold | `fd/receipts-1b/inv/i2/connect24-post-bulk.out` (I2, 204 unfolds) |
| a change on the pseudo-data side (toys) | max `seconds_unfold` 801.4 s, `seconds_load` 16.0 s | `FD-1B-STAGE2-REPORT.md` §2 |
| node-h per unfold at 8 lanes | 0.022828 (S1 P1: 2.00889 node-h / 88 universes); 0.022813 (S1 seed job: 1.82500 / 80) | `S1-REPORT.md` §3 table |

**The unit** is 1,062 s (1.25 × 849.6 s), as in mode D. The run uses 8 lanes per node, CPU only, QOS regular,
`--exclusive --no-requeue`, every job under 12 h.

**Items:**
- per tune: 227 remade + 300 toys = 527;
- the 4 procedure controls (§9) once;
- the base, G18 + AR23, is **1,058**;
- the plug-in adds 527 + 1 capture = **528**.

| step | nodes | items | limit | fullest lane at the unit | reserved |
|---|---:|---:|---|---|---:|
| **stage 0** (carried, #655 §7) | 1 + 2 | 104 | 1:00:00, 2:15:00 | — | **5.5** |
| S1-0, the pilot: 4 controls, G18 x̂_T, G18 toy 3,620,000, AR23 stat replica b = 1, and the capture (or AR23 toy 3,630,000 without the plug-in) | 1 | 8 | 1:00:00 | 1,062 s | **1.0** |
| stage 1 bulk, base | 6 | 1,050 (1,051 with the plug-in) | 8:00:00 | 22 × 1,062 = 23,364 s, 81 % | **48.0** |
| stage 1 bulk, plug-in | 3 | 527 | 8:00:00 | 23,364 s, 81 % | **24.0** |

**The caps:**
- stage 1 without the plug-in: **49.0 node-h**, or **54.5** with stage 0;
- stage 1 with the plug-in: **73.0 node-h**, or **78.5** with stage 0.

**The expectation at S1's measured rate** (0.022828 node-h per unfold) is 24.2 node-h for the base and 36.2 with the
plug-in. At I2's median and 8 lanes it is 26.6 and 39.9.

**The re-price trigger** is as mode D's. After S1-0, the walls must be at most 1,062 s per unfold and the peak RSS at
most 44,040,192 KiB, or REPRICE, which is an amendment.

**The balance.** The last read was `iris` at 2026-11-01T19:27Z: 2,069.4 node-h remain, so half is 1,034.7. The
campaign's largest cap, 78.5, is below half, so the standing approval covers it (decision item 4). The first connect
re-reads the balance, and if the cap is then above half, it goes to Joseph before any submission.

**Storage:** an HPSS copy at each step's end, with `hpssquota` read first. Nothing goes to CFS.

## 9. Controls

Any failure reads INVALID and is reported unrepaired.

**The procedure controls,** run in S1-0. Each re-runs a block's path on the **real data** and must reproduce S1's
product bitwise:
- set-A replica b = 1 (`data_b1_j101.npz`, against the Stage 0 inventory digest);
- interaction universe MaRES_0;
- flux universe Flux_0;
- detector universe GEANT_Pion_0 (against S1's universe products, by the S1 readout's digests).

These show that stage 1's remade blocks use S1's code path, not a second implementation. A failure is INVALID for all
of stage 1.

**Per truth:**
- **The truth pin:** the ratio digest equals F1's committed sum (`fd_1b_toys.truth_ratio`).
- **The seed check:** x̂_T at seed 45 equals seed 42 bitwise (§4.3).
- **Consistency of d_T:** the toy path at T with no draws and every Poisson draw at its mean builds the same
  experiment arrays as the remade blocks' d_T, bitwise. This costs no unfold.
- **C_T** is symmetric to 10⁻¹² and positive semi-definite at 10⁻¹² relative; ndf is recorded. If ndf = 16, the
  Cholesky check of §5.1 applies.
- **One code and one input set** across every product of a truth: `code_sha256`, the input, background and pins
  digests, configuration, iterations and estimator seed.
- **Every product names its own** truth, role (toy, remade block, stat replica or control), universe and seed.
- **The toys' seeds** are exactly the declared range: none missing and none extra.

**Reads:** every input not made by this lane is read with `O_NOATIME`. EPERM is raised, never retried. Each job
writes an atime sidecar and exits with 8 set if an atime moved, which is a deviation, reported unprompted and not
restored. This is #655's mechanism, in §11's code.

**The plug-in:** §6 (a)–(c).

## 10. Order, connects and routing

The director is told before each connect and each submission. **The audit gets each report before the next
submission.**

1. **Binding 1** (this declaration). Then connect 25 reads `iris`, `hpssquota`, `squeue` and the stat of the staged
   inputs. Connect 26 makes a fresh deploy at the binding's merge, then stage 0's D-0.
2. **D-0's readout** goes to the audit and the director. The stage-0 bulk goes after walls PASS and the audit's
   written acknowledgement. If none comes within 2 h, I message the director and do not submit.
3. **Stage 0's report:** rule K. Then the gate (§2).
4. **Binding 2:** §11's code, as an amendment that changes no rule here. It may be prepared while stage 0 runs and is
   reviewed by the audit.
5. **S1-0,** after stage 0's PASS, the audit's acknowledgement of stage 0's report and binding 2. Its readout goes to
   both.
6. **The stage-1 bulk,** after S1-0's walls PASS, its controls pass and the audit's written acknowledgement.
7. **The readout,** the HPSS copy and the report, to the audit and the director, and through the director to Joseph.

## 11. Stage 1's code, to come as binding 2

The code is not written in this revision. It will import and not copy:
- the draws and source factors (`fd_1b_toys`);
- the nature arrays (`s5p_universe.universe_inputs`, `fd_1b_moded.d_experiment`'s construction);
- the remade blocks (`fd_1b_inv.mode_inputs("A", …)`, `s1_assemble.mat_cov`, `flux_weights`, `model_abs`);
- the surrogates (`fd_1b_score.surrogate`);
- the bootstrap (`s5n_pseudo.bootstrap_replica`);
- the capture (§6).

**The tests** will include, at least:
- the composition rule (§4.2) against single-universe arrays;
- the truth's flux and denominator under a flux draw;
- every §9 control in both directions (it fires on a defect and is silent on a correct run);
- §5.2's thresholds against `arith.out`;
- the Cholesky equality;
- the one-sidedness;
- the capture's bitwise identity with the uncaptured unfold, on a toy.

**A mutation receipt** will follow #655's form, with digests, counting a kill only on a test failure.

**If any rule here proves unimplementable as written,** that is a finding for an amendment, not a silent change.

## 12. The paper, in each outcome (decision item 5), fixed now

Bracketed values are filled from the report's readout only. <!-- absence-ok: quotes the paper's existing qualifier (paper_body.tex:81) that a pass would replace --> The sentence replaced is `paper_body.tex:81`'s "and its
coverage at truths held out of its construction has not been validated". What follows it, "and the first two tests of
an earlier route to a calibrated model term with validated coverage did not pass (…)", is kept as history unless
Joseph rules otherwise (§14.5).

**Both tunes COVER:**
> At two GENIE v3 tunes held out of the analysis, G18_10a_02_11b and AR23_20i_00_000, pseudo-data drawn with the
> statistical, flux, interaction, detector, lateral and normalization uncertainties and unfolded with the nominal
> simulation had errors covered by $C_{\mathrm{total}}$ rebuilt by the same procedure at each tune's truth
> ($\chi^2/\mathrm{ndf}$ = [a] and [b]; per-cell 68\,\% content [p–q]\,\% and [r–s]\,\%). The lateral block was carried
> to each truth, not rebuilt, and $C_{\mathrm{resp}}$ and $C_{\mathrm{PL,5D}}$, which were not drawn, were left out,
> which can only widen the intervals. This tests the method at two truths, which share their quasielastic model; it
> is not a coverage rate and not a property of the reported intervals in nature. The interaction block depends on
> the truth at which it is built: [the median per-cell ratio of A_T to A_nom and of the nominal to the data block,
> 0.68].

**One tune covers and the other under-covers** (per tune, as decision item 2 requires):
> At G18_10a_02_11b [or AR23], … covered (…). At AR23_20i_00_000 [or G18], the covariance rebuilt at its truth
> under-covered in cells [list] by factors [k_c], and [jointly / not jointly]; the uncertainties in those cells
> should be read as lower bounds at truths like that tune's.

The scope sentences of the pass text are kept.

**Both tunes under-cover:**
> At both held-out tunes the covariance rebuilt at each truth under-covered: at G18_10a_02_11b in cells [list] by
> factors [k_c], at AR23_20i_00_000 in cells [list] by factors [k_c]. The uncertainties in those cells should be
> read as lower bounds.

No covariance is inflated without Joseph.

**The plug-in,** if run, adds one clause in any case: "[and at a truth reweighted to the unfolded data, (covered /
under-covered in cells …)]".

**Stage 0 FAIL, PARTIAL without Joseph's go-ahead, INVALID, or no result:** the paper is unchanged, and the
stopped-attempt disclosure stays.

**In every outcome,** the note states:
- the resolution of §5.2, about 0.08–0.10 in content per cell;
- the two overlaps of §3 (6);
- that the d_T-at-means block stands in for a per-toy block.

## 13. What stage 1's report can and cannot say

**MEASURES:** per truth, §5's statistics and §5.2's reading; §7's readouts.

**CANNOT SUPPORT:**
- **a coverage rate,** or coverage at truths unlike these two;
- **that the reported intervals cover nature;**
- **anything about the lateral block, C_resp or C_PL,5D,** none of which is tested;
- **the response model:** every nature uses the nominal detector response;
- **a block remade per toy** (§4.3).

An under-coverage under C_T is not shown to persist under the full reported covariance (§4.3). A pass under C_T
carries over to it.

## 14. For the director

1. **#655: closed unmerged, with its four artifacts carried here byte-identical** (§2). The code, tests and mutation
   receipt are stage 0's. `FD-1B-MODED-DECLARATION.md` is the record of the design finding (its §3), and it lands on
   `main` with this PR.
   - I chose this over merging #655 because #655 conflicts with `main` in the generated `MANIFEST.tsv`, and carrying
     the files lands one current version once.
   - I will not close #655 myself until you confirm.
2. **PARTIAL at stage 0** (§2): I declare that stage 1 waits for Joseph. The decision names only FAIL as a stop, so
   this is your ruling.
3. **The plug-in** (§6): included, priced separately at +24 node-h of cap (73.0 for stage 1, 78.5 with stage 0). The
   code is small and touches no production file. Drop it if you prefer: the base stands alone.
4. **The plug-in's capture re-reads the real data** once, by S1's central path, and must reproduce S1's central
   product bitwise. The procedure controls of §9 also re-run four S1 data unfolds.
5. **The kept clause of `paper_body.tex:81`** about the earlier route (§12) is Joseph's to rule on if a pass lands.
6. **Binding 2** (§11) is a separate binding of code against these fixed rules. It lets stage 0 run while the code is
   written and reviewed.
