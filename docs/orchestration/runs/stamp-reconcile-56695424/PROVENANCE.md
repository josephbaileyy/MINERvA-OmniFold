# `stamp-reconcile-56695424` — surviving artifacts

## ⚠ NOT CITABLE: `ben106-stamp-verify-complete-56695424.SUPERSEDED-DRAFT-NOT-CITABLE.json`

**This file is a superseded draft. Do not cite it, quote it, or treat it as a receipt.**

**The authoritative record is `docs/orchestration/state/ben106-stamp-verify-complete-56695424.json`.**

| | this draft | the authoritative file |
|---|---|---|
| `recorded_at_utc` | `2026-08-12T00:39:00Z` | `2026-08-12T00:43:07Z` |
| bytes | 3669 | 3274 |
| key names | `receipt_type: terminal-reconciliation`, `event_type`, `observed_at_utc`, `event_sha256` | `receipt_type: slurm-terminal-reconciliation`, `type`, `observed_at`, `sha256`, plus a `path` field |

**Why this needs a warning at all, and why the filename was changed.** Both files carry the
**same `event_sha256`** (`d63d1697…`) and both are internally consistent, so a reader searching
for that sha finds two artifacts that each satisfy the description "the BEN-106 stamp-verify
receipt" — and the wrong one may answer first. That is a conflated name silently double-counting
a single guarantee. A warning in prose is a *check*; renaming the file makes the confusion
**unreachable by filename search**, which is the stronger remedy. Its original name inside the
archive was `ben106-stamp-verify-complete-56695424.json`, recorded here because the original name
is itself provenance.

It is kept only because its bytes are in no commit (see the admission test in
`../retired-worktree-archive-20260824/PROVENANCE.md`), not because it has standing.

## `uncommitted-tracked.diff` — citable

38,422 bytes, md5 `1c8c7fe435a591bd851a69b792009070`. **Uncommitted tracked modifications**, which
by definition cannot be in git — the only non-empty one of the seven archived worktrees. This is
a genuine record of working state at `f139964f`, and is the most substantive single artifact
recovered from the archive.
