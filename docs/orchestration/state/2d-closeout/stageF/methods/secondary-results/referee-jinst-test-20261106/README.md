# The JINST venue test, 2026-11-06

**Asked for by** Joseph (`DECISION-20261106-joseph-diagnoses-jinst-corrections.md`, item 2): the same blind procedure
on the current methods draft, with the referee addressed to JINST instead of PRD.

## What was read

**The draft:** the same as round 2, `draft/methods-framing-20261106` at `0de103f7`. Its rater copy is
`../referee-methods-round2-20261106/manuscript-methods-r2.blind.txt` (10,280 words), and it isn't duplicated here.

**The prompt:** `referee-prompt-jinst.txt` (sha256 `fa84ae14…`). It is `referee-prompt-neutral.txt` (`b67be0e8…`) with
"Physical Review D" changed to "the Journal of Instrumentation (JINST)" and each "PRD" changed to "JINST". Nothing else
differs.

**Referees:**
- Sonnet as read-only subagents. Their transcripts show only Reads of their two files, with the paper read in chunks.
- Gemini via agy (`gemini-3.8-flash-high`, `--sandbox`), from an empty directory, with the round-1 preamble
  (`gemini-run-jinst.sh`). Both reads succeeded on the first attempt.

## Scores

| draft `0de103f7` | Sonnet | Gemini | mean | recommendations |
|---|---|---|---|---|
| addressed to JINST | 4, 4 | 5, 5 | **4.5** | all four major revision |
| addressed to PRD (round 2) | 3, 4 | 3, 3 | 3.25 | Sonnet: reject in present form, and major revision; Gemini: reject, and reject |

**What the numbers show:**
- Addressing the draft to JINST raises the mean by about 1.25. Gemini moves from reject to major revision.
- The reports still ask for the same diagnoses as the PRD round:
  - the rounding instability's mechanism and an ensemble-averaged estimator;
  - the coverage pre-check's cause;
  - the cause of the prior retention;
  - a binned-unfolding control for the 2D shape difference and for the run-period step;
  - a self-contained paper.
- Both Sonnet reads say JINST is in scope for a diagnosed negative result.

**CITABLE FOR:** these referees' reports on the round-2 rater copy, addressed to JINST, and the scores they gave.

**NOT CITABLE FOR:** any physics claim, any venue decision, or approval of any wording.
