# Article shortening and analysis-note homes (2026-10-11)

**CITABLE FOR:** what was removed from the PRD article on 2026-10-11, where each removed detail now lives in the
analysis note, and which note sections were reorganized.
**NOT CITABLE FOR:** any physics result. No number, claim, scope, ruling or grade changes here; every result
quoted is routed to the records named in the article's and note's source comments.

**Request.** Joseph asked, on 2026-10-11, for the article to be cut and for every necessary detail to be present
in the analysis note in its proper place. He also asked that the note be made easier to navigate, with less
duplication. He stated that the s5p lane no longer exists, so the joint-test wording it had supplied is no longer
fixed.

## 1. Article

The article body (`docs/analysis-note/paper_body.tex`, excluding comments) went from about 6,350 to about 4,970
words, and the PRD build from 12 to 11 pages. The abstract was rewritten at the same scope.

**Independent review.** A read-only reviewer compared every rewritten sentence with the original before commit. It
found 3 HIGH, 6 MEDIUM and several LOW items; all were applied:
- H1: the 2D construction defects had read as not affecting the budget; the text now says the budget has not been
  revised for them and their effect is unmeasured.
- H2: "test-beam hadrons" widened the ±4% basis to neutrons.
- H3: "prevent" overstated the intro.
- Dropped qualifiers were restored: "deterministic variant", "the tested" shapes, "report-only", the two missing
  untested effects, "products distinct from the adopted one", and the claim/robustness roles of ±2δ/±3δ.

It found no transcription errors in `sec_joint.tex`. The two details the note lacked (the estimator qualifier for
the <0.3% refinement result, and "correcting a nominal closure bias does not certify coverage") were added to
`sec_5d.tex`.

| Article section | What was cut | Note home |
|---|---|---|
| II.D 2D uncertainty and coverage | pooling and target caveats; the one-sigma fraction and pull mean; the post hoc bootstrap diagnostic (KI 85); purity check; the full list of construction findings; split-sample argument | `sec_validation.tex` `sec:coverage` (new paragraph "The rebuilt band, scored post hoc"); `sec_systematics.tex` `sec:uq-2d-construction` |
| IV.C Higher-dimensional central values | the flux-sampling caveat on the GiBUU/GENIE ratio; the prior/response/finite-capacity taxonomy paragraph; the "these checks probe" paragraph | `sec_5d.tex` `sec:val-fiveaxis`, `sec:val-negweight` |
| V Central-value results | true-`E_avail` definition detail and the 11% bin-1 migration; GiBUU 14–15%/7% energy share, 1.37/1.29 | `sec_3d.tex` `sec:eavail-definition` and the Ascencio paragraph (migration added); `sec_eavailw.tex` `sec:eavailw-band` |
| VI Joint tests | the itemized nuisance draws; condition (i)'s null-SD sizes; rounding effect on NuWro's shape p; clipped band names; kappa-scan endpoints and the tests that first lose determinacy; the lost-seed split, second margin, earlier stops and narrower check scope; unscaled-recoil control and the full untested-effects list | `sec_joint.tex` (new section, `sec:joint5d`) |
| VII 5D uncertainty status | the seed variation's movement of projected central values; the nested-subset detail beyond one sentence | `sec_5d.tex` `sec:eavailw-construction` |

The article now cites the note as `AnalysisNote2026` (`publication.bib`), pinned to `506e4857`, the commit that
carries the reorganized note. **That citation points readers to a GitHub tree, not a deposited document.** Whether the note is
deposited with the release is a decision for Joseph; it is not made here.

The Sec. IV receipt check (`check_sec4_receipts.py`) still finds every printed value it guards in the article: 14/14
PASS, self-test 17/17.

## 2. Analysis note

| Change | Why |
|---|---|
| New `sec_joint.tex`, "Calibrated joint tests of generator predictions" | The note held about 1,000 words on the joint tests and the article about 2,700, so the article was the only complete record. The section is the union of the two. It uses `values_inference.tex`, now read by the note as well, so the joint-test numbers have one source. |
| `sec_eavailw.tex` split: it keeps the `W` axis, the `(E_avail,W)` map and the generator band; new `sec_5d.tex` holds the five-axis validation, model dependence, 5D coverage and the adopted covariance | The section was titled as an `(E_avail,W)` study, but about 60% of it was 5D estimator validation and uncertainty. Labels are unchanged. |
| Reporting-definition result (RD1–RD3, `RECORD-20260927-s5p-stage2-exit.md` §4) added to `sec:gbdt-model-dependence` | The article stated it, and the note carried only a one-line verdict. |
| 2D fixed-truth coverage promoted from a `\paragraph` to a subsection; same-ensemble pull diagnostic labelled `sec:val-other` | `\ref{sec:coverage}` printed the number of "Other validation diagnostics". Two references that meant the pull diagnostic now point to it. |
| `app_statmethods.tex` "C^stat is not changed" corrected | The statement was stale: the band was rebuilt on 2026-10-06 (VL170). |
| PET full-event `C_stat` moved verbatim into its own appendix, `app_cstat.tex` | It was the last subsection of a generic statistics appendix; its rationale paragraph is kept. |
| `sec_summary.tex` summary rewritten | Its bullets restated the executive summary item by item; the original is in git history. |
| "Where to find it" map added to `sec_intro.tex`; README source map updated | Navigation. |

**One inconsistency found and fixed:** the note's condition (iv) said the half-simulation shift is "at most about
0.05 null standard deviations". The article says 0.07, which is the frozen-V prefreeze measurement (maximum 0.068,
GENIE+MEC). The 0.05 is amendment 7's reviewer-proxy wording, superseded per
`audit-20261008/CLAIM-TABLE-20261008.tsv` row J12. The note now says 0.07.

## 3. Not done

The duplication audit also listed overlaps that were left alone because each copy already gives a summary and a
pointer, or because an earlier organization review placed it deliberately:
- the tension anatomy (results vs App. A);
- the five-dimensional pseudo-experiments (§9 vs App. B);
- the extended-fiducial fractions (App. A, moved there on 2026-10-04);
- the `(E_avail,W)` covariance audit numbers (§9.6 vs App. G).

`CLAIMS-20261005-claim-to-evidence.md` and `audit-20261008/` cite line numbers in the earlier article; they are
dated records and were not rewritten.

## 4. Verification

`bash build_all.sh` (local, TMPDIR set) exited 0. Its gates and results:
- page counts: note 134, primer 12, paper 11;
- no unresolved references;
- struck-value containment PASS (self-test PASS);
- Sec. IV receipts 14/14 PASS.

`python3 -m pytest test_build_all.py test_check_sec4_receipts.py`: 53 passed.
