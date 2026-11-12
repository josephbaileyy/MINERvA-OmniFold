# BINDING 1 (design): RDX, the event-loop re-dump for the fresh referee's F1.2(i) (director, 2026-11-12)

**Binds** [`RDX-DECLARATION.md`](RDX-DECLARATION.md) design rev 3, sha256 `a37c49e49af8d8ea…`, as merged in PR #1090
at **M_RDX = `e747fc6c62a281aeca5d93ec173bb10fe231f672`**, byte-identical to its audited head `b3f61e0c`.

**Under:**
- the fresh referee round's F1.2(i), on whether truth information outside the five features matters
  (`state/2d-closeout/stageF/methods/methods-short-20261109/RESPONSE.md`);
- Joseph's instruction of 2026-11-11 to run new analyses that are not too costly;
- `RSN-BINDING-1.md` ruling 6, the approval in principle with a cap of 2.5 node-h, pilot included;
- [`DECISION-20261112-joseph-1a-cfs-and-redump-timing.md`](../../../../../DECISION-20261112-joseph-1a-cfs-and-redump-timing.md):
  the paper does not wait for this lane.

## What the director checked

**coverage-5b-audit's design reads,** over three rounds:
- **Rev 1** (`faf53d96`): five majors.
  - D1: the appended truth-only miss rows would get `truthx` = 0 through KNOWN_ISSUES #12's rebind.
  - D2: C-BKG needs no pilot.
  - D3: there was no permuted null.
  - D4: "the five features suffice" overreached.
  - D5: the build was not pinned to S0's MANIFEST.
- **Rev 2** (`319d38d0`): D1–D5 closed. One new major, D6: `truthx` was checked only by row count, so a
  misaligned column would read like the permuted null X1p.
- **Rev 3** (`b3f61e0c`): D6 closed. `truthx` and `mc_id` share the sentinel mask, the per-row join gate
  C-TRUTHX-NPZ runs before stage 3, and two mutants are declared. **GO for code**, with no blockers or majors.
  Lows y1–y5 are held for the code audit.

**The reference:** MP-1's bitwise chain (S0 `base_cv` 1A, `lat_zero.npz`), with each arm carrying its own nominal.
`of_inputs_5d.npz` is not the reference, because it came from a different binary and dump path
(`FD-CT-5B-INPUTS.md`:41-43, 53-55).

**The price:** projected about 1.40 node-h, with a ceiling of about 2.17 at the declared limits.

## Rulings

1. **The design is bound as declared at M_RDX.** No code exists yet. Code C1–C4, with tests and declared mutants,
   comes next. Then a code audit and a code addendum to this binding, before any build or connect.
2. **The price:** a **cap of 2.5 CPU node-h**, the pilot included. A projection above it at any gate STOPs to the
   director.
3. **Order:**
   - stage 0 (the build and D5's provenance) and the 1A pilot with C-ALIGN-1A and C-TRUTHX come first;
   - stage 2 only after both pass;
   - stage 3 only after C-TRUTHX-NPZ passes.

   Each connect's shas come to the director first. A new job-name family is announced to every fenced lane before
   its first submit. The inputs exposed to purge are read before 2026-12-15.
4. **C-BKG is out of this lane's scope.** It ran separately on 2026-11-12, at 0 node-h, on S0's `base_cv` 1A (#977,
   `methods-short-20261109/cbkg-20261112/`).
5. **Licence:** as D4 scopes it. Adding E_ν, the true vertex and the leading-proton KE moves the result by no more
   than the declared floor, beyond X1p, in MP-1's chain. Nothing is said about untested quantities.
   <!-- absence-ok: a scoping statement of this lane's licence (D4), not a claim that a result does not exist -->
6. **Timing:** the methods paper does not wait (#1092). A result ready before the paper is final is folded in through
   the usual value checks and reads.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the bound design, price and order.
- **Not citable for:** any reading. No code exists, and nothing has run.

Nothing is submitted, deposited or tagged.
