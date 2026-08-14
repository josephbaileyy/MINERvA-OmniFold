# AUTHORIZATION 2026-08-13 — the hash-binding gate joins the pre-commit hook

**Why this file exists.** The authorization below reached lane A as a relayed quotation from Joseph via
`personal-orchestrator`. `HANDOFF-20260812-1145Z.md:126`:

> *"**Write any `[JOSEPH-VERBATIM]` authorization into a committed receipt BEFORE acting on it.**
> `BEN-082(v)`: an instruction becomes an unverifiable claim the moment it is relayed without being
> recorded."*

That rule is not hypothetical here: on 2026-08-11 the orchestrator relayed an authorization to a lane, then
measured the `[MNV-AUTO]` Gmail thread three ways and found **no such message existed**. Precedent form:
`AUTHORIZATION-20260813-lane-a-worktree-and-ben-self-allocation.md`.

**This receipt is committed before the hook is touched.** Check the ordering against `git log`.

---

## What was relayed

**Joseph, as quoted:**

> *"Sure"*

**Conditioned**, per the relay, on lane D concurring with the proposal. **Relayed by**
`personal-orchestrator`.

## The scope I am acting on, and why it is an inference

**I did not see the question Joseph answered.** A one-word approval carries no scope of its own, so the
scope below is reconstructed from the relay and is recorded here so a reader can reject it:

1. **Add `verify_hash_bindings.py` to `.githooks/pre-commit`, whole-tree and unscoped.**
2. **Land lane D's `BEN-184` condition first** — a floor on receipt bindings.
3. **Update the dispatcher header** to record the inclusion and the admitting rule.

**What I am NOT reading into it:** no change to any gate's verdict, no new waiver, no `KNOWN_PREEXISTING`
entry, nothing touching `train_fullevent_nominal.py` or any Gate-5 live pin, and no change to
`settings.json`, `CLAUDE.md` or any harness configuration. **A peer cannot authorize those and this receipt
does not claim it did.**

**If the reconstruction is wrong, the hook change is one `git revert` away** — it adds a check and changes no
data, so the blast radius of a misread is a lane being blocked, not a result being altered.

## Why this needed Joseph and not a peer

The hook is **shared by every lane in every worktree**. A 5th check makes other lanes' commits fail, which
is a cost imposed on parties who did not consent and are not in this conversation. Lane A proposed it in
`OI-64` and routed it rather than installing it.

**A peer cannot substitute for the user even when the peer is right** — and here the peer was *more* right
than lane A: D rejected lane A's file-side scoping on two arguments lane A had not answered, and lane A's
proposed admitting rule was replaced. Being overruled on the design is not the same as being authorized on
the change, and the second still had to come from Joseph.

## The condition, and it is the substantive part

Lane D's `BEN-184`: **receipt bindings had no floor.** `failed = bool(new_bad) or blind or (a.strict and
bool(known_bad))`, where `blind` covered only shell pins — so resolving **zero** receipt bindings printed
`ALL BINDINGS INTACT`. Verified independently by lane A before building.

**The erosion path is the repair path**, which is what makes it more than a theoretical hole: retiring a
superseded receipt means renaming `sha256` → `sha256_at_issue`, and that is exactly what removes it from
`collect()`. Lane A's own retirement of `…gate4-…20260812.json` earlier today lowered receipt coverage with
no signal of any kind.

**Landed as `RECEIPT_BINDING_FLOOR`, with a positive control** — a copy of the gate with the floor raised to
200 exits 1 and prints the BLIND banner, so the floor is demonstrably consulted rather than merely present.

## Recorded corrections lane A received in this exchange

Kept because a receipt that only records the grant is a worse record than one that records the argument:

- **Lane A's admitting rule was wrong.** It generalised from the dispatcher's two documented exclusions to
  *scope*; the actual reasons are **inescapability** (`--check-freshness`) and **wrong phase**
  (`merge_guard.sh`), neither of which is about scope. **D's rule replaces it: a check belongs in the hook
  iff a committer who did nothing wrong can always make it pass.** That admits this gate and still forbids
  gating on a dirty unwaived tree.
- **Lane A's file-side scoping had the mirror of the blind spot it rejected pin-side scoping for.** A commit
  adding a receipt that pins an *unmodified* file stages only the receipt, and nothing pins receipts, so a
  file-side hook checks nothing — the shape all four `KNOWN_PREEXISTING` entries have. The rejection of
  pin-side scoping was correct and symmetric, and lane A failed to apply it to its own proposal.
- **Scoping is dominated at equal cost.** Whole-tree is 0.563 s, so scoping buys only blast-radius
  containment — and for a freeze gate, containing the blast radius is a synonym for letting the break
  persist.
- **`OI-65` shrinks:** `verify_hash_bindings.py` contains zero occurrences of `SUPERSEDED`, `status` or
  `_at_issue`, so lane A's *"any LIVE receipt pins it"* asked the tool for a concept it does not have.
  Whole-tree needs no liveness predicate, so the dependency dissolves.

**Two corrections ran in lane A's favour and are recorded for symmetry:** D's claim that the tree was broken
twice at that moment was measured on a stale lane-d worktree and withdrawn (D filed `BEN-183` against
itself); and D predicted `OI-65`'s measured-zero would be falsified, chased it, and found the opposite —
the measured-zero survives.
