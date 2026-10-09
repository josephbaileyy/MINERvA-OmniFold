# Publication correction — keep and disclose (2D estimator pairing)

| field | content |
|---|---|
| `Lane` | publication correction (assigned by Joseph 2026-10-09 after Session 1's §11 ruling) |
| `Decision` | Are the paper, note and primer factually consistent about the frozen central estimator, the uncertainty estimators, seed provenance and unmeasured transfer, without claiming that disclosure has established publication readiness? |
| `Branch` / `Base` / `Head` | `prep/next-publication-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (merge of PR #61; equal to `origin/main` at 2026-10-09T19:58Z) / IN PROGRESS |
| `Owned files` | claimed below, before any edit |
| `Pinned inputs` | IN PROGRESS |
| `Resources` | IN PROGRESS |
| `Review` | IN PROGRESS |
| `Model / effort` | owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | IN PROGRESS |
| `Next action` | IN PROGRESS |

`Q` = `docs/orchestration/state/next-preparation-20261009`.

## 0. Claimed files (recorded before editing)

Ownership observed at 2026-10-09T20:00Z: no worktree had uncommitted changes to any path below
(`git status --porcelain` in all 20 worktrees; the guard lane's new worktree was mid-checkout and owns
none of them); no local or `origin` branch ahead of the base touches `docs/analysis-note/`,
`KNOWN_ISSUES.md`, `docs/publication/`, `CATALOG.md` or `MANIFEST-overrides.tsv` except branches last
touched on or before 2026-10-05, which are not live claims; no open PR. The standalone repository's
`origin/main` `ad3fb80` is blob-identical to the base's `docs/analysis-note/` in every tracked file
except its own `.gitignore` and `AGENTS.md`.

Canonical repository, this branch:

- `docs/analysis-note/paper_body.tex`
- `docs/analysis-note/primer_body.tex`
- `docs/analysis-note/sec_method.tex`
- `docs/analysis-note/sec_systematics.tex`
- `docs/analysis-note/sec_results.tex`
- `docs/analysis-note/sec_validation.tex`
- `docs/analysis-note/sec_execsummary.tex`
- `docs/analysis-note/sec_intro.tex`
- `docs/analysis-note/sec_summary.tex`
- `docs/analysis-note/app_statmethods.tex`
- `KNOWN_ISSUES.md`, row 88 only
- `docs/publication/CLAIMS-20261005-claim-to-evidence.md` (a dated status section only)
- `docs/publication/submission/PACKAGE-MANIFEST-20261006.md` (a dated status note only)
- `Q/publication/` (this report and its minimal evidence)
- `docs/orchestration/CATALOG.md` (one route row), `docs/orchestration/MANIFEST-overrides.tsv` (one
  row), `docs/orchestration/MANIFEST.tsv` (regenerated from source only)

Standalone `MINERvA-OmniFold-Analysis-Note`: the same `docs/analysis-note/` files, on a new branch
`sync-publication-correction-20261009` in a new isolated worktree.

Not touched: frozen audits, receipts, `publication/release/preservation/`, other lanes' `Q/` subtrees
and reports, scientific registers other than KI-88.
