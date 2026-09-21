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

`MANIFEST.tsv` inventories Git-tracked files plus nonignored untracked files proposed in the current
change. Its `tracking` column distinguishes `tracked` from `intended`; ignored caches and build
products are excluded. Thus an intended file is reviewable before `git add` but cannot be mistaken
for committed repository inventory.

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

## ⚠ BEFORE A RETENTION PASS: A BASENAME INVENTORY CANNOT SEE AN ELLIPSISED CITATION

Added 2026-09-21, after the first backfill of obligation 1 nearly reclassified a cited document.

The obvious way to find reclassification candidates is "which `LIVE` documents does nothing cite",
by searching the corpus for each basename. **That search is blind to how this repository actually
cites.** Long names are routinely shortened in tables with an ellipsis:

    `EVIDENCE-20260919-…md`        OPERATIVE-SHEET-scalar5d.md, C7 citation table, item 3
    `DECISION-SUPPORT-20260916-…`  and at least eight more families

Measured on 2026-09-21: of 245 `LIVE` `.md` documents, a strict basename search called **52**
uncited. Re-run with a `TYPE-YYYYMMDD` prefix key — and discounting same-prefix siblings, which
would otherwise cite each other by their shared stem — **29 of those 52 turned out to be reachable
by an ellipsised or truncated reference**, leaving 23. Acting on the first number would have
archived cited records, and the failure is silent: the document stays on disk, the citation still
renders, and only the read path degrades.

**The rule, therefore:**

1. Score each candidate twice — by full basename **and** by its `TYPE-YYYYMMDD` stem. Exclude
   same-stem siblings from the second, or a document family reports itself as cited.
2. Reclassify only what fails **both**.
3. Then apply this convention's substantive test — *has the event concluded?* — which the citation
   count does not answer. In the same pass, three of 23 zero-citation documents were kept `LIVE`
   because their events had **not** concluded: a completion report carrying live limitations, a
   checklist that governs a **future** re-verification, and a finding that is a standing caution
   about how to read a field. **Uncited is a safety filter, never the criterion.**

## Enforcement

```bash
python3 docs/orchestration/generate_manifest.py           # regenerate
python3 docs/orchestration/generate_manifest.py --check   # nonzero if stale
```

`--check` is the guard: it fails when the tree and the manifest disagree, which is what catches a
document added without a classification. Run it before committing documentation changes.

The generator classifies tracked files plus untracked files that are not ignored, so that a new
document is classified before it lands. Every such row is visibly `tracking=intended`. Ignored files
never enter the inventory. A `--check` failure after another commit lands means regenerate and review
the path-set difference; it does not authorize silently accepting unrelated inventory changes.

## Scope

This convention governs `docs/orchestration/`, and the generator inventories only that directory.
**Do not add override rows for paths outside it** — they are inert, and they make every run print
`unused_overrides=N`, which is how a warning becomes background noise. Detail files that live
elsewhere are routed by their own parent index instead: `docs/known-issues/ISSUE-*.md` by
`KNOWN_ISSUES.md`, `CLAIM-CLM-*.md` by `CLAIMS.md`. If a directory outside `docs/orchestration/`
ever needs manifest classification, widen the generator's inventory deliberately rather than
adding rows it will not read.

`runs/` and `state/` are `MACHINE` without exception
and are never context-loaded wholesale — open one exact receipt when a live document names it.
Sibling conventions: [`CONVENTION-receipt-ingredients.md`](CONVENTION-receipt-ingredients.md).
