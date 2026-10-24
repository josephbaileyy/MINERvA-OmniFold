# RE-2 declaration, part B: the production runs, their checks, and the items deferred from part A

**Declared by** the re-1 lane for the director, 2026-10-24.
- It follows part A ([`RE2-DECLARATION.md`](RE2-DECLARATION.md), bound by [`RE2-BINDING-J0.md`](RE2-BINDING-J0.md)) and
  J0's report ([`RE2-J0-REPORT.md`](RE2-J0-REPORT.md), PR #295).
- The director confirmed part B's scope on 2026-10-24: J1–J4, J6, J8 plus J7, within the 90 node-h grant
  (room 84.5245), J5 out. That confirmation also set items (1)–(5) below.

**No production job has run.** This takes effect only when the director commits a BINDING record.

**CITABLE FOR:**
- the 644 production runs, their argv, and their packing into 12 jobs, with limits;
- each job's projected charge, and the cap that bounds it;
- the charge gate, the DTN preflight and the CFS stat check;
- the production readout: 596 checks and 644 health rows;
- the post-processing identity table;
- the inventory;
- the R7, RO-FPS and C2ST findings;
- the HPSS procedure.

**NOT CITABLE FOR:**
- any refined number, since none exists yet;
- an adoption, a coverage statement or a claim, which are Joseph's;
- the post-processing code (part C, §6).

**In brief:**
- **The runs:** 644 refined runs in 12 one-node regular jobs.
- **Charge:**

  | | projected | caps sum to |
  |---|---|---|
  | core | 57.51 node-h | 72.00 |
  | core plus J7 | 63.75 node-h | **79.80** |

  - Each cap is the job's limit on one exclusive node, so 79.80 is the most part B can be charged.
  - It is inside room, 84.5245, so a gate on caps passes for every job, J7 included.
- **The director's packing formula disagrees** (§3.2, decision B1). Step node-h ÷ J0's packing fraction × 1.25 puts
  the core at 89.0, over room.
  - J0's fractions were not lost inside lanes. Every J0 lane was ≥ 99.97 % busy.
  - The loss came from J0a's 5,057 s preflight and its lanes ending 1.25 h apart. Part B's layout removes both.
- **Two plan dependencies were wrong** (§7):
  - the C2ST is a 3D configuration-(a) diagnostic that never reads `E_U`;
  - the "1–2 %" normalization sentence compares 4D with 3D and 5D with 4D, never with 2D.
  
  So J1 writes no step weights, and both items are unchanged by RE-2.
- **A defect in part A's readout,** fixed here (§2.1):
  - `re2_k1.py` required `random_state == 45` literally;
  - every correct run at seeds 43, 45, 48, 51 or 54 would have failed it;
  - the rule is now the run's seed + 3, and a test covers it in both directions.

---

## 1. What changes from part A and the plan

| item | before | part B | reason |
|---|---|---|---|
| inputs on CFS | J0a hashed the 53.8 GB lateral inside the job: 5,057 s, deviation D1 | **hashed once on a DTN**, with no charge (§4). The universe omnifile gets the same treatment, which is its full hash before J2 (part A §3) | CFS reads 1.3–1.5 GB/s on login12 and dtn01, but 5.7–12 MB/s through DVS on a compute node (`RE2-J0-REPORT.md` D1). 2 GiB `dd` reads gave 1.3 GB/s on login12 and 1.5 GB/s on dtn01 (2026-10-24) |
| the stat check | the director's ruling (b), for the BeamAngleX_0 lateral | **the same rule for every DTN-hashed input** (CV omnifile, 10 laterals, universe omnifile) | ruling (b) generalized: `stat -c '%s %Y %i'`. A mismatch forces a full re-hash, and a hash mismatch refuses. The device number is excluded: it is 124 on login12, 105 on compute nodes and 53 on dtn01 for the same file |
| J1 | `E_R` with C2ST step weights (RE2-PLAN §4.2) | **`ER`, `C0_cv` (the same unfold again), `C0_unit`**; no step weights | the C2ST does not read `E_U` (§7.3) |
| charge projection | step node-h × 1.25 (`re2_units.py`) | **each job's own layout**: preflight + longest lane. Bounded by its cap (§3.2) | J0 lane utilization ≥ 0.9997 (§3.2) |
| charge gate | the director's form: before J7, ledgered + J7's projection ≤ room | **before every job**: charged so far + every unfinished job's cap + this job's cap ≤ room. The director's form is also printed (§3.3) | a cap bounds the charge; a projection does not |
| health rule | `random_state == 45` | `random_state == seed + 3` (`re2_driver.py:2182`) | part B runs at seeds 42, 43, 45, 48, 51 and 54 |
| post-processing | "new code under review" (RE2-PLAN §3) | **its identity table is declared now (§6); its code is part C**, bound before any post-processing run | production need not wait on it. The pscratch purge risk argues for prompt production (part A §8) |

## 2. Code

The commit is the one this declaration lands in on `re2/declaration-b-20261024`. The BINDING names its sha. The jobs
run from a fresh clone detached at it, as J0 did. Part A's files are unchanged except `re2_k1.py`.

| file | role |
|---|---|
| `2d-unfolding/re2/re2_driver.py` (unchanged from part A, `38ff3705…`) | the RE-2 driver |
| `2d-unfolding/re2/re2_k1.py` (changed, §2.1) | the readout: part A's checks and part B's |
| `2d-unfolding/re2/re2_partb_layout.py` | writes `partb_runs.tsv`, `partb_jobs.tsv` and `partb_checks.tsv` from pinned sources |
| `2d-unfolding/re2/re2b_gate.py` | the charge gate |
| `2d-unfolding/re2/re2_inventory.py` | writes `inventory.tsv` (§7.1) |
| `2d-unfolding/re2/tests/test_re2b.py` | 19 tests (§2.2) |
| `2d-unfolding/re2/tests/test_re2_readouts.py` (one test added) | 11 tests |
| `run/partb_runs.tsv`, `run/partb_jobs.tsv`, `run/partb_checks.tsv` | the 644 runs, the 12 jobs, the 596 checks |
| `run/partb_identities.tsv` | the post-processing identity table (§6) |
| `inventory.tsv` | the dependency inventory (§7.1) |
| `run/launch/re2b_env.sh` | part B's settings; sources part A's `re2_env.sh` unchanged |
| `run/launch/re2b_dtn_hash.sh` | the DTN preflight |
| `run/launch/re2b_job.sbatch` | the job |
| `run/launch/re2b_submit.sh` | gate, then submit; each submission logged |
| `run/launch/test_stat_check.sh`, `run/launch/test_lane_stdin_b.sh` | the launcher tests (§2.2) |

The sha256 of each file is in §12. The production driver is part A's: the copy and its diff are unchanged.

### 2.1 What changed in `re2_k1.py`

- **Health:** `random_state` must equal the run's `--seed` + 3, the driver's own rule (`re2_driver.py:2182-2183`).
  - A run with no `--seed` fails health. Every declared run passes one.
  - At seed 42 this is the old rule's 45.
  - The defect was found by this declaration's identity audit. Under the old rule, every J6 run, J7's runs at seeds
    45–54 and J8's seed-43 runs would have failed health.
- **`--sums-glob`:** the jobs' `SHA256SUMS` files beside `--out-dir`. The default, `SHA256SUMS.J0*`, keeps J0's
  readout as it was. Part B passes `SHA256SUMS.J[1-8]*`.
- **J0's readout is unchanged:** the changed code, run on J0's real outputs on 2026-10-24, gave checks, health and
  sums identical to the committed `k1.json`. Only `code_sha256` differs.

### 2.2 Tests

- **`test_re2b.py`, 19/19 locally** (python3.13 with PyROOT; 17 pass and 2 skip without ROOT).
  - **Layout:**
    - the committed tables are byte-equal to the generator's output;
    - the counts per class;
    - every run is refined 400/31;
    - every part-B run that repeats a J0 run's purpose has that run's argv, option by option, with the same CPUs
      (`U_MaCCQE_0` and F_MaCCQE0, `S1_001` and RB_001, `S3_BeamAngleX0` and FL_BAX0, `C0_cv` and D_cv,
      `pu_PA_b01` and RPR_PA_b01; 17 pairs);
    - `ER` equals `C0_cv`;
    - each S4(ii) seed-42 run equals its J2 universe;
    - the 175 universes are exactly the rollup's;
    - every limit is under 12 h and ≥ 1.25 × its wall time;
    - the caps sum within room.
  - **Checks:**
    - every replica has a stream check;
    - every universe has a power check, except the two null bands (NormDISCC) and the two weak ones (EtaNCEL);
    - every external reference carries a digest.
  - **`re2_k1.py` over the declared part-B tables**, with a synthetic output for each of the 644 runs:
    - the verdict can be PASS, with 644 health rows and 644 listed sums;
    - a seed-48 run that records `random_state` 45, a universe that does not move, and a wrong stream sum on
      `S1_150` each fail exactly their own row.
  - **Gate:**
    - it passes when the caps fit and refuses when one would cross room;
    - a running job reserves its cap, and an ended or cancelled job counts its charge;
    - a job missing from `sacct` counts its cap;
    - a job already submitted is refused;
    - a ledger without the two J0 rows is refused.
- **`test_re2_readouts.py`, 11/11 locally,** including the new seed + 3 test in both directions.
- **`test_stat_check.sh`, 8/8 on Perlmutter**, GNU stat (§4.2). Two mutants were each caught: "never re-hash"
  failed 4 cases, and "drop the inode" failed 2.
- **`test_lane_stdin_b.sh` on Perlmutter:**
  - `re2b_job.sbatch`'s `lane()`, with a stub `srun` that reads all its stdin, makes **644 of 644 calls**, each with
    its own label, CPUs and `--out`.
  - With the table read from stdin instead of fd 3, it makes 35 of 644.

## 3. Production

### 3.1 The runs (`run/partb_runs.tsv`)

**Common argv.** Every run passes `--bkg-mode negweight-refined --refine-n-estimators 400 --refine-num-leaves 31`
in place of purity. Otherwise each repeats the argv of the purity product it replaces.

**Names.** Labels are Stage C's member names without `2dc_P_`, the period test's names, and `U_<band>_<index>`, so
the post-processing copies change only the directory they read.

| job | runs | what | argv, as | CPUs |
|---|---|---|---|---|
| J1 | 3 | `ER` (the future `E_R`), `C0_cv` (the same unfold again: Stage C's C0 row and the S4(ii) seed-42 CV), `C0_unit` | J0's `D_cv`, `D_unit` | 64 |
| J2a–d | 175 | the July universes: `sweeps.json` "pn/" (pinned `15b57de9…`) less CV, the 10 laterals and the 2 Rvp1pi. That leaves 38 bands, including Flux's 100 | J0's `F_*` (K1-U4–U6 reproduced the July files with it) | 128 |
| J3 | 10 | the 10 active laterals | Stage C S3, as J0's `FL_BAX0` | 128 |
| J4a–c | 300 | S1: bootstrap seeds 1–300, three streams, seed 42 | J0's `RB_*` | 64 |
| J6 | 80 | S4(i): seeds 45, 48, 51, 54 × bootstrap seeds 1–20 | Stage C `2dc_P_S4B_*` | 64 |
| J7 | 39 | S4(ii): 7 panel universes × seeds 42, 45, 48, 51, 54 (128 CPUs), and the CV at 45, 48, 51, 54 (64 CPUs) | Stage C `2dc_P_S4U_*`, `2dc_P_S4CV_*` | 128 / 64 |
| J8 | 37 | the period test's rows (its `jobs.tsv`, pinned `c2283eb3…`): control, P_A/P_B/P_C at seeds 42 and 43, 10 replicas each | J0's `RF_PA`, `RPR_PA_b01` | 64 |

**Seeds:**
- estimator `random_state` seed, seed + 1 and seed + 2;
- refinement seed + 3, so 45, 46, 48, 51, 54 and 57;
- the bootstrap seeds of Stage C and the period test, replica for replica.

No other seed is used.

**Kept, though it could be saved.** J7's seven seed-42 universe runs repeat argv that J2 also runs. They are kept as
cross-job repeats (§5.1), at about 1.1 node-h.

### 3.2 Packing, projection and limits (`run/partb_jobs.tsv`)

**The evidence.** Every J0 lane was busy for at least 99.97 % of its span: the sum of its steps' `ElapsedRaw`
against its first start and last end.

| lane | runs | span, s | busy, s |
|---|---|---|---|
| a1 | 9 | 9,479 | 9,476 |
| a2 | 3 | 4,998 | 4,998 |
| b1 | 5 | 4,232 | 4,231 |
| b2 | 5 | 4,230 | 4,229 |
| b3 | 6 | 3,949 | 3,948 |
| b4 | 6 | 4,664 | 4,663 |

So J0's packing fractions (0.825, and 0.763 after the preflight) come from two things, not from the lanes:
- the preflight: 508 s for J0b and 5,057 s for J0a;
- the lanes' unequal ends: J0a's a2 ended 1.25 h before a1.

**The rule.** A job's wall time is its preflight (300 s declared; §4) plus its longest lane. An exclusive node is
charged for that time.

**Run times** are J0's class maxima (`units.json`):

| class | time |
|---|---|
| central | 866 s |
| universe | 1,150 s |
| lateral | 1,678 s |
| replica | 920 s |
| period | 588 s |
| period control | 891 s |

The period control was run by J0 only in the purity arm, so its time is the purity control's 801 s × the PA central's
refined/purity ratio of 588/529.

**Packing.** Runs are placed longest first, each on the least-loaded lane: two 128-CPU lanes or four 64-CPU lanes per
node.

**Limit:** 1.25 × wall time, rounded up to a minute, and under 12 h.

| job | lanes × CPUs | runs | wall, s | limit | projected node-h | cap node-h | J0-fraction formula, node-h |
|---|---|---|---|---|---|---|---|
| J1 | 4 × 64 | 3 | 1,166 | 0:25 | 0.32 | 0.42 | 0.22 |
| J2a, J2b, J2c | 2 × 128 | 44 each | 25,600 | 8:54 | 7.11 each | 8.90 each | 9.21 each |
| J2d | 2 × 128 | 43 | 25,600 | 8:54 | 7.11 | 8.90 | 9.00 |
| J3 | 2 × 128 | 10 | 8,690 | 3:02 | 2.41 | 3.03 | 3.05 |
| J4a, J4b, J4c | 4 × 64 | 100 each | 23,300 | 8:06 | 6.47 each | 8.10 each | 7.74 each |
| J6 | 4 × 64 | 80 | 18,700 | 6:30 | 5.19 | 6.50 | 6.20 |
| J8 | 4 × 64 | 37 | 6,180 | 2:09 | 1.72 | 2.15 | 1.86 |
| **core** | | 605 | | | **57.51** | **72.00** | 71.19 (× 1.25 = **88.99**) |
| J7 (gated) | 2 × 128 | 39 | 22,448 | 7:48 | 6.24 | 7.80 | 7.64 |
| **total** | | 644 | | | **63.75** | **79.80** | 78.83 (× 1.25 = 98.54) |

**The director's formula,** step node-h ÷ J0's packing fraction × 1.25, gives a core worst case of 88.99, over room.
It also predicts each J2 job at 9.21 node-h, more than that job's own 8.90-hour limit, so it is not consistent with
a balanced layout.
- **The bound that holds:** the cap sum, 79.80 with J7, because no exclusive job is charged past its limit.
- **The scheduler's kill delay** after a limit is seconds per job, and is not priced.
- **Decision B1** (§11).

**What each job does not cover:**
- **Within-class variation above J0's maximum.** J0 measured 1–10 runs per class. A slow node slows every lane of
  its job, and 1.25 × the wall time covers a node about 25 % slower.
- **The period-test nodes** whose replicas timed out (nid004074, nid004078) are excluded, as RE2-PLAN §4.2 said.

### 3.3 The charge gate (`re2b_gate.py`, `re2b_submit.sh`)

**The rule.** Before each job is submitted, all of the following must hold, or the job is refused:

charge of every ended part-B job (`sacct`) + the cap of every unfinished one + this job's cap ≤ room = 90 − J0's
5.4755.

A job already submitted is refused. Each submission is logged before the next job is gated.

**For J7** the director's form is also printed (ledgered + J7's projection ≤ room). The cap form implies it.

**Measured on 2026-10-24** with no part-B job submitted: all 12 jobs pass in order. The caps reach 72.00 after the
core and 79.80 after J7.

**A resubmission is not covered.** Allowing one needs the director (§10). The gate would then count the failed job's
charge and the new cap.

## 4. Inputs and the preflight

### 4.1 The DTN preflight (`re2b_dtn_hash.sh`)

**Where it runs:** once, on dtn01, after the BINDING and before any submission. There is no Slurm charge.

**What it checks:**
- The deploy must be a clean checkout at the bound sha.
- `$ACT/SHA256SUMS` must match its pinned digest (`73775251…`).
- That file's BeamAngleX_0 row must equal part A's digest (`38b9fc30…`).

**What it hashes,** 12 files, four at a time:

| input | location | reference digest |
|---|---|---|
| the CV omnifile | CFS, 2.1 GB | `43f8cc16…` |
| the 10 active laterals | CFS, 53.8 GB each | each its `SHA256SUMS` row |
| the universe omnifile | pscratch, 171 GB | `220c479e…`; this is part A §3's full hash before J2 |

**Each file:**
- its stat is taken before and after its hash, and the two must agree;
- its digest must equal the reference;
- it gets one row in `$B/partb/preflight/inputs.stat`: `sha256 size mtime inode path`.

The record is written once, made read-only, and refused if it already exists. Its sha256 is printed and goes in the
part-B report.

**Expected time:** about 0.7 TB at the measured 1.3–1.5 GB/s, about 0.5 GB/s per `sha256sum` process. That is about
10–25 min.

**Recorded so far.** On 2026-10-24 the stats were:

| input | size | mtime | inode |
|---|---|---|---|
| BeamAngleX_0 | 53,845,911,012 | 1784361874 | 759636316 |
| universe omnifile | 171,117,087,867 | 1783523295 | 882725391507234642 |
| CV omnifile | 2,144,008,221 | 1779094334 | 6874571285 |

Login12, both J0 nodes and dtn01 agree on these stats, though not on the device number.

### 4.2 The stat check in each job (`re2b_stat_check`, `re2b_env.sh`)

**For each DTN-hashed input a job reads:**
1. The record must have exactly one row for the path, and its sha256 must be the declared one. Otherwise the job
   exits 5.
2. If `stat -c '%s %Y %i'` equals the recorded size, mtime and inode, there is no re-hash.
3. Otherwise the job re-hashes the file in full. A mismatch refuses, with exit 4.

**What is hashed in the job.** The pscratch inputs not in the record (MC flux, flux universes, the 8 period files,
about 4.3 GB in all, almost all of it J8's period omnifiles) are still hashed in each job that reads them, as in J0.

**Its test (`test_stat_check.sh`, 8/8; mutants caught, §2.2):**

| case | re-hash | outcome |
|---|---|---|
| unchanged stat | no | pass |
| touched mtime | yes | pass (same bytes) |
| changed size, mtime restored | yes | refused |
| changed inode, same bytes | yes | pass |
| changed inode and bytes, same size and mtime | yes | refused |
| record sha not the declared one | no | refused |
| two record rows | no | refused |
| no record row | no | refused |

### 4.3 Which job reads what (`re2b_check_inputs`)

| job | inputs checked |
|---|---|
| J1, J4, J6 | the CV omnifile |
| J2 | the universe omnifile and the flux universes |
| J7 | the universe omnifile, the flux universes and the CV |
| J3 | `$ACT/SHA256SUMS` and the 10 laterals |
| J8 | the 8 period files |

Every job also checks the MC flux file.

## 5. The production readout

The readout runs on a login node after every job has ended. It is `re2_k1.py` with:
- `--runs partb_runs.tsv` and `--checks partb_checks.tsv`;
- `--out-dir $B/partb/out` and `--sums-glob 'SHA256SUMS.J[1-8]*'`;
- `E_U` for the 205 cells.

Then `re2_ledger.sh` over every part-B job. A part-B readout script lands with part C (§6).

### 5.1 Checks (`run/partb_checks.tsv`, 596)

**Pass rule.** Part A's rule:
- equality at ≤ 1e-8 on `E_U`'s 205 cells, with the same reported cell set for `hXSec2D`;
- references re-hashed against their digests;
- power above the row's `min_shift`;
- stream checks to 1e-9.

| ids | n | test → reference | what it shows |
|---|---|---|---|
| PB-ER-rep, PB-ER-D2, PB-ER-J0 | 3 | `ER` → `C0_cv`; RE-1 D2 `71ca3e5f…`; J0 `D_cv` | the adopted product repeats, and equals the refined unfold RE-1 and J0 made. The cell-set test is plan §5.3's structural requirement that `E_R` report `E_U`'s 205 cells |
| PB-ER-eff | 1 | `ER` → J0 purity `C_cv`, `hEff2D` | the efficiency the heat-map figure reads does not depend on the background treatment (CHK-eff) |
| PB-unit, PB-unit-J0 | 2 | `C0_unit` → `C0_cv`; J0 `D_unit` | the bootstrap with factors 1 is the CV |
| PB-null-NormDISCC_0, _1 | 2 | `U_NormDISCC_*` → `ER` | the null band. In the July purity sweep both are within 1.5e-11 of the CV (measured 2026-10-24) |
| PB-J0-* | 15 | 4 universes, `S3_BeamAngleX0`, `pu_PA_s42`, `pu_PA_b01`, `S1_001`–`008` → their J0 runs | the same argv in J0 and part B, run to run |
| PB-panel-* | 6 | `S4U_<u>_s42` → `U_<u>` | the S4(ii) seed-42 universes equal J2's: the refined form of `analyze_prod.py`'s July identity (AP-15) |
| PB-stream-* | 380 | every `S1_*` and `S4B_*` → Stage C's purity replica with the same seeds (digests from `stageC/production/evidence/production/SHA256SUMS.pscratch`, pinned) | **on the data**, each replica's refined background stream: signed sum = data-factor sum − the purity replica's resampled background (STREAM-1, for all 380) |
| PB-pow-U_* | 171 | every universe except NormDISCC and EtaNCEL → `ER`, > 1e-4 | each universe moves the result. In the July sweep every one moved ≥ 1.08e-2 |
| PB-pow-S3_* | 10 | every lateral → `ER`, > 1e-6 | each lateral moves it |
| PB-pow-* | 6 | `S1_001` → `ER`; `S4B_s45_01` → `S1_001`; `S4CV_s45` → `ER`; `pu_PA_b01` → `pu_PA_s42`; `pu_PA_s43` → `pu_PA_s42`; `pu_PB_s42` → `pu_CTRL_s42` | a replica, the seed, a period replica, a period seed and a period each move it |

**Health:** all 644 rows. Each needs:
- clipped fraction ≤ 0.01;
- refined/signed in [0.99, 1.01];
- `random_state` = seed + 3;
- 400 trees and 31 leaves.

**Not checked, and why:**
- **EtaNCEL_0 and EtaNCEL_1** move the purity result by 3.0e-7. That is below a power floor and above the null
  tolerance, so they get neither check, only health and provenance.
- **Nine laterals have no refined reference:** all but BeamAngleX_0, including Muon_Energy_MINOS_0. That universe is
  also an S4(ii) panel universe with no J2 counterpart. They get health, power and provenance only. J0's CHK-det2
  showed a lateral repeats to 6.4e-13.
- **S4(i)'s 80 replicas have no numerical identity** (the identity audit's finding, as in Stage C). Each gets a
  stream check and health, and one of them (`S4B_s45_01`) a power check.

### 5.2 Verdict

Production is **COMPLETE** when all of the following hold:
- every check and every health row passes;
- every output matches its job's `SHA256SUMS`;
- every step COMPLETED.

Otherwise the report names what failed, and nothing downstream runs on a failed product.

## 6. Post-processing: the identity table now, the code in part C

**What part C covers.** It is the copies of:
- `analyze_prod.py` and `s5_rollup.py`;
- the period analysis (`periods.py`, `analyze_periods.py`) and `export_cov.py`;
- `playlist_term.py` and `combine_s5.py`;
- `build_q_products.py` with `run_rebuild.sh`;
- the Fig. 1 reducer (P13).

Each copy changes only:
- its pins;
- an input-mode guard;
- the identities `partb_identities.tsv` marks for replacement, each by the replacement named there.

**`run/partb_identities.tsv`.** It has 173 rows, one per check in those producers, read at `5b8b9765`. Each row is
classified:

| class | rows | meaning |
|---|---|---|
| K | 95 | keep as it is |
| R | 49 | repin to the refined product |
| X | 16 | replace, because it is an identity against a purity reference |
| G | 13 | a new mode guard, or the driver record it reads |

An independent agent wrote the table. The lane spot-checked five of its line claims against the code at
`5b8b9765`, and all five hold.

**The 16 replacements:**

| ids | where | replaced by |
|---|---|---|
| AP-09, AP-10 | `analyze_prod.py:146-147`, C0 against XR-L0 | PB-unit; PB-ER-D2 and PB-ER-J0 |
| AP-13 | `analyze_prod.py:196-200`, S3 against the pilot laterals | PB-J0-S3_BeamAngleX0. The other nine have none (§5.1) |
| AP-15 | `analyze_prod.py:222-225`, the July identity at seed 42 | PB-panel-* (so J7's readout needs J2) |
| AP-18 | `analyze_prod.py:265-274`, the pilot replicas | PB-J0-S1_001–008, and PB-stream-* for all 380 |
| AP-05, AP-06 | `analyze_prod.py:99-119`, the pilot and July digest loaders | the J0 and part-B `SHA256SUMS` |
| S5-09, S5-10 | `s5_rollup.py:369-370`, the July universe block (44 bands, 187 universes) | a committed J2 manifest, every file digest-checked and mode-guarded: 38 bands, 175 universes. `build_q_products.py:591` reads the check by name and is changed with it |
| S5-22 | `s5_rollup.py:349-350,386`, the S2 gate and the `bkg_separable` term | dropped in the refined arm (J5 is not bound). Kept in the purity K1-roll run, so that it still reproduces `6689d2fc…` |
| PD-04, PA-05b | `periods.py:53-54`, `analyze_periods.py:324-336`, the control against XR-L0 | the refined control against J0's `D_cv` and D2 |
| EX-04, BQ-22, BQ-24 | `export_cov.py:90-93`, `build_q_products.py:370-437`, controls that reproduce VL175's numbers relative to `E_U` | run with a separately pinned `E_U` as the control denominator only. EX-04 is made to stop, which it does not today |
| CB-18 | `combine_s5.py:29-33,153-168`, four hard-coded χ² values from the purity `playlist_term.json` | the values read from the pinned refined `re2_playlist_term.json` |

**K1-roll** (RE2-PLAN §5.1) is unchanged. Each copy first runs on the purity inputs and must reproduce:
- `production_cov.npz` `6689d2fc…`;
- `playlist_term.npz` `c1723cb5…`;
- `s5_plus_playlist.npz` `8ccb4d72…`.

Only then does it run on refined inputs.

**What the audit found for part C to fix:**
- **Gates that don't check inputs.**
  - `s5_rollup.py`'s analysis gate (`:347-355`) reads only each item's verdict and `out_root`. It records input
    digests but never compares them.
  - `playlist_term.py:117-121` and `combine_s5.py`'s check 2 compare two copies of a central value, but not which
    value it is.
- **A rollup that changed only its output path would mix arms.** It would read the 38 July purity bands beside
  refined laterals, stat and C08, and no check would fire (S5-09).
- **The only mode check today** is `analyze_prod.py:61,81`, and on a mismatch it gives INCONCLUSIVE.
- **Every consumer needs the new guard.** The driver records `runConfig`, holding `bkg_mode` and `refine_*`, on
  every path (`re2_driver.py:1403-1410`). It writes `re2Refinement` only on the refined path (`:2218-2220`). Stage C's
  purity products lack the `refine_*` keys, so the purity guard accepts absent or null.
- **Checks that record but don't stop:** `analyze_periods.py`'s control (`:336-339`) and `export_cov.py`'s controls.

**Decision B4** (§11).

## 7. The deferred items of part A §1

### 7.1 The inventory (`inventory.tsv`, by `re2_inventory.py`)

**How it was made:**
- It reads the git-tracked files under `docs/analysis-note/` and records the HEAD it read (`5b8b9765`).
- It writes one row per use of each RE2-PLAN §2.2 macro and each §2.3 figure (with the `\ref`s of their labels).
- It adds the PHASE2-INVENTORY literal-number search for `E_U`'s and Q's printed numbers at several precisions, and
  keywords.
- Each row gives its action, its build targets and whether it sits in a comment.
- It fails closed if a listed macro is not defined exactly once, or a listed figure is never included.

**At `5b8b9765`:**

| kind | rows | names | in a built file, outside a comment |
|---|---|---|---|
| macro | 226 | 73 | 183 |
| figure | 84 | 36 | 61 |
| literal | 417 | 59 | 238 |
| **total** | **727** | | |

- **The build set:** five targets (`build_all.sh`: `main_note`, `main_primer`, `main_paper`, `pet_note`,
  `main_records`), and every tracked `.tex` is in one of them.
- **Four patterns have no hit,** and one macro (`\covTwoDRepCTwo`) is never used.
- **RE2-PLAN §2.4's `sec_3d.tex` numbers are stale.** The RE-1 integration replaced +0.95 %, 1.0016 and 4.4 % with
  0.001 %, 1.0000 and about 3.5 %. The inventory greps both.

A literal hit is a site to read, not a finding. The integration step reads every one.

### 7.2 R7: "marginal normalizations agree at about 1–2 %"

**Where it is printed now:** `paper_body.tex:95` (Table I) and `:470-472`, `main_note.tex:75-77`,
`sec_execsummary.tex:44`, `sec_summary.tex:31-33` and `primer_body.tex:373`.

**Its producers:** two configuration-(a) checks. Neither reads `E_U` or any 2D product.

| producer | compares | recorded values |
|---|---|---|
| `nd-unfolding/check_4d_anchors.py` | 4D with 3D | medians 0.38 / 0.64 / 1.68 %, ratio 0.9960 (`VALIDATION_LEDGER.md:1822-1824`, `:1763-1764`) |
| `nd-unfolding/check_5d_anchors.py` | 5D with 4D | 5D/4D 1.0011, medians 0.3–1.5 % (`VALIDATION_LEDGER.md:1764`, `sec_eavailw.tex:49-52`) |

`CLAIM-TABLE-20261008.tsv:29` (V15) maps the sentence to these outputs as an envelope.

**Result: unchanged by RE-2.** Only `sec_3d.tex`'s 3D-against-2D clause (0.001 %) is re-evaluated against `E_R`, by
RE-1's `re1_f_numbers.py` route.

### 7.3 The C2ST (RE2-PLAN §2.2 "Other dependents", and J1)

**Its producer** is `nd-unfolding/unbinned_gof.py` (launcher `sbatch_unbinned_gof.sh`, deleted in `b017cfe6`; still
listed at `nd-unfolding/MANIFEST.md:60`).

**What it reads:**
- the **3D** (pT, p∥, E_avail) inputs `of_inputs_3d.npz`;
- the configuration-(a) OmniFold weights it computes itself (`:132-136`), or loads (`:125-127`).

The 0.535 → 0.501 is at `docs/STATVAL_REPAIR.md:113,131`.

**Result: it does not read `E_U`,** so RE2-PLAN's dependency was wrong.
- J1 writes no step weights.
- The C2ST stays a configuration-(a) 3D diagnostic, unchanged.
- A refined 2D C2ST would be a new test, not a re-evaluation, and is not in RE-2 (§9).

### 7.4 RO-FPS (part A §6)

**The reference:** "Control unfold total 3.073e-38 = the frozen production 2D number exactly"
(`VALIDATION_LEDGER.md:1614-1615`, job 54244120, 2026-06-10).
- It was made by step [5] of `nd-unfolding/sbatch_fps_mefhc.sh:64-67`: the ND driver with `--axes ""`, seed 1,
  purity.
- It is printed to 4 significant figures (`.4g`, `unfold_nd_omnifold_unbinned.py:1095`), the precision of
  `\sigTwoD`.
- No log or digest of its output is committed, so the ledger line is the reference.

**The readout,** when `E_R` lands: `E_R`'s total on its reported cells, to 4 significant figures, against 3.073e-38.
The result is printed either way: "reproduces", or the two values and their difference.

On RE-1's D2 (−0.139 %, about 3.069e-38) the outcome is expected to be a difference. The rule does not depend on that
expectation.

### 7.5 The replaced-identity list

§6.

## 8. Storage and HPSS (R9)

**On pscratch:**
- **Part B's products** go to `$B/partb/` (`out/<label>/xsec.root`, `logs/`, `inventory/`, `preflight/`,
  `SHA256SUMS.<job>`, `submissions.log`): about 46 MB of outputs, at J0's about 72 KB each, plus logs.
- **Nothing is written** under a checkout, to CFS, or over a purity product.
- **Pscratch** reads 68 % (`df`, 2026-10-24).

**On HPSS.** The final products (`E_R`, `Q_R`, the S5 and C_PL products, the combination, the receipts; part A §8:
about 35 MB) are copied to HPSS after part C. The procedure, fixed now, follows the lane's HPSS record (an archive was
once found empty while its markers said verified):
1. **Bundle and manifest.** The products go into one `htar` bundle. Small files are bad on tape, so they are
   bundled. A manifest gives each member's sha256 and md5.
2. **Put and migrate.** `hsi put` the bundle, then `hsi migrate -R`.
3. **Check residency.** `ls -V` must show the bytes **at the tape level**. The `DISK` in the mode line is a
   class-of-service name, not residency.
4. **Verify the digests.** `hsi hashverify -R`, with its exit status captured unpiped. The verified path set must
   equal the manifest's, both non-empty.
5. **Test recovery.** `hsi get` into a fresh, empty directory, re-hash every member against the manifest, and open
   every ROOT file. A `hashverify` pass alone is not a recovery.
6. **Reconcile quota.** `hsi du` of the archive must match the manifest's bytes.

Every step's output is committed with the part-C report. HPSS had 161 GiB free on 2026-10-23.

## 9. Not done in RE-2

Each item below is outside RE-2. A rollup copy, receipt or report that summarizes RE-2 must not imply that RE-2
covers it.
- **A 2D model-dependence component.** The 2d test lane's prior-variation test (`pv2d/`) is measuring a
  model-dependence envelope on the refined 2D estimator. If Joseph adopts a 2D model-dependence component, it is
  built from those products, not RE-2's. `Q_R` does not contain it, and RE-2's rollup copies do not claim to be
  complete without it.
- **A refined C2ST** (§7.3).
- **A refined 5D covariance, and the extended-fiducial value** (R8: 2D only; the extended-fiducial value stays purity,
  labelled).
- **A coverage test of `Q_R`.**
- **A new release candidate.**
- **J5 (S2).** The `bkg_separable` term is not rebuilt.
- **Power for EtaNCEL,** and refined references for nine laterals (§5.1).

## 10. Stops and grant fields

**Stops:**
- **Preflight:**
  - the deploy is not clean at the bound sha;
  - the DTN record is missing or has a row wrong;
  - an input digest fails on its re-hash;
  - the job's QOS or time limit differs from the declared one.
- **A failed run.** Its lane records it and goes on. The readout fails what needs it, and the verdict is not
  COMPLETE.
- **The time limit.** Slurm stops the job (`--no-requeue`), and it is reported. It is never resubmitted without the
  director, and a split of a declared limit is raised first.
- **The gate refuses.**
- **Refinement health fails,** or a check fails. Nothing downstream runs on that product.

**Grant fields (delegation §3.1):**
- **Window:** from the BINDING record to the part-B readout, or 2026-11-30.
- **Charge:** ≤ 84.5245 node-h (room), enforced by the gate. The declared caps sum to 79.80.
- **Attempts:** one submission per job. A failed job is resubmitted at most once, only for a cause outside the
  declared code, and only with the director's approval. The gate then counts both attempts.
- **Terminal outcomes:**
  - COMPLETE;
  - stopped at preflight;
  - stopped at a limit;
  - a named check or health row failed;
  - refused by the gate.

## 11. Decisions for the director before binding

| # | decision | the lane's recommendation |
|---|---|---|
| B1 | how to project charge: each job's own layout (preflight + longest lane; J0 lanes ≥ 99.97 % busy), or step node-h ÷ J0's packing fraction × 1.25 (core 88.99 > room) | the layout, with the cap sum (79.80) as the bound |
| B2 | the gate: cap form before every job, the director's form printed for J7 | accept. Since the caps fit, all 12 jobs may be submitted at once |
| B3 | ruling (b) applied to every DTN-hashed input (CV, the 10 laterals, the universe omnifile); the full universe hash on a DTN | accept |
| B4 | the post-processing identity table now, its code as part C, bound before any post-processing run | accept |
| B5 | the C2ST and "1–2 %" corrections: both unchanged; J1 writes no step weights | accept; a refined C2ST is not done (§9) |
| B6 | J1's repeat (`C0_cv`) and J7's seed-42 repeats are kept | accept (about 1.2 node-h of repeats, inside the caps) |
| B7 | the RO-FPS reference is the ledger line, not a committed file | accept, since no digest exists. The readout prints its source |
| B8 | the stated gaps of §5.1: EtaNCEL, nine laterals, S4(i) | accept, disclosed |

## 12. File digests

Paths under `docs/…/methods/re2/` are given relative to it.

| file | sha256 |
|---|---|
| `2d-unfolding/re2/re2_driver.py` | `38ff37055af026bd11b1c12a431b31eed522d5038c1bcf020cd47c374d2ddf7c` |
| `2d-unfolding/re2/re2_k1.py` | `25da704896e2d450b690850b570009b09db8dd97e64bf13cadb92d6c4f00ed37` |
| `2d-unfolding/re2/re2_partb_layout.py` | `e1562ebc650935eb54e6e63ce10c3c0ee48cdaee30973ba06589137c6e529d88` |
| `2d-unfolding/re2/re2b_gate.py` | `35a47ea8e61dcf9627499838cbd10c9baec35215878304348e0ad60ba7b654eb` |
| `2d-unfolding/re2/re2_inventory.py` | `e686621bcd1331c6167fdefbcf386a1f7c042393d7a41f52e3edc17b61764d39` |
| `2d-unfolding/re2/tests/test_re2b.py` | `e4b067dc8a4a933ab46ef010ee2b05bac3f28d921d1fd9bced71ab9a4f3a7445` |
| `2d-unfolding/re2/tests/test_re2_readouts.py` | `fc7e87b5624b2eed736132a44d1fa206abd5e4501917e4a618a70ae1f2c1e46a` |
| `run/partb_runs.tsv` | `526b70e0cda78ef476f921d817ff264f67f1b8844b241ca4e65083a196a1127b` |
| `run/partb_jobs.tsv` | `8372d10755a7b4687d978fb1bca8ad87b2e01b8566414183fdfddd26ce81c1ed` |
| `run/partb_checks.tsv` | `607187093a921641795214e503264f161222b3e9014c651cdc1d55d15710c9b7` |
| `run/partb_identities.tsv` | `7efe151211b2b89c94ebf2b8112a1611d3ae9a8918b8de42495bbdcc8fb7fd97` |
| `inventory.tsv` | `532deabaf725f42b4fb95b7cf71a45e3437e37af81af0fec50647ca6c9f86672` |
| `run/launch/re2_env.sh` | `cb6c23b2b490e57788ec9e2e8f7fcf942d359c49e27028343905b1d939352a2c` |
| `run/launch/re2b_env.sh` | `5a8c5e14b3796307a853d36dcb3a72077ebd34f9308ad8772cab968302957ac2` |
| `run/launch/re2b_dtn_hash.sh` | `27671cb60f37868e2376a7e68dee5e61bef89a8bdebe54ccde76ce8f0d2c3c8a` |
| `run/launch/re2b_job.sbatch` | `a1cdd1b8d5dbd7f800f3e57535a1f3dce8a3c65e9bf2be3c8cec04bf5450a806` |
| `run/launch/re2b_submit.sh` | `9ac13bb70fef6f15540963e30af071c8b15a12db5f4b6aa2f0c93eb7dc1f8098` |
| `run/launch/test_stat_check.sh` | `daaae51bb4a44e4049a553a364cae09613380b937c27eb6b72e3852ce66f118c` |
| `run/launch/test_lane_stdin_b.sh` | `e5c8d68fdbe50135d152c38a898526f5aa75158394154e4261aa5f15c6d6056a` |
