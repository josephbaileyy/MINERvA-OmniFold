# The revised draft (d2): a decision packet for Joseph (2026-10-28)

**From** the paper rewrite lane, through the director. **Under:** your decisions on (d), `DECISION-20261028-joseph-final-draft-d.md` (PR #452). The record of this round is `d2/REPORT.md`. #413 stays a draft PR, and everything here returns to you before it merges.

**How to read it.** Each item gives what was done, the independent raters' choice and its runner-up, and the current printed text, quoted exactly from the sources (`final-draft/make_final_draft2.py`, which stops if a quote no longer matches). Your protected text is shown unedited, with proposals beside it. Every rater read was blind and in both orders, by sol2 (gpt-6.1-sol) and by gemini, with controls; the tallies are `d2/raters/TABLE.md` and `d2/raters-v2/TABLE.md`.

**The PDFs** (`build_all.sh` rc 0): `final-draft-2/main_paper.pdf` (11 pp), `final-draft-2/main_note.pdf` (130 pp), and `final-draft-2/redline-paper.pdf` (17 pp), the paper against the pre-integration base `8b0f83fd` (`final-draft/make_redline.sh`; a "??" appears only inside deleted text, at a label r19 removed).

## 1. What changed since (d)

1. **The title is T1** (your decision).
2. **Both abstracts are rewritten to the genre's typical form,** by removing whole sentences only, and the raters chose among the candidates (§3).
3. **IV H takes the shorter F1 paragraph** (your decision), and it adds one sentence on R11 (the raters' choice, §5).
4. **O3's sentence** adds the note's "although no single cause is established" (the raters' choice, §7).
5. **Data Availability, R1–R4 and the release text** are your protected text: the raters' choices are proposals here (§6), and nothing there is edited.

## 2. The title (applied)

> Simultaneous measurement of the ν_μ charged-current inclusive cross section on hydrocarbon in five observables from MINERvA open data

The note's title is its own ("Analysis Note: Unbinned OmniFold analysis of MINERvA charged-current inclusive data") and is unchanged. **For you:** T1 says "on hydrocarbon", and no sentence of the paper's body names the target material: the body places the vertex in "whose true vertex lies in the tracker fiducial volume". The note does ("Its central tracker comprises hexagonal planes of triangular polystyrene scintillator strips", `sec_experiment.tex`). **DRAFT:** "…whose true vertex lies in the fiducial volume of the polystyrene-scintillator (CH) tracker…". The plain-language primer's title still follows the old methods framing (its source comment says so); the primer is outside this round.

## 3. The abstracts (applied; drafts, yours)

**What is typical, measured** (`d2/MEASURE.md`, with register-prd-study's tools):
- **The paper:** the corpus's eight abstracts have 98–141 words (median about 120). At most one sentence carries a scope, condition or status marker, and no sentence carries two. Ours had 238 words with 5 of 8 sentences marked. **Caps:** 120–150 words; at most one marked sentence, with one marker.
- **The note:** the long-document anchors, T2K (PRD 91, 072010) and ProtoDUNE-SP (JINST 15, P12004), have 184 and 190 words, with no marked sentence. Ours had 382 words with 5 of 9 marked. **Caps:** at most 190 words, and the same marker caps.
- **No metatext** ("As an illustration", "This note documents", "The note also gives", and similar).

**How the candidates were made.** Each is whole sentences of the printed abstract, so no sentence that stays is weakened. Every fact of a dropped sentence still prints in a body, and the ledger probes each one there (rows D2-M4 … D2-A8). The note's candidates open with the paper abstract's first sentence: without the metatext sentence, the note's own "principal result" sentence no longer named the measurement.

**The raters' choice.**
- **Paper:** PB in all 8 runs over the two reads (PB 4; v2 PB 4). Runners-up PA and PC tie on mean rank.
- **Note** (v2): NA, 3 of 4 (NA 3, ND 1). gemini chose NA in both orders; sol2's two runs split by order. The runner-up is ND.
- **The control,** P02: ACCEPT in all 8 runs.

**The paper abstract as it now prints (120 words; PB):**
> We report a simultaneous measurement of the ν_μ charged-current inclusive cross section in five observables, the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass, unfolded without binning with OmniFold from MINERvA medium-energy open data and reported in sixteen cells with a covariance whose median per-cell uncertainty is 7.29%. Three external generator predictions compared on all sixteen cells give χ² of 109–272 for 16 degrees of freedom, and GiBUU, on 8 cells, 58. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic q3 tilt. The same unfolding reproduces the integral of the published muon-kinematic cross section within about 1%, with a correlated shape difference.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

**Runner-up PA (134 words), which keeps the coverage and bias-test sentence:**
> We report a simultaneous measurement of the ν_μ charged-current inclusive cross section in five observables, the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass, unfolded without binning with OmniFold from MINERvA medium-energy open data and reported in sixteen cells with a covariance whose median per-cell uncertainty is 7.29%. Three external generator predictions compared on all sixteen cells give χ² of 109–272 for 16 degrees of freedom, and GiBUU, on 8 cells, 58. The coverage of the intervals has not been validated; a bias test at two held-out GENIE v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic q3 tilt.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

**Runner-up PC (129 words), which keeps the validation findings:**
> We report a simultaneous measurement of the ν_μ charged-current inclusive cross section in five observables, the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass, unfolded without binning with OmniFold from MINERvA medium-energy open data and reported in sixteen cells with a covariance whose median per-cell uncertainty is 7.29%. Three external generator predictions compared on all sixteen cells give χ² of 109–272 for 16 degrees of freedom, and GiBUU, on 8 cells, 58. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic q3 tilt. Pseudo-experiments measure a background-subtraction bias that negative-weight subtraction largely removes, a partial recovery of generator-sized truth changes, and statistical undercoverage of a deterministic purity-subtracted variant at the tested truths.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

**The note abstract as it now prints (138 words; NA):**
> We report a simultaneous measurement of the ν_μ charged-current inclusive cross section in five observables, the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass, unfolded without binning with OmniFold from MINERvA medium-energy open data and reported in sixteen cells with a covariance whose median per-cell uncertainty is 7.29%. Three external generator predictions compared on all sixteen cells give χ² between 109 and 272 for 16 degrees of freedom, and GiBUU, on its 8 cells, 58. The coverage of the result's intervals has not been validated; a bias test at two held-out GENIE v3 truths finds the estimator's bias below the reported uncertainty in every cell but does not test interval widths. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic q3 tilt.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

**Runner-up ND (119 words), which keeps the flux sentence instead of the coverage one:**
> We report a simultaneous measurement of the ν_μ charged-current inclusive cross section in five observables, the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass, unfolded without binning with OmniFold from MINERvA medium-energy open data and reported in sixteen cells with a covariance whose median per-cell uncertainty is 7.29%. Three external generator predictions compared on all sixteen cells give χ² between 109 and 272 for 16 degrees of freedom, and GiBUU, on its 8 cells, 58. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic q3 tilt. The sixteen-cell χ² values fall by 24–48% when only the flux correlations are weakened by 10%.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

**What left the abstracts, and where it still prints** (ledger rows D2-*):
- **The paper:**
  - the coverage and bias-test sentence (Sec. I);
  - the flux sentence (Sec. I and Sec. V B);
  - the validation findings (Sec. IV);
  - the joint-test sentence. Its limitation, "no evidence of additional discrimination beyond matched coarse projections", is in the paper's Scope paragraph. Its rejections ("five generator predictions all reject at the 5% familywise level") now print only in the note.
- **The note:** the metatext opening; the list of covariance terms; the flux, reproduction, validation and joint-test sentences. Each prints in the note's body.
- **Two facts print in no note body file, for you:**
  - the note abstract's "principal result": the executive summary and summary say the validation findings are the main results (the n4 inconsistency, §10). agy flags the new opener, "We report a simultaneous measurement", for this framing;
  - "on a finer grid", which the cell counts only imply.

## 4. The wording of the coverage limitation (§3.4 of d)

The raters chose **(i) "Interval coverage has not been validated."** in 4 of 4 runs, against (ii) "The coverage of the intervals …" and (iii) "The coverage of the result's intervals …". The runner-up is (ii). Sec. I already prints (i), and the paper abstract no longer carries the sentence, so nothing changes. The note abstract keeps its own (iii); the read asked about the paper.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

## 5. F1 (applied)

**5.1 IV H's paragraph, as it now prints** (PRD read r6's sol2 r2 form, your decision; then the R11 sentence, the raters' choice in 4 of 4):
> Two GENIE v3 tunes, G18_10a_02_11b and AR23_20i_00_000, were generated for this test and held out of the analysis. Each reweights the simulated truth using its shape ratio to GENIE CV, constructed as for the C_model components. The simulated detector response is not probed. For each tune, 20 Poisson pseudo-experiments and a noise-free closure are compared with the truth using the full reported covariance. Both tunes satisfy the bias criteria: the pseudo-experiment means give χ²=11.84 (p=0.76) and 16.86 (p=0.39), respectively, with |z|≤0.65 in every cell of the means and closures. In cell R11 at G18_10a_02_11b, the bias lies below the reported uncertainty only with C_model included. The tunes share a quasielastic cross-section model; G18_10a_02_11b and the GENIE + MEC component of C_model also use Valencia-family MEC models. These tests provide partial evidence and are not independent. Omitting that C_model component gives χ²=15.15 (p=0.51) and 24.60 (p=0.077), respectively, as a descriptive comparison. The tests assess bias, not coverage: only event counts fluctuate, with systematic parameters fixed, so interval widths cannot be tested.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

**The R11 sentence** says what the review measured: |b|/σ at G18's R11 is 0.62 under the full covariance, 0.93 without GiBUU's vertex and 1.07 with C_e + C_resp alone. agy asks for the fuller form. **DRAFT, for you:** "…only with C_model included, mainly through its GiBUU component." The runner-up is not adding it.

**5.2 Sec. I's sentence** (unchanged; the R11 sentence qualifies it):
> Interval coverage has not been validated. At two held-out GENIE v3 truths, a bias test finds the estimator's bias below the reported uncertainty in every cell, but does not test interval widths.
<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->

## 6. Data and release (protected; proposals only)

**What is typical** (`d2/DA-SURVEY.md`, the seven corpus measurement papers, from source):
- all seven release cross sections, a covariance and the binning in machine-readable form;
- four say where; three point to the Supplemental Material; two cite a collaboration web page;
- none has a Data Availability section (all predate the 2024 PRD requirement), and none cites a DOI or HEPData.

The most typical sentences (verbatim from the corpus sources, as LaTeX):

- `The data release for the results presented in this analysis is posted at the link in Ref. \cite{bib:datarel}.  It contains the analysis binning, the oxygen and carbon $\nu_\mu$ double-differential  cross  sections  central  values, their ratio and associated covariance and correlation matrices.`
- `The data release for the results presented in this analysis is posted in Ref.~\cite{data}. It contains the analysis binning, the differential cross section best-fit values, and associated covariance matrices.`
- `The data release, the unfolded covariance matrices, and the additional matrices $A_{C}$ can be found in the Supplemental Material.`

**6.1 Data Availability, as it prints:**
> The input data and simulation are the MINERvA open-data AnaTuples, released under CC0 [12]. This analysis used an earlier production of that release; its 2,374 input files are identified by SHA256 checksum in the records cited in Ref. [14], App. G. A candidate release package of about 16 MB, not yet deposited, requires only numpy, scipy, and matplotlib. It recomputes every p value, decision, robustness result, and power figure of the joint tests and the numbers quoted in Sec. V C, and it regenerates the analysis note's figures of the joint-test null distributions and the (E_avail,W) map. The other quoted numbers, except the multiplier scan, and the event-level processing require the archived analysis products, the open-data AnaTuples, and the generator samples produced for this analysis; Ref. [14], App. G states what each part of the release does and does not reproduce. [HOLD: deposit identifier and access route, after the separately authorized release decision.]

**The raters' choice:** the typical DRAFT, in 4 of 4 runs at strength 3. The runner-up is the current text.
> The input data and simulation are the MINERvA open-data AnaTuples, released under CC0 [12]. The sixteen-cell cross section, its covariance matrix and the cell definitions are provided as machine-readable files in the Supplemental Material.
- **Its condition:** it is true only if you answer **Q8** yes, the article carries the sixteen-cell vector, covariance and cell definitions as supplemental files, and the files are made.
- **What it leaves out:** the release package and the input-file checksums, both described in the note's App. G.
- **It also removes** the stale pointer "the numbers quoted in Sec. V C" (`FINAL-DRAFT.md` 6.3).

**6.2 The deposit, beyond typical, for later.**
- The raters chose to add the caption's citation (B6, 4 of 4), but it fails the truth column: nothing is deposited.
- The raters chose not to add the Data Availability deposit sentence (B8, 4 of 4).
- `predictions-reference.json`, in the deposit or not, is still yours.

**6.3 R1–R4,** the release appendix's scopings. The raters chose the scoped forms in 4 of 4 runs; the runner-up keeps the current text. This is a proposal, because `app_release.tex` is protected:

- **R1.** Now: "the quoted closure, bias and covariance-status measurements." → proposed: "the quoted closure, bias and covariance-status measurements of the configuration-(a) central value."
- **R2.** Now: "the five-axis covariance used in this note and its" → proposed: "the five-axis covariance of the configuration-(a) central value and its"
- **R3.** Now: "travel with the five-axis covariance used in this note" → proposed: "travel with the five-axis covariance of the configuration-(a) central value"
- **R4.** Now: "The five-axis covariance used in this note is the file" → proposed: "The five-axis covariance of the configuration-(a) central value is the file"

**6.4 `app_release.tex:9`'s figure list:** the raters chose to keep it, in 4 of 4 runs. The runner-up is "directly or through its pointers".

## 7. O3 (applied) and Q4 (open)

**7.1 O3, as it now prints** (the raters' choice: sol2 2 of 2 for the qualified form, gemini 2 of 2 for keeping it; the models split, so sol2's true form, by round 3's rule. The runner-up is the unqualified sentence):
> We interpret the residual as regularization bias, because it persists over the tested iteration numbers and classifier capacities, although no single cause is established.

**7.2 Q4,** whether the final uncertainty accounts for the rounding instability. It has no options and stays an open question for you.

## 8. The flux band (§4 of d)

The raters chose **keep both** in 4 of 4 runs. The runner-up is replace: the band sentences stay; the two weakening sentences and the clause "which the weakening probes" leave V B, and Sec. I's flux sentence keeps its numbers and points to the note. The paper is unchanged, and ruling 2's band constraints hold.

## 9. Unchanged from (d)

These items are in `FINAL-DRAFT.md` and are not repeated here:
- the reading notes: gemini's five, and P02's;
- the register result: r19 adopted; r20 not; P1 3, 3, 3 against the anchors' 3.67.

## 10. Deferred to the note round n4

The two items of (d) §10, now sharpened: with the note abstract opening "We report a simultaneous measurement", the inconsistency with the executive summary's "The main results are the validation findings" is visible on the note's first page.

## 11. Untouched, and yours

KI-85, `\pubhold`, claims, Q8, Q4, the deposit, and every protected text (Data Availability, `app_release.tex`, `values.tex`, `values_inference.tex`, `app_history.tex`), which are byte-identical.

## 12. Gates and build

- `build_all.sh` rc 0: paper 11 pp, note 130 pp; no undefined reference; no `??`; SEC4 15/15.
- The ledger (`r19/check_ledger.py --base 9df8f748`): 255 rows, 475 probes, 0 failures. Its `--self-test` passes, with 57 scope guards, each planted strengthening caught, and the title, abstract and allowance pins (T1 and PB, by sha256) each caught.
- `make_values_fived16.py --check`, fived16 rule 7, reflow, swallowed-text, the registry, absence-claims, the live-doc index and the manifest all pass.
- agy, with a control (5 of 5 caught): `d2/agy/README.txt`.
<!-- absence-ok: quotes printed and protected text, decisions and rater readings for Joseph; not a new absence claim -->
