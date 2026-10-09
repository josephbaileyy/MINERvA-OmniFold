# Session 3 — targeted repository consolidation

| field | content |
|---|---|
| `Lane` | Session 3, structure |
| `Decision` | Which small structural changes materially simplify supported development and reproduction without changing scientific behavior or destroying independent verification? |
| `Branch` / `Base` / `Head` | `prep/next-structure-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (merged PR #61; the session prompt makes it supersede dispatch `8eafd357`) / the head that adds the final review record (§10); the reviewed freeze is named there |
| `Owned files` | Code: `2d-unfolding/uq/reported_cells.py` (new), `2d-unfolding/uq/analyze_uq.py`, `2d-unfolding/uq/analyze_universes.py`, `2d-unfolding/uq/_ours_only_chi2.py`, `2d-unfolding/uq/final_rollup_full.sh`, `2d-unfolding/tests/test_reported_cells.py` (new), `2d-unfolding/tests/test_final_rollup_full_refusal.py` (new). Docs: `README.md`, `docs/POST_PUBLICATION_REORG_PLAN.md`, `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`. Lane subtree: `Q/structure/` (this report, `census-*.tsv`, `checks/{equivalence,real_operands,census}.py`, `checks/nav.sh`, `logs/*`). |
| `Pinned inputs` | Code and records at `5ac9706a`. D's `disposition.md`/`dependencies.tsv` at `5ac9706a`. Read-only copies of eight adopted 2D products, each sha256-matched to its recorded digest (§3.4). Paper ancillary text `minerva_paper_anc/*.txt` (tracked). |
| `Resources` | §11 (final figures there). Cluster/GPU **0**: one read-only `ssh`/`scp` of eight named files, no job. |
| `Review` | §10 |
| `Model / effort` | Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable |
| `Disposition` | **PASS** for the structural decision, with the scope limits in §12. Reviewer verdict in §10. |
| `Next action` | §13: the publication owner's identity patch for two count-only consumers (specified in §5), with its prerequisites; and regenerating `MANIFEST.tsv` at merge. |

The overall objective (a publication-ready measurement with a reproducible central estimator, matched
uncertainty construction and validation supporting its claims) is **not** achieved by this lane. Nothing
here re-quotes, adopts, changes a gate, measures transfer or validates coverage.

## 1. Pre-edit claim: exact files and caller analysis

Pushed as `53e4f7fa` before any implementation file was edited. It is kept here unchanged except for
this line. The two new tests, `test_final_rollup_full_refusal.py` and the census, navigation and
operand scripts, are the "small relevant tests" and lane-subtree evidence the claim allows.

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

## 2. Semantic duplication, measured

`checks/census.py` counts conventions by meaning at any revision. Its output is
[`census-5ac9706a.tsv`](census-5ac9706a.tsv) (the pin) and [`census-head.tsv`](census-head.tsv) (rev
`1cc3d5d9`, after both families). It starts from D's inventory (`dependencies.tsv` rows D01–D07, N01–N19)
rather than repeating it. Classes: shared scientific logic (S), intentionally independent checker (I),
experiment-specific (X), supported entry point (E), historical evidence (H), generated product (G).

| Convention | Measured at the pin | Class and disposition |
|---|---|---|
| 2D bin edges | 23 files define a top-level `PT_EDGES`/`PZ_EDGES` literal (live 19, test 2, historical 1, handoff 1). 6 literals differ from the driver: 2 are the IBU pair (0.075/0.325/0.475, D's D03), 3 are the extended 15×19 FPS/PET grid (`fps_provenance.py`, `pet/validate_gate2_target_receipt.py`), and 1 is a toy test grid. | The two adopted UQ producers' copies become the contract's (S, **implemented**: 23 → 22, 3 importers). Checkers keep their own literals (I, kept by design). The IBU difference is scientific (§6, P1). FPS/PET is a different grid (X). |
| Reported-cell selection (2D) | 27 `'> 0'` mask assignments in live 2D code. By operand: paper StatOnly diagonal 7, another covariance diagonal 4, replica mean 4, matched CV 2, central 1, closure or diagnostic reference 9. 0 files compared cell identity rather than count. | **Implemented (family 1)**: 4 files now compare identity. The two count-only publication consumers are deferred to their owner (§5). Closure and diagnostic masks are X. |
| Covariance normalization | `np.cov` (1/(N−1)) in 10 live files; MAT mean-centered 1/N in 2 (2D and 3D universe rollups). | Intentional difference (D's D02). Not harmonized; kept. |
| 2D launcher estimator/seed | 14 `sbatch_unfold_2d*` launchers that call the driver. The central passes no `--estimator` or `--seed` (driver defaults exact, None). The bootstraps use lgbm `--seed 1 --bootstrap-seed N`. The universes and CVs use lgbm `--seed 42`. The seedscan uses **hist** `--seed ${SEED}`; the ML block came from the separate lgbm `seedscan_lgbm/` route (D's N13). The 8-iteration launcher uses hist `--seed 1`. | E or X. Every value is recorded per launcher in the census. The central's backend question is A's and E's (D's D06), not a structural edit. No launcher changed. |
| Hardcoded checkout root | 459 tracked `.py`/`.sh` files name `/pscratch/sd/j/josephrb/MINERvA-OmniFold`: live 360 (2D 81, 3D 15, N-D 264), historical 74, test 11, publication 9, handoff 5. | Not consolidated. It is the OI-136 surface and Session 2's lane. Rooting is a launch-provenance question for the guarded runner, not a refactor (§7 backlog). |
| Cross-dimensional imports | 47 files import the 2D driver (N-D 41 live + 1 test, 2D 2, 3D 1, docs 2); 14 import the 3D driver, all within 3D. | S. The driver is frozen for this lane, so not changed. |
| Generator code location | 5 `gen5d*` files of the s5p family sit under `3d-unfolding/genie/`. | D's deferred move design stays the route; recommendation: do not move. |
| ROOT reader helpers | `th2_to_array` is defined in 11 live files, `tmatrix_to_numpy` in 4, `flatten_ours` in 3. | Not consolidated. They are 5-line readers, some inside publication producers. One shared reader would couple frozen and publication code for no scientific gain. |
| Tracker-nucleon constant | 0 live literals outside the driver (D's D07). | Single definition; nothing to do. |

## 3. Family 1: 2D reported-cell identity (implemented)

**The contract** (`2d-unfolding/uq/reported_cells.py`). A cell is a (pT bin, p∥ bin) pair. Its flat
index is the C-order position in a (14, 16) [pt, pz] array, which equals the paper's
`GlobalID = (Ptbin−1)·16 + (P||bin−1)`. A reported set is the sorted index array. Two covariances over
reported bins may be summed, or embedded in the 224-cell grid, only if the arrays are equal. Producers
store the set as `hReportedCells`: a TH2D on the grid with exact edges, 1 = reported, and only the
values 0 and 1 allowed. For `analyze_uq.py` files written before this change, `read_cells` falls back
to `hMean2D > 0`, which is the rule that selected their cells.

**Commits**, each separately reviewable:

| Commit | Kind | Change |
|---|---|---|
| `88e7e4cd` | structural | Adds the contract; `analyze_uq.py`/`analyze_universes.py` import `PT_EDGES`/`PZ_EDGES` from it. Arrays bitwise and dtype-equal; `au.th2_to_array`, `th1_to_array`, `PT_EDGES`, `PZ_EDGES` kept for the seven importers. |
| `82448140` | additive output | Both producers also write `hReportedCells`. The selection rules are unchanged. |
| `40330351` | **behavior change, defective inputs only** | `analyze_universes.py --bootstrap-cov` exits before any write unless the bootstrap's set equals the CV's. This replaces a silent misaligned sum on an equal-count permutation, and a warn-and-omit on a count mismatch. `_ours_only_chi2.py` requires the bootstrap's set, and the universe file's when it is stored, to equal the paper's. A universe file with no stored set gets a printed count-only warning. |

### 3.1 Equivalence on synthetic operands (pinned scripts against edited ones)

`checks/equivalence.py` uses a fixed seed (20261009) and the paper's own 205-cell set, taken from the
tracked StatOnly text file. Each case runs both versions as subprocesses on identical inputs. It
compares stdout, every ROOT object (class, title, axis edges, every bin content and error including
flow bins, entries), every PNG byte for byte, and every PDF with `/CreationDate` removed (matplotlib
stamps the wall clock).

| State | Result over 3 `analyze_uq`, 7 `analyze_universes` and 5 `_ours_only_chi2` cases | Log |
|---|---|---|
| after `88e7e4cd` | **0 differences** of any kind, including on the defective inputs | `logs/equivalence-A1-structural.txt` |
| after `82448140` | the only difference is the added `hReportedCells` in `uq_covariance.root` and `uq_universe_covariance.root`; the stored sets are exactly the paper's 205 cells (or the permuted set for the permuted fixture) | `logs/equivalence-A2-additive{,.summary}.txt` |
| after `40330351` | matched inputs, including a legacy bootstrap read through `hMean2D`: outputs unchanged. The defective cases are below. | `logs/equivalence-B-guards{,.summary}.txt` |

### 3.2 Negative controls (permutation and omission)

| Input | Pinned scripts (`5ac9706a`) | Edited scripts |
|---|---|---|
| bootstrap with one reported cell moved to an unreported cell (205 = 205) | `analyze_universes` rc 0, **writes a misaligned `hCov_combined`** | rc 1, cells named (`100(pt7,pz5)` vs `144(pt10,pz1)`), nothing written |
| bootstrap with one cell omitted (204) | rc 0, warns, silently omits `hCov_combined` | rc 1, nothing written |
| bootstrap file with neither `hReportedCells` nor `hMean2D` | rc 0, combined | rc 1, "reported cells are unknown" |
| `_ours_only_chi2` with a permuted bootstrap, or a permuted stored universe set | rc 0, χ² printed | rc 1, cells named |
| `_ours_only_chi2` with a legacy universe file | rc 0 | rc 0, identical numbers plus one `[WARN] … checked by count only` line |

The tests in `2d-unfolding/tests/test_reported_cells.py` (16; 8 need no ROOT) cover the contract and
the scripts. **They reject the defect.** A count-only mutant of `require_same_cells` fails
`test_equal_count_permutation_is_refused`. With the pinned `analyze_universes.py` and
`_ours_only_chi2.py` swapped in, both script-level refusal tests fail (rc 0 instead of a refusal), and
the matched-input test passes on both versions (`logs/guard-tests-against-pinned-scripts.txt`). The
grid test compares the contract with two copies it is not derived from: the driver's literal, read
with `ast`, and `minerva_paper_anc/bin_mapping.txt`.

### 3.3 Callers checked

- An import smoke test of every importer pattern passed (Homebrew Python 3.13, PyROOT 6.36, numpy 2.4.4,
  matplotlib 3.11.2 in a scratch venv). The pattern is `uq/` at `sys.path[0]`, then `import analyze_uq`
  and `_ours_only_chi2` exactly as the six frozen records, `paper_median.py` and `ki85_compare.py` do.
  Every name they use resolves, and the edges are bitwise and dtype-identical to the pin.
- `plot_uncertainty_fig6_7_style.py --help` and both producers' `--help` exit 0.
- The note figure producer (unchanged file, edited `analyze_universes` import) was run on the adopted
  inputs. It reproduces the tracked
  `ki84-adopt-20261006/products/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/MEFHC_fig6_7_uncertainty_summary.txt`
  exactly; only the input-directory prefixes differ.
- Session 2's `test_coverage_fixed_truth.py` does not import any changed module (`grep`). `ki85_compare.py`
  imports `analyze_uq` through the cluster path at run time, so only the name check above applies to it.

### 3.4 Real operands: the adopted 2D chain is cell-aligned

`checks/real_operands.py`, log `logs/real-operands.txt`. Eight products were copied read-only from
`saul.nersc.gov:/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/` with one `scp` each (29 MB in
total; no job, no compute). Each copy's sha256 equals its recorded digest:

- the VL170 bootstrap `71a75821`;
- the VL162 bootstrap `f7c734b1`;
- the ML block `3b6b48ec`;
- the matched CV `4f5a1b6d`;
- the VL172 universe file `077912e3`;
- the VL162 universe file `62590df7`;
- the frozen central `142a45b0`;
- the paper ROOT `6c6dce72`.

| Operand, under its producer's or consumer's rule | n | equal to the paper's cells, cell by cell |
|---|---:|---|
| paper StatOnly diagonal > 0 (ROOT; tracked text) | 205; 205 | yes; yes |
| VL170, VL162 and ML `hMean2D > 0` (`analyze_uq`) | 205 each | yes |
| matched CV `hXSec2D > 0` (`analyze_universes`) | 205 | yes |
| frozen central `hXSec2D > 0` (Fig. 6/7) | 205 | yes |
| VL172 and VL162 universe `hSigma_universe_total > 0` (proxy) | 205 each | yes |

So the new guard accepts the adopted inputs, and re-running the adopted rollup is not blocked. The
edited `_ours_only_chi2.py`, run on the VL172 universe file and the VL170 bootstrap (rollup step 4),
prints every line of the tracked `ours_only_chi2.txt` and one added disclosure warning. That record's
χ²/ndf `24.400` matches. It is the ours-only diagnostic, not the quoted paper-comparison number.

This turns D's statement that "today the cells coincide" from a documentary reading into a
measurement on these operands. It is an indexing check. It is not a scientific validation of any
covariance.

## 4. Family 2: the superseded 2D rollup entry point (implemented)

`1cc3d5d9`, a behavior change on purpose. `uq/final_rollup_full.sh` called its output "the
publication-grade headline". Its steps (a) and (b) rewrote two sha-pinned products in place:
`uq/seedscan_lgbm_ml/uq_covariance_ml.root` (`3b6b48ec`), the ML input of the adopted VL172 rollup
(`recompute_2d_budget.json` `inputs.ml`), and `uq/bootstrap_MEFHC_300/uq_covariance_boot300.root`
(`f7c734b1`, VL162). The supported `uq/rollup_vl170_adoption.sh` refuses to overwrite. The script now
says it is superseded and names the supported route. It exits 2 before any write while either product
exists. Its steps and arguments are unchanged. The sbatch wrapper `sbatch_final_rollup_full.sh` is
unchanged.

`2d-unfolding/tests/test_final_rollup_full_refusal.py` runs the script in a throwaway tree that
satisfies its preconditions, with a stub `python` that only records its arguments:
- with either product present, the script refuses and no step runs;
- with neither present, the script runs;
- the control runs the pinned script, which reaches step (a) with the product present.

The refusal test fails against the pinned script (`logs/rollup-refusal-test-against-pinned-script.txt`).
Workflow improvement: the one route that could silently replace an input of the adopted budget is
closed, and the script's own header no longer contradicts the reference.

## 5. Deferred patch specification: the two count-only consumers (not applied)

`2d-unfolding/compare_to_paper_fullcov.py` (publication producer; digest `05075acb` in
`publication/release/figs/_data/fig_arrays.npz.manifest.json`) and
`2d-unfolding/uq/plot_uncertainty_fig6_7_style.py` (note figure producer, `make_figures.sh`) still align
by count. This lane may not edit them.

**Change.**
- `compare_to_paper_fullcov.py:load_omnifold_cov`, after opening `path`: call
  `reported_cells.read_cells(f, mean_fallback="hMean2D")`. If a set is returned,
  `require_same_cells(np.where(reported_mask)[0], cells, "paper StatOnly", spec)`; on mismatch, raise
  `SystemExit` naming the cells. If none is returned (the VL172 universe file), keep the count check and
  print one `[WARN] … count only` line.
- `plot_uncertainty_fig6_7_style.py`: replace the `WARN` at `:106-108` with the same comparison of
  `xsec > 0` against each loaded covariance file's set; refuse on mismatch.

**Behavior contract.** On the adopted inputs every set equals the paper's (§3.4). So every number,
χ² log and figure must be unchanged, apart from the one new warning line for the legacy universe file.

**Prerequisites and owner.** The publication owner, not this lane. Required:
- equivalence on the frozen inputs: rollup steps (3) and (5) before and after, logs identical apart
  from the warning;
- an update to the producer digest in `fig_arrays.npz.manifest.json`;
- the three builds and the standalone synchronization if any figure source changes. None should.

The identity of the adopted `hCov_combined` can only be stored by re-running `analyze_universes.py`
into a new directory, which makes a new product. That is not authorized and is not needed for the
check above.

**Reopening authority.** The publication-correction owner or Joseph. Until then, the count check plus
§3.4's measurement is what protects the adopted chain.

## 6. Behavior-change proposals, labeled separately (none applied)

| # | Proposal | Why it is not a refactor |
|---|---|---|
| P1 | `2d-unfolding/ibu_omnifold_paired_cdelta.py` and `ibu_1d_projection/build_1d_ibu_inputs.py` bin at pT edges 0.075/0.325/0.475, where the driver and `bin_mapping.txt` use 0.07/0.33/0.47 (D's D03; census row 2). | Changing the edges changes that closed study's numbers. Its owner decides whether the difference was intended. Only that study is affected. |
| P2 | `analyze_uq.py` and `analyze_universes.py` could also check every input `hXSec2D`'s axis edges against the grid. | This refuses inputs the current code accepts, and production edges were not measured for all 187 universes. Proposed, not applied. |
| P3 | `sbatch_analyze_MEFHC_{final,universes}.sh` could get `final_rollup_full.sh`'s refusal. | Their glob mixes the Stage-1 and full sweeps, and they overwrite unpinned outputs. The lane's file allowance went to the two families. See the reorganization plan, "Removal candidate, not proposed". |

## 7. Bounded remaining backlog

1. §5's patch, with the publication owner.
2. P1, with the IBU study's owner. P2 and P3, as a later structure lane, each with the §3.2 style of
   negative control.
3. Hardcoded `/pscratch` roots (360 live files). Route through Session 2's guarded-launch work; it is
   not a refactor.
4. The status headline's backend label for the central value (D's D06). A, B and E's routing
   decision.
5. `MANIFEST.tsv` regeneration at merge (§13).

No broad reorganization, historical removal, publication change or scientific claim follows.

## 8. Verification

| Check | Result |
|---|---|
| pre-commit (shared `.githooks`) on every commit of the branch | 13 checks passed, every commit. In one rejected attempt, the receipt-artifact check read a `.json` log citing scratch `.root` outputs as receipts; the logs are now JSON content in `.txt` files, and the outputs stayed in scratch (stated in `88e7e4cd`'s message). |
| `test_reported_cells.py` | 16 passed with ROOT and matplotlib; with the system `python3` (no ROOT), 16 run and 8 skipped |
| `test_final_rollup_full_refusal.py` | 3 passed |
| `python3 docs/orchestration/verify_hash_bindings.py` | rc 0, ALL BINDINGS INTACT |
| `pytest nd-unfolding/tests/test_hash_bindings.py` (inspected: verifier subprocesses and synthetic temp repos) | 33 passed |
| OI-136 ratchets (both files) | 2 failed, 15 passed: **pre-existing**. The two set-membership tests list the nine October sites of `KNOWN_ISSUES.md` 89 (Session 2's disposition). None is a file this lane changed, and this lane added no rooted insert. |
| `generate_manifest.py --check --at-sha 5ac9706a` | OK at the pin |
| `generate_manifest.py --check` at head | OUT OF DATE, from integration only: new rows for this lane's `Q/structure/` files, plus the `consumer`/`inbound_count` columns of existing rows these files cite. No override is needed (the report row is pre-registered `MACHINE open`). §13. |
| `checks/nav.sh` | every hop resolves (`logs/nav.txt`); its MISSING branch fires on an absent string |
| Real operands, the Fig. 6/7 reproduction, the import smoke test | §3.3 and §3.4 |
| `test_bootstrap_completeness_ki84.py` | not run: it exercises the driver, which this lane did not touch |

## 9. Limitations

- Equivalence is shown on synthetic inputs for the full scripts, and on real inputs for cell identity,
  `_ours_only_chi2` and the Fig. 6/7 summary. The full universe rollup was not re-run on the 187
  production sweep files, because that would be a bulk copy.
- "Bitwise" covers ROOT bin contents and errors, stdout text, summary text and PNG bytes. PDFs are equal
  only after removing `/CreationDate`. Raw ROOT file bytes differ between any two runs (timestamps and
  UUIDs), so they were never compared.
- The guards protect future runs of the edited scripts only. The frozen records run at their own pins,
  and the publication consumers stay count-only until §5 lands.
- Local timing is not a Perlmutter measurement.

## 10. Independent review

Pending at the freeze commit; filled in after the review.

## 11. Resources

| Resource | Used | Cap |
|---|---|---|
| Active elapsed | 19:59Z → delivery; about 0.6 h before the review | 6 h |
| Local CPU | under 0.5 core-h. Largest steps: 3 harness runs at about 70 s user each, the hash-binding tests at 87 s, the OI-136 ratchets at about 80 s, the guard tests at about 25 s ×2. Every command was capped at 2 threads. | 3 core-h |
| Peak RAM | under 0.5 GiB (harness max RSS 0.49 GB) | 8 GiB |
| Scratch | 0.20 GiB (venv 84 MB, product copies 29 MB, harness work dirs) | 1 GiB |
| Tracked bytes added | about 0.12 MiB net | 10 MiB |
| Cluster node-hours, GPU, training, toys | 0. Cluster contact: one `ls`/`sha256sum` and eight `scp` reads of named products. | 0 |
| Families / existing implementation files edited | 2 / 4 | 2 / 6 |

## 12. Disposition

**PASS** for the decision, within these limits:
- Two small structural changes measurably simplify and protect supported reproduction:
  - the reported-cell identity contract, which turns four count-only junctions into explicit,
    tested identity checks in the adopted UQ chain;
  - the superseded rollup's refusal, which closes the one route that could overwrite an input of the
    adopted budget.
- Both are proven equivalent on matching inputs. Synthetic inputs show bitwise equality. Real inputs
  show cell identity, the `_ours_only_chi2` record and the Fig. 6/7 summary.
- Their negative controls reject the defect.
- Independent checkers and frozen paths are untouched.
- Every prioritized finding (D's O4/D01, the entry-point hazard, D03, D06, the `/pscratch` roots and the
  `gen5d` location) is implemented or deferred precisely.

It does not establish:
- coverage, transfer or any uncertainty's validity;
- publication readiness;
- adoption;
- that the two count-only publication consumers check identity (§5).

## 13. Next action and integration patch

1. **Merge decision (Joseph).** This draft PR is structural code plus documentation. Merging changes
   no product and no number.
2. **Integration owner, at merge.** Regenerate `docs/orchestration/MANIFEST.tsv` from source with
   `python3 docs/orchestration/generate_manifest.py`. Do not hand-merge it. No `CATALOG.md` or
   `MANIFEST-overrides.tsv` change is needed. If another lane merges first, regenerate after both.
3. **Publication owner.** §5's patch, priced as about 1 h of local work plus the rollup steps (3) and (5)
   equivalence on frozen inputs (minutes of login-node CPU, no training), the producer-digest update and
   the builds. Its acceptance criterion is §5's behavior contract.
4. **Shared-register owner.** No `KNOWN_ISSUES`/`OPEN_ITEMS` row is required. Optional one-line text for
   the 2D status, if wanted: *"2026-10-09: the adopted 2D chain's reported cells were measured equal,
   cell by cell, across all nine operands (`state/next-preparation-20261009/structure/REPORT.md` §3.4);
   `analyze_universes.py` now refuses a cell mismatch."*
