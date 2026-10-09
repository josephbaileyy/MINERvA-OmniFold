# 2D OmniFold run log

The complete pre-compaction chronology is frozen at
`evidence/prepublication-2026-08-20-0b329e8a` under this exact path:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:2d-unfolding/2D_OMNIFOLD_RUN_LOG.md
```

Read `2D_OMNIFOLD_STUDY_STATUS.md` for current state, `2D_OMNIFOLD_REFERENCE.md` for durable
contracts, and `VALIDATION_LEDGER.md` for verified numbers. Pre-freeze history must be cited by tag
and old path.

## Post-freeze chronology

Append only committed post-2026-08-20 events here; keep the current-state summary in STATUS.

### 2026-10-09 — uncertainty preparation (sessions A–E): driver provenance records; no product changed

- **Code.** `unfold_2d_omnifold_unbinned.py` now writes, into every output, `runConfig` (every
  effective argument, defaults included), `runArgv`, the driver's path and sha256, and the path and
  sha256 of the OmniFold helper module actually imported (lane A behavior commit `971fc00c`, with six
  new tests in `tests/test_bootstrap_completeness_ki84.py`). No histogram, weight or estimator changes;
  the rooted insert stays inside `main()` and `omnifold.py` keeps its digest. Existing products do not
  gain the records. Only future runs write them.
- **Findings recorded, not acted on.** The quoted central product `142a45b0…` is exact-split GBT
  with an unpinned seed; every uncertainty block is LightGBM, and the transfer is unmeasured
  (`KNOWN_ISSUES.md` 88). STATUS's headline label, lateral-band list and PPFX qualifier were
  corrected the same day.
- **Compute.** None: zero node-hours, no training, no toys, no product rebuilt.
- **Route.** [`DELIVERY-20261008-uncertainty-preparation.md`](../docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md).
