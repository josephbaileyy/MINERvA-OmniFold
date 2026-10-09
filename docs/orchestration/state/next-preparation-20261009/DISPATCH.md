# Next preparation (sessions 1–6), 2026-10-09 — dispatch and writer table

**CITABLE FOR:** the common base commit, the exclusive writer of each surface, the six report paths and
the metadata each report must carry, and the ownership conflicts observed at dispatch.
**NOT CITABLE FOR:** any scientific result, compute authority, review verdict or lane status. Lane status
lives only in each lane's own `REPORT.md`; this file is not updated with progress.

Written by Session 1 (closeout), the single writer of this file. The lane goals, as dispatched, are the
planner's file copied unedited to
[`closeout/GOALS-20261009-as-dispatched.md`](closeout/GOALS-20261009-as-dispatched.md)
(sha256 `81496789b64609d68c934172a4dc50e815c80e7ab742e77fc6582fee7d54380a`, planner mtime
2026-10-09 09:30 PDT). The text pasted into a session governs that session if the two ever differ.
Session 1 spot-checked six distinctive sentences of its own prompt (shared contract, Goal 1 and the
budget table) against the copy, and all six matched.

## Common base

- **Use this commit (the one that adds this file) as the base of every `prep/next-<lane>-20261009`
  branch.** Its parent is `901f0088e23c2394d5ea9cdce7c12d9a2710bb07` (the integrated preparation
  delivery on `prep/uncertainty-e-20261008`), and it changes nothing else in the tree beyond these
  registration surfaces.
- Remote `main` checked 2026-10-09T18:30Z: `460631d1f93c2f0cbaab6ecffdf313121c431751`, an ancestor of
  `901f0088` (0 commits on `origin/main` not in `901f0088`; 41 the other way). There is no upstream delta
  to reconcile at dispatch.
- Frozen reviewed preparation commit: `ee61fb223668252dc571327af7678d40c3d47aee`. The preparation
  branch is **not merged**; merging is Joseph's decision.

## Writer table

`Q` = `docs/orchestration/state/next-preparation-20261009`. Every lane writes `Q/<lane>/` and nothing in
another lane's subtree. A path not listed for a lane is not that lane's to write.

| Session | Branch | Report | Exclusive writes beyond its own `Q/<lane>/` |
|---|---|---|---|
| 1 closeout | `prep/next-closeout-20261009` | `Q/closeout/REPORT.md` | `Q/DISPATCH.md` (this file); `docs/orchestration/CATALOG.md`; `docs/orchestration/MANIFEST-overrides.tsv`; generated `docs/orchestration/MANIFEST.tsv`; the closeout corrections only, in `DELIVERY-20261008-uncertainty-preparation.md`, `ASSESSMENT-20261008-2d-estimator-pairing.md`, `DESIGN-20261008-2d-independent-statistical-validation.md` and `ASSESSMENT-20261008-2d-total-uncertainty-feasibility.md` (all in `docs/orchestration/`) |
| 2 guard | `prep/next-guard-20261009` | `Q/guard/REPORT.md` | `2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py`; `2d-unfolding/uq/coverage_fixed_truth/ki85_compare.py`; their directly relevant test `2d-unfolding/uq/coverage_fixed_truth/test_coverage_fixed_truth.py`; new subtree `2d-unfolding/uq/coverage_fixed_truth/n2/`; narrowly justified classification/inventory changes to `nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py` and `nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py` |
| 3 structure | `prep/next-structure-20261009` | `Q/structure/REPORT.md` | `README.md`; `docs/POST_PUBLICATION_REORG_PLAN.md`; `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`; at most two consolidation families and six existing non-frozen implementation files, plus small relevant tests, **each named in `Q/structure/REPORT.md` with its caller analysis in a pushed commit before the file is edited** |
| 4 speed | `prep/next-speed-20261009` | `Q/speed/REPORT.md` | none (prototypes and benchmarks inside `Q/speed/`) |
| 5 gbdt | `prep/next-gbdt-20261009` | `Q/gbdt/REPORT.md` | none (reductions and the proposal inside `Q/gbdt/`) |
| 6 pet | `prep/next-pet-20261009` | `Q/pet/REPORT.md` | none (reductions and the proposal inside `Q/pet/`) |

**Claimed by no lane in this dispatch.** A lane that needs a change here puts the exact proposed text in
its own report; it does not edit the file.

- The guard core `nd-unfolding/mnv_guarded_run.py` and the probe
  `docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py`. Session 2 may *propose* a change in
  `Q/guard/REPORT.md`; Session 3 may not claim either.
- The seven historical scripts Goal 2 names (under `state/ki84-adopt-20261006/`,
  `state/ki84-rebuild-20261006/`, `state/note-boot-20261003/` and `state/uqpaper-median-20261006/`):
  read-only, byte-for-byte.
- The 2D production driver, the pinned `unbinned_unfolding/python/omnifold.py`, every receipt-bound
  script, `verify_hash_bindings.py` and its constants, and every scanner's historical receipt.
- Shared registers: `KNOWN_ISSUES.md`, `docs/OPEN_ITEMS.md`, `VALIDATION_LEDGER.md`,
  `docs/orchestration/control-plane/` and the generated `docs/CURRENT_WORK.md`.
- Publication surfaces: `docs/analysis-note/`, `docs/publication/`, `publication/` and the standalone
  note repository stay with their existing owner (see conflicts below).
- New documents under `docs/orchestration/` outside `Q/`. None is planned; a lane needing one asks in its
  report instead of creating it, because a new document needs an overrides row and a router entry.

## Report paths and required metadata

The six report paths are pre-registered in `MANIFEST-overrides.tsv` as `MACHINE open` (an authored
record under `state/`, editable by its owner, not an immutable generated receipt) and routed from
`CATALOG.md` § Current work. Each is absent until its lane pushes it.

- `Q/closeout/REPORT.md`
- `Q/guard/REPORT.md`
- `Q/structure/REPORT.md`
- `Q/speed/REPORT.md`
- `Q/gbdt/REPORT.md`
- `Q/pet/REPORT.md`

Every `REPORT.md` opens with a header block carrying these fields, in this order:

| field | content |
|---|---|
| `Lane` | session number and lane name |
| `Decision` | the goal's decision sentence, verbatim |
| `Branch` / `Base` / `Head` | branch name, this dispatch commit, the head the report describes |
| `Owned files` | every path the lane wrote, exactly |
| `Pinned inputs` | each input with its commit or digest |
| `Resources` | measured elapsed time, local CPU core-hours, scratch bytes, tracked bytes added; cluster/GPU must read 0 |
| `Review` | reviewer, fixed commit reviewed, findings and dispositions; or `INCONCLUSIVE — independent review unavailable` |
| `Model / effort` | only what is observable; otherwise `not observable` |
| `Disposition` | `PASS`, `FAIL` or `INCONCLUSIVE`, one per decision, each with its reason |
| `Next action` | the exact next decision, its inputs and its cost |

The body then gives commands, results, limitations and the full next-action specification. Machine-
readable operands and results sit beside the report in `Q/<lane>/`. Keep tracked evidence under the
lane's 10 MiB cap.

## Ownership observed at dispatch (2026-10-09T18:30Z)

Measured from `git worktree list`, `git status --porcelain` in each worktree, and every local and
`origin` branch with commits not in `901f0088` (`git diff --name-only` from its merge base). An old branch
was not treated as live ownership.

- **No `prep/next-*` branch existed** locally or on `origin`, and no worktree held a `Q/` path.
- **`preserve/anatuple-data-cfs-20261009`** (pushed, 1 commit, 2026-10-09T02:57 PDT, clean worktree
  `MINERvA-OmniFold-anatuple-data-20261009`) is the live publication-preservation writer. It touches
  `docs/publication/corrections-20261008/`, `publication/release/preservation/` and the generated
  `docs/orchestration/MANIFEST.tsv`. Its publication paths are **excluded** from all six lanes. The
  manifest is the one overlap: it is generated, so whichever branch merges second regenerates it from
  source with `generate_manifest.py`; nobody hand-merges it.
- The publication worktrees (`prd-audit`, `prd-editorial`, `prd-fix`, `prd-followup`, `prd-paper`,
  `prd-review`, `/private/tmp/minerva-abstract-20261008`) were all clean, with no commits outside
  `901f0088`. Publication ownership is unchanged and stays with its existing owner.
- The A–D preparation worktrees (`uncprep-a` … `uncprep-d`) and `uncertainty-planner-20261008` were
  clean and their branches contained in `901f0088`, so they hold no live claim. Their lanes' repair
  allowances are spent; Session 1's correction of their text is the separate, narrowly scoped
  authority in Goal 1.
- Older branches ahead of `901f0088` that touch a dispatched surface — the 2026-09-23
  `worktree-agent-*` branches (`CATALOG.md`, `MANIFEST-overrides.tsv`, `2D_OMNIFOLD_REFERENCE.md`, note
  sources) and `docs/scalar-measurement-successor-20261005` (`CATALOG.md`, `MANIFEST-overrides.tsv`;
  the local-only draft `eeeaad78`) — have no worktree, and none has been touched since 2026-10-05.
  They are not live claims and are not excluded.
- The primary checkout `MINERvA-OmniFold/` had eleven untracked root files belonging to other
  sessions. They are left untouched.

## Coordination rules

- A lane learns about another lane only through that lane's pushed report. Do not edit another lane's
  subtree or branch, and do not wait on another lane except where the goals' dependency column says so.
- No lane touches `CATALOG.md`, `MANIFEST-overrides.tsv` or `MANIFEST.tsv`. Session 1 regenerates the
  manifest from source at its own closeout.
- At most three CPU- or data-heavy commands run at once across all six sessions on this laptop
  (six compute threads, 24 GiB RAM combined). If a lane cannot see the others' load, it runs its heavy
  steps one at a time.
