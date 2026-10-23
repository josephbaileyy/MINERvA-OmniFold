# RE-2 declaration, part A: the refined 2D path and the J0 pilot (frozen before any job)

**Declared by** the re-1 lane for the director, 2026-10-23. It follows [`RE2-PLAN.md`](RE2-PLAN.md) (PR #275) and the
director's [`RE2-PLAN-RULINGS.md`](RE2-PLAN-RULINGS.md) (PR #277), under DECISION-20261023 (second) item 1.
**No job has run under it.** It takes effect only when the director commits a BINDING record.

**CITABLE FOR:**
- the code RE-2 runs, with its digests;
- J0's inputs, runs, controls and stop rules;
- the rule that turns J0's measured units into a production decision;
- the registry entry `a-refined-400-31`.

**NOT CITABLE FOR:**
- any number: none exists yet;
- a production job (J1–J8). Part B, declared and bound after J0, covers those;
- an adoption, coverage or claim, which are Joseph's.

**In brief:**
- **J0 is two regular jobs, one node each.**
  - It reproduces 15 existing products with the new code's purity arm.
  - It checks the refined arm against the driver and against RE-1's D2.
  - It measures every refined production unit.
- **Projected charge:** 4.7 node-h; worst case 5.9.
- **What J0 decides.** At today's measured 1.4× slowdown, the plan's production would project above the 90 node-h
  grant in its worst case. So J0's units decide, by a rule fixed here (§5.3), whether part B fits the 90, needs the
  diagnostics dropped, or goes back to the director.

---

## 1. What changes from the plan

| item | RE2-PLAN | this declaration | reason |
|---|---|---|---|
| code path (R1) | extend `re1_2d.py` as `re2_2d.py` | **`2d-unfolding/re2/re2_driver.py`: a copy of `driver_p1.py` with blocks marked RE-2** (§2) | Every consumer of the production outputs reads the driver's full ROOT output, not only `hXSec2D`: `analyze_prod.py` reads `hOFCompleteness2D`, `hEffDenSource`, `hOFTruthDenom2D` (`:173-180`), and the period analysis reads truth, completeness and flux. `re1_2d.py` writes an npz with `hXSec2D` alone. The copy keeps `driver_p1.py`'s outputs, so the rollup, C_PL and Stage F read refined products in the same containers. The diff is 59 changed lines (`run/driver.diff`), each in a block marked RE-2 |
| K1 tolerance | bitwise where the reference was made by the same code at the same thread count | **≤ 1e-8 relative on the 205 cells; bitwise reported, not deciding** | Configuration (a) is LightGBM's non-deterministic mode (the deterministic variant is (c)), so a bitwise rerun is not promised even at a fixed thread count. 1e-8 is the XR frozen-repeat criterion, and RE-1's K1-2D used it (2.3e-13). The unit tests show bitwise equality at 1 thread (§2.2) |
| null-universe check | bitwise against the refined CV | **≤ 1e-8** | The universe path reads with `--branch-select derived`; Stage C's purity `NormDISCC:0` reproduced the CV to 1.38e-11, not bitwise (`stageC/production/REPORT.md:65-66`) |
| sequencing | J0, then J1–J8 under one declaration | **part A (this file) declares J0 only. Part B (J1–J8, the post-processing copies) is declared after J0, before any production job** | The director's ruling 2: "the J0 units, not historical ones, set the job limits". Part B's limits need J0's measured units, and its post-processing copies are written before any production product exists |
| J0 price | 4.0 / 5.0 node-h at September units | **4.7 / 5.9** (§4) | `state/gpu-timing-20261023/REPORT.md`: today's unit is about 1.4× slower than its record |

## 2. Code

The code is committed at **`4af4928eaf730abf8978b08518605fca8a1f42a7`** on `re2/declaration-20261023`. That commit adds
only the readout script to `6970abd9`, where the code was smoke-tested (§2.2). J0 runs from a
fresh clone detached at it. The submit wrapper and the job both refuse a deploy that is not a clean checkout at that
sha.

| file | sha256 | role |
|---|---|---|
| `2d-unfolding/re2/re2_driver.py` | `38ff37055af026bd11b1c12a431b31eed522d5038c1bcf020cd47c374d2ddf7c` | the RE-2 driver |
| `2d-unfolding/driver_p1.py` (unchanged) | `3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578` | its original; the Stage C S1/S2/S4(i) driver |
| `run/driver.diff` (`git diff --no-index driver_p1.py re2/re2_driver.py`) | `d235f33cb4fdf3a2440c414f28030ebf7696e46fa3ae395923f6961171dce7ea` | the record of the copy |
| `2d-unfolding/re2/re2_with_helper.py` | `059b67a366fb0748911eb4d03df97fbb6041f6b422371a933a2c832e15080b81` | runs a frozen driver with this checkout's helper (the K1-R reference runs) |
| `2d-unfolding/re2/re2_k1.py` | `caa3acb03508e0a99d1a4c51feadafdd3f28384a3be45fc721ab1f27e82bef79` | J0 control readout |
| `2d-unfolding/re2/re2_units.py` | `1477f45075e3ed0b4fa3375253f580896438b4eddb188c2755d0b0da8fd52172` | J0 unit readout and the production rule |
| `2d-unfolding/re2/tests/test_re2_driver.py` | `db235796f49884ab5200f643d0e03201f22ebe0d435ad319c950e1f50045a982` | 9 tests |
| `2d-unfolding/re2/tests/test_re2_readouts.py` | `ae8c64ee68d543121a1e2b9054aaf852aaed1687970e2520166c68b0436a68a9` | 5 tests |
| `run/j0_runs.tsv` | `383fddfc2904928cd224610cbbd4691371ae36ff9fc2edb78724c136884acbd3` | the 32 runs |
| `run/j0_checks.tsv` | `0123f5efb0fc9f09e29b6724c7af9bf9c20b06ece3f2b39aa0f85d68976fe803` | the 25 checks |
| `run/launch/re2_env.sh`, `re2_j0.sbatch`, `re2_submit_j0.sh`, `re2_ledger.sh` | `13bbb006…`, `1a23e710…`, `0f3e2718…`, `4018b8f1…` | inputs and preflight, the job, the submit wrapper, the ledger |
| `run/launch/re2_j0_readout.sh` | `23a45f5d7e1764c1f5527aab90c6aafc1763627dc9cef4884329aeb7aaf0b6b2` | the login-node readout |

The OmniFold helper is `unbinned_unfolding/python/omnifold.py` `e96234124a31…`. That is the same bytes as the
cluster copy Stage C imported (`stageC/production/DESIGN.md:43`).

### 2.1 What the copy changes

Every change is in a block marked RE-2 (`run/driver.diff`). With none of the RE-2 options and `--bkg-mode purity`, it
runs `driver_p1.py`'s code path. The changes:
1. **`--refine-n-estimators`, `--refine-num-leaves`.** These set the Stay-Positive refinement classifier's size,
   merged into the `random_state` = seed + 3 the driver already passes. The driver's own call passes `random_state`
   alone, so its refinement is always 100/8 (`unfold_2d_omnifold_unbinned.py:402-407,2037-2041`). Both options are
   refused without `--bkg-mode negweight-refined`.
2. **The P1 three-stream and background-only bootstrap, also on `--bkg-mode negweight-refined`.**
   - The background stream's Poisson(1) factor of each `mc_background` entry (seed + 20,000,000, drawn over all
     entries, `driver_p1.py:368-372`) multiplies that entry's injected −w row.
   - The rows are matched by `re2_injected_entries`, which uses the loader's own fiducial tests on its fill rows.
   - The data rows keep +1 × b_data, and the signal MC rides b_truth, as in the purity arm.
   - The refinement is refitted on the resampled signed sample.
   - The completeness keeps the un-resampled truth weights (KNOWN_ISSUES 84, unchanged).
   - The run refuses an input with signal fakes, or an injected-row count that differs from its entries.
3. **The helper import.** It comes from this checkout, not from the fixed path `/pscratch/…/MINERvA-OmniFold/…`
   (OI-136).
4. **A `re2Refinement` record** in the output: the classifier parameters, the clipped fraction, the signed and
   refined sums and their ratio, the row counts, and whether the background stream ran.

### 2.2 Tests

- **`test_re2_driver.py`, 9/9 passed on Perlmutter.** It ran on a login node, `taskset -c 8-11`, root_6_28,
  LightGBM 4.6.0, on files byte-equal to the committed ones (re-hashed after the run). It runs `driver_p1.py` and
  `re2_driver.py` on a synthetic omnifile with one vertical universe, and compares every histogram's contents and
  errors bit for bit at one thread:
  - **The purity arm equals `driver_p1.py`** on the CV, a three-stream replica, a background-only replica and a
    universe (`--branch-select derived`). The universe moves the result.
  - **Without a size, the refined arm equals `driver_p1.py`'s own `negweight-refined`** (CV and universe).
  - **400/31 reaches the classifier.** The recorded parameters are `{random_state 45, n_estimators 400,
    num_leaves 31}`, and the result moves.
  - **The refined three-stream bootstrap with all factors 1 equals the refined CV.**
  - **The background stream's signed sums equal an independent recomputation** from the fixture's rows and the
    stream's draws, both background-only and three-stream. With the stream off, the test fails.
  - **The guards refuse** the size options without the refined mode, and the P1 streams with plain `negweight`.
- **`test_re2_readouts.py`, 5/5 passed locally** (python3.13, PyROOT). It covers:
  - K1 pass and fail, both directions, including the digest check and the power check;
  - refinement health: clipping, and a wrong size;
  - all three branches of the production rule;
  - that the unit is the class maximum;
  - that a missing step stops the readout.
- **A smoke run from a clean clone at `6970abd9`.** On the fixture, through the OI-136 guard,
  `re2_with_helper.py driver_p1.py` and `re2_driver.py` both ran with rc 0 and `outside_expect_root=0`. Both used the
  clone's helper (`e96234124a31…`), and their `hXSec2D` are bit-identical.
  - A dry expansion of all 32 `j0_runs.tsv` rows with `re2_env.sh` found every path present and nothing unexpanded.

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
| Stage C C0_cv, C0_unit, S1_001, S2_001 | `/pscratch/…/2d-closeout-stageC-production-20261015/out/2dc_P_{C0_cv,C0_unit,S1_001,S2_001}/xsec.root` | `71249143…`, `f1699e66…`, `c67bb587…`, `501bb020…` |
| Stage C S4U at seed 42: MaCCQE:0, Flux:23, NormDISCC:0 | `…/out/2dc_P_S4U_{MaCCQE0,Flux23,NormDISCC0}_s42/xsec.root` | `26bde3ba…`, `87e65b2c…`, `84f822e3…` |
| July sweep (pn) | `…/2d-unfolding/uq/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_{MaCCQE_0,Flux_23,NormDISCC_0}.root` | `d17b45c6…`, `eb8414af…`, `5819b46b…` |
| Stage C S3 lateral | `…/out/2dc_P_S3_BeamAngleX0/xsec.root` | `5aac876a…` |
| period unfolds | `/pscratch/…/2d-closeout-period-unfold-20261014/out/pu_{CTRL,PA}_s42/xsec.root` | `5582d19e…`, `9e59f456…` |
| RE-1 D2 (the refined data unfold) | `/pscratch/…/methods-paper/re1-20261022/out/2d/d2_data_refined.npz` | `71ca3e5f…` |

Each reference's argv is recorded in its own `runArgv`. Each J0 run in `j0_runs.tsv` repeats that argv: the same
options and the same CPUs (64 for the CV and replica classes and the periods, 128 for universes and laterals), with
memory at 1,905 MB per CPU, as Stage C allocated it.

## 4. J0: runs, compute and storage

| job | QOS | node | lanes | runs (`j0_runs.tsv`) | projected | limit | worst charge |
|---|---|---|---|---|---|---|---|
| J0a `re2-j0a` | regular, `--exclusive` | 1 | 2 × 128 CPUs | 9 universe runs, then 3 lateral runs | 3.0 h | 3:45 | 3.75 node-h |
| J0b `re2-j0b` | regular, `--exclusive` | 1 | 4 × 64 CPUs | 20 runs: CV, unit-factor, replicas, periods | 1.7 h | 2:10 | 2.17 node-h |
| **J0** | | | | 32 runs | **4.7 node-h** | | **5.9 node-h** |

**The projections.**
- The basis is the Stage C units × 1.4, from the gpu-timing report, × 1.06 for the refinement where it runs (the
  measured C2 ratio).
- J0a lane 1: 9 universe runs at about 1,150–1,220 s each. Lane 2: 3 laterals at about 3,360 s, plus the lateral's
  hash.
- J0b: 5 runs per lane at about 1,000–1,450 s.
- Each run is one `srun` step named by its label, so `sacct` times every run.

**What runs:**
- **J0a, 128 CPUs.**
  - Purity: universes MaCCQE:0, Flux:23 and NormDISCC:0 (K1-U); lateral BeamAngleX0 (K1-L).
  - Reference and RE-2 refined without a size on MaCCQE:0 (K1-R).
  - Refined 400/31: universes MaCCQE:0, Flux:23, MaRES:0 and NormDISCC:0 (null check); lateral BeamAngleX0, run
    twice (determinism).
- **J0b, 64 CPUs.**
  - Purity: CV (K1-C), unit-factor control, S1 replica 1, S2 replica 1 (K1-B), periods CTRL and PA (K1-P).
  - Reference and RE-2 refined without a size on period PA (K1-R).
  - Refined 400/31: CV (vs D2), unit-factor control, three-stream replicas with bootstrap seeds 1–8 (seed 1 twice,
    determinism), period PA.

**The ceiling.**
- J0 is booked under the 2D closeout ceiling (ruling 4).
- **Spent under it: 39.4714 node-h.** This is RE2-PLAN §4.3, re-derived from `sacct`; no 2D closeout job has run
  since, and RE-1 is not re-booked.
- J0's worst case leaves the 90 node-h grant at ≥ 84.1 for part B.

**Storage.**
- Outputs go to `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/j0/` (`out/<label>/xsec.root`, `logs/`,
  `inventory/`, `readout/`).
- Nothing is written under a checkout, or to CFS.
- A run whose output directory exists is not run again.

## 5. Controls, readouts and rules, fixed now

### 5.1 Controls (`run/j0_checks.tsv`, read by `re2_k1.py`)

Every check compares `hXSec2D` on `E_U`'s 205 reported cells.

**PASS rule.**
- The largest relative difference must be ≤ 1e-8, and both files must report the same cell set.
- Where the reference has a digest, it must match.
- Bitwise equality over all 224 cells is reported but does not decide.

| id | test (J0 run) | reference | what it shows |
|---|---|---|---|
| K1-C1, K1-C2 | purity CV | Stage C C0_cv; `E_U` | the copy's purity path reproduces the CV and the adopted central value |
| K1-C3 | purity unit-factor | Stage C C0_unit | the three-stream path with factors 1 |
| K1-B1, K1-B2 | purity S1 and S2 replica 1 | Stage C S1_001, S2_001 | the bootstrap streams, replica for replica |
| K1-U1–U3, K1-U4–U6 | purity universes | Stage C S4U at seed 42; the July sweep | the universe path, selective read |
| K1-L1 | purity lateral | Stage C S3 | the lateral path |
| K1-P1, K1-P2 | purity periods | `pu_CTRL_s42`, `pu_PA_s42` | the period path |
| K1-R1, K1-R2 | RE-2 refined, no size | `driver_p1.py` refined, same job, same CPUs | the copy's refined path equals the driver's |
| K1-D1 | RE-2 refined 400/31 CV | RE-1 D2 | equals the refined data unfold C2 was read against |
| CHK-unit | refined unit-factor | refined CV | the refined bootstrap with factors 1 is the CV |
| CHK-det1, CHK-det2 | a refined replica and a refined lateral, run again | their first runs | run-to-run stability at 1e-8 |
| CHK-null | refined NormDISCC:0 | refined CV | the null universe in the refined arm |
| POW-1–POW-4 | refined CV; refined replica 1; refined MaCCQE:0; refined lateral | purity CV; refined CV (×3) | the refined result, a replica, a universe and a lateral **differ** from what they are compared with (power) |

**Refinement health.** Every refined run must have a clipped fraction ≤ 0.01 and refined/signed in [0.99, 1.01]. A
run that declares 400/31 must record `n_estimators` 400 and `num_leaves` 31.

**Verdict.** J0 PASSES only if every check and every health row passes.

### 5.2 Seeds

- Estimator seed 42: OmniFold `random_state` 42/43/44, refinement 45.
- Bootstrap seeds 1–8, as Stage C's S1_001–008 used.
- No other seed.

### 5.3 The production rule (`re2_units.py`)

**The measured unit.**
- A run's node-h is its step's ElapsedRaw × AllocCPUS / 256 / 3600.
- The refined unit of each production class is the **maximum** over J0's runs of that class.
- Counts are RE2-PLAN §4.2's:
  - 3 central;
  - 175 universes;
  - 10 laterals;
  - 300 S1;
  - 80 S4(i);
  - 37 periods;
  - diagnostics: 100 S2 and 39 S4(ii).

**The rule.**
- **Core worst case (1.25 × projected, J1/J2/J3/J4/J6/J8) ≤ 90:** part B is declared within the 90 node-h grant.
  - The diagnostics J5/J7 are included only if their total worst case also fits in 90.
- **Core worst case > 90:** no production job starts. The projection goes to the director for a fresh binding
  (ruling 2).
- **A class or a step not measured:** the readout is INCOMPLETE, and no production job starts.

**For orientation, not a rule.** The plan's units × 1.4 put the core at about 81 node-h (worst 101) and the total
with diagnostics at about 96 (worst 120). If J0 confirms the 1.4×, the rule's second branch applies.

### 5.4 What stops J0

- **A preflight failure:** an input digest, the universe omnifile's size/mtime/inode, or a deploy that is not clean.
  The job exits before any run.
- **A failed run.** Its lane records it and goes on. The readout then fails the checks that need the run.
- **The time limit.** A job beyond its limit is stopped by Slurm and reported. It is never resubmitted without the
  director. A split of a declared limit is raised first.
- **J0 cannot authorize anything beyond itself.** With J0 PASS, the lane writes part B: production jobs J1–J8 with
  limits from J0's units, and the post-processing copies listed in RE2-PLAN §3. The director binds part B before any
  production job.

## 6. The registry (ruling 3)

`a-refined-400-31` is in `docs/orchestration/registry/ESTIMATORS.tsv`, defined at `2d-unfolding/re1/re1_2d.py:74`
(`REFINE_OVERRIDE = {"n_estimators": 400, "num_leaves": 31}`). Its aliases, each with a cited line and its digest:
- `REFINE_OVERRIDE` (`re1_2d.py:74`);
- `--refine-n-estimators 400` (`re2_driver.py:1528`);
- `a-refined-400-31` (`RE2-PLAN-RULINGS.md:16`).

`check_registry.py` passes, and so does the pre-commit suite (`bash .githooks/pre-commit`: 13 checks).
`results_index.py --write` regenerated `docs/analysis-note/records_estimators.tex`, which gains four generated rows.
That is the only change to a file under `docs/analysis-note/`.

The `whatis.py` Search line: `Search: REFINE_OVERRIDE (re1_2d.py); --refine-n-estimators 400 (re2_driver.py);
a-refined-400-31 (director ruling R4) @ c1578ea812a8`.

**For the director.** The existing `e-R-joint-test` alias "refinement 400/31" (`ALIASES.tsv` row 48, and
`UNRESOLVED-NAMES` row 7 "400/31") no longer identifies one estimator. Both (e) and `a-refined-400-31` use the 400/31
refinement. Those rows are outside this lane's file set.

## 7. Storage size estimate (R9, for Joseph)

**Like-for-like with Stage C**, whose durable CFS copy is 90 MB in all (`/global/cfs/…/2d-closeout-stageC-production-20261015/`,
`du` on 2026-10-23):
- its unfold outputs were 40 MB for 531 files (`xsec.root` about 72 KB each);
- its S5 products were 31 MB (`production_cov.npz` 16.9 MB, `uq_production_covariance.root` 14.2 MB, `s5.json`).

RE-2 adds 175 universe outputs (Stage C reused the July sweep) and 37 period outputs:
- **Final products** (`E_R`, `Q_R`, the S5 and C_PL products, the combination, the receipts): about **35 MB**.
- **Everything,** including every unfold output and log: about **120 MB**.

The director's recommendation is HPSS for the final products; the intermediates stay on pscratch until integration.

## 8. Decisions for the director before binding

| # | decision | the lane's recommendation |
|---|---|---|
| A1 | the code path: `re2_driver.py` (a `driver_p1.py` copy) in place of the plan's `re1_2d.py` extension (§1) | accept |
| A2 | K1 at ≤ 1e-8 with bitwise reported, and the null check at ≤ 1e-8 (§1) | accept |
| A3 | part A / part B: bind J0 now; part B after J0 | accept |
| A4 | J0's grant: ≤ 6.0 node-h inside the 90 | accept |
| A5 | the production rule of §5.3 | accept |
| A6 | the `400/31` alias rows of `e-R-joint-test` (§6) | the director's file set |

R8 and R9 are with Joseph (rulings 5). This part does not depend on them.

## Review record

To be completed by the independent review before the PR.
