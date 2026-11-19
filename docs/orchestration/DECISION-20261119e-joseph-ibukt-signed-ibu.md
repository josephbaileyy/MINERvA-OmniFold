# DECISION 2026-11-19 (e) — Joseph: IBUKT's binned IBU takes the signed target, and a declared check on data

**Recorded by** director-helper-3, for the director, who relayed Joseph's words. It goes with [`DECISION-20261119d-joseph-ibukt-cap.md`](DECISION-20261119d-joseph-ibukt-cap.md), which raises the cap.

## What led to it

- **The STOP.** The director reports that screen c STOPPED on the noise-free nominal control (IBU at K=5 gave 0.060, above the 0.02 criterion). A read-only diagnostic ruled out the edge term and the migration term, which leaves the refinement by elimination (DECISION-20261119d).
- **The director's two questions to Joseph:**
  1. Should binned IBU take the signed, background-subtracted target in the IBUKT rerun, with OmniFold keeping the refined target?
  2. Should we run a cheap, declared check? It would unfold the REAL data by binned IBU on the signed target and compare the result with REF-C2C1's refined-target IBU result: χ²/ndf 1.03 at K=10 and 0.83 at K=5 ([`OUTCOME-20261106-ref-c2c1-read.md`](OUTCOME-20261106-ref-c2c1-read.md)). These are the director's figures.

## Joseph's words, verbatim

2026-11-19, answering both questions:

> okay yes lets do all of it

(`6bfbdd559b7563889eace84376443141e4ba606d6837f42a916f3956d215cd6b`, the sha256 of the text plus a final newline.)

## What is decided

1. **The IBUKT design amendment.**
   - Binned IBU takes the signed target, under a declared fail-closed rule for negative bins.
   - OmniFold keeps the refined target.
2. **The cap** is 6.5 CPU node-h across all IBUKT runs (DECISION-20261119d).
3. **A new small declared study:** signed-target IBU on the data, compared with REF-C2C1's refined-target IBU result. It runs at 0 node-h on a login node if that is feasible.
4. **For every step:**
   - its code is reviewed and sha-pinned before it runs;
   - each connect gets fresh fence acknowledgments;
   - DECISION-20261119's other conditions stand.
5. **No note wording changes from any outcome.**

## Not decided here

- Any tolerance change.
- Any claim from the outcomes.
- The wording of the amendment and of the new study's declaration, which the director reviews before anything runs.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the IBUKT design amendment (signed-target binned IBU with a fail-closed negative-bin rule, OmniFold on the refined target), and the authorization of the declared signed-target IBU check on data.
- **Not citable for:**
  - a tolerance change;
  - a director go on any script sha;
  - any outcome or claim;
  - any note or paper wording.

Nothing is submitted, deposited or tagged.
