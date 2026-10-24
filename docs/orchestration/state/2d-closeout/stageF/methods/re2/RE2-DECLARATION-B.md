# RE-2 declaration, part B: the production runs, their checks, and the items deferred from part A

**Declared by** the re-1 lane for the director, 2026-10-24.
- It follows part A ([`RE2-DECLARATION.md`](RE2-DECLARATION.md), bound by [`RE2-BINDING-J0.md`](RE2-BINDING-J0.md)) and
  J0's report ([`RE2-J0-REPORT.md`](RE2-J0-REPORT.md), PR #295).
- The director confirmed part B's scope on 2026-10-24: J1–J4, J6, J8 plus J7, within the 90 node-h grant
  (room 84.5245), J5 out. That confirmation also set items (1)–(5) below.
- The director's preliminary rulings on B1–B8 (2026-10-24) are recorded in §11. They become final in the BINDING.

**No production job has run.** This takes effect only when the director commits a BINDING record.

**CITABLE FOR:**
- the 644 production runs, their argv, and their packing into 12 jobs, with limits;
- each job's projected charge, and the cap that bounds it;
- the charge gate;
- the DTN preflight, with its staging, and the stat check;
- the production readout: 596 checks, 644 health rows, 644 argv rows, and the sums coverage;
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
- **A director correction:** the director withdrew the packing-fraction formula (B1, §3.2). Every J0 lane was
  ≥ 99.97 % busy, so J0's packing losses came from its preflight and from lanes ending unevenly, not from packing
  itself.
- **The CFS inputs** (the CV omnifile and the 10 laterals) are staged to pscratch by a DTN preflight that hashes
  them there (B9, §4).
  - J0's lateral and CV run times were measured right after an in-job hash of the same file on the same node, so
    their reads were probably page-cached.
  - A cold read through a compute node's DVS mount runs at about 10 MB/s, and would make J3 overrun.
- **Two plan dependencies were errors,** found at declaration (§7):
  - the C2ST is a 3D configuration-(a) diagnostic that never reads `E_U`;
  - the "1–2 %" normalization sentence compares 4D with 3D and 5D with 4D, never with 2D.
  
  So J1 writes no step weights, and both items are unchanged by RE-2.
- **A part-A readout defect, fixed before part B** (§2.1):
  - `re2_k1.py` required `random_state == 45` literally;
  - every correct run at a seed other than 42 would have failed it;
  - the rule is now the run's seed + 3, and its test runs in both directions.

---

## 1. What changes from part A and the plan

| item | before | part B | reason |
|---|---|---|---|
| inputs on CFS | J0a hashed the 53.8 GB lateral inside the job (5,057 s, deviation D1), then read it on the same node | **staged once to pscratch by a DTN, and hashed there** (no charge, §4.1). The universe omnifile is hashed in place on the DTN: its full hash before J2 (part A §3) | 2 GiB `dd` reads on 2026-10-24 ran at 1.3 GB/s on login12 and 1.5 GB/s on dtn01, against 5.7–12 MB/s through DVS on a compute node (D1). Every J0 and Stage C compute-node reader of these files hashed them in the job first, so their run times are not cold-read evidence (review B-2) |
| the stat check | the director's ruling (b), for the BeamAngleX_0 lateral | **the same rule for every input the DTN records** (12 files) | ruling (b) generalized, accepted as B3: `stat -c '%s %Y %i'`. A mismatch forces a full re-hash, here on Lustre, and a hash mismatch refuses. The device number is excluded: for the same file it is 124 on login12, 105 on compute nodes and 53 on dtn01 |
| J1 | `E_R` with C2ST step weights (RE2-PLAN §4.2) | **`ER`, `C0_cv` (the same unfold again), `C0_unit`**; no step weights | the C2ST does not read `E_U` (§7.3) |
| charge bound | step node-h × 1.25 (`re2_units.py`); then the director's packing-fraction formula | **the cap sum**: each job's limit on one exclusive node. Each job's projection is its preflight plus its longest lane (§3.2) | J0 lane utilization ≥ 0.9997. The director withdrew the formula (B1) |
| charge gate | the director's form: before J7, ledgered + J7's projection ≤ room | **before every job**: the charge of every ended attempt + the cap of every unfinished one + this job's cap ≤ room. The J7 form is also printed (§3.3) | a cap bounds the charge; a projection does not. Accepted as B2 |
| health rule | `random_state == 45` | `random_state == seed + 3` (`re2_driver.py:2182`) | part B runs at seeds 42, 43, 45, 48, 51 and 54. This is the plan's own rule (RE2-PLAN §5.2) |
| readout | one verdict; sums checked only where listed | **per-set verdicts** (core, J7); every output must be listed in a sums file; every output's recorded argv must match the declared argv (§5) | review M-2, M-3, m-5 |
| post-processing | "new code under review" (RE2-PLAN §3) | **its identity table is declared now (§6); its code is part C**, bound before any post-processing run | accepted as B4. Production need not wait on it, and the pscratch purge risk argues for prompt production (part A §8) |

## 2. Code

The commit is the one this declaration lands in on `re2/declaration-b-20261024`. The BINDING names its sha. The jobs
run from a fresh clone detached at it, as J0 did. Part A's files are unchanged except `re2_k1.py`.

| file | role |
|---|---|
| `2d-unfolding/re2/re2_driver.py` (unchanged from part A, `38ff3705…`) | the RE-2 driver |
| `2d-unfolding/re2/re2_k1.py` (changed, §2.1) | the readout: part A's checks and part B's |
| `2d-unfolding/re2/re2_partb_layout.py` | writes `partb_runs.tsv`, `partb_jobs.tsv` and `partb_checks.tsv` from pinned sources |
| `2d-unfolding/re2/re2b_gate.py` | the charge gate (runs under the login node's system Python 3.6) |
| `2d-unfolding/re2/re2_inventory.py` | writes `inventory.tsv` (§7.1) |
| `2d-unfolding/re2/tests/test_re2b.py` | 23 tests (§2.2) |
| `2d-unfolding/re2/tests/test_re2_readouts.py` (one test added) | 11 tests |
| `run/partb_runs.tsv`, `run/partb_jobs.tsv`, `run/partb_checks.tsv` | the 644 runs, the 12 jobs, the 596 checks |
| `run/partb_identities.tsv` | the post-processing identity table (§6) |
| `inventory.tsv` | the dependency inventory (§7.1) |
| `run/j0_readout/k1_rerun_partb.json` | J0's readout re-run with part B's `re2_k1.py` (§2.1) |
| `run/launch/re2b_env.sh` | part B's settings; sources part A's `re2_env.sh` unchanged |
| `run/launch/re2b_dtn_hash.sh` | the DTN preflight: staging and hashes |
| `run/launch/re2b_job.sbatch` | the job |
| `run/launch/re2b_submit.sh` | gate, then submit; each submission logged |
| `run/launch/re2b_readout.sh` | the production readout (§5) |
| `run/launch/test_stat_check.sh`, `run/launch/test_lane_stdin_b.sh` | the launcher tests (§2.2) |

The sha256 of each file is in §12.

### 2.1 What changed in `re2_k1.py`

- **Health: a part-A readout defect, fixed before part B.**
  - `random_state` must now equal the run's `--seed` + 3, the driver's own rule (`re2_driver.py:2182-2183`) and the
    plan's (RE2-PLAN §5.2: 48, 51, 54 and 57 for the panel seeds).
  - A run with no `--seed` fails health. Every declared run passes one.
  - Under the old literal 45, every J6 run, J7's runs at seeds 45–54 and J8's seed-43 runs would have failed health.
  - The defect was found by this declaration's identity audit.
- **`--sums-glob`:** the jobs' `SHA256SUMS` files beside `--out-dir`. The default, `SHA256SUMS.J0*`, keeps J0's
  readout as it was.
- **Three part-B options.** Without them the readout is J0's.
  - `--classes`: read only the named job classes, so each set gets its own verdict.
  - `--sums-cover-runs`: every selected run's output must be listed in a sums file.
  - `--check-argv`: every selected output's recorded `runConfig` must hold each declared option.
- **J0's readout is unchanged.** The final code, run on J0's real outputs on 2026-10-24, gave a result identical to
  the committed `k1.json` apart from `code_sha256`. The re-run is committed beside the original as
  `run/j0_readout/k1_rerun_partb.json` (`557ce75d…`). Its `code_sha256` is `d10480d0…`, the `re2_k1.py` of §12.

### 2.2 Tests

- **`test_re2b.py`, 23/23** locally (python3.13 with PyROOT) and on Perlmutter (root_6_28); without ROOT, 2 skip.
  - **Layout:**
    - the committed tables are byte-equal to the generator's output;
    - the counts per class;
    - every run is refined 400/31;
    - 17 part-B runs repeat a J0 run's argv option by option, with the same CPUs (`U_MaCCQE_0` and F_MaCCQE0,
      `S1_001` and RB_001, `S3_BeamAngleX0` and FL_BAX0, `C0_cv` and D_cv, `pu_PA_b01` and RPR_PA_b01, …);
    - `ER` equals `C0_cv`;
    - each S4(ii) seed-42 run equals its J2 universe;
    - the 175 universes are exactly the rollup's;
    - every limit is under 12 h and ≥ 1.25 × its wall time;
    - the caps sum within room.
  - **Checks:**
    - every replica has a stream check;
    - every universe except the null and weak bands has a power check;
    - every external reference carries a digest.
  - **`re2_k1.py` over the declared part-B tables,** with a synthetic output for each of the 644 runs. Each output
    records the `runConfig` the driver would record, and the per-lane sums are written as the job writes them.
    - The verdict can be PASS: 644 health rows, 644 argv rows, 644 listed and none unlisted.
    - Each of these defects fails exactly its own row: a seed-48 run recording `random_state` 45, a universe that
      does not move, a wrong stream sum on `S1_150`, and `U_GEANT_Pion_0` recording the other universe index.
    - A job with no sums file fails the readout (its 44 outputs are unlisted).
    - The core and J7 sets get separate verdicts: a defect in J7 fails J7 only.
  - **Gate:**
    - it passes when the caps fit and refuses when one would cross room;
    - an unfinished attempt reserves its cap, and an ended or cancelled one counts its charge;
    - an attempt that never started counts 0;
    - every attempt of a job counts: a timed-out first attempt and a running second;
    - an unlogged attempt found only by name in `sacct` blocks a duplicate;
    - a logged attempt not yet in `sacct` counts its cap;
    - a job with any attempt is refused;
    - a ledger without the two J0 rows is refused.
- **`test_re2_readouts.py`, 11/11** locally and on Perlmutter, including the new seed + 3 test in both directions.
- **`test_stat_check.sh`, 8/8 on Perlmutter** (GNU stat; §4.2). Two mutants were each caught: "never re-hash" failed
  4 cases, and "drop the inode" failed 2.
- **`test_lane_stdin_b.sh` on Perlmutter:**
  - `re2b_job.sbatch`'s `lane()`, with a stub `srun` that reads all its stdin, makes **644 of 644 calls**, each with
    its own label, CPUs and `--out`.
  - Each output is digested in its own lane's sums file: 644 of 644.
  - The table is guarded twice: it is read on fd 3, and `srun`'s stdin is `/dev/null`. Either guard alone keeps all
    644 calls, and removing both gives 35 of 644. So the test detects the loss of both guards, not of one.
- **The gate under `/usr/bin/python3`** (3.6.15) on a login node, with the real tables and nothing submitted: all 12
  jobs pass in order, with caps reaching 72.00 after the core and 79.80 after J7.
- **`bash -n`** passes on every part-B script.

## 3. Production

### 3.1 The runs (`run/partb_runs.tsv`)

**Common argv.** Every run passes `--bkg-mode negweight-refined --refine-n-estimators 400 --refine-num-leaves 31`
in place of purity, with the CPUs and thread environment of its purity counterpart (`OMP_NUM_THREADS=64`).

**Names.** Labels are Stage C's member names without `2dc_P_`, the period test's names, and `U_<band>_<index>`, so
the post-processing copies change only the directory they read.

| job | runs | what | argv, as | CPUs |
|---|---|---|---|---|
| J1 | 3 | `ER` (the future `E_R`), `C0_cv` (the same unfold again: Stage C's C0 row and the S4(ii) seed-42 CV), `C0_unit` | J0's `D_cv`, `D_unit` | 64 |
| J2a–d | 175 | the July universes: `sweeps.json` "pn/" (pinned `15b57de9…`) less CV, the 10 laterals and the 2 Rvp1pi. That leaves 38 bands, including Flux's 100 | J0's `F_*`, which is Stage C S4U's argv | 128 |
| J3 | 10 | the 10 active laterals | Stage C S3, as J0's `FL_BAX0` | 128 |
| J4a–c | 300 | S1: bootstrap seeds 1–300, three streams, seed 42 | J0's `RB_*` | 64 |
| J6 | 80 | S4(i): seeds 45, 48, 51, 54 × bootstrap seeds 1–20 | Stage C `2dc_P_S4B_*` | 64 |
| J7 | 39 | S4(ii): 7 panel universes × seeds 42, 45, 48, 51, 54 (128 CPUs), and the CV at 45, 48, 51, 54 (64 CPUs) | Stage C `2dc_P_S4U_*`, `2dc_P_S4CV_*` | 128 / 64 |
| J8 | 37 | the period test's rows (its `jobs.tsv`, pinned `c2283eb3…`): control, P_A/P_B/P_C at seeds 42 and 43, 10 replicas each | J0's `RF_PA`, `RPR_PA_b01` | 64 |

**J2's lineage.** J2 repeats Stage C S4U's argv (`--flux-universe-file`, `--verbose`, `--branch-select derived`,
64 threads), not the July producer's literal argv: that one had none of the three options and used 128 threads
(`sbatch_unfold_2d_MEFHC_5iter_universes_full_puritynew.sh:67-75`). The two reproduce each other in the purity arm:
- J0's K1-U4–U6 at ≤ 1.4e-11 on 3 bands;
- the July sweep's own CV, which equals `E_U` to 1.4e-11.

**Seeds:**
- estimator `random_state` seed, seed + 1 and seed + 2;
- refinement seed + 3, so 45, 46, 48, 51, 54 and 57;
- the bootstrap seeds of Stage C and the period test, replica for replica.

No other seed is used.

**Kept, though it could be saved.** J7's six seed-42 universe runs that J2 also runs (`Muon_Energy_MINOS:0` has no
J2 counterpart) are kept as cross-job repeats (§5.1), at about 0.96 node-h.

### 3.2 Packing, projection, limits and the bound (`run/partb_jobs.tsv`)

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

The review checked the rule against J0's actual charge: preflight plus longest lane gives J0a 14,533 s against
14,539 s charged, and J0b 5,169 s against 5,173 s.

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
node. Memory is the CPUs × 1,905 MB, as in J0. Two 128-CPU steps take 487,680 MB of the exclusive allocation's
487,802 MB.

**Limit:** 1.25 × wall time, rounded up to a minute, and under 12 h.

| job | lanes × CPUs | runs | wall, s | limit | projected node-h | cap node-h |
|---|---|---|---|---|---|---|
| J1 | 4 × 64 | 3 | 1,166 | 0:25 | 0.32 | 0.42 |
| J2a, J2b, J2c | 2 × 128 | 44 each | 25,600 | 8:54 | 7.11 each | 8.90 each |
| J2d | 2 × 128 | 43 | 25,600 | 8:54 | 7.11 | 8.90 |
| J3 | 2 × 128 | 10 | 8,690 | 3:02 | 2.41 | 3.03 |
| J4a, J4b, J4c | 4 × 64 | 100 each | 23,300 | 8:06 | 6.47 each | 8.10 each |
| J6 | 4 × 64 | 80 | 18,700 | 6:30 | 5.19 | 6.50 |
| J8 | 4 × 64 | 37 | 6,180 | 2:09 | 1.72 | 2.15 |
| **core** | | 605 | | | **57.51** | **72.00** |
| J7 (diagnostic) | 2 × 128 | 39 | 22,448 | 7:48 | 6.24 | 7.80 |
| **total** | | 644 | | | **63.75** | **79.80** |

**The bound (B1, accepted).** The bound is the cap sum, **79.80 ≤ room 84.5245**: no exclusive job is charged past
its limit, so even if every job runs to its limit, part B stays in room. The scheduler's kill delay after a limit is
seconds per job.

**Director correction (2026-10-24).** The director withdrew the earlier instruction to project charge as "step
node-h ÷ the measured packing fraction × 1.25". That formula gives 88.99 for the core and 98.54 with J7. It also
predicts each J2 job at 9.21 node-h, more than its own 8.90-hour limit. J0's measured lane utilization shows the
fractions were not packing losses. The formula's column stays in `partb_jobs.tsv` (`j0_fraction_node_h`) for the
record.

**What the limits leave room for:**
- **Within-class variation above J0's maximum.**
  - J0 measured 1–10 runs per class. A slow node slows every lane of its job, and 1.25 × the wall time covers a node
    about 25 % slower.
  - Stage C's purity S4U steps ran 682–1,323 s (review m-9). At 1,323 s a J2 lane takes 29,406 s with its
    preflight, still inside the 32,040 s limit.
- **Reading the staged inputs from Lustre.** A lateral run reads about its whole 53.8 GB file (`--branch-select
  all`), roughly 30–60 s per run at Lustre's per-client rate. That is about 300 s per J3 lane, against 2,230 s of
  slack.
- **A re-hash after a stat mismatch,** on Lustre at about 0.5 GB/s:
  - each lateral takes about 110 s, against J3's slack;
  - the universe omnifile takes about 340 s, against J2's 6,440 s of slack.
- **The excluded nodes.** The period-test nodes whose replicas timed out (nid004074, nid004078) are excluded, as
  RE2-PLAN §4.2 said.

### 3.3 The charge gate (`re2b_gate.py`, `re2b_submit.sh`; B2, accepted)

**What counts.** An attempt is every `sacct` row named `re2b-<job>` since 2026-10-24, plus every `submissions.log`
id not yet in `sacct`. So an unlogged or duplicate submission still counts. For each attempt:
- an ended attempt counts its charge;
- an unfinished one counts its cap;
- one that never started counts 0.

**The rule.** Before each job is submitted, all of the following must hold, or the job is refused:

charge of every ended attempt + the cap of every unfinished one + this job's cap ≤ room = 90 − J0's 5.4755.

A job with any attempt is refused: a resubmission needs a declared amendment, and the gate then counts every
attempt. Each submission is logged.

**J7 is not held behind the core.** The cap form bounds every job, so J7 may be submitted with the others. The J7
form (ledgered charge + J7's projection ≤ room) is printed as the director asked, and the cap form implies it.

**Measured on 2026-10-24** under the login node's system Python, with nothing submitted: all 12 jobs pass in order.

## 4. Inputs and the preflight

### 4.1 The DTN preflight (`re2b_dtn_hash.sh`; B3 and B9)

**Where it runs:** once, on dtn01, after the BINDING and before any submission. There is no Slurm charge.

**What it checks first:**
- The deploy must be a clean checkout at the bound sha.
- The CFS `SHA256SUMS` of the laterals must match its pinned digest (`73775251…`).
- That file's BeamAngleX_0 row must equal part A's digest (`38b9fc30…`).

**What it does:**
1. **Staging (B9).** It copies the CV omnifile (2.14 GB) and the 10 active laterals (53.8 GB each) from CFS to
   `$B/partb/inputs/`.
   - Each copy is hashed, and its digest must equal the declared one: `43f8cc16…` for the CV, and each lateral's CFS
     `SHA256SUMS` row. So the copy holds the declared bytes.
   - It is then made read-only.
   - The jobs read the copies.
2. **The universe omnifile** (171 GB, pscratch) is hashed in place and must equal `220c479e…`. This is part A §3's
   full hash before J2.

**The record.** Each of the 12 files gets one row in `$B/partb/preflight/inputs.stat`: `sha256 size mtime inode
path`. Its stat is taken before and after its hash, and the two must agree. The record is written once, made
read-only, and refused if it or the staged directory already exists. Its sha256 and the staged size are printed for
the part-B report.

**Staging footprint and cleanup.**
- **Size:** about 0.54 TB.
- **Quota:** `showquota` gives 16.97 of the user's 20.00 TiB on 2026-10-24 (84.8 %; the filesystem itself reads
  68 %). Staging raises it to about 17.46 TiB (87.3 %).
- **Cleanup:**
  - the staged laterals are deleted once J3's outputs are in the core readout with their argv, health and sums rows
    passing;
  - the staged CV is deleted once every job that reads it has been read out.
  
  The CFS originals are untouched.
- **Ruling:** this reverses the director's earlier "do not stage 54 GB to pscratch" (at 85 %), for the reason in §1.
  It is decision B9.

**Expected time:** about 1.25 TB of reads and 0.54 TB of writes at the measured 1.3–1.5 GB/s, with `sha256sum` at
about 0.5 GB/s per process, four at a time. That is about 20–40 min.

**Recorded so far.** On 2026-10-24 the CFS originals and the universe omnifile had these stats:

| input | size | mtime | inode |
|---|---|---|---|
| BeamAngleX_0 | 53,845,911,012 | 1784361874 | 759636316 |
| universe omnifile | 171,117,087,867 | 1783523295 | 882725391507234642 |
| CV omnifile | 2,144,008,221 | 1779094334 | 6874571285 |

Login12, both J0 nodes and dtn01 agree on these stats, though not on the device number. The review confirmed the
DTN stats for all 12 inputs.

### 4.2 The stat check in each job (`re2b_stat_check`, `re2b_env.sh`)

**For each recorded input a job reads:**
1. The record must have exactly one row for the path, and its sha256 must be the declared one. Otherwise the job
   exits 5.
2. If `stat -c '%s %Y %i'` equals the recorded size, mtime and inode, there is no re-hash.
3. Otherwise the job re-hashes the file in full. On Lustre that fits the limits (§3.2). A mismatch refuses, with
   exit 4.

**What is hashed in the job.** The pscratch inputs not in the record (MC flux, flux universes, the 8 period files;
about 4.3 GB, almost all of it J8's period omnifiles) are hashed in each job that reads them, as in J0. Each job
also re-hashes the 3 KB CFS `SHA256SUMS` of the laterals (J3).

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
| J1, J4, J6 | the staged CV |
| J2 | the universe omnifile and the flux universes |
| J7 | the universe omnifile, the flux universes and the staged CV |
| J3 | the CFS `SHA256SUMS` and the 10 staged laterals |
| J8 | the 8 period files |

Every job also checks the MC flux file. The review found every input a job reads covered by a hash or a record
check. Nothing is written to CFS.

## 5. The production readout (`re2b_readout.sh`)

**When and where:** on a login node, once every part-B attempt is in a terminal state. It refuses to overwrite a
readout.

**What it writes** to `$B/partb/readout/`:
- `steps.psv` (`sacct`) and `ledger.tsv` (`re2_ledger.sh`, over every attempt);
- two `re2_k1.py` results, `k1_core.json` (J1–J4, J6, J8) and `k1_j7.json` (J7, if submitted).

**How `re2_k1.py` is run** for each:
- `--sums-glob 'SHA256SUMS.J[1-8]*' --sums-cover-runs --check-argv`;
- `E_U` pinned (`…/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`, `4f5a1b6d…`) for the 205 cells;
- the environment of `re2b_env.sh`, which expands the argv's `$CV`, `$ACT`, `$UNI`, …

### 5.1 Checks (`run/partb_checks.tsv`, 596)

**Pass rule.** Part A's rule:
- equality at ≤ 1e-8 on `E_U`'s 205 cells, with the same reported cell set for `hXSec2D`;
- references re-hashed against their digests;
- power above the row's `min_shift`;
- stream checks to 1e-9.

Each check belongs to the set of its test run.

| ids | n | test → reference | what it shows |
|---|---|---|---|
| PB-ER-rep, PB-ER-D2, PB-ER-J0 | 3 | `ER` → `C0_cv`; RE-1 D2 `71ca3e5f…`; J0 `D_cv` | the adopted product repeats, and equals the refined unfold RE-1 and J0 made. The cell-set test is plan §5.3's structural requirement that `E_R` report `E_U`'s 205 cells |
| PB-ER-eff | 1 | `ER` → J0 purity `C_cv`, `hEff2D` | the efficiency the heat-map figure reads does not depend on the background treatment (CHK-eff) |
| PB-unit, PB-unit-J0 | 2 | `C0_unit` → `C0_cv`; J0 `D_unit` | the bootstrap with factors 1 is the CV |
| PB-null-NormDISCC_0, _1 | 2 | `U_NormDISCC_*` → `ER` | the null band. In the July purity sweep both are within 1.5e-11 of the CV (measured 2026-10-24) |
| PB-J0-* | 15 | 4 universes, `S3_BeamAngleX0`, `pu_PA_s42`, `pu_PA_b01`, `S1_001`–`008` → their J0 runs | the same argv in J0 and part B, run to run |
| PB-panel-* | 6 | `S4U_<u>_s42` → `U_<u>` (J7 set) | the S4(ii) seed-42 universes equal J2's: the refined form of `analyze_prod.py`'s July identity (AP-15) |
| PB-stream-* | 380 | every `S1_*` and `S4B_*` → Stage C's purity replica with the same seeds (digests from `stageC/production/evidence/production/SHA256SUMS.pscratch`, pinned) | **on the data**, each replica's refined background stream: signed sum = data-factor sum − the purity replica's resampled background (STREAM-1, for all 380). The review confirmed the identity on a real pair and that the S4B references carry the same bootstrap stream |
| PB-pow-U_* | 171 | every universe except NormDISCC and EtaNCEL → `ER`, > 1e-4 | each universe moves the result. In the July sweep every one moved ≥ 1.08e-2 |
| PB-pow-S3_* | 10 | every lateral → `ER`, > 1e-6 | each lateral moves it |
| PB-pow-* | 6 | `S1_001` → `ER`; `S4B_s45_01` → `S1_001`; `S4CV_s45` → `ER` (J7 set); `pu_PA_b01` → `pu_PA_s42`; `pu_PA_s43` → `pu_PA_s42`; `pu_PB_s42` → `pu_CTRL_s42` | a replica, the seed, a period replica, a period seed and a period each move it |

**Health:** every run. Each needs:
- clipped fraction ≤ 0.01;
- refined/signed in [0.99, 1.01];
- `random_state` = seed + 3;
- 400 trees and 31 leaves.

**Argv:** every run's recorded `runConfig` must hold each option of its declared argv: inputs, universe, seeds,
bootstrap seed and streams, branch selection, mode and size. A swapped universe index or bootstrap seed fails its
own row (review m-5).

**Sums:** every run's output must be listed in its lane's `SHA256SUMS.<job>.<lane>`, which the job appends as each
run succeeds, and must match it.

**Not checked, and why:**
- **EtaNCEL_0 and EtaNCEL_1** move the purity result by 3.0e-7. That is below a power floor and above the null
  tolerance, so they get neither check, only health, argv and sums.
- **Nine laterals have no refined reference:** all but BeamAngleX_0, including Muon_Energy_MINOS_0. That universe is
  also an S4(ii) panel universe with no J2 counterpart. They get health, power, argv and sums. J0's CHK-det2 showed a
  lateral repeats to 6.4e-13.
- **S4(i)'s 80 replicas have no numerical identity** (the identity audit's finding, as in Stage C). Each gets a
  stream check, health, argv and sums, and one of them (`S4B_s45_01`) a power check.

### 5.2 Verdicts

**Each set gets its own verdict:** the core (J1–J4, J6, J8) and J7.

A set is **COMPLETE** when, for every run in it:
- each of its checks passes;
- its health and argv rows pass;
- its output is listed and matches its sums.

**What depends on the core:** part C's products, `E_R` and `Q_R`. J7 contributes only the reported, not-added X03
diagnostic, so a refused or failed J7 does not block them.

**A failed core** means the report names what failed and nothing downstream runs on a failed product. A rerun needs
the director.

## 6. Post-processing: the identity table now, the code in part C (B4, accepted)

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

**Binding.** The director binds part C before any post-processing run.

**`run/partb_identities.tsv`.** It has 173 rows, one per check in those producers, read at `5b8b9765`. Each row is
classified:

| class | rows | meaning |
|---|---|---|
| K | 95 | keep as it is |
| R | 49 | repin to the refined product |
| X | 16 | replace, because it is an identity against a purity reference |
| G | 13 | a new mode guard, or the driver record it reads |

An independent agent wrote the table. The lane spot-checked five of its line claims, and the review checked
AP-09/10/15 and S5-09/10. All hold.

**The 16 replacements:**

| ids | where | replaced by |
|---|---|---|
| AP-09, AP-10 | `analyze_prod.py:146-147`, C0 against XR-L0 | PB-unit; PB-ER-D2 and PB-ER-J0 |
| AP-13 | `analyze_prod.py:196-200`, S3 against the pilot laterals | PB-J0-S3_BeamAngleX0. The other nine have none (§5.1) |
| AP-15 | `analyze_prod.py:222-225`, the July identity at seed 42 | PB-panel-* (J7's readout needs J2's outputs) |
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
- **Every consumer needs the new guard.** The driver records `runConfig` on every path (`re2_driver.py:1403-1410`)
  and `re2Refinement` only on the refined path (`:2218-2220`). Stage C's purity products lack the `refine_*` keys, so
  the purity guard accepts absent or null.
- **Checks that record but don't stop:** `analyze_periods.py`'s control (`:336-339`) and `export_cov.py`'s controls.
- **The period chain's χ² values** use the purity VL175+ML covariance (`analyze_periods.py:104`). Part C states
  whether that stays.

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
- **Reproducibility:** the review regenerated it byte-identically in a scratch clone.

A literal hit is a site to read, not a finding. The integration step reads every one.

### 7.2 R7: "marginal normalizations agree at about 1–2 %" (a plan error, found at declaration)

**Where it is printed now:** `paper_body.tex:95` (Table I) and `:470-472`, `main_note.tex:75-77`,
`sec_execsummary.tex:44`, `sec_summary.tex:31-33` and `primer_body.tex:373`.

**Its producers:** the 3D–5D anchor checks, both configuration (a). Neither reads `E_U` or any 2D product.

| producer | compares | recorded values |
|---|---|---|
| `nd-unfolding/check_4d_anchors.py` | 4D with 3D | medians 0.38 / 0.64 / 1.68 %, ratio 0.9960 (`VALIDATION_LEDGER.md:1822-1824`, `:1763-1764`) |
| `nd-unfolding/check_5d_anchors.py` | 5D with 4D | 5D/4D 1.0011, medians 0.3–1.5 % (`VALIDATION_LEDGER.md:1764`, `sec_eavailw.tex:49-52`) |

`CLAIM-TABLE-20261008.tsv:29` (V15) maps the sentence to these outputs as an envelope.

**Result: RE2-PLAN §2.4 was wrong to list the sentence as depending on the 2D result.** It is unchanged by RE-2.
Only `sec_3d.tex`'s 3D-against-2D clause (0.001 %) is re-evaluated against `E_R`, by RE-1's `re1_f_numbers.py`
route.

### 7.3 The C2ST (a plan error, found at declaration)

**Its producer** is `nd-unfolding/unbinned_gof.py` (launcher `sbatch_unbinned_gof.sh`, deleted in `b017cfe6`; still
listed at `nd-unfolding/MANIFEST.md:60`).

**What it reads:**
- the **3D** (pT, p∥, E_avail) inputs `of_inputs_3d.npz`;
- the configuration-(a) OmniFold weights it computes itself (`:132-136`), or loads (`:125-127`).

The 0.535 → 0.501 is at `docs/STATVAL_REPAIR.md:113,131`.

**Result: RE2-PLAN §2.2 and §4.2 were wrong** to say it uses the purity 2D central unfold's weights and that J1
writes them.
- It never reads `E_U`, and stays an unchanged configuration-(a) 3D diagnostic.
- J1 writes no step weights.
- A refined 2D C2ST would be a new test, not a re-evaluation, and is not in RE-2 (§9).

### 7.4 RO-FPS (part A §6)

**The reference:** "Control unfold total 3.073e-38 = the frozen production 2D number exactly"
(`VALIDATION_LEDGER.md:1614-1615`, job 54244120, 2026-06-10). **It has no committed digest.**
- It was made by step [5] of `nd-unfolding/sbatch_fps_mefhc.sh:64-67`: the ND driver with `--axes ""`, seed 1,
  purity.
- It is printed to 4 significant figures (`.4g`, `unfold_nd_omnifold_unbinned.py:1095`).

**The readout,** when `E_R` lands: `hXSec2D.Integral("width")` of `E_R`, the bin-area-weighted total, at 4
significant figures, against 3.073e-38.
- The result is printed either way: "reproduces", or the two values and their difference.
- Its source is printed as "`VALIDATION_LEDGER.md:1614-1615`, no committed digest".

**Positive control:** the same quantity on `E_U` must give 3.073e-38, "reproduces".
- Measured 2026-10-24: `E_U` gives 3.073023e-38, and J0's refined `D_cv` gives 3.068738e-38.
- The plain bin sum, 3.726e-37, is not the quantity.

On those values the refined outcome is expected to be a difference (3.069e-38). The rule does not depend on that
expectation.

### 7.5 The replaced-identity list

§6.

## 8. Storage and HPSS (R9)

**On pscratch:**
- **Part B's products** go to `$B/partb/` (`out/<label>/xsec.root`, `logs/`, `inventory/`, `preflight/`, `inputs/`
  (staged, §4.1), `SHA256SUMS.<job>.<lane>`, `submissions.log`, `readout/`). That is about 46 MB of outputs, at
  J0's about 72 KB each, plus logs, and the staged inputs until their cleanup.
- **Nothing is written** under a checkout, to CFS, or over a purity product.

**On HPSS.** The final products (`E_R`, `Q_R`, the S5 and C_PL products, the combination, the receipts; part A §8:
about 35 MB) are copied to HPSS after part C. The procedure, fixed now, follows the lane's HPSS record (an archive was
once found empty while its markers said verified):
1. **Bundle and manifest.** A local tar bundle holds the products, because small files are bad on tape. A manifest
   gives each member's sha256 and the bundle's own sha256.
2. **Put with a hash.** `hsi put -c on <bundle> : <hpss path>` stores an md5 for `hashverify`.
3. **Migrate.** `hsi migrate -R`.
4. **Check residency.** `hsi ls -V` must show the bundle's bytes **at the tape level**. The `DISK` in the mode line is
   a class-of-service name, not residency.
5. **Verify the digest.** `hsi hashverify` on the bundle, with its exit status captured unpiped.
6. **Test recovery.**
   - `hsi get` the bundle into a fresh, empty directory, and check its sha256 against the manifest;
   - untar it into another fresh directory;
   - re-hash every member against the manifest, and diff the path sets both ways, both non-empty;
   - open every ROOT file.
   
   A `hashverify` pass alone is not a recovery.
7. **Reconcile.** `hsi du` of the archive directory must equal the bundle's size, and quota-used must be consistent
   with it.

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
- **A failed run.** Its lane records it and goes on. The readout fails what needs it, and that set is not COMPLETE.
- **The time limit.** Slurm stops the job (`--no-requeue`), and it is reported. The runs it finished keep their
  digests. It is never resubmitted without the director, and a split of a declared limit is raised first.
- **The gate refuses.**
- **Refinement health, argv or a check fails.** Nothing downstream runs on that product.

**Grant fields (delegation §3.1):**
- **Window:** from the BINDING record to the part-B readout, or 2026-11-30.
- **Charge:** ≤ 84.5245 node-h (room), enforced by the gate. The declared caps sum to 79.80.
- **Attempts:** one submission per job, which the gate enforces. A failed job may be resubmitted at most once, and
  only:
  - for a cause outside the declared code;
  - with the director's approval;
  - under a declared amendment.
  
  The gate counts every attempt.
- **Terminal outcomes, per set (core, J7):**
  - COMPLETE;
  - stopped at preflight;
  - stopped at a limit;
  - a named check, health, argv or sums row failed;
  - refused by the gate.

## 11. Decisions for the director

**The director's preliminary rulings, 2026-10-24.** They become final in the BINDING after this PR's review.

| # | decision | ruling |
|---|---|---|
| B1 | how to bound charge | **accepted:** the cap sum, 79.80 ≤ 84.52, with each job projected from its own layout. The packing-fraction formula is withdrawn (a director correction, §3.2) |
| B2 | the gate | **accepted:** before every job, cap form; the J7 form printed |
| B3 | ruling (b) for every DTN-recorded input, and the full universe hash on a DTN | **accepted**, with the dev 53 on dtn01 noted |
| B4 | the identity table now, the code as part C, bound before any post-processing run | **accepted** |
| B5 | the C2ST and "1–2 %" | **accepted as corrections to RE2-PLAN:** both unchanged; only `sec_3d`'s 0.001 % clause is re-evaluated |
| 6 | seed + 3 in place of the literal 45, with its test | **accepted:** a part-A readout defect fixed before part B; the re-run `k1` committed beside the original |
| 7 | RO-FPS against `VALIDATION_LEDGER.md:1614-1615` | **accepted:** labelled "no committed digest", printed either way at 4 s.f. |

**Raised after those rulings,** by the review:

| # | decision | the lane's recommendation |
|---|---|---|
| B9 | stage the CV and the 10 laterals on pscratch (0.54 TB, quota 84.8 % → 87.3 %, deleted after use, §4.1). This reverses the earlier "do not stage 54 GB to pscratch" | accept. Without it, J3 reads cold over DVS: at J0a's ≈ 10 MB/s, at least 4,500 s per lateral against its 1,678 s unit, and J3 would time out (review B-2) |
| B10 | the refinement seed follows the estimator seed (seed + 3; 46–57 off seed 42), as RE2-PLAN §5.2 declared. The registry entry `a-refined-400-31` names `random_state` 45, its seed-42 value | confirm: the S4 seed main effect then includes the refinement's seed, as the estimator's other seeds do |
| B11 | per-set verdicts: J7 cannot block `E_R` or `Q_R` (§5.2) | accept |

## Review record

**Reviewer.** A fresh Claude agent, given the declaration, the code, the records and the director's instructions,
and none of the author's working. It reviewed `71ab26bc` read-only, in two directions:
- declaration → evidence;
- requirements → declaration.

It worked on the cluster only under its own review directory, and ran no jobs.

**Findings:** 2 blockers, 4 majors, 9 minor and 3 nits.

**What it confirmed:**
- every digest of §12 at `71ab26bc`;
- 30/30 tests;
- the stat test;
- the lane test;
- the inventory, byte-identical;
- every row and sum of the job table;
- the layout rule against J0's actual charge;
- every class's argv, CPUs and labels against the purity producers;
- the 175 universes;
- the 399 external references and their digests;
- the stream identity on a real pair;
- the `--seed` regex;
- the `hEff2D` and sums-glob handling;
- the scontrol formats;
- the memory fit;
- the DTN stats;
- input coverage;
- no CFS writes;
- the R7, C2ST and RO-FPS citations.

| finding (severity) | disposition |
|---|---|
| B-1: the gate fails under the login node's Python 3.6 (`from __future__ import annotations`), so every submission is refused (BLOCKER) | the gate is 3.6-clean and is called as `/usr/bin/python3`; re-measured there: 12/12 pass |
| B-2: J0's lateral and CV times followed an in-job hash of the same file, so they were probably page-cached; a cold DVS read would time out J3 and squeeze J1 (BLOCKER) | the DTN stages the CV and laterals to pscratch and hashes them there (B9); Lustre read and re-hash time budgeted (§3.2) |
| M-1: a stat mismatch in J3 re-hashes 53.8 GB over DVS, a certain timeout (MAJOR) | the re-hash is now on Lustre (≈ 110 s per lateral), within J3's slack |
| M-2: a job with no sums file went unchecked; a TIMEOUT left finished runs undigested (MAJOR) | `--sums-cover-runs`; each lane appends each run's digest as it succeeds; test: a missing job's sums fail the readout |
| M-3: one verdict over all 644 rows let a refused or failed J7 block `E_R` (MAJOR) | per-set verdicts, core and J7 (B11); test |
| M-4: the gate kept only the last attempt per job, so "counts both attempts" was false (MAJOR) | every attempt counts, from `sacct` by name and from the log; tests |
| m-1: a never-started cancelled job (empty AllocTRES) crashed the gate | counts 0; test |
| m-2: the "director's form" was neither the director's projection nor enforced; J7's release was unstated | renamed the J7 form; §3.3 states J7 is not held behind the core |
| m-3: "seven" seed-42 repeats | six, 0.96 node-h |
| m-4: RO-FPS's "total" undefined | `Integral("width")`, with `E_U` as positive control; both measured |
| m-5: no check that an output is the run it is labelled | `--check-argv` on all 644; test with a swapped universe index |
| m-6: the HPSS steps did not hang together (`htar` vs `hsi put`, no hash created, `du` against members) | §8 rewritten: local bundle, `put -c on`, migrate, residency, `hashverify`, recovery, `du` against the bundle |
| m-7: the refinement seed moves with the estimator seed | stated as RE2-PLAN §5.2's rule; B10 for the director |
| m-8: the readout command was not pinned | `re2b_readout.sh` (§5) |
| m-9: J2's argv is Stage C S4U's, not the July producer's; Stage C's S4U steps reached 1,323 s | §3.1 lineage; §3.2: 1,323 s still fits |
| nit: the lane test sees the loss of both guards, not of one | stated (§2.2) |
| nit: the launch scripts were committed without the execute bit | set; usage lines say `bash …` |
| nit: `sacct` logging came after `sbatch`, so an unlogged job was invisible to the gate | the gate now finds attempts by name in `sacct` |

## 12. File digests

Paths under `docs/…/methods/re2/` are given relative to it.

| file | sha256 |
|---|---|
| `2d-unfolding/re2/re2_driver.py` | `38ff37055af026bd11b1c12a431b31eed522d5038c1bcf020cd47c374d2ddf7c` |
| `2d-unfolding/re2/re2_k1.py` | `d10480d0ce5fa2a7deec16ac6a76de0409e945c0ba587dd1d9dda31d2899da09` |
| `2d-unfolding/re2/re2_partb_layout.py` | `e1562ebc650935eb54e6e63ce10c3c0ee48cdaee30973ba06589137c6e529d88` |
| `2d-unfolding/re2/re2b_gate.py` | `77e9854b58863ecaa312ffeb59c1fb29785ab8d98e95f1d00e80e806e599d067` |
| `2d-unfolding/re2/re2_inventory.py` | `e686621bcd1331c6167fdefbcf386a1f7c042393d7a41f52e3edc17b61764d39` |
| `2d-unfolding/re2/tests/test_re2b.py` | `b079c3f3fcf39c161bdcb0e8e9bec3693b19a75ab0e2d4da5480f092b44c0628` |
| `2d-unfolding/re2/tests/test_re2_readouts.py` | `fc7e87b5624b2eed736132a44d1fa206abd5e4501917e4a618a70ae1f2c1e46a` |
| `run/partb_runs.tsv` | `526b70e0cda78ef476f921d817ff264f67f1b8844b241ca4e65083a196a1127b` |
| `run/partb_jobs.tsv` | `8372d10755a7b4687d978fb1bca8ad87b2e01b8566414183fdfddd26ce81c1ed` |
| `run/partb_checks.tsv` | `607187093a921641795214e503264f161222b3e9014c651cdc1d55d15710c9b7` |
| `run/partb_identities.tsv` | `7efe151211b2b89c94ebf2b8112a1611d3ae9a8918b8de42495bbdcc8fb7fd97` |
| `inventory.tsv` | `532deabaf725f42b4fb95b7cf71a45e3437e37af81af0fec50647ca6c9f86672` |
| `run/j0_readout/k1_rerun_partb.json` | `557ce75d35abbee43ca8ad1f146caaa0e3e2b73188be9564e9e2781b3bf084fc` |
| `run/launch/re2_env.sh` | `cb6c23b2b490e57788ec9e2e8f7fcf942d359c49e27028343905b1d939352a2c` |
| `run/launch/re2b_env.sh` | `65100d84c564f3bd10b73062a64750fd481dca37df9f6d2eafdceab301293d5c` |
| `run/launch/re2b_dtn_hash.sh` | `b39c35663f734fc5be1e8f5e06c011c878c4a19e9e9d70ce45c0b6665ffc9c9b` |
| `run/launch/re2b_job.sbatch` | `628abbef4a71e88dcb36bbac56b1682319018fc649866d751524bb571f3a857f` |
| `run/launch/re2b_submit.sh` | `a28287fc2a2d4e299ab18c847d83bb85e019c5eb5cd05e082ba3f78eb3bc9924` |
| `run/launch/re2b_readout.sh` | `ca904ff3e11cd3428e239606540a0d97375284c39132d26cc95d7e495ec200c3` |
| `run/launch/test_stat_check.sh` | `daaae51bb4a44e4049a553a364cae09613380b937c27eb6b72e3852ce66f118c` |
| `run/launch/test_lane_stdin_b.sh` | `d3d27367ee7c7e24742338fb2b611598b2d236323a9d0fc11fea316cad5af17e` |
