#!/bin/bash
# Draw every print-style figure of families 3-6 from the fetched dumps, under capture_any, and compare drawn data with
# the cluster's off-arm captures. usage: bash restyle_run.sh <scratch>
S=$1; G=$S/groupc; W=$S/wt-note; T=$W/docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261113/tools
PY=$S/figenv/mpl3108np126/bin/python; R=$G/rs; rm -rf $R; mkdir -p $R
export MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$T/fakeroot5:$W
cap() { local name=$1; shift; mkdir -p $R/$name; (cd $R/$name && $PY $T/capture_any.py $R/cap-$name "$@") > $R/$name.log 2>&1 || echo "FAIL run $name"; }
cap stat "$W/2d-unfolding/uq/plot_bootstrap_figs.py" --from-arrays $G/f3x/f3/out/stat_arrays.npz --outdir $R/stat --print-style
cap spec "$W/3d-unfolding/plot_eavail_spectrum.py" --from-arrays $G/f4x/f4/out/eavail_spectrum_arrays.npz --out $R/spec/eavail_spectrum.png --print-style
cap q3 "$W/nd-unfolding/q3_excess_projection.py" --from-arrays $G/f5x/f5/out/q3_arrays.npz --out $R/q3/q3_excess_projection.png --print-style
cap acc "$W/nd-unfolding/fps_acceptance.py" --from-arrays $G/f5x/f5/out/acc_arrays.npz --out-png $R/acc/fps_acceptance_MEFHC.png --print-style
cap pilot "$W/nd-unfolding/fps_pilot_compare.py" --from-arrays $G/f5x/f5/out/pilot_arrays.npz --out-png $R/pilot/fps_pilot_compare_MEFHC.png --print-style
cap env "$W/nd-unfolding/fps_prior_envelope.py" --from-arrays $G/f5x/f5/out/env_arrays.npz --out-png $R/env/fps_prior_envelope_MEFHC.png --print-style
cap jn "$G/f6x/f6/code/plot_joint_null_distributions_physlabels.py" --from-arrays $G/f6x/f6/out/joint_nulls_arrays.npz --out $R/jn/paper_joint_nulls.pdf --print-style
for pair in stat:f3/cap-stat-off spec:f4/cap-spec-off q3:f5/cap-q3-off acc:f5/cap-acc-off pilot:f5/cap-pilot-off env:f5/cap-env-off jn:f6/cap-jn-off; do
  n=${pair%%:*}; off=$G/${pair#*:}; off=${off/\/f3\//\/f3x\/f3\/}; off=${off/\/f4\//\/f4x\/f4\/}; off=${off/\/f5\//\/f5x\/f5\/}; off=${off/\/f6\//\/f6x\/f6\/}
  echo "== $n"; $PY $T/compare_any.py $off $R/cap-$n 2>&1 | grep -v 'overlap:'
done
