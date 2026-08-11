# The live Gate-4 receipt asserts a blocker that closed five days earlier, and its evidence is a pointer to a key that was deleted

**Found 2026-08-11 by Session C (PET), in its own lane's artifact.** BEN id **PENDING BLOCK ASSIGNMENT** —
see §6; the PET range is exhausted and taking `max+1` is the failure BEN-105 was written about.

## 1. The defect

`docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260810c.json` — the **live** Gate-4 launch
code gate, `observed_at_utc 2026-08-10T13:20:00Z` — carries:

    "prerequisite": { "gate2": "PASS (RE-ISSUE PENDING -- see open_blockers.gate2_reissue_pending)" }

and its `open_blockers` block contains exactly four keys, **none of which is
`gate2_reissue_pending`**:

    nominal_must_be_RE-TRAINED_under_the_fixed_driver
    gate4_still_cannot_PASS
    powered_closure_criterion_reason_REFINED_2026-08-07
    step1_under_achieves_by_32pc

So a reader who follows the receipt's own pointer to find out *what* the Gate-2 blocker is finds
nothing.

**And the assertion it makes is false.** The Gate-2 re-issue landed on **2026-08-05**, five days before
this receipt was written: commit `8a9d22c` *"Land the re-issued Gate-2 receipt, archive both superseded
runs, close every live pin"*, with the superseded run archived at
`nd-unfolding/g2_fullevent/gate2/final/superseded-20260805-r1/` (`status: SUPERSEDED`) and the live
receipt at `gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json` reading
`status: PASS`, `verdict: GATE2_CANONICAL_RUNTIME_PASS_INDEPENDENT_PROMOTION_PENDING`.

**The receipt names the wrong pending thing.** What is actually outstanding for Gate 2 is *independent
promotion*, which the Gate-2 receipt says in its own verdict string. What the Gate-4 receipt claims is
outstanding is a *re-issue*, which is done. Those are different acts with different owners, and a reader
planning work off the Gate-4 receipt would schedule a run that has already happened.

## 2. How long it has been there: nine consecutive re-issues

Measured across every receipt in the family:

| receipt | pointer present in `prerequisite.gate2` | target key present in `open_blockers` |
|---|---|---|
| `20260721` | no | no |
| `20260731` | **yes** | **yes** ✓ consistent |
| `20260801` | **yes** | **yes** ✓ consistent |
| `20260801b` | **yes** | **NO** ← breaks here |
| `20260806`, `20260806b`, `20260806c`, `20260807`, `20260809`, `20260810`, `20260810b`, `20260810c` | **yes** | **NO** |

The break is at `20260801b` and it has been carried by **nine** successive receipts, each derived from
its predecessor.

## 3. The recovered content, so it is not lost twice

From `20260801` — the last receipt that still carried the key:

> **state:** "Both Gate-2 receipts remain red on `fullevent_fps_dataloader.py`, and
> `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` on `gate2_target_runtime.py`. RESTORE Step 2 owns them, and this
> patch added the FINDING-20260730 guard to the dataloader, deepening (not creating) that drift."
> **consequence:** "`nd-unfolding/tests/test_hash_bindings.py::test_no_new_broken_hash_bindings` stays RED
> until Step 2 re-runs Gate-2 on the real dump. That red is correct behaviour. Do not repair it by
> editing receipt hashes to match the tree."

That blocker was **real and is now resolved** — `20260810c`'s own `gate_state` records
`test_no_new_broken_hash_bindings = GREEN after this re-issue`. So the deletion of the key was correct.
**The bug is that the deletion was half-done:** the record was removed, and the *claim* that pointed at
it was left behind.

## 4. Why nothing caught it, which is the part worth carrying

This is the inverse of the shapes already catalogued. Those are cases where a **check** reads state it
cannot see. Here the state is fine and the **pointer** is the casualty:

- **A resolved blocker's record is deleted, and the assertion referencing it survives.** Deleting the
  record is the correct act; the assertion is in a *different block of the same file* and nothing ties
  them together. The natural editing motion — remove the closed blocker from `open_blockers` — does not
  visit `prerequisite`.
- **The failure is self-concealing in the reassuring direction *for the deleter* and the alarming
  direction *for the reader*.** The receipt over-reports work outstanding, so no gate fires, no test
  goes red, and nobody is blocked by it. It just makes the campaign look further from done than it is —
  which is exactly why it survives: **an over-cautious receipt generates no pressure to fix it.**
- **Derivation propagates it for free.** Each re-issue copies its predecessor and edits the fields it is
  about. A field nobody is currently thinking about is never re-read, so nine receipts asserted it.
- **A dangling pointer is weaker evidence than no pointer at all, and reads as stronger.** `"PASS
  (RE-ISSUE PENDING -- see open_blockers.gate2_reissue_pending)"` looks *more* sourced than a bare
  `"PASS (RE-ISSUE PENDING)"`. The citation is the thing that makes it credible, and the citation is the
  part that is broken.

**Mechanical check this suggests, and it is cheap enough to be worth running across the state tree:** for
every string in a receipt of the form `see <block>.<key>`, assert `<block>.<key>` resolves. That is a
pure JSON walk over `docs/orchestration/state/*.json`, no domain knowledge required, and it would have
caught this on 2026-08-01. Offered to the verifier lane's corpus as a fifth shape rather than
implemented here, because a sweep whose corpus nobody checked returns a plausible list.

## 5. Disposition: the receipt is NOT edited

Per this repo's standing convention — committed receipts are historical records and are not rewritten to
match a later state (the same reasoning that leaves pre-renumber BEN ids in commit messages, and that
forbids hand-editing a stale hash to clear a mismatch) — **`20260810c` is left exactly as written.** Its
claim was wrong when made; making it look right now would destroy the evidence that it was wrong for
nine receipts.

The correction lands in the **next** Gate-4 re-issue, which is required anyway: promoting the annealed
nominal `56563761` would force a re-issue on independent grounds, because `20260810c`'s
`gate_state.quotability` reads *"branch C STILL GOVERNS: the fold-forward deficit (~34%) is untouched"* —
scoped correctly to today's canonical artifact, but **falsified as a description of the canonical
artifact the moment a `-3.56%` artifact becomes canonical.** So the next re-issue owes two corrections:
`prerequisite.gate2` (re-issue done 08-05; independent promotion is what remains) and the quotability
rationale. Both are recorded here so the re-issue cannot be written without them.

**Note the timing, because it is a near-miss rather than a caught error:** `20260810c` was written at
`13:20:00Z` and the annealed nominal's own completion marker is `2026-08-10T18:00:43Z` — the gate predates
the artifact by 4 h 40 m. Nothing is wrong with the gate for that reason; it is why its quotability text
must not be read forward.

## 6. BEN id: deliberately not allocated

BEN-105 records that both documented ranges are exhausted, that `max(existing)+1` is the allocation the
header forbids, and that it has now failed four times — once inside the row written to complain about it.
Measured here: ids present on `origin/main` are **001–046, 060–089, 100–105**; the uncertainty lane holds
`100+`, the verifier holds `090–099` by the orchestrator's assignment, and **the PET lane has no free
block**. Taking `106` would be the fifth instance and would collide with the uncertainty lane's next
allocation.

So this finding is filed **as a long-form document and indexed**, which is the load-bearing part — an
unindexed finding is one nobody reads — and the block assignment is routed to the orchestrator, exactly
as BEN-105 did rather than taking it as settled. The row will be added under whatever block is assigned.
