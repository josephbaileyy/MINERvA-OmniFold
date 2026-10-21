# IBU-1: a binned iterative-unfolding baseline under matched conditions (specification, frozen before any run)

**Owner:** the paper-tighten lane, as director, 2026-10-21. This is methods-paper new work: the outside referees asked
for it (X6 and X7, "is the failure OmniFold's or the inverse problem's?"), and Joseph said "sure spec them now". The
compute comes under the methods-paper approval of DECISION-20261019 §1 and DECISION-20261020 item 3 (Delta).

**CITABLE FOR:** IBU-1's question, design, reading rule and grant.
**NOT CITABLE FOR:** any result before its report.

## 1. Question, and what is already known

**The question.** Does a conventional binned iterative Bayesian unfolding (IBU), on the same simulation, background
treatment, data, cells and iteration count, show the residual bias and miscoverage that our OmniFold configurations
show? If it does, the failures belong to the inverse problem at this binning and prior; if not, they are specific to
the OmniFold implementation.

**Already on record (D-ID, `state/next-preparation-20261009/d-id/REPORT.md` §11, :522-536):**
- the boosted-tree OmniFold's median residual equals that of exact binned and fine-grid IBU at K = 5;
- the approximation share is 0.014;
- weakly constrained response directions are supported for the label-stable J and EW functionals.

D-ID was noise-free, signal-only, on development truths, and for binned estimators. IBU-1 extends it to background,
Poisson noise, coverage and the data result.

**For the paper now.** The D-ID statement can be cited in the methods paper as it stands, with its scope.

## 2. Design (declared in a file with code shas and seeds before any output)

- **Estimator.**
  - Binned IBU (D'Agostini) on the reconstruction bins of D-ID (`d-id/did.py`), unfolding to the 109 J cells.
  - Same-sample response from the analysis simulation (Tune v1), split-half where the matching OmniFold study is
    split-half.
  - Background subtracted as in configuration (a) (purity) and, separately, as a nominal background expectation.
  - Iterations: K = 5 primary, with K ∈ {1, 2, 3, 4, 5, 10, 20} reported.
- **Truths:**
  - nominal;
  - the GiBUU E_avail deformation;
  - W1, W2, W3;
  - the ~10% signal-rate reduction of the coverage test (KI 98).

  Each is applied by the code that made the OmniFold studies (`s5c_pseudo` / `s5n_pseudo` truth weights).
- **Pseudo-experiments.** Poisson draws of the reconstruction-bin contents, with background included, at the seeds the
  OmniFold studies used where those are recorded. At least 400 per truth for coverage, matching the OmniFold coverage
  test.
- **Intervals.** IBU statistical intervals from the same pseudo-experiment ensemble's spread at nominal truth, with the
  same bias-correction rule as the OmniFold coverage test (amendment 4), so the comparison is like for like.
- **Data.** The IBU data unfold at K = 5 on the J cells, compared with configurations (a) and (e).

## 3. Readout and reading rule (fixed now)

**Readout.** Per truth, over the J cells:
- the median and maximum |residual| of IBU against OmniFold;
- coverage at 68% and 95% against the same gates (0.66 and 0.94);
- the IBU data result over the OmniFold data result, per cell.

**Reading (descriptive, for the paper):**
- **"Inverse-problem limited":** the IBU median |residual| is within a factor of 2 of OmniFold's, and its count of
  quantities below the gate is within a factor of 2, at every deformed truth.
- **"Implementation specific":** IBU is better by more than a factor of 2 at the GiBUU deformation and at the rate
  change.
- **Otherwise: mixed.** Each case is reported per truth.

## 4. Grant

- At most 10 CPU node-h on m3246, or on Delta after a reproduction control there (the D-ID admitted numbers reproduced
  bitwise). Local machines may also be used, as D-ID was.
- Each job under 12 h. Every job is ledgered.
- Outputs on pscratch or scratch, nothing on CFS.
- It runs once the inputs are reachable: Perlmutter after 2026-10-27, or Delta or local machines earlier if the inputs
  can be staged.
