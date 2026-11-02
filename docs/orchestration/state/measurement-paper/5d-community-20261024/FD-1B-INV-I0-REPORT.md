# REPORT 1B gate-D investigation, step I0: H2 REJECTED in all 11 failing cells (2026-11-01)

**By** the measurement session `coverage-5b`, for the director and `coverage-5b-audit`.

**Under:**
- [`FD-1B-INV-DECLARATION.md`](FD-1B-INV-DECLARATION.md) (revision 2), bound by
  [`FD-1B-INV-BINDING.md`](FD-1B-INV-BINDING.md) (#644) at M = `b1c615f1`;
- `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`, item 1.

**The reading: rule H2 is REJECTED in every one of gate D's 11 failing cells.**
- **H2 is rejected as the account** of each failing cell: the noise-consistent terms do not explain the departure.
  None of the 11 cells is SUPPORTED or OPEN, so no O3 is pending.
- **The next step (binding ruling 1):** I2. I1 does not run, since it runs only if I0 reads a cell SUPPORTED or OPEN.
- **Cost:** 0 node-h.
- **Deviations:** none. Access times are unchanged on all 396 sources (§1).

**MEASURES:** the declared I0 readouts, labelled DERIVATION. **CANNOT SUPPORT:**
- any statement about which mechanism carries gate D's mismatch. I0 tests only H2;
- any claim about the coverage of the reported intervals, in either direction.

Gate D's FAIL and the diagnosis's NOT LOCALIZED stand.

## 1. What ran

| connect | when (UTC) | what | result |
|---|---|---|---|
| 18 | 19:20:59–19:21:01 | `stat` only (`find -printf`) of every §4 and §8 input, and `iris` | all present; none exposed before 2026-12-18 (§2) |
| 19 | 19:21:51–19:22:54 | I0 on login37, `nice -n 19` | `stage` rc 0 (3 s), `i0` rc 0 (3 s) |
| 20 | 19:23:45–19:23:49 | HPSS copy | verified (§5) |

- **Deploy:** `$V/deploy`, a fresh clone detached at M `b1c615f12fca5f8597d34750b2c074f1fd7b2cdd`, with empty porcelain.
  `fd_1b_inv.py` is `71b3903a…`, the digest the mutation receipt names. Gate D's readout is `e1838c0a…`.
- **Staging:** 396 inputs, none missing, each read once with `O_NOATIME` into `$V/i0/in/` and verified by sha256.
  The staging record is `staged.json`, `29994972…` (in `SHA256SUMS`, not committed, because it names the products).
- **Access times:** `stat` of all 396 sources, before staging and after I0, is identical in atime, mtime and size.
- **Readout:** `$V/i0/i0.json`, 163,958 bytes, sha256 `9a4142d348f591134ba4912a2197ca958ea387ec58b095622bce5f206d007021`.
- **Controls, all passed:** ρ on the copies reproduces gate D's bit for bit; the failing cells are the declared 11;
  `S1_CV` equals the N1 base bitwise; the 38 S1 band blocks are reproduced exactly from S1's universe unfolds.

`$V` is `/pscratch/sd/j/josephrb/fd-1b-inv-20261101`. The receipts are in [`fd/receipts-1b/inv/i0/`](fd/receipts-1b/inv/i0/):
the readout, both logs, each connect's script and transcript, and `SHA256SUMS`.

## 2. The inputs, before anything ran (connect 18)

| input | files | oldest atime | exposed from |
|---|---:|---|---|
| derivation products | 176 | 2026-11-01 | 2026-12-27 |
| S1 universe unfolds | 176 | 2026-10-25 | 2026-12-20 |
| S1 assembly | 1 | 2026-11-01 | 2026-12-27 |
| s5p data jitters (base + 20) | 21 | 2026-10-23 | **2026-12-18** |
| s5p nominal jitters (base + 20) | 21 | 2026-10-23 | **2026-12-18** |
| flux constraint | 1 | 2026-11-01 | 2026-12-27 |
| inputs npz (1.55 GB) | 1 | 2026-11-01 | 2026-12-27 |
| background dump | 1 | 2026-10-31 | 2026-12-26 |
| bank `cv.npz` (2.16 GB) | 1 | 2026-10-31 | 2026-12-26 |
| bank interaction weights (67 × 4, 26.6 GB) | 268 | 2026-10-31 | 2026-12-26 |
| detector dump | 32 | 2026-11-01 | 2026-12-27 |
| pins | 1 | 2026-11-01 | 2026-12-27 |

"Exposed from" is the oldest atime plus NERSC's 8 weeks **(arithmetic)**. Nothing was missing, so no fallback
applied. `iris` read m3246 at 17,930.6 of 20,000.0 charged, so 2,069.4 remain and half is 1,034.7, against the
investigation's caps of 19.0.

## 3. The floor

The floor is **measured**, from s5p study N's 20 data jitters and 20 nominal jitters, on the 16 cells:
- σ_J/f on the data has median 0.133 %, range 0.055–0.252 %;
- on nominal pseudo-data, carried by g, it has median 0.011 %.

These agree with the receipt's per-box medians, 0.176 % and 0.0125 %, on the 32-box set that the 16 cells merge
(`stage2_receipt.json`, `study_N`). The upper floor is 1.878 × σ_J².

**Scale, as arithmetic on the readout:** a pair band's pure-noise block on S1's side has median about 2 × 10⁻⁴ of
M_d,cc, where the total σ/f has median 6.45 %.

## 4. Rule H2, per cell

| cell | ρ_c | ρ_c^res, point floor | ρ_c^res, upper floor | reading | positive terms resolved on the toys' side |
|---|---:|---:|---:|---|---:|
| R00 | 1.157 | 1.157 | 1.157 | REJECTED | +0.345 |
| R02 | 1.149 | 1.152 | 1.154 | REJECTED | +0.403 |
| R05 | 0.838 | 0.846 | 0.855 | REJECTED | +0.027 |
| R07 | 0.696 | 0.698 | 0.700 | REJECTED | +0.013 |
| R08 | 2.296 | 2.297 | 2.297 | REJECTED | +4.322 |
| R09 | 1.113 | 1.114 | 1.115 | REJECTED | +0.325 |
| R10 | 1.780 | 1.782 | 1.783 | REJECTED | +2.290 |
| R11 | 1.827 | 1.827 | 1.828 | REJECTED | +2.356 |
| R12 | 1.251 | 1.251 | 1.252 | REJECTED | +0.621 |
| R13 | 1.314 | 1.315 | 1.315 | REJECTED | +0.778 |
| R15 | 1.418 | 1.419 | 1.419 | REJECTED | +1.136 |

- **What the noise-consistent terms carry.** 27 of the 38 bands are noise-consistent on both sides in at least one
  cell at the upper floor. Six are noise-consistent in all 16: EtaNCEL, FrPiProd_pi, MaNCEL, NormDISCC, NormNCRES and
  RDecBR1gamma. Removing every such term moves ρ_c² by at most 0.029 in any cell.
- **H2's sign.** In each of the nine failing cells above the window, the positive terms of bands resolved on the toys'
  side are at least ρ_c² − 1 (last column; R00 +0.345 against +0.338). The nominal floor is the small one, so H2
  does not predict these.
- **The two cells below the window,** R05 and R07, stay below it with the noise-consistent terms removed.

The per-band terms, the cells where each band is noise-consistent, and q = √(block / floor) are in `i0.json`
(`per_band`).

## 5. Storage

- `$V/i0.tar` (57,405,440 bytes, sha256 `7aa607b5…10ed`) holds `i0/` (the spec, the staged copies, the readout) and
  `logs/`.
  - It does not hold `deploy/`, the git clone at M, which the repository reproduces. Stage 2's tar left its clone out
    the same way.
- It is on HPSS at `fd-1b-inv-20261101/i0.tar`. `hashcreate` and `hashverify` returned OK (md5 `10a86257…`), and a
  retrieved copy was identical under `cmp`.
- Nothing went to CFS. Nothing on pscratch was deleted except the retrieved copy, after the `cmp`.
- **HPSS space.** `hpssquota` was not read before the put. The director's instruction to read it first arrived after
  connect 20 had run. It was read afterwards, in connect 21 at 19:27Z: 446.01 of 512.00 GiB used, so about 66 GiB
  free. The tar, at 57.4 MB, is under 0.1 % of that, so the whole of `i0/`, staged copies included, is on HPSS.

## 6. Descriptive readouts (no verdict role)

These are per interaction universe, from `i0.json` (`per_universe`). They are not part of rule H2 and assert no
mechanism.
- **Correlation of s_D against −s_S1:** median −0.12 over the 67 universes, positive in 36 % of them. §2 of the
  declaration states a first-order expectation, that S1's shift is about −r + p and the toys' about r. It is
  **inference**, and these numbers show only that S1's per-universe shifts do not mirror the toys'.
- **Pair antisymmetry,** |s₊ + s₋| / (|s₊| + |s₋|): the toys' pairs are close to antisymmetric, while S1's are less so.

| band | median antisymmetry, toys | S1 | ‖s_D‖ / ‖s_S1‖ |
|---|---:|---:|---:|
| MaRES | 0.11 | 0.51 | 2.00 |
| MaCCQE | 0.30 | 0.94 | 2.79 |
| MvRES | 0.06 | 0.42 | 1.34 |
| MFP_pi | 0.04 | 0.32 | 3.61 |
| BhtBY | 0.11 | 0.50 | 2.47 |

I2 decomposes S1's mechanism at the nominal truth. These readouts set no expectation for it.

## 7. Not changed

- **Unchanged:** gate D's readout and verdict, the diagnosis, the toys, M_d, the window, the reported covariance, κ,
  every claim and number, and the data product.
- **Not proposed:** any repair. The next step is I2-0, under binding ruling 1. Its submit line goes to the director
  before submission.
