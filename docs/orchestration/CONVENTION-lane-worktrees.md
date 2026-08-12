# CONVENTION — per-lane worktrees, and the author merges their own row

**Decided by Joseph 2026-08-12**, after six absorption events across four lanes in roughly two hours,
every one by a session correctly applying the then-current published remedy.

## Why the shared checkout had to go, in one measured paragraph

Six successive **pre-commit** remedies were each defeated: `git add -A` → stage by path → split by hunk
→ read `git diff --cached --stat` → verify the file clean first → private index with `read-tree` +
`commit-tree`. Each narrowed *what you name*; none removed the window between editing a shared file and
committing it. The last defeat was the orchestrator's, twenty minutes after it relayed the remedy: the
private index was verified by listing its **paths** — exactly three, as intended — and it still absorbed
1325 lines of another lane's restructure, because a private index does not make the working *tree*
private. The only technique that ever caught an absorption at the moment it happened is the **post-hoc
contents read**, and it is one-directional: it finds what you took, never what was taken from you. The
only query for the other direction, `git log -S '<your own text>'`, is one nobody runs and it produced
two false positives when someone finally did.

**Worktrees do not mitigate this; they eliminate it.** Separate worktrees have separate indexes, proven
rather than assumed: staging a probe file in `lane-b` left the main checkout's index empty.

## The worktrees

    .claude/worktrees/lane-b   branch lane-b    B — uncertainty construction
    .claude/worktrees/lane-c   branch lane-c    C — PET
    .claude/worktrees/lane-d   branch lane-d    D — verifier
    <repo root>                branch main      A — orchestrator

`.claude/` is gitignored, so the worktrees are invisible to the tracked tree. A worktree cannot check out
a branch another worktree holds — that is git refusing to recreate the shared-checkout hazard, not an
obstacle. Enter one with the `EnterWorktree` tool and its `path`, not by `cd`.

**Cluster worktrees remain FORBIDDEN** until `p4_evidence.py` stops hardcoding `REPO` *and the
replacement is power-tested* — a test that FAILS on the hardcoded form. Deriving `REPO` from `__file__`
is not sufficient on its own, and "make it relative" is how that instruction will otherwise be read.
Until then a cluster worktree would record the canonical tree's blobs while a different file executes,
which is a provenance lie rather than an inconvenience.

## The rule: no lane's ledger row is merged by anyone but its author

Worktrees convert silent absorptions into **merge conflicts** in the contended files. Loud beats silent —
but someone still resolves the conflict, and that someone is the person least likely to know what the
other lane meant. Five of the six absorptions landed in exactly three files: `FINDINGS.md` (×3),
`VALIDATION_LEDGER.md` (×2), `OPEN_ITEMS.md` (×1).

So the rule ships with a **mechanism**, because this campaign has a measured record of attentiveness
remedies failing: BEN-105 counts four failures of BEN id attentiveness, twice while the failing agent was
reading the rule.

    python3 docs/orchestration/whose_row.py --conflicts --lane C     # exit 1 if a contested row is not yours
    python3 docs/orchestration/whose_row.py --self-test              # 42 checks, both directions

Run it on every conflict before resolving. It attributes each row to its owning lane by **deriving** the
BEN block table out of `FINDINGS.md`'s own header, and it refuses to fall back to a hardcoded copy — a
stale block map attributes rows to the wrong lane, which is worse than no attribution and is the shape of
the false confession BEN-160 records. When it refuses, **route to the named author; do not resolve.**

### What the attributor cannot do, stated so it does not overstate its reach

- It attributes by **id block, not authorship**. A lane filing in another lane's block is misattributed;
  that has happened (BEN-089, `max+1` from outside both documented ranges).
- **`VALIDATION_LEDGER.md` has no per-row id scheme and cannot be attributed.** It is the file with the
  second-most absorptions. Conflicts there print `NO ATTRIBUTABLE ROWS` and are refused, by design.
- It sees rows, not prose. A conflict in a header paragraph is unattributable and reported as such.

### It shipped with a false pass, which is why the self-test is the cross-product

The first `lane_matches()` was `lane.lower() in owner.lower()`, and it returned **True** for lane `C`
against owner `B — uncertainty construction`, because "constru**c**tion" contains a `c`. The gate passed
lane C on lane B's row: a false pass, in the only direction that matters, inside the check written to
prevent exactly that. It was caught by an **end-to-end merge between two real worktrees**, not by the
self-test — whose single negative control happened to be a case where the bug does not fire. The
self-test now runs the full lane × owner cross-product and requires the diagonal exactly, plus both
historical false passes pinned by name. **The battery is the form set, not one variant.**

## Merging to main

Each lane merges its own branch to `main` and pushes. Before resolving any conflict, run the attributor.
Ledger rows are **append-only in practice**: add your line, never reflow or rewrite another lane's, since
git merges added lines cleanly and cannot merge two rewrites of the same 1000-character row. That is why
the index restructures matter — `KNOWN_ISSUES.md` is now 53 lines with a 254-character maximum and will
merge; `FINDINGS.md` still has a 1032-character line and `CLAIMS.md` a 1529-character one, and those
will not. Finishing that shortening is what makes conflicts resolvable rather than merely visible.

**Still true inside a worktree, because it was never about the index:** the post-hoc contents read.
`git show --stat` after the commit exists, and read the diff's contents for rows you did not write.

## What worktrees cost, named rather than discovered later

Essentially every real catch on 2026-08-11/12 came from a peer noticing something in the shared tree —
the comment-form `\dead` evasion, the false confession, the dangling archive pointer, the insufficient
regex. Isolated lanes see less of each other. **Worktrees isolate WRITES, not ATTENTION**: the
peer-messaging protocol is unchanged and cross-lane review remains the mechanism that actually found
things.
