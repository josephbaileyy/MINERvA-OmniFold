# DECISION 2026-10-27 — Joseph: the 5D χ² table prints χ² with ndf, and shape-only is its only companion

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The comparator check (`state/2d-closeout/stageF/methods/comparator-chi2-20261027/REPORT.md`, PR #398) read six
  published MINERvA, T2K, NOvA and MicroBooNE papers. It agrees with
  `DECISION-20261026-joseph-5d-generator-comparison-presentation.md` on all three decided points.
- It raised two presentation details:
  - none of the papers prints χ²/ndf as a ratio;
  - both MINERvA papers pair the standard χ² with a log-normal χ² for Peelle's Pertinent Puzzle, where T2K and NOvA
    pair it with shape-only.
- Our shape-only χ² is close to the total for every 16-cell prediction (`FD-G-REPORT.md`), so normalization does not
  drive it.

Joseph's answers, verbatim, the options he selected:

> χ² with ndf, e.g. 109/16 (Recommended)

sha256 of the text plus a final newline begins `d64e94a07c50af2a`.

> No, shape-only only (Recommended)

sha256 of the text plus a final newline begins `4fa803b262934d1f`.

## What is decided

1. **The table prints χ² with its ndf** (for example 109/16), as a pair or as two columns. It does not print the
   ratio.
2. **The only companion column is the shape-only χ².**
   - No log-normal χ² is computed or printed.
   - If a reviewer asks for one, it becomes a declared, 0 node-h addition.

## Not changed

- The rest of the presentation decision.
- The wording is Joseph's, drafted at the 5D integration.
