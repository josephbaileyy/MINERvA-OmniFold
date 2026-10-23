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
| "Where is every result on estimator X?" | `python3 tools/registry/whatis.py "X"` |

## The rules

| # | Rule | Enforced by (pre-commit run name, `.githooks/pre-commit`) |
|---|---|---|
| 1 | **Registry integrity.** Every estimator definition and every alias cites `file:line`, and the cited line holds the row's quote word for word. A moved line is re-pointed (`check_registry.py --repoint`). A row is never dropped to make the check pass. | `registry citations+labels` (`tools/registry/check_registry.py`); power: `registry self-test` |
| 2 | **Registry completeness.** Every estimator label printed by the paper, note, primer or records document resolves to exactly one registered estimator. The label patterns are the explicit list `LABEL_PATTERNS` in the script: "configuration (x)", the paper's findings-table Conf. cells, the first cells of the estimator tables, and "candidate/family/baseline X". Labels outside that list are **not checked**. Names a source uses without mapping them to an estimator go in `UNRESOLVED-NAMES.tsv` and are reported, not guessed. | `registry citations+labels`; power: `registry self-test` (a planted unregistered name and a planted two-way registration both fire; registered labels stay silent) |
| 3 | **Index freshness and completeness.** The committed index equals a fresh generation from the staged receipts. Every receipt in the declared population has rows. The population is a rule (the docstring of `tools/registry/results_index.py`): a tracked JSON under `docs/orchestration/{state,receipts,runs}/` in which a key fully matching one of the listed metric families (coverage 68/95, coverage, pull SD, pull mean, max \|pull\|, bias, closure, residual) holds numbers. Every run prints the counts included, excluded and outside the roots. | `results index fresh+complete` (`results_index.py --check`); power: `results index self-test` (a planted result receipt fails; a planted non-result JSON and a result JSON outside the roots pass) and `tools/registry/test_registry.py` (15 fixture tests, run by hand: 40 s, over the hook's budget) |
| 4 | **Absence claims carry their search.** An added or changed line of a `docs/orchestration/**/*.md` record, or of printed `docs/analysis-note/*.tex` prose, that asserts a result is absent must sit in a paragraph with a search line: `Search: <aliases or terms; separated by ;> @ <commit sha>`. The sha must name a commit of this repository. In `.tex` the line is a `%` comment. `whatis.py` prints such a line. The patterns are the list `ABSENCE_PATTERNS` in the script, each with an example it must fire on. Only the staged diff is judged; lines already on `main` are not re-judged. | `absence claims carry search` (`tools/registry/absence_claims.py`); power: `absence-claims self-test` (fires on a bare claim, on a claim whose search line names no commit, and on a search line in another paragraph; silent with a search line, on unrelated "no", on comments and code spans) |
| 5 | **Never delete; supersede with a status.** A superseded or withdrawn result keeps its index rows. Its status is `withdrawn`/`superseded` when the receipt's file name says so, when its own top-level `status` begins with the word, or when a `STATUS.tsv` row (citing a line that holds its quote) matches. Otherwise the status is `unreviewed`: no registered record withdraws or supersedes the result. That is **not** a claim that the result is current. | Partly. Statuses are generated and checked by rule 3. Deleting a receipt makes the index stale, so the commit fails until the index is regenerated; at that point the rows are gone. **Not enforced:** that a receipt is never deleted from git. Nothing here can stop `git rm` plus a regenerated index. The repository's removal rules (AGENTS.md, "Pre-freeze provenance may leave main only through…") govern that. |
| 6 | **The records document holds the index.** `main_records.tex` inputs `records_estimators` and `records_results_index`, outside comments. The posted note, primer and paper do not. | `registry citations+labels` (the `records_include_index` clause); power: `registry self-test` (an input commented out fires) |
| 7 | **Attribution is by citation.** A receipt's results are attributed to an estimator only by an `ATTRIBUTION.tsv` row whose cited line names that estimator. Everything else is `UNATTRIBUTED` and stays listed. | `results index fresh+complete` (each row's quote is checked on its line) |

## What the checks do not do

- **They do not decide what a receipt measured.** The index copies numbers and key paths. A value under a key
  named `bias` is indexed as bias whatever the receipt meant by it.
- **Attribution is partial.** At `a84697f3` it covers 457 of 1866 rows. `whatis.py` lists receipts that mention
  an alias but carry no row attributed to that estimator. Read those receipts before claiming a result is
  absent.
- **The population covers the listed metric families only.** p-values, χ², σ and power are outside it, and so
  are receipts outside the three roots, such as `nd-unfolding/pet/**` (158 tracked `*receipt*.json` there at
  `a84697f3`).
- **Shared aliases do not identify an estimator.** Examples are `--bkg-mode negweight-refined` (d, e and the
  2D exact-split study) and `400/31` (R's refinement classifier and s5p configuration 3's OmniFold estimators).
  `whatis.py` reports them as ambiguous, and the records document lists them in §R5.

## How to add an estimator, a name or a result

1. **A new estimator or a new name for one.** Add rows to `ESTIMATORS.tsv` or `ALIASES.tsv` with `source`,
   `line` and a verbatim `quote` from that line. Then `git add` the files and run
   `python3 tools/registry/results_index.py --write`, then `git add` its four outputs.
2. **A new receipt.** `git add` it, run `results_index.py --write`, then `git add` the four outputs. If you can
   cite the line that names its estimator, add an `ATTRIBUTION.tsv` row.
3. **A superseded result.** Add a `STATUS.tsv` row that cites the superseding record's line. Do not edit or
   delete the receipt.
