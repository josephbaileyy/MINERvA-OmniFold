# DECISION 2026-10-30 (later) — Joseph: the two note-abstract pairs B01-s-04 and B01-s-10 are approved

**Recorded by** the paper-tighten lane, as director.

**What led to it.** `DECISION-20261030-joseph-r22-protected-gaps.md` item 1 allowed sol2's abstract gaps, provided each
came to Joseph as a pinned before/after pair before adoption. The paper rewrite lane pinned two pairs for the note
abstract:
- **B01-s-04,** pin `d2075a04421dcc5e`: the first sentence is split into three, with the same facts and numbers,
  going from 54 to 59 words;
- **B01-s-10,** pin `2b0420a3ab1e1432`: the χ² sentence is split, with the GiBUU comparison in its own sentence, going
  from 27 to 35 words. "the 8 cells its sample covers" is the note's own reason (Sec. 10: GiBUU has no events above
  E_ν = 20 GeV).

Each pin is `sha256(before + NUL + after)[:16]`, as `r22/step2/check_ledger.py` computes it. The director put each
AFTER text to Joseph in full.

Joseph's answer to each question, verbatim:

> Approve (Recommended)

sha256 of the text plus a final newline begins `b012841bf16cb4da` (the same text for both answers).

## What is decided

1. **Both pairs are approved,** exactly as pinned, for the note abstract (`main_note.tex`). The lane adds them to
   `ABSTRACT` and `ABSTRACT_PINS`, so that the note abstract may differ from the base by exactly these two pairs.
2. **They are adopted with the note round they belong to,** under its pre-committed adoption rule. If the round's piece
   B01 is not adopted, neither pair is.

## Not changed

- The paper's abstract and every number. Nothing is submitted, deposited or tagged.
