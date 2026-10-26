# C_resp build report (2026-10-26, session "2d test")

**Status: sensitivity variant, not adopted.** Whether C_resp joins the reported total is Joseph's decision, made from
this readout, before Stage G runs (`DECISION-20261026-joseph-abstract-and-cresp-build.md` item 3).

**What ran.** The one bound run of [`C-RESP-SPEC.md`](../C-RESP-SPEC.md) §6.2:
- bound by [`C-RESP-BINDING.md`](../C-RESP-BINDING.md) (PR #371, main `35c46aed`);
- on login node `login37`, 2026-10-26T07:18:19Z to 07:19:14Z, at 0 node-h;
- once, with no retries, no Slurm job and nothing written to CFS.

**Outcome:**
- **The build completed.** Both test modules passed in the clone, and every refusal and check in the spec's §5 held.
- **The npz:** `/pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz`, sha256
  `4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a`, 12,952 bytes. It stays on pscratch.
- **The readout:** [`cresp.json`](cresp.json), sha256 `19bb2ee12827207fa346242ac901af48f6c80785eff5a14ff54133dff1ea01f0`,
  byte-identical to the file on pscratch.
- **Median per-cell relative σ over R00–R15:**
  - C_resp 2.14 %;
  - C_total 6.74 %, which is S1's;
  - C_total_resp 7.29 %.

**CITABLE FOR:** the size, rank and trace share of C_resp and its species blocks on R00–R15, and C_total_resp's σ beside
C_total's.

**NOT CITABLE FOR:**
- adoption of C_resp into the reported total;
- any data-against-generator quantity. None was computed.
- coverage, or any claim.
<!-- absence-ok: a statement about this session's own run: the argv is the spec's §6.2 (receipts/run.sh), whose only computation is build_cresp.py, which reads no generator prediction -->

## 1. The run

- **The script:** [`receipts/run.sh`](receipts/run.sh). It is the §6.2 argv verbatim under `set -eu` and `set -x`, so
  any failed command stops it. It ends with sha256s and listings, after the last argv line.
- **Sent as:** `ssh saul.nersc.gov bash -s < run.sh`. The exit status was 0, and the log ends `RUN-OK`.
- **The log:** [`receipts/run.txt`](receipts/run.txt).
  - It is committed as `.txt`, since the repo ignores `*.log`. The committed copy drops the single line of git's
    carriage-return checkout progress.
  - The original is `$R/logs/run.log`, sha256 `aa2e0bdf…7660a1`. The script was copied to `$R/logs/run.sh` after the
    run.

**The steps, from the log:**

| step | result |
|---|---|
| `test ! -e $R` | passed: `$R=/pscratch/sd/j/josephrb/cresp-20261026` did not exist |
| clone, detach at `973142a7` | `HEAD is now at 973142a7` and the `rev-parse` test passed |
| porcelain before (`--ignored`) | 0 lines |
| `test_build_cresp`, `test_s1_assemble` | `Ran 40 tests in 15.838s`, `OK` |
| `build_cresp.py` | exit 0; wrote `cresp.npz` and `cresp.json` |
| porcelain after (`--ignored`) | 0 lines; re-checked after the logs were copied: 0 |
<!-- absence-ok: the "did not exist" row is the run's own precondition `test ! -e $R`, which passed under set -eu on login37 at 2026-10-26T07:18:19Z (receipts/run.txt) -->

**Code in the clone, by sha256** (the log's `sha256sum` lines), all equal to the binding's:
- `build_cresp.py` `fe1aec8b…`;
- `test_build_cresp.py` `ea0dd6db…`;
- `s1_assemble.py` `b157250a…`;
- `s5p_stage1_inspect.py` `26569afc…`.

The JSON's `meta.inputs_sha256` records all 11 product digests, S1's assembly `db000707…` and the definition `b6790761…`,
each as the spec's §1 pins them.

## 2. Per-cell relative σ

These are √diag / f, with S1's f, from `cresp.json` `relative_sigma`. The min, max and per-cell tables come from
[`receipts/summarize.py`](receipts/summarize.py), which reads only the JSON; its output is
[`receipts/summary.txt`](receipts/summary.txt).

| block | median | min (cell) | max (cell) |
|---|---:|---:|---:|
| proton | 0.79 % | 0.04 % (R10) | 2.51 % (R08) |
| meson | 1.69 % | 0.09 % (R07) | 3.15 % (R05) |
| EM | 0.58 % | 0.09 % (R04) | 1.39 % (R02) |
| other | 0.58 % | 0.04 % (R04) | 1.18 % (R02) |
| **C_resp** (the sum of the four) | **2.14 %** | 0.70 % (R04) | 3.71 % (R05) |
| cross-talk (variant, not summed) | 0.36 % | 0.03 % (R02) | 0.98 % (R08) |
| C_total (S1) | 6.74 % | 4.14 % (R04) | 13.69 % (R02) |
| **C_total_resp** | **7.29 %** | 4.20 % (R04) | 14.00 % (R02) |

**Per cell, in %.** The last column is C_total_resp's σ divided by C_total's.

| cell | proton | meson | EM | other | C_resp | cross-talk | C_total | C_total_resp | ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R00 | 1.10 | 1.69 | 0.39 | 0.28 | 2.07 | 0.43 | 6.79 | 7.10 | 1.046 |
| R01 | 0.66 | 2.02 | 0.80 | 0.61 | 2.35 | 0.34 | 6.69 | 7.10 | 1.060 |
| R02 | 0.44 | 2.27 | 1.39 | 1.18 | 2.95 | 0.03 | 13.69 | 14.00 | 1.023 |
| R03 | 0.29 | 1.49 | 0.54 | 0.91 | 1.85 | 0.49 | 12.50 | 12.64 | 1.011 |
| R04 | 0.52 | 0.46 | 0.09 | 0.04 | 0.70 | 0.16 | 4.14 | 4.20 | 1.014 |
| R05 | 1.45 | 3.15 | 1.13 | 0.68 | 3.71 | 0.77 | 6.49 | 7.47 | 1.152 |
| R06 | 1.67 | 0.42 | 0.39 | 0.42 | 1.81 | 0.34 | 5.60 | 5.89 | 1.051 |
| R07 | 1.45 | 0.09 | 0.14 | 0.52 | 1.55 | 0.23 | 7.82 | 7.98 | 1.019 |
| R08 | 2.51 | 2.46 | 0.56 | 0.46 | 3.58 | 0.98 | 5.13 | 6.25 | 1.220 |
| R09 | 0.99 | 1.85 | 0.60 | 0.58 | 2.26 | 0.37 | 5.84 | 6.26 | 1.072 |
| R10 | 0.04 | 2.31 | 0.95 | 0.98 | 2.69 | 0.43 | 8.16 | 8.59 | 1.053 |
| R11 | 0.13 | 2.37 | 1.08 | 1.14 | 2.85 | 0.37 | 13.39 | 13.69 | 1.022 |
| R12 | 1.66 | 1.41 | 0.33 | 0.12 | 2.20 | 0.36 | 6.25 | 6.63 | 1.060 |
| R13 | 0.26 | 1.69 | 0.87 | 0.82 | 2.08 | 0.25 | 10.87 | 11.07 | 1.018 |
| R14 | 0.69 | 1.54 | 0.52 | 0.45 | 1.82 | 0.44 | 4.94 | 5.27 | 1.066 |
| R15 | 0.90 | 1.07 | 0.62 | 0.59 | 1.64 | 0.20 | 7.77 | 7.94 | 1.022 |

**What the table shows:**
- **The σ ratio:** median 1.048, from 1.011 (R03) to 1.220 (R08).
- **Two cells have C_resp above half of C_total's σ:** R05 (3.71 % against 6.49 %) and R08 (3.58 % against 5.13 %).
- **The largest species** is meson in 11 cells and proton in 5. EM and other are never the largest.
- **Cross-talk,** reported beside C_resp and not in it, has a median of 0.16 of C_resp's σ per cell, and at most 0.27
  (R08).

**Internal consistency of the readout** (summary.txt):
- The four species' σ add in quadrature to C_resp's on every cell, to a relative 1.9 × 10⁻¹⁶.
- C_total's and C_resp's σ add in quadrature to C_total_resp's, to 2.2 × 10⁻¹⁶.
- The recomputed medians equal the JSON's.

## 3. Ranks, spectra and trace shares

**Ranks** (relative cutoff 10⁻¹², `cresp.json` `eigen`):
- each species block, cross-talk included: 1;
- C_resp: 4;
- C_total and C_total_resp: 16.

**Spectra.**
- The smallest eigenvalue of each rank-deficient block is negative at 10⁻⁹⁶–10⁻⁹⁷ in absolute units, against a largest of
  10⁻⁸⁰–10⁻⁸¹. That is 15–16 orders below, which is rounding, and inside the spec's PSD gate.
- C_total_resp's smallest eigenvalue is 1.44 × 10⁻⁸³, against C_total's 1.19 × 10⁻⁸³.

**Each block's share of tr(C_total_resp / f fᵀ):**

| block | share |
|---|---:|
| C_total (S1) | 0.9262 |
| proton | 0.0168 |
| meson | 0.0436 |
| EM | 0.0071 |
| other | 0.0062 |
| *cross-talk, same normalisation, not in C_total_resp* | *0.0026* |

- The five summed shares total 1 to 10⁻¹⁶, and each one reproduces from the per-cell σ.
- The cross-talk row is computed by summarize.py on the same denominator. It is not a share of the matrix it is
  absent from.

## 4. Curvature ratio (descriptive, no gate)

This is ‖U x(+1) + U x(−1) − 2 U x(0)‖ / ‖U x(+1) − U x(−1)‖ on R00–R15 (spec §5), from `cresp.json`:

| species | proton | meson | EM | other | cross-talk |
|---|---:|---:|---:|---:|---:|
| ratio | 0.178 | 0.072 | 0.200 | 0.234 | 0.265 |

The JSON's label is: "MP-1 read a G3 curvature of this form as estimator discreteness at rounding scale (S1-REPORT,
input-jitter study); no gate". This report reads nothing further into these values.

## 5. The estimator-noise scale, for reading the small entries (inference, not measured on these cells)

**The products are single, unjittered unfolds,** so each half-span carries estimator discreteness (spec §7).
- MP-1's median per-cell relative SD of f₀ under input jitter is 0.21 %, on the J cells (`S1-REPORT.md`, "Input-jitter
  study").
- That study found that sharing a jitter seed between variants does not cancel the noise.
- If R00–R15 had the same per-unfold scatter, a half-span (x(+1) − x(−1)) / 2 would carry about 0.21 % / √2 ≈ 0.15 %.

**What this would mean, if it held on these cells:**
- Six species entries are at or below that scale:
  - proton R10 (0.04 %) and R11 (0.13 %);
  - meson R07 (0.09 %);
  - EM R04 (0.09 %) and R07 (0.14 %);
  - other R04 (0.04 %) and R12 (0.12 %).
- Cross-talk's median, 0.36 %, is about 2.4 times that scale. Its smallest entries, R02 (0.03 %) and R04 (0.16 %),
  are at or below it.
- In quadrature over four species, noise of that size would be about 0.3 % of C_resp's per-cell σ. Against a median of
  2.14 %, that is about 2 % of C_resp's variance.

None of this was measured on R00–R15. No jittered unfold of these products exists.
<!-- absence-ok: MP-1's input-jitter study (S1-REPORT.md, "Input-jitter study") jittered zero, em±1σ and other±1σ on the J-cell lateral dumps; its products are read on the J cells, and C-RESP-SPEC §7 records that the 11 inputs here are single unjittered unfolds -->

## 6. What C_resp covers, and what it does not

This is unchanged from [`C-RESP-SPEC.md`](../C-RESP-SPEC.md) §7.

**Covers:** configuration (e)'s 5D result on R00–R15, as unfolded from the data, under a ±1σ scale of the simulation's
reconstructed recoil energy, for proton, meson, EM and other at D1's sizes.

**Does not cover:**
- the joint tests' null distributions (MP1-A-full);
- neutron and muon deposits;
- configuration (a)'s products;
- the 3D, 4D and 2D results.

## 7. Next, by the decision's order

1. **The director brings this readout to Joseph.** Joseph decides whether C_resp joins the reported total.
2. **Stage G's binding** names the adopted matrix, with the other as a declared variant. It names `cresp.npz` by sha256
   `4d8b5797…a8a20a`.
3. **Stage G runs.**

**Retention.**
- `$R` holds the clone, `out/` and `logs/`.
- The npz is not on HPSS.
  - The same argv would rebuild its matrices while the 11 MP-1 products and S1's assembly survive.
  - A byte-identical file is not expected: `np.savez_compressed` writes zip member timestamps. So Stage G's pin is
    to this file.
- It joins the pscratch retention list re-raised before 2026-11-20.

## Not changed

S1's covariance, R00–R15, κ = 1, F0, the route decision, every claim and all printed wording.
