chain.json sha256 1dc0dc2e8acd4246b6ff7f33a5d5ddfb8563b935e3fdf50fc1c6e9bd3d99b5ed; 59 records, 35 checks, all ok: True

## T1 steps

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

## T2 checks (control R on the without arm; C and S on the with arm)

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

## T3 every product, before (committed, unchanged) and after (with the block, beside it)

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

block: npz sha256 d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f; rank 2; trace share of M + P 0.060905; controls ['A', 'L', 'B0', 'B1', 'B2', 'B3']
table leaf counts: f0b 2203, f1 2626, g 861, g_diag 6006, g_followup 3052, g_sens2 3464, flux_boot 624
unpaired committed leaves: f0b: ['/triggers/listed/0/p_lt_0.01', '/triggers/listed/1/p_lt_0.01', '/triggers/listed/2/p_lt_0.01']; f1: ['/triggers/listed/0/p_lt_0.01', '/triggers/listed/1/p_lt_0.01', '/triggers/listed/2/p_lt_0.01']
f0b triggers.listed without: [{'truth': 'q3', 'cells': [], 'p_lt_0.01': True}, {'truth': 'stage0c_gibuu', 'cells': ['R06'], 'p_lt_0.01': False}, {'truth': 'A7_gibuu', 'cells': ['R02', 'R06', 'R07'], 'p_lt_0.01': True}]
f0b triggers.listed with: [{'truth': 'q3', 'cells': [], 'p_lt_0.01': True}, {'truth': 'A7_gibuu', 'cells': ['R02', 'R06'], 'p_lt_0.01': True}]
f1 triggers.listed without: [{'truth': 'q3', 'cells': [], 'p_lt_0.01': True}, {'truth': 'stage0c_gibuu', 'cells': ['R06'], 'p_lt_0.01': False}, {'truth': 'A7_gibuu', 'cells': ['R02', 'R06', 'R07'], 'p_lt_0.01': True}]
f1 triggers.listed with: [{'truth': 'q3', 'cells': [], 'p_lt_0.01': True}, {'truth': 'A7_gibuu', 'cells': ['R02', 'R06'], 'p_lt_0.01': True}]
largest fractional chi2 fall: nuwro shape_only 0.3951 (the audit's ceiling 0.7261)
