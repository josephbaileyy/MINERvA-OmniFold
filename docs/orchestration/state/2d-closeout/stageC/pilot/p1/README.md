# Stage C pilot P1: statistical streams package (diagnostic; no job has run)

Grant: [`AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md`](../../../../../AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md)
§2 P1. Recipe: Stage B [`REPORT.md`](../../../stageB/REPORT.md) §2.8, §4 R5, §7 P1. Joseph's R5 ruling:
[`DECISION-20261012-joseph-2d-closeout-recipe.md`](../../../../../../publication/DECISION-20261012-joseph-2d-closeout-recipe.md).
Pattern: the P5 package (`stageB/diagnostics/p5/`).

**CITABLE FOR:** what the P1 code does, and the login-node control results below.
**NOT CITABLE FOR:** any σ ratio or covariance (no replica has run); submission (the grant needs its binding
addendum first); any change to the production driver.

Built 2026-10-13 in the worktree `closeout/stagec-pilot-20261013` at `ca1bb536`. Nothing was committed and no
Slurm command was used. Login-node runs wrote only under
`/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/p1-dev/`.

## Files

sha256 as of this README. `SHA256SUMS` covers every file, this README included.

| file | sha256 | role |
|---|---|---|
| `driver_p1.py` | `3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578` | production driver `74a4ed69…` plus the patch |
| `patch.diff` | `2cdac849478688920359d312f9a793ec39ff1dd7aaaefe65f973a6114b073905` | `diff -u 2d-unfolding/unfold_2d_omnifold_unbinned.py driver_p1.py`: 12 hunks, +113 / −7 lines |
| `test_noop.py` | `6b36401d96a4d2d3c8b746d1439f54b6979b9df8a16017c0fc1d4c3c1a6585ba` | controls C0–C4 on the CV omnifile |
| `test_rows_mapping.py` | `689ae47239f3913a2751339385c881ddb188ff4ef83c894975229b685e2ad6db` | entry-to-row mapping on a synthetic tree |
| `bkgvar_check.py` | `deb2d2bb1d5899446c04d90f24b90164b1e6577c8d3956fa878bd0e94dd29f0f` | declared check: bkg-stream variance vs Σw² |
| `analyze_p1.py` | `18663a42233e4521239a715effa99c8e60481ed8baf70a5ec54a41ba32919a90` | replica analysis, gates, b ≡ 1 check |
| `smoke_analyze_p1.py` | `ea6d255772f6f26899dc0ccccea677c2d2bf5491b192db750688a697d8146814` | synthetic plumbing smoke for `analyze_p1.py` |
| `evidence/test_noop_report.json` | see `SHA256SUMS` | C0–C4 report |
| `evidence/test_noop_workers/*.json` | see `SHA256SUMS` | per-configuration digests and checks |
| `evidence/test_noop_stdout.txt`, `evidence/bkgvar_check_stdout.txt` | see `SHA256SUMS` | stdout without ROOT rootmap warnings, with `/usr/bin/time -v` |
| `evidence/bkgvar_check.json` | see `SHA256SUMS` | declared-check result, per cell |
| `evidence/test_rows_mapping.json`, `evidence/smoke_analyze_p1.json` | see `SHA256SUMS` | the two plumbing controls |

## The patch (`driver_p1.py`; every change is marked "P1 diagnostic")

- `fill_bkg_reco_2d(..., return_fill_rows=False)`. When True it also returns a dict of `pt, pz, w_pot, entry`,
  one element per `Fill` call: fill order, overflow rows included, `w_pot` = the same `w * pot_scale` the Fill
  received, `entry` = the `mc_background` tree index. When False the function is unchanged.
- New module-level `P1_STREAMS = ("three", "bkg")`, `P1_BKG_SEED_OFFSET = 20_000_000`,
  `p1_draw_bkg_factors(seed, n)` = `default_rng(seed + 20_000_000).poisson(1.0, n)` over **all** tree entries
  (n = `t_bkg.GetEntries()` = 658,227 on the CV file), and `p1_refill_bkg_2d(...)` = B\* refilled as
  Σ b_bkg[entry]·w_pot in production fill order.
- `--bootstrap-streams` gains `three` and `bkg`; new test-only `--unit-factors`. Both are recorded in
  `runConfig`, as `vars(args)` is. Refusals, right after parsing: `three|bkg` without `--bootstrap-seed`, with
  `--closure`, with `--bkg-mode negweight|negweight-refined`, or with `--universe`; `--unit-factors` without
  `three|bkg`.
- `raise` if `n_fakes != 0` on the P1 path. It is placed just before the existing fake-fill block (production
  `:1793`), because B\* is refilled from `mc_background` only.
- In the bootstrap block the data draw (`default_rng(s)`) and the MC draw (`default_rng(s + 10_000_000)`) are
  unchanged and still unconditional, so arms pair by bootstrap seed. On the P1 path:
  - `b_bkg` is drawn;
  - `bkg` and `--unit-factors` set `b_data` and `b_truth` to 1, and `--unit-factors` sets `b_bkg` to 1 too;
  - D\* is filled with `Fill(pt, pz, b_data[i])` over the measured rows, and B\* comes from `p1_refill_bkg_2d`;
  - the purity is the production `build_measured_training_2d(meas_pt, meas_pz, D*, B*)`;
  - the measured weights are purity × b_data, through the existing `do_data` branch;
  - the MC weights get × b_truth through the existing `do_mc` branch, so completeness keeps the un-resampled
    `w_truth_cv` (KI 84), as production does.
- Output: the new histograms `hDataRecoStar2D`, `hBkgRecoStar2D` and `hMeasTrainStar2D`, plus a `p1Streams`
  TNamed with the seeds, offsets, n and factor sums. The production `hDataReco2D`, `hBkgReco2D`, `hMeasSub2D`
  and `hMeasTrain2D` keep their un-resampled content, as in a production bootstrap replica.

Cost on the P1 path: a measured ≈ +10–18 s up to the OmniFold call (118 s production vs 129–136 s P1, login
node), and about 100 MB more memory. Peak RSS up to that call is 9.7 GB in both cases.

## Results (login node `login16`, CV omnifile `runEventLoopOmniFold_MEFHC.root`, sha256 `43f8cc16…` re-measured)

I used the full CV omnifile, not a per-playlist file. Peak RSS was 9.68 GB per worker, two workers at a time,
inside the 30 GiB user cgroup.

**`test_noop.py`: PASS** (8 min 41 s wall). Each configuration runs the driver's own `main()` up to
`ohf.omnifold`, where a stand-in module records sha256 digests of every OmniFold input and of `main()`'s
locals. The configurations are `prod_cv`, `p1_cv`, `prod_both`, `p1_both`, `p1_unit`, `p1_bkg` and `p1_three`,
all at seed 42 with bootstrap seed 7.
- C0: all 6 forbidden combinations refuse before any file is opened.
- C1 (options off), bitwise:
  - `p1_cv` = `prod_cv` on 34/34 recorded objects;
  - `p1_both` = `prod_both` on 36/36;
  - at the loader level, return_fill_rows False/True gives the production arrays and histogram;
  - a b = 1 refill of the recorded rows reproduces `hBkgReco2D`;
  - 658,227 rows were filled, 36,680 of them outside the window.
  - The unchanged functions are source-identical.
- C2 (`three --unit-factors`), bitwise:
  - `p1_unit` = `prod_cv` on 34/34;
  - D\*, B\* and the starred target equal `hDataReco2D`, `hBkgReco2D` and `hMeasTrain2D` (content and sumw2);
  - the purity equals the central measured weights;
  - all three factor vectors are 1.
- C3 (`bkg`, seed 7):
  - out of 41 objects compared with `prod_cv`, exactly B\*, the starred target, the purity and the measured
    weights differ;
  - kinematics, pass flags, MC weights, completeness weights, D\* and every production histogram are bitwise
    equal;
  - b_data and b_truth are all 1;
  - b_bkg is the declared draw (sum 657,662 over n = 658,227);
  - B\* integral is 118,961.06 against B 119,132.37;
  - the worker's own recomputation of D\* (exact), B\* (max rel 0.0 vs bincount), the purity (bitwise) and
    the measured = purity × b_data (bitwise) all agree.
- C4 (`three`, seed 7, against `prod_both`):
  - b_data and b_truth are identical (paired);
  - MC weights, kinematics and the production histograms are identical on 34 shared objects;
  - the measured weights differ;
  - B\* and b_bkg equal the `bkg` arm's;
  - the worker recomputations pass.
- n_fakes = 0 in all 7 configurations.

**`test_rows_mapping.py`: PASS.** On the CV file every entry is filled, so row = entry and the CV tests
cannot see a mapping error. This synthetic tree has 12 entries, 4 of them rejected and 2 outside the grid. The
recorded entries are exactly [0,2,3,5,7,8,10,11]. B\* equals a by-hand Σ b[entry]·w·pot, and a row-position
refill differs.

**`bkgvar_check.py` (declared check): PASS** (52 s).
- N = 2000 draws (seeds 1..2000) over 205 cells with Σw² > 0. That set is the E_C reported set, by
  coincidence.
- max |z| = 3.15 (GlobalID 92: 982 rows, κ = 0.0012); pooled z = 0.77.
- z mean 0.054, sd 1.04; 2 cells have |z| > 3.
- s²/Σw²: median 1.002, range 0.912–1.100.
- The vectorized refill equals `p1_refill_bkg_2d` exactly for seeds 1–3.
- Information only: the mean check gives pooled z = 2.17 (max |z| 3.22). It is not a declared check, and I
  recorded it rather than explained it.

**`smoke_analyze_p1.py`: PASS** (synthetic files, not replicas):
- complete tree: arms OK; ratio medians 1.032 ± 0.005 (planted 1.03) and 0.199 ± 0.007 (planted 0.2);
  b ≡ 1 PASS (XR-L0 against itself, max rel 0);
- a missing fixed replica makes fixed and both ratios INCONCLUSIVE;
- a joint replica at seed 43 makes joint INCONCLUSIVE;
- the unit run scaled by 1 + 1e-6 gives b ≡ 1 FAIL (max rel 1.0e-6).

## Commands (login node; `source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh` first, no `set -u`)

```
R=/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/p1-dev
# $R/repo/2d-unfolding holds unfold_2d_omnifold_unbinned.py (74a4ed69…), driver_p1.py, uq/reported_cells.py
export TMPDIR=$R/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
OMNI=/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
FLUX=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root   # d40aea69…
python3 $R/scripts/test_noop.py --d2 $R/repo/2d-unfolding --omnifile $OMNI --omnifile-sha256 43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df \
    --mcfile $FLUX --workdir $R/work/noop --report $R/work/noop/test_noop_report.json --jobs 2
python3 $R/scripts/test_rows_mapping.py --d2 $R/repo/2d-unfolding --report $R/work/rows/test_rows_mapping.json
python3 $R/scripts/bkgvar_check.py --d2 $R/repo/2d-unfolding --omnifile $OMNI --out $R/work/bkgvar/bkgvar_check.json
python3 $R/scripts/smoke_analyze_p1.py --work $R/work/smoke_analyze --xr-dir $R/xr \
    --p1-sha 3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578 --report $R/work/smoke_analyze/smoke_analyze_p1.json
# after the replicas exist (from a repo checkout, so the xr dir and driver_p1.py resolve):
python3 analyze_p1.py --out-root <OUT> --result <RESULT.json>
```

`$R/xr` holds byte copies of the frozen `xr_compare.py` (`9e59c590…`) and `manifest/references.json`
(`af7d5a19…`).

## Replica layout and arguments that `analyze_p1.py` expects (the sbatch script must match)

- `OUT/2dc_C_P1_<arm>_<NN>/xsec.root`, for arm in `fixed`, `joint` and `bkg`, NN = 01..20, and
  `OUT/2dc_C_P1_unit/xsec.root`: the layout `../sbatch_pilot.sh` writes (`out/<job name>/xsec.root`). Changed by
  the package author after this sub-package was built; `analyze_p1.py`'s `replica_path`/`unit_path` were edited to
  match, and the synthetic smoke uses those functions.
- Every run uses `--omnifile <CV 43f8cc16…> --mcfile <flux d40aea69…> --iters 5 --use-weights --estimator lgbm --seed 42`
  (L0's argv), plus:
  - fixed: the production driver with `--bootstrap-seed N`;
  - joint: `driver_p1.py --bootstrap-seed N --bootstrap-streams three`;
  - bkg: `driver_p1.py --bootstrap-seed N --bootstrap-streams bkg`;
  - unit: `driver_p1.py --bootstrap-seed 1 --bootstrap-streams three --unit-factors`.
- `analyze_p1.py` gates each output on:
  - `driverSha256`;
  - `runConfig`: seed, bootstrap_seed, streams, unit_factors, bkg_mode, estimator, iters, use_weights,
    universe, closure;
  - `p1Streams`;
  - one shared omnifile and mcfile across all outputs.

## Judgment calls

1. **`--unit-factors` needs `--bootstrap-seed`.** The P1 path lives in the bootstrap block. The seed value is
   irrelevant when all factors are 1, and the analysis expects 1.
2. **`bkg` arm and unit control.** Their factor vectors are set to 1 after the unconditional draws, and are then
   applied through the existing `do_data`/`do_mc` branches (× 1.0 is exact). The RNG streams therefore stay
   identical across arms, and completeness takes `w_truth_cv`, which has the same values.
3. **Production histogram names keep un-resampled content.** The resampled D\* and B\* and the starred training
   target are written only under the new names. `hMeasTrainStar2D` is the per-row purity fill, without b_data,
   which mirrors `hMeasTrain2D`.
4. **The n_fakes assert is on the P1 path only.** That keeps the off path byte-identical.
5. **The fill rows come back as a 4th tuple element only when requested,** rather than as an output list, so the
   default return is unchanged.
6. **`test_noop.py` intercepts `main()` at the OmniFold call** instead of testing loaders alone. This covers the
   real control flow, and bitwise equality is sha256 digest equality of bytes, dtype and shape. The bootstrap
   seed for the tests is 7, chosen arbitrarily. I added `prod_both`/`p1_both` (the existing modes unchanged)
   and C4 (pairing) beyond the brief.
7. **bkgvar_check cells.** It uses all 14 × 16 cells with Σw² > 0, and overflow rows are excluded from the
   cells. The 2000-draw refill is vectorized (bincount on cells found with the TH2D's own `FindFixBin`). It is
   gated by exact agreement with the driver's refill for 3 seeds.
8. **Jackknife in `analyze_p1.py`.** Leave-one-replica-out removes replica k from both arms, and the SE of the
   median recomputes the median over cells on each leave-one-out set. With 20 replicas the median's jackknife
   SE is itself rough, since a median is not smooth. It is reported as MEASURED, with no pass/fail.
9. **Arm gates.** An arm is INCONCLUSIVE if any replica is missing or mismatched, and also if the 61 outputs do
   not share one omnifile and mcfile.
10. **E_U cells.** They are E_U `hXSec2D > 0`, and are also checked equal to `references.E_C.reported_globalid`
    (equal in the smoke). The b ≡ 1 check passes `E_C`'s list to `xr_compare.compare`, as instructed.
11. **One extra file each.** `test_rows_mapping.py` and `smoke_analyze_p1.py` were added because the CV file
    cannot test the entry mapping and `analyze_p1.py` had no data to run on.

## Limits

- No sbatch script is written here. The layout above is the contract it must follow.
- The variance check validates the stream's variance law, not its effect on the unfolded σ.
- Same-model caveat: the code and its controls are by one model; an independent review is still required
  before the binding addendum.
