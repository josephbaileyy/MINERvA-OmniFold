# r22 Step 3, the note round on the reviewed protected gaps: plan and adoption rule

**Under** [DECISION-20261030-joseph-adopt-openai-review.md](../../../../../DECISION-20261030-joseph-adopt-openai-review.md)
(#534): the independent review's ALLOW and ALLOW-NARROW gaps enter the round after Step 2's note round was measured.
The director started the round on 2026-10-30, after #561. The method, the adoption rule and the stopping rule are
those of [STEP2-PLAN.md](STEP2-PLAN.md) §3–§5, with the held-for-facts rule of
[STEP2-PAPER.md](STEP2-PAPER.md) §5, which the director set for later note rounds too. This file adds only what
Step 3 needs. It is committed before any text is written and before any score.

## 1. The gap list

`tools/step3_gaps.py` writes `step3/gaps.tsv` and `step3/held.tsv`.

**In scope: 38 note gaps.** These are the note rows of `openai-review/REVIEW.md` with verdict ALLOW or ALLOW-NARROW.
- **How each enters (#534 item 1):**
  - an ALLOW gap enters as gemini proposed;
  - an ALLOW-NARROW gap enters only in the reviewer's narrowed form (`effective_change`).
- **What each must still pass (#534 item 2):** the truth guardrail, the KEEP list, the fact ledger (`N:`, `R:` and
  `L:` probes) and agy's agreement read.
- **Spread:** 12 pieces. B01 3, B02 4, B03 2, B04 2, B05 4, B07 1, B09 4, B11 6, B12 3, B13 2, B14 4, B15 3.
- **By protection group:** A4 1, B1 14, B2 16, C1 2, C2 3, C9 2.

**One Joseph pair.** B01-g-07 is in the note's abstract, so it is A4.
- Its writer proposes a before/after pair in `step3/abstract-pairs.md` and does not edit `main_note.tex`.
- The director pins the pair and passes it to Joseph. `step3/check_ledger.py` allows `main_note.tex` to differ only by
  a pinned pair.
- B01 is judged without the pair unless Joseph approves it before B01's runs. A later approval gets its own check, as
  the paper's pairs did.

**Carried by quote (STEP2-PLAN.md §2).** B09-g-09's sentence is unchanged, but the note round's added table renumbered
it from "Table 15" to "Table 16". The quote is carried with that one substitution (`CARRY`). All 38 quotes then locate
exactly in the base pieces.

**Deferred to the paper's next round:** REVIEW.md's three paper gaps, paper-g-02, -g-03 and -g-06. The director has
put the next paper round after the figure report.

**Held: 29 sentences.** These are the Step 1 note gaps that neither Step 2 nor Step 3 carries: the review's KEEP
verdicts and the earlier protections.
- Each must still print exactly in its piece (`tools/check_held_note.py`, an exact `key()` match; its self-test plants
  a one-word mutation).
- No in-scope quote overlaps a held one, so no sentence is held for its facts in this round. All 29 are byte-held.

## 2. The base

- **Base commit:** origin/main at the round's start, `14a0415f`.
- **The note is unchanged since the note round.** The note sources there equal those that the note round adopted
  (#539, `f47b1b4a`). The only differences in `docs/analysis-note/` are the paper (#549, #561) and the generated
  `records_estimators.tex`.
- **The re-split matches.** The note was rebuilt and re-split with `tools/split_base.py`, and every one of the 15
  pieces is byte-identical to `step2/pieces/` (56,343 words).
- **So the base is unchanged:**
  - the pieces are `step2/pieces/`;
  - the P1N scores are the note round's adopted runs `step2/runs/P1N.Bxx.sol2.r{1,2,3}.txt`;
  - the note's piece mean is 3.222, against a target of 3.875.
- No base piece is re-scored.

## 3. Method (STEP2-PLAN.md §3)

1. **Writers, in parallel,** one per piece with a gap. Each works from `step3/WRITER-BRIEF.md` and its own
   `step3/briefs/<piece>.md`, which `tools/step3_briefs.py` writes.
2. **The fact ledger:** `step3/ledger-<piece>.md`, merged into `step3/ledger.md`, checked by `step3/check_ledger.py`.
   - The checker is `step2/check_ledger.py` run with this round's base, its ledger and its own pairs.
   - Its self-test on this base gives 12 caught and 2 silent.
3. **The held check:** `tools/check_held_note.py` on NEW's pieces.
4. **A two-direction review** by independent read-only agents.
5. **agy agreement** on every changed passage, with a planted control. `make_agy_pairs.py` tops up a short chunk with
   identity fillers.
6. **The build and all gates,** and the record-checks.yml steps with BASE=origin/main.
7. **Immediately before the runs,** NEW's pieces are cut from a build of the committed tree. A `key()` check that every
   changed sentence prints in its piece is recorded with them, since a copy built before a later edit voided a run set
   in the paper's pass 2.

## 4. Adoption, per piece (STEP2-PLAN.md §4, unchanged)

A piece is adopted if, and only if, all three hold:
- NEW beats the base in at least 3 of the 4 blind P2N runs: sol2 and gemini, both orders, with
  `note-rating/P2N.prompt.txt` unchanged;
- sol2 does not flip between orders;
- on 3 sol2 P1N runs, NEW's mean and its lowest run are each at least the base piece's.

A piece that fails keeps its base text. Pieces without a gap are not rewritten and keep their base scores. The adopted
pieces are assembled, rebuilt and re-gated.

## 5. Score and stopping rule (STEP2-PLAN.md §5)

- **The score:** the note's sol2 P1N piece mean over all 15 pieces, with an unchanged piece keeping its base runs.
- **Movement:** a rise above the previous round's mean, which is 3.222.
- **The count:** the note round of Step 2 moved, from 3.122 to 3.222. So this is the note's first round counted after
  a movement.
- **Stop:** at 3.875, or after three rounds without movement.
