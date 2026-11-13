# #981 re-pin list: the quotes the result package re-sources from #977 (2026-11-12)

**By** the limitation-resolver lane, at the director's request of 2026-11-12. This directory keeps the list
committed, because the lane's scratch copy is lost to macOS cleanup after a few days. It is updated in place at each
#977 head that director-helper-3 announces. The edit of #981 itself (PR #981, `build_package.py`, `PROVENANCE.txt`,
`README.txt`) is held until the director calls #977's text freeze. The re-pin then runs once, from this list.

## What is here

| file | what it is |
|---|---|
| `repin_list.tsv` | One row per change the re-pin makes (RP01–RP25). Each row has the ruling date, the RESPONSE.md quote id if any (`supp-quotes.tsv`'s Q number), the sites in #981 at `91f9cb615`, the action, the source document and the exact new quote. |
| `repin_check.py` | Counts every new quote at a #977 head the way the re-pinned build will read it. |
| `REPIN-CHECK.txt` | The checker's output at the latest #977 head checked. |
| `comment_strip_measure.py`, `COMMENT-STRIP-30e2e79e.txt` | The measurement behind RP18 (strip LaTeX comments before every count). It runs #981's build in memory twice at #977 `30e2e79e`, once as read and once with comments stripped. Only the old §4.1 quote changes (34 failures against 36), and that quote was already ruled for re-source. The director asked for this in the re-pin's receipt. |

The actions are:
- `resource`: the new quote must count 1 in its document.
- `drop`: the quote and its check leave #981.
- `code`: a build change.
- `fd16row`: a row of `tab:fd16`, read with `\newline` as a space.
- `keys`: each value key must still be printed (`\fvval{key}` at least once).
- `term`: a term in one of #981's descriptions follows the paper's term. The row holds `old|new`; the new term must be
  printed at least once in the document and the old one not at all.

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
| `fed85b6d6` | REPIN-CHECK PASS (25 rows), after five rows changed in the body's sentence pass and were proposed to the director: RP02 and RP07 are each split into two sentences, RP05's seed clause is reworded, RP08 moves into the display equation eq:crep (new row RP08L requires its label), and RP10 opens with "In eq.~(\ref{eq:crep}),". The director accepted all five on 2026-11-12. |
| `1ccb08c29` | REPIN-CHECK PASS (26 rows), after five quotes moved in style round 3 and were proposed to the director: RP02 opens "The held-out-tune tests" and is quoted up to its new cross-reference, RP06 now reads "lack validated coverage", RP08b is now the Supplement's unnumbered equation, RP12 is split after "carbon.", and the new row RP22 holds Table 1's benchmark anchor, which gained "descriptive". The director accepted all five on 2026-11-12. |
| `9c9203f41` | REPIN-CHECK PASS (27 rows). The B0/RS1 rewrite and RSN's paper text moved none of #981's quotes: RP02, RP03 and RP04 each still count 1. The new row RP23 (`keys`) checks that the seven ens1-* keys #981's ENS1 rows depend on are still printed. #981 quotes no B0 or RS1 sentence. |
| `f0c451a9d` | REPIN-CHECK PASS (28 rows). Style round 4's paper pass moved none of #981's quotes, and the dry run flags only ruled failures. One term changed under a #981 description: the paper now says "reported cells" where #981's glossary entry for a cell says "reporting cells". The new row RP24 (`term`) proposes that the glossary follow the paper. The director accepted it on 2026-11-13. Search: `git show f0c451a9d:docs/analysis-note/paper_body.tex`, counted case-insensitively after comment stripping: "reporting cells" 0, "reported cells" 13. Coming next: journal-editor is removing Supplement Table S14, which is `tab:gen16` at this head. #981 binds `tab-gen16.csv` to that label and its self-test plants a missing `\label{tab:gen16}`, so that removal needs the director's ruling once it lands. |
| `990aad756` | REPIN-CHECK PASS (28 rows), after three rows moved under Joseph's critique of sections 1–4 and option B and were proposed to the director. RP07 and its self-test plant RP07p are now the one sentence "The origin of the shape difference has not been identified.": the binned-unfolding sentence is gone, and "mechanism" became "origin". RP11 reads ", without reweighting events", and the glossary description follows. The paper's new sentence comparing OmniFold with binned IBU occurs twice, so it could join #981's 2D scope line only anchored to the sentence after it. The dry run flags only ruled failures. |
| `990aad756`, the director's rulings | REPIN-CHECK PASS (29 rows). The director ruled on 2026-11-13 that the 2D SCOPE line states the IBU difference. RP07 and RP07p therefore quote the adjacent pair "On this analysis's inputs, OmniFold and binned IBU, the publication's method, differ beyond paired replica noise (section~\ref{sec:paired2d}). The origin of the shape difference has not been identified." The pair counts 1, though its first sentence alone occurs twice. The new row RP25 changes "cause" to "origin" in #981's own scope sentence; the OUTCOME quote stays verbatim. RP11 is accepted. |
| `01bb9a7fe` | REPIN-CHECK PASS (29 rows). Its output equals the run at the director's 990aad756 rulings except for the head line. Joseph's read of sections 5 to 6.1 moved none of #981's quotes, and the dry run flags only ruled failures. Tune names: the paper prints `\fvval{f1-tune-g18}` and `\fvval{f1-tune-ar23}` once each, at first use with the short names G18 and AR23 in parentheses, and the short keys after that (14 and 13 uses). #981's own 2D scope sentence (B765-766, R305) names the tunes "AR23 and G18_10a_02_11b", as its OUTCOME-20261108 quote does, and #981's tune column prints the full names. The lane proposes keeping that sentence as it is; the director rules. The seven ens1-* keys of RP23 keep their print counts. |
