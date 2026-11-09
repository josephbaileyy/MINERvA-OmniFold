# FD-PRR DECLARATION: what moves the estimator's retained prior on the 16 cells, a one-factor-at-a-time study in simulation with IBU on the same fake data (2026-11-08, rev 2, for coverage-5b-audit; nothing runs)

**By:** the valid-region lane (session director-helper-2), at the director's request of 2026-11-08.

**Authority.**
- Joseph authorized the study on 2026-11-06 (`DECISION-20261106-joseph-plateau-next-work.md:47-48`, "What is decided"
  item 2).
- He released it on 2026-11-08 (`DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md:39-40`, item 3, #934):
  "It is declared, priced, audited and bound before it runs."
- Compute that resolves a limitation is under `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`
  item 2 (#640), as `FD-STAB-DECLARATION.md` §7 cites it. A campaign priced above half the group balance goes back to
  Joseph first. The cap here, 27.0 CPU node-h, is far below that. The director checks the current balance at binding.
- **The director's rulings on rev 1's §11 (2026-11-08)** are in §11.1. They are written into the licences.

**Status.**
- Rev 1 fixed the question, design, readings, price and licences. The director ruled on its four questions and
  asked for the code with the declaration (§11.1).
- **Rev 2 adds the code (§8), with its digests and 103 tests.** The mutation receipt follows on this PR (§8.2). It also corrects what rev 1
  got wrong or left out. Each change is listed in §13.
- Design and code are audited together by coverage-5b-audit. Nothing runs before that audit and the director's binding. Every path is relative to `docs/orchestration/` unless it
  starts with `nd-unfolding/` or `docs/analysis-note/`. Every `file:line` is at main `52334c34` unless another commit is
  named.

**MEASURES:** in simulation only, on R00–R15, at F0b's 12 graded truths, with noise-free background-inclusive pseudo-data:
- how much of each truth's departure from the prior configuration (e) leaves in its result (the retained fraction ρ,
  §4.1);
- how ρ and the noise-free bias χ² change when one factor of (e) changes at a time: iterations, classifier capacity,
  training statistics, or the observables the classifiers see;
- the same quantities for a binned D'Agostini IBU on the same pseudo-data, at K from 1 to 200.

**CITABLE FOR:**
- each level's ρ, per-cell bias, noise-free χ², p and z at each graded truth, labelled "noise-free, one MC split,
  simulation only";
- each factor's class at the two flagged truths (§5.1);
- the IBU-against-(e) classes (§5.2);
- whether each level, and IBU at K = 5, clears or does not clear the flagged truths **at these truths**, under the
  Table II rule on the noise-free analogue (§5.3);
- the composite labels of §5.4, each worded "consistent with", as defined there;
- the measured cost per level.

**NOT CITABLE FOR:**
- **a cause.** The labels say which factors move the retained prior over the tested levels. They do not establish
  why;
- **an estimator change.** No level is adopted, whatever PR-3 shows. A level that clears the flagged truths is a
  finding about the mechanism, not a new estimator. Any change to the reported procedure would need a new decision by
  Joseph and its own held-out test (§6; the director's ruling 1);
- **any held-out performance claim, or any statement that a level "would pass".** Grading at F0b's truths is
  admissible here only because nothing is selected on them (the director's ruling 2);
- **Table II or its grades.** Noise-free closures at one MC split are not F0b's pseudo-experiment means. §5.3 is an
  analogue, read relative to its own baseline;
- **coverage, an interval, or a measurement;**
- **any data quantity.** No data is read;
- **held-out truths.** F0b's truths are the simulation's own and were not held out (`FD-F0-REPORT.md`, the manuscript's
  IV G);
- **any real-data bias, or the size of the bias in the reported result;**
- **paper or note wording.** Any sentence goes through the paper lane, a PRD-referee read of the exact wording, and
  Joseph.

## 1. What the records already establish

### 1.1 What the referees ask

- **The round-4 item.** "The prior retention's mechanism. A one-factor-at-a-time simulation study (observables, W,
  iterations, capacity), or truth recovery by IBU and OmniFold on the same fake data"
  (`state/2d-closeout/stageF/methods/secondary-results/referee-methods-round4-20261106/README.md:45-46`).
- **The reads behind it,** in the same directory:
  - Sonnet JINST 1 asks for a controlled study, "in simulation with signal-only, noise-free pseudo-data". Its factors
    are the number of observables ("2, 3, 4, 5, with and without the redundant W"), the iteration count, classifier
    capacity and training statistics. It asks for "the prior retention as a function of each"
    (`sonnet-jinst-methods-r4-1.txt:47-53`).
  - Sonnet PRD 1 asks for the bias mapped "against iteration count and classifier capacity for the fake-data truths
    on the sixteen cells", and for IBU on "these same fake data cell by cell". It wants to know "whether IBU would
    pass or fail the same criteria" (`sonnet-prd-methods-r4-1.txt:75-76`).
  - Sonnet JINST 2 asks for "the effect of iteration count and classifier capacity on the flagged truths, with the
    criteria fixed in advance" (`sonnet-jinst-methods-r4-2.txt:51`).
  - Gemini PRD 2 asks whether the retention comes from stopping at five iterations, from tree capacity, or from weak
    detector constraints (`gemini-prd-methods-r4-2.txt:38`).

### 1.2 What is measured, by whom, and at what resolution

| what | measured | resolution, truths, estimator | source |
|---|---|---|---|
| the fake-data bias that is flagged | **Flagged under the reported covariance:** the GiBUU hybrid truth (p < 10⁻²⁷; cells R02, R06) and the q3 tilt (p < 10⁻⁵, by p alone). **Flagged only without C_PL,5D:** the GiBUU E_avail shape (R06) | **16 cells**, the 12 graded truths, (e), pseudo-experiment means | manuscript `…/referee-methods-round4-20261106/manuscript-methods-r4.blind.txt:1039-1050`; `state/measurement-paper/5d-community-20261024/FD-F0b-REPORT.md:123-128` |
| (e)'s noise-free bias at A7 GiBUU | RMS fractional bias 0.130 and maximum 0.365. Tree regularisation (`min_child_samples` 10⁴, 10⁵) and 2-fold cross-fitting move them by at most 0.012 | **16 cells**, noise-free closures at one MC split (pseudo seed 991000), 17 F0b truths; K = 5, 100/8 | `OUTCOME-20261105-fd-stab-none-pass.md:34-36`; `…/5d-community-20261024/FD-STAB-DECLARATION.md:105-123` |
| IBU against (e) on the same fake data | Median |residual| ratio IBU/(e) 2.98 at the NuWro closure ("IBU worse"), plus the trivial closure at Tune v1. **R2 covers only these two truths, F0b's two noise-free closures** (`readout.json` key `R2` = {`nuwro`, `tune_v1`}). There is no IBU at the GiBUU hybrid or the q3 tilt | **16 cells**, IBU noise-free against (e) with seed noise | `OUTCOME-20261106-ref-g1-r1-differ.md:31-33`; `…/fd/receipts-ref-g1/a1-read/readout.json` (sha256 `4db170d3…`); `nd-unfolding/ref_g1/config.json` `closures` |
| the IBU–(e) data difference against K | R06: −2 % at K = 2, −18 % at K = 5, −43 % at K = 20 | 16 cells, **data**, at K = 1 to 20 | `OUTCOME-20261106-ref-g1-r1-differ.md:28-29` |
| IBU against OmniFold on the same pseudo-experiments | At GiBUU and W1–W3, IBU's median residual is 0.77–1.31 × OmniFold's, all within the factor-2 band at every K ≥ 2 | **109 J cells**, development truths, K = 1 to 20 | `state/2d-closeout/stageF/methods/ibu1/REPORT.md:56-60, 129-143` |
| exact binned IBU, noise-free, against GBDT | At K = 5 the J medians agree (GiBUU 9.5 % against 8.3 %; q3 4.3 % against 5.3 %). At K = 200 GiBUU falls to 3.3 %, and after 10⁵ iterations to 0.8 %; W3 and q3 do not fall. Capacity 400/31 barely moves it. The residuals sit in functionals with binned CR widths > 10 %. The verdict: "finite-iteration regularization: consistent, and dominant at K = 5"; GBDT approximation "not supported as the main cause" | **109 J cells**, development truths, signal-only binned construction | `state/next-preparation-20261009/d-id/REPORT.md:432-452, 466, 518, 524-535` |
| GBDT iterations and capacity, noise-free | 30 iterations reduce the E_avail residual by 26 %; q3's grows with K. A larger classifier improves the reco fit, not the truth residual. Removing the missed-event regression does not help. W3's J median goes from 5.57 % at K = 5 to 6.57 % at K = 200 | J, H2, EW; development truths (D1, W1–W3, q3 stress); 100/8 and 400/31; **without background** | `docs/analysis-note/sec_5d.tex:77, 109, 137` |
| the iteration rule in the paper | k ∈ {10, 15, 20} does not improve the residual proxy on k = 5 (0.384 against 0.314). Capacity at k = 5 lowers it by 8 % (H2) and 3 % (J) | J and H2 proxy | `RECORD-20260927-s5p-stage2-exit.md:114-117` |
| the 11-04 diagnosis | **Completed:** of A7 GiBUU's squared relative-bias norm, 42.65 % lies outside the span of all the model vertices (53.87 % outside its own leave-own-vertex grade span); for q3 it is 58.74 %. **Ranked, not tested:** early stopping in weak directions; sparse support or extreme weights; classifier approximation; background subtraction. **Proposed, not run:** A-I, a matched binned-against-classifier comparison at A7 and q3; A-S, a sparsity and support tabulation | 16 cells, F0b's committed bias | `state/2d-closeout/stageF/methods/secondary-results/diagnosis-three-items-20261104/REPORT.md` §A1–A3 (`:52` onward) |
| the draft's own reading | "Two validation findings point to the unfolded result retaining part of its prior" | — | `manuscript-methods-r4.blind.txt:1272-1280` |

**What is not measured.** No record measures any of the following:
- the retained prior's dependence on iterations, capacity, training statistics or the observable set **on the 16
  reported cells, at the graded truths, under (e)'s full background-inclusive pipeline**;
- IBU at the two flagged truths on the 16 cells, or whether IBU would pass Table II's rule;
- any observable-set factor (with or without W, or fewer observables) at any resolution;
- whether the retention is support mismatch rather than slow convergence. The 11-04 scope names that as unseparated
  (`state/2d-closeout/stageF/methods/secondary-results/scope-referee-analysis-20261104/REPORT.md:437-444`), and the
  11-04 diagnosis proposes A-S for it without running it.
- **The search and its hits.** The cited records' own cross-references were followed. Every hit of the term search was
  then read by file:
  - referee reports and consult prompts;
  - the methods-draft revision ledgers (`stageF/methods/r12`–`r21`, `caveat-study`, `caveat-remeasure`);
  - the two decisions;
  - `secondary-results/CANDIDATES.md:201`;
  - the 11-04 diagnosis.
  None of them measures the dependence above.
Search: prior retention; retains part of its prior; retained prior (`git grep -n -i -E`, over docs/orchestration and docs/analysis-note) @ 52334c34

**The note's own statement of the missing study:** "Deciding the tradeoff would require sharing pseudo-data and MC
splits across a small set of iteration and capacity settings and measuring bias, variance and mean squared error for
common functionals" (`docs/analysis-note/sec_5d.tex:209`).

**So the records support a clean question.** It is not "is there a mechanism", which D-ID answered at J for binned
estimators. It is whether the J-cell picture carries to the reported cells and truths, and which of the named factors
moves the retention there.

## 2. The question

At the 16 reported cells and F0b's graded truths, with noise-free, background-inclusive pseudo-data:
1. **Which factors move (e)'s retained fraction** at the two flagged truths, the A7 GiBUU hybrid and the q3 tilt?
   Each factor is changed one at a time.
2. **Does exact binned IBU** on the same pseudo-data retain the same fraction at K = 5? Does IBU's retention fall as
   K grows to 200?
3. **Does any level clear the two flagged truths** under Table II's rule, without flagging another graded truth?

It cannot answer:
- why, beyond "consistent with" (§5.4);
- whether any level is a better estimator (§6);
- anything about data.

## 3. Design: both routes, paired on the same pseudo-data

### 3.1 The baseline B0 and the pairing

- **B0 is configuration (e)** (`registry/ESTIMATORS.tsv`, `e-R-joint-test`). That is s5e candidate R: the
  Stay-Positive refinement at 400 trees and 31 leaves, and the three OmniFold estimators at 100 trees, 8 leaves,
  5 iterations (`FD-STAB-DECLARATION.md:41-44`).
- **The pseudo-data is FD-STAB's closure construction, unchanged** (`FD-STAB-DECLARATION.md:105-123`):
  `s5p_nullexp.py --expectation --no-nuisance --mc-fraction half`:
  - every Poisson draw replaced by its mean;
  - background and refinement included;
  - one MC split per pseudo seed (`split = s5c_pseudo.split_key_for(seed)`, `nd-unfolding/s5p_nullexp.py:318`).
- **The primary split is pseudo seed 991000,** FD-STAB's, so B0 is FD-STAB's control at every truth. Control C-PAIR
  (§7) checks that bitwise.
- **Every level runs at the same seed and split as B0.** Each comparison is a paired difference at one truth and one
  split.

### 3.2 The truths

The **12 graded truths** of Table II, through FD-STAB's truth table (`FD-STAB-DECLARATION.md:112-122`):
- nominal and A7 MnvTune (the prior; closure controls);
- W1, W2, W3, q3, Stage 0c GiBUU and closure NuWro;
- A7 GENIE CV, A7 GENIE+MEC, A7 NuWro and A7 GiBUU.

The truth files are the ones F0's pins name (`fd_f0_regrade.RATIO`, `ALT`, `HYP`). They are checked, not retyped. The
six ungraded P-rows are not run.
<!-- absence-ok: a design statement about this study's own truth set -->

**Flagged truths:** A7 GiBUU and q3, the two Table II flags under the reported covariance. They carry the primary
readings. The other ten carry §5.3's "no new flag" check and are printed.

### 3.3 Route 1: the factors and levels (OFAT around B0)

| factor | levels (B0's in bold) | how | bound code? |
|---|---|---|---|
| **F1 iterations** K | 2, **5**, 10, 20, 50 | `s5p_nullexp.py --iters K` | yes, a runner flag (`s5p_nullexp.py:278`) |
| **F2 capacity** (trees, leaves) of the three OmniFold estimators | (25, 4), **(100, 8)**, (400, 31), (1000, 63) | `s5p_nullexp.py --capacity N,L` (`s5p_numerics.omnifold_capacity`, `s5p_numerics.py:91-102`). The refinement stays at 400/31 | yes, a runner flag (`s5p_nullexp.py:277`) |
| **F3 training statistics** (the unfolding MC) | **half**, quarter | `s5p_nullexp.py --mc-fraction quarter` | yes, a runner flag (`s5p_nullexp.py:275`) |
| **F4 observables the classifiers see** | **O5**: all five; **O4r**: W dropped from the step-1 (reco) classifier only; **O4**: W dropped from all three OmniFold estimators; **O3**: (p_T, p_∥, E_avail); **O2**: (p_T, p_∥) | a column mask on the classifier inputs only. The truth histogram, the extraction and the refinement keep all five, so every level reports the same 16 cells | **no:** new, a pass-through wrapper (§8) |

**Why these levels:**
- **F1** spans the iteration readings already on main: the paper's K ≤ 20, the note's 30, and D-ID's direction of
  K = 200, here 50 for the unbinned estimator's cost. IBU covers K = 200 in route 2.
- **F2:** 400/31 is the capacity probe of D-ID and the note. (1000, 63) is beyond it. (25, 4) is below.
  FD-STAB's `min_child_samples` points already measured regularisation at A7 GiBUU (§1.2), so they are not repeated.
- **F3:** a quarter is the only smaller size the bound runner offers. A larger one would need the pseudo-data source
  B, so it is not possible here.
- **F4:**
  - O4r tests the referees' reco-level degeneracy between W and (p_T, p_∥, q3) (`sonnet-jinst-methods-r4-1.txt:35-41`).
  - O4 tests W's redundancy throughout.
  - O3 and O2 complete Sonnet's "2, 3, 4, 5". The order in which observables are dropped is the one the paper builds
    up in: 2D, then E_avail, then q3 and W.
  - The column order is checked by control C-COLS, not assumed.

### 3.4 Route 2: IBU on the same pseudo-data

- **The algorithm.** REF-G1's IBU, unchanged: D'Agostini with the background as a known additive reco term (`fold`),
  through IBU-1's `unfold_ibu`, on the H2 truth grid, integrated to R00–R15 (`REF-G1-DECLARATION.md:46-54`).
- **The data.** At each graded truth, the same expectation experiment B0 unfolds. It is not rebuilt: B0's own queue
  line runs through `s5p_nullexp.main`, unchanged, under B0's namespace check, and is stopped where `build` returns,
  before the refinement and before any unfold (`prr_ibu.capture`, the pattern of FD-STAB's truth control). The
  runner's `--out` is moved to an empty scratch directory, which must still be empty afterwards.
- **The response.** It is binned from the same MC half A that (e) unfolds with, through `ibu1.Half` on those rows. So
  "the same fake data" also means the same simulation. That is the one change from REF-G1, which used the full MC.
- **K:** 1, 2, 3, 4, 5, 10, 20, 50, 200. K = 5 is primary, as in REF-G1.
- **The experiments:** the 12 graded truths at split 991000, and A7 GiBUU and the nominal truth at each floor split, for
  s_IBU (§3.5): 20 in all. Rev 1 defined s_IBU but did not list these eight.
- **R-ID (descriptive, read by nothing).** The binned Cramér–Rao width of each of the 16 cells, from the same response
  at the analysis exposure, by D-ID's definition (`d-id/REPORT.md:518`). It answers the referees' question of which
  reported cells are weakly constrained (`sonnet-jinst-methods-r4-2.txt:47-51`).
  - **The definition, pinned:** D-ID's `did.fisher` and `did.widths_from_eig`, on the response, prior and known term
    the nominal truth's `fold` unfold hands `did.ibu` (captured as it calls it). A cell's quantity is its truth count
    as IBU represents it: each H2 cell's estimate spread over its fine cells by the prior shape (`did.share_matrix`),
    summed over the fine cells the cell's S1 row covers. The width is relative to the prior's count
    (`prr_ibu.r_id`).
- **R-SUP (descriptive, read by nothing): the 11-04 diagnosis's A-S at the reported cells.**
  - **What it prints,** per cell and per graded truth: the unfolding MC half A's sum of weights, sum of squared
    weights and Kish effective count, after the truth reweight, and the largest single-event weight share.
  - **Beside each truth's per-cell |b_c| at B0:** their Spearman rank correlation with the effective count.
  - **What it can and cannot show.** It can show whether the bias concentrates where the MC is sparse. It cannot
    show support outside this MC (`diagnosis-three-items-20261104/REPORT.md`, §A2 rank 2).
  - **Cost:** about 0. It is computed in `prr_ibu` from the arrays route 2 already loads.

### 3.5 The noise floor of a paired difference: four more MC splits

- At A7 GiBUU, B0 and one level per factor (K = 20, (400, 31), quarter, O2) run at pseudo seeds **994001–994004**.
  The nominal truth also runs at each of those seeds, for the prior's integral there (§4.1).
- **s_L** is the sample SD, over the five splits, of Δρ_L = ρ_L − ρ_B0. It has 4 degrees of freedom.
- A factor's s is the s_L of its measured level, applied to all of that factor's levels and at both flagged truths.
  At q3 that is a transfer, and it is labelled as one.
- **For IBU,** s_IBU is the same SD of ρ_IBU(K = 5) − ρ_B0, from route 2 at the same five splits.
- **Why splits, not rounding jitter.** A paired difference at one split cancels most MC noise. What is left is how
  much Δρ itself varies with the split. That is the scale against which a level must differ.
- **Seeds 994001–994004.** They are not 991001–991004, because 991001 appears in two committed tests as the value the
  FD-STAB and ENS1 closure guards refuse (`nd-unfolding/tests/test_estimator_stability_probe.py:1154`,
  `nd-unfolding/tests/test_ensemble_estimator.py:547`). A test checks them against the campaigns' seed registries.
  <!-- absence-ok: scoped to the stated git grep over the named trees at the named commit -->
  Search: `git grep -n -E '(^|[^0-9.])99400[0-9]([^0-9]|$)'` over nd-unfolding and docs/orchestration gives one hit,
  inside a sha256 digest, @ 52334c34

## 4. Quantities, defined before any number is read

### 4.1 Retained fraction ρ

For truth T, level L and split s, on the 16 cells, by S1's integration rule (as `FD-STAB-DECLARATION.md` §5.1):
- **X̂_c:** the unfolded integral.
- **X_c:** the truth integral of the experiment's pseudo-data source (the product's `x_true`).
- **P_c:** the prior's integral: the nominal truth's `x_true` at the same split.
- **The relative departure** is d_c = (X_c − P_c)/P_c, and **the bias** is b_c = (X̂_c − X_c)/P_c.
- **The retained fraction** is ρ = −Σ_{c∈S} b_c d_c / Σ_{c∈S} d_c², with S the cells where |d_c| ≥ 0.01.

**What ρ means:**
- If X̂ = P, then b = −d and ρ = 1: the result is the prior.
- If X̂ = X, then ρ = 0: the departure is fully recovered.
- ρ is the least-squares coefficient of −b on d, so bias orthogonal to the departure does not enter it. That bias is
  in the χ² (§4.2) and in the per-cell b, which are printed.

**Where ρ is undefined:** if |S| < 2, ρ is "undefined" at T. Nominal and A7 MnvTune are the prior, so d ≈ 0 and ρ is
undefined by construction; they print the RMS of b.

### 4.2 Noise-free χ², p and z (the Table II analogue)

- **The bias** is F0b's: r_c = X̂_c / X_c − 1, relative, on R00–R15.
- **The matrix C_T is F0b's grade matrix for T, relative:** C_e/(f fᵀ) + Σ_{j ≠ own(T)} s_j s_jᵀ + (C_resp + C_PL,5D)/(f fᵀ).
  - It is built by F0b's own `fd_f0_regrade.leave_out`, with own(T) read from `fd_f0_regrade.TRUTHS`.
  - The inputs are committed: C_e and f from the with-C_PL,5D data product (`fd/with-cpl/data-product/fd_data_product_cpl.json`),
    S from `cmodel_5d.json`, and the block `C_resp_plus_C_PL5D` from `fd/with-cpl/block/cpl_block.npz` (`d9aa32fd…`,
    the block F0b's with-C_PL,5D re-grade added; `FD-CT-5B-ADDITION-REPORT.md:40`).
  - **f, the data's central value, enters only as the divisor that makes the matrix relative,** as in F0b. No data
    quantity is formed, and the readout passes F0b's `LeakGuard` before it is written.
  - **Control C-CT (§7)** checks that these matrices reproduce F0b's committed relative sigmas for all five matrices,
    and its noise-free `closure_nuwro` grade (χ² and every z). On the committed files they agree to 0 in σ and
    1.9 × 10⁻¹⁴ in χ² (my arithmetic, rerun by the test `test_c_ct_reproduces_f0b`).
- **The statistics,** by F0b's `grade` with its noise term zero: χ²₁₆ = rᵀ C_T⁻¹ r, p from χ²₁₆, and
  z_c = r_c / √(C_T)_cc.
- **Flagged** under Table II's rule: p < 0.01, or some |z_c| > 2 (`manuscript-methods-r4.blind.txt:1031-1033`).
- **Disclosed:**
  - there is no pseudo-data noise term, so this is the bias alone against the reported matrix;
  - B0's flagged set need not equal Table II's. It is printed beside the committed one and read by nothing.

**Rev 1 got this wrong.** It defined the bias in cross-section units against an absolute matrix. F0b grades the
relative bias against the relative matrix, and rev 2 follows the bound code.

## 5. Readings, fixed before any number is read

### 5.1 PR-1: each factor's class at each flagged truth (8 readings)

At T ∈ {A7 GiBUU, q3} and factor F with non-baseline levels L, at split 991000:
- **The bar** is δ_F = max(0.05, 9.03 s_F).
  - 9.03 is the two-sided Student-t quantile on 4 degrees of freedom at 0.01/12, Bonferroni over the 12 primary
    readings of §5.1 and §5.2 at familywise 0.01. The code uses 9.02936702750999 (`prr_read.T_Q`), and
    `test_t_quantile` recomputes it with `scipy.stats.t.ppf`.
  - The absolute floor of 0.05 keeps a tiny s from making a trivial change "real".
- **The classes:**
  - **reduces** if some L has ρ_L ≤ ρ_B0 − δ_F and none has ρ_L ≥ ρ_B0 + δ_F;
  - **increases** if the reverse;
  - **both** if each happens at some level;
  - **no effect** if every |ρ_L − ρ_B0| < δ_F;
  - **undefined** if ρ is undefined at T. That truth's χ² of §5.3 is printed instead.

### 5.2 PR-2: IBU against (e) on the same pseudo-data (4 readings)

At each flagged truth T:
- **PR-2a.** At K = 5, Δ = ρ_IBU(5) − ρ_B0 against δ_IBU = max(0.05, 9.03 s_IBU). The classes are **IBU retains
  less**, **IBU retains more** and **same**.
- **PR-2b.** IBU's retention against K: **falls** if ρ_IBU(200) ≤ ρ_IBU(5) − 0.05; **rises** if ρ_IBU(200) ≥
  ρ_IBU(5) + 0.05; otherwise **flat**.
  - IBU here is noise-free and exact given the binned response, so its only noise is the split, which PR-2b holds
    fixed. The 0.05 is the bar.
  - ρ_IBU at every K is printed.

### 5.3 PR-3: does a level clear the flagged truths at these truths? (descriptive, one reading per level)

At each level L, and for IBU at K = 5:
- **"clears at these truths"** if neither A7 GiBUU nor q3 is flagged under §4.2's rule; otherwise **"does not clear
  at these truths"**. Those are the only wordings (the director's ruling 2);
- **without new flags** if, in addition, no graded truth unflagged at B0 is flagged at L.
- A level that clears is a finding about the mechanism. It is not a new estimator, and it is not evidence that the
  level would pass a held-out test (§6).

The full 12 × levels table of χ², p and max |z| is printed.

**This reading answers Sonnet PRD's "whether IBU would pass or fail the same criteria", on the noise-free analogue
only.**

### 5.4 Composite labels, per flagged truth (descriptive; "consistent with" only)

Each label holds if its condition holds. Several can hold at once, and none excludes another:

| label | condition |
|---|---|
| **consistent with finite-iteration regularization** | PR-1 F1 = reduces **and** PR-2b = falls |
| **consistent with an information limit at these settings** | PR-1 F1 and F2 ∈ {no effect, increases} **and** PR-2b ∈ {flat, rises} |
| **consistent with an implementation-specific share** | PR-2a = IBU retains less, **or** PR-1 F2 = reduces |
| **sensitive to the observable set** | PR-1 F4 ∈ {reduces, increases, both} |
| **sensitive to training statistics** | PR-1 F3 ∈ {reduces, increases, both} |
| **unattributed** | none of the above |

R-ID and R-SUP are printed beside these labels and enter none of them.

### 5.5 Multiplicity

- **The primary readings are 12:** 8 from PR-1 and 4 from PR-2.
- **The family is bounded only in part.** δ's Student-t term bounds the familywise rate of a false class change at 0.01,
  under a Gaussian model of Δρ across splits. The absolute floor makes it smaller.
- **What that does not cover:**
  - the transfer of s from A7 GiBUU to q3;
  - the use of one level's s for a factor's other levels.

  Both are disclosed (§9).
- **PR-3 and §5.4 are descriptive** and add nothing to the family.

## 6. What the readings can and cannot change

- **No estimator change follows from any reading.** That includes a level that "clears at these truths" in §5.3. The
  director ruled so on 2026-11-08 (§11.1, ruling 1).
  - This is the FD-STAB precedent: §6's terminal branches, "No estimator change proceeds from this probe"
    (`FD-STAB-DECLARATION.md:214`), applied at NONE_PASS (`OUTCOME-20261105-fd-stab-none-pass.md:40-42`). It is also
    the 11-04 scope's e1 ("not now"; `scope-referee-analysis-20261104/REPORT.md:458`).
  - Adopting any level would need its own declaration, chosen on simulation and bound before any new data read. That
    would be Joseph's decision.
- **Unchanged:**
  - the reported result R00–R15, every covariance block, Table II, F0b's grades and REF-G1's readings;
  - the paper and the note.
- **Where the results go.** The outcome goes to the director, and from there to Joseph and methods round 5
  (`DECISION-20261108-…:41-42`, item 4). No wording is drafted here.

## 7. Controls (each gates the readings; any failure is a STOP reported to the director)

| control | check | where |
|---|---|---|
| **C-PINS** | every bound module equals its digest before the runner is imported: the 15 in `prr_probe.CODE_PINS` (the runner `s5p_nullexp.py` and every module it imports, the unfold and loop, the truths, FD-STAB's truth plumbing, and the refinement driver `2d-unfolding/unfold_2d_omnifold_unbinned.py`, which `s5n_pseudo` loads at call time), and REF-G1's and IBU-1's five in `prr_ibu.CODE_PINS`. Each product's recorded code digests must be these. Each staged input equals its pin (§10.4). Each product's runner digest, and its hypothesis and alternative digests by FD-STAB's `expected_pin`, are checked by the reader. The reader's committed inputs are in `prr_read.INPUT_PINS` | `prr_probe.check_pins`, `stage`; `prr_read.meta_problems`, `check_inputs` |
| **C-PAIR** | B0's unfolded array at split 991000 equals FD-STAB's control closure **bitwise** at nominal and at A7 GiBUU, read from their staged copies, each carrying its pin (`3753f414…`, `b4d2ba5c…`; `fd/receipts-stab-a1r/{dry,full}/SHA256SUMS`). Both B0 tasks are in the dry run, so the pairing is checked before any full job. A mismatch stops the study. Same thread layout as FD-STAB, 8 lanes × 32 threads. FD-STAB's production modules are unchanged between its pin `cc54d86f` and `52334c34` (`git diff --stat cc54d86f 52334c34` on all 15 is empty) | `prr_probe.pair`, at the end of `prr_dry` |
| **C-MASK** | the five-column mask (level O5, at nominal, in the dry run) equals B0 bitwise, dtype included | `prr_probe.pair`; recomputed by `prr_read.c_mask` |
| **C-COLS** | the input's axis names are (p_T, p_∥, E_avail, q3, W) in that order (`pvl_lib.npz_axes`), and its edges are the pv-ladder's 5D fine grid (`pvl_lib.check_edges`). Read from the input file at every task, before any mask is applied, and recorded in the product | `prr_probe.check_columns`; `prr_read` |
| **C-IBU** | (a) the route-2 adapter, given REF-G1's NuWro closure experiment, reproduces REF-G1's committed `R2.nuwro.median_abs_residual_ibu` (0.03322119601639817) to 10⁻¹² relative; (b) route 2's truth on R00–R15 equals (e)'s B0 truth at every one of its 20 experiments to 10⁻¹² relative | `prr_ibu.c_ibu`; `prr_read.route2` |
| **C-CT** | the rebuilt grade matrices reproduce F0b's committed relative sigmas and its noise-free `closure_nuwro` grade (§4.2) | `prr_read.grade_matrices` |
| **C-SPLIT** | at each seed, every product's split key is `s5c_pseudo.split_key_for(seed)` | `prr_read.products` |
| **C-CAP** | every product records its level's declared and recorded `iters`, `capacity` and `mc_fraction`, and they are equal. A masked level records exactly one loop call through its mask, with its columns; an unmasked level records none | `prr_probe.install`; `prr_read.meta_problems` |
| **C-FIN** | every X̂, X, P and IBU estimate is finite, every truth integral positive, and every C_T positive definite | `prr_read` |

## 8. Code

### 8.1 The files

All under `nd-unfolding/prior_retention/`. **No production module is edited.** The runner is `s5p_nullexp.py`,
unchanged. Each wrapper rebinds a name for one invocation and restores it on exit, as FD-STAB's does.

| file | role |
|---|---|
| `prr_probe.py` | the level table (14 levels, with O5 for C-MASK); the truths, read from FD-STAB's `CLOSURES`; the task list, jobs and queues; the namespace check on the runner's own parse; the F4 column mask around `omnifold_nn_core.omnifold_loop`; C-PINS and C-COLS; the gate and its packing price; `stage` and `verify-stage` (§10.4); `pair` (C-PAIR, C-MASK); `limit` (each job's `--time` as Slurm reads it) |
| `prr_ibu.py` | route 2: the capture, REF-G1's `unfold_experiment` on `ibu1.half_from_experiment` (half A), R-ID, R-SUP and C-IBU, under REF-G1's O_NOATIME read guard |
| `prr_read.py` | completeness; the controls; §4's quantities; §5's readings; F0b's `LeakGuard` on the readout |
| `sbatch_prr.sh` | the five jobs. It refuses unless the deploy is the pin, the job is named `prr_<mode>` and Slurm's TimeLimit is at most the declared limit. It writes a DONE only for a complete, clean run, as `sbatch_fd_stab.sh` does |
| `test_prr.py` | 103 tests (§8.2) |
| `prr_mutation.py` | 62 planted defects, each to be killed by a named test, run in a mirrored tree (§8.2) |

**Digests** (sha256 of the files at this revision's commit; the binding pins them):

| file | sha256 |
|---|---|
| `prr_probe.py` | `f87ee90c58d2b8904fe881931edc61966a6adda8be7eb503da6644797a3d1232` |
| `prr_ibu.py` | `17acad82bad7c43f45c423e41039eb81381f5acab15ecdf983ad0d023848d046` |
| `prr_read.py` | `f35bc3282b50215dd583b76b0d6a747f90185e4b96b6e3f5b693d42c01166372` |
| `sbatch_prr.sh` | `323f491afa2038a55bfb791be0d7abf81a6cda7e27a7f5124ea8cacb75efda66` |
| `test_prr.py` | `33bfdf099077dbc420c7db67ff517efc1fd798f9d2ab41fd285752e91a7b2caf` |
| `prr_mutation.py` | `28f3f9e5edf1e63c65ba5db9f2050c9159a89372bf27fe7e1558cc9ffb682b86` |

Both test logs record the same six (`fd/receipts-prr/rev2/tests-serial.txt`, `tests-jobscript.txt`).

### 8.2 Tests and the mutation receipt

- **Where the receipts were made.** Every receipt is made in a clean clone at the code commit, the commit that
  carries the six files above. The receipt README names that commit. The next commit adds only the receipt files.
  - Each run is one serial process, under `nice -n 19`, with every BLAS and OpenMP thread cap at 1.
  - Each log's header carries the six files' digests and the clone's HEAD.
- **The suite has 103 tests.**
  - Every class but `JobScript`: `fd/receipts-prr/rev2/tests-serial.txt`.
  - The `JobScript` class alone, afterwards: `tests-jobscript.txt`. That class runs `sbatch_prr.sh`, which starts
    8 gate processes at once by design, so the director held it while the shared machine was loaded. The split is by
    the test loader's selection.
- The tests run without LightGBM, ROOT or the cluster:
  - the estimators are deterministic stand-ins;
  - the inputs are synthetic rows on the real 5D fine grid, FD-STAB's test helpers;
  - REF-G1's own `Lib`, `worlds` and `unfold_experiment` run on them, with the real H2 cells and S1 rows.
- **They include:**
  - every queue line through the real runner's parser, all 181;
  - the job script, run on a stand-in deploy with the real gate;
  - C-CT on the committed files;
  - the readings end to end on a planted run.
- **Mutation, `python3 -B nd-unfolding/prior_retention/prr_mutation.py`:** 62 mutants. Each must be killed by its
  named test, and the unmutated suite must pass with 103 tests in the mirrored tree (`mutation.txt`).
- **The first serial mutation run failed: 59 of 62 killed** (`mutation-run1-fail.txt`, at the earlier test file).
  - Three tests did not isolate their check, and a neighbouring check masked each mutant:
    - C-COLS's order check, behind the edges check;
    - C-MASK's dtype check, behind a value change;
    - the job script's rc record, behind the end count.
  - Three assertions were added to `test_prr.py`, and no checked code changed.
  - The receipts here are the rerun at the commit with those assertions.
- **The receipts** are in `fd/receipts-prr/rev2/`, with a README naming the commit they were made at.
- **Not testable here:** LightGBM, the real inputs, `squeue` and O_NOATIME (macOS has none, so the tests read with a
  zero flag). The dry run is the first run with each.

## 9. Disclosures and limits

- **Not blind to the J-cell picture.** The design was fixed after the lane had read every row of §1.2: Table II,
  FD-STAB's A7 GiBUU RMS, D-ID, IBU-1, REF-G1 and the note's traces. The 16-cell per-cell biases at the new levels
  have not been seen. No data enters, so the data's blindness is not at issue.
- **The truths are not held out** (§3.2). Nothing is selected on them (§6).
- **Background-inclusive, not signal-only.**
  - Sonnet asked for signal-only pseudo-data. This study keeps (e)'s background and refinement, because that is the
    pipeline Table II grades.
  - At J, D-ID found signal-only close to the noise-free trace: GiBUU 9.2 % against 9.5 % (`d-id/REPORT.md:461-464`).
  - A signal-only level would need a new construction. It is left out.
- **One unfolding MC size up and none larger.** F3 can only shrink the MC (§3.3).
- **s is measured at A7 GiBUU and transferred to q3,** with 4 degrees of freedom (§3.5, §5.5).
- **Support mismatch is not separated.** The 11-04 consult's limit, the truth's mass where Tune v1 has almost none,
  stays open (`scope-referee-analysis-20261104/REPORT.md:443-444`).
- **No variance or MSE per level.** The note's tradeoff question (`sec_5d.tex:209`) also asks for variance. That would
  need noisy ensembles per level, about 20× this price. It is out of scope.
- **The cost per K and per capacity is unmeasured,** so the dry run measures it before any full job (§10).
  <!-- absence-ok: describes this declaration's own pricing assumption, measured by its own dry run -->
- **The staged bank directory holds only `cv.npz`.** Under `--no-nuisance` the runner reads nothing else from the bank:
  it globs the bank's universe files to list bands and flux universes, and draws none. So each product's meta records
  `model_bands` as empty, where FD-STAB's lists the bank's bands. The unfolded arrays do not depend on it, and C-PAIR
  checks that bitwise. The detector directory is never read under `--no-nuisance`.

## 10. Price, caps and job names

### 10.1 The unit cost and the assumptions

- **Measured:** 0.022828 CPU node-h per (e) unfold at 8 lanes per node (S1 P1, 2.00889 node-h for 88 universes;
  `FD-1B-STAGED-DECLARATION.md:528-530`), which is 657 s of one lane.
- **Conservative unit:** 1,062 s, which is 1.25 × the I2 maximum of 849.6 s (`:528`, `:532`), or 0.036875 node-h.
- **FD-STAB's closures** of this exact construction took 428–907 s per lane at B0 (median 537 s;
  `fd/receipts-stab-a1r/full/records/stab_control_closure_*.{start,end}`; my arithmetic). ENS1 cites 466 s per control
  closure unfold from FD-STAB's gate projection (`fd/rounding-stability-20261106/ensemble/ENS1-DECLARATION.md:284-285`). Its full job, 280 unfolds, charged 16,447 s
  on one node (`fd/receipts-stab-a1r/full/sacct-60837713.txt`).
- **The multipliers are assumptions, all measured by the dry run:**
  - cost ∝ K, with K = 2 at 0.4. This is an upper bound if part of the cost is fixed per unfold;
  - capacity (25, 4) 0.5×, (400, 31) 4×, (1000, 63) 15×. The s5p stage-2 forecast implies about 3.4× for 400/31:
    190.8 node-h at k = 5 against 222.6 at k = 20 for the same work (`RECORD-20260927-s5p-stage2-exit.md:111-113`;
    the ratio and the linearity are my arithmetic);
  - quarter 1×, and the F4 levels 1×. Neither should cost more than B0.

### 10.2 The units of work

u = one B0 unfold.

| block | unfolds | units |
|---|---:|---:|
| B0, 12 truths | 12 | 12.0 |
| F1: K = 2, 10, 20, 50 × 12 | 48 | 196.8 |
| F2: three capacities × 12 | 36 | 234.0 |
| F3: quarter × 12 | 12 | 12.0 |
| F4: four masks × 12 | 48 | 48.0 |
| C-MASK: O5 at nominal | 1 | 1.0 |
| floor: 4 splits × (nominal + A7 GiBUU at B0, K = 20, (400, 31), quarter, O2) | 24 | 48.0 |
| **total, (e)** | **181** | **551.8** |
| route 2: IBU at 20 experiments × 9 K, plus R-ID, R-SUP and C-IBU | — | priced apart: 0.25 node-h. REF-G1's whole run was 0.225 (`OUTCOME-20261106-ref-g1-r1-differ.md:55`) |

- **Expected:** 551.8 × 0.022828 = **12.60** node-h, plus 0.25 for IBU: **about 12.9 CPU node-h**.
- **At the conservative unit:** 551.8 × 0.036875 = 20.35, plus 0.5.
- `prr_probe.all_tasks` is the list, and the tests check its count (181) and its units (551.8).

### 10.3 Jobs, `--time` and the cap

Every job runs on one node with 8 lanes, CPU only, QOS regular, `--exclusive --no-requeue`. Every job is under 12 h.
Nothing is written to CFS. The charge is taken from `sacct`.

| job name | contents | tasks | units | packed lane wall at 1,062 s | `--time` | node-h at most |
|---|---|---:|---:|---|---|---:|
| `prr_dry` | one nominal task per level (13), O5 at nominal (C-MASK), B0 at A7 GiBUU (C-PAIR); then C-PAIR and C-MASK | 15 | 43.9 | 4.43 h (the (1000, 63) task) | 5:15:00 | 5.25 |
| `prr_iter` | the rest of F1 | 44 | 180.4 | 6.73 h | 7:30:00 | 7.50 |
| `prr_cap` | the rest of F2, except (1000, 63) at the last four truths | 29 | 154.5 | 5.75 h | 6:30:00 | 6.50 |
| `prr_misc` | the rest of B0, F3 and F4, (1000, 63) at A7 GENIE CV, GENIE+MEC, NuWro and GiBUU, and the floor splits | 93 | 173.0 | 6.49 h | 7:15:00 | 7.25 |
| `prr_ibu` | route 2, R-ID, R-SUP and C-IBU | — | — | — | 0:30:00 | 0.50 |
| **total** | | **181** | **551.8** | | | **27.00** |

**Cap: 27.0 CPU node-h, the sum of the five limits.**
- Each full job's limit is its queue's packed lane wall at the conservative unit, over 0.9, rounded up to a quarter
  hour. The queue is fed longest first to the lane that frees first, as `xargs -P 8` does (`prr_probe.price`).
- The dry job adds 0.25 h for its staging, verify and pair steps, which the gate does not project.
- At the expected unit the packed walls are 2.7, 4.2, 3.6 and 4.0 h.
- A test fails if any limit is below what `price` requires, or if the limits do not sum to the cap.

**The packing arithmetic** (`prr_probe.price` and `pack`; u = 1,062 s of one lane):

| job | its tasks, by units | the 8 lane totals, u | the longest lane | its wall | wall / 0.9 | `--time` |
|---|---|---|---|---|---|---|
| `prr_dry` | 15 × 1, 10 × 1, 4 × 2, 2 × 1, 1 × 8, 0.5 × 1, 0.4 × 1 | 15.0, 10.0, 4.0, 4.0, 3.0, 3.0, 2.5, 2.4 | 15 | 15 u = 4.425 h | 4.917 h, + 0.25 = 5.167 h | 5.25 h |
| `prr_iter` | 10 × 11, 4 × 11, 2 × 11, 0.4 × 11 | 22.8 × 3, 22.4 × 5 | 10 + 10 + 2 + 0.4 + 0.4 | 22.8 u = 6.726 h | 7.473 h | 7.5 h |
| `prr_cap` | 15 × 7, 4 × 11, 0.5 × 11 | 19.5 × 5, 19.0 × 3 | 15 + 4 + 0.5 | 19.5 u = 5.753 h | 6.392 h | 6.5 h |
| `prr_misc` | 15 × 4, 4 × 8, 1 × 81 | 22.0 × 5, 21.0 × 3 | 15 + 7 × 1 | 22.0 u = 6.490 h | 7.211 h | 7.25 h |

- **Unsplit, for comparison:** with all 11 (1000, 63) tasks in `prr_cap`, three lanes carry two of them, 30 u or more.
  That is 8.85 h, so the job would need 10.0 h, and `prr_misc` 5.0 h, for a sum of 28.25 with the dry job and route 2.
- **The queue order** is longest first, ties broken by task id, and each task goes to the lane that frees first. The
  lane totals above are that order's, not an optimum's.

**Rev 1's limits were wrong.** It priced each job's lane wall as its units over 8 lanes, as if perfectly packed. Whole
tasks do not pack that way:
- 11 tasks of (1000, 63) at 15 u each put two on three lanes of `prr_cap`. That job needs 10.0 h, not rev 1's 9.0.
- Moving four of them to `prr_misc` gives the smallest total of the splits I tried that keep each factor's other
  levels together: 27.0, against 28.25 unsplit.
- So the cap rises from rev 1's 26.5 to 27.0. That touches the director's ruling 4 (§11.2).

**It binds three ways:**
1. **Slurm.** On one node a job cannot charge more than its `--time`, so the five `--time` limits sum to the cap.
   - The job script refuses unless its Slurm TimeLimit is at most the declared limit (`prr_probe.py limit <mode>`,
     printed as H:MM:SS).
   - It also refuses unless its job name is `prr_<mode>`.
2. **The gate.** Every task starts only through `prr_probe.py gate`.
   - It projects the job's whole queue, tail included, packed onto 8 lanes.
   - If the projection exceeds 0.9 × the job's `--time`, nothing further starts. The study comes back to the director
     with the measured rates, to be repriced.
   - In the dry job, a level not yet measured is priced at 657 s × its assumed units.
   - A full job starts only after `prr_dry` has completed: its DONE, every one of its tasks ended, and C-PAIR and
     C-MASK passed. A full job's gate refuses any level without a dry-run rate, so nothing starts on an assumed rate.
3. **No raise.** A full job's `--time` can be lowered from the dry run's measurements, never raised without an
   addendum the director binds.

**After a stop:**
- there is no resume without an addendum the director binds. The script refuses if the job's log exists;
- the products already made are kept and pinned;
- nothing is read until every job has completed. An incomplete study is reported as INCOMPLETE.

**Job-name family: `prr_`** (`prr_dry`, `prr_iter`, `prr_cap`, `prr_misc`, `prr_ibu`).
- No committed file uses it.
  <!-- absence-ok: scoped to the stated git grep over the whole tree at the named commit -->
  Search: `git grep -n -i -E '(^|[^A-Za-z0-9])prr_'` over the tree at `52334c34` gives one hit, a binary PDF.
- The director tells every fenced lane before any go (the job-family rule). The director has noted it (§11.1).

**Order of the jobs:** `prr_dry` first. Then `prr_iter`, `prr_cap`, `prr_misc` and `prr_ibu`, in any order, each
after the dry run's DONE.

**Who runs it.** A cluster lane the director assigns at binding submits the jobs, watches them and charges them from
`sacct`. This lane writes the code and does not connect.

### 10.4 Inputs, the shared reads and the connect design

**Every file outside the deploy that the jobs read is staged once,** by `prr_dry`, before its queue starts
(`prr_probe.py stage`, from `prr_probe.SOURCES`):

| role | source | pin | where the pin comes from |
|---|---|---|---|
| `of_inputs_5d` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz` | `07fccc1a…` | `s1_assemble.INPUT_NPZ_SHA256`; REF-G1's preconditions listing |
| `bkg_dump` | `/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz` | `2addac8f…` | `s1_assemble.BKG_SHA256`; the listing |
| `bank_cv` | `…/nd-unfolding/bank_sweep_5d_bkgaware/cv.npz` | `072643e1…` | `s1/PRESERVE-INVENTORY.sha256`; the listing |
| `closure_ratio_nuwro` | `/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/nuwro.json` | `38e47eb6…` | `fd_f0_regrade.RATIO["closure_nuwro"]` |
| `fd_stab_control_nominal`, `fd_stab_control_A7_gibuu` | FD-STAB's control closures under `/pscratch/sd/j/josephrb/fd-stab-a1r-20261104/runs/control/closure/` | `3753f414…`, `b4d2ba5c…` | `fd/receipts-stab-a1r/{dry,full}/SHA256SUMS` |

The listing is `fd/receipts-ref-g1/preconditions/listing.json`.

**How each file is staged:**
- It is copied once through O_NOATIME, by REF-G1's `copy_noatime`, into `<OUT>/stage/`. The digest is taken in the
  same pass, and the copy is refused unless that digest is the pin.
- **Its own stat is recorded before and after the copy:** size, mtime, atime and inode. The copy is refused if any of
  them moved.
- **Only per-file stat records are used.** No directory's atime is read or compared: ENS1's stat listing of the bank
  directory moved that directory's atime on 2026-11-08 (#940), and the director ruled it out as a control.
- **No absolute atime is expected.** The before-stat is whatever the file shows at staging. ENS1 stage 1's bound
  plain reads left `of_inputs_5d.npz` and `bkg_dump.npz` at 15:42:54Z, and ENS1 stage 2 will move them again. The
  check is only that this study's own copy moved nothing.

**After staging:**
- Every task reads only the staged copies. The queues point the runner's `--npz`, `--bkg`, `--bank` and the closure
  ratio at them (`prr_probe.py tasks --stage-dir`).
- Each later job re-verifies every copy's digest before its queue starts (`verify-stage`).
- Route 2 reads under REF-G1's read guard, which refuses a plain read of anything under `/pscratch` or `/global/cfs`
  outside the repository, the stage and its own output.
- **So after the dry run's one copy, no job of this study touches a shared file.**

**Sharing with ENS1** (the director's ruling of 2026-11-08):
- **ENS1's stage 2 has ended and its post-run is done before `prr_dry` is submitted.** ENS1's jobs read
  `of_inputs_5d.npz` and `bkg_dump.npz` in place with plain reads, so "runs first" is not enough.
- The two lanes' connects never copy at the same time.
- Both use noatime copies.
- **Enforced in part by the job script.** `prr_dry` refuses before staging if any `ens1_*` job is queued or running
  (`squeue -u <user> -o '%j|%T'`). It also refuses if `squeue` cannot answer.
- **The rest is the cluster lane's to confirm** before `prr_dry` is submitted: that ENS1's post-run is done, and that
  no ENS1 connect is copying. A queue check cannot see either.

**The rest:**
- The deploy is a clean clone at the bound commit on pscratch. Its committed truth files are read from it.
- As FD-STAB did, a DTN pins check precedes the dry run (`FD-STAB-DECLARATION.md:349-351`). Staging then re-checks
  every pin, so a missing or changed input stops the study before any unfold.

## 11. Rulings

### 11.1 The director's rulings on rev 1 (2026-11-08)

1. **FD-STAB §6's terminal rule applies.**
   - No level is adopted, whatever PR-3 shows.
   - A level that clears the flagged truths is a finding about the mechanism, not a new estimator.
   - Any change to the reported procedure would need a new decision by Joseph and its own held-out test.
   - Written into the licences and §6.
2. **Grading at F0b's truths is admissible, because nothing is selected.**
   - FD-STAB §3.1's contamination rule bars selection on those truths, not description.
   - NOT CITABLE FOR now includes any held-out performance claim and any statement that a level "would pass".
   - PR-3 is worded "clears / does not clear at these truths" (§5.3; `prr_read.LABELS`).
3. **Write the code now.** Rev 2 comes with the digests, the tests and a mutation receipt, and design and code are
   audited together.
4. **26.5 node-h was within the 11-01 authority.**
   - All the new caps together come to about 180 node-h, far below half the balance.
   - The balance is re-read at the first connect.
- **Overlap with ENS1:** ENS1 stage 2 first, connects never copying at the same time, noatime copies for both, per-file
  stat records only (§10.4).

### 11.2 For the director: what rev 2 changes that touches a ruling

1. **The cap, 26.5 → 27.0 node-h** (§10.3). Rev 1's limits assumed perfect packing; with whole tasks on 8 lanes,
   `prr_cap` needed 10.0 h. The repacked limits sum to 27.0, and the expected cost is unchanged at about 12.9.

Everything else in §13 is the lane's to choose under the brief: the R-ID definition, the IBU floor experiments, the
extra dry-run tasks, F0b's relative grade convention and the staged inputs.

## 12. Not changed

- **Unchanged:**
  - the reported result R00–R15 and every covariance block;
  - every fake-data readout, Table II and REF-G1;
  - the paper and the note.
- **No production or bound file is edited.** The new code is under `nd-unfolding/prior_retention/` only.
- **Nothing is run, submitted, deposited or tagged.**
<!-- absence-ok: a statement about this declaration's own status -->

## 13. What rev 2 changes from rev 1

| § | change | why |
|---|---|---|
| licences, §5.3, §6 | the director's rulings 1 and 2: no adoption whatever PR-3 shows; NOT CITABLE FOR held-out claims and "would pass"; PR-3 worded "clears / does not clear at these truths" | §11.1 |
| §4.2 | the χ² grades F0b's relative bias X̂/X − 1 against F0b's relative grade matrix, built by `fd_f0_regrade.leave_out` from committed files, with control C-CT. Rev 1 wrote an absolute bias against an absolute matrix | rev 1 did not follow the bound code's convention |
| §3.4, §3.5 | route 2 also runs A7 GiBUU and the nominal truth at the four floor splits (20 experiments), which s_IBU needs | rev 1 defined s_IBU without listing them |
| §3.4 | the capture: B0's own queue line, stopped where `build` returns, with `--out` moved to scratch | the runner makes its output directory before building; found by a test |
| §3.4 | R-ID's definition pinned | rev 1 deferred it to rev 2 |
| §7 | C-CT added; C-IBU (b), route 2's truths against (e)'s; each control names its code | — |
| §10.2, §10.3 | O5 at nominal added (C-MASK; rev 1 used it without counting it), and B0 at A7 GiBUU moved into the dry run so C-PAIR is complete before any full job: 181 tasks, 551.8 u. Limits repacked: 5.25, 7.5, 6.5, 7.25, 0.5; cap 27.0 | rev 1's limits assumed perfect packing (§10.3) |
| §10.3 | the job script checks its job name and Slurm TimeLimit | a `--time` in the wrong format would otherwise pass unseen |
| §10.4 | every shared read staged once through O_NOATIME with per-file stat records; no directory atime and no absolute atime used | the director's sharing ruling and note of 2026-11-08 |
| §10.4, `sbatch_prr.sh` | ENS1's stage 2 ended and post-run done before `prr_dry`; the dry job refuses while any `ens1_*` job is queued or running, or if `squeue` fails (with its test and two mutants) | coverage-5b-audit's low on dd33c678, at the director's direction |
| §8 | the code, its digests, 103 tests and the mutation receipt | ruling 3 |

