# DECISION 2026-10-24 — Joseph: pursue a 5D measurement by the community-standard route

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The validated-coverage route did not pass.**
  - Stage 0 stopped (`state/measurement-paper/5d-design-20261023/STAGE0-REPORT.md`). It failed 0a, calibration
    transfer, for both reporting definitions. J reached NuWro 0.570 and GiBUU 0.541; H2 reached GiBUU 0.259. Both
    definitions passed 0b, usefulness.
  - R10 is INCOMPLETE (`state/measurement-scoping/r10/REPORT.md`). None of its 11 configurations met the residual
    requirement at any departure; the closest was 0.766 against a cut of 0.667.
- **Joseph's aim.** "I really just want to try and get a published 5d measurement, what would it take for this?"
  (DECISION-20261024, adopt record, item 4).
- **The outside opinion** (`state/measurement-scoping/consult-5d-20261024/`, gpt-6.1-sol at high effort, fresh
  context, minimal prompt) argued for a coarser joint measurement under configuration (e).
  - It would carry a correlated, unscaled unfolding-model component and relaxed precision targets.
  - It named a regularized result published with its smearing matrix (A_C) as the fallback.
  - It called the project's precision and coverage bars project objectives, not publication requirements.
- **The director's recommendation:** adopt that route, with three decisions for Joseph:
  1. reopen coarser joint cells, starting from H2's 27 cells;
  2. carry the 5D model dependence as an unscaled correlated uncertainty, as in 2D. This drops validated coverage as
     the 5D publication requirement, and the paper states that as a limitation;
  3. treat the precision targets as goals, not gates.

  If Joseph agreed: drop R10 option (b), and scope two first steps at about 0 node-h.

Joseph's answer, verbatim:

> okay I agree

sha256 of the text plus a final newline begins `62e26bfad5dec2cd`.

## What is decided

1. **The 5D measurement goes by the community-standard route.** DECISION-20261023 (`-5d-targets-and-paper-round-2`)
   item 7 kept that route as the fallback if Stage 0 or R10 failed, and this decision invokes it.
2. **The reporting definition reopens coarser joint cells, starting from H2,** the 27 cells of a 2⁵ partition, joint
   in all five observables.
   - This widens the exception to DECISION-20261019 §1a that DECISION-20261023 (`-5d-targets…`) item 1 granted for
     the RD2 fallback.
   - Further merging or restriction of cells by sensitivity and simulation support is allowed, provided it is
     declared before any refined-estimator data result is read.
3. **The model dependence is an uncertainty component.**
   - It is M2, C_model,5D = Σ_k s_k s_kᵀ, unscaled (κ = 1), one fully correlated component per generator vertex. It is
     reported beside the statistical and systematic covariance, and in the total.
   - Validated coverage at held-out truths is **not** a requirement for publishing this measurement. The paper states
     plainly that coverage was not validated, and why: Stage 0 and R10 are reported.
     <!-- absence-ok: a requirement on the paper's future text, not a claim that a result is absent from the repository -->
4. **The precision targets are goals.** T1 (10 % median 68 % half-width) and the 8.6 % model-term bar are reported
   descriptively, not used as gates.
5. **The estimator is configuration (e)** (s5e candidate R, the refinement 400/31). Central value and covariance come
   from the same estimator. A 5D (e) covariance does not exist yet (DECISION-20261023 third,
   `-5d-a-and-register-round.md:8-9`; S1 below confirms it while pricing one).
   <!-- absence-ok: restates the recorded absence at DECISION-20261023-joseph-5d-a-and-register-round.md:8-9, which S1 re-checks -->
6. **R10 option (b) is dropped.** R10 stays INCOMPLETE on the record. The validated-coverage route is not pursued
   further with these inputs.
7. **First steps, scoping only, at about 0 node-h:**
   - **S1.** Price the configuration (e) 5D covariance, including its input preparation, which is unpriced
     (`DESIGN.md:310-370` costs the construction at 15.9–18.4 CPU or 24.6–28.3 GPU node-h once its inputs exist).
   - **S2.** Establish whether C_model,5D on the H2 cells can be built from the prior-variation ladder's existing
     L-5D-PV products, or what it would need.

   Each comes back as a costed plan for Joseph. No compute is granted here.

## Not changed

- **The 2D result** and its decisions.
- **Claims and KI-85** are Joseph's.
- **GPU use and Ben.** The 5,100 GPU node-h approved for 5D Stages 2–4 (DECISION-20261023,
  `-gpu-5100-for-5d-stages`) were for tests gated on Stage 0 and R10 passing. They do not run. Any GPU use for the new
  route needs its own plan, Joseph's approval and, for the group pool, Ben's agreement. Joseph's message to Ben stays
  held.
- **MINERvA review.** Publishing a measurement from MINERvA data needs collaboration review. That is Joseph's act.

## Risks recorded with the decision (from the consult and the record)

- **The detector response may depend on the model in ways the five scalars do not capture.** Full-event generator
  reweighting failed its establishment tests for every generator (`phase1/mp2/S2-CLOSURE-SUMMARY.md:18-31`).
- **The model term is large.** L-5D-PV measured a median of 12.6 % on the 39 (E_avail, W) cells, h is not a per-cell bias
  bound: across the ladder's rungs, |shift| ≥ |bias| holds in 47–71 % of positive-control cells
  (`state/measurement-scoping/pv-ladder/REPORT.md`).
- **The five observables carry fewer than five independent constraints,** because reconstructed W is an exact
  function of (p_T, p_∥, q₃) (`sec_eavailw.tex:109-140`). This affects how the paper is pitched and how the cells are
  binned.
