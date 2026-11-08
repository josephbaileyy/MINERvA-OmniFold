# FD-PRR DECLARATION: what moves the estimator's retained prior on the 16 cells, a one-factor-at-a-time study in simulation with IBU on the same fake data (2026-11-08, rev 1, for the director; nothing runs)

**By:** the valid-region lane (session director-helper-2), at the director's request of 2026-11-08.

**Authority.**
- Joseph authorized the study on 2026-11-06 (`DECISION-20261106-joseph-plateau-next-work.md:47-48`, "What is decided"
  item 2).
- He released it on 2026-11-08 (`DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md:39-40`, item 3, #934):
  "It is declared, priced, audited and bound before it runs."
- Compute that resolves a limitation is under `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`
  item 2 (#640), as `FD-STAB-DECLARATION.md` §7 cites it. A campaign priced above half the group balance goes back to
  Joseph first. The cap here, 25.0 CPU node-h, is far below that. The director checks the current balance at binding.

**Status.**
- Rev 1 fixes the question, design, readings, price and licences.
- **The code in §8 is not written yet.** Rev 2 will pin its digests and its test and mutation counts, before
  coverage-5b-audit's audit. The director rules on the order in §11.
- Nothing runs before the audit and the director's binding. Every path is relative to `docs/orchestration/` unless it
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
- the IBU-against-(e) classes (§5.2), and whether each level clears the flagged truths under the Table II rule (§5.3);
- the composite labels of §5.4, each worded "consistent with", as defined there;
- the measured cost per level.

**NOT CITABLE FOR:**
- **a cause.** The labels say which factors move the retained prior over the tested levels. They do not establish
  why;
- **an estimator change.** No level is adopted, whatever it shows (§6);
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
- **The data.** At each graded truth, the same expectation experiment B0 unfolds, built by `s5p_nullexp`'s own `build`
  at the same split.
- **The response.** It is binned from the same MC half A that (e) unfolds with, through `ibu1.Half` on those rows. So
  "the same fake data" also means the same simulation. That is the one change from REF-G1, which used the full MC.
- **K:** 1, 2, 3, 4, 5, 10, 20, 50, 200. K = 5 is primary, as in REF-G1.
- **R-ID (descriptive, read by nothing).** The binned Cramér–Rao width of each of the 16 cells, from the same response
  at the analysis exposure, by D-ID's definition (`d-id/REPORT.md:518`). It answers the referees' question of which
  reported cells are weakly constrained (`sonnet-jinst-methods-r4-2.txt:47-51`). Rev 2 pins the definition's code.
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
- **For IBU,** s_IBU is the same SD of ρ_IBU(K = 5) − ρ_B0.
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

- **The bias** is b_abs,c = X̂_c − X_c, in cross-section units.
- **The matrix C_T is Table II's matrix for T:** the reported covariance C_total + C_resp + C_PL,5D, without T's own
  vertex for the vertex-family truths. It is built by the bound code that made the with-C_PL,5D grades (`FD-CT-5B-ADDITION`'s
  re-grade, whose products are in `fd/with-cpl/`;
  `FD-CT-5B-ADDITION-REPORT.md:40`). Rev 2 names the function and pins it.
- **The statistics:** χ²₁₆ = b_absᵀ C_T⁻¹ b_abs, p from χ²₁₆, and z_c = b_abs,c / √(C_T)_cc.
- **Flagged** under Table II's rule: p < 0.01, or some |z_c| > 2 (`manuscript-methods-r4.blind.txt:1031-1033`).
- **Disclosed:**
  - there is no pseudo-data noise term, so this is the bias alone against the reported matrix;
  - B0's flagged set need not equal Table II's. It is printed beside Table II's and read by nothing.

## 5. Readings, fixed before any number is read

### 5.1 PR-1: each factor's class at each flagged truth (8 readings)

At T ∈ {A7 GiBUU, q3} and factor F with non-baseline levels L, at split 991000:
- **The bar** is δ_F = max(0.05, 9.03 s_F).
  - 9.03 is the two-sided Student-t quantile on 4 degrees of freedom at 0.01/12, Bonferroni over the 12 primary
    readings of §5.1 and §5.2 at familywise 0.01. The arithmetic is mine; rev 2 recomputes it in a test.
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

### 5.3 PR-3: does a level clear the flagged truths? (descriptive, one reading per level)

At each level L, and for IBU at K = 5:
- **clears** if neither A7 GiBUU nor q3 is flagged under §4.2's rule;
- **without new flags** if, in addition, no graded truth unflagged at B0 is flagged at L.

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

- **No estimator change follows from any reading.** That includes a level that "clears" in §5.3.
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

| control | check |
|---|---|
| **C-PINS** | every imported bound module and every input equals its binding's digest at run time: `s5p_nullexp.py`, `s5p_numerics.py`, `estimator_stability_probe.py` (truth plumbing only), `ref_g1.py`, `ibu1.py`, `s1_assemble.py`, the truth files, and the C_T inputs |
| **C-PAIR** | B0's unfolded array at split 991000 equals FD-STAB's control closure **bitwise** at nominal and at A7 GiBUU. The FD-STAB products are read with O_NOATIME; the thread layout is the same, 8 lanes × 32 threads. A mismatch stops the study: the pairing with the bound pipeline has failed. RS1 met the same kind of check on FD-STAB's control stability products, 21 of 21 bitwise (`OUTCOME-20261108-rs1-rounding-mechanism.md`, G1) |
| **C-MASK** | the F4 wrapper with all five columns is a bitwise pass-through of B0 (at nominal, in the dry run) |
| **C-COLS** | the classifier columns' order is (p_T, p_∥, E_avail, q3, W), read from the experiment's own edges and keys, before any mask is applied |
| **C-IBU** | the route-2 adapter, given REF-G1's NuWro closure experiment, reproduces REF-G1's committed `R2.nuwro.median_abs_residual_ibu` to 10⁻¹² relative |
| **C-SPLIT** | every level's split key equals B0's at the same seed and truth |
| **C-CAP** | every product records `capacity`, `iters` and `mc_fraction`, and each equals its level's declared value |
| **C-FIN** | every X̂, X, P and C_T is finite, and C_T is positive definite |

## 8. Code (to be written; rev 2 pins it)

| file | role |
|---|---|
| `nd-unfolding/prior_retention/prr_probe.py` | the level table; the F4 column mask (a pass-through around `omnifold_nn_core.omnifold_loop` for one invocation, slicing the classifier inputs only); the task queue; the budget gate, ported from `estimator_stability_probe.project` and `gate` with its tests. **No production module is edited**; the runner is `s5p_nullexp.py`, unchanged |
| `nd-unfolding/prior_retention/prr_ibu.py` | route 2: `s5p_nullexp`'s `build` at expectation, then REF-G1's `unfold_experiment` on `ibu1.Half` of MC half A; R-ID; R-SUP |
| `nd-unfolding/prior_retention/sbatch_prr.sh` | the jobs of §10, on 8 lanes, every task through the gate; a DONE receipt only for a complete, clean run, as `sbatch_fd_stab.sh` |
| `nd-unfolding/prior_retention/prr_read.py` | §4–§5: completeness, controls, quantities, readings |
| `nd-unfolding/prior_retention/test_prr.py`, `prr_mutation.py` | every reading tested in the direction it acts and the other, the gate, the refusals; planted defects, each killed by a named test |

**Not testable locally:** LightGBM and the real inputs are absent here, so the tests use stand-in estimators on a
synthetic grid, as FD-STAB's do. The dry run is the first run with LightGBM.

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
| floor: 4 splits × (nominal + A7 GiBUU at B0, K = 20, (400, 31), quarter, O2) | 24 | 48.0 |
| **total, (e)** | **180** | **550.8** |
| route 2: IBU at 12 truths × 9 K, plus R-ID, plus C-IBU | — | priced apart: 0.25 node-h. REF-G1's whole run was 0.225 (`OUTCOME-20261106-ref-g1-r1-differ.md:55`) |

- **Expected:** 550.8 × 0.022828 = **12.57** node-h, plus 0.25 for IBU: **about 12.8 CPU node-h**.
- **At the conservative unit:** 550.8 × 0.036875 = 20.31, plus 0.5.

### 10.3 Jobs, `--time` and the cap

Every job runs on one node with 8 lanes, CPU only, QOS regular, `--exclusive --no-requeue`. Every job is under 12 h.
Nothing is written to CFS. The charge is taken from `sacct`.

| job name | contents | units | lane wall at 1,062 s | `--time` | node-h at most |
|---|---|---:|---|---|---:|
| `prr_dry` | one nominal task per level type (13), split 991000; C-PAIR, C-MASK, C-COLS, C-CAP | 41.9 | the longest, (1000, 63), 4.4 h | 4:45:00 | 4.75 |
| `prr_iter` | the rest of F1 | 180.4 | 6.65 h | 7:00:00 | 7.00 |
| `prr_cap` | the rest of F2 | 214.5 | 7.9 h | 8:15:00 | 8.25 |
| `prr_misc` | the rest of B0, F3 and F4, and the floor splits | 114.0 | 4.2 h | 4:30:00 | 4.50 |
| `prr_ibu` | route 2, R-ID, R-SUP and C-IBU | — | — | 0:30:00 | 0.50 |
| **total** | | **550.8** | | | **25.00** |

**Cap: 25.0 CPU node-h, the sum of the five limits.** It binds three ways:
1. **Slurm.** On one node a job cannot charge more than its `--time`, so the five `--time` limits sum to the cap.
2. **The gate.** The full jobs start only after `prr_dry` completes, every one of its tasks has ended and C-PAIR has
   passed.
   - Each full job's gate projects its whole queue, tail included, from the dry run's measured per-level rates, packed
     onto 8 lanes as `xargs -P 8` feeds them.
   - If a projection exceeds 0.9 × that job's `--time`, the job does not start. The study comes back to the director
     with the measured rates, to be repriced.
   - Every level type is in the dry run, so nothing starts on an assumed rate.
3. **No raise.** A full job's `--time` can be lowered from the dry run's measurements, never raised without an
   addendum the director binds.

**After a stop:**
- there is no resume without an addendum the director binds;
- the products already made are kept and pinned;
- nothing is read until every job has completed. An incomplete study is reported as INCOMPLETE.

**Job-name family: `prr_`** (`prr_dry`, `prr_iter`, `prr_cap`, `prr_misc`, `prr_ibu`).
- No committed file uses it: `git grep -i -E '\bprr_'` over the tree at `52334c34` gives no hit.
  <!-- absence-ok: scoped to the stated git grep over the whole tree at the named commit -->
- The director tells every fenced lane before any go (the job-family rule).

**Who runs it.** A cluster lane the director assigns at binding submits the jobs, watches them and charges them from
`sacct`. This lane writes the code and does not connect.

### 10.4 Calendar and inputs

- **The inputs are FD-STAB's:**
  - `of_inputs_5d.npz` and `bkg_dump.npz` (pscratch, the s5p bank);
  - the s5p detector directory;
  - the pv-ladder closure ratio;
  - for route 2, also IBU-1's and REF-G1's world inputs and the S1 bank.
- **C-PAIR also reads** FD-STAB's control closure products under `/pscratch/sd/j/josephrb/fd-stab-a1r-20261104/`.
- **Their exposure dates are not recorded here.** As FD-STAB did, a DTN pins-and-atime check precedes the dry run
  (`FD-STAB-DECLARATION.md:349-351`). If an input is missing, differs or is exposed before the planned run, the study
  stops and reports.
- **Overlap with ENS1.** The ensemble-estimator lane (director-helper-3) reads the same inputs. It runs FD-STAB's 18
  closures at seed 991000 and compares them with the same FD-STAB control products
  (`fd/rounding-stability-20261106/ensemble/ENS1-DECLARATION.md:118-127`).
  - Its products and job names are its own. This study writes nothing it reads.
  - Both read FD-STAB's control products, which pushes their atime, and so their exposure, later.
  - The director's job-family notice goes to that lane too.
- The jobs read through the production loaders, which update atime. That is legitimate use
  (`DECISION-20261101-joseph-eventloops-copy-to-cfs.md` item 4). Any inspection read uses O_NOATIME.

## 11. For the director: design questions that touch rulings

1. **No estimator change (§6).** Is FD-STAB §6's terminal rule the rule here: no level is adopted, whatever PR-3 shows?
   The licences in the header assume yes.
2. **F0b's truths as the object.** FD-STAB §3.1's selection-contamination rule kept F0b's truths out of a stability
   input that selected a candidate. Here nothing is selected and the graded truths are the subject. Is grading at them
   admissible under that rule?
3. **The order of work.** Rev 1 is design only, and the code is not written. Should I write the code now and send rev 2
   with digests for the audit? Or would you rule on the design first?
4. **The cap.** 25.0 CPU node-h under the 11-01 authority. You check the current balance against the half-balance
   rule.

The other choices are the lane's, as the brief allows:
- the levels;
- ρ's definition;
- the bars 0.05 and 9.03 s;
- IBU on MC half A;
- background-inclusive pseudo-data;
- the split floor.

## 12. Not changed

- **Unchanged:**
  - the reported result R00–R15 and every covariance block;
  - every fake-data readout, Table II and REF-G1;
  - the paper and the note.
- **No code is edited.** No bound file is touched.
- **Nothing is run, submitted, deposited or tagged.**
<!-- absence-ok: a statement about this declaration's own status -->
