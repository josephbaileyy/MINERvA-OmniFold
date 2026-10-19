# Plain-language pass 2: prompts and reports, verbatim
**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-19. The prompts given to the outside models and every report of pass 2 ([`../PLAIN-LANGUAGE-PASS2.md`](../PLAIN-LANGUAGE-PASS2.md)), copied verbatim from the director's session scratchpad, except that every heading is demoted two levels so this file keeps one title. Each item's sha256 (of the scratchpad original) is given with it. The outside runs used `run_x.sh` (this directory): agy `gemini-3.8-flash-high` and codex-school `gpt-6.1-sol` in a read-only sandbox, each prompt followed by the input files named in the report.
**CITABLE FOR:** what each model and agent was asked, found and did. **NOT CITABLE FOR:** a decision or a fact about the analysis. The outside models saw only the paper and primer text; their statements are advice and contain errors (some are listed in the integration reports). The dispositions are in [`../PLAIN-LANGUAGE-PASS2-IMPLEMENTATION.md`](../PLAIN-LANGUAGE-PASS2-IMPLEMENTATION.md).

---

## P1. Prompt: outside referee report (round 1) (sha256 `5cf83a2015ed1b2c…`)

You are an experienced referee for Physical Review D in experimental neutrino physics: you have worked on neutrino-nucleus cross-section measurements (MINERvA, T2K, NOvA or MicroBooNE), know iterative/D'Agostini unfolding and its regularization, multi-universe systematic uncertainties, covariance-based chi-squared tests, pseudo-experiment calibration and coverage, and the OmniFold method. You have never seen this project.

Below is the full text of a manuscript submitted to PRD (extracted from the PDF, so equations and figure text may be garbled). Write a referee report.

Part 1 — the standard report: summary of what the paper claims; assessment of significance and novelty; major comments; minor comments; recommendation. Be candid. Judge the physics and the support for each claim, not only the writing.

Part 2 — presentation, because the authors specifically asked for it. They worry the paper is written in an over-defensive, process-record register (stacked negations, internal project vocabulary, project history in the body) rather than the way PRD papers in this field are usually written. For each section: does it read like a PRD paper? Quote the worst passages exactly and show how an experienced author in the field would write the same content. Keep every limitation the authors disclose — do not make the paper claim more than it does — but say where a limitation is stated more often, or more prominently, than it deserves.

Part 3 — the abstract. It is about 230 words. (a) Which of its sentences carry the paper's headline results, and which are qualifications? (b) Write the abstract you would expect for this paper in 120–160 words, in PRD style, keeping the results and only the limitations a reader must know not to misread them. (c) List what you dropped and where in the body it should be stated instead.

Part 4 — anything else you think the authors need to hear.

---

## P2. Prompt: paragraph main-idea and outline analysis (round 1; Gemini run used the no-tools variant) (sha256 `85cbdd0cb20c83de…`)

Do not use any tools, commands or files: everything you need is in this message. Answer directly, in text, in full.

You are an expert scientific editor for physics journals (PRD/PRL) and a former experimental particle physicist. Two documents follow, extracted from PDFs: a research paper (for Physical Review D) and a plain-language primer on the same work (for a physics-literate non-specialist).

Do a structural analysis of each document, independent of sentence-level style.

1. Paragraph main-idea map. For every paragraph (number them by section, e.g. IV.B.3), give its main idea in one sentence of at most 25 words. Mark a paragraph:
   - [NONE] if it has no single main idea you can state;
   - [MULTI] if it carries two or more unrelated ideas;
   - [HIST] if its main idea is the history of the analysis (what was done earlier, changed, rebuilt) rather than the final method or result;
   - [CAVEAT] if its main idea is a limitation;
   - [RESULT] if its main idea is a result;
   - [METHOD] if its main idea is the method.
2. The argument outline. From the map, reconstruct the document's actual line of argument in 8–15 bullets. Then give the outline a typical PRD paper of this kind (an unfolding measurement plus generator tests) would follow, and say where this paper departs from it and whether the departure helps or hurts.
3. Proportions. Estimate the fraction of text spent on results, method, caveats and history, per section and overall. Say whether the balance is appropriate for the genre.
4. Repetition. List every limitation that is stated more than once, with each location. For each, say where the single best place to state it would be.
5. The abstract of the paper: list its sentences, label each as headline result or qualification, and say what a 120–160-word abstract would keep. Explain why an abstract of this kind tends to grow when authors are trying hard to be honest, and how to stop that.
6. For the primer only: does the order of sections and paragraphs serve a non-specialist? Propose a better order if there is one, in a list of section and paragraph headings.

Be concrete; quote short phrases to identify paragraphs.

---

## P3. X1 Gemini 3.8 Flash: referee report on the pass-1 paper (sha256 `8e3e523afbf6bcb1…`)

### Review of Manuscript PRD / Bailey & Nachman

**Title:** *Multidimensional unbinned unfolding of MINERvA inclusive charged-current neutrino data: validation and calibrated model tests*  
**Authors:** Joseph Bailey and Benjamin Nachman  
**Referee:** Experienced Reviewer in Experimental Neutrino Physics (Neutrino–Nucleus Cross Sections / MINERvA, T2K, NOvA, MicroBooNE)

---

#### PART 1 — THE STANDARD REFEREE REPORT

##### 1. Summary of Claims and Methodology

This manuscript presents the first application of an unbinned, machine-learning-based deconvolution technique (OmniFold) to experimental neutrino–nucleus scattering data. Using the MINERvA open-data release of medium-energy $\nu_\mu$ charged-current (CC) inclusive interactions on hydrocarbon ($1.057 \times 10^{21}$ protons on target, $\langle E_\nu \rangle \sim 6\text{ GeV}$, $4.12 \times 10^6$ selected data events), the authors pursue three related goals:

1. **Two-Dimensional Benchmark:** Reproduce the published MINERvA double-differential cross section in muon kinematics, $d^2\sigma/(dp_T\,dp_\parallel)$ [PRD 104, 092007 (2021)], using gradient-boosted decision trees (LightGBM) within the iterative OmniFold framework. The authors construct a four-component covariance matrix (systematics universes, bootstrap statistics, training-seed variance, and run-period stability).
2. **Higher-Dimensional Extension:** Extend the unfolding to five simultaneous kinematic variables: muon transverse momentum $p_T$, muon longitudinal momentum $p_\parallel$, available hadronic energy $E_\text{avail}$, three-momentum transfer $q_3$, and hadronic invariant mass $W$. The authors present central values for 3D, 4D, and 5D distributions and compare projections against four external generator models (GENIE 2.12.10 with and without Valencia 2p2h, NuWro 21.09, and GiBUU 2019).
3. **Calibrated Hypothesis Testing:** Recognizing that internal covariance validation criteria could not be met for a 5D cross-section measurement (due to machine-learning seed instability and large regularization bias), the authors construct an alternative inference framework: simulation-calibrated goodness-of-fit tests of the five generator predictions evaluated on a coarse 109-cell grid in 5D. Pseudo-experiments simulate the full analysis chain (including prior pull, background refinement, and systematic nuisance variations). Under six explicitly stated conditions, all ten tests (total rate and normalized shape for each of the five models) reject the models at the familywise $\alpha = 0.05$ level via the Holm step-down procedure.

---

##### 2. Assessment of Significance and Novelty

**Novelty:**  
This work represents a milestone in neutrino cross-section methodology. While OmniFold and related unbinned deconvolution methods have matured in collider physics (H1, ATLAS) and have been demonstrated on mock neutrino simulation (Huang et al., PRD 112, 012008 (2025)), this is the first deployment on real neutrino data. Neutrino cross-section measurements face acute challenges absent at colliders: non-monochromatic beams, complex nuclear environments (2p2h, RPA, final-state interactions), and secondary hadronic interactions inside heavy target nuclei where reconstructed calorimetric observables share overlapping information. Demonstrating how unbinned unfolding behaves under these realistic conditions is of high interest to the PRD readership.

**Methodological Rigor and Candor:**  
The authors deserve commendation for exceptional technical transparency. Rather than concealing the failure of the 5D covariance matrix to achieve predefined stability thresholds, or downplaying the substantial regularization bias observed when testing generator-level shape distortions (up to 74% bias in high-$W$ cells under GiBUU injection), the authors document these failure modes in detail. This level of candor is rare and provides vital practical guidance for the community.

**Physics Impact:**  
The physics impact of the cross-section results themselves is modest. The 2D result replicates a known measurement. The 5D central values recover the established low-recoil ($2\text{p}2\text{h}$) enhancement and show an excess over MINERvA Tune v1 at high $E_\text{avail}$ and high $W$; however, because no validated covariance matrix is provided, these 5D distributions cannot be used quantitatively for generator tuning. Furthermore, the hypothesis tests reject models that were already known to be disfavored by the published 2D data, and the authors explicitly demonstrate that the joint 5D test provides no statistically significant discrimination beyond matched coarse 2D projections.

Consequently, this paper is primarily a **methodological benchmark and diagnostic study**, not a standalone measurement of new physics. The paper will be well-received by PRD if it is framed consistently in this manner.

---

##### 3. Major Comments

###### Major Comment 1: Missing Calorimetric Hadronic-Response Systematic in the Joint Tests
In Section VI.D, the authors disclose that the nuisance model used to calibrate the null distributions in the generator tests does not include a calorimetric hadronic energy response uncertainty (such as the test-beam-derived single-particle energy response uncertainties of 4–10% standard in MINERvA analyses; NIM A 789, 28 (2015)). 

This is a critical physics omission:
* The observables $E_\text{avail}$, $q_3$, and $W$ all depend directly on the calorimetric recoil energy.
* In Section VI.D, the authors note that when the calibrated tests are restricted to the $(p_T, p_\parallel)$ projection (which depends solely on muon tracking and spectrometry), **GENIE 2.12.10 CV is not rejected ($p = 0.48$ total, $p = 0.63$ shape)**. 
* Therefore, the rejection of GENIE CV in the 5D test is driven entirely by the hadronic recoil axes—precisely where the leading experimental systematic uncertainty has been omitted.
* While the exploratory $\pm 4\%$ global scale test in Sec. VI.D is a useful check, real calorimetric uncertainties are particle-dependent (protons vs. charged pions vs. neutrons), non-linear, and asymmetric due to neutron energy leakage. The authors must state prominently in the abstract, introduction, and conclusion that the formal rejections of the generator models on the hadronic axes are conditional on the simulation's unperturbed calorimetric response model.

###### Major Comment 2: Regularization Bias and OmniFold Prior Dependence
The closure tests with injected generator differences (Sec. IV.C) reveal that when the true distribution is warped by the ratio of GiBUU to GENIE, the unfolded result deviates from the target by up to 74% in high-$W$ cells (and 16–31% for other generators), persisting across tested iteration counts and tree capacities.
* In traditional iterative D'Agostini unfolding, a 74% residual bias in a closure test would disqualify the binning or iteration choice, or mandate a large unfolding model-dependence systematic uncertainty.
* The paper should provide physical insight into *why* OmniFold fails to recover this shape: Is it due to low reconstructed event density at high $W$? Is it the decision tree's inability to split correlated calorimetric features? Or is it an intrinsic property of stopping at 5 iterations (early stopping acting as excessive Tikhonov-like shrinkage)? 
* Connecting this failure to the underlying physics of neutrino interaction modeling is essential for readers planning to apply OmniFold to T2K, MicroBooNE, or DUNE data.

###### Major Comment 3: Machine-Learning Seed Variance as an Experimental Systematic
In Section VII, the authors report that varying the random seed of the BDT training shifts the projected 5D uncertainty by 6.15% (which failed their predefined 5% criterion), and in Section IV.A, switching between LightGBM seeds shifts the 2D $\chi^2/\text{ndf}$ against published data between 2.64 and 2.75, while changing from LightGBM to scikit-learn exact-split changes $\chi^2/\text{ndf}$ to 3.57–3.66.
* This is a fundamental finding: machine-learning training stochasticity is not negligible in comparison to Poisson statistical uncertainties or subleading systematics.
* The authors should formulate clear guidance for the field: How many ensemble seeds are required to suppress this variance below the statistical floor? Can seed-averaging of the density ratio (bagging the unfolded weights) stabilize the estimator prior to covariance evaluation?

###### Major Comment 4: Status of Central Values vs. Measurement
The manuscript displays 5D unfolded central-value distributions in Figs. 2 and 3 and discusses their features (e.g., excesses at high $E_\text{avail}$ and high $W$, 2p2h filling 52% of the gap). Yet in Section VII, the authors state that a 5D measurement could not be defined with acceptable uncertainties, and Section V warns that "these statements are descriptive. No significance is assigned."
* Publishing central-value cross sections without associated covariance matrices is generally discouraged in PRD because experimental data points without uncertainties cannot be used in global fits or generator tuning.
* The authors must make the distinction crystal clear: Figs. 2 and 3 should be explicitly identified as *unvalidated proof-of-concept demonstrations*, and the data release must clearly flag them as uncalibrated central values not intended for cross-section database ingestion (e.g., HepData).

###### Major Comment 5: Clarification of the Pion Mass Constant (135 MeV) in $E_\text{avail}$
Equation (1) defines $E_\text{avail}$ by subtracting a constant of 135 MeV from charged-pion energies, rather than the physical charged-pion mass $m_{\pi^\pm} \approx 139.57\text{ MeV}$. The authors state: *"We have not corrected this constant."*
* The text must explain *where* this constant originated. Was it an upstream legacy definition in the MINERvA AnaTuples / Analysis Toolkit, or an implementation error in the authors' analysis scripts?
* While the authors demonstrate that the effect is small (<1% bin migration), leaving the phrase "We have not corrected this constant" unexplained gives an impression of carelessness. State clearly whether this was done to preserve backward compatibility with existing MINERvA open-data definitions.

---

##### 4. Minor Comments

1. **Title:** The title is accurate but somewhat dry. "Multidimensional unbinned unfolding of MINERvA inclusive charged-current neutrino data: validation, limitations, and calibrated model tests" would better reflect the prominent methodological caveats.
2. **Equation (1):** Please define $Q^2$ in the definition of $W$ immediately preceding Eq. (1) for completeness ($Q^2 = 2 E_\nu (E_\mu - p_\parallel) - m_\mu^2$ or $-q^2$).
3. **Figure 1 (Bottom Left):** The 2D residual map $(N_\text{OmniFold} - N_\text{pub})/\sigma_\text{pub}$ uses an equal-area grid for variable-width bins. Please label the axes clearly with physical bin units or explicitly note in the caption that bin areas are normalized for display purposes.
4. **Figure 2:** In the ratio panel (top), please specify whether the denominator is GENIE 2.12.6 with MINERvA Tune v1. The overflow bin ($E_\text{avail} \to 100\text{ GeV}$, $W \to 100\text{ GeV}$) accounts for 20% of the cross-section excess; the physical origin of this (deep-inelastic scattering / unmodeled high-energy hadron showers) deserves a brief sentence.
5. **Ledoit–Wolf Shrinkage:** In Section VI.A, the covariance $V$ is estimated with Ledoit–Wolf shrinkage from 194 pilot toys. Briefly state the target matrix used for shrinkage (e.g., diagonal empirical covariance).
6. **Sub-fine-grid Convergence Metric (Condition i):** The parameter $\delta_\text{fine}$ is defined as the shift in the noise-free unfolded result during the last grid refinement. Clarify the mathematical definition of the $L_2$ norm used to evaluate this ratio.
7. **References [25], [32], [33], [34], [35], [37], [38], [39]:** Several references point to internal repository records (e.g., `RECORD-20261005-s5p...`, `W1-RECORD...`). For a formal archival journal like PRD, these should be consolidated into the published Analysis Note (Ref. [14]) or an archived Zenodo/data repository rather than bare GitHub commit hashes.
8. **Editorial Placeholders:** Remove the bracketed editorial tags `[HOLD: funding and grant acknowledgments]` in Acknowledgments and `[HOLD: deposit identifier...]` in Data Availability before publication.

---

##### 5. Recommendation

**Major Revision.**  
This manuscript represents high-quality, innovative computational and experimental physics that addresses a critical forward-looking challenge in neutrino physics. However, the manuscript suffers from a severe stylistic problem (it reads like an internal audit investigation rather than a PRD physics paper) and requires technical tightening regarding the omitted calorimetric systematic and the presentation of the 5D distributions. Once revised to meet standard PRD scientific register and framing, this paper will be a valuable and highly cited contribution.

---

#### PART 2 — PRESENTATION AND EDITORIAL REGISTER

The authors explicitly requested feedback on the tone and register of the paper. They are completely right to be concerned. 

As currently written, large portions of the paper read like an **internal quality-assurance audit**, a **git commit incident report**, or a **defensive legal deposition**. The prose is characterized by:
* Stacked negations ("cannot exclude", "does not establish", "neither establishes recovery nor coverage").
* Over-defensive disclaimers repeated four or five times across different sections.
* Internal project-management jargon ("frozen contract", "claim variant", "reviewers of the design", "exception to the criteria", "predefined criteria").
* Computational triage history in the main text (e.g., describing batch job timeouts, recovering lost seeds, extending computing budgets).

In a peer-reviewed PRD paper, scientific rigor is demonstrated by presenting methods, assumptions, and validation metrics cleanly and dispassionately. The paper must state its limitations clearly, but it should state them **as physical boundaries of the method**, not as confessions of administrative non-compliance.

Below is a section-by-section analysis with exact quotations of the worst offending passages and concrete examples of how an experienced experimentalist would rewrite them for PRD.

---

##### Section I: Introduction

###### Critique
The Introduction oscillates between presenting the work as an exciting multi-observable measurement and anticipating every conceivable referee criticism by preemptively listing all limitations. The final paragraph of Section I (p. 1–2) delivers a devastating litany of disclaimers that undermines reader confidence before any physics or methodology has been explained.

###### Quote 1 (Section I, p. 2, col. 1):
> *"The higher-dimensional central values agree in normalization with the lower-dimensional results they extend and recover the known low-recoil discrepancy; the three- and four-observable central values also pass closure tests with injected shape changes. Pseudo-experiments that include backgrounds, however, reveal a background-subtraction bias of up to 4 % in simulation in the highest-W cells. An unbinned treatment, used only for the generator tests, largely removes it; the quoted uncertainties do not include it. The unfolding also recovers only part of a change of the Eavail shape as large as the difference between generators. This regularization bias, the dependence on the estimator’s random seed, and the untested coverage limit the method, and the measured model dependence prevents a five-dimensional measurement with total uncertainties that meet our predefined criteria at useful precision."*

###### PRD Rewrite:
> *"While the higher-dimensional unfolded central values reproduce the lower-dimensional marginal distributions and capture established nuclear features—such as the low-recoil enhancement—validation studies reveal important methodological challenges. In particular, we identify a background-subtraction bias of up to 4% at high invariant mass $W$ when using binned purity corrections, which is mitigated by an unbinned negative-weight treatment. Furthermore, closure tests with alternative generator shapes indicate non-negligible regularization bias and estimator seed variance in five dimensions. Consequently, rather than quoting an unvalidated five-dimensional cross-section covariance matrix, we deploy the five-dimensional framework in a simulation-calibrated hypothesis-testing mode to evaluate generator predictions directly."*

*Why this is better:* It conveys exactly the same technical limitations without the panicked, apologetic tone. It frames the decision not to quote a 5D covariance as a principled scientific choice rather than a failed contractual obligation.

---

##### Section II: Data, Signal, and Simulation

###### Critique
The discussion of the 135 MeV pion subtraction constant in Eq. (1) is written in an overly defensive, confessional manner ("We have not corrected this constant... this effect has not been compared with the full covariance").

###### Quote 2 (Section II, p. 2, col. 2):
> *"in which protons contribute kinetic energy, charged pions their energy minus an inherited constant of 135 MeV rather than the charged-pion mass, and neutral pions and photons their total energy; all other final-state particles, including neutrons, contribute nothing. We have not corrected this constant. Relative to the charged-pion mass, in a simulated sample it moves 0.67 % of events into another true-Eavail bin and changes no true-Eavail bin by more than 1.05 %; this effect has not been compared with the full covariance."*

###### PRD Rewrite:
> *"where protons contribute kinetic energy, neutral pions and photons contribute total energy, and charged pions contribute kinetic energy approximated via an offset of 135 MeV (inherited from the upstream MINERvA AnaTuple conventions) rather than the physical charged-pion mass $m_{\pi^\pm} \approx 139.57\text{ MeV}$. In simulation, this nominal definition shifts only 0.67% of events across true-$E_\text{avail}$ bin boundaries, altering individual bin contents by at most 1.05%, which is negligible compared to the leading systematic uncertainties."*

*Why this is better:* It explains *why* the 135 MeV value is there (an inherited convention from the open-data format) and quantifies its impact concisely without the hand-wringing apology.

---

##### Section IV.A: Two-Dimensional Reproduction

###### Critique
The authors describe their decision to switch from an exact-split BDT to LightGBM in terms that sound like a confession to a research-misconduct committee regarding post-hoc decision making.

###### Quote 3 (Section IV.A, p. 3, col. 2):
> *"We quote the LightGBM result as the central value, so that it uses the same estimator as its covariance. This choice, which replaced the exact-split result, was made after both comparisons were known. The two differ by a per-bin median of 0.98 % (maximum 12.2 %), and this learner dependence is not included in any term of the covariance."*

###### PRD Rewrite:
> *"To ensure internal consistency between the central value and the systematic-universe covariance evaluation, the nominal result is evaluated using LightGBM. A comparison against an exact-split decision-tree implementation reveals a median per-bin difference of 0.98% (reaching 12.2% in peripheral bins), reflecting the sensitivity to classifier architecture and feature binning. This difference illustrates the learner-dependent uncertainty inherent to machine-learning unfolding, which is not captured in standard detector or flux systematic variations."*

*Why this is better:* It highlights the important physical and methodological point (classifier architecture sensitivity) without sounding like a defendant admitting to p-hacking under cross-examination.

---

##### Section IV.B: Two-Dimensional Uncertainty and Its Coverage

###### Critique
This subsection contains the densest concentration of destructive audit language. The authors explain in detail that an earlier version of their code had a bug, that they rebuilt the band, that rescoring it was circular, and that their run-period check "is not a test" and "says nothing about its coverage."

###### Quote 4 (Section IV.B, p. 4–5):
> *"Because the block is built from the differences among the periods, it contains them by construction; this says nothing about its coverage, that is, whether its size is right. For the same reason, the block’s own consistency check passes whatever the data, and it is not a test... An earlier version of the statistical band undercovered in its tails in 100 closure pseudo-experiments, specified in advance, against a fixed truth: pooled over experiments and bins, 91.2 % of standardized residuals fell within two standard deviations, against 95.4 % nominal. The main cause, a division by the completeness that the bootstrap replicas carried and the central value does not, was removed in a rebuilt band. Rescoring the same pseudo-experiments against the rebuilt band is post hoc and partly circular... A review of the stored analysis products found errors in an earlier version of the uncertainty budget, among them a mismatch between the truth input of its systematic-universe unfoldings and that of their reference, and statistical fluctuations of the background templates that were not propagated [25]; the quoted covariance is free of both."*

###### PRD Rewrite:
> *"The run-period systematic block accounts for observed temporal variations across beam epochs, exhibiting a median per-bin uncertainty of 2.1%. By construction, this component encompasses the empirical epoch-to-epoch scatter, though it does not formally guarantee frequentist coverage in the presence of unmodeled detector drifts. 
> 
> The statistical covariance matrix is evaluated via 300 bootstrap replicas of the data and simulation streams. In initial closure evaluations using simulated pseudo-experiments, standard bootstrap construction yielded minor tail undercoverage (91.2% within $2\sigma$ versus 95.4% nominal). Refining the bootstrap estimator to handle reconstruction completeness consistently resolved this tail undercoverage, yielding empirical intervals that conservatively envelope statistical fluctuations. The resulting statistical and systematic covariances cleanly propagate all template and universe variations as detailed in Ref. [14]."*

*Why this is better:* 
1. Readers do not need a diary of the intermediate buggy iterations of the code that were fixed before submission.
2. It treats the run-period covariance as an empirical systematic envelope (standard practice in MINERvA and T2K) rather than declaring it "not a test."

---

##### Section VI.A & VI.C: Calibrated Joint Tests and Batch Job Recovery

###### Critique
Section VI includes detailed descriptions of committee oversight ("reviewers of the design"), computing budget allocation decisions, and a blow-by-blow narrative of batch jobs hitting NERSC wall-clock limits and being recovered in a secondary run. This belongs in a lab notebook or internal technical note, not PRD.

###### Quote 5 (Section VI.A, p. 8, col. 1):
> *"Two parts of the procedure were informed by the data. The reviewers of the design had seen descriptive per-cell residuals before it was fixed. A bounded extension of the production computing budget was decided while the outputs of the computing jobs showed the observed p values used for the decisions; it changed no statistic, shifted null, threshold, or stopping rule, and the Monte Carlo p values remain valid at the number of pseudo-experiments reached."*

###### Quote 6 (Section VI.C, p. 8, col. 2):
> *"Batch-job time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments. Had every interrupted one exceeded the observed statistic, no test would have been rejected. We therefore reran the lost pseudo-experiments after the decisions, outside the decision rule, with a procedure fixed and independently reviewed beforehand [34]; it first reproduced 16 completed pseudo-experiments exactly. None of the recovered pseudo-experiments reaches the observed statistic in any test or shifted null. Every submitted pseudo-experiment has now been observed, and no assignment of the lost outcomes changes any decision."*

###### PRD Rewrite for VI.A & VI.C:
> *"The hypothesis-testing protocol, test statistics, null shifts, and familywise error control were specified prior to generating the production calibration ensembles. To ensure robust statistical power while controlling computational cost, pseudo-experiments were evaluated in sequential batches up to a maximum of 2000 per hypothesis, stopping when Clopper–Pearson intervals unambiguously determined rejection relative to the Holm thresholds.
> 
> Due to batch-queue execution limits, a subset of pseudo-experiments experienced job timeouts during the initial campaign. Completing these jobs in a secondary run confirmed the stability of the ensemble: across all completed pseudo-experiments ($B = 1343\text{--}1751$ per model), no simulated pseudo-experiment approaches the observed test statistic in any of the rejected channels. The test outcomes are therefore completely robust against ensemble completion effects."*

*Why this is better:* It explains the sequential batching and job completion cleanly as a numerical validation step, completely stripping away the legalistic "outside the decision rule" and "reviewers of the design" vocabulary.

---

##### Section VII: Status of a Five-Dimensional Uncertainty

###### Critique
This section reads like an ISO-9001 compliance audit finding where an engineer confesses to using a part under an "authorized variance."

###### Quote 7 (Section VII, p. 10, col. 1):
> *"We have built a covariance for the five-dimensional central value and formed its 42-cell (Eavail , W ) projection; it is separate from the joint-test calibration. It has not met the criteria that the analysis set in advance for an uncertainty. One of these criteria requires a bound fixed before the covariance was produced and can no longer be applied to it. We use the covariance only under an exception to the criteria, recorded in the analysis note and limited to this one covariance. We quote no covariance-based generator significance, because covariances from this estimator depend measurably on its random seed."*

###### PRD Rewrite:
> *"We investigated the feasibility of constructing a full five-dimensional systematic covariance matrix for the unfolded cross section. However, extensive validation revealed that the evaluated uncertainties exhibit unacceptable sensitivity to the estimator’s internal training seed: varying the random seed produces a 6.1% shift in the projected uncertainty, which failed our a priori stability criterion of 5%. Furthermore, this variation does not scale down with increasing ensemble size (remaining at ~6% across 40 to 160 draws). In addition, addressing the large observed model-dependence bias would require an uncertainty band that exceeds the target precision of the measurement. 
> 
> Because an uncertainty matrix must be stable under nuisance variations and estimator stochasticity, we conclude that a five-dimensional cross-section measurement with a validated covariance matrix is not currently achievable with this estimator configuration. This limitation directly motivated our development of the simulation-calibrated hypothesis-testing framework in Sec. VI."*

*Why this is better:* It explains the technical reason (seed instability and model-dependence bias) with dignity, framing the pivot to hypothesis testing as a rational scientific response to empirical findings.

---

##### Acknowledgments and Data Availability

###### Critique
The Acknowledgments section lists an exhaustive catalog of AI models and version numbers (e.g., "Opus 4.7, 4.8, 5, and 5.5; Fable 5 and 5.1; GPT-5.5, GPT-5.6 Sol and Luna, GPT-6 Astra, and GPT-6.1") and discusses their role in "independent reviews." Meanwhile, Data Availability includes unfulfilled template directives like `[HOLD: deposit identifier...]`.

###### PRD Rewrite:
> *"We gratefully acknowledge the MINERvA Collaboration for providing their open-data AnaTuples and analysis framework [8, 15], and thank Callum Wilkinson and Kevin McFarland for valuable discussions and suggestions regarding detector response validation. This research used resources of NERSC under DOE contract DE-AC02-05CH11231. LLM-based coding assistants were utilized during the development of analysis scripts and documentation. The authors verified all mathematical derivations, code implementations, and final results, and take full responsibility for the contents of this work."*

---

#### PART 3 — THE ABSTRACT

##### (a) Classification of Current Abstract Sentences

The submitted abstract consists of 10 sentences (~230 words). Here is the breakdown:

1. **Sentence 1 (Context/Scope):** *"We test the practical limits of multidimensional unbinned unfolding with OmniFold on MINERvA open data for medium-energy νµ charged-current inclusive interactions."*  
   $\rightarrow$ **Headline/Scope.**
2. **Sentence 2 (Headline Result 1):** *"The analysis reproduces the published double-differential cross section in muon kinematics and extends it to five simultaneous observables by adding available energy, three-momentum transfer, and hadronic invariant mass."*  
   $\rightarrow$ **Headline Result.**
3. **Sentence 3 (Headline Result 2):** *"The higher-dimensional central values pass checks of their marginal normalizations against the lower-dimensional results, and the three- and four-observable central values pass closure checks with injected shape changes."*  
   $\rightarrow$ **Headline Result.**
4. **Sentence 4 (Qualification 1):** *"Pseudo-experiments that include backgrounds, and studies of the uncertainties, show limitations of the background treatment, the regularization, the interval coverage, and the stability under changes of the estimator’s random seed."*  
   $\rightarrow$ **Qualification.**
5. **Sentence 5 (Qualification 2):** *"The measured model dependence prevents a five-dimensional measurement with total uncertainties that meet our predefined criteria at useful precision."*  
   $\rightarrow$ **Qualification / Negative Result.**
6. **Sentence 6 (Headline Result 3):** *"Generator tests, calibrated with pseudo-experiments that rerun the full analysis chain under a stated nuisance model, reject all five tested predictions (MINERvA Tune v1, GENIE 2.12.10 with and without Valencia two-particle–two-hole contributions, NuWro 21.09, and GiBUU 2019) in total and in shape at the 5% familywise level."*  
   $\rightarrow$ **Headline Result.**
7. **Sentence 7 (Qualification 3):** *"These rejections hold only under stated conditions."*  
   $\rightarrow$ **Qualification.**
8. **Sentence 8 (Qualification 4):** *"The tests recover known discrepancies, but they do not show that the tested joint five-observable information discriminates beyond matched coarse projections of the same cells."*  
   $\rightarrow$ **Qualification / Physics Assessment.**
9. **Sentence 9 (Qualification 5):** *"Their physical interpretation is limited because the nuisance model has no calorimetric recoil-response uncertainty and because convergence of the fine grid on which the null hypotheses are defined has not been shown."*  
   $\rightarrow$ **Qualification / Systematic Limitation.**

**Summary:** Only 3.5 sentences carry headline results (what was done and discovered); 5.5 sentences are stacked qualifications, disclaimers, and negative statements.

---

##### (b) Recommended PRD-Style Abstract (142 words)

> We report the first application of unbinned multidimensional unfolding to experimental neutrino–nucleus data, using the OmniFold technique on the MINERvA open-data sample of medium-energy $\nu_\mu$ charged-current inclusive interactions. The method successfully reproduces the published double-differential cross section in muon kinematics ($p_T, p_\parallel$) and provides simultaneous central values across five kinematic observables by incorporating available hadronic energy, three-momentum transfer, and invariant mass. Extensive validation using simulated pseudo-experiments reveals key practical challenges: non-negligible regularization bias under alternative generator shapes, classifier seed variance, and sensitivity to background modeling at high invariant mass. These effects prevent quoting a five-dimensional cross section with a validated covariance matrix. Instead, we perform simulation-calibrated hypothesis tests that account for estimator prior bias and nuisance variations; these reject five standard generator predictions at the familywise 5% level. We discuss the implications of missing calorimetric recoil uncertainties and outline requirements for future multidimensional unbinned cross-section measurements.

---

##### (c) List of Dropped Items and Where They Belong in the Body

The following details were removed from the abstract to achieve a concise, professional PRD abstract:

1. **Specific enumeration of all five generator model tunes** (*MINERvA Tune v1, GENIE 2.12.10 with/without Valencia 2p2h, NuWro 21.09, GiBUU 2019*):  
   *Where it belongs:* Section II (Data and Simulation) and Section VI.A (Joint Tests). In the abstract, "five standard generator predictions" is standard PRD style.
2. **"These rejections hold only under stated conditions"**:  
   *Where it belongs:* Section VI.B (Conditions). It is redundant in an abstract; all scientific measurements hold under stated conditions.
3. **Explicit mention that 5D tests do not discriminate beyond matched coarse projections**:  
   *Where it belongs:* Section VI.C (Results) and Section VIII (Conclusions). This is a nuanced finding about statistical power and binning granularity that requires context to interpret properly.
4. **Specific technical failure mechanisms** (*"convergence of the fine grid on which the null hypotheses are defined has not been shown"*; *"predefined criteria at useful precision"*):  
   *Where it belongs:* Section VI.B (for the fine-grid sub-cell convergence) and Section VII (for the seed stability threshold). An abstract should state the scientific conclusion (a 5D covariance could not be validated), not quote internal project metrics.

---

#### PART 4 — WHAT ELSE THE AUTHORS NEED TO HEAR

This section contains candid, experienced advice for the authors as they prepare this work for publication.

##### 1. You Have Solved a Real Problem, but You Are Writing Like You Are on Trial
Reading this manuscript, one gets the unmistakable impression of authors who have spent months adhering to strict, blinded pseudo-experiment protocols and are terrified of being accused of $p$-hacking, cutting corners, or overselling machine learning. 

You have leaned so far into self-policing that you have obscured your own achievements:
* You successfully took real, messy, detector-level neutrino data and demonstrated that OmniFold reproduces published MINERvA 2D cross sections within ~1%. That is a major accomplishment!
* You discovered that unbinned unfolding in neutrino physics encounters severe obstacles that collider physics does not see: overlapping calorimetric variables, low-purity background regions at high $W$, seed instability in tree boosting, and strong regularization bias when the true nuclear physics deviates from the training MC.
* **This is not a failure of your analysis; this is the primary scientific contribution of your paper.** 

Do not write about these findings as if you failed an audit. Write about them as **new empirical discoveries about the behavior of machine-learning deconvolution in neutrino physics**.

##### 2. Clarify the Experimental Status of the 5D Distributions
In the neutrino community, presenting unfolded cross-section distributions without uncertainties (Figs. 2 and 3) is a lightning rod for referee criticism. Theorists will digitize your plots and compare them to their models; experimentalists will complain that you are showing unphysical results.
* You must make a clean editorial choice: Either frame Section V strictly as an *exploratory demonstration of classifier feature space* (and make sure the plots are labeled "Illustrative Central Values; see Sec. VII for uncertainty status"), or move these figures into the validation section to demonstrate feature capture (e.g., showing that the network successfully captures the 2p2h dip).
* Never leave readers wondering whether you are offering these curves as a new measurement of neutrino cross sections. Be explicit that the primary physics inference is delivered through the calibrated hypothesis tests in Section VI.

##### 3. The Hadronic Calorimetry Issue Will Determine Your Reception in the Neutrino Community
If this paper is reviewed by a MINERvA, NOvA, or MicroBooNE experimentalist, their immediate focus will be on Section VI.D: *Where is the calorimetric energy scale uncertainty?*
* Neutrino physicists know that MINERvA's calorimetric response to low-energy hadrons and neutrons is the single hardest systematic in the experiment. Because your joint tests reject GENIE CV only when the hadronic axes are included, omitting the full test-beam calorimetric response systematic makes the hypothesis test vulnerable to the charge of being an artifact of detector mismodeling.
* Frame this limitation with complete transparency, but without defensiveness: state that while muon kinematics are fully constrained by detector systematics, full 5D hypothesis testing requires integrating non-linear calorimetric response variations into the training pipeline—a fruitful challenge for future studies.

##### 4. Clean Up Software Development Artifacts and LLM Cataloging
* The detailed catalog of LLM model versions (Opus, GPT-5.6 Sol, GPT-6 Astra) in the Acknowledgments reads like science fiction or an internal AI benchmarking log. Follow PRD’s standard policy on generative AI: include a clean, two-sentence acknowledgment stating that AI tools were used for code development and draft editing under human oversight.
* Remove all repository commit hashes, internal document labels (`RECORD-...`), and `[HOLD: ...]` placeholders. Replace them with standard citations to your publicly accessible GitHub repository, archived Zenodo release, or the companion Analysis Note.

##### Summary
You have done the hard, honest work that the machine-learning and neutrino communities desperately need. Now, rewrite the manuscript with the confidence, clarity, and professional voice of experienced experimental physicists. The paper will be vastly stronger for it.

---

## P4. X1 GPT-6.1-sol: referee report on the pass-1 paper (sha256 `073807cea4251551…`)

**Part 1 — Referee report**

**Summary and overall assessment.** The manuscript applies OmniFold to MINERvA medium-energy inclusive charged-current neutrino data. It compares a two-observable unfolding with the published muon-kinematic measurement, extends the estimator to five observables, investigates background subtraction and regularization, and constructs generator tests calibrated through repeated execution of the analysis chain.

The principal positive results are approximate reproduction of the published two-dimensional central values; consistency of higher-dimensional marginal normalizations; recovery of selected injected distortions in three- and four-observable tests; and substantial reduction of a demonstrated background-subtraction bias using unbinned background refinement. The principal negative results are substantial regularization bias for some generator-sized deformations, unresolved interval coverage, and instability of the higher-dimensional uncertainty estimate. The generator comparisons reject the simulated null hypotheses under the adopted calibration procedure, but their interpretation is limited by the missing calorimetric recoil-response uncertainty and the unresolved dependence on structure below the fine truth grid.

This is potentially a useful methodological paper. It is not yet a validated five-dimensional cross-section measurement, and the manuscript generally acknowledges that distinction. Its strongest contribution is the investigation of what fails, and why, when an unbinned unfolding implementation is extended to this dataset.

My recommendation is **major revision**. The changes needed concern the statistical and physical support for the conclusions, as well as presentation. My assessment is based on the supplied manuscript; I have not audited the companion analysis products.

**Significance and novelty.** An application of unbinned unfolding to neutrino-scattering data would be interesting. The practical treatment of backgrounds, efficiency, systematic universes, and regularization in a sample of this size is relevant to future measurements.

However, counting observables is not sufficient to establish the advance. The manuscript does not demonstrate improved physics discrimination over matched coarse projections, does not deliver a validated higher-dimensional uncertainty, and recovers generator disagreements already observed in the published MINERvA measurement. Those are appropriate boundaries on its novelty.

A carefully supported study of these limitations could merit publication. It would need to establish which failures arise from the chosen implementation, which reflect limited detector information or released inputs, and which are general concerns for unfolding. The present evidence does not establish a limitation of OmniFold as a method, or the impossibility of a useful multidimensional measurement with these data.

**Major comments**

1. **The claimed dimensionality requires a more precise physical explanation.**

   The statement that the reconstructed observables share inputs understates a potentially exact kinematic redundancy. For a massless incoming neutrino along the longitudinal axis,
   \[
   q_3^2=p_T^2+(E_\nu-p_\parallel)^2,
   \]
   while
   \[
   Q^2=2E_\nu(E_\mu-p_\parallel)-m_\mu^2,\qquad
   W^2=M^2+2M(E_\nu-E_\mu)-Q^2.
   \]
   With fixed \(M\), the usual physical branch, and common beam-axis conventions, \(p_T,p_\parallel,q_3\) determine \(E_\nu\) and therefore \(W\). Thus these five coordinates need not describe five independent continuous degrees of freedom.

   The authors should establish the actual relations for their implemented truth and reconstructed definitions, including beam direction, nucleon-mass conventions, and the two recoil estimators. If the redundancy is exact or nearly exact, say so. Adding a nonlinear derived coordinate may still help a finite-capacity classifier, but that is a different claim from accessing another independent physical dimension.

   This also matters for the supported cells, fine-grid refinement, and interpretation of the apparent benefit of adding \(W\).

2. **Calorimetric response is an essential missing uncertainty for the generator interpretation.**

   This is the most important experimental limitation. The tests use several hadronic coordinates, and the manuscript explicitly finds that the matched muon-only projection does not reject GENIE CV. The rejection of that prediction therefore depends on information whose detector-response uncertainty is incomplete.

   Scaling reconstructed recoil energy by \(\pm4\%\) and retaining the original null distributions is a useful sensitivity check. It does not establish robustness to a response uncertainty. The uncertainty can change both the observed statistic and its calibrated distribution, with correlated effects on selection, migrations, background refinement, and derived observables. Species-dependent response, invisible energy, and resolution changes need not resemble a uniform scale variation.

   For a headline physical rejection, a defensible recoil-response model should be propagated through calibration. Otherwise the conclusions should consistently identify the results as conditional tests using an incomplete detector-uncertainty model. The exploratory scale study should not be presented as substantially resolving that omission.

3. **The hybrid null is not yet demonstrably equivalent to the named generator prediction.**

   The authors are commendably explicit about the within-cell Tune v1 structure. Nevertheless, a rejection of a generator’s fine-grid integrals combined with Tune v1 subcell structure is a rejection of that constructed hypothesis.

   The observed refinement ratios do not establish a remainder bound. Moreover, a residual proportional to \(\delta_{\rm fine}\) explores one direction in the space of possible changes. Robustness to \(5.2\delta_{\rm fine}\) along that direction provides no bound on a residual pointing elsewhere.

   The paper should either demonstrate adequate convergence, test alternative within-cell structures, or restrict its claims to the explicitly constructed nulls. An assumed geometric extrapolation without a recorded calculation is not an adequate basis for extending the rejection to the continuous generator prediction.

   There is a related issue beyond grid resolution: reweighting Tune v1 in these observables preserves its conditional distribution of unreported hadronic properties. Different generators can predict different neutron fractions and particle compositions at the same reported coordinates, changing the detector response. Grid refinement alone does not test this dependence.

4. **The claims of exact Monte Carlo validity and familywise error control need revision or proof.**

   The fixed-sample Monte Carlo formula
   \[
   p=(k+1)/(B+1)
   \]
   does not by itself establish validity when \(B\) is selected by inspecting exceedance counts. Repeatedly checking ordinary 95% Clopper–Pearson intervals also does not make them simultaneous confidence intervals over the stopping sequence. Predetermining a stopping rule is necessary for transparency, but does not establish that the rule controls the claimed error.

   Consequently, the assertion that the Monte Carlo \(p\) values “remain valid at the number of pseudo-experiments reached” needs a statistical argument that is currently absent. Holm’s procedure controls familywise error when supplied with valid marginal \(p\) values; it cannot repair invalid marginal calibration. Dependence among the ten tests is not itself a problem for Holm.

   Sequential Monte Carlo methods with explicit resampling-error guarantees are available; see, for example, [Gandy’s sequential Monte Carlo test](https://arxiv.org/abs/math/0612488) and [Gandy, Hahn, and Ding](https://arxiv.org/abs/1703.09305). The authors should use an appropriate sequential construction, account for Monte Carlo decision error, or provide a valid fixed-sample analysis.

   This concern does not imply that the observed rejections will disappear. Their apparent separation from the null distributions may make the decisions robust. It does mean that the current claim of exact control is not established by the procedure described.

5. **The nuisance ensemble and the meaning of “calibrated” must be defined more carefully.**

   Drawing nuisance universes defines an ensemble averaged over a specified nuisance distribution. Calibration in that ensemble is not automatically frequentist size control at every fixed nuisance value allowed by a composite null.

   The manuscript should state whether its error claim is an average over nuisance draws or a uniform claim over nuisance parameters. It should specify the probabilities assigned to universes, correlations between bands, treatment of asymmetric variations and clipped weights, and validation of the lateral surrogate.

   It must also explain how the 34 interaction-model bands act when the null truth is fixed to \(G\). Do they vary response and efficiency conditional on the specified truth, or also vary the truth distribution? If the latter, the null is broader than “the true cross section equals \(G\).” This is a question about the hypothesis being tested, not merely implementation detail.

6. **The uncertainty section contains unresolved scientific issues that cannot be settled by procedural exceptions.**

   The run-period discrepancy is especially concerning. A roughly 7% step in a muon-momentum distribution could indicate a response, normalization, selection, or simulation problem. Constructing a covariance from three period groups is a reasonable diagnostic response, but does not establish that the discrepancy has been covered correctly.

   The paper needs enough information to assess that construction: the group definitions, exposures, formula, treatment of statistical fluctuations, correlations with existing systematics, and resulting covariance structure. The small number of groups and possible regularization shrinkage should remain explicit.

   Likewise, five training seeds give a poorly determined training-variance estimate. That need not invalidate the two-dimensional result if the contribution is negligible, but the scale of its uncertainty should be distinguished from the more consequential seed dependence of the five-dimensional covariance.

   Finally, the authors should distinguish pointwise interval coverage from simultaneous coverage across bins and projections. A conventional cross-section uncertainty band is not ordinarily a simultaneous confidence band. The manuscript should specify which coverage property it seeks rather than treating every untested coverage notion as an equivalent deficiency.

7. **The validation should focus on the final estimators and on deformations that challenge the inferred correlations.**

   Marginal normalization agreement is useful bookkeeping and stability evidence. It does not test recovery of the joint distribution. Same-response signal reweighting tests are valuable, but they do not test detector mismodelling or changes in unreported hadronic composition.

   The manuscript reports failed coverage for a deterministic variant, historical tests of a rebuilt band, and no coverage test for the quoted statistical block. Those studies do not establish the coverage of the final reported estimator and uncertainty.

   A compact validation programme should target the final configurations: nominal closure, an alternative with approximately preserved marginals but changed correlations, and at least one plausible detector-response deformation. Failure should be reported quantitatively, with biases compared with both statistical precision and claimed uncertainty.

   The statement that validation would require an independent production-size simulation, continuous nuisance generator, and uninspected external-generator samples is too categorical. Those would strengthen the study, but useful conditional coverage tests and targeted response tests can be performed with less. The paper should distinguish a comprehensive validation programme from the minimum additional evidence needed for its actual claims.

8. **The known background bias should be handled consistently.**

   The manuscript identifies a purity-subtraction bias and shows that unbinned refinement substantially reduces it. Yet the central-value figures retain the biased treatment while the calibrated tests use the improved estimator.

   There may be a practical reason for retaining both, but the reader needs to see its consequence directly. Show the central-value shift in the affected projection and identify the estimator used in every figure and table. Either use the improved estimator for the principal descriptive result or explain the choice and quantify the omitted effect.

   A known bias of approximately one quoted standard deviation should not be left as a textual caveat beside an otherwise conventional uncertainty presentation.

9. **The physical interpretation of the generator comparisons needs tighter control.**

   NuWro and GiBUU are described as carbon predictions, whereas the data are on hydrocarbon. Per-nucleon normalization does not remove the target-composition difference. The authors should provide the relevant hydrogen contribution or correction, or quantify its omission.

   GiBUU’s missing high-energy flux also requires more than a low-\(p_\parallel\) domain restriction: high-energy interactions can populate that domain. Adding a high-energy contribution from another generator is a useful diagnostic, but does not produce a GiBUU prediction with a completed energy range.

   The claim that Valencia 2p2h fills 52% of a gap is descriptive and model dependent. Small changes under selected pion-FSI variations do not exclude other FSI effects or establish a unique mechanism. The paper largely recognizes this, but its mechanistic language should remain as restrained as its statistical language.

   The comparison with the published low-recoil result should use matched observable definitions before numerical agreement is emphasized. An estimated 11% migration out of a relevant truth bin makes “within 10%” agreement difficult to interpret without the common-cell calculation.

10. **The deliverable and benchmark should be clearer.**

   The manuscript needs one concise table identifying each estimator, its background treatment, uncertainty status, and use. A second table should summarize validation results, including the deformation, tested configuration, quantitative bias, and coverage status.

   For a methodological paper, one matched comparison with conventional iterative unfolding would help determine whether the demonstrated limitations are specific to the classifier implementation or common to the inverse problem. This need not become an extensive algorithm competition.

   A deposited, internally consistent release is also required for publication. The described package carries a superseded two-dimensional curve and omits reproduction of many quoted quantities. Recomputing stored statistics is valuable, but should be distinguished from reproducing the event-level analysis.

**Minor comments**

- Describe the two-dimensional result as an approximate reproduction of the published central values. The displayed \(\chi^2/\mathrm{ndf}=2.65\) is not a compatibility significance without the cross-covariance.
- State the signal phase-space cuts, fiducial definition, flux integration range, target normalization, and background fractions explicitly enough to understand the analysis without the note.
- Retain the implemented \(135\) MeV charged-pion subtraction if it defines the reported observable, but give it a clearly identified convention. Correcting it would require consistent regeneration of affected products.
- Explain whether \(W\) is a stationary-nucleon kinematic estimator or a generator hadronic-system invariant mass. These are not generally interchangeable for nuclear events.
- Define “supported” cells, including occupancy and efficiency requirements, and give the fine-grid edges in accessible supplementary material.
- State where the shape-normalization Jacobian is evaluated and how prediction-sample correlations are propagated.
- Include observed test statistics and null summaries in Table I. The many zero exceedance counts primarily indicate Monte Carlo resolution.
- Give binomial uncertainties on power estimates; distinguish observed power estimates of zero or one from exact probabilities.
- Explain the metric behind the covariance’s quoted “6.145%” change. Its precision is excessive relative to the limited seed study.
- Replace “claim variant” in Fig. 4 with a physical or statistical description of the null variation.
- Resolve the incomplete references and all HOLD placeholders before publication.

**Recommendation.** Major revision. A publishable methods paper is plausible, but the current manuscript does not establish the advertised exact error control or a detector-systematics-complete physical rejection of the named generators. A narrower interpretation is acceptable if made scientifically precise and supported by the final implementation.

---

**Part 2 — Presentation and suggested rewrites**

The authors’ concern is justified. Much of the paper reads as an audit of a project rather than a physics argument. The problem is not the candor. It is that numerical results, scientific limitations, development history, and internal acceptance procedures receive similar prominence.

The following quotations retain the manuscript’s wording, with PDF line wrapping removed. Suggested rewrites preserve the limitations in the quoted material; where detail should move, I specify its destination.

**Title and abstract.** The title is plausible for PRD, but “validation” may suggest a successful validation programme more broadly than the results support. A more accurate title would be:

> *Multidimensional OmniFold unfolding of MINERvA inclusive charged-current data: performance and limitations*

“Calibrated model tests” can remain if their statistical calibration is established and their physical scope is clear.

The abstract’s weakest sentence is:

> “These rejections hold only under stated conditions.”

This provides no information beyond announcing a qualification. Replace it with the two conditions that matter most:

> “The generator tests assume the simulated calorimetric recoil response and unresolved within-cell truth structure.”

The full abstract is addressed in Part 3.

**I. Introduction.** The opening paragraphs read like a PRD introduction. The long results paragraph then becomes a catalogue of caveats, configurations, and adjudications.

The clearest example is:

> “All ten calibrated tests, in total and in shape for each of the five predictions, reject at the 5% familywise level under six stated conditions (Sec. VI B). Two of them, the absence of a calorimetric recoil-response uncertainty and the undemonstrated convergence of the fine grid on which the null hypotheses are defined, limit their physical interpretation.”

Suggested version:

> “The calibrated total and shape comparisons reject the five simulated generator hypotheses at a nominal familywise level of 5%. Their interpretation is limited principally by the missing calorimetric recoil-response uncertainty and unresolved truth structure below the calibration grid.”

Keep the complete six-condition specification in Sec. VI. The introduction needs the two material interpretation limits, not their numbering.

Similarly:

> “The measured model dependence prevents a five-dimensional measurement with total uncertainties that meet our predefined criteria at useful precision.”

Suggested version:

> “For the configurations and reporting domains studied, model dependence prevents a five-observable measurement from reaching the adopted uncertainty targets.”

The targets and scope belong in the uncertainty section. “Predefined” does not explain what makes them physically useful.

**II. Data, signal, and simulation.** This is mostly conventional. The unusual observable definition deserves disclosure, but its presentation sounds like a confession about inherited code.

> “We have not corrected this constant.”

Suggested replacement for the surrounding discussion:

> “The implemented truth definition subtracts 135 MeV for each charged pion. Replacing this constant by the charged-pion mass changes the true-\(E_{\rm avail}\) bin assignment of 0.67% of simulated events and changes individual bin populations by at most 1.05%; its effect relative to the full covariance has not been evaluated.”

This states exactly what was done and its assessed consequence. The origin of the constant belongs in the analysis note.

Also:

> “The files analysed are an earlier production of that release; their names and sizes are recorded for reproduction (see Data availability).”

Suggested version:

> “The analysis uses an earlier production of the released AnaTuples, identified by the file manifest and checksums in the data release.”

The earlier-production qualification remains, but the sentence identifies the reproducibility mechanism directly.

**III. Unbinned unfolding.** The first two paragraphs read like a methods section. The estimator paragraph becomes difficult because it follows implementation history.

> “An exact-split scikit-learn estimator (one that evaluates tree splits on the exact feature values rather than on histogram bins), which was the original two-dimensional choice, is kept as a cross-check (Sec. IV A).”

Suggested version:

> “An exact-split scikit-learn implementation provides a two-dimensional cross-check.”

Retain the substantive selection disclosure in Sec. IV A: the adopted learner was chosen after both comparisons were known. The original implementation’s chronological status adds nothing here.

The distinctions among the central-value and joint-test estimators should be expressed in a configuration table. Give the main text one short paragraph explaining why they differ.

> “The use of AI tools in this work is described in the Acknowledgments.”

Delete this cross-reference. The acknowledgment can stand on its own.

**IV. Validation — opening.** The definitions are sensible, but their presentation is unusually tutorial and defensive:

> “The bookkeeping of missed events (those that fail reconstruction) is checked for completeness, an identity that must hold, and the dependence on the number of iterations is a stability diagnostic; neither establishes recovery or coverage.”

Suggested version:

> “We assess signal recovery with closure tests and interval coverage with repeated pseudo-experiments. Efficiency bookkeeping and iteration scans provide additional consistency and stability checks.”

Explain the narrower interpretation of those checks once in the validation summary. There is no need to anticipate every possible overinterpretation before presenting any result.

**IV A. Two-dimensional reproduction.** This is close to a normal results subsection. The learner-selection disclosure is necessary and should remain:

> “This choice, which replaced the exact-split result, was made after both comparisons were known.”

Suggested integrated version:

> “The LightGBM central value matches the estimator used to construct the covariance. This choice was made after comparison with the published result. The exact-split alternative differs by a median of 0.98% per bin and by at most 12.2%; this dependence is not included in the covariance.”

This retains the potentially consequential selection history without narrating the development sequence.

The cross-covariance qualification is correctly placed here and should remain. It need not also occupy a long parenthesis in the figure caption.

**IV B. Two-dimensional uncertainty and coverage.** This is the least conventionally written subsection. Important limitations are interwoven with old bugs, retired bands, internal reviews, and repeated statements that coverage is unknown.

For example:

> “Because the block is built from the differences among the periods, it contains them by construction; this says nothing about its coverage, that is, whether its size is right. For the same reason, the block’s own consistency check passes whatever the data, and it is not a test.”

Suggested version:

> “The run-period covariance describes the observed differences among the three period groups. Its coverage is unvalidated, and those same differences cannot provide an independent validation.”

Retain the small-group, shrinkage, and retained-noise limitations immediately afterward.

The historical statistical-band discussion should be condensed:

> “Rescoring the same pseudo-experiments against the rebuilt band is post hoc and partly circular.”

Suggested replacement for the history in the main text:

> “An earlier statistical-interval construction undercovered in closure tests. After correction, evaluation on the same pseudo-experiments gave 97.7% containment within two standard deviations and 78.1% within one, indicating intervals wider than the simulated scatter. These tests are not independent and do not validate the different bootstrap covariance reported here.”

Put the completeness-division bug, the original 91.2% result, and the relationship among the retired ensembles in a supplementary validation record. They remain available without competing with the final result.

The ending is excessively repetitive:

> “The result’s intervals, bias and covariance have not been independently validated.”

> “We make no claim about coverage.”

Use one consolidated statement:

> “The reported covariance has not undergone independent end-to-end coverage validation. It excludes learner dependence, unfolding-model and regularization dependence, and the tested approximation in systematic-universe efficiency weighting.”

Then specify the detector-family assumption and outstanding validation requirements once. There is no need to restate unknown coverage in several adjacent sentences.

**IV C. Higher-dimensional central values.** This subsection contains substantive results, but its organization repeatedly alternates result and warning.

> “In this implementation, then, agreement in the marginal normalizations coexists with substantial regularization bias, and the model dependence and the calibration of the uncertainties remain limiting.”

Suggested version:

> “Marginal normalization agreement does not establish joint shape recovery: generator-sized deformations leave substantial regularization bias, and the tested five-dimensional statistical intervals fail the coverage criterion.”

Organize the subsection into three consecutive subjects: marginal checks, closure and background bias, and interval/estimator stability. Keep the numerical bias results prominent.

Also:

> “Input changes at the level of floating-point rounding move the unfolded values on data by up to a few statistical standard deviations”

Suggested version:

> “Rounding-level perturbations of the inputs change some unfolded cells by several statistical standard deviations. For the joint-test estimator, the resulting spread remains within its data-bootstrap uncertainty.”

The main text should state the effect. The note should document the perturbation and diagnostic mechanism. Clarify the configurations behind the different uncertainty comparisons.

**V. Central-value results.** This section sounds most like a physics paper, but several observations are followed by long qualifications that interrupt interpretation.

The opening overstates independence:

> “The Eavail dimension provides an independent view of the established low-recoil discrepancy”

Suggested version:

> “The \(E_{\rm avail}\) projection displays the established low-recoil discrepancy.”

It uses the same data and correlated reconstructed information; “independent” is unnecessary.

The low-recoil comparison should lead with its comparability limit:

> “That measurement defines true Eavail more broadly, counting every final-state particle except neutrons, several species of which our definition omits; in our simulation this moves about 11 % of our lowest true-Eavail bin out of it, with the sign of the residual, but its effect on the two common cells has not been computed, so the comparison is not quantitative.”

Suggested version:

> “The comparison is qualitative because the published measurement uses a broader truth definition of \(E_{\rm avail}\). In simulation, this difference moves approximately 11% of events out of our lowest truth bin, in the direction of the observed residual; its effect in the two common cells has not been evaluated.”

The associated ratios can then be reported as descriptive numbers.

The repeated sentences “These statements are descriptive” and “no significance is assigned” can become one opening statement:

> “The comparisons in this section describe central values; validated higher-dimensional uncertainties are unavailable.”

Keep the specific high-\(W\) regularization and detector-response concerns next to Fig. 2. Those are local interpretive limitations, not redundant disclaimers.

**VI A. Hypotheses, statistics, and calibration.** The technical content belongs in the paper. The account of design review and job-budget decisions does not belong at this length.

> “The reviewers of the design had seen descriptive per-cell residuals before it was fixed.”

> “A bounded extension of the production computing budget was decided while the outputs of the computing jobs showed the observed p values used for the decisions”

Suggested version:

> “The test design followed inspection of descriptive data residuals, and the simulation budget was extended after preliminary \(p\) values were visible. The statistics, null variations, thresholds, and stopping rule were unchanged.”

Keep this disclosure in a short design subsection or supplement. It is material, but it does not need the vocabulary of internal review.

The phrase

> “independent recomputation with separately written code agrees with the production evaluation in all 1379 compared quantities”

could become:

> “A separately implemented calculation reproduces the reported test statistics and decisions.”

The full comparison count belongs in the reproducibility documentation. This verification does not establish calibration validity, which must be addressed separately.

**VI B. Conditions.** A consolidated assumptions subsection is appropriate. Its six items currently mix hypothesis definition, missing physics, Monte Carlo approximations, and finite-sample treatment.

The most problematic passage is:

> “If the step kept shrinking geometrically, at a rate taken from the review of the test design, for which no calculation is recorded, the residual would be about one to three times the last step.”

Suggested version:

> “The \(\pm2\delta_{\rm fine}\) variations were motivated by an assumed geometric extrapolation of the refinement sequence. This extrapolation has not been demonstrated, and the observed refinement ratios do not establish a remainder bound.”

Preserve the unrecorded derivation in the supplementary design history. In the paper, the scientific consequence is that the variation is a sensitivity prescription rather than a demonstrated bound.

The limitation is important enough to remain in the abstract and conclusions. It should not appear as another generic member of an undifferentiated six-condition list.

**VI C. Results.** The first result and interpretation paragraphs are appropriate. The interrupted-job narrative is disproportionately prominent.

> “Had every interrupted one exceeded the observed statistic, no test would have been rejected.”

> “Every submitted pseudo-experiment has now been observed, and no assignment of the lost outcomes changes any decision.”

Suggested final-state account:

> “All interrupted pseudo-experiments were subsequently recovered after exact reproduction checks on 16 completed cases. None exceeded the observed statistics for any tested null variation, and their inclusion leaves every decision unchanged.”

Retain the timing relative to the original decisions, recovery protocol, and worst-case missingness calculation in the supplement.

The projection comparison is scientifically important and deserves its current prominence. However, “no demonstrated added discrimination” should be distinguished from evidence that the joint test has no added discrimination. Binary rejection of both projections and joint tests is a limited comparison of their power.

**VI D. Hadronic-response condition.** This subsection is scientifically necessary and largely reads appropriately. It can be shorter without becoming less candid.

> “Particle-species, energydependent, and resolution effects, a response difference applied before calibration, and larger variations were not tested.”

Suggested consolidated version:

> “This check varies only a uniform recoil scale and retains the original null distributions. It does not test species-dependent response, energy dependence, resolution, larger variations, or propagation of response uncertainty through calibration.”

State the surviving-rejection result immediately before this. The missing response uncertainty deserves prominent treatment; it is not an overemphasized minor caveat.

**VII. Status of a five-dimensional uncertainty.** This section reads like an internal acceptance review.

> “One of these criteria requires a bound fixed before the covariance was produced and can no longer be applied to it. We use the covariance only under an exception to the criteria, recorded in the analysis note and limited to this one covariance.”

Suggested version:

> “The covariance does not satisfy the analysis’s uncertainty-validation requirements. One requirement cannot be assessed retrospectively because its bound was not fixed before construction. The covariance is therefore retained only as a diagnostic and is not used for generator significance.”

Keep the documented exception and original criterion in the analysis note. The main text must explain what the missing bound would have established.

The seed study can be stated more directly:

> “For one pair of training seeds, the projected uncertainty changes by approximately 6.1%, exceeding the adopted 5% tolerance. The difference does not decrease over 40–160 throws. This comparison uses nested ensembles and one seed pair, and five uncertainty bands remain untested for seed sensitivity.”

The detailed sequence, resampling-noise results, and trace contribution should remain in the note or a compact table. They qualify how convincing the seed conclusion is, but do not require this many prose digits.

Finally:

> “None of the definitions it considered could meet the precision targets set in advance, within the study’s rules and computing budget.”

Suggested version:

> “None of the reporting definitions studied met the adopted precision targets within the available computational budget. For the fallback definition, the estimated model-dependence contribution alone exceeded the target total uncertainty.”

Call it a bound only if a defensible bounding argument is supplied. An envelope of tested alternatives should be identified as such.

**VIII. Conclusions.** The conclusion repeats nearly the entire validation section. It should retain four findings: approximate two-dimensional reproduction, higher-dimensional descriptive results, the dominant extraction failures, and the conditional model tests.

The sentence

> “The joint tests are calibrated generator tests; they are conditional on six stated conditions and provide no new measurement uncertainty.”

could become:

> “Full-chain calibration enables conditional tests of the specified generator hypotheses despite substantial estimator bias; it does not supply a validated cross-section uncertainty.”

Keep the missing recoil response and unresolved subcell structure explicit. Remove the number of conditions, recovery history, and detailed status of each retired interval construction. Those are not concluding physics results.

**Acknowledgments.** The disclosure of substantial AI assistance is appropriate. The assurance language is too long:

> “Results were accepted only after verification against committed evidence: predeclared criteria, independent recomputation by separately written code”

A more conventional disclosure is:

> “The authors used AI language-model tools to assist with analysis code, statistical calculations, figures, and manuscript preparation. The authors verified the results and take responsibility for the analysis and text.”

The detailed tools, versions, and verification record can be retained in supplementary reproducibility documentation. AI-assisted reviews should not be presented as substitutes for independent scientific validation.

**Data availability.** This is a release-status report rather than a final availability statement.

> “A candidate release package of about 16 MB [39], prepared locally but not yet deposited”

> “The package was assembled before the two-dimensional central value was changed to LightGBM, and it carries the exact-split curve.”

These are outstanding tasks to resolve, not sentences to polish. Deposit a consistent package and state its actual scope:

> “The deposited package reproduces the joint-test calculations and specified figures from archived analysis outputs. Event-level reproduction additionally requires the identified AnaTuples and generator samples.”

Any quantities still unreproducible from the deposit must be listed clearly. Preserve that distinction; remove the assembly chronology after fixing the release.

---

**Part 3 — The abstract**

**(a) Which sentences carry results?**

| Sentence opening | Function |
|---|---|
| “We test the practical limits…” | Aim and scope. |
| “The analysis reproduces…” | Main positive result and observable extension; “reproduces” needs qualification. |
| “The higher-dimensional central values…” | Validation results, with marginal consistency distinguished from shape recovery. |
| “Pseudo-experiments that include backgrounds…” | Negative methodological result, expressed too generically. |
| “The measured model dependence prevents…” | A headline negative result, bounded by the configurations and criteria studied. |
| “Generator tests, calibrated…” | Main inferential claim, requiring the statistical corrections discussed above. |
| “These rejections hold only…” | Redundant signposting. |
| “The tests recover known discrepancies…” | Interpretation and limit on novelty. |
| “Their physical interpretation is limited…” | Essential qualifications to the generator claim. |

The abstract contains a real result: this implementation does not deliver the intended validated measurement. That should be stated plainly, rather than concealed inside a succession of qualifications.

**(b) Suggested abstract — 151 words**

> We apply OmniFold to MINERvA medium-energy inclusive muon-neutrino charged-current data and unfold five observables describing muon and hadronic kinematics. The integrated muon-kinematic cross section differs from the published measurement by 1.1%, and 95.6% of its bins agree within 10%. Higher-dimensional results reproduce marginal normalizations, and three- and four-observable tests recover injected shape changes. Background subtraction, regularization bias, and estimator instability limit the extraction; a five-observable measurement with validated total uncertainties is not achieved. Full-chain pseudo-experiments yield nominal 5% familywise rejections of all five tested generator predictions in both normalization-sensitive and shape-only comparisons. These results apply to discretized generator hypotheses under the adopted nuisance model, which omits calorimetric recoil-response uncertainty, and convergence of the hypothesis grid remains unestablished. The comparisons recover known disagreements without demonstrating additional discrimination from the joint five-observable information relative to matched coarse projections.

“Nominal” is deliberate: until the sequential Monte Carlo issue is resolved, I would not endorse an unqualified exact familywise-error claim.

**(c) What was dropped, and where it belongs**

- **The full generator-version list:** Sec. II and Table I. It occupies too much abstract space for this paper’s methodological emphasis.
- **The full list of added observables:** the introduction and observable definitions. The abstract can describe their physical role.
- **Separate references to background-inclusive pseudo-experiments and uncertainty ensembles:** Secs. IV and VII.
- **The internal phrase “predefined criteria at useful precision”:** Sec. VII, with numerical targets and their motivation.
- **“These rejections hold only under stated conditions”:** delete; the important conditions are stated explicitly.
- **The catalogue of interval-coverage qualifications:** Sec. IV. The abstract retains their material consequence: no validated total-uncertainty measurement.
- **The detailed null-grid construction:** Sec. VI. The abstract retains the unresolved grid dependence.

---

**Part 4 — What else the authors need to hear**

The manuscript currently gives the reader more evidence that the project was carefully monitored than that its final physical inference is adequately calibrated. Those are different achievements. Specifications, independent implementations, archived records, and recovery of interrupted jobs support reproducibility. They do not supply a missing detector uncertainty, bound an unresolved response dependence, or establish coverage.

The authors should choose the paper’s central deliverable. A methods paper about the performance and limitations of this implementation is credible and potentially useful. A paper centered on five-generator physical rejection needs stronger detector and hypothesis validation. Presenting both with equal headline weight leaves the weaker inference carrying too much of the paper.

Several of the negative results deserve clearer figures. A closure plot showing injected, prior, and recovered distributions would communicate the regularization problem better than another paragraph of warnings. A compact bias-versus-precision summary would help establish where the method is informative. One clear plot of the covariance’s seed dependence would make the uncertainty limitation assessable.

Finally, the authors should retain their candor while exercising more editorial judgment. State each important limitation where it affects a conclusion, summarize the two or three decisive ones in the abstract and conclusion, and put the procedural history in the supplement. The paper will sound more authoritative when the reader can see exactly what the evidence establishes—and exactly which additional calculations would change that assessment.

---

## P5. X1 Gemini 3.8 Flash: outline analysis of the pass-1 paper and primer (sha256 `2de1e24b4e46f668…`)

Here is the structural analysis of both documents from the perspective of an experimental neutrino physicist and journal editor.

---

##### 1. Paragraph Main-Idea Map

*Criteria: Maximum 25 words per main-idea sentence. Tagged as `[NONE]`, `[MULTI]`, `[HIST]`, `[CAVEAT]`, `[RESULT]`, or `[METHOD]`.*

###### A. Research Paper (`paper.txt`)

* **Abs.1** (“We test the practical limits…”): OmniFold reproduces 2D MINERvA cross sections and rejects five generators in 5D, but exhibits severe regularization, coverage, and stability limits. (21 words) **[MULTI]**
* **I.1** (“Multidifferential neutrino cross sections test…”): Unbinned machine-learning unfolding with OmniFold circumvents the combinatorial scaling bottlenecks of binned migration matrices for higher-dimensional neutrino cross-section measurements. (20 words) **[METHOD]**
* **I.2** (“We apply the method to MINERvA…”): OmniFold is applied to MINERvA open data to reproduce 2D muon kinematics and extract simultaneous 5D cross sections incorporating hadronic observables. (22 words) **[METHOD]**
* **I.3** (“We assess how reliable the method…”): The analysis assesses practical reliability through lower-dimensional consistency, shape-injection closures, pseudo-experiments with backgrounds, and seed-stability ensembles. (18 words) **[METHOD]**
* **I.4** (“As an application, we test specified…”): Calibrated full-chain pseudo-experiments test five generator predictions while incorporating the unbinned estimator’s prior-pull bias into the null distributions. (19 words) **[METHOD]**
* **I.5** (“The two-dimensional reproduction agrees with…”): While 2D reproduction succeeds, higher-dimensional unfolding exhibits regularization bias, seed dependence, and missing uncertainties, though generator tests reject all five predictions. (22 words) **[MULTI]**
* **I.6** (“Sections II and III describe the data…”): The remaining sections detail the data, estimators, validation checks, central-value results, calibrated generator tests, and uncertainty budget status. (19 words) **[NONE]**
* **II.1** (“The analysis uses the twelve MINERvA…”): The analysis uses MINERvA medium-energy data with $1.057\times 10^{21}$ POT and GENIE simulation reweighted to the MINERvA Tune v1. (19 words) **[METHOD]**
* **II.2** (“The unfolded observables are defined at…”): Five truth-level observables are defined, noting that three hadronic quantities share calorimetric inputs and inherit an uncorrected pion-mass offset. (20 words) **[METHOD]**
* **II.3** (“Event selection is held fixed as…”): Event selection remains fixed across all dimensionalities, and external generator predictions are reweighted to the analysis neutrino flux. (19 words) **[METHOD]**
* **III.1** (“Each OmniFold iteration consists of two…”): OmniFold unfolds unbinned cross sections via two-step classifier reweighting between reconstruction and truth levels across successive iterations. (18 words) **[METHOD]**
* **III.2** (“Backgrounds enter the reconstruction-level step through…”): Backgrounds are handled either via bin-purity weights for central values or unbinned negative-weight classifier refinement for generator tests. (18 words) **[METHOD]**
* **III.3** (“All estimator configurations use five OmniFold…”): Five iterations of gradient-boosted decision trees regularize unfolding, with LightGBM chosen for central values and deterministic negative weights for joint tests. (21 words) **[METHOD]**
* **IV.1** (“In closure tests, truth denotes the…”): Validation distinguishes closure, coverage, completeness, and stability, noting that bookkeeping and iteration stability do not establish truth recovery or interval coverage. (22 words) **[METHOD]**
* **IV.A.1** (“The two-dimensional result is an end-to-end…”): Unfolding reproduces the published 2D cross section within 1.1% globally, though correlated shape differences depend on the tree-learner implementation. (20 words) **[RESULT]**
* **IV.A.2** (“Both results derive from the same…”): Because both results derive from identical data, rigorous statistical comparison of their differences would require an unavailable cross-covariance matrix. (20 words) **[CAVEAT]**
* **IV.B.1** (“The covariance of our two-dimensional result…”): The 2D covariance combines systematic, statistical, training-seed, and run-period blocks, matching the published total uncertainty magnitude despite smaller flux errors. (20 words) **[METHOD]**
* **IV.B.2** (“The systematic-universe unfoldings approximate the…”): The run-period block captures observed period-to-period data discrepancies by construction, but this diagnostic cannot guarantee correct statistical coverage. (19 words) **[CAVEAT]**
* **IV.B.3** (“The statistical block is a bootstrap…”): Past tail undercoverage was resolved by rebuilding the bootstrap band, but neither the rebuilt band nor the total covariance has independent coverage validation. (23 words) **[HIST]**
* **IV.B.4** (“In summary, we report a reproducible…”): The 2D covariance lacks independent coverage validation, omits learner and regularization dependencies, and makes no formal claim of correct frequentist coverage. (21 words) **[CAVEAT]**
* **IV.C.1** (“Each higher-dimensional central value is checked…”): Higher-dimensional marginal normalizations match lower dimensions, but purity background subtraction introduces high-$W$ biases that unbinned negative-weight refinement largely eliminates. (20 words) **[MULTI]**
* **IV.C.2** (“The unfolding recovers only part of…”): Severe regularization bias, rounding sensitivity, and failed interval coverage tests prevent establishing frequentist interval validity for the 5D central values. (21 words) **[CAVEAT]**
* **V.1** (“The Eavail dimension provides an independent…”): Unfolded low-$E_\text{avail}$ data confirm the established low-recoil discrepancy, which is partially bridged by two-particle–two-hole contributions rather than pion final-state interactions. (21 words) **[RESULT]**
* **V.2** (“The fifth observable, W, separates the…”): Joint $(E_\text{avail}, W)$ central-value projections show an unquantified rate excess over MINERvA Tune v1 concentrated at high available energy and high $W$. (21 words) **[RESULT]**
* **V.3** (“The one-dimensional projections in Fig. 3…”): External generator models underestimate unfolded 1D distributions overall and at high $W$, though discrepancies reflect comparisons to Tune v1 without statistical significance. (22 words) **[RESULT]**
* **VI.A.1** (“For each of five predictions G…”): Calibrated joint tests evaluate hybrid null hypotheses across 109 5D cells using generator rates matched to Tune v1 sub-grid shapes. (21 words) **[METHOD]**
* **VI.A.2** (“A total statistic Ttot = r⊤…”): Total and shape test statistics utilize a regularized covariance metric derived from pilot pseudo-experiments plus generator sample variance. (19 words) **[METHOD]**
* **VI.A.3** (“The null distribution of each statistic…”): Full-chain pseudo-experiments incorporate nuisance variations, prior pull, and pre-specified shifted nulls to calibrate valid Monte Carlo $p$-values. (19 words) **[METHOD]**
* **VI.A.4** (“The ten tests are controlled at…”): Multiple testing across ten hypotheses is controlled at 5% familywise error using the Holm procedure with Clopper-Pearson binomial intervals. (20 words) **[METHOD]**
* **VI.B.1** (“The decisions test the hybrid null…”): Generator test rejections are conditional on six nuisance-model assumptions, notably unmeasured sub-fine-grid shape convergence and missing calorimetric recoil-response uncertainties. (21 words) **[CAVEAT]**
* **VI.C.1** (“Table I lists the ten decisions…”): All ten generator hypotheses are rejected at 5% familywise error, remaining determinate under shifts along the fine-grid direction up to $5.2\,\delta_\text{fine}$. (22 words) **[RESULT]**
* **VI.C.2** (“Batch-job time limits interrupted or prevented…”): Post-decision recovery of all time-limited pseudo-experiments confirmed that no interrupted jobs alter any of the ten rejection decisions. (19 words) **[HIST]**
* **VI.C.3** (“The comparisons recover the generator disagreements…”): While rejections recover known generator disagreements, matched coarse 2D projections also reject, showing no demonstrated power gain from 5D joint information. (22 words) **[CAVEAT]**
* **VI.C.4** (“Power studies characterize the response to…”): Pre-specified alternative models demonstrate high statistical power to detect shape distortions for Tune v1, but lower power for GENIE. (20 words) **[RESULT]**
* **VI.D.1** (“MINERvA’s recoil-energy analyses assign a hadronic-energy…”): The absence of a calorimetric recoil-energy systematic limits physical interpretation, as generator rejections rely crucially on hadronic observables. (19 words) **[CAVEAT]**
* **VI.D.2** (“In an exploratory sensitivity study [37]…”): Shifting reconstructed recoil energy by $\pm 4\%$ does not overturn rejections, but comprehensive energy-dependent and species-dependent response uncertainties remain untested. (20 words) **[CAVEAT]**
* **VII.1** (“We have built a covariance for…”): A 5D covariance was constructed but failed pre-declared acceptance criteria due to unacceptable sensitivity to the tree learner's random training seed. (22 words) **[CAVEAT]**
* **VII.2** (“A separate study looked for a…”): Model dependence prevented defining a 5D measurement meeting predefined precision targets, motivating calibrated hypothesis testing as an alternative inference path. (21 words) **[HIST]**
* **VIII.1** (“This study applies OmniFold to MINERvA…”): OmniFold reproduces 2D measurements and enables 5D extensions, but exposes significant regularization bias, seed instability, and model dependence. (19 words) **[MULTI]**
* **VIII.2** (“The generator comparisons illustrate calibration through…”): Calibrated generator tests successfully reject all models, but physical interpretation remains constrained by untested recoil response and unverified sub-grid convergence. (21 words) **[MULTI]**

---

###### B. Plain-Language Primer (`primer.txt`)

* **P.Abs.1** (“This is a short, jargon-light guide…”): This primer explains unbinned OmniFold unfolding on MINERvA data, summarizing reproductions, multivariable extensions, simulation discrepancies, and signal-definition limits. (20 words) **[METHOD]**
* **P.1.1** (“A neutrino is a nearly invisible…”): Neutrino cross sections measure interaction probabilities versus muon kinematics in the MINERvA detector. (14 words) **[METHOD]**
* **P.1.2** (“The difficulty is that the detector…”): Unfolding removes detector smearing and inefficiency, acting like delicate photographic deblurring to recover true physical distributions without amplifying noise. (20 words) **[METHOD]**
* **P.2.1** (“The traditional way to unfold builds…”): Traditional binned migration matrix unfolding scales poorly to multiple dimensions because required simulation statistics and matrix conditioning degrade rapidly. (20 words) **[METHOD]**
* **P.2.2** (“This analysis uses a different, machine-learning…”): OmniFold iteratively reweights simulated events using machine-learning classifiers to match observed detector data, yielding unfolded true distributions. (18 words) **[METHOD]**
* **P.2.3** (“The decisive advantage is what happens…”): OmniFold scales efficiently to higher dimensions by adding feature inputs rather than multiplying bins, though validation challenges remain. (19 words) **[METHOD]**
* **P.2.4** (“In a simulated experiment, truth is…”): Validation requires understanding definitions of truth, prior, and response, acknowledging that limited classifier capacity and iterations cause approximation errors. (20 words) **[METHOD]**
* **P.2.5** (“One more distinction matters later: which…”): Event selection differs from classifier input features; decision trees evaluate summary kinematics, while the experimental PET neural network ingests raw hits. (22 words) **[METHOD]**
* **P.3.1** (“Our results have different levels of…”): The analysis yields six distinct findings spanning 2D reproduction, multidimensional central values, physical features, joint tests, PET development, and extended fiducials. (22 words) **[MULTI]**
* **P.3.2** (“Before trusting a new method, one…”): OmniFold successfully reproduces the published 2D MINERvA cross section and total rate, with uncertainties closely matching published magnitudes. (19 words) **[RESULT]**
* **P.3.3** (“One qualification: two software implementations of…”): Two tree-learner implementations differ by ~1%, and the faster one was chosen post hoc to construct the covariance. (19 words) **[HIST]**
* **P.3.4** (“The error budget also has known…”): Historical errors in the 2D uncertainty budget were corrected, but reconstruction-failure approximations and model dependencies remain unquantified. (19 words) **[HIST]**
* **P.3.5** (“To test whether error bars have…”): Demonstrating frequentist coverage requires independent simulation samples and continuous nuisance variations, so no formal coverage claim is made. (19 words) **[CAVEAT]**
* **P.3.6** (“We did run such a test…”): An initial statistical undercoverage was patched, but the newly rebuilt statistical uncertainty band has not been independently validated. (19 words) **[HIST]**
* **P.3.7** (“With the central value reproduced, and…”): Simultaneous 5D unbinned unfolding recovers lower-dimensional normalizations, providing an internal consistency check for higher-dimensional extensions. (16 words) **[RESULT]**
* **P.3.8** (“These are five recorded coordinates, not…”): Reconstructed variables share common underlying hadronic and muon inputs, so five coordinates do not represent five independent physical constraints. (20 words) **[CAVEAT]**
* **P.3.9** (“The first physics payoff appears in…”): Four generators underestimate low available-energy data, recovering the known low-recoil discrepancy which two-nucleon processes partly mitigate. (17 words) **[RESULT]**
* **P.3.10** (“Adding the hadronic-mass axis W lets…”): Joint $(E_\text{avail}, W)$ distributions show an unquantified rate excess concentrated at high available energy and high $W$ relative to Tune v1. (22 words) **[RESULT]**
* **P.3.11** (“The multi-quantity central values above pass…”): Multidimensional results are presented as central values only, as their uncertainties failed predefined criteria and cannot support significance claims. (20 words) **[CAVEAT]**
* **P.3.12** (“Our method has a random component…”): Changing the classifier random seed shifts the $(E_\text{avail}, W)$ uncertainty by 6.1%, exceeding the pre-set 5% tolerance and resisting sample size scaling. (22 words) **[CAVEAT]**
* **P.3.13** (“Two further facts qualify the shift…”): Five fixed-seed systematic components were unmeasured under seed variations, while seed shifts move central values by ~6% of their uncertainty. (21 words) **[CAVEAT]**
* **P.3.14** (“One more thing is worth saying…”): Reweighted detector systematic uncertainties explain why some bands were not fully regenerated, but do not guarantee complete hadronic-response modeling. (20 words) **[CAVEAT]**
* **P.3.15** (“Two end-to-end tests limit what…”): Background subtraction introduces a 4% high-$W$ bias, while unfolding fails to fully recover generator-scale shape changes in available energy. (20 words) **[CAVEAT]**
* **P.3.16** (“A follow-up study looked inside the…”): Investigating regularization bias revealed persistent truth dependence and input rounding instability that exceeds statistical uncertainties on data. (18 words) **[HIST]**
* **P.3.17** (“Three possible remedies each have a…”): Proposed remedies like longer training or coarser cells introduce tradeoffs, while statistical interval coverage tests for 5D unfolding failed. (20 words) **[CAVEAT]**
* **P.3.18** (“None of these five-quantity findings affects…”): Multidimensional limitations do not compromise the standalone validity of the 2D reproduction and its independent uncertainty budget. (18 words) **[METHOD]**
* **P.3.19** (“We also asked a sharper question…”): Calibrated full-chain pseudo-experiments reject all ten total and shape hypotheses for five generators at the 5% familywise error level. (20 words) **[RESULT]**
* **P.3.20** (“This is a test of the…”): Generator test rejections are strictly conditional on six assumptions, including unmeasured sub-grid structure and omission of calorimetric recoil systematics. (20 words) **[CAVEAT]**
* **P.3.21** (“In a comparison chosen after the…”): Post-hoc tests show hadronic observables drive GENIE rejections, but joint 5D tests do not demonstrate greater discrimination than matched 2D projections. (22 words) **[CAVEAT]**
* **P.3.22** (“How robust are the rejections to…”): Rejections remain determinate under one-directional sub-grid shifts up to $5.2\,\delta_\text{fine}$, but actual convergence below the grid remains unmeasured. (19 words) **[CAVEAT]**
* **P.3.23** (“Two studies test the method’s limits…”): Exploratory studies investigate raw hit-level point-cloud networks (PET) and expanded truth signal phase space without contributing to published measurements. (20 words) **[METHOD]**
* **P.3.24** (“We ran PET, the “point-cloud…”): PET demonstrates hit-level unfolding for hadronic recoils, but serves purely as exploratory method development without contributing final cross sections. (20 words) **[METHOD]**
* **P.3.25** (“Completed simulation studies then improved how…”): PET design iterations improved simulated truth recovery from 31% to ~90%, but failed to satisfy pre-established progression criteria. (19 words) **[HIST]**
* **P.3.26** (“Better recovery was not enough: no…”): PET designs were rejected because one failed robustness rules while the other showed severe interval undercoverage in low-acceptance regions. (20 words) **[CAVEAT]**
* **P.3.27** (“Our diagnosis of the saved outputs…”): Archival diagnosis indicates that averaging bootstrap fits reduced empirical variance without correcting fundamental sample bias or ensuring proper coverage. (20 words) **[HIST]**
* **P.3.28** (“An exploratory comparison then ran OmniFold…”): PET outperforms decision trees on smooth energy tilts, but lags on generator reweightings, showing task-dependent performance without general superiority. (20 words) **[RESULT]**
* **P.3.29** (“For the three generator-model tests, a…”): Diagnostic investigations attribute PET's generator reweighting shortfalls to detector-level underfitting and poor extrapolation to missed events. (18 words) **[HIST]**
* **P.3.30** (“Separately, the published signal definition excludes…”): Relaxing muon kinematic selection expands the fiducial cross section, but 28% of the rate represents simulation-dominated extrapolation lacking detector support. (21 words) **[CAVEAT]**
* **P.4.1** (“Unbinned machine-learning unfolding reproduces a flagship…”): OmniFold enables multidimensional neutrino unfolding and generator tests, but unvalidated uncertainties and regularization bias necessitate presenting results as central values only. (21 words) **[MULTI]**

---

##### 2. The Argument Outline

###### A. Actual Line of Argument Reconstructed from the Map (12 Bullets)
1. **The Scaling Problem**: Multidimensional neutrino cross sections are essential for testing nuclear physics, but traditional binned migration matrices cannot scale beyond 2–3 observables due to dimensional explosion.
2. **The ML Promise**: Unbinned classifier-based unfolding (OmniFold) circumvents binned migration tensors, promising scalable simultaneous unfolding of arbitrarily many kinematic variables.
3. **The Baseline Benchmark**: OmniFold successfully reproduces MINERvA's published 2D muon cross section ($p_T, p_\parallel$) within 1.1% globally and yields uncertainty bands of comparable magnitude.
4. **Uncertainty Limitations in 2D**: The 2D covariance lacks independent frequentist coverage validation, displays estimator-software dependence ($\Delta\chi^2/\text{ndf} \approx 1$), and absorbs unmodeled run-period drift by construction.
5. **Scaling to 5D**: Adding calorimetric recoil variables ($E_\text{avail}, q_3, W$) produces 3D, 4D, and 5D central values that satisfy internal marginal-normalization consistency and simple toy closures.
6. **Procedural Failures in 5D**: Rigorous pseudo-experiments reveal severe procedural defects: a 4% high-$W$ background-subtraction bias, high sensitivity to numerical rounding, and strong regularization bias that recovers only a fraction of generator-scale shape shifts.
7. **Physical Features (Descriptive Only)**: Unfolded central values independently confirm the low-recoil ($E_\text{avail}$) deficit (mitigated by Valencia 2p2h) and reveal a localized excess at high $E_\text{avail}$ and high $W$ relative to MINERvA Tune v1; neither can be assigned statistical significance.
8. **Failure of the 5D Error Budget**: A 5D covariance matrix fails pre-declared acceptance criteria because changing the tree-learner's random seed shifts the uncertainty by 6.1% (exceeding the pre-declared 5% tolerance), forcing the authors to abandon reporting a 5D measurement with uncertainties.
9. **Pivot to Hypothesis Testing**: Unable to publish a calibrated 5D measurement, the authors pivot to calibrated hypothesis testing of five specific generator models on a coarse 5D grid.
10. **Full-Chain Calibration**: By rerunning the complete analysis chain across thousands of pseudo-experiments, the tests incorporate the estimator’s prior pull and systematic nuisances directly into the null distributions, rejecting all ten total and shape hypotheses at $\alpha = 0.05$ familywise error.
11. **Disqualification of Dimensional Value**: Matched 2D projections of the same data reject the same models, meaning the joint 5D information is not shown to provide any statistical discrimination beyond lower dimensions.
12. **Severely Conditional Rejections**: The rejections cannot be interpreted physically because the analysis omits calorimetric recoil-energy systematic uncertainties and relies on an unverified assumption of sub-grid convergence.

---

###### B. Typical PRD Outline for an Unfolding Measurement + Generator Tests
A standard Physical Review D experimental measurement follows a canonical deductive structure:
1. **Introduction**: Theoretical motivation (neutrino-nucleus modeling, oscillations), previous experimental status, and purpose of the multidimensional measurement.
2. **Experimental Setup & Beam**: NuMI beam flux, MINERvA detector technology, MINOS spectrometer matching.
3. **Event Selection & Background Subtraction**: Fiducial cuts, detector reconstruction, sideband tuning, and background estimation.
4. **Unfolding Methodology**: Unfolding formalism, detector response matrix, regularisation parameter optimization, and efficiency/acceptance corrections.
5. **Systematic Uncertainties**: Detailed breakdown of covariance matrices (flux, detector response, interaction models, unfolding/model bias).
6. **Cross-Section Results**: Tabulated and plotted differential cross sections ($d^n\sigma$) with complete error bars and correlation matrices.
7. **Model Comparisons & Generator Tests**: Goodness-of-fit ($\chi^2$ / $p$-values) comparing data to generator predictions (GENIE, NuWro, GiBUU), followed by physical discussion of nuclear mechanisms (2p2h, RPA, FSI).
8. **Conclusions**: Summary of measured cross sections, preferred models, and implications for future oscillation experiments.

---

###### C. Where This Paper Departs, and Whether It Helps or Hurts
1. **Inversion of Validation and Physics (Section IV precedes Section V)**:
   * *Departure*: Rather than presenting methodology, results, and uncertainties, the paper spends Section IV detailing extensive validation failures, seed instabilities, and code audit findings *before* presenting physical distributions.
   * *Verdict*: **Helps scientific integrity, but hurts narrative momentum**. In an unfolding paper where the core result is the discovery of methodological limits, placing validation first prevents the reader from anchoring on unvalidated central values. However, it gives the paper the flavor of an internal technical post-mortem rather than a physics paper.
2. **Bifurcation of Measurement and Inference (Withholding 5D Uncertainties and Pivoting to Sec. VI)**:
   * *Departure*: Typical PRD papers publish cross sections with an error band and calculate $\chi^2$ directly against generator curves. This paper completely suppresses 5D error bars (Sec. VII) and constructs a parallel, computationally massive simulation-calibration apparatus (Sec. VI) to test models without an unfolded covariance.
   * *Verdict*: **Helps statistical rigor; hurts archival utility**. The authors refuse to publish an unvalidated covariance matrix. However, because no 5D cross section or covariance is released, the data cannot be deposited in HEPData for global neutrino generator tuning, severely limiting the paper's utility to external theorists.
3. **Forensic Analysis-History Detail in Main Body Text**:
   * *Departure*: The main text documents earlier discarded implementations (exact-split trees), software bugs found during review (completeness divisor errors, unpropagated template noise), and cluster time-limit crashes.
   * *Verdict*: **Hurts**. This forensic bookkeeping belongs in an internal technical note or an appendix. Embedding it in the PRD main text clutters the scientific narrative and distracts from the final validated conclusions.
4. **Self-Disqualification of the Primary Scientific Claim (Sec. VI.C)**:
   * *Departure*: After establishing a 5D testing framework, the authors prove that matched 2D projections yield identical rejections, demonstrating that their 5D joint information provides no added discrimination.
   * *Verdict*: **Helps scientific honesty immensely**. In an era of machine-learning hype, explicitly demonstrating that an unbinned 5D technique yields zero demonstrable power gain over coarse 2D projections is a vital negative result that saves future experimentalists from futile complexity.

---

##### 3. Proportions

###### A. Fraction of Text by Category per Section and Overall

| Section | Method | Results | Caveats | History |
| :--- | :---: | :---: | :---: | :---: |
| **Abstract** | 20% | 25% | 45% | 10% |
| **I. Introduction** | 45% | 15% | 35% | 5% |
| **II. Data, Signal, Simulation** | 80% | 0% | 20% | 0% |
| **III. Unbinned Unfolding** | 85% | 0% | 10% | 5% |
| **IV. Validation** | 25% | 15% | 45% | 15% |
| **V. Central-Value Results** | 10% | 60% | 30% | 0% |
| **VI. Calibrated Joint Tests** | 35% | 25% | 30% | 10% |
| **VII. Status of 5D Uncertainty** | 10% | 0% | 60% | 30% |
| **VIII. Conclusions** | 20% | 25% | 50% | 5% |
| **OVERALL (Paper)** | **37%** | **17%** | **36%** | **10%** |

---

###### B. Appropriateness for the Genre
* **Standard PRD Experimental Baseline**: A typical PRD measurement devotes ~35–45% to Method, ~35–45% to Results, ~15–20% to Systematics/Caveats, and <2% (ideally 0%) to History.
* **Assessment of this Paper**:
  * **Results (17%) is severely depressed**: Less than a fifth of the text reports physical cross sections or inference decisions.
  * **Caveats (36%) is double the normal level**: Over a third of the paper is defensive prose detailing what the analysis *cannot* conclude.
  * **History (10%) is drastically anomalous**: Devoting 10% of a PRD paper to software evolution, bug fixes, and cluster job management violates the journal's premise as an archival record of physics rather than a development log.
* **Editorial Verdict**: The balance is **inappropriate for a standard PRD cross-section paper**, but **appropriate for a critical methodological benchmark**. The authors intended to write a measurement paper, hit fundamental machine-learning and systematic roadblocks, and converted the manuscript into a cautionary methodological study. To conform to PRD standards, the historical and software-debugging sections should be excised to supplemental technical notes, condensing the text around two poles: the 2D benchmark and the calibrated 5D hypothesis tests.

---

##### 4. Repetition of Limitations

The manuscript displays significant anxiety regarding its limitations, stating several caveats up to five times:

1. **Regularization Bias / Inability to Recover Generator-Scale $E_\text{avail}$ Tilts**:
   * *Locations*: Abstract; Sec. I (para 5); Sec. IV.C (para 2); Sec. V (para 2); Sec. VIII (para 1).
   * *Best Single Place*: **Section IV.C** (Validation of Higher-Dimensional Central Values). This is where closure tests are quantitatively presented. Abstract and Conclusions need only a one-clause summary.
2. **Omission of Calorimetric Recoil-Energy Response Systematics**:
   * *Locations*: Abstract; Sec. I (para 5); Sec. VI.B (Condition ii); Sec. VI.D (para 1 & 2); Sec. VIII (para 2).
   * *Best Single Place*: **Section VI.D** (Hadronic-Response Condition). Stating it in full detail here, while simply listing it in the enumerated conditions of VI.B, eliminates three unnecessary repetitions.
3. **Unverified Sub-Fine-Grid Convergence / Unknown Residual Below Grid ($\pm 2\delta_\text{fine}$)**:
   * *Locations*: Abstract; Sec. I (para 5); Sec. VI.A (para 3); Sec. VI.B (Condition i); Sec. VI.C (para 1); Sec. VIII (para 2).
   * *Best Single Place*: **Section VI.B** (Conditions of the Test). Condition (i) is the exact mathematical definition of the hybrid null; repeating the geometric extrapolation rationale elsewhere is redundant.
4. **Estimator Random-Seed Sensitivity / Failure of the 5% Covariance Target**:
   * *Locations*: Abstract; Sec. I (para 3 & 5); Sec. IV.C (para 2); Sec. VII (para 1); Sec. VIII (para 1).
   * *Best Single Place*: **Section VII** (Status of a Five-Dimensional Uncertainty). This section is specifically dedicated to the failure of the 5D covariance budget.
5. **No Demonstrated Power Advantage of 5D Joint Information over Matched 2D Projections**:
   * *Locations*: Abstract; Sec. I (para 5); Sec. VI.C (para 3); Sec. VIII (para 2).
   * *Best Single Place*: **Section VI.C** (Results of Calibrated Joint Tests). This belongs strictly alongside the discussion of test power and projection results.
6. **Untested Frequentist Coverage of 2D/5D Uncertainty Intervals**:
   * *Locations*: Abstract; Sec. I (para 5); Sec. IV.B (para 3 & 4); Sec. IV.C (para 2); Sec. VIII (para 1).
   * *Best Single Place*: **Section IV.B** (for 2D) and **Section IV.C** (for 5D).
7. **Purity-Based Background Subtraction Bias (~4% at high $W$)**:
   * *Locations*: Abstract; Sec. I (para 5); Sec. III (para 3); Sec. IV.C (para 1); Sec. VIII (para 1).
   * *Best Single Place*: **Section IV.C** (where the comparison between purity and unbinned negative-weight refinement is shown).
8. **Learner / Software-Package Dependence (LightGBM vs. Exact-Split GBDT, $\Delta\chi^2/\text{ndf} \approx 1$)**:
   * *Locations*: Sec. I (para 5); Sec. III (para 3); Sec. IV.A (para 1); Sec. IV.B (para 4); Sec. VIII (para 1).
   * *Best Single Place*: **Section IV.A** (Two-Dimensional Reproduction).
9. **Shared Kinematic Inputs Among $E_\text{avail}, q_3, W$ (Non-Independent Constraints)**:
   * *Locations*: Sec. I (para 2); Sec. II (para 2).
   * *Best Single Place*: **Section II** (Data, Signal, and Simulation).
10. **GiBUU Truncation at $E_\nu = 20\text{ GeV}$ Biasing High-$W$ Ratios**:
    * *Locations*: Sec. II (para 3); Sec. V (para 3); Sec. VI.A (para 1); Sec. VI.B (Condition v).
    * *Best Single Place*: **Section II** (Signal and Simulation definitions).

---

##### 5. The Abstract of the Paper

###### A. Sentence-by-Sentence Breakdown and Labeling
1. *“We test the practical limits of multidimensional unbinned unfolding with OmniFold on MINERvA open data for medium-energy $\nu_\mu$ charged-current inclusive interactions.”*  
   $\rightarrow$ **Scope / Context** (Introductory framing).
2. *“The analysis reproduces the published double-differential cross section in muon kinematics and extends it to five simultaneous observables by adding available energy, three-momentum transfer, and hadronic invariant mass.”*  
   $\rightarrow$ **Headline Result** (Primary positive milestone).
3. *“The higher-dimensional central values pass checks of their marginal normalizations against the lower-dimensional results, and the three- and four-observable central values pass closure checks with injected shape changes.”*  
   $\rightarrow$ **Headline Result** (Validation milestone).
4. *“Pseudo-experiments that include backgrounds, and studies of the uncertainties, show limitations of the background treatment, the regularization, the interval coverage, and the stability under changes of the estimator’s random seed.”*  
   $\rightarrow$ **Qualification** (Methodological failure modes).
5. *“The measured model dependence prevents a five-dimensional measurement with total uncertainties that meet our predefined criteria at useful precision.”*  
   $\rightarrow$ **Qualification** (Crucial negative result: suppression of 5D measurement).
6. *“Generator tests, calibrated with pseudo-experiments that rerun the full analysis chain under a stated nuisance model, reject all five tested predictions (MINERvA Tune v1, GENIE 2.12.10 with and without Valencia two-particle–two-hole contributions, NuWro 21.09, and GiBUU 2019) in total and in shape at the 5% familywise level.”*  
   $\rightarrow$ **Headline Result** (Primary statistical inference result).
7. *“These rejections hold only under stated conditions.”*  
   $\rightarrow$ **Qualification** (Epistemic disclaimer).
8. *“The tests recover known discrepancies, but they do not show that the tested joint five-observable information discriminates beyond matched coarse projections of the same cells.”*  
   $\rightarrow$ **Qualification** (Deflating the value of the 5D feature space).
9. *“Their physical interpretation is limited because the nuisance model has no calorimetric recoil-response uncertainty and because convergence of the fine grid on which the null hypotheses are defined has not been shown.”*  
   $\rightarrow$ **Qualification** (Systematic model deficiencies).

*Summary*: 3 Headline Results, 5 Qualifications, 1 Scope statement. The current abstract contains 228 words.

---

###### B. Proposed 120–160-Word Abstract
> We test multidimensional unbinned unfolding using OmniFold on MINERvA open data for $\nu_\mu$ charged-current inclusive interactions. The analysis reproduces the published double-differential muon cross section within 1.1% and extends it to five simultaneous observables by adding available energy, three-momentum transfer, and hadronic invariant mass. While higher-dimensional central values satisfy marginal consistency checks, pseudo-experiments reveal that regularization bias, training-seed instability, and unmodeled coverage prevent reporting a five-dimensional measurement with validated total uncertainties. Instead, we perform full-chain calibrated hypothesis tests of five generator models across a 109-cell five-dimensional volume. At the 5% familywise error level, all five models—including MINERvA Tune v1 and GENIE with Valencia 2p2h—are rejected in rate and shape. These rejections recover known discrepancies, but matched two-dimensional projections achieve comparable rejection power, showing no demonstrated discrimination gain from the joint five-dimensional information. Furthermore, physical interpretation remains conditional on the detector's calorimetric recoil response and unverified sub-grid convergence. *(155 words)*

---

###### C. Why Abstracts of This Kind Grow, and How to Stop It
* **The Mechanism of Growth (“Epistemic Debt”)**:  
  When authors attempt extreme transparency, every assertive claim of a result immediately triggers a feeling of epistemic dishonesty unless paired with its exact boundary conditions. A sentence stating *"we extend unfolding to 5D"* feels fraudulent to the author unless immediately followed by *"but we cannot quote 5D uncertainties."* Then, stating *"we rejected all five generators"* feels misleading unless followed by *"but this holds under six conditions,"* which in turn demands specifying *which* conditions are most fatal (missing recoil response and sub-grid convergence). The abstract rapidly degenerates into a defensive legal contract.
* **How to Stop It**:
  1. **Shift from listing caveats to defining output types**: Rather than claiming a 5D measurement and qualifying it into oblivion, state cleanly upfront that the 5D output is restricted to *unvalidated central values* and *calibrated hypothesis tests*.
  2. **Synthesize failure modes into a single structural sentence**: Group specific pathologies (seed shifts, rounding noise, purity bias, regularization bias) under overarching statistical categories (e.g., *"regularization bias and training-seed instability prevent reporting validated total uncertainties"*).
  3. **Rely on the functional division of a paper**: An abstract’s duty is indexing and mapping claims, not executing the defense. Trust the reader to read Sections IV.C, VI.B, and VII for the technical conditions.

---

##### 6. Primer Analysis (For Non-Specialists)

###### A. Critique of Current Ordering
The current structure of `primer.txt` severely disserves a physics-literate non-specialist:
1. **Premature Architectural & Diagnostic Clutter (Section 2 & Table 1)**:  
   Immediately after introducing neutrinos in Section 1, Section 2 abruptly presents Table 1 (distinguishing closure, coverage, bookkeeping, and stability) and contrasts GBDTs with PET point-cloud transformers. A non-specialist has not yet been shown what physical question is being asked or what the data look like.
2. **Forensic Audit Intrudes Before Physics (Section 3, Subsections 1 & 4)**:  
   Before reaching the physics discoveries (the low-recoil anomaly in 3.9 and the $(E_\text{avail}, W)$ corner excess in 3.10), the reader is subjected to a blow-by-blow forensic history of software bugs (pion-weight double-counting, completeness divisor patches, LightGBM vs. exact-split differences).
3. **Decoupling Discoveries from Their Invalidating Caveats**:  
   Section 3 presents exciting physical features in Fig. 3 and Fig. 4 ("A new puzzle for the tuned simulation"), but hides the devastating caveats—that these central values have failed coverage tests, possess no statistical significance, and shift with random seeds—in a completely separate subsequent subsection ("Limits on the multi-quantity results"). A reader is led down a path of excitement only to be deflated pages later.
4. **Dead-End Methodological Side Quests at the Climax (Subsection 6)**:  
   The primer concludes by spending eight dense paragraphs detailing PET (point-cloud transformers) and extended fiducial definitions—two R&D efforts that failed pre-declared criteria and contributed *zero* final results to the measurement.

---

###### B. Proposed Restructuring for `primer.txt`
A non-specialist narrative must follow an intuitive pedagogical trajectory:  
**The Goal $\rightarrow$ The Core Innovation $\rightarrow$ The Benchmark $\rightarrow$ The Physical Payoff & Its Real-World Limits $\rightarrow$ The Workaround (Hypothesis Testing) $\rightarrow$ The Horizon (R&D).**

```markdown
1. The Challenge: Deblurring Neutrino Interactions
   - 1.1 The invisible beam: how MINERvA records neutrino collisions.
   - 1.2 The deblurring problem: why detector smearing demands unfolding.

2. The New Tool: Machine Learning Without Tables
   - 2.1 The curse of bins: why traditional unfolding cannot scale beyond two variables.
   - 2.2 Unbinned OmniFold: teaching simulations to morph into data using classifiers.
   - 2.3 The scaling advantage: adding physical observables as features, not matrix dimensions.

3. The Trust Check: Reproducing an Established 2D Measurement
   - 3.1 Validating the baseline: matching MINERvA's published muon cross section within 1%.
   - 3.2 Sizing the error bars: independently deriving consistent experimental uncertainties.
   - 3.3 A transparent caveat: small software-choice differences and why we claim no coverage.

4. Stepping into Five Dimensions: Physical Payoffs and Methodological Limits
   - 4.1 Measuring five variables at once: combining muon motion with nuclear recoil energy.
   - 4.2 Rediscovering known physics: the low-energy recoil deficit and two-nucleon kicks (2p2h).
   - 4.3 A localized puzzle: the high-energy, high-mass corner excess over MINERvA Tune v1.
   - 4.4 The catch: why these multi-variable plots show central values only (no error bars).
   - 4.5 Why ML error bars are hard: random-seed sensitivity, rounding noise, and regularization bias.

5. A Rigorous Pivot: Testing Simulations When Measurements Fail
   - 5.1 Changing the question: from extracting cross sections to testing model hypotheses.
   - 5.2 Calibrated pseudo-experiments: accounting for machine-learning bias by simulating the full chain.
   - 5.3 The verdict: why all five standard simulations fail to match the data.
   - 5.4 The sobering reality check: why 5D machine learning provided no extra power over simple 2D views.
   - 5.5 Essential fine print: missing calorimeter response errors and sub-grid assumptions.

6. Exploratory Frontiers: Raw Detector Hits and Expanded Boundaries (Optional Deep Dive)
   - 6.1 Point-cloud transformers (PET): attempting hit-level unfolding on raw energy deposits.
   - 6.2 Lessons from PET: why neural-network intervals undercovered in low-acceptance regions.
   - 6.3 Enlarging the signal definition: separating detector-backed data from simulation extrapolation.

7. Key Takeaways
   - 7.1 What worked, what failed, and the practical roadmap for AI in neutrino physics.
```

##### Rationale for this Order
* **Pedagogical Anchoring**: Begins with the tangible physics challenge (deblurring/unfolding) and shows why OmniFold is conceptually revolutionary before introducing any code or mathematical checks.
* **Immediate Truth in Advertising (Section 4)**: The moment higher-dimensional physical discrepancies (the low-recoil gap and high-$W$ corner) are displayed, the text immediately explains *why* error bars are omitted, linking the physical observation directly to the seed-instability and regularization-bias diagnostics.
* **Separation of Core Results from Exploratory R&D**: Moves PET and extended fiducial volume studies into an explicit post-conclusion "Frontiers / Appendices" section, preventing exploratory dead-ends from derailing the main scientific narrative.

---

## P6. X1 GPT-6.1-sol: outline analysis of the pass-1 paper and primer (sha256 `f3e5febe66c3acdb…`)

The paper’s strongest structural identity is **a study of what can and cannot be validated in multidimensional unfolding, followed by conditional generator tests**. It is less successful as a conventional measurement paper: its measurement claims repeatedly stop for qualifications, while its strongest inferential result arrives late.

The primer has a more fundamental problem. It explains the same work but also includes two substantial projects—PET and an expanded signal definition—that the paper does not present. Its structure consequently resembles a guide to the analysis program rather than a guide to this paper.

I treat paragraphs continued across page breaks as single paragraphs. References, equations, plot labels, and author information are excluded. Captions and list items are mapped separately. Tags can overlap; untagged entries provide context or orientation. Main-idea sentences below contain at most 25 words; quoted identifiers are separate.

#### 1. Paragraph main-idea maps

##### Paper

| Location | Identifying phrase | Main idea |
|---|---|---|
| Abstract.1 | “We test the practical limits” | [MULTI] The study extends unfolding, identifies validation limits, and conditionally rejects five generator predictions without demonstrating added joint discrimination. |

**I. Introduction**

| Location | Identifying phrase | Main idea |
|---|---|---|
| I.1 | “Multidifferential neutrino cross sections” | OmniFold offers a practical route around the rapidly growing response tensors required for multidimensional binned unfolding. |
| I.2 | “We apply the method” | [METHOD] The analysis extends a published muon measurement to five observables that share reconstructed information. |
| I.3 | “We assess how reliable” | [METHOD] Reproduction, projection comparisons, closure, and repeated unfoldings assess the method’s practical reliability. |
| I.4 | “As an application” | [METHOD] Generator tests calibrate the full analysis chain so that estimator bias enters the null distributions. |
| I.5 | “The two-dimensional reproduction agrees” | [MULTI][RESULT][CAVEAT] Reproduction and selected validation checks succeed, but measurement limitations and conditional generator rejections restrict the conclusions. |
| I.6 | “Sections II and III” | The remaining sections separate inputs, estimators, validation, central values, generator tests, and uncertainty status. |

**II. Data, signal, and simulation**

| Location | Identifying phrase | Main idea |
|---|---|---|
| II.1 | “The analysis uses the twelve” | [METHOD] The analysis uses MINERvA open data, the published selection and signal definition, and tuned GENIE simulation. |
| II.2 | “The unfolded observables are defined” | [METHOD][CAVEAT] Truth and reconstructed observable definitions include an inherited pion-energy convention and shared reconstructed hadronic information. |
| II.3 | “Event selection is held fixed” | [MULTI][METHOD][CAVEAT] The selection remains fixed as dimensions increase, while external generator samples differ in target composition and energy coverage. |

II.3 contains two separable subjects: the measurement population and the comparison samples. They deserve separate paragraphs.

**III. Unbinned unfolding**

| Location | Identifying phrase | Main idea |
|---|---|---|
| III.1 | “Each OmniFold iteration” | [METHOD] Alternating reconstruction- and truth-level classifiers produce event weights that yield unfolded cross sections. |
| III.2 | “Backgrounds enter” | [METHOD] Purity subtraction and unbinned negative-weight refinement match different within-bin background-subtracted target densities. |
| III.3 | “All estimator configurations” | [MULTI][METHOD][HIST] Several classifier configurations serve central values, cross-checks, and generator tests, with different background treatments and selection histories. |

III.3 is the paper’s principal configuration bottleneck. It combines common settings, regularization, an architecture comparison, estimator assignments, a superseded choice, and joint-test design.

**IV. Validation**

| Location | Identifying phrase | Main idea |
|---|---|---|
| IV.1 | “In closure tests, truth denotes” | [METHOD] Closure, coverage, bookkeeping, and iteration stability answer distinct validation questions. |

**IV.A. Two-dimensional reproduction**

| Location | Identifying phrase | Main idea |
|---|---|---|
| IV.A.1 | “The two-dimensional result” | [MULTI][RESULT][CAVEAT][HIST] The reproduction closely matches normalization but retains correlated shape differences and unbudgeted learner dependence after a retrospective estimator choice. |
| IV.A.2 | “Both results derive” | [CAVEAT] Shared data make the comparison procedural, while a significance for the difference requires the missing cross-covariance. |

**IV.B. Two-dimensional uncertainty and its coverage**

| Location | Identifying phrase | Main idea |
|---|---|---|
| IV.B.1 | “The covariance … four terms” | [METHOD][RESULT][CAVEAT] Four covariance blocks give uncertainties comparable to the publication, with unresolved flux differences and a poorly determined seed contribution. |
| IV.B.2 | “The systematic-universe unfoldings approximate” | [MULTI][CAVEAT] An incompletely tested missed-event approximation and unexplained run-period disagreement limit interpretation of the covariance. |
| IV.B.3 | “The statistical block is a bootstrap” | [MULTI][HIST][CAVEAT] The current bootstrap lacks coverage validation; earlier bands failed, were rebuilt, and were reassessed without an independent test. |
| IV.B.4 | “In summary, we report” | [CAVEAT] The reported covariance omits several dependencies and supports neither validated coverage nor calibrated generator significance. |

IV.B.2 should divide at “Data from different run periods.” IV.B.3 should separate the **current statistical construction**, **current validation status**, and **superseded-band history**.

**IV.C. Higher-dimensional central values**

| Location | Identifying phrase | Main idea |
|---|---|---|
| IV.C.1 | “Each higher-dimensional central value” | [RESULT][CAVEAT] Marginal checks and selected closure tests succeed, while end-to-end tests expose background bias reduced by unbinned subtraction. |
| IV.C.2 | “The unfolding recovers only part” | [MULTI][CAVEAT] Regularization bias, rounding sensitivity, and failed interval validation limit higher-dimensional measurement claims and motivate calibrated tests. |

**V. Central-value results**

| Location | Identifying phrase | Main idea |
|---|---|---|
| V.1 | “The Eavail dimension provides” | [RESULT] The central values recover the low-recoil deficit, which tested 2p2h additions reduce more than the chosen pion-FSI variations. |
| V.2 | “Adding q3 resolves” | [RESULT][CAVEAT] Agreement with a dedicated low-recoil measurement is descriptive because available-energy definitions differ. |
| V.3 | “The fifth observable, W” | [RESULT][CAVEAT] Relative to Tune v1, much positive excess occupies high-energy, high-mass cells, without established significance or response-mismatch validation. |
| V.4 | “The one-dimensional projections” | [RESULT][CAVEAT] External generators underpredict the rate, but the high-energy, high-mass concentration depends on the reference prediction and GiBUU’s energy coverage. |

V.4 has a coherent comparative purpose, although it would read more clearly as separate **external-generator findings** and **interpretive boundaries** paragraphs.

**VI.A. Hypotheses, statistics, and calibration**

| Location | Identifying phrase | Main idea |
|---|---|---|
| VI.A.1 | “For each of five predictions” | [METHOD] Hybrid nulls specify generator rates on a fine grid and are tested on supported coarse cells. |
| VI.A.2 | “A total statistic” | [METHOD] Total and shape residual statistics use a regularized covariance metric incorporating prediction-sample variance. |
| VI.A.3 | “The null distribution” | [METHOD] Full-chain pseudo-experiments calibrate statistics under specified nuisance variations and conservative shifted nulls. |
| VI.A.4 | “The ten tests are controlled” | [MULTI][METHOD][HIST] Multiplicity and Monte Carlo decision rules govern testing, while disclosures document data-informed design choices and independent recomputation. |

**VI.B. Conditions**

| Location | Identifying phrase | Main idea |
|---|---|---|
| VI.B.1 | “The decisions test the hybrid null” | [CAVEAT] Six conditions restrict the tests, especially unbounded sub-grid structure and the missing calorimetric recoil-response uncertainty. |

Although technically one paragraph, VI.B.1 is effectively a subsection compressed into a paragraph. Condition (i) alone warrants its own paragraph.

**VI.C. Results**

| Location | Identifying phrase | Main idea |
|---|---|---|
| VI.C.1 | “Table I lists” | [RESULT][CAVEAT] All ten tests reject, and a directional sensitivity scan preserves rejection without bounding the actual sub-grid error. |
| VI.C.2 | “Batch-job time limits” | [HIST][RESULT] Recovery of interrupted pseudo-experiments leaves every rejection unchanged. |
| VI.C.3 | “The comparisons recover” | [RESULT][CAVEAT] Calibration recovers known disagreements but demonstrates neither additional joint discrimination nor a localized physical explanation. |
| VI.C.4 | “Power studies characterize” | [RESULT] Power varies strongly with the null prediction and the selected alternative. |

**VI.D. Hadronic-response condition**

| Location | Identifying phrase | Main idea |
|---|---|---|
| VI.D.1 | “MINERvA’s recoil-energy analyses assign” | [CAVEAT] The missing recoil-response band matters because hadronic information contributes to at least one rejection. |
| VI.D.2 | “In an exploratory sensitivity study” | [RESULT][CAVEAT] Rejections survive reconstructed-energy rescaling, but unchanged calibration distributions prevent this check from resolving the response-model limitation. |

**VII. Status of a five-dimensional uncertainty**

| Location | Identifying phrase | Main idea |
|---|---|---|
| VII.1 | “We have built a covariance” | [CAVEAT] The five-dimensional covariance fails predefined requirements and exhibits incompletely characterized seed sensitivity. |
| VII.2 | “A separate study looked” | [RESULT][CAVEAT] No studied measurement definition meets the precision targets; calibrated generator tests provide a separate form of inference. |

**VIII. Conclusions**

| Location | Identifying phrase | Main idea |
|---|---|---|
| VIII.1 | “This study applies OmniFold” | [MULTI][RESULT][CAVEAT] Reproduction and higher-dimensional central values establish practical capabilities while bias and uncertainty validation constrain measurement claims. |
| VIII.2 | “The generator comparisons illustrate” | [RESULT][CAVEAT] Conditional generator rejections survive computational recovery but establish neither added joint discrimination nor unrestricted physical interpretation. |

**Back matter**

| Location | Identifying phrase | Main idea |
|---|---|---|
| Acknowledgments.1 | “The authors thank” | [MULTI] The authors acknowledge collaborators and computing support, then disclose AI assistance, verification practices, and responsibility. |
| Data.1 | “The input data and simulation” | [METHOD][CAVEAT][HIST] Archived inputs and a candidate release support partial reproduction, with unresolved deposition and estimator-version limitations. |

**Captions and table**

| Location | Main idea |
|---|---|
| Fig. 1 | [RESULT][CAVEAT] Muon projections reproduce the publication closely, but correlated bands and omitted learner dependence limit compatibility interpretations. |
| Fig. 2 | [RESULT] Joint ratio and integrated-difference maps show complementary views of departures from Tune v1, including overflow-cell weighting. |
| Fig. 3 | [RESULT][CAVEAT] Central-value projections compare external generators without uncertainty bands or statistical significance. |
| Fig. 4 | [RESULT] Calibrated null distributions account for estimator-induced displacement and locate the observed statistics. |
| Table I | [RESULT][METHOD] Monte Carlo counts, p values, thresholds, and intervals document the ten rejection decisions. |

No paragraph needs **[NONE]**. The problem is usually excessive scope or competing functions, not absence of an identifiable subject.

##### Primer

For its unnumbered subsections, I use:

- **2.A:** “What the checks tell us”
- **3.O:** opening overview
- **3.A:** reproduction
- **3.B:** more quantities and known physics
- **3.C:** tuned-simulation puzzle
- **3.D:** multi-quantity limitations
- **3.E:** joint tests
- **3.F:** alternative representations and signal definitions

**Abstract and Sections 1–2**

| Location | Identifying phrase | Main idea |
|---|---|---|
| Abstract.1 | “This is a short, jargon-light guide” | [MULTI] The guide introduces unfolding, summarizes selected findings, and emphasizes a partly simulation-dependent extension of the signal definition. |
| 1.1 | “A neutrino is a nearly invisible particle” | A neutrino cross section describes interaction frequency as a function of the outgoing muon’s motion. |
| 1.2 | “The difficulty is” | Unfolding attempts to recover true distributions from detector-blurred observations without amplifying noise. |
| 2.1 | “The traditional way” | Binned unfolding becomes increasingly demanding as additional measured quantities enlarge the migration matrix. |
| 2.2 | “This analysis uses” | [METHOD] OmniFold repeatedly reweights paired simulated events until reconstructed predictions resemble the data. |
| 2.3 | “The decisive advantage” | [METHOD][CAVEAT] Additional inputs avoid new migration tables but still increase training, simulation, and uncertainty demands. |
| 2.A.1 | “In a simulated experiment” | [METHOD] Truth, prior, response, and approximation error identify different sources of unfolding behavior. |
| 2.A.2 | “One more distinction matters later” | [MULTI][METHOD] Selection, learner inputs, PET variants, and truth-domain extensions define distinct analysis choices. |

2.A.2 introduces several concepts before readers know why they need them. PET and relaxed truth cuts interrupt the main explanation.

**3.O. Findings overview**

| Location | Identifying phrase | Main idea |
|---|---|---|
| 3.O.1 | “Our results have different levels” | The findings require different interpretations because their validation status differs. |
| 3.O.B1 | “A published result, reproduced” | [RESULT][CAVEAT] The published central value is closely reproduced, but learner dependence and unvalidated uncertainties limit the comparison. |
| 3.O.B2 | “More quantities at once” | [CAVEAT] Higher-dimensional central values pass selected checks, while biases and failed uncertainty requirements preclude validated error bars. |
| 3.O.B3 | “Known and new features” | [RESULT][CAVEAT] Central values show a known low-recoil deficit and a Tune v1 excess without assigned significance. |
| 3.O.B4 | “A joint test” | [RESULT][CAVEAT] Conditional total and shape tests reject five simulations without resolving sub-grid uncertainty. |
| 3.O.B5 | “A neural network” | [CAVEAT] PET studies improve recovery but produce no validated measurement or uncertainty. |
| 3.O.B6 | “A wider signal definition” | [RESULT][CAVEAT] An enlarged truth domain contains both newly detector-supported rate and substantial simulation-dependent extrapolation. |
| 3.O.2 | “Each result is only” | [CAVEAT] Each finding’s interpretation is restricted to its own validation evidence. |

**3.A. First, a trust check**

| Location | Identifying phrase | Main idea |
|---|---|---|
| 3.A.1 | “Before trusting a new method” | [RESULT][CAVEAT] Central values and uncertainty sizes resemble the published measurement, although correlated shape and unexplained flux-uncertainty differences remain. |
| 3.A.2 | “One qualification” | [HIST][CAVEAT] The quoted learner was selected after comparing implementations whose results differ. |
| 3.A.3 | “The error budget also” | [HIST][CAVEAT] The rebuilt error budget corrects earlier construction errors but still omits several dependencies. |
| 3.A.4 | “To test whether error bars” | [METHOD][CAVEAT] Coverage requires repeated simulated experiments, and broader validation needs independent simulation and nuisance-generation inputs. |
| 3.A.5 | “We did run such a test” | [HIST][CAVEAT] Earlier statistical intervals undercovered; their main defect was removed, but the currently quoted intervals remain untested. |

**3.B. More quantities and known physics**

| Location | Identifying phrase | Main idea |
|---|---|---|
| 3.B.1 | “With the central value reproduced” | [RESULT] Simultaneous unfolding extends to five quantities while retaining agreement in marginal normalization. |
| 3.B.2 | “These are five recorded coordinates” | [CAVEAT] Shared reconstructed inputs mean five coordinates do not establish five independent measurable directions. |
| 3.B.3 | “The first physics payoff” | [RESULT][CAVEAT] Low-energy central values recover a known deficit partly reduced by 2p2h, without uniquely identifying its origin. |

**3.C. A new puzzle**

| Location | Identifying phrase | Main idea |
|---|---|---|
| 3.C.1 | “Adding the hadronic-mass axis” | [MULTI][RESULT][CAVEAT] The Tune v1 joint excess appears localized, but external-generator normalization, GiBUU coverage, and seed effects complicate interpretation. |

The paragraph moves from observation to comparisons, sample limitations, numerical stability, and a stronger physics claim. Those are distinct argumentative steps.

**3.D. Limits on the multi-quantity results**

| Location | Identifying phrase | Main idea |
|---|---|---|
| 3.D.1 | “The multi-quantity central values” | [CAVEAT] The five-quantity uncertainty fails predefined requirements and therefore supports no significance claims. |
| 3.D.2 | “Our method has a random component” | [CAVEAT] Measured covariance sensitivity exceeds the seed threshold and does not diminish across the tested ensemble sizes. |
| 3.D.3 | “Two further facts” | [CAVEAT] Untested fixed-seed components and seed-dependent central values further limit interpretation of the measured covariance shift. |
| 3.D.4 | “One more thing … detector uncertainties” | [METHOD][CAVEAT] Different detector variations require different implementations, which does not establish completeness of the hadronic-response uncertainty model. |
| 3.D.5 | “Two end-to-end tests” | [CAVEAT] Background subtraction and incomplete recovery of a changed truth cause biases absent from the quoted uncertainty. |
| 3.D.6 | “A follow-up study” | [MULTI][HIST][CAVEAT] Follow-up studies diagnose background bias, persistent regularization error, and rounding sensitivity with estimator-specific bootstrap behavior. |
| 3.D.7 | “Three possible remedies” | [CAVEAT] Tested remedies do not establish a bias–variability tradeoff or validated five-quantity interval coverage. |
| 3.D.8 | “None of these five-quantity findings” | [CAVEAT] The higher-dimensional limitations do not replace the separately constructed two-dimensional uncertainty or its stated qualifications. |

**3.E. A joint test**

| Location | Identifying phrase | Main idea |
|---|---|---|
| 3.E.1 | “We also asked a sharper question” | [MULTI][METHOD][RESULT][HIST] Hybrid-null pseudo-experiments reject all ten hypotheses, and recovered interrupted simulations leave the decisions unchanged. |
| 3.E.2 | “This is a test … six conditions” | [CAVEAT] Six modelling and simulation conditions define the scope of the generator rejections. |
| 3.E.B1 | “structure finer than the grid” | [CAVEAT] The test does not resolve structure below its hypothesis grid. |
| 3.E.B2 | “detector-uncertainty model” | [CAVEAT] Calibration omits a calorimetric hadronic-recoil response band. |
| 3.E.B3 | “interaction-model variations” | [CAVEAT] Interaction-model uncertainty is restricted to the stated variations and negative-weight clipping. |
| 3.E.B4 | “a calibration shift” | [CAVEAT] Calibration and data unfolding use different simulation sizes, addressed through a bounded shift. |
| 3.E.B5 | “range of neutrino energies” | [CAVEAT] Generator samples cover restricted neutrino-energy ranges. |
| 3.E.B6 | “finite size” | [CAVEAT] Each prediction is represented by a finite simulated sample. |
| 3.E.3 | “Sensitivity to numerical rounding” | [METHOD][CAVEAT] Rounding checks and detailed conditions accompany tests that provide no new measurement uncertainty. |
| 3.E.4 | “In a comparison chosen after” | [RESULT][CAVEAT] Hadronic information contributes to GENIE CV rejection, without establishing added power from the full joint test. |
| 3.E.5 | “How robust are the rejections” | [RESULT][CAVEAT] A directional grid-sensitivity scan finds where decisions become ambiguous without bounding the actual unresolved error. |

**3.F. Alternative representations and signal definitions**

| Location | Identifying phrase | Main idea |
|---|---|---|
| 3.F.1 | “Two studies test” | Two additional studies explore methodological limits rather than adding measurement results. |
| 3.F.2 | “We ran PET” | [METHOD][CAVEAT] Recoil-only and full-event PET implementations remain development exercises without measurement outputs. |
| 3.F.3 | “Completed simulation studies then” | [HIST][RESULT] Successive PET studies improve recovery of injected distributions without initially qualifying designs for interval validation. |
| 3.F.4 | “Better recovery was not enough” | [RESULT][CAVEAT] Neither leading PET design satisfies all requirements, and one exhibits sharply acceptance-dependent coverage failures. |
| 3.F.5 | “Our diagnosis of the saved outputs” | [METHOD][CAVEAT] Averaging bootstrap fits partly explains PET interval behavior but supplies no validated repair or general coverage guarantee. |
| 3.F.6 | “An exploratory comparison then” | [RESULT][CAVEAT] PET and tree performance depends on the distortion, without establishing a general ranking or comparative precision. |
| 3.F.7 | “For the three generator-model tests” | [RESULT][CAVEAT] PET generator-test failures involve detector-level underfitting and missed-event extrapolation, without establishing a general cause. |
| 3.F.8 | “Separately, the published signal definition” | [RESULT][CAVEAT] Relaxing truth cuts yields a preliminary extended rate containing a small supported increment and substantial simulation-dependent extrapolation. |

**4. Takeaway**

| Location | Identifying phrase | Main idea |
|---|---|---|
| 4.1 | “Unbinned machine-learning unfolding” | [RESULT][CAVEAT] OmniFold extends practical unfolding and reveals descriptive features, while unvalidated uncertainties and simulation dependence restrict measurement claims. |

**Captions and table**

| Location | Main idea |
|---|---|
| Fig. 1 | [METHOD] Migration maps illustrate detector smearing and motivate unfolding rather than bin-by-bin correction. |
| Table 1 | [METHOD][CAVEAT] Closure, coverage, bookkeeping, and stability answer different questions and provide different guarantees. |
| Fig. 2 | [RESULT] Machine-learning unfolding reproduces the published muon cross section. |
| Fig. 3 | [RESULT][CAVEAT] Central-value projections show generator deficits without uncertainty bands, significance claims, or independent GENIE configurations. |
| Fig. 4 | [RESULT][CAVEAT] Joint maps display the Tune v1 excess while distinguishing ratios, integrated differences, overflow effects, and seed sensitivity. |
| Fig. 5 | [RESULT][CAVEAT] Exploratory paired comparisons show PET recovery gains for selected distortions without validating measurement uncertainties. |
| Fig. 6 | [RESULT][CAVEAT] The extended signal retains the published-region result but becomes prior-sensitive where acceptance is low. |

Again, **[NONE]** is unnecessary. The major problem is that identifiable ideas are repeatedly bundled with their entire qualification history.

#### 2. Actual and conventional argument outlines

##### Paper: actual line of argument

1. Multidimensional unfolding is valuable, and OmniFold avoids constructing increasingly large migration tensors.
2. MINERvA open data permit reproduction of an existing measurement and extension to five observables.
3. Several distinct validation checks are necessary.
4. Generator tests offer an application whose calibration can incorporate estimator bias.
5. The introduction previews almost every success, limitation, and inferential qualification.
6. Inputs and multiple estimator configurations are specified.
7. Two-dimensional reproduction succeeds approximately, but learner choice and uncertainty construction complicate interpretation.
8. Higher-dimensional marginal and selected closure checks succeed, while background, regularization, rounding, and coverage tests expose limitations.
9. Central values recover known low-recoil behavior and describe a joint excess relative to Tune v1.
10. Full-chain pseudo-experiments define and calibrate hybrid-null generator tests.
11. Six conditions restrict those tests; all ten reject, including after recovery of interrupted simulations.
12. Neither matched-projection comparisons nor response studies establish added joint discrimination or unconditional physics conclusions.
13. The five-dimensional covariance fails predefined requirements, and no studied measurement definition meets the precision targets.
14. The conclusion presents practical validation lessons and conditional generator testing as the defensible outputs.

##### Typical PRD outline for an unfolding measurement plus generator tests

1. Physics motivation and the specific information missing from existing measurements.
2. Dataset, detector, signal definition, and reporting domain.
3. Observable definitions and simulation predictions.
4. Final unfolding estimator, background treatment, and regularization.
5. Validation of recovery, bias, response robustness, and interval construction.
6. Uncertainty model and covariance, including material omissions.
7. Measurement results with their warranted uncertainties.
8. Generator-comparison hypotheses, statistics, and calibration.
9. Generator-test results, robustness, and physics interpretation.
10. Conclusions distinguishing measurement advances from model constraints.

The paper departs in four consequential ways:

| Departure | Effect |
|---|---|
| A substantial uncertainty-status discussion follows the results and generator tests. | **Hurts.** Readers encounter the five-dimensional findings before receiving the definitive account of what their uncertainty supports. |
| Construction history appears inside the final-method and validation narrative. | **Mostly hurts.** Disclosure is necessary, but replacement histories and repair sequences obscure the estimator actually used. |
| Conditional tests replace the unavailable validated five-dimensional measurement. | **Helps scientifically**, provided this is stated as the organizing purpose early. The paper already contains the evidence for that identity. |
| The introduction, validation summaries, uncertainty section, and conclusion repeatedly inventory the same limitations. | **Hurts.** Repetition makes the argument feel less settled without adding evidence. |

I would move the substance of VII immediately after IV.C and before descriptive results. Retain a short, separate section on **measurement status**, then present central-value observations and calibrated tests as two explicitly different outputs.

The headline should be: **this implementation supports useful central-value studies and conditional calibrated tests, but not the intended validated five-dimensional measurement at the target precision.**

##### Primer: actual line of argument

1. Define the neutrino cross section and detector smearing.
2. Explain migration matrices and event reweighting.
3. Introduce validation terminology.
4. Introduce selection, PET architectures, and expanded truth domains before their purposes are established.
5. Preview six findings, each with substantial qualifications.
6. Reproduce the published result, then recount learner choice and uncertainty repairs.
7. Extend to five quantities and recover known low-recoil behavior.
8. Present a localized Tune v1 discrepancy.
9. Explain a lengthy catalogue of higher-dimensional uncertainty failures and attempted remedies.
10. Present conditional generator rejections and grid sensitivity.
11. Recount PET development, failed designs, diagnostics, and comparative studies.
12. Present the expanded signal definition.
13. Conclude with measurement capabilities and limitations, omitting the joint-test result from the takeaway.

For a non-specialist, the dominant question should be **“What can we learn from this analysis, and how firmly?”** The actual structure repeatedly substitutes **“What happened during its development?”**

#### 3. Proportions

These are approximate **word shares by rhetorical function**, not paragraph counts. A paragraph can contribute to several functions; I allocate its words accordingly.

“Other” includes motivation, definitions without procedural content, and navigation. History means superseded versions, repairs, development chronology, and procedural provenance. Negative findings count as results when reporting evidence; statements restricting conclusions count as caveats. Estimates are uncertain by roughly 5–10 percentage points.

##### Paper

Percentages exclude captions, references, acknowledgments, and data availability.

| Section | Results | Method | Caveats | History | Other |
|---|---:|---:|---:|---:|---:|
| Abstract | 40 | 10 | 50 | 0 | 0 |
| I | 30 | 25 | 25 | 0 | 20 |
| II | 0 | 75 | 20 | 5 | 0 |
| III | 10 | 65 | 10 | 15 | 0 |
| IV, including subsections | 20 | 25 | 40 | 15 | 0 |
| V | 60 | 0 | 40 | 0 | 0 |
| VI, including subsections | 20 | 40 | 30 | 10 | 0 |
| VII | 20 | 10 | 60 | 10 | 0 |
| VIII | 45 | 5 | 50 | 0 | 0 |
| **Overall, approximately** | **25** | **30** | **35** | **8** | **2** |

The imbalance is not simply “too many limitations.” A validation paper should report failures prominently. The problem is that **restrictions and provenance occupy more space than the evidence-to-conclusion progression**.

Specific concerns:

- Section V spends roughly two-fifths of its space restricting interpretation. A common scope statement could absorb repeated “descriptive/no significance” qualifications.
- Section IV mixes final construction, observed validation outcomes, repair history, and requirements for hypothetical future validation.
- Section VI devotes substantial space to production bookkeeping and the status of auxiliary studies. Much belongs in the analysis note.
- Section VII contains a major scientific finding—the measurement precision target was unattainable under the study’s rules—but presents it after an intricate covariance exception narrative.

For a conventional measurement paper, the balance is inappropriate. For a methods-and-validation paper, the **scientific content is appropriate but the allocation and placement need revision**.

##### Primer

Here Section 3 is divided by its unnumbered headings.

| Section | Results | Method | Caveats | History | Other |
|---|---:|---:|---:|---:|---:|
| Abstract | 30 | 15 | 20 | 0 | 35 |
| 1 | 0 | 20 | 5 | 0 | 75 |
| 2, including checks | 0 | 65 | 15 | 5 | 15 |
| 3.O: overview | 30 | 5 | 60 | 5 | 0 |
| 3.A: reproduction | 25 | 15 | 35 | 25 | 0 |
| 3.B: more quantities | 55 | 15 | 30 | 0 | 0 |
| 3.C: tuned-simulation puzzle | 55 | 0 | 45 | 0 | 0 |
| 3.D: limitations | 10 | 20 | 55 | 15 | 0 |
| 3.E: joint tests | 25 | 30 | 35 | 10 | 0 |
| 3.F: PET and expanded signal | 25 | 20 | 35 | 20 | 0 |
| 4 | 55 | 10 | 35 | 0 | 0 |
| **Overall, approximately** | **25** | **25** | **35** | **10** | **5** |

For a primer, the balance is poor. Readers receive many qualifications before acquiring a stable picture of the findings. The PET discussion especially demands specialist attention to bootstrap estimands, acceptance-dependent coverage, development banks, and competing configurations.

A better primer would give more space to **what the observation means**, with one compact explanation of each uncertainty boundary. Technical evidence for those boundaries can remain accessible through the paper and analysis note.

#### 4. Repeated limitations and their best locations

This inventory distinguishes genuinely different limitations. Broad phrases such as “unvalidated uncertainty” recur because several specific problems are repeatedly gathered under that umbrella.

Locations use the paragraph IDs above. “Overview” includes the abstract, introductory findings summary, or conclusion where specified.

| Repeated limitation | Paper locations | Primer locations | Single best full treatment |
|---|---|---|---|
| Five observables share reconstructed information; independence is not demonstrated. | I.2; II.2 | 3.B.2; conceptually 2.A.2 | Observable definitions: paper II.2; primer’s introduction to the five quantities. |
| Same-data reproduction is not an independent compatibility test; cross-covariance is needed. | IV.A.1–2; Fig. 1 | Shape-comparison qualification in 3.O.B1 and 3.A.1 | Paper IV.A.2, with a brief caption pointer. |
| Learner implementation changes the result and is omitted from covariance. | III.3; IV.A.1; IV.B.4; VIII.1; Fig. 1 | 3.O.B1; 3.A.2–3; 3.D.8 | A dedicated estimator-dependence paragraph in validation. |
| Quoted learner was chosen after both comparisons were known. | III.3; IV.A.1 | 3.O.B1; 3.A.2 | One disclosure accompanying the final estimator choice. |
| Flux uncertainty differs from the publication for an unknown reason. | IV.B.1 | 3.A.1 | Two-dimensional uncertainty comparison. No additional warning is needed elsewhere. |
| Missed-event weighting approximation is uncorrected or incompletely tested. | IV.B.2; IV.B.4 | 3.A.3, within broader omissions | Two-dimensional covariance construction and omissions. |
| Run-period block does not identify the correct period or validate its own coverage. | Repeated within IV.B.2 | — | One compact paragraph on the block’s interpretation. |
| Current two-dimensional statistical intervals have no coverage test. | IV.B.3–4; VIII.1 | 3.O.B1; 3.A.4–5 | A current-status paragraph immediately after statistical covariance construction. |
| Earlier statistical intervals undercovered; repair does not independently validate the current intervals. | IV.B.3, with several restatements | 3.A.5 | A brief validation-history note, with details in the analysis note. |
| Total coverage, including simultaneous coverage, is unestablished. | IV.B.3–4; VIII.1 | 3.O.B1–2; 3.O.2; 3.A.4; 3.D.7; 4.1 | One validation-status summary distinguishing marginal, simultaneous, and estimator-specific coverage. |
| Unfolding-model and regularization dependence is absent from the quoted measurement covariance. | I.5; IV.B.4; IV.C.2; VII.2; VIII.1; abstract | 3.A.3; 3.D.5–7; overview and takeaway | Main bias-validation subsection, followed by an explicit covariance-omissions table. |
| Marginal agreement or selected closure does not establish general recovery. | IV.1; IV.C.1–2; VIII.1 | Table 1; 3.O.B2; 3.D.1, 3.D.5–7 | Validation explanation, then report precisely which tests passed. |
| Purity-based background removal biases high-\(W\) cells; quoted uncertainty omits it. | I.5; IV.C.1; VIII.1; abstract broadly | 3.O.B2; 3.D.5–6; 4.1 broadly | Higher-dimensional bias-validation results. |
| Generator-scale shape changes are only partly recovered. | I.5; IV.C.2; V.3; VIII.1; abstract broadly | 3.O.B2; 3.D.5–7; 4.1 broadly | Higher-dimensional recovery tests, adjacent to the background test. |
| Iteration and capacity changes do not establish a remedy. | IV.C.2 | 3.D.6–7 | Same recovery-test subsection; distinguish observed persistence from untested remedies. |
| Rounding-level changes move central values; bootstrap containment is estimator-specific. | IV.C.2; VI.A.3 includes its calibration treatment | 3.D.6; 3.E.3 | Numerical-stability subsection identifying the estimator tested. |
| Five-dimensional statistical coverage test failed on a variant. | IV.C.2 | 3.O.B2; 3.D.7 | Higher-dimensional interval-validation results. |
| Five-dimensional covariance fails predefined requirements and is used under an exception. | VII.1; VII.2 in broader terms; I.5 and VIII.1 summarize failure | 3.O.B2; 3.D.1; 4.1 broadly | Measurement-status section before central-value results. |
| Covariance depends on seed; only one seed pair and limited ensemble sizes were tested. | VII.1; VIII.1; abstract broadly | 3.O.B2; 3.D.2–3 | Measurement-status section, with one compact statement of evidence and limits. |
| Fixed-seed covariance components have unmeasured sensitivity. | VII.1 | 3.D.3 | Immediately after the seed-sensitivity result. |
| Central values also change with seed; effect on localized excess is unmeasured. | IV.A.1 for 2D; IV.C.2 for numerical effects more broadly | 3.O.B3; 3.C.1; 3.D.3; Fig. 4 | Central-value stability discussion; avoid repeating the same number in prose and caption. |
| Higher-dimensional plots are descriptive and carry no significance. | V.3–4; VII.1; VIII.1; Fig. 3 | 3.O.B2–3; 3.C.1; 3.D.1; Figs. 3–4; 4.1 | One scope statement opening central-value results, plus short caption labels. |
| Dedicated low-recoil comparison uses a different truth definition. | V.2 | 3.B.3 | At that comparison only. |
| Chosen pion-FSI tests do not rule out other FSI explanations. | V.1 | 3.B.3 | At the mechanism comparison only. |
| High-energy, high-mass concentration is reference-dependent and influenced by wide cells. | V.3–4; Fig. 2 | 3.C.1; Fig. 4 | Joint-map interpretation, explicitly separating absolute excess from relative excess. |
| GiBUU lacks high-energy neutrinos. | II.3; V.4; VI.A.1; VI.B.1 | 3.C.1; 3.E.B5 | Generator-input definition; state its distinct consequence at each affected analysis. |
| Five-dimensional comparisons do not demonstrate added discrimination beyond matched projections. | Abstract; I.5; VI.C.3; VIII.2 | 3.E.4; overview less explicitly | Generator-test interpretation, with one short abstract/conclusion reminder. |
| Tests are conditional and provide no new measurement uncertainty. | Abstract; I.5; VI.B.1; VII.2; VIII.1–2 | 3.O.B4; 3.E.2–3 | Test scope immediately after the hypotheses; summarize once at the end. |
| Fine-grid convergence is unshown and unresolved structure is unbounded. | Abstract; I.5; VI.B.1; VI.C.1; VIII.2 | 3.O.B4; 3.E.B1; 3.E.5 | Dedicated fine-grid condition paragraph. |
| Directional sensitivity scans do not bound the true sub-grid error. | VI.B.1; VI.C.1 | 3.E.5 | Report the scan once, immediately after explaining the unresolved-grid condition. |
| Calorimetric recoil-response uncertainty is absent. | Abstract; I.5; VI.B.1; VI.D.1–2; VIII.2 | 3.D.4 broadly; 3.E.B2 | Dedicated detector-response subsection, referenced from the condition list. |
| A fixed-null energy-scale check does not replace nuisance calibration. | VI.D.1–2 | No equivalent study presented | VI.D.2, directly after its result. |
| Global rejection does not identify a mechanism or kinematic cause. | V.3–4; VI.C.3 | 3.B.3; tension with 3.C.1’s final claim | Generator-test interpretation, with local mechanism qualifications only where needed. |
| Production decisions or auxiliary comparisons were informed by observed data. | VI.A.4; VI.C.1–3 | 3.E.4–5 | A concise design-provenance paragraph or table; distinguish each study’s status. |
| Interrupted simulations initially left potentially consequential missing outcomes. | VI.C.2; VIII.2 reports resolution | 3.E.1 | A resolved computational-validation note; do not repeatedly frame it as a current limitation. |
| PET contributes no cross section, uncertainty, or selected validated design. | — | 3.O.B5; 3.F.2–4, 3.F.7 | Opening and concluding sentences of a separate PET development box or companion guide. |
| Better PET point recovery does not establish interval validity. | — | 3.F.3–5; Fig. 5 | PET findings summary distinguishing recovery from coverage. |
| PET coverage is acceptance-dependent and available repairs are unvalidated. | — | 3.F.4–5 | PET interval-results paragraph. |
| PET/tree comparison does not establish a general ranking or comparative precision. | — | 3.F.6; Fig. 5; 3.F.7 limits causal generalization | Comparative-study paragraph, with short caption qualification. |
| PET conclusions apply only to studied distortions and finite sample sizes. | — | 3.F.5–7; Fig. 5 | One scope paragraph for the PET study. |
| Relaxing truth cuts adds no selected observations and introduces prior-dominated rate. | II.3 establishes fixed selection, without this extension | Abstract; 2.A.2; 3.O.B6; 3.F.8; Fig. 6; 4.1 | Separate expanded-domain section, beginning with selection versus truth-domain distinction. |

A single best full treatment does **not** mean banning all abstract, conclusion, or caption reminders. The useful pattern is:

> State the limitation fully once; attach a short qualification to the claim it limits; refer back for evidence.

The present pattern often restates the evidence, history, and warning together.

#### 5. Paper abstract

##### Sentence-by-sentence classification

“Headline” below includes the scope-setting first sentence; strictly, that sentence states the purpose rather than a result.

| No. | Sentence, identified by its opening | Label | Editorial disposition |
|---|---|---|---|
| 1 | “We test the practical limits …” | Headline: scope | Keep, shortened. It establishes the correct identity. |
| 2 | “The analysis reproduces … extends it to five …” | Headline result | Keep. This is the central methodological achievement. |
| 3 | “The higher-dimensional central values pass …” | Headline result | Compress to selected validation successes; preserve the distinction between marginal checks and closure. |
| 4 | “Pseudo-experiments … show limitations …” | Qualification | Merge with sentence 5; the catalogue is too granular for the abstract. |
| 5 | “The measured model dependence prevents …” | Qualification containing a major negative result | Keep prominently. It defines what the work does not establish as a measurement. |
| 6 | “Generator tests, calibrated … reject all five …” | Headline result | Keep the full-chain calibration, number of predictions, total/shape distinction, and familywise level. Shorten the model list. |
| 7 | “These rejections hold only under stated conditions.” | Qualification | Delete as a standalone sentence. It adds no specific information. |
| 8 | “The tests recover known discrepancies …” | Qualification containing a result | Keep the absence of demonstrated added joint discrimination, compressed. |
| 9 | “Their physical interpretation is limited because …” | Qualification | Keep the two material conditions, compressed. They directly affect the headline rejection claim. |

A 120–160-word abstract should retain five things:

1. Dataset and method.
2. Reproduction and extension to five central-value observables.
3. Selected validation success alongside the failed measurement-uncertainty objective.
4. Conditional full-chain generator rejections.
5. The principal inference limits: response, grid convergence, and unshown added discrimination.

It should omit the exhaustive validation taxonomy, full generator-version inventory, and a generic “conditions apply” sentence.

For example, this is approximately 150 words:

> We study multidimensional unbinned unfolding with OmniFold using MINERvA medium-energy inclusive muon-neutrino charged-current open data. The analysis reproduces the published muon-kinematic cross section and produces simultaneous central values for five observables. Marginal-normalization checks and selected closure tests succeed, but background-subtraction bias, regularization bias, and uncertainty-validation limitations remain. Measured model dependence prevents a five-dimensional measurement meeting our predefined uncertainty and precision criteria. Separately, generator tests calibrated with pseudo-experiments that rerun the full analysis chain reject all five tested predictions in total and shape at the 5% familywise level under the stated nuisance model. These tests incorporate the estimator’s bias toward its prior, but their physical interpretation remains limited by the absence of a calorimetric recoil-response uncertainty and unestablished convergence of the fine hypothesis grid. The comparisons recover known generator discrepancies without demonstrating additional discrimination from joint five-observable information beyond matched coarse projections.

The abstract grows because each honest claim prompts another question: *Which estimator? Which closure? Which uncertainty? Under which null? Was that check independent?* Authors then try to make the abstract carry the entire audit trail.

The remedy is to **narrow each claim until it needs fewer qualifications**, rather than append every qualification to a broad claim. Organize the abstract around the two outputs—central-value validation and conditional hypothesis testing—and retain only conditions that materially change their interpretation.

#### 6. Does the primer’s order serve a non-specialist?

Only partly. Sections 1 and the first three paragraphs of Section 2 work well: question, obstacle, conventional solution, alternative method, scaling advantage.

The structure deteriorates at “What the checks tell us.” A useful distinction among validation tests expands into selection logic, two PET architectures, and signal-domain extension. Readers have not yet encountered the findings those distinctions explain.

Three later ordering choices are particularly costly:

- **The overview duplicates the detailed findings.** Its six substantial bullets create an initial pass through nearly every qualification, followed by another pass through the same material.
- **Limitations arrive as a long retrospective block.** Readers must reinterpret the preceding “new puzzle” after learning how incompletely shape changes are recovered.
- **PET dominates the final substantive section.** Its development history displaces the paper’s principal inferential result, which then disappears from the takeaway.

The concluding claim in 3.C—“points theorists toward what their models are missing”—also exceeds the structural support supplied before it. The paragraph has just established reference dependence, absent significance, and unmeasured sensitivity of the excess’s localization. A descriptive observation should end with its warranted interpretation.

##### Proposed order and paragraph headings

For a primer specifically accompanying this paper:

1. **The question: what can neutrino data tell us?**
   - What a cross section measures.
   - Why muon and hadronic quantities are useful together.

2. **Why the detector blurs the answer**
   - Resolution, efficiency, and missing events.
   - Why unfolding requires simulation.

3. **How OmniFold works**
   - Learn which simulated events need more or less weight.
   - Transfer those weights from reconstructed events to truth.
   - Why adding observables becomes practical.
   - What “unbinned” does—and does not—remove.

4. **First finding: the published muon result is closely reproduced**
   - Agreement in total rate and measurement cells.
   - Remaining correlated shape differences and learner dependence.
   - Similar uncertainty sizes do not establish correct coverage.

5. **Second finding: five coordinates reveal useful correlations**
   - Introduce \(E_{\rm avail}\), \(q_3\), and \(W\).
   - Explain their shared reconstructed information.
   - State the successful marginal and selected closure checks.

6. **How firmly should we trust the five-coordinate picture?**
   - A compact version of the closure/coverage/stability table.
   - Background subtraction and incomplete recovery of changed truth.
   - Why the five-dimensional uncertainty did not meet the requirements.
   - What descriptive central-value plots can still show.

7. **What those central values show**
   - The established low-recoil deficit reappears.
   - Adding 2p2h fills part of the gap without settling its cause.
   - The joint excess relative to Tune v1.
   - Why ratios, integrated differences, overflow cells, and reference choice matter.

8. **A separate question: can the specified simulations explain the data?**
   - Why hypothesis testing differs from reporting a measurement uncertainty.
   - How full-chain pseudo-experiments calibrate the tests.
   - All five predictions are rejected in total and shape under the stated model.
   - Matched projections do not establish extra discrimination from all five coordinates.

9. **The two conditions that most limit the physics interpretation**
   - Missing calorimetric recoil-response uncertainty.
   - Unresolved structure below the hypothesis grid.
   - Other conditions summarized briefly, with a reference for details.

10. **What has been learned**
    - A successful reproduction and practical higher-dimensional central values.
    - A demonstrated boundary on the intended measurement.
    - Conditional generator rejections.
    - The detector and validation inputs needed for stronger conclusions.

Move PET and the expanded signal definition into **separate optional companion pieces**. If they must remain in this primer, append two clearly separated sections after the core account:

11. **Optional development study: learning from individual detector deposits**
    - What PET changes.
    - Improved recovery, but no design with validated intervals.
    - Why no PET measurement is reported.

12. **Optional development study: estimating interactions outside the published truth cuts**
    - Same selected observations, larger population being estimated.
    - Detector-supported increment versus simulation-dependent extrapolation.
    - Why the preliminary extended rate is not a model-independent measurement.

That order gives readers a stable progression: **question → method → demonstrated reproduction → higher-dimensional capability → validation boundary → observations → conditional inference**. It also lets the primer be honest without requiring the reader to reconstruct the analysis’s development history.

---

## P7. Claude triage of the outside referees' physics and statistics points (sha256 `6ef84f5b8c925eb1…`)

### Physics/statistics triage of the two r1 referee reports

Scope: every major comment of `gemini-referee.md` (G-M1..M5) and `sol-referee.md` (S-1..S-10), and every
physics or statistics minor comment (G-m*, S-m*). Wording-only items are skipped (listed at the end).

Tree measured: W = `scratchpad/wt-plain2`, HEAD `5cb1b038` (branch `stageF/plain-language-pass2-20261018`),
one commit past `34650231`. `git diff --stat 34650231 HEAD` touches only `docs/orchestration/*`, so every
`docs/analysis-note/*` and code line cited below is identical at `34650231`. Paths are relative to W.
Short forms: P = `docs/analysis-note/paper_body.tex`, MP = `docs/analysis-note/main_paper.tex`,
N/ = `docs/analysis-note/`, CVU = `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h`,
A7 = `docs/orchestration/state/s5p/contract-amendment-7-production-admission.json`.

Another session edited W's working tree while this triage ran; the files were modified at 22:24. The changed files are
N/sec_5d.tex, N/sec_joint.tex, N/result_status_rows.tex, N/app_release.tex and the two .bib files (`git status` afterwards).
Every line number here refers to committed HEAD `5cb1b038`; the sec_joint.tex citations were checked with `git show HEAD:`.
The uncommitted edits shift sec_joint.tex by +7 lines after line 26 and sec_5d.tex after line 216.
None of the sec_5d.tex lines cited here is affected. One of these uncommitted edits, sec_joint.tex after line 26,
adds the fine-grid definition (14x16x7x7x6) that GPT m5 asks for.

One new calculation was made for this triage (S-4): `scratchpad/triage-calc/seqsize.py` (read-only, no repo writes).

#### Table

| report | id | one-line summary | verdict | evidence (file:line) | what would close it | severity |
|---|---|---|---|---|---|---|
| Gemini | M1 | No calorimetric hadronic-response band in the test nuisance model; GENIE CV rejection rides on hadronic axes; state the condition in abstract, intro, conclusions | Request: ADDRESSED IN PAPER. Underlying gap: VALID, OPEN (already conceded) | Abstract MP:76-78; intro P:82-85; Sec. VI D P:873-904 (no band 878; null not regenerated 900; untested effects 901-902; "remain conditional" 903-904); conclusions P:999-1003; N/sec_joint.tex:158-161 | Physically: a response band (species and energy dependent, incl. neutrons) drawn through the calibration, i.e. new nulls (large new computation). For the paper: nothing more; the condition is already in all three places. "Driven entirely by the hadronic axes" overstates P:886-888 ("involves the hadronic axes") | high (limits physical interpretation of every rejection; disclosed) |
| Gemini | M2 | Explain physically why OmniFold misses the GiBUU/GENIE shape (74% at high W) | ADDRESSED IN NOTE; paper should carry one sentence | N/sec_5d.tex:88-102 (noise-free pseudo-data recover >99% of the reco-level departure while truth residuals stay up to 74%; 30 iterations cut the Eavail residual 26% while q3 grows; larger classifier does not help; "No single cause is established"); N/sec_validation.tex:175-192 (deformation lies in weakly constrained directions; marginal vs joint metric; iterations) | Text: one sentence in P:506-516 saying the departure lies mostly in directions the reconstructed inputs barely constrain (>99% of its reco signal is reproduced). See also S-1: reco W is an exact function of reco (pT, p∥, q3) | medium |
| Gemini | M3 | ML seed variance is "not negligible vs Poisson statistics"; give seed-count guidance / try seed bagging | Partly WRONG (2D), VALID OPEN (5D guidance) | 2D: seed block median 0.06% vs stat 0.684% P:326-329, P:389-392; chi2 seed range 2.64-2.75 is small, the learner swap (exact vs LightGBM) is the large term P:247-255. 5D: rounding-level changes move cells by a few stat SD P:516-520; seed effect flat over 40/80/160 throws P:925-935 | 5D guidance needs a seed-pair ensemble and a bagged-weights test (new computation). For the paper: say the 2D training-seed term is negligible and the 2D learner term is not | low |
| Gemini | M4 | Central values without covariance must be labelled as such, also in any release | ADDRESSED IN PAPER (largely) | "descriptive. No significance" P:576-580, P:602-603; Fig. 3 caption "uncertainties not shown" P:623-625; conclusions P:966-969; 5D covariance status P:915-943 | Text: add "central values only; no uncertainties" to the Fig. 2 caption (P:587-592), which lacks it; carry the same flag in the deposited release | low |
| Gemini | M5 | Explain where the 135 MeV constant came from | ADDRESSED IN NOTE/RECORDS; paper should carry half a sentence | docs/EAVAIL_DEFINITION.md:89-126 (it is the pi0 mass, CVU line 364; inherited from the MINERvA-101 tutorial code; upstream GENIEXSecExtract now uses 139.57; materiality vs full covariance not done, :117-119); N/sec_3d.tex:86 | Text: "inherited from the MINERvA-101 tutorial implementation (the pi0 mass)". Gemini's suggested wording "inherited from AnaTuple conventions" and "negligible compared with the leading systematics" are both wrong per these records | low |
| Gemini | m2 | Define Q^2 used in W | VALID, OPEN | P:118-119 uses Q^2 undefined. Implemented truth Q^2 is the massless-lepton form 4 E_nu E_mu sin^2(theta_mu/2) (CVU:385-393), used by truth W (CVU:396-410) | Text. Gemini's proposed formula (2E_nu(E_mu - p∥) - m_mu^2) is NOT what truth W uses; quote the implemented one | low |
| Gemini | m4 | Fig. 2 denominator; physical origin of the overflow-cell share | Denominator: ADDRESSED IN PAPER. Origin: VALID, OPEN | Caption "relative to the MINERvA Tune v1" P:587-588; Tune v1 = GENIE 2.12.6 + reweights P:110-114; overflow share P:573 | Text (one clause). Do not assign a mechanism without a test (P:859-861 says regional attribution needs separate tests) | low |
| Gemini | m5 | Ledoit-Wolf target | VALID, OPEN (answer exists in code) | nd-unfolding/s5p_joint.py:83-99: correlation shrunk toward the identity (Schaefer-Strimmer target D, LW intensity), rescaled by sample SDs. Not stated in N/sec_joint.tex:44-47 or P:655-658 | Text (metric affects power only, P:657-658) | low |
| Gemini | m6 | Define the L2 norm in condition (i) | ADDRESSED IN NOTE/RECORDS (partly) | N/values_inference.tex:35-37 (ratio of L2 norms of per-cell relative changes, over the 109 cells); P:758-760 comment; N/sec_joint.tex:118-121 | Text: one formula in P:721-723 | low |
| GPT | 1 | (pT, p∥, q3) determine E_nu and hence W: five coordinates are not five DOF | VALID, OPEN. Exact at reco level, near-exact at truth level; partly disclosed for reco only | Reco: CVU:208-240 (q3_reco and W_reco both from the same p_mu, theta_mu, q0); N/scalar_kinematics.tex:1-19; P:133-137. Truth: q3 = sqrt(Q^2 + (E_nu - E_mu)^2) from generator E_nu (3d-unfolding/genie/gen_to_xsec5d.py:27-28, 114-118); W from E_nu, E_mu, theta_mu, struck-nucleon M (CVU:396-410); truth pT, p∥ from the same theta_mu (CVU:71-79) | Text: state the relation for both levels (see section A). Cheap check: on any truth dump, residual of W_true vs F(pT, p∥, q3) (expected tens of MeV, from the M_n/M_p choice, the massless-lepton Q^2 and the beam-axis vs true-neutrino direction). Revisit "fifth observable W separates..." P:568-569 and "five simultaneous observables" framing | medium (framing of the dimensionality claim; no number is wrong) |
| GPT | 2 | Missing recoil-response uncertainty; +-4% scale check with old nulls is not robustness | ADDRESSED IN PAPER (as a condition); gap VALID, OPEN | P:879-881 (response moves both statistic and null); P:900-904 (nulls not regenerated; not species/energy/resolution; "remain conditional"); MP:76-78; P:999-1003 | As G-M1. The paper does not present the scale study as resolving the omission | high (same item as G-M1) |
| GPT | 3a | Hybrid null is not the generator prediction; one-direction kappa scan bounds nothing | ADDRESSED IN PAPER | P:635-640 (hybrid null defined), P:717 ("The decisions test the hybrid null"), P:724-740 (residual unmeasured; carry-over only if...; scan "bounds neither the residual nor the convergence"), P:777-779 | Nothing beyond consistency: the abstract (MP:66-70) names "five tested predictions", not hybrid nulls; one word ("hybrid", or "discretized") would align it | medium |
| GPT | 3b | Reweighting Tune v1 keeps Tune v1's distribution of unreported hadronic properties (neutron fraction, composition), hence its response | VALID, OPEN | Hybrid null is Tune v1 events reweighted on the fine grid (P:636-640); conditions (i) and (ii) (P:719-743) cover within-cell shapes in the five observables and the detector model, not the conditional composition; the note never states it (grep for neutron fraction / composition in N/sec_joint.tex: none) | Text: add to condition (i)/(ii) that the null inherits Tune v1's hadron composition at fixed observables. A test needs a hidden-composition reweighting or a second-generator response (new computation) | medium |
| GPT | 4 | (k+1)/(B+1) with data-dependent B and repeated 95% CP looks is not shown valid; FWER claim unproven | Partly VALID (the sentence), WRONG in substance (the decisions are conservative under any stopping) | Claim: P:703-704 "remain valid at the number of pseudo-experiments reached", P:750-753; N/sec_joint.tex:103-105; A7:23. Rule: stop on a 99.5% look interval plus precision (nd-unfolding/s5p_inference.py:89-114); decide on the 95% CP gate (s5p_inference.py:127-155; P:689-691). Paper P:691-694 conflates the stop interval with the decision interval | Text plus a short appendix argument, computed here (section B): with the CP gate, the null probability of a rejection at threshold t is <= 0.51t (t=0.005) to 0.89t (t=0.05) for ANY stopping rule up to B=1999, so Holm FWER <= 0.89 alpha. Replace the "p values remain valid" sentence by this decision-level statement; the bare (k+1)/(B+1) under worst-case stopping can reach ~1.2-1.6 t | medium |
| GPT | 5a | Is "calibrated" size averaged over nuisance draws or uniform over nuisance values? Universe probabilities, correlations, clipping, surrogate validation | VALID, OPEN (text); surrogate validation UNCLEAR | Draws: P:668-673; N/sec_joint.tex:58-71; A7:22 (one of 100 flux universes; every band at one of its universes; clipping <=0.35%, P:744 and N/sec_joint.tex:163-165). Nothing in note or paper states the error claim is an average over the nuisance prior | Text: say the size is prior-predictive (averaged over the stated nuisance distribution), not uniform over a composite null. Surrogate validation: not found in N/sec_joint.tex or app_statmethods_nd.tex | medium |
| GPT | 5b | Do the 34 model bands vary the null truth or only response/efficiency? | ADDRESSED IN RECORDS, not in note or paper | A7:22 "coherently for the background source and the signal response with fine-cell truth preservation"; docs/orchestration/REVIEW-20260927-s5p-round2-repairs-and-admission-draft.md:55 | Text: one clause in P:668-670 and N/sec_joint.tex:63-64 ("rescaled so that the fine-cell truth stays G") | medium |
| GPT | 6a | Run-period step: need groups, exposures, formula, stat treatment, rank | ADDRESSED IN NOTE; paper could carry one sentence | N/sec_systematics.tex:289-319 (1A-1F, 1G-1M, 1N-1P; exposure-weighted mean of three; rank <=2, ~1.8 dof, size uncertain ~100%; median 2.14%, max 5.69%; 1A-1F reference alternative) ; paper P:351-377 | Text (group names and "exposure-weighted mean"). The cause of the ~7% step is unknown (P:359-360): VALID, OPEN, not closable from released inputs | medium (2D uncertainty only; no coverage is claimed, P:456) |
| GPT | 6b | Five seeds give a poorly determined training variance | ADDRESSED IN PAPER | P:327-329 ("variance itself uncertain by about 70%"; 0.06% median) | none | low |
| GPT | 6c | Distinguish pointwise from simultaneous coverage | ADDRESSED IN NOTE and PAPER | N/sec_validation.tex:31-33; P:442-444 ("nor simultaneously over all reported bins") | none (the paper names both) | low |
| GPT | 7 | Validate the final estimators: correlation-changing deformation at fixed marginals, a detector-response deformation; "new inputs needed" too categorical | Partly ADDRESSED IN NOTE; VALID, OPEN for response deformation | Correlation deformation exists: hidden q3 at fixed (Eavail, W) truth, up to 37% (N/sec_validation.tex:167-168; N/sec_5d.tex:75-77). Response mismatch: protocol implemented, not run (N/app_response_mismatch.tex:1-48; N/sec_validation.tex:170-171). 2D coverage status P:396-419 | Run the record-only response-mismatch closure already implemented (cheap) on the joint-test estimator; scope P:452-456 to "validated total intervals over the full domain" (it already is) | medium |
| GPT | 8 | Central-value figures keep the biased purity subtraction; tests use negweight; show the shift, say why, label every figure | Shift: ADDRESSED IN PAPER. Reason: ADDRESSED IN NOTE. Labelling: VALID, OPEN | Shift on data <=1.4% (median 0.36%) P:501-502, N/sec_5d.tex:60-63; bias 3.5-4.1% = 0.36-1.07 sigma N/sec_5d.tex:39-47, P:494-498. Reason: N/app_negweight.tex:274-282 (footing consistency with the adopted covariance; switching invalidates the J28 covariance; "explicit obligation to revisit the footing before submission", not discharged); higher-capacity refinement failed a data stability test (N/app_negweight.tex:409 comment). Estimator named in text P:196-199, P:569-570, not in Fig. 2/3 captions (P:587-592, P:623-626) | Text: name the background treatment in both captions; one sentence with the reason. Optional: a central-value figure from the joint-test estimator (exists as a deterministic variant) | medium (descriptive results only) |
| GPT | 9a | NuWro and GiBUU on C, data on CH; quantify hydrogen | VALID, OPEN | P:150-154; N/sec_3d.tex:213-233 (GENIE on CH; NuWro, GiBUU on C; all "per nucleon"); 3d-unfolding/genie/README.md:32 (CH = C12 + H1, /13), :125 ("Target C12 (~92% of CH by nucleons; documented approximation)"); docs/research/MINERVA-MODEL-IMPROVEMENT-MEMO-20261011.md:45, :177 (says a species-weighted prediction is needed; not computed) | Section C. Cheap proxy: GENIE CH vs C12-only in the 109 test cells (both splines exist, 3d-unfolding/genie/gen5d_flux_reweight.py:173-191). Proper: NuWro on H, combined 12:1 | medium (few-% rate and Delta/DIS-shape effect on 2 of 5 nulls) |
| GPT | 9b | GiBUU missing E_nu>20 GeV also populates p∥<6 GeV | VALID, OPEN (disclosed, not quantified for the test domain) | Condition (v) P:747-748; domain cut P:645-646; shares quantified only overall (6.8-7.4%) and for the corner (14.3-14.8%) N/sec_eavailw.tex:113-123 | Cheap: GENIE/NuWro share of E_nu>20 GeV inside the 72-cell domain | low (GiBUU's deficit, integrated ratio 1.39, N/sec_eavailw.tex:112, is far larger) |
| GPT | 9c | 2p2h "fills 52%" and FSI statements are model dependent | ADDRESSED IN PAPER | P:545-550 ("applies to the chosen pion variations"); P:859-861 | none | low |
| GPT | 9d | Low-recoil comparison needs matched definitions | ADDRESSED IN PAPER (as a caveat); computation VALID, OPEN | P:556-560 ("not quantitative"); docs/EAVAIL_DEFINITION.md sec. 2-4 (aggregate over common cells "measured nowhere", P:565 comment) | Cheap: the definition migration in the two common (Eavail, q3) cells | low |
| GPT | 10a | One table of estimators and one of validation results | ADDRESSED IN NOTE | N/sec_method.tex:149-168 (three configurations); N/sec_validation.tex:16-33, 110-172 (validation tables); N/result_status_rows.tex | Text: port compact versions | low |
| GPT | 10b | Compare with conventional iterative unfolding | Partly ADDRESSED IN PAPER (2D), VALID, OPEN (higher D) | The 2D reproduction is against the published result from the same data (P:240-266); no D'Agostini comparison above 2D anywhere in N/sec_*.tex | New computation (IBU on the 3^5 or (Eavail, W) grid) | low |
| GPT | 10c | A deposited, consistent release is required | VALID, OPEN | MP:91-93 ("not yet deposited"), MP:105-106 (carries the exact-split curve) | Deposit a package with the LightGBM 2D curve | low for claims, required before publication |
| GPT | m1 | chi2/ndf 2.65 is not a compatibility significance | ADDRESSED IN PAPER | P:246-247 ("indicative only"), P:263-266 (needs cross-covariance) | none | low |
| GPT | m2 | Signal cuts, fiducial volume, flux range, target count, background fractions | ADDRESSED IN NOTE | N/sec_experiment.tex:37-58 (theta_mu < 20 deg, fiducial z range and apothem, 3.2353e30 nucleons); paper defers to Ref. P:107-109 | Text: two lines in Sec. II | low |
| GPT | m3 | Keep 135 MeV as a stated convention | ADDRESSED IN PAPER | P:122-132 | none (see G-M5 for origin) | low |
| GPT | m4 | Is W a stationary-nucleon estimator or the hadronic-system mass? | ADDRESSED IN PAPER (formula) and NOTE (explicitly) | P:118-119 (formula from E_nu, E_mu, Q^2, struck-nucleon M); N/sec_eavailw.tex:21-25; N/sec_pet.tex:302-305 ("assuming a single struck nucleon at rest"; differs from W_had by Fermi motion and extra baryons) | Text: add "(a struck nucleon at rest)" in P:118-119 | low |
| GPT | m5 | Define supported cells; give fine-grid edges | ADDRESSED IN NOTE | N/app_statmethods_nd.tex:73-75 (expected reco signal and selected truth weight >=1000 at data exposure); fine edges N/sec_3d.tex:435-437 (q3), N/sec_eavailw.tex:30-31 (W) | Text: one clause in P:644 | low |
| GPT | m6 | Where is the shape Jacobian evaluated; prediction-sample correlations | VALID, OPEN (answer in code) | nd-unfolding/s5p_inference.py:31-46 (J at the unfolded f of each experiment/data); nd-unfolding/s5p_joint.py:146-162 (diag Var(mu_G): cells taken independent) | Text (affects power only) | low |
| GPT | m7 | Put observed statistics and null summaries in Table I | VALID, OPEN | Table P:802-828 has only k, B; one observed value quoted P:838-839; Fig. 4 P:789-799 | Text from joint-evaluate.json (RECORD-20261005 sec. 2) | low |
| GPT | m8 | Binomial uncertainties on power | VALID, OPEN | P:862-866; CP intervals already computed by nd-unfolding/s5p_inference.py power_determined | Text | low |
| GPT | m9 | Metric behind "6.145%" and its excess precision | VALID, OPEN | N/values.tex:407 ("the correlation-sensitive leg"); s_proj is a maximum over projection functionals (N/release-package-20260922/README.md:45-46); P:926-928 | Text: name the functional; print 6.1% | low |

Skipped as wording or editorial: Gemini m1 (title), m3 (Fig. 1 axis labels; the caption already says "cells drawn at equal size", P:281), m7 (repository references), m8 (HOLD tags); GPT m10 ("claim variant" label), m11 (references and HOLD tags).

#### Referee statements that misread the paper or sources

- Gemini header "Bailey & Nachman": correct. MP:41 and MP:44 list Joseph Bailey and Benjamin Nachman; the PDF text (`in-r1/paper.txt:3`) shows the same.
- Gemini Part 4: "reproduces published MINERvA 2D cross sections within ~1%". Only the integral agrees to ~1% (ratio 1.011, N/values.tex:48). 95.6% of bins agree within 10% (P:60-62, P:243-244), and chi2/ndf is 2.65.
- Gemini Summary: "explicitly demonstrate that the joint 5D test provides no statistically significant discrimination beyond... projections". The paper says it finds "no evidence of additional discrimination" (P:853-855, P:85-87). That is not evidence of absence. GPT reads this correctly (its Part 2, VI C).
- Gemini Quote-6 rewrite: "no simulated pseudo-experiment approaches the observed test statistic". This is false: the closest recovered one is 4.6 below 868.6 (P:838-839). The rewrite also says "up to a maximum of 2000"; the cap is 1999 (N/values_inference.tex:19).
- Gemini Quote-4 rewrite: says the refined bootstrap "resolved" undercoverage and gives intervals that "conservatively envelope" the fluctuations. The paper says the rescoring is post hoc and partly circular, the rebuilt band is untested, and the quoted block is a different ensemble that has never had a coverage test (P:396-419).
- Gemini Quote-2 rewrite: attributes 135 MeV to "AnaTuple conventions" and calls it "negligible compared to the leading systematics". The records trace it to MINERvA-101 tutorial code and say the comparison with the full covariance has not been done (docs/EAVAIL_DEFINITION.md:104-126).
- Gemini m2: the Q^2 it proposes is not the implemented truth Q^2 (CVU:385-393).
- Gemini M3: its premise that training stochasticity is non-negligible holds in 5D but not in 2D (G-M3 row).
- GPT 4 says repeated CP checks invalidate the FWER claim. The decision gate makes the claim conservative under any stopping (section B). The defect is in the paper's sentence, not in the decisions.
- GPT 9a ("NuWro and GiBUU are described as carbon predictions") and GPT 10c (superseded 2D curve in the package) are accurate readings.

#### A. GPT 1: exact kinematic redundancy among (pT, p∥, q3, W) (medium; special-care item)

Implemented definitions:
- Reco (CVU:208-240). Both variables use the same q0 = `<tree>_recoil_E` (full calorimetric recoil, not reco Eavail), E_nu = E_mu + q0, and Q^2 = 2E_nu(E_mu - p_mu cos theta) - m_mu^2. Then q3 = sqrt(Q^2 + q0^2) and W = sqrt(M^2 + 2M q0 - Q^2), with M the average nucleon mass. Reco pT and p∥ use the same p_mu and theta_mu (CVU:61-69). At fixed (pT, p∥), q3_reco increases monotonically with q0, so reco W is an exact function of reco (pT, p∥, q3), apart from the Q^2 >= 0 and W^2 >= 0 clamps. The reco inputs carry four independent quantities: p_mu, theta_mu, q0 and the tracker-plus-ECAL Eavail. N/scalar_kinematics.tex:16-19 and P:133-137 say only that the inputs "share information".
- Truth. q3 = sqrt(Q^2_exact + (E_nu - E_mu)^2), with the generator's E_nu (3d-unfolding/genie/gen_to_xsec5d.py:27-28, 114-118). W is the stationary-nucleon "experimenter's" W from E_nu, E_mu and theta_mu, with M = M_n or M_p for the struck nucleon and Q^2 = 4E_nu E_mu sin^2(theta/2) (CVU:385-410). It is not the hadronic-system mass (N/sec_pet.tex:302-305). With the neutrino along the axis of pT and p∥: q3^2 = pT^2 + (E_nu - p∥)^2, and E_nu - p∥ > 0 always, so E_nu = p∥ + sqrt(q3^2 - pT^2) has a single branch. That fixes W up to three small terms: the M_n/M_p difference (~1.3 MeV), the massless-lepton Q^2 (shifts W^2 by ~m_mu^2(E_nu cos theta/p_mu - 1), at most a few tens of MeV in W), and the difference between the beam axis and the true neutrino direction (mrad level).

Consequences:
- The truth distribution lies on a 4D manifold in the 5 coordinates, smeared at the tens-of-MeV level. Bin edges in W are 0.3-0.8 GeV apart, so W adds coordinates but not truth degrees of freedom.
- Many of the 243 cells of the 3^5 grid are kinematically empty, which probably explains much of the 109-cell support (N/app_statmethods_nd.tex:73-75). This is a conjecture; the check is cheap.
- The tests remain valid as tests of distributions on the grid.
- "The fifth observable, W, separates the remaining discrepancy..." (P:568-569) is a change of coordinates of (pT, p∥, q3), not new information.
- The four-to-five-dimensional marginal agreement and any gain from adding W bear on classifier capacity, not on new physics information. GPT says the same.

To close (text only): state the truth and reco relations in Sec. II (two sentences). Quantify the truth residual W - F(pT, p∥, q3) on one simulation dump (cheap). Reword "five simultaneous observables" to make clear that W is a derived coordinate. Nothing quoted numerically changes.

#### B. GPT 4: Monte Carlo p values under the sequential rule (medium; special-care item)

What the paper claims:
- P:703-704: "the Monte Carlo p values remain valid at the number of pseudo-experiments reached".
- P:750-753: they are "exact for the simulated null to the extent that the pseudo-experiment chain reproduces the analysis".
- The contract asserts the same without an argument (A7:23 "the p-value stays valid at the B reached"; DECISION-20261004-s5p-production-budget-extension.md:23, :69-70 change only the budget meter).

The rule actually frozen:
- Stopping uses batches of 200 to at most 1999. A null stops when a 99.5% CP "look" interval straddles no threshold and meets a precision tier (nd-unfolding/s5p_inference.py:89-114). The comment there calls 99.5% "Bonferroni over at most ten looks".
- Rejection needs the 95% CP interval of k/B, at the stopping B, to lie entirely below the Holm threshold (s5p_inference.py:127-155).
- P:691-694 describes stopping as the 95% interval lying on one side of the threshold. That conflates the two intervals and needs a one-clause fix.

Is GPT right?
- About the bare formula, yes: (k+1)/(B+1) at a data-dependent B is not guaranteed super-uniform. Worst-case stopping (an adversary watching every b up to 1999) gives P(p <= t) up to 1.55t at t = 0.005 and 1.17-1.61t at t = 0.05 (seqsize.py, "plain" columns).
- About the claimed error control, no. A rejection at threshold t requires CP95_upper(k_B, B) < t. Bound P(exists b <= 1999 with CP95_upper(k_b, b) < t), integrated over u ~ U(0,1), where u is the true null tail probability. This union bound over every b holds for any stopping rule, including the data-informed budget extension (the cap stayed 1999). The bound is 0.514t at t = 0.005, 0.553t at 0.00556, 0.691t at 0.01, 0.825t at 0.025 and 0.890t at 0.05.
- In the Holm step-down, the first true-null rejection needs CP_upper < alpha/m0. So FWER <= m0 * s(alpha/m0) <= 0.89 alpha, whatever the dependence among the ten tests and whichever variant has the maximum claim p.
- The bound assumes exchangeability of the observed statistic with the null draws (continuous T). That is the "chain reproduces the analysis" condition the paper already states.

To close (text only, with this short calculation as an appendix or note paragraph): replace "the Monte Carlo p values remain valid at the number reached" with a statement that the determinacy gate keeps each decision's size below its threshold for any stopping up to 1999, so Holm FWER <= 0.89 alpha. Fix the 95% vs 99.5% conflation in P:691-694. The reported p values can stay as descriptive numbers. Gandy's method is unnecessary. No decision changes; nine tests have k = 0 at B >= 1343, and k = 0 needs B >= 737 at t = 0.005.

#### C. GPT 9a: carbon vs hydrocarbon in NuWro and GiBUU (medium; special-care item)

The data and the GENIE predictions are per CH nucleon: CH = C12 + H1 divided by 13 (3d-unfolding/genie/README.md:32; N/sec_3d.tex:213-214). NuWro and GiBUU are generated on C12 only and normalized per C nucleon (N/sec_3d.tex:225-229, 232-233; README.md:125 calls this "a documented approximation"). The one record that discusses it explains why a single constant correction fails: free protons give no nu-QE and no 2p2h but add resonance and DIS events without FSI. It does not compute the effect (docs/research/MINERVA-MODEL-IMPROVEMENT-MEMO-20261011.md:45, :177).

Expected size, by counting: per-nucleon CH/C = (6 sigma_n + 7 sigma_p)/(6.5(sigma_n + sigma_p)). That is a few percent overall, with channel-dependent sign: QE is about 12/13 of C, and inelastic is closer to C. The H events also put structure at W > 1.08 GeV with no nuclear smearing. Neither the paper nor the note quantifies this.

This is small next to the NuWro and GiBUU rate deficits and the rejection margins: lambda 318-6344 (P:682-684), and GiBUU's integrated ratio is 1.39. It is not small next to the 1.4% normalization nuisance. So the decisions are very probably unaffected, but the statement is uncontrolled.

To close: a cheap GENIE proxy (CH vs C12-only splines and samples in the 109 cells; gen5d_flux_reweight.py:173-191 already supports both targets). Better: NuWro run on H and combined 12:1. Then one sentence in P:150-154 with the number.

#### D. Calorimetric response (Gemini M1, GPT 2) (high; special-care item)

The paper already states the condition in all three places the referees ask for:
- abstract MP:76-78 ("the nuisance model has no calorimetric recoil-response uncertainty");
- introduction P:82-85;
- conclusions P:999-1003 ("depends on the simulation's calorimetric recoil response... would require a response band drawn through the calibration");
- Sec. VI D P:873-904, which ends "remain conditional on the simulation's hadronic response".

Sec. VI D also states what GPT wants said:
- the +-4% study keeps the original nulls (P:900);
- it is a single uniform scale;
- species, energy dependence, resolution and response-before-calibration were not tested (P:901-902).

The referees' request is therefore met in the text. The physics gap is real and remains the main limit on interpreting any rejection, as P:884-888 explains. In the matched (pT, p∥) projection, GENIE CV is not rejected (p = 0.48 total, 0.63 shape; N/values_inference.tex:52-53). So its rejection involves the axes a response band would act on.

The closures that would bear on it are not run: the response-mismatch closure is implemented but not run (N/app_response_mismatch.tex:46-48), and no response band exists in the systematic set (A7 condition 2, RECORD-20261005 sec. 3 item 2).

Closing it needs new computation: a response nuisance family, including neutrons, propagated through both the data extraction and the null pseudo-experiments.

For the paper: optionally, the abstract's "These rejections hold only under stated conditions" (MP:70) could be replaced by the two named conditions, as GPT suggests. The physics content is already present.

#### E. GPT 8: background treatment for central values vs joint tests (medium; special-care item)

- Central values for 2D-5D use LightGBM with purity subtraction (P:196-199, P:569-570). The joint tests use negweight with 400/31 refinement (P:208-214).
- The size of the inconsistency is in the paper: purity bias up to 4% in simulation at highest W, about 1 sigma in one (Eavail, W) cell (P:494-498; 0.36-1.07 sigma per N/sec_5d.tex:39-47). The two treatments differ on data by at most 1.4% (median 0.36%; P:501-502; N/sec_5d.tex:60-62).
- The reason is in the note only (N/app_negweight.tex:274-282): mixing footings inside one covariance is worse than either consistent choice, and switching would have meant rerunning everything and invalidating the J28 covariance adopted just before. The note records "an explicit obligation to revisit the footing before submission", and says nothing there discharges it. That obligation is relevant to whether the paper is ready.
- The Fig. 2 and Fig. 3 captions do not name the background treatment.

Severity is medium because the figures are descriptive only. To close: name the background treatment in both captions; add the reason in one sentence; either discharge or explicitly carry the note's "revisit the footing" obligation. Optionally show the joint-test-estimator (Eavail, W) map, or its ratio to Fig. 2, as GPT asks.

---

## P8. Claude: theme-A number sources (sha256 `0316ba328e0b22e2…`)

### Theme A: sources for the numbers the hedges stand in for

Read-only research at `main` `34650231` (worktree `wt-plain2`). Joseph's rule (DECISION-20261018-joseph-plain-language-pass2
§1, theme A): add a number "if it is expected to be there by the readers and it would make sense to them". It must
come from a committed record, and it must not need more than a clause of definition. No value below was computed for
this report. Where I did arithmetic, it was only to check a recorded value, and I say so.

Paths are relative to the worktree root. `paper_body.tex`, `primer_body.tex`, `sec_*.tex`, `app_*.tex` and `values*.tex`
are in `docs/analysis-note/`.

---

#### Paper F4: the model-dependence bound, "target total width", "predefined criteria", "useful precision"

**Where the hedge is:**
- abstract, `main_paper.tex:63-65` ("The measured model dependence prevents a five-dimensional measurement with total
  uncertainties that meet our predefined criteria at useful precision");
- Intro, `paper_body.tex:73-78`;
- Sec. VII, `paper_body.tex:945-949` ("None of the definitions it considered could meet the precision targets set in
  advance … For its fallback definition, the bounded model-dependence component alone exceeded the target total
  width");
- Conclusions, `paper_body.tex:987-990`.

**(1) Values.** The study assessed three reporting definitions: RD1, the 109 supported joint cells (J); RD2, 27 coarser
joint cells (H2); RD3, the 39 supported (E_avail, W) cells (EW).
- Bounded unfolding-model component (largest shift over five generator-sized truth departures): median **12.0%, 9.6%
  and 13.4%**; 90th percentile 38.6%, 22.5% and 39.2%. GiBUU is the dominant vertex in most cells.
- **T1, the total-width target:** median total 68% half-width **≤ 10%**. It is unattainable in RD1 and RD3 from the
  model component alone. RD2 fails once the flat 1.4% normalization is added: its median is ≥ 11.0%.
- **T2:** model-component median ≤ 5%, and recovery ≥ 75% of a generator-sized departure. T2 fails in every
  definition.
- **RD3 is the fallback** under the frozen selection procedure, and it fails T1.
- Summary phrase in the record: "prior dependence is ≈ 10–13% per coarse joint cell, comparable to the generator
  differences a user needs to resolve (3.7–16%, Stage 1)".

Printed form in the note: `\SI{12.0}{\percent}, \SI{9.6}{\percent} and \SI{13.4}{\percent}`; "median 68\% half-width
at most \SI{10}{\percent}"; "about 10--13\% per coarse joint cell".

**(2) Source.**
- Note: `sec_5d.tex:206-226` (§`sec:gbdt-model-dependence`, paragraph "Reporting definitions for a five-dimensional
  measurement"; the values are at :211-216, the 10–13% at :221). Its source comment (:224) is
  `docs/orchestration/RECORD-20260927-s5p-stage2-exit.md` §4 (VL155).
- Record checked: `RECORD-20260927-s5p-stage2-exit.md:122-147`. The table is at :127-131 (RD3 13.4% at :131), T1 at
  :133, T2 at :136-138, fallback at :139, "≈ 10–13% per coarse joint cell" at :144. The record states every value
  above. Its receipt is `state/s5p/stage2/stage2_receipt.json`.
- No values macro exists. The note prints literals.

**(3) Already printed?**
- Note: yes, `sec_5d.tex:211-221`. The values recur as prior-sensitivity envelopes at `sec_5d.tex:313-314`.
- Paper and primer: no. `grep` finds no 13.4, no 10–13%, and no "half-width" in either.

**(4) Does a reader expect it?** **Yes.** The paper's negative headline result has no number at all. A PRD reader who
reads "exceeded the target total width" asks at once "by how much, against what target?". Two numbers answer it: 13.4%
against a 10% median half-width. "68% half-width" is standard and needs no definition. "Fallback definition" needs one
clause, "the 39 (E_avail, W) cells". For the abstract and Conclusions, the record's own summary, "about 10–13% per
cell", is the interpretable form. It also explains *why* in one phrase: it is comparable to the generator differences
to be resolved.

Caution: RD2's median model component is 9.6%, below 10%. So "the model dependence alone exceeds the target" is true
of RD1 and RD3 only. RD2 fails only with the normalization added. The abstract wording must not say "exceeds 10% in
every definition".

**(5) Proposed text.**
- Sec. VII, replacing `paper_body.tex:948-949`:
  > For its fallback definition, the 39 supported $(\Eavail,W)$ cells, the bounded model-dependence component alone
  > has a median of 13.4\%, above the target of a 10\% median half-width for the total 68\% interval.
  >
  > % Source: note sec_5d.tex:206-221; RECORD-20260927-s5p-stage2-exit.md §4 (VL155).
- Abstract and Conclusions (the abstract carries a ~150-word budget, so this is about a 10-word net addition):
  > The measured model dependence, about 10--13\% per cell, prevents a five-dimensional measurement whose total
  > uncertainties meet the 10\% precision target we set in advance.

  Here "10–13%" is the record's ":144 ≈ 10–13%". If the budget will not take it, put the number in Sec. VII and the
  Intro only, and leave the abstract's sentence as it is.

**Side finding (note, possible base defect, not theme A).** `sec_5d.tex:216-217` reads "recovery of at least 75% of a
generator-sized departure, against 0.31–0.63 measured". The record (:138) reads "recovery ≥ 75% … (0.25 against the
measured 0.31–0.63)". So 0.31–0.63 is the residual proxy M (target ≤ 0.25), not a recovered fraction. The note's
juxtaposition reads as "31–63% recovered". The Fig. `gbdt-recovery` caption (`sec_5d.tex:238-239`) itself warns that
one minus the proxy is not an exact recovered fraction. For the director.

---

#### Paper F5: the integrated 2D agreement in the abstract

**(1) Value.** Ratio of integrated cross sections, ours over published: **1.011**, from the integral ratio 1.0112. The
two totals are 3.073e-38 and 3.039e-38 cm²/nucleon. 95.6% of the 205 bins (196/205) agree within 10%.

**(2) Source.**
- Macros: `\ratioTot` (`values.tex:48`), `\sigTwoD` (:46), `\sigTwoDpaper` (:47), `\binsTen` (:85).
- Receipt: `docs/orchestration/receipts/2d-lgbm42-20261011/RECEIPT-2d-agreement-windows-lgbm42-20261011.json`. Checked:
  `headline_totals_oi130.values.ratio_integrals_reported` = 1.0111916861814374;
  `results.within_10_percent` = 196 / 95.6.

**(3) Already printed?** Yes, everywhere except the abstracts:
- paper Intro `paper_body.tex:60-61` ("to about one percent (ratio $\ratioTot$)");
- paper Sec. IV A `paper_body.tex:241-243`;
- primer `primer_body.tex:179`;
- note `sec_results.tex:59` (`\SI{1.1}{\percent}` with `$\ratioTot$`) and :91;
- note `sec_execsummary.tex:26`.

Not in `main_paper.tex`'s abstract.

**(4) Does a reader expect it?** **Yes, weakly.** "Reproduces the published double-differential cross section" is the
abstract's one positive result, and a reader expects a figure of merit there. "About 1% in the integrated cross section"
needs no definition. But the abstract budget (§2 of the decision) is tight, and the number is an integral: alone it may
suggest bin-level agreement, while the body reports a correlated shape difference (χ²/ndf `\chiPaper`, `paper_body.tex:246`).
So this is optional. It is worth five or six words only if the budget allows.

**(5) Proposed text** (`main_paper.tex:53-55`):
> The analysis reproduces the published double-differential cross section in muon kinematics, with an integrated
> cross section within about 1\% of the published value, and extends it …

Use the Intro's wording ("about one percent"), not a new literal. The value derives from `\ratioTot`. The note prints
"1.1%" (`sec_results.tex:59`), which is the same receipt rounded.

---

#### Paper F7: what the "fine five-dimensional grid" is

**Where the hedge is:** `paper_body.tex:637` ("equals $G$ on a fine five-dimensional grid"), :719-724, :735, :1001-1003,
and the abstract `main_paper.tex:78`.

**(1) Value.** The fine grid is the analysis's dense five-axis binning:
- 14 p_T × 16 p∥ bins (the published 2D binning);
- E_avail edges [0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100] GeV (7 bins);
- q₃ edges [0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100] GeV (7 bins);
- W edges [0, 1.1, 1.4, 1.8, 2.2, 3.0, 100] GeV (6 bins).

That is a 14×16×7×7×6 grid. The 109 test cells (J) are integrals of it.

**(2) Source.**
- The edges are printed in the note at `sec_method.tex:270-275` (§`sec:method-binning`). The dense grid is printed as
  "$14\times16\times7\times7\times6$ grid in C order" at `app_release.tex:65`. The note says fine-grid outputs are
  integrated into the 109 J cells at `sec_5d.tex:158`.
- The **identification** of the joint test's "fine grid" with this grid is *not* stated in any note sentence or decision
  record I found. It rests on:
  - code, `nd-unfolding/s5p_stage1_inspect.py:38-44` (`FINE`, the same edges as `sec_method.tex:270-275`);
  - the s5p evaluator, which checks every prediction's fine edges against one reference
    (`nd-unfolding/s5p_recompute.py:618-635`);
  - the release-audit note `docs/publication/audit-20261008/notes/mapping-notes-C.md:25`. It records the RC4
    fine-to-J map as `U (109,65856)`, and 65,856 = 14·16·7·7·6.

  The contract (`state/s5p/contract-amendment-7-production-admission.json`, `claims.family`) says "the fine 5D grid"
  but gives no binning.
- No values macro exists.

**(3) Already printed?**
- Note: the edges and the dense grid are printed (as above), but not the statement that it is the joint test's fine
  grid. `sec_joint.tex:15-60` gives only the coarse 3⁵ grid.
- Paper: the coarse edges only (`paper_body.tex:641-644`).
- Primer: no.

**(4) Does a reader expect it?** **Yes.** "Fine grid" carries a condition the paper stresses three times: convergence
below it is unshown. A reader cannot judge "fine" without its size. The coarse grid's edges are printed a line later,
so the contrast is natural, and one clause defines it. The "twofold-merged grid" (:722) stays undefined, and I found no
record of its edges. That needs a separate pointer to the note.

Because the identification rests on code and an audit note rather than a record sentence, I recommend adding a note
sentence to `sec_joint.tex` §`sec:joint5d-design` first (theme B: content in the note before the paper relies on it).

**(5) Proposed text.**
- Note, `sec_joint.tex` after :22:
  > The fine grid is the analysis binning of \S\ref{sec:method-binning}, $14\times16\times7\times7\times6$ bins in
  > $(\pT,\pPar,\Eavail,q_{3},W)$; the test cells are its integrals.
  >
  > % Source: nd-unfolding/s5p_stage1_inspect.py:38-44; RC4 fine-to-J map (109, 65856), audit-20261008 mapping-notes-C.md:25.
- Paper, `paper_body.tex:637`:
  > … equals $G$ on a fine five-dimensional grid (the analysis binning: the published $14\times16$ muon-momentum bins
  > times 7 $\Eavail$, 7 $q_{3}$ and 6 $W$ bins), …

---

#### Paper F6: the halving rate behind κ = 2

**Where the hedge is:** `paper_body.tex:726-728` ("at a rate taken from the review of the test design, for which no
calculation is recorded, the residual would be about one to three times the last step").

**(1) Value.** The step in a proxy of the test metric (the "W-norm") shrinks by **0.45–0.76 per halving**.

**(2) Source.**
- Macros: `\jtMoneWnormMin` = 0.45 and `\jtMoneWnormMax` = 0.76 (`values_inference.tex:38-39`). The comment says: "A7
  claims.rejection … Origin: REVIEW-20260927-s5p-admission-confirmation.md item 4, computed with a PROXY metric … how the
  ratio was formed is not recorded."
- Record checked: `docs/orchestration/state/s5p/contract-amendment-7-production-admission.json`, `claims.rejection`:
  "the W-norm step between resolutions shrinks by 0.45-0.76 per halving, so the residual below the fine grid is ~1-3
  times the last step; kappa = 2 is its central value". The contract states the value.
- Provenance status: `docs/publication/corrections-20261008/RECORD-20261008-release-audit-corrections.md:241` (G6b):
  "Unresolved: provenance. No recorded operand reproduces it." Joseph's option at :346-347 is "accept it as disclosed".
- The paper's source comment `paper_body.tex:755, 761-762` gives the same value and status.

**(3) Already printed?** Note: yes, `sec_joint.tex:123-125` ("shrink by \jtMoneWnormMin--\jtMoneWnormMax{} per
halving, a design-review value whose calculation is not recorded"). Paper and primer: no.

**(4) Does a reader expect it?** **Yes.** The sentence names "a rate" and then gives its consequence ("one to three
times"), so the reader expects the rate. With it, the reader can check the consequence: a geometric series with ratio
r leaves r/(1−r) of the last step, which is 0.8–3.2 for 0.45–0.76. I checked this; the number is not added. One clause
suffices, "in a proxy of the test metric", and it must keep the disclosure that no calculation is recorded.

A clarity risk: the printed L2 ratio, 0.50–0.86 (`\jtMoneMin`–`\jtMoneMax`, :723), is a different quantity, the last
step as a fraction of the whole change, in a different norm. The sentence must keep the two apart.

**(5) Proposed text** (replacing `paper_body.tex:726-728`):
> If the step kept shrinking geometrically by \jtMoneWnormMin--\jtMoneWnormMax{} per halving in a proxy of the test
> metric, a design-review value whose calculation is not recorded, the residual would be about one to three times the
> last step.

This is the note's wording. It replaces "a rate taken from the review of the test design, for which no calculation is
recorded", so the net length is about the same.

---

#### Paper F12: which estimator the 74% belongs to

**Where the hedge is:** `paper_body.tex:506-516`. The sentence gives "by up to 74% at high W, with or without
background" with no estimator, then "for other fixed generator shapes, measured with the joint-test estimator, it is
16% to 31%".

**(1) Value.** The 74% (EW29, +74.1%) belongs to the s5c **F2** estimator: the deterministic LightGBM OmniFold variant
(five iterations), measured in the s5n family N, that is, with the `negweight-refined` background treatment. It is
reproduced signal-only, so it is a property of F2, not of the background treatment. Median residual: 9.7%.

**(2) Source.**
- Paper source comment `paper_body.tex:535`: "The 74% is the F2/N estimator (VL151)".
- Record checked: `docs/orchestration/OUTCOME-20260925-s5n-stage1-development-fail.md`. Line :25 defines family N as
  "the s5c F2 deterministic LightGBM OmniFold (5 iterations) with the driver's negweight-refined measured side". The
  results are at :57 (C4, "EW29 +74.1%") and :75-82 ("The F2 estimator does not follow …", median 9.7%, up to 74%,
  signal-only reproduces it).
- F2 is named "deterministic LightGBM OmniFold" in `OUTCOME-20260925-s5c-tier-s-futility-fail.md:3-4`.
- The audit claim table, `docs/publication/audit-20261008/CLAIM-TABLE-20261008.tsv` row V19, confirms that the 16–31%
  is "measured with candidate R (refinement 400/31), not the F2/N estimator of the 74%".
- The paper's own name for this family is "a deterministic variant of the five-dimensional LightGBM central-value
  estimator" (`paper_body.tex:499-500`, sourced to the same s5n record).

**(3) Already printed?** The 74% is printed at `paper_body.tex:509`, `sec_5d.tex:74, 94` and `sec_execsummary.tex:114`.
The attribution is printed only loosely in the note: `sec_5d.tex:75-77` calls it "a property of the estimator (five
iterations, the GBDT configuration of §method)". The median 9.7% is at `sec_5d.tex:73`. The paper does not name the
estimator.

**(4) Does a reader expect it?** **Yes.** The next clause names the joint-test estimator for 16–31%, so the reader
infers by contrast that the 74% is from something else, and cannot tell what. The fix is a phrase the paper already
uses three paragraphs earlier, and it needs no new definition. Adding the median 9.7% would also replace the vague
"several percent in the largest cells" with a recorded number. It is optional.

**(5) Proposed text** (`paper_body.tex:507-510`):
> When the true shape is reweighted by the GiBUU-to-GENIE ratio, the $(\Eavail,W)$ cells unfolded with the
> deterministic variant of the central-value estimator deviate from it by several percent in the largest cells and by
> up to \SI{74}{\percent} at high $W$, with or without background, …

---

#### Paper F17: is the quoted 2D statistical block built without the completeness division?

**Where the hedge is:** `paper_body.tex:389-419`. The paper says the earlier band's main cause, "a division by the
completeness that the bootstrap replicas carried and the central value does not, was removed in a rebuilt band", and
that "the quoted statistical block is a different ensemble from it". It does not say whether the quoted block carries
the defect.

**(1) What the records establish.** The quoted block is S1: 300 replicas at seed 42, three Poisson streams. Its
replicas compute the completeness from the **un-resampled** MC truth weights, as the central value does. So a
replica's c is the central value's c, which is 1 to rounding on this (Phase-17) input. Precisely put, the replicas
still divide by c, but by the central value's c, not a resampled one. "Built without the completeness division"
(F17's proposed wording) is therefore loose. "Uses the central value's completeness" is exact.

**(2) Sources.**
- Recipe:
  - `docs/orchestration/state/2d-closeout/stageB/REPORT.md:304`, row C02 ("`mc_signal_reco` rows, with completeness
    from unresampled truth (KI 84)");
  - :341, R5 ("Completeness stays unresampled (KI 84)").
  - Joseph adopted R5 (three-stream) in `docs/publication/DECISION-20261012-joseph-2d-closeout-recipe.md:18`. That row
    does not itself mention completeness.
- Production: `stageC/production/DESIGN.md:93`, §3.4 (S1 = `driver_p1.py --seed 42 --bootstrap-seed N
  --bootstrap-streams three`), and §2/§4 (driver pinned at `3056e625…`, the production driver plus the pilot patch).
- Code, at that digest (checked): `stageC/pilot/p1/driver_p1.py:2050-2052, 2097-2103, 2357-2372`. The MC bootstrap
  saves `w_truth_cv`, and completeness uses it when `hasTruthOnlyMisses` is set.
- The fix: `KNOWN_ISSUES.md:74` (row 84, code `bb4b0b6f`, an ancestor of `34650231`).
- **Not established by any measurement I found.** No committed record measures the completeness of the S1 replicas.
  The "rebuilt replicas max |c−1| = 1.6e-14" in KI 84 is for the VL170 rebuild, not S1. The S1 frozen check
  (`DESIGN.md` §7, :238; `REPORT.md:38`) is provenance plus reproduction of the pilot replicas, not a completeness
  read. The claim is established by design and code, not by a check on the S1 products.

**(3) Already printed?** No, nowhere.
- Note `sec_systematics.tex:97-129` (§`sec:uq-boot`) describes S1's streams and seed but not its completeness.
- `sec_validation.tex:266-275` says the term "was removed … and the band rebuilt" and "The quoted statistical block is
  now a different ensemble".

**(4) Does a reader expect it?** **Yes, as a clause.** The paragraph tells the reader that the old band had a defect,
that a rebuild removed it, and that the quoted block is neither. The obvious question is whether the quoted block has
the defect, and the paper leaves it open. This is a factual claim, not a number, so it is the director's call (F17 says
so). If added, the note should say it first in `sec:uq-boot`, citing Stage B R5 and DESIGN §3.4. The wording should
not claim a measured check.

**(5) Proposed text.**
- Paper, after :419:
  > Its replicas, like those of the rebuilt band, use the central value's completeness.
- Note, `sec_systematics.tex` after :101:
  > Each replica takes the completeness from the un-resampled simulation, as the central value does, so it does not
  > carry the resampled completeness behind the earlier band's undercoverage (\S\ref{sec:coverage}).
  >
  > % Stage B REPORT §3 C02, §4 R5; stageC/production/DESIGN.md §3.4; driver_p1.py 3056e625 :2050-2052, :2357-2372; KNOWN_ISSUES 84.

---

#### Paper Sec. IV C: the five-dimensional coverage-test failure ("failed its criterion", no numbers)

**Where the hedge is:** `paper_body.tex:520-524`.

**(1) Values** (Tier-S test of candidate F2: bias-corrected statistical intervals on 153 reported functionals, 400
pseudo-experiments per truth). The criterion is futility: a functional is futile when the upper confidence bound on its
coverage is < 0.66 at 68% or < 0.94 at 95%, at a per-comparison level of 0.05/459.

| truth | functionals futile at 68% | functionals futile at 95% | minimum coverage, 68% / 95% | median coverage, 68% / 95% |
|---|---|---|---|---|
| nominal | 0 | 2 (EW36, J161) | 0.570 / 0.850 | 0.710 / 0.960 |
| E_avail tilt (a = 0.2) | 51 | 42 | 0.060 / 0.288 | 0.665 / 0.950 |

The highest-W cells cover 0.07–0.13 at 68% under the tilt. The third truth (q₃) is a construction defect and does not
enter the verdict.

**(2) Source.** `docs/orchestration/OUTCOME-20260925-s5c-tier-s-futility-fail.md:3-6` (scope), :30-36 (table,
criterion, level) and :41-48 (nominal-only and tilt-only counts; highest-W 0.07–0.13). The receipt is
`state/s5c/tier_s/interim_400.json` (`aa574c17…`), VL150. The paper's comment `paper_body.tex:533` cites it. No values
macro exists.

**(3) Already printed?** No numbers anywhere.
- Note `sec_5d.tex:342-351` (§`sec:coverage-5d`) prints only "1,200 pseudo-experiments over three truths".
- `sec_execsummary.tex:105` gives no numbers.
- Paper and primer: no numbers.

**(4) Does a reader expect it?** **Yes, for the paper. For the primer, no.** A PRD reader told that a pre-registered
coverage test "failed" wants the size of the failure. One clause carries it: the number of failing quantities and the
worst coverage. Decided theme-C item F1 states the failure as miscoverage at the tested truths, and these numbers are
what make that statement concrete. Two cautions:
- "Functional" needs a gloss ("reported cell and projection integrals").
- Under the "every detail has a note home" rule, the numbers belong in the note first: `sec:coverage-5d` has none.

The minimum alone (0.06) without its denominator would overstate the failure, so print the count with it.

**(5) Proposed text.**
- Note, `sec_5d.tex:348`, after "futility criterion":
  > (an upper confidence bound on the coverage below 0.66 for 68\% or 0.94 for 95\% intervals): under the tilt 51 of the
  > 153 reported quantities fail at 68\% and 42 at 95\%, with coverage as low as 0.06 for nominal 68\% intervals; at
  > nominal truth two fail at 95\%, the lowest at 0.85.
  >
  > % OUTCOME-20260925-s5c-tier-s-futility-fail.md §1-§2; interim_400.json aa574c17.
- Paper, `paper_body.tex:522-524`:
  > … failed its criterion, fixed in advance: under the $\Eavail$ tilt, 51 of 153 reported cell and projection integrals
  > have 68\% coverage confidently below nominal (as low as 0.06), and at nominal truth two fail at 95\%.

---

#### Primer F7: false precision (`\sprojMeasured`, `\cvMoveOverSigmaMax`, `\fpsSigma`)

**What the macros are.**
- `\sprojMeasured` = **6.145** (`values.tex:407`): the seed-induced movement of the projected (E_avail, W) uncertainty,
  the correlation-sensitive leg s_proj, which is a maximum over an offset set at one seed pair. Record checked:
  `docs/orchestration/state/GRADE-20260920-cause3-two-member.json`, `"s_proj": 0.06145388143592225`. The bound
  `\sprojBound` = 5 is at :408.
- `\cvMoveOverSigmaMax` = **6.02** (`values.tex:458`): the maximum, over 43 functionals, of the seed-induced
  central-value movement divided by its quoted σ. Record checked: `docs/orchestration/state/CENTRAL-VALUE-VS-SIGMA-20260920.json`,
  `movement_over_uncertainty.max` = 0.06021989576891877 (median 0.0106; `grades_nothing: true`).
- `\fpsSigma` = **4.502e-38** cm²/nucleon (`values.tex:273`, no receipt in the comment). This is the preliminary
  extended-fiducial central value from the 2026-06-10 FPS battery (purity footing). The ledger at
  `VALIDATION_LEDGER.md:1615` states "4.502e-38". The ledger's three-prior values at :1625 are 4.502 / 4.475 /
  4.367e-38, a spread of about 3%. That spread is why four figures is false precision; I did not compute any new value
  from it.

**Where the primer prints them.**
- `\sprojMeasured`: `primer_body.tex:397` ("about \SI{\sprojMeasured}{\percent}", which prints "about 6.145 %"; "about"
  with four significant figures contradicts itself).
- `\cvMoveOverSigmaMax`: :352, :377 (Fig. caption) and :418.
- `\fpsSigma`: :651.

**What the paper and note print for the same quantities.**
- s_proj: the paper prints **6.145%** (`paper_body.tex:927, 930`). The note prints 6.145 (`sec_5d.tex:478, 495`).
- CV movement over σ: not in the paper. The note prints **6.02** (`sec_5d.tex:520`).
- σ_ext: not in the paper. The note prints **4.502e-38** (`sec_fps.tex:112`; `sec_summary.tex:54`;
  `app_history.tex:289`; `app_negweight.tex:285, 292`).

So the primer matches the macros and the other deliverables. The precision problem is shared. In the paper it is milder,
because a PRD reader reads 6.145% against a 5% limit as a grading operand.

**(4) Does a reader expect it?** This is not a missing number. It is a precision question. For a non-specialist,
**rounded values are right**: "about 6%", "at most about 6% of their own uncertainty", "about 4.5 × 10⁻³⁸ cm² per
nucleon". All three quantities are one-seed-pair, maximum-over-set or preliminary values. The digits beyond the second
carry no information for this reader.

A caution: rounding makes 6.145% (the uncertainty moves) and 6.02% (central values move, relative to σ) both read
"about 6%". The primer's words already distinguish the two objects; keep them.

**(5) Proposed text.** Keep the macro as the single source and round at print time. The preamble loads `siunitx`
(`preamble.tex:23`), so `\SI[round-mode=figures,round-precision=1]{\sprojMeasured}{\percent}` (and the same for
`\cvMoveOverSigmaMax`) and `\num[round-mode=figures,round-precision=2]{\fpsSigma}` print "6 %", "6 %" and
"4.5e-38" without a new literal. Wording:
- :397 "shifts by about 6\,\%";
- :352/:377/:418 "by at most about 6\,\% of their own uncertainty";
- :651 "$\sigma_{\mathrm{ext}}\approx 4.5\times10^{-38}$ cm$^2$/nucleon".

Before relying on it, confirm that the rounding options work with the siunitx version in the build. That is a build
check, not run here.

---

#### Primer F-new-1: the size of the changed-truth bias

**Where the hedge is:** findings item 2, `primer_body.tex:133-136` ("the unfolding follows a changed simulated truth
only partly"); the takeaway, :681-683 ("end-to-end tests on simulation show biases"). The body already says "typical
cells come back about 10% off, and the highest-W cells much more" (:440-443).

**(1) Values.** Under the GiBUU/GENIE E_avail-shape departure, the median (E_avail, W) residual is **9.7%**, and the
maximum is **74%** (EW29, +74.1%, the highest-W column).

**(2) Source.**
- `OUTCOME-20260925-s5n-stage1-development-fail.md:57, 75-77`.
- Note `sec_5d.tex:73-74` ("median \SI{9.7}{\percent}, up to \SI{74}{\percent} in the highest-$W$ column"; comment
  :78-79 cites the same record).
- The primer's "about 10%" (:442) has no source comment. It is the record's 9.7% rounded.

**(3) Already printed?**
- Primer: "about 10%" at :442 (body only), with "much more" for high W. The primer does not print 74%.
- Paper: 74% (`paper_body.tex:509`). Note: 9.7% and 74% (`sec_5d.tex:73-74`; `sec_execsummary.tex:114`).

**(4) Does a reader expect it?** **Yes, in item 2.** "Follows only partly" is the hedge a non-specialist cannot size.
"About 10% in typical cells" is immediately interpretable. Duplicating a body number in the summary is normal for a
summary list. The record supports "up to about 74% in the highest-W cells", but a non-specialist does not need it in
the summary, so I do not propose it there. In the body (:443) it could replace "much more", but "much more" is honest,
and the bare 74% invites over-reading. Optional.

**(5) Proposed text.**
- Item 2 (:134-135):
  > … the unfolding follows a changed simulated truth only partly (in a test of generator size, typical cells come back
  > about 10\% off) …
- Takeaway: leave as is. It points to item 2.

Add the source comment `% 9.7 % median: sec_5d.tex:73; OUTCOME-20260925-s5n-stage1-development-fail.md:76`.

---

#### Primer F-new-2: a number for the corner excess over Tune v1

**Where the hedge is:** `primer_body.tex:332-358` ("The leftover discrepancy sits in a specific corner"). That
paragraph gives numbers for the other simulations (14–16% in the corner, 7–15% overall; GiBUU 61% and 39%) but none
for Tune v1.

**(1) Values.** Two kinds are recorded.
- **Ratio, data over Tune v1:** **12–30%** above in the cells with E_avail ≥ 0.8 GeV and W ≥ 1.8 GeV. But it is also
  **23–31%** above at W < 1.1 GeV for every E_avail. In ratio, then, the corner is *not* larger than the low-W row.
- **Cell-integrated positive difference:** **67%** of it lies at E_avail ≥ 0.8 GeV, and **83%** of that at
  W ≥ 1.8 GeV. **22%** sits in the single deep-DIS catch cell (E_avail > 3 GeV, W > 3 GeV).

**(2) Source.**
- Ratios: macros `\figTwoHiHiLo`/`\figTwoHiHiHi` = 12/30 and `\figTwoLowWLo`/`\figTwoLowWHi` = 23/31
  (`values.tex:497-500`). The comment at :476-482 gives the released-figure-array values 12.35–30.46% and
  22.64–30.58% (fig_numbers.py, release audit ea939701 G11, `fig_arrays.npz` `72394a2b…`).
- Shares: note `sec_eavailw.tex:49-53`. The paper's comment `paper_body.tex:581-582` routes the shares to it and the
  22% to the released figure arrays.

**(3) Already printed?**
- Paper: both kinds (`paper_body.tex:571-576`).
- Note: the shares (`sec_eavailw.tex:49-53`). The ratio ranges are in the paper only, from the macros.
- Primer: neither.

**(4) Does a reader expect it?** **Yes, but the right number is the share, not the ratio.** The primer's claim is that
the leftover discrepancy *sits* in the corner, which is a statement about where the excess cross section is (the
right-hand, cell-integrated panel). Giving the ratio alone (12–30%) would, honestly, need the low-W 23–31% beside it,
because in ratio the excess is as large at low W. That would undercut the paragraph's framing unless explained, which
takes more than a clause. The share needs one clause ("of the extra cross section, summed over cells") and matches the
claim. The Fig. caption (:369-373) already teaches the reader that integrated and ratio views differ.

**(5) Proposed text** (after :336, "… where the neutrino shatters the nucleon."):
> About two thirds of the extra cross section, summed over cells, lies at high available energy, most of it at high
> $W$; about a fifth sits in the single widest corner cell.
>
> % shares 67 %, 83 %, 22 %: note sec_eavailw.tex:49-53; paper_body.tex:571-574.

If a ratio is wanted as well, add "and cell by cell the data there are 12 to 30 percent above the tuned simulation,
about as much as at the lowest $W$". This uses `\figTwoHiHiLo`–`\figTwoHiHiHi`, and the low-W comparison is
mandatory, as in `paper_body.tex:574-576`.

---

#### Primer F-new-8: the red curve in primer Fig. 2

**Where the hedge is:** primer Fig. 2 caption, `primer_body.tex:261-267`. The caption does not identify any curve.

**(1) Value.** The red curve is **MINERvA Tune v1 on GENIE 2.12.6**, the analysis reference simulation and unfolding
prior. Legend text: "GENIE 2.12.6 + MnvTune v1". The other legend entries are "Published (PRD 104, 092007)" and "This
work (OmniFold)".

**(2) Source.**
- Producer `2d-unfolding/plot_2d_threeway_fig13.py:200` (`label="GENIE 2.12.6 + MnvTune v1"`, `color="red"`), called
  by `make_figures.sh:35`. The comment at :112-115 says it is "the proper analogue of the paper's MnvTune-v1 model
  curve".
- Printed elsewhere: paper `paper_body.tex:110-114`; note `sec_experiment.tex:24-25`.
- The R12 fix-round §4 (`PLAIN-LANGUAGE-REPORTS.md:4789-4804`) reached the same finding by pdftotext.

**(3) Already printed?** "Tune v1" appears in the primer (:361, :486, :491). "2.12.6" does not. Fig. 3's caption
prints "version 2.12.10" (:314) for the untuned GENIE.

**(4) Does a reader expect it?** **Yes.** A figure with an unidentified red curve is a defect for any reader. The
version number matters here because the very next figure prints 2.12.10 for a different simulation. Without both
numbers, a non-specialist has nothing to tell the two apart. The clause is self-explanatory.

**(5) Proposed text** (append to the caption, :266):
> The red curve is MINERvA's tuned simulation (Tune~v1, built on GENIE~2.12.6), the starting point of the unfolding;
> the untuned GENIE~2.12.10 of Fig.~\ref{fig:primergen} is a different simulation.
>
> % Legend: 2d-unfolding/plot_2d_threeway_fig13.py:200; paper_body.tex:110-111.

---

#### Summary table

| item | value(s) | source (at `34650231`) | already printed? | reader expects? | proposed text |
|---|---|---|---|---|---|
| paper F4 | model component median 12.0 / 9.6 / **13.4%** (RD1/RD2/RD3); target median total 68% half-width **≤ 10%**; RD3 fallback; "≈ 10–13% per coarse joint cell" | `sec_5d.tex:206-221`; `RECORD-20260927-s5p-stage2-exit.md:127-144` (VL155); no macro | note only (`sec_5d.tex:211-221`) | **yes** (the main negative result has no number); RD2 is 9.6%, so do not say "every definition exceeds 10%" | VII: "For its fallback definition, the 39 supported (E_avail,W) cells, the bounded model-dependence component alone has a median of 13.4%, above the target of a 10% median half-width for the total 68% interval." Abstract, Intro and Conclusions: "The measured model dependence, about 10–13% per cell, prevents … meet the 10% precision target we set in advance." |
| paper F5 | ratio **1.011** (1.0112), "about one percent"; 95.6% of bins within 10% | `\ratioTot` `values.tex:48`; receipt `RECEIPT-2d-agreement-windows-lgbm42-20261011.json` | paper Intro :60-61, IV A :241-243; primer :179; note `sec_results.tex:59` (1.1%) | **yes, weakly**; optional under the ~150-word budget | "… muon kinematics, with an integrated cross section within about 1% of the published value, and extends it …" |
| paper F7 | fine grid = 14×16×7×7×6 analysis binning (E_avail 7, q₃ 7, W 6 bins; edges in note) | edges `sec_method.tex:270-275`; dense grid `app_release.tex:65`; identification only in code `s5p_stage1_inspect.py:38-44` and the audit note `mapping-notes-C.md:25` (U 109×65856) | edges yes (note); "fine grid = this grid" nowhere | **yes**; add a note sentence first, since no record sentence makes the identification | VI A: "on a fine five-dimensional grid (the analysis binning: the published 14×16 muon-momentum bins times 7 E_avail, 7 q₃ and 6 W bins)" |
| paper F6 | **0.45–0.76 per halving** (proxy metric; calculation not recorded) | `\jtMoneWnormMin/Max` `values_inference.tex:38-39`; A7 `claims.rejection`; G6b unresolved (`RECORD-20261008-release-audit-corrections.md:241`) | note `sec_joint.tex:123-125` | **yes** (the sentence names the rate and gives its consequence) | "If the step kept shrinking geometrically by 0.45–0.76 per halving in a proxy of the test metric, a design-review value whose calculation is not recorded, the residual would be about one to three times the last step." |
| paper F12 | 74% = the s5c **F2** deterministic LightGBM variant (family N, negweight-refined; reproduced signal-only); median 9.7% | paper comment :535; `OUTCOME-20260925-s5n-…:25, 57, 75-82`; audit V19 | 74% printed; estimator not named (note `sec_5d.tex:75-77` only loosely) | **yes** (the next clause names the other estimator) | "the (E_avail,W) cells unfolded with the deterministic variant of the central-value estimator deviate from it by … up to 74% at high W" |
| paper F17 | S1 replicas use the central value's (un-resampled) completeness; not "no division". **No measured check on S1 found** | Stage B `REPORT.md:304, 341` (R5); `DESIGN.md:93` §3.4; `driver_p1.py` (3056e625) :2050-2052, :2357-2372; KI 84 | no | **yes, as a clause** (the paragraph raises the question); a factual claim, so the director's call; note first | paper: "Its replicas, like those of the rebuilt band, use the central value's completeness." Note `sec:uq-boot`: the same, with sources |
| paper IV C coverage test | futility: UCB < 0.66 (68%) / < 0.94 (95%), level 0.05/459, 400 per truth; tilt: **51/42 of 153** futile, min 0.060/0.288; nominal: **2** at 95% (min 0.850) | `OUTCOME-20260925-s5c-tier-s-futility-fail.md:30-48` (VL150, `interim_400.json`) | **no numbers anywhere** (note `sec_5d.tex:342-351` gives only "1,200 over three truths") | **yes** for the paper (supports decided C item F1); note first; print counts with the minimum | paper: "failed its criterion, fixed in advance: under the E_avail tilt, 51 of 153 reported cell and projection integrals have 68% coverage confidently below nominal (as low as 0.06), and at nominal truth two fail at 95%." |
| primer F7 | s_proj **6.145%** (GRADE json 0.061454); CV move **6.02%** of σ (CENTRAL-VALUE-VS-SIGMA json 0.060220); σ_ext **4.502e-38** (ledger :1615; three-prior spread 4.367–4.502) | `values.tex:407, 458, 273` | paper 6.145% (:927, :930); note 6.145 (`sec_5d.tex:478, 495`), 6.02 (:520), 4.502e-38 (`sec_fps.tex:112` and more) | **round** for a non-specialist (not a missing number); keep the two 6% objects distinct in words | "about 6%", "at most about 6% of their own uncertainty", "σ_ext ≈ 4.5×10⁻³⁸ cm²/nucleon", via siunitx rounding of the same macros |
| primer F-new-1 | median **9.7%** ("about 10%"); max 74% | `OUTCOME-20260925-s5n-…:57, 75-77`; note `sec_5d.tex:73-74` | primer body :442 ("about 10%"); paper 74%; note both | **yes**, in item 2 | item 2: "(in a test of generator size, typical cells come back about 10% off)" |
| primer F-new-2 | shares **67%** at E_avail ≥ 0.8, **83%** of that at W ≥ 1.8, **22%** in the catch cell; ratios 12–30% (corner) **and 23–31% (W < 1.1)** | `sec_eavailw.tex:49-53`; `\figTwo*` `values.tex:497-500` (release arrays) | paper :571-576; note (shares) | **yes, the share**; a ratio alone would mislead (low W is as high) | "About two thirds of the extra cross section, summed over cells, lies at high available energy, most of it at high W; about a fifth sits in the single widest corner cell." |
| primer F-new-8 | red curve = **Tune v1 on GENIE 2.12.6** (legend "GENIE 2.12.6 + MnvTune v1") | `plot_2d_threeway_fig13.py:200`; `make_figures.sh:35`; paper :110-111; note `sec_experiment.tex:24` | Tune v1 yes; 2.12.6 not in primer | **yes** (an unidentified curve; Fig. 3 prints 2.12.10) | caption: "The red curve is MINERvA's tuned simulation (Tune v1, built on GENIE 2.12.6), the starting point of the unfolding; the untuned GENIE 2.12.10 of Fig. 3 is a different simulation." |

---

## P9. Prompt: PRD-style rewrite of the paper (round 2) (sha256 `907a61036bffd6b0…`)

Do not use any tools, commands or files: everything you need is in this message. Answer directly, in text, in full.

You are an experienced author and editor of Physical Review D papers in experimental neutrino physics (unfolded cross-section measurements, multi-universe systematics, calibrated hypothesis tests). Below are the LaTeX sources of a PRD manuscript (abstract, body, data-availability statement) and a file listing extra numbers the authors have decided may be added, with their sources and cautions.

The authors want the paper to read like a normal PRD paper. A previous rewrite kept every caveat in place and the paper still reads like an internal audit record. They have decided:
- A. State numbers the text hedges around where a reader expects them and can interpret them in place (use only the numbers in numbers-available.md, respecting its cautions; e.g. do NOT say every model-dependence definition exceeds 10%; do NOT say the statistical block is "built without the completeness division").
- B. Move analysis history (earlier versions, rebuilt bands, repaired defects, lost/interrupted batch jobs, implementation chronology) and repeated caveats out of the paper into the companion analysis note (cited as \cite{AnalysisNote2026}). The paper gives the final procedure, and one short paragraph on which choices were made after results were seen (those post hoc disclosures must stay in the paper).
- C. Two claims become more precise: the failed five-dimensional coverage test is stated as miscoverage at the tested truths (not merely "not established"); the generator rejections are rejections of the hybrid null hypotheses built from each prediction.
- The abstract must be about 150 words (it is now ~230): headline results plus only the limitations a reader needs not to misread them. State each other limitation once in the body, at the claim it qualifies. Narrow a claim rather than stack qualifiers on a broad one.

Hard constraints (a reviewer will check each against the original):
1. Do not strengthen any claim. In particular keep: the rejections are of hybrid nulls under a stated nuisance model with no calorimetric recoil-response uncertainty, and fine-grid convergence is not shown; the joint five-observable information is not shown to discriminate beyond matched coarse projections; GENIE CV is not rejected by the muon-kinematic projection alone; the 3–5D results are central values only, with no significance assigned; the 2D comparison's chi2/ndf (2.65 against the published covariance) and its learner dependence; the 2D total uncertainty has no coverage test; the post hoc choices.
2. Do not weaken or drop any limitation that affects a conclusion; you may compress, merge duplicates and move history to the note.
3. Keep every \label, and keep \ref/\cite keys valid (only use keys that appear in the source). Keep value macros (e.g. \uqMedian, \ratioTot) rather than typing their numbers.
4. Keep LaTeX that compiles in revtex (no new packages).

Rewrite: (i) the abstract; (ii) the Introduction's results paragraph(s); (iii) Sec. IV B; (iv) Sec. IV C; (v) the last paragraph of Sec. VI A, Sec. VI B condition (i), and the lost/interrupted pseudo-experiment paragraph of Sec. VI C; (vi) Sec. VII; (vii) Sec. VIII; (viii) the Data availability statement. You may also propose moving Sec. VII before Sec. V if you think that serves the reader (say so and why).

Output, in this order:
A. For each rewritten unit: the complete replacement LaTeX in a fenced block, preceded by its unit label.
B. A table of every sentence or clause you removed from the paper: the original text (short quote), and whether it is (moved to note) / (merged into: where) / (dropped: why it is not needed).
C. A table of every number you added, with its source line in numbers-available.md.
D. Word counts: old and new abstract; old and new total for the units you rewrote.

---

## P10. Prompt: rewrite of the primer (round 2) (sha256 `3ea8c1d66b3033fd…`)

Do not use any tools, commands or files: everything you need is in this message. Answer directly, in text, in full.

You are an expert science writer and former experimental particle physicist. Below are the LaTeX sources of a plain-language primer (abstract and body) on a MINERvA neutrino cross-section analysis with machine-learning unfolding (OmniFold), written for a physics-literate non-specialist, plus a file of extra numbers the authors have decided may be added (with sources and cautions).

Outside readers found pages 1–4 good, but from the findings onward the primer reads like a review record: a findings overview that pre-lists every qualification, a long block of limits (about five pages of limits against two of findings), PET development history displacing the main results, and the joint generator test missing from the takeaway. The authors have decided:
- Move history and technical detail the reader does not need (PET development chronology, design-study narrative, the six-item condition list, the kappa scan details, lists of repaired defects) out of the primer to the companion paper/analysis note (cite the existing keys); keep one or two plain sentences where a reader needs the point.
- State the numbers in numbers-available.md where this reader expects them (the corner-excess share, the ~10% changed-truth bias, rounding 6.145% to about 6% etc.), respecting its cautions.
- Keep the abstract to about 150 words.
- Reorder Section 3 so the reader first learns what was found and how firmly, then the limits that matter most (rank them; name the top two or three), then the joint test, then PET briefly, then the extended signal definition. Put the joint-test result in the takeaway.

Hard constraints (a reviewer checks against the original): do not strengthen any claim (keep: the 3–5D results are central values only; the joint test rejects hybrid nulls under stated conditions, with no calorimetric response uncertainty and unproven fine-grid convergence; no added discrimination over matched coarse projections is shown; the quoted 2D statistical error bars have had no coverage test; the post hoc choice of learner implementation; "a first at MINERvA" stays limited to unbinned unfolding); do not drop a limitation that affects a finding — compress and rank instead; keep every \label and valid \ref/\cite keys; keep value macros; LaTeX must compile in a standard article class.

Output, in this order:
A. The new Section 3 and Section 4 (takeaway) and the new abstract as complete LaTeX, each in a fenced block. If you change Sections 1–2, give only the changed paragraphs, each with the original's opening words.
B. A table of every removed sentence or paragraph: short quote, and (moved to note/paper) / (merged into: where) / (dropped: why).
C. A table of numbers added, with their source line in numbers-available.md.
D. Word counts old/new for the abstract and for Sections 3–4.

---

## P11. X2 Gemini 3.8 Flash: paper rewrite (sha256 `0e8c7fec9efb0709…`)

##### Structural Proposal: Moving Sec. VII before Sec. V

We recommend moving **Sec. VII ("Status of a five-dimensional uncertainty")** to precede **Sec. V ("Central-value results")** (e.g., as Sec. V, shifting the results and joint tests to Secs. VI and VII). 

**Rationale:**
1. **Direct narrative continuity:** Sec. IV concludes by showing that the five-dimensional unfolding exhibits substantial regularization bias, seed sensitivity, and interval miscoverage. Moving Sec. VII immediately after Sec. IV directly resolves the methodological question: it establishes why a full measurement covariance meeting pre-registered precision targets could not be formed (unfolding-model dependence of 10--13\% exceeding the 10\% target, and estimator seed instability).
2. **Context for the reader:** When readers encounter the multidimensional distributions in Sec. V, they will already understand why those distributions are presented strictly as *central values only*, with no error bars or covariance-based generator significance.
3. **Motivation for hypothesis testing:** It establishes the absence of a measurement covariance as the direct motivation for the calibrated joint hypothesis testing in Sec. VI.

***

##### A. Replacement LaTeX Units

###### Unit (i): Abstract
```latex
\begin{abstract}
We apply multidimensional unbinned unfolding with OmniFold to MINERvA open data
for medium-energy $\nu_{\mu}$ charged-current inclusive interactions.  The
analysis reproduces the published double-differential muon-kinematic cross
section to within about 1\% in the integrated cross section and extends it to
five simultaneous observables by adding available hadronic energy,
three-momentum transfer, and hadronic invariant mass.  While marginal
normalizations and low-dimensional closure tests succeed, the unfolding exhibits
substantial regularization bias under generator-level shape variations.  The
measured model dependence, about 10--13\% per cell, prevents a five-dimensional
measurement whose total uncertainties meet our 10\% precision target, leaving the
higher-dimensional results as central values.  We instead perform calibrated
hypothesis tests through the full analysis chain.  At the 5\% familywise level,
the tests reject the hybrid null hypotheses built from five generator
predictions (MINERvA Tune~v1, GENIE~2.12.10 with and without Valencia
two-particle--two-hole contributions, NuWro~21.09, and GiBUU~2019) in total and
in shape.  These rejections are subject to unquantified fine-grid convergence and
the absence of calorimetric recoil-response uncertainties in the nuisance model,
and they do not demonstrate discrimination beyond matched coarse projections.
\end{abstract}
```

###### Unit (ii): Introduction Results Paragraphs
```latex
As an application, we test specified generator predictions.  The published
muon-kinematic measurement already disfavours these generator
families~\cite{MINERvA:2021owq}.  We calibrate each test through the full
analysis chain, using an estimator with unbinned background refinement, so that the
estimator's bias toward its prior enters each simulated null distribution
(Sec.~\ref{sec:joint}).

The two-dimensional reproduction agrees with the published total cross section
to about one percent (ratio $\ratioTot$), with \SI{\binsTen}{\percent} of the
205 bins within \SI{10}{\percent}.  The higher-dimensional central values agree
in normalization with the lower-dimensional results they extend and recover
the known low-recoil discrepancy; the three- and four-observable central values
also pass closure tests with injected shape changes.
Pseudo-experiments that include backgrounds, however, reveal a
background-subtraction bias of up to \SI{4}{\percent} in simulation in the
highest-$W$ cells, which an unbinned treatment largely removes.  The unfolding
also exhibits substantial regularization bias under generator-level $\Eavail$
shape variations.  This model dependence, about 10--13\% per cell, prevents a
five-dimensional measurement whose total uncertainties meet the 10\% precision
target set in advance, leaving the higher-dimensional results as central values.
All ten calibrated tests reject the hybrid null hypotheses built from the five
predictions, in total rate and in shape, at the 5\% familywise level under six
stated conditions (Sec.~\ref{sec:conditions}).  Two of them---the absence of a
calorimetric recoil-response uncertainty and the undemonstrated convergence of
the fine grid on which the null hypotheses are defined---limit their physical
interpretation.  Each test also has $p<0.05$ in at least one matched coarse
projection of the same cells, so the joint information is not shown to add
discrimination.
```

###### Unit (iii): Section IV B
```latex
\subsection{Two-dimensional uncertainty and its coverage}
\label{sec:uq2d}

The covariance of our two-dimensional result is the sum of four terms, which
we call blocks: systematic universes, statistical, training seed, and run
period.  The first three are obtained from ensembles of LightGBM unfoldings with
the central value's estimator, and the fourth from LightGBM unfoldings of three
groups of run periods.  The resulting relative uncertainty has a median of
\SI{\uqMedian}{\percent} per bin and is \SI{\uqIntegral}{\percent} on the
integrated cross section, compared with \SI{\uqPaper}{\percent} and
\SI{\uqPaperIntegral}{\percent} for the publication.  The systematic-universe
block dominates it bin by bin (a median \SI{87}{\percent} of the variance) and
in the integral, and the run-period block raises the per-bin median from
\SI{\uqSFiveMedian}{\percent} to \SI{\uqMedian}{\percent}.  In the
systematic-universe block, the flux universes carry the MINERvA analysis
toolkit's per-universe neutrino--electron-scattering and inverse-muon-decay
constraint weights.  The published flux uncertainty (median \SI{4.01}{\percent})
is larger than ours (\SI{\fluxBand}{\percent}); we could not determine the reason
from the released inputs.  The systematic and statistical blocks use the central
value's training seed.  The training-seed block uses five seed settings,
including that one; its median is \SI{0.06}{\percent} per bin, and its variance
is itself uncertain by about \SI{70}{\percent}.

The systematic-universe unfoldings approximate the weighting of events that fail
reconstruction, and we do not correct this approximation.  We tested it in two
of the 187 universes (one resonance-production and one flux universe), each at
two training seeds.  Neither showed an effect above the noise of an earlier
ten-seed training scan, which is about three times the training-seed block.  The
test cannot exclude an effect below about twice that noise, so it is not tight.

Data from different run periods are not mutually consistent within the other
uncertainties.  One period group's unfolded $\pPar$ distribution, taken relative
to its own simulation, differs from that of the earliest periods by a step of
about \SI{7}{\percent} near \SI{8}{GeV/c}.  The cause is not known, and these
data cannot establish which period is correct.  Following this post hoc
observation, we include the effect of this inconsistency on the combined result
as the run-period block.  It is built from the differences among three period
groups, without choosing any as the reference.  Its median is \SI{2.1}{\percent}
per bin; it is \SIrange{1.2}{3.4}{\percent} on the $\pPar$ projections and
\SI{2.0}{\percent} on the integrated cross section.  The block uses double
ratios between groups: each group's unfolded result is taken over its own
simulated truth, and each group is unfolded through its own simulated detector
response.  It does not identify a correct period.  Its interpretation is limited
by the small number of groups, by possible shrinkage from the regularization,
and by the statistical and training noise it retains.  Because the block is built
from the differences among the periods, it contains them by construction; this
says nothing about its coverage, that is, whether its size is right.  For the
same reason, the block's own consistency check passes whatever the data, and it
is not a test.

The statistical block is a bootstrap of 300 replicas drawn at the central
value's training seed (data, signal simulation and background simulation
resampled in three independent streams), with a median statistical uncertainty of
\SI{0.684}{\percent}.  The mean of the replicas differs from the central value
by a per-bin median of 0.26 statistical standard deviations; the block is a
covariance about that mean, so it does not include this offset.  Its replicas,
like those of the rebuilt band, use the central value's completeness.  The
coverage of this block has not been tested, and the coverage of the total
remains untested.  Earlier iterations of the uncertainty budget, their diagnostic
coverage tests, and repaired implementation defects are detailed in the
companion analysis note~\cite{AnalysisNote2026}.

In summary, we report a reproducible two-dimensional central value with a
covariance built with the same estimator, under the conventions stated in the
analysis note~\cite{AnalysisNote2026}.  The coverage of its total intervals has
not been validated on independent simulated samples, nor simultaneously over all
reported bins and projections, and the covariance provides no calibrated
significance for generator comparisons.  The following are not included in any
block of the covariance: the approximation in the systematic-universe
unfoldings, the dependence on the machine-learning estimator
(Sec.~\ref{sec:repro2d}), and the dependence on the unfolding model and its
regularization.  We assume that the detector response varies only within its
parametrized family.  Validated total intervals over the full reporting domain
would require an independent simulation sample of production size, a validated
generator of continuous nuisance-parameter variations, and independent-generator
samples that have not already been inspected.
```

###### Unit (iv): Section IV C
```latex
\subsection{Higher-dimensional central values}

Each higher-dimensional central value is checked against the lower-dimensional
result it extends.  The three-, four-, and five-observable marginal
normalizations agree at the approximately $1$--$2\%$ level, and a closure test
recovers an injected $\Eavail$ distortion.  These closure tests reweight the
simulated signal only.  End-to-end pseudo-experiments that include the
purity-based background subtraction reproduce the input at nominal truth except
in the highest-$W$ cells, which are biased by up to \SI{4}{\percent} in
simulation, about one quoted standard deviation in one $(\Eavail,W)$ cell; the
quoted uncertainties omit this bias.  The unbinned negative-weight background
treatment, as first measured with a deterministic variant of the
five-dimensional LightGBM central-value estimator, reduces it to below
\SI{0.3}{\percent}, leaving up to \SI{1}{\percent} in some joint cells; on data
the two treatments differ by at most \SI{1.4}{\percent}.

The unfolding recovers only part of a change of the $\Eavail$ shape as large as
the difference between generators.  When the true shape is reweighted by the
GiBUU-to-GENIE ratio, the $(\Eavail,W)$ cells unfolded with the deterministic
variant of the central-value estimator deviate from it by a median of
\SI{9.7}{\percent} (several percent in the largest cells) and by up to
\SI{74}{\percent} at high $W$, with or without background, so background
subtraction alone does not explain the residual.  This regularization bias is not
included in the quoted uncertainties, and it persists over the tested ranges of
iteration number and classifier capacity; for other fixed generator shapes,
measured with the joint-test estimator, it is \SIrange{16}{31}{\percent} in the
most affected $(\Eavail,W)$ cell and within the quoted total uncertainty in about
half of those cells.  Input changes at the level of floating-point rounding move
the unfolded values on data by up to a few statistical standard deviations; for
the joint-test estimator this spread lies inside the data-bootstrap statistical
uncertainty, but it limits how exactly the central values can be reproduced.  An
end-to-end coverage test of bias-corrected statistical intervals from a
deterministic variant of the estimator failed its criterion, fixed in advance:
under an $\Eavail$ tilt, 51 of 153 reported cell and projection integrals have
68\% coverage confidently below nominal (as low as 0.06), and at nominal truth
two fail at 95\% (the lowest at 0.85).  The five-dimensional intervals therefore
exhibit substantial miscoverage at the tested truths.  In this implementation,
then, agreement in the marginal normalizations coexists with substantial
regularization bias, and the model dependence and interval miscoverage prevent
reporting validated total uncertainties, leaving the three- to five-dimensional
results as central values.  This motivates the full-chain calibrated comparisons
of Sec.~\ref{sec:joint}.
```

###### Unit (v): Section VI Selections

####### (v-a) Last paragraph of Sec. VI A
```latex
The ten tests are controlled at a familywise level $\alpha=\jtAlpha$ by the
Holm procedure~\cite{Holm:1979}, and a step rejects only when the 95\%
Clopper--Pearson interval~\cite{Clopper:1934} of $k/B$ lies entirely below its
Holm threshold.  Calibration proceeded in batches of \jtBatch{}
pseudo-experiments per null, to at most \jtBcap{}, until both of a null's
decisions were determined.  The hypotheses, statistics, shifted nulls,
multiplicity and stopping rules, and all inputs were specified in advance.
Two choices were informed by the data: reviewers of the test design had seen
descriptive per-cell residuals before it was fixed, and a bounded extension of
the production computing budget was approved while job outputs displayed
observed $p$ values.  This extension altered no statistic, shifted null,
threshold, or stopping rule, and the Monte Carlo $p$ values remain valid at the
number of pseudo-experiments reached.  An independent recomputation with
separately written code agrees with the production evaluation in all
\jtRecompRows{} compared quantities.  The specification fixed in advance and the
result are given in Ref.~\cite{JointTestRecord2026}, and full details in the
analysis note~\cite{AnalysisNote2026}.
```

####### (v-b) Sec. VI B Condition (i)
```latex
\subsection{Conditions}
\label{sec:conditions}

The decisions test the hybrid null hypotheses.  Each holds under six conditions
on the nuisance model, numbered as in the specification fixed in
advance~\cite{JointTestRecord2026}.  (i) Within each fine-grid cell (the
analysis binning: the published $14\times16$ muon-momentum bins times 7
$\Eavail$, 7 $q_{3}$, and 6 $W$ bins) the null truth has the Tune~v1's shapes,
and convergence of the fine grid has not been shown.  In the $L_{2}$ norm of the
per-cell relative changes, the last refinement step, from a twofold-merged grid
to the fine grid, is \jtMoneMin--\jtMoneMax{} of the whole change from the coarse
test grid.  The residual below the fine grid is therefore unmeasured and
potentially material.  If the step kept shrinking geometrically by
\jtMoneWnormMin--\jtMoneWnormMax{} per halving in a proxy of the test metric, a
design-review value whose calculation is not recorded, the residual would be
about one to three times the last step.  The shifted nulls used for the decisions
take its central estimate, $\pm\jtMoneKappa\,\delta_{\mathrm{fine}}$; robustness
checks, which do not enter the decisions, use its upper end,
$\pm\jtMoneKappaRobust\,\delta_{\mathrm{fine}}$.  The measured $L_{2}$ ratios
also allow slower convergence.  The rejections carry over from the simulated
hybrid null to $G$ itself only if replacing the Tune~v1's shape below the fine
grid by $G$'s moves the noise-free unfolded result by no more than
$\pm\jtMoneKappa\,\delta_{\mathrm{fine}}$ along $\delta_{\mathrm{fine}}$.
Separately from the decision rule, the scan of Sec.~\ref{sec:joint-results}
finds the rejections still determined for shifts along that direction up to about
$5.2\,\delta_{\mathrm{fine}}$; this bounds neither the residual nor the
convergence.
```

####### (v-c) Lost/Interrupted Pseudo-Experiment Paragraph of Sec. VI C
```latex
All submitted pseudo-experiments have been evaluated across every test and
shifted null, including \jtLostCal{} calibration and \jtLostPow{} power
pseudo-experiments completed in an extended run~\cite{JointTestRecovery2026}.
None reaches the observed statistic in any test or shifted null, and no
assignment of outcomes alters any decision.  The closest approach is \num{4.6}
below the observed value of \num{868.6} (GENIE~+~MEC shape, robustness shift).
Details of the batch execution and validation are documented in the companion
analysis note~\cite{AnalysisNote2026}.
```

###### Unit (vi): Section VII
```latex
\section{Status of a five-dimensional uncertainty}
\label{sec:uncertainty-status}

We have constructed a covariance for the five-dimensional central value and
evaluated its \zprojCells-cell $(\Eavail,W)$ projection; it is separate from the
joint-test calibration.  We quote no covariance-based generator significance,
because covariances from this estimator depend measurably on its random seed.  In
two test covariances built at two different seed settings, changing the seed
moves the projected uncertainty by \SI{\sprojMeasured}{\percent}, exceeding the
\SI{\sprojBound}{\percent} stability limit set before production.  This variation
did not decrease with ensemble size over the tested range
(\SI{\seedEffectNforty}{\percent}, \SI{\seedEffectNeighty}{\percent}, and
\SI{\sprojMeasured}{\percent} with 40, 80, and 160 random throws), whereas the
internal resampling noise floor fell from \SI{\floorNforty}{\percent} to
\SI{\floorNeighty}{\percent} between 40 and 80.  This comparison is based on one
seed pair with nested subsets of throws, so the variation across seed pairs and
at much larger ensembles remains unmeasured.  In addition, five of the
covariance's 45 uncertainty bands are evaluated at a fixed seed; the square root
of their contribution to the trace is \SI{\pinnedBandsSqrtTr}{\percent} of
$\sqrt{\mathrm{Tr}\,C}$.  Their seed sensitivity, and its net effect on the total
covariance, has not been determined.

A separate study investigated reporting definitions for a five-dimensional
measurement to assess whether total uncertainties could meet predefined
precision targets.  Three reporting definitions were evaluated: the 109 supported
joint cells, 27 coarser joint cells, and a fallback definition consisting of the
39 supported $(\Eavail,W)$ cells.  Across these definitions, the median bounded
model-dependence component is \SI{12.0}{\percent}, \SI{9.6}{\percent}, and
\SI{13.4}{\percent}, respectively.  None of the definitions could satisfy the
predefined target of a \SI{10}{\percent} median half-width for the total 68\%
interval: for the fallback definition of 39 $(\Eavail,W)$ cells, the model
component alone has a median of \SI{13.4}{\percent}, and while the coarse joint
grid has a model median of \SI{9.6}{\percent}, it exceeds the \SI{10}{\percent}
threshold once the \SI{1.4}{\percent} normalization uncertainty is included.
Because total uncertainties meeting our precision criteria could not be
established, the higher-dimensional unfolding results are reported as central
values only.  The joint hypothesis tests of Sec.~\ref{sec:joint} provide a
calibrated route to generator comparisons but do not constitute a measurement
covariance.  The full diagnostic record is preserved in the companion analysis
note~\cite{AnalysisNote2026}.
```

###### Unit (vii): Section VIII
```latex
\section{Conclusions}
\label{sec:conclusions}

This study applies OmniFold to MINERvA inclusive charged-current $\nu_{\mu}$
data, reproduces the published double-differential cross section in muon
kinematics, and extends unbinned unfolding to five simultaneous observables.
The results fall into three distinct categories.

First, the two-dimensional reproduction provides an end-to-end benchmark on data.
The integrated cross section agrees with the published measurement to about one
percent (ratio $\ratioTot$), with \SI{\binsTen}{\percent} of individual bins
agreeing within \SI{10}{\percent}.  A correlated shape difference
($\chi^{2}/\mathrm{ndf}=\chiPaper$ against the published covariance) depends on
the choice of machine-learning estimator at the level of one unit of
$\chi^{2}/\mathrm{ndf}$.  The quoted two-dimensional covariance incorporates
systematic, statistical, training-seed, and run-period uncertainties, but its
total coverage has not been independently validated.

Second, the higher-dimensional central values extend the measurement to five
kinematic axes, recovering the established low-recoil discrepancy and passing
marginal consistency and low-dimensional closure tests.  However,
pseudo-experiments demonstrate that the unfolding follows truth variations of
generator size only partially, exhibiting substantial regularization bias.  The
resulting model dependence, about 10--13\% per cell, prevents a five-dimensional
measurement whose total uncertainties meet the 10\% precision target set in
advance, and interval coverage tests exhibit substantial miscoverage at the
tested truths.  Consequently, the higher-dimensional results are reported as
central values only, without an associated measurement covariance or
significance.

Third, we implement calibrated hypothesis tests through the full analysis chain,
incorporating the estimator's prior bias and nuisance variations into each null
distribution.  Under six stated conditions, the tests reject the hybrid null
hypotheses built from all five tested generator predictions (MINERvA Tune~v1,
GENIE~2.12.10 with and without Valencia two-particle--two-hole contributions,
NuWro~21.09, and GiBUU~2019) in total rate and in shape at the 5\% familywise
level, and completing all submitted pseudo-experiments confirms these decisions.
Because each prediction is also rejected ($p<0.05$) in matched coarse
projections of the same cells, the tests do not establish that the joint
five-observable information provides additional discrimination.  Furthermore,
their physical interpretation is subject to unquantified fine-grid convergence
and the omission of calorimetric recoil-response uncertainties from the nuisance
model.  Overcoming these limitations in future multidimensional unfolding will
require dedicated response uncertainties in the calibration chain, demonstrated
fine-grid convergence, and independent datasets to constrain model dependence.
```

###### Unit (viii): Data Availability Statement
```latex
\section*{Data availability}
\label{sec:data-availability}

The input data and simulation are the MINERvA open-data AnaTuples, released under
CC0~\cite{MINERvA:OpenData}; this analysis used an earlier production of that
release, whose 2,374 input files are listed with their SHA256
checksums~\cite{AnaTuplePreservation2026}.  A release package of about
\SI{16}{MB}~\cite{ReleaseCandidate2026}, requiring only \texttt{numpy},
\texttt{scipy}, and \texttt{matplotlib}, reproduces every $p$ value, decision,
robustness result, and power figure of the joint tests, together with the
completion of all pseudo-experiments, the coarse-projection comparisons, and the
fine-grid $L_{2}$ ratios of condition~(i); regenerates
Figs.~\ref{fig:joint}--\ref{fig:joint-nulls}; and recomputes the numbers quoted
from Figs.~\ref{fig:joint} and~\ref{fig:generator-context}.  The multiplier scan
is recomputable from Ref.~\cite{JointTestKappa2026}.  The full event-level
processing, archived analysis products, and generator samples produced for this
analysis are documented in the release appendix of the companion analysis
note~\cite{AnalysisNote2026}.
\pubhold{deposit identifier and access route, after the separately authorized
release decision.}
```

***

##### B. Table of Removed Sentences and Clauses

| Unit | Original Text (Short Quote) | Disposition | Rationale / Destination |
| :--- | :--- | :--- | :--- |
| **Abstract** | *"Pseudo-experiments that include backgrounds, and studies of the uncertainties, show limitations..."* | Merged into: Abstract sentence on regularization bias | Compressed diagnostic list into the primary physical limitation. |
| **Abstract** | *"These rejections hold only under stated conditions."* | Dropped | Redundant with the explicit conditions stated immediately following. |
| **Abstract** | *"The tests recover known discrepancies, but they do not show that the tested joint five-observable information discriminates..."* | Merged into: Abstract final sentence | Retained the qualification while removing conversational phrasing. |
| **Intro** | *"This regularization bias, the dependence on the estimator's random seed, and the untested coverage limit the method..."* | Merged into: Intro results paragraph | Replaced abstract audit summary with concrete model dependence numbers. |
| **Intro** | *"Two of them, the absence of a calorimetric recoil-response uncertainty and the undemonstrated convergence..."* | Merged into: Intro results paragraph | Maintained conditions with direct PRD phrasing. |
| **Sec. IV B** | *"An earlier version of the statistical band undercovered in its tails in \covTwoDNtoy{} closure pseudo-experiments... The main cause, a division by the completeness... was removed in a rebuilt band."* | Moved to note | Implementation and defect history of superseded statistical bands (\cite{AnalysisNote2026}). |
| **Sec. IV B** | *"Rescoring the same pseudo-experiments against the rebuilt band is post hoc and partly circular... \SI{97.7}{\percent} fall within two standard deviations..."* | Moved to note | Intermediate post hoc rescoring diagnostics of superseded band (\cite{AnalysisNote2026}). |
| **Sec. IV B** | *"A review of the stored analysis products found errors in an earlier version of the uncertainty budget, among them a mismatch between the truth input..."* | Moved to note | Audit history of earlier analysis-product defect resolutions (\cite{AnalysisNote2026}). |
| **Sec. IV B** | *"The result's intervals, bias and covariance have not been independently validated. In particular, the coverage of its intervals has not been validated on independent simulated samples..."* | Merged into: Sec. IV B summary | Consolidated repeated coverage caveats into a single concise statement. |
| **Sec. IV B** | *"We make no claim about coverage. The analysis note also states the further approximations and limits."* | Dropped | Redundant repetition; preceding text explicitly states coverage is untested. |
| **Sec. IV C** | *"so frequentist coverage of the five-dimensional intervals has not been established. In this implementation, then, agreement in the marginal normalizations coexists with substantial regularization bias..."* | Merged into: Sec. IV C closing | Stated precisely as interval miscoverage at tested truths and reporting of central values only. |
| **Sec. VI A** | *"Calibration proceeded in batches of \jtBatch{} pseudo-experiments per null, to at most \jtBcap{}, until both of a null's decisions were determined, that is, until each interval lay entirely on one side of its threshold."* | Merged into: Sec. VI A last paragraph | Streamlined stopping-rule explanation. |
| **Sec. VI B** | *"Before any result was known, the size of the shifts was set from an assumed extrapolation. If the step kept shrinking geometrically, at a rate taken from the review of the test design, for which no calculation is recorded..."* | Merged into: Sec. VI B condition (i) | Stated extrapolation directly with the explicit halving rate values. |
| **Sec. VI C** | *"Batch-job time limits interrupted or prevented \jtLostCal{} calibration... Had every interrupted one exceeded the observed statistic, no test would have been rejected. We therefore reran the lost pseudo-experiments after the decisions... it first reproduced 16 completed pseudo-experiments exactly."* | Moved to note | Implementation narrative of computing timeouts, worst-case hypotheses, and test reproduction (\cite{AnalysisNote2026}). |
| **Sec. VI C** | *"Every submitted pseudo-experiment has now been observed, and no assignment of the lost outcomes changes any decision."* | Merged into: Sec. VI C replacement | Replaced batch recovery drama with definitive scientific statement that all pseudo-experiments were evaluated. |
| **Sec. VII** | *"It has not met the criteria that the analysis set in advance for an uncertainty. One of these criteria requires a bound fixed before the covariance was produced and can no longer be applied to it. We use the covariance only under an exception to the criteria..."* | Moved to note | Internal procedural exceptions and pre-registration bureaucracy (\cite{AnalysisNote2026}). |
| **Sec. VII** | *"A separate study looked for a definition of a five-dimensional measurement whose total uncertainties could meet these criteria. None of the definitions it considered could meet the precision targets set in advance... For its fallback definition, the bounded model-dependence component alone exceeded the target total width."* | Merged into: Sec. VII second paragraph | Replaced unquantified narrative with the reporting definitions, concrete model medians, and targets. |
| **Sec. VIII** | *"The three- to five-dimensional central values support only descriptive comparisons, without validated coverage of their total intervals and without a covariance-based generator significance."* | Merged into: Conclusions second category | Grouped neatly into the three structured outcome categories. |
| **Sec. VIII** | *"Studies of coverage and of the dependence on the estimator's seed show further limits: the quoted two-dimensional statistical block has had no coverage test... and the measured model dependence prevents a five-dimensional measurement..."* | Merged into: Conclusions second and third categories | Replaced audit listing with quantified findings. |
| **Sec. VIII** | *"and recovering every lost pseudo-experiment changes no decision."* | Merged into: Conclusions category 3 | Stated as completion of all pseudo-experiments. |
| **Data Avail.** | *"The package was assembled before the two-dimensional central value was changed to LightGBM, and it carries the exact-split curve. Fig.~\ref{fig:validation} and its numbers were instead regenerated separately..."* | Moved to note | Git release assembly history and intermediate software configuration chronology (\cite{AnalysisNote2026}). |
| **Data Avail.** | *"Rerunning the packaged files from an empty directory reproduces every value recorded in the package and every figure number that it checks."* | Merged into: Data availability paragraph | Condensed into standard description of release package reproducibility. |
| **Data Avail.** | *"Apart from the multiplier scan (recomputable from Ref.~\cite{JointTestKappa2026}), the other quoted numbers cannot be recomputed from this package. They, and the event-level processing, require the archived analysis products..."* | Merged into: Data availability paragraph | Replaced negative wording ("cannot be recomputed") with standard data/code repository pointers. |

***

##### C. Table of Added Numbers

| Number / Expression | Context & Placement | Source in `numbers-available.md` |
| :--- | :--- | :--- |
| `within about 1\%` | 2D integrated cross section agreement in Abstract | Paper F5 (lines 92--94, 115--121, 275) |
| `about 10--13\%` | Model dependence per cell in Abstract, Intro, Conclusions | Paper F4 (lines 38--40, 68--71, 78--83, 274) |
| `10\%` | Precision target (median total 68% half-width) in Abstract, Intro, Sec. VII, Conclusions | Paper F4 (lines 31--33, 62--65, 78--83, 274) |
| `\SI{9.7}{\percent}` | Median deviation under GiBUU/GENIE shape reweighting in Sec. IV C | Paper F12 (lines 173--174, 187, 277) |
| `51 of 153` | Cell and projection integrals futile at 68% coverage under $\Eavail$ tilt in Sec. IV C | Paper IV C coverage test (lines 230--234, 252--255, 279) |
| `as low as 0.06` | Lowest coverage observed under $\Eavail$ tilt for nominal 68% intervals in Sec. IV C | Paper IV C coverage test (lines 230--234, 252--255, 279) |
| `two` / `0.85` | Quantities failing at 95% at nominal truth / lowest coverage in Sec. IV C | Paper IV C coverage test (lines 230--234, 252--255, 279) |
| `14\times16\times7\times7\times6` | Published $14\times16$ muon bins $\times$ 7 $\Eavail$, 7 $q_3$, 6 $W$ bins in Sec. VI B condition (i) | Paper F7 (lines 129--136, 162--164, 276) |
| `\jtMoneWnormMin--\jtMoneWnormMax{}` (0.45--0.76) | Rate per halving in proxy metric behind $\kappa=2$ in Sec. VI B condition (i) | Paper F6 (lines 170--176, 196--199, 277) |
| `109`, `27`, `39` | Cell counts for reporting definitions (RD1, RD2, RD3) in Sec. VII | Paper F4 (lines 28--30, 60--62, 274) |
| `\SI{12.0}{\percent}`, `\SI{9.6}{\percent}`, `\SI{13.4}{\percent}` | Median model component across RD1, RD2, and RD3 in Sec. VII | Paper F4 (lines 30--31, 42--43, 274) |
| `\SI{1.4}{\percent}` | Normalization uncertainty causing RD2 to exceed 10% in Sec. VII | Paper F4 (lines 33--34, 274) |

***

##### D. Word Counts

| Section / Unit | Original Word Count | New Word Count | Difference |
| :--- | :---: | :---: | :---: |
| **Abstract** | 228 | 153 | $-75$ |
| **Intro Results Paragraphs** | 255 | 254 | $-1$ |
| **Sec. IV B (2D Uncertainty & Coverage)** | 835 | 588 | $-247$ |
| **Sec. IV C (Higher-D Central Values)** | 330 | 336 | $+6$ |
| **Sec. VI A (Last Paragraph)** | 195 | 164 | $-31$ |
| **Sec. VI B (Condition i)** | 235 | 246 | $+11$ |
| **Sec. VI C (Pseudo-Experiment Paragraph)** | 120 | 84 | $-36$ |
| **Sec. VII (Status of 5D Uncertainty)** | 295 | 298 | $+3$ |
| **Sec. VIII (Conclusions)** | 330 | 332 | $+2$ |
| **Data Availability Statement** | 225 | 154 | $-71$ |
| **Total (Rewritten Units)** | **3048** | **2609** | **$-439$** |

---

## P12. X2 GPT-6.1-sol: paper rewrite (sha256 `c2dfb47e51f14668…`)

#### A. Replacement LaTeX

I recommend moving Sec. VII immediately before Sec. V. Readers would then know the uncertainty status before encountering the higher-dimensional central-value comparisons. The existing labels and references can remain unchanged.

The short consequential edits below consolidate the post hoc disclosures into one paragraph and remove the remaining batch-job history. The companion note should receive the transferred material and the coverage-test numbers before publication.

##### (i) Abstract

```latex
\begin{abstract}
We apply OmniFold to MINERvA medium-energy $\nu_{\mu}$ charged-current
inclusive data.  The two-dimensional integrated cross section agrees with
the published value to about one percent (ratio $\ratioTot$).  Adding
available energy, momentum transfer, and hadronic invariant mass yields
three- to five-dimensional central values only.  The three- and
four-dimensional central values also pass closure tests with injected shape
changes.  These results recover the established low-recoil discrepancy, but
tested bias-corrected five-dimensional statistical intervals show
miscoverage at the tested truths.  Model dependence of about 10--13\% per
coarse cell prevents meeting the predefined precision criteria.
Full-chain calibrated total and shape tests reject the hybrid null
hypotheses constructed from all five tested predictions at the 5\%
familywise level.  These rejections apply under the specified nuisance
model, which lacks calorimetric recoil-response uncertainty; convergence
below the fine grid defining the nulls has not been shown.  The joint
five-observable information is not shown to discriminate beyond matched
coarse projections of the same cells.
\end{abstract}
```

##### (ii) Introduction: results paragraph

Replace the paragraph beginning “The two-dimensional reproduction agrees…” and ending “…add discrimination.”

```latex
The two-dimensional integrated cross section agrees with the published value
to about one percent (ratio $\ratioTot$), with
\SI{\binsTen}{\percent} of the 205 bins within \SI{10}{\percent}.
The three- to five-observable central values agree in marginal normalization
with the lower-dimensional results they extend and recover the established
low-recoil discrepancy.  Their validation and uncertainty limitations are
described in Secs.~\ref{sec:validation}
and~\ref{sec:uncertainty-status}.  For the fallback reporting definition,
the median bounded model-dependence component is \SI{13.4}{\percent},
above the target median total 68\% half-width of \SI{10}{\percent}.
The calibrated tests reject the total and shape hybrid null hypotheses
constructed from all five predictions at the 5\% familywise level, subject
to Sec.~\ref{sec:conditions}.  Matched coarse projections already yield
$p<0.05$ for every test in at least one projection, so additional
discrimination from the joint five-observable information is not demonstrated.
```

##### (iii) Sec. IV B: Two-dimensional uncertainty and its coverage

```latex
\subsection{Two-dimensional uncertainty and its coverage}
\label{sec:uq2d}

The covariance of the two-dimensional result is the sum of four blocks:
systematic universes, statistical, training seed, and run period.
The first three use ensembles of unfoldings with the central value's
LightGBM estimator; the fourth uses LightGBM unfoldings of three groups
of run periods.  The relative uncertainty has a per-bin median of
\SI{\uqMedian}{\percent} and is \SI{\uqIntegral}{\percent} on the
integrated cross section, compared with \SI{\uqPaper}{\percent} and
\SI{\uqPaperIntegral}{\percent}, respectively, for the publication.
The systematic-universe block dominates both the integral and the
individual bins, contributing a median \SI{87}{\percent} of the per-bin
variance.  Adding the run-period block raises the per-bin median uncertainty
from \SI{\uqSFiveMedian}{\percent} to \SI{\uqMedian}{\percent}.

The flux universes include the MINERvA analysis toolkit's per-universe
neutrino--electron-scattering and inverse-muon-decay constraint weights.
Their median uncertainty, \SI{\fluxBand}{\percent}, is smaller than the
published \SI{4.01}{\percent}; the released inputs do not establish the
reason.  The systematic and statistical blocks use the central value's
training seed.  The training-seed block uses five settings, including that
seed, and has a median uncertainty of \SI{0.06}{\percent} per bin.
Its variance is itself uncertain by about \SI{70}{\percent}.

The systematic-universe unfoldings approximate the weighting of events
that fail reconstruction.  This approximation is not corrected or included
as a covariance term.  Tests in two of the 187 universes, one
resonance-production and one flux universe, at two training seeds each
resolved no effect above the noise of a ten-seed training scan.
That noise is about three times the training-seed block, and the tests
cannot exclude effects below about twice that noise.

The run-period block describes an inconsistency among the data periods
within the other uncertainties.  Relative to its own simulated truth,
one period group's unfolded $\pPar$ distribution differs from that of the
earliest periods by a step of about \SI{7}{\percent} near
\SI{8}{GeV/c}.  The cause is unknown, and these data do not identify a
correct period.  Each group is unfolded with its own simulated detector
response, and the block is formed from differences among the three groups
using double ratios of their unfolded results to their own simulated
truths, without selecting a reference group.  Its median uncertainty is
\SI{2.1}{\percent} per bin, \SIrange{1.2}{3.4}{\percent} on the $\pPar$
projections, and \SI{2.0}{\percent} on the integral.  Its interpretation
is limited by the small number of groups, possible regularization
shrinkage, and retained statistical and training noise.
Containing the period differences and passing its own consistency check
are consequences of its construction, not evidence of coverage.

The statistical block is the covariance about the mean of 300 bootstrap
replicas at the central value's training seed.  Data, signal simulation,
and background simulation are resampled independently in three streams;
the replicas use the central value's completeness, obtained from the
un-resampled simulation.  The median statistical uncertainty is
\SI{0.684}{\percent}.  The replica mean differs from the central value
by a per-bin median of 0.26 statistical standard deviations; this offset
is not included in the covariance.

Neither the statistical block nor the total covariance has undergone a
coverage test.  The result's bias and covariance have not been independently
validated, and coverage has not been validated simultaneously over the
reported bins and projections.  The covariance supplies no calibrated
significance for generator comparisons.  In addition to the missed-event
approximation above, it excludes learner dependence
(Sec.~\ref{sec:repro2d}) and unfolding-model and regularization dependence,
whose assessment requires independent-generator samples.
The detector response is assumed to vary only within its parametrized
family.  Validating total intervals over the full reporting domain would
require an independent simulation sample of production size, a validated
generator of continuous nuisance variations, and independent-generator
samples not already inspected.  The complete construction, further
approximations, and validation history are documented in the companion
analysis note~\cite{AnalysisNote2026}.
```

##### (iv) Sec. IV C: Higher-dimensional central values

```latex
\subsection{Higher-dimensional central values}

The three-, four-, and five-observable central values agree in marginal
normalization with the lower-dimensional results they extend at
approximately the $1$--$2\%$ level.  Signal-only closure tests of the
three- and four-observable results recover injected $\Eavail$ shape changes.

End-to-end pseudo-experiments with purity-based background subtraction
recover nominal truth except in the highest-$W$ cells, where biases reach
\SI{4}{\percent}, about one quoted standard deviation in one
$(\Eavail,W)$ cell.  The quoted uncertainties omit this bias.
With a deterministic variant of the five-dimensional LightGBM
central-value estimator, unbinned negative-weight background treatment
reduces the bias below \SI{0.3}{\percent}, although residuals reach
\SI{1}{\percent} in some joint cells.  On data the two treatments differ
by at most \SI{1.4}{\percent}.

Recovery deteriorates for generator-sized changes of the truth shape.
For a GiBUU-to-GENIE $\Eavail$ reweighting, the deterministic variant of
the central-value estimator gives a median $(\Eavail,W)$ residual of
\SI{9.7}{\percent} and a maximum of \SI{74}{\percent} at high $W$.
The residual persists with or without background and over the tested
iteration counts and classifier capacities, identifying a regularization
bias that is absent from the quoted uncertainties.  For other fixed
generator shapes, the joint-test estimator has maximum cell residuals of
\SIrange{16}{31}{\percent}; about half of the $(\Eavail,W)$ cells lie
within the quoted total uncertainty.
Floating-point rounding changes the unfolded data values by up to a few
statistical standard deviations.  For the joint-test estimator this
spread lies within the data-bootstrap statistical uncertainty, but it
limits numerical reproducibility.

An end-to-end test of bias-corrected statistical intervals from the
deterministic estimator variant demonstrates miscoverage at the tested
truths.  With 400 pseudo-experiments per truth, 51 of 153 reported cell
and projection integrals fail the criterion fixed in advance for nominal
68\% intervals under an $\Eavail$ tilt, with coverage as low as 0.06;
42 fail for nominal 95\% intervals.  At nominal truth, two fail for
95\% intervals, with minimum coverage 0.85.  Failure means that an upper
confidence bound on coverage is below 0.66 or 0.94, respectively, at a
per-comparison level of $0.05/459$.
Thus agreement of marginal normalizations does not establish reliable
intervals or recovery of generator-sized departures.  These limitations
motivate the full-chain calibrated comparisons of Sec.~\ref{sec:joint};
the companion note gives the validation details~\cite{AnalysisNote2026}.
```

##### (v-a) Sec. VI A: last paragraph

```latex
The ten tests are controlled at familywise level $\alpha=\jtAlpha$
by the Holm procedure~\cite{Holm:1979}.  A step rejects only when the
95\% Clopper--Pearson interval~\cite{Clopper:1934} for $k/B$ lies
entirely below its Holm threshold.  Calibration uses batches of \jtBatch{}
pseudo-experiments per null, up to \jtBcap{}, stopping when both
intervals for that null lie entirely on one side of their thresholds.
The hypotheses, statistics, shifted nulls, multiplicity and stopping rules,
and inputs were fixed before production calibration or computation of
the observed statistics.  An independent implementation agrees with the
production evaluation in all \jtRecompRows{} compared quantities.
The specification and result are recorded in
Ref.~\cite{JointTestRecord2026}, with details in
Ref.~\cite{AnalysisNote2026}.

Several choices were informed by observed results.  The LightGBM
two-dimensional central value was selected after both learner comparisons
were known; design reviewers had seen descriptive cell residuals; and a
bounded computing-budget extension was approved with decision $p$ values
visible.  The extension changed no statistic, shifted null, threshold,
or stopping rule, and the Monte Carlo $p$ values remain valid at the
ensemble sizes reached.  The multiplier scan and matched-projection
comparison were specified before their execution, after the
five-dimensional decisions were known.
```

To make this the single paragraph containing the post hoc choices, apply these limited consequential edits:

```latex
% Sec. IV A:
% Delete only:
% "This choice, which replaced the exact-split result, was made after both
% comparisons were known."
%
% Retain the preceding sentence explaining estimator matching and the
% following numerical learner comparison.

% Sec. VI C, first paragraph:
% Replace the two sentences beginning "As a sensitivity check..." with:
As a sensitivity check outside the decision rule, we scanned the multiplier
of the shift along $\delta_{\mathrm{fine}}$~\cite{JointTestKappa2026}.

% In the same paragraph, replace:
% "with the recovered pseudo-experiments (below) included"
% by:
with all submitted calibration pseudo-experiments included

% Sec. VI C, matched-projection paragraph:
% Replace the sentence beginning "This comparison was specified..." with:
The comparison uses the same calibration ensembles, including all submitted
calibration pseudo-experiments, and its $p$ values were reproduced
independently~\cite{JointTestProjections2026}.

% In that paragraph, replace:
% "The rejections are global assessments of the five specified generator
% versions under the stated nuisance model;"
% by:
The rejections are global assessments of the hybrid null hypotheses
constructed from the five specified generator versions under the stated
nuisance model;

% Replace the power-study parenthesis with:
(each power estimate uses 172 to 199 of its 200 alternative
pseudo-experiments; the ensemble accounting is given in
Ref.~\cite{AnalysisNote2026}))
```

##### (v-b) Sec. VI B: condition (i)

Replace condition (i) only; retain the opening sentences and conditions (ii)–(vi).

```latex
(i) The fine grid is the analysis binning:
$14\times16\times7\times7\times6$ bins in
$(\pT,\pPar,\Eavail,q_{3},W)$, with Tune~v1 shapes within each cell.
Its convergence has not been demonstrated.  In the $L_{2}$ norm of
per-cell relative changes, the last refinement, from a twofold-merged
grid to the fine grid, is \jtMoneMin--\jtMoneMax{} of the full change
from the coarse test grid, leaving a potentially material unmeasured
residual.  The decision shifts,
$\pm\jtMoneKappa\,\delta_{\mathrm{fine}}$, assume geometric shrinkage
of \jtMoneWnormMin--\jtMoneWnormMax{} per halving in a proxy of the
test metric.  This design-review rate has no recorded calculation;
it implies a residual of about one to three last steps.
The robustness shifts use the upper estimate,
$\pm\jtMoneKappaRobust\,\delta_{\mathrm{fine}}$, and do not enter
the decisions.  The measured $L_{2}$ ratios permit slower convergence.
Extending a rejection from the hybrid null to $G$ itself requires that
replacing the subgrid Tune~v1 shape by $G$'s move the noise-free unfolded
result by no more than
$\pm\jtMoneKappa\,\delta_{\mathrm{fine}}$ along
$\delta_{\mathrm{fine}}$.  The directional sensitivity scan in
Sec.~\ref{sec:joint-results} bounds neither this residual nor convergence.
```

##### (v-c) Sec. VI C: lost/interrupted pseudo-experiment paragraph

```latex
Including every submitted calibration pseudo-experiment changes no decision.
None of the additional outcomes reaches the observed statistic in any test
or shifted null.  The smallest margin is \num{4.6} below the observed
\num{868.6}, for GENIE~+~MEC shape with the robustness shift.
The ensemble accounting and verification are documented in
Refs.~\cite{JointTestRecovery2026,AnalysisNote2026}.
```

##### (vi) Sec. VII: Status of a five-dimensional uncertainty

```latex
\section{Status of a five-dimensional uncertainty}
\label{sec:uncertainty-status}

The five-dimensional central value has a covariance and a
\zprojCells-cell $(\Eavail,W)$ covariance projection, separate from
the joint-test calibration.  This covariance does not satisfy the
analysis's predefined uncertainty criteria.  In particular, the required
bound fixed before covariance production is unavailable for this covariance,
so that criterion cannot be applied retrospectively.  Its use is restricted
to this covariance under the exception documented in
Ref.~\cite{AnalysisNote2026}; it supplies no covariance-based generator
significance.

Seed dependence also exceeds the predefined stability limit.
In two additional covariances, changing the seed moves the projected
uncertainty by \SI{\sprojMeasured}{\percent}, against a
\SI{\sprojBound}{\percent} limit.  The movement is
\SI{\seedEffectNforty}{\percent},
\SI{\seedEffectNeighty}{\percent}, and
\SI{\sprojMeasured}{\percent} for 40, 80, and 160 random throws,
respectively, whereas the fixed-seed resampling noise falls from
\SI{\floorNforty}{\percent} to \SI{\floorNeighty}{\percent}
between 40 and 80 throws.  These comparisons use one seed pair and
nested subsets; neither the spread across seed pairs nor substantially
larger ensembles has been studied.  Five of the 45 uncertainty bands
remain at a fixed seed.  The square root of their trace contribution is
\SI{\pinnedBandsSqrtTr}{\percent} of $\sqrt{\mathrm{Tr}\,C}$;
their seed sensitivity and its effect on the total in either direction
are unmeasured.

A separate study assessed whether alternative reporting definitions could
meet the predefined precision targets.  For 109 supported joint cells,
27 coarser joint cells, and 39 supported $(\Eavail,W)$ cells, the
bounded unfolding-model components have medians of
\SI{12.0}{\percent}, \SI{9.6}{\percent}, and
\SI{13.4}{\percent}, respectively.  These components are the largest
shifts over five generator-sized truth departures.
The target median total 68\% half-width is at most \SI{10}{\percent}.
The model component alone exceeds it for the first and third definitions;
the second reaches at least \SI{11.0}{\percent} after the
\SI{1.4}{\percent} normalization is included.
The fallback definition is the 39-cell $(\Eavail,W)$ projection.
Thus none of the considered definitions meets the precision targets
within the study's rules and computing budget.
The joint tests provide a separate route to inference through calibrated
hybrid null hypotheses, rather than a new measurement uncertainty.
```

##### (vii) Sec. VIII: Conclusions

```latex
\section{Conclusions}
\label{sec:conclusions}

We have applied OmniFold to MINERvA inclusive charged-current data.
The two-dimensional integrated cross section agrees with the published
value to about one percent; the binwise comparison and its learner
dependence are quantified in Sec.~\ref{sec:repro2d}.
The three- to five-observable results are central values only, supporting
descriptive comparisons without assigned significance.  They recover the
established low-recoil discrepancy, while the validation studies expose
background-subtraction bias, incomplete recovery of generator-sized shape
changes, and miscoverage of the tested five-dimensional statistical
intervals.  No considered reporting definition meets the predefined
five-dimensional precision targets.

Full-chain calibration rejects all ten total and shape hybrid null
hypotheses constructed from the five predictions at familywise level
$\jtAlpha$, under Sec.~\ref{sec:conditions}.
The joint information is not shown to discriminate beyond matched coarse
projections.  Extending the physical interpretation requires calorimetric
recoil-response uncertainty propagated through calibration and a
demonstrated bound on the unresolved fine-grid dependence.
```

##### (viii) Data availability

```latex
\section*{Data availability}
\label{sec:data-availability}

The input data and simulation are MINERvA open-data AnaTuples released
under CC0~\cite{MINERvA:OpenData}.  This analysis uses an earlier production;
its 2,374 input files and SHA256 checksums are listed in
Ref.~\cite{AnaTuplePreservation2026}.
A locally prepared candidate release of about
\SI{16}{MB}~\cite{ReleaseCandidate2026}, not yet deposited, requires
numpy, scipy, and matplotlib.

The package reproduces the joint-test $p$ values and decisions, packaged
robustness and power results, complete calibration-ensemble checks,
matched coarse-projection comparison, and fine-grid $L_{2}$ ratios.
It regenerates Figs.~\ref{fig:joint}--\ref{fig:joint-nulls}
and the quoted numerical summaries of
Figs.~\ref{fig:joint} and~\ref{fig:generator-context}.
A replay from an empty directory reproduces all recorded values and
figure numbers checked by the package.
The multiplier scan is separately reproducible from
Ref.~\cite{JointTestKappa2026}.

The package contains the exact-split two-dimensional curve.
Figure~\ref{fig:validation} and its numbers instead use the paper's
LightGBM central value and covariance, with separately generated
uncertainty bands.  Other quoted numbers and event-level processing
require the archived analysis products, open-data AnaTuples, and generator
samples produced for this analysis.  The companion note's release
appendix specifies the reproduction scope~\cite{AnalysisNote2026}.
\pubhold{deposit identifier and access route, after the separately authorized
release decision.}
```

#### B. Removal and merger accounting

The table tracks substantive prose, including clauses absorbed into replacements. Source comments and drafting annotations are omitted from the replacement LaTeX; they belong in the analysis record.

| Unit | Original sentence or clause: short quotation | Disposition |
|---|---|---|
| Abstract | “test the practical limits of multidimensional unbinned unfolding” | **Merged into:** opening application statement and specific results. |
| Abstract | “reproduces the published double-differential cross section” | **Merged into:** narrower, quantified integrated agreement. |
| Abstract | “extends it to five simultaneous observables” | **Merged into:** three- to five-dimensional central values only. |
| Abstract | “pass checks of their marginal normalizations” | **Merged into:** Introduction and IV C. |
| Abstract | “three- and four-observable central values pass closure checks” | **Merged into:** abstract closure sentence. |
| Abstract | “show limitations of the background treatment…random seed” | **Merged into:** specific abstract coverage statement; individual limitations retained in IV B, IV C, and VII. |
| Abstract | “predefined criteria at useful precision” | **Merged into:** quantified model dependence; target defined in Introduction and VII. |
| Abstract | Parenthetical list of five predictions | **Dropped:** identities remain explicitly listed in VI A; unnecessary for interpreting the abstract result. |
| Abstract | “reject all five tested predictions” | **Merged into:** rejection of their hybrid null hypotheses. |
| Abstract | “These rejections hold only under stated conditions” | **Merged into:** immediately stated nuisance-model and grid limitations. |
| Abstract | “The tests recover known discrepancies” | **Merged into:** low-recoil result in abstract and existing VI C comparison with the published measurement. |
| Abstract | “do not show…joint five-observable information discriminates beyond…” | **Merged into:** final abstract sentence. |
| Abstract | “Their physical interpretation is limited because…” | **Merged into:** explicit conditional-rejection sentence. |
| Introduction | “higher-dimensional central values agree in normalization…” | **Merged into:** marginal-normalization result. |
| Introduction | “three- and four-observable…pass closure tests” | **Merged into:** IV C; removed from this summary to avoid repeating validation details. |
| Introduction | “background-subtraction bias of up to…4 percent” | **Merged into:** IV C, where estimator and simulation scope are stated. |
| Introduction | “An unbinned treatment…largely removes it” | **Merged into:** quantified IV C background comparison and existing method description. |
| Introduction | “the quoted uncertainties do not include it” | **Merged into:** IV C background-bias sentence. |
| Introduction | “recovers only part of…difference between generators” | **Merged into:** quantified recovery study in IV C. |
| Introduction | “regularization bias…random seed…untested coverage” | **Merged into:** IV B, IV C, and VII at the relevant claims. |
| Introduction | “measured model dependence prevents…useful precision” | **Merged into:** fallback median and target comparison. |
| Introduction | “All ten calibrated tests…reject” | **Merged into:** explicit hybrid-null rejection sentence. |
| Introduction | “absence of a calorimetric recoil-response uncertainty…fine grid” | **Merged into:** conditions (i)–(ii) and existing hadronic-response subsection; summary refers directly to conditions. |
| Introduction | “Each test also has…at least one matched coarse projection” | **Merged into:** final results sentence. |
| IV B | “sum of four terms, which we call blocks” | **Merged into:** opening covariance definition. |
| IV B | “The first three are obtained from ensembles…” | **Merged into:** estimator-matched construction sentence. |
| IV B | “The resulting relative uncertainty…” | **Merged into:** unchanged macro-based uncertainty comparison. |
| IV B | “dominates it bin by bin…and in the integral” | **Merged into:** variance-share sentence. |
| IV B | “run-period block raises the per-bin median…” | **Merged into:** explicit before/after median sentence. |
| IV B | Flux constraint weights and unexplained smaller flux band | **Merged into:** flux paragraph; both facts retained. |
| IV B | Central-value seed; five seed settings; seed-block size and variance uncertainty | **Merged into:** compact training-seed paragraph. |
| IV B | “we do not correct this approximation” | **Merged into:** explicit statement that the approximation is uncorrected and outside the covariance. |
| IV B | “Neither showed an effect above the noise of an earlier ten-seed training scan” | **Merged into:** numerical diagnostic sensitivity statement; “earlier” **moved to note** as chronology. |
| IV B | “The test cannot exclude…so it is not tight” | **Merged into:** explicit exclusion limit; evaluative repetition dropped. |
| IV B | “Data from different run periods are not mutually consistent” | **Merged into:** opening run-period sentence. |
| IV B | “One period group's…step of about 7 percent” | **Merged into:** same double-ratio observation, retaining its definition. |
| IV B | “The cause is not known…which period is correct” | **Merged into:** one sentence. |
| IV B | “We include the effect…as the run-period block” | **Merged into:** opening and construction sentences of run-period paragraph. |
| IV B | “differences among three period groups…without choosing…reference” | **Merged into:** double-ratio construction sentence. |
| IV B | Run-period median, projections, and integral uncertainty | **Merged into:** single numerical sentence. |
| IV B | “The block uses double ratios…” | **Merged into:** construction sentence, including each group's own response. |
| IV B | “It does not identify a correct period” | **Merged into:** earlier unknown-cause sentence. |
| IV B | “small number…shrinkage…statistical and training noise” | **Merged into:** one limitations sentence. |
| IV B | “contains them by construction…nothing about its coverage” | **Merged into:** final construction-versus-coverage sentence. |
| IV B | “its own consistency check passes whatever the data” | **Merged into:** same sentence, explicitly identifying a construction consequence. |
| IV B | Bootstrap construction and median statistical uncertainty | **Merged into:** statistical-block paragraph. |
| IV B | “mean…differs…0.26…does not include this offset” | **Merged into:** two short statistical-block sentences. |
| IV B | “coverage of this block…total remains untested” | **Merged into:** opening sentence of final paragraph. |
| IV B | “An earlier version…undercovered…fixed truth” | **Moved to note:** historical test of a different statistical band. |
| IV B | Earlier-band two-standard-deviation coverage and nominal comparison | **Moved to note:** same historical coverage test. |
| IV B | “division by the completeness…removed in a rebuilt band” | **Moved to note:** defect and repair history; present recipe now states which completeness is used. |
| IV B | “Rescoring…post hoc and partly circular” | **Moved to note:** rescoring did not validate the quoted block and is no longer used to support a paper claim. |
| IV B | “97.7…78.1…wider than the toy scatter” | **Moved to note:** results for the historical rebuilt band. |
| IV B | “rebuilt band…not independently tested…different ensemble” | **Moved to note:** ensemble history; current block's untested coverage remains explicit. |
| IV B | “review…found errors…mismatch…background templates” | **Moved to note:** construction and repair history, including its `TwoDFollowup2026` citation. |
| IV B | “quoted covariance is free of both” | **Moved to note:** repair verification; final construction is stated directly. |
| IV B | “In summary, we report a reproducible…same estimator” | **Merged into:** opening estimator-matched construction; redundant summary removed. |
| IV B | “intervals, bias and covariance…not independently validated” | **Merged into:** final paragraph, with the more direct coverage statement. |
| IV B | “nor simultaneously over all reported bins and projections” | **Merged into:** explicit simultaneous-coverage limitation. |
| IV B | “no calibrated significance for generator comparisons” | **Merged into:** same explicit limitation. |
| IV B | “The following are not included in any block…” | **Merged into:** exclusions stated beside the approximation and in final paragraph. |
| IV B | Parametrized detector family and required independent inputs | **Merged into:** final paragraph; all three required input categories retained. |
| IV B | “We make no claim about coverage” | **Merged into:** explicit absence of statistical, total, independent, and simultaneous coverage validation. |
| IV B | “further approximations and limits” | **Merged into:** final companion-note reference. |
| IV C | “Each higher-dimensional central value is checked…” | **Merged into:** quantitative marginal-normalization statement. |
| IV C | “a closure test recovers an injected…distortion” | **Merged into:** explicitly scoped three- and four-observable signal-only closure result. |
| IV C | Nominal-truth purity bias and omitted uncertainty | **Merged into:** background-validation paragraph. |
| IV C | “as first measured with a deterministic variant” | **Merged into:** estimator attribution; “first measured” **moved to note** as chronology. |
| IV C | Negative-weight residuals and data-treatment difference | **Merged into:** same paragraph; all numerical limits retained. |
| IV C | “recovers only part of…difference between generators” | **Merged into:** quantified generator-sized recovery paragraph. |
| IV C | “several percent in the largest cells” | **Merged into:** recorded median and maximum; replaces a vague summary without asserting a new large-cell result. |
| IV C | “with or without background…alone does not explain” | **Merged into:** background-independent persistence statement. |
| IV C | “regularization bias…not included…persists…” | **Merged into:** one sentence retaining uncertainty omission and tested iteration/capacity scope. |
| IV C | Other-generator residual range and approximately half within uncertainty | **Merged into:** explicitly attributed joint-test-estimator sentence. |
| IV C | Rounding-level input sensitivity and bootstrap comparison | **Merged into:** final two sentences of recovery paragraph. |
| IV C | “failed its criterion…coverage…not been established” | **Merged into:** demonstrated miscoverage at tested truths, with test counts and magnitude. |
| IV C | “agreement…coexists with substantial regularization bias…” | **Merged into:** narrowed conclusion that marginal agreement does not establish intervals or recovery. |
| IV C | “This motivates…full-chain calibrated comparisons” | **Merged into:** final sentence. |
| VI A | Holm rule, CP requirement, batch size, cap, and stopping rule | **Merged into:** first replacement paragraph; no rule removed. |
| VI A | “every input…fixed before any production…” | **Merged into:** preregistration statement. |
| VI A | “Two parts…informed by the data” | **Dropped:** superseded by an explicit paragraph identifying all consolidated choices. |
| VI A | “reviewers…had seen descriptive per-cell residuals” | **Merged into:** consolidated post hoc paragraph. |
| VI A | “bounded extension…outputs…observed p values” | **Merged into:** same paragraph. |
| VI A | “changed no statistic…p values remain valid…” | **Merged into:** same paragraph, retaining the ensemble-size qualification. |
| VI A | Independent recomputation and specification references | **Merged into:** first paragraph. |
| IV A consequential edit | “This choice…was made after both comparisons were known” | **Merged into:** consolidated VI A post hoc paragraph. |
| VI C consequential edit | Scan “specified before it ran…after the decisions” | **Merged into:** consolidated VI A paragraph; scan remains outside the decision rule in VI C. |
| VI C consequential edit | “with the recovered pseudo-experiments…included” | **Merged into:** complete submitted calibration ensemble; recovery history **moved to note**. |
| VI C consequential edit | Projection comparison “specified…after…outcomes were known” | **Merged into:** consolidated VI A paragraph. |
| VI C consequential edit | “global assessments of the five specified generator versions” | **Merged into:** global assessments of the hybrid nulls constructed from those versions. |
| VI C consequential edit | Power toys “the rest having been lost to time limits” | **Moved to note:** retained subset sizes remain in the paper. |
| VI B(i) | “Within each fine-grid cell…Tune v1's shapes” | **Merged into:** explicit grid and subgrid-shape definition. |
| VI B(i) | “convergence…has not been shown” | **Merged into:** direct nonconvergence-demonstration statement. |
| VI B(i) | Last-refinement relative size and potentially material residual | **Merged into:** quantitative \(L_2\) statement. |
| VI B(i) | “Before any result was known…the size…set…” | **Merged into:** VI A fixation statement and VI B decision-shift definition. |
| VI B(i) | “at a rate taken from the review…no calculation is recorded” | **Merged into:** numerical proxy-metric rate with the provenance limitation retained. |
| VI B(i) | “one to three times…central estimate…upper end” | **Merged into:** decision and robustness shift explanation. |
| VI B(i) | “measured \(L_2\) ratios also allow slower convergence” | **Merged into:** explicit slower-convergence sentence. |
| VI B(i) | Conditional transfer from hybrid null to \(G\) | **Merged into:** same directional bound, stated directly. |
| VI B(i) | “rejections still determined…about \(5.2\)” | **Merged into:** existing VI C numerical scan results; VI B retains its interpretive limitation. |
| VI C recovery paragraph | “Batch-job time limits interrupted or prevented…” | **Moved to note:** operational history and lost-count macros. |
| VI C recovery paragraph | “Had every interrupted one exceeded…no test…” | **Moved to note:** superseded missing-outcome sensitivity, resolved by complete accounting. |
| VI C recovery paragraph | “reran…after the decisions…procedure fixed…reviewed” | **Moved to note:** recovery chronology and procedure. |
| VI C recovery paragraph | “first reproduced 16…exactly” | **Moved to note:** recovery implementation verification. |
| VI C recovery paragraph | “None…reaches…Every submitted…observed…” | **Merged into:** final complete-ensemble result. |
| VI C recovery paragraph | “no assignment of the lost outcomes changes…” | **Merged into:** actual complete-ensemble decision invariance; there are no remaining unobserved calibration outcomes. |
| VI C recovery paragraph | “closest approach…4.6…868.6” | **Merged into:** retained minimum-margin sentence. |
| VII | “We have built a covariance…and formed its…projection” | **Merged into:** present covariance and projection status. |
| VII | “has not met the criteria…set in advance” | **Merged into:** direct criteria-failure statement. |
| VII | “bound fixed before…can no longer be applied” | **Merged into:** explicit unavailable advance-bound condition. |
| VII | “exception…limited to this one covariance” | **Merged into:** covariance-specific use restriction and note citation. |
| VII | “quote no…significance, because…random seed” | **Merged into:** no-significance statement followed by quantitative seed failure. |
| VII | Two additional covariances, measured shift, and limit | **Merged into:** seed-stability paragraph. |
| VII | Ensemble-size movements and declining noise floor | **Merged into:** compact numerical comparison; every macro retained. |
| VII | One seed pair, nested subsets, unmeasured larger ensembles | **Merged into:** explicit scope limitation. |
| VII | Five pinned bands, trace contribution, unknown sensitivity | **Merged into:** final three sentences of seed paragraph. |
| VII | “A separate study looked for a definition…” | **Merged into:** three explicitly defined reporting choices. |
| VII | “None…could meet…rules and computing budget” | **Merged into:** numerical target comparison and scoped negative conclusion. |
| VII | “fallback…component alone exceeded…” | **Merged into:** named 39-cell fallback and explicit median comparison. |
| VII | “joint tests…came from the same study” | **Moved to note:** analysis chronology. |
| VII | “different route…provide no new measurement uncertainty” | **Merged into:** final hybrid-null inference sentence. |
| VIII | “reproduces the published two-dimensional result” | **Merged into:** narrower integrated-agreement result and reference to binwise validation. |
| VIII | “The results are of three kinds” and following classification | **Merged into:** two concise result paragraphs. |
| VIII | Higher-dimensional descriptive-only scope | **Merged into:** explicit central-values-only, no-significance statement. |
| VIII | “conditional on six stated conditions…no new measurement uncertainty” | **Merged into:** conditional hybrid-null conclusion and VII's explicit uncertainty distinction. |
| VIII | Marginal agreement and three-/four-observable closure | **Merged into:** Introduction and IV C; not repeated in conclusion. |
| VIII | Background bias and unbinned refinement | **Merged into:** detailed IV C result; conclusion retains background-bias finding. |
| VIII | Persistent generator-sized regularization bias | **Merged into:** incomplete-recovery conclusion and quantified IV C study. |
| VIII | “quoted…statistical block has had no coverage test” | **Merged into:** IV B's single explicit coverage statement. |
| VIII | “learner…one unit of chi2/ndf” | **Merged into:** unchanged numerical IV A comparison, referenced from conclusion. |
| VIII | “measured model dependence…useful precision” | **Merged into:** numerical VII result and scoped conclusion about considered definitions. |
| VIII | “practical checks for future…unfolding” | **Dropped:** generic implication adds no substantive result. |
| VIII | Calibration “with an estimator that retains substantial model dependence” | **Merged into:** IV C recovery results and VI A noncentral calibration explanation. |
| VIII | “recovering every lost pseudo-experiment changes no decision” | **Merged into:** VI C final ensemble-accounting result. |
| VIII | Matched projections and lack of additional discrimination | **Merged into:** final conclusion paragraph. |
| VIII | Response and fine-grid requirements | **Merged into:** final sentence. |
| Data availability | Inputs, license, earlier production, file count and checksums | **Merged into:** first paragraph. |
| Data availability | Candidate size, local preparation, nondeposit, dependencies | **Merged into:** first paragraph; all availability restrictions retained. |
| Data availability | Recompute tests, recovery, projections, \(L_2\), figures, summaries | **Merged into:** explicit package-scope paragraph. |
| Data availability | Empty-directory reproduction | **Merged into:** narrowly scoped replay statement. |
| Data availability | “assembled before…changed to LightGBM” | **Moved to note:** release chronology. |
| Data availability | “carries the exact-split curve” | **Merged into:** explicit current package limitation. |
| Data availability | Figure 1 separately regenerated using extended plotting code | **Merged into:** current Figure 1 provenance; code-extension history **moved to note**. |
| Data availability | Multiplier-scan exception | **Merged into:** separate reproduction-route sentence. |
| Data availability | “other quoted numbers cannot be recomputed from this package” | **Merged into:** explicit additional-input requirement. |
| Data availability | Release appendix “does and does not reproduce” | **Merged into:** reproduction-scope reference. |
| All units | `%` drafting comments, review dispositions, receipts, and implementation chronology | **Moved to note:** supporting analysis record; none is needed as manuscript source commentary. |

The unchanged Sec. IV A retains `\chiPaper`—the supplied 2.65—and its learner dependence. The unchanged hadronic-response subsection retains the nonrejection of GENIE CV by the muon projection, its two \(p\)-value macros, and the limitations of the recoil sensitivity study.

#### C. Numbers added

“Added” includes an existing manuscript number newly placed in a rewritten unit. Repeated appearances are grouped. The supplied Markdown has no numbered lines, so the source column identifies its exact heading and quoted source line.

| Added number or numerical statement | Placement | Source line in `numbers-available.md` |
|---|---|---|
| About one percent; `\ratioTot` | Abstract; Conclusions | **Paper F5, (1):** “Ratio…1.011, from the integral ratio 1.0112”; **(2):** `\ratioTot`, `values.tex:48`. |
| About 10–13% per coarse cell | Abstract | **Paper F4, (1):** “prior dependence is ≈ 10–13% per coarse joint cell”; record `:144`. |
| 13.4% model-component median | Introduction; VII | **Paper F4, (1):** “median 12.0%, 9.6% and 13.4%”; record table `:127–131`, RD3 `:131`. |
| 10% target median total 68% half-width | Introduction; VII | **Paper F4, (1), T1:** “median total 68% half-width ≤ 10%”; record `:133`. |
| 9.7% median residual | IV C | **Paper F12, (1):** “Median residual: 9.7%”; record `:75–82`; also **Primer F-new-1, (1)–(2)**. |
| 400 pseudo-experiments per truth | IV C | **Paper Sec. IV C, (1):** “400 pseudo-experiments per truth”; record `:3–6`, `:30–36`. |
| 153 reported quantities | IV C | **Paper Sec. IV C, (1):** “153 reported functionals”; same source. |
| 51 failing 68% intervals under tilt | IV C | **Paper Sec. IV C, (1), tilt row:** “51”; record `:41–48`. |
| Minimum tilt coverage 0.06 | IV C | **Paper Sec. IV C, (1), tilt row:** “0.060 / 0.288”; record `:30–36`, `:41–48`. |
| 42 failing 95% intervals under tilt | IV C | **Paper Sec. IV C, (1), tilt row:** “42”; same source. |
| Two failing 95% intervals at nominal truth | IV C | **Paper Sec. IV C, (1), nominal row:** “2 (EW36, J161)”; same source. |
| Minimum nominal-truth 95% coverage 0.85 | IV C | **Paper Sec. IV C, (1), nominal row:** “0.570 / 0.850”; same source. |
| Failure thresholds 0.66 and 0.94 | IV C | **Paper Sec. IV C, (1):** “upper confidence bound…< 0.66 at 68% or < 0.94 at 95%”. |
| Per-comparison level \(0.05/459\) | IV C | **Paper Sec. IV C, (1):** “at a per-comparison level of 0.05/459”. |
| Fine-grid dimensions \(14\times16\times7\times7\times6\) | VI B(i) | **Paper F7, (1):** grid dimensions; **(2):** `s5p_stage1_inspect.py:38–44` and audit `mapping-notes-C.md:25`. Identification should also be stated in the companion note. |
| `\jtMoneWnormMin`–`\jtMoneWnormMax` per halving | VI B(i) | **Paper F6, (1)–(2):** “0.45–0.76 per halving”; macros `values_inference.tex:38–39`. Unrecorded calculation remains disclosed. |
| 109, 27, and 39 reporting cells | VII | **Paper F4, (1):** “RD1, the 109…RD2, 27…RD3, the 39…”; record `:127–131`. |
| 12.0% and 9.6% model-component medians | VII | **Paper F4, (1):** median list; record `:127–131`. |
| Five generator-sized departures | VII | **Paper F4, (1):** “largest shift over five generator-sized truth departures”. |
| At least 11.0% with 1.4% normalization | VII | **Paper F4, (1), T1:** “RD2 fails once the flat 1.4% normalization is added: its median is ≥ 11.0%”. |

The completeness sentence adds a **recipe fact**, not a measured number: **Paper F17, (1)–(2)** establishes use of un-resampled completeness by design and code, without a measured check on the quoted replica products.

#### D. Word counts

These are **manual estimates**, counting prose and numerical expressions while excluding comments, LaTeX commands, and headings. They are not machine-verified exact counts.

| Scope | Old | New |
|---|---:|---:|
| Abstract | approximately 230 | approximately 150 |
| Requested replacement units, combined | approximately 3,500 | approximately 2,600 |

The combined estimate excludes the unchanged surrounding text and the small consequential edits listed separately above.

---

## P13. X2 Gemini 3.8 Flash: primer rewrite (sha256 `4a1447242a8a21a5…`)

##### A. LaTeX Sources

###### New `primer_abstract.tex`

```latex
\begin{abstract}
This is a short, jargon-light guide to a measurement of neutrino interactions in the MINERvA detector and to the machine-learning method (``unbinned OmniFold'') used to unfold them. The analysis reproduces a published two-variable cross section within about one percent overall, with uncertainties comparable to the original measurement. Extending the method simultaneously to up to five kinematic variables without binning---a first at MINERvA---recovers an established low-recoil discrepancy and reveals a localized excess over MINERvA's tuned simulation at high available energy and high hadronic mass. A joint test across five dimensions rejects five widely used neutrino event generators under stated assumptions. Because the multi-quantity results exhibit sensitivity to the starting simulation and the learner's random seed, and because statistical intervals failed a pre-registered coverage test, higher-dimensional distributions are reported as central values only. Finally, an extended signal definition explores wider kinematics while separating detector-supported data from simulation-dominated extrapolation.
\end{abstract}
```

###### New Section 3 and Section 4 for `primer_body.tex`

*(Note: Sections 1–2 are retained without changes.)*

```latex
\section{What we found}

Our results span several distinct measurements and checks, each with its own level of validation. The rest of this section describes each in detail; here is what was found:
\begin{itemize}
\item \textbf{A published result, reproduced.} The two-variable central value reproduces MINERvA's published measurement to within about one percent overall, with independently constructed uncertainties comparable to the published ones. A correlated shape difference remains, and the quoted statistical error bars have had no coverage test.
\item \textbf{More quantities at once.} Unbinned unfolding simultaneously across up to five quantities passes nominal recovery checks, but is reported as central values only. Tests with changed simulated truth show biases (in a test of generator size, typical cells come back about \SI{10}{\percent} off) that are not included in the quoted uncertainty, and five-dimensional error bars failed pre-registered coverage criteria.
% 9.7 % median: sec_5d.tex:73; OUTCOME-20260925-s5n-stage1-development-fail.md:76
\item \textbf{Known and new features in the data.} In these multi-variable central values, all tested simulations fall short of the data at low available energy, recovering an established low-recoil discrepancy. Adding a two-nucleon process fills part of the gap. In addition, an excess over MINERvA's tuned simulation is concentrated in one corner: high available energy and high hadronic mass.
\item \textbf{A joint test of five simulations.} Under stated modelling assumptions, each of five widely used simulations is rejected at a combined error level of five percent, both overall and in shape alone. This is an inference testing the simulations, not a new cross-section measurement.
\item \textbf{Point-cloud unfolding with a neural network.} Machine learning directly on low-level detector hits demonstrates end-to-end unbinned unfolding on raw energy deposits. It remains method development: no design met every pre-registered requirement, and it contributes no cross section or error bar.
\item \textbf{A wider signal definition.} Relaxing published muon kinematic cuts yields a preliminary total cross section, with detector-supported regions cleanly separated from simulation-dominated extrapolation.
\end{itemize}

\subsection*{First, a trust check: reproduce a known result}

Before trusting a new method, one must show it reproduces an established measurement. MINERvA already published this muon cross section using the traditional method. Our machine-learning result agrees with it closely: the overall interaction rate matches to about one percent (ratio $\ratioTot$), and \SI{\binsTen}{\percent} of the individual measurement cells agree within ten percent. Judged with the published correlations between cells, a shape difference remains.

Just as important, our \emph{uncertainties}---worked out independently of the published analysis---come out close in size to the published ones (\SI{\uqMedian}{\percent} versus \SI{\uqPaper}{\percent} typical). Ours are a little smaller in the typical cell, partly because our uncertainty on the beam's neutrino flux comes out below the published one, for a reason not yet established; both use MINERvA's constraint from neutrino--electron scattering and inverse muon decay. For the uncertainty on the overall interaction rate the comparison goes the other way: \SI{\uqIntegral}{\percent} for ours against \SI{\uqPaperIntegral}{\percent} published.

Two qualifications apply to this reproduction. First, two software implementations of the tree learner give answers that differ by about one percent in a typical cell, and the size of the remaining shape difference depends on which one is used. We quote the faster one, because every ingredient of the error bars was computed with it; we originally quoted the slower one. We made this choice post hoc, after both comparisons with the published result were known.

Second, the error budget has known limits. An earlier version had construction errors that were corrected in a rebuild~\cite{TwoDFollowup2026}. Some effects remain omitted from the budget: an approximation in how events that fail reconstruction are weighted, the difference between the two implementations of the tree learner, and dependence on the unfolding model. We make no claim that these intervals cover truth across independent simulation samples. Furthermore, when the statistical part of an earlier version of these error bars was tested across simulated pseudo-experiments, two-standard-deviation bars contained the truth only \SI{\covTwoDCTwoPct}{\percent} of the time instead of \SI{95}{\percent}, undercovering in cells with large forward or sideways momentum. The statistical error bars now quoted were rebuilt at the central-value settings, but they have had no coverage test. The published measurement is unaffected by these checks.

\begin{figure}[H]
  \centering
  \includegraphics[width=0.62\textwidth]{MEFHC_5iter_fig13}
  \caption{The unfolded muon cross section as a function of the two momentum components. This reproduces a published MINERvA measurement, but was produced by the machine-learning method described above. The red curve is MINERvA's tuned simulation (Tune~v1, built on GENIE~2.12.6), the starting point of the unfolding; the untuned GENIE~2.12.10 of Fig.~\ref{fig:primergen} is a different simulation.}
\end{figure}

\subsection*{Then, measure more at once --- and rediscover known physics}

With the central value reproduced and its uncertainties comparable to published values, we used OmniFold's defining ability and unfolded several quantities \emph{simultaneously} and \emph{without binning}---a first at MINERvA, where earlier multi-quantity results used binned methods: the muon momentum ($\pPar, \pT$) together with the available energy ($\Eavail$, roughly the energy released by the struck nucleus), the momentum transfer ($q_{3}$), and the hadronic mass ($W$). Each richer measurement, when collapsed back down, agrees with the simpler one in overall normalization.

These five coordinates do not represent five completely independent measurements. Reconstructed $q_{3}$ and $W$ reuse the muon kinematics and the recoil-energy estimate. Available energy omits energy carried by neutrons at truth level. Adding coordinates helps the learner capture correlations, even where it does not open a new independent physical direction.

The first physics payoff appears in the available energy. When data are compared to four simulation predictions, all four fall short of the data at low available energy, between about $0.1$ and $0.4$~GeV (Fig.~\ref{fig:primergen}, left). This reproduces an established low-recoil discrepancy that neutrino simulations have historically struggled to describe. Adding a two-nucleon interaction process (``2p2h'') fills part of the gap. Pion-rescattering variations have a much smaller effect, though related MINERvA measurements show that proton and pion rescattering also contribute~\cite{MINERvA:2026qeleme}. These comparisons support a two-nucleon contribution without uniquely establishing its mechanism. Where MINERvA has a dedicated published measurement of this region, our central values lie \SI{9.2}{\percent} and \SI{6.3}{\percent} above it on the finest shared cell edges; because that measurement defines true available energy more broadly, this comparison is qualitative.

\begin{figure}[H]
  \centering
  \includegraphics[width=0.99\textwidth]{eavailW_band}
  \caption{The unfolded central values (black points) compared to four tested simulation predictions---GENIE's untuned central configuration (version 2.12.10), GENIE with the two-nucleon process added, NuWro (21.09), and GiBUU (2019); the GENIE and NuWro predictions were rebuilt with a correctly sampled beam spectrum. \emph{Left:} available energy; all four fall below data at low available energy ($0.1$--$0.4$~GeV), recovering the known low-recoil shortfall with a different unfolding method. \emph{Right:} hadronic mass; all four sit below data at high hadronic mass. \textbf{Central values only.} No uncertainty band is drawn and no significance is assigned, for reasons detailed under ``Limits that matter most'' below.}
  \label{fig:primergen}
\end{figure}

\subsection*{A new puzzle for the tuned simulation}

Adding the hadronic-mass axis $W$ lets us examine where MINERvA's tuned simulation (Tune~v1), which already incorporates an enhanced two-nucleon process, still misses. The remaining discrepancy concentrates in a specific corner: high available energy \emph{and} high $W$ (Fig.~\ref{fig:primerjoint})---the deep-inelastic scattering region where the neutrino shatters the target nucleon.

About two thirds of the extra cross section, summed over cells, lies at high available energy, most of it at high $W$; about a fifth sits in the single widest corner cell.
% shares 67 %, 83 %, 22 %: note sec_eavailw.tex:49-53; paper_body.tex:571-574.
Cell by cell, the data in that corner are \SIrange{12}{30}{\percent} above the tuned simulation, about as much as at the lowest $W$ (\SIrange{23}{31}{\percent}). The four other simulations also fall short there: GENIE (with and without 2p2h) and NuWro fall short by \SIrange{14}{16}{\percent} in the corner and \SIrange{7}{15}{\percent} overall, meaning the corner is not unique for them. GiBUU falls further behind in the corner (\SI{61}{\percent} below data in the corner versus \SI{39}{\percent} overall), primarily because its simulation omitted neutrinos above \SI{20}{GeV}, which account for about \SI{15}{\percent} of the corner rate.

These distributions are reported as central values only; no statistical significance is assigned. Starting the learner from different random seeds moves these central values by at most about \SI[round-mode=figures,round-precision=1]{\cvMoveOverSigmaMax}{\percent} of their own uncertainty; how far that shift could alter the corner's share was not separately measured.

\begin{figure}[H]
  \centering
  \includegraphics[width=0.95\textwidth]{paper_joint_localization}
  \caption{The unfolded data compared to the MINERvA-tuned GENIE simulation (Tune~v1) across the available-energy / hadronic-mass plane jointly. Both panels share a seven-by-six grid of cells with available-energy boundaries $0$, $0.1$, $0.2$, $0.4$, $0.8$, $1.5$, $3$, and $100$~GeV, and hadronic-mass boundaries $0$, $1.1$, $1.4$, $1.8$, $2.2$, $3$, and $100$~GeV. \emph{Left:} ratio of data to simulation. \emph{Right:} cell-integrated cross-section difference (data minus simulation in \si{cm^2/nucleon}). The excess concentrates at high available energy and high hadronic mass. Central values only; no uncertainty is drawn and no significance is assigned. The learner's random seed moves these central values by at most about \SI[round-mode=figures,round-precision=1]{\cvMoveOverSigmaMax}{\percent} of their uncertainty.}
  \label{fig:primerjoint}
\end{figure}

\subsection*{Limits that matter most on the multi-quantity results}

We evaluated an uncertainty for the multi-quantity results, but it did not satisfy the validation criteria established in advance and is used only under a documented exception. Higher-dimensional results are therefore presented strictly as central values without claimed statistical significance. The three limits that matter most are:

\begin{enumerate}
\item \textbf{Unfolding-model bias and dependence on truth.} When simulated pseudo-data are generated with a modified distribution taken from an alternative generator, the unfolding follows the change only partly: typical $(\Eavail,W)$ cells return about \SI{10}{\percent} off (a median residual of \SI{9.7}{\percent}), rising to as much as \SI{74}{\percent} in the highest-$W$ cells for a deterministic variant of the estimator. For the fallback reporting definition (the 39 supported $(\Eavail,W)$ cells), the bounded model-dependence component alone has a median of \SI{13.4}{\percent}, exceeding our pre-set target of a \SI{10}{\percent} median half-width for the total 68\% interval. In addition, background subtraction leaves a bias of about \SI{4}{\percent} in the highest-$W$ cells (reduced below \SI{1}{\percent} with unbinned removal). Neither bias is included in the quoted uncertainty.
\item \textbf{Sensitivity to the learner's random seed.} Initializing the tree learner from a different random seed shifts the uncertainty on the $(\Eavail, W)$ projection by about \SI[round-mode=figures,round-precision=1]{\sprojMeasured}{\percent} (measured on test versions), exceeding the \SI{\sprojBound}{\percent} tolerance set in advance. This shift does not shrink when the number of simulated variations is increased, behaving as an intrinsic property of the learner rather than statistical noise. The same seed change moves multi-quantity central values by at most about \SI[round-mode=figures,round-precision=1]{\cvMoveOverSigmaMax}{\percent} of their uncertainty. Claiming statistical significance on top of this variation would overstate our precision.
\item \textbf{Failed coverage and unvalidated error bars.} In a direct coverage test of five-quantity statistical error bars on simulated experiments with an injected available-energy tilt, the method failed its pre-registered criteria: 51 of 153 reported cell and projection integrals exhibited coverage confidently below nominal, dropping as low as 0.06 for nominal 68\% intervals. Because the error bars have not demonstrated that they contain the truth at the stated rate, no coverage claim is made, and no error bands are drawn on multi-quantity figures.
\end{enumerate}

In addition, while muon detector variations were rebuilt end to end, the detector uncertainty model omits an uncertainty band for the calorimeter's response to hadronic recoil energy. Technical investigations into larger classifiers, longer training runs, and alternative binning are detailed in the companion analysis note; none resolved these limitations without introducing new tradeoffs or failing pre-registered stability criteria. None of these five-quantity limitations affects the two-dimensional trust check, which retains its independently constructed error budget.

\subsection*{A joint test of five simulations}

We also performed a hypothesis test asking whether five widely used simulations (MINERvA Tune~v1, GENIE with and without MEC, NuWro, and GiBUU) are statistically compatible with the five-dimensional data, both overall (rate and shape together) and in shape alone.

Each hypothesis sets the true cross section on a finite grid of cells to that generator's rate, with Tune~v1's shape inside each cell. Rather than assuming an asymptotic distribution for the test statistic, we evaluated 1,340 to 1,750 unfolded pseudo-experiments under each hypothesis. In each test, at most one pseudo-experiment looked as discrepant as the data. Consequently, all ten hypotheses (five simulations, tested overall and in shape) are rejected at a combined 5\% error level.

This test is an inference on the simulations under stated assumptions, not a new cross-section measurement with error bars:
\begin{itemize}
\item The test is evaluated on a grid; it does not resolve or bound possible errors from structure finer than the grid. A sensitivity scan shows that rejections become ambiguous if unmeasured sub-grid variations exceed several times the step between tested grid resolutions.
\item The detector uncertainty model includes no calorimetric response uncertainty for hadronic recoil energy.
\item Additional conditions detailed in the analysis note include interaction-model variations (such as event-weight clipping), calibration offsets between split samples, finite simulated generator sample sizes, and generator energy coverage.
\end{itemize}
In a post hoc check, GENIE's untuned configuration is not rejected when projected onto coarse muon variables alone, whereas its projection onto hadronic variables is rejected. Hadronic data thus contributes directly to the rejection, though the test does not establish added discrimination beyond all matched lower-dimensional projections. A simulation that is not rejected is not thereby confirmed as correct.

\subsection*{Point-cloud unfolding with a neural network (PET)}

To explore alternative event representations, we applied PET (a point-cloud transformer) directly to raw detector energy deposits rather than summary quantities. PET pairs reconstructed low-level recoil clusters with hadrons in the simulated true final state without using the muon. It demonstrates that unbinned unfolding can operate directly on low-level detector hits, serving as a recoil diagnostic and method cross-check; it contributes no cross section or error bar.

Extensive simulation studies improved PET's recovery of distorted truth distributions~\cite{PETImprovement2026,PETFinalDesign2026}. However, no design satisfied all pre-registered requirements: one failed point-estimate robustness criteria, while another failed interval coverage (its nominal 68\% intervals covered truth 90\% of the time overall, but dropped to 26\% in regions where the detector records few events)~\cite{PETIntervalDiagnosis2026}.

An exploratory simulation comparison between PET and the tree learner on identical events showed mixed performance across different injected distortions (Fig.~\ref{fig:primerpet})~\cite{PETGBDT2026}. Subsequent diagnoses identified underfitting at the detector level and weak extrapolation to missed events as key shortfalls in generator tests~\cite{PETGeneratorDiagnosis2026}. PET remains active method development; no PET uncertainty or point-cloud result is used for our reported cross sections.

\begin{figure}[H]
  \centering
  \includegraphics[width=0.90\textwidth]{pet_gbdt_paired_differences.pdf}
  \caption{Exploratory simulation comparison: gain in recovered fraction for each of the two best PET designs relative to the tree learner (GBDT) on the same events, at seven iterations. Positive indicates better recovery. E0 and E3 are opposite energy tilts; E1 separates acceptance regions; E4 tests proton content; E5 tests the joint energy--momentum-transfer distribution. Bars are unadjusted 95\% intervals for paired differences over 60 draws (E0, E1, E3) or 40 (E4, E5). Point-estimate comparisons only, conditional on simulated samples.}
  \label{fig:primerpet}
\end{figure}

\subsection*{Extending the signal definition}

The published signal definition excludes about one third of the simulated interaction rate through cuts on the true muon's angle and momentum. We evaluated relaxing these truth-level cuts while retaining the identical tracker interaction volume and reconstructed MINOS muon selection.

The preliminary central value for the extended cross section is $\sigma_{\mathrm{ext}}\approx \num[round-mode=figures,round-precision=2]{\fpsSigma}\text{ cm}^2/\text{nucleon}$ (Fig.~\ref{fig:primergen}). Crucially, only about \SI{6}{\percent} of the rate is a newly detector-supported measurement; about \SI{28}{\percent} lies in regions where detector efficiency is low or zero, representing a simulation-dependent extrapolation that must be interpreted separately.

\begin{figure}[H]
  \centering
  \includegraphics[width=0.99\textwidth]{fps_pilot_compare_MEFHC}
  \caption{The extended-fiducial study on the muon momentum grid ($p_T$ versus $p_\parallel$). Left: inside the published region (between black lines) the new result reproduces the original to better than one percent. Center: changing the starting simulation has a minor effect in accepted cells but a substantial effect in low-efficiency cells. Right: preliminary central value over the enlarged truth domain; detector-supported and prior-dominated regions must be interpreted separately.}
\end{figure}

\section{The takeaway}

Unbinned machine-learning unfolding reproduces a flagship MINERvA measurement to within about one percent overall and extends to many quantities simultaneously without the large response tables traditional binned methods require, though training, simulation, and uncertainty estimation become more demanding. Using this capability, this analysis:
\begin{itemize}
\item recovered an established low-recoil discrepancy with an unbinned machine-learning method,
\item identified a localized central-value excess over MINERvA's tuned simulation at high available energy and high hadronic mass,
\item rejected five widely used neutrino event generators at a combined five percent error level in a joint five-dimensional hypothesis test under stated conditions, and
\item mapped an extension of the signal definition beyond published muon kinematic limits, cleanly separating detector-supported data from simulation-dominated extrapolation.
\end{itemize}
The multi-quantity results are reported as central values only: their error bars have not met pre-registered validation criteria, exhibiting an unfolding-model dependence of about \SI{10}{\percent} (and up to \SI{74}{\percent} at high $W$), a sensitivity to the learner's random seed of about \SI{6}{\percent}, and unvalidated coverage.
```

---

##### B. Table of Removed or Compressed Sentences and Paragraphs

| Short Quote | Disposition |
|---|---|
| *"Its size depends on which of two implementations of the tree learner is used, and we chose which one to quote after both comparisons were known..."* | (merged into: Section 3, subsection *First, a trust check: reproduce a known result*) |
| *"That uncertainty has not met the requirements we set in advance, and it is used only under a documented exception to them, so their error bars have not been shown to be right..."* | (merged into: Section 3, subsection *Limits that matter most on the multi-quantity results*) |
| *"Neither feature is assigned a statistical significance. The learner's random seed also moves these central values... and how far that could shift... was not measured."* | (merged into: Section 3, subsection *A new puzzle for the tuned simulation*) |
| *"An assessment of the saved analysis outputs found errors in how an earlier version of the two-variable error budget was put together... Its set of systematic variations and the reference those variations are compared with now use the same truth inputs. A pion-model variation that appeared twice is counted once. The statistical fluctuations of the background simulation are propagated. And the detector variations that change which events are selected come from complete re-runs of the analysis."* | (moved to note/paper: companion note `sec_systematics.tex` and `\cite{TwoDFollowup2026}`; summary sentence retained) |
| *"The main cause of the shortfall was found and removed, and the statistical bars now quoted were built again, at the same learner settings as the central value."* | (moved to note/paper: companion note `sec_validation.tex`; plain sentence retained that quoted statistical bars lack a coverage test) |
| *"The natural hope is that this is just statistical noise from having a finite number of simulated variations... We checked over the range we have, and it does not shrink: the shift is the same size whether we use a quarter, a half, or all of our variations, while genuine statistical noise... falls by a factor of nearly three over the same step."* | (moved to note/paper: companion note `sec_5d.tex`; core point that shift behaves as learner property retained) |
| *"First, five of the forty-five uncertainty components are built with a fixed seed that this change cannot reach, so the shift is the effect of the other forty, and we have not measured which way those five would move it."* | (moved to note/paper: companion note `sec_5d.tex`) |
| *"Five of them describe effects that move a muon's measured momentum or angle, and for those we rebuilt the simulation end to end... Four others --- the efficiency of MINOS for the muon, and three describing how hadrons interact in the detector --- are applied instead by reweighting..."* | (dropped: technical implementation details not needed by primer reader; absence of calorimetric response band retained) |
| *"A follow-up study looked inside the unfolding to find out why. The tested changes to the number of iterations and to the learner's capacity do not remove the bias... The study did find the source of the remaining background bias: an auxiliary classifier used in the background removal was too simple, and a larger one removes the bias. But the study also found that the result on the real data shifts by up to a few times its statistical uncertainty when the inputs are rounded differently... A later study found that the bootstrap of the version of the method with the larger classifier... already carries this rounding variability. That finding is limited to that version's own bootstrap..."* | (moved to note/paper: companion note `sec_5d.tex` and audit records; compressed into ranked limits) |
| *"Three possible remedies each have a limit. Longer runs sometimes improve recovery and sometimes leave a persistent residual... Combining cells changes what is measured. Changing the starting model gives no guaranteed error bound."* | (dropped: exploratory narrative; core point of unvalidated error bars retained in ranked limits) |
| *"Some pseudo-experiments were lost to computing time limits. Rerunning exactly those seeds recovered them, in a check reported separately from the result: none looked as discrepant as the data, though in one robustness variant one came close."* | (moved to note/paper: companion note `sec_joint.tex`) |
| `\begin{itemize} \item structure finer than the grid... \item the detector-uncertainty model as stated... \item the interaction-model variations... \item a calibration shift... \item the range of neutrino energies... \item the finite size of each generator's simulated sample. \end{itemize}` | (moved to note/paper: companion note `sec_joint.tex`; compressed into narrative bullet list highlighting calorimetric response and sub-grid limits) |
| *"We scaled the last measured change from refining the grid by a sensitivity multiplier $\kappa$, which counts multiples of that shift; it is not a confidence level. In the tests as fixed in advance, the first decision stops being a clear-cut (determinate) rejection near $\kappa=5.26$, or $5.17$ when the recovered pseudo-experiments are included. At that point the decision becomes ambiguous..."* | (moved to note/paper: companion note `sec_joint.tex`; compressed into plain sentence on sensitivity scan) |
| *"Completed simulation studies then improved how well PET recovers truth distributions that were deliberately changed... But in the first of these studies, none of the designs tried, each fixed in advance at ten iterations, met the requirements for going on to a coverage test. A later study to choose a final design raised the recovered fraction... to about 90% and 86% for its two best designs, against 31% for the original PET~\cite{PETImprovement2026,PETFinalDesign2026}."* | (moved to note/paper: companion note `sec_pet.tex` and `\cite{PETImprovement2026,PETFinalDesign2026}`) |
| *"One of the two best designs failed a robustness threshold under the rule, fixed in advance, that judges the point estimate. The statistical comparison did not establish which of the two was more robust, and this design's coverage was never measured. The other passed the rules for the point estimate but failed the test of its intervals... yet only 26% of the time in regions where the detector records only a small fraction of the true events (low acceptance); there, intervals meant for 95% contained it 79% of the time..."* | (merged into: Section 3, subsection *Point-cloud unfolding with a neural network (PET)*; compressed into plain sentences on robustness and coverage failure) |
| *"Our diagnosis of the saved outputs of these studies gives a partial explanation~\cite{PETIntervalDiagnosis2026}. The point checks used one fit, while the intervals surrounded an average of six fits, each to a randomly resampled copy of the events (bootstrap fits). If the sources of variation simply add (an additive variance model), much of the fit-to-fit variation averages away in that average... dividing the width by the square root of six is not a validated repair..."* | (moved to note/paper: companion note `sec_pet.tex` and `\cite{PETIntervalDiagnosis2026}`) |
| *"Which learner does better depends on the test: the tree learner does better on all three tests that reweight to other generator models and on the narrow energy bump, while the gap between them on the proton-content test shrinks as the tree learner runs more iterations. In development tests a binned method already matches PET on the one-dimensional tilt... The tree learner in this comparison is a separate configuration... All of these results hold only for the study's finite simulated samples and their size."* | (moved to note/paper: companion note `sec_pet.tex` and `\cite{PETGBDT2026}`) |
| *"For the three generator-model tests, a separate diagnosis of the saved outputs finds two shortfalls in PET: it underfits at the detector-level step, and it extrapolates weakly to events the detector missed~\cite{PETGeneratorDiagnosis2026}. Applying the exact weights that define each distortion recovers the changes well... PET already receives the reconstructed muon and the summary-quantity inputs; the effect of adding the tree learner's summary truth-level inputs is untested..."* | (moved to note/paper: companion note `sec_pet.tex` and `\cite{PETGeneratorDiagnosis2026}`) |

---

##### C. Table of Numbers Added

| Added Number / Phrase | Source Line in `numbers-available.md` | Location in New Text |
|---|---|---|
| `\sprojMeasured` rounded to "about 6\,\%" via `\SI[round-mode=figures,round-precision=1]{\sprojMeasured}{\percent}` | Primer F7 (`numbers-available.md:189-224`, `values.tex:407`) | Section 3, *Limits that matter most* item 2 |
| `\cvMoveOverSigmaMax` rounded to "at most about 6\,\% of their uncertainty" via `\SI[round-mode=figures,round-precision=1]{\cvMoveOverSigmaMax}{\percent}` | Primer F7 (`numbers-available.md:193-224`, `values.tex:458`) | Section 3, *A new puzzle* body and Fig.~\ref{fig:primerjoint} caption; *Limits that matter most* item 2 |
| `\fpsSigma` rounded to $\sigma_{\mathrm{ext}}\approx \num[round-mode=figures,round-precision=2]{\fpsSigma}\text{ cm}^2/\text{nucleon}$ ($\approx 4.5\times 10^{-38}$) | Primer F7 (`numbers-available.md:197-224`, `values.tex:273`) | Section 3, *Extending the signal definition* |
| Changed-truth bias: "typical cells come back about \SI{10}{\percent} off" | Primer F-new-1 (`numbers-available.md:231-255`, `sec_5d.tex:73-74`) | Section 3 overview list item 2; Section 4 takeaway |
| Changed-truth bias: median residual \SI{9.7}{\percent}, rising to up to \SI{74}{\percent} at high $W$ for deterministic variant | Primer F-new-1 (`numbers-available.md:231-255`), Paper F12 (`numbers-available.md:129-152`) | Section 3, *Limits that matter most* item 1 |
| Unfolding model-dependence component: median \SI{13.4}{\percent} vs \SI{10}{\percent} total half-width target (fallback definition) | Paper F4 (`numbers-available.md:15-68`, `sec_5d.tex:211-221`) | Section 3, *Limits that matter most* item 1 |
| 5D coverage test failure: 51 of 153 functionals futile at 68\%, coverage as low as 0.06 | Paper IV C coverage test (`numbers-available.md:175-188`) | Section 3, *Limits that matter most* item 3 |
| Corner excess over Tune v1 shares: ~two thirds (67\%) at $E_{\mathrm{avail}} \ge 0.8\text{ GeV}$, 83\% of that at $W \ge 1.8\text{ GeV}$, and ~a fifth (22\%) in single catch cell | Primer F-new-2 (`numbers-available.md:261-294`, `sec_eavailw.tex:49-53`) | Section 3, *A new puzzle for the tuned simulation* |
| Red curve in Fig. 2 caption: "MINERvA's tuned simulation (Tune~v1, built on GENIE~2.12.6)" | Primer F-new-8 (`numbers-available.md:299-318`, `paper_body.tex:110-111`) | Section 3, Fig. 2 caption |

---

##### D. Word Counts

| Document Section | Old Word Count | New Word Count | Notes |
|---|---|---|---|
| **Abstract** | 122 words | 146 words | Exactly on target for the ~150-word budget; adds joint test, multi-quantity central-value status, and corner excess. |
| **Sections 3–4** | ~2,295 words | ~1,680 words | Net reduction of over 600 words; cuts extensive chronology, diagnostic derivations, and defect catalogs while introducing ranked limits and requested numbers. |

---

## P14. X2 GPT-6.1-sol: primer rewrite (sha256 `aaeef1345c19f883…`)

A. Replacement LaTeX

Sections 1–2 are unchanged. The replacements use the existing macros, packages and bibliography keys.

```latex
\section{What we found}

\subsection*{Reproducing the published muon measurement}

OmniFold closely reproduces MINERvA's published two-variable cross section:
the overall interaction rate agrees to about one percent
(ratio $\ratioTot$), and \SI{\binsTen}{\percent} of the measurement cells
agree within ten percent. A shape difference remains when the published
correlations between cells are taken into account.

The independently constructed uncertainties are also close in size:
\SI{\uqMedian}{\percent} versus \SI{\uqPaper}{\percent} in a typical cell.
For the overall rate, ours is \SI{\uqIntegral}{\percent}, compared with
the published \SI{\uqPaperIntegral}{\percent}. Similar sizes do not
establish that the error bars contain the truth as often as stated.

Two qualifications matter here. Two implementations of the tree learner
differ by about one percent in a typical cell, and the remaining shape
difference depends on the implementation. We chose the faster one after
both comparisons with the published result were known, because the error
budget was built with it. Also, the quoted statistical error bars have
had no coverage test. An earlier statistical band contained the truth
within two-standard-deviation bars \SI{\covTwoDCTwoPct}{\percent} of the
time, rather than \SI{95}{\percent}, with shortfalls concentrated at large
forward or sideways momentum. Its main defect was corrected, but that
test does not validate the statistical bars now quoted.

The rebuilt error budget and its construction are documented
separately~\cite{TwoDFollowup2026}. It excludes an approximation in the
weighting of events that fail reconstruction, the difference between
learner implementations, and dependence on the unfolding model. The
flux uncertainty is smaller than the published one for an unexplained
reason, although both use MINERvA's neutrino--electron scattering and
inverse-muon-decay constraints. We make no coverage claim for this budget;
testing it across independent samples needs new simulation and validated
model variations.

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.62\textwidth]{MEFHC_5iter_fig13}
  \caption{The unfolded cross section in the two muon-momentum
  components, compared with the published MINERvA measurement.
  The red curve is MINERvA's tuned simulation, Tune~v1 built on
  GENIE~2.12.6, which supplies the unfolding's starting prediction.
  The untuned GENIE~2.12.10 in Fig.~\ref{fig:primergen} is a different
  simulation.}
\end{figure}

\subsection*{More quantities: a known shortfall and a localized excess}

We then unfolded three to five quantities simultaneously and without
binning --- a first at MINERvA for \emph{unbinned unfolding}, rather than
for measuring several quantities together. The inputs combine the two
muon-momentum components with available energy ($\Eavail$), momentum
transfer ($q_{3}$), and hadronic mass ($W$). Collapsing each richer result
back to fewer quantities preserves the simpler result's overall
normalization.

These are five coordinates, not five demonstrated independent pieces
of information: reconstructed $q_{3}$ and $W$ reuse the muon motion and
the same recoil-energy estimate. Available energy is distinct and,
at truth level, omits energy carried by neutrons. The three- to
five-dimensional results below are \textbf{central values only}.
They pass particular recovery checks, but their error bars have not
been shown reliable.

All four tested simulation predictions fall below the data at available
energies of about $0.1$--$0.4$~GeV
(Fig.~\ref{fig:primergen}). This resembles the established low-recoil
discrepancy, recovered here with a different unfolding method. Adding
a two-nucleon interaction process, called 2p2h, fills part of the gap.
The two tested pion-rescattering variations have smaller effects, but
they do not exclude other changes to particle motion inside the nucleus.
Related MINERvA measurements show why proton and pion rescattering also
matter~\cite{MINERvA:2026qeleme}. These comparisons support a two-nucleon
contribution without uniquely identifying the cause.

Our central values are \SI{9.2}{\percent} and \SI{6.3}{\percent} above
MINERvA's dedicated measurement on the finest shared grid. That
measurement uses a broader truth definition of available energy, so
these percentages do not provide a quantitative comparison of the
same cross section.

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.99\textwidth]{eavailW_band}
  \caption{Central values compared with untuned GENIE~2.12.10,
  GENIE with the two-nucleon process added, NuWro~21.09 and GiBUU~2019.
  The GENIE and NuWro predictions use a correctly sampled beam spectrum.
  Left: all four undershoot the data at low available energy.
  Right: all four undershoot at high hadronic mass; for the first three,
  the shortfall is similar to their overall shortfall.
  The two GENIE configurations are not independent predictions.
  No uncertainty band or statistical significance is assigned.}
  \label{fig:primergen}
\end{figure}

The comparison with MINERvA's tuned simulation reveals a more localized
feature. About \SI{67}{\percent} of the positive extra cross section,
summed over cells, lies at $\Eavail\geq\SI{0.8}{GeV}$; of that,
\SI{83}{\percent} lies at $W\geq\SI{1.8}{GeV}$. About
\SI{22}{\percent} of the total positive difference sits in the single
wide cell with $\Eavail>\SI{3}{GeV}$ and $W>\SI{3}{GeV}$.
These shares describe where the integrated excess lies, rather than
where the data-to-simulation ratio is largest. The joint map
(Fig.~\ref{fig:primerjoint}) locates this feature in a way that either
one-dimensional view alone cannot.
% Shares: sec_eavailw.tex:49-53; paper_body.tex:571-574.

The other simulations also undershoot in this corner. For the two GENIE
configurations and NuWro, the data are \SIrange{14}{16}{\percent} higher
there and \SIrange{7}{15}{\percent} higher overall, so the corner is
not a special shortfall for them. For GiBUU the corresponding differences
are \SI{61}{\percent} and \SI{39}{\percent}, largely because its sample
omits neutrinos above \SI{20}{GeV}. Those neutrinos supply about
\SI{15}{\percent} of the corner and \SI{7}{\percent} overall in the
other simulations. Supplying that contribution makes GiBUU's corner
shortfall similar to its overall one. No significance is assigned to
the localized excess, and its share has not been tested against changes
of the learner's random seed.

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.95\textwidth]{paper_joint_localization}
  \caption{Central-value comparison with MINERvA Tune~v1 across
  available energy and hadronic mass jointly.
  Left: data divided by simulation. Right: data minus simulation,
  integrated over each cell, in \si{cm^2/nucleon}.
  Both use seven available-energy cells with boundaries
  $0$, $0.1$, $0.2$, $0.4$, $0.8$, $1.5$, $3$, $100$~GeV,
  and six mass cells with boundaries
  $0$, $1.1$, $1.4$, $1.8$, $2.2$, $3$, $100$~GeV.
  Axes count cells from zero. The last cells collect values above
  $3$~GeV: their large areas help explain their prominent integrated
  differences, so both panels should be read together.
  No uncertainty or significance is assigned.}
  \label{fig:primerjoint}
\end{figure}

\subsection*{The three main limits on these findings}

The most consequential limits are incomplete recovery of changed truth,
unvalidated uncertainties, and numerical stability. They restrict the
interpretation of the multi-quantity central values; they do not replace
the independently constructed two-variable error budget.

\emph{First, recovery can be biased even in simulated experiments.}
For a deterministic variant of the central-value estimator, a deliberate
available-energy distortion leaves typical $(\Eavail,W)$ cells about
\SI{10}{\percent} from the known answer, with much larger residuals at
high $W$. The distortion came from a generator ratio containing a
wrongly sampled beam spectrum: it tests a chosen departure, rather than
measuring a generator difference. Other generator-based tests, using
the joint-test estimator, leave worst-cell residuals of
\SIrange{16}{31}{\percent}; about half the $(\Eavail,W)$ cells have
residuals smaller than the quoted uncertainty. These truth-dependent
biases are absent from that uncertainty, and tested changes to
iterations and learner capacity do not consistently remove them.
% About 10%: 9.7% median, sec_5d.tex:73;
% OUTCOME-20260925-s5n-stage1-development-fail.md:75-77.

Background removal adds another bias: about \SI{4}{\percent} in the
highest-$W$ cells in an end-to-end test. A finer removal reduces this
below \SI{0.3}{\percent}, while leaving about \SI{1}{\percent} in some
combined cells; a larger auxiliary classifier removes the remaining
bias in the follow-up study. These improvements have not changed the
reported five-quantity central value or uncertainty.

\emph{Second, the quoted uncertainty has not met the requirements set
in advance.} It is used under a documented exception, and neither it
nor its $(\Eavail,W)$ projection supports significance claims.
On two test versions of the projected uncertainty, changing one pair
of learner seeds shifts the uncertainty by about
\SI[round-mode=figures,round-precision=1]{\sprojMeasured}{\percent},
above the preset \SI{\sprojBound}{\percent} limit. This was not measured
on the quoted uncertainty. The shift did not shrink over the tested
subsets of simulated variations, unlike ordinary sampling noise;
that does not establish what a much larger ensemble would do.
Five of the forty-five uncertainty components were fixed against this
seed change, and their effect on the comparison is unmeasured.
The central values also move, by at most about
\SI[round-mode=figures,round-precision=1]{\cvMoveOverSigmaMax}{\percent}
of their quoted uncertainty. This is a different quantity from the
percentage shift of the uncertainty itself.

The one direct coverage test of five-quantity statistical intervals
used a variant of the method and failed. No coverage is claimed.
Longer runs have no established tradeoff between bias and variability;
combining cells changes the quantity measured; changing the starting
model supplies no guaranteed error bound. Detector variations account
for selection changes where needed, while other effects are applied
by reweighting. That bookkeeping does not establish that the included
hadronic-response variations are complete.

\emph{Third, a numerical stability test failed.} In the follow-up
configuration with the larger background classifier, rounding the
inputs differently shifts real-data results by up to a few statistical
uncertainties. Its own bootstrap includes that rounding variability,
but this finding does not transfer to the uncertainty quoted for the
five-quantity result or turn the failed stability test into a pass.
The companion paper and analysis note give the tests and their
configuration-specific limits.

\subsection*{A separate joint test rejects five hybrid hypotheses}

A separate inference asks whether five generator predictions are
compatible with the data, both in overall rate and shape together
and in shape alone. The generators are MINERvA Tune~v1, GENIE with and
without its two-nucleon MEC contribution, NuWro and GiBUU.
Each tested hypothesis is a \emph{hybrid}: it takes the generator's
rate in each truth-grid cell, but Tune~v1's distribution inside that
cell. The unfolding still learns from unbinned events; the grid
defines the hypotheses and the quantities tested.

About 1,340--1,750 simulated experiments were unfolded under each
generator hypothesis. In each test, at most one was as discrepant as
the data. All ten hypotheses --- five generators, each tested in two
ways --- are rejected at a combined \SI{5}{\percent} error level,
under the stated conditions. Recovering runs lost to computing time
limits did not change that result; one recovered run came close in
a robustness variant.

The principal qualifications are the hybrid within-cell shapes,
\emph{no calorimetric-response uncertainty for hadronic recoil}, and
unproven convergence as the grid is refined. The possible error from
structure finer than the grid is unbounded. Other conditions concern
the interaction-model variations, including clipped negative weights;
a bounded calibration shift from using different simulation sample
sizes; and each generator's energy range and finite simulated sample.
Numerical-rounding checks and a grid-sensitivity scan are documented
in the analysis note's ``Joint five-dimensional generator tests.''
The scan does not bound the unresolved grid error. This is a
conditional test, not a new cross-section measurement with validated
error bars.

In a comparison chosen after seeing the result, untuned GENIE is not
rejected on the matched coarse muon projection but is rejected on
the hadronic projection. Hadronic information therefore contributes
to the rejection. No added discrimination over the matched coarse
lower-dimensional projections has been demonstrated, and
non-rejection would not establish that a simulation is true.

\subsection*{PET: promising development, no measurement}

PET demonstrates that OmniFold can run on individual detector deposits.
The original version reads recoil alone; a later version also reads
the muon. Simulation studies improved recovery of deliberately changed
truth distributions, but no design met every requirement fixed in
advance. Interval tests found poor coverage, especially where detector
acceptance is low; neither averaging fits nor adjusting their widths
provides a validated repair. Comparisons with the tree learner depend
on the test and establish no general ranking or precision advantage.
PET supplies no cross section or uncertainty for any result here.
The development studies, interval diagnosis and generator-test
diagnoses are reported separately
\cite{PETImprovement2026,PETFinalDesign2026,PETIntervalDiagnosis2026,
PETGBDT2026,PETGeneratorDiagnosis2026}.

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.90\textwidth]{pet_gbdt_paired_differences.pdf}
  \caption{Exploratory PET comparison with the tree learner
  (GBDT) on the same finite simulated samples.
  Positive values mean greater recovery of an imposed distortion.
  E0 and E3 are energy tilts; E1 separates acceptance regions;
  E4 tests proton content and E5 the joint energy--momentum-transfer
  distribution. Bars are unadjusted 95\% intervals for paired
  differences at seven iterations, over 60 draws for E0, E1 and E3
  and 40 for E4 and E5. They compare point estimates conditional
  on these samples, not validated measurement uncertainties.
  The tree configuration differs from that of the five-quantity
  result.}
  \label{fig:primerpet}
\end{figure}

\subsection*{A wider signal definition}

The published true-muon cuts exclude about a third of the simulated
interaction rate; that fraction is a simulation estimate.
Relaxing those cuts retains the same tracker volume and reconstructed
MINOS-based selection, so it enlarges the population being estimated
without adding selected observations.

The preliminary extended cross section is
$\sigma_{\mathrm{ext}}\approx
\num[round-mode=figures,round-precision=2]{\fpsSigma}$
\si{cm^2/nucleon}.
Only about \SI{6}{\percent} of the rate is a newly detector-supported
extension. About \SI{28}{\percent} lies in low- or zero-efficiency
cells and remains a separately labelled, simulation-dependent
extrapolation.

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.99\textwidth]{fps_pilot_compare_MEFHC}
  \caption{Extended-signal study on the muon-momentum grid,
  shown by cell number.
  Left: within the published region, between the black lines,
  the central value agrees with the original to better than
  one percent. Center: changing the starting simulation has
  a small effect in accepted cells and a much larger effect
  in low-efficiency cells. Right: the preliminary extended
  central value, with rate shown logarithmically.
  Detector-supported and simulation-dominated regions must
  be interpreted separately.}
\end{figure}
```

```latex
\section{The takeaway}

Unbinned OmniFold closely reproduces MINERvA's published muon cross
section and makes unfolding more quantities together practical,
while training, simulation and uncertainty estimation remain demanding.
The three- to five-dimensional central values recover a known
low-recoil shortfall and locate an integrated excess over the tuned
simulation at high available energy and hadronic mass.

The main limits are incomplete recovery of changed truth, unvalidated
uncertainties and numerical instability. The multi-quantity results
remain central values only, with tested biases outside their quoted
uncertainty; the two-variable statistical error bars now quoted have
also had no coverage test.

Separately, the joint test rejects hybrid hypotheses for all five
generators, in rate and shape and in shape alone, at a combined
\SI{5}{\percent} error level under its stated conditions.
It includes no calorimetric-response uncertainty, has unproven
fine-grid convergence, and shows no added discrimination over matched
coarse projections.

PET remains method development. The extended signal study identifies
a small detector-supported addition alongside a larger,
separately labelled simulation-dependent extrapolation.
```

```latex
\begin{abstract}
This primer explains a MINERvA measurement of muon-neutrino interaction
probabilities and OmniFold, the machine-learning method used to unfold
detector effects. The two-variable result reproduces the published
interaction rate to about one percent, although a correlated shape
difference remains and the quoted statistical error bars have not been
coverage-tested. Unbinned unfolding of three to five quantities, a first
at MINERvA, recovers a known low-recoil discrepancy and locates excess
cross section relative to the tuned simulation at high available energy
and hadronic mass. These results are central values only: simulation
tests reveal biases outside their quoted uncertainty. A separate joint
test rejects five hybrid generator hypotheses under stated conditions,
without calorimetric-response uncertainty or demonstrated fine-grid
convergence. Added discrimination over matched coarse projections is
unshown. PET remains method development. Relaxing the true-muon cuts
also identifies a small detector-supported extension of the signal
definition alongside a larger, separately labelled simulation-dependent
extrapolation.
\end{abstract}
```

B. Removal and merger audit

Each row covers the **whole original paragraph, item or caption beginning with the quoted words**, including its sentences retained in compressed form. Source comments and replaced headings are excluded.

| Original opening or short quote | Disposition |
|---|---|
| Abstract: “This is a short, jargon-light guide…” | **Merged into:** replacement abstract; retains purpose, method, findings and supported/extrapolated distinction, and adds the joint test and essential validation limits. |
| “Our results have different levels of validation…” | **Dropped:** the preliminary inventory delays the findings; validation now accompanies the relevant result. |
| Overview item: “A published result, reproduced.” | **Merged into:** “Reproducing the published muon measurement.” |
| Overview item: “More quantities at once.” | **Merged into:** multi-quantity findings and the three ranked limits. |
| Overview item: “Known and new features in the data.” | **Merged into:** low-recoil and localized-excess findings. |
| Overview item: “A joint test of five simulations.” | **Merged into:** joint-test subsection, abstract and takeaway. |
| Overview item: “A neural network on raw detector data.” | **Merged into:** brief PET subsection. |
| Overview item: “A wider signal definition.” | **Merged into:** final subsection on the extended signal. |
| “Each result is only as validated as its own checks.” | **Dropped:** its content is expressed through result-specific qualifications. |
| “Before trusting a new method…” | **Merged into:** opening two-variable findings paragraphs; removes the introductory maxim and preserves agreement, correlated shape difference and uncertainty comparisons. |
| “The new method reproduces the old answer…” | **Dropped:** repeats the preceding numerical comparison; similar uncertainty sizes are now explicitly distinguished from validation. |
| “One qualification: two software implementations…” | **Merged into:** two-variable qualification paragraph; preserves implementation dependence and post hoc selection. |
| “The error budget also has known limits.” | **Merged into:** rebuilt-budget paragraph, retaining all three excluded effects. **Moved to note/paper:** repaired-defect inventory, with existing `TwoDFollowup2026` citation. |
| “To test whether error bars have the right size…” | **Merged into:** coverage qualifications. **Moved to note/paper:** detailed independent-sample and nuisance-generation requirements; the need for new independent inputs remains explicit. |
| “We did run such a test…” | **Merged into:** earlier-band coverage result; retains the measured coverage and affected momentum regions. |
| “That test was of the statistical error bars…” | **Merged into:** statement that the earlier defect was corrected and the quoted bars remain untested. |
| “The published numbers are unchanged by this check.” | **Dropped:** wording can ambiguously refer to either measurement; the replacement distinguishes the earlier band from the quoted result. |
| Muon-figure caption: “The unfolded muon cross section…” | **Merged into:** revised caption, now identifying the red curve and distinguishing GENIE versions. |
| “With the central value reproduced…” | **Merged into:** multi-quantity opening; keeps the first-at-MINERvA claim explicitly limited to unbinned unfolding. |
| “Each richer measurement, when collapsed back down…” | **Merged into:** normalization-only consistency statement. |
| “These are five recorded coordinates…” | **Merged into:** coordinate-dependence paragraph, including the truth-level neutron omission. |
| “The first physics payoff appears…” | **Merged into:** two low-recoil paragraphs; preserves four predictions, 2p2h interpretation, rescattering caveat and published-result comparison. |
| “That measurement defines true available energy…” | **Merged into:** immediate qualification of the 9.2% and 6.3% comparison. |
| Simulation-figure caption: “The unfolded central values…” | **Merged into:** shortened caption, retaining configurations, beam-spectrum correction, non-independence and central-values-only status. |
| “Adding the hadronic-mass axis…” | **Merged into:** two localized-excess paragraphs; preserves the other-generator comparisons, GiBUU energy-range limitation and untested seed dependence of the excess share. |
| “This is the kind of localized discrepancy…” | **Merged into:** statement that the joint map locates the feature; removes the broader suggestion that it identifies missing model physics. |
| Joint-map caption: “The unfolded data compared…” | **Merged into:** revised caption; retains grid boundaries, cell-integrated units, catch-all-cell interpretation and absence of significance. Seed movement is stated once in the ranked limits. |
| “The multi-quantity central values above…” | **Merged into:** multi-quantity status paragraph and second ranked limit; preserves the documented exception and lack of significance claims. |
| “Our method has a random component…” | **Merged into:** second ranked limit. **Moved to note/paper:** detailed quarter/half/full subset chronology and noise-reduction factor. The tested range, one seed pair and larger-ensemble limitation remain. |
| “Two further facts qualify the shift.” | **Merged into:** second ranked limit; preserves the five fixed components and the distinct central-value movement. |
| “One more thing is worth saying plainly…” | **Merged into:** detector-variation summary. **Moved to note/paper:** five-versus-four component inventory and individual variation names. |
| “By itself, it says nothing…” | **Merged into:** explicit statement that bookkeeping does not establish completeness of hadronic-response variations. |
| “Two end-to-end tests limit…” | **Merged into:** first ranked limit and background-bias paragraph; retains numerical residuals and the wrongly sampled spectrum caveat. |
| “A follow-up study looked inside…” | **Merged into:** truth-dependent recovery, background-classifier and stability paragraphs. |
| “A later study found that the bootstrap…” | **Merged into:** third ranked limit; retains that the larger-classifier variant’s own bootstrap includes rounding variability. |
| “That finding is limited to that version’s own bootstrap…” | **Merged into:** third ranked limit; preserves non-transfer to the quoted uncertainty and the failed stability verdict. |
| “Three possible remedies each have a limit.” | **Merged into:** second ranked limit; retains the limits of longer runs, cell merging and starting-model changes, plus the failed variant coverage test. |
| “None of these studies changed…” | **Merged into:** end of background-bias paragraph. |
| “None of these five-quantity findings affects…” | **Merged into:** ranked-limits introduction, retaining the separate two-variable uncertainty. |
| “We also asked a sharper question…” | **Merged into:** first two joint-test paragraphs; preserves hybrid nulls, both testing modes, pseudo-experiment calibration, multiplicity and recovered runs. |
| “This is a test of the simulations under six conditions:” and six-item list | **Merged into:** ranked joint-test qualifications. **Moved to note/paper:** the list presentation and technical implementation detail; every substantive condition remains named in prose. |
| “Sensitivity to numerical rounding is also checked.” | **Merged into:** pointer to documented rounding checks. |
| “These conditions are detailed in the analysis note…” | **Merged into:** existing titled-note pointer. |
| “The result is not a new measurement…” | **Merged into:** conditional-test qualification. |
| “In a comparison chosen after the result was known…” | **Merged into:** final joint-test paragraph; retains post hoc status, projection result and absence of demonstrated added discrimination. |
| “How robust are the rejections…” | **Moved to note/paper:** definition and numerical results of the κ scan. **Merged into:** explicit statement that the sensitivity scan does not bound unresolved grid error. |
| “At that point the decision becomes ambiguous…” | **Moved to note/paper:** scan-specific decision interpretation. **Merged into:** no bound on sub-grid error or demonstrated convergence. |
| “Two studies test the method’s limits…” | **Dropped:** replaced by separate PET and extended-signal subsections. |
| “We ran PET, the ‘point-cloud transformer’…” | **Merged into:** brief PET paragraph; preserves recoil-only versus full-event distinction and no measurement contribution. **Moved to note/paper:** pairing and classifier-level description. |
| “Completed simulation studies then improved…” | **Merged into:** statement of improved recovery without meeting all requirements. **Moved to note/paper:** design chronology, ten-iteration admission history and 31%/90%/86% recovery comparison, cited with `PETImprovement2026` and `PETFinalDesign2026`. |
| “Better recovery was not enough…” | **Merged into:** no design meeting all requirements, poor interval coverage and no PET uncertainty. **Moved to note/paper:** individual design verdicts, six-fit construction and detailed coverage percentages. |
| “Our diagnosis of the saved outputs…” | **Merged into:** no validated repair through averaging or width adjustment. **Moved to note/paper:** additive-variance explanation, six-fit estimator mismatch and unmeasured deployment coverage, cited with `PETIntervalDiagnosis2026`. |
| “An exploratory comparison then ran…” | **Merged into:** test-dependent comparisons with no general ranking or precision claim, plus configuration caveat in the caption. **Moved to note/paper:** individual test rankings, binned-method comparison and iteration history, cited with `PETGBDT2026`. |
| “For the three generator-model tests…” | **Moved to note/paper:** detector-step underfitting, missed-event extrapolation, exact-weight check and untested truth-input addition, cited with `PETGeneratorDiagnosis2026`. **Merged into:** unchanged verdict that no PET design met every requirement. |
| PET-figure caption: “Exploratory simulation comparison…” | **Merged into:** shortened caption retaining sample-conditional interpretation, test definitions, iterations, draw counts and unadjusted intervals. |
| “Separately, the published signal definition…” | **Merged into:** two extended-signal paragraphs; preserves simulated excluded fraction, unchanged selection and separately labelled extrapolation. |
| Extended-signal caption: “The extended-fiducial scalar study…” | **Merged into:** shortened caption retaining accepted-region agreement, prior sensitivity and separate interpretation of unsupported cells. |
| Takeaway: “Unbinned machine-learning unfolding reproduces…” | **Merged into:** replacement takeaway; retains practical scaling qualification and the supported/extrapolated distinction, and adds the conditional joint-test result. |
| “The multi-quantity measurements are shown…” | **Merged into:** takeaway’s ranked limitations and central-values-only statement. |

C. Numbers added or newly rounded

The supplied Markdown has no numbered lines. The source column therefore identifies its subsection and exact source-bearing line or bullet.

| Addition or rounding | Where used | Source line in `numbers-available.md` |
|---|---|---|
| About one percent integrated agreement | Newly added to abstract | **Paper F5, (1) Value:** “Ratio of integrated cross sections, ours over published: **1.011**…”; macro source `values.tex:48`. |
| 67% of positive integrated excess above 0.8 GeV; 83% of that above \(W=1.8\) GeV | Localized-excess finding | **Primer F-new-2, (1) Values:** “**67%** … E_avail ≥ 0.8 GeV, and **83%** of that … W ≥ 1.8 GeV”; source bullet `sec_eavailw.tex:49-53`. |
| 22% of positive integrated excess in the \(E_{\rm avail}>3\), \(W>3\) GeV cell | Localized-excess finding | **Primer F-new-2, (1) Values:** “**22%** sits in the single deep-DIS catch cell…”; source `sec_eavailw.tex:49-53` and released figure arrays. |
| 6.145% → about 6%, retaining `\sprojMeasured` | Ranked uncertainty limit | **Primer F7, “What the macros are”:** “`\sprojMeasured` = **6.145** (`values.tex:407`)”; rounding recommendation in **(5) Proposed text**. |
| 6.02% of quoted uncertainty → at most about 6%, retaining `\cvMoveOverSigmaMax` | Ranked uncertainty limit | **Primer F7, “What the macros are”:** “`\cvMoveOverSigmaMax` = **6.02** (`values.tex:458`)”; rounding recommendation in **(5)**. |
| \(4.502\times10^{-38}\) → about \(4.5\times10^{-38}\), retaining `\fpsSigma` | Extended signal | **Primer F7, “What the macros are”:** “`\fpsSigma` = **4.502e-38**”; ledger `VALIDATION_LEDGER.md:1615`; rounding recommendation in **(5)**. |
| About 10% changed-truth residual, now placed in the first ranked limit | Ranked recovery limit; already present deeper in the original | **Primer F-new-1, (1) Values:** “median … residual is **9.7%**”; source `OUTCOME-20260925-s5n-stage1-development-fail.md:57,75-77`, note `sec_5d.tex:73-74`. |
| GENIE 2.12.6 identifies Tune v1’s red curve | Two-variable figure caption | **Primer F-new-8, (1) Value:** “The red curve is **MINERvA Tune v1 on GENIE 2.12.6**”; producer `plot_2d_threeway_fig13.py:200`. |
| Combined 5% error level | Newly added to takeaway; retained in body | **Not a new external number:** already supplied in the original joint-test subsection. |

The corner percentages refer to **positive cell-integrated differences**, not ratios. The two rounded 6% quantities retain distinct descriptions. The changed-truth residual is attributed to the tested deterministic variant, rather than presented as a measured bias of every reported estimator.

D. Word counts

Counts exclude LaTeX commands, comments and mathematical expressions; section counts include headings and captions. The section totals below are **manual estimates**, not verified exact counts.

| Text | Old | New |
|---|---:|---:|
| Abstract | 129 | 147 |
| Sections 3–4 combined | approximately 5,300 | approximately 2,500 |

The siunitx rounding syntax follows the supplied recommendation. Compilation and exact section word counts have not been checked, in accordance with the instruction to use no tools, commands or files.

---

## P15. Claude: note homes and theme D (sha256 `7c6f999ec9dddde9…`)

### Plain-language pass 2: note prerequisites (theme B/A note homes) and theme D

Worktree `wt-plain2`, branch `stageF/plain-language-pass2-20261018` at `5cb1b038` (base `main` `34650231`). I edited only
`docs/analysis-note/`. I made no git writes. I did not touch `paper_body.tex`, `main_paper.tex`, `primer_body.tex` or `main_primer.tex`.
Every changed site carries `% plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2)`, or the base-defect
variant in 1d. Comments are on their own lines.

Files changed: `app_release.tex`, `sec_joint.tex`, `sec_5d.tex`, `result_status_rows.tex`, `technote.bib`, `publication.bib`.

#### 1a. Paper P6 note home: `app_release.tex:17-28` (§`app:release`, "Release status")

**Added after** "…and its joint-null figure.":

> RC7 was assembled before the two-dimensional central value was changed to LightGBM, so its two-dimensional curve is
> the exact-split one. The article's two-dimensional validation figure and its numbers were instead regenerated
> separately, from the committed LightGBM values and covariance, with RC7's plotting code extended to draw this
> analysis's band.

**Source.**
- The paper's sentence: `main_paper.tex:143-147`.
- Its comment, copied into the note comment (`main_paper.tex:148-150`):
  - `stageF/rebuild/outputs/fig1/fig1_validation.pdf`. I checked that the file exists; its sha256 begins `82665808`, as the comment says.
  - `rebuild/scripts/make_fig1_q.py` and `rebuild/outputs/outA/cov2d_Q_205.json.gz`. Both exist.

**Note for the paper step.** The existing note sentence "It also regenerates the article's first three figures from
packaged arrays" stays. The new sentence directly after it qualifies that sentence for the 2D figure.

#### 1b. F7 note home: `sec_joint.tex:27-33` (§`sec:joint5d-design`, after "\jtNtests{} tests.")

> The fine grid is the analysis binning of \S\ref{sec:method-binning}, $14\times16\times7\times7\times6$ bins in
> $(\pT,\pPar,\Eavail,q_{3},W)$; the test cells below are its integrals.

**Confirmed myself:**
- `nd-unfolding/s5p_stage1_inspect.py:38-44`, `FINE`:
  - the edges are 15 for p_T, 17 for p∥, 8 for E_avail, 8 for q₃ and 7 for W, which is 14×16×7×7×6 bins;
  - the E_avail, q₃ and W edges are identical to `sec_method.tex:270-275`;
  - :251 checks the loaded edges against `FINE`.
- `J_EDGES` (:45-46) equal `sec_joint.tex`'s coarse 3⁵ edges, and every coarse edge is a fine edge.
- `docs/publication/audit-20261008/notes/mapping-notes-C.md:25` gives "U (109,65856)", and 65,856 = 14·16·7·7·6.
- `s5p_recompute.py:618-635` checks each prediction's fine edges against the first prediction's, not against a literal.

So the identification rests on code and an audit note, as themeA-sources said. No record sentence states it. The comment
cites all three.

#### 1c. IV C coverage numbers: `sec_5d.tex:357-366` (§`sec:coverage-5d`, after "…claimed for any five-dimensional interval.")

> A quantity fails when the upper confidence bound on its coverage lies below 0.66 for 68\% intervals or below 0.94 for
> 95\% intervals. Under the $\Eavail$ tilt, 51 of the 153 reported cell and projection integrals have 68\% coverage
> confidently below nominal, with coverage as low as 0.060, and 42 fail at 95\%. At nominal truth two fail at 95\%, the
> lowest at 0.850.

**Verified in `docs/orchestration/OUTCOME-20260925-s5c-tier-s-futility-fail.md`:**
- :30, the futility thresholds: UCB < 0.66 at 68% and < 0.94 at 95%.
- :32, nominal truth: 0 futile at 68% and 2 at 95% (EW36, J161); minimum coverage 0.570 at 68% and 0.850 at 95% (EW36).
- :33, E_avail tilt (a = 0.2): 51 futile at 68% and 42 at 95%; minimum coverage 0.060 at 68% (J224) and 0.288 at 95%.
- :36, the per-comparison level, 0.05/459. It is in the comment only.
- :41-43, the counts as the record states them.

**The "153 reported cell and projection integrals" gloss.** I checked it against the receipt
`state/s5c/tier_s/interim_400.json`: `n_functionals` = 153, made of 109 J cells, 42 EW cells, the EW all-ones sum and
`total_integrated`.

**Paper step.**
- The note now carries a 95% minimum only at nominal truth (0.850).
- The tilt's 95% minimum, 0.288, is in the comment, not the text.

#### 1d. Base defect sec_5d-31-63: CONFIRMED and corrected, `sec_5d.tex:216-224`

**Base text:** "(median at most 5%; recovery of at least 75% of a generator-sized departure, against 0.31--0.63
measured)". It reads as "31-63% recovered".

**The record, `RECORD-20260927-s5p-stage2-exit.md`:**
- :76-78: "T2 proxy is the median over reported cells with a > 1% departure of |bias| / |departure|. M is its maximum
  over the development alternatives";
- :96: "T2 needs ≤ 0.25";
- :138: "recovery ≥ 75% … (0.25 against the measured 0.31–0.63)".

So 0.31–0.63 is the measured residual proxy, whose target is ≤ 0.25. It is not a recovered fraction.

**New text:** "…recovery of at least 75\% of a generator-sized departure, that is, a residual proxy of
Fig.~\ref{fig:gbdt-recovery} of at most 0.25, against 0.31--0.63 measured) fail in every definition."
- The figure's caption already defines this proxy with "frozen bound 0.25".
- The site is marked `% plain-language pass 2, director ruling on base defect sec_5d-31-63 (DECISION-20261018-joseph-plain-language-pass2)`.
- The base wording is quoted in the comment.

**Sites with the same misreading.** I grepped `*.tex` in `docs/analysis-note` for `0.31`, `0.63`, `31--`, `63%`, `75%`
and "recover…":
- Note: **`sec_5d.tex:216-218` only**, now fixed. No other note file states the T2 recovery target or 0.31–0.63.
- Paper (`paper_body.tex`, `main_paper.tex`): **none**. The paper's recovery sentences (:71, :506) concern the 74%
  E_avail regularization bias, not T2.
- Primer: **none**. Its "recovered fraction" (:567, :634) is the PET tilt study.

#### 2a. Bibliography

**Paper numbers.** I mapped them through the r3 `main_paper.bbl` order and confirmed them in the new build's PDF:
[25] TwoDFollowup2026, [32] JointTestRecord2026, [33] JointTestKappa2026, [34] JointTestRecovery2026,
[35] JointTestProjections2026, [37] JointTestRecoil2026, [38] AnaTuplePreservation2026, [39] ReleaseCandidate2026.
The numbering is unchanged after the edit. Keys are unchanged.

**Why [25], [38] and [39] had no printed locator.** They were `@online` entries in `technote.bib` with the URL in `url`:
- apsrev4-2 has no `online` function; it falls back to `misc` and only hyperlinks the title with the URL;
- the note's biblatex runs with `url=false` (`preamble.tex:45`).

So neither deliverable printed the URL. I converted these three to `@misc` with
`howpublished = {MINERvA-OmniFold repository record, \url{…}}`, the form `publication.bib`'s repository records use. The
URL is unchanged. I dropped `organization` because "MINERvA-OmniFold" is now in `howpublished`.

**Results.**
- The paper now prints all three URLs. The note's bibliography prints them too, at [45], [96] and [97].
- The three "entry type isn't style-file defined" BibTeX warnings are gone. The only remaining warnings are the 2 base
  ones (jnrlst, empty year in MINERvA:OpenData).
- The old titles are kept in comments. There is no `@` in any comment, since BibTeX would parse it as an entry.

| # | key (file) | old title | new title |
|---|---|---|---|
| [25] | TwoDFollowup2026 (technote.bib) | Two-dimensional uncertainty follow-up: construction findings and validation feasibility | Two-dimensional uncertainty budget: defects in the earlier version and feasibility of a calibration test (+ locator) |
| [32] | JointTestRecord2026 (publication.bib) | Joint five-dimensional generator tests: frozen contract and recorded result | Five-dimensional joint generator tests: specification and result |
| [33] | JointTestKappa2026 (publication.bib) | Joint-test decisions under rescaled sub-fine-grid variants: report-only sensitivity scan | Sensitivity of the joint-test decisions to the assumed residual below the fine grid |
| [34] | JointTestRecovery2026 (publication.bib) | Joint five-dimensional generator tests: report-only recovery of the lost pseudo-experiments | Five-dimensional joint generator tests: rerun of the pseudo-experiments lost to time limits |
| [35] | JointTestProjections2026 (publication.bib) | Joint tests restricted to matched coarse projections | Joint generator tests restricted to coarse two-dimensional projections |
| [37] | JointTestRecoil2026 | Recoil-response sensitivity of the joint-test rejections | **unchanged** |
| [38] | AnaTuplePreservation2026 (technote.bib) | AnaTuple input identities and data preservation: completed hashes and data addition | SHA256 checksums of the AnaTuple input files and preservation of the data files (+ locator) |
| [39] | ReleaseCandidate2026 (technote.bib) | Article release candidate RC7: sufficient-input replay and figure regeneration | Candidate release package for the article: replay of the joint tests and regeneration of the figures (+ locator) |

**Where each title comes from.** Each new title describes its record's CITABLE FOR scope and opening:
- [25] the defects in the 2D budget and the SD/SM calibration's feasibility;
- [32] the frozen decisions;
- [33] the κ breakdown along δ_M1;
- [34] the rerun of the 277 lost seeds; "time limits" is the note's own wording, `sec_joint.tex:258, 266`;
- [35] the (p_T,p∥) and (E_avail,W) projections;
- [38] the completed checksums of the 2,374 inputs and the CFS data copy;
- [39] RC7's replay and its Figs. 1–3.

**[37] is unchanged.** Its "W2B-REPORT" is the file name in the URL, not the title. Renaming it would mean a new path at a
new commit, which I did not do.

**Not done (out of my list).** `technote.bib`'s five PET `@online` entries (PETImprovement2026 … PETGeneratorDiagnosis2026)
have the same locator defect in the note (url=false), but none is cited in the paper. They are left for the director.

#### 2b. `result_status_rows.tex` (note Table 1): `:12-14`, `:19-22`, `:24-26`

| cell | old | new |
|---|---|---|
| row 1 rsD | Publication readiness unresolved. | Readiness for publication not yet established. |
| row 2 rsB | One scalar-5D covariance adopted under exception | One scalar-5D covariance, used under a documented exception |
| row 2 rsD | Central comparisons; all four adoption measurements apply. | Central-value comparisons; the covariance's four measured limitations apply. |
| row 3 rsC | Frozen tests and arithmetic recomputation; … | Tests specified in advance; independent recomputation of the arithmetic; … |
| row 3 rsD | …; no new reportable uncertainty. | …; no new uncertainty on the cross section. |

- The wording follows pass-1 R5 F7, except row 1, which R5 did not propose.
- "Four measured limitations" refers to `sec_5d.tex` "What the covariance supports" ("Four measurements bound the
  claims"). The comment says so.
- The column structure is unchanged. The table still sits on the exec-summary page. The note's overfull-box count is 12,
  the same as the r3 build.

**Left as they are:**
- the header "Uncertainty construction" (the R2 "construction" noun);
- "Central reproduction stands";
- the caption in `sec_execsummary.tex` ("construction, adoption, testing and publication readiness are distinct").

The caption is outside this task's file. The director may want it aligned with the row wording.

#### Checks

**Build:** `build_copy.sh p2-note $W` exit status **0**, read directly (output redirected to `build-p2-note.out`, no pipe).
- All four targets "written by this run; no unresolved references".
- 0 "undefined on input" lines in each final log.
- Gates: SELF-TEST PASS, RESULT PASS, gzip receipt PASS, SELF-TEST PASS (18 perturbations rejected), SEC4-RECEIPTS PASS (15/15).

**Pages:** note **123**, paper 12, primer 14, PET note 26. This is the same as `pdfs-final`.

**`check_invariance.py $W 34650231`:** rc=1, output in `inv-p2-note.out`.
- **Note block:** `[SAME]` for numerals (640), value macros (84), cite keys (28), ref targets (147) and labels (36); all 337
  base comment lines survive.
- **Paper and primer blocks:** all `[SAME]`.
- **Mid-line block:** `[SAME] none`.
- **Files outside pass 1's scope** (expected for this pass): `app_release.tex`, `publication.bib`, `result_status_rows.tex`,
  `sec_5d.tex`, `sec_joint.tex`, `technote.bib`.
- **My own check on these six files** (they are outside the script's coverage), against the `34650231` copies:
  - every base comment line survives;
  - no new line has a mid-line `%`;
  - the only base lines removed are the reworded ones: app_release 1 (a line split), sec_5d 2, result_status_rows 3,
    publication.bib 4 titles, and technote.bib 15 (the three entries' bodies).

**Numbers added** (all from committed sources):
- 14, 16, 7, 7, 6: `sec_method.tex`, `s5p_stage1_inspect.py`, `mapping-notes-C.md`;
- 0.66, 0.94, 51, 153, 0.060, 42, 0.850 and "two": OUTCOME-20260925 :30-43 and the receipt;
- 0.25: RECORD-20260927 :96, :138 and the caption.

Not run: pytest.

---
Path: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/p2-note-prereq.md`

1. The note now carries homes for paper P6 (`app_release.tex:17-28`), F7 (`sec_joint.tex:27-33`; I confirmed the identification in code and the audit note) and the IV C coverage numbers (`sec_5d.tex:357-366`; I verified them against OUTCOME :30-43 and the receipt).
2. Base defect sec_5d-31-63 is confirmed and fixed: 0.31–0.63 is the residual proxy (target ≤ 0.25), not a recovered fraction. There are no other sites in the note, paper or primer.
3. Bibliography: six titles are in physics terms and [37] is unchanged, with the keys kept. [25], [38] and [39] became `@misc` entries with a `howpublished` locator, so both the paper and the note now print the URLs.
4. `result_status_rows.tex`: five internal phrases became plain wording with the same content. The table still fits.
5. Build rc 0, no unresolved references, all gates PASS; pages note 123 / paper 12 / primer 14 / PET 26. Invariance: the note, paper, primer and mid-line blocks are all SAME; the six expected out-of-scope files are listed.

---

## P16. Claude: paper integration (sha256 `ba98adf3acead59f…`)

### Plain-language pass 2: the paper (integration writer's record)

Worktree `wt-plain2` (branch at `b3fc422b`; pass-2 base `34650231`). Files edited, uncommitted, no git write:
`docs/analysis-note/paper_body.tex` and `docs/analysis-note/main_paper.tex` (abstract and Data availability only).
Every changed site carries `% plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2)` with the theme
and item. All 255 base comment lines survive verbatim, and no new comment sits mid-line. Base copies of both files
are at `$S/paper_body.base-p2.tex` and `$S/main_paper.base-p2.tex`.

#### 1. Summary by section

| section | what changed |
|---|---|
| Abstract | 233 → 155 words (source). Headline results, plus only these limitations: 3–5D are central values only; the model dependence (about 10–13% per cell) prevents a 5D measurement meeting the predefined 10% target; the rejections are of the **hybrid null hypotheses** (F15); the nuisance model has no calorimetric recoil-response uncertainty; fine-grid convergence is not shown; the joint information is not shown to discriminate beyond matched coarse projections. Theme A: "integrated cross section within about one percent" (F5) and 10–13%/10% (F4). These items now appear only in the body: the generator names, the marginal-normalization and closure checks, the seed and coverage limits, "These rejections hold only under stated conditions" (replaced by the two named conditions), and "recover known discrepancies". |
| I | The results paragraph keeps its structure. Changes: "the quoted uncertainties do not include it" is stated once, at its claim (IV C); the failed 5D coverage test is named (F1); "untested coverage" became "untested or failed interval coverage"; the model dependence gets its number and target (F4) with a pointer to Sec. V; the rejections are of the hybrid nulls (F15). The roadmap follows the new section order. |
| II | unchanged |
| III | "which was the original two-dimensional choice" is cut (history). The replacement is disclosed at its claim (IV A). |
| IV intro | P2: the bookkeeping and iteration-stability sentence moved to the note. |
| IV A | unchanged. The post hoc learner choice stays at its claim. |
| IV B | P4/P16: the earlier-budget defects are now stated as method ("Each universe is unfolded with the same simulated truth input as its reference"; the three-stream bootstrap "so that the statistical fluctuations of the background templates are propagated"), with one clause of history and the cite kept. G2: two sentences merged. P3 is shortened: the cause (the completeness division), its removal, and "wider than the toy scatter, for reasons not established" moved to the note. **P3 could only be partly moved**, because D2's must-carry history and the three values bound by `check_sec4_receipts.py` (95.4, 97.7/78.1) have to stay in `paper_body.tex`. Summary paragraph: "We make no claim about coverage" is joined to the W1 sentence; nothing removed. The D1, D2, D4 and D5 required content is unchanged, and D5's required clause is verbatim. |
| IV C | "as first measured" is cut. F12: the 74% is attributed to "the same deterministic variant". F1 with theme-A numbers: the coverage test "failed its criterion …: under an E_avail tilt, 51 of the 153 … integrals have 68% coverage confidently below nominal, as low as 0.06, and 42 fail at 95%; at nominal truth two fail at 95%, the lowest at 0.85. These intervals therefore miscover at the tested truths, and no frequentist coverage is claimed for the five-dimensional intervals." "This motivates …" moved to the end of the new Sec. V. |
| **V (was VII)** | **Moved before the central values**, label `sec:uncertainty-status` kept. Register: "an exception to the criteria" became "We nevertheless use this covariance, as recorded in the analysis note, and that allowance covers no other covariance". P5: the seed-convergence evidence is one sentence; the 40/80 values and the floor values moved to the note. F4: "For its fallback definition, the 39 supported (E_avail,W) cells, the bounded model-dependence component (the largest shift over five generator-sized changes of the truth) alone has a median of 13.4%, above the target of a 10% median half-width for the total 68% interval. Over the definitions considered, this model dependence is about 10–13% per cell, comparable to the generator differences …". This also resolves pass-1 F8. "came from the same study" moved to the note. The section closes with the motivation for the joint tests. |
| VI (was V) | One opening scope sentence ("descriptive: … central values only, and no significance is assigned (Sec. V)") replaces the two repeated statements, at Fig. 2 and at Fig. 3. The local caveats (no response-mismatch closure for the map; regularization bias largest there) stay with the map. |
| VII A (was VI A) | F7: the fine grid is defined ("the published 14×16 muon-momentum bins times 7 E_avail, 7 q₃, and 6 W bins"). P8: the 1379-row count moved to the note. **P15**: one new paragraph, "Some choices were made after results had been seen", collects: the 2D learner choice (pointer to IV A), the design reviewers' view of residuals, the budget extension, the three post-decision studies (κ scan, lost-PE rerun, coarse projections; the last specified after the 5D outcomes were known) and the post hoc GENIE CV projection observation. Register: "The reviewers of the design" became "Those who reviewed the test design". |
| VII B | F6: the rate is given (\jtMoneWnormMin–\jtMoneWnormMax per halving in a proxy of the test metric, "a value adopted when the test was designed whose calculation is not recorded"), kept apart from the L2 ratio. P9: the 5.2 δ_fine endpoint and "bounds neither" are stated only in VII C; (i) points there. |
| VII C | The scan's timing moved to P15. P7: the lost-PE paragraph is cut from 6 sentences to 3. "Batch-job" became "Computing time limits"; the worst-case sentence, the independent review of the procedure and the 16/16 check moved to the note. The margin 4.6/868.6 is kept. Coarse-projection timing moved to P15. F15: "global assessments of the hybrid null hypotheses built from the five specified generator versions". |
| VII D | unchanged ("a post hoc observation" kept at its claim, and also listed in P15) |
| VIII | The repeated limitation list is merged into the three kinds of result. The C4 statement "the quoted two-dimensional statistical block has had no coverage test" and the C6 learner statement are kept. F4 has its number. F15 applies. "recovering every lost pseudo-experiment changes no decision" is now in VII C only. |
| Data availability | P6: the assembly chronology and the plotting-code extension moved to the note (app_release.tex:23–27, b3fc422b). Kept: "The package carries the exact-split two-dimensional curve; Fig. 1 and its numbers were instead regenerated separately, from this paper's LightGBM values and covariance." Everything else is unchanged, including "not yet deposited" and the `\pubhold`. |

#### 2. Outside-model advice: adopted, and errors rejected

**Adopted (each checked against the current source and its records):**

| idea | model | check |
|---|---|---|
| Move Sec. VII before the results | GPT outline §2; Gemini r2 | director's decision; labels and refs verified in the build |
| Replace "These rejections hold only under stated conditions" with the named conditions | GPT r1 Part 2/3, Gemini r1 Part 3 | the two named conditions are the base abstract's last sentence |
| Narrow claims, do not stack qualifiers; abstract around two outputs | GPT outline §5 | applied in the abstract (155 words) |
| One scope statement at the start of the central-value section | GPT r1 Part 2 (V) | it replaces two identical statements; the local caveats stay |
| One paragraph for the data-informed choices | GPT r2 (v-a), Gemini r2 | P15 (from pass 1); every item checked against VI A/C/D base text and sec_joint.tex:105, :278, :316 |
| Compress the lost-PE narrative to its final state | GPT r1 Part 2 (VI C), r2 (v-c) | sec_joint.tex sec:joint5d-lost carries all of the moved content |
| Shorten the recomputation sentence | GPT r1 | the note keeps the count (sec_joint.tex:114) |
| Sec. VII register ("exception to the criteria") | GPT r1, Gemini r1 | rephrased without removing that the covariance fails the criteria and is used only by an allowance limited to it. GPT's "retained only as a diagnostic" was **not** adopted (a new use claim; F9) |
| State the coverage numbers and "miscoverage at the tested truths" | GPT r2 (iv), Gemini r2 (iv) | numbers checked against sec_5d.tex:362–366 (b3fc422b) and themeA-sources; tested object kept as "a deterministic variant of the estimator" |
| Name the estimator of the 74% | Gemini r2, GPT r2 | OUTCOME-…s5n…:25, :57; the same dev receipt backs the negweight values (check_sec4_receipts.py) |
| Fine-grid binning, halving rate, fallback 13.4% vs 10% | GPT r2, Gemini r2 | themeA-sources F4/F6/F7, with its cautions (RD2 9.6%, kept apart from the L2 ratio) |
| Merge the repeated "no coverage" statements in IV B | GPT r1, Gemini r2 | D1 must-carry list checked: every item is still present |

**Rejected (outside-model errors or overreach):**
- Gemini r1 Quote-6 rewrite: "no simulated pseudo-experiment approaches the observed statistic". False; the closest is 4.6 below 868.6, which is kept. Its "maximum of 2000" is also wrong (the cap is 1999, \jtBcap).
- Gemini r1 Quote-4: says the bootstrap fix "resolved" undercoverage and gives intervals that "conservatively envelope" the fluctuations. Rejected. The rebuilt band is only rescored post hoc, and the quoted block is untested.
- Gemini r2 abstract "unmodeled coverage"; Gemini r1 abstract "first application" and "successfully". Not used. The paper says "We are not aware of".
- Gemini r1 Quote-2: "inherited from AnaTuple conventions" and "negligible compared to the leading systematics". Both wrong (triage G-M5); not used.
- Gemini r2 IV B: "Following this post hoc observation, we include … the run-period block". Rejected: a new claim that no source supports here.
- Gemini r2 Data availability: drops "not yet deposited" and "cannot be recomputed". Rejected, because both are limitations.
- Gemini r2 VII: moves the exception and the failed criteria to the note. Rejected; they are kept, rephrased.
- GPT r2 abstract: "tested bias-corrected five-dimensional statistical intervals show miscoverage". Rejected: the tested object is a deterministic estimator **variant**, so the abstract omits the coverage test and the body names the variant. GPT's abstract "1.1%, 95.6% of bins" was replaced by the Intro's "about one percent".
- GPT r2 IV B: adds "the replicas use the central value's completeness" (F17). Not added: the director's call, not a theme-A number, and no measured check exists (themeA-sources F17).
- GPT r2 VI A: drops the "remain valid at the number reached" qualification from its own place. The sentence is kept verbatim; its defect is listed in §7 as F-p2-2.
- GPT r1 "the observed refinement ratios do not establish a remainder bound": already said ("unmeasured and potentially material").
- GPT r2 IV B: "Containing the period differences … are consequences of its construction" would replace D5's required clause. Rejected: W2 requires the clause verbatim.

#### 3. Moved to the note

| paper text (base) | note location that carries it (wt-plain2 at b3fc422b) |
|---|---|
| IV intro: "The bookkeeping of missed events … checked for completeness …; the dependence on the number of iterations is a stability diagnostic; neither establishes recovery or coverage" (P2) | sec_validation.tex:24 ("Miss completeness … no recovery or coverage claim"), :26 ("Iteration stability … not a known-truth accuracy test") |
| III: "which was the original two-dimensional choice" | stated in the paper at IV A ("This choice, which replaced the exact-split result"); note sec_method.tex sec:method-config |
| IV B: "The main cause, a division by the completeness …, was removed in a rebuilt band" (P3) | sec_validation.tex:266–274 |
| IV B: "so the rebuilt band is wider than the toy scatter, for reasons not established" (P3) | sec_validation.tex:286, :290 |
| IV B: "A review of the stored analysis products found errors …" (P4/P16), now method plus one clause | sec_systematics.tex:205–215 (truth-input mismatch; "The July sweep, which the quoted universe block uses, does not have this mismatch"), :243 ("did not propagate background-template statistics") |
| IV B: "We make no claim about coverage" (merged, not moved) | still in the paper; also sec_systematics.tex sec:uq-2d-scope |
| IV C: "as first measured" | history only; sec_5d.tex sec:val-negweight |
| IV C: "This motivates the full-chain calibrated comparisons" | merged into the end of Sec. V (paper) |
| VII (now V): the movements at 40/80 throws and the noise floor (\seedEffectNforty, \seedEffectNeighty, \floorNforty, \floorNeighty, one \sprojMeasured) (P5) | sec_5d.tex:510–514 (item 2 of "What the covariance supports") |
| VII (now V): "The joint tests above came from the same study" | sec_5d.tex:230–231 ("the separately admitted inference branch") |
| V/VI repeated "These statements are descriptive. No significance is assigned"; "As for Fig. 2, these comparisons are descriptive; no significance is assigned" | merged into one opening sentence of the central-value section (paper) |
| VI A: "in all \jtRecompRows{} compared quantities" (P8) | sec_joint.tex:114 |
| VI B (i): "finds the rejections still determined … up to about 5.2 δ_fine" (P9) | the paper's VII C (5.25/5.17); sec_joint.tex:241 (exact endpoints) |
| VI C: "Had every interrupted one exceeded the observed statistic, no test would have been rejected" (P7) | sec_joint.tex:270–273 |
| VI C: "and independently reviewed beforehand"; "it first reproduced 16 completed pseudo-experiments exactly" (P7) | sec_joint.tex:278–279 |
| VI C: "Every submitted pseudo-experiment has now been observed" (merged) | the paper ("All of them were rerun … no assignment … changes any decision"); sec_joint.tex:280 |
| VIII: "and recovering every lost pseudo-experiment changes no decision" | the paper's VII C; sec_joint.tex sec:joint5d-lost |
| Data availability: "The package was assembled before the two-dimensional central value was changed to LightGBM"; "with the package's plotting code extended to draw this analysis's band" (P6) | app_release.tex:23–27 |
| Abstract: the five prediction names, closure checks, seed and coverage limits, "recover known discrepancies" | the paper body (Secs. II, I, IV C, V, VII C) |

**NEEDS NOTE HOME:** none. The note agent's b3fc422b supplies P6, F7 and the coverage numbers.

#### 4. Numbers added (theme A), with sources

| number | where | source (also in a LaTeX comment on its own line) |
|---|---|---|
| "about one percent" (integrated cross section) | abstract | `\ratioTot` (values.tex:48); RECEIPT-2d-agreement-windows-lgbm42-20261011.json; the Intro already prints it (no new numeral) |
| about 10–13% per cell; 10% target | abstract, Intro, Sec. V, Conclusions | note sec_5d.tex:206–231; RECORD-20260927-s5p-stage2-exit.md §4 (VL155) :133, :144 |
| 39 cells, 13.4%, five departures, 10% median half-width, 68% interval | Sec. V | sec_5d.tex:208–216; RECORD-20260927 :127–133, :139 |
| fine grid: 14×16 × 7 × 7 × 6 | VII A | sec_joint.tex:31–33 (b3fc422b); s5p_stage1_inspect.py:38–44; mapping-notes-C.md:25 |
| \jtMoneWnormMin–\jtMoneWnormMax (0.45–0.76) per halving | VII B (i) | values_inference.tex:38–39; A7 claims.rejection; sec_joint.tex:131; provenance-open status kept in words |
| 400 per truth; 51 of 153; 0.06; 42; two; 0.85; 68%/95% | IV C | sec_5d.tex:357–366 (b3fc422b); OUTCOME-20260925-s5c-tier-s-futility-fail.md :30–36, :41–43; interim_400.json (aa574c17), VL150 |
| (attribution, no number) the 74% belongs to "the same deterministic variant" | IV C | OUTCOME-…s5n-stage1…:25, :57, :75–82; audit CLAIM-TABLE V19 |

Not added: the optional 9.7% median (it would sit beside "several percent in the largest cells" and confuse the two); F17 (not a number, the director's call, no measured check); the RD1/RD2 medians (the RD2 caution is easier to keep with the fallback alone).

**Coverage-test TODO:** none. The note prints the numbers (sec_5d.tex:362–366).

#### 5. Post hoc disclosures and where each now sits

| disclosure | where |
|---|---|
| LightGBM 2D central value chosen after both comparisons were known | IV A, at its claim (verbatim); pointer in the VII A P15 paragraph |
| The design reviewers had seen descriptive per-cell residuals | VII A, P15 paragraph |
| Budget extension decided with the observed p values visible; changed no statistic … p values "remain valid" | VII A, P15 paragraph (verbatim content) |
| κ scan specified before it ran, run after the decisions, outside the decision rule | VII A P15 ("Three studies ran after the decisions … each to a specification fixed before it ran"); VII C keeps "outside the decision rule" |
| Lost-PE rerun after the decisions, outside the rule, procedure fixed beforehand | VII A P15; VII C keeps "with a procedure fixed in advance" |
| Coarse-projection comparison specified before it ran but after the 5D outcomes were known | VII A P15 |
| GENIE CV non-rejection in (pT, p∥) is post hoc | VII D at its claim, and P15 |
| Rescoring against the rebuilt band is post hoc and partly circular | IV B, at its claim |
| Shifts set before any result was known, from an assumed extrapolation | VII B (i), at its claim |

#### 6. Invariance check, paper block (verbatim)

Command: `python3 -I …/check_invariance.py $W 34650231 > $S/inv-p2-paper.out; echo rc=$?` gave **rc=1**. The
differences are listed below and explained after the block. The other non-zero causes are outside my files: the
"files changed outside scope" list has app_release.tex, publication.bib, result_status_rows.tex, sec_5d.tex,
sec_joint.tex and technote.bib, all from the note agent's commit b3fc422b. The primer files are modified by the primer
agent. The mid-line block reads `[SAME] none`.

```
== paper
  [DIFF] numerals: lost {'2.12': 1, '21.09': 1, '2019': 1, '16': 1, '5.2': 1, '80': 1}  gained {'10': 8, '13': 4, '6': 1, '3': 1, '0.06': 1, '7': 2, '400': 1, '51': 1, '153': 1, '68': 2, '42': 1, '95': 2, '0.85': 1, '39': 1, '13.4': 1, '14': 1}
  [DIFF] value macros: lost {'jtRecompRows': 1, 'sprojMeasured': 1, 'seedEffectNforty': 1, 'seedEffectNeighty': 1, 'floorNforty': 1, 'floorNeighty': 1}  gained {'jtMoneWnormMin': 1, 'jtMoneWnormMax': 1}
  [DIFF] cite keys: lost {}  gained {'AnalysisNote2026': 1}
  [DIFF] ref targets: lost {'fig:joint': 1}  gained {'sec:uncertainty-status': 3, 'sec:joint': 1, 'sec:repro2d': 1, 'sec:joint-results': 1, 'sec:response': 1}
  [SAME] labels (18)
  [SAME] comment lines: all 255 base lines survive
  [INFO] comment lines added (93):
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): abstract cut to about 150 words; headline
      % results and only the limitations needed not to misread them; theme A (F4, F5) and theme C (F15). Moved to the body
      % only: the five prediction names (Secs. II, VI A), the marginal-normalization and closure checks (Intro, Sec. IV C,
      % Conclusions), "of the same cells" (Intro, Sec. VI C), the seed and coverage
      % limits (Secs. IV, V), "These rejections hold only under stated conditions" (the two that limit interpretation are
      % named), and "The tests recover known discrepancies" (Sec. VI C).
      % Sources: "about one percent" is \ratioTot (values.tex:48; receipt RECEIPT-2d-agreement-windows-lgbm42-20261011.json),
      % as printed in the Introduction; "about 10--13% per cell" and the 10% target: note sec_5d.tex "Reporting definitions
      % for a five-dimensional measurement"; RECORD-20260927-s5p-stage2-exit.md sec. 4 (VL155) :133, :144.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P6. The assembly chronology ("assembled
      % before the two-dimensional central value was changed to LightGBM") and the extension of the plotting code moved to
      % the note, app_release.tex app:release (b3fc422b, :17-28); the package's limitation stays here.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): "the quoted uncertainties do not include it"
      % is stated once, at the claim (Sec. IV C); the failed five-dimensional coverage test is named (theme C, F1).
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme A (paper F4), the size and the target.
      % Source: note sec_5d.tex "Reporting definitions for a five-dimensional measurement" (about 10--13% per coarse joint
      % cell; median 68% half-width at most 10%); RECORD-20260927-s5p-stage2-exit.md sec. 4 (VL155) :133, :144.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme C (F15), the hybrid null hypotheses.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): the section order after the uncertainty
      % status was moved before the central values (director's structure decision).
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, history; that the LightGBM central
      % value replaced the exact-split one is stated once, at its claim (Sec. IV A).
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P2. The sentence on the missed-event
      % bookkeeping and the iteration-number stability diagnostic ("neither establishes recovery or coverage") moved to the
      % note: sec_validation.tex tab:validation-questions, rows "Miss completeness" ("no recovery or coverage claim") and
      % "Iteration stability" ("not a known-truth accuracy test").
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P4/P16, the earlier-budget defect
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P4/P16, the earlier-budget defect
      % stated as method. Source: note sec_systematics.tex sec:uq-2d-construction ("The July sweep, which the quoted universe
      % block uses, does not have this mismatch"); stageC/production/DESIGN.md S5 universe row.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): merged sentences, same content.
      % stated as method (the background stream propagates the template fluctuations); the history kept as one clause.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P3, shortened. Moved to the note
      % (sec_validation.tex sec:coverage): the cause (the bootstrapped completeness division, "attributed to this term of
      % the band"), its removal and the rebuild, and "the rebuilt band is wider than the toy scatter ... its cause is not
      % established". Kept here: D2's must-carry history, and the three values that check_sec4_receipts.py binds in this file.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, the repeated coverage statements of
      % this paragraph merged ("We make no claim about coverage" joined to the W1 sentences); no content removed.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, "as first measured" (history) dropped.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme A (paper F12), the estimator of the 74%.
      % Source: the comment below ("The 74% is the F2/N estimator (VL151)"); OUTCOME-20260925-s5n-stage1-development-fail.md
      % :25 (family N = the s5c F2 deterministic LightGBM with the negweight-refined measured side), :57, :75-82; the same
      % dev_receipt (s5n/stage1) backs the negative-weight values above (check_sec4_receipts.py); audit CLAIM-TABLE V19.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme C (paper F1), the failed test stated as
      % miscoverage at the tested truths; theme A, its size. Source: note sec_5d.tex sec:coverage-5d (b3fc422b, :357-366:
      % UCB < 0.66 / < 0.94; tilt 51 and 42 of 153, as low as 0.060; nominal two at 95%, lowest 0.850; "1,200
      % pseudo-experiments over three truths", of which two enter the verdict); OUTCOME-20260925-s5c-tier-s-futility-fail.md
      % :30-36, :41-43; state/s5c/tier_s/interim_400.json (aa574c17...), VL150.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): "This motivates the full-chain calibrated
      % comparisons of Sec. VI" merged into the end of Sec. V (sec:uncertainty-status), which now follows.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): section moved before the central values
      % (director's structure decision, after the GPT outline analysis), so that the reader knows what the uncertainty
      % supports before the results; register ("exception to the criteria" rephrased; same content).
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P5, one sentence. The movements at
      % 40 and 80 throws (\seedEffectNforty, \seedEffectNeighty) and the noise floor (\floorNforty, \floorNeighty) moved to
      % the note: sec_5d.tex sec:eavailw-adopted, "What the covariance supports", item 2.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme A (paper F4; also resolves pass-1 F8,
      % "bounded component exceeded"). Source: note sec_5d.tex "Reporting definitions for a five-dimensional measurement"
      % (RD3 = the 39 EW cells, the fallback; bounded model component = the largest shift over five generator-sized truth
      % departures, median 13.4%; target median 68% half-width at most 10%; "about 10--13% per coarse joint cell, ...
      % comparable to the generator differences a user would need to resolve"); RECORD-20260927-s5p-stage2-exit.md sec. 4
      % (VL155) :127-133, :139, :144. RD2's model median is 9.6% (it fails only with the 1.4% normalization), so the text does
      % not say the model component alone exceeds 10% in every definition. "Came from the same study" (chronology) moved to
      % the note (sec_5d.tex: "The calibrated joint tests ... were the separately admitted inference branch").
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, the section's two repeated
      % "descriptive; no significance is assigned" statements (Fig. 2 and Fig. 3 paragraphs) collected here once.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme A (paper F7), the fine grid. Source:
      % note sec_joint.tex sec:joint5d-design (b3fc422b, :27-33: "the analysis binning of sec:method-binning,
      % 14x16x7x7x6 bins"); nd-unfolding/s5p_stage1_inspect.py:38-44 (FINE); RC4 fine-to-J map U (109, 65856),
      % audit-20261008 mapping-notes-C.md:25; the 14 x 16 muon bins are the published binning (themeA-sources, F7).
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P8. The count of compared quantities
      % (\jtRecompRows) moved to the note: sec_joint.tex sec:joint5d-frozen ("agrees with the production evaluation on all
      % \jtRecompRows{} compared rows").
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P15, the choices made after results
      % were seen, collected in one paragraph. From VI A (design review; budget extension), VI C (the scan's, the recovery's
      % and the coarse-projection comparison's timing) and VI D (post hoc); the 2D learner choice stays at its claim (IV A).
      % Each source comment stays at its claim. Register: "the reviewers of the design" rephrased.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme A (paper F6), the rate. Source:
      % \jtMoneWnormMin/\jtMoneWnormMax (values_inference.tex:38-39); amendment 7 claims.rejection; note sec_joint.tex
      % sec:joint5d-conditions ("a design-review value whose calculation is not recorded"); provenance open (corrections
      % record G6b). This proxy rate per halving is a different quantity from the L2 ratio above.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P9; the scan's endpoint and its
      % limitation are stated once, in Sec. VI C (sec:joint-results).
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P15; the scan's timing is in Sec. VI A.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P7. Moved to the note, sec_joint.tex
      % sec:joint5d-lost: the worst-case sensitivity ("had every interrupted draw exceeded the observed statistic, no test
      % would have been rejected"), the independent review of the procedure, and the 16-of-16 determinism check. The timing
      % (after the decisions, outside the decision rule) is in Sec. VI A.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, P15 (the comparison's timing is in
      % Sec. VI A); theme C (F15), the rejections are of the hybrid null hypotheses.
      % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2): theme B, the conclusions' repeated limitation
      % list merged into the three kinds of result; theme A (F4) as in the Introduction (source there); theme C (F15); the
      % lost-pseudo-experiment recovery is stated once, in Sec. VI C.
```

Mid-line block: `== new lines with a mid-line comment (text before an unescaped %)` / `[SAME] none`.

**Each difference explained:**
- numerals lost:
  - `2.12`, `21.09`, `2019`: the generator versions in the abstract's parenthetical list, now in the body only
    (Sec. II and VII A print them);
  - `16`: "reproduced 16 completed pseudo-experiments", moved to sec_joint.tex:279;
  - `5.2`: condition (i)'s scan endpoint (P9), kept in VII C as 5.25/5.17 and in sec_joint.tex:241;
  - `80`: Sec. V's "with 40, 80, and 160" list, merged into "between 40 and 160" (P5; values in sec_5d.tex:510–514).
- numerals gained:
  - `10` ×8, `13` ×4: F4, "about 10–13% per cell" and the 10% target, in the abstract, Intro, Sec. V and Conclusions;
  - `13.4`, `39`, `68` (one of two): F4 in Sec. V;
  - `14`, `7` ×2, `6`, `3`: F7, the fine grid. The `3` is the subscript of `q_{3}`; `16` in `14\times16` is not
    counted by the checker's regex;
  - `400`, `51`, `153`, `42`, `0.06`, `0.85`, `95` ×2, `68` (the other): theme A / F1, the 5D coverage test in IV C.
- value macros lost:
  - `jtRecompRows`: P8, moved to sec_joint.tex:114;
  - `sprojMeasured` ×1, `seedEffectNforty`, `seedEffectNeighty`, `floorNforty`, `floorNeighty`: P5, moved to
    sec_5d.tex:510–514. `\sprojMeasured` remains once, with `\sprojBound`.
- value macros gained: `jtMoneWnormMin`, `jtMoneWnormMax`, theme A F6 (VII B (i)).
- cite keys gained: `AnalysisNote2026` ×1, the IV B pointer for the shortened old-band test ("the analysis note gives
  the full test"). `TwoDFollowup2026` is kept.
- ref targets lost: `fig:joint` ×1, the removed repeat "As for Fig. 2, these comparisons are descriptive".
- ref targets gained:
  - `sec:uncertainty-status` ×3: Intro pointer, IV C end, central-value scope sentence;
  - `sec:joint` +1 (net): Sec. V references the joint tests twice; IV C's reference moved there;
  - `sec:repro2d`, `sec:response` and one `sec:joint-results`: the P15 paragraph. Condition (i)'s
    `sec:joint-results` is kept as a pointer.
- labels: SAME (18). Comment lines: all 255 base lines survive; 93 added. Each added line is a pass-2 marker or a
  source comment on its own line.

#### 7. F-list (flagged, not made)

| id | location | base text | proposed text | why |
|---|---|---|---|---|
| F-p2-1 (triage-verified text error, GPT 4) | VII A, `paper_body.tex` "Calibration proceeded in batches … until both of a null's decisions were determined, that is, until each interval lay entirely on one side of its threshold" | stopping is described with the 95% decision interval | "…until both of a null's decisions were determined: a null stopped when a 99.5% Clopper–Pearson look interval of $k/B$ lay entirely on one side of each of its thresholds (and a precision tier was met); the decision itself uses the 95% interval above" | triage §B: the stopping rule uses the 99.5% look interval (nd-unfolding/s5p_inference.py:89–114), the decision the 95% CP gate (:127–155). The note's sentence (sec_joint.tex:99–101) names no interval, so it does not conflate the two |
| F-p2-2 (triage, GPT 4) | VII A P15 paragraph: "and the Monte Carlo $p$ values remain valid at the number of pseudo-experiments reached" | as quoted | "and, because a rejection requires the 95% Clopper–Pearson upper bound to lie below its threshold, each decision's size stays below that threshold for any stopping up to 1999 pseudo-experiments (Holm familywise rate ≤ 0.89 α)" | triage §B: the bare $(k+1)/(B+1)$ at a data-dependent $B$ is not guaranteed super-uniform; the decisions are conservative. A new statistical claim from a new calculation (scratchpad triage-calc/seqsize.py), so it is for Joseph. Also in sec_joint.tex:111–112 |
| F-p2-3 | VI, opening: "The $\Eavail$ dimension provides an independent view of the established low-recoil discrepancy" | "independent" | "shows" (GPT r1: same data, correlated reconstructed information) | possibly overstates; changing it weakens a claim (C3) |
| F-p2-4 (triage m2, m4) | II: $W=\sqrt{M^2+2M(E_\nu-E_\mu)-Q^2}$ | $Q^2$ undefined; "struck-nucleon mass $M$" | "…with $Q^{2}=4E_{\nu}E_{\mu}\sin^{2}(\theta_{\mu}/2)$ and the mass $M$ of a struck nucleon at rest" | an omission, not wrong; adds content (CVUniverse.h:385–410) |
| F-p2-5 (P10, carried) | Fig. 4 legend "most conservative claim variant"; the caption glosses it | as is | relabel the legend "most conservative shifted null"; drop the caption gloss | the figure producer is out of scope; the caption gloss is kept so that the legend stays defined |
| F-p2-6 (F9, carried) | Sec. V "We nevertheless use this covariance" | what it is used for is not said | name its uses (it is the "quoted" σ in IV C's "about one quoted standard deviation" and "within the quoted total uncertainty in about half of those cells", per VL154 A4 "within the adopted sigma") | a new claim; for Joseph |
| F-p2-7 | gate constraint on P3 | IV B keeps D2's history and three gate-bound values | if the director wants the old-band numbers out of the paper, `check_sec4_receipts.py` (three CHECKS rows) and D2's must-carry ruling must change first | not my files |
| F-p2-8 (P1, carried) | III "The use of AI tools in this work is described in the Acknowledgments." | as is | cut (GPT r1) | not in the pass-2 theme-B list |

The pass-1 F-list items F1, F4–F8, F12 and F15 are now made (themes A and C). F3 was done earlier. F9, F10, F11, F13,
F14, F16 and F18–F22 stand.

#### 8. Build, pages, abstract

- `$S/build_copy.sh p2-paper $W` gave **rc=0** (`$S/build-p2-paper.out`). All four targets report "written by this
  run; no unresolved references". The containment gate gives SELF-TEST PASS and RESULT PASS. The Sec. IV receipt gate
  gives SELF-TEST PASS (18 perturbations rejected) and **SEC4-RECEIPTS PASS (15/15)**. The PDF text has no "??". The two
  overfull hboxes (the title block, 11.06 pt, and Table I, 0.71 pt) are the base's own.
- Pages: main_paper **12**. The text shrank: page 12 now holds references [25]–[39] only, against [20]–[39] in the
  pass-1 final PDF. That is about a third of a column, but not enough to lose the page. main_note 123, main_primer 13,
  pet_note 26 (these include the other agents' edits).
- Abstract words:
  - **old 233** (the director's count; 235 by raw `wc` of the source);
  - **new 155** by `wc` of the source, with comments stripped; 158 counted from the PDF text, where hyphenated
    line-breaks inflate the count.
- I read the rebuilt `builds/p2-paper/repo/docs/analysis-note/main_paper.pdf` in full, as pdftotext (`builds/p2-paper/paper.txt`).
  - The section order is I–VIII, with V the uncertainty status.
  - Every cross-reference resolves: Sec. V, VII B, VII C, VII D, IV A, Figs. 1–4, Table I.
  - No comment text leaks into the PDF, and no sentence is broken.
  - The mixed "10 %" (from \SI) and "10–13%" spacing follows the base's own mix ("1–2%", "5%").

Report: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/p2-paper.md`

1. The abstract is 233 → 155 words. It carries the hybrid-null rejections (F15), the recoil-response and fine-grid
   conditions, no demonstrated added discrimination, central values only, and the 10–13% model dependence against
   the 10% target.
2. The uncertainty status is moved before the central values. The note's coverage numbers, fine grid, halving rate,
   the fallback's 13.4% versus 10%, and the 74%'s estimator are added (theme A). The 5D coverage test is stated as
   miscoverage at the tested truths (F1).
3. Theme B: P2, P4–P9 and P16 moved, each with its note location; P3 is partly moved because D2 and the Sec. IV
   receipt gate bind three values. One P15 paragraph collects the post hoc choices, and the learner choice stays at its
   claim. Nothing needs a new note home.
4. Invariance: labels SAME and all 255 base comment lines survive. Every numeral, macro, cite and ref difference is
   explained as theme A, a note move, or a merge. No mid-line comment.
5. The build has rc 0, both gates PASS (SEC4 15/15), no unresolved references, and 12 pages (shorter, still 12).
   F-list: two triage-verified statistical-text errors (F-p2-1, F-p2-2) and one gate constraint (F-p2-7) are for the
   director.

---

## P17. Claude: primer integration (sha256 `fedefb315788ffd0…`)

### Plain-language pass 2: primer integration (themes A and B, Section 3 reorder, abstract)

Writer: primer integration, pass 2. Worktree `wt-plain2` at HEAD `b3fc422b` (pass-2 base `main` `34650231`).
Files edited: `docs/analysis-note/primer_body.tex`, `docs/analysis-note/main_primer.tex` (abstract). Nothing else
touched; no git writes. The worktree's other modified file (`paper_body.tex`) belongs to the paper writer.
Every changed site has `% plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2)` on its own line;
29 such markers. All 76 base comment lines survive verbatim.

#### 1. New structure, and why

| § / heading (unchanged headings in plain type) | content now | change |
|---|---|---|
| 1 What was measured, and why it is hard | unchanged | — |
| 2 The method, in plain language; *What the checks tell us* | unchanged up to Table 1; the "One more distinction" paragraph keeps selection vs inputs and the tree learner only | PET sentences and the truth-cut sentence moved to §3 (P-new-3); the selection-table pointer moved to the note (P9) |
| **3 What we found**: overview list | 6 items, each stating the finding and only the caveat needed not to misread it (§5 below); the intro sentence now gives the section's order | shortened items 1, 3, 4, 5; item 2 gains the ~10 % number; item 4 names the two main conditions and the coarse-projection limit |
| *First, a trust check: reproduce a known result* | 2D agreement, uncertainty sizes, post hoc learner choice, budget limits, coverage, earlier 91 % test, untested quoted bars; Fig. 2 | repaired-defect list → one clause + note (P1); Fig. 2 caption identifies the red curve (F-new-8); Fig. 2 placement `[tbp]` |
| *Then, measure more at once --- and rediscover known physics* | unchanged prose; Fig. 3 | Fig. 3 caption drops the beam-spectrum repair clause (P8) |
| *A new puzzle for the tuned simulation* | adds the corner-excess shares (F-new-2); seed movement rounded to "about 6 %"; Fig. 4 | theme A |
| *Limits on the multi-quantity results* (heading kept, so the two pointers to it stay valid) | **ranked**: a lead paragraph names the three limits in order — (1) the unfolding follows a changed truth only partly (biases not in the uncertainty); (2) the uncertainty has not met its pre-set requirements and depends on the learner's seed; (3) a pre-set numerical-stability test failed — then one paragraph each (run-in headings *Biases in following a changed truth*, *An uncertainty that has not been validated*, *Numerical stability*), then the narrower detector-coverage point and the 2D-independence sentence | was a sequence of 9 paragraphs in discovery order; compressed, regrouped by limit, P6/P7 compressed |
| *A joint test of five simulations* | hypotheses (now called "hybrid" where defined); **new two-sentence calibration explanation**; result; lost pseudo-experiments; conditions in prose with the top two named; post hoc projection paragraph | six-item list → prose + note (P4); κ paragraph → one sentence + note (P5) |
| *Alternative representations and signal definitions* | PET, briefly (what it is, moved from §2; one paragraph of outcomes with all five cites; Fig. 5 kept); then the extended signal definition (σ_ext to two figures; Fig. 6) | PET chronology/design narrative → PET note (P2) |
| 4 The takeaway | adds the joint-test result with its conditions | — |

Why this order: both outside outlines (sol-outline §6, gemini-outline §6) and the pass-1 readers found that the overview
pre-listed every qualification, the limits came as an unranked five-page retrospective, PET history displaced the
joint test, and the takeaway omitted the joint test. The order now is: what was found and how firmly (overview, then
the 2D finding with its own caveats, then the multi-quantity findings) → the limits that matter most, ranked → the
joint test (which a reader can only interpret after knowing why the 5D error bars are not used) → PET briefly → the
extended signal definition → takeaway. The 2D caveats stay with the 2D finding (C2, kept in pass 2), so the ranked
limits section is about the multi-quantity results, which is where they bind.

#### 2. Outside-model ideas adopted and errors rejected

**Adopted (each checked against the base primer, `paper_body.tex` and the note):**

| idea | from | how checked |
|---|---|---|
| Order: findings → ranked limits → joint test → PET optional/brief → extended signal; joint test in the takeaway | sol-outline §6, gemini-outline §6, both rewrites | the brief's own instruction |
| Name three limits, in the order bias / unvalidated uncertainty / stability | sol-primer "The three main limits" | each limit and its wording is the base primer's (base L432–476); "fails a stability test fixed in advance" is base L455–456 |
| Conditions as prose, the calorimetric response and the sub-grid error named first, the others listed in one sentence | sol-primer, gemini-primer | all six conditions still named (base L509–518); "conditional on the simulation's hadronic response" is the note's `sec_joint.tex:375` |
| κ reduced to "probes this in one direction only and gives no bound" | sol-primer | base L540–541; note `sec:joint5d-kappa` |
| PET reduced to one paragraph with all five cite keys | sol-primer | every cite key kept; outcomes checked against `sec_pet_campaigns.tex` (§3 below) |
| Fig. 2 red-curve clause | both rewrites (themeA F-new-8 text) | producer `plot_2d_threeway_fig13.py:200`; legend read in the rebuilt PDF ("GENIE 2.12.6 + MnvTune v1") |
| Corner-share sentence | gemini-primer (themeA F-new-2 text) | `sec_eavailw.tex:49-53` (67 %, 83 %, 22 %) |
| Takeaway sentence on the joint test with its conditions | sol-primer takeaway | paper abstract and `paper_body.tex:993-1002` |
| Abstract shape (finding + one caveat each; joint test "under stated conditions") | sol-primer abstract | §8 |

**Rejected (errors or unsupported content):**

| proposal | model | why rejected |
|---|---|---|
| "rejects five widely used neutrino event generators" (abstract, takeaway) | gemini | drops "hybrid"; the decisions test the hybrid null (`paper_body.tex:638, 717`) |
| "statistical intervals failed a pre-registered coverage test" as the reason for central values only | gemini | conflates the untested 2D bars with the 5D variant's failed test |
| "sensitivity to the starting simulation" as a reason | gemini | not the base's reason (seed dependence and unvalidated uncertainty) |
| "Extending … to up to five variables without binning — a first at MINERvA" in the abstract | gemini | moves the scoped "first" claim into the abstract and attaches it to multi-variable measurement; the abstract carries no "first" |
| 51/153, 0.06, 13.4 %, "up to 74 %" in the primer | gemini | paper-side theme-A numbers (paper F4, IV C, F12); not in the primer's list; themeA advises against the bare 74 % here |
| "GiBUU (61 % below data …)" | gemini | wrong direction: the data are 61 % above GiBUU |
| σ_ext "(Fig. ref{fig:primergen})" | gemini | wrong figure |
| "pre-registered" | gemini | not the field's or the base's term ("fixed in advance") |
| dropping the remedies and the lost-pseudo-experiment check | gemini | limitations/disclosures; kept, compressed |
| attributing the ~10 % to "a deterministic variant" and the 16–31 % to "the joint-test estimator" | sol | the primer body names neither; the 16–31 % attribution is not confirmed by the record I read (`sec_5d.tex` "Unfolding-model dependence"); kept the base wording |
| cutting "This is the kind of localized discrepancy that points theorists …" | sol | a change of claim strength; listed as F-p2-2 instead |
| "Similar sizes do not establish …" (new sentence) | sol | the base already says "We make no coverage claim"; it would add words |
| `round-mode=figures,round-precision=1` | both | works, but the brief prefers `places/0`; used `places/0` (renders "6 %") |
| moving Fig. 5 out | sol (P3) | the brief's "keep \label names"; kept with a shorter caption (F-p2-3) |

#### 3. Moved out (theme B)

Every location below was confirmed by grep in the worktree at `b3fc422b`.

| item | content leaving the primer | where it is carried |
|---|---|---|
| P1 | the four repairs (same truth inputs, the double-counted pion variation, background-simulation statistics, selection-complete re-runs) | note `sec_systematics.tex` `sec:uq-2d-construction` (l.205–255); the primer keeps "rebuilt without them; the analysis note lists the repairs" and the cite `TwoDFollowup2026` |
| P2 | PET chronology and design narrative: the ten-iteration first study; 31 % → about 90 % / 86 % recovery; the robustness failure being statistically unresolved; 68 %→90 %/26 % and 95 %→79 % coverage; six-fit bootstrap and the additive-variance/√6 diagnosis; unmeasured generator-case/data-scale coverage; per-test learner ranking, binned methods on the 1D tilt; detector-step underfitting, missed-event extrapolation, exact weights, untested truth inputs | PET note (`pet_note.tex` → `sec_pet.tex` → `sec_pet_campaigns.tex`): `sec:pet-campaigns` (l.2–175, `tab:pet-improvement`, `tab:pet-final-coverage`, "What the saved intervals diagnose"), `sec:pet-gbdt-paired` (l.206–300, incl. "Where generator recovery is lost"). The primer keeps one paragraph with all five cite keys |
| P3 | Fig. 5 | **not moved** (label rule); caption shortened, and it now carries the "separate configuration" clause from the body |
| P4 | the six-item list | note `sec_joint.tex` `sec:joint5d-conditions` (l.118–178); paper `sec:conditions`. All six conditions are still named in prose |
| P5 | κ paragraph (meaning of κ; 5.26 / 5.17; "ambiguous, not a clear non-rejection") | note `sec_joint.tex` `sec:joint5d-kappa` (l.234–247); paper `paper_body.tex:775` |
| P6 | remedies paragraph | **compressed, not removed** (one sentence keeps all three limits); note `sec_5d.tex` l.250–262 (no tradeoff; coarser cells estimate different integrals), l.316–324 ("no … guaranteed bias bounds") |
| P7 | "made with a wrongly sampled beam spectrum" | note `sec_5d.tex` l.67–71 ("mis-sampled flux … not a measured GiBUU–GENIE difference"); the primer keeps "a test of chosen size, not a measured difference between them" |
| P8 | Fig. 3 caption "rebuilt with a correctly sampled beam spectrum" | note `sec_3d.tex` l.239–245, `sec_eavailw.tex` l.97–98, l.139 |
| P9 | "A table in the companion analysis note lists … signal events only" | note `selection_features.tex` `tab:selection-features` (input by `sec_experiment.tex:69`); "signal events only" is kept in the primer's PET paragraph |
| P-new-3 | PET description and truth-cut sentence in §2 | moved within the primer: to the PET paragraph and the signal-definition paragraph |

**NEEDS HOME:** none.

#### 4. Numbers added (theme A)

| number as printed | where | source (comment in the source beside it) |
|---|---|---|
| "about 10 %" (typical cells under a changed truth) | overview item 2 (the body already had it) | median 9.7 %: `sec_5d.tex:73`; `OUTCOME-20260925-s5n-stage1-development-fail.md:76` (F-new-1) |
| "about two thirds … most of it at high W … about a fifth" | puzzle paragraph | `sec_eavailw.tex:49-53` (67 %, 83 %, 22 %); `paper_body.tex:571-574`, release arrays (F-new-2). Shares only, in words; no ratio, so the low-W caveat themeA requires for a ratio does not apply |
| "about 6 %" (seed shift of the uncertainty) | limits, uncertainty paragraph | `\SI[round-mode=places,round-precision=0]{\sprojMeasured}{\percent}`; `values.tex:407`, GRADE json s_proj 0.06145 (F7) |
| "at most about 6 % of their own uncertainty" | puzzle paragraph, Fig. 4 caption, uncertainty paragraph | `\SI[round-mode=places,round-precision=0]{\cvMoveOverSigmaMax}{\percent}`; `values.tex:458` (F7). The words keep the two 6 % objects distinct |
| σ_ext ≈ 4.5 × 10⁻³⁸ cm²/nucleon | signal-definition paragraph | `\SI[round-mode=figures,round-precision=2]{\fpsSigma}{cm^2/nucleon}`; `values.tex:273`, `VALIDATION_LEDGER.md:1615` (F7) |
| GENIE 2.12.6 / 2.12.10 in Fig. 2 caption | Fig. 2 | `plot_2d_threeway_fig13.py:200`, `paper_body.tex:110-111` (F-new-8) |

Rendering confirmed in the rebuilt PDF (siunitx 3.3.12): "about 6 %", "at most about 6 % of their own uncertainty",
"σext ≈ 4.5 × 10−38 cm2 /nucleon".

#### 5. Overview items and the caveat each carries

| item | caveat carried |
|---|---|
| A published result, reproduced | a shape difference remains with the published correlations; its size depends on the learner implementation, chosen after both comparisons were known (post hoc); some effects not in the budget, no coverage claim; the quoted statistical bars have had no coverage test (V4) |
| More quantities at once (R2) | central values only; end-to-end biases not in the quoted uncertainty (about 10 % under a changed truth; background removal); the uncertainty has not met its pre-set requirements, documented exception, error bars not shown right; the one direct coverage test (on a variant) failed; no significance because the uncertainty depends on the seed |
| Known and new features | in these central values; the low-recoil match is "resembling"; 2p2h fills part without establishing the cause; no significance for either feature (seed detail now only in the body, at the claim) |
| A joint test of five simulations | a separate inference, not a measurement; hybrid form; six stated conditions; the two main conditions named (no calorimetric recoil-response uncertainty; unbounded sub-grid error); no added discrimination over matched coarse projections shown |
| A neural network on raw detector data | method development; no design met every requirement; no cross section or error bar |
| A wider signal definition | same selection, no added measured events; preliminary; small detector-supported part, larger simulation-dependent extrapolation |

#### 6. Invariance check, primer block (verbatim)

`python3 -I …/check_invariance.py $W 34650231 > $S/inv-p2-primer.out; echo rc=$?` → **rc=1**. The rc comes from the
primer block's numeral and ref differences below, and from "files changed outside scope", which lists the
director's committed `b3fc422b` files and the paper/note writers' files (none mine).

```
== primer
  [DIFF] numerals: lost {'95': 1, '31': 1, '5.26': 1, '5.17': 1, '90': 2, '86': 1, '68': 1, '26': 1, '79': 1}  gained {'10': 1, '2.12': 2, '2': 1, '0': 4}
  [SAME] value macros (13)
  [SAME] cite keys (7)
  [DIFF] ref targets: lost {}  gained {'fig:primergen': 1}
  [SAME] labels (3)
  [SAME] comment lines: all 76 base lines survive
  [INFO] comment lines added (75):
      29 x % plain-language pass 2 (DECISION-20261018-joseph-plain-language-pass2)
      46 x source/route comments (Theme A sources, Theme B note locations, calibration sources, Fig. 2 placement)
== new lines with a mid-line comment (text before an unescaped %)
  [SAME] none
```
(The 75 added lines are listed in full in `$S/inv-p2-primer.out`; tallied here.)

| difference | explanation |
|---|---|
| lost 31, 90, 86 | PET recovery fractions 31 % / about 90 % / 86 %: theme B P2, PET note `sec:pet-campaigns` (0.316/0.306, 0.895, 0.863) |
| lost 68, 90, 26, 95, 79 | PET interval coverage (68 %→90 % overall, 26 % low acceptance; 95 %→79 %): theme B P2, `tab:pet-final-coverage` (0.896, 0.257, 0.789). The "95" lost is that one; the 2D "95 %" and Fig. 5's "95 %" remain |
| lost 5.26, 5.17 | κ endpoints: theme B P5, note `sec:joint5d-kappa`; paper `paper_body.tex:775` |
| gained 10 | "about \SI{10}{\percent}" in overview item 2: theme A F-new-1 |
| gained 2.12 ×2 | "GENIE 2.12.6" and "2.12.10" in the Fig. 2 caption: theme A F-new-8 |
| gained 0 ×4, 2 ×1 | siunitx `round-precision=0` (four uses) and `=2` (σ_ext): rounding options, not printed numerals (theme A F7) |
| gained ref fig:primergen | the Fig. 2 caption's pointer to Fig. 3 (F-new-8) |

No primer line is in the mid-line-comment block.

#### 7. F-list (flagged, not made)

| id | site | proposal | why not made |
|---|---|---|---|
| F-p2-1 | puzzle paragraph | add the paper's caveat (`paper_body.tex:577-579`): the high-E_avail, high-W corner "is also where the regularization bias … is largest" | a caveat the primer does not state at this claim; it weakens the corner finding, so for the director |
| F-p2-2 | puzzle paragraph, last sentence | "This is the kind of localized discrepancy that points theorists toward …" (sol: exceeds its support, given no significance and the unmeasured share shift) → cut, or "This is a localized feature that only the joint map shows." | change of claim strength (base text) |
| F-p2-3 | Fig. 5 | move to the PET note (P3; `fig:pet-gbdt-paired` already carries it) and drop "Figure 5 shows …" | removes the label `fig:primerpet`, against the brief; would save about half a page |
| F-p2-4 | abstract | name the two joint-test conditions | budget (155 words); the overview, body and takeaway name them |
| carried | F5 ("The published numbers are unchanged by this check"), F8, F9 ("yet"), F10, F13, F-new-6, F-new-7 | unchanged from pass 1 | still open for Joseph/the author |
| closed | F-new-5 (√6 sentence base defect) | the sentence left the primer with P2; the PET note gives the correct reasoning (`sec_pet_campaigns.tex` l.158–160) | — |

#### 8. Build, pages, abstract

`$S/build_copy.sh p2-primer $W` → **rc 0**. All four PDFs "written by this run; no unresolved references";
`main_primer.log` has 0 undefined references/citations; no "??" in the PDF text. Gates: containment SELF-TEST PASS,
RESULT PASS (strict); Sec. IV receipts SELF-TEST PASS (18 perturbations rejected), SEC4-RECEIPTS PASS (15/15).

| PDF | pages |
|---|---|
| main_primer | **13** (base 14) |
| main_paper | 12 |
| main_note | 123 |
| pet_note | 26 |

Primer: `$S/builds/p2-primer/repo/docs/analysis-note/main_primer.pdf`, sha256 `0c5f6d7b3de09e86…`. The text alone
gave 14 pages, because the `[H]` Fig. 2 (nearly a full page) left page 5 half empty. With `[tbp]` for that figure
the primer is 13 pages, and Fig. 2 sits at the top of the page after its text. Rendered words: whole primer
7042 → 6634; Sections 3–4 5584 → 5274 (pdftotext counts, including figure-label text). The cut is modest because the
pass moved history and kept every limitation, compressed and ranked.

**Abstract:** 130 → 155 words (source count, as for the base; rendered 131 → 156). It adds the joint test (hybrid,
under stated conditions), the untested 2D statistical bars, and "central values only". It drops "with a different
unfolding method" (still in the body and takeaway), and merges the two signal-definition sentences into one.
"Close reproduction" (ruling F12) is now "closely reproduces"; "more practical than" (ruling F2) is kept, and so is the
ruling comment.

I read the rebuilt primer PDF in full. All changed sites read as intended, with no stray comment text and no broken
sentences.

---

Path: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/p2-primer.md`

1. Section 3 now runs: findings, the ranked limits (bias under a changed truth; an unvalidated, seed-dependent uncertainty; a failed stability test), the joint test, PET in brief, then the extended signal. The takeaway now includes the joint test and its conditions.
2. The joint test gains a two-sentence calibration explanation taken from the paper. The six conditions are now prose, with the top two named. The κ scan, the PET chronology and the repaired-defect list moved to the note or the PET note (all homes confirmed; none needs a home).
3. Theme A: the ~10 % changed-truth bias, the corner-excess shares, "about 6 %" twice and σ_ext ≈ 4.5×10⁻³⁸ (rounded by siunitx from the same macros), and the Fig. 2 red curve (Tune v1 on GENIE 2.12.6). Each has a source comment.
4. Invariance: all 76 base comments survive. The numeral differences are exactly the theme-B PET/κ values out and the theme-A values and rounding options in. No mid-line comments.
5. Build rc 0, no unresolved references, gates PASS. Primer 14 → 13 pages; abstract 130 → 155 words. Four new flags for the director (F-p2-1 to F-p2-4).

---

## P18. Prompt: outside referee report (round 3; abstract length updated) (sha256 `61a432e2e617b854…`)

Do not use any tools, commands or files: everything you need is in this message. Answer directly, in text, in full.

You are an experienced referee for Physical Review D in experimental neutrino physics: you have worked on neutrino-nucleus cross-section measurements (MINERvA, T2K, NOvA or MicroBooNE), know iterative/D'Agostini unfolding and its regularization, multi-universe systematic uncertainties, covariance-based chi-squared tests, pseudo-experiment calibration and coverage, and the OmniFold method. You have never seen this project.

Below is the full text of a manuscript submitted to PRD (extracted from the PDF, so equations and figure text may be garbled). Write a referee report.

Part 1 — the standard report: summary of what the paper claims; assessment of significance and novelty; major comments; minor comments; recommendation. Be candid. Judge the physics and the support for each claim, not only the writing.

Part 2 — presentation, because the authors specifically asked for it. They worry the paper is written in an over-defensive, process-record register (stacked negations, internal project vocabulary, project history in the body) rather than the way PRD papers in this field are usually written. For each section: does it read like a PRD paper? Quote the worst passages exactly and show how an experienced author in the field would write the same content. Keep every limitation the authors disclose — do not make the paper claim more than it does — but say where a limitation is stated more often, or more prominently, than it deserves.

Part 3 — the abstract. It is about 155 words. (a) Which of its sentences carry the paper's headline results, and which are qualifications? (b) Write the abstract you would expect for this paper in 120–160 words, in PRD style, keeping the results and only the limitations a reader must know not to misread them. (c) List what you dropped and where in the body it should be stated instead.

Part 4 — anything else you think the authors need to hear.

---

## P19. X3 Gemini 3.8 Flash: referee report on the pass-2 paper (27edd449) (sha256 `91c0b8ed7b7bee58…`)

### PHYSICAL REVIEW D — REFEREE REPORT

**Title:** Multidimensional unbinned unfolding of MINERvA inclusive charged-current neutrino data: validation and calibrated model tests  
**Authors:** Joseph Bailey and Benjamin Nachman  
**Manuscript Ref:** PRD / [Open Data Application]

---

#### PART 1 — STANDARD REFEREE REPORT

##### 1. Summary of Claims
The manuscript presents the first application of an unbinned, machine-learning-based deconvolution technique (OmniFold) to experimental neutrino-nucleus scattering data, using the MINERvA medium-energy $\nu_\mu$ charged-current (CC) inclusive sample on hydrocarbon ($1.057 \times 10^{21}$ POT, $\langle E_\nu \rangle \approx 6\text{ GeV}$).

The primary claims and results are:
1. **Two-dimensional benchmark:** OmniFold reproduces the published MINERvA double-differential cross section in muon kinematics, $d^2\sigma/(dp_T\,dp_\parallel)$, with an integrated cross section agreeing within 1.1% and 95.6% of bins agreeing within 10%, though with an indicative $\chi^2/\text{ndf} = 2.65$ against the published covariance matrix.
2. **Higher-dimensional extension:** The unfolding is extended up to five simultaneous kinematic observables $(p_T, p_\parallel, E_\text{avail}, q_3, W)$. The authors report central values only for 3D, 4D, and 5D, showing qualitative agreement with the established low-recoil ($2\text{p}2\text{h}$) enhancement and exploring high-$(E_\text{avail}, W)$ event distributions.
3. **Methodological characterization of OmniFold in neutrino kinematics:** The authors perform extensive stress tests, revealing:
   - A background subtraction bias (up to 4% in high-$W$ cells with standard purity-weighting), which is mitigated by an unbinned negative-weight classifier refinement.
   - Significant regularization bias (16% to 74% in kinematic tails) when recovering truth distributions that differ substantially from the simulation prior (e.g., GiBUU vs. GENIE).
   - Instability under GBDT random training seeds (e.g., 6.1% movement in projected uncertainty; one unit of $\chi^2/\text{ndf}$ in the 2D benchmark).
   - Frequentist coverage failure for statistical intervals under shape tilts (coverage dropping as low as 0.06).
   - Intrinsic model dependence of 10–13% per cell, preventing the authors from quoting a 5D cross-section measurement that satisfies their pre-set 10% precision target.
4. **Calibrated hypothesis testing:** Because a direct 5D cross section with validated uncertainties could not be achieved, the authors design full-chain, pseudo-experiment-calibrated hypothesis tests of five generator models (MINERvA Tune v1, GENIE 2.12.10 CV, GENIE + Valencia 2p2h, NuWro 21.09, and GiBUU 2019). All five "hybrid null hypotheses" are rejected at the familywise $\alpha = 0.05$ level (Holm-adjusted).
5. **Caveats on model rejection:** The authors demonstrate that these rejections do not prove 5D unbinned discrimination over standard measurements, because:
   - Matched coarse 2D projections already reject the models at $p < 0.05$.
   - The calibration model lacks a dedicated calorimetric recoil-energy response systematic.
   - Sub-grid convergence below the fine binning is unproven.

---

##### 2. Assessment of Significance and Novelty
This is a sophisticated, exceptionally transparent, and cautionary paper. The neutrino community (T2K, MicroBooNE, SBN, NOvA, DUNE, and MINERvA) has debated moving away from classical binned iterative Bayesian unfolding (D'Agostini) toward unbinned ML methods to bypass the "curse of dimensionality" inherent in multi-differential response tensors. To date, however, demonstrations of OmniFold in neutrino physics have been restricted to mock data and synthetic detector studies (e.g., Huang *et al.*, PRD 112, 012008). 

This work represents the first application of unbinned unfolding to real neutrino data, but its true scientific importance lies elsewhere: **it is the first rigorous forensic audit of where unbinned ML unfolding encounters severe roadblocks in neutrino physics.** Unlike collider physics, neutrino scattering suffers from non-monochromatic beams, unobserved neutral particles, complex nuclear feed-down, and imperfect generator priors. The paper documents that OmniFold's prior-dependence, regularization bias, and training-seed variance are large enough to compromise nominal measurement uncertainties and interval coverage in 5D. 

The paper is novel, technically sound in its execution, and should be published in *Physical Review D*. However, it currently struggles with its identity: it oscillates between a physics cross-section measurement, an audit/post-mortem report, and a methodological critique. It requires a Major Revision to restructure its scope, re-frame its narrative, and resolve several key physics issues.

---

##### 3. Major Comments

###### 1. Paper Identity: Methodological Assessment vs. Physics Measurement
The manuscript presents 3D, 4D, and 5D "central values" but repeatedly insists that they cannot be interpreted as measurements because they carry no validated covariance, miscover in coverage tests, exhibit 10–13% prior dependence, and depend on classifier seeds. 
*Recommendation:* In PRD, presenting multi-differential cross-section plots and tables without valid uncertainties or covariance matrices creates immediate hazards for the community (e.g., phenomenologists reading numbers off plots to tune generators). The authors must formally designate this manuscript as a **Methods and Validation Study**. Central values in 3D–5D must be explicitly labeled as uncalibrated algorithmic demonstrations, and the authors should state unequivocally that these distributions should not be used in external neutrino cross-section fits or global nuclear model tunings.

###### 2. Statistical Compatibility of the 2D Reproduction ($\chi^2/\text{ndf} = 2.65$)
In Sec. IV A, the authors compare their OmniFold 2D result to the published MINERvA result on the *exact same dataset*, finding $\chi^2/\text{ndf} = 2.65$ (205 bins) evaluated against the published covariance matrix $V_\text{pub}$. The authors correctly note this is "indicative only." 
*Physics issue:* Evaluating $\Delta \sigma^T V_\text{pub}^{-1} \Delta \sigma$ between two unfoldings of the **identical data events** is statistically uninterpretable. Because both analyses unfold the same raw events, their statistical fluctuations are virtually 100% correlated. If two estimators are unbiased, their difference variance is $\text{Cov}(\hat{\sigma}_1 - \hat{\sigma}_2) = V_1 + V_2 - 2\,\text{Cov}(\hat{\sigma}_1, \hat{\sigma}_2) \ll V_\text{pub}$. A $\chi^2/\text{ndf}$ of 2.65 evaluated against $V_\text{pub}$ might actually represent a massive $>10\sigma$ procedural discrepancy between D'Agostini and OmniFold, or it could simply reflect the different regularizations. The authors must compute the statistical bootstrap of the *difference* on the data (resampling data events and running both estimators, or at least running pseudo-data with known truth) to give a meaningful metric of procedural compatibility.

###### 3. The Hadronic Recoil Systematic Loophole in Generator Rejections
The calibrated generator test in Sec. VII rejects all five generator hypotheses at $\alpha = 0.05$. Yet, in Sec. VII D, the authors disclose that the nuisance model entirely omitted the MINERvA calorimetric recoil-energy response systematic (derived from test-beam data, scaling up to 10% in low-recoil analyses). Crucially, the authors note that in the matched $(p_T, p_\parallel)$ projection—which does *not* rely on calorimetric recoil—GENIE CV is **not** rejected ($p = 0.48$). Therefore, the rejection of GENIE CV in 5D is driven entirely by the hadronic observables ($E_\text{avail}, q_3, W$), exactly where the leading detector response systematic was omitted from the calibration!
*Physics issue:* The exploratory $\pm 4\%$ constant recoil shift in Sec. VII D is insufficient: test-beam data showed hadron energy response is non-linear, particle-species dependent, and subject to passive-to-active absorber leakage. Without propagating a proper recoil-energy scale and resolution nuisance parameter into the pseudo-experiment calibration ensemble, the rejection of the physical generators cannot be claimed as a robust physics conclusion. The paper must tone down the headline claim of "generator rejection" and state clearly that this rejection is conditional on an incomplete detector nuisance model.

###### 4. Diagnostic of Regularization Bias and Coverage Failure
The paper discovers that OmniFold recovers only a fraction of large truth deformations (e.g., failing to recover GiBUU-like shapes with biases up to 74% at high $W$), and that 68% statistical intervals undercover drastically (down to 0.06). 
*Physics issue:* This is a critical result for experimental neutrino physics. Why does this happen? In collider physics, unbinned unfolding benefits from relatively sharp detector resolutions and high-efficiency selections. In neutrino interactions, $W$ and $E_\text{avail}$ suffer from large missing energy (neutrons), nuclear feed-down, and broad migration distributions. When the migration matrix is broad, the classifier density ratio in the denominator becomes severely regularized by early stopping (five iterations) and tree depth, causing the unfolded weights to stick stubbornly to the simulation prior. The authors should add physical commentary explaining that unbinned unfolding in neutrino physics is uniquely vulnerable to prior-pull because detector smearing is far more severe than in collider leptonic/jet observables.

###### 5. Lack of Added Value in 5D vs. Coarse Projections
The paper notes that testing matched $3\times 3$ coarse projections in $(p_T, p_\parallel)$ and $(E_\text{avail}, W)$ yields $p < 0.05$ for every model. Thus, the 5D joint unfolding did not provide demonstrable extra statistical power over simple, low-dimensional projections. The paper should state this upfront: if 5D unbinned unfolding introduces severe regularization bias, seed noise, and prior dependence, but does not increase hypothesis discrimination beyond standard 2D projections, what is the practical utility of scaling to 5D with present techniques?

---

##### 4. Minor Comments
1. **$E_\text{avail}$ Definition Constant:** In Eq. (1), the authors state that charged pions subtract an "inherited constant of 135 MeV rather than the charged-pion mass (139.57 MeV)," noting: "We have not corrected this constant." Please explain why this historical artifact was retained, or state whether this was hardcoded in the legacy MINERvA AnaTuple processing script.
2. **Run-Period Systematic Block:** The ad-hoc 7% step observed near $p_\parallel \sim 8\text{ GeV}/c$ across run periods is puzzling. Is this related to MINOS coil status, NuMI target degradation, or beam spot shifts? Citing known MINERvA operations or acknowledging this as an unresolved detector artifact is necessary.
3. **ML Architecture:** Sec. III mentions that a neural network in place of LightGBM changes the 3D cross section by 0.8% overall and 0.7–1.4% in projections. Was the MLP trained with continuous variables, and did it use the exact same feature set? A brief sentence on the MLP architecture (layers, activation, optimizer) should be included in the text rather than deferring entirely to the analysis note.
4. **Finite Sample Noise of Prior Generators:** The external generator predictions (NuWro, GiBUU) have their own finite Monte Carlo sample variances added to the test metric $\Sigma$. How large was the MC statistical variance relative to the data statistical variance in the coarse test bins?

---

##### 5. Recommendation
**Major Revision.** The paper provides an outstanding, mathematically rigorous service to the field by puncturing the naive assumption that unbinned ML unfolding is a turn-key solution for multi-differential neutrino cross sections. However, the manuscript must be recast: remove the defensive/audit prose, clearly classify the 5D results as algorithmic demonstrations rather than physics cross sections, and moderate the claims of generator rejection in light of the omitted recoil systematic.

---

#### PART 2 — PRESENTATION & REGISTER AUDIT

##### Overall Diagnosis
The authors' self-assessment is entirely correct. The manuscript is written in an **over-defensive, compliance-audit register**. It reads like an internal investigation, a legal defense brief, or a post-mortem report prepared for a laboratory oversight committee. 

Specific pathologies:
1. **Stacked Negations and Defensive Apologies:** Sentences are structured around what was *not* done, what *cannot* be claimed, or what *failed*, often compounding two or three negative constructions in a single sentence.
2. **Internal Audit / Laboratory Notebook Vocabulary:** Terms like "predefined precision target," "fallback definition," "computing budget," "lost seeds," "claim variant," "separately authorized release decision," and "allowance covers no other covariance" are completely foreign to PRD. They belong in an internal experiment note, an analysis logbook, or a software repository issue tracker.
3. **Repeated and Hyper-Prominent Limitations:** Every single section repeats that the 5D result has no uncertainties, that frequentist coverage is unproven, and that the recoil band is missing. In PRD, limitations are stated once, clearly, mathematically, and objectively in the methodology/discussion sections. Repeating them in every paragraph makes the text defensive rather than rigorous.

Below is a section-by-section audit with exact quotes and professional PRD rewrites.

---

##### Section-by-Section Review and Rewrites

###### 1. Title and Abstract
* **The Problem:** The abstract devotes more than half of its word count to stacked caveats and procedural disclaimers ("predefined 10% precision target," "have not been shown," "is not shown to discriminate").
* *(Detailed analysis and rewrites are provided in Part 3).*

---

###### 2. Section I (Introduction)
* **Diagnosis:** The introduction reads like a project log that is apologizing in advance for failing to deliver a 5D cross-section measurement.
* **Worst Passage (Lines 52–65):**
  > *"These biases, the dependence on the estimator’s random seed, and the untested or failed interval coverage limit the method, and the measured model dependence, about 10–13% per cell, prevents a five-dimensional measurement whose total uncertainties meet the 10 % precision target we set in advance (Sec. V). All ten calibrated tests, in total and in shape, reject the hybrid null hypotheses built from the five predictions at the 5% familywise level under six stated conditions (Sec. VII B). Two of them, the absence of a calorimetric recoil-response uncertainty and the undemonstrated convergence of the fine grid on which the null hypotheses are defined, limit their physical interpretation."*
* **Why it fails PRD style:** "predefined 10% precision target," "six stated conditions," and the bureaucratic cadence of "under two of them... limit their physical interpretation" read like an administrative report.
* **PRD Rewrite:**
  > *"While OmniFold successfully scales to five dimensions, closure and pseudo-experiment studies reveal key challenges for neutrino cross-section measurements: non-negligible background-subtraction bias, sensitivity to classifier initialization, and a 10–13% residual model dependence that dominates the uncertainty budget. Furthermore, statistical intervals exhibit undercoverage under truth deformations. Consequently, we report unbinned five-dimensional distributions as central-value demonstrations rather than formal cross-section measurements. To perform model comparisons without relying on ill-conditioned measurement covariances, we employ full-chain calibrated hypothesis testing. Although these tests reject five generator predictions at the 5% familywise significance level, we show that the rejections are sensitive to the hadronic calorimeter response model and sub-grid modeling assumptions."*

---

###### 3. Section II (Data, Signal, and Simulation)
* **Diagnosis:** Mostly standard, but marred by odd procedural confessions and defensive side-remarks.
* **Worst Passage (Col. 2, lines 17–23):**
  > *"Relative to the charged-pion mass, in a simulated sample it moves 0.67 % of events into another true-Eavail bin and changes no true-Eavail bin by more than 1.05 %; this effect has not been compared with the full covariance."*
* **Why it fails PRD style:** "We have not corrected this constant... this effect has not been compared with the full covariance." State what the definition is, quantify the impact, and move on. Do not apologize for software legacy choices.
* **PRD Rewrite:**
  > *"In Eq. (1), charged pions contribute their kinetic energy evaluated with an offset of 135 MeV, following the convention of Ref. [9]. In simulation, this definition shifts fewer than 0.7% of events across bin boundaries relative to the physical pion mass, altering bin populations by at most 1.0%."*

---

###### 4. Section III (Unbinned Unfolding)
* **Diagnosis:** Good technical explanation of purity vs. negative-weight background subtraction, but concludes with awkward self-justification regarding hyperparameter tuning and AI usage.
* **Worst Passage (Col. 2, lines 52–57):**
  > *"...and no hyperparameter search was performed on data: the nominal settings are scikit-learn defaults, with LightGBM matched to their capacity, and the refinement capacity of the joint-test estimator (below) was chosen in simulation closure studies."*
* **PRD Rewrite:**
  > *"Classifier architectures and hyperparameters were fixed a priori based on simulation studies to prevent tuning on data. Default tree capacities were used for both scikit-learn and LightGBM implementations, while the background-refinement network capacity was optimized using simulated closure tests."*

---

###### 5. Section IV A & IV B (Validation: 2D Reproduction and Uncertainty)
* **Diagnosis:** This is the most severely compromised section. It reads like an internal committee audit addressing an accusation of data snooping or p-hacking ("This choice, which replaced the exact-split result, was made after both comparisons were known..."). It then descends into defensive despair over the run-period block and bootstrap coverage.
* **Worst Passage 1 (Sec. IV A, col. 1, lines 34–42):**
  > *"We quote the LightGBM result as the central value, so that it uses the same estimator as its covariance. This choice, which replaced the exact-split result, was made after both comparisons were known. The two differ by a per-bin median of 0.98 % (maximum 12.2 %), and this learner dependence is not included in any term of the covariance."*
* **PRD Rewrite 1:**
  > *"We adopt LightGBM for the central cross-section result to maintain algorithmic consistency with the ensemble-based covariance matrix evaluation. An alternative exact-split decision-tree implementation yields consistent results, differing by a median of 0.98% per bin (peaking at 12.2% in poorly populated edge bins). This algorithmic variation represents a systematic limitation of tree-based density estimation that is not parameterized in the experimental covariance."*

* **Worst Passage 2 (Sec. IV B, col. 2, lines 17–28):**
  > *"Because the block is built from the differences among the periods, it contains them by construction; this says nothing about its coverage, that is, whether its size is right. For the same reason, the block’s own consistency check passes whatever the data, and it is not a test."*
* **Why it fails PRD style:** "passes whatever the data, and it is not a test" is an author having an existential argument with themselves on the page.
* **PRD Rewrite 2:**
  > *"To account for observed rate variations across beam periods (most notably a ~7% discrepancy in the longitudinal momentum distribution near 8 GeV/c), we include an empirical run-period covariance block derived from independent period subsets. By construction, this component encompasses the observed inter-period scatter, though it does not isolate the underlying physical or detector mechanism."*

* **Worst Passage 3 (Sec. IV B, col. 2, lines 36–49):**
  > *"An earlier version of the budget did not propagate these fluctuations... Rescoring the same pseudo-experiments against the rebuilt band, which is post hoc and partly circular, removes the tail undercoverage: 97.7 % fall within two standard deviations and 78.1 % within one. The rebuilt band has not been independently tested either, and the quoted statistical block is a different ensemble from it..."*
* **Why it fails PRD style:** The entire narrative of "Version 1 was flawed, we noticed it, rebuilt Version 2, tested it post hoc, which is circular..." is git commit history, not a scientific paper!
* **PRD Rewrite 3:**
  > *"The statistical covariance is evaluated using a 300-replica bootstrap that independently resamples data, signal simulation, and background templates, fully propagating template statistical fluctuations. In simulated closure tests with nominal truth, the resulting statistical intervals contain the true value within $\pm 2\sigma$ for 97.7% of bins (78.1% within $\pm 1\sigma$), exhibiting slight overcoverage in the tails."*

---

###### 6. Section V (Status of a Five-Dimensional Uncertainty)
* **Diagnosis:** The absolute nadir of presentation in the paper. The authors write as if an auditor is about to revoke their analysis license.
* **Worst Passage (Col. 1, lines 4–11):**
  > *"It has not met the criteria that the analysis set in advance for an uncertainty: one of them requires a bound fixed before the covariance was produced, and it can no longer be applied. We nevertheless use this covariance, as recorded in the analysis note, and that allowance covers no other covariance."*
* **Why it fails PRD style:** *"and that allowance covers no other covariance"* reads like a legal liability disclaimer issued by a corporate compliance department.
* **PRD Rewrite:**
  > *"An experimental covariance matrix was evaluated for the five-dimensional central value and projected onto the 42-cell $(E_\text{avail}, W)$ space. However, we find that the resulting uncertainty estimates are destabilized by classifier training-seed fluctuations: varying the random seed introduces a 6.1% root-mean-square variation in the projected uncertainty, exceeding our target stability threshold of 5%. Furthermore, evaluating model dependence across alternative generator truths reveals an intrinsic prior sensitivity of 10–13% per cell, which is comparable to the generator discrepancies under investigation. Consequently, we conclude that the current implementation cannot support a formal five-dimensional cross-section measurement with robust total uncertainties."*

---

###### 7. Section VI (Central-Value Results)
* **Diagnosis:** Reads relatively well as a physics discussion, but repeatedly interrupts itself to re-warn the reader that these are "central values only" and "no significance is assigned."
* **Recommendation:** State once at the beginning of the section: *"The distributions presented in this section are unregularized central values intended for qualitative comparison; in light of the methodological limitations established in Sec. V, no formal goodness-of-fit significance is assigned to them."* Then discuss the physics cleanly without repeating the disclaimer in every paragraph.

---

###### 8. Section VII (Calibrated Joint Tests of Generator Predictions)
* **Diagnosis:** Technically sophisticated, but riddled with procedural self-flagellation regarding compute times, batch sizes, lost seeds, and pre-commit protocols.
* **Worst Passage (Sec. VII A, col. 2, lines 34–47):**
  > *"Some choices were made after results had been seen. Besides the choice of the two-dimensional central value (Sec. IV A), two parts of this procedure were informed by the data. Those who reviewed the test design had seen descriptive per-cell residuals of the data before it was fixed. A bounded extension of the production computing budget was decided while the outputs of the computing jobs showed the observed p values used for the decisions; it changed no statistic, shifted null, threshold, or stopping rule..."*
* **Why it fails PRD style:** No PRD reader needs to know that reviewers peeked at residuals or that the authors extended their NERSC computing allocation while monitoring job queues! This is pure process anxiety.
* **PRD Rewrite:**
  > *"To ensure statistical rigor, the hypothesis testing framework—including test statistics, null-shift bounds, multiplicity corrections, and stopping criteria—was fully defined prior to evaluating the final data test statistics. The Monte Carlo $p$-value precision was determined using sequential Clopper–Pearson intervals evaluated in batches of 200 pseudo-experiments."*

* **Second Worst Passage (Sec. VII C, lines 17–25):**
  > *"Computing time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments. All of them were rerun with a procedure fixed in advance [34], and none reaches the observed statistic in any test or shifted null, so no assignment of the lost outcomes changes any decision."*
* **Why it fails PRD style:** Batch job timeouts on a computing cluster do not belong in the body of a physics paper.
* **PRD Rewrite:**
  > *"All submitted calibration pseudo-experiments were executed to completion, with an ensemble size of at least $B = 1343$ achieved for each tested model."* (Keep the recovery details in the technical analysis note).

---

###### 9. Section VIII (Conclusions) & Acknowledgments / Data Availability
* **Diagnosis:** The conclusions repeat the stacked disclaimers. In Data Availability, the phrase *"after the separately authorized release decision"* sounds like classified government intelligence rather than an open-access Zenodo upload.
* **PRD Rewrite for Data Availability:**
  > *"The analysis code, candidate release packages, reproducible pipeline scripts, and plotting routines are available in an open-access repository [cite Zenodo/GitHub]. Raw input files are archived through the MINERvA open-data portal [8]."*

---

#### PART 3 — THE ABSTRACT

##### (a) Breakdown of the Current Abstract
The submitted abstract is 157 words. Here is the sentence-by-sentence categorization:

1. *"We apply OmniFold to MINERvA open data for medium-energy $\nu_\mu$ charged-current inclusive interactions."*  
   $\rightarrow$ **Scope / Method context.**
2. *"The analysis reproduces the published double-differential cross section in muon kinematics, with the integrated cross section within about one percent, and extends it to five simultaneous observables by adding available energy, three-momentum transfer, and hadronic invariant mass."*  
   $\rightarrow$ **Headline Result 1** (2D reproduction & 5D extension).
3. *"The three- to five-observable results are central values only."*  
   $\rightarrow$ **Qualification / Restriction.**
4. *"Pseudo-experiments reveal background-subtraction and regularization biases, and the measured model dependence, about 10–13% per cell, prevents a five-dimensional measurement whose total uncertainties meet our predefined 10% precision target."*  
   $\rightarrow$ **Qualification / Negative finding** (Methodological barrier).
5. *"Tests calibrated with pseudo-experiments that rerun the full analysis chain reject the hybrid null hypotheses built from five generator predictions, in total and in shape, at the 5% familywise level."*  
   $\rightarrow$ **Headline Result 2** (Calibrated generator hypothesis rejections).
6. *"Their interpretation is limited: the nuisance model has no calorimetric recoil-response uncertainty, convergence of the fine grid defining the null hypotheses has not been shown, and the joint five-observable information is not shown to discriminate beyond matched coarse projections."*  
   $\rightarrow$ **Qualification / Technical caveat** (Three heavy disclaimers).

**Assessment:**  
Only **2 out of 6 sentences** (Sentences 2 and 5) state positive results. Four sentences (67% of the abstract) are defensive qualifications. Sentence 6 alone packs three dense technical caveats into a single 38-word run-on sentence.

---

##### (b) Rewritten Abstract (142 words)

> We report the first application of unbinned machine-learning deconvolution (OmniFold) to experimental neutrino-nucleus data, analyzing MINERvA medium-energy $\nu_\mu$ charged-current inclusive interactions on hydrocarbon. The method reproduces the published double-differential cross section in muon kinematics ($p_T, p_\parallel$) within 1.1% in integrated rate. We extend the deconvolution to five simultaneous kinematic observables by incorporating available hadronic energy, three-momentum transfer, and invariant mass. We examine the operational limits of unbinned unfolding in neutrino physics, identifying non-negligible regularization biases under generator shifts and a 10–13% residual model dependence that precludes a full five-dimensional measurement with robust uncertainties. Instead, we perform model comparisons using full-chain calibrated hypothesis tests. All five tested generator models are rejected at the 5% familywise significance level. However, we demonstrate that these rejections are primarily driven by low-dimensional projections and remain sensitive to calorimetric recoil-energy response modeling.

*(Word count: 142 words. Meets the 120–160 word target, adheres strictly to PRD style, highlights both achievements and real physics limitations, and eliminates defensive jargon).*

---

##### (c) Accounting of Omissions from the Abstract

Here is what was removed from the original abstract and where each item should be stated in the main text:

1. **"The three- to five-observable results are central values only":**  
   *Dropped from abstract.* Replaced by the clearer statement that model dependence *"precludes a full five-dimensional measurement with robust uncertainties."*  
   *Where in body:* Section I (Introduction, end of overview) and Section VI (Central-Value Results, opening sentence).
2. **"meet our predefined 10% precision target":**  
   *Dropped entirely.* A target chosen by the authors during analysis planning is internal project management context, not a physical property of nature.  
   *Where in body:* Section V (Uncertainty Status), framed simply as an operational design goal.
3. **"Background-subtraction biases" (explicit mention in abstract):**  
   *Dropped from abstract.* The negative-weight refinement successfully removes this bias to $<0.3\%$, so it is a solved technical problem rather than a headline limitation.  
   *Where in body:* Section III and Section IV C, where the unbinned background treatment is detailed.
4. **"Hybrid null hypotheses":**  
   *Dropped term from abstract.* Replaced by "generator models." The specific construction of the null (fine-grid bins with Tune v1 sub-structure) is a simulation detail that confuses uninitiated readers in an abstract.  
   *Where in body:* Section VII A (Hypotheses, Statistics, and Calibration), where the mathematical definition belongs.
5. **"Convergence of the fine grid defining the null hypotheses has not been shown":**  
   *Dropped from abstract.* This is a specific systematic caveat of the hypothesis test.  
   *Where in body:* Section VII B (Condition i), under the conditions of the test.
6. **"The nuisance model has no calorimetric recoil-response uncertainty":**  
   *Retained in spirit in the abstract* ("remain sensitive to calorimetric recoil-energy response modeling"), but the detailed critique of the missing band belongs in the text.  
   *Where in body:* Section VII B (Condition ii) and Section VII D (Hadronic-Response Condition).

---

#### PART 4 — CANDID ADVICE TO THE AUTHORS

##### 1. Stop Apologizing for Negative Results
This manuscript contains an exceptional amount of rigorous work. You took an advanced machine-learning method that was hailed as a revolution in collider physics and subjected it to the brutal reality of neutrino-nucleus scattering. You discovered that because neutrino interactions have broad migrations, severe missing energy, and substantial model uncertainties, OmniFold suffers from regularization bias, seed instability, and model dependence that prevent straightforward extraction of 5D cross sections.

**That is not a failure; that is a major scientific result.** 

The neutrino community desperately needs this paper. Currently, experimental collaborations are drafting roadmaps that assume unbinned deep learning will magically solve high-dimensional unfolding for DUNE and Hyper-K. Your paper proves that ML unfolding is subject to the same fundamental bias-variance trade-offs and prior-pull limitations as classical D'Agostini unfolding—and in some respects is harder to stabilize. 

However, you write as if you are ashamed of this finding. You write as though you committed a crime by failing to produce a 5D measurement with $<10\%$ uncertainties, and so you surround the paper with barbed wire: stacked disclaimers, audit trails, and legalistic qualifications. Strip the defensiveness away. Frame your paper proudly as an objective investigation into the boundaries and feasibility of unbinned unfolding in neutrino physics.

##### 2. Discard the "Audit Trail" Register
Phrases like *"this allowance covers no other covariance,"* *"predefined precision target,"* *"a bounded extension of the computing budget was decided while jobs showed p-values,"* and *"separately authorized release decision"* do not demonstrate rigor. They project anxiety. They sound like the authors are afraid of being accused of fraud or protocol violations by an internal review committee. 

PRD papers operate on scientific demonstration, mathematical proof, and code reproducibility. You have committed checksums, Docker/code packages, reproducible scripts, and clear equations. Let the artifacts demonstrate your integrity; do not clutter the physics text with the history of your computational budget meetings or data-peeking anxieties.

##### 3. Be Rigorous About What You Actually Disproved
Be careful with the claim that you "rejected five generator predictions." 
As neutrino experimentalists, you know that MINERvA's calorimetric recoil response has non-trivial systematic uncertainties. When you discover that:
- In the muon variables $(p_T, p_\parallel)$, GENIE CV is **not** rejected ($p = 0.48$),
- In the 5D space, GENIE CV **is** rejected ($p < 0.006$),
- But the 5D space relies on $E_\text{avail}, q_3, W$, which use calorimetric recoil, and your calibration **omitted the calorimetric recoil uncertainty**,

you have not definitively rejected GENIE CV. You have rejected a hybrid simulation model under an incomplete detector error budget. An experienced referee in our field will immediately seize on this. State it with scientific maturity: the hypothesis tests serve as a proof-of-principle for full-chain calibrated inference, but their physical conclusions regarding generator validity remain preliminary pending full hadronic detector systematics.

##### 4. Acknowledging AI Usage
The paragraph in the Acknowledgments describing the specific AI model versions (GPT-5.5, Claude Opus 4.8, Fable 5.1, etc.) is honest, but the register is again overly detailed. A concise statement—*"The authors utilized language models (Anthropic Claude, OpenAI GPT) as assistive tools for coding, script generation, and text editing, with all analyses, verification, and final manuscript content directed and validated by the authors"*—is standard, professional, and compliant with APS ethics guidelines without sounding like an IT software licensing inventory.

---
*End of Report.*

---

## P20. X3 GPT-6.1-sol: referee report on the pass-2 paper (27edd449) (sha256 `a6260d91946fd59c…`)

**Part 1 — Referee report**

**Summary and overall assessment**

This manuscript applies OmniFold to public MINERvA medium-energy inclusive charged-current neutrino data. It compares a two-observable unfolding with the published muon-kinematic cross section, extends the estimator to five observables, investigates several sources of bias and uncertainty, and constructs generator tests calibrated with pseudo-experiments that repeat the analysis chain.

The most substantial findings are methodological. The implementation approximately reproduces the published normalization and most individual bins, but exhibits appreciable regularization bias for plausible truth deformations, background-treatment bias, and serious undercoverage in a tested five-observable interval construction. A study of alternative reporting definitions does not achieve the authors’ chosen precision target. Full-chain calibration nevertheless permits tests of specified simulated hypotheses, all of which are rejected under the implemented nuisance model. These tests concern hybrid generator hypotheses, omit calorimetric recoil-response uncertainty, and do not establish additional discrimination from the joint five-observable information.

There is potentially publishable work here. Applying an unbinned unfolding method to a large, public neutrino dataset is useful, and a careful account of its limitations could be valuable to the field. Calibration of a biased estimator is also a legitimate and interesting approach: an estimator need not be unbiased for a test based on it to have correct size.

However, the present manuscript does not yet establish either a validated higher-dimensional cross-section measurement or sufficiently secure physical generator exclusions. Its strongest physics statements depend on unresolved detector and hypothesis-definition issues. Its statistical claims also require clarification and, in places, additional validation. The considerable transparency is welcome, but disclosure does not itself resolve those deficiencies.

**Significance and novelty**

The novelty is principally the application to neutrino-scattering data and the associated validation study. I cannot establish priority from the supplied manuscript alone, but the claimed distinction from the cited simulation study is clear.

The physics novelty is limited. The low-recoil discrepancy and the broad generator disagreements are already known. The manuscript explicitly finds no demonstrated increase in discrimination from the joint information. Moreover, the generator versions tested are largely older configurations; they provide useful benchmarks but do not by themselves establish a contemporary advance in interaction-model discrimination.

The negative results could constitute a substantive contribution if presented as a quantitative study of identifiability, regularization, and inference with public neutrino data. At present, the paper alternates between that contribution and the stronger framing of a multidimensional measurement with calibrated physical model exclusions.

**Major comments**

**1. The paper must identify its primary scientific result and align the claims with it.**

The higher-dimensional central values do not have validated total uncertainties. Plausible truth changes produce residual biases reaching tens of percent, and a tested statistical interval construction has coverage as low as 0.06 for nominal 68% intervals. These are substantial limitations on the interpretation of an unfolded distribution.

The results remain useful as outputs of a specified estimator and as a validation study. They are not yet a generally usable five-dimensional cross-section measurement. This distinction should govern the title, abstract, figures, conclusion, and released products.

There are two defensible directions:

- Complete the detector-response, hypothesis-definition, and statistical-calibration work needed to support the generator tests as physical results.
- Reframe the paper around the performance and limitations of this implementation, with the generator tests explicitly serving as conditional demonstrations.

Neither direction requires suppressing the negative findings. Those findings are among the paper’s most useful results.

**2. The calorimetric response omission is a central physics issue.**

The five-observable analysis uses several quantities that depend on reconstructed hadronic energy. The missing calorimetric response uncertainty therefore acts directly on the information that distinguishes this analysis from the published muon-only measurement.

The manuscript appropriately distinguishes this uncertainty from GEANT hadron-interaction reweights. Its own projection study makes the omission particularly consequential: GENIE CV is not rejected in the matched muon-kinematic projection, so its rejection relies on hadronic information.

Scaling reconstructed recoil energy by ±4% and comparing with unchanged null distributions is a sensitivity check. It is not a propagation of the missing uncertainty. It tests neither the corresponding change in the null distributions nor particle-dependent, energy-dependent, resolution, or correlated response effects. The test-beam agreement quoted also does not establish a universal uncertainty envelope for this event sample.

For physical exclusions, a defensible response model must be propagated through the calibration. If the available public inputs do not support that, the limitation should define the scope of the result: exclusions within the implemented response model, rather than exclusions of the generator predictions without that qualification.

**3. The external-generator null hypotheses are materially different from the generators themselves.**

The hybrid-null construction is a reasonable computational device, but its consequences must be made explicit. Reweighting the analysis simulation on a finite truth grid preserves its conditional distributions within each grid cell. Those conditional distributions can affect detector response and unfolding.

The observed refinement steps do not demonstrate convergence. More importantly, the residual discrepancy need not lie along the last observed refinement direction. Enlarging the displacement along that direction to \(5.17\,\delta_{\rm fine}\) does not bound a residual with a different direction.

The statement that a geometric extrapolation was adopted but its calculation is not recorded is particularly problematic for a quantity used in the decision procedure. A predeclared assumption is still an assumption; predeclaration cannot supply its missing justification.

The paper should either demonstrate adequate stability using further refinement and alternative within-cell reweightings, or retain the hybrid hypotheses as the actual objects tested throughout. A detector-level comparison using independently simulated generator events would provide an especially valuable check if feasible.

Tune v1 deserves separate treatment: its null does not have this particular hybridization problem, although it retains the detector and calibration limitations.

**4. The stated familywise error control is not established by the description provided.**

Several distinct issues require resolution.

First, \((k+1)/(B+1)\) has its usual finite-simulation validity under an appropriate exchangeable construction with a fixed simulation count. Here, the number of pseudo-experiments depends on observed exceedances and confidence-interval stopping criteria. Ordinary Clopper–Pearson intervals have fixed-sample coverage; repeatedly inspecting them does not automatically produce a valid sequential procedure. Using 99.5% intervals for stopping and 95% intervals for the final decisions may be conservative in this application, but that needs demonstration.

Second, the text states that a computing-budget extension was chosen while observed p values were visible and then asserts that the Monte Carlo p values remain valid at the attained sample sizes. That assertion needs a statistical argument. A valid sequential Monte Carlo procedure, a simultaneous confidence construction over the allowed looks, or an independent fixed-size calibration could resolve the issue.

Third, Holm control requires valid individual p values for the stated hypotheses. The additional confidence-interval criterion does not by itself establish that prerequisite. The treatment of hypothesis ranking, ties, shared total/shape ensembles, and differing stopping counts should be specified.

Fourth, nuisance parameters are drawn from a prescribed distribution. This calibrates a nuisance-averaged ensemble. It does not automatically guarantee a 5% rejection probability for every fixed nuisance configuration allowed by the model. The manuscript should say which interpretation it claims. Taking the largest p value over a finite set of selected shifts supplies protection over that set, not over all unmodelled detector responses or within-cell shapes.

These issues do not establish that any particular rejection will disappear. They establish that “5% familywise level” is currently stronger than the demonstrated statistical result.

**5. Drawing interaction-model uncertainties under a fixed-generator null requires a precise definition.**

The null is stated as a fixed true cross section \(G\), yet the pseudo-experiments draw 34 interaction-model uncertainty bands. Such variations can change:

- the truth distribution defining the hypothesis;
- the response conditional on the reported truth variables;
- the background prediction;
- or the unfolding prior.

These roles are different. If a variation changes the true cross section, the null is a family or mixture around \(G\), rather than the equality stated. If it changes only conditional response or the analysis model, the implementation must explain how the truth cross section remains fixed.

The manuscript needs a compact generative description of a pseudo-experiment: what is generated, what is varied, what the unfolding assumes, and which quantities remain fixed. This also needs to explain correlations among systematic bands, the treatment of clipped negative weights, and the normalization uncertainty.

**6. Full-chain calibration must be validated as an approximation to the data analysis.**

The paper recognizes that the data use the full simulation while pseudo-experiments use half. A bounded shift in the mean unfolded result does not necessarily account for changes in covariance, classifier fluctuations, or tail probabilities. The reported small shift is reassuring, but its relevance to rejection probabilities needs to be demonstrated.

There are additional questions:

- Are the pilot pseudo-experiments used to determine the metric independent of the production calibration?
- How is the metric treated in repeated experiments?
- Does the procedure reproduce the intended rejection rate under simulated null datasets processed like the actual data?
- Does event reuse induce correlations absent from the real-data application?
- Does the lateral-variation surrogate reproduce relevant changes in the test statistic?

An independently written calculation of p values verifies arithmetic and implementation consistency. It does not validate the pseudo-experiment ensemble.

The missing coverage validation of the unfolded intervals does not, by itself, invalidate these tests. The appropriate requirement here is validation of test size under the specified ensemble.

**7. The validation does not yet establish reliable recovery of the higher-dimensional distributions.**

The reported regularization bias is too large to treat as a secondary qualification. Failure to recover a generator-sized deformation, with deviations up to 74% in some cells, shows that the estimator can substantially reshape plausible truths. The coverage failure is consistent with this concern.

Several distinctions need to be maintained:

- Agreement of marginal normalizations is a useful consistency check but provides weak evidence for recovering joint structure.
- Truth-reweighting closure tests do not test detector-response mismatch.
- Changing reconstructed features can change the estimator’s implicit regularization even when the event sample is unchanged.
- A fixed five-iteration choice and default classifier settings do not establish an adequate bias–variance balance.

The main paper should show at least one compact quantitative closure and coverage figure. Currently, its most consequential validation failures appear largely as prose.

The statement that the “three- and four-observable central values also pass closure tests” should identify the deformations and acceptance criteria. Passing selected tests cannot be read as general validation, especially given the five-observable failures.

**8. The five observables’ information content and truth definitions require clearer treatment.**

The authors correctly note shared reconstructed inputs, but the implications extend beyond correlation. The muon variables, \(q_3\), and \(W\) are connected by interaction kinematics. Depending on their precise construction, the nominal five-dimensional distribution can occupy a constrained region and contain fewer independent degrees of freedom than the variable count suggests.

The paper should provide explicit reconstructed and truth definitions in the article, explain the kinematic relationships, and describe the supported domain. “Five simultaneous observables” is an appropriate description; it should not imply five independent constraints.

The available-energy definition also deserves correction or a stronger justification. Retaining an inherited 135 MeV subtraction for charged pions produces a nonstandard observable. Its measured numerical effect may be small, but the physically motivated solution is to correct the definition and propagate the change, unless compatibility with a specific released quantity requires otherwise. In that case, define the quantity explicitly as used and ensure every generator prediction uses precisely that definition.

For \(W\), specify the struck-nucleon mass convention and explain its interpretation for bound-nucleon, multinucleon, and other relevant interaction categories.

**9. The two-dimensional reproduction is useful but should not be presented as full validation.**

The normalization agreement and binwise comparisons are encouraging. They do not establish equivalence with the published extraction. A covariance-weighted distance of \(\chi^2/\mathrm{ndf}=2.65\) is substantial as a descriptive metric, even though it cannot be assigned a compatibility significance using only the published covariance.

The manuscript correctly recognizes the missing cross-covariance. It should consistently describe the number as a covariance-weighted distance, rather than alternate between a reproduction claim and a shape-disagreement interpretation.

Choosing LightGBM to match the estimator used for the covariance is methodologically sensible. Because that choice followed inspection of both comparisons, the paper should show the alternative clearly and avoid treating the agreement as wholly independent validation. A concise disclosure is sufficient; repeated project history is unnecessary.

The unresolved run-period discrepancy is more concerning than the prose emphasis suggests. A roughly 7% step deserves further examination of selection, flux, response, and run-dependent normalization before it is absorbed into an empirical covariance. The covariance may be a pragmatic representation of observed variation, but it is not a demonstrated systematic-error model.

**10. The uncertainty discussion needs a coherent definition of what is being estimated.**

The paper combines systematic-universe variation, bootstrap covariance, training variation, and an empirical run-period term. It should explain the probability model and estimand associated with each contribution and how possible overlaps are handled.

The model-dependence study is useful, but the largest shift over five selected deformations is an envelope over those deformations. It is not a general bound on unfolding bias. Likewise, exceeding a chosen 10% target does not establish a fundamental precision limit for OmniFold or neutrino multidimensional unfolding. It establishes that the tested configurations and reporting definitions do not meet that target.

The apparent discrepancy between a 0.06% median training uncertainty in two dimensions and a 6.145% change in a projected five-dimensional uncertainty also needs clarification. These may be entirely different quantities; the paper must define their denominators and aggregation explicitly.

Independent simulation of production size and a continuous nuisance generator may be useful validation resources, but they are not universal prerequisites for every defensible uncertainty statement. The authors should identify what those resources would resolve in this analysis.

**11. Some descriptive physics interpretations exceed what the comparisons establish.**

The low-recoil result is consistent with known discrepancies. It does not uniquely identify a missing nuclear mechanism. The small effect of selected pion-FSI variations cannot exclude other FSI uncertainties or detector effects.

Similarly, adding Valencia 2p2h and filling 52% of a central-value gap is a model comparison, not a measurement of the multinucleon contribution. The denominator, integration region, and uncertainty on that fraction should be clear.

The high-\(E_{\rm avail}\), high-\(W\) excess is sensitive to the comparison model, response assumptions, large overflow cells, and regularization bias. The manuscript acknowledges these issues, but “separates the remaining discrepancy” still suggests a stronger physical localization than is supported.

Comparisons also require consistent targets and fluxes. NuWro and GiBUU are on carbon, whereas the measurement and GENIE predictions are on CH. Normalization per nucleon does not by itself remove the target difference. The hydrogen contribution must be evaluated or the comparison qualified quantitatively.

Adding the high-energy share from another generator to GiBUU can illustrate sensitivity to the missing flux tail. It cannot supply the missing GiBUU prediction without an additional modelling assumption.

**12. The article and release are not yet publication-ready.**

Essential estimator definitions, validation criteria, and uncertainty prescriptions are deferred to a repository analysis note. The article should contain enough information to understand its central claims without navigating internal project records.

The release remains a locally prepared candidate, contains the obsolete two-dimensional curve rather than the figure’s current input, and does not reproduce many quoted results. Funding and access placeholders remain. These issues must be resolved before acceptance.

A numerical replay package is valuable, but it should be distinguished from a release sufficient to reproduce the analysis. The final package should contain the current figures’ inputs, machine-readable central values, applicable covariance products, domain masks, estimator configurations, and precise access information for the additional required inputs.

**Minor comments**

- State the essential signal and fiducial definitions explicitly, including kinematic restrictions and the target convention.
- Distinguish selected simulation events from all truth signal events in the quoted sample sizes.
- Give the integrated flux and target normalization used to form cross sections.
- Define the reported “ndf,” treatment of singular covariance modes, and normalization constraints.
- State the exact definition of the shape statistic after dropping a cell and whether the result depends on that choice.
- Explain whether prediction finite-sample uncertainty is included consistently in both the metric and calibration. Its appearance in both is not inherently double counting, but the construction needs to be explicit.
- Report binwise and aggregate coverage separately. Pooling over correlated cells can obscure the location and severity of failures.
- Reconcile the power-study denominators with the statement that all lost pseudo-experiments were recovered.
- Define the “6.145%” uncertainty movement mathematically and avoid unjustified numerical precision.
- Clarify the square-root/trace expression in Sec. V; as extracted, its meaning is unclear.
- Remove “claim variant” from Fig. 4. Identify the plotted shift mathematically.
- A null distribution’s largest median need not correspond to its largest tail probability at the observed statistic. Explain the relationship between the displayed distribution and the conservative decision.
- Supply uncertainties for estimated powers and make clear that finite ensembles cannot establish power exactly equal to 1.
- Consider showing the overflow contributions explicitly in Fig. 3 or in an accompanying table, since they matter to the discussion.
- Do not infer substantive agreement from overlapping correlated uncertainty bands.

**Recommendation**

I recommend **major revision and do not support publication in its present form**.

The application and validation findings warrant further consideration. Acceptance would require a coherent scientific scope, a defensible treatment of sequential Monte Carlo calibration, and either resolution of the principal detector and hybrid-null limitations or a substantial narrowing of the physical claims. Editorial revision alone will not address those points.

---

**Part 2 — Presentation and section-by-section revision**

The authors’ concern is justified. Much of the paper reads as a project audit written to anticipate objections. The problem is not that limitations are disclosed. Several limitations are scientifically central and deserve prominent treatment. The problem is that physical assumptions, methodological failures, bookkeeping details, and project chronology receive similar emphasis.

A PRD article should state the method, show the evidence, interpret the result, and place each limitation where it changes that interpretation. It should not require readers to reconstruct the analysis from successive corrections to earlier versions.

The quotations below retain the manuscript’s wording, with PDF line breaks reflowed.

**Title**

It is broadly appropriate, but “validation and calibrated model tests” suggests a more complete validation outcome than the paper establishes.

For the narrower methodological paper, I would suggest:

> “OmniFold unfolding of MINERvA inclusive charged-current data: performance, limitations, and conditional model tests”

“Five-observable” is preferable to an unqualified emphasis on five independent dimensions.

**Abstract**

It reads like an unusually compressed referee response. The first two sentences establish the application; the rest rapidly stack status statements, failure modes, and conditions.

The most overloaded passage is:

> “Their interpretation is limited: the nuisance model has no calorimetric recoil-response uncertainty, convergence of the fine grid defining the null hypotheses has not been shown, and the joint five-observable information is not shown to discriminate beyond matched coarse projections.”

These are three different conclusions: an omitted detector uncertainty, an inadequately controlled hypothesis approximation, and an absence of demonstrated added discrimination. All matter, but they should be expressed as results and assumptions rather than as an accumulated warning. A complete replacement appears in Part 3.

**I. Introduction**

The opening paragraphs read like a conventional PRD introduction. The section becomes overlong when it recapitulates nearly the entire validation record.

The clearest example is:

> “These biases, the dependence on the estimator’s random seed, and the untested or failed interval coverage limit the method, and the measured model dependence, about 10–13% per cell, prevents a five-dimensional measurement whose total uncertainties meet the 10 % precision target we set in advance (Sec. V).”

An experienced author might write:

> “For the five-observable configurations studied here, regularization bias and model dependence prevent us from obtaining validated uncertainties at the chosen 10% precision target. We therefore report higher-dimensional central values and investigate hypothesis tests calibrated through the complete analysis chain.”

The remaining details belong in Secs. IV and V. The introduction needs one paragraph describing the outcome, not an inventory of every validation result and procedural condition.

Also replace:

> “All ten calibrated tests, in total and in shape, reject the hybrid null hypotheses built from the five predictions at the 5% familywise level under six stated conditions (Sec. VII B).”

with:

> “Under the implemented nuisance model, the calibrated tests reject all five hybrid generator hypotheses in normalization and shape. Their physical interpretation is limited by the missing calorimetric-response uncertainty and unresolved within-cell generator dependence.”

The exact familywise claim should be restored only once its calibration is established.

**II. Data, signal, and simulation**

This section mostly reads like a PRD paper. Its main weakness is insufficient self-contained definition, coupled with excessive attention to the provenance of one implementation defect.

The passage:

> “We have not corrected this constant. Relative to the charged-pion mass, in a simulated sample it moves 0.67 % of events into another true-Eavail bin and changes no true-Eavail bin by more than 1.05 %; this effect has not been compared with the full covariance.”

could become:

> “The implemented definition subtracts 135 MeV from each charged-pion energy. Replacing this value with the charged-pion mass changes the true-\(E_{\rm avail}\) bin assignment for 0.67% of simulated events and changes each bin content by at most 1.05%. Its effect relative to the full covariance has not been evaluated.”

This preserves the limitation without sounding like an unresolved work ticket. Scientifically, I would still prefer correcting the definition.

The shared-input qualification belongs here once, accompanied by equations and a discussion of the resulting kinematic constraints. It does not need repeated reminders elsewhere that the observables are correlated.

**III. Unbinned unfolding**

The basic method description is suitable. The estimator taxonomy is difficult to follow, and the closing AI sentence interrupts the scientific description.

The worst passage is:

> “The two- to five-dimensional central values use LightGBM at matched nominal capacity with the purity-based subtraction, which we call the central-value estimator; the two-dimensional one is the central value of its systematic-universe ensemble, so its covariance is built with the same estimator.”

A clearer version is:

> “We use two principal configurations. The reported central values use LightGBM with purity-weighted background subtraction. The generator tests use a deterministic LightGBM configuration with unbinned background refinement. The two-dimensional covariance is evaluated with the same configuration as its central value.”

Follow this with a small configuration table containing classifier capacity, background treatment, determinism, iteration count, and use. Include the exact-split cross-check as a third row.

For:

> “The joint tests (Sec. VII) use a deterministic LightGBM configuration, the joint-test estimator, selected before the joint-test design was fixed.”

write:

> “The generator tests use a deterministic LightGBM configuration selected in simulation studies.”

Place the precise selection chronology in one disclosure paragraph later. Move the AI cross-reference to the acknowledgments.

**IV. Validation**

This section needs the most structural revision. It contains important science, but the evidence is buried in chronology and qualifications.

The opening definitions of closure and coverage are useful. They could be shortened and immediately followed by a table of tests, configurations, truths, and outcomes.

**IV A. Two-dimensional reproduction**

The disclosure of the learner change is appropriate:

> “This choice, which replaced the exact-split result, was made after both comparisons were known.”

It should be integrated into the methodological reason:

> “We report the LightGBM result to use the same estimator for the central value and covariance. This choice was made after inspecting both comparisons; the exact-split alternative is retained as a cross-check.”

One disclosure is enough. It need not recur in the introduction, joint-test history, and conclusion.

Also replace the significance-like presentation of \(\chi^2/\mathrm{ndf}\) with:

> “Using the published covariance as a metric gives a covariance-weighted squared distance of 2.65 per reported degree of freedom. Because the estimates share data and their cross-covariance is unavailable, this quantity is descriptive.”

**IV B. Two-dimensional uncertainty and its coverage**

This subsection reads most strongly like an internal review response.

The worst passage is:

> “Because the block is built from the differences among the periods, it contains them by construction; this says nothing about its coverage, that is, whether its size is right. For the same reason, the block’s own consistency check passes whatever the data, and it is not a test.”

The scientific content can be stated directly:

> “The run-period covariance is an empirical estimate based on three groups. Its construction reproduces the observed intergroup variation and therefore provides no independent validation of its magnitude or coverage. Statistical and training fluctuations, possible regularization shrinkage, and the small number of groups limit its interpretation.”

The long account of the earlier statistical band should become:

> “The current statistical covariance has not undergone an independent coverage test. A previous interval construction undercovered; revising it and evaluating it on the same pseudo-experiments does not constitute independent validation. The earlier study and numerical results are documented in the Supplemental Material.”

That preserves the failed test and the limitation of the revision. The detailed 91.2%, 97.7%, and 78.1% history need not occupy the main article unless it supports a methodological conclusion.

The repetition becomes particularly conspicuous here:

> “The result’s intervals, bias and covariance have not been independently validated, and we make no claim about coverage. In particular, the coverage of its intervals has not been validated on independent simulated samples, nor simultaneously over all reported bins and projections.”

Replace with:

> “Independent coverage validation is unavailable for the current statistical and total intervals, including simultaneous coverage across bins and projections.”

Then list the omitted covariance contributions once. “Simultaneous coverage” should also be distinguished from ordinary pointwise interval coverage; it is a separate statistical objective.

**IV C. Higher-dimensional central values**

This subsection is scientifically important but overloaded. Separate background bias, regularization bias, numerical sensitivity, and coverage into distinct paragraphs supported by figures.

The sentence:

> “These intervals therefore miscover at the tested truths, and no frequentist coverage is claimed for the five-dimensional intervals.”

can be more direct:

> “The tested interval construction fails coverage, particularly for the \(E_{\rm avail}\) tilt: nominal 68% coverage falls to 6% in the most affected integral.”

Then state precisely which estimator and interval construction were tested, and how they relate to any displayed uncertainties. The failure deserves prominence; repeating “no coverage is claimed” in multiple sections does not add information.

The numerical-sensitivity sentence should also use a physical scale as well as statistical standard deviations. A reader needs to know whether the effect is a fraction of a percent or a several-percent change.

**V. Status of a five-dimensional uncertainty**

The current section title and opening sound like a project status report.

The worst passage in the manuscript is:

> “It has not met the criteria that the analysis set in advance for an uncertainty: one of them requires a bound fixed before the covariance was produced, and it can no longer be applied. We nevertheless use this covariance, as recorded in the analysis note, and that allowance covers no other covariance.”

This describes an internal exception without explaining the scientific adequacy of the covariance.

A suitable replacement is:

> “The five-observable covariance does not satisfy all validation criteria adopted for this study. One criterion required a bound specified before covariance construction; because that bound was not fixed, the criterion cannot be assessed retrospectively. We retain this covariance as a descriptive analysis product, but do not use it to assign generator significances. No other covariance is covered by this decision.”

The last sentence is only needed if it has a meaningful consequence for released products. Otherwise, retain that administrative detail in the analysis record.

Rename the section “Five-observable uncertainty studies” and divide it into covariance stability and precision/model dependence.

The computing limitation can be stated without procedural language:

> “None of the reporting definitions examined within the available computing budget met the chosen precision target. For the fallback 39-cell projection, the median envelope over the five tested truth deformations is 13.4%, exceeding the 10% target before other uncertainties are included.”

This does not generalize beyond the tested definitions.

**VI. Central-value results**

This is the section closest to a conventional physics-results discussion. Its central weakness is occasional causal or localization language stronger than the evidence.

For:

> “The fifth observable, W, separates the remaining discrepancy from the low-mass enhancement.”

write:

> “The \((E_{\rm avail},W)\) projection shows how the central-value difference from Tune v1 is distributed in hadronic invariant mass.”

For:

> “That measurement defines true Eavail more broadly, counting every final-state particle except neutrons, several species of which our definition omits; in our simulation this moves about 11 % of our lowest true-Eavail bin out of it, with the sign of the residual, but its effect on the two common cells has not been computed, so the comparison is not quantitative.”

write:

> “The published measurement uses a broader available-energy definition. In simulation, the difference moves about 11% of events out of our lowest true-\(E_{\rm avail}\) bin, in the direction of the observed residual. Its effect on the two common cells has not been evaluated, so the comparison is qualitative.”

The limitations concerning response mismatch and regularization bias belong beside Fig. 2. They are appropriately prominent there because they directly affect its interpretation.

**VII A. Hypotheses, statistics, and calibration**

The mathematical structure is recognizable as a PRD methods section. The vocabulary and chronology obscure it.

For:

> “We call this hypothesis the hybrid null: it is the hypothesis the calibration simulates, and for the Tune v1, the analysis simulation itself, it is H0 exactly.”

write:

> “For external generators, the simulated null reproduces the generator’s fine-grid cell cross sections while retaining Tune v1 conditional shapes within each cell. We refer to this as a hybrid hypothesis. For Tune v1, the simulated and stated hypotheses coincide.”

This states the actual model before naming it.

The passage:

> “The hypotheses, statistics, shifted nulls, multiplicity and stopping rules, and every input were fixed before any production pseudo-experiment was run or any observed statistic computed.”

should be shortened and reconciled with the subsequent qualifications:

> “The production calibration followed a fixed specification of hypotheses, statistics, nuisance variations, and stopping rules. Test development followed inspection of descriptive data residuals, and the computing allocation was subsequently extended while p values were visible.”

Then explain the statistical consequences. Repeated declarations that specifications were fixed do not establish validity.

The separate paragraph cataloguing post-decision studies can mostly move to a supplemental methodological chronology. Retain a clear label on each exploratory result in the main text.

**VII B. Conditions**

The title sounds contractual. “Scope of the calibrated hypotheses” would be more informative.

The most problematic wording is:

> “a value adopted when the test was designed whose calculation is not recorded”

An experienced author cannot repair that scientifically through style alone. The replacement must expose the assumption:

> “The decision procedure assumed a geometric decrease of unresolved grid effects and used shifts of \(\pm2\delta_{\rm fine}\). The derivation of the assumed decrease is unavailable, and the measured refinement sequence does not establish convergence. These shifts therefore provide a directional sensitivity test rather than a validated bound on within-cell generator dependence.”

The six conditions should not have equal rhetorical weight. Missing calorimetric response and unresolved hybridization are primary interpretation limits. Finite generator statistics and simulation sample size are implementation issues whose treatment must be demonstrated.

**VII C. Results**

This section mixes results with computing operations.

The passage:

> “Computing time limits interrupted or prevented 224 calibration and 53 power pseudo-experiments. All of them were rerun with a procedure fixed in advance [34], and none reaches the observed statistic in any test or shifted null, so no assignment of the lost outcomes changes any decision.”

can become:

> “Previously incomplete pseudo-experiments were recovered and do not change any rejection decision.”

Keep the counts and recovery procedure in the supplement. Reconcile the power denominators before making that statement.

The following passage is already clear and appropriately candid:

> “so this study provides no evidence of additional discrimination from the joint five-observable information.”

Retain that conclusion. Add that the projection study was post hoc and compared rejection outcomes; it is not a general equivalence or power result.

**VII D. Hadronic-response condition**

This is a necessary section, not excessive defensiveness. Its limitation is central.

The list:

> “Particle-species, energydependent, and resolution effects, a response difference applied before calibration, and larger variations were not tested.”

would read better as:

> “The study varies only a global recoil-energy scale. It does not propagate particle-dependent response, energy dependence, resolution changes, or a varied response through the null calibration; larger scale shifts were also not tested.”

The section should lead with the absent uncertainty and the scope of the check, then give the numerical result. Its present substance should remain in the main paper.

**VIII. Conclusions**

The conclusion repeats too much of the validation ledger.

For:

> “The results are of three kinds.”

and the ensuing inventory, use a scientific synthesis:

> “OmniFold approximately reproduces the published muon-kinematic cross section and provides simultaneous central-value estimates for five observables. In the configurations studied, plausible truth deformations expose substantial regularization bias, and the tested five-observable intervals fail coverage. The resulting central values therefore support descriptive comparisons.”

Then discuss the conditional tests:

> “Full-chain pseudo-experiment calibration rejects all five hybrid generator hypotheses under the implemented nuisance model. The missing calorimetric-response uncertainty and unresolved within-cell generator dependence limit their physical interpretation. Matched coarse projections already reject each hypothesis in at least one comparison, so added discrimination from the joint information has not been demonstrated.”

The exact-split learner’s one-unit change in \(\chi^2/\mathrm{ndf}\), the training-covariance details, and the full list of validation omissions do not belong in the conclusion.

**Acknowledgments**

The AI disclosure is unusually long and adopts the same process-assurance register:

> “Results were accepted only after verification against committed evidence: predeclared criteria, independent recomputation by separately written code (for example, the joint-test evaluation and the lost-seed recovery), and independent read-only reviews.”

A more conventional disclosure would be:

> “The authors used Anthropic Claude and OpenAI GPT tools to assist with analysis software, statistical studies, figures, and manuscript preparation. The authors reviewed the outputs and take responsibility for the analysis and manuscript. Numerical cross-checks are described in the relevant methods sections.”

Retain any version information required by journal policy, preferably in a compact disclosure. The use of AI for “independent review” must not imply independent scientific validation. Distinct implementations can expose coding errors; they can also share assumptions and conceptual mistakes.

The statement about not using generative image tools seems unnecessary unless required by policy. Complete the funding acknowledgment.

**Data availability and references**

This section currently reads like a release-readiness memorandum:

> “A candidate release package of about 16 MB [39], prepared locally but not yet deposited, needs only numpy, scipy, and matplotlib.”

The final article should say:

> “The archived numerical release at [persistent identifier] contains the calibrated test ensembles, evaluation code, and inputs for Figs. 1–4. The accompanying manifest identifies which quoted results it reproduces and which require event-level reprocessing.”

That wording must await a release that actually contains those products. Until then, state the present incompleteness plainly.

Internal orchestration paths and project records should be consolidated into a stable analysis note, supplement, and archival release. Their scientific content may be valuable; their workflow names are not useful bibliographic descriptions.

The recurring limitations should be consolidated as follows:

- **Coverage failure and regularization bias:** abstract, validation results, and a concise conclusion.
- **Missing calorimetric response and unresolved hybridization:** abstract and generator-test interpretation.
- **Learner selection chronology:** one methodological disclosure.
- **Earlier defective uncertainty versions:** supplement, with one main-text sentence explaining why current coverage remains unvalidated.
- **Lost jobs, review records, computing extensions, and release permissions:** statistical-procedure disclosure where consequential; otherwise supplement or archive.

---

**Part 3 — Abstract**

**(a) Headline results and qualifications**

The abstract contains six sentences.

1. **“We apply OmniFold…”** establishes the application and potential novelty.
2. **“The analysis reproduces…”** carries the principal positive measurement-method result: approximate two-dimensional reproduction and extension to five observables.
3. **“The three- to five-observable results are central values only.”** is an essential qualification.
4. **“Pseudo-experiments reveal…”** carries a substantive negative result, combined with a precision-target qualification. The bias findings are scientifically more important than whether a particular 10% target was chosen in advance.
5. **“Tests calibrated…”** carries the principal inference result.
6. **“Their interpretation is limited…”** states two essential assumptions and one negative result about added discrimination.

The abstract therefore contains real results, but its last sentence compresses too many distinct messages. It also omits the severity of the coverage failure while spending words on the administrative status of the precision target.

**(b) Proposed abstract — 157 words**

> We apply OmniFold to MINERvA open data for medium-energy muon-neutrino charged-current inclusive interactions. The unfolded muon-kinematic cross section reproduces the published integral within 1.1%, with 95.6% of reported bins agreeing within 10%. We extend the unfolding to five simultaneous observables by including available hadronic energy, three-momentum transfer, and hadronic invariant mass. Simulation studies identify background-subtraction and regularization biases; tested five-observable intervals fail coverage, and model dependence of approximately 10–13% per cell exceeds the chosen precision target. We therefore report higher-dimensional central values without validated total uncertainties. Generator tests calibrated through the full analysis chain reject five hybrid generator hypotheses in normalization and shape at a nominal 5% familywise level. These conclusions are conditional on the implemented nuisance model, which omits calorimetric recoil-response uncertainty, and on the within-cell shapes used to construct the hypotheses. Matched coarse projections also reject every hypothesis in at least one comparison, so additional discrimination from the joint information is not established.

“Nominal” is deliberate pending resolution of the sequential-calibration issue. If that issue is resolved, it can be removed.

**(c) What was dropped or changed, and where it belongs**

- **The claim that the precision target was predefined:** put its definition and timing in Sec. V. It does not change what the abstract’s result means.
- **The implication that model dependence alone establishes a general impossibility:** restrict the conclusion to the tested configurations and reporting definitions in Sec. V.
- **Detailed fine-grid convergence language:** give the grid, refinement results, directional shifts, and unresolved residual in Sec. VII. The abstract retains the essential dependence on within-cell shapes.
- **“Pseudo-experiments that rerun the full analysis chain”:** shortened to “calibrated through the full analysis chain”; the detailed generative procedure belongs in Sec. VII A.
- **The separate central-values-only sentence:** incorporated into the consequence of the validation findings.
- **The vague reference to regularization limitations:** supplemented with the concrete coverage failure, which a reader needs to understand the status of the unfolded results.

---

**Part 4 — Additional advice**

The paper’s credibility will improve if the authors distinguish three kinds of statements consistently: an observed numerical result, a demonstrated validation property, and an assumption required for interpretation. Much of the current difficulty comes from moving between them within the same paragraph.

Several points deserve emphasis.

First, a negative methodological result can make a strong paper. Demonstrating that plausible deformations produce large unfolding bias, that attractive-looking projections can coexist with failed coverage, and that calibrated testing has limited power against some alternatives is useful science. Those results deserve figures and interpretation, not presentation as unfortunate obstacles encountered before reaching the headline exclusions.

Second, predeclaration is helpful but is receiving too much argumentative weight. It limits some opportunities for selective analysis. It does not validate an uncertainty model, establish convergence, turn a directional sensitivity scan into a bound, or make optional stopping harmless.

Third, the paper should explain why unfolding is useful for these generator tests. A reconstructed-space comparison could avoid part of the regularization and hybridization problem, although it would still require a credible response model. A comparison with such a baseline would help establish the value of the proposed inference route.

Fourth, uncertainty validation should be proportionate to the claim. The authors need not prove simultaneous coverage for every conceivable truth before publishing a methodological study. They do need to avoid presenting intervals as reliable where plausible tested truths already show dramatic failure.

Finally, the manuscript should receive a substantive human scientific revision before resubmission. The acknowledgments describe extensive AI-assisted production and review. That is not itself an objection to the work. But the authors must be able to defend the null hypotheses, nuisance ensemble, sequential calibration, detector assumptions, and physical interpretation directly. The present abundance of process documentation cannot substitute for that scientific argument.

---

## P21. X3 Gemini 3.8 Flash: outline analysis of the pass-2 paper and primer (sha256 `0730cd2668c8d0f2…`)

As an editor for *Physical Review D* and *Physical Review Letters* and a former experimental particle physicist, here is the comprehensive structural analysis of the two documents.

---

##### 1. Paragraph Main-Idea Map

*Rules: Main ideas are strictly formulated in one sentence of at most 25 words. Paragraphs are identified by opening phrases and tagged as `[NONE]`, `[MULTI]`, `[HIST]`, `[CAVEAT]`, `[RESULT]`, or `[METHOD]`.*

###### A. Research Paper (`paper.txt`)

* **Abstract** (“We apply OmniFold to MINERvA open data...”): OmniFold reproduces 2D MINERvA cross sections and extends to 5D central values, while calibrated tests reject five generator predictions under stated limitations. (22 words) — **`[MULTI]`**
* **I.1** (“Multidifferential neutrino cross sections test interaction models...”): OmniFold enables simultaneous multidimensional unbinned cross-section unfolding, bypassing the exponential binning growth that limits traditional migration matrices. (18 words) — **`[METHOD]`**
* **I.2** (“We apply the method to MINERvA medium-energy...”): The analysis applies OmniFold to MINERvA data, reproducing 2D muon kinematics and extending to 3D, 4D, and 5D central values. (21 words) — **`[METHOD]`**
* **I.3** (“We assess how reliable the method is in practice...”): The authors validate the method through 2D comparisons, closure tests, and pseudo-experiments to identify limits on a 5D measurement. (20 words) — **`[METHOD]`**
* **I.4** (“As an application, we test specified generator predictions...”): Full-chain calibrated hypothesis tests evaluate five generator models, incorporating the unfolding estimator’s prior bias into the simulated null distributions. (20 words) — **`[METHOD]`**
* **I.5** (“The two-dimensional reproduction agrees with the published...”): The analysis reproduces published 2D results and rejects generator hypotheses, but substantial biases, seed dependence, and mismodelling limit 5D measurements. (21 words) — **`[MULTI]`**
* **I.6** (“Sections II and III describe the data and estimators...”): The introduction outlines the manuscript’s structure across data, estimators, validation, uncertainties, central values, and joint hypothesis tests. (19 words) — **`[NONE]`**
* **II.1** (“The analysis uses the twelve MINERvA medium-energy...”): The dataset comprises MINERvA medium-energy neutrino data with 4.12 million selected events, simulated using tuned GENIE 2.12.6. (18 words) — **`[METHOD]`**
* **II.2** (“The unfolded observables are defined at truth level...”): Truth-level observables comprise muon momentum components, momentum transfer, invariant mass, and available energy, which share reconstructed calorimetric inputs. (19 words) — **`[METHOD]`**
* **II.3** (“Event selection is held fixed as the classifier inputs...”): Event selection requires a tracker vertex and MINOS-matched muon, while external generator predictions are reweighted to the analysis flux. (20 words) — **`[METHOD]`**
* **III.1** (“Each OmniFold iteration consists of two classification steps...”): OmniFold iteratively reweights simulated events using reconstruction-level and truth-level classifiers to derive cross sections from final event weights. (19 words) — **`[METHOD]`**
* **III.2** (“Backgrounds enter the reconstruction-level step through...”): Backgrounds are handled either via binned purity weights or through unbinned negative-weight simulation refined by a classifier. (17 words) — **`[METHOD]`**
* **III.3** (“All estimator configurations use five OmniFold iterations...”): The unfolding uses five iterations of gradient-boosted decision trees, specifying configurations for central values and joint hypothesis tests. (19 words) — **`[METHOD]`**
* **IV.0** (“In closure tests, truth denotes the known simulated target...”): Closure tests assess the recovery of known distribution deformations, whereas coverage tests evaluate whether constructed intervals contain the truth. (20 words) — **`[METHOD]`**
* **IV.A.1** (“The two-dimensional result is an end-to-end test...”): OmniFold reproduces the published 2D cross section within 1.1% globally, though learner choice shifts agreement by one chi-squared unit. (20 words) — **`[RESULT]`**
* **IV.A.2** (“Both results derive from the same data...”): Because both results derive from identical data, rigorous statistical comparison of their differences would require their unmeasured cross-covariance. (19 words) — **`[CAVEAT]`**
* **IV.B.1** (“The covariance of our two-dimensional result is the sum...”): The 2D covariance combines systematic, statistical, training-seed, and run-period components, yielding a median 6.45% per-bin uncertainty dominated by systematics. (19 words) — **`[METHOD]`**
* **IV.B.2** (“The systematic-universe unfoldings approximate the weighting...”): Unresolved run-period inconsistencies and approximations for unselected events are incorporated into the covariance without proving coverage or identifying causes. (19 words) — **`[MULTI]`**
* **IV.B.3** (“The statistical block is a bootstrap of 300 replicas...”): An earlier statistical uncertainty band undercovered in pseudo-experiments and was rebuilt post hoc, leaving the quoted band's coverage untested. (20 words) — **`[HIST]`**
* **IV.B.4** (“In summary, we report a reproducible two-dimensional central value...”): The reported 2D covariance lacks coverage validation and omits machine-learning learner dependence, reconstruction approximations, and model dependence. (18 words) — **`[CAVEAT]`**
* **IV.C.1** (“Each higher-dimensional central value is checked against...”): Higher-dimensional marginal normalizations agree with lower projections, but purity background subtraction induces an uncorrected 4% bias at high invariant mass. (20 words) — **`[MULTI]`**
* **IV.C.2** (“The unfolding recovers only part of a change of the Eavail shape...”): Regularization bias, numerical rounding instability, and failed statistical interval coverage preclude claiming frequentist coverage for five-dimensional results. (18 words) — **`[CAVEAT]`**
* **V.1** (“We have built a covariance for the five-dimensional central value...”): The 5D covariance violates predefined stability criteria by exhibiting 6% seed dependence, precluding covariance-based generator significance. (17 words) — **`[CAVEAT]`**
* **V.2** (“A separate study looked for a definition of a five-dimensional measurement...”): Model dependence of 10–13% per cell exceeds predefined precision targets, preventing a 5D measurement and motivating calibrated hypothesis tests. (19 words) — **`[CAVEAT]`**
* **VI.1** (“The comparisons in this section are descriptive...”): Unfolded central values reveal an excess over predictions at low available energy, partially mitigated by adding two-particle–two-hole contributions. (19 words) — **`[RESULT]`**
* **VI.2** (“Adding q3 resolves the momentum-transfer dependence...”): Adding three-momentum transfer shows agreement within 10% of MINERvA's low-recoil measurement, though differing particle definitions preclude exact comparison. (19 words) — **`[RESULT]`**
* **VI.3** (“The fifth observable, W, separates the remaining discrepancy...”): The 5D central value reveals an unmodelled excess over Tune v1 concentrated at high available energy and high invariant mass. (21 words) — **`[RESULT]`**
* **VI.4** (“The one-dimensional projections in Fig. 3 compare...”): External generators underpredict data across kinematics, demonstrating that the localized high-energy, high-mass discrepancy is specific to Tune v1. (19 words) — **`[RESULT]`**
* **VII.A.1** (“For each of five predictions G...”): Five generator models are formulated as hybrid null hypotheses on a fine 5D grid and evaluated on coarse bins. (20 words) — **`[METHOD]`**
* **VII.A.2** (“A total statistic Ttot = r⊤ Σ−1 r is formed...”): Total and shape test statistics use a regularized covariance metric derived from simulated null pseudo-experiments and generator sample variances. (20 words) — **`[METHOD]`**
* **VII.A.3** (“The null distribution of each statistic is obtained from pseudo-experiments...”): Full-chain pseudo-experiments incorporate systematic uncertainties and estimator prior bias into calibrated null distributions for each generator. (18 words) — **`[METHOD]`**
* **VII.A.4** (“The ten tests are controlled at a familywise level...”): Ten hypothesis tests are evaluated using Clopper–Pearson intervals and controlled at 5% familywise significance via the Holm procedure. (19 words) — **`[METHOD]`**
* **VII.A.5** (“Some choices were made after results had been seen...”): Several analysis choices, including budget extensions and projection comparisons, were decided after inspecting intermediate data and test outcomes. (19 words) — **`[HIST]`**
* **VII.B.1** (“The decisions test the hybrid null. Each holds under six conditions...”): The generator rejections depend strictly on six conditions, notably unverified fine-grid convergence and the absence of calorimetric recoil-response uncertainties. (20 words) — **`[CAVEAT]`**
* **VII.C.1** (“Table I lists the ten decisions...”): All ten hybrid null hypotheses are rejected at 5% familywise significance, with robustness scans confirming stability along one grid-shift vector. (21 words) — **`[RESULT]`**
* **VII.C.2** (“Computing time limits interrupted or prevented 224 calibration...”): Rerunning lost pseudo-experiments confirms that computing timeouts did not alter any hypothesis test decision. (16 words) — **`[RESULT]`**
* **VII.C.3** (“The comparisons recover the generator disagreements...”): Calibrated tests reject generators but show no greater discrimination in 5D than in matched 2D projections. (17 words) — **`[RESULT]`**
* **VII.D.1** (“MINERvA’s recoil-energy analyses assign a hadronic-energy response uncertainty...”): Omitting a calorimetric recoil-energy response systematic is critical because generator rejection relies entirely on hadronic observables. (17 words) — **`[CAVEAT]`**
* **VII.D.2** (“In an exploratory sensitivity study [37], the data are re-unfolded...”): Rejections withstand a global ±4% recoil energy scale shift, but energy-dependent and species-specific response uncertainties remain unassessed. (18 words) — **`[CAVEAT]`**
* **VIII.1** (“This study applies OmniFold to MINERvA inclusive charged-current data...”): OmniFold reproduces 2D cross sections and yields 5D central values, but model dependence and biases prevent a 5D measurement. (20 words) — **`[MULTI]`**
* **VIII.2** (“The joint tests are calibrated generator tests...”): Calibrated full-chain tests reject five generator predictions, though without demonstrated additional multidimensional power and subject to unmodelled hadronic response. (21 words) — **`[MULTI]`**

---

###### B. Plain-Language Primer (`primer.txt`)

* **Abstract** (“This is a short, jargon-light guide...”): The primer introduces OmniFold unfolding on MINERvA data, summarizing 2D reproduction, 5D central-value trends, generator rejections, and signal definitions. (20 words) — **`[MULTI]`**
* **1.1** (“A neutrino is a nearly invisible particle...”): Neutrinos interact rarely, producing charged particles like muons whose energies and angles define cross sections in the MINERvA detector. (20 words) — **`[METHOD]`**
* **1.2** (“The difficulty is that the detector never measures these quantities perfectly...”): Detector blur smears recorded particle properties, requiring delicate unfolding algorithms to recover true physical distributions without amplifying noise. (19 words) — **`[METHOD]`**
* **2.1** (“The traditional way to unfold builds a big table...”): Traditional migration matrices scale poorly to higher dimensions because multiplying bins rapidly degrades simulation precision and matrix conditioning. (19 words) — **`[METHOD]`**
* **2.2** (“This analysis uses a different, machine-learning method called OmniFold...”): OmniFold trains neural or tree classifiers to iteratively reweight simulated events to match observed data at reconstructed and truth levels. (20 words) — **`[METHOD]`**
* **2.3** (“The decisive advantage is what happens when you want to measure more...”): OmniFold scales to multiple observables without expanding bin grids, though computational demands and uncertainty validation remain challenging. (18 words) — **`[METHOD]`**
* **2.4** (“In a simulated experiment, truth is the known answer...”): Validation requires distinguishing truth, prior models, detector response, closure tests, interval coverage, numerical stability, and bias. (17 words) — **`[METHOD]`**
* **2.5** (“One more distinction matters later: which events are kept...”): The analysis uses gradient-boosted decision trees on MINOS-matched muon events to infer cross sections from reconstructed summary quantities. (19 words) — **`[METHOD]`**
* **3.Intro** (“Our results have different levels of validation...”): Findings are organized by validation level, spanning primary measurements, caveats, simulation tests, and exploratory studies. (17 words) — **`[NONE]`**
* **3.Bullet1** (“• A published result, reproduced...”): OmniFold reproduces the published 2D result within 1%, but error bars have untested coverage and depend on software implementations. (20 words) — **`[MULTI]`**
* **3.Bullet2** (“• More quantities at once...”): Higher-dimensional results are reported as central values only due to uncorrected biases, failed coverage, and seed dependence. (18 words) — **`[CAVEAT]`**
* **3.Bullet3** (“• Known and new features in the data...”): Data exceed simulations at low available energy and reveal an unmodelled excess over Tune v1 at high kinematic values. (21 words) — **`[RESULT]`**
* **3.Bullet4** (“• A joint test of five simulations...”): A full-chain test rejects five generator predictions at 5% error level under conditions omitting recoil response uncertainties. (19 words) — **`[RESULT]`**
* **3.Bullet5** (“• A neural network on raw detector data...”): Point-cloud transformer networks reading raw detector deposits remain exploratory method development without contributing final measurements. (16 words) — **`[HIST]`**
* **3.Bullet6** (“• A wider signal definition...”): Expanding the signal definition beyond published muon limits increases the target population, but much of the extension remains simulation-dominated. (20 words) — **`[METHOD]`**
* **3.Outro** (“Each result is only as validated as its own checks.”): Every reported finding carries validity strictly bounded by the specific checks and diagnostics performed on it. (17 words) — **`[CAVEAT]`**
* **3.Trust.1** (“Before trusting a new method, one must show it reproduces...”): The 2D OmniFold cross section and uncertainties closely match published MINERvA values, though a correlated shape difference remains. (19 words) — **`[RESULT]`**
* **3.Trust.2** (“One qualification: two software implementations of the tree learner...”): Switching between two tree implementations shifts bin values by 1%, and the quoted result was selected post hoc. (19 words) — **`[HIST]`**
* **3.Trust.3** (“The error budget also has known limits...”): The 2D error budget was rebuilt to correct previous flaws, but it still omits reconstruction approximations and model dependence. (20 words) — **`[HIST]`**
* **3.Trust.4** (“To test whether error bars have the right size...”): Rigorous coverage validation requires independent large-scale simulations and uninspected generator samples that are unavailable here. (16 words) — **`[CAVEAT]`**
* **3.Trust.5** (“We did run such a test on the statistical part...”): Simulated tests showed statistical error bars undercovered in high-momentum regions, prompting a post hoc rebuild that remains untested. (19 words) — **`[HIST]`**
* **3.More.1** (“With the central value reproduced, and its error bars found...”): OmniFold successfully unfolded up to five simultaneous observables, with marginal normalizations agreeing with lower-dimensional results. (17 words) — **`[RESULT]`**
* **3.More.2** (“These are five recorded coordinates, not five demonstrated independent...”): Reconstructed momentum transfer, invariant mass, and available energy reuse calorimetric inputs, representing correlated coordinates rather than independent constraints. (19 words) — **`[CAVEAT]`**
* **3.More.3** (“The first physics payoff appears in the available energy...”): The unfolded available energy confirms the low-recoil discrepancy seen in earlier data, which two-particle–two-hole processes partially resolve. (18 words) — **`[RESULT]`**
* **3.Puzzle.1** (“Adding the hadronic-mass axis W lets us look...”): The 5D central value exposes an excess over Tune v1 concentrated at high available energy and high invariant mass. (20 words) — **`[RESULT]`**
* **3.Limits.1** (“The multi-quantity central values above pass the validation tests...”): Higher-dimensional results are restricted to central values because of uncorrected biases, unvalidated uncertainties, seed sensitivity, and failed numerical stability. (20 words) — **`[CAVEAT]`**
* **3.Limits.2** (“Biases in following a changed truth...”): Unfolding only partially recovers generator-scale shape changes and introduces background-subtraction biases that are omitted from quoted uncertainties. (18 words) — **`[CAVEAT]`**
* **3.Limits.3** (“An uncertainty that has not been validated...”): The 5D uncertainty shifts 6% across random seeds and failed its coverage test, precluding claims of statistical significance. (19 words) — **`[CAVEAT]`**
* **3.Limits.4** (“Numerical stability...”): The unfolding shifts under different numerical rounding, failing a stability test but matching the variability seen in bootstrap resampling. (19 words) — **`[CAVEAT]`**
* **3.Limits.5** (“A narrower point concerns what the detector uncertainties cover...”): While muon tracking uncertainties were re-simulated end to end, hadronic response variations rely on reweighting and may be incomplete. (19 words) — **`[CAVEAT]`**
* **3.Limits.6** (“None of these five-quantity findings affects the two-dimensional trust check...”): Technical failures and limitations identified in five dimensions do not invalidate the separate uncertainty budget established for 2D kinematics. (19 words) — **`[METHOD]`**
* **3.Joint.1** (“We also asked a sharper question: under stated modelling assumptions...”): Calibrated hypothesis tests evaluate whether five generator predictions match the data across five dimensions, using hybrid null distributions. (19 words) — **`[METHOD]`**
* **3.Joint.2** (“Rather than rely on a textbook formula for how the test statistic...”): Full-chain pseudo-experiments account for prior bias and nuisance variations, rejecting all ten generator hypotheses at the 5% error level. (20 words) — **`[RESULT]`**
* **3.Joint.3** (“This is a test of the simulations under six conditions...”): Generator rejections are conditional because the nuisance model omits calorimetric recoil response uncertainties and unmeasured sub-grid structure. (18 words) — **`[CAVEAT]`**
* **3.Joint.4** (“In a comparison chosen after the result was known (post hoc)...”): Post hoc checks reveal hadronic observables drive the rejections, though 5D tests add no demonstrated power over 2D projections. (19 words) — **`[CAVEAT]`**
* **3.Alt.1** (“Two studies test the method’s limits rather than adding...”): Exploratory studies examine point-cloud neural networks and wider signal definitions to test methodological limits. (15 words) — **`[METHOD]`**
* **3.Alt.2** (“PET is a different learner from the tree learner...”): The PET point-cloud transformer processes raw energy clusters, demonstrating unbinned processing of low-level detector data for hadronic recoils. (19 words) — **`[METHOD]`**
* **3.Alt.3** (“Studies on simulated samples that contain signal events only then improved...”): PET designs improved shape recovery in simulation but failed predefined robustness and coverage criteria, preventing their use in measurements. (19 words) — **`[HIST]`**
* **3.Alt.4** (“Separately, the published signal definition excludes about a third...”): Removing kinematic cuts enlarges phase space, but 28% of the resulting cross section represents unmeasured, simulation-dependent extrapolation. (18 words) — **`[CAVEAT]`**
* **4.1** (“Unbinned machine-learning unfolding reproduces a flagship MINERvA measurement...”): OmniFold enables multidimensional neutrino unfolding and calibrated generator rejections, but substantial biases, unvalidated uncertainties, and model dependence limit measurements. (21 words) — **`[MULTI]`**

---

##### 2. The Argument Outline

###### Actual Line of Argument in `paper.txt` (11 Bullets)
1. **Methodological Promise**: Unbinned machine-learning unfolding (OmniFold) circumvents the curse of dimensionality inherent in traditional binned migration matrices, enabling simultaneous multi-observable neutrino cross-section measurements.
2. **External Validation (2D)**: When applied to MINERvA medium-energy data, OmniFold reproduces the published double-differential muon cross section within 1.1% globally and yields comparable uncertainty magnitudes.
3. **2D Caveats**: The 2D result exhibits learner dependence ($\Delta\chi^2 \approx 1$ between LightGBM and exact-split trees), uncorrected unselected-event approximations, an ad-hoc run-period covariance block, and untested interval coverage.
4. **Higher-Dimensional Central Values**: Extending unfolding to five simultaneous observables ($(p_T, p_\parallel, E_{\text{avail}}, q_3, W)$) produces self-consistent marginal normalizations and reproduces the established low-recoil discrepancy (partially mitigated by 2p2h physics).
5. **Emergence of Severe Biases**: End-to-end pseudo-experiments in higher dimensions reveal an uncorrected 4% background-subtraction bias in high-$W$ cells and massive regularization bias (up to 74% deviation under generator-scale shape changes).
6. **Failure of the 5D Uncertainty Budget**: The 5D covariance fails predefined stability criteria (shifting 6.1% under random-seed changes), statistical intervals fail frequentist coverage, and model dependence reaches 10–13% per cell, exceeding the predefined 10% precision target.
7. **The Pivot to Descriptive Reporting**: Because a rigorous 5D measurement with valid uncertainties cannot be achieved, higher-dimensional distributions are demoted to descriptive, unquantified central values (locating an excess over Tune v1 at high $E_{\text{avail}}$, high $W$).
8. **Alternative Inference via Hypothesis Testing**: To extract rigorous physics without relying on a 5D measurement covariance, the authors pivot to full-chain calibrated hypothesis tests of five generator models.
9. **Simulation-Based Calibration**: Generating null pseudo-experiments through the complete analysis chain incorporates the estimator's prior bias and nuisance variations directly into the test statistic distributions.
10. **Rejection of Generator Hypotheses**: All ten tests (five generators, evaluated in total rate and shape) reject the hybrid null hypotheses at the familywise $\alpha = 0.05$ level via the Holm procedure.
11. **Severe Interpretive Boundaries**: The rejections provide no demonstrated multidimensional power beyond matched 2D projections, lack proof of sub-grid convergence, and—most critically—are conditional on a simulation lacking calorimetric recoil-energy response uncertainties.

###### Standard PRD Experimental Unfolding/Generator Paper Structure
A standard PRD paper reporting a multidimensional cross-section measurement and generator comparisons follows an established, monotonic narrative:
1. **Introduction**: Neutrino oscillation context, cross-section uncertainties, limitation of previous binned measurements, and motivation for higher dimensions.
2. **Experimental Setup & Dataset**: NuMI beam flux, MINERvA detector, MINOS spectrometer, and event selection criteria.
3. **Signal Definition & Background Modeling**: True fiducial phase space, background processes, sideband fitting, and constraint procedures.
4. **Unfolding Methodology**: Mathematical formulation of the unfolding algorithm, regularization scheme, and mock-data closure tests establishing bias-free behavior.
5. **Systematic Uncertainties**: Detailed breakdown of flux, interaction models, detector response (including dedicated test-beam hadronic calorimetry), and covariance matrix construction with demonstrated coverage.
6. **Cross-Section Results**: Tabulated and plotted differential cross sections with full covariance matrices across all reported dimensions.
7. **Model Comparisons & Physics Discussion**: Goodness-of-fit $\chi^2$ evaluations comparing data against generators (GENIE, NuWro, GiBUU), dissecting nuclear mechanisms (2p2h, RPA, FSI).
8. **Conclusions**: Summary of measured cross sections and guidance for generator tuning.

###### Structural Departures, Analysis, and Assessment
This paper departs radically from the PRD archetype in three structural ways:
1. **The "Failed Measurement Pivot" (Sec. V $\rightarrow$ Sec. VII)**: Instead of progressing from uncertainties to cross sections to model tests, the paper conducts an autopsy on its 5D uncertainty budget in Section V (admitting model dependence of 10–13% killed the measurement), strips Section VI of all error bars, and invents a fallback hypothesis-testing framework in Section VII.
2. **Decoupling Measurement from Inference**: In a typical paper, model tests are $\chi^2$ comparisons derived directly from the measurement's data vector and covariance matrix. Here, because the measurement covariance is unstable, the authors construct an entirely separate, simulation-calibrated pseudo-experiment apparatus to test hypotheses.
3. **Interleaving Validation with Historical Forensics**: Section IV and V read like an internal collaboration analysis log, documenting earlier flawed iterations, post hoc band rebuilds, software implementation shootouts, and failed coverage tests.

**Does it help or hurt?**
* **Methodologically & Ethically (Helps)**: It represents exemplary scientific integrity. Rather than sweeping 10–13% model dependence, seed instability, and 74% regularization bias under the rug, the authors refuse to publish unvalidated error bars. The calibrated full-chain hypothesis test is a brilliant statistical contribution to machine-learning unfolding, correctly capturing prior pull under the null.
* **Rhetorically & Structurally (Hurts)**: For a PRD physics readership, it creates severe cognitive whiplash. The reader is promised a 5D measurement, shown a post-mortem of why a 5D measurement is impossible, shown unquantified 5D plots anyway, and then redirected to a hypothesis test that turns out to have no calorimetric recoil uncertainty and no added power over 2D projections. The narrative tension between celebrating a breakthrough and cataloging its failures paralyzes the paper.

---

##### 3. Proportions

###### Estimated Text Distribution per Section (`paper.txt`)

| Section | Method | Results | Caveats / Limits | History / Forensics |
| :--- | :---: | :---: | :---: | :---: |
| **Abstract** | 15% | 25% | 60% | 0% |
| **I. Introduction** | 35% | 20% | 40% | 5% |
| **II. Data, Signal, Simulation** | 85% | 0% | 15% | 0% |
| **III. Unbinned Unfolding** | 90% | 0% | 10% | 0% |
| **IV. Validation (A, B, C)** | 25% | 15% | 45% | 15% |
| **V. Status of 5D Uncertainty** | 10% | 0% | 80% | 10% |
| **VI. Central-Value Results** | 15% | 65% | 20% | 0% |
| **VII. Calibrated Joint Tests** | 35% | 25% | 30% | 10% |
| **VIII. Conclusions** | 15% | 30% | 55% | 0% |
| **OVERALL PAPER** | **~35%** | **~20%** | **~37%** | **~8%** |

###### Genre Appropriateness Assessment
The proportion profile is **heavily distorted and inappropriate for a standard experimental paper in *Physical Review D***. 
* A standard PRD experimental paper typically allocates **50–60% to Method/Setup**, **30–40% to Results/Physics Discussion**, and **5–10% to Systematics/Caveats**, with **0% allocated to internal project history**.
* In this paper, **Caveats (37%) and History (8%) consume nearly half the manuscript (45%)**, exceeding the space devoted to actual Results (20%). 
* While such an emphasis is appropriate for a diagnostic review, a methodological white paper in *Journal of Instrumentation* (JINST), or an internal collaboration analysis note, it suffocates the physics narrative of a PRD paper. The paper spends more time explaining why it cannot report a 5D measurement than reporting what it measured.

---

##### 4. Repetition

The manuscript suffers from chronic defensive repetition. The table below catalogs every limitation stated more than once and specifies its single best location.

| Limitation / Caveat | Specific Locations in `paper.txt` | Single Best Location | Editorial Rationale |
| :--- | :--- | :--- | :--- |
| **1. Absence of calorimetric recoil-energy response systematic** | • Abstract (sentence 6)<br>• Sec. I.5<br>• Sec. VII.B (condition ii)<br>• Sec. VII.D.1–2 (entire subsection)<br>• Sec. VIII.2 | **Section VII.D** (with a single-sentence mention in Abstract & Conclusions) | It is a technical limitation specific to the hypothesis test framework; burying it in five different sections dilutes its definitive technical treatment in VII.D. |
| **2. Unproven convergence of the fine grid ($\delta_{\text{fine}}$)** | • Abstract (sentence 6)<br>• Sec. I.5<br>• Sec. VII.B (condition i)<br>• Sec. VII.C.1<br>• Sec. VIII.2 | **Section VII.B (Condition i)** | Belongs strictly where the hybrid null hypothesis $H_0(G)$ is formally defined and its mathematical boundary conditions are established. |
| **3. Joint 5D information adds no discrimination beyond 2D projections** | • Abstract (sentence 6)<br>• Sec. I.5<br>• Sec. VII.C.3<br>• Sec. VIII.2 | **Section VII.C** | This is an empirical outcome of the statistical tests and should be stated once when presenting the hypothesis test results. |
| **4. Model dependence (10–13%) prevents meeting 10% target** | • Abstract (sentence 4)<br>• Sec. I.5<br>• Sec. IV.C.2<br>• Sec. V.2<br>• Sec. VIII.1 | **Section V.2** | Belongs exclusively in the section dedicated to the feasibility autopsy of the 5D measurement uncertainty budget. |
| **5. Estimator random-seed instability (6.1% vs 5% target)** | • Abstract (sentence 4)<br>• Sec. I.5<br>• Sec. IV.A.1<br>• Sec. V.1<br>• Sec. VIII.1 | **Section V.1** | Belongs in the technical discussion of covariance matrix properties and estimator stability in Section V. |
| **6. Higher dimensions are "central values only" / no coverage claim** | • Abstract (sentence 3)<br>• Sec. I.5<br>• Sec. IV.C.2<br>• Sec. V.1<br>• Sec. VI.1<br>• Sec. VIII.1 | **Section VI.1** (preamble to plots) | A single, clear programmatic warning at the start of the results section prevents reader misinterpretation without defensive clutter elsewhere. |
| **7. Background subtraction bias (up to 4% at high $W$)** | • Abstract (sentence 4)<br>• Sec. I.5<br>• Sec. III.3<br>• Sec. IV.C.1<br>• Sec. VIII.1 | **Section IV.C** | Belongs in the validation discussion of higher-dimensional mock data and purity subtraction. |
| **8. Severe regularization bias (up to 74% at high $W$)** | • Abstract (sentence 4)<br>• Sec. I.5<br>• Sec. IV.C.2<br>• Sec. VI.3<br>• Sec. VIII.1 | **Section IV.C** | Belongs in the closure test analysis of Section IV, where shape deformations are explicitly quantified. |
| **9. Learner dependence ($\Delta\chi^2 \approx 1$ between tree codes)** | • Sec. III.3<br>• Sec. IV.A.1<br>• Sec. IV.B.4<br>• Sec. VIII.1 | **Section IV.A** | Belongs in the 2D reproduction comparison where the numerical discrepancy between LightGBM and scikit-learn is evaluated. |
| **10. Untested coverage / post hoc rebuild of 2D statistical band** | • Abstract (sentence 4)<br>• Sec. I.5<br>• Sec. IV.B.3<br>• Sec. IV.B.4<br>• Sec. VIII.1 | **Section IV.B** | Belongs in the systematic breakdown of the 2D covariance matrix blocks. |

---

##### 5. The Abstract of the Paper

###### Sentence-by-Sentence Breakdown & Labeling

1. *“We apply OmniFold to MINERvA open data for medium-energy $\nu_\mu$ charged-current inclusive interactions.”*  
   $\rightarrow$ **Context / Scope** (Method application).
2. *“The analysis reproduces the published double-differential cross section in muon kinematics, with the integrated cross section within about one percent, and extends it to five simultaneous observables by adding available energy, three-momentum transfer, and hadronic invariant mass.”*  
   $\rightarrow$ **Headline Result** (2D reproduction and 5D unbinned extension).
3. *“The three- to five-observable results are central values only.”*  
   $\rightarrow$ **Qualification / Demotion** (Stripping of measurement status).
4. *“Pseudo-experiments reveal background-subtraction and regularization biases, and the measured model dependence, about 10–13% per cell, prevents a five-dimensional measurement whose total uncertainties meet our predefined 10% precision target.”*  
   $\rightarrow$ **Qualification / Negative Result** (Failure of uncertainty budget and self-imposed target).
5. *“Tests calibrated with pseudo-experiments that rerun the full analysis chain reject the hybrid null hypotheses built from five generator predictions, in total and in shape, at the 5% familywise level.”*  
   $\rightarrow$ **Headline Result** (Rejection of five generator models at familywise 5% level).
6. *“Their interpretation is limited: the nuisance model has no calorimetric recoil-response uncertainty, convergence of the fine grid defining the null hypotheses has not been shown, and the joint five-observable information is not shown to discriminate beyond matched coarse projections.”*  
   $\rightarrow$ **Qualification / Boundary Condition** (Triple caveat on physical validity).

*Balance*: 2 Headline Results vs. 3 Heavy Qualifications (and 1 Context sentence).

###### What a 120–160-Word Abstract Would Keep
A standard PRD abstract must state: (1) what was done, (2) the principal quantitative measurement, (3) the primary physics outcome, and (4) the exact domain of validity. It must eliminate internal project history, self-imposed criteria autopsies, and nested hedges.

**Recommended Revised Abstract (142 words):**
> We demonstrate unbinned multidimensional cross-section unfolding on neutrino-scattering data using OmniFold applied to MINERvA medium-energy $\nu_\mu$ charged-current inclusive interactions. The method reproduces the published double-differential muon cross section to within 1.1% in total rate. We extend the unfolding to five simultaneous observables by incorporating available hadronic energy, three-momentum transfer, and invariant mass. While marginal distributions are self-consistent and recover established low-recoil enhancements, an unbinned model dependence of 10–13% per cell restricts the multidimensional results to central values. To enable rigorous inference without a measurement covariance, we evaluate five neutrino event generators using hypothesis tests calibrated through the full analysis chain. Under the baseline simulation response, all five generator hypotheses are rejected in total rate and shape at the 5% familywise significance level. The rejections are driven by hadronic observables, underscoring the necessity of incorporating calorimetric recoil-energy response uncertainties in multidimensional neutrino unfolding.

###### Why Honest Abstracts Grow and How to Stop It
* **The "Honesty Trap" (Epistemic Liability Creep)**: When conscientious physicists discover that a cutting-edge technique exhibits algorithmic instability (seed dependence, regularization bias, unvalidated coverage), they experience acute anxiety about misleading the community. Every positive claim feels fraudulent without an immediate disclaimer. Then, because the disclaimer itself has caveats (e.g., “we rejected the generators, *but* the null was a hybrid, *and* the fine grid didn't converge, *and* we lacked a recoil band”), the disclaimer spawns sub-clauses. The abstract degenerates into a legal deposition.
* **How to Stop It**:
  1. *Define the Validity Envelope Once*: Instead of making an unqualified claim and spending two sentences walking it back, state the conditional result directly (e.g., “Under the simulation's detector response model, we reject...”).
  2. *Excise Internal Governance*: Discard self-imposed administrative targets (“our predefined 10% target”, “our stopping rule”). PRD readers care about physical uncertainties, not the authors' internal milestone documents.
  3. *Separate Capability from Post-Mortem*: Announce what the method *can* reliably deliver (2D measurement; calibrated hypothesis tests; 5D central trends). Reserve the detailed post-mortem of failed error bars for the dedicated technical sections of the paper.

---

##### 6. Primer Analysis (Order of Sections & Proposed Structure)

###### Does the Current Order Serve a Non-Specialist?
**No, it severely disserves a non-specialist.** While the prose itself is admirably clear and accessible, the macro-structure is pedagogically dysfunctional:
1. **Redundant Executive Summary (Section 3 Intro)**: Section 3 opens with an 8-paragraph bulleted list that summarizes the entire remainder of the document. A non-specialist is forced to read the results twice in succession.
2. **The "Bait-and-Switch" Narrative**: Section 3 presents exciting physics discoveries (“rediscover known physics”, “a new puzzle for the tuned simulation”), only to follow them with an exhaustive, demoralizing 6-paragraph autopsy of technical failures (“Limits on the multi-quantity results”). The reader is told that the plots they just inspected have unvalidated error bars, failed stability tests, and up to 74% bias.
3. **Distracting Methodological Cul-de-Sacs**: Subsections on PET (point-cloud transformers) and expanded fiducial definitions are dumped at the end of Section 3. These are inconclusive machine-learning R&D projects that contribute zero physics results to the paper and derail reader comprehension.
4. **Developer-Level Forensics**: Lengthy discussions regarding tree-learner software discrepancies (LightGBM vs. scikit-learn), rebuilt statistical error budgets, and 6.1% seed shifts belong in software issue trackers, not in a conceptual guide for physics-literate readers.

###### Proposed Logical Restructuring for the Primer

A non-specialist needs a pedagogical narrative: **Concept $\rightarrow$ Baseline Proof $\rightarrow$ What We Learned $\rightarrow$ Honest Boundaries $\rightarrow$ The Big Picture.**

* **1. The Goal: Photographing Neutrino Collisions**
  * *1.1 The Elusive Neutrino*: What MINERvA measures and why neutrino cross sections matter.
  * *1.2 The Blurry Lens*: Why detector smearing occurs and why "unfolding" is necessary.
* **2. The Solution: Teaching Computers to Deblur Without Bins**
  * *2.1 The Traditional Trap*: Why big lookup tables (migration matrices) fail in multiple dimensions.
  * *2.2 The OmniFold Concept*: How machine learning iteratively reweights simulations to match data.
* **3. Verification: Proving the Algorithm on Known Ground**
  * *3.1 Re-creating the Benchmark*: Reproducing MINERvA's published 2D muon measurement within 1%.
  * *3.2 Testing the Error Bars*: What worked in the uncertainty budget, and why coverage testing is hard.
* **4. New Physics: Unfolding Five Dimensions at Once**
  * *4.1 Beyond the Muon*: Adding available energy, momentum transfer, and hadronic mass.
  * *4.2 Rediscovering Nuclear Effects*: How the data expose the low-recoil discrepancy and 2p2h physics.
  * *4.3 A New Puzzle*: Pinpointing the high-energy, high-mass shortfall in MINERvA’s tuned simulation.
* **5. The Honest Limits: Why We Report "Central Values Only"**
  * *5.1 The Pull of the Prior*: Why machine learning struggles to follow extreme shape changes (regularization bias).
  * *5.2 The 10% Barrier*: Why model dependence and random-seed sensitivity prevented a complete 5D error bar.
* **6. A Clever Workaround: Testing Five Simulations Directly**
  * *6.1 Bypassing Measurement Uncertainties*: Simulating full-chain experiments to test models as hypotheses.
  * *6.2 The Verdict*: Rejecting five standard simulations at the 5% error level.
  * *6.3 Crucial Caveats*: Why missing calorimeter response uncertainties mean the case is not closed.
* **7. Frontiers: Exploratory Machine Learning (PET & Phase Space)**
  * *7.1 Raw Point Clouds (PET)*: What happened when neural networks read raw energy clusters.
  * *7.2 Expanding the Horizon*: The promise and peril of extrapolating outside detector acceptance.
* **8. Takeaway: What This Means for Future Particle Physics**
  * *8.1 Summary of Achievements*: The reality of ML unfolding in real-world experimental physics.

---

## P22. X3 GPT-6.1-sol: outline analysis of the pass-2 paper and primer (sha256 `d06a7b4d014ae94d…`)

The paper’s strongest argument is methodological: **unbinned unfolding reproduces an established result, but higher-dimensional validation exposes limits; full-chain calibration nevertheless permits conditional generator tests.** Its structure obscures that argument by repeatedly revisiting limitations, estimator changes, and validation history.

The primer inherits this structure and adds two research branches absent from the paper. It consequently reads more like an accessible analysis dossier than a guide to the paper’s central argument.

**Conventions for the maps**

I treat paragraphs continued across pages or columns as single paragraphs and restore the obvious reading order in Section II. I include captions and substantive table text separately, but exclude author information, equations standing alone, reference entries, and plot labels.

The quoted phrase identifies the paragraph; the following sentence states its main idea in no more than 25 words. Tags can coexist. Untagged paragraphs provide context or navigation. `[MULTI]` means the paragraph combines distinct argumentative jobs, rather than merely giving several details supporting one idea. No paragraph requires `[NONE]`: even the most overloaded paragraphs have identifiable purposes.

#### 1. Paragraph main-idea maps

##### Paper

| ID | Identifying phrase | Main idea |
|---|---|---|
| Abstract.1 | “We apply OmniFold” | [MULTI][RESULT][CAVEAT] OmniFold reproduces the published measurement and supports higher-dimensional central values and conditional generator rejections, while validation limits stronger measurement claims. |
| I.1 | “Multidifferential neutrino cross sections” | OmniFold offers a practical route to multidimensional neutrino unfolding beyond conventional response matrices. |
| I.2 | “We apply the method” | [METHOD] The analysis extends the published muon measurement to five observables that share reconstructed inputs. |
| I.3 | “We assess how reliable” | [METHOD] Reproduction, projection checks, closure tests, and pseudo-experiments assess the unfolding’s reliability. |
| I.4 | “As an application” | [METHOD] Full-chain calibration tests generator predictions while incorporating the estimator’s pull toward its prior. |
| I.5 | “The two-dimensional reproduction agrees” | [MULTI][RESULT][CAVEAT] Reproduction and conditional generator rejections succeed, but background bias, regularization, uncertainty failures, and redundant discrimination restrict interpretation. |
| I.6 | “Sections II and III” | The paper separates data, estimators, validation, uncertainty status, central values, and calibrated tests. |
| II.1 | “The analysis uses the twelve” | [METHOD] The analysis follows the published selection and normalization using MINERvA open data and tuned GENIE simulation. |
| II.2 | “The unfolded observables are defined” | [METHOD][CAVEAT] Truth and reconstructed observable definitions specify the measurement, including an inherited energy convention and shared reconstructed information. |
| II.3 | “Event selection is held fixed” | [MULTI][METHOD] Higher-dimensional unfolding retains the selection, while external predictions differ in generator, target, flux treatment, and energy coverage. |
| III.1 | “Each OmniFold iteration” | [METHOD] Alternating reconstruction- and truth-level classifiers learn weights that produce unfolded cross sections. |
| III.2 | “Backgrounds enter” | [METHOD] Purity weighting and unbinned subtraction match different within-bin background-subtracted densities. |
| III.3 | “All estimator configurations” | [MULTI][METHOD] Distinct classifier configurations serve central values, cross-checks, and joint tests, with different background treatments and regularization choices. |
| IV.1 | “In closure tests” | Closure and coverage answer different validation questions about point estimates and intervals. |
| IV.A.1 | “The two-dimensional result” | [RESULT][CAVEAT] The reproduced measurement agrees closely in normalization, but correlated shape differences depend on learner choice and an omitted covariance contribution. |
| IV.A.2 | “Both results derive” | [CAVEAT] Shared data prevent interpreting differences using the published covariance without the estimates’ cross-covariance. |
| IV.B.1 | “The covariance of our” | [METHOD][RESULT] Four covariance blocks yield uncertainties close to the publication, dominated by systematic universes. |
| IV.B.2 | “The systematic-universe unfoldings approximate” | [MULTI][CAVEAT] Universe weighting remains approximate, and an unexplained run-period inconsistency motivates an additional covariance block whose coverage is unknown. |
| IV.B.3 | “The statistical block is” | [HIST][CAVEAT] Successive statistical-band constructions and reused validation samples leave the currently quoted statistical covariance without an independent coverage test. |
| IV.B.4 | “In summary, we report” | [CAVEAT] The two-dimensional covariance lacks validated coverage and several uncertainty contributions, requiring new simulation inputs for stronger claims. |
| IV.C.1 | “Each higher-dimensional central value” | [RESULT][CAVEAT] Marginal checks and selected closure tests succeed, but purity subtraction biases high-mass cells; unbinned subtraction substantially reduces that bias. |
| IV.C.2 | “The unfolding recovers only part” | [CAVEAT] Generator-sized truth changes expose persistent regularization bias, numerical sensitivity, and failed statistical-interval coverage. |
| V.1 | “We have built a covariance” | [CAVEAT][HIST] The five-dimensional covariance misses predefined requirements, exhibits seed sensitivity, and omits sensitivity checks for some fixed-seed components. |
| V.2 | “A separate study looked” | [RESULT][CAVEAT] Studied measurement definitions cannot meet the precision target because model dependence alone is too large. |
| VI.1 | “The comparisons in this section” | [RESULT] Descriptive energy comparisons recover the established low-recoil shortfall, partly reduced by adding Valencia 2p2h. |
| VI.2 | “Adding q3 resolves” | [RESULT][CAVEAT] Agreement with a dedicated low-recoil measurement is suggestive but cannot be quantified because truth definitions differ. |
| VI.3 | “The fifth observable, W” | [RESULT][CAVEAT] The joint map locates excess cross section relative to Tune v1, including regions with substantial validation limitations. |
| VI.4 | “The one-dimensional projections” | [RESULT][CAVEAT] External generators generally underpredict the rate, but the high-energy, high-mass concentration is specifically pronounced relative to Tune v1. |
| VII.A.1 | “For each of five predictions” | [METHOD] Hybrid null hypotheses specify generator rates on a fine grid and Tune v1 subcell shapes, with coarser supported test domains. |
| VII.A.2 | “A total statistic” | [METHOD] Quadratic total and shape statistics use a regularized covariance metric whose role is sensitivity rather than calibration. |
| VII.A.3 | “The null distribution” | [METHOD] Full-chain nuisance-varied pseudo-experiments calibrate statistics, including prior pull and conservative shifts for specified approximations. |
| VII.A.4 | “The ten tests are controlled” | [METHOD] Prespecified multiplicity, Monte Carlo precision, and stopping rules govern decisions verified by independent recomputation. |
| VII.A.5 | “Some choices were made” | [HIST][CAVEAT] Data exposure, a computing-budget extension, and later studies qualify which procedural choices were fixed before results. |
| VII.B.1 | “The decisions test the hybrid null” | [CAVEAT] Six conditions restrict the tests, especially unresolved subgrid structure and missing calorimetric-response uncertainty. |
| VII.C.1 | “Table I lists” | [RESULT] All ten tests reject, and prescribed directional shift scans preserve the decisions without establishing grid convergence. |
| VII.C.2 | “Computing time limits” | [HIST][RESULT] Rerunning interrupted pseudo-experiments shows that their missing outcomes do not change any rejection. |
| VII.C.3 | “The comparisons recover” | [MULTI][RESULT][CAVEAT] Calibration reproduces known generator disagreements, offers no demonstrated joint-information advantage, and shows alternative-dependent power without localizing physical causes. |
| VII.D.1 | “MINERvA’s recoil-energy analyses” | [CAVEAT] Missing calorimetric-response uncertainty matters physically because hadronic information contributes to at least one rejection. |
| VII.D.2 | “In an exploratory sensitivity study” | [RESULT][CAVEAT] Rejections survive a limited recoil-scale perturbation, but recalibrated and more realistic response variations remain untested. |
| VIII.1 | “This study applies” | [MULTI][RESULT][CAVEAT] Reproduction and multidimensional central values demonstrate feasibility, while bias and uncertainty failures prevent a precision five-dimensional measurement. |
| VIII.2 | “The joint tests are” | [RESULT][CAVEAT] Full-chain tests reject all hybrid nulls conditionally, without demonstrating additional joint discrimination or resolving response and subgrid limitations. |
| Acknowledgments.1 | “The authors thank” | [MULTI] Acknowledgments combine scientific support, computing resources, unfinished funding information, extensive AI disclosure, verification procedures, and author responsibility. |
| Data availability.1 | “The input data and simulation” | [METHOD][CAVEAT] Archived inputs and a candidate replay package support partial reproducibility, but deposition and reproduction of other results remain incomplete. |

The main structural problems appear in **I.5, III.3, IV.B.2–4, VII.C.3, and VIII.1**. These are not merely long paragraphs: each switches among several levels of the argument.

The paragraph in IV.B.3 is especially consequential. Its organizing principle is **which statistical band existed when**, whereas the reader principally needs to know **which band is reported now and what validates it**.

**Paper captions and table**

| ID | Identifying phrase | Main idea |
|---|---|---|
| Fig.1 | “Comparison with the published result” | [RESULT][CAVEAT] Projections and residuals show reproduction quality, while correlated bands and omitted learner dependence prevent a simple compatibility interpretation. |
| Fig.2 | “Joint … projection” | [RESULT] Ratio and integrated-difference panels distinguish relative excesses from the rate contributions of wide cells. |
| Fig.3 | “Unfolded … central-value projections” | [RESULT][CAVEAT] Energy and mass projections compare central values with generators without measurement uncertainties. |
| Fig.4 | “Calibrated null distributions” | [RESULT] Observed statistics exceed the displayed calibrated null distributions for all five predictions. |
| Table I | “Joint-test decisions” | [RESULT] Monte Carlo counts and multiplicity thresholds document all ten rejections. |

##### Primer

For Section 3, I use descriptive subsection labels because its subsections are unnumbered. Each list item counts as a paragraph.

| ID | Identifying phrase | Main idea |
|---|---|---|
| Abstract.1 | “This is a short” | [MULTI][RESULT][CAVEAT] The guide introduces unfolding, summarizes qualified measurement and test results, and adds an exploratory signal-extension study. |
| 1.1 | “A neutrino is” | The cross section describes neutrino interaction rates as functions of the outgoing muon’s motion. |
| 1.2 | “The difficulty is” | Detector smearing makes unfolding necessary and potentially unstable. |
| 2.1 | “The traditional way” | Conventional migration matrices become increasingly demanding as the number of measured quantities grows. |
| 2.2 | “This analysis uses” | [METHOD] OmniFold repeatedly reweights paired simulated events to connect measured distributions with truth distributions. |
| 2.3 | “The decisive advantage” | [METHOD][CAVEAT] Additional inputs avoid a new migration table but still increase training, simulation, and validation demands. |
| 2.Checks.1 | “In a simulated experiment” | Truth, prior, response, and approximation error describe distinct sources of unfolding behavior. |
| 2.Checks.2 | “One more distinction” | [METHOD] Event selection and learner inputs are separate choices; the main analysis uses MINOS-selected events and summary-input decision trees. |
| 3.Intro.1 | “Our results have different” | The findings are introduced according to their differing validation status. |
| 3.Summary.1 | “A published result, reproduced” | [RESULT][CAVEAT] The published rate is reproduced, but learner dependence, omitted effects, and untested coverage limit the uncertainty claim. |
| 3.Summary.2 | “More quantities at once” | [CAVEAT] Higher-dimensional central values have unaccounted biases and uncertainties that fail requirements or coverage checks. |
| 3.Summary.3 | “Known and new features” | [RESULT] Central values recover the low-recoil shortfall and locate an excess over Tune v1 without assigning significance. |
| 3.Summary.4 | “A joint test” | [RESULT][CAVEAT] Five hybrid simulation hypotheses are rejected conditionally, without demonstrating an advantage from joint five-variable information. |
| 3.Summary.5 | “A neural network” | [CAVEAT] Raw-detector neural-network studies remain method development because no design meets all requirements. |
| 3.Summary.6 | “A wider signal definition” | [RESULT][CAVEAT] Relaxed truth cuts yield a preliminary extension containing both detector-supported and simulation-dominated contributions. |
| 3.Intro.2 | “Each result is only” | Claims must remain within the scope of their validation. |
| 3.Trust.1 | “Before trusting a new method” | [RESULT][CAVEAT] The reproduced rate and uncertainty sizes resemble the publication, although correlated shape and flux-uncertainty differences remain. |
| 3.Trust.2 | “One qualification” | [HIST][CAVEAT] The reported learner implementation changed after comparison results were known. |
| 3.Trust.3 | “The error budget also” | [HIST][CAVEAT] Repairing an earlier error budget leaves several methodological effects outside the quoted covariance. |
| 3.Trust.4 | “To test whether” | [CAVEAT] Independent simulation and validated nuisance variations are needed for stronger coverage claims. |
| 3.Trust.5 | “We did run” | [HIST][CAVEAT] An earlier statistical band undercovered, while its rebuilt successor has not been tested. |
| 3.More.1 | “With the central value reproduced” | [RESULT] Simultaneous unfolding of additional observables preserves the lower-dimensional normalization checks. |
| 3.More.2 | “These are five recorded coordinates” | [CAVEAT] Shared reconstructed inputs mean five coordinates do not establish five independent constraints. |
| 3.More.3 | “The first physics payoff” | [RESULT][CAVEAT] Low-energy generator shortfalls support, but do not identify uniquely, a two-nucleon contribution. |
| 3.Puzzle.1 | “Adding the hadronic-mass axis” | [RESULT][CAVEAT] A joint map localizes the Tune v1 excess, while generator comparisons and validation limits constrain its interpretation. |
| 3.Limits.1 | “The multi-quantity central values” | [CAVEAT] Bias, unvalidated seed-sensitive uncertainties, and numerical instability restrict the multidimensional results to descriptive central values. |
| 3.Limits.2 | “Biases in following” | [MULTI][CAVEAT][HIST] Truth-recovery and background biases persist or require estimator changes, while proposed remedies have unresolved limitations. |
| 3.Limits.3 | “An uncertainty that” | [CAVEAT] Seed sensitivity, incomplete component checks, and failed interval coverage prevent validated five-quantity uncertainty claims. |
| 3.Limits.4 | “Numerical stability” | [HIST][CAVEAT] Rounding sensitivity fails a stability criterion, and a later bootstrap result applies only to another estimator version. |
| 3.Limits.5 | “A narrower point” | [METHOD][CAVEAT] Different detector variations require different propagation methods, without establishing completeness of the hadronic-response uncertainty model. |
| 3.Limits.6 | “None of these” | [CAVEAT] Five-quantity validation failures do not transfer automatically to the separately constructed two-dimensional uncertainty. |
| 3.Joint.1 | “We also asked” | [METHOD] Total and shape tests assess five simulation hypotheses whose within-cell shapes come from Tune v1. |
| 3.Joint.2 | “Rather than rely” | [MULTI][METHOD][RESULT] Full-chain simulated repeats calibrate all ten rejections independently of measurement error bars, and recovered missing repeats preserve the results. |
| 3.Joint.3 | “This is a test” | [CAVEAT] Six conditions, especially missing recoil-response uncertainty and unresolved subgrid structure, restrict the rejections’ physical meaning. |
| 3.Joint.4 | “In a comparison chosen” | [RESULT][CAVEAT] Hadronic information contributes to GENIE CV’s rejection, but additional joint-test power is unestablished and non-rejection does not imply truth. |
| 3.Exploratory.1 | “Two studies test” | Alternative representations and signal definitions explore methodological limits rather than extend the established measurement. |
| 3.Exploratory.2 | “PET is a different learner” | [METHOD][HIST] Recoil-only and full-event PET variants explore unfolding from detector deposits without producing a measurement. |
| 3.Exploratory.3 | “Studies on simulated samples” | [MULTI][HIST][CAVEAT] PET development improves selected recovery tests but yields no validated design, uncertainty, or general performance ranking. |
| 3.Exploratory.4 | “Separately, the published signal” | [RESULT][CAVEAT] Relaxing truth-level muon cuts produces a preliminary rate dominated partly by extrapolation rather than newly supported observations. |
| 4.1 | “Unbinned machine-learning unfolding” | [MULTI][RESULT][CAVEAT] The guide recaps reproduction, multidimensional features, signal extension, and conditional tests while restating their principal limitations. |

**Primer captions and table**

| ID | Identifying phrase | Main idea |
|---|---|---|
| Fig.1 | “Why unfolding is needed” | Detector migration motivates unfolding, which OmniFold performs without a binned response matrix. |
| Table 1 | “Different checks answer” | Closure, coverage, bookkeeping, and stability test different properties and cannot substitute for one another. |
| Fig.2 | “The unfolded muon cross section” | [RESULT] Machine-learning unfolding reproduces the published muon measurement, using a tuned simulation distinct from the later external GENIE comparison. |
| Fig.3 | “The unfolded central values” | [RESULT][CAVEAT] Generator comparisons show energy and mass shortfalls without uncertainties, significance claims, or independence between the two GENIE configurations. |
| Fig.4 | “The unfolded data compared” | [RESULT][CAVEAT] Joint ratio and integrated-difference maps locate the Tune v1 excess, with overflow-cell and seed-sensitivity qualifications. |
| Fig.5 | “Exploratory simulation comparison” | [RESULT][CAVEAT] Paired simulation tests show PET recovery gains on specified deformations without validating uncertainty bands or establishing general superiority. |
| Fig.6 | “The extended-fiducial scalar study” | [RESULT][CAVEAT] Extended-domain maps distinguish stable accepted regions from simulation-dependent low-efficiency extrapolation. |

Two primer paragraphs particularly need splitting: **3.Puzzle.1** combines the finding, comparison-generator interpretation, energy truncation, seed effects, and response validation; **3.Exploratory.3** compresses almost an entire development report.

#### 2. The actual arguments and a conventional PRD structure

##### Paper: actual line of argument

1. Multidimensional neutrino measurements need alternatives to rapidly expanding response matrices.
2. OmniFold can extend an existing MINERvA measurement to five observables.
3. Reliability must be assessed through reproduction, closure, pseudo-experiments, and uncertainty studies.
4. Several estimator configurations are needed for central values, cross-checks, and generator tests.
5. The two-dimensional central value reproduces the published rate, but its correlated shape comparison depends on the learner.
6. A detailed uncertainty reconstruction yields plausible sizes but leaves coverage and omitted contributions unresolved.
7. Higher-dimensional normalization checks succeed, while background bias, regularization bias, and failed coverage expose weaknesses.
8. Five-dimensional measurement definitions cannot meet the chosen precision target.
9. Central values nevertheless recover the low-recoil feature and locate a Tune v1 excess in the joint energy–mass map.
10. Full-chain pseudo-experiments calibrate tests of specified hybrid generator hypotheses despite estimator bias.
11. All ten tests reject under six conditions; limited robustness studies preserve the decisions.
12. Missing recoil-response uncertainty, unresolved subgrid structure, and the lack of demonstrated joint-information advantage constrain the contribution.

This is a coherent argument. Its weakness is that steps 5–8 occupy so much detailed procedural space that the physics results arrive after the reader has already traversed most of the paper’s uncertainty dossier.

##### Primer: actual line of argument

1. Neutrino cross sections are difficult to infer because detectors smear the observations.
2. Conventional unfolding becomes cumbersome as dimensionality increases.
3. OmniFold learns event weights instead of building a multidimensional response table.
4. Several different checks are needed, and selection differs from learner input.
5. A six-item synopsis announces reproduction, higher dimensions, physics features, joint tests, PET, and signal extension.
6. Reproduction succeeds, followed by the history and limitations of its uncertainty budget.
7. Additional observables reproduce known low-recoil behavior.
8. A joint map reveals a localized difference relative to Tune v1.
9. A long limitations discussion revisits biases, seed sensitivity, interval failures, and numerical stability.
10. Separately calibrated tests reject five hybrid simulation hypotheses conditionally.
11. PET development and signal-definition extension introduce two further research branches.
12. The takeaway repeats the principal findings and conditions.

The primer’s order makes readers learn the results repeatedly: first in the abstract, then in the six-item synopsis, then in the detailed subsections, then in the takeaway.

##### A typical PRD outline for this work

1. **Physics motivation and precise contribution:** what the measurement or methodological study adds.
2. **Dataset, detector, signal, phase space, and observables.**
3. **Simulation and comparison predictions:** including target and energy-domain differences.
4. **Final unfolding estimator:** clearly distinguishing the production configurations.
5. **Validation:** reproduction, deformation closure, background treatment, numerical behavior.
6. **Uncertainty model and demonstrated scope:** contributions, exclusions, coverage, and reporting status.
7. **Central-value results:** projections and multidimensional features.
8. **Generator-test construction:** hypotheses, nuisance model, calibration, multiplicity, and essential conditions.
9. **Generator-test results:** decisions, robustness, projection comparison, and physical interpretation.
10. **Conclusions, reproducibility statement, and technical appendices.**

##### Where this paper departs, and whether that helps

| Departure | Effect |
|---|---|
| Validation precedes the central-value physics discussion. | **Helps.** Readers need to know what kind of result they are seeing. |
| Failed precision targets become an explicit scientific outcome. | **Helps.** This supports a valuable feasibility and validation paper. |
| Measurement uncertainty and test calibration are separated. | **Helps substantially.** The distinction is central to the work’s defensible inference. |
| Three estimator roles are introduced in one long paragraph. | **Hurts.** Readers cannot easily track which validation result applies to which estimator. A compact configuration table would help. |
| The Introduction contains an exceptionally dense results-and-limitations inventory. | **Hurts.** It duplicates the abstract, validation, uncertainty section, test conditions, and conclusions. |
| Current uncertainty status is interleaved with earlier defects, repairs, and rescoring. | **Hurts.** The reader must reconstruct the final analysis state from its chronology. |
| Detailed test conditions intervene between calibration and results. | **Mixed.** The conditions are necessary, but should be organized as a concise scope statement plus technical detail. |
| Lost-job recovery and development chronology occupy main-text results space. | **Mostly hurts.** Retain their implications in the paper; move the operational record to the note. |
| Physical interpretation is constrained immediately where each feature appears. | **Helps locally**, but repeated full qualifications undermine the paper globally. |
| No demonstrated gain from five-dimensional joint discrimination is stated explicitly. | **Helps scientific positioning.** It clarifies that the contribution is calibrated methodology rather than proven additional physics sensitivity. |

The paper should present itself consistently as **an unfolding validation study with descriptive multidimensional results and conditional calibrated model tests**. Its present organization sometimes invites the expectations of a completed precision measurement, then repeatedly withdraws them.

#### 3. Proportions

These are editorial estimates by textual space, not measured word counts. Categories are exclusive for estimation: mixed passages are apportioned by function. “Other” includes motivation, definitions, navigation, and acknowledgments. History is separated from the scientific content of the final method.

##### Paper

| Section | Results | Method | Caveats | History | Other |
|---|---:|---:|---:|---:|---:|
| Abstract | 40% | 15% | 45% | 0% | 0% |
| I. Introduction | 20% | 25% | 25% | 0% | 30% |
| II. Data, signal, simulation | 0% | 80% | 15% | 5% | 0% |
| III. Unfolding | 5% | 80% | 10% | 5% | 0% |
| IV. Validation | 20% | 25% | 40% | 15% | 0% |
| V. Uncertainty status | 15% | 10% | 65% | 10% | 0% |
| VI. Central-value results | 60% | 5% | 35% | 0% | 0% |
| VII. Calibrated tests | 20% | 40% | 30% | 10% | 0% |
| VIII. Conclusions | 40% | 5% | 55% | 0% | 0% |
| Acknowledgments | 0% | 10% | 0% | 5% | 85% |
| Data availability | 5% | 50% | 35% | 10% | 0% |
| **Overall, abstract and I–VIII** | **≈23%** | **≈34%** | **≈35%** | **≈8%** | **≈0–5%*** |

*Rounded estimates; the overall “other” share is small because the methodological sections dominate.*

The caveat burden is understandable for this particular study. The problem is **distribution and duplication**, not an obligation to make the results sound more positive.

For a conventional measurement paper, results receive too little space relative to qualification and development history. For a methodological validation paper, the method/result balance is more plausible—but approximately eight percent devoted to history is still excessive when a companion note exists.

##### Primer

| Section or subsection | Results | Method | Caveats | History | Other |
|---|---:|---:|---:|---:|---:|
| Abstract | 35% | 10% | 25% | 0% | 30% |
| 1. What was measured | 0% | 10% | 5% | 0% | 85% |
| 2. Method and checks | 0% | 70% | 15% | 0% | 15% |
| 3. Opening synopsis | 35% | 5% | 55% | 5% | 0% |
| 3. Trust check | 25% | 10% | 40% | 25% | 0% |
| 3. More quantities | 50% | 15% | 30% | 0% | 5% |
| 3. New puzzle | 55% | 0% | 45% | 0% | 0% |
| 3. Limits | 5% | 15% | 65% | 15% | 0% |
| 3. Joint test | 25% | 35% | 35% | 5% | 0% |
| 3. Exploratory studies | 20% | 20% | 40% | 20% | 0% |
| 4. Takeaway | 40% | 10% | 50% | 0% | 0% |
| **Overall** | **≈25%** | **≈24%** | **≈35%** | **≈9%** | **≈7%** |

For a physics-literate non-specialist, this balance is inappropriate. Roughly as much space explains why claims are restricted as explains the method and its physical purpose, while development history adds another substantial burden.

A primer can explain uncertainty honestly without teaching readers the sequence of covariance rebuilds, estimator variants, nested ensemble comparisons, and failed development gates.

#### 4. Repeated limitations and their best locations

Locations below use the paragraph IDs above. “Abstract” and “conclusion” repetition is sometimes justified; the recommendation is to retain a short scope statement there and put the full explanation in one authoritative location.

##### Limitations repeated in the paper

| Repeated limitation | Locations | Best authoritative location |
|---|---|---|
| Higher-dimensional results are central values, without validated measurement uncertainties or descriptive-comparison significance. | Abstract.1; I.2, I.5; IV.B.4; IV.C.2; V.1–2; VI.1; Fig.3; VIII.1–2 | End of V, as a clear reporting-status statement; short reminders in captions. |
| Two-dimensional coverage remains unvalidated. | IV.B.3–4; VIII.1 | IV.B, directly after defining the current covariance. |
| Learner dependence is omitted from the covariance. | IV.A.1; IV.B.4; Fig.1; VIII.1 | IV.A.1, with a concise inclusion/exclusion reference in IV.B. |
| The central learner was chosen after both comparisons were known. | IV.A.1; VII.A.5 | IV.A.1. |
| Shared data prevent a calibrated significance from the published covariance alone. | IV.A.1, “indicative only”; IV.A.2; Fig.1 | IV.A.2. |
| Systematic-universe treatment of missed events is approximate and uncorrected. | IV.B.2; IV.B.4 | IV.B.2. |
| The run-period block does not establish the correct period or its own coverage. | Repeated within IV.B.2, including “does not identify,” “contains them by construction,” and “not a test.” | One compact explanation in IV.B.2. |
| Background subtraction biases high-\(W\) cells; quoted uncertainties omit it. | Abstract.1, generally; I.5; III.3; IV.C.1; VIII.1 | IV.C.1, separated by estimator configuration. |
| Generator-sized truth changes leave regularization bias absent from quoted uncertainties. | Abstract.1, generally; I.5; IV.B.4; IV.C.2; VI.3; VIII.1 | IV.C.2. |
| Five-dimensional statistical intervals fail coverage tests. | I.5; IV.C.2; VIII.1, more generally | IV.C.2. |
| Rounding-level changes limit exact reproducibility. | IV.C.2; VII.A.3, as a calibrated nuisance | IV.C.2; VII.A.3 need only state its inclusion. |
| Covariance seed dependence prevents the claimed covariance-based comparison precision. | I.5, generally; V.1; VI.1 by reference; VIII.1 | V.1. |
| Model dependence exceeds the 10% precision target. | Abstract.1; I.5; IV.C.2 by reference; V.2; VIII.1 | V.2, including the numerical evidence. |
| Rejections concern hybrid nulls rather than unrestricted generator truths. | Abstract.1; I.5; VII.A.1; VII.B.1; VII.C.3; VIII.2 | VII.A.1 for definition; VII.B.1 for transfer to the generator itself. |
| Fine-grid convergence is unshown and residual subgrid effects are unbounded. | Abstract.1; I.5; VII.A.3; VII.B.1; VII.C.1; VIII.2 | VII.B.1. |
| Shift scans probe one direction and do not establish a residual bound. | VII.B.1; VII.C.1 | VII.C.1, adjacent to the scan result. |
| Calorimetric recoil-response uncertainty is absent. | Abstract.1; I.5; VII.B.1; VII.D.1–2; VIII.2 | VII.D, with one-line identification in VII.B. |
| Limited response-scale checks do not validate the response model. | VII.D.1–2, including the closing conditionality statement | VII.D.2. |
| No additional discrimination from joint five-observable information is demonstrated. | Abstract.1; I.5; VII.C.3; VIII.2 | VII.C.3. |
| GiBUU’s high-energy truncation limits comparison and migration modeling. | II.3; VI.4; VII.A.1; VII.B.1 | II.3 for sample scope, then brief application-specific references. |
| Predictions have finite-sample fluctuations. | VII.A.1–3; VII.B.1 | VII.A, in one account of how prediction sampling enters the hypothesis and calibration. |
| Pseudo-experiments use half the simulation while data use all of it. | VII.A.3; VII.B.1 | VII.A.3, with the measured correction and residual scope together. |
| Different true-\(E_{\rm avail}\) definitions prevent quantitative low-recoil comparison. | II.2 supplies the definition; VI.2 explains the limitation | VI.2; this is mostly useful definition-to-application linkage rather than excessive repetition. |
| The joint high-energy, high-\(W\) map lacks detector-mismatch closure. | VI.3; VIII.2 invokes the broader response limitation | VI.3, with a reference to VII.D rather than another response discussion. |

Two qualifications matter here.

First, **the untested two-dimensional intervals and failed five-dimensional variant intervals are different limitations**. They should not be collapsed into one generic “coverage was not validated” disclaimer.

Second, **seed variability, rounding sensitivity, learner dependence, and regularization bias are different phenomena**. A short estimator-status table would prevent them from being repeatedly bundled together.

##### Additional repetition within the primer

| Repeated limitation | Locations | Best authoritative location |
|---|---|---|
| Two-dimensional statistical bars lack a coverage test. | Abstract.1; 3.Summary.1; 3.Trust.4–5 | A single current-status paragraph at the end of 3.Trust. |
| Learner dependence and a result-informed implementation choice. | 3.Summary.1; 3.Trust.2–3; 3.Limits.6 by reference | 3.Trust.2; omit the procedural chronology from the primer. |
| Omitted two-dimensional uncertainty contributions. | 3.Summary.1; 3.Trust.3 | 3.Trust.3, compressed to their implication. |
| Higher-dimensional central values have no assigned significance. | Abstract.1; 3.Summary.2–3; 3.Puzzle.1; 3.Limits.1, 3; Fig.3–4; 4.1 | Opening of the multidimensional-results section, with short caption labels. |
| Truth-recovery bias is absent from quoted uncertainties. | 3.Summary.2; 3.Limits.1–2; 4.1 | 3.Limits.2. |
| Background removal leaves bias unless the estimator is changed. | 3.Summary.2; 3.Limits.2 | 3.Limits.2, distinguishing the reported estimator from the improved test estimator. |
| The five-dimensional uncertainty fails predefined requirements and is used by exception. | 3.Summary.2; 3.Limits.1, 3 | 3.Limits.3; procedural exception details belong in the note. |
| Seed sensitivity affects the covariance. | 3.Summary.2; 3.Limits.1, 3 | 3.Limits.3. |
| Seed changes also move the central values. | 3.Puzzle.1; Fig.4; 3.Limits.3 | 3.Limits.3; keep a caption reminder only if visually material. |
| A variant’s five-dimensional statistical intervals fail coverage. | 3.Summary.2; 3.Limits.3 | 3.Limits.3. |
| Rounding sensitivity fails a stability criterion. | 3.Limits.1, 4 | 3.Limits.4. |
| Later validation results cannot be transferred between estimator variants. | Table 1; 3.Limits.4, 6 | Explain once beside a simple estimator distinction; preserve the table’s general warning. |
| Five coordinates do not establish five independent constraints. | 3.More.2; 3.Summary.4 and 3.Joint.4 address its test-performance consequence | 3.More.2; distinguish coordinate dependence from demonstrated discrimination. |
| The low-recoil feature does not uniquely identify a mechanism. | 3.Summary.3; 3.More.3 | 3.More.3. |
| Missing calorimetric-response uncertainty conditions the rejections. | 3.Summary.4; 3.Joint.3; 4.1; anticipated indirectly in 3.Limits.5 | 3.Joint.3. |
| Fine-grid convergence is unshown and finer-structure error is unbounded. | 3.Summary.4; 3.Joint.3; 4.1 | 3.Joint.3. |
| Joint five-variable discrimination has no demonstrated advantage. | 3.Summary.4; 3.Joint.4; 4.1 | 3.Joint.4. |
| The tests are separate from measurement uncertainties. | 3.Summary.4; 3.Joint.2–3; 4.1 | 3.Joint.2, where calibration is explained. |
| PET remains development and supplies no validated measurement or uncertainty. | 3.Summary.5; 3.Exploratory.1–3 | Opening of a separate optional PET section. |
| No PET design meets all requirements. | 3.Summary.5; 3.Exploratory.3 | 3.Exploratory.3, in one sentence. |
| The PET comparison is conditional on finite samples and does not establish general superiority or precision. | 3.Exploratory.3; Fig.5 | Fig.5 plus one interpretation sentence in the text. |
| Relaxed truth cuts add no selected observations. | 3.Summary.6; 3.Exploratory.4 | 3.Exploratory.4. |
| The signal extension is preliminary and partly simulation-dominated. | Abstract.1; 3.Summary.6; 3.Exploratory.4; Fig.6; 4.1 | 3.Exploratory.4, with a short caption label. |
| The joint-map excess lacks response-mismatch validation and occurs where prior bias is largest. | 3.Puzzle.1; broader bias discussion in 3.Limits.2 | Directly beside the map, in a compact qualification. |

Several other limitations appear only once and do not need consolidation: the unexplained flux-uncertainty difference, the limited tested pion variations, the dedicated measurement’s different truth definition, and the rule that non-rejection does not establish truth.

The best repetition policy is **claim-sized repetition**: the abstract states the restricted claim; the body establishes the restriction; the conclusion states its consequence. None needs to reproduce the whole qualification inventory.

#### 5. The paper abstract

##### Sentence-by-sentence classification

| Sentence | Text | Classification |
|---|---|---|
| 1 | “We apply OmniFold to MINERvA open data for medium-energy νµ charged-current inclusive interactions.” | **Headline contribution.** Under the requested binary classification, this belongs with headline results, although literally it states scope. |
| 2 | “The analysis reproduces the published double-differential cross section in muon kinematics, with the integrated cross section within about one percent, and extends it to five simultaneous observables by adding available energy, three-momentum transfer, and hadronic invariant mass.” | **Headline result.** |
| 3 | “The three- to five-observable results are central values only.” | **Qualification.** |
| 4 | “Pseudo-experiments reveal background-subtraction and regularization biases, and the measured model dependence, about 10–13% per cell, prevents a five-dimensional measurement whose total uncertainties meet our predefined 10% precision target.” | **Qualification with a substantive negative result.** The precision failure is scientifically important enough to function as a headline. |
| 5 | “Tests calibrated with pseudo-experiments that rerun the full analysis chain reject the hybrid null hypotheses built from five generator predictions, in total and in shape, at the 5% familywise level.” | **Headline result.** |
| 6 | “Their interpretation is limited: the nuisance model has no calorimetric recoil-response uncertainty, convergence of the fine grid defining the null hypotheses has not been shown, and the joint five-observable information is not shown to discriminate beyond matched coarse projections.” | **Qualification.** |

The abstract alternates between contribution and restriction reasonably well. Its structural problem is the **accumulation of qualification detail**, especially three different issues in its closing sentence.

##### What a 120–160-word abstract should keep

Keep:

- The data and method.
- The one-percent reproduction result.
- The extension to five observables, explicitly as central values.
- The measured model-dependence scale and failed precision target.
- Full-chain calibration and the familywise rejection result.
- The two principal physical conditions.
- A short statement that additional joint discrimination was not demonstrated.

Compress the observable list and the catalogue of bias mechanisms. Their details belong in the body.

A possible **153-word abstract** is:

> We apply OmniFold to MINERvA medium-energy muon-neutrino charged-current inclusive open data. The unfolded muon-kinematic cross section reproduces the published integrated result within about one percent. Adding available energy, momentum transfer, and hadronic invariant mass yields simultaneous five-observable central values. Validation exposes background-subtraction and regularization biases; model dependence of approximately 10–13% per cell prevents the studied five-dimensional measurement definitions from meeting a predefined 10% total-uncertainty target. Separately, pseudo-experiments that repeat the full analysis chain calibrate total and shape tests of hybrid hypotheses constructed from five generator predictions. All ten tests reject at the 5% familywise level under the stated nuisance model. These rejections remain conditional on the simulated calorimetric recoil response and unresolved structure below the hypotheses’ fine grid. Matched coarse projections already discriminate against every prediction in at least one test projection, so additional discrimination from the joint five-observable information is not demonstrated.

##### Why honest abstracts grow

They grow because authors try to prevent **every foreseeable overinterpretation at the point of first mention**. Each result then acquires its own explanation of estimator identity, failed validation, omitted uncertainty, procedural timing, and physical scope. Additional sentences attempt to distinguish the qualifications from one another.

The way to stop this is to define the **claim hierarchy before drafting**:

1. What was demonstrated?
2. What reporting status follows?
3. Which conditions materially change the headline interpretation?

An abstract needs those answers. It does not need the audit trail establishing each answer. Honesty requires accurate scope; it does not require a miniature analysis note.

#### 6. Does the primer’s order serve a non-specialist?

Partly. Sections 1 and 2 establish the problem and basic solution effectively. The order then becomes progressively less helpful.

The main obstacles are structural:

- **The six-item synopsis is too complete.** It makes readers encounter nearly every result and limitation before they have the concepts needed to retain them.
- **The reproduction discussion turns into a covariance repair history.** That interrupts the transition from understanding the method to seeing what it reveals.
- **The longest physics paragraph carries its entire defense.** The Tune v1 map is introduced together with generator normalization, GiBUU truncation, seed effects, detector response, and regularization.
- **“Limits” is a technical report inside the primer.** Its nested ensemble and fixed-component details are disproportionate to the intended reader.
- **PET and the signal extension broaden the subject late.** They are absent from the paper’s main argument and require fresh conceptual machinery.
- **The separate inference route arrives too late.** Readers spend many paragraphs hearing that error bars are unvalidated before learning why a calibrated hypothesis test can still be meaningful.
- **Figure 2 is an argument about reproduction presented through a dense specialist display.** Figure 1 similarly introduces much more dimensional detail than the opening deblurring explanation needs.
- **Figure 5 asks the reader to interpret development configurations and study-specific labels.** That belongs in optional technical material.

The guide also needs to state early whether it explains **this paper** or **the broader analysis program**. Its present title and abstract imply the former, while PET and the signal extension make it the latter.

##### Proposed order: section and paragraph headings

**1. The question: what can neutrino data tell us?**

- Rare interactions and the meaning of a cross section.
- What MINERvA records: a muon and the hadronic recoil.
- Why several observables can reveal different aspects of the same interaction.

**2. Why the recorded distribution needs unfolding**

- Detector smearing, inefficiency, and the deblurring analogy.
- Why a larger migration table becomes difficult.
- How OmniFold reweights paired simulated events.
- What “unbinned” makes practical—and what it does not guarantee.

**3. What was actually analyzed**

- The fixed event selection and MINOS muon requirement.
- The five observables, explained before their symbols dominate.
- Why five coordinates need not supply five independent constraints.
- The two analysis products: descriptive central values and separately calibrated model tests.

**4. The first check: recover an established measurement**

- Agreement with the published total rate and most cells.
- The remaining correlated shape difference.
- What has and has not been established about the uncertainty.
- A compact explanation of closure versus coverage, using Table 1 as optional support.

**5. What the additional observables show**

- The known low-recoil shortfall.
- What adding a two-nucleon contribution changes.
- The joint energy–mass excess relative to Tune v1.
- Why that corner is less exceptional for the other generators.
- One adjacent scope paragraph: central values, no assigned significance, and the most relevant bias and response limitations.

**6. Why trustworthy multidimensional error bars remain difficult**

- Recovering a changed truth only partly: regularization bias.
- Background removal and the distinction between the reported and improved estimators.
- Seed sensitivity and failed coverage checks.
- What additional validation would be needed.

This section should be much shorter than the current “Limits” subsection. Covariance rebuilds, exception procedures, nested ensemble details, and rounding chronology should move to the analysis note.

**7. A different question: can specified simulations explain the observations?**

- What hypothesis is tested, including the hybrid-grid definition.
- Why repeating the entire analysis calibrates the test despite estimator bias.
- What the ten rejections mean.
- The two principal physical conditions: recoil response and subgrid structure.
- What the tests do not establish: mechanism attribution or extra joint-variable discrimination.

**8. What this study establishes**

- Reproduction demonstrates practical feasibility.
- Multidimensional central values expose useful patterns.
- Validated measurement intervals remain unfinished.
- Conditional full-chain tests provide a separate inference.

**Optional extension A. Learning directly from detector deposits**

- What PET changes.
- What its simulation studies demonstrate.
- Why it remains development rather than a measurement.

**Optional extension B. Extending beyond the published signal region**

- Changing the population without adding observations.
- Detector-supported extension versus simulation-dependent extrapolation.
- Why the preliminary extended rate needs those components reported separately.

This order gives the reader a continuous progression: **question → detector problem → method → successful check → physics patterns → uncertainty limits → separate calibrated inference**. The exploratory branches remain available without interrupting that progression.

---

## P23. Claude: independent preservation review, paper (27edd449) (sha256 `0b8399c9df1f8281…`)

### Pass-2 preservation review, paper (`paper_body.tex`, `main_paper.tex` abstract and Data availability)

Independent read-only reviewer (Claude Opus 5.5; authored none of the pass). Base `34650231`, new `27edd449`
(the note-side prerequisite `b3fc422b` is in between; the note files are identical at `b3fc422b` and `27edd449`).
Compared `git show 34650231:<path>` against `27edd449:<path>`, in both directions. Rules: PLAIN-LANGUAGE-PASS2.md,
DECISION-20261018-joseph-plain-language-pass2.md, and pass 1's PLAIN-LANGUAGE.md where pass 2 is silent. The writer's
report `p2-paper.md` was used only as a lead. Every record and note location below was opened at `27edd449`. The worktree
`wt-plain2` was not modified (`git status` clean, HEAD `27edd449`).

Line numbers are at `27edd449`: `P:` = `paper_body.tex`, `M:` = `main_paper.tex`.

#### 1. Findings

| id | severity | base text | new text (line) | problem | minimal fix |
|---|---|---|---|---|---|
| R-M1 | **MATERIAL** | abstract: "Generator tests, calibrated with pseudo-experiments that rerun the full analysis chain **under a stated nuisance model**, reject all five tested predictions … **These rejections hold only under stated conditions.** … Their physical interpretation is limited because the nuisance model has no calorimetric recoil-response uncertainty and …" (base M:65-78) | "Tests calibrated with pseudo-experiments that rerun the full analysis chain reject the hybrid null hypotheses built from five generator predictions, in total and in shape, at the 5% familywise level. Their interpretation is limited: the nuisance model has no calorimetric recoil-response uncertainty, …" (M:72-80) | Both conditionality markers on the rejection itself are gone. The base made the calibration, and so the rejection, conditional on the nuisance model, and then limited its *interpretation* separately. Now the rejection reads as unconditional, and the missing recoil-response band appears only as a limit on "interpretation". That is a strengthening of the headline claim relative to base (task item 2: "rejections of hybrid nulls under the stated nuisance model lacking calorimetric response uncertainty"). It also leaves "the nuisance model" in the next sentence with no antecedent. The body is correct: the Intro (P:88-90), VII B (P:853-854) and the Conclusions (P:1090-1091) all keep "under six stated conditions". | Restore the qualifier in the calibration clause: "Tests calibrated with pseudo-experiments that rerun the full analysis chain **under a stated nuisance model** reject the hybrid null hypotheses …" (+5 words, abstract about 161). This also gives "the nuisance model" its antecedent. |
| R-m1 | MINOR | (base had no number: "prevents a five-dimensional measurement with total uncertainties that meet our predefined criteria at useful precision") | "the measured model dependence, about 10--13% per cell, prevents …" (M:68-69; Intro P:84; Conclusions P:1083); Sec. V: "Over the definitions considered, this model dependence is about 10--13% per cell" (P:633-634) | "About 10–13% per cell" reads as a per-cell value. It is the range of the **medians** over the three definitions (12.0, 9.6, 13.4%; note `sec_5d.tex:211`). The 90th percentiles are 22.5–39.2% (`sec_5d.tex:212`), so the phrase understates the limitation in the tail cells. The record's phrase (RECORD-20260927 :144, note `sec_5d.tex:228-229`) is "per coarse joint cell", which is no more precise. The RD2 caution is respected: no sentence says the model component alone exceeds 10% in every definition. | Insert "a median of" in all four places: "the measured model dependence, a median of about 10--13% per cell, …" (+3 words in the abstract). Sec. V: "Over the definitions considered, its median is about 10--13% per cell, …". |
| R-m2 | MINOR | Conclusions: "**The three- to five-dimensional central values** support only descriptive comparisons, without validated coverage of their total intervals and without a covariance-based generator significance." (base P:967-969) | "… and the three- and four-observable central values pass closure tests with injected shape changes. **They** support only descriptive comparisons, …" (P:1072-1077) | The nearest antecedent of "They" is "the three- and four-observable central values". Read that way, the restriction no longer covers the five-dimensional central values, which have no closure pass and are the ones the restriction matters most for. The scope is narrower than the base. | "**All the higher-dimensional central values** support only descriptive comparisons, …" |
| R-m3 | MINOR | Sec. VII (now V): "We use the covariance **only under an exception to the criteria**, recorded in the analysis note and limited to this one covariance." (base P:919-921) | "We nevertheless use this covariance, as recorded in the analysis note, and **that allowance** covers no other covariance." (P:592-593) | "Only" and "exception" are gone. "That allowance" has no antecedent, because no allowance has been named, so the restriction ("covers no other covariance") qualifies nothing the reader has seen. The meaning survives through "nevertheless", but it is weaker and less clear than the base. "Allowance … covers" is also internal register. | "We use it nevertheless, under an exception to these criteria that the analysis note records and that applies to this covariance only." |
| R-m4 | MINOR | VII B (i): "at a rate taken from the review of the test design, for which no calculation is recorded" (base P:726-728) | "by \jtMoneWnormMin--\jtMoneWnormMax{} per halving in a proxy of the test metric, **a value adopted when the test was designed** whose calculation is not recorded" (P:866-868) | The number matches its source (`values_inference.tex:38-39`; note `sec_joint.tex:131`; amendment 7 `claims.rejection`), it is kept apart from the L2 ratio, and the provenance disclosure survives. Two problems: "adopted" as a project act is R2 vocabulary, and the base's information that the value came from the **review** of the design (REVIEW-20260927 item 4) is lost. | Use the note's own wording: "…, a design-review value whose calculation is not recorded, …" (the theme-A source's proposal). |
| R-n1 | NOTE | abstract: "The analysis reproduces the published double-differential cross section in muon kinematics, and extends it …" | "… in muon kinematics, with the integrated cross section within about one percent, and extends it …" (M:62-64) | Theme A F5. The value is correct: `\ratioTot` = 1.011 (values.tex:48; receipt `ratio_integrals_reported` 1.0112). "Integrated" scopes it. The theme-A source itself warned that this number, standing alone, may suggest bin-level agreement while the body reports a correlated shape difference (χ²/ndf `\chiPaper`, learner-dependent). The phrase is allowed and is not an overclaim, but it is the one abstract phrase that adds a positive figure of merit with no counterweight. | Keep it (the budget allows it), or drop the phrase if the director wants the abstract to stay strictly neutral on the 2D agreement. |
| R-n2 | NOTE | — | abstract "the hybrid null hypotheses" (M:73) | F15 wording, approved. In the abstract the term is undefined: a reader learns what "hybrid" means only at VII A (P:752-753). | Optional: none within budget. If words are freed (R-M1 adds five), "hybrid" could be left as is. |
| R-n3 | NOTE | IV B: "A review of the stored analysis products found errors in an earlier version of the uncertainty budget, **among them** a mismatch … and statistical fluctuations of the background templates that were not propagated; the quoted covariance is free of both." (base P:423-427) | method statements at P:337-338 ("Each universe is unfolded with the same simulated truth input as its reference.") and P:413-420 ("…so that the statistical fluctuations of the background templates are propagated … An earlier version of the budget did not propagate these fluctuations, and its universe unfoldings used a truth input different from that of their reference") | The content is preserved: the two defects, their absence from the quoted covariance, and the cite. "Among them" is lost, so the text now reads as if these were the earlier budget's only defects. The note has more (`sec_systematics.tex:206-207` "further defects"; the Rvn1pi double count at :222-226, fixed in the quoted block). No conclusion depends on it. | Optional: "An earlier version of the budget had several construction errors; among them, it did not propagate these fluctuations, and …" |
| R-n4 | NOTE | VII C: "Had every interrupted one exceeded the observed statistic, no test would have been rejected. We therefore reran …" (base P:831-833) | "Computing time limits interrupted or prevented … All of them were rerun with a procedure fixed in advance, and none reaches …" (P:974-978) | This is a legitimate theme-B move (P7). The note carries it verbatim in substance (`sec_joint.tex:270-273`), and the P15 paragraph (P:843-846) keeps "after the decisions … not part of the decision rule". What a VII C reader no longer learns is that the robustness of every decision to the lost draws rests on this report-only rerun. | Optional, one clause: "All of them, which could otherwise have changed every decision, were rerun …". |
| R-n5 | NOTE | "We therefore reran the lost pseudo-experiments …" (base) | "All of them were rerun" (P:975) beside "each power estimate uses 172 to 199 of its 200 alternative pseudo-experiments, the rest having been lost to time limits" (P:1008-1009) | "All of them" now covers the \jtLostPow{} power draws explicitly. The quoted power figures still use the frozen sets (source comment P:1010-1011). The two sentences read as contradictory. The base had the same tension, but less sharply. | "(each quoted power estimate uses the 172 to 199 of its 200 alternative pseudo-experiments completed at the frozen stop)". |
| R-n6 | NOTE | "One of these criteria requires a bound fixed before the covariance was produced and can no longer be applied to it." | "one of them requires a bound fixed before the covariance was produced, and it can no longer be applied." (P:590-592) | "It" can now be read as the bound or as the criterion, and "to it" (the covariance) is gone. The meaning survives. | "… and that criterion can no longer be applied to it." |
| R-n7 | NOTE | "until both of a null's decisions were determined, that is, until each interval lay entirely on one side of its threshold" (base P:691-694) | "until both of a null's decisions were determined: a null stopped when a 99.5% Clopper--Pearson interval of $k/B$ lay entirely on one side of each of its thresholds and met a fixed precision requirement" (P:810-814) | Director ruling F-p2-1 is **verified correct** against `nd-unfolding/s5p_inference.py:89-114` (`sequential_decision`, `look_level=0.995`: stop iff no threshold is straddled **and** the T7 precision tier is met) and :127-155 (`holm_determined`, the 95% decision interval). Amendment 7 `sequential_rule` confirms "stops the null when … sequential_decision stops both". One looseness: the threshold set is every Holm level α/j that the test could face (`holm_thresholds`), not thresholds belonging to the null. The base's own omissions (MnvTune/GENIE CV may not stop before B = 1200; budget stops) are unchanged. | Optional: "… on one side of every Holm threshold it could face …". |
| R-n8 | NOTE | — | Sec. V: "…, comparable to the generator differences that such a measurement would need to resolve." (P:634-635) | This is new interpretive content in the paper, not a number. It comes from the record (RECORD-20260927 :144) and the note (`sec_5d.tex:228-230`), and it unpacks the base's hedge "at useful precision", which the pass removed from the abstract and Intro. I treat it as within theme A, the content the hedge stood for, and it strengthens nothing. | none |
| R-x1 | NOTE (excess) | — | IV C closing: "In this implementation, then, agreement in the marginal normalizations coexists with substantial regularization bias, and the model dependence and the calibration of the uncertainties remain limiting (Sec. V)." (P:566-569), immediately followed by Sec. V's own statement | This summary now leads straight into the section that states the same limits with numbers. It is a candidate for cutting to "…remain limiting; Sec. V gives their status". | optional |
| R-x2 | NOTE (excess) | — | Intro P:71-87, two sentences of about 90 words carrying the biases, the 5D coverage failure, the seed, coverage, model dependence and the target | This is still the densest passage of the paper (an R4 chain). Every clause is earned, so this is about register only. | optional split after "tested truths." (already a full stop) and after "limit the method," |
| R-x3 | NOTE (excess) | — | P15 (P:833-848) restates "outside the decision rule" (also at P:913) and "a post hoc observation" (also VII D) | A deliberate collect-and-keep-at-claim design (the theme-B P15 item). It is acceptable duplication. | none |

**Abstract budget.** 156 words by `wc` of the source with comments stripped and math collapsed (base 237). With R-M1 it is
about 161, and with R-m1 about 164, which is still "about 150". Each sentence is needed:
1. what was done;
2. the 2D headline, plus the extension;
3. "central values only" (needed so that 3–5D are not read as measurements);
4. the negative 5D headline and its cause;
5. the rejections (needs R-M1);
6. the three limits a reader needs in order not to over-read the rejections.

Dropped from the abstract, and correctly left to the body:
- the generator names;
- the normalization and closure checks;
- the seed and coverage limits;
- "recover known discrepancies".

None of these is needed to read a headline result correctly, because "central values only" covers the 3–5D intervals.

#### 2. Moves to the note, verified at `27edd449`

| moved paper content | note location opened | same content? |
|---|---|---|
| P2: missed-event bookkeeping and iteration stability, "neither establishes recovery or coverage" | `sec_validation.tex:24` ("no recovery or coverage claim"), `:26` ("not a known-truth accuracy test") | yes. The paper no longer mentions either check, so it needs no pointer |
| P3: cause of the old-band undercoverage (completeness division) and its removal | `sec_validation.tex:266-276` (incl. "The attribution is partial") | yes, and fuller than the base paper |
| P3: "rebuilt band is wider than the toy scatter, for reasons not established" | `sec_validation.tex:284-290` ("wider than the toy scatter … its cause is not established") | yes. The 97.7/78.1 values stay in the paper with the pointer "the analysis note gives the full test" (P:447-448) |
| P4/P16: earlier-budget truth-input mismatch; background-template statistics not propagated | `sec_systematics.tex:206-215` (incl. ":213 The July sweep, which the quoted universe block uses, does not have this mismatch"), `:243` | yes (see R-n3 on "among them") |
| P5: seed movements at 40/80/160 throws and the noise floor values | `sec_5d.tex:508-520` (`\seedEffectNforty`, `\seedEffectNeighty`, `\sprojMeasured`, `\floorNforty`, `\floorNeighty`; nested subsets at :518) | yes. The paper keeps the qualitative result and the one-seed-pair limit (P:604-608) |
| "The joint tests above came from the same study" | `sec_5d.tex:230-231` ("the separately admitted inference branch") | chronology only; the paper keeps "a different route to inference … no new measurement uncertainty" (P:635-638) |
| P6: package assembled before the LightGBM switch; plotting code extended | `app_release.tex:23-27` | yes. The paper keeps "carries the exact-split curve", "regenerated separately", "not yet deposited" and the `\pubhold` |
| P8: `\jtRecompRows` compared rows | `sec_joint.tex:112-115` | yes. The paper keeps "every $p$ value and decision" and VII B keeps "verifies the calculation, not whether the chain does so" (P:891-893) |
| P9: κ-scan endpoint 5.2 and "bounds neither" in condition (i) | the paper's VII C (P:913-919: 5.25/5.17, "bounds neither the actual residual nor the convergence"); `sec_joint.tex:239-249` | yes. Condition (i) keeps a pointer (P:880) |
| P7: worst-case sensitivity of the lost draws | `sec_joint.tex:270-273` | yes (see R-n4) |
| P7: "independently reviewed beforehand"; 16-of-16 determinism check | `sec_joint.tex:278-280` | yes |
| "This motivates the full-chain calibrated comparisons" (IV C) | merged into Sec. V (P:635-638) | yes |
| "which was the original two-dimensional choice" (III) | stated at the claim, IV A (P:267-268, "This choice, which replaced the exact-split result, was made after both comparisons were known") | yes |
| "as first measured" (IV C) | history only; `sec_5d.tex` `sec:val-negweight` | no limitation is lost |
| the coarse-projection comparison's timing (VII C) | P15 (P:846-847); `sec_joint.tex:316-317` | yes |
| fine-grid identification (new theme-A content, note home first) | `sec_joint.tex:31-33`; `sec_method.tex:270-275`; `s5p_stage1_inspect.py:38-44` (FINE: 14 p_T, 16 p∥, 7, 7, 6 bins) | yes, verified |
| 5D coverage numbers (new theme-A content, note home first) | `sec_5d.tex:361-365` | yes. They match OUTCOME-20260925-s5c-tier-s-futility-fail.md :32-33 (nominal 0/2 futile, min 0.850 at 95%; tilt 51/42, min 0.060 at 68%; UCB < 0.66 / < 0.94) and :41-43 |

**Added numbers checked against their records:**
- 13.4% (RD3, the 39 EW cells), the five departures, and the 10% median 68% half-width: `sec_5d.tex:208-216` and the record.
- About 10–13%: the record's :144 phrase; see R-m1.
- The 74% attribution to the same deterministic variant: OUTCOME s5n :24-25 (family N = s5c F2 with negweight-refined), :57, :75-82 (signal-only reproduces it).
- 400 per truth: s5c :3-6. All the other coverage values are as above.
- The two cautions in themeA-sources are respected:
  - The RD2 9.6% caution: no "exceeds 10% in every definition", and Sec. V attributes 13.4% to the fallback only.
  - The F17 caution: no "built without the completeness division". IV B says only "The band was then rebuilt", and the theme-A F17 sentence was not added.

#### 3. Paragraphs checked and preserved

Each was compared clause by clause with the base:
- **Intro, results paragraph** (P:62-97):
  - "the quoted uncertainties do not include it" is now at its claim, IV C P:523-524;
  - the 5D coverage failure is named (F1);
  - the 2D integrated and bin figures are unchanged;
  - the six conditions and the two limiting ones are kept;
  - the coarse-projection non-discrimination is kept.
- **Intro roadmap**: new order, all refs resolve.
- **III**: one history clause cut, disclosed at IV A.
- **IV A** (2D reproduction, unchanged):
  - χ²/ndf indicative, learner range 2.64–2.75 and the exact-split values;
  - the post hoc LightGBM choice;
  - 0.98%/12.2% learner dependence outside the covariance.
- **IV B**:
  - universe block, flux, training-seed block;
  - G2 test "not tight";
  - run-period block with D5's required clause verbatim;
  - statistical block, its 0.26σ offset, and "coverage of this block has not been tested, and the coverage of the total remains untested";
  - old band 95.4/97.7/78.1, the post hoc and partly circular rescoring, "rebuilt band has not been independently tested either";
  - summary paragraph with every D1 must-carry item, "we make no claim about coverage" and the not-in-any-block list.
- **IV C**:
  - normalization and closure, signal-only closure, background bias up to 4% omitted from quoted uncertainties;
  - negweight 0.3%/1%/1.4%;
  - regularization bias 74% (now attributed), 16–31%, "within the quoted total uncertainty in about half";
  - rounding-level reproducibility;
  - 5D coverage now as F1 with numbers, "no frequentist coverage is claimed".
- **V (moved)**:
  - separate from the joint-test calibration; criteria not met (R-m3, R-n6);
  - no covariance-based significance and why; `\sprojMeasured` against `\sprojBound`;
  - the one-seed-pair limit; five pinned bands and their unmeasured seed sensitivity;
  - the study's failure and the fallback's 13.4% versus 10%; no new measurement uncertainty.
- **VI**:
  - one scope sentence replaces two identical ones;
  - the FSI limited to the chosen variations;
  - the low-recoil "not quantitative";
  - no response-mismatch closure for the map, and regularization bias largest there;
  - GiBUU's 20 GeV limit; shallow-inelastic "not independent confirmation".
- **VII A**:
  - hybrid null (now with the fine grid);
  - metric versus calibration (power versus size);
  - non-centrality; Holm with the CP determinacy;
  - stopping rule (F-p2-1, verified);
  - inputs fixed before production;
  - P15 holds every data-informed or post hoc item: design reviewers saw residuals; budget extension with p values visible and "remain valid"; the κ scan, rerun and coarse projections after the decisions and outside the rule; projections specified after the 5D outcomes; GENIE CV post hoc.
- **VII B**:
  - all six conditions;
  - (i) unmeasured and potentially material, shifts set before results, κ robust;
  - the carry-over condition to G;
  - "verifies the calculation, not whether the chain does so".
- **VII C**:
  - table unchanged;
  - κ scan outside the decision rule, one direction, bounds neither;
  - lost draws (R-n4, R-n5); margin 4.6/868.6;
  - no added discrimination;
  - hybrid-null global assessments (F15), region attribution requires separate tests;
  - power values and the 172–199 retained.
- **VII D** (unchanged):
  - the response band is absent and the effect on p is unmeasured;
  - GENIE CV not rejected in (p_T, p∥) alone (post hoc), so the rejecting information involves the hadronic axes;
  - the ±4% study and its untested effects; "conditional on the simulation's hadronic response".
- **VIII**:
  - 2D learner dependence and the untested 2D statistical block, now at the 2D sentence;
  - descriptive-only scope (R-m2);
  - biases, seed and model dependence (R-m1);
  - joint tests: no new uncertainty, six conditions, hybrid nulls, no added discrimination, recoil response and below-grid residual;
  - "recovering every lost pseudo-experiment changes no decision" is now only in VII C, a merge with no loss.
- **Data availability**: everything kept except the P6 chronology, which is verified in the note.

No new claim outside themes A and C was found, other than R-n8, which I judge to be within A. Apart from R-M1, the post hoc
disclosures, the 2D χ²/ndf and learner dependence, the untested 2D block, fine-grid convergence, the absence of added
discrimination, the GENIE CV muon-projection non-rejection and "3–5D central values only" are all present at
their claims and of base strength.

---

Path: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/p2-review-paper.md`

Counts: **MATERIAL 1** (R-M1), **MINOR 4** (R-m1–R-m4), **NOTE 11** (R-n1–R-n8, R-x1–R-x3).

---

## P24. Claude: independent preservation review, primer, note and bibliography (27edd449) (sha256 `b7b73bc0e8cbea3a…`)

### Plain-language pass 2: independent preservation review, primer and note/bibliography

Reviewer: fresh context, no authorship, read-only (no file edits in the worktree, no git writes).
Range: base `34650231` → new `27edd449` (note/bib changes in `b3fc422b`), worktree `wt-plain2`.
Rules applied: `PLAIN-LANGUAGE-PASS2.md`, `DECISION-20261018-joseph-plain-language-pass2.md`, and pass 1's
`PLAIN-LANGUAGE.md` where pass 2 does not override it.
Inputs: `git show` of both shas for every file (extracted to `scratchpad/rv2/`); the built primer
`pdfs-p2-27edd449/main_primer.pdf` (13 pp., read with `pdftotext -layout`); the writer's `p2-primer.md` and
`themeA-sources.md` were used as leads only. Every location cited as a home or a source below was opened.
Unless a file is named, line numbers are `primer_body.tex` at `27edd449`. The paper is `paper_body.tex`
and the abstract is `main_primer.tex`.

#### 1. Findings

| id | sev | base (34650231) | new (27edd449, file:line) | problem | minimal fix |
|---|---|---|---|---|---|
| P-1 | **MATERIAL** | l.153–252: the limits came in discovery order, with no ranking | `primer_body.tex:420-425` gives the ranking: "Three limits matter most, in this order. First … changed truth … Second, that uncertainty has not met the requirements … and it depends measurably on the learner's random seed. Third, a test of numerical stability, fixed in advance, failed." | The new ranking does not match the paper. The paper's own ranked statement (`paper_body.tex:76-86` at 27edd449; base l.73-77) is: "These biases, the dependence on the estimator's random seed, and **the untested or failed interval coverage** limit the method", plus the model dependence (P-9). Its Conclusions (l.1080-1085) give the same list. The paper ranks rounding stability below these. It "lies inside the data-bootstrap statistical uncertainty" for the joint-test estimator and "limits how exactly the central values can be reproduced" (l.550-553). The primer promotes it to third, and the failed five-quantity coverage test is not named in the lead at all: it survives only as the last sentence of the second paragraph (l.493-495). Nothing is lost from the body. But the "matter most" ranking gives a reader the wrong order | Make the lead's third limit the coverage failure, and demote stability: "Third, the one direct test of whether such error bars contain the truth as often as stated, made on a variant of the method, failed. A pre-set test of numerical stability also failed." Leave the run-in paragraphs as they are, or move the "Finally, the one direct test …" sentence to its own paragraph *Coverage* placed before *Numerical stability* |
| P-2 | MINOR | l.141-146 overview item 3 ended "…The learner's random seed also moves these central values, by an amount given below, and how far that could shift the corner's share of the excess was not measured." | `:148-154` | The overview restates the corner claim ("concentrated in one corner") with only "no significance". The seed and share caveat is gone from the overview; it is still at the body claim (`:378-382`). The director's new F-p2-1 caveat ("No test with a deliberately wrong detector response has been run for this map, and this corner is also where the unfolding's bias toward its starting simulation is largest", `:386-388`) is also not in the overview, so the overview reads stronger than the body at this claim. Pass 2 allows a caveat to be stated once in the body, so this is not a loss. But it is the caveat a reader of the overview needs about where the excess sits | Append to item 3: "The corner is also where the unfolding's pull toward its starting simulation is largest." (13 words) |
| P-3 | MINOR | overview item 2 gave no number | `:138-140` "…typical cells come back about \SI{10}{\percent} off, and the background removal…" | Theme-A number is correct (9.7 % median, `sec_5d.tex:73`; OUTCOME-…-s5n-stage1 :76). But the overview prints only the typical-cell size, while the body says "and the highest-$W$ cells much more" (`:437-438`; up to 74 %, `sec_5d.tex:74`). Alone, "about 10 %" understates the bias where the corner finding sits | Add ", and the highest-$W$ cells much more," after "off" |
| P-4 | MINOR | l.238-240 "Longer runs sometimes improve recovery **and sometimes leave a persistent residual**, but how much they vary …" | `:456-458` "longer runs sometimes improve recovery, but how much they vary …" | The P6 compression dropped the clause that qualifies the remedy, so the remedy now reads more promising than in the base. The note home (`sec_5d.tex:250-262`) carries it, but this remedy sentence stayed in the primer and is now one-sided | Restore "and sometimes leave a persistent residual" (5 words) |
| P-5 | MINOR | l.103-127 (no shares) | `:359-362` "…about two thirds lies at high available energy, most of it at high $W$, **and** about a fifth sits in the single widest corner cell." | The paper's sentence (`paper_body.tex` 34650231 l.571-576) is "…most of that at $W\ge1.8$ GeV, **but** a fifth of it sits in the single widest overflow cell … so the relative excess also extends to low $W$". There the catch-cell share is a caveat (its size comes from the wide cell). The primer turns it into support for the concentration claim. Neither base nor new mentions the low-$W$ excess, which the note also states (`sec_eavailw.tex:53`, "a secondary low-$W$ QE-like excess lies below 1.1 GeV"). The numbers are right (67 %, 83 %, 22 %: `sec_eavailw.tex:49-53`) | "…most of it at high $W$, but about a fifth of it sits in the single widest corner cell; in ratio, the excess also extends to low $W$." |
| P-6 | MINOR | l.267-270 (no calibration explanation) | `:549-551` "Because each pseudo-experiment repeats the whole analysis … these repeats set how often the test would wrongly reject a true hypothesis." | The new sentences match the paper (`paper_body.tex` 27edd449 l.772-773, "The metric influences each test's power; the null calibration determines its size"; l.777, l.799; the separate covariance at l.587-588). But this one is stated unconditionally. The note's own statement is conditional: "exact for the simulated null to the extent that the pseudo-experiment chain reproduces the analysis applied to the data. Two known departures are bounded" (`sec_joint.tex` "Calibration validity"). The conditions paragraph follows, but a reader of this sentence sees no hedge | Add "as far as the repeats reproduce the analysis of the real data" after "true hypothesis" |
| P-7 | MINOR | takeaway had no joint test | `:715-721` "That holds only under stated conditions: the test has no uncertainty for …, convergence as its grid is refined has not been shown, and it does not show … coarse projections." | The sentence is no stronger than the body (`:568-575`, `:586-592`), and it carries hybrid, the calorimetric response, grid convergence and the coarse-projection limit. But the colon makes the list read as complete, and its third item is not a condition at all. The body says six conditions | "That holds only under six stated conditions, in particular that the test has no uncertainty … and that convergence as its grid is refined has not been shown; nor does it show …" |
| P-8 | MINOR | `main_primer.tex` base abstract had no excess claim | `main_primer.tex:31-33` "…it recovers an established low-recoil discrepancy and locates an excess over MINERvA's tuned simulation; these results are central values only." | A headline claim new to the abstract. The paper's abstract does not carry it. "Central values only" is a fair hedge, but the abstract does not say that no significance is assigned, which is the caveat the overview gives this feature (`:153-154`) | "…locates an excess over MINERvA's tuned simulation; these are central values only, with no significance assigned." (+4 words; see P-10 for the room) |
| P-9 | MINOR (base defect, C7, for the director) | absent in base too | absent | The primer never says that the measured model dependence, about 10–13 % per cell, prevents a five-quantity measurement whose total uncertainties meet the 10 % target set in advance. That is the paper's negative headline (`main_paper.tex:68-70` abstract; `paper_body.tex:83-86`, :1083-1085) and the note's (`sec_summary.tex:34-37`). Pass 2 did not drop it. But the new "limits that matter most" framing makes the gap visible | Under C7, report and do not fix: a candidate theme-A sentence for the *Biases* paragraph is "This dependence on the starting model, about 10–13 % per cell, is too large for a five-quantity measurement to meet the 10 % precision target we set in advance." (source as in the paper's comment: RECORD-20260927-s5p-stage2-exit.md :133, :144) |
| P-10 | NOTE | 130 words | 155 words (rendered, `pdftotext`) | Over the ~150 budget by 5. The two framing sentences (`main_primer.tex:22-27`, about 50 words, "This is a short, jargon-light guide … It explains what the method does … and what we found") earn the least. Dropping "It explains what the method does in everyday terms," and "more practical than the traditional method does" would make room for P-8 and for the writer's F-p2-4 (naming the two joint-test conditions). Note, though, that "more practical than" carries ruling F2's comment | Director's choice |
| P-11 | NOTE | "about \SI{\sprojMeasured}" printed 6.145 % | `:477`, `:381`, `:410-411`, `:490-491`, `:682` | Rounding renders as claimed: "about 6 %", "at most about 6 % of their own uncertainty", "σext ≈ 4.5 × 10−38 cm2/nucleon" (PDF text lines 437, 486, 522, 531, 671). The primer now prints "about 6 %" for three different quantities within two pages: the seed shift of the uncertainty (6.145 %), the central-value movement as a fraction of σ (6.02 %), and the detector-supported share of the extended rate. The words keep them apart, but a reader can conflate them | Optional |
| P-12 | NOTE | — | `:359-360` "Of the extra cross section, summed over cells" | The record's operand is the **positive** excess (`sec_eavailw.tex:49-51`, "of all positive excess"; paper "of the positive difference"). "Extra … summed over cells" can read as the net difference | "Of the positive excess, summed over cells" |
| P-13 | NOTE (base) | l.263-266, l.280 | `:535-538`, `:573-575`, `:719` | The primer uses one "grid" both for the hypothesis and for the quantities tested. The paper separates the fine grid on which $H_0(G)$ is defined from the coarse $3^5$ test grid (`paper_body.tex` 27edd449 l.744-760). Pass 2 adds "convergence as the grid is refined has not been shown" to that single grid. This is correct for the fine grid, but the primer reader cannot tell which grid is meant | Optional: "the hypothesis is defined on a finer grid than the one the test reports" |
| N-1 | NOTE | `technote.bib` `ReleaseCandidate2026` "Article release candidate RC7: sufficient-input replay and figure regeneration" | `technote.bib` (27edd449) `ReleaseCandidate2026` "Candidate release package for the article: replay of the joint tests and regeneration of the figures" | RC7-README: RC7 draws Figs. 1–3 and the joint-null figure. But its Fig. 1 is the exact-split curve, and the article's Fig. 1 was regenerated separately (`app_release.tex:23-27` new; `main_paper.tex:148-150`). "The figures" is a little broader than the base's "figure regeneration". The new title also no longer names RC7, while `app_release.tex:10-11` names RC7 and cites this key | "Candidate release package RC7: replay of the joint tests and regeneration of four figures" |
| N-2 | NOTE | `JointTestRecovery2026` "…report-only recovery…"; `JointTestKappa2026` "…report-only sensitivity scan" | `publication.bib` new titles | Both records are report-only, and the κ record measures sensitivity "along that one direction only" (kappa RECORD header). The new titles drop both qualifiers. The bodies keep them (`sec_joint.tex:236-246`, :277; primer `:577-578`), so no finding is affected | Optional: "…to rescaling the assumed residual below the fine grid along one direction" |
| N-3 | NOTE | `sec_5d.tex` "recovery of at least 75% …, against 0.31–0.63 measured" | `sec_5d.tex:222-225` (the 0.25 clause at :224) "…that is, a residual proxy of Fig.~\ref{fig:gbdt-recovery} of at most 0.25, against 0.31–0.63 measured" | The correction is right. RECORD-20260927-s5p-stage2-exit.md defines the T2 proxy (median \|bias\|/\|departure\|, M its maximum over alternatives), gives the table at k = 5 (M_J 0.626, M_H2 0.314), and states "T2 needs ≤ 0.25" and "(0.25 against the measured 0.31–0.63)". "That is" equates the 75 % wording with the proxy bound, as the record does. The figure caption (`sec_5d.tex:247-248`) warns that one minus the proxy is not an exact recovered fraction, so "operationalized as" would be more exact | Optional |

**Not findings (checked, correct):**
- the director's rulings F-p2-1 and F-p2-2 (`:383-389`) against `paper_body.tex` 34650231 l.577-580. "No test with a deliberately wrong detector response" = "no closure test with a mismodelled detector response". "Bias toward its starting simulation" = the regularization bias of Sec. IV (l.505-511: failure to follow a changed truth). The "points theorists toward…" sentence is cut, leaving "The localized difference was only visible because we measured … jointly", which the base already supports (l.108-111).
- `result_status_rows.tex`: the content is unchanged in all three rows. "Independent recomputation" is supported by RECORD-20261005 ("independent recompute verdict", "independently reviewed comparer returned AGREE"). "Four measured limitations" matches `sec_execsummary.tex` ("Four measurements … limit every result built from the five-dimensional covariance").
- Bibliography keys are unchanged (7 entries).

#### 2. Moves and numbers verified

**Theme B (opened at 27edd449):**

| item | claimed home | verified |
|---|---|---|
| P1 four 2D repairs | `sec_systematics.tex` `sec:uq-2d-construction` | :205-255: May sweep truth-input mismatch (:207-214), Rvn1pi/Rvp1pi (:229-232), background-template statistics (:243), selection-complete laterals (:249). Yes |
| P2 PET chronology | `sec_pet_campaigns.tex` (via `pet_note.tex:62` → `sec_pet.tex`) | 0.316/0.306, 0.895/0.863 (:28, :88-89); robustness not statistically resolved (:92-94); 0.896/0.257/0.789 (:116-117); six-fit mean and √6 (:150-160); "Where generator recovery is lost" (:270-285); binned methods on the 1D tilt (:291). Yes |
| P4 six conditions | `sec_joint.tex` `sec:joint5d-conditions` | :118-178, all six, grouped by kind. Yes; the primer still names all six (`:569-583`) |
| P5 κ | `sec:joint5d-kappa` | :234-247 (5.2547/5.2563; 5.1688/5.1703; "one prescribed direction"). Yes; "no bound" is kept in the primer (`:577-578`) |
| P6 remedies | `sec_5d.tex` | no tradeoff (:141, :262), different integrals (:260), "guaranteed bias bounds" (:323). Yes (but see P-4) |
| P7 mis-sampled flux | `sec_5d.tex` "Generator-sized truth changes" | :66-71. Yes |
| P8 flux-repaired predictions | `sec_3d.tex:235-245`, `sec_eavailw.tex:97, :139` | Yes |
| P9 selection vs inputs table | `selection_features.tex` (input at `sec_experiment.tex:69`) | "PET design studies & Signal-only simulation banks" (:20). Yes |
| P-new-3 | within the primer | truth-cut sentence at `:678-679`; PET description at `:602-612`; "signal events only" at `:631`. Yes |

**Theme A (primer):**
- 9.7 % → "about 10 %": `sec_5d.tex:73`. Yes.
- 67 / 83 / 22 % → "two thirds / most / a fifth": `sec_eavailw.tex:49-53`, `paper_body.tex` l.571-573. Yes (see P-5 and P-12).
- `\sprojMeasured` 6.145, `\cvMoveOverSigmaMax` 6.02, `\fpsSigma` 4.502e-38: `values.tex:407, :458, :273`. Rounding renders as claimed.
- Fig. 2 legend "GENIE 2.12.6 + MnvTune v1", color red: `2d-unfolding/plot_2d_threeway_fig13.py:200`; GENIE 2.12.6 in `paper_body.tex` 34650231 l.111 and `sec_experiment.tex:24`. Yes.

**Note additions (b3fc422b):**
- `sec_5d.tex` coverage numbers match OUTCOME-20260925-s5c-tier-s-futility-fail.md §1 (UCB < 0.66 / < 0.94; tilt 51/42, min 0.060; nominal 2 at 95 %, min 0.850; 400 seeds × 3 truths = 1,200). The scope sentence (bias-corrected statistical intervals of a deterministic variant) sits directly above.
- `sec_joint.tex:27-33` (sentence at :31-33) fine grid = 14×16×7×7×6 is consistent:
  - `s5p_stage1_inspect.py:38-44` (FINE: 15/17/8/8/7 edges);
  - `s5p_truths.py` docstring ("rho (65,856 values)" for the fine-ratio null);
  - `mapping-notes-C.md:25` (U 109×65856);
  - 14·16·7·7·6 = 65,856, and every J edge is a FINE edge.

  The identification rests on code and an audit note, not on a decision record.
- `app_release.tex:17-27` matches the paper sentence it replaces (`main_paper.tex` 34650231 l.143-147).

**Joint test (primer):** it keeps all four required items:
- the hybrid nulls (`:160`, `:535`, `:716`; abstract);
- no calorimetric response uncertainty (`:162-163`, `:570-572`, `:718`);
- unshown grid convergence and an unbounded sub-grid error (`:164-165`, `:573-575`, `:719`);
- no added discrimination over matched coarse projections (`:165-166`, `:589-591`, `:719-721`).

#### 3. Preserved paragraphs (content identical or reworded, no change of strength)

- §1 and §2 up to Table 1.
- "One more distinction" (selection vs inputs, tree learner).
- Overview items 1, 5 and 6, and the "Each result is only as validated…" closer.
- All of *First, a trust check* except P1. That includes the uncertainty sizes and flux sentence, the learner qualification and post hoc choice, the excluded effects, the coverage-infrastructure paragraph and "no coverage claim", and the 91 % test with "They have not been tested". Fig. 2 also keeps its base text.
- All of *Then, measure more at once*: the "first at MINERvA" scope, normalization only, five coordinates and not five independent pieces, the low-recoil paragraph with 9.2 / 6.3 % and "not quantitative". Fig. 3 keeps everything except the P8 clause.
- The puzzle paragraph's generator comparison (14–16 %, 7–15 %, GiBUU 61 / 39 %, the 20 GeV supplement) and "not separately measured". Fig. 4 is unchanged except for the rounding.
- In *Limits*: the background 4 % / 0.3 % / 1 %, the auxiliary classifier, "Neither effect is in the quoted uncertainty yet", the 16–31 % and about half the cells, and the iterations and capacity result.
  - The uncertainty paragraph is complete: documented exception, two test versions not the quoted one, the quarter/half/full and factor-three argument, one seed pair, 5 of 45 fixed-seed components, the CV move, and the failed variant coverage test.
  - Also kept: the stability paragraph with the F4 ruling's limitation, the detector-coverage paragraph, "None of these studies changed…", and 2D independence.
- Joint test:
  - the hypotheses, the MEC/Tune v1 definitions, the 1,340–1,750 pseudo-experiments, "at most one", ten tests at 5 %, and the lost and rerun seeds with "one came close";
  - the post hoc GENIE CV projection paragraph with "not thereby accepted as true".
- PET: the overview item and the body's recoil-only diagnostic, method development only, no design met every requirement, no PET uncertainty used, all five cite keys, and Fig. 5.
- The signal-definition paragraph (a third excluded, simulation estimate, 6 % / 28 %, preliminary) and Fig. 6.
- The base takeaway paragraph, verbatim.

---

Path: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/p2-review-primer-note.md`

Counts: **MATERIAL 1** (P-1), **MINOR 8** (P-2 to P-9, of which P-9 is a base defect for the director),
**NOTE 7** (P-10 to P-13, N-1 to N-3).

---

## P25. Claude: primer fix round (sha256 `801c08110e19ce81…`)

### Plain-language pass 2: primer fix round (review P-1 … P-13)

Writer: primer fix round. Worktree `wt-plain2` at `27edd449`. Files edited: `docs/analysis-note/primer_body.tex`
and `main_primer.tex` only. I did not touch the director's uncommitted `paper_body.tex` / `main_paper.tex`, and I
made no git writes. Pre-fix copies are at `$S/primer_body.pre-fix-r2.tex` and `$S/main_primer.pre-fix-r2.tex`.

Each site carries `% plain-language pass 2, review fix <id> (DECISION-20261018-joseph-plain-language-pass2)` on its own
line, with a source comment below it. P-9 carries
`% plain-language pass 2, director ruling on base defect P-9 (DECISION-20261018-joseph-plain-language-pass2)`.
There are 15 markers: 14 in `primer_body.tex` and 1 in `main_primer.tex`. All 76 base comment lines survive verbatim.

#### 1. Findings and dispositions

Line numbers are `primer_body.tex` after the fix, unless the abstract is named.

| id | disposition | new text (line) | checked against |
|---|---|---|---|
| **P-1** MATERIAL | **Fixed.** The lead now names four limits, in the paper's order: biases, the unvalidated and seed-dependent uncertainty, untested or failed coverage, and model dependence. Stability follows them as the reproducibility limit. Coverage gets its own run-in paragraph *Coverage.*, placed before *Numerical stability.* The sentence is moved verbatim from the end of the uncertainty paragraph, minus "Finally," | l.439–455: "Four limits matter most. First, the unfolding follows a changed simulated truth only partly … Second, that uncertainty has not met the requirements … random seed. Third, whether the five-quantity error bars contain the truth as often as stated is untested, and the one direct test of it, made on a variant of the method, failed. Fourth, [P-9] … A test of numerical stability, fixed in advance, also failed; it limits how exactly the central values can be reproduced." l.536–538: "*Coverage.* The one direct test …" | `paper_body.tex` Intro l.76–86 ("These biases, the dependence on the estimator's random seed, and the untested or failed interval coverage limit the method, and the measured model dependence … prevents …"); Conclusions l.1080–1090; stability l.550–553 ("limits how exactly the central values can be reproduced") |
| **P-9** director ruling | **Added** as the fourth ranked limit, in theme-A form with a source comment (l.446–450) | l.451–454: "Fourth, the result depends on the simulation the unfolding starts from: this measured model dependence, a median of about 10 % to 13 % per cell, prevents a five-quantity measurement whose total uncertainty meets the 10 % precision target we set in advance." | `main_paper.tex:66-68` and `paper_body.tex:84-86`, :1088-1090 (same wording); note `sec_5d.tex` "Reporting definitions …" (12.0 / 9.6 / 13.4 %; target "median 68 % half-width at most 10 %"); `RECORD-20260927-s5p-stage2-exit.md:131-144` ("≈ 10–13% per coarse joint cell"); themeA F4 |
| P-2 | Fixed, overview item 3 | l.159–160: "The corner is also where the unfolding's bias toward its starting simulation is largest." (the body's own wording, l.~401) | `paper_body.tex` at 34650231 l.577–580 |
| P-3 | Fixed, overview item 2 | l.142–143: "typical cells come back about 10 % off and the highest-$W$ cells much more, and the background removal …" | `sec_5d.tex:73-74` (9.7 % median; up to 74 % in the highest-W column) |
| P-4 | Fixed: the base clause is restored | l.489–490: "longer runs sometimes improve recovery and sometimes leave a persistent residual, but how much they vary …" | base `primer_body.tex` at 34650231 l.467–468 |
| P-5 | Fixed | l.373–376: "… most of it at high $W$, but about a fifth of it sits in the single widest corner cell; as a ratio to the simulation, the excess also extends to low $W$." | `paper_body.tex` at 34650231 l.571–576 ("but a fifth … so the relative excess also extends to low W"); `sec_eavailw.tex:49-53` |
| P-6 | Fixed | l.601–602: "… how often the test would wrongly reject a true hypothesis, as far as they reproduce the analysis of the real data." | `sec_joint.tex:151-154` "Calibration validity" |
| P-7 | Fixed: "six"; "in particular"; the coarse-projection limit separated with "nor" | l.776–780: "That holds only under six stated conditions, in particular that the test has no uncertainty for the calorimeter's response to the hadronic recoil and that convergence as the fine grid defining the hypotheses is refined has not been shown; nor does the test show that the five quantities together discriminate better than matched coarse projections." | `paper_body.tex` Conclusions l.1093–1103 |
| P-8 | Fixed (abstract) | `main_primer.tex:35-36`: "these are central values only, with no significance assigned." | overview item 3 ("Neither feature is assigned a statistical significance") |
| P-10 (abstract budget) | Fixed. "what the method does in everyday terms," and the closing "does" were cut. "More practical than" (ruling F2) and its comment are kept, and so is "closely reproduces" (F12) | `main_primer.tex:24-31`: "It explains why the method makes measuring several quantities at once more practical than the traditional method, and what we found." | — |
| P-11 NOTE | Fixed at the one site where the two 6 % values sit side by side. The Fig. 4 caption and the puzzle paragraph already name "of their own uncertainty", and the σ_ext "6 % of the rate" already says what it is | l.528–529: "… at most about 6 % of their own uncertainty, a separate measurement from the shift of the uncertainty itself." | `values.tex:407` (`\sprojMeasured`, GRADE json) vs `:458` (`\cvMoveOverSigmaMax`, CENTRAL-VALUE-VS-SIGMA json) |
| P-12 NOTE | Fixed | l.373: "Of the excess, summed over the cells where the data lie above the simulation, …" | `sec_eavailw.tex:49-51` ("of all positive excess"); paper "of the positive difference" |
| P-13 NOTE | Fixed at all four sites: the hypotheses are on the fine grid, and the test is on a coarser grid | l.173–174 (overview: "finer than the grid on which the hypotheses are defined"); l.582–585 ("in each cell of a fine grid … the fine grid specifies the hypothesis, and the test compares data and hypothesis in the cells of a coarser grid"); l.625–627 ("And the hypotheses are defined only down to the fine grid: convergence as that grid is refined has not been shown, and the possible error from structure finer than it is not bounded"); takeaway l.778 | `paper_body.tex` sec:joint l.744–760 (H0(G) on the fine grid; tests on the coarse 3^5 grid) |
| N-1, N-2, N-3 | Not mine (note and bibliography); left for the note writer or director | — | — |
| layout | Fig. 5 (`fig:primerpet`) placement `[H]` → `[tbp]` (l.705–708, marked P-1, P-9). This is layout only, with no text change. The first build at `[H]` gave 14 pages, with the bibliography spilling three-quarters of a page and pages 11–12 half empty. Fig. 5 now sits at the top of p.12, still inside its section, so the primer is back to 13 pages. I tried a float for Fig. 6 and rejected it: it split the takeaway | — | — |

**Not done (for the director):**
- The model-dependence headline (P-9) is stated once, in the ranked limits. It is not in the overview's item 2 or in the primer abstract. Adding it to the abstract would cost about 25 words over the 150 budget.
- F-p2-4 (naming the two joint-test conditions in the abstract) remains unmade, for the same budget reason.

#### 2. Invariance check

`python3 -I …/check_invariance.py $W 34650231 > $S/inv-p2-primer-r2.out; echo rc=$?` → **rc=1**. Primer block:

```
[DIFF] numerals: lost {'95':1,'31':1,'5.26':1,'5.17':1,'90':2,'86':1,'68':1,'26':1,'79':1}
                 gained {'10':3,'2.12':2,'2':1,'0':4,'13':1}
[SAME] value macros (13)   [SAME] cite keys (7)   [SAME] labels (3)
[DIFF] ref targets: gained {'fig:primergen':1}
[SAME] comment lines: all 76 base lines survive    [INFO] comment lines added (123)
== new lines with a mid-line comment: [SAME] none
```

Compared with the integration round (`inv-p2-primer.out`), the only new numeral differences are **+2 × '10' and
+1 × '13'**. These are the P-9 theme-A numbers ("about 10 % to 13 % per cell", "the 10 % precision target"), and their source comment is at
l.446–450. Everything else is unchanged and was explained in `p2-primer.md` §6:
- the theme-B PET and κ values out;
- the theme-A 10 %, the GENIE 2.12.x versions and the siunitx rounding options in;
- the Fig. 2 → Fig. 3 ref.

The rc=1 comes from those primer differences and from the other writers' note/bib files, none of which are mine. No primer line is in the
mid-line-comment block.

#### 3. Build, pages, abstract

`$S/build_copy.sh p2-primer-r2 $W` → **rc 0** (`build_all rc=0`).
- All four PDFs report "written by this run; no unresolved references".
- `main_primer.log` has 0 reference or citation warnings, and there is no "??" in the primer text.
- Gates:
  - containment: SELF-TEST PASS, RESULT PASS (strict);
  - gzip receipt: PASS;
  - Sec. IV receipts: SELF-TEST PASS (18 perturbations rejected), SEC4-RECEIPTS PASS (15/15).

| PDF | pages |
|---|---|
| main_primer | **13** (unchanged from the integration round) |
| main_paper | 12 |
| main_note | 123 |
| pet_note | 26 |

Primer PDF: `$S/builds/p2-primer-r2/repo/docs/analysis-note/main_primer.pdf`, sha256 `0cfe8ef9…0c34`.

**Abstract: 155 → 151 words.** That is the source count, matching the integration report; the rendered count is also 151.

**Pages read** (pdftotext, rebuilt PDF): 1 (abstract), 3–4 (overview), 7–8 (puzzle paragraph, Fig. 4, limits lead), 9
(Biases, remedies, uncertainty, Coverage, Numerical stability), 10 (joint test, calibration, conditions), 11–13 (PET,
Fig. 5 at the top of p.12, signal definition, Fig. 6, takeaway, references). Every changed site reads as intended. There is
no stray comment text, the two-6 % sentence reads cleanly, "10 % to 13 %" renders through `\SIrange`, and the takeaway
heading on p.12 has two lines under it before the break.

---

Path: `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/p2-fix-primer.md`

1. P-1 (MATERIAL) is fixed. The limits lead now ranks them as the paper does: biases, the seed-dependent unvalidated uncertainty, untested or failed coverage, and model dependence. Rounding stability follows as the reproducibility limit, and coverage has its own run-in paragraph.
2. P-9 (director ruling) is added as the fourth limit: "a median of about 10 % to 13 % per cell, prevents a five-quantity measurement whose total uncertainty meets the 10 % precision target we set in advance". It carries the sec_5d / RECORD-20260927 source comment.
3. P-2 to P-8 and the NOTEs P-11, P-12 and P-13 are fixed as proposed, each checked against the paper or note. P-13 separates the fine hypothesis grid from the coarser test grid at all four sites.
4. Invariance rc=1 is explained. The only new differences are the P-9 numerals (+10 ×2, +13). All 76 base comments survive, and there are no mid-line comments.
5. Build rc 0, no unresolved references, gates PASS. The primer is 13 pages (Fig. 5 moved to `[tbp]` to undo a 14th page), and the abstract went from 155 to 151 words.
