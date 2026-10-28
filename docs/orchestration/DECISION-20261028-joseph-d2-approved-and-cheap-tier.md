# DECISION 2026-10-28 — Joseph: the final draft d2 is approved, and the cheap tier of the coverage scoping runs first

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The scoping.** `LIMITATION-PLAN-ADDENDUM-20261028.md` (PR #456) costs five items. The director recommended
  running the cheap tier first and deciding 1B with its results in hand. The cheap tier is:
  - 3a, the ±4 % recoil data unfolds projected onto the cells, at 0 node-h;
  - 3b, mismatch closures from existing shifted dumps, at about 0.6–3.5 node-h;
  - 4C, the χ² spread from A7's existing nuisance-drawn products, at 0;
  - 5A, the 2D run-period block projected onto the sixteen cells, at 0;
  - 5B, per-period 5D unfolds, at about 1–3 node-h.

  In all, about 2–7 node-h. The sixteen-cell C_total carries no run-period block.
- **The draft.** The revised final draft d2 (`fived16/FINAL-DRAFT-2.md`, #413 at `d9e5c4a9`) applied Joseph's
  decisions on (d) and the independent raters' choices.

Joseph's answer, verbatim:

> I agree with your recomendation for the coverage scoping. d2 is approved but we still haven't gotten a similar rating to PRL papers/notes yet right? I think that indicates that there is more to be done. For example, in the note is it redundant to have a super long abstract plus an executive summary plus a results table plus a table of contents, plus whatever table is on page 10? also why does app_release need to be protected text? do you think its worth investing time into analyzing what type of rewriting/restructuring has been best so far and setting up a dspy agent with prompt optimization?

sha256 of the text plus a final newline begins `f6735904062c2648`.

## What is decided

1. **d2 is approved,** so #413 merges, as `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md`
   item 2 and the director handoff §5.1(e) set out. The items d2 left as proposals stay proposals: R1–R4,
   app_release.tex:9, the deposit wording, the typical Data Availability draft, the "on hydrocarbon" body phrase and the
   GiBUU-vertex wording. Q4 stays open.
2. **The cheap tier of the coverage scoping runs first.** It is the five items listed above, under the standing approval
   for jobs under 12 h, declared and bound as usual. A fresh measurement session runs it. Its first step checks that
   the dumps items 3b and 5B depend on are retained, before the 2026-11-20 purge window.
3. **1B, and 4B, are decided after the cheap tier reports.** No compute is granted for them here.
4. **Joseph's questions** are answered by the director, not decided here:
   - the rating against the published anchors;
   - redundancy in the note's front matter;
   - why app_release.tex is protected;
   - a DSPy agent with prompt optimization.

## Not changed

- The abstracts' final wording, the claims, KI-85, `\pubhold`, Data Availability and the release text stay Joseph's.
- Nothing is submitted, deposited or tagged.
