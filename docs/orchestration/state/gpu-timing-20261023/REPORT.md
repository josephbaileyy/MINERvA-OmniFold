# REPORT: GPU-node timing of the 5D unfold unit (2026-10-23)

**By** the measurement session, under [`ASSIGNMENT.md`](ASSIGNMENT.md) and the pre-committed [`RUN.md`](RUN.md)
(committed at `6bab0d8a` before any job; its §6 adds C1, approved by the director by message, at `c51ab514` before the
C1 job). Jobs 60145929–60145932 and 60151381, ledgered in [`LEDGER.tsv`](LEDGER.tsv). Receipts are in `receipts/`
(`SHA256SUMS` covers all 76 files).

**CITABLE FOR:**
- the measured per-task time of the recorded K = 5 configuration (e) pseudo unfold on CPU and GPU nodes, packed and
  unpacked;
- its bitwise reproduction (K-T1);
- the re-priced gbdt §9 table in GPU node-h;
- the facts of the G3 probe.

**NOT CITABLE FOR:**
- the cause of today's slowdown against the record (§3), which is measured but not explained;
- any coverage, uncertainty or claim;
- an authorization of any campaign (Joseph's criterion, DECISION-20261023 §3, governs that);

## 1. Answer

- **On a GPU node's CPUs, packed 4 × 32, one unit takes a median 411.25 s per task.** That is 35.0 unfolds per GPU
  node-hour, or **0.028559 GPU node-h per unfold**.
- The re-priced §9 table, in admitted GPU node-h:
  - **786** for 1 unfold per experiment;
  - **24,369** for 31 (statistical only), which is 57% of the 42,727.4 left in `m3246_g` on 2026-10-23;
  - **79,395** for 101;
  - **226,395** for 288.
- **K-T1 passes for every product.** All 16 products (C0 × 8, C1, G1, G2 × 4 × 4, G2 × 2 × 2) equal the recorded
  product byte for byte. So every arm timed exactly the recorded unit.
- **Today the unit is slower than recorded, on any node.**
  - Alone, it takes 420 s on a CPU node (C1) and 409 s on a GPU node (G1), against the recorded packed median of
    294 s.
  - Packing 8 on a CPU node adds a further 1.27× (C0, 533 s). Packing on a GPU node adds nothing.
  - The cause of the 1.43× gap to the record is not identified (§3).
- **G3 (LightGBM GPU training) is not available** in the analysis environment, on a login node or on a GPU compute
  node (§5). No rebuild was made.

## 2. The unit and the controls

- **The unit.** Per `RUN.md` §1, it is the s5p stage-2 receipt `s5p-20260926/runs/s2/num/nom/nom_b-_j-.npz`.
  - sha256 `c9975f69…`; one of the 423 products behind 293.973 s, all candidate R = configuration (e).
  - Nominal pseudo seed 930000, no bootstrap or jitter, float32, K = 5.
  - Code at `18337b8c`. All 11 recorded code sha256 equal those in the fresh deploy.
  - Inputs: `of_inputs_5d.npz` `07fccc1a…` and `bkg_dump.npz` `2addac8f…`.
- **What ran.** Every task ran the pinned deploy's `s5c_array.sh` → `mnv_guarded_run.py` → `s5p_numerics.py`, with
  `srun --exact -c 32 --mem=56G`, as the recorded allocation 58911473 did.
- **K-T1 checks** (`tools/kt1_readout.py`, output `receipts/kt1.json`):

| arm | products | `xsec_flat`, `xtrue_flat`, `shape` bitwise | max \|Δ xsec\| | code, inputs, experiment metadata equal |
|---|---:|---|---:|---|
| C0 | 8 | 8 / 8 | 0 | yes |
| C1 | 1 | 1 / 1 | 0 | yes |
| G1 | 1 | 1 / 1 | 0 | yes |
| G2 × 4 | 4 | 4 / 4 | 0 | yes |
| G2 × 2 | 2 | 2 / 2 | 0 | yes |

## 3. Per-arm timings

`seconds_unfold` is the recorded quantity: pseudo construction, the K = 5 unfold and the refinement. It excludes
`seconds_load`, which was 18.1–18.9 s in every task. Step wall times come from `sacct` (`receipts/sacct.txt`).

| arm | node | concurrent × CPUs | `seconds_unfold` median (min–max) | step wall (sacct) | unfolds per node-h | node-h per unfold |
|---|---|---|---:|---:|---:|---:|
| recorded, 423 products | CPU | 8 × 32 | 293.973 (max 348.522) | — | 97.97 | 0.010207 CPU |
| recorded, this unit | CPU | 8 × 32 | 338.105 | — | 85.18 | 0.011740 CPU |
| **C0** | CPU (nid004458) | 8 × 32 | **533.06** (532.09–533.75) | 647–648 s | 54.03 | 0.018509 CPU |
| **C1** | CPU (nid004144) | 1 × 32 | **420.12** | 557 s | 8.57 | 0.116701 CPU |
| **G1** | GPU (nid003085) | 1 × 32 | **408.79** | 526 s | 8.81 | 0.113553 GPU |
| **G2 × 4** | GPU (nid002304) | 4 × 32 | **411.25** (406.35–425.52) | 507–528 s | **35.02** | **0.028559 GPU** |
| G2 × 2 | GPU (nid001589) | 2 × 32 | 403.79 (403.34–404.23) | 504 s | 17.83 | 0.056082 GPU |

How the columns are computed: unfolds per node-h = n_concurrent × 3600 / median; node-h per unfold = median / 3600 /
n_concurrent. For example, G2 × 4 is 411.2535 / 3600 / 4 = 0.028559.

- **Packing costs nothing on a GPU node.** 1, 2 and 4 concurrent tasks take 408.8, 403.8 and 411.3 s. So 4 × 32, the
  node's full 128 CPUs, is the efficient packing there.
- **Today's unit is slower than recorded, on both node types.**
  - **Alone:** 420.12 s on a CPU node (C1) and 408.79 s on a GPU node (G1). Both are about 1.4× the recorded packed
    median of 293.973 s, and above the recorded maximum of 348.5 s.
  - **Packing:** 8 × 32 on a CPU node adds 1.27× (C0 533.06 / C1 420.12). On a GPU node, 1, 2 and 4 tasks take 408.8,
    403.8 and 411.3 s, so packing adds nothing. 4 × 32, the node's full 128 CPUs, is the efficient packing there.
  - The products are bitwise equal throughout, so the work was identical; only the speed differed.
- **The recorded 423 are consistent across their three allocations.** Median, min and max `seconds_unfold` by
  allocation, read from the product metadata:
  - 58904837: 40 products, 293.8 (272.1–320.8);
  - 58911473: 201 products, 292.7 (269.3–343.6);
  - 58920424: 182 products, 302.0 (273.6–348.5).
- **Checked, and not the cause:**
  - The environment is unchanged since before the recorded runs. No file in `root_6_28` is newer than 2026-09-20 except
    fontconfig caches and `lib/modules.timestamp`. LightGBM 4.6.0 dates from 2026-05-21, scikit-learn from 2026-01-09
    and NumPy from 2025-12-18.
  - The code and inputs are the same, by sha256.
- **Frequency, as read on the C1 node** (nid004144, `receipts/runs/c1/freq.log`):
  - governor `performance`, driver `acpi-cpufreq`;
  - `cpuinfo_max_freq` 3,530,493 kHz, `scaling_max_freq` 2,450,000 kHz, `scaling_min_freq` 1,500,000 kHz, boost 1;
  - over the 18 samples during the step, the 32 busiest CPUs read a median 2,450 MHz in 12 and 3,143–3,144 MHz
    in 6.
  - What the recorded nodes ran at in September is not on the record, so this test cannot say whether a frequency or
    power setting changed since.
  - sacct `AveCPUFreq` is unusable for every job, old and new: per-step values read from 3K to 762K.
  - lscpu at C0's start printed "CPU(s) scaling MHz: 69%".
  - Node power from sacct `ConsumedEnergyRaw`: C0 about 437 W (8 tasks), C1 about 297 W (1 task), and the recorded
    58911473 about 510 W (8 steps).
- **Untested possibilities for the 1.43× gap:**
  - a change in node frequency or power policy since 2026-09-26;
  - the recorded steps running mixed, staggered work, where today's tasks were identical;
  - the particular nodes.
- **For pricing, this means:** the gbdt §9 figures from 293.973 s are optimistic against today's machine by about
  1.4×, on CPU and GPU nodes alike.
- **Ratios of node-h per unfold,** G2 × 4 against the CPU node:
  - **2.80×** against the recorded 293.973;
  - **1.54×** against today's C0 (both measured today, packed).
  - The earlier unmeasured "roughly 2×" estimate lies between them.
  - The like-for-like figure is today's 1.54×: per task the two node types take about the same time alone (C1 420 s,
    G1 409 s), and a GPU node holds 4 tasks where a CPU node holds 8, at a 1.27× packing cost.

## 4. The gbdt §9 table, re-priced

The form is `gbdt/REPORT.md:416-427`: node-h per unfold × 1.25 (packing) × 4 cases × 4,404 experiments × U unfolds per
experiment; admitted = subtotal / 0.8. The common factor is 1.25 × 17,616 = 22,020.

| unfolds per experiment (procedure) | CPU, recorded 293.973 (8 × 32): subtotal / admitted | CPU, C0 today (8 × 32) | CPU, C1 today (1 × 32, unpacked) | **GPU, G2 × 4** |
|---|---:|---:|---:|---:|
| 1 (central only, no interval) | 225 / 281 | 408 / 509 | 2,570 / 3,212 | **629 / 786** |
| 31 (central + 30 bootstrap) | 6,968 / 8,710 | 12,635 / 15,793 | 79,662 / 99,578 | **19,495 / 24,369** |
| 101 (central + 100 bootstrap, the s5e R recipe) | 22,701 / 28,377 | 41,164 / 51,455 | 259,544 / 324,430 | **63,516 / 79,395** |
| 288 (+ 187 refit flux/detector/interaction universes) | 64,733 / 80,916 | 117,379 / 146,724 | 740,087 / 925,109 | **181,116 / 226,395** |

The C1 column prices one task per CPU node, as asked. It is not a campaign packing: C0 is the CPU campaign figure.

Arithmetic for G2 × 4:
- per U: 0.028559 × 22,020 = 628.88;
- U = 31: 628.88 × 31 = 19,495, and / 0.8 = 24,369;
- U = 288: 628.88 × 288 = 181,116, and / 0.8 = 226,395.

The recorded column reproduces the published table exactly. As in §9, these exclude sample construction, identity
work, the I1/I2 confirmation, retries and review.

**Against the GPU pool:** `m3246_g` had 42,727.4 node-h left on 2026-10-23 (ASSIGNMENT.md). The pool is used at
about 860 node-h a day (DECISION-20261019 §1b, as of 10-19).
- The statistical-only recipe (24,369 admitted) is 57% of what is left.
- The 101-unfold recipe (79,395) and the 288-unfold recipe (226,395) exceed the whole pool.

## 5. G3: LightGBM GPU training

| where | `device_type="cuda"` | `device_type="gpu"` (OpenCL) |
|---|---|---|
| login10 (A100, `/etc/OpenCL/vendors/nvidia.icd`), before the jobs | LightGBMError "CUDA Tree Learner was not enabled in this build. Please recompile with CMake option -DUSE_CUDA=1" | segmentation fault in `Booster.__init__` (`basic.py:3661`), rc 139 |
| nid003085 (G1 job, steps 60145930.0 and .1, one A100 each) | the same LightGBMError (`receipts/runs/g1/probe_cuda-60145930.log`) | segmentation fault; step CANCELLED, exit 0:11 (`probe_gpu-60145930.log`) |

- The environment is LightGBM 4.6.0 in `root_6_28` (`lib_lightgbm.so` sha256 `6a12e1a7b138…`). The library contains
  the OpenCL learner (boost::compute symbols) but has no `NEEDED` entry for `libOpenCL`.
- One correction to the job log: the line "probe gpu rc=0" is the status of the shell redirect, not of the step. sacct
  and the probe log show the segfault.

**What a CUDA build would take** (not done; the director ruled no rebuild now). Per LightGBM v4.6.0's installation
guide and its Python-package README:
- **Source:** LightGBM v4.6.0, the same version as the environment.
- **Build:** `cmake -B build -S . -DUSE_CUDA=ON` and `cmake --build build`, or for the Python package
  `pip install lightgbm==4.6.0 --no-binary lightgbm --config-settings=cmake.define.USE_CUDA=ON`. The guide requires
  gcc (or Clang), CMake and CUDA, and an NVIDIA GPU of compute capability ≥ 6.0 (the A100 is 8.0).
- **Toolchain on Perlmutter:** modules `cudatoolkit` 12.2, 12.4, 12.9, 13.0 and 13.2, and `cmake` 3.24.3 and 3.30.2,
  are available.
- **Where:** a new scratch-only conda environment on `$PSCRATCH`, never `root_6_28`, so the analysis environment and
  its recorded `lib_lightgbm.so` stay unchanged.
- **Then:** use `device_type="cuda"` in the classifier parameters.
- **What it would not give:** the frozen configuration's bitwise controls. The deterministic CPU path is what K-T1
  verifies, and GPU-trained trees are not expected to reproduce it. As the director notes, this matters only if a
  campaign is ever justified.

## 6. Compute and storage

| | charged | cap |
|---|---:|---:|
| CPU (`m3246`, debug) | 0.3394 node-h (60145929 657 s; 60151381 565 s) | 0.5 |
| GPU (`m3246_g`, gpu_debug) | 0.4644 node-h (60145930 623 s, 60145931 535 s, 60145932 514 s) | 1.0 |

- Billing is from `sacct` AllocTRES: 256 per CPU node, 128 per GPU node; elapsed time × 1 node.
- The GPU jobs were submitted with `-q debug`, and Slurm ran them under `gpu_debug`. No premium QOS was used. Every
  job ran under 11 minutes.
- Phase-1 grant: GPU now 0.4644 of 3.
- Storage: only `/pscratch/sd/j/josephrb/gpu-timing-20261023/` (the deploy clone is 3.3 GB). Nothing was written to
  CFS.

## 7. What was not done

- **No G3 timing.** There is no usable GPU device in the environment, and no rebuild was made.
- **No identification of the cause** of today's 1.4× gap to the recorded time (§3). C1 separated packing (1.27×,
  CPU only) from the rest, but the rest is not explained.
- **The recorded sample.** One unit was timed per task, all the same nominal experiment. The 423 recorded products
  include bootstrap replicas and other experiments. Their per-unit times spread from 269 to 349 s, so the unit is
  typical of them on the recorded runs.
- **No claim, campaign or outward act.**
