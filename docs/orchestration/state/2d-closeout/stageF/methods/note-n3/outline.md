# Note register round n3: outline for the director (2026-10-27)

**Base:** origin/main `0d919b1a`, which is n2 merged plus the reflow (#396). The branch is `stageF/note-register-n3-20261027`, created at `0d919b1a` with no commits yet. No edits come before the director approves this outline.

**Standing rules, unchanged:**
- Presentation and language only. No number, claim, scope, citation key, value macro, table value, figure or caption meaning changes.
- No fact leaves both documents. A qualifier stays wherever leaving it out would make a printed sentence false.
- No rater rewrite is adopted without checking every fact in it.
- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's.
- New prose is one source line per paragraph. After every scripted edit:
  - `reflow_tex.py --note` must leave the tree unchanged, and `--check` must pass (CI);
  - `printed_diff.py` must show only the intended sentences changed.

## Where the note stands after n2

**P1N** (sol2, 2-run means): the note's mean was 3.083 at n1's base, 3.117 after n1 and 3.133 after n2.
- 11 of 15 pieces sit at 3 or 3.25. N04, N07 and N10b reach 3.5. N12, re-scored on its delivered base text, is at 2.75.
- Every sol2 justification ends with the same verdict: the prose "require[s] a dedicated language pass".

**P2N** preferred NEW on 12 of 13 changed pieces in n2. §11 was the exception.

**So the pairwise preference is real, but the rubric score has moved 0.05 in two rounds.** The caveat study's own finding (R-N7) is that the note's distinct caveats run 3–5× the long comparators' (8.4 per 1,000 words against 1.6–2.5), and it says a register round cannot close that gap. n3 can still remove the register defects sol2 names. Reaching 3.5 may need the content decision R-N7 leaves for Joseph. See question 4.

**The work list.** On n2's delivered text, sol2 quoted 6 passages per piece. That gives 90 quotes, 69 of them distinct (`n3/sol2-quotes.tsv`). They locate the work; their rewrites are not adopted. Rough keyword classes (a quote can fall in several):

| class | distinct quotes | example (piece) |
|---|---:|---|
| stacked qualification (40+ words, or 4+ commas and parentheses) | 38 | "The comparison is binned, signal-only and noise-free; it fixes the detector response at the simulation's, uses the development truths, and covers these 144 residuals only." (N08) |
| development history and chronology | 28 | "That band is an earlier one, not the quoted statistical block." (N04); "the control no longer reproduces it" (N10a) |
| provenance or production bookkeeping | 20 | "Two provenance limits travel with the production numbers: the driver was uncommitted …" (N12) |
| internal labels and code | a few | "MnvH1D without MAT's per-universe weights (SetUnivWgts)" (N11) |
| repeated scope declarations | (in the above) | "does not meet the acceptance criteria of its specification … nevertheless uses this file" (N08, N10b, N12) |

## The moves

**R-N3a. Status, not chronology.** This covers the 28 history quotes and their like in the round's files.
- A sentence that narrates a superseded state becomes the current status, plus one pointer to where the history is kept. Examples: "X was the quoted value until 2026-10-11"; "that band is an earlier one"; "no longer reproduces"; "was not rebuilt after the flux repair".
- Where the history qualifies a printed number, its consequence stays. For example, "the regularization scan was made for the exact-split cross-check and not repeated for the quoted value" stays as a status.
- **Question 1 is where the history goes.**
  - App. history (`app_history.tex`) is the note's stated home for it. It says the body "states the current position in one or two sentences with a pointer to this appendix".
  - But the file is protected in round checkers, and its parts B and C are declared verbatim from `152ef7a6`.
  - Options:
    - **(a)** Remove a history clause only where App. history, or the records, already prints it. That gets an `N:`/`R:` probe of its home. Otherwise keep it, compressed.
    - **(b)** Also allow new paragraphs in App. history, as a new part D, "Recorded in register rounds", outside the verbatim parts.
  - I recommend (a).

**R-N3b. One home per scope statement.** This covers the repeated scope declarations.
- A scope or status that a section states more than once is stated at its home, and the other sites point to it. Examples: the 5D covariance's status, "does not meet the acceptance criteria of its specification" (home: `sec_5d.tex:250`), restated at `app_negweight.tex:182`, `sec_execsummary.tex:109` and `sec_summary.tex:46`; and "No acceptance threshold fixed before either closure is on record" (home §7), restated at `sec_execsummary.tex:40` and `sec_summary.tex:19`. The ES and §12 restatements are summaries and stay; the body repeats are the target.
- The guardrail decides each site. A restatement stays wherever the sentence would be false or misleading without it.
- Ledger: an `N:` probe of the home and an `X:` probe of each removed restatement. A pointer replaces the removed text.

**R-N3c. Stacked qualifications, second pass.** R-N2a split many sentences. sol2 still quotes 38 long ones.
- **Lesson from §11.** Mechanical splitting can read as choppy: §11 lost P2N 0 of 4 on exactly that ground.
- So n3 uses list sentences, or a "within / for / under" lead clause, where a split would repeat the subject.
- No sentence is split twice.

**R-N3d. Provenance bookkeeping, remaining.** This continues R-N2b on the 20 provenance quotes, under the same rulings: a fact leaves only where the records print it, each removal has an `R:` probe, and a consequence that bears on a printed number stays.
- The cases are N03's July-sweep reproduction sentence, N09's recovery-check scope list, and App. A's MAT-check paragraph.

**Director's items:**
1. **App. C** `app_negweight.tex:361-363`. It becomes "…, not with refined negative-weight subtraction, the intended extended-fiducial baseline". The injection designation's surviving homes are `:268-269` and `:370-371`.
2. **App. A** `app_statmethods.tex:1029`. "∼1 χ²-unit of the tension" is scoped to the exact-split cross-check's tension, checked against `:1022-1028` first. This is an accuracy clarification at sentence level.
3. **N12 re-proposal.** n2-E's App. B and App. C edits come back as candidates under the new P1 rule. They are taken from `d4a51c88`, re-checked by a fresh reviewer against the reflowed base, and scored again.
   - The fps-battery move goes with them, since it is a register move.
   - The n2-E review fix at App. C :290-294 also goes with them, because it repairs a referent that move C3 removes.
- **Dropped from the list, already done:** the stale J36 and App. A source comments. `sec_systematics.tex:227-233` was corrected in n2-B, and `app_statmethods.tex:372`, `:459-460` and `:469` were corrected in `03e98d3d`. All now cite the refined values the text prints.

**Not in n3:**
- **§11 (N10a).** It stays at base, because P2N preferred it 4 of 4 over n2's splits. Only director's item 1's counterpart could touch it, and that is App. C, not §11.
- **App. G and H (N14),** which are release text and Joseph's.
- **The 5D generator-comparison wording,** which is Joseph's (DECISION-20261026, item 5). It waits for the comparator check.
- **The protected files.**

## Batches

| batch | files | pieces |
|---|---|---|
| n3-B | sec_method, sec_systematics, sec_validation | N02–N04 |
| n3-C | sec_3d, sec_eavailw, sec_5d | N06–N08 |
| n3-D | sec_joint | N09 (§11 not touched) |
| n3-E | app_statmethods, app_statmethods_nd, app_negweight, app_response_mismatch | N11–N13, including the N12 re-proposal |
| n3-A | sec_execsummary, sec_intro, sec_summary | N01, N10b. Written last, against the new body |

Each batch gets a writer (a Claude Opus 5.5 subagent of this claude-school session) and a fresh two-direction reviewer. Then agy runs on every changed passage.

## Checks and scoring

- **Ledger.** `note-n3/check_ledger.py`, a copy of n2's with `--base 0d919b1a`, the same protected set, and `R:` probes naming a records file.
- **Guards.** printed_diff on every scripted edit; `reflow_tex.py --note --check`; `check_note_records.py`, all modes; a full build.
- **P2N.** OLD is the note at `0d919b1a`. Both orders, sol2 and gemini. A piece is adopted at 3 of 4.
- **P1N.** 2 sol2 runs and 1 gemini run per piece. The baseline is n2's delivered scores:
  - n2 final for adopted pieces;
  - the base-text re-score for N12 (3, 2.5);
  - the base+ACC score for N10a.
- **The adoption test, under the director's noise rule (ruled 2026-10-26):**
  - a piece reverts only if its sol2 2-run mean falls by **more than 0.25**;
  - a fall of exactly 0.25 gets 2 more sol2 runs, and the piece reverts only if the 4-run mean falls.
  - The noise estimate behind the rule comes from n1 and n2. On unchanged pieces the 2-run-mean deltas have SD 0.22 and a largest move of 0.25. Within a piece, run pairs differ by 0.5 in 8 of 45.
- **Stop rule:** P2N no longer prefers NEW, or P1N ≥ 3.5, or round 4. n3 is round 3.

## Questions for you

1. R-N3a: (a) remove history only where App. history or the records already print it, or (b) also allow a new part D in App. history? I recommend (a).
2. N12: re-propose n2-E's App. B/C edits as they were at `d4a51c88`, re-reviewed, or let n3-E rewrite App. B/C afresh from the base? I recommend re-proposing them as they were, re-reviewed, so the new rule is tested on the same text.
3. §11 stays out of n3. Agree?
4. "Done": after two rounds P1N has moved 0.05, while P2N keeps preferring NEW. Should n3's report also give Joseph a costed list of the content reductions R-N7 points to? These would be distinct caveats that could be consolidated or dropped by his decision. I recommend yes, as a separate list, not edits. Without it, round 4 is likely to end on the round limit, not on P1N ≥ 3.5.

## Director's rulings on this outline (2026-10-27): approved as written

1. **R-N3a: (a).** A history clause leaves the note only where App. history or the records already print it, proved by an N: or R: probe. Where neither does, the option is a new records entry under n2's ruling 1(b) (App. G, new paragraphs, pin moved), not a part D in the protected app_history. Otherwise the clause stays, compressed.
2. **N12: re-propose n2-E's text as it was**, re-reviewed, with the fps-battery move and the :290-294 fix. It scored −0.25 in n2; under the new rule that means 2 more sol2 runs, not an automatic revert.
3. **§11 stays out.**
4. **Costed content-reduction list: yes**, as a list in n3's REPORT, not edits. For each distinct caveat that could be consolidated or dropped: its homes; what the reader would lose; whether it bears on a printed number or claim; the P1N quotes it answers. Joseph decides.
- Parallel work: the comparator check and the 20-claim audit continue; the audit's edits go in their own PR; any "false as read" verdict comes to the director before editing.
