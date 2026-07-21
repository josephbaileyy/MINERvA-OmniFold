# Post-publication reorganization plan

**Instructions only — no move has occurred.** This plan is deliberately gated
behind the publication result freeze. It is not authority to clean the current
worktree, move an active output, or merge dimensional pipelines now.

## Gate: the publication-results tag

Reorganization may begin only after an annotated tag named
`publication-results-YYYY-MM-DD` points to the reviewed freeze commit. That
commit must:

- contain all publication production summaries and canonical ledger/RUN_LOG/
  STATUS updates;
- build the analysis note, primer, and paper from a clean checkout;
- identify ignored heavy artifacts by manifest and stable fingerprint;
- have no unresolved publication blocker in `OPEN_ITEMS.md`;
- be pushed with the tag so concurrent sessions share the same immutable base.

If any result changes after the candidate freeze, rebuild and review the
documents and create a new freeze commit/tag. Do not reorganize between a result
change and its replacement tag.

Canonical STATUS and RUN_LOG files stay at their current locations throughout:

- `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md` and
  `2d-unfolding/2D_OMNIFOLD_RUN_LOG.md`;
- `3d-unfolding/3D_OMNIFOLD_STATUS.md` and
  `3d-unfolding/3D_OMNIFOLD_RUN_LOG.md`;
- `nd-unfolding/ND_OMNIFOLD_STATUS.md` and
  `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`.

PET/FPS execution trackers may be retired only by a short tombstone at their
old path that points to the final canonical STATUS/RUN_LOG entries and freeze
tag.

## Non-negotiable method

Use a series of small, reviewable `git mv` commits. For each commit:

1. move one family or one coherent group only;
2. update direct references in the same commit;
3. search the full tracked tree for stale old paths and retired names;
4. run the moved family's help/smoke/wrapper tests without scientific
   production;
5. verify every publication artifact still resolves through its frozen product
   summary and fingerprint;
6. compare document builds or tracked outputs where the move can affect them.

Never combine cleanup with a physics-method change. Never use a bulk filesystem
move followed by repair. **A big-bang dimensional merge is explicitly
rejected:** 2D, 3D, 4D, 5D, PET, and FPS have different contracts, masks,
resources, and provenance. Shared utilities may be extracted only after callers
are protected by wrappers and tests.

## Stage 1 — transient job files

Inventory logs, scheduler receipts, scratch workdirs, partial outputs, and
one-off helper files by owner and campaign.

- Preserve tracked compact summaries and receipts that establish provenance.
- Move retained stale logs/one-offs to the dated external scratch archive
  convention in `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`.
- Delete only regenerable, untracked transients whose owning campaign is frozen
  and whose summary does not cite them.
- Never delete or relocate a heavy artifact until its summary fingerprint and
  current path have been verified against the freeze tag.
- Confirm no queued/running job writes any candidate path before touching it.

Acceptance: `git status` contains only the scoped cleanup; no publication
summary loses an input; scheduler/output namespaces are quiet.

## Stage 2 — status and layout index

Create or refresh one concise repository-layout index that points to, rather
than duplicates, canonical STATUS, RUN_LOG, reference, issue, ledger, open-item,
and publication documents.

- Keep all canonical STATUS/RUN_LOG paths unchanged.
- Mark frozen production roots, cold/historical families, compatibility entry
  points, and heavy-output locations.
- Record the freeze tag in the index.
- Add a machine-readable old-path → intended-new-path table before any cold
  family moves.

Acceptance: every current top-level workstream has one discoverable status and
chronology path; the index contains no verified number or copied chronology.

## Stage 3 — cold-family moves

Move only families with no active publication consumer. Candidate order is
oldest/coldest first: superseded diagnostics and archived launchers, completed
binned studies, then other frozen auxiliary families. Decide the exact candidate
list from the Stage-2 index; do not infer “cold” from file age alone.

For each family:

- use `git mv` and preserve internal relative structure where possible;
- update AGENTS/reference/index links and all tracked launchers that refer to it;
- search with `rg` for the old directory, filenames, output stems, and import
  paths;
- run syntax/help/unit tests and any ROOT-free fixture for that family;
- check frozen product summaries still point either to the unchanged heavy
  output or an explicit compatibility path.

Acceptance: zero unexplained stale references and no change to a scientific
artifact fingerprint.

## Stage 4 — compatibility wrappers

Before moving a launcher or import path used by external notes, batch recipes,
or collaborators, leave a small wrapper at the old path.

- Wrappers forward arguments and exit status without changing defaults.
- They resolve the repository root dynamically; no new personal HOME path.
- They print one concise deprecation/new-path message.
- Shell wrappers pass `bash -n` and a no-production `--help`/fixture test;
  Python wrappers pass compile/import/help tests.
- Keep wrappers for at least one publication cycle or until all external
  consumers explicitly migrate.

Acceptance: recorded old invocations and new invocations resolve the same
configuration and output namespace in dry-run/fixture mode.

## Stage 5 — limited parameterization

Only after wrappers and family tests pass, parameterize code that is demonstrably
identical apart from a small declared set of values.

Allowed examples include common manifest parsing, replica-manifest validation,
covariance projection, or launcher fields such as axes/output root when their
contracts are already identical. Requirements:

- a table of old caller → parameter set;
- golden fixture outputs for every caller;
- unchanged defaults and output names through compatibility wrappers;
- no weakening of fail-closed validation;
- one shared change per commit with all caller tests.

Do not create a universal dimensional driver, merge PET and scalar estimators,
or hide standard/FPS phase-space differences behind implicit flags. Duplication
is preferable to an abstraction that obscures a physics contract.

Acceptance: wrapper and direct calls agree on configuration, schema, and fixture
outputs; publication summaries still resolve to the freeze-tag implementation.

## Stage 6 — PET and FPS moves last

PET and FPS move only after all other stages are stable. They have the deepest
links to large point-cloud inputs, GPU launchers, standard/FPS selection modes,
W-source alignment, and support-complete lateral products.

- Freeze a PET/FPS path inventory including NPZ memmaps, ignored ROOTs, model
  weights, replica directories, active-universe inputs, and summaries.
- Move one of PET or FPS at a time, never both in one commit.
- Retain old entry-point wrappers and explicit standard-versus-FPS mode checks.
- Run PET ROOT-free tests, extraction fixture, wrapper tests, manifest readback,
  and output-provenance checks without retraining.
- Verify W-source and event-row alignment metadata after every path change.
- Rebuild all three publication documents after each family move.

Acceptance: no stale path in tracked files; all wrappers pass; every PET/FPS
published claim maps to the same freeze-tag summary and artifact fingerprint;
no GPU or event-loop production was triggered by the move.

## Final reorganization audit

The reorganization is complete only when:

- the old-path search is empty except for intentional wrappers, tombstones, and
  historical RUN_LOG text;
- all wrappers and family fixtures pass from a clean checkout;
- note, primer, and paper build successfully;
- frozen product summaries and heavy-output fingerprints are unchanged;
- canonical STATUS/RUN_LOG locations remain intact;
- the final layout index matches the filesystem;
- a reviewer can compare every reorganization commit to the
  `publication-results-YYYY-MM-DD` tag without disentangling a physics change.
