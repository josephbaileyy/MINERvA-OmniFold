# FINDING 2026-08-13 — `git config --local` is NOT lane-local here, and the instruction that set it cited the finding it broke

**`BEN-218`.** Lane A block (`210-219`). Measured, live, **caused by me and reverted in the same session.**
**Confirmed independently by the instructing party**, who retracted the instruction to a second lane.

## What happened

The reassignment handoff closed with a working rule:

> *"**Set a distinct git identity before your first commit** (`git config user.name "Lane A (Eavail)"`,
> **local config only**). You, codex and I all commit as "Joseph Bailey", which is why 34 recent commits
> are not separable — your predecessor established that by measurement and filed **`BEN-214`** on it."*

I ran it as my first tool call. **`BEN-214` is my own predecessor's row and its recommended structural fix
is exactly this**, so there was no friction to notice: the instruction cited the finding, the finding
recommended the action, and the parenthetical *"local config only"* read as the safe, scoped form.

## Why it is wrong

**`git config --local` is per-REPOSITORY, and this repository has six working trees sharing one
`.git/config`.** Measured:

```
$ git worktree list
/Users/josephbailey/local-research/MINERvA-OmniFold                     [main]
/private/tmp/.../agy-audit                                             (detached HEAD)
/Users/josephbailey/local-research/MINERvA-OmniFold-gregor-pet2         [codex/gregor-pet2-omnifold]
/Users/josephbailey/local-research/MINERvA-OmniFold/.claude/worktrees/lane-b  [lane-b]
/Users/josephbailey/local-research/MINERvA-OmniFold/.claude/worktrees/lane-c  [lane-c]
/Users/josephbailey/local-research/MINERvA-OmniFold/.claude/worktrees/lane-d  [lane-d]
```

So for the ~4 minutes it stood, **every lane committing from any of those trees without a per-commit
override would have committed as `Lane A (Eavail)`.** The instructing party confirmed the sharper form of
it:

> *"had you and B both followed my instruction, the second would have silently overwritten the first and
> every lane would have committed under one name — **the exact attribution collapse the instruction was
> written to fix.**"*

It also sent the same instruction to lane B, and has retracted it there.

## The correct mechanism was already recorded, by a lane that had already hit this

`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`, item 11, lane B:

> *"`git -c user.name=… -c user.email=…` per commit; **no shared git config written.** Effective identity
> for these commits is `Lane B (uncertainty construction) <josephrb+laneb@stanford.edu>`… **D's measured
> nuance holds: `-c user.email` sets BOTH author and committer**, whereas `GIT_AUTHOR_EMAIL` would set
> only the author — verified on the first commit that used it (`9925ba8`)."*

`OI-45` carries the same standing constraint: *"Shared git configuration is prohibited and receipt identity
remains best-effort."*

**So the correct fix, its exact form, the author-vs-committer subtlety, and a prohibition on the wrong form
were all already in the repo, in two places, one of them a live open item.**

## The mechanism: the naive form of a good recommendation regresses a better one

**`BEN-214` recommended the right thing and named it at the wrong resolution.** Its wording —
*"give each lane a distinct committer identity, as C and D already have"* — is correct as an outcome and
silent on implementation. C and D achieve it **per commit**. Read by someone reaching for the obvious
command, "give each lane a distinct identity" becomes `git config user.name`, which in a shared checkout
produces the *opposite* of the intent.

That is the reusable shape: **a finding that recommends a structural fix without naming its mechanism will
be implemented in whatever form is most obvious, and in a shared checkout the obvious form of an identity
change is repo-global.** The failure is silent, it is in the flattering direction (the operator believes
attribution is now clean), and it is discovered only when someone else's commit comes out wrong.

**It also has the shape `BEN-201` records** — a fact filed in a canonical place not reaching the reader who
needed it. Lane B's item 11 is nine hours old and in a RUN_LOG that a lane assigned to E_avail has no
reason to open. Neither the instructing party nor I consulted it, and both of us had `OI-45` in a file we
had each read today.

## How it was caught, which is not a mechanism

**By luck.** A peer's commit (`51607bb`) landed 3 minutes after my config change and came through as
`Joseph Bailey` — so that lane uses `-c` overrides and was immune. **Had it not been, `git log` would have
attributed lane D's work to lane A**, which is `BEN-214`'s own failure mode with the sign flipped. I
noticed only because I was reading that commit's author field for an unrelated reason.

**Nothing in the repo would have reported this.** There is no check on `.git/config` and none of the lane
receipts record whether an identity came from config or from `-c`.

## The check

- **Never `git config user.name` / `user.email` in this repository.** It is repo-global across all six
  worktrees. Use per-commit `git -c user.name="Lane X (…)" -c user.email="josephrb+lanex@stanford.edu"
  commit …`, which is what `OI-45` and lane B's item 11 already require.
- **Before any `git config --local`, run `git worktree list`.** More than one entry means "local" is not
  "mine."
- **`git config --show-origin <key>`** names the file a value comes from — the honest way to check what
  scope you are about to write.
- **A finding that recommends a structural fix must name the MECHANISM, not the outcome.** `BEN-214` said
  "distinct committer identity"; it needed to say "per-commit `-c`, never `git config`." *This row is that
  amendment*, and `BEN-214` now has a sibling rather than a correction.
- **Record in each lane receipt HOW the identity was set**, not just what it was — per `OI-45`, identity is
  best-effort, and a receipt that cannot distinguish config from `-c` cannot detect this.

## Related

`BEN-214` (whose fix this is, at the wrong resolution — same lane, same day). `BEN-203` / `BEN-204` (the
shared checkout as an attribution and scope hazard; this is the `.git/config` face of it). `OI-45`.
**And an instance in the same turn:** my `OI-30` amendment was swept into `51607bb`, a commit about
`BEN-149` ownership, under the shared identity — `BEN-203`'s shape, happening to me while I wrote this row
about it. Not reverted; this file is the index of that correction.

> **AND I MISATTRIBUTED THAT COMMIT, WHICH IS BEN-214'S MECHANISM A THIRD TIME — COMMITTED BY ME, IN THE
> ROW ABOUT MISATTRIBUTION.** This section and `4574ef5`'s commit message both called `51607bb` *"lane D's
> commit."* **It is the mediator's.** Evidence, in the order it is worth: the mediator asserts authorship of
> it twice unprompted (*"my `51607bb`"*) — an author claiming its own row is the best available evidence
> here; `git branch --contains 51607bb` returns `main`, `lane-b`, `lane-c` and **not `lane-d`**; and it was
> committed in the **main checkout**, which only lane A and the mediator occupy. **`git log` cannot settle
> it** — author and committer are both `Joseph Bailey <josephrb@stanford.edu>`, which is `BEN-214`'s
> enabling condition exactly.
>
> **How I got it wrong is the reusable part:** I inferred the author from the commit's *subject matter*
> (`BEN-149`, an audit-flavoured topic) and from the `lane-d` merge commit sitting next to it in
> `git log --oneline`. **Adjacency in a log is not authorship, and topic is not authorship** — under a
> shared identity they are the only signals left, and both are wrong here. `BEN-214`'s own check says read
> the `BEN-*` id against the block table; `51607bb` carries an `OI-*` id, for which there is no block table,
> so **the check I wrote does not cover the case I then failed.** Recorded as a gap in that check, not as a
> slip.

## THE SWEEP RAN BOTH WAYS, AND THE RETURN LEG BREAKS THE STATED REMEDY

**Added 2026-08-13 after the mediator measured the other half.** The exchange was symmetric and neither
party noticed at the time:

| | into whose commit | what moved |
|---|---|---|
| outbound | `51607bb` (mediator's, *"OI-57/OI-58: the BEN-149 repair had no owner"*) | **my** `OI-30` amendment |
| **inbound** | **`b8bd939` (mine)** | **the mediator's `OI-57` action-column correction** — the withdrawn re-pin clause |

Verified here rather than accepted: `git log -S "there is NO re-pin step" -- docs/OPEN_ITEMS.md` returns
**`b8bd939` and only `b8bd939`**, and that commit's diff touches the `OI-57` row in three places. So a
correction the mediator authored is attributed to lane A, inside the very commit whose message records the
outbound half.

**AND THE MECHANISM CONVICTS `BEN-203`'S REMEDY, WHICH I FOLLOWED.** `BEN-203` says *"stage and commit with
explicit pathspecs."* I did — `git commit -- <six explicit paths>`, no `git add -A` anywhere. **It did not
help, and it could not have.** `git commit -- <path>` commits that path's **worktree** content, bypassing
the index entirely; `docs/OPEN_ITEMS.md` had been left staged by another lane and its worktree copy already
held that lane's in-flight edits to a *different row of the same file*.

**Confirmed independently from the documentation** rather than from the observation alone — `git help
commit` states it outright: a pathspec commit will *"ignore changes staged in the index, and instead record
the current contents of the named files."*

**So: explicit pathspecs protect you from committing other FILES. They do nothing about other lanes' edits
to the SAME file.** Where `OPEN_ITEMS.md` / `FINDINGS.md` / `VALIDATION_LEDGER.md` are append-target
ledgers every lane writes to, that residual is silent in both directions.

> **SCOPED DOWN 2026-08-13 — I wrote "six trees share one working directory" and that overstates it in the
> direction that sends a reader hunting a hazard that is not there.** Measured: `git worktree list` gives
> six trees, but **B, C and D each have their OWN directory** under `.claude/worktrees/`, and each
> `.claude/worktrees/<lane>/.git` is an 82-byte gitdir *pointer* — so they have separate working trees and
> separate index files and **cannot collide this way at all.**
>
> **What the six trees genuinely share is `.git/config`, which is this row's OTHER leg** and is correctly
> stated above. **The shared *working directory* is the main checkout alone, and only two parties occupy
> it: lane A and the mediator.** Both observed instances are that one pair. **That is the whole exposure**
> — smaller than my framing, and it makes the fix smaller too.

`BEN-203`'s advice is necessary and **not sufficient**. What actually closes it is a per-lane worktree, and
this exchange is the concrete argument for taking one rather than the abstract one.

**Nothing is unwound.** Both edits are correct and committed; only the attribution is wrong, and per this
repo's convention written history stays written and the correction is indexed. This section is that index
for both legs.

**Why it strengthens `BEN-214` rather than complicating it.** That row's mechanism was stated as a one-way
loss — the under-credited party is the only one positioned to notice. Measured, it is an **exchange**: each
party silently acquired credit for the other's work *and* lost credit for its own, in the same hour, and
each noticed only the leg that went against it. **Neither party's incentives pointed at the leg that
favoured it**, which is exactly `BEN-214`'s claim, now observed twice in one commit pair instead of once.
