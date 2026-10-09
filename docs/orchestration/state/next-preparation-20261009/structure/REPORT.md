# Session 3 — targeted repository consolidation

| field | content |
|---|---|
| `Lane` | Session 3, structure |
| `Decision` | Which small structural changes materially simplify supported development and reproduction without changing scientific behavior or destroying independent verification? |
| `Branch` / `Base` / `Head` | `prep/next-structure-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (merged PR #61; supersedes dispatch `8eafd357` per the session prompt) / filled at delivery |
| `Owned files` | filled at delivery; the pre-edit claim is §1 |
| `Pinned inputs` | filled at delivery |
| `Resources` | filled at delivery |
| `Review` | filled at delivery |
| `Model / effort` | filled at delivery |
| `Disposition` | filled at delivery |
| `Next action` | filled at delivery |

**Status of this commit: pre-edit ownership claim only.** DISPATCH requires every implementation file
to be named here, with its caller analysis, in a pushed commit before it is edited. No source file has
been edited when this section is pushed.

## 1. Pre-edit claim: exact files and caller analysis

Measured at `5ac9706a` (= `origin/main` at 2026-10-09T19:59Z, 0 commits ahead). Ownership recheck at
20:03Z: no local or `origin` branch has commits since its merge base with `5ac9706a` that touch any
path below, and no worktree has uncommitted changes to them. No Session-2 path, 2D production driver,
pinned OmniFold helper, publication producer, receipt-bound script or other lane's namespace is
claimed.

### Family 1: 2D reported-cell identity (D's finding `O4`/`D01`)

Today four producers and consumers derive the 205-of-224 reported-cell set from four different
operands, and every junction checks only the count:

- `analyze_uq.py:117`: replica-ensemble mean > 0.
- `analyze_universes.py:208`: matched CV > 0. It block-sums the bootstrap matrix after a shape-only
  check (`:300`), and on a shape mismatch it warns and silently omits `hCov_combined`.
- `_ours_only_chi2.py:86,103,114`: paper StatOnly diagonal > 0, with shape-only checks.
- `compare_to_paper_fullcov.py:148-159`: paper mask, count-only check.

| File | Edit kind | Callers and constraints (measured) |
|---|---|---|
| `2d-unfolding/uq/reported_cells.py` | **new**: the identity contract. Cell = (pT edges, p∥ edges, C-order flat index = paper `GlobalID`); a reported set is its sorted flat indices. It reads and writes a `hReportedCells` TH2D on the grid. Pure numpy, with ROOT only inside the I/O helpers. | none yet. The name is unused in the tree (`git grep reported_cells`). |
| `2d-unfolding/uq/analyze_uq.py` | Structural: derive `reported` through the contract (same rule, mean > 0). Additive: write `hReportedCells`. No change to the mean, std, covariance, Cholesky, stdout or existing ROOT objects. | Run by `uq/rollup_vl170_adoption.sh` step 1 (the adopted VL172 chain), `uq/final_rollup_full.sh` (a, b), `sbatch_analyze_MEFHC_final.sh`, `uq/run_split_analysis.sh` and `HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh`. **Imported as `au`** by six frozen scripts that Goal 2 names (`ki84-adopt-20261006/{purity_datastream_check,recompute_2d_budget}.py`, `ki84-rebuild-20261006/{boot_spreads_vl170,compare_ki84_band,predict_ki84}.py`, `note-boot-20261003/boot_spreads.py`) and by Session 2's `coverage_fixed_truth/ki85_compare.py`. Each inserts the `uq/` directory at `sys.path[0]`, then uses only `au.th2_to_array`, `au.th1_to_array`, `au.PT_EDGES` and `au.PZ_EDGES`. **These four names keep their bytes and values.** No digest of this file is recorded anywhere (`git grep` of its sha256 prefix and blob: 0 hits). |
| `2d-unfolding/uq/analyze_universes.py` | Additive: write `hReportedCells`. **Behavior change, defective inputs only:** before the block sum, refuse unless the bootstrap's cell identity (its `hReportedCells`, else `hMean2D > 0`, which is `analyze_uq`'s own rule) equals the CV's reported cells and grid. This replaces warn-and-omit on a count mismatch and the silent sum on an equal-count permutation. On matching inputs every output is unchanged. | Run by `rollup_vl170_adoption.sh` steps 0 and 2, `final_rollup_full.sh` (c), `sbatch_analyze_MEFHC_{final,universes}.sh` and the negweight handoff script. Imported by `uq/plot_uncertainty_fig6_7_style.py` (`CATEGORY_ORDER`, `category_for_band` only; kept). Its digest `c070e852…` is recorded in `docs/sep-09-presentation/ai-research-talk/measurements/two_d_uncertainty.json` and pinned **at revision `901f2c64`** by `nd-unfolding/tests/test_hash_bindings.py:701-702`, not at current bytes (D, row N04). |
| `2d-unfolding/uq/_ours_only_chi2.py` | **Behavior change, defective inputs only:** require the bootstrap identity, and the universe identity when it is stored, to equal the paper mask's flat indices. If a legacy universe file has no stored identity, keep the count check and print a warning. | Run by `rollup_vl170_adoption.sh` step 4. Imported as `oo` by the frozen `uqpaper-median-20261006/paper_median.py` (`oo.flatten_paper`, `oo.tmatrix_to_numpy`; kept byte for byte). No digest recorded (0 hits). It is not a publication producer: 0 hits in `docs/analysis-note`, `publication`, `docs/publication` and `VALIDATION_LEDGER.md`. |
| `2d-unfolding/tests/test_reported_cells.py` | **new** small test: contract unit tests, a permutation and an omission negative control, and ROOT-gated script-level controls on synthetic files. | none |

Not edited, deferred with a specification: `compare_to_paper_fullcov.py` (a publication producer;
digest `05075acb` is recorded in `publication/release/figs/_data/fig_arrays.npz.manifest.json`) and
`uq/plot_uncertainty_fig6_7_style.py` (a note figure producer, `docs/analysis-note/make_figures.sh`).

### Family 2: 2D rollup entry points (supported vs superseded)

`uq/final_rollup_full.sh` still calls its own output "the publication-grade headline" (header,
lines 2-26). Its steps (a) and (b) rewrite two products **in place, without a refusal**:

- `uq/seedscan_lgbm_ml/uq_covariance_ml.root`, sha256 `3b6b48ec…`. This is the ML input of the
  **adopted** VL172 rollup (`ki84-adopt-20261006/recompute_2d_budget.json` `inputs.ml`; listed in
  `sha256sums_2d-unfolding_uq.txt:32`).
- `uq/bootstrap_MEFHC_300/uq_covariance_boot300.root`, sha256 `f7c734b1…`, the sha-pinned VL162 band
  (`sha256sums_2d-unfolding_uq.txt:30`).

The supported chain, `uq/rollup_vl170_adoption.sh`, refuses to overwrite.

| File | Edit kind | Callers and constraints (measured) |
|---|---|---|
| `2d-unfolding/uq/final_rollup_full.sh` | **Behavior change on purpose:** refuse before step (a) when either sha-pinned target already exists, and name the supported route. Correct the header's "publication-grade" claim to "superseded". The steps' commands and arguments are unchanged. | Called only by `2d-unfolding/sbatch_final_rollup_full.sh:16` (unchanged). Cited by `2D_OMNIFOLD_REFERENCE.md:197,206,300` and `2D_OMNIFOLD_STUDY_STATUS.md:307`. No digest recorded (0 hits). No test runs it. |

Total: **four existing implementation files** (cap: six), two new files (one module and one test),
and two families (cap: two). Reports and docs: this report, plus `README.md`,
`docs/POST_PUBLICATION_REORG_PLAN.md` and `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` (the three
dispatched documents).

Commit discipline: (1) this claim; (2) structural plus additive changes, proven equivalent; (3) the
fail-closed guards, as separate behavior commits with their negative controls; (4) documents and the
report.
