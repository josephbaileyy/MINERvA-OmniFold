# 5B step 2 (section 2.2; binding condition 2): the precheck, login node, 0 node-h.
set -o pipefail
P=/pscratch/sd/j/josephrb; B=$P/fd-ct-5b-20261030; D=$B/deploy/2c960659
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
[ -e "$B/control" ] && { echo "STOP: $B/control exists"; exit 2; }
mkdir $B/control && cd $B && TMPDIR=$B/tmp timeout 600 $PY $D/nd-unfolding/fd_ct_periods.py precheck \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --cresp $P/cresp-20261026/out/cresp.npz --b $B \
  --mp1-zero $D/docs/orchestration/state/measurement-paper/phase1/mp1/jitter-receipts/mp1s1_zero_b-_j-.npz \
  --out-json $B/control/fd_ct_5b_precheck.json > $B/logs/precheck.out 2> $B/logs/precheck.err; echo "rc=$?" >> $B/logs/precheck.out
{ date -u +%FT%TZ; hostname; } >> $B/logs/precheck.out
cat $B/logs/precheck.out; echo "--- stderr"; cat $B/logs/precheck.err
