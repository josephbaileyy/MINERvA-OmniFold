# DECLARATION 1B staged method coverage, revision 2: stage 0 κ as the hard gate, then held-out-tune coverage with the covariance remade at each truth (2026-11-01)

**By** the measurement session `coverage-5b`, for `coverage-5b-audit` to review and the director to bind.

**What changed from revision 1** (head `589cfcbc`), on `coverage-5b-audit`'s review (issuecomment-6570466640),
upheld by the director:
- **R1.** §4.5's power argument now rests on the estimator's prior dependence, measured by I2's mode C (C/A median
  0.476), not on F_truth, and it states what is expected at first order if the procedure is sound.
- **R2.** §5.2's null is no longer the Gaussian P₀. It is simulated from the declared draw laws under an exactly
  matched C_T, by a declared function (`nd-unfolding/fd_1b_null.py`, new here with 23 tests and an 18-of-18 mutation
  receipt), evaluated at each truth before any toy error is read.
  - The family size per truth is now ≤ 0.05 by construction (0.025 over the cells, 0.025 joint), against revision 1's
    0.074. Across truths it is ≤ 0.10, or ≤ 0.15 with the plug-in.
  - `arith.py` checks the null at the data's point from committed readouts, with the lateral split bracketed.
- **R3.** §4.2 states one composition rule. It reduces exactly to S1's single-universe arrays and keeps S1's
  treatment of zero, negative and non-finite weights. §9 adds a bitwise control against κ's nature, and binding 2's
  first receipt counts the rows where the rule departs from a pure product.
- **M1:** every flag gets a bias-versus-width attribution (§5.1), and §5.4 adds the predicted offset of the
  un-centred draws. **M2:** sizes are stated per truth and across truths (§5.2), and clause F carries them (§12).
  **m1:** clause P's χ² carry-over needs ndf = 16. **m2:** §6's control (b) is labelled a plumbing check.
- **Stage 0 is untouched** and stays byte-identical to `55435ec0`.

**What changed from revision 0** (head `466b6ac7`), on the director's two points before the audit's review:
- **Point 1.** A pass carries over to the procedure's full covariance at the ensemble's truth T, not to the reported
  covariance made at the data's point. This is reworded at every site that stated it (§4.3, §13), and §12's paper
  text claims no more.
  - Clause F no longer says "lower bounds" (§12).
- **Point 2.** The tunes' overlaps with C_model and with each other are in the paper text's scope in every outcome
  (§12, clause T: G18 "only partly held out").
  - The leave-out-MEC variant's reading is fixed before any number is read (§5.4).
- **The director ruled on §14.2:** a stage-0 PARTIAL waits for Joseph.
- **#655 is closed unmerged,** with a pointer to this PR.

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

**Composition: one rule (revision 2, the audit's R3).**

**Loading.** Each drawn universe's arrays are first loaded exactly as S1's block and κ load them:
`s5p_universe.weights(bank, tag, nonfinite="zero")` (the detector dump for the detector bands), then
`s5p_universe.universe_inputs`. So non-finite weights are zeroed, and negative weights are kept.

**The rule.** Take a draw D = (u₁, …, u_k) in `fd_1b_toys.draw`'s order: the flux universe, the interaction bands
sorted, then the detector bands. Each per-row array a ∈ {w_truth, w_reco, bkg_w, tdw} composes as follows.
- **On rows where a_CV ≠ 0:** a_D = a_{u₁} ⊙ Π_{j≥2} (a_{u_j} / a_CV). Negative ratios are kept, and nothing is
  clipped.
- **On rows where a_CV = 0,** where no ratio exists: a_D = a_{u₁} + Σ_{j≥2} a_{u_j}.

**What it reduces to.** For k = 1 the product and the sum are empty, so a_D = a_{u₁} exactly. A single drawn universe is
therefore S1's and κ's nature bitwise. This is a §9 control and a test in binding 2.

**The other arrays:**
- **The denominator** is `s5p_universe.denominator` of the composite tdw, as `universe_inputs` builds it.
  - A detector-dump universe that carries its own `denom_nd` histogram enters by its cell ratio to the CV's
    histogram, on cells where the CV is > 0. For k = 1 this again gives `universe_inputs`' array.
  - Binding 2's first receipt compares each detector universe's `denom_nd` with the CV's. If they are bitwise equal,
    the factor is 1 and the branch is inert, and the receipt says which.
- **The flux histogram** is the one flux universe's (`flux_universe_bins`), as in `universe_inputs`.

**Not used:** the `ne.ModelCache` / `checked_ratio` path (ratio 1 where the CV ≤ 0, negatives clipped, no tdw), which
revision 1 named by mistake.

**Counted before S1-0, in the real bank, by binding 2's first receipt (login node, 0 node-h),** per universe and
array:
- rows with a_CV = 0 and a_u ≠ 0;
- rows with a_CV < 0;
- rows with a_u < 0;
- rows non-finite before zeroing.

These are the rows where the rule departs from a pure product of ratios, or where S1's loader alters a weight.

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
- **So a pass carries over to the procedure's full covariance at T:** C_T + C_resp(T) + C_PL,5D(T), every block at
  the ensemble's truth T. A cell that covers under C_T also covers under that matrix.
  - The χ² region carries over only when both matrices have ndf = 16 (the audit's m1). With a rank-deficient C_T, the
    non-null χ² drops components the full-rank matrix counts, and the χ² quantile changes with ndf.
  - S1's C_total has rank 16 at 10⁻¹² (`s1_assembly.json`), so the condition is expected to hold. It is checked, not
    assumed.
- **It does not carry over to the reported covariance,** which is made at the data's point. The block's dependence on
  the truth at which it is made is the finding that led here (I2's F_truth, §7). Nothing in stage 1 relates C_T to the
  matrix made at the data.
- **An under-coverage under C_T** is not shown to persist under the procedure's full covariance at T.
- Every report says all three. (Director's point 1, on #664.)

### 4.4 The lateral block, carried

The 5D lateral dumps no longer exist, so the lateral bands cannot be remade at any truth (`FD-1B-DECLARATION.md` §3,
`fd/receipts-1b/stage1/cluster-reads.out` of 2026-10-30).
- **At T,** S1's lateral blocks are transferred in relative form, as the original 1B rule does (its §2): Δ_b(T) =
  Δ_b ∘ (x̂_T / f) per cell, and C_lat,b(T) = ¼ Δ_b(T) Δ_b(T)ᵀ.
- **In the toys,** the surrogate draws the same Δ_b(T).
- **So the lateral block is carried at each truth, not tested.** Its share of S1's C_total trace is 0.1406
  (`FD-1B-DECLARATION.md` §3). Every report and the paper text (§12) state this.

### 4.5 Why stage 1 can fail (inference, not measured; revision 2, the audit's R1)

**The setup.** Write B(m_n, m_s) = U(D(m_n); m_s) − T(m_n): the estimator's error when nature is m_n and the
unfolding uses the simulation m_s. Closure is B(m, m) = 0 for every m.
- At truth T, a toy drawing universe u has error B(m_T ⊕ u, m₀).
- The remade block's shift for u is B(m_T, m_u) − B(m_T, m₀).

**The invariance.** Take an estimator that depends on the simulation only through its response p(reco | truth):
prior-independent.
- Then B depends on (m_n, m_s) only through the difference of their responses, and vanishes when they agree.
- Stage 1's truths are truth reweights, so they leave the response unchanged. A universe changes the response by the
  same δK on m_T as on m₀.
- **So at every T,** the toy's error and the remade shift are equal and opposite at first order, band by band, as on
  the diagonal (#655 §3.2).
- **The block's truth dependence (I2's F_truth) sits on both sides of that equality,** so it gives no power. It is
  dropped as a ground.

**Where the power comes from: the prior dependence.** That is the estimator's response to the simulation's truth
distribution at a fixed response.
- I2's mode C measures it directly. Mode C is a pure prior reweight (`fd_1b_inv.prior_mc`), and a prior-independent
  estimator gives C = 0.
- `i2.json`'s `prior_share_C_over_A` has median **0.476**, range 0.156–1.390 over the 16 cells (`arith.out`).
- The prior enters the toy's error and the remade shift with different weights once m_T ≠ m₀. The difference is first
  order in the truth's departure times that sensitivity, and it can go in either direction.
- The same prior dependence sets the zeroth-order term B(m_T, m₀), F1's bias.

**What is expected at first order if the procedure is sound** (the covariance procedure describes the error at T):
- each cell's in-interval count is consistent with the draw-matched null p_c(T) of §5.2, and the joint count with
  q(T);
- the toys' mean error is B(m_T, m₀) plus the un-centred draws' offset (§5.4). It is C_model's term that must absorb
  B(m_T, m₀);
- departures are expected first where the prior share is large and the tune departs most from the nominal.

**No outcome is predicted.**

## 5. Grading, fixed before any number is read

**One implementation.** Every threshold is computed by `nd-unfolding/fd_1b_null.py`:
- at each truth, from its null, by §11's scorer, which imports the module;
- here, by `arith.py`, which imports it too and checks its binomial duality against scipy's Clopper–Pearson.

The module's tests and mutation receipt are in this PR. The numbers below are committed in `arith.out`.

### 5.1 Statistics per truth T, over its 300 toys

- **Per-cell in-interval fraction** p̂_c = #{t : |e_tc| ≤ σ_c} / 300, with σ_c = √(C_T)_cc. It is read against the
  draw-matched null content p_c(T) of §5.2, not against the Gaussian P₀ = erf(1/√2) = 0.682689, which is printed
  beside it.
  - It is reported with its Clopper–Pearson interval at 95 %, two-sided.
- **χ² on the non-null subspace.** Eigendecompose C_T and keep the eigenvalues above 10⁻¹² of the largest (S1's
  rank convention, S1-REPORT §4). Then χ²_t = Σ_k (v_kᵀ e_t)² / λ_k over the kept k, with ndf the number kept.
  - If ndf = 16, the code checks that χ²_t equals the Cholesky χ² the paper uses (`paper_body.tex`, "Every χ² …
    by Cholesky decomposition") to 10⁻⁹ relative, or INVALID.
- **The joint in-region fraction** q̂ = #{t : χ²_t ≤ F⁻¹_{χ²(ndf)}(P₀)} / 300, with its Clopper–Pearson interval. It
  is read against the null's q(T).
- **Pulls,** per cell: the mean and standard deviation of e_tc / σ_c, with their standard errors.
- **The bias-versus-width attribution, for every flagged cell** (the audit's M1; `fd_1b_null.attribute`):
  - the pull mean and the pull standard deviation, with their standard errors;
  - the count of the centred errors, #{|e_tc − ē_c| ≤ σ_c}.
  - The reading is fixed now:
    - **"bias"** if the centred count is not flagged;
    - **"width"** if it is flagged and the pull mean is within 2 standard errors of 0;
    - **"both"** otherwise.
  - A flag from a bias inside an MSE-exact C_T is real under-coverage at that truth, but a different finding from
    "too narrow". The attribution names which.
- **Mean χ²/ndf** with its standard error (0.020 at ndf 16 for an exact χ²). Descriptive.
- **The under-coverage factor,** per cell: s_c = Q_{p_c(T)}(|e_tc|) / σ_c, the scale σ_c would need to hold the null
  content. Descriptive. It is the "by a factor" of §12's failure text.

### 5.2 The rule, per truth (revision 2: a null matched to the draws)

**Why not P₀.** The declared draws are partly two-point: 32 pair and 4 detector bands at ±endpoints, 2p2h at one of
3, and the 5 lateral bands at s_b = ±1. A sum dominated by one two-point term holds less than P₀ inside its own exact
σ. In the audit's bracket, with one lateral band carrying the lateral block, R00, R01 and R12 would hold 0.648–0.658
under an exactly correct covariance. Against P₀, the per-truth false-flag rate would then be about 0.14, not the
declared 0.035.

**The null, a declared function of the remade blocks** (`fd_1b_null.null_contents`), evaluated at each truth T after
the remade blocks exist and **before any toy error is read**:
- **The laws.** Each drawn band is a discrete law: its universes' centred shift vectors at T, with their draw
  probabilities.
  - A pair band's two endpoints at ½ each, 2p2h's three at ⅓, the 100 flux universes at w_u / Σw, a detector band's
    two endpoints, and a lateral band's ±Δ_b(T)/2.
  - Centring removes the probability-weighted mean, so each law's covariance is its band's block exactly. The tests
    check this against `s1_assemble.mat_cov`.
- **The Gaussian part.** Stat, normalization and C_model_abs(T) are one Gaussian with their summed covariance.
  - C_model is in the null's error on purpose. The rule asks whether C_T's intervals hold their nominal content given
    the draws' shape, and a Gaussian share holds P₀ by definition.
  - Leaving C_model out of the error, as the audit's bracket did, would raise the null to about 0.75 where C_model is
    large. The rule would then flag the bias C_model is built to absorb.
- **The match.** The components must sum to C_T to 10⁻¹² relative, or the null refuses (`check_matched`).
- **The simulation.** 2,000,000 error vectors at seed 3,642,000 give p_c(T) per cell and q(T) for the χ² region.
  - The Monte Carlo standard error is at most 3.3 × 10⁻⁴.
  - Each flag count is computed at the content minus 3 standard errors. That can only lower the count, and so the
    false-flag rate.
- **Where it runs:** in the readout on a login node, at 0 node-h.

| reading | condition |
|---|---|
| **cell c under-covers** | #{|e_tc| ≤ σ_c} ≤ k_c(T), the largest k with P(Bin(300, p_c(T)) ≤ k) < 0.025/16. This is the exact one-sided Clopper–Pearson duality, with Bonferroni over the 16 cells |
| **joint under-coverage** | #{χ²_t in region} ≤ k_J(T), the largest k with P(Bin(300, q(T)) ≤ k) < 0.025 |
| **COVERS at T** | no cell under-covers, and there is no joint under-coverage |
| **UNDER-COVERS at T** | otherwise. The report names each cell and states whether the joint fraction is under too |
| **INVALID at T** | any §9 control fails for T. Reported unrepaired; the other truths are still graded if their controls pass |

**The rule is one-sided.** Over-coverage is reported, but it is not a failure:
- a cell **over-covers** if its one-sided lower bound at 1 − 0.025/16 is above p_c(T). At p_c = P₀ that is a count of at
  least 229;
- C_model is an unscaled envelope, so over-coverage where it dominates is expected, and the paper text states the
  fractions (§12).

**Size** (the audit's M2):
- **Per truth,** the family (16 cell flags and the joint flag) has size at most 0.025 + 0.025 = **0.05** by the union
  bound, whatever p_c(T) and q(T) turn out to be. `fd_1b_null.size` prints the exact sum at the null for each truth.
- **Across truths,** at most **0.10** for the two tunes and **0.15** with the plug-in. A "one tune under-covers"
  outcome carries that size.
- **Revision 1's rule,** 0.05/16 per cell and 0.05 joint against P₀, had 0.074 per truth even with a Gaussian null,
  and about 0.14 in the audit's worst lateral bracket.

**The check at the data's point** (`arith.out` `null_at_data_proxy`, from committed readouts only; a proxy, labelled
as such in `arith.py`):

| lateral split (bracket) | p_c: min, median | lowest cells | k_c there | cells' false-flag sum |
|---|---|---|---|---:|
| 5 equal bands | 0.676, 0.681 | R10 0.676, R00 0.677 | 177 | 0.018 |
| one band carries it | **0.645**, 0.680 | R00 0.645, R01 0.647, R12 0.657 | 168, 168, 171 | 0.018 |

- With the null matched, the cells' false-flag sum stays at about 0.018, and the per truth at ≤ 0.043 with the joint
  at its 0.025.
- The truths' own p_c(T) use the remade shifts themselves, so this bracket only shows the size is held.

**Power,** against the Gaussian null for orientation (`arith.out`): a cell is flagged with probability 0.52 at true
content 0.60, 0.78 at 0.58 and 0.96 at 0.55. The joint count is flagged with probability 0.62 at 0.62 and 0.84 at
0.60.
- **So stage 1 resolves under-coverage of about 0.10 in content per cell, or 0.08 jointly,** below the null.
- Smaller deficits can pass, and the report states the resolution beside any COVERS.

### 5.3 What is graded where

- **G18 and AR23:** §5.2's rule. These are the decision's held-out tunes.
- **Plug-in** (if run): the same rule. Its reading is labelled "at a truth made from the data". The truth is not held
  out of the data, but it is held out of the construction of C_model and the estimator.

### 5.4 Descriptive readouts, no verdict

- **The spread alone:** pulls and p̂ against C_e(T), without C_model. It shows how much of the coverage is C_model's
  doing.
- **The bias:** the toys' mean error, U-weighted, against σ_c, per cell. It is F1's bias at the nature-drawn truth, as
  a check against F1 (`FD-F1-REPORT.md:39`, |z| ≤ 0.644).
- **The predicted offset of the un-centred draws** (the audit's M1): −Σ_b Σ_u p_u (U x̂_u(T) − U x̂_T), over the drawn
  bands and their draw probabilities, from the remade products at no unfold cost.
  - MAT mean-centring drops a band's mean shift from its block, but the toys draw it. The sign is the swap's.
  - It is printed beside the toys' mean error, and is what the mean error minus F1's bias should be at first order.
- **The leave-out-MEC variant,** C_T⁻ = C_e(T) + diag(x̂_T) C_model⁻ diag(x̂_T). C_model⁻ is C_model rebuilt from the
  NuWro and GiBUU shifts only, as in F1's descriptive variant (§3 (6)). §5.1's statistics and §5.2's thresholds are
  applied to C_T⁻ for both tunes. Its reading is fixed now (director's point 2, on #664):
  - **Why only one case can move.** C_model = Σ_k s_k s_kᵀ, so C_model⁻ ≼ C_model and C_T⁻ ≼ C_T. Under C_T⁻ every
    per-cell count and the joint count are at most their counts under C_T.
  - **A tune that UNDER-COVERS under C_T:** its counts can only fall under C_T⁻ (each is read against C_T⁻'s own
    draw-matched null). The variant is printed and adds no reading.
  - **A tune that COVERS under C_T, and also under C_T⁻,** reads "covers without the GENIE + MEC shift".
  - **A tune that COVERS under C_T, but has a cell or the joint count flagged under C_T⁻** by §5.2's thresholds, reads
    "its coverage in cells [list] (and jointly, if flagged) rests on the GENIE + MEC shift".
    - For G18, whose Valencia 2p2h shares that shift's family, this reading **enters the paper text** (§12, clause V).
    - For AR23, no overlap with that shift is recorded. The reading is reported, and it enters the paper text through
      the same clause.
  - **The variant changes no verdict.** §5.2's reading under C_T is the verdict.
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
  cell by cell as `s5p_universe.prior_inputs` does. Its U x_T must equal U f to 10⁻¹², as Ddl's control did (#655 §8).
  - This holds by construction (the audit's m2): `prior_inputs` keeps the CV completeness, so x_T is x̂ by
    `unfold`'s own formula.
  - It checks the plumbing (the right weights, rows and denominator reach the truth). It is not evidence about the
    truth;
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
- **The single-universe nature (the audit's R3).** §4.2's rule with k = 1 gives arrays bitwise equal to
  `s5p_universe.universe_inputs`' for MaRES_0, Flux_0 and GEANT_Pion_0. Its experiment at the nominal truth is bitwise
  `fd_1b_moded.d_experiment`'s, which is κ's nature. This costs no unfold, and a failure is INVALID for all of
  stage 1.
- **The null:** `check_matched` passes at 10⁻¹². The null is computed and committed (its digest in the readout)
  before the scorer opens any toy product.
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

**In this PR:** `nd-unfolding/fd_1b_null.py`, the §5.2 rule's one implementation. It comes with
`tests/test_fd_1b_null.py` (23 passed) and `fd/receipts-1b/staged/mutation_null.{py,out}` (18 of 18 killed, with
digests; a kill counts only on a test failure).

**Still to come, in binding 2:** the toy, block and scorer code. It will import and not copy:
- the draws and source factors (`fd_1b_toys`);
- the nature arrays (`s5p_universe.universe_inputs`, `fd_1b_moded.d_experiment`'s construction);
- the remade blocks (`fd_1b_inv.mode_inputs("A", …)`, `s1_assemble.mat_cov`, `flux_weights`, `model_abs`);
- the surrogates (`fd_1b_score.surrogate`);
- the bootstrap (`s5n_pseudo.bootstrap_replica`);
- the capture (§6);
- the null and the flag rule (`fd_1b_null`).

**The tests** will include, at least:
- the composition rule (§4.2): a single universe bitwise against `universe_inputs`. The fixture holds a CV ≤ 0 row, a
  CV = 0 row with a non-zero universe weight, a negative universe weight, a non-finite weight, a tdw row and a
  detector-dump universe carrying `denom_nd`;
- the bank row counts of §4.2's receipt, on a toy bank;
- the truth's flux and denominator under a flux draw;
- every §9 control in both directions (it fires on a defect and is silent on a correct run);
- the null's inputs built from the remade products: each law's covariance equals its band's block;
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

**Every outcome's text is built from the clauses below, verbatim.** Only the bracketed values change. Clause T and
clause S appear in every stage-1 outcome (director's point 2, on #664).

- **Clause T (the truths):**
  > Pseudo-data were generated at two GENIE v3 tunes not used in the analysis: G18_10a_02_11b, which is only partly
  > held out of the model term's construction, since its Valencia 2p2h model belongs to the same family as the
  > GENIE + MEC shift used to build $C_{\mathrm{model}}$; and AR23_20i_00_000, which shares G18_10a_02_11b's Nieves
  > quasielastic model.
- **Clause M (the method):**
  > The pseudo-data were drawn with the statistical, flux, interaction, detector, lateral and normalization
  > uncertainties and unfolded with the nominal simulation, and $C_{\mathrm{total}}$ was rebuilt by the same procedure
  > at each tune's truth, with the lateral block carried to each truth rather than rebuilt.
- **Clause S (the scope):**
  > This tests the method with its covariance rebuilt at each of two truths. It is not a coverage rate. It does not test
  > the reported intervals, which are built at the data, and the interaction block depends on the truth at which it
  > is built ([median per-cell ratio, the nominal to the data block, 0.68; at the tunes, A_T/A_nom = …]).
  > $C_{\mathrm{resp}}$ and $C_{\mathrm{PL,5D}}$ were not drawn and were left out of the rebuilt covariance.
- **Clause P (pass, per tune):**
  > At [tune], the errors were covered ($\chi^2/\mathrm{ndf}$ = [a]; per-cell 68\,\% content [p–q]\,\%), and would
  > remain covered with $C_{\mathrm{resp}}$ and $C_{\mathrm{PL,5D}}$ added at that truth.

  "and would remain covered …" is printed in that form only if ndf(C_T) = 16 at that tune. Otherwise it reads "and
  each cell would remain covered …" (m1).
- **Clause V (leave-out-MEC, per tune, only when §5.4 reads "rests on the GENIE + MEC shift"):**
  > At [tune], coverage in cells [list] rests on the GENIE + MEC shift[, whose 2p2h family the tune shares].

  The bracketed phrase is printed for G18 only.
- **Clause F (failure, per tune):**
  > At [tune], the covariance rebuilt at its truth, without $C_{\mathrm{resp}}$ and $C_{\mathrm{PL,5D}}$, under-covered
  > in cells [list] by factors [s_c][, and jointly], [from a bias of the result / from too narrow an interval / from
  > both]; the test's false-flag rate is at most 0.05 at each tune and 0.10 over both.

  The bracketed cause is §5.1's attribution, per cell. The rate is §5.2's size.

**The outcomes:**
- **Both COVER:** T, M, P(G18), [V(G18)], P(AR23), [V(AR23)], S.
- **One covers, one under-covers:** T, M, P and [V] for the tune that covers, F for the one that under-covers, S.
- **Both under-cover:** T, M, F(G18), F(AR23), S.

**What clause F does not say.** It makes no "lower bound" statement about the reported uncertainties. The consult's
wording ("should be read as lower bounds") is not used, because an under-coverage under C_T is not shown to persist
under the procedure's full covariance at T, nor under the reported covariance (§4.3). Whether to say more is Joseph's
(decision item 5).

No covariance is inflated without Joseph.

**The plug-in,** if run, adds one clause in any case: "[and at a truth reweighted to the unfolded data, (covered /
under-covered in cells …)]".

**Stage 0 FAIL, PARTIAL without Joseph's go-ahead, INVALID, or no result:** the paper is unchanged, and the
stopped-attempt disclosure stays.

**In every outcome,** the note states:
- the resolution of §5.2, about 0.10 in content per cell and 0.08 jointly;
- the size, at most 0.05 per tune and 0.10 over both (0.15 with the plug-in);
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

**A pass under C_T** carries over to the procedure's full covariance at T (C_T + C_resp(T) + C_PL,5D(T)), not to the
reported covariance made at the data's point. An under-coverage under C_T is not shown to persist under the full
covariance at T (§4.3).

## 14. For the director

1. **#655: closed unmerged** on the director's instruction, with a pointer to this PR. Its four artifacts are carried here byte-identical (§2). The code, tests and mutation
   receipt are stage 0's. `FD-1B-MODED-DECLARATION.md` is the record of the design finding (its §3), and it lands on
   `main` with this PR.
   - I chose this over merging #655 because #655 conflicts with `main` in the generated `MANIFEST.tsv`, and carrying
     the files lands one current version once.
2. **PARTIAL at stage 0** (§2): stage 1 waits for Joseph, as the director ruled on #664.
3. **The plug-in** (§6): included, priced separately at +24 node-h of cap (73.0 for stage 1, 78.5 with stage 0). The
   code is small and touches no production file. Drop it if you prefer: the base stands alone.
4. **The plug-in's capture re-reads the real data** once, by S1's central path, and must reproduce S1's central
   product bitwise. The procedure controls of §9 also re-run four S1 data unfolds.
5. **The kept clause of `paper_body.tex:81`** about the earlier route (§12) is Joseph's to rule on if a pass lands.
6. **Binding 2** (§11) is a separate binding of code against these fixed rules. It lets stage 0 run while the code is
   written and reviewed.
