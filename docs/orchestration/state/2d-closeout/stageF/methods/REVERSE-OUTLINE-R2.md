# Reverse outline of the methods paper, and the structural round it motivates (2026-10-21)

**Owner:** the paper-tighten lane, as director (Stage F).
**Asked for by Joseph** (2026-10-21), verbatim:

> sure can you do the structural round? do they have any comments about the outline? what if you turn every paragraph
> into a one sentence main idea and analyze that, does it reveal anything?

sha256 of the text plus a final newline begins `b027d5a021c3ab48`.

**Text outlined:** `docs/analysis-note/paper_body.tex` and the abstract of `main_paper.tex` at main `b5028e4e`. That is
the register-round-1 paper, PR #204, and it prints 13 pages. Comments were stripped, and floats are not counted. The
word counts are of printed prose.

**CITABLE FOR:**
- the one-sentence main idea of each printed paragraph at `b5028e4e`;
- the word distribution;
- the director's structural diagnosis and the round-2 plan built from it.

**NOT CITABLE FOR:**
- any physics claim (cite the paper and its sources);
- the outcome of round 2 (see METHODS-IMPLEMENTATION.md §12).

## 1. One sentence per paragraph

| ¶ | words | section | main idea |
|---|---:|---|---|
| abs | 149 | Abstract | 2D reproduction within ~1%; five-observable central values only, with bias, undercoverage and no definition meeting 10%; generator tests reject hybrid nulls, with caveats. |
| 3 | 132 | I | Binned unfolding scales badly with observables; OmniFold is unbinned and has been used on collider data and simulated neutrino data. |
| 4 | 100 | I | We reproduce MINERvA's 2D cross section and extend it to five simultaneous but not independent observables. |
| 5 | 131 | I | The question is reliability under generator-sized mismodelling. Interval coverage and test calibration are different requirements, and a test can be calibrated without validated intervals. |
| 6 | 149 | I | The validation findings are the main results (the abstract's list, repeated). |
| 7 | 226 | I | Scope: one implementation, no measurement, hybrid nulls, averaged size, no recoil band, target mismatch. |
| 8 | 26 | I | The note has the details. |
| 9 | 283 | II | Data, signal definition, selection and simulation. |
| 10 | 438 | II | Truth-level definitions; then reconstructed W is an exact function of (pT, p∥, q3), so the five observables are not independent. |
| 11 | 241 | II | The external predictions and their convention and target differences. |
| 12 | 120 | II | Fine grid, coarse 3⁵ test grid, reported-cell rule. |
| 13 | 84 | III | How an OmniFold iteration works. |
| 14 | 174 | III | The two background treatments; training on the full sample. |
| 15 | 237 | III | Which configuration is used for what, and the history of why. |
| 16 | 157 | III | Definitions of closure and coverage, and how truth changes are applied. |
| 17 | 295 | IV | 2D: integral within 1%, χ²/ndf ≈ 2.7 shape difference, learner chosen after the comparison. |
| 19 | 186 | V | Higher-D normalizations agree; background bias at high W, removed by the negative-weight treatment. |
| 20 | 238 | V | A generator-sized E_avail change is only partly recovered (up to 74% in one cell), interpreted as regularization bias. |
| 21 | 309 | V | The coverage test fails under a ~10% rate reduction; the cause is residual bias growing with W, its source not established. |
| 25 | 213 | VI A | 2D covariance: four blocks and their sizes. |
| 26 | 197 | VI A | Run periods are mutually inconsistent; the run-period block absorbs this by construction and is not a test. |
| 27 | 225 | VI A | The 2D statistical band: an earlier version failed coverage, and the rebuilt one has no independent test. |
| 28 | 149 | VI A | The 2D intervals, bias and covariance are not independently validated. |
| 29 | 211 | VI B | The 5D covariance fails its validation criteria, and covariances depend on the seed. |
| 30 | 234 | VI C | No tested reporting definition meets the 10% target, which motivates hypothesis tests. |
| 31 | 273 | VII A | Descriptively, generators underpredict at low E_avail and high W; this is not a mechanism. |
| 32 | 199 | VII B | Definition of the hybrid null. |
| 33 | 199 | VII B | How a calibration pseudo-experiment is generated. |
| 34 | 131 | VII B | The total and shape statistics and their metric. |
| 35 | 118 | VII C | p values and shifted nulls. |
| 36 | 312 | VII C | Holm plus a sequential Clopper–Pearson gate controls FWER under two assumptions; the lost pseudo-experiments. |
| 37 | 202 | VII C | What was fixed in advance, and what was chosen after results were seen. |
| 38 | 597 | VII D | Six conditions, chiefly fine-grid convergence and simulation size, and the decision margins. |
| 39 | 219 | VII E | All ten reject; target correction; multiplier scan; the external nulls are displaced by the estimator's pull toward its prior. |
| 41 | 243 | VII E | The rejections recover known disagreements; coarse projections reject too; power. |
| 42 | 163 | VII F | No recoil-response band, and the GENIE CV rejection needs the hadronic axes. |
| 43 | 124 | VII F | A ±4% recoil-scale check: the rejections hold. |
| 44 | 189 | VIII | The validation findings (the abstract's list, a third time). |
| 45 | 143 | VIII | The tests' caveats (repeated from Sec. I and VII). |
| 46 | 128 | VIII | Why unfold before testing: reusability; a reconstruction-level test would need the same response model. |

## 2. What the reverse outline shows

1. **No paragraph explains why the method fails.**
   - Four paragraphs report the same phenomenon, in different sections:
     - ¶20, residual bias, read as regularization;
     - ¶21, coverage failure from residual bias that the nominal-truth correction does not remove;
     - ¶30, the envelope "tracks the regularization bias";
     - ¶39, the external nulls are displaced by the estimator's pull toward its prior.
   - In each, the unfolded result keeps part of its prior. No paragraph's main idea is this connection.
   - Both outside models' main remaining request is "explain why". The diagnostic evidence for it is already on
     main and is not in the paper. D-ID (`state/next-preparation-20261009/d-id/REPORT.md` §11), on the same 109
     joint cells, noise-free and signal-only:
     - the boosted-tree OmniFold leaves the same median residual as an exact binned iterative unfolding at K = 5;
     - the tree approximation accounts for a small share (0.014);
     - the label-stable residuals lie in directions the binned response constrains weakly.
2. **The thesis is stated once and never used to organize anything.** The coverage-versus-calibration distinction
   (¶5) is the paper's most transferable idea. It appears mid-paragraph in the introduction and returns only implicitly
   in ¶46.
3. **The paper is organized by kind of quantity, not by object.** The 2D story is split between Sec. IV (¶17) and
   Sec. VI A (¶25–28). Coverage appears in ¶21 (V) and ¶27 (VI A). Estimator instability appears in ¶15, ¶20 and ¶29.
   The five-observable precision result (¶30) sits in "uncertainties", although it is a consequence of the V bias. This
   is the structural complaint behind GPT's "move the coverage test" and Gemini's "merge V and VI".
4. **The main results are listed three times** (abstract; ¶6; ¶44), and the test caveats three times (¶7; ¶38–43;
   ¶45).
5. **Balance.** The application (Sec. VII, 2,780 words) is longer than the whole validation (Secs. IV–VI, 2,257 words),
   though the paper calls it secondary. ¶38 alone (597 words) is the longest paragraph in the paper.
6. **Topic sentences.** Several paragraphs bury their main idea:
   - ¶10's redundancy finding comes after 250 words of definitions;
   - ¶29 opens "We have built a covariance" when its point is that it fails its criteria;
   - ¶41 opens by saying the result is not new.

## 3. The outside models on the outline (rounds r8 and r9)

- **GPT-6.1-sol (r9 §3):**
  - the progression is conventional;
  - move the five-observable coverage test into Sec. VI, beside the intervals it evaluates;
  - condense Sec. VII C–D, moving the sequential-sampling argument, the recovery bookkeeping and the chronology to
    the note;
  - a separate Conditions subsection is defensible.
  - r8 asked for the Sec. VI rename and the fold of old Sec. VII, both done in round 1.
  - r9 §4 also asks for a summary table linking each finding to its configuration, test and limitation, and for space
    on which failures are implementation-specific and which checks a reader should carry to another analysis.
- **Gemini (r9 §3):**
  - merge Secs. V and VI, with the precision target placed beside the bias and coverage results;
  - compress Sec. VII toward its methodological takeaways (how estimator bias enters the null; sensitivity to the
    missing response systematic).
  - §4 asks for the "why".
- **Not adopted from Gemini:**
  - its rewrites that drop or change facts;
  - its unsupported mechanism, that the redundant W coordinate causes the failure. The paper says the information
    added by W has not been measured.

## 4. Round-2 plan (structural)

**Paper outline after the round:**

- **I. Introduction.**
  - The coverage/calibration distinction is the stated organizing idea.
  - ¶6's list is replaced by a findings table (finding | configuration | test | limitation | section).
  - The scope is kept, with each fact stated once.
- **II. Data, observables and domains.** ¶10 is split into definitions and redundancy.
- **III. Estimators and validation design.**
- **IV. Two-dimensional benchmark.** It now includes its covariance (former VI A).
- **V. Five observables: bias, coverage and precision.**
  - normalization and closure;
  - generator-sized changes;
  - coverage;
  - covariance and estimator stability (former VI B, with the stability sentences of ¶15 and ¶20);
  - reporting definitions and the precision target (former VI C).
- **VI. What limits the estimator (new, short).**
  - The common thread of ¶20, ¶21, ¶30 and ¶39, without asserting the coverage failure's source (not established).
  - **Claim addition, separate commit, for Joseph:** the D-ID diagnosis, with its scope.
  - The checks a reader should carry to another analysis.
- **VII. Application.**
  - Condensed. The recoil-response subsection becomes condition (ii).
  - Sequential-sampling and recovery bookkeeping move to the note's existing sections.
  - Every limitation and post-hoc disclosure stays, at least as a clause.
- **VIII. Conclusions.** They refer to the table instead of re-listing it; "Why unfold before testing" is kept.

**Rules:**
- DECISION-20261021: no fact dropped. A number may move to the note only where the note prints it.
- The `\pubhold` text is not touched.
- The paper stays at ≤ 13 pages.
- The round gets an independent two-direction review before the two models rescore it.

## 5. Joseph on the claim addition and on moves to the note (2026-10-21)

Verbatim:

> yes you can keep it, what do you mean by the no-dropped-facts rule still holds, I thought there was an option to
> reference it in the note

sha256 of the text plus a final newline begins `16cf8c483c1ab63c`.

- **The D-ID diagnosis is approved** for the paper (Sec. VI) and the note (`sec:val-departure`). It is still a
  separate commit.
- **Moving to the note is the default for detail.**
  - Any number, bookkeeping or derivation may leave the paper for a pointer to the note section where it prints.
    This is DECISION-20261020 item 2, "move as much as possible into the note".
  - "No fact dropped" (DECISION-20261021) means no fact leaves both documents.
  - The one thing kept in the paper is that each limitation or post-hoc disclosure still appears there, as at least
    a clause beside the claim it bounds. Without it, the claim reads stronger in the paper than the evidence allows.
    The detail behind the clause can move.
