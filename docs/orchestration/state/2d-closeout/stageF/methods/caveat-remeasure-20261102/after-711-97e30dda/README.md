# Caveat density after the cut-list round (#711): the paper at 97e30dda (2026-11-03)

**Asked for by** the director: one full re-measure of #711's final head against 58fa0b89, with:
- the per-move attribution against the cut list's expected 77 → 53;
- the effect of the second PRD-referee read's edits E1–E3, including whether IV C's "of unknown cause (Sec. IV A)"
  is coded as a repeat.

**Done by** the limitations-catalog session, by `remeasure.py` and one fresh coder under the committed prompt
(`../CODER-PROMPT.md`), read-only on the paper.

**CITABLE FOR:**
- the paper's caveat measures at 97e30dda, by the 10-25 caveat study's procedure;
- which moves a fresh coder counts as merged.

**NOT CITABLE FOR:**
- a change smaller than the coder spread, about ±25% (`../../caveat-study/REPORT.md` §2.4);
- the note, which was not re-coded.

## 0. A blinding defect, found here and fixed in `remeasure.py`

- **The defect.** In 97e30dda's two-column layout, pdftotext prints VI A items 3 and 2 after "ACKNOWLEDGMENTS" and
  "DATA AVAILABILITY"; item 2 lands among the reference entries. The 10-25 study's `blindcount.py` drops everything
  from the acknowledgments to the end of the references, so the measured text lost two Limitations paragraphs.
- **How it was found.** The first coder, on that text, reported it "truncated", and that was correct. Its inventory
  is discarded. For the record, it gave 7,625 words, 117 statements, 73 distinct and 9.57 per 1k.
- **The fix.**
  - After blinding, every item of `paper_body.tex`'s Limitations enumerate must appear as a numbered line ("n. "
    followed by the item's opening words, which stop at the first value or reference macro).
  - A displaced item is restored from the raw text, up to the next blank line, reference entry, heading or numbered
    item.
  - The run fails if an item is still missing.
  - The restored text is counted by `blindcount.py`'s own word rule. The summary records the restored items.
- **Tests.** The self-test covers three cases: an item restored when displaced; an item left alone when present,
  including the false match on "four of the sixteen cells" from the list's own introduction; and a run that fails when
  an item is lost.
- **The baselines stand.** On 58fa0b89 and 16cd55ca the fix restores nothing and leaves the blinded texts byte for
  byte unchanged.

## 1. Result

| paper at | words | statements | distinct | distinct /1k | statements per caveat |
|---|---|---|---|---|---|
| 58fa0b89 (before the round) | 8,080 | 145 | 77 | 9.53 | 1.88 |
| **97e30dda (after; Limitations items 2 and 3 restored)** | **7,752** | 136 | **77** | **9.93** | 1.77 |
| expected after the moves made (cut list) | | | 53 | | |

By kind, distinct caveats at 58fa0b89 and at 97e30dda:
- (a) 4 and 5;
- (b) 3 and 3;
- (c) 44 and 41;
- (d) 22 and 24;
- (e) 4 and 4.

**The round did not lower the distinct count a fresh coder finds.**
- Distinct caveats per 1k rose by 4%, because the words fell by 328 while the count stayed at 77. That is inside the
  coder spread.
- At the text level, 22 of the 58fa0b89 caveats lost every verbatim statement and 16 appeared with new text, mostly
  rewordings of the merged facts. That is about −6, also inside the spread.

## 2. Per move (`move-check.json`, `../cutlist/move_check.py`)

Each new statement is assigned to the move whose proposal or old sentences share its longest verbatim token run (at
least 6 tokens and half the statement). A merge "holds" if a fresh coder counts its content as one caveat, and an M
move holds if none remains.

| move | the cut list expected | a fresh coder counts | the new labels |
|---|---|---|---|
| MV01, run periods | 1 | 5 | added after seeing differences (b and e), size poorly determined, consistency check by construction, unknown cause |
| MV02, coverage | 1 | 6 | interval coverage not validated, claims limited in scope, coverage test stopped at a gate (c and e), 2D covariance not validated, earlier 2D band undercovered |
| MV03, 3D/4D values | 1 | 2 | the same label under (c) and (d) |
| MV04, envelope | 1 | 2 | precision target not met; envelope a diagnostic, not an interval. A third assignment, regularization bias, is a heuristic misfire: that is C20 |
| MV07 and MV07F, hydrogen samples | 1 | 3 | hydrogen sample quality, post hoc check of the B3 premise, internal check name. MV07F's two assignments (low stability, Tune v1) are misfires; the legend tokens are gone |
| MV08, background | 1 | 3 | purity closure bias, refined residual, treatment dependence |
| MV10, χ² sensitivity | 1 | 2 | χ² depends on flux correlations; bands are not intervals |
| MV06 (into C_model's definition) | 0 | 0 | holds |
| MV13, MV14, MV16 (to the note) | 0 | 0 | hold |
| MV15, IV G | 0 | 1 | IV G was reconciled, not moved (the round's second pass). The rounding instability prints, as three statements under one label |

**What this shows, and a correction to the cut list.**
- The cut list (`../cutlist/README.md`) assumed a merged statement would be coded as one distinct caveat. **That
  assumption is false for this coder.**
- The study's distinct unit is (kind, issue label), with one statement per sentence and kind. A merged paragraph
  still holds several sentences, and a coder gives each fact its own label. A label can also be split across two
  kinds: six labels at 97e30dda, as at 58fa0b89.
- So merging lowers statements and words, not the distinct count.
- The moves that hold are the ones that remove facts from the paper: MV06, MV13, MV14 and MV16, and the legend
  tokens of MV07F.
- My cut list's "77 → 44 / 53" predictions for the merges overstated what the metric can show.

## 3. E1–E3

- **E1 (IV C, the 2D step).** The sentence "In the two-dimensional result, data from different run periods are not
  mutually consistent … of unknown cause (Sec. IV A)" is coded under IV A's label, "run-period inconsistency of
  unknown cause". **It is a repeat, not a new distinct caveat.** Its clause "passes its own consistency check by
  construction" has its own label, but that fact was already a caveat at 58fa0b89 (C37), so it is not new either.
- **E2 (VI A drops a restated sentence).** No label is lost or gained. One fewer statement.
- **E3 (IV G in two).** Three statements under one label, "instability under input rounding". **One distinct caveat;
  a statement is added, not a caveat.**

## 4. Reproduce

    python3 -I ../remeasure.py --repo <checkout at 97e30dda> --work <scratch> --inv after-711-97e30dda/inv

This exits 0. `inv/CODED-ON.sha256` pins the corrected blinded text (`2c881c60…`).

    python3 -I ../cutlist/move_check.py ../after-58fa0b89/inv/ours-paper.tsv <58fa0b89 blind> \
        after-711-97e30dda/inv/ours-paper.tsv <97e30dda blind> out.json \
        --moves MV01,MV02,MV03,MV04,MV06,MV07,MV07F,MV08,MV10,MV13,MV14,MV15,MV16
