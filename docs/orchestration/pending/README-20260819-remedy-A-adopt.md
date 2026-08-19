# PENDING — remedy (A) on `adopt_unified_5d.py` is implemented, reverted, and BLOCKED

**Lane B, 2026-08-19.** The patch beside this file is complete and tested. It is not in the tree.

## Why it is not committed

Any edit to `nd-unfolding/adopt_unified_5d.py` breaks a receipt `sha256` binding:

    verify_hash_bindings.py  ->  MISMATCH nd-unfolding/adopt_unified_5d.py
      want e1260e8dec2d39cb4653a8b4b02a198d04ea103d548a2d90b5f003f0b8044c35
      got  9c0f5d3923a4c7177a9ddf2c5020a3bc555d6f58ff0d81cdd4cd77f53e1178b7
      from docs/orchestration/state/ben106-stamp-verify-active-56695424.json

**The pre-commit hook refuses the commit**, and the guarding test states the remedy itself: *"the owning
gate must be deliberately re-run and its receipt re-issued — DO NOT JUST UPDATE THE HASH."*

**Confirmed mine and confirmed unavoidable.** Restoring the file to `HEAD` returns the verifier to
`181 OK / ALL BINDINGS INTACT`, so the binding was clean before this edit; and the conflict is with *any*
edit, not with this one's content. **So C's ruling that remedy (A) is MANDATORY BEFORE ADMISSION and
BEN-106's frozen binding are in direct conflict, and only a gate re-run resolves it.**

## What the patch contains

1. **The member identity** — `est_seed_offset` + `est_seed_offset_declared`, single-valued, from the
   process. Two keys, not a sentinel.
2. **The estimator seeds BY GROUP** — `upstream_estimator_seed_g1/_g2` and their `_checked` flags. **Not**
   a single `estimator_seed`: VL141 records that this product mixes g1 (`42+k`) with g2 (`1000+k`), so one
   key would be exactly the false quotable claim VL141 exists to correct.
3. **A cross-member refusal that could not exist before** — with g1's offset now reachable (via the
   analyzer's new stamp), a product assembled from two different members' legs is detectable **in the
   artifact** rather than only in the directory layout, which is the property C refused to rely on when it
   rejected glob non-recursion as a safety argument.
4. **C's §11g precondition** — `hDiagCombinedOld`, 0.0856 MB, from `diag_comb` already in memory at `:135`.
   A write, not a computation, and not an extra read of the 41 GB file. Without it `sqrt_tr_old` — the
   predeclared bar's own operand — stops being recomputable from retained bytes once §11g releases the
   intermediate.

## What must happen, and by whom

- **BEN-106's stamp-verify gate re-run and its receipt re-issued.** Not a lane's edit, and explicitly not
  a hash update.
- Then the patch applies, and `ADOPTED_UTHROW`'s commented-out key block plus
  `STAMP_COVERAGE["adopt_unified_5d.py"]["stamps"]` flip **in the same commit** — a writer change and a
  table change are one change, in both directions.

**Why the table was NOT left describing the intended state.** With those keys classified,
`identity_is_checkable("adopted_uthrow.root")` returns `True` while the writer stamps nothing — a gate
reporting that identity is checkable on an artifact that carries none. **A table describing a writer that
does not exist yet is worse than a table admitting the gap.**
