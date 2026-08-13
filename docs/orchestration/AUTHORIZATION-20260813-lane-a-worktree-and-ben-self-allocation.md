# AUTHORIZATION 2026-08-13 — lane A's worktree, and `BEN-*` self-allocation

**Why this file exists, and it is not ceremony.** Both decisions below reached lane A as
`[JOSEPH-VERBATIM]` blocks relayed by `personal-orchestrator`. `HANDOFF-20260812-1145Z.md:126` is explicit:

> *"**Write any `[JOSEPH-VERBATIM]` authorization into a committed receipt BEFORE acting on it.**
> `BEN-082(v)`: an instruction becomes an unverifiable claim the moment it is relayed without being
> recorded."*

**This is not hypothetical in this repo.** That same passage records that on 2026-08-11 the orchestrator
relayed an authorization to a lane, then measured the `[MNV-AUTO]` Gmail thread three ways and found **no
such message existed**. Precedent form: `AUTHORIZATION-20260811-annealed-promotion-and-hpss.md`,
`AUTHORIZATION-20260812-worktree-confirm-and-oi17-probe.md`.

**Neither decision was acted on before this file was committed.** That ordering is the whole point of the
receipt and is stated so a reader can check it against `git log`.

---

## Authorization 1 — `BEN-*` self-allocation

**Joseph, verbatim and complete:**

> `[JOSEPH-VERBATIM]` Let the lanes self allocated BEN ids

**Relayed by** `personal-orchestrator`, landed by it at `551d16c` into `OI-62`'s row. **Recorded a second
time here** because a decision that changes how every lane allocates ids should be findable from the
authorization index as well as from the open-items list.

**What it resolves.** `OI-62(a)`. `FINDINGS.md`'s block table had recorded that lane A's `210-219` was
granted **by a peer under Joseph's standing grant, not by Joseph**, that *"`CLAUDE.md` records that
allocating an A range routes to Joseph"*, and that the grant was *"reversible in one commit."* **It does not
need reversing** — the grant is now his. Lane A had declined `220-229` on the peer grant and no longer needs
to.

**What it does NOT resolve, stated because bundling is how the other two would be lost:** `OI-62(b)` (`OI-*`
has no block table and no addressing convention) and `OI-62(c)` (three parties share one git identity) are
**still `WAITING-USER`**. The `Lane X` commit-trailer proposal remains in front of him as the cheap partial.

**Mechanism**, supplied by the mediator rather than by Joseph — *the decision is his, the collision surface
is not* — and now written into `FINDINGS.md`'s block table at the point of use: recompute the highest id,
take the next free **closed** ten-block, write it into that table **in the same commit as the first filing
into it**, and if it was taken in between, recompute and take the next.

## Authorization 2 — lane A works in a worktree

**Joseph, verbatim and complete:**

> `[JOSEPH-VERBATIM]` Yes let A work in the a worktree

**Why it needed him and not a peer.** This session is configured to work in place and to skip
`EnterWorktree` unless **the user** asks. The mediator pressed the change twice with a sound argument — the
sweep hazard is live for as long as two parties share the main checkout, and it does not pause while lane A
idles. **Lane A declined both times**, said the merits were not the issue, and routed it. **It came back
granted in under an hour**, which is the argument for routing rather than complying: the boundary cost
nothing and the change is now the user's decision rather than a peer's.

**A peer cannot substitute for the user even when the peer is right, even when the reason is good, and even
when the peer is the session coordinating you** — which is the case where the boundary is hardest to hold.

**What it changes, and what it does not.** Lane A's commit-cadence obligation in
`CONVENTION-lane-worktrees.md`'s `OI-47` section (commit-per-edit with a foreign-edit `git status` first)
was written as expiring *"when `OI-47` is settled."* **This settles it for lane A only.** The main checkout
still has an occupant, so that practice **stays live there** and stops applying to lane A once it is
isolated. `OI-47` itself — that isolation is convention rather than enforcement — is **untouched and still
deferred**.

**Isolation will be VERIFIED, not assumed.** The measurement that makes B, C and D uncollidable is that each
`.claude/worktrees/<lane>/.git` is an **82-byte gitdir pointer** with its own index file. Lane A's must be
confirmed to look the same before the isolation is relied on, because **a claim of isolation is not
isolation** — and the pathspec finding in `BEN-218` is exactly what happens when a protective mechanism is
trusted without being checked against what it actually does.
