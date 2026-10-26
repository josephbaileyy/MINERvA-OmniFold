# Methods paper: the approved abstract sentence (2026-10-26, unscored)

**Authority.** `docs/orchestration/DECISION-20261026-joseph-abstract-and-cresp-build.md` item 1. Joseph approved the
abstract change proposed in `r18/REPORT.md` ("For Joseph", item 1), as worded there. It lands as its own commit, with
agy's agreement, a ledger row and the full build. No other abstract text changes.

Base: origin/main `35c46aed`.

## The change

`docs/analysis-note/main_paper.tex:80-82`, one sentence of the abstract:

- **before:** "Pseudo-experiments reveal background-subtraction bias, incomplete recovery of generator-sized truth
  changes, and statistical undercoverage at the tested truths."
- **after:** "Pseudo-experiments measure a background-subtraction bias, a partial recovery of generator-sized truth
  changes, and statistical undercoverage at the tested truths."

A non-printing `%` comment after the abstract's last sentence cites the decision. Nothing else in the abstract or the
paper changes (`git diff` touches only these lines).

## Fact ledger

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| A1 | pseudo-experiments: background-subtraction bias, partial (incomplete) recovery of generator-sized truth changes, statistical undercoverage at the tested truths | abstract | KEEP (reworded, approved: DECISION-20261026 item 1) | abstract | `N:main_paper.tex::Pseudo-experiments measure a background-subtraction bias, a partial recovery of generator-sized truth changes, and statistical undercoverage at the tested truths. && X:main_paper.tex::reveal background-subtraction bias && X:main_paper.tex::incomplete recovery` |

Probe check, on the comment-stripped, whitespace-collapsed source of `main_paper.tex`: the `N:` text prints once; each
`X:` text prints 0 times.

## agy agreement

agy (`run_x.sh gemini`) read the whole abstract, before and after, with the rule that no fact, condition, scope or
status may be lost or added and no claim may become stronger or weaker:

```
PASSAGE: abstract
VERDICT: AGREE
ISSUE: none
FIX: none
```

## Build and gates

`bash build_all.sh` in the round's worktree: rc=0.

- `main_paper.pdf`: 13 pages, 0 undefined references or citations, no `??`. The abstract prints the new sentence.
- `main_note.pdf`: 121 pages, 0 undefined references or citations, no `??`.
- `SEC4-RECEIPTS :: PASS (15/15)`; `RECORDS-PIN :: PASS`; the build's `RESULT :: PASS`.
- The tree's own hook, `bash .githooks/pre-commit`, passes on the commit.

## Scoring

Unscored. The next paper round's baseline includes this sentence.
