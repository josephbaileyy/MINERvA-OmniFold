# DECISION 2026-11-19 (b) — Joseph: no duplicates in the note

**Recorded by** director-helper-3, for the director, who relayed Joseph's words.

## What led to it

- **The restructure.** `DECISION-20261118-joseph-deep-restructure.md` (on main) moves history out of the body. Its item 3 states each limitation once, in §12.
- **The count.** The deterministic quality check (`docs/analysis-note/quality_checks.py`) still found repeats at draft 1acece939:
  - 51 duplicated passages (67 location pairs, about 1,020 words);
  - 20 table pairs that share numbers;
  - figures that draw the same data, Figs. 7, 9, 10 and 13.
- **The question.** The director proposed folding Fig. 13 into Fig. 7 and merging Figs. 9 and 10.

## Joseph's words, verbatim

2026-11-19, his reply to that proposal:

> yes lets go ahead, I really have no preference for if we put them in separate or a singular figure, I just don't want there to be duplicates

(`809a5c40a38882499275c132b55216babf2908dcf91325c7915649f3c56cd5df`, the sha256 of the text plus a final newline.)

## What is decided

1. **No duplicates in the note.** Each data series, number set, sentence and definition prints once, and other places point to it. The form, separate figures or combined, is the lanes' choice.
2. **When a repeat stays.** A repeat is kept only in two cases:
   - beside something new it is compared with;
   - as an intended copy with its reason recorded. These are the rule C and rule D caveats, and the abstract and executive-summary coverage statement of DECISION-20261116 item 32.
3. **The records document.** Its pointers and provenance sentences may be retargeted, or made historical, where removing a duplicate deletes their target. Struck and replacement values stay byte-identical.
4. **Glosses and definitions.** Each survives exactly once.

## Not decided here

- Any change of a value, a claim or a limitation.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - removing a duplicate from the note, with a pointer to the copy that stays;
  - retargeting a records-document pointer whose target such a removal deletes;
  - keeping a repeat for one of the reasons in item 2.
- **Not citable for:**
  - changing a value, a claim or a limitation;
  - removing the last copy of anything;
  - any paper wording.

Nothing is submitted, deposited or tagged.
