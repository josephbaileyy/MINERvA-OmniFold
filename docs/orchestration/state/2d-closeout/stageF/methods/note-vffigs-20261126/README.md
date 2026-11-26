# The note's 5D figures on C_e^infl (V_F), 2026-11-26

**Request.** The director, 2026-11-26: redraw the three 5D figures the note prints from the V_F products, through their own
producers, changing only the inputs. The figures are `fd_g_fig_modes.pdf`, `fived16_headline.pdf` and
`fived16_genresidual.pdf`. Also move `valid_region`'s COV_KEY to the V_F key. These are the figure follow-ups of
`fd/receipts-vf/readings/vf_readings.md` section 5. Local, 0 node-h, no remote host contacted.
**Branch.** Cut from #1378's head (362011d2, JE's V_F note text). JE merges it into #1378, so the figures and the text
they belong with go through CI together.
**Scope.** Figures, their install lines and pins, and the dead-containment exemption that only the old modes figure
needed. No caption, sentence or value is changed here. The captions are #1378's.

| figure | installed before (sha256) | installed now (sha256) | drawn by |
|---|---|---|---|
| fd_g_fig_modes.pdf | 0d6fe57c8554aa05… | 889e175ba938ab5163b55b619e1ce9b3b83031dacbb0f63d106cb2aea44526cc | the V_F phase-1 chain (fd/with-vf/figures/) |
| fived16_headline.pdf | 1002e7056bfe457f… | 7700c4d474b3857d4485699803cbe50c1c7b23483624c1b58072797f6035e297 | tools/make_fig_fived16_headline.py, --variant P |
| fived16_genresidual.pdf | d310e8b946cb6bca… | 4400bd70a3454b23d28e4b1c1f3885a60d2e48cdc6472f5722c5db59abb12b35 | tools/make_fig_fived16_genresidual.py |

The digests of every file in `figs/` are in `figs/SHA256SUMS`.

## fd_g_fig_modes.pdf: installed as committed, not redrawn

- **Source.** The V_F addition's phase-1 chain (FD-VF-ADDITION, bound `fd_vf_addition.py` run, `fd/receipts-vf/p1/run/run/`) already drew it.
  - It ran `fd_g_figures.py` unchanged on the V_F with-arm E readouts, `fd/with-vf/readout/vf-with-E/` and `vf-with-S/fd_f0b_readout.json`.
  - It used `--reported-block-name 'C_resp + C_PL5D + DeltaC_e'`. That name is not drawn in the modes figure.
  - It ran in E-A2's renderer on NERSC: python 3.11.14, numpy 1.26.4, matplotlib 3.10.8.
- **Control.** In the same run, control R redrew the OLD arm, and E-A2's installed file (0d6fe57c8554aa05…) came out byte for byte.
  - The renderer check also passed. All four checks are `ok` in `chain.json`.
  - The V_F file is `fd/with-vf/figures/fd_g_fig_modes.pdf`, 889e175ba938ab5163b55b619e1ce9b3b83031dacbb0f63d106cb2aea44526cc.
- **A local redraw cannot reproduce those bytes.** The rerun used the chain's own entry, `fd_gencmp_e.BOOT` with the committed pins and prediction set, in `figenv/rootmpl3108` (python 3.11.18, numpy 1.26.4, matplotlib 3.10.8).
  - Each arm's sidecar equals the committed one, except for argv, code, versions and the PDF digest: every plotted value and every drawn text is the same.
  - `fd_g_figures_check.py` passes 498/0 on each arm.
  - The PDFs differ, by about 76,000 pixels at 300 dpi. That is the laptop's renderer, not the inputs.
  - The director's ruling: install the committed V_F file as it is.
- **Pin.** `make_values_fived16.py` FIGURES is `("fd/with-vf/figures", "889e175b")`. Its `--check` requires the installed file, the source and the sidecar's `pdf_sha256` to be equal.

## fived16_headline.pdf and fived16_genresidual.pdf

- **Producers.** These are input-only copies of the installed producers. The director approved each diff before it ran. The diffs are in `tools/*.diff`.
  - **Headline:** `tools/make_fig_fived16_headline.py` (bb90169f1ae596979e2983a102de785ed3ff509ffd007038861fd3902d3156fb) is round 4's `note-figredraw-20261123/tools/make_fig_fived16_headline.py` (d801f3067a95c7bbb6af7ca96543fa3a74d9b9c3a90f7044f1c65a51ef41b784).
    - RECORD is the V_F data product (`fd/with-vf/data-product/fd_data_product_vf.json`, pin 1a37b082, #1378's READOUTS["dp"]).
    - COV_KEY is `C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e`.
    - The record must carry the schema `fd-data-product-vf/1`.
  - **Genresidual:** `tools/make_fig_fived16_genresidual.py` (a428c5659c4f7b535a7b51f255a15cc750eaa6d622125a747b71048d64cd7d7d) is `note-genresid-20261120/tools/make_fig_fived16_genresidual.py` (c70829705705a8d423eacf370205bc79700b4777cbb3ea0fe22bdc62bfe9c43c).
    - Its INPUTS are #1378's pins:
      - dp: the V_F data product, 1a37b082;
      - g: `fd/with-vf/readout/vf-with-E/fd_g_readout.json`, 7034a08e;
      - gdefs: `fd/with-vf/p2/gdefs.vf.json`, 6c202b08b5d9ed0b.
    - COV_KEY is the V_F key.
    - It asserts the records' own labels: the schema `fd-data-product-vf/1`, the reported covariance `C_total + C_resp + C_PL5D + DeltaC_e`, and the carbon χ² matrix `… + DeltaC_e + V_g`.
    - It still checks against the note's own `values_fived16.tex`, which on this branch is #1378's file. That file prints the V_F carbon χ²: NuWro 92.20, GiBUU 39.70.
- **Drawn text.** Neither figure names the matrix's composition, so the redraw changes no wording.
  - The genresidual legend reads "Reported uncertainty, ±√C_ii/f_i".
- **Recipe.** `bash tools/run.sh <worktree>` (sha256 a032c6cebd78970b8018ce02524e81340677b597382bc33752ea43dbfbab2672). It writes `runs/CHECKS.txt` and copies the V_F outputs to `figs/`.
  - The headline runs as round 4 did: the miniconda3 base env (python 3.12.2, matplotlib 3.10.1, numpy 1.26.4), under `note-figstyle-20261117/tools/capture_palette.py`, with LAYOUT_PALETTE=1.
  - The genresidual runs as note-genresid did: `cov2d-work/figenv/mpl3108` (python 3.12.2, matplotlib 3.10.8, numpy 1.26.4).
  - Both run under env -i, with an empty HOME and MPLCONFIGDIR and BLAS threads 1.
- **Controls** (`runs/CHECKS.txt`: RUN :: PASS).
  - **Headline:** the unchanged producer on the OLD record equals the installed 1002e7056bfe457f… byte for byte.
  - **Genresidual on this branch:** the unchanged producer refuses, because its printed-χ² check fires (C_e-era record, V_F table). That check is what keeps the figure and the table together.
  - **Genresidual at main:** at the branch's merge-base with main (a temporary worktree), the unchanged producer equals the installed d310e8b946cb6bca… byte for byte.
  - **Repeatability:** each V_F copy ran twice, and its PDF, values file and data file are byte-equal across the two runs.
- **Values against the records.**
  - **Headline:** every cell's f equals the V_F product's, and its σ equals sqrt(diag) of the V_F reported matrix to 1e-12. The relative σ range is 0.050–0.144; it was 0.048–0.141.
  - **Genresidual:** every residual (g − f)/f equals the committed file's, bit for bit. Only the bars (the reported σ), the inputs and the source paths differ.
- **Outputs** (`figs/`):
  - `fived16_headline.pdf`, `fived16_headline_values.json` (2dcb04166c18f60052af71ebb7800483ea9d3aa6b71a6290aec3d0efa52b6ea7) and `fived16_headline_data.json` (2083fbc5322b29c2c444e4c638906e8aa147f93eabadde3182a9739fb48faf4f);
  - `fived16_genresidual.pdf` and `fived16_genresidual_values.json` (bb901af8109066f21c806992f9d32638db418c0ace42badd5d6f183257ed0176).
  - The PNG previews are not committed.
- **Install.** `docs/analysis-note/make_figures.sh` installs both with `install_current_fig`, after every earlier line.
  - The superseded headline line carries a "layered (2026-11-26)" comment.
  - `fived16_genresidual.pdf` had no install line before (it was committed straight to figures/ on 2026-11-20). It has one now.
  - A dry run of the two lines into a scratch directory reproduced the committed figures.

## Dead containment: the 6.86 exemption is retired

- **The entry.** `check_dead_containment.py` CONTEXT_EXEMPT[("main_note", "6.86")] exempted the old modes figure's "σ = 6.86%, distance +4.99σ" (NuWro's third mode).
- **Why it goes.** The V_F modes figure prints that mode as "σ = 2.49%, distance +3.77σ" and prints no 6.86.
  - The guard could not flag the entry STALE: its source, amendment E's sidecar, still holds 0.0685. Kept, it would have been a blind spot.
  - The entry and its CONTEXT_RENDERED line are removed.
  - In `test_build_all.py`, the sidecar source in EXEMPT_SOURCES is removed. So are the two tests of an exemption whose source lies outside the note tree: SKIP in the standalone shape, STALE in the canonical layout.
- **Gap left.** No live exemption has an outside source now, so the checker's outside-source branch is untested until one does. <!-- absence-ok: a statement of test coverage in check_dead_containment's own suite, not a claim that a result does not exist -->
- **Struck literals in the new figures.** I checked every number the three new figures print (pdftotext) against the 69 literals struck in main_records and pet_note, with the checker's own `outward_hit`: no hits. The old modes figure, the positive control, hits 6.86.
- **Tests.** `test_build_all.py`: 86 passed. `make_values_fived16.py --check`: PASS (3990 values, 1 figure equal to its source).

## valid_region on V_F: valid_region_vf.py (the director's ruling (b))

- **The copy.** `valid-region-20261107/valid_region_vf.py` (1f1f0dd733d2dbe6e7853981d486fbb5b3a98650707735a2fdd8c7d81227b96b) is `valid_region.py` (896201cc9d03754ddac5185f548b1b7e3a56183dbb0fe6503fcd75c5c59d5433) with only its inputs moved:
  - I1 is the V_F with-block F0b, `fd/with-vf/readout/vf-with-S/fd_f0b_readout.json`;
  - I4 is the V_F data product;
  - COV_KEY is `C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e`;
  - its pins file is `INPUTS-vf.sha256` (5a79997be11c4d16bf6fb831b61b226248b9e1db1612fa2d6fcc73c59b2e3861), set by a new PINS_FILE constant.
  - I2, I3, I5 and I6 are unchanged, as `fd_vf_p2.p2_vatlas` gave them.
- **Left as bound:** `valid_region.py`, `INPUTS.sha256`, `receipts/read/` and `fd_vf_p2.py`.
- **Run.** `python3 -B valid_region_vf.py read --repo <worktree> --out receipts/read-vf` (miniconda3 python 3.12.2, numpy 1.26.4, the env of `receipts/read/`).
  - All 11 controls pass.
  - `receipts/read-vf/readout.json` is ab5355021e61532d1933decdf06f844e120a9023a690a6b9ccc271495d287461.
- **Control.** `check_read_vf.py` (d7c0a80057b93fdbad19e3e2628974449e91279f23c337fd5c63fa558b3a0a33) passes 5/5:
  - every control passes;
  - the six inputs are the V_F pins and the files' digests;
  - the code sha is the copy's;
  - its readings equal `fd/with-vf/p2/vatlas.vf.json`'s (380682e69408b51b8299cb473254b7a5f3ae73113aa31797d02b85a41a80472a) exactly.
  - Its power: the OLD `receipts/read/` readings do not equal them.

NOT CITABLE FOR: any caption or sentence; a validated size for C_e^infl.
