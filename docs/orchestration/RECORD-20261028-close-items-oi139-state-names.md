# RECORD — OI-139: what an `active` in a state/ filename means, a forward guard, and the key side closed (2026-10-28)

The close-items session owns `OI-139` (promoted from the director's standing list). The director
ruled on 2026-10-28 to do all three parts, in one PR, and then retire the item.

## (a) The fourteen `active`-named receipts, as measured

Measured read-only on `login37` at 2026-10-29T06:30:21Z (2026-10-28 PDT). The query reads every
`sacct` task row per job, not `-X | head -1`, plus `squeue --me` (empty), as OI-139's design
constraint requires. Every query returned rows.

| Receipt (`docs/orchestration/state/`) | Job | State of every task |
|---|---|---|
| `ben106-stamp-verify-active-56695424.json` | 56695424 | COMPLETED 1/1 |
| `gate5-do-train-array-active-57266000.json` | 57266000 | **FAILED** 1/1 |
| `gate5-extraction-active-56935552.json` | 56935552 | **CANCELLED 2, FAILED 1** |
| `gate5-extraction-r2-active-56936015.json` | 56936015 | COMPLETED 50/50 |
| `gate5-extraction-r2-manifest-active-56936016.json` | 56936016 | COMPLETED 1/1 |
| `gate6-floor-replication-active-56863958.json` | 56863958 | COMPLETED 4/4 |
| `gate6-trajectory-array-active-56847059.json` | 56847059 | COMPLETED 5/5 |
| `k0r2-bootstrap-array-active-57527866.json` | 57527866 | COMPLETED 100/100 |
| `k0r2-seedscan-array-active-57527869.json` | 57527869 | COMPLETED 24/24 |
| `k0r2-detector-array-active-57527870.json` | 57527870 | COMPLETED 19/19 |
| `k0r2-uthrow-run-array-active-57527872.json` | 57527872 | COMPLETED 40/40 |
| `k0r2-uthrow-block-array-active-57527873.json` | 57527873 | COMPLETED 21/21 |
| `k0r2-sweep-array-active-57527874.json` | 57527874 | COMPLETED 169/169 |
| `k0r2-combine-job-active-57527875.json` | 57527875 | COMPLETED 1/1 |

**None of the fourteen is active.** The names stay, because paths are provenance and
`CONVENTION-document-retention.md` forbids renaming. `CATALOG.md` ("Evidence and claims") now says
how to read such a name.

## (b) The forward guard

`docs/orchestration/state_receipt_names.py` judges a `.json` file a change **adds** under
`docs/orchestration/state/` whose name has a token `active`, `live` or `armed` (split on `-`, `_` and
`.`, so `deliverable` and `inactive` do not match). Such a file must hold a non-empty top-level
`recorded_at_utc`. The hook runs `--check` on the staged index, CI runs `--base` against the merge
base, and both run `--self-test`.

**Two directions**, from `--self-test` in a throwaway repository, 8/8 passing:
- **Fires** on a new state-named file with no timestamp; on one whose timestamp is blank; and in CI
  mode on a bad addition.
- **Silent** on an untouched existing file; on a modified existing file; on the same new file once
  it carries `recorded_at_utc`; on `deliverable-3.json`, `inactive-lanes.json` and
  `relive_notes.json`; and in CI mode on a clean branch.

**It re-judges no existing file.** `--existing` lists 18 tracked state files whose names match and
judges none of them: the 14 above, the three `live-state*` files (the dashboard's own, where "live"
names the file), and `preflight-20260906-r5/r5-meter-receipt-INCOMPLETE-live.json`. On this branch,
`--check` and `--base origin/main` each judge 0 added state files.

**Friction, measured.** None of the 575 state JSON files added since 2026-09-28 has a state word in
its name, so over the past month the guard would have refused nothing. A new file in the
`live-state` family would need a timestamp, which is a small cost and is disclosed rather than
exempted.

## (c) The key side — closed, not a defect class here

Of the 575 state JSON files added 2026-09-28..10-28, 59 have keys containing `verified`, `live`,
`active`, `complete`, `current` or `armed`. Only 1 of those 59 carries a timestamp key. The commonest
keys are `verified_before_first_read` (13), `n_active_on_entry` (13), `active` (11),
`sig_reco_rel_shift_active` (10), `current` (7), `complete` (7) and `complete_set` (3). In this
repository `active` mostly names **active-universe laterals**, a physics term, `complete` names a
complete population, and `current_sha256` is a digest. A key lint requiring a timestamp would have
refused about 58 files in a month, almost all for vocabulary. The originating error (quoting
`supervision.armed_watch` as live) is a reading discipline. Remedy (2), the dashboard printing the
MEASURED scheduler state, already covers every job that is watched.

## OI-139 — retired; OI-151 promoted

All three parts are done, so OI-139 is retired. Its dependency check (KNOWN_ISSUES and the DECISION,
RULING, AUTHORIZATION, OPERATIVE and `docs/publication/` records) returns 0 hits. OI-151, the
fourth and last item on the director's standing list, is promoted to keep the queue at
`current_work_min` = 10. The standing list is now used up.
