# Sixteen-cell generator residuals figure (cov2d, 2026-11-20)

**Request.** Joseph asked for this figure for the journal-voice rewrite's generator comparison on the sixteen cells
(§5.3 of the rewrite). The director relayed the request on 2026-11-20. It is new figure-making off the note branch:
pass 2 of the rewrite wires it in. This lane changes no note text.

**What it shows.**
- For each reporting cell R00–R15, the fractional difference (g_i − f_i)/f_i (%), for each prediction of the note's
  main comparison table (tab:fived16-gen):
  - GENIE 2.12.10 CV;
  - GENIE 2.12.10 + Valencia MEC;
  - NuWro 21.09 on carbon;
  - GiBUU 2019 on carbon, on its 8 cells below p_par = 4.5 GeV/c only;
  - MINERvA Tune v1.
- Grey bars at ±sqrt(C_rep,ii)/f_i, where C_rep = C_total + C_resp + C_PL,5D is the reported covariance.
- Dotted separators between the four (p_T, p_par) quadrants, each headed by its box.
- The figure is descriptive. The bars show only the diagonal of C_rep. The table's χ² also includes V_g and the
  correlations, which no bar shows.

**Producer.**
- Script: `tools/make_fig_fived16_genresidual.py` (sha256 `c70829705705a8d423eacf370205bc79700b4777cbb3ea0fe22bdc62bfe9c43c`).
- Command, from the repository root: `python3 -I <record>/tools/make_fig_fived16_genresidual.py --out <dir>`.
- Environment: matplotlib 3.10.8 and numpy 1.26.4 (cov2d's `figenv/mpl3108`, the environment of the figure pass's
  fived16_headline). It uses the note's `note_palette` colours and `note_print_style` fonts, at `\textwidth`, with no
  font under 7 pt (asserted).
- It reads committed records only, never table text. Each record is held to the sha256 prefix that
  `make_values_fived16.py` READOUTS pins for the reported arm:

| key | record (under `docs/orchestration/state/measurement-paper/5d-community-20261024/`) | sha256 | used for |
|---|---|---|---|
| dp | `fd/with-cpl/data-product/fd_data_product_cpl.json` | `d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50` | f; C_rep (`C_total_plus_C_resp_plus_C_PL5D`) |
| g | `fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json` | `a19009e0bd83b9bb8f9ad65fb65804e6f62c8953310103fbfe6fce5f84995875` | GENIE CV, GENIE + MEC, Tune v1 |
| gdefs | `fd/gencmp/readout/defs.json` | `544f4f4343095b5e78b59e0782ac3ce5ef5974b2e24dbb59be3708b5937556f8` | NuWro and GiBUU, carbon, analysis definitions |

- The producer's source mapping is the table's own: `make_values_fived16.py` takes tab:fived16-gen's GENIE and Tune
  rows from `g`, and its NuWro and GiBUU (carbon) rows from gdefs' `carbon/analysis_definitions`, against the
  reported matrix.

**Checks.** If any check fails, nothing is written.
- Each input's sha256 matches its pin.
- Every readout's f equals the data product's f, cell by cell.
- Every readout's cells are R00–R15. For GiBUU they are exactly the 8 cells whose p_par box ends at `h2-mid-pz`.
- The record's relative sigma of C_rep equals sqrt(diag)/f.
- Each readout's own `g_over_f_minus_1` equals the (g − f)/f computed here.
- The figure agrees with the note's printed values (`docs/analysis-note/values_fived16.tex`):
  - every GENIE CV, GENIE + MEC and Tune per-cell `g-<p>-gf-R<nn>` (tab:fived16-pulls, one decimal) is equal;
  - NuWro's and GiBUU's carbon total χ² (`g-<p>-carbon-total-chi2`, tab:fived16-gen), recomputed from the same
    gdefs record the points come from, is equal.
- Identity check: the marker heights, cell positions and bar half-heights read back from the drawn artists equal the
  computed values.
- Two runs give byte-identical PDF and values files. The PDF carries no creation date.

**Outputs.**
- `docs/analysis-note/figures/fived16_genresidual.pdf` (sha256
  `d310e8b946cb6bca02958824810acbba2abee38ab64fc61182e6e2b97c75af3a`). It is installed, but no `.tex` file
  references it yet.
- `run/fived16_genresidual_values.json` (sha256 `1b945d95f3dc3716475f31abc854fa701b536e489801cf250d7d6b677b1341e2`):
  every plotted number, the input paths and digests, and the checks.
- The PNG preview is written to `--out` and is not committed.

**Ranges, for the caption writer.** These are read from the values file. A caption that prints any of them should
format it from that file, not from this list.
- Bar half-heights: 4.8 % to 14.1 %.
- GENIE CV: −17.4 % to +15.1 %.
- GENIE + MEC: −17.3 % to +19.1 %.
- NuWro (carbon): −23.9 % to +12.5 %.
- GiBUU (carbon): −52.3 % to −14.5 %, on 8 cells.
- Tune v1: −20.3 % to +10.0 %.

**Design.** The layout follows codex's placeholder, which was drawn from table text for the design only and is not an
input: `~/codex-reports/note-measurement/rewrite-20261121/pass1/s5/section5-generator-comparison.pdf`. That
placeholder showed three predictions. This figure shows all five predictions of tab:fived16-gen, as the request asks.
