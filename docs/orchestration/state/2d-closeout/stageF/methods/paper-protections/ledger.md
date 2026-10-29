# The four paper protection edits: fact ledger

**Under:** `DECISION-20261028-joseph-protections-remade-and-r21.md`, items 1–4.

**Checker:** `check_ledger.py <worktree>`, with base `b554de56`, main at the branch's creation. The edits are made by
`apply_p.py`, item by item. Sentence ids are `--list`'s: PB for paper_body.tex and MP for main_paper.tex, followed by
the sentence's index in the base file's printed text.

## Item 1: the low-stability cells

This adds one sentence to the Limitations subsection, as `DECISION-20261024-joseph-h2-16-cell-definition.md` item 3
decided. It changes no base sentence.
- **The numbers:** `make_values_fived16.py` generates `h2-lowstab-cells`, `h2-lowstab-min` and `h2-lowstab-max` from
  the pinned `nd-unfolding/pv-ladder/readouts/h2_definition.json` (sha256 `b6790761…`, the decision's).
- **What the generator asserts:** the decided cells R02, R06, R10 and R15 are the four lowest-stability cells
  (0.185, 0.162, 0.217 and 0.251), and the range prints as the decision's 0.16–0.25. Its self-test plants a fifth
  cell below them and is refused.
- **The definition:** stability is a cell's fraction of simulated signal events generated in it and reconstructed
  that are reconstructed in it (`h2_definition.py`, `Stats.of`: `same / truth_reco`). The sentence states the
  definition because the paper's "Estimator stability" subsection uses the word for rounding instability.

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| L1 | four of the sixteen cells have stability 0.16–0.25 (the decision's disclosure), with the definition | — | ADDED | the Limitations subsection | `P::Four of the sixteen cells, \fvval{h2-lowstab-cells}, have a stability of \fvval{h2-lowstab-min}--\fvval{h2-lowstab-max}: of the simulated signal events generated in such a cell and reconstructed, only that fraction is reconstructed in the same cell.` && `N:values_fived16.tex::\@namedef{fv@h2-lowstab-cells}{R02, R06, R10 and R15}` && `N:values_fived16.tex::\@namedef{fv@h2-lowstab-min}{0.16}` && `N:values_fived16.tex::\@namedef{fv@h2-lowstab-max}{0.25}` |

## Item 2: Data Availability (the director's ruling (b))

The CC0 and input-file sentences are unchanged. The package sentences become one, narrowed to what the package
regenerates (`note-n4/release-claims.md`: RL-19 and RL-21; RC7's Fig. 2 output is byte-identical to the note's
`paper_fig2_joint.pdf`), and the reproducibility sentence stays, without its stale "except the multiplier scan". The false clause "and the numbers quoted in
Sec.~\ref{sec:central}" is removed, because that section quotes no numbers. `\pubhold` is untouched. The pair is
pinned in `check_ledger.DA_PINS`. B7's Supplemental Material sentence is not applied: no machine-readable files
exist, and Q8 is with Joseph.

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| D1 | a candidate package of about 16 MB, not deposited, needing numpy, scipy and matplotlib, which regenerates the note's null-distribution figure and the (Eavail,W) map | MP13, MP14 | ACC | one sentence, with the pointer | `MP::A candidate release package of about \SI{16}{MB}, not yet deposited, requires only numpy, scipy, and matplotlib, and regenerates the analysis note's figures of the joint-test null distributions and the $(\Eavail,W)$ map.` |
| D2 | the package reproduces the joint-test p values, decisions, robustness labels and power results; the paper now reports those tests only through its pointer to the note | MP14 | POINTER | the note's release appendix | `N:app_release.tex::reproduces the joint-test $p$ values, decisions, robustness labels and power results` |
| D3 | "the numbers quoted in Sec. central": FALSE as read, because sec:central quotes no numbers | MP14 | REMOVED (truth fix) | — | `P::These comparisons use the three- and four-observable central values of the joint-test estimator, without uncertainties.` |
| D4 | the other quoted numbers and the event-level processing need the archived products, the AnaTuples and the generator samples; the stale "except the multiplier scan" goes, because the paper quotes no multiplier scan | MP15 | KEPT-REWORDED | the same sentence without the exception, as "The paper's quoted numbers" (agy run1 Q5: the limitation stays; run2 Q5: "other" had lost its antecedent) | `MP::The paper's quoted numbers and the event-level processing require the archived analysis products, the open-data AnaTuples, and the generator samples produced for this analysis; \napp{app:release} states what each part of the release does and does not reproduce.` && `N:app_release.tex::The multiplier scan of the joint tests is recomputable from RC7's sufficient inputs` |

## Items 3 and 4: duplicate limitations, and the Scope wording (the director's rulings)

The rule: the body home keeps the evidence; §VI (Limitations) is the one numbered home; §I keeps "Interval coverage has
not been validated."; the abstract is untouched. Two joint-test caveats printed only in Scope, so they move to §VI.
Item 3 says no fact leaves the paper, and S3 below is that move.
<!-- absence-ok: ledger rows and rule quote printed limitation sentences and their homes; not a claim that a result does not exist -->

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| P15 | "The result has three limitations, each stated with it." The count no longer holds once §I keeps one, and each is still stated with the result | PB15 | META, removed | §I's pointer sentence | `P::Interval coverage has not been validated. The bias tests, the fake-data study and the dependence of the generator $\chi^{2}$ on the flux correlations are given with the result (Secs.~\ref{sec:fd16} and~\ref{sec:gen16}).` |
| P17 | F1 (E1): at two held-out GENIE v3 truths the bias is below the reported uncertainty in every cell; it is a bias test, not of interval widths | PB17 | DROPPED COPY | its home, sec:fd16 | `P::Two GENIE~v3 tunes, \fvval{f1-tune-g18} and \fvval{f1-tune-ar23}, were generated for this test and held out of the analysis.` && `P::with $|z|\leq\fvval{f1-zmax-ceil}$ in every cell of the means and closures` && `P::The tests assess bias, not coverage: only event counts fluctuate, with systematic parameters fixed, so interval widths cannot be tested.` |
| P18 | the fake-data study at its truths: the reported uncertainty does not cover the bias at the GiBUU-like truths or the q3 tilt | PB18 | DROPPED COPY | its home, sec:fd16; the abstract is untouched | `P::we unfold pseudo-data at \fvval{f0b-all-truths} truths` && `P::the reported uncertainty does not cover the fake-data bias at these GiBUU-like truths or at the $q_3$ tilt` && `MP::In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt.` |
| P19 | the generator χ² depends on the flux correlations, with the weakening numbers | PB19 | DROPPED COPY | its home, sec:gen16 | `P::Weakening only the flux correlations by \fvval{sens-alpha-pct}\,\% lowers the $\chi^2$ of the 16-cell predictions by \fvval{sens-flux-fall-lo}--\fvval{sens-flux-fall-hi}\,\%.` |
| P21 | 3D/4D: central values without intervals of validated coverage, the output of the joint-test estimator of Sec. II | PB21 | DROPPED COPY | §VI and sec:central | `P::The three- and four-observable central values lack intervals of validated coverage (Sec.~\ref{sec:central}).` && `P::These comparisons use the three- and four-observable central values of the joint-test estimator, without uncertainties.` |
| P22 | the sixteen-cell result has total uncertainties whose coverage is not validated | PB22 | DROPPED COPY | §VI | `P::The sixteen-cell result also has total uncertainties, whose coverage is not validated; Sec.~\ref{sec:fd16} reports the fake-data tests of the estimator's bias.` |
| P23 | the note's simulation-calibrated tests test hybrid nulls, are calibrated within the simulation model, and are not physical exclusions | PB23 | DROPPED COPY; "not physical exclusions" MOVED to §VI | §VI | `P::The note's calibrated tests reject hybrid nulls, conditionally on the simulation's hadronic response` && `P::Their calibration is valid to the extent that the simulated chain reproduces the analysis of the data` && `P::They are not physical exclusions of the generators` |
| P24 | no evidence of additional discrimination beyond matched coarse projections | PB24 | MOVED to §VI | §VI | `P::they show no evidence of additional discrimination beyond matched coarse projections.` |
| P180 | the sixteen-cell C_model label: built from the prior reweighted to each generator, unscaled and not a calibrated bound | PB180 | DROPPED COPY; the pointer kept | its home, sec:cov16 | `P::is built from the change in the unfolded data when the prior is reweighted to GENIE + MEC, NuWro and GiBUU in turn; it represents unscaled generator-shape dependence, not a calibrated bound` && `P::For the sixteen-cell result, Sec.~\ref{sec:fd16} reports the fake-data tests of the estimator's bias.` |
| P229 | the reported uncertainty does not cover the fake-data bias at the GiBUU-like truths (in sec:gen16) | PB229 | DROPPED COPY | its home, sec:fd16 | `P::the reported uncertainty does not cover the fake-data bias at these GiBUU-like truths or at the $q_3$ tilt` |
| S2 | Scope keeps its positive scope and points to §VI | — | REWORDED | Scope | `P::\emph{Scope.} The findings are those of one OmniFold implementation on one data set, for the observables, configurations, and deformations tested, rather than of multidimensional OmniFold in general. The limitations are listed in Sec.~\ref{sec:limitations}.` |
<!-- absence-ok: ledger rows and rule quote printed limitation sentences and their homes; not a claim that a result does not exist -->
