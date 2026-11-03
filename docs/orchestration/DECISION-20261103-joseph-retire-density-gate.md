# DECISION 2026-11-03 (latest) — Joseph: retire the ≤ 6 density gate; a referee gate and one targeted round

**Recorded by** the paper-tighten lane, as director.

**Supersedes** the density target of `DECISION-20261102-joseph-caveat-cut-list.md`, section "The density gate" (`:79`).

## What led to it

- **The cut-list round.** It left the distinct caveat count unchanged at 77, 9.93 per 1,000 words at `97e30dda`
  (`caveat-remeasure-20261102/after-711-97e30dda/`, #716). A fresh coder counts each fact of a merged paragraph as its
  own caveat.
- **The R-P9 re-price** (`caveat-remeasure-20261102/rp9-reprice-97e30dda/`, #728) moved whole secondary results to
  the note, built and blinded from the measured 77. No combination reaches ≤ 6 per 1,000; the lowest is 9.25–9.41.
  Reaching 6 would take removing about 21 more caveats from the main result's own sections.
- **The PRD-referee read (Gemini)** is in the same directory, `PRD-REVIEW-RP9-GEMINI-{PROMPT,ANSWER}.txt`.
  - **On the metric:** referees do not count caveats per 1,000 words, and the ≤ 6 target is "an arbitrary,
    counterproductive proxy".
  - **To keep:** the 2D benchmark against the published result, and the generator-sized truth-change test,
    condensed.
  - **To move to the note:** III A, IV D's background closure and V C.
  - **It quoted specific over-qualified sentences.**
- **Two points where it differs from earlier reads:**
  - It would move the input-rounding section. The 11-02 cut-list read objected to that, and Joseph kept it (MV15).
  - It calls the target "an arbitrary, counterproductive proxy", where the #707 read called about 6 per 1,000 words "an appropriate, realistic target".

## Joseph's answer, verbatim

Asked what should replace or keep the density target, since no legitimate move reaches ≤ 6 caveats per 1,000 words:

> Retire ≤6; referee gate + one round (Recommended)

sha256 of the text plus a final newline begins `83207df333ad1c7d`.

The option as put to him:
- drop the numeric gate from readiness;
- run one targeted round: the over-qualified sentences the referee quoted, plus moving III A, IV D's closure and V C;
- keep the 2D benchmark, input rounding and the stopped-gate disclosure;
- readiness then rests on a fresh two-referee read finding no over-qualification;
- density is still measured and reported.

## What is decided

1. **The ≤ 6 per 1,000 target is retired as a readiness gate.**
   - Caveat density is still measured with `remeasure.py` after each paper round, and reported in the register as
     information.
   - The readiness panel's density row becomes informational.
2. **The readiness gate for over-qualification** is the register's referee gate: a fresh two-referee read of the
   paper that finds no over-qualification left. It is run after the round below.
3. **One targeted round by the paper lane.** It works sentence by sentence against the base, keeping the fact ledger
   and the note-prints-it probes (`DECISION-20261029`), and it covers:
   - **(a) the over-qualified sentences the referee quoted:**
     - the E_avail comparison with other papers' definitions (Sec. II);
     - "No finite-ensemble correction is applied" and the block's size interval wording (IV A);
     - "the change is not a smaller bias or a validated uncertainty" (the fake-data section);
     - Table III's footnote on the hydrogen sample's checks;
     - the χ² bands' "are not intervals" sentence;
   - **(b) the whole moves to the note, with pointers:** III A, IV D's background closure and V C. Their facts print
     in the note already (3 of 3, 5 of 5 and 2 of 2, #728).
4. **Kept in the paper:**
   - the 2D benchmark (IV B);
   - the input-rounding section (IV F);
   - the stopped-gate disclosure in the Limitations.

   The round may tighten their wording. It may not move or remove the facts.
5. **The process.** Each changed sentence is given before and after in the round's REPORT. A fact that would leave
   both paper and note is a stop. The REPORT goes through a PRD-referee read and to Joseph before merge.

Nothing is submitted, deposited or tagged.
