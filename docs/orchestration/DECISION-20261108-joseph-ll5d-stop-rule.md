# DECISION 2026-11-08 (later) — Joseph: the like-for-like 5D coverage test (LL5D) has no stop rule fixed in advance; each STOP comes to him, and he decides then

**Recorded by** the paper-tighten lane, as director.

## What led to it

- `DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md` (#934) opened the LL5D declaration under Joseph's
  2026-11-06 override of 1B's rule (iii) (`DECISION-20261102-joseph-1b-redesign.md:78`).
- cov2d, drafting `LL5D-DECLARATION.md` (#936), flagged as Joseph's whether the new test carries its own analogue of
  rule (iii) (its §8, row R3). Its default until he ruled was fail-closed: any STOP to the director and Joseph,
  unrepaired, nothing relaunched.
- The director put it through AskUserQuestion, recommending "Any STOP ends it":

  > Your November 6 override let a like-for-like 5D coverage test run despite 1B's "second STOP ends it" rule. Does
  > the new test get its own stop rule? (A STOP is a fail-closed check firing during the run, e.g. a cell's expected
  > count going negative. Every STOP comes to you unrepaired either way.)

  The options were "Any STOP ends it (Recommended)", "One repair allowed" and "Decide at the STOP".

## Joseph's answer, verbatim

> Decide at the STOP

sha256 begins `4a95fb05e2c5f165`.

## What is decided

1. **No stop rule is fixed in advance for LL5D.** Each STOP goes to the director and to Joseph unrepaired. Nothing
   relaunches, and no repair is declared, until Joseph decides for that STOP.
2. **What a STOP still means:** the run halts where the declaration's fail-closed check fires. The STOP is recorded
   as it fired, before any decision.
3. **Unchanged:** an INVALID (infrastructure, no reading) may be rerun unchanged under the director's operational
   authority, as for every campaign.
4. **A disclosure that the paper and the note will carry if any repair follows a STOP:** the repair was chosen after
   that STOP was seen.

## Not decided here

- LL5D's R5 (the wording of the two readings, and the note's text on the denominator clip) and R8 (the director's
  four-evaluation mapping of the 11-03/11-04 variance-gate budget, which Joseph may override).
- Any wording, or any coverage claim.

Nothing is submitted, deposited or tagged.
