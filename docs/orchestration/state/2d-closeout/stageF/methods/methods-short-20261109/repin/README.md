# #981 re-pin list: the quotes the result package re-sources from #977 (2026-11-12)

**By** the limitation-resolver lane, at the director's request of 2026-11-12. This directory keeps the list
committed, because the lane's scratch copy is lost to macOS cleanup after a few days. It is updated in place at each
#977 head that director-helper-3 announces. The edit of #981 itself (PR #981, `build_package.py`, `PROVENANCE.txt`,
`README.txt`) is held until the director calls #977's text freeze. The re-pin then runs once, from this list.

## What is here

| file | what it is |
|---|---|
| `repin_list.tsv` | One row per change the re-pin makes (RP01–RP21). Each row has the ruling date, the RESPONSE.md quote id if any (`supp-quotes.tsv`'s Q number), the sites in #981 at `91f9cb615`, the action, the source document and the exact new quote. |
| `repin_check.py` | Counts every new quote at a #977 head the way the re-pinned build will read it. |
| `REPIN-CHECK.txt` | The checker's output at the latest #977 head checked. |
| `comment_strip_measure.py`, `COMMENT-STRIP-30e2e79e.txt` | The measurement behind RP18 (strip LaTeX comments before every count). It runs #981's build in memory twice at #977 `30e2e79e`, once as read and once with comments stripped. Only the old §4.1 quote changes (34 failures against 36), and that quote was already ruled for re-source. The director asked for this in the re-pin's receipt. |

The actions are:
- `resource`: the new quote must count 1 in its document.
- `drop`: the quote and its check leave #981.
- `code`: a build change.
- `fd16row`: a row of `tab:fd16`, read with `\newline` as a space.

The documents are `paper` (`paper_body.tex`), `supplement` (`supplemental_body.tex`) and `abstract`
(`main_paper.tex`), all under `docs/analysis-note/` at the #977 head.

## How the check reads

`repin_check.py` strips LaTeX comments (an unescaped `%` to the end of the line) and collapses whitespace, as the
re-pinned build will. Each `resource` row must then count exactly 1. Each `fd16row` entry must open a row of the
table labelled `tab:fd16`. The checker exits 1 if any check fails. Run it from any checkout that has fetched #977's
branch (`draft/methods-short-20261109`):

    python3 -B docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/repin/repin_check.py <#977 head>

The lane also runs a dry run of #981's build at each head (`PAPER_REF` patched in memory). That run checks #981's
current quotes. This checker covers the ruled replacement quotes, which the dry run cannot see.

## Merge with RESPONSE.md's re-pin list

RESPONSE.md's section "The #981 re-pin list from the Supplement style pass" maps to these rows:
- Q09 is RP14 (drop, with V-PRIOR).
- Q11–Q13 are RP12, the one anchored P3 quote that replaces them.
- Q19 is RP13 ("Fourteen cells pass it; R02 and R06 fail").
- Q20–Q22 are RP15 (drop, with V-PRIOR). The paper's "each leave 14 of the 16 cells valid and 12 under both" check is RP16 (drop).

The director confirmed this mapping on 2026-11-12 and asked director-helper-3 to align RESPONSE.md's wording.

## Heads checked

| #977 head | result |
|---|---|
| `223c1431a` | REPIN-CHECK PASS (24 rows). RP06 and RP09 were re-sourced for capitalization only, and the director accepted both on 2026-11-12. |
| `fed85b6d6` | REPIN-CHECK PASS (25 rows), after five rows changed in the body's sentence pass and were proposed to the director: RP02 and RP07 are each split into two sentences, RP05's seed clause is reworded, RP08 moves into the display equation eq:crep (new row RP08L requires its label), and RP10 opens with "In eq.~(\ref{eq:crep}),". |
