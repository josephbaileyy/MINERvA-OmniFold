# Table S1's template composition (C-BKG-2): the PRD-referee read and the meaning read (2026-11-12)

Rows: `pairs.tsv` (base 2a2af2417).

**PRD-referee read** (an independent subagent, no tools, facts only): **ACCEPT.**
- "10 %" is the right precision: the ±1 mm vertex-position sensitivity (2.5 % of the weight) makes the first decimal
  unstable.
- Neither the ±1 mm figure nor the 7.2 % other-flavour share needs printing. The template is subtracted whole, so the
  composition is descriptive.
- The neighbours (S1 :26, S4 :224 and the out-of-phase-space row) are consistent with it.
- Optional, adopted: split the sentence, so that "full sample" does not carry over to the 10 %, and say "true vertex":
  "Composition measured on playlist 1A only: about 10 % (weighted) is out-of-phase-space signal; the rest is genuine
  background, mostly ν_μ charged-current events with a true vertex outside the fiducial volume".

**Meaning read** (an independent subagent, read-only, given the records): **OK on all three checks.**
- The value and its population match cbkg2_summary.json: weighted, 1A, the passing rows in the grid, the same
  denominator as the 2.91 %.
- "The rest genuine, mostly out-of-fiducial ν_μ CC" holds: 82.4 % of the template is 92 % of the genuine part.
- The neighbours are consistent.
- Notes:
  - **Convention:** MAT's code puts the fiducial cuts in phaseSpace (runEventLoopOmniFold.cpp:1716-1720), whereas S1
    :26 counts out-of-fiducial events as genuine background. The row follows S1. Recorded in RESPONSE.md for a referee
    question.
  - **Provenance:** mat_source.json holds the MAT excerpts only; the event-loop link rests on the README and the
    repo's .cpp.
  - **Comment pointer:** the :31 comment now routes the template row to cbkg2 as well.
