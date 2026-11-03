# REPORT The caveat cut list: the approved moves (2026-11-02)

**By** the paper rewrite lane (Claude), for the director, the PRD-referee read, limitations-catalog's re-measure and
Joseph.

**Under:** `DECISION-20261102-joseph-caveat-cut-list.md` and the director's work order of 2026-11-02. The inputs are
limitations-catalog's cut list (`caveat-remeasure-20261102/cutlist/`, #706: `cutlist.md`, `cutlist.json` and `moves.tsv`)
and the Gemini PRD review beside it (#707).

**MEASURES:** nothing. No value changes: `values_fived16.tex` is unchanged, and `make_values_fived16.py --check` passes.

**CANNOT AUTHORIZE:** a claim, a wording or a caveat count. The re-measure is limitations-catalog's (`remeasure.py`).

## What was done, move by move

| move | done | where now | note |
|---|---|---|---|
| MV01 run periods | merged | IV A, the 5D block's one statement; IV C, the 2D block's facts in two separated sentences (ruling 2) | V B's repeat of the post-hoc addition is gone; the abstract keeps the timing. Each block's construction and "cannot fail" are attributed to it: the 5D block "contains the differences by construction" (IV A), the 2D block "cannot fail its own consistency check" (IV C), as in the base |
| MV02 coverage | merged | VI A item 1 | The fake-data sentences of IV H and IV's "pointwise" clause join it. It states only what is established (ruling 1): "The coverage of the sixteen-cell intervals is therefore untested." The staged 1B campaign is in the note only (`sec_fived16.tex:246`), which keeps the 1B declaration's §12. Neither "halted" nor "an intermediate gate" is used. The A7 sentence "We make no coverage claim …" stays verbatim (G1b:paper-g-20). The intro's frozen "Interval coverage has not been validated." stays (G1b:paper-g-02) |
| MV03 3D/4D central values | merged | V C | V's opening and VI A no longer repeat it |
| MV04 envelope | merged | III A | Three sentences become two, with every number. The conclusions keep "tracks the same bias". The sentence is held for its facts (G1:paper-g-06) |
| MV06 C_model's sources | moved | IV A, in C_model's definition | V B's "(below)" now points to IV A |
| MV07 hydrogen samples | merged | the Table III footnotes | GiBUU's row keeps its footnote, and NuWro's row gets its own (review). With MV07F, Fig. 4's pointer sentence goes |
| MV07F Fig. 4 legend | done | the paper's Fig. 4 and the note's modes figure | E-A2's redraws (#712: ratio `6214ed78`, modes `0d6fe57c`, from the same E-1 with-arm readouts, without the hydrogen flags on the legend). make_values' FIGURES is re-pinned, and the installed copies equal their sources. Fig. 4's pointer sentence and the modes caption's definition of "supplement FLAGGED" go; the facts stay in the Table III footnotes and the note's Sec. 11.9 (`sec_joint.tex:327`) |
| MV08 background subtraction | merged | IV D | Five short sentences (ruling 5). The wording "biased by up to", "reduces it to below", "leaving up to" and "differ by at most" is bound by `check_sec4_receipts.py` (VL149, VL151, VL152), so it is kept |
| MV10 χ² correlation sensitivity | merged | V B | Short sentences (ruling 5) |
| MV13 IV F | moved | the note, sec:coverage-5d; a pointer in IV E | The pointer keeps the correction, the strongest case and the magnitude, "coverage as low as 0.06 for 68% intervals" (ruling 3), bound to its receipt in `check_sec4_receipts.py`. The conclusion sentence (Q43) moves too |
| MV14 binned diagnostic | moved | the note, sec:val-departure; IV E's existing pointer names it "with its scope" | — |
| MV15 IV G | condensed | IV G, two sentences | Reconciled from the records (below). The numbers sentence is byte-exact (G1b:paper-g-14) |
| MV16 the seed sentence | moved | the note, sec:val-departure; IV E's pointer names the seed sets | — |
| MV17 R11 | note first | sec_fived16.tex:244 | The paper sentence stays this round |
| MV18 hydrogen-sample sign | already in the note | sec_fived16.tex:388 and the target table | The cut list did not find it. No change |
| MV19 unpaired pseudo-experiments | note first | sec_5d.tex:51 | The caption stays this round |
| MV05, MV11, MV12 | skipped | — | — |
| MV09 | stays | — | — |
<!-- absence-ok: quotes the paper's printed coverage sentences, before and after; not a claim of this report -->

**Pages:** the paper goes from 13 to 12 pages and the note from 134 to 135.

## The second pass: the PRD-referee read and the director's rulings

The referee read (Gemini) is committed verbatim beside this report: `PRD-REVIEW-GEMINI-PROMPT.txt` (sha256 begins
`e3889104f35fbcac`) and `PRD-REVIEW-GEMINI-ANSWER.txt` (`0150b72e5a68e52b`). The director's rulings on it add no caveat.
1. **VI A item 1** states only what is established: "The coverage of the sixteen-cell intervals is therefore untested."
   The sentence on the staged 1B campaign is removed from the paper. It stays in the note (`sec_fived16.tex:246`), which
   keeps the 1B declaration's §12 ("paper unchanged until a result"), so no override is needed. Gemini's "stopped at an
   intermediate gate" is not used.
2. **MV01.** IV A states the 5D block alone: its groups differ beyond their bootstrap scatter, the cause is unknown,
   it is built from the double ratios with no reference group so it contains the differences by construction, it was
   added after they were seen following a pre-fixed audit, and it has rank 2, uncorrected noise and a poorly determined
   size. IV C states the 2D block in two separated sentences: the inconsistency (the step of about 7 % near 8 GeV/c),
   then its block, built in the same way, amounting to 2.0 % and unable to fail its own consistency check. That is two
   sentences, not one: the step and the block each read more clearly on their own. The base sentence "It was added
   after these differences were seen, following an audit whose stopping criterion was fixed in advance." is back word
   for word.
3. **MV13's pointer** gives the magnitude in one clause: "with coverage as low as 0.06 for 68% intervals". **There is
   no values key for this number.** The base printed it as a literal in IV F, and the note prints 0.060
   (`sec_5d.tex:215`). It is therefore bound like the other Sec. IV numbers. `check_sec4_receipts.py` gains one entry,
   which requires the printed 0.06 to equal `state/s5c/tier_s/interim_400.json` grid `eavail_tilt` `coverage68_min`
   (0.06, J224) to the printed digit. That makes the check 16/16, and its self-test rejects 19 perturbations, the new
   one included.
   - The receipt's third truth, `q3_given_eavail_w`, reads 0.000. OUTCOME-20260925-s5c-tier-s-futility-fail.md §3 calls
     it a construction defect, not estimator evidence, and says the verdict does not depend on it. So "most strongly
     when the true signal rate is lowered" and "0.06" stand, as in the base.
4. **IV G, reconciled from the records (for Joseph: a fact clarification, not a correction).** The two numbers are
   different statistics of the same instability, and both are right.
   - "Up to 2.6 statistical standard deviations" (held, byte-exact) is the largest shift of a reported quantity under
     **one** edge-safe float32-ulp perturbation of the data, in units of that quantity's data-bootstrap σ: median 0.78,
     maximum 2.58 at J145, for the joint-test estimator, and 0.80 and 2.48 for the development variant
     (`OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md:81`, `:92`).
   - "Inside the data-bootstrap statistical uncertainty" is the **scatter** of each quantity over 20 such perturbations:
     a J-cell median of 0.233 % against a refit-per-replica bootstrap σ of 0.368 %. Each replica carries the scatter at
     the same size, and σ_boot² ≥ σ_num,rep² holds for every functional. The record calls this "ABSORBED", about 37 % of
     the bootstrap variance (`RECORD-20260927-s5p-stage2-exit.md:38–45`).
   - **Before:** "The joint-test estimator is unstable under perturbations of its inputs within floating-point rounding.
     … This spread lies inside the data-bootstrap statistical uncertainty but limits how exactly the central values can
     be reproduced." The base's "this spread" did not say which statistic it meant, so it read as the 2.6σ shifts.
   - **After** (as corrected in the follow-up below): "…over 20 rounding-level perturbations of the data, the reported
     quantities scatter by a median of 0.23 % per joint cell, against a median data-bootstrap statistical uncertainty of
     0.37 %, a scatter that each bootstrap replica carries at the same size and that limits how exactly the central
     values can be reproduced, while a single perturbation moves the most affected quantity further." The held sentence
     follows unchanged.
   - No base number is wrong.
5. **Readability (ruling 5).** MV01, MV08 and MV10 are split into short sentences. No fact and no receipt-bound phrase
   changes, and `check_sec4_receipts.py` passes.
<!-- absence-ok: quotes the paper's printed coverage sentences, before and after; not a claim of this report -->

## Follow-up (the director, on `5a11eeb29`): one fix and two confirmations

1. **Fix: the 2D step's cause statement.** In the base, "The cause is not known, and these data cannot establish which
   period is correct" stood with the two-dimensional step of about 7 % near 8 GeV/c. Ruling 2 moved it to IV A only,
   where it is attached to the 5D groups, so it no longer stood with the 2D step.
   - **After:** IV C now reads "…by a step of about 7 % near 8 GeV/c. As for the sixteen-cell result, its cause is not
     known, and these data cannot establish which period is correct."
   - The held sentence (G1b:paper-g-19) still prints exactly in IV A. Ledger row MV01 probes both.
2. **Confirmation: what the record states about the scatter. This changes the text.**
   - `RECORD-20260927-s5p-stage2-exit.md:43–45` gives σ_boot² ≥ σ_num,rep² for 100 % of functionals. That is the
     replica rounding spread. For the base spread (`:38–41`), the record gives medians only.
   - The committed receipt (`state/s5p/stage2/stage2_receipt.json`, `0daa7cd8`, `study_N.N1_data.J`) gives both lists.
     The base spread lies below the bootstrap σ in **108 of the 109 J cells, not all**: at cell index 62 it is 0.435 %
     against 0.393 % (replica spread 0.347 %).
   - So the second pass's "each reported quantity scatters by less than its data-bootstrap statistical uncertainty"
     was not true of every cell. It now states the medians and the replica property only: "scatter by a median of
     0.23 % per joint cell, against a median data-bootstrap statistical uncertainty of 0.37 %, a scatter that each
     bootstrap replica carries at the same size".
   - **J is defined** as "the 109 supported fine joint cells (J cells)" (`sec_5d.tex:83`); these are the paper's 109
     joint cells.
3. **Confirmation: the same estimator.**
   - s5p stage 2 ran R: "Every refinement classifier carries R's 400/31, random_state 45; every OmniFold estimator
     carries F2" (`RECORD-20260927-s5p-stage2-exit.md:33–34`), and "Selected estimator: configuration 1 = R" (`:119`).
   - The receipt's control `data_base_equals_s5e_data_R` is true: the s5p base is s5e's R data result.
   - s5e's 2.58 is R's (`OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md:81`).
   - R is the candidate with raised refinement capacity, configuration (e) of the sixteen-cell result (`sec_5d.tex:91`),
     which the paper names the joint-test estimator.
   - So both numbers describe one estimator, and the sentence may pair them.

## The second PRD-referee read (the director, on `16cd55caf`): edits E1–E3

The read (Gemini) of the round's printed diff is committed verbatim beside this report:
- `PRD-REVIEW-2-GEMINI-PROMPT.txt`, which is `head.txt` followed by `diff.txt`, byte for byte;
- `PRD-REVIEW-2-GEMINI-ANSWER.txt`.
`SHA256SUMS` covers both reads. Each edit keeps every fact in paper plus note.

**E1. IV C's run-period statement.**
- The referee objected to the verbatim repeat of the cause sentence and to the jargon "cannot fail its own consistency
  check". Both facts are now stated once and plainly.
- **Before** (the follow-up's text): "…by a step of about 7 % near 8 GeV/c. As for the sixteen-cell result, its cause is
  not known, and these data cannot establish which period is correct. Its run-period block, built in the same way
  (Sec. IV A), includes this inconsistency, amounts to 2.0 % on the integrated cross section and, being built from the
  observed differences, cannot fail its own consistency check."
- **After:** "…by a step of about 7 % near 8 GeV/c, of unknown cause (Sec. IV A). Its run-period block, built from these
  differences in the same way, includes this inconsistency, amounts to 2.0 % on the integrated cross section and passes
  its own consistency check by construction."
- **"Which period is correct"** for the 2D step: the IV A pointer carries it, where the held sentence (G1b:paper-g-19)
  prints unchanged. The note prints it for the 2D step: "These data cannot establish which period, if any, is correct."
  (`sec_systematics.tex:165`, probed in ledger row MV01).

**E2. VI A item 1.**
- "The coverage of the sixteen-cell intervals is therefore untested." is dropped. It restated the item's opening, "No
  reported interval has validated coverage."
- The stopped-gate sentence stays: the disclosure is required in every outcome (Q39).
- The referee's "could not be completed" is not used. 1B is not finished, so it would be false.
<!-- absence-ok: quotes the paper's printed coverage sentences, before and after; not a claim of this report -->

**E3. IV G.** The first sentence is split in two:
- the scatter: over 20 perturbations, a median of 0.23 % per joint cell against the 0.37 % median bootstrap σ, which
  each replica carries at the same size;
- "It limits how exactly the central values can be reproduced, and a single perturbation moves the most affected
  quantity further."
The held 2.6/2.5 sentence follows unchanged. No fact changes.

**Kept by the director's ruling:**
- **The stopped-gate sentence in VI A.** The referee suggested moving it to the note. It stays: Q39 requires the
  disclosure in every outcome.
- **The replica clause in IV G.** The referee suggested moving it to the note. It stays: that is a B0 wording question,
  which Joseph takes with the B4 outcome (`DECISION-20261102-joseph-bias-and-stabilisation-routes.md` item 5).

**Referee suggestions not adopted, for Joseph:**
1. **(d) Excising MV13's pointer**, the earlier estimator's 0.06 coverage. `DECISION-20261029-joseph-limitations-may-leave-paper.md`
   requires a pointer for a limitation that leaves the paper.
2. **Pruning the Table III footnote on GiBUU's hydrogen sample** (B3, the post-hoc premise check, the DIS energy
   non-conservation). That would be a new move, outside the approved set.
3. **The C_PL,5D audit clause** ("following an audit whose stopping criterion was fixed in advance"). It is a base
   sentence, restored word for word at the director's ruling 2.

**Item 3 of VI A (MV09; limitations-catalog's mechanical check).**
- The source is byte-identical at `58fa0b89`, `589eb47d0` and this head (the same md5).
- At `cf595ccac` it also printed every word. In that layout, though, the item broke across the column where the
  references begin, so pdftotext interleaved "[1] G. D'Agostini …" between "matched" and "coarse projections". That is
  why a verbatim search failed.
- In this pass's layout the item prints contiguously. Every fact of C66–C68 prints at the same place.

## Points for the director and Joseph

1. **IV G** (above, item 4): a clarification from the records for Joseph. No number changes.
2. **The 0.06** (item 3): bound to its receipt in code, not through a values key, since none existed.
3. **IV C's 2D run-period facts** are two sentences rather than one (item 2).
4. **MV07F is done.** The redrawn legends say "NuWro 21.09: CH" and "GiBUU 2019: CH; p∥ < 4.5 cells only", with no
   "hydrogen". So both caption sentences go: Fig. 4's pointer, and the modes caption's "supplement FLAGGED" definition.

## Every changed sentence, before and after

Rendered from the sources: `\fvval` values are filled in, and a pointer reads "note <label>". The base is `589eb47d0`. MV07F's two removed caption sentences (Fig. 4's legend definitions and the modes caption's "supplement FLAGGED") are quoted under MV07 (before).

### MV01 — run periods (IV A; IV C's paragraph; V B)

**Before:**

> The run-period block C_PL,5D accounts for differences among the three run-period groups, whose unfolded results, each relative to its own simulation, differ by more than their bootstrap scatter. The cause is not known. As for the two-dimensional result (Sec. sec:uq2d), the block is built from the double ratios among the groups, with no reference period; it has rank 2, is not corrected for the bootstrap noise it contains, and with three groups its size is poorly determined: the 68 % interval on the ratio of its true to its estimated size is 0.73–2.56. It was added after these differences were seen, following an audit whose stopping criterion was fixed in advance.
>
> Data from different run periods are not mutually consistent within the other uncertainties. One period group's unfolded p∥ distribution, taken relative to its own simulation, differs from that of the earliest periods by a step of about 7 % near 8 GeV/c. The cause is not known, and these data cannot establish which period is correct. The run-period block is built from double ratios among the three period groups, each group's unfolded result over its own simulated truth, with no group chosen as the reference. It includes this inconsistency in the combined result and amounts to 2.0 % on the integrated cross section. Because the block is built from the observed differences among the periods, it contains them by construction, and its own consistency check cannot fail.
>
> The run-period block was added after the data were seen (Sec. sec:cov16). With it, each total
>

**After:**

> The unfolded results of the three run-period groups, each relative to its own simulation, differ by more than their bootstrap scatter. The cause is not known, and these data cannot establish which period is correct. The run-period block C_PL,5D includes this inconsistency in the reported covariance. It is built from the double ratios among the groups, each group's unfolded result over its own simulated truth, with no group chosen as the reference, so it contains the differences by construction. It was added after these differences were seen, following an audit whose stopping criterion was fixed in advance. It has rank 2 and is not corrected for the bootstrap noise it contains, and with three groups its size is poorly determined: the 68 % interval on the ratio of its true to its estimated size is 0.73–2.56.
>
> In the two-dimensional result, data from different run periods are not mutually consistent within the other uncertainties: one period group's unfolded p∥ distribution, relative to its own simulation, differs from that of the earliest periods by a step of about 7 % near 8 GeV/c, of unknown cause (Sec. sec:cov16). Its run-period block, built from these differences in the same way, includes this inconsistency, amounts to 2.0 % on the integrated cross section and passes its own consistency check by construction.
>
> With the run-period block, each total
>

### MV02 — the one coverage statement (IV opening; IV H; VI A item 1)

**Before:**

> Coverage, how often intervals contain their target over repeated experiments, tests the estimator and the interval construction together, and the coverage tested here is pointwise, for each reported quantity separately, not the stronger simultaneous coverage of all of them.
>
> The tests assess bias, not coverage: only event counts fluctuate, with systematic parameters fixed, so interval widths cannot be tested. A coverage test at these two tunes, declared in advance for the covariance without the run-period block, with pseudo-experiments that also draw the flux, interaction, and detector uncertainties, was stopped at one of its gates before any coverage pseudo-experiment ran: the uncertainties reproduced through its pseudo-experiments disagreed with the covariance blocks they draw, for reasons not established (note sec:fived16-fd).
>
> The coverage of the sixteen-cell total uncertainties has not been tested: the fake-data tests of Sec. sec:fd16 assess the estimator's bias, and the coverage test declared at two of their truths stopped before any coverage pseudo-experiment ran. Neither the coverage of C_model at truths held out of its construction nor the size of either run-period block is independently validated (note sec:fived16-cov, sec:fived16-pl and sec:uq-combine). The two-dimensional covariance has not been independently validated and gives no calibrated significance for generator comparisons. An earlier statistical band of that result undercovered in its tails in a coverage test at fixed truth (note sec:coverage); the coverage of the current statistical block and of the total covariance has not been tested. We make no coverage claim on independent simulated samples or simultaneously over all reported bins and projections. The three- and four-observable central values lack intervals of validated coverage (Sec. sec:central).
>
<!-- absence-ok: quotes the paper's printed coverage sentences, before and after; not a claim of this report -->

**After:**

> Coverage, how often intervals contain their target over repeated experiments, tests the estimator and the interval construction together.
>
> Coverage is discussed in Sec. sec:limitations.
>
> No reported interval has validated coverage. The fake-data tests of Sec. sec:fd16 assess bias, not coverage: only event counts fluctuate, with systematic parameters fixed, so interval widths cannot be tested. A coverage test at two of their truths, declared in advance for the covariance without the run-period block, with pseudo-experiments that also draw the flux, interaction, and detector uncertainties, was stopped at one of its gates before any coverage pseudo-experiment ran: the uncertainties reproduced through its pseudo-experiments disagreed with the covariance blocks they draw, for reasons not established (note sec:fived16-fd). Neither the coverage of C_model at truths held out of its construction nor the size of either run-period block is independently validated (note sec:fived16-cov, sec:fived16-pl and sec:uq-combine). The two-dimensional covariance has not been independently validated and gives no calibrated significance for generator comparisons; an earlier statistical band of that result undercovered in its tails in a coverage test at fixed truth (note sec:coverage), and the coverage of the current statistical block and of the total covariance has not been tested. The coverage tests cited are pointwise, for each reported quantity separately, not the stronger simultaneous coverage of all of them. We make no coverage claim on independent simulated samples or simultaneously over all reported bins and projections.
>
<!-- absence-ok: quotes the paper's printed coverage sentences, before and after; not a claim of this report -->

### MV03 — the 3D/4D central values (V B opening; V C)

**Before:**

> The two-dimensional result is therefore reusable, the sixteen-cell result can be used for the comparison that follows, and the higher-dimensional central values can be used for qualitative comparison.
>
> These comparisons use the three- and four-observable central values of the joint-test estimator, without uncertainties.
>

**After:**

> The two-dimensional result is therefore reusable, and the sixteen-cell result can be used for the comparison that follows.
>
> These comparisons use the three- and four-observable central values of the joint-test estimator, which have no uncertainties and serve for qualitative comparison only.
>

### MV04 — the envelope (III A; the conclusions)

**Before:**

> With the envelope added, none of the reporting definitions of a five-observable measurement tested in the study meets this target. With the joint-test estimator, the envelope alone exceeds the target for the 109 coarse joint cells and for the 39 supported (E_avail,W) cells. For a coarser, non-nested partition of all five observables into 27 cells, the same estimator's envelope alone does not exceed the target, but the 1.4 % normalization contained in every probabilistic half-width lifts the median above it.
>
> The second is the envelope of Sec. sec:uncertainty-status, which tracks the same bias and alone exceeds the precision target in two of the three tested reporting definitions.
>

**After:**

> With the envelope added, none of the reporting definitions of a five-observable measurement tested in the study meets it. With the joint-test estimator, the envelope alone exceeds it for the 109 coarse joint cells and the 39 supported (E_avail,W) cells; for a coarser, non-nested partition of all five observables into 27 cells it does not, but the 1.4 % normalization contained in every probabilistic half-width lifts the median above it.
>
> The second is the envelope of Sec. sec:uncertainty-status, which tracks the same bias.
>

### MV06 — C_model's sources (V B to IV A)

**Before:**

> That rise comes from pairing the CH prediction with C_model, whose NuWro and GiBUU shape ratios are from carbon (below):
>
> The GENIE + MEC, NuWro and GiBUU comparisons use covariance contributions derived from those generators, and GENIE CV enters as their common reference; those contributions come from the generators' samples in their own definitions, with NuWro and GiBUU on carbon, not from the predictions compared here.
>
> The two-dimensional covariance is the sum of four blocks, each from LightGBM unfoldings with the central value's estimator: systematic universes (187 universes, including the normalization), statistical (300 bootstrap replicas), run period (three period groups), and training seed (five seed settings, so that its own size is poorly determined).
>

**After:**

> Its contributions come from those generators' samples in their own definitions, with NuWro and GiBUU on carbon and GENIE CV as the common reference, not from the predictions compared in Sec. sec:gen16. The comparisons there with GENIE + MEC, NuWro and GiBUU therefore use covariance contributions derived from the same generators.
>
> That rise comes from pairing the CH prediction with C_model, whose NuWro and GiBUU shape ratios are from carbon (Sec. sec:cov16):
>
> The two-dimensional covariance is the sum of four blocks, each from LightGBM unfoldings with the central value's estimator: systematic universes (187 universes, including the normalization), statistical (300 bootstrap replicas), run period (three period groups), and training seed (five seed settings, so that its own size is poorly determined).
>

### MV07 and MV07F — the hydrogen samples (Table III footnotes; Fig. 4 caption; the note's modes caption)

**Before:**

> The sampling-closure check failed on that hydrogen sample; a bias check of the check's premise, added post hoc, passed at ≤0.1 σ_c, with σ_c a cell's standard deviation under the null distribution of the note's joint tests (note sec:joint5d-ch). Deep-inelastic events, 46 % of the hydrogen sample, do not conserve energy.
>
> In the legend, GiBUU's “closure B3 failed” is the sampling-closure check that failed on its hydrogen sample (the footnote to Table tab:gen16), and NuWro's “supplement FLAGGED” marks the part of its free-proton sample generated at neutrino energies of 50–100 GeV, in which the events lost to generator aborts were not shown to be negligible (note sec:joint5d-ch).
>
> NuWro's “supplement FLAGGED” marks the part of its free-proton sample generated at neutrino energies of 50–100 GeV, in which the events lost to generator aborts were not shown to be negligible (\S\refsec:joint5d-ch).
>

**After:**

> That hydrogen sample failed its sampling-closure check, B3 (a bias check of the check's premise, added post hoc, passed at ≤0.1 σ_c, with σ_c a cell's standard deviation under the null distribution of the note's joint tests), and its deep-inelastic events, 46 % of it, do not conserve energy (note sec:joint5d-ch).
>
> In NuWro's free-proton sample, the supplement generated at neutrino energies of 50–100 GeV is flagged: the events lost to generator aborts there were not shown to be negligible (note sec:joint5d-ch).
>

### MV08 — background subtraction (IV D)

**Before:**

> Figure \reffig:bkg-residual shows that, with purity-based background subtraction in a deterministic LightGBM estimator, end-to-end pseudo-experiments at nominal truth reproduce the input except in the highest-W cells, which are biased by up to 4 % in simulation. In the same estimator, unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves reduces it to below 0.3 % in those cells and at most 0.4 % elsewhere in the projection, leaving up to 1 % in some joint cells. On data, the two treatments differ by at most 1.4 %. Both kinds of closure study are described in note sec:closure-map. In two observables, a closure test with backgrounds (20 pseudo-experiments at nominal truth) finds the purity and refined estimates more than one statistical standard deviation apart in 14 of the 205 cells. The purity estimate lies up to 5.9 statistical standard deviations from the truth, and more than one total standard deviation in one cell, while the refined one lies within 0.44 in every cell. The two-dimensional result therefore uses the refined estimator (note app. sec:negweight-footing).
>

**After:**

> With purity-based background subtraction in a deterministic LightGBM estimator, end-to-end pseudo-experiments at nominal truth reproduce the input except in the highest-W cells, which are biased by up to 4 % in simulation (Fig. fig:bkg-residual). In the same estimator, unbinned negative-weight subtraction with a refinement of 100 trees and 8 leaves reduces it to below 0.3 % in those cells and at most 0.4 % elsewhere in the projection, leaving up to 1 % in some joint cells. In a two-dimensional closure test with backgrounds (20 pseudo-experiments at nominal truth), the purity estimate lies up to 5.9 statistical standard deviations from the truth, and more than one total standard deviation in one cell. The refined one lies within 0.44 in every cell, and the two are more than one statistical standard deviation apart in 14 of the 205 cells. On data, the two treatments differ by at most 1.4 %, and the two-dimensional result uses the refined estimator (note sec:closure-map; note app. sec:negweight-footing).
>

### MV10 — the χ² correlation sensitivity (V B)

**Before:**

> Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 23–38 %. The same change to the detector or lateral correlations lowers it by at most 18 %. With the correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps χ²≥41 for 16 degrees of freedom. The flux correlations are estimated from 100 hadron-production (PPFX) flux universes [ref], weighted by the neutrino–electron and inverse-muon-decay constraint. Bootstrapping these universes, with the flux variances kept, gives 16th–84th percentile bands for each 16-cell χ², with edges within 3.8 % of the reported value and a median at most 0.4 % above it. These bands describe the scatter of the χ² from estimating the correlations with these universes, not its sensitivity to incorrect correlations, which the weakening probes. In particular, they are not intervals for the χ² under the true correlations.
>

**After:**

> Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 23–38 %, and the same change to the detector or lateral correlations lowers it by at most 18 %. With the correlations of the interaction, flux, detector and lateral groups removed, every 16-cell prediction keeps χ²≥41 for 16 degrees of freedom. The flux correlations are estimated from 100 hadron-production (PPFX) flux universes [ref], weighted by the neutrino–electron and inverse-muon-decay constraint. Bootstrapping these universes, with the flux variances kept, gives 16th–84th percentile bands for each 16-cell χ², with edges within 3.8 % of the reported value and a median at most 0.4 % above it. The bands describe the scatter of the χ² from estimating the correlations with these universes, not the sensitivity to incorrect correlations that the weakening probes, and are not intervals for the χ² under the true correlations.
>

### MV13 and MV14 — IV F and the binned diagnostic to the note (IV E's pointer; the conclusions)

**Before:**

> A binned, signal-only and noise-free diagnostic on the 109 joint cells and the truth changes used to develop the estimator, with the detector response fixed at the simulation's, shows that exact binned iterative unfolding with five iterations leaves about the same median residual as the boosted-tree estimator. It covers only the residuals whose diagnosis does not change with the resolution of the truth binning (38 % of the joint-cell residuals above 2 %). Within that scope, the residual is consistent with the regularization of the inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (note sec:val-departure). The diagnostic does not address what unbinned information could recover, the miscoverage of Sec. sec:coverage, or the validity of any interval.
>
> The deformation studies, the iteration and capacity tests, the exact binned comparison and the joint-test-estimator shapes are given in Ref. [ref], Secs. \ref*N-sec:val-negweight and \ref*N-sec:val-departure.
>
> Statistical intervals from a deterministic LightGBM estimator with purity-based subtraction, corrected for the estimator's closure bias at nominal truth, miscover at the tested truths, most strongly when the true signal rate is lowered by about 10 %. Under that change, 51 of the 153 reported cell and projection integrals have a 68% coverage whose upper confidence bound lies below the acceptance threshold of 0.66, with coverage as low as 0.06. The end-to-end test unfolds 400 pseudo-experiments per truth. A diagnosis attributes the miscoverage to a residual bias that grows with W and survives the nominal-truth bias correction. The source of this residual bias has not been established. Agreement in the marginal normalizations coexists with substantial residual bias under the tested deformations. The interval construction and the diagnosis are described in note sec:coverage-5d.
>
> The miscoverage of Sec. sec:coverage is also attributed to a residual bias, but whether that bias has the same origin is not established.
>

**After:**

> The deformation studies, the iteration and capacity tests, the exact binned comparison with its scope, and the joint-test-estimator shapes with the seed sets of their pseudo-experiments are given in Ref. [ref], Secs. \ref*N-sec:val-negweight and \ref*N-sec:val-departure.
>
> Statistical intervals of an earlier five-observable estimator with purity-based subtraction, corrected for its closure bias at nominal truth, miscover at the tested truths, most strongly when the true signal rate is lowered by about 10 %, with coverage as low as 0.06 for 68% intervals (note sec:coverage-5d).
>

### MV15 — IV G condensed

**Before:**

> The joint-test estimator is unstable under perturbations of its inputs within floating-point rounding. Rounding-level changes of its inputs move its results by up to 2.6 statistical standard deviations, and those of the lower-capacity development variant by up to 2.5, so the estimator fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations. This spread lies inside the data-bootstrap statistical uncertainty but limits how exactly the central values can be reproduced.
>

**After:**

> The joint-test estimator is unstable under floating-point rounding of its inputs: over 20 rounding-level perturbations of the data, the reported quantities scatter by a median of 0.23 % per joint cell, against a median data-bootstrap statistical uncertainty of 0.37 %, and each bootstrap replica carries this scatter at the same size. It limits how exactly the central values can be reproduced, and a single perturbation moves the most affected quantity further. Rounding-level changes of its inputs move its results by up to 2.6 statistical standard deviations, and those of the lower-capacity development variant by up to 2.5, so the estimator fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations.
>

### MV16 — Fig. 3's seed sentence (caption to the note)

**Before:**

> Neither seed set was held out from the estimator's development.
>

**After:**

> (removed from the paper; see the note below)


### The note's additions

**MV13 — the note, sec:coverage-5d (added):**

> Agreement in the marginal normalizations thus coexists with a substantial residual bias under the tested deformation, and whether that bias has the same origin as the regularization bias of \S\refsec:val-departure is not established.

**MV16 — the note, sec:val-departure (added):**

> The pseudo-experiments of the paper's recovery figure, sixty for the development variant at the GiBUU-to-GENIE E_avail shape and twenty for each of three shapes not used in the joint-test estimator's selection, use seed sets that were not held out from the estimator's development.

**MV19 — the note, sec:val-negweight (extended):**

> brings the highest-W column to 0.11–0.24 % and the corner cell to 0.24 % over sixty nominal-truth experiments, which are not paired with the purity-based ones.

**MV17 — the note, sec:fived16-fd (extended):**

> In every cell of the four records, the bias is below 0.62 of the cell's reported σ; in cell R11 at G18\_10a\_02\_11b, the bias lies below the reported uncertainty only with C_model included.

**MV02 — the note, sec:fived16-fd (added: the staged campaign):**

> A staged coverage test at the two tunes, with the covariance rebuilt by the same procedure at each tune, is under way.


## Where the note prints each moved fact (by file:line, this branch)

- **IV F (MV13):**
  - `sec_5d.tex:213` (sec:coverage-5d): the test, its futility, the 10 % rate reduction, and 1,200 pseudo-experiments
    over three truths;
  - `:215`: 51 of 153 below 0.66, as low as 0.060;
  - `:228`: the residual bias, growing with W and not removed by the correction; its source not established; and,
    added here, the marginal normalizations and whether the bias has the same origin.
- **The binned diagnostic (MV14):** `sec_5d.tex:84`, with its results and its scope ("It does not address what unbinned
  or biased estimators could recover…").
- **The seed sets (MV16):** `sec_5d.tex:77`.
- **The unpaired pseudo-experiments (MV19):** `sec_5d.tex:51`.
- **R11 (MV17):** `sec_fived16.tex:244`.
- **The staged 1B campaign (MV02; the note only, ruling 1):** `sec_fived16.tex:246`.
- **The hydrogen-sample sign (MV18):** `sec_fived16.tex:388`, and the target table.
- **The run-period audit and the block's validation (MV01):** `sec_fived16.tex:175` and `sec_systematics.tex:186`.
- **The NuWro supplement flag (MV07):** `sec_joint.tex:327`.

## Checks

| check | result |
|---|---|
| the ledger (`check_ledger.py`, base `589eb47d0`) | 16 rows, 97 probes, 57 changed base sentences, 0 failures; self-test PASS. `sec:coverage` is declared removed from the paper. The note's own label of that name is not counted as a reference to it, and a test shows the check still fires on a paper reference |
| `make_values_fived16.py --check` and `--self-test` | PASS; no value changes; the two installed figures equal their E-A2 sources |
| `check_sec4_receipts.py` and its self-test | PASS (16/16, the 0.06 binding added; 19 perturbations rejected) |
| `build_all.sh` | PASS: paper 12 pp, note 135 pp, primer 15 pp; no "??". The paper's one overfull box is the base's (Table III) |
| the two-direction review (`review.md`) | nothing false, no lost fact. 4 Medium: all fixed. 8 Low: 6 fixed; the 1B wording and IV G's tension were then settled by the director's rulings (above) |
| the PRD-referee read (Gemini, verbatim beside this report) | the director's rulings 1–5, all applied (above) |
| the rater copy | `make_rater_copy.sh` exits 0; holddiff PASS |
| `check_held.py --fact-held` | the 3 known flags (G1:paper-g-08, G1:paper-s-08, G1b:paper-s-07) |
| `generate_manifest.py --check` | see the PR |
| local CI | see the PR |
| the reading copy | 33 pages: each changed paper page (1 and 3–12) followed by its base page, then the base's page 13; the note's pages 56, 58, 64, 74 and 78 (the added facts, and the modes figure with its caption), each followed by the base page where that text stood (56, 57, 64, 73, 78) |

Nothing is submitted, deposited or tagged.
<!-- absence-ok: the report quotes the paper's caveats, before and after, with their sources; it makes no claim of its own -->
