# Writer brief: analysis-note register batches (shared by every batch)

`S` = `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad`

## What the note is now

The author will post two documents to arXiv together:
- a 13-page PRD methods paper;
- its companion analysis note, about 119 pages: "Unbinned OmniFold analysis of MINERvA charged-current inclusive data:
  analysis note". The note is the paper's supplementary material.

Records have been taken out of the note. Provenance, superseded values, withdrawn results and history now live in a
separate internal records document, `main_records.tex`, which is never posted. The posted note cites it as
`\cite{NoteRecords2026}`, giving the tag or heading. That is the only form in which the posted note may point to
records.

A glossary batch has already fixed the note's vocabulary:
`S/wt-note-b3/docs/orchestration/state/2d-closeout/stageF/methods/note-g0/GLOSSARY.md`. Use its terms. Do not
reintroduce "in use", "adopted", "frozen", "footing", "gate", "receipt", "lane" or "branch" as internal jargon.

## Why this batch

A baseline rating used P1N, a rubric-anchored 1–5 register prompt, with GPT-6.1-sol.
- Published long technical papers (T2K PRD 91 072010; ProtoDUNE-SP JINST 15 P12004) score 3.875.
- The note's chapters score 2.25–3.0.
- The complaint types, ranked:
  1. internal bookkeeping;
  2. stacked defensive hedging;
  3. project jargon;
  4. development history;
  5. software detail in prose;
  6. editorial meta-text ("Three things have to be said …");
  7. process narrative;
  8. overdense sentences.

The rated quotes for your chapters are in `S/xmodel/note-cal/runs/` (files `P1N__<piece>__*.md`) and in
`S/xmodel/note-cal/complaints.json`. Read them.

**Target.** The batch's chapters should read like a well-edited long technical write-up for specialists, such as a
long PRD or JINST paper or a detailed supplement:
- results and methods stated directly;
- each claim once, with its scope built in, not appended as a disclaimer;
- procedural detail kept where a specialist needs it to judge or reproduce a result;
- no record-keeping tone;
- no "we record", "this is stated so that", "an earlier version of this sentence";
- no history of how the analysis got here, unless a reader needs it to interpret a result. If one does, say it once,
  as a fact about the result.

The note may stay long and dense where the content needs it. Density is not a defect in this genre. Bookkeeping is.

## Hard rules

1. **No fact or number is lost, and no claim is strengthened.**
   - A number, limitation or disclosure may leave the prose only if it moves to the records document, cited by
     `\cite{NoteRecords2026}` with a tag or heading that exists there. You may NOT edit the records document's moved
     text.
   - A pure record (an earlier value, the history of a decision, who decided what when) may leave the posted note when
     the records print it.
   - Limitations and caveats that bound a result stay in the note, stated once beside the result.
2. **The guardrail.** A qualifier stays wherever leaving it out would make a printed sentence false as read.
3. **Do not add, remove, rename or reorder any `\label`, section or subsection.**
   - The paper cites the note's section numbers through xr-hyper, and the records document references the note's
     labels.
   - Paragraph headings (`\paragraph`) may be reworded.
4. **Do not edit:**
   - `paper_body.tex`, `main_paper.tex`, the primer, the PET note, `values*.tex`, figures, `.bib` files;
   - `main_records.tex` and anything it inputs exclusively (`app_provenance.tex`, `app_history.tex`, `*_records.tex`);
   - build scripts and checks;
   - the acknowledgments, the AI-use statement, `\pubhold`, the funding text, release text that carries a hold, and
     any text the source comments mark as verbatim or protected. Read the comments around what you edit.
5. **Edit only your batch's files** (listed in your task). Other batches are editing other chapters in parallel.
6. **No git operations** other than read-only `status`, `diff`, `show` and `log`. No commits.
7. **No outward act.** No bare `codex` command. Outside models only through `S/xmodel/run_x.sh`, if at all.
8. **Do not trust model rewrites.** Gemini's rewrites in earlier rounds repeatedly asserted things that are not
   established. Check every fact.

## Method

1. Reverse-outline your chapters, one sentence per paragraph.
2. Build a fact ledger: one row per number, claim, limitation and disclosure, each with a probe string. Write a checker
   in the style of `S/wt-reg2-work/check_ledger.py`. A planted bad probe must fail it.
3. Rewrite paragraph by paragraph, from the outline and the ledger.
4. Check every ledger row against the new text.

## Checks (run all, quote the outputs)

- `bash S/plain-language/build_copy.sh <batch-name> <absolute worktree path>`. It must show:
  - build_all rc 0;
  - RESULT PASS, BODY-POINTERS PASS and SEC4 15/15;
  - struck-value containment passing;
  - RECORDS-MOVE and RECORDS-PIN passing or SKIP;
  - 0 undefined references in every log, and no `??` in the note's or paper's pdftotext.
- **The paper's text must be byte-identical** to the base build, and so must the label numbers. Compare the pdftotext
  of `main_paper.pdf` against `S/plain-language/builds/rec3/repo/docs/analysis-note/main_paper.pdf`.
- `python3 S/tools/swallowed_text.py <worktree> origin/main` must report "flagged 0".
- Your ledger check: 0 failures.

## Deliverables (in your work directory)

- `outline-before.md`, `ledger.md`, `check_ledger.py`, `changes.md` (before, after and reason, per paragraph);
- `REPORT.md`, with:
  - word counts before and after;
  - every move to the records, with its tag;
  - the qualifiers the guardrail kept;
  - open questions;
  - the check outputs.

If the harness refuses `REPORT.md`, put it in your reply.
