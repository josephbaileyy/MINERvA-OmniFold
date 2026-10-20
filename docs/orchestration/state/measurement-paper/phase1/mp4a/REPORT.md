# MP4-A: the P0-OSB diagnostic, a negative feasibility verdict for RD1

**By** the measurement session, 2026-10-20, under the frozen MP4-A specification (PLAN.md §5.3, frozen by
BINDING-PHASE1-20261019 §2 with its radius amendment). This report was written by the coordinating session from the
agent's report text, because the agent's file write was refused, and checked against `osb_summary.json` and
`DECLARATION.json` in this directory.

**CITABLE FOR:**
- the verdict that one-at-a-time strict-bounds (OSB) intervals with positivity fail the frozen T1 width target on
  RD1 at D-ID grid T2, even in the optimistic noise-free, signal-only case;
- the per-functional OSB widths;
- the gating control and its ruling.

**NOT CITABLE FOR:**
- a validated interval;
- any statement about unbinned information beyond binned Fisher widths;
- any claim (claims are Joseph's).

**Verdict: FAIL.** On J (RD1, 109 functionals) at D-ID grid T2, the OSB 68% relative half-width with positivity has
median **28.59%** (the bar is 10%) and 90th percentile **120.8%** (the bar is 25%). The verdict does not depend on how
holes or unresolved endpoints are treated, or on the quantile definition. Per §5.3, MP-4 is therefore recorded as a
**negative feasibility verdict for RD1 at the frozen targets**:
- prior-free intervals fail T1 even in the optimistic case;
- prior-including methods fail T2 on the measured model component (PLAN §5.1);
- the remaining loophole is unbinned information, which this diagnostic does not bound. It is **material**: a 2× reco
  refinement alone brings the binned J floor to the edge of T1 (§6a). So the result is a no-go at the analysis
  binning, not a proof of impossibility.

## 1. Inputs and construction

- **Events.** `of_inputs_5d.npz`, 1,548,438,020 B, sha256 `07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f`,
  equal to D-ID's pinned digest. One read-only `scp` copy was made; 0 node-h.
- **Operands.** Rebuilt with D-ID's own classes (`state/next-preparation-20261009/d-id/did.py`), and D-ID's admission
  checks pass. D-ID's committed T2 widths are reproduced **bitwise** from `tables.npz`.
- **Problem.** For each reported functional h (J 109, H2 27; EW 39 in the gate only), min and max of hᵀλ subject to
  ‖W^{1/2}(y − Rλ − b)‖² ≤ ψ² and λ ≥ 0. Here y = R t + b is the noise-free nominal reco data,
  W = diag(1/(R t + b)) is D-ID's Fisher weighting, and ψ² = χ²₁ quantile at 0.6827 = 1.000043427 (the binding's
  amendment).
- **Solver (declared).** A Lagrangian search in s = 1/(2μ), with the inner problem solved by `scipy.optimize.lsq_linear`
  (`method='bvls'`, `lsq_solver='exact'`, tol 1e-12, max_iter 6915), on an exact n-column factor G with GᵀG = F.
  Settings are in `DECLARATION.json`. Every one of the 245 converged endpoints is certified by a primal–dual gap
  ≤ 6.6e-10 relative.

## 2. The declaration and its one amendment

- **Version 1** (`DECLARATION-v1.json`, 2026-10-20T08:03:59Z) used `method='trf'`. Its run returned solver failures on
  51 of the first 138 endpoints and was killed before it wrote any endpoint value; `osb-run1-aborted.log` holds only
  statuses and timings. A status-and-cost check showed `trf` stopping short of the optimum where `bvls` solved the same
  calls.
- **Amended** (`DECLARATION.json`, 08:25:19Z): only the inner method changes, to `bvls`, still within `lsq_linear` as
  frozen. Radius, constraint, tolerances, hole reductions, gate rule and PASS rule are unchanged. The gate was re-run
  under the amended code with the same result (`gate.json`; the v1 gate is `gate-v1.json`).
- The director accepted the amendment: it preceded any endpoint value, stays in the frozen family, and is disclosed
  with both declarations and the aborted log kept.

## 3. Gating control (positivity off, all 175 reported functionals)

| reading | worst relative deviation from D-ID's `T2/nominal/widths_nom/sigma_rel` | meets 1e-6 |
|---|---|---|
| OSB half-width at unit radius (ψ² = 1) | 1.52e-14 | yes |
| frozen-radius half-width ÷ ψ (**radius-normalized; binding**) | 1.51e-14 | **yes** |
| frozen-radius half-width compared literally | 2.1713323e-5 on every finite cell | no |

- **Hole sets are identical:** J 7, H2 11, EW 12.
- **Why the literal reading cannot pass.** Without positivity, OSB at radius ψ is exactly ψ·σ, and D-ID's `sigma_rel`
  is a unit-radius width. So the literal comparison fails by exactly ψ − 1 = 2.17e-5 on every finite cell, **for any
  correct solver**. The conflict is between PLAN §5.3's 1e-6 gate and the binding's radius amendment.
- **Ruling** (director, 2026-10-20; to be recorded in binding addendum 6): the radius-normalized reading binds, because
  it tests what the gate was written to test. It had been declared before the run. **The gate PASSES.**

## 4. Results with positivity

| group | treatment | n | finite | median | p90 |
|---|---|---:|---:|---:|---:|
| **J** | holes and unresolved as +∞ | 109 | 100 | **0.2859** | **1.2080** |
| **J** | D-ID's 7 holes excluded | 102 | 100 | **0.2612** | **0.9372** |
| J | holes and the 2 unresolved excluded | 100 | 100 | 0.2499 | 0.8717 |
| J | every non-finite set to 0 (most optimistic bound) | 109 | — | 0.2133 | 0.7929 |
| H2 (descriptive) | holes and unresolved as +∞ | 27 | 16 | 0.5299 | +∞ |
| H2 (descriptive) | D-ID's 11 holes excluded | 16 | 15 | 0.2248 | 1.3765 |
| H2 (descriptive) | holes and unresolved excluded | 15 | 15 | 0.1803 | 0.8754 |

- **Quantiles.** p90 is numpy's default (linear). For J, the lower/higher variants are 1.1842 / 1.3028 with holes and
  0.9142 / 0.9398 without. No radius or quantile choice moves a value across 10% or 25%.
- **Holes.**
  - All 7 J holes carry weight on a truth cell that never reaches reco (zero efficiency). Their upper bound is provably
    +∞, and none became finite.
  - In H2, 10 holes are of that kind. One (H2 row 17) became finite through an exact merge of two truth cells with
    proportional response columns.
- **Unresolved.** J117 min, J195 min and H2_9 min stopped short of the convergence tolerance and count as +∞, as
  declared. They cannot change the verdict.
- **Effect of positivity.** It barely helps. Over the 100 finite J functionals, the median ratio of constrained to
  unconstrained width is 0.9983 (minimum 0.807). The J median moves from 28.66% (the Cramér–Rao width) to 28.59%.
- **Per-functional values** are in `osb_table.csv` and `osb_functionals.json`; the summary is in `osb_summary.json`.

## 5. Cost

- **Result run:** 12,613 CPU-s over 1,729 s wall with 8 workers.
- **Total local use:** ≈ 31,500 core-s (8.8 core-h), against the 10 core-h cap.
- **Peak memory:** 2.88 GB, in the operand build.
- **Cluster:** 0 node-h, one read-only copy.

## 6. Not done, and UNCONFIRMED

- **Extras.** (a), the truth-rate share in holes, and (b), OSB at grid T3, were not run. (c) is in §6a.

## 6a. Extra (c): reco binning refined 2× per axis (descriptive; approved by the director after the verdict)

- **Construction.** Every fine reco bin of D-ID's binning is split at its arithmetic midpoint along each axis, with the
  outer edges unchanged. That gives 2,107,392 refined reco cells, 113,062 of them occupied, against 10,499 unrefined.
  The midpoint split is the session's reading of "split in two": it is the only parameter-free choice, but the frozen
  text does not fix it.
- **Code path.** Built with D-ID's own code: the same builder with its admission checks, `Diagnostic.problem`, then
  `did.response`, `did.fisher` and `did.widths_from_eig`.
- **Control.** The unrefined widths recomputed on the same path are bitwise equal to `tables.npz` at T1 and T2.
- **Cost.** 43 CPU-s, 3.17 GB peak, local. Code `measurement-paper/phase1/mp4a/extra_c.py`; outputs `extra_c.json`
  and `extra_c.log`.

1σ Cramér–Rao at unit radius, no positivity, relative to nominal:

| grid | group | unrefined median / p90 (holes +∞) | refined median / p90 (holes +∞) | unrefined median / p90 (holes excluded) | refined median / p90 (holes excluded) | per-functional refined/unrefined, median / p90 |
|---|---|---|---|---|---|---|
| **T2** | **J** (n 109, 7 holes) | 0.2866 / 1.1716 | **0.1083 / 0.3157** | 0.2516 / 0.8637 | **0.0975 / 0.2629** | 0.358 / 0.496 |
| T2 | H2 (n 27; holes 11 → 10) | 0.5397 / +∞ | 0.1563 / +∞ | 0.2254 / 1.0038 (n 16) | 0.0748 / 0.2649 (n 17) | 0.326 / 0.386 |
| T1 | J (n 109, no holes) | 0.1125 / 0.5843 | 0.0686 / 0.2200 | same | same | 0.579 / 0.754 |
| T1 | H2 (n 27, 1 hole) | 0.0295 / 0.0889 | 0.0152 / 0.0431 | 0.0254 / 0.0840 | 0.0130 / 0.0401 | 0.520 / 0.663 |

**Findings.**
- **J functionals at ≤ 10%** go from 32 to 54 at T2, and from 51 to 66 at T1.
- **Holes.** The 7 J holes are untouched: they are zero-efficiency truth cells, which no reco binning can fix. One H2
  hole closes: two truth cells shared one reco cell, and splitting that cell makes their columns no longer proportional.

**Reading.**
- The verdict above holds as frozen, at the analysis binning.
- A 2× reco refinement alone brings the J information floor to the edge of T1: median 10.8% with holes as +∞, or
  9.7% with them excluded, against 10%; p90 31.6% or 26.3%, against 25%.
- **The unbinned-information loophole is therefore material, not marginal.** Whether unbinned information could reach
  T1 is open. Positivity changes the binned J widths by only ≈ 0.2% at the median, so it does not close the gap.

**Why (c) is optimistic, not a bound.**
- The refined response comes from the same finite MC (≈ 180 events per occupied refined cell), and the Fisher treats R
  as exact, so MC fluctuations in R read as resolution.
- The case is signal-only and noise-free.
- T2, the bias/prior target, is a separate failure that (c) does not address.
- Sizing the loophole soundly would need a study that accounts for response-MC noise, for example with split-half
  responses. That is not part of MP4-A.
- **No independent second solver** was run on the real problem; the frozen scope allowed only scipy for production
  numbers. The primal–dual certificates are the internal check.
- **Signal-only and noise-free**, by design: no background, response-MC noise or s² slack. That makes a FAIL decisive
  and would have made a PASS only permissive.

## 7. Files

- **Code:** `measurement-paper/phase1/mp4a/`: `osb.py`, `run_mp4a.py`, `build_problem.py`, `synth_prototype.py`,
  `extras.py` (untested).
- **Outputs:** this directory:
  - the declarations: `DECLARATION.json`, `DECLARATION-v1.json`;
  - the gates: `gate.json`, `gate-v1.json`;
  - the results: `osb_summary.json`, `osb_functionals.json`, `osb_table.csv`;
  - the build and logs: `build_record.json`, `osb-run1-aborted.log`;
  - the synthetic prototypes: `synthetic_prototype_{bvls,trf}.json`, `synthetic_inner_method_compare.log`.
