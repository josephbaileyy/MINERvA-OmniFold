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

**After the editor's second read of f51d22c8b:**
- **Applied (presentation):**
  - Table 1's held-out-tune row gets its "not independent" qualifier back.
  - The run-period groups are written out once, and the reconstruction-level reference 1A–1E (without 1F) is stated.
  - The abstract's variant uses "the estimator".
  - §5.3 defines the composite labels, "clears", and the 9.03's origin, and the repeated "at these truths" is cut.
  - Table 1's caption is shorter.
  - "record" becomes "result" in §5.1.
  - The 0.8 median is named as over the 153 quantities.
  - The 204 degrees of freedom are explained from the AR23 readout README.
- **Sent to the director:**
  - W-22: the editor's "one covariance" point becomes a new recommended option 0 in W-OPTIONS.md. The paper's W-22 text is unchanged, since the director asked that no W-item be applied before the decisions.
  - W-11 is redrafted as one sentence per like-for-like outcome. The current sentence contradicts the both-cover
    variant, and it is the one C3 failure found.
  - The new W-24 covers how the published covariance is characterized.
  - The holds-enforcement and citable-home submission blockers, in W-OPTIONS.md.
- **Counts:** 13 pages, 8,842 blind words.

## Follow-up: before submission

The director, 2026-11-09:
- **A submission-time check that refuses "[HOLD:"** in the built paper and Supplement. It is not added to the normal
  build (`build_all.sh:283` refuses only "PENDING:"), because the paper carries its funding and deposit holds by design.
  check_round should self-test it when it is built.
- **The first hold's results have no citable source for a JINST reader:** the IBU comparisons, the gate diagnosis, the
  per-period benchmark, the rounding studies, the 2D held-out-tune coverage test and the validity rules. These are
  banked for Joseph with W-19 and W-21: the deposit, and what the note must carry.
- **The AGENTS.md refresh** (the stale 2D value and Q's 6.45/4.75) is on the director's follow-up list, not on #977.

## Banked for Joseph

- **W-4, naming a future bias–variance study as the basis for the ensemble's adoption question.** The director decided
  option 3: it is not named in the paper. My option 1 is banked as a scope question for Joseph. Both positions:
  - **IR-sol (`answer.txt:22-25`):** "A referee can reasonably question the adoption rule, but a promised study cannot
    supply its missing trade-off result … Joseph says nothing about the future study enters this initial paper without
    a new decision (`943d5f97:…:59-64`). Options 1 and 2 exceed that scope, even as promises rather than findings."
  - **Mine (W-OPTIONS.md, W-4):** three of the four round-6 reads, and G1 too, ask for exactly that basis. One sentence
    would state the basis without claiming any result. I read "nothing about it enters this paper" as being about the
    study's result, not its existence.
- **W-9, W-10, W-19 and W-21,** as before.
- **A both-cover calibration sentence,** if the like-for-like test covers at both tunes. It would be a coverage
  statement. The current W-11 sentence holds in every outcome without it.

## Reader item 2 (C_PL,5D), for the director: no change applied

**Does the paper show the fake-data readings with and without C_PL,5D side by side? Not fully.**
- Table 2 shows the reported covariance (with the block) and C_total alone.
- The reading under C_total + C_resp, the reported covariance without the block, appears only in §5.2's text, for its
  one change: the GiBUU E_avail shape, R06, z = 2.01 against 1.76.

**Proposed, from existing numbers only:** a third column group in Table 2, "C_total + C_resp (without C_PL,5D)", with
χ², p and cells per truth, from `make_values_fived16.py`'s committed `f0b-<truth>-chi2int-nopl`, `-pr-nopl` and
`-cells-nopl` keys. These are the same readout's without-block arm, `fd_f0b_readout.json` pinned in `NOPL_READOUTS`.
- It adds no number that is not already in `values_fived16.tex`.
- §5.2's sentence would then point to the column.
- **Its cost:** Table 2 widens from 9 to 12 numeric columns. It can stay `table*`, at `\scriptsize`.
