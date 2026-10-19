# Plain-language pass on the deliverables: frozen brief

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-18, under
[`DECISION-20261018-joseph-plain-language-pass`](../../../DECISION-20261018-joseph-plain-language-pass.md).
**Base:** `main` `28d28626` (PR #160).

**CITABLE FOR:** the rules, the scope and the acceptance of the plain-language pass.
**NOT CITABLE FOR:** any claim, number, figure, scope, ruling or disclosure content. Those stay as decided (J1–J5,
DECISION-20261006 and the records the sources cite). Not citable for any outward act (J6).

## 1. Why

Joseph, 2026-10-18: the deliverables' language "alienates the physics readers and what they are used to reading".
The internal records are written so that no sentence can be read as an overclaim, and they should stay that way.
The deliverables inherited that register:
- stacked negations ("is not evidence of coverage … passes by construction; it is not a test");
- project vocabulary ("Full scientific closeout is not achieved", "declared conventions", "standalone
  covariance", "construction");
- project history in the paper's body (a band first built, rebuilt, then rescored post hoc).

The pass rewrites how things are said, not what is said.

## 2. Scope

| deliverable | sources | in scope |
|---|---|---|
| paper | `main_paper.tex`, `paper_body.tex` | the abstract, the body and the captions (not the acknowledgments, `\pubhold` or the bibliography) |
| primer | `main_primer.tex`, `primer_body.tex` | all text, abstract and captions |
| note | `main_note.tex` | the abstract only |
| note | `sec_execsummary.tex`, `sec_summary.tex` | all |
| note | `sec_systematics.tex` | §1 up to, but not including, `\subsection{What changes for the higher-dimensional products}` |
| note | `sec_results.tex` | `\subsection{Comparison to the published measurement}` and `\subsection{Uncertainty budget}` |
| note | `sec_validation.tex` | `\subsection{Fixed-truth coverage of the 2D statistical band}` |

**Out of scope:**
- every other file, including `values*.tex`, the PET note, the figures and the gates;
- the internal records;
- the rest of the note.

## 3. Rules

**C. Content is invariant.**
- **C1.** Every number, value macro, citation, cross-reference and label survives in the same deliverable. A
  numeral may change only as a spelling (e.g. "three" for "3") or by merging an exact duplicate in the same
  paragraph. Each such change is listed in the implementation record.
- **C2.** Every limitation, caveat, exclusion and condition survives, attached to the claim it qualifies (the
  failure EDITORIAL-20261011 H1 recorded: a caveat moved away from its claim made the defects read as not affecting
  the budget). Two statements of the same caveat in one paragraph may merge.
- **C3.** No new claim, strengthening or weakening:
  - "untested" must not become "expected to cover";
  - "indicative" must not become "good agreement";
  - "not excluded" must not become "negligible".
  A plainer sentence that might read stronger or weaker than the original is not made. It is listed as a flag
  (§5, F-list), with the proposed text, for Joseph.
- **C4.** Nothing moves between deliverables, and no paragraph is dropped. A cut or move that would help, such as
  project history from the paper body to the note, is listed as a proposal (§5, P-list), with the exact text and the
  note location that already carries it.
  Paragraphs may be reordered within one section of one deliverable, as long as every caveat stays with its claim.
- **C5.** The J3–J5 content stands. The decided D0–D12 content (`DRAFT-disclosures.md` revision 4, as written into
  the sources at `28d28626`) is reworded, not reduced. That includes W1's "full scientific closeout is not achieved"
  meaning and W2's required clause. Each such site keeps its `% J3/J4 provisional` comment, and a short
  `% plain-language pass (DECISION-20261018-joseph-plain-language-pass)` comment is added beside it.
- **C6.** LaTeX comments are kept. Each base comment line survives verbatim and travels with its sentence.
- **C7. Defects in the base are reported, not fixed silently.** A writer may find a base sentence that is
  inconsistent with its own deliverable's body or with the records it cites, such as a summary that is stronger than
  the section it summarizes. The writer leaves that sentence's content as it is, and lists it with a proposed
  correction (§5, F-list, marked "base defect").
  - The director rules on corrections that only align a sentence with already-decided content.
  - Any other change to a claim goes to Joseph.

**R. Register.** The paper reads like a PRD article in neutrino physics; the note's in-scope parts read like a
collaboration technical note; the primer keeps its own plain voice for a physics-literate non-specialist.
- **R1.** Say what was done and what it gives, positively and first. Then say what it omits or has not tested,
  once, in plain words.
  - Not: "Containment of the observed differences by this construction is not evidence of coverage."
  - But: "Because the block is built from the differences among the periods, it covers them automatically; this says
    nothing about whether its size is right."
- **R2.** No internal vocabulary in printed text:
  - closeout, receipt, record, ruling, lane, adopted (as a project act), declared conventions;
  - "construction" as a noun for a covariance;
  - J/W/C/D/KI/VL/OI identifiers, Q/S5/C_PL symbols, unless the text defines them.
  Use the physics word: the covariance, the uncertainty, the estimate, the method.
- **R3.** Define every non-standard term at first use, or replace it with the standard one. Terms that need this:
  - "population or simultaneous interval coverage";
  - "calibrated covariance-based generator significance";
  - "exact-split";
  - "double ratio";
  - "block".
- **R4.** One idea per sentence, mostly under about 30 words. No chains of three or more qualifiers on one noun.
- **R5.** History appears in the body only where a reader needs it to understand a limitation that is still true,
  in as few sentences as C1–C4 allow. "Earlier", "rebuilt", "changed after" and "post hoc" stay where they disclose
  something a reader must know, such as the post hoc choice of the central-value estimator.
- **R6.** Prefer the standard phrasing of the field: "we do not assign an uncertainty for", "is not included in the
  covariance", "has not been tested with pseudo-experiments", "the χ² is shown for orientation only, because the
  cross-covariance between the two measurements is not available".
- **R7.** Keep what already reads well. Do not rewrite for its own sake.

## 4. Acceptance

1. `check_invariance.py` (this directory) against `28d28626`. Every difference it prints is explained, line by
   line, in the implementation record, and nothing changed outside the scope.
2. The four builds in a scratch copy (`build_all.sh`, all targets) rc 0, with no undefined references, and both
   gates pass. Page counts are reported, and the paper does not exceed 12 pages.
3. **An independent preservation review** (fresh context, no authorship of the pass). It checks, paragraph by
   paragraph, from the base text, that every limitation, condition, number and claim in the base is present and of
   the same strength in the new text. Findings are fixed before merge.
4. **A fresh outside-reader test** of the rebuilt paper and primer PDFs (the same two reader briefs as the
   baseline, Appendix A). The before and after are reported to Joseph.
5. Pre-commit (13 checks), `generate_manifest.py --check --at-sha HEAD`, `verify_hash_bindings.py`.

## 5. Deliverable

`PLAIN-LANGUAGE-IMPLEMENTATION.md` (this directory) holds:
- the files and paragraphs changed;
- the invariance-check output and the explanation of each difference;
- the F-list (C3: flagged, not made);
- the P-list (C4: proposed cuts and moves, not made);
- the review findings and their dispositions;
- the build and page counts;
- the reader-test comparison.

**Same-model caveat:** the director, the writers, the reviewer and the readers are Claude Opus 5.5 on claude-school.
Ben is the first outside reader.

## Appendix A. The reader briefs

The baseline readers ran on 2026-10-18 on the review PDFs built from `28d28626` (`main_paper.pdf` `9cae2bc3…`,
`main_primer.pdf` `35805adf…`). The after-test uses the same briefs on the rebuilt PDFs, in fresh contexts. Each reader
opens only its PDF.

**Paper reader.** A neutrino cross-section physicist (a postdoc on MINERvA, T2K or MicroBooNE). This reader knows:
- unfolding (D'Agostini, regularization);
- covariance matrices and multi-universe systematics;
- χ² against a covariance;
- pseudo-experiments and coverage;
- OmniFold, by name.

The reader has never seen this project and reads the draft as a PRD submission. It reports:
1. the overall verdict;
2. passages in non-physics register, each with the quote and the usual physics phrasing, keeping every disclosed
   limitation;
3. undefined or non-standard terms;
4. hedging that hides the result;
5. project-history passages the body does not need;
6. wording that lowers trust below what the content warrants, and places where plainer wording would risk
   overclaiming.

**Primer reader.** A physicist outside neutrino physics (a condensed-matter or astrophysics graduate student) or a
physics-literate science journalist, who has never seen this project. It reports the same six items for a
plain-language primer.
