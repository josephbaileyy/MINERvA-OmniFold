# Carbon-only predictions in the sixteen-cell ratio figure

The ratio figure retains NuWro and GiBUU using their committed **carbon-only,
analysis-definition** predictions. No hydrogen contribution is used. NuWro has
sixteen cells; GiBUU has the eight cells whose upper parallel-momentum edge is
4.5 GeV/c. GENIE CV, GENIE + MEC and MINERvA Tune v1 are unchanged. This is a
display change using existing integrals, not a generator rebuild, new covariance
calculation or inference result.

## Printed producer and baseline

Base: `78ab386e04276cd5027eeed12d2611c489bc02c3`.
Commit `a24d7c421` installed the ratio PDF from
`fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2/`. The PDF in that commit,
the installed PDF at the base, and that committed source have identical SHA256:
`6214ed7800e9a6d0454dc376d3f100306969fa11dff83f703f134ef4d36fb0c7`.
Its sidecar records `data-over-prediction`, a separate GiBUU axis and the
`C_resp + C_PL5D` extra block. `nd-unfolding/fd_gencmp_ea2.py` invokes
`fd_g_figures.py` through `fd_gencmp_e.BOOT`; the drawing producer is
`fd_g_figures.ratio_model` followed by `paint` and `render`.

`nd-unfolding/fd_g_ratio_carbon.py` calls those same functions. First it requires
the unmodified producer model to equal the committed E-A2 sidecar's entire
`plotted` object exactly. It then passes the carbon definitions to the producer.
The historical default remains unchanged.

## Committed operand trace

All paths below are relative to
`docs/orchestration/state/measurement-paper/5d-community-20261024/`, except the
explicit `nd-unfolding/` path. Full SHA256 pins for every opened input are in
`inputs.json`; no release-package pin supplies a plotted operand.

| Operand | Committed file and field |
| --- | --- |
| Data integrals, every curve | `fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json`, `predictions[name].f` |
| GENIE CV, GENIE + MEC, Tune v1 integrals | Same readout, `predictions[name=genie_cv, genie_mec, mnvtune_v1].g` (each named entry separately) |
| NuWro carbon integrals | `fd/gencmp/readout/defs.json`, `generators.nuwro.carbon.analysis_definitions.chi2.reported.g` |
| GiBUU carbon integrals | Same definitions, `generators.gibuu.carbon.analysis_definitions.chi2.reported.g` |
| Carbon target and cell/data agreement | Same carbon branches, `chi2.reported.cells`, `chi2.reported.f`; each vector also equals its branch's `analysis_definitions.g` |
| Relative data uncertainty | E-A2 readout above, `predictions[name].sigma_total_over_f`, unchanged for every curve |
| Independent uncertainty consistency | `fd/with-cpl/readout/fd_f0b_readout.json`, `relative_sigma_plus_C_resp + C_PL5D.C_total` and `extra_block.relative_sigma` |
| Cell labels, intervals, GiBUU selection | `nd-unfolding/pv-ladder/readouts/h2_definition.json`, `reporting_cells[id].box`; labels/order also checked against the E-A2 readout's `cells` |
| Historical labels and prediction identities | `fd/gencmp-e/rerun1/chain/pins/predictions-chdefs.json`, named entries; existing labels retained except the two carbon-only qualifiers |
| Baseline plotted arrays and geometry | `fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2/fd_g_fig_ratio.json`, `plotted` |

The definitions' SHA256 is
`544f4f4343095b5e78b59e0782ac3ce5ef5974b2e24dbb59be3708b5937556f8`.
Their `rebuild_json_sha256` is
`e2ba8d54cfbd122d1951613aea82121422708c96fcf4f66edd6bd55797a4ccca`,
exactly the SHA256 of committed `fd/gencmp/readout/rebuild_b.json`.
`nd-unfolding/fd_gencmp.py`'s step-B `readout` constructs these carbon vectors
from the carbon sample alone; `analysis_definitions` holds the five-seed mean
in the analysis definitions. Its later `CH` branch combines carbon and hydrogen;
that branch supplies neither new curve. The rebuild receipt is checked for its
identity only. No event or NPZ file is opened.

The displayed arithmetic remains `f/g`, with error-bar endpoints
`f/g +/- (f/g)*sigma_total_over_f`. These are the original data uncertainties,
not a new uncertainty for carbon predictions. No chi-square value is computed
or printed by this change. Colors, markers, offsets, cell key, two-panel
geometry, limits and legend font size are unchanged. The producer's constants
supply styles; `carbon only` explicitly identifies the selected target branch.

## Reported estimator

All five E-A2 readouts reference S1 assembly
`db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4`.
Pinned `s1/readout/s1_assembly.json` has that `assembly_sha256`; its
`meta.code_sha256.s1_assemble.py` equals the current assembler's SHA256,
`b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7`.
That producer's `check_meta` requires configuration R, five iterations, the
100-tree/eight-leaf classifiers at seed 42, and 400-tree/31-leaf refinement at
seed 45 for the central product. These are configuration (e)'s settings.
The present check follows this committed assembly and its enforced configuration;
it does not reopen raw estimator products. The data and uncertainty vectors are
identical to the printed parent's, including those used for both carbon curves.

## Regeneration and checks

From the repository root, with NumPy and Matplotlib installed:

```sh
python3 nd-unfolding/fd_g_ratio_carbon.py --out-dir /tmp/ratio-carbon-new
```

The output directory must not exist. Install its PDF in
`docs/analysis-note/figures/fd_g_fig_ratio.pdf`; its matching source PDF and JSON
are retained here. `make_values_fived16.py` binds this source and PDF digest,
leaving the modes figure's existing binding unchanged.

Checks performed:

- Full parent plot model exactly reproduced from pinned committed readouts.
- Every item except NuWro/GiBUU points, error bars and legend entries exactly
  equal to the parent, including all remaining curves' coordinates and errors.
- Carbon point values and both error endpoints independently checked by exact
  NumPy equality against the definitions and original data-error vectors.
- Original artist readback, cell-mask, legend-handle, bounds, no-overlap and
  repeat-render checks passed; the regenerated PDF was visually inspected.
- The 11 existing E-A2 regression tests passed, including its full historical redraw.
- `make_values_fived16.py --check` passed (3,849 values, both figure source
  bindings and all ten listed-truth sentences).
- The new input pins add exactly nine live receipt bindings. Excluding only
  this directory's new receipts reproduces the previous 169-binding inventory
  and its digest exactly; no existing binding is removed or repointed. The
  inventory guard is updated with this owning change, with the complete delta
  in `binding-delta.txt`.
- Native PDF remains 504 by 360 points (7 by 5 inches). Extracted character-font
  size sets are identical to the parent, including the 6.8-point legend and
  7.5-point axis-label size. No resizing or font change was made.

New PDF SHA256:
`1e6d550e043104f7ebfe19d1d122c6da1ba6abbd6a480168e243d3c4fe7e5567`.
No caption, manuscript or Supplement text is edited. Their integration and the
standalone note synchronization remain with the manuscript integrator.
