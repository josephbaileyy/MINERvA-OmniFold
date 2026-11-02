# REPORT 1B staged method coverage, stage 0: rule K reads PASS, κ in the window in 16 of 16 cells (2026-11-02)

**By** the measurement session `coverage-5b`, for `coverage-5b-audit` and the director, and through the director for
Joseph.

**Under:**
- [`FD-1B-STAGED-DECLARATION.md`](FD-1B-STAGED-DECLARATION.md) (revision 2) §2, bound by
  [`FD-1B-STAGED-BINDING-1.md`](FD-1B-STAGED-BINDING-1.md) (#667) at M = `b3705d43`;
- [`FD-1B-MODED-DECLARATION.md`](FD-1B-MODED-DECLARATION.md) §2–§9, carried byte-identical from #655 at `55435ec0`;
- `DECISION-20261101-joseph-1b-staged-method-coverage.md` (#663).

**The reading: rule K is PASS.** κ = √(Dnom / A_unc) lies in [0.9, 1.1] in all 16 reporting cells, from 0.9757 (R01)
to 1.0570 (R08), with median 0.9994. The nearest approach to an edge is 0.043, in R08.
- **What it shows** (#655 §3.5, §6): at the nominal truth, the full universe's second-order departures at ±1σ under
  the swap are below the window. That covers its truth reweight, completeness and background. Closure fixes κ = 1 at
  first order, so this is the expected outcome.
- **The gate (binding 1, ruling 2).** Stage 1 may proceed only after three things: `coverage-5b-audit` acknowledges
  this report, binding 2 binds §11's code (amendment 1, #673), and Joseph is told. None of these has happened yet,
  and nothing has been submitted for stage 1.
- **Every control passed** (§3). Nothing read INVALID, either for rule K or for the grid part.
- **The grid check** (descriptive, §5): B does not depend on the grid, and the sub-cell hypothesis is not supported
  for it. C depends on the grid, and the hypothesis is supported for it.
- **Cost:** 3.12 node-h against the 5.5 node-h cap (§1).
- **Deviations:** four, in §6. No access time moved, either on the 272 sources or in any of the 104 atime sidecars.
- **HPSS:** not copied yet. HPSS was in maintenance at every attempt. Both archives stay on pscratch under their
  recorded digests (§1, §6). By the director's ruling, HPSS does not gate.

**MEASURES:** rule K on κ per cell, I2's F_truth beside it, the grid readings with their occupancy, and the
descriptive Dnom blocks. All are labelled DERIVATION.

**CANNOT SUPPORT, whatever the outcome** (#655 §11):
- coverage, in either direction;
- that the toy realizes S1's block M, because κ is read at the nominal truth (§3.5);
- anything about the flux and detector groups, or about the correlation structure;
- that S1's block is right or wrong.

Gate D's FAIL, the diagnosis, I0, I2 and every claim and number in the paper are unchanged.

## 1. What ran

| connect | when (UTC, 2026-11-02) | what | result |
|---|---|---|---|
| 25 | 06:44:46–06:44:49 | `stat` of every input, `iris`, `hpssquota` | all present |
| 26 | 06:45:34–06:46:35 | fresh clone at M, the task tables, D-0's submission | job 60678921 |
| 27 | 07:09:41–about 08:14 (killed) | after D-0: ledger, lanes, products, `walls`, controls, atime; HPSS | walls PASS; the HPSS step hung and was killed (§6.2) |
| 29 | 10:52:15 | HPSS retry for `stage0-d0.tar` | STOP: maintenance had not cleared |
| 28 | 10:53:59–10:54:03 | the bulk's submission, after walls PASS and the audit's written acknowledgement | jobs 60683107, 60683108 |
| 30 | 12:22:23–12:23:57 | after the bulk: ledger, lanes, products, atime, **the readout**, `stage0.tar`, an HPSS probe | rule K PASS; HPSS still in maintenance |
| 31 | 12:25:44 | read-only: the readout log, `walls-d0.json`, the tables' digests, `SHA256SUMS` | — |

- **Deploy:** `$W/deploy` is a fresh clone detached at M `b3705d4360520612842c4c819ac6f51041f274f2`, with empty
  porcelain at connects 26 and 28. `fd_1b_moded.py` is `420088436948d942…` in every product and in the readout.
  `fd_1b_inv.py` is `71b3903a…`.
- **Jobs.** Every job ran on regular CPU nodes (`-q regular -C cpu`) with `--exclusive --no-requeue`, and every job
  and step ended COMPLETED with exit code 0:

  | job | name | node-h | elapsed | time limit | steps |
  |---|---|---:|---|---|---|
  | 60678921 | fd1b_d0 | 0.303 | 00:18:11 | 01:00:00 | 8 |
  | 60683107 | fd1b_d_n0 | 1.432 | 01:25:55 | 02:15:00 | 8 lanes, 48 items |
  | 60683108 | fd1b_d_n1 | 1.387 | 01:23:12 | 02:15:00 | 8 lanes, 48 items |
  | **total** | | **3.122** | | 5.5 node-h reserved, the cap | 104 items |

  The node-h figures are elapsed × 1 node **(arithmetic)**.
- **Products:** 104 of 104 in `$W/stage0/unf`, with no partial files:
  - Dnom: 68, the CV and the 67 interaction universes;
  - the grid check: 36, B and C on three grids for six universes.

  `seconds_unfold` has median 776.7 s and maximum 964.5 s. `peak_rss_kib` has maximum 21,734,248.
- **Walls (D-0):** PASS, with maximum 964.464 s and maximum 21,668,912 KiB (`walls-d0.json`, `a832b726…`).
- **The readout:** `fd_1b_moded.py readout` on login37 at `nice -n 19`, rc 0, about 1 s. It wrote
  `$W/stage0/readout.json`, 61,825 bytes, sha256 `05be73ee363c5263ffb5db14ad23a0de1efa27c7d755bad804bddd677d9ca5bb`.
  It read `i2.json` as `a9d3dc9c…` and `i0.json` as `9a4142d3…`, which are the committed receipts' digests.
- **The archives:**
  - `$W/stage0-d0.tar` is `a97f366c…`, unchanged since connect 27.
  - `$W/stage0.tar` is `51747c959a9b63ab021183e4ab0c5988e333d39723d06184771f858c123a512a`. It holds `stage0/`,
    `tables/` and `logs/`.
  - Neither is on HPSS yet (§6.2).

`$W` is `/pscratch/sd/j/josephrb/fd-1b-staged-20261102`. The receipts are in
[`fd/receipts-1b/staged/stage0/`](fd/receipts-1b/staged/stage0/):
- each connect's script and transcript;
- the readout;
- `SHA256SUMS`, covering the 104 products, the readout, the walls JSON and both archives;
- the table generator, in `tables/`;
- `DEVIATIONS.md`.

## 2. Rule K, per cell

A cell is "in" if its value lies in [0.9, 1.1], edges inside. The last two columns are descriptive (#655 §4).

| cell | κ | κ in window | F_truth (I2) | F_truth in window | √(raw shift / A_unc) | √(truth spread / A_unc) |
|---|---:|---|---:|---|---:|---:|
| R00 | 1.0004 | in | 0.536 | **out** | 19.67 | 19.55 |
| R01 | 0.9757 | in | 0.695 | **out** | 5.82 | 5.02 |
| R02 | 0.9950 | in | 0.568 | **out** | 7.37 | 7.88 |
| R03 | 0.9931 | in | 0.872 | **out** | 2.42 | 2.93 |
| R04 | 1.0210 | in | 0.559 | **out** | 29.46 | 29.03 |
| R05 | 0.9882 | in | 0.632 | **out** | 3.65 | 3.04 |
| R06 | 0.9987 | in | 0.858 | **out** | 7.43 | 7.58 |
| R07 | 0.9916 | in | 0.844 | **out** | 2.60 | 3.09 |
| R08 | 1.0570 | in | 0.999 | in | 14.56 | 14.24 |
| R09 | 1.0062 | in | 0.691 | **out** | 5.58 | 5.33 |
| R10 | 0.9968 | in | 0.569 | **out** | 8.19 | 8.85 |
| R11 | 1.0008 | in | 0.588 | **out** | 8.19 | 8.96 |
| R12 | 1.0001 | in | 0.674 | **out** | 16.49 | 15.87 |
| R13 | 1.0367 | in | 0.527 | **out** | 8.39 | 9.31 |
| R14 | 1.0056 | in | 0.767 | **out** | 6.13 | 5.58 |
| R15 | 0.9974 | in | 0.739 | **out** | 10.84 | 11.24 |

- **κ: 16 of 16 in.** `rule_K` reads `{"verdict": "PASS", "cells_in_window": 16, "above": [], "below": []}`.
- **F_truth: 1 of 16 in (R08),** as I2 measured. κ and F_truth are different objects (#655 §3.5).
  - κ compares the toy's error block with S1's mechanism, both at the nominal truth.
  - F_truth is the gap in S1's mechanism between the nominal pseudo-data and the data.

  κ's PASS leaves F_truth's reading as it was.
- **R00 and R05** are graded as every other cell. κ tests the interaction group only, which in gate D carried 0.565 of
  ρ_c² − 1 in R00 and 0.359 in R05 (I2 report §3).
  - The remainder, 0.435 in R00 and 0.641 in R05 **(arithmetic)**, lies in other groups, which neither I2 nor κ
    decomposes.
  - At R05, I2's H3 cell, κ is 0.9882 and F_truth is 0.632.
- **The raw-shift and truth-spread columns** are 2.4–29.5 times A_unc, and they track each other. This is what
  ruling 1 expected (#655 §2): the raw shift is mostly the universe's own truth movement, so the rule reads the
  error e(u) and not the shift.
- **The bands.** The 33 interaction bands' diagonals sum to Dnom exactly (maximum relative difference 0). By median
  share of Dnom across the cells, the largest are:

  | band | median share |
  |---|---:|
  | MaRES | 0.152 |
  | MvRES | 0.067 |
  | Rvn2pi | 0.048 |
  | MFP_pi | 0.047 |
  | FrAbs_pi | 0.032 |

## 3. Controls (#655 §8)

All of these passed. Each one raises `Invalid` or `Refusal` in the code when it fails, and none was raised:

| control | where it is enforced | result |
|---|---|---|
| Dnom at CV equals the derivation CV product's `xsec_flat` bitwise | `readout`; also printed at connect 27 | equal |
| S1's interaction diagonal from the staged assembly equals `i2.json`'s M bitwise | `readout` | equal |
| one code and one input set across the products: code, input, background and pins digests, configuration, iterations, estimator seed | `readout`, `ONE_CODE_KEYS` | one value each |
| every product names its own mode, grid, universe and truth | `d_blocks`, `grid_check` | all 104 |
| every universe's weight files carry the pins file's digests | `run_unfold`, per item | all 104 |
| the grid part: nominal-grid B and C equal I2's products bitwise, and occupancy is identical across the six universes | `grid_check` | equal; identical (`verdict: READ`) |
| reads with `O_NOATIME`; an atime sidecar per item | every unfold | 104 sidecars, one per item (8 from D-0, 96 from the bulk), `moved` empty in all |
| `stat` of the 272 sources: atime, mtime, size | connects 28 and 30, before the bulk, after it and after the readout | unchanged |

The Ddl controls do not apply, because the option was excluded from stage 0 (binding 1, ruling 1).

## 4. The grid check (#655 §5; descriptive, no outcome role)

**Occupancy (M2).** It is identical across the six universes in every mode and grid, as the control requires:

| grid | factor cells | occupied | mean rows per occupied cell | fraction of rows alone | largest per-cell fraction alone |
|---|---:|---:|---:|---:|---:|
| coarse | 3,584 | 1,056 | 31,104.5 | 4.3 × 10⁻⁷ | 6.8 × 10⁻⁶ |
| nominal | 65,856 | 10,694 | 3,071.5 | 1.2 × 10⁻⁵ | 1.1 × 10⁻⁴ |
| fine | 2,107,392 | 116,972 | 280.8 | 3.4 × 10⁻⁴ | 2.3 × 10⁻³ |

- No reporting cell is construction-limited on any grid. The threshold is more than half of a cell's truth-passing
  rows alone, and the largest observed fraction is 0.0023. So all 16 cells are counted on both grids, in both modes.
- The fraction of rows with k_wr/k_wt ≠ 1 is 0.976–0.977 for every universe.

**γ = √(S_coarse / S_nominal) and φ = √(S_fine / S_nominal)**, over the six universes. Bold marks a value outside
[0.9, 1.1]:

| cell | B γ (coarse) | B φ (fine) | C γ (coarse) | C φ (fine) |
|---|---:|---:|---:|---:|
| R00 | 1.050 | 0.995 | **1.472** | **0.743** |
| R01 | 0.997 | 1.089 | **0.776** | 1.070 |
| R02 | 1.050 | 1.004 | **1.122** | **0.892** |
| R03 | 1.020 | 1.019 | 1.072 | 0.922 |
| R04 | 1.071 | 0.974 | **1.592** | 0.953 |
| R05 | **1.399** | **0.878** | 1.024 | 0.908 |
| R06 | **1.101** | 1.005 | 1.100 | 0.994 |
| R07 | 1.046 | 1.027 | **1.108** | **0.899** |
| R08 | **0.895** | 0.984 | **1.601** | **1.157** |
| R09 | 1.008 | 1.091 | 1.051 | **0.782** |
| R10 | 1.061 | 0.975 | **1.516** | **0.842** |
| R11 | 0.982 | 0.975 | 0.958 | 1.043 |
| R12 | 1.052 | 0.966 | **3.178** | **0.878** |
| R13 | 1.021 | 0.963 | **1.373** | **0.880** |
| R14 | 1.036 | **1.153** | 1.024 | **0.866** |
| R15 | **1.240** | 0.951 | **1.509** | 0.910 |

B's R06 γ is 1.1009, out; C's R06 γ is 1.0999, in. The readout's own counts agree with the table.

**The fixed reading:**

| mode | out of window (coarse / fine) | γ > 1.1 (coarse) | φ < 0.9 (fine) | depends on the grid | supports the sub-cell hypothesis |
|---|---|---:|---:|---|---|
| B (response-only) | 4 / 2 of 16 | 3 | 1 | no | no |
| C (cell-mean truth reweight) | 10 / 9 of 16 | 9 | 8 | yes | yes |

- **The declared qualification applies:** φ < 0.9 is still expected partly from construction as occupancy falls. The
  coarse leg is the one less exposed to it.
- **For the note's label for B** (decision item 1), as the declaration routes it: on these six universes, B's spread
  does not move with the fine-cell grid, and C's does.
- **This report draws no label from it.** The grid check has no outcome role.

## 5. What this does not change

- **The covariance, the toys and the window** are unchanged, as are gate D, M_d, I0 and I2. No readout here feeds
  back into any of them (#655 §1).
- **Stage 1's design and code** are as in amendment 1 (#673), which awaits the audit and binding 2. This report
  changes nothing in it.

## 6. Deviations

These are also in [`DEVIATIONS.md`](fd/receipts-1b/staged/stage0/DEVIATIONS.md). Items 1–3 are the ones the
director's ruling of 2026-11-02 asked to be recorded.

1. **The D-0 readout was routed late.**
   - D-0 completed at 07:07Z, and walls read PASS at connect 27 (07:09Z).
   - The readout reached `coverage-5b-audit` and the director at about 08:17Z. I held it while connect 27's HPSS step
     hung, when it should have gone as soon as the gate's data existed.
   - Nothing was submitted in between. The director asked for it.
2. **The HPSS step of connect 27 was killed, and HPSS has not been reached since.**
   - `hsi -q mkdir -p fd-1b-staged-20261102` hung for 65 min with HPSS in maintenance. I killed it and its connect
     shell by PID at about 08:14Z, so no put, hashcreate, hashverify, retrieval or cmp ran.
   - Every later `hsi` call is under `timeout`. The retries at connects 29 and 30 found maintenance still on.
   - `stage0-d0.tar` (`a97f366c…`) and `stage0.tar` (`51747c95…`) stay on pscratch. Both are put, verified and
     retrieved when maintenance clears, and `stage0-d0.tar` is checked against its digest at the put (the
     director's ruling 1).
   - The products date from 2026-11-02, so their pscratch exposure begins about 2026-12-28 **(arithmetic: plus 8
     weeks)**.
3. **The table generator ran uncommitted.** This is the audit's condition on its D-0 acknowledgement (#667
   issuecomment-6575337812), which the director made binding.
   - `make_stage0_tables.py` (sha256 `3da6aafe1a763e179bf73abdb36bf3a9ec0dd07a32936740d657b2ca1f615884`) was written
     into `$W/tables` by connect 26's heredoc and run from there. It was in neither the deploy nor any origin ref,
     against #655 §9.2's "a committed generator".
   - **It is committed at that digest in this PR** ([`tables/make_stage0_tables.py`](fd/receipts-1b/staged/stage0/tables/make_stage0_tables.py)).
     Connect 31 re-measured the cluster copy at the same digest.
   - The audit verified the tables' contents directly, so the bulk's item set does not rest on the generator.
4. **A unit nit.** sacct's MaxRSS is in KiB, so D-0's step peaks are 21.7–23.1 GB (20.2–21.5 GiB). My D-0 readout
   said 21.2–22.5 GB. This has no effect on the gate, which reads `peak_rss_kib`.

## 7. For the audit and the director

1. **The audit's acknowledgement of this report** is the first of the three conditions in binding 1, ruling 2.
2. **Binding 2** of amendment 1 (#673) is the second. After it, the bound order is:
   - one connect for `stage-flux` and `receipt` (N1);
   - the tables;
   - the S1-0 submission, whose line goes to the director first.
3. **Joseph is told** of stage 0's PASS, through the director, which is the third.
4. **HPSS:** I retry when maintenance clears, either on its own or folded into stage 1's first connect.
