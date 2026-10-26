set -u
P=/pscratch/sd/j/josephrb; B=$P/fd-g-diag-20261026; D=$B/deploy/d02ce2f2
T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"
grep -q "^tests rc=0$" $B/logs/deploy.log || { echo "STOP: deploy not clean"; exit 9; }
test ! -e $B/fd_g_diag_readout.json || { echo "STOP: readout exists"; exit 9; }
echo "diag start $(date -u +%FT%TZ) $(hostname)" > $B/logs/diag-start.txt
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_g_diag.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --g-readout $T/fd/readout/fd_g_readout.json \
  --extra-block $P/cresp-20261026/out/cresp.npz \
  --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a \
  --extra-block-key C_resp --extra-block-name C_resp --extra-block-role adopted \
  --out-json $B/fd_g_diag_readout.json > $B/logs/diag.out 2> $B/logs/diag.err; echo "rc=$?" >> $B/logs/diag.out
echo "diag end $(date -u +%FT%TZ)" >> $B/logs/diag-start.txt
cat $B/logs/diag-start.txt; grep -c PASS $B/logs/diag.out; grep -v '^PASS' $B/logs/diag.out; tail -5 $B/logs/diag.err
