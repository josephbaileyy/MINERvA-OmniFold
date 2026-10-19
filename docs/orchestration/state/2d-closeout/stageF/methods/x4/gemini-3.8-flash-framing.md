### Part 1 — The Central Contribution

This paper’s central contribution is the first application of unbinned machine-learning deconvolution (OmniFold) to neutrino-nucleus scattering data (MINERvA medium-energy $\nu_\mu$ charged-current inclusive open data), establishing an end-to-end stress test of unbinned unfolding up to five dimensions and demonstrating full-chain Monte Carlo calibration of hypothesis tests under an explicit nuisance model despite substantial estimator bias. This contribution is carried by four core results: (1) reproducing the published two-dimensional $(p_T, p_\parallel)$ cross section to within 1.1% in total normalization; (2) demonstrating that an unbinned negative-weight background refinement reduces high-$W$ subtraction bias from 4% to below 0.3%; (3) exposing severe multidimensional failure modes, specifically an uncorrected regularization bias reaching 74% under generator-scale shape shifts and empirical coverage collapsing to 0.06 for nominal 68% statistical intervals; and (4) calibrating ten hybrid-null generator tests that incorporate prior pull and reject five generator configurations at the 5% familywise error level under stated conditions. 

As a Physical Review D methods paper, this is a strong and exceptionally timely study: experimental neutrino physics is actively pursuing high-dimensional unbinned cross sections, and a rigorous, unsparing demonstration of where unbinned deconvolution breaks down is far more valuable to the community than an unvalidated measurement claim. 

The paper would be made substantially stronger without any new physics results by elevating its most critical diagnostic findings—specifically the 74% GiBUU regularization bias and the 0.06 coverage failure—from brief prose into standalone figures, by providing an explicit algorithmic flowchart of the full-chain calibration, and by providing a defensible statistical justification for its sequential Monte Carlo stopping rules. 

What caps this paper as a methods paper is that the estimator's 10–13% model dependence and seed instability prevent it from delivering a validated five-dimensional measurement with total uncertainties, while the five-observable joint tests provide no demonstrated increase in statistical discrimination over matched coarse two-dimensional projections.

---

### Part 2 — The Section-by-Section Outline

#### Title Options
1. *Methodology, Regularization Biases, and Full-Chain Calibration of Multidimensional Unbinned Unfolding in Neutrino Scattering: An OmniFold Study of MINERvA Open Data*
2. *Unbinned Multidimensional Deconvolution and Calibrated Generator Hypothesis Tests in Neutrino Interactions with OmniFold*
3. *Performance and Limitations of High-Dimensional Unbinned Neutrino Cross-Section Unfolding: An Application to MINERvA Open Data*

---

#### Section I. Introduction
* **Main Point:** Unbinned machine-learning unfolding offers a route to simultaneous multidimensional neutrino cross sections, but its adoption requires rigorous empirical stress-testing of regularization bias, background subtraction, interval coverage, and hypothesis testing on real scattering data.
* **Existing Results, Numbers, and Figures:**
  * Citation of previous collider applications (H1 8 observables [4], ATLAS 24 observables [5], review [6]) and T2K simulation demonstration [7].
  * Context of MINERvA open-data release ($1.057 \times 10^{21}$ POT, $\langle E_\nu \rangle \sim 6\text{ GeV}$) [8, 9].
  * Overview of the five observables: $p_T, p_\parallel, E_{\text{avail}}, q_3, W$.
  * Summary of key outcomes: 2D reproduction to 1.1% normalization; 4% background bias reduced to $<0.3\%$; failure to meet 10% uncertainty target due to 10–13% model dependence; 10 calibrated hybrid-null rejections at $\alpha=0.05$.
* **Prose to Convert to Figure/Table:** None; retain as high-level introductory orientation.
* **Separation of Categories:**
  * *Observed results:* 1.011 normalization ratio to published data.
  * *Demonstrated validation properties:* Identification of regularization bias and background bias in simulation.
  * *Interpretive assumptions:* Framing ML deconvolution as density-ratio estimation in an unbinned feature space.

---

#### Section II. Data Sample, Kinematics, and Feature Definitions
* **Main Point:** The analysis selects 4.12 million MINERvA $\nu_\mu$ charged-current events and defines five truth and reconstruction observables that capture leptonic and hadronic kinematics, subject to specific kinematic constraints and an inherited pion-mass offset.
* **Existing Results, Numbers, and Figures:**
  * Sample sizes: 4.12 million data events, 32.8 million true signal simulation events (GENIE 2.12.6 + MINERvA Tune v1) [17, 18].
  * External generator predictions: GENIE 2.12.10 CV, GENIE + MEC (Valencia 2p2h) [19], NuWro 21.09 [20], GiBUU 2019 [21].
  * Target compositions: CH for data and GENIE; pure carbon for NuWro and GiBUU.
  * GiBUU sample truncation at $E_\nu \approx 20\text{ GeV}$.
  * Mathematical definitions: $p_T, p_\parallel, q_3 = |\vec{q}|$, $W = \sqrt{M^2 + 2M(E_\nu - E_\mu) - Q^2}$, and $E_{\text{avail}}$ (Eq. 1).
  * Impact of the inherited 135 MeV charged-pion subtraction: moves 0.67% of events to another bin, maximum true-bin shift of 1.05%.
  * Reconstructed calorimetric overlap: $E_{\text{avail}}, q_3$, and $W$ all depend on reconstructed hadronic recoil energy.
* **Prose to Convert to Figure/Table:** 
  * *New Table 1 (Observable and Kinematic Definitions):* Tabulate the 5 observables, their truth mathematical formulas, reconstruction definitions, struck-nucleon mass conventions ($M$), and kinematic boundary conditions.
* **Separation of Categories:**
  * *Observed results:* Event count (4.12 million selected data events).
  * *Demonstrated validation properties:* 0.67% migration from the 135 MeV pion definition in simulation.
  * *Interpretive assumptions:* Selection and fiducial volume definitions inherited from Ref. [9]; target differences (CH vs C).

---

#### Section III. Unbinned Deconvolution and Background Subtraction
* **Main Point:** OmniFold performs iterative density-ratio reweighting using gradient-boosted decision trees, where unbinned negative-weight background refinement substantially eliminates cell-level subtraction biases present in standard purity reweighting.
* **Existing Results, Numbers, and Figures:**
  * OmniFold setup: 5 iterations; LightGBM matched to scikit-learn capacity defaults; neural network cross-check (changes 3D total cross section by 0.8%, 1D projections by 0.7%–1.4%).
  * Purity-based target density $D(x)w_{\text{pur}}(b)$ vs unbinned negative-weight target $D(x) - B(x)$ with classifier refinement [22].
  * Purity-based subtraction bias: up to 4% in high-$W$ simulation cells (about $1\sigma$).
  * Unbinned refinement performance: reduces nominal truth bias to $<0.3\%$ (residual up to 1% in some joint cells; data difference at most 1.4%).
* **Prose to Convert to Figure/Table:**
  * *New Figure 1 (Background Subtraction Bias Comparison):* Plot the fractional residual bias $(F_{\text{unfolded}} - \text{Truth})/\text{Truth}$ in high-$W$ cells comparing the purity-based subtraction against the unbinned negative-weight refinement in nominal simulation pseudo-experiments.
* **Separation of Categories:**
  * *Observed results:* Difference between purity and unbinned background treatment on data (at most 1.4%).
  * *Demonstrated validation properties:* Reduction of simulation bias from 4% to $<0.3\%$ via unbinned classifier refinement.
  * *Interpretive assumptions:* Assumption that background templates and negative weights can be clipped at zero without distorting physics tails.

---

#### Section IV. Two-Dimensional Validation and Benchmark
* **Main Point:** The two-dimensional OmniFold extraction reproduces the published MINERvA cross section within 1.1% globally and exhibits a covariance-weighted distance of $\chi^2/\text{ndf} = 2.65$, with total uncertainties dominated by systematic universes and an empirical run-period spread.
* **Existing Results, Numbers, and Figures:**
  * Existing Figure 1 (top: $p_T$ and $p_\parallel$ projections with $\pm 1\sigma$ bands and Tune v1; bottom left: standardized residual 2D map; bottom right: summary metrics).
  * Integrated cross section: $3.073 \times 10^{-38}\text{ cm}^2/\text{nucleon}$ vs published $3.039 \times 10^{-38}\text{ cm}^2/\text{nucleon}$ (ratio 1.011).
  * Bin-by-bin agreement: 95.6% of 205 bins within 10%; standardized residual mean $= 0.074$, RMS $= 0.564$.
  * Covariance-weighted distance: $\chi^2/\text{ndf} = 2.65$ (LightGBM 10-seed range 2.64–2.75; exact-split scikit-learn 3.66 unseeded, 3.57 fixed seed).
  * Per-bin median relative uncertainty: 6.45% (OmniFold) vs 6.85% (published); integrated uncertainty 4.75% vs 4.61%.
  * Four covariance blocks: Systematic universes (median 87% of variance, flux median 3.75% vs published 4.01%), statistical bootstrap (300 replicas, median 0.684%, replica mean offset 0.26 standard deviations), training seed (5 seeds, median 0.06%, 70% variance uncertainty), and run-period block (median 2.1% per bin, 1.2%–3.4% on $p_\parallel$, 2.0% integrated).
  * Run-period inconsistency: 7% step near 8 GeV/$c$ in $p_\parallel$ between period groups.
  * Unfolding approximation: weighting of unreconstructed events tested in 2 universes, bounded at twice the training noise.
* **Prose to Convert to Figure/Table:**
  * *New Table 2 (Two-Dimensional Covariance Budget Breakdown):* Explicitly tabulate the median per-bin and integrated uncertainty contribution from each of the four covariance blocks, alongside the published MINERvA values.
  * Add the exact-split estimator comparison as a ratio curve directly onto Figure 1 (top panels).
* **Separation of Categories:**
  * *Observed results:* Integrated cross section ($3.073 \times 10^{-38}$); 7% step between run periods; 2.65 $\chi^2/\text{ndf}$ distance against published covariance.
  * *Demonstrated validation properties:* Training seed spread (2.64–2.75); failure of initial statistical bootstrap tail coverage (91.2% vs 95.4% at $2\sigma$) and post-hoc rescoring (97.7%).
  * *Interpretive assumptions:* Run-period block absorbs unexplained data differences by construction without establishing a physical systematic model.

---

#### Section V. Stress-Testing Multidimensional Unfolding: Regularization, Coverage, and Seed Stability
* **Main Point:** While higher-dimensional marginal normalizations remain consistent, unbinned unfolding exhibits severe regularization bias under generator-scale deformations, interval coverage failure, and seed instability, which prevent the extraction of a 5D measurement meeting a 10% precision target.
* **Existing Results, Numbers, and Figures:**
  * Marginal normalizations in 3D, 4D, and 5D agree with lower-dimensional projections at the 1%–2% level.
  * Closure tests with signal-only $E_{\text{avail}}$ reweighting successfully recover injected shape changes.
  * Regularization bias under GiBUU-to-GENIE reweighting: residual bias in unfolded $(E_{\text{avail}}, W)$ cells of several percent in largest cells and up to 74% at high $W$, persisting across iteration count and classifier capacity.
  * Other generator-shape biases: 16% to 31% in the most affected cell.
  * Rounding-level data input noise shifts unfolded results by up to several statistical standard deviations.
  * Coverage test failure (400 pseudo-experiments per truth): under an $E_{\text{avail}}$ tilt, 51 of 153 reported cell/projection integrals have 68% coverage confidently below nominal (falling as low as 0.06), and 42 fail at 95%; at nominal truth, 2 fail at 95% (lowest 0.85).
  * Random seed instability in 5D covariance: changing seed shifts projected $(E_{\text{avail}}, W)$ uncertainty by 6.145% (exceeding the 5% target limit); five fixed-seed bands contribute $\sqrt{\sum \text{Var}} / \sqrt{\text{Tr } C} = 26.0\%$.
  * Model dependence study: bounded model dependence (envelope over 5 generator truth changes) has a median of 13.4% in 39 $(E_{\text{avail}}, W)$ cells and 10%–13% per cell across all definitions, exceeding the 10% target half-width.
* **Prose to Convert to Figure/Table:**
  * *New Figure 2 (Regularization Bias and Shape Non-Closure):* Plot the 2D grid of $(E_{\text{avail}}, W)$ showing the percentage unfolding residual $[(F_{\text{unfolded}} - \text{Truth}_{\text{GiBUU}})/\text{Truth}_{\text{GiBUU}}]$ following GiBUU reweighting, explicitly displaying the 74% high-$W$ failure.
  * *New Figure 3 (Empirical Interval Coverage Breakdown):* Plot empirical coverage versus nominal confidence level (or bin index) for the 153 cell and projection integrals under the $E_{\text{avail}}$ tilt, highlighting the collapse to 0.06 coverage.
* **Separation of Categories:**
  * *Observed results:* Input rounding-level sensitivity on MINERvA data.
  * *Demonstrated validation properties:* 74% regularization bias; 0.06 coverage failure; 6.145% seed-induced uncertainty shift; 10%–13% median model dependence.
  * *Interpretive assumptions:* Pre-defining a 10% median half-width precision target as a threshold for publishing a measurement.

---

#### Section VI. Descriptive Five-Dimensional Central Values
* **Main Point:** The unbinned five-dimensional central value provides a granular descriptive view that isolates the known low-recoil enhancement and exhibits a localized excess at high $E_{\text{avail}}$ and high $W$ relative to MINERvA Tune v1.
* **Existing Results, Numbers, and Figures:**
  * Existing Figure 2 (Joint $(E_{\text{avail}}, W)$ projection relative to Tune v1: top ratio map, bottom cell-integrated difference map).
  * Existing Figure 3 (1D unfolded central-value projections of $E_{\text{avail}}$ and $W$ compared to GENIE CV, GENIE + MEC, NuWro, GiBUU, with data/prediction ratios).
  * Low-recoil region ($E_{\text{avail}} < 0.4\text{ GeV}$): underpredicted by GENIE, Tune v1, NuWro, and GiBUU.
  * MEC and FSI sensitivity: GENIE Valencia 2p2h fills 52% of the low-recoil data–GENIE gap; pion FSI variations change $d\sigma/dE_{\text{avail}}$ by $<1\%$.
  * Comparison to dedicated low-recoil measurement [26]: within 10% (ratios 1.09 and 1.06 in two common cells); 11% shift in lowest bin due to missing non-neutron particle species in truth definition.
  * High-$E_{\text{avail}}$, high-$W$ behavior: two thirds of positive difference relative to Tune v1 sits at $E_{\text{avail}} \ge 0.8\text{ GeV}$ and $W \ge 1.8\text{ GeV}$ (one fifth in the single overflow cell); data exceed Tune v1 by 12%–30% in these cells and by 23%–31% at $W < 1.1\text{ GeV}$.
  * External generator comparisons: integrated data-to-prediction ratios 1.07–1.39; GENIE and NuWro high-$W$ shortfalls (ratios 1.11–1.16) match their overall normalization shortfalls; GiBUU shortfall (1.61) matches overall shortfall once high-energy flux tail ($E_\nu > 20\text{ GeV}$) is accounted for.
* **Prose to Convert to Figure/Table:**
  * *New Table 3 (Integrated Cross-Section Normalizations and Domain Ratios):* Tabulate the integrated cross sections, data-to-prediction ratios, and the fraction of cross section in overflow bins for Data, Tune v1, GENIE CV, GENIE + MEC, NuWro, and GiBUU.
* **Separation of Categories:**
  * *Observed results:* Five-dimensional unbinned central values and projections; ratios to generator predictions.
  * *Demonstrated validation properties:* Coincidence of the high-$E_{\text{avail}}$, high-$W$ excess with the kinematic region where regularization bias is largest in simulation.
  * *Interpretive assumptions:* Attributing low-recoil gap filling specifically to Valencia 2p2h; treating the high-$E_{\text{avail}}$, high-$W$ feature as a statement relative to Tune v1 rather than a confirmed physical deficit.

---

#### Section VII. Full-Chain Calibrated Hypothesis Tests of Generator Predictions
* **Main Point:** By calibrating test statistics through pseudo-experiments that replicate the full analysis chain under an explicit nuisance model, the tests incorporate estimator prior pull and reject five hybrid generator hypotheses at $\alpha=0.05$, though these rejections are conditional on the simulated recoil response and intra-cell shapes.
* **Existing Results, Numbers, and Figures:**
  * Existing Table I (Joint-test decisions: $B$, $k$, $p = (k+1)/(B+1)$, Holm thresholds, Clopper-Pearson intervals; all 10 tests rejected at familywise $\alpha=0.05$).
  * Existing Figure 4 (Calibrated null distributions of $T_{\text{tot}}$ and $T_{\text{sh}}$ on log axes, observed test statistics, and non-centrality parameters $\lambda = 318 - 6344$).
  * Test setup: Coarse $3^5$ evaluation grid (109 supported cells; 72 for GiBUU); metric $\Sigma = V + \text{diag Var}(\mu_G)$ using Ledoit-Wolf shrunk covariance of 194 pilot pseudo-experiments.
  * Sequential stopping rule: batches of 200 up to 1999 pseudo-experiments; stopping when 99.5% Clopper-Pearson interval clears thresholds.
  * Six explicit conditions (Sec. VII B):
    (i) Hybrid null: fine-grid cells ($14 \times 16 \times 7 \times 7 \times 6$) use Tune v1 intra-cell shape; unproven convergence; shift by $\pm 2\delta_{\text{fine}}$ based on unrecorded geometric extrapolation; fine-grid $L_2$ step ratios (0.50–0.86).
    (ii) Detector model lacks calorimetric recoil-energy response band.
    (iii) 34 interaction-model uncertainty bands with clipped negative weights.
    (iv) Simulation split: pseudo-experiments use half-simulation, data use all (shift bound $\le 0.07\sigma_{\text{null}}$).
    (v) GiBUU flux truncation at 20 GeV.
    (vi) Prediction finite-sample variance in metric and residuals.
  * Robustness checks: shift multiplier scan up to $5.17\delta_{\text{fine}}$ maintains rejections; rerun of 224 interrupted calibration pseudo-experiments leaves decisions unchanged (closest approach 4.6 below observed statistic of 868.6).
  * Hadronic recoil sensitivity check: scaling reconstructed recoil energy by $\pm 4\%$ moves observed statistics by up to 11%; NuWro shape changes from $k=1$ to $k=3$ of 1751 ($p=0.0023$, below Holm threshold 0.05).
  * Coarse projection tests: matched 2D projections onto $(p_T, p_\parallel)$ and $(E_{\text{avail}}, W)$ both yield $p < 0.05$ for all models; GENIE CV is not rejected in $(p_T, p_\parallel)$ alone ($p = 0.48$ total, 0.63 shape).
  * Power studies: shape powers at Tune v1 null (1.0, 1.0, 0.23); shape powers at GENIE CV null (0.74, 0.02, 0.00).
* **Prose to Convert to Figure/Table:**
  * *New Figure 5 (Hadronic Response Sensitivity and Coarse Projections):* Plot the test statistic shifts under the $\pm 4\%$ recoil energy scaling relative to the null distributions, alongside the matched coarse-projection $p$-values.
* **Separation of Categories:**
  * *Observed results:* Rejection of the 10 hybrid nulls on data; observed $T_{\text{tot}}$ and $T_{\text{sh}}$ values; $p$-values in matched 2D projections.
  * *Demonstrated validation properties:* Non-centrality of null distributions under estimator prior pull; robustness to shift multiplier up to $5.17\delta_{\text{fine}}$; stability under rerun of lost pseudo-experiments.
  * *Interpretive assumptions:* The assumption that intra-cell variations along $\delta_{\text{fine}}$ bound within-cell generator differences; the assumption that a $\pm 4\%$ scale envelope approximates calorimetric response uncertainties.

---

#### Section VIII. Discussion and Methodological Outlook for Neutrino Physics
* **Main Point:** Unbinned deconvolution is a viable tool for exploratory multidimensional analysis and calibrated hypothesis testing, but delivering true unbinned cross-section measurements will require independent production-scale simulations, continuous nuisance models, and explicit regularization tuning.
* **Existing Results, Numbers, and Figures:**
  * Synthesis of failure modes: regularization bias (16%–74%), model dependence (10%–13%), statistical undercoverage (0.06), and seed variance (6.145%).
  * Evaluation of full-chain calibration as a general strategy to overcome estimator bias in scientific hypothesis testing.
  * Identification of required ingredients for future measurements: independent simulation samples of production size, validated continuous nuisance generators, test-beam calorimetric response covariance, and hyperparameter optimization targeting interval coverage.
* **Prose to Convert to Figure/Table:** None; conceptual synthesis and roadmap.
* **Separation of Categories:**
  * *Observed results:* Summary of data findings.
  * *Demonstrated validation properties:* Proven capabilities (2D benchmark, background refinement, calibrated testing) vs demonstrated failure modes (coverage breakdown, regularization bias).
  * *Interpretive assumptions:* Recommendations and prerequisites for future experimental programs.

---

### Part 3 — The Scope Statement and Caveat Audit

#### The Scope Statement (139 words)
All higher-dimensional unfolded distributions and calibrated hypothesis tests in this work are conditional methodological demonstrations evaluated under a specified detector and nuisance model. The three- to five-observable unfolded results are descriptive central values from a fixed-capacity LightGBM estimator; they do not possess validated frequentist interval coverage and do not constitute a cross-section measurement with a complete systematic uncertainty budget. The calibrated generator tests evaluate hybrid null hypotheses defined on a fine $14 \times 16 \times 7 \times 7 \times 6$ analysis grid with MINERvA Tune v1 intra-cell shapes, rather than raw generator models. All test calibrations and central values assume the detector response is fully described by the simulation and its 34 discrete model bands without an independent calorimetric recoil-energy systematic. Rejections establish incompatibility with these hybrid hypotheses under the stated nuisance model, but do not establish physical generator exclusions or demonstrate multidimensional discrimination beyond coarse two-dimensional projections.

---

#### Caveat Audit

1. **"Higher-dimensional results are central values only / descriptive only / no significance assigned"**
   * *Status:* **Collapses into the Scope Statement.**
   * *Rationale:* Once the scope statement formally defines all 3D–5D distributions as descriptive outputs of a specific estimator without asserted measurement uncertainties, repeating "central values only" on every page is redundant. The text can refer to them straightforwardly as "unfolded central values."

2. **"Absence of calorimetric recoil-response uncertainty in the nuisance model"**
   * *Status:* **Must stay at its claim in Section VII (and be introduced in the Scope Statement).**
   * *Rationale:* This is not merely an analysis premise; it is a critical physical limitation that directly controls the interpretation of the test results. Because GENIE CV is *not* rejected in the muon-only projection ($p=0.48$), its rejection relies entirely on hadronic variables. Readers examining Table I and Figure 4 must be reminded at that specific claim that the rejection is conditional on this missing detector uncertainty.

3. **"Hybrid null hypothesis / convergence below the fine grid unproven"**
   * *Status:* **Must stay at its claim in Section VII.**
   * *Rationale:* The tests do not evaluate the generator source code or physical models directly; they evaluate the generator binned on a fine grid with MINERvA Tune v1 filling the sub-grid phase space. This distinction is mathematically intrinsic to what the $p$-values mean and cannot be dismissed into a general opening caveat.

4. **"Estimator's pull toward its prior / strongly non-central null distributions"**
   * *Status:* **Must stay at its claim in Section VII.**
   * *Rationale:* This explains the actual physical shape and location of the null distributions in Figure 4 ($\lambda = 318 - 6344$). It is a demonstrated statistical mechanism of the full-chain calibration, not an interpretive qualification.

5. **"Joint 5D information is not shown to add discrimination beyond matched coarse projections"**
   * *Status:* **Must stay at its claim in Section VII and Section VIII.**
   * *Rationale:* This is an explicit, quantitative finding of the paper ($p < 0.05$ in matched 2D projections). It directly limits the methodological claim that 5D unfolding provides superior model-testing power compared to standard lower-dimensional approaches.

6. **"Detector response varies only within its parameterized family"**
   * *Status:* **Collapses into the Scope Statement.**
   * *Rationale:* This is a standard foundational assumption of all simulation-based forward-folding and deconvolution analyses in high-energy physics. Stating it once in the overarching scope statement is standard practice.

7. **"Statistical intervals miscover / no frequentist coverage claimed"**
   * *Status:* **Collapses into the Scope Statement for general framing, but specific quantitative findings must stay in Section V.**
   * *Rationale:* The general disclaimer that intervals lack coverage belongs in the scope statement. However, the specific empirical failure rates (coverage dropping to 0.06 under an $E_{\text{avail}}$ tilt across 51 of 153 integrals) must stay in Section V as a primary validation finding.

8. **"Run-period block contains differences by construction and does not identify the correct period"**
   * *Status:* **Must stay at its claim in Section IV.**
   * *Rationale:* This explains the exact mathematical construction of the 2D covariance matrix and prevents readers from interpreting the run-period block as a validated physics systematic or an endorsement of a specific run epoch.

9. **"Approximation in systematic-universe unfoldings regarding events that fail reconstruction"**
   * *Status:* **Collapses into the Scope Statement (or a single technical footnote in Section IV).**
   * *Rationale:* The manuscript notes that tests in two universes showed effects within simulation noise (bounded at twice the training noise). It is a minor technical approximation that does not warrant recurring caveats.

10. **"Inherited 135 MeV charged-pion subtraction constant rather than pion mass"**
    * *Status:* **Must stay at its claim in Section II.**
    * *Rationale:* This defines the exact kinematic observable $E_{\text{avail}}$ being unfolded. Because external theorists must reproduce this exact observable to compare against the data, the definition and its 0.67% migration impact must be explicitly recorded where the feature is defined.

11. **"Pion FSI and Valencia 2p2h interpretations are model-dependent statements relative to Tune v1"**
    * *Status:* **Must stay at its claim in Section VI.**
    * *Rationale:* Stating that Valencia 2p2h fills "52% of the gap" could easily be misquoted as a physical measurement of multinucleon contributions. Keeping the caveat at the claim ensures it is understood as a descriptive model comparison.

12. **"GiBUU sample truncation at $E_\nu \approx 20\text{ GeV}$ and NuWro/GiBUU carbon vs hydrocarbon target differences"**
    * *Status:* **Must stay at its claim in Section II and Section VI/VII.**
    * *Rationale:* These are concrete differences in the input generator samples that directly explain why GiBUU falls further behind at high $W$ and why normalizations differ. They must accompany the comparisons.

---

### Part 4 — The Abstract

We apply OmniFold, an unbinned machine-learning deconvolution technique, to MINERvA open data for medium-energy $\nu_\mu$ charged-current inclusive interactions. Benchmarked against the published double-differential cross section in muon kinematics ($p_T, p_\parallel$), the method reproduces the total cross section to 1.1% and 95.6% of bins within 10%, exhibiting a covariance-weighted distance $\chi^2/\text{ndf} = 2.65$. Extending the unfolding to five simultaneous kinematic and calorimetric observables ($p_T, p_\parallel, E_{\text{avail}}, q_3, W$) yields consistent marginal normalizations while revealing substantial methodological limitations: an unbinned background refinement reduces high-$W$ subtraction bias from 4% to below 0.3%, but severe regularization bias (up to 74%) persists under generator-scale shape deformations, statistical intervals fail frequentist coverage (reaching 0.06), and a 10%–13% model dependence prevents a measurement with total uncertainties. Full-chain Monte Carlo calibration enables hypothesis testing under an explicit nuisance model despite estimator bias, rejecting five hybrid generator hypotheses at the 5% familywise level. These tests demonstrate full-chain calibration for biased multidimensional estimators while highlighting key prerequisites for future unbinned measurements.

*(Word count: 153 words)*

---

### Part 5 — Treatment of the Earlier Referee Report's Major Comments

#### Comment 1: Primary scientific result and framing
* **Verdict:** **(a) Answers it by framing alone.**
* **Action:** The recast systematically repositions the paper as a methodological investigation of unbinned unfolding and full-chain calibration on neutrino data. The 3D–5D results are explicitly designated as descriptive central values and stress tests rather than an unvalidated measurement, exactly matching the referee's recommended second path.

#### Comment 2: Calorimetric response omission
* **Verdict:** **Combination of (a) Framing for methods paper, (b) Minor analysis/presentation, and (c) Later physics paper.**
* **Action for Methods Paper:** 
  * *(a) Framing:* The scope statement and Section VII explicitly condition all generator rejections on the simulation's nominal calorimetric response, clearly stating that exclusions do not hold outside this fixed detector model.
  * *(b) Minor analysis:* Present the existing $\pm 4\%$ exploratory scaling study in a dedicated summary table or figure panel (New Figure 5), explicitly stating that while this sensitivity check leaves test decisions intact, it is an exploratory scale envelope rather than a true propagated detector covariance.
* **Belongs to Physics Paper:** *(c)* Generating a full, test-beam-calibrated, particle- and energy-dependent hadronic response covariance and propagating it through the pseudo-experiment calibration chain belongs entirely to the subsequent measurement paper.

#### Comment 3: External-generator null hypotheses are hybrid nulls
* **Verdict:** **Combination of (a) Framing and (b) Analysis/computation.**
* **Action for Methods Paper:**
  * *(a) Framing:* Consistently use the terminology "hybrid null hypothesis $H_0(G)$" throughout the title, abstract, and text; remove any claim of excluding the raw physical generators; treat MINERvA Tune v1 separately as the only exact null.
  * *(b) Computation:* Eliminate the unrecorded geometric extrapolation assumption for $\delta_{\text{fine}}$. Instead, transparently document the empirical $L_2$ refinement ratios (0.50–0.86) and report the shift-multiplier scan up to $5.17\delta_{\text{fine}}$ strictly as an empirical sensitivity parameterization along the last refinement vector, admitting that orthogonal intra-cell variations remain unconstrained.
* **Belongs to Physics Paper:** *(c)* Generating full detector-level simulations directly from external generators (NuWro, GiBUU) without hybridization belongs to the future measurement paper.

#### Comment 4: Familywise error control and sequential stopping
* **Verdict:** **(b) Needs analysis or computation even for a methods paper.**
* **Action for Methods Paper:** The authors must provide a rigorous, transparent statistical description of the sequential calibration:
  1. Formally specify the multi-look stopping protocol: pseudo-experiments ran in batches of 200 up to 1999, stopping when the 99.5% Clopper-Pearson interval cleared the Holm threshold.
  2. Address alpha-spending: compute or demonstrate via bounding arguments [inference] that using an inner 99.5% Clopper-Pearson stopping criterion before applying the outer 95% decision threshold preserves the nominal type-I error rate, or soften "controlled at familywise $\alpha=0.05$" to "calibrated to an empirical sequential threshold designed to conservatively bound familywise error."
  3. Formally justify why the computing budget extension did not bias the Monte Carlo $p$-values (i.e., that the stopping boundaries were not adapted based on observed test statistics).
  4. Clarify that drawing nuisance parameters calibrates a *nuisance-averaged* test size under the prior, rather than guaranteeing Neyman coverage for every point in nuisance parameter space.

#### Comment 5: Interaction-model uncertainties under a fixed-generator null
* **Verdict:** **(b) Needs analysis or computation even for a methods paper.**
* **Action for Methods Paper:** The manuscript must include an explicit, step-by-step generative algorithm (pseudocode or procedural text in Section VII A) defining exactly what occurs in each pseudo-experiment:
  1. *Truth level:* Truth events are drawn with weights defining hypothesis $H_0(G)$ on the fine grid, holding the true cross section fixed to $G$.
  2. *Reconstruction/Detector level:* The 34 interaction-model and detector systematic bands are applied as reweighting factors affecting migration, selection efficiency, and background templates, but *normalized* such that they do not alter the target fine-grid truth cross section $G$.
  3. Specify the exact mathematical treatment of clipped negative weights and the 1.4% normalization uncertainty.

#### Comment 6: Full-chain calibration validation as an approximation
* **Verdict:** **Combination of (a) Framing and (b) Analysis/computation.**
* **Action for Methods Paper:**
  * *(a) Framing:* Acknowledge that the calibration uses a half-simulation split (due to computational constraints) as an operational approximation, bounded by the $+0.07\sigma_{\text{null}}$ mean shift.
  * *(b) Computation:* Document whether the 194 pilot pseudo-experiments used for the Ledoit-Wolf metric $\Sigma$ are completely independent of the production calibration ensembles, and demonstrate that the joint test exhibits nominal size ($p \sim \text{Uniform}(0,1)$) when evaluated on simulated pseudo-data generated under the null.
* **Belongs to Physics Paper:** *(c)* Rerunning all calibration pseudo-experiments using the full 100% simulation statistics belongs to the later measurement paper.

#### Comment 7: Validation of higher-dimensional distributions (regularization bias & coverage)
* **Verdict:** **(b) Needs analysis or computation even for a methods paper.**
* **Action for Methods Paper:** These critical negative results must be brought into the visual core of the paper:
  1. Create a dedicated figure (New Figure 2) displaying the $(E_{\text{avail}}, W)$ distribution of the residual unfolding bias under GiBUU truth reweighting, visually highlighting the 74% high-$W$ failure.
  2. Create a dedicated figure (New Figure 3) plotting empirical coverage against nominal coverage across the 153 tested integrals, showing the collapse to 0.06 coverage under the $E_{\text{avail}}$ tilt.
  3. Explicitly define the deformations used in the 3- and 4-observable closure tests and specify their quantitative acceptance criteria.

#### Comment 8: Kinematic dependence, collinearity, and truth definitions
* **Verdict:** **Combination of (a) Framing and (b) Minor computation.**
* **Action for Methods Paper:**
  * *(a) Framing:* In Section II, state the exact kinematic equations connecting $(p_T, p_\parallel, q_3, W, E_{\text{avail}})$, explicitly explain that $q_3, W$, and $E_{\text{avail}}$ share calorimetric recoil energy, and describe the physical boundaries of the supported 5D phase space. Clarify the struck-nucleon mass convention ($M$) for bound and multi-nucleon states.
  * *(b) Minor computation:* Quantify the numerical impact of the inherited 135 MeV charged-pion subtraction across all reported kinematic bins (confirming it moves $\le 0.67\%$ of events overall and $\le 1.05\%$ in any bin), and provide the explicit domain masks for the 109 supported cells (72 for GiBUU).

#### Comment 9: Two-dimensional reproduction framing and run-period step
* **Verdict:** **Combination of (a) Framing and (b) Minor analysis.**
* **Action for Methods Paper:**
  * *(a) Framing:* Strictly describe $\chi^2/\text{ndf} = 2.65$ as a "covariance-weighted descriptive distance" rather than a formal test of statistical compatibility; disclose the choice of LightGBM over exact-split as a pragmatic alignment with the covariance estimator without defensiveness; clearly characterize the run-period block as an empirical uncertainty envelope rather than a validated systematic model.
  * *(b) Minor analysis:* Plot the exact-split scikit-learn result directly on Figure 1 as an alternative curve to transparently display the learner dependence (median 0.98%, max 12.2%).

#### Comment 10: Coherent uncertainty definitions
* **Verdict:** **(b) Needs analysis or computation even for a methods paper.**
* **Action for Methods Paper:**
  1. Provide formal mathematical definitions for the four covariance blocks in Section IV B ($C = C_{\text{syst}} + C_{\text{stat}} + C_{\text{seed}} + C_{\text{run}}$), defining the probability space and resampling mechanics of each.
  2. Mathematically define the 6.145% seed shift metric (relative change in projected trace or bin-average uncertainty between seed instances) and explain the trace metric ($\sqrt{\sum \text{Var}_{\text{fixed}}} / \sqrt{\text{Tr } C} = 26.0\%$).
  3. Reframe the 13.4% model dependence as an empirical envelope across five specific generator variations, rather than a universal bound on unfolding bias, and explicitly state that failing the 10% target represents an internal benchmark failure for this specific configuration.

#### Comment 11: Descriptive physics interpretations
* **Verdict:** **(a) Answers it by framing alone.**
* **Action for Methods Paper:** 
  * Reframe all discussion in Section VI strictly as descriptive comparisons of the unfolded central value against MINERvA Tune v1 and external models.
  * Replace claims of "separating the remaining discrepancy" with descriptive statements about localized rate differences.
  * Explicitly qualify the 52% gap filling by Valencia 2p2h as an illustrative model feature rather than a physical measurement of MEC.
  * Explicitly emphasize the target differences (CH vs C) when comparing data to NuWro and GiBUU, and note that adding the high-energy tail to GiBUU is an empirical sensitivity check rather than a true GiBUU prediction.

#### Comment 12: Article completeness and release readiness
* **Verdict:** **(b) Needs concrete computation and engineering actions.**
* **Action for Methods Paper:**
  1. Move all essential definitions, formulas, and domain masks from the repository analysis note directly into the main text and appendices of the paper.
  2. Remove all internal project placeholders (`[HOLD: funding...]`, `[HOLD: deposit identifier...]`).
  3. Update the 16 MB candidate release package to ensure it contains the current LightGBM 2D curves (removing the obsolete exact-split curve), domain masks, covariance matrices, and replay scripts that reproduce every figure and table in the recast paper from scratch.

---

### Part 6 — Guidance for the Authors Before Starting

1. **Embrace the Methods Framing as an Intellectual Upgrade, Not a Downgrade**
   Do not treat this recast as a face-saving fallback or an apologetic retreat. In modern high-energy physics, machine-learning deconvolution methods are frequently published with superficial closure tests that mask severe failure modes. A rigorous, unsparing PRD paper that demonstrates an unbinned 5D application on real scattering data—while transparently exposing 74% regularization bias, 0.06 interval coverage collapse, seed instability, and the lack of added 5D discrimination—will be an essential, heavily cited reference. Neutrino cross-section physics desperately needs this paper to establish the benchmark criteria that any future unbinned measurement must meet.

2. **Avoid "Disclosure as Absolution"**
   The earlier referee report explicitly warned against using transparent disclosure to excuse methodological shortcomings. In the previous draft, the prose repeatedly confessed limitations, disclaimed coverage, and noted unmeasured effects, but then proceeded to claim 5% familywise rejections of generator families. In the recast, align the claims strictly with what is demonstrated:
   * Do not say: *"We reject the five generators, but note that the recoil response uncertainty is missing."*
   * Say: *"Under a nuisance model that conditions on the simulation's nominal calorimetric recoil response, the hybrid null hypotheses built from five generator predictions are rejected."*
   State your scope once, formally and cleanly, and write the rest of the manuscript with calm, objective precision.

3. **Treat the Sequential Testing with Absolute Statistical Rigor**
   The earlier report’s critique of sequential Monte Carlo stopping is technically incisive. If you report $p = (k+1)/(B+1)$ derived from sequential batches stopped via Clopper-Pearson intervals, you are operating a multi-stage sequential test. You cannot assert exact 5% Holm familywise error control without demonstrating that the sequential stopping rule does not inflate alpha. Either provide the bounding argument that your 99.5% stopping threshold makes alpha-spending negligible, or rephrase your statistical claim: describe the tests as *calibrated multi-stage hypothesis tests with conservative stopping thresholds* rather than claiming a formal, unadjusted 5% familywise frequentist guarantee.

4. **Clean House in the Release Package**
   A paper whose primary contribution is methodological transparency will be judged by the reproducibility of its release package. Shipping a package with an obsolete 2D curve, missing figures, or broken replay scripts will invite immediate skepticism. Ensure the 16 MB candidate package runs out of the box in an empty environment, contains the exact LightGBM outputs, and reproduces every number in your text and tables.

5. **Maintain Authorial Voice in AI Tool Documentation**
   The manuscript contains an unusually detailed disclosure of AI tool usage (Claude, GPT models). While transparency is commendable and adheres to emerging editorial standards, ensure that this documentation remains strictly confined to the Acknowledgments. The main text must read with the authoritative, rigorous, and skeptical voice of experimental neutrino physicists who have personally verified every calculation against the underlying data and simulation.
