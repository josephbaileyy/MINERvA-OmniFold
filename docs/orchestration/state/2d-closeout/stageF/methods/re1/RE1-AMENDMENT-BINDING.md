# Binding: RE-1 run 2 (2026-10-22)

**By** the paper-tighten lane, as director, under [`../RE1-SPEC.md`](../RE1-SPEC.md) and the lane brief
[`../../lanes/RE1-LANE-BRIEF.md`](../../lanes/RE1-LANE-BRIEF.md).

**Bound:** [`RE1-AMENDMENT-DECLARATION.md`](RE1-AMENDMENT-DECLARATION.md) as merged in PR #249 (head `5966dd52`), file
sha256 `d7a2a54b85edea0751132892cb85e105e64bfaa974e23b84e2b7b79c4ce7c2a1`, with its code at `ec829e28`. It is bound as written: code, inputs, runs, controls, readouts,
F, compute, storage and §8's limits. A change after this binding needs a new declaration and a new binding, and no
change may follow a result.

## The §7 decisions

| # | ruling | reason |
|---|---|---|
| D1 | **Recommended:** P3/P4 through P5's frozen configuration-(e) path, on 3D/4D inputs from the frozen dumpers | no new unfold code; the dumpers' built-in exact-reproduction check guards the inputs; the (e)−(c), (e)−(a) and (c)−(a) split keeps the reader honest about which difference is the background treatment and which is the estimator path |
| D2 | **Recommended:** both C2 arms on the same pseudo-data and template | pairing isolates the background treatment, which is RE-1's question |
| D3 | **Recommended:** add D2, P3c, P4c and P5c | the movement table then separates background from path; about 0.9 node-h |
| D4 | **Recommended:** relative change for 3D/4D | no quotable 3D/4D covariance exists, and a trunk projection would be a new covariance product outside RE-1 |
| D5 | **Bound:** K1-2D ≤ 1e-8 relative on the 205 cells; K1-ND bitwise | as declared |
| D6 | **Bound:** 6.0 CPU node-h for run 2, inside RE-1's remaining 29.947 | as declared |

## Conditions

- RE1-SPEC §4's 2026-10-21 04:00 deadline has passed. The grant stands without it, as the declaration restates.
- Pin LightGBM threads with `srun -c`: root_6_28's LightGBM 4.6 follows CPU affinity and ignores
  `OMP_NUM_THREADS`. Each product records its affinity.
- The C2 FLAG/NO-FLAG rule (§5.2) is applied as written.
  - A FLAG goes to Joseph through the director, for the adopted 2D result.
  - The movement table is descriptive and carries no verdict on OI-6.
- REPORT-2 gets an independent two-direction review before its PR.
