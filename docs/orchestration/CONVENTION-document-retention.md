# CONVENTION — document retention: classify in place, never relocate

**Why this exists.** `docs/orchestration/` reached 498 tracked files, of which ~14% were live. Agents
could not tell a live constraint from a concluded campaign record, so they either read everything —
measured at ~82k tokens of standing docs before any work — or missed the live item. The obvious fix,
moving concluded documents into `archive/`, is **not available here**: filenames and paths are cited
from `RUNS.tsv`, run logs, receipt JSON and hash bindings, so a move breaks provenance, and top-level
reorgs are frozen behind `docs/POST_PUBLICATION_REORG_PLAN.md` anyway.

So retention is expressed as **classification**, not as location. Nothing is moved, renamed, or
deleted. See [`BEN-202`](FINDINGS.md) for the failure this is the second half of.

## The rule

**A document's lifecycle state lives in [`MANIFEST-overrides.tsv`](MANIFEST-overrides.tsv), never in
its path and never in its bytes.**

| | |
|---|---|
| Authority on classification | [`MANIFEST.tsv`](MANIFEST.tsv) (generated) |
| Where judgment is recorded | [`MANIFEST-overrides.tsv`](MANIFEST-overrides.tsv) (hand-maintained, 4 columns) |
| Generator | [`generate_manifest.py`](generate_manifest.py) |
| Router agents actually read | [`CATALOG.md`](CATALOG.md) |

`class` is one of `LIVE / ARCHIVAL / MACHINE / DEAD`; `event_status` is one of
`open / terminal / superseded / generated`.

## Two obligations, both at commit time

**1. When an event gets a terminal receipt, flip its document in the same commit.** A predeclaration,
audit, verdict, plan, or runbook whose event has concluded is `ARCHIVAL` **however important its
content was** — importance is not liveness. The commit that records the terminal receipt is the
commit that flips `event_status` to `terminal` (or `superseded`, naming the successor). This is the
same discipline as the existing rule that a campaign's commit carries its ledger and RUN_LOG entries.

**2. When you create a document a session must read, declare it `LIVE` in the same commit.** The
generator's default class is `ARCHIVAL`, deliberately — the bias protects the read path. But it means
**an undeclared live document is invisible to the router**, which is precisely how
`TASK.template.md` ended up live with zero inbound references. Adding the file is not enough; add its
override row.

## What must not be done

- **Do not move, rename, or delete** to express retirement. Paths are provenance.
- **Do not backfill status front matter into receipts, prompts, transcripts, or findings.** Editing
  those bytes falsifies the record. Status lives in the manifest; the artifact stays as written.
- **Do not mark a document `DEAD` while anything still cites it.** `DEAD` means unreachable and
  superseded, not merely finished; `MANIFEST.tsv` carries `inbound_count` so this is checkable.
- **Do not hand-edit `MANIFEST.tsv`.** It is generated. Edit the overrides file and regenerate.

## Enforcement

```bash
python3 docs/orchestration/generate_manifest.py           # regenerate
python3 docs/orchestration/generate_manifest.py --check   # nonzero if stale
```

`--check` is the guard: it fails when the tree and the manifest disagree, which is what catches a
document added without a classification. Run it before committing documentation changes.

**Regenerate on as clean a tree as you can.** The generator classifies tracked files *plus* untracked
files that are not ignored, so that a new document is classified the moment it exists rather than the
moment it lands. The cost is that several sessions share this checkout: a regeneration picks up
whatever untracked scratch other sessions currently have on disk. A `--check` failure after someone
else's work lands is therefore expected and means *regenerate*, not *something is broken*.

## Scope

This convention governs `docs/orchestration/`. `runs/` and `state/` are `MACHINE` without exception
and are never context-loaded wholesale — open one exact receipt when a live document names it.
Sibling conventions: [`CONVENTION-receipt-ingredients.md`](CONVENTION-receipt-ingredients.md).
