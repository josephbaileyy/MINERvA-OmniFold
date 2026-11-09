# The short methods paper, prose draft with placeholders: report (2026-11-09)

**Recorded by** `director-helper-3`, for the director. The draft is on PR #977, `draft/methods-short-20261109`. It is not
for merge until the director says so, and no wording is approved.

**What it is:** the short methods-and-validation paper of `DECISION-20261109-joseph-methods-baseline-and-plan.md`
(#976), items 1–3 and 6.
- It is built on the director's approval of OUTLINE.md, with the three answers: rewrite `paper_body.tex` in place;
  Appendix A to S10; about 6,500 words, Tables 1–2 and Figs. 1–3.
- It applies the journal-editor's read of the outline (JINST referee and copy-editor).
- It applies the director's ruling on the χ² divisors.

## Counts against the base

Both drafts are built by the committed scripts, `rater-calibration/make_rater_copy.sh` and `make_supp_rater_copy.sh`,
and both exited rc 0.

| | round 5 (`bc8673186`) | short draft |
|---|---|---|
| paper, pages | 17 | 13 |
| paper, words (blind rater copy) | 12,701 (sha256 `7470a0e9…`, equal to the committed round-5 copy) | 8,463 (`0fef2e44…`) |
| Supplement, pages | 18 | 24 |
| Supplement, words (blind) | 10,143 | 13,516 (`1c5fa5be…`) |
| paper tables and figures | Tables I–VII, Figs. 1–4 | Tables 1–2, Figs. 1–3 |

**About the 8,463 words:**
- It is 1,963 over the 6,500 target, and it counts the placeholders as one `[PENDING: …]` each.
- Table 1 is 689 words, Table 2 about 250, and the three captions about 310.
- **Prose alone is about 7,200.** Once the three groups are filled, the variants add about 250 words: the fill test's
  builds run 9,584–9,771 words, against 9,277 for the normal build.
- **To reach 6,500,** the remaining cuts would remove findings' evidence rather than history. Each is a choice for the
  director:
  1. a shorter Table 1, such as one row per finding;
  2. the run-period paragraphs of §4.2, to S6;
  3. the 2D covariance paragraph of §6.2, to S6, with its coverage test kept;
  4. Table 2's $C_{\mathrm{total}}$-only columns, with their paragraph, to S9.

  Together these are about 900 words.

## The structure

**Changed from OUTLINE.md, after the editor's read:**
- a "method and validation strategy" section comes before the findings (§3.3, the editor's A1). It defines the truth
  sets once, reconciles the 12 graded truths with the 17 of the ensemble comparison, and states each criterion once;
- every Table 1 row names its estimator, 2D or 5D (A2);
- descriptive section titles (A3);
- arabic numbering, lowercase cross-references, and equations numbered by section (C1);
- the descriptive names replace the internal labels (D). `check_round` GONE lists them;
- the generators and the cell definition stay in the paper (B3, B4), as does the iteration count's rule (B1);
- the stopped coverage test says what stopped it (B5).

**The sections:**
1. Introduction
2. Data and observables
3. Unfolding method and validation strategy
4. Benchmark against the published two-dimensional measurement
5. Recovery of controlled truth changes
6. Reproducibility, stability and uncertainty calibration
7. Discussion and conclusions

**What moved, and where:**
- S1: the 1A copy check.
- S2: the comparison of E_avail definitions, and the truth-level relation among the observables.
- S4: the estimator-choice history and the mechanism's ratio detail.
- S6: the eigenmode, flux, bootstrap, run-period and C_model detail, and COV2D's per-cell flags.
- S8: the Cramér–Rao reading and the per-truth binned-unfolding residuals.
- S9: the first coverage test's gate diagnosis, the eight-cell GiBUU reading and the tune sensitivity.
- S10 (new): the illustrative output's text, the generator definitions, the generator comparison (Tables S7, S8) and
  Fig. S1.
  - round 5's Tables III–V are not duplicated. S3 and S5 already carry them (Tables S2, S4, S5), and S10 points to
    them.
- S11 (new): the two validity rules in full.

Each moved paragraph names its round-5 line in a comment, and keeps that line's evidence route.

**The label map** for the result package is `label-map.tsv`, with 75 labels across the paper and the Supplement, read
from the build's `.aux` files by `make_label_map.py`.

## Placeholders

**The pending groups.** There are three, each printing one `[PENDING: …]` until its record lands:
- **the prior-retention study (FD-PRR):** the §5.3 paragraph, a Table 1 row and an abstract clause;
- **the bias-half validity rule (V-HALF):** §5.4 and a Table 1 row;
- **the like-for-like coverage test (LL5D):** §6.3, a Table 1 row and an abstract clause.

**Where the classes come from:** `make_values_fived16.py` holds the keys and their class sets, with the declaration
line for each; `variants.md` holds one row per site.

**The macros:**
- `\fvgroup` and `\fvcase` are defined in the generated `values_fived16.tex`;
- `values_fived16.tex --check` passes.

## Checks (all at the round's commit)

| check | result |
|---|---|
| `methods-short-20261109/check_round.py . ` | PASS: variant sets, no number in a variant, every key defined, numerals against `bc8673186` (two new, 136 and 285, ledger L-12b), ONCE and GONE |
| `check_round.py --self-test` | PASS: each planted defect is caught |
| `check_round.py . --fill-test` | PASS: five builds, every pending key at each class index; no `[PENDING`, no `??`, no undefined reference |
| `make_values_fived16.py --check` | PASS: 3,717 values, 10 listed-truth sentences agree |
| `check_supp_pointers.py` | PASS: 29 pointers |
| `check_sec4_receipts.py` and `--self-test` | PASS, 17/17. The 0.676 % median is now found in `supplemental_body.tex` (S6), and the check reads that file |
| `tools/registry/check_registry.py` | PASS. ALIASES rows 38 and 47 and ATTRIBUTION row 17 are re-cited from `paper_body.tex:93` to `:103` (digest `0c58175ad15b5fed`; the three other stale hints that `--repoint` would refresh, in rows not this round's, are left as they are); `results_index.py --write` regenerated `records_estimators.tex` |
| `make_rater_copy.sh`, `make_supp_rater_copy.sh` | rc 0. The holds drop cleanly (multiset PASS), and 8 of 8 Supplement table captions are present |

**What the checks don't cover:**
- **The prose of a variant** is checked for its class set and for digits, not for its wording. Its wording is part of
  the reads.
- **The V-HALF sentence** is drafted from the bias-half decision. The rule's declaration is not yet committed, so the
  sentence needs a re-read when it lands (ledger L-17).
- **The JINST class isn't installed,** so the build is revtex, with JINST numbering and referencing.
- **Keywords** (the editor's C3) aren't added yet, because they need JINST's controlled list.

## For the director

- **The rater copy builds.** `rater-copy/manuscript-short.blind.txt` and `rater-copy/supplement-short.blind.txt` are
  committed with their sha256s above, for the round-6 blind reads (#978).
- **W-items** are in `ledger.md`:
  - W-1 to W-6 are the outline's;
  - W-7: the per-learner χ² clause kept, which is the editor's B2;
  - W-8: "declared" in the approved B0 and RS1 sentences, kept verbatim;
  - W-9: the article type, and a resolvable identifier for the analysis note;
  - W-10: authorship and the data-use statement.

  Each is marked "for Joseph via the director" where the editor said so.
- **A front-door discrepancy, unrepaired:** `AGENTS.md:27` still gives the 2D central value as 3.073e-38, "1.1 %
  above the paper". The paper's 3.069e-38 and ratio 1.010 are the refined estimate (`values.tex:8`, RE-2 E_R/Q_R);
  3.073e-38 is the purity-subtracted one (`values.tex:79`). The editor raised it as E1. AGENTS.md is the front
  door's owner's to change.

## Round 6 and the fixes after it (2026-11-09)

**The reads.** The round-6 blind JINST reads (#982) scored `e3b99c82b` at 4, 4 (Sonnet) and 5, 5 (Gemini), a mean of
4.5. All four recommend major revision. Their README records my two defects in the text they read:
- the placeholders printed internal labels;
- the abstract's calibration sentence overclaimed (W-11).

**What this commit does:**
- **Applied:** the editor's presentation fixes, C4, A2, and the director's items 1–5. Each is listed in
  `QUEUE-editor-1.md`, with what was not applied and why.
- **Table 1:** moved to §3.3 as a test map, one row per test, every status word defined in its caption. Each pending row
  prints one marker, with the status "Pending" (`\fvgroupalt`).
- **The supplement:** S4's internal date is gone. check_round now refuses ISO dates in the printed paper and
  Supplement, and internal labels in the printed pending-group names.
- **Fig. 3:** the caption and §5.1 name each panel's estimator. The 74 % is always named with its variant, and the
  reported estimator's result at that truth (Table 2) is cited beside it.
- **§4.1:** states the near-singular published covariance, its condition number and its 73 well-determined directions
  next to χ²/ndf. "Validation" is gone from the method's section titles and from Table 1's caption. The paper's title
  and its "methods and validation study" phrase are W-1.
- **The telegraphic phrases the reads quoted** are rewritten, along with the S4 jargon (MAT, PPFX, "H2 grid").
- **W-22's recommended draft** is in §1.
- **W-OPTIONS.md** gives the director's W-items with options, recommendations and records.

**Counts:** 13 pages, 8,696 blind words, up from 8,463. The status definitions, the symbols, the bar and the W-22
sentence add words, and the presentation cuts take some out. No new rater copy is built for a round, per the director.

**One check found during the round:** the Data availability first sentence is protected text (the rater script
refuses a change to it). My gloss there was reverted, and goes to Joseph with W-19.
- **Registry:** ALIASES rows 38 and 47 and ATTRIBUTION row 17 are re-cited to `paper_body.tex:68` (digest `824f4ce05ad1b7b0`), the estimators paragraph after the table moved; `records_estimators.tex` is regenerated. **The label map** is regenerated (`label-map.tsv`).
