# FINDINGS — BEN id allocation policy history

**Why this file exists.** This policy lived in `FINDINGS.md`'s header, where it had grown to ~3.8 KB
of successive allocation schemes — the `060+`/`070+` ranges, the 200+ block, a renumber mapping, and
a superseding block table — each layer written without removing the one it replaced. Every agent
paid that on turn 1 to learn one thing: which block to allocate from. The current block table and
the renumber mapping stayed in `FINDINGS.md`; everything below is preserved **verbatim** as it stood
on 2026-08-12, because it records decisions and their reasons.

Nothing here is current policy. For current policy read `FINDINGS.md`'s header.

---

> **BEN id allocation — take ids from your lane's RANGE, not from the shared maximum (set 2026-08-07).**
> Two collisions in one day (041, then 044): concurrent lanes each fetch, each see the same highest id,
> and each increment. Sequential allocation from a shared maximum does not work here. Ranges as Joseph
> assigned them: **the GBDT/P4 lane takes 060+; the PET/nd-unfolding lane takes 070+.** Read the range,
> not the maximum. Committed verifier receipts that cite a pre-renumber id are left as written —
> rewriting a receipt to match a later renumber would falsify it.
>
> **NEW BLOCK 2026-08-12: 200+ is reserved for repo-infrastructure findings** — the ledgers, the read
> path, the dispatch machinery, anything that is not a physics lane. BEN-105 recorded that the namespace
> is exhausted *inside its documented ranges*, and 160/161 were then allocated above them anyway. Opening
> a block rather than incrementing a shared maximum is the only allocation that cannot collide with a
> lane's sequence, because no lane draws from it. First occupant: BEN-200.
>
> **RENUMBERED 2026-08-09: BEN-077→061, 078→062, 079→063, 080→064.** I allocated four ids from the
> shared maximum instead of my lane's range, landing them inside the PET block — the exact mistake
> the paragraph above warns about, made while reading the paragraph above. Caught on a merge that
> brought in PET's BEN-081; no collision had occurred, but the ranges would have stopped meaning
> anything. **Four already-pushed commit messages (`aa220b4`, `34068d0`, `2fdf384`, and the
> stage-6/mechanism commit) cite the OLD ids and are left as written** — same convention as the
> verifier receipts above. Use this mapping when following a commit message into the ledger.
> The lesson generalises the header: reading the range rule is not the same as applying it, and the
> moment of allocation is when to re-read it, because `max(existing)+1` is what a tired agent
> computes by default.
>
> **BLOCKS AS THEY STAND 2026-08-12, set by the orchestrator and superseding the two open-ended
> ranges above for the close-out campaign.** Read this table, not the `060+`/`070+` sentence.
>
> | lane | block | state |
> |---|---|---|
> | D — verifier | `090-099` | **EXHAUSTED** at BEN-099 |
> | B — uncertainty construction | `100-129` | in use through BEN-115 |
> | C — PET | `130-159` | in use through BEN-138 |
> | **D — verifier, successor** | **`160-189`** | **opened 2026-08-12, empty** |
> | **A — orchestrator** | **`190-199`** | **opened 2026-08-12, empty** |
>
> **Two things this fixes, both of which had already cost something.** D's block ran out on the last
> night of the close-out with no successor defined, which is BEN-105's *"a range exhausted with no
> successor rule"* recurring — a successor is now named in advance rather than at the moment of need,
> which is the moment BEN-105 identifies as the worst time to allocate. And **the orchestrator held no
> block at all**, so two orchestrator-origin findings were routed into D's block for want of anywhere
> else (BEN-097, BEN-098) and D's own `160-189` was consumed faster as a result; BEN-092 flagged that
> gap and it is closed here.
>
> **What this does NOT fix, stated so it is not read as closed.** The ranges are still enforced by
> attentiveness and not by an allocator. BEN-105 counts four instances of attentiveness failing, twice
> while the failing agent was reading the rule; BEN-080 records the exposure as *"known and accepted,
> not fixed"*. Adding two blocks makes the next allocation defined; it does not make a wrong one
> detectable. A fifth instance is the evidence that the choice was wrong, per BEN-105's own terms, and
> it should be read that way rather than as a fifth instance.
