# History restructure, §4 (sec_systematics.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13.

**The rule, verbatim as adopted:** history stays in the note only if removing it would change a reader's understanding
of the reported object, its reproducibility, its evidential independence or its limitations. Everything else goes to
the ledger. Each "fixed before" names its object, and "declared" alone is replaced.

**Referee:** for §4 it gave "10–20 %, compress". Its items 3 (§4.6's earlier-budget forensic account, to the ledger)
and 4 (§4.7's earlier 5D construction, cut) apply here.

**Base:** `docs/analysis-note/sec_systematics.tex` at `a4cec87570b82421b37269c83e14c64bc86c0d7a`. Line numbers are
the base's. Every removed passage stays in the commit history at that sha and line, which is its ledger home.

## The changes

| id | base line | old text | new text | ledger home |
|---|---|---|---|---|
| S1 | :53 | "A declared test of the analysis procedure's 2D covariance, remade at each of two held-out GENIE~v3 tunes, reads under-covers" | "A test of the analysis procedure's 2D covariance, remade at each of two held-out GENIE~v3 tunes, with thresholds fixed before it ran, reads under-covers". The object comes from §5's own "declared before it ran" and "declared thresholds" (sec_validation.tex, sec:coverage-tunes). | a4cec8757:sec_systematics.tex:53; COV2D-DECLARATION.md |
| S2 | :220 | "a declared test of the procedure's 2D covariance remade at each tune's truth reads under-covers" | "a test of the procedure's 2D covariance remade at each tune's truth, with thresholds fixed before it ran, reads under-covers" (as S1) | a4cec8757:sec_systematics.tex:220 |
| S3 | :233 | "when a predeclared relative-error gate passes" | "when a relative-error gate, fixed before the reweighted unfolds were run, passes". The gate is PV-2D's statistical gate (`stat_max` = 0.05, pv2d/DECLARATION.md:75). The binding (pv2d/BINDING.md) accepts it as a deviation before the run pin, that is, before the reweighted unfolds ran. A first wording, "fixed before the measurement", was failed by the meaning read as moving the coarser cell's timing onto the gate. | a4cec8757:sec_systematics.tex:233 |
| S5 | :327 | "A 5D covariance construction that preceded it used both mean-centered and CV-centered unified throws (\S…uq-combine); neither variant is used, and no magnitude from either is quoted." | cut (referee item 4) | a4cec8757:sec_systematics.tex:327 |

## Proposed and reverted: S4, the "Comparison with the earlier 2D budget" paragraph (:282–286)

The paragraph is restored byte for byte. The first meaning read failed the compression:
- **S4, and D4's first wording:** "three defects" adds a count to the original's open "the following defects".
- **S4d:** the 0.088 % lost its referent, the band's size.
- **S4b:** "A common displacement cancels to first order in the MAT mean-centered covariance" is a NEEDED limit on how to read the mismatch, and it was lost.
- **S4c:** "Because the May input and code revision are not available" is a NEEDED reproducibility limitation, and it was lost.

The earlier budget remains a comparison in §4, so its defects and their limits stay in full. Only S4a and S4e were LEDGER, and they stay too, because restoring the paragraph whole is clearer than a partial edit.

The proposal, kept for the record:
| id | base line | old text | proposed | ledger home |
|---|---|---|---|---|
| S4 | :282–286 | the paragraph "Comparison with the earlier 2D budget", 3 sub-paragraphs (base text at a4cec8757:sec_systematics.tex:282, :284 and :286) | one paragraph, which keeps the three defects, each one's correction, every number (205, 0.088 %, 60 of 205), the EtaNCEL example, the mismatch's limits ("does not invalidate the entire covariance, supplies no correction to subtract and cannot be attributed more specifically"), "drops Rvp1pi", "no conclusion about the published analysis's implementation follows", the 60-of-205 qualifier and "The values printed for the earlier budget were not changed". The removed pieces are S4a–S4f. | a4cec8757:sec_systematics.tex:282-286; docs/orchestration/state/next-preparation-20261009/two-d-followup (TwoDFollowup2026) |
| S4a | :282 | "(the May sweep)", the internal name | cut | as S4 |
| S4b | :282 | "A common displacement cancels to first order in the MAT mean-centered covariance." | cut | as S4 |
| S4c | :282 | "Because the May input and code revision are not available," (the reason it cannot be attributed) | cut ("cannot be attributed more specifically" stays) | as S4 |
| S4d | :284 | "The band is small, \SI{0.088}{\percent}, but the double count is a defect in the construction of the covariance;" | the number stays, in parentheses; the "defect" framing is carried by the paragraph's "three defects in its construction" | as S4 |
| S4e | :286 | "so neglecting them everywhere is unsupported" | cut (the 60-of-205 diagnostic and its qualifier stay) | as S4 |
| S4f | :286 | "and the quoted universe block takes its lateral bands from re-unfolds of re-selected universes (\S…uq-universes)" | cut. It is the current construction, stated in §4.1 (:12) and §4.7 (:302). | as S4 |

**Kept as they are, because each is a disclosure or limitation the rule keeps:**
- The run-period block "is an uncertainty assigned for an observed inconsistency between run periods whose cause is
  unknown" (:166).
- "Because the block is built from the observed differences among the periods, it contains them by construction"
  (:187). This is the post-observation run-period disclosure.
- "Identified after the measurement, these 52 cells hold …" (:237).
- The earlier statistical bands scored by the coverage studies (:53).
- The earlier ten-seed block as the σ yardstick (:99, :245, :273).

**Numbers and keys:** `numdiff.py` on the base and new files, comments stripped:
- Removed: only the "5" of S5's "5D".
- Added: none.
- Value keys and macros: unchanged.

## The Development-history appendix: new rows

| row | from | content |
|---|---|---|
| D4 | :282–286, :143, :166 | the earlier 2D budget: its construction defects, each corrected, three named ("among them": first wording "Three construction defects" failed the read); its printed values unchanged; still a comparison for the flux weights (§4.4) and the run-period step (§4.5) |
| D5 | :99, :245, :273 | an earlier ten-seed training-seed block (first wording "before the fixed-seed statistical block" failed the read as an added chronology): superseded, because its spread was dominated by the bootstrap × seed interaction, which the fixed-seed statistical block now contains; its σ remains the yardstick of the completeness and retraining tests (§4.6) |

There is no row for S5's earlier 5D construction: nothing uses it and no magnitude from it is quoted.

## Disclosure checklist

| disclosure | in §4? | survives |
|---|---|---|
| the 2D adoption after the published distance was known | no (§3) | — |
| the post-observation run-period term | yes, :166, :187 | ✓ unchanged |
| reused samples and seeds | no | — |
| the invalid q3 deformation | no | — |
| the stopped coverage tests | the 2D tune test is cited (it completed: under-covers), with its thresholds now named as fixed before it ran (S1, S2) | ✓ |
| the data-informed joint-test design and budget extension | no | — |
| the missing response uncertainty | no; the covariance's omitted terms (:220–229, :245) are unchanged | ✓ |
| the generator-sample problems | no | — |
| the target-correction sensitivity | no | — |
| also found: the C_model step cells identified after the measurement | yes, :237 | ✓ unchanged |

## Unreleased support

The note-wide list, `UNRELEASED-SUPPORT.md`, already includes §4's sites:
- TwoDFollowup2026 [39] at :282;
- NoteRecords2026 [34] at :121, :143 and :332.

None changes here.

## Meaning read (codex-school gpt-6.1-sol, high, read-only; the director's two-question form, reads/PROMPT-two-question.txt)

- **Pass 1:** OVERALL FAIL.
  - Question 1 failed S3, S4, S4d, D4 and D5.
  - Question 2 classified S4a, S4e and S5 as LEDGER, and S4b and S4c as NEEDED, both lost.
  - S1 and S2 passed, and no disclosure disappeared.
  - The answer is in reads/sec_systematics-pass1.txt.
  - The fixes: S4 restored whole; S3 reworded to the record's object; D4 and D5 reworded.
- **Pass 2, on the revised section:** OVERALL PASS, with no FAILs.
  - Question 1: S1, S2, S3, D4 and D5 pass.
  - Question 2: S5 is LEDGER and leaves; S4's items are retained.
  - No disclosure was lost.
  - The answer is in reads/sec_systematics-pass2.txt.
