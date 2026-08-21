# Triage — the 65 open `OI-*` rows against the publication critical path

**Filed 2026-08-21 by the publication close-out lane, at `6b19b2af`. This is a VIEW, not evidence
and not authorization.** It exists because `docs/OPEN_ITEMS.md` presents 65 open rows as one
undifferentiated queue, and a session reading it top-to-bottom works the wrong one. Every
classification below is a recommendation. **No row was edited to produce this file.**

## Method, and what it cannot do

Rows were partitioned by reading each row's own `blocker` cell, not by keyword match on the whole
row. That distinction matters: a naive search for `publication` matches **31** rows, including rows
whose text says they are *not* on the publication critical path, so that signal is worthless as a
classifier and is not used here. Keyword signals were used only to find the PET family, which is
self-identifying (`PET`, `Gate 5`, `Gate 6`, `C_stat`, `C_ML`, `P3F`).

**What this cannot tell you:** whether a row's own claim is still true. Several rows carry dated
measurements; this triage reads what they say, not whether it still holds. A row moved to
"off-path" here is off the path *as it describes itself*.

## Counts

| bucket | rows |
|---|---|
| PET / method-development — off the path by the `OI-126` ruling | 33 |
| Explicitly post-publication or deferred past the freeze, by their own text | 4 |
| Bookkeeping only — id collisions and pointers, no work | 4 |
| Frozen or deferred **by Joseph**, do not re-raise | 2 |
| On the path, or adjacent to it and worth reading | 7 |
| Remainder — code quality and latent defects, not publication-blocking | 15 |

33 of 65 are PET. `OI-126` (2026-08-20) ruled PET diagnostic/method-development, which takes
Gate 5, Gate 6, `C_stat` and `C_ML` off the publication critical path. **Those 33 rows are not
wrong and not closed — they are simply not this queue.** Reading them as live publication work is
the single largest way to waste a session here.

## The seven that are on the path or adjacent

| row | why it is here | shape |
|---|---|---|
| `OI-147` | **The binding constraint.** Seven further keys each set `class_failed`, so the adoption gate cannot pass any product steps 4–5 would create. | Joseph's decision: verify or declare |
| `OI-129` | The projection write path digests `central5d_sha256`, `central4d_sha256`, `M_content_sha256` and `row_index_sha256` but **not the object it produces**. The 3D/4D projections are exactly what gets unquarantined after adoption. | provenance gap on a product that does not exist yet |
| `OI-130` | Advanced 2026-08-21, not closed. Enumeration run: **71 macros; the hard core is 3** — `\sigTwoD`, `\sigTwoDpaper`, `\ratioTot` cite no artifact even generously, so nothing can bind them. Producer extended to attest them. | one cluster run from a receipt |
| `OI-75` | A Standard-P4 stage-3 run exists on the cluster that this repo has no record of, products untracked on purgeable scratch. **Same class as `OI-130`: durability, not correctness.** | needs a preservation decision |
| `OI-148` | Four `OPEN_ITEMS.md` rows are structurally malformed, so any tool reading them by column gets the wrong fields. | needs the four rows' authors |
| `OI-59` | A note-side definitional caveat missing from the Ascencio bin-identical cross-check, and it is the one that lines up with the residual. Note-side, so it can reach a deliverable. | one caveat, needs the ledger's owner |
| `OI-30` | The E_avail truth-definition difference. The charged-pion convention was resolved 2026-08-13; what remains is projecting the adopted covariance onto the E_avail marginal. | **downstream of adoption** — cannot start before it |

## Explicitly post-publication or past-freeze, by their own text

`OI-1` ("Standard C is post-publication and requires CI first"), `OI-42` ("counted but unclassified
until after the publication freeze"), `OI-56` ("FROZEN — do not action"), `OI-63` ("DEFERRED
2026-08-13 by Joseph — do not re-raise before the publication reorganisation"). **These four should
not be picked up by anyone before the freeze, and two of them say so in Joseph's own words.**

## Bookkeeping, not work

`OI-64` ×2 and `OI-65` ×2 are the 2026-08-13 id collisions — two lanes ran `max(existing)+1`
concurrently, which is what the block table now prevents. `OI-80` is a pointer to `OI-122`, not a
second item. **Nothing to do on any of them except not double-count them:** the "65 open rows"
figure includes 4 that are not open work at all, and 2 of the 4 are the same defect counted twice.

## The remainder

15 rows are code-quality or latent-defect items whose own blocker cells describe them as such —
e.g. `OI-10` (writer metadata misleading while the reader is correct), `OI-11` (nine sites
recompute the same POT ratio independently), `OI-12` (a diagonal check latent because the PSD check
subsumes it), `OI-9` (checks testable only in the ROOT environment). **None is publication-blocking
by its own description.** They are real and they are not this queue either.

## `OI-142` IS ALREADY IN FLIGHT — do not start it

Observed 2026-08-21 while writing this file: `lib/resume_guard.sh` is **modified and uncommitted in
the shared checkout** by another session, and the change is exactly the recommended fix —
`rg_is_complete` refuses a marker carrying neither `size` nor `mtime`, with P4 receipts routed to
`nd-unfolding/p4_check_receipt.py` instead. Its own comment adds a better argument than the
recommendation carried: the old exemption was *"a claim about a marker's PROVENANCE authorising a
test over its SHAPE"*, and it enumerates that **no `rg_*` caller in the repo reads that path at all**,
so the branch protected no live caller and was pure attack surface.

**This lane did not touch that file and did not commit it.** Recorded here because two sessions
starting `OI-142` from the same recommendation is the `One authorization, two builders` failure, and
the only thing that prevents it is somebody writing down that a builder already exists.

## What this changes

Nothing, by itself. The intended use is that a session arriving at `OPEN_ITEMS.md` reads this first
and picks from the seven rather than the sixty-five. If a row is mis-bucketed, the row wins and this
file is wrong — it is a view over rows, and the rows are the record.
