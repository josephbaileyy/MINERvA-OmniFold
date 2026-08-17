# DETERMINATION — the sha-identity hook: NOT WIRED, and it would have caught neither instance

**Lane E, 2026-08-17.** Answers the mediator's authorization to build C's proposed dispatcher check:
*"refuse a commit whose message names a sha that does not touch any file in that commit."*

**Nothing wired. `.githooks/pre-commit` unchanged by this work — still 9 `run` lines. No batch job,
no cluster work.** The authorization attached a condition — *"if the honest outcome is that the
innocent case cannot be separated from the defect at commit time, DO NOT WIRE IT, say so, and
deliver the measurement instead."* **That is the outcome, on three independent grounds, and the
third one is fatal on its own.**

---

## The defect is real and I am not disputing it

Two agents, warned, same hour, same error: a `MANIFEST`/`LIVE-STATE` auto-regen commit cited as the
commit that did the work. `git merge-base --is-ancestor` confirms **membership** and never
**identity**, and lane A's control is the clean demonstration — `8874f1f`, `2a92c71` and the repo
root commit all pass it identically. C's remedy is the right one and is better than an ancestry
test: `git log -1 --format=%h -- <path>` names the commit that touched **the file**, so an auto-regen
commit cannot satisfy it. **None of that is in question here.** The question is only whether the
rule can be *mechanised at commit time*, and it cannot.

---

## Ground 1 — the rule as specified rejects **66%** of real sha citations

Run over the last 150 commits, every 7–40 hex token in every message:

```
hex tokens seen              394
  resolving to a commit      168        (226 are sha256 fragments, digests, not commits)
    111  shares NO path with the citing commit  -> rule REJECTS
     57  shares a path                          -> rule PASSES

THE RULE WOULD REJECT 111 of 168 real sha citations (66%)
```

**And the rejected set is almost entirely innocent** — it is the normal, correct use of a sha in a
commit message: citing a prior finding, a superseded product, an authorization, another lane's work.
A sample, verbatim from the run:

```
9fddbf29 cites 966d202   BEN-394 amended: the commit that broke the trigger was the OI-96 fix…
b71ed839 cites 4dfeccd   BEN-382: git rebase does not run pre-commit…
fabdf421 cites b82ac63   OI-82 CLOSED — the third value is num/1e6…
d608e544 cites 00e794e   Causes 3 and 4: the shared leg was never an edit, it was a READ…
```

**This is the mirror of `BEN-387`'s inversion, exactly as the dispatch predicted** — there the guard
was silent on the defect and loud on the innocent edit; here it would be loud on the innocent edit at
a 66% rate. A hook that reddens on two commits in three is not a check, it is a `--no-verify`
generator, and it fails the dispatcher's admitting rule at `:11` more comprehensively than anything
currently declined there.

---

## Ground 2 — the narrow variant works, and its false-positive rate is **designed to grow**

The specified rule is too broad, so I tried the narrowest rule that still catches the defect. Both
instances cite an **auto-regen** commit — one whose entire diff is generated files — and that is
*why* the citation is wrong: **an auto-regen commit cannot be the commit that did the work, because
it contains no work.**

> **RULE 2:** flag a message citing a sha whose diff is entirely `MANIFEST.tsv` / `LIVE-STATE.md` /
> `live-state.json` / `MANIFEST-overrides.tsv`.

Measured, and it looks good at first:

```
8874f1f  autoregen=True   [LIVE-STATE.md, MANIFEST.tsv]   "Regenerate MANIFEST and LIVE-STATE after merge"
8a23194  autoregen=True   [LIVE-STATE.md, MANIFEST.tsv]   "Regenerate MANIFEST and LIVE-STATE after merge"

fires on 1 of 168 real sha citations over 150 commits (0.6%)
```

**Both known instances caught; one firing in 150 commits. Then read the firing.** It is
`257779c6 cites a05feee`, and `a05feee` is *also* `Regenerate MANIFEST and LIVE-STATE after merge` —
but lane A cited it as **the tree at which the check exited 1**, which is entirely legitimate. You
can measure a tree state at *any* commit, including a regen commit.

**So Rule 2 cannot separate "the commit that did the work" from "the tree I measured at", and the
second usage is the one this campaign has just adopted repo-wide.** `BEN-382`'s remedy — bind every
reading to the sha it was computed against — is now being applied by at least three lanes, including
in `.githooks/pre-commit`'s own header where I bound four readings to four shas an hour ago.
**Rule 2's false-positive rate is therefore not 0.6% and stable; it is 0.6% and rising, by design,
because the remedy for one defect manufactures the innocent case for the guard against another.**
A guard whose false-positive rate grows as the team gets *better* is the shape that trains people to
route around it.

---

## Ground 3 — the hook would have caught **zero of two**, and this ground stands alone

The dispatch raised this itself and asked me to check it. Measured:

```
git log --all --grep="8874f1f"   ->  (nothing)
git log --all --grep="8a23194"   ->  (nothing)
```

**Neither instance was ever cited in a commit message.** Both were in a **peer message** and a
**report to Joseph**. A commit-time hook cannot see either channel, so the check would have had a
0% detection rate on the entire measured population of this defect while rejecting 66% (Rule 1) or a
growing fraction (Rule 2) of legitimate commits.

**That inverts the cost/benefit completely, and it generalises past this item:** *the channel a
defect actually travels on is an empirical question, and a hook is a commit-channel instrument.*
Before wiring any check, ask where the known instances occurred — here, both occurred somewhere no
hook runs. Wiring it would publish a green tick implying coverage of a class it does not cover,
which is `KNOWN_ISSUES 48`'s shape and the exact objection this lane raised an hour ago about field
pins being read as artifact integrity.

---

## What to do instead — and it is C's remedy, unwired

**The remedy is already correct and needs no mechanism: `git log -1 --format=%h -- <path>`.** It
makes the wrong answer *unavailable* rather than merely detectable, which is why it beats the
mediator's `git show --stat` form — that one still requires the human to read the output correctly.
**A form that cannot produce the wrong answer does not need a guard that catches it.**

**What is worth mechanising is not the check but the habit's absence of friction.** The reason both
agents got it wrong while knowing about it is that the *convenient* command (`git log -1
--format=%h`, no path) is one word shorter than the *correct* one. That is a documentation and
muscle-memory problem, and `CLAUDE.md`'s own principle — *prefer the executable form of any rule you
are tempted to write down* — is the thing that pushed me toward a hook here and is **wrong for this
case**, because no executable form is available on the channel where the defect occurs.

**Recorded rather than built.** If the disposition should be different — for instance, wiring Rule 2
as advisory — note that `run()` discards a passing check's output, so this dispatcher has exactly two
channels, silence and failure (`BEN-226`). *"Wire it but only warn"* is not available here.
