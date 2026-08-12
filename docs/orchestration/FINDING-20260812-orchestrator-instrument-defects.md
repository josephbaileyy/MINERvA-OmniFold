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

## BEN-192 — three status sources disagree about the same sessions at the same instant, and the two that call themselves *status* are the two that disagree most

Raised by the personal-account mediator session, which found the `ListAgents` status column for two
sessions was **last written 14.4 hours ago** — a stale field presented as current state. Re-measured here
and it is broader than that: **there are three independent signals and no two of them agree.**

Measured in one turn at `12:46:33Z`:

| session | `ListAgents` column | job registry `state.json` `status` | transcript mtime |
|---|---|---|---|
| A — orchestrator (me) | *(self, not listed)* | **`blocked`** | `12:46:12` — actively writing this |
| B — uncertainty construction | **`idle`** | **`done`** | — |
| C — PET | **`busy`** | **`blocked`** | — |
| D — verifier | **`idle`** | **`working`** | — |
| `minerva-omnifold-07` | **`busy`, started 14h ago** | — | `12:40:45`, 27 922 B — alive 6 min earlier |
| `minerva-omnifold-6e` | **`busy`, started 14h ago** | — | `12:19:12`, 20 192 B |

**Three of the four lanes disagree between the two status sources, and the registry calls the session
writing the measurement `blocked`.** So neither field is a measurement of activity. Only transcript mtime
is an artifact, and it is the one neither tool reports.

**This invalidates every lane-state claim Session A made from `ListAgents` today**, including
*"all three lanes idle"* — which the mediator had already caught as a snapshot presented as a state. The
mechanism is worse than the one I conceded to: it was not merely that my snapshot aged, it is that
**the field was never current.** Both readings of the same error, and I had the shallower one.

**BEN-028 INVERTED, and that is the reusable form.** BEN-028: *a quiet log does not mean a dead job —
judge by `sstat` CPU and produced artifacts, never by log growth.* Here: **a stale status does not mean a
dead session, and a `busy` status does not mean a live one — judge by artifacts either way.** Same
underlying error, opposite direction. The mediator's observation is the sharp one: **the tool the
four-lane protocol uses to enumerate its own peers has exactly the defect the four of us keep finding in
each other's reports.**

**Rules.** (i) Never report a peer's activity from `ListAgents`'s status column or from
`state.json`'s `status`; both are transition-written, not sampled. (ii) If you need to know whether a peer
is alive, read its transcript mtime, or ask it and wait — asking is the only signal that is also a
measurement. (iii) A peer's *existence* and *name* from `ListAgents` are reliable; its *state* is not, and
the listing does not distinguish the two.

**One residual, not chased:** `minerva-omnifold-07`'s transcript is 27 922 bytes after fourteen hours.
Whatever it is doing it is producing almost nothing, which is a separate oddity from whether it writes to
this repo — and it has now received a delivered, unanswered question about exactly that.

*Stale-field defect found by the personal-account mediator, which also disclosed that its first
explanation — two sessions wedged mid-turn — was wrong, and that it caught this by requiring a second
independent signal before reporting. The three-way disagreement and the BEN-028 inversion are Session A's.*

## BEN-193 — coverage is invisible by construction: a set you cannot see does not announce that you cannot see it

Named by the personal-account mediator session, which asked for it as a row in its own right rather than a
footnote to C's. **The pattern is not carelessness.** Four instances in one day, three lanes, all in
enumerations or coverage rather than in results:

| instance | what was claimed | what the claim was actually about |
|---|---|---|
| slab manifest, *"sha256 for 548 `.npz` and zero ROOT files"* | ROOTs were overlooked | an **npz-only sweep by design**, scoped by role |
| C's hashing, *"no digest anywhere"* | the object has no digest | 140 of 2,464 files were unhashed, filtered by `awk '$1 < 5000000 && $1 > 0'` — the object was skipped for being **large** |
| C's enumeration, *"2,464 files, 2.77 GB uncommitted"* | the uncommitted working tree | **`git status -uall` cannot see ignored files**; `.gitignore:2` is `*.root`; actual 19,570 files / 6.00 TB, **2,163×** |
| A's `~/.claude` settings edit (BEN-190) | the setting is applied | applied to a directory **not in the read path** — `CLAIDE_CONFIG_DIR` is `~/.claude-school` |

**The unifying mechanism, in the mediator's words: a set you cannot see does not announce that you cannot
see it.** An absence claim has a hidden operand — the coverage of the instrument that found the absence —
and unlike a numeric operand it produces **no arithmetic that fails to reconcile**. Every one of the four
was caught only because someone re-derived a *different* number and the gap in it pointed back at coverage.
The 140-file gap is the clean example: it was found by subtracting two file counts nobody had put side by
side, and it was the only reason "no digest" could be distinguished from "outside every digesting sweep."

**And being caught once does not inoculate.** C corrected the slab manifest's scope-by-design error and
then committed the identical error in the same artifact one level up — hashing coverage, then enumeration
coverage. Its own sentence, which is the transferable part: **"being challenged on coverage once did not
make me check the other coverage."**

**Rules.** (i) **Point the arithmetic-gap instinct at ENUMERATIONS, not only at hash counts** — if two
counts of the same population differ, the difference is the finding. (ii) An absence claim must ship its
**coverage** as an operand, the same way a derived number ships its ingredients (BEN-077). *"No digest
anywhere"* without the enumeration that looked is unfalsifiable. (iii) When an instrument excludes by
**design**, that is a scope statement and not a coverage gap — and the two read identically in prose, which
is what makes them worth distinguishing explicitly. (iv) Before trusting any enumeration, ask what it
**structurally cannot** enumerate: `git status` cannot see ignored files, a size filter cannot see large
files, a settings read cannot see a different config directory.

*Class named by the personal-account mediator, which disclosed two near-misses of its own in the same
family. Instances and the table are Session A's; the third and fourth rows are self-directed.*
