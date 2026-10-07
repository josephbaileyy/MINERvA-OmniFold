# Active-tree compaction and post-publication reorganization

Two different operations share this plan. Do not infer publication completion from active-tree
compaction.

## Evidence boundary now in force

The complete committed pre-compaction tree is frozen at:

`evidence/prepublication-2026-08-20-0b329e8a`

That pushed annotated tag points to `0b329e8ae8482e6334a68faf947fc80ae7265ac9`. A full-tree inventory,
all-ref bundle, ref/worktree/job snapshots, cited-commit reachability report, and fresh-clone recovery
proofs are stored outside the repository at both:

- local: `/Users/josephbailey/local-research/evidence-epochs/prepublication-2026-08-20-0b329e8a/`
- NERSC: `/global/homes/j/josephrb/evidence/repository-epochs/prepublication-2026-08-20-0b329e8a/`

The bundle SHA-256 is `9d4c6806f97781c1da27a45337ad5429c05c43f48346174e41a17b30afa80dc2`.
This is an evidence epoch, not a publication-results tag and not scientific adoption.

## Lane A — active-tree compaction, authorized now

`main` may retain current science, supported reproduction, publication source, active tests, exact
live receipts, compact canonical records, and a searchable historical router. Complete pre-freeze
chronology and terminal campaign machinery may live only at the evidence tag when every removal
family passes the following gate:

1. Enumerate exact paths; do not act on an unresolved glob.
2. Confirm no dirty worktree, live writer, queued job, runtime reader, test, import, hash pin, or
   publication build depends on those paths in `main`.
3. Separate references internal to the removed family from references in surviving files.
4. Prove every path exists at the pushed evidence tag and restore a representative sample with a
   matching digest.
5. Make each surviving reference resolve locally or name the evidence tag and historical path.
6. Keep a compact old-path/identifier discovery route.
7. Run affected lint, tests, dry runs, and all three publication builds from a clean checkout.
8. Verify scientific products and build outputs are unchanged when the family can affect them.
9. Obtain read-only independent review of the family-scoped diff.
10. Record before/after tracked-file, Markdown-file, and Markdown-line counts.

Pre-freeze RUN_LOG text may be replaced at its canonical path by an evidence-tag pointer, final-summary
route, and post-freeze chronology. A cited pre-freeze script may leave `main` under the same gate; its
tag and old path become the citation. Do not leave path-shaped prose that silently resolves to a
different current file.

Compaction commits contain no physics-method change, product promotion, compute launch, history
rewrite, or unrelated refactor. The evidence tag and external bundle are immutable inputs, not targets.

## Protected active surface

Retain unless an exact later review proves otherwise:

- `AGENTS.md`, `CLAUDE.md`, current generated queue/playbook sources and guards;
- `VALIDATION_LEDGER.md`, active `KNOWN_ISSUES.md`, `docs/OPEN_ITEMS.md`, and current claims;
- supported 2D, 3D, scalar N-D, PET, FPS, and standard-P4 source/launch/test paths;
- `docs/analysis-note/` source and build-critical inputs;
- current STATUS files and compact canonical RUN_LOG paths;
- exact receipts read by retained code or governing a live gate;
- cluster-frozen worktrees and outputs used by live job `57266000_0`.

*Superseded 2026-10-07 (see* Lane A closure and A2 *below): the job clause is stale
(`orchestration/LIVE-STATE.md:34` records `57266000_[0-0]` FAILED), and the release surfaces are added.*

The live job executes from `/pscratch/sd/j/josephrb/gate5-data-only-frozen-377c713`; compaction of local
`main` must never rewrite or delete that frozen worktree or its `gate5-do-g2` outputs.

## Lane B — publication-results freeze, later

Create `publication-results-YYYY-MM-DD` only after publication blockers close, required product
summaries and canonical records land, ignored heavy artifacts are fingerprinted and preserved, supported
reproduction passes, and note/primer/paper build from a clean checkout. If science changes after a
candidate tag, review and replace the tag; never relabel this prepublication evidence epoch as final.

## Lane C — layout moves, only after publication freeze

Directory moves and abstractions remain post-publication work. Move one coherent family per commit,
update callers and references together, retain compatibility wrappers for external entry points, and
run family fixtures plus all three document builds. PET and FPS move last. Do not build a universal
dimensional driver or combine distinct masks, resources, defaults, and provenance behind implicit flags.

## Completion criteria

Active-tree compaction is complete only when:

- the tree has at most 950 tracked files, 200 Markdown files, and 45,000 Markdown lines, or a failed
  removal gate demonstrates why the target cannot safely be reached;
  *(numeric targets retired 2026-10-07 under the failed-gate clause; see* Lane A closure and A2 *below)*
- every historical lookup resolves through the evidence tag and old path;
- no supported runtime, test, publication input, or active gate loses a dependency;
- a fresh clone passes the repository checks and all three publication builds;
- independent reviewers approve every removal family;
- the final counts and recovery commands are recorded without promoting a scientific result.

## Compaction outcome — 2026-08-20

The evidence boundary and seven reviewed removal families reduced the active tree from 2,481 tracked
files, 640 Markdown files, and 126,234 Markdown lines to **1,446 tracked files, 197 Markdown files,
and **43,427 Markdown lines**. The Markdown gates are met *(no longer true as of 2026-10-07; see*
Lane A closure and A2 *below)*. The 950-file gate is not met, and
the failed-removal evidence below is the completion condition allowed by this plan; the count was
not forced by weakening an active gate.

- The current orchestration surface has 319 files: 199 machine/guard artifacts, 32 live records,
  87 archival records with surviving consumers, and one dead compatibility path. The exact live
  receipt inventory remains 117 path/hash bindings at digest
  `7586d636e6c4cde2af89e075d12d02633d21acc6709f796417ba25c37d5eec0c` *(superseded 2026-10-07: 144
  bindings at `f9dab8dd…`; see* Lane A closure and A2 *below)*.
- The old launcher survey named 64 root N-D launchers unreferenced as of 2026-08-12. A current audit
  found 17 had since acquired tests, policies, status routes, or current scientific consumers; those
  stayed. The independently reviewed 47-path remainder moved to the evidence tag.
- The remaining N-D tree has 734 files, including 89 test/fixture files and 141 flat-root shell
  launchers. Exact consumer scans of the remaining archival Markdown and orchestration state
  surfaces found active open-item, receipt, code, test, or quarantine dependencies on nearly every
  further candidate. Shallow absence of a caller was not treated as proof that a standalone
  scientific CLI was unsupported.
- Reaching 950 would require at least 496 additional deletions. The remaining conservative
  no-consumer scans are orders of magnitude smaller than that and include active standalone
  diagnostics when inspected by name. Therefore another size-driven family would require changing
  the supported reproduction surface, deleting current evidence, or weakening guards—none is
  authorized by Lane A.

Historical recovery remains:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:<old-path>
git grep '<identifier>' evidence/prepublication-2026-08-20-0b329e8a --
```

This outcome is active-tree hygiene only. It creates no publication-results freeze and promotes no
scientific result.

## Lane A closure and A2, 2026-10-07

**Decision (Joseph, 2026-10-07 UTC, verbatim):** "Close Lane A + do A2 (Recommended)". That option's text, as
answered, was: "Record the target-unreachable completion, fix the plan's stale clauses, and remove the 27
archival records (A2). They are already preserved under the 09-24 snapshot tag. Full checks and
independent review. Then the paper pass." This admits the second epoch as A2's removal boundary.

**Evidence epochs.** Two pushed epochs now exist. `evidence/prepublication-2026-08-20-0b329e8a`, above,
is one. The other is **`evidence/preparation-2026-09-24-bf34a12c`**: tag object `6bb0af34…`, commit
`bf34a12cff9a2f06f0a3f1c516628085565eef60`. Its bundle and recovery proofs are in
[`orchestration/RECOVERY-MANIFEST-20260924-preparation-epoch.md`](orchestration/RECOVERY-MANIFEST-20260924-preparation-epoch.md).
Only Joseph's 2026-09-24 authorization admitted it as a removal boundary, for the families reviewed
then, and his 2026-10-07 decision does the same for A2. Any further family needs its own owner
authorization, as does any material that neither epoch contains.

**Family A2: 25 ARCHIVAL/terminal `docs/orchestration` records.** The read-only reassessment at
`381dc8b7` proposed 27 records. Two left the family because surviving records cite them by short
identifier:
- `CHECK-20260911-…` at `CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md:189`;
- `COSTMODEL-20260911-…` at `HANDOFF-20260921-gbdt-remaining.md:199`.

The producer ran the gate at `0a95bf87`. After the branch was rebased onto `6800a754` (PRs #37 and #5),
the independent reviewer re-ran steps 1–8 and 10 on the rebased head. The results were identical, except
for the counts in step 10:

1. **Enumeration.** The list is exact. Each path is named in the 25-row discovery table in
   [`orchestration/CATALOG.md`](orchestration/CATALOG.md), *Lane A family A2*.
2. **Dependency scan.** `git grep -a` over every tracked file at `0a95bf87` (9,206 files) searched for
   each full stem, each type-date prefix and distinctive fragments. Surviving references appear only in:
   `MANIFEST.tsv` and `MANIFEST-overrides.tsv`; `CATALOG-ARCHIVE-scalar5d.md` (17 link rows); and the
   historical `docs/sep-09-presentation/…/commit_inventory.json`, a measurement output frozen at revision
   `901f2c64` whose digest no tracked file pins. No file is a hash-pin source or target. No path is read by
   code, a test or a publication build. The reviewer re-scanned all 9,205 files at the rebased head,
   including PRs #37 and #5, and found no live reference. It also found that none of the 43 local
   worktrees has a dirty edit to these paths or an untracked file citing them. The 4 queued cluster jobs run
   from a separate checkout and read a different record.
3. **Internal references.** One family member cites another (`VERDICT-20260820-lanec-remedy-a-FAIL.md:15`, now at
   `evidence/preparation-2026-09-24-bf34a12c`).
4. **Present at the tags.** 21 paths are byte-identical at `bf34a12c` and 4 at `0b329e8a`, checked with
   `git rev-parse <tag>:<path>` against the head blob. All 25 were restored with `git show` and matched
   by sha256.
5. **Surviving references resolve.** The 17 `CATALOG-ARCHIVE-scalar5d.md` rows now read
   `` `git show <tag>:<path>` `` instead of a relative link. Override rows were removed and `MANIFEST.tsv`
   regenerated. `commit_inventory.json` is a frozen historical inventory and stays as it was.
6. **Discovery route.** The 25-row path→tag table in `CATALOG.md`.
7. **Checks.** Pre-commit (13 checks), `generate_manifest.py --check`, `verify_hash_bindings.py`,
   `control_plane_lint.py`, `live_doc_indexed.py --check --unrowed`, and the withdrawal-completeness
   check with its self-test all pass. On main, `generate_manifest.py --check` was already OUT OF DATE
   before the change.
   - The `docs/orchestration` tests plus `test_hash_bindings.py` show the same pass/fail set before
     and after: 981 passed and 23 failed, with an identical failure set. The failures are environment-bound tests (`test_wakerctl`,
     `test_watch_slurm_array_resume`, `test_usagectl`, `test_deploy_oi135_watcher_swap`) that also fail
     on main.
   - `probe-20260922-seven-gates.sh` refuses outside the main checkout ("not on main"), so it was not
     run.
8. **Products unchanged.** `build_all.sh` was run from clean checkouts of `0a95bf87` and of the
   removal commit. Both give PASS (containment strict; 0 of 29 struck literals) at 123 / 9 / 9 pages.
   The `docs/analysis-note` source trees are identical, and the `pdftotext` digests of all three PDFs
   match.
9. **Independent review.** A fresh read-only reviewer examined the family-scoped diff on the rebased head
   (`5d3f4e32`). Verdict: **APPROVE WITH CHANGES**. It found nothing blocking and six should-fix items,
   all about the accuracy and scoping of this section; they were applied before the merge. The removal
   family itself passed every gate step.
10. **Counts.**

| | tracked files | Markdown files | Markdown lines |
|---|---:|---:|---:|
| before A2, producer's run (`0a95bf87`) | 9,206 | 824 | 206,497 |
| before A2, rebased base (`6800a754`) | 9,230 | 828 | 207,468 |
| after A2 (removal commit on `6800a754`) | 9,205 | 803 | 202,790 |

The removal is −25 files, −25 Markdown files and −4,678 Markdown lines on either base. This section adds
about 100 lines.

**Lane A completion: the targets cannot be reached safely.** This follows the completion clause above:
"or a failed removal gate demonstrates why the target cannot safely be reached".
- The read-only reassessment (`381dc8b7`) found the gate-passing families total about 1% of the tree.
  A2 is one of them. The other, `nd-unfolding/pet/runtime_runs` (48 files), sits at no epoch and needs a
  new one.
- The PET study trees and all campaign state, s5p included, are read by code, tests, hash pins,
  `reproduction/s5p` or the release candidates. They therefore fail step 2.
- LIVE/open orchestration records alone total 297 Markdown files and 89,379 lines at `381dc8b7`
  (307 and 91,992 at the rebased head).
- The realistic floor at `381dc8b7` was therefore about 9,100 files, 785 Markdown files and 198,000 Markdown
  lines. It rises as live lanes add records.
- The 950 / 200 / 45,000 targets are retired as targets. File counts are diagnostics, not deletion
  quotas (`orchestration/DRAFT-preservation-and-stabilization-session-prompts.md:246-247`).
- Lane A is closed. A future family needs its own exact authorization and, if its paths are post-09-24,
  a new evidence epoch.

**Stale facts in this plan, corrected here; earlier text is kept as written:**
- **The live job.** The "live job `57266000_0`" clause under *Protected active surface* is superseded.
  The generated `orchestration/LIVE-STATE.md:34` records `57266000_[0-0]` as `ERROR: FAILED=1`, measured
  2026-09-21T05:24:49Z on `login27`. That is a record citation; the scheduler was not queried for this
  closure. The frozen worktree `/pscratch/sd/j/josephrb/gate5-data-only-frozen-377c713` and its outputs
  are still not compaction targets.
- **Bindings.** The 2026-08-20 outcome's "117 path/hash bindings at digest `7586d636…`" is now **144
  receipt bindings, inventory sha256 `f9dab8dd…`** (`verify_hash_bindings.py`, ALL BINDINGS INTACT, at the
  A2 commit).
- **Markdown gates.** The 2026-08-20 outcome's "The Markdown gates are met" no longer holds: 803 files
  and 202,790 lines after A2 on `6800a754`.
- **Release surfaces.** These are added to the *Protected active surface*: `publication/`,
  `docs/publication/`, `reproduction/s5p/`, and `publication/release/verify_rc.py` with the release
  candidates it verifies.
- **Lane B.** Its `publication-results-YYYY-MM-DD` tag is a reserved act. `DECISION-20261006`: "Public
  deposit, release tagging, submission, and any additional scientific work remain separately
  authorized." Lane B's rules are otherwise unchanged.
