# DECISION 2026-11-20 (c) — Joseph: App. F leaves the posted note for the records; the acknowledgement points to App. D.1 and lists GPT-6.2 Sol and Sonnet 5.5; the Figs. 6/7 takeaway drops its descriptive label

**Recorded by** director-helper-3, for the director, who relayed Joseph's words.

## What led to it

1. **Joseph's request.** Joseph asked for a referee review of App. F (`app_verification.tex`, "How the note's numbers and statements are checked"), saying he was "not too opposed to just removing it". [DECISION-20261120b](DECISION-20261120b-joseph-figs67-appf-records-pointer.md) item 2 had approved App. F as merged on the draft.
2. **The referee review.** A codex2 referee (gpt-6.2-sol) reviewed it. The report is `~/codex-reports/referee-appf-20261120/report.md`, not in the repository (sha256 `ec604656e5a1c3a70989ead400276f582d4fb9285e9685b27cf572109d2cc03f`). Its verdict: "(c). Remove Appendix F from the posted note and keep its contents in the records document." It recommends replacing the AI-use acknowledgement's App. F sentence with "For the scope and limits of result replay, see Appendix D.1."
3. **The options.** The director offered Joseph three:
   1. as the referee says;
   2. keep App. F;
   3. remove it, but add a sentence on the period when the readers were Claude models only.
4. **Joseph's follow-up.** Joseph's second message below questions the Figs. 6/7 takeaway's descriptive label and the acknowledgement's "Sonnet 5 or 5.5", approves adding GPT-6.2 Sol, and asks for a current PDF.
5. **The Sonnet version.** The acknowledgement says "Sonnet 5 or 5.5" because DECISION-20261114 records that the version was not logged and that Joseph gave it as 5 or 5.5. Joseph asked whether timing could settle it (his third message below). The director reported the transcript results, and the recorder recounted the replies on 2026-11-20:
   - The Claude Code transcripts under `~/.claude-school/projects` and `~/.claude-personal/projects` hold 2,291 Sonnet replies (1,969 and 322), dated 2026-10-22 to 2026-11-17. Every one is model `claude-sonnet-5-5`. No `claude-sonnet-5` ID appears.
   - The repository's Sonnet consults postdate the start of Sonnet 5.5 use. The two cited commits, 2a9e2aae8 and f2cbc54cb, are both dated 2026-11-01.

## Joseph's words, verbatim

Three messages of 2026-11-20, quoted as relayed, typos and spacing included; each sha256 is of the text plus a final newline.

1. Answering the three options:

   > yeah lets do 1 and remove App F.

   (`1b67e3499a2003ad1aab7ca68b9232a2346ec11a039dee94ac5b723bc073de91`)

2. The follow-up:

   > is it necessary to say 'this comparison is descriptive'? It feels pretty obvious?  Also yes you should add GPT 6.2 sol. Also why do we say Sonnet 5 or 5.5? this probably should be an 'and' like everything else right? after,  can you give me an current version of the pdf to read?

   (`01eaaa060f11c4275a7f2566b2c273e2cb1ef48eacf23ca35908f073d5969acb`)

3. On the Sonnet version:

   > its true it may not be in the logs but we can't using timing and release dates to figure it out? I'm pretty sure I always used the latest model

   (`2bbf68f9a708a4a652e29472f5824e4bb2fad4884f33435388fcf38de8e2a318`)

## What is decided

1. **App. F leaves the posted note.**
   - `app_verification.tex` moves verbatim to the records document.
   - This supersedes DECISION-20261120b item 2 (App. F approved as merged) for the note's placement only. App. F's contents stay as approved, in the records.
2. **The acknowledgement's App. F sentence is replaced.**
   - The AI-use acknowledgement's sentence in `main_note.tex` that points to App. F (the one ending `described in` / `App.~\ref{app:verification}.`) becomes: "For the scope and limits of result replay, see Appendix D.1."
   - Appendix D.1 is `app:release`, "Result package and reproduction limits", in `appD_release.tex` (D.1 in the build at c8d55e50f).
   - This updates the acknowledgement that [DECISION-20261114-joseph-ai-use-statement](DECISION-20261114-joseph-ai-use-statement.md) governs, and is limited to that sentence of the current draft. DECISION-20261114's approved wording had no App. F sentence.
   - The acknowledgement changes only by this replacement and by items 4 and 6.
3. **The Figs. 6/7 takeaway prints without "This comparison is descriptive."**
   - The takeaway is still stated as what the panels show.
   - This supersedes DECISION-20261120b item 1's "It is labeled descriptive" for the printed label only.
4. **The acknowledgement's OpenAI list adds GPT-6.2 Sol.**
   - It joins the list of OpenAI GPT models used through the OpenAI Codex agent.
   - The rest of the list is unchanged.
5. **Who does it.** journal-editor moves App. F once this record is on the draft.
6. **The acknowledgement lists "Sonnet 5.5".**
   - It replaces "Sonnet 5 or 5.5" in the list of Claude models.
   - This is decided on the log evidence above, with Joseph's question as the authority.
   - It supersedes DECISION-20261114's "Sonnet 5 or 5.5" (Joseph's best knowledge at the time) for the printed version only.

## Not decided here

- Any other acknowledgement wording.
- Option 3's sentence on the Claude-only reader period.
- Any paper wording.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - moving App. F verbatim from the posted note to the records document;
  - replacing the acknowledgement's App. F sentence with "For the scope and limits of result replay, see Appendix D.1.";
  - printing the Figs. 6/7 takeaway without "This comparison is descriptive.";
  - adding GPT-6.2 Sol to the acknowledgement's OpenAI list;
  - printing "Sonnet 5.5" for "Sonnet 5 or 5.5" in the acknowledgement.
- **Not citable for:**
  - dropping App. F's contents from the records;
  - any other acknowledgement wording;
  - a complete census of model versions used outside the logged transcripts;
  - any paper wording.

Nothing is submitted.
