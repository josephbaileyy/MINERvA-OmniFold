# Binding addendum 12: MP-1 input-jitter result, and what it means for a response band (2026-10-21)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-ADDENDUM-11.md`](BINDING-PHASE1-ADDENDUM-11.md).

**CITABLE FOR:** the reading below and the status of MP-1.
**NOT CITABLE FOR:** any band or decision.

## What the session reported (declared study, descriptive)

**The input-jitter study** used edge-safe ±½ float32-ulp jitter of every coordinate, with J = 1–5 for each of zero,
EM ±1 and other ±1. It ran as 5 jobs, about 1 CPU node-h. No grid membership changed, and all 25 products verify.

**Result.** The ratio of the G3 curvature to the jitter noise of a second difference is 1.00–1.19 for EM and other,
below the declared threshold of 3. So the G3 curvature reads as the estimator's discreteness under rounding-scale
input changes, not as hadronic nonlinearity.

**Supporting evidence:**
- Averaging over the jitter seeds shrinks the curvature as noise would.
- The jitter-mean G3 form is 0.073–0.083. This is descriptive, not a gate.

**The session's own, undeclared derivation.** The jitter noise of any second difference is at least 2√T₀. Against
that floor, the proton and meson curvatures are at most about 1.5×, so their G3 PASS reflects their larger spans, not
a measured linearity.

## Reading and status

- **MP1-A stays not calibrated** (PLAN §2.3; addendum 10). The jitter result revives nothing.
- **The G3 gate cannot discriminate.** At ±1σ the estimator's discreteness is as large as the curvature G3 measures,
  for every species. A future response band needs a design whose linearity test sits above that floor: larger
  endpoint shifts, endpoints averaged over jitter, or event-level response-varied nulls (MP1-A-full).
  - The choice belongs to the combined-campaign contract.
  - It is declared before any output.
  - It is costed against the group pool.
  - It is not granted here.
- **Hadronic nonlinearity below the jitter noise is not excluded.**
