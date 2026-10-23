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

**Today, the checks below run only when someone runs them.** They are wired into this branch's own
`.githooks/pre-commit`, which runs when invoked from a worktree of the branch: `bash .githooks/pre-commit`, before
a push. They do **not** run at commit time in worktrees. This clone's `core.hooksPath` is the absolute path
`/Users/josephbailey/local-research/MINERvA-OmniFold/.githooks`. That is the shared checkout's hook directory, and
its local `main` (`e25abfd5` when this was written) predates these checks, so a worktree commit runs the old hook.
No CI check exists either (`git ls-files` at `40dc2e5f` holds no `.github/`, GitLab, CircleCI or workflow YAML file). Commit-time enforcement in worktrees therefore needs one of two things: the shared
checkout's hook updated, or a CI check. **Both are pending Joseph's decision.** Until then, the "Enforced by"
column below names the check and the hook line that runs it when invoked, not a guarantee that every commit was
checked.

In the hook, the three plain checks (`registry citations+labels`, `results index fresh+complete`, `absence claims
carry search`) always run. The three `--self-test` runs, which prove the instruments, run only when the commit
stages something under `tools/registry/` or `docs/orchestration/registry/`. Each check also runs on its own:
`python3 tools/registry/<script> …` (commands below).

## The rules

| # | Rule | Enforced by (run name in this branch's `.githooks/pre-commit`; see "Where the checks run") |
|---|---|---|
| 1 | **Registry integrity.** Every estimator definition, alias, unresolved name, attribution, status and waiver row cites `file:line`, its quote verbatim, and `line_sha256`: the digest of the WHOLE cited line. A citation is resolved by that digest; the line number is a hint. It holds if exactly one line of the file has the digest and that line holds the quote. When the line has moved, the check names where it found it, and `check_registry.py --repoint` refreshes the hint. It FAILS if no line has the digest, because the cited line was edited. That includes a retraction that keeps the quote; `--repoint` never accepts an edit. It also FAILS if several lines have the digest. Re-cite by hand with `check_registry.py --cite FILE:LINE`. | `registry citations+labels` (`tools/registry/check_registry.py`); `results index fresh+complete` for ATTRIBUTION, STATUS and WAIVERS rows; power: `registry self-test` (a moved line passes and is named, and no note remains after `--repoint`; a retraction quoting the alias fails and `--repoint` refuses it; a removed quote fails; a duplicated line fails). **Not enforced:** that a row is never *dropped* to make the check pass. Deleting a row also removes what the check would verify, and no instrument here compares the registry with an earlier version of itself. Rule 8's gate covers the one consequence it can see: an estimator losing every attributed row. Review the diff of `docs/orchestration/registry/*.tsv`. |
| 2 | **Registry completeness.** Every estimator label printed by the paper, note, primer or records document must name exactly one registered estimator through aliases marked `identifying=yes`. The label patterns are the explicit list `LABEL_PATTERNS` in the script: "configuration (x)", the paper's findings-table Conf. cells, the first cells of the estimator tables, and "candidate/family/baseline X". Labels outside that list are **not checked**. Aliases that several configurations share (`lgbm`, `--estimator exact`, `negweight-refined`, "5 iterations", "n_estimators 100") are marked `identifying=no`; `whatis.py` reports them as NON-IDENTIFYING. The contract names F2, B0, R and N are searched by default with tight patterns (`candidate F2`, `"B0"`, `candidate R`, `family N`); their bare-token forms (`\bF2\b`, `\bB0\b`) are opt-in. Names a source uses without mapping them to an estimator go in `UNRESOLVED-NAMES.tsv` and are reported, not guessed. | `registry citations+labels`; power: `registry self-test` (an unregistered name and a two-way registration both fire; registered labels stay silent) |
| 3 | **Index freshness and completeness.** The committed index equals a fresh generation from the staged receipts, and every receipt in the declared population has rows. The population is a rule, stated in the docstring and the `METRIC_FAMILIES` block of `tools/registry/results_index.py`: a tracked JSON under `docs/orchestration/{state,receipts,runs}/` holding numbers under a key that the tokenized family rules assign to a family. The families are coverage 68/95 (and their hit counts), coverage, pull SD/mean/max, pulls, bias, closure, residual and residual SE. Count keys and parameter keys are excluded first. Every run prints the counts included, excluded and outside the roots. | `results index fresh+complete` (`results_index.py --check`); power: `results index self-test` (a planted result receipt fails; a planted non-result JSON and a result JSON outside the roots pass) and `tools/registry/test_registry.py` (fixture tests, run by hand; over the hook's time budget) |
| 4 | **Absence claims carry their search.** Applies to a paragraph of a `docs/orchestration/**/*.md` record, or of printed `docs/analysis-note/*.tex` prose, that asserts a result is absent, when the claim touches a line added or changed in the staged diff. That diff is `git diff --cached`: the index against HEAD. Such a paragraph must carry a search line: `Search: <aliases or terms; separated by ;> @ <commit sha>`. The sha must name a commit of this repository. In `.tex` the line is a `%` comment. `whatis.py` prints such a line. The patterns are the list `ABSENCE_PATTERNS` in the script, each with an example it must fire on. They are matched on the paragraph's joined text, so a claim wrapped across lines is caught. Lines already in HEAD are not re-judged. | `absence claims carry search` (`tools/registry/absence_claims.py`); power: `absence-claims self-test` (fires on a bare claim, on a claim wrapped across two lines, on a search line naming no commit, and on a search line in another paragraph; silent with a search line, on unrelated "no", on comments and code spans) |
| 5 | **Never delete; supersede with a status.** A superseded or withdrawn result keeps its index rows. Its status is `withdrawn`/`superseded` when the receipt's file name says so, when its own top-level `status` begins with the word, or when a `STATUS.tsv` row (citing a line that holds its quote) matches. Otherwise it is `design-projection` when the receipt's OWN `status` (or, lacking one, `schema`) declares design arithmetic, or when a `STATUS.tsv` row says so. A file name alone is not enough: `r2_design.json` holds measured values. Otherwise it is `unreviewed`: no registered record withdraws or supersedes the result. That is **not** a claim that the result is current. The receipt's own `verdict` field (Tier S: `FUTILITY-FAIL`) is printed beside its status. | Partly. Statuses are generated and checked by rule 3. Deleting a receipt makes the index stale, so the check fails until the index is regenerated; at that point the rows are gone. **Not enforced:** that a receipt is never deleted from git. Nothing here can stop `git rm` plus a regenerated index. The repository's removal rules (AGENTS.md, "Pre-freeze provenance may leave main only through…") govern that. |
| 6 | **The records document holds the index, and only it does.** `main_records.tex` inputs `records_estimators` and `records_results_index`, outside comments. No posted driver's `\input` closure (`main_note`, `main_paper`, `main_primer`, `pet_note`) reaches either file. | `registry citations+labels` (`records_include_index`); power: `registry self-test` (fires when the records input is commented out, and when `main_note` inputs the index) |
| 7 | **Attribution is by citation, and by explicit key scope.** A receipt's results are attributed to an estimator only by an `ATTRIBUTION.tsv` row. The row's cited line must hold its quote **and** match one of that estimator's identifying alias patterns. Every row names the keys it covers (`keypath_regex`, e.g. `results/ours_` for the 2D LightGBM receipt, so its `data_vs_tune` comparison is not attributed); no row covers a whole receipt. A row with no such line is not kept; its results stay `UNATTRIBUTED` and listed. | `results index fresh+complete` (`load_rules`); power: `results index self-test` (a row citing a line that names (a), attributed to R, fails; the same line attributed to (a) passes) |
| 8 | **Never silently zero.** (i) A gate: an estimator with at least one attributed row in HEAD's committed index must keep at least one in the regenerated index, unless `WAIVERS.tsv` holds a row for it citing the line that says why. (ii) A disclosure: every estimator that a posted document (note, paper, primer, PET note) prints by a registered label either has an attributed row or is listed in the NO-RESULTS-INDEXED table of the records rendering (§R5.2). At this commit that table lists `b-exact-split`. | `results index fresh+complete` (`attribution_drops`, `no_results_listed`); power: `results index self-test` (dropping R's real attribution rules and regenerating fails with ATTRIBUTION LOST; a cited waiver makes it pass; emptying the NO-RESULTS-INDEXED listing fails with SILENT ZERO) |

## What the checks do not do

- **They do not decide what a receipt measured.** The index copies numbers and key paths under the family rules. A
  value under a key with a `bias` token is indexed as bias, whatever the receipt meant by it. The rules exclude
  counts (`m_residual` is a seed count, `state/s5p/recovery/s5p_recovery.py:500`; `hits68` is indexed as a hit
  count), parameters, OmniFold's step-2 pull/push weights, design keys, bin edges (`E_lo_*`), correlations and
  chi-square values. Nothing under a correlation key is indexed, and under a `chi2` key only pulls and residuals
  are. A key is a p-value only when the WHOLE key is `p`, `p_value`, `pvalue` or `null_p…`, so labels such as
  `v3_p_mult_KE20` are descended. `residency_*` and keys that are paths are also excluded. Each exclusion is named in the script and has a self-test fixture.
- **Attribution is partial.** At this branch's fourth commit it covers 678 of 4978 rows. The rest are listed as
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

## How to add an estimator, a name or a result

1. **A new estimator or a new name for one.** Add rows to `ESTIMATORS.tsv` or `ALIASES.tsv` with `source`,
   `line`, a verbatim `quote` from that line, and its `line_sha256` (`check_registry.py --cite FILE:LINE` prints
   it). Then `git add` the files and run
   `python3 tools/registry/results_index.py --write`, then `git add` its four outputs.
2. **A new receipt.** `git add` it, run `results_index.py --write`, then `git add` the four outputs. If you can
   cite the line that names its estimator, add an `ATTRIBUTION.tsv` row.
3. **A superseded result.** Add a `STATUS.tsv` row that cites the superseding record's line. Do not edit or
   delete the receipt.
