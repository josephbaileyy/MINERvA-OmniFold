# FINDING 2026-08-14 — the rebase falsified a verified claim inside the commit carrying it

**`BEN-225`.** Lane A, found by lane D on review. **Seven seconds elapsed between the claim being true and the
commit publishing it being false.**

## The measurement

`ea4a4f3`'s message asserted, as a deliberate verification step:

> *"`BEN-186` IS CITED AS ANNOUNCED-BUT-NOT-YET-FILED, verified by grep rather than assumed: `BEN-173`, `180`,
> `183` and `185` exist as rows; `186` does not."*

| moment | reflog | state |
|---|---|---|
| grep run, tree at `23d9c50` | — | `BEN-185` present (**1**), `BEN-186` absent (**0**) — **the claim was TRUE** |
| **00:41:20** | `commit: ea4a4f3` | message carries the claim |
| **00:41:27** | `pull --rebase origin main (start): checkout a2b98e7` | `a2b98e7` (Lane D) had filed `BEN-186` |
| **00:41:27** | `(pick) → 542bdad` | **`BEN-186` present (1) in the published commit's own tree** |

Measured at both refs: `git show 23d9c50:…/FINDINGS.md | grep -c "^| BEN-186 "` → **0**;
`git show 542bdad:…/FINDINGS.md | grep -c` → **1**. `git log -1 -S "| BEN-186 |"` → `a2b98e7`.

## What this is NOT, because the obvious reading is wrong

**This is not `BEN-183`'s "I measured the wrong tree."** The tree was the right one — lane A's own worktree,
the tree the commit was being made from — and the grep was accurate in it. Nor is it a pattern error: the
identical pattern matched `BEN-185` in the same run.

**The rebase changed the tree the commit describes, and left the message untouched.** `git pull --rebase`
replays your commit onto a new base; the diff is reapplied, the message is copied verbatim, and any factual
claim in it about *tree state* is silently re-scoped to a tree that did not exist when the claim was verified.

## Why it gets its own row rather than folding into `BEN-224`

Applying the criterion lane D and lane A settled hours earlier — **separate when the remedies differ:**

| | `BEN-224` | this row |
|---|---|---|
| mechanism | the hook file and its payload come from different **trees** | the **same** tree changed under a claim between verification and publication |
| when it bites | at execution | at `git pull --rebase`, after the work is done |
| the fix | make the hook bind the payload it invokes | **re-verify tree-state claims after a rebase — or do not put them in a commit message at all** |

## The transferable rule, and it is about the medium

**A commit message is immutable. A verified claim about a concurrently-written tree is not.**

Those two facts are incompatible, and the incompatibility is structural rather than a lapse:

- The message cannot be corrected in place, only superseded by a later commit that most readers will never
  reach from it.
- Four lanes write `FINDINGS.md` concurrently, so any assertion of the form *"row X does not exist"* has a
  shelf life measured in minutes.
- **So the absence of another lane's artifact does not belong in a commit message.** Put the verification in a
  **file**, where a later session can amend it and where the amendment is visible at the point of use. That is
  the same reasoning `BEN-201` gives for retractions landing at the point of use rather than only in an index.

The narrower operational form, for when a message really must carry a count:
**re-run the check after `git pull --rebase` and before `git push`.** The rebase is the event; nothing else in
the workflow moves the base under a finished commit.

## Third instance today of one shape, and the shape is worth naming

- `BEN-219` — `VALIDATION_LEDGER.md:1043` was exact when written and pointed 73 lines off 15 hours later.
- `BEN-222` — lane C's *"the pre-commit hook doesn't run the hash-binding gate"* was true when written and
  silently became false when the main checkout pulled.
- **this row** — a grep was true when run and false in the commit that published it, 7 seconds later.

**Right at write time, wrong at read time**, at three different timescales — hours, hours, seconds — in three
different media: a document, a message, a commit message. The generalisation is not "check your facts"; it is
that **a fact about a concurrently-written repository is a measurement with a timestamp, and publishing it
without one is what fails.**

## The part that makes it the strongest entry in the family

**The measurement that went stale was itself a verification step**, performed specifically to avoid citing a
row that did not exist (`BEN-216`), inside the commit that adds
`CONVENTION-verifying-a-check-is-deployed.md` — a convention about not trusting checks you have not probed.

That is not irony worth enjoying; it is the reason the convention now names the one case where its probe is
**mandatory** rather than optional. A limits section is the first thing a future agent quotes to skip the work,
which is lane D's caution and it was correct.

## Related

`BEN-224` (sibling: different trees, versus one tree changing), `BEN-219` (right at write time, wrong at read
time — the ledger-line instance), `BEN-222`, `BEN-216` (a pointer to nothing — what the stale verification was
trying to prevent), `BEN-183` (measuring the wrong tree — explicitly *not* this),
`CONVENTION-verifying-a-check-is-deployed.md`.
