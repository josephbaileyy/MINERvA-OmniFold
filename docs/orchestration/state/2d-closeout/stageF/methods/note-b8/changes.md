# Changes, batch b8 (before -> after -> reason), per paragraph

Full diff: `b8.diff`. Ids from `outline-before.md`; ledger rows in `ledger.md`.

## Abstract
- A1: "An independent unfolding method reproduces the integral ... and reproduces its uncertainty scale" -> "Unfolded
  independently of the publication, the ... cross section ... reproduces the published integral ..., and its
  uncertainty is comparable in size to the published one." Reason: the subject was the method, not the result;
  "comparable" is the body's word (sec_results "comparable to the published total").
- A2: "...with its universe and statistical blocks at the central value's training seed; whether it describes the
  central value has not been measured." -> "..., and it has not been independently validated." Reason: states the
  body's status (sec_systematics, "Status of the 2D result") instead of an unmeasured-quantity hedge.
- A4: one 75-word sentence split into four: low-Eavail deficit; excess over the tune with its three qualifiers; the
  external generators with the GiBUU and C-vs-CH qualifiers; no mechanism. "there" now has one antecedent.
- A5: "that treatment is used only for the generator tests, and the central values keep the purity subtraction ..."
  -> "The quoted central values and uncertainties use the purity subtraction, a choice still to be revisited, and
  keep its bias ...; the negative-weight treatment is used in the generator tests and in some five-dimensional
  validation studies." Reasons: (i) "only for the generator tests" was incomplete (configurations (d), (e) of
  Table 3 give §9.2-9.4 studies; director correction); (ii) item 3: the background choice must not read as settled
  (App. C.6: obligation not met).
- A6: "Coverage and estimator-seed studies show further limitations: statistical intervals miscover ..." -> "Statistical
  intervals miscover at the tested truths, and ..." Reason: editorial lead-in; it named a seed finding it did not
  state (ledger AB19).
- A8: five sentences of stacked caveats -> three: the rejection with both of its conditions (six stated conditions;
  5% FWER under the calibration assumptions); known discrepancies and not exclusions; the three limits (no gain over
  matched projections, no recoil-response uncertainty, fine-grid convergence not shown); NuWro CH. "These tests are
  valid only under stated conditions" folded into "under six stated conditions". "do not demonstrate discriminating
  power beyond" -> "show no evidence of discrimination beyond" (the body's and the paper's wording).

## Executive summary
- E0: framing sentence reordered (main results first); scope kept.
- E1: "separately reconstructed" -> "separately constructed"; "the quoted central value was changed to it from an
  exact-split estimator, now a cross-check, after both comparisons ... were known" -> "share the LightGBM estimator,
  which was chosen after both comparisons ... were known; the exact-split estimator is a cross-check". Reason:
  history narrative restated once as a fact about the result; the disclosure is kept. "whose source is not
  identified" -> "has not been identified" (paper wording).
- E2: parenthetical numbers turned into the sentence ("leave 0.10 ... and close q3 to 1.1%; neither has an acceptance
  threshold recorded in advance"); the 135 MeV clause made its own sentence.
- E3: minor ("are central-value comparisons without uncertainties" -> "use central values without uncertainties").
- E4: three semicolon-joined clauses split; the covariance sentence now leads with the consequence ("The comparison
  uses central values only:") and keeps "measured on two companion covariances".
- E5: "there is no calorimetric recoil-response band" -> "the nuisance model has no ..."; "Pseudo-experiments lost to
  time limits were all rerun and observed afterwards, outside the decisions; none changes a decision" -> "... were
  rerun afterwards, for reporting only, and no recovered draw changes a decision (§10.6)" (rated PROC/HEDGE; the
  body's terms). CH clause: "descriptive re-evaluation, which leaves the recorded decisions standing" added
  (item 1: the hydrocarbon re-evaluations are descriptive, sec:joint5d-ch).
- E6: "reporting the joint mean shift separately" -> "stores ... separately" (body: "stored separately").
- E9 (caption): "how each uncertainty is built, what it has been tested against, and how far each result may be
  interpreted are distinct" -> "for each, the central estimator, the construction of its uncertainty, the recovery and
  interval checks applied, and the interpretation it supports" (says what the four columns are).
- E10: "a rebuilt band has not been re-tested independently" -> "was rescored only post hoc, on the same
  pseudo-experiments" (the body's fact); "the statistical block quoted now, a different ensemble" -> "the quoted
  statistical block, a third ensemble" (body: "a third, different ensemble").
- E11: one sentence with four trailing qualifiers -> three sentences; every qualifier kept.
- E12: "missing by up to 74%" -> "with residuals of up to 74%" (body wording); "the refinement is used only for the
  generator tests" -> "It enters only estimator configurations (d) and (e) of Table 3, which give validation studies of
  §§9.2-9.4 and the generator tests" (director correction: Table 3, not App. C's sentence); added "the obligation to
  revisit that choice of background treatment before submission has not been met (App. C.6)" (item 3).
- E13: "failed the data-stability criterion set in advance, as does its baseline: they shift by up to 2.6" -> "fails
  the predeclared data-stability test: ... its results ... by up to 2.6 ..., and those of the baseline estimator by up
  to 2.5" (the body gives 2.5 for the baseline and does not grade it); "the refit-per-replica data bootstrap" -> "The
  candidate's refit-per-replica data bootstrap" (sec_5d: the containment holds for this candidate only).
- E15: the 50-word sentence reordered: "No five-dimensional measurement with total uncertainties was constructed"
  (added from §9.4); the criterion sentence; the envelope as a sensitivity diagnostic.
- E16: "Four measurements, led by ..., limit every result" -> "Four measured limitations apply to every result ...,
  the first ...".
- E17: "is separately reported prior-dominated extrapolation" -> "is prior-dominated extrapolation, reported
  separately".

## §1
- I1: "MINERvA aims to measure ... precisely" -> "MINERvA measures"; "cleanly" -> "well"; "We use" -> "This analysis
  uses".
- I4: "several of the practices audited there appear in our uncertainty budget (...)" -> "three of the practices it
  audits appear ...: ..." (the list has three).
- I6: "Two of its findings shape expectations" -> "bear on"; em-dash clause tidied; "a complete 2D uncertainty budget
  built with the central value's own learner" -> "a 2D uncertainty budget whose blocks are all built with the central
  value's own learner" ("complete" was false as read: sec:systematics lists what the covariance omits).
- I7: bullets tightened; "deliberate" dropped; "quantifies the result's method-dependence" -> "probes" (weaker).
- I8: order follows the note (2D, extensions and their tests, §9-§10, §11, PET); the 2D validation range §§2-5 ->
  §§2-6 (the published comparison and the budget-size comparison are §6).
- I9: heading "Where to find it." -> "Roadmap."; the meta lead rewritten (rated BOOK/META); "open issues in how they
  are built" -> "limitations of their construction"; "its four measurements" -> "its four measured limitations";
  rows for App. D and App. E added (item 2: every appendix of the posted note now has a row; G, H and the records row
  unchanged, as records-move-ledger L11 requires).

## §11
- F1: lead reordered: what the section gives; the signal and domain; then the covariance limitation.
- F2: "Because OmniFold's miss treatment corrects acceptance natively, removing ... is a configurational change: an
  event-loop switch enlarges the truth denominator from 32.8M to 49M ..." -> "OmniFold's treatment of events that
  fail reconstruction already corrects for acceptance, so removing ... is a change of configuration only: the truth
  denominator grows from 32.8 million to 49 million events ..." (rated CODE/JARG); "the validation tests quantify the
  prior cost" -> "quantify the resulting prior dependence".
- F3 caption: "dies in" -> "falls to zero in".
- F4: "Four results establish the extension" -> "Four tests characterize the extension" (weaker; no covariance).
- F5: "so opening the phase space does not damage the measurement where it was already made" -> "opening the phase
  space leaves the result in the published region unchanged at this level".
- F6: "without bookkeeping or normalization bias" -> "with no event-accounting or normalization bias".
- F7: "Their mis-sampled flux" (antecedent: NuWro events) -> "The sample's mis-sampled flux ... this prior was not
  rebuilt after the flux repair".
- F8: "This probes ... not the full quoted band" -> "The diagnostic probes ... not a full uncertainty band" (no band is
  quoted for this domain).
- F11: the purity clause moved out of the equation's lead-in into its own sentence, with App. C's "no extended-fiducial
  production with refined negative-weight subtraction has been run" (item 3); tier 1 rewritten so the ~6% attaches to
  the extension; "the extended-domain covariance has not been constructed" -> "no extended-domain covariance has been
  constructed".

## §12
- S0: as E0; the pointer "(\S\ref{sec:execsummary})" printed "(§)" because the executive summary is unnumbered (base
  defect); it is now "(p.~\pageref{sec:execsummary})".
- S1: estimator sentence as E1; coverage clause as E10.
- S2: one 140-word sentence split. "they lie above all four external generators at low Eavail" -> "lie above all four
  truth-level generators of §7.6 in the quasielastic-Δ dip" (false as read: the four at low Eavail include Tune v1 and
  exclude GENIE+MEC, and in the lowest bin GiBUU reaches the data).
- S3: purity scope as E12 (configurations (d), (e); quoted central values and uncertainties); the obligation sentence
  added (item 3); the envelope sentence ("is such that") rewritten; the miscoverage sentence split. "The one five-axis
  covariance used in this note has an estimator-seed sensitivity above the limit" -> "For the one five-dimensional
  covariance used in this note, two companion covariances built at different estimator seeds show a seed sensitivity
  above the limit" (false as read: the criterion has not been computed for this file, sec:eavailw-adopted).
- S4: CH clause as E5.
- S6: the outlook's repeat of the 10% criterion collapsed into S3; the two remaining facts kept in one sentence;
  "a fifth generator, NEUT, and a finer 44-cell Ascencio comparison" -> "a fifth external generator, NEUT, and a finer
  44-cell comparison with the Ascencio et al. measurement".
- S7: "App. G specifies this release for our analysis. It records which objects have fixed identities today and which
  do not exist yet. A local candidate data package, with checksums and a script ..., exists (App. G), but no release
  ...; rebuilding the documents reproduces no result here." -> "App. G specifies this release ..., including which of
  its objects already have fixed identities and which are still to be produced. A local release candidate, with
  checksums and a verifier ..., exists, but **no release has been tagged or deposited**; rebuilding this note's PDFs
  assembles documents and reproduces no scientific result (App. G)." The bold disclosure is verbatim; the rest uses
  App. G's own wording. "do not affect the choice of covariance, which was made separately" -> "have no bearing on the
  choice of covariance".

## Round 2 (REVIEW.md, ADOPT-AFTER-FIXES)
- B1 `sec_execsummary.tex:153`: "..., so the instability belongs to the estimator family. The candidate's
  refit-per-replica data bootstrap already contains this rounding spread (about 37% of its variance), and central
  values are reproducible only to that size (§9.3)." The baseline's 2.5 is kept.
- B2 `main_note.tex:58`: "With this method, the double-differential cross section ... reproduces the published
  integral ..." (no claim of independence).
- S1: the bias belongs to the central values only (§9.2: it enters no quoted covariance).
  - `main_note.tex:93-95`: "The quoted central values and uncertainties use the purity subtraction; the central values
    keep its bias ..., which no quoted uncertainty includes."
  - `sec_execsummary.tex:136`: the same.
  - `sec_summary.tex:59`: "which the quoted central values keep and no quoted uncertainty includes".
- S2: "only" removed. The new wording is "It is the background treatment of estimator configurations (d) and (e) of
  Table 3, which give ...".
  - `sec_execsummary.tex:136` adds "App. C also compares it with the purity subtraction on the 2D measurement".
  - `sec_summary.tex:61` uses the same wording as the executive summary.
  - N1: the abstract (`main_note.tex:96-97`) now reads "the generator tests, ... some five-dimensional validation
    studies and ... two-dimensional equivalence studies".
- S3: "a fifth of the positive difference".
  - `sec_execsummary.tex:61`.
  - `main_note.tex:82`, as "a fifth of the positive difference from that simulation".
- Background treatment, stated as its content once per layer: "No full five-dimensional comparison of the two
  background treatments has been made, and the choice of purity is to be revisited before submission".
  - `main_note.tex:95-96`, `sec_execsummary.tex:136` and `sec_summary.tex:63-64`.
  - Pointer: App. C. The comparison statement is in the unlabelled subsection C.7, and the revisit statement in C.6.
- Q3 `sec_execsummary.tex:89`: "nonlinear cross-source response terms".
- Nits applied:
  - N3 `sec_fps.tex:47`: "in the published region the extended unfold agrees with the control at this level".
  - N4 `sec_execsummary.tex:32`: "chosen over the exact-split estimator, now a cross-check, after ...".
  - N5 `sec_execsummary.tex:84`: "so every submitted draw has been observed".
  - N6 `sec_summary.tex:72`: "the miscoverage comes from a residual bias, not from too-narrow intervals".
