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
| tests | `2d-unfolding/cov2d/g2r/tests/test_g2r.py` (27 tests), `2d-unfolding/re2/tests/test_re2_miss_map.py` (11), `2d-unfolding/cov2d/g2r/tests/test_g2r_glue.py` (18), `2d-unfolding/cov2d/g2r/tests/g2r_mutation.py` (23 mutants). |

Digests (sha256) at the code commit `62864b1641a580c52b2918babc0926e468925dad`, the commit the receipts were made at:

| file | sha256 |
|---|---|
| `2d-unfolding/re2/re2_driver.py` | `e226daf3f51954c7079cc7b3ab509e464865502f5dbde4acf11876409971dd67` |
| `2d-unfolding/cov2d/g2r/g2r.py` | `dbcc416d35565c183d73d6ce03a9efa89dddf8cbda618fa3e6eb00bbe08d28ec` |
| `2d-unfolding/cov2d/g2r/g2r_prepare.py` | `bb97fba12034e39c4b6dd5679b93f8259bcc4fab2b69890931c95c1311c7eb57` |
| `2d-unfolding/cov2d/g2r/g2r_readout.py` | `590ffba1cb8cb65410abee93cd8b3c679b05d4e77155591d619a2f24ba4a0cf1` |
| `2d-unfolding/cov2d/g2r/tests/test_g2r.py` | `24d8399b339ea458eec10d02a302e86ed87649aa20093e4624a8a2431ff96f8e` |
| `2d-unfolding/re2/tests/test_re2_miss_map.py` | `8957d38ee7925f1c8b3b35d548cea341b34ea83c7cf5ac6eb158bec55ede03d3` |
| `2d-unfolding/cov2d/g2r/tests/test_g2r_glue.py` | `c926932578573b4452549678654f90bd3d87d81cd557d66bb3f03178f0df6d8d` |
| `2d-unfolding/cov2d/g2r/tests/g2r_mutation.py` | `245bc00608afdfc3cdfe65e3f47b8d8afd1d7679ebc400964ac41e9af68a3653` |

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

## 2a. The audit's blocker B1, and the director's sweep

**B1 (coverage-5b-audit, at `cf502c67`).** The provenance line `provenance.append(("g2rMissMap", json.dumps(...)))`
raised `UnboundLocalError` on every `--miss-map` run: `main()` binds `json` only in two later branches, so `json` is a
local of `main()` and was unbound there. No test reached the line. **Fixed:** it imports `json` under its own name,
`g2r_json`, marked `# G2R`. **Now tested:** `MainWithMissMap` runs `main()` itself, with and without the flag, on a
fixture with misses, through to a stub OmniFold helper that records `main()`'s provenance and the training weights
and exits 17. With the flag, `g2rMissMap` carries the map's sha256, `MaRES:0`, its branch and counts, and the training
weights change exactly on the varied miss rows to the override × the POT scale. Without it there is no record. On the
unfixed driver both tests fail with the auditor's `UnboundLocalError`. Two mutants (the line removed; the line broken
back to B1) are killed. `P5Builder` makes the auditor's n2 permanent: P5's committed builder (blob `7f346e1a`,
unmodified, all checks) on per-playlist ROOT fixtures (a block with no misses, one all misses) equals the map's
override bitwise for two universe columns.

**The director's sweep** ("no path in the driver, prepare, readout or regrade code may be reachable only on the
cluster without a test that has run it"). A line tracer (`sys.settrace` through `usercustomize`, so it follows the
driver's subprocesses) ran all three suites and listed every executable line never executed: all of g2r.py; the G2R
lines of re2_driver.py (those marked `# G2R` and `g2r_miss_override`); g2r_prepare.py; g2r_readout.py. To close it,
`test_g2r_glue.py` runs:
- **the prepare** end to end (uproot replaced by a stand-in serving numpy columns), its STOP, INVALID and no-overwrite
  paths, and both count mismatches;
- **`phase_tune` on the REAL committed AR23 inputs** (blocks, null, score, E and C2's record at their digests), with
  175 small ROOT products whose rows are blocks_AR23.npz's own universe rows. On real data: G7 reproduces the committed
  grade; G6 passes; **the null rebuilt at C_T' equals the committed `null_AR23.json` field for field** (the auditor's n4);
  and the regrade reproduces the committed verdict, ndf, counts, joint count and flagged cells. A tampered
  blocks_AR23.npz (C_univ × (1 + 1e-9)) makes the record INVALID with "G6 failed" before any product is read or any
  null is written. E of the wrong shape, and E_R's cells not the blocks', refuse;
- **`phase_data`** end to end on stand-ins for its pscratch inputs, each read at its own digest through the real
  `read_pinned`, and its INVALID and refusal paths;
- **the readout's CLI** (arguments and exit codes 0, 5, 8).

**What remains never executed by any test** (the sweep after the fix):
| file | line | what | why |
|---|---|---|---|
| g2r_prepare.py | 137 | an atime move sets STOP, rc 8 | the stand-in reads restore atime; the receipt run on `$UNI` shows the ledger |
| g2r_readout.py | 246 | C_T' not PSD appends a control failure | needs a non-PSD C_T' from real products |
| g2r_prepare.py, g2r_readout.py | 144, 343 | `if __name__ == "__main__": sys.exit(main())` | each `main` is tested |
| re2_driver.py | 845 | "not every finite entry was applied" | unreachable: the override is applied before any `continue` (P5 recorded the same) |
| re2_driver.py | 1441 | the truth column's length differs from the tree's entries | unreachable through RDataFrame on the tree itself |

**Found by the real-data run, and corrected: G6's rule.** The first version required bitwise reproduction at a tune.
On the committed AR23 and G18 blocks, under this machine's numpy 2.4.4, the rebuilt C_univ differs from the committed
one by about 6 × 10⁻²¹ of its largest element (the lateral and normalization blocks are bitwise). That is the BLAS's
rounding in the weighted covariance, not a code difference. The declaration's §8 states G6 "to 10⁻¹² relative", so
`g6_tune` now applies 10⁻¹² relative, as declared, and records whether each block is also bitwise. On the cluster,
under phase N's own environment, it is expected to be bitwise, and the record will show it.

## 3. The controls, and where each is tested

| control (declaration §8) | here | test or receipt |
|---|---|---|
| G1 no-op | the loader with no override equals the pre-patch driver's (blob at `05a74e7c`) bitwise, under `--branch-select all` and `derived` | `MissMapLoader.test_c1_no_override_equals_the_pre_patch_loader`; the whole-driver comparison (every histogram, as `test_re2_data_file.py`) needs LightGBM and runs in the cluster-environment test |
| G2 identity plumbing | an override equal to the proxy gives equal arrays | `MissMapLoader.test_c2_an_override_equal_to_the_proxy_changes_nothing` |
| G3 effect only on miss rows | w_truth and w_reco change exactly on the miss rows whose universe weight differs, to that weight × the POT scale; kinematic and pass arrays bitwise equal | `MissMapLoader.test_c3_the_override_changes_only_the_miss_rows` |
| G4 alignment | P5's five checks, each shown to refuse by name | `Map.test_each_alignment_check_refuses` (8 cases), `Map.test_universe_check_refuses_a_non_proxy_miss_and_a_complement_mismatch` |
| G5 the file | `$UNI`'s size by stat = 171,117,087,867 B | `g2r_prepare.run` (the cluster-environment test) |
| G6 block reproduction | at a tune, `c_t_prime` on the old bands reproduces the committed `C_univ`, `C_T`, `C_T_minus` to 1e-12 relative, with bitwise recorded (§2a); at the data, `band_cov` on part B's 175 products reproduces each `band_<b>` to 1e-12 | `CTPrime.test_the_old_bands_reproduce_the_committed_blocks_bitwise` (same process: bitwise), `CTPrime.test_g6_tolerates_rounding_and_refuses_beyond_1e_12`, `PhaseTune` on the committed AR23 blocks, `PhaseTuneTampered`; the data side by `PhaseData` on stand-ins and on the cluster |
| G7 grade reproduction | the committed errors against the committed C_T and null reproduce `score_<T>.json`'s grade | `ReadoutCores.test_grade_reproduction` (the rule); `PhaseTune.test_g7_and_g6_pass_on_the_committed_inputs` (the committed AR23 records, locally) |
| G8 the realization | each product's `dataFileSha256` is the realization's | `read_products` (the cluster) |
| G9 atime and reads | `O_NOATIME` everywhere outside the driver; `Run`'s atime ledger and open audit | the prepare's and readout's records |
| G11 (new, §2's condition 1) the map against P5 on real arrays | first, middle, last universe and MaRES:0, bitwise | `Map.test_the_spot_check_passes_and_refuses` (the rule); `g2r_prepare.run` on `$UNI` |
| G10 (new) the budget | `re2c_build_q.metrics` on Q_R reproduces `budget_Q.json`'s 6.4137 % and 4.7592 % | `phase_data` (the cluster) |

**Part (+)'s order.** `regrade_core` computes the null at C_T' from the corrected bands and hands it out before any
error is read against it (`RegradeCore.test_the_null_is_from_the_corrected_bands_and_c_t_prime`), then grades the
committed errors against C_T' (`RegradeCore.test_the_grade_reads_the_errors_against_c_t_prime`).

## 4. The mutants

23 mutants, each killed by a named test (`g2r_mutation.py`):
- **the declaration's six:** the flag silently ignored; the override applied to a passing row; a universe's override from
  another column; eps on the full space, not the retained eigensystem; the regrade reading the old C_T; the null left at
  the old laws;
- **the controls':** the subsequence order unchecked; the complement unchecked; a miss row's proxy unchecked per
  universe; the override at the wrong truth rows; C_T' with the lateral check dropped; G7 ignoring the integer fields;
  part (a) not subtracting the old universe block;
- **the director's conditions on §2:** state carried between universes (a cached override); G11 comparing the
  override with itself;
- **B1 and the sweep:** the g2rMissMap provenance line removed; the provenance line broken back to B1; a product's
  universe unchecked; G6's result not enforced in phase_tune; G6's tolerance opened; the null at C_T' not written;
  the prepare skipping G11; a missing per-playlist file not a STOP.

**Results** (`fd/receipts-cov2d/g2r/a1/`, from a clean detached checkout of `62864b16`, python 3.13, ROOT 6.36.000, numpy 2.4.4):
- `test_g2r.py`: 27 tests, OK, at PYTHONHASHSEED 0, 1 and 2.
- `test_re2_miss_map.py`: 11 tests, OK.
- `test_g2r_glue.py`: 18 tests, OK.
- `g2r_mutation.py`: the three unmutated suites full (27, 11 and 18, none skipped), 23 mutations all killed, the sources restored byte-identical to HEAD, rc 0.
- `coverage_sweep.txt`: 6 executable lines never executed, each listed in §2a.
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
