# After-Ben batch 1, the Supplement (2026-11-17): meaning read

**Asked by** the director, relaying Joseph and a JINST-style referee he agrees with, on `prep/after-ben-20261117`. The
instruction: no claim changes.

**What changed** (the content of `7735a305c`, carried unchanged in director-helper-3's `5f7f9d5c2`):
1. **US spelling:** neighbor, centered, artifact. check_round check 15 now gates the Supplement
   (`SPELLING_SUPPLEMENT_GATED = True`).
2. **S9's heading** is "Illustrative five-observable results on data". The not-for-fitting restriction leads S9's
   opening paragraph, with its reasons. #981's quote Q08 is re-sourced in `supp-quotes.tsv`.
3. **S8.5's repair** is one chronological account. `ll5d-route-record` (`make_values_fived16.py`) keeps every approved
   fact, and is followed by its implication and the GEANT4 limitation.
4. **The opening** is an overview by scientific purpose, every section destination kept.
5. **Cold read 3.13:** the joint tests' 34 bands are 33 plus Rvp1pi.
6. **Cold read 3.14:** the 0.31 is of the noise-subtracted value.

| read | what it read | verdict |
|---|---|---|
| `read12/` | the batch, against the old text, the route record, the A6/item-14 decision, the band inventory code and the ppbench readout | PASS (one note: the prompt's sign convention for delta; the printed text is right) |
| `read13/` | cold read 3.12 (S8.7's outcome paragraph becomes a pointer, by the director's ruling) and 3.16 (S7's q3 stress test is the synthetic q3 tilt: d-id's config, q3_given_eavail_w at amplitude 0.3), at `ae1705188` | PASS |
| `read14/` | the deferred table layouts at `a5e1c2732` (Table S2's formula lines and widths; S15-S17 pinned): content unchanged | first answer (`answer-first.txt`) FAIL only on the $ delimiters that split one expression at its line break; rerun with that allowed, PASS |

Not done, with reasons:
- **Table S11's restructure:** r3 moves the criteria out of the index. The paper's table 4 caption points readers to S8 for every test's criteria, thresholds and classes, and the index is already a multipage table with repeated headings.
- **Table S5 (the code map):** held for the freeze cut.

**CITABLE FOR:** the wording as read against its cited sources.
**NOT CITABLE FOR:** any result; a locked wording.
