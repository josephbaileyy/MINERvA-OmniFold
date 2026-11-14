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

`inventory.tsv` has one row per clause of every old S11 and S12 cell (145 rows: 60 in the index, 68 moved to a home
section, 17 already printed there), plus the two repointed sentences.
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
  that is row 10's threshold, but the old row 9 states only "as 10". So a1bd56bfe kept "as 10" and typed no
  number. The second round replaced it from test 9's own record (below).
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

## Second round, after a1bd56bfe (the director's layout note, and Joseph's ruling on items 1-3)

The director accepted a1bd56bfe. Joseph ruled on the three items (2026-11-13: "yes make 1–3 as you recommended").

- **The p24 break.** p24 ended after row 1, with 64 pt free. Row 2 needed about 77 pt: it is 72 pt high, plus the
  5 pt `\addlinespace` after row 1. Nothing else forced the break: there is no `\nopagebreak` or `\flushbottom`, and the
  11 rows are well under xltabular's chunk size. Three changes fixed it:
  - the caption is one line (the column headers already name the content);
  - a redundant "as the unfolding simulation" is dropped from the S8 definition of "half split";
  - row 4 is shorter (below).

  Row 2 now fits on p24, with no gap. p25 now ends 71 pt short, against 37 pt before, because row 9 (10 lines)
  cannot split. The total page-bottom gap on pp. 24–25 falls from 101 pt to 71 pt.
- **Row 4.** Two parts of its Reading move to a new S8.2 paragraph, "The study's results":
  - "Every higher iteration count and capacity lowers ρ, by at most …", in its own `\fvgroup{prr}`;
  - IBU's overshoot along the prior-to-truth direction.

  The index keeps the classes and "IBU at five iterations: ρ<0 at both truths", as the paper's tab:outcomes does. The
  Reading is now 9 lines, against 13.
- **Item 1: row 9's provenance.** The reading is unchanged. Three source comments no longer call it "the paper's
  section 6.2 sentence". It is the Supplement's account of the first test. The paper's shorter version is
  paper_body.tex:626: it has no staged-redesign clause, and it adds that the first test's checks led to the second
  test's like-for-like construction.
- **Item 2: test 9's design in its records' terms.** "As 10" is replaced. Index row 9 now prints its own statistics
  and levels, and S8.6's sentences 2–6 give its design. Test 10's band variants are not carried over: test 9 draws
  every group, and the record names no variants. The sources, with lines at this head, and the declaration at the
  sha make_values pins (50d9e883):
  - the two tunes, every group drawn, the nominal-simulation unfold and the covariance remade at each tune:
    FD-1B-STAGED-DECLARATION.md:66-69, carrying DECISION-20261101-joseph-1b-staged-method-coverage.md:39-44;
  - 300 per truth: :236 (key fd1b-ntoys);
  - the groups, with the MC and template Poisson streams: :186-193;
  - the statistics: :345 (per cell) and :353 (joint, χ² ≤ F⁻¹(P₀));
  - the levels, 0.025/16 per cell and 0.025 jointly: :399-400. They are keyed as fd1b-alpha, read from that table by
    make_values_fived16.py's supp_literal_values() and asserted equal at both places.
- **Item 3: the plug-in truth.** The declaration made it optional (:178, sec. 6). FD-1B-STAGED-BINDING-3.md:52-53
  bound the no-plug-in path, G18 and AR23 only, with the plug-in deferred. The question became moot when stage 1
  ended (OUTCOME-20261106-1b-stage1-receipt-stop.md:120-121; draws 600-899 were declared, :45-49). So test 9 ran at
  the two tunes, which agrees with S8.6's opening. The old S11's "and a plug-in truth" is corrected to "A plug-in truth
  was declared as an option and was not included".
- `meaning-read-3.txt`: the codex-school meaning read of this round, with the record excerpts
  (`meaning-read-3-records.txt`).
