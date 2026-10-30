# 5B step 5 (section 2.4; binding condition 3): the pooled control, login node. Then STOP for the director.
set -o pipefail
P=/pscratch/sd/j/josephrb; B=$P/fd-ct-5b-20261030; D=$B/deploy/2c960659
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
[ -e "$B/control/fd_ct_5b_control.json" ] && { echo "STOP: control record exists"; exit 2; }
cd $B && TMPDIR=$B/tmp timeout 600 $PY $D/nd-unfolding/fd_ct_periods.py control \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz --b $B \
  --mp1-zero $D/docs/orchestration/state/measurement-paper/phase1/mp1/jitter-receipts/mp1s1_zero_b-_j-.npz \
  --out-json $B/control/fd_ct_5b_control.json > $B/logs/control.out 2> $B/logs/control.err; echo "rc=$?" >> $B/logs/control.out
{ date -u +%FT%TZ; hostname; } >> $B/logs/control.out
cat $B/logs/control.out; echo "--- stderr"; cat $B/logs/control.err
echo "--- record"; cat $B/control/fd_ct_5b_control.json 2>/dev/null | head -c 6000
