# DECISION 2026-10-25 — Joseph: caveats follow the practice of comparable published documents

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- `DECISION-20261025-joseph-r18-history-to-note.md` set r18's brief for the passages the raters quoted.
- The director then described to Joseph how PRD papers present caveats:
  - the final procedure, in the present tense;
  - validation of the final method only;
  - superseded versions left to a companion document;
  - deviations from a predeclared procedure stated briefly, with their consequence;
  - each caveat stated once, quantified and positive-first where the facts allow.

Joseph's words, verbatim:

> can we handle caveats the same way PRD papers do?

sha256 of the text plus a final newline begins `2ee72b8f25bc8032`.

> at least the paper should handle it the same way similar length PRD papers do and the note should handle it the same way similar length notes do

sha256 of the text plus a final newline begins `5f940c532b84fb7e`.

## What is decided

1. **Each document follows comparators of its own kind and length.**
   - **The methods paper** (about 9,200 words, 13 pp) follows published PRD papers of similar length. The paper's
     rater anchors are of that length: 8,148–8,992 words blinded (`rater-calibration/REPORT.md` §1).
   - **The analysis note** (about 56,000 words, 121 pp) follows published long technical documents of similar length,
     not PRD letters or short articles.
2. **First, a comparator study of caveat handling.**
   - It is read-only, with no cluster work, and the paper rewrite lane does it. It extends
     `register-prd-study/REPORT.md`, whose corpus was chosen, not length-matched or sampled.
   - **Sets:**
     - at least 4 published PRD papers of 7,000–12,000 words in the genre (neutrino cross sections, unfolding, ML
       methods for HEP);
     - at least 3 published technical documents of 30,000 words or more. Examples are long PRD or JINST technical
       papers, or public collaboration technical notes.
   - **Each comparator** is verified on its arXiv abstract page, as before.
   - **For each kind of caveat** (item 3), it measures:
     - how often the comparators state it;
     - where they put it;
     - how they phrase it;
     - whether they quantify it or assign an uncertainty to it.
   - It reports the same measures for our two documents.
   - **The result is the brief:** per-document rules that replace the director's summary above wherever the two
     differ. It is committed before the round it governs.
3. **The five kinds** used to sort our caveats, with the provisional treatment until the study reports:

   | kind | paper (provisional) | note (provisional) |
   |---|---|---|
   | (a) the history of superseded work | leaves the paper; it prints in the note | kept where it bears on a quoted result; otherwise to the internal records |
   | (b) a deviation from a predeclared procedure | one sentence where the result is reported, with its consequence | the full account |
   | (c) an untested property or an effect that is not included | stated once, as a plain declarative, quantified where a number exists | stated where the method is described, and in the note's limitations |
   | (d) scope | stated once, in the abstract and Sec. I (R1) | stated once, in the introduction |
   | (e) process vocabulary | removed | removed |
   <!-- absence-ok: names categories of caveat; not a claim that any result is absent from the repository -->
4. **The guardrails are unchanged.**
   - A qualifier stays where leaving it out would make a printed sentence false as read.
   - No number or claim changes, and no fact leaves both documents.
   - agy agrees on every printed passage.
   - The blind pairwise comparison and the calibrated rating decide adoption.
5. **The limit.** Comparators often turn a caveat into an assigned uncertainty, such as a non-closure systematic. Here
   that would change numbers and claims, so the register rounds do not do it.
   - The lane may list where it would be possible, as options for Joseph.
   - Each needs its own decision, and compute where a measurement is missing.

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
