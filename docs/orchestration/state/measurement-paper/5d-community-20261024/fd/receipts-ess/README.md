# ESS of configuration (e)'s final unfolded weights on the 16 reported cells: receipt (job 61082774, COMPLETED)

The valid-region lane, 2026-11-10. This answers the interim GPT referee's major issue 7, under the director's task of
2026-11-10, which Joseph approved, and the director's rulings 1-3: the rerun route; (B) printed with (A) beside it;
the data-side n_eff as a labelled extra. The director gave the go at exact bytes:
- the tool commit 96a13a792e4e010aa895f47fb5915d6ef9987d1f (`ess_capture.py` 4755681f…, `sbatch_ess.sh` 7ceb35bb…);
- the connect `ess_connect.sh` d8f2be393f1375f757aee5b1e5715998b68311531cb1268557d93a0c4c1d9e1e;
- the post `ess_post.sh` 36499758cfb6cabbbdcdf03d1f8c39ccbc3fa7fe367ea798306e882eb3466471;
- the launcher `ess_launch.sh` 19a33d445360fde51fd60b2a173f98ab2100eb36f42eda0f52a3af8e4559dece.

Nothing was changed after the go. The run happened once.

CITABLE FOR:
- the re-made central product's `xsec_flat` is byte-identical to fb5cc679's, the product behind the 16-cell result
  (s1_assemble.py:49);
- every number in the table below, and the global row, as the per-event Kish n_eff and weight tails of that result's
  simulated events under (B) and (A);
- the data-side `refinement.n_eff_refined` 4,259,159.7, labelled as the measured sample's;
- the job's charge, 0.2206 node-h.

NOT CITABLE FOR:
- an uncertainty, a coverage or validity statement, or any change to the result or its covariance;
- the ESS of any other product (the 50 bootstrap replicas, the seeds, the universes, configuration (a) or (f));
- why (A) and (B) coincide here: this job measures that they do, not the cause (section "A and B").

## The run

- **Node.** A read-only load survey of login20-32 found login21 quietest, at 8.44 / 9.52 / 8.66 on 244 CPUs
  (`lane/login-survey.txt`). login21 was passed as the launcher's NODE argument, so no byte changed.
- **Connect** (`cluster/logs/connect.log.txt`; `lane/connect-readback.txt` is its `cat -n`). It ran on login21 at
  2026-11-10T10:50:57Z and ended rc 0 at 10:52:07Z:
  - iris balance 1568.3 node-h, half 784.1, bound 0.5 (lines 11-13);
  - a fresh clone at abdc88c5, porcelain --ignored 0 (line 14);
  - the 11 producer files and setup_salloc_env.sh OK, and the tool's two files OK against the tool commit;
  - env python 3.11.14, numpy 1.26.4, lightgbm 4.6.0, ROOT 6.28/12 (line 30);
  - "Submitted batch job 61082774", with scontrol TimeLimit 00:30:00 (lines 33-35).
- **Job** (`cluster/sacct.txt`). ess_e 61082774 COMPLETED 0:0 after an ElapsedRaw of 794 s on 1 node, from
  2026-11-10T02:56:01 to 03:09:15 Pacific. Its one srun step, `61082774.0`, ran 776 s.
  - The charge is 794 × 1 / 3600 = 0.2206 node-h, against the bound 0.5.
  - `cluster/charge_node_h.txt` has a second line, 0.2156. That is the srun step (776 s), which the post's awk also
    matched because it compared JobIDs numerically. The job's charge is the first line.
  - The producer's own `seconds_unfold` was 653.123 (`cluster/logs/ess-run-61082774.log.txt`), against 692.864
    when the product was first made.
- **DONE** (`cluster/logs/DONE-61082774`): rc 0, deploy porcelain --ignored 0 after, stage_dir_left false.
- **Reads** (`cluster/ess/ess.json` "reads", line 24). The three shared inputs were each read once through O_NOATIME
  into /dev/shm/ess-61082774; os.stat before and after were equal, atime included; the copy digests were 07fccc1a…,
  2addac8f… and fb5cc679…. The post's stat (`cluster/stat-post.txt`) equals the connect's
  (`cluster/logs/stat-connect.txt`) field for field: bytes, atime, mtime, inode.
- **Post and fetch.**
  - The post ran on login21 at 2026-11-10T11:13:14Z and ended rc 0 (`cluster/post.log.txt`).
  - post.tar.gz has sha256 e709a651a65f37cf25d2a2b385815e07759fcc66601c10cec82120c141fb8a8c (`lane/fetch-sha256.txt`).
  - `shasum -c SHA256SUMS` gives 20 of 20 OK.
  - The re-made product stays on pscratch: `ess/product/data_b-_j-.npz`, sha256
    a23bbfc7ddbd9c54c92aa73473392b6655564ab863962412ad03d3c5a2590eed. `*.npz` is gitignored. Its file digest
    differs from fb5cc679's because its meta carries this run's job id and seconds; the binding is on `xsec_flat`.
  - `*.log` and `*.out` are committed as `.txt` (`RENAMES.tsv`).

## The binding and the checks

From `cluster/ess/ess.json`, sha256 d4f1268d6eea9d9e19defe60890f815f44ed31bdfb48f4c8d3e0ca2caa9aae65:
- **binding** (line 109): `xsec_flat_bytes_equal` true over 65,856 entries; `captured_equals_remade` true.
- **meta_compare** (line 98): equal after removing exactly slurm_job, slurm_step, seconds_load, seconds_unfold and
  refinement.seconds; `differing_keys` is the empty list.
- **checks** (line 116):
  - recomputed_xs_bytes_equal, edges_equal_fine_grid, event_index_counts_equal (exact counts against
    np.histogramdd), fine_map_digest_equal (930326a3) and volume_equal are all true;
  - the cell sums of (B) reproduce f_R to 3.8e-15;
  - f_R from U·xs equals fd_data_product_cpl.json's f to 3.3e-16 (main 025459c8f, d6752d2c);
  - 0 events sit in a fine cell with a zero denominator.
- **verdict** (line 1121): "PASS: the re-made xsec_flat equals fb5cc679's byte for byte; ESS computed".

## The numbers

The definitions are as printed in ess.json "definitions":
- **Kish:** n_eff = (Σw)²/Σw² over the simulated events of the set.
- **(B):** w_i = 1e4·wpush_i·w_truth_i / (comp_f·flux_f·N·POT), each event's contribution to the reported cell integral.
- **(A):** wpush_i·w_truth_i.
- **prior:** w_truth_i, a labelled reference.
- **Tails:** numpy's linear percentile at 99 and 99.9, over the set's mean weight. The max share is the largest
  single weight over the set's sum.
- **Events with no reconstructed partner:** their step-1 weight was filled by the regressor. They are included in
  every set, and the last column gives their share of the (B) sum.

Per cell ("cells", line 126) and over the 16 cells together ("global"."reported_16_cells", line 960):

| cell | events n | n_eff (B) | n_eff/n (B) | p99/mean (B) | p99.9/mean (B) | max share (B) | n_eff/n (A) | n_eff/n (prior) | no-reco share of B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R00 | 4,060,485 | 2,589,013 | 0.638 | 3.28 | 12.11 | 3.73e-06 | 0.638 | 0.723 | 0.326 |
| R01 | 3,798,081 | 3,632,426 | 0.956 | 1.75 | 2.24 | 1.13e-06 | 0.956 | 0.985 | 0.489 |
| R02 | 901,832 | 844,054 | 0.936 | 1.36 | 1.40 | 1.57e-06 | 0.936 | 0.949 | 0.401 |
| R03 | 526,907 | 478,417 | 0.908 | 1.67 | 1.84 | 3.79e-06 | 0.908 | 0.922 | 0.356 |
| R04 | 5,772,542 | 3,532,059 | 0.612 | 4.06 | 11.91 | 4.79e-06 | 0.612 | 0.681 | 0.157 |
| R05 | 886,761 | 824,004 | 0.929 | 1.95 | 2.89 | 6.52e-06 | 0.929 | 0.975 | 0.228 |
| R06 | 758,693 | 707,444 | 0.932 | 1.60 | 1.98 | 3.77e-06 | 0.932 | 0.950 | 0.183 |
| R07 | 360,147 | 325,119 | 0.903 | 1.72 | 2.12 | 8.97e-06 | 0.903 | 0.921 | 0.180 |
| R08 | 1,483,408 | 1,368,250 | 0.922 | 1.41 | 1.47 | 1.49e-06 | 0.922 | 0.936 | 0.548 |
| R09 | 4,223,666 | 4,056,504 | 0.960 | 1.39 | 2.23 | 6.79e-07 | 0.960 | 0.964 | 0.627 |
| R10 | 895,241 | 839,563 | 0.938 | 1.40 | 1.46 | 2.29e-06 | 0.938 | 0.943 | 0.561 |
| R11 | 637,547 | 589,323 | 0.924 | 1.33 | 1.44 | 2.38e-06 | 0.924 | 0.926 | 0.681 |
| R12 | 2,217,692 | 2,068,195 | 0.933 | 1.54 | 1.95 | 2.56e-06 | 0.933 | 0.945 | 0.270 |
| R13 | 962,469 | 875,155 | 0.909 | 1.51 | 2.20 | 2.85e-06 | 0.909 | 0.915 | 0.448 |
| R14 | 4,147,782 | 3,754,166 | 0.905 | 2.23 | 3.36 | 1.35e-06 | 0.905 | 0.953 | 0.387 |
| R15 | 1,213,048 | 1,129,160 | 0.931 | 1.49 | 2.06 | 2.32e-06 | 0.931 | 0.939 | 0.302 |
| 16 cells (global) | 32,846,301 | 26,899,121 | 0.819 | 2.17 | 7.70 | 7.65e-07 | 0.819 | 0.859 | 0.383 |

- (B) n_eff/n ranges from 0.612 (R04) to 0.960 (R09). The smallest n_eff is 325,119 (R07); the largest single-event
  share is 8.97e-6 (R07); the heaviest 99.9 % tails are R00 (12.11) and R04 (11.91).
- The 16 cells hold 32,846,301 simulated events, with n_eff 26,899,121 under (B) (n_eff/n 0.819). The prior's n_eff
  over the same events is 28,218,604 (0.859).
- Every (A) and (B) weight in the 16 cells is positive (each n_negative is 0).
- The whole truth-selected ensemble ("whole_truth_selected_ensemble_A_only") has 32,849,103 events, (A) n_eff/n 0.819
  against the prior's 0.859, and 12,444,811 events with no reconstructed partner.
- **Data side** ("data_side_refinement", line 1099): `n_eff_refined` 4,259,159.7 and `n_eff_signed_abs`
  4,307,071.2, identical in the reference and re-made metas. This is the Kish n_eff of the refined measured-data
  weights feeding step 1, over the whole sample. It does not describe the unfolded simulated ensemble.

## A and B

In every cell, (A) and (B) agree in n_eff to 6.6e-7 relative, and in n_eff/n, both percentiles and the max share to
the printed figures. ΣB/ΣA, the per-event conversion factor averaged over a cell, ranges from 4.681991e-45 to
4.682018e-45 across the 16 cells, a spread of 5.7e-6. So within this result the per-fine-cell factor
1e4/(comp_f·flux_f·N·POT) is constant to a few parts per million, and the two definitions give the same ESS. The
job's JSON records the per-event sums; it does not record the factors' components, so it does not show which of
completeness or flux is responsible.

## Local test

`lane/local-test-at-96a13a79.txt` is `test_ess_capture.py` run from a clean clone at the tool commit (porcelain 0,
the three tool digests as above), with python 3.11.15, numpy 1.26.4 and lightgbm 4.6.0. It ran a synthetic PASS, a
one-ulp STOP (rc 8), a wrong pin (rc 9), the read guard, and --fixture refused in Slurm. The result was ALL PASS,
test rc 0.
