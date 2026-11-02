# DECISION 2026-11-01 (latest) — Joseph: 1B proceeds as a staged method-coverage design

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The previous decision.**
  [`DECISION-20261101-joseph-1b-keep-block-redesign-test.md`](DECISION-20261101-joseph-1b-keep-block-redesign-test.md)
  (#654) kept S1's full-simulation block. Next it was to run a redesigned test (mode D), and if that passed, the
  coverage ensemble.
- **The redesign's finding.** Mode D's declaration (#655, head `55435ec0`, acknowledged by `coverage-5b-audit`) found
  that no pseudo-data construction compared with the reported block M has power. M depends on the truth point at
  which it is made: I2's F_truth is in the window in 1 of 16 cells. The audit's corrected reasoning is in its comments
  on #655.
- **What was left, and its limits.**
  - The fallback, a symmetry check κ at the nominal truth, is expected to pass by closure at first order.
  - A κ PASS licenses only method coverage, graded against a block remade at the ensemble's own truth.
- **The consult.** An independent Sonnet consult is verbatim in
  `state/measurement-paper/5d-community-20261024/FD-1B-MODED-CONSULT-{PROMPT,ANSWER}.txt` (#660). It recommended
  option (c). The director agreed. The reasons:
  - the paper's qualification (`paper_body.tex:80`) is about coverage "at truths held out of its construction", which
    is method coverage at held-out truths;
  - κ alone cannot change the paper.

## Joseph's answer, verbatim

Asked how 1B should proceed, now that the reported covariance cannot be tested directly against simulation:

> Staged method-coverage (Recommended)

sha256 of the text plus a final newline begins `fd622fc17106ead8`.

## What is decided

1. **One staged declaration,** by coverage-5b. coverage-5b-audit reviews it, and the director binds it before anything
   runs.
   - **Stage 0:** κ (#655's Dnom against uncarried A), with a hard gate. A κ FAIL stops the campaign, and the result
     goes to Joseph.
   - **Stage 1:** a method-coverage ensemble at the GENIE v3 tunes G18 and AR23.
     - The declaration must show from the records that neither tune was used to build C_model or the estimator.
     - Pseudo-data are drawn with every uncertainty group (statistical, flux, interaction, detector, lateral,
       normalization), not interaction only.
     - Each pseudo-dataset is unfolded with the nominal simulation by the production procedure.
     - At each tune, the covariance is rebuilt by the same procedure as the reported one, at that tune's truth.
   - **Optional, only if cheap:** a plug-in truth reweighted to the unfolded data. This needs the unfolding's final
     truth weights exposed, which is a code change bound with the rest.
2. **Grading.** Fixed before any number is read:
   - per-tune pulls and χ² on the covariance's non-null subspace;
   - the in-interval fraction per cell, with a binomial interval;
   - a pass/fail rule per tune.
   With two tunes, the result is per-tune statements, not a population coverage rate.
3. **The truth dependence is a readout.** Each truth's blocks against the nominal block (A_tune/A_nom), and against M
   where a plug-in truth exists. It is reported as a fact beside the coverage result.
4. **Price.** From measured per-unfold costs (I2's 850 s maximum, S1's per-replica and per-universe costs), before
   binding.
   - The standing compute approval covers it.
   - A campaign above half the group's balance comes back to Joseph.
5. **The paper, in each outcome:**
   <!-- absence-ok: quotes the paper's existing qualifier (paper_body.tex:80) that a pass would replace -->
   - **Pass:** the paper's coverage qualifier at `paper_body.tex:80` is replaced by the measured result, with its scope: held-out
     tunes, a covariance remade by the same procedure, and per-tune χ² and in-interval fractions. The truth dependence
     of the block is stated as a fact.
   - **Failure:** reported by cell and tune, as under-coverage. No covariance is inflated without Joseph.
   - **Until a result lands:** the stopped-attempt disclosure stays.
6. **Mode D is folded into stage 0** rather than run on its own (κ only, or κ + Ddl, as #655 declared it). Its κ becomes
   stage 0. #655 is closed unmerged, or merged as the record of the design's finding, whichever the lane prefers, with
   the director's ruling recorded.

Nothing is submitted, deposited or tagged.
