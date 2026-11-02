# DECISION 2026-11-02 (later) — Joseph: the quadrant sentence, Section IV in PRD style, three validation campaigns, and a limitations register

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The quadrant result.** GENCMP X (`FD-GENCMP-X-REPORT.md`, #686) found that the sixteen-cell result agrees with the
adopted 2D result in every quadrant, at every point of the bounded family:
- χ²₄ = 1.17 at r = 0 and 1.24 at r = 1, with p = 0.88 and 0.87;
- no |z| above 0.985.

**Two consults on the paper sentence** are verbatim in `FD-GENCMP-X-WORDING-{SONNET,GEMINI}-{PROMPT,ANSWER}.txt` (#689).
Gemini acted as a PRD referee, at Joseph's request ("can we ask an independent prd reviewer?", sha256 begins
`6b51d091f06644a5`). The two consults agreed on three points:
- the declaration's minimum text has two phrases that are false here;
- "any value from 0 to 1" overclaims, because only a one-parameter family was tested;
- the short candidate misstates what was measured.

The director merged their wording into a compact sentence. He checked that the paper's 0.141% (the three-observable
marginal's total, `sec_3d.tex:85`) and QA's +0.141% are different quantities.

**Joseph's question on Section IV**, typed during the turn:

<!-- absence-ok: Joseph's message, quoted verbatim; it quotes the paper's existing qualifiers -->
> I did a quick read of IV and here are some things I noticed. IV A has the sentences "its coverage at truths held out of its construction has not been validated... validated coverage did not pass" and "Passing that audit does not validate the block: its size and coverage have not been independently validated" What is the status on validating these things? Also is there a more typical way to present the last paragrpah of 4b in the PRD style? does all of it belong there or should some go to the note. Similarly IV C has "the covariance has not been independently validated ..." and "the coverage of this block and of the total covaraince has not been tested. We make no coverage claim..."

**The director's answer** had three parts:
- **The status of each statement:**
  - 1B stage 1 stopped at its N1 guard (0 node-h);
  - the run-period block's size cannot be validated with three groups, but its cause can be diagnosed;
  - 2D coverage has no campaign;
  <!-- absence-ok: cites the committed OUTCOME-20261005 record and the note line that discloses it; describes paper wording -->
  - an earlier version of the 2D statistical band failed a fixed-truth coverage test (`OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`). The note discloses this (`app_statmethods.tex:619`). The paper's "has not been tested" is true only of the current band.
- **A PRD-style consult.** Gemini, as referee, gave it. Its prompt and answer are verbatim in
  `state/2d-closeout/stageF/methods/secondary-results/referee-and-qualifications-20261101/sec4-prd-style-gemini-{prompt,answer}.txt`.
- **The director's caveat.** Gemini's IV C rewrite drops the failed 2D test, and any consolidation must keep it.

## Joseph's answers, verbatim

1. On the quadrant sentence:

   > Merged sentence (Recommended)

   sha256 begins `76a12c947990b853`.
2. On restructuring Section IV:

   > Consolidate (Recommended)

   sha256 begins `8be0713784ddc41e`.
3. On which validation work goes ahead:

   > 1B stage-1 redesign, Run-period diagnosis, 2D method coverage, I think what might be helpful is a running list of all the limitations listed in the note or paper with their location that both I and you can look at and work at closing them all (paper is highest priority over note)

   sha256 begins `91450b4ca1858f81`.

## What is decided

1. **The quadrant sentence.** `paper_body.tex:120`'s first sentence becomes the following, and the 0.141% marginal
   sentence follows as one clause:

   > "Summed over each of the four (pT, p∥) quadrants, the sixteen-cell result agrees with the two-dimensional result: the sums differ by −1.5 to +0.7 per cent, and with the covariance between the two results evaluated from the systematic variations they share, the four differences give χ² = 1.17–1.24 for four degrees of freedom (p ≥ 0.87), with no quadrant beyond one standard deviation. The statistical correlation, and that of four systematic terms that could not be evaluated directly, are bounded within a family of valid covariances, over which the agreement holds."

   Every number comes from the committed readouts (`fd/xcov/run/k/k.json`, `fd/gencmp-e/c-r/overlap_refined.json`)
   via values. This is #651 item 5's resolution.
2. **Section IV is consolidated in PRD style.**
   - IV A–C define each term neutrally ("a measure of …, not a calibrated bound").
   - One coverage statement sits in Limitations.
   - **That statement includes the failed fixed-truth test of the earlier 2D statistical band**, with the current
     band's status stated accurately.
   - Development history (for example "the first two tests of an earlier route … did not pass") moves to the note.
   - IV B's last paragraph is rewritten neutrally (a consistency benchmark, the post-hoc learner choice stated once,
     and the 1.03% exact-split difference).
   - No fact is lost from paper plus note.
   - A coverage result that lands later replaces its statement.
   - The paper lane drafts this, the director reviews it, and Joseph reads it before merge.
3. **Three validation campaigns go ahead,** each declared, priced, audited and bound before anything runs:
   - **(a) The 1B stage-1 redesign.** It follows the N1 attribution (connect 34). The bound stays at 10. The redesign
     is argued on grounds independent of the receipt's values. It goes to Joseph before binding.
   - **(b) The run-period diagnosis.** 12 per-playlist unfolds from the CFS-preserved event loops (#646), to look for
     the cause of the p∥ step and test the block's size.
   - **(c) The 2D method coverage.** A held-out-tune coverage ensemble for the 2D covariance, on 1B's staged design,
     with the covariance remade at each truth. It is priced first.
4. **A limitations register.**
   - **What it is.** A running list of every limitation stated in the paper or the note, with its location, owner,
     status and route to closure.
   - **Who uses it.** Joseph and the director both read it, and both work it.
   - **Priority.** Paper items first, then note items.
   - **Where it lives.** The director builds it as a shared, live page, seeded from the 2026-11-01 inventory (Q01–Q44),
     re-located against the current paper, and updated as each item moves.

Nothing is submitted, deposited or tagged.
