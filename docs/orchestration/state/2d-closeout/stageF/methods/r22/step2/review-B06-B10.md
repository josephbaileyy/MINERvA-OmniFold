# r22 Step 2 review: pieces B06–B10, in both directions

Scope: `sec_3d.tex`, `scalar_kinematics.tex` (B06), `sec_eavailw.tex` (B07), `sec_5d.tex` (B08), `sec_fived16.tex` (B09),
`sec_joint.tex` (B10). Worktree `wt-con` against base `9d3054f9`; ledgers `ledger-B06.md`–`ledger-B10.md`.
`scalar_kinematics.tex` is unchanged (empty diff). I read every changed printed sentence in the five changed files.
Comment-only changes were skimmed and are not reviewed for meaning.

Counts: **LOST 1, WEAKENED 6, MOVED-AWAY 6, AMBIGUOUS 6, ADDED 5 (24 findings).** Severity is given per finding (H/M/L).
None is high. Seven are medium.

Process note: while reading diffs I wrote two scratch files by mistake (`$R/x_b07.diff` and
`scratchpad/b08.diff`, both git diff outputs). I deleted both. No other file was written apart from this review.

---

## B06: sec_3d.tex

### F01 (M): AMBIGUOUS. The IBU motivation sentence
- Base: "The primary methodological motivation is the absence of a practical analog of D'Agostini iterative Bayesian unfolding (IBU)."
- New: "The primary methodological motivation is that D'Agostini iterative Bayesian unfolding (IBU) has no practical analog for unfolding many observables simultaneously."
- Why: The new text reads as a claim that binned IBU cannot practically unfold many observables. That claim sits next to the
  paragraph citing MINERvA's binned triple-differential results. It also conflicts with the note's own five-dimensional
  exact binned iterative unfolding (sec_5d.tex, "Comparison with exact binned unfolding": a response "binned in the 10,499
  occupied five-dimensional reconstructed cells"). "Many" is undefined. No source states what the task is. The same
  paragraph and sec_intro.tex:31 give the supported reason: the response matrix grows combinatorially with each binned
  observable.
- Fix: reword so that it names the cost, not an impossibility. For example: "The primary methodological motivation is that
  D'Agostini iterative Bayesian unfolding (IBU) has no practical analog of this: each observable it adds multiplies the
  bins of its response matrix."

### F02 (M): ADDED. The gloss on the unified throw
- Base: "Nor is any ratio of the unified-throw to the block covariance."
- New: "Neither a 4D uncertainty nor a ratio of the covariance from joint variation of all sources (the unified throw of \S\ref{sec:uq-combine}) to the summed per-source block covariance is reported."
- Why: sec:uq-combine defines the unified throw as perturbing "all reweightable interaction-model bands and the flux
  universes simultaneously". It does not vary all sources: $C_{\rm stat}$, $C_{\rm ML}$ and $C_{\rm PL}$ are not thrown. So
  "all sources" is inaccurate.
- Fix: "...of the covariance from simultaneous variation of all reweightable interaction-model bands and the flux universes
  (the unified throw of \S\ref{sec:uq-combine}) to the block covariance..."

### F03 (L): AMBIGUOUS. The pointer that replaced the list of corrected-construction items
- Base: "A corrected 4D covariance would use the actual minus and plus variation endpoints; MAT's mean-centered covariance blocks, normalized by $1/N$; one fixed estimator seed; and mean-centered joint throws, with the mean shift reported separately. It would not subtract a scalar jitter floor."
- New: "A 4D covariance would require that section's corrected construction and, ..."
- Why: sec:uq-combine contains each element, as the ledger's probes confirm. But it never calls anything the "corrected
  construction", and its centering and $1/N$ clause describes the "matched block-sum comparator". A reader cannot tell
  which procedure "corrected construction" names.
- Fix: name it, for example "would require the endpoint, seed and centering procedure of \S\ref{sec:uq-combine}, with no
  jitter-floor subtraction". Or restore the short list.

### F04 (M): AMBIGUOUS. The direction of variation in the q3excess caption
- Base: "The joint plane shows genuine $q_{3}$ structure in the data\,$-$\,MC discrepancy (ratio rising with $q_{3}$ across the quasielastic--$\Delta$ dip)."
- New: "In the displayed joint plane the data/Tune~v1 ratio varies with $q_{3}$, rising across the quasielastic--$\Delta$ dip."
- Why: "rising across the dip" now reads as rising along $E_{\rm avail}$. The base fact, repeated in the text ("At fixed
  $\Eavail$ in the quasielastic--$\Delta$ dip, data/Tune~v1 rises with $q_3$"), is that the ratio rises with $q_3$. Dropping
  "genuine" is fine.
- Fix: "...the data/Tune~v1 ratio rises with $q_{3}$ across the quasielastic--$\Delta$ dip."

### F05 (L–M): LOST. The 2D comparison in "invisible in 2D"
- Base: "The $\Eavail$ axis exposes this excess, invisible in 2D."
- New: "Of the displayed projections, only $\Eavail$ locates this excess."
- Why: The scoping was requested (B06-s-10), but the object of the comparison changed. The base contrasted the result with
  the 2D $(\pT,\pPar)$ measurement. The new text contrasts it with the 1D $\pT$ and $\pPar$ projections of Fig. 3dmodels.
  The fact that the 2D measurement does not show the dip excess no longer prints.
- Fix: "Of the displayed projections, only $\Eavail$ locates this excess; the 2D $(\pT,\pPar)$ measurement does not
  resolve it."

### F06 (L): WEAKENED. The closure result's limit to configuration (a)
- Base: "That result does not extend to configuration~(e), and the data-versus-2D scatter compares (e) with (f). The scatter is therefore not read here as ..."
- New: "The recovery is shown for configuration~(a) only, so the data-versus-2D scatter is not interpreted as ..."
- Why: "Shown for (a) only" is softer than "does not extend to (e)". The reason (the scatter is (e) against (f)) now prints
  only in the previous paragraph.
- Fix: "The recovery is shown for configuration~(a) only and does not extend to (e); since the data-versus-2D scatter sets
  (e) against (f), it is not interpreted as ..."

### Reviewed in B06, no finding
- The new configuration table (tab:3d-configs) matches the base sentences and Table tab:estimators-matrix: (e) is "as (c)",
  that is deterministic LightGBM with 400/31 refinement; (a) is LightGBM with purity-based subtraction.
- "Overall completeness of the unfolding input" is supported by the definition of $c$ in sec_method.tex:182.
- "High-level observables" is supported by sec_method.tex:44 ("five high-level features per event").
- "All other final-state particles except neutrons" is supported by EAVAIL_DEFINITION.md:53 ("any other final state
  particles except neutrons").
- Cutting "We therefore do not claim..." is acceptable. Each non-match is still stated per definition ("includes four of
  those five species"; "includes species omitted here"), and "There is no unique published definition" prints.
- The flux-repair reorder, the move of the normalization sentence, "untuned GENIE CV", the mode-decomposition split, the
  FrInel cut (the conclusion prints as the paragraph heading) and "has not been made" (44 cells) all keep their facts.
- "Agrees between the two tested classifier families" is a sanctioned narrowing (B06-s-10). "Bears directly on" is mild
  and acceptable.

## B07: sec_eavailw.tex

### F07 (M): WEAKENED. The Tune v1 localization sentence was cut
- Base: "The localization in \S\ref{sec:eavailw-map} is relative to MINERvA Tune~v1; data exceed all four external generators both overall and in the corner."
- New: (cut)
- Why: Each half has a home: Tune v1 is subtracted in the map, and the ratios exceed 1. But the sentence carried the
  interpretive qualifier that ties them together. The high-$\Eavail$, high-$W$ localization is relative to Tune v1;
  against the external generators the corner shows no distinct deficit beyond each generator's normalization shortfall. A
  reader of the map no longer has that bridge.
- Fix: restore one sentence after the corner discussion: "The localization of \S\ref{sec:eavailw-map} is therefore relative
  to MINERvA Tune~v1; against the four external generators the data are high both overall and in the corner."

### F08 (L): ADDED. A trial factor as the required remedy
- Base: "A future significance for the location identified in the central-value map must account for any selection of the tested region using these data."
- New: "A later significance ... must include a trial factor (look-elsewhere effect) for any selection of the tested region made with these data."
- Why: "Account for" leaves the remedy open; for example, a held-out sample or a declared region would also work. "Include
  a trial factor" prescribes one method, and that prescription comes from general knowledge.
- Fix: "...must account for any selection of the tested region made with these data (the look-elsewhere effect)."

### F09 (L): AMBIGUOUS. Whose seed sensitivity
- Base: "...no compatibility metric based on the configuration-(a) covariance is quoted, for the reason given in \S\ref{sec:eavailw-adopted}, item~1 ..."
- New: "...because that covariance's estimator-seed sensitivity exceeds its preset limit (\S\ref{sec:eavailw-adopted})"
- Why: sec_5d.tex states "Items 1, 2 and 4 use two companion covariances built at two estimator-seed settings; only item 3
  describes this file." The sensitivity is measured on the construction, through the companions, and not on the adopted
  file itself. "Preset" is supported ("set before production, on 2026-09-18").
- Fix: "...because the estimator-seed sensitivity of its construction, measured with two companion covariances, exceeds
  the limit set before production (\S\ref{sec:eavailw-adopted})."

### F10 (L): MOVED-AWAY. The reason GiBUU is low
- Base: "GiBUU is low throughout the $\Eavail$ tail: ... ($E_\nu\approx\SI{20}{GeV}$ limit: \S\ref{sec:eavailw-band})."
- New: "GiBUU is low throughout the $\Eavail$ tail. Its $W$-integrated ... in configuration~(a), ..."
- Why: The opening no longer signals that GiBUU's sample stops at 20 GeV. The fact prints only in the band subsection.
- Fix: append "; its sample stops at $E_\nu\approx\SI{20}{GeV}$ (\S\ref{sec:eavailw-band})".

### F11 (L): MOVED-AWAY. The reason reconstructed Eavail is not a function of the other inputs
- Base: "reconstructed $\Eavail$ comes from a separate calorimetric estimator and is not a function of them."
- New: "reconstructed $\Eavail$ is not a function of them." The reason now sits two paragraphs earlier (in a $q_0$ clause)
  and in the table.
- Fix: restore "comes from a separate calorimetric estimator and". It costs six words.

### Reviewed in B07, no finding
- "Does not establish a bias–variance tradeoff across estimator settings" is supported by sec_5d.tex:105.
- "Estimator-seed shifts of central values" matches item 4.
- "Gives a sixteen-cell $\chi^2$ comparison" matches sec:fived16-gen.
- The 2p2h and FSI rewording of the opening is consistent with sec_3d (2p2h leaves $[1.5,3)$ unchanged; dials below 1%).
- The corner-ratio merge and the "lies close to its integrated ratio" restatement keep the numbers. GiBUU's supplemented
  ratio, 1.37/1.29, is about 6%.
- The cut accessor names have L homes. The headings and "independent of cell area" are fine.

## B08: sec_5d.tex

### F12 (M): ADDED. The gloss on "identified"
- Base: "15 are dominated by the tree approximation, 2 of them in identified quantities, a share of 0.014."
- New: "Only 2 of these 15 lie in identified quantities, those that the binned response constrains well, a share of 0.014 of the 144."
- Why: Neither the base note nor the record defines "identified" as "constrained well". The record
  (`d-id/REPORT.md`) defines "weakly identified" as CR width > 10% (:195). It uses "identified at target" with
  $\sigma_c\le2.5\%$ at T2 (:11, :572, :576), and it treats infinite-$\sigma$ functionals separately. Followed by "121 lie
  in quantities that the binned response constrains weakly", the gloss implies a clean well/weakly split of the 144, which
  the record does not make: there is a 2.5–10% band and there are acceptance holes. "0.014 of the 144" is correct
  (2/144).
- Fix: drop the gloss and point to the record, which the paragraph already cites: "Only 2 of these 15 lie in identified
  quantities (as defined in the diagnostic record cited below), a share of 0.014 of the 144." Alternatively, if the
  director confirms which threshold the A share used, state it ("binned Cramér–Rao width at most 2.5%").

### F13 (L–M): WEAKENED. A necessary condition became a proviso
- Base: "The same information can be transferred onto a sweep block, ..., only with the low-rank treatment, the mean shift and the selection-support bound above documented, a condition set in July 2026."
- New: "...can be transferred onto a sweep block, ..., provided that the low-rank treatment, the mean shift and the selection-support bound above are documented (a condition set in July 2026)."
- Why: "Only with" is a necessary condition. "Provided that" reads as a sufficient one, a permission. The gloss "the same
  inflation of the vertical bands" is correct, from the formula.
- Fix: "...can be transferred onto a sweep block ... only if the low-rank treatment, ... are documented (a condition set in
  July 2026)."

### F14 (L): WEAKENED. The bias-spread caption lost its frontier qualifier
- Base caption end: "They supply neither simultaneous bounds nor total uncertainties. Truth panels and reporting cells form no frontier across estimator settings."
- New: the second sentence is cut.
- Why: The figure plots mean against SD, a bias–spread display, so it invites a frontier reading. The writer brief keeps
  brief reminders in captions that must read on their own. The body statement is far from the figure.
- Fix: restore "They form no frontier across estimator settings."

### F15 (L): WEAKENED. The prior-response caption lost its real-data-bias qualifier
- Base: "Strong correlation supplies no per-cell bound; shifts do not measure unknown real-data bias."
- New: "Strong correlation supplies no per-cell bound."
- Why: This is the figure's main interpretive limitation. It prints only as the paragraph title, which a reader of the
  caption alone does not see.
- Fix: restore "; shifts do not measure unknown real-data bias".

### F16 (L): MOVED-AWAY. The consequence "no tradeoff can be inferred"
- Base: "No matching repeat ensembles exist at more iterations or larger OmniFold capacity, so no tradeoff can be inferred."
- New: "No matching repeat ensembles exist at more iterations or larger OmniFold capacity."
- Why: The sentence now states a missing ensemble without its consequence. The consequence prints in the study's
  introduction and in "Deciding the tradeoff would require..." below.
- Fix: restore ", so no tradeoff can be inferred".

### F17 (L): MOVED-AWAY. H2's five-axis subdivision
- Base: "Both joint partitions subdivide all five axes; H2 is not nested within J."
- New: the label table gives J "subdividing all five axes" but gives H2 only "coarser joint cells, not nested within J". The
  H2 fact prints in sec_fived16.tex:9.
- Fix: in the table, "27 supported coarser joint cells, also subdividing all five axes, not nested within J".

### Reviewed in B08, no finding
- The edge-safe jitter gloss matches `nd-unfolding/s5e_trace.py:351-366`: ±½ float32 ulp, and a value on a grid edge is
  not moved.
- "Estimator $R$, the raised-refinement-capacity candidate of §val-departure" agrees with the candidate paragraph in that
  subsection, the label table and the sec_method comment (R = configuration (e)).
- The "J cells" gloss matches the label table.
- The RD1–RD3 rewrite agrees with the arithmetic (12.0 and 13.4 are above 10; 9.6 + 1.4 = 11.0).
- The eligibility move, the coverage denominators, item 2's merge (the "within these limits" qualifier is kept and moved
  first), the configuration (e) identity move and the status merge all keep their facts.
- "A diagnosis ... accounts for the failure" became "The diagnosis below uses..."; the accounting still prints in the
  paragraph.

## B09: sec_fived16.tex

### F18 (L): AMBIGUOUS. "Not tested" for the power alternatives
- Base: "...the six power alternatives built on that correction are therefore descriptive and ungraded; Table ... with the two descriptive variants of each graded truth."
- New: "...are therefore descriptive and not tested; Table ... with two descriptive variants of each tested truth."
- Why: The alternatives were run, and the table gives their numbers. "Not tested" can be read as "not run". "Ungraded"
  meant not judged against the failure criteria.
- Fix: "descriptive and not judged against the failure criteria".

### F19 (L): ADDED. "Alone" in the model-only variant
- Base: "Model-only: against the statistical block and $C_{\mathrm{model}}$ without the own vertex, ..., so a lower bound on $C_{\mathrm{model}}$'s reach."
- New: "...so a lower bound on what $C_{\mathrm{model}}$ alone accommodates."
- Why: The model-only covariance includes the statistical block, so "alone" is inaccurate.
- Fix: "...so a lower bound on what $C_{\mathrm{model}}$, with the statistical block, accommodates". Or keep the base's
  "$C_{\mathrm{model}}$'s reach".

### Reviewed in B09, no finding
- The support-rule gloss "(minimum expected signal and truth weight)" matches app_statmethods_nd.tex:25 (both at least
  1000).
- "PPFX flux universes" already printed in the base, later in the same file.
- The C_model construction moved up from the base's own later sentence.
- "Its median ... is 2.14%" was correctly attributed to $C_{\rm resp}$; the macro is `sigmed-C_resp`.
- The three groups sum to 8 + 2 + 2 = 12.
- "One control check failed" matches the base (controls 0–6 and 8 passed, control 7 failed).
- "Fixed in advance" for "as declared" is acceptable.

## B10: sec_joint.tex

### F20 (L): ADDED. "Each halving of the cell width"
- Base: "The design takes the step, in a proxy of the test metric, to shrink by a factor of ... per halving."
- New: "The design assumes that each halving of the cell width multiplies the refinement change, measured in a proxy of the test metric, by a factor of ..."
- Why: The refinement is from a "twofold-merged grid" to the fine grid, which halves the cell size or count. It is not
  shown to halve the width along each axis. "Cell width" adds a specification the base does not state.
- Fix: "each twofold refinement of the grid".

### F21 (L): MOVED-AWAY. The local "for reporting only" on the κ scan
- Base: "A scan along the direction $\delta_{\rm fine}$ ... is for reporting only. In the calibration ensembles used for the decisions, it found..."
- New: the qualifier is removed here and prints only in the overview ("They are for reporting only, outside the decision
  rule.").
- Why: The projections subsection keeps its local reminder ("do not enter the Holm family"). The κ result, read alone, now
  has none.
- Fix: insert "(for reporting only)" after the citation.

### F22 (L): MOVED-AWAY. The verbatim conditions and their annotations
- Base: the six conditions were quoted verbatim, with bracketed annotations marking two superseded statements ("MnvTune's
  shapes", and "~0.05" superseded by 0.068).
- New: integrated prose; the verbatim text is in the records (`R:` app_provenance "six conditions verbatim").
- Why: This is the intended change, and every substantive element survives: (i) composition and fixed fine-cell integrals
  with G's fluctuations, 0.50–0.86, κ=2, fixed V before any observed statistic; (ii) bands, ±1σ, five-band surrogate, no
  recoil-scale band; (iii) 34 bands, LowQ2_1/HighQ2_1 clipping ≤0.35% whitened, pilot; (iv) 16 pairs, 0.02–0.075%, +4.7/−3.4,
  0.068, the bias-aligned variant; (v) 20 GeV, out-of-domain migrations, 100 GeV negligible; (vi) diag Var(μ_G) and the drawn
  residual. I list it only so that the reader knows the "as superseded" annotation of "MnvTune's shapes" now lives only in
  the records.
- Fix: none required.

### Reviewed in B10, no finding
- "Each in total and in shape" and "against a null distribution obtained by simulating the full analysis chain" are
  supported by the section.
- The claim-p definition is fine.
- The recovery list-to-prose and "fixed-shift" / "recomputed-shift" (defined before use in projections) are fine.
- The κ merge, power, recoil "scale" and generation-check split keep their facts.
- "Proxy significance ... for the Tune~v1" lacks a noun ("the Tune~v1 null"). This is editorial only.

### Cross-file editorial notes (no meaning change)
- F23 (L, AMBIGUOUS, B07): "as used in the companion paper". The note's own term elsewhere is "companion journal article"
  (sec_intro.tex:30); align for consistency.
- F24 (L, AMBIGUOUS, B06): "It bears directly on the bin-compatible comparison". "Directly" is slightly stronger than the
  base's "natural input"; "It bears on" suffices.

---

## Rulings on the brief's specific points (B06–B10)

**B06: "IBU has no practical analog for unfolding many observables simultaneously".** Fix needed (F01). As written, it
implies that binned multi-dimensional unfolding is impractical. That sits beside MINERvA's binned triple-differential
results and the note's own 10,499-cell five-dimensional binned iterative unfolding (sec_5d). Reword it to name the cost
(response-matrix bins multiply with each observable), not an impossibility.

**B07:**
- **"Spline-normalized" read as "normalized by its flux-averaged total CC cross section per nucleon": OK.** sec_3d prints
  this convention for "each prediction". GENIE+MEC's special handling (non-MEC CC count fixed to the total, MEC added through
  $1/(1-f_{\rm MEC})$) is still flagged by the next sentence ("GENIE$+$MEC uses the normalization convention of the 3D
  comparison").
- **"Null spread" to "null standard deviation": OK.** MP-5 REPORT.md:38 defines $\sigma_c$ reading (a) as "the SD over the
  frozen null ensemble (primary)". GENIE's −0.47/+0.53 is in that unit (:100).
- **"The article" to "The analysis": OK.** "The article" was the companion journal article, main_paper.tex, the PRD target.
  The comment at sec_eavailw.tex:29 says the passage "moved verbatim from the article's Sec. II". In this note "the
  analysis distinguishes" is accurate. Optional: "companion journal article" for the table sentence (F23).
- **Cut sentence on the localization relative to Tune v1: fix (F07).** Restore a one-sentence bridge. Its parts print
  elsewhere, but the interpretive link between the Tune v1-relative map and the generator band does not.

**B08:**
- **The "identified" definition: fix (F12).** Drop the gloss "those that the binned response constrains well" and point to
  the diagnostic record. Or state the record's actual criterion, once the director confirms it.
- **The "edge-safe jitter" definition from code: OK.** It matches `s5e_trace.jitter_coords` (s5e_trace.py:351-366) and
  s5p_numerics.py:15, :80, the L: home in the ledger.

**B09:**
- **Bands glossed "which reweight simulated events": OK.** sec_systematics.tex:12 prints that the lateral bands "shift
  reconstructed kinematics rather than event weights", so the interaction-model and detector bands are the weight bands.
- **"Noise gate" equated with the "statistical gate": OK.** The base itself says the tune ratios are "built as the
  reweighting ratios of the $C_{\rm model}$ vertices are, ... where the tune's sample fails the ratio's statistical gate".
  The PV records (pv-ladder REPORT.md:70, H2-DEFINITION-DECLARATION.md:213, :257) call the same 5% gate on those ratios the
  "noise gate".

**B10:**
- **"About 0.07" replaced by 0.068: OK.** The base already printed 0.068 as "the value used in (iv)", in the quoted
  annotation.
- **A superseded "~0.05" now prints: OK.** It printed in the base inside the verbatim quote, marked superseded. The new
  text keeps it explicitly labelled as superseded ("supersedes the specification's estimate of about 0.05"). Moving it to
  the records would also be acceptable, but it is not required.
- **`\jtRecompRows` count moved to the records: OK.** The scope ("every $p$ value and decision") still prints, and
  app_provenance holds "1379 of 1379 rows".
- **"0.72" named as "the shape power at 0.005 against the first alternative": OK.**
  RECORD-20261006-s5p-lost-seed-recovery-resolution.md §4 gives 0.715 for P1g, shape @0.005, under the union null
  recomputed on all draws.
