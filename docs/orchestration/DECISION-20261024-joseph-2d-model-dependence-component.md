# DECISION 2026-10-24 — Joseph: report a 2D model-dependence component as a separate named covariance beside Q

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The measurement.** The 2D prior-variation test (`state/2d-closeout/stageF/methods/pv2d/REPORT.md`, PR #300;
  comparison PR #304) measured the envelope of the unfolded 2D result's dependence on the prior's shape, across
  GENIE+MEC, NuWro and GiBUU. Its median is 3.1 % per cell on the refined estimator, about 0.43 σ_Q, and it is in no 2D
  uncertainty construction (C09).
- **Joseph's question.** He asked whether our uncertainty without it matches MINERvA's, and whether MINERvA leaves it
  out because they "assume their model as true".
- **The director's answer.**
  - Q (median 6.45 %) is **comparable** to the published uncertainty (median 6.85 %), built the same way. "Matches"
    is too strong.
  - MINERvA **does** vary its model: "The uncertainties from individual sources are evaluated by re-extracting the
    cross section using modified simulations", arXiv:2106.16210, main.tex:376.
  - MINERvA chose its 10 iterations from a fake-data study of 10 GENIE-reweighted predictions, "Only statistical
    uncertainties were considered in determining the number of iterations" (main.tex:343-344), and assigns no
    uncertainty to the residual unfolding bias. That last point is the PRD study's reading of the full paper.
  - So "assume their model as true" is not accurate. The accurate contrast is that neither Q nor the published
    uncertainty carries the residual dependence on the prior's generator shape.
- **The director's proposal:**
  - keep Q as the headline 2D uncertainty, so the comparison with MINERvA stays like for like;
  - report the model-dependence term as a separate, named covariance beside Q, in the M2 form;
  - state the total for users, Q + C_model, which has a median of 7.69 % in quadrature;
  - put the exact paper wording to Joseph before it prints.

Joseph's answer, verbatim:

> yes that sounds like a plan

sha256 of the text plus a final newline begins `a68c05141f8b46d1`.

## What is decided

1. **Q, which becomes Q_R once RE-2 lands, stays the headline 2D uncertainty.** The reproduction comparison with
   MINERvA's published result is made with Q alone, like for like.
2. **C_model,2D is built and reported as a separate named covariance.**
   - **Form:** M2, C_model = Σ_k s_k s_kᵀ. There is one fully correlated component per generator vertex k (GENIE+MEC,
     NuWro, GiBUU), and s_k is that vertex's per-cell shift on the refined estimator from PV-2D.
   - **Scale:** κ = 1, unscaled and declared as such.
   - **Label:** "generator-shape model dependence; not a calibrated bound". In 2D, |shift| ≥ |bias| holds in 61 % of
     cells.
   - **Users** are given Q + C_model as the total.
   - **The tail caveat:** the cells beside the noise gate's reweighting steps (REPORT §5) go in as measured, and the
     caveat is stated.
3. **Wording.**
   - The comparison sentence must not say that MINERvA "assumes its model is true".
   - It says, in substance: like the published measurement, Q contains no component for the residual dependence on
     the prior; the published analysis chose its iteration count from a fake-data study and assigns no uncertainty to
     the residual. Iteration counts differ (10 there, 5 here), so no claim is made about the size of the published
     analysis's residual.
   - The exact printed wording goes to Joseph before it prints.
4. **Order.** C_model,2D is built from the existing PV-2D products, at 0 node-h, as a declared product with a review.
   It is integrated into the note, paper and primer with RE-2's rebuilt result.

## Not changed

- Claims beyond these items. The PV-2D numbers. No submission, deposit or tag.
