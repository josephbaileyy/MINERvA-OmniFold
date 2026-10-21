# Binding addendum 10: MP-1 G3 outcome, a noise-floor study, and a labelled partial (2026-10-20)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-20261019.md`](BINDING-PHASE1-20261019.md) §2
(MP1-A).

**CITABLE FOR:** the rulings below.
**NOT CITABLE FOR:** any result. The G3 report lands with the session's next PR.

## What the session reported

G3, the linearity gate: the curvature norm over the span norm must be at most 0.2.

| species | ratio | verdict |
|---|---|---|
| proton | 0.172 | PASS |
| meson | 0.104 | PASS |
| EM | 0.248 | FAIL |
| other | 0.241 | FAIL |
| cross-talk (variant) | 0.302 | FAIL |

The curvature norm is nearly constant across species, while the span varies by a factor of four. That pattern
suggests a training-noise floor, but this is not shown.

## Rulings

1. **G3 is recorded as FAIL for EM and other**, PASS for proton and meson, and FAIL for the cross-talk variant.
   - By the frozen rule (PLAN §2.3, on G3 failure), MP1-A is **not reported as a calibrated result**: no band and no
     decision.
   - MP1-A-full is priced in the report, as the rule requires.
2. **A descriptive noise-floor study is approved.** It has no gate and no re-gating, and it cannot revive MP1-A.
   - Design, declared in a file before running: K = 5 perturbed training seeds for each of the δ=0 control and the
     EM ±1σ and other ±1σ endpoints, as in S1.
   - Readout: the seed scatter of f, the second-difference norm expected under pure noise, and each species' curvature
     against that expectation.
   - Budget: at most 4 CPU node-h, within the phase-1 ceiling, before the drain; otherwise deferred.
3. **A labelled descriptive partial S2 is approved.** The frozen S2 machinery runs with only the proton and meson
   bands.
   - Label: "not the MP-1 result; species restricted after the G3 outcome; post hoc".
   - It is reported beside A7, including whether any decision moves.
   - Login-node work, 0 node-h.
4. **Option (c), any loosening of the 0.2 tolerance, is refused.**
