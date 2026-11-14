# History restructure, §5 (sec_validation.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13.

**The rule, verbatim as adopted:** history stays in the note only if removing it would change a reader's understanding
of the reported object, its reproducibility, its evidential independence or its limitations. Everything else goes to
the ledger. Each "fixed before" names its object, and "declared" alone is replaced.

**Referee:** for §5 it gave "20–30 %, compress / appendix: keep failed coverage outcomes and exact applicability; move
secondary analyses and the same-ensemble diagnostic to an appendix". Its item 5 (the attribution clause written after
the pilot pulls) is marked "Disclosure—stay".

**Base:** `docs/analysis-note/sec_validation.tex` and `app_statmethods.tex` at
`2cac548bdfb9ee90aae6f7138a5144f13e712911`. Line numbers are the base's.

## The changes

| id | base line | old text | new text | ledger home |
|---|---|---|---|---|
| V1a | :188 | "the declared test reads \emph{under-covers}." | "the test reads \emph{under-covers}." The same paragraph keeps "A second coverage test, declared before it ran," (with its object) and "The thresholds were fixed from the null before any pseudo-experiment was read." | 2cac548bd:sec_validation.tex:188 |
| V1b | :188 | "against declared thresholds of …" | "against thresholds of …", for the same reason | 2cac548bd:sec_validation.tex:188 |
| V2 | :228–239 | the paragraph "Same-ensemble pull diagnostic (not a coverage test)" and its two following paragraphs, with their source comments | moved verbatim to App. A as `\subsection{Same-ensemble pull diagnostic}` (`sec:pull-diagnostic`, app_statmethods.tex), following the referee. In §5.4 it is replaced by the pointer "The same-ensemble pull diagnostic of an earlier ensemble of 200 2D closure unfolds, which is not a coverage test, is in App.~\ref{sec:pull-diagnostic}." | no text leaves the note; 2cac548bd:sec_validation.tex:228-239 |

**Kept as they are, because each is a disclosure, applicability or limitation the rule keeps:**
- The band genealogy that names which band the fixed-truth test scored (:137).
- The design, criteria and positive control "specified before any toy was generated" (:137).
- The interim failure and the stop (:146).
- The secondary analysis "added after the pilot" and the attribution clause "written after the pilot pulls had been seen" (:152), which is the referee's item 5. It is kept verbatim: the current text is more exact than the referee's suggested rewrite, and the rewrite would drop "fixed before the full run".
- "The band was then rebuilt … the quoted statistical block has not been tested" (:154).
- The post hoc rescoring and its circularity (:163).
- The single-toy diagnostic, "Its decision rule was recorded before it ran" (:165).
- Both scope paragraphs (:183, :209).
- The tune test's limits (:206).

**Numbers and keys:** `numdiff.py` over §5 plus App. A, base against new, comments stripped:
- Removed: none.
- Added: "200" and "2" in the pointer, both from the moved paragraph's own "$N_{\text{toy}}=200$ 2D closure unfolds".
- Value keys and macros: unchanged. `\pullFrac` and `\pullMeanAbs` move with the paragraph.

## The Development-history appendix: new rows

| row | from | content |
|---|---|---|
| D6 | :137, :146, :152, :154 | the completeness-divided band: the first-built band, quoted when the test ran. The test found tail undercoverage and stopped at the interim. The undercoverage is attributed, partly, to its completeness term, and the band was rebuilt without it. The quoted block is a separate ensemble, not tested. The attribution clause for the undercoverage outcome was written after the pilot pulls had been seen. |
| D7 | :137, :154, :163 | the undivided band: rebuilt without the division, since superseded, and rescored only post hoc, on the same toys. The fixed-truth test's toys and result had been seen. |

## Disclosure checklist

| disclosure | in §5? | survives |
|---|---|---|
| the 2D adoption after the published distance was known | no (§3) | — |
| the post-observation run-period term | no (§4); the tune test excludes the run-period term (:188) | — |
| reused samples and seeds | yes: the simulation-side scatter reuses the band's resampling (:183), the rescoring is partly circular (:163), and the closure toys are built on the training MC (:165) | ✓ unchanged |
| the invalid q3 deformation | no | — |
| the stopped coverage tests | yes, the fixed-truth test stopped at the interim (:146) | ✓ unchanged, and in D6 |
| the data-informed joint-test design and budget extension | no | — |
| the missing response uncertainty | no | — |
| the generator-sample problems | no | — |
| the target-correction sensitivity | no | — |
| also found: the attribution clause written after the pilot pulls (:152) | yes | ✓ unchanged, and in D6 |

## Unreleased support

`UNRELEASED-SUPPORT.md` lists §5's sites: TwoDFollowup2026 [39] at :46, and NoteRecords2026 [34] at :137 (coverage-fixed-truth) and :228 (coverage-toys). The
latter now sits in App. A.8, with its line to be re-measured in the list's next refresh. Nothing changes here.

## Meaning read (codex-school gpt-6.1-sol, high, read-only; reads/PROMPT-two-question.txt)

- **Pass 1:** OVERALL PASS, with no FAILs.
  - Question 1: V1a, V1b, V2, D6 and D7 pass.
  - Question 2: V1a and V1b are LEDGER; V2 is NEEDED and kept verbatim in App. A.
  - No disclosure was lost.
  - The answer is in reads/sec_validation-pass1.txt.
