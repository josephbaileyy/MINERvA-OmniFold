# r22 Step 2 agy triage: chunks 06-09 (67 rows)

Measured against `$WT` at HEAD `ee520a19e` (clean tree), base `9d3054f9`. Every "now prints" quote was found by
`grep -F` in `$WT/docs/analysis-note/`. Every "base" quote comes from `git show 9d3054f9:docs/analysis-note/<file>`.
I use RATER-WRONG both when the DETAIL misreads the pair and when the change it names is wording only (no fact,
qualifier or limitation changes).

Counts: MOVED-OK 33, SUPPORTED 18, RATER-WRONG 8, REAL 8, UNSURE 0.

| chunk | Q | file tag | class | evidence | fix |
|---|---|---|---|---|---|
| chunk06 | Q1 | sec_joint.tex JT93 | MOVED-OK | The base already says "of every $p$ value and decision". The count is now in the records file: app_provenance.tex "the independent recomputation (verdict AGREE, 1379 of 1379 rows)" (ledger B10-7). | none |
| chunk06 | Q2 | sec_joint.tex JT101 | MOVED-OK | The verbatim quote is in the records: app_provenance.tex "the result, with its six conditions verbatim". Its numbers now print in sec_joint.tex: "is \jtMoneMin--\jtMoneMax{} of the whole change" (0.50/0.86), "claim variants at $\pm\jtMoneKappa\,\delta_{\mathrm{fine}}$" ($\kappa=2$), and conditions (ii)-(vi) in their own paragraphs (rows Q7-Q10). | none |
| chunk06 | Q6 | sec_joint.tex JT115 | REAL | The fact is SUPPORTED by the base quote (i), "its size in null-$T$ units (with the frozen $V$) is committed before the first look". But the base calls $\Sigma=V+\mathrm{diag}\,\mathrm{Var}(\mu_{G})$ "the metric" and $V$ "a Ledoit--Wolf-shrunk covariance", so the label "the fixed metric $V$" is not supported. | See R1 |
| chunk06 | Q7 | sec_joint.tex JT118 | SUPPORTED | Base quote (vi): "the predictions' own finite MC enters as $\mathrm{diag}\,\mathrm{Var}(\mu_{G})$ in the metric and as a drawn residual term". The base generative-model figure of the calibration has the step "add lateral, normalization, rounding, prediction terms: $T_{\mathrm{null}}$". | none |
| chunk06 | Q8 | sec_joint.tex JT121 | REAL | All the numbers are SUPPORTED by base quote (iv): "$D$ (16 pairs)", "median $\lvert D\rvert/f$ 0.02--0.075\%", "proxy $a/\mathrm{se}$ $+4.7$ MnvTune, $-3.4$ NuWro", "[measured with the frozen $V$ before any observed statistic: at most 0.068]", and "${\sim}0.05$". The same "fixed metric $V$" label as Q6 is not supported. Two minor glosses also lack a base source: "proxy significance" and "relative shift". | See R2 |
| chunk06 | Q9 | sec_joint.tex JT136 | SUPPORTED | Base quote (ii): "per event ... (MinosEfficiency, GEANT neutron/pion/proton, each $\pm1\sigma$) and the linear lateral surrogate (five bands)". The gloss is in base app_statmethods.tex: "\texttt{MinosEfficiency} (MINOS muon-match efficiency)". "GEANT4 hadron-interaction reweights" is in the base sec_joint generative model. | none |
| chunk06 | Q10 | sec_joint.tex JT138 | SUPPORTED | Base quote (ii): "there is no recoil-energy-scale band in the analysis's systematic set [App.~\ref{app:statmethods}], so hadronic-response completeness is not established". Base quote (iii): "LowQ2\_1/HighQ2\_1 ... [measured on the pilot] ... in whitened norm". "Reweighting bands": base sec_experiment.tex says "a vertical band reweights events". | none |
| chunk06 | Q13 | sec_joint.tex JT167 | SUPPORTED | The preceding base sentence defines the quantity: "At the GENIE~2.12.10 null the shape powers at 0.005 are \jtPowPonegShape, 0.02 and 0.00". So "the first GENIE~2.12.10 set moves to 0.72" is the shape power at 0.005 against the first alternative. | none |
| chunk06 | Q14 | sec_joint.tex JT180 | MOVED-OK | "856 of 856" is in app_provenance.tex: "independent cross-check (856 of 856 quantities; frozen-shift reading only". The reporting status prints in sec_joint.tex: "the rerun of the lost pseudo-experiments (\S\ref{sec:joint5d-lost}) ... They are for reporting only, outside the decision rule." The rejections holding prints in the same subsection: "No recovered draw reaches the observed statistic ... so no assignment of the lost draws changes any decision." | none |
| chunk06 | Q21 | sec_fps.tex FP6 | MOVED-OK | The section opening of sec_fps.tex has "The truth-muon kinematic cuts are removed, but the reconstructed MINOS-based selection is unchanged" (ledger B11-2). | none |
| chunk06 | Q28 | sec_summary.tex SU0 | MOVED-OK | The next paragraph of sec_summary.tex: "The executive summary lists the principal limitations, each with the section that states it." Note that both `\pageref` calls in sec_summary.tex were removed (gap s-05). The page reference to the limitations still prints in sec_intro.tex. | none |
| chunk06 | Q33 | app_guide.tex AG8 | SUPPORTED | The new row gathers base text from app_statmethods.tex: "i.e.\ \texttt{np.cov(Xrep, rowvar=False, ddof=1)}" (after eq:bootcov), "\texttt{np.random.default\_rng().poisson(1.0)}" (app:poisson), "calls \texttt{np.linalg.pinv} at its default" (sec:invert), and "band sum without the normalization band (\texttt{-{}-add-norm 0})" (sec:minerva). | none |
| chunk06 | Q34 | app_statmethods.tex AA0 | MOVED-OK | The list item names the renamed subsection "Summary of the 2D comparison numbers". Its provenance table still prints as "\subsubsection*{Sources of the 2D comparison numbers}". | none |
| chunk06 | Q35 | app_statmethods.tex AA11 | MOVED-OK | "\texttt{np.linalg.pinv}" and "(default cutoff)" are in the app_guide.tex row. The lstsq/MATLAB contrast is in the unchanged records file app_history.tex:145: "convention of \texttt{np.linalg.lstsq} and MATLAB" (ledger B12-5). The cutoff value is kept: "$\tau = 10^{-15}\,\sigma_{\max}$". | none |
| chunk06 | Q36 | app_statmethods.tex AA15 | MOVED-OK | sec_systematics.tex: "Each setting is a triplet $(s,s{+}1,s{+}2)$ of seeds ... with $s\in\{42,45,48,51,54\}$". The name random\_state is in records_estimators.tex ("random\_state=seed"). The July label prints in sec:universes: "The universe sweep used by the quoted budget (the July sweep)". | none |
| chunk06 | Q38 | app_statmethods.tex AA22 | MOVED-OK | np.cov is in the app_guide.tex row. "Cholesky factorization and ridge jitter" is the base sec:invert heading "\paragraph{Cholesky and ridge jitter.}". | none |
| chunk06 | Q39 | app_statmethods.tex AA30 | MOVED-OK | The call is in the app_guide.tex row: "\texttt{np.random.\allowbreak default\_rng().\allowbreak poisson(1.0)}". | none |
| chunk06 | Q40 | app_statmethods.tex AA32 | REAL | Most of the row is MOVED-OK. MNV101\_ACTIVE\_UNIVERSE is already in the app_guide.tex label table. The muon-scale and MINOS-efficiency glosses are base ("(muon energy scale)", "(MINOS muon-match efficiency)"). The problem is the symbols $M_{A}^{\mathrm{RES}}$, $M_{V}^{\mathrm{RES}}$, $M_{A}^{\mathrm{CCQE}}$: no base file writes them (base: "GENIE knobs \texttt{MaRES}, \texttt{MvRES}, \texttt{MaCCQE}"). They are a gloss from general knowledge. | See R3 |
| chunk07 | Q1 | app_statmethods.tex AA47 | REAL | The caption label is fine ("the July sweep" is given in sec:universes). The MINOS and MINERvA muon-energy-scale and MINOS muon-match-efficiency names are base (AA32). The table rows "$M_{A}^{\mathrm{RES}}$ (MaRES)" and the others have the same unsupported symbol gloss as Q40. | See R4 |
| chunk07 | Q2 | app_statmethods.tex AA49 | RATER-WRONG | Wording only. "These are the bands that the Ruterbories paper identifies" is a definite description, so it still states that the two sets are the same; "exactly" was an intensifier. | none |
| chunk07 | Q4 | app_statmethods.tex AA60 | RATER-WRONG | Wording only. A non-block-diagonal piece of a per-band covariance is a correlation between bands. The content under the removed run-in label is kept verbatim: "It leaves to MAT, or does not state, ...". | none |
| chunk07 | Q5 | app_statmethods.tex AA65 | SUPPORTED | Base app_statmethods.tex defines "$\mathbf{C}^{B}_{\text{CV-centered}}$" for this pair formula and states "CV-centering adds the rank-1 $\mathbf{m}\mathbf{m}\T$". "It" refers to the previous sentence's subject, \texttt{MnvVertErrorBand::CalcCovMx}. | none |
| chunk07 | Q6 | app_statmethods.tex AA67 | MOVED-OK | The app_guide.tex row: "\texttt{-{}-add-norm 0} & ... the earlier MAT check's option without the normalization band (\S\ref{sec:minerva})". | none |
| chunk07 | Q8 | app_statmethods.tex AA79 | MOVED-OK | The label prints once in sec:universes ("(the July sweep)") and in the app_guide.tex table ("the quoted universe block uses the July sweep"). | none |
| chunk07 | Q9 | app_statmethods.tex AA93 | MOVED-OK | The call is in the app_guide.tex row ("\texttt{np.linalg.pinv} ... \S\ref{sec:invert} (default cutoff)"). | none |
| chunk07 | Q17 | app_statmethods.tex AA161 | MOVED-OK | The sentence is now the definition at "The obstruction": "A data-to-model $\chi^{2}/\mathrm{ndf}$ with this analysis's covariance alone, $\chi^{2}_{\ours}$, requires inverting $\mathbf{C}^{\ours} = ...$". | none |
| chunk07 | Q20 | app_statmethods.tex AA177 | MOVED-OK | sec:chisq prints "and three limits apply to every use of it". Limit (i) is the paragraph that contains eq:diffcov, so the parenthesis points to the right place. | none |
| chunk07 | Q22 | app_statmethods.tex AA182 | RATER-WRONG | The previous sentence is "This derivation supports \S\ref{sec:results-tension}", so "the derivation" resolves the base pronoun as the base intends. Ledger B12-24. | none |
| chunk07 | Q29 | app_statmethods.tex AA209 | REAL | "This is direct evidence that ... is OmniFold's implicit regularization" became "We therefore attribute ... to OmniFold's implicit regularization". The strength of the claim is weakened (in the conservative direction). "Genuine" is covered by the next sentence: "Normalization and small-$\lambda$ inversion artifacts do not drive it." | See R5 |
| chunk07 | Q30 | app_statmethods.tex AA213 | RATER-WRONG | Wording only. "is the covariance structure that governs" is still a definite identification; "exactly" was an intensifier. | none |
| chunk07 | Q31 | app_statmethods.tex AA238 | MOVED-OK | The causes print in limit (i) of sec:chisq, which the new sentence cites: "For estimates $x$ and $y$ from the same data ... Without $C_{xy}$ ... No value of the statistic ... can be converted to a goodness-of-fit probability". | none |
| chunk07 | Q32 | app_statmethods.tex AA242 | MOVED-OK | The row points to \S\ref{sec:universes}, which prints "(the July sweep)". The heading change is wording. | none |
| chunk07 | Q33 | app_statmethods_nd.tex AB4 | SUPPORTED | Base app_release.tex: "Load $M$ ... and $C_{Z}$ ... The five-axis covariance of the configuration-(a) central value is the file \texttt{z-cv.npz}, ..., so a loaded $C_{Z}$ can be checked". Base sec_5d.tex eq:zassembly also has "$C_{Z} \;=\; ...$" under sec:eavailw-adopted. | none |
| chunk07 | Q34 | app_statmethods_nd.tex AB6 | SUPPORTED | Base AB18 in the same file: "A sum of about 45 deterministic rank-one MAT outer products plus statistical and ML blocks". "Not a defect" is an evaluative tag; "follows from the construction" keeps the claim. | none |
| chunk07 | Q35 | app_statmethods_nd.tex AB8 | REAL | Base: "Every N-D $\chi^{2}$ must state (i) ...". New: "The reporting convention for an N-D $\chi^{2}$ is to state ...". The requirement is weakened to a convention. "Or that none is applied" for "or explicit absence of one" is acceptable. | See R6 |
| chunk07 | Q36 | app_statmethods_nd.tex AB11 | MOVED-OK | The topic removed from the heading still prints in the same subsection: "No generic correction is prescribed." | none |
| chunk07 | Q37 | app_statmethods_nd.tex AB18 | MOVED-OK | "About 45" prints in AB6 ("a sum of about 45 rank-one outer products"). The example is SUPPORTED by base AB4/AB6, where the earlier 5D covariance is the "~45 two-endpoint MAT bands plus statistical and ML blocks" object. | none |
| chunk07 | Q40 | app_statmethods_nd.tex AB36 | SUPPORTED | Base, same file: "For experiment $i$ ... The truth of the stored pseudo-data source varies with the MC split". The development experiments are pseudo-data experiments. | none |
| chunk08 | Q4 | app_negweight.tex AC7 | MOVED-OK | The opening of the same paragraph: "The numbers in this appendix are not quoted uncertainties". "To binned purity": the appendix's comparison is negative-weight against binned purity (base AC72, "compared to binned purity"). "Natural" prints in the introduction (ledger B13-12). | none |
| chunk08 | Q5 | app_negweight.tex AC61 | SUPPORTED | Base AC116: "With the histogram backend, the real-data totals agree to \SI{\nwPctTot}{\percent} ... These are the comparisons of \S\ref{sec:negweight-2d} and ...". | none |
| chunk08 | Q6 | app_negweight.tex AC72 | MOVED-OK | Moved from base AC116: "On the 2D ME~FHC measurement at full statistics with LightGBM, the estimator of the quoted 2D central value, the two covariances differ by one to two percent." | none |
| chunk08 | Q7 | app_negweight.tex AC75 | MOVED-OK | Moved verbatim from base AC116. The operands are now assigned by order in "(negative-weight/purity) is ..., from A and B" rather than labelled one by one, as the base did ("negative-weight", "purity", "respectively"). | none |
| chunk08 | Q8 | app_negweight.tex AC78 | MOVED-OK | \S\ref{sec:negweight-2d} prints "median $\nwMedianBin$ and \SI{\nwRmsBin}{\percent} RMS" and "(\SI{\nwWorstBin}{\percent})". | none |
| chunk08 | Q9 | app_negweight.tex AC85 | MOVED-OK | The two kinds of evidence still print: "as established by elimination from their job scripts and logs", and "Current production fixes the background treatment in a configuration object that rejects every other mode." | none |
| chunk08 | Q10 | app_negweight.tex AC88 | MOVED-OK | "Passes ... explicitly from that configuration" carries "rather than inheriting the default". The inference-by-absence case prints as "established by elimination" in the previous paragraph. | none |
| chunk08 | Q11 | app_negweight.tex AC91 | RATER-WRONG | "Inferior to one that uses either treatment consistently" keeps "worse than either consistent choice", which is the content of "not an upgrade". The base's lateral-block sentence was also hypothetical. | none |
| chunk08 | Q13 | app_negweight.tex AC110 | MOVED-OK | The ledger name is in the records: app_provenance.tex "(\texttt{VALIDATION\_LEDGER.md}, ``FPS MEFHC battery'')" (ledger B13-28). | none |
| chunk08 | Q15 | app_negweight.tex AC116 | MOVED-OK | Every number prints in AC72/AC75 (\S\ref{sec:negweight-uq}). The histogram-backend totals print in \S\ref{sec:negweight-2d}. | none |
| chunk08 | Q16 | app_negweight.tex AC127 | SUPPORTED | Base AC116: "These are the comparisons of \S\ref{sec:negweight-2d} and \S\ref{sec:negweight-uq}". The covariances are those of negweight-uq, and the reference replaces an antecedent that was lost. | none |
| chunk08 | Q17 | app_negweight.tex AC134 | MOVED-OK | Two sentences earlier, in the same paragraph: "It does not show that the background treatment is irrelevant in five dimensions, which would require the full comparison." "Safe" was evaluative. | none |
| chunk08 | Q20 | app_response_mismatch.tex AD0 | MOVED-OK | The opening of the appendix (AD3): "Its first stage has been implemented but not yet run: no output has been produced and no pass threshold has been set." | none |
| chunk08 | Q21 | app_response_mismatch.tex AD3 | SUPPORTED | Base AD0: "(protocol implemented; not yet run)". Base AD18: "This appendix records a validation protocol, not a result or an uncertainty component. No response-mismatch output has been produced and no pass threshold has been set." | none |
| chunk08 | Q22 | app_response_mismatch.tex AD7 | REAL | The Eq. reference is SUPPORTED: base sec_3d.tex eq:eavail-reco-implemented is "$E_{\rm avail}^{\rm reco}=1.17[...]$", with "Both definitions were inherited". But "That amplitude remains to be specified" asserts a status that the base does not state. The base says only "should justify that amplitude". It would become SUPPORTED if a record states that no amplitude has been fixed. | See R7 |
| chunk08 | Q26 | app_response_mismatch.tex AD18 | MOVED-OK | Moved to AD3: "This appendix gives a validation protocol for such a test, not a result or an uncertainty component. ... no output has been produced and no pass threshold has been set." | none |
| chunk08 | Q27 | app_response_mismatch.tex AD22 | REAL | Base: "would not be absorbed silently into a non-closure error", which forbids silent absorption. New: "rather than inclusion in a non-closure error", which forbids any inclusion. That overstates the base, and "separate" is added. | See R8 |
| chunk08 | Q28 | app_landscape.tex AE0 | MOVED-OK | The text now defines it: "dimensionality: the number of kinematic variables unfolded simultaneously in each analysis's main differential result". The caption points to it ("defined in the text"). | none |
| chunk08 | Q29 | app_landscape.tex AE4 | RATER-WRONG | Wording only. The dimensional fact (three variables, like our 3D result, with a different signal) is kept. "Direct dimensional precedent" is an evaluative frame, and dropping it loses no limitation. | none |
| chunk08 | Q31 | app_release.tex RL5 | MOVED-OK | RL14 now prints "The package also carries the 20 rounding jitters of the data, from which the stability of the observed $p$ values ... can be recomputed; no packaged script recomputes it." The verifier is the package's own script. | none |
| chunk08 | Q32 | app_release.tex RL10 | RATER-WRONG | "Regenerated" to "drawn" is wording: the source, the code and the separateness are kept, and nothing is said about what exists or what is deposited. "Current" is supported by RL5: "which neither this note nor the article now prints". | none |
| chunk08 | Q33 | app_release.tex RL14 | SUPPORTED | Base, same file: "The pseudo-experiment products are archived (about \SI{2.3}{GB})". Base RL42 attaches the covariance's limiting measurements to "(\S\ref{sec:eavailw-adopted})". | none |
| chunk08 | Q37 | app_release.tex RL42 | SUPPORTED | Base sec_5d.tex (sec:eavailw-adopted): "Four measurements limit what the covariance supports." The dropped "that readers will quote" is a description of the package, not a fact or a limitation. | none |
| chunk08 | Q38 | app_release.tex RL49 | RATER-WRONG | The register changes from imperative to declarative. The same sizes, shapes and checks are stated, and the list is still "the following computation" that the package "is to support". | none |
| chunk09 | Q2 | app_release.tex RL65 | SUPPORTED | Base sec_5d.tex item 1 under sec:eavailw-adopted: "Estimator-seed sensitivity exceeds its limit." | none |
| chunk09 | Q3 | app_codebase.tex AH5 | SUPPORTED | The paths are moved: the 2D path is in AH12, and the N-D path is a ledger home (B15-29, L: docs/HIGHER_DIM_OMNIFOLD_DESIGN.md and README.md, both checked). The options are in the base app_guide.tex table: "\texttt{purity}, \texttt{negweight}, \texttt{negweight-refined} & the values of the drivers' background-mode option ...: purity-based subtraction, negative-weight injection, and refined negative-weight subtraction". Base app_negweight.tex also has "negative-weight injection with Stay-Positive refinement". | none |
| chunk09 | Q4 | app_codebase.tex AH9 | MOVED-OK | The alias now lives in a ledger home: L: 2d-unfolding/2D_OMNIFOLD_REFERENCE.md "over the lgbm seedscan (`seedscan_lgbm/`)" (ledger B15-32, checked, 4 hits). | none |
| chunk09 | Q5 | app_codebase.tex AH12 | SUPPORTED | Base AH5: "per-analysis orchestration in \texttt{2d-unfolding/unfold\_2d\_omnifold\_unbinned.py}". | none |
| chunk09 | Q6 | app_codebase.tex AH14 | SUPPORTED | The base figure caption reads "Empirical coverage of statistical intervals for the 153 reported cell and projection integrals, corrected for nominal-truth bias". Base sec_5d.tex has "assessed statistical intervals ... with nominal-truth bias correction". The note uses coverage as a containment fraction elsewhere, for example base sec_fps.tex "contain the fixed truth in \SI{\covFPS}{\percent} of evaluation bin--toy cells". | none |

## REAL rows: base text, new text and fix

Each `old_str` was checked with `grep -F -o ... | wc -l` and occurs exactly once in the current file in `$WT`.

**R1. chunk06 Q6, sec_joint.tex JT115.** The label "metric" for $V$ is not supported.
- Base, quote (i): "its size in null-$T$ units (with the frozen $V$) is committed before the first look". Base JT115: "Measured before any observed statistic, the claim variants move ...". Base definition: "The metric $\Sigma=V+\mathrm{diag}\,\mathrm{Var}(\mu_{G})$ ... Here $V$ is a Ledoit--Wolf-shrunk covariance".
- New: "Measured with the fixed metric $V$ before any observed statistic, the claim variants ...".
- Fix:
  - old_str: `Measured with the fixed metric $V$ before any observed statistic`
  - new_str: `Measured with $V$ fixed before any observed statistic`

**R2. chunk06 Q8, sec_joint.tex JT121.** Same label as R1. The numbers are supported.
- Base, quote (iv): "[measured with the frozen $V$ before any observed statistic: at most 0.068, ...]".
- New: "That bound was measured with the fixed metric $V$ before any observed statistic, and it supersedes ...".
- Fix:
  - old_str: `That bound was measured with the fixed metric $V$ before any observed statistic`
  - new_str: `That bound was measured with $V$ fixed before any observed statistic`
- Optional strict fixes for two glosses with no base source (base: "proxy $a/\mathrm{se}$", "median $|D|/f$"):
  - old_str `proxy significance $a/\mathrm{se}$ of`, new_str `proxy $a/\mathrm{se}$ of`
  - old_str `with a median relative shift $|D|/f$ of`, new_str `with a median $|D|/f$ of`

**R3. chunk06 Q40, app_statmethods.tex AA32.** The symbol gloss for the GENIE knobs has no base source.
- Base: "GENIE knobs \texttt{MaRES}, \texttt{MvRES}, \texttt{MaCCQE}".
- New: "the GENIE parameters $M_{A}^{\mathrm{RES}}$, $M_{V}^{\mathrm{RES}}$ and $M_{A}^{\mathrm{CCQE}}$".
- Fix:
  - old_str: `the GENIE parameters $M_{A}^{\mathrm{RES}}$, $M_{V}^{\mathrm{RES}}$ and $M_{A}^{\mathrm{CCQE}}$`
  - new_str: `the GENIE parameters \texttt{MaRES}, \texttt{MvRES} and \texttt{MaCCQE}`
- The symbols are correct physics. Joseph may instead accept the gloss as a definition at first use. That is a judgement call, not something the base supports.

**R4. chunk07 Q1, app_statmethods.tex AA47.** Same gloss, in table tab:band-medians.
- Base: "MaRES & $0.627\%$", "MvRES & $0.362\%$", "MaCCQE & $0.336\%$".
- New: "$M_{A}^{\mathrm{RES}}$ (MaRES) & $0.627\%$", and the same for the other two.
- Fix, three edits:
  - old_str `$M_{A}^{\mathrm{RES}}$ (MaRES) & $0.627\%$`, new_str `MaRES & $0.627\%$`
  - old_str `$M_{V}^{\mathrm{RES}}$ (MvRES) & $0.362\%$`, new_str `MvRES & $0.362\%$`
  - old_str `$M_{A}^{\mathrm{CCQE}}$ (MaCCQE) & $0.336\%$`, new_str `MaCCQE & $0.336\%$`
- Apply R3 and R4 together, or neither, so that the prose and the table agree.

**R5. chunk07 Q29, app_statmethods.tex AA209.** The strength of the claim is weakened.
- Base: "This is direct evidence that $\sim1$ $\chi^{2}$-unit of the exact-split cross-check's tension is OmniFold's implicit regularization rather than a physical data--MC disagreement."
- New: "We therefore attribute $\sim1$ $\chi^{2}$-unit of the exact-split cross-check's tension to OmniFold's implicit regularization rather than to a physical data--MC disagreement."
- Fix:
  - old_str: `We therefore attribute $\sim1$ $\chi^{2}$-unit of the exact-split cross-check's tension to OmniFold's implicit regularization`
  - new_str: `This is direct evidence that $\sim1$ $\chi^{2}$-unit of the exact-split cross-check's tension is due to OmniFold's implicit regularization`
- The rest of the sentence ("rather than to a physical data--MC disagreement.") stays.

**R6. chunk07 Q35, app_statmethods_nd.tex AB8.** The requirement is weakened to a convention.
- Base: "Every N-D $\chi^{2}$ must state (i) the actual inverse ... at the point of quotation; ...".
- New: "The reporting convention for an N-D $\chi^{2}$ is to state, where it is quoted, (i) ...".
- Fix:
  - old_str: `The reporting convention for an N-D $\chi^{2}$ is to state, where it is quoted,`
  - new_str: `Every N-D $\chi^{2}$ must state, where it is quoted,`

**R7. chunk08 Q22, app_response_mismatch.tex AD7.** The status claim is added.
- Base: "A documented hadronic-response variation or a quantified assumption should justify that amplitude; the inherited factor in reconstructed $\Eavail$ is not enough on its own."
- New: "That amplitude remains to be specified from a documented hadronic-response variation or an explicit quantitative assumption; the overall factor in the reconstructed-$\Eavail$ definition, Eq.~\eqref{eq:eavail-reco-implemented}, is not by itself a sufficient basis."
- Fix:
  - old_str: `That amplitude remains to be specified from a documented hadronic-response variation or an explicit quantitative assumption;`
  - new_str: `A documented hadronic-response variation or an explicit quantitative assumption should justify that amplitude;`
- The Eq. reference is supported and is kept.

**R8. chunk08 Q27, app_response_mismatch.tex AD22.** The prohibition is overstated.
- Base: "A large bias would require a decision on the response model or an uncertainty component, and would not be absorbed silently into a non-closure error."
- New: "A large bias would require a decision on the response model or a separate uncertainty component, rather than inclusion in a non-closure error."
- Fix:
  - old_str: `a separate uncertainty component, rather than inclusion in a non-closure error.`
  - new_str: `an uncertainty component, and would not be absorbed silently into a non-closure error.`

## Note outside the classification

- sec_summary.tex dropped both `\pageref` calls (in SU0 and in the "Principal limitations" paragraph). The writers' brief says to keep every `\ref`. The ledger
  ties the removal to gap s-05, and no fact is lost, but the director may want to confirm that the gap list
  authorized it.
