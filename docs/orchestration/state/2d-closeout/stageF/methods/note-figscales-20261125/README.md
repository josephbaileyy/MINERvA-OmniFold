# Note figure scale and legend updates

The note installs the PDFs in this directory through the SHA-256 pins in
docs/analysis-note/make_figures.sh. The rendering recipes below start at the repository root.
Set `methods` to the absolute path of this directory's parent and `out` to a scratch directory.

## Figure 4

Run the local copy of the note-figpass-20261119 producer with Matplotlib 3.10.1.

~~~sh
python3 -I "$methods/note-figscales-20261125/tools/make_fig_runperiod_steps.py" --out "$out"
~~~

The producer pins the two input readouts. The SHA-256 of
`methods-short-20261109/lrows-g/g4-runperiod/runperiod_values.json` is
`f63074b1d8af178f6a1b14b48f5fb23ea42610e0a75c2c07d8b59b5e93ce0386`.
The SHA-256 of `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/run/readout/fd_rpd.json`
is `c0b06cfd2d11d99fc9226d054e68b951231f5d02e81ea3abc80cf7f89b624658`.
The earlier producer reproduces the previous installed PDF byte for byte. The two producers'
numeric JSON outputs match byte for byte, and the rendered changes are confined to the legend.

## Figure 6

Use Matplotlib 3.10.8 for the existing palette, layout, label-contrast and bin-edge recipe,
and pikepdf 9.4.2 for the existing exposure-stamp removal. Run the two commands with the
respective Python environments. The first Python uses the array-only ROOT stand-in used in
the previous note round.

~~~sh
mkdir -p "$out/home" "$out/mplconfig" "$out/capture"
HOME="$out/home" MPLCONFIGDIR="$out/mplconfig" SOURCE_DATE_EPOCH=0 LAYOUT_PALETTE=1 \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  PYTHONPATH="$methods/note-figstyle-20261113/tools/fakeroot5" \
  python3 "$methods/note-figstyle-20261117/tools/capture_palette.py" "$out/capture" \
  "$methods/note-stepedges-20261121/tools/compose_q3_steps.py" \
  "$PWD/nd-unfolding/q3_excess_projection.py" \
  --from-arrays "$methods/note-figstyle-20261113/runs/family5/dumps/q3_arrays.npz" \
  --out "$out/q3_excess_projection.png" --print-style
python3 "$methods/note-figround-20261121/tools/strip_stamp.py" \
  "$out/q3_excess_projection.pdf" "$out/q3-stripped.pdf" "$out/stamp.json"
~~~

The SHA-256 of `note-figstyle-20261113/runs/family5/dumps/q3_arrays.npz` is
`aa02d0c32e6bee24d6a38558cd560d9043c19f132f9d6008fe66341d3d871af4`.
The previous producer gives the same raster as the previous installed PDF. The artist
captures match bit for bit for the map values, mask, bin extents and marginal values.
Rendered changes are confined to the map and colorbar.

## Figure 7

`publication/release/figs/make_figs.py` with Matplotlib 3.11.2 reproduces the installed PDF
byte for byte from the RC7 `data/figs/fig_arrays.npz` (SHA-256
`72394a2b4eff9f14b01903ff97525bcb690c2adee58ccaf573a8d95139b415b8`).
The ratio and difference scales are already symmetric around 1 and 0, respectively.
The note displays the upper and lower halves of this PDF side by side.
