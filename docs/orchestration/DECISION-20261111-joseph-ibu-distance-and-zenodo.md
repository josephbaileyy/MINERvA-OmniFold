# DECISION 2026-11-11 — Joseph: the short paper prints the IBU-to-publication distance with a careful reading; the reproduction package goes to Zenodo

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The fresh referee round** (`state/2d-closeout/stageF/methods/secondary-results/referee-methods-fresh-20261111/gpt.txt`,
  major 4) asked for the direct IBU-to-publication distance beside OmniFold's. Its major 8 and the recheck round's §4
  table both require an accessible reproduction package before publication.
- **The number exists and was never printed.** helper-3 found it in a committed readout (`read-2/readout.json`,
  `0ee21301`, as RESPONSE.md row F4.2 cites it): on these inputs the binned IBU's distance to the published 2D result
  under the published covariance is about 1.03 per degree of freedom at K = 10 (0.830 at K = 5), against 2.27 for
  OmniFold. The director has not re-read these values; the paper text will quote them from that readout through the
  usual value checks.
- **The package** (PR #981) is not deposited. Nothing is deposited without Joseph.

## The questions and Joseph's answers, verbatim

On the IBU distance (options: print with a careful reading, recommended; print with no interpretation; do not print):

> Print + careful reading (Rec.)

(`3cefa22b50b978f4`). On the deposit venue (options: Zenodo, recommended; HEPData; JINST attachment only; decide later):

> Zenodo (Recommended)

(`2dca0b5943cf964a`). Each sha256 is of the text plus a final newline.

On a third question, whether to also regrade the 2D coverage test after rebuilding the systematic universes, Joseph
answered "what does an independent reviewer think? 10 node hours isn't too big of a cost" (`1caea9a086833353`). That
is not decided here: an independent consult is under way, and its decision will be recorded separately.

## What is decided

1. **The IBU distance is printed in §4.2**, beside OmniFold's, with one sentence that on these inputs the binned
   method is much closer to the published shape, so the difference arises mainly in the unfolding step. The mechanism
   stays unestablished, and without the cross-covariance the comparison stays descriptive. A PRD-referee read of the
   paragraph comes before it is final, and no other sentence may still imply that the inputs cause the difference.
2. **The reproduction package's venue is Zenodo.** The paper's availability text says what will be released.
   **Nothing is deposited** until Joseph gives the final go on the package's contents and timing.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** printing the IBU distance with that reading, and the Zenodo venue, as Joseph's choices.
- **Not citable for:** the distances' values (cite the readout); any attribution of the shape difference's mechanism;
  a deposit; the 2D regrade.

Nothing is submitted, deposited or tagged.
