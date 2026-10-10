# Independent review, cycle 1 — Session 3 (structure), commit f0deb0be

Reviewed: `prep/next-structure-20261009` at `f0deb0be31bcd52d7aa666c8993d542cff6ca868`, full delta from the pin
`5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (9 commits, 26 files). I worked read-only in the clean review worktree.
Scratch: `.../scratchpad/structure-20261009/review/`.

**Verdict: ACCEPT WITH MINOR FINDINGS.** I found no semantic regression, no scope violation and no material
defect. The guards fire on the defects and stay silent on matched inputs, both on my own fixtures and on
the real adopted operands. The findings below are about test coverage, wording and one omission in the
caller analysis.

## Findings

1. **MINOR: two guard paths can be removed without failing any tracked test.**
   I ran mutants in a scratch mirror against `2d-unfolding/tests/test_reported_cells.py`:
   - **Caught.** M1, a count-only `require_same_cells`, failed 3 tests. M2, an F-order ravel, failed 6.
     M4, no 0/1 check, failed 1. M7, no edge check, failed 2.
   - **Not caught: M3.** I deleted the universe-identity `require_same_cells` in `_ours_only_chi2.py:116-117`.
     All 16 tests still passed.
   - **Not caught: M6.** I made `analyze_universes.load_bootstrap_cells` (`:150`) drop `mean_fallback="hMean2D"`.
     All 16 tests still passed. That mutant refuses every legacy bootstrap. Every real adopted bootstrap
     is legacy, so step 0 of `rollup_vl170_adoption.sh` (`BOOT_OLD`) would break with no test going red.
   - **Harness-only paths.** The omission refusal, the refusal when no cell identity is stored, the
     shape refusal and the `_ours_only` legacy WARN path have no tracked test. They rest only on the
     lane-local harness logs. The tests that do exist test what they claim and launch no real work.
   - **Rollup test gap.** `test_final_rollup_full_refusal.py` does not check that the refusal comes
     before `archive_old_full_rollup` (an `mv`, `final_rollup_full.sh:91-113`). A guard moved below
     the archive call would still pass. No archived target is sha-pinned, so the impact is low.
   - *Fix:* add a `ScriptGuardTest` case for a universe file whose `hReportedCells` is permuted. Add a
     matched block-sum case with a legacy bootstrap that has `hMean2D` and no `hReportedCells`.
     Optionally place an archive-target file in the rollup test and assert that it was not moved.

2. **MINOR: "nothing written" overstates the refusal by one empty directory.**
   - `analyze_universes.py:190` calls `os.makedirs(args.outdir)` before the identity refusal at `:228-237`.
   - Observed: every refused run (permuted, omitted, no identity, shape mismatch) exits with rc 1 and
     leaves an empty `--outdir`. No file is written.
   - This affects REPORT §3.1/§3.2 ("nothing written") and the commit `40330351` text ("exits before any write").
   - *Fix:* say "no output file is written", or move the check above `makedirs`.

3. **MINOR: some report and doc wording goes beyond the evidence (no adoption or validation overclaim found).**
   - (a) **"Four junctions" (§12).** The text says the contract "turns four count-only junctions into
     explicit, tested identity checks in the adopted UQ chain". Three junctions are guarded:
     analyze_universes bootstrap vs CV, and `_ours_only` universe and bootstrap vs paper. One of the
     three has no tracked test (finding 1). The junctions behind the quoted numbers are still count-only
     (`compare_to_paper_fullcov.py`, step 3; Fig. 6/7, step 5). §5 and §12's "does not establish" list
     disclose this, but the headline sentence reads as more.
   - (b) **Lost qualifier.** `2D_OMNIFOLD_REFERENCE.md:224` and the §13 register text say "all nine
     operands' sets were measured equal cell by cell". They drop §3.4's qualifier that the two
     universe-file sets were read through the `hSigma_universe_total > 0` proxy. The ordering is pinned
     through the matched CV, which was measured directly.
   - (c) **Line added to §1.** It says "The two new tests, `test_final_rollup_full_refusal.py` and the
     census…", which is garbled: it names one test plus scripts. That test file is also not named in
     the pre-edit claim `53e4f7fa`. It is arguably covered by "small relevant tests", and it is disclosed.
   - (d) **"Derive through the contract."** The pre-edit claim says `analyze_uq` will "derive
     `reported` through the contract". The code keeps the old mask and adds a second, parallel
     derivation (`analyze_uq.py:115/117`, `analyze_universes.py:221/223`). The two are equal by
     construction, but the selection rule is still computed twice per producer.
   - *Fix:* reword these four places.

4. **MINOR: the caller analysis misses one consumer of `analyze_universes.py`.**
   - Not in §1: the 3D E_avail-marginal rollup. It is named in `3d-unfolding/sbatch_unfold_3d_MEFHC_5iter_universes_full.sh:26-27`,
     `3d-unfolding/3D_SYSTEMATIC_UQ_PLAN.md:108`, and the lane's own README row.
   - Its `hXSec2D` uses u2d's 14×16 grid (`unfold_3d_omnifold_unbinned.py:58-59`), so the only effect
     is the added `hReportedCells`.
   - Off-grid input is not a regression. On a 14×15 fixture both versions exit rc 1: the edited one
     with `CellIdentityError` at `:223`, the pinned one with a matplotlib `ValueError` later.
   - *Fix:* add the 3D route to §1's caller list.

5. **INFO: the edge arrays are now one shared object.**
   - `analyze_uq.PT_EDGES is analyze_universes.PT_EDGES` is now True (False at the pin), so the edges
     are one shared, writable ndarray.
   - My grep found no in-place mutation by any importer, so this has no effect today.
   - *Optional hardening:* `setflags(write=False)` on the arrays in `reported_cells.py`.

## Independently verified

- **Scope and ownership.**
  - The delta touches exactly 7 code/test files (4 existing implementation files + `reported_cells.py`
    + 2 tests), the 3 dispatched docs and `Q/structure/`.
  - Untouched: the 2D driver, `omnifold.py`, `compare_to_paper_fullcov.py`,
    `plot_uncertainty_fig6_7_style.py`, the seven frozen scripts, CATALOG/MANIFEST*, registers,
    Session 2 paths and the verify_hash_bindings constants.
  - The `origin` reflog shows `53e4f7fa` pushed at 13:05:51 −0700, before the first code commit
    `88e7e4cd` (13:14). That pre-edit claim names all 4 existing files. §1 at head equals `53e4f7fa`
    apart from one added paragraph.
- **The structural commit `88e7e4cd` changes no behavior.** It only replaces two edge literals with an
  import. The edges are bitwise and dtype-equal (float64). The importer names `au.th2_to_array`,
  `th1_to_array`, `PT_EDGES` and `PZ_EDGES`, `oo.flatten_paper` and `tmatrix_to_numpy`, and
  `CATEGORY_ORDER` and `category_for_band` all resolve at both revisions.
- **Recorded digests.**
  - The pinned `analyze_uq.py`, `_ours_only_chi2.py` and `final_rollup_full.sh` sha256 values and blob
    ids have 0 hits in the tree.
  - `analyze_universes.py` = `c070e852…` has 2 hits: `two_d_uncertainty.json` and
    `test_hash_bindings.py:702`, which pins it at `_REV_901F`.
  - `verify_hash_bindings.py` passes (rc 0, ALL BINDINGS INTACT).
- **My own synthetic old-vs-new comparison.**
  - Setup: my own generator (seed 99173), a different zero pattern (last p∥ column, a 2×3 corner, 9
    scattered cells; 196 reported) and 7 replicas.
  - Universes: 5 bands, including an N=1 band that is skipped and a `full_` prefix.
  - `analyze_uq`: the ROOT objects are identical apart from the added `hReportedCells`. The 4 PNGs are
    byte-identical, and stdout differs only in output paths.
  - `analyze_universes`, 3 cases: (`--add-norm` + `--shrinkage`), (legacy bootstrap through `hMean2D`),
    (`--legacy-pair-formula` + bootstrap with identity). Stdout is identical, every ROOT object is
    identical apart from the added `hReportedCells`, and the PNGs and summary text are byte-identical.
- **Permuted and defective inputs.**
  - Equal-count permutation (196 = 196, cell 40 moved to 47). The pinned version exits rc 0 and writes
    a misaligned `hCov_combined`; its COMBINED median is 6.768% for the legacy file and 6.621% with
    `hReportedCells`. The edited version exits rc 1, names `40(pt3,pz9)` and `47(pt3,pz16)`, and
    writes no file.
  - Omission (195): the pinned version warns and omits the combined covariance; the edited one refuses.
  - No stored identity: the pinned version sums; the edited one refuses.
  - Covariance shape that contradicts the file's own set: the pinned version warns; the edited one refuses.
- **Real operands.** All 8 sha256 values match the recorded digests (`142a45b0`, `6c6dce72`,
  `4f5a1b6d`, `077912e3`, `f7c734b1`, `62590df7`, `71a75821`, `3b6b48ec`). With my own reader, every
  set below has n = 205 and equals the paper's set:
  - paper StatOnly diag > 0, and paper xsec > 0 on the 16×14 histogram transposed to [pt,pz] (this
    confirms TMatrix index = GlobalID);
  - the tracked `_stat.txt`;
  - VL170, VL162 and ML `hMean2D > 0`;
  - matched CV `hXSec2D > 0` and central `hXSec2D > 0`;
  - VL172 and VL162 `hSigma_universe_total > 0`.
  No operand has NaN or negative cells, and every `hCov` is 205×205. This confirms §3.4.
- **`_ours_only_chi2` on real inputs (VL172 universe + VL170 bootstrap).** The pinned output is
  identical to the tracked `ours_only_chi2.txt`. The edited output is the same plus one `[WARN]` line
  (χ²/ndf = 24.400). An equal-count permuted real bootstrap, or a universe file with a permuted
  `hReportedCells`, gives rc 0 for the pinned script and rc 1 for the edited one, with the cells named
  (`151(pt10,pz8)` vs `178(pt12,pz3)`). A matched stored identity gives rc 0 and 24.400.
- **Fig. 6/7 producer.** Run unchanged with the edited `analyze_universes` import on the real VL172
  inputs, it reproduces the tracked summary (only path prefixes differ).
- **Other consumers.** The only other script that iterates the output keys (`plot_uncertainty_sources.py`)
  filters on the `hCov_universe_` prefix, so it does not see `hReportedCells`.
- **Tests and checks.** `test_reported_cells.py` passes 16/16 and `test_final_rollup_full_refusal.py`
  passes 3/3 (venv with ROOT + matplotlib).
  - `generate_manifest --check --at-sha`: OK at the pin, OUT OF DATE at head. The only differences are
    the 16 new `Q/structure/` rows plus consumer/inbound columns, as stated.
  - OI-136 ratchets: they fail only on the 9 named October sites, none of them a lane file.
  - The lane adds no rooted insert.
- **Report §2 counts I re-measured.** 459 `/pscratch` `.py`/`.sh` files; 23 → 22 files with top-level
  edge assignments; 47 and 14 driver importers; `th2_to_array` in 11 files; `tmatrix_to_numpy` in 4.

## Not verified

- The census's 27 `> 0` mask classification, the launcher seed table and the 6-literal breakdown.
- The pre-commit runs.
- The author's harness cases (§3.2 cell numbers `100`/`144`).
- `nd-unfolding/tests/test_hash_bindings.py` (I ran the verifier only).
- Anything on the cluster, including the state of the cluster checkout that the frozen records import from.

## Resources

About 40 min of wall time, roughly 0.1 core-h (about 9 test-suite runs of about 20 s each, plus small
script runs), all capped at 2 threads. Peak RAM was well under 1 GiB. No network, cluster or GPU use.

`git -C /Users/josephbailey/local-research/MINERvA-OmniFold-next-structure-review-20261009 status --short`:
(empty; `--ignored` is also empty)
