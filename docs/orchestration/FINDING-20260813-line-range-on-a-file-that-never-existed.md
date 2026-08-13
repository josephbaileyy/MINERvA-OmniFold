# FINDING 2026-08-13 — A handoff cited a 57 KB primary source, with a line range, that has never existed

**`BEN-216`.** Lane A block (`210-219`). Measured, live. **Confirmed by the citing party**, who then
found a second circulating instance neither of us knew about. Census context:
`ADVISORY-20260813-advisor-review-items-rebuilt.md` §6.

## What was cited

The reassignment handoff naming the E_avail thread gave a fresh lane two primary sources:

> - `docs/orchestration/ADVISORY-20260813-oi30-eavail-residuals.md` (~26 KB)
> - **`OI30-RESIDUALS-REPORT.md` (~57 KB) — the more thorough of the two. Its §"lines 866–871" bounds the
>   strange-species truncation exposure with measured operands.**

So the second file was flagged as the *better* of the two, with a size, a section, and a line range.

## Measured: it has never existed

- absent from the working tree and from all four lane worktrees under `.claude/worktrees/`;
- `find /Users/josephbailey/local-research -iname "*OI30*"` returns **only** the advisory, in four copies;
- `git log --all --oneline --diff-filter=A -- '*OI30*' '*RESIDUALS*'` returns **nothing** — never added on
  any branch;
- not on the cluster either (the check was attempted; the login host did not resolve from this session, so
  this leg is **unverified rather than negative**);
- the file it could be confused with is **396 lines / 26,182 bytes**, so a line-866 citation cannot refer
  to it under any reading.

**The substance attributed to it is real and is in the tree.** The `part_gen[:,:,4]` route, the 0.1286%
binning fidelity, and the zero-η/K⁰_S census are all in the **`OI-56` row** of `docs/OPEN_ITEMS.md`. So
the content exists and the container does not.

## Confirmed by the citing party, who found the worse half

`personal-orchestrator` verified it independently rather than accepting the report, and volunteered
something outside my reach:

> *"It came to me through a context summary and I passed it on with a line range, which is the detail that
> makes it look consulted. **Worse than you could have known: I also cited it to the codex session in a
> mailbox message at 12:04Z, quoting `OI30-RESIDUALS-REPORT.md:78` verbatim.** That false citation is
> circulating in two places."*

**Two independent fabricated line numbers for one nonexistent file** — `866-871` to me, `:78` to codex.
That is the diagnostic detail: a genuine misremembered *filename* does not acquire two different specific
line numbers. **The line numbers are what a context summary's compression produces and what makes the
citation unfalsifiable-looking.**

## The mechanism: a line range is a claim to have opened the file

**A bare path can be a misremembered name. A path plus a line range asserts that someone looked.** That
is the entire cost of this defect: a fresh lane's first act is to open what it was handed, and a citation
carrying a section reference is the *last* one it will think to `ls` — precisely because the specificity
reads as evidence of consultation.

It is `BEN-172` (cite-without-opening) and `BEN-207` (a present verdict is also a statement about the
search) **in one artifact**, and the citing party's own framing is right: it is not inherited, because the
line number was added downstream of whatever the summary contained.

**The cost landed on the least-equipped reader.** A fresh lane has no priors about which of two named
reports exists. Half its handed sources were a dead end, and it cannot tell whether that means the file was
deleted, is on the cluster, is in another worktree, or was never real — all four are live possibilities in
this repo, and distinguishing them took five commands. **A dead pointer is most expensive at exactly the
moment it is cheapest to emit.**

## What the handoff did right, and it is why this was found at all

The same message said:

> *"I am reconstructing 'what Gregor pointed out' from the tree and from a Slack thread, and I am not
> certain that list is complete. **Rebuild it yourself** … and report back what you find that I have not
> named here. **Do not assume my list is the list.**"*

**That instruction is the reason the rebuild happened**, and the rebuild is what produced §2 and §5 of the
census — six `\gk{}` items with two open and unowned, and the measured fact that no Slack or email channel
exists in this repo to corroborate anything outside them. **A handoff that declares its own uncertainty
converts its errors into findings.** This row is a mechanical correction to an otherwise well-formed
handoff, not a complaint about it.

## The check

- **`ls` a path before quoting it to another agent, and especially before quoting a line range.** One
  command, always available, no context needed.
- **Do not carry a line number across a context summary.** Filenames survive compression;
  line numbers are regenerated, and two agents received two different ones for the same nonexistent file.
- **When a handed source does not exist, `git log --all --diff-filter=A -- '<glob>'` before concluding
  anything** — it separates "deleted" from "never existed," and those route completely differently.
- **A citation's specificity is not evidence of consultation.** Size, section and line range are exactly
  what a confident summary produces.
- **Correct a false citation everywhere it was sent, not only where it was caught.** The `:78` instance
  would have gone uncorrected had the citing party not volunteered it.
