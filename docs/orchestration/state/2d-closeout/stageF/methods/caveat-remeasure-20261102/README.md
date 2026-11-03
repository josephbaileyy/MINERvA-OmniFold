# Caveat density re-measured on current main (2026-11-02)

**Asked for by** the director (paper-tighten lane), under `DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md`
item 4 and Joseph's readiness gate. It is the baseline the gate re-measures after each paper round.

**Done by** the limitations-catalog session. The work was read-only on the paper and note sources. The only model use
was three in-session Claude subagents acting as coders. Their routing was verified: `CLAUDE_CONFIG_DIR` is
`~/.claude-school`.

**CITABLE FOR:**
- the 10-25 caveat study's measures (`../caveat-study/`), recomputed for the paper and the note as built from main
  `108040f8`, by that study's own procedure and code;
- the before point for #695. The after point will be added when #695 merges.

**NOT CITABLE FOR:**
- any physics claim;
- the genre as a whole (the study's own limit, `../caveat-study/REPORT.md` §8);
- a change smaller than the coder spread. One coder per document reproduces a row count to about ±25%
  (`../caveat-study/REPORT.md` §2.4), and every number below carries that spread.

## Result at main `108040f8`

| document | words (blinded) | distinct caveats /1k | statements per caveat | statements /1k | negation word | assigned |
|---|---|---|---|---|---|---|
| paper | 7,982 | **10.52** (84) | **1.76** | 18.54 (148) | 45% | 11% |
| note | 58,491 | **7.61** (445) | **1.97** | 14.98 (876) | 50% | 4% |
| *10-25 paper (r17)* | 8,785 | 10.02 | 2.28 | 22.88 | 35% | 8% |
| *10-25 note (`fe92211c`)* | 53,018 | 8.41 | 2.17 | 18.24 | 50% | 3% |
| *P range (6 PRD papers)* | 7,703–11,922 | 1.38–4.54 | 1.60–2.29 (median 2.0) | 2.38–7.76 | 6–30% | 0–14% |
| *N range (3 long documents)* | 30,678–35,620 | 1.55–2.51 | 1.38–1.91 | 2.13–4.79 | 17–26% | 0–28% |

Comparator rows are the study's committed `../caveat-study/tables/rates.md`, unchanged. By kind per 1k (paper; note):
- (a) 0.88; 0.74;
- (b) 0.88; 0.72;
- (c) 10.77; 8.82;
- (d) 5.51; 4.00;
- (e) 0.50; 0.70.

The full tables are `tables/rates.md` and `tables/placement.md`, in the study's format, with the run summary in
`tables/summary.json`.

**What it shows:**
- **Distinct-caveat density is unchanged within the coder spread**: paper +5%, note −10%.
- **Restatement has fallen.**
  - The paper's statements per caveat went from 2.28 to 1.76, now below the PRD median of 2.0.
  - The note's went from 2.17 to 1.97, still above the long-document range.
- **The remaining gap is the number of distinct caveats.** The paper has 2.3 times the top of set P; the note has 3
  times the top of set N. This is the study's finding R-P9 and R-N7 again.
- **Cutting a restatement cannot close that gap.** It removes words and no caveat, so distinct caveats per 1k rises
  slightly. It lowers statements per caveat and statements per 1k only.

**A separate, mechanical measure: old-quote survival. This is NOT density.**
- Of the 207 coded rows of the r17 paper inventory, 29 still verify verbatim against today's text (28 after the
  study's one-statement-per-sentence merge) and 178 do not.
- Of the 967 rows of the `fe92211c` note inventory, 413 still verify and 554 do not.
- It sees removals and rewording only. A caveat added since is invisible to it.

## Method

1. **Build.** `main_note`, then `main_paper`, from `docs/analysis-note/` with `latexmk -g`, with a second pass if
   the log reports unresolved references. The paper's `N-` references resolve through `main_note.aux` (xr), so the
   note is built first.
2. **Blind.** The study's own `tools/blindcount.py` for the paper, with the abstract's first line as its start, and
   its own `tools/blind_note.py` for the note. The note is split at "Guide to the appendices" into body and
   appendices, as the study coded it.
3. **Code.** One Claude subagent per part (paper, note body, note appendices) under the study's unchanged
   `CODEBOOK.md`, with the prompt in `CODER-PROMPT.md`.
   - All 1,029 quotes verified (148 + 630 + 251).
   - The study's one-statement-per-sentence rule merged 5 note rows (881 → 876).
4. **Tally.** The study's `tools/tally.py`, imported unchanged, with its `WORDS`, `SETS`, `H` and `T` pointed at this
   run.

**Inputs pinned.** `inv/CODED-ON.sha256` holds the sha256 of each blinded text the inventories were coded on. The
blinded texts themselves are not committed, as in the study. The coders read a copy of the note body that differed
from the pinned one only by one trailing blank line, which leaves the word content identical.

## Re-measuring (one command)

    python3 -I docs/orchestration/state/2d-closeout/stageF/methods/caveat-remeasure-20261102/remeasure.py --work <scratch dir>

It builds, blinds, tallies, prints the density next to the 10-25 baseline and the comparator ranges, runs the survival
measure, and writes `tables/`.

**The stale-coding guard.** If a document's blinded text differs from the one its inventory was coded on, its density
is printed as STALE and the run **exits 3**. A stale inventory counts only the coded caveats still present, and new
caveats are invisible to it.

**After a paper round:**
1. Re-code the paper (one subagent, `CODER-PROMPT.md`) into `inv/ours-paper.tsv`.
2. Run with `--record-coded ours-paper` (only the re-coded document's hash is recorded).

Coding is a judgment, so it is the one step the command cannot do. `--no-build` reuses `WORK/build/*.pdf`, and
`--self-test` checks the abstract-start detection, the study's own quote self-test, and the issue counting.

## Files

- `remeasure.py`: the command;
- `CODER-PROMPT.md`: the coders' prompts;
- `inv/ours-paper.tsv`, `inv/ours-note-body.tsv`, `inv/ours-note-app.tsv`: the inventories, in the study's columns;
- `inv/CODED-ON.sha256`: the blinded texts they were coded on;
- `tables/`: the outputs of the run at `108040f8`.
