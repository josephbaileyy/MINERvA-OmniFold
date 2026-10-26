# Records rules: estimator names, the results index, and absence claims

**Status:** LIVE, 2026-10-22. Written by the paper-tighten lane (Claude) under Joseph's instruction of 2026-10-22:
*"yes do all three, use a subagent. ideally the internal note (not the analysis note) keeps all of these records
too right? there should probably exist some rules"*. Each rule names the check that enforces it. A rule without a
check is marked **not enforced**, with the reason.

**Why these rules exist.** On 2026-10-22 a session said `coverage under configuration (e) is untested`. The claim
was false. The same estimator is called `R` in the s5e and s5p contracts, and s5e had measured its
development-scale intervals (`state/s5e/cand/assess_receipt.json`, `points/*/pooled_cov68`). Three things went
wrong:

1. One estimator had many names and no registry.
2. Results were filed by campaign, not by question.
3. Nobody searched before claiming the result was absent.

The correction is recorded in `DECISION-20261022-joseph-open-items-and-rewrite-timing.md`.

## Where things are

| What | Where |
|---|---|
| Estimators, with every alias and its source line | `docs/orchestration/registry/ESTIMATORS.tsv`, `ALIASES.tsv` |
| Names the sources use that map to no single registered estimator | `docs/orchestration/registry/UNRESOLVED-NAMES.tsv` |
| Rules that attribute a receipt's results to an estimator | `docs/orchestration/registry/ATTRIBUTION.tsv` |
| Declared supersessions and withdrawals | `docs/orchestration/registry/STATUS.tsv` |
| The results index (generated) | `docs/orchestration/registry/RESULTS-INDEX.tsv`, `RESULTS-POPULATION.tsv` |
| The same, in the internal records document (generated) | `docs/analysis-note/records_estimators.tex`, `records_results_index.tex`, input by `main_records.tex` §R5 |
| The indexed results on estimator X, and a search for its other names | `python3 tools/registry/whatis.py "X"` (scope: "What the checks do not do") |

## Where the checks run

**On every pull request to `main`, once `.github/workflows/record-checks.yml` is merged.** The workflow (Joseph's
decision of 2026-10-23, `DECISION-20261023-joseph-2d-refined-integrate-ci.md` item 4) runs on GitHub's merge commit
of the pull request into its base (`refs/pull/N/merge`), so whole-tree checks judge the tree `main` would have after
the merge. Each check is its own named step, and every step runs even when an earlier one fails. It runs:

- the records checks: `generate_manifest.py --check --at-sha HEAD` (HEAD is the merge commit),
  `verify_hash_bindings.py`, `check_registry.py`, `results_index.py --check --base origin/<base>`, and
  `absence_claims.py --base origin/<base>`;
- the three registry `--self-test` runs, on every pull request (the hook runs them only when registry files are
  staged), and `tools/registry/test_registry.py`, which is over the hook's time budget but not CI's;
- the hook's other thirteen run lines, all stdlib Python reading only the repository: findings long-form pointers,
  ledger VL ids, row-owner side table, `whose_row` self-test, OPEN_ITEMS OI ids, receipt artifact tracking, LIVE doc
  indexed and its self-test, every doc has an overrides row, bounded control plane and its self-test, manifest
  inventory self-test;
- the note checkers' tests: `pytest` on `docs/analysis-note/test_check_sec4_receipts.py` (one pinned package,
  `pytest==8.3.4`, is installed for it), and `check_note_records.py --self-test` (on `records-inventory-base.json`)
  and `--self-test-pin`. `build_all.sh` runs the checkers themselves locally, not these tests;
- a last step that fails if any check modified the checkout.

**Why `--base`.** In CI nothing is staged and HEAD already contains the change, so the two checks that compare a
change with its base would compare it with itself. `absence_claims.py --base REF` judges the lines that
`git diff <merge-base> HEAD` adds or changes, where `<merge-base>` is `git merge-base REF HEAD`, and skips a line
whose text REF's or the merge-base's file already holds (the merge rule of rule 4). `results_index.py --check --base
REF` runs rule 8's gate against the merge-base's committed index instead of HEAD's. On the merge commit the
merge-base is the base tip. Without `--base`, both behave exactly as before.

**Weaker in CI than at commit time.** Two hook checks have arms that judge only what the index adds against HEAD.
In CI the index equals HEAD, so those arms judge nothing there: `whose_row.py --check-oi-ids` (block ownership of
new ids; its duplicate-id arm is whole-tree) and `live_doc_indexed.py --check` (newly LIVE and newly added docs;
its whole-tree arm and `--unrowed` still bind). They run in CI for their whole-tree arms. `generate_manifest.py
--check --at-sha HEAD` judges the merge commit: a pull request whose own head is fresh can still fail if the merge
with a newer `main` leaves `MANIFEST.tsv` stale. Merge `main` into the branch and regenerate.

**Local only.** These do not run in CI:
- the LaTeX builds of the note, paper and records document (they need a TeX installation and `biber`; build them
  locally as before);
- the loop-ledger advisory (`probes/probe-20260922-ledger-reconciles.py`): it warns and never blocks, it runs only
  when its report is staged, and it needs `markdown-it-py`;
- the checks the hook header declines (`generate_live_state.py --check-freshness`, `merge_guard.sh`,
  `nd-unfolding/pet/check_canonical_designation.py`), for the reasons given there.

**At commit time, in worktrees, the checks still do not run.** This clone's `core.hooksPath` is the absolute path
`/Users/josephbailey/local-research/MINERvA-OmniFold/.githooks`, the shared checkout's hook directory, and its
working tree lags `main`, so a worktree commit runs the old hook. Joseph chose CI over updating it. Run
`bash .githooks/pre-commit` from the branch's worktree before pushing to catch failures before the pull request
does. Until the workflow is merged, the "Enforced by" column below names the check and the hook line that runs it
when invoked.

In the hook, the three plain checks (`registry citations+labels`, `results index fresh+complete`, `absence claims
carry search`) always run. The three `--self-test` runs, which prove the instruments, run only when the commit
stages something under `tools/registry/` or `docs/orchestration/registry/`. Each check also runs on its own:
`python3 tools/registry/<script> …` (commands below).

## The rules

| # | Rule | Enforced by (run name in this branch's `.githooks/pre-commit`; see "Where the checks run") |
|---|---|---|
| 1 | **Registry integrity.** Every estimator definition, alias, unresolved name, attribution, status and waiver row cites `file:line`, its quote verbatim, and `line_sha256`: the digest of the WHOLE cited line. A citation is resolved by that digest; the line number is a hint. It holds if exactly one line of the file has the digest and that line holds the quote. When the line has moved, the check names where it found it, and `check_registry.py --repoint` refreshes the hint. It FAILS if no line has the digest, because the cited line was edited. That includes a retraction that keeps the quote; `--repoint` never accepts an edit. It also FAILS if the hinted line no longer has the digest and several lines do; a hinted line that still has its digest passes even if a copy of it exists elsewhere. Re-cite by hand with `check_registry.py --cite FILE:LINE`. | `registry citations+labels` (`tools/registry/check_registry.py`); `results index fresh+complete` for ATTRIBUTION, STATUS and WAIVERS rows; power: `registry self-test` (a moved line passes and is named, and no note remains after `--repoint`; a retraction quoting the alias fails and `--repoint` refuses it; a removed quote fails; a line duplicated onto two other lines, away from its hint, fails). **Not enforced:** that a row is never *dropped* to make the check pass. Deleting a row also removes what the check would verify, and no instrument here compares the registry with an earlier version of itself. Rule 8's gate covers the one consequence it can see: an estimator losing every attributed row. Review the diff of `docs/orchestration/registry/*.tsv`. |
| 2 | **Registry completeness.** Every estimator label printed by the paper, note, primer or records document must name exactly one registered estimator through aliases marked `identifying=yes`. The label patterns are the explicit list `LABEL_PATTERNS` in the script: "configuration (x)", the paper's findings-table Conf. cells, the first cells of the estimator tables, and "candidate/family/baseline X". Labels outside that list are **not checked**. Aliases that several configurations share (`lgbm`, `--estimator exact`, `negweight-refined`, "5 iterations", "n_estimators 100") are marked `identifying=no`; `whatis.py` reports them as NON-IDENTIFYING. The contract names F2, B0, R and N are searched by default with tight patterns (`candidate F2`, `"B0"`, `candidate R`, `family N`); their bare-token forms (`\bF2\b`, `\bB0\b`) are opt-in. Names a source uses without mapping them to an estimator go in `UNRESOLVED-NAMES.tsv` and are reported, not guessed. | `registry citations+labels`; power: `registry self-test` (an unregistered name and a two-way registration both fire; registered labels stay silent) |
| 3 | **Index freshness and completeness.** The committed index equals a fresh generation from the staged receipts, and every receipt in the declared population has rows. The population is a rule, stated in the docstring and the `METRIC_FAMILIES` block of `tools/registry/results_index.py`: a tracked JSON under `docs/orchestration/{state,receipts,runs}/` holding numbers under a key that the tokenized family rules assign to a family. The families are coverage 68/95 (and their hit counts), coverage, pull SD/mean/max, pulls, bias, closure, residual and residual SE. Count keys and parameter keys are excluded first. Every run prints the counts included, excluded and outside the roots. | `results index fresh+complete` (`results_index.py --check`); power: `results index self-test` (a planted result receipt fails; a planted non-result JSON and a result JSON outside the roots pass) and `tools/registry/test_registry.py` (fixture tests, run by hand; over the hook's time budget) |
| 4 | **Absence claims carry their search.** Applies to a paragraph of a `docs/orchestration/**/*.md` record, or of printed `docs/analysis-note/*.tex` prose, that asserts a result is absent, when the claim touches a line added or changed in the staged diff. That diff is `git diff --cached`: the index against HEAD. During a merge (MERGE_HEAD present), only lines new relative to EVERY parent are judged; a line either side already had is not. Such a paragraph must carry a search line: `Search: <aliases or terms; separated by ;> @ <commit sha>`. The sha must name a commit of this repository; `whatis.py` prints such a line. If the sentence is a scoping statement about a projection or a method parameter, not a claim that a result is absent, the paragraph may instead carry an explicit waiver with a reason: `<!-- absence-ok: <reason> -->` in `.md`, `% absence-ok: <reason>` in `.tex`. A waiver with an empty reason, or one quoted in a code span, is rejected, and accepted waivers are counted in the check's summary line. **Never drop an honest qualifier to pass this check.** The patterns are the list `ABSENCE_PATTERNS` in the script, each with an example it must fire on. They are matched on the paragraph's joined text, so a claim wrapped across lines is caught. "has/had no X" needs a test or measurement noun ("have no further run planned" is silent). Lines already in HEAD are not re-judged. In CI, `--base REF` judges instead the lines HEAD adds since `git merge-base REF HEAD`, skipping lines REF's or the merge-base's file already holds. | `absence claims carry search` (`tools/registry/absence_claims.py`); power: `absence-claims self-test` (fires on a bare claim, on a claim wrapped across two lines, on a search line naming no commit, on a search line in another paragraph, on a waiver with an empty reason, and on a claim new in a real merge's resolution; silent with a search line, with a waiver that gives a reason, on a claim only the other merge parent had, on unrelated "no", on comments and code spans; `--base`: fires on a bare claim a branch adds, including on the pull request's merge commit, and silent on a base line the branch copies, on a line the base tip already holds, with a waiver giving a reason, and with a search line) |
| 5 | **Never delete; supersede with a status.** A superseded or withdrawn result keeps its index rows. Its status is `withdrawn`/`superseded` when the receipt's file name says so, when its own top-level `status` begins with the word, or when a `STATUS.tsv` row (citing a line that holds its quote) matches. Otherwise it is `design-projection` when the receipt's OWN `status` (or, lacking one, `schema`) declares design arithmetic, or when a `STATUS.tsv` row says so. A file name alone is not enough: `r2_design.json` holds measured values. Otherwise it is `unreviewed`: no registered record withdraws or supersedes the result. That is **not** a claim that the result is current. The receipt's own `verdict` field (Tier S: `FUTILITY-FAIL`) is printed beside its status. | Partly. Statuses are generated and checked by rule 3. Deleting a receipt makes the index stale, so the check fails until the index is regenerated; at that point the rows are gone. **Not enforced:** that a receipt is never deleted from git. Nothing here can stop `git rm` plus a regenerated index. The repository's removal rules (AGENTS.md, "Pre-freeze provenance may leave main only through…") govern that. |
| 6 | **The records document holds the index, and only it does.** `main_records.tex` inputs `records_estimators` and `records_results_index`, outside comments. No posted driver's `\input` closure (`main_note`, `main_paper`, `main_primer`, `pet_note`) reaches either file. | `registry citations+labels` (`records_include_index`); power: `registry self-test` (fires when the records input is commented out, and when `main_note` inputs the index) |
| 7 | **Attribution is by citation, and by explicit key scope.** A receipt's results are attributed to an estimator only by an `ATTRIBUTION.tsv` row. The row's cited line must hold its quote **and** match one of that estimator's identifying alias patterns. Every row names the keys it covers (`keypath_regex`, e.g. `results/ours_` for the 2D LightGBM receipt, so its `data_vs_tune` comparison is not attributed); no row covers a whole receipt. A row with no such line is not kept; its results stay `UNATTRIBUTED` and listed. | `results index fresh+complete` (`load_rules`); power: `results index self-test` (a row citing a line that names (a), attributed to R, fails; the same line attributed to (a) passes) |
| 8 | **Never silently zero.** (i) A gate: an estimator with at least one attributed row in HEAD's committed index (in CI, with `--base REF`, the committed index of `git merge-base REF HEAD`) must keep at least one in the regenerated index, unless `WAIVERS.tsv` holds a row for it citing the line that says why. (ii) A disclosure: every estimator that a posted document (note, paper, primer, PET note) prints by a registered label either has an attributed row or is listed in the NO-RESULTS-INDEXED table of the records rendering (§R5.2). At this commit that table lists `b-exact-split`. | `results index fresh+complete` (`attribution_drops`, `no_results_listed`); power: `results index self-test` (dropping R's real attribution rules and regenerating fails with ATTRIBUTION LOST; a cited waiver makes it pass; the same drop once committed is silent against HEAD and fails with `--base` the commit before it; emptying the NO-RESULTS-INDEXED listing fails with SILENT ZERO) |

## What the checks do not do

- **They do not decide what a receipt measured.** The index copies numbers and key paths under the family rules. A
  value under a key with a `bias` token is indexed as bias, whatever the receipt meant by it. The rules exclude
  counts (`m_residual` is a seed count, `state/s5p/recovery/s5p_recovery.py:500`; `hits68` is indexed as a hit
  count), parameters, OmniFold's step-2 pull/push weights, design keys, bin edges (`E_lo_*`), correlations and
  chi-square values. Nothing under a correlation key is indexed, and under a `chi2` key only pulls and residuals
  are. A key is a p-value only when the WHOLE key is `p`, `p_value`, `pvalue` or `null_p…`, so labels such as
  `v3_p_mult_KE20` are descended. `residency_*` and keys that are paths are also excluded. Each exclusion is named in the script and has a self-test fixture.
- **Attribution is partial.** At this branch's fifth commit it covers 678 of 4958 rows. The rest are listed as
  UNATTRIBUTED. `whatis.py` lists receipts that mention an alias but carry no row attributed to that estimator,
  and "mentioned, not indexed" JSON receipts under the roots that hold no indexed metric at all. Read both before
  claiming a result is absent.
- **The population covers the listed metric families only.** p-values, χ² statistics, σ and power are outside it
  unless a family token names them. Receipts outside the three roots are outside it too. For example,
  `nd-unfolding/pet/**` holds 131 tracked files whose name contains `receipt` and ends `.json` (192 tracked paths
  match the pathspec `*receipt*.json` there, which also matches directory names), measured at `40dc2e5f`.
- **Shared aliases do not identify an estimator.** `--bkg-mode negweight-refined` serves (d), (e) and the 2D
  exact-split study. `400/31` is R's refinement classifier and also the capacity of s5p configuration 3's
  OmniFold estimators. `lgbm` is the learner of (a), (c), (d) and (e). `whatis.py` reports these as
  NON-IDENTIFYING or AMBIGUOUS, and the records document lists them in §R5.1.

- **Known limitations, recorded at the final review (2026-10-22).** Each is a property of the instruments above, not
  something they check.
  1. **Point groups come from key paths.** A point is "nominal" only if its path contains the word, or if
     `NOMINAL_POINTS` in `results_index.py` declares it. Today that covers one receipt family: s5e's
     development K1 is the nominal closure, per `state/s5p/contract.json:27`. Any other receipt that names its
     nominal point differently is pooled with its departures in the summary.
  2. **`bias_term_bWb` is a squared-norm quantity.** It is b'W⁻¹b (`m2-archive/m2_archive_results.json`, 5 rows,
     unattributed, up to 6214), and it is indexed as bias because of its token.
  3. **Waivers and the rule-8 gate are narrow.** A waiver is checked only for a valid citation, not for the merit
     of its reason. The gate catches only an estimator falling to **zero** attributed rows; a partial loss passes.
  4. **Editing a cited line fails until it is re-cited.** That is the point of the digest, and it is friction for
     anyone editing those files. The heaviest are `docs/analysis-note/sec_method.tex` (14 citations) and
     `paper_body.tex` (11), 25 in all. `VALIDATION_LEDGER.md:25` is cited too, and new rows land near the top of
     that file. Re-cite with `check_registry.py --cite`.
  5. **Design rows can land in a measurement family.** The `p_high_edge`/`p_low_edge` rows of
     `uncertainty-preparation-20261008/b/assurance.json` are filed under coverage (8 rows). They carry status
     `design-projection`, and the summary never pools them with `unreviewed` rows.
  6. **Enforcement is at the pull request, not at commit time.** Worktree commits run the shared checkout's old
     hook; the CI workflow runs these checks on every pull request to `main` once it is merged ("Where the checks
     run").
  7. **Attribution is partial, and families come from key names.** Attribution covers 678 of 4958 rows. The
     family and exclusion rules are name heuristics, and every exclusion is a named rule with a fixture.

## How to add an estimator, a name or a result

1. **A new estimator or a new name for one.** Add rows to `ESTIMATORS.tsv` or `ALIASES.tsv` with `source`,
   `line`, a verbatim `quote` from that line, and its `line_sha256` (`check_registry.py --cite FILE:LINE` prints
   it). Then `git add` the files and run
   `python3 tools/registry/results_index.py --write`, then `git add` its four outputs.
2. **A new receipt.** `git add` it, run `results_index.py --write`, then `git add` the four outputs. If you can
   cite the line that names its estimator, add an `ATTRIBUTION.tsv` row.
3. **A superseded result.** Add a `STATUS.tsv` row that cites the superseding record's line. Do not edit or
   delete the receipt.
