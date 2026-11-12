# COV2D-G2R AMENDMENT 1: the code of §9 (the driver's --miss-map, the prepare, the readout), with tests and mutants (2026-11-11)

**By** the `cov2d` session, for `coverage-5b-audit` to audit and the director to bind as a code addendum to
[`COV2D-G2R-DECLARATION.md`](COV2D-G2R-DECLARATION.md) (bound at M_G2R `03037c3ebcb21d38e80e4247998f48c787bc56ec`,
binding PR #1080). **DRAFT: nothing has run on the cluster.**

**MEASURES:** nothing. Every number below is a test result on synthetic fixtures.

**CANNOT AUTHORIZE:** any job. The job scripts, the cluster-environment test, the connects and the cap gate come in a
second addendum, each with the director's go, after LL5D's gates end. No change to any bound COV2D, RE-2 or T2A function.

**CITABLE FOR:** the code at the digests in §1, and what each test and mutant shows. **NOT CITABLE FOR:** any reading.

## 1. What changes

| file | change |
|---|---|
| `2d-unfolding/re2/re2_driver.py` | **patched**, every line marked `# G2R`: P5's loader change carried over (`collect_signal_arrays_2d(..., miss_weight_override=None)`, its two guards and its count), a `--miss-map NPZ` flag, and `g2r_miss_override`, which builds the per-entry override from the map and the universe's own `mc_truth_denom` column. With the flag absent, the driver is unchanged in behaviour (G1). The output records `g2rMissMap` (map path, sha256, universe, counts). |
| `2d-unfolding/cov2d/g2r/g2r.py` | **new.** The pure functions: `build_map` (P5's alignment checks), `universe_check` (P5's per-universe checks), `override`, the readings (`epsilon`, `corr_change`, `rank`, `readings`) and `c_t_prime`. |
| `2d-unfolding/cov2d/g2r/g2r_prepare.py` | **new.** §6 step 1: the map from `$UNI` and the per-universe checks for all 175 columns, every read through `O_NOATIME` (uproot over `cov2d_receipt.open_noatime`, as COV2D's step A reads `$UNI`). |
| `2d-unfolding/cov2d/g2r/g2r_readout.py` | **new.** Phase `data` (part (a), §3) and phase `tune` (part (+), §4-§5), glue over the bound COV2D modules (`cov2d_blocks`, `cov2d_null`, `cov2d_score`, `cov2d_readouts`, `cov2d_readout`'s `Run`, `read_pinned`, `cholesky_tol`, `null_from_json`), the rollup (`universe_block`, `band_cov`) and `re2c_build_q.metrics`, all imported unchanged. |
| tests | `2d-unfolding/cov2d/g2r/tests/test_g2r.py` (24 tests), `2d-unfolding/re2/tests/test_re2_miss_map.py` (8), `2d-unfolding/cov2d/g2r/tests/g2r_mutation.py` (15 mutants). |

Digests (sha256) at the code commit `2f6dac56a2382f9decf098eb309ed6683af0caed`, the commit the receipts were made at:

| file | sha256 |
|---|---|
| `2d-unfolding/re2/re2_driver.py` | `8abee6347313105e5189031bdea78b78aa9f4bbc8f00a681e8871e272df3860e` |
| `2d-unfolding/cov2d/g2r/g2r.py` | `dbcc416d35565c183d73d6ce03a9efa89dddf8cbda618fa3e6eb00bbe08d28ec` |
| `2d-unfolding/cov2d/g2r/g2r_prepare.py` | `bb97fba12034e39c4b6dd5679b93f8259bcc4fab2b69890931c95c1311c7eb57` |
| `2d-unfolding/cov2d/g2r/g2r_readout.py` | `7dd1b7eb2f971f7243f43b90d4d9aa51a836857390b7d464a4d39c362917c900` |
| `2d-unfolding/cov2d/g2r/tests/test_g2r.py` | `d635b33059d1f893a553400f645cced5949b091e06e39fcdd755af6e199486d2` |
| `2d-unfolding/re2/tests/test_re2_miss_map.py` | `3b1b9b602535854a588f67f3b5ccb6e6dbea61d4fd1e73bdf1e63d325fb97583` |
| `2d-unfolding/cov2d/g2r/tests/g2r_mutation.py` | `789688443b8e02ed5f5e10cb591a5022fa3c661324764e5bc078de867edef104` |

## 2. One change from the declaration's §9, for the director

**§9 says** "an `--miss-weight-override NPZ` flag" and "P5's `build_miss_override.py` extended to all 175 universe columns
in one pass". **This amendment** builds one universe-independent **map** (the miss rows' signal indices and their
`mc_truth_denom` indices, from P5's exact-key alignment on the CV columns), and the driver forms P5's `w_override` at
run time from the map and the universe's own truth column. **Why:** 175 stored override arrays are 175 × 32,849,103 ×
8 B ≈ 46 GB on pscratch, while the map is two int64 arrays of 8,999,007 entries (≈ 144 MB). **What keeps it P5's:**
- the loader change is P5's, byte for byte in its logic, with the flag renamed;
- `test_g2r.Map.test_override_equals_p5_builder_semantics`: for a universe, `g2r.override` from the map equals, bitwise,
  what P5's builder loop (transcribed in the test as `p5_reference`) writes;
- `test_re2_miss_map.MissMapLoader.test_the_override_from_the_map`: the driver's `g2r_miss_override` equals
  `g2r.override` bitwise;
- P5's check 5 (the complement equals the reco rows as exact multisets) runs on the CV columns in `build_map` and on
  every universe column in `universe_check`, all 175 in the prepare.

**The director accepted this on 2026-11-11, pending the audit, on two conditions, both now met in code:**
1. **bitwise equality on real universe indices, not only on a fixture, for more than one universe and the last.** On
   the fixture, `Map.test_override_equals_p5_builder_semantics` covers three universe columns (an identity one, a varied
   one and one named for the last universe). On the real arrays, the prepare's new control **G11**
   (`g2r.spot_check`) compares the map's override with P5's builder loop (`g2r.p5_override`, the loop of
   `build_miss_override.py` blob `7f346e1a` without its checks) bitwise, for the first (`Flux:0`), the middle
   (`Flux:87`) and the last (`VecFFCCQEshape:1`) of the 175 in draw order, and P5's own `MaRES:0`. A difference is
   INVALID before any unfold. G11 can only run on `$UNI`, so its result arrives with the prepare's receipt;
2. **no state carried between universes.** `g2r_miss_override` loads the map and reads the column afresh on each call
   and keeps nothing between calls. `MissMapLoader.test_no_state_is_carried_between_universes` calls it for `MaRES:0`,
   then `VecFFCCQEshape:1`, then `MaRES:0` again in one process: each equals its own `g2r.override`, the two differ,
   and the first and third are bitwise equal. The mutant "state carried between universes (a cached override)" is
   killed by it. (Each unfold is also its own driver process in the job scripts.)

## 3. The controls, and where each is tested

| control (declaration §8) | here | test or receipt |
|---|---|---|
| G1 no-op | the loader with no override equals the pre-patch driver's (blob at `05a74e7c`) bitwise, under `--branch-select all` and `derived` | `MissMapLoader.test_c1_no_override_equals_the_pre_patch_loader`; the whole-driver comparison (every histogram, as `test_re2_data_file.py`) needs LightGBM and runs in the cluster-environment test |
| G2 identity plumbing | an override equal to the proxy gives equal arrays | `MissMapLoader.test_c2_an_override_equal_to_the_proxy_changes_nothing` |
| G3 effect only on miss rows | w_truth and w_reco change exactly on the miss rows whose universe weight differs, to that weight × the POT scale; kinematic and pass arrays bitwise equal | `MissMapLoader.test_c3_the_override_changes_only_the_miss_rows` |
| G4 alignment | P5's five checks, each shown to refuse by name | `Map.test_each_alignment_check_refuses` (8 cases), `Map.test_universe_check_refuses_a_non_proxy_miss_and_a_complement_mismatch` |
| G5 the file | `$UNI`'s size by stat = 171,117,087,867 B | `g2r_prepare.run` (the cluster-environment test) |
| G6 block reproduction | at a tune, `c_t_prime` on the old bands reproduces the committed `C_univ`, `C_T`, `C_T_minus` bitwise; at the data, `band_cov` on part B's 175 products reproduces each `band_<b>` to 1e-12 | `CTPrime.test_the_old_bands_reproduce_the_committed_blocks_bitwise` (against `cov2d_blocks.assemble` itself); the data side on the cluster |
| G7 grade reproduction | the committed errors against the committed C_T and null reproduce `score_<T>.json`'s grade | `ReadoutCores.test_grade_reproduction` (the rule); the committed records on the cluster |
| G8 the realization | each product's `dataFileSha256` is the realization's | `read_products` (the cluster) |
| G9 atime and reads | `O_NOATIME` everywhere outside the driver; `Run`'s atime ledger and open audit | the prepare's and readout's records |
| G11 (new, §2's condition 1) the map against P5 on real arrays | first, middle, last universe and MaRES:0, bitwise | `Map.test_the_spot_check_passes_and_refuses` (the rule); `g2r_prepare.run` on `$UNI` |
| G10 (new) the budget | `re2c_build_q.metrics` on Q_R reproduces `budget_Q.json`'s 6.4137 % and 4.7592 % | `phase_data` (the cluster) |

**Part (+)'s order.** `regrade_core` computes the null at C_T' from the corrected bands and hands it out before any
error is read against it (`RegradeCore.test_the_null_is_from_the_corrected_bands_and_c_t_prime`), then grades the
committed errors against C_T' (`RegradeCore.test_the_grade_reads_the_errors_against_c_t_prime`).

## 4. The mutants

15 mutants, each killed by a named test (`g2r_mutation.py`):
- **the declaration's six:** the flag silently ignored; the override applied to a passing row; a universe's override from
  another column; eps on the full space, not the retained eigensystem; the regrade reading the old C_T; the null left at
  the old laws;
- **the controls':** the subsequence order unchecked; the complement unchecked; a miss row's proxy unchecked per
  universe; the override at the wrong truth rows; C_T' with the lateral check dropped; G7 ignoring the integer fields;
  part (a) not subtracting the old universe block;
- **the director's conditions on §2:** state carried between universes (a cached override); G11 comparing the
  override with itself.

**Results** (`fd/receipts-cov2d/g2r/a1/`, from a clean detached checkout of `2f6dac56`, python 3.13, ROOT 6.36.000, numpy 2.4.4):
- `test_g2r.py`: 24 tests, OK, at PYTHONHASHSEED 0, 1 and 2.
- `test_re2_miss_map.py`: 8 tests, OK.
- `g2r_mutation.py`: both unmutated suites full (24 and 8, none skipped), 15 mutations all killed, the sources restored byte-identical to HEAD, rc 0.
- Not run here: the cluster's numpy 1.26 under root_6_28, and the LightGBM end-to-end comparisons. Both are in the cluster-environment test of the job addendum.

## 5. For the auditor

- §2's change from the declaration's literal form, and whether its equivalence tests cover it.
- `g2r_miss_override` reads the truth column with `ROOT.RDataFrame(t_truth_denom).AsNumpy`, inside the driver, a read the
  declaration's G9 lists among the driver's own (its `--omnifile`).
- `regrade_core`'s use of `cov2d_readouts.leave_out_mec` and `spread_alone` with C_T' and C_T'-.
- Section 6's readouts that need pscratch inputs (the realization check, the clipping residual) are not in this
  amendment's readout. They are descriptive (COV2D-DECLARATION §6) and come in the job addendum, from the committed null
  record's inventory digests.

Nothing is submitted, deposited or tagged.
