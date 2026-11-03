# DECISION 2026-11-02 — Joseph: probe a stabilised estimator before 1B stage 1; no fake-data bias term

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The referees.** Both blind PRD referees of 11-01 (`state/2d-closeout/stageF/methods/secondary-results/referee-and-qualifications-20261101/`)
list two items, among others they call disqualifying, that no campaign was working on:
- **(A)** the fake-data bias at the GiBUU-like hybrid and the q3 tilt, and the prior dependence missing from the budget;
- **(B)** the estimator's instability under input rounding (up to 2.6 statistical σ), and training and evaluating on
  the same events.

Sonnet ranks the run-period item and coverage as the most important (`sonnet-referee-answer.txt:146`). Those two are
separately in progress.

**The scope.** Joseph asked for both items to be scoped and priced ("yes scope and price both"; sha256 of the text plus
a final newline begins `14ad7ab765b1f3a4`). The scope report is
`state/2d-closeout/stageF/methods/secondary-results/scope-bias-stabilisation-20261102/REPORT.md` (#713, merged
0b75291b). Its findings:
- **A1, an assigned bias term from the graded truths:** passes them by construction, +5 distinct caveats (measured
  blind), double-counts C_model along the shared vertex directions, and nothing running can test it.
- **A2, a data-reweighted prior term:** +3 caveats; the GiBUU failure stays.
- **B0, reconcile only:** 0 node-h, ±0 caveats.
- **B4, a declared probe on simulated GiBUU-like pseudo-data before any estimator change.** Testing cross-fitting
  (B2) and tree regularisation (B3) costs about 3.2–6.4 node-h. A winner's re-run is about 45–115 node-h. Two things
  fall outside that:
  - the 5D lateral block cannot be remade (unpriced);
  - the s5p joint tests would be regenerated (208–416 node-h) or labelled as from the previous estimator.

**The independent consult.** Gemini read the scope with the referees anonymised (`CONSULT-GEMINI-{PROMPT,ANSWER}.txt`
beside the report):
- It rejects A1 and A2.
- It calls B0 alone insufficient.
- It would test B2 and B3 in B4 and drop the jitter ensemble (B1).
- It would hold 1B so that it runs once, on the final estimator.
- It calls keeping A stated acceptable only under a methods-paper framing.
- **Its proposed cell merge.** The scope's check of F0b's committed readouts finds that merging would not be expected
  to remove the failure:
  - R02 and R06 are the only cells with |z| > 2, but their z² sum to 38.1 against a full-covariance χ² of 171.0;
  - the 8-cell variant without R06 and R07 still fails, at 133.91/8;
  - the merge is also inadmissible after the data read (`DECISION-20261027-joseph-measurement-framing…:45-46`).

## Joseph's answers, verbatim

Asked whether the paper lane should declare a stabilisation probe on simulated pseudo-data, and whether 1B's stage 1
should wait for it:

> Probe, 1B waits (Recommended)

sha256 of the text plus a final newline begins `a830b9c7dd691581`.

The option as put to him: declare a probe of cross-fitting and tree regularisation on GiBUU-like pseudo-data, about
3–6 CPU node-h, which also reports the bias. 1B's amendment 2 keeps being written and audited, but stage 1 launches
only after the probe, on the winner or on the current estimator.

Asked which route for the fake-data bias (A):

> No bias term (Recommended)

sha256 of the text plus a final newline begins `2ec0d36fe07be140`.

The option as put to him: build neither A1 nor A2. The failure stays stated with its measured size, and A is decided
together with the measurement-or-methods-study framing once coverage and run period report.

## What is decided

1. **A stabilisation probe (B4) is declared**, testing:
   - **B2,** K-fold cross-fitting;
   - **B3,** tree regularisation (for example `min_child_samples` and depth limits).

   The probe leaves out the jitter ensemble (B1). The probe's declaration must fix, before any unfold:
   - **Inputs:** simulated GiBUU-like pseudo-data only, never the data. "No hyperparameter search was performed on
     data" must stay true.
   - **Criteria:** the predeclared stability bar of at most 0.3 (median) and 1.0 (maximum) statistical σ, and the
     bias no worse at any F0b truth.
   - **Readout, no criterion:** whether the bias at the GiBUU-like truth improves.
   - **Compute:** about 3.2–6.4 CPU node-h, within the standing grant (CPU only, jobs under 12 h, nothing written to
     CFS from jobs). It follows the usual audit and two-step binding.
2. **Adopting a winner as the single final estimator is decided separately,** after the probe reports. That decision
   includes the re-run, the lateral block and s5p. The probe alone changes nothing in the paper.
3. **1B continues on paper only.** Amendment 2 keeps being written and audited, and binding 3 may proceed. Stage 1
   does not launch until the probe has reported and the estimator is settled:
   - on the winner, if one is adopted;
   - otherwise, on configuration (e) as planned.
4. **No fake-data bias term.** Neither A1 nor A2 is built.
   - The IV H listing and the abstract's residual-bias sentence stay, with their measured sizes.
   - Item A is decided with the measurement-or-methods-study framing, once coverage and the run-period diagnosis
     report.
   - No cell merge is made.
5. **Not decided by these answers:** B0's reconciliation sentence (seeds inert; the bootstrap already carries the
   rounding spread). The director brings its wording to Joseph with the probe's outcome, through the usual PRD-referee
   read.

Nothing is submitted, deposited or tagged.
