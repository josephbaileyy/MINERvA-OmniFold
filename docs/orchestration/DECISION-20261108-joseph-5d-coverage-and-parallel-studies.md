# DECISION 2026-11-08 — Joseph: declare the like-for-like 5D coverage test now, with the two departing bands read both ways; the band diagnosis and the prior-retention study in parallel; methods round 5

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The 1B pre-check, Part 1, reported** (`OUTCOME-20261108-1b-precheck-part1.md`, #933). Both drawn groups, flux and
  detector, REPRODUCE under rule S. Within the detector group, bands GEANT_Neutron and GEANT_Proton DEPART (rule K
  FAIL) in 6 and 4 cells, with no cause licensed.
- **The precondition of the authorized coverage test.** `DECISION-20261106-joseph-plateau-next-work.md`, "What is
  decided" item 2, authorized "a coverage test run", Joseph's override of 1B's rule (iii)
  (`DECISION-20261102-joseph-1b-redesign.md:78`), for a test built like-for-like. It was to start "only after Part 1
  … reports and shows whether a like-for-like construction holds for every group". Part 1 shows it for both groups,
  with the two bands above as the exception.
- **The director's recommendation, in conversation:** declare the test now; expect it to show under-coverage (the
  director's judgement, not a measurement: 2D under-covers at both tunes, `OUTCOME-20261108-cov2d-both-tunes-under-cover.md`);
  fix in advance a rule for the two departing bands, by default reading the test both with and without them, with
  the version without them as the primary reading. Its alternative was to diagnose the two bands first, which delays
  the start.
- **The director asked:** "Shall I start the declaration with that default? Writing a declaration launches nothing on
  the cluster."

## Joseph's answer, verbatim

> yes lets do it all, do you need me to open a lane for you?

sha256 begins `3590c51d437ca034`.

## What is decided (the director's reading of "do it all")

1. **The like-for-like 5D coverage test is declared now**, under the 2026-11-06 override of rule (iii).
   - **The two departing bands, fixed before any draw:** the test is read with and without GEANT_Neutron and
     GEANT_Proton. **The reading without them is primary.** The reading with them is reported beside it.
   - It is declared, priced, audited by coverage-5b-audit and bound by the director before anything runs. A campaign
     above half the group balance goes back to Joseph first.
   - The 1B campaign branch `decl/1b-staged-a2-1-20261103` stays as it is; the new test is a new declaration.
2. **The GEANT_Neutron and GEANT_Proton departure is diagnosed**, under a new declaration, in parallel. It does not
   gate the coverage test and cannot change item 1's primary reading after the fact.
3. **The prior-retention study starts.** It was authorized and paused until a lane freed (2026-11-06 decision, item 2);
   lanes are now free. It is declared, priced, audited and bound before it runs.
4. **Methods round 5.** The new results go into the methods draft, the ENS1 result when it lands, then the same eight
   blind reads as round 4 (PRD and JINST, Sonnet and Gemini). No wording is approved by this.
5. **Lanes.** Joseph offered to open a lane; the director uses the idle ones and asks if they run short.

## Not decided here

- **Item (c), the truth dependence,** stays excluded. Joseph was not asked about it.
- **Any wording** for the paper or the note, and the publication-scope decision (OI-205).
- **Any coverage claim.** Nothing here reads a coverage result in either direction.

If Joseph meant "all" more narrowly or more widely, he corrects this record.

Nothing is submitted, deposited or tagged.
