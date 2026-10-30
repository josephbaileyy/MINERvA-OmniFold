# DECISION 2026-10-29 (later) — Joseph: limitations and disclosures may leave the paper if the note keeps them

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- Joseph relaxed B2 for implementation detail kept in the internal ledger
  ([`DECISION-20261029-joseph-relax-b2-internal-ledger.md`](DECISION-20261029-joseph-relax-b2-internal-ledger.md),
  #521). The director's reading kept limitations, disclosures, qualifiers and reported numbers in a published document,
  and offered to widen it.
- r22's preliminary tallies: the protected share of the gaps is 6 % (paper) and 2 % (note) for sol2, and about 50 % for
  gemini.

Joseph's words, verbatim, in his own message:

> I think we can relax it more too if that is what the reviewers are suggesting. or at least they can go from the paper but stay in the note

sha256 of the text plus a final newline begins `812fe7b841862e67`.

## What is decided

1. **Limitations, after-the-fact disclosures and their supporting detail may leave the paper when the note keeps
   them.**
   - This covers the honesty-required facts (inventory §4, C1–C23). It also covers the paper placements set earlier for
     them, including "Interval coverage has not been validated." in §I and the four low-stability cells in the
     Limitations.
     <!-- absence-ok: quotes the paper's printed sentence by name; not a claim that something has not been run -->
   - Each move leaves a pointer in the paper to the note's section, and a probe that the note prints the fact.
   - The classification rule "move it to the note where the result it bounds stays" (r22 `RULES.md` §4, class 1) is
     relaxed accordingly. Such a move is STRUCTURE.
2. **What still holds** (the director's reading, which Joseph may override):
   - **The truth guardrail:** a qualifier stays where its omission makes the paper's own sentence false (B1 and the
     KEEP list, B3). Moving a limitation is allowed. Leaving a paper sentence that the limitation was needed to keep true
     is not.
   - **The paper keeps one pointer to its limitations in the note,** so a reader of the paper alone learns that they
     exist.
   - **Claims (A7), the title and abstracts (A4, A5), Data Availability (A1) and the FROZEN and gate-bound phrases
     (B4)** are unchanged by this decision.
3. **"Relax it more", out of both documents:** Joseph's words make this conditional on the reviewers suggesting it.
   - When a rater's gap asks for a limitation, disclosure, qualifier or reported number to leave the note as well, the
     gap goes to Joseph as a named choice, quoting the sentence and the rater's reason. It is not done by default.
   - Implementation detail and provenance already may leave both documents under #521.

## Not changed

- Every claim and number. Nothing is submitted, deposited or tagged.
