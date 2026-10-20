# Binding addendum 6: the MP4-A gating-control ruling and the refined-reco extra (2026-10-20)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-20261019.md`](BINDING-PHASE1-20261019.md) §2 (MP4-A).

**CITABLE FOR:** the rulings below.
**NOT CITABLE FOR:** the MP4-A result itself, which lands with the session's MP4-A report.

## What the session reported

**Verdict: FAIL.** On J (RD1) at D-ID grid T2, the one-at-a-time strict-bounds 68% half-width with positivity has a
median of 28.6% and a 90th percentile of 121%, against bars of 10% and 25%. The verdict is the same under every
treatment of acceptance holes and every quantile definition. Positivity changes the median by less than 1%
(constrained over unconstrained, median 0.998).

## Rulings

- **The gating control is read radius-normalized.**
  - PLAN §5.3 requires that with positivity off the solver reproduce D-ID's `sigma_rel` to 1e-6 relative.
  - Addendum 1 to the binding (§2, MP4-A) set the radius to ψ² = χ²₁(0.6827) ≈ 1.0000434, where D-ID uses a unit
    radius.
  - Read literally, the control therefore fails by exactly ψ − 1 = 2.17e-5 on every finite cell, for any correct
    solver.
  - The control exists to check the solver, so it is read with the width divided by ψ. The session declared this
    reading before the run. It reproduces D-ID to 1.5e-14 on all 175 cells, with identical hole sets.
  - **The gate passes and the FAIL stands.** The report states the literal mismatch and this ruling.
- **The solver amendment (trf → bvls within `lsq_linear`) is accepted.** It was declared before any endpoint value
  existed. Both declarations and the log of the aborted run are kept.
- **MP-4 is a negative feasibility verdict for RD1 at the frozen targets** (PLAN §5.3, on FAIL). The remaining
  loophole is unbinned information.
- **The refined-reco extra is approved**, as a descriptive measure of that loophole. It runs locally, 0 node-h, within
  10 core-h.
- **Whether RD2 alone counts as "coarser"** stays Joseph's decision.
