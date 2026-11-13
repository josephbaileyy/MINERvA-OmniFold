# The S8 headline-test index (2026-11-13)

Joseph (2026-11-13, "yes can you do the restructure?") asked, via the director's ruling, that the Supplement's tables
S11 (`tab:tests-spec`: what each test tests and how it is built) and S12 (`tab:tests-result`: statistic, threshold,
result) become one results index. His reasons: too much white space, and S12 row 9 is hard to read. The director's
pdflatex harness found that the best column widths shorten the tables by only 7.5 % and 6.9 %.

## What changed (docs/analysis-note/supplemental_body.tex)

- **One xltabular, `tab:tests` (Table S11):** Test | Statistic and criterion | Reading | Details.
  - Booktabs rules and the repeated header are kept, with `\addlinespace` between rows and ragged-right X columns.
  - Details names this Supplement's sections that set each test out, with the paper's sections in parentheses.
  - The column widths are typed as `\hsize` factors, as in the tables before, so check_supplement_constants.py
    excludes them. The referee's `Y{..}` argument form is equivalent, but that check would read its widths as
    unlisted decimals.
- **Readings carried unchanged:**
  - Rows 2, 4, 5, 6, 7, 8, 9 and 10 are copied programmatically from the old S12 cells.
  - Row 9 is the paper's section 6.2 sentence. Row 10 is the LL5D group with all seven `\fvcase` arms.
  - Row 4's trailing "(the paper's table 6)" pointer moves to its Details cell.
- **Design clauses go to each test's home section,** as new sentences, each with a "Moved 2026-11-13" comment:
  - test 1 → S6.2;
  - tests 2 and 7 → S4.4, two new `\paragraph`s;
  - test 3a → S8.1, after paragraph 0;
  - test 3b's full tune names → S8.1, "The held-out tunes";
  - test 4 → S8.2, `\paragraph{The study's design.}`;
  - test 6 → S10, first paragraph;
  - test 9 → S8.6, second sentence.
  - After the first meaning read: test 5's common inputs → S7's first paragraph; tests 8 and 10's estimators and
    test 8's full-simulation draw → S8.3; test 3b's half split and estimator → S8.1, "The held-out tunes".

  Clauses the home section already printed are not repeated (parts of tests 3a, 3b, 5, 8 and 10).
- **Pointers repointed:**
  - the S8 introduction's "Table S11 specifies …, and table S12 gives …" sentence;
  - S10's "table S12 (test 6)".

  The paper and paper_labels.tex had no pointer to either old table. make_paper_labels.py was rerun for the new
  `\psec` targets: P-sec:calib, ibu, ll5d, paired2d, repro2d, vhalf.
- **main_supplement.tex:** the xltabular package comment now names the index.

## The inventory

`inventory.tsv` has one row per clause of every old S11 and S12 cell (140 rows: 59 in the index, 65 moved to a home
section, 16 already printed there), plus the two repointed sentences.
- Columns: id, test, old table, old column, clause, how, now_prints_at (file:line), locator.
- `make_inventory.py <worktree> <out.tsv>` regenerates it. Every locator must occur exactly once in the comment-free
  lines, so each line number is found by the script, not typed.

All 81 `\fvval`/`\fvgroup`/`\fvgroupalt`/`\fvcase` keys of the old tables still print in the Supplement, outside
comments.

## The referee's worked rows (the layout referee's report, 2026-11-13)

Each was checked against the source cells before use:
- **Rows 1, 3a and 4:** they type literal numbers. The index keeps the number macros.
- **Row 4:** it would move the class breakdown to S8.2 ("Reduced-setting classes: see section S8.2"). S8.2 prints the
  classes' definitions, but not this study's class results, so the index keeps the `\fvgroup{prr}` reading unchanged.
- **Row 9:** it reconstructs "as 10" by hand as "Cutoffs: 0.025/16 per cell; 0.025 jointly". Against rows 8 and 10,
  that is row 10's threshold, but the old row 9 states only "as 10". So the index keeps "as 10" and types no number.
  - The referee's relocated test-9 design also adds row 10's two band variants ("without and with the GEANT4 neutron
    and proton bands") to test 9.
  - S8.5 says these variants exist because of the first test's own checks, and the 1B design record
    (DECISION-20261101-joseph-1b-staged-method-coverage.md) names no such variants. That expansion was not used.

## Checks at the committed head

They are listed in the commit message: the Supplement and paper builds, make_values --check and --self-test,
check_supplement_constants.py, check_style.py --part supplement (no regression), check_supp_pointers.py, check_round.py
--fill-test, step_check.sh against ab9a50335 (inventory changes only), and the gate.

The codex-school meaning reads of old against new used gpt-6.1-sol at high effort, read-only:
- `meaning-read-1.txt`: FAIL, with four problems, all design clauses that the cited home text did not fully state.
  They were fixed, and the inventory was repointed.
- `meaning-read-2.txt`: the second round, on the committed text.

## Inherited, not changed (for Joseph via the director)

- **Row 9's reading is no longer the paper's section 6.2 sentence word for word.**
  - The old S12 cell, and the S8 comment calling it "the paper's section 6.2 sentence", date from an earlier paper
    revision.
  - paper_body.tex:626 now has no "staged redesign" clause, and it adds "Its checks led to the second test's
    like-for-like construction".
  - The reading is kept unchanged, as ruled.
- **Test 9's "as 10" (the old S11's Simulation and What is varied) literally includes test 10's two band variants.**
  - S8.5 says those variants follow from the first test's checks.
  - The new S8.6 sentence ("Its estimator, simulation, variations, statistic and thresholds were specified as the
    second test's") is no stronger than "as 10", but it inherits that looseness.
- **S8.6 opens "at the two tunes", while old S11 gave test 9 a plug-in truth as well.** The new sentence names all
  three truths, and the opening is unchanged.
