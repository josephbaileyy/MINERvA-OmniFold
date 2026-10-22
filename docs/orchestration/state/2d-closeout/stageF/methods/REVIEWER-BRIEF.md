# Reviewer brief: analysis-note register batches (shared by every batch)

`S` = `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad`

You are an independent, adversarial, read-only reviewer of one register batch of the analysis note.
- Edit nothing in any worktree, and do not commit.
- Write your report to `<work dir>/REVIEW.md`. If the harness refuses, return the report as text.

## What the writer had to obey

The binding rules are `S/note-batch/WRITER-BRIEF.md`; read it. In summary:
- No fact or number is lost, and no claim is strengthened.
- A record may leave the posted note only if the records document (`main_records.tex`) prints it and the note cites
  `\cite{NoteRecords2026}` with a tag or heading that exists there.
- Limitations stay beside the results they bound.
- The guardrail: a qualifier stays wherever leaving it out would make a printed sentence false as read.
- No label, section or subsection changes.
- Protected and verbatim text is byte-identical.
- The paper's text and its label numbers are unchanged.

## Directions to check

**A. Lost facts.**
- Script a comparison of every number in the batch's printed chapters, before against after.
- For each changed or removed sentence, find every fact in the new text or in the records document at the cited
  tag or heading.
- **The paper cites note subsections by number.** For each `\nsec{...}`/`\napp{...}` pointer from
  `paper_body.tex` and `main_paper.tex` into the batch's labels, confirm the pointed-to fact still prints in that
  subsection, in substance. Be exact: a fact moved to a different subsection breaks the paper's pointer.

**B. Strengthened claims.**
- Check every rewritten sentence against the old text and its sources (records, decision files, reports under
  `docs/orchestration`).
- Flag:
  - a stronger verb;
  - lost scope;
  - a status changed, such as "used in this note" against "computed but not used", or "for reporting only";
  - a timing claim that is not supported, such as "predeclared" or "before".
- Where the writer added specifics ("in every cell", a number), verify them against the source the writer cites.

**C. Protected text.** Verify byte-identity of the verbatim and protected spans the task names, and of anything the
source comments mark as verbatim.

**D. Mechanics.**
- The writer's checker passes, and a planted bad probe fails it.
- The build log shows the gates passing.
- The paper's pdftotext is identical to the base build.

**E. Register.** Did the batch reach the target register? List at most 8 surviving passages that still read as
bookkeeping, history or meta-text, quoted exactly.

## Output

Give each finding:
- a severity: BLOCKING (a lost fact, a strengthened claim, a broken paper pointer or changed protected text),
  SHOULD-FIX or NIT;
- exact before and after quotes;
- file:line;
- a fix.

End with:
- a verdict: ADOPT, ADOPT-AFTER-FIXES or REJECT;
- the counts of what you checked;
- what you did not check.
