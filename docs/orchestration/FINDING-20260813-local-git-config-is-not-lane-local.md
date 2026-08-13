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
**And an instance in the same turn:** my `OI-30` amendment was swept into `51607bb`, another lane's commit
about `BEN-149` ownership, under the shared identity — `BEN-203`'s shape, happening to me while I wrote
this row about it. Not reverted; this file is the index of that correction.
