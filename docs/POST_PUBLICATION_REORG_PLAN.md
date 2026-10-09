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

## Second simplification pass, 2026-10-07 (documentation only; one family proposed)

Run from `origin/main` `e2cf8a4e` in an isolated worktree. Lane A stays closed, and this pass removes nothing. It
changes no scientific claim, grade, gate or publication source.

**Authority.** Joseph's 2026-10-07 instruction to this session asked for a second simplification pass from
`origin/main`. Its first priority is to reconcile stale current-work and lifecycle records against committed
terminal outcomes. It authorizes reversible documentation improvements, and archival removals only after a proposal
is approved. The six retired backlog rows keep `migration-carried-forward` in their `authority` column, and `OI-193` keeps its
authorization link. This instruction, recorded here, is the authority for all seven retirements. The prose owner of five of the rows is Joseph
(OI-140, OI-141, OI-147, OI-149, OI-187). To reverse a retirement, restore the row from `e2cf8a4e`, with its queue, promotion and terminal criterion, and
run `control_plane_lint.py --write`.

**Lifecycle records reconciled with committed terminal outcomes.**
- **Register.** `OI-193` is retired. Its terminal criterion, "campaign final-disposition record committed and
  pushed", is met by `DELIVERY-20261006-s5p-campaign-terminal.md` (`9984a5fd`). Its `OPEN_ITEMS.md` row now reads
  CLOSED and routes to that record. Six unassigned backlog rows are also retired, each because its own record states
  the outcome: `OI-140` ("VERIFICATION LANDED", with the remainder moved to `OI-147`), `OI-141` ("FIXED AND LANDED"),
  `OI-145` ("REPINNED"), `OI-147` ("COMPLETE"), `OI-149` ("FIXED AND LANDED") and `OI-187` ("RULED … BY JOSEPH").
  The views were regenerated with `control_plane_lint.py --write`, and the current-work list went from 14 rows to 13.
- **Residuals that do not travel with the retired rows.**
  - `OI-145`: its remaining checker failure belongs to `OI-148`, which stays active.
  - `OI-147` and `OI-149`: they hand their residual to the B1 pause's *expiry* clause (c) and the B1 lift. Both
    are routed to `DECISION-20260822-joseph-b1-lift-and-clause-c.md`. This is not the §6.4 clause (c) disposed of on
    2026-09-20.
  - `OI-187`: its ruling has two halves. Half (a), "upgrade, not a submission blocker", is complete. Half (b) is a
    standing posture: *"keep the covariance work going"*. It was later amended conditionally (`R5`,
    `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`), then modified "for this article only" by item 1 of
    `docs/publication/DECISION-20261006-joseph-publication-approvals.md`. After retirement it lives in
    `DECISION-20260901-joseph-oi187-upgrade-not-blocker.md`, which stays LIVE and is routed from `CATALOG.md`, and
    in that 2026-10-06 decision. No active register row carries it.
- **Handoffs.** Six concluded orchestration handoffs are now `ARCHIVAL terminal` in `MANIFEST-overrides.tsv`, each
  with a `canonical_successor`: 0925 negweight, 0926 precision completion, 0928 s5p parallel tasks, 0929 s5p cold
  start, 0929 seed-gap correction and 1005 2D coverage. No document bytes changed.
- **Kept LIVE.** Four handoffs stay `LIVE` because each still holds items tracked nowhere else: 0924 preparation
  (D1–D11), 0928 s5p recompute (two LOWs owed), and the 0921/0922 GBDT pair (see the 2026-09-24 recovery
  manifest). The remaining s5p harness, tier-D and note-sync handoffs are current.
- **Router.** `CATALOG.md`'s scalar-5D "start here" row and its "what is authorized next" row had still routed to
  the 2026-09-24 preparation handoff. Both now point to the terminal delivery and to `docs/CURRENT_WORK.md`.
- **Left for owners.** These items are partly done, and their owners must decide them:
  - `OI-127`, `OI-128`, `OI-129`, `OI-70`, `OI-73`, `OI-125`, `OI-173`;
  - `OI-131(b)`: discharged by measurement on 2026-08-20, but the lint gives a leaf row no retirement except
    deletion;
  - `LIVE-STATE.md`, generated 2026-09-21, which has never routed `OI-193`; regenerating it is held under `OI-73`.

**Compact entry points added.**
- `nd-unfolding/pet/README.md`: one table that names where each of the six completed PET campaign directories ends.
- `reproduction/s5p/README.md`: which of the five committed reports is current, which is history, and where each
  is recorded. Two of them are 9,417 lines, the longest Markdown in the tree.

**Size by dependency.** Tracked content totals 452.6 MB in 9,213 files. `nd-unfolding/pet` alone is 332.2 MB in
6,003 files. A read-only classification of its campaign subtrees found:
- **P (reproduction/publication):** none. No reproduction or publication build reads them. The two PET figures in
  the note are byte copies.
- **R/T (runtime readers and tests):** the code that reads them is PET's own, and none of it is outside
  `nd-unfolding/pet`. Bank building and the decks read `final_design/results/final`, `predecessor_posthoc`,
  `step2int`, `improvement_campaign/{confirm,phase_*}` and `gbdt_comparison/results`, and tests cover them. The
  runners and a test that requires 500 or more committed configs matched to `runs/*.tsv` read `configs/*`. These
  configs are regenerable by `freeze/make_stage_manifests.py`, but removing them is a test migration, not an
  archival.
- **H (hash bindings):** `configuration_comparison/receipts` and `direct_token_comparison/local_validation` are the
  only sources of inventory rows in `verify_hash_bindings.py` (144 at `f9dab8dd…`).
  `direct_token_comparison/execution_runs` is asserted by `test_hash_bindings.py`.
- **C (citations only):** `final_design/results/{dev1,dev2S,dev2Q,dev2P,dev2L,dev2T,s3p,s3p_new}` (674 files),
  `source_audit_runs` (64) and `runtime_runs/20260910` (48).

None of these PET subtrees exists at either evidence epoch. Any removal therefore needs a new epoch and Joseph's
authorization (Lane A closure, above).

### HISTORICAL, SUPERSEDED — the A3 proposal as written before authorization; executed 2026-10-07, see *Family A3 executed*

Original heading, preserved: *Proposed family A3 — PET final-design development and sizing outputs (NOT authorized; not executed)*

*Superseded 2026-10-07: authorized and executed the same day; see* Family A3 executed *below.*

- **Paths.** The exact list is [`POST_PUBLICATION_REORG_A3_PATHS.txt`](POST_PUBLICATION_REORG_A3_PATHS.txt): 674
  paths, sha256 `149ee290…e2b9`, from `git ls-files` at `e2cf8a4e`. They are 668 JSON and 6 TXT files, 47.5 MB, and
  no Markdown. By directory: dev1 273, dev2S 97, dev2Q 65, dev2P 65, dev2L 65, dev2T 33, s3p 44, s3p_new 32.
- **What depends on them.**
  - No runtime import, test, publication build, manifest row or hash-binding row.
  - Their producer is `final_design/results/harvest.sh`. It copies stage outputs from Perlmutter into
    `results/<stage>/` in a checkout, and it stays.
  - Three siblings in `results/` are excluded:
    - `dev3N` is read by `gbdt_comparison/pgc_*.py`, and by `summarize_dev.py` too;
    - `s3n` is read by `analysis/run_final.sh` and `run_look1.sh`;
    - `smokeX` is a 2026-09-26 smoke record with its own Markdown, and it was not classified.
  - The family is an *indirect reproduction input* for two dev summaries. After removal, both are rebuilt from the
    tag rather than from main:
    - `dev/summarize_dev.py --root` reads the dev directories and builds `dev/DEV_TABLES-*.json`. It also reads
      `dev3N/` and the predecessor post-hoc files, which both stay. The script globs `posthoc2/` under `--root`,
      but the committed files are in `predecessor_posthoc/`, so the rebuild needs a `--root` that maps one to the
      other. Its `dev3X` source is not in the tree. The 2026-09-27 table is pinned in
      `slides/deck_numbers.json`. The review rebuilt it from the committed inputs at `e2cf8a4e`, with
      `--ks 2,3,4,5,6`. All 144 populated cells are identical, but the bytes differ (`62e226ae…` against the pinned
      `eb7a7eb6…`). The pinned file carries empty `L128H2E16` entries in four tables, and committed `dev2L/` holds
      no such runs, so the pinned table was built from scratch rather than from these files. This difference
      exists before any removal.
    - `dev/n2_table.py --scores` reads the `S3P-*` score files, which are in `s3p/`, for the S-N2 screen in
      `dev/SCREENS-*.json`.
  - The prose citations are `final_design/DEVELOPMENT-20260926.md:9`, `PROTOCOL-20260925.md:320,596`,
    `sizing/SIZING-20260926.md:5` and `HANDOFF-pet-final-design.md:115`. The last of these names a scratch path.
- **Dry run.** A throwaway worktree at `e2cf8a4e` was checked with the 674 paths removed and again without the
  removal. The results were identical:
  - `verify_hash_bindings.py`: ALL BINDINGS INTACT.
  - `verify_receipt_artifacts.py`: the same pinned inventory, `49916d28…`.
  - `generate_manifest.py`: byte-identical output.
  - pytest over `final_design`, `gbdt_comparison`, `generator_diagnosis` and `nd-unfolding/tests/test_hash_bindings.py`,
    run locally on macOS with Python 3.12:
    - 308 passed, 9 skipped, and the same 4 failures, which also fail on unmodified main;
    - the 4 are in `test_pfd_build_evidence`, `test_pfd_provenance_gate` and `test_step2_ensemble` (×2);
    - the reviewer's environment gave 309/9/3, with `test_pfd_build_evidence` passing.

    The comparison that matters is the before/after failure set in one environment.
  - None of the 40 local worktrees has a dirty edit under these directories. Cluster checkouts were not
    inspected.
- **Preservation and recovery.**
  1. Push an annotated tag `evidence/simplification-2026-10-07-<sha>` at the pre-removal main commit.
  2. Write an all-ref bundle and its sha256 to new sibling directories named after the new tag. Place them beside
     the 2026-08-20 epoch directories named at the top of this plan, which are immutable and not targets.
  3. In a fresh clone, restore all 674 paths with `git show <tag>:<path>` and match each sha256.
  4. From a checkout of the tag, rebuild `DEV_TABLES-20260927.json`. Expect every populated cell to equal the
     pinned file, not a byte match; the known difference is recorded above. Then rebuild the S-N2 values in
     `SCREENS-20260927.json`. Record any input that does not resolve, rather than proceeding.
- **Consumer changes, in the removal commit.**
  - Add one `final_design/results/README.md` stub, the old-path discovery route. It names the tag, the list file and
    the `git show` command.
  - Add one line to each of `summarize_dev.py`'s and `n2_table.py`'s usage docstrings naming the tag as the inputs'
    source.
  - The dated records keep their bytes.
- **Expected reduction.** −673 tracked files net (−674, plus the stub) and −47.5 MB. Markdown grows by one file
  and about 10 lines. As a reference, `e2cf8a4e` has 9,213 files, 804 Markdown files and 203,166 Markdown lines.
  Step 10 records the real counts at the removal's own base.
- **Validation.**
  - Run gate steps 1–10 above on the rebased head.
  - Re-run the dry-run set and expect the same failure set.
  - `build_all.sh`: the three `pdftotext` digests must not change.
  - Run `squeue` to confirm that no queued job writes into the repository paths. PET jobs write to `$B` on scratch.
  - Run `git status` in the cluster checkouts to confirm that none has a dirty edit under these directories.
  - Have one independent read-only reviewer check the family diff.

The other two citation-only subtrees, `source_audit_runs` and `runtime_runs`, could join A3 under the same epoch.
They are left out because `source_audit_runs` carries a manifest consumer row (`preserve.py`) and
`reproduce_evidence.py` reads it at a pinned revision; each needs its own check.

### Family A3 executed, 2026-10-07

**Decision (Joseph, 2026-10-07, verbatim):** "Merge PR #41, then execute A3 under a new evidence tag".

PR #41 was merged at its reviewed head `1e377eaf` as `fc97eaf9`. The proposal above is the specification. Each gate
step was run against `fc97eaf9`, the pre-removal main:

1. **Enumeration.** At `fc97eaf9`, `git ls-tree` over the eight directories gives exactly the 674 paths in
   [`POST_PUBLICATION_REORG_A3_PATHS.txt`](POST_PUBLICATION_REORG_A3_PATHS.txt), sha256 `149ee290…e2b9`. Nothing
   under them changed between `e2cf8a4e` and `fc97eaf9`.
2. **Dependencies.**
   - No tracked or untracked edit under the eight directories in any of the 39 local worktrees.
   - On NERSC (2026-10-07T21:11Z, `login07`), `squeue --me` returned 0 jobs.
   - The five scratch checkouts that contain the tree are clean under these directories. No `harvest`, `keep_busy`
     or `pfd` process was running on that login node; other login nodes were not inspected.
   - The proposal's consumer classification stands: no code, test, manifest or hash-binding reader.
3. **Internal references.** Only the producer `harvest.sh`, which stays.
4. **Preservation.**
   - **Tag.** Annotated tag `evidence/simplification-2026-10-07-fc97eaf9`, tag object `48a16c16…`, commit
     `fc97eaf9`. It was pushed before the removal.
   - **Bundle.** `repository-all.bundle` (289,789,560 B, `git bundle verify` okay) sits with ref and worktree
     snapshots, `a3-blobs.tsv` (path, blob id and sha256 for all 674), `RECOVERY.md` and `SHA256SUMS`. They are in
     new sibling directories `simplification-2026-10-07-fc97eaf9/`, under the local `evidence-epochs/` and under
     NERSC `evidence/repository-epochs/`. The NERSC copy passes `sha256sum -c`. The earlier epoch directories were
     not touched.
   - **Recovery.** All 674 paths were restored with matching sha256 three ways: from the bundle alone (locally),
     from the bundle alone on NERSC, and from a fresh clone of GitHub.
   - **Derived rebuilds, from a clean worktree of the tag:**
     - `DEV_TABLES-20260927.json`: every populated cell equal; the only differing leaves are the 65 known
       `L128H2E16` placeholders.
     - The S-N2 values in `SCREENS-20260927.json`: all seven numeric values reproduce exactly. H2S1 and L128S1 come
       from `s3p/` at the tag; the other five come from `s3n/`, which stays.

     Proofs: `derived-rebuild-proof.txt` in both epoch directories.
5. **Surviving references.**
   - The dated records keep their bytes.
   - New stub `nd-unfolding/pet/final_design/results/README.md` names the tag, the list and the recovery commands.
   - `summarize_dev.py` and `n2_table.py` each gained a two-line docstring note naming the tag. Neither file is
     hash- or blob-pinned.
6. **Discovery.** The stub; the *Family A3* subsection of `CATALOG.md`; and this record.
7. **Checks, on the removal tree against `fc97eaf9`.**
   - `verify_hash_bindings.py`: ALL BINDINGS INTACT, 144 receipt bindings at `f9dab8dd…`, the same as before.
   - `verify_receipt_artifacts.py`: the same pinned inventory, `49916d28…`.
   - `control_plane_lint.py` and `live_doc_indexed.py --check` pass, and so does the withdrawal-completeness check.
   - `generate_manifest.py` was regenerated. Its changes are line counts and inbound counts from the new stub and the
     CATALOG lines.
   - Pytest over `final_design`, `gbdt_comparison`, `generator_diagnosis` and `test_hash_bindings.py`: 308 passed,
     9 skipped, 4 failed, both before (a clean worktree of the tag) and after, with an identical failure set. The
     reviewer's environment gave 309 / 9 / 3 at both `fc97eaf9` and `0e55c19e`, with `test_pfd_build_evidence`
     passing there; the invariance holds in both environments.
   - `docs/orchestration` tests: 948 passed and 23 failed, before and after, with an identical failure set. The
     failures are the environment-bound `test_wakerctl` (17), `test_deploy_oi135_watcher_swap` (3),
     `test_watch_slurm_array_resume` (2) and `test_usagectl` (1).
   - Local macOS, Python 3.12.
8. **Products unchanged.** Before: `build_all.sh` on a clean worktree of the tag gives PASS (strict containment,
   0 of 29 struck literals) at 123 / 9 / 9 pages. The `pdftotext` sha256 prefixes are note `56865a04…`, primer
   `11b21c1f…` and paper `dd521150…`. The first run hit the known biber PAR-cache failure on the pristine tree, and
   purging the temp cache cleared it.

   After: `build_all.sh` on a clean worktree of the removal commit `0e55c19e` gives PASS (strict, tree clean, 0 of
   29 struck literals) at 123 / 9 / 9 pages, and all three `pdftotext` digests are identical. The
   `docs/analysis-note` sources are byte-identical between `fc97eaf9` and `0e55c19e`.
9. **Independent review.** One fresh read-only reviewer examined `0e55c19e` and returned **APPROVE WITH CHANGES**.
   - It re-verified: the deleted set equals the list exactly; all 674 blobs match at the tag; the epoch checksums
     pass locally and on NERSC; the bundle verifies; there is no surviving consumer; and the checks and discovery
     links work.
   - Nothing was blocking. It made one should-fix, to complete steps 8–10, and three notes: the environment-dependent
     test counts, the placement and wording of the docstring note, and a recovery line for the CATALOG entry.
   - All four were applied in the follow-up commit.
10. **Counts.**

| | tracked files | Markdown files | Markdown lines | tracked bytes |
|---|---:|---:|---:|---:|
| before A3 (`fc97eaf9`) | 9,214 | 804 | 203,328 | 452.63 MB |
| after A3 (removal commit `0e55c19e`) | 8,541 | 805 | 203,426 | 405.14 MB |

The removal is −674 files and −47.49 MB. The new stub adds one Markdown file. The record, the stub and the CATALOG
lines add 98 Markdown lines, against an estimate of about 10 that counted only the stub.

## Uncertainty preparation, lane D, 2026-10-09 (deferred designs only; nothing moved or removed)

This section was written from base `f8e2bf85` under the uncertainty-preparation plan
(`orchestration/PLAN-20261008-uncertainty-investigation-preparation.md`). It moves nothing, removes
nothing and asks for no authorization. Lane C (layout moves only after the publication freeze) and the
family-specific authority rule under *Lane A closure and A2* still govern. Lane D's measurements and
dispositions are in `orchestration/state/uncertainty-preparation-20261008/d/`.

### Deferred move design: the s5p generator-prediction family in `3d-unfolding/genie/`

**Why it is a navigation problem.** These files compute the 5D generator predictions for s5p
(`OI-193`, terminal). They live in a 3D directory, beside 3D generator code with similar names.
`README.md` now says what they are. That routing is the improvement made now; the move stays deferred.

**Exact paths.** These five, all added on or after 2026-09-27 (`e13caf87`):
`3d-unfolding/genie/gen5d_flux_reweight.py`, `gen5d_flux_supplement.py`, `gen5d_mode_components.py`,
`gen5d_to_rootpreds.py` and `run_gen5d_supplement.sh`. The `gen5d_*` glob misses the fifth.

**Consumers in `main` at `f8e2bf85`.**
- *Runtime and reproduction.*
  - `reproduction/s5p/scope.py` `PRODUCER_FILES` requires all five to be byte-identical at these
    checkout paths to the copies that ran.
  - `reproduction/s5p/repro_s5p.py` launches `3d-unfolding/genie/gen5d_to_rootpreds.py` by path (line 719).
    It also imports that file after inserting `3d-unfolding/genie` on `sys.path` (lines 561-562).
- *Imports within the family.* `gen5d_flux_supplement` and `gen5d_mode_components` import
  `gen5d_flux_reweight`. `gen5d_mode_components` also imports `gen5d_flux_supplement` and
  `gen5d_to_rootpreds`.
- *Other importer.* The frozen record `orchestration/state/note-capgap-20261003/cap_share.py`.
- *Tests.* `reproduction/s5p/tests/test_repro_s5p.py`.
- *Recorded digests (receipts; never edited).* These record the five files' digests:
  - `state/s5p/gen5d/gen5d-fluxfix{,-2,-3}.json`;
  - `state/s5p/stage7/generator-context/*`;
  - `state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt`;
  - the committed `reproduction/s5p/reports/*`.
  None of these files is in `verify_hash_bindings.py`'s inventory: ALL BINDINGS INTACT, with no
  `gen5d` binding.
- *Publication.* `docs/analysis-note/redraw_central_only.py` cites the family in comments and
  reads its receipts. Nothing under `publication/` names any of the five code paths, but
  `publication/release/figs/export_fig_arrays.py` and `publication/w2/design/*.json` read the
  family's cluster products (`/pscratch/.../s5p-20260926/gen5d*/*.npz`). A code move does not
  change those paths.

**Evidence epochs.** All five are absent at `evidence/prepublication-2026-08-20-0b329e8a` and
`evidence/preparation-2026-09-24-bf34a12c`. All five are byte-identical at
`evidence/simplification-2026-10-07-fc97eaf9` (`git rev-parse <tag>:<path>` against `HEAD`). That
tag was admitted as a removal boundary **for A3 only**, and that authority does not transfer.

**Intended destination, if a move is ever authorized.** `nd-unfolding/gen5d/`, keeping the five
basenames so that the family's own imports survive unchanged.

**Compatibility contract.** A wrapper left at the old path would change the bytes there, which
`scope.py` compares to the recorded copies. So no wrapper can keep both the old path and its bytes.
Any move must instead:
- repoint `scope.py`'s `PRODUCER_FILES` and `repro_s5p.py`'s two references in the same commit;
- leave every receipt's recorded path as a historical citation, recoverable with `git show <tag>:<path>`;
- keep a discovery row from each old path to its new path.

**Preconditions.**
- The publication-results freeze (Lane B), because `reproduction/s5p/` is a protected release surface.
- A new pushed evidence epoch containing the five paths, or Joseph's explicit admission of an existing
  epoch for this family.
- Joseph's family-specific authorization.
- The s5p reproduction tiers that `reproduction/s5p/README.md` names as current, re-run from a clean
  checkout before and after, with an identical report verdict.
- All three document builds, with unchanged `pdftotext` digests.

**Migration sequence, each step reviewable on its own.**
1. Record the authorization and the epoch, and restore the five paths from the tag by sha256.
2. In one commit, move the five files and update `scope.py`, `repro_s5p.py` and its test. Change no
   other bytes. Run the s5p harness and its tests before and after.
3. Add the discovery row (here and in `CATALOG.md`) and update `README.md`'s layout line.
4. Have one read-only reviewer check the family diff.

**Recommendation now: do not move.** The README route already removes the misdirection. A move costs
a reproduction re-run and a protected-surface edit, and it buys only a better location.

### Not a removal candidate: `2d-unfolding/sbatch_final_rollup_full.sh`, `2d-unfolding/uq/final_rollup_full.sh`

These are no longer the route to the quoted 2D combined covariance; `uq/rollup_vl170_adoption.sh`
is (`2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, "Which script produced the quoted 2D uncertainty"). They
stay for two reasons:
- step (a) of `final_rollup_full.sh` produced the ML covariance
  `uq/seedscan_lgbm_ml/uq_covariance_ml.root`, which the current rollup reads;
- its step (c) and (d) outputs in `uq/universe_stage2_MEFHC_full/` are untracked cluster files
  that `2d-unfolding/PLOT_GUIDE.md` still cites.

Documentation now marks them superseded. No removal is proposed.

## Next preparation, Session 3 (structure), 2026-10-09 (move constraints and one removal candidate; nothing moved or removed)

This section is written from base `5ac9706a`. It moves nothing, removes nothing and asks for no
authorization. Lane C (layout moves only after the publication freeze) and the family-specific
authority rule under *Lane A closure and A2* still govern. The session's code changes, measurements and
deferred code patches are in `orchestration/state/next-preparation-20261009/structure/REPORT.md`. Lane
D's s5p `gen5d` design above is unchanged and remains the discovery route for that family.

### Move constraint: the 2D covariance modules in `2d-unfolding/uq/`

**Exact paths.** `2d-unfolding/uq/analyze_uq.py`, `uq/analyze_universes.py`, `uq/_ours_only_chi2.py`
and, from this session, `uq/reported_cells.py`. The first three import the fourth as a sibling.

**Inbound imports that a move breaks.** Each of these puts `2d-unfolding/uq` (on Perlmutter, the
hardcoded `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq`) at `sys.path[0]` and imports
by module name:
- `analyze_uq`, for `th2_to_array`, `th1_to_array`, `PT_EDGES` and `PZ_EDGES`, from six frozen
  records: `state/ki84-adopt-20261006/{purity_datastream_check,recompute_2d_budget}.py`,
  `state/ki84-rebuild-20261006/{boot_spreads_vl170,compare_ki84_band,predict_ki84}.py` and
  `state/note-boot-20261003/boot_spreads.py`. The live
  `uq/coverage_fixed_truth/ki85_compare.py` imports it the same way.
- `_ours_only_chi2`, for `flatten_paper` and `tmatrix_to_numpy`, from the frozen
  `state/uqpaper-median-20261006/paper_median.py`.
- `analyze_universes`, for `CATEGORY_ORDER` and `category_for_band`, from
  `uq/plot_uncertainty_fig6_7_style.py`, a note figure producer.

**Launchers that name the paths.** `uq/rollup_vl170_adoption.sh` (the adopted VL172 chain),
`uq/final_rollup_full.sh`, `sbatch_analyze_MEFHC_{final,universes}.sh`, `uq/run_split_analysis.sh`
and `HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh`.

**Hash and reproduction constraints.** No current-bytes digest of these files is verifier-checked.
`analyze_universes.py` is pinned at revision `901f2c64` by `nd-unfolding/tests/test_hash_bindings.py`,
which a move does not break. The frozen records are byte-frozen (Goal 2 of the next-preparation
dispatch), so they cannot be repointed. Their imports must keep resolving at the old directory.

**Compatibility contract, if Lane C ever moves `uq/`.** No byte-scope applies to these modules, so a
re-exporting wrapper at each old path is possible. Each of the four old paths keeps a module that
re-exports every name listed above, and `reported_cells.py` stays importable as a sibling of all
three.

**Recovery test.** In a clean checkout at the post-move commit, for each frozen record, import its
module from the old directory with that directory at `sys.path[0]` and resolve every attribute the
record uses. `2d-unfolding/tests/test_reported_cells.py`
(`test_producers_keep_the_names_their_importers_use`) is the static form of this check; extend it to
the wrappers.

**Migration sequence.**
1. Authorization and the evidence epoch.
2. Move plus wrappers in one commit.
3. The recovery test, plus `test_reported_cells.py` and `test_final_rollup_full_refusal.py`.
4. One read-only review.

**Recommendation: do not move.** The directory is the de facto import contract of seven frozen
records.

### Removal candidate, not proposed: the Stage-1-era 2D analysis launchers

**Exact paths.** `2d-unfolding/sbatch_analyze_MEFHC_final.sh` and
`2d-unfolding/sbatch_analyze_MEFHC_universes.sh`.

**Why they are a hazard.**
- Their universe glob `uq/2d_xsec_MEFHC_5iter_lgbm_uni_*.root` also matches the later full sweep's
  `uni_full_*` files, so the two sweeps mix whenever both are on disk.
- They write `uq/uq_covariance.root` and `uq/universe_stage2_MEFHC/` in place, without a refusal.
- Neither output is a quoted or sha-pinned product
  (`state/ki84-adopt-20261006/sha256sums_2d-unfolding_uq.txt` lists neither).

**Inbound references.** No code calls either script. They are cited only by
`orchestration/AUDIT-FINDINGS-20260731.md:654` and the Sep-09 talk's `commit_inventory.json`.

**Disposition.**
- Keep both files; removal needs family-specific authority and an evidence epoch.
- They are not edited in this session: the lane's file allowance went to the two families recorded in
  its report.
- A prospective guard would be the same refusal as `uq/final_rollup_full.sh`'s. It is listed in that
  report's backlog.
