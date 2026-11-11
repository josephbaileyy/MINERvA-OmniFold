# DECISION 2026-11-09 — Joseph: the second five-observable coverage test's pre-written cases print a per-tune, per-variant status, label adaptive routes "Descriptive", and use the approved pass wording; nothing is locked

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The pre-read.** The paper (#977) pre-writes the text for every outcome of the second five-observable coverage test
  (LL5D). A Sonnet and a Gemini agent referee read the cases (`secondary-results/preread-outcomes-20261109/`, #998),
  and the director's rulings were applied on #977.
- **The style integration** (#977 at `46ed923d`, restored at `9b6f5cb2`) rewrote the cases in plain declarative form.
  It followed `DECISION-20261102-joseph-1b-redesign.md` item 4 strictly: clipping detail moved out of the main text,
  there is no "does not test" clause, and R5's facts are printed once.
- **The director put three questions to Joseph:**
  - (a) the pass wording;
  - (b) the label for a result reached after the test continued past a check, or after a repair;
  - (c) the Table 1 status when the variants or tunes disagree.
- **The independent read.** A fresh codex-school2 gpt-6.1-sol session read (b) and (c), read-only at `46ed923d`
  (`secondary-results/independent-read-coverage-status-20261109/`, with `answer.txt` verbatim). It recommended:
  - the status "Descriptive" for adaptive routes;
  - a status for each tune and variant in place of "Mixed";
  - the rank-16 condition on the carry-over sentence.
  The director recommended adopting all three.

## Joseph's answer, verbatim

> yes lets apply it

sha256 of the text plus a final newline begins `2a2af2dcc3d31c56`.

## What is decided

1. **(a) The pass wording** is the integrated text at `9b6f5cb2`, with three additions:
   - "The graded covariance includes the model term, whose role is to cover each tune's departure from the
     simulation";
   - "The data result remains an illustration";
   - on the carry-over sentence, the declaration's condition for the joint reading, that both matrices have rank 16
     (`LL5D-DECLARATION.md`:317-324).
2. **(b) Adaptive routes.** A run that continued past a check fixed in advance, or ran with a repair after a stop,
   gets the Table 1 status **Descriptive**, whatever its readings.
   - The readings print in the Result text.
   - The caption defines this status: the criteria fixed in advance were applied, but the run continued, or was
     repaired, by a decision made after a check was seen.
   - The abstract and §6.3 keep their disclosure.
   - Supplement S9 records what the reader needs: the exceeded quantity and its bound, what was visible when the
     decision was made, its reason, every repair, and the fact that the gate sample shares its first 300 seeds with
     the coverage pseudo-experiments (`LL5D-DECLARATION.md`:250-255).
3. **(c) No "Mixed" status.**
   - Table 1 gives one entry for each tune and variant ("No under-coverage detected", "Under-coverage flagged" or
     "Invalid"), with the primary variant marked.
   - The abstract's per-variant wording stays.
   - No reading of a secondary variant is promoted over the primary, and no overall "any flag" status is formed.
4. **Nothing is locked.** Every sentence stays open to the PRD-referee read and to Joseph. A coverage sentence prints
   only from the test's outcome record, once it lands.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the case wording and the status scheme as Joseph's choice.
- **Not citable for:** any coverage result; the independent read's views as findings; a locked wording.

Nothing is submitted, deposited or tagged.
