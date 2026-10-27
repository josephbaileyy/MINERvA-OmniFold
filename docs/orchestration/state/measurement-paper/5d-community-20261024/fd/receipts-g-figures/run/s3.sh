# Step 3 (FD-G-FIGURES-DECLARATION.md section 2.2, bound; rulings 1, 2, 6 and 8: the declared argv).
P=/pscratch/sd/j/josephrb
B=$P/fd-g-figures-20261027
D=$B/deploy/933cfe35
T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
date -u +%FT%TZ > $B/logs/figures.start; hostname >> $B/logs/figures.start
cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_g_figures.py \
  --g-readout $T/fd/readout/fd_g_readout.json --g-diag-readout $T/fd/readout/fd_g_diag_readout.json \
  --g-followup-readout $T/fd/readout/fd_g_followup_readout.json --g-sens2-readout $T/fd/readout/fd_g_sens2_readout.json \
  --f0b-readout $T/fd/readout/fd_f0b_readout.json --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --figures ratio modes sens --ratio-form data-over-prediction --gibuu-axis separate \
  --out-dir $B/figures > $B/logs/figures.out 2> $B/logs/figures.err; echo "rc=$?" >> $B/logs/figures.out
date -u +%FT%TZ >> $B/logs/figures.start
cat $B/logs/figures.start; grep -v "^PASS" $B/logs/figures.out; grep -c "^PASS" $B/logs/figures.out; grep -v "timestamp seems very low" $B/logs/figures.err | head -5; grep -c "timestamp seems very low" $B/logs/figures.err
