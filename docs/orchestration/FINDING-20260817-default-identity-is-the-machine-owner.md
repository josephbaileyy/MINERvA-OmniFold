# Default git identity is inherited from the human who owns the machine

**BEN-399.** Filed 2026-08-17 by the seconding lane — **the last id in block `390-399`, which this filing
exhausts.** Relaying a repo-wide change made by the mediator, which asked this lane to carry it into the
record. **Every number and every precedence leg below was re-measured here rather than accepted.**

## The defect

> **Unattributed agent work is not anonymous. It is attributed to the human who owns the machine.**

Measured on `origin/main`, last 10 hours:

| author | commits | correct? |
|---|---|---|
| `Joseph Bailey <jrbailey555@gmail.com>` | **61** | **no — none of them are Joseph's** |
| `Lane C (PET) <josephrb@stanford.edu>` | 33 | yes |
| `Lane D (verifier) <jrbailey555@gmail.com>` | 15 | name right, **Joseph's email still attached** |

`user.name` and `user.email` resolved from `~/.gitconfig` — Joseph's global config — because **nothing was set
at the repo level.** Any lane that did not explicitly identify itself committed as the repo's owner.

**This is worse than a missing value.** A blank author is a hole you notice. A wrong-but-plausible author is a
**false positive that looks exactly like legitimate human authorship**, so it passes every check in this repo,
and it fails **systematically in one direction — toward the human.** A merely unreliable field would scatter.

## Against me, which is the sharpest fact here

**All thirteen of my commits today are authored `Joseph Bailey <jrbailey555@gmail.com>`.** Including:

- **`BEN-395`**, whose own text reads *"`%an` IS NOT A LANE FIELD"*;
- **`BEN-398`**, about whose hunks travel in a shared checkout;
- **`BEN-396`**, about verification effort being spent on other people's claims rather than one's own.

**I filed the day's attribution findings while being an instance of the defect in all of them.** The check that
would have caught it is `git log -1 --format='%an'` on my own commit — **one command, never run** — which is
precisely `BEN-396`'s allocation failure: I audited other parties' attribution and never my own, because my own
was not in dispute.

**And it upgrades `BEN-395` rather than merely illustrating it.** That row said the field cannot be *trusted*;
this supplies the cause and sharpens the consequence: **the field is not noisy, it is biased**, and every
`OI-*` ownership audit `BEN-395` contemplates is defeated silently by it.

## The fix, applied by the mediator — not by me

On Joseph's own words, relayed: *"I am not committing anything, but it would be nice if we could fix this."*
**I did not hear them, and this row records them as relayed.**

```bash
git config --local user.name  "MINERvA-OmniFold agent (unattributed)"
git config --local user.email "agent-unattributed@minerva-omnifold.invalid"
```

**A shared config that six live lanes depend on is not something to change on a peer's message**, which is why
the change is the mediator's and the verification is mine.

**Verified here independently, in a throwaway worktree, before adopting it — all three legs:**

| leg | result |
|---|---|
| explicit `-c user.name=` still wins | `Lane TEST <test@minerva-omnifold.invalid>` — **so C's and D's identification is unaffected** |
| repo-local now beats the global fallback | `MINERvA-OmniFold agent (unattributed) <agent-unattributed@minerva-omnifold.invalid>`, **not `Joseph Bailey`** |
| holds inside a linked worktree | yes — `git config user.email` in a linked worktree returns the local value |

**The fallback is now honest rather than false. It does not attribute correctly; it stops attributing
wrongly** — the same distinction as `BEN-084`'s *an artifact asserting the wrong thing beats no artifact for
damage.*

**`.invalid` is a reserved TLD that can never resolve to a real address**, so a forge cannot link these commits
to a person. An agent is not a person and the metadata should not imply one.

## What every lane should do, and this row's own commit is the first instance

```bash
git -c user.name="<lane>" -c user.email="<lane>@minerva-omnifold.invalid" commit ...
```

**Per-commit `-c`, and not a config write.** `EnterWorktree` normalises `core.hooksPath` into the *shared*
`.git/config` for every lane, so an identity fix routed through config is itself a cross-lane write — `BEN-370`'s
mechanism. `git -c` touches no file.

## The clean fix is available and deliberately not taken

`extensions.worktreeConfig` with a real per-worktree identity is the correct answer. It **changes config
resolution semantics**, and git's documentation requires migrating `core.bare` (set here, `=false`) to enable
it. **Doing that mid-session with six live lanes is `BEN-370`'s exact shape** — a config change that breaks
every lane silently. Recorded as available, for a quiet moment, and not done.

## The mechanism is `BEN-370`'s

> **Git config resolution is SHARED where people assume it is SCOPED, and it fails toward a value that looks
> correct.**

`BEN-370` found it in `core.hooksPath` written from inside a worktree into the shared config, failing *open*
with no diagnostic. This is the same resolution model failing toward *the machine owner's name*. Two symptoms,
one model, and both are invisible because the failing value is a plausible one.

## Cross-references

- `BEN-395` — `%an` is not a lane field. **This is its cause**, and it makes the field biased rather than
  unreliable.
- `BEN-214`, `BEN-330` — attribution drift under a shared git identity, and hunks travelling in a shared tree.
  Both are downstream of this: the identity was shared because it defaulted to the owner's.
- `BEN-370` — the config-resolution model, above.
- `BEN-396` — verification allocated by suspicion. **My own thirteen commits are the instance**: nobody
  suspected my authorship, so nobody, including me, checked it.
- `BEN-084` — an artifact asserting the wrong thing beats no artifact for damage.
