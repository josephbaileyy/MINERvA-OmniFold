# REPORT 3D: the flux-correlation bootstrap over the 100 universes (2026-10-28)

**By** the measurement session.

**Under:**
- [`FD-FLUX-BOOT-BINDING.md`](FD-FLUX-BOOT-BINDING.md) (PR #430), which binds
  [`FD-FLUX-BOOT-DECLARATION.md`](FD-FLUX-BOOT-DECLARATION.md);
- [`FD-FLUX-BOOT-BINDING-AMENDMENT-1.md`](FD-FLUX-BOOT-BINDING-AMENDMENT-1.md) (PR #437), which binds
  [`FD-FLUX-BOOT-DECLARATION-AMENDMENT-1.md`](FD-FLUX-BOOT-DECLARATION-AMENDMENT-1.md) at deploy pin `91312bc8`;
- `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md`, item 3.

**MEASURES:** the estimation scatter of Stage G's reported χ² when the flux block is rebuilt from bootstrap replicates
of the 100 weighted Flux universes, under PPFX and the ν-e + IMD constraint. Numbers only.

**CANNOT AUTHORIZE:**
- a reading;
- a claim;
- the new form of the paper's sensitivity sentence, which goes through the PRD read and the truth column, then to
  Joseph;
- any change to a covariance, cell, readout or κ.

**CITABLE FOR:**
- the bands, the offsets and the controls' outcomes;
- the run's steps, times and digests;
- the first deploy's STOP (§6).

**NOT CITABLE FOR** (the readout's `labels.not_citable_for`):
- that the χ² is insensitive to the flux correlations;
- that the PPFX or constraint correlations are correct;
- an interval for the χ² under the true flux correlations.

G-SENS2's α results stand.

## Outcome

**Every bound step exited 0,** on login36, at 0 node-h. There was no Slurm job and nothing went to CFS.
- `$B` = `/pscratch/sd/j/josephrb/fd-flux-boot-20261028` was absent beforehand.
- Both steps ran detached (`nohup`) and were polled.

| step | what | UTC | rc | outcome |
|---|---|---|---|---|
| §2.1, as amended | deploy and tests | 05:35:50–05:39:24 | 0 | HEAD `91312bc8f22b…`; porcelain 0 before and after (ignored files included); all §8 digests as amended, with the declaration `a5166316…` and the amendment `44e6a889…`; **Ran 207 tests in 170.4 s, OK** |
| §2.2 | `fd_flux_boot.py`, the declared argv | 05:39:53–05:39:59 | 0 | D0–D5 and B0–B6 PASS; `controls_passed` ends with B6; stderr empty; porcelain 0 after |

**The readout** `fd/readout/fd_flux_boot_readout.json` has sha256
`b7b5652cbd163b6830655250c18bbcfd65f87bb199821c97c7abdbd671e70001`. It is schema `fd-flux-boot-readout/1`, with
`non_finite_written_as_null` 0. The fetched copy, and every fetched log, is byte-identical to the cluster's
(`logs/outputs-sha256.txt`).

## 1. The controls on real inputs

| control | worst | tolerance |
|---|---:|---:|
| D5: Stage G reproduced | 0.0 | 1e-10 |
| B0: constraint file, weights and 100 universes | Σw 211.012, n_eff 19.06; digests as S1 recorded | — |
| B1: S1's flux block rebuilt from the universes | **0.0** | 1e-12 |
| B2: the rebuilt block swapped in reproduces Stage G, total and shape-only | **0.0** | 1e-10 |
| B6: every swapped matrix is its parts | **3.4e-16** | 1e-12 |

**B1's 0.0 means the rebuild equalled S1's block bit for bit on login36.** The review's laptop rebuild differed from it
by up to 27 ulp (`FD-FLUX-BOOT-DECLARATION-AMENDMENT-1.md` §2.3).
- So on the real inputs, B2 carried no difference through the swap, and its 0.0 is Stage G's own computation on Stage
  G's own bits, as D5 checks.
- B6, the swap's matrix-level check, ran over the identity, the 4,000 replicate variants and `uniform`, and its worst
  was 3.4 × 10⁻¹⁶.

## 2. The bands

**Ruling 2 (`FD-FLUX-BOOT-BINDING.md` §2) applies.**
- Each band is the percentile band of the χ² over the 2,000 replicates. It is estimation scatter given these 100
  universes under PPFX and the ν-e + IMD constraint, and not an interval.
- Each band is printed beside Stage G's χ̂ and the offset, median − χ̂, which is the bootstrap's estimate of χ̂'s bias.
  Every offset measured here is positive.
- The basic band 2χ̂ − q is the declared companion. It is in the readout and not proposed for print; it is shown in the
  last column only for completeness.

**Why neither band is an interval.** This is the declaration's synthetic check (§4.3, after the focused re-review).
Against a nominal 0.68, the 16–84 % percentile band covered its target:
- in **0.37** (correlation) and **0.32** (block) of ensembles, with independent weights;
- in **0.47** and **0.45**, against χ²(C_post), when the weights follow the values.

The basic band covered **0.48** and **0.57**, and **0.57** and **0.61**.

The readout's `labels.band` says: "estimation uncertainty, not sensitivity … Neither band is an interval for the chi2
under the true correlations".

### 2.1 `correlation` (primary): S1's flux variances kept bit for bit, the replicate's correlations

**Total χ²:**

| prediction | ndf | χ̂ (Stage G) | offset | 16–84 % | 2.5–97.5 % | halves, 16–84 % | basic 16–84 % (companion) |
|---|---:|---:|---:|---|---|---|---|
| genie_cv | 16 | 109.35 | +0.25 | 105.97–112.45 | 101.25–114.68 | 105.86–112.48 / 106.12–112.42 | 106.26–112.74 |
| genie_mec | 16 | 272.12 | +1.22 | 262.37–282.71 | 249.24–290.98 | 262.23–282.67 / 262.50–282.72 | 261.54–281.87 |
| nuwro | 16 | 188.03 | +0.75 | 185.47–190.93 | 180.92–192.32 | 185.62–190.89 / 185.35–190.97 | 185.13–190.59 |
| gibuu | 8 | 58.46 | +0.16 | 57.33–59.47 | 55.58–60.02 | 57.31–59.47 / 57.34–59.47 | 57.46–59.59 |
| mnvtune_v1 | 16 | 329.72 | +3.12 | 314.90–350.00 | 297.41–367.19 | 314.87–349.12 / 315.00–350.63 | 309.43–344.53 |

**Shape-only χ²:**

| prediction | ndf (shape) | χ̂ (Stage G) | offset | 16–84 % | 2.5–97.5 % | basic 16–84 % (companion) |
|---|---:|---:|---:|---|---|---|
| genie_cv | 15 | 108.51 | +0.23 | 104.89–111.84 | 99.99–114.19 | 105.17–112.12 |
| genie_mec | 15 | 258.07 | +0.82 | 250.90–265.42 | 240.66–270.52 | 250.73–265.25 |
| nuwro | 15 | 188.00 | +0.68 | 185.40–190.75 | 180.39–192.01 | 185.24–190.59 |
| gibuu | 7 | 27.69 | +0.08 | 26.94–28.34 | 25.78–28.72 | 27.04–28.44 |
| mnvtune_v1 | 15 | 311.19 | +1.90 | 301.50–323.19 | 288.68–332.54 | 299.19–320.88 |

### 2.2 `block` (second): the replicate's block itself, variances included

Under resampling, this variant's variances are biased low by about (1 − 1/n_eff), which pushes its χ² high (the
readout's `labels.variants`).

**Total χ²:**

| prediction | ndf | χ̂ (Stage G) | offset | 16–84 % | 2.5–97.5 % | halves, 16–84 % | basic 16–84 % (companion) |
|---|---:|---:|---:|---|---|---|---|
| genie_cv | 16 | 109.35 | +0.99 | 107.59–112.83 | 104.76–115.03 | 107.58–112.95 / 107.61–112.69 | 105.88–111.12 |
| genie_mec | 16 | 272.12 | +2.09 | 267.00–281.72 | 258.67–289.33 | 266.85–282.04 / 267.10–281.55 | 262.52–277.24 |
| nuwro | 16 | 188.03 | +0.94 | 187.15–190.62 | 185.36–192.33 | 187.15–190.66 / 187.18–190.57 | 185.44–188.91 |
| gibuu | 8 | 58.46 | +0.78 | 55.89–62.93 | 52.64–67.33 | 55.80–62.93 / 55.99–62.92 | 54.00–61.03 |
| mnvtune_v1 | 16 | 329.72 | +4.08 | 322.30–347.09 | 313.15–362.11 | 322.35–347.38 / 322.25–346.69 | 312.34–337.13 |

**Shape-only χ²:**

| prediction | χ̂ (Stage G) | offset | 16–84 % | 2.5–97.5 % | basic 16–84 % (companion) |
|---|---:|---:|---|---|---|
| genie_cv | 108.51 | +0.73 | 106.46–111.66 | 103.50–113.78 | 105.35–110.56 |
| genie_mec | 258.07 | +1.87 | 254.57–265.02 | 249.06–269.91 | 251.12–261.58 |
| nuwro | 188.00 | +0.73 | 187.05–190.38 | 185.25–192.12 | 185.62–188.95 |
| gibuu | 27.69 | +0.14 | 27.37–28.28 | 26.94–28.65 | 27.10–28.01 |
| mnvtune_v1 | 311.19 | +3.25 | 307.11–322.84 | 300.24–333.18 | 299.54–315.27 |

**The full readout also holds:** the medians, minima and maxima, and both halves' percentiles at every quantile.

## 3. The R04–R08 correlation

| matrix | S1's own | 2.5 % | 16 % | 50 % | 84 % | 97.5 % | min–max |
|---|---:|---:|---:|---:|---:|---:|---|
| the flux block alone | 0.9828 | 0.9587 | 0.9737 | 0.9834 | 0.9897 | 0.9934 | 0.9310–0.9957 |
| C_total + C_resp, `correlation` variant | 0.8113 | 0.7994 | 0.8068 | 0.8115 | 0.8146 | 0.8165 | 0.7857–0.8176 |
| C_total + C_resp, `block` variant | 0.8113 | 0.7687 | 0.7888 | 0.8088 | 0.8248 | 0.8378 | 0.7456–0.8604 |

## 4. The named alternative, `uniform`

`uniform` is the block from the 100 universes with equal weights: the flux prior without the constraint, n_eff 100. Its
label says it is a named alternative, not an alternative result. Its flux-block R04–R08 correlation is 0.9897.

| prediction | χ² (Stage G's in brackets) | shape-only χ² |
|---|---|---:|
| genie_cv | 106.07 (109.35) | 105.86 |
| genie_mec | 264.21 (272.12) | 253.41 |
| nuwro | 176.42 (188.03) | 176.12 |
| gibuu | 44.88 (58.46) | 28.13 |
| mnvtune_v1 | 320.20 (329.72) | 305.68 |

## 5. How n_eff entered

**The weights:** Σw 211.012 and n_eff 19.06, as S1 recorded.

**`sd_over_sigma_w_root_n_eff`,** per cell. It is the bootstrap sd of the weighted mean universe integral, over
σ_w/√n_eff. It is 1 when the residuals do not follow the weights.

| R00 | R01 | R02 | R03 | R04 | R05 | R06 | R07 | R08 | R09 | R10 | R11 | R12 | R13 | R14 | R15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.999 | 0.901 | 1.037 | 0.943 | 0.936 | 1.059 | 0.887 | 0.946 | 0.974 | 0.900 | 0.983 | 0.906 | 0.940 | 0.984 | 0.997 | 0.906 |

**Median 0.945, range 0.887–1.059.**

**`delta_method_ratio`** is the same sd over √(Σw²(x − μ)²)/Σw. Its label says it is about 1 for any weights, and so is
a check that the bootstrap carries that term. **Median 1.025, range 1.019–1.029.** Both ratios are descriptive (ruling
7).

## 6. The first deploy's STOP

These receipts are from `fd/flux-boot-report` at `79c013ac`, and are merged here.
- **What happened:** deploy `f370da5b` on login12, at 2026-10-28T00:39:31–00:41:35Z, under `FD-FLUX-BOOT-BINDING.md`
  condition 1.
  - HEAD was the pin, porcelain was 0 before and after, and all §8 digests matched.
  - The tests failed: `tests rc=1`, "Ran 203 tests … FAILED (failures=6, errors=1)". All seven failures were control
    B2 refusing the synthetic fixture, at 1.025 × 10⁻¹⁰ against 10⁻¹⁰.
- **What followed:** the run was not started, and nothing was rerun or repaired.
- **Where it is:**
  - the receipts are `fd/receipts-flux-boot/run/s1.sh`, `s1.out`, `logs/deploy-tests.log` and
    `logs/deploy-and-stamps.log`;
  - the ledger row is `3D S2.1 deploy and tests (FD-FLUX-BOOT-BINDING)`, with rc 1 at 0 node-h;
  - its deploy root, `/pscratch/sd/j/josephrb/fd-flux-boot-20261027`, is untouched.
- **Its cause and repair** are `FD-FLUX-BOOT-DECLARATION-AMENDMENT-1.md` §1–§2, bound by the amendment binding.

## 7. Receipts, ledger and retention

**`fd/receipts-flux-boot/run/amended/`:**
- `s1-launch.sh`, `s1-launch.out`, `s1-poll.sh` and `s1-poll.out`: the deploy and tests;
- `s2-launch.sh`, `s2-launch.out`, `s2-poll.sh` and `s2-poll.out`: the run;
- `logs/`: `deploy.log`, `deploy-tests.log`, `boot.out`, `boot.err` (empty), `s1.stamps`, `s2.stamps`, the two step
  bodies, the empty `nohup` captures and `outputs-sha256.txt`.

**Ledger:** two rows in `fd/LEDGER.tsv`, both 0 node-h, with no Slurm job, plus the STOP's row (§6).

**Retention:** both `/pscratch/sd/j/josephrb/fd-flux-boot-20261027` (the STOP's evidence) and
`/pscratch/sd/j/josephrb/fd-flux-boot-20261028` (613 MB, the deploy clone, the readout and the logs) are on the
pscratch list.

**The results index:** the readout is classed `excluded-no-metric`, so no index row is added.

## Not changed

- Every covariance, cell, readout and κ. G-SENS2's α results stand.
- `docs/analysis-note/**`, including the sensitivity sentence.
- Claims, readings and printed wording are Joseph's.
