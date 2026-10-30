# 5B step 8 (section 2.6; binding condition 4): the readout, login node.
set -o pipefail
P=/pscratch/sd/j/josephrb; B=$P/fd-ct-5b-20261030; D=$B/deploy/2c960659
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
[ -e "$B/fd_ct_5b_periods.json" ] && { echo "STOP: readout exists"; exit 2; }
cd $B && TMPDIR=$B/tmp timeout 600 $PY $D/nd-unfolding/fd_ct_periods.py periods \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz --b $B \
  --control-json $B/control/fd_ct_5b_control.json \
  --readout-5a $D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_period.json \
  --out-json $B/fd_ct_5b_periods.json > $B/logs/periods.out 2> $B/logs/periods.err; echo "rc=$?" >> $B/logs/periods.out
{ date -u +%FT%TZ; hostname; } >> $B/logs/periods.out
cat $B/logs/periods.out; echo "--- stderr"; cat $B/logs/periods.err
