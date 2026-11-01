# REPORT 1B with 4A, stage 2: gate D FAIL, a STOP before any coverage toy (2026-11-01)

**By** the measurement session `coverage-5b`, for the director.

**Under:**
- [`FD-1B-STAGE2-DECLARATION.md`](FD-1B-STAGE2-DECLARATION.md), bound by
  [`FD-1B-STAGE2-BINDING.md`](FD-1B-STAGE2-BINDING.md) (#587);
- [`FD-1B-STAGE2-AMENDMENT-1.md`](FD-1B-STAGE2-AMENDMENT-1.md), bound by
  [`FD-1B-STAGE2-AMENDMENT-1-BINDING.md`](FD-1B-STAGE2-AMENDMENT-1-BINDING.md) (#615).

**MEASURES:** gate 1 and gate 2 of stage 2, and nothing more.
- Gate D read **FAIL**, which is the protocol's STOP before any coverage toy. Jobs 2b and 2c were not submitted.
- No coverage toy ran, so there is no coverage verdict, no 4A, and no statement about the reported intervals.

**CANNOT SUPPORT:** any claim about the coverage of the reported covariance, in either direction. Gate D's readout
is a DERIVATION, which sizes how far the fixed-truth toy mechanics reproduce S1's blocks. It is not a coverage
result. This report also proposes no repair: what follows a gate-D FAIL is the director's decision, to take to
Joseph.

**The matrix under test** has not changed: the reported C_total + C_resp of `fd_data_product.json` (`b79556f0…`),
as on `main` at `91a27ad1`, with no run-period block. It was not tested.
<!-- absence-ok: a scoping statement of what this stage's own jobs did; the STOP came before any coverage toy (§4.1) --> The lateral and normalization surrogates
carry 29.0 % of C_e's trace. The control would carry them but not test them, and only 71.0 % would be tested
through the estimator (binding ruling 2). Every readout under `run/score/` restates this.

## 1. What ran

Each job ran on one node or more, with `-A m3246 -q regular -C cpu --exclusive --no-requeue`, through the committed
packer. The ledger is [`run/LEDGER.psv`](fd/receipts-1b/stage2/run/LEDGER.psv), from `sacct`.

| job | JobID | pin | contents | State, ExitCode | Elapsed | node-h | cap |
|---|---|---|---|---|---|---:|---:|
| 2a-0 | 60623576 | R `664c38db` | 4 derivation, 2 pilot toys, 2 reproduction runs | COMPLETED 0:0 | 00:13:54 | 0.232 | 1.00 |
| 2a | 60624652 | R | node 0 of 3 | **FAILED 1:0** | 01:40:22 | 1.673 | |
| 2a | 60624653 | R | node 1 of 3 | COMPLETED 0:0 | 01:40:46 | 1.679 | |
| 2a | 60624654 | R | node 2 of 3 | COMPLETED 0:0 | 01:40:37 | 1.677 | 8.00 |
| 2a-r | 60631190 | R2 `e3c91978` | 8 half pilots, 4 derivation | COMPLETED 0:0 | 00:13:42 | 0.228 | 1.00 |
| **stage 2** | | | 204 products written, 2 quarantined, 202 kept | | | **5.489** | 23.00 |

The 204 written are 8 by 2a-0, 184 of 2a's 194 by 2a, and 12 by 2a-r. 2a's other 10 were never made (§3). The 202
kept are the 202 declared, each once: 2a-r's two replacements stand in for the quarantined pair.

- **Charges.** Node-h is NNodes × Elapsed. Jobs 2b (cap 5.00) and 2c (cap 9.00) were not submitted.
- **Login-node steps.** L1–L5 and A3–A5 passed on login37. Their transcripts are under `run/connects/`.
- **Pins.** The weight-file pins hashed 701 files against their recorded digests (`5adcd576…`). `check_pins` held
  at every step, and the derivation check reproduced its committed output exactly, both times it ran.
- **The balance.** iris at 23:17:29Z showed m3246 at 17,925.5 of 20,000.0 charged.

## 2. Gate 1, after 2a-0: PASS

- **The reproduction:** `repro` PASS. The toy mode with every draw off reproduces F1c's `xsec_flat` bitwise:
  - G18 806,000 against `pe/genie_v3_g18/ratio_nd_a1_s806000.npz`;
  - AR23 807,000 against `pe/genie_v3_ar23/ratio_nd_a1_s807000.npz`.

  The readout is `$B/score/repro.json`, whose sha256 is in `run/score/SHA256SUMS` (§7).
- **The walls:** `walls --after 2a-0` PASS.
  - The largest `seconds_unfold` was 801.4 s (derivation MaRES_1), and the largest `seconds_load` was 16.0 s.
  - 2a's fullest lane came to 2L + 9w = 7,244.5 s, against 7,680 s.
  - The largest peak RSS was 18,175,300 KiB, against 44,040,192 KiB.

## 3. The half-MC defect, found in the field

**What happened.** Job 60624652 ended FAILED 1:0, and its lanes 1 and 2 exited 4 (`run/lanes/`):

    [fd-1b] refusing: Refusal: fd1b_pilot_half_s2600001.npz: its truth differs from this run's first toy's
    [fd-1b] refusing: Refusal: fd1b_pilot_half_s2600005.npz: its truth differs from this run's first toy's

- **The code.** `fd_1b_toys.run` held every unfold of one step to the first unfold's truth.
- **Where the rule is right and where it is wrong.** It is right in toy and derivation mode, where the truth is
  fixed. It is wrong in half mode, where each seed's truth is its own half-MC split's (`split_key_for(seed)`, then
  `s5n_pseudo.build_pseudo`).
- **The second site.** The scorer's half read-back (`fd_1b_score.load_toys`) had the same assumption, so the pairs
  readout would have read the 8 half toys as INVALID.
- **What it left unmade:**
  - 6 half pilots, 2,600,001–003 and 2,600,005–007;
  - the 4 derivation universes queued behind them in lane 2: 2p2h_0, 2p2h_1, 2p2h_2 and AGKYxF1pi_0.

**Why no fixture caught it.** Every half run before 2a had a single seed:
- the stage-1 tests (`806000:806000`);
- the two reproduction runs;
- 2a-0's layout of one unfold per lane.

A check that compares item k with item 1 cannot fire on one item.
- **The toy-mode guard** had no test in the direction it acts (amendment 1, §1): at R, the guard's message and
  variable hit the code (`fd_1b_toys.py:410`) and nothing under `nd-unfolding/tests`.
  Search: git grep -E "truth differs|first_truth" -- nd-unfolding/tests @ 664c38db
- **Both reviews missed it:** the stage-1 independent review and the stage-2 independent review.
- **Both mutation receipts passed for the same reason.** No fixture had a second half seed, so no mutant could be
  told apart.

**The repair, under the director's rulings (amendment 1):**
- **The fix:** #602, merged at `2aa16538`. One truth per run is required only in toy and derivation mode. In half
  mode, each truth must bitwise-equal `half_truth(seed)`, which is recomputed from the seed's split alone. The scorer
  returns one truth per half toy. The fix came with 6 tests, an independent review with no blockers, and a 7-of-7
  mutation receipt.
- **The quarantine:** the two half pilots made before the fix were moved, not deleted, to `$B/quarantine/`:
  - `fd1b_pilot_half_s2600000.npz`, `d7b6d020…ac14`;
  - `fd1b_pilot_half_s2600004.npz`, `a19f14db…f0af`.

  Both digests were re-checked after the move (`run/logs/a5-quarantine.sha256`). The 8-toy half set is then one
  code.
- **The rerun:** job 2a-r reran all 8 half pilots and the 4 derivation universes. In its tables, lanes 0–3 each run
  a two-seed half step, which is the case the defect broke, and all completed rc 0.
- **The ceiling:** it counted ended jobs at their ledgered charge, so stage 2 stood at 20.26 within 23.00 before
  2a-r.

## 4. Gate 2, after 2a-r

### 4.1 Gate D: FAIL

`$SC2 gate-d` on all 176 derivation products returned rc 1 and verdict **FAIL** (window [0.9, 1.1]).
- **Readout:** `run/score/gate-d.json`, labelled DERIVATION.
- **Its own statement:** "STOP before any coverage toy: the control would be predicted to fail by construction".

**What gate D computes** (`fd_1b_score.cmd_gate_d`):
- For each band, E is S1's own estimator applied to the noise-free derivation unfolds of that band's universes.
- E is carried to f by diag(f / x_T), x_T being the runs' common truth.
- S1's stat, normalization and lateral blocks enter E_d unchanged.
- ρ_c = √(E_d,cc / M_d,cc), with M_d S1's drawn matrix.
- The per-group σ ratio is √(diag e / diag m) over each group's band blocks alone: e from the toys, m from S1.

| cell | ρ_c | flux | interaction | detector |
|---|---:|---:|---:|---:|
| R00 | **1.157** | 1.189 | 3.183 | 1.077 |
| R01 | 1.032 | 1.009 | 1.687 | 1.006 |
| R02 | **1.149** | 1.183 | 1.430 | 0.981 |
| R03 | 0.938 | 1.217 | 0.689 | 1.179 |
| R04 | 1.020 | 0.971 | 2.186 | 1.030 |
| R05 | **0.838** | 0.837 | 0.540 | 0.892 |
| R06 | 1.015 | 0.983 | 1.023 | 1.247 |
| R07 | **0.696** | 0.876 | 0.418 | 0.907 |
| R08 | **2.296** | 1.170 | 6.521 | 0.934 |
| R09 | **1.113** | 0.983 | 1.631 | 1.043 |
| R10 | **1.780** | 1.201 | 2.107 | 0.908 |
| R11 | **1.827** | 1.080 | 2.402 | 0.966 |
| R12 | **1.251** | 0.963 | 2.667 | 0.916 |
| R13 | **1.314** | 0.897 | 1.605 | 0.958 |
| R14 | 1.091 | 1.112 | 1.324 | 1.016 |
| R15 | **1.418** | 0.981 | 2.191 | 0.961 |

Bold marks a ρ_c outside the window.
- **ρ_c:** 2 cells are below 0.9 (R05 and R07), 5 are inside (R01, R03, R04, R06 and R14), and 9 are above 1.1.
  The range is 0.696–2.296, with median 1.131.
- **Per group (arithmetic on the table):**

| group | min | median | max | > 1 | < 1 | outside [0.9, 1.1] |
|---|---:|---:|---:|---:|---:|---:|
| flux | 0.837 | 0.996 | 1.217 | 8 | 8 | 9 |
| interaction | 0.418 | 1.659 | 6.521 | 13 | 3 | 15 |
| detector | 0.892 | 0.973 | 1.247 | 7 | 9 | 3 |

### 4.2 The scope of the measurement

<!-- absence-ok: this section scopes this stage's own measurement (what its jobs and readouts computed); it claims no search of the repository -->

**Measured:**
- each band's spread in the fixed-truth mechanics, from 176 noise-free unfolds (CV plus S1's 175 universes);
- its ratio to S1's own block per cell, per group, and in total.

The table is that measurement.

**Not measured:**
- why the ratios depart from 1;
- which bands within the interaction group carry the departure. The per-band ratios are computable from the 176
  products already on disk, but they were not run, because gate D's readout reports groups;
  <!-- absence-ok: scoping of this stage's own readouts --> 
- whether the departure would carry into the control's coverage. No coverage toy ran.

<!-- absence-ok: labels a candidate mechanism as not measured by this stage, as the director asked; it claims no search -->
**The declaration's anticipated gap, a candidate mechanism, UNMEASURED.** The protocol's §3 anticipated "the
first-order gap the derivation must size":
- S1's interaction bands reweight the whole unfolding MC, prior included, and a fixed-truth toy moves only the
  response.
- If the prior part of a band is material, "the control's intervals hold spread the toys cannot produce".

That gap is named here as a candidate, and is not asserted.

**A sign check, as arithmetic only.**
- The gap as stated predicts E smaller than M, so interaction ratios below 1.
- Measured: the interaction ratio is above 1 in 13 of 16 cells, with median 1.659. It is below 1 in R03 (0.689),
  R05 (0.540) and R07 (0.418).
- So, in most cells, the toys give more interaction spread than S1's blocks hold. That is the opposite of the
  direction the anticipated gap predicts. Taken alone, it cannot account for the cells above 1.

No other mechanism is offered.

### 4.3 The half-MC pairs: no verdict

`$SC2 pairs` returned rc 0 (`run/score/pairs.json`). It pairs the 8 half pilots, all made by one code, with the 8
full pilots of the same seeds, 2,600,000–007, each in σ of its own truth.

| quantity | shape | mean | sd | max \|·\| |
|---|---|---:|---:|---:|
| paired full-minus-half difference, in σ | 8 × 16 | −0.012 | 0.054 | 0.173 |
| truth difference, in σ | 8 × 16 | | | 0.0034 |

The readout carries no verdict, by declaration.

### 4.4 The pilot's walls: PASS

`$TK2 walls --after 2a` PASS (`$B/score/walls-2a.json`, sha256 in `run/score/SHA256SUMS`).
- **Pilot median.** The 16 pilot toys' median `seconds_unfold` was 664.8 s, against 1.25 × 832 = 1,040 s.
- **RSS.** The largest peak RSS across 2a-0 and 2a was 18,439,836 KiB, against 44,040,192 KiB.
- **What it means.** Had the control run, it would not have been re-priced.

## 5. An instrument discrepancy, resolved

The waiting script for 2a-r counted 8 `[s5c] task=` lines without ` rc=0 ` among 16, while `sacct` showed every
step COMPLETED 0:0.
- **The read.** I read the 16 lines (`run/connects/read15.out`): the packer writes a `start=` line and an
  `rc=… end=` line for each lane.
- **The result.** All 8 end lines read `rc=0`, and all 8 `[f1-lane]` step lines read `rc=0`.
- **The cause.** The 8 were the start lines: a defect in my count, not in the job.

The earlier gate script for 2a pointed its grep at the wrong directory, so it read 0 lines. Its STOP rested on
`sacct`, which was right.

## 6. Storage

- `$B/stage2.tar` (41,134,080 bytes, sha256 `ef432a3e…7f56`) holds `runs`, `logs`, `score`, `quarantine` and
  `pins.json`.
- It is on HPSS at `fd-1b-20261030/stage2.tar`. `hashcreate` and then `hashverify` returned OK (md5).
- A retrieved copy is byte-identical under `cmp` (`run/connects/hpss.out`).
- It used 40.6 MB of the roughly 66 GiB headroom.
- Nothing went to CFS, and nothing on pscratch was deleted.

## 7. Receipts in this PR

Under [`fd/receipts-1b/stage2/run/`](fd/receipts-1b/stage2/run/):
- `LEDGER.psv`, with all 5 jobs. `stage2/LEDGER.psv` stays as the 4-row receipt that the charge constants are tested
  against.
- `logs/`: the L-step and A-step logs, submit lines, gate logs and job batch logs.
- `score/`: `gate-d.json` and `pairs.json` as the scorer wrote them, and `SHA256SUMS` over all six readouts.
  - The other four are `repro.json`, `walls-2a-0.json`, `walls-2a.json` and `pilot-walls-pregate.json`. They name
    products by file, so the receipt-artifact check would read them as products git should carry. They stay
    unmodified in `$B/score/` and in the HPSS archive (§6), and their figures are quoted in §2 and §4.4.
  - The preflights' derivation-check outputs are under `logs/`.
- `lanes/`: the two lanes of 60624652 that refused.
- `connects/`: every connect's script and transcript.

No product is committed, and no cross-section value is printed.

## 8. Not changed

The protocol, the reported covariance, κ, every claim and number, and the data product. The paper's statement that
coverage was not validated stands. Stage 3 is not declared.
Search: git ls-files docs/orchestration/state | grep -i FD-1B-STAGE3 (no hit; FD-1B-STAGE2 hits 5) @ c97e6db1
