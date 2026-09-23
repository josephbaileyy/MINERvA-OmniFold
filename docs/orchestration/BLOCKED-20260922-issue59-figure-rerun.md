# BLOCKED 2026-09-22 — ISSUE-59's figure re-run is NOT executed: it is PET work, and PET is a hard limit

**CITABLE FOR:** why this lane did not re-run the PET point-cloud projection figure, and what it
measured instead.
**NOT CITABLE FOR:** any claim that ISSUE-59 is resolved, or that the figure has been regenerated.
**ISSUE-59 remains OPEN and MEDIUM, exactly as `KNOWN_ISSUES.md` row 59 states.**

## 1. The conflict, stated exactly

This session's work order contains two clauses that point opposite ways on the same item, both from
Joseph, both 2026-09-22:

- **D6** — *"3D COVARIANCE PROJECTION from the adopted trunk (handoff §9.2), **and ISSUE-59's figure
  re-run (§9.4)**. Both authorized, compute included."*
- **D7** — *"HARD LIMITS — these are NOT stalls, they are terminal outcomes. If an item turns out to
  require any of the following, write the finding to `docs/orchestration/BLOCKED-20260922-<item>.md`
  with its measurements, and move on to the next item: … **PET work of any kind (out of scope per
  handoff §0)**."*

ISSUE-59's re-run executes `nd-unfolding/pet/pointcloud_projection.py`. That is PET work on its
face, so D7's enumerated limit is engaged by the very item D6 names.

## 2. Why the limit governs — three independent sources agree with D7, and one is Joseph's own words

1. **`HANDOFF-20260922` §0**, quoting Joseph verbatim, 2026-09-21: *"The pending jobs are for PET. I
   don't want to focus on it and just want to focus on finishing GBDT."*
2. **§9.4 warns about itself**: *"⚠ **This is PET-adjacent; §0 applies.**"*
3. **§11** lists ISSUE-59 under *"NOT GBDT — listed only so you do not adopt them"*, with
   *"**PET-adjacent; out of scope per §0.**"*

D6 is a general authorization naming the item; D7 is an explicit **hard limit** with a prescribed
terminal branch, written in the same instruction and labelled as governing. Where one clause of an
authorization enumerates a prohibition and another grants the item generally, the enumerated
prohibition is the narrower and later-controlling statement, and it is also the **reversible**
choice under **D8**: not running a job is undoable; regenerating a committed figure asset and
re-syncing the standalone note repository is not.

**So this is recorded as a terminal outcome under D7 and the lane moved on, which is what D7
instructs. It is not a stall and it is not a request for further instruction.**

## 3. What was measured anyway, read-only, because it costs nothing and the record should be current

Every claim `KNOWN_ISSUES` row 59 makes that can be checked from the repository was checked at
`origin/main = 384c2eb1`. **All of it holds.**

| row-59 claim | measured |
|---|---|
| `figures/pet_cloud_projection_xsec.pdf` last written at `6749ddf8` (2026-07-05) | ✅ `git log -- <path>` returns exactly one commit, `6749ddf8`, 2026-07-05 |
| the re-run entry is in `make_figures.sh` with the three `PCPROJ_*` full-cloud inputs | ✅ present at `make_figures.sh:78-83`, setting `of_inputs_pc_fullcloud.npz`, `pet_weights_fullcloud.npz`, `runEventLoopOmniFold_PC_MEFHC_fullcloud.root` |
| inputs live only on `/pscratch`, so it cannot be rebuilt locally | ✅ **all three re-measured 2026-09-22 against the files themselves.** All three are absent from the local checkout and present on the cluster: `of_inputs_pc_fullcloud.npz` **6,558,953,264 B** and `runEventLoopOmniFold_PC_MEFHC_fullcloud.root` **51,464,282,286 B** under `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/`, and `pet_weights_fullcloud.npz` **174,365,198 B** under `…/nd-unfolding/products/pet/`. ~58 GB in total, so a local rebuild is out on size alone. ⚠⚠ **THIS CELL BRIEFLY PUBLISHED A FALSE NEGATIVE.** It claimed *"`pet_weights_fullcloud.npz` is **NOT at that path**… so *all three* is **not** established — two are"*, and attributed the gap to a scope limit (*"PET work is out of scope for this lane"*). **The file was there the whole time.** I looked under `nd-unfolding/`, where the other two live, while `nd-unfolding/pet/sbatch_project_fullcloud.sh` sets `PCPROJ_WEIGHTS="${REPO}/nd-unfolding/products/pet/pet_weights_fullcloud.npz"` — the real path, named by the script the row **immediately above** quotes. A wrong operand, dressed as a scope boundary, and **withdrawing a claim that was fully established**. It is the only defect this session that reached a committed record without being caught by reading the source first. ⚠ This cell previously also read *"all three `PCPROJ_*` paths are under `$REPO/nd-unfolding/…` gitignored product trees"*, which does **not test the row**: the paths are ignored by the suffix rules `*.npz`/`*.root`, and *gitignored* does not establish *only on `/pscratch`*. |
| *"Also noticed and not fixed here: `make_figures.sh`'s PET comment cites `KNOWN_ISSUES #18`, and no row `18` exists"* | ✅ cited at **`make_figures.sh:59`**; index rows run `5`–`11`, `16`, `17`, `19`–`21`, **`23`–`60` at `384c2eb1`** (and `23`–`62` at `9e78a8cf`, after rows 61-62 were added later the same day). Absent at both: `12`–`15`, **`18`**, `22` |

### 3a. ⚠ The dangling `#18` is not a typo — the row was RESOLVED and then deleted

Traced rather than guessed. Row `18` read:

> `| 18 | **pet_event_displays.png / pet_cardinality*.png had no generating script** — ad-hoc
> products (absent from make_figures.sh) … RESOLVED 2026-07-10: nd-unfolding/pet/plot_event_disp…`

which is **exactly** what the citing comment at `make_figures.sh:59` is about. It survived until
`d2ca8ed1` and was dropped at `1f714b7f` — *"KNOWN_ISSUES.md finally obeys its own line 3: 113 KB of
index-plus-copy becomes an 8.7 KB index"* — i.e. removed as **resolved**, in a compaction that did
not sweep inbound citations.

**The citation was correct when written.** It is stale because a resolved row was deleted, not
because anyone mis-numbered it. **Not repaired here**: `make_figures.sh` lives under
`docs/analysis-note/`, and a change there is incomplete until the standalone
`MINERvA-OmniFold-Analysis-Note` repository is synchronised (`AGENTS.md`, *Deliverable
synchronization*) — a note-side action this record's own reasoning keeps out of a PET-blocked item.
Recorded so the next reader stops hunting for row 18.

## 4. What a future lane needs, and what it must NOT do

- **The exact command is already written down** — `HANDOFF-20260922` §9.4 and `KNOWN_ISSUES` row 59
  both carry it. Nothing has to be reconstructed.
- ⚠ **Do NOT run it with the defaults.** Both sources warn that the default `of_inputs_pc.npz` is
  the **pre-fix diagnostic input**, so a defaulted run would reproduce the defect and look like a
  fix.
- After regenerating, **sync the `.pdf` twin and restore the plain caption** — the caption and body
  of `sec_pet.tex` currently state that the asset is the pre-fix *"before"* state, and that
  disclosure must come out in the same change that makes it false.
- ⚠ **Do not "fix" the adjacent `27.395%` / `37.885%` discrepancy by substitution.** Row 59 records
  it as real and unexplained: the pre-fix `empty_cloud` fraction is `27.395%`, **not** the
  `37.885%` `truth_only_miss` fraction `sec_pet.tex`'s prose implies. They are different quantities.

## 5. What this record does NOT do

- It does **not** resolve ISSUE-59, and does not change its severity.
- It does **not** assert that D6 was wrong — only that D7's enumerated limit governs the overlap,
  and that the reversible reading was taken under D8.
- It touches **no** PET product, launches **no** PET job, and reads **nothing** on `/pscratch`
  belonging to the live PET session.

**Co-Authored-By: Claude Opus 5 (1M context)**
