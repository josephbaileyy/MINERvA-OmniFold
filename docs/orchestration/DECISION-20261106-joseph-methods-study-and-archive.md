# DECISION 2026-11-06 — Joseph: work toward the methods study; archive the measurement-framed paper; both options go to Ben

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The package.** The publication-scope package (OI-205) was merged with the director's recommendation in section 6
(#827,
`state/2d-closeout/stageF/methods/secondary-results/scope-decision-package-20261106/REPORT.md`). Its recommendation:
- retire the 5D-headline option (A);
- recommend option C, a methods and benchmark study, decided now;
- keep B1, a 2D-led measurement, as a conditional alternative with three stated conditions;
- decline B2.

**The independent read.** It was taken by agy, reading as a PRD referee, and committed verbatim. That read moved the
director's first draft from B1 to C.

**Joseph's first question.** He asked why 5D can't be a measurement. The director answered with the four standing items:
- 1B ended on a terminal §2b STOP without a coverage reading (#832);
- B4 NONE_PASS, with rounding-level shifts of up to 2.6 σ_stat at worst;
- generator-sized fake-data bias in R02 and R06;
- REF-G1's measured algorithm dependence.

The unexplained run-period step comes on top. He also gave the route that would be needed: an override of (iii), a
redesigned post-hoc 5D coverage test, a conservative inflated error budget, and a fresh referee read. He then put the
framing question again, with four options:
- the methods study, decided now (recommended);
- pursue a 5D measurement;
- a 2D-led conditional measurement;
- wait for COV2D.

## Joseph's answers, verbatim

1. To the first framing question:

   > wait why can't 5d be a measurement?

   sha256 of the text plus a final newline begins `cf0dfd975ac5f9fe`. This is a question, not a decision; the director
   answered it as above.
2. To the second framing question:

   > okay can you keep the previous work as an artifact? Lets do the methods study and I can bring both options to Ben

   sha256 begins `44ff44683cac1ade`.
3. A clarification of "artifact", sent while the director was building it:

   > not like claude artifact artifact, but as an archival package of the latest measurement framed paper

   sha256 begins `b25f09cf609bc018`.

## What is decided

1. **The working target is the methods and benchmark study** (option C).
   - The paper lane reframes toward it.
   - Every wording choice goes through a PRD-referee read before it reaches Joseph.
   - No paper text merges without Joseph's wording approval.
2. **The measurement-framed paper is archived** as an in-repository package. It is not a claude.ai artifact:
   `state/2d-closeout/stageF/methods/archive-measurement-framed-20261106/`. It holds:
   - the PDFs built from main at `3bd6e3ce` (main_paper 13 pp; main_note 136 pp);
   - a manifest of every source blob at that commit;
   - the build log, the toolchain and the rebuild commands.
3. **Joseph takes both options to Ben:** the methods study and the measurement framing. The director doesn't contact
   Ben. If Joseph returns with a different framing after that conversation, this decision is revisited then.
4. **Unchanged:**
   - The campaigns run as bound: COV2D's readout enters the methods study whichever way it reads, and d1/d2 proceed.
   - (iii) is not overridden.
   - Publication, release and contact acts stay Joseph's.

Nothing is submitted, deposited or tagged.
