# RE-1 amendment declaration: C2, P3, P4 and the movement table (frozen before any run)

**Declared by** the re-1 lane for the director, 2026-10-22, under
[`RE1-LANE-BRIEF.md`](../../lanes/RE1-LANE-BRIEF.md) and [`COMMON-RULES.md`](../../lanes/COMMON-RULES.md). It amends
[`RE1-SPEC.md`](../RE1-SPEC.md) where RE-1's first pass ([`RE1-REPORT.md`](../RE1-REPORT.md) §2–3) found the frozen
code could not run it. **No job has run under it.** It takes effect only when the director commits a BINDING record.

**CITABLE FOR:** what run 2 of RE-1 runs, the code and inputs it uses, its controls, its readout rules and its cap.
**NOT CITABLE FOR:**
- any number (none exists yet);
- a change to the adopted 2D result, which is Joseph's decision;
- a covariance or coverage for configuration (e);
- a judgement on whether the background-treatment obligation (OI-6) is met.

## 1. What changes from RE1-SPEC

| item | RE1-SPEC | this amendment |
|---|---|---|
| C2 | needs a 2D path at 400/31 with background in the pseudo-data | a new path, `2d-unfolding/re1/re1_2d.py` (§2.1) |
| P3, P4 | "by the frozen 3D/4D code paths, if those paths support the refinement unchanged" | the frozen dimension-generic configuration-(e) path that made P5 (`s5e_candidate.py --candidate R` over `s5n_pseudo.py --data`). It runs on 3D/4D inputs written by the frozen dumpers. No unfold code is new (§2.2) |
| products for the movement table | not in the spec | D2 (2D refined, data), and P3c, P4c, P5c (deterministic purity, data); see §4 |
| grant | ≤ 30 node-h, Perlmutter work before 2026-10-21 04:00 PDT | ≤ 6.0 node-h for this run, inside RE-1's remaining 29.947 (§6). The 04:00 cutoff was for the maintenance, which ended 2026-10-21 17:28:57 PDT |

Everything else in RE1-SPEC stands. That covers products (P5) and (F), controls K1–K3, the outcome rule of §3, and the output-location rule (nothing on CFS).

## 2. Code

The code is at commit **`ec829e28559af987f9ca69b60ad0f00ad02ce0ea`** on branch `re1/declaration-20261022` (the first
code commit was `7f509004`). The runs use a fresh clone detached at that sha. The submit wrapper and every job refuse
a deploy that is not a clean checkout at it.

| new file | sha256 |
|---|---|
| `2d-unfolding/re1/re1_2d.py` | `b9c7e1da65afe0ccbe02714031f94000b01af0889b7c0cff6ea1da00f7ca75b0` |
| `2d-unfolding/re1/re1_2d_analyze.py` | `8bd9676019c3ec0a72d20897332d498d622fbf547e3f479e9b8f95d3a58aa555` |
| `2d-unfolding/re1/tests/test_re1_2d.py` | `3396d17cac0df2a50b98b0eb10969f7a8ac55a105a2c6ee2c878cd5e52bf8f33` |
| `nd-unfolding/re1/re1_nd_movement.py` | `c562e365f8a3e29fdee708a50fabd08da8586ead23ac95f8688fe2228c268518` |
| `nd-unfolding/re1/tests/test_re1_readouts.py` | `6727ff2a35ac000c72176dad71df979b7adfadbff44c8e32517f52d6abed5d9e` |
| `run2/launch/re1_env.sh` | `29726108adb5a4b0333c4a23dec53adfb2bd916f9a3dd82d9e1657ac370ce079` |
| `run2/launch/re1_inputs.sbatch` | `3d9e752c289f90c6f01525a69ba0740217b0cff3335c7d5eec860a93b3f4e40a` |
| `run2/launch/re1_nd.sbatch` | `9d7f395e0fb63577c0b747595514964c1c508017d1328e1bddcf0ef5840309aa` |
| `run2/launch/re1_2d.sbatch` | `470208e80a95a0af9ff18350f95811c781eedce57b2aa8bed908dad0313542f6` |
| `run2/launch/re1_submit.sh` | `b68e7a9fafa0019c99a523232e734fd89b973e49300f34bf633ccb73a9ffd9e5` |

Frozen modules called unchanged, at the same sha:

| module | sha256 | note |
|---|---|---|
| `2d-unfolding/unfold_2d_omnifold_unbinned.py` | `74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56` | loaders, purity, `refine_stay_positive`, completeness, extraction |
| `unbinned_unfolding/python/omnifold.py` | `e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a` | the 2D OmniFold helper, imported from the deploy (never the driver's hard-coded path) |
| `nd-unfolding/s5n_pseudo.py` | `8981f97b96b418cfe46f1e940cb120f174053d7d3429f3b0b01a229c6c02ee6c` | equal to P5's recorded digest |
| `nd-unfolding/s5c_pseudo.py` | `d81d4f46fb55f25fdf7ce2e4b9a9a63bf876beaf754bdc250eee974579e11f5d` | equal to P5's |
| `nd-unfolding/s5c_unfold.py` | `510d749a2e82fa448de6172753ae2adc9ebd81a89d4f18bf76beb5faa8bb3968` | equal to P5's |
| `nd-unfolding/s5e_candidate.py` | `bda8c48ce2365e173bbba083b18233d6f6b7c2dfbab5179156073860c8281ec7` | equal to P5's |
| `nd-unfolding/s5e_deform.py` | `6726ff99c7787d1ee6dff7fa5d08df88f9df76285d98c4c462f964ac6164779f` | equal to P5's |
| `nd-unfolding/omnifold_nn_core.py` | `24f87f119073c4f125c2f753310507d4375b6f8a1b7751e59d3615dd50e90582` | equal to P5's |
| `nd-unfolding/xsec_nd.py` | `454001f3c9ac3aa6485d184aadb8aba65dd71dba124816962b9c3b6344920fa5` | equal to P5's |
| `nd-unfolding/nn_dump_inputs.py` | `6e8061f836e9ac941f24ca518907c1c94efe772e9d92cf29eeeb940062c8b685` | 3D/4D npz writer |
| `nd-unfolding/s5c_dump_bkg.py` | `c4e87d18a4003e6795ca78eba8d704c41060ef91c41e838a9cff69939db20982` | background dump. It refuses unless it reproduces the npz's purity weights exactly |
| `nd-unfolding/unfold_nd_omnifold_unbinned.py` | `8a9bc84ecea206a8f3f59913a18e41fab31b47ebdbeac83cc7bb16f25b75c9c4` | the ND collectors the dumpers call |
| `nd-unfolding/mnv_guarded_run.py` | `30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b` | OI-136 guard on every Python run, with the deploy as the only admitted tree |

The 2D driver's digest differs from the one P5 recorded (`8ebe0277…`). The s5n path uses only its
`refine_stay_positive` and `_make_bkg_classifier`, and K1-ND below tests the whole path end to end.

### 2.1 The 2D path (C2, D2)

`re1_2d.py` imports the frozen driver and its helper and calls them as module functions. It edits nothing and
re-implements none of them.
- **The estimator** is the adopted `E_U` one: the driver's `OmniFold_helper_functions.omnifold` call
  (`unfold_2d_omnifold_unbinned.py:2080-2097`), with LightGBM at 100 trees, 8 leaves and learning rate 0.1;
  `random_state` 42/43/44; 5 iterations; MC weights.
- **Arm (i), purity:** `build_measured_training_2d`.
- **Arm (ii), refined:** the signed sample {observed at +count} ∪ {template at −weight}, in the driver's order and
  with every row, refined by `refine_stay_positive`. Its LGBMClassifier takes `random_state` 45 with 400 trees and
  31 leaves, the driver's defaults otherwise. The capacity is the one setting the driver cannot reach
  (`:2037-2042`).
- **Recorded and verified on every product:**
  - every OmniFold fit's parameters: 10 classifier fits and 5 regressor fits, seeds {42, 43, 44}, 100/8;
  - the refinement classifier's parameters;
  - the refinement evidence (`s5n_pseudo.refinement_evidence`);
  - the module origins;
  - the CPU affinity and joblib's counts. LightGBM's default thread count follows these, not `OMP_NUM_THREADS`
    (measured on login15, LightGBM 4.6.0).
- **`dump`** reads the omnifile once with the driver's loaders, as `main()` does, and caches the arrays. It refuses
  signal fakes; post-Phase-18 inputs have none.

**The C2 pseudo-experiments** follow the s5n sampling model (`s5n_pseudo.build_pseudo`), in 2D, at nominal truth:
- the same keyed splits (`s5c_pseudo.half_mask`, `split_key_for`, `bkg_split_key`), so signal A/B and background
  C/D;
- the same Poisson draws in the same order;
- the unfolding MC is half A, at ×2;
- the truth is half B's truth through the analysis's own extraction.

**The departure from s5n, for the director to bind (D2 in §7):** both arms unfold the **same** pseudo-data against
the **same** template D.
- Purity takes D's histogram (×2) as its background prediction.
- The refinement takes D's rows at −2w.
- s5n's purity baseline was instead `s5c_pseudo.build_experiment`: background drawn from every row, with the full
  prediction subtracted. That gives different pseudo-data from its refined arm.
- Pairing the arms isolates the background treatment, and it makes the C2 arm difference a paired difference.

**Tests.**
- Locally: 13 of 15 pass, and the 2 that need LightGBM are skipped.
- On Perlmutter (login15, root_6_28, pinned to 4 CPUs): 15 of 15 pass. Among them:
  - the draw equals `s5n_pseudo.build_pseudo` for seeds 1, 2 and 20;
  - purity weights equal `s5c_pseudo.purity_weights`;
  - the 400/31 override reaches the classifier, and a classifier without it is refused;
  - the fit checks refuse a wrong seed, capacity or count.
- **Driver equivalence**, on a synthetic omnifile:
  - this path's purity `hXSec2D` equals the frozen driver's (`--seed 42 --estimator lgbm`) bit for bit;
  - with the override removed, its refined `hXSec2D` equals the driver's `--bkg-mode negweight-refined` bit for bit;
  - with the override, the two differ.

### 2.2 The 3D/4D path (P3, P4)

**P3 and P4 are made by P5's own configuration-(e) code,** run on 3D/4D inputs:
- `nn_dump_inputs.py --axes eavail` (3D) or `--axes eavail,q3` (4D) writes the npz;
- `s5c_dump_bkg.py` writes the background dump;
- the unfold is `s5e_candidate.py --candidate R -- --data --bkg-mode negweight-refined --estimator-seed 42
  --threads 32 --iters 5`.

**The (c) baselines** P3c, P4c and P5c are `s5n_pseudo.py --bkg-mode purity --data` on the same inputs. That is the
same deterministic estimator with the npz's purity weights, so (e) − (c) isolates the background treatment.

**This is the ND reader on the 3D omnifile, not the 3D driver.** The current 3D central value (a) was made by the 3D
driver with LightGBM seed 1. The current 4D one was made by the ND driver, unseeded. So (c) − (a) mixes three
things: the reader (the ND collectors drop non-finite truth; `unfold_nd_omnifold_unbinned.py:433-437`), the
deterministic estimator, and the seed. The table reports all three differences.

The readout `re1_nd_movement.py` passes its 9 local unit tests. They check:
- known movements;
- trunk σ mapped through `hRowIndex5D`;
- refusals: wrong digest, (e) not at 400/31, swapped arms, mismatched inputs;
- the K1, C2 and flag rules of `re1_2d_analyze.py`, in both directions.

## 3. Inputs (the existing ME-FHC inputs; no newer release)

All are on Perlmutter, measured 2026-10-22 on login15.

| input | path | sha256 |
|---|---|---|
| 2D CV omnifile (XR's L0 input; L0 regenerated `E_U` from it to 1.4e-11) | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC.root` | `43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df` |
| flux | `…/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root` | `d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316` |
| 3D omnifile | `…/3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root` | `7db0c27c8ba25395285fbac237700c390fedd43314c485af1c8b01f86e4dd4bd` |
| 4D omnifile | `…/nd-unfolding/runEventLoopOmniFold_4D_MEFHC.root` | `5a1a7b9df2bb07bcc00b710a5b0d3d553bd7f76bbe8306004e43aba1c7179a40` |
| 5D npz (P5's) | `…/nd-unfolding/of_inputs_5d.npz` | `07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f` |
| 5D background dump (P5's) | `/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz` | `2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955` |
| P5 (K1-ND reference) | `/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz` | `fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c` |
| `E_U` (K1-2D reference, central (a) in 2D) | `…/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` | `4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c` |
| current 3D central (a) | `…/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root` | `0dd94830821576a3b060fae2d4a20564610c535ed06046cd1eb05cd11885dd59` |
| current 4D central (a) | `…/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root` | `1fb8250820c00428fc547cb05aa95535023146723acdccb61f615f3fa763f9d2` |
| current 5D central (a) | `…/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | `630306e20e4e175bde8b459174842a58e4f4b5a694b8a5018e730a952820aec8` |
| S5 production covariance (2D σ_stat) | CFS `m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz` (read only) | `6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc` |
| Q, the adopted 2D uncertainty (2D σ_total) | CFS `m3246/josephrb/2d-closeout-playlist-combination-20261017/s5_plus_playlist.npz` (read only) | `8ccb4d723c3dbf737a7fb1d5236e5e25409c41b42b64ac55dccbbc12f595600e` |
| adopted 5D trunk (5D σ_total) | `…/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz` | `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5` |

Every input is re-hashed by the job or readout that reads it, which refuses on a mismatch. The 3D/4D npz and
background dumps are new; their digests go into the run's `SHA256SUMS.inputs` and the report.

## 4. Runs and products

Seeds:
- estimator seed 42 throughout;
- C2 pseudo-seeds **1–20**, the same in both arms (one pseudo-data set per seed, unfolded twice);
- split keys derived from each seed as in s5n.

| job | QOS | runs | products (pscratch `/pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/`) |
|---|---|---|---|
| J1 `re1-inputs` | regular, 1 node | three chains at once: 2D `dump`; 3D `nn_dump_inputs` → `s5c_dump_bkg`; the same for 4D | `2d/cache.npz`, `3d/of_inputs_3d.npz`, `3d/bkg_3d.npz`, `4d/of_inputs_4d.npz`, `4d/bkg_4d.npz` |
| J2 `re1-nd` (after J1) | regular, 1 node | six data unfolds at once, each 42 CPUs with LightGBM `num_threads` 32: K1-ND (P5 rerun), P5c, P3, P3c, P4, P4c | `5d/k1_p5_rerun.npz`, `5d/p5c.npz`, `3d/p3.npz`, `3d/p3c.npz`, `4d/p4.npz`, `4d/p4c.npz` |
| J3 `re1-2d` (after J1) | regular, 1 node | four 64-CPU streams: K1-2D (purity, data), D2 (refined, data), C2 seeds 1–20 with both arms per seed | `2d/k1_data_purity.npz`, `2d/d2_data_refined.npz`, `2d/c2/nominal_s{1..20}.npz` |
| readouts | login node | `re1_2d_analyze.py` (K1-2D, D2, C2); `re1_nd_movement.py` for 3D, 4D and 5D | JSON and TSV, committed with the report |
| F (after the readouts) | debug, 1 node | K3, then the figure regeneration of §5.3 | under `out/f/` |

## 5. Controls and readouts, fixed now

### 5.1 Controls

- **K1-2D.** The purity data unfold from the new path equals `E_U`'s `hXSec2D` on its 205 reported cells, with a
  maximum relative difference of at most **1e-8** (the XR frozen repeat criterion), and reports the same cell set.
  - Bitwise equality is reported separately.
  - XR's L0 reached 1.4e-11 at 64 threads, and J3 runs at 64.
  - **Failure:** C2 and D2 are not used, and the report says so.
- **K1-ND.** The P5 rerun's `xsec_flat` equals P5's (`fb5cc679…`) **bit for bit**: the deterministic configuration
  at the same `num_threads` 32, with the s5 modules at P5's recorded digests.
  - **Failure:** P3, P4, P3c, P4c and P5c are not used, and the report says so.
- **The dumpers.** `s5c_dump_bkg.py`'s built-in check (it reproduces the npz's purity weights and measured
  coordinates exactly, or exits 5) runs for 3D and 4D.
- **K2.** No recorded 2D purity closure with background exists (RE1-REPORT §2), so arm (i) is reported only.
- **K3,** before any figure input is swapped. Each figure producer in §5.3 reproduces its current output bitwise from
  the current input, or the figure is not regenerated and the report says so.

### 5.2 Readouts

**σ definitions.**
- **2D:**
  - σ_stat is `sqrt(diag(stat))` of the S5 production covariance;
  - σ_total is `sqrt(diag(total_plus_C_PL))` of Q;
  - the cells are `E_U`'s 205 reported cells, checked to reproduce both files' `cells_x_EU`.
- **5D:** σ_total is `sqrt(diag(hCov_combined5d_total_uthrow))` of the trunk on its 10,694-cell support.
  - **The adoption record's four measurements (§4 of
    `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`) travel with every number in these units.**
- **3D and 4D:** no quotable covariance exists, so those movements are relative only (decision D4 in §7).

**C2,** per RE1-SPEC §1 and §3:
- for each arm, the per-cell mean residual against truth and its SE, in σ_stat;
- the paired arm difference (ii) − (i), per cell, in σ_stat and σ_total, with its SE;
- the integrated arm difference as a fraction of the integrated truth.
- **Rule:** if any cell's mean arm difference exceeds 1 σ_stat, or the integrated difference exceeds 0.5 %, it is
  **FLAG** (for Joseph's decision on the adopted 2D result). Otherwise it is **NO-FLAG**: the refinement does not
  change the 2D result at that level.

**The movement table** (descriptive, for Joseph's background-treatment revisit; no decision attached):
- **2D:** D2 − K1-2D, per cell, in σ_total and σ_stat, and the integral change. K1-2D is `E_U` regenerated, and it is
  used only if K1 passes.
- **3D, 4D, 5D:** (e) − (c), (e) − (a) and (c) − (a), per cell, as relative changes, with percentiles, counts and
  the integral change. For 5D, these are also given in trunk σ_total on its support.

### 5.3 F: figures and numbers

These follow RE1-SPEC (F): the existing producers, with only the input product changed, writing into `out/f/`. They
never write into `docs/analysis-note/`. The research list (cited in the report) is:
- **from 3D:**
  - `plot_eavail_spectrum.py` (`fig:eavail`);
  - `compare_to_paper_fullcov.py` (`fig:eavail-marg`);
  - `redraw_central_only.py --genfig` (`fig:3dmodels`, `fig:modedecomp`, `fig:mec`);
- **from 4D:**
  - `redraw_central_only.py --xsec4d` (`fig:ascencio`);
  - `q3_excess_projection.py` (`fig:q3excess`);
  - `pet/pet_vs_gbdt.py`;
- **printed numbers:** `sec_3d.tex` and `paper_body.tex:480-484`.

P3 and P4 are put in each producer's input container by the production writers (the 3D driver's
`numpy_to_th3d`/`hXSec3D` for 3D, and `write_thnd` for 4D), as RE-1's `p5_to_root.py` did. The readback through each
producer's own loader must be bitwise, or nothing is kept. The converters are committed, with their digests in the
report, before they run. If a producer needs an input that cannot be regenerated, that figure is reported as not
regenerated.

## 6. Compute and storage

| job | projected | limit (1.25×) | worst-case charge |
|---|---|---|---|
| J1 | 1.5 h | 1:52 | 1.867 node-h |
| J2 | 0.75 h (P5's data unfold took 693 s at 32 threads) | 0:56 | 0.933 node-h |
| J3 | 1.75 h | 2:11 | 2.183 node-h |
| F | 0.3 h, debug | 0:22 | 0.367 node-h |

- **Cap for this declaration: 6.0 CPU node-h** on m3246, inside RE-1's remaining 29.947 (0.0531 used).
  - QOS: regular, or debug for F; never premium.
  - Every job is under 12 h.
  - Every job is ledgered in `re1/run2/ledger.tsv`, with job id, QOS, elapsed and charge.
  - A job beyond its limit is stopped by Slurm, and the report says so; it is never resubmitted without the
    director.
  - A failed job is resubmitted at most once, and only for a cause outside the declared code, such as node
    failure or preemption. Its charge counts toward the cap.
- **Storage.**
  - Everything goes to `$PSCRATCH` (`/pscratch/sd/j/josephrb/methods-paper/re1-20261022/`), and nothing to CFS.
  - Expected size is under 15 GB: the 2D cache and the 3D/4D npz files at 1–3 GB each, and small products.
  - Every product's path and sha256 goes into the report's receipts.
  - The intermediates are deleted, or their retention is raised with the director, once the report merges.

## 7. Decisions for the director to bind

The re-1 lane's recommendation is the first option of each.

| # | decision | recommended | alternative |
|---|---|---|---|
| D1 | the P3/P4 route | P5's frozen configuration-(e) path on 3D/4D inputs written by the frozen dumpers (§2.2) | extend copies of the 3D and ND drivers to take the 400/31 refinement (new unfold code, a K1 needed for each) |
| D2 | C2 pairing | both arms on the same pseudo-data and template D (§2.1) | s5n exactly: purity from `s5c_pseudo.build_experiment`, unpaired |
| D3 | added products | D2, P3c, P4c, P5c, so the movement table isolates the background treatment (about 0.9 node-h of the cap) | (e) against (a) only |
| D4 | 3D/4D yardstick | relative change only. No 3D/4D covariance is quotable, and projecting the trunk would be a new covariance product that RE-1 does not build | a labelled, non-quotable projection of the 5D trunk to the 3D/4D grids |
| D5 | K1 tolerances | K1-2D ≤ 1e-8 relative; K1-ND bitwise | — |
| D6 | the cap | 6.0 node-h for run 2 | — |

## 8. What this cannot authorize

The following are outside it:
- a change to the adopted 2D result or its uncertainty;
- any claim, wording or deliverable edit (the director integrates);
- an adoption of P3, P4 or P5 as central values beyond DECISION-20261020 item 1;
- a covariance or coverage for configuration (e);
- a verdict on OI-6;
- a switch to the newer open-data release;
- any job before the director's BINDING record.
