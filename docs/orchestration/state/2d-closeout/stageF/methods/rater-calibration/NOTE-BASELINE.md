# Analysis-note register baseline (P1N), 2026-10-21

This is the director's summary, saved from the agent's reply, because the harness refused the agent's own write.
The agent's raw outputs are in this directory.

**Inputs:**
- **The note:** the r12 build `main_note.pdf`, 136 pages, sha256 `c6fd1ebe…7c459c5b26`. It was split into 15 blinded
  pieces of 2,077–7,448 words each, 60,963 words in total.
- **The prompt:** `prompts/P1N.md`. It is P1 with only the framing changed, to a chapter of a long technical companion
  note. The rubric, scale and format are byte-identical to P1.
- **The runs:** 59, all through `run_x.sh`:
  - 2 sol runs and 1 Gemini run per note piece;
  - anchors: 2 sol runs and 1 Gemini run per piece;
  - the paper: 1 sol run per piece.

**Anchors.** Each was verified on its arXiv abs page, from the labelled journal-reference row.
- **T2K**, arXiv 1502.01550v2, Phys. Rev. D 91, 072010 (2015). Pieces AT1 (Sec. VI) and AT2 (Secs. VIII–IX).
- **ProtoDUNE-SP**, arXiv 2007.06722v4, JINST 15 (2020) P12004. Pieces AP1 (Sec. 4) and AP2 (Sec. 6).

**Scores** (sol mean over 2 runs, then Gemini):

| set | sol | Gemini |
|---|---|---|
| anchors: AT1, AT2, AP1, AP2 | 4.0, 4.0, 4.0, 3.5 → 3.875 | 4.0, 3.5, 3.0, 3.0 → 3.375 |
| paper r12, two pieces | 3.5, 3.5 | – |
| note, 15 pieces | 2.83 | 2.30 |
| note body, N01–N10 | 2.98 | 2.55 |
| note appendices, N11–N15 | 2.55 | 1.80 |

- **The gap.** The note is 1.04 below the anchors with sol (Welch z 7.2), and 1.08 below with Gemini.
- **Run-to-run sd** for sol is 0.16 (19 pairs).
- **Scale link.** P1N on chapter-sized pieces reads about 0.5 above P1 on the whole paper. The paper scores 3.0 on P1
  and 3.5 on P1N. Framing and splitting are confounded in that comparison.
- **Resolution.** sol gave 3.0 in both runs to 10 of the 15 pieces, so it has little resolution in that band.

**Worst pieces** (sol / Gemini):
- N15, App. J: 2.25 / 1.0;
- N13, Apps. D–G: 2.25 / 2.0;
- N14, Apps. H–I: 2.50 / 2.0;
- N08, §9: 2.75 / 2.0;
- N12, Apps. B–C: 2.75 / 2.0.

**Complaint types.** There are 135 quotes, all verified to occur in their pieces, from 78 passages. The agent's hand
labels give these counts:

| type | quotes | pieces |
|---|---|---|
| BOOK, internal record-keeping | 42 | 13 |
| HEDGE, stacked qualifiers | 38 | 12 |
| JARG, coined project terms | 34 | 12 |
| HIST, development history | 33 | 10 |
| CODE, software detail | 23 | 11 |
| META, editorial and meta-text | 22 | 10 |
| PROC, process narrative | 22 | 9 |
| DENSE, compressed sentences | 13 | 6 |

The anchors' complaints are informal wording and grammar slips. They have almost no bookkeeping or jargon.

**Recommended order for the note's register pass:**
1. Batch 0: a glossary, applied once across the note.
2. Then, worst first and the summaries last:
   1. App. J;
   2. Apps. D–I;
   3. §9 with Apps. B–C;
   4. §5 with App. A;
   5. §§2–4;
   6. §§6–8;
   7. §10;
   8. the abstract, executive summary, introduction and §§11–12.

**Targets** (sol, P1N, 2 runs): 3.5 for each batch, with 4.0 as a stretch, against the anchors' 3.875.

**Decision needed before batches 1 and 2.** Apps. G–J are records by design: struck values, commits and provenance
tags. They cannot be line-edited into journal register. The question is whether they stay as they are, are
shortened, or move to the repository. This is Joseph's call, and it was already pending as "App. J placement".

**What went wrong, and limits:**
- The agent stopped once on an API rate limit; no run was duplicated.
- The scheduler printed "ALL-DONE" too early. The agent caught it and waited on every output.
- The agent found a bug in `cal/tools/absparse.py`: it takes the first `jref` cell, which may be the report number.
  - The director re-checked all three paper-calibration anchors on their arXiv abs pages, from the labelled
    journal-reference rows: Phys. Rev. D 112, 012008 (2025); 101, 112007 (2020); 106, 036011 (2022).
  - All three are correct.
- Neither note anchor is an unfolding paper.
- The complaint types are the agent's labels, not rater output.
