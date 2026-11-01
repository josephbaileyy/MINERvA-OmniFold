# REPORT 1B gate-D investigation, step I2: H1 accounts (14 of 15), O1 (2026-11-01)

**By** the measurement session `coverage-5b`, for the director and `coverage-5b-audit`.

**Under:**
- [`FD-1B-INV-DECLARATION.md`](FD-1B-INV-DECLARATION.md) (revision 2), bound by
  [`FD-1B-INV-BINDING.md`](FD-1B-INV-BINDING.md) (#644) at M = `b1c615f1`;
- `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`, item 1;
- step I0's report, [`FD-1B-INV-I0-REPORT.md`](FD-1B-INV-I0-REPORT.md) (#645), which sent the run to I2.

**The reading: rule I2 attributes 14 of the interaction group's 15 out-of-window cells to F_prior (H1) and 1 to
F_truth (H3, R05).** No cell is attributed to F_src (H4), and none is unresolved.
- **The headline is H1, outcome O1:** gate D compared unlike objects. The fixed-truth toys' block matches the response
  alone moved in the MC (F_src = 0.986–1.015 in every cell). S1's full universe at the same truth gives a different
  block, by F_prior = √(B/A), with median 2.72 and range 0.49–6.51.
- **H3 and H4 are each refuted as the account** (1 and 0 cells, the level being 3 or fewer). They are counted
  separately and never pooled with H1.
- **Cost:** 5.621 node-h, against I2's caps of 1.0 + 14.0. I2-0 used 0.251 and the bulk 5.370 (§1).
- **Deviations:** none. Access times are unchanged on every source (§1).

**Under binding ruling 4(a), this O1 does not validate S1's interaction block, and this report must not read that
way.** The question it raises goes to Joseph in §5, unanswered.

**MEASURES:** the declared I2 readouts at the nominal derivation CV pseudo-data, labelled DERIVATION, and rule I2's
per-cell attribution. **CANNOT SUPPORT:**
- **That C (the prior alone) is what separates A from B.** The additivity readout does not hold (§4.3). F_prior
  measures the response alone against S1's whole universe, not against the response plus C.
- **That either block is the right one** for the reported intervals (§5).
- **Any statement about gate D in the cells where flux carries part of ρ_c² − 1** (R05, R00; §3).
- **Any claim about the coverage of the reported intervals,** in either direction.

Gate D's FAIL, the diagnosis's NOT LOCALIZED, and I0's H2 REJECTED stand.

## 1. What ran

| connect | when (UTC) | what | result |
|---|---|---|---|
| 21 | 19:27:46–19:27:54 | table check, `hpssquota`, `iris`, I2-0 submit | job 60656806 |
| 22 | 19:54:42–19:54:47 | I2-0 ledger, lanes, `walls`, CV controls, atime, HPSS | `walls` PASS; i2-0.tar verified |
| 23 | 19:55:28–19:55:31 | `walls` re-read, table check, `stat` of 272 sources, bulk submit | jobs 60658473–76 |
| 24 | 21:41:34–21:41:43 | bulk ledger, lanes, 204 products, atime, `i2` on login37 with `nice -n 19`, HPSS | `i2` rc 0, verdict O1; i2.tar verified |

**Jobs.** All ran from `$V/deploy`, a fresh clone detached at M with empty porcelain. Each used `-A m3246 -q regular
-C cpu` and the committed packer `sbatch_timing_packed.sh`, whose own directives give `--nodes=1 --exclusive
--no-requeue`. All ran at 32 CPUs and 56 G per lane, 8 lanes per node.

| job | name | limit | start–end (UTC) | elapsed | node-h | lines | items |
|---|---|---|---|---|---:|---|---:|
| 60656806 | fd1b_inv_i20 | 1:00:00 | 19:38:27–19:53:30 | 0:15:03 | 0.251 | 0–7 of tasks-i2-0 | 8 |
| 60658473 | fd1b_inv_i2n0 | 3:30:00 | 20:05:37–21:33:39 | 1:28:02 | 1.467 | 0–7 of tasks-i2 | 52 |
| 60658474 | fd1b_inv_i2n1 | 3:30:00 | 20:05:37–21:24:11 | 1:18:34 | 1.309 | 8–15 | 48 |
| 60658475 | fd1b_inv_i2n2 | 3:30:00 | 20:19:09–21:37:16 | 1:18:07 | 1.302 | 16–23 | 48 |
| 60658476 | fd1b_inv_i2n3 | 3:30:00 | 20:19:55–21:37:25 | 1:17:30 | 1.292 | 24–31 | 48 |

- Every job is COMPLETED 0:0. Every lane returned rc 0 (8 + 32 lanes), and no log holds a refusal or a traceback.
- `sacct` prints local time, PST since 02:00 that morning, and the table adds 8 h. The job logs' own UTC stamps agree:
  for example, 60658473 launched at 20:05:41.95Z.
- **Reserved, nodes × limit:** 1.0 for I2-0 and 4 × 3.5 = 14.0 for the bulk, each equal to its cap. **Used:** 5.621
  node-h. I1's cap of 4.0 was not used. The investigation has used 5.621 of 19.0.

**The pilot, I2-0 (connect 22).**
- **`walls` read PASS.** The largest `seconds_unfold` is 849.6 s (A_MaRES_0), against the unit of 1,370 s. The largest
  peak RSS is 20,786,436 KiB (A_2p2h_0), against 44,040,192. The readout is `walls-i2-0.json`.
- **The three CV controls are bitwise equal** to the staged derivation CV product's `xsec_flat`. Each pilot universe
  product differs from CV and is finite.
- The bulk was submitted only after PASS, under ruling 1.

**The bulk's walls.** Over 196 items, `seconds_unfold` has median 724.7 s and maximum 826.0 s. Peak RSS has maximum
20,934,284 KiB.

**Products.**
- 204 of 204: 68 per mode, the three CV controls included. No partials.
- Every product carries `code_sha256` `71b3903a…`, the digest the mutation receipt names. `i2` checks one code and one
  input set across all 204 (ONE_CODE_KEYS) and refuses otherwise. It did not refuse.

**Access times.**
- 204 atime sidecars, with no file moved.
- `stat` of the 272 bulk sources, before submission and after the jobs, is identical in atime, mtime and size. So is
  `stat` of I2-0's 16 sources.

**The readout.** `$V/i2/i2.json`: 62,900 bytes, sha256 `a9d3dc9c0e331eb635d6598c03b5bf95f6931f88c0cf0a43a1e73e2df9135bdb`.
`i2` passed every control it enforces:
- gate D's committed readout;
- I0's readout, with I1 absent because I0 read no cell SUPPORTED or OPEN;
- the interaction ratio reproduces gate D's bit for bit;
- every mode at CV is bitwise equal to the derivation CV;
- every product names its own mode and universe;
- one code and one input set;
- 15 interaction cells outside the window, as declared.

`$V` is `/pscratch/sd/j/josephrb/fd-1b-inv-20261101`. The receipts are in
[`fd/receipts-1b/inv/i2/`](fd/receipts-1b/inv/i2/). They hold:
- the readout and its log, and `walls-i2-0.json`;
- both `sacct` ledgers, the five job logs, the submit lines and their outputs;
- each connect's script and transcript;
- the four task tables, with their generator and digests (`tables/`);
- the 40 lane logs' digests (`lanes.SHA256SUMS`);
- `SHA256SUMS`.

## 2. The factors, per cell

All blocks are diagonal entries of the interaction group's sum, built with the pair estimator. E, A, B and C are
carried by g = f / x_T, as gate D's E is. M is S1's, made at the data. The window is [0.9, 1.1].

| cell | √(E/M) | F_src = √(E/B) | F_prior = √(B/A) | F_truth = √(A/M) | F_truth, S1-resolved | F_truth, uncarried | attributed | rule I2 |
|---|---:|---:|---:|---:|---:|---:|---|---|
| R00 | 3.183 | 0.994 | **5.980** | 0.536 | 0.476 | 0.503 | F_prior | H1 → O1 |
| R01 | 1.687 | 0.998 | **2.432** | 0.695 | 0.671 | 0.604 | F_prior | H1 → O1 |
| R02 | 1.430 | 1.006 | **2.501** | 0.568 | 0.545 | 0.590 | F_prior | H1 → O1 |
| R03 | 0.689 | 0.986 | **0.801** | 0.872 | 0.878 | 0.739 | F_prior | H1 → O1 |
| R04 | 2.186 | 0.989 | **3.949** | 0.559 | 0.556 | 0.546 | F_prior | H1 → O1 |
| R05 | 0.540 | 0.996 | 0.857 | **0.632** | 0.656 | 0.516 | F_truth | H3 → O1 |
| R06 | 1.023 | 0.997 | 1.195 | 0.858 | 0.736 | 0.944 | — (in window) | — |
| R07 | 0.418 | 1.004 | **0.493** | 0.844 | 0.847 | 0.728 | F_prior | H1 → O1 |
| R08 | 6.521 | 1.003 | **6.506** | 0.999 | 0.905 | 0.797 | F_prior | H1 → O1 |
| R09 | 1.631 | 1.007 | **2.343** | 0.691 | 0.676 | 0.611 | F_prior | H1 → O1 |
| R10 | 2.107 | 0.987 | **3.750** | 0.569 | 0.564 | 0.474 | F_prior | H1 → O1 |
| R11 | 2.402 | 1.014 | **4.025** | 0.588 | 0.560 | 0.483 | F_prior | H1 → O1 |
| R12 | 2.667 | 1.012 | **3.909** | 0.674 | 0.671 | 0.573 | F_prior | H1 → O1 |
| R13 | 1.605 | 1.015 | **3.003** | 0.527 | 0.521 | 0.434 | F_prior | H1 → O1 |
| R14 | 1.324 | 0.997 | **1.732** | 0.767 | 0.758 | 0.618 | F_prior | H1 → O1 |
| R15 | 2.191 | 1.007 | **2.942** | 0.739 | 0.715 | 0.638 | F_prior | H1 → O1 |

**The headline.**

| mechanism | cells | level | outcome |
|---|---:|---|---|
| H1 (F_prior) | 14 | **account** (≥ 8) | O1 |
| H3 (F_truth, surviving over S1-resolved bands) | 1 | refuted as the account (≤ 3) | |
| H4 (F_src) | 0 | refuted as the account (≤ 3) | |
| unresolved | 0 | | |

- **Re-derived.** The attributions, the counts and the identity were recomputed outside `fd_1b_inv.py` from the
  readout's factors. The product F_src · F_prior · F_truth equals √(E/M) to within 4.4 × 10⁻¹⁶ in every cell.
- **R05 under H3.** F_truth carries 74 % of |ln √(E/M)|. F_truth over S1-resolved bands is 0.656, out of the window on
  the same side, so the B2 condition is met.
- **R03 and R07,** two of the three cells below 1, are H1. There B < A: S1's whole universe gives a larger block than
  the response alone. F_prior carries 59 % and 81 % of the log.
- **R08**, the largest ratio, has F_truth = 0.999. All of its departure is B against A.

## 3. How much of each failing gate-D cell the interaction group carries

This is the share of ρ_c² − 1 that the interaction bands' terms carry, per gate-D failing cell (review m2).

| cell | R00 | R02 | R05 | R07 | R08 | R09 | R10 | R11 | R12 | R13 | R15 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| interaction share | 0.565 | 0.708 | **0.359** | 0.839 | 0.955 | 0.999 | 0.962 | 0.989 | 1.060 | 1.062 | 1.019 |

- **R05 and R00.** The interaction attribution covers about a third and about half of gate D's departure there. The
  rest is in other groups, which I2 does not decompose.
- **The other nine cells.** The interaction group carries at least 0.70 of ρ_c² − 1.
  - In R12, R13 and R15 it carries more than all of it, because the other groups' terms are net negative.

## 4. What else the readout shows

### 4.1 F_truth, under condition 4(b)

- **Condition 4(b):** a truth-dependent block is expected in kind, and the finding is its size beyond the carry.
- **The size.** F_truth is outside the window in 15 of 16 cells, all below 1 (median 0.683, range 0.527–0.999). It
  holds over S1-resolved bands (median 0.671, outside the window in 15).
- **The carry.**
  - **Arithmetic:** the carry moves F_truth from a median of 0.597 uncarried to 0.683.
  - **Reading:** S1's mechanism at the nominal truth, carried by g, gives a σ about 0.68× S1's at the data.
- **Why it is attributed in only one cell.** In all 13 cells above 1, F_truth is below 1 (R08 at 0.999), so it lies on
  the other side of 1 from √(E/M) and partly offsets F_prior. Rule I2 attributes by the dominant factor on the same side, so F_truth is
  attributed only in R05. The rule is bound.
- **What this does not show.** Being attributed in one cell does not make the truth dependence small. It is only
  smaller than F_prior and opposite to it in most cells.

### 4.2 F_src

- **The factor.** F_src is within 0.986–1.015 in every cell. The response moved in the pseudo-data (the toys) and the
  same response moved in the MC (B) give the same block to within 1.5 % in σ.
- **Per band (√ ratios):** B/E has median 0.995 over band-cells, with 10th–90th percentile 0.63–1.63.
- **Per universe:** the correlation of s_D with −s_B has median 0.95 over 67 universes and exceeds 0.9 in 37.
  - 13 universes have a negative correlation, in nine bands.
    - **The strongly negative ones** (−0.71 to −0.96, 8 universes) are in EtaNCEL, MaNCEL, NormNCRES, RDecBR1gamma
      and FrPiProd_pi. These are five of the six bands I0 found noise-consistent in all 16 cells. Their A/M medians in
      σ are 0.010–0.146.
    - **The weaker ones** (−0.05 to −0.49, 5 universes) are in FrElas_N, FrElas_pi, FrInel_N and FrPiProd_N.

### 4.3 Additivity: A ≈ B + C does not hold

- **The prediction.** §3 of the declaration predicts, under H1, "E ≠ M even at one truth, with A ≈ B + C (§6) and
  B/A outside the window".
  - The second part holds: F_prior is outside the window in all 16 cells.
  - The first part does not.
- **The readout.** The declared readout is the residual block(A − B − C), as a σ ratio √(residual / A) per band-cell.
  - Over band-cells it has median 0.49 and quartiles 0.19 and 1.89.
  - In seven bands the median over cells is above 1:

    | band | median over cells | cells above 1 |
    |---|---:|---:|
    | MaRES | 5.47 | 11 of 16 |
    | MvRES | 4.06 | 11 of 16 |
    | Rvp2pi | 3.90 | 13 of 16 |
    | Theta_Delta2Npi | 2.56 | 11 of 16 |
    | MaCCQE | 1.67 | 9 of 16 |
    | Rvn2pi | 1.66 | 10 of 16 |
    | MFP_pi | 1.60 | 15 of 16 |

  - **What the residual holds.** The declaration (§6) names the completeness change and the second order. By C's
    construction it also holds the variation of the truth weights within a fine cell, which C's fine-cell mean r
    leaves out. This report does not measure how the residual divides among these.
- **The prior share.** C/A, as a block ratio at the group level, has median 0.476 and range 0.156–1.390.
- **What this limits.** F_prior = √(B/A) compares the response alone with S1's whole universe at the same truth. The
  part of A that B lacks is not C alone.
  - The O1 stands under the bound rule.
  - This report cannot say that "the prior", in C's sense, is the part the toys cannot produce. It can say only that
    the toys' object is the response alone, and S1's is not.

NormDISCC's blocks are zero on every side in every cell (its two universes give identical shifts), so its per-band
ratios are undefined. The per-band A, B and C against M and E are in `i2.json` (`per_band`), as σ ratios.

## 5. For the director and Joseph, condition 4(a): B beside M in the data's frame

B is the response alone, moved in the MC, at the nominal truth, carried into the data's frame by g as E is. M is S1's
interaction block at the data. Both are diagonal entries of the group sum, in (cross-section units)².

| cell | M | B | √(B/M) | | cell | M | B | √(B/M) |
|---|---:|---:|---:|---|---|---:|---:|---:|
| R00 | 1.020e-81 | 1.046e-80 | 3.203 | | R08 | 4.450e-82 | 1.881e-80 | 6.501 |
| R01 | 1.888e-81 | 5.390e-81 | 1.690 | | R09 | 5.360e-81 | 1.405e-80 | 1.619 |
| R02 | 5.057e-82 | 1.022e-81 | 1.422 | | R10 | 1.876e-81 | 8.541e-81 | 2.134 |
| R03 | 5.380e-82 | 2.626e-82 | 0.699 | | R11 | 8.394e-82 | 4.705e-81 | 2.367 |
| R04 | 7.959e-82 | 3.885e-81 | 2.209 | | R12 | 1.834e-81 | 1.275e-80 | 2.636 |
| R05 | 4.519e-82 | 1.327e-82 | 0.542 | | R13 | 2.876e-81 | 7.197e-81 | 1.582 |
| R06 | 1.570e-82 | 1.651e-82 | 1.026 | | R14 | 3.645e-81 | 6.432e-81 | 1.328 |
| R07 | 2.656e-82 | 4.605e-83 | 0.416 | | R15 | 1.295e-81 | 6.130e-81 | 2.175 |

- **The fact (declaration §6).** S1's interaction block is built from S1's whole universe by construction.
- **The arithmetic on this readout.** √(B/M) has median 1.654 and range 0.416–6.501. It is above 1 in 13 cells and
  below 1 in 3 (R03, R05, R07).
- **The question for Joseph, not answered here:** should the reported intervals carry the response-only spread
  var(r), and leave the prior part to C_model, which already holds a model-dependence term? It is a question about
  what the covariance is for.
- **What this report does not do.** It does not say which block is right. §4.3 adds one fact to the question: B
  and A differ by more than C.

## 6. Storage

- **The tar.** `$V/i2.tar` is 44,195,840 bytes, sha256 `528c2eb2aaaeeccdd461ca131043901754f127f093b1860a5e0849534e23defe`.
  - It holds `i2/` (the 204 products, the atime sidecars, the lane logs, `walls-i2-0.json` and `i2.json`), `tables/`
    and `logs/`.
  - It does not hold `deploy/`, as with I0.
- **On HPSS** at `fd-1b-inv-20261101/i2.tar`. `hashcreate` and `hashverify` returned OK (md5 `4bba8d76…`), and a
  retrieved copy was identical under `cmp`.
- **I2-0's copy** is `fd-1b-inv-20261101/i2-0.tar`: 2,068,480 bytes, sha256 `de8da962…526f`. It was verified the
  same way in connect 22.
- **Space.** `hpssquota` was read before each put. It read 446.01 of 512.00 GiB in connects 21, 22 and 24.
  - **Arithmetic:** the two tars, 0.04 GiB together, do not show at that precision.
- **Nothing went to CFS.** Nothing on pscratch was deleted except the two retrieved copies, after their `cmp`.

## 7. Not changed

- **Unchanged:** gate D's readout and verdict, the diagnosis, I0's reading, the toys, M_d, the window, the reported
  covariance, κ, every claim and number, and the data product.
- **Binding ruling 5:** the O1 authorizes no new toys, no change to gate D, the window or M_d, and no coverage
  ensemble. Each needs its own declaration and binding.
- **Not proposed:** any repair. The question in §5 is Joseph's.
