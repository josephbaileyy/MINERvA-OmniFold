# #981 re-pin list: the quotes the result package re-sources from #977 (2026-11-12)

**By** the limitation-resolver lane, at the director's request of 2026-11-12. This directory keeps the list
committed, because the lane's scratch copy is lost to macOS cleanup after a few days. It is updated in place at each
#977 head that director-helper-3 announces. The edit of #981 itself (PR #981, `build_package.py`, `PROVENANCE.txt`,
`README.txt`) is held until the director calls #977's text freeze. The re-pin then runs once, from this list.

## What is here

| file | what it is |
|---|---|
| `repin_list.tsv` | One row per change the re-pin makes (RP01–RP42, with RP33n, RP33e and RP33k). Each row has the ruling date, the RESPONSE.md quote id if any (`supp-quotes.tsv`'s Q number), the sites in #981 at `91f9cb615`, the action, the source document and the exact new quote. |
| `repin_check.py` | Counts every new quote at a #977 head the way the re-pinned build will read it. It also checks the `tab:gen16` table block against its pinned sha256, and fails with "STOP to the director" if the block changed (the director's standing order). Its MACRO guard fails if a values.tex macro that #981 checks is no longer printed, unless the key it was re-sourced to is printed (RP42). |
| `REPIN-CHECK.txt` | The checker's output at the latest #977 head checked. |
| `comment_strip_measure.py`, `COMMENT-STRIP-30e2e79e.txt` | The measurement behind RP18 (strip LaTeX comments before every count). It runs #981's build in memory twice at #977 `30e2e79e`, once as read and once with comments stripped. Only the old §4.1 quote changes (34 failures against 36), and that quote was already ruled for re-source. The director asked for this in the re-pin's receipt. |
| `dryrun.py`, `ruled_baseline.txt` | The dry run of #981's build at a #977 head, and the failures already ruled. See "The dry run and the merge simulation". |
| `merge_sim.sh` | Builds the merge simulation: a worktree at the #977 head with #981's package checked out into it, then runs `dryrun.py` there. |
| `DRYRUN-a87137996.txt`, `MERGE-SIM-a87137996.txt`, `MERGE-SIM-a87137996-RP27-RP28.txt` | Both runs at #977 `a87137996`, and the merge simulation again with RP27 and RP28 applied in its scratch tree. |
| `READS-a87137996.tsv` | Every file the build and the values producer open in the merge simulation, with sizes, and the four files the build reads through git at `PAPER_REF`. The input to the S1 design. |
| `DRYRUN-a5e3005fd.txt`, `MERGE-SIM-a5e3005fd.txt`, `MERGE-SIM-a5e3005fd-fixes.txt`, `READS-a5e3005fd.tsv` | The same runs and inventory at #977 `a5e3005fd`. The fixes run applies RP27, RP28 and the proposed RP33. |
| `DRYRUN-89b5969b8.txt`, `MERGE-SIM-89b5969b8.txt`, `MERGE-SIM-89b5969b8-fixes.txt`, `READS-89b5969b8.tsv` | The same runs and inventory at #977 `89b5969b8`. The fixes run applies the ruled RP27, RP28 and RP33. |
| `g2r-transcription-20261114/` | The lossless transcription of COV2D-G2R's `data_g2r.npz` (RP34), the measurement behind RP35's ruling (`SUMS.out`), and the one producer of `\fluxBand` under C_new (RP38). Its own `README.txt` and `SHA256SUMS.txt`. |
| `PREP-1f3279bf7.txt` | The three checks run on director-helper-3's D1 prep branch (`prep/d1-cnew-20261114`), before it reaches the draft. |
| `PYTHON-VERSIONS-20261113.txt` | The S3 measurement: the build and the producer on Python 3.10, 3.11 and 3.12. |

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

This checker covers the ruled replacement quotes, which a dry run of #981's current build cannot see.

## The dry run and the merge simulation

`dryrun.py` runs #981's `assemble()` with `PAPER_REF` patched in memory to the #977 head and every check collected.
Failures the director has ruled on are counted, and any other failure is printed as NEW FAILURE (exit 1). Run from
the top of a checkout:

    python3 -B <this directory>/dryrun.py <#977 head>

**What the plain dry run does not see.** #981 reads the paper and Supplement at `PAPER_REF` through git. It reads
`values_fived16.tex` and `values.tex`, and imports `make_values_fived16.py`, from its own tree. In #981's worktree
those are #981's own copies, so the plain dry run checks only the quotes against the head. From `223c1431a` to
`01bb9a7fe` the lane ran only the plain dry run. Two breaks in the head's values files were present at all of those
heads and went unseen: RP27 and RP28. director-helper-2's D6 test found the first, and the merge simulation found the
second.

**The merge simulation** reads everything at the head. `merge_sim.sh` makes a worktree at the #977 head and checks
#981's package directory out into it from #981's head, so the build reads the head's producer and values files, as it
will after the re-pin. The lane runs both, the plain dry run and the merge simulation, at every head:

    bash <this directory>/merge_sim.sh <new empty dir> <#977 head> <#981 head>
    git worktree remove --force <that dir>


## Merge with RESPONSE.md's re-pin list

RESPONSE.md's section "The #981 re-pin list from the Supplement style pass" maps to these rows:
- Q09 is RP14 (drop, with V-PRIOR).
- Q11–Q13 are RP12, the one anchored P3 quote that replaces them.
- Q19 is RP13 ("Fourteen cells pass it; R02 and R06 fail").
- Q20–Q22 are RP15 (drop, with V-PRIOR). The paper's "each leave 14 of the 16 cells valid and 12 under both" check is RP16 (drop).

The director confirmed this mapping on 2026-11-12 and asked director-helper-3 to align RESPONSE.md's wording.

## D1: the rebuilt 2D covariance (RP34–RP40)

Joseph ruled on 2026-11-14 that COV2D-G2R's rebuilt covariance becomes the reported 2D covariance
(`DECISION-20261114-joseph-d1-g2r-adopted.md`, PR #1145). At the data that matrix is
C_new = C_rep − C_univ,old + C_univ,new (`COV2D-G2R-DECLARATION.md` §3); the readout is
`fd/receipts-cov2d/g2r/readout/data/` (PR #1144). Rows RP34–RP40 are proposed to the director. They are `code`
rows, which the checker lists without counting, because the new numbers are not printed in the paper yet. The
director accepted all seven on 2026-11-14, ruled RP35 and RP38 as recorded in their rows, and added the follow-up
RP41.

What moves in #981 (sites at `91f9cb615`):
- `sec-uq2d_universe.csv`, `sec-uq2d_s5_total.csv` and `sec-uq2d_Q.csv` (RP34, RP35). `sec-uq2d_stat.csv`,
  `sec-uq2d_c08.csv` and `sec-uq2d_C_PL.csv` stay, because the declaration changes only the universe block.
- The cross-checks against `cov2d_Q_205.json.gz`, `budget_Q.json.gz` and `fig67_projections.json` (RP36). Each is
  computed from the old Q.
- The macros `\uqMedian` (6.41 → 6.46) and `\uqIntegral` (4.76, unchanged when printed) checked by
  `fig-validation_result2d.csv`, whose x column stays (RP37).
- The `sec-repro2d_benchmark.csv` rows `median_relative_uncertainty`, `integral_relative_uncertainty` and
  `flux_band_median` (RP38). G2R prints no per-band σ, so the third needs a reading of the new universe block.
- PROVENANCE's "THE 2D ARRAYS" paragraph and the universe block's description (RP39).
- The 2D scope line and the OUTCOME-20261108 record quotes keep their words, because the coverage counts are the same
  under C_T' (RP40).

`data_g2r.npz` (sha256 `3b8cc7ceaef97c3dc6bbcd2c5cfdf853442c347e37e23f64eca54898d0e9eb4b`) stays out of git. Its
lossless transcription is `g2r-transcription-20261114/` (PR #1147). It was made from cov2d's local O_NOATIME copy,
whose sha256 equals main's `out.sha256`, with no connect. Two findings there shaped the rulings:
- The package's universe block is not G2R's C_univ_old. RP35's exact sums therefore hold only to rounding (at most
  1.3e-16 relative). The director ruled that Q ships as C_new byte for byte, with the identities checked at 1e-15.
- `\fluxBand` needs the 100 Flux weights, which the npz lacks. They are committed in COV2D's readout blocks. With
  them, the 38 band covariances reproduce C_univ_new to 1.3e-20. The receipt's `fluxband_g2r.py` gives 3.723437872589673
  (printed 3.72), and cov2d pins it from there.

What does not move. These read the published covariance (arXiv:2106.16210's TotalCov), which D1 does not change:
- \chiPaper, the shape and normalization parts, the 73 and 139 directions with their χ² values, and the condition
  number. The tension report computes them as "the paper-cov chi2", with "cond(V) = 1.47e+12" (RE-2
  `receipts/figs/tension_report.txt`, lines 12-13).
- The two run-period rows. They read `compare_to_paper_fullcov` and replica noise (the per-period readout).
- The sixteen-cell tables. They are five-observable, not 2D.

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
| `01bb9a7fe`, the director's ruling | REPIN-CHECK PASS (30 rows). The director ruled on 2026-11-13 that #981's own 2D scope sentence names both tunes in full, "(AR23_20i_00_000 and G18_10a_02_11b)", because #981 defines no short names. The new code row RP26 makes that change at the re-pin. The OUTCOME-20261108 quote stays verbatim. |
| `a87137996` | REPIN-CHECK PASS (34 rows). The plain dry run flags only ruled failures. The merge simulation, run here for the first time, flags three more: f1-tune-g18 and f1-tune-ar23 are `\mbox`-wrapped in values_fived16.tex (RP27, director-helper-2's D6 finding), and #981's freshness check compares the file with `all_values()` alone, while the file also holds the producer's 90 pending-group keys (RP28). With both applied in the simulation's scratch tree, the simulation flags only ruled failures. The director accepted RP27 and RP28 on 2026-11-13 and asked for the README rows RP29 (Python >= 3.12, measured) and RP30 (git). The S1 snapshot design and the S4 checksum for `connect/` are proposed to the director separately. |
| `a87137996`, the director's design ruling | The director approved the S1 and S4 design on 2026-11-13, to be built at the freeze. RP31 is the snapshot: its file list is pinned in code, it includes the producer's two figure sources, and the deposit is the package directory alone. RP32 adds `connect/` to SHA256SUMS. RP29 becomes Python >= 3.10 once #977's producer requotes its two PEP 701 f-strings and the lane measures again. |
| `a5e3005fd` | REPIN-CHECK PASS (40 rows) after three proposals. Commit 97d470aaa keyed the 2D benchmark's literals (re2-cond, re2-chi2-norm, re2-chi2-shape, re2-modes-4, re2-modes-6, re2-chi2-4, re2-chi2-6). Their printed values equal what #981 derives, but #981's four printed checks and rows RP20 and RP22 quoted the literal text. Proposed: RP20 and RP22 quote the keyed sentences, and RP33 turns each value into a key check with the keyed sentences as quotes (RP33n, RP33e, RP33k). The plain dry run flags those four checks. The merge simulation flags them plus RP27 and RP28. With RP27, RP28 and RP33 applied, it flags only ruled failures (44) on Python 3.10, 3.11 and 3.12, with identical output. The requote landed, so RP29 is Python >= 3.10. `tab:gen16` is unchanged: its block sha256 is the same from 1ccb08c29 to this head, and 1ccb08c29 changed only the caption's "Sec.~" to "section~". Until this head, the lane's comparison of that table compared two empty extracts. The guard now in `repin_check.py` replaces it. |
| `a5e3005fd`, the director's ruling | The director accepted RP33 as proposed on 2026-11-13, with RP20 and RP22 quoting the keyed sentences. REPIN-CHECK PASS (40 rows). |
| `89b5969b8` | REPIN-CHECK PASS (47 rows). The Supplement's keying of its decimal results (00ee8569c, 8a5db5d3c, ab9a50335) and the S8 index restructure (a1bd56bfe, 4db16d946) moved none of #981's six Supplement quotes (RP08b, RP09, RP10b, RP12, RP13, RP21 each count 1), and `tab:gen16`'s block sha256 is unchanged. The plain dry run and the merge simulation flag only ruled failures. The RP27, RP28 and RP33 failures are now in `ruled_baseline.txt` (34 → 43 lines), since the director accepted them. With those three applied, the merge simulation flags only ruled failures (44). The snapshot inventory grows from 141 to 161 files (153 outside the package, 17,118,886 bytes): 21 new pins, among them the published 2D result and covariance under `2d-unfolding/minerva_paper_anc/`, and `playlist-term/outputs/playlist_term.json` replaced by RE-2's `partc-r2/playlist/playlist_term.json` (3f7f315f6). |
| `89b5969b8`, D1 | Rows RP34–RP40 added for the rebuilt 2D covariance (section "D1" above), proposed to the director. REPIN-CHECK PASS (47 rows). |
| `89b5969b8`, the director's D1 rulings | The director accepted RP34–RP40 on 2026-11-14. RP35 is ruled: Q = C_new byte for byte, the block identities at 1e-15 with the worst printed, and a 1e-12 plant. RP38 is ruled: `\fluxBand` comes from `g2r-transcription-20261114/fluxband_g2r.py`, 3.723437872589673. RP41 is the follow-up for a route-(A) budget after the LL5D lift. REPIN-CHECK PASS (48 rows). |
| `a8d1746f2` | REPIN-CHECK PASS (49 rows). The only commit since `89b5969b8` is S8.6's wording ("declared" becomes "specified"), which moves none of #981's quotes. The plain dry run, the merge simulation and the fixes simulation flag only ruled failures. The snapshot inventory is identical to `READS-89b5969b8.tsv` (161 files), so no new READS file is kept. |
| `1f3279bf7`, the D1 prep (not a draft head) | director-helper-3's prep re-points the 2D covariance keys to C_T'. #981 quotes none of the changed keys: its only cov2d keys are RP05's five counts. REPIN-CHECK, the plain dry run and the merge simulation all pass (`PREP-1f3279bf7.txt`). The merge simulation passes only because values.tex keeps `\uqMedian` 6.41 and `\uqIntegral` 4.76, while the prep's paper prints `\fvval{q2d-sigma-med}` (6.46) and `\fvval{q2d-sigma-int}` instead. #981's macro checks would bind to numbers the paper no longer prints. RP42 (proposed) re-sources them to the keys, and the new MACRO guard in `repin_check.py` enforces it. Without RP42's mapping the guard fails at this prep (2 BAD); with it, it passes. |
