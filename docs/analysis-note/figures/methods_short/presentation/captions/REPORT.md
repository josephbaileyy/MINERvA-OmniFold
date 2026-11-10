# Shortened captions: meaning and counts

Baseline: d1d60e74f. Captions and added citing-text sentences only; no result, table cell, data value or case key changed. Counts below use the same `texcount -sum -brief` method on standalone fragments, so math/control tokens are treated consistently before and after. They differ from the editor's prose-token counts.

| Figure | Before | After |
|---|---:|---:|
| fig:validation | 87 | 52 |
| fig:tension2d | 46 | 35 |
| fig:deformation | 163 | 64 |
| fig:bias-cells | 167 | 51 |
| fig:rounding-shifts | 152 | 65 |
| fig:prior-response | 152 | 65 |

## fig:validation

1. Original: Comparison with the published result~\cite{MINERvA:2021owq}.
   Disposition: Kept in shortened caption, including MINERvA citation.

2. Original: Top: $\pT$ and $\pPar$ projections of the published result and of this analysis, each with its total $\pm1\sigma$ band, and of the MINERvA Tune~v1, with ratios to the published result below.
   Disposition: Kept: published/unfolded bands distinguished from Tune v1 curve and ratios.

3. Original: The band of this analysis is the four-block covariance of section~\ref{sec:cov16}, without $C_{\mathrm{model}}$.
   Disposition: Kept, including sec:cov16 pointer and omission of C_model.

4. Original: Here the two bands are correlated, so their overlap is not a compatibility test.
   Disposition: Moved verbatim in meaning to sec:repro2d citing text, new paragraph beginning "The two bands in figure".

5. Original: Bottom left: $(\mathrm{OmniFold}-\mathrm{published})/\sigma_{\mathrm{published}}$ per reported bin, with cells drawn at equal size (grey: not reported).
   Disposition: Kept, including equal-size cells and unreported gray cells.

6. Original: Bottom right: median relative uncertainties and residual summary.
   Disposition: Kept.


## fig:tension2d

1. Original: Per-bin contribution $\Delta_{i}(\mathbf{C}^{+}\boldsymbol{\Delta})_{i}$ to the published-covariance $\chi^{2}$ of the two-dimensional result, where $\boldsymbol{\Delta}$ is its difference from the published result and $\mathbf{C}$ the published covariance, on the grid of reported $(\pT,\pPar)$ bins, numbered upward in momentum.
   Disposition: Kept with same Delta and covariance definition, grid and upward momentum ordering.

2. Original: The contributions sum to the $\chi^{2}$ and can be negative.
   Disposition: Kept.


## fig:deformation

1. Original: Recovery of generator-sized changes of the truth: the fractional residual, (unfolded $-$ truth)/truth, per $(\Eavail,W)$ cell, at each pseudo-experiment's changed truth, with backgrounds.
   Disposition: Kept residual sign, EW population and backgrounds.

2. Original: Neither panel shows the sixteen-cell result or its reported covariance.
   Disposition: Moved to sec:departure, paragraph immediately before sec:fd16, beginning "Neither panel of figure".

3. Original: (a) A lower-capacity variant of the five-observable estimator, not the reported estimator: its refinement has 100 trees and 8 leaves, the configuration with which the generator-sized-change study was run (\ssec{S4}{supp:estimators}); the truth is reweighted by the GiBUU/GENIE $\Eavail$ shape ratio (60 pseudo-experiments), and the grey step is the injected change of the cell truth.
   Disposition: Kept variant/configuration, truth, experiment count, injected step and S4 pointer.

4. Original: The reported estimator's result at this truth is on the sixteen cells, the GiBUU $\Eavail$ shape of table~\ref{tab:fd16}.
   Disposition: Comparison already in sec:departure paragraph beginning "Figure...shows" ("For the reported estimator at the same truth, we report the result on the sixteen cells"); table pointer retained in shortened caption.

5. Original: (b) The five-observable estimator, the reported one, for three shape changes not used while it was chosen (NuWro in $\Eavail$; GENIE + MEC in $(\Eavail,W)$; NuWro in $(\pT,\pPar,\Eavail)$), 20 pseudo-experiments each (\nsec{sec:eavailw-adopted}).
   Disposition: Kept three truths, reported estimator, experiment count and note pointer. Selection-timing clause moved to new sec:departure paragraph: "The three shape changes in panel (b) were not used while the estimator was chosen".

6. Original: In both panels, ``exp.'' in the key means pseudo-experiments.
   Disposition: Kept as exp.: pseudo-experiments.

7. Original: $W$ bin 6 is $W\ge\SI{3}{GeV}$.
   Disposition: Kept.

8. Original: Error bars are standard errors of the mean.
   Disposition: Kept.


## fig:bias-cells

1. Original: Fake-data bias of the reported five-observable estimator on the sixteen cells, at the twelve graded truths of table~\ref{tab:fd16}, in the same order.
   Disposition: Kept population via table pointer; exact count/order already in sec:fd16 citing paragraph beginning "To assess".

2. Original: Color gives the signed residual $z$, the mean fractional residual, (unfolded $-$ true)/true, divided by its uncertainty $\sqrt{\mathrm{diag}(C+N)}$, where $N$ is the noise covariance of that mean.
   Disposition: Moved to sec:fd16 new citing paragraph beginning "In figure", including definition of N.

3. Original: The noise-free closure uses its single residual and $N=0$.
   Disposition: Moved to same paragraph, verbatim.

4. Original: Left panel: the reported covariance, $C_{\mathrm{total}}+C_{\mathrm{resp}}+C_{\mathrm{PL,5D}}$.
   Disposition: Kept.

5. Original: Right panel: the covariance without the run-period block.
   Disposition: Kept.

6. Original: The table's $C_{\mathrm{total}}$-only reading is not shown.
   Disposition: Moved to same sec:fd16 paragraph: total-only reading given in table; caption specifies only reported and no-period panels.

7. Original: Each covariance omits the truth's own generator component as in the table.
   Disposition: Already in sec:fd16 citing paragraph "For a truth from a generator...the covariance omits that generator component".

8. Original: Numbers give the largest $|z|$ in each outlined row, to two decimals; in the left panel they are those of table~\ref{tab:fd16}.
   Disposition: Kept row maxima/two decimals/left-panel-table identity.

9. Original: Black outlines show only the per-cell criterion, $|z|>\fvval{trig-z}$.
   Disposition: Kept per-cell threshold macro.

10. Original: A truth can also be flagged by its $\chi^2$ $p$ value (table~\ref{tab:fd16}), as the synthetic $q_3$ tilt is under the reported covariance.
   Disposition: Already in sec:fd16 protected paragraph after table: "synthetic q3 tilt, by p alone" and p-versus-z criteria; untouched.

11. Original: The bias is identical in both panels; only the covariance differs.
   Disposition: Kept verbatim.

12. Original: An asterisk marks the simulation's own truth.
   Disposition: Kept; exact prior and Tune-v1 closure identities already in sec:fd16 citing paragraph.

13. Original: These tests assess only bias.
   Disposition: Already in sec:fd16 final paragraph: "These tests assess bias, not coverage: only event counts fluctuate, with the systematic parameters fixed".


## fig:rounding-shifts

1. Original: Rounding-level shifts of the reported five-observable estimator.
   Disposition: Kept as descriptive caption opening.

2. Original: The cumulative distribution shows, for each of the 153 quantities, the larger absolute shift under two rounding-level perturbations of the data, divided by the study's own data-bootstrap statistical standard deviation (100 refitted replicas; the reported statistical block uses 50, section~\ref{sec:cov5d}).
   Disposition: Kept larger-of-two definition and study100/reported50 distinction, including sec:cov5d pointer. Total153 stays in graph and citing paragraph population totals.

3. Original: The quantities are the 109 supported joint (J) cell integrals, all 42 $(E_{\mathrm{avail}},W)$ cells, including the three outside the support rule used in figure~\ref{fig:prior-response}, and two totals.
   Disposition: Moved to new sec:cov5d citing paragraph beginning "Figure...includes the 109", including Fig6 support-rule pointer.

4. Original: The edge-safe perturbations hold values on an analysis-grid edge fixed and move other inputs by at most half a float32 unit in the last place; the reference is the unperturbed inputs in float64.
   Disposition: Moved verbatim to same paragraph.

5. Original: Vertical lines mark the requirements fixed before the test: at most 0.3 statistical standard deviations for the median and 1.0 for the maximum.
   Disposition: Kept declared median/max requirements; timing also in sec:strategy grading-rules paragraph.

6. Original: The observed median and largest shift are marked, at the text's precision.
   Disposition: Kept markers, and labels remain same precision as protected B0 text.

7. Original: Points in this distribution are different quantities, not repeated experiments.
   Disposition: Kept.


## fig:prior-response

1. Original: Sensitivity to the prior of the reported five-observable estimator at five iterations.
   Disposition: Kept reported estimator and five iterations.

2. Original: The vertical axis gives the fractional change of the data result, using the reported estimator with its background refinement, when the simulation prior is reweighted to the NuWro $(p_T,p_\parallel,E_{\mathrm{avail}})$ shape.
   Disposition: Kept prior shape, data shift, background refinement.

3. Original: The horizontal axis is minus the noise-free residual, (unfolded $-$ true)/true, at that changed truth: this comparator uses signal-only simulation, with no background refinement, whereas the data result uses the reported estimator's background refinement.
   Disposition: Kept signal-only construction, sign and no-refinement distinction.

4. Original: Panels (a), (b) and (c) use the joint (J, 109), coarser joint (H2, 27) and $(E_{\mathrm{avail}},W)$ (EW, 39) cells defined in the companion note (\nsec{sec:gbdt-model-dependence}; \napp{sec:gbdt-diagnostic-definitions}); no panel is the sixteen-cell result.
   Disposition: Kept grid names/counts, section/appendix pointers and no-sixteen-cell qualification.

5. Original: Points are cells, not independent repeated experiments.
   Disposition: Moved to sec:stability/Discussion citing paragraph beginning "Two findings indicate", immediately following its Fig6 citation.

6. Original: The dotted line is $y=x$, for reference, with no fit.
   Disposition: Kept reference/no-fit meaning.

7. Original: The shifts measure sensitivity to the prior, not a measured bias of the data result.
   Disposition: Moved there: "The shifts are not a measured bias of the data result"; its sensitivity clause already in preceding sentence.

8. Original: The correlation supplies no per-cell bias bound (\nsec{sec:gbdt-model-dependence}).
   Disposition: Moved there verbatim with original note pointer.

## Verification

Every old caption ref/nsec/napp target remains in the revised caption or explicitly moved citing text. Citation MINERvA:2021owq and the S4 pointer remain. No fvval key was introduced; trig-z remains in Fig4. Protected B0 sentences and LISTED_CLAIMS paragraphs are unchanged. All sentence pairs are machine-readable in pairs.json. The integrator owns the meaning check and final caption choice.
