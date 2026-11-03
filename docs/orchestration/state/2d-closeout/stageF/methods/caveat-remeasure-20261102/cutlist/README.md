# Cut list for the paper lane: the distinct caveats, and the moves that lower their number (2026-11-02)

**Asked for by** the director (Task 3, reframed): "the cut list must target the number of distinct caveats". For each
of the paper's distinct caveats it gives a class, the proposed single statement, the words saved, and the q-id; the
moves are ranked by distinct caveats removed, then words. The aim is the smallest set of moves toward 4.5 distinct
per 1,000 words, without dropping any fact from paper plus note.

**On** the paper at main `58fa0b89` (after #695): the after inventory, `../after-58fa0b89/inv/ours-paper.tsv`.
- 77 distinct caveats;
- 8,080 words;
- 9.53 per 1k.

**CITABLE FOR:** a proposal to the paper lane and the director.

**NOT CITABLE FOR:**
- any physics claim;
- a decision. Every class and proposal is this lane's;
- an exact saving. Words saved are sentence-level estimates, and a coder may split a merged statement again: the
  caveat study's coder spread is about ±25%.

## The answer

| moves made | distinct | words | distinct /1k |
|---|---|---|---|
| none (58fa0b89) | 77 | 8,080 | 9.53 |
| the 16 moves with no prerequisite | 49 | 7,556 | **6.48** |
| all 20 moves (including 2 figure edits and 3 facts the note must first receive) | 44 | 7,484 | **5.88** |
| plus every R campaign resolving its caveat (5) | 39 | 7,484 | 5.21 |
| *P range (6 PRD papers)* | | | *1.38–4.54* |

**4.5 is out of reach without moving inherent caveats.**
- At about 7,500 words, 4.5 per 1k allows 33 distinct caveats.
- 29 caveats are K (inherent), 10 merged statements remain after the moves, and the 5 R caveats remain until their
  campaigns land: 29 + 10 + 5 = 44, the all-moves total.
- The rest of the gap closes only if secondary results leave the paper for the note, with their caveats. That is the
  caveat study's finding R-P9, and it is Joseph's decision.

**Classes of the 77:** merge 33, K 29, M 10, R 5. Full table: `cutlist.md`; data: `cutlist.json`.

## The moves, ranked (the proposals are in `moves.tsv`)

1. **MV02, coverage.** Six caveats become the one VI A coverage statement that #690 item 2 asked for: interval
   coverage, pointwise only, bias not coverage, the stopped coverage test, the 2D covariance not validated, and the
   earlier band's failure. It removes 5 distinct caveats and about 47 words. #695 consolidated the location but left
   six labels.
2. **MV01, run periods.** Five caveats become one IV A statement: post hoc, cause unknown, size poorly determined,
   the audit, and the self-consistency check that cannot fail. It removes 4 and about 54 words. The χ² effect stays
   at V B.
3. **MV09, the note's calibrated tests (M).** VI A item 3's conditions move to the note's Sec. 11, which states them
   (register n68, n71). One sentence stays, with a pointer. It removes 3 and about 61 words. This uses Joseph's rule
   that a limitation may leave the paper with a pointer and a note-prints-it probe.
4. **MV08, background subtraction.** Four caveats become one IV D statement: the purity bias up to 4%, the purity
   estimate's 5.9σ in the 2D closure test, the refined subtraction's residual, and the 1.4% treatment difference. It
   removes 3 and about 31 words.
5. **MV07 and MV07F, the hydrogen samples.**
   - MV07 merges the three caption caveats into the Table III footnote.
   - MV07F also needs Fig. 4's legend tokens removed ("closure B3 failed", "supplement FLAGGED"), which is a figure
     regeneration.
   - Together they remove 4.
6. **MV13, MV15 and MV14 (M).** These move IV F, IV G and the binned diagnostic, each with its scope, to the note:
   - IV F is an earlier estimator's coverage test, with its conclusion sentence (Q43);
   - IV G is the rounding instability;
   - the note states all three (register n51, n54, n53).
   Each removes 1. Their counted words cover only the coded sentences; moving the whole subsections saves more.
7. **The rest each remove 1:**
   - MV04: the envelope;
   - MV03: the 3D/4D central values;
   - MV10: χ² correlation sensitivity;
   - MV06: C_model's sources, merged into its definition;
   - MV16: the caption's "neither seed set was held out".

**Join-only merges: count them low.** MV05, MV11 and MV12 join two sentences into one. They lower the coded count
(−3) and save no words, so they lighten nothing for the reader.

**Prerequisites:**
- MV17 (R11), MV18 (the hydrogen-sample sign dependence) and MV19 (closure pseudo-experiments not paired) need the
  note to print the fact first: none was found in the note at `58fa0b89`.
- MV19 is also figure text.

**R, with their campaigns:**
- C04: a GiBUU sample above 20 GeV (KNOWN_ISSUES 82); not declared;
- C22: the detector-response mismatch test; not declared;
- C31: a finite-ensemble correction; cheap and not declared;
- C40: a four-observable marginal comparison with the 2D result. It is what remains of Q26;
- C65: a stability criterion for the cells, which would change the result: Joseph's decision.

The merged statements also carry R routes, though resolving them does not remove the merged statement:
- MV01 has the run-period diagnosis, #690 3b;
- MV02 has the 1B redesign (3a) and the 2D method coverage (3c).

## Guardrails each proposal was written to

- **Facts.** A proposal uses only the facts and numbers of the sentences it replaces, and `retain` keeps a rewritten
  sentence's other content. The paper lane must still read each proposal against its sentences.
- **No fact leaves paper plus note.** An M move names the note register row that keeps the fact, or is flagged NOTE
  FIRST.
- **The abstract is protected.** Its statements are never counted as cut.
- **What the tool checks.** `distinct_cuts.py` fails if classes.tsv disagrees with the inventory, if an M or merge
  caveat has no move, or if a move names a caveat that does not point back to it. Its self-test exercises both
  directions.

**Rebuild:**

    python3 -I distinct_cuts.py ../after-58fa0b89/inv/ours-paper.tsv <WORK>/blind/ours-paper.txt 8080 <analysis-note at 58fa0b89> cutlist

`<WORK>` comes from `../remeasure.py --work <WORK>` at `58fa0b89`.

## Correction (2026-11-03): merges do not lower the distinct count a fresh coder finds

The re-measure after the round (`../after-711-97e30dda/README.md` §2) tests this list's central assumption: that a
merged statement is coded as one distinct caveat. **It is false.**
- A fresh coder still counts MV01's merged paragraph as 5 caveats, MV02's as 6, and MV07's and MV08's as 3 each. The
  study's distinct unit is (kind, issue label) per sentence, so each fact in a merged paragraph keeps its own label.
- The moves that hold are those that take facts out of the paper: MV06, MV13, MV14 and MV16, and MV07F's legend
  tokens.
- **What this means for the predictions:**
  - the "all 20 moves → 44 distinct, 5.88 /1k" and "16 moves → 49, 6.48" predictions above overstate what this metric
    can show;
  - so does `RP9.md`'s starting point of 44.
  - Merging still lowers words and statements, which is a reader-facing gain. It does not reach the study's distinct
    count.
