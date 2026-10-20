# A7 decision-boundary margins: the ten frozen joint-5D tests

**By** the measurement session, 2026-10-19. **DESCRIPTIVE, not a re-grade (A7 stands).**
**Job** 60023575 (Perlmutter, `-q debug -C cpu -N 1 -c 4 -t 00:30:00`). It ran on debug because shared was draining
for maintenance. sacct: COMPLETED, 0:0, ElapsedRaw 93 s, AllocTRES `billing=256,cpu=256,node=1`.
**Charge** 93 × 256/256/3600 = **0.0258 CPU node-h**. Not premium, 0 GPU, nothing written to CFS.
**Code** `measurement-paper/phase1/a7margins/a7margins.py`, `a7margins_job.sh`.
**Output** `a7margins.json` (sha256 `f0960dc6…`, the same on pscratch and here) and the job log `a7margins-60023575.log`.
Cluster outputs are under `/pscratch/sd/j/josephrb/measurement-paper/phase1/a7margins/`.

**CITABLE FOR:** where each frozen A7 decision sits relative to the boundary of A7's own rule, holding the frozen
Holm order fixed.
**NOT CITABLE FOR:** a re-grade, a new decision, or any claim outside the frozen family.

## Frozen inputs and environment

- **Code copies.** `s5p_joint.py` `51d3424f`, `s5p_inference.py` `f42e0e20`, `s5p_stage1_inspect.py` `b6aee05d`
  (git blobs equal to `4f5a613f`). `mp3b_eval.py` `91a663db` is the staged MP3-B copy, reused for `kstar`,
  `t_critical`, `same` and `sha256`; that exact blob is vendored at
  `measurement-paper/phase1/a7margins/vendored/mp3b_eval.py`, since the MP3-B working copy has since changed.
- **Inputs.** `design.json` `5c30ba87`, `s5c contract.json` `28125d96`, `joint-evaluate.json` `daf92651`
  (sha256 `b9604502…`), and `V-s3v.npz` (checked against `design.v_sha256`).
- **Verification.** Each file's blob was verified on both sides. The job prints `git hash-object` and sha256, and
  asserts each module's `__file__` (all of them are in `…/a7margins/code/`).
- **Environment.** `root_6_28`: Python 3.11.14, numpy 1.26.4, scipy 1.16.3.

## Controls (run first; the margins are computed only if they pass)

1. **Each null.** All five nulls were recomputed with `s5p_joint.test_null`, and each equals its
   `joint-evaluate.json` entry **bitwise**: T_obs, every variant's p, k, median and SD, the claims, robust, and jitter
   p. The κ_robust = 3 M1 nulls reproduce the frozen `robustness_variants` **bitwise**. B: MnvTune 1365, GENIE CV
   1366, GENIE MEC 1343, NuWro 1751, GiBUU 1351.
2. **The family.** `holm_determined` on the *recomputed* claims reproduces `decisions` and `decisions_robust_kappa`
   **bitwise**. `holm` reproduces `holm_point` bitwise. No Clopper–Pearson path needed the last-ulp tolerance.
3. **NuWro shape against the MP3-B values.** Threshold 0.05, k* 69, B 1751, T_crit 8672.55, T_frozen 9660.01,
   margin 1.11 null SD. **All reproduced.**
4. **Per-test checks, all ten tests in both families. All pass.**
   - The recomputed claim k at T_obs equals the frozen k.
   - The c = 0 null median and SD equal the frozen record exactly.
   - The threshold equals the frozen `threshold`.
   - Boundary direction: at T = T_crit the claim k is k_max + 1, with the CP upper end ≥ threshold. At
     nextafter(T_crit) the claim k is ≤ k_max, with the upper end below the threshold.

## Definitions (from the frozen code)

- **Holm order.** The order is by claim p, with Python's stable sort. **Ties** (GENIE CV, MnvTune, GiBUU and GENIE MEC
  each have total p = shape p) are broken by the design's insertion order, which puts total before shape. Position i
  (1-based) is compared with th = α/(m − i + 1), with α = 0.05 and m = 10.
- **k_max.** The largest k whose 95% CP upper end is below th. A test is REJECTED iff its claim k ≤ k_max.
- **Claim k.** The largest #{null ≥ T} over the claim variants: c ∈ {0, 0.5, 1}, plus m1 ± 2 for every null except
  MnvTune, which has no M1 shift.
- **T_crit (claim variants).** The maximum over those variants of the (k_max+1)-th largest null T. A test is
  rejected iff T > T_crit.
- **T_crit (unshifted).** The same quantity from the c = 0 null alone.
- **What crossing means.** Every test crosses into **"undetermined"** (the CP interval straddles th), not into "not
  rejected".
- **SD.** SD is the c = 0 null's `np.std`, **ddof 0**, which is how `s5p_joint` records `null_T_*_sd`. The margins
  are (T_obs − T_crit)/SD and (T_obs − median₀)/SD. The last is the "margin over median", the quantity the M2-AUDIT
  Q4e figures used.
- **ORDER HELD FIXED.** Each margin moves one test's T with its Holm position frozen. A lower T raises its p and could
  re-order the family. See "Re-sorted crossing" below.
- **Inherited.** No test was inherited. All ten are rejected and `holm_determined` never stopped, so every decision
  is made at the test's own position. The "margin at the stop position" therefore does not arise.

## Primary family (`decisions`; claim variants 0, 0.5, 1, m1±2)

| # | test | th | B | k_max | T_obs | T_crit claim (bind) | T_crit c=0 | SD₀ | median₀ | margin claim | margin c=0 | margin/median | decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | NuWro total | 0.005 | 1751 | 3 | 7427.14 | 6953.94 (m1+2) | 6826.81 | 174.29 | 6323.86 | **2.72** | 3.44 | 6.33 | rejected |
| 2 | GENIE CV total | 0.005556 | 1366 | 2 | 1812.66 | 780.11 (m1+2) | 704.01 | 58.43 | 527.74 | **17.67** | 18.97 | 21.99 | rejected |
| 3 | GENIE CV shape | 0.00625 | 1366 | 2 | 1086.14 | 962.76 (m1+2) | 883.41 | 95.04 | 582.44 | **1.30** | 2.13 | 5.30 | rejected |
| 4 | MnvTune total | 0.007143 | 1365 | 3 | 2852.30 | 103.99 (1.0) | 103.95 | 13.55 | 49.21 | **202.78** | 202.78 | 206.82 | rejected |
| 5 | MnvTune shape | 0.008333 | 1365 | 4 | 630.88 | 107.94 (1.0) | 107.83 | 14.69 | 48.66 | **35.60** | 35.60 | 39.63 | rejected |
| 6 | GiBUU total | 0.01 | 1351 | 6 | 2866.96 | 2169.65 (m1+2) | 2027.69 | 88.77 | 1791.37 | **7.86** | 9.45 | 12.12 | rejected |
| 7 | GiBUU shape | 0.0125 | 1351 | 8 | 4013.30 | 2946.25 (m1+2) | 2748.93 | 298.42 | 1974.99 | **3.58** | 4.24 | 6.83 | rejected |
| 8 | GENIE MEC total | 0.016667 | 1343 | 13 | 1647.12 | 585.92 (m1+2) | 508.61 | 38.72 | 406.01 | **27.41** | 29.40 | 32.05 | rejected |
| 9 | GENIE MEC shape | 0.025 | 1343 | 22 | 868.59 | 679.78 (m1+2) | 605.04 | 67.70 | 449.62 | **2.79** | 3.89 | 6.19 | rejected |
| 10 | NuWro shape | 0.05 | 1751 | 69 | 9660.01 | 8672.55 (m1+2) | 8586.92 | 890.03 | 7110.29 | **1.11** | 1.21 | 2.86 | rejected |

- The frozen claim k is 0 for every test except NuWro shape, where it is 1.
- **A second scale.** The claim-variant SD (ddof 0) of the binding variant gives margins of 2.66, 15.35, 1.22,
  202.61, 35.56, 7.59, 3.47, 23.90, 2.63 and 1.11. The SD of the pooled claim variants is in the JSON.

## κ_robust = 3 family (`decisions_robust_kappa`; claim variants plus m1±3; report only in s5p)

The order, thresholds, B, k_max, SD₀, median₀, T_crit at c = 0 and the margin over the median are the **same as
above**. The robust claim k equals the primary claim k everywhere except NuWro shape, where it is 2.

| # | test | T_crit robust (bind) | margin robust (SD₀) | margin (binding-variant SD) | decision |
|---|---|---:|---:|---:|---|
| 1 | NuWro total | 7054.73 (m1+3) | **2.14** | 2.06 | rejected |
| 2 | GENIE CV total | 863.21 (m1+3) | **16.25** | 12.79 | rejected |
| 3 | GENIE CV shape | 1022.51 (m1+3) | **0.67** | 0.61 | rejected |
| 4 | MnvTune total | 103.99 (1.0) | **202.78** | 202.61 | rejected (no M1 shift: identical to primary) |
| 5 | MnvTune shape | 107.94 (1.0) | **35.60** | 35.56 | rejected (identical to primary) |
| 6 | GiBUU total | 2268.83 (m1+3) | **6.74** | 6.35 | rejected |
| 7 | GiBUU shape | 3062.97 (m1+3) | **3.18** | 3.04 | rejected |
| 8 | GENIE MEC total | 648.75 (m1+3) | **25.79** | 20.67 | rejected |
| 9 | GENIE MEC shape | 732.29 (m1+3) | **2.01** | 1.83 | rejected |
| 10 | NuWro shape | 8757.04 (m1+3) | **1.01** | 1.01 | rejected |

**Smallest margins:** NuWro shape (1.11 primary, 1.01 robust) and GENIE CV shape (1.30 primary, **0.67 robust**,
the smallest of all twenty).

## Re-sorted crossing (labelled extra: `holm_determined` re-sorts; the other nine tests stay at their frozen claims)

- **What happens.** When a test's k rises, its p rises and it moves to the last position, with threshold 0.05. It
  stays rejected until k_max(0.05) + 1: k = 70 at B = 1751, 53 at B = 1365 or 1366, and 52 at B = 1343 or 1351.
- **Effect on the family.** In every case, the first change anywhere in the family is that test itself becoming
  "undetermined". No other decision changes first.
- **Re-sorted margins, primary family** (SD₀): NuWro total 4.03, GENIE CV total 18.90, GENIE CV shape 2.52, MnvTune
  total 204.74, MnvTune shape 37.56, GiBUU total 8.65, GiBUU shape 4.33, GENIE MEC total 28.04, GENIE MEC shape 3.25,
  NuWro shape 1.11 (already last).
- **Re-sorted margins, κ = 3 family:** 3.53, 17.51, 1.90, 204.74, 37.56, 7.58, 3.93, 26.49, 2.48, 1.01.
- **Reading.** The fixed-order margins in the two tables above are therefore the stricter reading for positions
  1–9.

**Reproduce:** `cd /pscratch/sd/j/josephrb/measurement-paper/phase1/a7margins && sbatch code/a7margins_job.sh`
(code/ and inputs/ are staged; out/ must not exist).
