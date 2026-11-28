# COVFIX PG seal and ledger: follow-ups carried forward (cov2d, 2026-11-27)

These are the items from the PG seal and ledger reads that the director ruled non-blocking (ruling on round 6,
2026-11-27). The scope rule: after round 6, only a finding that could change a published number or a gate's acceptance,
or cause a false STOP of a correct run, blocks; everything else comes here. Each item is closed in the code chain that
owns it, with its own test and mutant, or kept with a reason.

## For PV's decrypt-and-write step (the PV design round, after the PG rehearsal)

1. **SealedManifest's backing maps are mutable.** `SealedManifest` keeps private copies of its `products` and
   `paths` dicts in slots (`_products`, `_paths`); the copies themselves can still be changed. A PV caller that deletes
   an entry (for example `manifest._products`) makes `publish_guard` stop
   refusing that entry's plaintext hash, because `ids()` no longer lists it. PV requirement: hold read-only views
   (`types.MappingProxyType` over private copies) and test that every mutation raises. No PV caller exists yet.
   (codex-school2 round 5, "decryptors" PARTIAL and the MAJOR "mutating the manifest can disable hash protection";
   `reads/codex2-r5/REPORT.md`)

## Ledger

2. **The old-format diagnostic after a torn append.** `state()` checks the policy line's format only after
   `_entries()` has parsed every line, so a ledger whose policy is an older format and whose last line is a torn append
   is refused as "ledger line N is not JSON" instead of "expected format 4, found ...". Both refuse; only the message
   differs. The fix is to check line 1's format inside `_entries()` before parsing the rest, which is more than the
   one-line reorder the director allowed into round 6. (codex-school2 round 5, "new (format 4)" PARTIAL)

## PG

3. **A test and a mutant for the trap's walk-failure branch.** covfix_pg.py 549-551 (round 6) handle a W that cannot
   be walked at all inside the failure trap: the run is marked failed (`trap_unreadable: "failed"`) and the scratch
   scan still runs. Round 6's receipted tests do not reach it (line trace 99%). An out-of-tree check on round 6's bytes
   showed the intended behavior (`reads/codex2-r5/REPRO-r5.txt`, last block). The fix is to add that check as a test
   with a mutant, for example one removing the `max(...)` mark, in the next code chain that touches covfix_pg.py. It
   only acts on a run that is already failing. (cov2d, round 6 receipt run, 2026-11-28)
