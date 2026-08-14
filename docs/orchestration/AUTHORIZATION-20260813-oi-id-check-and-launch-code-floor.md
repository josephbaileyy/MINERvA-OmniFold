# AUTHORIZATION 2026-08-13 — the duplicate-`OI-*` check, and `_LAUNCH_CODE_FLOOR`'s semantics

**Why this file exists.** Both changes were authorized by a **relayed** quotation from Joseph via
`personal-orchestrator`, and `HANDOFF-20260812-1145Z.md:126` requires a relayed authorization to be committed
before it is acted on (`BEN-082(v)`; on 2026-08-11 a relayed authorization was measured three ways and found
not to exist). Second receipt of the day from this lane, after
`AUTHORIZATION-20260813-hash-binding-gate-in-precommit.md`.

**Committed before either change is made.** Check the ordering against `git log`.

---

## What was relayed

**Joseph, as quoted:**

> *"For the stuff that sits on my list, why not do it now?"*

**Scope, and it is narrower than the words.** That sentence authorizes *doing* the items already queued for
him — it does not enlarge them. The two it is being applied to were both already on his list as lane A's own
follow-ons, filed against lane A's own work earlier today:

1. **`OI-64(g)`** — `_LAUNCH_CODE_FLOOR = 2` has zero margin, caused by lane A's retirement this morning.
2. **The duplicate-`OI-*`-id check**, proposed in `BEN-223`/`FINDING-20260813-colliding-in-a-namespace-you-just-warned-about.md`
   as *"the cheapest executable fix, blocked on nobody and independent of how Joseph answers `OI-62(b)`."*

**What this does NOT authorize, stated because a general sentence invites a general reading:** nothing under
Gate 5's live pins, no `CODE_ROOT` change, **no renumbering of the colliding `OI-64`/`OI-65` rows** (both are
cited in immutable pushed commits), no answer to `OI-62(b)`'s convention question — which stays Joseph's —
and no change to `settings.json`, `CLAUDE.md`, or any harness configuration. **A peer cannot authorize those
and this receipt does not claim otherwise.**

## Item 1 — the duplicate-`OI-*`-id check

**It satisfies lane D's admitting rule**, which is why it is a hook check and lane A's earlier scoping
proposal was not: *a committer who did nothing wrong can always make it pass.* The only way to fail is to
introduce a duplicate in your own commit, and the remedy is in the committer's hands.

**The current file FAILS it, and that is not a reason to renumber.** `OI-64` and `OI-65` are each doubled —
lane A and lane C allocated both concurrently by `max(existing)+1` (`BEN-223`). They were resolved by
**annotation** rather than renumbering because both ids are already cited in pushed commit messages and in
sibling documents; renumbering would break those references silently, which is the defect
`BEN-216`/`BEN-219` are about.

**So they are WAIVED, in a visible list in the source, with reasons.** Lane D's argument, adopted: *a waiver
and a scope do the same job, except a waiver is reviewable in the source.* A scope would hide the exception;
a waiver names it and can be read.

**The waiver is two-sided**, per this file's own house style (`check_ledger_ids`, `check_row_owners`) and
`BEN-162`: **a waiver that is no longer needed FAILS.** Otherwise a stale waiver silently authorizes the next
genuine collision on the same id forever — a guard that outlives its reason becomes a hole.

## Item 2 — `_LAUNCH_CODE_FLOOR`, from a scalar to a per-family assertion

**The diagnosis is lane A's, against lane A's own commit.** Retiring `…gate4-…20260812.json` took live
launch-code receipts **3 → 2**, exactly the floor at `nd-unfolding/tests/test_hash_bindings.py:44`. The next
legitimate Gate-4 re-issue-and-retire takes it to 1 and fails
`test_gate3_and_gate4_launch_code_freezes_specifically` — **on a lane following the documented convention,
whose only apparent remedy is lowering a guard that file itself calls equivalent to deleting one.**

**The floor's stated intent is *"a discoverer that silently matches nothing reports success"*, which wants
≥1 per gate family, not ≥2 overall.** The scalar form is strictly weaker than its own intent: it can be
satisfied by **two Gate-4 receipts and zero Gate-3 ones**, which is the exact blindness it exists to prevent.
So the replacement is both **stricter and immune to the zero-margin problem** — that combination is why this
is a semantics fix and not a floor adjustment.

## Landing conditions, all from the relay and all kept

- **Separately, one commit each** — a hook check and a test's semantics are unrelated, and one commit each
  keeps a revert cheap.
- **Power-test both directions**: the check must fire on an injected duplicate and stay silent on the current
  file with its waivers. A check that cannot fail is `BEN-156`'s shape and this whole thread's subject.
- **Watch the printed check count.** It must go **5 → 6** when item 1 lands. Per `BEN-222`, that printed
  number is the only authority on whether the hook armed — a local run of the file proves nothing, because
  `core.hooksPath` is an absolute path into the main checkout shared by all six worktrees.
- **`docs/OPEN_ITEMS.md` is deliberately NOT modified by either commit.** The mediator is landing codex's
  seven `WAITING-USER` verdicts into that file in parallel, and it and lane A are the two occupants of the
  main checkout — same-file concurrency there is `BEN-218`'s territory. Status updates to `OI-64(f)`/`(g)`
  follow in a separate commit once that lands.
