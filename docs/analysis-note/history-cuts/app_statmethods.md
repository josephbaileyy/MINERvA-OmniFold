# History restructure, App. A (app_statmethods.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13, and the
director's ruling (A) of 2026-11-14 (recorded in sec_5d.md).

**The rule, verbatim as adopted:** history stays in the note only if removing it would change a reader's understanding
of the reported object, its reproducibility, its evidential independence or its limitations. Everything else goes to
the ledger. Each "fixed before" names its object, and "declared" alone is replaced.

**Referee:** for App. A it gave "10–20%, Compress / ledger. Keep statistical definitions; remove obsolete scans and
checks unless they support an explicit comparison." Its item 8 (§A.2.6): "**Cut (ledger)** the obsolete agreement
calculation and its autopsy. Keep the check on the quoted weighted covariance and its scope. If the old check remains
cited as evidence, its limitation must remain too."

**Base:** `docs/analysis-note/app_statmethods.tex` at `ae4285e94`. Line numbers are the base's.

## The changes

| id | base line | old text | new text | ledger home |
|---|---|---|---|---|
| A1 | :231 | "An earlier check compared \texttt{MnvH1D::GetTotalErrorMatrix} with our band sum without the normalization band, over $44$ bands / $187$ universes, and gave a maximum difference of $5.5\times10^{-17}$ of the largest element (machine $\varepsilon$) and $\sqrt{\Tr\mathbf{C}}$ matching to seven digits. That check could not detect that the Flux band omitted those constraint weights, because it filled the \texttt{MnvH1D} without MAT's per-universe weights (\texttt{SetUnivWgts}). Both sides were unweighted. That check used a sweep from before the flux fix. It did not test a quoted product." | cut (referee item 8). The paragraph keeps the check on the quoted product: "The quoted universe block, filled into a \texttt{PlotUtils::MnvH1D} with MAT's universe weights on Flux, agrees with \texttt{MnvH1D::GetTotalErrorMatrix} to $1.3\times10^{-16}$ of its largest element. The quoted Flux band carries MAT's $\nu$--$e$ and inverse-muon-decay constraint weights." | ae4285e94:app_statmethods.tex:231 |
| A2 | :505 | "with the Flux band weighted as MAT weights it (the earlier machine-precision check of \S\ref{sec:minerva} covers the unweighted bands) and" | "with the Flux band weighted as MAT weights it (\S\ref{sec:minerva}) and". The old check was cited here as evidence, so it leaves with A1, as item 8 requires. The pointer now goes to the check on the quoted, weighted block. | ae4285e94:app_statmethods.tex:505 |
| A3 | :583 | "would leak more than the analysis declared tolerable" | "would leak more than the analysis specified as tolerable" | a method use of "declared" (the 3.0% acceptance bound of the same paragraph): no timing |

**Kept as they are, because each supports an explicit comparison or limitation that App. A reports:**
- **:362** "Nor is the exact-split cross-check's $1.47$, computed with an earlier covariance built before the flux-band
  repair, evidence against them on its own": the applicability of a printed comparison.
- **:411**, the exact-split cross-check's pulls on the earlier covariance: printed beside the quoted ones, and labelled.
- **:458** and **:468**, the split bootstrap of the earlier rebuilt bootstrap: the quoted block's own ratio (0.407,
  0.425) is printed with it, and "is not established here" limits its reading.
- **:476** "Regularization scans (earlier covariance; all cutoff-dependent)": the evidence for "The inverse of
  $\mathbf{C}^{\ours}$ remains regularizer-dependent" (:474) and for :505's "no covariance-based goodness-of-fit is
  claimed". :505 states that the scan is of an earlier $\mathbf{C}^{\ours}$.
- **:545**, the exact-split row "(cross-check; earlier central value)", and **:565**, the "$0.166\%$ ML floor of the
  earlier ten-seed scan, which was in force when the tests were graded": each labels an earlier object where it is
  compared.
- **App. A.8, the same-ensemble pull diagnostic** (moved here from §5 as V2): no change.

**Numbers and keys:** `numdiff.py` on the base and new files, comments stripped:
- Removed: "44", "187", "5.5", "17" and "0", all from A1's cut check: $44$ bands, $187$ universes and
  $5.5\times10^{-17}$. The "0" is how numdiff.py's pattern reads "\times10", whose "1" follows a letter and is skipped.
- Added: none.
- Value keys and macros: unchanged.

## The Development-history appendix

No new row. The cut check was a regeneration check of a pre-fix sweep, which the referee's structure excludes, and no
released result rests on it.

## Disclosure checklist

| disclosure | in App. A? | survives |
|---|---|---|
| the 2D adoption after the published distance was known | no (§3) | — |
| the post-observation run-period term | no (§4) | — |
| reused samples and seeds | the same-ensemble pull diagnostic (A.8) | ✓ unchanged |
| the invalid q3 deformation | no | — |
| the stopped coverage tests | no | — |
| the data-informed joint-test design and budget extension | no | — |
| the missing response uncertainty | no | — |
| the generator-sample problems | no | — |
| the target-correction sensitivity | no | — |
| also found: the hidden-$\dpT$ leak above the acceptance bound, "an open sensitivity, not a passing test" (:583) | yes | ✓ unchanged (A3 is the word only) |
| also found: the earlier covariance's results labelled where compared (:362, :411, :476, :505) | yes | ✓ unchanged |

## Unreleased support

No site in App. A changes its citation. `UNRELEASED-SUPPORT.md` is unchanged.

## Meaning read (codex-school gpt-6.1-sol, high, read-only; reads/app_statmethods-prompt.txt)

- **Pass 1:** OVERALL PASS, with no FAILs. A1–A3 pass; A1 and A2 are LEDGER; no NEEDED item lost; no disclosure lost.
  reads/app_statmethods-pass1.txt.
