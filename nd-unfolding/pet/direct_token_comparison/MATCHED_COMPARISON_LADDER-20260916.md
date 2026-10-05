# What a matched comparison with Gregor's complete approach would require

**CITABLE FOR:** the design requirements below, and the reasons the two approaches are
not yet commensurable.
**NOT CITABLE FOR:** any result. Nothing here is measured, nothing here is authorized,
and none of it is evidence about either approach's performance.

Written under Joseph's 2026-09-16 direction: "Finish the controlled token comparison,
then identify what additional matched comparison is needed to compare our complete
approach with Gregor's. Keep those conclusions separate." This document is that
identification, deliberately held apart from the token-routing result. It requests no
compute and proposes no adoption.

## The question these comparisons must answer

Joseph's practical question is: **which approach gives better unfolding closure,
stability, and compute cost on the same task?** Every requirement below exists to make
"the same task" literally true, because that phrase is where such comparisons usually
fail.

## Why the two approaches are not comparable as they stand

Four gaps, each of which would by itself make a head-to-head number meaningless.

1. **Different objective.** Gregor's [paper v2](https://arxiv.org/abs/2604.12364v2)
   studies supervised regression and pion classification. Ours is OmniFold: iterative
   unbinned reweighting, where the network is a likelihood-ratio classifier inside a
   fixed-point iteration. A model that regresses `E_avail` well is not thereby a good
   OmniFold step classifier, and no reported regression metric converts into a closure
   metric.
2. **Different population.** His preprocessing requires a MINOS-matched muon and
   filters interaction types and prongs (PID −999, PID 0, energy ≤ 1e-6). Our event
   identity, truth denominator, backgrounds, data, and all 12 playlists must stay
   aligned. Comparing across two different event populations measures the selection,
   not the method — this is the asymmetric-comparison failure and it is the single
   most likely way to get a confident wrong answer here.
3. **Different metrics.** His IQR on a regression target versus our closure
   `log_ratio_rmse`, normalization ratio, ESS, tail ESS and truth projections. There is
   no defensible conversion.
4. **Unresolved source semantics.** Photon/blob meaning and calibration, prong
   hypotheses, shared objects and the primary lepton, and the exact tuple release and
   time range all remain open, and the producer questions remain unsent. Until those
   resolve, no real-data comparison of either approach is interpretable.

## The one structural requirement

**Gregor's architecture must be run inside our closure harness, not compared against
its own published numbers.** The architecture becomes the variable; the task, data,
weights, truth denominator, iteration count, budgets, seeds and acceptance criteria
stay fixed at ours. Any design that instead compares his published regression result
to our closure result is an uncontrolled swap of all four gaps above at once and
cannot attribute a difference to a cause.

This is feasible in principle rather than hypothetical: the repository already carries
a vendored PET stack, and OmniLearned is the same architecture family as PET2, so the
architecture can be instantiated on our side of the bridge. It is nonetheless
substantial work, and the bridge itself needs verification before it carries a
conclusion — equal input tensors, equal ratio conventions, and a demonstrated
equivalence on a shared fixture.

## The ladder, one axis per rung

Each rung varies exactly one axis with everything else frozen, and each is a separate
experiment with its own criteria. Rungs are ordered by cost and by how much they
depend on unresolved prerequisites.

| rung | axis varied | status | what it would settle |
|---|---|---|---|
| **R0** | token routing: family-pooled vs individual typed objects | **running** — the frozen 24-job matrix | whether individual tokens improve closure at fixed information, model size and budget |
| **R1** | overflow: uncapped vs cap+truncate vs cap+aggregate | **specified**, unexecuted, [spec](OVERFLOW_SPECIFICATION-20260915.md) | whether compression costs or buys closure, separately from retention |
| R2 | token feature set: his 4 kinematic scalars + type + 5 auxiliary fields vs our field set | not specified | whether his feature definitions carry more usable `E_avail` information than ours |
| R3 | event globals: his 15–16 globals vs our 13 event features | not specified | whether the global block, not the tokens, explains any difference |
| R4 | coordinates: collider-style (η, φ, log pT) vs our view-aware detector geometry | not specified | whether his coordinate convention helps reco clusters or only truth four-vectors |
| R5 | membership: his PID/energy filter and MINOS-matched muon vs our raw retention | not specified | the selection's effect — and it changes the denominator, so it needs its own normalization treatment, not a shared one |
| **R6** | **architecture: PET2/OmniLearned vs our attention bridge, inside our closure harness, random init** | not specified; **this is the rung that answers Joseph's question** | whether his network unfolds better than ours on identical data, weights and budget |
| R7 | framework: PyTorch vs TF/Keras at fixed architecture and data | not specified | bounds framework effects; a control for R6 rather than a result |
| R8 | initialization: hash-bound licensed pretrained checkpoint vs random init | **blocked** | whether foundation-model transfer helps, which is his central claim |

R6 is the rung that answers the question as asked. R0 and R1 are prerequisites in the
weak sense that they tell us which representation to give R6, not in the sense that
they predict its outcome.

## Common footing every rung must share

Stated once, because a rung that omits any of these is not matched:

- identical events, splits, physics weights, truth denominator and normalization,
  fitted once and frozen;
- identical iteration count, epochs per fit, batch size and optimizer budget;
- paired seeds, with the paired difference as the statistic, never two independent
  means;
- identical acceptance criteria, declared before running, including the safeguard
  gates (normalization ratio, ESS, tail ESS, truth projections, cap diagnostics);
- **compute cost measured per arm**, not inferred: per-arm fit and inference seconds
  from the run receipts plus measured allocation seconds, so "better" can be priced;
- a shuffle or label-destroying control per rung, to show the harness can detect
  nothing when there is nothing.

## Blockers, named with what would clear them

| blocker | what clears it |
|---|---|
| Source semantics: photon/blob meaning and calibration, prong hypotheses, shared objects and primary lepton, exact release and time range | producer answers; the questions are drafted and **unsent**, and sending them is not authorized |
| R8 checkpoints | a reachable, licensed, hash-bound checkpoint. Earlier attempts found the HyperScale and NERSC copies unreachable; historical unavailability is not evidence of present unavailability, so this needs re-checking rather than assuming |
| R6/R7 bridge | a verified PyTorch↔TF bridge with equal tensors and ratio conventions, demonstrated equivalent on a shared fixture before it carries any conclusion |
| R5 denominator | a normalization and background treatment valid for a changed population |
| Real-data anything | every item above, plus publication-side prerequisites that this campaign does not touch |

## What this document deliberately does not do

It does not rank the rungs by expected outcome, because that would smuggle in a
prediction as a plan. It does not treat the comparison code's uncapped representation
as evidence that we would win R6 — retention is an implementation property, not a
performance claim. (Scoped 2026-09-17: "uncapped" describes
`typed_token_comparison.py`, **not** the production PET estimator, whose clouds are
energy-ranked and truncated to 12 tokens per `docs/analysis-note/sec_pet.tex:56-57` at
`66d35706`. See §1(b) of `COMPARISON_PROPOSAL-20260917.md`.) It does not treat the cross-device
preflight discrepancy as evidence about either approach. And it does not request
compute: each rung needs its own specification, criteria and authorization, and R2–R8
are unauthorized today.
