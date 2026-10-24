# Qualifier density before and after register round r16

**Instrument:** the register study's density tool, run as its REPORT.md §3.1 states:
- `tex2prose.py` on `main_paper.tex`, with `paper_body.tex` expanded;
- `qcount.py table` and `strict_index.py` on that prose;
- `abstract_stats.py` on the abstract.

**Inputs.** The corpus prose is the study's twelve files, checked against `register-prd-study/INPUTS.sha256` (12 of
12 OK).
- **before:** origin/main 927f40bf. The prose sha256 is `b52aa139a492…`, the same as r15's after-review-fixes prose.
- **after:** this branch. The prose sha256 is `645f84dbbd35…`.

The corpus medians are the study's (REPORT.md §3.3). They are not recomputed, because `qcount.py table` treats every
document not named `ours` as corpus.

| measure (per 1,000 words unless marked) | before (927f40bf) | after (r16) | corpus median [min, max] |
|---|---|---|---|
| words / sentences | 6,603 / 258 | 6,609 / 261 | — |
| mean sentence length | 25.6 | 25.3 | 22.7 [19.1, 28.2] |
| Q (all markers) | 29.4 | 28.9 | 14.4 [7.1, 26.9] |
| Q excl. NEG | 18.2 | 18.0 | 10.3 [5.7, 21.5] |
| SCOPE | 9.5 | 9.4 | 3.7 [2.1, 6.0] |
| COND | 2.4 | 2.6 | 0.8 [0.3, 9.3] |
| STATUS | 3.8 | 3.8 | 0.2 [0.0, 0.6] |
| HEDGE | 0.8 | 0.8 | 1.9 [1.1, 4.0] |
| CONCESS | 1.7 | 1.5 | 2.5 [0.8, 5.3] |
| NEG | 11.2 | 10.9 | 4.1 [1.5, 5.4] |
| sentences with ≥ 2 markers | 19 % | 18 % | 5 % [2, 12] |
| sentences with a scope restriction | 25 % | 25 % | 10 % [6, 21] |
| pointer parentheticals | 1.4 | 1.4 | 0.2 [0.0, 1.3] |
| strict index | 12.4 | 12.3 | 2.6 [1.3, 4.2] |
| sentences with a strict marker | 28 % | 27 % | 5.5 % [3, 9] |
| abstract | 115 words, 5 markers | unchanged | 0–3 markers |

**The changed sentences.** The ten sentences that left hold 13 markers. The thirteen that replace them hold 10.
- **Out:** "under a [rule]", "although", "neither … nor", and two NEG in the old rerun sentence.
- **In:** one COND, "does not depend on", in the budget sentence. It states that the error bound does not depend on
  the stopping rule. It is a technical use, not a caveat.
- **Kept:** STATUS is unchanged at 25 markers. Its two "descriptive" uses are the KEEP-list adjective (E3) and the
  disclosure of what the design's reviewers saw.

**Reading.** The round's targets were register classes, not counts: internal bookkeeping, development history,
record words ("re-grade", "assessment seeds", "the rule's measure", "validity claim", "design record") and one
restated caveat. These are not in the lexicon, so the density barely moves.
- **Why the counts stay outside the corpus range:** the reasons are r15's (`r15/density.md`, "What holds the remaining
  excess"):
  - the Limitations list;
  - the KEEP-list qualifiers;
  - the two sentences that `check_sec4_receipts.py` binds;
  - technical uses that the lexicon counts.
- **No true scope or disclosure was deleted to move a number.** The one clause removed (the scan's "bounds neither")
  prints twice more in the paper and once in the note.
