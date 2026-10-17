# 2D closeout Stage C production: REPORT (C0, S3, S4(ii), S1, S2, S4(i), S5)

**Owner:** 2D closeout executor (2d closer), directed by the paper-tighten lane under
AUTHORIZATION-20261012-2d-closeout-delegation.md.

This is the production record the grant requires
([`AUTHORIZATION-20261015-2d-closeout-stageC-production.md`](../../../../AUTHORIZATION-20261015-2d-closeout-stageC-production.md)
§3, "record"). It gives every job's `sacct` row, the gates, the products and their digests, the S5 matrices and the
terminal outcome. Every number here was measured from `sacct`, the cluster namespace, the CFS copy or the committed
evidence in [`evidence/production/`](evidence/production/), except the shared-QOS gate lines marked † in §5, which
come from the executor's session transcript. All times are UTC unless marked PDT.

**Not covered:** adoption of any product, central value or uncertainty (all S5 products are diagnostic until Joseph
adopts them, DESIGN §8); disclosure wording (Stage F); `driver_p1.py` reaching `2d-unfolding/` on `main` (a Stage F
precondition, §13).

| field | content |
|---|---|
| `Grant` | [`AUTHORIZATION-20261015-2d-closeout-stageC-production.md`](../../../../AUTHORIZATION-20261015-2d-closeout-stageC-production.md) (PR #130): ≤ 100.0 charged node-h, window to this REPORT or 2026-11-15 |
| `Bindings` | [`…-production-binding.md`](../../../../AUTHORIZATION-20261015-2d-closeout-stageC-production-binding.md) (PR #132, shared-QOS package `4139548b`); [`…-regular-packing.md`](../../../../AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md) (build step); [`…-smoke-resubmit.md`](../../../../AUTHORIZATION-20261016-2d-closeout-stageC-smoke-resubmit.md); [`…-packing-binding.md`](../../../../AUTHORIZATION-20261016-2d-closeout-stageC-packing-binding.md) (PR #140, packed package `c873cc22`) |
| `Package` | [`DESIGN.md`](DESIGN.md) and the files beside it, on `main` since PR #131 (`e96c20e8`) and PR #138 (`bea0cc47`; production tree identical to `c873cc22630f8c5b2736c1ca98b455c52db0e5d6`) |
| `Namespace` | `/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/` (`$NS`); `repo/` = `4139548b3920c1c7944e700c08649493167bc45d`, `repo_k/` = `c873cc22630f8c5b2736c1ca98b455c52db0e5d6` |
| `Terminal outcome` | **Construction complete.** C0, S3, S4(ii), S1, S2, S4(i) and S5 all **PASS**; 539 allocations, of which 153 ran and all COMPLETED 0:0, and 386 were cancelled before starting; 0 FAILED, TIMEOUT, OUT_OF_MEMORY, DEADLINE or NODE_FAIL; 0 retries; 0 stops |
| `Charged` | **29.0297 node-h** of the 100.0 ceiling (§6) |
| `Products` | `results/s5/production_cov.npz` `6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc`; `s5.json` `8c815149517857302af4b3a64b0db4148a13515b8182bd6eebb2f89c57d92510`; `uq_production_covariance.root` `34cf33f96cd688e2c00064f314ff76d294b0d012b0bed5a4560cb1c2e3fc0df8` (§3) |
| `Durable copy` | `/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-production-20261015/`: 2,355 checksummed files; `SHA256SUMS.pscratch` `eab367a67b5664fe2d3d45298bac7bd80a5f43ad01a2c72b82b4b56f3c38ff78`; `sha256sum -c` on CFS returned 0 (§10) |

## 1. Answer

Every frozen check in DESIGN §7 and §8 passed, on one `out_root` (`$NS/out`), with the bound scripts
(`analyze_prod.py` `f9e0d8f2…`, `s5_rollup.py` `6c437004…`, both re-verified on the deployed trees after the run, §8).

| item | jobs | verdict | key measurements | result file sha256 |
|---|---|---|---|---|
| C0 | 2 | **PASS** | `C0_unit` and `C0_cv` vs XR-L0: max rel diff 1.37e-11 and 1.36e-11 over 205 cells, 0 over 1e-8 | `1f131c643906cf1e46cdcb777396e76bfa7c262b5621945235f2bc846685d734` |
| S3 | 10 | **PASS** | provenance 10/10; closure max \|c − 1\| ≤ 1.98e-14 in every lateral, with the canonical denominator; P3 reproduction 7.7e-12 (`BeamAngleX0`), 3.5e-13 (`MINOS0`) | `5df53a2efc0e6740e567f65b002fb6e8856bbd87e4b560b0c83d9c8200684377` |
| S4(ii) | 39 | **PASS** | provenance 39/39; July identity at seed 42, 7/7 universes, ≤ 1.38e-11; null vs CV, 5/5 seeds, ≤ 6.0e-12 | `a7c58368ceb5f1657b36a30030dba30d4d57c83dc51d629117f33016b85c02a4` |
| S1 | 300 | **PASS** | provenance 300/300; pilot joint replicas 1–20 reproduced 20/20, ≤ 2.96e-11 | `78cc8356213cb79268f5e53b2f6171522f6d3c87a27b741494c58d4ce613f6ef` |
| S2 | 100 | **PASS** | provenance 100/100; pilot bkg replicas 1–20 reproduced 20/20, ≤ 6.38e-12 | `989f5e6da5394635c7ed69e0fa8cadba682eebadb4510614ea9d342f06f74927` |
| S4(i) | 80 | **PASS** | provenance 80/80 | `e19ff38634a6f8601e439afbba97732ade1a3bfbd53b4614314e2d691bc2b50d` |
| S5 | login node | **PASS** | 55 checks in `s5.json`, all `ok`; the log prints 54 `[PASS]` lines, 0 FAIL, 0 INCONCLUSIVE (§3) | `s5.json` `8c815149…` |

All six item JSONs read `pins_failed {}`, `analyze_prod_sha256` `f9e0d8f2…` and `out_root` `$NS/out`. The S1
analysis counts 300 replicas: 296 ran in production packs and `S1_001`–`004` ran in the smoke pack 59860260, whose
outputs DESIGN §14.5 keeps once they pass the production checks, as they do here.

**G2.** G2 is carried as a disclosed approximation, per
[`DECISION-20261015-joseph-g2-carry.md`](../../../../DECISION-20261015-joseph-g2-carry.md). Nothing in this REPORT
measures the G2 effect, and nothing here says it is zero. The S4(ii) identities test that the universe panel
reproduces the July products and that the null universe reproduces the CV; passing them is not evidence about the
size of G2.

## 2. Item checks in detail

The analyses ran on a saul login node after `setup_salloc_env.sh`, from the deployed `repo_k` package:
- `s4ii` at 2026-10-17T01:08:45Z, after all 17 G2 packs ended (transcript `gatelog/analyze_s4ii.txt`);
- `s1`, `s2`, `s4i` from 22:29:43Z to 22:30:05Z, after all 136 packs ended (`gatelog/analyze_final_run.txt`, each
  rc 0, transcripts `gatelog/analyze_{s1,s2,s4i}.txt`);
- `c0` and `s3` on 2026-10-15/16, after G0 and G1 (their JSONs are in `evidence/production/results/`).

**S4(ii) identities** (max rel diff over cells / integral rel diff):

| check | worst | all |
|---|---|---|
| July, seed 42: `2p2h:0`, `Flux:23`, `MaCCQE:0`, `MaRES:0`, `MinosEfficiency:0`, `Muon_Energy_MINOS:0`, `NormDISCC:0` | `NormDISCC:0` 1.38e-11 / 7.2e-13 | 7/7 PASS |
| `NormDISCC:0` vs CV, seeds 42, 45, 48, 51, 54 | s48 6.0e-12 / 2.2e-14 | 5/5 PASS |

**S3 closure** (DESIGN §7.1). Every lateral has the title "OmniFold input completeness (mc_signal_reco truth-pass /
mc_truth_denom)", `hEffDenSource` = `mc_truth_denom`, and a non-empty denominator (integral 5,779,535.68 for the
eight non-MINOS laterals, 5,723,867.86 for `Muon_Energy_MINOS_0`, 5,776,329.75 for `_1`). The worst \|c − 1\| is
1.98e-14 (`Muon_Energy_MINOS_1`). The guard against a vacuous pass therefore holds in all 10.

## 3. S5: the matrices

`s5_rollup.py --out $NS/results/s5` ran in `root_6_28` from 22:31:00Z to 22:31:08Z, rc 0
(`gatelog/s5_run.txt`, `gatelog/s5_rollup.txt`). `s5.json` records `S5: PASS`, `s5_rollup_sha256` `6c437004…` and
the sha256 of every input it read. Its `checks` object has 55 entries, all `ok: true`; the log prints 54 of them
(`control_vl175_per_block`, the per-block detail behind the control rows below, is not printed).

**Checks** (each a stop; all passed):

| check | measured |
|---|---|
| control: the May sweep reproduces VL175, all 45 blocks found | every block ≤ 2.6e-17 × max\|C_total\|; non-null blocks ≤ 2.1e-16 at own scale (null: `EtaNCEL`, `MaNCEL`, `NormNCRES`); total 1.3e-17 |
| X01 factors vs VL175 `minos_rescaled.npz`, May and S3 outputs | 0.0 and 0.0 |
| every item analysis PASS on the same `out_root` | C0, S3, S4ii, S1, S2, S4i |
| the 24 flux/POT files vs VL175 `build.json`; the pn sweep vs `sweeps.json`; July 44 bands, 187 universes | all match |
| universe bands | 43 plus the normalization |
| MAT `GetTotalErrorMatrix` vs numpy | 3.4e-16 |
| integrals from vectors: weighted Flux, X01 MINOS, stat | 1.3e-15, 1.9e-14, 1.6e-14 |
| functionals from vectors (31 × 205), blocks at total scale / non-null at own scale | 5.2e-15 / 1.84e-12 (worst `AhtBY`) |
| normalization rank 1 | 5.7e-16 |
| symmetry and PSD: universe, stat, c08, total | all symmetric; min eigenvalue / max: −3.0e-17, 7.7e-10, −3.5e-16, 1.2e-12 |

**X01 and Flux implementation details that DESIGN §8 does not state** (`s5_rollup.py:144-194`): the per-playlist
flux histogram is `pTmu_reweightedflux_integrated`; the POT is each playlist's `runEventLoopData_<pl>.root`
`POTUsed`, and Φ_MINOS,u is combined over the 12 playlists as a POT-weighted mean; Flux universe u takes the
constraint file's entry u (u = 0–99 of the file's 1,000 `Flux` entries, `sorted_NuEConstraint_FHC_RHC_IMD.txt`,
`e38ad7d2…`). The director's F4 verifier reproduced VL175's `minos_rescaled.npz` exactly with these.

**Reported numbers** (no pass/fail; from `s5.json` `numbers`). σ is per cell, relative to E_U. "Rank" counts the
eigenvalues above 1e-10 × the largest (the total is strictly positive-definite, min/max eigenvalue 1.2e-12; numpy's
default `matrix_rank` tolerance gives 141 for universe and 205 for the total):

| block | rank | median σ | p84 | min | max | integral σ |
|---|---|---|---|---|---|---|
| universe | 123 | 5.97% | 8.73% | 4.19% | 20.28% | 4.328% |
| stat (300 S1 replicas, ddof 1) | 205 | 0.684% | 1.71% | 0.235% | 17.98% | 0.061% |
| c08 (seed main effect) | 4 | 0.057% | 0.140% | 0.0069% | 0.715% | 0.0025% |
| **total** | 197 | **6.04%** | **8.95%** | 4.24% | 23.29% | **4.328%** |
| VL175 block sum, for comparison | | 6.09% | 9.02% | 4.10% | 23.11% | 4.230% |

The total's σ on the 31 functionals: integral 4.33%; the 14 pT projections 4.36–7.27%; the 16 p∥ projections
4.30–13.71%.

**Ensemble error:**
- stat: per-cell relative SE of σ 4.09% (1/√(2·299)); nested 150-vs-300 σ ratio, median 1.0012;
- jackknife relative SE of the stat variance: 7.4–8.9% over the total's 10 leading eigenmodes, 7.0–9.4% over the
  31 functionals; the stat share of the total variance in those 10 modes is 0.05–29.6%;
- C08: 4 degrees of freedom, Gaussian relative SE of variance 71%.

**Reported, not added:**
- bkg-only separable term (S2): median σ_bkg/σ_stat 0.263;
- C08 vs σ_ML: median σ_c08/σ_ML 0.304; the clipped random-effects seed variance, median 0.027% (reported, not
  used);
- X02 (bootstrap × seed interaction, S4(i)): median diag(C_int)/diag(C_stat) 0.0758, jackknife SE 0.0052 over the
  20 bootstrap seeds, Gaussian relative SE 16% (76 dof); median interaction/B over c08 diagonal 0.685;
- X03 (universe × retraining, S4(ii)), per universe, median over cells:

  | universe | shift | seed SD of shift | seed SD / σ_ML (jackknife SE) |
  |---|---|---|---|
  | `Flux:23` | 8.42% | 0.220% | 1.29 (0.069) |
  | `MaRES:0` | 0.711% | 0.233% | 1.28 (0.087) |
  | `MaCCQE:0` | 0.266% | 0.220% | 1.29 (0.098) |
  | `2p2h:0` | 0.114% | 0.235% | 1.24 (0.050) |
  | `MinosEfficiency:0` | 1.57% | 0.227% | 1.33 (0.122) |
  | `Muon_Energy_MINOS:0` | 2.64% | 0.245% | 1.31 (0.096) |
  | `NormDISCC:0` (null) | 1.9e-12% | 5.6e-12% | 3.6e-11 |

  Each SD has 4 degrees of freedom (Gaussian relative SE 35%).
- **Centring (R9).** Per universe band, the median offset of the band's centre (the weighted mean for Flux, the mean
  otherwise) from E_U is 0.12–0.50% of E_U, or 0.08–2.26 σ_band (null bands `EtaNCEL`, `NormDISCC` at
  ≤ 4.2e-8%). For the stat ensemble, the replica mean's median offset from E_U is **4.43 σ/√300**. The stat block is
  the covariance about the replica mean (ddof 1), so this offset does not enter it; it is reported as R9 requires,
  and it is a surviving limitation (§12).

**C03.** The background stream is independent of the signal stream (three independent streams, R5). The C03 shared
draw is not applied, because the overlap it is conditioned on was never measured (DESIGN §8).

**Products** (`$NS/results/s5/`, copied to CFS):

| file | bytes | sha256 |
|---|---|---|
| `production_cov.npz` | 16,877,824 | `6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc` |
| `s5.json` | 70,418 | `8c815149517857302af4b3a64b0db4148a13515b8182bd6eebb2f89c57d92510` |
| `uq_production_covariance.root` | 14,166,411 | `34cf33f96cd688e2c00064f314ff76d294b0d012b0bed5a4560cb1c2e3fc0df8` |

The ROOT rollup is regenerable from the NPZ and is on CFS per the 2026-10-15 binding §3.5, which the packing binding
§4 keeps.

## 4. Run record

| when (UTC) | event |
|---|---|
| 2026-10-15 20:11–21:00 | G0 (C0) on the shared QOS, `repo` `4139548b`; C0 PASS |
| 2026-10-15 22:15–22:27 | G1 (10), G2 (39), S1a–S1f (300) and S2a (50) submitted to the shared QOS: the 399 jobs in `gatelog/all_deadline_check_20261015.txt`. S2b's gate was NOT ADMITTED (a wait) |
| 2026-10-16 01:36–15:33 | G1 ran (S3, 10 laterals); S3 PASS |
| 2026-10-16 17:18–19:41 | four shared S4U rows (`NormDISCC0_s42`–`s51`) started and completed |
| 2026-10-16 16:30 | smoke migration: the 4 shared `S1_001`–`004` jobs cancelled before starting (`evidence/smoke_pack/`) |
| 2026-10-16 19:03–19:13 | smoke pack 59860260 (`K4_S1_001`), PASS (DESIGN §14.5). The first smoke pack, 59859828, was cancelled while pending |
| 2026-10-16 20:37:10 | `repo_k` deployed at `c873cc22` (the earlier copy retired to `tmp/repo_k.8ea086eb.retired.20261016T203710Z`) |
| 2026-10-16 20:37:42 | migration: `migrate` dry run, then `--execute`, cancelling 381 never-started shared jobs; `sacct` check 381/381 CANCELLED, ElapsedRaw 0, Start None, QOS shared |
| 2026-10-16 21:08:56 | G2 submitted, 17 packs |
| 2026-10-16 21:11–21:29 | S1a–S2b submitted, 99 packs |
| 2026-10-16 22:29 – 2026-10-17 01:04 | all 17 G2 packs ran and completed |
| 2026-10-17 01:03:11 | S4a submitted, 10 packs (the waiter's submit-completion time, `watchers/task_b0lvmo979.txt`; `sacct` Submit 01:02:59–01:03:11) |
| 2026-10-17 01:08:45 | `s4ii` PASS |
| 2026-10-17 02:36:04 | S4b submitted, 10 packs (the waiter's submit-completion time, `watchers/task_b0lvmo979.txt`; `sacct` Submit 02:36:02–02:36:03) |
| 2026-10-17 00:49 – 22:25 | the 119 CV packs ran (S1 00:49–20:25, S2 20:20–21:43, S4B 21:34–22:25) |
| 2026-10-17 22:29:04 | the pack watcher sees 137 K-packs ended (136 production + the smoke pack); `squeue` empty |
| 2026-10-17 22:29:43–22:30:05 | `s1`, `s2`, `s4i` PASS |
| 2026-10-17 22:31:00–22:31:08 | S5 PASS |
| 2026-10-17 22:32:24 | CFS copy complete; `sha256sum -c` 0 |

**Packed runs** (from `sacct`; caps in minutes; charges at ElapsedRaw × billing / 256 / 3600):

| class | packs | members | ElapsedRaw (s) | cap | charge |
|---|---|---|---|---|---|
| S4U pairs and the K1 single | 16 | 31 | 736–910 | 30 | 3.5611 |
| S4CV | 1 | 4 | 709 | 51 | 0.1969 |
| S1 | 74 | 296 | 607–774 | 51 | 13.2003 |
| S2 | 25 | 100 | 605–663 | 51 | 4.3106 |
| S4B | 20 | 80 | 608–637 | 51 | 3.4364 |
| smoke pack (`S1_001`–`004`) | 1 | 4 | 634 | 51 | 0.1761 |

All 137 packs wrote their `#pack` line (`$NS/packs/<jobid>.status`, copied to CFS). Their 515 member steps all read
COMPLETED 0:0 in `sacct`, and every member's runner rc in the status files is 0. Member ElapsedRaw was 574–891 s;
member MaxRSS 12.9–16.0 GiB (CV members ≤ 14.3 GiB), against 119 GiB per CV step and 238 GiB per S4U step.

## 5. Gates

Every gate line as `launch.py` printed it (`evidence/production/gatelog/<batch>_gate.txt` and `_submit.txt`). The
gate is terminal charges + every in-flight job at its full cap + the batch's caps, against 100.0.

| batch | QOS | when (UTC) | completed | in flight at cap | batch / packs | total | jobs submitted |
|---|---|---|---|---|---|---|---|
| G0 | shared | 2026-10-15 | 0.0000 | 0.0000 | 0.4250 | 0.4250 | 2 |
| G1 | shared | 2026-10-15 22:15 | 0.2430 | 0.0000 | 5.8333 | 6.0763 | 10 |
| G2 † | shared | 22:18:51 | 0.2430 | 5.8333 | 9.6000 | 15.6763 | 39 |
| S1a † | shared | 22:19:59 | 0.2430 | 15.4333 | 10.6250 | 26.3013 | 50 |
| S1b † | shared | 22:20:41 | 0.2430 | 24.1458 | 10.6250 | 35.0138 | 50 |
| S1c † | shared | 22:20:49 | 0.2430 | 35.4083 | 10.6250 | 46.2763 | 50 |
| S1d † | shared | 22:20:59 | 0.2430 | 46.6708 | 10.6250 | 57.5388 | 50 |
| S1e † | shared | 22:22:12 | 0.2430 | 57.9333 | 10.6250 | 68.8013 | 50 |
| S1f † | shared | 22:23:30 | 0.2430 | 68.3458 | 10.6250 | 79.2138 | 50 |
| S2a † | shared | 22:25:17 | 0.2430 | 79.1833 | 10.6250 | 90.0513 | 50 |
| S2b † | shared | after 22:27:10 | 0.2430 | 89.8083 | 10.6250 | 100.6763 | NOT ADMITTED (rc 3, a wait) |
| smoke pack (re-submission) | regular | 2026-10-16 | 3.4744 | 83.1250 | 0.8500 | 87.4494 | 1 |
| G2 | regular | 2026-10-16 21:08 | 4.3244 | 0.0000 | 8.8500 | 13.1744 | 17 |
| S1a | regular | 21:11 | 4.3244 | 8.8500 | 9.3500 | 22.5244 | 11 |
| S1b | regular | 21:14 | 4.3244 | 18.2000 | 11.0500 | 33.5744 | 13 |
| S1c | regular | 21:16 | 4.3244 | 29.2500 | 10.2000 | 43.7744 | 12 |
| S1d | regular | 21:19 | 4.3244 | 39.4500 | 11.0500 | 54.8244 | 13 |
| S1e | regular | 21:21 | 4.3244 | 50.5000 | 10.2000 | 65.0244 | 12 |
| S1f | regular | 21:24 | 4.3244 | 60.7000 | 11.0500 | 76.0744 | 13 |
| S2a | regular | 21:27 | 4.3244 | 71.7500 | 10.2000 | 86.2744 | 12 |
| S2b | regular | 21:29 | 4.3244 | 81.9500 | 11.0500 | 97.3244 | 13 |
| S4a | regular | 2026-10-17 01:02:57 | 9.1591 | 76.4500 | 8.5000 | 94.1091 | 10 |
| S4b | regular | 2026-10-17 02:36:02 | 10.6955 | 80.7500 | 8.5000 | 99.9455 | 10 |

† The shared-QOS gate and submit transcripts for G2 and S1a–S2b were written to the same `gatelog/` file names that
the packed path later reused (`G2_gate.txt`, `S1a_submit.txt`, …), so the files now hold the packed submissions. The
shared-era GATE lines above are as printed in the executor's session at 2026-10-15 22:18–22:27Z, extracted verbatim
with their transcript line numbers into `gatelog/shared_era_gate_lines_from_transcript.txt` (source: the session
transcript `~/.claude-school/projects/-Users-josephbailey-local-research-MINERvA-OmniFold/42670017-c41b-4c65-9b50-994312a5d203.jsonl`,
first 22,553,453 bytes, sha256 `2211c960202b198f796ef4554e3aae6fabb20bf0fb0264d23dafaa58bea721d8`; the file is
append-only, so `head -c 22553453 <transcript> | shasum -a 256` re-checks it); the jobs themselves
are in `sacct` (§11) and their `Deadline=` reads in `all_deadline_check_20261015.txt` (§7). For these rows the time
is the batch's first `sacct` Submit (for S2b, the last S2a Submit), not the gate's own time. `S2b_gate_2.txt` is a
later shared-QOS re-check of S2b on 2026-10-16 (98.0744; nothing submitted before the packed path replaced it).

**Deviation: four shared-QOS gates under-counted the jobs in flight.** DESIGN §6 requires each gate to run only after
every earlier `2dc_P_*` submission appears in the printed ledger, and the grant's gate counts "the full cap of every
job pending or running". On 2026-10-15 the shared batches were gated back to back: each gate ran within about a
second of the previous batch's last `sbatch` (S1a's last Submit 22:20:40, S1b's first 22:20:41; S1b's last 22:20:48,
S1c's first 22:20:49; S1c's last 22:20:58, S1d's first 22:20:59), before `sacct` listed every job. The printed
in-flight terms therefore fall short of the caps actually pending (G1 5.8333 + G2 9.6000 + 10.6250 per earlier S1
batch):

| gate | in flight, printed | in flight, all earlier jobs | short by | true total |
|---|---|---|---|---|
| S1b | 24.1458 | 26.0583 | 1.9125 (9 jobs) | 36.9263 |
| S1c | 35.4083 | 36.6833 | 1.2750 (6 jobs) | 47.5513 |
| S1d | 46.6708 | 47.3083 | 0.6375 (3 jobs) | 58.1763 |
| S1f | 68.3458 | 68.5583 | 0.2125 (1 job) | 79.4263 |

S1e, S2a and S2b match exactly. No ceiling was affected: the largest true total was 79.4263, and S2b's refusal at
100.6763 used a complete ledger. The lag itself was observed on 2026-10-15, and the packed path's DESIGN §14.4 step 4
responded to it: each `gate` runs at least 2 min after the last `submit` and only when the ledger's in-flight count
matches `squeue`. The executor applied that as follows:
- S1b–S2b: `submit_seq.sh` waited 130 s before each gate (measured gaps 133–170 s) and required equal counts;
- S1a: its first pack was submitted at 21:11:08, at most 92 s after G2's last (21:09:36), and its count check is not
  in the evidence;
- S4a and S4b: polled every 10 min, admitted under the v2 coverage rule (every `squeue` id in the ledger, ledger
  in-flight ≤ `squeue`; S4a ran with `squeue` 93 and ledger 92), not an equal count.

Recomputed from `sacct`, the printed in-flight term is complete at every packed gate checked (S1a 8.85, S1b 18.2,
S2b 81.95, S4a 76.45, S4b 80.75). The size of the shortfall in the four shared gates was not quantified until the
executor's verifier checked this REPORT.

**Waits, not stops.** S4a was NOT ADMITTED (rc 3, jobs in flight) at all 21 ten-minute polls from 2026-10-16
21:30:34Z to 2026-10-17 00:52Z (105.8244, 105.2563, 104.6802, then 104.1124). S4b was NOT ADMITTED from 01:05Z to 02:25Z at a flat 101.2958; no pack
completed in that window. Every poll is in `evidence/production/watchers/task_b7wco0xeo.txt` and
`task_b0lvmo979.txt` (the `<batch>_gate.txt` files hold only the last poll).

**Operator-side count guard, changed once.** Before each submit, the executor's waiter compared `squeue` (read first)
with the gate's ledger. The rule was `squeue count == ledger in-flight count`
(`watchers/wait_submit.v1_rule.txt`; also `submit_seq.sh`, which ran S1b–S2b, all equal). At 2026-10-17 01:02:02Z
the gate admitted S4a at 95.2319, but the guard saw `squeue 97` against `ledger in-flight 96` and submitted nothing.
Cause: a pack ended between the two reads (COMPLETING in `squeue`, COMPLETED and charged at actual in `sacct`); at
01:02:16Z every `squeue` id had a ledger line. The rule became: every `squeue` id (read first) has a line in the gate
file, and ledger in-flight ≤ `squeue` (`watchers/wait_submit.sh`, sha256 `2d013856…`). It still refuses the hazard it
exists for, a submitted job not yet in `sacct`. The director accepted the change in correspondence (not committed); the binding does not pin this
script.

**Final gate.** After production, `launch.py gate S4b` gives "REFUSE: batch S4b has no rows owed a first submission
(or only a held partial pack)" (`gatelog/final_ledger_gate_S4b.txt`), a navigation refusal under packing binding R4,
not a stop.

## 6. Accounting

Charge = ElapsedRaw × billing / 256 / 3600, from every `2dc_P_` allocation since 2026-10-15
(`evidence/production/sacct/sacct_report_allrows.txt`):

| QOS | state | allocations | charge (node-h) |
|---|---|---|---|
| shared | COMPLETED (C0 2, S3 10, S4U 4) | 16 | 4.1483 |
| regular_1 | COMPLETED (136 production packs + the smoke pack) | 137 | 24.8814 |
| shared | CANCELLED, never started | 385 | 0 |
| regular_1 | CANCELLED, never started (first smoke pack) | 1 | 0 |
| **total** | | **539** | **29.0297** |

This is 29.0% of the 100.0 ceiling. The packed path's pre-launch expectation was ≈ 31–37 including the measured
4.3244 (DESIGN §14.5); the measured G2 charge (3.7581) came in under its shared-QOS estimate (6.1–6.8), and the 119
CV packs (20.9472: 75,410 s / 3600) at the low end of theirs (21.0–26.2). The all-at-cap worst case was 118.1083 (packing binding
R1); the highest gate total at any submission was 99.9455 (S4b).

## 7. Deadline, maintenance and retries

- **`Deadline=` check.** After the first G0 submission, `scontrol` showed `Deadline=2026-10-20T23:00:00` and
  `Requeue=0` on both jobs (`gatelog/G0_deadline_check.txt`), as the 2026-10-15 binding §4 requires; on 2026-10-15
  the same field read `2026-10-20T23:00:00` on all 399 shared-QOS jobs then queued
  (`gatelog/all_deadline_check_20261015.txt`). For the packed path, all 136 production `sbatch` lines carry
  `--deadline=2026-10-20T23:00:00` (`gatelog/*_submit.txt`); `scontrol`'s field was not read for the packs (§12).
- **`DEADLINE` rows:** none. No job ended in state DEADLINE (`sacct`), and no job ended after 2026-10-21T06:00Z.
  From 2026-10-17 02:40Z the throughput watch also saw no pending job with Reason DeadLine. So no `redo` was owed.
- **Maintenance:** the grant §3, the 2026-10-15 binding §4 and DESIGN §6 put the straddle limit at 2026-10-21
  06:00Z; the packing binding §4 says 13:00Z, and `pack_watch.sh` used 13:00Z. The stricter 06:00Z governs. No job
  straddled either: the last job ended 2026-10-17T22:25:05Z.
- **Retries:** none. `retries/` is empty; no TIMEOUT, OUT_OF_MEMORY or FAILED attempt occurred.
- **Purge:** no input check failed.

## 8. Deployment

Both trees were checked against their manifests after the run, at 2026-10-17T22:35:01Z
(`evidence/production/post_run_deploy_verify.txt`):
- `repo_k`: `manifest.json` `77c6676b…`, 41 manifest and driver files, `deployed_commit` `c873cc22…`, 0 mismatches;
- `repo`: the six bound digests (`manifest.json` `3962cb4d…`, `jobs.tsv` `c4f1b708…`, `launch.py` `ea9f06d7…`,
  `sbatch_prod.sh` `1dc95ad3…`, `analyze_prod.py` `f9e0d8f2…`, `s5_rollup.py` `6c437004…`), 31 files,
  `deployed_commit` `4139548b…`, 0 mismatches.

`driver_p1.py` in both trees is `3056e625…`, the copy from `stageC/pilot/p1/` on `main`.

## 9. Watch items and director reports

Packing binding §3.6 watch items, each reported to the director when it happened (in correspondence, not committed):
- **First G2 packs:** 765, 790, 790 and 736 s against 1,800 s (charges 0.2044–0.2194); at the end all 17 G2 packs
  ran 709–910 s (S4CV 709 s against 3,060 s; the K1 single 792 s against 1,800 s).
- **CV packs over 2,000 s:** none; the longest was 774 s (59872064, `K4_S1_121`).
- **Packs removed by the Deadline:** none.

The director added a throughput watch on 2026-10-17 (no start for 8 h; < 30 completions in 24 h; > 45 non-terminal
at 2026-10-19 00:00Z; Reason DeadLine; any failed read). None fired; it exited DONE at 22:29:43Z with 136 completed in
the trailing 24 h. Its log is `watchers/throughput_log.txt`.

**Watcher scripts** (in `evidence/production/watchers/`):

| script | role | sha256 |
|---|---|---|
| `pack_watch.sh` | ABNORMAL, NOPACK, STRADDLE, SLOW, G2ENDED, PROGRESS; 300 s poll | `bb4e82b94426d8f8c4f8ed2f057b3ecf5a5c8b34d9de7055b140c5bcd7b71a5c` |
| `throughput_watch.sh` | director triggers (a)–(e); 900 s poll | `b8354dadf44b817b4db42b6ebeb72cfce4f93d3d3de0353cb496950ca3e782e8` |
| `wait_submit.sh` (v2) | S4a/S4b waiter with the coverage guard | `2d013856a549e358d6eca0b34b26fe258e8f86e251b716d0be0ec8f65e8cbf4f` |
| `submit_seq.sh` | S1b–S2b sequencer with the count guard | `0832b7259ae021dae254c7d148446a0b71cff306a9dbbe6b9d572a4b19ee3cc0` |
| `gate_stall.sh` | 2 h gate-stall check on S4b polls; ended on ALL SUBMITTED | `b83d266e70ba276e22f6100e6c09c004fb24a3679267687d6c9ab111ca19ecc8` |

## 10. Evidence and durable copy

**CFS** (`/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-production-20261015/`, new; checked absent first),
the pilot's procedure:
- the list `.filelist` (2,355 paths): all 531 `out/<job>/xsec.root`; `results/` (the six item JSONs, the smoke-pack
  JSON, and `s5/` with the NPZ, JSON and ROOT rollup); `logs/`; `gatelog/`; `retries/` (empty);
  `packs/`; `preflight/`; and the `tmp/` records cited here (`sacct_report_allrows.txt` and `.raw`,
  `prod_packs_final.txt`, `g2_rows.txt`, `g2_steps.txt`, `sacct_all.txt`, `mig_ids.txt`, `ledger_ids.txt`,
  `sq_now.txt`, `sq_ids.txt`, both `verify_deploy_*.py`, `deploy_repo_k_c873cc22.sh`);
- `SHA256SUMS.pscratch` computed on the pscratch originals (2,355 entries, sha256 `eab367a6…`);
- copied with `rsync -a --files-from`; then `sha256sum -c --quiet SHA256SUMS.pscratch` on the CFS copies returned
  **0**;
- `repo-meta/`: both `.deployed_commit` values (`4139548b…`, `c873cc22…`).

The directory holds 2,359 files: the 2,355, plus `.filelist`, `SHA256SUMS.pscratch` and the two `repo-meta/` files.
Not copied: the inputs, the deploy tarballs and the retired `repo_k` copies.

**In this repository** (`evidence/production/`): every `gatelog/` file; the seven result JSONs; the two S5
products `results/production_cov.npz` and `results/uq_production_covariance.root`, byte-identical to the CFS copies
(sha256 in §3; tracked with `git add -f` because `.gitignore` excludes `*.npz`, and `s5.json` names both); every `sacct` row
(`sacct/sacct_report_allrows.txt`, 1,360 rows including steps; `sacct/prod_packs_final.txt`, the 136 production
packs); `SHA256SUMS.pscratch` and `cfs_filelist.txt`; `preflight/`; the post-run deploy check; the watcher scripts,
their transcripts and the throughput log.

## 11. Every `sacct` row

Allocation rows of the 153 jobs that ran. The raw rows, including every member step, batch and extern step, are in
`evidence/production/sacct/sacct_report_allrows.txt` (TZ=UTC, `sacct -n -P -S 2026-10-15T00:00:00 -u josephrb`,
filtered to `2dc_P_` jobs and their steps).

The 386 jobs that never started all read CANCELLED, ElapsedRaw 0, Start None, charge 0 (ids 59829236–59859828):
- 381 shared-QOS rows cancelled by the production migration (`gatelog/migrate_prod_sacct.txt`, 381/381
  `CANCELLED by 112498|0|None|shared`; `gatelog/migrate_20261016T203742Z.tsv`);
- 4 shared `S1_001`–`004` cancelled by the smoke migration (`gatelog/migrate_20261016T163006Z.tsv`);
- the first smoke pack 59859828 (`gatelog/smoke_pack1_cancel_sacct.txt`).

| JobID | JobName | QOS | State | Start (UTC) | End (UTC) | ElapsedRaw | cap (min) | billing | ExitCode | charge |
|---|---|---|---|---|---|---|---|---|---|---|
| 59806379 | 2dc_P_C0_unit | shared | COMPLETED | 2026-10-15T20:11:12 | 2026-10-15T20:25:16 | 844 | 51 | 64 | 0:0 | 0.0586 |
| 59806381 | 2dc_P_C0_cv | shared | COMPLETED | 2026-10-15T20:16:15 | 2026-10-15T21:00:30 | 2655 | 51 | 64 | 0:0 | 0.1844 |
| 59829128 | 2dc_P_S3_BeamAngleX0 | shared | COMPLETED | 2026-10-16T01:36:41 | 2026-10-16T02:24:09 | 2848 | 70 | 128 | 0:0 | 0.3956 |
| 59829129 | 2dc_P_S3_BeamAngleX1 | shared | COMPLETED | 2026-10-16T02:24:40 | 2026-10-16T03:11:21 | 2801 | 70 | 128 | 0:0 | 0.3890 |
| 59829130 | 2dc_P_S3_BeamAngleY0 | shared | COMPLETED | 2026-10-16T05:07:08 | 2026-10-16T05:39:21 | 1933 | 70 | 128 | 0:0 | 0.2685 |
| 59829131 | 2dc_P_S3_BeamAngleY1 | shared | COMPLETED | 2026-10-16T06:24:02 | 2026-10-16T06:57:55 | 2033 | 70 | 128 | 0:0 | 0.2824 |
| 59829132 | 2dc_P_S3_MuonResolution0 | shared | COMPLETED | 2026-10-16T08:56:45 | 2026-10-16T09:28:36 | 1911 | 70 | 128 | 0:0 | 0.2654 |
| 59829133 | 2dc_P_S3_MuonResolution1 | shared | COMPLETED | 2026-10-16T12:28:01 | 2026-10-16T13:11:04 | 2583 | 70 | 128 | 0:0 | 0.3588 |
| 59829134 | 2dc_P_S3_MuonEnergyMINERvA0 | shared | COMPLETED | 2026-10-16T13:26:19 | 2026-10-16T14:10:16 | 2637 | 70 | 128 | 0:0 | 0.3663 |
| 59829135 | 2dc_P_S3_MuonEnergyMINERvA1 | shared | COMPLETED | 2026-10-16T14:15:40 | 2026-10-16T14:52:51 | 2231 | 70 | 128 | 0:0 | 0.3099 |
| 59829136 | 2dc_P_S3_MuonEnergyMINOS0 | shared | COMPLETED | 2026-10-16T14:51:09 | 2026-10-16T15:30:38 | 2369 | 70 | 128 | 0:0 | 0.3290 |
| 59829137 | 2dc_P_S3_MuonEnergyMINOS1 | shared | COMPLETED | 2026-10-16T15:01:41 | 2026-10-16T15:33:41 | 1920 | 70 | 128 | 0:0 | 0.2667 |
| 59829232 | 2dc_P_S4U_NormDISCC0_s42 | shared | COMPLETED | 2026-10-16T17:18:01 | 2026-10-16T17:38:00 | 1199 | 30 | 128 | 0:0 | 0.1665 |
| 59829233 | 2dc_P_S4U_NormDISCC0_s45 | shared | COMPLETED | 2026-10-16T17:38:56 | 2026-10-16T17:56:04 | 1028 | 30 | 128 | 0:0 | 0.1428 |
| 59829234 | 2dc_P_S4U_NormDISCC0_s48 | shared | COMPLETED | 2026-10-16T18:56:58 | 2026-10-16T19:19:01 | 1323 | 30 | 128 | 0:0 | 0.1837 |
| 59829235 | 2dc_P_S4U_NormDISCC0_s51 | shared | COMPLETED | 2026-10-16T19:19:33 | 2026-10-16T19:41:15 | 1302 | 30 | 128 | 0:0 | 0.1808 |
| 59860260 | 2dc_P_K4_S1_001 | regular_1 | COMPLETED | 2026-10-16T19:03:09 | 2026-10-16T19:13:43 | 634 | 51 | 256 | 0:0 | 0.1761 |
| 59871479 | 2dc_P_K2_S4U_NormDISCC0_s54 | regular_1 | COMPLETED | 2026-10-16T22:29:28 | 2026-10-16T22:42:13 | 765 | 30 | 256 | 0:0 | 0.2125 |
| 59871511 | 2dc_P_K2_S4U_Flux23_s45 | regular_1 | COMPLETED | 2026-10-16T22:29:28 | 2026-10-16T22:42:38 | 790 | 30 | 256 | 0:0 | 0.2194 |
| 59871513 | 2dc_P_K2_S4U_Flux23_s51 | regular_1 | COMPLETED | 2026-10-16T22:45:21 | 2026-10-16T22:58:31 | 790 | 30 | 256 | 0:0 | 0.2194 |
| 59871569 | 2dc_P_K2_S4U_MaRES0_s42 | regular_1 | COMPLETED | 2026-10-16T22:45:21 | 2026-10-16T22:57:37 | 736 | 30 | 256 | 0:0 | 0.2044 |
| 59871571 | 2dc_P_K2_S4U_MaRES0_s48 | regular_1 | COMPLETED | 2026-10-16T23:45:47 | 2026-10-16T23:58:37 | 770 | 30 | 256 | 0:0 | 0.2139 |
| 59871572 | 2dc_P_K2_S4U_MaRES0_s54 | regular_1 | COMPLETED | 2026-10-16T23:45:47 | 2026-10-16T23:58:53 | 786 | 30 | 256 | 0:0 | 0.2183 |
| 59871579 | 2dc_P_K2_S4U_MaCCQE0_s45 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:01:53 | 753 | 30 | 256 | 0:0 | 0.2092 |
| 59871581 | 2dc_P_K2_S4U_MaCCQE0_s51 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:04:30 | 910 | 30 | 256 | 0:0 | 0.2528 |
| 59871586 | 2dc_P_K2_S4U_2p2h0_s42 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:03:36 | 856 | 30 | 256 | 0:0 | 0.2378 |
| 59871587 | 2dc_P_K2_S4U_2p2h0_s48 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:02:16 | 776 | 30 | 256 | 0:0 | 0.2156 |
| 59871588 | 2dc_P_K2_S4U_2p2h0_s54 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:03:02 | 822 | 30 | 256 | 0:0 | 0.2283 |
| 59871590 | 2dc_P_K2_S4U_MinosEfficiency0_s45 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:02:21 | 781 | 30 | 256 | 0:0 | 0.2169 |
| 59871591 | 2dc_P_K2_S4U_MinosEfficiency0_s51 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:02:59 | 819 | 30 | 256 | 0:0 | 0.2275 |
| 59871593 | 2dc_P_K2_S4U_Muon_Energy_MINOS0_s42 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:02:49 | 809 | 30 | 256 | 0:0 | 0.2247 |
| 59871594 | 2dc_P_K2_S4U_Muon_Energy_MINOS0_s48 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:03:45 | 865 | 30 | 256 | 0:0 | 0.2403 |
| 59871595 | 2dc_P_K1_S4U_Muon_Energy_MINOS0_s54 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:02:32 | 792 | 30 | 256 | 0:0 | 0.2200 |
| 59871596 | 2dc_P_K4_S4CV_s45 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:01:09 | 709 | 51 | 256 | 0:0 | 0.1969 |
| 59871682 | 2dc_P_K4_S1_005 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:00:39 | 679 | 51 | 256 | 0:0 | 0.1886 |
| 59871683 | 2dc_P_K4_S1_009 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T00:59:59 | 639 | 51 | 256 | 0:0 | 0.1775 |
| 59871694 | 2dc_P_K4_S1_013 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:00:46 | 686 | 51 | 256 | 0:0 | 0.1906 |
| 59871697 | 2dc_P_K4_S1_017 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:00:15 | 655 | 51 | 256 | 0:0 | 0.1819 |
| 59871699 | 2dc_P_K4_S1_021 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:00:21 | 661 | 51 | 256 | 0:0 | 0.1836 |
| 59871701 | 2dc_P_K4_S1_025 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:00:32 | 672 | 51 | 256 | 0:0 | 0.1867 |
| 59871702 | 2dc_P_K4_S1_029 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:00:48 | 688 | 51 | 256 | 0:0 | 0.1911 |
| 59871703 | 2dc_P_K4_S1_033 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:01:00 | 700 | 51 | 256 | 0:0 | 0.1944 |
| 59871704 | 2dc_P_K4_S1_037 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:01:00 | 700 | 51 | 256 | 0:0 | 0.1944 |
| 59871705 | 2dc_P_K4_S1_041 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:01:00 | 700 | 51 | 256 | 0:0 | 0.1944 |
| 59871707 | 2dc_P_K4_S1_045 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:00:38 | 678 | 51 | 256 | 0:0 | 0.1883 |
| 59871804 | 2dc_P_K4_S1_049 | regular_1 | COMPLETED | 2026-10-17T00:49:20 | 2026-10-17T01:00:50 | 690 | 51 | 256 | 0:0 | 0.1917 |
| 59871807 | 2dc_P_K4_S1_053 | regular_1 | COMPLETED | 2026-10-17T02:20:44 | 2026-10-17T02:31:16 | 632 | 51 | 256 | 0:0 | 0.1756 |
| 59871808 | 2dc_P_K4_S1_057 | regular_1 | COMPLETED | 2026-10-17T02:21:42 | 2026-10-17T02:32:09 | 627 | 51 | 256 | 0:0 | 0.1742 |
| 59871809 | 2dc_P_K4_S1_061 | regular_1 | COMPLETED | 2026-10-17T04:01:07 | 2026-10-17T04:11:33 | 626 | 51 | 256 | 0:0 | 0.1739 |
| 59871810 | 2dc_P_K4_S1_065 | regular_1 | COMPLETED | 2026-10-17T04:03:14 | 2026-10-17T04:13:28 | 614 | 51 | 256 | 0:0 | 0.1706 |
| 59871813 | 2dc_P_K4_S1_069 | regular_1 | COMPLETED | 2026-10-17T05:00:48 | 2026-10-17T05:11:09 | 621 | 51 | 256 | 0:0 | 0.1725 |
| 59871815 | 2dc_P_K4_S1_073 | regular_1 | COMPLETED | 2026-10-17T05:01:50 | 2026-10-17T05:12:05 | 615 | 51 | 256 | 0:0 | 0.1708 |
| 59871818 | 2dc_P_K4_S1_077 | regular_1 | COMPLETED | 2026-10-17T06:20:56 | 2026-10-17T06:31:18 | 622 | 51 | 256 | 0:0 | 0.1728 |
| 59871820 | 2dc_P_K4_S1_081 | regular_1 | COMPLETED | 2026-10-17T06:21:56 | 2026-10-17T06:32:15 | 619 | 51 | 256 | 0:0 | 0.1719 |
| 59871821 | 2dc_P_K4_S1_085 | regular_1 | COMPLETED | 2026-10-17T07:17:24 | 2026-10-17T07:27:35 | 611 | 51 | 256 | 0:0 | 0.1697 |
| 59871824 | 2dc_P_K4_S1_089 | regular_1 | COMPLETED | 2026-10-17T07:17:24 | 2026-10-17T07:27:46 | 622 | 51 | 256 | 0:0 | 0.1728 |
| 59871825 | 2dc_P_K4_S1_093 | regular_1 | COMPLETED | 2026-10-17T08:08:23 | 2026-10-17T08:18:52 | 629 | 51 | 256 | 0:0 | 0.1747 |
| 59871826 | 2dc_P_K4_S1_097 | regular_1 | COMPLETED | 2026-10-17T08:10:30 | 2026-10-17T08:20:43 | 613 | 51 | 256 | 0:0 | 0.1703 |
| 59872059 | 2dc_P_K4_S1_101 | regular_1 | COMPLETED | 2026-10-17T08:37:54 | 2026-10-17T08:48:03 | 609 | 51 | 256 | 0:0 | 0.1692 |
| 59872060 | 2dc_P_K4_S1_105 | regular_1 | COMPLETED | 2026-10-17T08:38:55 | 2026-10-17T08:49:16 | 621 | 51 | 256 | 0:0 | 0.1725 |
| 59872061 | 2dc_P_K4_S1_109 | regular_1 | COMPLETED | 2026-10-17T09:11:59 | 2026-10-17T09:22:20 | 621 | 51 | 256 | 0:0 | 0.1725 |
| 59872062 | 2dc_P_K4_S1_113 | regular_1 | COMPLETED | 2026-10-17T09:17:03 | 2026-10-17T09:27:21 | 618 | 51 | 256 | 0:0 | 0.1717 |
| 59872063 | 2dc_P_K4_S1_117 | regular_1 | COMPLETED | 2026-10-17T09:55:09 | 2026-10-17T10:05:41 | 632 | 51 | 256 | 0:0 | 0.1756 |
| 59872064 | 2dc_P_K4_S1_121 | regular_1 | COMPLETED | 2026-10-17T10:02:27 | 2026-10-17T10:15:21 | 774 | 51 | 256 | 0:0 | 0.2150 |
| 59872065 | 2dc_P_K4_S1_125 | regular_1 | COMPLETED | 2026-10-17T10:35:32 | 2026-10-17T10:47:18 | 706 | 51 | 256 | 0:0 | 0.1961 |
| 59872067 | 2dc_P_K4_S1_129 | regular_1 | COMPLETED | 2026-10-17T10:39:39 | 2026-10-17T10:50:19 | 640 | 51 | 256 | 0:0 | 0.1778 |
| 59872068 | 2dc_P_K4_S1_133 | regular_1 | COMPLETED | 2026-10-17T10:55:16 | 2026-10-17T11:06:30 | 674 | 51 | 256 | 0:0 | 0.1872 |
| 59872069 | 2dc_P_K4_S1_137 | regular_1 | COMPLETED | 2026-10-17T10:56:11 | 2026-10-17T11:06:44 | 633 | 51 | 256 | 0:0 | 0.1758 |
| 59872070 | 2dc_P_K4_S1_141 | regular_1 | COMPLETED | 2026-10-17T11:37:55 | 2026-10-17T11:50:13 | 738 | 51 | 256 | 0:0 | 0.2050 |
| 59872071 | 2dc_P_K4_S1_145 | regular_1 | COMPLETED | 2026-10-17T11:38:56 | 2026-10-17T11:49:51 | 655 | 51 | 256 | 0:0 | 0.1819 |
| 59872181 | 2dc_P_K4_S1_149 | regular_1 | COMPLETED | 2026-10-17T12:02:50 | 2026-10-17T12:13:08 | 618 | 51 | 256 | 0:0 | 0.1717 |
| 59872182 | 2dc_P_K4_S1_153 | regular_1 | COMPLETED | 2026-10-17T12:04:53 | 2026-10-17T12:16:00 | 667 | 51 | 256 | 0:0 | 0.1853 |
| 59872183 | 2dc_P_K4_S1_157 | regular_1 | COMPLETED | 2026-10-17T12:30:49 | 2026-10-17T12:41:02 | 613 | 51 | 256 | 0:0 | 0.1703 |
| 59872186 | 2dc_P_K4_S1_161 | regular_1 | COMPLETED | 2026-10-17T12:44:00 | 2026-10-17T12:54:32 | 632 | 51 | 256 | 0:0 | 0.1756 |
| 59872187 | 2dc_P_K4_S1_165 | regular_1 | COMPLETED | 2026-10-17T13:01:13 | 2026-10-17T13:12:40 | 687 | 51 | 256 | 0:0 | 0.1908 |
| 59872188 | 2dc_P_K4_S1_169 | regular_1 | COMPLETED | 2026-10-17T13:04:14 | 2026-10-17T13:15:04 | 650 | 51 | 256 | 0:0 | 0.1806 |
| 59872190 | 2dc_P_K4_S1_173 | regular_1 | COMPLETED | 2026-10-17T13:44:12 | 2026-10-17T13:54:43 | 631 | 51 | 256 | 0:0 | 0.1753 |
| 59872223 | 2dc_P_K4_S1_177 | regular_1 | COMPLETED | 2026-10-17T13:51:18 | 2026-10-17T14:02:31 | 673 | 51 | 256 | 0:0 | 0.1869 |
| 59872227 | 2dc_P_K4_S1_181 | regular_1 | COMPLETED | 2026-10-17T14:12:52 | 2026-10-17T14:24:20 | 688 | 51 | 256 | 0:0 | 0.1911 |
| 59872230 | 2dc_P_K4_S1_185 | regular_1 | COMPLETED | 2026-10-17T14:16:06 | 2026-10-17T14:26:22 | 616 | 51 | 256 | 0:0 | 0.1711 |
| 59872233 | 2dc_P_K4_S1_189 | regular_1 | COMPLETED | 2026-10-17T14:28:35 | 2026-10-17T14:38:54 | 619 | 51 | 256 | 0:0 | 0.1719 |
| 59872237 | 2dc_P_K4_S1_193 | regular_1 | COMPLETED | 2026-10-17T14:29:45 | 2026-10-17T14:40:33 | 648 | 51 | 256 | 0:0 | 0.1800 |
| 59872238 | 2dc_P_K4_S1_197 | regular_1 | COMPLETED | 2026-10-17T14:54:14 | 2026-10-17T15:04:38 | 624 | 51 | 256 | 0:0 | 0.1733 |
| 59872372 | 2dc_P_K4_S1_201 | regular_1 | COMPLETED | 2026-10-17T14:55:17 | 2026-10-17T15:05:42 | 625 | 51 | 256 | 0:0 | 0.1736 |
| 59872373 | 2dc_P_K4_S1_205 | regular_1 | COMPLETED | 2026-10-17T15:22:41 | 2026-10-17T15:33:50 | 669 | 51 | 256 | 0:0 | 0.1858 |
| 59872374 | 2dc_P_K4_S1_209 | regular_1 | COMPLETED | 2026-10-17T15:22:41 | 2026-10-17T15:32:58 | 617 | 51 | 256 | 0:0 | 0.1714 |
| 59872375 | 2dc_P_K4_S1_213 | regular_1 | COMPLETED | 2026-10-17T15:34:58 | 2026-10-17T15:47:18 | 740 | 51 | 256 | 0:0 | 0.2056 |
| 59872376 | 2dc_P_K4_S1_217 | regular_1 | COMPLETED | 2026-10-17T15:37:00 | 2026-10-17T15:47:16 | 616 | 51 | 256 | 0:0 | 0.1711 |
| 59872377 | 2dc_P_K4_S1_221 | regular_1 | COMPLETED | 2026-10-17T17:20:42 | 2026-10-17T17:31:24 | 642 | 51 | 256 | 0:0 | 0.1783 |
| 59872378 | 2dc_P_K4_S1_225 | regular_1 | COMPLETED | 2026-10-17T17:20:42 | 2026-10-17T17:31:13 | 631 | 51 | 256 | 0:0 | 0.1753 |
| 59872379 | 2dc_P_K4_S1_229 | regular_1 | COMPLETED | 2026-10-17T17:51:12 | 2026-10-17T18:01:31 | 619 | 51 | 256 | 0:0 | 0.1719 |
| 59872380 | 2dc_P_K4_S1_233 | regular_1 | COMPLETED | 2026-10-17T17:53:45 | 2026-10-17T18:04:00 | 615 | 51 | 256 | 0:0 | 0.1708 |
| 59872381 | 2dc_P_K4_S1_237 | regular_1 | COMPLETED | 2026-10-17T18:47:56 | 2026-10-17T18:58:17 | 621 | 51 | 256 | 0:0 | 0.1725 |
| 59872382 | 2dc_P_K4_S1_241 | regular_1 | COMPLETED | 2026-10-17T18:50:23 | 2026-10-17T19:00:32 | 609 | 51 | 256 | 0:0 | 0.1692 |
| 59872383 | 2dc_P_K4_S1_245 | regular_1 | COMPLETED | 2026-10-17T18:52:49 | 2026-10-17T19:03:06 | 617 | 51 | 256 | 0:0 | 0.1714 |
| 59872497 | 2dc_P_K4_S1_249 | regular_1 | COMPLETED | 2026-10-17T18:57:49 | 2026-10-17T19:08:01 | 612 | 51 | 256 | 0:0 | 0.1700 |
| 59872498 | 2dc_P_K4_S1_253 | regular_1 | COMPLETED | 2026-10-17T19:07:08 | 2026-10-17T19:17:20 | 612 | 51 | 256 | 0:0 | 0.1700 |
| 59872499 | 2dc_P_K4_S1_257 | regular_1 | COMPLETED | 2026-10-17T19:07:08 | 2026-10-17T19:17:15 | 607 | 51 | 256 | 0:0 | 0.1686 |
| 59872500 | 2dc_P_K4_S1_261 | regular_1 | COMPLETED | 2026-10-17T19:14:35 | 2026-10-17T19:25:14 | 639 | 51 | 256 | 0:0 | 0.1775 |
| 59872501 | 2dc_P_K4_S1_265 | regular_1 | COMPLETED | 2026-10-17T19:17:03 | 2026-10-17T19:27:21 | 618 | 51 | 256 | 0:0 | 0.1717 |
| 59872502 | 2dc_P_K4_S1_269 | regular_1 | COMPLETED | 2026-10-17T19:24:57 | 2026-10-17T19:35:10 | 613 | 51 | 256 | 0:0 | 0.1703 |
| 59872503 | 2dc_P_K4_S1_273 | regular_1 | COMPLETED | 2026-10-17T19:27:36 | 2026-10-17T19:38:01 | 625 | 51 | 256 | 0:0 | 0.1736 |
| 59872504 | 2dc_P_K4_S1_277 | regular_1 | COMPLETED | 2026-10-17T19:27:52 | 2026-10-17T19:38:12 | 620 | 51 | 256 | 0:0 | 0.1722 |
| 59872505 | 2dc_P_K4_S1_281 | regular_1 | COMPLETED | 2026-10-17T19:57:53 | 2026-10-17T20:08:12 | 619 | 51 | 256 | 0:0 | 0.1719 |
| 59872507 | 2dc_P_K4_S1_285 | regular_1 | COMPLETED | 2026-10-17T19:57:53 | 2026-10-17T20:08:04 | 611 | 51 | 256 | 0:0 | 0.1697 |
| 59872508 | 2dc_P_K4_S1_289 | regular_1 | COMPLETED | 2026-10-17T20:12:16 | 2026-10-17T20:22:25 | 609 | 51 | 256 | 0:0 | 0.1692 |
| 59872510 | 2dc_P_K4_S1_293 | regular_1 | COMPLETED | 2026-10-17T20:12:16 | 2026-10-17T20:22:32 | 616 | 51 | 256 | 0:0 | 0.1711 |
| 59872511 | 2dc_P_K4_S1_297 | regular_1 | COMPLETED | 2026-10-17T20:15:03 | 2026-10-17T20:25:16 | 613 | 51 | 256 | 0:0 | 0.1703 |
| 59872701 | 2dc_P_K4_S2_001 | regular_1 | COMPLETED | 2026-10-17T20:20:11 | 2026-10-17T20:30:38 | 627 | 51 | 256 | 0:0 | 0.1742 |
| 59872707 | 2dc_P_K4_S2_005 | regular_1 | COMPLETED | 2026-10-17T20:32:39 | 2026-10-17T20:43:00 | 621 | 51 | 256 | 0:0 | 0.1725 |
| 59872713 | 2dc_P_K4_S2_009 | regular_1 | COMPLETED | 2026-10-17T20:34:44 | 2026-10-17T20:44:56 | 612 | 51 | 256 | 0:0 | 0.1700 |
| 59872714 | 2dc_P_K4_S2_013 | regular_1 | COMPLETED | 2026-10-17T20:38:45 | 2026-10-17T20:48:58 | 613 | 51 | 256 | 0:0 | 0.1703 |
| 59872716 | 2dc_P_K4_S2_017 | regular_1 | COMPLETED | 2026-10-17T20:39:01 | 2026-10-17T20:49:17 | 616 | 51 | 256 | 0:0 | 0.1711 |
| 59872717 | 2dc_P_K4_S2_021 | regular_1 | COMPLETED | 2026-10-17T20:41:08 | 2026-10-17T20:51:28 | 620 | 51 | 256 | 0:0 | 0.1722 |
| 59872720 | 2dc_P_K4_S2_025 | regular_1 | COMPLETED | 2026-10-17T20:43:21 | 2026-10-17T20:53:41 | 620 | 51 | 256 | 0:0 | 0.1722 |
| 59872721 | 2dc_P_K4_S2_029 | regular_1 | COMPLETED | 2026-10-17T20:49:50 | 2026-10-17T21:00:05 | 615 | 51 | 256 | 0:0 | 0.1708 |
| 59872723 | 2dc_P_K4_S2_033 | regular_1 | COMPLETED | 2026-10-17T20:51:43 | 2026-10-17T21:01:51 | 608 | 51 | 256 | 0:0 | 0.1689 |
| 59872724 | 2dc_P_K4_S2_037 | regular_1 | COMPLETED | 2026-10-17T20:52:01 | 2026-10-17T21:02:08 | 607 | 51 | 256 | 0:0 | 0.1686 |
| 59872725 | 2dc_P_K4_S2_041 | regular_1 | COMPLETED | 2026-10-17T20:54:06 | 2026-10-17T21:04:35 | 629 | 51 | 256 | 0:0 | 0.1747 |
| 59872727 | 2dc_P_K4_S2_045 | regular_1 | COMPLETED | 2026-10-17T21:00:20 | 2026-10-17T21:10:43 | 623 | 51 | 256 | 0:0 | 0.1731 |
| 59872934 | 2dc_P_K4_S2_049 | regular_1 | COMPLETED | 2026-10-17T21:02:25 | 2026-10-17T21:12:39 | 614 | 51 | 256 | 0:0 | 0.1706 |
| 59872937 | 2dc_P_K4_S2_053 | regular_1 | COMPLETED | 2026-10-17T21:06:22 | 2026-10-17T21:16:43 | 621 | 51 | 256 | 0:0 | 0.1725 |
| 59872939 | 2dc_P_K4_S2_057 | regular_1 | COMPLETED | 2026-10-17T21:06:22 | 2026-10-17T21:16:40 | 618 | 51 | 256 | 0:0 | 0.1717 |
| 59872942 | 2dc_P_K4_S2_061 | regular_1 | COMPLETED | 2026-10-17T21:06:44 | 2026-10-17T21:17:07 | 623 | 51 | 256 | 0:0 | 0.1731 |
| 59872947 | 2dc_P_K4_S2_065 | regular_1 | COMPLETED | 2026-10-17T21:10:48 | 2026-10-17T21:20:53 | 605 | 51 | 256 | 0:0 | 0.1681 |
| 59872950 | 2dc_P_K4_S2_069 | regular_1 | COMPLETED | 2026-10-17T21:16:36 | 2026-10-17T21:27:28 | 652 | 51 | 256 | 0:0 | 0.1811 |
| 59872954 | 2dc_P_K4_S2_073 | regular_1 | COMPLETED | 2026-10-17T21:16:39 | 2026-10-17T21:27:42 | 663 | 51 | 256 | 0:0 | 0.1842 |
| 59872956 | 2dc_P_K4_S2_077 | regular_1 | COMPLETED | 2026-10-17T21:19:05 | 2026-10-17T21:29:21 | 616 | 51 | 256 | 0:0 | 0.1711 |
| 59872958 | 2dc_P_K4_S2_081 | regular_1 | COMPLETED | 2026-10-17T21:26:37 | 2026-10-17T21:37:02 | 625 | 51 | 256 | 0:0 | 0.1736 |
| 59872960 | 2dc_P_K4_S2_085 | regular_1 | COMPLETED | 2026-10-17T21:26:40 | 2026-10-17T21:37:01 | 621 | 51 | 256 | 0:0 | 0.1725 |
| 59872962 | 2dc_P_K4_S2_089 | regular_1 | COMPLETED | 2026-10-17T21:27:00 | 2026-10-17T21:37:12 | 612 | 51 | 256 | 0:0 | 0.1700 |
| 59872965 | 2dc_P_K4_S2_093 | regular_1 | COMPLETED | 2026-10-17T21:28:48 | 2026-10-17T21:39:12 | 624 | 51 | 256 | 0:0 | 0.1733 |
| 59872981 | 2dc_P_K4_S2_097 | regular_1 | COMPLETED | 2026-10-17T21:32:48 | 2026-10-17T21:43:01 | 613 | 51 | 256 | 0:0 | 0.1703 |
| 59882311 | 2dc_P_K4_S4B_s45_01 | regular_1 | COMPLETED | 2026-10-17T21:34:42 | 2026-10-17T21:44:53 | 611 | 51 | 256 | 0:0 | 0.1697 |
| 59882313 | 2dc_P_K4_S4B_s45_05 | regular_1 | COMPLETED | 2026-10-17T21:38:16 | 2026-10-17T21:48:24 | 608 | 51 | 256 | 0:0 | 0.1689 |
| 59882314 | 2dc_P_K4_S4B_s45_09 | regular_1 | COMPLETED | 2026-10-17T21:51:45 | 2026-10-17T22:02:20 | 635 | 51 | 256 | 0:0 | 0.1764 |
| 59882316 | 2dc_P_K4_S4B_s45_13 | regular_1 | COMPLETED | 2026-10-17T21:51:46 | 2026-10-17T22:02:05 | 619 | 51 | 256 | 0:0 | 0.1719 |
| 59882317 | 2dc_P_K4_S4B_s45_17 | regular_1 | COMPLETED | 2026-10-17T21:52:06 | 2026-10-17T22:02:17 | 611 | 51 | 256 | 0:0 | 0.1697 |
| 59882319 | 2dc_P_K4_S4B_s48_01 | regular_1 | COMPLETED | 2026-10-17T21:52:06 | 2026-10-17T22:02:20 | 614 | 51 | 256 | 0:0 | 0.1706 |
| 59882321 | 2dc_P_K4_S4B_s48_05 | regular_1 | COMPLETED | 2026-10-17T21:52:06 | 2026-10-17T22:02:28 | 622 | 51 | 256 | 0:0 | 0.1728 |
| 59882322 | 2dc_P_K4_S4B_s48_09 | regular_1 | COMPLETED | 2026-10-17T21:52:06 | 2026-10-17T22:02:19 | 613 | 51 | 256 | 0:0 | 0.1703 |
| 59882326 | 2dc_P_K4_S4B_s48_13 | regular_1 | COMPLETED | 2026-10-17T21:52:06 | 2026-10-17T22:02:25 | 619 | 51 | 256 | 0:0 | 0.1719 |
| 59882328 | 2dc_P_K4_S4B_s48_17 | regular_1 | COMPLETED | 2026-10-17T21:52:06 | 2026-10-17T22:02:29 | 623 | 51 | 256 | 0:0 | 0.1731 |
| 59885464 | 2dc_P_K4_S4B_s51_01 | regular_1 | COMPLETED | 2026-10-17T22:01:33 | 2026-10-17T22:11:47 | 614 | 51 | 256 | 0:0 | 0.1706 |
| 59885465 | 2dc_P_K4_S4B_s51_05 | regular_1 | COMPLETED | 2026-10-17T22:01:33 | 2026-10-17T22:11:50 | 617 | 51 | 256 | 0:0 | 0.1714 |
| 59885466 | 2dc_P_K4_S4B_s51_09 | regular_1 | COMPLETED | 2026-10-17T22:12:03 | 2026-10-17T22:22:19 | 616 | 51 | 256 | 0:0 | 0.1711 |
| 59885467 | 2dc_P_K4_S4B_s51_13 | regular_1 | COMPLETED | 2026-10-17T22:12:03 | 2026-10-17T22:22:14 | 611 | 51 | 256 | 0:0 | 0.1697 |
| 59885468 | 2dc_P_K4_S4B_s51_17 | regular_1 | COMPLETED | 2026-10-17T22:14:28 | 2026-10-17T22:25:05 | 637 | 51 | 256 | 0:0 | 0.1769 |
| 59885469 | 2dc_P_K4_S4B_s54_01 | regular_1 | COMPLETED | 2026-10-17T22:14:28 | 2026-10-17T22:24:53 | 625 | 51 | 256 | 0:0 | 0.1736 |
| 59885470 | 2dc_P_K4_S4B_s54_05 | regular_1 | COMPLETED | 2026-10-17T22:14:28 | 2026-10-17T22:24:50 | 622 | 51 | 256 | 0:0 | 0.1728 |
| 59885471 | 2dc_P_K4_S4B_s54_09 | regular_1 | COMPLETED | 2026-10-17T22:14:28 | 2026-10-17T22:24:50 | 622 | 51 | 256 | 0:0 | 0.1728 |
| 59885472 | 2dc_P_K4_S4B_s54_13 | regular_1 | COMPLETED | 2026-10-17T22:14:28 | 2026-10-17T22:24:40 | 612 | 51 | 256 | 0:0 | 0.1700 |
| 59885473 | 2dc_P_K4_S4B_s54_17 | regular_1 | COMPLETED | 2026-10-17T22:14:28 | 2026-10-17T22:24:48 | 620 | 51 | 256 | 0:0 | 0.1722 |

Total of the charge column: 29.0297.

## 12. Limits and surviving limitations

- **Same model.** The executor and its verifier are the same model, so their blind spots may be correlated. The
  director's F4 verifier (§14) is a separate dispatch.
- **Packed `Deadline=` field not read.** For the 136 packs, the evidence is the `--deadline` flag on every `sbatch`
  line, not `scontrol`'s field. No pack came near the deadline (the last ended 3 days before it).
- **S5 products are diagnostic** until Joseph adopts them (DESIGN §8). Disclosure wording is Stage F's.
- **G2** is carried, not repaired or measured, per the G2 carry decision (§1).
- **C03** shared draw not applied; the background stream is independent (§3).
- **Laterals** are one active-file unfold each at seed 42; their trainer noise is not removed (DESIGN §12).
- **Ensemble error:** C08 has 4 degrees of freedom (71% relative SE of its variance); each X03 seed SD has 4
  (35%).
- **X03 is large relative to σ_ML** (median seed SD of the universe shift 1.24–1.33 σ_ML, non-null universes). It is
  reported, not added, per R5/R7.
- **Stat centring (R9):** the replica mean sits a median 4.43 σ/√300 from E_U. It does not enter the ddof-1
  covariance, but it is reported for Stage F.
- **Shared-QOS gate deviation.** Four shared gates on 2026-10-15 under-counted the jobs in flight, by up to 1.9125
  node-h, because they ran before `sacct` listed the previous batch (§5). No ceiling was affected. It remains a
  breach of DESIGN §6. Director ruling 2026-10-17: disclosure suffices; no separate record (the packed-era coverage
  check closes the hazard).
- **Shared-era gate files overwritten.** The `gatelog/` transcripts of the shared-QOS G2 and S1a–S2b gates and
  submissions were overwritten by the packed path's same-named files (§5 †). Their GATE lines survive in the
  executor's session transcript only. Of the 389 jobs those batches created, 381 were cancelled unstarted by the
  migration, 4 (`S1_001`–`004`) by the smoke migration, and 4 S4U rows completed on the shared QOS; all 389 rows are
  in `sacct`.
- **Operator scripts** (the waiter, sequencer and watchers) are not pinned by any binding; their sha256 and
  transcripts are recorded (§9).
- **Inputs stay on pscratch** (the universe omnifile, MC and flux files, E_U, the sweeps, the VL175 build, the pilot
  outputs); a purge there would block a re-run of S5 from `$NS`, not the products, which are on CFS.

## 13. Stage F inputs and carried items

| input | identity |
|---|---|
| total covariance and blocks | `production_cov.npz` `6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc`, at CFS `…/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz` (and `$NS/results/s5/`) |
| every check and number, inputs with sha256 | `s5.json` `8c815149517857302af4b3a64b0db4148a13515b8182bd6eebb2f89c57d92510` |
| χ²/figure-producer schema | `uq_production_covariance.root` `34cf33f96cd688e2c00064f314ff76d294b0d012b0bed5a4560cb1c2e3fc0df8` |
| item verdicts | the six JSONs in `evidence/production/results/` (sha256 in §1) |
| every production unfold | 531 `out/<job>/xsec.root` on CFS, sha256 in `SHA256SUMS.pscratch` `eab367a6…` |
| package | `main`: shared `4139548b`, packed `c873cc22` (PR #131, #138) |
| G2 | [`DECISION-20261015-joseph-g2-carry.md`](../../../../DECISION-20261015-joseph-g2-carry.md) |

**Carried:**
- `driver_p1.py` (`3056e625…`) reaches `2d-unfolding/` on `main` through its own reviewed PR before Stage F
  adoption (2026-10-15 binding ruling 1; packing binding §4). Not done here.
- The director's playlist-term combination (F9) reads `production_cov.npz` `6689d2fc…`.

**Recovery routes.**
- Products: from CFS, verified by `sha256sum -c SHA256SUMS.pscratch`.
- `uq_production_covariance.root`: regenerable from the NPZ (DESIGN §8).
- S5: re-runnable on a login node with `s5_rollup.py` `6c437004…` against `out_root` `$NS/out` while the pscratch
  inputs survive. Reading the CFS copy of `out/` instead needs a director ruling, since the item JSONs record
  `$NS/out` and S5 checks that.
- Unfolds: each job's `jobs.tsv` row (`c4f1b708…`) and the deployed package regenerate it; any re-run needs a new
  grant.

## 14. Independent review

**Executor's verifier** (fresh, read-only, detached worktree at `093d9011`, git-dir ≠ git-common-dir; same model as
the executor, so their blind spots may be correlated). It re-measured from fresh `sacct`, the namespace, the CFS copy
and the committed evidence. **Verdict: APPROVE WITH CHANGES, 1 MATERIAL, 9 MINOR.**

It confirmed:
- 539 allocations (153 ran, all COMPLETED 0:0; 386 never started), the charge 29.0297 and its split, and all 153
  rows of §11 field by field; the committed `sacct` file equals fresh `sacct`;
- 515 member steps and all 821 steps COMPLETED 0:0; 137 status files with `#pack`, 515 member rc 0;
- every result file's sha256 on `$NS` equals the committed copy and §1/§3; every quoted verdict and difference;
- from the NPZ with numpy: total = universe + stat + c08 exactly, universe = the 43 sorted bands + normalization
  exactly, the normalization block, symmetry, eigenvalue ratios, every σ summary and functional range, σ_bkg/σ_stat
  and X02 (the stat block from replicas, X03, centring and the jackknife SEs are not recomputable from the NPZ);
- CFS `sha256sum -c` rc 0, 2,359 files, the committed `SHA256SUMS.pscratch` equal to the CFS one;
- every packed GATE line, the poll "completed" terms recomputed from `sacct`, the `Deadline=` reads, the migration
  id sets, both deploy verifications (re-run), and the five watcher sha256.

| finding | disposition |
|---|---|
| M1 four shared-QOS gates (S1b, S1c, S1d, S1f) ran before `sacct` listed the previous batch, under-counting in-flight caps by up to 1.9125; not disclosed | disclosed in §5 (table of printed vs true) and §12; no ceiling affected (true maximum 79.4263) |
| m2 119 CV packs 20.9473 vs `sacct` 20.9472 | fixed (§6) |
| m3 maintenance time 13:00Z vs the grant's 06:00Z | §7 names both and the stricter 06:00Z |
| m4 S4a wait window understated | fixed: 21 polls from 21:30:34Z (§5); the v1 rule note's time fixed |
| m5 c0 and s3 digests missing from §1 | added |
| m6 S5 check count: 55 in `s5.json`, 54 printed | §1 and §3 state both |
| m7 "rank" undefined | threshold stated (§3) |
| m8 null-band bound 4e-8% vs 4.13e-8% | fixed (4.2e-8%) |
| m9 header claims every number from files, but † rows come from a transcript | header carves them out |
| m10 † times approximate; director-correspondence claims uncommitted; DeadLine-reason claim covers only the throughput window | † times are now first `sacct` Submits; the claims say "in correspondence, not committed"; §7 scopes the DeadLine-reason claim and rests the result on `sacct` |

**Re-review 1** (`7e0e181e`): **APPROVE**, all 10 dispositions confirmed; 2 new MINOR, both fixed in the next commit:

| finding | disposition |
|---|---|
| n1 "at least 2 min … equal counts" held for S1b–S2b only (S1a ≤ 92 s after G2, count check not in evidence; S4a/S4b under the v2 rule) | §5 now states how each packed gate applied DESIGN §14.4 step 4, and that the printed in-flight was complete at the gates recomputed |
| n2 footnote range 22:19–22:27Z vs G2's first Submit 22:18:51 | 22:18–22:27Z |

**Director's F4 verifier** (dispatched by the director on PR #150 at `5a247ee3`): **VERIFIED WITH FINDINGS, 0 MATERIAL,
4 MINOR**, as relayed by the director; the director's F4 record with the verifier's outputs goes on `main` under
`stageF/`. It rebuilt every S5 block from the 530 consumed `xsec.root` vectors with its own code (universe, the 43
bands, normalization, c08, X02 and F at 0.0; stat 1.4e-16; bkg-separable 9.8e-17; total 8.8e-19; the 31 functional σ
match `s5.json`), and confirmed the 10 result files byte-identical across pscratch, CFS and `evidence/`, the
`repo_k` code against the binding, 539/153/386 and 29.0297, all 531 `xsec.root` under `sha256sum -c` on pscratch and
CFS, and the four gate shortfalls. Dispositions, all in one commit:

| finding | disposition |
|---|---|
| F1 X01/Flux implementation details not stated in DESIGN §8 | named in §3, citing `s5_rollup.py:144-194` |
| F2 † shared-era GATE lines exist only in the session transcript | verbatim extract committed as `gatelog/shared_era_gate_lines_from_transcript.txt`, with the transcript path and the sha256 of its byte prefix (§5 †) |
| F3 the director's ruling on the gate deviation | added to §12 as sent |
| F4 01:03:11 and 02:36:04 are the waiter's submit-completion times | relabelled in §4, with the `sacct` Submit windows |
