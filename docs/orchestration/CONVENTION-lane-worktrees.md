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

    bash docs/orchestration/merge_guard.sh C      # <- RUN THIS. It runs the self-test, then the gate.

**The path is the contract; this document deliberately no longer quotes the command.** BEN-163: the gate
grew from one exit code to three across seven return sites, and this snippet went on saying
*"exit 1 if a contested row is not yours"* and *"42 checks"* against a suite that now runs a different
number. This is the only place an operator learns the contract — and BEN-117's own text notes that the
empty-`--lane` case *"is how any wrapper or hook will invoke this"*, so **the reader most likely to write
that wrapper was reading the line that omitted exit 2.** A wrapper written faithfully from the old
snippet tests `[ $? -eq 1 ]`, and exit 2 — added precisely because a misconfigured caller had been told
it passed — would read as success. The hole was not closed; it moved from the script into the prose
describing the script, which is worse, because the script has a self-test and the prose has none.
`merge_guard.sh` cannot drift from the exit codes because it *is* their only interpreter, and it prints
no check count of its own — the suite reports its own total, and a second copy in prose can only drift.
Same remedy and same reason as `waker_fired_but_unread.sh` (BEN-097).

    exit 0  PASS          every contested row is yours; you may resolve
    exit 1  REFUSED       a row belongs to another lane — route it, do not resolve
    exit 2  CANNOT CHECK  nothing was examined, so nothing was verified. NOT a pass
    exit 3  BLOCKED       no lane given, or the gate's own self-test failed

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

> **UNIT: CHARACTERS, not bytes — stated here because this file got it wrong.** Every length in this
> document is a **character** count. The figures above originally read *1032* and *1529*, which are the
> **byte** counts of those lines (1028 and 1509 characters); em-dashes are three bytes each and these rows
> are dense with them. The one figure that happened to agree — `KNOWN_ISSUES.md`'s 254 — agrees only
> because that line is pure ASCII, so **the single example a reader would spot-check is the one where the
> discrepancy cannot appear.** Harmless so far, because the over-600 set is identical under both units,
> but that is luck about where rows fall relative to the threshold: **a 598-character row can be 604
> bytes.** Measure with `len(line.rstrip())` in Python or `awk '{print length($0)}'`, not `wc -c`.
> (`BEN-166`, found by Session D in Session A's file.)

Each lane merges its own branch to `main` and pushes. Before resolving any conflict, run the attributor.
Ledger rows are **append-only in practice**: add your line, never reflow or rewrite another lane's, since
git merges added lines cleanly and cannot merge two rewrites of the same 1000-character row. That is why
the index restructures matter — `KNOWN_ISSUES.md` is now 53 lines with a 254-character maximum and will
merge; `FINDINGS.md` still has a 1028-character line and `CLAIMS.md` a 1509-character one, and those
will not. Finishing that shortening is what makes conflicts resolvable rather than merely visible.

**Still true inside a worktree, because it was never about the index:** the post-hoc contents read.
`git show --stat` after the commit exists, and read the diff's contents for rows you did not write.

## What worktrees cost, named rather than discovered later

Essentially every real catch on 2026-08-11/12 came from a peer noticing something in the shared tree —
the comment-form `\dead` evasion, the false confession, the dangling archive pointer, the insufficient
regex. Isolated lanes see less of each other. **Worktrees isolate WRITES, not ATTENTION**: the
peer-messaging protocol is unchanged and cross-lane review remains the mechanism that actually found
things.

## OI-47 — the isolation is CONVENTION, not ENFORCEMENT, and the premise needs establishing first

Raised by the personal-account mediator session and **deferred by Joseph 2026-08-12**: *"note to do the
durable fix later"* (`AUTHORIZATION-20260812-worktree-confirm-and-oi17-probe.md`). The point stands and is
worth stating plainly: **nothing above stops a lane from writing the main checkout.** Entering a worktree
is something each lane does because it was asked to, and `worktree.bgIsolation: "worktree"` would make it
a block rather than a courtesy.

**The mediator's premise is imprecise and I measured it rather than recording it.** It reported
`bgIsolation` as *"currently `none` for all four lanes"*. Measured: it is **unset** — in
`~/.claude-school/settings.json`, `~/.claude-personal/settings.json`, `~/.claude/settings.json`, in no
project `.claude/settings*.json` (neither exists), and in no launch flag (`respawnFlags` is
`--permission-mode bypassPermissions --name --model` only). **Unset is not `none`**, and the documented
default for the key is `"worktree"` — which would *block* background sessions from the main checkout.

Yet all four background lanes have written the main checkout freely all day. **So one of two things is
true and I did not establish which:** the effective default in this deployment differs from the documented
one, or isolation is configured somewhere I did not find. **Establish that before flipping anything** —
setting a key to its apparent current value is how a no-op change gets recorded as a fix, and this session
has already done exactly that once today with a settings edit to the wrong config directory (BEN-190).

**Why not now, and this part is not deferral-by-inertia:** four lanes are mid-write, and enforcement would
stop all of them at once. The mediator recommended against flipping it today for that reason and Joseph
agreed. Its supporting measurement, which argues the same way: at `12:31:48Z` all four branches were
byte-identical at `fa45fc1`, i.e. **zero divergence on every lane**, while `main` moved `07059a2` →
`fa45fc1` in nine minutes. **The reason to fix this is the write pressure, not any current divergence.**

### OI-47's precondition is RESOLVED, and the answer changes what the fix is

Established 2026-08-12 by the mediator session reading job state, then re-measured here across all four
lanes. **The two readings were of different objects and both were true:**

    settings   worktree.bgIsolation = <unset>   in all three config dirs; no project settings file exists
    job state  ~/.claude-school/jobs/<id>/state.json  ->  "bgIsolation": "none"   for ALL FOUR lanes
               (7731b75e D, a973d86c A, d9b3c3b6 C, f00bb3d3 B; in no respawnFlags either)

So the dichotomy above resolves to its **first** branch: the effective value is **not read from settings at
write time — it is recorded per job at spawn**, and every lane carries `none`. The documented `"worktree"`
default is not what these jobs got.

**The consequence is not cosmetic: setting `worktree.bgIsolation: "worktree"` in a settings file would very
likely be a NO-OP for the four running lanes**, because they already hold a spawned value and are not
consulting that key. It would apply to the *next* spawn. So the remedy is a **respawn-time** change, and
verifying it means **re-reading `state.json` for the new jobs, not diffing the settings file.**

**This is exactly the trap BEN-190 was filed against**, one object over: verifying a config file's contents
rather than whether that file is in the read path. OI-47 as originally framed — *flip the key at a quiet
point* — was set up to walk into it a second time, and would have recorded a no-op as a fix.
