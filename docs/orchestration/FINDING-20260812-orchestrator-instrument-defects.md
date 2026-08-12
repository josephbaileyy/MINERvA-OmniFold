# Two orchestrator instrument defects, 2026-08-12 — BEN-190 and BEN-191

Long-form detail for two `BEN-19x` rows, split out because both exceeded 2 000 characters and a row that
long **cannot merge**: git merges added lines cleanly and cannot merge two rewrites of one enormous line.
`CONVENTION-lane-worktrees.md` says finishing that shortening is what makes conflicts resolvable rather
than merely visible — and measured just now, **only 8 of 125 rows in `FINDINGS.md` exceed 600 characters,
and all eight were written by the four active lanes within the last few hours.** The August restructure
compressed the history into one-liners and we immediately re-inflated it. These two were mine, so they go
first.

Both defects are in **instruments**, both were found by someone else re-deriving a claim of mine, and
neither was findable from the code alone.

## BEN-190 — I edited the config directory this session does not read, and verified only its contents

Joseph asked for `crossSessionInbound: "accept"`. I read `~/.claude/settings.json`, merged the key, validated
the JSON, confirmed the siblings intact, and reported it applied.

`env` says **`CLAUDE_CONFIG_DIR=/Users/josephbailey/.claude-school`**. Three config directories exist —
`~/.claude`, `~/.claude-school`, `~/.claude-personal` — each with its own `settings.json`. The file I edited
is not this session's config. **The effective change came from the mediator session editing the right file;
mine was a no-op here.**

**Why the verification missed it.** Every check I ran was about the file's *contents*: parses, key present,
value in the enum, siblings preserved. **None was about whether that file is in the read path.** A settings
edit has two correctness conditions and I tested one. This is BEN-088's shape — reading a real artifact for
something it does not contain — in the **write** direction.

**Same class as the cluster/local fork**, which is why it is a row rather than a quiet fix: the question is
not *"is the file right"* but **"which file is authoritative"**, and this campaign has now been bitten by
that twice in two days on two different objects.

**Rules.** (i) Before editing config, print `CLAUDE_CONFIG_DIR` and edit the directory it names; a bare
`~/.claude` is an assumption, not a location. (ii) Verify a settings change by its **effect** where one is
observable, not by re-reading the file you wrote. (iii) The `~/.claude` edit is **left in place
deliberately** — it is a genuine application of the instruction for any session that does not set
`CLAUDE_CONFIG_DIR`, and reverting would be a second unrequested change; but its presence must not be read
as what took effect here.

## BEN-191 — we fixed the staleness detector and the artifact is still always stale

`LIVE-STATE.md` went stale three times in under an hour, **the third time during the exchange in which its
freshness detector was repaired** (BEN-164). Measured by the mediator running the new check: `Git: fa45fc1`,
`HEAD ae60dcf`, `HEAD^ e16da21` — stale by more than one, so beyond the born-stale-by-one state the new rule
blesses.

**So the instrument is now truthful about a condition it cannot escape.** That is progress and it is not a
fix. A generated snapshot committed into a repo that commits every few minutes cannot be fresh.

**Root cause: the file conflates two things with different natural lifetimes.** A **generated view** — jobs,
watches, branch heads — volatile and worthless the moment it is committed. And **authored prose**,
`Declared state`, which is the load-bearing part, is worth versioning, and is the part that carried
*"no cause is discharged"* through two regenerations after `d75833a` falsified it. **Freshness is a property
of the first; truth is a property of the second; `--check-freshness` can only ever test the first.**

**Options, and why I reject the one the mediator preferred.** (a) generate on read — unconditional freshness,
loses the git-visible control-plane history. (b) regenerate in a pre-commit hook so the file is always
born-stale-by-one, which the new rule calls FRESH. (c) mandatory `--check-freshness` for every reader, which
is where we effectively are.

**(b) manufactures the exact defect the worktrees were adopted to remove.** A hook that regenerates and
stages this file puts it in **every lane's commit**, so a file **no lane's row owns** becomes permanently
contended: `whose_row.py` returns `NO ATTRIBUTABLE ROWS`, and **every merge touching it refuses**. It is
also a `git add` on every commit, which rule (i) forbids. The mediator's reasoning for (b) was sound and the
objection needs a fact it did not have — that the attributor has no row scheme for that file.

**Preferred instead: split the file.** Version the authored declaration; generate the volatile view on read.
Freshness becomes unconditional where it is a real property and irrelevant where it never was. **Not
actioned** — four lanes are mid-write and this is the read path.

*Structural point raised by the personal-account mediator session, which leaned (b). The objection to (b),
the split, and BEN-190 are Session A's.*
