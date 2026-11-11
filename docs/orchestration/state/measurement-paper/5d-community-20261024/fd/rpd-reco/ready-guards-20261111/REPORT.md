# RPD-RECO: two before-READY guards (2026-11-11)

**Director-authorized** (2026-11-11), from the audit of the production-config proposal (#1064, coverage-5b-audit GO as
a proposal). Authored by the limitation-resolver lane. The branch is based on #848's head `9634aadf` and is proposed as
a PR into #848's branch, so #848's authorship stays Codex2's. Nothing runs: the config is not READY, #848 is unmerged,
and binding 2 does not exist yet.
<!-- absence-ok: the document's own status (nothing runs before READY, merge and binding 2), not a claim that a result does not exist -->

## The two changes

**(1) A loud refusal of unexpanded `${...}` fields.** `fd_rpd_reco.placeholder_paths` lists every key or string that
still holds `${`. Four guards use it:
- `CONFIG_PLACEHOLDER` (`Inputs`, after `CONFIG_READY`): any `${` left in the resolved config refuses before any step.
  That covers `flux_extract` and `flux_custody`, which no existing check read for placeholders: the check at
  `fd_rpd_reco_custody.py:1049` covers `trace_platform_roots` only.
- `PREPARE_PLACEHOLDER` (custody `prepare`, after its READY check): the same, before any staging.
- `ARGV_PLACEHOLDER` (the producer's CLI, including `flux-extract`) and `CUSTODY_ARGV_PLACEHOLDER` (custody's CLI):
  any `${` in the command arguments.

**(2) The extract receipt pins all 15 MAT files.** `flux-extract.json` gains `mat_dependency_sha256`: for each file
FluxReweighter opens, its original path and the sha256 that `prepare` measured under O_NOATIME.
- Each file is read once, at `prepare`. The extract reuses that measurement and adds no new read of an original.
- The list is `closed_mat_inventory()`, the closed set custody's `MAT_INVENTORY` guard fixes, now a module function
  that guard also uses. It is never discovered.
- `MAT_DEPENDENCY_RECEIPT` refuses a missing, extra, duplicated or malformed entry.

## Tests and mutants

New tests:
- `test_config_placeholder_refuses`: `flux_custody`, `flux_extract` and a nested list;
- `test_placeholder_paths_reports_each_location`;
- `test_argv_placeholder_refuses`;
- `test_prepare_placeholder_refuses`;
- `test_custody_argv_placeholder_refuses`;
- `test_mat_dependency_receipt_all_fifteen`: it removes each of the 15 in turn, and each refusal fires. It also adds a
  duplicate and corrupts a digest.

`test_constrained_extract_protocol_roundtrip` now builds a prestage with all 15 dependencies, and it asserts the
record's 15 pinned digests. Its two ROOT-open counts rise from 6 to 6 + 11: one units read of each other `.root` file
in the set.

Each new guard is mapped in `fd_rpd_reco_mutation.py`. The harness then generates a mutant that removes that guard's
refusal, and the guard's test must kill it.

| run | result | file |
|---|---|---|
| the suite at `9634aadf` (baseline, separate clean worktree) | 290 passed | `BASELINE-SUITE-9634aadf.txt` |
| the suite on this branch | **298 passed** (290 + 8 new) | `SUITE.txt` |
| the harness on this branch | **234 required, 234 executed, 234 killed**, complete and all_killed true (229 prior + 5 new) | `MUTATIONS.txt`, `MUTATIONS.json` |
| black / ruff | clean on the five files | `STATIC-CHECKS.txt` |
| mypy --strict | one error, identical at the baseline (numpy stubs in this venv) | `STATIC-CHECKS.txt` |

All runs were serial, with the five thread caps at 1.

`MUTATIONS.json` is the harness's raw report (sha256 `a400d5732bce1a79…`, recorded in its `receipt_annotation`) with
two annotations added, as in #848's `negative-exit-test-repair-20261108`: that annotation, and the precedent's
`disposable_fixture_artifact_paths`. The second lets the receipt checker resolve fixture names printed in test output
(such as `staged.root`) as disposable paths, so they are not read as citations of committed files. `SOURCE-SHA256SUMS` holds the four changed files' sha256. They
were equal before and after the suite and harness runs.

Nothing is submitted, deposited or tagged.
