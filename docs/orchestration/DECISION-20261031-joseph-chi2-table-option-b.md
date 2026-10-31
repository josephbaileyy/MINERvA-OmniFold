# DECISION 2026-10-31 (later) — Joseph: the χ² tables take Option B, with GiBUU in a separate labelled block

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The independent PRD-reviewer consult
([`state/2d-closeout/stageF/methods/secondary-results/astra-consult-chi2-table-20261031/REPORT.md`](state/2d-closeout/stageF/methods/secondary-results/astra-consult-chi2-table-20261031/REPORT.md),
#576) recommended Option B. It also flagged that the figure diagnosis's "58/8 = 7.3 against 109/16 = 6.8" cannot be a
per-ndf ranking that puts GiBUU first. The director told Joseph so.

> χ² tables (paper Table IV, note Table 16): which presentation?

Joseph's answer, verbatim:

> Option B: separate block (Recommended)

sha256 of the text plus a final newline begins `1c8be4fd766e7774`.

## What is decided

1. **Paper Table IV and note Table 16 are restructured.** The option offered read: "GiBUU in its own labelled "8-cell
   subset: p∥ < 4.5 GeV/c" block; χ² and ndf in separate columns; the caption replaced, not lengthened. No number
   changes."
   - The rows are grouped under **All 16 cells** (GENIE 2.12.10 CV, GENIE 2.12.10 + Valencia MEC, NuWro 21.09 and
     MINERvA Tune v1) and **8-cell subset: p∥ < 4.5 GeV/c** (GiBUU 2019).
   - The columns are χ², ndf, shape-only χ² and ndf. No χ²/ndf ratio is printed.
   - The paper's caption is replaced by the consult's text: "χ² and ndf for each prediction in the indicated comparison
     region, using C_total + C_resp + V_g, where V_g is the prediction's finite-sample (diagonal) covariance. Shape-only
     χ² frees the normalization."
   - The note's Table 16 takes the same structure and keeps its own precision.
2. **This amends `DECISION-20261027-joseph-chi2-table-format.md`'s layout,** which already allowed separate columns.
   Every number and the χ²-with-ndf convention stand.
3. **The paper rewrite lane makes the change** with the values macros unchanged, a probe that every printed number
   equals its macro, and the usual build and register checks. The paper caption is Joseph's approved wording here.

## Not changed

- Every χ², ndf and shape-only value. Nothing is submitted, deposited or tagged.
