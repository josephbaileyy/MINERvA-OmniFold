# The price of moving secondary results to the note (caveat-study R-P9), 2026-11-02

**Asked for by** the director, so that Joseph can decide R-P9 with facts: the candidates, what each costs, the
smallest set that reaches ≤ 4.5 distinct caveats per 1,000 words together with the cut list's 20 moves, and what a
referee would expect a PRD measurement paper to keep.

**On** the paper at `58fa0b89`, after the 20 moves of `cutlist.json`: 44 distinct caveats, 7,484 blinded words,
5.88 per 1k.

**CITABLE FOR:** a priced option for Joseph.

**NOT CITABLE FOR:**
- a decision;
- any physics claim;
- exact counts. Every number carries the caveat study's ±25% coder spread, and words are TeX-section estimates
  calibrated to the blinded count (factor 1.062).

The data and the search are in `price_rp9.py`, with its output in `rp9.json`.

## The answer

1. **4.5 is reachable only by moving the 2D benchmark.** Every smallest set has 8 candidates.
   - Each includes IV B (the end-to-end test against the published result, with Fig. 1), which the abstract and
     Sec. I cite.
   - Each also includes two or three disclosures that qualify the main result itself:
     - Fig. 4's note that the predictions' finite-sample uncertainties are not drawn;
     - the hydrogen-sample footnote;
     - the non-independence of the GENIE v3 tunes;
     - the χ² sensitivity to correlations.
   - **These sets reach 29 distinct caveats in 6,440–6,510 words: 4.45–4.50 per 1k.** The paper would be about 6,500
     blinded words, against 8,080 now and 7,484 after the 20 moves.
2. **The margin is not robust.** 4.45–4.50 sits inside the coder spread: a re-code could land at 3.4 or 5.6.
3. **Moving nothing a referee would expect kept gives 4.93 per 1k**: 33 caveats in 6,693 words. The moves are IV C,
   V C, III A, the low-stability item, two IV A details, and rewording the iteration choice.
4. **Moving every candidate gives 4.24 per 1k** (24 caveats, 5,662 words). That removes the 2D benchmark, the
   generator-sized truth changes and the precision-target study, and it needs abstract and conclusion edits.
5. **Why sections barely help.** Moving a section removes its words as well as its caveats. A section near the
   paper's average density changes little, and one with few caveats makes the rate worse. IV E, the generator-sized
   truth changes, carries no caveat that leaves with it alone. Moving it raises the rate from 5.88 to 6.27, so it is
   in no minimum set. IV F and IV G are already in the 20 moves (MV13, MV15).

## Each candidate (after the 20 moves)

| candidate | distinct caveats it removes | words | what the paper loses | cited by | note holds it | referee |
|---|---|---|---|---|---|---|
| IV C, 2D covariance (a summary sentence stays) | 4: C34, C35, C36, C38 | 455 | the 2D covariance's construction and budget | VI A's coverage statement (points to the note) | yes: note §4, fuller | movable with a summary |
| IV B, 2D benchmark and Fig. 1 (needs IV C) | 3: C32, C33, C69 (C02 too, only if the abstract changes) | 306 | the end-to-end test against the published result | **the abstract** (protected) and Sec. I | content yes (note §6); Fig. 1 no | **keep** |
| V C, 3D/4D descriptive comparisons | 2: MV03, C11 | 108 | the descriptive comparisons of the 3D and 4D central values | Sec. I | yes: note §§7–8 | movable |
| III A, reporting definitions, precision target, envelope | 1: MV04 | 163 | the precision-target study and the envelope | the conclusions (second validation finding) | yes: note §9.4 | movable with a conclusions edit |
| IV E, generator-sized truth changes and Fig. 3 | 0 alone | 465 | the regularization-bias result (up to 74% at high W) | the conclusions (first finding; lessons) | content yes (note §9); Fig. 3 no | **keep** |
| IV E with III A: the conclusions' prior-retention sentences | 1: C20 | 45 | the conclusions' statement that the result retains part of its prior | the conclusions | yes: note §9 | **keep** |
| IV E with V C: IV D's pointer to the earlier result | 1: C41 | 25 | a pointer | — | yes: note §8.1 | movable |
| VI A item 2, low-stability cells | 1: C65 | 35 | a cell-level property of the result | — | yes: note n58 | movable |
| IV A: zero training-seed block; no finite-ensemble correction | 2: C30, C31 | 30 | two covariance details | — | C31 yes (n61); C30 NOTE FIRST | movable |
| the iteration choice reworded (R-P4) | 1: C17 | 0 | nothing (a rephrase; a coder may still count it) | — | — | movable |
| Fig. 4 caption: finite-sample uncertainties not drawn | 1: C76 | 10 | the main figure's disclosure | — | no | **keep** |
| Table III footnote: hydrogen-sample defects | 1: MV07 | 70 | the compared predictions' qualification | — | yes: note §10.5 | **keep** |
| IV H: GENIE v3 tunes not independent | 1: C51 | 30 | the main validation's qualification | — | yes: note §10.4 | **keep** |
| V B: χ² sensitivity to correlations | 1: MV10 | 80 | the χ²'s qualification | — | yes: note n67 | **keep** |

## What a referee would expect the main text to keep

Marked **keep** above; the reasons:
- **The validation evidence behind the main result.** That is the fake-data tests of IV H with their qualifiers, and
  the end-to-end test against the published result (IV B), which the abstract states.
- **The bias evidence that limits how the result is read.** The generator-sized truth changes (IV E) carry the
  regularization bias that the conclusions name as the first validation finding.
- **The qualifications of what is compared.** The hydrogen-sample defects behind the CH-corrected predictions, the
  χ² sensitivity to correlations, and the figure disclosure.

## For Joseph

- **The decision.** Either accept a rate near 5 per 1k, with the benchmark and the bias evidence in the paper, or
  move them to the note to reach about 4.5. The second option needs edits to the abstract and conclusions, and
  removes evidence a referee would look for.
- **The measured gap is about kind, not repetition.** The comparators carry fewer distinct caveats because they
  report fewer secondary results (caveat-study R-P9). This paper's remaining caveats after the 20 moves are mostly
  inherent (K).

## Superseded starting point (2026-11-03)

This price started from 44 caveats, the cut list's prediction after its 20 moves. The re-measure after #711 found
that merges do not lower the count (77 at `97e30dda`; `../after-711-97e30dda/README.md` §2), so the 44 was never
reached. Joseph asked for R-P9 to be re-priced from the measured 77
(`DECISION-20261103-joseph-711-merge-and-rp9-reprice.md` item 2). That price, built and measured, is
`../rp9-reprice-97e30dda/README.md`: no combination of whole moves reaches 6 per 1k, and the lowest is 9.25–9.41.

