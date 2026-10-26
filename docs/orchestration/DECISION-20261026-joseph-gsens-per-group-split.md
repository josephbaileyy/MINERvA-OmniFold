# DECISION 2026-10-26 — Joseph: accept the director's reading of G-FOLLOWUP and split the systematic family by group

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- G-FOLLOWUP (`state/measurement-paper/5d-community-20261024/FD-G-FOLLOWUP-REPORT.md`, PR #392) shrank the
  correlations of Stage G's reported covariance toward diagonal.
- **Every generator stayed at χ²/ndf ≳ 2.8 at every α.** Two families were shrunk: interaction alone, and interaction,
  flux, detector and lateral jointly.
- **But shrinking the joint family by 10 % roughly halved the χ²** for GENIE+MEC, NuWro and MnvTune v1. Interaction
  alone mattered much less.
- R04, the lowest-σ cell (4.2 %), is flux-dominated, and its flux correlation with its neighbours is 0.98–1.0.
- **The director's reading:**
  - the disagreement is robust, but its size is not;
  - the reported χ² rests mainly on the flux and detector correlation structure, through cell contrasts;
  - GiBUU behaves differently.
- **The director offered two steps:**
  - (a) shrink flux, detector and lateral each alone, to find which carries the sensitivity;
  - (b) decide how the 5D generator comparison is presented.

Joseph's answer, verbatim:

> I agree with your reading, lets do (a), and what are the options for (b) and whats your recommendation/others?

sha256 of the text plus a final newline begins `58a4c137ec5af8d8`.

## What is decided

1. **The director's reading stands as Joseph's working reading.** It is not printed wording. The 5D section's text
   comes to Joseph when it is written.
2. **(a) is approved:** the same shrinkage applied to flux alone, detector alone and lateral alone.
   - It runs at 0 node-h on a login node, through a declaration and a binding.
   - The pinned inputs are those of G-FOLLOWUP, with the role adopted.
   - It is descriptive, with no p values. It changes no covariance, cell or readout.
3. **(b) is a question.** The director answers it with options and a recommendation, and Joseph decides. Nothing is
   printed before he does.

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
