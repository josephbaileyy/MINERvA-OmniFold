# r22 Step 3, the note round on the reviewed protected gaps: report (2026-10-31)

The round followed [STEP3-PLAN.md](../STEP3-PLAN.md), with STEP2-PLAN.md's method, adoption rule and stopping rule.
Its gaps are the 38 note gaps that the independent review allowed (#534).

**Result:**
- **Adopted:** 7 of the 12 pieces, under the rule committed before any score (§4).
- **Not adopted:** B01, which carried Joseph's abstract pair, so the pair is not adopted either.
- **Score:** the note's sol2 P1N piece mean rose from 3.222 to 3.278, against a target of 3.875. Under the stopping
  rule (§5), that rise is movement.

Nothing is submitted, deposited or tagged. The paper is unchanged in this round.

## Raters and accounts

- **sol** (gpt-6.1-sol) ran on **codex-school**, with `run_x.sh` key `sol`. Each run's key is in `runs/status.tsv`,
  and all 60 runs give `key=sol`.
  - codex-school2 reported its usage limit until 2026-11-04.
  - The director moved sol to codex-school on 2026-10-30. The director confirmed it was usable on 2026-10-31
    (DECISION-20261031-joseph-rater-account-figures-chi2-consult.md, #574).
  - The 60 runs were made one at a time, with nothing else on the account (`step2_runs.sh` with `RATERS=sol2 JOBS=1`).
  - The output names keep "sol2", the rater's name in the rule.
- **gemini** (gemini-3.8-flash-high) ran through agy.
- **Attempts set aside, none of them scored:**
  - **2026-10-30:** all 60 sol runs failed, because codex-school was out of credits
    (`runs/status-20261030.tsv`). The figure study's image calls on the same account had drained it.
  - **B01's first two gemini runs** judged B01 without the abstract pair. Joseph approved the pair before B01's sol
    runs, so under STEP3-PLAN §1 B01 is judged with it. Its two gemini runs were repeated on the re-cut piece.
  - **Two sol calls** were made with the piece ids passed as one word, so they ran as id B01 with order "B02".
    `step2_runs.sh` now refuses such an id (`bb71f57b`).

## The pieces measured

NEW's pieces were cut from a build of the committed tree `36ed8ea1`, which adds Joseph's approved pair B01-g-07 to the
rewrite (`new/PROOF.txt`).
- Only B01 differs from the cut of `928fec6b`, and only by the pair.
- The key proof gives 20 of 20 changed phrases printed. The held check gives 29 of 29 exact.
- The base pieces are `../step2/pieces/`. The base P1N runs are the note round's adopted
  `../step2/runs/P1N.<id>.sol2.r{1,2,3}.txt` (STEP3-PLAN §2).

## Adoption (§4)

`tools/adopt_step2.py` writes [runs/adoption.tsv](runs/adoption.tsv) with
`--base-runs step2/runs --base-pattern "P1N.{i}.sol2.r{k}.txt"`.
- The rater outputs are committed verbatim as `runs/<P2N|P1N>.<id>.<model>.<AB|BA|rN>.txt`.
- `adoption.tsv`, recomputed from copies renamed to `.md`, is byte-identical.

| piece | P2N NEW wins (of 4) | sol2 same in both orders | P1N new | P1N base | words base → new | adopted |
|---|---|---|---|---|---|---|
| B01 | 1 | yes (OLD) | 3.5, 3.5, 3.5 | 3.5, 3.5, 3.5 | 1835 → 1837 | no |
| B02 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 4799 → 4779 | YES |
| B03 | 4 | yes | 3.5, 3.5, 3.0 | 3.0, 3.0, 3.0 | 4184 → 4186 | YES |
| B04 | 3 | no | 3.5, 3.0, 3.5 | 3.5, 3.5, 3.5 | 2977 → 2981 | no |
| B05 | 4 | yes | 3.5, 3.5, 3.5 | 3.5, 3.5, 3.5 | 3277 → 3279 | YES |
| B07 | 3 | no | 3.5, 4.0, 3.5 | 4.0, 4.0, 3.5 | 2506 → 2503 | no |
| B09 | 4 | yes | 3.5, 3.5, 3.5 | 3.5, 3.5, 3.0 | 4352 → 4346 | YES |
| B11 | 4 | yes | 3.5, 3.5, 3.5 | 3.5, 3.5, 3.0 | 1660 → 1658 | YES |
| B12 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 7619 → 7592 | YES |
| B13 | 3 | no | 3.0, 3.0, 3.0 | 3.0, 3.0, 3.0 | 5688 → 5694 | no |
| B14 | 4 | yes | 3.0, 3.5, 3.0 | 3.0, 3.0, 3.0 | 999 → 998 | YES |
| B15 | 4 | yes | 3.0, 3.0, 3.0 | 3.0, 3.5, 3.0 | 2445 → 2442 | no |

**Why each failed:**
- **B01:** sol preferred the base in both orders, and gemini split.
- **B04 and B07:** sol flipped between orders, and the P1N mean fell.
- **B13:** sol flipped.
- **B15:** the P1N mean fell, from 3.17 to 3.00.

**Pairwise:** NEW won 42 of 48 runs, sol 19 of 24 and gemini 23 of 24. Every run answered on the first attempt.
- **sol's STRENGTH** was 1 (slight) in all 24 runs.
- **gemini's STRENGTH** was 1 in 3 runs and 2 in 21.

The changes in this round are small, a few words per gap, and sol rates every difference as slight. So a 3-of-4
decision here rests on preferences that sol itself calls slight.

## The adopted note

The five pieces that were not adopted keep their base text. Their files are restored to `14a0415f`:
- B01: `main_note.tex` and `sec_execsummary.tex`;
- B04: `sec_validation.tex`;
- B07: `sec_eavailw.tex`;
- B13: `app_statmethods_nd.tex`;
- B15: `app_release.tex`.

The adopted note is `f13912b6`.
- **`app_codebase.tex`'s `\clearpage`** stays. It is layout only and keeps the coverage figure (`fig:coverage-5d-paper`)
  ahead of the References. In the adopted build the figure is on p. 121 and the References start on p. 122.
- **Pieces:** [adopted/PROOF.txt](adopted/PROOF.txt) cuts them from a build of `f13912b6`.
  - Each adopted or gap-free piece is byte-identical to NEW's.
  - B01 is byte-identical to the base.
  - B07 and B15 equal the base after masking the table numbers that B03's new table shifts.
  - B13 holds the same words in another order, because pdftotext emits a float elsewhere.
  - B04 also differs only by page layout: "pseudo-data" is hyphenated across page 26, and the page number prints inside
    the word.
  - The held check gives 29 of 29 exact.
- **Fact ledger:** `step3/check_ledger.py` now checks only the adopted pieces' rows, from `runs/adoption.tsv`. A piece
  that was not adopted has no changed sentence, and its rows assert NEW's text.
  - Adopted: 45 rows, 127 probes, 0 failures. With the n4 frozen sentences checked, there are still 0 failures. The
    self-test passes.
  - `--all-pieces` checks NEW as before: 64 rows, 183 probes, 0 failures, self-test PASS on NEW's files.
- **Registry:** the round's re-pins are all in adopted files and stand: `app_guide.tex:8` (B12) and
  `sec_method.tex:48`, `:79` (B02). `check_registry.py` passes, and the regenerated records are unchanged.
- **The records-move ledger.** B12-g-04 turned the glossary's J28 row into a sentence. So row L-thin-C02's `N:` probe
  of `records-move-ledger.md` named text that no longer printed, and the records-move self-test caught it in the CI
  steps. The probe now names the new sentence, and the row is marked "probe updated for r22 Step 3", as Step 2 marked
  its own.
- **The CI steps** (`record-checks.yml`, run locally after merging origin/main) pass: 37 steps, 0 failed.

## Score and the stopping rule (§5)

- **The score.** The sol2 P1N piece mean over all 15 pieces is **3.222 → 3.278**. A piece that was not adopted keeps
  its base runs. The rise comes from four pieces:
  - B03, 3.00 → 3.33;
  - B09 and B11, each 3.33 → 3.50;
  - B14, 3.00 → 3.17.
- **What it means.** The rise is movement, so the count of rounds without movement stays at zero. The target is 3.875.

## For the director

- **Joseph's abstract pair B01-g-07 is not adopted.** Its decision (#571) ties it to B01, and B01 failed. Nothing about
  the pair changes.
- **CLAIMS-20261005 L4** (`docs/publication/CLAIMS-20261005-claim-to-evidence.md:145`) says that the note records the
  seed provenance: "`random_state=None`, from the launcher and driver revision; the run log was not found".
  - B02 is adopted. So the note now says "Its seed was not fixed, and its run log was not found".
  - The reason moved to `uncertainty-preparation-20261008/a/pairings.tsv` P01, by the director's ruling on B02-g-01.
  - So L4 points partly at moved wording. It is left alone, as ruled.
- **B11-g-10 was skipped.** The sentence needed a change in `sec_method.tex`, outside B11's files. It prints unchanged
  (review B07–B11).
- **An older inaccuracy, not from this round.** Both the base and the note call the third truth hadronic diagnostic the
  "leading-hadron angle". At `6420ee7e` the stored branch is `MC_hadangle`, filled by
  `CVUniverse::GetHadronAngleTrue()`
  (`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:269-282`). That is the polar angle of the summed hadronic
  momentum. B07 was not adopted, so the base wording prints. It is a truth fix for the next note round, beside the Fig. 13
  and Fig. 25 captions.
- **The next paper round** is the third, and the last unless P1 moves. It carries:
  - the deferred paper gaps paper-g-02, -g-03 and -g-06;
  - the χ² tables in Option B (#581).
