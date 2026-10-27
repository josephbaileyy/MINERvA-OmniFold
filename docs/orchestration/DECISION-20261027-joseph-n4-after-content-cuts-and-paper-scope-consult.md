# DECISION 2026-10-27 — Joseph: round 4 after the content cuts, merge repeats now, and an independent consult on the paper's scope

**Recorded by** the paper-tighten lane, as director.

**What led to it.** Note round n3 merged (PR #405, main `a24c7f2c`).
- **The score has stopped moving.** sol2's absolute P1N mean was 3.133, flat across n2 and n3, against a target of 3.5.
  The blind pairwise comparison still preferred the new text on 9 of 12 pieces.
- **The cost list** (`state/2d-closeout/stageF/methods/note-n3/content-reduction.md`) found:
  - consolidation cannot close the caveat-density gap: about 7.0–8.0 distinct per 1,000 words, against the
    comparators' 1.6–2.5;
  - only removing secondary results with their qualifiers would close it.
- **The director put three questions to Joseph:**
  - whether to run round 4;
  - what the note's caveat target is;
  - how to decide the paper's secondary results (`state/2d-closeout/stageF/methods/secondary-results/CANDIDATES.md`,
    PR #370).

Joseph's answers, verbatim. The first is the option he selected:

> Round 4 after content cuts

sha256 of the text plus a final newline begins `af809928fc952597`.

> I think merge repeats for now, but during our read we might decide to drop caveats, especially if they are talking about superseeded results

sha256 of the text plus a final newline begins `03bf843bd8288700`.

> wait for the 5d integration but maybe also we can have an independent unbiased gpt astra high suggest what to move based on its understanding of the literature standards

sha256 of the text plus a final newline begins `bd8bb088ee870585`.

## What is decided

1. **The repeats are merged now.**
   - The paper rewrite lane applies the CONSOLIDATE rows of the cost list.
   - Each removed restatement becomes a pointer to its single home, and no fact leaves the note. Rows that only drop
     are not applied.
   - It is a content PR, not a scored register round. It carries a ledger with a probe for every kept fact,
     agy agreement and the note's gates.
   - Two rows remove executive-summary or §12 restatements: R01 and the ES/§12 part of R17. They override the n3 rule
     that ES and §12 restatements stay, and are applied because the summary keeps a pointer to the single home.
2. **Drops are deferred to Joseph's read with Ben,** especially caveats about superseded results.
   - "No fact leaves both documents" stands until Joseph lifts it for a named fact.
3. **Round 4, the last register round under the stop rule,** runs after the content cuts. That is the merges, plus any
   drops Joseph and Ben decide. Its outline comes to the director before any edit.
4. **The paper's secondary results are decided at the 5D integration.** Before that, an independent consult suggests
   what should move.
   - **The model:** `gpt-6-astra`, reasoning high, on `codex-school2` (`CODEX_HOME=~/.codex-school2`), read-only.
   - **Unbiased** means it gets:
     - the paper's current printed text;
     - the results the note prints;
     - a neutral description of the 5D section to be added.

     It does not get the lane's candidate ranking, the director's recommendation or the earlier scores.
   - **It answers from its understanding of the literature's standards,** and it names any published papers it relies
     on, so they can be checked before they are used.
   - **Its output is advice.** It comes to Joseph with the candidate list at the 5D integration, and nothing moves
     until he decides.

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
