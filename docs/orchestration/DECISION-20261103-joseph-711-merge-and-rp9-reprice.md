# DECISION 2026-11-03 — Joseph: merge the cut-list round (#711); re-price R-P9 from the measured 77

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The round.** #711 is the paper lane's cut-list round, made under `DECISION-20261102-joseph-caveat-cut-list.md`. Its
final head is `97e30dda`. It went through two PRD-referee reads, both committed beside its REPORT:
- the read of the moves;
- a second read of the rewritten text, which led to the director's edits E1–E3.

Three suggestions from the second read were not adopted, and the REPORT records them for Joseph:
- excising MV13's pointer;
- pruning Table I's GiBUU footnote;
- the C_PL,5D audit clause.

The ledger has 97 probes with 0 failures. Local CI passed 38 of 38.

**The re-measure.** `caveat-remeasure-20261102/after-711-97e30dda/` (#716) is one full fresh coding, at ±25%:
- **at 58fa0b89:** 8,080 words, 77 distinct caveats, 9.53 per 1k;
- **at 97e30dda:** 7,752 words, 77 distinct, 9.93 per 1k.

The cut list expected 53. A fresh coder counts each fact of a merged paragraph as its own distinct caveat:
- MV01 codes as 5;
- MV02 as 6.

Only the moves that take facts out of the paper hold: MV06, MV13, MV14, MV16, and MV07F's legend tokens.
limitations-catalog corrected the cut list's assumption in `cutlist/README.md`. The cut list's predictions of 44 and
49, and RP9.md's starting point of 44, overstate what this metric shows.

## Joseph's answers, verbatim

Asked whether #711 should be merged, given that it improves the text but does not lower the distinct caveat count:

> Merge now (Recommended)

sha256 of the text plus a final newline begins `aa3b7338ca685370`.

Asked what comes next for the ≤ 6 per 1k density target, with merges shown not to move the caveat count:

> Re-price R-P9 from 77 (Recommended)

sha256 of the text plus a final newline begins `021a4fdd29b7e9e5`.

## What is decided

1. **#711 is merged at `97e30dda`** through the CI-gated merge, and the Overleaf standalone is re-synced afterwards
   under the sync record's procedure.
   - The three referee suggestions not adopted stay open, and are not made by this decision.
2. **limitations-catalog re-prices R-P9**, moving whole secondary results to the note, starting from the measured 77
   at `97e30dda`. For each candidate result the price gives:
   - which facts leave the paper;
   - the measured or coded change in distinct caveats and words;
   - the pointer and note-prints-it probe each move needs (`DECISION-20261029`).

   The price comes back to Joseph with a PRD-referee read before anything moves. Nothing in the paper changes under
   this item.
3. **The density gate** (`DECISION-20261102-joseph-caveat-cut-list.md`, the ≤ 6 section) **is unchanged.**

Nothing is submitted, deposited or tagged.
