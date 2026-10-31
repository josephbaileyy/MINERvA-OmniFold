# r22 Step 3 review: pieces B12, B13, B14, B15 (and the integrator's `\clearpage`)

Reviewer: an independent, read-only session. Base `14a0415f`; worktree `wt-con`. Each change was read with
`git diff 14a0415f -- docs/analysis-note/<file>`. Files: `app_guide.tex`, `app_statmethods.tex` (B12);
`app_statmethods_nd.tex` (B13; `app_negweight.tex` is unchanged); `app_response_mismatch.tex`, `app_landscape.tex`,
`app_pet_pointer.tex` (B14); `app_release.tex`, `app_codebase.tex` (B15 and the integrator).
Ledger homes were opened at the cited files. No command wrote anything, and no build was run.

Findings: 6 (LOST 1, ADDED 2, AMBIGUOUS 3). Two further observations come after the findings. They are not
regressions.

## Findings

### F1 (B12-g-04): the registry still cites the cut label-table rows
- **ID:** `app_guide.tex`, the cut table row "`\texttt{lgbm}, \texttt{exact}, \texttt{hist}` & the learner backends:
  LightGBM (the quoted central values and their uncertainty ensembles; also the joint-test estimator), …".
- **direction:** LOST (the records' anchor for the `lgbm` code name).
- **base text:** base `app_guide.tex:15-16` held `\texttt{lgbm}` and "also the joint-test estimator".
  **new text:** the row is gone. The new `app_guide.tex` has 8 lines and contains no `lgbm`.
- **why:** The ledger's `R:` home is the generated records file, and that file still points into the cut row.
  - `docs/orchestration/registry/ALIASES.tsv:7` cites `docs/analysis-note/app_guide.tex` line 15 with quote
    `\texttt{lgbm}` and a line digest.
  - `UNRESOLVED-NAMES.tsv:5` cites line 16 ("also the joint-test estimator").
  - The generated `records_estimators.tex` prints these citations at rows 32, 117 and 126 ("code-name lgbm …
    app_guide.tex:15"; "also used unmapped (app_guide.tex:16)"). Its header says "Every row cites a line that carries
    its quote".
  - Neither the TSVs nor `records_estimators.tex` changed in this round. So the records' home for "lgbm = LightGBM"
    now names a line that no longer exists.
  - `tools/registry/check_registry.py`, run in CI (`.github/workflows/record-checks.yml:88`), should fail on these
    rows once the change is committed. I checked this by reading the files; I did not run the checker, because it
    reads the git index.
  - The mapping itself still prints at `records_estimators.tex:10` ("nominal LightGBM … `--estimator lgbm`"). What
    is lost is the integrity of the registry's citation, not the fact.
  - The ledger check could not see this. It probes only that strings print, not what other files cite.
- **fix:** reword. Re-point or retire ALIASES.tsv row 7 and UNRESOLVED-NAMES.tsv row 5. Candidate targets are
  `nd-unfolding/unfold_nd_omnifold_unbinned.py:635` (`--estimator lgbm`), which is already cited at row 31, or
  `records_estimators.tex:10`. Then regenerate with `tools/registry/results_index.py --write`, and run
  `check_registry.py` before the commit. These files are outside B12's file set, so the director must assign them.

### F2 (B12-g-06): "MAT's code supplies these" covers the ±1σ pair formula, which the note says MAT does not have
- **ID:** `app_statmethods.tex`, `\paragraph{Ruterbories 2021, Section V.}`: "The paper itself gives no per-band
  covariance construction, no $\pm1\sigma$ pair formula and no band-independence or block-sum statement; MAT's code
  supplies these (below)."
- **direction:** ADDED. It is also partly BEYOND-NARROWED, toward the refused form "previously encapsulated within
  the experiment's analysis framework".
- **base text:** "It leaves to MAT, or does not state, the per-band covariance construction, any $\pm1\sigma$ pair
  formula and any band-independence or block-sum statement; …"
  **new text:** as quoted in the ID.
- **why:**
  - The base's "leaves to MAT, or does not state" did not say which item MAT supplies. The narrowed form asks the
    writer to make that split. The writer put all three items on the MAT side.
  - The very next paragraph contradicts this for the pair formula:
    - `CalcCovMx` is mean-centered at 1/N "with no special case for $N=2$";
    - the CV-centered pair formula is the "MINERvA-101 $\pm1\sigma$ pair", which "agrees with it only for CV-symmetric
      shifts".
  - So MAT's code has no ±1σ pair formula. That item belongs on the side the publication does not state. The per-band
    construction (`CalcCovMx`) and the band sum assuming independence (`GetTotalErrorMatrix`) are rightly on the MAT
    side.
- **fix:** reword, for example: "The paper itself gives no per-band covariance construction, no $\pm1\sigma$ pair
  formula and no band-independence or block-sum statement. MAT's code supplies the per-band construction and the
  independent band sum, but no separate pair formula (below)." Keep the "Nor does it state …" sentence as written.

### F3 (B14-g-02): a proposal becomes an asserted property
- **ID:** `app_response_mismatch.tex`, opening paragraph: "Stressing the hadronic record, especially for quasielastic
  events, probes low-$W$ bias."
- **direction:** ADDED.
- **base text:** "Kevin McFarland suggested this distinction and proposed stressing the hadronic record, especially for
  quasielastic events, to inspect low-$W$ bias (private communication)."
  **new text:** the sentence in the ID, with the footnote "We thank Kevin McFarland for suggesting this distinction
  and stress (private communication)."
- **why:**
  - The base gives a purpose: someone proposed the stress in order to inspect low-W bias. The new sentence says, in
    the present indicative, that the stress does probe low-W bias.
  - That is a claim about how well the method works. Nothing supports it: App. D says the test has not been run and
    no threshold is set.
  - The narrowed form asks to "retain the physical rationale". A rationale is not an established property.
- **fix:** reword, for example: "Stressing the hadronic record, especially for quasielastic events, is proposed to
  inspect low-$W$ bias." or "… would probe low-$W$ bias." Keep the footnote (see F6).
<!-- absence-ok: quotes printed note sentences, the raters' flags or the reviewers' findings; not a claim that something has not been run -->

### F4 (B13-g-06): "requires pseudo-experiments to be lost" can be misread
- **ID:** `app_statmethods_nd.tex`, *Probability model*: "this requires pseudo-experiments to be lost independently of
  their outcomes, which has not been shown (…)".
- **direction:** AMBIGUOUS.
- **base text:** "this requires the lost pseudo-experiments to be lost independently of their outcomes."
  **new text:** "this requires pseudo-experiments to be lost independently of their outcomes, which has not been
  shown (\S\ref{sec:joint5d-frozen}, with the design's data-informed elements)."
- **why:**
  - Dropping "the lost" removes the presupposition that some draws were lost. The sentence then reads naturally as
    "A2 requires that pseudo-experiments be lost".
  - The fact of the loss still prints in the "Crossing event" paragraph ("lost draws") and in `sec_joint.tex`. So
    nothing is lost, but the clause that carries the requirement is now ambiguous.
- **fix:** restore. Use "this requires the lost pseudo-experiments to have been lost independently of their
  outcomes", which is the `sec_joint.tex` wording.

### F5 (B13-g-06): the cross-reference parenthetical is unclear
- **ID:** the same sentence: "(\S\ref{sec:joint5d-frozen}, with the design's data-informed elements)".
- **direction:** AMBIGUOUS (low).
- **why:** The section reference is right. Both the A2 disclosure (`sec_joint.tex:109`) and the two data-informed
  elements (`:118`) print in §11.3. But "with the design's data-informed elements" reads as if those elements were
  part of what "has not been shown", or were attached to the reference. It does not clearly say "see also".
- **fix:** reword, for example: "… which has not been shown (\S\ref{sec:joint5d-frozen}, which also states the design's
  two data-informed elements)". Check the length against the file budget.

### F6 (B14-g-02): "this distinction and stress" in the footnote
- **ID:** `app_response_mismatch.tex` footnote: "We thank Kevin McFarland for suggesting this distinction and stress
  (private communication)."
- **direction:** AMBIGUOUS (low).
- **why:**
  - "Stress" as a bare noun can be read as "emphasis".
  - The base credited two acts: he *suggested* the distinction and *proposed* stressing the hadronic record. The
    footnote merges them into "suggesting".
  - The credit is not lost. It is compressed, and the object of "stress" is two sentences away.
- **fix:** reword, for example: "… for suggesting this distinction and the stress of the hadronic record (private
  communication)."

## Observations (not regressions)

- **"flux-corrected" has two meanings (carried over from the base).**
  - The new prose definition reads: "Products described as flux-corrected are those repaired for an audit finding that
    the $N$-dimensional code divided every flux universe by the central-value flux".
  - It repeats the base table row. But `sec_eavailw.tex` also calls the GENIE and NuWro *generator predictions*
    "flux-corrected". That refers to the flux-repaired predictions of 2026-09-27, a different repair.
  - The base had the same conflict, so this round introduced nothing. Now that the label J28 has gone, the
    definition reads as universal.
  - Optional: "Unfolded products described as flux-corrected …".
- **B12-g-11: the reviewer's premise is inaccurate, but the result is OK.**
  - App. D's *title*, "Detector-response-mismatch closure test", does not state the unexecuted status.
  - Its first paragraph does: "Its first stage has been implemented but not yet run: no output has been produced and
    no pass threshold has been set." That paragraph is where the status qualifies the protocol.
  - The guide's new description ("rescales the reconstructed available energy of the pseudo-data while OmniFold keeps
    its nominal response") matches App. D's equation and "OmniFold still uses the nominal response". "Protocol" keeps
    the status of a plan.

## Changes checked and found clean

- **B12-g-04, the remaining rows.** The calls row is kept as a sentence; every call, the option and every `\ref`
  survive. "Without the normalization band … used the option `--add-norm 0`" is the same fact. "Or here" is removed
  together with the table, which is consistent.
- **B13-g-09.** "No new validation result accompanies these requirements" keeps both "requirements" and "no new
  validation result". The merged sentences keep the citation and every statement. Dropping "also" and "their" changes
  no meaning.
- **B14-g-05.** "By design a computationally inexpensive adversarial stress test; it is not a detector model" is the
  narrowed form. It makes no sensitivity-bound or conservativeness claim.
- **B14-g-09.** "The survey is nonexhaustive through 2026" has the same strength and the same cutoff.
- **B14-g-03.**
  - The path and `\repolink` are removed. "That work, in progress, is documented separately" and the exclusion
    sentence are kept, and no citation is invented.
  - The repository link still prints on the title page (`main_note.tex:37`).
  - The ledger home `docs/analysis-note/README.md` names `pet_note.tex` and its role.
- **B15-g-04.**
  - "An earlier release candidate, RC1, passed its packaged verifier when replayed from an empty directory in a
    separate AI-agent session (Opus 5.5) using only the package and its README, without repository access."
  - It keeps the version, the agent, the empty directory, no repository access, README-only and the pass. It is
    tied to RC1, not RC7.
  - "Packaged" is supported: the replay had only the tarball, according to the source comment's receipt.

## Rulings on the specific points in this range

- **B12-g-04 (the cut rows and their `R:`/`L:` homes): fix needed (F1). Otherwise OK.**
  - `lgbm`/`exact`/`hist`: `records_estimators.tex:10-12` holds each label with its learner (LightGBM; scikit-learn
    GradientBoosting exact-split; HistGradientBoosting). `sec_method.tex` and `app_codebase.tex` print the roles,
    including the joint-test estimator. OK, but F1 applies: the registry rows still cite the cut lines.
  - `purity`/`negweight`/`negweight-refined`: the driver's `--bkg-mode` (`unfold_2d_omnifold_unbinned.py:1362-1369`)
    lists the three values. Its help text maps 'purity' to the binned purity down-weight and 'negweight' to unbinned
    negative-weight injection. `app_provenance.tex:115` gives purity as the default. The note prints the three
    treatments in words and the option at first use in App. C. OK.
  - `cv`/`mean`: both labels print at first use (`sec_5d.tex`, `sec_systematics.tex`), with "this note uses cv". OK.
  - `MNV101_ACTIVE_UNIVERSE`: `2D_OMNIFOLD_REFERENCE.md:430-433` gives it as the mode to use when a shifted selection
    can move events. The note prints the re-selected loops in words (`sec_systematics.tex`, `app_statmethods.tex`). OK.
  - The calls and `--add-norm 0`: kept in the note. OK.
  - July/May sweep: both names print at first use in `sec_systematics.tex`, and both were present at the base. The
    July sweep's role prints there too. OK.
  - J28: the `AUDIT-FINDINGS-20260731.md` J28 heading matches the cut row. `app_history.tex` cites J28. Neither the
    note text nor the built PDF prints "J28" or "(J28)" any more, so no undefined label is left. OK.
- **B13-g-06 ("which has not been shown" in the appendix): a restatement, not a new claim. OK, apart from wording
  (F4, F5).**
  - The clause repeats, at the same strength, `sec_joint.tex:109`: "A2 requires the lost pseudo-experiments to have
    been lost independently of their outcomes, which has not been shown."
  - The narrowed form asks for exactly this link, and `\S\ref{sec:joint5d-frozen}` points to the section that prints
    it.
  - The data-informed elements are linked, not restated. That respects the round-n1 rule, recorded in a source
    comment at `sec_joint.tex:6-7`, that they are stated once, in sec:joint5d-frozen.
- **B14-g-02 (McFarland credit moved to a footnote): the narrowed form, OK. It adds no acknowledgment beyond the base.
  Fix F3 (and optionally F6).**
  - The footnote carries exactly the base credit: the distinction, the hadronic-record stress, and "private
    communication". The Acknowledgments in `main_note.tex:108-109`, Joseph's protected text, are unchanged.
  - The Acknowledgments already thank him for "suggesting a detector-response-mismatch closure targeting correlations
    among the reconstructed hadronic observables". So the footnote is a second, narrower thanks for the same
    contribution, not a new credit.
  - A footnote is the only form of acknowledgment the writer could reach, since `main_note.tex` is off-limits.
  - The defect is in the body sentence left behind (F3), not in the move.
- **B15-g-08 ("should not be checked" for "Do not check"): OK.**
  - The sentence is advice about checking a printed value. In this spec register, "should not be checked" keeps the
    prohibition, alongside "should *not* be inverted" two items later.
  - The reason is unchanged: the value is at the noise floor and its sign carries no information.
  - "Two hosts agree on $\lambda_{\min}$ to only five significant digits" is the same finding as "a second host
    reproduces … to only five significant digits".
  - It stays true of the package: `publication/release/verify_rc.py` and the other release scripts contain no check
    of an eigenvalue sign.
- **B15-g-06 ("(fixed)" for the check marks): OK.**
  - The same five items are marked, so the set of fixed identities is unchanged.
  - The definition sentence keeps "the rest are packaging" and "A fixed identity specifies which object is meant, not
    whether the object is scientifically qualified."
  - The Provenance item still lists, in words, its only fixed parts. `acceptance_question: UNDECLARED` keeps its own
    explicit-status paragraph.
  - Nothing said to exist, be deposited or be reproduced has changed.
- **Integrator `\clearpage` at the end of `app_codebase.tex`: OK. It changes no printed text.**
  - The diff is two added lines after `\end{figure}`: one full-line `%` comment, which does not print, and
    `\clearpage`.
  - Only `main_note.tex` inputs `app_codebase.tex` (line 143), immediately before `\printbibliography` (line 145). So
    the page break can affect only where Fig. 36 and the References page fall.
  - The only `\pageref` targets are in the executive summary, before this point, so their numbers cannot move.
  - In `main_note.pdf`, App. I's text ends p. 120, Fig. 36 is alone on p. 121 and "References" begins on p. 122.
  - Caveat: that PDF (16:31:41) is 48 s older than the last write to `app_codebase.tex` (16:32:29). Its layout shows
    the `\clearpage` in effect, which suggests only the comment changed afterwards. Still, a rebuild from the final
    source is needed to confirm the delivered layout.
