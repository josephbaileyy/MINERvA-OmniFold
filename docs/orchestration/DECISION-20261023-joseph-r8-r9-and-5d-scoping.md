# DECISION 2026-10-23 (fourth) — Joseph: RE-2 rebuilds 2D only, with HPSS for durable copies; scope a 5D measurement seriously

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The rulings on `RE2-PLAN` (`state/2d-closeout/stageF/methods/re2/RE2-PLAN-RULINGS.md`, PR #278)
put two questions to Joseph, each with alternatives:
- **R8, the scope of the rebuild:**
  - (a) 2D only, re-evaluating the extended-fiducial "reproduces σ_2D" sentence (recommended);
  - (b) also rebuild the extended-fiducial value with the refined estimator;
  - (c) also build a refined 5D covariance;
  - (d) drop the claim.
- **R9, durable copies:**
  - (a) HPSS (recommended; 161 GiB free, 350.9 of 512 GiB used, measured 2026-10-23 by `hpssquota`);
  - (b) a CFS exception;
  - (c) reproducibility only;
  - (d) Delta.

The director had also answered Joseph's question on what a 5D cross-section measurement whose uncertainty includes
model dependence would take, and whether it fits the GPU pool.

Joseph's answer, verbatim:

> okay lets do r8 (a) for now but I still want to try and scope out the 5d measurements as a serious possibility, r9 lets do (a)

sha256 of the text plus a final newline begins `91eec2ee7d927f02`.

## What is decided

1. **R8 (a):** RE-2 rebuilds the adopted 2D result only.
   - The extended-fiducial value stays on its purity N-D pipeline, labelled.
   - When `E_R` lands, `sec_fps.tex:47-52`'s "reproduces \sigTwoD" is re-evaluated against the new value, and the
     outcome is printed either way.
   - The 5D covariance stays configuration (a), as decided (DECISION-20261023 third, item 1).
2. **R9 (a):** RE-2's final products get durable copies on HPSS, after the lane's size estimate.
   - Each copy needs a recorded `hsi` hash verification.
   - Intermediates stay on pscratch until the integration. pscratch is at 85% (16.97 of 20 TiB) and purges idle
     files.
3. **A 5D measurement is scoped as a serious possibility.**
   - The measurement session writes a 5D measurement design (`state/measurement-paper/5d-design-20261023/`,
     `ASSIGNMENT.md` there).
   - It takes the model-dependence-included route the director outlined. It builds on the validation lane's scoping
     memo (PR #279), IBU-1 (PR #277), the GPU timing (`state/gpu-timing-20261023/REPORT.md`) and the s5p stage-2
     record with its amendment-6 correction.
   - The design runs nothing and authorizes nothing. Cheap decisive tests it proposes go through the usual
     declaration and binding.
   - Joseph's GPU-campaign criterion stands (DECISION-20261023 first, item 3): a large campaign only on a reasonable
     expectation of a measurement-quality paper.

## Not changed

- The frozen targets T1/T2 stand until Joseph changes them. The design must say plainly what it would need changed.
- No submission, deposit or tag. MP-2 stays held.
