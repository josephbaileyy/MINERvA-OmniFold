# r22 Step 2 review: pieces B11-B15 (two directions)

Reviewer: independent, read-only. Worktree `WT=.../796e7ecc-.../scratchpad/wt-con`, base `9d3054f9`, diff read with
`git -C $WT diff [--word-diff=plain] 9d3054f9 -- docs/analysis-note/<file>`. Ledgers `ledger-B11.md` .. `ledger-B15.md`.

Files reviewed: sec_fps.tex, sec_summary.tex (B11); app_guide.tex, app_statmethods.tex (B12); app_statmethods_nd.tex,
app_negweight.tex (B13); app_response_mismatch.tex, app_landscape.tex, app_pet_pointer.tex (B14); app_release.tex,
app_codebase.tex (B15). **app_pet_pointer.tex has no diff against the base** (nothing to review).

Sources opened to check content: `VALIDATION_LEDGER.md` lines 1615-1645 and 1705-1711 (FPS battery, 3-prior envelope,
coverage toys, hidden-variable closure); `docs/publication/release/RC7-README.md` (contents, verifier, jitters);
`nd-unfolding/fps_acceptance.py`, `nd-unfolding/pet/fullevent_fps_dataloader.py:71-72` and
`HANDOFF_fps_step3/stage2_anchor_check.py:7-8` (catch bins); `nd-unfolding/RESPONSE_MISMATCH_CLOSURE.md` and
`unfold_nd_omnifold_unbinned.py:675` (amplitude default `None`); `app_history.tex:145`; `app_provenance.tex:101`;
`sec_5d.tex:212-216, 248, 302-312`; `sec_method.tex:46-48`; `sec_systematics.tex:4,12,50,99`; `sec_experiment.tex:10`.

Severity is my judgement: **H** (a reader is likely to take a false or unsupported statement away), **M** (a real
change of meaning or a broken pointer), **L** (wording that should be tightened but is unlikely to mislead).

---

## Findings

### F1 (M-H). app_statmethods.tex, sec:invert: "The cutoff is $\tau = 10^{-15}\,\sigma_{\max}$."
- **direction:** LOST (and a records entry is now false)
- **base:** "The comparison calls \texttt{np.linalg.pinv} at its default, NumPy's documented cutoff $\tau = \texttt{rcond}\cdot\sigma_{\max}$ with $\texttt{rcond}=10^{-15}$; this is not the $n\,\sigma_{\max}\varepsilon_{\text{machine}}$ convention of \texttt{np.linalg.lstsq} and MATLAB."
- **new:** "The cutoff is $\tau = 10^{-15}\,\sigma_{\max}$."
- **why:** The cut of the library names was authorized (B12-g-03, home app_history.tex:145). But the statement that the cutoff is *not* the looser $n\,\sigma_{\max}\varepsilon$ convention was cut with them, and it was a correction of an earlier wrong formula. The record that is meant to hold it, app_history.tex:145, says: "The body keeps the operative cutoff ($\texttt{rcond}=10^{-15}$) **and the statement that it is not that convention**." That sentence of the records document is now false, and the note no longer says which convention it is not.
- **fix:** reword, keeping it library-free: "The cutoff is $\tau = 10^{-15}\,\sigma_{\max}$, not the looser $n\,\sigma_{\max}\varepsilon_{\text{machine}}$ convention." This keeps the rater's request (no software names) and keeps app_history.tex:145 true. (If the clause stays cut, the integrator must amend app_history.tex:145.)

### F2 (M). app_codebase.tex, Code identifiers: "\texttt{extract\_cross\_section\_2d} in the 2D driver"
- **direction:** AMBIGUOUS (a pointer lost its target)
- **base:** the Driver item read "per-analysis orchestration in \texttt{2d-unfolding/unfold\_2d\_omnifold\_unbinned.py} and its $N$-dimensional generalization \texttt{nd-unfolding/unfold\_nd\_omnifold\_unbinned.py}."
- **new:** "per-analysis orchestration, by a two-dimensional driver and its $N$-dimensional generalization."
- **why:** The paths' move to the ledger homes was authorized (B15-g-03). But the unchanged list "Code identifiers cited in the note", three paragraphs below, still says "\texttt{extract\_cross\_section\_2d} in the 2D driver". Its purpose is to locate code, and no file in the note now names the 2D driver, so that identifier cannot be found from the note. (The N-D generalization is still located, as `nd-unfolding/xsec_nd.py`.) sec_method.tex:46 also still sends the reader to App. codebase for "code paths".
- **fix:** put the 2D driver path in the code-identifier list, the note's locator list, where it belongs: "\texttt{extract\_cross\_section\_2d} in the 2D driver, \repopath{2d-unfolding/unfold\_2d\_omnifold\_unbinned.py}". The Driver item can stay functional.

### F3 (M). app_negweight.tex, Scope of the numbers: "this appendix neither establishes negative-weight injection as a production method nor changes a default."
- **direction:** AMBIGUOUS
- **base:** "Here negative-weight injection is an equivalence study and the natural extended-fiducial treatment; this appendix establishes no supported production path and changes no default."
- **new:** "Negative-weight injection is studied here for its equivalence to binned purity and as the extended-fiducial treatment; this appendix neither establishes negative-weight injection as a production method nor changes a default."
- **why:** The new sentence names the method as the thing not established "as a production method". But the quoted 2D result *is* produced with refined negative-weight subtraction, configuration (f) (same file: "The 2D result quoted in this note uses the refined treatment, configuration~(f)"; sec_method.tex:46). The extended-fiducial analysis also designates negative-weight injection with Stay-Positive refinement for publication (same file). A reader can take the new sentence to deny both. The base's vaguer "no supported production path" did not name the method.
- **fix:** reword so that the scope is what the appendix does, not the method's status: "...; this appendix does not itself select the production method of any result (\S\ref{sec:method-algo} states which each uses) and changes no default." Or restore the base clause.

### F4 (M-L). app_release.tex, opening: "...with the identities fixed so far and what each part reproduces."
- **direction:** WEAKENED
- **base:** "It states which identities are fixed and what each part does and does not reproduce."
- **new:** "This appendix describes RC7, the existing local replay package, and specifies the broader event-level and covariance release, with the identities fixed so far and what each part reproduces."
- **why:** The appendix's title is "Result package and reproduction limits". Its scope sentence no longer announces the limits ("does not reproduce"), which take up most of §app:release-scope. B15-s-04 asked for the qualifications to be consolidated, not dropped. "So far" is a small addition. It is harmless but not in the base.
- **fix:** restore: "...with the identities fixed so far and what each part does and does not reproduce."

### F5 (M-L). sec_fps.tex, Closure item: "The per-cell relative deviation of the recovered cross section from the bump-reweighted $(\pT,\pPar)$ truth has a median of \SI{0.17}{\percent} ... and a median of \SI{0.77}{\percent} (maximum \SI{4.05}{\percent}) in the extension"
- **direction:** AMBIGUOUS
- **base:** "The recovered cross section reproduces the bump-reweighted $(\pT,\pPar)$ truth to median \SI{0.17}{\percent} (90th percentile \SI{0.65}{\percent}) ... (max \SI{4.05}{\percent})"
- **why:** The source (VALIDATION_LEDGER.md:1708-1711) gives "median |dev| 0.17%", "max **4.05%**", "max|dev| 4.05%". These are absolute deviations. The new text names a *signed* "relative deviation", whose median could be near zero for an unbiased closure and whose "maximum" differs from max |dev|. The base "reproduces ... to median" carried the magnitude reading. Note that the same writer added "absolute" to the published-region check two items earlier (F6), so the two adjacent statistics are now named inconsistently.
- **fix:** "The per-cell absolute relative deviation of the recovered cross section ..."

### F6 (L). sec_fps.tex, Published-region check: "median absolute deviation \SI{\fpsAnchor}{\percent} over all 185 reported cells"
- **direction:** AMBIGUOUS (the specific point B11; see the ruling below)
- **base:** "median deviation \SI{\fpsAnchor}{\percent} across all 185 reported cells"
- **why:** "Absolute" is supported: VALIDATION_LEDGER.md:1623-1624 reads "median |Δ| 0.57% (185 cells)". But "median absolute deviation" is the name of a standard robust spread statistic, median |x - median(x)|, which this is not. Here it is the median over cells of |ratio - 1|.
- **fix:** "median absolute relative deviation from the control" (or "median $|\Delta|$").

### F7 (M-L). app_statmethods_nd.tex: "A sum of deterministic rank-one band terms and statistical and ML sample blocks, such as the covariance above, has no single debiasing factor."
- **direction:** AMBIGUOUS (an added antecedent can point to the wrong object)
- **base:** "A sum of about 45 deterministic rank-one MAT outer products plus statistical and ML blocks has no single debiasing factor."
- **why:** The nearest covariance "above" is the one in the preceding paragraph, "the superseded unified-throw 5D covariance" ($N=160$, $p=100$). That paragraph uses it as the case to which the debiasing factor $(N-p-2)/N$ *does* apply. It is a throw ensemble, not a sum of rank-one band terms. "Such as the covariance above" therefore reads as saying the throw covariance has no debiasing factor, contradicting the paragraph before it. The intended referent is the earlier 5D covariance of the standard production chain, two paragraphs up.
- **fix:** "..., such as the earlier 5D covariance of the standard production chain, has no single debiasing factor."

### F8 (L). app_statmethods_nd.tex: "The covariance is a sum of about 45 rank-one outer products, one for each two-endpoint systematic band, ..."
- **direction:** LOST (minor), and a ledger misstatement
- **base:** "About ${\sim}45$ two-endpoint MAT bands ..." and "about 45 deterministic rank-one MAT outer products"
- **why:** "MAT" no longer prints anywhere in app_statmethods_nd.tex: it printed twice in the base and now prints 0 times (`grep -c`). Ledger row B13-5 says "'about 45' and 'MAT' print once, in AB6's successor"; its probe checks only "about 45". The bands' identity as MAT's standard error bands is stated for 2D in sec_systematics.tex:12, so this is minor. But the ledger's claim is false.
- **fix:** "about 45 rank-one outer products, one for each two-endpoint MAT systematic band" (MAT is defined in sec_experiment.tex:10). Correct the ledger row in any case.

### F9 (L). app_statmethods_nd.tex: "The appropriate treatment depends on the covariance and inverse actually used, and is determined from the quantities recorded under item (v)."
- **direction:** AMBIGUOUS
- **base:** "The treatment must be chosen for the covariance and inverse actually used, from the quantities that declaration (v) records."
- **why:** The base was a requirement on a future analyst; the paragraph opens "No generic correction is prescribed". "Is determined from" reads as a description of something done, which suggests that some treatment has been determined and applied.
- **fix:** "..., and is to be determined from the quantities recorded under item (v)."

### F10 (M-L). app_negweight.tex: "It comes from the extended-fiducial ME~FHC battery of 2026-06-10, the set of unfolds run on that date."
- **direction:** ADDED (a gloss not supported by the source, and over-broad; specific point B13)
- **base:** "It comes from the extended-fiducial ME~FHC battery of 2026-06-10."
- **why:** The record (app_provenance.tex:101) identifies the battery as "FPS ME~FHC battery of 2026-06-10, scheduler job 54244120". The validation ledger agrees: VALIDATION_LEDGER.md:1621, "full-statistics campaign stage". At least one other FPS job ran that date and is not the battery: VALIDATION_LEDGER.md:1636, "FPS 3-prior envelope (2026-06-10, job 54244178)". "The set of unfolds run on that date" is a gloss from the label, and it is wider than the object. The gloss also comes after first use: sec_fps.tex (out of scope, unchanged) prints "the battery of 2026-06-10" first, unglossed.
- **fix:** "It comes from the full-statistics extended-fiducial ME~FHC production of 2026-06-10, a single scheduler job (the battery; Ref.~\cite{NoteRecords2026}, \recentry{fps-battery})". Alternatively drop the gloss and rely on the record entry already cited in the next sentence.

### F11 (L). app_negweight.tex, sec:negweight-uq: "Agreement is at the level predicted by the $(D-B)/S$ identity: the two covariances differ by one to two percent."
- **direction:** AMBIGUOUS (from a merge)
- **base:** "Agreement is at the level predicted by the $(D-B)/S$ identity." In the separate Measured-size paragraph: "the two covariances differ by one to two percent."
- **why:** The colon makes "one to two percent" the *content* of the identity's prediction. The same paragraph says the residuals "are bootstrap and classifier-seed sampling noise, with no method bias". In other words, the identity predicts equality up to noise, not a 1-2 % difference.
- **fix:** use a full stop: "Agreement is at the level predicted by the $(D-B)/S$ identity. The two covariances differ by one to two percent."

### F12 (L). app_negweight.tex, standard N-D chain: "The standard job script passes the driver's background-mode option (\texttt{-{}-bkg-mode}) explicitly from that configuration, and the value is written into the record ..., so the background treatment of each new component can be read from the component itself."
- **direction:** LOST (minor disclosure)
- **base:** "... explicitly from that configuration rather than inheriting the driver's default, and the value is written ... as it is produced. This changes how the treatment is documented, not the physics: the background treatment of a future component can be read from the component itself rather than inferred from the absence of an option."
- **why:** Two qualifiers went. First, the change of job script did not change any result ("not the physics"). Second, earlier components' treatment had to be inferred from the *absence* of the option, which is why the July unfolds needed "elimination". The ledger (B13-23) points to the heading for "purity" and to the record for the driver default. The no-physics-change statement has no probe at any home.
- **fix:** restore one short clause: "...; this changes how the treatment is recorded, not the treatment itself."

### F13 (L). app_codebase.tex, Driver: "subtracts the background by the method an option selects, the purity weight by default (\S\ref{sec:method-algo}) or negative-weight injection (App.~\ref{app:negweight})"
- **direction:** ADDED, incomplete (specific point B15)
- **base:** "applies the background subtraction its background-mode option selects (by default the purity weight; \S\ref{sec:method-algo})"
- **why:** Naming the alternative is supported by the code comment beside it (`--bkg-mode {purity, negweight, negweight-refined}`) and by App. negweight. But the option has *three* modes, and the quoted 2D result uses the refined one (the same comment, and sec_method.tex:46). "Purity ... or negative-weight injection" reads as two methods. It does not show that the production 2D method is a separate, refined mode.
- **fix:** "the purity weight by default (\S\ref{sec:method-algo}), or negative-weight injection with or without the Stay-Positive refinement (App.~\ref{app:negweight})".

### F14 (L). app_statmethods.tex, anatomy: "A scan of the pseudo-inverse cutoff gives no indication of a numerical artifact"
- **direction:** WEAKENED
- **base:** "A \texttt{pinv}-rcond scan excludes a numerical artifact"
- **why:** B12-s-07 asked for measured language, so this is within the brief. But the claim is now weaker than the base made it ("excludes" became "no indication"), and the supporting numbers (73 directions: 1.42; 139: 2.79; no late jump) are unchanged. Not misleading. Flagged because the review rule is to flag any weakening.
- **fix:** optional: "A scan of the pseudo-inverse cutoff rules out a numerical artifact".

### F15 (L). app_statmethods.tex, Ruterbories 2021 Sec. V: "It reports a flux uncertainty below $4\%$ across most of phase space with the $\nu$-$e$-scattering constraint"
- **direction:** WEAKENED
- **base:** "flux below $4\%$ across most of phase space thanks to the $\nu$-$e$-scattering constraint"
- **why:** "Thanks to" attributed the result to the constraint; "with" only places them together. This is minor.
- **fix:** "...below $4\%$ across most of phase space as a result of the $\nu$-$e$-scattering constraint".

### F16 (L). app_response_mismatch.tex: "The implementation runs only as a pseudo-data closure on the five observables and cannot be combined with truth-reweight injection or bootstrapping."
- **direction:** AMBIGUOUS
- **base:** "The implementation runs only as a closure on pseudo-data and only on the five observables, and it cannot be combined ..."
- **why:** The second "only" carried a separate restriction, enforced in code (`unfold_nd_omnifold_unbinned.py:696`, which requires exactly `--axes eavail,q3,W`). In the new sentence "on the five observables" can be read as describing the closure, not as restricting it.
- **fix:** "The implementation runs only as a pseudo-data closure and only on the five observables, and cannot be combined ..."

### F17 (L). sec_summary.tex, Outlook: "A flux and muon-energy-scale posterior derived with MAT, independently of the published analysis, ..."
- **direction:** AMBIGUOUS (inconsistent naming across files)
- **base:** "derived from MAT-MINERvA, independent of the published analysis, would let ... be derived"
- **why:** "MAT-MINERvA", the MINERvA-specific layer of the toolkit, became "MAT". app_statmethods.tex §sec:rank, unchanged, still says the same posterior comes "from MAT-MINERvA", so the note now names the same proposal two ways. "Would determine $\rho$" in place of "would let $\rho$ be derived" is equivalent.
- **fix:** use one name in both places. "With MAT" is fine if app_statmethods.tex is aligned. Otherwise write "with the MINERvA-specific MAT tools".

### F18 (L). app_release.tex, worked example step 6: "$C_{EW}$ is \emph{not} inverted without a declared regularization: ... The estimator-seed sensitivity, the first measurement of \S\ref{sec:eavailw-adopted}, is why no significance is computed from it."
- **direction:** AMBIGUOUS
- **base:** "Do \emph{not} invert $C_{EW}$ without a declared regularization: ..., and \S\ref{sec:eavailw-adopted}'s first measurement is the reason no significance is computed from it at all."
- **why:** (a) The instruction to a package user ("Do not invert") became a description ("is not inverted"). That reads as a statement about this note's practice, and it loses the instruction that the worked example exists to give. The neighbouring protected sentence "Do not check the sign of $\lambda_{\min}$" stays imperative. (b) The named reason is supported: sec_5d.tex:306, "Estimator-seed sensitivity exceeds its limit." But the reason is that it *exceeds its limit*, not the sensitivity as such.
- **fix:** "$C_{EW}$ should not be inverted without a declared regularization: ... The estimator-seed sensitivity, which exceeds its limit (the first measurement of \S\ref{sec:eavailw-adopted}), is why no significance is computed from it."

### F19 (L). app_statmethods.tex, Standing assumptions (list end)
- **direction:** MOVED-AWAY
- **base:** the items "\textbf{Band independence in $\mathbf{C}^{\syst}$.} Different physics sources are taken as uncorrelated; the one known exception, the Bashyal flux$\leftrightarrow$muon-E joint block, is treated in \S\ref{sec:rank}." and "\textbf{Combined-$\chi^{2}$ double-count.} ... it is no independent ours-only test (\S\ref{sec:rank})."
- **new:** both items cut (ledger B12-34, B12-35: CUT-NOTE).
- **why:** Both facts still print (§universes, lines 146 and 157; §rank, line 496; limit (i) of §chisq). But the list is titled "Standing assumptions", and band independence is a standing assumption: line 157 calls it "a modeling assumption with one known correlated exception". The summary list of assumptions is now incomplete. The clause "no independent test with our covariance alone" is only implied elsewhere ("what OmniFold's uncertainty estimate adds on top of the published $V$").
- **fix:** restore a one-line item: "Bands in $\mathbf{C}^{\syst}$ are assumed independent, with one known exception (\S\ref{sec:rank})." The double-count item may stay cut.

---

## Checked and found faithful (no finding)

- **sec_fps.tex:**
  - "low-acceptance region, $\epsilon<2\%$" for "dead region" fits VL:1630, "eff<2% ... dead-cell share 27.7%". "Zero-acceptance cells" is kept where the base had it.
  - "Overflow bins" for "catch bins" fits the code: the bins too wide for a linear axis are the $\pT\in[4.5,30]$ column and the $\pPar\in[60,120]$ row. The low-$\pPar$ catch rows are narrow.
  - The control definition sentence, "agrees at the printed precision with", "does not reproduce", "varies by $\pm1.5\%$ across three priors" (VL:1638-1640) and the half-spread definition are all faithful.
  - The merged containment scope sentence keeps the statistical-only and not-a-full-band limits.
  - "None is used to certify a covariance" is faithful.
  - The cut restatement of the unchanged MINOS selection prints in the opening paragraph.
- **sec_summary.tex:** the executive-summary pointer is merged without losing "lists the principal limitations" (it prints in the Principal-limitations paragraph). The page references are removed.
- **app_guide.tex:** the prose conversion keeps every appendix pointer and the protected sentence. "Is not needed to follow the physics results" is faithful. The new label-table row for the four calls is faithful to the cut prose.
- **app_statmethods.tex:**
  - "The central value's seed, 42" is supported (sec_method.tex:46, sec_systematics.tex:4).
  - The seed triplet prints in sec_systematics.tex:99.
  - "Cholesky factorization and ridge jitter" matches the §invert heading.
  - The physics band names match the base identifiers.
  - "Conventional CV-centered pair formula" is accurate for $\tfrac12(\Delta_+\Delta_+^\top+\Delta_-\Delta_-^\top)$.
  - The $\chi^2_{\ours}$ renaming and the Ruterbories digest are faithful (apart from F15).
  - "Attributable to the estimator" and "We therefore attribute" keep the claim as an attribution.
  - "Summary"/"Sources of the 2D comparison numbers" and "This distance is descriptive ... (\S\ref{sec:chisq})" are faithful. The reason prints in limit (i).
  - Cutting the sentence that repeated the shared-systematics limit is acceptable: limit (i) is 20 lines earlier in the same subsection.
- **app_statmethods_nd.tex:**
  - The $C_Z$ gloss matches app_guide.tex.
  - "ndf is the retained rank" and the reporting convention keep items (i)-(v) intact.
  - The interval-diagnostic split is faithful. "Pseudo-experiment" for "development experiment" agrees with sec_5d.tex:179 ("nominal truth", contrasted with the real-data procedure).
  - The pull-fraction and split-sample sentences are faithful.
- **app_negweight.tex:**
  - The operands of both ratios and the LightGBM and histogram-backend attributions moved to the right comparisons.
  - "Natural" prints in the introduction.
  - The consistency, cost and comparison-scale rewordings are faithful.
  - "Least computationally expensive" is faithful.
  - The 5D limit ("does not show ... irrelevant in five dimensions") still precedes the LightGBM clause.
  - The subsection retitle fits its content (the Displacement paragraph opens it).
- **app_response_mismatch.tex:**
  - The status moved from the title into the opening paragraph. "First stage implemented but not yet run" is more precise than the base title, and the follow-up is unimplemented.
  - "Remains to be specified" is supported: the code default is `None`, and RESPONSE_MISMATCH_CLOSURE.md:65-72 says the amplitude must be frozen with a stated basis.
  - "Overall factor" is correct: the factor 1.17 multiplies the whole expression in sec_3d's equation.
  - "A separate uncertainty component, rather than inclusion in a non-closure error" is faithful in substance.
- **app_landscape.tex:** the single definition of dimensionality, "main" for "headline", and "has the dimensionality of our three-dimensional result" (the same three variables) are faithful. The cut "Counting measured observables ..." is covered by the definition.
- **app_release.tex:** every changed claim about the package is true of the package (see the B15 ruling).

---

## Rulings on the specific points in range (B11, B13, B15)

**B11: "absolute" added to "median deviation" (VALIDATION_LEDGER.md:1623-1638).** OK in substance. The ledger reads "median |Δ| 0.57% (185 cells)", so the deviation is absolute. Recommended reword, to avoid confusion with the MAD statistic: "median absolute relative deviation from the control" (F6). The same reasoning requires "absolute" in the hidden-variable closure sentence, whose source is "median |dev|" (VL:1708). That sentence needs a fix (F5).

**B13: the gloss for "battery" ("the set of unfolds run on that date").** Fix. The gloss is not in any source, and it is wider than the object. The record (app_provenance.tex:101) defines the battery as scheduler job 54244120, and another FPS job (54244178, the three-prior envelope) ran the same date. Use "the full-statistics extended-fiducial ME~FHC production of 2026-06-10, a single scheduler job" or drop the gloss (F10). Note also that "battery" first prints unglossed in sec_fps.tex (protected sentence B11-g-01).

**B15: the second subtraction method is now named "negative-weight injection".** Partly OK. It is supported by the option list in the code comment and by App. negweight, but it is incomplete. The option has two negative-weight modes, plain and refined, and the quoted 2D result uses the refined mode. Fix: "or negative-weight injection with or without the Stay-Positive refinement" (F13). See also F3: the same naming in app_negweight.tex's scope sentence now reads as denying that the method is used in production.

**B15: release item 10 now names "the four measurements".** OK. It is supported by sec_5d.tex:302, "Four measurements limit what the covariance supports", under §sec:eavailw-adopted. "Stored with it in the released package, not only in this note" keeps the base's requirement. Item 10 is still a requirement under "must contain every item below", with no $\checkmark$.

**B15: worked-example step 6 now names "the estimator-seed sensitivity".** OK. It is the first item of the list at sec_5d.tex:306, "Estimator-seed sensitivity exceeds its limit". Recommended: say that it *exceeds its limit*, and restore the step's instruction to the reader ("should not be inverted") (F18).

**B15: every claim about the package in app_release.tex stays true.** Checked against RC7-README.md (:55-115) and the base:
- verifier scope: unchanged;
- "every number quoted from a figure": README item 4, "the numbers it quotes from Figs. 1-3";
- 16 MB contents and the reading-(a) results: unchanged;
- figure regeneration: unchanged;
- the exact-split curve and the separately drawn current figure: unchanged;
- contents list: same five objects;
- verifier run conditions: README "fresh environment ... Run from this directory";
- tolerances: README "relative 1e-12";
- Figs. 1-3 numbers and files: unchanged;
- "20 rounding jitters of the data ... no packaged script recomputes it": README, where only the audit-branch `checks/agentC_checks.py` recomputed it;
- the not-supported list, now with the 2.3 GB archive size attached to the archived products;
- the AnaTuple preservation status "as of" 2026-10-10;
- fixed provenance items: unchanged.

Nothing is now said to exist, be deposited or be reproduced that the base did not say. The one change of scope is the opening sentence, which no longer says the appendix states what each part "does not" reproduce. Restore it (F4).

---

## Counts by direction

| direction | count | findings |
|---|---|---|
| LOST | 3 | F1, F8, F12 |
| WEAKENED | 3 | F4, F14, F15 |
| MOVED-AWAY | 1 | F19 |
| AMBIGUOUS | 10 | F2, F3, F5, F6, F7, F9, F11, F16, F17, F18 |
| ADDED | 2 | F10, F13 |
| **total** | **19** | |

Most serious: F1 (the pinv-convention clause is cut, and app_history.tex:145 now states that the body keeps it), F3
(the negweight scope sentence now reads as denying that negative-weight subtraction is used in production, contrary
to configuration (f)), and F2 (the "2D driver" identifier no longer resolves to any path in the note).
