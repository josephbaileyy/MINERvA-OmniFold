# FLAG 2026-08-24 — unpreserved work in the `gregor-pet2` worktree

**This is a FLAG, not an action, and not this lane's tree.** Raised by the OI-126 free-reads lane
("PET mentor") while answering whether the PET sessions could be closed. The tree belongs to a
`codex/` lane. Nothing here is repaired, moved, committed, or deleted by this record, and nobody
should read it as authorization to do any of those.

**Not urgent, and not made urgent by session closure.** The worktree is
`/Users/josephbailey/local-research/MINERvA-OmniFold-gregor-pet2`, which sits **outside**
`.claude/worktrees/`, so it is not cleaned when a session ends. Branch refs live in the shared `.git`
regardless. So closing sessions costs none of this.

## What is actually exposed

**The working tree is nearly all disposable.** 12 uncommitted entries, of which **10 untracked and 1
modified are waker/monitor telemetry from 2026-07-24/25** — `evt-idle-*.json`,
`evt-gregor-pet2-conditional-array-20441096-deadline*.json`, and one modified `watches/*.json`. They
are one month old, they are scheduler bookkeeping rather than analysis products, and losing them
costs nothing. Do not spend a decision on them.

**Two files are substantive**, both dated 2026-07-25 and both self-labelled:

| file | bytes |
|---|---|
| `docs/orchestration/gregor-pet2/UNCOMMITTED-delta-gate2-units-20260725.diff` | 2245 |
| `docs/orchestration/gregor-pet2/UNCOMMITTED-delta-gate2-units-20260725.md` | 3442 |

A diff plus its write-up concerning gate-2 **units**. The `UNCOMMITTED-` prefix is in the filenames,
so parking them was deliberate by whoever wrote them; this flag does not second-guess that, it only
notes that the parking has lasted a month and nothing points at it.

**The larger exposure is not the working tree at all: `codex/gregor-pet2-omnifold` carries 29 commits
reachable from NO remote ref.** Measured 2026-08-24 with `git rev-list --count HEAD --not --remotes`.
HEAD is `b65f9ff2` *"Finalize Gregor PET2 conditional stress: post-result auditors ACCEPT/PASS"*. That
is a finalisation commit, so the branch reads as complete work that was never pushed. It lives only in
this one local clone.

## What would settle it, for whoever owns it

1. Push the branch, or record a decision that it stays local and why.
2. Adjudicate the two `UNCOMMITTED-delta-gate2-units` files — commit, or record that they are
   superseded. Either is fine; a month of neither is the thing worth noticing.
3. The telemetry needs no decision.

## Why this is only a flag

The Gregor PET2 evaluation already reached a **no-promotion** outcome, so this is the tail of
closed-out work rather than a live result. It is a preservation question, it belongs to a lane that is
not this one, and "commit another lane's uncommitted files" is exactly the sweep this campaign has
been careful not to do — an unrelated lane's `--write` sweeping a peer's working tree is a recorded
defect here, not a courtesy.
