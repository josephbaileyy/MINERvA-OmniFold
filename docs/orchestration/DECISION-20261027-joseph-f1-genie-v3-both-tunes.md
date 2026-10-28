# DECISION 2026-10-27 — Joseph: the F1 bias test uses both GENIE v3 tunes

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md` item 1 approved 1A, the GENIE v3
  held-out bias test.
- `FD-DIRECTOR-RULINGS.md` §4 makes the GENIE v3 configuration Joseph's choice. LIMITATION-PLAN's 1A names two tunes,
  both at GENIE v3_04_00 on CVMFS: G18_10a_02_11b and AR23_20i_00_000.
- The 5D measurement session asked which to use, and the director put the question to Joseph.

Joseph's answer, verbatim, the option he selected:

> Both tunes (Recommended)

sha256 of the text plus a final newline begins `2e050077c7a8d1fa`.

## What is decided

1. **F1 generates and grades both tunes:** G18_10a_02_11b and AR23_20i_00_000. They are two held-out truths, each the
   generator's own shape, with no amplitude.
2. **The seeds are fixed a priori, and no earlier product has used them.** They are declared before any F1 product is
   read.
3. **The cost stays near the priced 0.84–1.25 node-h** for both, in jobs under 12 h. The binding sets the exact
   budget.

## Not changed

- F1 is a bias test, not a coverage test. Grading follows FD-PLAN's statistics and triggers.
- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
