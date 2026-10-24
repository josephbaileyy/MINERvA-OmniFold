# RE-2 part B report: the 2D production rebuild's runs, controls, charge and cleanup (2026-10-24, re-1 lane)

**Status.**
- All 12 part-B jobs ran once and COMPLETED, with exit 0:0.
- All 644 runs completed, and every output is digested.
- Both verdicts are **PASS**:
  - the core (J1–J4, J6, J8): 589 of 589 checks, with 605 of 605 health and argv rows;
  - the gated diagnostic J7: 7 of 7 checks, with 39 of 39 health and argv rows.
- Part B charged **47.7083 CPU node-h**. With J0's 5.4755 that is **53.1838** of the 90 node-h grant.
- The staged inputs were deleted under B9's conditions, and each deletion is ledgered.

The jobs were bound by [`RE2-BINDING-B.md`](RE2-BINDING-B.md) and its
[amendment 1](RE2-BINDING-B-AMENDMENT-1.md). They ran from a clean deploy at
`dbdad2f93a255f1bd4bf357951aaa5689aaac512`: `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/deploy-dbdad2f9`.

**MEASURES:**
- part B's runs against Stage C, J0, RE-1's D2 and each other;
- the power of the checks;
- the refinement health of every run;
- part B's charge.

**CANNOT AUTHORIZE:**
- post-processing: part C is bound before any post-processing run (RE2-BINDING-B);
- a claim: no product here is a result. `E_R`, `Q_R`, RO-FPS and the combination come from part C.

**Where the records are.** They are in [`run/partb_readout/`](run/partb_readout/), copied from
`/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/`. The files below were re-hashed from the copies here. The
first four match the hashes `re2b_readout.sh` printed on the cluster.

| record | sha256 |
|---|---|
| `k1_core.json` (`re2_k1.py`, core) | `7c407e958e5247f76f4eebdf7caa0dbeff504e13d22da6ed92b41ae1e669d86a` |
| `k1_j7.json` (`re2_k1.py`, J7) | `faa4656d9fb4b38bbc5734bd5fa613ddd09ac6e56b266fd0d40a732d64a1c3b8` |
| `steps.psv` (`sacct`) | `962a21eeb0ae6ed3ba11c55daecbd627bcf852d23faf83ab6184d7740e02ad08` |
| `ledger.tsv` (`re2_ledger.sh`) | `667ee55785b6ad151422e79515e44ddfc722513c3b332b661633f4caa0d9d107` |
| `preflight/inputs.stat` (DTN preflight) | `89595b3e6c4ee3dddc77841ef53ef78b7f71aa488bdf8dfb2ca02254173da0fc` |
| `submissions.log` | `7355be00bf924543bd0785cece2eb2746ffc04652277c7339d3b89749a18ecfb` |
| `deletions.tsv` (B9 cleanup) | `2eb5d0db0013b5d68324983cbd5da0f96f96aab3fc5ebade5d4580f5e1c26f01` |

**The other records:**
- `sums/SHA256SUMS.<job>.<lane>`: 35 files, holding the sha256 of all 644 outputs, which are at
  `partb/out/<label>/xsec.root`;
- `logs/`: the 12 job logs, each submission's gate record, and the empty `sacct` file of the refused first attempt
  (§2, D1);
- `preflight/dtn.log` and `preflight/quota_before.txt`;
- `quota_before_cleanup.txt` and `quota_after_cleanup.txt`.

## 1. The jobs and the ledger

| job | Slurm id | state | start (local) | elapsed | limit | projected wall | elapsed / projected | charge, node-h | cap, node-h |
|---|---|---|---|---|---|---|---|---|---|
| J1 | 60195820 | COMPLETED, 0:0 | 2026-10-24T00:09:09 | 0:15:10 (910 s) | 0:25 | 1,166 s | 0.780 | 0.2528 | 0.4167 |
| J2a | 60195821 | COMPLETED, 0:0 | 2026-10-24T00:09:09 | 5:17:33 (19,053 s) | 8:54 | 25,600 s | 0.744 | 5.2925 | 8.9 |
| J2b | 60195822 | COMPLETED, 0:0 | 2026-10-24T00:14:38 | 5:21:26 (19,286 s) | 8:54 | 25,600 s | 0.753 | 5.3572 | 8.9 |
| J2c | 60195835 | COMPLETED, 0:0 | 2026-10-24T00:14:38 | 5:23:36 (19,416 s) | 8:54 | 25,600 s | 0.758 | 5.3933 | 8.9 |
| J2d | 60195837 | COMPLETED, 0:0 | 2026-10-24T00:14:38 | 5:18:39 (19,119 s) | 8:54 | 25,600 s | 0.747 | 5.3108 | 8.9 |
| J3 | 60195838 | COMPLETED, 0:0 | 2026-10-24T00:14:38 | 1:42:54 (6,174 s) | 3:02 | 8,690 s | 0.710 | 1.7150 | 3.0333 |
| J4a | 60195839 | COMPLETED, 0:0 | 2026-10-24T00:17:10 | 4:50:06 (17,406 s) | 8:06 | 23,300 s | 0.747 | 4.8350 | 8.1 |
| J4b | 60195842 | COMPLETED, 0:0 | 2026-10-24T00:17:10 | 4:52:22 (17,542 s) | 8:06 | 23,300 s | 0.753 | 4.8728 | 8.1 |
| J4c | 60195843 | COMPLETED, 0:0 | 2026-10-24T00:18:29 | 4:57:11 (17,831 s) | 8:06 | 23,300 s | 0.765 | 4.9531 | 8.1 |
| J6 | 60195844 | COMPLETED, 0:0 | 2026-10-24T00:19:43 | 3:54:07 (14,047 s) | 6:30 | 18,700 s | 0.751 | 3.9019 | 6.5 |
| J8 | 60195845 | COMPLETED, 0:0 | 2026-10-24T00:19:43 | 1:08:09 (4,089 s) | 2:09 | 6,180 s | 0.662 | 1.1358 | 2.15 |
| J7 (gated) | 60195846 | COMPLETED, 0:0 | 2026-10-24T00:19:43 | 4:41:17 (16,877 s) | 7:48 | 22,448 s | 0.752 | 4.6881 | 7.8 |
| **part B** | | | | | | | | **47.7083** | 79.80 |

All jobs were regular QOS, one exclusive node (billing 256), `--no-requeue`, on account m3246.

**The charge against the bounds:**
- The core charged 43.0202 node-h, against its projection of 57.51 and its cap sum of 72.00.
- J7 charged 4.6881, against its projection of 6.2356 and its cap of 7.8.
- Part B's 47.7083 is under its projection of 63.75 and its cap sum of 79.80. Room was 84.5245.
- With J0, RE-2 has charged **53.1838** of 90 node-h. The grant sits under the 700 node-h ceiling.

**Wall time against the 1.25× stop rule.**
- Every job ended at 0.66–0.78× of its projected wall time (preflight 300 s plus the longest lane).
- No job came near 1.25×, and no job ended other than COMPLETED.

**Packing.** The run steps' node-h as a share of each job's charge:
- 0.98–1.00 for J2a–d, J3, J4a–c and J6;
- 0.96 for J7;
- 0.89 for J8 and 0.72 for J1, the two shortest jobs, where the fixed preflight and the lane tails weigh most.

**Submission and the gate.**
- Each job was submitted once, at 07:06:49–07:07:03Z (`submissions.log`), by `re2b_submit.sh`. The charge gate
  (`re2b_gate.py`) ran before each one.
- Each gate record counts every earlier part-B attempt. All were still pending, so each counted at its cap. J7's gate gave 72.00 used before, 79.80 after,
  ≤ 84.5245, with J7's own form at 0.0 ledgered + 6.2356 projected: PASS.
- `steps.psv` has exactly 644 run steps, one per `partb_runs.tsv` label, all COMPLETED, besides each job's `batch`
  and `extern` steps. No diagnostic or other step ran.

**Provenance (OI-136).**
- All 644 run inventories have `expect_root` equal to the deploy, outcome `ok` and no repository origin outside
  it.
- The two readout inventories (`re2b_k1_core`, `re2b_k1_j7`) record `EMPTY-REPOSITORY-ORIGIN-SET`.
  - `re2_k1.py` imports no module from a checkout.
  - The loaded-checkout receipt names one root, the deploy (`__main__`).
  - That is the guard reporting that it had nothing to inspect, not a refusal.

## 2. Deviations

**D1. The first submission attempt stopped at the gate, before any `sbatch`** (2026-10-24T06:38:44Z).
- The bound `re2b_submit.sh` passed `sacct -S 2026-10-24`. `sacct` reads that in local time (PDT), so it was still in
  the future and was refused.
- The gate's `sacct` file is empty (`logs/gate-J1-20261024T063844Z.psv`, 0 bytes), and nothing was submitted or
  charged.
- The director bound the fix as amendment 1 (PR #302, `dbdad2f9`, `-S 2026-10-23`). All 12 jobs then ran from a
  fresh clean deploy at that sha.
- The DTN preflight, which ran before the stop, stayed valid under the amendment.

**D2. The lane read J1's outputs once, early.**
- When J1 completed, the lane ran the bound `re2_k1.py` over J1's three runs into a scratch directory,
  `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/review/partb-early/`. The aim was to find a fault while the
  other jobs ran.
- It passed. It is not a record, and the official readout above replaces it.
- It read outputs only, and wrote nothing under `partb/`.

There were no other deviations. Every job ran its declared runs at its declared limit, and nothing was resubmitted.

## 3. The preflight (B3, B9)

- **The quota:** `showquota` at 06:29:40Z read 16.97 of 20.00 TiB (84.8 %). Staging was projected to take it to
  87.3 % ≤ 90 %, the B9 condition (`preflight/quota_before.txt`).
- **The DTN preflight:** it ran on dtn01 from 06:30:03Z to 06:37:09Z (`preflight/dtn.log`).
  - It staged the CV omnifile and the 10 active laterals to `partb/inputs/` (504 G). Each copy hashed to its
    declared digest and was made read-only.
  - It hashed the 171 GB universe omnifile in place, to its declared `220c479e…`.
  - It recorded all 12 files in `preflight/inputs.stat`.
- **In every job,** `re2b_check_inputs` found each input's `stat -c '%s %Y %i'` equal to the DTN record. No input
  was re-hashed; J3's log lists all 10 laterals.

## 4. Controls

**The criteria:**
- Equality checks (`le`) pass at max rel. diff. ≤ 1e-8 on the row's histogram (hXSec2D unless named), with the
  same reported cell set.
- Power checks (`differs`) pass above their row's `min_shift`: 1e-4 for the 171 universe checks, 1e-6 for the
  others (`run/partb_checks.tsv`).
- Stream checks pass when a refined run's signed sum equals its own data-factor sum minus the in-range integral of
  its reference's resampled background (same bootstrap seed), at rel. ≤ 1e-9 (`re2_k1.py:17-19` at `dbdad2f9`).
- Every reference given with a sha256 re-hashed to it: 399 of 399 core checks that carry one.

**Digest coverage:** both readouts find all 644 outputs listed in the `SHA256SUMS.<job>.<lane>` files, with
`mismatched` and `unlisted` both empty.

### 4.1 The core (`k1_core.json`): 589 checks, PASS

| check | kind | test | reference | max rel. diff. |
|---|---|---|---|---|
| PB-ER-rep | le | `ER` | `run:C0_cv` | 9.17e-12 |
| PB-ER-D2 | le | `ER` | RE-1's `d2_data_refined.npz` | 7.45e-12 |
| PB-ER-J0 | le | `ER` | J0's `D_cv` | 9.16e-12 |
| PB-ER-eff | le | `ER` (hEff2D) | J0's `C_cv` | 0 |
| PB-unit | le | `C0_unit` | `run:C0_cv` | 1.43e-12 |
| PB-unit-J0 | le | `C0_unit` | J0's `D_unit` | 5.15e-12 |
| PB-null-NormDISCC_0, _1 | le | `U_NormDISCC_0`, `_1` | `run:ER` | 7.89e-12, 9.17e-12 |
| PB-J0-S1_001 … _008 | le | `S1_001` … `S1_008` | J0's `RB_001` … `RB_008` | 2.73e-13 – 8.34e-12 |
| PB-J0-U_* (4) | le | `U_Flux_23`, `U_MaCCQE_0`, `U_MaRES_0`, `U_NormDISCC_0` | J0's `F_*` | 1.24e-12 – 5.49e-11 |
| PB-J0-S3_BeamAngleX0 | le | `S3_BeamAngleX0` | J0's `FL_BAX0` | 2.2e-12 |
| PB-J0-pu_PA_s42, pu_PA_b01 | le | `pu_PA_s42`, `pu_PA_b01` | J0's `RF_PA`, `RPR_PA_b01` | 4.8e-13, 4.96e-12 |
| PB-stream-S1_* (300) | stream | each S1 replica | Stage C's `2dc_P_S1_*` | 300 of 300, max rel. 7.8e-16 |
| PB-stream-S4B_* (80) | stream | each S4(i) replica, seeds 45, 48, 51, 54 | Stage C's `2dc_P_S4B_s*` | 80 of 80 |
| PB-pow-U_Flux_* (100) | differs | each flux universe | `run:ER` | 0.0636 – 0.405 |
| PB-pow-U_* (71, 35 bands) | differs | each other universe | `run:ER` | 0.0100 – 0.139 |
| PB-pow-S3_* (10) | differs | each lateral | `run:ER` | 0.00885 – 0.217 |
| PB-pow-S1_001 | differs | `S1_001` | `run:ER` | 0.182 |
| PB-pow-S4B_s45_01 | differs | `S4B_s45_01` | `run:S1_001` | 0.0198 |
| PB-pow-pu_PA_s43, pu_PA_b01 | differs | `pu_PA_s43`, `pu_PA_b01` | `run:pu_PA_s42` | 0.0127 – 0.216 |
| PB-pow-pu_PB_s42 | differs | `pu_PB_s42` | `run:pu_CTRL_s42` | 0.253 |

That is 23 `le`, 380 `stream` and 186 `differs` checks.

**What the core establishes:**
- **The adopted central unfold, `ER`, repeats itself** to 9.2e-12. It matches RE-1's D2 to 7.5e-12 and J0's
  refined CV to 9.2e-12, and its efficiency is bit-identical.
- **Part B reproduces J0** for every class it shares: replicas, universes, the lateral and the periods. All agree to
  ≤ 5.5e-11. The largest, `U_MaRES_0`, is still 180× below the tolerance.
- **The null universe moves nothing:** `U_NormDISCC_0` and `_1` against `ER`.
- **Every power check moves hXSec2D** by at least 8.9e-3. That covers every universe band but the null and
  EtaNCEL (RE2-DECLARATION-B.md §5.1), every lateral, a replica, a seed change and the periods. It is about 10^9 times
  the repeat noise of 9.2e-12.
- **Every refined replica's background stream** matches its reference.

### 4.2 J7, the gated diagnostic (`k1_j7.json`): 7 checks, PASS

| check | kind | test | reference | max rel. diff. |
|---|---|---|---|---|
| PB-panel-2p2h_0 | le | `S4U_2p2h0_s42` | `run:U_2p2h_0` | 3.32e-12 |
| PB-panel-Flux_23 | le | `S4U_Flux23_s42` | `run:U_Flux_23` | 6.69e-13 |
| PB-panel-MaCCQE_0 | le | `S4U_MaCCQE0_s42` | `run:U_MaCCQE_0` | 5.08e-12 |
| PB-panel-MaRES_0 | le | `S4U_MaRES0_s42` | `run:U_MaRES_0` | 5.47e-11 |
| PB-panel-MinosEfficiency_0 | le | `S4U_MinosEfficiency0_s42` | `run:U_MinosEfficiency_0` | 3.52e-12 |
| PB-panel-NormDISCC_0 | le | `S4U_NormDISCC0_s42` | `run:U_NormDISCC_0` | 1.8e-12 |
| PB-pow-S4CV | differs | `S4CV_s45` | `run:ER` | 0.0142 |

The seed-42 panel runs reproduce the core's universes (≤ 5.5e-11), and a changed seed moves the central unfold by
1.4e-2.

### 4.3 Refinement health and argv

- **Every run** used `--bkg-mode negweight-refined` with 400 trees and 31 leaves, and recorded `random_state` equal
  to its estimator seed + 3 (B10). `re2_k1.py` checks that per row.
- **The core's 605 rows:** `random_state` 45 for 522 rows, 46 for the three seed-43 period runs (`pu_PA_s43`, `pu_PB_s43`, `pu_PC_s43`), and 48, 51, 54 and
  57 for 20 rows each.
  - The clipped fraction is at most 3.4e-4; the allowed maximum is 0.01.
  - Refined/signed lies in [0.9999983, 1.0000151]; the allowed band is [0.99, 1.01].
- **J7's 39 rows:** `random_state` 45 for 7 rows, and 48, 51, 54 and 57 for 8 each.
  - The clipped fraction is at most 9.4e-5.
  - Refined/signed lies in [0.9999996, 0.9999998].
- **The argv check:** each run's recorded `runConfig` holds every option of its `partb_runs.tsv` argv, in 605 of
  605 core rows and 39 of 39 J7 rows.

## 5. The B9 cleanup

B9's conditions were met at 12:43Z:
- J3's rows in the core readout pass: health 10 of 10, argv 10 of 10, its 11 checks (PB-J0-S3_BeamAngleX0 and the
  10 PB-pow-S3_*), and the digests (644 listed, none mismatched).
- Every job that reads the staged CV (J1, J4, J6, J7) has been read out, with core PASS and J7 PASS.

**What the lane did:**
- Before deleting each of the 11 staged files, the lane checked its `stat -c '%s %Y %i'` against
  `preflight/inputs.stat`. All 11 matched, so each deleted file held the bytes hashed on the DTN.
- It then deleted the files and the two empty directories.
- `deletions.tsv` has one row per file: UTC time, path, sha256, size, mtime, inode, stat match and the condition
  met.
- The CFS originals and the universe omnifile were not touched.

**The quota:** 17.47 TiB (87.3 %) before, 17.08 TiB (85.4 %) after.

| deleted file (under `partb/inputs/`) | sha256 |
|---|---|
| `runEventLoopOmniFold_MEFHC.root` (the CV) | `43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df` |
| `laterals/…_BeamAngleX_0.root` | `38b9fc307eabd864cd0fd663679b51fb2e6d064672410af6b3cf8b0a7e161ed5` |
| `laterals/…_BeamAngleX_1.root` | `0e0491a624c2d64c6fa3fde271940f0cfa9acb2d08b72cdf1e21e1c15903c3f2` |
| `laterals/…_BeamAngleY_0.root` | `058746fdb29aa2cc0e3db82e7be42648cd7ce43b8603e96e444111546949ecf6` |
| `laterals/…_BeamAngleY_1.root` | `3bca6a458336c7b4b2250ccbcdc8ca0ac26d416ac4604114f5dfffe0fece2b0e` |
| `laterals/…_MuonResolution_0.root` | `839ab9c51bdc69b13e340d5fdc8fd21968bfcc7a62deeb3db529d5f2fc4a6d5d` |
| `laterals/…_MuonResolution_1.root` | `3330800629d536a94d37d91941089620ca90af228c64f43b4ed633a97550644f` |
| `laterals/…_Muon_Energy_MINERvA_0.root` | `533037d27e0b5e38d778c935b7a44f5e30e0a1afb81870c8b063303859986bfe` |
| `laterals/…_Muon_Energy_MINERvA_1.root` | `90a1d7b78d6deed51499e11ae735f09438dbf3d85c4a463c18fae441b6668ab2` |
| `laterals/…_Muon_Energy_MINOS_0.root` | `f105f68193cc80d125fe272588d3223e9df57cd2e9f720e0853dbd712f52a87a` |
| `laterals/…_Muon_Energy_MINOS_1.root` | `f2e67fd6c986f0a7d45eb894c1640c7d8fb48af83dbce37122d6946ae4aedfa0` |

## 6. What remains, for part C

- **Part C** is to be bound by the director before any post-processing. Its scope includes:
  - the rollup;
  - C_PL;
  - the combination;
  - the Fig. 1 copies under the replaced-identity table (`run/partb_identities.tsv`, RE2-DECLARATION-B.md §6);
  - RO-FPS (RE2-DECLARATION-B.md §7.4), printed either way;
  - the HPSS copies of the final products by the procedure in RE2-DECLARATION-B.md §8.
- **The products** stay on pscratch at `partb/out/` (44 MB) until then. The purge risk (RE2-DECLARATION.md §8) argues
  for binding part C promptly.
- **Room left in the grant:** 36.8162 node-h.
