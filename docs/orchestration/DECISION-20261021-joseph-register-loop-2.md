# DECISION 2026-10-21 (second) — Joseph: lift the register-loop cap; both documents in scope; disclosures may move to the note; calibrate the raters

**Recorded by** the paper-tighten lane, as director (Stage F).

**What led to it.**
- The first register loop (DECISION-20261021-joseph-ai-ack-and-register-loop.md) ended at its three-round cap.
  - GPT-6.1-sol rated the methods paper 3/5 and Gemini rated it 3.5/5 (METHODS-IMPLEMENTATION.md §13).
- Joseph said the plan is to put the methods paper and the analysis note on arXiv at the same time. He asked why the
  wording could not reach 4.5–5.
- The director gave four causes:
  - the raters score the `\pubhold` placeholders and the GitHub citation of the note;
  - one rating per model per round is noisier than the change being measured;
  - the director's rule kept every limitation and post-hoc disclosure in the paper, which is GPT's main complaint;
  - the writers patched sentences rather than rewriting from the outline.
- The director proposed calibrating the raters, keeping the holds out of what the models rate, and rewriting from the
  outline.

Joseph's answer, verbatim:

> I suppose we can keep the holds out of the pdfs/outputs we give to the models right? maybe you or a subagent or a
> dedicated session can do the pass to accomodate GPT's main complaint? I think the limitations and after-the-fact
> disclosures don't need to be in the paper as long as they are mentioned somewhere, like in the note or another
> supplementary material. How did the outline review go and why do you assume that rewriting each section fresh
> wouldn't work? Yes, calibrate the raters and note which prompts are the best. Lift the cap and when I said both notes
> I meant both the methods paper and analysis note

sha256 of the text plus a final newline begins `423dfdd416efcdc3`.

## What is decided

1. **The cap is lifted.** This amends DECISION-20261021 item 2.
   - The loop no longer stops after three rounds.
   - Every other rule of that item stands:
     - presentation and language only;
     - an independent two-direction review of each round before rescoring;
     - what remains goes to Joseph with the record.
   - The stopping rule is replaced; see item 5.
2. **Both documents are in scope.** That is the methods paper and the analysis note. Joseph plans to post both to arXiv
   at the same time.
   - Posting is Joseph's act, after his own review and Ben's. Nothing is submitted, deposited or tagged.
   - The paper is to cite the note as its arXiv companion. Until an identifier exists, that citation is pending
     author text.
3. **Holds are kept out of what the models rate.**
   - The rater copy is built with `\pubhold` rendering nothing, and with any sentence that exists only to carry a hold
     removed.
   - The copies built for Joseph and for deposit are unchanged. They still render every hold until Joseph supplies the
     text.
4. **Limitations and post-hoc disclosures may move out of the paper.** Each may move to the note, or to other
   supplementary material, provided:
   - it prints there;
   - the paper points to where it prints.

   This replaces the rule recorded in REVERSE-OUTLINE-R2.md §5, that each one stays in the paper as at least a clause.
   DECISION-20261021's "no fact dropped" now means no fact leaves both documents.

   **The director's reading, stated for Joseph to confirm or override.** A qualifier stays in the paper only where
   leaving it out would make a sentence the paper prints false as read. For example, the familywise-error-rate claim
   holds only under its stated assumptions, so "under the stated assumptions" stays beside it, and the derivation of the
   assumptions moves.
5. **The raters are calibrated before the next rescoring, and the best prompts are recorded.**
   - The calibration rates published papers and our own versions with several prompts, several runs each, with
     identifying front matter removed from every document.
   - It measures, for each prompt:
     - how far apart published papers and our drafts score;
     - how much one document's score varies between runs;
     - whether the "revised several times" framing moves the score.
   - It ranks the prompts by these measurements.
   - **The new stopping rule** is fixed from the calibration and recorded before the rounds it governs. It is:
     - the published anchors' calibrated score;
     - or a blind side-by-side comparison of the new and previous versions that no longer prefers the new one in
       either model, whichever comes first.

## Answered in the same exchange (no decision)

- **The outline review.**
  - The reverse outline (REVERSE-OUTLINE-R2.md) drove round 2.
  - After it, both models called the sequence conventional and needing no major restructuring.
  - GPT said Sec. VI should stay as the synthesis.
  - Their remaining outline asks (rounds r10 and r11):
    - move "Why unfold before testing" to the opening of Sec. VII (GPT);
    - move the Sec. VII C–D procedure to the note or an appendix (both);
    - move Table I or fold Sec. VI elsewhere (Gemini). These two proposals conflict with GPT's.
- **Rewriting each section fresh.** The director did not argue against it. The director proposed it, as the likelier
  route to a register change than patching sentences. Its risk is losing facts, and the two-direction review and a
  fact ledger cover that risk.

## Not changed

- Claims and numbers.
- The `\pubhold` text, the release text and the funding text, which are Joseph's.
- No outward act. Nothing is submitted, deposited or tagged.
