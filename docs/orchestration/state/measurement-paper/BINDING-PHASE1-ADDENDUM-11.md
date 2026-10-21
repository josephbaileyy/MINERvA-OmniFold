# Binding addendum 11: MP-1 noise-floor result, and an input-jitter study (2026-10-21)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-ADDENDUM-10.md`](BINDING-PHASE1-ADDENDUM-10.md).

**CITABLE FOR:** the ruling below.
**NOT CITABLE FOR:** any result. The results are in the session's PR #194 records.

## What the session reported

- **The noise-floor study, descriptive.** The unfold is invariant to the training seed: its configuration is
  deterministic, with no bagging, so the random state randomizes nothing. Training-seed noise is ruled out as the
  cause of the G3 curvature.
- **Still open:** a physical nonlinearity, or a deterministic but non-smooth response of the binned tree estimator
  to small changes in its inputs.
- **The labelled partial S2,** with only the proton and meson bands, post hoc: no decision moves, in the frozen
  family or at κ = 3.
- **MP1-A-full** is priced at about 230–320 CPU node-h.

## Ruling

- **An input-jitter study is approved as DESCRIPTIVE**, with no gate. It cannot revive MP1-A.
  - **Design:** `s5p_numerics --pairs=-:J`, the code's own edge-safe ±½ float32-ulp jitter of every coordinate, which
    refuses any change of grid membership. J = 1–5, for each of zero, EM ±1 and other ±1: 25 unfolds.
  - **Declared in a file before running.**
  - **Readout:** the jitter-to-jitter scatter of f and the second-difference norm it implies, against each species'
    curvature.
  - **Budget:** about 1 CPU node-h on regular, within the phase-1 ceiling. Every job finishes by 2026-10-21 04:00 PDT;
    otherwise the study is deferred.
- **MP1-A-full is not granted.** It waits for the jitter result and for the combined-campaign planning.
