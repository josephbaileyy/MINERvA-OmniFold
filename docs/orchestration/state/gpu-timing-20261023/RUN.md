# RUN: GPU-node timing of the 5D unfold unit (2026-10-23)

**By** the measurement session, under [`ASSIGNMENT.md`](ASSIGNMENT.md) (the binding) and
[`DECISION-20261023-joseph-gpu-test-and-campaign-criterion.md`](../../DECISION-20261023-joseph-gpu-test-and-campaign-criterion.md).
Written and committed before any job. This is a timing measurement, not a result.

**CITABLE FOR:** which unit is timed, with its code, inputs and seed; the exact commands and scripts.
**NOT CITABLE FOR:** any timing (that goes in `REPORT.md`), coverage, uncertainty or claim.

## 1. The unit, and where 293.973 s comes from

- **The figure.** `gbdt/REPORT.md:416` quotes `results.json:635`, `pseudo_unfold_seconds_K5_32threads` 293.973. That
  is `state/s5p/stage2/stage2_receipt.json`, `costs["('pseudo', 5, 'None', 'float32')"]`: n 423, median
  `seconds_unfold` 293.973, max 348.522.
  - The analyzer `nd-unfolding/s5p_stage2_analyze.py:412-418` (sha256 `662d577a…`, as the receipt records) keys each
    product by (construction, iters, capacity, coords).
  - The 423 are every pseudo, K = 5, default-capacity, float32 product under `s5p-20260926/runs/s2/num/`.
- **Configuration.** Every one of them is candidate R, so they are configuration (e). Of the 71 table lines, 61 run
  `s5p_numerics.py --config R` and the 10 C2 lines run `s5e_candidate.py --candidate R`.
  - `state/s5p/contract.json:25-26` names the baseline estimator R.
  - `state/2d-closeout/stageF/methods/r12/REVIEW.md:48` identifies it as "the paper's configuration (e)".
  - So no substitute unit is needed.
- **Where they ran.** All stage-2 numerics ran on CPU nodes, 8 steps × 32 CPUs concurrently, on the interactive QOS.
  - `state/s5p/queues/s2-cpu-r.q` lists the tracks: B = 4+1+2+1 and C = 3+1+4 concurrent steps.
  - The GPU lane `s2-gpu-r.q` was "NOT USED".
- **The chosen receipt:** `/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/nom/nom_b-_j-.npz`.
  - sha256 `c9975f69752c388af343ecc3222df5d1401119549f90cbc8f7c0ee6e4c9cf315`, 183,898 bytes.
  - It is one of the 423. It is the nominal pseudo experiment with no bootstrap and no jitter: the first pair `-:-`
    of task line 14 (`n_nom_jit0`, 0-based) of `state/s5p/s2-num-tasks.tsv`.
  - That table is byte-identical at `18337b8c` and at main `c957f514`.
  - Allocation 58911473, step 0, host nid004153 (CPU). The step log is
    `s5p-20260926/runs/s2/num-logs-b4/logs-step-14.out`.
  - Its recorded `seconds_unfold` is **338.105** (`seconds_load` 18.44).
  - That is one draw from the 423. The readout compares each arm both with it and with the 423-median.
- **Meta of the recorded unit:**
  - schema `s5p-numerics/1`, config R, iters 5, capacity null, construction pseudo, truth nominal, amplitude 0.0;
  - pseudo seed 930000, split key 2468625257753644, no bootstrap seed or jitter seed, coords float32;
  - estimator seed 42 (refinement `random_state` 45), threads 32, LightGBM deterministic and `force_row_wise`;
  - OmniFold estimators 100 trees / 8 leaves; refinement 400 / 31.
- **Code.** The pinned deploy was `deploy/18337b8c` = commit `18337b8c0322fb1a052f82d436439bd942ca7333` (on main).
  - It is recorded by `steps-58911473.log`.
  - That deploy no longer exists. A fresh clean clone at the same commit is at
    `/pscratch/sd/j/josephrb/gpu-timing-20261023/deploy/18337b8c`, with 0 modified tracked files.
  - Its sha256 equals the product's recorded `code_sha256` for all 11 files:

| file | sha256 (recorded = deploy) |
|---|---|
| `s5p_numerics.py` | `9d7c12322200dc2dca2944883ad0f51e41e58a70d5ac3d87991c3bb85611630a` |
| `s5n_pseudo.py` | `8981f97b96b418cfe46f1e940cb120f174053d7d3429f3b0b01a229c6c02ee6c` |
| `s5c_pseudo.py` | `d81d4f46fb55f25fdf7ce2e4b9a9a63bf876beaf754bdc250eee974579e11f5d` |
| `s5c_unfold.py` | `510d749a2e82fa448de6172753ae2adc9ebd81a89d4f18bf76beb5faa8bb3968` |
| `omnifold_nn_core.py` | `24f87f119073c4f125c2f753310507d4375b6f8a1b7751e59d3615dd50e90582` |
| `xsec_nd.py` | `454001f3c9ac3aa6485d184aadb8aba65dd71dba124816962b9c3b6344920fa5` |
| `2d-unfolding/unfold_2d_omnifold_unbinned.py` | `8ebe0277ee4c277f6f697712a901b14d6ba24ed5dcadfc3c66b29276acf81b5e` |
| `s5e_candidate.py` | `bda8c48ce2365e173bbba083b18233d6f6b7c2dfbab5179156073860c8281ec7` |
| `s5e_deform.py` | `6726ff99c7787d1ee6dff7fa5d08df88f9df76285d98c4c462f964ac6164779f` |
| `s5e_trace.py` | `c47e9dd3feef9eab323e40f4e0da770ad67e86431a1ce95f99a10007decc66c1` |

  The deploy's `s5c_array.sh` is `693055815f1b…`, `mnv_guarded_run.py` is `30162f57771c…` and
  `setup_salloc_env.sh` is `ea3c6998d33f…`.
- **Inputs.** `of_inputs_5d.npz` sha256 `07fccc1a…a649f` and `bkg_dump.npz` sha256 `2addac8f…82955`. The tool itself
  checks both digests and exits 4 on a mismatch (`s5p_numerics.py:158-162`).
- **Environment.** As recorded: `setup_salloc_env.sh` activates `$HOME/.conda/envs/root_6_28`, with Python 3.11.14,
  LightGBM 4.6.0 (`lib_lightgbm.so` sha256 `6a12e1a7b138…`), scikit-learn 1.8.0 and NumPy 1.26.4. Nothing is built
  or installed.

## 2. Tables and scripts (`tools/`, copied to `/pscratch/sd/j/josephrb/gpu-timing-20261023/tools/`, sha256 equal)

| file | sha256 |
|---|---|
| `tools/tasks.tsv` | `703ce4606f0560c5e4cf484bb481fe3dfaa94a39e0071c252a59d0250ebbab9c` |
| `tools/sbatch_timing_packed.sh` | `b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3` |
| `tools/g3_probe.py` | `f6d6fb23f2acf39c1781a93cccca8456a0f5bd7b866c4533ac15d52d339ede4c` |
| `tools/kt1_readout.py` | `1f39e395f039a8cac6fcac7b3915c68c8bec67f1d462c47e67949b055cb9ea6d` |

- **`tasks.tsv`** has 15 lines, generated from recorded line 14 with two changes only:
  - `--pairs=-:-` (the recorded line's first pair alone);
  - `--out <pscratch>/runs/<arm>/<task>` (a separate directory per task, so concurrent tasks never collide).
  - Lines 0-7 are C0, 8 is G1, 9-12 are G2 × 4 and 13-14 are G2 × 2.
- **`sbatch_timing_packed.sh`** runs one table line per `srun --exact -n1 -c 32 --mem=56G` step, all concurrently,
  each through the pinned deploy's `s5c_array.sh`.
  - That is the recorded step's form (`s5c_steps.sh`: `srun --exact --cpus-per-task=32 --mem=56G`).
  - On GPU nodes the steps take `--gres=none`, as the s5p GPU lane did (`s5c_launch.sh`), so CPU steps are not
    serialized on the GPUs.
  - Memory: the recorded steps used at most 24.2 GB MaxRSS (sacct 58911473). 4 × 56G fits a GPU node's 257,100 MB.
- **`g3_probe.py`** is the one-line LightGBM device probe.
- **`kt1_readout.py`** does the K-T1 comparison and collects the timings.

## 3. The G3 probe, already run (login node, 0 node-h)

- `device_type="cuda"`: **LightGBMError "CUDA Tree Learner was not enabled in this build. Please recompile with CMake
  option -DUSE_CUDA=1"**.
- `device_type="gpu"` (OpenCL): **segmentation fault in `Booster.__init__`** (`basic.py:3661`, rc 139).
  - This was on login node login10, which has an NVIDIA A100 and `/etc/OpenCL/vendors/nvidia.icd`.
  - The library contains the OpenCL learner (boost::compute symbols) but does not link `libOpenCL`.
- So the existing environment has **no usable GPU device** for LightGBM.
- G3 timing is **not run**. Making it run would need a new build or install, which the assignment reserves to the
  director. The same one-line probe repeats once on the G1 GPU compute node, before G1's timed step, as a fact for the
  report. It runs as two short steps with one GPU each. Whatever it prints, no G3 timing runs under this binding.

## 4. Jobs (all on the debug QOS, never premium; each under 1 h)

```bash
B=/pscratch/sd/j/josephrb/gpu-timing-20261023; D=$B/deploy/18337b8c; PIN=18337b8c0322fb1a052f82d436439bd942ca7333
T=$B/tools/tasks.tsv; S=$B/tools/sbatch_timing_packed.sh
# C0: CPU node, 8 x 32 concurrent
sbatch -A m3246   -q debug -C cpu                     -t 00:25:00 -J gput_c0   -o $B/logs/%x_%j.out $S $D $PIN $T $B/runs/c0   32 56G 0  7  inherit
# G1: GPU node, CPUs only, 1 x 32 (after the two probe steps)
sbatch -A m3246_g -q debug -C gpu --gpus-per-node=4   -t 00:15:00 -J gput_g1   -o $B/logs/%x_%j.out $S $D $PIN $T $B/runs/g1   32 56G 8  8  none $B/tools/g3_probe.py
# G2: GPU node, CPUs only, 4 x 32 concurrent (the node's 128 CPUs)
sbatch -A m3246_g -q debug -C gpu --gpus-per-node=4   -t 00:25:00 -J gput_g2x4 -o $B/logs/%x_%j.out $S $D $PIN $T $B/runs/g2x4 32 56G 9  12 none
# G2 (2 x 32, within the cap)
sbatch -A m3246_g -q debug -C gpu --gpus-per-node=4   -t 00:15:00 -J gput_g2x2 -o $B/logs/%x_%j.out $S $D $PIN $T $B/runs/g2x2 32 56G 13 14 none
```

**Cap, enforced by the time limits:** CPU at most 25 min = 0.417 node-h (cap 0.5). GPU at most 15 + 25 + 15 = 55 min =
0.917 node-h (cap 1.0). Expected use is about 0.15 CPU and 0.4 GPU node-h. The debug QOS runs at most 2 jobs per user
at a time (`sacctmgr`), so the jobs queue behind each other. Every job exclusively holds one node, so the arms never
share a node.

**Phase-1 grant:** GPU so far 0 of 3. CPU is within the 35-node-h grant. Every job is ledgered here in `LEDGER.tsv`
from `sacct` (job id, QOS, elapsed, AllocTRES billing, charge).

## 5. Readout (after the jobs; login node, 0 node-h)

```bash
env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I $B/tools/kt1_readout.py \
  --recorded /pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/nom/nom_b-_j-.npz --runs $B/runs --out $B/kt1.json
sacct -j <ids> -P --format=JobID,JobName,Account,QOS,NodeList,Start,End,ElapsedRaw,State,ExitCode,AllocTRES%120,MaxRSS > receipts/sacct.txt
```

- **K-T1.** `xsec_flat`, `xtrue_flat` and `shape` must equal the recorded product byte for byte, for every C0 and G1
  product. A mismatch voids that arm's timing as a measurement of the recorded unit. G2 is reported the same way, as
  a fact.
- **Per arm:**
  - per-task `seconds_unfold` (the recorded quantity: pseudo construction + K = 5 unfold + refinement), median and
    range over the concurrent tasks, and the step wall time from `sacct`;
  - node throughput = n_concurrent × 3600 / median `seconds_unfold`, in unfolds per node-hour;
  - node-h per unfold = median `seconds_unfold` / 3600 / n_concurrent. This is the gbdt §9 form: 293.973 / 28,800 =
    293.973 / 3600 / 8.
- **Re-pricing** the gbdt §9 table for 1, 31, 101 and 288 unfolds per experiment: (node-h per unfold) × 1.25 ×
  4 × 4,404 × U, then admitted = subtotal / 0.8.
  - In GPU node-h from G2 × 4, beside the CPU figures from C0 and those from the recorded 293.973.
  - The arithmetic is shown in `REPORT.md`.
- **Products, logs, sacct and `kt1.json`** are copied into `receipts/` with a `SHA256SUMS`. The products are about
  180 kB each.
