# RE-2 declaration, part A: the refined 2D path and the J0 pilot (frozen before any job)

**Declared by** the re-1 lane for the director, 2026-10-23, under DECISION-20261023 (second) item 1. It follows:
- [`RE2-PLAN.md`](RE2-PLAN.md) (PR #275);
- the director's [`RE2-PLAN-RULINGS.md`](RE2-PLAN-RULINGS.md) (PR #277);
- Joseph's R8/R9 decision (`DECISION-20261023-joseph-r8-r9-and-5d-scoping.md`, PR #281).

**No job has run under it.** It takes effect only when the director commits a BINDING record.

**CITABLE FOR:**
- the code RE-2's J0 runs, with its digests;
- J0's inputs, runs, controls and stop rules;
- the rule that turns J0's measured units into a production decision;
- the readouts already fixed for part B (§6);
- the registry entry `a-refined-400-31`.

**NOT CITABLE FOR:**
- any number: none exists yet;
- a production job (J1–J8). Part B, declared and bound after J0, covers those;
- an adoption, coverage or claim, which are Joseph's.

**In brief:**
- **J0 is two regular jobs, one node each, with 34 runs.**
  - It reproduces 15 existing purity products with the new code's purity arm.
  - It checks the refined arm against the driver, RE-1's D2 and itself (null, unit-factor, determinism, the data
    background stream, power).
  - It times every refined production class.
- **Projected charge:** 8.1 node-h; worst case 10.2.
- **On current evidence the 90 node-h grant will not cover production.**
  - The plan's production priced at today's packed slowdown (1.81×) is about 98 node-h for the core, with a worst
    case of about 122.
  - The fixed rule (§5.3) then sends part B to the director for a fresh binding.
  - J0's own measurements, not this estimate, decide.

---

## 1. What changes from the plan, and what is deferred

| item | RE2-PLAN | this declaration | reason |
|---|---|---|---|
| code path (R1) | extend `re1_2d.py` as `re2_2d.py` | **`2d-unfolding/re2/re2_driver.py`: a copy of `driver_p1.py`**, changed only in blocks marked RE-2 (§2) | Every consumer of production outputs reads the driver's full ROOT output: `analyze_prod.py` reads `hOFCompleteness2D`, `hEffDenSource`, `hOFTruthDenom2D` (`:173-180`), and the period analysis reads truth, completeness and flux. `re1_2d.py` writes `hXSec2D` alone. The copy keeps `driver_p1.py`'s outputs, so the existing analyses read refined products in their own containers |
| tolerance of K1 and of the CHK checks | bitwise where the reference was made by the same code at the same thread count; null, unit-factor and determinism checks bit for bit | **≤ 1e-8 relative on the 205 cells; bitwise reported, not deciding** | Configuration (a) is LightGBM's non-deterministic mode (the deterministic variant is (c)), so a bitwise rerun is not promised even at a fixed thread count. 1e-8 is the XR frozen-repeat criterion. RE-1's K1-2D met it at 2.3e-13 |
| null-universe check | bitwise against the refined CV | **≤ 1e-8** | Stage C's purity `NormDISCC:0` reproduced the CV to ≤ 6.0e-12 at five seeds, not bitwise (`stageC/production/REPORT.md:66`) |
| sequencing | J0, then J1–J8 under one declaration | **part A (this file) declares J0 only. Part B, after J0 and before any production job, declares J1–J8 and their limits, the post-processing copies, and the items below** | Ruling 2: "the J0 units, not historical ones, set the job limits" |
| deferred to part B (each before any production product exists) | in "the declaration" | **not here:** `re2/inventory.tsv` (RE2-PLAN §2.2); the R7 producer search; the replaced-identity list for the rollup copies (RE2-PLAN §5.1); code to write the step weights the C2ST re-evaluation needs (RE2-PLAN §2.2, "Other dependents", and J1 in §4.2) | These concern part B's products. J0 also makes one refined product on data, `D_cv`, the refined central unfold. It is a control product here, compared with D2 only, and no identity list consumes it |
| J0 price | 4.0 / 5.0 node-h at September units | **8.1 / 10.2** (§4) | The limits come from each class's observed **maximum** × today's packed slowdown 1.81 (`state/gpu-timing-20261023/REPORT.md:34,65-67`) × 1.06 for the refinement × 1.25, as RE2-PLAN §4.2 requires. The plan's estimate used means and September units |
| S2 and period classes | J0 measures them | **S2 is priced from the three-stream replicas** (the same unfold with two factor vectors held at 1). **The period class is priced from a period central and a period replica (`--bootstrap-streams both`)**, the maximum of the two | No separate S2 run; a period replica is added (it is the only refined path no unit test executes, §2.2) |
| the J5/J7 priority | J7 recommended, J5 optional (R10) | the rule adds J7 before J5 (§5.3) | R10 |

## 2. Code

The code is committed at **`668e9b44e41e6eae7b2d0727b0a924bc311d063d`** on `re2/declaration-20261023`. J0 runs from a
fresh clone detached at it.
- The operator passes the sha. `re2_submit_j0.sh` and the job refuse a deploy that is not a clean checkout at the sha
  passed, and the submission is recorded in `submissions.log`. The BINDING record names the sha; that it was the one
  passed is checked by reading `submissions.log` against it.
- The job also checks its own QOS (regular) and time limit against the declared values.
- `re2_submit_j0.sh` refuses a second J0 submission.

| file | sha256 | role |
|---|---|---|
| `2d-unfolding/re2/re2_driver.py` | `38ff37055af026bd11b1c12a431b31eed522d5038c1bcf020cd47c374d2ddf7c` | the RE-2 driver |
| `2d-unfolding/driver_p1.py` (unchanged) | `3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578` | its original: the Stage C S1/S2/S4(i) driver |
| `run/driver.diff` (`git diff --no-index 2d-unfolding/driver_p1.py 2d-unfolding/re2/re2_driver.py`, with its mode header) | `5cf933d3936ca1b1bebcffafbc4047325d2aef4888cf940c845d2e6cbeabe4cd` | the record of the copy: 58 insertions, 4 deletions |
| `2d-unfolding/re2/re2_with_helper.py` | `059b67a366fb0748911eb4d03df97fbb6041f6b422371a933a2c832e15080b81` | runs a frozen driver with this checkout's helper (the K1-R reference runs) |
| `2d-unfolding/re2/re2_k1.py` | `33ffee109f38983e9972dc502a3a47b43b34593aab42f216a5bb3e4832043902` | J0 control readout |
| `2d-unfolding/re2/re2_units.py` | `8cd7aa34a449b0ef2b20da0122d1077c8a526073406524fc85199e93a4a69bbf` | J0 unit readout and the production rule |
| `2d-unfolding/re2/tests/test_re2_driver.py` | `db235796f49884ab5200f643d0e03201f22ebe0d435ad319c950e1f50045a982` | 9 tests |
| `2d-unfolding/re2/tests/test_re2_readouts.py` | `c7fa5dad33c608df10b2d2c25b483bd380902477a08c18357882136c85341614` | 10 tests |
| `run/j0_runs.tsv` | `9ce5571add054ccf7c5fd41b4f374ee8bc3633ca651b20e9dda7705910547b00` | the 34 runs |
| `run/j0_checks.tsv` | `f3be0863652bb2c48f747ec496e02497734e7711040f7ec1be0ef7941291bfa8` | the 30 checks |
| `run/launch/re2_env.sh` | `cb6c23b2b490e57788ec9e2e8f7fcf942d359c49e27028343905b1d939352a2c` | inputs, declared limits, preflight |
| `run/launch/re2_j0.sbatch` | `8b8243711624a1c63f930de0277d384ff8316b0edc9577b2de3a00c7a439aa18` | the job |
| `run/launch/re2_submit_j0.sh` | `23cedef7e3fe39f66e9c7c03db30b72ba4b1f2a11301bf6a63a6058ce2f017e5` | submit, once (J0a logged before J0b is submitted) |
| `run/launch/re2_j0_readout.sh` | `f10644e9a7a7101e2f369509c97caaa857765b5cb278bdcb2e919dda8205fafa` | the login-node readout (only after both jobs are in a terminal state) |
| `run/launch/re2_ledger.sh` | `4018b8f1bbd0daa82ced4a4b30623d09b3219da458e4a344c98f5a5942e8f9b9` | `sacct` ledger (a copy of `re1_ledger.sh`) |
| `run/launch/test_lane_stdin.sh` | `1aae12eb70dcd306d9f1f3a11406eb4b5b3803504b301ccdb6d1b244c7c47846` | the launcher test (§2.2) |

The OmniFold helper is `unbinned_unfolding/python/omnifold.py` `e96234124a31…`. That is the same bytes as the
cluster copy Stage C imported (`stageC/production/DESIGN.md:43`).

### 2.1 What the copy changes

Every change is in a block marked RE-2. With none of the RE-2 options and `--bkg-mode purity`, it runs
`driver_p1.py`'s code path. The changes:
1. **`--refine-n-estimators`, `--refine-num-leaves`.** They set the Stay-Positive refinement classifier's size,
   merged into the `random_state` = seed + 3 the driver already passes. The driver's own call passes `random_state`
   alone, so its refinement is always 100/8 (`unfold_2d_omnifold_unbinned.py:402-407,2037-2041`). Both options are
   refused without `--bkg-mode negweight-refined`.
2. **The P1 three-stream and background-only bootstrap, also on `--bkg-mode negweight-refined`.**
   - The background stream's Poisson(1) factor of each `mc_background` entry (seed + 20,000,000, drawn over all
     entries, `driver_p1.py:368-372`) multiplies that entry's injected −w row.
   - The rows are matched by `re2_injected_entries`, which applies the loader's own fiducial tests, in order, to its
     fill rows.
   - The data rows keep +1 × b_data, and the signal MC rides b_truth.
   - The refinement is refitted on the resampled signed sample.
   - The completeness keeps the un-resampled truth weights (KNOWN_ISSUES 84, unchanged).
   - The refusal of signal fakes is defensive. On this path the P1 guard already refuses them first
     (`re2_driver.py:1901-1903`). The injected-row count guard has no test.
3. **The helper import** comes from this checkout, not from the fixed `/pscratch/…/MINERvA-OmniFold/…` path
   (OI-136).
4. **A `re2Refinement` record** in the output: the classifier parameters, the clipped fraction, the signed and
   refined sums and their ratio, the row counts, and whether the background stream ran.

### 2.2 Tests

- **`test_re2_driver.py`, 9/9 passed on Perlmutter.** It ran on a login node (`taskset -c 8-11`, so **4 threads**),
  root_6_28, LightGBM 4.6.0, on files byte-equal to the committed ones. It runs `driver_p1.py` and `re2_driver.py`
  on a synthetic omnifile with one vertical universe, and compares every histogram's contents and errors bit for bit:
  - **The purity arm equals `driver_p1.py`** on the CV, a three-stream replica, a background-only replica and a
    universe (`--branch-select derived`). The universe moves the result.
  - **Without a size, the refined arm equals `driver_p1.py`'s own `negweight-refined`** (CV and universe).
  - **400/31 reaches the classifier.** The recorded parameters are `{random_state 45, n_estimators 400,
    num_leaves 31}`, and the result moves.
  - **The refined three-stream bootstrap with all factors 1 equals the refined CV.**
  - **The background stream's signed sums equal an independent recomputation** from the fixture's rows and the
    stream's draws, both background-only and three-stream.
  - **The guards refuse** the size options without the refined mode, and the P1 streams with plain `negweight`.
  - **The independent review ran mutants** on Perlmutter. Stream off: 3 failures. Row index in place of tree entry:
    3 failures. Size ignored: 1 failure.
  - **Not tested:** lateral and period inputs (J0's K1-L, K1-P1–P3 and K1-R2 cover them), and the refined
    `--bootstrap-streams both` path (J0's `RPR_PA_b01` exercises it).
- **`test_re2_readouts.py`, 10/10 passed locally** (python3.13, PyROOT). It includes **`re2_k1.py` over the declared
  `j0_runs.tsv` and `j0_checks.tsv`**, with synthetic outputs for all 34 runs:
  - the verdict can be PASS, and the two `p1ref` rows are not health rows;
  - a wrong stream sum fails STREAM-1 alone;
  - a tampered output fails the `SHA256SUMS` check;
  - K1 passes and fails in both directions, and fails on a wrong digest;
  - health fails on clipping, a wrong size or a wrong `random_state`;
  - every branch of the production rule, J0's charge taken from the grant, J5 refused without J7, a ledger
    without both J0 jobs refused, and a step not COMPLETED.
- **`run/launch/test_lane_stdin.sh` passed on Perlmutter.** It runs the job's `lane()` with a stub `srun` that reads
  all of its stdin, as the real one forwards it (srun(1), IO Redirection). It gives **34 of 34 runs**. With the
  table read from stdin and no `/dev/null` (the earlier draft), it gives 6 of 34.
- **Smoke run from a clean clone at `6970abd9`.** `re2_driver.py` and `re2_with_helper.py` there are byte-identical
  to `668e9b44`. Both ran through the OI-136 guard on the fixture with rc 0 and `outside_expect_root=0`, used the
  clone's helper, and gave bit-identical `hXSec2D`.

## 3. Inputs

The inputs are the existing ME-FHC files every 2D product was made from. No newer FHC release is used.

| input | path | sha256 | checked |
|---|---|---|---|
| CV omnifile | `/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root` (read only, as Stage C) | `43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df` | by each job |
| MC (flux) file | `/pscratch/…/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root` | `d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316` | by each job |
| universe omnifile (171 GB) | `…/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root` | `220c479efa9751116fd396ea32398de5631f8b755e6b16a94ce090975f011418` (Stage C's preflight hash). Size, mtime and inode `171117087867 1783523295 882725391507234642` are unchanged on 2026-10-23 | size/mtime/inode by each job; **a full hash before part B's J2** |
| flux universes | `…/baseline_flux/flux_integral_universes_MEFHC.root` | `5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb` | by each job |
| lateral `BeamAngleX_0` (53.8 GB) | `/global/cfs/…/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged/runEventLoopOmniFold_5D_MEFHC_active_BeamAngleX_0.root` (read only) | `38b9fc307eabd864cd0fd663679b51fb2e6d064672410af6b3cf8b0a7e161ed5` (its `SHA256SUMS` `73775251…`) | by J0a |
| period inputs | `/pscratch/…/2d-closeout-period-unfold-20261014/inputs/runEventLoopOmniFold_{ALL,PA}.root`, `flux/runEventLoopMC_{ALL,PA}.root` | `a7a4bcb3…`, `1d2f5b37…`, `e3dc9e63…`, `927f5af2…` (full values in `re2_env.sh`) | by each job |

**The references the controls compare against.** Each is re-hashed by `re2_k1.py`; the full digests are in
`run/j0_checks.tsv`.

| reference | path | sha256 |
|---|---|---|
| `E_U` | `…/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` | `4f5a1b6d…` |
| Stage C C0_cv, C0_unit, S1_001, S2_001 (64 CPUs) | `/pscratch/…/2d-closeout-stageC-production-20261015/out/2dc_P_{C0_cv,C0_unit,S1_001,S2_001}/xsec.root` | `71249143…`, `f1699e66…`, `c67bb587…`, `501bb020…` |
| Stage C S4U at seed 42 (128 CPUs): MaCCQE:0, Flux:23, NormDISCC:0 | `…/out/2dc_P_S4U_{MaCCQE0,Flux23,NormDISCC0}_s42/xsec.root` | `26bde3ba…`, `87e65b2c…`, `84f822e3…` |
| July sweep (pn; CPU count not recorded) | `…/2d-unfolding/uq/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_{MaCCQE_0,Flux_23,NormDISCC_0}.root` | `d17b45c6…`, `eb8414af…`, `5819b46b…` |
| Stage C S3 lateral (128 CPUs) | `…/out/2dc_P_S3_BeamAngleX0/xsec.root` | `5aac876a…` |
| period unfolds (64 CPUs) | `/pscratch/…/2d-closeout-period-unfold-20261014/out/pu_{CTRL_s42,PA_s42,PA_b01}/xsec.root` | `5582d19e…`, `9e59f456…`, `e20e031a…` |
| RE-1 D2 (the refined data unfold, 64 CPUs) | `/pscratch/…/methods-paper/re1-20261022/out/2d/d2_data_refined.npz` | `71ca3e5f…` |

**Argv and allocation.** Eleven references record their argv in `runArgv` (the Stage C and period outputs). Each J0
run repeats it: the same options and the same CPUs, with memory at 1,905 MB per CPU and the thread environment
Stage C set (`OMP_NUM_THREADS=64`, MKL/OpenBLAS/NumExpr at 1, `LOKY_MAX_CPU_COUNT` unset; `sbatch_prod.sh:66-68`).
`E_U`, the July files and D2 record no `runArgv`.

## 4. J0: runs, compute and storage

| job | QOS | lanes | runs | basis (class maximum × 1.81, × 1.06 refined) | projected | limit | worst charge |
|---|---|---|---|---|---|---|---|
| J0a `re2-j0a` | regular, `--exclusive`, `--no-requeue` | a1: 9 universe runs, 128 CPUs; a2: 3 laterals, 128 CPUs | 12 | universe 910 s (`REPORT.md:189`); lateral BeamAngleX0 2,848 s (`:396`); preflight with the 53.8 GB lateral hash ≈ 900 s | 4.72 h | 5:55 | 5.92 node-h |
| J0b `re2-j0b` | the same | b1–b4, 64 CPUs each | 22 | CV 2,003 s (pilot `REPORT.md:278`); replica 774 s (`REPORT.md:191`); period central 995 s and replica 1,558 s (`period-unfold-20261014/REPORT.md:118`, `sacct_charges.txt`); preflight ≈ 300 s | 3.40 h | 4:15 | 4.25 node-h |
| **J0** | | | **34** | | **8.1 node-h** | | **10.2 node-h** |

**Lane order.** The lanes are balanced on these bases: J0a's lanes take 15,417 s and 16,083 s, J0b's
11,923 / 11,923 / 10,730 / 11,665 s. The null and determinism runs come early in their lanes. The last run of
some lanes is still a control (`L_BAX0`, `B_S2_001`, and `B_S1_001`, the STREAM-1 reference), so a time limit can
cost a control. Any step not COMPLETED makes the unit readout INCOMPLETE either way.

**What runs:**
- **J0a, 128 CPUs.**
  - Lane a1: purity MaCCQE:0, refined NormDISCC:0 (null), purity NormDISCC:0 and Flux:23; reference and RE-2
    refined without a size on MaCCQE:0 (K1-R); refined MaCCQE:0, Flux:23 and MaRES:0.
  - Lane a2: refined lateral BeamAngleX0, run twice (determinism); purity lateral BeamAngleX0.
- **J0b, 64 CPUs.**
  - Purity: CV, unit-factor control, S1 replica 1, S2 replica 1, periods CTRL and PA, period replica PA b01.
  - Reference and RE-2 refined without a size on period PA.
  - Refined 400/31: CV, unit-factor control, three-stream replicas with bootstrap seeds 1–8 (seed 1 twice), period
    PA, period replica PA b01.

**The ceiling.** J0 is booked under the 2D closeout ceiling (ruling 4).
- **Spent under it: 39.4714 node-h** (RE2-PLAN §4.3, re-derived from `sacct`). No 2D closeout job has run since
  (the review re-checked `sacct` from 2026-10-22 12:00), and RE-1 is not re-booked.
- J0 takes its charge out of the 90 node-h grant. Part B's room is 90 minus J0's actual charge (§5.3), at least
  79.8.

**Storage** (R9 decided):
- Outputs go to `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/j0/` (`out/<label>/xsec.root`, `logs/`,
  `inventory/`, `readout/`). That is about 3 MB of outputs plus logs.
- Nothing is written under a checkout (`PYTHONDONTWRITEBYTECODE=1`), or to CFS.
- A run whose output directory exists is not run again.

## 5. Controls, readouts and rules, fixed now

### 5.1 Controls (`run/j0_checks.tsv`, read by `re2_k1.py`)

Each check compares `hXSec2D`, or the named histogram, on `E_U`'s 205 reported cells.

**PASS rule.**
- The largest relative difference must be ≤ 1e-8. For `hXSec2D`, both files must also report the same cell set.
- Where the reference has a digest, it must match.
- Bitwise equality over all 224 cells is reported but does not decide.
- An unreadable or malformed file fails its check.
- Before any check, the outputs are verified against the jobs' `SHA256SUMS.J0a` / `SHA256SUMS.J0b`.

| id | test (J0 run) | reference | what it shows |
|---|---|---|---|
| K1-C1, K1-C2 | purity CV | Stage C C0_cv; `E_U` | the copy's purity path reproduces the CV and the adopted central value |
| K1-C3 | purity unit-factor | Stage C C0_unit | the three-stream path with factors 1 |
| K1-B1, K1-B2 | purity S1 and S2 replica 1 | Stage C S1_001, S2_001 | the bootstrap streams, replica for replica |
| K1-U1–U3, K1-U4–U6 | purity universes | Stage C S4U at seed 42; the July sweep | the universe path, selective read |
| K1-L1 | purity lateral | Stage C S3 | the lateral path |
| K1-P1–P3 | purity period CTRL, PA, replica PA b01 | `pu_CTRL_s42`, `pu_PA_s42`, `pu_PA_b01` | the period path, including `--bootstrap-streams both` |
| K1-R1, K1-R2 | RE-2 refined, no size | `driver_p1.py` refined, same job, same CPUs | the copy's refined path equals the driver's (universe, period) |
| K1-D1 | RE-2 refined 400/31 CV | RE-1 D2 | equals the refined data unfold C2 was read against |
| CHK-unit | refined unit-factor | refined CV | the refined bootstrap with factors 1 is the CV |
| CHK-det1, CHK-det2 | a refined replica and a refined lateral, run again | their first runs | run-to-run stability at 1e-8 |
| CHK-null-r, CHK-null-p | refined and purity NormDISCC:0 | refined and purity CV | the null universe in each arm |
| CHK-eff | refined CV, `hEff2D` | purity CV, `hEff2D` | the MC efficiency does not depend on the background treatment (RE2-PLAN §2.3) |
| STREAM-1 | refined replica seed 1 | purity S1 replica seed 1 | **on the data**, the refined background stream's signed sum = its data-factor sum (`p1Streams`) minus the purity replica's in-range `hBkgRecoStar2D` integral, same seed, to 1e-9 |
| POW-1–POW-5 | refined CV; refined replica 1; refined MaCCQE:0; refined lateral; refined period replica | purity CV; refined CV; refined NormDISCC:0 (×2); refined period central | the refined result, a replica, a universe, a lateral and a period replica each **differ** by more than 1e-6, against a run on the same CPU count |

**Refinement health.** Every `re2_driver.py` run with `--bkg-mode negweight-refined` must have:
- a clipped fraction ≤ 0.01;
- refined/signed in [0.99, 1.01];
- `random_state` 45;
- 400 trees and 31 leaves, where the run declares them.

**Verdict.** J0 PASSES only if every check, every health row and the `SHA256SUMS` comparison pass.

### 5.2 Seeds

- Estimator seed 42: OmniFold `random_state` 42/43/44, refinement 45.
- Bootstrap seeds 1–8, as Stage C's S1_001–008, and 1001, as `pu_PA_b01`.
- No other seed.

### 5.3 The production rule (`re2_units.py`)

**The measured unit.**
- A run's node-h is its step's ElapsedRaw × AllocCPUS / 256 / 3600.
- Each production class's refined unit is the **maximum** over J0's runs of that class.
- Counts are RE2-PLAN §4.2's:
  - 3 central;
  - 175 universes;
  - 10 laterals;
  - 300 S1;
  - 80 S4(i);
  - 37 periods;
  - diagnostics: 39 S4(ii) and 100 S2.

**The rule.** `room` = 90 − J0's charge (the jobs' `charge_node_h` from `re2_ledger.sh`).
- **1.25 × core (J1, J2, J3, J4, J6, J8) ≤ room:** part B is declared within the grant. J7 is added if it still
  fits, and then J5, but only if J7 was added.
- The ledger must hold exactly the two J0 job rows, or the readout stops.
- **1.25 × core > room:** no production job starts. The projection goes to the director for a fresh binding
  (ruling 2).
- **Any J0 step not COMPLETED, or any class unmeasured:** INCOMPLETE, and no production job starts.

**What the plan's figures imply.** At today's packed 1.81×, the plan's production (58.0 − 4.0 = 54.0 node-h,
which carries the plan's 1.25 planning factor) becomes about 98 node-h for the core, worst case about 122. With the
diagnostics it is about 117, worst case about 147. On J0's own basis (× 1.06 for the refinement in place of the
planning factor) the core is about 83, worst case about 104. Both exceed `room` (≤ 90). Unless J0 measures the refined 2D unit well below
today's 5D figure, the second branch applies. The ≤ 165 of ruling 2 would then be the relevant binding, and with
the diagnostics even that is close.

### 5.4 What stops J0

- **A preflight failure:** an input digest, the universe omnifile's size/mtime/inode, the job's QOS or time limit,
  or a deploy that is not clean. The job exits before any run.
- **A failed run.** Its lane records it and goes on. The readout then fails the checks that need the run, and the
  unit readout is INCOMPLETE.
- **The time limit.** A job beyond its limit is stopped by Slurm (`--no-requeue`) and reported. It is never
  resubmitted without the director, and a split of a declared limit is raised first.
- **The readout's own refusals.** It refuses until both jobs have ended, and refuses to overwrite a readout.
- **J0 cannot authorize anything beyond itself.** With J0 PASS and the rule's verdict, the lane writes part B. The
  director binds part B before any production job.

## 6. Readouts fixed now for part B

- **RO-FPS** (R8, Joseph's decision). When `E_R` lands, `N/sec_fps.tex:47-52`'s statement that the
  extended-fiducial control "reproduces the 2D total at the printed precision (`\sigTwoD`)" is re-evaluated:
  - The purity extended-fiducial control's 2D-restricted total (read from its record; the producer is identified in
    part B) is compared with `E_R`'s total at `\sigTwoD`'s printed precision (4 significant digits, e.g. 3.073e-38).
  - The outcome is printed either way: "reproduces" or the measured difference.
  - The extended-fiducial value itself stays on its purity N-D pipeline, labelled.
- **The 2D scope** (R8): RE-2 rebuilds 2D only.

## 7. The registry (ruling 3)

`a-refined-400-31` is in `docs/orchestration/registry/ESTIMATORS.tsv`, defined at `2d-unfolding/re1/re1_2d.py:74`
(`REFINE_OVERRIDE = {"n_estimators": 400, "num_leaves": 31}`). Its summary says it is adopted only when RE-2's
rebuilt result is. Its aliases, each with a cited line and its digest:
- `REFINE_OVERRIDE` (`re1_2d.py:74`);
- `--refine-n-estimators 400 --refine-num-leaves 31` (`run/j0_runs.tsv:3`);
- `a-refined-400-31` (`RE2-PLAN-RULINGS.md:16`).

`check_registry.py` passes, and so does the pre-commit suite (`bash .githooks/pre-commit`).
`results_index.py --write` regenerated `docs/analysis-note/records_estimators.tex`, which gains four generated rows.
That is the only change under `docs/analysis-note/`.

`whatis.py a-refined-400-31` gives the Search line `Search: REFINE_OVERRIDE (re1_2d.py); --refine-n-estimators 400
--refine-num-leaves 31 (re2_driver.py argv); a-refined-400-31 (director ruling R4)`, followed by `@` and the
checkout's HEAD.

**For the director.** The existing `e-R-joint-test` alias "refinement 400/31" (`ALIASES.tsv` row 48, and
`UNRESOLVED-NAMES` row 7 "400/31") no longer identifies one estimator: both (e) and `a-refined-400-31` use the
400/31 refinement. Those rows are outside this lane's file set.

## 8. Storage and durability (R9, Joseph's decision)

**Size estimate**, like-for-like with Stage C, whose durable copy is 90 MB in all (`du` on 2026-10-23):
- Stage C's unfold outputs were 42 MB for 531 `xsec.root` files (about 72 KB each); its S5 products were 31 MB.
- RE-2 adds 175 universe and 37 period outputs.
- **Final products** (`E_R`, `Q_R`, the S5 and C_PL products, the combination, the receipts): about **35 MB**.
- **Everything,** including every unfold output and log: about **120 MB**.

**Durable copies.**
- RE-2's final products go to **HPSS**. HPSS has 161 GiB free (director, from `hpssquota`, 2026-10-23).
- Each archived file has a **recorded `hsi` hash verification**, with its sha256 re-measured against the local
  copy.
- That step is part of part B.
- The intermediates stay on pscratch until integration.

**Pscratch purge risk.** Pscratch is at 85% and purges idle files. The rebuild's pscratch-only inputs are the
universe omnifile (171 GB, mtime July), the July sweep and the period inputs. J0 reads the universe omnifile, the
period inputs and 3 of the July sweep's files, not the whole sweep, so part B should follow J0 promptly. A purged input stops the rebuild (RE2-PLAN §5.4) and cannot be recreated without
re-running the event loop.

## 9. Grant fields (delegation §3.1)

- **Window:** from the BINDING record to J0's readout, or 2026-11-06.
- **Attempts:** one submission of each J0 job; no resubmission without the director; `--no-requeue`.
- **Terminal outcomes:** J0 PASS with the rule's verdict; J0 FAIL (a named check or health row); INCOMPLETE; stopped
  at a limit.

## 10. Decisions for the director before binding

| # | decision | the lane's recommendation |
|---|---|---|
| A1 | the code path: `re2_driver.py` (a `driver_p1.py` copy) in place of the plan's `re1_2d.py` extension (§1) | accept |
| A2 | K1 and the CHK checks at ≤ 1e-8, bitwise reported (§1) | accept |
| A3 | part A / part B, with the deferred items of §1 | accept |
| A4 | J0's grant: ≤ 10.5 node-h inside the 90 | accept |
| A5 | the production rule of §5.3, including J0's charge coming out of the 90 | accept |
| A6 | the `400/31` alias rows of `e-R-joint-test` (§7) | the director's file set |
| A7 | the expected outcome: on current evidence part B needs more than the 90 node-h (§5.3) | note it now, so a fresh binding can be prepared |

## Review record

**Reviewer.** A fresh Claude agent, given the declaration, the code, the plan and the rulings, and none of the
author's working. It made two read-only passes. It worked on the cluster only under its own review directory, and
ran no jobs.

**First pass** (`7f36e9a1`, code `4af4928e`): two blockers, five majors, fourteen minor findings and a list of nits.
The reviewer confirmed:
- every digest;
- the argv and CPUs of every J0 run against its reference;
- the driver diff, read line by line (purity path unchanged; the entry mapping right; the completeness untouched);
- the unit tests, 9/9 on Perlmutter, which caught all three of its mutants.

| finding (severity) | disposition |
|---|---|
| `re2_k1.py` checked health on the `p1ref` rows, so J0 could never PASS (BLOCKER) | fixed; a test over the declared tables |
| srun inherited the table on stdin, so each lane would run only its first row (BLOCKER) | fixed (fd 3, `< /dev/null`); `test_lane_stdin.sh`: 34/34, and 6/34 on the old pattern |
| J0's share of the 90 was spent twice (MAJOR) | `room` = 90 − J0's charge |
| the limits were mean-based, and 1.4× is not the packed factor (MAJOR) | class maxima × 1.81 × 1.06 × 1.25; lanes rebalanced; null and determinism runs early |
| the power checks had no power (MAJOR) | > 1e-6, between runs on the same CPUs |
| nothing detected a wrong refined background stream on the data (MAJOR) | STREAM-1 |
| plan items deferred without saying so (MAJOR) | §1 |
| minor: requeue, pins, readout lock-out, killed steps, `random_state`, unstated deviations, the environment, overclaims, citations, registry wording, J1's step weights, untested guards | fixed, or stated in §1–§2 |

**Second pass** (`7f36e9a1..e3869b39`). Every first-pass finding holds as fixed or as stated, and there is nothing
new at MAJOR or above.
- **STREAM-1** was checked on the real CV omnifile against Stage C S1_001. The injected rows' b·w sum equals
  `hBkgRecoStar2D.Integral()` to 2.2e-16. With the stream off, the sum moves by 3.3e-5. A row exactly on the upper
  edge would fail the check, not pass it, and the file has none.
- **`test_lane_stdin.sh`** gives 34/34, and 6/34 on the `7f36e9a1` sbatch.
- **The arithmetic and the 1.81× basis** reproduce.
- **Its six nits:**
  - the lane-order claim: corrected in §4;
  - J5 could be added without J7: fixed in code and test;
  - an empty ledger read as a charge of 0: now refused;
  - the readout accepted any non-listed state, and the submit wrapper could double-submit J0a: terminal-state list,
    J0a logged first;
  - the orientation figures: J0's own basis added to §5.3;
  - "J0 reads all of them": corrected in §8.
  These are fixed at `668e9b44`.
