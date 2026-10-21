# Proposal: a shorter Data availability paragraph (for Joseph to decide; NOT applied)

`main_paper.tex`'s Data availability section is protected (rule 4). r13 leaves it byte-identical. This is a draft.

**Why.** Sol quoted the release bookkeeping in 2 of 3 P1 runs:
- r2 quoted "A candidate release package … not yet deposited …";
- r1 and r3 quoted "Rerunning the packaged files from an empty directory …".

Both sol P3 runs flagged all seven sentences, as `[bookkeeping]`, `[internal-record]` and `[development-history]`.

**Length.** The current text is about 262 words (macros stripped). The proposal is about 140 words.

## 1. Current text (main_paper.tex at 38a53a53, comments removed)

```latex
\section*{Data availability}
\label{sec:data-availability}
The input data and simulation are the MINERvA open-data AnaTuples, released under
CC0~\cite{MINERvA:OpenData}; this analysis used an earlier production of that
release, whose 2,374 input files are listed with their SHA256 checksums in the
records cited by the analysis note's appendix on the result package and fixed
identities~\cite{AnalysisNote2026}.  A candidate release package of about
\SI{16}{MB}, described there and prepared locally but not yet deposited, needs
only numpy, scipy, and matplotlib.
With it a reader can
recompute every $p$ value, decision, robustness result, and power figure of
the joint tests, together with the recovery of the lost pseudo-experiments,
the coarse-projection comparison, and the fine-grid $L_{2}$ ratios of
condition~(i); regenerate the null-distribution figure of the analysis note's
joint-test section, the joint $(\Eavail,W)$ map of its fifth-axis section, and
the one-dimensional generator projections; and recompute the numbers quoted in
Sec.~\ref{sec:central}.
Rerunning the packaged files from an empty
directory reproduces every value recorded in the package and every figure
number that it checks.
The package carries the exact-split two-dimensional curve;
Fig.~\ref{fig:validation} and its numbers were instead regenerated
separately, from this paper's LightGBM values and covariance.
Apart from the multiplier scan (recomputable from the record that the same
appendix cites), the other quoted numbers cannot be recomputed from this
package.
They, and the event-level processing, require the archived
analysis products, the open-data AnaTuples, and the generator samples produced
for this analysis.  That appendix states what each part of the release does and does not
reproduce.
\pubhold{deposit identifier and access route, after the separately authorized
release decision.}
```

## 2. Proposed text

```latex
\section*{Data availability}
\label{sec:data-availability}
The input data and simulation are the MINERvA open-data AnaTuples, released under
CC0~\cite{MINERvA:OpenData}.  This analysis used an earlier production of that
release; its 2,374 input files are identified by SHA256 checksum in the records
cited in \napp{app:release}.  A candidate release package of about \SI{16}{MB},
not yet deposited, requires only numpy, scipy, and matplotlib.  It recomputes
every $p$ value, decision, robustness result, and power figure of the joint
tests and the numbers quoted in Sec.~\ref{sec:central}, and it regenerates the
analysis note's figures of the joint-test null distributions and the
$(\Eavail,W)$ map.  The other quoted numbers, except the multiplier scan, and
the event-level processing require the archived analysis products, the
open-data AnaTuples, and the generator samples produced for this analysis;
\napp{app:release} states what each part of the release does and does not
reproduce.
\pubhold{deposit identifier and access route, after the separately authorized
release decision.}
```

**Notes on the draft.**
- `\napp` is defined in `paper_body.tex`, which is input before this section. It prints "Ref. [14], App. H".
- The `\pubhold` text is copied byte for byte.
- "Candidate" and "not yet deposited" stay in the paper, as a guardrail. The rater copy renders `\pubhold` as nothing. Without these words, the rater copy, and any copy built before the deposit, would read as if the package were available. That is stronger than the evidence.
- The multiplier-scan exception ("except the multiplier scan"; "Apart from the multiplier scan" before review D-1) stays for the same reason. Without it, "the other quoted numbers … require the archived products" would be false as read of the scan, which RC7's inputs can recompute.

## 3. Where every fact goes

"App. H" is `app_release.tex`, `\label{app:release}`, which prints as App. H in the r13 build.

| # | fact in the current text | destination | already prints in the note? |
|---|---|---|---|
| 1 | inputs are the MINERvA open-data AnaTuples, CC0 [8] | stays | — |
| 2 | this analysis used an earlier production of the release | stays | also H.1 ("the earlier production of MINERvA open-data AnaTuples") |
| 3 | 2,374 input files with SHA256 checksums, in records cited by App. H | stays (shortened) | yes, H.1: "SHA256 identities for all 2,374 inventoried AnaTuple input files~\cite{AnaTuplePreservation2026}" |
| 4 | candidate package, about 16 MB | stays | yes, H: "approximately 16 MB sufficient-input package" |
| 5 | "described there" | stays, as the pointer `\napp{app:release}` | — |
| 6 | "prepared locally" | moves to App. H | yes, H: "A local release candidate, RC7, exists with a README, checksums and a replay verifier" |
| 7 | not yet deposited | stays (guardrail) | yes, H: "It has not been deposited or released under a publication tag." |
| 8 | needs only numpy, scipy, matplotlib | stays | **no.** If it is wanted in the note as well, ADD to H; source `docs/publication/release/RC7-README.md` ("Tested with …") |
| 9 | recomputes every p value, decision, robustness result, power figure of the joint tests | stays | yes, H: "reproduces the joint-test $p$ values, decisions, robustness and power results" |
| 10 | … together with the recovery of the lost pseudo-experiments | moves to App. H | yes, H: "the lost-seed resolution under reading~(a)" |
| 11 | … the coarse-projection comparison | moves to App. H | yes, H: "coarse-projection comparison" |
| 12 | … the fine-grid L2 ratios of condition (i) | moves to App. H | yes, H: "fine-grid $L_2$ ratios" |
| 13 | regenerates the note's null-distribution figure | stays (shortened) | yes, H: "the null distributions of the joint tests (Fig.~\ref{fig:joint5d-nulls})" |
| 14 | regenerates the joint (Eavail, W) map | stays (shortened) | yes, H: "the $(\Eavail,W)$ excess map (Fig.~\ref{fig:eavailWexcess})" |
| 15 | regenerates the one-dimensional generator projections | moves to App. H | yes, H: "and the one-dimensional generator projections" |
| 16 | recomputes the numbers quoted in Sec. VII A | stays | **no.** The note says RC7 draws the figures but not that it recomputes the article's Sec. VII A numbers. Keep it in the paper (as proposed), or ADD to H |
| 17 | rerunning from an empty directory reproduces every value recorded in the package and every figure number it checks | moves to App. H; **needs an ADD** | **no.** H.1 prints only "An earlier version of the package was also replayed from an empty directory by an independent reader". Proposed ADD to H, "Release status": "Rerunning RC7's packaged files from an empty directory reproduces every value recorded in the package and every figure number that its verifier checks." Source: RC7-README.md ("fresh virtual environment, empty directory"; `verify_rc.py`). Joseph or the reviewer should confirm the wording against the RC7 replay record before adopting. |
| 18 | the package carries the exact-split 2D curve; Fig. 1 and its numbers were regenerated separately from the LightGBM values and covariance | moves to App. H | yes, H: "RC7 was assembled before the two-dimensional central value was changed to LightGBM, so its two-dimensional curve is the exact-split one. The article's two-dimensional validation figure and its numbers were instead regenerated separately, from the committed LightGBM values and covariance" |
| 19 | the multiplier scan is recomputable from the record the appendix cites | the exception stays ("Apart from the multiplier scan"); the "recomputable from the cited record" detail moves to H.1 | yes, H.1: "The multiplier scan … is recomputable from RC7's sufficient inputs with the scan code of Ref.~\cite{JointTestKappa2026}" |
| 20 | the other quoted numbers cannot be recomputed from this package | stays, as "the other quoted numbers … require the archived analysis products, …" | yes, H.1 lists what RC7 does not reproduce |
| 21 | they, and the event-level processing, require the archived analysis products, the AnaTuples, and the generator samples | stays | yes, H.1: "Event processing requires the earlier production of MINERvA open-data AnaTuples, event-loop outputs, and the generator samples used here"; "The pseudo-experiment products are archived (about 2.3 GB)" |
| 22 | that appendix states what each part does and does not reproduce | stays, as the pointer | H.1 |
| 23 | `\pubhold{deposit identifier and access route, …}` | stays, byte-identical | — |

**If Joseph adopts the proposal,** one sentence must be added to `app_release.tex` first (row 17), so that no fact leaves both documents. Rows 8 and 16 stay in the paper, so they need no addition. Then the ledger needs DA rows, and the r12 rule that the protected text is checked by diff must be lifted for this section.

## 4. The independent review's comments on this draft (`REVIEW.md` §D), and what changed

The review found all 23 destination rows correct and the "current text" transcription exact.

- **D-1 (should fix).** "Apart from the multiplier scan, the other quoted numbers, and the event-level processing, require …" parses as a list governed by "Apart from". Read that way, the verb has no subject, and the other quoted numbers are exempted.
  - **Applied to the draft above:** "The other quoted numbers, except the multiplier scan, and the event-level processing require …".
  - The test compile in §2 used the earlier wording; the change is to words only.
- **D-2 (should fix; the proposed note addition in row 17).** The wording is supported by `docs/publication/release/RC7-README.md:75–78` and `:105–106`: a fresh virtual environment, an empty directory, and `verify_rc.py` reporting "VERIFY: PASS".
  - **Caveat 1.** That is RC7's own README, not an independent replay record. H.1's independent empty-directory replay was of an earlier version (RC1). The addition must not be worded as, or placed beside, the independent replay.
  - **Caveat 2.** The same README is stale on Fig. 1: it says `make_figs.py` reproduces `paper_fig1_validation.pdf` byte for byte, which stopped being true when the 2D central value became LightGBM. Cite the README for the empty-directory run only.
  - **Revised wording for row 17,** placed in H's "Release status" paragraph, not beside H.1's independent replay: "RC7's own verifier, run on the packaged files in an empty directory, reproduces every value recorded in the package and every figure number that it checks (RC7 README)."
- **D-3 (decision flag, not a defect).** The draft moves "The package carries the exact-split two-dimensional curve; Fig. 1 … regenerated separately" to App. H.
  - A `main_paper.tex` comment records an earlier ruling (plain-language pass 2, theme B, P6): "the package's limitation stays here".
  - DECISION-20261021 (second) item 4 plausibly supersedes it, but adopting the draft reverses P6. Joseph should decide this explicitly.
  - No sentence of the draft becomes false without it, because the draft does not claim that the package reproduces Fig. 1.
