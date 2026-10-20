# SF-1 report: the null distribution and the unfolding-simulation size

**Run by** a Claude agent for the director, 2026-10-19, under [`SF1-SPEC.md`](SF1-SPEC.md), which was frozen before any run. The charge was 5.445 of the 25 CPU node-h granted, on regular QOS. All 600 quarter-simulation products exist. Scripts, tables, the input manifest, the ledger and the results are in [`sf1/`](sf1/); the products are on pscratch. The agent could not write this file, so the director saved its final report verbatim below.

**Outcome:** all three shape tests **PASS** (§4 of the spec). Under the most adverse adjustment the spec allows, NuWro shape goes to k = 2/1751 (p = 0.0017) against its Holm threshold of 0.05, and GENIE CV and GENIE+MEC shape stay at k = 0. All ten family decisions remain rejected. No test shows a resolved change of location, scale or tail between half and quarter simulation (|Δ| ≤ 0.074 null SD; s between 0.975 and 1.010). The only resolved effect is a small positive mean paired shift, 0.006–0.034 null SD.

**CITABLE FOR:** the robustness of the three smallest-margin shape decisions to the unfolding-simulation size, within the measured change from half to quarter simulation, under the spec's conservative extrapolation.

**NOT CITABLE FOR:** a test of the data process itself, which would need an independent simulation sample. It does not cover the detector-model differences between pseudo-data and data, and it does not change any amendment 7 decision.

**Margins.** The spec's §1 margins (2.8, 4.5 and 4.9 null SD) are distances to the null median, not to the decision boundary ([`../../../measurement-paper/BINDING-PHASE1-ADDENDUM-3.md`](../../../measurement-paper/BINDING-PHASE1-ADDENDUM-3.md) §2). The `margin_in_sd` fields in `sf1-results.json` are distances to the median as well.

---

# SF-1 report: does the null distribution depend on the unfolding-simulation size?

All three shape tests PASS. Every decision is still "rejected" after the most adverse adjustment SF1-SPEC §4 allows. The study used 5.445 of the 25 charged CPU node-h. All 600 quarter runs produced products, so there is no shortfall, and there are no deviations from the spec's measurements or acceptance rule.

`squeue -u josephrb` at 2026-10-20 00:52 PDT shows no SF-1 job still queued or running. The harness blocked writing `REPORT.md`, so the full report is here. Every script, table, the manifest, the ledger and the small results are in `scratchpad/methods-sf1/` and on pscratch.

## 0. Outcome

| test | production decision | claim after the §4 adjustment (k/B, p) | 95% Clopper–Pearson interval vs Holm threshold | adjusted decision | **SF-1** |
|---|---|---|---|---|---|
| NuWro 21.09 shape | rejected, k=1/1751 | k=2/1751, p=0.001712 | [0.000138, 0.00412] vs 0.05 | rejected | **PASS** |
| GENIE CV shape | rejected, k=0/1366 | k=0/1366, p=0.000732 | [0, 0.00270] vs 0.00625 | rejected | **PASS** |
| GENIE+MEC shape | rejected, k=0/1343 | k=0/1343, p=0.000744 | [0, 0.00274] vs 0.025 | rejected | **PASS** |

- **Holm runs.** The decisions come from one Holm run with all three shape tests adjusted together. Adjusting them one at a time gives the same decisions. All ten family decisions remain "rejected".
- **No resolved size dependence.** None of the six tests shows a resolved change of location, scale or tail between half and quarter simulation:
  - median shift Δ is at most 0.074 null SD in size;
  - scale ratio s is 0.975–1.010;
  - the 95th- and 99th-percentile ratios are 0.987–1.008;
  - every 95% interval contains 0 (for Δ) or 1 (for the ratios).
- **The one resolved effect is small.** The mean paired difference T_q − T_h is positive and resolved in all six tests, at 0.006–0.034 null SD. A quarter-simulation experiment gives a slightly higher T than the same experiment at half simulation.
- **Margins correction (accepted).** The spec's §1 "margins" of 2.8 / 4.5 / 4.9 null SD measure how far the observed statistic is from the null median, not from the decision boundary. They must not be quoted as decision margins.
  - The coordinator's figure for NuWro shape is 1.11 null SD from flipping (T_crit 8672.55). I did not re-derive it.
  - This changes nothing in SF-1, because §4 recomputes each decision directly.
  - The `margin_in_sd` fields in `sf1-results.json` are likewise distances from the median.

## 1. Code used

- **Spec.** The spec was read at origin/main `c5aa0e907fdc56ff03dba5ec3d72c216b40a82e7`, in the detached worktree `scratchpad/wt-sf1`.
- **Runs used the production tree.** Production commit `4f5a613f383d3776db0be64eccc05e2d89af4a86` was cloned fresh and clean to `/pscratch/sd/j/josephrb/methods-paper/sf1-20261019/deploy-4f5a613f`. HEAD was verified and `git status --porcelain` is empty. No existing deploy was touched.
- **Why not origin/main.**
  - These files are byte-identical between `4f5a613f` and origin/main: `s5p_nullexp.py` (`789271bb`), `s5n_pseudo.py` (`8981f97b`), `s5c_pseudo.py` (`d81d4f46`), `s5p_joint.py` (`2cd98235`) and `s5p_inference.py` (`55239135`).
  - But `2d-unfolding/unfold_2d_omnifold_unbinned.py` differs. It is `8ebe0277` at `4f5a613f` and in every production product, and `74a4ed69` on origin/main.
- **Which deploys made the 600 half products.** These come from the meter ledger, `/pscratch/sd/j/josephrb/s5p-20260926/ledger/admissions.jsonl`.
  - Batch 0 of all three nulls, and NuWro batch 1, ran at deploy `4f5a613f`.
  - GENIE CV and MEC batch 1 ran at `55a41765d2073f50a52acd759e5f5182b0b40005`. The first 200 seeds reach into batch 1: 3 NuWro seeds, 7 CV seeds and 7 MEC seeds.
  - `55a41765` differs from `4f5a613f` only by an added `s5p_requeue.py`, which the unfold does not import.
  - All 600 half products record one identical `code_sha256` set, and it equals the `4f5a613f` bytes:
    - `s5c_unfold` `510d749a`
    - `omnifold_nn_core` `24f87f11`
    - `xsec_nd` `454001f3`
    - `s5e_candidate` `bda8c48c`
    - `s5e_deform` `6726ff99`
    - `unfold_2d_omnifold_unbinned` `8ebe0277`
    - plus the five modules above.
- **Execution path.** Every run went through the production wrapper `nd-unfolding/s5c_array.sh`: clean-HEAD pin check, environment activation, the OI-136 import guard and the inventory.
  - Environment: `setup_salloc_env.sh` → `~/.conda/envs/root_6_28`, Python 3.11.14, numpy 1.26.4.
  - Each task line is the production `cal-<null>-b0.tsv` line with exactly three changes: `--mc-fraction quarter` is added, `--pseudo-seeds` is set to the item, and `--tag`/`--out` point to the SF-1 tree.
- **SF-1 scripts.** The cluster copies (`$S/scripts/`) and local copies (`scratchpad/methods-sf1/scripts/`) have identical sha256.

| script | sha256 | role |
|---|---|---|
| `sf1_node.sh` | `7419f7d7` | sbatch script: one whole node, 8 workers, each pinned to one NUMA domain (32 hardware threads, same as production `--cpus-per-task=32`), dynamic line queue, no line started with under 50 min left |
| `make_tables.py` | `2579c564` | seed selection and task tables |
| `check_products.py` | `749d5aad` | quarter/half product comparison |
| `sf1_stats.py` | `c0e0f064` | statistics and evaluation, importing `s5p_joint` and `s5p_inference` from `4f5a613f` |
| `ledger.sh` | `6ac62499` | sacct charges |
| `input_manifest.sh` | `8e413d8c` | input sha256 manifest |
| `inspect_prod_meta.py` | `587cf6e6` | production product metadata |

## 2. Inputs (sha256)

The full manifest is `manifest/inputs-sha256.txt`: 783 files, manifest sha256 `3a50f502b5a425bc4d116245c36f79bbc279cbd876b87aa72bd0298b001b5031`, error log empty. Every path was opened and hashed.

- **MC and background:**
  - MC events, `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz`: `07fccc1a…`, equal to `--expect-npz-sha256`.
  - Background, `/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz`: `2addac8f…`, equal to `--expect-bkg-sha256`.
- **Universe weights:**
  - bank `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/`: 701 files, 67 GB, each hashed in the manifest;
  - detector directory `/pscratch/sd/j/josephrb/s5p-20260926/bank_detector/`: 33 files, each hashed.
- **Null hypotheses** (in the deploy tree, equal to the hashes the production products record):
  - `null-nuwro_cv-F.json` `9297a698`
  - `null-genie_cv-F.json` `8c37f545`
  - `null-genie_mec-F.json` `9033c952`
- **Frozen evaluator design and inputs:**
  - `prod/design.json` `404446eb`
  - `stage1_inspect.json` `def4c67c`
  - `s5c/contract.json` `d54fd7c9`
  - V, `/pscratch/sd/j/josephrb/s5p-20260926/stage3/V/V-s3v.npz`: `35979ef7`, with the frozen-V check enforced.
- **Predictions:**
  - `gen5d_fluxfix/nuwro_cv_xsec5d_full.npz` `475a2871`
  - `genie_cv_xsec5d_full.npz` `cfa42210`
  - `genie_mec_xsec5d_full.npz` `c179855d`
- **Process shifts and sub-fine (M1) residuals.** The D16 shift files (`b7b5de71`, `0d7d1b58`, `768f942c`) and M1 files (`706b87d4`, `40d9aa1c`, `5e6aa8a6`) equal the hashes the design declares.
- **Data:** data central `runs/s2/num/data/data_b-_j-.npz` `fb5cc679`. The 20 rounding jitters and 10 lateral endpoints are in the manifest.
- **Production claim ensembles:** `/pscratch/sd/j/josephrb/s5p-20260926/runs/prod/cal/{NuWro_21_09,GENIE_2_12_10_CV,GENIE_2_12_10_MEC}/`.
  - They hold 1751, 1366 and 1343 finished products, with no partials. Each count equals the null's final-status B.
  - The recorded result, `/pscratch/sd/j/josephrb/s5p-20260926/stage7/joint/joint-evaluate.json` `b9604502`, equals the repo copy.

## 3. Seeds and products

- **Selection.** I took the first 200 seeds by seed order of each production ensemble (`tables/seeds-*.txt`).

  | null | seed range | production seeds missing from that range (never finished, so not selected) |
  |---|---|---|
  | NuWro | 1260000–1260202 | 3 |
  | GENIE CV | 1220000–1220206 | 7 |
  | MEC | 1240000–1240206 | 7 |

- **Quarter products: 200/200 for each null.** There are no partials and no failed lines. Every line returned rc=0, and the deadline guard skipped no line.
  - Location: `/pscratch/sd/j/josephrb/methods-paper/sf1-20261019/runs/quarter/<null>/sf1q_<null>_s<seed>.npz`, 106 MB in total.
- **Check over all 600 pairs** (`results/check-all-*.json`):
  - Each quarter product has the same members (`meta`, `xsec_flat`, `xtrue_flat`), shapes (65856) and dtype (float64) as its half product.
  - `xtrue_flat` is bitwise equal, so the split and pseudo-data source are the same.
  - The metadata are identical: split key, nuisance draws, detector bands, input hashes and code digests.
  - The only differences are the expected ones: `development.mc_fraction` (quarter vs half), the added `experiment.n_unfolding_mc` (about 8.21M, half of half A), and the timing fields.
- **Step 1, dry run (job 60004676).** It passed before the main submission.
  - It ran the NuWro quarter for seeds 1260000–1260006, plus a half rerun of seed 1260000 in `runs/halfcheck/`.
  - The half rerun is **bitwise identical** to the production product (`xsec_flat` and `xtrue_flat`). The SF-1 setup therefore reproduces production exactly.
  - A quarter seed takes about 275 s to unfold, against about 416 s for the half rerun on the same node.

## 4. Jobs and charges

- **Account and QOS:** `m3246`, regular QOS (shown by Slurm as `regular_1`); never premium, never debug.
- **Charge formula:** the s5p meter's (`nd-unfolding/s5c_meter.py`), charged CPU node-h = ElapsedRaw/3600 × billing/256 × 1.0. Every job was billed 256, one whole node.
- **Source:** `sacct -X`, times in PDT, in `results/ledger.txt`.

| JobID | name | state | start (PDT) | elapsed | nodes | node-h |
|---|---|---|---|---|---|---|
| 60004676 | sf1-dryrun | COMPLETED | 10-19 11:17:45 | 00:07:56 | 1 | 0.1322 |
| 60017066 | sf1-NuWro_21_09-a | COMPLETED | 10-19 16:21:02 | 00:51:20 | 1 | 0.8556 |
| 60017068 | sf1-NuWro_21_09-b | COMPLETED | 10-19 16:21:02 | 00:48:01 | 1 | 0.8003 |
| 60017069 | sf1-GENIE_2_12_10_CV-a | COMPLETED | 10-19 17:47:57 | 00:54:23 | 1 | 0.9064 |
| 60017070 | sf1-GENIE_2_12_10_CV-b | COMPLETED | 10-19 17:47:57 | 00:54:20 | 1 | 0.9056 |
| 60017071 | sf1-GENIE_2_12_10_MEC-a | COMPLETED | 10-19 19:20:01 | 00:55:40 | 1 | 0.9278 |
| 60017074 | sf1-GENIE_2_12_10_MEC-b | COMPLETED | 10-19 19:20:01 | 00:55:01 | 1 | 0.9169 |
| **total** | | | | | | **5.445 of 25** |

- **Worst case.** The time limits (1 h for the dry run, 3 h for each of the 6 main jobs) capped the worst-case charge at 18.13 node-h. The actual cost was about 0.009 node-h per quarter experiment.
- **Rules met.** Every job ran under 12 h. Every output is under `/pscratch/sd/j/josephrb/methods-paper/sf1-20261019/`, and nothing was written to CFS.
- **Maintenance.** All SF-1 jobs finished by 2026-10-19 20:15 PDT, before the 2026-10-21 cut-off. Nothing was cancelled or deferred.
- **Other sessions.** The measurement session's `mp*` jobs were never touched.

## 5. Statistics method (spec §2–§3)

- **Production code path.** All statistics use the production `s5p_joint` functions (`Model`, `ensemble`, `statistics`, `test_null`) and `s5p_inference`, both from the `4f5a613f` tree.
  - Frozen inputs: V, each null's `surrogate_seed0` from the design (NuWro 1760000, CV 1720000, MEC 1740000), the pseudo-seed keys and the full domain.
  - Threads: `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` and `MKL_NUM_THREADS` set to 4, as in the production evaluate.
  - The statistics ran on a login node, as the production evaluate did. No unfold ran on a login node.
- **Reproduction gate.** `test_null` over each production claim ensemble reproduces **every** recorded field of `joint-evaluate.json` exactly, for all three nulls.
  - This covers the observed T, every variant's p, k, B, median and SD, the shift, the robustness variants, the claim and the jitter p.
  - The recomputed Holm decisions equal the record.
  - The 200 half T values recomputed on the subset alone equal the ones taken from the full ensemble, which confirms that the additive draws are keyed by seed.
- **Quarter statistics.** The quarter T values use the same additive draws, at variant c=0. The half T in each pair is the production c=0 value.
- **Bootstrap:**
  - one `numpy.random.default_rng(20261019)` per null;
  - one 10,000 × 200 index matrix, shared by T_tot and T_shape;
  - 95% intervals from the 2.5 and 97.5 percentiles;
  - SD with ddof 0, matching the production null SD;
  - numpy's default linear percentiles.

## 6. Numbers (spec §3)

Δ is in half-null SD; intervals are 95% paired-bootstrap intervals.

| test | median_h | SD_h | median_q | SD_q | Δ | s | P95 q/h | P99 q/h |
|---|---|---|---|---|---|---|---|---|
| NuWro total | 6319.65 | 184.94 | 6333.20 | 186.16 | 0.073 [−0.046, 0.127] | 1.007 [0.986, 1.027] | 1.0013 [0.9988, 1.0063] | 1.0078 [0.9988, 1.0079] |
| NuWro shape | 7081.36 | 917.92 | 7091.50 | 916.24 | 0.011 [−0.032, 0.049] | 0.998 [0.992, 1.004] | 1.0058 [0.9948, 1.0098] | 0.9965 [0.9965, 1.0081] |
| GENIE CV total | 526.01 | 55.77 | 527.21 | 56.19 | 0.022 [−0.050, 0.106] | 1.008 [0.986, 1.030] | 0.9983 [0.9851, 1.0226] | 1.0037 [0.9826, 1.0290] |
| GENIE CV shape | 584.13 | 96.76 | 582.59 | 97.74 | −0.016 [−0.059, 0.060] | 1.010 [0.999, 1.022] | 1.0053 [0.9914, 1.0192] | 0.9996 [0.9892, 1.0353] |
| MEC total | 410.67 | 37.42 | 411.60 | 36.50 | 0.025 [−0.090, 0.081] | 0.975 [0.950, 1.001] | 0.9934 [0.9803, 1.0167] | 0.9866 [0.9677, 1.0165] |
| MEC shape | 455.11 | 69.32 | 453.53 | 68.71 | −0.023 [−0.063, 0.066] | 0.991 [0.976, 1.006] | 0.9899 [0.9781, 1.0134] | 0.9968 [0.9737, 1.0167] |

**Paired differences** d = T_q − T_h (n = 200 per test):

| test | mean | SD | median | 5% / 95% | fraction d < 0 | corr(T_q, T_h) | mean d / SD_h [95%] |
|---|---|---|---|---|---|---|---|
| NuWro total | 6.27 | 32.10 | 5.32 | −43.8 / 66.6 | 0.455 | 0.985 | 0.034 [0.010, 0.059] |
| NuWro shape | 5.80 | 38.87 | 4.97 | −50.3 / 81.1 | 0.445 | 0.999 | 0.006 [0.0005, 0.012] |
| GENIE CV total | 1.41 | 8.19 | 1.17 | −11.0 / 14.0 | 0.450 | 0.989 | 0.025 [0.005, 0.046] |
| GENIE CV shape | 1.41 | 8.63 | 0.92 | −11.2 / 14.7 | 0.445 | 0.996 | 0.015 [0.002, 0.027] |
| MEC total | 1.09 | 6.33 | 1.13 | −9.7 / 12.1 | 0.430 | 0.986 | 0.029 [0.005, 0.053] |
| MEC shape | 1.06 | 6.86 | 1.11 | −10.5 / 13.4 | 0.440 | 0.995 | 0.015 [0.002, 0.030] |

The median paired difference over SD_h has an interval containing 0 for every test except MEC total, at 0.030 [0.0001, 0.055].

**Observed statistics** (unchanged by SF-1):

| null | T_tot,obs | T_shape,obs |
|---|---|---|
| NuWro | 7427.14 | 9660.01 |
| GENIE CV | 1812.66 | 1086.14 |
| MEC | 1647.12 | 868.59 |

## 7. Adjusted ensembles (spec §4)

Each null draw becomes T′ = median_h + (T − median_h)/s_lo − Δ_lo·SD_h.
- median_h and SD_h are the 200-pair half-null c=0 values of the shape statistic.
- s_lo and Δ_lo are the lower 95% ends of s and Δ.
- The transform is applied to every claim variant of the production ensemble: c = 0, ½, 1 and m1±2, with B as reached.

| shape test | s_lo | Δ_lo | k per variant (0 / ½ / 1 / m1+2 / m1−2) | claim | Holm threshold | decision |
|---|---|---|---|---|---|---|
| NuWro | 0.99225 | −0.03192 | 1 / 1 / 1 / 2 / 1 (production: 1 in every variant) | k=2/1751, p=0.001712 | 0.05 (last Holm step) | rejected |
| GENIE CV | 0.99882 | −0.05917 | 0 / 0 / 0 / 0 / 0 | k=0/1366, p=0.000732 | 0.00625 | rejected |
| MEC | 0.97641 | −0.06273 | 0 / 0 / 0 / 0 / 0 | k=0/1343, p=0.000744 | 0.025 | rejected |

- **NuWro.** The adjustment lifts one more NuWro draw above the observed value, in the m1+2 variant. The claim p rises to 0.00171, still far below its Holm level.
- **Whole family.** All ten family decisions remain "rejected", both in the joint run and one at a time.
- **Sensitivity check (not the frozen rule).** Centring and scaling each variant at its own production median and SD gives identical claims and decisions.

## 8. Deviations and notes

No deviation affects the measured quantities or the acceptance rule. These are my execution choices:

1. **Dry run.**
   - It also included a half rerun of seed 1260000, as a reproduction check only; that product enters no statistic.
   - It ran 6 more NuWro quarter seeds, with the same command as the main runs, and they count toward the 600.
2. **Code tree.** Runs used production tree `4f5a613f` rather than origin/main, because of the `unfold_2d_omnifold_unbinned.py` difference (§1). The CV and MEC batch-1 half products come from `55a41765`, whose unfold code is identical by recorded digests and by git diff.
3. **Execution.**
   - Production ran Slurm array tasks of 32 CPUs in shared QOS. SF-1 instead ran 8 lines per whole regular node, each pinned with `taskset` to one NUMA domain (32 hardware threads), with `SLURM_ARRAY_TASK_ID` set per line. The bitwise half reproduction shows this changes no result.
   - `TMPDIR` is `$SCRATCH/tmp`, set by the production environment script, which is on pscratch and not CFS.
4. **Reading of the transform (§4).** I took median_h and SD_h to be the §3 quantities: the 200-pair half shape statistic at c=0. The variant-own alternative gives identical decisions.
5. **PASS rule.** PASS was evaluated with all three shape tests adjusted together; the one-at-a-time runs agree.
6. **Scratch run.** A 7-pair preliminary run, used only to test the script, is in `$S/results/prelim/` and enters no result.
7. **Dry-run log location.** The coordinator gave the log as `runs/tasks/sf1-dryrun-60004676.out`. It is actually at `$S/logs/sf1-dryrun-60004676.out`.
8. **Report file.** `REPORT.md` could not be written (the harness blocked it), so this text is the report.

## 9. Where things are

`$S` is `/pscratch/sd/j/josephrb/methods-paper/sf1-20261019`.

- **Cluster:**
  - `$S/deploy-4f5a613f/`, `scripts/`, `tables/`, `manifest/`, `logs/`;
  - `runs/quarter/` (the 600 products), `runs/halfcheck/`, `runs/tasks/`, `runs/jobs/<jobid>/line-*.out`;
  - `results/sf1-results.json` (sha256 `028ac3777e1a6a1b7bf4401e2073388dd530f13f32647ebb9143dd0c637cdfff`);
  - `results/sf1-pairs.csv` (sha256 `c95c5c94d4a43b1f5182f4d5fc45ce94fb942563ed52f139d727a3483b736d4a`);
  - `results/ledger.txt`, `results/check-all-*.json`, `results/dryrun-check.json`.
- **Local:** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/methods-sf1/` holds `scripts/`, `tables/`, `manifest/`, `logs/` and `results/`. `results/` has the files above plus `inspect_prod_meta.out.json` and `check-all-summary.txt`.
- **Git:** nothing was committed or pushed, and no cluster git checkout was edited. The local repo checkout was not written. The worktree `scratchpad/wt-sf1` (detached at `c5aa0e90`) was used read-only.
- **Status:** these results are not yet a live record; that needs a commit, which I have not made. Any change to a claim is Joseph's decision.