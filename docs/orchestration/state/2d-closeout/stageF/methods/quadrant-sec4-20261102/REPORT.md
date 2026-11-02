# REPORT The quadrant sentence and Section IV in PRD style (2026-11-02)

**By** the paper rewrite lane (Claude), for the director and for Joseph, who reads this round before merge.

**Under:**
- `DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md` (#690), items 1 and 2;
- the director's work order of 2026-11-02.

**MEASURES:** nothing new. Every number comes from committed readouts through `make_values_fived16.py`:
- step C-R, `fd/gencmp-e/c-r/overlap_refined.json`, pinned `f1f2fb78`;
- GENCMP X, `fd/xcov/run/k/k.json`, pinned `f3dc2a34`.

**CANNOT AUTHORIZE:** a claim, a reading or a wording. Every changed sentence is below, before and after, for Joseph.

**What did not change:**
- the covariance, Table IV and every printed value (all 2630 base values print as before);
- the abstracts, the title, `main_paper.tex`, `main_note.tex` and the primer;
- Sec. I's "Interval coverage has not been validated." (a held sentence, outside this round).
<!-- absence-ok: quotes the paper's printed coverage and validation sentences, before and after, with their sources; not a claim of this report -->

Sentences are quoted as they print. Section numbers are the built PDFs'; the note's Secs. 10.2–10.6 of the base are 10.3–10.7 now, since the new Sec. 10.2 comes before them.

## Part 1. The quadrant sentence (decision item 1)

### The paper, Sec. IV D ("Normalization and closure"), first paragraph

**Before:**
> Of the joint-test estimator's results, only the three-observable marginal has been compared with the
> lower-dimensional result it extends. Its area-weighted total agrees with the two-dimensional result to 0.141 %, a
> comparison across the two estimators.

**After.** The first two sentences are the decided text, word for word, with Joseph's two amendments on #695 (below):
"one-parameter" is added, and the χ² range becomes its upper bound. The third sentence is the reworked marginal clause.
> Summed over each of the four (pT, p∥) quadrants, the sixteen-cell result agrees with the two-dimensional result: the
> sums differ by −1.5 to +0.7 per cent, and with the covariance between the two results evaluated from the systematic
> variations they share, the four differences give χ² ≤ 1.24 for four degrees of freedom (p ≥ 0.87), with no
> quadrant beyond one standard deviation. The statistical correlation, and that of four systematic terms that could not
> be evaluated directly, are bounded within a one-parameter family of valid covariances, over which the agreement holds. Of the
> joint-test estimator's other results, only the three-observable marginal has been compared with the two-dimensional
> result, agreeing with it to 0.141 % in area-weighted total over all 205 reported cells (Ref. [14], Sec. 10.2).

The paragraph's last sentence, on the normalization and closure checks, is unchanged.

**Where each number comes from:**

| printed | key | source | value |
|---|---|---|---|
| −1.5 to +0.7 per cent | `x-dpct-min`, `x-dpct-max` | C-R, `quadrants.*.2D.d_pct` | QC −1.478, QD +0.724 (QA +0.141, QB −0.217) |
| χ² ≤ 1.24 | `x-chi2-hi` | X, `primary.r1`, the family's largest value (convexity) | 1.2402 at r = 1 (1.170 at r = 0, in the note's Table 14) |
| p ≥ 0.87 | `x-p-min` | X, the smaller p, rounded down | 0.871 at r = 1 (0.883 at r = 0) |
| no quadrant beyond one standard deviation | (asserted) | X, the largest \|z\| | 0.985, QC at r = 1 |
| four systematic terms | (asserted) | X, `bounded` | AGKYxF1pi, AhtBY, BhtBY, MinosEfficiency |
| the statistical correlation is bounded | (asserted) | X, `route` = A | the paired replicas failed K2 (X report §4) |
| over which the agreement holds | (asserted) | X, every reading | "agree", with no change on the grid |
| 0.141 %, 205 cells | unchanged | `sec_3d.tex:85` | the marginal of configuration (e) against E_R |

**The marginal clause.** The work order asked it to name its estimator and its range:
- **The estimator** is the joint-test estimator, the one the sixteen-cell result uses.
- **The range** is all 205 reported cells.
- **"other results".** The old "only" became false once X compared the sixteen-cell result, so it now covers the
  estimator's other results.
- **Not QA's +0.141 %.** The note says this 0.141 % is a different quantity from QA's +0.141 % (0.141044 % against
  0.141053 %).

### What the readouts establish over the whole family r ∈ [0, 1]

`k.json` records the readings at r = 0 and r = 1, and whether the reading changes anywhere on the 10,001-point grid. It
does not change.
- **Every |z| < 1 over the family.** Each quadrant's variance is linear in r, so each |z| is largest at an end.
- **χ² ≤ 1.24 and p ≥ 0.87 over the family.** χ² is convex in r, so its largest value, and the smallest p, are at an
  end.
- **χ² has no lower bound over the family.** Convexity does not bound the minimum, and `k.json` lacks the bounded
  blocks needed to compute χ² inside [0, 1]. So the paper prints the upper bound only (Joseph, on #695); the note's
  Table 14 gives both ends.

`quadrant_values` asserts each stated fact, and seven self-test plants are each refused by their own assertion:
- route A and the four bounded bands;
- "agree" at every r, in every reading;
- every |z| < 1;
- X's d equals C-R's;
- V_d(0), rebuilt from `k.json`'s own and paired blocks, reproduces χ² = 1.170.

### The note: new Sec. 10.2, "Quadrant sums against the lower-dimensional results"

It goes before the covariance subsection. The section's opening now lists it, and the existing 3D descriptive paragraph
moves under it unchanged. It contains:
- **The quadrants.** The four quadrants, the two results and their estimators, configurations (e) and (f), and the
  marginal's 0.141 % named as a different quantity.
- **Without the cross covariance (C-R), Table 13.**
  - The rule: agree at every ρ; agree below a correlation ρ*; differ beyond two standard deviations at every
    non-negative ρ.
  - Per quadrant: S₁₆ and S₂D with their σ, d/S₂D, z at ρ = 0, the reading and ρ*.
  - The without-C_PL,5D reading, printed only.
  - The outcome: all four agree, QA at every ρ, the others below correlations of 0.9902 (QC) to 0.9997 (QB).
- **With the cross covariance (X), Table 14.**
  - **What is paired:** 34 of the 38 systematic bands, universe by universe; the 5 lateral shifts; the normalization;
    the run-period terms, period by period; and the C_model shifts, generator by generator.
  - **What is bounded:** the statistical correlation (the paired replicas do not fit the stated statistical blocks, and
    the joint matrix is not positive semidefinite) and the four bands whose weight check failed on non-finite ratios.
    They enter as r·S₁₆^½S₂D^½, a one-parameter family, not every admissible correlation.
  - **The rule:** p ≥ 0.05 and every |z| ≤ 2.50, read on the grid. 99 controls passed.
  - **The result:** per-quadrant z and implied correlations at r = 0 and 1; χ², p and the largest |z| for the primary
    reading, against the four-block covariance alone, and with the run-period pair set to zero.
  - **The ends-of-family argument** is stated, including that χ² between the ends is not recorded.

## Part 2. Section IV in PRD style (decision item 2)

For each sentence removed from the paper, the table gives where the fact now prints. The note's line numbers are those
of this branch.

### IV A, the reported covariance

**1. C_model.**
- **Before:** "It represents unscaled generator-shape dependence, not a calibrated bound, and its coverage at truths
  held out of its construction has not been validated, and the first two tests of an earlier route to a calibrated
  model term with validated coverage did not pass (Ref. [14], Sec. 10.2)."
- **After:** "It is a measure of unscaled generator-shape dependence, not a calibrated bound (Ref. [14], Sec. 10.3)."
- **Where the facts are now:**
  - **The held-out coverage** is in the paper's Limitations, item 1, and in the note, `sec_fived16.tex:98`.
  - **The earlier route's first two tests** are development history, in the note only, `sec_fived16.tex:101`.
<!-- absence-ok: quotes the paper's printed coverage and validation sentences, before and after, with their sources; not a claim of this report -->

**2. C_PL,5D.**
- **Before:** "It was added after these differences were seen, following an audit whose stopping criterion was fixed in
  advance. Passing that audit does not validate the block: its size and coverage have not been independently
  validated."
- **After:** "It was added after these differences were seen, following an audit whose stopping criterion was fixed in
  advance."
- **Kept in the paper:** the post-hoc addition. The abstract states the block's timing, and IV A still gives its size's
  68 % interval.
- **Where the removed facts are now:**
  - **"Passing that audit does not validate"** is development history, in the note only, `sec_fived16.tex:175`.
  - **Its size** is in Limitations item 1.
  - **Its coverage** falls under the sixteen-cell total's coverage in Limitations item 1. The note gives size and
    coverage at `sec_fived16.tex:175`.

### IV B, the two-dimensional benchmark: the last paragraph

Gemini's draft (`sec4-prd-style-gemini-answer.txt` §3) was the starting point, checked against the facts.

**Before:**
> We quote the LightGBM result as the central value because its covariance uses the same estimator. The distance
> depends on the estimator (Ref. [14], Sec. 6.4). The learner was selected after the LightGBM and exact-split comparisons
> with the published result, so the benchmark is a reproduction rather than an independent validation. The
> purity-subtracted exact-split result differs from the central value by a median of 1.03 % per bin (maximum 17.6 %), as
> detailed in Ref. [14], Sec. 3.2.

**After:**
> We quote the LightGBM result as the central value because its covariance uses the same estimator. The comparison is a
> consistency benchmark, not a blind validation: the learner was chosen after the LightGBM and exact-split results had
> been compared with the published result, and the distance depends on the estimator (Ref. [14], Sec. 6.4). The
> purity-subtracted exact-split result differs from the central value by a median of 1.03 % per bin (maximum 17.6 %;
> Ref. [14], Sec. 3.2).

**How it was checked against Gemini's draft:**
- The post-hoc learner choice is stated once.
- Gemini's "agrees closely" is not used. The 1.03 % median and the 17.6 % maximum are printed instead.
- "The distance depends on the estimator", which Gemini dropped, is kept.

### IV C, the two-dimensional covariance

| before (removed or changed) | after | where the fact is now |
|---|---|---|
| "The covariance has not been independently validated and provides no calibrated significance for generator comparisons." | removed from IV C | Limitations item 1; note `sec_systematics.tex:214` |
| "The coverage of this block and of the total covariance has not been tested." | removed from IV C | Limitations item 1 ("the coverage of the current statistical block and of the total covariance has not been tested"); note `sec_validation.tex:152` |
| "We make no coverage claim on independent simulated samples or simultaneously over all reported bins and projections." | moved verbatim to Limitations item 1 (an A7 sentence, held byte-exact) | Limitations item 1; note `sec_systematics.tex:214` |
| "Because the block is built from the observed differences among the periods, its size is not validated and its own consistency check cannot fail." | "Because the block is built from the observed differences among the periods, it contains them by construction, and its own consistency check cannot fail." | the size is in Limitations item 1; note `sec_systematics.tex:186` |
<!-- absence-ok: quotes the paper's printed coverage and validation sentences, before and after, with their sources; not a claim of this report -->

The statistical block's definition (300 replicas at the central value's training seed, with background templates
resampled) stays in IV C.

### Limitations, the one coverage statement

**The opening.**
- **Before:** "Apart from the low stability of four of the sixteen cells (below), the limitations of these results are
  stated with the results they qualify, in Secs. III–V, and those of the calibrated tests in the companion note."
- **After:** "Apart from the validation of the uncertainties and the low stability of four of the sixteen cells
  (below), the limitations of these results are stated …" The rest is unchanged.
- **Why:** after this round, the validation status prints only in item 1.

**Item 1, before:**
> The two-dimensional covariance has not been independently validated, and its coverage has not been tested
> (Sec. IV C); the three- and four-observable central values lack intervals of validated coverage (Sec. V C); and the
> coverage of the sixteen-cell total uncertainties is not validated (the fake-data tests of Sec. IV H assess the
> estimator's bias).
<!-- absence-ok: quotes the paper's printed coverage and validation sentences, before and after, with their sources; not a claim of this report -->

**Item 1, after:**
> The coverage of the sixteen-cell total uncertainties has not been tested: the fake-data tests of Sec. IV H assess the
> estimator's bias, and the coverage test declared at two of their truths stopped before any coverage pseudo-experiment
> ran. Neither the coverage of C_model at truths held out of its construction nor the size of either run-period block is
> independently validated (Ref. [14], Secs. 10.3, 10.4 and 4.5). The two-dimensional covariance has not been
> independently validated and gives no calibrated significance for generator comparisons. An earlier statistical band of
> that result undercovered in its tails in a coverage test at fixed truth (Ref. [14], Sec. 5.2); the coverage of the
> current statistical block and of the total covariance has not been tested. We make no coverage claim on independent
> simulated samples or simultaneously over all reported bins and projections. The three- and four-observable central
> values lack intervals of validated coverage (Sec. V C).
<!-- absence-ok: quotes the paper's printed coverage and validation sentences, before and after, with their sources; not a claim of this report -->

**The three things the work order requires:**
- **The sixteen-cell total's coverage is untested.** The stopped test is paper Sec. IV H.
- **The 2D covariance is not independently validated.**
- **The earlier 2D statistical band failed a fixed-truth coverage test, and the current band is untested.**
  - The failure: `OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`, FAIL-undercoverage. C1 = 0.679 is inside its
    window; C2 = 0.912 is below it.
  - The note: `sec_validation.tex:144`, and `app_statmethods.tex:619–620`.
  - The current band untested: `sec_validation.tex:152`.
<!-- absence-ok: quotes the paper's printed coverage and validation sentences, before and after, with their sources; not a claim of this report -->

A coverage result that lands later replaces its clause (decision item 2).

## Points for the director and Joseph

1. **"one-parameter": applied (Joseph, on #695).** The paper now reads "bounded within a one-parameter family of valid
   covariances". This is the X declaration's A4 qualifier (`FD-GENCMP-X-DECLARATION.md:247`, `:389`).
2. **The χ² range: replaced by its upper bound (Joseph, on #695).** The paper now reads "χ² ≤ 1.24 for four degrees of
   freedom (p ≥ 0.87)". 1.24 is `x-chi2-hi`, the r = 1 end. χ² is convex in r, so the family's largest value is at an
   end, and `quadrant_values` asserts it is the r = 1 end. `x-chi2-lo` is dropped; the r = 0 value, 1.170, stays in the
   note's Table 14.
   - **Rounding.** The r = 1 value is 1.2402, which rounds to the printed 1.24 but lies 0.0002 above it. A strictly
     rounded-up bound would print 1.25 (or 1.241 at three decimals). The text prints 1.24, as Joseph worded it.
3. **G1b:paper-g-09 is released from the hold (the director's ruling on #695).**
   - This is the old IV B sentence "The learner was selected after …", held byte-exact by the r22 round's rule.
   - Decision item 2 orders that paragraph rewritten, and the director ruled that #690 stands over the hold.
   - It is in `check_held.py` RELEASED with that reason, and `r22/STEP2-PAPER.md` records the release. Its facts are
     ledger row Q-6.
   - `check_held.py` is back at the three pre-existing flags: G1:paper-g-08, G1:paper-s-08 and G1b:paper-s-07.
     `CHECK-HELD.txt` shows the same copy before the release (4 flags) and after (3).
   - G1b:paper-g-20, the A7 coverage sentence, is not flagged: it moved verbatim.
4. **The paper is 13 pages; the base is 12.** Page 13 holds only references [25] and [26]. I did not cut a fact to win
   them back.
5. **Kept in IV A:** "It was added after these differences were seen, following an audit whose stopping criterion was
   fixed in advance." It is a disclosure that the abstract relies on, not a validation sentence.

## Checks, on the final text (`fbac3d4b5` and its records commit; before the rebase onto `848c7df7a`, `eb0de39db`, with the same `docs/analysis-note`)

| check | result |
|---|---|
| `make_values_fived16.py --check` and `--self-test` | PASS: 2716 values. Seven new plants, each refused by its own assertion |
| `check_values.py` (`VALUES-CHECK.txt`) | PASS: all 2630 base keys unchanged. 86 added keys (44 `cr-`, 42 `x-`), each recomputed from its readout. A changed value, a changed base key and a stray key each make it FAIL |
| the ledger (`check_ledger.py`, base `7bac3c634`) | 11 rows, 61 probes, 14 changed base sentences, 0 failures; self-test PASS |
| the decided text | prints word for word in `main_paper.pdf` (whitespace ignored, punctuation kept) |
| `build_all.sh` | PASS: paper 13 pp, note 134 pp, primer 15 pp; no "??". The paper's one overfull box is the base's (Table III) |
| the two-direction review (`review.md`) | nothing false. 3 Medium: 2 fixed, 1 to Joseph (point 1). 7 Low: 5 fixed, 1 to Joseph (point 2), 1 reported (the page count) |
| the rater copy | `make_rater_copy.sh` exits 0 on the clean tree; holddiff's multiset check PASSES |
| `check_held.py --fact-held` (`CHECK-HELD.txt`) | the 3 pre-existing flags; G1b:paper-g-09 released (point 3) |
| `generate_manifest.py --check --at-sha HEAD` | see the PR |
| local CI (`run_ci.py`) | see the PR |
| the reading copy | 21 pages: the paper's pages 4–6 and 8–12, each followed by its base page, then the new page 13; the note's new pages 67–69, with base page 67 |

## Follow-up (director, 2026-11-02): the containment check in the standalone note repository

**The defect.**
- #665 pointed the `CONTEXT_EXEMPT[('main_note', '6.86')]` exemption at a figure sidecar outside the note tree
  (`../orchestration/…/fd_g_fig_modes.json`).
- The standalone Analysis-Note repository has no `../orchestration`, so the staleness guard reported a false STALE, and
  its `build_all.sh` exited 1. Canonical passed.

**The fix** (`check_dead_containment.py`; the director's option 2):
- **The check is unchanged** when the source is inside the note tree, or when it is present.
- **A missing out-of-tree source is still STALE in the canonical layout.** The layout test is `canonical_layout()`:
  `<git toplevel>/docs/analysis-note`, as `check_note_records.py pin` decides it.
- **Anywhere else, the guard reports SKIP with its reason.** That covers the standalone repository and a copy, as the
  other repository-dependent checks do. The canonical build enforces it.

**The tests** (`test_build_all.py::ExemptionGuardTest`):
- **The standalone shape** (the note at the top of its own git checkout, no sidecar): SKIP, exit 0, no "is STALE", and
  the in-tree exemptions still hold. With the SKIP branch disabled, this test fails.
- **The canonical layout** (`<repo>/docs/analysis-note`, sidecar missing): STALE, exit 1.

**The shown result** (`STANDALONE-CHECK.txt`):
- `bash build_all.sh` in a copy of `docs/analysis-note` outside any repository returns **rc 0** (paper 13 pp, note
  134 pp, primer 15 pp).
- In that copy, the check prints the SKIP. The base code reproduces the false STALE, exit 1.
- In the canonical worktree, the exemption still "holds", from the sidecar.
- `test_build_all.py`: 85 passed.

Nothing is submitted, deposited or tagged.
<!-- absence-ok: the report quotes the paper's coverage and validation statements before and after, with their sources; the uncomputed interior chi2 is a fact about k.json (fd_xcov.route_a records r0, r1 and outcomes) -->
