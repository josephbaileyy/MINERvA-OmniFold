# MINERvA Tune v1 labels in the analysis note

The LaTeX recorder for `main_note` lists 26 unique figure PDFs. Seven had alternate names for the tune. The figure SHA-256 pins in `docs/analysis-note/make_figures.sh` install the PDFs in [figs](figs/) after the earlier figure rounds.

## Figure inventory

| Installed PDF | Label producer | Previous label | Current label |
|---|---|---|---|
| `control_plots.pdf` | `nd-unfolding/make_control_plots.py` | MC signal (MnvTune v1) | MC signal (MINERvA Tune v1) |
| `MEFHC_5iter_xsec_proj_pz.pdf` | `note-figround3-20261121/tools/compose_fig2_r3.py` | Tune v1 prior (this work)<br>Tune v1 published prediction | MINERvA Tune v1 prior<br>MINERvA Tune v1 published prediction |
| `MEFHC_5iter_xsec_paper_pt_slices.pdf` | `note-figpass-20261119/tools/compose_slices_markers.py` | Tune v1: our simulation (the prior) | MINERvA Tune v1 prior |
| `MEFHC_5iter_xsec_paper_pz_slices.pdf` | `note-figpass-20261119/tools/compose_slices_markers.py` | Tune v1: our simulation (the prior) | MINERvA Tune v1 prior |
| `q3_excess_projection.pdf` | `note-q3fig-20261121/tools/compose_q3_labels.py` | unfolded / Tune v1 prior | unfolded / MINERvA Tune v1 prior |
| `paper_fig2_joint.pdf` | `publication/release/figs/make_figs.py` | unfolded − Tune v1 per cell (10⁻⁴⁰ cm²/nucleon) | unfolded − MINERvA Tune v1 per cell (10⁻⁴⁰ cm²/nucleon) |
| `generators_vs_unfolded_band_central.pdf` | `note-fig18-20261121/tools/compose_fig18.py` | Tune-v1 | MINERvA Tune v1 |

Labels wrap within the control legend, the published-prediction entry, the two (q_3) figure marginal-axis labels, and the difference-map colorbar label. The generator legend uses tighter spacing.

| Installed PDF | Previous SHA-256 | Current SHA-256 |
|---|---|---|
| `MEFHC_5iter_xsec_paper_pt_slices.pdf` | `9fca64a7779ce4f913325b3e551a2b3653fa09e47748ac9bb5608dcb0a0eee8b` | `846be3bd1647c14b5cb525626e129aa6753c03547681f432842c8b55afdadc5f` |
| `MEFHC_5iter_xsec_paper_pz_slices.pdf` | `4d56eb9b5033b855a9c9ea0f83a8829bffccd5ae6f0f6def563b04bfe6ab3bb1` | `4e9560615d51839562cdf65e1399467110db220435cebe5c4fd1256a8cee8cf2` |
| `MEFHC_5iter_xsec_proj_pz.pdf` | `4d73ab9210fabf569d126d196ef205b7030257f66996a349657f5615d0a34a1d` | `f50545b425446f4dc3b762a14f3714af8574c80778b5faf310437843bc2962ae` |
| `control_plots.pdf` | `8910181e147c32515159f477e7e6864870c5c1f46aa64638c55d2bcd447f098c` | `65353e3acff2b22db326dd85dc766d9d981e5450d19edc2b4270d93e91be59f3` |
| `generators_vs_unfolded_band_central.pdf` | `d030980eeba9ce29dfa40c03baf426e41b9fb489cdb559651202cce94788e62c` | `5757bd67f2ce7a37e53479a6c41daf9c280c96fa4e5ecf160a514ca5cee32378` |
| `paper_fig2_joint.pdf` | `57f3cc601281950cf9251b04a627efa3e0d803eca6620178839c48f9d4b0782a` | `9023625a876bd5ca6071fbc1f0b55de672f8a5b2609ff3e56a573f8e91d45fd5` |
| `q3_excess_projection.pdf` | `29ec1e63c6673acf3dffbac64fb436c777e6c5850ac668148e6d089d50d2d57d` | `c36d48dd624b3bf268cf7a19a50e0f5d4d67b74c6508f009956755dce3efb443` |

## Data inputs

Paths beginning with `note-` are relative to the methods directory. The three momentum figures use the same A4 published-edge inputs. The public ancillary ROOT file and the RC7 array file are local copies verified against the committed [A4 pins](../../../../ibu-chi2-20261123/regenA4/AMENDMENT-A4.txt) and [RC7 manifest](../../../../../../publication/release/RC7-SHA256SUMS.txt).

| Figure | Input | SHA-256 |
|---|---|---|
| Control | `note-figstyle-20261113/runs/family1b/dumps/control_plots_ext_arrays.npz` | `815e6c0a2bfcdbf95ca5c5b53c344f1f53410043164675eee92639125fc9dee2` |
| Momentum projection and slices | `docs/orchestration/state/ibu-chi2-20261123/tier1/units/e/er.root` | `5171c7b8ecacda6090e242349dd622218c1c38885c60ef8b91027033a8c4b780` |
| Momentum projection and slices | `cov_ptpl_minerva_inclusive_6GeV.root` | `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3` |
| Momentum projection and slices | `2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt` | `222317522662b7001e8d4fcc155c1ec0b28b85f2cd868ab10206a7e7f6bf8240` |
| `q3_excess_projection` | `note-figstyle-20261113/runs/family5/dumps/q3_arrays.npz` | `aa02d0c32e6bee24d6a38558cd560d9043c19f132f9d6008fe66341d3d871af4` |
| Joint map | RC7 `data/figs/fig_arrays.npz` | `72394a2b4eff9f14b01903ff97525bcb690c2adee58ccaf573a8d95139b415b8` |
| Generator comparison | `note-figstyle-20261113/runs/family4/pickles/generators_vs_unfolded_band_central.pdf.figpickle` | `720a350efb64bf57bef15e6337a23783f351ac36a14485614bdf47adfde0d714` |

The A4 ancillary remapper also verifies every ancillary text file against the committed copies before running. The A4 pins list their individual digests.

## Regeneration

Start in Bash at the repository root. Set `out` to a new scratch directory, `anc` to the A4 ancillary directory, and `rc7_arrays` to the pinned RC7 array file. Set `mpl` to Python with Matplotlib 3.10.8, `rootmpl` to Python with ROOT 6.40.04 and Matplotlib 3.10.8, `pdfedit` to Python with pikepdf 9.4.2, and `mpl_release` to Python with Matplotlib 3.11.2.

~~~sh
methods="$PWD/docs/orchestration/state/2d-closeout/stageF/methods"
palette="$methods/note-figstyle-20261117/tools"
inputs="$methods/note-figstyle-20261113/runs"
fakeroot="$methods/note-figstyle-20261113/tools"
xsec="$PWD/docs/orchestration/state/ibu-chi2-20261123/tier1/units/e/er.root"
strip="$methods/note-figround-20261121/tools/strip_stamp.py"
mkdir -p "$out"/{home,mpl,cap,control,proj,slices,q3,joint,generators,stripped}
export SOURCE_DATE_EPOCH=0 MPLCONFIGDIR="$out/mpl"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1

HOME="$out/home" PYTHONPATH="$fakeroot/fakeroot" "$mpl" "$palette/capture_palette.py" "$out/cap/control" \
  "$palette/palette_run.py" "$PWD/nd-unfolding/make_control_plots.py" \
  --from-arrays "$inputs/family1b/dumps/control_plots_ext_arrays.npz" \
  --extended-display --outdir "$out/control" --print-style

"$rootmpl" "$palette/capture_palette.py" "$out/cap/proj" "$palette/remap_anc.py" "$anc" \
  "$methods/note-figround3-20261121/tools/compose_fig2_r3.py" "$xsec" "$anc" "$out/proj"

"$rootmpl" "$palette/capture_palette.py" "$out/cap/slices" "$palette/remap_anc.py" "$anc" \
  "$methods/note-figpass-20261119/tools/compose_slices_markers.py" \
  --pt-ncols 3 --logx --font-floor 7 --pz-top-hundredths 30 --pub-size-percent 100 --pub-edge-hundredths 40 \
  "$xsec" "$anc" "$out/slices"

HOME="$out/home" LAYOUT_PALETTE=1 PYTHONPATH="$fakeroot/fakeroot5" \
  "$mpl" "$palette/capture_palette.py" "$out/cap/q3" \
  "$methods/note-stepedges-20261121/tools/compose_q3_steps.py" "$PWD/nd-unfolding/q3_excess_projection.py" \
  --from-arrays "$inputs/family5/dumps/q3_arrays.npz" --out "$out/q3/q3_excess_projection.png" --print-style

for item in control/control_plots slices/MEFHC_5iter_xsec_paper_pt_slices \
  slices/MEFHC_5iter_xsec_paper_pz_slices q3/q3_excess_projection; do
  name=${item##*/}
  "$pdfedit" -I "$strip" "$out/$item.pdf" "$out/stripped/$name.pdf" "$out/stripped/$name.json"
done

"$mpl_release" publication/release/figs/make_figs.py --npz "$rc7_arrays" --outdir "$out/joint"
cp "$out/joint/fig2_joint_localization.pdf" "$out/joint/paper_fig2_joint.pdf"

HOME="$out/home" "$mpl" "$palette/capture_palette.py" "$out/cap/generators" \
  "$methods/note-fig18-20261121/tools/compose_fig18.py" "$inputs/family4/pickles" "$out/generators"
~~~

The baseline producers at `81e8fe14e` reproduced all seven previous installed renders pixel for pixel at 145 dpi with Poppler. The six artist captures had identical plotted arrays in both runs. The generator readout JSON also matched byte for byte. The Fig. 7 pixel difference was confined to the difference-map colorbar label. The other raster differences were confined to the changed legends or axis labels. All seven PNGs were inspected for fit.
