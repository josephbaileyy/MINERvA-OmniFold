# REPORT: the 5B run-period block's addition, C_total + C_resp + C_PL,5D (2026-10-31)

**By** the measurement session `coverage-5b-audit`, for the director.

**Under** [`FD-CT-5B-ADDITION-BINDING.md`](FD-CT-5B-ADDITION-BINDING.md) (PR #595), which binds
[`FD-CT-5B-ADDITION-DECLARATION.md`](FD-CT-5B-ADDITION-DECLARATION.md) (`881e7ad80aa308e3…`) at deploy pin `3b12c451`,
under `DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md` item 2, after the audit's `stop` = false
([`FD-CT-5B-AUDIT-REPORT.md`](FD-CT-5B-AUDIT-REPORT.md)).

**The addition followed the data.** The block was built after the period double ratios were seen. Its audit's stop
condition was fixed before any audit number was read, and it did not fire. The block is added because of that outcome,
and every product is published with and without it (decision item 2; binding ruling 2).

**MEASURES:**
- the bound deploy and tests, and the single chain run, with their receipts;
- every control's outcome;
- every product's digest, before (committed, unchanged) and after (with the block, written beside it);
- the with-and-without numbers, copied from the chain's own table and by `make_addition_report_tables.py`.

**CANNOT AUTHORIZE, and draws no reading on:**
- any change to the paper, the note or `docs/analysis-note/**`. That is the paper lane's step, with results printed
  with and without the block (binding);
- what the with-and-without differences mean;
- 1B's matrix, which stays `fd_data_product.json` `b79556f0…` (binding ruling 3).

**CITABLE FOR:**
- that the chain ran once as bound, with every control passed;
- the revised products and their digests;
- the with-and-without numbers, each labelled with its matrix.

**NOT CITABLE FOR** (the block's label, declaration §2): a validated size for C_PL,5D, since a block built from the observed differences contains them by construction; the cause of a period difference, or which period is right; a coverage or calibration statement.

**Receipts:** [`fd/receipts-ct/5b/addition/run/`](fd/receipts-ct/5b/addition/run/):
- the step scripts `s1_deploy.sh` and `s2_chain.sh`. The chain's argv is the declaration's §6 command, verbatim;
- `chain.json`, the receipt of every step and check (`1dc0dc2e…`);
- `logs/`: the deploy, its tests, the chain, and every step's `.out` and `.err`;
- `pins/`: every pin set passed in-process;
- `make_addition_report_tables.py` and its output `report-tables.md`, from which every table below is copied.

**The revised products** are in [`fd/with-cpl/`](fd/with-cpl/): `block/`, `readout/`, `data-product/`,
`deposit-candidate/`, `figures/` and `table/`. Nothing in `fd/readout/`, `fd/data-product/`, `fd/deposit-candidate/`,
`fd/figures/` or `docs/analysis-note/` changed: `git diff origin/main` on those paths is empty.

## 0. Summary

- **Deploy and tests** (binding §3): all held. HEAD was the pin, with 0/0 porcelain lines, the declaration's sha256
  `881e7ad8…`, 15 of 15 §8.1 pins, and "**Ran 419 tests in 682.531s, OK**" with **no skip** (§1).
- **The chain:** once, on login37, 2026-10-31T20:59:06Z–21:03:39Z (4 min 33 s), exit 0, at 0 node-h. 24 steps all exited
  0, and all 35 checks passed (§2).
- **Control R:** every committed product is reproduced without the block at the deploy pin, under the exclusions the
  binding quotes. So the with-and-without differences are the block's alone (§2).
- **The revised matrix:** `cpl_block.npz` `d9aa32fd…`, rank 2. C_PL,5D's trace share of M + P is 0.060905, beside 5B's
  0.0609.
- **The largest χ² fall** is NuWro's shape-only, 0.3951 of its value without the block (arithmetic, by the generator),
  inside the audit's ceiling of 0.7261 (§3).
- **The next step** is the paper lane's: the note and the paper, through the usual truth and register checks.

## 1. Deploy and tests

- `s1_deploy.sh` on login37, 2026-10-31T20:47:21Z–20:58:55Z (694 s; `logs/deploy.log`).
- `BA=/pscratch/sd/j/josephrb/fd-ct-5b-addition-20261031` and `D=$BA/deploy/3b12c451`.
<!-- absence-ok: s1_deploy.sh exits 2 with "STOP: $BA exists" when $BA exists, and it reached its clone step (deploy.log); an `ls -d` on login37 just before returned "No such file or directory" -->
- `$BA` did not exist beforehand.
- A clean clone, detached at `3b12c451d617b860450f516b3b63266379308f80`: HEAD equals the pin, with 0 porcelain
  (`--ignored`) lines before the tests and 0 after.
- The declaration's sha256 is `881e7ad80aa308e33b811bbc6b42664f8bfa8d610e6cbe789e0f7e3b9dd23e30`, and all 15 §8.1 pins
  match (`pins 15 mismatches 0`).
- The nine test modules ran with root_6_28 activated by prefix (Python 3.11.14): `tests rc=0`, "Ran 419 tests in
  682.531s, OK", `skipped_lines 0`.

## 2. The chain

`s2_chain.sh` ran §6's command once. It refused to start unless the deploy log showed tests rc=0, 15/0 pins and 0
skipped lines. After the chain, the deploy's porcelain is still 0 lines. Every step's tool, exit code, time and the pins
passed in-process:

| arm | step | tool | rc | wall (s) | start (UTC) | pins passed in-process |
|---|---|---|---:|---:|---|---|
| without | f0b | `fd_f0_regrade` | 0 | 104.2 | 2026-10-31T20:59:09Z | — |
| without | f1 | `fd_f0_regrade` | 0 | 44.7 | 2026-10-31T21:00:53Z | — |
| without | g | `fd_g_compare` | 0 | 0.5 | 2026-10-31T21:01:38Z | — |
| without | g_diag | `fd_g_diag` | 0 | 0.7 | 2026-10-31T21:01:38Z | — |
| without | g_followup | `fd_g_followup` | 0 | 0.7 | 2026-10-31T21:01:39Z | — |
| without | g_sens2 | `fd_g_followup` | 0 | 0.7 | 2026-10-31T21:01:40Z | — |
| without | flux_boot | `fd_flux_boot` | 0 | 5.6 | 2026-10-31T21:01:41Z | — |
| without | data_product | `fd_data_product` | 0 | 0.5 | 2026-10-31T21:01:46Z | — |
| without | deposit_build | `fd_deposit_candidate` | 0 | 0.4 | 2026-10-31T21:01:47Z | — |
| without | figures | `fd_g_figures` | 0 | 6.0 | 2026-10-31T21:01:47Z | — |
| with | block | `fd_cpl_addition` | 0 | 0.5 | 2026-10-31T21:01:53Z | — |
| with | f0b | `fd_f0_regrade` | 0 | 43.4 | 2026-10-31T21:01:54Z | — |
| with | f1 | `fd_f0_regrade` | 0 | 46.3 | 2026-10-31T21:02:37Z | — |
| with | g | `fd_g_compare` | 0 | 0.7 | 2026-10-31T21:03:23Z | — |
| with | g_diag | `fd_g_diag` | 0 | 0.7 | 2026-10-31T21:03:24Z | s1_npz `db000707`, s1_json `81e5ef3f`, cmodel_json `3cfdc6a5`, g_readout `b55366b3` |
| with | g_followup | `fd_g_followup` | 0 | 0.9 | 2026-10-31T21:03:25Z | s1_npz `db000707`, s1_json `81e5ef3f`, cmodel_json `3cfdc6a5`, g_readout `b55366b3`, g_diag_readout `bfd529ab` |
| with | g_sens2 | `fd_g_followup` | 0 | 0.6 | 2026-10-31T21:03:26Z | s1_npz `db000707`, s1_json `81e5ef3f`, cmodel_json `3cfdc6a5`, g_readout `b55366b3`, g_followup_readout `5c95c6d0` |
| with | flux_boot | `fd_flux_boot` | 0 | 4.3 | 2026-10-31T21:03:26Z | s1_npz `db000707`, s1_json `81e5ef3f`, cmodel_json `3cfdc6a5`, g_readout `b55366b3` |
| with | data_product | `fd_cpl_addition` | 0 | 0.5 | 2026-10-31T21:03:31Z | data_product `b79556f0`, block_npz `d9aa32fd`, block_json `4023746e`, g_readout `b55366b3`, audit_json `6d34d7f8` |
| with | deposit_build | `fd_deposit_candidate` | 0 | 0.6 | 2026-10-31T21:03:31Z | data_product `d6752d2c`, g_readout `b55366b3` (variant with-cpl) |
| with | deposit_check | `fd_deposit_candidate` | 0 | 0.5 | 2026-10-31T21:03:32Z | data_product `d6752d2c`, g_readout `b55366b3` (variant with-cpl) |
| with | figures | `fd_g_figures` | 0 | 5.7 | 2026-10-31T21:03:33Z | g_readout `b55366b3`, g_diag_readout `bfd529ab`, g_followup_readout `5c95c6d0`, g_sens2_readout `cff60b63`, f0b_readout `5f542830` |
| with | figures_check | `fd_g_figures_check` | 0 | 0.1 | 2026-10-31T21:03:39Z | — |
| with | table | `fd_cpl_addition` | 0 | 0.7 | 2026-10-31T21:03:39Z | f0b_without `b9db935a`, f1_without `cbe411a9`, g_without `75a9ddee`, g_diag_without `680dc5ef`, g_followup_without `cd82517a`, g_sens2_without `0f6568ab`, flux_boot_without `b7b5652c`, data_product_without `b79556f0`, f0b_with `5f542830`, f1_with `5ccc89e5`, g_with `b55366b3`, g_diag_with `bfd529ab`, g_followup_with `5c95c6d0`, g_sens2_with `cff60b63`, flux_boot_with `7d117515`, data_product_with `d6752d2c` |

**The with arm's pins chain as declared.** Each downstream step's pins are its defaults with only the upstream sha256
replaced, by the digest of the file the step before wrote: `b55366b3…` (Stage G), `bfd529ab…` (G-DIAG), `5c95c6d0…`
(G-FOLLOWUP), `cff60b63…` (G-SENS2), `5f542830…` (F0b), `d6752d2c…` (the data product). F1's `--f0b-readout-sha256`
was step F0b's digest (`pins/` and `chain.json`).

**Every check:**

- PASS R f0b: the committed readout is the pinned bytes
- PASS R f1: the committed readout is the pinned bytes
- PASS R g: the committed readout is the pinned bytes
- PASS R g_diag: the committed readout is the pinned bytes
- PASS R g_followup: the committed readout is the pinned bytes
- PASS R g_sens2: the committed readout is the pinned bytes
- PASS R flux_boot: the committed readout is the pinned bytes
- PASS R data_product: the committed readout is the pinned bytes
- PASS R f0b: every number and the structure are the committed readout's
- PASS R f1: every number and the structure are the committed readout's
- PASS R g: every number and the structure are the committed readout's
- PASS R g_diag: every number and the structure are the committed readout's
- PASS R g_followup: every number and the structure are the committed readout's
- PASS R g_sens2: every number and the structure are the committed readout's
- PASS R flux_boot: every number and the structure are the committed readout's
- PASS R data_product: every CSV is the committed product's, byte for byte
- PASS R data_product: its JSON is the committed one but argv
- PASS R deposit cells.csv: the committed file
- PASS R deposit covariance.csv: the committed file
- PASS R deposit correlation.csv: the committed file
- PASS R deposit deposit.json: the committed file but code_sha256 (without_code)
- PASS R deposit predictions-reference.json: the committed file but code_sha256 (without_code)
- PASS R figure fd_g_fig_ratio: its sidecar is the committed one but argv, code and versions; the PDF the same bytes
- PASS R figure fd_g_fig_modes: its sidecar is the committed one but argv, code and versions; the PDF the same bytes
- PASS R figure fd_g_fig_sens: its sidecar is the committed one but argv, code and versions; the PDF the same bytes
- PASS C block: its readout names the npz it wrote
- PASS C f0b: the readout names the combined block's sha256, and each upstream readout's as written
- PASS C f1: the readout names the combined block's sha256, and each upstream readout's as written
- PASS C g: the readout names the combined block's sha256, and each upstream readout's as written
- PASS C g_diag: the readout names the combined block's sha256, and each upstream readout's as written
- PASS C g_followup: the readout names the combined block's sha256, and each upstream readout's as written
- PASS C g_sens2: the readout names the combined block's sha256, and each upstream readout's as written
- PASS C flux_boot: the readout names the combined block's sha256, and each upstream readout's as written
- PASS S g: every prediction's sigma_total_over_f is sqrt(diag(C_rep))/f
- PASS S f0b: its sqrt(diag(C_total + X))/f is sqrt(diag(C_rep))/f

## 3. With and without

**Every product, before and after.** The before files are the committed products, unchanged. The after files are the
revised ones, written beside them:

| product | before | sha256 | after | sha256 |
|---|---|---|---|---|
| readout fd_f0b_readout.json | `fd/readout/fd_f0b_readout.json` | `b9db935a3187646b…` | `fd/with-cpl/readout/fd_f0b_readout.json` | `5f542830561731b5…` |
| readout fd_f1_readout.json | `fd/readout/fd_f1_readout.json` | `cbe411a926a7392e…` | `fd/with-cpl/readout/fd_f1_readout.json` | `5ccc89e58096a14a…` |
| readout fd_g_readout.json | `fd/readout/fd_g_readout.json` | `75a9ddee19a7affe…` | `fd/with-cpl/readout/fd_g_readout.json` | `b55366b3fd2d35a5…` |
| readout fd_g_diag_readout.json | `fd/readout/fd_g_diag_readout.json` | `680dc5ef9c40b1ab…` | `fd/with-cpl/readout/fd_g_diag_readout.json` | `bfd529ab67ddf6e9…` |
| readout fd_g_followup_readout.json | `fd/readout/fd_g_followup_readout.json` | `cd82517afdfb1dc8…` | `fd/with-cpl/readout/fd_g_followup_readout.json` | `5c95c6d0f43ba028…` |
| readout fd_g_sens2_readout.json | `fd/readout/fd_g_sens2_readout.json` | `0f6568aba032e5d9…` | `fd/with-cpl/readout/fd_g_sens2_readout.json` | `cff60b63a951834d…` |
| readout fd_flux_boot_readout.json | `fd/readout/fd_flux_boot_readout.json` | `b7b5652cbd163b68…` | `fd/with-cpl/readout/fd_flux_boot_readout.json` | `7d11751577d4b2db…` |
| data product (JSON) | `fd/data-product/fd_data_product.json` | `b79556f0538c8194…` | `fd/with-cpl/data-product/fd_data_product_cpl.json` | `d6752d2c64aad442…` |
| data product C_e | `fd/data-product/fd_data_product_C_e.csv` | `222c4dd4efef0780…` | `fd/with-cpl/data-product/fd_data_product_cpl_C_e.csv` | `222c4dd4efef0780…` |
| data product C_model_abs | `fd/data-product/fd_data_product_C_model_abs.csv` | `ad179dea32b13600…` | `fd/with-cpl/data-product/fd_data_product_cpl_C_model_abs.csv` | `ad179dea32b13600…` |
| data product C_resp | `fd/data-product/fd_data_product_C_resp.csv` | `35bfcb2a332b8b5a…` | `fd/with-cpl/data-product/fd_data_product_cpl_C_resp.csv` | `35bfcb2a332b8b5a…` |
| data product C_total_plus_C_resp | `fd/data-product/fd_data_product_C_total_plus_C_resp.csv` | `20a4b9d8e41c2b53…` | `fd/with-cpl/data-product/fd_data_product_cpl_C_total_plus_C_resp.csv` | `20a4b9d8e41c2b53…` |
| data product cells | `fd/data-product/fd_data_product_cells.csv` | `e7582bfec1f572df…` | `fd/with-cpl/data-product/fd_data_product_cpl_cells.csv` | `b3a7d0cac19ab3ca…` |
| data product reported matrix | `fd/data-product/fd_data_product_C_total_plus_C_resp.csv` | `20a4b9d8e41c2b53…` | `fd/with-cpl/data-product/fd_data_product_cpl_C_total_plus_C_resp_plus_C_PL5D.csv` | `76730c5b7143f893…` |
| data product its correlation | `fd/data-product/fd_data_product_corr_C_total_plus_C_resp.csv` | `838f16617ed88f86…` | `fd/with-cpl/data-product/fd_data_product_cpl_corr_C_total_plus_C_resp_plus_C_PL5D.csv` | `262e3a5b289a5620…` |
| data product C_PL5D | — | — | `fd/with-cpl/data-product/fd_data_product_cpl_C_PL5D.csv` | `03babead4dff1bf1…` |
| deposit cells.csv | `fd/deposit-candidate/cells.csv` | `640a0f931cd3c368…` | `fd/with-cpl/deposit-candidate/cells.csv` | `0b01400174ad99c6…` |
| deposit covariance.csv | `fd/deposit-candidate/covariance.csv` | `20a4b9d8e41c2b53…` | `fd/with-cpl/deposit-candidate/covariance.csv` | `76730c5b7143f893…` |
| deposit correlation.csv | `fd/deposit-candidate/correlation.csv` | `838f16617ed88f86…` | `fd/with-cpl/deposit-candidate/correlation.csv` | `262e3a5b289a5620…` |
| deposit deposit.json | `fd/deposit-candidate/deposit.json` | `36738b459292592a…` | `fd/with-cpl/deposit-candidate/deposit.json` | `67e6c22d915f4d7e…` |
| deposit predictions-reference.json | `fd/deposit-candidate/predictions-reference.json` | `ee2ee08f7346fc3b…` | `fd/with-cpl/deposit-candidate/predictions-reference.json` | `cc94168ea9146d88…` |
| figure fd_g_fig_ratio.pdf | `fd/figures/fd_g_fig_ratio.pdf` | `6372244f9e15f065…` | `fd/with-cpl/figures/fd_g_fig_ratio.pdf` | `b57cbb2ca95df8c9…` |
| figure fd_g_fig_ratio.json | `fd/figures/fd_g_fig_ratio.json` | `d91d2a29e1eb4cb3…` | `fd/with-cpl/figures/fd_g_fig_ratio.json` | `d885f3d4ec19b0ac…` |
| figure fd_g_fig_modes.pdf | `fd/figures/fd_g_fig_modes.pdf` | `5421815f4dfdfb4c…` | `fd/with-cpl/figures/fd_g_fig_modes.pdf` | `980351edbfe1294a…` |
| figure fd_g_fig_modes.json | `fd/figures/fd_g_fig_modes.json` | `d567dd6fff01d355…` | `fd/with-cpl/figures/fd_g_fig_modes.json` | `c7f607e2b05ba51f…` |
| figure fd_g_fig_sens.pdf | `fd/figures/fd_g_fig_sens.pdf` | `96af0ed9dc2be870…` | `fd/with-cpl/figures/fd_g_fig_sens.pdf` | `662e09acaf915ebc…` |
| figure fd_g_fig_sens.json | `fd/figures/fd_g_fig_sens.json` | `dc40d8e1a79221c9…` | `fd/with-cpl/figures/fd_g_fig_sens.json` | `aafac37e6901ac7f…` |
| block cpl_block.npz | — | — | `fd/with-cpl/block/cpl_block.npz` | `d9aa32fdb6435776…` |
| block cpl_block.json | — | — | `fd/with-cpl/block/cpl_block.json` | `4023746e3a819e8c…` |
| table fd_cpl_table.json | — | — | `fd/with-cpl/table/fd_cpl_table.json` | `eb786bcf41f1fa2f…` |
| table fd_cpl_table.md | — | — | `fd/with-cpl/table/fd_cpl_table.md` | `08f76b4d4b1977de…` |

- **What the with-block data product carries:** C_e, C_model_abs, C_resp and C_total_plus_C_resp, byte-identical to the
  committed product's CSVs (the same sha256 above), plus C_PL5D, the revised matrix and its correlation.
- **The with-block deposit candidate:** its covariance and correlation are the revised matrix's (`76730c5b…`,
  `262e3a5b…`).

**The numbers,** from `fd/with-cpl/table/fd_cpl_table.md`, verbatim. Each without number is the committed readout's,
and each with number is the with arm's:

**sigma/f per cell**

| cell | without | C_PL5D | with | with / without |
|---|---:|---:|---:|---:|
| R00 | 7.097% | 0.400% | 7.108% | 1.0016 |
| R01 | 7.095% | 2.706% | 7.594% | 1.0702 |
| R02 | 14.004% | 1.137% | 14.050% | 1.0033 |
| R03 | 12.637% | 1.502% | 12.726% | 1.0070 |
| R04 | 4.203% | 2.313% | 4.797% | 1.1414 |
| R05 | 7.475% | 3.165% | 8.117% | 1.0860 |
| R06 | 5.891% | 2.885% | 6.559% | 1.1135 |
| R07 | 7.977% | 2.793% | 8.452% | 1.0595 |
| R08 | 6.255% | 0.279% | 6.261% | 1.0010 |
| R09 | 6.265% | 2.774% | 6.851% | 1.0936 |
| R10 | 8.592% | 1.291% | 8.688% | 1.0112 |
| R11 | 13.686% | 2.361% | 13.888% | 1.0148 |
| R12 | 6.632% | 2.183% | 6.982% | 1.0528 |
| R13 | 11.071% | 2.648% | 11.383% | 1.0282 |
| R14 | 5.265% | 2.131% | 5.680% | 1.0788 |
| R15 | 7.941% | 2.369% | 8.287% | 1.0435 |

**Stage G**

| prediction | kind | ndf | chi2 without | p without | chi2 with | p with |
|---|---|---:|---:|---:|---:|---:|
| genie_cv | total | 16 | 109.354 | 5.95e-16 | 105.417 | 3.31e-15 |
| genie_cv | shape_only | 15 | 108.508 | 3.12e-16 | 100.574 | 1.02e-14 |
| genie_mec | total | 16 | 272.121 | 1.47e-48 | 223.552 | 1.32e-38 |
| genie_mec | shape_only | 15 | 258.073 | 2.69e-46 | 223.463 | 3.49e-39 |
| nuwro | total | 16 | 188.029 | 2.06e-31 | 130.681 | 4.73e-20 |
| nuwro | shape_only | 15 | 187.997 | 5.77e-32 | 113.728 | 3.09e-17 |
| gibuu | total | 8 | 58.463 | 9.32e-10 | 45.255 | 3.29e-07 |
| gibuu | shape_only | 7 | 27.690 | 0.00025 | 24.753 | 0.000839 |
| mnvtune_v1 | total | 16 | 329.716 | 1.73e-60 | 262.060 | 1.73e-46 |
| mnvtune_v1 | shape_only | 15 | 311.190 | 2.63e-57 | 261.875 | 4.42e-47 |

**F0B: each graded truth**

| truth | chi2 without | p without | cells abs(z) > 2 | chi2 with | p with | cells abs(z) > 2 |
|---|---:|---:|---:|---:|---:|---:|
| nominal | 0.002081 | 1 | 0 | 0.001665 | 1 | 0 |
| W1 | 5.013 | 0.996 | 0 | 4.819 | 0.997 | 0 |
| W2 | 0.5676 | 1 | 0 | 0.4975 | 1 | 0 |
| W3 | 30.83 | 0.0141 | 0 | 27.41 | 0.0372 | 0 |
| q3 | 53.42 | 6.44e-06 | 0 | 52.48 | 9.15e-06 | 0 |
| stage0c_gibuu | 25.46 | 0.0621 | 1 | 24.57 | 0.0777 | 0 |
| closure_nuwro | 11.6 | 0.771 | 0 | 10.66 | 0.83 | 0 |
| A7_mnvtune | 0.005458 | 1 | 0 | 0.003143 | 1 | 0 |
| A7_genie_cv | 16.14 | 0.443 | 0 | 15.58 | 0.482 | 0 |
| A7_genie_mec | 14.54 | 0.558 | 0 | 13.65 | 0.625 | 0 |
| A7_nuwro | 24.92 | 0.0713 | 0 | 23.86 | 0.0925 | 0 |
| A7_gibuu | 175.1 | 7.96e-29 | 3 | 171 | 5.3e-28 | 2 |

**F1: each graded truth**

| truth | chi2 without | p without | cells abs(z) > 2 | chi2 with | p with | cells abs(z) > 2 |
|---|---:|---:|---:|---:|---:|---:|
| nominal | 0.002081 | 1 | 0 | 0.001665 | 1 | 0 |
| W1 | 5.013 | 0.996 | 0 | 4.819 | 0.997 | 0 |
| W2 | 0.5676 | 1 | 0 | 0.4975 | 1 | 0 |
| W3 | 30.83 | 0.0141 | 0 | 27.41 | 0.0372 | 0 |
| q3 | 53.42 | 6.44e-06 | 0 | 52.48 | 9.15e-06 | 0 |
| stage0c_gibuu | 25.46 | 0.0621 | 1 | 24.57 | 0.0777 | 0 |
| closure_nuwro | 11.6 | 0.771 | 0 | 10.66 | 0.83 | 0 |
| A7_mnvtune | 0.005458 | 1 | 0 | 0.003143 | 1 | 0 |
| A7_genie_cv | 16.14 | 0.443 | 0 | 15.58 | 0.482 | 0 |
| A7_genie_mec | 14.54 | 0.558 | 0 | 13.65 | 0.625 | 0 |
| A7_nuwro | 24.92 | 0.0713 | 0 | 23.86 | 0.0925 | 0 |
| A7_gibuu | 175.1 | 7.96e-29 | 3 | 171 | 5.3e-28 | 2 |
| F1_genie_v3_g18 | 11.84 | 0.755 | 0 | 9.263 | 0.902 | 0 |
| F1_closure_genie_v3_g18 | 11.44 | 0.782 | 0 | 9.142 | 0.907 | 0 |
| F1_genie_v3_ar23 | 16.86 | 0.395 | 0 | 14.06 | 0.594 | 0 |
| F1_closure_genie_v3_ar23 | 16.05 | 0.449 | 0 | 13.43 | 0.641 | 0 |

**The flux bootstrap: each total chi2's replicate percentiles 16 / 50 / 84**

| variant | prediction | without | with |
|---|---|---|---|
| correlation | genie_cv | 105.97 / 109.60 / 112.45 | 102.21 / 105.67 / 108.23 |
| correlation | genie_mec | 262.37 / 273.34 / 282.71 | 216.80 / 223.85 / 229.43 |
| correlation | nuwro | 185.47 / 188.78 / 190.93 | 128.51 / 130.90 / 132.69 |
| correlation | gibuu | 57.33 / 58.62 / 59.47 | 44.63 / 45.33 / 45.79 |
| correlation | mnvtune_v1 | 314.90 / 332.84 / 350.00 | 252.65 / 263.06 / 271.80 |
| block | genie_cv | 107.59 / 110.34 / 112.83 | 103.54 / 106.37 / 109.08 |
| block | genie_mec | 267.00 / 274.21 / 281.72 | 219.71 / 224.79 / 229.39 |
| block | nuwro | 187.15 / 188.97 / 190.62 | 129.16 / 131.50 / 134.23 |
| block | gibuu | 55.89 / 59.24 / 62.93 | 43.80 / 45.69 / 47.76 |
| block | mnvtune_v1 | 322.30 / 333.80 / 347.09 | 257.97 / 264.38 / 271.29 |

**What the table's pairing could not pair:**
- **The only unpaired committed leaves** are F0b's and F1's `triggers.listed[*].p_lt_0.01`, because the list's length
  changes.
- **Without the block,** it lists q3 (no cells, p < 0.01), stage0c_gibuu (R06) and A7_gibuu (R02, R06, R07, p < 0.01).
- **With the block,** it lists q3 (no cells, p < 0.01) and A7_gibuu (R02, R06, p < 0.01).
- The same counts are in the table's F0b and F1 rows. Every other leaf of every readout is paired: 2203 for F0b, 2626 for
  F1, 861 for Stage G, 6006 for G-DIAG, 3052 for G-FOLLOWUP, 3464 for G-SENS2 and 624 for the flux bootstrap.

## 4. Deviations and notes

- **None from the bound steps.** Each command is the declaration's §6, run once.
- **The step scripts add guards:** `s2_chain.sh` refuses unless the deploy log is clean, writes `chain.start`, and
  prints the deploy's porcelain afterwards.
- **A companion directory for the with-block G-FOLLOWUP readout.** Its item-5 search again lists S1's 20 data-replica
  input names. As for the committed readout (the director's ruling (a), 2026-10-26),
  `fd/with-cpl/readout/fd_g_followup_readout/` holds 20 relative symlinks to S1's tracked copies, with a README, so that
  `verify_receipt_artifacts.py` resolves them: MISSING 0, and the UNRESOLVED inventory is unchanged.
- **The commit regenerates the results index,** by the hook's own rule, because the with-block readouts are in its
  population: `RESULTS-INDEX.tsv`, `RESULTS-POPULATION.tsv` and the generated `docs/analysis-note/records_results_index.tex`.
  Nothing in the note's text changes.
- **The ledger's wall times** are the scripts' timestamps. The deploy took 694 s, mostly its tests on a
  login node at load about 40.

## 5. Ledger, storage and not changed

- **Ledger:** two rows in `fd/LEDGER.tsv`: the deploy and tests, and the chain.
- **Storage:** `$BA` stays on pscratch with the without arm's outputs and F0b's and F1's experiment tables. It joins
  the pscratch retention list. Nothing went to CFS, and there was no Slurm job.
- **Not changed:**
  - every committed readout, data product, deposit file and figure, and the reported matrix C_total + C_resp, until
    the paper lane's step;
  - `docs/analysis-note/**`, claims and printed wording;
  - 1B's matrix.
- Nothing is submitted, deposited or tagged.
