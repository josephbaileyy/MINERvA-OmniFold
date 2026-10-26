# REPORT G: the data result on the 16 H2 cells against five generator predictions, C_resp adopted (2026-10-26)

**By** the measurement session.

**Under** [`FD-F0b-AND-G-BINDING.md`](FD-F0b-AND-G-BINDING.md) (PR #376) §3 and §4 item 5. That binding binds
[`FD-G-DECLARATION.md`](FD-G-DECLARATION.md) as amended (amendment 1) at deploy pin `c4396756`. It runs after F0b's
report, PR #377, merged on main as `5bb5e179`.

**MEASURES:** for each of the five predictions:
- the total and shape-only χ², ndf and p of configuration (e)'s data result f on R00–R15;
- the per-cell pulls, g/f − 1 and σ/f;
- the reported comparison, against C_total + C_resp + V_g, and the variant without C_resp, against C_total + V_g.

**CANNOT AUTHORIZE:** any reading of these numbers, a claim, printed wording, or a conclusion on the generators or on
publishability. All of these are Joseph's.

**CITABLE FOR:** the numbers below, each beside its matrix's name, size and rank, as `fd/readout/fd_g_readout.json`
holds them.

**NOT CITABLE FOR:**
- any interpretation;
- any 16-cell GiBUU quantity, since none was formed;
- anything about targets other than CH, since NuWro and GiBUU are on C12 with no correction applied.

**Outcome:**
- **Both steps exited 0** on login37 at 0 node-h.
  - **The deploy:** "Ran 49 tests … OK".
  - **The comparison:** it took about 1 s, and controls G0–G4 passed.
- **The readout** is `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee`, schema `fd-g-readout/2`.
- **Binding §3 item 3:** the run without an extra block was not made. The variant record carries C_total + V_g.

## 1. The steps

| step | host | start (UTC) | end | rc | wall | result |
|---|---|---|---|---:|---:|---|
| §2.1 deploy and tests | login37 | 10:15:41 | 10:16:43 | 0 | 62 s | `$B=/pscratch/sd/j/josephrb/fd-g-20261025` absent before; HEAD `c4396756…`; porcelain 0 before and after; every §8 digest matches (`fd_g_compare.py` `0a3c09cd…`, tests `b4d0ff26…`), and the declaration's is `e5445e25…`, the binding's; `tests rc=0`, "Ran 49 tests in 21.490s", OK |
| §2.2 the comparison | login37 | 10:16:49 | 10:16:50 | 0 | 1 s | G0–G4 PASS (15 lines); readout written; `g.err` empty |

All on 2026-10-26.

**The start time.** The deploy start, 10:15:41, is the local stamp at the moment the script was sent
(`g1-launch.txt`). `deploy.log`'s first stamp, 10:16:16, comes after the clone.

**The scripts,** under `fd/receipts-g/`:
- `g1.sh` is FD-G §2.1 verbatim, with a guard that refuses if `$B` exists;
- `g2.sh` is §2.2 with the binding's five arguments, exactly:
  `--extra-block /pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a --extra-block-key C_resp --extra-block-name C_resp --extra-block-role adopted`.
  It adds guards that refuse unless `deploy.log` shows `tests rc=0`, and refuse if the readout exists.
- The readout's `argv` records the same arguments.

**`$B` after the run** (`post-run.txt`): the deploy clone, `logs/`, `tmp/` and `fd_g_readout.json`, 1000 MB in all.
No step script names a CFS path.

**Controls, from `g.out`:**
- **G0:** the S1 assembly, the definition, the three records, the five predictions and `cresp.npz` match their digests.
- **G1:** every prediction's structure is as declared.
- **G2:** S1's shapes, U, f > 0, f = x, C_total = C_e + C_model_abs, the committed σ, and C_total positive definite
  with rank 16. Then, for C_resp: finite 16 × 16, symmetric, PSD, and C_total + C_resp positive definite.
- **G3:** GiBUU's eight cells are the p_∥ < 4.5 boxes.
- **G4:** every prediction's integrals are positive on its cells.

## 2. χ² by prediction

There is no reading of these numbers.
- **The reported comparison** is against C_total + C_resp + V_g. The **variant without C_resp** is against
  C_total + V_g.
- **The shape-only form** adds 100 f fᵀ, a free normalization along f with ndf n − 1. The readout prints its
  mode-direction note beside each one: a mode along g would differ, by 2.4 % on 16 cells and 7 % on 8 cells, in
  review A's synthetic check.
- **GiBUU** is on the eight p_∥ < 4.5 cells only.
- **Matrix names are shortened here:** the readout's strings also carry "(free normalization)" on the shape-only
  matrix and write fᵀ as `f^T`. Prediction names are shown in words (GENIE CV for `genie_cv`, and so on).

| prediction | cells | comparison | statistic | χ² | ndf | p | matrix | size | rank |
|---|---:|---|---|---:|---:|---:|---|---|---:|
| GENIE CV | 16 | reported | total | 109.35 | 16 | 5.95e-16 | C_total + C_resp + V_g | 16×16 | 16 |
| GENIE CV | 16 | reported | shape-only | 108.51 | 15 | 3.12e-16 | C_total + C_resp + V_g + 100 f fᵀ | 16×16 | 16 |
| GENIE CV | 16 | without C_resp | total | 160.62 | 16 | 6.19e-26 | C_total + V_g | 16×16 | 16 |
| GENIE CV | 16 | without C_resp | shape-only | 158.70 | 15 | 4.46e-26 | C_total + V_g + 100 f fᵀ | 16×16 | 16 |
| GENIE+MEC | 16 | reported | total | 272.12 | 16 | 1.47e-48 | C_total + C_resp + V_g | 16×16 | 16 |
| GENIE+MEC | 16 | reported | shape-only | 258.07 | 15 | 2.69e-46 | C_total + C_resp + V_g + 100 f fᵀ | 16×16 | 16 |
| GENIE+MEC | 16 | without C_resp | total | 318.26 | 16 | 4.18e-58 | C_total + V_g | 16×16 | 16 |
| GENIE+MEC | 16 | without C_resp | shape-only | 305.26 | 15 | 4.51e-56 | C_total + V_g + 100 f fᵀ | 16×16 | 16 |
| NuWro | 16 | reported | total | 188.03 | 16 | 2.06e-31 | C_total + C_resp + V_g | 16×16 | 16 |
| NuWro | 16 | reported | shape-only | 188.00 | 15 | 5.77e-32 | C_total + C_resp + V_g + 100 f fᵀ | 16×16 | 16 |
| NuWro | 16 | without C_resp | total | 298.69 | 16 | 4.76e-54 | C_total + V_g | 16×16 | 16 |
| NuWro | 16 | without C_resp | shape-only | 298.64 | 15 | 1.07e-54 | C_total + V_g + 100 f fᵀ | 16×16 | 16 |
| GiBUU | 8 | reported | total | 58.46 | 8 | 9.32e-10 | C_total + C_resp + V_g | 8×8 | 8 |
| GiBUU | 8 | reported | shape-only | 27.69 | 7 | 0.00025 | C_total + C_resp + V_g + 100 f fᵀ | 8×8 | 8 |
| GiBUU | 8 | without C_resp | total | 68.44 | 8 | 1.01e-11 | C_total + V_g | 8×8 | 8 |
| GiBUU | 8 | without C_resp | shape-only | 36.15 | 7 | 6.8e-06 | C_total + V_g + 100 f fᵀ | 8×8 | 8 |
| MnvTune v1 (prior) | 16 | reported | total | 329.72 | 16 | 1.73e-60 | C_total + C_resp + V_g | 16×16 | 16 |
| MnvTune v1 (prior) | 16 | reported | shape-only | 311.19 | 15 | 2.63e-57 | C_total + C_resp + V_g + 100 f fᵀ | 16×16 | 16 |
| MnvTune v1 (prior) | 16 | without C_resp | total | 360.79 | 16 | 5.8e-67 | C_total + V_g | 16×16 | 16 |
| MnvTune v1 (prior) | 16 | without C_resp | shape-only | 341.29 | 15 | 1.39e-63 | C_total + V_g + 100 f fᵀ | 16×16 | 16 |

**Each prediction carries its label from the readout:**
- **GENIE CV:** "GENIE 2.12.10 CV, no MEC; CH".
- **GENIE+MEC:** "GENIE 2.12.10 + Valencia MEC; CH".
- **NuWro:** "NuWro 21.09; C12 target; no correction to CH applied".
- **GiBUU:** "GiBUU 2019; C12 target; no correction to CH applied; no events above E_ν = 20 GeV (KNOWN_ISSUES 82)",
  so it is compared on the eight p_∥ < 4.5 cells only.
- **MnvTune v1:** "MINERvA Tune v1, the analysis MC truth: prior (not an independent prediction)".

**The covariance label also says:** each C_model,5D vertex is a data shift, unfolded with a prior reweighted by that
generator's ratio to GENIE 2.12.10 CV. So the GENIE+MEC, NuWro and GiBUU comparisons each carry a covariance built
partly from the compared generator, and so does the GENIE CV comparison, through the ratios' reference (FD-G §7.3).

## 3. Per-cell pulls

The pull is (f − g)/√M_cc. Each entry is reported / without C_resp. "–" marks a cell not compared.

| cell | GENIE CV | GENIE+MEC | NuWro | GiBUU | MnvTune v1 |
|---|---:|---:|---:|---:|---:|
| R00 | +1.49 / +1.56 | +0.12 / +0.13 | +1.88 / +1.96 | +2.26 / +2.36 | +0.85 / +0.89 |
| R01 | +1.58 / +1.68 | +1.56 / +1.65 | +0.89 / +0.94 | +4.06 / +4.30 | +1.85 / +1.96 |
| R02 | −0.87 / −0.89 | −1.09 / −1.11 | +0.75 / +0.76 | +3.74 / +3.83 | −0.27 / −0.27 |
| R03 | −0.00 / −0.00 | +0.06 / +0.06 | −0.72 / −0.73 | +3.53 / +3.57 | +1.21 / +1.22 |
| R04 | +1.99 / +2.02 | −0.61 / −0.62 | +2.17 / +2.20 | – | +0.59 / +0.60 |
| R05 | +1.95 / +2.23 | +2.26 / +2.59 | −0.61 / −0.70 | – | +2.47 / +2.84 |
| R06 | −2.51 / −2.64 | −3.13 / −3.28 | +1.35 / +1.42 | – | −1.69 / −1.78 |
| R07 | −0.30 / −0.31 | +0.11 / +0.11 | −1.59 / −1.62 | – | +1.72 / +1.75 |
| R08 | +2.77 / +3.38 | +2.21 / +2.69 | +3.83 / +4.67 | +2.80 / +3.33 | +3.24 / +3.95 |
| R09 | +1.02 / +1.09 | +0.97 / +1.04 | +2.48 / +2.66 | +2.51 / +2.68 | +1.86 / +1.99 |
| R10 | +0.86 / +0.90 | +0.73 / +0.77 | +2.28 / +2.40 | +4.40 / +4.63 | +1.94 / +2.05 |
| R11 | +0.29 / +0.30 | +0.28 / +0.29 | +0.78 / +0.80 | +1.09 / +1.12 | +1.31 / +1.34 |
| R12 | +2.43 / +2.58 | +1.85 / +1.96 | +3.01 / +3.19 | – | +2.28 / +2.41 |
| R13 | +0.40 / +0.40 | +0.29 / +0.30 | +0.87 / +0.88 | – | +1.59 / +1.62 |
| R14 | +3.17 / +3.37 | +2.91 / +3.10 | +3.94 / +4.19 | – | +3.68 / +3.92 |
| R15 | +0.57 / +0.58 | +0.38 / +0.39 | +2.22 / +2.26 | – | +1.73 / +1.76 |

No threshold is declared for G's pulls (FD-G §7, the director's ruling 4). The table gives them without a count.

## 4. g/f − 1 per cell, in %

| cell | GENIE CV | GENIE+MEC | NuWro | GiBUU | MnvTune v1 |
|---|---:|---:|---:|---:|---:|
| R00 | −10.6 | −0.9 | −13.3 | −16.3 | −6.0 |
| R01 | −11.2 | −11.0 | −6.3 | −28.8 | −13.1 |
| R02 | +12.2 | +15.3 | −10.5 | −52.4 | +3.7 |
| R03 | +0.0 | −0.8 | +9.1 | −44.6 | −15.2 |
| R04 | −8.4 | +2.6 | −9.1 | – | −2.5 |
| R05 | −14.7 | −17.1 | +4.6 | – | −18.4 |
| R06 | +15.0 | +18.7 | −8.0 | – | +10.0 |
| R07 | +2.4 | −0.9 | +12.8 | – | −13.7 |
| R08 | −17.4 | −13.8 | −24.0 | −18.6 | −20.3 |
| R09 | −6.4 | −6.1 | −15.5 | −15.7 | −11.6 |
| R10 | −7.4 | −6.3 | −19.6 | −38.1 | −16.7 |
| R11 | −4.0 | −3.9 | −10.7 | −15.0 | −17.9 |
| R12 | −16.2 | −12.3 | −20.0 | – | −15.1 |
| R13 | −4.4 | −3.2 | −9.6 | – | −17.6 |
| R14 | −16.9 | −15.5 | −20.9 | – | −19.4 |
| R15 | −4.5 | −3.1 | −17.6 | – | −13.7 |

## 5. σ/f per cell, in %

| cell | √(C_total + C_resp)/f | √C_total/f | √V_g/f: GENIE CV | GENIE+MEC | NuWro | GiBUU | MnvTune v1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| R00 | 7.10 | 6.79 | 0.25 | 0.27 | 0.21 | 1.32 | 0.05 |
| R01 | 7.10 | 6.69 | 0.33 | 0.34 | 0.28 | 0.29 | 0.04 |
| R02 | 14.00 | 13.69 | 0.65 | 0.67 | 0.49 | 0.41 | 0.11 |
| R03 | 12.64 | 12.50 | 0.75 | 0.75 | 0.66 | 0.50 | 0.12 |
| R04 | 4.20 | 4.14 | 0.29 | 0.30 | 0.25 | – | 0.05 |
| R05 | 7.47 | 6.49 | 1.10 | 1.18 | 1.27 | – | 0.09 |
| R06 | 5.89 | 5.60 | 0.98 | 1.02 | 0.84 | – | 0.13 |
| R07 | 7.98 | 7.82 | 1.17 | 1.15 | 1.12 | – | 0.15 |
| R08 | 6.25 | 5.13 | 0.38 | 0.39 | 0.31 | 2.23 | 0.07 |
| R09 | 6.26 | 5.84 | 0.33 | 0.33 | 0.27 | 0.38 | 0.04 |
| R10 | 8.59 | 8.16 | 0.53 | 0.54 | 0.42 | 1.15 | 0.09 |
| R11 | 13.69 | 13.39 | 0.65 | 0.66 | 0.53 | 0.99 | 0.11 |
| R12 | 6.63 | 6.25 | 0.46 | 0.46 | 0.37 | – | 0.06 |
| R13 | 11.07 | 10.87 | 0.90 | 0.93 | 0.76 | – | 0.09 |
| R14 | 5.27 | 4.94 | 0.81 | 0.83 | 0.70 | – | 0.04 |
| R15 | 7.94 | 7.77 | 0.72 | 0.72 | 0.53 | – | 0.08 |

**How the two covariance columns check:**
- **Median, min, max:** 7.29, 4.20, 14.00 % with C_resp, and 6.74, 4.14, 13.69 % without.
- **Against CRESP-REPORT:** both columns equal `CRESP-REPORT.md` §2's C_total_resp and C_total per cell.
- **Quadrature:** the squared σ with C_resp equals the squared σ without it plus C_resp's
  (`extra_block.relative_sigma`), to 6 × 10⁻¹⁶ relative.
- **Across predictions:** the covariance σ is the same for all five on every shared cell.

**MC events in the compared cells.** Three medians are half-integers in the readout (GENIE CV 33,887.5, NuWro
42,520.5, MnvTune v1 1,087,758.5). They are rounded half to even here.

| prediction | median | min | max |
|---|---:|---:|---:|
| GENIE CV | 33,888 | 11,477 | 164,963 |
| GENIE+MEC | 33,658 | 10,949 | 181,633 |
| NuWro | 42,520 | 17,550 | 230,973 |
| GiBUU | 58,901 | 18,112 | 137,626 |
| MnvTune v1 | 1,087,758 | 360,147 | 5,772,542 |

## 6. GiBUU above p_∥ 4.5

- **The readout's GiBUU record** holds eight cells, R00–R03 and R08–R11, and its only ndf values are 8 and 7, in both
  the reported comparison and the variant.
- **No GiBUU value on R04–R07 or R12–R15 appears,** in the readout, on stdout or in this report. The tests show that
  the tool never forms one (FD-G §5).

## 7. What is committed

- **The readout:** [`fd/readout/fd_g_readout.json`](fd/readout/fd_g_readout.json), sha256 `75a9ddee…`.
  - As declared, this stage is unguarded, so the readout carries f, g and f − g.
  - `code_sha256` names `fd_g_compare.py` `0a3c09cd…`.
- **Receipts:** [`fd/receipts-g/`](fd/receipts-g/), with a `SHA256SUMS`:
  - the deploy log and test log;
  - `g.out`, `g.err` and the start/end stamps;
  - `post-run.txt`;
  - the two scripts and their stdout;
  - `summarize_g.py`, which reads only the readout, and its output `summary.txt`. The tables in §§2–5 are from it,
    with the names shortened as §2 says; §1's are from the receipts.
- **The ledger:** two rows in `fd/LEDGER.tsv`.
- **The results index:** this branch's first commit adds the readout and the index regenerated from it, under the
  director's standing ruling (a). The PR body gives the scope.

## 8. Retention

`$B=/pscratch/sd/j/josephrb/fd-g-20261025` (1000 MB, mostly the deploy clone) is on the pscratch retention list
re-raised before 2026-11-20. Its readout is in git.

## Not changed

S1's covariance, C_model,5D, C_resp, R00–R15, κ = 1, the route decision, and F0's and F0b's records. The reading of
these comparisons, any claim, printed wording and publication are Joseph's.
