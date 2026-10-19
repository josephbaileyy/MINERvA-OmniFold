# Plain-language pass: implementation record

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-18. Under
[`DECISION-20261018-joseph-plain-language-pass`](../../../DECISION-20261018-joseph-plain-language-pass.md) and the
frozen brief [`PLAIN-LANGUAGE.md`](PLAIN-LANGUAGE.md) (§5's deliverable). The agents' reports are in
[`plain-language/PLAIN-LANGUAGE-REPORTS.md`](plain-language/PLAIN-LANGUAGE-REPORTS.md), cited below as R1–R14.

**CITABLE FOR:**
- what the pass changed and how it was checked;
- the director's rulings on base defects (C7);
- the list of decisions it leaves to Joseph.

**NOT CITABLE FOR:**
- any claim, number or scope (unchanged by design);
- final wording. The J3–J5 wording stays provisional until the review with Ben, and the decisions in §6 are open;
- any outward act (J6).

## 1. Commits (branch `stageF/plain-language-20261018`, base `main` `28d28626`)

| commit | content |
|---|---|
| `99b4a4c4` | decision record, frozen brief, `check_invariance.py` (before any deliverable edit) |
| `386ece45` | the rewrite (three writers: paper, primer, note) and the director's first C7 rulings |
| `24ec59af` | fixes for every MATERIAL and MINOR finding of the three preservation reviews; further C7 rulings; the checker's mid-line-comment detector |
| `bf00b312` | fixes for the verifier's findings |

Files changed, all in scope (brief §2): `main_paper.tex`, `paper_body.tex`, `main_primer.tex`, `primer_body.tex`,
`main_note.tex` (abstract), `sec_execsummary.tex`, `sec_summary.tex`, and the 2D ranges of `sec_systematics.tex`,
`sec_results.tex` and `sec_validation.tex`.

## 2. What changed

- **Paper** (R3, R11): every section was rewritten except Sec. III, most of V, VI A and VI D, which were left nearly
  as they were (R7).
  - Internal terms are replaced or defined at first use: "construction", "closeout", "declared conventions",
    "qualified", "claim p value", "determinate", "documented exception", "block", "exact-split", "claim variant".
  - The statistical-block paragraph in IV B now starts with the block that is quoted.
  - The run-period caveats are plain sentences.
  - The W1 endpoint sentence, identical in paper and note, now reads: "The result's intervals, bias and covariance
    have not been independently validated." It names the three things the endpoint ruling says are missing
    (DECISION-20261014 §2, l.49–56).
  - 11 → 12 pages; page 12 holds references only.
- **Primer** (R4, R12):
  - Section 3 is reordered within itself:
    - it opens with a findings list, each finding with its caveats;
    - the trust check comes first;
    - a new subsection, "Limits on the multi-quantity results", follows those results.
  - The tree learner has one name, defined once.
  - PET, MINOS, coverage, κ, MEC, Tune v1, acceptance and bootstrap are explained.
  - Status codes and project vocabulary are removed.
  - 12 → 14 pages.
- **Note** (R5, R13):
  - The scope subsection, the D-disclosures, the executive summary and the summary are in physics prose.
  - Internal identifiers in printed text are replaced by descriptions, except VL162 and VL170, which the appendices
    use and the text now defines.
  - KNOWN_ISSUES row numbers moved from printed text into the adjacent comments. Where the issue is open, the printed
    pointer reads "tracked in the analysis repository's known-issues log".
  - The run-period block's required clause (D5) is reworded; every element is kept (§4).
  - Still 123 pages; the executive summary stays on its pages.

## 3. Mechanical invariance (`plain-language/check_invariance.py` against `28d28626`, at `bf00b312`)

| deliverable | numerals | value macros | cite keys | ref targets | labels | base comment lines |
|---|---|---|---|---|---|---|
| paper | 325, same | 68, same | 64, same | 35, same | 18, same | all 204 survive |
| primer | 76, same | 13, same | 7, same | 5, same | 3, same | all 32 survive |
| note | lost 92 ×2, 95 ×2, 96, 85 ×2, 91, 84; gained 2 ×7 | 84, same | 28, same | 147, same | 36, same | all 264 survive |

- **The note's numeral differences are all explained:**
  - The lost numerals are ten printed KNOWN_ISSUES row numbers. Each moved verbatim into a comment beside its
    sentence.
  - The seven 2s are notational: five come from `$\chi^{2}$` replacing "covariance distance", one from the gloss
    of C₂ as "fraction within 2σ", one from "2D" in a paragraph title.
  - No number was added or removed.
- **No new line hides text behind a comment.** The detector was added in `24ec59af`, after the paper's fixer found
  and repaired seven such lines in its own work, and was tested on a planted case.
- **No file changed outside scope.**

## 4. Review and verification

- **The preservation reviews** were three fresh agents, one per deliverable, comparing 386ece45 with the base,
  paragraph by paragraph (R6–R8):
  - paper: 3 MATERIAL, 10 MINOR, 7 NOTE;
  - primer: 2 MATERIAL, 7 MINOR, 4 NOTE;
  - note: 2 MATERIAL, 6 MINOR, 5 NOTE.
- **The seven MATERIAL findings:**
  - a normalization-only check written as agreement with the marginals (paper and note);
  - a wrong gloss of "population coverage" (paper);
  - the flux defect softened into a refinement (paper);
  - "nothing new was adopted" widened into a false "no change to the method" (primer);
  - a findings-list item that lost its caveats in the reorder (primer);
  - the D5 clause's reason for needing no reference period wrong, and its own-response element lost (note).
- **The fix round (R11–R13)** fixed all of them, and all MINOR findings, after checking each against the base and
  its sources. Most NOTEs were applied.
- **The verifier (R14)**, a fresh agent:
  - confirmed every disposition (48 YES, 0 NO);
  - confirmed that paper and note agree on the endpoint sentence, the coverage gloss and the marginal checks;
  - confirmed that every MATERIAL-fix sentence appears in the PDFs.
- **Its findings** were 0 MATERIAL, 1 MINOR and 6 NOTE. V1–V5 and V7 are fixed in `bf00b312`; V6 concerns the
  fixers' reports only.

## 5. Director's rulings on base defects (C7)

Each ruling aligns a sentence with content the deliverables or records already state. Each is marked in a LaTeX
comment "director ruling on base defect …" and was checked by a reviewer (R7, R14).

| id | site | correction | source |
|---|---|---|---|
| primer F1 | takeaway | "scales … where the binned method's response table does not" → extends to many quantities without the larger response table, though training, simulation and uncertainty estimation become more demanding; adds that the multi-quantity results are central values only | primer §2 |
| primer F2, F12 | abstract | "when the traditional method cannot" → "more practical than"; "faithful" → "close" reproduction | primer §2, §3 |
| primer F3 | §3 | "With the trust check passed" → central value reproduced, error bars found close in size to the published ones (as refined by review R3) | primer: quoted statistical bars untested |
| primer F4 | limits | "the uncertainty attached to the published result" → "the uncertainty quoted for the five-quantity central value" | `sec_5d.tex` l.305–306 |
| primer F6 | low-recoil | adds "That measurement defines true available energy more broadly, so this comparison is not quantitative." | `paper_body.tex` l.488–492 (base) |
| primer F11 | trust check | "completely independently" → "independently of the published analysis" | same paragraph (shared flux constraint) |
| paper F3 | IV B | "three run periods" → "three groups of run periods" | period-unfold REPORT l.42–44 |
| note F1 | §uq-boot | "these explanations" (antecedent cut 2026-10-05) → efficiency gain, regularization bias or undercoverage | `43aaa140` text |
| note F2 | summary, primer | "as first built" → "in use when the fixed-truth coverage test ran" | `sec_validation.tex` l.216; `app_history.tex` |
| note M2 | note abstract, executive summary, summary | "reproduces the lower-dimensional result to ≈1–2%" → "passes marginal-normalization checks … to ≈1–2%" (the summary's version was already wrong at base) | `sec_3d.tex` l.122–133 |
| F-r2-1 | note §uq-boot, summary, paper IV B, paper conclusions, primer findings | the quoted statistical block "has not been tested independently" or "awaits an independent coverage test" → "has had no coverage test" | DRAFT-disclosures D2 |

## 6. Builds

`build_all.sh`, all four targets, in a scratch copy of the tree at `bf00b312`:
- rc 0, and each PDF "written by this run; no unresolved references";
- `check_dead_containment.py` and `check_sec4_receipts.py` PASS (15/15);
- `pytest test_check_sec4_receipts.py test_build_all.py` 63 passed.

Page counts:

| PDF | pages | sha256 |
|---|---|---|
| main_note.pdf | 123 | `7cedd11d…` |
| main_paper.pdf | 12 | `1b4c5e34…` |
| main_primer.pdf | 14 | `bd3c90eb…` |
| pet_note.pdf | 26 | `73e83707…` |

## 7. Reader tests, before and after (R1, R2, R9, R10)

- **Paper.**
  - Before: the register problem was real and concentrated in IV B, VI B(i), VI C, VII and Data availability.
  - After: Sec. II, III, V and VI D read as normal PRD prose. IV B, VI A–C, VII and Data availability are still
    hard going.
  - Remaining causes:
    - limitations still arrive as negations before the positive number;
    - the history of the analysis still sits in the body;
    - the central negative result rests on "predefined criteria" and a "target total width" the paper never states
      numerically.
- **Primer.**
  - Before: pages 3–4 and 8–10 read as a review log.
  - After: pages 1–4 do the job. Pages 8–11 still read as a review record: the limits take about five pages against
    two for the findings, and they are not ranked.
- **Why the after-tests still find a gap.** The brief froze content: no number added, no paragraph cut or moved
  between deliverables, no change of claim strength. The remaining problems are mostly of those kinds, so they are
  Joseph's decisions (§8).

## 8. Decisions left to Joseph

The full items, with exact text and proposals, are the F- and P-lists in R3–R5 and R11–R13. Grouped:

| theme | items | what it would do | director's recommendation |
|---|---|---|---|
| **A. State the numbers the hedges stand in for** | paper F4 (the model-dependence bound and the target total width), F5 (the 1.1% integrated agreement in the abstract), F7 (the fine grid's binning), F6 (the halving rate, stated as an assumption), F12, F17; primer F-new-1, F-new-2, F-new-8, F7 (rounding false precision) | turns "prevents … at useful precision" and similar into stated results | yes for F4, F5, F7, F17 and the rounding; F6 as an assumption with its value; the others case by case |
| **B. Move history and repeated caveats from the paper and primer to the note** | paper P2–P9, P15, P16; primer P1–P9, P-new-3; note P1–P5 | gives the final procedure in the body and one paragraph on blinding and analysis order, with the history in the note | yes, under the same preservation review. P6 has no note home yet |
| **C. Claim-strength wording** | paper F1 (a failed coverage test stated as miscoverage), F15 ("reject the hybrid null hypotheses for all five"), F14, F21, F22, F13, F8, F9, F11; primer F5, F8, F9, F10, F13, F-new-3, F-new-4; note F3–F6 | makes a stated result say exactly what was tested | F1 and F15 yes (they are more precise); the others need your reading |
| **D. Outside the pass's scope** | bibliography titles with internal names and three references without a locator (paper P11, primer P-new-1); `\pubhold` text (P12); the acknowledgments' AI paragraph (P13, text you approved on 2026-10-06/08); the "GENIE CV" label (P14, W10); figure legends (paper P10, primer P-new-2, F-new-6); `result_status_rows.tex` (note F7); the provenance tracker rows (note F-r2-3) | the parts referees see that the pass could not touch | bibliography and `result_status_rows.tex` yes; the rest your call |

## 9. Caveats

- **Same model.** The director, writers, reviewers, verifier and readers are all Claude Opus 5.5 on claude-school.
  The readers are simulated, and Ben is the first outside reader.
- **Reader quotes.** The reader reports quote from page images, so their quotes may differ slightly from the
  source.
