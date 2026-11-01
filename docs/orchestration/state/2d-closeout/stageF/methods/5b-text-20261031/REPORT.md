# The 5B text round: report (2026-10-31)

**Under:**
- `DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md` item 2: the block is added to the reported covariance,
  and every product is published with and without it;
- `DECISION-20261031-joseph-j1-j2-and-protections-split.md`: J1(a), J2(a), the referee's corrections and the
  protections split;
- `PROPOSAL-20261031-5b-with-without.md`, items 0 and 3, as the director accepted them;
- the director's rulings of 2026-10-31: the guard first, no P2, one P1 ×3 non-regression, and #607's item-(v)
  disclosure.

**Result.** In the paper and the note, the reported covariance of the sixteen-cell result is now
C_total + C_resp + C_PL,5D, and every 16-cell result is given with and without the block. The text is checked. **The two
abstracts wait for Joseph:** under A4 he approves each revised abstract as a whole. Nothing is submitted, deposited or
tagged.

## What changed

**The values** (`make_values_fived16.py`):
- the headline keys are pinned to the with-block readouts (`fd/with-cpl/`), and every matrix-dependent key is also
  written without the block, under the suffix `-nopl`;
- a key outside the matrix-dependent families that differs between the two arms stops the run;
- new keys for:
  - the block's effect: the median rise 7.8 %, the median per-cell rise 4.8 %, R04's 14.1 %, the shares;
  - the falls of χ²: 3.6–30.5 % total and 7.3–39.5 % shape-only;
  - the block's label: the 68 % interval 0.73–2.56, the noise-dominated cells, rank 2;
  - declaration (v): 50 replicas and n_eff 19.

**The guard first:**
- the re-pin alone made `--check` fail on all six old listed-truth sentences (`GUARD-FIRES-ON-OLD-PROSE.txt`);
- the guard now checks nine sentences against both arms, with four rule kinds (keys, without, both, count);
- the arm-swap world fixture fails exactly the six sentences that tell the arms apart;
- the new two-way test found that the sentence splitter missed an anchor that opens its sentence. That is fixed;
- seven mutants, all killed (`GUARD-MUTANTS.txt`).

**The paper:**
- sec:cov16 names C_PL,5D and has a run-period paragraph: built from the period double ratios with no reference period,
  rank 2, not debiased, its size poorly determined (0.73–2.56); added after the differences were seen, following an
  audit with a stop condition fixed in advance; size and coverage not independently validated. The medians are printed
  three ways;
- one declaration-(v) paragraph covers every 16-cell χ² (#607 §6);
- J1(a): both listed-truth lists, with the criterion beside them and "the other 10 truths";
- J2(a): Table IV in two column groups, with ndf once per block and an amended caption, plus one sentence on the χ²
  falls;
- Table III, Fig. 4 and its caption are on the reported matrix.

**The note:**
- a new sec:fived16-pl: the construction, the audit (all four items; passing it establishes neither the block's size nor
  the absence of overlap), the label's caveats, and the inference, marked as one;
- the cells table, the fake-data table and Table 16 are given with and without the block;
- declaration (v) is given per block.

**The abstracts and executive summary:**
- they print the reported median, 7.86 %;
- both abstracts say "the estimator's bias exceeds the thresholds set against the reported uncertainty at a GiBUU-like
  truth and at a synthetic q3 tilt".

**Coupled files:**
- the Supplemental Material is regenerated on the reported matrix, with its sha256 pins re-pinned and the earlier pins
  recorded in the code;
- the with-block figures are installed (`b57cbb2c`, `980351ed`);
- `check_dead_containment.py` declares three digit coincidences, each verified at its source and tested in both
  directions:
  - 3.65: a pull, struck as 3.65 %;
  - 1.65: a pull, struck as 1.65 × 10⁻³⁸;
  - 6.86: a mode's σ in the modes figure, struck as the 2D per-bin median.

## Checks

| check | result |
|---|---|
| `make_values_fived16.py --check` and `--self-test` | PASS: 2273 values; 9 listed-truth sentences agree |
| `make_supplemental.py --check` and `--self-test` | PASS, with its independent side-CSV control on the with-block product's own covariance CSV |
| `build_all.sh` | PASS: all five PDFs |
| `test_build_all.py` | the same 23 failures as the base `ac8fb9ae3`, measured in a detached worktree. They are pre-existing: the harness copies `build_all.sh` without `make_values_fived16.py`. None is new |
| `reflow_tex.py --note --check` | PASS |
| the ledger (`check_ledger.py`) | 10 rows, 45 probes and 17 changed base sentences. **One failure, by design:** the two note-abstract pairs stay unpinned until Joseph approves (A4) |
| `check_held.py --fact-held` (`CHECK-HELD.txt`) | 3 held quotes changed. All three are decided changes: the paper abstract's fake-data sentence and its median (J1, #542; A4, for Joseph), and the body's "does not cover … GiBUU-like truths" sentence (J1(a)). The base gives 0 |
| Option B's number probe (`TABLE-MACROS.txt`) | the note's Table 16 PASS. The paper's Table IV PASSES on its own column; the full-page read fails only because pdftotext puts the next column's text on the table's lines |
| agy (`agy-triage.md`) | every flag is a declared change. **Its control caught 2 of 6 planted negations, so this read is weak** |
| the independent two-direction review (`review.md`) | 10 findings (1 High, 4 Medium, 5 Low), all fixed or dispositioned. R11's F1 sentence re-measured, and it holds |
| P1 ×3 non-regression (`p1/`; sol, codex-school, one call at a time, on the rater copy of `5da83a76d`) | 3, 3, 3: mean and min 3.0 ≥ 3.0 |
| the rater copy (`rater-copy/`) | holddiff VERDICT PASS. `fix_da_order.py` gained case 5: the new page flow put references [1]–[7] inside the acknowledgments, and blinding then dropped the data-availability section |

## For Joseph (through the director)

- **The two revised abstracts, each as a whole (A4).** The fake-data sentence uses "and" where the decision quotes "or".
  The review asked that it name what the thresholds are set against, so it now says "set against the reported
  uncertainty".
- **The with-block headline numbers in the abstracts:** 7.86 %; 105–224; GiBUU 45. Without the block they would be
  7.29 %, 109–272 and 58. The referee endorsed the with-block headline. Whether the abstract should mention the block is
  his to say.

## The abstracts, finalized (2026-11-01)

**Joseph's choice:** "astra's, minus exclusions"
(`DECISION-20261031-joseph-abstracts-astra-without-exclusions-line.md`, #632).
- **The text:** both abstracts are the astra consult's §2 drafts
  (`secondary-results/astra-consult-abstracts-coverage-20261031/answer.txt`), each without "These comparisons do not
  establish generator exclusions." That sentence stays in the body (`paper_body.tex` sec:limits).
- **Kept, as the director listed:**
  - the run-period clause, with no without-block number;
  - "predeclared" thresholds: FD-DIRECTOR-RULINGS.md §2, bound 2026-10-25 (`092702292`) before F0's report
    (`28c4870f4`), and reused unchanged by F0b and the with-block chain;
  - one coverage sentence, last.
- **Every number prints through `\fvval`:** 7.86 %, 105–224, 16, 45, and "eight", from a new `g-gibuu-ncells-word`
  key.
- **The guard's two abstract anchors** follow the new wording, and still require exactly one listed GiBUU truth and the
  q3 tilt.
- **The ledger:** the note's pair is the whole revised abstract plus its source comment. It is unpinned until Joseph
  approves; a dry run with the pins gives 0 failures.

**Checks, on the final text:**
- build PASS; values `--check` and self-test PASS; reflow PASS;
- the ledger: 10 rows, 48 probes, 0 failures apart from the unpinned pair, by design;
- `check_held` (`CHECK-HELD.txt`): four quotes flagged.
  - Three are the decided changes: the paper abstract's two sentences (#632, A4) and the body's J1(a) sentence.
  - The fourth, G1b:paper-g-14, is not a text change. The sentence is byte-identical; pdftotext broke it at its hyphen
    after the column reflowed, and `key()` does not fold the dropped hyphen.
- P1 ×3 (sol, on the rater copy of the final commit): 3, 3, 3, so the non-regression holds.

**The built abstracts,** as the PDFs print them, go to the director for Joseph's approval of each whole abstract.
#619 does not merge before he approves.

## Joseph's approval and the pins (2026-11-01)

- **Approved:** Joseph approved both whole abstracts exactly as built at `6ed1e5c91` ("Approve both (Recommended)").
  The director relayed it, rebuilt both PDFs at that head, and recorded the approval. The abstract sources are
  byte-identical at that head and at this one.
- **Pinned:** `ABSTRACT_PINS` holds the two pairs' `--pins` values: 5B-c `fd090d51b370d29a`, 5B-a `ccc3fecf293bf597`.
- **Main merged:** `origin/main` (`8fcc9e689`) is merged into the round, with no conflicts. The ledger's base is now
  `8fcc9e689`. Against `ac8fb9ae3`, the install round's five caption sentences (#631, under its own ledger) read as
  uncovered. Against `8fcc9e689`, the round's own 17 changed sentences remain, all covered.
- **A self-test fix in `r22/step2/check_ledger.py`:** the "undeclared abstract edit" plant replaced "We report a
  simultaneous measurement", which the approved note abstract no longer contains. So the plant left its input unchanged
  and could not fail. While the pairs were unpinned, the baseline's own failure hid this. The plant now adds text
  before `\end{abstract}`, and an assert requires it to change its input. Before and after, on this tree: the 5B
  wrapper's self-test goes from FAIL (that plant NOT CAUGHT) to PASS. The step3, step4 and step4-install wrappers print
  the same lines as before. On this tree their abstract plants fail as they did, because their base abstract no longer
  matches the note's, so their baselines already fail check 4. Each wrapper is valid at its own round's head.
