# IBUB code, read 4: agy gemini-3.8-flash-high (2026-11-24)

**By** `director-helper-3`. This read checks the codex-school2 read 1 fixes. Its inputs came from `git archive` of
`d547fa1fa` (`inputs.sha256`).

**MEASURES:** one reader's findings. **CANNOT AUTHORIZE:** anything.

**What it confirmed:** each of codex2 read 1's blockers B1–B8, and NB1 and NB3, read **CORRECT AND COMPLETE** against
the code, with file:line citations.

**VERDICT: REVISE,** on one MAJOR and one NOTE:

| # | label | finding | disposition |
|---|---|---|---|
| 1 | MAJOR | `code/mutants.txt` was still the 39-mutant run at `79a3427a0`. codex2-r1's README said the extended run "ran at the final commit", which was not yet true at `d547fa1fa` | **correct, and my error:** I wrote that sentence before the run had happened. The 69-mutant run at `d547fa1fa` then killed 67. The two survivors were masked by redundant later checks; `ee189fefc` fixed both tests, and one equivalent mutant was replaced. The full run at `ee189fefc`, in a separate worktree, is the committed `code/mutants.txt`. The README's NB4 row now states this |
| 2 | NOTE | the review archive omitted `cov2d.py` and rpd's `fence_overlap.py` | noted for future archives. The production connect clones the whole repository at M |
