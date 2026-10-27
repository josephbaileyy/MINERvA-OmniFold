# Step 4 (FD-G-FIGURES-DECLARATION.md section 2.3, bound): the independent check of the figures' sidecars.
P=/pscratch/sd/j/josephrb
B=$P/fd-g-figures-20261027
D=$B/deploy/933cfe35
T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
date -u +%FT%TZ > $B/logs/check.start; hostname >> $B/logs/check.start
cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_g_figures_check.py \
  --g-readout $T/fd/readout/fd_g_readout.json --g-diag-readout $T/fd/readout/fd_g_diag_readout.json \
  --g-followup-readout $T/fd/readout/fd_g_followup_readout.json --g-sens2-readout $T/fd/readout/fd_g_sens2_readout.json \
  --f0b-readout $T/fd/readout/fd_f0b_readout.json --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --figures-dir $B/figures > $B/logs/check.out 2>&1; echo "rc=$?" >> $B/logs/check.out
date -u +%FT%TZ >> $B/logs/check.start
cat $B/logs/check.start $B/logs/check.out; echo "porcelain $(git -C $D status --porcelain --ignored | wc -l)"
cd $B && sha256sum figures/* data-product/* > $B/logs/outputs-sha256.txt; cat $B/logs/outputs-sha256.txt; du -sh $B/figures $B/data-product
