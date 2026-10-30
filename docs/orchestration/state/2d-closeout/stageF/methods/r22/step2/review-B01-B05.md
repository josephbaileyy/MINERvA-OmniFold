# r22 Step 2 review: pieces B01-B05 (two directions)

Reviewer: independent, read-only. Worktree `wt-con`, diffs taken with `git diff 9d3054f9` (word diff) on
sec_execsummary.tex, sec_intro.tex, sec_experiment.tex, selection_features.tex, sec_method.tex, sec_systematics.tex,
sec_validation.tex and sec_results.tex. Ledgers B01-B05 read in full. I read every changed sentence. I checked glosses
and added facts against the base note, other note files, `values.tex`, `technote.bib`, `KNOWN_ISSUES.md` (row 84),
`docs/known-issues/VALIDATION_LEDGER.md` (VL162/VL170/VL172), the PV-2D report
(`docs/orchestration/state/2d-closeout/stageF/methods/pv2d/REPORT.md` sections 2 and 5) and `cmodel_R.json`.

Severity: **M** = it changes what a reader takes away; **L** = minor or wording-level, so fix it if cheap.

## Findings

### B01: sec_execsummary.tex, sec_intro.tex

**F1 (M)**
- **ID:** sec_execsummary.tex: "Adding $\Eavail$, $q_{3}$ and $W$ gives simultaneous unfolds in three, four and five dimensions, all reported as central values."
- **Direction:** AMBIGUOUS (a qualifier has moved away from its claim).
- **Base:** "Adding ... gives simultaneous unfolds, and the 3D, 4D and configuration-(a) five-dimensional unfolds are reported as central values."
- **Why:** The base limited "reported as central values" to the configuration-(a) 5D unfold. The new "all" covers every five-dimensional unfold. That includes the sixteen-cell configuration-(e) result, which the first paragraph reports with a covariance. The next sentence's apposition ("configuration~(a), the purity-subtracted estimator of the five-dimensional central value") only partly brings the limit back.
- **Fix:** Reword to "...gives simultaneous unfolds in three, four and five dimensions; the 3D, 4D and configuration-(a) five-dimensional unfolds are reported as central values."

**F2 (L)**
- **ID:** sec_execsummary.tex: "The principal limitations are these."
- **Direction:** WEAKENED.
- **Base:** "The body states each limitation with the result it qualifies; the principal ones are these."
- **Why:** The statement that every limitation, including the two principal ones, also sits with its result in the body is gone. Only "The others are stated with their results" survives.
- **Fix:** Restore the clause: "The body states each limitation with the result it qualifies; the principal ones are these."

**F3 (M)**
- **ID:** sec_intro.tex: "The second is an ensemble of reweighting trials with different train/test splits that controls the ML stochastic component; we include it explicitly as the training-seed variation band"
- **Direction:** AMBIGUOUS.
- **Base:** "...; we budget that component explicitly as the training-seed variation band"
- **Why:** "it" now reads most naturally as Huang et al.'s ensemble. That reading is false: we do not adopt their train/test-split ensemble. The base's "that component" was unambiguous.
- **Fix:** Reword to "we include that component explicitly, as the training-seed variation band".

**F4 (L)**
- **ID:** sec_intro.tex: "Third, OmniFold regularizes through model capacity and through an iteration count, which it shares with IBU, so comparing the two methods on the same data probes the result's method dependence"
- **Direction:** ADDED (a causal link).
- **Base:** "...which it shares with IBU. Comparing the two methods on the same data probes the result's method dependence"
- **Why:** "so" makes the method-dependence probe follow from the shared iteration-count regularization. The base set the two sentences side by side and drew no inference.
- **Fix:** Restore the full stop: "...which it shares with IBU. Comparing the two methods..."

Checked and OK in B01: the GiBUU scope ("the 8 cells its sample covers"; sec_fived16.tex: no GiBUU events above the $E_\nu$ cut). "The ten decisions, made with the carbon-only predictions" (sec_joint.tex sec:joint5d-ch). "re-unfolds" for the unified throw (sec_systematics.tex sec:uq-combine). The tier glosses (sec_fps.tex: "only tier 1 is interpreted", "Tier 2, prior-extrapolated"). $C_k$ (sec_validation.tex: $|z|\le k$). The configuration (e)/(f) descriptors (Table tab:estimators-matrix). GBDT, expanded in sec_method.tex. "point-cloud transformer (PET)" and "in progress" (app_pet_pointer.tex). The scope sentence was cut as a repetition; it prints in the intro's Scope paragraph.

### B02: sec_experiment.tex, selection_features.tex, sec_method.tex

**F5 (M, specific point)**
- **ID:** sec_experiment.tex: "combining hadron-production weights from PPFX (Package to Predict the FluX) and the neutrino--electron-scattering constraint"
- **Direction:** ADDED.
- **Base:** "combining PPFX hadron-production weights and the neutrino--electron-scattering constraint"
- **Why:** `git grep "Package to Predict"` finds the expansion only in this sentence. No repository or note source states it, so it is a gloss from memory. Under the brief's rule that counts as an addition, whether or not it is right.
- **Fix:** Restore "combining PPFX hadron-production weights and ..."; the sentence already carries \cite{MINERvA:2016iqn} for the flux.

**F6 (M, specific point)**
- **ID:** sec_experiment.tex: "These are a combined flux and central-value (CV) weight, the GENIE model-parameter (``dial'') weights, ..."
- **Direction:** ADDED / AMBIGUOUS.
- **Base:** "These are the flux-and-CV and GENIE dial weights, ..."
- **Why:** The base names MAT's FluxAndCVReweighter without saying what it combines. "a combined flux and central-value weight" asserts that one weight combines a flux weight with a separate "central-value" weight. No repository source says that. The only description found is `GetFluxAndCVWeight` in VERIFICATION.md, which does not support the "combined" reading. "CV = central value" is the note's own usage and is fine. "model-parameter (dial)" is fine too.
- **Fix:** Reword to "These are the flux-and-central-value (flux-and-CV) weight, the GENIE model-parameter (``dial'') weights, ...", and drop "combined".

**F7 (L)**
- **ID:** sec_experiment.tex: "\item The simulated signal sample is therefore complete by construction at ME~FHC (completeness $c=1$; ...)."
- **Direction:** AMBIGUOUS.
- **Base:** "\item Completeness is $c=1.000000$ by construction at ME~FHC (\num{32849103} entries; ...)."
- **Why:** The list is introduced by "Two conditions make the truth sample the complete reference". With "therefore", the second item becomes a consequence of the first, so the list now holds one condition. The six-decimal value has also become "c=1", which loses that the value was checked to $10^{-6}$. The entry count still prints earlier in the file.
- **Fix:** Drop "therefore", or make the lead-in "Two conditions hold:". Restore "$c=1.000000$".

**F8 (L)**
- **ID:** sec_method.tex: "The per-reco-bin weight is adopted at the sub-percent genuine-background scale."
- **Direction:** WEAKENED / AMBIGUOUS.
- **Base:** "At the sub-percent genuine-background scale, a per-reco-bin weight is a conservative middle ground."
- **Why:** The justification is gone. "is adopted" now reads as the analysis-wide treatment, but three sentences later the quoted 2D result uses the refined negative-weight form.
- **Fix:** Reword to "At the sub-percent genuine-background scale, the per-reco-bin weight is a conservative compromise between no subtraction and a fully unbinned one." Or simply restore the base sentence.

**F9 (L)**
- **ID:** sec_method.tex: "...; so do the background-bias and generator-sized-change studies (\S\ref{sec:val-negweight}), ... Every other quoted cross section and uncertainty, including the five-dimensional central value and the extended-fiducial value, uses the binned correction."
- **Direction:** AMBIGUOUS.
- **Base:** "(d) in the background-bias and generator-sized-change studies ..."; "including the configuration-(a) 5D central value"
- **Why:**
  - The background-bias study also has a purity arm, configuration (c) (Table tab:estimators-matrix). "so do the background-bias ... studies" now says the whole study uses the refined form.
  - "the five-dimensional central value" lost "configuration-(a)". The sentence before it names the refined sixteen-cell 5D result, so the label was what kept the two apart.
- **Fix:**
  - Reword to "so does the refined arm of the background-bias and generator-sized-change studies".
  - Restore "the configuration-(a) five-dimensional central value".

**F10 (L)**
- **ID:** sec_method.tex: "Configurations (c) and (d) are deterministic variants, with purity-based subtraction and with negative weights and a nominal-capacity refinement respectively"
- **Direction:** WEAKENED.
- **Base:** "Configuration (c), the deterministic variant with purity-based subtraction, and (d), the same variant with negative weights and a nominal-capacity refinement"
- **Why:** The base said (d) is the same variant as (c) and differs only in background treatment. "deterministic variants" in the plural loses that.
- **Fix:** Reword to "...; (d) is the same variant with negative weights and a nominal-capacity refinement".

**F11 (L)**
- **ID:** sec_method.tex:
  - "train deterministically and faster on CPU"
  - "a bin-by-bin correction would be biased"
- **Direction:** WEAKENED.
- **Base:** "far faster"; "would be badly biased"
- **Why:** Both cut words carry magnitude: they say how much faster and how badly biased. They are not only evaluative.
- **Fix:** Acceptable if the director treats them as evaluative wording. Otherwise use "substantially faster" and "strongly biased".

Checked and OK in B02:
- "pre-selected analysis ntuples (AnaTuples)" (paper_body.tex).
- The MINOS-match wording, with the flags moved to an `L:` home.
- The out-of-phase-space definition. "fakes" survives only in the intro's general literature sentence.
- The lateral/vertical gloss (now "rather than reweighting events").
- "Step-1 training within the phase space", which matches the bullet's last sentence.
- The configuration (f) refinement details, which still print in list items (e) and (f) and in the table.
- The exact-split status sentence and table row (b).
- The underflow/overflow merge.

### B03: sec_systematics.tex

**F12 (M, specific point)**
- **ID:** sec_systematics.tex: "The band sum omits the GENIE band for nonresonant charged-current single-pion production on protons (Rvp1pi), which encodes the same shift as the band for neutrons (Rvn1pi; ...)"
- **Direction:** ADDED.
- **Base:** "The band sum drops Rvp1pi, which encodes the same shift as Rvn1pi"
- **Why:** The base and the repository support only "nonresonant single-pion" (base, later in the same file: "the two nonresonant single-pion bands, Rvn1pi and Rvp1pi"). "charged-current" and "on protons / on neutrons" come from general GENIE usage; `git grep` finds no repository description. The reading is probably right, but it is an addition.
- **Fix:** Reword to "The band sum omits the nonresonant single-pion band Rvp1pi, which encodes the same shift as Rvn1pi (\S...); it holds 43 bands plus the flat normalization."

**F13 (M, specific point)**
- **ID:** sec_systematics.tex: "For two bands whose universes barely change the unfolding inputs, the neutral-current elastic axial parameter (EtaNCEL) and the neutral-current resonant normalization (NormNCRES), ..."
- **Direction:** ADDED.
- **Base:** "The two examined small-input responses, EtaNCEL and NormNCRES, ..."
- **Why:**
  - The repository supports only "NC-elastic" for EtaNCEL ("`EtaNCEL` is null ... NC-elastic") and "do not touch the CC signal". It also lists both bands among "Pure-norm bands (EtaNCEL/MaNCEL/NormDISCC/NormNCRES)".
  - "axial parameter" is general knowledge, and it is imprecise: EtaNCEL is GENIE's strange axial form-factor parameter, and the NC-elastic axial parameter a reader would think of is MaNCEL, the axial mass.
  - "neutral-current resonant normalization" for NormNCRES is consistent with "pure-norm".
- **Fix:** Reword to "the neutral-current elastic band EtaNCEL and the neutral-current resonant normalization band NormNCRES". Do not call EtaNCEL an axial parameter.

**F14 (L)**
- **ID:** sec_systematics.tex: three glosses.
  - "a resonant axial-mass universe (\texttt{MaRES\_0})"
  - "the two-particle two-hole universe \texttt{2p2h:0}"
  - "the quasielastic axial-mass universe \texttt{MaCCQE:0}"
- **Direction:** ADDED.
- **Base:** bare identifiers.
- **Why:** No note or repository source glosses these names; `git grep` finds the glosses only in this file. They are standard GENIE/MINERvA meanings and physically correct, but under the brief they are general-knowledge glosses.
- **Fix:** Joseph's call. Keep them if standard-term glosses are allowed. Otherwise cut back to the identifiers.

**F15 (M)**
- **ID:** sec_systematics.tex: "Where a pooled cell, a cell set to one by the statistical-noise gate, or an unreported cell meets another cell, the construction draws steps of more than 0.1 in a generator's reweighting ratio; the cells beside such steps keep their measured shifts."
- **Direction:** ADDED (the scope widens from some boundaries to every boundary).
- **Base:** "The cells beside a step of more than 0.1 in a generator's reweighting ratio drawn by its construction, where a pooled, noise-gated or unreported cell meets another cell, enter as measured."
- **Why:**
  - The base defines the 52 cells as those beside the steps above 0.1 that are drawn at such boundaries.
  - The new sentence asserts that a step above 0.1 is drawn wherever such a cell meets another cell. PV-2D REPORT section 5 classifies a cell as "gate" only when a neighbour's ratio differs by more than 0.1, so not every boundary carries such a step.
  - The gloss "a cell set to one by the statistical-noise gate" is supported: REPORT section 2 gives r = 1 for noisy cells, and section 5 says "coarse-pooled or noisy (r = 1) cell".
- **Fix:** Reword to "Where a pooled cell, a cell set to one by the statistical-noise gate, or an unreported cell meets another cell, the construction can draw a step of more than 0.1 in a generator's reweighting ratio; the cells beside such steps enter with their measured shifts."

**F16 (L)**
- **ID:** sec_systematics.tex: "Both programs ... require its stored set of cells to equal the published set; every run of both on the quoted covariance meets this requirement."
- **Direction:** WEAKENED.
- **Base:** "...check that the covariance's stored set of cells equals the published set; the check passes in every run of both on the quoted covariance."
- **Why:** The base says the programs verify the set; that is a guard that runs. "require" states only a precondition and no longer says the programs test it.
- **Fix:** Reword to "...check that its stored set of cells equals the published set, and the check passes in every run of both on the quoted covariance."

**F17 (L)**
- **ID:** sec_systematics.tex: two phrases.
  - "even an EtaNCEL universe, whose truth weights equal those of the central value, differs in all 205 truth-input cells"
  - "instability of the fixed-seed GBDT training"
- **Direction:** ADDED.
- **Base:**
  - "even a no-op EtaNCEL universe differs in all 205 truth-input cells"
  - "trainer instability"
- **Why:**
  - "whose truth weights equal those of the central value" spells out "no-op" more strongly than the sources do. The sources say "null (√tr ~1e-51)" for May and "below the power floor (3.0e-7)" for July, so the weights are not exactly equal.
  - "fixed-seed" is an inference from the context, which is plausible, not a stated fact.
- **Fix:**
  - Reword to "an EtaNCEL universe that leaves the event weights essentially unchanged".
  - Use "instability of the GBDT training".

**F18 (L)**
- **ID:** sec_systematics.tex: "Figure~\ref{fig:uqbands} shows the fractional uncertainty grouped as in Figs.~6--7 of Ref.~\cite{MINERvA:2021owq}"
- **Direction:** ADDED (a citation).
- **Base:** "grouped fractional-uncertainty projections in the published Fig.~6/7 style"
- **Why:** This adds a \cite. The referent is correct, since "the published" analysis is MINERvA:2021owq throughout the note, but the writer brief says "add no citation".
- **Fix:** Joseph or the director decides. It is accurate, so either keep it or use "as in Figs.~6--7 of the published measurement".

Checked and OK in B03:
- "205 reported cells" for $C_{\mathrm{model}}$. `cmodel_R.json` has `per_cell.cells` of length 205 and `cell_rel_sigma.C_model.median` = 0.03707.
- "Ranked by per-bin median fractional standard deviation" (values.tex: `bands.Flux.median_pct`; app_history.tex: "Per-bin medians").
- "MINOS muon-match efficiency" (app_statmethods.tex).
- $C_Z$ as the name of the configuration-(a) five-axis covariance (app_statmethods_nd.tex; sec_5d.tex eq. zinflation).
- The "Bashyal joint block" rewording.
- The lateral-band definition, cut to the cross-reference; it prints later in the same file.
- The cuts of the repeated sentences. Each one's fact still prints in the same file, which I confirmed for "matched in estimator and seed", "valid only where ... linearly", "1.4% normalization" and "which period is correct".
- "Comparison with the earlier 2D budget", which sits inside sec:uq-2d-scope, so the new pointer in sec:uq-2d-construction is right.

### B04: sec_validation.tex

**F19 (M, specific point)**
- **ID:** sec_validation.tex: "The test scored the \emph{completeness-divided band}, ... The \emph{undivided band} is that band rebuilt without the division, since superseded."
- **Direction:** AMBIGUOUS (terminology across files).
- **Base:** "...the 2D statistical band quoted when it ran ... That band is an earlier one"; "the rebuilt (since superseded) band"
- **Why:**
  - Accuracy: the names are accurate. KNOWN_ISSUES 84 says the VL162 replicas "divide by" the bootstrapped completeness P/T and the central value (c ≡ 1) does not. The VL170 fix computes replica completeness from un-resampled truth, so replica c equals the central value's, which in effect means no division. VL172 records VL170 adopted, and VL162 superseded. The base text itself says "rebuilt without this term".
  - Consistency: the other files still use the old terms. sec_execsummary.tex has "scored two earlier statistical bands, of which the first-built undercovers" (a protected sentence). app_statmethods.tex:636 has "the first-built $\mathbf{C}^{\stat}$ ... the band was rebuilt ... the rebuilt band". sec_validation.tex now uses neither "first-built" nor "rebuilt", so nothing links the summary's term to the body's.
- **Fix:** Add the old terms at the two definitions in sec_validation.tex (a few words):
  - "...the \emph{completeness-divided band}, the first-built statistical band, quoted when the test ran..."
  - "The \emph{undivided band} is the rebuilt band, without the division, since superseded."

**F20 (L)**
- **ID:** sec_validation.tex, table tab:validation (Fixed-truth coverage row): "scored band undercovers in its tails (\S\ref{sec:coverage})"
- **Direction:** MOVED-AWAY.
- **Base:** "earlier band fails"
- **Why:** "earlier" told a reader of the table that the result is not for the quoted statistical block. "scored band" does not say that, and the distinction now appears only in sec:coverage.
- **Fix:** Reword to "earlier (completeness-divided) band undercovers in its tails".

**F21 (L-M)**
- **ID:** sec_validation.tex: two sentences.
  - "These closure tests probe only the listed deformations and amplitudes; no non-closure uncertainty is assigned from them."
  - "The five-dimensional estimator, including its background subtraction, is tested in \S\ref{sec:val-fiveaxis}."
- **Direction:** WEAKENED (a positive claim changed).
- **Base:**
  - "These closure tests validate the estimator; ..."
  - "...is validated in ..."
- **Why:** The writer brief says no claim changes. Both base claims of validation are now weaker. The change is in the conservative direction, and the scope ("listed deformations and amplitudes") is supported by the table cell "passes depend on deformation and amplitude". It is still a change to what the note claims.
- **Fix:** Joseph decides whether to adopt the narrower claim. If not, reword to "These closure tests validate the estimator for the listed deformations and amplitudes; ..." and restore "is validated in".

**F22 (L)**
- **ID:** sec_validation.tex: "...these figures diagnose standardized pulls and Gaussianity only and are not a coverage test of the bootstrap band; the 2D coverage statement is the fixed-truth test of \S\ref{sec:coverage}."
- **Direction:** LOST.
- **Base:** "...they do not certify the bootstrap band, and no coverage number is quoted from this ensemble."
- **Why:** The explicit statement that no coverage number is quoted from this ensemble is gone. Ledger B04-27 lists it as a kept fact but gives it no probe. "not a coverage test" covers it only partly: the paragraph still prints a 68.4% within-one-sigma fraction that a reader could quote as a coverage figure.
- **Fix:** Restore it: "...; no coverage number is quoted from this ensemble, and the 2D coverage statement is the fixed-truth test of \S\ref{sec:coverage}."

**F23 (L)**
- **ID:** sec_validation.tex: "The AUC drops from $\approx0.535$ before unfolding to $\approx0.501$ after, close to the chance value."
- **Direction:** WEAKENED.
- **Base:** "..., indicating removal of the reconstructed data\,$\leftrightarrow$\,MC mismatch."
- **Why:** The base's interpretation, what the drop shows, is gone. This is the conservative direction, and "descriptive" still follows.
- **Fix:** Joseph's call. If restored: "close to the chance value, so the reconstructed data--MC mismatch the classifier can detect is removed".

**F24 (L)**
- **ID:** sec_validation.tex: "With the current inputs, validated total uncertainties for all 205 bins, the integral and the projections therefore cannot be obtained."
- **Direction:** LOST (a disclosure was folded into fronting).
- **Base:** "... cannot be obtained from the current inputs. ... This is a limit of the available inputs, not a general impossibility result for 2D unfolding."
- **Why:** The explicit denial that this is an impossibility result is cut. The fronted "With the current inputs" carries most of it, so this is a borderline case.
- **Fix:** Optional. Append ", a limit of the inputs rather than of 2D unfolding."

**F25 (L)**
- **ID:** sec_validation.tex: "It resamples the simulation with the per-event Poisson(1) bootstrap of the statistical band and unfolds with that band's estimator, LightGBM with five iterations at a fixed training seed (\S\ref{sec:method-config})."
- **Direction:** WEAKENED.
- **Base:** "...(LightGBM, five iterations, fixed training seed): the learner of the quoted central value, at a different seed"
- **Why:** The statement that the tested learner is the quoted central value's learner is dropped. Only "not at the quoted central value's seed~42" survives, in Scope. That fact is what makes the test relevant to the quoted result.
- **Fix:** Append ", the learner of the quoted central value at a different seed".

Checked and OK in B04: the gate-bound phrases are byte-identical. Also OK:
- The interim result in prose; "failure by undercoverage" is kept.
- The post hoc and amendment disclosures. "by amendment" is now an `R:` home, and "added after the pilot" stays.
- "independent reimplementation of the scoring" (g-09 home).
- The heading "Comparison of injected-bump and generator-shaped closure tests". The bullets still say "closing injections" and "generator-shaped failures".
- The Scope prose.
- "denominator $N_{\text{toy}}-1$".
- "ME1A".

### B05: sec_results.tex

I found no substantive change of meaning. All the relabelings (ours/paper to this/published; "distance" to "$\chi^2$ per bin", which matches the table row "Indicative $\chi^{2}$/bin"; the TotalCov row; arXiv:2106.16210 to \cite{MINERvA:2021owq}, eprint confirmed in technote.bib) are supported. The slice-figure statement that the published data do not enter now sits in both captions. The caption sentence "Neither map has the published data as its denominator" is cut, but the caption's opening ("ratios to MINERvA Tune~v1") carries it.

**F26 (L)**
- **ID:** sec_results.tex: "\subsection{Eigenmode analysis of the published-covariance $\chi^{2}=\chiPaper$}"
- **Direction:** AMBIGUOUS (naming across files).
- **Base:** "\subsection{Anatomy of the $\chi^{2}=\chiPaper$ tension}"
- **Why:** The body no longer calls the $\chi^2=\chiPaper$ excess a "tension". The appendix it points to keeps "Anatomy of the paper-covariance tension" (app_statmethods.tex:508) and says "The tension is neither ...", so the two headings no longer match.
- **Fix:** None needed for meaning. Optionally keep the word: "Eigenmode analysis of the published-covariance tension, $\chi^{2}=\chiPaper$".

## Rulings on the brief's specific points in my range

- **B02, PPFX "Package to Predict the FluX":** Fix (F5). The expansion has no repository source; it was written from memory. Revert to "PPFX hadron-production weights"; the sentence keeps \cite{MINERvA:2016iqn}.
- **B02, "a combined flux and central-value (CV) weight":** Fix (F6). Expanding "CV" is fine. "combined" asserts a structure of MAT's FluxAndCVReweighter that nothing in the repository states. Use "the flux-and-central-value (flux-and-CV) weight".
- **B03, EtaNCEL gloss:** Fix (F13). Only "neutral-current elastic" is supported (repository notes). "axial parameter" is general knowledge and imprecise, since EtaNCEL is the strange axial form-factor η and not the NC-elastic axial mass, MaNCEL.
- **B03, Rvp1pi/Rvn1pi gloss:** Fix (F12). "nonresonant single-pion" is base-supported. "charged-current" and "on protons/neutrons" are general GENIE usage, probably correct but unsourced. Trim them, or have Joseph approve them as standard-term glosses. F14 (MaRES, MaCCQE, 2p2h) is the same case.
- **B03, "205 reported cells" for $C_{\mathrm{model}}$:** OK. `cmodel_R.json` `per_cell.cells` has 205 entries, and the median (0.03707) is the `cell_rel_sigma` over them.
- **B04, "completeness-divided band" and "undivided band":**
  - Accurate: OK. KI-84: the VL162 replicas divide by a bootstrapped P/T. VL170 computes replica completeness from un-resampled truth, so c equals the central value's c (≡ 1). VL172 adopts VL170, and VL162 is superseded.
  - Consistent: not as written. sec_execsummary.tex ("first-built", protected) and app_statmethods.tex:636 ("first-built ... rebuilt") are not linked to the new names. Fix F19: add "the first-built" and "the rebuilt" at the two definitions. F20 is the related table cell.
- **B05, 0.66 and 1.42 labelled $\chi^2$/ndf:** OK. app_statmethods.tex (sec:tension) says "the $73$ best-determined directions ($\lambda_{k}/\lambda_{\max}>10^{-4}$) give $\chi^{2}/\mathrm{ndf}=1.42$" for the exact-split cross-check, and app_statmethods.tex:511 says the LightGBM decomposition is "from the same code". "9.6% of the total $\chi^2$" matches the appendix's "carry only 3% of the $\chi^{2}$".

## Count by direction

- LOST: 2 (F22, F24)
- WEAKENED: 8 (F2, F8, F10, F11, F16, F21, F23, F25)
- MOVED-AWAY: 1 (F20)
- AMBIGUOUS: 6 (F1, F3, F7, F9, F19, F26)
- ADDED: 9 (F4, F5, F6, F12, F13, F14, F15, F17, F18)
- Total: 26. Of these, 8 are rated M (F1, F3, F5, F6, F12, F13, F15, F19) and 1 is rated L-M (F21); the other 17 are L.
