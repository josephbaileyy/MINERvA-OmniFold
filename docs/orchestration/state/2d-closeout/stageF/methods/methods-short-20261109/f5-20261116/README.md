# Paper F5: section 5.4 to section 4.5, section 7 stated once (2026-11-16)

Joseph approved F5 as one bounded editorial pass on the paper's sections 5.4 and 7, with no claim changes. The
pass came from a read-only referee report kept outside the repository; this README restates it. The director ruled
on the placement. Joseph ruled on the titles, relayed by the director on 2026-11-16. Commit e51088eb1, on
director-helper-3's head adbacc6fc. It was pushed on GATE PASS, with this record.

| Change | What | Read 1 |
|---|---|---|
| A | Section 5.4 moves whole to section 4.5, retitled "Algorithm dependence of the sixteen-cell result" ("an IBU" becomes "a binned IBU"). Section 4 is retitled "Comparisons on data", section 4.2 "Paired comparisons of two-dimensional unfoldings", and table 1's block heading "Comparisons on data". The sixteen-cell IBU row moves into that block. | PASS |
| B | Table 1's caption: "Descriptive" also covers the bias-half rule, a diagnostic defined after the fake-data biases it classifies had been seen. The coverage-test sentence is unchanged. | PASS |
| C | Supplement: "grades" becomes "applies", and the bias-half rule "is graded" becomes "is applied descriptively". | PASS |
| D | Introduction: the findings paragraph is split at "Third,". | PASS |
| E | Section 7: the paragraph after the checklist is dissolved (its benchmark sentences open the section, and its bias-screening sentences end the limitations list, with "grade" now "classify"). Limitation 4's duplicate of the opening's algorithm-dependence sentence is removed, and two scope sentences are split. | PASS |

In B the record's word is "declared", and the paper prints "defined". check_round's GONE list bans the printed word
"declared", and the director accepted the substitution.

The evidence is in read1/. The read (gpt-6.1-sol, high effort, read-only) also read two files that are not copied:
old_paper.tex and new_paper.tex, which are docs/analysis-note/paper_body.tex at adbacc6fc and at e51088eb1, byte for
byte. diff.txt is `git diff -U0 adbacc6fc e51088eb1` of paper_body.tex, supplemental_body.tex and paper_labels.tex.
decision_items.txt holds the decided items of DECISION-20261110-joseph-paper-asap-vhalf-diagnostic.md. Lines 22-46
of the v-half DECLARATION.md (valid-region-20261107/v-half/) are in vhalf_decl_22_46.txt. Verdict: PASS, with no
problems ranked.
