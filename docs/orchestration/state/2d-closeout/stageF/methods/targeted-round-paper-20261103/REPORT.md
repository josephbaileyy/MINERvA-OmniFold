# The targeted paper round: the referee-quoted sentences tightened; III A, IV D's closure and V C to the note (2026-11-03)

**Asked for by** Joseph's decision `DECISION-20261103-joseph-retire-density-gate.md` item 3 (#729, `5848abe3f`), through
the director. **Done by** the paper rewrite lane, on branch `docs/targeted-round-paper-20261103`, from `origin/main`
`7bdd39f69`; main was brought to `5848abe3f` before the first push. `docs/analysis-note` did not change between the two.

**Sources:**
- the R-P9 re-price, #728 (`4ea94a989`): `caveat-remeasure-20261102/rp9-reprice-97e30dda/` (`README.md`, `reprice.py`
  CANDIDATES, `probes.json`);
- its PRD-referee read, `PRD-REVIEW-RP9-GEMINI-ANSWER.txt` in the same directory (sha256 `c5eac29d1815b4d0…`, the file
  read before #728 merged).

**CITABLE FOR:**
- the changed sentences, before and after;
- where the note prints each fact that left the paper;
- the checks listed below.

**NOT CITABLE FOR:**
- a caveat density. This round does not re-measure; the director runs `remeasure.py` and limitations-catalog's
  re-measure afterwards, as information (decision item 1);
- the referee gate (decision item 2), which is a fresh two-referee read after this round;
- Joseph's approval of any wording.

## The round

| row | what | disposition | where the fact now prints |
|---|---|---|---|
| T1 | Sec. II, the E_avail comparison | tightened in place | paper; the examples and "Eq. 4 of" in the note, sec:eavail-definition |
| T2 | IV A, the run-period block's size | **restored** as at the base after the PRD-referee read and Joseph's answer (below) | paper, with the 0.73–2.56 interval; also the note, sec:fived16-pl |
| T3 | IV A, "No finite-ensemble correction is applied" | **restored** as at the base after the PRD-referee read and Joseph's answer (below) | paper; also the note, sec:fived16-cov |
| T4 | the fake-data section, "so the change is not a smaller bias or a validated uncertainty" | the inference to the note | paper (the bias equal, the covariance differing); the note, sec:fived16-fd |
| T5 | Table III, GiBUU's footnote | B3's name and the premise check to the note | paper (the failed check, the DIS share); the note, sec:joint5d-ch and sec:fived16-gen-target |
| T6 | V B, the χ² bands' "not the sensitivity … and are not intervals …" | the two negations to the note, with a pointer | the note, sec:fived16-gen |
| T7 | III A, reporting definitions, the precision target and the envelope | moved whole | the note, sec:gbdt-model-dependence |
| T8 | IV D's background closure, with Fig. 2 | moved whole; **note first** | the note, sec:val-negweight, sec:negweight-footing, app:bkg-residual-fig (Fig. 37) |
| T9 | V C, the 3D/4D descriptive comparisons | moved whole | the note, sec_3d.tex, sec_execsummary.tex, sec:eavailw-map/-band |

Every fact of every row is in `ledger.md`, with a probe that the paper or the note prints it. No fact left both. After
the restorations, T2 and T3 change no paper sentence.

**Kept, as the decision orders (item 4):**
- IV B, the 2D benchmark;
- IV F, input rounding;
- the Limitations' stopped-gate disclosure.

None of their sentences changed. The referee's suggestions to move IV F and to replace the stopped-gate account are
not adopted.

## Note first (T8)

#728's probes found 5 of 5 IV D facts in the note. They do not probe three more facts of the moved text, which the
note did not print:
- the refinement's capacity of the variant (100 trees, 8 leaves);
- the residual in the other (E_avail, W) cells ("at most 0.4 %", which Fig. 3's caption gives as 0.39 %);
- Fig. 2 itself.

Before the move:
- sec:val-negweight (`sec_5d.tex:51`) now states the first two. The capacity is the dev receipt's
  `controls.C2.refinement_params` (100, 8). The 0.39 % is the receipt's largest non-highest-W EW residual, 0.387.
- Fig. 2, with its caption verbatim, is in the note's last appendix after the coverage figure, as r19 placed that one.
  No existing figure number of the note changes; the new one is Fig. 37.

`check_sec4_receipts.py` bound four of IV D's printed values (VL149, VL151, VL152). Those bindings now read the note's
sentence: the purity column 3.5–4.1 %, the refined column 0.11–0.24 %, the joint cells 1.0 % and the data difference
1.4 %. It also binds the new 0.39 %. The result is 17/17, and the self-test rejects 21 perturbations (19 before).
`test_check_sec4_receipts.py` follows the values to the note (17 tests pass).

## Not adopted, or adopted only in part, for Joseph

1. **T1, the E_avail sentence.** The referee would move the 4.57 MeV comparison to the note. That is not adopted,
   because `DECISION-20261101-joseph-eavail-keep-135.md` item 2 requires this sentence to state four things:
   - that no single published definition exists;
   - the e± exclusion and the 4.57 MeV per charged pion, against the closed list and the charged-pion mass;
   - the open list's additional species;
   - nothing that implies the pion constant is the only departure.

   The 11-03 decision names the sentence for tightening but does not amend 11-01. So the sentence is shortened, and
   only the examples and the locator move. If Joseph wants the comparison in the note only, 11-01 item 2 needs
   amending.
2. **T5, Table III's footnote.** The referee would keep only a pointer. That the hydrogen sample failed its
   sampling-closure check, and that 46 % of it does not conserve energy, stay in the paper: they qualify the GiBUU χ²
   printed in the same row. Only B3's name and its post hoc premise check moved. Joseph may prefer the bare pointer.
3. **T2, the block's size.** The round first moved the interval to the note, which the decision allowed. The
   PRD-referee read asked for it back, and Joseph restored it (below).
4. **Outside this round's list:** the referee's other items are not acted on. These are condensing IV C, removing the
   earlier estimators from IV E, and rewriting the Limitations' domain-of-validity statement.

## Findings for the director

1. **#728's third III A probe is a false match.** `envelope.{0,80}(not an interval|diagnostic)` matches
   `sec_fps.tex:4` ("a three-prior dependence envelope, … a 200-pseudo-experiment containment diagnostic"), not III
   A's fact. The fact does print in the note, `sec_5d.tex`'s "Prior sensitivity is not a measured real-data bias"
   ("These envelopes are sensitivities: they provide no probabilities, covariance components or guaranteed bias
   bounds"). Ledger row T7 probes that sentence. Re-run at this round's sources, #728's probes give 3/3, 5/5 and 2/2
   (`NOTE-PROBES-728.txt`).
2. **The introduction still lists "a coverage test" among the validation studies** (`paper_body.tex`, Sec. I). Since
   #711 that test prints in the paper only as IV E's one-sentence pointer. This round removed "background-subtraction
   tests" from the same list, since T8 moves them. It left "a coverage test" as it is, for the next read.
3. **The registry cited the paper's estimator paragraph by line digest.** These are `ALIASES.tsv` rows 38 and 47 and
   `ATTRIBUTION.tsv` row 17. That line changed (T7 removed "and the precision study", and T8 re-pointed its closure
   reference), so the three rows are re-cited at line 55, and `records_estimators.tex` is regenerated. The quoted
   words are unchanged.

## After the PRD-referee read: two restorations

**The read.** The director ran a PRD-referee read of the round at `b98491263`. It is committed verbatim beside this
REPORT:
- `PRD-REVIEW-GEMINI-PROMPT.txt`, sha256 `d71c68039db44e45…`: the prompt header, then the word diff of the paper;
- `PRD-REVIEW-GEMINI-ANSWER.txt`, sha256 `02c30292e3b71f98…`.

**What it asks for.** It finds the three moves appropriate, and T1, T4 and T5 clear. It asks for two edits:
1. **The run-period block's interval.** Leaving only "poorly determined size" is "deficient": "The numerical interval
   must remain in the text."
2. **The finite-ensemble statement.** "An explicit 'without finite-ensemble corrections' in the text is preferable to
   an external pointer."

The answer numbers the figures "Fig. 5" and "Fig. 6", which no build of the paper does. By their content, they are
the background-closure figure that moved and the deformation figure's caption (0.09 % at nominal truth).

**Joseph's answer**, as the director relays it, verbatim: "Restore both, then merge (Recommended)". The decision
record is to follow.

**Done.** Both sentences are restored exactly as at the base `7bdd39f69`, so neither is now a changed sentence. The
ledger rows T2 and T3 read RESTORED, and their source comments in `paper_body.tex` say why.

### T2 — the run-period block's size

**At `b98491263`:**

> It has rank 2, is not corrected for the bootstrap noise it contains and, estimated from three groups, has a poorly
> determined size.

**Now (as at the base):**

> It has rank 2 and is not corrected for the bootstrap noise it contains, and with three groups its size is poorly
> determined: the 68 % interval on the ratio of its true to its estimated size is 0.73–2.56.

### T3 — the finite-ensemble correction

**At `b98491263`:**

> The note gives each block's ensemble, normalization and finite-ensemble treatment, the cells, the central values,
> the per-group uncertainties and the correlation matrix of the reported covariance (note sec:fived16-cov).

**Now (as at the base):**

> No finite-ensemble correction is applied. The note gives each block's ensemble and normalization, the cells, the
> central values, the per-group uncertainties and the correlation matrix of the reported covariance (note
> sec:fived16-cov).

## Before and after, every changed sentence

From the sources, rendered: values printed, macros expanded, references shown by label, comments removed. The base is `7bdd39f69`. Generated by the round's `pairs.py` (not committed; it reads only the two trees).

### T1 — Sec. II, the E_avail comparison

**Before:**

> No single published definition of E_avail exists: Eq. (1) keeps the species of the closed list of Ref. [ref] except electrons and positrons, its charged-pion term exceeds the kinetic energy used there and in Eq. 4 of Ref. [ref] by 4.57 MeV per charged pion, and it omits further species, such as kaons, antiprotons, and strange baryons, that the open list of Ref. [ref] includes.
>

**After:**

> No single published definition of E_avail exists. Eq. (1) keeps the species of the closed list of Ref. [ref] except electrons and positrons, omits species such as kaons that the open list of Ref. [ref] includes, and has a charged-pion term 4.57 MeV per pion above the kinetic energy used in Refs. [ref] (note sec:eavail-definition).
>

T2 and T3 are restored as at the base (the section above), so they change no sentence.

### T4 — the fake-data section

**Before:**

> The bias is the same in both; only the covariance differs, so the change is not a smaller bias or a validated uncertainty.
>

**After:**

> The bias is the same in both; only the covariance differs.
>

### T5 — Table III, GiBUU's footnote

**Before:**

> [footnote] Corrected to CH with GiBUU's own free-proton sample, which enters with weight 1/13 per nucleon. That hydrogen sample failed its sampling-closure check, B3 (a bias check of the check's premise, added post hoc, passed at ≤0.1 σ_c, with σ_c a cell's standard deviation under the null distribution of the note's joint tests), and its deep-inelastic events, 46 % of it, do not conserve energy (note sec:joint5d-ch).
>

**After:**

> [footnote] Corrected to CH with GiBUU's own free-proton sample, which enters with weight 1/13 per nucleon. That sample failed its sampling-closure check, and its deep-inelastic events, 46 % of it, do not conserve energy (note sec:joint5d-ch).
>

### T6 — V B, the χ² bands

**Before:**

> The bands describe the scatter of the χ² from estimating the correlations with these universes, not the sensitivity to incorrect correlations that the weakening probes, and are not intervals for the χ² under the true correlations.
>

**After:**

> The bands describe the scatter of the χ² from estimating the correlations with these universes (note sec:fived16-gen).
>

### T7 — III A to the note (III A; III B; IV's opening; IV A; III's estimators; the conclusions)

**Before:**

> [subsection] Reporting definitions and the precision target To include model dependence, a dedicated study defines the envelope of a cell as the largest shift of its data result when the simulation's prior is reweighted to each of five generator-sized changes of the truth, and adds it linearly to the probabilistic half-width. The envelope is a sensitivity diagnostic that tracks the regularization bias, not an interval. Our precision target is a 10 % median half-width for the total 68% interval. With the envelope added, none of the reporting definitions of a five-observable measurement tested in the study meets it. With the joint-test estimator, the envelope alone exceeds it for the 109 coarse joint cells and the 39 supported (E_avail,W) cells; for a coarser, non-nested partition of all five observables into 27 cells it does not, but the 1.4 % normalization contained in every probabilistic half-width lifts the median above it. Over these definitions, the envelope has a median of about 10–13% per cell, comparable to the generator differences that such a measurement would need to resolve. The study is described in note sec:gbdt-model-dependence.
>
> A five-observable cross section with total uncertainties is reported separately from those reporting definitions: the joint-test estimator's data result on 16 cells, R00–R15.
>
> Throughout, the prior used to unfold them stays at Tune v1. The envelope of Sec. sec:uncertainty-status instead reweights the prior used to unfold the data.
>
> The reported covariance of the sixteen-cell result is C_total+C_resp+C_PL,5D. Unlike the envelope of Sec. sec:uncertainty-status, its model term is a covariance built from three generator shifts.
>
> Its seeds are fixed, so its training is reproducible, and it also gives the held-out shape tests of Fig. fig:deformationb and the precision study.
>
> Two validation findings point to the unfolded result retaining part of its prior. The first is the residual under a generator-sized change of the truth in Sec. sec:departure, which we interpret as regularization bias. The second is the envelope of Sec. sec:uncertainty-status, which tracks the same bias.
>

**After:**

> A five-observable cross section with total uncertainties is reported as the joint-test estimator's data result on 16 cells, R00–R15. Other reporting definitions of a five-observable measurement, with their precision, are studied in note sec:gbdt-model-dependence.
>
> Throughout, the prior used to unfold them stays at Tune v1.
>
> The reported covariance of the sixteen-cell result is C_total+C_resp+C_PL,5D.
>
> Its seeds are fixed, so its training is reproducible, and it also gives the held-out shape tests of Fig. fig:deformationb.
>
> Two validation findings point to the unfolded result retaining part of its prior. The first is the residual under a generator-sized change of the truth in Sec. sec:departure, which we interpret as regularization bias. The second is the shift of the data result when the simulation's prior is reweighted to generator-sized changes of the truth, which tracks the same bias (note sec:gbdt-model-dependence).
>

### T8 — IV D's background closure and Fig. 2 to the note (IV D; Fig. 2; Fig. 3's caption; III's estimators; I; the conclusions)

**Before:**

> With purity-based background subtraction in a deterministic LightGBM estimator, end-to-end pseudo-experiments at nominal truth reproduce the input except in the highest-W cells, which are biased by up to 4 % in simulation (Fig. fig:bkg-residual). In the same estimator, unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves reduces it to below 0.3 % in those cells and at most 0.4 % elsewhere in the projection, leaving up to 1 % in some joint cells. In a two-dimensional closure test with backgrounds (20 pseudo-experiments at nominal truth), the purity estimate lies up to 5.9 statistical standard deviations from the truth, and more than one total standard deviation in one cell. The refined one lies within 0.44 in every cell, and the two are more than one statistical standard deviation apart in 14 of the 205 cells. On data, the two treatments differ by at most 1.4 %, and the two-dimensional result uses the refined estimator (note sec:closure-map; note app. sec:negweight-footing).
>
> [caption] Fractional closure residual, (unfolded - truth)/truth, at nominal truth, for pseudo-experiments that include backgrounds. Both from a deterministic LightGBM estimator. Circles: purity-based background subtraction (9 pseudo-experiments). Squares: unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves (60 pseudo-experiments). The pseudo-experiments are not paired. (a) The 42 (E_avail,W) projection cells, grouped by E_avail bin. (b) The 109 coarse joint cells, labelled by their index in the 3^5 grid, then the total integrated cross section. Error bars are the standard error of the mean.
>
> At nominal truth this variant's largest residual is 0.39 % (the squares of Fig. fig:bkg-residuala).
>
> This estimator removes most of the bias of purity-based subtraction at nominal truth in the highest-W cells (Sec. sec:validation), and the note's simulation-calibrated tests use the same estimator.
>
> The validation studies assess the result through the two-dimensional reproduction, background-subtraction tests, recovery of generator-sized truth changes, a coverage test, and a fake-data study of estimator bias.
>
> The studies of Sec. sec:validation show what must be checked before unfolded intervals are interpreted:
>

**After:**

> Closure tests with backgrounds included, comparing purity-based with unbinned negative-weight subtraction, are given in note sec:val-negweight and note app. sec:negweight-footing.
>
> At nominal truth this variant's largest residual is 0.39 % (note sec:val-negweight).
>
> This estimator removes most of the bias of purity-based subtraction at nominal truth in the highest-W cells (note sec:val-negweight), and the note's simulation-calibrated tests use the same estimator.
>
> The validation studies assess the result through the two-dimensional reproduction, recovery of generator-sized truth changes, a coverage test, and a fake-data study of estimator bias.
>
> The studies of Sec. sec:validation and of the companion note show what must be checked before unfolded intervals are interpreted:
>

### T9 — V C to the note (V C; I)

**Before:**

> These comparisons use the three- and four-observable central values of the joint-test estimator, which have no uncertainties and serve for qualitative comparison only. GENIE, the MINERvA Tune v1, NuWro, and GiBUU all underpredict the unfolded central value at low E_avail, between the quasielastic and \Delta peaks, in the region of the established low-recoil discrepancy [ref]. Comparisons with pion final-state-interaction variations, GENIE's Valencia 2p2h component, and the published measurement are given in Ref. [ref], Secs. note sec:3d-2p2h and note sec:4d. The five-observable (E_avail,W) map of the earlier purity-subtracted central value, and its comparisons with these generators, are given in Ref. [ref], Secs. note sec:eavailw-map and note sec:eavailw-band.
>
> We first reproduce the published double-differential cross section d^2σ/(dpT dp∥) [ref] as an end-to-end test of the unfolding, and we also give three- and four-observable central values.
>

**After:**

> We first reproduce the published double-differential cross section d^2σ/(dpT dp∥) [ref] as an end-to-end test of the unfolding. The three- and four-observable central values are given in the companion note [ref].
>

### The note's changes

**T8 — the note, sec:val-negweight (extended first):**

Before:

> Refined unbinned negative-weight subtraction (App. \refapp:negweight), applied with a deterministic variant of the five-dimensional LightGBM production estimator, brings the highest-W column to 0.11–0.24 % and the corner cell to 0.24 % over sixty nominal-truth experiments, which are not paired with the purity-based ones.

After:

> Refined unbinned negative-weight subtraction (App. \refapp:negweight), applied with a deterministic variant of the five-dimensional LightGBM production estimator and a refinement of 100 trees and 8 leaves, brings the highest-W column to 0.11–0.24 %, the corner cell to 0.24 % and every other (E_avail,W) cell to at most 0.39 % over sixty nominal-truth experiments, which are not paired with the purity-based ones (Fig. fig:bkg-residual-note).

**T8 — the note, the last appendix (added: Fig. 2 and its caption, verbatim):**


> \sectionSupplementary figure: closure with backgrounds The closure of the five-dimensional pseudo-experiments with backgrounds, under purity-based and refined negative-weight subtraction (\S\refsec:val-negweight), is shown cell by cell in Fig. fig:bkg-residual-note. [caption] Fractional closure residual, (unfolded - truth)/truth, at nominal truth, for pseudo-experiments that include backgrounds. Both from a deterministic LightGBM estimator. Circles: purity-based background subtraction (9 pseudo-experiments). Squares: unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves (60 pseudo-experiments). The pseudo-experiments are not paired. (a) The 42 (E_avail,W) projection cells, grouped by E_avail bin. (b) The 109 coarse joint cells, labelled by their index in the 3^5 grid, then the total integrated cross section. Error bars are the standard error of the mean.

## The checks

At the head after the two restorations:
- **Ledger** (`check_ledger.py`): 9 rows, 71 probes, 40 changed base sentences, 0 failures; self-test PASS.
- **Build** (`build_all.sh`): PASS. The paper drops from 12 to 11 pages and the note grows from 135 to 136; no
  undefined reference in either.
- **Receipts:** `check_sec4_receipts.py` 17/17; its self-test rejects 21 perturbations;
  `test_check_sec4_receipts.py` 17 passed.
- **Values:** `make_values_fived16.py --check` and `--self-test` PASS (`VALUES-CHECK.txt`).
- **Held sentences:** `check_held.py --fact-held --pair-applied G1:paper-s-09` gives the three pre-existing flags
  only (`CHECK-HELD.txt`). G1:paper-g-06, III A's envelope sentence, is held for its facts; ledger row T7 probes them
  in the note. G1b:paper-g-07, III's estimator sentence, prints unchanged.
- **Rater copy** (`make_rater_copy.sh`): PASS, 11 pages (after the restorations too).
- **Reflow** (`reflow_tex.py --note --check`): PASS.
- **Registry and results index:** PASS (finding 3).
- **Absence claims, the manifest and local CI:** see the director's message for the pushed head; the push runs only
  after local CI passes 38/38.

**The reading copy** is not committed. It has 27 pages:
- the paper's pages, new then base, interleaved (the base's page 12 last);
- the note's page 56 (sec:val-negweight), new then base;
- the note's new pages 128 and 130 (the appendix heading and Fig. 37).
