# Changes: note register round n1 (2026-10-25/26)

Base origin/main `ddf16f10`. Every change, paragraph by paragraph, for the six batches. The full source diff is
`git diff ddf16f10 -- docs/analysis-note/` on this round's commit; the fact ledger is `ledger.md` in this directory.
The batch sections are the writers' records as adopted; the review fixes that followed are listed after them, and
each one's ledger row carries its final text.

## Changes, batch n1-B (§3 sec_method.tex, §4 sec_systematics.tex, §5 sec_validation.tex)

Base `ddf16f10`. Each entry: before, after, rule, and the restatement's home. Ledger rows in
`ledger.md`. Labels, section and paragraph headings, numbers, macros, tables, figures and captions are unchanged.

## §3.2 sec:method-config

**C1. Single home for the 2D central value's history (R-N2).**
- Before: the exact-split paragraph opened "It gave the quoted 2D central value until 2026-10-11, and studies in this
  note labeled *exact-split* use that central value; they have not been recomputed." The rebuild with (f) was stated
  separately, after the configuration list.
- After: the exact-split paragraph describes the estimator only. The paragraph after the configuration list carries
  the 2D history in two adjacent sentences: "The 2D central value and its covariance were rebuilt with
  configuration (f) after a two-dimensional closure test with backgrounds found the purity bias (App. C). The
  exact-split cross-check gave the quoted 2D central value until 2026-10-11; studies in this note labeled
  *exact-split* use that central value and have not been recomputed."
- Home: §3.2, the paragraph after the configuration list. The date is kept: `app_history.tex` is not input by
  `main_note.tex` (it is part of the records document), so moving the date there would take the fact out of the note.
  Search lines were added to both changed paragraphs (each contains absence claims).
- Not done: the outline's replacement sentence ("results labelled exact-split use the exact-split cross-check"). It
  would drop the date and "have not been recomputed", which have no other home in the note.

**C2. Seed choice (R-N6, R-P4).**
- Before: "Seed 42 was chosen on cost: of the two ways of matching the central value and the statistical band in seed
  that the analysis design costed, a matched seed-42 statistical band was the cheaper."
- After: "Seed 42 was chosen on computing cost: of the two costed ways of matching the central value and the
  statistical band in seed, a matched seed-42 statistical band was the cheaper."

**C3. Stale comment.** The FACT comment saying the May-sweep clause "stays in sec:uq-2d-construction" now names
sec:uq-2d-scope.

## §4 sec:systematics

**C4. §4.1 pointer.** "(… same shift as Rvn1pi (§4.4) …)" now points to §4.6, where the double count is described.

**C5. §4.2, the 2D-band restatement points to §5.2 (R-N2, R-N1, R-N6).**
- Before (5 sentences): no coverage test of the quoted block; the band quoted when the test ran undercovered in its
  tails, unevenly; it was rebuilt; neither band is the quoted block; the rebuilt band was re-evaluated only post hoc,
  on the same pseudo-experiments, partly circularly, and is untested independently; no held-out test, "no design for
  one has been registered in advance".
- After (2 sentences): "The statistical block quoted here has had no coverage test: the fixed-truth coverage studies
  of §5.2 scored two earlier statistical bands, not this block. No coverage test on held-out simulation has been run,
  and no design for one has been specified." The sentence on what a fixed-truth test cannot decide stays, because it
  qualifies the 0.407 ratio printed just before it (guardrail).
- Homes: §5.2 prints the undercoverage ("The band fails: it undercovers in its tails"), the unevenness ("Uneven in
  both directions"), the rebuild ("The band was then rebuilt without this term"), the third ensemble ("The quoted
  statistical block is a third, different ensemble"), and the post hoc, circular rescoring on the same 100 toys.
  Table `tab:validation-questions` prints "Rebuilt band awaits independent test". The wording follows the paper's
  "The block supersedes two earlier statistical bands, whose coverage studies are described in [note §5.2]".
- "registered in advance" became "specified" (R-N6). KNOWN_ISSUES row 85 gives the fact: the re-test is deferred and
  not pre-registered. Search line added.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

**C6. §4.4 sec:uq-2d-construction keeps the checks of the quoted construction.**
- Before: §4.4 opened with the review's finding of defects in the earlier budget, then interleaved the earlier
  budget's defects with checks of the quoted construction.
- After: §4.4 holds the July sweep's provenance (driver checksum, driver not committed, seven universes reproduced),
  the small-input responses, the lateral bands' seed noise, the flux-universe index identity and the flux weights.
  It ends with one pointer sentence: "The corrections the quoted budget makes to the earlier 2D budget are stated in
  §4.6."
- Two sentences gained a subject because the sentence before them moved: "The products of the July sweep, which the
  quoted universe block uses, do not record a checksum …", and "Each lateral band of the quoted universe block uses a
  single unfold …".
- The label and the subsection title are unchanged.

**C7. §4.6, new paragraph "Changes from the earlier 2D budget." (director ruling).**
- The paragraph gathers the seven statements on the earlier budget that §4.4 printed:
  1. the review's finding;
  2. the May sweep's truth-input mismatch;
  3. its consequence (does not invalidate the covariance, no correction to subtract);
  4. the Rvn1pi/Rvp1pi double count;
  5. its size (0.088%, a real defect, no conclusion about the published analysis);
  6. the unpropagated background-template statistics;
  7. the earlier printed budget left unchanged.
- It also carries their attached sentences: the first-order cancellation; the unavailable May input; the July sweep
  without the mismatch; Rvp1pi dropped in the quoted block; the 60-of-205 reconstructed-space diagnostic; the quoted
  block's background stream and re-selected laterals. Each fact is kept, with a ledger row each (SY-D1 to SY-D7, and
  the a/b rows).
- Framing: "The saved products and code of the earlier 2D budget [46] show the following defects in its
  construction, each of which the quoted budget corrects. First, … Second, … Third, …".
  - "A review … found further defects" became "show the following defects" (R-N6). No count is printed, because the
    review (TwoDFollowup2026 §A4) lists more items than these three, and "the following" keeps the correction claim
    to the three named.
  - "counting it twice" became "and the earlier budget counted it twice". This names the subject the participle
    referred to. The review says "the adopted C_U sums one shift twice".
- Placement: the end of §4.6, after "Seed-related terms reported, not added". The source comments moved with the text.
- The "Other limitations" list now gives the duplicated pion band as "(below)".

## §5 sec:validation (the check-bound sentences, the `\covTwoD*` uses and the struck-value context are untouched)

**C8. §5.2 outcome sentence (R-N6).**
- Before: "Under the predeclared criteria this is a failure by undercoverage, and the study stopped under its
  futility rule."
- After: "By the criteria above this is a failure by undercoverage, and the study stopped at the interim analysis."
- Home of the pre-specification: "The design, criteria and positive control of the test were specified before any
  toy was generated". Home of the stopping rule: "A failure at the interim analysis of 100 toys, with 99.5%
  intervals, stops the study."

**C9. §5.2 (R-N1).** "The result above is for the earlier band." is dropped. Home: the section's second sentence,
"That band is an earlier one, not the quoted statistical block." The next sentence ("… and the quoted block has not
been tested"), which the paper's source comment quotes, is unchanged.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

**C10. §5.2 (R-N1).**
- Dropped: the closing sentence on split-sample width checks and the new inputs.
- Home: the §5 paragraph "What the remaining validation needs", which says the same with more detail: precision is
  conditional on the fixed MC sample, binning maps and purity; there is no variation across MC populations; validated
  totals for the 205 bins, integral and projections cannot be obtained from current inputs; the needed inputs are
  listed; it points to §4.6. §4.6 also lists the omitted terms.

**C11. §5.3 pull diagnostic (R-N1, R10).**
- Before: "… diagnostics only. They are not a frequentist coverage measurement, they do not certify the bootstrap
  band, and no coverage number is quoted from this ensemble."
- After: "… diagnostics only: they do not certify the bootstrap band, and no coverage number is quoted from this
  ensemble."
- Home of "not a coverage measurement": the paragraph heading, "(not a coverage test)".

**C12. Stale comment.** The C3 comment in "What the remaining validation needs" now says the construction fixes are
stated in §4.6.

## Changes, batch n1-C (§7 `sec_3d.tex`, §8 `sec_eavailw.tex`, §9 `sec_5d.tex`)

Ledger row ids (C01–C33) in
`ledger.md`. Section numbers are as the PDF prints them: `sec:val-departure` is §9.3 and `sec:coverage-5d` is §9.5
(the outline and the brief call them §9.2 and §9.4; I followed the labels).

## Reverse outline before editing (one line per paragraph; changed paragraphs marked *)

**§7.** lead: dimensional cost; IBU motivation | binned 3D results exist; what is distinctive | *[new: one statement of
the three caveats]* | 7.1 E_avail truth definition | reco definition | inherited, not matched to a published convention |
135 MeV constant, effect not assessed | unfolding and binning, configurations | 7.2 spectrum | 7.3 2D anchor,
cross-configuration, normalization and shape | 7.4 closure, one bump | scope of the closure | 7.5 GBDT vs NN |
7.6 generators listed | *flux repair* | totals and ordering | *Fig. 3dmodels caption* | *integrated rates; no 3D
covariance* | 7.7 *lead: central values, no mechanism* | *FSI dials (footnote)* | missing 2p2h | *Valencia 2p2h
(central-value qualifier)* | high-E_avail bin | *2p2h vs two-body current, so no mechanism* | *Ascencio deficit,
descriptive* | *captions modedecomp, mec* | 7.8 q3 definition | 4D→3D check | *what q3 adds; no per-cell
significance* | no 4D uncertainty | Ascencio bin-identical | *caption ascencio* | caption q3excess.

**§8.** *lead: in central values; no mechanism* | 8.1 W definitions | W edges; 5D/4D check | 8.2 table | reco W
redundancy | truth W residual | correlations, W information unmeasured | negative W², axis pT | 8.3 table; target
difference | 8.4 excess shares | *descriptive, no mechanism, nominal response, bias* | caption | 8.5 corner ratios |
2p2h leaves corner | W 1.4–1.8 | Tune-v1-relative | caption | *SIS context; descriptive location; Ascencio with no
metric*.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

**§9.** lead roadmap | 9.1 *mechanisms; summary of refinement and signal-only findings* | 2D closures no background |
table intro | *table (two criterion cells)* | 9.2 background subtraction | *generator-sized change; bias status* |
9.3 steps behave; noise-free residual | *diagnosis; rules allow; requirement* | binned comparison | *refinement
candidate; predeclared stability test* | held-out shapes | 9.4 production LightGBM | three quantities | set-up,
seeds | cells | labels table | historical deformations (built before the flux repair) | recovery traces; iteration
rule | *reporting definitions; fixed before ×2; rules allow* | variability | *development intervals; neither check* |
*paired perturbation study* | prior sensitivity | deciding the tradeoff | 9.5 *coverage test, predeclared, no
coverage claimed* | definition and numbers | diagnosis | 9.6 *Status: exception, metadata* | construction | centering |
projection | conditioning | four limitations | magnitude criterion not computed.

## Per paragraph

| where | before | after | rule | home of the restatement |
|---|---|---|---|---|
| §7 lead (new paragraph after "not the number of dimensions by itself") | — | "The comparisons with generator predictions in this section and in Sec. 8 are descriptive comparisons of central values, and they do not identify a nuclear or interaction mechanism (§7.7). In three and four observables they use central values without uncertainties: no 3D or 4D covariance is quoted, and no generator χ², p-value or significance (§§7.6 and 7.8)." With a Search line. | R-N1 | this is the home (director's ruling) |
| §7.6 flux repair | two history sentences, then "Apart from three studies …, the GENIE and NuWro predictions … are repaired by exact per-event reweighting …" | the repair sentence first (unchanged, its exception kept in the sentence), then one sentence: "The repair corrects the flux from which the GENIE (CV and +Valencia 2p2h) and NuWro samples were generated: it had no PPFX weights, was capped at 50 GeV, and stored flux densities in variable-width bins that were sampled and normalized as contents, which under-weighted every wide high-energy bin and suppressed the high-p∥ predictions and the integrated rates (Ref., flux-repair)." | R-N2 | — (every fact kept; the citation keeps its sentence, records-ledger row L-thin-C29 still holds) |
| Fig. 3dmodels, modedecomp, mec captions | "Data have/carry no error bars because the 3D covariance that would be quoted is not used for any result in this note." | "… because no 3D covariance is quoted (§7)." | R-N1 (caption meaning kept: no error bars, and why) | §7 lead; the projection's status stays in §7.6 |
| §7.6 after Fig. 3dmodels | "No 3D covariance, generator χ², p-value or significance is quoted. The 3D covariance that would be quoted is the exact projection …" | first sentence removed; the projection sentence kept | R-N1 | §7 lead |
| §7.7 lead | "… by generating the relevant physics. The comparisons use central values without uncertainties and do not identify a nuclear mechanism. MINERvA first …" | sentence removed | R-N1 | §7 lead |
| §7.7 FSI footnote | "In 2026 the collaboration confirmed that this is current practice and that the reason is a degeneracy …" | "This is MINERvA's current practice (private communication from the collaboration, 2026), and the reason is a degeneracy …" Search line added for the paragraph's "neither was recomputed". | R-N6 | — |
| §7.7 Valencia 2p2h | "closing, in central values without uncertainties, 52 % …" | "closing 52 % …" | R-N1 | §7 lead (the Fig. mec caption keeps "in central values") |
| §7.7 2p2h vs two-body currents | "… and the subsequent hadronic transport, so these comparisons do not identify a nuclear mechanism." | "… and the subsequent hadronic transport." The reasons stay; the lead points here for them. | R-N1 | §7 lead |
| §7.7 Ascencio deficit | "… consistent with that established low-recoil deficit; the comparison is descriptive and does not measure its cause." | "… consistent with that established low-recoil deficit." | R-N1 | §7 lead |
| §7.8 what q3 adds | "The map uses central values and the MINERvA Tune v1 prior, distinct from … No per-cell significances are reported without a corrected 4D covariance (below)." | "The map's comparator is the MINERvA Tune v1 prior, distinct from …" | R-N1 | §7 lead; "no corrected 4D covariance" stays in the next paragraph and at the Ascencio comparison |
| Fig. ascencio caption | "… because the 4D covariance that would be quoted is not used for any result in this note; …" | "… because no 4D covariance is quoted (§7); …" | R-N1 | §7 lead |
| §8 lead | "In central values, Valencia 2p2h closes …"; "… maps where in W the high-E_avail excess lies; it does not identify an interaction mechanism." | "Valencia 2p2h closes …"; "… maps where in W the high-E_avail excess lies." | R-N1 | §7 lead, which names §8 |
| §8.4 after the shares | "These are descriptive central-value statements under the nominal detector response. The map does not locate an interaction mechanism, and the regularization bias of Sec. 9 is largest at high E_avail and high W." | "These statements hold under the nominal detector response, and the regularization bias of Sec. 9 is largest at high E_avail and high W." Search line added (the paragraph's two absence claims are unchanged). | R-N1; guardrail keeps the response condition and the bias location | §7 lead; the caption keeps its "they do not locate an interaction mechanism" |
| §8.5 end | "The location identified in the central-value map is descriptive; a future significance must account …"; "… on the maximal common grid, with no reported covariance-based consistency metric." | "A future significance for the location identified in the central-value map must account …"; "… on the maximal common grid." | R-N1 | §7 lead; §7.8 ("No pulls or full-covariance χ² are reported") |
| §9.1 | "Each test below isolates one intervention. Improved background refinement repairs the nominal recovery, while the failure of signal-only experiments to follow a truth departure shows that background subtraction does not explain all the residuals." | "Each test below isolates one intervention." | R-N1 | §9.2 (refined subtraction; signal-only result), §9.3 (refinement candidate) |
| Table validation-design-5d | "recovery requirement set before the test; not met"; "upper bound on coverage at least 0.66 (0.94), fixed in advance" | "recovery requirement; not met"; "upper bound on coverage at least 0.66 (0.94)" | R-N6 | the timing once at each home: §9.3 (recovery requirement), §9.5 (futility criterion) |
| §9.2 generator-sized change | "… not of the background treatment. This regularization (unfolding-model) bias enters no quoted uncertainty." | "… not of the background treatment (§9.3)." | R-N1 | §9.3 |
| §9.3 diagnosis | "No single cause is established, and no estimator change that the study's rules allow meets the recovery requirement of the GiBUU-to-GENIE departure screen, which was set before the test." | "No single cause is established, and no estimator change within the scope of the study meets the recovery requirement, set before the test, for the GiBUU-to-GENIE departure. The E_avail and q3 residuals, a regularization (unfolding-model) bias of the estimator, enter no quoted uncertainty." | R-N1 (home), R-N6 | this is the home; "E_avail and q3" keeps the scope of base "this bias" (both results) |
| §9.3 refinement candidate | "The candidate fails the predeclared data-stability test: …" | "The candidate fails the data-stability test, whose criterion was set before it was run: …" | R-N6 | — |
| §9.4 reporting definitions | "… so the total-width target fixed before the study (median 68 % half-width at most 10 %) cannot be met …"; "The selection procedure, also fixed before the study, then takes RD3 …"; "… with any estimator configuration that the study's selection rules allow within its computing budget." | "The study set its total-width target, a median 68 % half-width of at most 10 %, and its selection procedure before it was run. It adds … so the total-width target cannot be met …"; "The selection procedure then takes RD3 …"; "… with any estimator configuration within the study's scope and computing budget." | R-N6 | — |
| §9.4 development intervals | "… among the six estimates. Neither check establishes total coverage." | "… among the six estimates." | R-N1 | §9.5 |
| §9.4 paired perturbation study | "The study leaves the stability failure in place, establishes no interval coverage, and does not transfer to the five-axis covariance used in this note." | "The study leaves the stability failure in place and does not transfer to the five-axis covariance used in this note (for interval coverage, see §9.5)." | R-N1 | §9.5 |
| §9.5 opening | "It failed its predeclared futility criterion at the nominal truth and under …, so no frequentist coverage is claimed for any five-dimensional interval." | "It failed its futility criterion, set before the test was run, at the nominal truth and under … (below). No frequentist coverage is therefore claimed for any five-dimensional interval." | R-N1 (home), R-N6, R10 | this is the home |
| §9.6 Status | "The covariance does not meet the acceptance criteria of its specification. The specification requires …, so the requirement cannot be met for it, and the file's own metadata records it as not passing and as not to be used. It is used under an exception that covers only this file and its projection, not any other covariance built to the same specification, including the two companion covariances of the measurements below." | "The covariance does not meet the acceptance criteria of its specification, and its metadata mark it as not passing and as not to be used. The specification requires …, so this covariance cannot meet that requirement. This note nevertheless uses this file and its projection. That use does not extend to any other covariance built to the same specification, including the two companion covariances of the measurements below." | R-N6 | this is the home (stated once) |

## Not changed, deliberately

- **§9.4 iteration rule**, "a rule fixed before the comparison would have replaced its five iterations by 10, 15 or 20
  only if one of them lowered the rule's measure of model dependence": already the criterion stated as a criterion, and
  `paper_body.tex` (r18 S8 comment) cites this sentence as the note's home for "fixed before the comparison".
- **§9.6 item 1** ("movement limit set before production, on 2026-09-18") and the closing paragraph ("criterion
  specified before production has not been computed"): the first is the basis of the limit; the second is an absence
  paragraph, kept with no Search line needed.
- **§7.4** "No acceptance threshold fixed before the test is on record": an absence claim whose "on record" is the
  epistemic content (no record that a threshold existed); "was set" would strengthen it.
- **§9.4 "built before the generator flux was repaired"**: kept as the label of the historical truths (director's
  ruling). §9.2's "uses a mis-sampled flux (§7.6)" also kept.
- **Guardrail keeps**: §8.5 "These are central-value ratios; no compatibility metric is quoted, for the reason given in
  §9.6, item 1" (a different reason from §7's, and a different printed number); §7.8 Ascencio "No pulls or
  full-covariance χ² are reported" (a published covariance exists, so a reader would expect one); §7.3 "not a
  calibrated goodness-of-fit statistic"; §9.3 refinement "which does not establish calibration for every functional";
  §9.3 binned diagnostic scope; every figure caption's own disclaimer apart from the shortened covariance reason.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

## Changes, batch n1-D (§10 `sec_joint.tex`; §11 `sec_fps.tex`)

`sec_fps.tex` is byte-identical to the base. Ledger rows in
`ledger.md` (D* for §10, F* for §11).

## Reverse outline before editing (one line per paragraph)

**§10 intro.** What the section is; design fixed before production with two data-informed elements; hybrid nulls; not
a cross section, no uncertainty, no covariance validation; contents ("pre-registered specification"); where it is
documented ("each later study cites its own record").
**§10.1 sec:joint5d-design.** (1) H0(G), the hybrid null, three distinct requirements (fidelity = (ii)-(iv)). (2) Fine
grid. (3) Coarse 3^5 grid edges. (4) Edge rule, supported cells, GiBUU domain. (5) T_tot, T_sh, metric. (6) Pilot V:
diagonal, shrinkage, power only, other intensities not measured.
**§10.2 sec:joint5d-calibration.** (7) The pseudo-experiment (estimator "chosen before the design was fixed"). (8) MC
p value, claim p, non-central nulls. (9) Generative model; data-derived Delta_b conditioning not validated. Table.
**§10.3 sec:joint5d-frozen.** (10+11, one paragraph) Holm "under the testing assumptions … at most 5%"; determinacy;
batches; stopping; gate; A1, A2; "controls FWER at 5% under these assumptions"; A2 and the lost draws; size averaged.
(12) Fixed before production, two data-informed elements, budget extension ("its predeclared rule"). (13) Independent
recomputation verifies the calculation, not the calibration's adequacy. (14) Three later studies, each specified
before it ran.
**§10.4 sec:joint5d-conditions.** (15) Quoted "from the pre-registered specification". Quote (i)-(vi), with "[a
recorded ruling on the pilot]". (16) Numerical convergence ("predeclared design", "comes from the design review").
(17) Calibration validity: valid to the extent …; recomputation verifies calculation; no rejection rate measured; (iv);
SF-1; margins; rounding. (18) Physical-model adequacy: (ii) surrogate; no recoil band, "completeness not established";
(iii); (v).
**§10.5.** Decisions; Table (caption "predeclared rule"); figure; κ scan ("predeclared direction"); power.
**§10.6 sec:joint5d-lost (Joseph's disposition).** Losses; sensitivity; rerun "under a procedure fixed and independently
reviewed beforehand"; determinism; margins; earlier stops; scope of the checks; disposition paragraph.
**§10.7.** Projections, criterion specified after the 5D outcomes, GENIE muon-only, power not compared.
**§10.8 sec:joint5d-response.** (P1) MINERvA practice; no calorimetric band; how a band would act; net effect
unmeasured; muon-only context; GENIE projection. (P2) ±4% study of "the predeclared tests"; size not validated;
results. Table (nulls not regenerated). (P3) "calibration distributions stay fixed"; what the study measures; "a
response-uncertainty construction would also need to vary the nulls"; untested (a)-(c); rejections conditional.
**§10.9 sec:joint5d-ch.** Intro ("do not re-grade … which stand"); construction; re-evaluated tests ("predeclared
metric"); generation checks ("reported under the label").
**§10.10.** What the tests establish.
**§11.** Intro (preliminary, no covariance); acceptance, extrapolation through the step-1 regressor; battery (control,
closure, envelope, containment); central value; purity; two tiers; no uncertainty beyond the envelope.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

## Changes, per paragraph

| where | before | after | rule | the restatement's home |
|---|---|---|---|---|
| §10 intro | "Their design was fixed before any production pseudo-experiment or observed statistic was computed, with two data-informed elements (§10.3)." | removed | R-N6 (pre-specification once, in §10.3); R-N1 | §10.3, para 2, "The hypotheses, statistics, … were fixed before any production pseudo-experiment or observed statistic, with two data-informed elements." |
| §10 intro | "The section gives the pre-registered specification, with its six conditions in its own words (§10.4), …" | "The section gives the design, the six conditions of the declared model in the words of the test specification (§10.4), …" | R-N6 | — |
| §10 intro | "The specification and the decisions are documented in Ref. [JointTestRecord2026]; each later study cites its own record." | "Reference [JointTestRecord2026] gives the specification and the decisions, and each later study has its own reference, cited where it is described." | R-N6 ("documented in Ref. …; each later study cites its own record") | — |
| §10.2 para 1 | "…31-leaf refinement classifier, chosen before the design was fixed)" | "…31-leaf refinement classifier)" | R-N6 (pre-specification once, in §10.3) | §10.3 para 2, new sentence "The joint-test estimator (§10.2) was chosen before the design was fixed." (also the home the outline names for §3's restatement) |
| §10.3 para 1 | "controlled at familywise level α by the Holm procedure: under the testing assumptions, the probability of falsely rejecting at least one true hypothesis among the ten is at most 5%." … "controls the familywise error rate of the ten decisions at 5% under these assumptions" | "combined by the Holm procedure at familywise level α." … "controls the familywise error rate of the ten decisions, the probability of falsely rejecting at least one true hypothesis among them, at 5% under these assumptions" | R-N1 (calibration assumptions: one statement, in §10.3, where A1 and A2 are defined); R-N4 (the assumption stated as an assumption, once) | same paragraph, the A1/A2 sentence; Search line added |
| §10.3 para 2 | "so that the sequential rule could reach the stop set by its predeclared rule rather than a budget stop." | "so that the sequential rule, rather than the budget, could set the stop." | R-N6 | the paragraph's first sentence |
| §10.3 para 3 | recomputation sentence | + "The calibration is valid for the simulated null to the extent that the pseudo-experiment chain reproduces the analysis applied to the data; no rejection rate has been measured for null pseudo-data processed like the data, which would require an independent simulation sample." (moved, wording kept) | R-N1 (calibration assumptions' home §10.3) | this is now the home; Search line added |
| §10.4 intro | "quoted below from the pre-registered specification" | "quoted below from the test specification" | R-N6 | — |
| §10.4 quote (iii) | "[a recorded ruling on the pilot]" | "[the effect of clipping rather than keeping them, measured on the pilot]" | R-N6 (the bracket gives the file's content, as the intro says brackets do) | source: EXCEPTION-20260927, "Quantified effect" (0.35% of the band's shift in whitened norm); the `%` substitution note updated |
| §10.4 numerical convergence | "The predeclared design takes the step …; this value comes from the design review, and its derivation is not given." | "The design takes the step …; this factor was set when the design was reviewed, and its derivation is not given." | R-N6 (both facts kept: set at the design's review; derivation not given) | Search line added |
| §10.4 calibration validity | "The calibration is valid … ; the independent recomputation verifies the calculation, not whether the chain does so, and no rejection rate has been measured …" | "The calibration's validity, and what the independent recomputation verifies, are stated in §10.3." | R-N1 | §10.3 para 3 (validity, rejection rate) and its recomputation sentence ("it verifies the calculation, not the adequacy of the calibration"); Search line added |
| §10.4 physical-model adequacy | "The analysis has no band for the calorimetric recoil-energy response, so completeness of the hadronic-response model is not established (§10.8)." | "The analysis has no band for the calorimetric recoil-energy response; §10.8 gives the consequences." | R-N1 (recoil omission: one clause at this consequence) | §10.8, "The rejections are therefore conditional on the simulation's hadronic response, and the response model is not shown to be complete."; the quoted condition (ii) also keeps "hadronic-response completeness is not established"; Search line added |
| Table tab:joint5d caption | "at the stop set by the predeclared rule" | "at the stop set by the sequential rule" | R-N6 (caption meaning unchanged: the same rule) | §10.3 |
| §10.5 κ scan | "A scan along the predeclared direction δ_fine" | "A scan along the direction δ_fine of the claim variants" | R-N6 | §10.3 para 4 ("each was specified before it ran: the scan of the shift multiplier"); Search line added |
| §10.6 | "under a procedure fixed and independently reviewed beforehand" | "under a procedure that was fixed, and reviewed independently, before the rerun" | R-N6 (wording; both facts kept, disposition text otherwise unchanged) | — |
| §10.8 P2 | "the predeclared tests are re-evaluated" | "the ten tests are re-evaluated" | R-N6 | §10.3; Search line added |
| §10.8 P3 | "The calibration distributions stay fixed in this study, which measures …" | "The study measures …" | R-N1 | P2 ("re-evaluated against the null distributions used for the decisions") and item (a) ("not regenerated with the variation") |
| §10.8 P3 | "A response-uncertainty construction would also need to vary the null distributions." | removed | R-N1 | P1 ("a band drawn in the calibration would also broaden and could shift each null distribution") |
| §10.8 P3 | "The study leaves untested (a) …" | "It leaves untested (a) …" | (follows from the above) | Search line and a `%` note naming this subsection the one home |
| §10.9 intro | "The re-evaluations are descriptive: they do not re-grade the decisions of Table 12, which stand." | "These target-corrected evaluations are descriptive; the decisions of Table 12 are unchanged." | director's ruling 2026-10-25 (both elements kept); R-N6 | `%` comment cites DECISION-20261020-joseph-nuwro-ch-claim.md:37 |
| §10.9 re-evaluated tests | "Under the predeclared metric" | "With the metric used for the decisions" | R-N6 | §10.1 (the metric), §10.3 |
| §10.9 generation checks | "The GiBUU re-evaluation is reported under the label ``B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its premise passed at ≤0.1σ_c'': the sampling-closure check …" | "For the GiBUU re-evaluation, B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its premise passed at ≤0.1σ_c. That is, the sampling-closure check …" | R-N6; the label's words are kept verbatim (DECISION-20261020:35; mp3c/REPORT.md:7-8 requires the label) | Search line added |
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

## Not changed, with the reason

- **The other recoil-response statements in §10** (inventory 11): quoted condition (ii) (a quotation); §10.8 P1 "no
  calorimetric response band" and "net effect … unmeasured" (the home); P2 "±4% size is not a validated uncertainty
  prescription" (qualifies that study's size); the Table tab:joint5d-recoil caption "not regenerated" (qualifies the
  table's numbers); item (a) and the closing "rejections are therefore conditional" (the home); §10.10's "remain
  outside any validated uncertainty bound" (the section's reading; it also carries the sub-fine-grid residual).
  Result: three restatements removed or reduced to a pointer clause; the omission now prints once as a fact in §10.8
  P1, with its consequence once at the end of §10.8.
- **Calibration assumptions** (inventory 7): §10.1 "calibration fidelity (conditions (ii)-(iv))" defines the term;
  §10.2 "conditional on these data-derived inputs …; not validated" is a distinct assumption at the place the Delta_b
  are described. Both kept (guardrail).
- **§10.6 (Joseph's disposition):** only the "independently reviewed beforehand" sentence changed. "A determinism check
  fixed in advance" and "the predeclared rule would have stopped" stay.
- **§10.7:** "The comparison and its criterion were specified after … but before the comparison was run" stays: it is
  the deviation's account at the result it qualifies (R-N3).
- **§11 (`sec_fps.tex`), byte-identical.** The six prior-dominance statements are: tier 2 and the two-tier
  interpretation (the home, §11.3); the §11.1 extrapolation clause, which qualifies the sentence before it ("already
  corrects for acceptance" is false as read in the dead cells without it); the envelope item's own numbers (2.9%, 7.9%,
  P90 62%); and two figure captions (27.7% of the truth rate; the few-percent/tens-of-percent caption), whose meaning
  is protected. The home already is single; nothing could be removed without breaking the guardrail or a caption.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

## Changes, batch n1-E (App. A–D)

Base `ddf16f10`. Ledger rows are in brackets.

## Reverse outline of the touched paragraphs (one sentence each, before the edit)

- **App. A §sec:chisq, limit (iii):** the distance says nothing about coverage; the only 2D coverage test scored an
  earlier band and found tail undercoverage; nothing validates this covariance's intervals.
- **App. A, standing assumption 3:** the same-ensemble check tests Gaussianity only; the first-built band undercovered
  and was rebuilt; the rebuilt band and the quoted block are untested.
- **App. B §sec:nd-declarations, the declarations paragraph:** an N-D chi-square must state five declarations; the
  records hold the measurements, the derivation and the "predeclared rank cut".
- **App. B §sec:gbdt-diagnostic-definitions, the data-sensitivity paragraph:** the envelope and the reductions'
  bookkeeping; the analyst cross-checked them, and no independent review is claimed.
- **App. C §sec:negweight-footing, the purity-choice paragraph:** purity is a recorded choice, on two grounds; it
  carries an obligation to revisit before submission; the 2D revisit is done, and 5D still uses purity.
- **App. C, "Purity bias":** the within-bin shape term is measurable and is evidence for that obligation.
- **App. C, "Refined negative-weight subtraction":** refinement reduces the bias but fails closure; no coverage test;
  the obligation remains open.
- **App. C, "Background treatment and choice of covariance":** the two choices are independent; the five-axis
  covariance is used under an exception; the background choice removes one blocking decision.
- **App. D, the reconstruction-only paragraph:** the protocol perturbs reconstructed E_avail only; both signs run at a
  pre-fixed amplitude.
- **App. D, "Physically correlated follow-up":** the arm is deferred unless there is a material bias or a collaboration
  request.
- **App. D, "Status and interpretation":** a protocol, not a result; a large bias triggers a decision and would not be
  silently absorbed.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

## Per paragraph

### App. A, limit (iii) (`app_statmethods.tex`, §sec:chisq) [E1]
- **Before:** "The only 2D coverage test, the fixed-truth test of §5.2, scored an earlier statistical band alone and
  found it undercovering in its tails."
- **After:** "The only 2D coverage test, the fixed-truth test of §5.2, scored an earlier statistical band alone."
- **Rule:** R-N2 (the earlier band's history is told once, at §5.2), R-N1.
- **Home:** §5.2 (sec:coverage): "The band fails: it undercovers in its tails"; check-bound "lies entirely below its
  window (Gaussian 0.954)".
- **Guardrail:** the labels "only", "earlier" and "alone" stay, because without them the sentence would imply that
  this covariance was tested. A `% Search:` line was added (absence claim).

### App. A, standing assumption 3 (`app_statmethods.tex`, §sec:assemble) [E2, E3]
- **Before:** "The fixed-truth test (§5.2) found the diagonal of the first-built C^stat undercovering in its tails
  (C_2 = 0.912, unevenly across bins); the band was rebuilt in response, and the rebuilt band has not been
  independently re-tested. The statistical block quoted here is a different ensemble and has not been tested either."
- **After:** "The statistical block quoted here is a different ensemble from the earlier bands scored by the
  fixed-truth test and its rescoring (§5.2), and it has not been tested."
- **Rule:** R-N2.
- **Home:** §5.2. It prints the tail failure, "Uneven in both directions", "The band was then rebuilt without this
  term" and "The rebuilt band was only rescored post hoc". C_2 = `\covTwoDCTwo` also still prints in App. A's own
  audit-trail table, labelled "Earlier statistical band".
- **Guardrail:** the untested status of the quoted block stays here, because it qualifies this assumption. A
  `% Search:` line was added.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

### App. B, N-D declarations (`app_statmethods_nd.tex`) [E4]
- **Before:** "Measurements, derivation and predeclared rank cut are in Ref. [41] (rank-inversion)."
- **After:** "The measurements, the derivation and the requirement that N-D difference statistics use a rank cut fixed
  independently of the data are in Ref. [41] (rank-inversion)."
- **Rule:** R-N6.
- **Not done as written:** the outline asked for the cut "stated as its value". The records hold no value: the
  `rank-inversion` entry (`app_provenance.tex:73-74`), `RANK-AND-INVERSION-20260810.md` §5 ("does not choose the cut")
  and `docs/STATVAL_REPAIR.md` ("PREDECLARED rank/pseudoinverse cut") all give a requirement, not a number. The
  requirement is therefore stated in physics terms (a data-independent cut, the property that line 53 of the same
  appendix says the standard debiasing factor assumes). A `%` comment records this.

### App. B, scalar-5D reductions (`app_statmethods_nd.tex`) [E5]
- **Before:** "The analyst cross-checked the reductions numerically; no new independent scientific review of the
  synthesis is claimed."
- **After:** "The analyst cross-checked the reductions numerically."
- **Rule:** R-N6. The outline removes the clause because it has no scientific content. Nothing claims an independent
  review, so leaving it out makes no sentence false.

### App. C, purity choice and the revisit status (`app_negweight.tex`, §sec:negweight-footing) [E6, E7, E8]
- **Before:** "Purity is **a recorded choice, not a silent default** (Ref. [41], oi6-oi8-oi126), made on two
  grounds. … This consequence, not the computing cost, decided the choice. The choice carries an obligation to
  revisit the background treatment before submission. In two dimensions, the closure test below is the revisit's
  result, and the 2D result and its covariance now use the refined estimator; the five-dimensional central value
  still uses purity."
- **After:** "The standard chain uses purity by choice, on two grounds (Ref. [41], oi6-oi8-oi126). … This consequence,
  not the computing cost, decided the choice. The background treatment has been revisited in two dimensions: the
  closure test below is the result, and the 2D result and its covariance use the refined estimator. For the
  five-dimensional central value, which still uses purity, the revisit is open."
- **Rule:** the director's ruling of 2026-10-25 (the status is stated once, here, split by result; "before submission"
  is dropped; a `%` comment names the source) and R-N6 ("a recorded choice, not a silent default" becomes the choice
  with its basis; the two grounds follow unchanged).
- **Home:** this paragraph is the home.
- **Comment:** the RE-2 W7 comment was merged into a new comment that names the ruling and keeps every earlier
  source: DECISION-20261024 adopt-re2 item 1, DECISION-20261023 (second) item 2, W7 approval, 5D-route item 5.

### App. C, "Purity bias" [E9]
- **Before:** "…direct evidence for the obligation of §C.6 to revisit the background treatment before submission."
- **After:** "…direct evidence for revisiting the five-dimensional background treatment (§C.6)."
- **Rule:** the ruling (point to the home), R-N6.

### App. C, "Refined negative-weight subtraction" [E10]
- **Before:** "The obligation to revisit the background treatment therefore remains open; reducing one bias does not
  itself qualify an uncertainty."
- **After:** "Reducing one bias does not itself qualify an uncertainty, so this result does not close the revisit of
  the five-dimensional background treatment (§C.6)."
- **Rule:** the ruling (point to the home), R-N6.
- **Note:** "No coverage test was run" is unchanged. A `% Search:` line was added.
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

### App. C, "Background treatment and choice of covariance" [E11, E12]
- **Before:** "…and that five-axis covariance is used under an exception limited to the file with its checksum
  (§9.6); neither fact follows from this appendix, and the appendix needs neither. The choice of background treatment
  removes one blocking decision and leaves every other precondition for using a component in place."
- **After:** "…used in this note. That five-axis covariance is used although it does not meet the acceptance criteria
  of its specification, and the use covers only this file and its projection (§9.6). Neither fact follows from this
  appendix, and the appendix needs neither. The choice of background treatment settles one of the conditions for using
  a component; every other condition still applies."
- **Rule:** R-N6 (the exception as plain status, as the outline proposes for §9), R10 (one sentence becomes three).
- **Home:** §9.6 (sec:eavailw-adopted): "The covariance does not meet the acceptance criteria of its specification"
  and "It is used under an exception that covers only this file and its projection".

### App. D, the reconstruction-only test [E13]
- **Before:** "Both signs of ε must run at an amplitude fixed before inspecting results."
- **After:** "Both signs of ε must run, at an amplitude that is set independently of the outputs."
- **Rule:** R-N6 (the protocol in physics terms).

### App. D, the physically correlated follow-up [E14]
- **Before:** "…or the collaboration requests the stronger model."
- **After:** "…or the stronger response model is otherwise required."
- **Rule:** R-N6. This is an open question (see the report).

### App. D, status and interpretation [E15]
- **Before:** "A large bias would trigger a model/uncertainty decision and would not be silently absorbed as a
  non-closure error."
- **After:** "A large bias would call for a change to the response model or an explicit uncertainty component, rather
  than being absorbed into a non-closure error."
- **Rule:** R-N6.
- **Unchanged:** the protocol status: the title "(protocol implemented; not yet run)", "No response-mismatch output
  has been produced and no pass threshold has been set". A `% Search:` line was added.

## Changes, batch n1-A (executive summary `sec_execsummary.tex`, §1 `sec_intro.tex`, §12 `sec_summary.tex`)

Base `ddf16f10`. Ledger rows in `ledger.md` (A* executive summary, I* §1, S* §12). Labels, headings referenced elsewhere,
numbers, macros, the table and its caption are unchanged. `main_note.tex` (abstract) and `result_status_rows.tex` are
byte-identical to the base.

## Reverse outline before editing (one line per paragraph)

**Executive summary.** Opening (OmniFold on ME data; main results are validation findings, scope; tests an
application) | Results overview: Reproduction | 3D/4D/5D unfolds | Low-E_avail (descriptive; FSI/Valencia caveat) |
High-E_avail, high-W (map, no mechanism, covariance status) | Joint tests (conditions, calibration, margins, no
exclusions, no recoil band, robustness variant, lost draws, CH, "hypothesis tests") | Methodological finding |
Extended fiducial | PET future work | Table and caption | *What is not claimed*: Coverage (2D bands; 5D miscoverage)
| Regularization bias (+ background treatment, 2D closure, no 5D comparison) | Estimator stability | Mechanism | 5D
measurement | 5D covariance | Extended fiducial | PET.
**§1.** MINERvA | the publication and OmniFold | unbinned methods | prior applications | background practice | Huang et
al. and what differs | Why unbinned | Analysis strategy (ends with PET) | Roadmap.
**§12.** Summary lead (scope) | 2D bullet (+ coverage restatement) | higher-dim bullet (+ descriptive, no mechanism,
W redundancy) | background and 5D bullet (+ configurations, no 5D comparison, regularization bias, 10% criterion,
miscoverage, covariance) | joint-test bullet ("specified in advance", recoil band, "recorded decisions") | PET bullet |
Outlook (fps; PET; 5D measurement and covariance status; NEUT; flux posterior) | Reusing the result.

## Per paragraph

| where | before | after | rule | the restatement's home |
|---|---|---|---|---|
| ES opening | "…which hold for this implementation and for the configurations, observables and deformations tested; the generator tests are…" | "…within the scope stated in §1: this implementation, one data set, and the configurations, observables and deformations tested. The generator tests are…" | R-N5 (the ES's single restatement of §1) | §1 "Scope" |
| ES Low-E_avail | "Comparisons with the tested pion-FSI dials and with Valencia 2p2h [cites] use central values without uncertainties and do not identify a nuclear mechanism (§7.7, Fig.)." | "The comparisons with the tested pion-FSI dials and with Valencia 2p2h [cites] are in §7.7 (Fig.)." (citations and pointers kept) | R-N1 | §7 lead; one clause in Principal limitations |
| ES High-E_avail | "The map shows where…; it does not locate an interaction mechanism." and "The comparison uses central values only: the projection's covariance is used … although it has not passed …, and the estimator-seed sensitivity … exceeds the limit set before production (§9.6)." | both removed | R-N1 | §7 lead; §9.6 (sec:eavailw-adopted); one clause each in Principal limitations |
| ES Joint tests | "…reject as well (§10.7), and the nuisance model has no calorimetric recoil-response band (§10.8)." | "…reject as well (§10.7)." | R-N1 | §10.8; Principal limitations |
| ES Joint tests | "in this descriptive re-evaluation, which leaves the recorded decisions standing, NuWro's total-test rejection is not robust to the correction (§10.9). These are hypothesis tests, not a measured uncertainty (§10)." | "in this descriptive re-evaluation, NuWro's total-test rejection is not robust to the correction, and the ten decisions are unchanged (§10.9)." | R-N6; DECISION-20261020 line 37 (both elements kept, as in §10.9) | "hypothesis tests": §1 Scope and the §10 lead ("add no reportable uncertainty") |
| ES PET item | "Future work: point-cloud representations. Point-cloud (PET) unfolding of the full event is under development and documented separately (App. F); no result in this note depends on it." | removed | R-N5 | §1 Scope (all three facts) |
| ES "What is not claimed" (8 items, 27 inventory statements) | the list | **"Principal limitations:"**, one paragraph, one clause per home: the quoted 2D block's untested coverage (§4.2, §5.2); descriptive central-value comparisons, no mechanism, no 3D/4D covariance (§7); no quoted uncertainty includes the residual regularization bias (74% at highest W, §9.3) or the 4% purity bias the 5D central value keeps (§9.2); above 2D, central values without intervals of validated coverage: no 5D measurement (§9.4), no frequentist coverage, the one test of bias-corrected statistical intervals miscovered (§9.5); the one 5D covariance fails its specification's acceptance criteria and four measurements limit it (§9.6); calibration valid for the simulated null to the extent the chain reproduces the analysis of the data (§10.3); no calorimetric recoil band (§10.8); tier 2 prior-dominated (§11); PET future work (§1) | S1; R-N1; model: paper_body.tex sec:limitations | each removed fact has an N: probe at its home (rows A09–A33). The former items' source comments are gathered in one comment; a Search line names the home of each absence claim. |
| ES line 153 (base) | "fails the predeclared data-stability test" | the item is removed with the list | R-N6 | §9.3: "fails the data-stability test, whose criterion was set before it was run" |
| ES line 159 (base) | "Mechanism" item | removed with the list | R-N1 | §7 lead; §7.7 ("other transport models or proton-FSI effects are not excluded") |
| ES table caption | unchanged ("Point-cloud (PET) studies are future work and contribute no result here.") | — | caption meaning protected | — |
| §1 Analysis strategy | "…probes an alternative signal definition. Point-cloud (PET) representations are future work (App. F)." | the PET sentence moves to Scope | R-N5 | §1 Scope |
| §1 new paragraph "Scope." | — | "The results hold for one implementation of unbinned OmniFold, applied to one data set, and for the configurations, observables and deformations tested. The two-dimensional result has an uncertainty budget whose coverage has not been tested (§5.2); above two dimensions the results are central values without intervals of validated coverage (§§7–9). The generator tests of §10 test hybrid null hypotheses and add no reportable uncertainty. Point-cloud (PET) unfolding of the full event is future work, under development and documented separately (App. F); no result in this note depends on it." With a Search line. | R-N5 (the single statement) | this is the home |
| §1 Roadmap | "2D covariance blocks and the limitations of their construction & §4; §4.4" | "… & §4; limitations §4.4, §4.6" | known pointer fix (earlier-budget defects now in §4.6, "Changes from the earlier 2D budget") | — |
| §12 lead | "…which hold for this implementation and for the configurations, observables and deformations tested;…" | "…within the scope stated in §1;…" | R-N5 | §1 Scope |
| §12 2D bullet | "In the fixed-truth coverage test, the statistical band then quoted undercovers in its tails; a rebuilt band was rescored only post hoc…, and the quoted statistical block has not been tested (§5.2)." | removed | S2; R-N2 | §5.2; Principal limitations |
| §12 higher-dim bullet | "The five are simultaneous, not independent, observables: reconstructed W is fixed by (pT, p∥, q3) (§8.2)."; "The central values, read descriptively, lie above…"; "These comparisons locate no interaction mechanism." | the first and third removed; "read descriptively" removed | S2; R-N1 | §8.2 (and the ES item); §7 lead; Principal limitations |
| §12 background/5D bullet | purity bias; "The refined negative-weight subtraction that largely removes it is the background treatment of estimator configurations (d) and (e) …, which give validation studies of §§9.2–9.4 and the generator tests; configuration (e) also gives …"; 2D closure; "No full five-dimensional comparison …"; the 5D estimator's partial recovery; envelope and 10% criterion; miscoverage; the covariance's seed sensitivity | purity bias, "the refined negative-weight subtraction largely removes it", and the 2D closure sentence (unchanged, now ending with "(App. C)"); the configuration list, the 5D comparison and the envelope go to their homes; the 5D estimator and covariance sentences move to Principal limitations | S2; R-N1; R-N6 ("predeclared") | Table 3 and App. C "Scope of the numbers"; App. C "Limits of the five-dimensional evidence"; §9.3–§9.6 |
| §12 joint-test bullet | "joint tests specified in advance and calibrated …"; "…depend on a nuisance model without a calorimetric recoil-response band, and provide no new uncertainty on the cross section. In a descriptive re-evaluation that leaves the recorded decisions standing, NuWro's …" | "joint tests whose design was fixed, apart from two data-informed elements, before any production pseudo-experiment or observed statistic (§10.3), calibrated …"; the recoil band to Principal limitations; "no new uncertainty" removed; "In a descriptive re-evaluation, NuWro's … to CH, and the ten decisions are unchanged" | R-N6 (pre-specification stated once in the summaries, as the body's property, with its home and its qualifier); DECISION-20261020 line 37 | §10.3; §1 Scope and §10 lead |
| §12 PET bullet | "Point-cloud (PET) representations of the full event are future work (App. F); no result here depends on them." | removed | R-N5 | §1 Scope |
| §12 new paragraph "Principal limitations." | — | one clause per principal limitation, with its home: the quoted 2D block (§4.2, §5.2); descriptive comparisons, no mechanism, no 3D/4D covariance (§7); partial recovery and regularization bias in no quoted uncertainty (§9.3); above 2D central values without validated-coverage intervals: no 5D measurement (§9.4), statistical intervals miscover (§9.5); the one covariance fails its acceptance criteria and its companions' seed sensitivity exceeds the limit, so no covariance-based significance (§9.6); calibration validity (§10.3); no recoil band (§10.8). Sources of the former Outlook sentence moved with it. Search line. | S2; R-N1 | each clause has its home's N: probe |
| §12 Outlook | "Full-event point-cloud (PET) unfolding is under development as future work (App. F)."; "No five-dimensional measurement with total uncertainties that meet the criteria set in advance was obtained, within the study's rules and budget (§9.4), and the scalar five-dimensional covariance …, built with re-selected lateral bands, has not passed its specification's acceptance criteria (§9.6)." | both removed; "separately labeled prior-dominated extrapolation contributes about 28%" stays (so the tier-2 clause is not repeated in the §12 limitations) | R-N5; S2; R-N6 ("set in advance") | §1 Scope; Principal limitations; §9.4 (budget limit), §9.6 (re-selected laterals, "Construction") |
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

## Not changed, deliberately (guardrail)

- ES 3D/4D item: "neither has an acceptance threshold recorded in advance" qualifies the printed 0.10 and 1.1 %, and
  "recorded" is its epistemic content (n1-C kept the body's "on record" for the same reason). §12 keeps "with no
  acceptance threshold recorded in advance" for the same numbers.
- ES joint item: "under six stated conditions", "under the stated calibration assumptions", "the size averaged over
  the nuisance priors", the robustness variant ("that residual is unmeasured") and the lost-draw sentence. Each
  qualifies the printed rejection or its margins.
- ES and §12: "a cross-configuration comparison" / "across configurations" (qualifies 0.141 %); "this region carries
  the largest regularization bias"; the uncorrected carbon-versus-CH difference (qualifies "fall below the data");
  "LightGBM was chosen … after both comparisons with the publication were known" (R-P4 disclosure at the result; the
  b8 B2 lesson); the χ² "descriptive distance whose source has not been identified".
- "the limit set before production" (§9.6's movement limit): the basis of the limit, kept as the body keeps it.
- The table caption's PET sentence: caption meaning is protected.
- §12 "Reusing the unbinned result" (release text) and the roadmap rows bound by `records-move-ledger.md` (L11).
<!-- absence-ok: quotes or summarizes the note's own text, before or after this round, as the round's record; not a new absence claim -->

## Review fixes applied after the batch writers (two-direction review, four reviewers)

Each fix restores base wording or a home's wording; none adds a fact. Ledger rows were updated to match.

**§3–§9 (batches n1-B, n1-C):**
- **BLOCKING, §4.2** (SY-6). The held-out sentence had become "no design for one has been specified". That is false:
  a held-out design exists as an unregistered draft. The base wording "registered in advance" is restored.
- **§9.6** (C33). "Covers only" is restored: "the use covers only them, not any other covariance built to the same
  specification…" (DECISION-20260920 §3).
- **§4.6** (SY-D3b). An unsupported pointer to `sec:uq-2d-construction` is removed from "does not have this mismatch".
- **§7 and §8** (C06, C14, guardrail). "In central values" is restored beside the printed 52% and 63% and in the §8 lead
  sentence.
- **NITs:**
  - **§7.x** (C03). "No 3D covariance is quoted (§7); the one that would be quoted is …" now gives "would be quoted" an
    antecedent.
  - **§9.2** (C21). The pointer to `sec:val-departure` is now its own sentence.
  - **§9.4** (C27). "The study's selection procedure permits" is restored.
  - **Source comments:** the `FrInel_pi` footnote gets a comment naming its source
    (`docs/COLLABORATOR_QUESTIONS.md`, 2026-08-02). The §3 KI-93 comment is updated.

**§10–§11, App. A–D (batches n1-D, n1-E):**
- **BLOCKING, App. D** (E13). "Independently of the outputs" is restored as the base's timing condition: "fixed before
  the results are examined".
- **App. D** (E14, E15):
  - "or the collaboration asks for the stronger response model" is restored;
  - "would require a decision on the response model or an uncertainty component, and would not be absorbed silently
    into a non-closure error" is restored.
- **§10.3:**
  - (D5) "carried out with the Holm procedure" replaces "combined by";
  - the estimator-timing sentence moves to open the pre-specification paragraph, off the "two data-informed
    elements" slot;
  - (D16) "this factor comes from the review of the design" is restored.
- **§10.9** (D37). The GiBUU label is quoted as a label again, with the base framing (mp3c/REPORT.md:7).
- **App. B and App. C:**
  - (E4) "fixed in advance" replaces "independently of the data";
  - (E8, E11) "its result" and "that file".
- **App. A** (E1–E3): the fixes were made, but the file is not adopted (piece N11 lost P2N), so they are not in the note.

**Executive summary, §1, §12 (batch n1-A):**
- **BLOCKING** (A02, S03). The new limitation "The generator comparisons are descriptive …" is scoped to §§7–8.
  Unscoped, it took in §6.5's χ² and the calibrated joint tests. "Nuclear or interaction" is restored in §12.
- **§12** (S13). The design-timing clause follows its home's structure: "fixed before any production pseudo-experiment
  or observed statistic, with two data-informed elements".
- **Executive summary and §12** (A11, S10). The coverage-test clause keeps "of a deterministic estimator variant".
- **NITs:**
  - (A01) the scope sentence;
  - (A20) the 4% purity bias keeps its closure-test condition;
  - (A04) the covariance "with its $(E_{\rm avail},W)$ projection";
  - (I02) the §1 pointers to §4.2 and §4.6;
  - (A07) "evaluate hybrid null hypotheses";
  - §12's lead sentence, so it is not printed twice.

## Batch n1-F (director's addendum): process words

- **NF1.** "(corrected for audit finding J28)" is dropped. "Flux-corrected" is the glossary term.
- **NF2.** "Predeclared nominal closure criterion" becomes the criterion, stated from its contract (s5n C3 and C6). The
  result is a failure, so timing is not stated.
- **NF3.** "The predeclared design defines containment" becomes "Containment, as defined before the study ran,
  requires a median consistency ratio …". The timing is kept because it qualifies a pass (s5p amendment 2, FROZEN
  before any Stage-2 compute).
- **NF4.** "Decision gate" becomes "decision rule uses the upper end …"; "passing this gate" becomes "the probability that
  this upper end falls below the threshold"; the flowchart box's "gate" becomes "interval".
- **NF5, NF6.** §10.3 is retitled "Multiplicity, stopping rule and design", and §10.9 "Hydrocarbon target correction
  for NuWro and GiBUU". The labels are unchanged, and every reference prints a number.

The n1-F review found two BLOCKING problems, both fixed before adoption:
- in NF2, the 153 are "reported quantities", not all integrals, and σ is each quantity's bootstrap σ;
- in NF4, "95% … bound" read as one-sided.

## Outside the batch files

- **`app_provenance.tex`** (records): not changed. The `rvp1pi` row's pointer edit fails `check_note_records.py probe` P5,
  which keeps every base record paragraph verbatim. Per the director's ruling it lands in the next PR, with R-EDIT ledger
  rows.
- **`records-move-ledger.md`.** 14 probe repoints across 15 rows (L-thin-C07, C12, C13, C31, C35–C38, C41, C48, C58,
  C60, C63, C70) follow the new body wording. `check_note_records.py probe` gives RECORDS-MOVE PASS with 0 failures.

## Not adopted

- **App. A (`app_statmethods.tex`).** Piece N11 lost P2N (NEW 1 of 4), so the file keeps its base text; the n1-E changes
  to App. A above (rows E1–E3) and the review fixes to them are not in the note. Its pointers were re-checked against
  the new body: each lands on text that supports it (§4.1 PPFX rank 1; §3 `sec:method-config` exact-split history;
  §4.5 `sec:uq-combine`, unchanged; §5.2 and §5.3).
